#!/usr/bin/env python3
# =============================================================================
# entcount.py -- **F53's WHOLE EVIDENCE**, AND THE INDEPENDENT METHOD BEHIND F44
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/php19/`, which is GITIGNORED.
# **F53** (`RECAP_PHP.md:8191`, landed 2026-09-09, commit 2d780ea) cites it by
# name: *"✅ **Measured at each commit** (`entcount.py` run at nine PHP-5.0
# commits touching `html.c` between 5.0.3 and 5.0.4)"* -- and that measurement
# IS the finding: `ph32`'s stated R1h is wrong for two of the three tables it
# claims. `.memory-php/04-process.md` LAW 11. Promoted by `TASK_PHP_064`,
# 2026-09-17, repo at commit f4bda71.
#
# ⭐⭐ F53's LOAD-BEARING HALF RE-DERIVES EXACTLY. Re-run on promotion,
# 2026-09-17, against `b9ff04703f16` (2005-01-11) fetched fresh from php-src:
#
#       ent_uni_338_402    declares 65   has 63   SHORT
#       ent_uni_spacing    declares 23   has 23   ok
#       ent_uni_8592_9002  declares 411  has 411  ok
#
# **Two of the three are already `ok` two months before `56adfe1f3cf1`**, which
# is precisely F53's claim. (At `56adfe1f3cf1`, `ent_uni_338_402` reads **41**,
# the comment-swallowed 24 that F45 is about.)
#
# ⛔⛔ WHAT IS **NOT** RE-DERIVABLE, AND IT IS THE REAL GAP THIS PROMOTION
# EXPOSES: **the NINE-COMMIT CORPUS HAS NO COMMITTED GENERATOR.** F53 says
# *"nine PHP-5.0 commits touching `html.c` between 5.0.3 and 5.0.4"* and names
# only two of them. `probes/refetch_f50_census.sh` fetches the 5.0.0/5.0.4/
# 5.0.5/5.1.0/5.2.0 TAGS, not the intermediate commits. ▶ Promoting this file
# makes the INSTRUMENT durable and leaves the INPUT SET a recipe:
#
#   curl -sSL 'https://api.github.com/repos/php/php-src/commits?path=ext/standard/html.c&sha=PHP_5_0&per_page=100' \
#     | python3 -c "import json,sys;[print(c['sha'][:12], c['commit']['author']['date'][:10]) for c in json.load(sys.stdin)]"
#   # then, per sha:
#   curl -sSL -o html-<sha>.c https://raw.githubusercontent.com/php/php-src/<sha>/ext/standard/html.c
#   python3 .tasks-php/probes/entcount.py html-<sha>.c
#
# ⚠ Writing that as a script is OWED and was deliberately NOT done here: it
# would be a NEW generator authored in a promotion pass, and *"which nine"* is
# a judgement F53's author made and did not record.
#
# RUN IT:  python3 .tasks-php/probes/entcount.py <path/to/html.c>
# ⚠ It needs an ARGUMENT and `gcc`. As written it died with an unhandled
# `FileNotFoundError` on `sys.argv[1]` when given none -- repaired to a usage
# message, because a traceback reads as a broken probe.
#
# ⭐⭐ WHY IT EXISTS BESIDE `probes/count_ent.py`, AND THIS IS THE POINT OF THE
# PAIR: `count_ent.py` is a REGEX over the source and shipped a false claim
# twice; **this file asks the COMPILER**. Comment handling is the real C
# lexer's, `entity_map[]`'s bounds are read from the COMPILED struct (so the 15
# HEX rows a `(\d+)` regex silently skips are handled), the map is enumerated by
# walking to `cs_terminator`, and table <-> map row is joined by POINTER
# IDENTITY rather than by name. ▶ **Where the two disagree, trust this one** --
# and `scratchdeps.py`'s ADJUDICATION says the same thing about F44: what the
# tree would lose is the INDEPENDENT METHOD, not the numbers.
#
# ⛔ WHAT IS STILL OWED. (1) **F53 is a REVIEW finding and its `ph32` correction
# landed in the catalogue; this promotion does not re-open it.** (2) ⚠ **It has
# NO must-fire negatives** -- filed `negatives="none", kind="tool"` in
# `.tasks-php/checkers.py`, which is honest and is not a pass. (3) It writes a
# temp `.c`/binary under `tempfile.mkdtemp` and removes them; that is outside
# `.temp/`, which `CLAUDE.md` Don't #1 would prefer, and it is left as written
# because changing where a promoted probe writes changes what it measured.
# (4) The nine-commit input set above.
# =============================================================================
"""TASK_PHP_019 §10 — count ext/standard/html.c's entity tables WITH THE C COMPILER.

Independent of any regex over the source, on every axis that matters:
  * comment handling is the real C lexer's, not `re.sub(r'/\\*.*?\\*/')`;
  * `entity_map[]`'s bounds are read from the COMPILED struct, so hex literals
    (`0x80`, `0xa0`, `0xff` -- eight of the 24 rows) are handled, where a
    `(\\d+)` regex silently skips them and reports "ok";
  * the map is enumerated by walking to `cs_terminator`, so no table can be
    missed by not being on a command line;
  * table <-> map row is joined by POINTER IDENTITY, not by name matching.

    python3 entcount.py <html.c>          # prints one line per entity_map row

Only the list of `static entity_table_t NAME[]` names is taken from the text,
and that grep is checked: every name found must appear in the compiled output.
"""
import re, subprocess, sys, os, tempfile

# ⛔ A missing ARGUMENT is a usage error, not a missing cache -- so this is rc 2
# with a message, NOT item 149's report-and-return-0. As written it raised an
# unhandled FileNotFoundError on `sys.argv[1]`, which reads as a broken probe.
if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "--selftest"):
    sys.stderr.write(
        "usage: python3 .tasks-php/probes/entcount.py <path/to/html.c> "
        "[table ...]\n"
        "  Counts ext/standard/html.c's entity tables WITH gcc and compares\n"
        "  each against the range entity_map[] declares. F53's instrument.\n"
        "  ⚠ It has NO --selftest; see the header for what that costs.\n"
        "  Get an html.c: tar -xzOf <php-5.0.0.tar.gz> "
        "php-5.0.0/ext/standard/html.c\n"
        "               or curl raw.githubusercontent.com/php/php-src/<sha>/"
        "ext/standard/html.c\n")
    sys.exit(2)

path = sys.argv[1]
src = open(path, 'rb').read().decode('latin-1')

# ---- the only textual step: the table NAMES, and the slice to compile -------
names = re.findall(r'^static entity_table_t (\w+)\[\]', src, re.M)
lines = src.split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('enum entity_charset'))
end = next(i for i, l in enumerate(lines)
           if l.startswith('static const struct html_entity_map entity_map[]'))
end = next(i for i in range(end, len(lines)) if lines[i].rstrip() == '};')
body = '\n'.join(lines[start:end + 1])

prog = ['#include <stdio.h>', body, '', 'int main(void) {',
        '  struct { const char *n; entity_table_t *t; unsigned long c; } T[] = {']
for n in names:
    prog.append('    { "%s", %s, sizeof(%s)/sizeof(%s[0]) },' % (n, n, n, n))
prog += ['    { 0, 0, 0 }', '  };', '  int i, j;',
         '  for (i = 0; entity_map[i].charset != cs_terminator; i++) {',
         '    unsigned span = entity_map[i].endchar - entity_map[i].basechar + 1;',
         '    const char *nm = "<unknown>"; unsigned long have = 0;',
         '    for (j = 0; T[j].n; j++) if (T[j].t == entity_map[i].table) { nm = T[j].n; have = T[j].c; }',
         '    printf("%-2d %-18s base=%-5u end=%-5u declares=%-4u has=%-4lu %s\\n",',
         '           i, nm, entity_map[i].basechar, entity_map[i].endchar, span, have,',
         '           have < span ? "SHORT" : (have > span ? "over" : "ok"));',
         '  }',
         '  printf("map rows: %d ; named tables in file: %d\\n", i, (int)(sizeof(T)/sizeof(T[0]) - 1));',
         '  return 0;', '}']

d = tempfile.mkdtemp(prefix='entcount.')
c, b = os.path.join(d, 'x.c'), os.path.join(d, 'x')
open(c, 'wb').write('\n'.join(prog).encode('latin-1'))
r = subprocess.run(['gcc', '-std=c89', '-Wall', '-o', b, c],
                   capture_output=True, text=True)
if r.returncode:
    sys.stderr.write(r.stdout + r.stderr)
    sys.exit(1)
if r.stderr.strip():
    sys.stderr.write('--- compiler diagnostics (READ THEM) ---\n' + r.stderr)
out = subprocess.run([b], capture_output=True, text=True).stdout
print(out, end='')
for n in names:
    if n not in out:
        print('  ⚠ named table NOT reachable from entity_map[]: %s' % n)
os.remove(c); os.remove(b); os.rmdir(d)
