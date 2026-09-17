#!/bin/sh
# ph70_overdec.sh -- ROW 14's CRITERION-2 INSTRUMENT, run on real 5.0.0.
#
#   sh ph70_overdec.sh [workdir]
#
# ⭐ ROW 14's instrument, promoted out of `.temp/` with `ROW14_001.md` --
# `_063` §7.2: a generator in scratch with no committed twin is the one
# citation case NO arm can see. Default workdir `.temp/php70probe`. `CLAUDE.md` rule 1: THIS
# FILE is the generator, the `.php` scripts and the workdir are artefacts --
# delete them when your gates are green. Never cite the workdir from
# `spec.md`/`NOTES.md` (§F6); cite this.
#
# ====================== WHAT IT MEASURES, AND WHY =========================
# `ext/standard/array.c:3803-3808` in pristine PHP 5.0.0, `array_reduce`:
#
#     if (ZEND_NUM_ARGS() > 2) {
#         result = *initial;        /* ADOPTS the caller's zval. NO increment. */
#     } else {
#         MAKE_STD_ZVAL(result);
#         ZVAL_NULL(result);
#     }
#     ...
#     zval_ptr_dtor(&result);       /* :3843 -- DROPS a count it never took */
#
# PHP 5.1.0 replaces the adopting line with a deep copy that takes ownership:
# ALLOC_ZVAL + `*result = **initial` + zval_copy_ctor + convert_to_long +
# INIT_PZVAL. ⭐ FOUR LINES REPLACING ONE -- structurally unlike ph69's repair,
# which is a single added `ZVAL_ADDREF`. Same invariant (`I7`), two fix shapes.
#
# ========================= HOW TO READ THE OUTPUT =========================
# ⛔⛔ UNLIKE `ph66` AND `ph69`, THIS ROW **FAULTS**, AND THAT IS THE POINT.
#
#   A  adversarial: `initial` has an ALLOCATED payload -> ⛔ SIGSEGV rc=139.
#   B  benign:      no third argument, so the MAKE_STD_ZVAL arm runs -> correct.
#   C  negative:    `initial` is an IS_LONG -> CORRECT, rc=0.
#
# ⭐⭐⭐ CELL C IS THE DISCRIMINATOR AND IT MUST NOT BE DROPPED. A long carries no
# allocated payload, so the unmatched decrement corrupts a count and frees
# nothing. ▶ A row whose blob emits only integers MEASURES NOTHING HERE. Cells B
# and C together attribute the fault to exactly the line 5.1.0 replaces.
#
# ⚠⚠ TWO CAUTIONS TRAVEL WITH ANY RESULT FROM THIS PROBE (§A3a), AND A ROW THAT
# QUOTES IT MUST REPEAT THEM:
#   (1) the binary is php-in-safe-rust's ORACLE build, the PLAIN
#       `php-5.0.0-mysql-webext`, NOT a museum-default 5.0.0, and its flags are
#       NOT RECORDED IN A `.buildinfo`; its `config.status` says `-O0`. Say that,
#       do not name flags (F139);
#   (2) a CLEAN run would NOT be evidence of absence (F3).
set -e

WORK="${1:-.temp/php70probe}"
ORACLE="${ORACLE:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext}"
REPEAT="${REPEAT:-3}"

[ -x "$ORACLE" ] || { echo "no 5.0.0 oracle at $ORACLE" >&2; exit 2; }
mkdir -p "$WORK"

cell() {   # cell <name> <expected rc> <php body>
	printf '<?php\n%s\n' "$3" > "$WORK/c_$1.php"
	rcs=""
	i=0
	while [ "$i" -lt "$REPEAT" ]; do
		set +e
		# ⛔⛔⛔ DO NOT PIPE HERE. The first draft was
		#     out=$(... "$ORACLE" ... | tr '\n' '|'); rc=$?
		# and `$?` is the exit status of the LAST command in a pipeline -- `tr`,
		# which always succeeds. The oracle segfaulted on all three runs and this
		# harness printed `rc=[ 0 0 0 ]`. ⭐ A CRITERION-2 PROBE WHOSE WHOLE CLAIM
		# IS AN EXIT STATUS REPORTED THE WRONG EXIT STATUS. Capture rc with NO
		# pipe, then reshape the text in a separate step.
		out=$(timeout 60 "$ORACLE" -n "$WORK/c_$1.php" 2>/dev/null); rc=$?
		out=$(printf '%s' "$out" | tr '\n' '|')
		set -e
		rcs="$rcs $rc"
		i=$((i + 1))
	done
	printf '%-22s rc=[%s ] out=%-26s' "$1" "$rcs" "$out"
	# every repeat must agree, and agree with the expectation
	if [ "$rcs" = "$(for _ in $(seq "$REPEAT"); do printf ' %s' "$2"; done)" ]
	then printf 'ok\n'
	else printf '⛔ EXPECTED rc=%s on all %s runs\n' "$2" "$REPEAT"; fail=1; fi
}

fail=0
printf '%-22s %-14s %-26s %s\n' CELL RC OBSERVABLE VERDICT

# ⛔⛔⛔ CELL A's FIRST DRAFT OMITTED THE LAST LINE AND READ rc=0 THREE TIMES,
# WHILE THE HAND-RUN SCRIPT IT WAS COPIED FROM FAULTED 3/3. THE PROBE REFUSED
# ITS AUTHOR'S RESULT AND THE AUTHOR WAS WRONG ABOUT THE MECHANISM.
# ⭐⭐⭐ THE CHURN IS NOT THE OBSERVABLE. `$seed` MUST BE READ AFTER IT.
# array_reduce drops a count it never took, so `$seed`'s zval is freed while
# `$seed` STILL NAMES IT; the churn merely recycles the block; the fault is the
# READ THROUGH THE DANGLING OWNER -- the same shape as ph69's cell C, and the
# same rule `_062` §3.1 states: THE OBSERVABLE IS NOT `rc`.
# ⛔ DO NOT "SIMPLIFY" THIS CELL BY DROPPING THE TRAILING strlen/substr.
cell 'A adversarial-alloc' 139 \
 "function cat(\$a,\$b){return \$a;}
  \$seed=str_repeat('S',40);
  \$r=array_reduce(array(1,2,3),'cat',\$seed);
  echo 'len='.strlen(\$r).\"\\n\";
  \$pad=str_repeat('Z',40); \$more=str_repeat('Q',40);
  echo 'seed='.strlen(\$seed).'/'.substr(\$seed,0,4).\"\\n\";"

cell 'B benign-no-initial' 0 \
 "function cat(\$a,\$b){return \$b;}
  \$r=array_reduce(array('aaa','bbb','ccc'),'cat');
  echo 'reduced='.var_export(\$r,true).\"\\n\";
  \$pad=str_repeat('Z',40);"

cell 'C negative-long-seed' 0 \
 "function add(\$a,\$b){return \$a+\$b;}
  \$seed=100;
  \$r=array_reduce(array(1,2,3),'add',\$seed);
  echo 'reduced='.\$r.\"\\n\";
  \$pad=str_repeat('Z',40);"

echo
if [ "$fail" = 0 ]; then
	cat <<'EOF'
AS EXPECTED. ⭐ Cell A faults DETERMINISTICALLY -- `len=40` prints, so the reduce
itself completes; the fault is the LAST line, which READS `$seed` after the churn
has recycled the block array_reduce freed out from under it. ⛔⛔ THE CHURN IS NOT
THE OBSERVABLE AND AN EARLIER DRAFT OF THIS MESSAGE SAID IT WAS: drop the
trailing read and this cell exits 0. ⭐⭐⭐ Read cells B and C together: they make
the fault ATTRIBUTABLE. B takes the other arm of the same `if` and is correct;
C takes the SAME defective arm with an IS_LONG seed and is ALSO correct, because
a long has no allocated payload to free early.
▶ SO THE ROW'S BLOB MUST EMIT PAYLOAD-BEARING VALUES OR IT MEASURES NOTHING.
▶ §A3a obligation 5 (re-run against the R1h post-image) is where this becomes a
two-sided result. ⚠ THAT OBLIGATION'S WORDING IS `F141`, IT IS UNREVIEWED, AND
`_063` §4 MAY OVERTURN IT -- check the protocol before quoting it.
EOF
else
	cat <<'EOF'
⛔ DEVIATES. That is a REPORTABLE RESULT, not a broken probe -- record what you
saw, name the binary, and do NOT edit the expectations to match (F43/F47: a
check that refuses your row is a hypothesis first).
⚠ If cell A's rc MOVED rather than vanished, say which rc: a different fault is
a different finding from no fault.
EOF
fi
echo
echo 'ⓘ artefacts are under '"$WORK"' -- delete them when your gates are green.'
exit "$fail"
