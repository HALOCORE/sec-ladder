#!/bin/sh
# Regenerates the manager's scratch downloads into .temp/mgr/.
#   mbfl/*.c, f95c1df58349.patch  -> RECAP_PHP.md F34, TASK_PHP_016 §2
#   batch/up/*                    -> RECAP_PHP.md F36, .tasks-php/UPSTREAM_001.md
# Artefacts deleted per CLAUDE.md "Don't" rule 1; this is the generator.
set -e
# artefacts stay in gitignored scratch; only this generator is committed
cd "$(dirname "$0")/../.temp/mgr" || { mkdir -p "$(dirname "$0")/../.temp/mgr"; cd "$(dirname "$0")/../.temp/mgr"; }

# --- F34 / ph07: mbfl_strcut at three tags -----------------------------------
mkdir -p mbfl
for tag in php-5.0.0 php-5.3.0 php-5.4.0; do
  curl -sSL -o "mbfl/$tag.c" \
    "https://raw.githubusercontent.com/php/php-src/$tag/ext/mbstring/libmbfl/mbfl/mbfilter.c"
done

# ph03's R1h, verified in TASK_PHP_013 (the row keeps its own copy; this is a cross-check)
curl -sSL -o "f95c1df58349.patch" \
  "https://github.com/php/php-src/commit/f95c1df58349.patch"

# --- F36 / UPSTREAM_001: the batch survey ------------------------------------
# 5.0.0 comes from the PINNED TARBALL, never from GitHub (SOURCES.md).
: "${PHP500_TARBALL:=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz}"
mkdir -p batch/up
sha256sum "$PHP500_TARBALL" | grep -q 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919 \
  || { echo "REFUSED: tarball sha256 is not the pin (SOURCES.md)"; exit 1; }
for f in string streamsfuncs; do
  tar -xzOf "$PHP500_TARBALL" "php-5.0.0/ext/standard/$f.c" > "batch/$f.c"
done

# later tags: the four rows' two files, plus the PHP_SAFE_FD_SET macro
for tag in php-5.1.0 php-5.2.0 php-5.3.0 php-5.4.0 php-5.6.0; do
  for f in string streamsfuncs; do
    curl -sSL -o "batch/up/$tag.$f.c" \
      "https://raw.githubusercontent.com/php/php-src/$tag/ext/standard/$f.c"
  done
done
for tag in php-5.0.0 php-5.1.0; do
  curl -sSL -o "batch/up/$tag.php_network.h" \
    "https://raw.githubusercontent.com/php/php-src/$tag/main/php_network.h"
done

# --- F35: the non-UTF-8 census -----------------------------------------------
# Reproduces "41 of 1170", the 5 cited files and the grep/ugrep false negative.
rm -rf batch/x && mkdir -p batch/x && tar -xzf "$PHP500_TARBALL" -C batch/x
find batch/x -name '*.c' -o -name '*.h' | while read -r f; do
  iconv -f UTF-8 -t UTF-8 "$f" >/dev/null 2>&1 || echo "$f"
done > batch/nonutf8.txt
echo "non-UTF-8 .c/.h files: $(wc -l < batch/nonutf8.txt) of $(find batch/x \( -name '*.c' -o -name '*.h' \) | wc -l)"
# The one-byte trigger: this copy differs from string.c ONLY at "S\xe6ther".
python3 -c "
b=open('batch/string.c','rb').read()
open('batch/string_clean.c','wb').write(b.replace(b'S\xe6ther',b'Saether'))"
cat <<'EOF'
⚠ F35 CANNOT BE REPRODUCED FROM THIS SCRIPT. `grep` is a shell FUNCTION in the
  interactive profile and functions are not exported to sh, so everything below
  runs GNU grep and SUCCEEDS. To see the failure, paste these into a Bash call:
      grep -n "PHP_FUNCTION(str_repeat)" .temp/mgr/batch/string.c        # exit 1, SILENT
      grep -n "PHP_FUNCTION(str_repeat)" .temp/mgr/batch/string_clean.c  # 4115  (one byte apart)
EOF

echo "refetched: mbfl/*.c, f95c1df58349.patch, batch/{string,streamsfuncs}.c, batch/up/*"
