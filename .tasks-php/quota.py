#!/usr/bin/env python3
"""Re-derive `QUOTA_001.md`'s numbers from `CATALOGUE.md`, instead of counting by hand.

    python3 .tasks-php/quota.py            # from the repo root

QUOTA_001.md's family sizes, the 20-family count and the "both built rows are
S1" fact were all counted by hand, once, against a 93-row catalogue that was
already being edited by two running tasks. This makes them re-derivable.

⚠⚠ IT IS NOT IN `harness-php/`, DELIBERATELY. Adding a file there moves the php
preflight record and costs a re-gate on every built row; this is a manager tool
and it never writes anything.

⚠⚠ IF IT CANNOT PARSE, IT SAYS SO AND EXITS NON-ZERO. It never prints a number
it could not derive -- that failure mode (a probe that renders both its success
and its failure as a positive claim) put a false figure into RECAP F44.
"""
import re, sys, os, glob, collections

CAT = 'patterns-php/CATALOGUE.md'

def die(msg):
    print(f'CANNOT EVALUATE: {msg}')
    sys.exit(2)

if not os.path.exists(CAT):
    die(f'{CAT} not found -- run from the repo root')
text = open(CAT, encoding='utf-8', errors='replace').read()
lines = text.splitlines()

# --- the three parts -------------------------------------------------------
def find(pat):
    hits = [i for i, l in enumerate(lines) if re.match(pat, l)]
    return hits

a = find(r'^## Part A\b'); b = find(r'^## Part B\b'); c = find(r'^## Part C\b')
if len(a) != 1 or len(b) != 1 or len(c) != 1:
    die(f'expected exactly one each of Part A/B/C headings, got {len(a)}/{len(b)}/{len(c)}')
A, B, C = a[0], b[0], c[0]
if not A < B < C:
    die(f'Part A/B/C are out of order at lines {A},{B},{C}')

partA, partB = lines[A:B], lines[B:C]

# --- Part A: the table, and the declared section counts --------------------
rowA = [m.group(1) for l in partA if (m := re.match(r'^\|\s*(ph\d+)\s*\|', l))]
if not rowA:
    die('no `| phNN |` rows found in Part A')

secA = []                                    # (heading, declared, counted)
cur = None
for l in partA:
    if m := re.match(r'^### (.+?)\s*\((\d+)\)\s*$', l):
        cur = [m.group(1), int(m.group(2)), 0]
        secA.append(cur)
    elif re.match(r'^\|\s*ph\d+\s*\|', l) and cur:
        cur[2] += 1

# --- Part B: family headings and per-row blocks ----------------------------
axis = None
fam = None
famrows = collections.OrderedDict()          # 'S1' -> [phNN, ...]
famname = {}
famaxis = {}
rowB = []
for l in partB:
    if m := re.match(r'^## ([A-Z][A-Z /]+)\s*$', l):
        axis = m.group(1).strip()
    elif m := re.match(r'^### ([STE]\d+)\s*[-—]+\s*(.+?)\s*$', l):
        fam = m.group(1)
        famrows.setdefault(fam, [])
        famname[fam] = m.group(2)
        famaxis[fam] = axis
    elif m := re.match(r'^\*\*(ph\d+)\s*·', l):
        if fam is None:
            die(f'row {m.group(1)} appears before any `### Sn --` family heading')
        famrows[fam].append(m.group(1))
        rowB.append(m.group(1))

if not rowB:
    die('no `**phNN ·` blocks found in Part B')

# --- built rows ------------------------------------------------------------
# ⛔⛔ FIXED 2026-09-14 (RECAP_PHP.md item 114).  This used to glob
# `patterns-php/ph*/` -- i.e. it counted a DIRECTORY, not a built row -- and it
# agreed with the truth for NINE ROWS only because no row had ever existed in a
# half-built state: every previous row went from nothing to fully gated inside
# one task.  `TASK_PHP_051` stopped mid-row with `ph56`'s C and Rust rungs on
# disk and no `spec.md`, no `verus.rs` and no gate record, and this tool
# immediately reported `built 10`.
#
# ⭐ The right definition was already written down in `RECAP_PHP.md`'s own STATE
# cell -- *"count it: `ls results-php/gate/ | grep -av ph00 | wc -l`"* -- so the
# repo knew it and this file used a different one.  A ROW IS BUILT WHEN IT HAS A
# GATE RECORD.
GATE_DIR = 'results-php/gate'
built = sorted(m.group(1)
               for f in glob.glob(os.path.join(GATE_DIR, 'ph*.json'))
               for m in [re.match(r'.*/(ph\d+)', f)]
               if m and 'smoke' not in f)

# ⭐ A directory with no gate record is IN PROGRESS, and saying so is the whole
# point: it is neither "built" (it has no verdict) nor absent (work exists).
_dirs = sorted(m.group(1)
               for d in glob.glob('patterns-php/ph*/')
               for m in [re.match(r'.*/(ph\d+)', d)]
               if m and 'smoke' not in d)
in_progress = [r for r in _dirs if r not in built]
orphan_records = [r for r in built if r not in _dirs]

fam_of = {r: f for f, rs in famrows.items() for r in rs}

# --- report ----------------------------------------------------------------
print(f'{CAT}\n')
print(f'  Part A rows      {len(rowA)}')
print(f'  Part B blocks    {len(rowB)}')
if len(rowA) != len(rowB):
    print(f'  ⚠ MISMATCH: Part A has {len(rowA)}, Part B has {len(rowB)}')
onlyA, onlyB = set(rowA) - set(rowB), set(rowB) - set(rowA)
if onlyA: print(f'  ⚠ in A not B: {sorted(onlyA)}')
if onlyB: print(f'  ⚠ in B not A: {sorted(onlyB)}')
dupA = [r for r, n in collections.Counter(rowA).items() if n > 1]
if dupA: print(f'  ⚠ duplicated in Part A: {dupA}')

print(f'\n  families         {len(famrows)}')
print(f'  built rows       {len(built)}  {built}')
if in_progress:
    print(f'  ⏳ IN PROGRESS    {len(in_progress)}  {in_progress}'
          f'   <- a row DIRECTORY with NO gate record. NOT counted as built.')
if orphan_records:
    print(f'  ⛔ ORPHAN RECORD  {len(orphan_records)}  {orphan_records}'
          f'   <- a gate record whose row directory is GONE. Investigate.')

print('\n--- Part A section headers: declared vs counted ---')
tot_dec = tot_cnt = 0
for name, dec, cnt in secA:
    tot_dec += dec; tot_cnt += cnt
    flag = '' if dec == cnt else f'   <== DRIFT, declared {dec}'
    print(f'  {name:<28} {cnt:>3}{flag}')
print(f'  {"TOTAL":<28} {tot_cnt:>3}   (headers declare {tot_dec}, table has {len(rowA)})')

print('\n--- families, and the quota (QUOTA_001 rule: min 2, cap 4) ---')
print(f'  {"fam":<4} {"n":>3}  {"built":>5}  status   name')
owed = 0
for f, rs in famrows.items():
    nb = sum(1 for r in rs if r in built)
    if nb == 0:   st, need = 'OWES 2', 2
    elif nb == 1: st, need = 'OWES 1', 1
    else:         st, need = 'open',   0     # open until a row moves no answer; cap 4
    owed += need
    # ⚠ this used to read '<== both built rows', which was true only while the
    # tree had exactly two. Name the rows instead of counting them.
    mark = ('  <== ' + ', '.join(r for r in rs if r in built)) if nb >= 2 else ''
    print(f'  {f:<4} {len(rs):>3}  {nb:>5}  {st:<7}  {famname.get(f,"?")[:44]}{mark}')

print(f'\n  minimum rows still owed to reach 2/family: {owed}')
print(f'  floor = {len(famrows)} families x 2 = {len(famrows)*2} rows;'
      f' built {len(built)}; remaining {len(famrows)*2 - len(built)}')
print('\n  ⚠ "min 2" is a FLOOR, not a target: a family stays OPEN until a new row')
print('    moves none of PLAN_PHP.md §9\'s six answers, cap 4. So this is the')
print('    cheapest possible programme, not the expected one.')

axes = collections.Counter()
for f, rs in famrows.items():
    axes[famaxis.get(f, '?')] += len(rs)
print('\n--- rows per axis (Part B) ---')
for k, v in axes.items():
    print(f'  {k:<22} {v:>3}')

# --- the cross-check that names names --------------------------------------
# Part A files a row under a section heading; Part B files it under a family,
# which sits under an axis. When they disagree, the row is filed twice and one
# of them is wrong. Counting alone shows only that the totals differ.
sec_of = {}
cur = None
for l in partA:
    if m := re.match(r'^### (.+?)\s*\(\d+\)\s*$', l):
        cur = m.group(1)
    elif (m := re.match(r'^\|\s*(ph\d+)\s*\|', l)) and cur:
        sec_of[m.group(1)] = cur

NORM = {'spatial': 'SPATIAL', 'type / initialisation': 'TYPE / INITIALISATION',
        'temporal': 'TEMPORAL'}
misfiled = []
for r in rowB:
    sa, fb = sec_of.get(r), famaxis.get(fam_of.get(r))
    if sa is None or fb is None:
        continue
    if NORM.get(sa.strip().lower()) != fb:
        misfiled.append((r, sa, fam_of[r], fb))

print('\n--- Part A section vs Part B axis, per row ---')
if not misfiled:
    print('  ✅ every row is filed under the same axis in both parts')
else:
    for r, sa, f, fb in misfiled:
        print(f'  ⚠ {r}: Part A files it under "{sa}", Part B under {f} ({fb})')
    print(f'  {len(misfiled)} row(s) filed under different axes in the two parts')

# --- §H negatives, INSIDE the tool, on every invocation ---------------------
# PROTOCOL_PHP.md §H: a validator change lands with its must-fire negatives or it
# does not land.  These pin the item-114 repair: `built` must mean "has a gate
# record", never "has a directory".
print('\n--- §H negatives ---')
_neg = []

# N1 MUST-FIRE: a directory with no gate record is IN PROGRESS, not built.
#    Live reach: `ph56` today.  If this list is ever empty the arm is vacuous
#    and says so, rather than passing silently (F10).
if in_progress:
    ok = all(r not in built for r in in_progress)
    print(f'  N1 MUST-FIRE      in-progress rows excluded from `built`: '
          f'{in_progress} -> {"OK" if ok else "FAIL"}')
    if not ok:
        _neg.append('N1: an in-progress row is being counted as built')
else:
    print('  N1 MUST-FIRE      ⓘ VACUOUS TODAY -- no row is half-built. '
          'The arm cannot fire; it is not passing.')

# N2 MUST-FIRE: every `built` row really has a gate record on disk.
_missing = [r for r in built
            if not glob.glob(os.path.join(GATE_DIR, r + '*.json'))]
print(f'  N2 MUST-FIRE      every built row has a gate record: '
      f'{len(_missing)} missing -> {"OK" if not _missing else "FAIL"}')
if _missing:
    _neg.append(f'N2: `built` contains rows with no gate record: {_missing}')

# N3 MUST-NOT-FIRE: ph00-smoke is a relocated PAT calibration kernel with no PHP
#    provenance.  It has a gate record and must never be counted.
print(f'  N3 MUST-NOT-FIRE  ph00 excluded: '
      f'{"OK" if not any(r.startswith("ph00") for r in built) else "FAIL"}')
if any(r.startswith('ph00') for r in built):
    _neg.append('N3: ph00-smoke is being counted as a corpus row')

# N4 MUST-FIRE: the directory glob and the record glob must not have silently
#    become the same set for the wrong reason -- if a row directory vanished
#    while its record survived, that is a deletion nobody announced.
print(f'  N4 MUST-FIRE      no orphan gate records: '
      f'{len(orphan_records)} -> {"OK" if not orphan_records else "FAIL"}')
if orphan_records:
    _neg.append(f'N4: gate record(s) with no row directory: {orphan_records}')

if _neg:
    print(f'\n⛔ {len(_neg)} NEGATIVE(S) FAILED:')
    for n in _neg:
        print('   -', n)

bad = (len(rowA) != len(rowB)) or onlyA or onlyB or dupA \
      or (tot_dec != len(rowA)) or misfiled or _neg
sys.exit(1 if bad else 0)
