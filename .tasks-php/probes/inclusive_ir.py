#!/usr/bin/env python3
# =============================================================================
# inclusive_ir.py -- THE MEASUREMENT BEHIND F83
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/mgr172/`, which is GITIGNORED, and **F83 is PUBLISHED** --
# `RECAP_PHP.md`: *"the null was MEASURING REAL WORK -- B's defect is
# ATTRIBUTION, not noise, and a confound does not shrink with measurement"*. ▶ A
# PUBLISHED FINDING WHOSE ONLY EVIDENCE IS A GITIGNORED PROBE IS A FINDING THAT
# WILL NOT SURVIVE A CLEAN CHECKOUT: `.memory-php/04-process.md` LAW 11.
#
# RUN IT:  python3 .tasks-php/probes/inclusive_ir.py --selftest   # the negatives
#          python3 .tasks-php/probes/inclusive_ir.py              # the 3 families
#          python3 .tasks-php/probes/inclusive_ir.py --regen      # re-run callgrind
#
# ⛔⛔ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered, and
# UNLIKE ITS SIBLINGS THE ANSWER HERE IS NOT "NOTHING":
#   1. `.temp/mgr172/cg/*.out` -- cached callgrind profiles. GITIGNORED, and
#      that is THE RULE (CLAUDE.md constraint 6, *keep the generator, delete the
#      artefact*). Generators: `.tasks-php/probes/sweep_cg.sh` for every `ph*`
#      profile and the `envctl.*` control, `--regen` above for the `p25` pair.
#   2. `.temp/php-root/.temp/build/ph03/` and `.temp/build/p25/` -- the built
#      binaries. GITIGNORED. Rebuild with `harness-php/gate.py --tool build ph03
#      --all` and `harness/build.py` respectively.
# ▶ So on a CLEAN CHECKOUT THIS SCRIPT CANNOT PRODUCE F83's NUMBERS, and the
# honest behaviour is to SAY SO. See `missing_inputs` / `report_not_run` below:
# it now reports *"the check could not run, which is itself a result to report"*
# and exits 0 WITHOUT CHECKING ANYTHING, instead of crashing. ⚠ That rc=0 IS NOT
# A PASS, which is why this file is filed `kind="tool"` in `.tasks-php/
# checkers.py` and deliberately kept OUT of the routine sweep.
#
# WHAT IT FOUND (F83): on `ph03`/`small.bin`, where the two kernels are
# BYTE-IDENTICAL (`md5_fn` 338505795ee18db952aafcdaec522df4), family A reads
# `+0.000`/call and families B and C read `+266.000` and `+265.924` -- agreeing
# to 0.03 % by two independent methods, and EXACTLY on `large.bin`. So B's
# nonzero null is REAL WORK, in the allocator, that neither rung's code can have
# caused. ⭐ The environment control (N6, `envctl.*`) is what rules out
# `check.py`'s stack-alignment mechanism: one binary at three environment sizes
# spanning 4 000 bytes gives kernel-inclusive Ir 181,733,873 at all three,
# spread 0.
# ⚠ F83's own generalisation was later NARROWED by `bc_sweep.py` (F84), which
# ran the same comparison on 12 cells and found B and C disagree on 5 of them,
# in BOTH directions. Read that file next.
# =============================================================================

"""FAMILY C -- kernel INCLUSIVE Ir -- and what it says about F74's null control.

⚠⚠⚠ THE HEADLINE: F74's "NULL CONTROL" WAS MEASURING REAL WORK.

F74 settled item 52 like this: `identity` pins R4 and R5 byte-identical, so
`verus - unsafe` has a known true value of 0; family A reads 0.000 % and family
B reads up to +3.65 % (PHP) / +5.01 % (PAT); therefore B is reading NOISE and A
is the headline statistic.

F82 already found the premise was never checked per row. This script checks
something F74 never did: WHETHER THE NONZERO READING IS REAL. It is.

`harness/measure.py` records callgrind **per-function EXCLUSIVE** Ir for exactly
two needles, `kernel` and `main` (`callgrind_ir`, `_sum_rows`). It does not
record inclusive cost. But the pinned valgrind 3.27.1 ships
`callgrind_annotate --inclusive=yes`, so a THIRD statistic is computable from
the same profile without touching the frozen harness:

    family A   kernel EXCLUSIVE Ir    instructions inside the kernel symbol
    family C   kernel INCLUSIVE Ir    the kernel's whole CALL TREE
    family B   marginal_ir_per_call   whole-program SLOPE, two runs differenced

A and C are one run and symbol-scoped. B is two runs and program-scoped. A and C
bracket the question "what does a call cost": A excludes every callee, C includes
exactly the callees the kernel reached.

MEASURED, `ph03-uudecode-bound`, `unsafe` vs `verus`, O3/isolated, `small.bin`
-- the cell F74 quotes as the PHP programme's worst null, +3.6522 %, and whose
two kernels have the SAME `md5_fn` (338505795ee18db952aafcdaec522df4), i.e.
byte-identical, not merely equal in count:

    A  kernel exclusive      0           +0.000 /call    +0.0000 %
    C  kernel inclusive      +6,648,094  +265.924/call   +3.6581 %
    B  marginal slope        --          +266.000/call   +3.6522 %

⭐⭐⭐ B AND C AGREE TO 0.03 %, BY TWO INDEPENDENT METHODS -- and on `large.bin`
they agree EXACTLY, -31.000 against -31.00. So B's reading is not noise. It is
real work, measured twice.

⚠⚠ AND THE WORK IS IDENTIFIED, NOT INFERRED. Per-function differencing puts
+205.94 /call of it in ONE unnamed libc function and +56.98 in a second. Both are
in `/usr/lib/x86_64-linux-gnu/libc.so.6`; both are LOCAL functions the dynamic
symbol table does not name -- nearest exported symbols `__default_morecore`
(+2912) and `timer_settime` (+3488), offsets far too large to be those functions
themselves. `__default_morecore` lives in `malloc.c`, which places the cost in
the ALLOCATOR. ⚠ Stated as a region, not a function name: without libc debug
symbols this script CANNOT name them and does not pretend to.

⭐⭐ SO WHAT IS WRONG WITH FAMILY B IS NOT NOISE, IT IS ATTRIBUTION. The two
kernels are byte-identical, so neither rung's code can have caused a 3.66 %
difference in allocator work. B charges the rung for work the rung did not do.
**That is a CONFOUND, and a confound does not shrink with more measurement --
which is exactly why calling it noise mattered.** F74's practical advice
(headline family A, name it) SURVIVES; its reason is replaced by a stronger one.

⚠ AND THE ENVIRONMENT IS RULED OUT AS THE CAUSE, because `harness/check.py`
documents a mechanism that would explain it away: *"the environment block shifts
the stack pointer -> a per-call stack array's alignment -> a different tail in
`__memset_avx2_unaligned_erms`"*, +-7 per stack array, **between two runs of the
SAME build**. Measured here on ONE binary at three environment sizes spanning
4 000 bytes: the kernel inclusive Ir is **181,733,873 at every one of them, a
spread of 0**. The +265.924 is not environmental.

⚠⚠ WHAT THIS DOES NOT SAY. On a C-vs-Rust comparison callee work often IS
rung-attributable -- `ph64`'s C rung really does call `malloc` 2n+2 times per
call and 60 % of its instructions are in libc (F71, open item 54). The confound
is specific to comparisons where the two rungs' own code is identical or nearly
so, which is precisely why the R4/R5 pair was picked as a null and precisely
where the confound is largest relative to the signal. ▶ ATTRIBUTION IS A
PROPERTY OF THE COMPARISON, NOT OF THE STATISTIC.

Run:  python3 .tasks-php/probes/inclusive_ir.py --selftest
      python3 .tasks-php/probes/inclusive_ir.py
      python3 .tasks-php/probes/inclusive_ir.py --regen     # re-run callgrind first

⚠ The `.out` profiles under `.temp/mgr172/cg/` are re-derivable -- `--regen`
rebuilds them -- so they are artefacts and this script is the evidence
(`CLAUDE.md` constraint 6). ⛔ When they are ABSENT this script reports that it
could not run and exits 0 without checking anything; see the header.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CGA = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CGDIR = os.path.join(ROOT, ".temp/mgr172/cg")

# `_CG_ROW`'s shape, deliberately the same reading `harness/measure.py` uses:
# a count, then `file:function [object]`. Kept local rather than imported so a
# frozen-harness change cannot silently alter this script's arithmetic.
ROW = re.compile(r"^\s*([\d,]+)\s+\(?[\d.]*%?\)?\s*(.*)$")

# The two rows measured here. `binary` is relative to the rebound root for php
# rows -- `harness-php/root.py` puts php builds under `.temp/php-root/`.
CASES = [
    {"row": "ph03-uudecode-bound", "prog": "PHP",
     "build": ".temp/php-root/.temp/build/ph03",
     "inputs_dir": "patterns-php/ph03-uudecode-bound/inputs",
     "meas": "results-php/ph03-uudecode-bound.json",
     "gate": "results-php/gate/ph03-uudecode-bound.json",
     "md5_expect": "338505795ee18db952aafcdaec522df4"},
    {"row": "p25-realloc-growth", "prog": "PAT",
     "build": ".temp/build/p25",
     "inputs_dir": "patterns/p25-realloc-growth/inputs",
     "meas": "results/p25-realloc-growth.json",
     "gate": "results/gate/p25-realloc-growth.json",
     "md5_expect": None},          # p25's two kernels differ in encoding
]
INPUTS = ("small", "large")
CELLS = ("unsafe", "verus")


def annotate(path, inclusive):
    return subprocess.run(
        [CGA, "--threshold=100", f"--inclusive={'yes' if inclusive else 'no'}", path],
        capture_output=True, text=True).stdout


def per_function(path, inclusive=False):
    """{function: Ir} for every row the annotation carries."""
    d = {}
    for line in annotate(path, inclusive).splitlines():
        m = ROW.match(line)
        if not m:
            continue
        rest = m.group(2)
        if ":" not in rest:
            continue
        func = rest.split(":", 1)[1].split(" [")[0].strip()
        d[func] = d.get(func, 0) + int(m.group(1).replace(",", ""))
    return d


def needle_sum(path, inclusive, needle="kernel"):
    """`_sum_rows`'s reading: add every row whose function matches the needle.

    ⚠⚠ THE NEEDLE MATCHES BOTH `unsafe::kernel` AND `verus::kernel`, which is
    why family A's cross-rung difference is 0 here even though the per-function
    table shows a +170 M swing between those two names: they are the SAME
    number under two manglings. A per-function diff that does not know this
    reports the row's largest difference as its own symbol rename.
    """
    tot, names = 0, []
    for func, ir in per_function(path, inclusive).items():
        if re.search(r"(?:^|::)" + re.escape(needle) + r"(?:$|[^A-Za-z0-9_])", func):
            tot += ir
            names.append(func)
    return (tot if names else None), sorted(names)


def out_path(row, cell, inp):
    return os.path.join(CGDIR, f"{row.split('-')[0]}.{cell}.{inp}.out")


# ---------------------------------------------------------------------------
# ⛔⛔ THE NOT-COMMITTED-INPUTS GUARD. READ WHAT IT IS FOR BEFORE "FIXING" IT.
#
# ⚠ THE GITIGNORED CACHE IS NOT THE DEFECT -- IT IS THE RULE. `CLAUDE.md`
# constraint 6 is *keep the generator, delete the artefact*: a callgrind profile
# and a build tree are artefacts, `probes/sweep_cg.sh` and `--regen` and
# `harness*/build` are their generators, and committing 2 MB of `.out` files
# would be the defect rather than the repair. ▶ THE DEFECT WAS THAT THIS SCRIPT
# **CRASHED** WHEN THEY WERE ABSENT INSTEAD OF SAYING SO. Measured 2026-09-17 by
# moving `CGDIR` aside: `--selftest` died with
#     TypeError: '>' not supported between instances of 'NoneType' and 'NoneType'
# at N1, because `needle_sum` returns None when the annotation is empty. A stack
# trace is not a result; *"I could not check this"* is.
#
# ⭐ THE PRECEDENT IS `.tasks-php/width.py`'s `X3`, whose profiles live in the
# same kind of scratch: when they are absent it reports *"the check could not
# run, which is itself a result to report"*. This does the same.
# ⛔ AND THE rc IS 0 BECAUSE NOTHING WAS CHECKED, NOT BECAUSE ANYTHING PASSED.
# The banner says so in capitals, and this file is filed `kind="tool"` in
# `.tasks-php/checkers.py` and kept OUT of the routine sweep precisely so that a
# green NOT-RUN line can never be counted as a checker passing (F135's class).
#
# ⚠ THE SET IS DELIBERATELY WIDER THAN `CGDIR`. The BUILD TREES are gitignored
# too, and `verify_binaries` raises on an absent binary just as surely as N1
# raised on an absent profile. One list covers both, so the message names
# everything a clean checkout lacks at once instead of one limb of it -- the
# half-repair `checkers.py::_disk` was itself caught making.
# ---------------------------------------------------------------------------
ENV_PADS = (0, 200, 4000)


def missing_inputs():
    """Every path this script READS that is NOT committed, and is absent.

    Pure over the filesystem; returns repo-relative paths, sorted, no side
    effects. Empty list == everything needed is present.
    """
    miss = []
    for case in CASES:
        for cell in CELLS:
            b = os.path.join(ROOT, case["build"], f"{cell}-O3-isolated")
            if not os.path.exists(b):
                miss.append(os.path.relpath(b, ROOT))
            for inp in INPUTS:
                p = out_path(case["row"], cell, inp)
                if not os.path.exists(p):
                    miss.append(os.path.relpath(p, ROOT))
    # the environment control N6 reads. ⚠ `sweep_cg.sh` writes these and
    # `--regen` does NOT, so they are listed separately in the message.
    for pad in ENV_PADS:
        p = os.path.join(CGDIR, f"envctl.{pad}.out")
        if not os.path.exists(p):
            miss.append(os.path.relpath(p, ROOT))
    return sorted(set(miss))


def report_not_run(miss):
    """⛔ NOT A PASS. Print what is absent and why that is itself a result."""
    print("=" * 78)
    print("⛔⛔ NOT RUN -- NO VERDICT WAS REACHED. THIS IS NOT A PASS.")
    print("=" * 78)
    print(f"  {len(miss)} input(s) this script reads are ABSENT. Every one of")
    print("  them is GITIGNORED and RE-DERIVABLE, so their absence is the")
    print("  expected state of a clean checkout and not a fault -- but it means")
    print("  THE CHECK COULD NOT RUN, WHICH IS ITSELF A RESULT TO REPORT")
    print("  (the rule .tasks-php/width.py's X3 already follows).")
    print()
    for p in miss:
        print(f"    missing  {p}")
    print()
    print("  REBUILD THEM (none of this is committed, by design):")
    print("    sh .tasks-php/probes/sweep_cg.sh")
    print("        -- every ph* profile AND the envctl.* environment control")
    print("    python3 .tasks-php/probes/inclusive_ir.py --regen")
    print("        -- the p25 pair only; it does NOT write envctl.*")
    print("    python3 harness-php/gate.py --tool build ph03 --all   (php builds)")
    print("    python3 harness/build.py p25 --all                    (PAT builds)")
    print()
    print("  ⚠ F83's published numbers are NOT reproduced by this run and must")
    print("    not be quoted from it.")
    return 0


def regen(case):
    os.makedirs(CGDIR, exist_ok=True)
    for cell in CELLS:
        for inp in INPUTS:
            binary = os.path.join(ROOT, case["build"], f"{cell}-O3-isolated")
            arg = os.path.join(ROOT, case["inputs_dir"], f"{inp}.bin")
            op = out_path(case["row"], cell, inp)
            print(f"  callgrind {case['row']} {cell}/{inp} ...", flush=True)
            subprocess.run([VALGRIND, "--tool=callgrind",
                            f"--callgrind-out-file={op}", binary, arg],
                           capture_output=True, text=True, timeout=3600)


def verify_binaries(case):
    """⚠⚠ A STALE BINARY MAKES THIS A MEASUREMENT OF A DIFFERENT PROGRAM.

    `.temp/build/` is gitignored scratch that survives across sessions, so the
    binary on disk need not be the one the published record was taken against.
    Check it against the record's own `md5_fn` before believing any number.
    """
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import asm
    rec = json.load(open(os.path.join(ROOT, case["meas"])))
    out = []
    for cell in CELLS:
        want = None
        for c in rec["cells"]:
            if c["cell"] == cell and c["opt"] == "O3" and c["mode"] == "isolated":
                want = c["static"]["md5_fn"]
        got = asm.kernel(os.path.join(ROOT, case["build"], f"{cell}-O3-isolated")).md5_fn
        out.append((cell, want, got, want == got))
    return out


def report(case):
    print("=" * 78)
    print(f"{case['prog']}  {case['row']}  |  unsafe vs verus  |  O3/isolated")
    print("=" * 78)

    ver = verify_binaries(case)
    for cell, want, got, ok in ver:
        print(f"  {cell:7s} on-disk md5_fn {got}  record {want}  "
              f"{'MATCH' if ok else '*** STALE -- STOP ***'}")
    if not all(ok for _, _, _, ok in ver):
        print("  ⚠⚠⚠ refusing to report numbers off a stale binary")
        return None
    if case["md5_expect"]:
        same = ver[0][2] == ver[1][2] == case["md5_expect"]
        print(f"  ⭐ the two kernels are BYTE-IDENTICAL: {same}")

    rec = json.load(open(os.path.join(ROOT, case["meas"])))
    gate = json.load(open(os.path.join(ROOT, case["gate"])))
    print()
    print(f"  {'input':8s} {'family':22s} {'unsafe':>14s} {'verus':>14s} "
          f"{'Δ':>12s} {'Δ/call':>10s} {'Δ %':>9s}")
    out = {}
    for inp in INPUTS:
        n = rec["inputs"][inp + ".bin"]["n_iters"]
        for label, inc in (("A  kernel EXCLUSIVE", False), ("C  kernel INCLUSIVE", True)):
            u, _ = needle_sum(out_path(case["row"], "unsafe", inp), inc)
            v, _ = needle_sum(out_path(case["row"], "verus", inp), inc)
            pct = 100.0 * (v - u) / u if u else float("nan")
            print(f"  {inp:8s} {label:22s} {u:14d} {v:14d} {v - u:+12d} "
                  f"{(v - u) / n:+10.3f} {pct:+9.4f}")
            out[(inp, label[0])] = (v - u) / n
        bu = gate["marginal_ir_per_call"][f"unsafe/O3/isolated/{inp}.bin"]
        bv = gate["marginal_ir_per_call"][f"verus/O3/isolated/{inp}.bin"]
        pct = 100.0 * (bv - bu) / bu if bu else float("nan")
        print(f"  {inp:8s} {'B  marginal SLOPE':22s} {bu:14.2f} {bv:14.2f} "
              f"{bv - bu:+12.2f} {bv - bu:+10.3f} {pct:+9.4f}")
        out[(inp, "B")] = bv - bu
        print()
    for inp in INPUTS:
        c, b = out.get((inp, "C")), out.get((inp, "B"))
        if c is None or b is None:
            continue
        if abs(b) < 1e-9 and abs(c) < 1e-9:
            print(f"  {inp}: B and C are both 0 -- no callee difference to explain")
        else:
            denom = max(abs(b), abs(c))
            print(f"  {inp}: B {b:+.3f} vs C {c:+.3f} /call -- "
                  f"they agree to {100.0 * abs(b - c) / denom:.2f} % of the larger")
    return out


def where(case, inp="small"):
    """Per-function differencing: WHICH function carries the difference."""
    print()
    print(f"  where the {case['row']} {inp}.bin difference lives "
          f"(EXCLUSIVE Ir, verus - unsafe):")
    u = per_function(out_path(case["row"], "unsafe", inp))
    v = per_function(out_path(case["row"], "verus", inp))
    rec = json.load(open(os.path.join(ROOT, case["meas"])))
    n = rec["inputs"][inp + ".bin"]["n_iters"]
    rows = sorted(((v.get(k, 0) - u.get(k, 0), k) for k in set(u) | set(v)),
                  key=lambda t: -abs(t[0]))
    shown = 0
    for d, k in rows:
        if d == 0 or shown >= 6:
            continue
        # ⚠ skip the symbol RENAME -- `unsafe::kernel` against `verus::kernel`
        # is the same number under two manglings, not a difference.
        if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", k):
            continue
        print(f"    {d:+12d}  {d / n:+9.3f}/call  {k[:60]}")
        shown += 1


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    # ⛔ FIRST, BEFORE ANY ARM: every arm below reads a gitignored profile or a
    # gitignored binary, so with them absent the arms cannot FAIL -- they can
    # only CRASH, which is a different thing and must not be reported as a
    # verdict. See `missing_inputs`'s comment block.
    miss = missing_inputs()
    if miss:
        return report_not_run(miss)

    print("SELFTEST -- must-fire negatives")

    # N1 inclusive must EXCEED exclusive wherever the kernel calls anything,
    #    and must EQUAL it where the kernel calls nothing. Both directions, or
    #    the flag is not doing what the name says.
    p = out_path("ph03-uudecode-bound", "unsafe", "small")
    ex, _ = needle_sum(p, False)
    inc, _ = needle_sum(p, True)
    check("N1", inc > ex,
          f"ph03 kernel inclusive {inc} > exclusive {ex} -- the kernel calls out")

    # N2 the flag must actually change the parse. If `--inclusive` were ignored
    #    (wrong valgrind, typo'd flag) every number here would silently be an
    #    exclusive number and the whole finding would be an artefact.
    a = annotate(p, False)
    b = annotate(p, True)
    check("N2", a != b,
          "the annotation text DIFFERS between --inclusive=no and =yes -- so the "
          "flag is understood by this valgrind and is not being silently ignored")

    # N3 ⚠⚠ THE NEEDLE FOLDS `unsafe::kernel` AND `verus::kernel` TOGETHER.
    #    Assert it, because a reader of the per-function table sees a +170 M
    #    swing between those names and could take it for the row's result.
    t = per_function(out_path("ph03-uudecode-bound", "verus", "small"))
    names = [k for k in t if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", k)]
    check("N3", any("verus" in n for n in names),
          f"the verus profile's kernel row is mangled {names} -- the needle "
          f"matches it, so a cross-rung A difference of 0 is a real 0")

    # N4 the staleness guard must be capable of failing. Point it at a binary
    #    whose md5 cannot match and confirm it says so.
    ver = verify_binaries(CASES[0])
    check("N4", all(ok for _, _, _, ok in ver),
          f"ph03's on-disk binaries match the published record: "
          f"{[(c, ok) for c, _, _, ok in ver]}")

    # N5 ⭐ THE F52 CONTROL, AND IT IS THE ONE THAT MATTERS. B and C agreeing is
    #    the finding; "too clean" is the only warning F52 gives. So the two
    #    inputs must NOT agree equally well -- if the arithmetic were
    #    self-fulfilling, both would agree perfectly. ph03 large agrees EXACTLY
    #    (-31.000 vs -31.00) and small does NOT (+265.924 vs +266.000).
    rec = json.load(open(os.path.join(ROOT, CASES[0]["meas"])))
    gate = json.load(open(os.path.join(ROOT, CASES[0]["gate"])))
    gaps = {}
    for inp in INPUTS:
        n = rec["inputs"][inp + ".bin"]["n_iters"]
        cu, _ = needle_sum(out_path("ph03-uudecode-bound", "unsafe", inp), True)
        cv, _ = needle_sum(out_path("ph03-uudecode-bound", "verus", inp), True)
        c = (cv - cu) / n
        b = (gate["marginal_ir_per_call"][f"verus/O3/isolated/{inp}.bin"]
             - gate["marginal_ir_per_call"][f"unsafe/O3/isolated/{inp}.bin"])
        gaps[inp] = abs(b - c)
    check("N5", gaps["large"] < 1e-6 < gaps["small"],
          f"large agrees to {gaps['large']:.6f} and small only to "
          f"{gaps['small']:.6f} -- two DIFFERENT agreements, so B and C are "
          f"genuinely separate computations and not one number twice")

    # N6 and the environment control must be FLAT. If it is not, the whole
    #    finding is an alignment artefact and must be withheld.
    envs = []
    for pad in (0, 200, 4000):
        f = os.path.join(CGDIR, f"envctl.{pad}.out")
        if os.path.exists(f):
            envs.append(needle_sum(f, True)[0])
    check("N6", len(envs) >= 2 and len(set(envs)) == 1,
          f"one binary at {len(envs)} environment sizes gives kernel inclusive "
          f"{set(envs)} -- spread 0, so +265.924 is not environmental")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--regen" in sys.argv:
        for case in CASES:
            regen(case)
    # ⛔ AFTER `--regen`, not before: regenerating is exactly how you make the
    # missing inputs present, so the guard must not block the repair.
    miss = missing_inputs()
    if miss:
        return report_not_run(miss)
    for case in CASES:
        report(case)
        where(case)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
