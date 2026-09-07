#!/usr/bin/env python3
"""Put every `common-php/` file into every php gate record's digest.

    python3 common-php/digest_bridge.py            # classify + verify
    python3 common-php/digest_bridge.py --verify   # verify only, exit 1 on drift
    python3 common-php/digest_bridge.py --regen    # rewrite the table below

============================================================================
THE PROBLEM THIS FILE EXISTS FOR
============================================================================
`harness/check.py::main` builds a gate record's `source_sha256` from a
fixed glob list. Three of its entries reach `common/`, and through the shim
(`common -> common-php`) they are the ONLY way a `common-php/` file gets into
a php record:

    glob(REPO/common/driver.*)      -- gate AND measurement
    glob(REPO/common/*.py)          -- gate only, NON-RECURSIVE
    glob(REPO/common/layout/*.py)   -- gate only

⚠⚠ NOTHING ELSE IS REACHED. `common-php/emalloc_shim.h` is a `.h` at the top
level: it matches none of the three, so it sits in NO DIGEST AT ALL. That is
exactly the failure `TASK_PHP_002` §1.4 names -- ten committed control sources
sat in no digest on the PAT side for many tasks -- and `common/census/
README.md`'s "Digest note" states the same glob property from the other side.

⚠ It cannot be fixed by editing the glob: `check.py` is hashed into all 33 PAT
gate records (`PLAN_PHP.md` §2.1).

============================================================================
WHAT THIS FILE DOES INSTEAD, AND WHAT IT DOES *NOT* BUY
============================================================================
This module is a `.py` at the top level of `common-php/`, so it IS matched by
`common/*.py` and its own sha256 lands in every php gate record. It carries
the sha256 of every `common-php/` file the globs do not reach. Therefore:

  ✅ no `common-php/` file's content can change without either (a) moving a
     hash that is in every php gate record, or (b) making `--verify` fail.
  ✅ `--verify` runs before every gate (`harness-php/gate.py`), so (b) is
     loud rather than silent.
  ✅ a DIRECTORY SYMLINK under `common-php/` is REFUSED rather than walked --
     `os.walk` does not follow one, so anything behind it would be in no
     digest while `--verify` printed `current` (TASK_PHP_003 m5). See
     `symlinked_dirs` for why refusing beats `followlinks=True`.

  ⚠ WHAT IT DOES NOT BUY, STATED PLAINLY BECAUSE A HALF-TRUE CHECK IS WORSE
     THAN NO CHECK: the bridged files do NOT appear as KEYS in
     `source_sha256`. `TASK_PHP_002` §2's test T4 asks that "every
     `common-php/` file appears in `ph00`'s gate `source_sha256`", and that
     is NOT achievable without a harness edit. A reader of a php gate record
     sees `common/digest_bridge.py`'s hash, not `common/emalloc_shim.h`'s,
     and must come here to expand it.
  ⚠ AND IT COVERS THE GATE DIGEST ONLY. `measure.py::measurement_sources`
     globs `common/driver.*` and `common/slb.py` and
     no other `.py`, so THIS FILE IS NOT IN THE MEASUREMENT DIGEST and
     neither is anything it bridges. A row whose kernel `#include`s
     `emalloc_shim.h` therefore has an allocator that its measurement record
     does not pin. ⚠ THE ROW MUST CLOSE THAT ITSELF, and there is a
     zero-machinery way: `check.py::main` globs `<row>/c/*` and
     `measure.py::measurement_sources` globs the row's own `c/*`, so a SYMLINK
         patterns-php/<row>/c/emalloc_shim.h -> ../../../common-php/emalloc_shim.h
     puts the real content under a natural key in BOTH digests
     (`glob` returns symlinks; `os.path.isfile` and `sha256_file` follow
     them -- measured, `TASK_PHP_002` T4). `.tasks-php/PROTOCOL_PHP.md` makes
     that symlink mandatory for any row that links the shim.
"""

import argparse
import glob
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

#: Files reached by `check.py`'s `common/` globs when `common -> common-php`.
#: Kept as the literal patterns rather than a hand list, so this ages with the
#: directory instead of with a comment.
GLOB_PATTERNS = ["driver.*", "*.py", os.path.join("layout", "*.py")]

# ---------------------------------------------------------------------------
# BEGIN BRIDGED TABLE -- rewritten by `--regen`. Do not hand-edit.
BRIDGED = {
    "emalloc_probe.c": "ad013ba83ff59e496cec5565263a8b4d58da6a0b8dea9c0f367ae82729d08c46",
    "emalloc_shim.c": "2e7a82b002949faf599c92fbf4da1ce8e4fec6fad55bc4d8620980bc5dfedff9",
    "emalloc_shim.h": "aa9abf48535e8df93c9398e96c044697a784d73c40d7a7ccc830b5ee308c378f",
}
# END BRIDGED TABLE
# ---------------------------------------------------------------------------


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def globbed():
    """Relative paths under `common-php/` that check.py's globs DO reach."""
    out = set()
    for pat in GLOB_PATTERNS:
        for p in glob.glob(os.path.join(HERE, pat)):
            if os.path.isfile(p):
                out.add(os.path.relpath(p, HERE))
    return out


def all_files():
    """Every file under `common-php/`, excluding derived bytecode."""
    out = set()
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".pyc"):
                continue
            out.add(os.path.relpath(os.path.join(root, f), HERE))
    return out


def symlinked_dirs():
    """Directory symlinks under `common-php/`.

    ⚠⚠ `os.walk` DOES NOT FOLLOW DIRECTORY SYMLINKS, so every file behind one
    is invisible to `all_files()` and therefore to the bridge -- it is neither
    GLOBBED nor BRIDGED, and `--verify` used to print `current` with a payload
    sitting behind it. Measured at TASK_PHP_003 m5:

        a new top-level .h            -> rc=1  NOT BRIDGED
        a file in a REAL subdirectory -> rc=1  NOT BRIDGED
        a file behind a SYMLINKED dir -> rc=0  "digest bridge: current"   <-- blind

    ⚠ `os.walk(followlinks=True)` is NOT the fix: `common-php/` is a directory
    of FILE symlinks into `common/`, and a directory symlink pointing back at
    `common/` (or at `patterns/`) would silently pull the PAT tree into the php
    bridge table and make every `--regen` a cross-programme diff. So the rule
    is REFUSE, not follow: a directory symlink under `common-php/` has no
    sanctioned use, and the bridge says so instead of being blind to it.
    Negative: `.temp/php4/m5b_bridge_test.py`.

    ⚠⚠ ONE NAME IS DIFFERENT AND THE MESSAGE USED TO SAY SOMETHING UNTRUE
    ABOUT IT (TASK_PHP_005 F-9). `GLOBBED_SUBDIRS` below is the set of directory
    names `check.py`'s own `common/` globs reach -- today exactly `layout`, from
    `glob(REPO/common/layout/*.py)`. A `common-php/layout -> ../common/layout`
    symlink is still REFUSED, and refusing is still right, but the reason is NOT
    "everything behind it is in NO digest": `check.py` follows the symlink and
    those eight `.py` files land in every php gate record as real
    `common/layout/*.py` keys. Measured by planting the link
    (`.temp/php5/08-bridge-layout.log`, re-run `.temp/php6/12-bridge-layout.log`).
    The real reason for `layout/` is narrower and still sufficient: THIS BRIDGE
    is blind to it, so anything under it that those globs do not match -- a
    `.md`, a `.c`, a nested directory -- is in no digest at all while `--verify`
    prints `current`. ⚠ Saying the wrong reason is how a CORRECT refusal gets
    argued away by the next person who checks it. `_symlinked_dir_message`
    carries the two texts.
    """
    out = []
    for root, dirs, _files in os.walk(HERE):
        for d in sorted(dirs):
            p = os.path.join(root, d)
            if os.path.islink(p):
                out.append(os.path.relpath(p, HERE))
    return out


#: Directory components of `GLOB_PATTERNS` -- the names `check.py` DOES reach
#: behind. Derived, not hand-listed, so it ages with `GLOB_PATTERNS`.
GLOBBED_SUBDIRS = {os.path.dirname(p) for p in GLOB_PATTERNS if os.path.dirname(p)}


def _symlinked_dir_message(rel):
    """The refusal text for one symlinked directory. See `symlinked_dirs`."""
    if os.path.basename(rel.rstrip("/")) in GLOBBED_SUBDIRS:
        pats = sorted(p for p in GLOB_PATTERNS
                      if os.path.dirname(p) == os.path.basename(rel))
        return (f"SYMLINKED DIRECTORY: {rel}/ -- REFUSED, but not for the usual "
                f"reason. check.py globs {pats} and FOLLOWS the link, so the "
                f"files it matches WOULD be real `common/{rel}/…` keys in every "
                f"php gate record. What is blind is THIS bridge: `os.walk` does "
                f"not follow the link, so anything under {rel}/ that those "
                f"globs do NOT match is in no digest and --verify would print "
                f"`current` over it. Use per-file symlinks "
                f"(`ln -s ../../common/{rel}/x.py common-php/{rel}__x.py` is "
                f"NOT equivalent -- the key must stay `{rel}/x.py`, so make "
                f"{rel}/ a REAL directory of per-file links) and re-run "
                f"--regen. (TASK_PHP_003 m5; message corrected TASK_PHP_006 "
                f"from TASK_PHP_005 F-9.)")
    return (f"SYMLINKED DIRECTORY: {rel}/ -- `os.walk` does not follow it, so "
            f"everything behind it is in NO digest and this check would "
            f"otherwise print `current`. Replace it with a real directory (its "
            f"files then bridge normally) or with per-file symlinks. See "
            f"`symlinked_dirs`. (TASK_PHP_003 m5.)")


def classify():
    g = globbed()
    return sorted(g), sorted(all_files() - g)


def verify(quiet=False):
    """Returns a list of problems; empty means the bridge is current."""
    _g, bridged = classify()
    problems = []
    for rel in symlinked_dirs():
        problems.append(_symlinked_dir_message(rel))
    for rel in bridged:
        want = BRIDGED.get(rel)
        got = sha256_file(os.path.join(HERE, rel))
        if want is None:
            problems.append(f"NOT BRIDGED: {rel} is in no digest at all "
                            f"(sha256 {got[:12]}). Run --regen.")
        elif want != got:
            problems.append(f"MOVED: {rel} {want[:12]} -> {got[:12]}. "
                            f"Run --regen, and say so in the row's NOTES.md.")
    for rel in sorted(set(BRIDGED) - set(bridged)):
        if rel in _g:
            problems.append(f"NOW GLOBBED: {rel} is reached by check.py's own "
                            f"globs and must leave the table. Run --regen.")
        else:
            problems.append(f"GONE: {rel} is in the table and not on disk. "
                            f"Run --regen.")
    if not quiet:
        for rel in _g:
            print(f"  GLOBBED  {rel:24s} -> key `common/{rel}` in every php "
                  f"gate record")
        for rel in bridged:
            mark = "ok " if rel in BRIDGED and BRIDGED[rel] == \
                sha256_file(os.path.join(HERE, rel)) else "!! "
            print(f"  BRIDGED  {rel:24s} {mark}{BRIDGED.get(rel, '<absent>')[:16]}")
    return problems


def regen():
    _g, bridged = classify()
    table = {rel: sha256_file(os.path.join(HERE, rel)) for rel in bridged}
    src = open(__file__, encoding="utf-8").read()
    lines = ["BRIDGED = {"]
    for rel in sorted(table):
        lines.append(f'    "{rel}": "{table[rel]}",')
    lines.append("}")
    new = "\n".join(lines)
    a = src.index("# BEGIN BRIDGED TABLE")
    a = src.index("BRIDGED = {", a)
    b = src.index("# END BRIDGED TABLE")
    b = src.rindex("}\n", a, b) + 2
    open(__file__, "w", encoding="utf-8").write(src[:a] + new + "\n" + src[b:])
    print(f"regenerated: {len(table)} bridged file(s)")
    for rel in sorted(table):
        print(f"  {table[rel][:16]}  {rel}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--regen", action="store_true")
    a = ap.parse_args()
    if a.regen:
        regen()
        return 0
    problems = verify(quiet=a.verify)
    for p in problems:
        print(f"  BAD  {p}")
    if problems:
        print(f"digest bridge: {len(problems)} problem(s)")
        return 1
    print("digest bridge: current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
