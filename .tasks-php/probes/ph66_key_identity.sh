#!/bin/sh
# ph66_key_identity.sh -- row 13's CRITERION-2 INSTRUMENT, run on real 5.0.0.
#
#   sh .tasks-php/probes/ph66_key_identity.sh [workdir]
#
# Default workdir is `.temp/php66probe`. Writes only there. ⚠ `CLAUDE.md`
# "Don't" rule 1: THIS FILE is the generator; the `.php` scripts and the workdir
# are artefacts -- delete them when your gates are green. Never cite the workdir
# from `spec.md`/`NOTES.md` (§F6); cite this.
#
# ====================== WHAT IT MEASURES, AND WHY =========================
# `Zend/zend_hash.c:464` in pristine PHP 5.0.0 settles a bucket's KEY KIND with
# a DISJUNCT:
#
#     if ((p->h == h) && ((p->nKeyLength == 0) ||        /* Numeric index */
#         ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, n)))))
#
# For a NUMERIC bucket `nKeyLength` is 0, the left disjunct fires, and the key
# is never compared at all -- hash equality alone is treated as identity. The
# collision does not need a preimage: a numeric bucket stores the RAW index, so
# running DJBX33A FORWARDS on a string key gives the integer index it will
# destroy (`probes/ph66_djbx33a_collide.py`). "abc" -> 6385036779.
#
# ⭐⭐⭐ THE CENSUS IN THAT PROBE SHOWS :464 IS THE *ONLY* ONE OF THE FILE'S TEN
# `p->h == h` PREDICATES THAT SERVES BOTH KEY KINDS FROM ONE CALL SITE, and the
# only one that is wrong. The other nine already spell the R1h's own required-
# conjunct form.
#
# ========================= HOW TO READ THE OUTPUT =========================
# ⛔⛔ EVERY CELL EXITS 0. THAT IS THE RESULT, NOT A FAILURE TO REPRODUCE.
# This row's target error is a WRONG ANSWER, not a signal: no fault, no ASan
# report, nothing in `si_addr`. The observable is the SURVIVOR LIST, which is
# why each cell prints one and compares it to a stated expectation.
#
#   A  victim alone                 -> victim destroyed.  SILENT.
#   B  a reference still holds it    -> victim destroyed.  SILENT.
#   C  victim is an array            -> victim destroyed.  SILENT.
#   D  string key inserted FIRST     -> ⭐⭐⭐ THE NAMED KEY SURVIVES AND THE
#                                       UNNAMED ONE DIES. Both halves wrong.
#   E  benign (keys really present)  -> correct, and identical post-R1h.
#
# ⛔⛔ CELLS A-C REFUTE A MANAGER CLAIM AND THE REFUTATION IS THE POINT.
# `ROW13_001.md` §4 asserted that the harm was SELECTABLE FROM THE BLOB between
# a silent wrong answer and an ASan-visible use-after-free, and built a research
# argument on top of it. ⛔ MEASURED, ALL THREE SHAPES ARE SILENT AND rc=0.
# The reason is in the delete's own tail: `pDestructor` is `zval_ptr_dtor`,
# which frees only at count 0 -- so the last holder's free is a CORRECT free of
# a value nobody else names -- and the bucket's one external alias,
# `ht->pInternalPointer`, is explicitly repaired four lines above the free
# (`zend_hash.c` "if (ht->pInternalPointer == p)"). There is no dangling holder
# to produce a UAF. ▶ The catalogue's own `⚠ risk` note said exactly this
# ("it produces no fault -- a silent wrong answer") and it was right; §4 was a
# second home for the fact, and it disagreed (F131).
#
# ⚠⚠ TWO CAUTIONS TRAVEL WITH ANY RESULT FROM THIS PROBE (§A3a), AND A ROW
# THAT QUOTES IT MUST REPEAT THEM:
#   (1) the binary is php-in-safe-rust's ORACLE build, the PLAIN
#       `php-5.0.0-mysql-webext`, NOT a museum-default 5.0.0, and its flags are
#       NOT RECORDED IN A `.buildinfo` (only the `-O3lto`/`-maxlto` siblings
#       carry one); its `config.status` says `-O0`. Say that, do not name
#       flags (F139);
#   (2) a CLEAN run would NOT be evidence of absence (F3).
set -e

WORK="${1:-.temp/php66probe}"
ORACLE="${ORACLE:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext}"

[ -x "$ORACLE" ] || { echo "no 5.0.0 oracle at $ORACLE" >&2; exit 2; }
mkdir -p "$WORK"

# One helper, shared by every cell: print the surviving keys, comma-separated.
cat > "$WORK/_survivors.inc" <<'EOF'
<?php
function survivors($a) {
  $r = array();
  foreach ($a as $k => $v) { $r[] = var_export($k, true); }
  return implode(",", $r);
}
EOF

cell() {   # cell <name> <expected survivors> <php body>
	{ cat "$WORK/_survivors.inc"; printf '%s\n' "$3"; } > "$WORK/c_$1.php"
	set +e
	got=$(timeout 60 "$ORACLE" -n "$WORK/c_$1.php" 2>&1); rc=$?
	set -e
	printf '%-26s rc=%-4s survivors=%-22s' "$1" "$rc" "$got"
	if [ "$rc" = 0 ] && [ "$got" = "$2" ]; then printf 'ok\n'
	else printf '⛔ EXPECTED rc=0 survivors=%s\n' "$2"; fail=1; fi
}

N=6385036779          # DJBX33A("abc\0"), see ph66_djbx33a_collide.py
fail=0
printf '%-26s %-7s %-31s %s\n' CELL RC OBSERVABLE VERDICT

cell 'A victim-alone'    "'other'" \
 "\$a=array(); \$a[$N]='V'; \$a['other']='O'; unset(\$a['abc']); echo survivors(\$a);"

cell 'B reference-held'  "'other'" \
 "\$a=array(); \$a[$N]='V'; \$a['other']='O'; \$b=&\$a[$N]; unset(\$a['abc']); echo survivors(\$a);"

cell 'C victim-is-array' "'other'" \
 "\$a=array(); \$a[$N]=array(1,2,3); \$a['other']='O'; unset(\$a['abc']); echo survivors(\$a);"

cell 'D named-key-survives' "'abc'" \
 "\$a=array(); \$a['abc']='ABC'; \$a[$N]='NUM'; unset(\$a['abc']); echo survivors(\$a);"

cell 'E benign-control'  "$N,'other'" \
 "\$a=array(); \$a[$N]='V'; \$a['other']='O'; \$a[7]='S'; \$a['abc']='A'; unset(\$a['abc']); unset(\$a[7]); echo survivors(\$a);"

echo
if [ "$fail" = 0 ]; then
	cat <<'EOF'
AS EXPECTED. ⭐ Read cell D twice: `unset($a["abc"])` LEFT 'abc' IN THE ARRAY
and destroyed the unrelated live element instead -- the named key survives, the
unnamed one dies, and PHP exits 0 with nothing on stderr. ⛔ Cells A-C are
SILENT TOO; there is no UAF variant (see this file's header).
▶ §A3a obligation 5 (re-run against the R1h post-image) is where this becomes
a two-sided result. Run:
    sh .tasks-php/probes/rebuild_hardened_php.sh --label ph66 \
       --patch <b73349dbe4e9.patch> --trigger <cell D's script>
⛔⛔ AND NOTE WHAT OBLIGATION 5 SAYS: it is "GATED ON the pre-image run
faulted", and this row's pre-image run does NOT fault -- so the protocol as
written tells this row to SKIP it. That is F141, and the row must discharge the
obligation anyway and say so.
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
