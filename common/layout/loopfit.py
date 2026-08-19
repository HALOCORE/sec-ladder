#!/usr/bin/env python3
"""The mechanism: 32-byte instruction-fetch geometry of every loop in a kernel.

Two binaries built from identical source, differing only in where the linker
put the kernel -- same `n_fn`, same `md5_fn_norel`, same executed instruction
stream -- can differ by up to 27% of wall clock and can flip the sign of a
rung-to-rung comparison (`.memory/03-measurement.md`, "Code layout: the 32-byte
fetch grid").  Two static, zero-parameter properties account for every mode
this project has found, on all seven patterns:

    win32   how many 32-byte fetch windows a loop body occupies
    jcc32   how many of a loop's branches CROSS or END ON a 32-byte boundary

`jcc32` is the Intel SKX102 "Jump Conditional Code" erratum predicate.  This
box is a Xeon Gold 6230, family 6 model 85 stepping 7 (Cascade Lake), microcode
`0x5000024`, i.e. a part carrying the *mitigated* microcode: a 32-byte chunk
containing such a jump is not cached in the DSB.  The predicate is exactly
LLVM's `-x86-align-branch` one -- an instruction occupying `[start, end)` is
affected iff `start // 32 != end // 32`, which covers "crosses" and "ends on"
at once.  Macro-fusion is applied: a fusible ALU op (cmp/test/add/sub/and/
inc/dec) immediately before a Jcc fuses into one uop and Intel's rule applies
to the pair, starting at the ALU op.

WHY EVERY LOOP AND NOT "THE INNER LOOP".  The predecessor of this file
(`.temp/r30/jcc.py`) picked the *tightest backward branch* as "the inner loop".
On any vectorised kernel that is the scalar tail, not the hot loop: on p01 it
picks a 12-byte tail over the 30-byte SSE loop, and that heuristic is what
produced p07 NOTES.md 11e's wrong-loop negative.  Do not reintroduce it.  This
module enumerates every back-edge and reports each loop's geometry; the caller
names the loop it means, by index.

The kernel's bytes are layout-invariant (`md5_fn_norel` is single-valued over a
layout population), so loop offsets are read ONCE from any build and shifted by
each recorded kernel address -- fitting a whole population needs no rebuild.

    python3 common/layout/loopfit.py .temp/layout/layout_p01.json
    python3 common/layout/loopfit.py --loops <binary>      # list loop indices
"""
import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402

JCC = {"jo", "jno", "jb", "jnb", "jae", "jc", "jnc", "je", "jz", "jne", "jnz",
       "jbe", "jna", "ja", "jnbe", "js", "jns", "jp", "jpe", "jnp", "jpo",
       "jl", "jnge", "jge", "jnl", "jle", "jng", "jg", "jnle", "jrcxz",
       "jecxz", "loop", "loope", "loopne"}
JMP = {"jmp", "jmpq", "bnd"}
FUSIBLE = {"cmp", "cmpq", "cmpl", "cmpb", "cmpw", "test", "testq", "testl",
           "testb", "testw", "add", "addq", "addl", "sub", "subq", "subl",
           "and", "andq", "andl", "inc", "incq", "incl", "dec", "decq", "decl"}

#: keys `layout_gen.py` writes that are NOT timing measurements.  Anything else
#: in a population row is an input stem (`small`, `large#p1c5`, ...).
META = {"lever", "idx", "addr", "n_fn", "md5_fn", "md5_fn_norel", "loops",
        "n_branch_fn", "n_hit_fn"}


def _class(insn):
    m = insn.mnemonic
    if m in JCC:
        return "jcc"
    if m in JMP:
        return "jmp"
    if m in ("call", "callq"):
        return "call"
    if m.startswith("ret"):
        return "ret"
    return None


def crosses(start, length, boundary=32):
    """Intel SKX102 predicate: crosses OR ends on a `boundary`-byte boundary."""
    return (start // boundary) != ((start + length) // boundary)


def analyse(insns, boundary=32):
    """Per-instruction records for every branch, with macro-fusion applied."""
    out = []
    for i, ins in enumerate(insns):
        cls = _class(ins)
        if cls is None:
            continue
        start, length = ins.addr, len(ins.raw)
        fused = False
        if cls == "jcc" and i > 0:
            prev = insns[i - 1]
            if prev.mnemonic in FUSIBLE and prev.addr + len(prev.raw) == start:
                start, length, fused = prev.addr, length + len(prev.raw), True
        out.append({"addr": ins.addr, "cls": cls, "fused": fused,
                    "start": start, "len": length,
                    "hit": crosses(start, length, boundary),
                    "text": " ".join(ins.text.split())[:48]})
    return out


def loops_of(binary, needle="kernel"):
    """Every loop in the kernel, as offsets from the kernel's entry address.

    A loop is a backward branch inside the declared extent; for each back-edge
    target the widest such branch is kept.  Returns
    `[{"lo", "hi", "bytes", "branches": [(start_off, len), ...]}, ...]`
    sorted by `lo`, which is the index space every `@N` rule refers to."""
    k = asm.kernel(binary, needle)
    insns = k.insns_fn
    base = k.extent[0] if k.has_extent else insns[0].addr
    recs = analyse(insns)
    seen = {}
    for ins in insns:
        if _class(ins) not in ("jcc", "jmp"):
            continue
        t = asm._branch_target(ins.text)
        if t is None or t >= ins.addr or t < base:
            continue
        lo, hi = t - base, ins.addr + len(ins.raw) - base
        if lo not in seen or hi > seen[lo]["hi"]:
            seen[lo] = {"lo": lo, "hi": hi, "bytes": hi - lo,
                        "branches": [(r["start"] - base, r["len"])
                                     for r in recs
                                     if lo <= r["addr"] - base < hi]}
    return [seen[lo] for lo in sorted(seen)]


def win32(loop, addr, boundary=32):
    """How many `boundary`-byte fetch windows the loop body occupies."""
    return ((addr + loop["hi"] - 1) // boundary
            - (addr + loop["lo"]) // boundary + 1)


def jcc32(loop, addr, boundary=32):
    """How many of the loop's branches cross/end on a `boundary` boundary."""
    return sum(1 for s, ln in loop["branches"]
               if crosses(addr + s, ln, boundary))


def kernel_report(binary, needle="kernel", boundary=32):
    """Layout-sensitive static description of one built binary.

    Everything here is derived from the disassembly with no fitted parameter
    and no choice of "the" loop.  `md5_fn_norel` is the control the population
    builder asserts is single-valued -- **not** `md5_fn`, which changes at
    every layout whenever the kernel can `call` a panic path, because the
    `call rel32` displacement moves (`.memory/03-measurement.md`)."""
    k = asm.kernel(binary, needle)
    insns = k.insns_fn
    recs = analyse(insns, boundary)
    addr = k.extent[0] if k.has_extent else insns[0].addr
    loops = loops_of(binary, needle)
    return {
        "addr": addr,
        "n_fn": k.n_fn,
        "md5_fn": k.md5_fn[:12],
        "md5_fn_norel": k.md5_fn_norel[:12],
        "n_branch_fn": len(recs),
        "n_hit_fn": sum(1 for r in recs if r["hit"]),
        "loops": [{"lo": L["lo"], "hi": L["hi"], "bytes": L["bytes"],
                   "n_branch": len(L["branches"]),
                   "win32": win32(L, addr, boundary),
                   "jcc32": jcc32(L, addr, boundary)} for L in loops],
        "recs": recs,
    }


def any_loop_jcc32(row):
    """`jcc32` aggregated over every loop: >=1 crossing branch anywhere in a
    loop body.  The one loop-free reading of the predicate, so a rule that does
    not want to name a loop index can still be stated without a heuristic."""
    return sum(L["jcc32"] for L in row["loops"])


def perfect(groups):
    """True iff the groups are totally ordered with no overlap."""
    gs = [g for g in groups.values() if g]
    if len(gs) < 2:
        return False
    gs.sort(key=statistics.median)
    return all(max(gs[i]) < min(gs[i + 1]) for i in range(len(gs) - 1))


def load(path):
    """A `layout_<tag>.json` as `{cell: [row, ...]}`."""
    rows = {}
    for key, v in json.load(open(path)).items():
        cell, lever, idx = key.split("|")
        rows.setdefault(cell, []).append({"lever": lever, "idx": int(idx), **v})
    return rows


def stems(rows):
    """The input-stem keys (timing columns) of a loaded population."""
    any_row = next(iter(rows.values()))[0]
    return sorted(k for k in any_row if k not in META)


def fit(rows, cell, min_effect=0.01):
    """Score every (loop, property) pair of one cell against every timing
    column.  Yields `(li, loop, prop, keys, stem, ratio, is_perfect)`."""
    pop = rows[cell]
    loops = pop[0]["loops"]
    for li in range(len(loops)):
        for prop in ("win32", "jcc32"):
            groups = {}
            for r in pop:
                groups.setdefault(r["loops"][li][prop], []).append(r)
            if len(groups) < 2:
                continue
            for stem in stems(rows):
                gr = {k: [x[stem] for x in v] for k, v in groups.items()}
                ks = sorted(gr)
                ratio = statistics.median(gr[ks[-1]]) / \
                    statistics.median(gr[ks[0]])
                ok = perfect(gr)
                if abs(ratio - 1) < min_effect and not ok:
                    continue
                yield li, loops[li], prop, ks, stem, ratio, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="+",
                    help="layout_<tag>.json population(s), or a binary with "
                         "--loops")
    ap.add_argument("--loops", action="store_true",
                    help="argument is a BINARY: just list its loop indices")
    ap.add_argument("--symbol", default="kernel")
    ap.add_argument("--min-effect", type=float, default=0.01)
    a = ap.parse_args()

    if a.loops:
        for b in a.target:
            r = kernel_report(b, a.symbol)
            print(f"{b}\n  kernel @ {r['addr']:#x}  %32={r['addr'] % 32}  "
                  f"n_fn={r['n_fn']}  md5_fn_norel={r['md5_fn_norel']}")
            for li, L in enumerate(r["loops"]):
                print(f"  loop{li} [+{L['lo']:#x},+{L['hi']:#x}) "
                      f"{L['bytes']:3d}B  {L['n_branch']} branch(es)  "
                      f"win32={L['win32']}  jcc32={L['jcc32']}")
        return 0

    for path in a.target:
        rows = load(path)
        print(f"\n### {os.path.basename(path)}")
        for cell in sorted(rows):
            for li, L, prop, ks, stem, ratio, ok in fit(rows, cell,
                                                        a.min_effect):
                print(f"  {cell:12s} loop{li} [+{L['lo']:#x},+{L['hi']:#x}) "
                      f"{L['bytes']:3d}B  {prop:5s}{ks} {stem:12s} "
                      f"x{ratio:.4f}{'  *PERFECT*' if ok else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
