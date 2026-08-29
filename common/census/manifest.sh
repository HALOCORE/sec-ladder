#!/bin/sh
# Regenerate the three C-corpus sha256 manifests (TASK_129, promoted at
# TASK_132). READ-ONLY on the corpora -- two of the three live under ANOTHER
# PROJECT'S `.temp/`, which that project's convention makes deletable at any
# time, and that is exactly why these manifests are in the tree.
#
# ⚠ Paths are CORPUS-RELATIVE, and that is not cosmetic: the absolute form is
# 950 K, the relative form is 506 K, and the corpus root is one header line, so
# the halving costs NO information at all.
set -e
OUT="$(cd "$(dirname "$0")" && pwd)"
php=/home/apt/repos_common/php-in-safe-rust/build/php-4.0.2
coreutils=/home/apt/repos_common/unsafe-rust-pitfall/TASKS/TASK014_eng_coreutils_u2/.temp/work/coreutils
cgnu=/home/apt/repos_common/unsafe-rust-pitfall/.temp/shared/artifacts/pr2/benchmarks/c-gnu
gen() {  # $1 = corpus name, $2 = root
  if [ ! -d "$2" ]; then
    echo "MISSING CORPUS: $1 -> $2" >&2
    return 1
  fi
  { echo "# corpus: $1"
    echo "# root:   $2"
    echo "# fields: sha256 <2sp> path-relative-to-root"
    ( cd "$2" && find . \( -name '*.c' -o -name '*.h' \) -type f \
        | LC_ALL=C sort | xargs sha256sum | sed 's#  \./#  #' )
  } > "$OUT/$1.manifest"
}
rc=0
for c in php coreutils cgnu; do
  eval "root=\$$c"
  gen "$c" "$root" || rc=1
done
# digest-of-digests: verifies the manifests themselves without reading a corpus
( cd "$OUT" && LC_ALL=C sha256sum php.manifest coreutils.manifest cgnu.manifest \
    > MANIFEST.sha256 )
wc -l "$OUT"/*.manifest
cat "$OUT/MANIFEST.sha256"
exit $rc
