#!/usr/bin/env python3
"""WHAT DOES p36's `identity` PIN ACTUALLY COVER? Measured, not argued.

Built at TASK_073 for TASK_072_REVIEW M5. `spec.md` pins
`unsafe == verus, O0 norel / O3 norel`, and ../NOTES.md 5 and 5a used to say
*"the `identity` pin caught it"* of the vtable-slot finding without saying what
"it" ranges over. The scope matters on this pattern more than on any other,
because **p36's dispatch mechanism is DATA**: `TABLE` and the eight vtables live
in `.data.rel.ro`, outside the kernel symbol, and no digest the gate computes
over the kernel function's bytes can see them.

The probe: take `unsafe.rs`, REVERSE the eight entries of `TABLE`, change
nothing else. The program then computes a different answer with the same
instructions.

    python3 patterns/p36-vtable-dispatch/controls/identity_probe.py

Expected, and the point of the file: `n_fn`, `fn_bytes`, `md5_fn` (the `exact`
level) and `md5_fn_norel` (the `norel` level p36 pins) are ALL equal, and the
checksum differs. So on p36 the `identity` pin's coverage of the thing the
pattern is about is **zero at every level**, and what catches a permuted table
is the gate's stage-2 checksum comparison against `model.py`. ✅ The gate is not
unsound -- it fails immediately -- but "the identity pin caught it" needs the
clause "of the kernel function's bytes".
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.environ.get("SLB_P36_SCRATCH", os.path.join(REPO, ".temp", "p36"))
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
RUST_FLAGS = ["-C", "opt-level=3", "-C", "debug-assertions=off",
              "-C", "codegen-units=1", "--cfg", "slb_isolated"]

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402

SHIPPED_TABLE = """const TABLE: [&'static dyn Op; NOPS] = [
    &OpTag::<0>,
    &OpTag::<1>,
    &OpTag::<2>,
    &OpTag::<3>,
    &OpTag::<4>,
    &OpTag::<5>,
    &OpTag::<6>,
    &OpTag::<7>,
];"""

REVERSED_TABLE = """const TABLE: [&'static dyn Op; NOPS] = [
    &OpTag::<7>,
    &OpTag::<6>,
    &OpTag::<5>,
    &OpTag::<4>,
    &OpTag::<3>,
    &OpTag::<2>,
    &OpTag::<1>,
    &OpTag::<0>,
];"""


def build(name, text):
    d = os.path.join(OUT, "identity")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(d, name + ".rs")
    open(src, "w").write(text)
    out = os.path.join(d, name)
    r = subprocess.run([RUSTC, *RUST_FLAGS, src, "-o", out],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{name}: build failed\n{r.stdout}{r.stderr}")
    return out


def main():
    ship = open(os.path.join(PDIR, "unsafe.rs")).read()
    if ship.count(SHIPPED_TABLE) != 1:
        raise SystemExit("identity_probe.py: unsafe.rs's TABLE moved; fix this "
                         "probe rather than the rung.")
    rows = []
    for name, text in (("A_ship", ship),
                       ("B_permuted", ship.replace(SHIPPED_TABLE, REVERSED_TABLE))):
        b = build(name, text)
        k = asm.try_kernel(b)
        blob = os.path.join(PDIR, "inputs", "small.bin")
        ck = subprocess.run([b, blob], capture_output=True, text=True).stdout.strip()
        rows.append((name, k, ck))
        print(f"{name:12s} n_fn={k.n_fn} nopad={k.n_fn_nopad} bytes={len(k.fn_bytes)}")
        print(f"             md5_fn      (level `exact`) = {k.md5_fn}")
        print(f"             md5_fn_norel(level `norel`) = {k.md5_fn_norel}")
        print(f"             small.bin checksum          = {ck}")
    (_, a, ca), (_, b, cb) = rows
    print(f"\nA vs B: n_fn eq={a.n_fn == b.n_fn}  bytes eq="
          f"{len(a.fn_bytes) == len(b.fn_bytes)}  "
          f"md5_fn(EXACT) eq={a.md5_fn == b.md5_fn}  "
          f"md5_fn_norel(NOREL) eq={a.md5_fn_norel == b.md5_fn_norel}  "
          f"checksum eq={ca == cb}")
    if a.md5_fn == b.md5_fn and ca != cb:
        print("=> the `identity` pin is BLIND to p36's dispatch table at EVERY "
              "level; the gate's stage-2 checksum is what carries it.")
        return 0
    print("=> UNEXPECTED: the pin saw the table. Re-read ../NOTES.md 5a.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
