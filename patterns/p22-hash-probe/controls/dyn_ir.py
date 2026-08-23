#!/usr/bin/env python3
"""Per-INSTRUCTION *dynamic* Ir inside one symbol, for two builds, and the diff.

⚠ **This exists because a STATIC diff cannot settle a per-key cost.**
`../NOTES.md` 4e used to explain clang's +5.00/key as *"presumably by
restructuring the key loop"*; TASK_070_REVIEW F7 refuted the presumption from
`harness/asm.py diff`, and re-deriving it here showed the static diff is not
enough on its own either: `asm.py stat` puts `c-gcc` at 87 -> 89 instructions,
**+2**, while the measured marginal is **+1.00 per key**. A static count says
what is in the extent; it does not say what ran. This does.

    python3 patterns/p22-hash-probe/controls/dyn_ir.py \\
        .temp/build/p22/c-gcc-O3-isolated .temp/build/p22/c-gcc-h-O3-isolated \\
        patterns/p22-hash-probe/inputs/small.bin 200

The cells come from `harness/build.py` (`python3 harness/build.py p22`), so the
flags are the gate's and not this file's -- the point is to compare the SHIPPED
cells, and a second set of build flags here would be a second experiment.

Output is one line per mnemonic whose dynamic count differs, in units of
per-call (divide by the window's key count for per-key). The whole-symbol delta
divided by `iters` reproduces the kernel-exclusive marginal in `../NOTES.md` 4e.

⚠ **Every run is under an explicit `timeout=`** (`.memory/00-environment.md`);
nothing here is backgrounded.
"""

import argparse
import collections
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p22", "controls")
assert OUT.endswith(os.path.join("p22", "controls")), OUT
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")


def probe_input(blob, iters):
    """The blob with its `n_iters` header word rewritten -- `.memory/03`'s
    marginal convention, the same trick `gen_controls.py` uses."""
    b = open(blob, "rb").read()
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"dynir-{iters}-" + os.path.basename(blob))
    open(p, "wb").write(struct.pack("<Q", iters) + b[8:])
    return p


def callgrind(exe, arg, timeout=1800):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "dynir.cg." + os.path.basename(exe))
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--dump-instr=yes",
                        f"--callgrind-out-file={out}", exe, arg],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise SystemExit(f"dyn_ir.py: callgrind failed on {exe}:\n"
                         f"{r.stderr[-600:]}")
    return out


def parse(path, sym):
    """address -> Ir, for the named fn.

    Two callgrind encodings have to be handled or the answer is silently zero:
    POSITION COMPRESSION (`+n`/`-n`/`*` relative to the previous instruction)
    and NAME COMPRESSION (`fn=(N) name` defines the id, a later bare `fn=(N)`
    refers back to it -- and the defining occurrence may be a `cfn=`)."""
    counts, names = collections.Counter(), {}
    cur, last = None, 0
    for line in open(path):
        line = line.rstrip("\n")
        m = re.match(r"^(c?fn)=\((\d+)\)\s*(.*)$", line)
        if m:
            kind, num, nm = m.group(1), m.group(2), m.group(3)
            if nm:
                names[num] = nm
            if kind == "fn":
                cur, last = names.get(num, nm), 0
            continue
        if line.startswith(("fn=", "cfn=", "cfi=", "fi=", "fe=", "fl=", "ob=",
                            "calls=")):
            if line.startswith("fn="):
                cur, last = line[3:], 0
            continue
        m = re.match(r"^(0x[0-9a-f]+|\+\d+|-\d+|\*)\s+\S+\s+(\d+)\s*$", line)
        if not m:
            continue
        pos, ir = m.group(1), int(m.group(2))
        last = int(pos, 16) if pos.startswith("0x") else \
            (last if pos == "*" else last + int(pos))
        if cur == sym:
            counts[last] += ir
    return counts


def disas(exe, sym):
    r = subprocess.run(["objdump", "-d", "--no-show-raw-insn", exe],
                       capture_output=True, text=True)
    keep, out = False, {}
    for line in r.stdout.splitlines():
        m = re.match(r"^([0-9a-f]+) <(.+)>:$", line)
        if m:
            keep = m.group(2) == sym
            continue
        if not keep:
            continue
        m = re.match(r"^\s*([0-9a-f]+):\s+(.*)$", line)
        if m:
            out[int(m.group(1), 16)] = m.group(2).strip()
    return out


def profile(exe, blob, iters, sym):
    ctr = parse(callgrind(exe, probe_input(blob, iters)), sym)
    if not ctr:
        raise SystemExit(f"dyn_ir.py: no dynamic counts for `{sym}` in {exe} "
                         f"-- wrong symbol, or the cell inlined it away")
    ins = disas(exe, sym)
    per = collections.Counter()
    for a, n in ctr.items():
        per[ins.get(a, "?").split()[0] if a in ins else "?"] += n
    return sum(ctr.values()), per


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exe_a")
    ap.add_argument("exe_b")
    ap.add_argument("blob")
    ap.add_argument("iters", type=int)
    ap.add_argument("--sym", default="kernel")
    ap.add_argument("--keys", type=int, default=0,
                    help="key bytes walked per call; adds a per-key column")
    a = ap.parse_args()
    ta, pa = profile(a.exe_a, a.blob, a.iters, a.sym)
    tb, pb = profile(a.exe_b, a.blob, a.iters, a.sym)
    print(f"{os.path.basename(a.exe_a):26s} {a.sym} Ir = {ta}")
    print(f"{os.path.basename(a.exe_b):26s} {a.sym} Ir = {tb}")
    print(f"delta = {tb - ta}   per call = {(tb - ta) / a.iters:.4f}" +
          (f"   per key = {(tb - ta) / a.iters / a.keys:.4f}" if a.keys else ""))
    print("\nby mnemonic, only where the DYNAMIC count differs:")
    for mn in sorted(set(pa) | set(pb)):
        if pa[mn] != pb[mn]:
            d = (pb[mn] - pa[mn]) / a.iters
            print(f"    {mn:10s} {pa[mn]:10d} -> {pb[mn]:10d}  {d:+9.2f}/call" +
                  (f"  {d / a.keys:+7.2f}/key" if a.keys else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
