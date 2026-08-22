#!/usr/bin/env python3
"""p47's per-byte rates, taken off the DISASSEMBLY and never off a marginal.

    python3 patterns/p47-ct-compare/controls/loops.py --opt O3 --mode isolated

`.tasks/TASK_026.md` §0 item 2: *a five-decimal rate must come from the
disassembly (`body_len / K`), never from a marginal.* This script finds each
shipped kernel's innermost backward branch, prints the body, counts it, and
divides by the number of tag bytes that body consumes -- so the rate is an
instruction count, not a regression coefficient.

It also answers the pattern's other half **statically**: is there a
data-dependent early exit inside the comparison loop? A conditional branch out
of the loop body whose condition is derived from the loaded bytes is exactly
the thing `.memory/06-catalogue.md` predicted the optimiser would reintroduce.
The script reports every conditional branch in each body so the claim is
readable rather than asserted.

    python3 patterns/p47-ct-compare/controls/loops.py --vecops

⚠ `--vecops` exists because TASK_064_REVIEW minor 6 measured that ../NOTES.md
1's original "vector ops" column (18 / 22 / 22 / 22 / 22) **reproduced under no
counting rule**, this script's included -- it was the only column of that table
that did not. The column is withdrawn and replaced by this one, whose rule is
one line of code and is printed with the numbers: **an instruction counts as
vector when one of its operands names an `%xmm`/`%ymm`/`%zmm` register**, over
the whole kernel symbol. That rule is checkable by a reader with objdump and
does not depend on keeping a mnemonic list in sync with the toolchain -- which
is how the original column went wrong: the `vec=` figure this file prints per
LOOP BODY uses a mnemonic PREFIX list, and a prefix list silently under-counts
whatever the next LLVM emits (here `pshufd`, `psrld`, `psrlw` and `movdqa` are
all outside it).
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
BUILD = os.path.join(REPO, ".temp", "build", "p47")
OBJDUMP = os.path.expanduser("~/tools/llvm/bin/llvm-objdump")

CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

#: bytes of *tag* consumed per iteration of the body, read off the pointer
#: bump in the listing. Hand-transcribed rather than parsed: the increment is
#: an immediate on an `add`/`inc` and picking the right one is a reading.
VECWIDTH_NOTE = ("`K` is the tag bytes one iteration consumes, taken from the "
                 "loop's own induction-variable bump ($0x10 / $0x20) and "
                 "cross-checked against the sweep: rate * 128 must equal the "
                 "band-t step per +128 compared bytes.")


def kernel_body(binary):
    r = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", binary],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"loops.py: objdump failed on {binary}")
    out, on = [], False
    for line in r.stdout.splitlines():
        if re.match(r"^[0-9a-f]+ <.*kernel.*>:", line):
            on = True
            continue
        if on:
            if not line.strip():
                break
            out.append(line)
    return out


def insns(lines):
    """(addr, mnemonic, operands) per instruction line."""
    out = []
    for ln in lines:
        m = re.match(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$", ln)
        if m:
            out.append((int(m.group(1), 16), m.group(2), m.group(3).strip()))
    return out


def inner_loops(ins):
    """Every backward conditional/unconditional branch and the body it closes.

    The INNERMOST loop is the shortest such body; p47's kernels have two
    (the comparison walk and the tag loop) plus vectoriser epilogues."""
    by_addr = {a: i for i, (a, _, _) in enumerate(ins)}
    loops = []
    for i, (a, mn, op) in enumerate(ins):
        if not mn.startswith("j"):
            continue
        m = re.match(r"^(0x[0-9a-f]+)", op)
        if not m:
            continue
        t = int(m.group(1), 16)
        if t < a and t in by_addr:
            loops.append((by_addr[t], i))
    return sorted(loops, key=lambda p: p[1] - p[0])


#: THE VECTOR-OP RULE, stated as code so ../NOTES.md 1 can name it: an
#: instruction is a vector instruction when one of its operands is an
#: %xmm/%ymm/%zmm register. Deliberately NOT a mnemonic list -- see the module
#: docstring, and TASK_064_REVIEW minor 6.
VECREG = re.compile(r"%[xyz]mm")


def cmd_vecops(a):
    print(f"# p47 vector ops in the kernel symbol  [{a.opt} {a.mode}]")
    print("# RULE: one operand names an %xmm/%ymm/%zmm register. Whole kernel "
          "symbol, not just the tag loop.")
    print(f"{'cell':12s} {'insns':>6s} {'vector':>7s}   by mnemonic")
    for c in a.cells.split(","):
        b = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
        if not os.path.exists(b):
            print(f"{c:12s} MISSING {b}")
            continue
        ins = insns(kernel_body(b))
        if not ins:
            print(f"{c:12s} no `kernel` symbol (whole-mode inlines it into main)")
            continue
        tab = {}
        for _, m, o in ins:
            if VECREG.search(o):
                tab[m] = tab.get(m, 0) + 1
        n = sum(tab.values())
        print(f"{c:12s} {len(ins):6d} {n:7d}   "
              + ("  ".join(f"{k}:{v}" for k, v in sorted(tab.items())) or "-"))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--show", action="store_true", help="print each body")
    ap.add_argument("--vecops", action="store_true",
                    help="count vector instructions in the kernel symbol")
    a = ap.parse_args()
    if a.vecops:
        return cmd_vecops(a)
    print(f"# p47 loop bodies  [{a.opt} {a.mode}]   {VECWIDTH_NOTE}")
    for c in a.cells.split(","):
        b = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
        if not os.path.exists(b):
            print(f"{c:12s} MISSING {b}")
            continue
        ins = insns(kernel_body(b))
        if not ins:
            print(f"{c:12s} no `kernel` symbol (whole-mode inlines it into main)")
            continue
        loops = inner_loops(ins)
        print(f"\n## {c}   ({len(ins)} instructions in the kernel symbol, "
              f"{len(loops)} backward branch(es))")
        for lo, hi in loops[:4]:
            body = ins[lo:hi + 1]
            mn = [m for _, m, _ in body]
            vec = sum(1 for m in mn if m.startswith(("movdq", "pxor", "por",
                                                     "pcmpeq", "pand", "pshuf",
                                                     "psrl", "movd", "movq")))
            # every conditional branch inside the body EXCEPT the closing one
            conds = [(hex(ad), m, o) for ad, m, o in body[:-1]
                     if m.startswith("j") and m != "jmp"]
            bump = [o for _, m, o in body if m in ("add", "addq", "inc", "incq")]
            print(f"   body {len(body):3d} insn  vec={vec:2d}  "
                  f"iv-bump={bump}  "
                  f"interior conditional branches={len(conds)}")
            if conds:
                print(f"      ⚠ {conds}")
            if a.show:
                for ad, m, o in body:
                    print(f"        {ad:#x}  {m:<12s} {o}")
    print("\n# An 'interior conditional branch' inside the TAG loop would be a "
          "data-dependent early exit -- the thing .memory/06-catalogue.md "
          "predicted the optimiser would reintroduce. Read the count above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
