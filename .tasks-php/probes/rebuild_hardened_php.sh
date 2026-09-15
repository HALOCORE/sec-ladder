#!/usr/bin/env bash
# rebuild_hardened_php.sh -- build PHP 5.0.0, apply a row's R1h, and rebuild.
#
# PROTOCOL_PHP.md §A3a OBLIGATION 5 IS *REQUIRED* AND THIS IS HOW YOU DISCHARGE
# IT. Run it; do not re-derive the cost. Written by TASK_PHP_057's reviewer as
# §1.2's generator and COMMITTED out of gitignored .temp/ by the manager --
# evidence for a protocol rule may not live in scratch (F51/F99, citecheck's §H
# warning block, and the fourth instance of that class this programme has had).
#
# /!\ IT IS PINNED TO ph97's R1h. A row using it edits step 4's patch path --
# and if you generalise it to take the row as an argument, say so here.
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
OH=$SEC/.temp/php57/oracle
ROW=$SEC/patterns-php/ph97-optarg-unwritten

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

echo '==> 3. PRISTINE: the trigger must fault'
printf '<?php var_dump(mb_get_info()); ?>\n' > "$OH/trigger.php"
set +e; "$PHP" -n "$OH/trigger.php" >/dev/null 2>&1; echo "  pristine rc=$? (expect 139)"; set -e

echo '==> 4. apply R1h and rebuild INCREMENTALLY (timed)'
( cd "$SRC" && patch -p1 < "$ROW/controls/f7326d627962.patch" )
S=$(date +%s%N)
( cd "$SRC" && make -j"$(nproc)" >"$OH/incr.log" 2>&1 )
echo "INCR_REBUILD_MS=$(( ( $(date +%s%N) - S ) / 1000000 ))"

echo '==> 5. POST-IMAGE: the trigger must answer'
set +e; "$PHP" -n "$OH/trigger.php" >/dev/null 2>&1; echo "  hardened rc=$? (expect 0)"; set -e
du -sh "$OH"
echo '==> DONE. Delete $OH when finished -- it is the artefact, this file is the generator.'
