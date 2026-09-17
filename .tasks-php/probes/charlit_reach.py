#!/usr/bin/env python3
# =============================================================================
# charlit_reach.py -- THE PROBE **F73** RESTS ON, AND THE ONE `PROTOCOL_PHP.md`
# §H1 CITES AS ITS EVIDENCE
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr169/`, which is GITIGNORED.
# **F73** (`RECAP_PHP.md:1915`, landed 2026-09-11, commit 652c741) cites it by
# path with *"`--selftest` PASS, 6 must-fire"*, and its headline --
# **`0 of 33 PAT AND 0 of 6 PHP`** -- IS this file's output. `.memory-php/
# 04-process.md` LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17, commit f4bda71.
#
# ⚠⚠ SECOND CITATION, AND NO CHECKER WAS READING IT: `PROTOCOL_PHP.md` §H1 --
# a STANDING WRITING RULE -- cites `.temp/mgr169/charlit_reach.py` for the same
# figure. `probes/scratchdeps.py::scan_set` reads `RECAP_PHP.md` and
# `.memory-php/*.md` and NOTHING ELSE, so that citation was never in the law-11
# census at all. Same class as `F151` (`ph53/verus.rs`), at a new site.
#
# ⛔⛔⛔ RE-RUN ON PROMOTION, 2026-09-17, AND **THE HEADLINE HAS MOVED**:
#
#       PAT  patterns/      (33 rows)  ->  0 affected, 0 forbidden   UNCHANGED
#       PHP  patterns-php/  (14 rows)  ->  **1 affected**, 0 forbidden
#
# The one hit is `ph52-concat-copy-uninit` `required[0].rust`, spelling
# `` `ensures` ``, which `check.exec_code(..., "rust")` blanks to seven spaces.
# ▶ **THREE THINGS FOLLOW AND ALL THREE ARE THE POINT.**
#   (1) `F73`'s `0 of 6 PHP` is a 2026-09-11 snapshot over a 6-row corpus. It is
#       **`1 of 14` today**. Quote it with its date.
#   (2) `PROTOCOL_PHP.md` §H1's *"✅ LATENT, NOT LIVE: 0 affected spellings
#       across 33 PAT rows and 6 PHP rows"* is **no longer true of the php
#       half**. The DANGEROUS half of §H1 -- `forbidden`, a ban that cannot fire
#       -- is still **0**, so the rule's force is undiminished; only its
#       reassurance is stale.
#   (3) ⭐ **THE MECHANISM IS NOT A CHARACTER LITERAL.** `ensures` is a Verus
#       clause keyword that `exec_code`'s rust layer strips. §H1 is spelled
#       *"never backtick a spelling that contains a CHARACTER LITERAL"*, and
#       that spelling does not reach this case -- the hazard is *any span the
#       shipped blanker erases*, which is what THIS FILE actually tests and what
#       §H1's own title narrows. ⚠ Already visible in the gate record
#       (`ph52` `required_pins_nothing: 25`), so nothing is hidden -- but it is
#       visible only to a reader who distrusts the field.
#   ⓘ None of this is a defect in `ph52` and none of it fails a gate. It is a
#   published figure and a protocol reassurance going out of date together.
#
# RUN IT:  python3 .tasks-php/probes/charlit_reach.py --selftest  # 6 negatives
#          python3 .tasks-php/probes/charlit_reach.py             # both trees
# ⚠ Negatives are INLINE as well as flag-gated: a bare run runs them first and
# refuses to print if one fails. ⭐ The detector is DIFFERENTIAL -- it asks the
# shipped blanker whether the span changes, so it cannot drift from the matcher.
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. It imports `harness/check.py`
# and `harness/vparse.py` and reads each row's `spec.md`; all committed. It
# builds nothing, runs no binary and WRITES NOTHING. 0.5 s, 2026-09-17.
#
# ⛔ WHAT IS STILL OWED: (1) **F73 is UNREVIEWED**, and §H1 is an UNREVIEWED
# manager construction on top of it. (2) The count above is a REPORT, not an
# arm: nothing in this file FAILS when the php count moves off 0, so the drift
# recorded here was found by running it, not by a checker. ▶ An arm that pins
# `forbidden == 0` -- the half that fails a gate -- is the cheap next step and
# is NOT written here, because adding an arm to a promoted probe in the same
# pass that promotes it hides which behaviour was inherited.
# =============================================================================

"""How far does the char-literal blind spot reach? Both programmes, read-only.

FOUND AT ITEM 51. `harness/check.py::exec_code` layer 1 blanks "comments and
string/char literals" -- deliberate, documented in its own docstring, and right
for `"..."`. But a C CHARACTER literal is an executable operand, not text, so a
declared spelling that contains one can never match any rung:

    c/kernel.c:247   read_buf[recvd] = '\\0';        <- really is spelled
    exec_code        read_buf[recvd] =     ;         <- what the matcher sees

The consequence is the finding, not the behaviour:

  * in `required`, such an entry reports `pins nothing` -- visible, but only to
    a reader who knows to distrust it. ph29's `required[1].c` is exactly this
    and it names the row's OWN FAULT LINE.
  * in `forbidden`, such an entry is a BAN THAT CANNOT FIRE, and since
    TASK_068 `forbidden_hits` FAILS the gate, a dead ban is a check that
    silently cannot fail -- PROTOCOL_PHP.md §H's target, inside the frozen
    infrastructure.

So the question this answers is only: how many declared spellings contain a
char literal, and are any of them `forbidden`? ⚠ It answers nothing else. It
does not propose an `exec_code` change: that file is hashed into all 33 PAT
gate records and all 6 PHP ones (CLAUDE.md), so this is a REPORT.

⚠ The detector. A C char literal is `'...'`; the hard part is not confusing it
with a Rust LIFETIME (`&'a str`), which exec_code itself gets right. So the
test here is not a regex over the spelling -- it is differential and uses the
shipped blanker as its own oracle: a spelling contains blankable text iff
`blank_noncode` changes it. That cannot drift from what the matcher does,
because it IS what the matcher does.
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "harness"))
import check   # noqa: E402
import vparse  # noqa: E402

TICK = re.compile(r"`([^`]+)`")


def blanked(spelling, lang):
    """Does the shipped blanker erase any of `spelling`? Differential, not regex."""
    out = vparse.blank_noncode(spelling)
    if lang != "c":
        out = check.exec_code(spelling, lang)
    return out != spelling, out


def sweep(dirs):
    rows = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        try:
            contract, _ = check.read_contract(d)
        except Exception:
            continue
        idi = contract.get("idiom") or {}
        for key in ("required", "forbidden"):
            for i, e in enumerate(idi.get(key) or []):
                per = {"c": e, "rust": e} if isinstance(e, str) else e
                for lang, v in sorted(per.items()):
                    if lang not in ("c", "rust"):
                        continue
                    for tok in TICK.findall(v):
                        hit, out = blanked(tok, lang)
                        if hit:
                            rows.append({"row": os.path.basename(d),
                                         "entry": f"{key}[{i}].{lang}",
                                         "key": key, "tok": tok, "seen": out})
    return rows


def selftest():
    """Must-fire negatives: the detector must fire where it should and nowhere else."""
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    ck("P1 C char literal is caught", blanked("x = '\\0'", "c")[0], True)
    ck("P2 plain C spelling is not", blanked("to_read + 1", "c")[0], False)
    ck("P3 Rust lifetime is NOT caught",
       blanked("&'a [u8]", "rust")[0], False)
    ck("P4 Rust char literal is caught", blanked("c == 'z'", "rust")[0], True)
    ck("P5 a C string literal is caught too",
       blanked('puts("hi")', "c")[0], True)
    ck("P6 an ordinary Rust method chain is not",
       blanked("tr.wrapping_add(1)", "rust")[0], False)
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} ({len(fails)} failure(s))")
    return not fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if not selftest():
        print("\n⚠ selftest FAILED -- nothing below is believable")
        return 1
    print()

    for label, pat in (("PAT  patterns/", "patterns/p*"),
                       ("PHP  patterns-php/", "patterns-php/ph*")):
        dirs = sorted(glob.glob(os.path.join(ROOT, pat)))
        rows = sweep(dirs)
        ndirs = len([d for d in dirs if os.path.isdir(d)])
        print(f"=== {label}  ({ndirs} rows scanned) ===")
        if not rows:
            print("  no declared spelling contains blankable text")
        for r in rows:
            flag = "⚠⚠ DEAD BAN" if r["key"] == "forbidden" else "   pins nothing"
            print(f"  {flag}  {r['row']:<28} {r['entry']:<18} {r['tok']}")
            print(f"  {'':<14}  {'':<28} {'matcher sees:':<18} {r['seen']!r}")
        nf = sum(1 for r in rows if r["key"] == "forbidden")
        print(f"  -> {len(rows)} affected spelling(s), {nf} of them `forbidden`")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
