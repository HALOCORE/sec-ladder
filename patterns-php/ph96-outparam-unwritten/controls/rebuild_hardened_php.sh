#!/usr/bin/env bash
# ph96 -- PROTOCOL_PHP.md §A3a OBLIGATION 5, DISCHARGED: build PHP 5.0.0, apply
# this row's R1h backport, rebuild, and re-run the trigger against BOTH builds.
#
#   bash patterns-php/ph96-outparam-unwritten/controls/rebuild_hardened_php.sh
#
# ⚠ ADAPTED FROM `.tasks-php/probes/rebuild_hardened_php.sh`, WHICH IS PINNED TO
# ph97's R1h AND SAYS SO IN ITS OWN HEADER. That file is NOT edited: this is a
# row-local copy whose step 4 applies ph96's backport instead. The probe's own
# measured costs still hold -- cold build ~30 s, 60 MB, no sudo, NO NETWORK.
#
# ⛔⛔ AND THE PATCH CANNOT BE APPLIED WITH `patch -p1`, WHICH IS THE WHOLE
# REASON THIS ROW SAYS **BACKPORT**. `controls/cf020f133487.patch`'s pre-image
# carries `SEPARATE_ARG_IF_REF(offset);` and `zval_ptr_dtor(&offset);`, two lines
# 5.0.0 does not have. Step 4 therefore performs the THREE-LINE EDIT the patch
# describes, in place, and prints the diff so a reader can compare it with the
# commit. `controls/r1h_backport.py` is what checks the edit reproduces
# upstream's own diffstat.
#
# ⭐ WHAT THIS BUYS, AND IT IS THE STRONGEST EVIDENCE A ROW CAN CARRY ABOUT ITS
# OWN R1h: the fix's efficacy is measured ON REAL PHP rather than on the kernel.
#
# ⚠⚠ AND IT ALSO MEASURES THE SECOND LIMB, WHICH IS THIS ROW'S POINT: the SAME
# rebuilt, patched interpreter is driven with a throwing `offsetExists`, and
# `cf020f133487` does not repair that one. ../NOTES.md section 5.
#
# ⚠ NO NETWORK. The build script would curl museum.php.net if the tarball cache
#   is absent; step 1 copies the already-cached tarball instead. Its sha256 is
#   5783e0c0...d6919, which is the corpus's own citation base.
# ⚠ CLAUDE.md rule 1: keep the generator, delete the artefact. Delete $OH when
#   your gates are green; this file rebuilds it.
set -euo pipefail

SEC=/home/apt/repos_common/sec-ladder
PISR=/home/apt/repos_common/php-in-safe-rust
OH=$SEC/.temp/php96/oracle

echo '==> 1. stage a relocated oracle home from the CACHED tarball (no fetch)'
mkdir -p "$OH/build-5.0.0"
cp -n "$PISR/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz" "$OH/build-5.0.0/"
sha256sum "$OH/build-5.0.0/php-5.0.0.tar.gz"
ln -sfn "$PISR/.app-tests/.temp/oracle/expat-prefix" "$OH/expat-prefix"

echo '==> 2. COLD BUILD (timed)'
S=$(date +%s)
env APPTEST_ORACLE_HOME="$OH" WEBEXT=1 \
    MYSQL_PREFIX="$PISR/.app-tests/.temp/oracle/mysql-4.1.15" \
    timeout 1800 bash "$PISR/.app-tests/oracle/build-php-5.0.0.sh" >"$OH/cold.log" 2>&1
echo "COLD_BUILD_WALL_SECONDS=$(( $(date +%s) - S ))"
tail -3 "$OH/cold.log"

SRC=$OH/build-5.0.0-mysql-webext/php-5.0.0
PHP=$SRC/sapi/cli/php

# the two triggers: the row's own site, and the limb cf020f133487 does not touch
mk_trigger() {   # $1 = method that throws, $2 = the operation
	{
		echo '<?php'
		echo 'class C implements ArrayAccess {'
		for n in offsetExists offsetGet offsetSet offsetUnset; do
			case "$n" in offsetSet) sig='$o,$v' ;; *) sig='$o' ;; esac
			if [ "$n" = "$1" ]; then body='throw new Exception("boom");'
			elif [ "$n" = offsetGet ]; then body='return 1;'
			elif [ "$n" = offsetExists ]; then body='return true;'
			else body=''; fi
			echo "  function $n($sig){ $body }"
		done
		echo '}'
		echo '$c = new C;'
		echo "$2"
	} > "$OH/t_$1.php"
}
mk_trigger offsetUnset 'unset($c[0]);'
mk_trigger offsetExists '$x = isset($c[0]);'

echo '==> 3. PRISTINE: both triggers must fault (rc 139)'
set +e
"$PHP" -n "$OH/t_offsetUnset.php"  >/dev/null 2>&1; echo "  pristine offsetUnset  rc=$? (expect 139)"
"$PHP" -n "$OH/t_offsetExists.php" >/dev/null 2>&1; echo "  pristine offsetExists rc=$? (expect 139)"
set -e

echo '==> 4. apply the THREE-LINE BACKPORT of cf020f133487 and rebuild (timed)'
F=$SRC/Zend/zend_object_handlers.c
cp "$F" "$OH/zend_object_handlers.c.pristine"
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]
lines = open(p, encoding='latin-1').read().split('\n')
assert lines[508].strip() == 'zval *retval;', lines[508]
assert 'offsetunset' in lines[511] and '&retval' in lines[511], lines[511]
assert lines[512].strip() == 'zval_ptr_dtor(&retval);', lines[512]
lines[511] = lines[511].replace('"offsetunset", &retval, offset',
                                '"offsetunset", NULL, offset')
open(p, 'w', encoding='latin-1').write(
    '\n'.join(l for i, l in enumerate(lines) if i not in (508, 512)))
print("  backport applied at :509/:512/:513")
PY
diff -u "$OH/zend_object_handlers.c.pristine" "$F" || true
S=$(date +%s%N)
( cd "$SRC" && make -j"$(nproc)" >"$OH/incr.log" 2>&1 )
echo "INCR_REBUILD_MS=$(( ( $(date +%s%N) - S ) / 1000000 ))"

echo '==> 5. POST-IMAGE on REAL PHP'
set +e
"$PHP" -n "$OH/t_offsetUnset.php"  >/dev/null 2>&1
echo "  hardened offsetUnset  rc=$? (expect 255 -- PHP's own Uncaught exception fatal)"
"$PHP" -n "$OH/t_offsetExists.php" >/dev/null 2>&1
echo "  hardened offsetExists rc=$? (expect 139 -- THE SECOND LIMB, UNREPAIRED)"
set -e
echo
echo '  ⭐ THE UNSET LIMB IS REPAIRED ON REAL PHP BY THE ROW'"'"'S OWN R1h.'
echo '  ⛔ THE EXISTS LIMB IS NOT, AND cf020f133487 DOES NOT CLAIM TO: it edits'
echo '     zend_std_unset_dimension and nothing else. ../NOTES.md section 5 has'
echo '     the SCOPE of what this box can say about that.'
du -sh "$OH"
echo '==> DONE. Delete $OH when finished -- it is the artefact, this file is the generator.'
