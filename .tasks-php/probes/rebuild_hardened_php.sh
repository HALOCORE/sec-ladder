#!/usr/bin/env bash
# rebuild_hardened_php.sh -- build PHP 5.0.0, apply a row's R1h, and rebuild.
#
# PROTOCOL_PHP.md §A3a OBLIGATION 5 IS *REQUIRED* AND THIS IS HOW YOU DISCHARGE
# IT. Run it; do not re-derive the cost. Written by TASK_PHP_057's reviewer as
# §1.2's generator and COMMITTED out of gitignored .temp/ by the manager --
# evidence for a protocol rule may not live in scratch (F51/F99, citecheck's §H
# warning block, and the fourth instance of that class this programme has had).
#
#   sh .tasks-php/probes/rebuild_hardened_php.sh \
#        [--patch PATH] [--trigger PATH] [--label NAME] [--workdir DIR] [--dry-run]
#
# ⭐ `--dry-run` PRINTS THE RESOLVED SETTINGS AND EXITS. It exists so the claim
# two paragraphs down -- *"the defaults are still exactly ph97's"* -- is
# CHECKABLE IN A SECOND instead of by a 30-second build nobody will re-run
# (`.memory-php/04-process.md` law 6: a figure a document asserts is computed
# from the tree, or it is not asserted).
#
# ✅ GENERALISED 2026-09-16 BY THE MANAGER, WHICH LINE 10 OF THE PREVIOUS
# VERSION ASKED WHOEVER DID IT TO SAY HERE. It used to be PINNED to ph97 and to
# hard-code the trigger inline. **The defaults are still exactly ph97's**, so
# `§A3a`'s citation of this file and `_057 §1.2`'s measured costs both still
# resolve to the same run; pass the flags to point it at another row.
# ⚠ ONE DEFAULT DID CHANGE, and it is the workdir: `.temp/php57/oracle` became
# `.temp/r1h-<label>/oracle`, so two rows can hold trees at once. Nothing cites
# the old path -- it is deleted scratch by construction -- but it is named here
# rather than left for a reader to discover from a diff.
#
# ⭐⭐ AND THE GENERALISATION FOUND A REAL GAP, WHICH IS WHY THE OUTPUT CHANGED.
# Steps 3 and 5 used to assert `rc=139` then `rc=0` and throw stdout away. That
# is only legible for a row whose target error is a SIGNAL. `ph66`'s error is a
# WRONG ANSWER at `rc=0` -- the delete removes a live element and PHP exits
# cleanly -- so an rc-only report reads "no change" across a repair that in fact
# flips the observable completely. ▶ **THIS SCRIPT NOW PRINTS rc AND stdout FOR
# BOTH IMAGES AND ADJUDICATES NOTHING.** The row compares them and says what it
# saw. A generator that encodes one row's notion of "worked" is a generator that
# silently mis-reports every row with a different one.
#
# CLAUDE.md rule 1: keep the generator, delete the artefact. The 60 MB build tree
# this produces was deleted when the round finished; this script rebuilds it.
#
# Measured 2026-09-15 on this box: cold build 30 s wall, 60 MB, no sudo, NO NETWORK.
# Incremental rebuild after applying the R1h patch: 685 ms.
#
# ⚠ NO NETWORK. The build script would curl museum.php.net if the tarball cache
#   is absent; step 1 copies the already-cached tarball instead. Its sha256 is
#   5783e0c0...d6919, which is the corpus's own citation base.
set -euo pipefail

SEC=/home/apt/repos_common/sec-ladder
PISR=/home/apt/repos_common/php-in-safe-rust

# ---- ph97's defaults, unchanged, so §A3a's citation still names this run ----
LABEL=ph97
PATCHF=$SEC/patterns-php/ph97-optarg-unwritten/controls/f7326d627962.patch
TRIGGER=
WORKDIR=
DRY=0

while [ $# -gt 0 ]; do
	case "$1" in
		--patch)   PATCHF=$2; shift 2 ;;
		--trigger) TRIGGER=$2; shift 2 ;;
		--label)   LABEL=$2; shift 2 ;;
		--workdir) WORKDIR=$2; shift 2 ;;
		--dry-run) DRY=1; shift ;;
		*) echo "unknown argument: $1" >&2; exit 2 ;;
	esac
done
OH=${WORKDIR:-$SEC/.temp/r1h-$LABEL/oracle}

if [ "$DRY" = 1 ]; then
	echo "label   = $LABEL"
	echo "patch   = $PATCHF"
	echo "patch exists? $([ -f "$PATCHF" ] && echo yes || echo NO)"
	echo "trigger = ${TRIGGER:-<inline ph97 default: var_dump(mb_get_info())>}"
	echo "workdir = $OH"
	echo 'ⓘ dry run: nothing was built.'
	exit 0
fi

[ -f "$PATCHF" ] || { echo "no patch at $PATCHF" >&2; exit 2; }

echo '==> 1. stage a relocated oracle home from the CACHED tarball (no fetch)'
mkdir -p "$OH/build-5.0.0"
cp -n "$PISR/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz" "$OH/build-5.0.0/"
sha256sum "$OH/build-5.0.0/php-5.0.0.tar.gz"
ln -sfn "$PISR/.app-tests/.temp/oracle/expat-prefix" "$OH/expat-prefix"

# The ph97 default trigger stays inline so a no-argument run is self-contained.
if [ -z "$TRIGGER" ]; then
	TRIGGER=$OH/trigger.php
	printf '<?php var_dump(mb_get_info()); ?>\n' > "$TRIGGER"
fi
[ -f "$TRIGGER" ] || { echo "no trigger at $TRIGGER" >&2; exit 2; }
echo "    label=$LABEL"
echo "    patch=$PATCHF"
echo "    trigger=$TRIGGER"

echo '==> 2. COLD BUILD (timed)'
S=$(date +%s)
env APPTEST_ORACLE_HOME="$OH" WEBEXT=1 \
    MYSQL_PREFIX="$PISR/.app-tests/.temp/oracle/mysql-4.1.15" \
    timeout 1800 bash "$PISR/.app-tests/oracle/build-php-5.0.0.sh" >"$OH/cold.log" 2>&1
echo "COLD_BUILD_WALL_SECONDS=$(( $(date +%s) - S ))"
tail -3 "$OH/cold.log"

SRC=$OH/build-5.0.0-mysql-webext/php-5.0.0
PHP=$SRC/sapi/cli/php

# rc AND stdout, for both images.  ⛔ This function asserts NOTHING -- see the
# header.  The row reads the two blocks and states the difference itself.
run_image() {
	set +e
	"$PHP" -n "$TRIGGER" >"$OH/$1.out" 2>"$OH/$1.err"
	echo "  $1 rc=$?"
	set -e
	echo "  $1 stdout ---"
	sed 's/^/    | /' "$OH/$1.out"
	echo "  $1 stdout end (sha $(sha256sum < "$OH/$1.out" | cut -c1-12))"
}

echo '==> 3. PRE-IMAGE (pristine 5.0.0): what does the trigger do?'
run_image pristine

echo '==> 4. apply R1h and rebuild INCREMENTALLY (timed)'
( cd "$SRC" && patch -p1 < "$PATCHF" )
S=$(date +%s%N)
( cd "$SRC" && make -j"$(nproc)" >"$OH/incr.log" 2>&1 )
echo "INCR_REBUILD_MS=$(( ( $(date +%s%N) - S ) / 1000000 ))"

echo '==> 5. POST-IMAGE (R1h applied): what does the same trigger do now?'
run_image hardened

echo '==> 6. THE COMPARISON, stated as data and not as a verdict'
if cmp -s "$OH/pristine.out" "$OH/hardened.out"; then
	echo '  stdout: IDENTICAL across the repair'
else
	echo '  stdout: DIFFERS across the repair -- diff pristine -> hardened:'
	diff "$OH/pristine.out" "$OH/hardened.out" | sed 's/^/    /' || true
fi
du -sh "$OH"
echo "==> DONE. Delete $OH when finished -- it is the artefact, this file is the generator."
