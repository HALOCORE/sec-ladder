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

def benign(doc, p):
    """A missing path is EXPECTED, not rot, when:"""
    if p in BENIGN: return True
    if p.endswith('_REPORT.md'): return True          # a report not yet written
    # scratch under .temp/ is re-derivable and CLAUDE.md rule 1 mandates deleting
    # it once the gates are green -- a historical report citing its own deleted
    # blobs is the rule working, not a broken pointer.
    if p.startswith('.temp/'): return True
    # a php gate record keys common-php/ sources under the frozen common/ prefix
    # (harness-php/root.py's rebinding -- RECAP_PHP.md open item 33)
    if p.startswith(('common/', 'common-php/layout', 'patterns/ph00-smoke')): return True
    return False

LIVE = [d for d in DOCS if not d.endswith('_REPORT.md')]
HIST = [d for d in DOCS if d.endswith('_REPORT.md')]

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
inherited = set.intersection(*per_spec.values()) if per_spec else set()
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
    # N1 MUST-FIRE: the citation that motivated the extension is FOUND and is
    #    classified row-specific, not inherited.
    hit = [(d, q) for d, q, _ in rowwarn if 'php41' in q and 'ph53' in d]
    ck('N1', hit,
       f'ph53 spec.md/NOTES.md `.temp/php41/...` found as ROW-SPECIFIC: {hit}')
    # N1b MUST-FIRE: and specifically inside the HASHED spec.md, which is the
    #     part that costs a re-gate.
    ck('N1b', any(d.endswith('spec.md') for d, _ in hit),
       'at least one is in spec.md (hashed), not only NOTES.md')
    # N2 MUST-FIRE: the shared-block PAT citations are classified INHERITED. If
    #    they were not, the row report would be 3x7 entries of noise and the
    #    real one would be invisible -- which is the failure mode this split
    #    exists to prevent.
    ck('N2', len(inherited) >= 1 and all(
        all(q in per_spec[d] for d in per_spec) for q in inherited),
       f'{len(inherited)} inherited citation(s), each present in ALL '
       f'{len(specs)} rows: {sorted(inherited)}')
    # N3 MUST-NOT-FIRE: a committed `controls/` citation must NOT be reported.
    #    `ph53` retargeted two of its three citations at
    #    `controls/mu_unwrapped.rs`; if those showed up, the check would be
    #    punishing the repair.
    ck('N3', not [q for _, q, _ in rowwarn if 'controls/' in q],
       'no `controls/` citation is reported -- the repair is not punished')
    # N4 MUST-NOT-FIRE: the extension is a WARNING and must not change the
    #    failure count for the live manager docs.
    ck('N4', rot == 0,
       f'the LIVE-doc rot count is untouched by this extension: {rot}')
    print()
    print('SELFTEST ' + ('PASS' if not fails else f'FAIL {fails}'))
    return 1 if fails else 0


if '--selftest' in sys.argv:
    sys.exit(selftest())
sys.exit(1 if rot else 0)
