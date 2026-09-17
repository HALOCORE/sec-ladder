#!/usr/bin/env python3
# =============================================================================
# ph29_predict.py -- **F72's SIX PUBLISHED PREDICTION NUMBERS**, AND THE ONE
# PROMOTION IN THIS BATCH THAT TURNED A DEAD ONE-SHOT INTO A STANDING CHECK
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr169/`, which is GITIGNORED,
# and **F72** cites it TWICE by name (`RECAP_PHP.md:1851` and `:1897`, landed
# 2026-09-11, commit 652c741). Line 1851 is the sentence that matters: *"⭐ **The
# falsifiable prediction** (`ph29_predict.py` runs the *shipped* `idiom_audit`
# on an *in-memory* edit): `spellings` 4 → 12, `pairs` 12 → 36, `present`
# 0 → 22, `required_pins_nothing` 0, `required_absent` 0 → 2, `forbidden_hits`
# 0."* **Those six numbers are this file's output.** `.memory-php/04-process.md`
# LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17, repo at commit f4bda71.
#
# ⛔⛔⛔ AND IT WAS BROKEN WHEN IT ARRIVED -- NOT BY A MISSING CACHE, BY SUCCESS.
# `apply_edit`'s `assert txt.startswith(old)` exists to refuse a stale
# simulation. **The simulated edit LANDED** (`TASK_PHP_033`), so `ph29`'s
# `spec.md` now opens `required[0].c` with the BACKTICKED span, the assert fires
# and the file dies:
#
#     AssertionError: required[0].c no longer opens with 'emalloc(to_read + 1)'
#                     -- spec.md moved
#
# ▶ **A prediction tool whose prediction came true crashes on its own success.**
# That is a THIRD way a promoted probe fails to run, beside `PROMOTE_001`'s two
# (a missing cache) -- and it is the one no amount of cache-guarding catches.
#
# ⭐⭐ WHAT IT DOES NOW, AND IT IS STRICTLY MORE THAN IT DID. It detects which
# image of `spec.md` is on disk:
#
#   PRE-IMAGE   -- simulate the edit and PRINT THE PREDICTION (as before).
#   POST-IMAGE  -- the edit has landed, so simulation is meaningless. Instead it
#                  VERIFIES the six published numbers against the COMMITTED gate
#                  record. ✅ Measured 2026-09-17: **all six land exactly** --
#                  spellings 12 · pairs 36 · present 22 · pins_nothing 0 ·
#                  absent 2 · forbidden_hits 0. F72's prediction was FALSIFIABLE
#                  and it was NOT FALSIFIED, and that is now checkable by anyone
#                  rather than being a sentence in a handoff.
#
# RUN IT:  python3 .tasks-php/probes/ph29_predict.py --selftest   # 5 negatives
#          python3 .tasks-php/probes/ph29_predict.py              # the table
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. It imports `harness/check.py`
# and reads `patterns-php/ph29-recvfrom-alloc/` plus that row's committed gate
# record. Builds nothing, runs no binary, WRITES NOTHING. 0.4 s, 2026-09-17.
#
# ⛔ WHAT IS STILL OWED. (1) **F72 is UNREVIEWED.** (2) ⚠ `PREDICTED` below is a
# HARDCODED SIX-NUMBER LITERAL, which is `.memory-php/04-process.md` law 6's
# class -- and it is DELIBERATE and must not be "derived": it is the PUBLISHED
# 2026-09-11 prediction, a historical constant, and the whole point is that the
# tree is compared against it rather than it tracking the tree. A `PREDICTED`
# that re-derived itself from the gate record could never fail. (3) The
# PRE-IMAGE arm is now unreachable on this tree and is kept only so the file
# still documents what it did; nothing exercises it except `N3`, which plants a
# synthetic pre-image. (4) F72's own caveat stands and is not softened here:
# **`required` CANNOT FAIL THE GATE.** `ph29` became *searchable*, not
# *enforced*.
# =============================================================================

"""Item 51: simulate the repaired ph29 declaration and PREDICT the new audit.

The decision is to backtick the eight leading spans of ph29's `required[0..3]`,
with ONE respelling: `required[1].c` becomes `read_buf[recvd] =` and NOT
`read_buf[recvd] = '\\0'`, because `exec_code` blanks C char literals and the
literal spelling would be a pin that can never match (see
`.tasks-php/probes/charlit_reach.py` -- it would be the first such spelling in
either programme, 0 of 33 PAT and 0 of 6 PHP today).
⚠ THAT PARENTHESIS IS A 2026-09-11 SNAPSHOT AND IT HAS MOVED. Re-run 2026-09-17
over the 14 gated php rows, `charlit_reach.py` reports **1** affected spelling
(`ph52` `required[0].rust`, the Verus keyword `ensures`, blanked by
`exec_code`'s rust layer -- NOT a character literal). The `forbidden` half, the
one that is a ban that cannot fire, is still **0**. The decision below is
unaffected; the reassurance is stale.

⚠ This does NOT edit spec.md. It applies the edit to an in-memory copy of the
contract and runs the SHIPPED `idiom_audit` over the SHIPPED rungs, so the
numbers below are the ones the re-gate must produce. A task that applies the
edit and gets different numbers has found something, and should stop.

⚠ PROTOCOL rule 14: the prediction is printed by running the real function, not
by reasoning about it. The point of writing it down is that it is falsifiable.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "harness"))
import check  # noqa: E402

PDIR = os.path.join(ROOT, "patterns-php", "ph29-recvfrom-alloc")

#: `required[i].<lang>` -> the span to wrap in backticks, exactly as the task
#: must write it. The value MUST already occur at the head of that entry, save
#: for `required[1].c`, which is the deliberate respelling.
#: THREE of the eight are RESPELLINGS and the reasons differ; see NOTES §1.
EDIT = {
    (0, "c"):    "emalloc(to_read + 1)",
    # RESPELLED. `tr.wrapping_add(1)` pins a BINDING NAME: all four Rust rungs
    # compute it, but the safe two spell `(to_read as u64).wrapping_add(1)`.
    # `.wrapping_add(1)` pins all four at exactly one line each (100/64/88/450).
    (0, "rust"): ".wrapping_add(1)",
    # RESPELLED. `read_buf[recvd] = '\0'` pins NOTHING -- `exec_code` layer 1
    # blanks C char literals, so the literal spelling is dead on arrival.
    (1, "c"):    "read_buf[recvd] =",
    # KEPT, and genuinely unsafe-side: the safe rungs spell the CHECKED
    # `read_buf[recvd as usize] = 0`. The entry must gain the English that says
    # so -- today it is a bare span with no scope at all.
    (1, "rust"): "vset_unchecked(&mut read_buf, recvd, 0)",
    (2, "c"):    "php_shim_tally()",
    (2, "rust"): "1000039",
    (3, "c"):    "php_shim_reset",
    (3, "rust"): "real_size",
}

#: `required[i][lang]` spans that are NOT a prefix of the entry, because the
#: entry is being respelled rather than merely quoted. Maps to the old span.
RESPELLED = {
    (0, "rust"): "tr.wrapping_add(1)",
    (1, "c"):    "read_buf[recvd] = '\\0'",
}


def apply_edit(contract):
    """Backtick the leading span of each edited entry, in memory."""
    c = copy.deepcopy(contract)
    req = c["idiom"]["required"]
    for (i, lang), span in EDIT.items():
        txt = req[i][lang]
        old = RESPELLED.get((i, lang), span)
        assert txt.startswith(old), \
            f"required[{i}].{lang} no longer opens with {old!r} -- spec.md moved"
        # The entry keeps its old span in the prose that follows, so a reader
        # still sees what the rung literally writes; only the PIN is the new
        # span. That is why the tail is preserved rather than replaced.
        tail = txt[len(old):]
        if (i, lang) in RESPELLED:
            # ⚠ NO BACKTICKS on the old span here. Quoting what you are
            # EXPLAINING makes it a second pin -- that is forbidden[0]'s own
            # trap, and on required[1].c the second pin would be the dead
            # char-literal one this respelling exists to avoid.
            tail = (f"  -- the rung writes {old} and the pin is the span above, "
                    f"quoted without backticks on purpose") + tail
        req[i][lang] = f"`{span}`" + tail
    return c


def audit(contract):
    rungs = [(r, l, open(os.path.join(PDIR, r)).read())
             for r, l in check.rung_sources(PDIR)]
    extra = [(r, l, open(os.path.join(PDIR, r)).read())
             for r, l in check.forbidden_only_sources(PDIR)]
    return check.idiom_audit(contract, rungs, extra)


#: ⛔⛔ THE PUBLISHED PREDICTION, `RECAP_PHP.md:1851`, 2026-09-11. A HARDCODED
#  LITERAL ON PURPOSE. `.memory-php/04-process.md` law 6 forbids a figure that
#  goes stale unnoticed; this one is a HISTORICAL CONSTANT, and deriving it from
#  the tree would make it a check that cannot fail. ▶ If the tree moves off it,
#  that is a REAL result -- either the row was re-gated or F72's number is
#  stale -- and the arm below is what says so.
PREDICTED = {"spellings": 12, "pairs": 36, "present": 22,
             "required_pins_nothing": 0, "required_absent": 2,
             "forbidden_hits": 0}

KEYS = ("spellings", "forbidden_spellings", "pairs", "present",
        "required_pins_nothing", "required_absent", "forbidden_hits",
        "forbidden_unaudited_entries", "no_rung_entries")

GATE = os.path.join(ROOT, "results-php", "gate", "ph29-recvfrom-alloc.json")


def landed(contract):
    """Has the simulated edit already been APPLIED to `spec.md`?

    PURE over the contract, so `N3` can plant a synthetic pre-image. True iff
    EVERY edited entry opens with the backticked NEW span; False iff every one
    opens with the bare OLD span. Anything in between is a third state and is
    reported rather than guessed at.
    """
    req = contract["idiom"]["required"]
    post = sum(1 for (i, lang), span in EDIT.items()
               if req[i][lang].startswith("`" + span + "`"))
    pre = sum(1 for (i, lang), span in EDIT.items()
              if req[i][lang].startswith(RESPELLED.get((i, lang), span)))
    if post == len(EDIT):
        return True
    if pre == len(EDIT):
        return False
    return None                      # ⚠ mixed: neither image, say so


def mismatches(got, predicted=None):
    """PURE. `[(key, got, want)]` for every published prediction that missed."""
    predicted = PREDICTED if predicted is None else predicted
    return [(k, got.get(k), v) for k, v in sorted(predicted.items())
            if got.get(k) != v]


def selftest():
    fails = []

    def ck(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST -- must-fire negatives")
    contract, _ = check.read_contract(PDIR)
    committed = json.load(open(GATE))["idiom_audit"]

    # N1 MUST-FIRE: a perturbed audit is caught. Without this the comparison
    #    could be vacuously true and nobody would know.
    bad = dict(committed, spellings=999)
    ck("N1", [k for k, _, _ in mismatches(bad)] == ["spellings"],
          f"a perturbed `spellings` is caught: {mismatches(bad)}")

    # N2 ⭐ THE ONE THAT CARRIES F72: the COMMITTED gate record must still match
    #    all six published predictions.
    miss = mismatches(committed)
    ck("N2", not miss,
          f"the committed ph29 gate record matches all {len(PREDICTED)} "
          f"published predictions"
          + (f" -- ⛔ MISSED: {miss}" if miss else ""))

    # N3 MUST-FIRE both ways: `landed` reads the shipped contract as POST-IMAGE
    #    and a synthetic pre-image as PRE-IMAGE. Planting the input is the only
    #    way to show the PRE arm at all, since the edit has landed for good.
    pre = copy.deepcopy(contract)
    for (i, lang), span in EDIT.items():
        old = RESPELLED.get((i, lang), span)
        pre["idiom"]["required"][i][lang] = old + "  -- synthetic pre-image"
    ck("N3", landed(contract) is True and landed(pre) is False,
          f"shipped spec.md reads POST-IMAGE ({landed(contract)}) and a planted "
          f"pre-image reads PRE-IMAGE ({landed(pre)})")

    # N4 the harness reads the same thing the gate wrote. If this fails, nothing
    #    else here means anything -- it is `item83_sim.py`'s N1 by another name.
    now = audit(contract)
    drift = [k for k in KEYS if now.get(k) != committed.get(k)]
    ck("N4", not drift,
          f"re-running the SHIPPED idiom_audit reproduces the committed record "
          f"on all {len(KEYS)} keys" + (f" -- DRIFT: {drift}" if drift else ""))

    # N5 MUST-FIRE: `apply_edit` still REFUSES a stale simulation. This is the
    #    assert that killed the file, kept deliberately -- what changed is that
    #    `main` no longer walks into it, not that the guard was weakened.
    try:
        apply_edit(contract)
        ok5 = False
    except AssertionError:
        ok5 = True
    ck("N5", ok5,
          "apply_edit still refuses to simulate an edit that has already "
          "landed (the guard is kept, not weakened)")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 0 if not fails else 1


def main():
    contract, _ = check.read_contract(PDIR)
    before = audit(contract)
    committed = json.load(open(GATE))["idiom_audit"]
    state = landed(contract)

    if state is False:
        after = audit(apply_edit(contract))
        print(f"{'key':<30} {'committed':>10} {'now':>6} {'PREDICTED':>10}")
        for k in KEYS:
            mark = "" if before.get(k) == committed.get(k) else "   <- DRIFT"
            print(f"{k:<30} {committed.get(k):>10} {before.get(k):>6} "
                  f"{after.get(k):>10}{mark}")
        print("\n⚠ `forbidden_hits` MUST stay 0 -- it is the half that FAILS "
              "the gate.")
        if after["forbidden_hits"]:
            print("  ⚠⚠ the simulated edit would FAIL the gate:", after["hits"])
        print("\nrequired entries that pin nothing after the edit "
              f"({after['required_pins_nothing']}):")
        for p in after["pins_nothing"]:
            print("   ", p)
        print(f"\nrequired entries scoped-absent after the edit "
              f"({after['required_absent']}):")
        for p in after["absent"]:
            print("   ", {k: p[k] for k in ("entry", "lang", "spelling")
                          if k in p}, "on:", p.get("on"), "off:", p.get("off"))
        return 0

    if state is None:
        print("⚠⚠ spec.md is in NEITHER image -- some edited entries carry the "
              "backticked span and some do not. Simulating would compare two "
              "different things, so nothing is simulated. Inspect by hand.")
        return 1

    # ---- POST-IMAGE: the edit landed. VERIFY instead of simulating. ---------
    print("=" * 70)
    print("ph29's spec.md is the POST-IMAGE: item 51's edit has LANDED, so the")
    print("simulation is meaningless and the PREDICTION is now CHECKABLE.")
    print("=" * 70)
    print(f"\n{'key':<30} {'committed':>10} {'re-run':>8} {'F72 predicted':>14}")
    for k in KEYS:
        want = PREDICTED.get(k)
        mark = ""
        if before.get(k) != committed.get(k):
            mark = "   <- DRIFT vs record"
        elif want is not None and committed.get(k) != want:
            mark = "   ⛔ MISSED"
        elif want is not None:
            mark = "   ✅"
        print(f"{k:<30} {committed.get(k):>10} {before.get(k):>8} "
              f"{'--' if want is None else want:>14}{mark}")
    miss = mismatches(committed)
    print()
    if miss:
        print(f"⛔⛔ {len(miss)} of {len(PREDICTED)} PUBLISHED PREDICTIONS MISSED:")
        for k, got, want in miss:
            print(f"     {k}: record {got}, F72 predicted {want}")
        print("   ▶ Either ph29 was re-gated or RECAP_PHP.md F72 is stale.")
        return 1
    print(f"✅ ALL {len(PREDICTED)} PUBLISHED PREDICTIONS LAND EXACTLY. F72's "
          f"prediction was falsifiable and was NOT falsified.")
    print("⚠ It buys the SPREAD SEARCH, not a check: `required` still cannot "
          "fail the gate (F72's own caveat).")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
