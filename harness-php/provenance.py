#!/usr/bin/env python3
"""Validate a php row's `provenance` block against the pinned PHP 5.0.0 tarball.

    python3 harness-php/provenance.py ph00            # one row
    python3 harness-php/provenance.py --all           # every row
    python3 harness-php/provenance.py ph07 --show     # print the excerpt
    python3 harness-php/provenance.py ph07 --no-tarball
                                                      # manifest-only, for a
                                                      # box without the tarball

Exit 0 if every checked row verifies, 1 otherwise.

============================================================================
WHAT IT IS FOR
============================================================================
`PLAN_PHP.md` §6: `extract_sha256` is the load-bearing field, because it turns
*"this kernel came from those lines of that tarball"* from a claim into a
one-command check. Nothing else in the programme can tell a citation that
drifted from a citation that is right -- and `PLAN_PHP.md` §1 records that six
reproducer comments in the source corpus describe PHP 4.0.2 code that no
longer exists at 5.0.0, one of which SAYS SO IN ITS OWN TEXT and was still
believed.

============================================================================
IT DOES NOT `exec` `extract_cmd`, AND THAT IS DELIBERATE
============================================================================
Running a shell string out of a `spec.md` would be arbitrary code execution
driven by a document, and it would also be a WEAKER check: a command that
extracts the right bytes by some other route would pass while the recorded
coordinates were wrong. So this module

  1. derives the excerpt from the STRUCTURED fields (`c_file`, `c_lines`)
     using Python's own tar reader, and hashes that;
  2. INDEPENDENTLY reconstructs the canonical `extract_cmd` string from those
     same fields and requires the recorded one to match it byte for byte.

(2) is what keeps the human-runnable command honest; (1) is what settles the
bytes. A row can fail either way, and the two failures mean different things:
(1) says the line span is wrong, (2) says the documented command does not
describe the line span.

⚠ `sed -n 'a,bp'` is 1-BASED AND INCLUSIVE, and the slice below is written to
match that exactly, including the case of a file with no final newline.
Verified against real `sed` in `TASK_PHP_002` T5.
"""

import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys
import tarfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS = os.path.join(REPO, "patterns-php")
MANIFEST = os.path.join(PATTERNS, "php-5.0.0.manifest")

TARBALL_SHA256 = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
TARBALL_ROOT = "php-5.0.0"
DEFAULT_TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
    "build-5.0.0/php-5.0.0.tar.gz")

#: ⚠ `check.py::read_contract`'s EXACT spelling, and it must stay exact.
#: The naive `\n``` form failed at TASK_PHP_002 on a `spec.md` whose
#: closing fence had no preceding newline: it ran on to the NEXT fence in
#: the file and reported `Extra data`, while the gate parsed it fine. A
#: validator that disagrees with the gate about where the contract ENDS
#: cannot be trusted about what is IN it.
_FENCE = re.compile(r"```slb-contract\s*\n(.*?)```", re.S)

#: A row that carries no PHP provenance at all -- `ph00-smoke` is the only one
#: this is meant for -- must say so IN TERMS rather than by omitting the block,
#: so that a missing block is always a defect and never a shrug.
NON_PHP_KEY = "php_provenance"

REQUIRED = ["php_version", "tarball_sha256", "c_file", "c_lines",
            "extract_cmd", "extract_sha256", "tier"]
TIERS = ("verbatim", "narrowed", "modelled")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def contract(spec_path):
    txt = open(spec_path, encoding="utf-8").read()
    m = _FENCE.search(txt)
    if not m:
        raise ValueError(f"{spec_path}: no ```slb-contract fence")
    return json.loads(m.group(1))


def canonical_cmd(c_file, a, b):
    """The one spelling of the read recipe. `PLAN_PHP.md` §1 and §6."""
    return (f"tar -xzOf <tarball> {TARBALL_ROOT}/{c_file} "
            f"| sed -n '{a},{b}p'")


def excerpt(tarball, c_file, a, b):
    """The bytes `sed -n 'a,bp'` would print. 1-based, inclusive."""
    member = f"{TARBALL_ROOT}/{c_file}"
    with tarfile.open(tarball, "r:gz") as tf:
        try:
            fh = tf.extractfile(member)
        except KeyError:
            raise ValueError(f"{member} is not in the tarball")
        if fh is None:
            raise ValueError(f"{member} is not a regular file")
        data = fh.read()
    # `splitlines(keepends=True)` keeps `\n` and does not invent one for a
    # final line that has none -- which is exactly what sed does.
    lines = io.BytesIO(data).readlines()
    if a < 1 or b < a:
        raise ValueError(f"bad span {a},{b}")
    if a > len(lines):
        return b""            # sed prints nothing; the hash of b"" is a real
                              # value and a wrong span lands here often
    return b"".join(lines[a - 1:b])


def manifest_map():
    if not os.path.exists(MANIFEST):
        return {}
    out = {}
    for line in open(MANIFEST, encoding="utf-8"):
        if line.startswith("#"):
            continue
        sha, _, path = line.rstrip("\n").partition("  ")
        if path:
            out[path] = sha
    return out


def check_row(pdir, tarball, use_tarball=True, show=False):
    """Returns (ok, [messages])."""
    msgs = []
    spec = os.path.join(pdir, "spec.md")
    row = os.path.basename(pdir)
    if not os.path.exists(spec):
        return False, [f"{row}: no spec.md"]
    try:
        c = contract(spec)
    except (ValueError, json.JSONDecodeError) as e:
        return False, [f"{row}: {e}"]
    prov = c.get("provenance")
    if prov is None:
        return False, [f"{row}: the slb-contract block has NO `provenance` "
                       f"object. Every php row carries one (PLAN_PHP.md §6); "
                       f"a row with no PHP source says so with "
                       f'"{NON_PHP_KEY}": false and a `why`.']

    if prov.get(NON_PHP_KEY) is False:
        if not prov.get("why"):
            return False, [f"{row}: declares {NON_PHP_KEY}=false with no "
                           f"`why`. Say what it is instead, so nobody ever "
                           f"mistakes it for a php row."]
        msgs.append(f"{row}: NOT A PHP ROW -- {NON_PHP_KEY}=false. "
                    f"why: {prov['why'][:90]}")
        return True, msgs

    missing = [k for k in REQUIRED if k not in prov]
    if missing:
        return False, [f"{row}: provenance is missing {missing}"]
    if prov["tarball_sha256"] != TARBALL_SHA256:
        return False, [f"{row}: tarball_sha256 {prov['tarball_sha256'][:12]} "
                       f"is not the pinned corpus {TARBALL_SHA256[:12]} "
                       f"(patterns-php/SOURCES.md)"]
    if prov["tier"] not in TIERS:
        return False, [f"{row}: tier {prov['tier']!r} not in {TIERS}"]
    lines = prov["c_lines"]
    if not (isinstance(lines, list) and len(lines) == 2
            and all(isinstance(x, int) for x in lines)):
        return False, [f"{row}: c_lines must be [a, b] integers, got {lines!r}"]
    a, b = lines

    # (2) the recorded command must be the canonical spelling of the fields
    want_cmd = canonical_cmd(prov["c_file"], a, b)
    if prov["extract_cmd"] != want_cmd:
        return False, [f"{row}: extract_cmd does not describe c_file/c_lines\n"
                       f"       recorded: {prov['extract_cmd']}\n"
                       f"       canonical: {want_cmd}"]

    # the manifest half -- works with no tarball at all
    mm = manifest_map()
    if mm:
        if prov["c_file"] not in mm:
            return False, [f"{row}: {prov['c_file']} is not in "
                           f"patterns-php/php-5.0.0.manifest"]
        msgs.append(f"{row}: {prov['c_file']} is in the manifest "
                    f"({mm[prov['c_file']][:12]})")
    else:
        msgs.append(f"{row}: ⚠ no manifest at {MANIFEST}; file-level check skipped")

    if not use_tarball:
        msgs.append(f"{row}: ⚠ --no-tarball: extract_sha256 was NOT verified. "
                    f"This is a PARTIAL check.")
        return True, msgs

    if not os.path.exists(tarball):
        return False, [f"{row}: tarball not found at {tarball}. Set "
                       f"PHP500_TARBALL, or use --no-tarball and say in the "
                       f"report that the excerpt hash went unchecked."]
    got_tar = hashlib.sha256(open(tarball, "rb").read()).hexdigest()
    if got_tar != TARBALL_SHA256:
        return False, [f"{row}: the tarball at {tarball} hashes "
                       f"{got_tar[:12]}, not {TARBALL_SHA256[:12]}"]
    try:
        ex = excerpt(tarball, prov["c_file"], a, b)
    except ValueError as e:
        return False, [f"{row}: {e}"]
    got = sha256_bytes(ex)
    if show:
        sys.stdout.write(ex.decode("utf-8", "replace"))
    if got != prov["extract_sha256"]:
        return False, [f"{row}: EXTRACT MISMATCH for "
                       f"{prov['c_file']}:{a}-{b}\n"
                       f"       recorded  {prov['extract_sha256']}\n"
                       f"       actual    {got}   ({len(ex)} bytes, "
                       f"{ex.count(chr(10).encode())} newlines)\n"
                       f"       run: {want_cmd} | sha256sum"]
    msgs.append(f"{row}: OK  {prov['c_file']}:{a}-{b}  {len(ex)} bytes  "
                f"sha256 {got[:16]}  tier={prov['tier']}")
    return True, msgs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row", nargs="?", help="row id or dir name, e.g. ph07")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--show", action="store_true", help="print the excerpt")
    ap.add_argument("--no-tarball", action="store_true",
                    help="manifest-only; does NOT verify extract_sha256")
    ap.add_argument("--tarball", default=DEFAULT_TARBALL)
    a = ap.parse_args()

    if a.all:
        dirs = sorted(d for d in glob.glob(os.path.join(PATTERNS, "ph*"))
                      if os.path.isdir(d))
    elif a.row:
        hits = sorted(d for d in glob.glob(os.path.join(PATTERNS, a.row + "*"))
                      if os.path.isdir(d))
        if len(hits) != 1:
            print(f"provenance.py: {a.row!r} matches {hits or 'nothing'}")
            return 1
        dirs = hits
    else:
        ap.error("give a row id or --all")

    if not dirs:
        print("provenance.py: no rows under patterns-php/")
        return 1
    bad = 0
    for d in dirs:
        ok, msgs = check_row(d, a.tarball, not a.no_tarball, a.show)
        for m in msgs:
            print(("  " if ok else "  BAD  ") + m)
        if not ok:
            bad += 1
    print(f"\n{len(dirs)} row(s) checked, {bad} FAILED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
