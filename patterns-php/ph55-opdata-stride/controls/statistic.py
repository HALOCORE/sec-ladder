#!/usr/bin/env python3
"""ph55 control -- **WHICH STATISTIC RESOLVES THIS ROW, AND A1 IS BLIND TO ITS
OWN DEFECT SITE.**

    python3 patterns-php/ph55-opdata-stride/controls/statistic.py
    python3 patterns-php/ph55-opdata-stride/controls/statistic.py --selftest
    python3 patterns-php/ph55-opdata-stride/controls/statistic.py --repeats 3

Produces `../NOTES.md` §8a's `inside_share` matrix, §8b's R1-vs-R1h table in
BOTH families, §8d's cross-language table with BOTH C columns, and §8h's
gcc-vs-clang gap. Writes `statistic.json` beside itself.

⭐⭐⭐ **THE TWO THINGS IT MEASURED THAT THE ROW DID NOT EXPECT.**

1. **`inside_share` is 74-83 % on the C cells and 96-99 % on the Rust cells**,
   and the cause is the row's own mechanism: in C the handlers are reached
   THROUGH A FUNCTION POINTER, so they cannot be inlined and each is its own
   symbol, and `kernel_exclusive_ir` never sees them. `TASK_PHP_048` §2.7's
   guess -- *"inside_share should be high on every cell"* -- is refuted for C.
2. ⛔ **A1 reports the upstream fix at EXACTLY `0.000 %` on every C cell**,
   because `c/kernel.c` and `c/kernel_hardened.c` compile to a BYTE-IDENTICAL
   `kernel` symbol -- the three-line fix lives in
   `ph55_binary_assign_op_helper`, a callee. One of the two binaries SEGVs on
   `inputs/adversarial-nullcall.bin` and the other answers. **A1 cannot see the
   difference between a crashing binary and a correct one on this row.**

⚠⚠ **AND THAT IS A LESSON ABOUT THE RULE, NOT ABOUT THIS ROW.** An
`inside_share` of 74-83 % is HIGH, and A1 is still blind, because what matters is
not how much of the cell A sees but whether **THE DIFFERENCE** lands inside it.
`STATISTICS_001.md` §4 says exactly that -- *"the exact flip condition is
geometric ... deciding whether A is safe to publish requires computing the
statistic the rule would let you skip"* -- and this file is a worked instance.
▶ **Do not read a high `inside_share` as a certificate.**

**HOW THE TWO FAMILIES ARE TAKEN.** One callgrind run per (cell, input) yields
both: **A1** is `harness/measure.py::_sum_rows` IMPORTED and never transcribed
(`TASK_PHP_022` §3.2 measured that a transcription is a different function and
produces a plausible wrong number rather than an error); **W1** is
`callgrind_annotate`'s own `PROGRAM TOTALS` line. Callgrind's return code is
checked and so is the presence of the totals line: a probe that CANNOT evaluate
says so rather than returning a figure-shaped `0`.

§H (`PROTOCOL_PHP.md`): the verdict functions are functions so they can be
attacked, and `--selftest` drives them over synthetic cells -- six must-FIRE and
four must-NOT-fire -- because a green run over the shipped tree is no evidence
that any arm CAN fire.
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

BUILD = os.path.join(ROOT, ".temp", "php-scratch", "build", "ph55")
SCRATCH = os.path.join(ROOT, ".temp", "php55-stat")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

_TOTAL = re.compile(r"^([\d,]+)\s.*PROGRAM TOTALS")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
INPUTS = ["small.bin", "large.bin"]

#: The C bases every cross-language figure owes BOTH of -- F108, and two
#: published claims in the authoritative layer changed SIGN between them.
C_BASES = ["c-gcc-h", "c-clang-h"]
RUST = ["safe_naive", "safe_tuned", "unsafe", "verus"]

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
    """`(A1, W1, inside_share, error_or_None)` from ONE callgrind run."""
    exe = os.path.join(BUILD, f"{cell}-O3-isolated")
    if not os.path.exists(exe):
        return None, None, None, (
            f"{cell}: no binary at {exe} -- run "
            f"`python3 harness-php/gate.py --tool build ph55-opdata-stride --all`")
    M = load_measure()
    out = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out,
                        exe, os.path.join(PDIR, "inputs", inp)],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        if os.path.exists(out):
            os.unlink(out)
        return None, None, None, f"callgrind exit {r.returncode} on {tag}: {r.stderr[-200:]}"
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
                               f"line for {tag} -- W1 cannot be computed and must "
                               f"not be reported as 0")
    n = n_iters(inp)
    return k / n, wp / n, k / wp, None


def pct(new, base):
    return None if not base else (new - base) / base * 100.0


# ---- the verdicts, factored so they can be ATTACKED -------------------------

def statistic_problems(rows):
    """The claims `../NOTES.md` §8 makes, as a function of the measured cells.

    1. every cell must have BOTH families. A cell with `A1` and no `W1` cannot
       have an `inside_share` and must not be tabulated as if it did.
    2. `inside_share` must be in `(0, 1]`. Outside that the two families are not
       nested scopes of one run and the whole table is meaningless.
    3. ⭐ if `|Δinside_share|` between a C base and a Rust cell exceeds 0.02,
       the cross-language column MAY NOT be published in A1
       (`STATISTICS_001.md` §1's condition). This row exceeds it, so the
       requirement is that the row SAYS SO -- and this arm is what would fire if
       a future edit quietly narrowed the gap and left §8d claiming it had to
       use W1.
    4. ⛔ the R1-vs-R1h A1 delta must be EXACTLY zero on every C cell, or §8b's
       blindness claim has stopped being true and the section is wrong.
    5. ⭐ at least one cross-language cell must CHANGE SIGN between `c-gcc-h`
       and `c-clang-h`, or §8d's F108 headline is unsupported on this row.
    6. W1 must be strictly greater than A1 in every cell -- the whole program
       cannot cost less than one of its symbols.
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
            p.append(f"6. {key}: W1 {r['W1']} < A1 {r['A1']} -- the whole program "
                     f"cannot cost less than one of its symbols")
    for inp in INPUTS:
        for base in C_BASES:
            b = rows.get(f"{base}/{inp}")
            for rc in RUST:
                r = rows.get(f"{rc}/{inp}")
                if not (b and r and b.get("inside_share") and r.get("inside_share")):
                    continue
                d = abs(b["inside_share"] - r["inside_share"])
                if d <= 0.02:
                    p.append(
                        f"3. {rc} vs {base} on {inp}: |Δinside_share| = {d:.4f} <= 0.02, "
                        f"so STATISTICS_001 §1's condition is now SATISFIED and "
                        f"../NOTES.md §8d's reason for publishing the "
                        f"cross-language column in W1 has gone stale")
    for inp in INPUTS:
        for r1, r1h in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            a, b = rows.get(f"{r1}/{inp}"), rows.get(f"{r1h}/{inp}")
            if a and b and a.get("A1") is not None and b.get("A1") is not None:
                if a["A1"] != b["A1"]:
                    p.append(
                        f"4. {r1} vs {r1h} on {inp}: A1 {a['A1']} != {b['A1']}. "
                        f"§8b claims A1 is BLIND to this row's fix because the "
                        f"`kernel` symbol is byte-identical; it is not any more")
    flips = 0
    for inp in INPUTS:
        for rc in RUST:
            r = rows.get(f"{rc}/{inp}")
            g, c = rows.get(f"c-gcc-h/{inp}"), rows.get(f"c-clang-h/{inp}")
            if not (r and g and c) or r.get("W1") is None:
                continue
            a, b = pct(r["W1"], g["W1"]), pct(r["W1"], c["W1"])
            if a is not None and b is not None and (a < 0) != (b < 0):
                flips += 1
    if flips == 0:
        p.append("5. NO cross-language cell changes sign between c-gcc-h and "
                 "c-clang-h, so ../NOTES.md §8d's F108 headline is not supported "
                 "by this row's own numbers")
    return p


def selftest():
    """⛔ The arms above over SYNTHETIC cells. Six must FIRE, four must not."""
    def cell(a1, w1):
        return {"A1": a1, "W1": w1, "inside_share": a1 / w1, "error": None}

    # a shape with the shipped properties: low C share, high Rust share, A1
    # identical across the fix, and one sign flip.
    good = {}
    for inp in INPUTS:
        good[f"c-gcc/{inp}"] = cell(1553.0, 1900.0)
        good[f"c-gcc-h/{inp}"] = cell(1553.0, 1880.0)
        good[f"c-clang/{inp}"] = cell(1340.0, 1759.0)
        good[f"c-clang-h/{inp}"] = cell(1340.0, 1759.0)
        good[f"safe_naive/{inp}"] = cell(1950.0, 2017.0)
        good[f"safe_tuned/{inp}"] = cell(1695.0, 1763.0)   # -6.2% vs gcc, +0.2% vs clang
        good[f"unsafe/{inp}"] = cell(1576.0, 1644.0)
        good[f"verus/{inp}"] = cell(1577.0, 1645.0)

    bad = []
    cases = []
    # N1 a missing family
    t = dict(good); t["unsafe/small.bin"] = {"A1": 1.0, "W1": None,
                                             "inside_share": None, "error": None}
    cases.append(("N1 a cell with no W1", t, True, "1."))
    # N2 an error string
    t = dict(good); t["verus/large.bin"] = {"A1": None, "W1": None,
                                            "inside_share": None,
                                            "error": "no binary"}
    cases.append(("N2 a cell that could not be measured", t, True, "1."))
    # N3 an impossible share
    t = dict(good); t["unsafe/large.bin"] = {"A1": 10.0, "W1": 5.0,
                                             "inside_share": 2.0, "error": None}
    cases.append(("N3 inside_share > 1", t, True, "2."))
    # N4 the shares converge -> the W1 justification goes stale
    # ⚠ N4 has to keep arm 4 satisfied while moving arm 3, or it fires on the
    # wrong arm and the selftest is testing nothing it means to. The R1 and R1h
    # A1 values must stay EQUAL while the shares converge.
    t = dict(good)
    for inp in INPUTS:
        t[f"c-gcc/{inp}"] = cell(1815.0, 1880.0)      # share 0.9654
        t[f"c-gcc-h/{inp}"] = cell(1815.0, 1880.0)
        t[f"c-clang/{inp}"] = cell(1698.0, 1759.0)    # share 0.9653
        t[f"c-clang-h/{inp}"] = cell(1698.0, 1759.0)
    cases.append(("N4 the C and Rust shares converge", t, True, "3."))
    # N5 the fix becomes visible to A1
    t = dict(good)
    for inp in INPUTS:
        t[f"c-gcc-h/{inp}"] = cell(1560.0, 1880.0)
    cases.append(("N5 A1 stops being blind to the fix", t, True, "4."))
    # N6 no sign flip anywhere
    t = dict(good)
    for inp in INPUTS:
        t[f"safe_tuned/{inp}"] = cell(1695.0, 1500.0)
    cases.append(("N6 no cross-language sign flip", t, True, "5."))
    # P1..P4 must NOT fire
    cases.append(("P1 the shipped shape", good, False, None))
    t = dict(good)
    for inp in INPUTS:
        t[f"safe_naive/{inp}"] = cell(3000.0, 3100.0)
    cases.append(("P2 a much dearer safe rung, same signs", t, False, None))
    t = dict(good)
    for inp in INPUTS:
        t[f"c-clang/{inp}"] = cell(1340.0, 1700.0)
    cases.append(("P3 the clang R1/R1h W1 gap widens (A1 still equal)", t, False, None))
    t = {k: dict(v) for k, v in good.items()}
    for inp in INPUTS:
        t[f"verus/{inp}"] = cell(1577.0, 1646.0)
    cases.append(("P4 R5 a hair dearer than R4", t, False, None))

    for label, rows, must_fire, arm in cases:
        got = statistic_problems(rows)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got[:2]})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repeats", type=int, default=1,
                    help="callgrind repeats per cell; 3 reproduces ../NOTES.md "
                         "§8b's within-build stability claim")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARMS, ATTACKED OVER SYNTHETIC CELLS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"10 arms (6 must-FIRE, 4 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    rows, spreads = {}, {}
    print(f"\n1. A1, W1 AND inside_share -- one callgrind run per cell, "
          f"{args.repeats} repeat(s)")
    print(f"   {'cell':12s} {'input':11s} {'A1 Ir/call':>12s} {'W1 Ir/call':>12s} "
          f"{'inside':>8s} {'spread':>8s}")
    for inp in INPUTS:
        for cell in CELLS:
            vals = []
            err = None
            for i in range(args.repeats):
                a, w, s, e = measure(cell, inp, f"{cell}.{inp}.{i}")
                if e:
                    err = e
                    break
                vals.append((a, w, s))
            key = f"{cell}/{inp}"
            if err or not vals:
                rows[key] = {"A1": None, "W1": None, "inside_share": None, "error": err}
                print(f"   {cell:12s} {inp:11s} {'--':>12s} {'--':>12s} "
                      f"{'--':>8s} {'--':>8s}   {err}")
                continue
            a, w, s = vals[0]
            sp = max(v[1] for v in vals) - min(v[1] for v in vals)
            spreads[key] = sp
            rows[key] = {"A1": a, "W1": w, "inside_share": s, "error": None}
            print(f"   {cell:12s} {inp:11s} {a:12.3f} {w:12.3f} "
                  f"{s * 100:7.2f}% {sp:8.3f}")

    print("\n2. ⛔ R1 vs R1h -- A1 IS BLIND, W1 IS NOT (the fix is in a CALLEE)")
    for inp in INPUTS:
        for r1, r1h in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            a, b = rows.get(f"{r1}/{inp}"), rows.get(f"{r1h}/{inp}")
            if not (a and b and a["A1"] is not None and b["A1"] is not None):
                continue
            print(f"   {inp:11s} {r1:10s} -> {r1h:10s}   "
                  f"A1 {a['A1']:9.3f} -> {b['A1']:9.3f} = {pct(b['A1'], a['A1']):+8.4f} %   "
                  f"W1 {a['W1']:9.3f} -> {b['W1']:9.3f} = {pct(b['W1'], a['W1']):+8.4f} %")

    print("\n3. CROSS-LANGUAGE, W1, AND **BOTH** C COLUMNS (F108)")
    for inp in INPUTS:
        print(f"   -- {inp}")
        for rc in RUST:
            r = rows.get(f"{rc}/{inp}")
            g, c = rows.get(f"c-gcc-h/{inp}"), rows.get(f"c-clang-h/{inp}")
            if not (r and g and c) or r["W1"] is None:
                continue
            pg, pc_ = pct(r["W1"], g["W1"]), pct(r["W1"], c["W1"])
            flip = "  <-- CHANGES SIGN" if (pg < 0) != (pc_ < 0) else ""
            print(f"      {rc:12s} W1 {r['W1']:9.3f}   vs c-gcc-h {pg:+8.2f} %   "
                  f"vs c-clang-h {pc_:+8.2f} %{flip}")
            pg, pc_ = pct(r["A1"], g["A1"]), pct(r["A1"], c["A1"])
            print(f"      {'':12s} A1 {r['A1']:9.3f}   vs c-gcc-h {pg:+8.2f} %   "
                  f"vs c-clang-h {pc_:+8.2f} %   [A1 is the BLIND column here]")

    print("\n4. SAME-LANGUAGE, A1 (inside_share 96-99 %, |Δ| < 0.01)")
    for inp in INPUTS:
        s = {k: rows.get(f"{k}/{inp}") for k in RUST}
        if not all(s.values()) or any(v["A1"] is None for v in s.values()):
            continue
        print(f"   {inp:11s} R2->R3 {pct(s['safe_tuned']['A1'], s['safe_naive']['A1']):+7.2f} %"
              f"   fixed-R4 bound (R3-R4) "
              f"{pct(s['safe_tuned']['A1'], s['unsafe']['A1']):+7.2f} %"
              f"   R4->R5 {pct(s['verus']['A1'], s['unsafe']['A1']):+7.3f} %")

    print("\n5. gcc vs clang ON IDENTICAL EXTRACTED C (W1)")
    for inp in INPUTS:
        g, c = rows.get(f"c-gcc/{inp}"), rows.get(f"c-clang/{inp}")
        if g and c and g["W1"]:
            print(f"   {inp:11s} gcc {g['W1']:9.3f}  clang {c['W1']:9.3f}  "
                  f"clang vs gcc {pct(c['W1'], g['W1']):+7.2f} %")

    problems.extend(statistic_problems(rows))
    out = {"rows": rows, "w1_spread": spreads, "repeats": args.repeats,
           "problems": problems}
    dst = os.path.join(HERE, "statistic.json")
    out.update(_pin.pin(
        ['c/kernel.c', 'c/kernel_hardened.c', 'c/main.c', 'safe_naive.rs', 'safe_tuned.rs', 'unsafe.rs', 'verus.rs', 'inputs/gen.py', 'controls/statistic.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/statistic.py --repeats 3',
        'every source that reaches one of the eight measured cells, plus inputs/gen.py and this script. It does NOT pin the BINARIES under .temp/php-scratch/: those are gitignored and re-derivable, and the pin is on what produces them.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
