#!/usr/bin/env python3
"""The classifier-free pointer-cursor count behind RECAP finding 45.

    python3 common/census/ptr_cursor_regex.py --ladder
    python3 common/census/ptr_cursor_regex.py --must-fire
    python3 common/census/ptr_cursor_regex.py --files <list.files> [...]
    python3 common/census/ptr_cursor_regex.py <path> [...]

## Why this file exists

RECAP finding 45 published *"`845` over PHP, `0` over the kernels, both numbers
exact"*. ⚠⚠ **Neither number could be re-derived**: the regex was never written
down. `TASK_131`'s reviewer reconstructed one and got **854 / 0** and recorded
in that task's notes that the working spelling was *"variant D"* -- but the
spelling that actually shipped in its scratch is an EARLIER variant printing
**952 / 2 / 38** (`v0` below is exactly it). So the reconstruction was published
and the instrument that produced it was not, which is the same defect one level
up. Dated record: `.tasks/TASK_131_REPORT.md`.

⚠ **The load-bearing number is the `0`, not the PHP count.** The claim is that
no shipped C rung walks with a pointer cursor; the PHP figure is only a scale.
So this script's primary arm is `--ladder`, which reads `patterns/*/c/*.c` and
`*.h` **out of the committed tree** and needs no corpus at all.

## The regex, and the guard that is the whole difference

Three alternations, all on raw bytes:

    \\*\\s*IDENT\\s*\\+\\+        *p++
    \\*\\s*\\+\\+\\s*IDENT        *++p
    \\*\\s*\\(\\s*IDENT\\s*[-+]   *(p + e) / *(p - e)

⚠⚠ **The third alternation needs a UNARY GUARD or it counts MULTIPLICATION.**
Without it, `8 * (n + m)` matches, and `TASK_131`'s first attempt scored the
ladder at **2** -- both hits being that expression in `p46` -- i.e. it
reproduced the manager's own known-defective probe rather than checking it. The
guard is that the byte before the `*` must not end an operand: not
`[A-Za-z0-9_)\\]]`, and not a second `*` (so `**p` and `a ** b` are handled the
same way).

⚠ It is a REGEX, not a parser: it counts occurrences in comments and string
literals too, and it cannot see `p[i]` where `p` is a pointer. It exists to be
CLASSIFIER-INDEPENDENT -- a second instrument for `census.py`'s `ptr_offset`
label, not a better one.

## Placement

`common/census/` is **outside** every digest: `check.py`'s `srcs` globs
`common/*.py` and `common/layout/*.py` NON-RECURSIVELY, and `measure.py`'s
`measurement_sources` does not reach `common/` at all. ⚠ **Nothing in this
directory may be imported by `check.py`, `measure.py` or `build.py`**, or it
silently rejoins the digest and a comment fix here starts costing a sweep.
"""

import argparse
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IDENT = rb"[A-Za-z_]\w*"

#: The three cursor spellings, UNGUARDED -- `TASK_131`'s shipped
#: reconstruction is exactly this (`.tasks/TASK_131_REPORT.md`).
_ALTS = (
    rb"\*\s*" + IDENT + rb"\s*\+\+",              # *p++
    rb"\*\s*\+\+\s*" + IDENT,                     # *++p
    rb"\*\s*\(\s*" + IDENT + rb"\s*[-+]",         # *(p + e)
)
PAT = re.compile(rb"|".join(_ALTS))

#: ⚠⚠ THE GUARD IS THE WHOLE INSTRUMENT, AND IT IS NOT ONE CHOICE BUT FOUR.
#: A `*` is a dereference only if what precedes it does not END AN OPERAND.
#: `v0` no guard at all; `v1` looks only at the byte IMMEDIATELY before the
#: `*`, which MISSES `8 * (n + m)` because that byte is a SPACE; `v2` skips
#: whitespace backwards, which catches it; `v3` additionally rejects a
#: preceding `)`, which also throws away the genuine cast-then-deref
#: `(u8) *str++`. **No spelling is right**, and the numbers differ by 4% over
#: PHP and by 2 sites over the ladder, which is the point: the figure a
#: publication quotes is a property of the guard, so the guard has to ship.
GUARDS = {
    "v0": None,
    "v1": rb"[A-Za-z0-9_)\]*]",
    "v2": rb"[A-Za-z0-9_\]*]",
    "v3": rb"[A-Za-z0-9_)\]*]",
}
_SKIP_WS = {"v0": False, "v1": False, "v2": True, "v3": True}


def _accept(b, i, variant):
    """Is the `*` at `b[i]` a dereference under `variant`?"""
    rej = GUARDS[variant]
    if rej is None:
        return True
    j = i - 1
    if _SKIP_WS[variant]:
        while j >= 0 and b[j:j+1].isspace():
            j -= 1
    if j < 0:
        return True
    return not re.match(rej, b[j:j+1])


def count(paths, show=0, variant="v2"):
    n = shown = 0
    for p in paths:
        try:
            b = open(p, "rb").read()
        except OSError as e:
            print(f"  !! {p}: {e}", file=sys.stderr)
            continue
        for m in PAT.finditer(b):
            if not _accept(b, m.start(), variant):
                continue
            n += 1
            if shown < show:
                a = max(0, m.start() - 30)
                print(f"    {p}:{b[:m.start()].count(chr(10).encode())+1} "
                      f"...{b[a:m.end()+20]!r}")
                shown += 1
    return n


def ladder_paths():
    return sorted(glob.glob(os.path.join(REPO, "patterns", "p*", "c", "*.c"))
                  + glob.glob(os.path.join(REPO, "patterns", "p*", "c", "*.h")))


def read_files_list(lf):
    out = []
    for ln in open(lf, errors="surrogateescape"):
        ln = ln.rstrip("\n")
        if ln.strip():
            out.append(ln.split("\t")[-1])
    return out


def kernels_only():
    return sorted(glob.glob(os.path.join(REPO, "patterns", "p*", "c", "kernel.c")))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--ladder", action="store_true",
                    help="the 26 patterns/*/c/kernel.c AND all patterns/*/c/*.{c,h}")
    ap.add_argument("--files", action="append", default=[],
                    help="a TASK_129-style `<label>\\t<path>` list")
    ap.add_argument("--must-fire", action="store_true",
                    help="the planted pointer-cursor kernel; MUST be 2 in every variant")
    ap.add_argument("--variant", choices=sorted(GUARDS), default=None,
                    help="one guard only; default prints all four")
    ap.add_argument("--show", type=int, default=0)
    a = ap.parse_args()
    variants = [a.variant] if a.variant else sorted(GUARDS)
    sets = []
    rc = 0
    if a.must_fire:
        sets.append(("MUST-FIRE planted", [os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "planted_p01_ptr_kernel.c")]))
    if a.ladder:
        sets.append(("ladder kernel.c", kernels_only()))
        sets.append(("ladder c/*.{c,h}", ladder_paths()))
    for lf in a.files:
        sets.append((os.path.basename(lf), read_files_list(lf)))
    if a.paths:
        sets.append(("(argv)", a.paths))
    if not sets:
        ap.error("nothing to count; try --ladder --must-fire")
    w = max(len(n) for n, _ in sets)
    print(f"{'corpus':{w}s} {'files':>6s} " + " ".join(f"{v:>7s}" for v in variants))
    print("-" * (w + 8 + 8 * len(variants)))
    for name, paths in sets:
        row = [count(paths, show=a.show if name.startswith("MUST") or a.show else 0,
                     variant=v) for v in variants]
        print(f"{name:{w}s} {len(paths):6d} " + " ".join(f"{n:7d}" for n in row))
        if name.startswith("MUST") and any(n != 2 for n in row):
            print("  MUST-FIRE ARM DID NOT FIRE AS EXPECTED (want 2 in every variant)")
            rc = 1
    print()
    print("v0 no guard  v1 byte-adjacent  v2 whitespace-skipping  "
          "v3 v2 + reject `)`")
    return rc


if __name__ == "__main__":
    sys.exit(main())
