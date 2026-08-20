#!/usr/bin/env python3
"""Attribute a Rust kernel's surviving panic landing pads to source `line:col`.

    python3 patterns/p12-strcat-fixed/controls/pads.py <binary> [<binary> ...]
    python3 .../pads.py --source <binary>      # + the guarded expression
    python3 .../pads.py --symbol '6kernel' --raw <binary>

**Why this exists.** Counting panic landing pads tells you *how many* bounds
checks survived optimisation; it does not tell you **which**. p12 shipped a
count -- 7 in R2, 2 in R3, 0 in R4 -- read it as "the destination fold's check
survives", and put that conclusion in `NOTES.md` 4 and in a source comment in
`safe_tuned.rs`. TASK_040_REVIEW decoded the pads and the conclusion was
backwards: `dst[..dlen]` contributes **zero** pads in all three fold spellings,
and both survivors are the window reslice `&buf[off..off + len]` and the source
reslice `&w[p..q]`. So the constant 2 was evidence the fold never contributed a
pad. `.memory/03-measurement.md`, *"Attribute a surviving panic pad by DECODING
its `core::panic::Location`"*: always decode before attributing.

**How.** rustc passes each panic entry a `&core::panic::Location` and materialises
it with a rip-relative `lea` in the pad:

    struct Location { file: *const u8, len: usize, line: u32, col: u32 }

`line` and `col` are plain constants in the image. `file` is **not**: in a PIE
it is stored as zero and its link-time address lives in the `R_X86_64_RELATIVE`
addend, so the name comes from `readelf -rW` and not from dereferencing the
image. Two traps, both stepped in while writing this:

- **the register is not fixed.** `panic_bounds_check(idx, len, &Loc)` puts the
  pointer in `%rdx`; the slice-range entries use `%rax`. Matching one register
  loses pads silently -- it cost 2 of R2's 7 on the first attempt. So this
  matches any register and validates the decoded struct instead.
- **the pad may hold more than one `lea`.** Take the nearest preceding one that
  decodes as a plausible `Location`, not simply the last.

Nothing here is p12-specific: point it at any pattern's Rust rung.

**Reading the output.** A pad is a check the optimiser could not discharge. Its
`line:col` is the *source* expression, so it survives inlining and it is stable
under everything except editing the file above that line -- which is why p12's
`safe_tuned.rs` comment block is kept at a fixed line count.
"""
import argparse
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
READELF = "/usr/bin/readelf"
OBJDUMP = "/usr/bin/objdump"


def load_segments(path):
    """[(vaddr, file_offset, filesz)] for every PT_LOAD."""
    out = subprocess.run([READELF, "-lW", path],
                         capture_output=True, text=True).stdout
    segs = []
    for line in out.splitlines():
        f = line.split()
        if f and f[0] == "LOAD":
            # Type Offset VirtAddr PhysAddr FileSiz MemSiz Flg Align
            segs.append((int(f[2], 16), int(f[1], 16), int(f[4], 16)))
    return segs


def load_relative(path):
    """{offset: addend} for every R_X86_64_RELATIVE.

    In a PIE the `file` pointer inside a `Location` is stored as zero and the
    real link-time address lives in the relocation's addend, so dereferencing
    the raw image finds nothing. `line` and `col` are plain constants and need
    none of this."""
    out = subprocess.run([READELF, "-rW", path],
                         capture_output=True, text=True).stdout
    rel = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 4 and f[2] == "R_X86_64_RELATIVE":
            rel[int(f[0], 16)] = int(f[-1], 16)
    return rel


def reader(path):
    data = open(path, "rb").read()
    segs = load_segments(path)

    def read(vaddr, n):
        for va, off, fsz in segs:
            if va <= vaddr < va + fsz:
                start = off + (vaddr - va)
                return data[start:start + n]
        return None
    return read


def kernel_body(path, symbol):
    """The disassembly lines of the one symbol matching `symbol`."""
    out = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", path],
                         capture_output=True, text=True).stdout
    lines = out.splitlines()
    pat = re.compile(r"^[0-9a-f]+ <(\S*%s)>:$" % symbol)
    hits = [i for i, l in enumerate(lines) if pat.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"pads.py: {path}: {len(hits)} symbols match "
                         f"{symbol!r}, expected exactly 1")
    body = []
    for l in lines[hits[0] + 1:]:
        if not l.strip():
            break
        body.append(l)
    return body


# The Location pointer is an ARGUMENT of the panic entry, so which register the
# `lea` targets depends on the entry's arity: `panic_bounds_check(idx, len,
# &Loc)` puts it in %rdx, `slice_index_len_fail`-style entries in %rax/%rcx.
# Matching one register silently under-counts, so match any and validate the
# decoded struct instead.
LEA = re.compile(r"lea\s+0x[0-9a-f]+\(%rip\),%\w+\s+#\s+([0-9a-f]+)")
CALL_IND = re.compile(r"call\s+\*0x[0-9a-f]+\(%rip\)")
CALL_DIR = re.compile(r"call\s+[0-9a-f]+ <([^>]+)>")
#: A `Location` is 24 bytes: a file pointer into a read-only segment, a file
#: length, and two u32s that are a plausible line and column of real source.
MAX_LINE, MAX_COL, MAX_PATH = 100000, 1000, 4096


def decode_location(read, rel, vaddr):
    blob = read(vaddr, 24)
    if not blob or len(blob) != 24:
        return None
    fptr, flen, line, col = struct.unpack("<QQII", blob)
    if not (1 <= flen <= MAX_PATH) or not (1 <= line <= MAX_LINE) \
            or not (1 <= col <= MAX_COL):
        return None
    name = read(rel.get(vaddr, fptr), flen)
    if name is None or b"\x00" in name:
        return None
    return line, col, name.decode("utf-8", "replace")


def pads(path, symbol):
    """[(line, col, file)] for each panic landing pad inside `symbol`."""
    read, rel = reader(path), load_relative(path)
    found, pending = [], []
    for l in kernel_body(path, symbol):
        m = LEA.search(l)
        if m:
            pending.append(int(m.group(1), 16))
            continue
        direct = CALL_DIR.search(l)
        is_panic_call = (CALL_IND.search(l) and "memcpy" not in l) or \
            (direct and "panic" in direct.group(1))
        if is_panic_call:
            # nearest preceding lea whose target decodes as a real Location
            for vaddr in reversed(pending):
                loc = decode_location(read, rel, vaddr)
                if loc:
                    found.append(loc)
                    break
            pending = []
    return found


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("binary", nargs="+")
    ap.add_argument("--symbol", default="6kernel",
                    help="regex the mangled kernel symbol must end with "
                         "(default: 6kernel)")
    ap.add_argument("--raw", action="store_true",
                    help="also print the source file each pad names")
    # NOT nargs="?": an optional-valued flag in front of the positional list
    # silently eats the first binary.
    ap.add_argument("--source", action="store_true",
                    help="resolve each pad's file against the repo root and "
                         "print the expression it guards, with a caret")
    ap.add_argument("--root", default=REPO,
                    help="what the decoded paths are relative to "
                         "(default: the repo this file lives in)")
    a = ap.parse_args()
    rc = 0
    for b in a.binary:
        try:
            p = pads(b, a.symbol)
        except SystemExit as e:
            print(f"{os.path.basename(b):30s} {e}")
            rc = 1
            continue
        loc = sorted(set((l, c) for l, c, _ in p))
        print(f"{os.path.basename(b):30s} pads={len(p):<2d} "
              + "  ".join(f"{l}:{c}" for l, c in loc))
        if a.raw:
            for l, c, f in sorted(set(p)):
                print(f"{'':30s}   {f}:{l}:{c}")
        if a.source:
            for l, c, f in sorted(set(p)):
                path = f if os.path.isabs(f) else os.path.join(a.root, f)
                try:
                    text = open(path).read().splitlines()[l - 1]
                except (OSError, IndexError):
                    print(f"  {l}:{c}  <{f} not readable>")
                    continue
                print(f"  {l:>4d}:{c:<3d} {text.strip()}")
                print(f"  {'':>4s} {'':<3s} "
                      + " " * (c - 1 - (len(text) - len(text.lstrip()))) + "^")
    return rc


if __name__ == "__main__":
    sys.exit(main())
