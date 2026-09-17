#!/bin/sh
# ph69_refcount.sh -- row 14's CRITERION-2 INSTRUMENT, run on real 5.0.0.
#
#   sh ph69_refcount.sh [workdir]
#
# ⭐ ROW 15's instrument, promoted out of `.temp/` with `ROW14_001.md` --
# `_063` §7.2: a generator in scratch with no committed twin is the one
# citation case NO arm can see. Default workdir `.temp/php69probe`.
# `CLAUDE.md` rule 1: THIS FILE is the generator, the `.php` scripts and the
# workdir are artefacts -- delete them when your gates are green. Never cite the
# workdir from `spec.md`/`NOTES.md` (§F6); cite this.
#
# ====================== WHAT IT MEASURES, AND WHY =========================
# `ext/pcre/php_pcre.c:584-593` in pristine PHP 5.0.0 ends `preg_match_all`'s
# PREG_PATTERN_ORDER path with:
#
#     for (i = 0; i < num_subpats; i++) {
#         if (subpat_names[i]) {
#             zend_hash_update(Z_ARRVAL_P(subpats), subpat_names[i],
#                              strlen(subpat_names[i])+1, &match_sets[i], ...);
#         }
#         zend_hash_next_index_insert(Z_ARRVAL_P(subpats), &match_sets[i], ...);
#     }
#
# Each `match_sets[i]` is `INIT_PZVAL`'d at `:461`, so refcount == 1 with ONE
# owner. When the subpattern is NAMED it enters TWO owning hash slots with no
# `ZVAL_ADDREF` between. ⭐ PHP 5.1.0 adds exactly one line at `:625` --
# `ZVAL_ADDREF(match_sets[i]);` -- and that is the whole repair.
#
# ⭐⭐ `F133`(i) IS A YES HERE, AND A STRUCTURALLY MATCHED ONE: 5.0.0's SAME FILE
# already carries `(*entry)->refcount++` at `:1533`, in `php_preg_grep`, guarding
# the SAME operation (`zend_hash_update` of a `zval *` into a result array) 943
# lines away. The correct site does the HARDER version -- one store, one
# increment -- while the defect does the easier one wrong.
#
# ========================= HOW TO READ THE OUTPUT =========================
# ⛔⛔ EVERY CELL EXITS 0. THAT IS THE RESULT, NOT A FAILURE TO REPRODUCE.
# Like `ph66`, this row's target error is a WRONG ANSWER: no fault, no ASan
# report, nothing in `si_addr`. ⚠ THE OBSERVABLE IS THE VALUE, NOT `rc` AND NOT
# `count` -- `ROW13_001` §4 asserted a UAF from reading a delete's tail, never
# ran it, and was refuted by five cells that all exited 0.
#
#   A  benign, unnamed subpattern   -> stored ONCE. correct, and identical
#                                      post-R1h.
#   B  named subpattern, keys       -> ⭐ the SAME zval is at BOTH `word` and `1`.
#   C  named + drop one owning slot -> ⭐⭐⭐ THE SURVIVING SLOT READS BACK AS A
#                                      DIFFERENT TYPE. Silent, rc=0.
#
# ⚠⚠ TWO CAUTIONS TRAVEL WITH ANY RESULT FROM THIS PROBE (§A3a), AND A ROW THAT
# QUOTES IT MUST REPEAT THEM:
#   (1) the binary is php-in-safe-rust's ORACLE build, the PLAIN
#       `php-5.0.0-mysql-webext`, NOT a museum-default 5.0.0, and its flags are
#       NOT RECORDED IN A `.buildinfo`; its `config.status` says `-O0`. Say that,
#       do not name flags (F139);
#   (2) a CLEAN run would NOT be evidence of absence (F3).
set -e

WORK="${1:-.temp/php69probe}"
ORACLE="${ORACLE:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext}"

[ -x "$ORACLE" ] || { echo "no 5.0.0 oracle at $ORACLE" >&2; exit 2; }
mkdir -p "$WORK"

cell() {   # cell <name> <expected stdout> <php body>
	printf '<?php\n%s\n' "$3" > "$WORK/c_$1.php"
	set +e
	got=$(timeout 60 "$ORACLE" -n "$WORK/c_$1.php" 2>&1 | tr '\n' '|'); rc=$?
	set -e
	printf '%-24s rc=%-4s out=%-34s' "$1" "$rc" "$got"
	if [ "$rc" = 0 ] && [ "$got" = "$2" ]; then printf 'ok\n'
	else printf '⛔ EXPECTED rc=0 out=%s\n' "$2"; fail=1; fi
}

fail=0
printf '%-24s %-7s %-34s %s\n' CELL RC OBSERVABLE VERDICT

cell 'A benign-unnamed' 'keys=0,1|' \
 "preg_match_all('/(\\\\w+)/','alpha beta',\$m,PREG_PATTERN_ORDER);
  echo 'keys='.implode(',',array_keys(\$m)).\"\\n\";"

cell 'B named-stored-twice' 'keys=0,word,1|same=yes|' \
 "preg_match_all('/(?P<word>\\\\w+)/','alpha beta',\$m,PREG_PATTERN_ORDER);
  echo 'keys='.implode(',',array_keys(\$m)).\"\\n\";
  echo 'same='.((\$m['word']===\$m[1])?'yes':'no').\"\\n\";"

cell 'C surviving-slot-uaf' 'was=array|now=integer|' \
 "preg_match_all('/(?P<word>\\\\w+)/','alpha beta gamma',\$m,PREG_PATTERN_ORDER);
  echo 'was='.gettype(\$m[1]).\"\\n\";
  unset(\$m['word']);
  \$pad=str_repeat('A',64); \$recycle=array(1,2,3,4,5,6,7,8);
  echo 'now='.gettype(\$m[1]).\"\\n\";"

echo
if [ "$fail" = 0 ]; then
	cat <<'EOF'
AS EXPECTED. ⭐ Read cell C twice: `$m[1]` held an ARRAY, `unset($m['word'])`
dropped the shared zval's only counted reference to 0 and FREED it, and the
surviving owning slot now reads back as an INTEGER -- a type-confused read
through a dangling owner. PHP exits 0 with nothing on stderr.
⛔ There is no fault here and cell A is correct on both images, so a row quoting
this must publish the VALUE, not `rc`.
▶ §A3a obligation 5 (re-run against the R1h post-image) is where this becomes a
two-sided result. ⚠ THAT OBLIGATION'S WORDING IS `F141`, IT IS UNREVIEWED, AND
`_063` §4 MAY OVERTURN IT -- check the protocol before quoting it.
EOF
else
	cat <<'EOF'
⛔ DEVIATES. That is a REPORTABLE RESULT, not a broken probe -- record what you
saw, name the binary, and do NOT edit the expectations to match (F43/F47: a
check that refuses your row is a hypothesis first).
EOF
fi
echo
echo 'ⓘ artefacts are under '"$WORK"' -- delete them when your gates are green.'
exit "$fail"
