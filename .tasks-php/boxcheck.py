#!/usr/bin/env python3
"""The RECAP_PHP.md invariants, checked rather than remembered.

    python3 .tasks-php/boxcheck.py     # from the repo root; rc!=0 on failure

The START HERE box has broken its own <= 20-line cap FIVE times, and every
time it was noticed by eye after the commit. It is one command.

⭐ `rule9_rows()` is a PURE function over the document text so that its
must-fire negatives can plant a defect in a STRING rather than in the committed
file -- `.tasks-php/probes/rule9_mustfire.py`, `PROTOCOL_PHP.md` §H.
"""
import re, sys, glob, collections

# The live RULE-9 table: its header row, then every `> |` row until the first
# bare `>` line. ⚠ Scoped deliberately -- the block also holds DATED SNAPSHOT
# tables (the `_047` one keys its findings in column TWO) and the `F96`
# per-group table, and neither is an index of cycles.
_R9 = re.compile(r'^> \| finding \| verdict \|.*?\n(.*?)(?=^> *$)', re.S | re.M)

# ⭐⭐ MODULE-LEVEL ON PURPOSE. `probes/rule9_mustfire.py` kept its OWN COPY of
# this pattern and the two DIVERGED: the copy was the narrow, pre-widening form,
# so the must-fire arm that exists to prove the widening works **passed without
# the widening** -- its `_063` case matched on `is a REVIEWER`, not on the round
# spelling the widening added. ⛔ F131 (one home per fact) and F138 (`"I called
# the tool's function" is not "I ran the tool"`), in the harness that polices
# this very arm. ▶ There is now ONE regex and the probe imports it.
ROUTE = re.compile(r"(▶|and it)[^|]{0,80}?"
                   r"(is a REVIEWER|Give it to a reviewer|a reviewer can rule"
                   r"|belongs in the round|THE REVIEWER SAYS"
                   r"|a REVIEWER'?s\b|goes to `_0[0-9]+`|\*\*`_0[0-9]+`\*\*"
                   r"|scope (it|them) into|_0[0-9]+ beside)", re.I)

_STRUCK = re.compile(r'~~.*?~~', re.S)


def unstruck(t):
    """PURE. Drop `~~struck~~` spans -- a struck route is a HISTORICAL route.

    ⚠⚠ WHY: after `_063` ruled all nine routed items, five still printed as
    `LIVE, unscheduled` because the arm matched inside the strikethrough that
    RECORDED the routing as spent. A report whose population never shrinks is
    one nobody reads (item 131's shape: a check that cannot come back clean).
    ⛔ AND THE RISK IS REAL AND IS ACCEPTED DELIBERATELY: striking a route is now
    a way to leave the report. That is tolerable ONLY because this arm never
    gates -- it prints -- and because the item text stays in the table where a
    reader sees both the route and its strike. It would NOT be tolerable in a
    gate.
    """
    return _STRUCK.sub('', t)


def rule9_rows(s):
    """PURE. -> (keys, open_cycles) for the live RULE-9 table, or (None, None).

    `keys` is every finding id in column 1, IN ORDER and WITH REPEATS, so a
    caller can count duplicates. `open_cycles` is the ids whose verdict column
    opens `⛔ **UNREVIEWED**`.

    ⭐⭐ THE BACKLOG IS DERIVED HERE AND WRITTEN DOWN NOWHERE. `F131`: the
    block carried the count as a literal, it said `3` while the box said `4`,
    and the ⭐⭐⭐ finding in the queue was missing from the queue's own scope
    line. A count in prose ABOUT a structure rots exactly like one inside it.
    """
    m = _R9.search(s)
    if not m:
        return None, None
    keys, open_cycles = [], []
    for row in m.group(1).split('\n'):
        if not row.startswith('> |'):
            continue
        cols = row.split('|')
        if len(cols) < 3:
            continue
        found = re.findall(r'\bF([0-9]+)\b', cols[1])
        keys += [f'F{x}' for x in found]
        if found and '⛔ **UNREVIEWED**' in cols[2]:
            open_cycles.append(f'F{found[0]}')
    return keys, open_cycles


def main():
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
    print(f'findings           {len(nums):4}  highest '
          f'{max(nums, key=lambda x: int(x[1:]))}')
    if dups: fail.append(f'duplicate finding headings: {dups}')

    print(f'file size          {len(s)//1024:4} KB')

    # ---- the RULE-9 table is an INDEX, and an index has ONE ROW PER KEY. -----
    # ⚠⚠⚠ WHY THIS IS HERE: F131. The table that decides what may enter
    # `.memory-php/` listed SIX findings as BOTH `UNREVIEWED` and verdicted --
    # `F120`-`F125`, each twice -- because `_057` verdicted a BATCH and the
    # batch was APPENDED below instead of APPLIED above. FOURTH instance of the
    # class; the previous three were one row each and were caught by eye.
    # ▶ A verdict must REPLACE the row it verdicts.
    #
    # ⭐ STRUCTURAL, not prose: it counts keys in a column and does not try to
    # read what a cell means. Open item 123 warns that a check reading prose and
    # calling it code has produced five false positives here -- which is why
    # F131's count-literal half is DELIBERATELY NOT CHECKED. That half is n = 1,
    # and item 123's own rule is that three instances is a rate and one is not
    # yet a design.
    keys, open_cycles = rule9_rows(s)
    if keys is None:
        fail.append('RULE-9 live table not found (header row moved?)')
    else:
        d9 = sorted({k for k, v in collections.Counter(keys).items() if v > 1},
                    key=lambda x: int(x[1:]))
        print(f'{"RULE-9 rows":18} {len(keys):4}  {len(set(keys))} distinct, '
              f'{len(open_cycles)} open cycle(s): {" ".join(open_cycles)}')
        if d9:
            fail.append(f'RULE-9 table has {len(d9)} finding(s) on TWO rows: '
                        f'{" ".join(d9)}. A verdict REPLACES the row it '
                        f'verdicts (F131) -- merge them, do not append.')

    for label, cmd in (('catalogue rows', r"^\| ph[0-9]"),):
        rows = len(re.findall(cmd, open('patterns-php/CATALOGUE.md',
                                        encoding='utf-8',
                                        errors='replace').read(), re.M))
        print(f'{label:18} {rows:4}')

    # ---- `.memory-php/`'s "findings F1-FNN live in RECAP_PHP.md" headers. ----
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

    # ⓘ REPORT, NEVER A GATE (F140). Four LIVE open items handed a question to
    # "a reviewer", and `TASK_PHP_061` -- the round that ran the day they were
    # measured -- scoped NONE of them. The cause is structural, not forgetful:
    # a round's scope is DERIVED from the RULE-9 table, and NOTHING is derived
    # from the items table, so an item saying "this is a reviewer's" is
    # invisible to the process that scopes rounds. Rounds have folded items in
    # before (_057: 2, _059: 4, _061: 1) -- by the manager REMEMBERING, which
    # is the variance.
    # ⛔ IT MUST NOT FAIL A RUN. An item may legitimately wait several rounds;
    #    what it may not do is wait INVISIBLY. Same discipline as quota.py's
    #    one-column report and F128's Kind-A/Kind-B rule: print the population,
    #    leave the judgement to a reader.
    # ▶ THIS IS `_061` SS5.0's RULING APPLIED TO ITS OWN NEXT INSTANCE: four
    #   homes for a trap all failed, and the durable home is an arm that PRINTS.
    # ⛔⛔⛔ WIDENED 2026-09-16 BECAUSE ITS AUTHOR EVADED IT IN THE TURN THAT
    #    WROTE IT. Items 144-147 were registered saying "▶ A REVIEWER's, and it
    #    goes to `_063`" and "▶ `_063`", and the arm did not print them all.
    #    ⛔⛔ THIS COMMENT SAID "the arm matched NONE of them" AND THAT IS FALSE.
    #    `_063` §6.2(d) MEASURED IT by running the exact pre-widening regex
    #    (`git show 3f8298e:.tasks-php/boxcheck.py`) against the same text: it
    #    matches 145, 146 AND 147, and misses only 144 -- plus 139, which this
    #    comment never mentioned. ▶ THE WIDENING BOUGHT TWO ITEMS, NOT FOUR.
    #    ⭐⭐ AND THE BACK-TEST IS THE ARM'S BEST DEFENCE, NOT ITS INDICTMENT:
    #    WIDE and NARROW print the SAME list at every historical dispatch commit
    #    (2, 2, 2, 4, 4), so the arm is NOT tuned to the instance that produced
    #    it -- it reproduces `_061`'s miss in the form it had BEFORE the tuning.
    #    ⛔ UNMEASURABLE, AND SAY SO: the regex widening and the item re-wording
    #    landed in ONE commit (`8c2a546`) with no intermediate state, so
    #    `NARROW x pre-rewording text` cannot be computed from this tree.
    #    ▶ `_063`'s layer-shaped clause: A VALIDATOR CHANGE AND THE DATA CHANGE
    #      IT IS MEASURED AGAINST MUST NOT LAND IN THE SAME COMMIT.
    #    ⭐ NAMING A ROUND THAT DOES NOT EXIST YET IS
    #    THE SAME ACT AS NAMING "the round the backlog already owes": a round is
    #    a PROCESS and a process has no inbox. ▶ So `_0NN` is now a routing
    #    spelling in its own right. ⚠ THE LESSON IS NOT THE REGEX -- it is that
    #    an arm keyed to the phrasing of the instance that produced it catches
    #    that instance and nothing else (F43/F47's shape, one level up).
    sec = s[s.index('## Open items'):] if '## Open items' in s else ''
    items = re.findall(r'^\| (~~)?([0-9]+)(~~)? \|(.*)$', sec, re.M)
    routed = [n for struck, n, _, t in items
              if not struck and ROUTE.search(unstruck(t))]
    print(f'{"items -> a reviewer":18} {len(routed):4}  '
          f'LIVE, unscheduled: {" ".join(routed) if routed else "none"}')

    for f in fail: print('FAIL:', f)
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
