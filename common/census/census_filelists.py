#!/usr/bin/env python3
"""Rebuild `TASK_129`'s deduplicated corpus file lists FROM the promoted
manifests, and check the counts it published.

    python3 common/census/census_filelists.py [OUTDIR]

⚠⚠ **This is what makes the manifests worth their 506 K.** A digest-of-digests
would prove a candidate corpus is the measured one; only the per-file list can
RE-DERIVE the population -- *"distinct `.c` by sha256"* -- and it reproduces
`TASK_129`'s **php 299 / coreutils 94 / cgnu 2162** exactly. Exit 1 if any of
the three moves, so the promotion is a check and not just a copy.

Default OUTDIR is a gitignored scratch dir under `<repo>/<scratch>/`: the
lists name absolute paths into OTHER projects' trees and must not be committed.
`common/census/` is outside every digest -- see `README.md`.
"""
import os, sys
REPO = "/home/apt/repos_common/sec-ladder"
OUT = (sys.argv[1] if len(sys.argv) > 1
       else os.path.join(REPO, ".temp", "census-filelists"))
os.makedirs(OUT, exist_ok=True)
WANT = {"php": 299, "coreutils": 94, "cgnu": 2162}
rc = 0
for name in ("php", "coreutils", "cgnu"):
    root = None
    seen, rows = set(), []
    for ln in open(os.path.join(REPO, "common", "census", f"{name}.manifest"),
                   "rb").read().splitlines():
        if ln.startswith(b"# root:"):
            root = ln.split(b":", 1)[1].strip()
        if ln.startswith(b"#"):
            continue
        h, p = ln.split(b"  ", 1)
        if not p.endswith(b".c") or h in seen:
            continue
        seen.add(h)
        rows.append(b"x\t" + root + b"/" + p)
    open(os.path.join(OUT, f"{name}.files"), "wb").write(b"\n".join(rows) + b"\n")
    ok = len(rows) == WANT[name]
    rc |= 0 if ok else 1
    print(f"{name:10s} {len(rows):5d} distinct .c   (TASK_129 published "
          f"{WANT[name]}) {'ok' if ok else 'DIFFERS'}")
sys.exit(rc)
