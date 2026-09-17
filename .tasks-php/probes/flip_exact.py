#!/usr/bin/env python3
# =============================================================================
# flip_exact.py -- THE MEASUREMENT BEHIND F85 AND F86
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/mgr172/`, which is GITIGNORED, and both findings it produced are
# PUBLISHED in `RECAP_PHP.md`: **F85** (*"the CROSS-LANGUAGE column carries 29
# of 38 sign flips ... this project's central claim"*) and **F86** (*"three
# classes not two (agree/FLIP/BLIND), and the exact flip test proves THERE IS
# NO SHORTCUT: certifying A needs B"*). ▶ A PUBLISHED FINDING WHOSE ONLY
# EVIDENCE IS A GITIGNORED PROBE IS A FINDING THAT WILL NOT SURVIVE A CLEAN
# CHECKOUT: `.memory-php/04-process.md` LAW 11.
#
# RUN IT:  python3 .tasks-php/probes/flip_exact.py --selftest   # the negatives
#          python3 .tasks-php/probes/flip_exact.py              # the table
#
# ✅ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered:
# ⭐ NOTHING. It reads `results-php/<row>.json` and `results-php/gate/<row>.json`
# for the seven rows in `ROWS`, all committed; it builds nothing, runs no binary
# and WRITES NOTHING. On a clean checkout it runs to completion in 0.07 s.
# ⚠ ONE THING IT DOES CARRY IS A POPULATION: `ROWS` is a hand-written list of
# seven rows, so a row gated after this was written is NOT in the count. The
# flip totals it prints are over THAT population and must be quoted with it.
#
# WHAT IT FOUND, beyond the algebra the docstring derives: the flip set is
# EXACTLY the set where `1` lies between the two ratios -- 0 mispredictions over
# every comparison in the corpus -- so `flip` is not an empirical phenomenon to
# be thresholded. ⭐⭐ And the three-class split is the part a count would have
# hidden: `BLIND` (A reads exactly 0 against a nonzero B) is a WORSE failure
# than `FLIP` and scoring it as one inflated the first draft's flip count to 52
# against `callee_share.py`'s 37 -- caught by this file's own N5.
# =============================================================================

"""F80's 0.02 THRESHOLD IS A PROXY FOR AN EXACT ALGEBRAIC CONDITION — derive it.

F80 measured: `min(inside_share)` high AND `|Δinside_share| <= 0.02` -> 0 sign
flips in 151 comparisons. `callee_share.py --flips` also prints an anomaly it
could not explain — ⛔ and that probe is UNCOMMITTED SCRATCH
(`.temp/mgr170/callee_share.py`, GITIGNORED, not promoted), so on a clean
checkout it does not exist; the two numbers it produced are quoted here rather
than re-derivable from it:

    flips with Δshare <= 0.02: 6   (all ph45)
    non-flips with Δshare > 0.02: 154  -- so asymmetry is NECESSARY, not SUFFICIENT

⚠⚠ FIRST, THE TRAP I ALMOST PUBLISHED. `inside_share` is DEFINED as
`s = A / B` (per call). So

    A_a / A_b  =  (s_a B_a) / (s_b B_b)  =  (s_a / s_b) * (B_a / B_b)

is an IDENTITY. *"A's disagreement with B is explained by the inside_share
ratio"* is therefore TRUE BY DEFINITION and explains NOTHING — it is F78's
arithmetic-identity shape exactly, and I had it written down as a mechanism
before noticing.

⭐ THE NON-TRIVIAL CONSEQUENCE IS THE FLIP CONDITION. Write r = s_a / s_b and
b = B_a / B_b. Then a = A_a / A_b = r * b exactly, and a SIGN FLIP between the
two families is precisely `a` and `b` falling on OPPOSITE SIDES OF 1:

    flip  <=>  (r*b - 1) and (b - 1) have opposite signs

▶ So a flip needs the share mismatch `r` to be big enough to carry `b` across 1,
which happens exactly when the TRUE EFFECT is SMALLER THAN THE SHARE MISMATCH:

    flip  <=>  1  lies strictly between  b  and  r*b

⭐⭐ AND THAT EXPLAINS THE PROBE'S OWN ANOMALY. Asymmetry is necessary because
`r = 1` gives `a = b` and never flips. It is not sufficient because a large
effect (`b` far from 1) survives any moderate `r`. **F80's `|Δs| <= 0.02` is a
one-sided proxy: it bounds `r` near 1 without looking at the effect size at
all**, which is why 154 comparisons cleared the threshold and did not flip.

⚠ This is ALGEBRA, so it cannot be "confirmed" by the data — it can only be
CONTRADICTED, which is what makes running it worth anything. If the predicate
below mispredicts even one of the 366 comparisons, then either a family is not
what its definition says or a number is being read from the wrong cell.

Run:  python3 .tasks-php/probes/flip_exact.py --selftest
      python3 .tasks-php/probes/flip_exact.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROWS = ["ph00-smoke", "ph03-uudecode-bound", "ph07-strcut-cursor",
        "ph16-fdset-index", "ph29-recvfrom-alloc", "ph45-htmlent-cache-int",
        "ph64-callback-frees-cursor"]
CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]


def load(row):
    m = json.load(open(os.path.join(ROOT, f"results-php/{row}.json")))
    g = json.load(open(os.path.join(ROOT, f"results-php/gate/{row}.json")))
    return m, g


def cells(row):
    """{(cell, input): (A_per_call, B_per_call)} at O3/isolated."""
    m, g = load(row)
    out = {}
    for c in m.get("cells", []):
        if c.get("opt") != "O3" or c.get("mode") != "isolated":
            continue
        for inp, blk in (c.get("ir") or {}).items():
            n = ((m.get("inputs") or {}).get(inp) or {}).get("n_iters")
            if not n or not blk or not blk.get("kernel_exclusive_ir"):
                continue
            b = (g.get("marginal_ir_per_call") or {}).get(
                f"{c['cell']}/O3/isolated/{inp}")
            if not b:
                continue
            out[(c["cell"], inp)] = (blk["kernel_exclusive_ir"] / float(n), b)
    return out


def sign(x, eps=1e-12):
    return 0 if abs(x) < eps else (1 if x > 0 else -1)


def analyse():
    tot = fl = bl = 0
    mis = []
    rows_out = []
    for row in ROWS:
        d = cells(row)
        inputs = sorted({i for _, i in d})
        for inp in inputs:
            present = [c for c in CELLS if (c, inp) in d]
            for i, a in enumerate(present):
                for b in present[i + 1:]:
                    Aa, Ba = d[(a, inp)]
                    Ab, Bb = d[(b, inp)]
                    if not Ab or not Bb:
                        continue
                    tot += 1
                    a_ratio = Aa / Ab
                    b_ratio = Ba / Bb
                    apct = 100.0 * (a_ratio - 1.0)
                    bpct = 100.0 * (b_ratio - 1.0)
                    # ⚠⚠ THREE CLASSES, NOT TWO, AND CONFLATING TWO OF THEM WAS
                    # THIS SCRIPT'S FIRST BUG -- caught by its own N5, which is
                    # the whole reason N5 is phrased as "a number is being read
                    # wrong" rather than "the rule is wrong".
                    #
                    #   agree  same nonzero sign
                    #   FLIP   opposite NONZERO signs -- A points the wrong way
                    #   BLIND  A is EXACTLY 0 while B is not -- A says NOTHING
                    #
                    # `sign(0) != sign(bpct)` scores BLIND as FLIP, which
                    # inflated the count to 52 against `callee_share.py`'s 37
                    # and produced 14 "mispredictions" of a predicate that was
                    # right. ⭐ BLIND is the worse failure and it deserved its
                    # own name: on ph45 it is A reading +0.000 % against a
                    # +23.37 % effect, which is `_037` §5.4's result exactly.
                    blind = sign(apct) == 0 and sign(bpct) != 0
                    flipped = (sign(apct) != 0 and sign(bpct) != 0
                               and sign(apct) != sign(bpct))
                    # the derived predicate: 1 strictly between b_ratio and
                    # r*b_ratio == a_ratio. Written WITHOUT reference to r, so
                    # it is the geometric statement and not a re-substitution.
                    lo, hi = min(a_ratio, b_ratio), max(a_ratio, b_ratio)
                    predicted = lo < 1.0 < hi
                    if flipped:
                        fl += 1
                    if blind:
                        bl += 1
                    if flipped != predicted:
                        mis.append((row, inp, a, b, apct, bpct, a_ratio, b_ratio))
                    # and the identity, checked numerically
                    r = (Aa / Ba) / (Ab / Bb)
                    ident_err = abs(a_ratio - r * b_ratio) / abs(a_ratio)
                    rows_out.append({"row": row, "inp": inp, "a": a, "b": b,
                                     "apct": apct, "bpct": bpct,
                                     "flipped": flipped, "blind": blind,
                                     "predicted": predicted,
                                     "ident_err": ident_err,
                                     "r": r})
    return tot, fl, bl, mis, rows_out


def report():
    tot, fl, bl, mis, rows = analyse()
    print("=" * 78)
    print("THE DERIVED FLIP PREDICATE against every A/B comparison in the corpus")
    print("=" * 78)
    print(f"  comparisons          {tot}")
    print(f"  measured sign FLIPS  {fl}   (opposite nonzero signs)")
    print(f"  A is BLIND           {bl}   (A exactly 0, B nonzero)")
    print(f"  MISPREDICTIONS       {len(mis)}")
    if mis:
        print()
        print("  ⚠⚠⚠ THE PREDICATE IS ALGEBRA, SO A MISPREDICTION IS NOT A")
        print("  FAILURE OF THE RULE -- IT MEANS A NUMBER IS BEING READ WRONG:")
        for row, inp, a, b, ap, bp, ar, br in mis[:12]:
            print(f"      {row} {inp} {a} vs {b}: A {ap:+.3f}% B {bp:+.3f}% "
                  f"ratios {ar:.6f} / {br:.6f}")
    else:
        print()
        print("  ✅ 0 mispredictions. The flip set is EXACTLY the set where 1 lies")
        print("     between the two ratios -- so `flip` is not an empirical")
        print("     phenomenon to be thresholded, it is a GEOMETRIC FACT about")
        print("     two ratios that differ by the share mismatch.")

    err = max(r["ident_err"] for r in rows)
    print()
    print(f"  the identity A_ratio == (s_a/s_b) * B_ratio: max relative error "
          f"{err:.2e}")
    print("  ⚠ That is DEFINITIONAL, not evidence -- `inside_share` IS `A/B`.")
    print("    It is printed so nobody re-derives it and calls it a mechanism.")

    # F80's threshold, scored against BOTH classes separately.
    # ⚠ An earlier version of this block scored against the CONFLATED
    # definition and printed "flips it MISSES 20" beside a comment saying
    # "F80's 6" -- the 20 was 6 real flips plus 14 BLIND cells. Scoring a
    # classifier against a definition the rest of the file has abandoned is
    # how a number survives a rename.
    print()
    print("  F80's PROXY |Δs| <= 0.02 => 'A is safe', SCORED PER CLASS:")
    stats = {"flip": [0, 0], "blind": [0, 0], "agree": [0, 0]}
    subthresh_flips = []
    for row in ROWS:
        d = cells(row)
        for inp in sorted({i for _, i in d}):
            present = [c for c in CELLS if (c, inp) in d]
            for i, a in enumerate(present):
                for b in present[i + 1:]:
                    Aa, Ba = d[(a, inp)]
                    Ab, Bb = d[(b, inp)]
                    if not Ab or not Bb:
                        continue
                    ap = 100.0 * (Aa / Ab - 1.0)
                    bp = 100.0 * (Ba / Bb - 1.0)
                    blind = sign(ap) == 0 and sign(bp) != 0
                    flip = (sign(ap) != 0 and sign(bp) != 0
                            and sign(ap) != sign(bp))
                    kind = "flip" if flip else ("blind" if blind else "agree")
                    ds = abs(Aa / Ba - Ab / Bb)
                    says_safe = ds <= 0.02
                    stats[kind][0 if says_safe else 1] += 1
                    if flip and says_safe:
                        subthresh_flips.append((row[:4], inp, a, b, ds))
    print(f"      {'class':7s} {'threshold says SAFE':>21s} {'says UNSAFE':>13s}")
    for kind in ("flip", "blind", "agree"):
        safe, unsafe = stats[kind]
        print(f"      {kind:7s} {safe:21d} {unsafe:13d}")
    print()
    print(f"  ⚠⚠ The threshold calls {stats['flip'][0]} real FLIPS safe "
          f"and {stats['blind'][0]} BLIND cells safe:")
    for r, inp, a, b, ds in subthresh_flips:
        print(f"        FLIP  {r} {inp:10s} {a} vs {b}  Δs={ds:.4f}")
    print(f"  ⚠ and it flags {stats['agree'][1]} comparisons that AGREE "
          f"-- the 'necessary not sufficient' set.")
    print()
    print("  ⭐ The exact predicate has 0 errors on the FLIP class by")
    print("     construction. What it does NOT cover is BLIND: `a_ratio == 1`")
    print("     exactly, where the predicate's strict inequality is false and")
    print("     A simply reports nothing. ▶ BLIND needs its own test and the")
    print("     threshold does not supply one either.")

    # ------------------------------------------------------------------
    # THE RULE THE DERIVATION ACTUALLY GIVES -- ONE CONDITION, NOT TWO
    # ------------------------------------------------------------------
    # a = r*b exactly. With r > 1: flip iff 1/r < b < 1. With r < 1: flip iff
    # 1 < b < 1/r. Either way:
    #
    #     FLIP  <=>  b lies strictly between 1 and 1/r
    #
    # so the NO-FLIP condition is  |b - 1| >= |1/r - 1|, i.e.
    #
    #   ⭐ A AND B AGREE IN SIGN IFF THE EFFECT IS AT LEAST THE SHARE MISMATCH.
    #
    # That is ONE derived condition replacing F80's two tuned ones, and it
    # explains BOTH of F80's anomalies at once: its 6-7 sub-threshold flips are
    # SMALL EFFECTS (which must flip, for any mismatch), and its 153 flagged
    # non-flips are LARGE EFFECTS (which cannot flip, for any mismatch).
    print()
    print("  " + "=" * 70)
    print("  ⚠⚠⚠ A SCALAR RESTATEMENT I TRIED AND IT IS REFUTED -- 30 of 346")
    print("  " + "=" * 70)
    print("  I tried to reduce the straddle test to `|effect| < |share mismatch|`,")
    print("  i.e. `|b-1| < |1/r-1|`. THAT IS NOT EQUIVALENT: it says b is CLOSER")
    print("  TO 1 than 1/r is, which permits b on the OPPOSITE SIDE of 1, where")
    print("  no flip can occur. The straddle test needs the SIDE as well as the")
    print("  magnitude. The failures below are all `predicted True actual False`")
    print("  -- exactly the wrong-side case. ⭐ KEPT, RUNNING AND LABELLED rather")
    print("  than deleted, because the tidy form is the one somebody will")
    print("  re-derive, and this is the counterexample list.")
    bad = 0
    checked = 0
    for row in ROWS:
        d = cells(row)
        for inp in sorted({i for _, i in d}):
            present = [c for c in CELLS if (c, inp) in d]
            for i, a in enumerate(present):
                for b in present[i + 1:]:
                    Aa, Ba = d[(a, inp)]
                    Ab, Bb = d[(b, inp)]
                    if not Ab or not Bb:
                        continue
                    ap = 100.0 * (Aa / Ab - 1.0)
                    bp = 100.0 * (Ba / Bb - 1.0)
                    if sign(ap) == 0:
                        continue                    # BLIND, not a sign question
                    checked += 1
                    b_ratio = Ba / Bb
                    r = (Aa / Ba) / (Ab / Bb)
                    effect = abs(b_ratio - 1.0)
                    mismatch = abs(1.0 / r - 1.0)
                    predicted_flip = effect < mismatch
                    actual_flip = sign(ap) != sign(bp)
                    if predicted_flip != actual_flip:
                        bad += 1
                        print(f"    ⚠ {row[:4]} {inp} {a} vs {b}: effect "
                              f"{effect:.6f} mismatch {mismatch:.6f} "
                              f"predicted {predicted_flip} actual {actual_flip}")
    print(f"    {checked} sign-bearing comparisons, {bad} DISAGREEMENTS -- so the")
    print("    scalar form is REFUTED and the geometric straddle test above,")
    print("    which has 0, is the only exact statement.")
    print()
    print("  " + "=" * 70)
    print("  ⭐⭐⭐ AND THE PRACTICAL CONCLUSION IS DEFLATIONARY, WHICH IS WHY IT")
    print("  MATTERS: THERE IS NO SHORTCUT.")
    print("  " + "=" * 70)
    print("  The exact test is `1 lies between a_ratio and b_ratio`. It needs")
    print("  BOTH ratios. So deciding whether family A is safe to publish")
    print("  requires computing family B (or C) -- THE VERY STATISTIC THE RULE")
    print("  WOULD LET YOU SKIP. A share-mismatch threshold cannot certify A on")
    print("  its own, at any threshold, because the flip condition depends on")
    print("  the EFFECT SIZE and no function of the shares alone knows it.")
    print()
    print("  ▶ So F80's rule is not a licence to publish A alone. It is a way to")
    print("    EXPLAIN a disagreement after seeing both. The operative rule is")
    print("    the one `ph45` already follows: PUBLISH BOTH, LABELLED, ALWAYS.")
    return mis


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST -- must-fire negatives")
    tot, fl, bl, mis, rows = analyse()

    check("N1", tot > 300, f"{tot} comparisons enumerated (expected ~366)")
    check("N2", fl > 0, f"{fl} measured sign flips -- if 0 there is nothing to "
                        f"predict and the predicate is untested")

    # N3 ⚠ THE PREDICATE MUST BE FALSIFIABLE BY THIS DATA. Feed it a synthetic
    #    pair where 1 does NOT lie between the ratios but the signs differ --
    #    impossible by construction, so instead check the converse: that a
    #    hand-built flipping pair IS predicted, and a non-flipping pair is not.
    def pred(ar, br):
        return min(ar, br) < 1.0 < max(ar, br)
    check("N3", pred(1.05, 0.98) and not pred(1.05, 1.02) and not pred(0.9, 0.8),
          "the predicate fires on (1.05, 0.98), and NOT on (1.05, 1.02) or "
          "(0.9, 0.8) -- it tests straddling 1, not mere inequality")

    # N4 the identity must hold to floating-point precision. If it does not,
    #    inside_share is not A/B in this tree and the whole derivation is void.
    err = max(r["ident_err"] for r in rows)
    check("N4", err < 1e-9,
          f"A_ratio == (s_a/s_b)*B_ratio to {err:.2e} -- so `inside_share` "
          f"really is `A/B` here and the algebra applies")

    # N5 ⭐ AND THE THING THIS SCRIPT EXISTS TO CATCH: 0 mispredictions. Stated
    #    as a negative because a misprediction would mean a number is read from
    #    the wrong cell, NOT that the algebra is wrong.
    check("N5", not mis,
          f"{len(mis)} mispredictions -- any nonzero value means a family is "
          f"being read from the wrong cell, since the predicate is algebra")

    # N6 F80's threshold must be STRICTLY WORSE than the exact predicate, or
    #    there is no point replacing it.
    worse = False
    for row in ROWS:
        d = cells(row)
        for inp in sorted({i for _, i in d}):
            present = [c for c in CELLS if (c, inp) in d]
            for i, a in enumerate(present):
                for b in present[i + 1:]:
                    Aa, Ba = d[(a, inp)]
                    Ab, Bb = d[(b, inp)]
                    if not Ab or not Bb:
                        continue
                    flipped = sign(100.0 * (Aa / Ab - 1)) != sign(100.0 * (Ba / Bb - 1))
                    if flipped and abs(Aa / Ba - Ab / Bb) <= 0.02:
                        worse = True
    check("N6", worse,
          "F80's 0.02 threshold misses at least one real flip, so the exact "
          "predicate is a strict improvement and not a restatement")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
