#!/usr/bin/env python3
# =============================================================================
# identity_null.py -- THE MEASUREMENT BEHIND F82
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/mgr172/`, which is GITIGNORED, and **F82 is PUBLISHED** --
# `RECAP_PHP.md`'s finding list carries it (*"F74's null control had an
# UNCHECKED PREMISE ... a null control is ONE-SIDED and family A's SENSITIVITY
# is now measured"*) and `.memory-php/` cites it. ▶ A PUBLISHED FINDING WHOSE
# ONLY EVIDENCE IS A GITIGNORED PROBE IS A FINDING THAT WILL NOT SURVIVE A
# CLEAN CHECKOUT. That is `.memory-php/04-process.md` LAW 11, and it is the
# same call already made for `width.py` (F92), `probes/item125_extract.py` and
# `probes/ph66_djbx33a_collide.py`.
#
# RUN IT:  python3 .tasks-php/probes/identity_null.py --selftest   # the negatives
#          python3 .tasks-php/probes/identity_null.py              # the report
#
# ✅ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered:
# ⭐ NOTHING. Every number it prints is re-derived from `results-php/<row>.json`,
# `results-php/gate/<row>.json`, `results/<row>.json`, `results/gate/<row>.json`
# and `patterns/p25-realloc-growth/spec.md` -- all committed. It builds nothing,
# runs no binary, touches no `.temp/` path and WRITES NOTHING. So on a clean
# checkout it runs to completion and F82 is re-derivable in 0.12 s.
# ⚠ Its sibling probes are NOT in that position: `inclusive_ir.py` and
# `bc_sweep.py` need gitignored callgrind profiles and gitignored build trees,
# and each says so in its own header.
#
# WHAT IT FOUND (F82): the premise `identity: unsafe == verus, O3 exact` --
# which is what makes `verus - unsafe` a KNOWN TRUE ZERO and therefore a null
# control -- was asserted for all 39 rows and **is false on 7 of 40**
# (`ph07` norel, `ph45`/`ph64` differ; PAT `p25` `p28` `p29` `p34` `p36`).
# ⭐ N6 is the arm that earns its keep: it reads the level out of the GATE
# RECORD and asserts the trap that forced that choice -- `p25`'s `spec.md`
# carries BOTH the boilerplate string `identity: unsafe == verus, O3 exact`
# AND its real pin `` `O3: norel` ``, so a script that grepped `spec.md` would
# have called `p25` a null.
# =============================================================================

"""Does the R4/R5 NULL CONTROL exist on every row it was computed over?

F74 settled item 52 by a null control: `identity` pins R4 and R5 byte-identical,
so `verus - unsafe` has a KNOWN TRUE VALUE OF 0, and a statistic reading nonzero
there is reading noise. Family A read 0.000 % on all 39 rows; family B reached
+3.65 % (PHP) and +5.01 % (PAT). Family A won.

⚠⚠ THE PREMISE IS PER-ROW AND `.tasks-php/probes/null_control.py` NEVER CHECKED
IT (that probe was `.temp/mgr170/null_control.py` when this line was written; it
is promoted alongside this file and the citation is updated, not rewritten).
`results*/gate/<row>.json .identity` records the MEASURED level per (pair, opt),
and at `O3` the `unsafe vs verus` level is `exact` on SOME rows only:

    PHP   ph03 ph16 ph29 exact  |  ph07 norel · ph45 differ · ph64 differ
    PAT   23 of 28 exact        |  p25 p28 p29 p34 p36 norel

On a row pinned `norel`/`differ` the two kernels are DIFFERENT MACHINE CODE, so
`verus - unsafe` there has no known true value and is not a null in any mode.

⚠⚠⚠ AND THE DIRECTION OF THE ERROR IS NOT OBVIOUS -- WHICH IS WHY THIS RUNS.
Two readings are possible and they point OPPOSITE WAYS:

  (i)  the null set was DILUTED. Family B's worst cells sit on non-null rows, so
       B's real null is smaller than published and F74 over-stated its case.
  (ii) family A is BLIND. If R4 and R5 differ by a measurable number of kernel
       instructions and family A still reads 0.000 %, then A is not accurate on
       those rows, it is INSENSITIVE -- and 0.000 % across "all 39 rows" is
       evidence AGAINST A, not for it.

Both are checkable from the record and this script refuses to assume either.

`harness/check.py`'s own null docstring corrects its table for MODE ("a null
control is only a null in the MODE ITS IDENTITY PIN COVERS"), for OPT LEVEL
(`p28 1732.73` and `p29 425.80` were `-O0` cells under an `-O3` heading) and for
INPUT ("on `small.bin` p25's and p42's nulls are `0.00`"). It does not correct
for the IDENTITY LEVEL, and its worst quoted cell -- `p25 large +269.52` -- is on
a row whose own `spec.md` pins `O0: norel`, `O3: norel`. ⚠ That is REPORTED FOR
ROUTING, NOT FIXED: `harness/` is frozen (`CLAUDE.md`), and p25 rescues the
premise by a DIFFERENT route its own identity note records -- identical
instruction count (189 non-pad at `-O3`), identical byte count, identical
`md5_norm`. So on p25 the null is real and the JUSTIFICATION for it is wrong.

⚠ The PHP rows are not rescued that way: `ph45`'s O3 counts are
`[313, 308, 1433]` against `[311, 306, 1417]` -- the counts THEMSELVES differ.

Run:  python3 .tasks-php/probes/identity_null.py --selftest
      python3 .tasks-php/probes/identity_null.py
"""
import json
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The identity levels that make `verus - unsafe` a TRUE ZERO. `exact` is
# byte-identical. `multiset` is the same instructions in a different order,
# which preserves the executed count, so it is also a null for a COUNT
# statistic -- recorded here to be explicit rather than to be permissive; no
# row in either programme currently measures `multiset` on this pair.
NULL_LEVELS = ("exact", "multiset")


def load(path):
    with open(path) as fh:
        return json.load(fh)


def identity_level(gate, opt):
    """Measured `unsafe vs verus` level at `opt`, or None if no such entry."""
    for e in gate.get("identity") or []:
        if e.get("opt") != opt:
            continue
        pair = str(e.get("pair", ""))
        if "unsafe" in pair and "verus" in pair:
            return e.get("level"), e.get("expected"), e
    return None, None, None


def static_counts(gate, opt):
    """(counts_unsafe, counts_verus) from the identity entry, or (None, None).

    `counts_*` is `[n_raw, n_nopad, n_bytes]` as `check_identity` writes it.
    """
    _, _, e = identity_level(gate, opt)
    if e is None:
        return None, None
    return e.get("counts_a"), e.get("counts_b")


def cell_of(meas, cellname, opt, mode):
    for c in meas.get("cells") or []:
        if c.get("cell") == cellname and c.get("opt") == opt and c.get("mode") == mode:
            return c
    return None


def family_a(meas, cellname, opt, mode, inp):
    """kernel_exclusive_ir -- family A, the raw total (not yet per call)."""
    c = cell_of(meas, cellname, opt, mode)
    if c is None:
        return None
    ir = (c.get("ir") or {}).get(inp)
    if not ir:
        return None
    return ir.get("kernel_exclusive_ir")


def family_b(gate, cellname, opt, mode, inp):
    """marginal_ir_per_call -- family B, a whole-program slope."""
    key = f"{cellname}/{opt}/{mode}/{inp}"
    return (gate.get("marginal_ir_per_call") or {}).get(key)


def rows():
    out = []
    for gate_glob, meas_dir, prog in (
        ("results-php/gate/ph*.json", "results-php", "PHP"),
        ("results/gate/p*.json", "results", "PAT"),
    ):
        for gp in sorted(glob.glob(os.path.join(ROOT, gate_glob))):
            name = os.path.basename(gp)[:-5]
            mp = os.path.join(ROOT, meas_dir, name + ".json")
            if not os.path.exists(mp):
                continue
            out.append((prog, name, load(gp), load(mp)))
    return out


# --------------------------------------------------------------------------
# §1  which rows have a null at all
# --------------------------------------------------------------------------

def report_levels(data):
    print("=" * 78)
    print("§1  IS `verus - unsafe` A NULL ON THIS ROW?  (measured level, per opt)")
    print("=" * 78)
    print(f"{'prog':5s} {'row':32s} {'O0':10s} {'O3':10s} {'null at O3?'}")
    tally = {"PHP": [0, 0], "PAT": [0, 0]}
    for prog, name, gate, _ in data:
        l0, _, _ = identity_level(gate, "O0")
        l3, _, _ = identity_level(gate, "O3")
        isnull = l3 in NULL_LEVELS
        tally[prog][0 if isnull else 1] += 1
        mark = "yes" if isnull else "⚠ NO"
        print(f"{prog:5s} {name:32s} {str(l0):10s} {str(l3):10s} {mark}")
    print()
    for prog in ("PHP", "PAT"):
        y, n = tally[prog]
        print(f"  {prog}: level == exact at O3 on {y} rows, NOT exact on {n}")

    # §1b ⚠⚠ THE LEVEL IS THE WRONG PREDICATE, AND USING IT WOULD HAVE LOOKED
    # RIGHT. `exact` is BYTE-identity. A count statistic needs only that the
    # EXECUTED INSTRUCTION COUNT agree, and `norel` covers two different
    # situations: same instructions at different rip-relative displacements
    # (p25's and ph07's own identity notes say so in terms -- "both resolving to
    # the same absolute address"; "251 instructions and 953 bytes in BOTH
    # cells") AND genuinely different code. Only the second breaks the null.
    print()
    print("-" * 78)
    print("§1b THE CORRECT PREDICATE IS Δnopad == 0, NOT level == 'exact'")
    print("-" * 78)
    t2 = {"PHP": [0, 0, 0], "PAT": [0, 0, 0]}
    rescued = []
    for prog, name, gate, _ in data:
        l3, _, _ = identity_level(gate, "O3")
        ca, cb = static_counts(gate, "O3")
        if l3 in NULL_LEVELS:
            t2[prog][0] += 1
            continue
        if ca and cb and cb[1] == ca[1] and cb[2] == ca[2]:
            t2[prog][1] += 1
            rescued.append((prog, name, l3))
        else:
            t2[prog][2] += 1
    for prog in ("PHP", "PAT"):
        ex, resc, real = t2[prog]
        print(f"  {prog}: {ex} exact · {resc} not-exact BUT Δnopad==0 and "
              f"Δbytes==0 (STILL A NULL) · {real} genuinely NOT a null")
    print()
    print("  rows the LEVEL excludes and Δnopad KEEPS -- these are the cells a")
    print("  level-based restriction would have thrown away:")
    for prog, name, l3 in rescued:
        print(f"      {prog} {name}  (level {l3})")
    return tally


# --------------------------------------------------------------------------
# §2  reading (ii): is family A BLIND where the code really differs?
# --------------------------------------------------------------------------

def report_blindness(data):
    print()
    print("=" * 78)
    print("§2  READING (ii): WHERE R4 AND R5 ARE DIFFERENT CODE, DOES A SEE IT?")
    print("=" * 78)
    print("    static Δ is from the identity entry's own `counts_a`/`counts_b`")
    print("    (`[n_raw, n_nopad, n_bytes]`), so it is what the GATE measured.")
    print()
    hdr = (f"{'prog':5s} {'row':32s} {'Δnopad':>7s} {'Δbytes':>7s} "
           f"{'input':10s} {'A: unsafe':>14s} {'A: verus':>14s} {'A Δ%':>9s}")
    print(hdr)
    blind = []
    for prog, name, gate, meas in data:
        l3, _, _ = identity_level(gate, "O3")
        if l3 in NULL_LEVELS:
            continue
        ca, cb = static_counts(gate, "O3")
        if not ca or not cb:
            print(f"{prog:5s} {name:32s}  -- no counts in identity entry --")
            continue
        dnopad = cb[1] - ca[1]
        dbytes = cb[2] - ca[2]
        for inp in sorted((meas.get("inputs") or {})) or ["small.bin"]:
            a_u = family_a(meas, "unsafe", "O3", "isolated", inp)
            a_v = family_a(meas, "verus", "O3", "isolated", inp)
            if a_u is None or a_v is None:
                continue
            pct = 100.0 * (a_v - a_u) / a_u if a_u else float("nan")
            print(f"{prog:5s} {name:32s} {dnopad:+7d} {dbytes:+7d} "
                  f"{inp:10s} {a_u:14d} {a_v:14d} {pct:+9.4f}")
            if dnopad != 0 and a_v == a_u:
                blind.append((prog, name, inp, dnopad))
    print()
    if blind:
        print(f"  ⚠ FAMILY A READS EXACTLY ZERO ON {len(blind)} CELL(S) WHOSE "
              f"KERNELS DIFFER IN STATIC INSTRUCTION COUNT:")
        for prog, name, inp, d in blind:
            print(f"        {prog} {name} {inp}  static Δnopad = {d:+d}")
        print()
        print("    ⚠⚠ THIS IS NOT YET READING (ii), AND SAYING SO WOULD BE THE")
        print("    ERROR THIS SCRIPT EXISTS TO AVOID. A STATIC count difference on")
        print("    a path the benign corpus never executes -- a panic landing pad,")
        print("    a cold overflow arm -- gives family A a CORRECT zero: the")
        print("    executed work really is identical. A flat zero is blindness only")
        print("    if the differing instructions are REACHED. ▶ Disassemble the two")
        print("    kernels and locate the delta before drawing either conclusion.")
    else:
        print("  ✅ Family A does NOT read a flat zero on any differing-code cell.")
        print("     Reading (ii) is REFUTED: A's 0.000 % on the null rows is not")
        print("     the same number it prints when the code genuinely differs.")
    return blind


# --------------------------------------------------------------------------
# §3  reading (i): does restricting to true nulls move either family's worst?
# --------------------------------------------------------------------------

def report_worst(data):
    print()
    print("=" * 78)
    print("§3  READING (i): THE WORST NULL, BEFORE AND AFTER THE RESTRICTION")
    print("=" * 78)
    print("    O3/isolated only -- the column corrections are published in, and")
    print("    the only mode `check_identity` compares digests in.")
    print()
    out = {}
    for prog in ("PHP", "PAT"):
        for fam, getter in (("A  kernel_exclusive_ir", "a"), ("B  marginal_ir_per_call", "b")):
            allrows, nullrows = [], []
            for p, name, gate, meas in data:
                if p != prog:
                    continue
                l3, _, _ = identity_level(gate, "O3")
                for inp in sorted((meas.get("inputs") or {})) or ["small.bin"]:
                    if getter == "a":
                        u = family_a(meas, "unsafe", "O3", "isolated", inp)
                        v = family_a(meas, "verus", "O3", "isolated", inp)
                    else:
                        u = family_b(gate, "unsafe", "O3", "isolated", inp)
                        v = family_b(gate, "verus", "O3", "isolated", inp)
                    if u is None or v is None or not u:
                        continue
                    pct = 100.0 * (v - u) / u
                    allrows.append((abs(pct), pct, name, inp))
                    if l3 in NULL_LEVELS:
                        nullrows.append((abs(pct), pct, name, inp))
            for label, bucket in (("all rows", allrows), ("TRUE NULLS only", nullrows)):
                if not bucket:
                    print(f"  {prog} {fam:26s} {label:16s} -- no cells --")
                    continue
                bucket.sort(reverse=True)
                _, pct, name, inp = bucket[0]
                print(f"  {prog} {fam:26s} {label:16s} worst {pct:+9.4f} %  "
                      f"({name} {inp})  n={len(bucket)}")
                out[(prog, getter, label)] = (pct, name, inp, len(bucket))
        print()
    return out


# --------------------------------------------------------------------------
# §4  the half F74 NEVER MEASURED: is family A SENSITIVE?
# --------------------------------------------------------------------------
#
# A null control is one-sided. It shows a statistic does not read noise; it
# cannot show the statistic reads SIGNAL. A statistic hard-wired to 0 would ace
# every null in the tree. ⚠⚠ F74 published family A on the strength of the null
# ALONE, and that argument would have been just as persuasive for a constant.
#
# The rows where identity does NOT pin R4 to R5 supply the missing side for
# free: there the two kernels differ by a KNOWN static instruction count, so
# family A has a PREDICTED nonzero value --
#
#     predicted Δ(kernel_exclusive_ir) = Δnopad × (calls on which it executes)
#
# and `calls` is bounded above by `n_iters`, which is read from a DIFFERENT
# field of a DIFFERENT file than Δ. Nothing here is fitted.

def report_sensitivity(data):
    print()
    print("=" * 78)
    print("§4  IS FAMILY A SENSITIVE?  (the half a null control cannot show)")
    print("=" * 78)
    print("    Δ is `kernel_exclusive_ir` (results*/<row>.json); Δnopad is the")
    print("    gate's own `counts_*`; n_iters is `inputs[].n_iters`. Three fields,")
    print("    two files, no fitting. `exec_rate` = Δ / Δnopad / n_iters.")
    print()
    print(f"{'row':32s} {'input':10s} {'Δnopad':>7s} {'Δ(A)':>8s} "
          f"{'n_iters':>8s} {'exec_rate':>10s}")
    seen = []
    for prog, name, gate, meas in data:
        l3, _, _ = identity_level(gate, "O3")
        if l3 in NULL_LEVELS:
            continue
        ca, cb = static_counts(gate, "O3")
        if not ca or not cb:
            continue
        dnopad = cb[1] - ca[1]
        if dnopad == 0:
            continue          # no signal is predicted, so nothing to calibrate
        for inp in sorted((meas.get("inputs") or {})):
            n = ((meas.get("inputs") or {}).get(inp) or {}).get("n_iters")
            a_u = family_a(meas, "unsafe", "O3", "isolated", inp)
            a_v = family_a(meas, "verus", "O3", "isolated", inp)
            if a_u is None or a_v is None or not n:
                continue
            d = a_v - a_u
            rate = d / dnopad / n
            print(f"{name:32s} {inp:10s} {dnopad:+7d} {d:+8d} {n:8d} "
                  f"{rate:10.4f}")
            seen.append((name, inp, dnopad, d, n, rate))
    print()
    exact = [s for s in seen if abs(s[5] - 1.0) < 1e-9]
    frac = [s for s in seen if 0.0 < s[5] < 1.0 - 1e-9]
    for name, inp, dnopad, d, n, rate in exact:
        print(f"  ⭐ {name} {inp}: exec_rate EXACTLY 1.0000 -- the {abs(dnopad)} "
              f"instruction(s) run ONCE PER CALL and A resolves all {abs(d)} "
              f"of them over {n} calls.")
    for name, inp, dnopad, d, n, rate in frac:
        print(f"  ⭐ {name} {inp}: exec_rate {rate:.4f} -- a CONDITIONAL path. "
              f"A reads the fraction, not the bound.")
    print()
    if exact and frac:
        print("  ✅✅ THE FRACTIONAL ROWS ARE THE CONTROL ON THE EXACT ONES.")
        print("     An exec_rate of exactly 1.0 is 'too clean', and too-clean is")
        print("     the only warning F52 gives. If this arithmetic were feeding")
        print("     itself -- if Δ were in any way derived from n_iters -- EVERY")
        print("     row would come out 1.0. They do not: the conditional rows land")
        print("     off 1.0 and AGREE WITH EACH OTHER across inputs of different")
        print("     size, which no self-fulfilling computation would produce.")
        rates = {}
        for name, inp, _, _, _, rate in frac:
            rates.setdefault(name, []).append((inp, rate))
        for name, rs in rates.items():
            if len(rs) > 1:
                spread = max(r for _, r in rs) - min(r for _, r in rs)
                print(f"     {name}: " +
                      " . ".join(f"{i} {r:.4f}" for i, r in sorted(rs)) +
                      f"  spread {spread:.4f}")
    elif not seen:
        print("  ⚠ NO ROW HAS Δnopad != 0 -- family A's SENSITIVITY IS UNTESTED")
        print("    by this tree, and the null control is the only evidence for it.")
    return seen


# --------------------------------------------------------------------------
# selftest -- must-fire negatives. A validator lands with these or it does not
# land (PROTOCOL_PHP §H).
# --------------------------------------------------------------------------

def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST -- must-fire negatives")

    # N1 the level reader must find the pair at all, on a row known to have it.
    g = load(os.path.join(ROOT, "results-php/gate/ph29-recvfrom-alloc.json"))
    l3, exp3, e = identity_level(g, "O3")
    check("N1", l3 == "exact" and e is not None,
          f"ph29 O3 unsafe-vs-verus reads {l3!r} (expected 'exact')")

    # N2 ... and must NOT report `exact` on a row the gate records as differing.
    g45 = load(os.path.join(ROOT, "results-php/gate/ph45-htmlent-cache-int.json"))
    l45, _, _ = identity_level(g45, "O3")
    check("N2", l45 not in NULL_LEVELS,
          f"ph45 O3 reads {l45!r}, which is NOT in NULL_LEVELS -- if this "
          f"passes as a null the whole script is pointless")

    # N3 a pair name that does not exist must yield None, not a silent match on
    #    the first identity entry. This is the bug that would make every row
    #    look `exact`.
    fake = {"identity": [{"pair": "c-gcc vs c-clang", "opt": "O3", "level": "exact"}]}
    l, _, _ = identity_level(fake, "O3")
    check("N3", l is None,
          "a record with only a c-gcc/c-clang pair yields None for unsafe/verus")

    # N4 the opt filter must bite: ph45 differs at BOTH opts, ph03 differs at O0
    #    and is exact at O3, so reading the wrong opt on ph03 flips the verdict.
    g03 = load(os.path.join(ROOT, "results-php/gate/ph03-uudecode-bound.json"))
    l0, _, _ = identity_level(g03, "O0")
    l3b, _, _ = identity_level(g03, "O3")
    check("N4", l0 == "differ" and l3b == "exact",
          f"ph03 reads O0={l0!r} O3={l3b!r} -- the opt filter distinguishes them")

    # N5 family A and family B must come from DIFFERENT files. If a refactor
    #    ever pointed both at one of them the comparison would be vacuous.
    m29 = load(os.path.join(ROOT, "results-php/ph29-recvfrom-alloc.json"))
    a = family_a(m29, "unsafe", "O3", "isolated", "small.bin")
    b = family_b(g, "unsafe", "O3", "isolated", "small.bin")
    check("N5", a is not None and b is not None and a != b,
          f"ph29 A={a} (results-php/) and B={b} (results-php/gate/) are distinct")

    # N6 ⚠ THE F52 CONTROL. Every level in this script is read out of the GATE
    #    RECORD, never out of `spec.md` -- because the two DISAGREE on p25,
    #    whose spec.md contains the literal string `identity: unsafe == verus,
    #    O3 exact` (shared-block boilerplate) while its own pin, in a table row,
    #    is `O0: norel`, `O3: norel`. A script that grepped spec.md would call
    #    p25 a null. Assert the trap is real so nobody re-introduces it.
    p25spec = os.path.join(ROOT, "patterns/p25-realloc-growth/spec.md")
    with open(p25spec, "rb") as fh:
        raw = fh.read().decode("utf-8", "replace")
    g25 = load(os.path.join(ROOT, "results/gate/p25-realloc-growth.json"))
    l25, _, _ = identity_level(g25, "O3")
    check("N6", ("identity: unsafe == verus, O3 exact" in raw
                 and "`O3: norel`" in raw and l25 == "norel"),
          "p25's spec.md carries BOTH the boilerplate 'O3 exact' string and its "
          f"real pin '`O3: norel`'; the gate measures {l25!r}. Grepping spec.md "
          "for the level is the trap this script avoids by reading the record")

    # N7 the blindness test must be capable of firing. Feed it a synthetic row
    #    whose counts differ and whose family-A numbers are equal.
    synth_gate = {"identity": [{"pair": "unsafe vs verus", "opt": "O3",
                                "level": "differ", "expected": "differ",
                                "counts_a": [10, 10, 40], "counts_b": [12, 12, 48]}]}
    synth_meas = {"inputs": {"x.bin": {}}, "cells": [
        {"cell": "unsafe", "opt": "O3", "mode": "isolated",
         "ir": {"x.bin": {"kernel_exclusive_ir": 1000}}},
        {"cell": "verus", "opt": "O3", "mode": "isolated",
         "ir": {"x.bin": {"kernel_exclusive_ir": 1000}}}]}
    hits = report_blindness([("SYN", "synthetic-blind", synth_gate, synth_meas)])
    check("N7", len(hits) == 1,
          f"a synthetic row with Δnopad=+2 and equal A values yields "
          f"{len(hits)} blindness hit(s) (expected 1)")

    # N8 ⚠⚠ THE SENSITIVITY CONTROL'S OWN CONTROL. §4's argument is that a
    #    fractional exec_rate proves the arithmetic is not self-fulfilling. That
    #    argument is only worth something if a fractional rate is REACHABLE by
    #    this code path -- so assert the tree actually contains one, and that it
    #    is not manufactured by a division that cannot return anything else.
    seen = report_sensitivity(rows())
    exact = [s for s in seen if abs(s[5] - 1.0) < 1e-9]
    frac = [s for s in seen if 0.0 < s[5] < 1.0 - 1e-9]
    check("N8", len(exact) >= 1 and len(frac) >= 1,
          f"the tree supplies BOTH exec_rate == 1.0 ({len(exact)} cells) and "
          f"exec_rate < 1.0 ({len(frac)} cells); if only the first existed, §4's "
          f"too-clean control would be untestable and §4 would prove nothing")

    # N9 and the fractional rates must AGREE ACROSS INPUTS. A conditional path
    #    taken at a stable rate is a fact about the kernel; two inputs of
    #    different size agreeing is the evidence. Disagreement would mean the
    #    rate is an artefact of one input's shape.
    byrow = {}
    for name, inp, _, _, _, rate in frac:
        byrow.setdefault(name, []).append(rate)
    multi = {k: v for k, v in byrow.items() if len(v) > 1}
    spreads = {k: max(v) - min(v) for k, v in multi.items()}
    check("N9", bool(multi) and all(s < 0.02 for s in spreads.values()),
          f"every multi-input fractional row agrees to < 0.02 across inputs: "
          f"{ {k: round(v, 4) for k, v in spreads.items()} }")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    data = rows()
    print(f"rows loaded: {len(data)}  "
          f"(PHP {sum(1 for d in data if d[0] == 'PHP')}, "
          f"PAT {sum(1 for d in data if d[0] == 'PAT')})")
    print()
    report_levels(data)
    report_blindness(data)
    report_worst(data)
    report_sensitivity(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
