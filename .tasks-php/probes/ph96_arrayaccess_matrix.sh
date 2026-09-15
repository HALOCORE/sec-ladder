#!/bin/sh
# ph96_arrayaccess_matrix.sh -- the FOUR-HANDLER NATURAL EXPERIMENT behind row 12.
#
#   sh .tasks-php/probes/ph96_arrayaccess_matrix.sh [workdir]
#
# Default workdir is `.temp/php96probe`. Writes only there; deletes nothing you
# own. ⚠ `CLAUDE.md` "Don't" rule 1: THIS FILE is the generator; the `.so`, the
# `.php` scripts and the workdir are artefacts -- delete them when your gates
# are green. Never cite the workdir from `spec.md`/`NOTES.md` (§F6); cite this.
#
# ====================== WHAT IT MEASURES, AND WHY =========================
# `Zend/zend_object_handlers.c` in pristine PHP 5.0.0 calls the SAME helper,
# `zend_call_method_with_1_params`, from FOUR ArrayAccess handlers. The helper
# writes its out-parameter via `zend_call_function`, which sets
# `*fci->retval_ptr_ptr = NULL` at `zend_execute_API.c:595` under the comment
# *"we may return SUCCESS, and yet retval may be uninitialized, if there was an
# exception"* -- and returns SUCCESS anyway at `:873` with `EG(exception)` set
# (`:870-872`). So after a throwing user method the out-parameter is a
# GUARANTEED, DOCUMENTED NULL sentinel, and the obligation (`I12/O1`) is to
# test it.
#
# The four handlers make a 2x2 that the corpus entry does not mention:
#
#     site  handler        contract                     obligation discharged?
#     :384  offsetGet      output, `&retval`            YES -- `:385 if (!retval)`
#     :413  offsetSet      NO-OUTPUT, passes `NULL`     YES -- vacuously
#     :427  offsetExists   output, `&retval`            NO
#     :512  offsetUnset    output, `&retval`            NO
#
# Both CORRECT spellings and both WRONG spellings are in one file, by one
# author. `:413` is the one the 2005 repair (`cf020f133487`) later applied to
# `:512` -- so the repair did not invent a strategy, it copied the sibling 99
# lines up. The no-output contract was already supported in 5.0.0 at
# `Zend/zend_interfaces.c:48` (`retval_ptr_ptr ? retval_ptr_ptr : &retval`) and
# `:88-93`, which disposes of the value behind ITS OWN `if (retval)` NULL test
# -- the very test `:513` omits.
#
# ========================= HOW TO READ THE OUTPUT =========================
#   rc=255  no fault  PHP's own "Uncaught exception" fatal -- the CORRECT
#                     behaviour. Both guarded cells must look like this.
#   rc=139  si_addr=0x10   SIGSEGV in `_zval_ptr_dtor` (`zend_execute_API.c:389`,
#                     `(*zval_ptr)->refcount--`) -- offsetof(zval, refcount).
#   rc=139  si_addr=0x14   SIGSEGV in `i_zend_is_true` (`zend_execute.h:72`,
#                     `switch (op->type)`) -- offsetof(zval, type).
#
# ⭐ The two faults are DISTINGUISHABLE BY ADDRESS, and both offsets follow
# from the verified `struct _zval_struct` layout (`Zend/zend.h:287-293`) on
# LP64: the `zvalue_value` union is 16 B (`zend_object_value` = `{uint handle;
# zend_object_handlers *handlers;}`), so `refcount` is at 16 = 0x10 and `type`
# at 20 = 0x14. ▶ An address that is NOT one of those two is a DIFFERENT bug;
# say so rather than filing it under this row.
#
# ⚠⚠ TWO CAUTIONS TRAVEL WITH ANY RESULT FROM THIS PROBE (§A3a), AND A ROW
# THAT QUOTES IT MUST REPEAT THEM:
#   (1) the binary is php-in-safe-rust's ORACLE build (`-O3 -march=native
#       -flto`, mysql+webext), NOT a museum-default 5.0.0;
#   (2) a CLEAN run would NOT be evidence of absence (F3). A faulting run is
#       evidence of PRESENCE, which is the half this programme long lacked.

set -e

WORK="${1:-.temp/php96probe}"
ORACLE="${ORACLE:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext}"
PROBE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

[ -x "$ORACLE" ] || { echo "no 5.0.0 oracle at $ORACLE" >&2; exit 2; }
mkdir -p "$WORK"

gcc -shared -fPIC -O0 -o "$WORK/segaddr.so" "$PROBE_DIR/segaddr.c"

# One script per handler: every method benign except the one under test, which
# throws. The throw is what leaves the out-parameter at its `:595` NULL.
for m in offsetGet offsetSet offsetExists offsetUnset; do
	{
		echo '<?php'
		echo 'class C implements ArrayAccess {'
		for n in offsetExists offsetGet offsetSet offsetUnset; do
			case "$n" in
				offsetSet) sig='$o,$v' ;;
				*)         sig='$o' ;;
			esac
			if [ "$n" = "$m" ]; then body='throw new Exception("boom");'
			elif [ "$n" = offsetGet ]; then body='return 1;'
			elif [ "$n" = offsetExists ]; then body='return true;'
			else body=''
			fi
			echo "  function $n($sig){ $body }"
		done
		echo '}'
		echo '$c = new C;'
		case "$m" in
			offsetGet)    echo '$x = $c[0];' ;;
			offsetSet)    echo '$c[0] = 1;' ;;
			offsetExists) echo '$x = isset($c[0]);' ;;
			offsetUnset)  echo 'unset($c[0]);' ;;
		esac
	} > "$WORK/t_$m.php"
done

# A control in which NOTHING throws: every handler must complete cleanly, or
# the faults below are not attributable to the unwritten out-parameter.
{
	echo '<?php'
	echo 'class C implements ArrayAccess {'
	echo '  function offsetExists($o){ return true; }'
	echo '  function offsetGet($o){ return 1; }'
	echo '  function offsetSet($o,$v){ }'
	echo '  function offsetUnset($o){ }'
	echo '}'
	echo '$c = new C;'
	echo '$c[0] = 1; $x = $c[0]; $y = isset($c[0]); unset($c[0]);'
	echo 'echo "benign ok\n";'
} > "$WORK/benign.php"

printf '%-14s %-6s %-26s %-7s %s\n' HANDLER SITE CONTRACT RC FAULT
fail=0
for m in offsetGet offsetSet offsetExists offsetUnset; do
	case "$m" in
		offsetGet)    site=':384'; kind='output + GUARD :385'; want='none' ;;
		offsetSet)    site=':413'; kind='NO-OUTPUT (NULL)';    want='none' ;;
		offsetExists) site=':427'; kind='output, UNGUARDED';   want='0x14' ;;
		offsetUnset)  site=':512'; kind='output, UNGUARDED';   want='0x10' ;;
	esac
	set +e
	out=$(LD_PRELOAD="$PWD/$WORK/segaddr.so" timeout 60 "$ORACLE" -n "$WORK/t_$m.php" 2>&1)
	rc=$?
	set -e
	got=$(printf '%s' "$out" | grep -ao 'si_addr=[^ ]*' | head -1 | sed 's/si_addr=//')
	[ -n "$got" ] || got='none'
	printf '%-14s %-6s %-26s rc=%-4s %s' "$m" "$site" "$kind" "$rc" "$got"
	if [ "$got" = "$want" ]; then printf '   ok\n'; else printf '   ⛔ EXPECTED %s\n' "$want"; fail=1; fi
done

set +e
bout=$(LD_PRELOAD="$PWD/$WORK/segaddr.so" timeout 60 "$ORACLE" -n "$WORK/benign.php" 2>&1); brc=$?
set -e
printf '%-14s %-6s %-26s rc=%-4s %s' 'benign(none)' '--' 'nothing throws' "$brc" 'none'
if [ "$brc" = 0 ] && printf '%s' "$bout" | grep -qa 'benign ok'; then printf '   ok\n'
else printf '   ⛔ EXPECTED a clean run\n'; fail=1; fi

echo
if [ "$fail" = 0 ]; then
	echo 'MATRIX AS EXPECTED -- 2 guarded cells clean, 2 unguarded cells faulting at'
	echo 'DISTINCT offsets that match offsetof(zval,refcount)=0x10 and (zval,type)=0x14.'
else
	echo '⛔ MATRIX DEVIATES. That is a REPORTABLE RESULT, not a broken probe --'
	echo 'record what you saw, name the binary, and do NOT edit the expectations'
	echo 'to match (F43/F47: a check that refuses your row is a hypothesis first).'
fi
echo
echo 'ⓘ artefacts are under '"$WORK"' -- delete them when your gates are green.'
exit "$fail"
