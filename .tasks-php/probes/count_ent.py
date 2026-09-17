#!/usr/bin/env python3
# =============================================================================
# count_ent.py -- **F44's FOUR-TABLE RESULT**, AND THE PROBE THAT IS CITED FOUR
# TIMES WHILE ONLY ONE OF THEM IS A DEBT
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr165/`, which is GITIGNORED.
# **F44** (`RECAP_PHP.md:8924`, landed 2026-09-09, commit fd07176) cites it BY
# PATH for the result *"it is FOUR tables, not two"*:
#
#       ent_uni_338_402   63 / 65      ent_uni_spacing    22 / 23
#       ent_uni_punct     66 / 67      ent_uni_8592_9002  410 / 411
#
# ⭐ RE-DERIVED ON PROMOTION, 2026-09-17, against the pinned 5.0.0 tarball:
# `17 tables · 4 short · 0 UNEVALUATED`, and all four figures land TO THE DIGIT.
# `.memory-php/04-process.md` LAW 11. Promoted by `TASK_PHP_064`, commit
# f4bda71.
#
# ⚠⚠ `nm -S` CORROBORATES THOSE NUMBERS, SO WHAT THE TREE WOULD HAVE LOST IS
# **THE INDEPENDENT METHOD**, not the numbers -- and that is `scratchdeps.py`'s
# ADJUDICATION's own reason line. ⛔ READ IT BEFORE ASSUMING THE VERDICT: this
# file is cited FOUR times and **three are `HISTORY`, not a defect.** Under F50,
# F51 and F52 it is the SUBJECT of a sentence about a defect class -- *"the
# exact failure `count_ent.py` produced last session"* -- and those sentences
# state the claim in full. **The verdict is the sentence, not the bucket.**
#
# ⛔⛔ AND THE DEFECT THOSE THREE SENTENCES ARE ABOUT IS THIS FILE'S OWN, which
# is why promoting it matters more than promoting a clean probe: v1's
# `declared()` matched bounds with `(\d+)` and could not read the 15
# `entity_map[]` rows whose bounds are HEX, then printed *"(not in entity_map --
# unused?)"* -- **a broken computation rendering as a positive claim about the
# C**. `RECAP_PHP.md` names it three times as the precedent for that class
# (F50's *"same class as count_ent.py"*, F51, F52's three-probes table).
# ▶ **A correction whose target has been deleted cannot be read** -- the same
# argument `PROMOTE_001` made for keeping `null_control.py` because F82 refuted
# it. The docstring below is the repaired file's own account of it.
#
# RUN IT:  python3 .tasks-php/probes/count_ent.py <path/to/html.c> [table ...]
# ⓘ `refetch_upstream002.sh` calls it once per fetched `html-*.c`.
#
# ✅ WHAT IT NEEDS: a `html.c` ON THE COMMAND LINE and nothing else. Pure
# stdlib, reads one file, writes nothing, builds nothing. The 5.0.0 copy comes
# from the PINNED tarball in `php-in-safe-rust`'s scratch (see
# `patterns-php/SOURCES.md`); the later tags come from the network via
# `probes/refetch_upstream002.sh`. ⛔ Neither is committed and neither should be.
#
# ⛔ WHAT IS STILL OWED. (1) **It has NO must-fire negatives** -- filed
# `negatives="none", kind="tool"` in `.tasks-php/checkers.py`, which is honest
# and is not a pass. A file whose v1 shipped a false claim twice, and which the
# programme cites three times as a cautionary precedent, is precisely the file
# that should carry arms; it does not, and none are added here because adding
# them in the promoting pass hides which behaviour was inherited. (2) Its
# `strip_comments` is a REGEX over C, not a lexer -- `probes/entcount.py` (F53)
# exists because the COMPILER is the independent method, and that file is the
# one to trust where the two disagree. (3) It exits non-zero on an unevaluated
# row, which is the repair; nothing checks that the arm still fires.
# =============================================================================
"""Count initialisers in ext/standard/html.c's entity tables and compare each
with the range entity_map[] declares for it.

    python3 count_ent.py <html.c> [table ...]

⚠⚠ THIS SCRIPT SHIPPED A FALSE CLAIM AND THE MANAGER QUOTED IT TWICE.
v1's `declared()` matched bounds with `(\\d+)`, so it could not read the 15
entity_map[] rows whose bounds are hex (`0x80`, `0xff`, ...). It returned None
for the 8 tables those rows name -- and then PRINTED "(not in entity_map --
unused?)", which is FALSE: all 17 tables are in entity_map[]. It also printed
`ok` for any row it could not evaluate.

The defect is not the arithmetic. It is that BOTH failure paths rendered as a
POSITIVE CLAIM ABOUT THE C rather than as "I could not evaluate this" --
`RECAP_PHP.md` F17's shape (a reassurance that tells the reader not to look) and
F10/F11's (a check that parses instead of asking the tool that decides).
`TASK_PHP_019` §10 caught it by re-deriving every number with the compiler.

Rule this file now obeys: an unevaluated row prints CANNOT EVALUATE and the
exit status is non-zero. Never say "ok" for something you did not check.
"""
import re, sys

def strip_comments(s):
    """C semantics, including an UNTERMINATED /* -- which is the whole point:
    php-5.0.4 ships ent_uni_338_402 at 41 for 65 because 24 initialisers sit
    inside a comment. Verified to agree with gcc on that exact file."""
    return re.sub(r'/\*.*?(?:\*/|$)', '', s, flags=re.S)

def table(src, name):
    m = re.search(r'static\s+entity_table_t\s+' + re.escape(name) + r'\[\]\s*=\s*\{', src)
    if not m: return None
    i, d = m.end(), 1
    while d:
        d += (src[i] == '{') - (src[i] == '}')
        i += 1
    return len([t for t in strip_comments(src[m.end():i-1]).split(',') if t.strip()])

def declared(src, name):
    """Every entity_map[] row naming `name`. Bounds may be decimal OR HEX --
    int(x, 0) reads both. Returns [(charset, count)], possibly several."""
    m = re.search(r'entity_map\[\]\s*=\s*\{(.*?)\n\};', src, re.S)
    if not m: return None
    rows = re.findall(r'\{\s*(cs_\w+)\s*,\s*([0-9a-fA-FxX]+)\s*,\s*([0-9a-fA-FxX]+)\s*,\s*'
                      + re.escape(name) + r'\s*\}', m.group(1))
    return [(cs, int(hi, 0) - int(lo, 0) + 1) for cs, lo, hi in rows] or None

def main(path, names):
    src = open(path, encoding='utf-8', errors='replace').read()
    names = names or re.findall(r'static\s+entity_table_t\s+(\w+)\[\]', src)
    unevaluated = short = 0
    for n in names:
        have, decls = table(src, n), declared(src, n)
        if have is None:
            print(f'  {n:22} CANNOT EVALUATE -- no such table'); unevaluated += 1; continue
        if decls is None:
            print(f'  {n:22} has {have:4}  CANNOT EVALUATE -- no entity_map[] row parsed')
            unevaluated += 1; continue
        for cs, want in decls:
            flag = (f'SHORT by {want-have}' if have < want else
                    f'over by {have-want}' if have > want else 'exact')
            if have < want: short += 1
            print(f'  {n:22} has {have:4}  {cs:14} declares {want:4}  {flag}')
    print(f'  -- {len(names)} tables · {short} short · {unevaluated} UNEVALUATED')
    return 1 if unevaluated else 0

if __name__ == '__main__':
    # ⛔ A missing ARGUMENT is a usage error, not a missing cache -- rc 2 with a
    # message, NOT item 149's report-and-return-0. As written it raised an
    # unhandled IndexError, which reads as a broken probe rather than as
    # "you did not tell me which file".
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', '--selftest'):
        sys.stderr.write(
            'usage: python3 .tasks-php/probes/count_ent.py <path/to/html.c> '
            '[table ...]\n'
            '  Comment-aware REGEX counter for ext/standard/html.c entity\n'
            "  tables. F44's instrument. ⚠ It has NO --selftest.\n"
            '  ⚠⚠ probes/entcount.py asks the COMPILER the same question and\n'
            '  is the one to trust where the two disagree.\n')
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
