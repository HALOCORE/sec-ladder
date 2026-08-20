#!/usr/bin/env python3
"""Attribute a per-iteration `Ir` law MNEMONIC BY MNEMONIC, inside the kernel.

`.memory/03-measurement.md` trap 3, dynamic half: **alignment padding inside a
hot loop is EXECUTED, so it lands in `Ir` and therefore inside a published law**
-- 23% of one of p06's laws turned out to be `nopl`. A coefficient looks like a
clean small integer either way, so a law must be attributed before it is named
after a mechanism.

This runs callgrind with `--dump-instr=yes`, reads the per-instruction `Ir` out
of the dump for the `kernel` symbol only, and joins it against `objdump`'s
mnemonics by address. It reports, per mnemonic, the executed count in each of two
binaries and their difference -- so a `+238.00 Ir/call` law comes out as a table
of mnemonics that sums to it.

    python3 patterns/p14-field-split/controls/attr.py \
        .temp/build/p14/c-gcc-O3-isolated .temp/build/p14/c-gcc-h-O3-isolated \
        --input small --iters 200

Divide by `--iters` for a per-call figure; the script prints both.

⚠ **Quote the DIFFERENCE, not the absolute.** A single run at one `n_iters`
carries a per-process constant that does not divide out, so the absolute
`Ir/call` here is ~74 above `results/*.json`'s kernel-exclusive column on p14's
`small`. The B-A column does not: the constant is the same in both binaries and
cancels, and the totals reproduce `results/p14-field-split.json`'s rung-to-rung
deltas EXACTLY (+238.00 gcc R1h-R1, +663.00 clang R1h-R1, +908.00 R2-R4 on
`small`), which is the check that this script measures the right thing.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402

VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
OBJDUMP = "objdump"
SCRATCH = os.path.join(REPO, ".temp", "p14", "attr")


def rewrite(path, n, out):
    f = slb.read(path)
    slb.write(out, n, f.payload[: f.declared_len])
    return out


def kernel_range(binary):
    """(start, size, name) of the symbol whose name contains `kernel`."""
    out = subprocess.run(["nm", "-S", "--defined-only", binary],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 4 and "kernel" in f[-1]:
            return int(f[0], 16), int(f[1], 16), f[-1]
    raise SystemExit(f"no kernel symbol in {binary}")


def mnemonics(binary, lo, hi):
    out = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", binary],
                         capture_output=True, text=True).stdout
    m = {}
    for line in out.splitlines():
        mm = re.match(r"\s*([0-9a-f]+):\s+([a-z][a-z0-9.]*)", line)
        if mm:
            a = int(mm.group(1), 16)
            if lo <= a < hi:
                m[a] = mm.group(2)
    return m


def per_insn_ir(binary, blob, symname):
    """{address: Ir} for every instruction inside the `kernel` FUNCTION BLOCK.

    Callgrind's `positions: instr line` means each cost line is
    `<instr> <line> <Ir>` with `instr` either absolute (`0x...`), relative
    (`+n` / `-n`) or `*` (unchanged). **The count is the LAST field, not the
    second** -- reading the second gives the LINE NUMBER, which is 0 in a build
    without `-g` and silently yields a table of zeros. That was this script's
    first defect and it failed SILENTLY, which is why the caller asserts a
    non-zero total.

    Scoping is by `fn=` block and not by object, because callgrind compresses
    `ob=` to a bare id after its first mention and a back-reference carries no
    path to match against.
    """
    os.makedirs(SCRATCH, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
        out = os.path.join(td, "cg.out")
        subprocess.run([VALGRIND, "--tool=callgrind", "--dump-instr=yes",
                        f"--callgrind-out-file={out}", binary, blob],
                       capture_output=True, text=True)
        counts, last, inside, seen, names = {}, 0, False, set(), {}
        for line in open(out):
            line = line.rstrip("\n")
            if line.startswith(("fn=", "cfn=")):
                # Callgrind NAME-COMPRESSES: `fn=(id) name` defines the id and a
                # later `fn=(id)` is a bare back-reference. The kernel's name is
                # often defined on a `cfn=` (called-function) line inside
                # `main`'s block and never repeated, so an id->name table is
                # mandatory -- without it every Rust cell profiles as empty.
                mid = re.match(r"c?fn=\((\d+)\)\s*(.*)$", line)
                if mid and mid.group(2).strip():
                    names[mid.group(1)] = mid.group(2).strip()
                if line.startswith("cfn="):
                    continue
                nm_ = (mid.group(2).strip() if mid and mid.group(2).strip()
                       else names.get(mid.group(1), "") if mid else "")
                # Callgrind DEMANGLES Rust symbols, so an exact match against
                # `nm`'s mangled name misses every Rust cell. Match on the
                # substring and record which names matched, so a second
                # kernel-ish symbol cannot be pooled in silently.
                inside = (nm_ == symname) or ("kernel" in nm_)
                if inside:
                    seen.add(nm_)
                last = 0
                continue
            if line.startswith(("fl=", "fi=", "fe=", "cfl=", "cob=",
                                "ob=", "calls=", "jump=", "jcnd=", "#")):
                continue
            if not inside:
                continue
            mm = re.match(r"^(0x[0-9a-f]+|\+\d+|-\d+|\*)\s+\S+\s+(\d+)\s*$", line)
            if not mm:
                continue
            pos, ir = mm.group(1), int(mm.group(2))
            if pos.startswith("0x"):
                addr = int(pos, 16)
            elif pos == "*":
                addr = last
            else:
                addr = last + int(pos)
            last = addr
            counts[addr] = counts.get(addr, 0) + ir
        if len(seen) > 1:
            raise SystemExit(f"attr.py: {len(seen)} symbols matched 'kernel' "
                             f"in the dump ({sorted(seen)}); refusing to pool "
                             f"them")
        return counts


def profile(binary, blob):
    lo, size, name = kernel_range(binary)
    mn = mnemonics(binary, lo, lo + size)
    ir = per_insn_ir(binary, blob, name)
    if not ir:
        raise SystemExit(f"attr.py: no per-instruction cost for {name} in "
                         f"{binary} -- the dump parser found nothing, which is "
                         f"a defect in THIS script and not a measurement")
    agg = {}
    tot = 0
    for a, c in ir.items():
        if a in mn:
            agg[mn[a]] = agg.get(mn[a], 0) + c
            tot += c
    return agg, tot, name


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--input", default="small")
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--per", type=float, default=None,
                    help="divide by this instead of --iters (e.g. total fields)")
    x = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)
    src = os.path.join(PDIR, "inputs", x.input + ".bin")
    blob = rewrite(src, x.iters, os.path.join(SCRATCH, "in.bin"))
    div = x.per if x.per else x.iters

    pa, ta, na = profile(x.a, blob)
    if not x.b:
        print(f"{os.path.basename(x.a)}  ({na})  total {ta} Ir "
              f"= {ta/div:.4f} per unit")
        for k in sorted(pa, key=lambda z: -pa[z]):
            print(f"  {k:12s} {pa[k]:10d} {pa[k]/div:10.4f}")
        return 0
    pb, tb, nb = profile(x.b, blob)
    keys = sorted(set(pa) | set(pb), key=lambda z: -(pb.get(z, 0) - pa.get(z, 0)))
    print(f"A = {os.path.basename(x.a)}   total {ta:12d}  {ta/div:10.4f}/unit")
    print(f"B = {os.path.basename(x.b)}   total {tb:12d}  {tb/div:10.4f}/unit")
    print(f"B - A = {tb - ta:+d}  =  {(tb - ta)/div:+.4f} per unit "
          f"(unit = {'--per' if x.per else 'call'}, div={div})")
    print(f"\n  {'mnemonic':12s} {'A':>10s} {'B':>10s} {'B-A':>10s} {'(B-A)/unit':>12s}")
    for k in keys:
        d = pb.get(k, 0) - pa.get(k, 0)
        if d == 0:
            continue
        print(f"  {k:12s} {pa.get(k,0):10d} {pb.get(k,0):10d} {d:+10d} "
              f"{d/div:+12.4f}")
    same = sum(min(pa.get(k, 0), pb.get(k, 0)) for k in keys)
    print(f"  (unchanged mnemonic mass: {same})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
