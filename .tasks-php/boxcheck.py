#!/usr/bin/env python3
"""The RECAP_PHP.md invariants, checked rather than remembered.

    python3 .tasks-php/boxcheck.py     # from the repo root; rc!=0 on failure

The START HERE box has broken its own <= 20-line cap FIVE times, and every
time it was noticed by eye after the commit. It is one command.
"""
import re, sys, collections

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

for f in fail: print('FAIL:', f)
sys.exit(1 if fail else 0)
