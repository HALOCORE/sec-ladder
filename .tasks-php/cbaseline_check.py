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
# ⭐⭐ LOOSENED 2026-09-15 ON TASK_PHP_059's RULING (item 134, part (a)).
#    It matched only `c-gcc`/`c-clang`, so `ph29` NOTES 1157 -- the line in the
#    corpus that obeys the rule BEST, naming BOTH columns -- was flagged because
#    it writes them `gcc-C` / `clang-C`.  F10: a grep has a spelling, and this
#    was the EIGHTH bare-spelling instance, the first cutting in this direction.
# ⛔ THIS IS A LOOSENING, NOT A TUNING, AND THE DISTINCTION IS THE WHOLE POINT:
#    it removes a FALSE POSITIVE (a unit that names its compiler in another
#    word order), and it does NOT weaken what the rule demands.  The reviewer
#    REFUSED the other half of item 134 -- making BASE demand BOTH columns --
#    for an eighth time, because the rule is a DISJUNCTION ("both columns, OR an
#    explicit statement that only one was measured") and the second disjunct is
#    not regex-decidable.  That half is an `ⓘ` REPORT arm instead; see `main`.
BASE = re.compile(r'c-(?:gcc|clang)(?:-h)?|(?:gcc|clang)-C\b')

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
# ⛔⛔⛔ RAISED 69 -> 77 ON 2026-09-15, AND THE REASON THIS COMMENT IS LONG IS
#    THAT THE RATCHET WAS NEVER BEING RUN.  `--ratchet` was the ONLY spelling
#    that enforced it, and `checkers.py` filed this tool with `argv=[]` plus the
#    `--selftest` flag arm -- NEITHER of which enforces.  Measured: at commit
#    `1cc2c0e`, BEFORE this session touched anything, the corpus already stood at
#    **70 hits against a ratchet of 69** and nothing had said so.  ⭐ A ratchet
#    you must opt into is not a ratchet, so the BARE run now enforces (see
#    `main`), and `--ratchet` survives as an accepted no-op for old callers.
#
# ⚠⚠ THE EIGHT NEW HITS, ADJUDICATED BY HAND -- the rule above is "raise ONLY
#    with a hand adjudication beside it", and all eight are `TASK_PHP_058`'s new
#    `inside_share` sections.  ALL EIGHT ARE BENIGN, and two are informative:
#      ph03 NOTES 1317  "Both C columns are ..." -- says so, sentence continues
#                       on the next line.  LINE-BOUNDARY artefact.
#      ph03 NOTES 1335  F109's `ph55` 74-83 % quote: a SHARE LEVEL, not a
#      ph16 NOTES  933  cross-language magnitude.  Same quote in both rows.
#      ph03 NOTES 1352  R1-vs-R1h -- C against C, same compiler.  Not x-language.
#      ph16 NOTES  921  "EVERY CELL IS 99.20-99.66 %" -- a share range.
#      ph29 NOTES 1145  ⭐ QUOTES the defective RECAP sentence IN ORDER TO
#                       CRITICISE IT.  A quotation of a defect scoring as the
#                       defect is item 115's class -- "a check that reads prose
#                       and calls it code" -- and this is its seventh instance.
#      ph29 NOTES 1157  ⭐⭐ THE MOST INFORMATIVE ONE.  It names BOTH columns --
#                       "gcc-C is 33 % dearer ... clang-C is 4.4 % cheaper" --
#                       and `BASE` does not match `gcc-C`/`clang-C`, only
#                       `c-gcc`/`c-clang`.  **The checker flags the one line in
#                       the corpus that obeys the rule BEST, because of a
#                       spelling.**  F10: a grep has a spelling.  This is the
#                       EIGHTH bare-spelling instance and it now cuts BOTH ways;
#                       open item 134 routes it to a reviewer with the rest.
#      ph97 README 115  a markdown table header.  Normaliser artefact.
# ⓘ RECAP_PHP.md went 35 -> 34 over the same window, so 8 arrived and 1 left.
# ⛔ ONE hit of the 70 at `1cc2c0e` was ALREADY unadjudicated and is NOT
#    attributed here: it predates this session and I did not chase it.
#
# ✅✅ TASK_PHP_059 CORRECTED THREE OF THE ADJUDICATIONS ABOVE AND FOUND THE
#    70th.  Left in place rather than rewritten, because a wrong REASON with a
#    right verdict is the record this ledger exists to keep:
#      ph03 1317  NOT a line-boundary artefact.  The unit is a BLANK-LINE
#                 PARAGRAPH, not a line, and `BASE` is searched over the whole
#                 unit.  It is flagged because the unit says "Both C columns are
#                 present" and never spells `c-gcc`/`c-clang` -- the BARE-
#                 SPELLING class, same as ph29 1157.  Benign either way.
#      ph03 1352  incomplete: the unit DOES carry a cross-language sentence, but
#                 carries no cross-language MAGNITUDE.  Benign on that ground.
#      ph97 115   not a normaliser artefact: a real unit.  MAG matches
#                 "+0.0000 Ir" and XLANG two bare C's.  Benign -- the Ir figure
#                 is a Rust-vs-Rust control's.
#      THE 70th  `RECAP_PHP.md:1812` at 1cc2c0e -- the body of F127 ITSELF,
#                 quoting the defective sentence in order to criticise it.
#                 BENIGN, item 115's class, and it makes that class the EIGHTH
#                 instance, not the seventh.  ▶ The ratchet is honest
#                 RETROSPECTIVELY too; the hedge above is withdrawn.
#
# ⛔⛔⛔ RAISED 77 -> 78 ON 2026-09-15, LANDING TASK_PHP_059.  THE BARE RUN
#    CAUGHT THIS -- the first drift the repaired ratchet has stopped, and it
#    stopped the MANAGER, mid-edit, in the session that repaired it.
#    THREE ARRIVED AND TWO LEFT, AND ⛔ NEITHER DEPARTURE IS A REPAIR:
#      NEW  03-numbers.md  the new caution box, quoting ph52's "22.24 % on its C
#                 rungs ... ~98.6 % on its Rust rungs" IN ORDER TO SHOW IT IS
#                 THE WRONG DEFINITION.  Share LEVELS, not a cross-language
#                 magnitude.  BENIGN -- item 115's class, NINTH instance.
#      NEW  RECAP_PHP.md  the F129 counterexample bullet, quoting ph97's
#                 "98.84 % -> 64.50 %" to show it is the W quantity.  Share
#                 levels, quoted to criticise.  BENIGN, item 115's class.
#      NEW  RECAP_PHP.md  ⭐⭐ THE INFORMATIVE ONE: a sentence quoting THIS
#                 FILE'S OWN ADJUDICATION LEDGER ("the four C cells actually
#                 span 20.23-22.69 %").  The checker flags a quotation of
#                 itself.  BENIGN, and a new sub-class of item 115's.
#      GONE 02-ladder.md  the FOURTH-FLAG blockquote stopped hitting because
#                 the item-132 block inserted into the SAME blockquote unit
#                 contains `c-gcc`, so BASE now matches.  ⛔ AN ACCIDENTAL
#                 BASE MATCH, NOT A REPAIR.
#      GONE ph16 NOTES 921  the "99.20-99.66 %" unit stopped hitting because a
#                 blank line I added SPLIT the unit in two; the first half lost
#                 its bare `C` and XLANG no longer matches.  ⛔ A UNIT-BOUNDARY
#                 ARTEFACT, NOT A REPAIR.
# ⭐⭐⭐ SO THE NET IS +1 AND THE TRUTH IS "+3 ARRIVED".  The reviewer named this
#    mechanism once (the Index unit gaining a literal `c-gcc` from a finding
#    title); these are instances TWO and THREE, both caused by ordinary prose
#    edits near a hit.  ▶ THE UNIT IS A BLANK-LINE PARAGRAPH, so ANY edit near a
#    hit can move the count with nothing repaired and nothing broken.  A NET
#    COUNT IS NOT A MEASURE OF CORPUS HEALTH -- adjudicate the SET, by unit
#    text, never the number.  RECAP_PHP.md F132.
#
# ✅ LOWERED 78 -> 77 IN THE SAME SITTING, ON TASK_PHP_059's ITEM-134 RULING.
#    Loosening BASE to accept the `gcc-C` / `clang-C` word order (see BASE)
#    retires exactly ONE hit: `ph29` NOTES 1157, which went 3 -> 2 for that file
#    while every other file's set is unchanged.  ⭐ VERIFIED AS A SET, NOT AS A
#    COUNT -- which is F132's own rule, applied in the edit that files F132.
#    That line names BOTH columns and was the best-labelled sentence in the
#    corpus; it should never have been a hit.
# ⛔ A LOWERING IS NOT A WEAKENING HERE: N2c is a must-fire arm asserting that
#    the loosened BASE still flags a claim naming NO compiler, so the rule's
#    teeth are checked rather than assumed.
RATCHET = 77
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
    # ⛔⛔ THE BARE RUN ENFORCES, AS OF 2026-09-15. This block used to be gated
    #    on `--ratchet`, and NO **AUTOMATED** CALLER EVER PASSED THAT FLAG --
    #    `checkers.py` files this tool with `argv=[]` and a `--selftest` arm, so
    #    enforcement depended on a TASK FILE remembering to ask for it, and
    #    after `_052` no task file did. The corpus drifted 69 -> 70 unnoticed.
    # ⛔ THIS COMMENT SAID "NOTHING EVER PASSED THAT FLAG" AND TASK_PHP_059
    #    REFUTED IT: `TASK_PHP_051.md` and `TASK_PHP_052.md` both instruct the
    #    flag by name, and TASK_PHP_051_REPORT.md:55 RECORDS THE RUN -- "rc 0 --
    #    68 hits, ratchet 69" -- with the agent declining the tool's "lower
    #    RATCHET" advice and giving a reason. Corrected in place, here and in
    #    RECAP_PHP.md's F130.
    # ⭐ It is a BIRTH DEFECT, not a regression: the guard is in this file's
    #    FIRST commit (9313449, RATCHET = 63). Nothing unwired it; it was never
    #    wired. The un-enforced window is ~32 hours and three commits.
    # ⭐ A ratchet you must opt into is not a ratchet. `--ratchet` is still
    #    ACCEPTED so older callers keep working; it simply no longer decides.
    # ⓘ ONE-COLUMN REPORT -- A REPORT, NEVER A VERDICT (TASK_PHP_059, item 134
    #   part (c)).  `.memory-php/03-numbers.md`'s fifth thing is a DISJUNCTION:
    #   "with both columns, OR an explicit statement that only one was
    #   measured."  A regex can decide the first branch and CANNOT decide the
    #   second -- spelling "only one was measured" for a grep is F10 one level
    #   up -- so demanding both columns would flag every legitimately
    #   single-column unit, of which there are at least four today.
    # ▶ So this PRINTS the population and leaves the judgement to a human.  It
    #   is `quota.py`'s discipline (report the state, do not invent a verdict)
    #   and F128's Kind-A/Kind-B rule at once: an arm may not assert a direction
    #   that is still being estimated.
    one_col = []
    for p in SCAN:
        if not os.path.exists(p):
            continue
        for lineno, u in units(p):
            if not (MAG.search(u) and XLANG.search(u)):
                continue
            named = {m.group(0) for m in BASE.finditer(u)}
            fams = {('clang' if 'clang' in n else 'gcc') for n in named}
            if len(fams) == 1:
                one_col.append((os.path.relpath(p, ROOT), lineno, fams.pop()))
    print('\nⓘ  ONE-COLUMN REPORT (no verdict): %d unit(s) carry a '
          'cross-language magnitude and name exactly ONE C compiler.' %
          len(one_col))
    print('   ⛔ THAT IS NOT AUTOMATICALLY A DEFECT -- the rule also permits an '
          'explicit "only one was measured", which no regex can see.')
    print('   ▶ Read them; do not count them.')
    for f, n, fam in one_col:
        print('     %-58s %5d  %s only' % (f, n, fam))

    if len(h) > RATCHET:
        print('\nRATCHET FAIL: %d hits > %d. Adjudicate each new one BY HAND, '
              'then raise RATCHET with the adjudication beside it.'
              % (len(h), RATCHET))
        return 1
    if len(h) < RATCHET:
        print('\nnote: %d hits < ratchet %d -- lower RATCHET to %d.'
              % (len(h), RATCHET, len(h)))
    return 0


def selftest():
    """MUST-FIRE NEGATIVES -- every one asserts this checker can FAIL.

    ⛔⛔ THIS USED TO PRINT ONLY `SELFTEST PASS (0 failures)`, AND THAT IS A
    DEFECT, NOT A STYLE. A checker whose arms are silent when they pass is
    indistinguishable from a checker with NO ARMS -- `checkers.py` N12 measured
    exactly that on 2026-09-15: this file's registry entry claimed `9 arms` and
    the observable count was **0**. ⭐ It is F10's rule (quota.py prints
    `VACUOUS TODAY` rather than passing silently) applied one level up: SAY
    WHICH ARM RAN.

    ⚠ The claim was also wrong: there are **10** arms, not 9 -- `N8b` is a
    separate assertion and was never counted. Seventh stale count literal in a
    `.tasks-php/` validator.
    """
    fails = []
    ran = []

    def arm(tag):
        if tag not in ran:
            ran.append(tag)

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
    arm('N1')
    if not scores('A says C is +33 % dearer than naive safe Rust.'):
        fails.append('N1 the target defect does NOT score as a hit')

    # N2 THE LABELLED FORM MUST NOT.
    # ⛔⛔ THIS ARM'S EXEMPLAR USED TO BE THE ONE-COLUMN SENTENCE
    #    "`ph29/large`, `c-gcc` vs `safe_naive`: A says C is +33.01 % DEARER."
    #    -- held up as "a correctly labelled claim" while naming ONE column of
    #    the very pair whose columns have OPPOSITE SIGNS (`c-clang` reads
    #    -4.36 %).  The enforcer's model of compliance was itself one item short
    #    of the rule it enforces (TASK_PHP_059, item 134 part (b)).
    # ▶ The exemplar is now a BOTH-COLUMNS sentence, which is what
    #   `.memory-php/03-numbers.md`'s fifth thing actually asks for.
    arm('N2')
    if scores('`ph29/large`: A says `c-gcc` is +33.01 % DEARER than '
              '`safe_naive` while `c-clang` is -4.36 % CHEAPER.'):
        fails.append('N2 a correctly labelled claim scored as a hit')

    # N2b MUST-NOT-FIRE: the OTHER WORD ORDER is equally labelled.  `ph29`
    #     NOTES 1157 writes `gcc-C` / `clang-C`; before the 2026-09-15 loosening
    #     BASE saw neither and flagged the best-labelled line in the corpus.
    arm('N2b')
    if scores('gcc-C is 33 % dearer than safe_naive; clang-C is 4.4 % cheaper.'):
        fails.append('N2b a both-columns claim in the `gcc-C` spelling scored')

    # N2c ⭐ MUST-FIRE, AND IT IS THE ARM THAT KEEPS (a) HONEST: loosening BASE
    #     must not silence a unit that names NO compiler at all.
    arm('N2c')
    if not scores('A says C is +33.01 % dearer than `safe_naive` on large.bin.'):
        fails.append('N2c the loosened BASE silenced an UNLABELLED claim')

    # N3 A MAGNITUDE IS REQUIRED. Prose about C with no number is not a figure.
    arm('N3')
    if scores('The C rungs are paying for PHP request boundary work.'):
        fails.append('N3 fired on a claim carrying no magnitude')

    # N4 A CROSS-LANGUAGE TOKEN IS REQUIRED. A pure Rust-vs-Rust figure must
    #    not fire, or the count is meaningless.
    arm('N4')
    if scores('`safe_tuned` is +3.7 % against `safe_naive` on this row.'):
        fails.append('N4 fired on a same-language figure')

    # N5 THE `C` TOKEN MUST NOT MATCH INSIDE WORDS OR PATHS. If it did, every
    #    paragraph mentioning CWE, CVE or a .c file would be a hit.
    arm('N5')
    for bad in ('CWE-125 costs 12 %.', 'See uuencode.c:66, +5 %.',
                'The CVE is +8 %.', 'C99 flags add 3 %.'):
        if scores(bad):
            fails.append('N5 fired on a non-language C: %r' % bad)

    # N6 clang ALONE must satisfy the rule as much as gcc alone does NOT get a
    #    free pass -- assert BASE recognises every spelling in use.
    arm('N6')
    for good in ('c-gcc', 'c-clang', 'c-gcc-h', 'c-clang-h'):
        if not BASE.search('X %s Y' % good):
            fails.append('N6 BASE does not recognise %r' % good)

    # N7 THE RATCHET MUST BE ABLE TO FAIL. Assert the comparison, not the data.
    arm('N7')
    if not (RATCHET + 1 > RATCHET):
        fails.append('N7 ratchet comparison is inert')

    # N8 THE SCAN LIST MUST BE NON-EMPTY AND EVERY ENTRY MUST EXIST -- a
    #    mistyped glob would report "0 hits" as a clean bill of health.
    arm('N8')
    arm('N8b')
    if len(SCAN) < 10:
        fails.append('N8 scan list has only %d entries' % len(SCAN))
    for p in SCAN:
        if not os.path.exists(p):
            fails.append('N8b scan entry missing: %s' % p)

    # N9 AND THE COUNT MUST NOT BE ZERO. A checker that finds nothing on a
    #    corpus known to contain the defect is broken, not clean.
    arm('N9')
    if len(hits()) == 0:
        fails.append('N9 zero hits on a corpus known to carry the defect')

    # ⭐ EVERY ARM NAMES ITSELF, PASS OR FAIL. `checkers.py` N12 reads these
    #   names to check this file's registry entry against reality, so a silent
    #   pass would make the claim uncheckable -- which is how `9 arms` stood
    #   while there were 10.
    bad_tags = {f.split()[0] for f in fails}
    for tag in ran:
        hit = [f for f in fails if f.split()[0] == tag]
        if hit:
            for f in hit:
                print('  FAIL  %s' % f)
        else:
            print('  PASS  %s' % tag)
    print('SELFTEST %s (%d arms, %d failures)'
          % ('PASS' if not fails else 'FAIL', len(ran), len(fails)))
    assert not (bad_tags - set(ran)), \
        'an arm reported a failure without registering itself: %s' % (bad_tags - set(ran))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else main(sys.argv))
