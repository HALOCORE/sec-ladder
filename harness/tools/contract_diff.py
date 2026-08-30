#!/usr/bin/env python3
"""What moved inside a pattern's HASHED `slb-contract` block, key by key.

    python3 harness/tools/contract_diff.py p32              # vs HEAD
    python3 harness/tools/contract_diff.py p32 <git-ref>    # vs any ref
    python3 harness/tools/contract_diff.py --all            # every pattern

`PROTOCOL.md` definition-of-done item 6 asks a task that moves a
`contract_sha256` to say WHAT moved. Until now each task answered that its own
way, and the answers were not reproducible: `TASK_144`'s check needed the output
of a generator living in a gitignored `.temp/` directory, and `TASK_145_REPORT`
§11 recorded, correctly, that the reviewer **could not reproduce the
disclosure** -- *"a real gap in the evidence chain"*.

This needs nothing but `git`. A committed pattern's pre-edit `spec.md` is
`git show <ref>:patterns/<pattern>/spec.md`, so the comparison is always
available to anyone with the repository and never depends on an artefact that
was deleted.

⚠ **This file lives in `harness/tools/`, which is OUTSIDE the gate digest**
(`check.py`'s `source_sha` globs `harness/*.py`, non-recursively), so adding or
editing it costs no re-gate and no re-measure. **Nothing here may be imported by
`check.py`, `measure.py` or `build.py`** or it silently joins that digest.

Written from `.temp/t147/contract_diff.py` (`TASK_147`), generalised from one
hardcoded pattern to any.
"""
import argparse
import difflib
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FENCE_RE = re.compile(r"```slb-contract\s*\n(.*?)```", re.S)


def pattern_dir(pid):
    """`p32` or `p32-free-list-pool` -> the repo-relative pattern directory."""
    hits = sorted(glob.glob(os.path.join(REPO, "patterns", f"{pid}*")))
    hits = [h for h in hits if os.path.isdir(h)]
    if len(hits) != 1:
        raise SystemExit(f"contract_diff.py: {pid!r} matches {len(hits)} "
                         f"pattern directories: {[os.path.basename(h) for h in hits]}")
    return os.path.relpath(hits[0], REPO)


def block(text):
    """The raw contract text, byte for byte as `check.py::read_contract` sees it."""
    m = FENCE_RE.search(text)
    if not m:
        raise SystemExit("contract_diff.py: no ```slb-contract block")
    return m.group(1)


def sha_of_block(text):
    """EXACTLY `harness/check.py::main`'s `contract_sha`: sha256 of
    `read_contract`'s `m.group(1)`. Spelled with the same regex so the number
    printed here is the number the gate prints, not a near-miss."""
    return hashlib.sha256(block(text).encode()).hexdigest()


def spanshow(old, new, label, indent):
    """For a long string value, the minimal changed span rather than the whole."""
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        print(f"{indent}  [{label}] {tag} at {i1}")
        if i2 > i1:
            print(f"{indent}    - {old[i1:i2][:900]!r}")
        if j2 > j1:
            print(f"{indent}    + {new[j1:j2][:900]!r}")


def diff_one(pid, ref, quiet=False):
    """Returns the list of moved key paths, or None if the file is not in `ref`."""
    rel = os.path.join(pattern_dir(pid), "spec.md")
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=REPO,
                       capture_output=True, text=True)
    if r.returncode != 0:
        if not quiet:
            print(f"{rel}: not present at {ref} (a pattern added since?)")
        return None
    old_txt, new_txt = r.stdout, open(os.path.join(REPO, rel)).read()
    old_sha, new_sha = sha_of_block(old_txt), sha_of_block(new_txt)
    o, n = json.loads(block(old_txt)), json.loads(block(new_txt))
    moved = []

    def walk(o, n, path, depth):
        for k in sorted(set(o) | set(n)):
            here = f"{path}.{k}" if path else k
            pad = "  " * depth
            if o.get(k) == n.get(k):
                if not quiet:
                    print(f"  {pad}{here:28s} IDENTICAL")
                continue
            moved.append(here)
            print(f"  {pad}{here:28s} ⚠ MOVED")
            ov, nv = o.get(k), n.get(k)
            if isinstance(ov, dict) and isinstance(nv, dict):
                walk(ov, nv, here, depth + 1)
            elif isinstance(ov, str) and isinstance(nv, str):
                spanshow(ov, nv, here, pad)
            else:
                print(f"  {pad}    - {json.dumps(ov)[:900]}")
                print(f"  {pad}    + {json.dumps(nv)[:900]}")

    if quiet and old_sha == new_sha:
        return []
    print(f"== {rel}")
    print(f"   block sha256  {ref}: {old_sha}")
    print(f"   block sha256  tree: {new_sha}")
    if old_sha == new_sha:
        print("   UNCHANGED")
        return []
    walk(o, n, "", 0)
    print(f"   {len(moved)} path(s) moved: {moved}")
    return moved


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern", nargs="?", help="pattern id, e.g. p32")
    ap.add_argument("ref", nargs="?", default="HEAD", help="git ref (default HEAD)")
    ap.add_argument("--all", action="store_true",
                    help="every pattern; prints only those whose block moved")
    a = ap.parse_args()

    if a.all:
        pids = [os.path.basename(d) for d in
                sorted(glob.glob(os.path.join(REPO, "patterns", "p*")))
                if os.path.isdir(d)]
        moved = [p for p in pids if diff_one(p, a.ref, quiet=True)]
        print(f"\n{len(moved)} of {len(pids)} pattern(s) have a moved contract "
              f"block against {a.ref}: {moved or 'none'}")
        return 1 if moved else 0
    if not a.pattern:
        ap.error("give a pattern id, or --all")
    return 0 if diff_one(a.pattern, a.ref) == [] else 1


if __name__ == "__main__":
    sys.exit(main())
