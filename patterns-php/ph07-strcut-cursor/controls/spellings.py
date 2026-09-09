#!/usr/bin/env python3
"""ph07 control -- **THE IN-CONTRACT SPELLING SPAN, BOTH SIDES SEARCHED.**

    python3 patterns-php/ph07-strcut-cursor/controls/spellings.py
    python3 patterns-php/ph07-strcut-cursor/controls/spellings.py --audit-only
    python3 patterns-php/ph07-strcut-cursor/controls/spellings.py --verus

⭐ **THE FIRST `controls/spellings.py` IN `patterns-php/`.** `.memory-php/02`
records the debt on both built php rows: *"NO RATIO HERE IS THE COST OF SAFETY,
AND THESE ARE `fixed-R4 bound`s -- PAT's term, and PAT's rule is that a bound
ships LABELLED, beside a cheapest-found counterpart."* `ph03`'s own hashed `why`
has demanded it since the row was built. This file discharges it for `ph07`.

WHAT SHIPS, AND WHAT THIS FILE DOES *NOT* DO
--------------------------------------------
⚠⚠⚠ **IT DOES NOT RE-SHIP A RUNG.** `.memory/02-bench-rules.md`: the shipped
rung is chosen by IDIOM, before measurement, and it stays. What a cheaper
in-contract spelling moves is the **published bound**, and TWO numbers ship,
labelled:

    fixed-R4 bound              R3ship - R4ship          both held by fiat
    cheapest-found in-contract  inf(R3 found) - R4ship   name the spelling
                                                          AND the input

and NO PAIR INTERVAL: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts
that construction in terms; this file does not resurrect it.

⚠⚠ **`TASK_PHP_017` B1 FOUND THE R3-SIDE LEVER AND ITS NUMBER IS NOT REUSED
HERE.** B1 measured `+13.50 % -> +2.62 %` on the corpus `inputs/gen.py` shipped
at the time, which had `from + length <= string->len` on every window because
R1h then carried `cb3cca21b345` hunk (b). `TASK_PHP_018` removed hunk (b) (see
`c/kernel_hardened.c`) and the corpus now spans the whole benign domain, so
**every one of those figures is about a corpus that no longer exists** and is
re-derived from scratch below. Quoting a figure measured against a deleted
corpus is the defect this programme keeps finding; it is not going to be
committed here.

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of.

R3 side, from `../safe_tuned.rs` -- all safe, no `unsafe` token:

  `v0_shipped`      the shipped R3, unmodified.
  `r3_reslice`      ⭐ TASK_PHP_017 B1's `v1`: `&s[..=frm]` before the start
                    walk and `&s[..=k]` before the end walk. After `R1h` the
                    kernel knows `frm <= slen` and `s.len() == slen + 1`, and
                    the end walk is entered only when `k < slen`, so BOTH
                    re-slices are facts the guards have already established --
                    the panic branch is unreachable and LLVM can see it. This
                    is not an in-loop bound (`../spec.md` `forbidden[1]`); it
                    re-expresses ONCE, OUTSIDE the loop, something two lines
                    above already proved.
  `r3_reslice_st`   the start walk only. Isolates which walk pays.
  `r3_reslice_en`   the end walk only. The other half of the same isolation.
  `r3_get_unwrap`   ⚠ the NEGATIVE: `s.get(n).unwrap_or(&0)`. It is safe, it is
                    total, it looks like the obvious answer, and TASK_PHP_017
                    measured it WORSE than the shipped R3. Kept because a
                    spelling search with no losing entry is a search nobody can
                    calibrate.

R4 side, from `../unsafe.rs` -- ⚠⚠ **and `../spec.md` pins
`identity: unsafe == verus`, so an R4 candidate is not merely a program that MAY
use `unsafe`: it must have a `verus.rs` twin that VERIFIES.** Each R4 variant's
substitution is therefore applied to `../verus.rs` as well and the result is put
through Verus; one that does not verify is a CONTROL and not a rung, which is
`p16`'s `r4_hdr` and `p42`'s `endptr` precedent.

  `v0_shipped`      the shipped R4, unmodified.
  `r4_index0`       the FIRST table read spelled `s[0]` instead of
                    `*s.get_unchecked(0)`. The index is a literal into a slice
                    the kernel has just proved is at least `slen + 1` long, so
                    rustc should elide the check. If it is free this is a
                    STRICTLY BETTER R4 -- same cost, one fewer use of a trusted
                    item. (`p34`'s `r4_readdirect` shape, re-derived here rather
                    than inherited.)
  `r4_fused`        the copy loop and the fold loop MERGED into one pass. Both
                    still touch every one of the `cnt` bytes -- nothing is
                    deleted -- but the second traversal of `out` goes.
  `r4_nozero`       `Vec::with_capacity(cap)` + `set_len(cap)` instead of
                    `vec![0u8; cap]`, i.e. do not `memset` `cap` bytes the copy
                    is about to overwrite. ⚠ Expected INADMISSIBLE and included
                    anyway: it leaves the four trailing NULs and the `cap - cnt`
                    tail uninitialised, which the fold never reads but which is
                    a `set_len` on uninitialised memory, and the pinned vstd has
                    no spec that makes that sound. A refusal with a reason is a
                    result (`p42` `endptr`).

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**. A variant
    nobody audited is a number about a different benchmark (`p05`'s lesson).
    ⚠ The token audit is not the whole admission test: `../spec.md`'s per-entry
    ENGLISH decides polarity and scope and no gate stage reproduces it, so
    `admissible` is THREE-VALUED here and the third value is a sentence.
  * every variant prints the SHIPPED checksum on every one of the seven inputs,
    adversarial included. A respelling that changed the answer is not one.
  * ⚠⚠ **`Ir` per kernel call is measured the way `harness/measure.py` MEASURES
    THE SHIPPED CELLS** -- kernel-exclusive `Ir` off the pinned callgrind on the
    SHIPPED `small.bin` and `large.bin` at their own `n_iters`, divided by
    `n_iters` -- and NOT by `check.py`'s 100-vs-200 marginal. ⚠ The first draft
    of this file used the 100/200 marginal and its `v0_shipped` figures came out
    **1 % from the record** (R3 2084.1 where the record says 2061.3). They are
    different statistics, not a discrepancy: the driver picks its window from a
    checksum, so 200 iterations visit a different SAMPLE of the 32 or 2 050
    windows from 25 000. **A control that is going to be quoted beside the row's
    headline has to compute the row's headline**, and there is nothing to cancel
    -- `kernel_exclusive_ir` already excludes the loader.
  * the pipeline reproduces the SHIPPED cells' recorded numbers before any
    variant is quoted, and prints the delta. If `v0_shipped` does not match
    `results-php/ph07-strcut-cursor.json` this file has measured something else
    and says so.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**
    `r4_fused` measures 0.007 % below the shipped R4 and has a WORSE fixed term;
    reading that as "the R4 endpoint moves" would be exactly the over-reading
    this file exists to prevent.
"""

import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import struct  # noqa: F401 -- kept: the probe-input rewriter it served was
                  # deleted at TASK_PHP_018 when this file switched to the
                  # shipped inputs; re-adding one is a two-line change.
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(PDIR, "..", ".."))
SCRATCH = os.path.join(REPO, ".temp", "php18", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph07-strcut-cursor.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph07-strcut-cursor.json`
#: carries and therefore what NOTES.md 8 quotes.
PROBES = (("small.bin", 553, 25_000), ("large.bin", 4074, 12_000))
#: Below this, two cells are a TIE and neither is "cheaper". 0.05 % is ~15x the
#: largest difference this file has seen between two runs of one binary, and
#: ~7x `r4_fused`'s margin over the shipped R4.
TIE_PCT = 0.05

# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]})
# `file` is "rs" for the rung source and "verus" for the R5 twin.

_RESLICE_ST = [
    ("    let mut n: usize = mbtab(s[0]) as usize;\n",
     "    let w0: &[u8] = &s[..=frm];\n"
     "    let mut n: usize = mbtab(w0[0]) as usize;\n", 1),
    ("        start = n;\n        let m: usize = mbtab(s[n]) as usize;\n",
     "        start = n;\n        let m: usize = mbtab(w0[n]) as usize;\n", 1),
]
_RESLICE_EN = [
    ("        end = start;\n        while n <= k {\n            end = n;\n"
     "            let m: usize = mbtab(s[n]) as usize;\n",
     "        let w1: &[u8] = &s[..=k];\n        end = start;\n"
     "        while n <= k {\n            end = n;\n"
     "            let m: usize = mbtab(w1[n]) as usize;\n", 1),
]

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}),
    ("r3_reslice", "R3",
     "TASK_PHP_017 B1's v1 -- `&s[..=frm]` and `&s[..=k]`, one hoisted check "
     "per walk instead of one per iteration",
     {"rs": _RESLICE_ST + _RESLICE_EN}),
    ("r3_reslice_st", "R3", "the START walk re-sliced, the end walk untouched",
     {"rs": _RESLICE_ST}),
    ("r3_reslice_en", "R3", "the END walk re-sliced, the start walk untouched",
     {"rs": _RESLICE_EN}),
    ("r3_get_unwrap", "R3",
     "`s.get(n).unwrap_or(&0)` -- safe, total, plausible, and MEASURED WORSE "
     "than the shipped R3 at TASK_PHP_017",
     {"rs": [("    let mut n: usize = mbtab(s[0]) as usize;\n",
              "    let mut n: usize = mbtab(*s.get(0).unwrap_or(&0)) as usize;\n", 1),
             ("        let m: usize = mbtab(s[n]) as usize;\n",
              "        let m: usize = mbtab(*s.get(n).unwrap_or(&0)) as usize;\n", 2)]}),
]

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}),
    ("r4_index0", "R4",
     "the first table read spelled `s[0]`; the index is a literal into a slice "
     "already known to be `slen + 1` long, so if this is free it is a strictly "
     "better R4 -- same cost, one fewer use of a trusted item",
     {"rs": [("mbtab(unsafe { *s.get_unchecked(0) })", "mbtab(s[0])", 1)],
      "verus": [("mbtab(get_unchecked(s, 0))", "mbtab(s[0])", 1)]}),
    ("r4_fused", "R4",
     "the copy loop and the fold loop merged into ONE pass over `cnt` bytes. "
     "Nothing is deleted -- every byte is still written to `out` and still "
     "folded -- what goes is the second traversal",
     {"rs": [("""    let mut i: usize = 0;
    while i < cnt {
        unsafe { *out.get_unchecked_mut(i) = *s.get_unchecked(start + i) };
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < cnt {
        acc = acc.wrapping_mul(31)
                 .wrapping_add(unsafe { *out.get_unchecked(j) } as u64);
        j = j + 1;
    }
""",
              """    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < cnt {
        let b: u8 = unsafe { *s.get_unchecked(start + i) };
        unsafe { *out.get_unchecked_mut(i) = b };
        acc = acc.wrapping_mul(31).wrapping_add(b as u64);
        i = i + 1;
    }
""", 1)],
      "verus": [("""    let mut i: usize = 0;
    while i < cnt
        invariant
            i <= cnt,
            cnt == end - start,
            start + cnt <= s@.len(),
            out@.len() == cap,
            cap == cnt + 8,
            forall|t: int| 0 <= t < i ==> out@[t] == s@[start + t],
        decreases cnt - i,
    {
        vset_unchecked(&mut out, i, get_unchecked(s, start + i));
        i = i + 1;
    }
    proof {
        lemma_fold_shift(s@, out@, start as int, cnt as int, 0);
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < cnt
        invariant
            j <= cnt,
            cnt <= out@.len(),
            acc == fold_out(out@, 0, j as int, 0),
        decreases cnt - j,
    {
        acc = acc.wrapping_mul(31).wrapping_add(vget_unchecked(&out, j) as u64);
        j = j + 1;
    }
""",
                 """    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < cnt
        invariant
            i <= cnt,
            cnt == end - start,
            start + cnt <= s@.len(),
            out@.len() == cap,
            cap == cnt + 8,
            acc == fold_out(s@, start as int, start + i as int, 0),
        decreases cnt - i,
    {
        let b: u8 = get_unchecked(s, start + i);
        vset_unchecked(&mut out, i, b);
        acc = acc.wrapping_mul(31).wrapping_add(b as u64);
        i = i + 1;
    }
""", 1)]}),
    ("r4_nozero", "R4",
     "`Vec::with_capacity(cap)` + `set_len(cap)` instead of `vec![0u8; cap]` -- "
     "do not memset `cap` bytes the copy overwrites. Expected INADMISSIBLE: it "
     "is `set_len` over uninitialised memory and the pinned vstd has no spec "
     "that makes it sound",
     {"rs": [("    let mut out: Vec<u8> = vec![0u8; cap];\n",
              "    let mut out: Vec<u8> = Vec::with_capacity(cap);\n"
              "    unsafe { out.set_len(cap) };\n", 1)]}),
]


# ---- machinery ---------------------------------------------------------------
def load_check():
    spec = importlib.util.spec_from_file_location(
        "slb_check", os.path.join(REPO, "harness", "check.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def contract():
    txt = open(os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt,
                                re.S).group(1))


def apply_subs(src, subs):
    for old, new, hits in subs:
        n = src.count(old)
        assert n == hits, (f"spellings.py: expected {hits} occurrence(s) of\n"
                           f"{old!r}\nfound {n}. The shipped rung has moved "
                           f"under this variant; fix the substitution rather "
                           f"than the assertion.")
        src = src.replace(old, new)
    return src


def materialise(name, side, subs):
    """Write the variant's sources into SCRATCH, driver path absolutised."""
    os.makedirs(SCRATCH, exist_ok=True)
    base = "safe_tuned.rs" if side == "R3" else "unsafe.rs"
    src = open(os.path.join(PDIR, base), encoding="utf-8").read()
    src = apply_subs(src, subs.get("rs", []))
    src = src.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
    p = os.path.join(SCRATCH, f"{side}_{name}.rs")
    open(p, "w", encoding="utf-8").write(src)
    vp = None
    if side == "R4":
        v = open(os.path.join(PDIR, "verus.rs"), encoding="utf-8").read()
        v = apply_subs(v, subs.get("verus", subs.get("rs", [])))
        v = v.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
        vp = os.path.join(SCRATCH, f"{side}_{name}_verus.rs")
        open(vp, "w", encoding="utf-8").write(v)
    return p, vp


def build(rs, out):
    """`harness/build.py`'s own rustc flags for an `-O3 isolated` cell."""
    cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
           "-C", "opt-level=3", "-C", "debug-assertions=off",
           "--cfg", "slb_isolated", rs, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return (out, None) if r.returncode == 0 else (None, r.stderr[-1500:])


def run(exe, path):
    r = subprocess.run([exe, path], capture_output=True, text=True, timeout=900)
    return r.stdout.strip()


_KIR = re.compile(r"^\s*([0-9,]+)\s", re.M)


def kernel_ir(exe, path, tag):
    """Kernel-EXCLUSIVE Ir, off the pinned callgrind, same as the harness."""
    out = os.path.join(SCRATCH, f"cg.{tag}")
    subprocess.run([VALGRIND, "--tool=callgrind",
                    "--callgrind-out-file=" + out, exe, path],
                   capture_output=True, text=True, timeout=3600)
    ann = subprocess.run(
        [os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate"),
         "--threshold=100", out], capture_output=True, text=True, timeout=600)
    tot = None
    for ln in ann.stdout.splitlines():
        if ":kernel" in ln or ln.strip().endswith("kernel"):
            m = _KIR.match(ln)
            if m:
                tot = int(m.group(1).replace(",", ""))
                break
    if os.path.exists(out):
        os.unlink(out)
    return tot


def verus_ok(vp):
    r = subprocess.run([sys.executable, VERUS_RUN, vp],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    if not m:
        return False, txt.strip()[-400:]
    return m.group(2) == "0", m.group(0)


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in ../spec.md's `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics rather than a stricter invention:

      * a `forbidden` hit DISQUALIFIES -- `check.py`'s stage 0 has hard-failed
        on one since TASK_068, and its scope is universal by the key's own
        meaning, so it is decidable with no English involved;
      * a `required` miss is REPORTED and does not -- `check.py` records those
        as `pins_nothing` / `absent` and never fails on them, because which
        rungs a `required` entry scopes to lives in the entry's ENGLISH and no
        gate stage reproduces it.

    ⚠ Getting this backwards is not a conservative error. `required[5]` pins
    three spellings of the mblen_table -- a C one, a Rust one and a Verus one --
    so EVERY rung misses two of them by construction, and an audit that treated
    a `required` miss as disqualifying would refuse the shipped rungs
    themselves. Measured at TASK_PHP_018: the first draft of this file did
    exactly that and reported `v0_shipped` as out of contract.
    ⚠ `admissible` is still THREE-VALUED. The token audit decides what a grep
    can decide; the third value is a sentence, and for each variant it is in
    the `why` above."""
    forb, miss = [], []
    for key, sink in (("required", miss), ("forbidden", forb)):
        for i, e in enumerate(decl.get(key) or []):
            txt = e.get(lang) if isinstance(e, dict) else e
            if not isinstance(txt, str):
                continue
            for tok in re.findall(r"`([^`]+)`", txt):
                hit = chk.spelling_matches(tok, src, lang=lang)
                if key == "forbidden" and hit:
                    sink.append(f"forbidden[{i}] `{tok}` PRESENT")
                elif key == "required" and not hit:
                    sink.append(f"required[{i}] `{tok}`")
    return forb, miss


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit; no build, no callgrind")
    ap.add_argument("--verus", action="store_true",
                    help="also put every R4 variant through Verus")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    chk = load_check()
    decl = contract()["idiom"]
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("spellings.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    variants = R3_VARIANTS + R4_VARIANTS
    rows = {}
    print("0. THE SPELLING AUDIT -- every backticked idiom entry, "
          "harness/check.py::spelling_matches")
    for name, side, why, subs in variants:
        rs, vp = materialise(name, side, subs)
        src = open(rs, encoding="utf-8").read()
        forb, miss = audit(chk, decl, src)
        rows[(side, name)] = {"side": side, "name": name, "why": why,
                              "rs": rs, "verus_rs": vp,
                              "forbidden_hits": forb, "required_absent": miss,
                              "in_contract": not forb}
        print(f"  {side} {name:16s} "
              + ("IN CONTRACT" if not forb else "OUT: " + "; ".join(forb))
              + f"   ({len(miss)} required spelling(s) absent -- reported, "
                f"not disqualifying)")
        if forb and name != "v0_shipped":
            print(f"      -> not quoted as a rung candidate")
    if args.audit_only:
        return 0

    print("\n1. BUILD + CHECKSUM -- a respelling that changes the answer "
          "is not one")
    ship = {}
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"], os.path.join(SCRATCH, f"{side}_{name}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side} {name:16s} BUILD FAILED")
            if name == "v0_shipped":
                problems.append(f"{side} v0_shipped does not build")
            continue
        r["exe"] = exe
        answers = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = answers
        if name == "v0_shipped":
            ship[side] = answers
            print(f"  {side} {name:16s} ok  "
                  + " ".join(f"{k.split('.')[0][:14]}={v[:8]}"
                             for k, v in list(answers.items())[:3]) + " ...")
        else:
            diff = [k for k, v in answers.items() if ship[side].get(k) != v]
            print(f"  {side} {name:16s} "
                  + ("ok  identical on all "
                     f"{len(answers)} inputs" if not diff
                     else f"*** DIFFERS on {diff}"))
            if diff:
                problems.append(f"{side} {name} changes the answer on {diff} "
                                f"-- it is not a respelling of this kernel")
                r["in_contract"] = False

    print("\n2. THE PRICE -- kernel-exclusive Ir per call on the SHIPPED "
          "inputs, harness/measure.py's own statistic")
    sm_st, lg_st = PROBES[0][1], PROBES[1][1]
    print(f"  {'cell':28s} {'Ir/call small':>14s} {'Ir/call large':>14s} "
          f"{'Ir/win-byte':>12s} {'fixed/call':>11s} {'vs R4ship':>10s}")
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if not r.get("exe"):
            continue
        per = {}
        for inp, stride, nit in PROBES:
            tot = kernel_ir(r["exe"], os.path.join(PDIR, "inputs", inp),
                            f"{side}.{name}.{inp}")
            per[inp] = None if tot is None else tot / float(nit)
        r["ir_small"] = per[PROBES[0][0]]
        r["ir_large"] = per[PROBES[1][0]]
        if r["ir_small"] is None or r["ir_large"] is None:
            problems.append(f"{side} {name}: callgrind gave no kernel figure")
            continue
        slope = (r["ir_large"] - r["ir_small"]) / float(lg_st - sm_st)
        fixed = r["ir_small"] - slope * sm_st
        r["ir_per_window_byte"], r["fixed_per_call"] = slope, fixed
    base4 = rows[("R4", "v0_shipped")].get("ir_per_window_byte")
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if r.get("ir_per_window_byte") is None:
            continue
        vs = (100.0 * (r["ir_per_window_byte"] - base4) / base4
              if base4 else None)
        r["pct_vs_r4ship"] = vs
        print(f"  {side + ' ' + name:28s} {r['ir_small']:14.1f} "
              f"{r['ir_large']:14.1f} {r['ir_per_window_byte']:12.4f} "
              f"{r['fixed_per_call']:11.1f} "
              + (f"{vs:+9.2f}%" if vs is not None else f"{'--':>10s}"))

    print("\n3. DOES THIS PIPELINE REPRODUCE THE SHIPPED CELLS?")
    rec_ok = None
    if os.path.exists(RECORD):
        rec = json.load(open(RECORD))
        want = {}
        nit = {i: n for i, _, n in PROBES}
        for c in rec.get("cells", []):
            if c.get("opt") == "O3" and c.get("mode") == "isolated":
                for inp, blk in (c.get("ir") or {}).items():
                    if inp in nit and blk and blk.get("kernel_exclusive_ir"):
                        want[(c["cell"], inp)] = (blk["kernel_exclusive_ir"]
                                                  / float(nit[inp]))
        pairs = [("safe_tuned", "R3"), ("unsafe", "R4")]
        rec_ok = True
        for cell, side in pairs:
            for inp, key in (("small.bin", "ir_small"), ("large.bin", "ir_large")):
                w = want.get((cell, inp))
                g = rows[(side, "v0_shipped")].get(key)
                if w is None or g is None:
                    print(f"  {cell:12s} {inp:10s} record={w} here={g}  "
                          f"(not comparable)")
                    continue
                d = abs(w - g) / w * 100.0
                print(f"  {cell:12s} {inp:10s} record={w:10.4f} "
                      f"here={g:10.4f}  delta={d:.3f}%")
                if d > 0.5:
                    rec_ok = False
                    problems.append(
                        f"{cell}/{inp}: this pipeline measures {g:.4f} where "
                        f"the shipped record says {w:.4f} ({d:.2f}% apart) -- "
                        f"the variants below are then about a different "
                        f"benchmark from the row")
    else:
        print(f"  no measurement record at {RECORD}")

    if args.verus:
        print("\n4. R4 ADMISSIBILITY -- ../spec.md pins `identity: unsafe == "
              "verus`, so every R4 candidate needs a twin that VERIFIES")
        for name, side, why, subs in R4_VARIANTS:
            r = rows[(side, name)]
            if not r.get("verus_rs"):
                continue
            ok, msg = verus_ok(r["verus_rs"])
            r["verus_verifies"], r["verus_msg"] = ok, msg
            if not ok:
                r["in_contract"] = False
            print(f"  R4 {name:16s} {'VERIFIES' if ok else 'DOES NOT VERIFY'}"
                  f"   {msg.splitlines()[0][:90] if msg else ''}")
            if not ok and name == "v0_shipped":
                problems.append("R4 v0_shipped's twin does not verify -- this "
                                "pipeline is not measuring the shipped rung")
    else:
        print("\n4. R4 ADMISSIBILITY -- skipped (pass --verus). ⚠ Until it is "
              "run, no R4 variant below is a RUNG; each is a control.")

    # ---- the two published numbers -----------------------------------------
    print("\n5. THE TWO NUMBERS THAT MAY BE QUOTED, LABELLED")
    r3s = rows[("R3", "v0_shipped")]
    r4s = rows[("R4", "v0_shipped")]
    cands = [r for (side, nm), r in rows.items()
             if side == "R3" and r.get("in_contract")
             and r.get("ir_per_window_byte") is not None]
    best = min(cands, key=lambda r: r["ir_per_window_byte"]) if cands else None
    print(f"  fixed-R4 bound              R3ship - R4ship            "
          f"{r3s.get('pct_vs_r4ship', float('nan')):+.2f}%   "
          f"({r3s.get('ir_per_window_byte', 0):.4f} vs "
          f"{r4s.get('ir_per_window_byte', 0):.4f} Ir/window byte)")
    if best is not None:
        print(f"  cheapest-found in-contract  inf(R3 found) - R4ship     "
              f"{best.get('pct_vs_r4ship', float('nan')):+.2f}%   "
              f"spelling `{best['name']}`, inputs small.bin + large.bin")
    r4c = [r for (side, nm), r in rows.items()
           if side == "R4" and r.get("in_contract")
           and r.get("ir_per_window_byte") is not None]
    b4r = r4s.get("ir_per_window_byte")
    beat = [r for r in r4c
            if r["name"] != "v0_shipped" and b4r
            and (b4r - r["ir_per_window_byte"]) / b4r * 100.0 > TIE_PCT]
    print(f"  ⚠ R4 SIDE, SEARCHED ({len(r4c)} admissible of "
          f"{len(R4_VARIANTS)} tried):")
    for r in sorted(r4c, key=lambda r: r["ir_per_window_byte"]):
        d = (r["ir_per_window_byte"] - b4r) / b4r * 100.0 if b4r else 0.0
        verdict = ("SHIPPED" if r["name"] == "v0_shipped"
                   else ("TIE (< %.2f%%)" % TIE_PCT if abs(d) <= TIE_PCT
                         else ("CHEAPER" if d < 0 else "dearer")))
        print(f"      {r['name']:16s} {r['ir_per_window_byte']:.4f} "
              f"Ir/window byte  {d:+.3f}%  fixed/call "
              f"{r['fixed_per_call']:.1f}   {verdict}")
    for (side, nm), r in sorted(rows.items()):
        if side == "R4" and not r.get("in_contract"):
            print(f"      {nm:16s} INADMISSIBLE -- "
                  + ("no verifying twin" if r.get("verus_verifies") is False
                     else "see stage 0/1"))
    if not beat:
        print("  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              "DEGENERATE on this row,\n     so the fixed-R4 bound above is a "
              "bound over a searched endpoint and not an\n     unsearched one. "
              "A clean negative, and it is the honest counterpart to the R3 "
              "result.")
    else:
        print(f"  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS ({beat[0]['name']}); the "
              f"published bound moves and the\n     headline was an artefact "
              f"of an unsearched R4 side.")
    print("  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it).")

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph07-strcut-cursor/controls/spellings.py "
                "--verus",
            "note":
                "The pin covers the two rung sources the variants are derived "
                "from, verus.rs (the R4 admissibility half), spec.md (the "
                "declaration the audit runs against), inputs/gen.py (the corpus "
                "every number is measured over) and this script. It does NOT "
                "cover results-php/ph07-strcut-cursor.json: stage 3 compares "
                "against that record at run time and prints the delta, which is "
                "a stronger check than a hash of it."},
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # ⚠⚠ REPO-RELATIVE KEYS, AND THE GATE MEASURES THAT.
        # `check.py` stage 9b re-hashes these paths against the REPO root and
        # refuses the run with `pins N of N source(s) that are ABSENT ... its
        # numbers are UNDATED` if it cannot find them. A first draft wrote
        # ROW-relative keys (`safe_tuned.rs`) and the gate caught it: the pin
        # existed, named the right files, and checked nothing.
        # ⚠ On a php row the REPO the gate runs against is the shim root, where
        # `patterns` is a symlink to `patterns-php`, so `patterns/<row>/...` is
        # the spelling that resolves in BOTH trees.
        "derived_from_sha256": {
            f"patterns/{ROW}/{rel}":
                hashlib.sha256(open(os.path.join(PDIR, rel), "rb").read()
                               ).hexdigest()
            for rel in ("safe_tuned.rs", "unsafe.rs", "verus.rs",
                        "spec.md", "inputs/gen.py",
                        "controls/spellings.py")},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        "statistic": "kernel_exclusive_ir / n_iters on the SHIPPED inputs -- "
                     "harness/measure.py's own, so stage 3 above compares "
                     "against results-php/ph07-strcut-cursor.json directly",
        "reproduces_shipped_record": rec_ok,
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "Every variant is in contract by harness/check.py::spelling_matches "
            "over EVERY backticked idiom entry, returns the shipped checksum on "
            "all seven inputs, and is priced by the harness's own two-point "
            "marginal-Ir method on both probe inputs. TWO numbers ship, "
            "labelled: the fixed-R4 bound and the cheapest-found in-contract "
            "counterpart. NO PAIR INTERVAL.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
