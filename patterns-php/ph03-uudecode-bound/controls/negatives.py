#!/usr/bin/env python3
"""ph03's negative controls -- the runs that must FAIL, regenerated on demand.

    python3 patterns-php/ph03-uudecode-bound/controls/negatives.py --list
    python3 patterns-php/ph03-uudecode-bound/controls/negatives.py --emit no2014

A gate that is green proves nothing on its own; what makes ph03's headline
checkable is that the two claims below have runs that go RED when the thing they
name is removed, and the mutants are derived from the shipped sources by this
script rather than kept as stale copies (`.memory/00-environment.md` constraint
6: keep the generator, delete the artefact).

⚠ The emitted file must be written INTO the row directory to compile -- both
`#[path = "../../common/driver.rs"]` and Verus's crate-name rules depend on
where it sits -- and it must be DELETED afterwards, or `gate.py`'s
`c_digest_audit` and `harness/measure.py` will see a source the record does not
pin. The commands below do both.

---------------------------------------------------------------- `no2014` ----
⚠⚠⚠ **THE ROW'S HEADLINE, AS A REFUSAL.** Deletes the FOUR LINES of PHP's 2014
fix `1e2818b14376` from `verus.rs`'s exec code -- `if e - s < 4 { err = true;
break; }` -- and nothing else. What is left is exactly the algorithm
`c/kernel_hardened.c` implements: `php_uudecode` plus the real 2004 fix
`f95c1df58349`. It must NOT verify.

    cp $(dirname $0)/../../..//dev/null /dev/null   # (no-op; see below)
    python3 controls/negatives.py --emit no2014 > ../verus_no2014_tmp.rs
    python3 verus_run.py .temp/php-root/patterns/ph03-uudecode-bound/verus_no2014_tmp.rs
    rm ../verus_no2014_tmp.rs

Recorded run (TASK_PHP_013, `.temp/php13/10-verus-negctl.log`):

    error: precondition not satisfied
       --> ...verus_no2014_tmp.rs:670:17
        |
    301 |         s + 4 <= off + len,
        |         ------------------ failed precondition
    ...
    670 |                 lemma_store_in_bounds(len as int, p as int, s as int, off as int);

    error: precondition not satisfied
       --> ...verus_no2014_tmp.rs:673:26
        |
    382 |         i < v@.len(),
        |         ------------ failed precondition
    ...
    673 |             let b1: u8 = get_unchecked(buf, s + 1);

    verification results:: 24 verified, 1 errors

⚠ Read the SECOND error, not the first: `i < v@.len()` on `get_unchecked(buf,
s + 1)` is the source over-read itself -- the same byte ASan reports at
`uuencode.c:144` in `controls/fix_incomplete.c`'s `fixed` arm, and the same one
`ext/standard/tests/strings/bug67252.phpt` reproduces. **The verifier refuses
the shipped 2004 fix for the reason the 2014 commit exists.**

-------------------------------------------- `no2004a` / `no2004a_both` ----
⚠⚠⚠ **THE FIRST CONTROL IN EITHER PROGRAMME WHOSE EXPECTATION IS THAT THE
MUTANT STILL VERIFIES**, and the reason it exists is a result rather than a
worry: `f95c1df58349`'s FIRST hunk decides nothing.

    `no2004a`       delete `if ln > src_len { err = true; break; }` from the
                    EXEC only, leaving `uu_walk`'s matching branch in the SPEC.
                    MUST STILL VERIFY -- 25 verified, 0 errors.
    `no2004a_both`  additionally make the SPEC branch unreachable (`ln` is
                    `dec_of(..)`, so `ln <= 63` and `ln > src_len + 64` is
                    false for every non-negative `src_len`).
                    MUST STILL VERIFY.

⚠ **`no2004a` alone is the decisive one, and it is worth saying why.** The spec
still refuses every `ln > src_len`, so an exec that has lost hunk 1 can only
satisfy the postcondition if some OTHER branch refuses exactly the same inputs.
It does: hunk 2. `line_len(ln) >= ln` for every `ln` in 1..63, and after `s++`
we have `e - s <= src_len - 1`, so `ln > src_len` forces `fl > e - s`.
`no2004a_both` is the same fact stated from the spec side.

Measured on the C side too (TASK_PHP_014 M5, `.temp/php14/06-hunk.c`), over the
same 12 600 documents as `.temp/php13/02-reach.log`: hunk 1 fires 1 953 times,
and hunk 2 would have refused **all 1 953** -- 0 documents are refused by hunk 1
alone.

⚠⚠ **A must-PASS control is weaker than a must-FAIL one and this file should
not pretend otherwise**: a mutant that verifies for the WRONG reason (a broken
emit, an anchor that matched nothing) also prints `25 verified, 0 errors`. Two
guards. The anchor-uniqueness check below refuses to emit when the anchor does
not occur exactly once, so a no-op edit cannot masquerade as a passing mutant;
and `no2014` shares the same emit path and is must-FAIL, so a `negatives.py`
that had stopped mutating anything at all would be caught there.

--------------------------------------------------------- `fix_incomplete` ----
The same fact on the C side, with a must-fire control. Not emitted by this
script -- it is a committed source, `controls/fix_incomplete.c`, because it is a
standalone program rather than a mutant of a shipped rung. Its header has the
build line; ../NOTES.md §5 has the recorded output.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)

# The exec text of `1e2818b14376`, exactly as `verus.rs` (and `unsafe.rs`,
# `safe_naive.rs`, `safe_tuned.rs`) spell it.
Y2014 = """            if e - s < 4 {
                err = true;
                break;
            }
"""

# `f95c1df58349` hunk 1, the EXEC copy (verus.rs's kernel loop).
Y2004A_EXEC = """        if ln > src_len {
            err = true;
            break;
        }
"""

# The same hunk in the SPEC (`uu_walk`). `ln` is `dec_of(..) as int`, so
# `ln <= 63`; `ln > src_len + 64` is therefore false for every `src_len >= 0`
# and the branch becomes unreachable WITHOUT introducing an `if false` that
# rustc would lint on.
Y2004A_SPEC_OLD = "        } else if ln > src_len {\n"
Y2004A_SPEC_NEW = "        } else if ln > src_len + 64 {\n"

# name -> (source, [(old, new), ...], expectation, why)
# ⚠ `expect` is "refuse" or "verify". A must-VERIFY mutant is a real control
# here -- see this file's docstring -- and it is why this table carries an
# expectation column at all rather than assuming every entry must go RED.
MUTANTS = {
    "no2014": ("verus.rs", [(Y2014, "")], "refuse",
               "delete PHP's 2014 fix 1e2818b14376; MUST NOT VERIFY"),
    "no2004a": ("verus.rs", [(Y2004A_EXEC, "")], "verify",
                "delete f95c1df58349 hunk 1 from the EXEC; MUST STILL VERIFY "
                "-- hunk 2 already refuses every input hunk 1 does"),
    "no2004a_both": ("verus.rs",
                     [(Y2004A_EXEC, ""),
                      (Y2004A_SPEC_OLD, Y2004A_SPEC_NEW)], "verify",
                     "and make the SPEC branch unreachable too; MUST STILL "
                     "VERIFY"),
}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--emit", metavar="NAME")
    a = ap.parse_args()
    if a.list or not a.emit:
        for k, (src, _edits, expect, why) in sorted(MUTANTS.items()):
            print(f"{k:14s} {src:11s} MUST {expect.upper():6s} {why}")
        return 0
    if a.emit not in MUTANTS:
        print(f"no such mutant: {a.emit}", file=sys.stderr)
        return 2
    src, edits, _expect, _why = MUTANTS[a.emit]
    txt = open(os.path.join(ROW, src)).read()
    # ⚠ Every anchor is checked BEFORE any is applied. One edit can destroy the
    # next one's anchor, and a partially applied mutant that still verifies is
    # exactly the false pass a must-VERIFY control is vulnerable to.
    for old, _new in edits:
        n = txt.count(old)
        if n != 1:
            print(f"controls/negatives.py: an {a.emit} anchor occurs {n} times "
                  f"in {src}, expected exactly 1 -- the mutant would be "
                  f"silently wrong. Fix the anchor before trusting any run.\n"
                  f"  anchor: {old!r}", file=sys.stderr)
            return 3
    for old, new in edits:
        txt = txt.replace(old, new, 1)
    sys.stdout.write(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
