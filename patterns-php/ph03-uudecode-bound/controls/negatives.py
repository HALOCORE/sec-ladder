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

MUTANTS = {
    "no2014": ("verus.rs", Y2014, "",
               "delete PHP's 2014 fix 1e2818b14376; MUST NOT VERIFY"),
}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--emit", metavar="NAME")
    a = ap.parse_args()
    if a.list or not a.emit:
        for k, (src, _o, _n, why) in sorted(MUTANTS.items()):
            print(f"{k:12s} {src:14s} {why}")
        return 0
    if a.emit not in MUTANTS:
        print(f"no such mutant: {a.emit}", file=sys.stderr)
        return 2
    src, old, new, _why = MUTANTS[a.emit]
    txt = open(os.path.join(ROW, src)).read()
    n = txt.count(old)
    if n != 1:
        print(f"controls/negatives.py: the {a.emit} anchor occurs {n} times in "
              f"{src}, expected exactly 1 -- the mutant would be silently wrong. "
              f"Fix the anchor before trusting any run.", file=sys.stderr)
        return 3
    sys.stdout.write(txt.replace(old, new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
