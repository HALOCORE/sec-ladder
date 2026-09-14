#!/usr/bin/env python3
"""ph56 control -- **WHICH STATISTIC RESOLVES THIS ROW, AND A1 IS NOT BLIND
HERE -- WHICH IS THE OPPOSITE OF `ph55` AND THE REASON IS STRUCTURAL.**

    python3 patterns-php/ph56-fetchmode-arith/controls/statistic.py
    python3 patterns-php/ph56-fetchmode-arith/controls/statistic.py --selftest
    python3 patterns-php/ph56-fetchmode-arith/controls/statistic.py --repeats 3

Produces `../NOTES.md` §12's `inside_share` matrix, its R1-vs-R1h table in BOTH
families and BOTH compilers, and its cross-language table with BOTH C columns.
Writes `statistic.json` beside itself.

⭐⭐⭐ **THE TWO THINGS WORTH KNOWING BEFORE READING THE TABLE.**

1. **A1 SEES THIS ROW'S FIX.** `ph55` reports its upstream fix at *exactly*
   `0.000 %` on every C cell, because there the three lines live in a callee
   that the function-pointer dispatch stops the compiler inlining, so
   `kernel_exclusive_ir` never sees them. Here `ph56_do_end_variable_parse` is a
   `static` reached through an ordinary call from an ordinary loop, it inlines
   into `kernel` at O3, and the R1→R1h delta lands INSIDE the symbol A1 sums.
   ▶ **So the two rows differ on whether A1 can see their own defect, and the
   difference is not about the defect: it is about whether the code path
   between the kernel symbol and the fix goes through a function pointer.**
2. ⛔ **A HIGH `inside_share` IS STILL NOT A CERTIFICATE.** `ph55`'s C cells
   are 74-83 % and A1 reads `0.000 %` on its own defect site anyway. What
   decides whether A is publishable is not how much of the cell A sees but
   whether **THE DIFFERENCE** lands inside it. `STATISTICS_001.md` §4 says
   exactly that. The matrix below is published so a reader can check the
   condition rather than take the share as a proxy for it.

**HOW THE TWO FAMILIES ARE TAKEN.** One callgrind run per (cell, input) yields
both: **A1** is `harness/measure.py::_sum_rows` IMPORTED and never transcribed
(`TASK_PHP_022` §3.2 measured that a transcription is a different function and
produces a plausible wrong number rather than an error); **W1** is
`callgrind_annotate`'s own `PROGRAM TOTALS` line. Callgrind's return code is
checked and so is the presence of the totals line: a probe that CANNOT evaluate
says so rather than returning a figure-shaped `0`.

⛔ **EVERY PERCENTAGE THIS FILE PRINTS NAMES FIVE THINGS** -- statistic, input,
opt/mode, base, and for a C base WHICH COMPILER -- and every cross-language
figure is printed against BOTH `c-gcc-h` and `c-clang-h`, because one C column
is not a number with error bars, it is a different sign (F108).
⛔ **O3 ONLY. No `O0` figure is a performance result** and none is printed.

⚠ **AND NO FAMILY-B FIGURE IS PRINTED HERE AT ALL.** `marginal_ir_per_call` is
a slope over `collapse.probe_iters` and is exposed to argv alignment;
`PROTOCOL_PHP.md` §B5 governs it and `.tasks-php/php50_align_sweep.py` is the
instrument. `../NOTES.md` §12d carries that sweep's two verdicts per pair.

§H (`PROTOCOL_PHP.md`): the verdict functions are functions so they can be
attacked, and `--selftest` drives them over synthetic cells -- **nine must-FIRE
and four must-NOT-fire** -- because a green run over the shipped tree is no
evidence that any arm CAN fire.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

BUILD = os.path.join(ROOT, ".temp", "php-scratch", "build", "ph56")
SCRATCH = os.path.join(ROOT, ".temp", "php56-stat")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

_TOTAL = re.compile(r"^([\d,]+)\s.*PROGRAM TOTALS")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
INPUTS = ["small.bin", "large.bin"]

#: The C bases every cross-language figure owes BOTH of -- F108, and two
#: published claims in the authoritative layer changed SIGN between them.
C_BASES = ["c-gcc-h", "c-clang-h"]
RUST = ["safe_naive", "safe_tuned", "unsafe", "verus"]

#: ⭐ `(C base, input)` pairs whose `inside_share` gap against the Rust cells
#: `../NOTES.md` §12d publishes as NARROW -- i.e. `<= 0.02`, so
#: `STATISTICS_001.md` §1's condition is satisfied and the cross-language
#: column IS admissible in A1 there. **Exactly one pair set qualifies on this
#: row**, and it is a compiler AND an input: clang on the 512-byte window,
#: where clang's `inside_share` is 0.9792 against Rust's 0.9897-0.9922.
#: Everything not listed here is published as WIDE. Arms 7 and 8 check the two
#: halves in opposite directions, so neither can rot silently.
DECLARED_NARROW = {("c-clang-h", "large.bin")}

_M = None


def load_measure():
    """`harness/measure.py`, IMPORTED and never transcribed. Reading under
    `harness/` is what the shim exists to do; `PLAN_PHP.md` §2.1 forbids
    WRITING there."""
    global _M
    if _M is None:
        spec = importlib.util.spec_from_file_location(
            "slb_measure", os.path.join(ROOT, "harness", "measure.py"))
        _M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_M)
    return _M


def n_iters(inp):
    sys.path.insert(0, os.path.join(ROOT, "common"))
    import slb
    return slb.read(os.path.join(PDIR, "inputs", inp)).n_iters


def measure(cell, inp, tag):
    """`(A1, W1, inside_share, error_or_None)` from ONE callgrind run, O3
    isolated. ⚠ `isolated` and not `whole`: in `whole` the kernel is inlined
    into `main` and there is no `kernel` symbol for A1 to sum, which the
    measurement record shows as `kernel=None` on six of this row's eight
    whole cells."""
    exe = os.path.join(BUILD, f"{cell}-O3-isolated")
    if not os.path.exists(exe):
        return None, None, None, (
            f"{cell}: no binary at {exe} -- run "
            f"`python3 harness-php/gate.py --tool build ph56-fetchmode-arith --all`")
    M = load_measure()
    out = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out,
                        exe, os.path.join(PDIR, "inputs", inp)],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        if os.path.exists(out):
            os.unlink(out)
        return None, None, None, (f"callgrind exit {r.returncode} on {tag}: "
                                  f"{r.stderr[-200:]}")
    ann = subprocess.run([M.CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=600)
    txt = (ann.stdout + ann.stderr).strip()
    os.unlink(out)
    k, _names = M._sum_rows(txt, "kernel")
    wp = None
    for ln in txt.splitlines():
        m = _TOTAL.match(ln.strip())
        if m:
            wp = int(m.group(1).replace(",", ""))
            break
    if k is None:
        return None, wp, None, (f"callgrind_annotate named no `kernel` function "
                                f"for {tag} (rc {ann.returncode})")
    if wp is None:
        return k, None, None, (f"callgrind_annotate printed no `PROGRAM TOTALS` "
                               f"line for {tag} -- W1 cannot be computed and "
                               f"must not be reported as 0")
    n = n_iters(inp)
    return k / n, wp / n, k / wp, None


def pct(new, base):
    return None if not base else (new - base) / base * 100.0


# ---- the verdicts, factored so they can be ATTACKED -------------------------

def statistic_problems(rows):
    """The claims `../NOTES.md` §12 makes, as a function of the measured cells.

    1. every cell must have BOTH families. A cell with `A1` and no `W1` cannot
       have an `inside_share` and must not be tabulated as if it did.
    2. `inside_share` must be in `(0, 1]`. Outside that the two families are
       not nested scopes of one run and the whole table is meaningless.
    3. `W1` must be strictly greater than `A1` in every cell -- the whole
       program cannot cost less than one of its symbols.
    4. ⭐ the R1-vs-R1h A1 delta must be NON-ZERO on every C cell. That is this
       row's contrast with `ph55`, where the same delta is exactly zero because
       the fix lives behind a function pointer, and §12b states it as a
       measured property of THIS row. If it ever becomes zero here the section
       is wrong and the reason -- an inlining decision changed -- is worth more
       than the number.
    5. ⭐ `unsafe` and `verus` must report the SAME A1 on every input. §12c
       publishes *R5 costs exactly R4 on this row*, which `ph55` could not say
       (it measured +0.071 % at O3/small). One text, one cost; if the two ever
       diverge the claim goes with it.
    6. ⭐ the ladder must be MONOTONE on every input: R2 >= R3 >= R4. It is the
       only ordering claim §12c makes, it is what a reader takes from the word
       *tuned*, and two corpus rows (`ph45`, `ph52`) have reversed under
       search -- so it is asserted about the SHIPPED cells and about nothing
       else.
    7. ⭐ the gaps the row publishes as **WIDE** must stay wide. `../NOTES.md`
       §12d says the cross-language column against **`c-gcc-h`** may not be
       quoted in A1, because gcc keeps 11-15 % of the per-call work OUTSIDE the
       `kernel` symbol while the Rust cells keep 1-3 % outside -- a gap of
       0.086 to 0.137, far past `STATISTICS_001.md` §1's 0.02. If one of those
       narrows, the reason for publishing that column in W1 has gone stale.
    8. ⭐ and the ONE PAIR SET the row publishes as **NARROW** must stay narrow:
       the four Rust cells against `c-clang-h` **on large.bin only**, where the
       gap is 0.0104-0.0130 and A1 IS admissible. §12d says so explicitly, and
       says it of that input and that compiler and no other.
    ⚠ Arms 7 and 8 are opposite in polarity ON PURPOSE. A single "report every
       gap" arm would fire on the shipped tree -- which is a validator that
       cries wolf, not one that checks anything.
    """
    p = []
    for key, r in sorted(rows.items()):
        if r.get("error"):
            p.append(f"1. {key}: {r['error']}")
            continue
        if r["A1"] is None or r["W1"] is None:
            p.append(f"1. {key}: missing a family (A1={r['A1']}, W1={r['W1']})")
            continue
        if not (0.0 < r["inside_share"] <= 1.0):
            p.append(f"2. {key}: inside_share {r['inside_share']} is outside (0, 1]")
        if r["W1"] < r["A1"]:
            p.append(f"3. {key}: W1 {r['W1']} < A1 {r['A1']} -- the whole program "
                     f"cannot cost less than one of its symbols")
    for inp in INPUTS:
        for r1, r1h in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            a, b = rows.get(f"{r1}/{inp}"), rows.get(f"{r1h}/{inp}")
            if a and b and a.get("A1") is not None and b.get("A1") is not None:
                if a["A1"] == b["A1"]:
                    p.append(
                        f"4. {r1} vs {r1h} on {inp}: A1 is IDENTICAL at "
                        f"{a['A1']}. ../NOTES.md §12b claims A1 SEES this row's "
                        f"fix -- that is how ph56 differs from ph55 -- and it "
                        f"no longer does")
        u, v = rows.get(f"unsafe/{inp}"), rows.get(f"verus/{inp}")
        if u and v and u.get("A1") is not None and v.get("A1") is not None:
            if u["A1"] != v["A1"]:
                p.append(
                    f"5. unsafe vs verus on {inp}: A1 {u['A1']} != {v['A1']}. "
                    f"§12c publishes *R5 costs exactly R4*; one exec text no "
                    f"longer means one cost")
        n2, n3, n4 = (rows.get(f"safe_naive/{inp}"), rows.get(f"safe_tuned/{inp}"),
                      rows.get(f"unsafe/{inp}"))
        if all(x and x.get("A1") is not None for x in (n2, n3, n4)):
            if not (n2["A1"] >= n3["A1"] >= n4["A1"]):
                p.append(
                    f"6. the ladder is NOT monotone on {inp}: R2 {n2['A1']}, "
                    f"R3 {n3['A1']}, R4 {n4['A1']}. §12c's ordering claim is "
                    f"refuted for the shipped cells")
        for base in C_BASES:
            b = rows.get(f"{base}/{inp}")
            for rc in RUST:
                r = rows.get(f"{rc}/{inp}")
                if not (b and r and b.get("inside_share") and r.get("inside_share")):
                    continue
                d = abs(b["inside_share"] - r["inside_share"])
                narrow = (base, inp) in DECLARED_NARROW
                if narrow and d > 0.02:
                    p.append(
                        f"8. {rc} vs {base} on {inp}: |Δinside_share| = {d:.4f} "
                        f"> 0.02, and ../NOTES.md §12d publishes this pair as "
                        f"NARROW -- i.e. as the one place the cross-language "
                        f"column IS admissible in A1. It no longer is")
                if not narrow and d <= 0.02:
                    p.append(
                        f"7. {rc} vs {base} on {inp}: |Δinside_share| = {d:.4f} "
                        f"<= 0.02, and ../NOTES.md §12d publishes this pair as "
                        f"WIDE -- which is its reason for quoting that column "
                        f"in W1 rather than A1. The reason has gone stale")
    return p


def selftest():
    """⛔ The arms above over SYNTHETIC cells. Nine must FIRE, four must not."""
    def cell(a1, w1):
        return {"A1": a1, "W1": w1, "inside_share": a1 / w1, "error": None}

    # ⭐ THE SHIPPED SHAPE, to three decimals, because both polarity arms are
    # checked against it: the fix VISIBLE to A1, R4 == R5, a monotone ladder,
    # gcc's share far below Rust's on BOTH inputs, clang's far below on
    # small.bin and WITHIN 0.02 on large.bin -- which is DECLARED_NARROW.
    good = {
        "c-gcc/small.bin": cell(3243.662, 3665.877),        # .8848
        "c-gcc-h/small.bin": cell(3268.084, 3690.297),      # .8856
        "c-clang/small.bin": cell(2960.773, 3160.525),      # .9368
        "c-clang-h/small.bin": cell(2978.150, 3177.902),    # .9371
        "safe_naive/small.bin": cell(4190.743, 4293.437),   # .9761
        "safe_tuned/small.bin": cell(3562.012, 3664.702),   # .9720
        "unsafe/small.bin": cell(3396.263, 3498.952),       # .9707
        "verus/small.bin": cell(3396.263, 3498.952),
        "c-gcc/large.bin": cell(9268.424, 10844.298),       # .8547
        "c-gcc-h/large.bin": cell(9367.849, 10943.721),     # .8560
        "c-clang/large.bin": cell(9385.609, 9585.965),      # .9791
        "c-clang-h/large.bin": cell(9453.653, 9654.010),    # .9792
        "safe_naive/large.bin": cell(13224.769, 13328.062),  # .9922
        "safe_tuned/large.bin": cell(10759.358, 10862.647),  # .9905
        "unsafe/large.bin": cell(9918.610, 10021.899),      # .9897
        "verus/large.bin": cell(9918.610, 10021.899),
    }

    cases = []
    t = dict(good)
    t["unsafe/small.bin"] = {"A1": 1.0, "W1": None, "inside_share": None,
                             "error": None}
    cases.append(("N1 a cell with no W1", t, True, "1."))
    t = dict(good)
    t["verus/large.bin"] = {"A1": None, "W1": None, "inside_share": None,
                            "error": "no binary"}
    cases.append(("N2 a cell that could not be measured", t, True, "1."))
    t = dict(good)
    t["unsafe/large.bin"] = {"A1": 10.0, "W1": 5.0, "inside_share": 2.0,
                             "error": None}
    cases.append(("N3 inside_share > 1", t, True, "2."))
    t = dict(good)
    t["safe_tuned/small.bin"] = {"A1": 100.0, "W1": 50.0, "inside_share": 0.5,
                                 "error": None}
    cases.append(("N4 W1 below A1", t, True, "3."))
    t = dict(good)
    t["c-gcc-h/small.bin"] = cell(3243.662, 3690.297)   # equal to c-gcc's A1
    cases.append(("N5 A1 goes blind to the fix", t, True, "4."))
    t = dict(good)
    t["verus/small.bin"] = cell(3398.000, 3500.952)
    cases.append(("N6 R5 stops costing exactly R4", t, True, "5."))
    t = dict(good)
    t["safe_tuned/small.bin"] = cell(4300.000, 4402.0)   # dearer than R2
    cases.append(("N7 the ladder is not monotone", t, True, "6."))
    t = dict(good)
    # a WIDE pair narrows: gcc's share on small.bin climbs to Rust's
    t["c-gcc/small.bin"] = cell(3243.662, 3343.0)      # .9703
    t["c-gcc-h/small.bin"] = cell(3268.084, 3368.0)    # .9703
    cases.append(("N8 a pair published as WIDE has narrowed", t, True, "7."))
    t = dict(good)
    # the one NARROW pair widens: clang's share on large.bin falls away
    t["c-clang-h/large.bin"] = cell(9453.653, 11000.0)  # .8594
    cases.append(("N9 the pair published as NARROW has widened", t, True, "8."))

    cases.append(("P1 the shipped shape", good, False, None))
    t = dict(good)
    t["safe_naive/small.bin"] = cell(9000.0, 9100.0)
    t["safe_naive/large.bin"] = cell(30000.0, 30300.0)
    cases.append(("P2 a much dearer R2, ladder still monotone", t, False, None))
    t = dict(good)
    t["c-clang-h/small.bin"] = cell(2978.150, 4000.0)   # small.bin is WIDE either way
    cases.append(("P3 a WIDE C cell's share drops further", t, False, None))
    t = dict(good)
    t["safe_tuned/small.bin"] = cell(3396.263, 3498.952)   # R3 == R4 exactly
    t["safe_tuned/large.bin"] = cell(9918.610, 10021.899)
    cases.append(("P4 R3 equals R4 (monotone is >=, not >)", t, False, None))

    bad = []
    for label, rows, must_fire, arm in cases:
        got = statistic_problems(rows)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} "
                       f"({got[:2]})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, "
                       f"want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repeats", type=int, default=1,
                    help="callgrind repeats per cell; >1 prints the spread and "
                         "is how ../NOTES.md §12a's within-build stability claim "
                         "is reproduced")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARMS, ATTACKED OVER SYNTHETIC CELLS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"13 arms (9 must-FIRE, 4 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    rows, spreads = {}, {}
    print(f"\n1. A1, W1 AND inside_share -- O3/isolated, one callgrind run per "
          f"cell, {args.repeats} repeat(s)")
    print(f"   {'cell':12s} {'input':11s} {'A1 Ir/call':>12s} {'W1 Ir/call':>12s} "
          f"{'inside':>8s} {'spread':>8s}")
    for inp in INPUTS:
        for cell in CELLS:
            vals, err = [], None
            for i in range(args.repeats):
                a, w, s, e = measure(cell, inp, f"{cell}.{inp}.{i}")
                if e:
                    err = e
                    break
                vals.append((a, w, s))
            key = f"{cell}/{inp}"
            if err:
                rows[key] = {"A1": None, "W1": None, "inside_share": None,
                             "error": err}
                print(f"   {cell:12s} {inp:11s} {'--':>12s} {'--':>12s} "
                      f"{'--':>8s}   {err[:40]}")
                continue
            a = vals[0][0]
            w = vals[0][1]
            s = vals[0][2]
            spread = (max(v[0] for v in vals) - min(v[0] for v in vals)
                      if len(vals) > 1 else 0.0)
            spreads[key] = spread
            rows[key] = {"A1": a, "W1": w, "inside_share": s, "error": None}
            print(f"   {cell:12s} {inp:11s} {a:12.3f} {w:12.3f} "
                  f"{s:8.4f} {spread:8.3f}")

    print("\n2. R1 -> R1h, BOTH FAMILIES, BOTH COMPILERS "
          "(statistic / input / O3 isolated / base = the R1 cell of the SAME "
          "compiler)")
    print(f"   {'pair':22s} {'input':11s} {'A1 Ir':>10s} {'A1 %':>9s} "
          f"{'W1 Ir':>12s} {'W1 %':>9s}")
    r1h = {}
    for inp in INPUTS:
        for a_, b_ in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            a, b = rows.get(f"{a_}/{inp}"), rows.get(f"{b_}/{inp}")
            if not (a and b and a["A1"] and b["A1"]):
                continue
            da, dw = b["A1"] - a["A1"], b["W1"] - a["W1"]
            r1h[f"{a_}->{b_}/{inp}"] = {"dA1": da, "pctA1": pct(b["A1"], a["A1"]),
                                        "dW1": dw, "pctW1": pct(b["W1"], a["W1"])}
            print(f"   {a_ + ' -> ' + b_:22s} {inp:11s} {da:10.3f} "
                  f"{pct(b['A1'], a['A1']):8.3f}% {dw:12.3f} "
                  f"{pct(b['W1'], a['W1']):8.3f}%")

    print("\n3. CROSS-LANGUAGE, BOTH C COLUMNS "
          "(statistic / input / O3 isolated / base named per column)")
    print(f"   {'rust cell':12s} {'input':11s} "
          f"{'A1 v gcc-h':>12s} {'A1 v clang-h':>13s} "
          f"{'W1 v gcc-h':>12s} {'W1 v clang-h':>13s}")
    cross = {}
    for inp in INPUTS:
        for rc in RUST:
            r = rows.get(f"{rc}/{inp}")
            g, c = rows.get(f"c-gcc-h/{inp}"), rows.get(f"c-clang-h/{inp}")
            if not (r and g and c and r["A1"] and g["A1"] and c["A1"]):
                continue
            e = {"A1_vs_gcc": pct(r["A1"], g["A1"]),
                 "A1_vs_clang": pct(r["A1"], c["A1"]),
                 "W1_vs_gcc": pct(r["W1"], g["W1"]),
                 "W1_vs_clang": pct(r["W1"], c["W1"])}
            cross[f"{rc}/{inp}"] = e
            print(f"   {rc:12s} {inp:11s} {e['A1_vs_gcc']:11.3f}% "
                  f"{e['A1_vs_clang']:12.3f}% {e['W1_vs_gcc']:11.3f}% "
                  f"{e['W1_vs_clang']:12.3f}%")

    print("\n4. THE LADDER, A1, O3/isolated (base named per column)")
    ladder = {}
    for inp in INPUTS:
        seq = [(n, rows.get(f"{n}/{inp}")) for n in RUST]
        if not all(r and r["A1"] for _n, r in seq):
            continue
        for (an, a), (bn, b) in zip(seq, seq[1:]):
            ladder[f"{an}->{bn}/{inp}"] = {"dA1": b["A1"] - a["A1"],
                                           "pctA1": pct(b["A1"], a["A1"])}
            print(f"   {an + ' -> ' + bn:26s} {inp:11s} "
                  f"{b['A1'] - a['A1']:10.3f} Ir/call  "
                  f"{pct(b['A1'], a['A1']):8.3f}%  (base = {an})")

    problems.extend(statistic_problems(rows))
    out = {"rows": rows, "spreads": spreads, "r1h": r1h, "cross": cross,
           "ladder": ladder, "repeats": args.repeats, "problems": problems}
    out.update(_pin.pin(
        ['c/kernel.c', 'c/kernel_hardened.c', 'c/main.c', 'safe_naive.rs',
         'safe_tuned.rs', 'unsafe.rs', 'verus.rs', 'inputs/small.bin',
         'inputs/large.bin', 'controls/statistic.py'],
        'python3 harness-php/gate.py --tool build ph56-fetchmode-arith --all && '
        'python3 patterns-php/ph56-fetchmode-arith/controls/statistic.py',
        'every rung SOURCE (the binaries are rebuilt from them), c/main.c (the '
        'driver loop is inside W1), the two probe inputs, and this script. '
        'NOT spec.md and NOT NOTES.md: no number here is derived from either.'))
    dst = os.path.join(HERE, "statistic.json")
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
