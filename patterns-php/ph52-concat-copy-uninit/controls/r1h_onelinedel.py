#!/usr/bin/env python3
"""ph52 control: R1h IS `c/kernel.c` MINUS ONE STATEMENT, and this is the check.

    python3 patterns-php/ph52-concat-copy-uninit/controls/r1h_onelinedel.py
    python3 .../r1h_onelinedel.py --write      # regenerate c/kernel_hardened.c
    python3 .../r1h_onelinedel.py --selftest   # the must-fire / must-NOT-fire suite

⚠⚠⚠ **WHY THIS EXISTS, AND IT IS `PROTOCOL_PHP.md` §C's OWED ARGUMENT MADE
MECHANICAL.** `ph53`'s `c/kernel_hardened.c` is a `patch -p1` of its
`fix_commit` at zero fuzz; **ph52's CANNOT BE.** `7412202c43e7` (Antony Dovgal,
2006-05-11, *"no need to destroy the zval here"*) deletes

    -\t\t\t\tzval_dtor(expr_copy);

from a 2006 `Zend/zend.c` whose CONTEXT lines name `STR_EMPTY_ALLOC()` and
`E_RECOVERABLE_ERROR` -- **two tokens that do not exist anywhere in the 5.0.0
tarball** (measured: 0 occurrences across `Zend/zend.h`, `zend_variables.h`,
`zend_API.h`, `zend_operators.h` and `zend_errors.h`). So `patch` has nothing to
match and §C is satisfied by a HAND RECONSTRUCTION, which §C says owes an
argument in writing.

▶ **THE ARGUMENT THIS FILE MAKES CHECKABLE:** the hardened kernel differs from
the plain one by exactly the deletion of ONE STATEMENT, `ph52_zval_dtor(expr_copy);`
at the site that stands for `zend.c:243`, plus the two header/comment blocks that
say so. Not *"a one-line change"* as prose -- `--selftest` drives it.

⭐ **AND THE DELETED TOKEN SEQUENCE IS BYTE-IDENTICAL TO THE COMMIT's, UP TO ONE
TAB.** The commit's removed line is `\\t\\t\\t\\tzval_dtor(expr_copy);\\n` (4 tabs);
5.0.0's `:243` is `\\t\\t\\t\\t\\tzval_dtor(expr_copy);\\n` (5 tabs), because by 2006 the
arm had lost one level of nesting. `..\\/NOTES.md` §3 has the `od -c` of both.

⚠ `--selftest`'s negatives are NEW to this row and not inherited
(`.memory-php/04-process.md` law 7).
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
PLAIN = os.path.join(ROW, "c", "kernel.c")
HARD = os.path.join(ROW, "c", "kernel_hardened.c")

#: The statement `7412202c43e7` deletes, as this kernel spells it. ⚠ NO CHARACTER
#: LITERAL in it, per `PROTOCOL_PHP.md` §H1 -- a backticked spelling containing one
#: is a check that cannot fail, and the same hazard applies to a matcher here.
DELETED_STMT = "ph52_zval_dtor(expr_copy);"

#: The block `c/kernel.c` carries at the deletion site, and what replaces it.
PLAIN_BLOCK = """                /* ⛔⛔ THE DEFECT.  `expr_copy->type` has not been written by
                 * ANY path that reaches here, and `ph52_zval_dtor` dispatches on
                 * it and frees a pointer read out of the same slot. */
                ph52_zval_dtor(expr_copy);                        /* :243 */
"""

HARD_BLOCK = """                /* ⭐ `7412202c43e7` DELETED THE LINE THAT WAS HERE:
                 *
                 *     ph52_zval_dtor(expr_copy);                  :243
                 *
                 * There is nothing to destroy: no path that reaches this arm has
                 * written `expr_copy`. */
"""

PLAIN_HDR = """/* ph52 rung R1 -- PHP 5.0.0's `concat_function` / `zend_make_printable_zval`,
 * NARROWED.  THE BUG (corpus row LOGIC-007, CWE-457 / CWE-824).
 *"""

HARD_HDR = """/* ph52 rung R1h -- c/kernel.c WITH `7412202c43e7` APPLIED.  THE FIX.
 *
 * ============================================================================
 * ⚠⚠⚠ THE WHOLE DIFF AGAINST c/kernel.c IS ONE DELETED STATEMENT
 * ============================================================================
 *     -                ph52_zval_dtor(expr_copy);                    :243
 *
 * `7412202c43e7` -- Antony Dovgal, 2006-05-11, "no need to destroy the zval
 * here", `Zend/zend.c`, 1 file, 1 hunk, 0 insertions, 1 deletion.
 *
 * ⚠⚠ IT IS A HAND RECONSTRUCTION AND NOT A `patch -p1`, AND ../spec.md's
 * `provenance.fix_commit_note` ACCOUNTS FOR EVERY TOKEN THAT DIFFERS.  The
 * DELETED STATEMENT is byte-identical to 5.0.0's `:243` up to one tab of
 * indentation; what does not match is the commit's CONTEXT, because by 2006 the
 * enclosing arm had been restructured and uses two tokens that do not exist in
 * 5.0.0 at all (`STR_EMPTY_ALLOC()` and `E_RECOVERABLE_ERROR`).
 *
 * ⭐ AND THE DELETION IS COMPLETE.  `zend.c:243` is the ONLY line in
 * `zend_make_printable_zval` that READS `expr_copy` with no write to it earlier
 * on the same path: every other read (`:210`, `:214`, `:250`, `:254`, `:259`,
 * `:260`) reads a field written one or two lines above, `:253`/`:258` are
 * whole-struct writes, `:222` is inside the `#if 0` at `:220-228`, and `:263`
 * -- `expr_copy->type = IS_STRING` -- sits AFTER the switch, so every path that
 * leaves the function has written the tag.  Deleting `:243` therefore leaves no
 * path that tears down an unconstructed slot.  ../spec.md and ../NOTES.md §3.
 *
 * ⚠ `controls/r1h_onelinedel.py` IS THIS CLAIM AS A CHECK, not as prose: it
 * regenerates this file from c/kernel.c and refuses any other difference.
 *
 * Everything below is c/kernel.c, unchanged.
 *
 * ---------------------------------------------------------------------------
 *
""" + PLAIN_HDR[2:]


def derive(plain):
    """c/kernel.c -> c/kernel_hardened.c. The ONLY transformation."""
    if PLAIN_HDR not in plain:
        raise SystemExit("c/kernel.c does not carry the expected R1 header")
    if plain.count(PLAIN_BLOCK) != 1:
        raise SystemExit(f"c/kernel.c carries the deletion site "
                         f"{plain.count(PLAIN_BLOCK)} times, expected 1")
    return plain.replace(PLAIN_HDR, HARD_HDR).replace(PLAIN_BLOCK, HARD_BLOCK)


def strip_comments(txt):
    """Blank `/* ... */` comments, so the comparison is over CODE.

    ⚠ Deliberately not a full C lexer: this kernel contains no string literal
    carrying `/*` and `--selftest` case N5 is what says so."""
    return re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)


def code_diff(plain, hard):
    """The list of (plain_line, hard_line) positions where the CODE differs.

    Returns `(only_in_plain, only_in_hard)` as lists of stripped lines."""
    a = [ln.strip() for ln in strip_comments(plain).splitlines() if ln.strip()]
    b = [ln.strip() for ln in strip_comments(hard).splitlines() if ln.strip()]
    import difflib
    minus, plus = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag in ("replace", "delete"):
            minus += a[i1:i2]
        if tag in ("replace", "insert"):
            plus += b[j1:j2]
    return minus, plus


def check(plain, hard):
    """Problems with the claim *R1h is R1 minus one statement*."""
    bad = []
    if hard != derive(plain):
        bad.append("c/kernel_hardened.c is NOT `derive(c/kernel.c)` -- run "
                   "--write, or the two kernels differ by more than the deletion")
    minus, plus = code_diff(plain, hard)
    if plus:
        bad.append(f"R1h ADDS code the plain kernel does not have: {plus}")
    if len(minus) != 1:
        bad.append(f"R1h deletes {len(minus)} code line(s), expected exactly 1: "
                   f"{minus}")
    elif DELETED_STMT not in minus[0]:
        bad.append(f"the deleted line is {minus[0]!r}, which does not contain "
                   f"{DELETED_STMT!r}")
    if DELETED_STMT + "  " not in plain and DELETED_STMT not in plain:
        bad.append("c/kernel.c does not contain the statement at all")
    # the statement must survive NOWHERE in the hardened kernel's CODE
    if DELETED_STMT in strip_comments(hard):
        bad.append("the deleted statement is still present in R1h's CODE")
    # ... and it must still be named in R1h's COMMENTS, so a reader finds it
    if DELETED_STMT not in hard:
        bad.append("R1h does not name the deleted statement anywhere, so a "
                   "reader cannot see what the fix was")
    return bad


# ---------------------------------------------------------------------------
# §H: a validator lands with its negatives, or it does not land.
# ⚠ NEW to this row. `.memory-php/04-process.md` law 7: a control cloned between
# rows carries its defects, and only the row that writes NEW negatives finds them.
# ---------------------------------------------------------------------------
def selftest():
    plain = open(PLAIN).read()
    hard = open(HARD).read()
    fails = []

    def expect(name, ps, want_bad, why):
        got = bool(ps)
        if got != want_bad:
            fails.append(f"{name}: expected {'problems' if want_bad else 'clean'},"
                         f" got {ps if ps else 'clean'}   [{why}]")
        return got

    # N0  MUST-NOT-FIRE: the shipped pair
    expect("N0 shipped pair", check(plain, hard), False,
           "the committed kernels must pass")

    # N1  MUST-FIRE: R1h identical to R1 -- the fix not applied at all
    expect("N1 fix not applied", check(plain, plain), True,
           "a hardened kernel that still calls the teardown is not the fix")

    # N2  MUST-FIRE: R1h deletes the :1188 teardown as well
    h2 = hard.replace("ph52_zval_dtor(&op1_copy);", "(void)0;", 1)
    expect("N2 second deletion", check(plain, h2), True,
           "deleting `:1188` too would be a DIFFERENT fix and must be refused")

    # N3  MUST-FIRE: R1h adds a guard instead of deleting the call
    h3 = hard.replace(HARD_BLOCK,
                      "                if (expr_copy->type == PH52_IS_STRING) "
                      "{ ph52_zval_dtor(expr_copy); }\n")
    expect("N3 guard instead of deletion", check(plain, h3), True,
           "a hand-written guard is not `7412202c43e7` and stage 7h would not "
           "notice")

    # N4  MUST-FIRE: the statement survives only inside a comment -- which is
    #     ALLOWED -- but ALSO in the code. The checker must look at CODE.
    h4 = hard.replace("                 * written `expr_copy`. */",
                      "                 * written `expr_copy`. */\n"
                      "                ph52_zval_dtor(expr_copy);")
    expect("N4 statement back in the code", check(plain, h4), True,
           "`strip_comments` must not be fooled by the comment that names it")

    # N5  MUST-NOT-FIRE: the comment block naming the deleted statement is the
    #     shipped shape, so a checker that counted TEXT occurrences would fire.
    expect("N5 comment naming it is fine", check(plain, hard), False,
           "R1h is REQUIRED to name the statement in a comment")

    # N6  MUST-FIRE: the headers swapped, so R1h claims to be R1
    expect("N6 header not swapped", check(plain, hard.replace(HARD_HDR, PLAIN_HDR)),
           True, "the provenance header is part of the derivation")

    # N7  MUST-FIRE: a whitespace-only change elsewhere in the kernel
    h7 = hard.replace("    php_shim_reset();", "    php_shim_reset() ;")
    expect("N7 unrelated code change", check(plain, h7), True,
           "ANY other code difference between the two kernels must be refused")

    # N8  MUST-NOT-FIRE: a COMMENT-only change elsewhere is not a code change
    #     -- but it IS a derive() mismatch, which is the stricter half. Recorded
    #     so the two halves are not confused.
    h8 = hard.replace("/* PROTOCOL_PHP.md B1.3 */", "/* PROTOCOL_PHP.md B1.3. */")
    minus8, plus8 = code_diff(plain, h8)
    if len(minus8) != 1 or plus8:
        fails.append(f"N8: a comment-only edit moved the CODE diff to "
                     f"{len(minus8)}/-{len(plus8)}+, which means strip_comments "
                     f"is not doing its job")
    if not check(plain, h8):
        fails.append("N8: a comment-only edit must still fail `derive`, because "
                     "the hardened kernel is GENERATED")

    # N9  MUST-FIRE: `derive` fed a plain kernel with TWO deletion sites
    try:
        derive(plain + PLAIN_BLOCK)
        fails.append("N9: derive() accepted a kernel with two deletion sites")
    except SystemExit:
        pass

    # N10 MUST-FIRE: `derive` fed a plain kernel with NONE
    try:
        derive(plain.replace(PLAIN_BLOCK, ""))
        fails.append("N10: derive() accepted a kernel with no deletion site")
    except SystemExit:
        pass

    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="regenerate c/kernel_hardened.c from c/kernel.c")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    plain = open(PLAIN).read()
    if a.write:
        open(HARD, "w").write(derive(plain))
        print(f"  wrote {os.path.relpath(HARD, ROW)} from c/kernel.c")
    hard = open(HARD).read()

    if a.selftest:
        fails = selftest()
        print(f"  --selftest: 11 cases (8 must-fire, 3 must-NOT-fire)")
        for f in fails:
            print(f"    FAIL {f}")
        print("  --selftest PASS" if not fails else "  --selftest FAILED")
        return 1 if fails else 0

    probs = check(plain, hard)
    minus, plus = code_diff(plain, hard)
    print(f"  c/kernel.c  -> c/kernel_hardened.c")
    print(f"  code lines only in R1  : {len(minus)}  {minus}")
    print(f"  code lines only in R1h : {len(plus)}   {plus}")
    for p in probs:
        print(f"    PROBLEM {p}")
    print("  ok: R1h is R1 minus exactly one statement"
          if not probs else "  REFUSED")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
