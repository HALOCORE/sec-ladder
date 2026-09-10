#!/bin/sh
# fdset_census.sh -- every FD_SET()/FD_ISSET() site in pristine PHP 5.0.0.
#
# Evidence for the open-item-46 adjudication: `ph16` prices ONE of the four
# fd-set sites that commit 99e290f882c9 repairs, and the commit leaves a fifth
# cluster untouched entirely. This regenerates the census so the finding rests
# on a committed generator rather than on a scratch file (CLAUDE.md rule 1, and
# `citecheck.py`'s warning about committed docs citing deletable `.temp/`).
#
#   sh .tasks-php/probes/fdset_census.sh            # table to stdout
#   sh .tasks-php/probes/fdset_census.sh out.txt    # ...and to a file
#
# ⚠ `grep -a` throughout: plain `grep` dispatches to `ugrep` on this box and
# exits 1 with NO OUTPUT on the 41 non-UTF-8 files in the corpus, which reads
# exactly like "no match" (F35).
set -e

T="${PHP500_TARBALL:-/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz}"
want=5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
got=$(sha256sum "$T" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "tarball sha256 $got != $want" >&2; exit 1; }

out="${1:-/dev/stdout}"
# ⚠ NOT mktemp: CLAUDE.md rule 1 forbids /tmp scratch, and mktemp honours TMPDIR.
# Scratch goes under the repo's own .temp/, which is gitignored and rm-able.
root=$(cd "$(dirname "$0")/../.." && pwd)
tmp="$root/.temp/fdcensus.$$"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT

tar -tzf "$T" | grep -a '\.c$' > "$tmp/cfiles"
: > "$tmp/hits"
while read -r f; do
	n=$(tar -xzOf "$T" "$f" 2>/dev/null | grep -ac '\bFD_SET(\|\bFD_ISSET(' || true)
	[ "${n:-0}" -gt 0 ] && printf '%s %s\n' "$n" "${f#php-5.0.0/}" >> "$tmp/hits"
done < "$tmp/cfiles"

{
	echo "FD_SET()/FD_ISSET() sites in pristine php-5.0.0"
	echo "tarball sha256 $want"
	echo
	sort -rn "$tmp/hits"
	echo
	awk '{s+=$1} END{printf "total: %d sites in %d files\n", s, NR}' "$tmp/hits"
	echo
	echo "repaired by 99e290f882c9 (7 files): ext/ftp/ftp.c ext/openssl/xp_ssl.c"
	echo "  ext/soap/php_http.c ext/sockets/sockets.c ext/standard/streamsfuncs.c"
	echo "  main/network.c main/streams/xp_socket.c"
	echo "NOT repaired by it: sapi/cgi/libfcgi/* (bundled third-party FastCGI),"
	echo "  win32/select.c, netware/pipe.c -- only the FastCGI one is built here."
} > "$out"
