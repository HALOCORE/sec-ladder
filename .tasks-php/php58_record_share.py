#!/usr/bin/env python3
"""**`F74`'s `inside_share`, for every built php row, out of the COMMITTED
RECORDS** -- no build, no callgrind, no gate. `TASK_PHP_058`.

    python3 .tasks-php/php58_record_share.py              # every row + the ph29 reconciliation
    python3 .tasks-php/php58_record_share.py --row ph29-recvfrom-alloc
    python3 .tasks-php/php58_record_share.py --find 0.655 0.669 0.927
    python3 .tasks-php/php58_record_share.py --pairs   # F74's rule, per published pair
    python3 .tasks-php/php58_record_share.py --selftest    # the must-fire arms

=============================================================================
⚠⚠⚠ WHY THIS EXISTS BESIDE `controls/inside_share.py`, WHICH ALREADY HAS A NAME
=============================================================================
**TWO DIFFERENT QUANTITIES ARE CALLED `inside_share` IN THIS PROGRAMME AND
NOTHING SAID SO.**

    W-share (the rows' control)   A1_total / callgrind `summary:` total, ONE run
    F74-share (this file)         (kernel_exclusive_ir / n_iters) / marginal_ir_per_call

`F74`'s denominator is the **whole-program MARGINAL per call**, which excludes
every fixed cost by construction and is measured by `check.py` stage 3b at
`collapse.probe_iters` -- a different run, at a different iteration count, from
the one the numerator comes off. **Every `inside_share` figure published in
`RECAP_PHP.md`, in `.memory-php/02-ladder.md` and in
`patterns-php/ph29-recvfrom-alloc/controls/spellings.py` is the F74 one**, and
the rule that consumes it -- *(i) `min(inside_share)` HIGH and
(ii) `|Δinside_share| ≤ 0.02`* -- is stated in those terms.

⛔ **THEY ARE NOT INTERCHANGEABLE.** On `ph29`'s `c-gcc`/`small.bin` cell the
two read **0.8045** and **0.8933**; on `ph03`'s `verus`/`small.bin` cell,
**0.9031** and **0.9013**. ⚠⚠ **AND THE F74 ONE EXCEEDS 1.0 ON 15 CELLS
ACROSS TWO ROWS -- 10 on `ph16`, 5 on `ph07`, the largest 1.0353** -- which no
quantity called a *share* can do: the numerator counts a run of `n_iters` calls
and the denominator a slope taken at `probe_iters`. ▶ **That is not a defect in
either statistic; it is the reason to name which one you mean.** ⓘ Count it
rather than trust this line: run the file with no arguments and read the
`ABOVE 1.0` tally it prints from the records.

⚠ This file READS `results-php/` and `patterns-php/*/inputs/*.bin` and writes
nothing. It is deliberately NOT a row control: the numbers derive from the gate
record, which every gate run rewrites, so they cannot be pinned by
`derived_from_sha256` and have no business in a `controls/*.json` sidecar.
"""

import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common-php"))
import slb  # noqa: E402

INPUTS = ("small.bin", "large.bin")


def n_iters(row, inp):
    """The driver's call count, read from the input file's header."""
    return slb.read(os.path.join(REPO, "patterns-php", row, "inputs", inp)).n_iters


def f74_share(kx, iters, marginal):
    """`(kernel_exclusive_ir / n_iters) / marginal_ir_per_call`. PURE.

    `None` when any operand is missing or the denominator is zero -- **never
    0.0**, because a missing operand and a zero share are different facts and
    the second one would read as evidence."""
    if not kx or not iters or not marginal:
        return None
    return (kx / iters) / marginal


def rows():
    return sorted(os.path.basename(p)[:-5]
                  for p in glob.glob(os.path.join(REPO, "results-php", "*.json"))
                  if not os.path.basename(p).startswith("ph00"))


def table(row):
    """`[(cell, opt, mode, input, a1_per_call, marginal, share)]` for every cell
    of one row where the record carries a `kernel_exclusive_ir`.

    ⚠ A cell with no `kernel_exclusive_ir` is OMITTED, not zeroed: at
    `O3`/`whole` the kernel is inlined into `main` and the record's own value is
    `null`, so the ratio is UNDEFINED rather than 100 %."""
    mrec = json.load(open(os.path.join(REPO, "results-php", row + ".json")))
    grec = json.load(open(os.path.join(REPO, "results-php", "gate", row + ".json")))
    marg = grec["marginal_ir_per_call"]
    out = []
    for c in mrec["cells"]:
        for inp in INPUTS:
            kx = ((c.get("ir") or {}).get(inp) or {}).get("kernel_exclusive_ir")
            if kx is None:
                continue
            m = marg.get(f"{c['cell']}/{c['opt']}/{c['mode']}/{inp}")
            it = n_iters(row, inp)
            out.append((c["cell"], c["opt"], c["mode"], inp,
                        kx / it, m, f74_share(kx, it, m)))
    return out


def find(value, tol, only=None):
    """Every (row, cell) whose F74 share rounds to `value` within `tol`."""
    hits = []
    for r in (only or rows()):
        for cell, opt, mode, inp, a1, m, s in table(r):
            if s is not None and abs(s - value) <= tol:
                hits.append((r, cell, opt, mode, inp, s))
    return hits


# --------------------------------------------------------------------------
_SYNTH = [("a", "O3", "isolated", "small.bin", 1.0, 2.0, 0.500),
          ("b", "O3", "isolated", "small.bin", 1.0, 2.0, 0.655)]


def arms():
    """`[(name, expected, ok, got)]` -- five must-fire, two must-NOT-fire."""
    out = []

    def arm(name, expect, got):
        out.append((name, expect, got == expect, got))

    arm("1 must-NOT-fire: the ratio is (kx/n)/marginal", 0.5,
        f74_share(1000, 100, 20.0))
    arm("2 MUST-FIRE: a missing kernel_exclusive_ir is None, NOT 0.0", None,
        f74_share(None, 100, 20.0))
    arm("3 MUST-FIRE: a missing marginal is None, NOT a division error", None,
        f74_share(1000, 100, None))
    arm("4 MUST-FIRE: a zero marginal is None, NOT infinity", None,
        f74_share(1000, 100, 0))
    arm("5 must-NOT-fire: a share above 1.0 is REPORTED, not clamped", 1.25,
        f74_share(1000, 100, 8.0))
    got = [(r[0], r[6]) for r in _find_in(_SYNTH, 0.655, 0.0005)]
    arm("6 must-NOT-fire: a planted value is found", [("b", 0.655)], got)
    arm("7 MUST-FIRE: an absent value is NOT found", [],
        [(r[0], r[6]) for r in _find_in(_SYNTH, 0.900, 0.0005)])
    return out


def _find_in(tbl, value, tol):
    return [t for t in tbl if t[6] is not None and abs(t[6] - value) <= tol]


# --------------------------------------------------------------------------
#: the pairs a row can publish a difference over. ⚠ Not every row publishes
#: every one; the point of printing all nine is that a reader can see which
#: comparison the rule admits WITHOUT first deciding which one the row makes.
PAIRS = [("safe_tuned", "unsafe"), ("safe_naive", "safe_tuned"),
         ("unsafe", "verus"), ("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h"),
         ("c-gcc", "safe_naive"), ("c-clang", "safe_naive"),
         ("c-gcc", "safe_tuned"), ("c-clang", "safe_tuned")]


def pairs(row):
    """`[(a, b, input, a1_delta_pct, share_a, share_b, abs_delta, passes_ii)]`.

    **`F74`'s corrected rule** (`RECAP_PHP.md` F74, `.memory-php/02-ladder.md`):
    *(i) `min(inside_share)` over the two cells must be HIGH -- threshold
    explicitly NOT tuned, six rows cannot pin it -- AND
    (ii) `|d inside_share| <= 0.02`.*

    ⛔ **Only (ii) is computed here, because only (ii) is a number.** A column
    that printed a verdict for (i) would be inventing the threshold this
    programme has twice declined to set."""
    t = {(c, i): (a1, s) for c, o, m, i, a1, mg, s in table(row)
         if o == "O3" and m == "isolated"}
    out = []
    for a, b in PAIRS:
        for inp in INPUTS:
            if (a, inp) not in t or (b, inp) not in t:
                continue
            (a1a, sa), (a1b, sb) = t[(a, inp)], t[(b, inp)]
            if sa is None or sb is None:
                continue
            d = abs(sa - sb)
            out.append((a, b, inp, 100.0 * (a1b / a1a - 1), sa, sb, d,
                        d <= 0.02))
    return out


def main(argv):
    if "--selftest" in argv:
        a = arms()
        for name, expect, ok, got in a:
            print(f"  {'ok  ' if ok else 'BAD '}{name}: got {got!r}")
        n_ok = sum(1 for x in a if x[2])
        print(f"\n{n_ok} of {len(a)} arms as expected")
        return 0 if n_ok == len(a) else 1

    if "--pairs" in argv:
        for r in (rows() if "--row" not in argv
                  else [argv[argv.index("--row") + 1]]):
            print(f"\n=== {r}   O3/isolated   -- rule (ii) only; (i) has no "
                  f"written threshold")
            print(f"  {'pair':28s} {'input':10s} {'A1 delta':>10s} "
                  f"{'shares':>17s} {'abs delta':>10s} {'rule(ii)':>9s}")
            for a, b, inp, dpct, sa, sb, d, ok in pairs(r):
                print(f"  {a + ' vs ' + b:28s} {inp:10s} {dpct:+9.2f}% "
                      f"{sa:8.4f}/{sb:8.4f} {d:10.4f} "
                      f"{'PASS' if ok else 'FAIL':>9s}")
        return 0

    if "--find" in argv:
        for v in argv[argv.index("--find") + 1:]:
            val = float(v)
            print(f"\n=== cells whose F74 share is {val} +- 0.0005")
            hits = find(val, 0.0005)
            for r, cell, opt, mode, inp, s in hits:
                print(f"  {r:28s} {cell:11s} {opt}/{mode:8s} {inp:10s} {s:.6f}")
            print(f"  {len(hits)} cell(s)")
        return 0

    only = None
    if "--row" in argv:
        only = [argv[argv.index("--row") + 1]]

    over_one = []
    for r in (only or rows()):
        print(f"\n=== {r}")
        print(f"  {'cell':11s} {'opt/mode':16s} {'input':10s} "
              f"{'A1/call':>12s} {'marginal':>12s} {'F74 share':>10s}")
        for cell, opt, mode, inp, a1, m, s in table(r):
            flag = "  <-- ABOVE 1.0" if s is not None and s > 1.0 else ""
            if flag:
                over_one.append((r, cell, opt, mode, inp, s))
            print(f"  {cell:11s} {opt + '/' + mode:16s} {inp:10s} "
                  f"{a1:12.2f} {m:12.2f} {s:10.4f}{flag}")

    if over_one:
        print(f"\n  {len(over_one)} cell(s) read ABOVE 1.0. A quantity called a "
              f"SHARE cannot exceed 1: the numerator is measured over "
              f"`n_iters` calls and the denominator is a slope taken at "
              f"`collapse.probe_iters`, so they are not two parts of one run.")

    if only is None:
        print("\n=== the `ph29` docstring's four numbers, searched over EVERY "
              "computable cell of EVERY built row")
        for v in (0.655, 0.669, 0.927):
            hits = find(v, 0.0005)
            print(f"  {v}: {len(hits)} hit(s)")
            for r, cell, opt, mode, inp, s in hits:
                print(f"       {r:28s} {cell:11s} {opt}/{mode:8s} "
                      f"{inp:10s} {s:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
