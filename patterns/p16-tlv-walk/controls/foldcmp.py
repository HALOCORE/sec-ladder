#!/usr/bin/env python3
"""Read p16's per-byte fold rates off the DISASSEMBLY, and check that the chunk
body is the same machine code on the safe and the unsafe side.

    python3 patterns/p16-tlv-walk/controls/gen_controls.py --build
    python3 patterns/p16-tlv-walk/controls/foldcmp.py
    python3 patterns/p16-tlv-walk/controls/foldcmp.py s_c4     # + full body text

**Why this file exists, and it is a repair.** `../NOTES.md` §10a.2 cited a
scratch script (`.temp/p24/foldbody.py`) for "the chunk body is the same machine
code on both sides". Re-run as committed that script prints `identical=False` at
every `K` and finds no body at all at `K = 4` and `8` — the **opposite** of the
verdict it was cited for — because it compares full instruction *text*, registers
included, when the published claim is about the **mnemonic sequence**, and
because it did not select the innermost loop. TASK_025_REVIEW minor 7. An
artefact a claim names must print that claim, so the working version ships here
and the broken one is not cited again.

**What it measures, and what kind of number that is.** The rates §10a.2
publishes to five decimal places — 6.50000, 6.62500, 5.18750, 5.09375, 5.04688,
5.37500 — are `chunk-body instructions / K`, i.e. **disassembly quantities**,
exact by construction. They are *not* five-decimal measured slopes: a marginal-Ir
slope on this driver carries ±0.01 Ir/byte from the `println` digit-count term,
which does not cancel within a binary and is 20× the gap between two of those
rates (TASK_025_REVIEW minor 6). This script is therefore the right way to
reproduce a rate; a two-point marginal difference is not.

What a run should print (rustc 1.97.1 / LLVM 22.1.6, `-O3 isolated`):

    K   body  movzbl  body/K     mnemonics equal safe-vs-unsafe?
    4     26       3  6.50000    True
    8     53       6  6.62500    True
    16    83      16  5.18750    True
    32   163      32  5.09375    True
    64   323      64  5.04688    True
    n4    43       8  5.37500    True     (chunks_exact(4), no try_into)
    n8    43       8  5.37500    True
    n16   83      16  5.18750    True     (identical to c16)
    ship  23       4  5.75000    False -- same 23-instruction multiset, different
                                 order: the load is scheduled before the x31
                                 chain on the safe side and after it on the
                                 unsafe side. §10a.2's identity claim is exact
                                 for the eight chunked spellings and
                                 multiset-only for the shipped pair.

`asm.py` is the only `objdump` caller on this project and this file goes through
it (`.memory/05-layout.md`).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
V = os.path.join(REPO, ".temp", "p16", "controls")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402


def loops(k):
    """Every backward-branch loop `(head_index, tail_index)` in the kernel."""
    out = []
    byaddr = {i.addr: n for n, i in enumerate(k.insns_fn)}
    for n, i in enumerate(k.insns_fn):
        t = asm._branch_target(i.text)
        if t is None or t >= i.addr:
            continue
        h = byaddr.get(t)
        if h is not None and h <= n:
            out.append((h, n))
    return out


def bodies(k):
    """`(len, n_movzbl, insns)` per INNERMOST loop, most `movzbl` first.

    Innermost = no other loop head lies strictly inside it. The chunk loop is
    the innermost loop carrying the most `movzbl`; the `.remainder()` fold is
    the other innermost loop and carries far fewer. Selecting on that rather
    than on nesting depth is what stops `K = 4` and `8` -- where LLVM has folded
    the four byte loads into one word load -- from being silently skipped.
    """
    ls = loops(k)
    out = []
    for h, t in ls:
        if any(h2 >= h and t2 <= t and (h2, t2) != (h, t) for h2, t2 in ls):
            continue
        b = k.insns_fn[h:t + 1]
        out.append((len(b), sum(1 for i in b if i.mnemonic == "movzbl"), b))
    out.sort(key=lambda r: (-r[1], r[0]))
    return out


def mnem(b):
    return [i.mnemonic for i in b]


def row(stem, k_for_rate):
    """One safe/unsafe pair. Returns (len, movzbl, rate, mnemonics_equal)."""
    got = {}
    for side in "su":
        path = os.path.join(V, side + "_" + stem)
        if not os.path.exists(path):
            return None
        got[side] = bodies(asm.kernel(path))[0]
    s, u = got["s"], got["u"]
    return s[0], s[1], u[0], u[1], s[0] / k_for_rate, mnem(s[2]) == mnem(u[2])


def main():
    print("%-6s %-14s %-14s %-10s %s"
          % ("probe", "safe (len/mvz)", "unsafe (len/mvz)", "body/K",
             "mnemonics equal?"))
    rows = [("c%d" % k, k) for k in (4, 8, 16, 32, 64)]
    rows += [("n%d" % k, 4 if k in (4, 8) else k) for k in (4, 8, 16)]
    rows += [("ship", 4)]
    bad = 0
    for stem, kr in rows:
        r = row(stem, kr)
        if r is None:
            print("  %-6s MISSING -- run gen_controls.py --build first" % stem)
            bad += 1
            continue
        sl, sm, ul, um, rate, eq = r
        note = ""
        if stem.startswith("n"):
            # Without `try_into` LLVM re-unrolls to a 8-byte body at K = 4 and
            # 8 alike, so the rate is body/8 there and body/K at K = 16.
            rate = sl / (8 if stem in ("n4", "n8") else int(stem[1:]))
            note = "  (no try_into)"
        if stem == "ship":
            note = ("  (LLVM 4x from rolled source; same multiset, different "
                    "schedule)")
        print("  %-6s %-14s %-14s %-10.5f %s%s"
              % (stem, "%d / %d" % (sl, sm), "%d / %d" % (ul, um), rate, eq,
                 note))
        if sl != ul:
            print("      ** body LENGTHS differ, %d vs %d" % (sl, ul))
            bad += 1
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            k = asm.kernel(os.path.join(V, name))
            print("\n==== %s: every innermost loop ====" % name)
            for ln, nz, b in bodies(k):
                print("  len=%-4d movzbl=%-4d head=%x" % (ln, nz, b[0].addr))
            print("---- fold body ----")
            for i in bodies(k)[0][2]:
                print("  %8x  %-9s %s" % (i.addr, i.mnemonic, i.text))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
