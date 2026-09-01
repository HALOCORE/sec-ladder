#!/usr/bin/env python3
"""p49 CONTROLS: **the `p08` question, answered with a census instead of an
argument.**

    python3 patterns/p49-interned-pool/controls/no_overlap.py

WHY THIS EXISTS
---------------
`harness/tools/composition.py` declares `p08`'s bug class as *"two live
references to overlapping storage, one of them mutable"*, and that sentence
describes `p49` word for word. **The sharpest question a reviewer can ask this
row is whether it duplicates `p08` C-side**, and `../spec.md` answers it four
ways. Three of those four are arguments; this file is the fourth, and it is a
number.

TWO PROPERTIES, MEASURED ON THE SHIPPED BLOBS
---------------------------------------------
  A. **every copy this kernel performs has DISJOINT source and destination.**
     The only copy is the safety line's -- `mem[pbump + j] = mem[roff[t] + j]`
     -- and `../c/kernel_hardened.c` argues it can never overlap because a
     SHARED record's content lies wholly inside `mem[0 .. ARENA)` while `pbump`
     is at or above `ARENA`. Here that is re-derived from the bytes.
  B. **two records' content ranges either COINCIDE EXACTLY or are DISJOINT --
     never PARTIAL.** That is the shape of the sharing: deduplication hands back
     *the same buffer*, not an overlapping one. ⚠ **Partial overlap is the only
     kind `p08` has**, so this is the property that separates the two rows, and
     it is checked after every operation in BOTH semantics -- the buggy rung's
     record table as well as the hardened one's.

THE NEGATIVE CONTROL, AND IT MUST FIRE
--------------------------------------
A census that only ever answers "no overlap here" would pass on a program with
no copies at all, so `p08`'s own copy is put through the same question.
`p08`'s kernel decodes `d` and `nrep_w` from its window header and performs
`nrep = 1 + nrep_w % 4` copies of `memcpy(scr + dr, scr, m - dr)` with
`dr = d + r`; source `[0, m-dr)` and destination `[dr, m)` **overlap exactly
when `2*dr < m`**, and because the destination starts at `dr > 0` while the
source starts at 0, an overlap is always PARTIAL. This file:

  * synthesises `p08` windows from that documented decode -- so the arm runs
    from a fresh clone, with no dependency on `p08`'s gitignored `.bin` files --
    and requires that at least one partially-overlapping copy is found;
  * ALSO censuses `p08`'s shipped blobs when they are present, and says so when
    they are not.

⚠ **If the `p08` arm ever stops finding a partial overlap, the `p49` result
below means nothing**: the question would not be being asked.
"""

import glob
import hashlib
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
P08 = os.path.join(REPO, "patterns", "p08-overlap-move")
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, PDIR)

import slb            # noqa: E402
import model as m49   # noqa: E402

P08_SCR = 4096


def _rel(a, b):
    """`'equal'`, `'disjoint'` or `'partial'` for two half-open ranges."""
    (a0, a1), (b0, b1) = a, b
    if (a0, a1) == (b0, b1):
        return "equal"
    if a1 <= b0 or b1 <= a0:
        return "disjoint"
    return "partial"


def walk_p49(buf, off, ln, harden):
    """The kernel, instrumented: returns every copy it performs and every
    record-pair relation it ever holds."""
    copies, pairs = [], {"equal": 0, "disjoint": 0, "partial": 0}
    if ln < m49.HDR:
        return copies, pairs
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return copies, pairs
    mem = bytearray(m49.MEM)
    ekey, elen, eoff = [], [], []
    roff, rlen, rshd = [], [], []
    abump, pbump = 0, m49.ARENA
    p = m49.HDR

    def snapshot():
        for i in range(len(roff)):
            for j in range(i + 1, len(roff)):
                pairs[_rel((roff[i], roff[i] + rlen[i]),
                           (roff[j], roff[j] + rlen[j]))] += 1

    for _ in range(nops):
        if ln - p < m49.OPSZ:
            break
        c, a = buf[off + p], buf[off + p + 1]
        p += m49.OPSZ
        w, key, op = 1 + a % m49.MAXW, a % m49.NKEY, c % 4
        if op in (m49.DEFINE_A, m49.DEFINE_B):
            if len(roff) >= m49.NREC:
                pass
            elif w < m49.THRESH:
                f = len(ekey)
                for k in range(len(ekey)):
                    if ekey[k] == key and elen[k] == w:
                        f = k
                        break
                if f == len(ekey):
                    if len(ekey) < m49.NENT and abump + w <= m49.ARENA:
                        for j in range(w):
                            mem[abump + j] = m49.cbyte(key, j)
                        ekey.append(key)
                        elen.append(w)
                        eoff.append(abump)
                        roff.append(abump)
                        rlen.append(w)
                        rshd.append(1)
                        abump += w
                else:
                    roff.append(eoff[f])
                    rlen.append(w)
                    rshd.append(1)
            elif pbump + w <= m49.MEM:
                for j in range(w):
                    mem[pbump + j] = m49.cbyte(key, j)
                roff.append(pbump)
                rlen.append(w)
                rshd.append(0)
                pbump += w
        elif op == m49.BREAK and roff:
            t = a % len(roff)
            if harden and rshd[t]:
                if pbump + rlen[t] > m49.MEM:
                    snapshot()
                    continue
                copies.append((pbump, roff[t], rlen[t]))
                for j in range(rlen[t]):
                    mem[pbump + j] = mem[roff[t] + j]
                roff[t] = pbump
                rshd[t] = 0
                pbump += rlen[t]
            mem[roff[t]] = 0
        snapshot()
    return copies, pairs


# ---- the p08 negative control ----------------------------------------------
def p08_window_copies(win):
    """`p08`'s own copies, decoded from a window exactly as its kernel decodes
    it (`patterns/p08-overlap-move/c/kernel.c`)."""
    if len(win) < 4:
        return []
    d = win[0] + 256 * win[1]
    nrep_w = win[2] + 256 * win[3]
    avail = len(win) - 4
    m = min(avail, P08_SCR)
    nrep = 1 + nrep_w % 4
    if m < 2 or d == 0 or d + nrep > m:
        return []
    out = []
    for r in range(nrep):
        dr = d + r
        out.append(((dr, m), (0, m - dr)))     # (dst range, src range)
    return out


def p08_synthetic():
    """Windows built from `p08`'s documented decode, so this arm runs from a
    fresh clone. The first is the overlapping shape (`2*d < m`); the second is a
    non-overlapping one, so the arm can tell the two apart."""
    def win(d, nrep_w, body_len):
        return bytes([d & 0xFF, (d >> 8) & 0xFF,
                      nrep_w & 0xFF, (nrep_w >> 8) & 0xFF]) + bytes(body_len)
    return {"overlapping  d=4  m=64": win(4, 0, 64),
            "overlapping  d=1  m=16": win(1, 3, 16),
            "disjoint     d=40 m=64": win(40, 0, 64)}


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/model.py",
                "patterns/p49-interned-pool/inputs/gen.py",
                "patterns/p49-interned-pool/c/kernel.c",
                "patterns/p49-interned-pool/c/kernel_hardened.c",
                "patterns/p08-overlap-move/c/kernel.c",
                "patterns/p49-interned-pool/controls/no_overlap.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    problems = []
    paths = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not paths:
        print("no_overlap.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1

    print("A/B. p49, every shipped window, BOTH semantics")
    print(f"{'input':32s} {'sem':>4s} {'copies':>7s} {'src+w<=dst':>11s}  "
          f"{'pairs equal':>11s} {'disjoint':>9s} {'PARTIAL':>8s}")
    rows = []
    tot = {"copies": 0, "disjoint_copies": 0, "equal": 0, "disjoint": 0,
           "partial": 0}
    for path in paths:
        name = os.path.basename(path)
        f = slb.read(path)
        stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
        if not (m49.HDR <= stride <= len(buf)):
            print(f"{name:32s}  (no whole window -- the driver guard skips it)")
            continue
        for harden in (True, False):
            nc = ndisj = 0
            pairs = {"equal": 0, "disjoint": 0, "partial": 0}
            for w in range(len(buf) // stride):
                cps, pr = walk_p49(buf, w * stride, stride, harden)
                nc += len(cps)
                for dst, src, ww in cps:
                    if _rel((dst, dst + ww), (src, src + ww)) == "disjoint":
                        ndisj += 1
                    else:
                        problems.append(
                            f"{name} window {w}: a copy from [{src},{src+ww}) "
                            f"to [{dst},{dst+ww}) is NOT disjoint. p49's "
                            f"copy-on-write copy is claimed never to overlap, "
                            f"and that claim is what separates this row from "
                            f"p08")
                for k in pairs:
                    pairs[k] += pr[k]
            tag = "R1h" if harden else "R1"
            rows.append({"input": name, "semantics": tag, "copies": nc,
                         "disjoint_copies": ndisj, **pairs})
            print(f"{name:32s} {tag:>4s} {nc:7d} {ndisj:11d}  "
                  f"{pairs['equal']:11d} {pairs['disjoint']:9d} "
                  f"{pairs['partial']:8d}")
            tot["copies"] += nc
            tot["disjoint_copies"] += ndisj
            for k in ("equal", "disjoint", "partial"):
                tot[k] += pairs[k]
            if pairs["partial"]:
                problems.append(
                    f"{name} ({tag}): {pairs['partial']} record-pair(s) hold "
                    f"PARTIALLY overlapping content ranges. p49's sharing is "
                    f"claimed to be exact -- deduplication hands back THE SAME "
                    f"buffer -- and partial overlap is p08's shape, not this "
                    f"row's")

    print(f"\n  p49 totals: {tot['copies']} copy/copies, "
          f"{tot['disjoint_copies']} of them disjoint; record pairs "
          f"{tot['equal']} EQUAL, {tot['disjoint']} disjoint, "
          f"{tot['partial']} PARTIAL")
    if tot["equal"] == 0:
        problems.append(
            "no two records ever hold the SAME buffer on any shipped input, so "
            "this census is not looking at a deduplicating pool and property B "
            "is vacuous")

    # ---- the negative control ------------------------------------------
    print("\nC. the NEGATIVE CONTROL -- p08's own copy, same question")
    p08_rows, n_partial = [], 0
    for label, win in p08_synthetic().items():
        rels = [_rel(dst, src) for dst, src in p08_window_copies(win)]
        n_partial += rels.count("partial")
        p08_rows.append({"window": label, "source": "synthetic",
                         "relations": rels})
        print(f"    synthetic {label:26s} {rels}")
    p08_bins = sorted(glob.glob(os.path.join(P08, "inputs", "*.bin")))
    if not p08_bins:
        print("    p08's shipped blobs are ABSENT (gitignored). Regenerate "
              "with: python3 patterns/p08-overlap-move/inputs/gen.py")
        p08_rows.append({"window": None, "source": "shipped", "relations": None})
    for path in p08_bins:
        name = os.path.basename(path)
        f = slb.read(path)
        stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
        if not (4 <= stride <= len(buf)):
            continue
        cnt = {"equal": 0, "disjoint": 0, "partial": 0}
        for w in range(len(buf) // stride):
            win = bytes(buf[w * stride:(w + 1) * stride])
            for dst, src in p08_window_copies(win):
                cnt[_rel(dst, src)] += 1
        n_partial += cnt["partial"]
        p08_rows.append({"window": name, "source": "shipped", **cnt})
        print(f"    shipped   {name:26s} equal={cnt['equal']} "
              f"disjoint={cnt['disjoint']} PARTIAL={cnt['partial']}")
    print(f"\n  p08 partially-overlapping copies found: {n_partial}")
    if n_partial == 0:
        problems.append(
            "THE NEGATIVE CONTROL DID NOT FIRE: no partially-overlapping copy "
            "was found in p08 at all, so this census cannot distinguish the two "
            "rows and p49's zero above means nothing")

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "no_overlap.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "p49": rows,
           "p49_totals": tot,
           "p08_control": p08_rows,
           "p08_partial_copies": n_partial,
           "problems": problems,
           "invariant": "In p49, every copy has disjoint source and "
                        "destination, and two records' content ranges are "
                        "always EQUAL or DISJOINT and never PARTIAL, in both "
                        "semantics on every shipped window; in p08 at least one "
                        "copy is PARTIALLY overlapping, which is what makes the "
                        "first half a distinction rather than a tautology."}
    out = os.path.join(HERE, "no_overlap.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
