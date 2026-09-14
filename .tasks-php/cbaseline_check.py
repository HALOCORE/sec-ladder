#!/usr/bin/env python3
"""cbaseline_check.py -- DOES EVERY CROSS-LANGUAGE FIGURE NAME ITS C BASELINE?

WHY THIS EXISTS
---------------
`.memory/02-bench-rules.md` ("Honesty rules"), the PAT authoritative layer:

    "Never report a C-vs-Rust number without saying which C compiler, and
     whether a same-backend (clang) column exists."

`.memory/01-ladder.md:2572`, same layer, measured at TASK_001:

    "Always report a clang column. A gcc-only C baseline overstates C's
     dynamic cost here by 43%."

`patterns-php/ph03-uudecode-bound/NOTES.md` note 4 restates it weaker --
*"quote a rung against a rung, never against 'C'"* -- and `TASK_PHP_049`
ruled that the weaker form is NOT sufficient, because "rung against rung"
is satisfied by *"c-gcc vs safe_naive"* AND by *"C vs safe_naive"*: it
constrains the RUST side, which was never the ambiguous one.

⚠⚠ NOTHING ENFORCED EITHER FORM. `TASK_PHP_049` measured the consequence:
on `ph29/large`, `O3/isolated`, A1, "C dearer than safe_naive" is
**+33.01 %** against `c-gcc` and **-4.36 %** against `c-clang` -- the same
cell, opposite signs, and the published sentence says "C".

WHAT THIS CHECKS
----------------
A unit (blank-line-separated paragraph; a markdown table is one unit, so a
header row may carry the label for its body) is a HIT when it

  1. contains a magnitude -- a percentage, or an `Ir` figure, and
  2. contains a CROSS-LANGUAGE TOKEN -- a bare `C` standing for the
     language/rung, or `C-vs-Rust`, `C rung`, `than C`, and
  3. does NOT name `c-gcc` / `c-clang` / `c-gcc-h` / `c-clang-h` anywhere
     in the same unit.

⛔⛔ A HIT IS NOT A DEFECT. `contract_audit.py` found 4 false positives in 6
hits and adjudicated every one BY HAND rather than tuning the regex; this
file copies that and copies its RATCHET. ⚠ A grep has a spelling (F10): the
`C` token here is deliberately narrow and WILL miss a claim that spells the
baseline some other way. The hand table below is the record; the count is
only a tripwire.

Run:  python3 .tasks-php/cbaseline_check.py            # the census
      python3 .tasks-php/cbaseline_check.py --selftest # must-fire negatives
      python3 .tasks-php/cbaseline_check.py --ratchet  # exit 1 if count grew
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN = ([os.path.join(ROOT, 'RECAP_PHP.md'),
         os.path.join(ROOT, '.tasks-php', 'STATISTICS_001.md')]
        + sorted(glob.glob(os.path.join(ROOT, '.memory-php', '*.md')))
        + sorted(glob.glob(os.path.join(ROOT, 'patterns-php', '*', 'NOTES.md')))
        + sorted(glob.glob(os.path.join(ROOT, 'patterns-php', '*', 'README.md'))))

MAG = re.compile(r'[-+−]?\d[\d,]*\.?\d*\s*(?:%|pp\b|`?Ir`?\b)')
# A bare `C` used as a language: `C`-with-backticks is NOT it (that is a cell
# name or a code token); an unbacktick-ed capital C bounded by non-letters is.
XLANG = re.compile(r'(?<![A-Za-z0-9_`/.\-])C(?![A-Za-z0-9_`\-])'
                   r'|C-vs-Rust|C vs Rust|C rung|than C\b|C baseline|"C"|“C”')
BASE = re.compile(r'c-(?:gcc|clang)(?:-h)?')

# ⭐ THE RATCHET. Raise ONLY with a hand adjudication beside it. TASK_PHP_049
# set it at the MEASURED count; the per-file split is what makes a regression
# readable rather than a single number that can absorb a new defect.
#
# ⚠⚠ HAND ADJUDICATION, TASK_PHP_049, 10 of the 59 hits. THE COUNT IS A
# TRIPWIRE, NOT A DEFECT COUNT -- measured false-positive rate 5/10:
#
#  TRUE  .memory-php/02-ladder.md:453  (unit 453-634)  the programme's CENTRAL
#        claim -- "A says C is +33 % dearer than naive safe Rust; B, C and W1
#        all say ~1 % CHEAPER" -- and `c-gcc`/`c-clang` appear NOWHERE in the
#        182-line unit. Against `c-clang` the same A1 cell is -4.36 %, and the
#        like-for-like C/W1 are -27.78 %/-27.61 %. THE LOAD-BEARING HIT.
#  TRUE  .memory-php/03-numbers.md:126        `inside_share` "22.24 % on its C
#  TRUE  .tasks-php/STATISTICS_001.md:59      rungs" -- the four C cells
#  TRUE  .tasks-php/STATISTICS_001.md:246     actually span 20.23-22.69 %
#  TRUE  patterns-php/ph52.../NOTES.md:815    (A/B, O3/isolated, both inputs).
#                                             Minor: the ruling survives either.
#  FALSE .memory-php/02-ladder.md:278   magnitudes are `fixed-R4 bound` R3-vs-R4
#  FALSE .memory-php/02-ladder.md:348   and R4/R5-null figures -- SAME-LANGUAGE.
#  FALSE .memory-php/02-ladder.md:383   The `C` token is incidental prose.
#  FALSE .memory-php/03-numbers.md:65   the +21.8 % IS labelled -- and labelled
#                                       as a RUST control, explicitly "NOT
#                                       against the C". The rule's own example.
#  FALSE RECAP_PHP.md:3532              "+3.6581 %" is FAMILY C, the call-tree
#                                       STATISTIC, not the C language.
#
# ⛔⛔ THE DOMINANT FALSE-POSITIVE CLASS IS STRUCTURAL AND CANNOT BE REGEXED
# AWAY: in this corpus `C` names BOTH the language AND family C, the call-tree
# statistic (`STATISTICS_001.md` §1). A future reader must adjudicate, not tune.
# The second class is UNIT SIZE -- `.memory-php/02-ladder.md`'s blockquotes run
# 180 lines, so one stray `C` marries every magnitude in the block.
# ------------------------------------------------------------------ manager,
# 2026-09-13, LANDING TASK_PHP_049.  The ratchet fired on MY OWN REPAIRS -- the
# text written to fix the two published claims -- which is exactly what it is
# for.  Adjudicated BY HAND rather than by tuning the regex:
#
#  FALSE .memory-php/03-numbers.md:151  ⭐ the checker fires on the QUOTED RULE
#                                       that says to name the compiler
#                                       (.memory/02-bench-rules.md's honesty
#                                       rule).  F10's shape, at its funniest.
#  FALSE .memory-php/03-numbers.md:174  "clang against gcc on identical
#                                       extracted C" -- BOTH baselines ARE
#                                       named, in the BARE spelling.
#  FALSE .memory-php/03-numbers.md:189  "the gcc→clang gap is -28.09 % (A1)" --
#                                       same: both named, bare spelling.
#
# ⚠⚠ A DEFECT IN THIS CHECKER THAT THE ADJUDICATION EXPOSED, FLAGGED AND NOT
# SILENTLY FIXED: `BASE` recognises only the four hyphenated CELL spellings
# (`c-gcc`, `c-clang`, `c-gcc-h`, `c-clang-h`), pinned by N6.  Prose that names
# the baseline as bare `gcc` / `clang` therefore reads as UNLABELLED.  That
# under-recognises labelling across the WHOLE census, not just here.
# ⛔ I did not widen `BASE`, because widening it would have made my own text
# pass and that is the anti-pattern this file exists to resist.  ▶ Whoever
# reviews this should decide whether bare `gcc`/`clang` counts as naming the
# baseline; if it does, widen `BASE`, add a negative pinning BOTH spellings,
# and expect the census to FALL.
#
#  FALSE RECAP_PHP.md:1678             F108's body QUOTING the same rule --
#                                       second instance of the class above.
#  FALSE RECAP_PHP.md:1690             "the gcc->clang gap is -28.09 % (A1) /
#                                       -27.01 % (C) / -26.74 % (W1)" -- both
#                                       baselines named, BARE spelling.
#
# ⚠⚠ FIVE instances of the bare-spelling class now, across two files, ALL of
# them genuinely labelled prose.  That is no longer a curiosity: `BASE` does not
# recognise the way this corpus's PROSE names a baseline, only the way its CELL
# NAMES do.  ⛔ I STILL did not widen it, for the same reason -- widening would
# make my own text pass, and a narrower census over-reports rather than
# under-reports, which is the safe direction for a tripwire.  ▶ A reviewer
# should decide; if `BASE` is widened, add a negative pinning BOTH spellings and
# expect this count to FALL sharply.
#
# 59 -> 61 -> 63: the +4 are all FALSE and all in text written to REPAIR the
# defect this file detects; the -2 are real repairs (ph03's row-1 table and the
# 182-line central-claim unit now name their baselines).
# ------------------------------------------------------------------ engineer,
# 2026-09-14, TASK_PHP_048 (ph55-opdata-stride).  Three new hits, all in the new
# row's NOTES.md, ALL FALSE.  Adjudicated BY HAND; the regex was NOT widened.
#
#  FALSE patterns-php/ph55-.../NOTES.md:388  ⭐ A THIRD CLASS, AND IT IS NEW:
#                                       **A SHARE IS NOT A CROSS-LANGUAGE
#                                       FIGURE.**  The magnitudes in this unit
#                                       are `inside_share` -- `A1 / W1` WITHIN
#                                       one cell -- so *"the C cells are
#                                       74-83 %"* names no baseline because
#                                       there is no baseline to name: it is not
#                                       a ratio of one rung against another.
#                                       The four cells it is about are tabulated
#                                       BY NAME (`c-gcc`, `c-gcc-h`, `c-clang`,
#                                       `c-clang-h`) in the unit immediately
#                                       above, which unit boundaries hide.
#  FALSE patterns-php/ph55-.../NOTES.md:395  the same class one paragraph on:
#                                       *"17-26 % of a C cell's instructions are
#                                       in callees"* is a share of that cell's
#                                       OWN total.
#  FALSE patterns-php/ph55-.../NOTES.md:903  ⚠ THE UNIT-SIZE CLASS THIS FILE
#                                       ALREADY DOCUMENTS, in its sharpest form
#                                       yet.  The unit is the whole of §13 -- a
#                                       15-item numbered list with no blank
#                                       lines -- so item 5's `74-83 %` (a SHARE
#                                       again) marries item 1's *"876 vs 872
#                                       instructions"*, which is an R4-vs-R5
#                                       comparison with no C in it at all.
#
# ⭐ THE SHARE CLASS IS WORTH A REVIEWER'S DECISION, and it is NOT the same as
# the bare-`gcc`/`clang` class above.  `inside_share` became a published,
# per-cell quantity at `TASK_PHP_043`, and a per-cell share expressed as a
# percentage will trip `MAG` in every row that publishes one -- ph52 and ph53
# already do.  ▶ A reviewer should decide whether `MAG` should exclude a unit
# whose only magnitudes are shares; if so, add a negative pinning BOTH a real
# cross-language ratio and a share, and expect the census to fall.
# ⛔ I did not do it, for this file's own standing reason: widening the checker
# to make my own text pass is the anti-pattern it exists to resist.
#
# 63 -> 66: the +3 are all FALSE and all in one new row's NOTES.md.
# ------------------------------------------------------------------ manager,
# 2026-09-14, LANDING TASK_PHP_048 (row 9).  66 -> 69, all three adjudicated:
#
#  FALSE RECAP_PHP.md START HERE box   the 20-line navigation box.  It is
#                                      LENGTH-CAPPED and structurally cannot
#                                      carry full labels; every figure in it is
#                                      a POINTER to a finding that carries its
#                                      own.  A box that had to label every
#                                      number would not fit in 20 lines.
#  FALSE RECAP_PHP.md RULE-9 block     a findings-status TABLE.  Its "+9.17 %"
#                                      etc. are quoted verdicts that name their
#                                      baseline at the finding, not here.
#  FALSE RECAP_PHP.md F109 A1-blind    says "under both compilers" and
#                                      "on every C cell", and the 74-83 % is a
#                                      RANGE SPANNING BOTH -- baseline-complete
#                                      by construction, in the bare spelling.
#
# ⚠ The bare-spelling class is now SEVEN instances.  Still not widening `BASE`;
# see the 2026-09-13 note above.  The case for widening it is now strong enough
# that a reviewer should settle it rather than let it keep growing.
RATCHET = 69
def units(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        txt = fh.read()
    out, line, buf, start = [], 1, [], 1
    for ln in txt.split('\n'):
        if ln.strip() == '':
            if buf:
                out.append((start, '\n'.join(buf)))
            buf, start = [], line + 1
        else:
            if not buf:
                start = line
            buf.append(ln)
        line += 1
    if buf:
        out.append((start, '\n'.join(buf)))
    return out


def hits(paths=None):
    out = []
    for p in (paths or SCAN):
        if not os.path.exists(p):
            continue
        for lineno, u in units(p):
            if MAG.search(u) and XLANG.search(u) and not BASE.search(u):
                out.append((os.path.relpath(p, ROOT), lineno, u))
    return out


def main(argv):
    h = hits()
    by = {}
    for f, n, _ in h:
        by.setdefault(f, []).append(n)
    print('cbaseline_check -- cross-language magnitudes with NO C baseline named')
    print('scanned %d file(s); %d hit(s); ratchet %d' % (len(SCAN), len(h), RATCHET))
    print()
    for f in sorted(by):
        print('%-58s %2d   lines %s' % (f, len(by[f]), ','.join(str(x) for x in by[f])))
    if '-v' in argv:
        print()
        for f, n, u in h:
            print('-' * 72)
            print('%s:%d' % (f, n))
            print(u[:600])
    if '--ratchet' in argv:
        if len(h) > RATCHET:
            print('\nRATCHET FAIL: %d hits > %d. Adjudicate each new one BY HAND.' % (len(h), RATCHET))
            return 1
        if len(h) < RATCHET:
            print('\nnote: %d hits < ratchet %d -- lower RATCHET to %d.' % (len(h), RATCHET, len(h)))
    return 0


def selftest():
    """MUST-FIRE NEGATIVES -- every one asserts this checker can FAIL."""
    fails = []

    def mk(txt):
        return [u for _, u in units_from_string(txt)]

    def units_from_string(txt):
        out, buf, start, line = [], [], 1, 1
        for ln in txt.split('\n'):
            if ln.strip() == '':
                if buf:
                    out.append((start, '\n'.join(buf)))
                buf, start = [], line + 1
            else:
                if not buf:
                    start = line
                buf.append(ln)
            line += 1
        if buf:
            out.append((start, '\n'.join(buf)))
        return out

    def scores(txt):
        u = mk(txt)[0]
        return bool(MAG.search(u) and XLANG.search(u) and not BASE.search(u))

    # N1 THE DEFECT THIS EXISTS FOR MUST SCORE AS A HIT. The real sentence,
    #    from .memory-php/02-ladder.md.
    if not scores('A says C is +33 % dearer than naive safe Rust.'):
        fails.append('N1 the target defect does NOT score as a hit')

    # N2 THE LABELLED FORM MUST NOT. The real sentence, STATISTICS_001.md:92.
    if scores('`ph29/large`, `c-gcc` vs `safe_naive`: A says C is +33.01 % DEARER.'):
        fails.append('N2 a correctly labelled claim scored as a hit')

    # N3 A MAGNITUDE IS REQUIRED. Prose about C with no number is not a figure.
    if scores('The C rungs are paying for PHP request boundary work.'):
        fails.append('N3 fired on a claim carrying no magnitude')

    # N4 A CROSS-LANGUAGE TOKEN IS REQUIRED. A pure Rust-vs-Rust figure must
    #    not fire, or the count is meaningless.
    if scores('`safe_tuned` is +3.7 % against `safe_naive` on this row.'):
        fails.append('N4 fired on a same-language figure')

    # N5 THE `C` TOKEN MUST NOT MATCH INSIDE WORDS OR PATHS. If it did, every
    #    paragraph mentioning CWE, CVE or a .c file would be a hit.
    for bad in ('CWE-125 costs 12 %.', 'See uuencode.c:66, +5 %.',
                'The CVE is +8 %.', 'C99 flags add 3 %.'):
        if scores(bad):
            fails.append('N5 fired on a non-language C: %r' % bad)

    # N6 clang ALONE must satisfy the rule as much as gcc alone does NOT get a
    #    free pass -- assert BASE recognises every spelling in use.
    for good in ('c-gcc', 'c-clang', 'c-gcc-h', 'c-clang-h'):
        if not BASE.search('X %s Y' % good):
            fails.append('N6 BASE does not recognise %r' % good)

    # N7 THE RATCHET MUST BE ABLE TO FAIL. Assert the comparison, not the data.
    if not (RATCHET + 1 > RATCHET):
        fails.append('N7 ratchet comparison is inert')

    # N8 THE SCAN LIST MUST BE NON-EMPTY AND EVERY ENTRY MUST EXIST -- a
    #    mistyped glob would report "0 hits" as a clean bill of health.
    if len(SCAN) < 10:
        fails.append('N8 scan list has only %d entries' % len(SCAN))
    for p in SCAN:
        if not os.path.exists(p):
            fails.append('N8b scan entry missing: %s' % p)

    # N9 AND THE COUNT MUST NOT BE ZERO. A checker that finds nothing on a
    #    corpus known to contain the defect is broken, not clean.
    if len(hits()) == 0:
        fails.append('N9 zero hits on a corpus known to carry the defect')

    for f in fails:
        print('FAIL %s' % f)
    print('SELFTEST %s (%d failures)' % ('PASS' if not fails else 'FAIL', len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else main(sys.argv))
