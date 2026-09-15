#!/usr/bin/env python3
"""ph96 — does every backticked span in `spec.md`'s idiom entries actually PIN?

    python3 patterns-php/ph96-optarg-unwritten/controls/spellings.py
    python3 .../spellings.py --json <idiom.json>    # a candidate, before landing

=============================================================================
WHY THIS EXISTS
=============================================================================
⛔⛔ **A BACKTICK IN AN `idiom.required` OR `idiom.forbidden` ENTRY IS A PIN.**
`harness/check.py::idiom_audit` matches every backticked span against every rung
source that entry scopes to, after comments, string literals and Verus ghost
clauses are blanked and whitespace is deleted, and since `TASK_068` a
`forbidden` hit **FAILS the gate**. Item 100 records **three instances in three
consecutive tasks** of an entry whose backticks pinned nothing, or pinned a
token only one language can carry.

⭐ **IT WAS RUN ON THE CANDIDATE `idiom` BEFORE `spec.md` EXISTED**, which is
what `TASK_PHP_060` §3.4 asks for and what item 100's three instances did not
get. `../NOTES.md` section 13 records what the audit moved.

▶ `required` wants every scoped rung to MATCH; `forbidden` wants every one to
MISS. A `c`-keyed entry scopes to the two C kernels, a `rust`-keyed one to the
four Rust rungs, and a plain string to all six.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)
import check  # noqa: E402
import _pin  # noqa: E402
C_RUNGS = [("c/kernel.c", "c"), ("c/kernel_hardened.c", "c")]
R_RUNGS = [("safe_naive.rs", "rust"), ("safe_tuned.rs", "rust"),
           ("unsafe.rs", "rust"), ("verus.rs", "rust")]

BT = re.compile(r"`([^`]+)`")


def load(path=None):
    if path:
        return json.load(open(path))
    txt = open(os.path.join(ROW, "spec.md")).read()
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    return json.loads(m.group(1))["idiom"]


def scoped(entry_key):
    if entry_key == "c":
        return C_RUNGS
    if entry_key == "rust":
        return R_RUNGS
    return C_RUNGS + R_RUNGS


def negatives():
    """§H: MUST-FIRE and MUST-NOT-FIRE, so a matcher that stopped matching
    could not pass as a clean audit."""
    src = open(os.path.join(ROW, "c", "kernel.c")).read()
    rsrc = open(os.path.join(ROW, "safe_naive.rs")).read()
    out = []
    # N1 MUST-FIRE: a spelling that is only in a COMMENT must MISS. This one is
    # upstream's macro name, which `c/kernel.c` quotes in its header and spells
    # `ph96_call_method` in its code.
    n1 = not check.spelling_matches("zend_call_method_with_1_params", src, "c")
    print(f"  N1 MUST-FIRE  a comment-only spelling -> "
          f"{'MISS (ok)' if n1 else 'HIT (BAD)'}")
    if not n1:
        out.append("N1: a spelling that occurs only in a comment MATCHED, so "
                   "the matcher is not blanking comments and every verdict "
                   "below is about prose rather than code")
    # N2 MUST-FIRE: a CHARACTER LITERAL is blanked before matching, which is
    # §H1's rule with a LIVE instance on this row -- `is_true` really does
    # compare against b'0' in all four Rust rungs, and a pin on it could not fire.
    n2 = not check.spelling_matches("== b'0'", rsrc, "rust")
    print(f"  N2 MUST-FIRE  a character literal -> "
          f"{'MISS (ok)' if n2 else 'HIT (BAD)'}")
    if not n2:
        out.append("N2: a character literal MATCHED; §H1's whole point is that "
                   "the matcher blanks them, and a pin on one cannot fire")
    # N3 MUST-NOT-FIRE: a real spelling from the code MUST match.
    n3 = check.spelling_matches("(*zval_ptr)->refcount--", src, "c")
    print(f"  N3 MUST-NOT-FIRE a real spelling -> "
          f"{'HIT (ok)' if n3 else 'MISS (BAD)'}")
    if not n3:
        out.append("N3: a spelling that IS in the code did not match, so the "
                   "matcher is matching nothing and a clean audit means nothing")
    # N4 MUST-FIRE: whitespace is deleted from both sides.
    n4 = check.spelling_matches("(*zval_ptr)->refcount --", src, "c")
    print(f"  N4 MUST-FIRE  the same spelling, unspaced -> "
          f"{'HIT (ok)' if n4 else 'MISS (BAD)'}")
    if not n4:
        out.append("N4: whitespace is not being deleted, so the pins in "
                   "spec.md are spacing-sensitive and six p17 cells went out of "
                   "contract on two space characters once already")
    return out


def main():
    args = sys.argv[1:]
    idiom = load(args[1] if len(args) > 1 and args[0] == "--json" else None)
    problems = negatives()
    print()
    bad = 0
    total = 0
    for kind in ("required", "forbidden"):
        for i, entry in enumerate(idiom.get(kind, [])):
            parts = entry.items() if isinstance(entry, dict) else [(None, entry)]
            for key, text in parts:
                for sp in BT.findall(text):
                    for rel, lang in scoped(key):
                        src = open(os.path.join(ROW, rel)).read()
                        hit = check.spelling_matches(sp, src, lang)
                        want = (kind == "required")
                        ok = (hit == want)
                        total += 1
                        if not ok:
                            bad += 1
                        print(f"{'ok ' if ok else 'BAD'} {kind}[{i}]"
                              f"{'.' + key if key else '':6s} {rel:22s} "
                              f"{'HIT ' if hit else 'MISS'}  {sp!r}")
    print(f"\n{total} (spelling x rung) obligations, {bad} unsatisfied")
    if bad:
        problems.append(f"{bad} of {total} (spelling x rung) obligations are "
                        f"unsatisfied -- a `required` span that MISSES pins "
                        f"nothing and a `forbidden` span that HITS fails the gate")
    rec = {"obligations": total, "unsatisfied": bad, "problems": problems}
    rec.update(_pin.pin(["spec.md", "c/kernel.c", "c/kernel_hardened.c",
                         "safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                         "verus.rs"],
                        "python3 controls/spellings.py", "seconds"))
    with open(os.path.join(HERE, "spellings.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"wrote controls/spellings.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  \u26d4 " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
