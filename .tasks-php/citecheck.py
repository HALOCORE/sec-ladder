#!/usr/bin/env python3
"""Every rooted path citation in the manager-owned php docs, resolved.

    python3 .tasks-php/citecheck.py            # run from the repo root

Open item 32's generator. The point is the CLEAN NEGATIVE: a run whose only
output is row-relative paths (`c/kernel.c`), deliberately hypothetical ones
(`patterns-php/shared/`) and reports not yet written is a repo with no dangling
pointers. Anything else is rot -- `PROTOCOL.md` rule 13.

Known-benign, printed but not counted: see BENIGN below.
"""
import re, os, glob, sys

ROOTS = ('harness/', 'harness-php/', 'common/', 'common-php/', 'patterns/',
         'patterns-php/', 'results/', 'results-php/', '.tasks/', '.tasks-php/',
         '.memory/', '.memory-php/', 'pilot/', '.web/', '.temp/')

BENIGN = {
    '.memory-php/00', '.memory-php/01', '.memory-php/02', '.memory-php/03',
    '.memory-php/04',                       # shorthand for the NN-*.md files
    'patterns-php/shared', 'patterns-php/shared/x.h', 'common-php/x.h',
    'patterns-php/.ph07-wip', 'patterns-php/.ph93',   # hypothetical rows (F16/F24)
    '.temp/san_tests',                      # lives in php-in-safe-rust/ -- item 32a
    # ⭐ A LIVE TASK FILE NAMING ITS OWN DELIVERABLE. `_042` §6.1 requires
    # `ph53`'s `controls/spellings.py` to be CREATED, so citing it is a FORWARD
    # pointer, not rot -- the same class as the `_REPORT.md` a task file names
    # before writing it. ⚠ Left as a path rather than a clever predicate because
    # the alternative is a heuristic over task titles; it goes INERT the moment
    # the file exists, and a stale BENIGN entry costs nothing.
    'patterns-php/ph53-iface-tail-uninit/controls/spellings.py',
}

DOCS = ['RECAP_PHP.md', 'PLAN_PHP.md', 'CLAUDE.md',
        'patterns-php/CATALOGUE.md', 'patterns-php/SOURCES.md'] + sorted(
    glob.glob('.tasks-php/*.md')) + sorted(glob.glob('.memory-php/*.md'))

def cited(text):
    # ⚠ Scan every WORD of a backtick span, not just spans that are a bare path.
    # `python3 .temp/php11/coverage.py` is one span with a space in it, and the
    # single-token version missed it -- which hid the catalogue's central
    # coverage claim resting on gitignored scratch.
    for m in re.finditer(r'`([^`\n]+)`', text):
        for tok in m.group(1).split():
            # `<row>` / `<subdir>` are TEMPLATE METAVARIABLES and `…` / `...` is
            # prose elision. Neither is a pointer, and the wider scan below picks
            # up both where the old single-token regex excluded them by accident
            # (`<` and `>` were simply not in its character class).
            if any(c in tok for c in '<>…') or '...' in tok:
                continue
            p = re.sub(r'[:#].*$', '', tok.strip('()[],;')).rstrip('/')
            if p.startswith(ROOTS):
                yield p

def exists(p):
    if '{' in p:                             # brace citation: all alternatives
        inner = re.search(r'\{([^}]*)\}', p).group(1)
        return all(glob.glob(re.sub(r'\{[^}]*\}', a, p)) for a in inner.split(','))
    return bool(glob.glob(p)) if '*' in p else os.path.exists(p)

#  A task's report, in EITHER naming. ⛔⛔ THIS USED TO BE `endswith('_REPORT.md')`
#  AND THE SPLIT NAMING SLIPPED PAST IT. `TASK_PHP_054` returned three reports --
#  `..._REPORT_E2E3E4.md`, `..._REPORT_E5E6E7E8.md`, `..._REPORT_S4S5S6T2T4T6.md`
#  -- none of which ends in `_REPORT.md`, so all three scored as ROT while the
#  task was in flight, and the count went 1 -> 4 -> 1 as they landed.
#  ⭐ THAT IS THE MEASURED HALF OF F117, AND IT IS NARROWER THAN EVERY DOCUMENT
#  SAID: rot does NOT rise for an in-flight task in general, only for one whose
#  report is SPLIT. A task with a plain `_REPORT.md` never moved it. Measured
#  2026-09-15 by citing both spellings from the same live file: 1 and 2.
#  ▶ Repaired rather than documented, because `.tasks-php/README.md` has stated
#  the exception in words since Phase 0 ("Ignore a MISSING report for a task that
#  is still open") and this checker simply never inherited it -- the THIRD
#  un-inherited caution the programme has caught, now the third to be closed.
_REPORT = re.compile(r'_REPORT(?:_[A-Za-z0-9]+)?\.md$')


# ⛔⛔ THESE TWO USED `endswith('_REPORT.md')` WHILE `benign()` ABOVE HAD ALREADY
#   BEEN WIDENED TO `_REPORT` (F122) -- so the SPLIT naming was benign in one
#   half of the repair and a LIVE DOC in the other. Six reports were on the
#   wrong side of it: TASK_PHP_001's three and TASK_PHP_054's three. ⭐ A repair
#   that fixes one limb of its own mechanism is worse than no repair, because
#   the finding reads as closed. ⓘ Found by TASK_PHP_057's reviewer, hours
#   after F122 landed, and `N6c` could not reach it -- N6c tests `benign()`,
#   and this is the PARTITION.
#   ▶ ONE SPELLING, ONE PLACE. `_REPORT` is the predicate for both halves now.
def _is_report(path):
    return bool(_REPORT.search(path))




def benign(doc, p):
    """A missing path is EXPECTED, not rot, when:"""
    if p in BENIGN: return True
    if _is_report(p): return True                     # a report not yet written
    # scratch under .temp/ is re-derivable and CLAUDE.md rule 1 mandates deleting
    # it once the gates are green -- a historical report citing its own deleted
    # blobs is the rule working, not a broken pointer.
    if p.startswith('.temp/'): return True
    # a php gate record keys common-php/ sources under the frozen common/ prefix
    # (harness-php/root.py's rebinding -- RECAP_PHP.md open item 33)
    if p.startswith(('common/', 'common-php/layout', 'patterns/ph00-smoke')): return True
    return False

LIVE = [d for d in DOCS if not _is_report(d)]
HIST = [d for d in DOCS if _is_report(d)]

rot = 0
for doc in DOCS:
    miss = sorted({p for p in cited(open(doc, encoding='utf-8', errors='replace').read())
                   if not exists(p)})
    real = [p for p in miss if not benign(doc, p)]
    if real:
        tag = 'ROT ' if doc in LIVE else 'hist'
        print(f'--- {doc}  ({"LIVE" if doc in LIVE else "historical report"})')
        for p in real: print(f'   {tag} {p}')
    if doc in LIVE: rot += len(real)
print(f'\nunresolved in a LIVE doc: {rot}'
      + ('   <- every citation in the live manager docs resolves' if not rot else ''))
print('(historical *_REPORT.md hits above are constructed demos, planted probes and\n'
      ' proposals never built -- they are the record, not pointers. Do not "fix" them.)')

# --- WARNING, not a failure: a COMMITTED doc resting on deletable scratch. ----
# `CLAUDE.md` rule 1 makes everything under `.temp/` re-derivable and mandates
# deleting it once the gates are green. A citation there resolves today and is
# gone tomorrow, and `exists()` cannot see the difference -- so this is a
# separate report, keyed on the doc being committed rather than on the path
# being broken.
#
# SCOPE: the CLAIM layer only -- the authoritative `.memory-php/`, the catalogue,
# the plan. NOT `.tasks-php/TASK_*.md`, which say "scratch under `.temp/phNN/`"
# as an INSTRUCTION TO CREATE, and NOT `RECAP_PHP.md`, which cites the manager's
# current scratch on purpose as provenance for work in flight. Neither is a
# committed claim resting on deletable evidence, which is the thing being hunted.
CLAIMS = ['patterns-php/CATALOGUE.md', 'patterns-php/SOURCES.md', 'PLAN_PHP.md',
          'CLAUDE.md'] + sorted(glob.glob('.memory-php/*.md'))

# ⭐⭐ AND EVERY BUILT ROW'S `spec.md` AND `NOTES.md`, ADDED 2026-09-12.
# ⚠⚠ WHY: `TASK_PHP_041` put a `.temp/php41/probe_wrap.rs` citation INSIDE
# `ph53`'s hashed `slb-contract` block, found it itself, and repaired two of the
# THREE places it had written it -- `verus.obligations_note` survived. It then
# reported the reason nothing caught the third: *"citecheck.py does not scan
# per-row spec.md/NOTES.md"*. ▶ It does now.
# ⭐ A row's `spec.md` is the MOST committed doc in the tree: its contract block
# is hashed into `contract_sha256`, so a dangling pointer there is frozen into
# the gate record of every row that carries it.
ROW_CLAIMS = sorted(glob.glob('patterns-php/*/spec.md')) + \
             sorted(glob.glob('patterns-php/*/NOTES.md'))

# ⛔⛔ AND THE LAYER THIS CHECKER COULD NOT SEE, WHICH IS WHERE THE WORST
# INSTANCE LIVES. `ROW_CLAIMS` is `spec.md` + `NOTES.md`, so a `.temp/` citation
# inside a COMMITTED `controls/*` file was invisible -- and `TASK_PHP_044` §3.2
# found `ph53/controls/spellings.py:1349` citing its own must-fire negatives
# suite at `.temp/php42/negatives_spellings.py`, which is GITIGNORED and due for
# deletion under CLAUDE.md constraint 6.
#
# ⭐⭐ THE SUBCLASS IS WORSE THAN A DANGLING POINTER AND IT IS WHY THIS SCAN
# EXISTS: `PROTOCOL_PHP.md` §H says a validator change lands with its must-fire
# negatives OR IT DOES NOT LAND. If those negatives live in gitignored scratch,
# §H is satisfied in a way that DOES NOT SURVIVE A CHECKOUT -- the validator
# ships and the evidence that it can fail does not. RECAP_PHP.md open item 97.
#
# ⚠ Reported as a WARNING and in its own class, deliberately. Many of the 50-odd
# hits are historical notes about where work happened, which are harmless; the
# §H subclass is the one that costs something, so it is flagged separately
# instead of being drowned.
CONTROL_CLAIMS = sorted(d for d in glob.glob('patterns-php/*/controls/*')
                        if os.path.isfile(d) and '__pycache__' not in d)

# A citation is in the §H subclass when the CITING LINE is about the thing that
# makes a validator trustworthy. Matched on the line, not the path, because the
# path is often just `.temp/phNN/` -- it is the role that matters.
SEC_H_WORDS = re.compile(r'negative|must-fire|must-NOT-fire|selftest|self-test',
                         re.I)

COMMITTED = [d for d in CLAIMS if os.path.exists(d)]


def temp_cites(doc):
    return sorted({q for q in cited(open(doc, encoding='utf-8',
                                        errors='replace').read())
                   if q.startswith('.temp/')})


warn = []
for doc in COMMITTED:
    for q in temp_cites(doc):
        warn.append((doc, q, 'resolves TODAY' if exists(q) else 'ALREADY GONE'))
if warn:
    print('\n⚠ committed docs citing deletable `.temp/` scratch (rule 1):')
    for doc, q, st in warn:
        print(f'   {doc}  ->  {q}   [{st}]')
    print('   a committed claim should rest on a committed generator.')

# ⚠ The shared `why` block is BYTE-IDENTICAL across every row, and it carries
# PAT-era `.temp/` citations of its own. Reporting those once per row would bury
# the row-specific ones under 7x the noise -- so split them, and detect
# "inherited" MECHANICALLY (present in EVERY row's spec.md) rather than by a
# hand-maintained list that would go stale the moment the block is edited.
specs = sorted(glob.glob('patterns-php/*/spec.md'))
per_spec = {d: set(temp_cites(d)) for d in specs}
# ⛔⛔ THE `>= 2` IS LOAD-BEARING AND IT IS WHY `N2b` EXISTS.
# `set.intersection` over ONE set IS that set, so at a single row EVERY citation
# classifies as "inherited" and ALL of them are suppressed -- and the old `N2`
# still passed, because its own condition ("each present in all rows") is
# VACUOUSLY TRUE of one row. A checker that silently checks nothing
# (RECAP_PHP.md F10's shape, open item 88, found by TASK_PHP_043 §5.3).
# ⚠ I had asked whether the ADD direction breaks this. It does, and it breaks
#   LOUD, which is safe. The degenerate direction was the one I did not ask
#   about -- so a guard audit enumerates the DEGENERATE inputs (0 rows, 1 row,
#   all-identical), not the interesting ones.
INHERIT_MIN_ROWS = 2
inherited = (set.intersection(*per_spec.values())
             if len(per_spec) >= INHERIT_MIN_ROWS else set())
rowwarn = []
for doc in ROW_CLAIMS:
    for q in temp_cites(doc):
        if doc in per_spec and q in inherited:
            continue
        rowwarn.append((doc, q, 'resolves TODAY' if exists(q) else 'ALREADY GONE'))
if rowwarn:
    print('\n⚠⚠ ROW-SPECIFIC `.temp/` citations in a row\'s `spec.md` / '
          '`NOTES.md`:')
    for doc, q, st in rowwarn:
        hashed = ' ⛔ INSIDE THE HASHED CONTRACT' if doc.endswith('spec.md') \
                 else ''
        print(f'   {doc}  ->  {q}   [{st}]{hashed}')
    print('   ⛔ A `spec.md` citation is HASHED into `contract_sha256`, so '
          'repairing one\n      costs that row a re-gate -- which is exactly '
          'why it should not be written.')
# ---- the controls/ layer (item 97) -------------------------------------------
ctlwarn, ctl_h = [], []
for doc in CONTROL_CLAIMS:
    try:
        lines = open(doc, encoding='utf-8', errors='replace').read().split('\n')
    except OSError:
        continue
    for i, ln in enumerate(lines, 1):
        for q in {c for c in cited(ln) if c.startswith('.temp/')}:
            st = 'resolves TODAY' if exists(q) else 'ALREADY GONE'
            rec = (doc, i, q, st)
            ctlwarn.append(rec)
            if SEC_H_WORDS.search(ln):
                ctl_h.append(rec)
if ctl_h:
    print('\n⛔⛔ §H AT RISK -- a COMMITTED validator cites its NEGATIVES in '
          'gitignored `.temp/`:')
    for doc, i, q, st in ctl_h:
        print(f'   {doc}:{i}  ->  {q}   [{st}]')
    print('   ⛔ `PROTOCOL_PHP.md` §H: a validator change lands with its '
          'must-fire negatives\n      OR IT DOES NOT LAND. If they are '
          'gitignored, the validator ships and the\n      evidence that it can '
          'FAIL does not. Commit the suite, or move the arms\n      into the '
          'validator so they run on every invocation (RECAP_PHP.md item 97).')
if ctlwarn:
    others = len(ctlwarn) - len(ctl_h)
    gone = sum(1 for r in ctlwarn if r[3] == 'ALREADY GONE')
    print(f'\nⓘ `.temp/` citations inside committed `controls/*`: '
          f'{len(ctlwarn)} total across '
          f'{len({r[0] for r in ctlwarn})} file(s) -- {len(ctl_h)} in the §H '
          f'subclass above, {others} historical, {gone} ALREADY GONE.')
    print('   ⓘ `controls/*` is in `source_sha256`, so repairing one costs that '
          'row a\n      RE-GATE and not a re-measure. Batch with the row\'s next '
          'task.')

if inherited:
    print(f'\nⓘ {len(inherited)} `.temp/` citation(s) are INHERITED by all '
          f'{len(specs)} rows\' `spec.md`')
    print("   (the byte-identical shared `why` block, PAT-era). Repairing them "
          "is a\n   six-row PHP re-gate -- RECAP_PHP.md open items 55/61, not a "
          "row's debt:")
    for q in sorted(inherited):
        print(f'   {q}   [{"resolves TODAY" if exists(q) else "ALREADY GONE"}]')


def selftest():
    """⚠ `PROTOCOL_PHP.md` §H: a change to a validator lands with its must-fire
    negatives. These four are the 2026-09-12 row-scope extension's."""
    fails = []

    def ck(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print('SELFTEST -- the row-scope extension')
    # N1 MUST-FIRE: the CAPABILITY, not a specific instance.
    # ⚠⚠ ITS FIRST VERSION ASSERTED `ph53`'s `.temp/php41/...` citation IS FOUND
    #    -- and `TASK_PHP_042` REPAIRED that citation, so the negative that
    #    proved the defect existed could no longer fire. Same shape as
    #    `preimage_screen.py`'s finding probe: A DETECTOR FOR A DEFECT AND A
    #    REGRESSION TEST AGAINST ITS RETURN ARE NOT THE SAME ARTEFACT, and only
    #    the second belongs in a suite. ▶ Restated as the capability (the scan
    #    reaches a HASHED `spec.md` at all) plus N1c, the regression test for
    #    that repair.
    hashed = [(d, q) for d, q, _ in rowwarn if d.endswith('spec.md')]
    ck('N1', hashed,
       f'the scan reaches row `spec.md` contracts: {len(hashed)} row-specific '
       f'`.temp/` citation(s) inside a HASHED contract, e.g. {hashed[:2]}')
    # N1b MUST-FIRE: and `NOTES.md` too, or half the surface is unscanned.
    ck('N1b', [(d, q) for d, q, _ in rowwarn if d.endswith('NOTES.md')],
       'the scan also reaches row `NOTES.md`, not only `spec.md`')
    # N1c ⭐ THE REGRESSION TEST for `_042`'s repair (F99 discharged on ph53).
    #     MUST-NOT-FIRE: if a `ph53` citation ever comes back, this fails.
    back = [(d, q) for d, q, _ in rowwarn if 'ph53' in d]
    ck('N1c', not back,
       f'`ph53` carries NO row-specific `.temp/` citation -- `_042` repaired it '
       f'and it has not come back: {back}')
    # N2 MUST-FIRE: the shared-block PAT citations are classified INHERITED. If
    #    they were not, the row report would be 3x7 entries of noise and the
    #    real one would be invisible -- which is the failure mode this split
    #    exists to prevent.
    ck('N2', len(inherited) >= 1 and all(
        all(q in per_spec[d] for d in per_spec) for q in inherited),
       f'{len(inherited)} inherited citation(s), each present in ALL '
       f'{len(specs)} rows: {sorted(inherited)}')
    # ⛔ N2b MUST-FIRE ON THE DEGENERATE INPUT -- the negative item 88 installs.
    #    Re-run the split over ONE row and over ZERO rows and assert that
    #    NOTHING is suppressed. Without `INHERIT_MIN_ROWS` the one-row case
    #    suppresses EVERY citation and `N2` above still passes.
    def _inherited_over(sets):
        return (set.intersection(*sets)
                if len(sets) >= INHERIT_MIN_ROWS else set())

    one = [per_spec[specs[0]]] if specs else [{'x'}]
    ck('N2b', _inherited_over(one) == set() and _inherited_over([]) == set(),
       f'at ONE row ({len(one[0])} citation(s)) and at ZERO rows the inherited '
       f'set is EMPTY, so nothing is suppressed -- the old code returned the '
       f'single row\'s whole set here and hid every citation in it')

    # ⚠ N2c MUST-NOT-FIRE: the guard must not change today's real answer.
    #    If it did, the repair would be buying safety with a false report.
    ck('N2c', _inherited_over(list(per_spec.values())) == inherited,
       f'the guard is inert at the real {len(specs)}-row corpus: still '
       f'{len(inherited)} inherited')

    # N3 MUST-NOT-FIRE: a committed `controls/` citation must NOT be reported.
    #    `ph53` retargeted two of its three citations at
    #    `controls/mu_unwrapped.rs`; if those showed up, the check would be
    #    punishing the repair.
    ck('N3', not [q for _, q, _ in rowwarn if 'controls/' in q],
       'no `controls/` citation is reported -- the repair is not punished')
    # ⛔ N5 MUST-FIRE (capability): the scan REACHES `controls/*` at all.
    #    Without this arm, narrowing CONTROL_CLAIMS back to nothing would pass.
    ck('N5', len(ctlwarn) >= 1 and len({r[0] for r in ctlwarn}) >= 2,
       f'the scan reaches committed `controls/*`: {len(ctlwarn)} citation(s) '
       f'across {len({r[0] for r in ctlwarn})} file(s) -- e.g. '
       f'{ctlwarn[0][0].split("/")[-1] if ctlwarn else "-"}')

    # ⛔⛔ N5b MUST-FIRE: the §H subclass is DETECTED, and it is not one row.
    #    This is the arm that matters. `TASK_PHP_044` §3.2 reported ONE instance
    #    (ph53); the scan finds it is systemic -- every row's `spellings.py` and
    #    `negatives.py` cites its must-fire suite in gitignored `.temp/`.
    #    ⚠ If this arm ever reads 0, either the debt is discharged (check the
    #    rows) or the detector broke (check SEC_H_WORDS).
    h_rows = {r[0].split('/')[1] for r in ctl_h}
    ck('N5b', len(ctl_h) >= 1,
       f'the §H subclass is detected: {len(ctl_h)} citation(s) across '
       f'{len(h_rows)} row(s) {sorted(h_rows)} -- a committed validator whose '
       f'must-fire negatives are gitignored satisfies §H in a way that does not '
       f'survive a checkout')

    # ⚠ N5c MUST-NOT-FIRE: `__pycache__` is not a claim. A `.pyc` carries the
    #   same strings as its source and would double every hit.
    ck('N5c', not [d for d in CONTROL_CLAIMS if '__pycache__' in d
                   or d.endswith('.pyc')],
       'no `__pycache__` / `.pyc` in CONTROL_CLAIMS -- a compiled copy carries '
       'the same strings and would double every hit')

    # ⚠ N5d / N4 MUST-NOT-FIRE: both extensions (the `controls/*` layer and the
    #   row `spec.md`/`NOTES.md` layer) are WARNINGS and must not feed the
    #   LIVE-doc failure count.
    #
    # ⛔⛔⛔ THESE TWO ARMS ASSERTED `rot == 0` UNTIL 2026-09-15, AND THEY HAD
    #   BEEN FAILING FOR 43 COMMITS WITH THE SWEEP PRINTING `ok` THE WHOLE TIME.
    #   Written at `4297b1d` when the live rot happened to be 0, they pinned that
    #   ABSOLUTE value while their own message makes a RELATIVE claim
    #   ("untouched by this extension"). The standing adjudicated false positive
    #   arrived at `3448a5a` the next day, rot became 1, and both arms went red
    #   -- blaming an extension that had nothing to do with it.
    #   ⭐ NOTHING CAUGHT IT because `citecheck` is the one checker registered
    #   `expect=1` (it carries that standing rot), `checkers.py` judges by
    #   `rc == expect`, and a failing arm exits 1 exactly like the standing rot
    #   does. THE EXIT CODE COULD NOT TELL THEM APART -- which is the warning
    #   `.tasks-php/README.md` already gives for the BARE run ("read the COUNT,
    #   never the exit code") and which nobody inherited for the SELFTEST run.
    #   ⚠ `.memory-php/04-process.md` law 6: a bound is not a derivation, and a
    #   pinned figure goes stale. This is the EIGHTH in `.tasks-php/` validators.
    #
    # ▶ THE REPAIR IS THE RELATIVE CLAIM, STATED STRUCTURALLY AND INDEPENDENT OF
    #   HOW MANY ROTS EXIST: the rot-bearing set is `LIVE`, derived from `DOCS`;
    #   the extensions read `CONTROL_CLAIMS` and `patterns-php/*/spec.md`. The
    #   inertness the arms claim is exactly that those sets are DISJOINT, so no
    #   extension input can ever reach `rot`. That is checkable at any rot value.
    _live = set(LIVE)
    _ext = set(CONTROL_CLAIMS) | set(specs) | {
        d.replace('/spec.md', '/NOTES.md') for d in specs}
    ck('N5d', not (_live & _ext),
       f'the controls/ + row layers are DISJOINT from the rot-bearing LIVE set '
       f'({len(_live)} live docs, {len(_ext)} extension inputs, '
       f'{len(_live & _ext)} shared) -- so no extension input can reach `rot`, '
       f'whatever `rot` happens to be (it is {rot} today)')

    # N4 MUST-FIRE (capability): and the extensions are actually POPULATED, or
    #   "disjoint" would be satisfied vacuously by an extension that reads
    #   nothing -- which is the shape N5b guards against one layer down.
    ck('N4', len(_ext) > 0 and len(_live) > 0,
       f'both sets are non-empty, so N5d\'s disjointness is a real separation '
       f'and not an empty one: {len(_live)} live, {len(_ext)} extension')

    # ⛔ N6 MUST-FIRE: BOTH report spellings are benign, and a non-report is NOT.
    #    The arm for the F117 repair above. Without the last clause, widening
    #    `_REPORT` to something sloppy would pass and this checker would go
    #    quiet on real rot.
    ck('N6a', benign('x', '.tasks-php/TASK_PHP_056_REPORT.md'),
       'a plain `_REPORT.md` that does not exist yet is benign (unchanged)')
    ck('N6b', benign('x', '.tasks-php/TASK_PHP_054_REPORT_E2E3E4.md'),
       '⭐ a SPLIT `_REPORT_E2E3E4.md` is benign too -- the three-report task '
       'that made rot read 4, which every document mis-explained as "rot rises '
       'per in-flight task"')
    ck('N6c', not benign('x', '.tasks-php/TASK_PHP_056.md')
       and not benign('x', 'patterns-php/ph97-x/spec.md'),
       'MUST-NOT-FIRE: a task SPEC and a row file are still rot when missing -- '
       'the widening did not swallow the checker')

    # ⛔⛔ N6d MUST-FIRE: the LIVE/HIST PARTITION AND `benign()` USE THE SAME
    #   PREDICATE. This is the arm that was missing. F122's repair widened
    #   `benign()` and left `LIVE`/`HIST` on `endswith('_REPORT.md')`, so a
    #   SPLIT-named report was benign in one half and a live doc in the other --
    #   SIX reports on the wrong side (TASK_PHP_001's three, TASK_PHP_054's
    #   three). ⭐ `N6a`/`N6b`/`N6c` all passed throughout, because every one of
    #   them tests `benign()` and none of them tests the PARTITION.
    #   ▶ THE LESSON, and it is item 124's class one level down: when a repair
    #   has two limbs, the arm must assert they AGREE, not that each works.
    _split = '.tasks-php/TASK_PHP_054_REPORT_E2E3E4.md'
    _plain = '.tasks-php/TASK_PHP_055_REPORT.md'
    _spec = '.tasks-php/TASK_PHP_054.md'
    ck('N6d', all(_is_report(d) == benign('x', d) for d in (_split, _plain))
       and not _is_report(_spec) and not benign('x', _spec)
       and not any(_is_report(d) for d in LIVE),
       'the LIVE/HIST partition and benign() agree on BOTH report spellings and '
       f'on a task spec, and no LIVE doc is a report: {len(LIVE)} live, '
       f'{len(HIST)} historical')
    print()
    print('SELFTEST ' + ('PASS' if not fails else f'FAIL {fails}'))
    return 1 if fails else 0


if '--selftest' in sys.argv:
    sys.exit(selftest())
sys.exit(1 if rot else 0)
