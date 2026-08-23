#!/usr/bin/env python3
"""The outward-dispatch LICENCE check, and the sidecar it emits.

⚠ **This is a PROTOTYPE for a decision that has not been taken.** It answers
§0 of `.tasks/TASK_075.md` -- *should the kernel-column licence be a recorded
column, an on-demand tool, or a static check?* -- as **a static check**, and it
is deliberately parked here rather than in `harness/` so that the decision can
be taken on its merits: a file in `harness/` stales all 22 gate records.

WHAT IT DECIDES.  `.memory/03-measurement.md`, widened at TASK_073:

    Ask "does every cell execute the same work OUTSIDE the kernel symbol",
    not "does every cell call the same libc routines".

For each cell it lists every control transfer that leaves the kernel symbol,
then compares the multisets.  Equal live sets => the kernel-exclusive `Ir`
column may be differenced between those two cells.  It needs no run and no
measurement record; it needs the `-O3 isolated` matrix built
(`harness/build.py pNN`).

FOUR THINGS IT GETS RIGHT AND A NAIVE VERSION DOES NOT -- each one was a
measured wrong answer from an earlier draft of this file:

 1. **Not `@plt`/`@GLIBC`.**  p36's callees are the pattern's own project-local
    functions, so a check that lists only library targets reproduces the exact
    miss that made this necessary.  Every outward target counts.
 2. **Absence of a call is the hazard.**  A devirtualised `match` calls
    nothing, so the verdict is multiset EQUALITY: `{}` against `{op_add}` is
    NOT LICENSED.
 3. **A GOT-indirect call is NOT unknown.**  rustc calls libc through the GOT,
    so every Rust rung's `memcpy` reads `call *0x413d1(%rip)  # <memcpy@GLIBC>`
    -- syntactically indirect, and objdump has already resolved it.  A rule of
    "operand starts with `*` => unknown" marks all four Rust rungs of every
    pattern NOT LICENSED and is useless.  When objdump falls back to
    `<_DYNAMIC+0x2c8>` the slot is read out of the relocations instead: on p13
    those six anonymous slots are `core::panicking::panic_fmt` and
    `core::slice::index::slice_index_fail`.
 4. **A DIVERGING callee cannot move a dynamic column.**  Every record in
    `results/` came from a run whose checksum the gate accepted, so a call to
    `core::panicking::*`, `slice_index_fail` or `__stack_chk_fail` executed
    exactly zero times.  Counting those would mark almost every safe-vs-unsafe
    pair NOT LICENSED for panic pads that never fire.  This is an argument, not
    a heuristic -- all of them are `-> !`.

WHAT IT CANNOT DO, MEASURED (`.temp/p75/crosscheck2.py`, 176 pair/blob rows
scored against `synthesis/outward_ir.json`, a callgrind caller->callee sweep):

    hits 156   false LICENSED 10   false alarms 0   abstentions 10

⚠ Scored against a SECOND, independent sweep the same numbers read
154 / 12 / 0 / 10, and the two-row difference is itself the first mechanism
below: p03's and p04's `memset` term does not reproduce.

The misses are exactly two mechanisms, and BOTH are cost differences behind an
equal set of names:

  * glibc `memset`'s path length moves with the stack array's alignment
    (p03, p04): +-7.00 `Ir`/call between cells with IDENTICAL call sets and,
    on `R5 - R4`, between BYTE-IDENTICAL kernels.  On the callee-inclusive
    column that makes `R5 - R4` read **-7.00** -- *"the proof costs -7
    instructions"* -- and which cells carry it is not stable: two independent
    sweeps of the same binaries moved the outward figure on 6 of 348
    (pattern, input, cell) triples while the kernel-EXCLUSIVE figure moved on
    **0 of 348**.  Here the kernel-exclusive column is the right one and
    adding callees is strictly worse.
  * gcc routes every libc call through a 2-instruction PLT thunk
    (`endbr64 ; jmp *GOT`) that callgrind attributes as its own function;
    clang's thunk is a bare `jmp` and is folded into the callee.  That is
    **+2.00 `Ir` per libc call in gcc's column only** (p02 +2.00, p12 +23.99,
    p11 +299.87 = 150 `strlen` calls x 2.00), and one of the two instructions
    is the `endbr64` of gcc's default `-fcf-protection=full`.

Usage:
    synthesis/licence.py p13 --show
    synthesis/licence.py --all
    synthesis/licence.py --emit synthesis/licence.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import build as bld  # noqa: E402

BUILD = os.path.join(REPO, ".temp", "build")
PAIRS = [("safe_naive", "unsafe", "R2-R4"),
         ("safe_tuned", "unsafe", "R3-R4"),
         ("verus", "unsafe", "R5-R4"),
         ("c-gcc", "c-clang", "gcc-clang")]

_BRANCHY = re.compile(r"^(j[a-z]+|callq?)$")
_NORETURN = re.compile(
    r"panic|slice_index_fail|slice_end_index|slice_start_index|len_mismatch"
    r"|unwrap_failed|expect_failed|assert_failed|handle_alloc_error"
    r"|rust_begin_unwind|__stack_chk_fail|\babort\b|_Unwind_Resume"
    r"|core.*9panicking|copy_from_slice")


def is_noreturn(sym):
    return bool(_NORETURN.search(sym))


_GOT_CACHE = {}


def got_map(binary):
    """{got_slot_addr: callee name} from the dynamic relocations."""
    if binary in _GOT_CACHE:
        return _GOT_CACHE[binary]
    byaddr = sorted((a, s, sz) for s, (a, sz) in asm.nm_extents(binary).items())
    out = {}
    r = subprocess.run(["readelf", "-rW", binary], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) < 3 or not re.fullmatch(r"[0-9a-f]{8,}", p[0]):
            continue
        slot, kind = int(p[0], 16), p[2]
        if kind in ("R_X86_64_GLOB_DAT", "R_X86_64_JUMP_SLOT") and len(p) >= 5:
            out[slot] = p[4]
        elif kind == "R_X86_64_RELATIVE" and len(p) >= 4:
            try:
                tgt = int(p[3], 16)
            except ValueError:
                continue
            hit = [s for a, s, sz in byaddr if a <= tgt < a + sz]
            if hit:
                out[slot] = hit[0]
    _GOT_CACHE[binary] = out
    return out


def outward(k, binary):
    """(sorted outward targets, unresolvable-indirect insn texts)."""
    if k.extent:
        lo, hi = k.extent[0], k.extent[0] + k.extent[1]
    else:
        lo, hi = k.insns[0].addr, k.insns[-1].addr + len(k.insns[-1].raw)
    gm = got_map(binary)
    targets, indirect = [], []
    for i in k.insns:
        mn = i.mnemonic
        if not _BRANCHY.match(mn) and not mn.startswith("jmp"):
            continue
        parts = i.text.split(None, 1)
        opnd = parts[1] if len(parts) > 1 else ""
        m = re.search(r"<([^>]+)>", i.text)
        name = m.group(1) if m else None
        if opnd.lstrip().startswith("*"):
            slot = re.search(r"#\s*([0-9a-f]+)\s", i.text)
            if slot and int(slot.group(1), 16) in gm:
                targets.append(gm[int(slot.group(1), 16)])
            elif name is not None and not name.startswith("_DYNAMIC"):
                targets.append(name)
            else:
                indirect.append(f"{mn} {opnd.split('#')[0].strip()}")
            continue
        addr = None
        m2 = re.match(r"\s*([0-9a-f]+)\b", opnd)
        if m2:
            addr = int(m2.group(1), 16)
        if mn.startswith("call"):
            targets.append(name or (f"0x{addr:x}" if addr is not None else "?"))
        elif addr is not None and not (lo <= addr < hi):
            targets.append((name or f"0x{addr:x}") + "  [tail/outlined]")
    return sorted(targets), indirect


def survey(pat, opt="O3", mode="isolated", cells=None):
    pdir = pattern_dir(pat)
    cells = cells or bld.measured_cells(pdir)
    out = {}
    for c in cells:
        p = os.path.join(BUILD, pat, f"{c}-{opt}-{mode}")
        if not os.path.exists(p):
            out[c] = ("NOT BUILT", None, None)
            continue
        k = asm.try_kernel(p)
        if k is None:
            out[c] = ("no kernel symbol (inlined; the column is None here)",
                      None, None)
            continue
        t, ind = outward(k, p)
        out[c] = (None, t, ind)
    return out


def pattern_dir(pat):
    for d in sorted(os.listdir(os.path.join(REPO, "patterns"))):
        if d.startswith(pat + "-"):
            return os.path.join(REPO, "patterns", d)
    raise KeyError(pat)


def short(s):
    s = re.sub(r"Cs[0-9A-Za-z]{10,}_", "", s)
    s = re.sub(r"_R[NIC]*[vt]?", "", s)
    s = re.sub(r"\d+(?=[A-Za-z_])", "::", s)
    return s.lstrip(":")


def verdict(a, b, sa, sb):
    ea, ta, ia = sa
    eb, tb, ib = sb
    if ea or eb:
        return None, f"cannot decide: {a}={ea or 'ok'}, {b}={eb or 'ok'}"
    if len(ia) != len(ib):
        return False, (f"ASYMMETRIC INDIRECT dispatch ({a}: {len(ia)}, "
                       f"{b}: {len(ib)}); e.g. `{(ia or ib)[0]}`")
    if ia or ib:
        return None, (f"both sides dispatch through an unresolvable pointer "
                      f"({len(ia)} each); e.g. `{ia[0]}`")
    la = sorted(x for x in ta if not is_noreturn(x))
    lb = sorted(x for x in tb if not is_noreturn(x))
    cold = sorted(set(x for x in ta + tb if is_noreturn(x)))
    if la == lb:
        note = ("0 outward transfers" if not la
                else "identical live set: " + ", ".join(short(x) for x in la))
        if sorted(ta) != sorted(tb):
            note += ("; differs only in DIVERGING callees, which execute 0 "
                     "times in any accepted run: "
                     + ", ".join(short(c) for c in cold))
        return True, note
    only_a = sorted(set(x for x in la if la.count(x) > lb.count(x)))
    only_b = sorted(set(x for x in lb if lb.count(x) > la.count(x)))
    bits = []
    if only_a:
        bits.append(f"only {a} calls {[short(x) for x in only_a]}")
    if only_b:
        bits.append(f"only {b} calls {[short(x) for x in only_b]}")
    return False, "; ".join(bits)


TAG = {True: "LICENSED", False: "NOT-LIC", None: "UNDEC"}


def all_patterns():
    return sorted(d for d in os.listdir(BUILD) if re.fullmatch(r"p\d\d", d))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--emit", metavar="PATH")
    a = ap.parse_args()

    pats = all_patterns() if (a.all or a.emit) else [a.pattern]
    doc = {}
    for pat in pats:
        s = survey(pat, a.opt, a.mode)
        gf = [f for f in sorted(os.listdir(os.path.join(REPO, "results", "gate")))
              if f.startswith(pat + "-") and not f.endswith(".partial.json")]
        gsha = None
        if gf:
            gsha = json.load(open(os.path.join(REPO, "results", "gate", gf[0]))) \
                .get("source_sha256")
        rec = {"opt": a.opt, "mode": a.mode,
               "gate_source_sha256": gsha, "cells": {}, "pairs": {}}
        for c, (e, t, i) in s.items():
            rec["cells"][c] = {"error": e, "outward": t, "unresolved_indirect": i}
        if not a.emit:
            print(f"\n=== {pat}  {a.opt}/{a.mode} ===")
            if a.show:
                for c, (e, t, i) in s.items():
                    print(f"  {c:12s} " + (e if e else
                          f"outward={[short(x) for x in t]} indirect={i}"))
        for x, y, lab in PAIRS:
            if x not in s or y not in s:
                continue
            ok, why = verdict(x, y, s[x], s[y])
            rec["pairs"][lab] = {"verdict": TAG[ok], "why": why}
            if not a.emit:
                print(f"  {lab:10s} {x:11s} - {y:11s}  {TAG[ok]:9s} {why}")
        doc[pat] = rec
    if a.emit:
        json.dump(doc, open(a.emit, "w"), indent=1, sort_keys=True)
        n = sum(len(v["pairs"]) for v in doc.values())
        print(f"wrote {a.emit}: {len(doc)} patterns, {n} pair verdicts")


if __name__ == "__main__":
    main()
