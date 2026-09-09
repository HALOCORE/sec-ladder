#!/usr/bin/env python3
"""ph07 -- UPSTREAM'S OWN REGRESSION TEST, run against all three guard
configurations. This is the control that decides which of them R1h is.

    python3 patterns-php/ph07-strcut-cursor/controls/bug49354.py

⭐⭐ **PHP DELETED HALF ITS OWN SECURITY FIX, AND SHIPPED A TEST THAT SAYS SO.**

`cb3cca21b345` (Ilia Alshanetsky, 2005-12-15, *"Fixed possible memory corruption
inside mb_strcut()"*) added TWO guards to `PHP_FUNCTION(mb_strcut)`:

    hunk (a)  if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }
    hunk (b)  if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1))
                  { len = Z_STRLEN_PP(arg1) - from; }

`c2471b495009` (Moriyoshi Koizumi, 2009-09-23) **removed hunk (b)** as bug
#49354, *"mb_strcut() cuts wrong length when offset is within a multibyte
character"*, and added `ext/mbstring/tests/bug49354.phpt` with it. The six
`--EXPECT--` lines below are that test, verbatim from
`controls/c2471b495009.patch`. ⚠ The removal was committed **three times in the
same second** -- `c2471b495009`, `0c974164e248`, `ce3c028803aa`, one per live
branch -- so it is not one branch's local decision.

**What this file runs.** A transcription of `PHP_FUNCTION(mb_strcut)`'s clamps
plus `mbfl_strcut`'s mblen_table arm, in three configurations:

⚠⚠⚠ **AND IT IS NOT INDEPENDENT OF `fix_scope.py`. THIS PARAGRAPH USED TO CLAIM
IT WAS, AND THAT WAS A FALSE DISCLOSURE** (`TASK_PHP_022` §5.3, re-measured at
`TASK_PHP_024` §1.5). It read *"deliberately a FIFTH spelling of the kernel,
**sharing no code with** `../model.py`, `../inputs/gen.py::_cut`, `fix_scope.py`
or any rung, so an agreement here is an independent one"*. What is actually
true, `diff`ed line for line:

    MBTAB              bug49354.py:51-53  vs fix_scope.py:55-57
                       BYTE-IDENTICAL, 3 lines, trailing `assert` included
    the caller clamps  bug49354.py:77-84  vs fix_scope.py:64-71
                       identical code, differing only in two trailing comments
    the end walk       bug49354.py:98-110 vs fix_scope.py:119-130
                       the same five statements; `fix_scope` reads through its
                       `at()` accounting helper where this file indexes `s`
                       directly and returns "OOB", and the comments differ

**So the two CAN agree for the same wrong reason** on the table, on the clamps
and on the shape of the walk. ✅ **The risk did not materialise, and it is not
this file that establishes that** -- three checks that share nothing with either
do: `model.py:576-628` re-derives all 256 `MBTAB` entries **from `c/kernel.c`'s
literal text** and fails the selfcheck on a mismatch (this file only asserts
`len == 256`); the differential against the row's **real C** --
`.temp/php22/bug49354/phpt_real_c.c`, which links `c/kernel.c` and
`c/kernel_hardened.c` themselves and folds their `u64` -- reproduces this table
**18 of 18 cells**, R1 wrong on case 6 only and R1h_ab on case 3 only (re-run at
`TASK_PHP_024`); and `TASK_PHP_022` §2.1/§2.4's independent transcription
reproduces `fix_scope` Q1's conclusion and `gen.py`'s window counts without
sharing a line with either.

⚠ **A false disclosure is worse than the thing it describes, because it is what
a reviewer trusts INSTEAD of re-checking** (`PROTOCOL.md` definition of done,
rule 6). **What is independent here is the ORACLE, not the model**: the six
`--EXPECT--` lines come out of upstream's own `.phpt` and out of nothing in this
repository, which is the property the control actually needs.

The three configurations:

    R1      php-5.0.0, no guards at all              <- ../c/kernel.c
    R1h_ab  + hunk (a) AND hunk (b)                  <- php-5.1.2 .. php-5.2.11
    R1h     + hunk (a) ALONE                         <- php-5.2.12 .. php-5.2.17
                                                        ../c/kernel_hardened.c

⚠⚠ **IT IS A MUST-FIRE CONTROL AND IT EXITS NON-ZERO IF IT STOPS FIRING.**
`R1h_ab` MUST disagree with upstream (that is bug #49354) and `R1h` MUST agree
(that is what upstream kept). If `R1h_ab` ever agreed, hunk (b) would be a
no-op, its removal would not have been a bug fix, and `TASK_PHP_018`'s whole
argument for changing this row's R1h would be wrong.

⭐ **AND IT SEPARATES THE TWO DEFECTS.** Case 3 is where hunk (b) returns the
wrong cut; case 6 is where R1 walks past `val[slen]`. They are different rows of
the table and different configurations fail them, which is the cleanest
statement this row has that *(a) is the memory-safety half and (b) is not*.
`fix_scope.py` Q1/Q2 puts the same fact in numbers over 133 932 calls.
"""

import sys

# ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56, as a run-length.
MBTAB = tuple(([1] * 192) + ([2] * 32) + ([3] * 16)
              + ([4] * 8) + ([5] * 4) + ([6] * 2) + ([1] * 2))
assert len(MBTAB) == 256

# ext/mbstring/tests/bug49354.phpt, verbatim from c2471b495009.patch.
#   $crap = 'AåBäCöDü';   -- 8 characters, 12 UTF-8 bytes
CRAP = 'AåBäCöDü'.encode('utf-8')
CASES = [
    (0,  100, 'string(12) "AåBäCöDü"'),
    (1,  100, 'string(11) "åBäCöDü"'),
    (2,  100, 'string(11) "åBäCöDü"'),
    (3,  100, 'string(9) "BäCöDü"'),
    (12, 100, 'string(0) ""'),
    (13, 100, 'bool(false)'),
]

CONFIGS = [("R1     ", False, False),   # php-5.0.0            -- c/kernel.c
           ("R1h_ab ", True,  True),    # php-5.1.2..5.2.11    -- WITHDRAWN
           ("R1h    ", True,  False)]   # php-5.2.12..5.2.17   -- SHIPPED


def strcut(s, slen, frm, length, hunk_a, hunk_b):
    """mbstring.c:1787-1805's clamps, then the optional guards, then
    mbfilter.c:1179-1259's mblen_table arm. `s` carries the zval terminator at
    index `slen`, exactly as `emalloc(len + 1)` does. Returns the cut bytes,
    `None` for `RETURN_FALSE`, or `"OOB"` if the walk leaves the buffer."""
    if frm < 0:                                   # mbstring.c:1787-1793
        frm = slen + frm
        if frm < 0:
            frm = 0
    if length < 0:                                # mbstring.c:1795-1801
        length = (slen - frm) + length
        if length < 0:
            length = 0
    if hunk_a and frm > slen:
        return None
    if hunk_b and frm + length > slen:
        length = slen - frm
    n = start = 0
    while True:                                   # mbfilter.c:1202-1210
        if n > slen:
            return "OOB"
        m = MBTAB[s[n]]
        n += m
        if n > frm:
            break
        start = n
    k = start + length                            # mbfilter.c:1212
    if k >= slen:
        end = slen
    else:
        end = start
        while n <= k:                             # mbfilter.c:1217-1222
            end = n
            if n > slen:
                return "OOB"
            n += MBTAB[s[n]]
    start = min(max(start, 0), slen)              # mbfilter.c:1227-1241
    end = min(max(end, 0), slen)
    start = min(start, end)
    return s[start:end]


def render(r):
    """PHP's `var_dump` spelling, so the comparison is against the `.phpt`
    text and not against a re-encoding of it."""
    if r is None:
        return 'bool(false)'
    if r == "OOB":
        return '<<OUT-OF-BOUNDS READ>>'
    return f'string({len(r)}) "{r.decode("utf-8", "replace")}"'


def main():
    s = CRAP + b"\0"
    slen = len(CRAP)
    fails = {name: 0 for name, _, _ in CONFIGS}
    print("ph07 controls/bug49354.py -- ext/mbstring/tests/bug49354.phpt, "
          "added by c2471b495009")
    print(f"  $crap = {CRAP!r}   ({slen} bytes, 8 characters)\n")
    head = f"  {'call':30s} {'--EXPECT--':27s}"
    print(head + "".join(f"{n:27s}" for n, _, _ in CONFIGS))
    for frm, length, want in CASES:
        got = [render(strcut(s, slen, frm, length, a, b))
               for _, a, b in CONFIGS]
        for (name, _, _), g in zip(CONFIGS, got):
            if g != want:
                fails[name] += 1
        call = f"mb_strcut($crap,{frm},{length})"
        print(f"  {call:30s} {want:27s}"
              + "".join(f"{g if g == want else g + ' <-WRONG':27s}"
                        for g in got))
    print()
    for name, _, _ in CONFIGS:
        verdict = ("AGREES with upstream on all 6" if not fails[name]
                   else f"{fails[name]} of {len(CASES)} answers WRONG")
        print(f"  {name}: {verdict}")

    ok_ab = fails["R1h_ab "] > 0
    ok_a = fails["R1h    "] == 0
    ok_r1 = fails["R1     "] > 0
    print()
    print(f"  MUST FIRE     R1h_ab disagrees (this IS bug #49354)   "
          f"{'ok' if ok_ab else 'FAILED'}")
    print(f"  MUST NOT FIRE R1h agrees (what upstream kept)          "
          f"{'ok' if ok_a else 'FAILED'}")
    print(f"  MUST FIRE     R1 over-reads on case 6 (CRASH-124)      "
          f"{'ok' if ok_r1 else 'FAILED'}")
    print()
    print("  ⭐ Case 3 and case 6 are DIFFERENT defects in DIFFERENT "
          "configurations:")
    print("     case 3 is hunk (b) cutting the wrong length -- a correctness "
          "bug, and the")
    print("       reason upstream removed it;")
    print("     case 6 is R1 walking past val[slen] -- CRASH-124, and the "
          "reason hunk (a)")
    print("       exists. Hunk (a) alone fixes case 6 and leaves case 3 "
          "correct. That is")
    print("     the whole argument for this row's R1h, in six lines of "
          "upstream's own test.")
    rc = 0 if (ok_ab and ok_a and ok_r1) else 1
    print("\n  CONTROL:", "as declared" if rc == 0
          else "*** A CONFIGURATION DID NOT BEHAVE -- see spec.md "
               "idiom.required[4] ***")
    return rc


if __name__ == "__main__":
    sys.exit(main())
