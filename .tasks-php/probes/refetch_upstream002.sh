#!/bin/sh
# =============================================================================
# refetch_upstream002.sh -- **F50's NAMED REGENERATOR**, and F44/F45's too
#
# ⛔⛔ WHY IT IS COMMITTED. It was written as `.temp/mgr165/REFETCH.sh`, which is
# GITIGNORED, and `RECAP_PHP.md:8335` (F50, landed 2026-09-08/09) names it in
# the finding's own sentence -- *"evidence and a `REFETCH.sh` that ..."* -- as
# the script that regenerates ALL of F50's evidence. `CLAUDE.md` Don't #1 says
# KEEP THE GENERATOR, DELETE THE ARTEFACT; it says nothing about WHERE the
# generator lives, so obeying it to the letter still produced a law-11 defect
# (`.memory-php/04-process.md` LAW 11, and F102's row of `scratchdeps.py`'s
# ADJUDICATION makes exactly this point). Promoted by `TASK_PHP_064`,
# 2026-09-17, repo at commit f4bda71.
#
# ⛔⛔⛔ RENAMED, AND THE RENAME IS NOT COSMETIC. `.tasks-php/refetch.sh` ALREADY
# EXISTS and is a **DIFFERENT SCRIPT** -- it regenerates `.temp/mgr/`'s F34/F35/
# F36 downloads and was itself promoted on 2026-09-08 by the commit *"Move the
# two cited generators out of gitignored scratch"*. Promoting this one as
# `refetch.sh` would have overwritten it. ▶ Two scripts, two findings, one
# basename: the collision is why this is `refetch_upstream002.sh`, after the
# document it was written for (`.tasks-php/UPSTREAM_002.md`).
#
# ⚠⚠ THREE CHANGES WERE MADE AT PROMOTION AND ALL THREE WERE FORCED:
#  1. **It used to `cd "$(dirname "$0")"`**, i.e. write every downloaded `.c`
#     and `.patch` INTO its own directory. In `.temp/mgr165/` that was correct;
#     in `.tasks-php/probes/` it would drop ~25 re-derivable artefacts into a
#     committed tree, which is `CLAUDE.md` Don't #1 inverted. ▶ It now works in
#     `.temp/mgr165/` explicitly, which is where its cached `.patch` files still
#     are, so a re-run costs nothing it has already fetched.
#  2. `FN=../php17/r1h/fn.py` pointed into gitignored scratch. ▶ Promoted beside
#     this script as `probes/fn_body.py`. **A generator that cannot generate is
#     not a promotion.**
#  3. `count_ent.py` was resolved from the working directory. ▶ Now resolved
#     from `probes/`, where `TASK_PHP_064` promoted it for F44.
#
# ⛔ IT NEEDS NETWORK (`api.github.com` + `raw.githubusercontent.com`) and the
# PINNED php-5.0.0 tarball in `php-in-safe-rust`'s scratch. It has NO self-test
# and asserts nothing, so it is filed `kind="tool", negatives="none"` in
# `.tasks-php/checkers.py` and is **NEVER IN A SWEEP** -- same call as
# `probes/sweep_cg.sh` and `probes/rebuild_hardened_php.sh`. Cached files are
# skipped (`[ -f ... ] ||`), so a re-run is cheap and safe.
#
# ✅ RE-RUN ON PROMOTION, 2026-09-17: see `.temp/mgr177/refetch-rerun.log`.
#
# ⛔ WHAT IS STILL OWED. (1) **F50 is MANAGER, UNREVIEWED, n = 1** by its own
# heading. (2) This script PRINTS; it does not ASSERT. Nothing in it fails if a
# hash moves, so it regenerates evidence for a human to read and is not a check.
# (3) The `list()` helper hits `api.github.com` unauthenticated and is subject to
# rate limiting; a throttled run prints a JSON error object and keeps going.
# (4) ⚠ The comment below is right and load-bearing: the blame line names an SVN
# revision that php-src's git mirror cannot resolve, so **do not** assert that
# `cb3cca21b345` introduced the removed hunk.
# =============================================================================
# UPSTREAM_002 -- the generator for every artefact in .temp/mgr165/.
# Manager, between TASK_PHP_017 and TASK_PHP_018.
#
# Question: PHP added `cb3cca21b345`'s hunk (b) in 2005. Is it still there?
# Method:   brace-match PHP_FUNCTION(mb_strcut) at each tag and hash the BODY
#           (F35 / .memory-php/00 -- ask about a FUNCTION, not about text; a
#           grep for "unsigned) from" MISSES 5.3.0, which spells it
#           "(unsigned int)from").
# Artefacts: the .c files are re-derivable and get deleted; this script and the
#           fetched .patch are the evidence.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)          # .tasks-php/probes
ROOT=$(cd "$HERE/../.." && pwd)              # the repo root
WORK="$ROOT/.temp/mgr165"                    # ⛔ artefacts live HERE, not in probes/
mkdir -p "$WORK"
cd "$WORK"
FN="$HERE/fn_body.py"                        # promoted from .temp/php17/r1h/fn.py
COUNT_ENT="$HERE/count_ent.py"               # promoted for F44

TAGS="5.1.2 5.2.0 5.2.1 5.2.3 5.2.5 5.2.6 5.2.7 5.2.8 5.2.9 5.2.10 5.2.11 \
      5.2.12 5.2.14 5.2.16 5.2.17 5.3.0 5.3.1 5.3.2 5.3.29"
for t in $TAGS; do
  [ -f "mbstring-php-$t.c" ] || curl -sSL -o "mbstring-php-$t.c" \
    "https://raw.githubusercontent.com/php/php-src/php-$t/ext/mbstring/mbstring.c"
  python3 "$FN" "mbstring-php-$t.c" 'PHP_FUNCTION(mb_strcut)'
done

# the commit that REMOVES hunk (b) on PHP-5.2
[ -f c2471b495009.patch ] || curl -sSL -o c2471b495009.patch \
  "https://github.com/php/php-src/commit/c2471b495009.patch"

list() {   # $1 branch  $2 since  $3 until
  curl -sSL "https://api.github.com/repos/php/php-src/commits?path=ext/mbstring/mbstring.c&sha=$1&since=$2T00:00:00Z&until=$3T00:00:00Z&per_page=100" \
  | python3 -c "import json,sys
d=json.load(sys.stdin)
if isinstance(d, dict):
    print('  (api error / rate limit):', d.get('message'))
else:
    [print(c['sha'][:12], c['commit']['author']['date'][:10], c['commit']['author']['name'], '|', c['commit']['message'].split(chr(10))[0][:90]) for c in d]"
}

# how the removal was found: the only non-cosmetic commit on that file in the window
echo "--- REMOVAL. PHP-5.2, 2009-09..2010-01 (expect c2471b495009 + a copyright sed) ---"
list PHP-5.2 2009-09-01 2010-01-15
echo "--- and its 5.3 counterpart, same message, separate sha ---"
list PHP-5.3 2009-09-20 2010-01-01

# WHERE THE LINES CAME FROM. The blame line in that message names an SVN
# revision (r202895) and php-src's git mirror carries NO git-svn-id, so it
# cannot be resolved from the mirror -- do not assert it is cb3cca21b345.
# What IS measured: on PHP-5.2 nothing else touched the function between the
# 2005 fix and the 2009 removal (body byte-identical php-5.1.2..php-5.2.6).
echo "--- INTRODUCTION. PHP-5.2, 2005-12..2006-02 (expect cb3cca21b345, Ilia) ---"
list PHP-5.2 2005-12-01 2006-02-01
echo "--- git-svn-id present in SVN-era messages? (expect: no) ---"
list "" 2008-01-01 2008-06-01 | head -5

# --- F45: ext/standard/html.c's entity tables, 5.0.0 -> 5.2.0 ---
# 5.0.0 is short on FOUR tables; 5.0.4 ships ent_uni_338_402 at 41 for a
# declared 65 (a comment swallowed 24 initialisers) with gcc -Wall silent;
# 5.0.5 repairs all four. count_ent.py is the comment-aware counter.
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
[ -f html-5.0.0.c ] || tar -xzOf "$TB" php-5.0.0/ext/standard/html.c > html-5.0.0.c
for t in 5.0.4 5.0.5 5.1.0 5.2.0; do
  [ -f "html-$t.c" ] || curl -sSL -o "html-$t.c" \
    "https://raw.githubusercontent.com/php/php-src/php-$t/ext/standard/html.c"
done
for f in html-*.c; do echo "--- $f"; python3 "$COUNT_ENT" "$f" | tail -1; done

# the two entity-table fixes (F45); the removal chain's warning commit is
# bd07142b9128, quoted in TASK_PHP_019_REPORT §10
for c in 46bc2c5ae2ae bd2e99ee50ed; do
  [ -f "$c.patch" ] || curl -sSL -o "$c.patch" "https://github.com/php/php-src/commit/$c.patch"
done
