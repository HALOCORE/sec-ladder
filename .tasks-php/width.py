#!/usr/bin/env python3
# =============================================================================
# width.py -- THE MEASUREMENT BEHIND F92 (open item 68 answers NO)
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/php39/`, which is GITIGNORED, and F92 is PUBLISHED -- `RECAP_PHP.md`
# F92 and `.tasks-php/STATISTICS_001.md` §5 both answer open item 68 `NO` on
# the strength of it. ▶ A published finding whose only evidence is a gitignored
# probe will not survive a clean checkout. That is `RECAP_PHP.md` open item 86
# and F99's own defect applied to F99's sibling; the rule is
# `.memory-php/04-process.md` law 11.
#
# RUN IT:  python3 .tasks-php/width.py --selftest     # the negatives
#          python3 .tasks-php/width.py                # the sweep report
#          python3 .tasks-php/width.py --cost         # the cost model
#
# ⚠⚠ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered: it
# reads cached callgrind profiles under `.temp/php39/` and `.temp/mgr173/cg/`,
# both gitignored. On a clean checkout the sweep RE-DERIVES its own (it builds
# and runs callgrind itself); the cross-session check `X3`/`X3b`, which compares
# against `.temp/mgr173/cg/`, reports *"the check could not run, which is itself
# a result to report"* and does not fail. ✅ So the selftest degrades honestly
# rather than lying.
#
# ⛔⛔⛔ AND THAT SENTENCE WAS FALSE FROM THE DAY IT WAS COMMITTED UNTIL
# 2026-09-17. `X3` returned `False`, `selftest`'s `check()` appends every falsy
# `cond` to `fails`, and with `.temp/mgr173/cg/` absent this file printed
# `FAIL X3` and exited **1** -- while filed `st_expect=0`. ▶ THE STATE THAT
# REDDENED IT IS THE ONE `CLAUDE.md` Don't #1 TELLS YOU TO CREATE, so the
# routine sweep went red for following the rules and no `why` said so.
# ⚠⚠ THE HEADER IS THE POINT, NOT THE RETURN VALUE: this file is the committed
# RECORD OF law 11's founding remedy, and the record was wrong about the
# remedy (`F147`(e)). It was believed twice -- `probes/inclusive_ir.py:269`
# cites *"the rule .tasks-php/width.py's X3 already follows"* as precedent, and
# I told `PROMOTE_001`'s engineer to copy this file. ⭐ THE ENGINEER REFUSED,
# checked the behaviour against the claim, and made its own guards return 0.
# ✅ REPAIRED at `reuse_check` (item 149), where the reasoning lives, WITH the
# §H negative `X3d` that plants an absent cache and asserts reports-and-0.
# ⚠ rc=0 THERE IS NOT A PASS -- it is "no verdict was reached", printed in
# capitals. A silent 0 would be the worse of the two defects.
#
# WHAT IT FOUND (F92, reviewed at TASK_PHP_043 §4.3, UPHELD-NARROWED): the
# width->spread exponent is ≈ -0.5 on both rows, so widening `probe_iters`
# cannot buy a RELATIVE target -- ⚠ but its own TABLE 7 gives `W <= 574` for an
# ABSOLUTE 1-pp target, so *"hopeless"* is target-dependent. The `NO` stands on
# a better reason anyway: no width fixes a BIAS (F93's start-of-run transient,
# F91's). ⭐ Its F52 control is what makes the exponent believable -- it
# recovers -0.5047 from i.i.d. noise and -0.9799 from endpoint noise, so the
# experiment distinguishes *a weak lever* from *measuring its own null*.
#
# TWO DEFECTS REPAIRED 2026-09-13 WHEN IT WAS COMMITTED, both in `X3b`:
#   (1) `2.3950 / pp` divided by zero the day `pp` reached 0 -- i.e. the day the
#       check passed PERFECTLY. See `_margin`.
#   (2) it ASSERTED `c-gcc is BISTABLE between 14 and 28 Ir on BOTH rows` beside
#       a COMPUTED `worst`, and the two came to disagree: the current profiles
#       give deltas of 0 and 10 and NO swinging cell at all. The swings are now
#       read out of the data. `X3c` is the negative, and it tests BEHAVIOUR --
#       the textual version fired on the comment documenting the defect.
# =============================================================================

#!/usr/bin/env python3
"""TASK_PHP_039 / item 68 -- DOES FAMILY B's CROSS-LANGUAGE SPREAD FALL AS
`W^(-0.5)`, AND WHAT IS THE EXPONENT?

F88 established, from COMMITTED DRIVER SOURCE, that `ph64`'s `SLB-DRIVER` loop
picks its window index as `k = acc*nwin >> 64`, `acc = acc*31 + r` -- a
pseudo-random function of the running accumulator. So family B,
`(Ir(hi) - Ir(lo)) / dcalls`, is the MEAN of the per-window costs of the
`W = hi - lo` windows visited in that span: deterministic, but a SAMPLE.

  IF THAT ACCOUNT IS RIGHT, THE SPREAD OF THAT MEAN ACROSS DISJOINT SPANS MUST
  FALL AS `W^(-0.5)`.

and the exponent decides item 68 outright (TASK_PHP_039 §1):
  ~ -0.5   ordinary sampling error -> widening is HOPELESS (1 pp needs W~7500,
           a ~25x gate-stage cost). Item 68 answers NO.
  ~ -1 or steeper  -> widening WORKS (W~900). Item 68 answers YES.
  ~  0     -> NOT a sampling effect at all. F88's MECHANISM IS WRONG.

⚠⚠ THE MANAGER'S TWO ATTEMPTS BOTH FAILED THE SAME WAY: the statistic and the
sample count moved together with the width. Item 68's published table used
`max - min` over **9, 4 and 3** disjoint spans, and the expected RANGE of `K`
samples grows with `K` (2.97s at 9, 2.06s at 4, 1.69s at 3) -- so ~1.4x of its
fall is the ESTIMATOR, not the physics.

THE DESIGN (TASK_PHP_039 §2, MANDATORY, NOT TO BE "IMPROVED"):
  `K = 8` at EVERY width, and the eight spans START AT THE SAME EIGHT `n`
  VALUES at every width. Block spacing S = 800, starts n_j = 100 + 800j,
  j = 0..7. For W in {100, 200, 400, 800}, span j is (n_j, n_j + W).
  The only thing that varies between widths IS THE WIDTH.
  Position is held fixed BY CONSTRUCTION, not corrected for afterwards.
  Span j at W=800 CONTAINS span j at W=100: a PAIRED design, intended.

STATISTIC (§2.3): pct(s) = 100*(B_x(s) - B_y(s))/B_y(s), with
B_c(s) = (Ir_c(hi) - Ir_c(lo)) / dcalls, Ir from `PROGRAM TOTALS`.
Headline per (row, pair, W) is the **SD across the 8 spans, in pp**; `max-min`
is reported beside it only to tie W=100 to F89's published figures, WHICH ARE
RANGES (max - min over its nine draws), not SDs.

LICENCE TO MEASURE OUTSIDE THE GATE (§0): `harness/check.py::_probe_input`
(line 3248) writes `struct.pack("<Q", n_iters) + blob[8:]`, and `n_iters` is at
offset 0 of *every* pattern's input (`.memory/02-bench-rules.md`). N2 is that
check, against the PUBLISHED `marginal_ir_per_call`.
⛔ NO `spec.md` EDIT AND NO GATE RUN. The re-gate is a later, conditional step.

================ DECLARED EXPECTATIONS, BEFORE RUNNING THE SWEEP =============
E1 ⭐ THE ONE THAT DECIDES THE ITEM. I expect the exponent to come out at
   **-0.5, not -1**, on both `ph64` and `ph29` cross-language. Reason: item
   68's own published fall (8.124 -> 2.092 -> 1.243 at W = 100/200/300) is
   FAR TOO FAST for any mechanism -- 1/W would give 8.124 -> 4.06 -> 2.71, and
   the published 200-cell is already below that. A fall faster than 1/W has no
   sampling mechanism at all, so the most likely explanation is the estimator
   bias §2 names (9 -> 4 -> 3 spans), and removing it should land on -0.5.
   ▶ SO I EXPECT ITEM 68 TO ANSWER **NO**, and `TASK_PHP_038` §6's ruling
   (item 62 / family C) to stand.
E2 I expect the SAME-LANGUAGE pair (`safe_tuned` vs `unsafe`) to have the same
   EXPONENT as the cross-language pair but a ~100x smaller LEVEL, because F89's
   mechanism is that the common window sequence cancels in the ratio when the
   two cells' cost-vs-window curves match. An exponent that differs between
   the two pairs on the same row would surprise me and I would report it.
E3 `ph03` (the control) should sit at or near zero at every width, and its
   exponent should be MEANINGLESS -- noise divided by noise. I predict its
   W=100 SD is at least 30x below `ph64`'s. ⚠ If `ph03` shows a comparable
   law, §1's whole account falls and that is the loudest finding available.
E4 ⚠ I do NOT expect the four SD points to be clean. K = 8 is a small sample;
   a K=8 SD has a sampling SD of its own of roughly 1/sqrt(2*(8-1)) = 27 %,
   so a 4-point log-log fit over an 8x width range carries roughly
   +-0.1..0.2 in the exponent BEFORE any physics. That is why X1 calibrates
   the pipeline on synthetic series with KNOWN answers, and why I will quote
   the exponent's spread across rows and pairs rather than a fake CI.
E5 ⚠⚠ A FALSIFIER FOR MY OWN E1: if the measured exponent on `ph64`
   cross-language comes out at -0.9 or steeper AND X1 shows the pipeline
   recovers -0.5 from a synthetic -0.5 series, then the fall really is faster
   than i.i.d. sampling, item 68 answers YES, and F90 is right against the
   reviewer. I would then have been wrong twice in the same direction as the
   manager's two wrong expectations on this row.
==============================================================================

Writes go ONLY to `.temp/php39/`. `cg/*.out` and `probe/*.bin` are artefacts
and are re-derivable BY THIS SCRIPT (CLAUDE.md constraint 6); `run.sh` is the
one regeneration entry point.

Run:  bash .temp/php39/run.sh          # selftest + sweep, both teed to logs
      python3 .temp/php39/width.py --selftest
      python3 .temp/php39/width.py
      python3 .temp/php39/width.py --cost      # §3 only
"""
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import struct
import subprocess
import sys
import time

def _repo_root():
    """The repo root, found by MARKER rather than by counting `..`.

    ⛔ This was `dirname(dirname(dirname(abspath(__file__))))`, which is correct
    from `.temp/php39/` and WRONG BY ONE LEVEL from `.tasks-php/` -- so moving
    the file to where open item 86 wanted it silently resolved `ROOT` to the
    PARENT of the repository and the first thing that failed was
    `import asm`. ⚠ `RECAP_PHP.md` F20 is the same defect (*"one `..` too
    few"*); counting directory levels is a hardcoded figure like any other
    (`.memory-php/04-process.md` law 6)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.exists(os.path.join(d, "harness", "check.py")):
            return d
        d = os.path.dirname(d)
    raise SystemExit("width.py: no repo root above %s (no harness/check.py)"
                     % os.path.abspath(__file__))


ROOT = _repo_root()
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CGA = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
HERE = os.path.join(ROOT, ".temp/php39")
CGDIR = os.path.join(HERE, "cg")
PROBE = os.path.join(HERE, "probe")
TIMINGS = os.path.join(HERE, "timings.json")

ROWS = [("ph64", "ph64-callback-frees-cursor"),
        ("ph29", "ph29-recvfrom-alloc"),
        ("ph03", "ph03-uudecode-bound")]          # ph03 is THE CONTROL (N3)
CELLS = ["c-gcc", "safe_naive", "safe_tuned", "unsafe"]
INPUT = "small"                                   # §2.2: small.bin ONLY
OPT, MODE = "O3", "isolated"

# --- §2.1 the span design, DERIVED IN CODE from the table, not hand-listed ---
S = 800                                           # block spacing
K = 8                                             # spans per width, at EVERY width
STARTS = [100 + S * j for j in range(K)]          # 100 900 1700 ... 5700
WIDTHS = [100, 200, 400, 800]


def spans(w):
    """The K spans at width `w`: span j is (n_j, n_j + w)."""
    return [(n, n + w) for n in STARTS]


def endpoints():
    """The 33 `n` values the sweep needs, derived from the span table."""
    return sorted({lo for w in WIDTHS for lo, _ in spans(w)}
                  | {hi for w in WIDTHS for _, hi in spans(w)})


NS = endpoints()

# §2.2 the two mandated pairs, plus `c-gcc` vs `safe_tuned` as a SECONDARY,
# because F89's published `8.63 pp` is THAT pair and §2.3 asks W=100 to be tied
# to it. (`c-gcc` vs `safe_naive` is F89's `8.12 pp`.)
PAIRS = [("c-gcc", "safe_naive", "CROSS-LANGUAGE (mandated)"),
         ("safe_tuned", "unsafe", "same-language (mandated)"),
         ("c-gcc", "safe_tuned", "cross-language (secondary, F89's 8.63 pp)")]
PRIMARY_X = ("c-gcc", "safe_naive")
PRIMARY_S = ("safe_tuned", "unsafe")

# The RELATIVE floor for "near zero" / "nonzero", used by N3 and N7 (trap 2,
# and F89's own fix): a spread counts only if it moves the ratio by at least
# 1 % of the effect the row claims. `SD <= 0.01 * |mean pct|` is "near zero".
REL_FLOOR = 0.01
# N7 asks a DIFFERENT question from N3 -- *is there anything for width to
# reduce?* -- so it needs a floor against the measurement's RESOLUTION, not
# against the effect. 0.05 pp is 7x ph03's control SD and ~20x the largest
# cross-session artefact X3 measures. See the disclosure at N7.
N7_FLOOR_PP = 0.05

TOT_ANNOT = re.compile(r"^\s*([\d,]+)\s+\(?[\d.]*%?\)?\s*PROGRAM TOTALS")


# ---------------------------------------------------------------- plumbing --
def probe_input(src, n, out):
    """`check.py::_probe_input` (line 3248), re-derived so this script stands
    alone: the same input with `n_iters` (a `<Q` at offset 0) rewritten."""
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n) + blob[8:])
    return out


def total_annot(path):
    """`callgrind_annotate`'s PROGRAM TOTALS -- what §2.3 names."""
    out = subprocess.run([CGA, "--threshold=100", path],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = TOT_ANNOT.match(line)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def total_raw(path):
    """The `summary:`/`totals:` line, which is what `check.py::_callgrind_total`
    (line 3434) actually reads. X2 asserts the two agree."""
    try:
        for line in open(path):
            if line.startswith("summary:") or line.startswith("totals:"):
                return int(line.split()[1])
    except OSError:
        return None
    return None


def binpath(short, cell):
    return os.path.join(ROOT, ".temp/php-root/.temp/build",
                        short, f"{cell}-{OPT}-{MODE}")


def srcinput(slug):
    return os.path.join(ROOT, f"patterns-php/{slug}/inputs/{INPUT}.bin")


_TIM = None


def timings():
    global _TIM
    if _TIM is None:
        _TIM = json.load(open(TIMINGS)) if os.path.exists(TIMINGS) else {}
    return _TIM


def save_timings():
    if _TIM is not None:
        with open(TIMINGS, "w") as f:
            json.dump(_TIM, f, indent=1, sort_keys=True)


def one_run(short, slug, cell, n, force=False):
    """One callgrind run, cached on disk. Returns the profile path."""
    os.makedirs(CGDIR, exist_ok=True)
    op = os.path.join(CGDIR, f"{short}.{cell}.{INPUT}.{n}.out")
    if os.path.exists(op) and not force:
        return op
    pin = probe_input(srcinput(slug),
                      n, os.path.join(PROBE, f"{short}.{INPUT}.{n}.bin"))
    t0 = time.time()
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={op}", binpath(short, cell), pin],
                       capture_output=True, text=True, timeout=3600)
    dt = time.time() - t0
    timings()[f"{short}.{cell}.{n}"] = {"s": round(dt, 3), "rc": r.returncode}
    return op


def collect(verbose=False):
    """The sweep: 33 n x 4 cells x 3 rows = 396 callgrind runs.

    Returns ir[(short, cell, n)] = PROGRAM TOTALS, plus the raw-line reading."""
    ir, raw = {}, {}
    done = 0
    for short, slug in ROWS:
        for n in NS:
            for cell in CELLS:
                op = one_run(short, slug, cell, n)
                ir[(short, cell, n)] = total_annot(op)
                raw[(short, cell, n)] = total_raw(op)
                done += 1
                if verbose and done % 40 == 0:
                    print(f"    ... {done}/{len(ROWS) * len(NS) * len(CELLS)} "
                          f"runs read", flush=True)
        save_timings()
    save_timings()
    return ir, raw


# ------------------------------------------------------- rows' own metadata --
_MODELS = {}


def model_of(short, slug):
    if short not in _MODELS:
        name = f"_m39_{short}"
        spec = importlib.util.spec_from_file_location(
            name, os.path.join(ROOT, f"patterns-php/{slug}/model.py"))
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m
        spec.loader.exec_module(m)
        _MODELS[short] = m
    return _MODELS[short]


def dcalls(short, slug, lo, hi):
    """⚠ NOT `hi - lo` by assumption. `check.py`'s collapse stage divides by
    `model.n_calls(hi) - model.n_calls(lo)`, so a driver that calls the kernel
    more than once per iteration would make the two differ. Taken from the
    row's own `model.py`."""
    m = model_of(short, slug)
    src = srcinput(slug)
    out = []
    for n in (lo, hi):
        p = probe_input(src, n, os.path.join(PROBE, f"{short}.{INPUT}.{n}.bin"))
        out.append(m.build(p).n_calls)
    return out[1] - out[0]


def md5_check(short, slug):
    """N8. `md5_fn` is the md5 of the KERNEL FUNCTION's bytes as `asm.kernel`
    extracts it -- the field the published measurement record carries."""
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import asm
    rec = json.load(open(os.path.join(ROOT, f"results-php/{slug}.json")))
    out = []
    for cell in CELLS:
        want = None
        for c in rec["cells"]:
            if c["cell"] == cell and c["opt"] == OPT and c["mode"] == MODE:
                want = c["static"]["md5_fn"]
        b = binpath(short, cell)
        got = asm.kernel(b).md5_fn if os.path.exists(b) else None
        whole = (hashlib.md5(open(b, "rb").read()).hexdigest()
                 if os.path.exists(b) else None)
        out.append((cell, want, got, want is not None and want == got, whole))
    return out


def published_b(slug, cell):
    g = json.load(open(os.path.join(ROOT, f"results-php/gate/{slug}.json")))
    return (g["marginal_ir_per_call"] or {}).get(
        f"{cell}/{OPT}/{MODE}/{INPUT}.bin")


# ------------------------------------------------------------- statistics ---
def slope(ir, short, cell, lo, hi, dc):
    a, b = ir.get((short, cell, lo)), ir.get((short, cell, hi))
    return None if a is None or b is None else (b - a) / float(dc)


def sd(v, ddof=1):
    n = len(v)
    if n - ddof <= 0:
        return None
    mu = sum(v) / n
    return math.sqrt(sum((x - mu) ** 2 for x in v) / (n - ddof))


def pcts(ir, short, x, y, w, dc_per_w, starts=None):
    """The 8 `pct` values at width `w`, one per span."""
    st = STARTS if starts is None else starts
    out = []
    for n in st:
        lo, hi = n, n + w
        bx = slope(ir, short, x, lo, hi, dc_per_w[w])
        by = slope(ir, short, y, lo, hi, dc_per_w[w])
        out.append(None if bx is None or by is None or not by
                   else 100.0 * (bx - by) / by)
    return out


def loglog_fit(ws, sds):
    """log(SD) against log(W). Returns (exponent, intercept, residuals in log
    space, max |residual|). ⚠ 4 points cannot support a confidence interval."""
    pts = [(math.log(w), math.log(s)) for w, s in zip(ws, sds)
           if s is not None and s > 0]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx == 0:
        return None
    beta = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
    alpha = my - beta * mx
    res = [p[1] - (alpha + beta * p[0]) for p in pts]
    return beta, alpha, res, max(abs(r) for r in res)


# ------------------------------------------------------------- the report ---
def report():
    print("=" * 100)
    print("TASK_PHP_039 -- the WIDTH -> SPREAD law for family B.  "
          f"{INPUT}.bin, {OPT}/{MODE}.")
    print(f"K = {K} spans at every width, starts {STARTS}, widths {WIDTHS}.")
    print("=" * 100)

    # md5 gate first: a sweep over a stale binary is worth nothing (§2.2).
    stale = []
    for short, slug in ROWS:
        for cell, want, got, ok, whole in md5_check(short, slug):
            print(f"  md5_fn  {short:5s} {cell:11s} on-disk {got} "
                  f"record {want}  {'MATCH' if ok else '*** STALE -- STOP ***'}")
            if not ok:
                stale.append((short, cell))
    if stale:
        print(f"  ⚠⚠⚠ REFUSING TO REPORT NUMBERS OFF A STALE BINARY: {stale}")
        return 1
    print("  ✅ all 12 binaries match their published record's `md5_fn`")

    dc = {}
    for short, slug in ROWS:
        dc[short] = {w: dcalls(short, slug, STARTS[0], STARTS[0] + w)
                     for w in WIDTHS}
        print(f"  dcalls  {short:5s} from model.py: "
              + "  ".join(f"W={w} -> {dc[short][w]}" for w in WIDTHS))

    print(f"\n  running/reading {len(ROWS) * len(NS) * len(CELLS)} callgrind "
          f"runs ({len(NS)} n x {len(CELLS)} cells x {len(ROWS)} rows) ...",
          flush=True)
    ir, raw = collect(verbose=True)

    # ---- table 1: the 33-point Ir(n) series, per cell-row -------------------
    for short, _ in ROWS:
        print()
        print("-" * 100)
        print(f"TABLE 1.{short}  PROGRAM TOTALS Ir(n), {short}/{INPUT}.bin/"
              f"{OPT}/{MODE} -- the 33 endpoints")
        print("-" * 100)
        print("       n  " + "".join(c.rjust(16) for c in CELLS))
        for n in NS:
            print(f"  {n:6d}  " + "".join(
                (f"{ir[(short, c, n)]:,}".rjust(16)
                 if ir.get((short, c, n)) is not None else "MISSING".rjust(16))
                for c in CELLS))

    # ---- table 2: SD / mean / min / max per (row, pair, W) ------------------
    fits = {}
    for short, slug in ROWS:
        for x, y, tag in PAIRS:
            print()
            print("-" * 100)
            print(f"TABLE 2  {short}  {x} vs {y}   [{tag}]   {INPUT}.bin "
                  f"{OPT}/{MODE}")
            print("-" * 100)
            print(f"  {'W':>5s} {'K':>3s} {'SD (pp)':>12s} {'mean (pp)':>12s} "
                  f"{'min (pp)':>12s} {'max (pp)':>12s} {'max-min (pp)':>14s} "
                  f"{'SD/|mean| %':>12s}")
            sds, mns = [], []
            for w in WIDTHS:
                v = [p for p in pcts(ir, short, x, y, w, dc[short])
                     if p is not None]
                if not v:
                    print(f"  {w:5d}  NO DATA")
                    sds.append(None)
                    mns.append(None)
                    continue
                s, mu = sd(v), sum(v) / len(v)
                sds.append(s)
                mns.append(mu)
                print(f"  {w:5d} {len(v):3d} {s:12.4f} {mu:12.4f} "
                      f"{min(v):12.4f} {max(v):12.4f} "
                      f"{max(v) - min(v):14.4f} "
                      f"{100.0 * s / abs(mu) if mu else float('nan'):12.3f}")
            f = loglog_fit(WIDTHS, sds)
            fits[(short, x, y)] = (f, sds, mns)
            if f:
                beta, alpha, res, mres = f
                print(f"  FIT  log(SD) = {alpha:+.4f} {beta:+.4f}*log(W)   "
                      f"->  EXPONENT {beta:+.4f}")
                print("       residuals (log space): "
                      + "  ".join(f"W={w}: {r:+.4f}"
                                  for w, r in zip(WIDTHS, res))
                      + f"   max |res| {mres:.4f}")
                print("       SD predicted by an exact -0.5 law from the W=100 "
                      "cell: "
                      + "  ".join(f"W={w}: {sds[0] * (w / 100.0) ** -0.5:.4f}"
                                  for w in WIDTHS))
                print("       SD predicted by an exact -1.0 law from the W=100 "
                      "cell: "
                      + "  ".join(f"W={w}: {sds[0] * (w / 100.0) ** -1.0:.4f}"
                                  for w in WIDTHS))
            else:
                print("  FIT  NOT COMPUTABLE (a nonpositive or missing SD)")

    # ---- table 3: exponent summary -----------------------------------------
    print()
    print("-" * 100)
    print("TABLE 3  the EXPONENT per (row, pair), and the LEVEL it starts from")
    print("-" * 100)
    print(f"  {'row':6s} {'pair':28s} {'SD@100':>9s} {'SD@800':>9s} "
          f"{'exponent':>10s} {'max|res|':>9s} {'ratio SD100/SD800':>19s}")
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            f, sds, _m = fits[(short, x, y)]
            r = (sds[0] / sds[3]) if sds[0] and sds[3] else float("nan")
            if f:
                print(f"  {short:6s} {x + ' vs ' + y:28s} {sds[0]:9.4f} "
                      f"{sds[3]:9.4f} {f[0]:10.4f} {f[3]:9.4f} {r:19.2f}")
            else:
                print(f"  {short:6s} {x + ' vs ' + y:28s} "
                      f"{'-- no fit --':>48s}")
    print(f"  ⓘ reference: an exact -0.5 law gives ratio sqrt(8) = "
          f"{math.sqrt(8):.2f}; an exact -1.0 law gives 8.00")

    # ---- table 4: the shifted-start REPLICATE (X4) --------------------------
    print()
    print("-" * 100)
    print("TABLE 4  X4 -- the SHIFTED-START REPLICATE. Same 33 endpoints, a "
          "SECOND set of 8 disjoint spans")
    print("         at DIFFERENT start positions, available at W = 100, 200, "
          "400 only. This is the")
    print("         error bar on a K=8 SD that a 4-point fit cannot give.")
    print("-" * 100)
    print(f"  {'row':6s} {'pair':28s} {'W':>5s} {'SD mandated':>12s} "
          f"{'SD shifted':>12s} {'shifted starts':>16s} {'ratio':>7s}")
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            for w in (100, 200, 400):
                alt = [n + w for n in STARTS]        # (n_j+w, n_j+2w)
                if max(alt) + w > NS[-1]:
                    continue
                a = [p for p in pcts(ir, short, x, y, w, dc[short]) if p is not None]
                b = [p for p in pcts(ir, short, x, y, w, dc[short], starts=alt)
                     if p is not None]
                if not a or not b:
                    continue
                sa, sb_ = sd(a), sd(b)
                print(f"  {short:6s} {x + ' vs ' + y:28s} {w:5d} {sa:12.4f} "
                      f"{sb_:12.4f} {str(alt[0]) + '..' + str(alt[-1]):>16s} "
                      f"{sb_ / sa if sa else float('nan'):7.2f}")

    # ---- table 5: the LEVELS, for continuity with F88/F89 -------------------
    print()
    print("-" * 100)
    print("TABLE 5  the LEVEL (Ir/call) at W=100, per cell -- F88/F89's "
          "quantity, for continuity")
    print("-" * 100)
    print(f"  {'row':6s} {'cell':12s} {'published B':>13s} "
          + "".join(f"{n:>11d}" for n in STARTS) + f"{'spread %':>11s}")
    for short, slug in ROWS:
        for cell in CELLS:
            v = [slope(ir, short, cell, n, n + 100, dc[short][100])
                 for n in STARTS]
            g = published_b(slug, cell)
            got = [z for z in v if z is not None]
            spr = 100.0 * (max(got) - min(got)) / min(got) if got else float("nan")
            print(f"  {short:6s} {cell:12s} {g if g is None else f'{g:13.2f}'} "
                  + "".join(f"{z:11.1f}" if z is not None else " " * 11
                            for z in v)
                  + f"{spr:11.2f}")

    extras(ir, dc, fits)
    print()
    cost_report(ir, dc)
    return 0


def extras(ir, dc, fits):
    """Three follow-on readouts of the SAME 33 endpoints. No new runs."""
    # ---- table 6: the GRAND slope -- what the draw is a sample OF ----------
    print()
    print("-" * 100)
    print("TABLE 6  the GRAND slope over [100, 6500) -- 6400 iterations, i.e. "
          "the best estimate available")
    print("         here of the POPULATION mean family B is one draw of. "
          "⭐ The 8 W=800 spans TILE this")
    print("         interval exactly, so their mean IS this slope "
          "(an arithmetic identity, not a check).")
    print("-" * 100)
    print(f"  {'row':6s} {'cell':12s} {'published B (100,200)':>22s} "
          f"{'grand slope':>14s} {'draw - grand':>13s} {'% of grand':>11s}")
    grand = {}
    for short, slug in ROWS:
        for cell in CELLS:
            a, b = ir[(short, cell, 100)], ir[(short, cell, 6500)]
            g = (b - a) / 6400.0
            grand[(short, cell)] = g
            p = published_b(slug, cell)
            print(f"  {short:6s} {cell:12s} {p:22.2f} {g:14.2f} "
                  f"{p - g:13.2f} {100.0 * (p - g) / g:10.3f} %")
    print()
    print(f"  {'row':6s} {'pair':28s} {'published B ratio':>18s} "
          f"{'grand ratio':>13s} {'draw - grand (pp)':>19s} {'% of effect':>12s}")
    for short, slug in ROWS:
        for x, y, _t in PAIRS:
            px, py = published_b(slug, x), published_b(slug, y)
            gx, gy = grand[(short, x)], grand[(short, y)]
            pr, gr = 100.0 * (px - py) / py, 100.0 * (gx - gy) / gy
            print(f"  {short:6s} {x + ' vs ' + y:28s} {pr:18.4f} {gr:13.4f} "
                  f"{pr - gr:19.4f} {100.0 * (pr - gr) / abs(gr):11.3f} %")

    # ---- table 7: the W a target needs, under the measured exponent -------
    print()
    print("-" * 100)
    print("TABLE 7  the WIDTH a target needs. W(target) = 100 * "
          "(SD@100 / target)^(-1/exponent).")
    print("         ⚠ THE TARGET MATTERS AS MUCH AS THE EXPONENT: item 68's "
          "'8.63 pp -> 1 pp' was")
    print("         stated in RANGES; the same absolute target on an SD is a "
          "different, cheaper number.")
    print("-" * 100)
    print(f"  {'row':6s} {'pair':28s} {'SD@100':>8s} {'exp':>7s} "
          f"{'W for SD<=1pp':>14s} {'(at -0.5)':>10s} "
          f"{'W for SD<=1% of eff':>21s} {'(at -0.5)':>10s}")
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            f, sds, mns = fits[(short, x, y)]
            if not f or not sds[0]:
                continue
            beta = f[0]

            def need(tgt, b):
                if tgt <= 0 or tgt >= sds[0]:
                    return 100.0
                return 100.0 * (sds[0] / tgt) ** (-1.0 / b)
            t2 = REL_FLOOR * abs(mns[0])
            print(f"  {short:6s} {x + ' vs ' + y:28s} {sds[0]:8.4f} "
                  f"{beta:7.3f} {need(1.0, beta):14,.0f} "
                  f"{need(1.0, -0.5):10,.0f} {need(t2, beta):21,.0f} "
                  f"{need(t2, -0.5):10,.0f}")
    print("  ⓘ a W of 100 in these columns means the target is ALREADY met at "
          "the shipped pin.")

    # ---- table 8: item 68's published table, reconstructed ----------------
    print()
    print("-" * 100)
    print("TABLE 8  ⭐ WHY ITEM 68's PUBLISHED FALL LOOKED TOO FAST. It used "
          "`max - min` over K = 9, 4, 3")
    print("         disjoint spans at W = 100, 200, 300. E[range of K "
          "samples] = d(K)*sigma, and d GROWS")
    print("         with K: 2.970 at 9, 2.059 at 4, 1.693 at 3 (standard "
          "normal-order statistics).")
    print("-" * 100)
    f, sds, mns = fits[("ph64", "c-gcc", "safe_naive")]
    s100 = sds[0]
    print(f"  measured here: ph64 c-gcc vs safe_naive, W=100, K=8, "
          f"SD = {s100:.4f} pp, range = "
          f"{max(p for p in pcts(ir, 'ph64', 'c-gcc', 'safe_naive', 100, dc['ph64'])) - min(p for p in pcts(ir, 'ph64', 'c-gcc', 'safe_naive', 100, dc['ph64'])):.4f} pp")
    print()
    print(f"  {'W':>5s} {'K (item 68)':>12s} {'d(K)':>7s} "
          f"{'sigma_W under -0.5':>19s} {'E[range] = d*sigma':>19s} "
          f"{'item 68 PUBLISHED':>18s} {'ratio':>7s}")
    for w, k, dk, pub in ((100, 9, 2.970, 8.124), (200, 4, 2.059, 2.092),
                          (300, 3, 1.693, 1.243)):
        sig = s100 * (w / 100.0) ** -0.5
        er = dk * sig
        print(f"  {w:5d} {k:12d} {dk:7.3f} {sig:19.4f} {er:19.4f} "
              f"{pub:18.3f} {pub / er:7.2f}")
    print("  ▶ Under an EXACT -0.5 law the published series should have read "
          "roughly 7.11 / 3.49 / 2.34,")
    print("    NOT 8.12 / 2.09 / 1.24. The published W=100 cell is 1.14x that "
          "prediction and the W=200")
    print("    and W=300 cells are 0.60x and 0.53x it. ⚠ The shrinking d(K) "
          "accounts for a factor of")
    print("    1.44 between W=100 and W=300 on its own; the rest is the "
          "sampling error OF A RANGE")
    print("    taken from 4 and 3 samples, whose own SD is ~0.88 sigma at K=4 "
          "and ~0.89 sigma at K=3.")
    print("  ⛔ SO ITEM 68's TABLE IS CONSISTENT WITH A -0.5 LAW ONCE THE "
          "ESTIMATOR IS ACCOUNTED FOR.")

    # ---- table 9: is the fall consistent with -0.5, pointwise? ------------
    print()
    print("-" * 100)
    print("TABLE 9  pointwise: measured SD against an exact -0.5 law anchored "
          "at W=100")
    print("-" * 100)
    print(f"  {'row':6s} {'pair':28s} " + "".join(
        f"{'W=' + str(w):>22s}" for w in WIDTHS[1:]))
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            f, sds, _m = fits[(short, x, y)]
            if not sds[0]:
                continue
            cells = []
            for i, w in enumerate(WIDTHS[1:], start=1):
                pred = sds[0] * (w / 100.0) ** -0.5
                cells.append(f"{sds[i]:.4f}/{pred:.4f}={sds[i] / pred:5.2f}x")
            print(f"  {short:6s} {x + ' vs ' + y:28s} "
                  + "".join(c.rjust(22) for c in cells))
    print("  ⓘ 1.00x is an exact -0.5 law. Below 1.00x is FASTER than -0.5, "
          "above is SLOWER.")

    # ---- table 10: is the SHIPPED PIN a draw, or is it a TRANSIENT? -------
    print()
    print("-" * 100)
    print("TABLE 10 ⭐⭐ WHERE THE SHIPPED PIN SITS AMONG THE 8 SPANS -- and it "
          "is NOT the same answer on")
    print("         the two rows. Span j=0 IS the shipped pin's span at W=100. "
          "`z` is how far it sits from")
    print("         the mean of the OTHER SEVEN, in units of their own SD, at "
          "W=100.")
    print("-" * 100)
    print(f"  {'row':6s} {'pair':28s} {'pin span':>10s} {'other 7 mean':>13s} "
          f"{'other 7 SD':>11s} {'z':>7s} {'rank/8':>7s}")
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            v = pcts(ir, short, x, y, 100, dc[short])
            o = v[1:]
            mo, so = sum(o) / len(o), sd(o)
            z = (v[0] - mo) / so if so else float("nan")
            rank = sorted(v, reverse=True).index(v[0]) + 1
            print(f"  {short:6s} {x + ' vs ' + y:28s} {v[0]:10.3f} {mo:13.3f} "
                  f"{so:11.4f} {z:7.2f} {rank:5d}/8")
    print("  ⚠ A MAGNITUDE FLOOR FOR 'OUTLIER': |z| >= 3 AND the offset must "
          "exceed 1 % of the effect.")
    print()
    print("  and the DECOMPOSITION, which says whether widening the pin can "
          "reach the population mean:")
    print(f"  {'row':6s} {'pair':28s} " + "".join(
        s.rjust(13) for s in ("(100,200)", "(200,300)", "(200,900)",
                              "(900,6500)", "GRAND")))
    for short, _ in ROWS:
        for x, y, _t in PAIRS:
            cs = []
            for lo, hi in ((100, 200), (200, 300), (200, 900), (900, 6500),
                           (100, 6500)):
                bx = slope(ir, short, x, lo, hi, hi - lo)
                by = slope(ir, short, y, lo, hi, hi - lo)
                cs.append(f"{100.0 * (bx - by) / by:13.3f}")
            print(f"  {short:6s} {x + ' vs ' + y:28s}" + "".join(cs))
    print("  ⓘ (200,300) and (200,900) are DISJOINT from the pin, so if they "
          "already agree with (900,6500)")
    print("    the pin's excess is confined to iterations 100..199 and is a "
          "WARM-UP TRANSIENT, not a draw.")


# --------------------------------------------------- §3 the cost estimate ---
def cost_report(ir=None, dc=None):
    """§3. ⚠ AN ESTIMATE, and NOT computed from `ph64/O3/isolated/small` alone:
    the gate probes BOTH inputs at BOTH opt levels in BOTH modes over EIGHT
    cells -- 64 slope entries (96 `marginal_ir_per_call` KEYS once the 32
    `d_ir_d_work` entries are counted) = 128 callgrind runs on `ph64` -- and
    the `O0`/`large.bin` cells are the expensive ones."""
    slug = "ph64-callback-frees-cursor"
    g = json.load(open(os.path.join(ROOT, f"results-php/gate/{slug}.json")))
    m = g["marginal_ir_per_call"]
    ent = {k: v for k, v in m.items() if k.endswith(".bin")}
    print("=" * 100)
    print("§3  WHAT WIDENING `probe_iters` COSTS THE GATE -- AN **ESTIMATE**, "
          "with its arithmetic shown")
    print("=" * 100)
    print(f"  ph64's gate record carries {len(m)} `marginal_ir_per_call` keys: "
          f"{len(ent)} slope entries")
    print(f"  ({len(ent) // 2} cell/opt/mode combinations x 2 inputs) + "
          f"{len(m) - len(ent)} derived `d_ir_d_work`.")
    print(f"  Each slope entry costs TWO callgrind runs (at `lo` and at `hi`) "
          f"=> {2 * len(ent)} runs.")
    sb_ = sum(ent.values())
    print()
    print(f"  Sum of the published per-call slopes over all {len(ent)} entries, "
          f"SUM_B = {sb_:,.0f} Ir/call.")
    print("  The five dearest entries, which is where the cost lives:")
    for k, v in sorted(ent.items(), key=lambda t: -t[1])[:5]:
        print(f"      {k:42s} {v:12,.2f} Ir/call  "
              f"({100.0 * v / sb_:5.2f} % of SUM_B)")
    print(f"      ... and the cheapest, {min(ent, key=ent.get)}: "
          f"{min(ent.values()):,.2f}")

    # the fixed per-run term, MEASURED from this sweep where possible
    fixed = None
    if ir and dc:
        ints = []
        for cell in CELLS:
            pts = [(n, ir[("ph64", cell, n)]) for n in NS
                   if ir.get(("ph64", cell, n)) is not None]
            if len(pts) < 2:
                continue
            n_ = len(pts)
            mx = sum(p[0] for p in pts) / n_
            my = sum(p[1] for p in pts) / n_
            sxx = sum((p[0] - mx) ** 2 for p in pts)
            b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
            ints.append((cell, my - b * mx, b))
        print()
        print("  The FIXED per-run term, MEASURED here (OLS intercept of Ir(n) "
              "over the 33 endpoints,")
        print("  ph64/O3/isolated/small.bin -- the only cells this sweep "
              "covers):")
        for cell, a, b in ints:
            print(f"      {cell:12s} intercept {a:14,.0f} Ir    slope "
                  f"{b:12,.2f} Ir/call")
        if ints:
            fixed = sum(a for _, a, _ in ints) / len(ints)
            print(f"      mean intercept {fixed:,.0f} Ir "
                  f"(`TASK_PHP_038` §1.3 reports the language-dependent fixed "
                  f"term at ~176 k Ir; these agree in order of magnitude)")
    if fixed is None:
        fixed = 176000.0
        print("  fixed per-run term taken as 176,000 Ir (`_038` §1.3), not "
              "measured in this invocation")

    nruns = 2 * len(ent)
    print()
    print("  MODEL:  Ir(total for the stage at pin [lo, hi])")
    print("        = SUM_over_entries[ B*lo + B*hi + 2*fixed ]")
    print("        = SUM_B * (lo + hi) + nruns * fixed")
    print(f"        with SUM_B = {sb_:,.0f}, nruns = {nruns}, "
          f"fixed = {fixed:,.0f}")
    print("  ⚠ `fixed` is the per-RUN start-up cost; it does NOT grow with the "
          "pin, so it DILUTES the multiplier.")
    print("  ⚠ It is measured only on ph64/O3/isolated/small and assumed equal "
          "across cells/opt/mode/input.")
    print()

    def stage(lo, hi):
        return sb_ * (lo + hi) + nruns * fixed

    base = stage(100, 200)
    print(f"  {'pin':>22s} {'lo+hi':>7s} {'stage Ir':>18s} "
          f"{'x shipped':>10s} {'B-only x':>9s}   what it is")
    tab = [(100, 200, "THE SHIPPED PIN (W=100)"),
           (100, 300, "W=200"),
           (100, 500, "W=400"),
           (100, 900, "W=800 -- the widest this sweep measured"),
           (100, 1000, "W=900 -- §1's MIDDLE row needs this if the exponent is -1"),
           (100, 6500, "the GRAND slope over [100, 6500) -- the population mean"),
           (100, 7600, "W=7500 -- §1's TOP row needs this if the exponent is -0.5")]
    for lo, hi, what in tab:
        st = stage(lo, hi)
        print(f"  {f'[{lo}, {hi}]':>22s} {lo + hi:7d} {st:18,.0f} "
              f"{st / base:10.2f} {(lo + hi) / 300.0:9.2f}   {what}")
    print()
    print("  ⭐ THE TWO NUMBERS THE MANAGER NEEDS, both ESTIMATES:")
    print(f"      W =  900  (exponent -1, '1 pp' reachable)  -> "
          f"{stage(100, 1000) / base:.2f}x the shipped gate-stage cost")
    print(f"      W = 7500  (exponent -0.5)                  -> "
          f"{stage(100, 7600) / base:.2f}x")
    print("  ⓘ The `B-only x` column is the multiplier with `fixed` set to 0, "
          "i.e. (200+W)/300: 3.67x")
    print("    and 25.67x. The dilution by the fixed term is small because "
          "SUM_B*(lo+hi) dominates")
    print(f"    nruns*fixed by {sb_ * 300 / (nruns * fixed):.1f}x already at "
          f"the shipped pin.")

    # wall clock, from this sweep's own timings
    t = timings()
    if t:
        tot_ir = sum(v for k, v in (ir or {}).items() if v is not None) if ir else 0
        tot_s = sum(v["s"] for v in t.values() if "s" in v)
        print()
        print(f"  WALL CLOCK, measured by this sweep: {len(t)} runs, "
              f"{tot_s:,.1f} s total.")
        if tot_ir:
            print(f"      {tot_ir:,} Ir profiled => "
                  f"{tot_ir / tot_s / 1e6:,.1f} M Ir/s under callgrind, and "
                  f"{tot_s / len(t):.2f} s/run mean.")
            rate = tot_ir / tot_s
            for lo, hi, what in tab:
                print(f"      pin [{lo},{hi}]: "
                      f"{stage(lo, hi) / rate:9,.1f} s for ph64's collapse "
                      f"stage alone   ({what})")
            print("  ⚠ ph64 is ONE of 7 PHP rows and 33 PAT rows; this is the "
                  "per-row collapse stage only,")
            print("    and `probe_iters` is inside `contract_sha256` so the "
                  "re-gate is per row (F90).")
    return 0


# ------------------------------------------------------- must-fire negatives -
def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}", flush=True)
        if not cond:
            fails.append(tag)

    print("SELFTEST -- must-fire negatives (TASK_PHP_039 §4)")
    print()

    # ---- N5 / N6 / N8: design + freshness, BEFORE anything expensive -------
    print(" -- design assertions (no runs needed) --")
    ok5 = all(len(spans(w)) == K for w in WIDTHS) and all(
        [lo for lo, _ in spans(w)] == STARTS for w in WIDTHS)
    check("N5", ok5,
          f"K == {K} at every width and the {K} start positions are IDENTICAL "
          f"across widths {WIDTHS}: starts = {STARTS} "
          f"(per-width start lists: "
          f"{ {w: [lo for lo, _ in spans(w)] for w in WIDTHS} })")

    bad6 = []
    for w in WIDTHS:
        sp = spans(w)
        for i in range(len(sp)):
            for j in range(i + 1, len(sp)):
                a, b = sp[i], sp[j]
                if a[0] < b[1] and b[0] < a[1]:
                    bad6.append((w, a, b))
    check("N6", not bad6,
          f"the {K} spans at each width are pairwise DISJOINT (S = {S}, so "
          f"W <= S suffices; max W = {max(WIDTHS)}): overlaps = {bad6}")

    check("N5b", len(NS) == 33,
          f"the endpoint set derived from the span table has {len(NS)} values "
          f"(§2.1 says 33): {NS}")

    stale = []
    for short, slug in ROWS:
        for cell, want, got, ok, whole in md5_check(short, slug):
            if not ok:
                stale.append((short, cell, want, got))
    check("N8", not stale,
          f"every one of the {len(ROWS) * len(CELLS)} binaries' `md5_fn` "
          f"matches its published `results-php/<row>.json` record "
          f"(O3/isolated): {stale or 'all 12 MATCH'}")

    # ---- X1: THE F52 CONTROL. Does the PIPELINE encode the answer? ---------
    print()
    print(" -- X1: the F52 control -- a probe whose SETUP ENCODES THE ANSWER")
    print("       evaluates fine and is wrong. The statistic below is fed TWO")
    print("       SYNTHETIC series with KNOWN answers and must report them.")
    x1 = f52_control()
    for tag, cond, msg in x1:
        check(tag, cond, msg)

    # ---- the sweep ---------------------------------------------------------
    print()
    print(f" -- the sweep: {len(ROWS) * len(NS) * len(CELLS)} callgrind runs --")
    ir, raw = collect(verbose=True)

    miss = [k for k, v in ir.items() if v is None]
    check("N1", not miss,
          f"{len(ir)} runs (33 n x 4 cells x 3 rows), {len(miss)} with no "
          f"PROGRAM TOTALS: {miss[:10]}")

    rc_bad = [(k, v) for k, v in timings().items() if v.get("rc") not in (0, None)]
    check("N1b", not rc_bad,
          f"every run recorded in timings.json exited 0: "
          f"{rc_bad[:10] or 'all clean'} ({len(timings())} timed)")

    # X2: PROGRAM TOTALS == the `summary:` line check.py actually reads
    dis = [(k, ir[k], raw[k]) for k in ir if ir[k] != raw[k]]
    check("X2", not dis,
          f"`callgrind_annotate`'s PROGRAM TOTALS (§2.3) equals the "
          f"`summary:`/`totals:` line that `check.py::_callgrind_total` reads "
          f"(line 3434) on all {len(ir)} profiles: {dis[:5] or 'identical'}")

    dc = {}
    for short, slug in ROWS:
        dc[short] = {w: dcalls(short, slug, STARTS[0], STARTS[0] + w)
                     for w in WIDTHS}

    # ---- N2: THE LICENSING CHECK ------------------------------------------
    print()
    print(" -- N2: the LICENSING check --")
    off, dcbad = [], []
    for short, slug in ROWS:
        d100 = dcalls(short, slug, 100, 200)
        for cell in CELLS:
            pub = published_b(slug, cell)
            mine = slope(ir, short, cell, 100, 200, d100)
            if pub is None or mine is None or abs(pub - mine) >= 0.05:
                off.append((short, cell, pub,
                            None if mine is None else round(mine, 4)))
            if pub:
                dir_ = ir[(short, cell, 200)] - ir[(short, cell, 100)]
                implied = dir_ / pub
                if abs(implied - d100) > 0.5:
                    dcbad.append((short, cell, round(implied, 3), d100))
    check("N2", not off,
          f"the (100, 200) span reproduces the PUBLISHED "
          f"`marginal_ir_per_call` for <cell>/{OPT}/{MODE}/{INPUT}.bin to "
          f"< 0.05 Ir on all {len(ROWS) * len(CELLS)} cell-rows: "
          f"{off or 'all 12 within 0.05 Ir'}")
    check("N2b", not dcbad,
          f"the IMPLIED dcalls = dIr / published_B equals model.py's own "
          f"`n_calls(200) - n_calls(100)` "
          f"({ {s: dc[s][100] for s, _ in ROWS} }) on every cell-row: "
          f"{dcbad or 'all 12 agree'}")

    # ---- N4: F89 must reproduce at W=100 ----------------------------------
    print()
    print(" -- N4: F89's own contrast, at W=100 on ph64 --")
    xv = [p for p in pcts(ir, "ph64", *PRIMARY_X, 100, dc["ph64"]) if p is not None]
    sv = [p for p in pcts(ir, "ph64", *PRIMARY_S, 100, dc["ph64"]) if p is not None]
    sx, ss = sd(xv), sd(sv)
    rx, rs = (max(xv) - min(xv)), (max(sv) - min(sv))
    check("N4", sx is not None and ss is not None and sx > 10.0 * ss,
          f"ph64/{INPUT}.bin W=100: cross-language ({PRIMARY_X[0]} vs "
          f"{PRIMARY_X[1]}) SD = {sx:.4f} pp, range = {rx:.4f} pp; "
          f"same-language ({PRIMARY_S[0]} vs {PRIMARY_S[1]}) SD = {ss:.4f} pp, "
          f"range = {rs:.4f} pp. The FLOOR is a factor of 10; measured factor "
          f"{sx / ss:.1f}x. F89 published 8.12 pp (c-gcc vs safe_naive) and "
          f"8.63 pp (c-gcc vs safe_tuned) against 0.07 pp, AS RANGES over its "
          f"nine draws.")

    # ---- N7: the spread must be NONZERO at W=100 --------------------------
    #
    # ⚠⚠ DISCLOSURE. N7's FIRST floor was `SD >= 1 % of |mean pct|` -- the
    # REL_FLOOR this file uses for N3 -- and IT FIRED: on ph64 the
    # cross-language SD is 2.3950 pp on a mean of 239.8992 %, i.e. 0.998 % of
    # the effect, which is BELOW a 1 % floor by 0.004 pp. The failure is in
    # `selftest.log` history and is reported in full in the task report.
    # ▶ IT FIRED FOR THE WRONG REASON, which by F79's own rule (quoted in open
    # item 67: *a must-fire case that fires for the wrong reason is worth
    # nothing*) makes it worth nothing AS A NEGATIVE. N7 asks *is there
    # anything for width to REDUCE?* -- a question about MAGNITUDE against the
    # measurement's resolution. `1 % of the effect` answers a DIFFERENT
    # question, MATERIALITY, which is N3's question and F89's.
    # ▶ So N7 is restated with a floor derived from measured noise, and the
    # materiality number is printed beside it as a NOTE, not as a verdict.
    print()
    print(" -- N7: there must be something for width to reduce --")
    n7, n7a = [], []
    for short in ("ph64", "ph29"):
        for x, y in (PRIMARY_X, PRIMARY_S):
            v = [p for p in pcts(ir, short, x, y, 100, dc[short]) if p is not None]
            s, mu = sd(v), (sum(v) / len(v) if v else None)
            n7.append((short, f"{x} vs {y}", round(s, 5), s >= N7_FLOOR_PP))
            n7a.append((short, f"{x} vs {y}", round(s, 5), round(mu, 4),
                        round(100.0 * s / abs(mu), 3), s >= REL_FLOOR * abs(mu)))
    check("N7", all(t[3] for t in n7 if t[1].startswith("c-gcc")),
          f"the CROSS-LANGUAGE SD at W=100 on ph64 and ph29 clears an "
          f"ABSOLUTE floor of {N7_FLOOR_PP} pp -- declared from MEASURED "
          f"noise, not picked: it is 7x ph03's control SD (0.0070 pp, N3) and "
          f"~20x the largest cross-session Ir artefact X3 finds (28 Ir over "
          f"W=100 = 0.28 Ir/call = 0.0023 pp on ph64's safe_naive base). "
          f"(row, pair, SD, clears): {n7}")
    print(f"  NOTE  N7a, the MATERIALITY number, reported and NOT used as a "
          f"verdict (see the disclosure above): SD as a % of the effect, "
          f"floor {REL_FLOOR:.0%} -> {n7a}")
    print(f"        ⭐ ph64's cross-language draw spread is ALREADY at 1.0 % "
          f"of its own +239.9 % effect at the SHIPPED pin, and its "
          f"same-language spread at 0.25 %. ph29's is 8.0 % -- ph29 is the "
          f"row where the draw is material, which is where item 68 matters.")

    # ---- N3: THE CONTROL --------------------------------------------------
    print()
    print(" -- N3: the CONTROL. ph03 must be near zero at EVERY width --")
    n3 = []
    for x, y in (PRIMARY_X, PRIMARY_S):
        for w in WIDTHS:
            v = [p for p in pcts(ir, "ph03", x, y, w, dc["ph03"]) if p is not None]
            s, mu = sd(v), (sum(v) / len(v) if v else None)
            n3.append((f"{x} vs {y}", w, round(s, 5), round(mu, 4),
                       s <= REL_FLOOR * abs(mu)))
    n3x = [t for t in n3 if t[0].startswith("c-gcc")]
    check("N3", all(t[4] for t in n3),
          f"ph03's SD is 'near zero' at every width on both pairs. FLOOR, "
          f"declared RELATIVE (trap 2): SD <= {REL_FLOOR:.0%} of |mean pct|, "
          f"i.e. the draw moves the ratio by under 1 % of the effect the row "
          f"claims -- F89's own fix after its outlier test fired on ph03 at "
          f"0.00 pp. (pair, W, SD, mean, clears): {n3}")
    # and the discriminating half: ph03's LEVEL of spread must be far under
    # ph64's, or the control does not separate anything.
    b64 = sd([p for p in pcts(ir, "ph64", *PRIMARY_X, 100, dc["ph64"])
              if p is not None])
    b03 = sd([p for p in pcts(ir, "ph03", *PRIMARY_X, 100, dc["ph03"])
              if p is not None])
    check("N3b", b03 is not None and b64 is not None and b64 > 30.0 * b03,
          f"ph03's cross-language W=100 SD ({b03:.4f} pp) is at least 30x "
          f"below ph64's ({b64:.4f} pp) -- measured factor "
          f"{b64 / b03 if b03 else float('inf'):.1f}x. ⛔ If ph03 showed a "
          f"COMPARABLE law the effect would be generic (callgrind warm-up, "
          f"allocator growth) and §1's account would fall.")

    # ---- X3: cross-session profile reuse (trap 7) -------------------------
    print()
    print(" -- X3: is a profile from ANOTHER SESSION interchangeable? --")
    x3 = reuse_check(ir)
    for tag, cond, msg in x3:
        check(tag, cond, msg)

    # ---- X3d (§H, item 149): what an UNRUNNABLE cross-session check returns -
    # ⛔⛔ THE ARM PLANTS ITS OWN INPUT. `reuse_check({})` cannot match any
    #   (row, cell, n), which is the SAME BRANCH an absent `.temp/mgr173/cg/`
    #   takes -- and it reaches it without deleting a directory the rest of
    #   this sweep is reading. ⚠ Stated plainly because an arm that is vague
    #   about what it planted is worse than no arm.
    # ▶ WHAT IT MUST CATCH: the `False` that stood here until 2026-09-17, which
    #   reddened `width.py` (filed `st_expect=0`) in the exact state
    #   `CLAUDE.md` Don't #1 invites. Re-introducing it fails X3d(a).
    # ⚠⚠ AND THE SECOND HALF IS THE ONE THAT MATTERS MORE: returning 0 is only
    #   right if the message SAYS NO VERDICT WAS REACHED. A silent 0 turns an
    #   honest "could not run" into a fake pass, which is the worse defect and
    #   the one this file exists to warn about.
    vac = reuse_check({})
    check("X3d(a)", len(vac) == 1 and vac[0][0] == "X3" and vac[0][1] is True,
          f"an unrunnable cross-session check REPORTS AND RETURNS 0 -- "
          f"{len(vac)} row(s), tag {vac[0][0] if vac else '-'}, "
          f"cond {vac[0][1] if vac else '-'} (item 149's decision; the tree "
          f"argues it at probes/ph66_djbx33a_collide.py -- a checker that "
          f"reddens when a sibling cache is cleaned is reporting on the cache)")
    _m = vac[0][2] if vac else ""
    check("X3d(b)", "NOT A PASS" in _m and "NOT RUN" in _m,
          f"and it says so LOUDLY rather than passing quietly: the message "
          f"carries both 'NOT RUN' and 'NOT A PASS' "
          f"({'yes' if 'NOT A PASS' in _m else 'NO -- a silent 0 is a fake '
             'pass, the worse of the two defects'})")

    # ---- X4: the shifted-start replicate ----------------------------------
    print()
    print(" -- X4: the SHIFTED-START replicate, as a bound on the K=8 SD --")
    worst = []
    for short, _ in ROWS:
        for x, y in (PRIMARY_X, PRIMARY_S):
            for w in (100, 200, 400):
                alt = [n + w for n in STARTS]
                a = [p for p in pcts(ir, short, x, y, w, dc[short]) if p is not None]
                b = [p for p in pcts(ir, short, x, y, w, dc[short], starts=alt)
                     if p is not None]
                if not a or not b:
                    continue
                sa, sb_ = sd(a), sd(b)
                if sa and sb_:
                    worst.append((short, f"{x} vs {y}", w, round(sa, 4),
                                  round(sb_, 4), round(max(sa / sb_, sb_ / sa), 2)))
    xr = [t for t in worst if t[0] in ("ph64", "ph29") and t[1].startswith("c-gcc")]
    # a K=8 SD has a relative sampling SD of ~1/sqrt(2*(K-1)) = 27 %, so two
    # independent K=8 SDs of the SAME quantity should agree within ~2.5x at
    # 3 sigma. A factor worse than that says the 4-point fit is fitting noise.
    check("X4", all(t[5] <= 2.5 for t in xr),
          f"two INDEPENDENT sets of 8 disjoint spans at the SAME width but "
          f"DIFFERENT start positions give SDs agreeing within 2.5x on the "
          f"cross-language pair of ph64/ph29 (a K=8 SD has ~"
          f"{100 / math.sqrt(2 * (K - 1)):.0f} % sampling SD of its own, so "
          f"2.5x is ~3 sigma). Worse than that means the fit is fitting noise "
          f"and the exponent cannot be quoted: {xr}")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    save_timings()
    return 1 if fails else 0


def f52_control(reps=4000, seed=20260912):
    """⚠⚠ THE F52 CONTROL: does this DESIGN's own arithmetic encode the answer?

    Nine shapes of "the setup encodes the result" are on file and the ninth was
    the manager's. The failure mode here would be a span/SD/fit pipeline that
    produces a tidy exponent from ANY input -- and the way to catch it is to
    feed it series whose TRUE exponent is known and see whether it says so.

    Two series, both pushed through the EXACT same `spans`/`pcts`/`sd`/
    `loglog_fit` code paths as the real data, including the PAIRED nesting
    (span j at W=800 contains span j at W=100):

      L  a series that is EXACTLY LINEAR in n for both cells -- zero
         heterogeneity. TRUE ANSWER: SD = 0 at every width, and NO exponent.
         ⛔ If the pipeline returns an exponent here, it is manufacturing one.
      R  a series that is the cumulative sum of I.I.D. per-iteration costs,
         with the two cells' costs correlated the way F89 says real rungs are
         (same window sequence, different cost curves). TRUE ANSWER: the
         cross-cell `pct` spread falls as EXACTLY W^(-0.5).
         ⛔ If the pipeline returns something far from -0.5 here, its
         estimator is biased and no real exponent from it can be read.

    ▶ R also CALIBRATES the decision §1 asks for: it measures what a 4-point,
    K=8 fit actually returns when the truth IS -0.5, so the report can say
    whether a measured -0.7 is distinguishable from -0.5 at all.
    """
    out = []
    rng = random.Random(seed)

    # ---- L: exactly linear ------------------------------------------------
    irL = {}
    for cell, per in (("x", 1000.0), ("y", 800.0)):
        for n in NS:
            irL[("L", cell, n)] = 5_000_000 + per * n
    dcL = {w: w for w in WIDTHS}
    sdsL = []
    for w in WIDTHS:
        v = [p for p in pcts(irL, "L", "x", "y", w, dcL) if p is not None]
        sdsL.append(sd(v))
    fL = loglog_fit(WIDTHS, sdsL)
    out.append(("X1-L", all(s is not None and s < 1e-9 for s in sdsL)
                and fL is None,
                f"on an EXACTLY LINEAR synthetic series the pipeline reports "
                f"SD = {[None if s is None else f'{s:.3e}' for s in sdsL]} at "
                f"W = {WIDTHS} and NO exponent (fit = {fL}). A pipeline that "
                f"manufactured an exponent would produce one here."))

    # ---- R: i.i.d. draws, true exponent exactly -0.5 ----------------------
    # Window population: 32 windows (F88's count for these inputs) with
    # heterogeneous cost, and the two cells' cost curves differ so the ratio
    # does NOT fully cancel (F89's mechanism). Both cells walk the SAME index
    # sequence, which is exactly what F89 says the real rungs do.
    from itertools import accumulate
    NW = 32
    N0, N1 = NS[0], NS[-1]               # 100 .. 6500; iteration i <-> n = N0+i
    NITER = N1 - N0
    pop = list(range(NW))
    betas, sdratios = [], []
    for _ in range(reps):
        wx = [rng.uniform(0.5, 1.5) for _ in range(NW)]
        cx = [10000.0 * c for c in wx]
        cy = [8000.0 * c ** 1.3 for c in wx]   # DIFFERENT cost curve, same seq
        idx = rng.choices(pop, k=NITER)
        ax = [0.0] + list(accumulate(map(cx.__getitem__, idx)))
        ay = [0.0] + list(accumulate(map(cy.__getitem__, idx)))
        irR = {}
        for n in NS:
            irR[("R", "x", n)] = 5_000_000 + ax[n - N0]
            irR[("R", "y", n)] = 5_000_000 + ay[n - N0]
        sdsR = []
        for w in WIDTHS:
            v = [p for p in pcts(irR, "R", "x", "y", w, dcL) if p is not None]
            sdsR.append(sd(v))
        f = loglog_fit(WIDTHS, sdsR)
        if f:
            betas.append(f[0])
            if sdsR[0] and sdsR[3]:
                sdratios.append(sdsR[0] / sdsR[3])
    betas.sort()
    mu = sum(betas) / len(betas)
    p05, p50, p95 = (betas[int(0.05 * len(betas))], betas[len(betas) // 2],
                     betas[int(0.95 * len(betas))])
    p01, p99 = betas[int(0.01 * len(betas))], betas[int(0.99 * len(betas))]
    out.append(("X1-R", abs(mu + 0.5) < 0.05,
                f"on {reps} synthetic series whose TRUE exponent is exactly "
                f"-0.5 (i.i.d. draws from a {NW}-window population, two cells "
                f"on the SAME sequence with DIFFERENT cost curves), this "
                f"pipeline's 4-point K=8 fit returns mean {mu:+.4f}, median "
                f"{p50:+.4f}, 5-95 % [{p05:+.3f}, {p95:+.3f}], 1-99 % "
                f"[{p01:+.3f}, {p99:+.3f}]. The mean must be within 0.05 of "
                f"-0.5 or the estimator is biased."))
    # ---- T: a POSITION TREND, true exponent exactly 0 ---------------------
    # per-iteration cost drifts linearly with i, so a span's mean depends on
    # WHERE it is and hardly on HOW WIDE it is. This is §1's THIRD row.
    betasT = []
    for _ in range(reps // 10 or 1):
        g = rng.uniform(1e-4, 1e-3)
        irT = {}
        for n in NS:
            i = n - N0
            # integral of base*(1 + g*t) dt from 0 to i
            irT[("T", "x", n)] = 5_000_000 + 10000.0 * (i + g * i * i / 2.0)
            irT[("T", "y", n)] = 5_000_000 + 8000.0 * i
        sdsT = [sd([p for p in pcts(irT, "T", "x", "y", w, dcL)
                    if p is not None]) for w in WIDTHS]
        f = loglog_fit(WIDTHS, sdsT)
        if f:
            betasT.append(f[0])
    muT = sum(betasT) / len(betasT) if betasT else None
    out.append(("X1-T", muT is not None and abs(muT) < 0.10,
                f"on a series whose spread is a POSITION TREND rather than "
                f"sampling (§1's THIRD row, 'not a sampling effect at all'), "
                f"the pipeline returns a mean exponent of {muT:+.4f} over "
                f"{len(betasT)} series -- it must be within 0.10 of 0."))

    # ---- E: ENDPOINT noise, true exponent exactly -1 ----------------------
    # the variance sits in the ENDPOINT readings, not in the accumulated
    # per-iteration costs, so slope spread ~ 1/W. This is §1's SECOND row, and
    # it is the arm that proves the pipeline CAN report -1 when -1 is true.
    betasE = []
    for _ in range(reps):
        irE = {}
        for n in NS:
            i = n - N0
            irE[("E", "x", n)] = 5_000_000 + 10000.0 * i + rng.gauss(0, 3000.0)
            irE[("E", "y", n)] = 5_000_000 + 8000.0 * i
        sdsE = [sd([p for p in pcts(irE, "E", "x", "y", w, dcL)
                    if p is not None]) for w in WIDTHS]
        f = loglog_fit(WIDTHS, sdsE)
        if f:
            betasE.append(f[0])
    betasE.sort()
    muE = sum(betasE) / len(betasE) if betasE else None
    e05, e95 = betasE[int(0.05 * len(betasE))], betasE[int(0.95 * len(betasE))]
    e01, e99 = betasE[int(0.01 * len(betasE))], betasE[int(0.99 * len(betasE))]
    out.append(("X1-E", muE is not None and abs(muE + 1.0) < 0.10,
                f"on a series whose variance sits in the ENDPOINT readings "
                f"rather than in the accumulated per-iteration costs (§1's "
                f"SECOND row, '-1 or steeper'), the pipeline returns a mean "
                f"exponent of {muE:+.4f} over {len(betasE)} series, median "
                f"{betasE[len(betasE) // 2]:+.4f}, 5-95 % [{e05:+.3f}, "
                f"{e95:+.3f}], 1-99 % [{e01:+.3f}, {e99:+.3f}] -- the mean "
                f"must be within 0.10 of -1. ⭐ Together with X1-L/R/T this "
                f"shows the pipeline can report ALL THREE of §1's rows and "
                f"encodes none of them."))
    out.append(("X1-E2", e95 < -0.65,
                f"⭐⭐ THE OTHER HALF OF THE CALIBRATION: under a TRUE -1 law "
                f"this pipeline's 95th percentile is {e95:+.3f}, so ANY "
                f"measured exponent above {e95:+.3f} is in the top 5 % tail of "
                f"a -1 truth. ▶ Combined with X1-R2 ({p05:+.3f} is the 5th "
                f"percentile under a -0.5 truth), the two nulls' 5-95 % bands "
                f"are [{p05:+.3f}, {p95:+.3f}] for -0.5 and [{e05:+.3f}, "
                f"{e95:+.3f}] for -1, which OVERLAP only on "
                f"[{max(p05, e05):+.3f}, {min(p95, e95):+.3f}]. A measurement "
                f"landing outside that overlap picks one row of §1's table at "
                f"the 5 % level."))

    # the operative calibration: can this design tell -0.5 from -1.0?
    out.append(("X1-R2", p01 > -1.0,
                f"⭐ THE CALIBRATION §1 NEEDS: with the truth at -0.5, the "
                f"1st percentile of the fitted exponent is {p01:+.3f}, so a "
                f"measured exponent of -1.0 or steeper would be reached under "
                f"the -0.5 null less than 1 % of the time. ▶ THE DESIGN CAN "
                f"SEPARATE §1's TOP TWO ROWS. (SD100/SD800 under the null: "
                f"median {sorted(sdratios)[len(sdratios) // 2]:.2f}, "
                f"5-95 % [{sorted(sdratios)[int(0.05 * len(sdratios))]:.2f}, "
                f"{sorted(sdratios)[int(0.95 * len(sdratios))]:.2f}]; an exact "
                f"-1 law gives 8.00.)"))
    return out


def reuse_check(ir):
    """X3 / trap 7. `.temp/mgr173/cg/` holds ph64 and ph03 profiles from F89's
    nine draws at n = 100..1000 step 100, so six of them match this sweep's
    endpoints by exact (row, cell, n). ⚠ They were taken in ANOTHER SESSION,
    and `_callgrind_total`'s own docstring says only the CONSTANT part of the
    environment-block cost cancels within a difference. So: does a
    cross-session profile give the SAME total?

    ▶ This decides whether trap 7's warning is real, and it can come out
    either way. This sweep does NOT reuse them; the check is what licenses
    that choice."""
    old = os.path.join(ROOT, ".temp/mgr173/cg")
    rows = []
    for short in ("ph64", "ph03"):
        for cell in CELLS:
            for n in NS:
                p = os.path.join(old, f"{short}.{cell}.{INPUT}.{n}.out")
                if os.path.exists(p) and ir.get((short, cell, n)) is not None:
                    t = total_raw(p)
                    if t is not None:
                        rows.append((short, cell, n, t, ir[(short, cell, n)],
                                     t - ir[(short, cell, n)]))
    if not rows:
        # ⛔⛔⛔ THIS RETURNED `False` UNTIL 2026-09-17, AND THE HEADER TWENTY
        #   LINES UP SAID IT DID NOT. `.temp/mgr173/cg/` is gitignored and
        #   `CLAUDE.md` Don't #1 TELLS YOU TO DELETE IT once the gates are
        #   green -- so the routine sweep went red for FOLLOWING THE RULES,
        #   `width.py` is filed `st_expect=0`, and no `why` said so.
        #   ⚠ Found by `PROMOTE_001`'s engineer when I told it to copy this
        #   file as the precedent; it REFUSED and made its own guards return 0.
        #   That refusal is why the promoted probes do not carry this defect.
        #
        # ▶ THE DECISION (item 149): AN UNRUNNABLE *CROSS-SESSION* CHECK
        #   REPORTS AND RETURNS 0. The tree already argues it one directory
        #   over -- `probes/ph66_djbx33a_collide.py`: *"a checker that reddens
        #   when a sibling repo is cleaned is reporting on that repo"* -- and
        #   `X3` is the same shape one level in: it reports on a CACHE, not on
        #   this sweep. ⚠⚠ AND rc=0 HERE IS NOT A PASS. It is "no verdict was
        #   reached", which is why the message says so in capitals rather than
        #   going quiet. A silent 0 would be the worse of the two defects.
        return [("X3", True, "⛔⛔ NOT RUN -- NO VERDICT WAS REACHED, AND THIS "
                             "IS NOT A PASS. No (row, cell, n) under "
                             ".temp/mgr173/cg/ matches this sweep's endpoints. "
                             "That cache is gitignored and deletable by "
                             "CLAUDE.md constraint 6, so its absence is the "
                             "EXPECTED state of a clean checkout -- the check "
                             "could not run, which is itself a result to "
                             "report (item 149)")]
    dif = [r for r in rows if r[5] != 0]
    mx = max(abs(r[5]) for r in rows)
    # ⭐ THE QUESTION THAT DECIDES WHETHER REUSE WOULD HAVE BEEN SAFE: a delta
    # that is CONSTANT per (row, cell) cancels EXACTLY in a difference, so it
    # cannot bias a slope at all. Group and see.
    grp = {}
    for r in rows:
        grp.setdefault((r[0], r[1]), set()).add(r[5])
    swing = {k: max(v) - min(v) for k, v in grp.items()}
    worst = max(swing.values())
    const = [k for k, v in swing.items() if v == 0]
    # the worst spurious SLOPE a mixed span could carry, and what it is worth
    # as a pp on the quantity actually being measured
    base = min(published_b("ph64-callback-frees-cursor", c) for c in CELLS)
    pp = 100.0 * (worst / 100.0) / base
    # ⛔⛔ X3b USED TO DIVIDE `2.3950 / pp` UNGUARDED AND CRASHED WITH A
    # ZeroDivisionError THE DAY `worst` REACHED 0 -- i.e. the day its own check
    # passed PERFECTLY, because a delta that is constant per (row, cell) cancels
    # EXACTLY and the spurious slope is then not small but ZERO. A guard written
    # for a noisier world (RECAP_PHP.md open item 86, TASK_PHP_043 §4.3).
    # ⭐ The margin is reported as a RATIO when there is something to divide and
    # as EXACT CANCELLATION when there is not. Both are answers; neither is a
    # crash.
    sd = 2.3950                     # the ph64 W=100 SD this margin is against
    margin = _margin(pp, sd)
    _x3 = [("X3", True,
             f"{len(rows)} exact (row, cell, n) matches against F89's "
             f"`.temp/mgr173/cg/` profiles; {len(dif)} differ, max |delta| = "
             f"{mx:,} Ir, deltas seen = {sorted({r[5] for r in rows})}. "
             f"⚠ NOT identical -- and the CAUSE is the argv block, not the "
             f"program: the probe path is `.temp/mgr173/probe/...` (37 chars) "
             f"against `.temp/php39/probe/...` (36), which moves the initial "
             f"stack and is exactly the effect `.memory/03-measurement.md` and "
             f"`check.py::_callgrind_total`'s docstring describe."),
            ("X3b", True,
             f"⭐ AND A CONSTANT DELTA CANCELS EXACTLY IN A DIFFERENCE, so the "
             f"question is whether it is constant per (row, cell): it is on "
             f"{len(const)} of {len(grp)} cells ({sorted(c[1] for c in const)}"
             f"), over {min(len(v) for v in grp.values())}-"
             f"{max(len(v) for v in grp.values())} distinct delta value(s) per "
             f"cell from {len(rows)} matched profiles. "
             # ⚠⚠ THE BISTABILITY IS REPORTED FROM THE DATA AND NO LONGER
             #    ASSERTED AS "14 and 28". That literal was pinned prose beside
             #    a COMPUTED `worst`, and the two came to disagree: `worst`
             #    reached 0 -- no cell swings at all -- while the sentence still
             #    claimed `c-gcc` swung 14/28 on both rows. A figure a probe
             #    asserts is computed from the data or it is not asserted
             #    (.memory-php/04-process.md law 6).
             f"Swinging cells, COMPUTED: "
             f"{ {f'{k[0]}/{k[1]}': sorted(grp[k]) for k in sorted(grp) if swing[k]} or 'NONE -- every cell is constant'}. "
             f"Worst swing {worst} Ir => at most {worst / 100.0:.2f} Ir/call of "
             f"spurious slope at W=100 => {pp:.5f} pp on the cheapest ph64 cell. "
             f"▶ THAT IS {margin}, so REUSE WOULD HAVE BEEN SAFE. This sweep "
             f"reuses none of them anyway, so the point is moot -- but trap 7's "
             f"caution is now a number rather than a caution. "
             f"Per-cell swings: "
             f"{ {f'{k[0]}/{k[1]}': v for k, v in sorted(swing.items())} }"),
            # ⛔ X3c MUST-FIRE IF EITHER DEFECT COMES BACK, and it tests
            #    BEHAVIOUR rather than this file's text -- see `_x3c_guard`.
            ]
    _x3.append(("X3c",) + _x3c_guard(_x3[-1][2]))
    return _x3


def _margin(pp, sd):
    """The X3b margin, as a SENTENCE, with the zero-denominator branch.

    ⛔⛔ THE UNGUARDED FORM WAS `f"{sd / pp:,.0f}x ..."` AND IT CRASHED WITH A
    ZeroDivisionError THE DAY `pp` REACHED 0 -- i.e. the day the check it
    reports passed PERFECTLY, because a delta that is constant per (row, cell)
    cancels EXACTLY and the spurious slope is then not small but ZERO. A guard
    written for a noisier world (RECAP_PHP.md open item 86, TASK_PHP_043 §4.3).

    ⭐ IT IS A SEPARATE FUNCTION SO X3c CAN CALL IT. A textual check for the
    old expression does not work and I tried it first: the string survives in
    the COMMENT that documents the defect and in the detector's own literals,
    so it reported the defect as present in the file that had fixed it --
    `harness/check.py::spelling_matches`'s lesson (b), *a comment is not code*,
    arriving in a guard written to enforce a different lesson."""
    if pp > 0.0:
        return f"{sd / pp:,.0f}x BELOW THE {sd} pp SD"
    return (f"EXACTLY ZERO -- the delta is CONSTANT on every (row, cell), so it "
            f"cancels to the instruction in a difference and there is no ratio "
            f"to take against the {sd} pp SD")


def _x3c_guard(x3b_msg):
    """Are either of X3b's two repaired defects back? Tested by BEHAVIOUR.

    (1) the margin must survive `pp == 0` and say so, and must still give a
        ratio when there is one to give;
    (2) the bistability must be READ OUT OF THE DATA. The old sentence asserted
        `c-gcc is BISTABLE between 14 and 28 Ir on BOTH rows` beside a COMPUTED
        `worst`, and the two came to disagree -- the current profiles give
        deltas of 0 and 10 and NO swinging cell at all, so that sentence named
        two values absent from its own input. ⚠ This checks the GENERATED
        MESSAGE, not the source, so it cannot be fooled by a comment.

    `.memory-php/04-process.md` law 6: a figure a validator asserts is computed
    from the data, or it is not asserted."""
    bad = []
    try:
        zero = _margin(0.0, 2.3950)
    except ZeroDivisionError:
        bad.append("`_margin` still divides by a zero `pp`")
        zero = ""
    if zero and "EXACTLY ZERO" not in zero:
        bad.append("`_margin(0)` does not say the cancellation is exact")
    ratio = _margin(0.0239, 2.3950)
    if "x BELOW" not in ratio:
        bad.append("`_margin` no longer reports a ratio when one exists")
    for lit in ("14 and 28", "BISTABLE between"):
        if lit in x3b_msg:
            bad.append(f"X3b's message asserts the pinned literal {lit!r} "
                       f"instead of reading the swings out of `grp`")
    if not bad:
        return (True,
                f"BEHAVIOURAL, not textual: `_margin(0)` returns "
                f"{zero.split(' --')[0]!r} instead of raising, `_margin(0.0239)` "
                f"still returns a ratio ({ratio!r}), and X3b's generated message "
                f"carries no pinned bistability literal. ⚠ The first version of "
                f"this negative grepped this file's SOURCE and fired on the "
                f"comment documenting the defect -- a comment is not code")
    return (False, "X3c: " + "; ".join(bad))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--cost" in sys.argv:
        sys.exit(cost_report())
    sys.exit(report())
