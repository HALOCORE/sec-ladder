#!/usr/bin/env python3
"""Does `patterns-php/CATALOGUE.md` account for all 166 corpus rows?

    python3 .tasks-php/coverage.py         # from the repo root; writes nothing

Parses Part A's `corpus rows` column and Part C's kill tables out of the
catalogue itself (so the check tracks the document, not a copy of it) and diffs
against the corpus index's `input_id` column.

⚠⚠ THIS IS A PROMOTED COPY OF `.temp/php11/coverage.py`, WHICH IS GITIGNORED
SCRATCH AND EXISTED IN FOUR DIVERGENT COPIES (85 / 75 / 39 / 19 lines). The
`166/166` that the catalogue's coverage claim rests on was reproducible only
from a file the repo does not carry and `CLAUDE.md` rule 1 mandates deleting.
That is the hazard `SOURCES.md` §1 already names for the tarball, on the check
rather than on the corpus.

TWO REPAIRS AGAINST THE SCRATCH ORIGINAL (`RECAP_PHP.md` F49):

  1. The row regexes were `ph\\d\\d` and `\\*\\*(ph\\d\\d) `, blind to ph100+.
  2. The `gaps:` set was built from `range(1, len(rows)+1)` -- ITS OWN HIT COUNT
     -- so a row it could not see shrank the expected set by exactly one and the
     gap list stayed empty. The check could not report its own blindness. It is
     now built from the observed id RANGE, so an unseen id shows up as a gap.

⚠ The `accounted for: N/166` figure was NEVER affected by (1): `covered` is
built from `line.startswith("| ph")`, not from the regex. F49 said so and it is
correct -- verified here by keeping both computations side by side.

Exits 1 on any missing/duplicate/unknown id, 2 if it cannot evaluate.
"""
import csv, os, re, sys

CAT = 'patterns-php/CATALOGUE.md'
CSV = ('/home/apt/repos_common/php-in-safe-rust/paper/evaluation/security/'
       'vuln-corpus-5.0/index.csv')
CSV = os.environ.get('PHP_CORPUS_INDEX', CSV)

ID = re.compile(r'\b((?:CRASH|LOGIC|V5C)-\d{3})\b')


def die(msg):
    print(f'CANNOT EVALUATE: {msg}')
    sys.exit(2)


def main():
    if not os.path.exists(CAT):
        die(f'{CAT} not found -- run from the repo root')
    if not os.path.exists(CSV):
        die(f'corpus index not found at {CSV}\n'
            f'  it lives in ANOTHER project\'s tree and is not ours to keep alive;\n'
            f'  set PHP_CORPUS_INDEX=<path> to point at a copy.')

    with open(CSV, newline='', encoding='utf-8', errors='replace') as fh:
        rows_csv = list(csv.DictReader(fh))
    corpus = [r['input_id'] for r in rows_csv]
    if not corpus:
        die(f'{CSV} parsed to zero rows -- wrong file, or no `input_id` column')
    corpus_set = set(corpus)

    # ⚠ THE CORPUS HAS A THIRD NAMESPACE. Beside `input_id` (CRASH-/LOGIC-) each
    # row carries a `v5c_id`, and rows the corpus merged away survive only in the
    # surviving row's `merged_members`. The catalogue legitimately cites those --
    # `ph03` carries `CRASH-115, V5C-116` because V5C-116 was merged into V5C-115.
    # Diffing against `input_id` alone reports all three as unknown ids, which is
    # what the block pasted into CATALOGUE.md C.7 says, and it is a limitation of
    # the check rather than a defect in the catalogue.
    merged = {}                                  # merged-away id -> surviving input_id
    for r in rows_csv:
        for m in ID.finditer(r.get('merged_members') or ''):
            merged[m.group(1)] = r['input_id']
    known = corpus_set | {r['v5c_id'] for r in rows_csv} | set(merged)
    print(f'corpus rows in index.csv   : {len(corpus)}'
          f'   (+{len(merged)} merged-away ids named in `merged_members`)')

    text = open(CAT, encoding='utf-8', errors='replace').read()

    # ---- Part A: the `corpus rows` column of every `| phNN | ... |` row
    covered = {}
    for line in text.splitlines():
        if not line.startswith('| ph'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 8:
            continue
        for m in ID.finditer(cells[5]):
            covered.setdefault(m.group(1), []).append(cells[0])

    # ---- Part C: a kill-table row names its corpus id(s) in the first cell,
    # possibly bold -- match on the id, not on the line's first characters.
    if '## Part C' not in text:
        die('no `## Part C` heading -- the kill list is where killed ids are named')
    partc = text.split('## Part C')[1]
    killed = set()
    for line in partc.splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or not ID.search(cells[0]):
            continue
        killed.update(m.group(1) for m in ID.finditer(cells[0]))

    print(f'Part A distinct corpus ids : {len(covered)}')
    print(f'Part C kill-table ids      : {len(killed)}  {sorted(killed)}')

    accounted = set(covered) | killed
    missing = sorted(corpus_set - accounted)
    cited_merged = sorted(a for a in accounted if a in merged)
    unknown = sorted(accounted - known)
    print(f'\naccounted for              : {len(accounted & corpus_set)} / {len(corpus_set)}')
    print(f'MISSING (in corpus, not in catalogue) : {len(missing)}')
    for m in missing:
        print(f'   {m}')
    print(f'merged-away ids the catalogue cites   : {len(cited_merged)}   '
          f'(legitimate -- resolved via `merged_members`)')
    for a in cited_merged:
        print(f'   {a:<11} merged into {merged[a]}  by rows {covered.get(a, ["(kill list)"])}')
    print(f'ids in NO corpus namespace at all     : {len(unknown)}  {unknown or ""}')

    dup = {k: v for k, v in covered.items() if len(v) > 1}
    print(f'\nids claimed by MORE THAN ONE catalogue row : {len(dup)}')
    for k, v in sorted(dup.items()):
        print(f'   {k:<11} {v}')

    # ---- row sanity. `ph\d+`, and gaps from the observed RANGE.
    rows = re.findall(r'^\| (ph\d+) \|', text, re.M)
    blocks = re.findall(r'^\*\*(ph\d+) ', text, re.M)
    if not rows:
        die('no `| phNN |` rows matched in Part A -- the table format changed')
    nums = sorted(int(r[2:]) for r in rows)
    gaps = sorted(set(range(min(nums), max(nums) + 1)) - set(nums))
    print(f'\ncatalogue rows in Part A : {len(rows)}  (ids ph{min(nums):02d}..ph{max(nums):02d},'
          f' gaps: {["ph%02d" % g for g in gaps] or "none"})')
    print(f'Part B blocks            : {len(blocks)}'
          f'  (in Part A but not Part B: {sorted(set(rows) - set(blocks)) or "none"})')

    # the blindness the scratch original could not report, made explicit
    wide = re.findall(r'^\| (ph\d+) \|', text, re.M)
    narrow = re.findall(r'^\| (ph\d\d) \|', text, re.M)
    if len(wide) != len(narrow):
        print(f'\n⭐ the old `ph\\d\\d` regex would have seen {len(narrow)} of these'
              f' {len(wide)} rows, missing {sorted(set(wide) - set(narrow))}'
              f'\n  -- and would still have printed `gaps: none`. That is F49.')

    bad = bool(missing or unknown or dup or gaps or set(rows) - set(blocks))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
