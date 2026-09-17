#!/usr/bin/env python3
# =============================================================================
# ph64_draws.py -- THE PROBE **F89** AND **F90** BOTH REST ON. ONE FILE, TWO
# FINDINGS, AND ONE OF THEM REFUTES A PUBLISHED RECOMMENDATION
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr173/`, which is GITIGNORED.
#
#   F89 (RECAP_PHP.md:6636, landed 2026-09-12, commit 27895aa) -- cited as
#       *"`--selftest` PASS, 5 negatives"*. Its `0.07 pp` same-language spread
#       and its N4 control (`0.034 %` against F88's `0.03 %`) are THIS FILE's
#       output. ⭐ MITIGATED, and say so: `TASK_PHP_043` §5.7 reproduced the
#       CONTRAST at 55.6x by a DIFFERENT design, so F89's conclusion survives
#       the loss of this file -- **its two published figures do not.**
#   F90 (RECAP_PHP.md:6570, landed 2026-09-12, commit adef454) -- *"this file's
#       data RE-SLICED"*. The re-slice is the WHOLE of F90, and F90 refutes a
#       published recommendation. ▶ **There is no second method for F90.**
#
# `.memory-php/04-process.md` LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17,
# repo at commit f4bda71. ⚠ F89 is REVIEWED-AND-NARROWED; **F90 is REFUTED on
# its operative half by F92** -- read both section headers before quoting either.
#
# ⛔⛔⛔ IT IS **NOT** IN THE ROUTINE SWEEP, AND THE REASON IS NOT COST ALONE.
# Filed `kind="tool"` in `.tasks-php/checkers.py`, same call as
# `probes/inclusive_ir.py` and `probes/bc_sweep.py`. It needs FOUR things a
# clean checkout does not have:
#   (1) the PINNED valgrind at `~/tools/valgrind/` (outside this repo);
#   (2) GITIGNORED build trees under `.temp/php-root/.temp/build/{ph64,ph03}/`;
#   (3) GITIGNORED fixture blobs `patterns-php/*/inputs/small.bin` (generator:
#       each row's `inputs/gen.py`);
#   (4) 80 GITIGNORED callgrind profiles under `.temp/mgr173/cg/`, which THIS
#       SCRIPT generates -- ~40 valgrind runs per row, tens of minutes.
# **A checker that reddens when scratch is cleaned is reporting on the scratch.**
#
# ⭐⭐ WHAT CHANGED AT PROMOTION, AND IT IS THE HALF THAT MATTERS (item 149).
# As written, a missing prerequisite made `N3` print **FAIL** and the process
# exit **1** -- which says *"F89 is refuted"* when the truth is *"the build tree
# is gone"*. **A MISSING INPUT IS NOT A REFUTATION.** And worse: with the build
# trees present but the profile cache cleaned, a bare run silently launched
# **80 valgrind invocations**. ▶ It now checks its inputs FIRST and, when they
# are absent, **REPORTS AND RETURNS 0 saying `NOT RUN -- NOT A PASS` in
# capitals, having checked nothing.** `.tasks-php/width.py`'s `X3`/`X3d` is the
# rule; `probes/inclusive_ir.py::report_not_run` is the other worked example.
# ⚠ **That rc=0 IS NOT A PASS**, which is exactly why `kind` is `tool`: swept, a
# green NOT-RUN line would read as a checker passing, which is `F135`.
# ⛔ Regenerating the profiles is now OPT-IN (`--collect`). A probe that spends
# an hour because someone ran it bare is a trap, not a tool.
#
# RUN IT:
#   python3 .tasks-php/probes/ph64_draws.py --selftest    # 5 negatives
#   python3 .tasks-php/probes/ph64_draws.py               # the draw table
#   python3 .tasks-php/probes/ph64_draws.py --collect     # + regenerate cache
#   (add `--collect` to either of the first two to permit valgrind runs)
#
# ⛔ WHAT IS STILL OWED: (1) F89's `0.07 pp` and `0.034 %` have **one method**
# here and one different-design corroboration in `_043` §5.7; nothing in the
# tree re-derives them a third way. (2) F90 has **no** second method at all.
# (3) `NS`/`SPANS` are hardcoded draw endpoints chosen for this question; they
# are not derived from anything and a different `probe_iters` in `check.py`
# would silently make `N5` compare the wrong quantity -- `N5` is the arm that
# would catch it, and it is the only one.
# =============================================================================

"""ITEM 66 — IS `ph64`'s PUBLISHED B1 HEADLINE ONE UNSTABLE DRAW?

F88 (`TASK_PHP_038`): family B is `(Ir(hi) - Ir(lo)) / (hi - lo)`, the mean cost
of draws `lo..hi-1` of a PSEUDO-RANDOM window sequence, and `check.py` fixes
`probe_iters` at **[100, 200]** for every row in both programmes. On `ph29` that
draw moves the level **32 %** and the published draw is the LARGEST of seven; on
`ph03` it is **0.03 %**, because `ph03`'s per-window work is uniform.

⚠⚠ THE REVIEWER FLAGGED `ph64` AS THE CHEAPEST NEXT MEASUREMENT AND LEFT IT
**UNTESTED**, for a specific reason: **`ph64` is the ONE ROW WHOSE PUBLISHED
HEADLINE IS FAMILY B** (F74), and it allocates **2n+2 blocks per call** (F71,
open item 54) with **60 % of the C rung's instructions in libc** — so its
per-window work must vary strongly, which is F88's exact precondition.

▶ IF `ph64`'s B MOVES LIKE `ph29`'s, THE BAN ON FAMILY B IS NOT A STYLE RULE --
IT IS A CORRECTNESS FIX, AND `ph64`'s HEADLINE NEEDS RESTATING.

================ DECLARED EXPECTATIONS, BEFORE RUNNING ================
E1 The LEVEL will move a lot -- I predict > 10 % spread across draws. `ph64`
   allocates per element, so a window with more elements costs
   disproportionately more, which is precisely the heterogeneity F88 needs.
E2 ⚠ But F88's own finding is that the RATIO is far more stable than the level,
   because every rung walks the SAME window sequence (same `r`, same `acc`
   orbit). So I expect `ph64`'s published RATIO to move much less than its
   level -- single-digit pp, not 32 %.
E3 ⭐ THE ONE THAT DECIDES THE ITEM: does the published `[100,200]` ratio sit
   OUTSIDE the range of the other draws, as it does on `ph29`? If yes, the
   headline is an outlier and must be restated. If it sits INSIDE, the headline
   is unlucky-but-representative and the item closes cheaply.
E4 ⚠ I do NOT predict the direction. `ph29`'s published draw happened to be the
   largest; there is no reason `ph64`'s must be.
E5 ⚠⚠ AND A FALSIFIER FOR THE WHOLE PREMISE: if `ph64`'s level spread comes out
   like `ph03`'s (~0.03 %), then per-call allocation does NOT imply per-window
   heterogeneity, F88's mechanism does not reach this row, and the reviewer's
   stated reason for flagging it was wrong. That would be the interesting
   outcome and I should not bury it.
=======================================================================

⚠ `n_iters` is a `<Q` at offset 0 of the input blob (`probe_input` below is the
reviewer's `alias.py` mechanism, re-derived not imported, so this script stands
alone). The probe inputs are written under `.temp/mgr173/probe/` and are
re-derivable; the profiles under `.temp/mgr173/cg/` likewise -- this script is
the generator for both.

Run:  python3 .temp/mgr173/ph64_draws.py --selftest
      python3 .temp/mgr173/ph64_draws.py
"""
import json
import os
import re
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CGA = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CGDIR = os.path.join(ROOT, ".temp/mgr173/cg")
PROBE = os.path.join(ROOT, ".temp/mgr173/probe")
ROWLIST = [("ph64", "ph64-callback-frees-cursor"), ("ph03", "ph03-uudecode-bound")]
CELLS = ["c-gcc", "safe_naive", "safe_tuned", "unsafe"]
# 100/200 are the harness's own probe_iters and must be first. The rest are
# spans of the SAME WIDTH (100) at different offsets, so every slope below is a
# 100-draw sample and the only thing varying is WHICH draws.
NS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
SPANS = [(100, 200), (200, 300), (300, 400), (400, 500),
         (500, 600), (600, 700), (700, 800), (800, 900), (900, 1000)]
ROW = re.compile(r"^\s*([\d,]+)\s+\(?[\d.]*%?\)?\s*(.*)$")


def probe_input(src, n, out):
    """A copy of the input with `n_iters` (a `<Q` at offset 0) replaced."""
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n) + blob[8:])
    return out


def total(path):
    """PROGRAM TOTALS -- what family B's slope is computed from."""
    out = subprocess.run([CGA, "--threshold=100", path],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if "PROGRAM TOTALS" in line:
            return int(ROW.match(line).group(1).replace(",", ""))
    return None


def fresh(short, slug):
    """⚠ `.temp/build/` is gitignored scratch that outlives sessions."""
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import asm
    m = json.load(open(os.path.join(ROOT, f"results-php/{slug}.json")))
    bad = []
    for cell in CELLS:
        want = [c["static"]["md5_fn"] for c in m["cells"]
                if c["cell"] == cell and c["opt"] == "O3" and c["mode"] == "isolated"]
        b = os.path.join(ROOT, f".temp/php-root/.temp/build/{short}/{cell}-O3-isolated")
        if not want or not os.path.exists(b):
            bad.append((cell, "missing"))
            continue
        if asm.kernel(b).md5_fn != want[0]:
            bad.append((cell, "STALE"))
    return bad


#: ⛔ OPT-IN. Regenerating the cache is ~40 valgrind runs PER ROW. A bare run
#  used to launch them, which makes "I ran the probe" and "I burned an hour"
#  the same command. Set by `main()` from `--collect`.
ALLOW_RUN = False


def binary(short, cell):
    return os.path.join(ROOT, ".temp/php-root/.temp/build/"
                              f"{short}/{cell}-O3-isolated")


def missing_inputs(inp="small"):
    """Every path this script READS that a clean checkout does not have.

    ⛔ ALL of them are GITIGNORED or outside this repo, so their absence is the
    EXPECTED state of a fresh clone and is NOT a fault -- `CLAUDE.md` Don't #1
    being OBEYED. What it means is that THE CHECK CANNOT RUN, and item 149 says
    an unrunnable cross-session check REPORTS AND RETURNS 0. Pure apart from
    `os.path.exists`, so the arms can drive it.
    """
    miss = []
    for t in (VALGRIND, CGA):
        if not os.path.exists(t):
            miss.append(t + "   (the PINNED valgrind, outside this repo)")
    for short, slug in ROWLIST:
        src = os.path.join(ROOT, f"patterns-php/{slug}/inputs/{inp}.bin")
        if not os.path.exists(src):
            miss.append(src + f"   (gitignored; regenerate with "
                              f"patterns-php/{slug}/inputs/gen.py)")
        for cell in CELLS:
            if not os.path.exists(binary(short, cell)):
                miss.append(binary(short, cell) + "   (gitignored build tree)")
    if not ALLOW_RUN:
        gone = [f"{CGDIR}/{short}.{cell}.{inp}.{n}.out"
                for short, _ in ROWLIST for cell in CELLS for n in NS
                if not os.path.exists(os.path.join(
                    CGDIR, f"{short}.{cell}.{inp}.{n}.out"))]
        if gone:
            miss.append(f"{CGDIR}/  -- {len(gone)} of "
                        f"{len(ROWLIST) * len(CELLS) * len(NS)} callgrind "
                        f"profiles absent (re-run with --collect to generate "
                        f"them; that is ~{len(gone)} valgrind invocations)")
    return miss


def report_not_run(miss):
    """⛔ NOT A PASS. Say what is absent and why that is itself a result."""
    print("=" * 78)
    print("⛔⛔ NOT RUN -- NOT A PASS. NO VERDICT WAS REACHED.")
    print("=" * 78)
    print(f"  {len(miss)} input(s) this script reads are ABSENT. Every one of")
    print("  them is GITIGNORED or lives outside this repo, so their absence is")
    print("  the EXPECTED state of a clean checkout and not a fault -- but it")
    print("  means THE CHECK COULD NOT RUN, WHICH IS ITSELF A RESULT TO REPORT")
    print("  (item 149; the rule .tasks-php/width.py's X3 already follows).")
    print()
    for p in miss:
        print(f"    missing  {p}")
    print()
    print("  ⚠ F89's `0.07 pp` / `0.034 %` and F90's re-slice are NOT")
    print("    reproduced by this run and must not be quoted from it.")
    print("  ⛔ A MISSING INPUT IS NOT A REFUTATION. Returning 0 here says")
    print("    'no verdict', not 'pass'.")
    return 0


def collect(short, slug, inp="small"):
    os.makedirs(CGDIR, exist_ok=True)
    src = os.path.join(ROOT, f"patterns-php/{slug}/inputs/{inp}.bin")
    d = {}
    for n in NS:
        pin = (probe_input(src, n, os.path.join(PROBE, f"{short}.{inp}.{n}.bin"))
               if ALLOW_RUN else None)
        for cell in CELLS:
            op = os.path.join(CGDIR, f"{short}.{cell}.{inp}.{n}.out")
            if not os.path.exists(op):
                if not ALLOW_RUN:
                    # ⛔ Never silently launch valgrind. `missing_inputs()` has
                    # already refused the run in this state; reaching here means
                    # an arm called `collect` directly.
                    d[(cell, n)] = None
                    continue
                subprocess.run(
                    [VALGRIND, "--tool=callgrind", f"--callgrind-out-file={op}",
                     binary(short, cell), pin],
                    capture_output=True, text=True, timeout=3600)
            d[(cell, n)] = total(op)
    return d


def slopes(d, cell):
    out = {}
    for lo, hi in SPANS:
        x, y = d.get((cell, lo)), d.get((cell, hi))
        if x is not None and y is not None:
            out[(lo, hi)] = (y - x) / float(hi - lo)
    return out


def report():
    for short, slug in ROWLIST:
        print("=" * 78)
        print(f"{short}  ({slug})  small.bin  --  100-wide spans, O3/isolated")
        print("=" * 78)
        bad = fresh(short, slug)
        if bad:
            print(f"  ⚠⚠⚠ BINARIES NOT USABLE: {bad} -- refusing to report")
            continue
        print("  ✅ every binary matches its published record's md5_fn")
        d = collect(short, slug)

        print()
        print("  LEVELS (Ir/call), per 100-draw span:")
        hdr = "  " + "cell".ljust(12) + "".join(f"{lo}-{hi}".rjust(11) for lo, hi in SPANS)
        print(hdr)
        lvl_spread = {}
        for cell in CELLS:
            sl = slopes(d, cell)
            vals = [sl.get(s) for s in SPANS]
            row = "  " + cell.ljust(12)
            for v in vals:
                row += ("%11.1f" % v) if v is not None else " " * 11
            got = [v for v in vals if v is not None]
            if got:
                lvl_spread[cell] = 100.0 * (max(got) - min(got)) / min(got)
                row += f"   spread {lvl_spread[cell]:5.2f}%"
            print(row)

        # the RATIO -- what the row actually publishes
        print()
        print("  RATIOS (%), the quantity the row PUBLISHES:")
        pairs = [("c-gcc", "safe_tuned"), ("c-gcc", "safe_naive"),
                 ("safe_naive", "safe_tuned"), ("safe_tuned", "unsafe")]
        for a, b in pairs:
            sa, sb = slopes(d, a), slopes(d, b)
            vals = []
            for s in SPANS:
                x, y = sa.get(s), sb.get(s)
                vals.append(100.0 * (x - y) / y if x is not None and y and y else None)
            got = [v for v in vals if v is not None]
            if not got:
                continue
            pub = vals[0]                     # the [100,200] draw == family B
            others = got[1:]
            # ⚠⚠ AN "OUTLIER" NEEDS A MAGNITUDE FLOOR, AND MY FIRST VERSION HAD
            # NONE -- so it fired on ph03 at spreads of 0.02 pp and 0.00 pp,
            # which is floating-point noise being reported as a finding. That is
            # the ph00 near-zero sign flip all over again (F86), and the BLIND
            # class's defect (item 67) a third time: a predicate that is
            # technically true and carries no information.
            # ▶ The floor is RELATIVE to the effect, because that is what a
            # reader of the headline cares about: does the draw move the number
            # enough to change what the row claims?
            miss = 0.0
            if others:
                miss = max(0.0, pub - max(others), min(others) - pub)
            rel = 100.0 * miss / abs(pub) if pub else 0.0
            outlier = bool(others) and rel >= 1.0
            row = "  " + f"{a} vs {b}".ljust(26)
            for v in vals:
                row += ("%+9.2f" % v) if v is not None else " " * 9
            print(row)
            if others:
                verdict = ("⚠⚠ OUTLIER" if outlier else
                           (f"outside by {miss:.2f} pp = {rel:.2f}% of the "
                            f"effect -- IMMATERIAL" if miss > 0 else
                            "INSIDE the range"))
                print(f"      published [100,200] = {pub:+.2f} · others "
                      f"{min(others):+.2f}..{max(others):+.2f} · "
                      f"spread {max(got) - min(got):.2f} pp · {verdict}")
        print()
    return 0


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST -- must-fire negatives")

    # N1 the n_iters patch must actually change the program's work, or every
    #    "draw" below is the same run and the whole script is vacuous.
    src = os.path.join(ROOT, "patterns-php/ph64-callback-frees-cursor/inputs/small.bin")
    a = probe_input(src, 100, os.path.join(PROBE, "_st.100.bin"))
    b = probe_input(src, 200, os.path.join(PROBE, "_st.200.bin"))
    ba, bb = open(a, "rb").read(), open(b, "rb").read()
    check("N1", ba != bb and ba[8:] == bb[8:] and
          struct.unpack("<Q", ba[:8])[0] == 100,
          "patching n_iters changes ONLY the first 8 bytes and sets the value")

    # N2 ⚠ the patched value must be what the ORIGINAL field held, i.e. offset 0
    #    really is n_iters on THIS row -- not assumed from another row's layout.
    orig = struct.unpack("<Q", open(src, "rb").read()[:8])[0]
    m = json.load(open(os.path.join(ROOT,
        "results-php/ph64-callback-frees-cursor.json")))
    rec = (m["inputs"]["small.bin"] or {}).get("n_iters")
    check("N2", orig == rec,
          f"offset 0 of ph64/small.bin holds {orig}, and the measurement record "
          f"says n_iters={rec} -- so the field being patched IS n_iters")

    # N3 binaries must be the published ones on both rows.
    bad64 = fresh("ph64", "ph64-callback-frees-cursor")
    bad03 = fresh("ph03", "ph03-uudecode-bound")
    check("N3", not bad64 and not bad03,
          f"ph64 {bad64 or 'ok'} · ph03 {bad03 or 'ok'}")

    # N4 ⭐ THE CONTROL ROW MUST BEHAVE AS F88 SAYS. `ph03` is in this script for
    #    one reason: F88 reports its level spread at 0.03 %. If it does not
    #    reproduce, my pipeline differs from the reviewer's and no ph64 number
    #    here means anything. ⚠ This is the negative that can invalidate the run.
    d3 = collect("ph03", "ph03-uudecode-bound")
    s3 = slopes(d3, "c-gcc")
    got = [v for v in s3.values() if v is not None]
    spread3 = 100.0 * (max(got) - min(got)) / min(got) if got else None
    check("N4", spread3 is not None and spread3 < 1.0,
          f"ph03/c-gcc level spread is {spread3:.3f}% (F88 reports 0.03%); "
          f"under 1% means this pipeline reproduces the control")

    # N5 and family B must be REPRODUCED by the [100,200] span, or the thing
    #    being varied is not the published statistic.
    g = json.load(open(os.path.join(ROOT,
        "results-php/gate/ph03-uudecode-bound.json")))
    pub = g["marginal_ir_per_call"].get("c-gcc/O3/whole/small.bin")
    mine = s3.get((100, 200))
    close = pub is not None and mine is not None and abs(pub - mine) / pub < 0.02
    check("N5", close,
          f"my [100,200] span gives {mine:.2f} and the record's whole-program "
          f"c-gcc marginal is {pub} -- within 2% means I am varying family B "
          f"itself and not some neighbouring quantity")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


def main(argv):
    global ALLOW_RUN
    ALLOW_RUN = "--collect" in argv
    miss = missing_inputs()
    if miss:
        return report_not_run(miss)
    return selftest() if "--selftest" in argv else report()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
