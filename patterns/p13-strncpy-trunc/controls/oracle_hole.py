#!/usr/bin/env python3
"""p13 control: THE ORACLE HOLE THE NARROW FOLD LEFT, and its repair, measured.

**This control used to demonstrate a hole and now demonstrates its closure, and
the difference is one line of every rung.** Until TASK_046 ../spec.md's fold
took `d` (where the consumer stopped) and `dst[0]`, and nothing else, so the
CONTENTS of `dst[1 .. d]` were observable only through "is this byte zero?" and
a rung that copied the wrong bytes there -- as long as none of them was zero --
printed the identical checksum on **all nine shipped inputs**. Since TASK_046
the fold is FULL-EXTENT (`d`, then every one of the DST_CAP destination bytes),
which is what `.memory/02-bench-rules.md` has required since TASK_004_REVIEW,
and the same substitution is caught on every input where it changes a byte.

The narrow fold was not chosen to hide anything -- TASK_043 specified it, on the
worry that a full fold would break the `exact` / `truncate` / `truncate-alt`
triple. **That worry was measured and is unfounded**: the three still print ONE
checksum, because `n = min(slen, DST_CAP)` caps the copy and the termination
store overwrites the last slot, so `dst` is byte-identical across all three.
The harm p13 models -- bytes past the truncation point stop influencing
anything -- does not need a weak fold to be visible; it needs only that `dst`
be the same, and it is.

    python3 patterns/p13-strncpy-trunc/controls/oracle_hole.py
    python3 patterns/p13-strncpy-trunc/controls/oracle_hole.py --verus

Builds `safe_naive.rs` with one substitution -- every copied byte except
`dst[0]` replaced by `0xFF` -- and runs it against every shipped input. The
`dst[0]` exemption is deliberate and is what made the mutant invisible before:
it keeps the one byte the narrow fold could see.

WHAT CATCHES IT NOW, in order of strength:
  * the FULL-EXTENT fold, i.e. `harness/check.py` stage 2 (checksum agreement)
    and stage 5d (the `ensures` re-derived on sampled calls) -- this is the
    repair, and the row-by-row table below is the evidence;
  * verus.rs's `ensures` is `r == strncpy_fold(...)` where `copy_into` is a
    byte-at-a-time transcription of the source bytes, so R5 with this
    substitution does not verify -- run with `--verus` to see it. That was
    already true under the narrow fold and is why ../NOTES.md 6a could say the
    proof was strictly stronger than the oracle. It no longer is, on this
    mutant, and saying so is the honest form of the result.

A row that still agrees is a row where the substitution changes nothing --
every string shorter than 2 bytes, and `adversarial-empty` / `adversarial-
stride3` where nothing is copied at all. Those are reported as `n/a`, not as
holes; the summary counts only the rows where the mutant actually differs.
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
    print(f"  {'input':30s} {'shipped R2':>22s} {'0xFF copy':>22s}  caught?")
    same = 0
    for n in names:
        arg = os.path.join(indir, n)
        s1 = sh([ship, arg])[1].strip()
        s2 = sh([binary, arg])[1].strip()
        ok = s1 == s2
        same += ok
        print(f"  {n:30s} {s1:>22s} {s2:>22s}  {'no' if ok else 'CAUGHT'}")
    caught = len(names) - same
    print(f"\n  caught on {caught}/{len(names)} shipped inputs "
          f"(identical on {same}).")
    if same == len(names):
        print("  ==> THE CHECKSUM ORACLE CANNOT SEE THIS. `harness/check.py` "
              "stage 2 and\n      stage 5d both pass a rung that copies the "
              "wrong bytes into dst[1..d].")
    else:
        print("  ==> THE FULL-EXTENT FOLD CATCHES IT. Under the narrow fold "
              "TASK_043 specified,\n      this mutant was identical on "
              "9/9 and both stage 2 and stage 5d passed it.")
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
