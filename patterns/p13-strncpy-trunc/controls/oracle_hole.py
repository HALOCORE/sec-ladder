#!/usr/bin/env python3
"""p13 control: what the checksum oracle does NOT discriminate, measured.

../spec.md's fold takes `d` (where the consumer stopped) and `dst[0]`, and
nothing else. So the CONTENTS of `dst[1 .. d]` are observable only through "is
this byte zero?", and a rung that copied the wrong bytes there -- as long as
none of them is zero -- prints the identical checksum.

That is not an oversight, it is the harm p13 exists to model: bytes past the
truncation point stop influencing anything, and the fold has to be weak enough
for the `exact` / `truncate` / `truncate-alt` triple to collapse onto one
answer. But a hole in the oracle still has to be written down and demonstrated,
not described -- `.memory/02-bench-rules.md`'s threat model is honest mistake,
and an honest mistake in a copy loop is exactly what this misses.

    python3 patterns/p13-strncpy-trunc/controls/oracle_hole.py

Builds `safe_naive.rs` with one substitution -- every copied byte except
`dst[0]` replaced by `0xFF` -- and runs it against every shipped input.

WHAT DOES catch it, and the reason the pattern is still sound:
  * ../spec.md's `idiom.required` pins the copy's spelling per rung;
  * verus.rs's `ensures` is `r == strncpy_fold(...)` where `copy_into` is a
    byte-at-a-time transcription of the source bytes, so R5 with this
    substitution does not verify -- run with `--verus` to see it;
  * `harness/check.py` stage 5d re-derives the `ensures` from the model on 128
    sampled calls, which is the same oracle and therefore has the same hole.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SCRATCH = os.path.join(REPO, ".temp", "p13", "oracle")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VERUS_RUN = os.path.join(REPO, "verus_run.py")

SUB_NAIVE = ("            dst[i] = buf[off + p + i];\n",
             "            dst[i] = if i == 0 { buf[off + p + i] } else { 0xFF };\n")
SUB_VERUS = ("            let b: u8 = buf_get_unchecked(buf, off + p + i);\n",
             "            let b: u8 = if i == 0 { buf_get_unchecked(buf, off + p + i) } else { 0xFFu8 };\n")


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verus", action="store_true",
                    help="also run the same substitution through Verus")
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)

    base = open(os.path.join(PDIR, "safe_naive.rs")).read()
    old, new = SUB_NAIVE
    if base.count(old) != 1:
        raise SystemExit(f"oracle_hole.py: substitution matched "
                         f"{base.count(old)} times, expected 1")
    path = os.path.join(SCRATCH, "ff_copy.rs")
    with open(path, "w") as f:
        f.write(base.replace(old, new))
    binary = os.path.join(SCRATCH, "ff_copy")
    rc, o, e = sh([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                   "-C", "opt-level=3", "-C", "debug-assertions=off",
                   "--cfg", "slb_isolated", path, "-o", binary])
    if rc != 0:
        print((o + e)[:2000])
        raise SystemExit("build failed")

    ship = os.path.join(REPO, ".temp", "build", "p13", "safe_naive-O3-isolated")
    indir = os.path.join(PDIR, "inputs")
    names = sorted(f for f in os.listdir(indir)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    print(f"  {'input':30s} {'shipped R2':>22s} {'0xFF copy':>22s}  same?")
    same = 0
    for n in names:
        arg = os.path.join(indir, n)
        s1 = sh([ship, arg])[1].strip()
        s2 = sh([binary, arg])[1].strip()
        ok = s1 == s2
        same += ok
        print(f"  {n:30s} {s1:>22s} {s2:>22s}  {'YES' if ok else 'no'}")
    print(f"\n  identical on {same}/{len(names)} shipped inputs.")
    if same == len(names):
        print("  ==> THE CHECKSUM ORACLE CANNOT SEE THIS. `harness/check.py` "
              "stage 2 and\n      stage 5d both pass a rung that copies the "
              "wrong bytes into dst[1..d].")
    os.remove(binary)

    if a.verus:
        vbase = open(os.path.join(PDIR, "verus.rs")).read()
        vold, vnew = SUB_VERUS
        if vbase.count(vold) != 1:
            raise SystemExit("oracle_hole.py: verus substitution did not match once")
        vpath = os.path.join(SCRATCH, "ff_copy_verus.rs")
        with open(vpath, "w") as f:
            f.write(vbase.replace(vold, vnew))
        r = subprocess.run([sys.executable, VERUS_RUN, vpath],
                           capture_output=True, text=True, cwd=REPO, timeout=1800)
        out = r.stdout + r.stderr
        m = re.search(r"(\d+) verified, (\d+) errors", out)
        print(f"\n  verus.rs with the same substitution: {m.group(0) if m else out[-300:]}")
        for l in out.splitlines():
            if l.startswith("error") or "not satisfied" in l:
                print(f"    | {l.strip()[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
