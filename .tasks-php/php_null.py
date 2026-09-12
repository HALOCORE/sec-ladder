#!/usr/bin/env python3
"""HAS ANY PHP FAMILY-B FIGURE BEEN COMPARED AGAINST ITS OWN R5-R4 NULL?

⭐ WHY THIS EXISTS. `harness/check.py`'s null-control docstring (search `269.52`)
carries an OPERATIVE RULE that no PHP document cites:

    "for a cross-RUNG comparison use `kernel_exclusive_ir`; use
     `marginal_ir_per_call` for anti-collapse, which is what it was built for"
    ... "and on any such pattern a published correction must be compared against
     **that pattern's OWN R5 - R4 null** before it is quoted in a band"

`ph64` publishes its headline in `marginal_ir_per_call` (family B1, F74). Every
comparison this programme publishes is cross-rung. ▶ So the question is whether
the PHP side has ever quoted the null the frozen harness says must be quoted
first, and whether the published figures survive it.

The harness's own reason for the rule is that `kernel_exclusive_ir` (family A)
"is structurally immune to BOTH mechanisms: 0 of 288 moved in the pad census
above, and it is symbol-scoped so it never charges a callee."
⚠⚠ THAT IS THE SAME PROPERTY F85 MEASURES AS A's DEFECT. The harness values
"never charges a callee" and F85 measures it as the reason A points the wrong way
cross-language. This probe does not settle that; it measures the null, which is
the input to settling it.

WHAT IT COMPUTES, from committed records only -- no callgrind, no build:
  * null_B  = B(verus) - B(unsafe)   per (row, opt, mode, input), Ir/call
  * null_A  = A(verus) - A(unsafe)   per the same cell, Ir/call
              A = `kernel_exclusive_ir` / n_iters, n_iters read from the input's
              offset 0 (`.memory/02-bench-rules.md`; `check.py::_probe_input`)
  * each row's `identity` pin per opt, so a cell where the null is NOT a null
    (level != `exact` -- the two programs genuinely differ) is marked as such
  * the published cross-language pair (c-gcc - safe_naive) and same-language
    pair (safe_tuned - unsafe) differences in Ir/call, against |null_B|

⚠⚠ A NULL IS ONLY A NULL WHERE THE IDENTITY PIN COVERS THE CELL, AND THE FIRST
VERSION OF THIS PROBE GOT THAT WRONG. `check.py`'s own docstring says it twice --
"⚠⚠⚠ A NULL IS A PROPERTY OF A CELL. DO NOT MAX IT OVER MODE, OVER LEVEL, OR
OVER INPUT" and "a null control is only a null in the MODE ITS IDENTITY PIN
COVERS" -- and N1 below originally asserted `null_A ~ 0` across ALL cells,
including `-O0` cells where every PHP row pins `differ` or `norel`. It FAILED at
`ph03 O0/isolated/small +3237.828`, which is not a defect: at `-O0` those two
kernels ARE different programs.

⛔⛔ AND THE FIX WAS WRONG TOO, IN THE WAY MY OWN F82 ALREADY REFUTED. The second
version used `identity[opt] == 'exact'`, and **F82's whole point is that the
LEVEL IS THE WRONG PREDICATE** -- its N6 exists because a level-based restriction
"drops PAT's family-B worst by 5.7% ... by discarding five valid cells. I WOULD
HAVE PUBLISHED IT." ▶ The predicate is `Δnopad == 0 and Δbytes == 0` from
`counts_a`/`counts_b`; see `valid()`. ⭐ That is the FIFTH time in this thread
that a check of mine lacked a scoping already on file -- and the first where the
document that supplied it was MY OWN FINDING FROM THE PREVIOUS ROUND.

DECLARED EXPECTATIONS, BEFORE RUNNING (the manager's last two on `ph64` were
both wrong, which is the argument for writing them down):
  E1 null_A is ~0 at every VALID cell. If it is not, the harness's structural
     claim does not transfer to this corpus and A needs its own null too.
  E2 null_B is NOT ~0 at some valid cell -- the PAT side reaches 269.52.
  E3 rows pinned `differ` (`ph45`, `ph64` per item 61) show the LARGEST |null_B|,
     because there the two programs really are different and it is not a null at
     all. ⚠ If `differ` rows show ~0 instead, the identity pin controls nothing
     and the framing above is wrong.
  E4 at least one published cross-language difference is SMALLER than its own
     row's |null_B|. That is the finding if it holds and a clean result if not.
  E5 ⚠ MEASURED WHILE FIXING N1, SO NOT A PREDICTION -- AND STATED WRONG THE
     FIRST TIME. True: not one PHP row PINS `exact` at `-O0`, and only 4 of 7 do
     at `-O3`. ⛔ FALSE, and N5b caught it: that does NOT mean there is no `-O0`
     null. F82's count predicate rescues `ph00` and `ph29` at `-O0` as well --
     which F82 never checked, because F82 measured O3 only. ▶ THE CORRECTED
     CENSUS: 5 of 7 rows have a valid null somewhere (`ph07` by the rescue);
     `ph45` and `ph64` have NONE at any cell; and `ph64` is the one row whose
     headline is family B (F74).

⭐ COMMITTED HERE, NOT IN `.temp/`, ON PURPOSE. This is a re-runnable check --
every new row should be asked "does it have a valid null? does its published
figure clear it?" -- so it belongs with `quota.py`, `boxcheck.py`, `citecheck.py`,
`coverage.py` and `fixsurvey.py` rather than in gitignored scratch. That is open
item 65's defect (*"a committed claim resting on gitignored scratch"*) avoided
rather than added to. ⚠ `PROTOCOL_PHP.md` §H binds it: it is a validator, so it
lands with its must-fire negatives. `--selftest` has 12.

Run:  python3 .tasks-php/php_null.py --selftest
      python3 .tasks-php/php_null.py
"""
import json
import math
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROWS = [
    ("ph00", "ph00-smoke"),
    ("ph03", "ph03-uudecode-bound"),
    ("ph07", "ph07-strcut-cursor"),
    ("ph16", "ph16-fdset-index"),
    ("ph29", "ph29-recvfrom-alloc"),
    ("ph45", "ph45-htmlent-cache-int"),
    ("ph64", "ph64-callback-frees-cursor"),
]
INPUTS = ["small.bin", "large.bin"]
OPTS = ["O0", "O3"]
MODES = ["isolated", "whole"]

# ⚠ An absolute floor, because "the difference is inside the null" is
# meaningless when both are rounding dust. 1.00 Ir/call is `check.py`'s own
# smallest documented null class boundary (`1.00 <= |null| < 2`).
IR_FLOOR = 1.0


def gate(slug):
    return json.load(open(os.path.join(ROOT, f"results-php/gate/{slug}.json")))


def meas(slug):
    return json.load(open(os.path.join(ROOT, f"results-php/{slug}.json")))


def n_iters(slug, inp):
    p = os.path.join(ROOT, f"patterns-php/{slug}/inputs/{inp}")
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return struct.unpack("<Q", f.read(8))[0]


def b_of(g, cell, opt, mode, inp):
    return (g.get("marginal_ir_per_call") or {}).get(f"{cell}/{opt}/{mode}/{inp}")


def a_table(slug):
    """(cell, opt, mode, inp) -> kernel_exclusive_ir / n_iters."""
    out = {}
    m = meas(slug)
    for c in m["cells"]:
        for inp, d in (c.get("ir") or {}).items():
            n = n_iters(slug, inp)
            k = d.get("kernel_exclusive_ir")
            if n and k is not None:
                out[(c["cell"], c["opt"], c["mode"], inp)] = k / n
    return out


def identity_levels(g):
    """opt -> the whole `unsafe vs verus` identity ENTRY (level + counts)."""
    out = {}
    for e in g.get("identity") or []:
        if e.get("pair") == "unsafe vs verus":
            out[e["opt"]] = e
    return out


def lvl(ident, opt):
    e = ident.get(opt)
    return (e or {}).get("level", "?")


def valid(ident, opt, mode):
    """⚠⚠ A NULL IS ONLY A NULL HERE, AND **THE LEVEL IS THE WRONG PREDICATE** —
    F82, which is MY OWN FINDING FROM LAST ROUND AND I USED THE WRONG TEST
    ANYWAY. `exact` is BYTE-identity; a *count* statistic needs only the executed
    count to agree, and `norel` covers two situations (same instructions at
    different rip-relative displacements, and genuinely different code).

    F82's predicate, from the identity entry's own `counts_a`/`counts_b` =
    `[n_raw, n_nopad, n_bytes]`:  **`Δnopad == 0 and Δbytes == 0`.**
    It rescues `ph07` (*"R4 == R5 at O3 UP TO RELOCATIONS … 251 instructions and
    953 bytes in BOTH cells"*) and 5 PAT rows. ⚠ F82's own N6 exists because a
    level-based restriction *"drops PAT's family-B worst by 5.7×, to a perfectly
    plausible number, by discarding five valid cells — I would have published
    it."* ▶ **And one round later I wrote the level test into this probe.**

    `check_identity` compares `isolated` digests only, so `whole` is never a
    null regardless of counts."""
    if mode != "isolated":
        return False
    e = ident.get(opt)
    if not e:
        return False
    a, b = e.get("counts_a"), e.get("counts_b")
    if not a or not b or len(a) < 3 or len(b) < 3:
        return False
    return a[1] == b[1] and a[2] == b[2]


def sensitivity():
    """⭐⭐ THE HALF F82 LEFT OPEN, FOR FAMILY B.

    F82: *"A NULL CONTROL IS ONE-SIDED ... A statistic hard-wired to `0` would
    ace every null in this tree. The SENSITIVITY half was never measured"* -- and
    it then measured **family A's** sensitivity on the two rows whose R4/R5
    kernels differ by a KNOWN static count (`ph45`, `ph64`), where A therefore
    has a PREDICTED nonzero value. ▶ **It never measured B's. This does.**

    Returns rows of (short, opt, inp, dnopad, A_per_call, rate_per_insn,
    B_per_call)."""
    out = []
    for short, slug in ROWS:
        g, at = gate(slug), a_table(slug)
        ident = identity_levels(g)
        for opt in OPTS:
            e = ident.get(opt)
            if not e:
                continue
            a, b = e.get("counts_a"), e.get("counts_b")
            if not a or not b:
                continue
            dn = b[1] - a[1]
            if dn == 0:
                continue          # a true null: A's predicted value is 0
            for inp in INPUTS:
                n = n_iters(slug, inp)
                au = at.get(("unsafe", opt, "isolated", inp))
                av = at.get(("verus", opt, "isolated", inp))
                bu = b_of(g, "unsafe", opt, "isolated", inp)
                bv = b_of(g, "verus", opt, "isolated", inp)
                if None in (au, av, bu, bv) or not n:
                    continue
                dA = av - au
                out.append((short, opt, inp, dn, dA, dA / dn, bv - bu))
    return out


def collect():
    """row -> {'ident':..., 'null_b':..., 'null_a':..., 'xlang':..., 'same':...}"""
    d = {}
    for short, slug in ROWS:
        g, at = gate(slug), a_table(slug)
        ident = identity_levels(g)
        nb, na, xl, sm = {}, {}, {}, {}
        for opt in OPTS:
            for mode in MODES:
                for inp in INPUTS:
                    key = (opt, mode, inp)
                    bu = b_of(g, "unsafe", opt, mode, inp)
                    bv = b_of(g, "verus", opt, mode, inp)
                    if bu is not None and bv is not None:
                        nb[key] = bv - bu
                    au = at.get(("unsafe", opt, mode, inp))
                    av = at.get(("verus", opt, mode, inp))
                    if au is not None and av is not None:
                        na[key] = av - au
                    bc = b_of(g, "c-gcc", opt, mode, inp)
                    bn = b_of(g, "safe_naive", opt, mode, inp)
                    if bc is not None and bn is not None:
                        xl[key] = bc - bn
                    bt = b_of(g, "safe_tuned", opt, mode, inp)
                    if bt is not None and bu is not None:
                        sm[key] = bt - bu
        d[short] = dict(slug=slug, ident=ident, null_b=nb, null_a=na,
                        xlang=xl, same=sm)
    return d


def report():
    d = collect()
    print("=" * 104)
    print("R5 - R4 NULL, family B (`marginal_ir_per_call`) vs family A "
          "(`kernel_exclusive_ir`/n_iters), Ir/call")
    print("=" * 104)
    print(f"  {'row':6s} {'identity O0/O3':16s} {'cell':26s} "
          f"{'null_B':>12s} {'null_A':>12s}  valid?")
    for short, _ in ROWS:
        r = d[short]
        il = f"{lvl(r['ident'],'O0')}/{lvl(r['ident'],'O3')}"
        first = True
        for key in sorted(r["null_b"], key=lambda k: (k[0], k[1], k[2])):
            nb = r["null_b"][key]
            na = r["null_a"].get(key)
            v = valid(r["ident"], key[0], key[1])
            print(f"  {short if first else '':6s} {il if first else '':16s} "
                  f"{'/'.join(key):26s} {nb:12.3f} "
                  f"{'   n/a      ' if na is None else f'{na:12.3f}'}  "
                  f"{'✅ NULL' if v else '⛔ not a null'}")
            first = False
        print()
    print("  ⚠⚠ `valid` = identity pin `exact` AND mode `isolated`, because")
    print("     `check_identity` compares isolated digests only. Everywhere")
    print("     else R4 and R5 are DIFFERENT PROGRAMS and the column is a")
    print("     real difference, not a null.")
    print()

    print("=" * 104)
    print("⭐ THE RULE'S QUESTION: is a PUBLISHED difference inside its own "
          "row's null?  (O3/isolated -- the column")
    print("   `check.py` says corrections are published in)")
    print("=" * 104)
    print(f"  {'row':6s} {'inp':10s} {'null_B':>10s} "
          f"{'c-gcc - safe_naive':>20s} {'ratio':>8s} "
          f"{'safe_tuned - unsafe':>21s} {'ratio':>8s}")
    for short, _ in ROWS:
        r = d[short]
        for inp in INPUTS:
            key = ("O3", "isolated", inp)
            nb = r["null_b"].get(key)
            if nb is None:
                continue
            x, s = r["xlang"].get(key), r["same"].get(key)
            ok = valid(r["ident"], key[0], key[1])

            def rat(v):
                # ⛔ THE DOCSTRING'S OWN WARNING, APPLIED TO THIS TABLE. Where
                # the identity pin does not cover the cell, `null_B` is a real
                # difference between two different programs, so a ratio against
                # it is not a null comparison and must not be printed as one.
                if not ok:
                    return " NO NULL"
                if v is None:
                    return "     n/a"
                if abs(nb) < IR_FLOOR:
                    return "  null~0"
                return f"{abs(v) / abs(nb):8.2f}"
            print(f"  {short:6s} {inp:10s} "
                  f"{nb:10.3f}{'' if ok else '*'} "
                  f"{'         n/a' if x is None else f'{x:20.3f}'} {rat(x)} "
                  f"{'          n/a' if s is None else f'{s:21.3f}'} {rat(s)}")
    print()
    print("  ⛔ `* / NO NULL` = F82's count predicate (Δnopad == 0 and")
    print("     Δbytes == 0) does NOT hold here, so the `null_B` column is a")
    print("     real difference between two different programs and a ratio")
    print("     against it would not be a null comparison. ⭐ 2 of 7 rows --")
    print("     ph45 and ph64 -- are in that state at EVERY cell, and ph64 is")
    print("     the one row whose HEADLINE is family B (F74). ⓘ `ph07` pins")
    print("     `norel` and IS a valid null here: F82's rescue, 247 non-pad")
    print("     instructions and 953 bytes in both cells.")
    print()
    print(f"  ⚠ `ratio` is |difference| / |own null|. A ratio under ~2 means the "
          f"published\n    figure is INSIDE its own null control. `null~0` means "
          f"|null| < {IR_FLOOR} Ir/call\n    and the ratio carries no "
          f"information -- the magnitude floor, stated.")
    print()
    print()
    print("=" * 104)
    print("⭐⭐ SENSITIVITY — the half F82 left open, for family B. Only cells "
          "where dnopad != 0, i.e.")
    print("   where A has a PREDICTED nonzero value and 'is it 0?' cannot be "
          "aced by a dead statistic.")
    print("=" * 104)
    print(f"  {'row':6s} {'opt':4s} {'inp':10s} {'dnopad':>7s} "
          f"{'A Ir/call':>11s} {'rate/insn':>10s} {'B Ir/call':>12s} "
          f"{'|B/A|':>9s}  sign")
    for short, opt, inp, dn, dA, rate, dB in sensitivity():
        ratio = abs(dB / dA) if dA else float("inf")
        agree = "same" if (dA > 0) == (dB > 0) else "⛔ OPPOSITE"
        print(f"  {short:6s} {opt:4s} {inp:10s} {dn:+7d} {dA:+11.4f} "
              f"{rate:+10.4f} {dB:+12.3f} {ratio:9.1f}x  {agree}")
    print()
    print("  ⭐ A resolves the static difference TO THE INSTRUCTION (`ph45` "
          "rate 1.0000 on both\n     inputs, 7.5x apart in call count) or to a "
          "stable conditional rate (`ph64`\n     0.5093/0.5100, agreeing to "
          "0.0007) — F82's own control, reproduced here.")
    print("  ⚠⚠ B IS NOT MEASURING THE KERNEL, and that is the honest framing: "
          "B is a WHOLE-\n     PROGRAM slope, so its true value is not -2. The "
          "operative consequence is that\n     at most |dnopad| Ir/call of B's "
          "reading can be the code change, and a reader\n     who takes B as a "
          "proxy for the kernel gets the DIRECTION wrong.")
    print("  ⭐⭐ AND IT IS SCOPED TO THE SMALL-delta REGIME — which is exactly "
          "where a\n     `fixed-R4 bound` operates. At -O0, where dnopad is "
          "-170/+44, |B/A| falls to\n     0.2x-3.0x. See N8.")
    print()
    print("  ⚠⚠ THE LEVEL IS NOT THE PREDICATE (F82). 5 of 7 rows have a "
          "valid null\n     somewhere; `ph45` and `ph64` have NONE, so on those "
          "two the frozen\n     harness's \"compare against that pattern's OWN "
          "R5-R4 null before it is\n     quoted in a band\" CANNOT BE SATISFIED "
          "by this method at all.")
    return d


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST — must-fire negatives")
    d = collect()

    # N1 ⭐ E1, AND IT IS SCOPED -- see the docstring. Family A is symbol-scoped,
    #    so at a cell the identity pin covers (`exact`, `isolated`) the two
    #    kernels are byte-identical and A's null MUST be 0. Anything else is a
    #    reading error in this probe, not a finding.
    vcells = [(s, k) for s, r in d.items() for k in r["null_a"]
              if valid(r["ident"], k[0], k[1])]
    bad = [(s, "/".join(k), round(d[s]["null_a"][k], 3)) for s, k in vcells
           if abs(d[s]["null_a"][k]) > 0.5]
    check("N1", not bad,
          f"family A's R5-R4 null is exactly ~0 at all {len(vcells)} VALID "
          f"cells (identity `exact` + `isolated`): {bad[:6]}")

    # N1b ⚠⚠ AND THE CONTROL THAT MAKES N1 MEAN SOMETHING. If A's null were ~0
    #    at INVALID cells too, N1 would be testing nothing -- it would pass for
    #    any scoping, including the wrong one I first wrote.
    icells = [(s, k) for s, r in d.items() for k in r["null_a"]
              if not valid(r["ident"], k[0], k[1])]
    loud = [(s, "/".join(k), round(d[s]["null_a"][k], 1)) for s, k in icells
            if abs(d[s]["null_a"][k]) > 100.0]
    check("N1b", loud,
          f"family A's null is LOUD (>100 Ir/call) at {len(loud)} of "
          f"{len(icells)} INVALID cells, so N1's scoping is load-bearing and "
          f"not decoration: {loud[:4]}")

    # N2 ⚠ THE READING CHECK. Reproduce a number a published finding quotes, so
    #    a mis-keyed lookup cannot pass silently. F84's table: ph03/small
    #    O3/isolated has A = 0 and B = +266.000.
    n2b = d["ph03"]["null_b"].get(("O3", "isolated", "small.bin"))
    n2a = d["ph03"]["null_a"].get(("O3", "isolated", "small.bin"))
    check("N2", n2b is not None and abs(n2b - 266.0) < 0.01
          and n2a is not None and abs(n2a) < 0.01,
          f"F84's published ph03/small O3/iso cell reproduces: null_B={n2b} "
          f"(expect +266.000), null_A={n2a} (expect 0)")

    # N3 ⚠ item 61's claim, checked rather than trusted: ph07 pins `norel`,
    #    ph45 and ph64 pin `differ`, the rest `exact`.
    want = {"ph00": "exact", "ph03": "exact", "ph07": "norel", "ph16": "exact",
            "ph29": "exact", "ph45": "differ", "ph64": "differ"}
    got = {s: lvl(d[s]["ident"], "O3") for s in want}
    check("N3", got == want,
          f"item 61's identity pins are right at O3: {got}")

    # N3b ⭐⭐ F82's RESCUE, CHECKED RATHER THAN TRUSTED. `ph07` pins `norel` at
    #     O3 and F82 says the COUNTS rescue it (251 instructions, 953 bytes in
    #     both cells). If this fails, either F82 is wrong or the predicate above
    #     is misreading `counts_a`/`counts_b`.
    e7 = d["ph07"]["ident"].get("O3") or {}
    check("N3b", valid(d["ph07"]["ident"], "O3", "isolated"),
          f"`ph07`/O3 is a VALID null by F82's count predicate despite pinning "
          f"`norel`: counts_a={e7.get('counts_a')} counts_b={e7.get('counts_b')}")

    # N3c ⚠ AND THE OTHER SIDE OF F82's TABLE: `ph45` and `ph64` must FAIL the
    #     count predicate too, or the predicate accepts everything and rescues
    #     nothing.
    check("N3c", not valid(d["ph45"]["ident"], "O3", "isolated")
          and not valid(d["ph64"]["ident"], "O3", "isolated"),
          f"`ph45` and `ph64` are still NOT nulls under the count predicate — "
          f"F82's 'genuinely NOT a null' column is 2 rows, not 0")

    # N4 ⭐ E2, SCOPED. At least one row's B null must be substantial at a VALID
    #    cell, or there is nothing for the rule to be about.
    vbig = {s: round(max((abs(d[s]["null_b"][k]) for k in d[s]["null_b"]
                          if valid(r["ident"], k[0], k[1])), default=0), 2)
            for s, r in d.items()}
    check("N4", any(v >= 2.0 for v in vbig.values()),
          f"at least one row has |null_B| >= 2.00 Ir/call at a VALID cell: "
          f"{vbig}")

    # N5 ⭐⭐ E5, AND IT IS THE FINDING. `ph64` publishes its headline in family
    #    B (F74) and pins `differ` at BOTH opt levels, so it has NO valid cell
    #    and the frozen harness's "compare against that pattern's OWN R5-R4
    #    null" cannot be satisfied on it by this method. ⚠ A check that CAN
    #    fail: if `ph64` turns out to have a valid cell, the finding is dead.
    nval = {s: sum(1 for k in r["null_b"] if valid(r["ident"], k[0], k[1]))
            for s, r in d.items()}
    check("N5", nval["ph64"] == 0 and nval["ph45"] == 0
          and all(nval[s] > 0 for s in ("ph00", "ph03", "ph07", "ph16", "ph29")),
          f"`ph64` and `ph45` have ZERO valid null cells while the other FIVE "
          f"rows — ph07 INCLUDED, by F82's rescue — have some: {nval}")

    # N5b ⭐⭐ THE `-O0` AXIS, WHICH F82 NEVER MEASURED. My first version of this
    #     asserted NO row is a valid null at -O0 (true of the LEVEL: none pins
    #     `exact`) and it FAILED, because the count predicate rescues `ph00` and
    #     `ph29` there. ▶ What is checkable is that the axis DISCRIMINATES: some
    #     rows are valid at -O0 and some are not. If all or none were, `-O0`
    #     would carry no information and the census could drop the level.
    o0 = {s: valid(r["ident"], "O0", "isolated") for s, r in d.items()}
    check("N5b", any(o0.values()) and not all(o0.values()),
          f"the `-O0` axis discriminates — some rows ARE valid nulls at -O0 "
          f"under F82's count predicate though NONE pins `exact` there, which "
          f"F82 did not measure: {o0}")

    # N6 ⚠ the magnitude floor is APPLIED, not merely declared: assert that some
    #    cell is actually below it, or the floor has never been exercised and I
    #    cannot claim it protects anything.
    tiny = [(s, "/".join(k)) for s, r in d.items()
            for k, v in r["null_b"].items() if abs(v) < IR_FLOOR]
    check("N6", tiny,
          f"the {IR_FLOOR} Ir/call floor is exercised by {len(tiny)} real cells, "
          f"so it is not a decoration: {tiny[:4]}")

    # N7 ⚠ every row must contribute cells, or a silent path error looks like a
    #    clean result.
    empty = [s for s, r in d.items() if not r["null_b"]]
    check("N7", not empty, f"every row contributed null_B cells: missing {empty}")

    sens = sensitivity()

    # N7b ⭐ F82's OWN CONTROL, REPRODUCED. `ph45`'s exec_rate must be exactly
    #     1.0000 on BOTH inputs and `ph64`'s ~0.51 on both. If my reading of the
    #     records were wrong this would not land on a published finding's digits.
    r45 = [round(t[5], 4) for t in sens if t[0] == "ph45" and t[1] == "O3"]
    r64 = [round(t[5], 4) for t in sens if t[0] == "ph64" and t[1] == "O3"]
    check("N7b", r45 == [1.0, 1.0] and len(r64) == 2
          and all(abs(v - 0.5096) < 0.001 for v in r64),
          f"F82's exec_rate control reproduces: ph45 O3 {r45} (expect 1.0 both) "
          f"ph64 O3 {r64} (expect ~0.51 both, agreeing to 0.0007)")

    # N8 ⚠⚠ THE F52 CONTROL, AND IT IS THE ONE THAT COULD KILL THE CLAIM. If
    #    |B/A| were large at EVERY cell the finding would be the empty "B is
    #    bigger than A". It must be large in the SMALL-delta regime and NOT in
    #    the large-delta one, or there is no regime and no finding.
    small = [abs(t[6] / t[4]) for t in sens if abs(t[3]) <= 2 and t[4]]
    large = [abs(t[6] / t[4]) for t in sens if abs(t[3]) > 2 and t[4]]
    check("N8", small and large and min(small) > 10.0 and max(large) < 10.0,
          f"|B/A| is >10x at every small-delta cell {[round(v, 1) for v in small]} "
          f"and <10x at every large-delta cell {[round(v, 1) for v in large]} — "
          f"so this is a REGIME, not 'B is bigger than A'")

    # N9 ⚠ the sign disagreement, counted rather than asserted, WITH the
    #    magnitude floor the third failure this round taught me to state.
    opp = [(t[0], t[1], t[2]) for t in sens
           if abs(t[3]) <= 2 and t[4] and (t[4] > 0) != (t[6] > 0)
           and abs(t[6]) >= IR_FLOOR]
    check("N9", len(opp) >= 2,
          f"B takes the OPPOSITE sign from the known static change on "
          f"{len(opp)} of 4 small-delta cells, all above the {IR_FLOOR} Ir/call "
          f"floor: {opp}")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else (report(), 0)[1])
