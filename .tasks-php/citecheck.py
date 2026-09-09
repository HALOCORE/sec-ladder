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
COMMITTED = [d for d in CLAIMS if os.path.exists(d)]
warn = []
for doc in COMMITTED:
    for p in sorted({p for p in cited(open(doc, encoding='utf-8',
                                           errors='replace').read())
                     if p.startswith('.temp/')}):
        warn.append((doc, p, 'resolves TODAY' if exists(p) else 'ALREADY GONE'))
if warn:
    print('\n⚠ committed docs citing deletable `.temp/` scratch (rule 1):')
    for doc, p, st in warn:
        print(f'   {doc}  ->  {p}   [{st}]')
    print('   a committed claim should rest on a committed generator.')

sys.exit(1 if rot else 0)
