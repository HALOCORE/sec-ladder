#!/usr/bin/env python3
"""Resolve a kernel's indirect `call *disp(%rip)` targets to SYMBOLS.

Rust emits `core::panicking::panic_bounds_check` through a GOT slot, so the
disassembly alone says only `_DYNAMIC+0x2c8`. Each slot carries an
R_X86_64_RELATIVE relocation whose ADDEND is the target address; `nm` maps that
address to a name. This is how TASK_060_REVIEW resolved the three surviving
panic sites by symbol rather than by counting calls, and it is what
../NOTES.md 4 and 5f quote.

    python3 patterns/p27-handle-table/controls/gotresolve.py <binary> [sym]

    harness/build.py p27                                    # the shipped cells
    sh patterns/p27-handle-table/controls/build_controls.sh  # the controls
"""
import re, subprocess, sys, collections
b = sys.argv[1]
sym = sys.argv[2] if len(sys.argv) > 2 else "kernel"
rel = {}
for ln in subprocess.run(["readelf", "-r", "-W", b], capture_output=True, text=True).stdout.splitlines():
    m = re.match(r"^([0-9a-f]+)\s+\S+\s+(\S+)\s+([0-9a-f]*)\s*(\S*)", ln.strip())
    if m and m.group(2).startswith("R_X86_64"):
        rel[int(m.group(1), 16)] = (m.group(2), ln.strip().split()[-1])
names = {}
for ln in subprocess.run(["nm", "-C", "--defined-only", b], capture_output=True, text=True).stdout.splitlines():
    p = ln.split(None, 2)
    if len(p) == 3:
        try: names[int(p[0], 16)] = p[2]
        except ValueError: pass
asm = subprocess.run(["objdump", "-d", "--no-show-raw-insn", b], capture_output=True, text=True).stdout
cur, out = None, collections.Counter()
for ln in asm.splitlines():
    m = re.match(r"^[0-9a-f]+ <(.*)>:", ln)
    if m: cur = m.group(1)
    if cur is None or sym not in cur: continue
    m = re.search(r"call\s+\*0x[0-9a-f]+\(%rip\)\s+#\s+([0-9a-f]+)", ln)
    if not m: continue
    slot = int(m.group(1), 16)
    kind, add = rel.get(slot, ("?", "?"))
    try: tgt = int(add, 16)
    except ValueError: tgt = None
    out[names.get(tgt, f"{kind} -> {add}")] += 1
    continue
for ln in asm.splitlines():
    pass
for k, v in out.most_common():
    print(f"  {v:2d}x  {k}")
