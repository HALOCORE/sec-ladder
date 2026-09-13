#!/usr/bin/env python3
"""The RECAP_PHP.md invariants, checked rather than remembered.

    python3 .tasks-php/boxcheck.py     # from the repo root; rc!=0 on failure

The START HERE box has broken its own <= 20-line cap FIVE times, and every
time it was noticed by eye after the commit. It is one command.
"""
import re, sys, glob, collections

s = open('RECAP_PHP.md', encoding='utf-8').read()
fail = []

m = re.search(r'## ▶ START HERE.*?\n```\n(.*?)```', s, re.S)
if not m:
    fail.append('START HERE box not found')
else:
    n = len(m.group(1).rstrip('\n').split('\n'))
    print(f'box lines          {n:4}  (cap 20)')
    if n > 20: fail.append(f'START HERE box is {n} lines, cap is 20')

nums = re.findall(r'^### (F[0-9]+)', s, re.M)
dups = [k for k, v in collections.Counter(nums).items() if v > 1]
print(f'findings           {len(nums):4}  highest {max(nums, key=lambda x: int(x[1:]))}')
if dups: fail.append(f'duplicate finding headings: {dups}')

print(f'file size          {len(s)//1024:4} KB')

for label, cmd in (('catalogue rows', r"^\| ph[0-9]"),):
    rows = len(re.findall(cmd, open('patterns-php/CATALOGUE.md',
                                    encoding='utf-8', errors='replace').read(), re.M))
    print(f'{label:18} {rows:4}')

# ---- `.memory-php/`'s "findings F1-FNN live in RECAP_PHP.md" headers. --------
# ⚠⚠⚠ WHY THIS IS HERE: those five lines have now gone STALE THREE TIMES --
# `F1-F41` while 49 findings existed, then `F1-F48`, then `F1-F90` while 101
# did -- and the lines THEMSELVES carry a warning about it (`PROTOCOL.md`
# rule 13). Twice it was repaired by hand and twice it came back. A pointer
# that names a range has to be checked or it will rot again, and the highest
# finding is already computed two blocks up.
hi = max(int(k[1:]) for k in nums)
mem_bad = []
for mf in sorted(glob.glob('.memory-php/*.md')):
    txt = open(mf, encoding='utf-8', errors='replace').read()
    # the header sentence, in either dash; the FIRST is the live pointer and
    # any later ones are the struck record of what it used to say.
    r = re.search(r'findings \*\*F1[–-]F([0-9]+)\*\*', txt)
    if not r:
        mem_bad.append((mf, 'no `findings **F1-FNN**` pointer'))
    elif int(r.group(1)) != hi:
        mem_bad.append((mf, f'says F1-F{r.group(1)}, actual highest is F{hi}'))
print(f'{".memory-php/ range":18} {len(glob.glob(".memory-php/*.md")):4}  '
      f'file(s), {len(mem_bad)} stale')
for mf, why in mem_bad:
    fail.append(f'{mf}: {why}')

for f in fail: print('FAIL:', f)
sys.exit(1 if fail else 0)
