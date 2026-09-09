#!/usr/bin/env python3
"""ph07 -- what each upstream guard actually buys, measured rather than argued.

    python3 patterns-php/ph07-strcut-cursor/controls/fix_scope.py

`PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically correct ... That is
a result, and one of the strongest a row can carry."* This file is where that
gets a number instead of a sentence, and it is also where the two things the
gate cannot hold live:

  * `check.py` stage 7h requires R1h to be clean on every input AND
    byte-identical to R1 on every non-adversarial one, so a corpus on which the
    fix CHANGES a benign answer cannot be shipped in `inputs/`. ⭐ Until
    `TASK_PHP_018` that was read as a harness limitation and worked around by
    restricting `inputs/gen.py`; Q2 is what showed it was not. **Stage 7h was
    right**: what it refused is the configuration upstream itself withdrew.
  * `inputs/` is five files. Q1 and Q3 range over 133 932 calls.

An OFFSET interpreter of the extracted walk -- it never holds a pointer, so it
can RECORD an access it does not perform, which is the only way to count reads
that would be out of bounds. Model of the source, exactly as PHP shapes it: a
zval string is `emalloc(slen + 1)` with `val[slen] == '\\0'`, so

    index  0 .. slen-1   the string
    index  slen          the NUL terminator          -- IN the allocation
    index  slen+1 ..     OUT OF BOUNDS               -- what Q1 counts

The variants, and every one of them is a real historical program:

    R1      mbfilter.c:1179-1259 as shipped in php-5.0.0 .. php-5.3.2
    R1h     + cb3cca21b345 hunk (a) ALONE, `from > len` -> RETURN_FALSE
              = php-5.2.12 .. php-5.2.17          <- c/kernel_hardened.c
    R1h_ab  + cb3cca21b345 hunks (a) AND (b)
              = php-5.1.2 .. php-5.2.11           <- WITHDRAWN by c2471b495009
    R1_2010 + d9dda48f8a7e's PROLOGUE `from >= len` -> `from = len`, 5.3.3+
    R1_walk + d9dda48f8a7e's REWRITTEN start walk, prologue NOT applied

⭐ `R1_walk` is here because it is the variant everybody guesses is the fix.
It is not.

⚠⚠ **THE LABELS `R1h` AND `R1h_a` SWAPPED MEANING AT `TASK_PHP_018`, AND THAT
IS THE POINT OF THE TASK.** Until then `R1h` meant both hunks, `R1h_a` meant
hunk (a) alone, and the row SHIPPED the former. `c2471b495009` (2009-09-23)
removed hunk (b) upstream as **bug #49354** and this row followed, so `R1h`
now means what the row ships and `R1h_ab` is the withdrawn configuration kept
here as evidence. ⚠ Older logs under `.temp/php16/` and `.temp/php17/` use the
OLD names; read `R1h_a` there as `R1h` here. Q1's and Q2's NUMBERS are
unchanged -- only which column is called what.
"""

import itertools
import os
import sys

MBTAB = tuple(([1] * 192) + ([2] * 32) + ([3] * 16)
              + ([4] * 8) + ([5] * 4) + ([6] * 2) + ([1] * 2))
assert len(MBTAB) == 256

VARIANTS = ("R1", "R1h", "R1h_ab", "R1_2010", "R1_walk")


def guard(slen, frm, length):
    """mbstring.c:1787-1805 -- the CALLER's two clamps, both from below."""
    if frm < 0:
        frm = slen + frm
        if frm < 0:
            frm = 0
    if length < 0:
        length = (slen - frm) + length
        if length < 0:
            length = 0
    return frm, length


def run(s, slen, frm, length, mode, filler=0x00):
    """(answer, max_index_read).

    `answer` is `(start, end, bytes)` or the string `"FALSE"`.
    `filler` is what the interpreter finds PAST the allocation; Q3 varies it."""
    maxread = -1

    def at(i):
        nonlocal maxread
        if i > maxread:
            maxread = i
        return s[i] if i < len(s) else filler

    if mode in ("R1h", "R1h_ab"):
        if frm > slen:                       # cb3cca21b345 hunk (a) -- SHIPPED
            return "FALSE", maxread
    if mode == "R1h_ab":
        if frm + length > slen:              # hunk (b) -- WITHDRAWN, c2471b495009
            length = slen - frm
    if mode == "R1_2010":
        if frm >= slen:                      # d9dda48f8a7e prologue
            frm = slen

    n = 0
    start = 0
    if mode == "R1_walk":
        # d9dda48f8a7e's rewritten start walk: test BEFORE read.
        #   for (m = 0, p = val, q = p + from; p < q; p += (m = mbtab[*p]));
        #   if (p > q) { p -= m; }
        m = 0
        while n < frm:
            m = MBTAB[at(n)]
            n += m
        if n > frm:
            n -= m
        start = n
    else:
        while True:                          # mbfilter.c:1202-1210
            m = MBTAB[at(n)]
            n += m
            if n > frm:
                break
            start = n

    k = start + length                       # mbfilter.c:1212
    if k >= slen:
        end = slen
    else:
        end = start
        while n <= k:                        # mbfilter.c:1217-1222, BOUNDED
            end = n
            n += MBTAB[at(n)]

    start = min(max(start, 0), slen)         # mbfilter.c:1227-1241
    end = min(max(end, 0), slen)
    start = min(start, end)
    return (start, end, bytes(s[start:end])), maxread


def corpus():
    """Strings spanning the lead-byte classes the table has, and the empty one."""
    fam = {
        "ascii": bytes(0x41 + (i % 26) for i in range(48)),
        "2byte": bytes((0xC3, 0xA9) * 24),
        "3byte": bytes((0xE3, 0x81, 0x82) * 16),
        "mixed": bytes(b"ab\xc3\xa9\xe3\x81\x82z" * 6),
        "4byte": bytes((0xF0, 0x9F, 0x98, 0x80) * 12),
        "wide":  bytes((0xFC, 1, 2, 3, 4, 5) * 8),
    }
    for name, b in fam.items():
        for slen in (0, 1, 2, 3, 5, 8, 13, 21, 34, 48):
            yield f"{name}/{slen}", bytes(b[:slen]) + b"\0"


def calls():
    for label, s in corpus():
        slen = len(s) - 1
        for fr, ln in itertools.product(range(-slen - 2, slen + 9),
                                        range(-slen - 2, slen + 5)):
            frm, length = guard(slen, fr, ln)
            yield label, s, slen, frm, length


def q1():
    print("Q1  over-reads and answer changes, by variant")
    tot = oob = {}
    tot = 0
    oob = {v: 0 for v in VARIANTS}
    diff = {v: 0 for v in VARIANTS}
    first = {}
    hunk_a = hunk_b = 0
    for label, s, slen, frm, length in calls():
        tot += 1
        hunk_a += (frm > slen)
        hunk_b += (frm <= slen and frm + length > slen)
        base = None
        for v in VARIANTS:
            ans, mx = run(s, slen, frm, length, v)
            if v == "R1":
                base = ans
            elif ans != base:
                diff[v] += 1
            if mx > slen:
                oob[v] += 1
                first.setdefault(v, (label, frm, length, mx, slen))
    print(f"    calls interpreted                     : {tot}")
    print(f"    cb3cca21b345 hunk (a) would fire      : {hunk_a}")
    print(f"    cb3cca21b345 hunk (b) would fire      : {hunk_b}"
          f"   (with (a) not firing)")
    print()
    print(f"    {'variant':9s} {'reads past val[slen]':>21s} "
          f"{'answer != R1':>13s}")
    for v in VARIANTS:
        print(f"    {v:9s} {oob[v]:21d} {diff[v]:13d}"
              + (f"   first oob: {first[v]}" if v in first else ""))
    return oob, diff


def q2():
    """⭐ Does the security fix change the answer on calls that never crashed?"""
    print()
    print("Q2  hunk (b)'s SEMANTIC change, on calls where NOTHING is out of "
          "bounds")
    safe = changed = 0
    example = None
    for label, s, slen, frm, length in calls():
        a_only, mx = run(s, slen, frm, length, "R1h")
        if mx > slen or a_only == "FALSE":
            continue                      # not a benign, non-refused call
        safe += 1
        both, _ = run(s, slen, frm, length, "R1h_ab")
        if both != a_only:
            changed += 1
            if example is None:
                example = (label, frm, length, a_only, both)
    print(f"    calls that neither over-read nor hit hunk (a) : {safe}")
    print(f"    of those, hunk (b) CHANGES the answer         : {changed}"
          f"   ({100.0 * changed / max(safe, 1):.1f} %)")
    if example:
        lb, fr, ln, a, b = example
        print(f"    e.g. {lb} from={fr} length={ln}")
        print(f"         (a) alone -> start={a[0]} end={a[1]} len={a[1]-a[0]}")
        print(f"         (a)+(b)   -> start={b[0]} end={b[1]} len={b[1]-b[0]}")
    print("    ⚠⚠ UNTIL TASK_PHP_018 THIS NUMBER WAS THE REASON "
          "inputs/gen.py REFUSED a window")
    print("       with `from + length > string->len`. It is now the reason "
          "R1h DOES NOT CARRY")
    print("       hunk (b), and gen.py REQUIRES such windows: the same "
          "measurement, read the")
    print("       other way round. check.py stage 7h was detecting a real "
          "defect, not")
    print("       obstructing a real fix.")
    print("    ⭐ Upstream itself withdrew hunk (b): c2471b495009 (2009-09-23, "
          "bug #49354),")
    print("       so php-5.2.12 .. php-5.2.17 carry (a) alone. "
          "controls/bug49354.py runs")
    print("       upstream's own six expectations against all three "
          "configurations.")
    return changed


def q3():
    """⭐ Is R1's ANSWER affected by the bytes it reads out of bounds?"""
    print()
    print("Q3  does R1's RETURN VALUE depend on the out-of-bounds bytes?")
    fillers = (0x00, 0x41, 0xC3, 0xE3, 0xF0, 0xFC, 0xFF)
    unstable = 0
    checked = 0
    for label, s, slen, frm, length in calls():
        ans0, mx = run(s, slen, frm, length, "R1", filler=fillers[0])
        if mx <= slen:
            continue
        checked += 1
        for f in fillers[1:]:
            ansf, _ = run(s, slen, frm, length, "R1", filler=f)
            if ansf != ans0:
                unstable += 1
                break
    print(f"    over-reading calls re-run under 7 different fillers : {checked}")
    print(f"    calls whose answer MOVED                            : "
          f"{unstable}")
    print("    mechanism: `start` is assigned the cursor of the iteration "
          "BEFORE the break,")
    print("      so the first read at index i > slen happens with "
          "`start == i > slen` already")
    print("      set; `start` only grows; mbfilter.c:1227 then forces "
          "start = end = slen.")

    # ⚠⚠ MUST-FIRE CONTROL, AND THE FIRST ONE WRITTEN HERE DID NOT FIRE.
    # It moved `start = n` past the break test, so `start` took the cursor that
    # had read out of bounds -- and the answer STILL did not move, because
    # mbfilter.c:1227's `if (start > len) { start = len; }` erased the
    # difference. **That is the mechanism, not a failed control**: the clamp
    # that arrives too late to prevent the over-read is exactly the clamp that
    # HIDES it. So the control that does fire is the one that deletes it --
    # `:1227-1229` and `:1239-1241` -- and reports `start` raw. If this prints
    # 0 the probe is measuring nothing and Q3's zero means nothing.
    def run_mut(s, slen, frm, length, filler):
        maxread = -1

        def at(i):
            nonlocal maxread
            if i > maxread:
                maxread = i
            return s[i] if i < len(s) else filler
        n = start = 0
        while True:
            m = MBTAB[at(n)]
            n += m
            if n > frm:
                break
            start = n
        # MUTANT: mbfilter.c:1227-1229 (`start > len`) and :1239-1241
        # (`start > end`) DELETED. Everything else is R1.
        return start, maxread

    mut_unstable = mut_checked = 0
    for label, s, slen, frm, length in calls():
        a0, mx = run_mut(s, slen, frm, length, fillers[0])
        if mx <= slen:
            continue
        mut_checked += 1
        for f in fillers[1:]:
            if run_mut(s, slen, frm, length, f)[0] != a0:
                mut_unstable += 1
                break
    print(f"    MUST-FIRE CONTROL (mbfilter.c:1227's `start > len` clamp "
          f"DELETED): {mut_unstable} of {mut_checked} moved")
    print("    ⭐ so the clamp that is too late to PREVENT the over-read is "
          "the clamp that HIDES it.")
    return unstable, mut_unstable


HISTORY = """
Q4  where each guard lives, PER FUNCTION, by release tag (recorded)

    tag         mb_strcut's own guards      mbfilter.c prologue   body sha256/16
    php-5.0.0          -   -                       -            <- THIS ROW (R1)
    php-5.0.5          -   -                       -
    php-5.1.0          -   -                       -
    php-5.1.1          -   -                       -
    php-5.1.2        FROM LEN                      -   <- cb3cca21b345
      .. php-5.2.6   FROM LEN                      -            a971fe526e8b8803
    php-5.2.7                                                   ec8b60b77f5d7e8e
      .. php-5.2.11  FROM LEN                      -
    php-5.2.12       FROM  -                       -   <- c2471b495009
      .. php-5.2.17  FROM  -                       -            26e2099e33433c74
                                                                ^^ THIS ROW (R1h)
    php-5.3.0        FROM LEN                      -            08719ef48d57d502
    php-5.3.1        FROM LEN                      -
    php-5.3.2        FROM  -                       -            49ad3ab2796d63e4
    php-5.3.3        FROM  -                      YES  <- d9dda48f8a7e
    php-5.3.29       FROM  -                      YES           49ad3ab2796d63e4
    php-5.4.0        FROM  -                      YES

    FROM = `if (from > <len>) RETURN_FALSE`   -- hunk (a), either spelling
    LEN  = the `(unsigned)` sum clamp         -- hunk (b), either spelling
    body sha256/16 = brace-matched PHP_FUNCTION(mb_strcut) body, per
    `.temp/mgr165/REFETCH.sh` over nineteen tags (UPSTREAM_002 §1).

    ⭐⭐ HUNK (b) WENT OUT IN 2005, WAS REMOVED FROM **BOTH** LIVE BRANCHES
    WITHIN FIVE MONTHS OF EACH OTHER, AND NEVER CAME BACK. It is present
    continuously php-5.1.2 .. php-5.2.11 and php-5.3.0 .. php-5.3.1, and absent
    from php-5.2.12 and php-5.3.2 onward. `c2471b495009` was committed THREE
    TIMES IN THE SAME SECOND -- c2471b495009, 0c974164e248, ce3c028803aa, one
    per live branch -- with `ext/mbstring/tests/bug49354.phpt`. R1h is pinned to
    php-5.2.12 .. php-5.2.17 rather than to 5.3.2+ only because 5.3 also carries
    the surrounding rewrite; the GUARD configuration is the same at both.
    ⚠ 5.2.6 -> 5.2.7 is `MBSTRG(current_language)` -> `MBSTRG(language)`, one
    token, unrelated to either guard; the 5.2 -> 5.3 size drop is the
    surrounding rewrite, not the guards.
    ⚠ NOT VERIFIED: that `r202895`, which c2471b495009's message blames, is
    cb3cca21b345. php-src's converted history carries no `git-svn-id` trailer
    and svn.php.net no longer resolves, so TASK_PHP_018 could not map it. What
    IS measured is the code: the three lines removed in 2009 are byte-identical
    to three of the seven added in 2005.

    ⚠⚠ THE SPELLING CHANGES AND A GREP FOR ONE OF THEM REPORTS THE WRONG
    ANSWER IN BOTH DIRECTIONS. `if (from > Z_STRLEN_PP(arg1))` is absent from
    5.3 onward (it becomes `(unsigned int)from > string.len`) and the
    unanchored `from > Z_STRLEN_PP(arg1)` is PRESENT at 5.0.5 -- inside
    PHP_FUNCTION(mb_strimwidth). The table above is built by parsing
    `PHP_FUNCTION(mb_strcut)` out of the file. NOTES.md 4c-bis.

    `mbfl_strcut`'s BODY is byte-identical (sha256 613648930a3d2551...) at
    php-5.0.0, 5.0.5, 5.1.0, 5.1.1, 5.1.2, 5.2.17, 5.3.0, 5.3.1 and 5.3.2 --
    NINE releases, five and a half years -- because the 2005 fix is in the
    CALLER. ⚠ This said SIX until TASK_PHP_017 m3 extracted the function at
    twelve tags and found nine; the claim was UNDERSTATED, not wrong. The
    library function itself was unsafe for any other caller until d9dda48f8a7e
    (2010-03-12), four years and three months later.

    * AND IN THE PINNED 5.0.0 TARBALL, mbstring.c:1900, PHP_FUNCTION
    (mb_strimwidth) ALREADY HAS `if (from < 0 || from > Z_STRLEN_PP(arg1))` --
    the only occurrence of that text in the file. The sibling entry point, one
    screen away, already clamped `from` from above. NOTES.md 4c-ter.

    Evidence: .temp/php16/01-fixcommit.log, .temp/php16/07-history.log.
"""


def main():
    q1()
    q2()
    q3()
    print(HISTORY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
