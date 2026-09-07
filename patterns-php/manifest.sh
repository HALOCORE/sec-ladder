#!/bin/sh
# Regenerate `patterns-php/php-5.0.0.manifest` -- the sha256 of every `.c` and
# `.h` in the PRISTINE PHP 5.0.0 museum tarball (TASK_PHP_002, Phase 0).
#
# ⚠ READ-ONLY ON THE TARBALL. It is never rewritten, never patched, never
# extracted over. The scratch tree below is created under `.temp/` and deleted
# again; if you kill this script mid-run, `rm -rf .temp/php0/manifest.*` is the
# cleanup.
#
# ⚠⚠ WHY THIS FILE EXISTS AT ALL, and it is the same argument
# `common/census/README.md` §1 makes: the tarball lives under ANOTHER PROJECT'S
# gitignored `.temp/`, which that project's own convention makes deletable at
# any time. Every `file:line` in the PHP programme cites it. A corpus that
# cannot be re-identified is a corpus nobody can check.
#
# ⚠ Paths are ROOT-RELATIVE (`Zend/zend_alloc.c`, not
# `php-5.0.0/Zend/zend_alloc.c`) for two reasons: it is what `common/census/`
# already does, and it is exactly the string that slots into the read recipe
#     tar -xzOf <tarball> php-5.0.0/<path> | sed -n '<a>,<b>p'
# so a manifest line and a citation are the same token.
set -e

TARBALL=${PHP500_TARBALL:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz}
OUT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$OUT/.." && pwd)"
ROOT=php-5.0.0
SCRATCH="$REPO/.temp/php0/manifest.$$"

# The pin. If the tarball on this box is not this one, the manifest it would
# produce is a manifest of a different program, so refuse rather than write it.
WANT_SHA=5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
WANT_SIZE=5595997
WANT_ENTRIES=3815

if [ ! -f "$TARBALL" ]; then
  echo "MISSING TARBALL: $TARBALL" >&2
  echo "  Set PHP500_TARBALL, or re-fetch from museum.php.net (see SOURCES.md)." >&2
  exit 2
fi

got_sha=$(sha256sum "$TARBALL" | cut -d' ' -f1)
got_size=$(wc -c < "$TARBALL" | tr -d ' ')
if [ "$got_sha" != "$WANT_SHA" ]; then
  echo "TARBALL SHA MISMATCH" >&2
  echo "  want $WANT_SHA" >&2
  echo "  got  $got_sha" >&2
  exit 3
fi
if [ "$got_size" != "$WANT_SIZE" ]; then
  echo "TARBALL SIZE MISMATCH: want $WANT_SIZE got $got_size" >&2
  exit 3
fi
got_entries=$(tar -tzf "$TARBALL" | wc -l | tr -d ' ')
if [ "$got_entries" != "$WANT_ENTRIES" ]; then
  echo "TARBALL ENTRY-COUNT MISMATCH: want $WANT_ENTRIES got $got_entries" >&2
  exit 3
fi

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH"
# `--no-same-owner`/`--no-same-permissions`: this runs as an unprivileged user
# and the archive's uid/gid are irrelevant to a content hash.
tar -xzf "$TARBALL" -C "$SCRATCH" --no-same-owner --no-same-permissions \
    --wildcards "$ROOT/*.c" "$ROOT/*.h"

{ echo "# corpus:          php-5.0.0 (pristine museum tarball)"
  echo "# tarball:         php-5.0.0.tar.gz"
  echo "# tarball_sha256:  $WANT_SHA"
  echo "# tarball_size:    $WANT_SIZE"
  echo "# tarball_entries: $WANT_ENTRIES"
  echo "# root:            $ROOT"
  echo "# fields:          sha256 <2sp> path-relative-to-root"
  echo "# read:            tar -xzOf <tarball> $ROOT/<path> | sed -n '<a>,<b>p'"
  echo "# regenerate:      sh patterns-php/manifest.sh"
  ( cd "$SCRATCH/$ROOT" && find . \( -name '*.c' -o -name '*.h' \) -type f \
      | LC_ALL=C sort | xargs sha256sum | sed 's#  \./#  #' )
} > "$OUT/php-5.0.0.manifest"

rm -rf "$SCRATCH"

# digest-of-digests, so the manifest itself can be checked without the corpus
( cd "$OUT" && LC_ALL=C sha256sum php-5.0.0.manifest > MANIFEST.sha256 )

echo "files:  $(grep -vc '^#' "$OUT/php-5.0.0.manifest")"
echo "bytes:  $(wc -c < "$OUT/php-5.0.0.manifest" | tr -d ' ')"
cat "$OUT/MANIFEST.sha256"
