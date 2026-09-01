#!/usr/bin/env python3
"""p49 CONTROLS: **the tautological-guard measurement** -- `.memory/03-measurement.md`
entry 19, run on this row rather than argued about.

    python3 patterns/p49-interned-pool/controls/threshold.py

WHY THIS EXISTS
---------------
The C demonstration this row was admitted on, `.temp/t160/red/k40304.c`, fixes
the content width at `K_CLEN 3` against `K_THRESH 5`, so

    if (K_CLEN < K_THRESH)      /* -> if (3 < 5).  A COMPILE-TIME CONSTANT. */

**the non-interned branch is DEAD and NO RECORD IS EVER BORN OWNED.** That is
the entry-19 defect: the threshold, which is the CVE's own precondition, is not a
test at all.

⚠⚠ **AND THE STRONGER FORM OF THAT CLAIM -- *the guard `if (r_shared[i])` CAN
NEVER BE FALSE*, which `TASK_161.md` and `.temp/mgr161/NOTES.md` both assert
verbatim -- IS FALSE, AND THIS CONTROL IS HALF OF THE REFUTATION.** The
reduction's own copy-on-write arm writes `r_shared[i] = 0;` when it un-shares, so
a SECOND `BREAK` on a record the FIRST one already copied takes the false branch.
Measured in the reduction's own C, with two counters spliced into a COPY of it
(`.temp/t161/red_probe/probe.py`, 20 000 random op streams at `SLB_HARDEN=1`):

    records BORN shared            215579
    records BORN owned                  0     <-- the DEAD branch, and the defect
    guard `if (r_shared[i])` TRUE   67195
    guard `if (r_shared[i])` FALSE  30263     <-- 31.1% of 97 458 evaluations

⚠ **What IS true of the reduction as SHIPPED**: its two blobs evaluate the guard
**once between them** (benign 0, adversarial 1) and it is TRUE that once, so the
demonstration never exercised the false branch even though the program can.
✅ **The precise defect is therefore *no record is ever born owned*, not *the
guard cannot fire* -- and the two need different repairs.**

The shipped kernel derives the width from the operand instead
(`w = 1 + a % MAXW`, `MAXW = 6`, `THRESH = 4`). **This control measures both
configurations, side by side, on the same op streams**, so *the fix worked* is a
number rather than a claim -- and it splits `guard FALSE` into *on a record BORN
owned* and *on a record a copy-on-write already un-shared*, because only the
first is what the threshold buys.

⚠ **THE SIMULATOR HERE IS NOT `model.py`, AND THAT IS DELIBERATE**: `model.py`
hard-codes the shipped width rule, so it cannot express the reduction's
configuration at all. This file carries a small parameterised walker instead, and
**cross-checks it against `model.py` on the SHIPPED blobs** -- if the two
disagree on a shipped input, the measurement below is about the wrong program and
the control fails.

WHAT IT ASSERTS
---------------
  * the shipped configuration takes BOTH branches of the threshold, and the
    copy-on-write guard is evaluated with BOTH answers;
  * the shipped configuration creates records that are BORN owned, and the
    reduction's creates none -- which is the defect, stated exactly;
  * in the reduction's configuration the guard is NEVER false on a record born
    owned (there are none), and every false evaluation follows an earlier
    copy-on-write;
  * the walker agrees with `model.py` on every shipped `.bin`;
  * on the SHIPPED blobs specifically, the guard is evaluated N times on the
    matrix inputs and is FALSE every time, and TRUE at least once on every
    adversarial input except `adversarial-stride3.bin` (whose windows the driver
    guard skips entirely).
"""

import glob
import hashlib
import json
import os
import random
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, PDIR)

import slb            # noqa: E402
import model as m49   # noqa: E402

SEED = 4903
NWIN = 20000
MASK = (1 << 64) - 1

#: `adversarial-stride3.bin`'s window is 3 bytes, below the driver's
#: `stride_w >= 4` guard, so the loop is skipped and NO op of any kind executes.
NO_OPS = ("adversarial-stride3.bin",)


def walk(win, width_fn, stats):
    """The CHECKED semantics with the width rule as a parameter. Offsets, exactly
    as the rungs and `model.py::_run_spec` carry them."""
    if len(win) < m49.HDR:
        return 0
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0
    mem = bytearray(m49.MEM)
    ekey, elen, eoff = [], [], []
    roff, rlen, rshd = [], [], []
    rborn = []          # was this record BORN owned? -- see `born_owned` below
    abump, pbump = 0, m49.ARENA
    acc, p = 0, m49.HDR
    for _ in range(nops):
        if len(win) - p < m49.OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += m49.OPSZ
        w = width_fn(a)
        key = a % m49.NKEY
        op = c % 4
        if op in (m49.DEFINE_A, m49.DEFINE_B):
            if len(roff) >= m49.NREC:
                v = m49.SENT
            elif w < m49.THRESH:
                stats["intern_branch"] += 1
                f = len(ekey)
                for k in range(len(ekey)):
                    if ekey[k] == key and elen[k] == w:
                        f = k
                        break
                if f == len(ekey):
                    if len(ekey) >= m49.NENT or abump + w > m49.ARENA:
                        v = m49.SENT
                    else:
                        for j in range(w):
                            mem[abump + j] = m49.cbyte(key, j)
                        ekey.append(key)
                        elen.append(w)
                        eoff.append(abump)
                        roff.append(abump)
                        rlen.append(w)
                        rshd.append(1)
                        rborn.append(0)
                        stats["born_shared"] += 1
                        abump += w
                        v = a
                else:
                    stats["dedup_hit"] += 1
                    roff.append(eoff[f])
                    rlen.append(w)
                    rshd.append(1)
                    rborn.append(0)
                    stats["born_shared"] += 1
                    v = a
            else:
                stats["own_branch"] += 1
                if pbump + w > m49.MEM:
                    v = m49.SENT
                else:
                    for j in range(w):
                        mem[pbump + j] = m49.cbyte(key, j)
                    roff.append(pbump)
                    rlen.append(w)
                    rshd.append(0)
                    rborn.append(1)
                    stats["born_owned"] += 1
                    pbump += w
                    v = a
        elif op == m49.BREAK:
            if not roff:
                v = m49.SENT
            else:
                t = a % len(roff)
                stats["guard_true" if rshd[t] else "guard_false"] += 1
                if not rshd[t]:
                    stats["gf_born_owned" if rborn[t] else "gf_after_cow"] += 1
                if rshd[t]:
                    if pbump + rlen[t] > m49.MEM:
                        stats["cow_refuse"] += 1
                        acc = (acc * 31 + m49.SENT) & MASK
                        continue
                    for j in range(rlen[t]):
                        mem[pbump + j] = mem[roff[t] + j]
                    roff[t] = pbump
                    rshd[t] = 0
                    pbump += rlen[t]
                mem[roff[t]] = 0
                v = 2
        else:
            if not roff:
                v = m49.SENT
            else:
                t = a % len(roff)
                v = 0
                for j in range(rlen[t]):
                    v = (v * 31 + mem[roff[t] + j]) & MASK
        acc = (acc * 31 + v) & MASK
    for t in range(len(roff)):
        for j in range(rlen[t]):
            acc = (acc * 31 + mem[roff[t] + j]) & MASK
        acc = (acc * 31 + rshd[t]) & MASK
    return (acc * 31 + len(roff)) & MASK


SHIPPED_WIDTH = ("shipped   w = 1 + a % MAXW", lambda a: 1 + a % m49.MAXW)
#: The reduction's rule, `.temp/t160/red/k40304.c:39` -- `#define K_CLEN 3`.
REDUCED_WIDTH = ("reduction w == 3 (K_CLEN)", lambda a: 3)


def rand_window(rng, nops):
    out = bytearray(struct.pack("<I", nops))
    for _ in range(nops):
        out.append(rng.randrange(0, 256))
        out.append(rng.randrange(0, 256))
    return bytes(out)


def blank():
    return dict(intern_branch=0, own_branch=0, dedup_hit=0, guard_true=0,
                guard_false=0, cow_refuse=0, born_shared=0, born_owned=0,
                gf_born_owned=0, gf_after_cow=0)


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/model.py",
                "patterns/p49-interned-pool/inputs/gen.py",
                "patterns/p49-interned-pool/c/kernel.c",
                "patterns/p49-interned-pool/c/kernel_hardened.c",
                "patterns/p49-interned-pool/controls/threshold.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    problems = []

    # ---- 1. the walker agrees with the SHIPPED instrument -----------------
    paths = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not paths:
        print("threshold.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1
    n_win_checked = 0
    for path in paths:
        f = slb.read(path)
        stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
        if not (m49.HDR <= stride <= len(buf)):
            continue
        for w in range(len(buf) // stride):
            win = bytes(buf[w * stride:(w + 1) * stride])
            got = walk(win, SHIPPED_WIDTH[1], blank())
            want, _ = m49._sim_window(buf, w * stride, stride, True)
            n_win_checked += 1
            if got != want:
                problems.append(
                    f"{os.path.basename(path)} window {w}: this control's "
                    f"walker says {got} and model.py says {want}. The "
                    f"measurement below is then about a different program")
                break
    print(f"1. cross-check against model.py: {n_win_checked} shipped window(s), "
          f"{'AGREE' if not problems else 'DISAGREE'}")

    # ---- 2. the two configurations, on the same op streams ----------------
    print(f"\n2. {NWIN} random windows, seed {SEED}, BOTH width rules on the "
          f"SAME streams")
    rng = random.Random(SEED)
    wins = [rand_window(rng, rng.randrange(4, 40)) for _ in range(NWIN)]
    cfgs = {}
    for label, fn in (SHIPPED_WIDTH, REDUCED_WIDTH):
        st = blank()
        for win in wins:
            walk(win, fn, st)
        g = st["guard_true"] + st["guard_false"]
        st["guard_evals"] = g
        st["guard_true_pct"] = round(100.0 * st["guard_true"] / g, 2) if g else None
        st["guard_false_pct"] = round(100.0 * st["guard_false"] / g, 2) if g else None
        d = st["intern_branch"] + st["own_branch"]
        st["intern_pct"] = round(100.0 * st["intern_branch"] / d, 2) if d else None
        cfgs[label] = st

    hdr = f"{'':30s} {'intern':>9s} {'own':>9s} {'dedup hit':>10s} " \
          f"{'guard T':>9s} {'guard F':>9s} {'refuse':>7s}"
    print(hdr)
    for label, st in cfgs.items():
        print(f"{label:30s} {st['intern_branch']:9d} {st['own_branch']:9d} "
              f"{st['dedup_hit']:10d} {st['guard_true']:9d} "
              f"{st['guard_false']:9d} {st['cow_refuse']:7d}")
    print(f"\n{'':30s} {'born shared':>12s} {'born owned':>11s} "
          f"{'guard F on born-owned':>22s} {'guard F after a COW':>20s}")
    for label, st in cfgs.items():
        print(f"{label:30s} {st['born_shared']:12d} {st['born_owned']:11d} "
              f"{st['gf_born_owned']:22d} {st['gf_after_cow']:20d}")
    for label, st in cfgs.items():
        print(f"   {label:28s} threshold: intern {st['intern_pct']}% of "
              f"DEFINEs;  guard: TRUE {st['guard_true_pct']}%  FALSE "
              f"{st['guard_false_pct']}%")

    ship = cfgs[SHIPPED_WIDTH[0]]
    red = cfgs[REDUCED_WIDTH[0]]
    if ship["intern_branch"] == 0 or ship["own_branch"] == 0:
        problems.append("the SHIPPED width rule leaves one branch of the "
                        "INLINE_THRESHOLD dead, which is the defect this "
                        "control exists to rule out")
    if ship["guard_true"] == 0 or ship["guard_false"] == 0:
        problems.append(
            "the SHIPPED copy-on-write guard `rshd[t]` takes only ONE value "
            "over 20 000 random windows, so it is a tautology of the "
            "representation and `.memory/03-measurement.md` entry 19 applies to "
            "this row as it did to the reduction")
    if red["own_branch"] != 0 or red["born_owned"] != 0:
        problems.append(
            "the REDUCTION's configuration no longer shows the defect it is "
            "here to contrast with -- either the constant changed or this "
            "walker is not modelling it")
    if red["gf_born_owned"] != 0:
        problems.append(
            "the REDUCTION's guard is FALSE on a record that was BORN owned, "
            "which its dead non-interned branch makes impossible")
    if ship["born_owned"] == 0:
        problems.append(
            "the SHIPPED configuration never creates an OWNED record, so its "
            "non-interned branch is dead too and the fix did not take")

    # ---- 3. the SHIPPED blobs, per input ----------------------------------
    print("\n3. the SHIPPED blobs: how often the guard is EVALUATED and with "
          "what answer")
    rows = []
    print(f"{'input':32s} {'nwin':>5s} {'guard T':>8s} {'guard F':>8s}")
    for path in paths:
        name = os.path.basename(path)
        f = slb.read(path)
        stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
        gt = gf = nwin = 0
        if m49.HDR <= stride <= len(buf):
            nwin = len(buf) // stride
            for w in range(nwin):
                _, t, fa = m49.window_share_break(buf, w * stride, stride)
                gt += t
                gf += fa
        adv = name.startswith("adversarial-")
        rows.append({"input": name, "nwin": nwin, "guard_true": gt,
                     "guard_false": gf, "adversarial": adv})
        print(f"{name:32s} {nwin:5d} {gt:8d} {gf:8d}"
              + ("   <-- adversarial" if adv else ""))
        if not adv and gt:
            problems.append(
                f"{name} is a MATRIX input and its guard is TRUE {gt} time(s) "
                f"-- R1 would write through a borrowed buffer and diverge")
        if adv and name not in NO_OPS and not gt:
            problems.append(
                f"{name} is an ADVERSARIAL input and its guard is never TRUE, "
                f"so it exercises nothing this pattern is about")

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "threshold.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "cross_check_windows": n_win_checked,
           "seed": SEED,
           "random_windows": NWIN,
           "configurations": cfgs,
           "shipped_blobs": rows,
           "problems": problems,
           "invariant": "The SHIPPED width rule takes BOTH branches of the "
                        "INLINE_THRESHOLD and makes the copy-on-write guard "
                        "take BOTH values; the reduction's constant width "
                        "(K_CLEN 3) leaves one branch dead and the guard "
                        "constantly TRUE, which is .memory/03-measurement.md "
                        "entry 19. On the SHIPPED blobs the guard is evaluated "
                        "on every BREAK and is FALSE on every matrix input and "
                        "TRUE at least once on every adversarial one except "
                        "adversarial-stride3.bin. \u26a0 The reduction's guard "
                        "IS reachable in its false branch -- after an earlier "
                        "copy-on-write -- so what the constant width kills is "
                        "records BORN owned, not the branch. See the module "
                        "docstring and .temp/t161/red_probe/probe.py."}
    out = os.path.join(HERE, "threshold.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
