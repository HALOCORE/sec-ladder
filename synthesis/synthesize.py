#!/usr/bin/env python3
"""The cross-pattern synthesis: `results/synthesis.md`.

`CLAUDE.md` describes this project as patterns *"compared on assembly,
instruction count, timing, proof burden and trusted-base size"*.  Until now
there were 22 per-pattern tables under `results/tables/` and nothing that
compared them (RECAP "Owed" 13).  This is that comparison.

    synthesis/synthesize.py                 # -> results/synthesis.md
    synthesis/synthesize.py --stdout        # to the terminal instead

WHY THIS DIRECTORY.  `harness/check.py::main` hashes
`harness/*.py`, `common/*.py`, `common/layout/*.py`, `patterns/pNN/*.md`,
`patterns/pNN/model.py`, `patterns/pNN/controls/*.py`, `patterns/pNN/inputs/gen.py`,
`common/driver.*` and `verus_run.py` into every gate record's `source_sha256`;
`harness/measure.py::provenance` hashes a subset of the same list into every
MEASUREMENT record.  A file in any of those places stales 22 gate records (and,
for `build/asm/measure.py`, 22 measurement records, which forces a re-measure
that re-takes the wall-clock block).  `synthesis/` is in neither glob, and so is
`results/synthesis.md` -- verified by evaluating both globs literally, not by
reading the docstring that describes them.

WHAT IT READS.  Committed records only: `results/pNN-*.json` (measurement) and
`results/gate/pNN-*.json` (gate).  It never builds, never runs a binary and
never writes a record.  One exception, declared at the top of every table it
affects: the outward-dispatch LICENCE comes from `synthesis/licence.json`,
because **no committed record carries the information** -- see `LICENCE_NOTE`.
"""
import argparse
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")
GATE = os.path.join(RESULTS, "gate")
HERE = os.path.dirname(os.path.abspath(__file__))
LICENCE = os.path.join(HERE, "licence.json")
OUTWARD = os.path.join(HERE, "outward_ir.json")

RUNGS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
PAIRS = [("safe_naive", "unsafe", "R2-R4"),
         ("safe_tuned", "unsafe", "R3-R4"),
         ("verus", "unsafe", "R5-R4"),
         ("c-gcc", "c-clang", "gcc-clang")]

# --------------------------------------------------------------------------
# The search state, and why it is a DECLARED table and not a derived one.
#
# `R3 - R4` differences two rungs whose spellings have been searched to wildly
# different depths.  A table that puts a well-searched pattern beside an
# unsearched one and differences both is partly measuring SEARCH EFFORT, and
# the tree has three measured instances of the difference moving a long way
# when a side was finally searched (below).  The honest first column is
# therefore the search state -- but **nothing committed records it**: control
# registries are heterogeneous and only 8 of 22 patterns have a `--list`
# (RECAP "Owed" 12).  So each entry below quotes the reviewed sentence it comes
# from, and every pattern not listed prints `undeclared`, which is the true
# state and not a default.
# --------------------------------------------------------------------------
SEARCH = {
    "p01": ("R3 span OWED",
            "RECAP 'Owed' 3: p01 and p08 owe an in-contract R3-side span"),
    "p03": ("R3 span 1 unreviewed measurement; the +5 constant NEVER searched",
            "RECAP 'Owed' 2"),
    "p08": ("R3 span OWED",
            "RECAP 'Owed' 3"),
    "p10": ("R4 searched at review: -323/-603 becomes -129/-241",
            ".memory/01-ladder.md finding 18 (p10): the rejected R4 candidate "
            "`u_win` verifies 10/0; `R3ship - u_win` is -129.00/-241.00, i.e. "
            "60% of the published margin was R4 SPELLING"),
    "p11": ("R4 chained to the prover; `r4_cstr` inadmissible",
            ".memory/01-ladder.md finding 9 (p11): `r4_cstr` would be "
            "-17 526 Ir/call and its twin is rejected with four "
            "`is not supported`"),
    "p13": ("R4 searched: the SIGN FLIPS to +44/+77",
            ".memory/01-ladder.md finding 14 (p13): a bounded unchecked "
            "consumer verifies 19/0 with no new trusted item and is excluded "
            "by nothing but spec.md's English"),
    "p36": ("BOTH sides searched (4 R3 levers, 3 R4)",
            ".memory/01-ladder.md finding 23 (p36): publishes +7.00 flat "
            "(fixed-R4 bound, cheapest R3 found) and +10.00 flat (matched "
            "pair), never a single number, and NO pair interval"),
    "p47": ("R4 searched, six levers",
            ".tasks/TASK_075.md, from p47's delivery"),
}

LICENCE_NOTE = """\
**The licence is not in the committed records and cannot be derived from them.**
`.memory/03-measurement.md`'s rule -- *"does every cell execute the same work
OUTSIDE the kernel symbol"* -- is a statement about the kernel's callees, and
the only callee information any record carries is `static.bulk_calls`, which is
a **whitelist of recognised bulk routines**.  Measured, on the current records:

* `p11`'s four plain C cells record `bulk_calls: []` while their disassembly
  calls `strlen@plt`, and p11's own headline is a 12.0x glibc-`strlen` library
  factor (RECAP "Owed" 6: the record predates `asm.py`'s `_BULK_STR_WORDS`);
* `p11`'s `safe_tuned` calls `CStr::from_bytes_until_nul` **out of line** and no
  whitelist would ever name it -- that call is worth **+9821.15 Ir/call** and it
  **reverses** p11's `R3-R4` on `small`;
* `p47`'s `c-clang` and `safe_naive` call `bcmp`, which `asm.is_bulk_symbol`
  does not recognise, so the record says their routine lists differ from
  `c-gcc`'s `memcmp` when the pattern's own source says they are the same
  glibc entry point;
* `p09`'s `c-gcc` calls `__popcountdi2` (378.00 / 2625.00 Ir/call) and `p27`'s
  `unsafe` dispatches through `call *%r12`; neither is a bulk routine and
  neither appears anywhere in a record.

So this file reads the licence from `synthesis/licence.json`, emitted by
`synthesis/licence.py` from the built `-O3 isolated` matrix, and it prints
`LICENCE STALE` for any pattern whose gate `source_sha256` has moved since.
Closing this properly is harness work: see `synthesis/README.md`.
"""


def load_measurements():
    out = {}
    for f in sorted(glob.glob(os.path.join(RESULTS, "p*.json"))):
        d = json.load(open(f))
        if "cells" not in d or not isinstance(d.get("inputs"), dict):
            continue                     # side record (p02-residue-sweep)
        out[d["pattern"].split("-")[0]] = d
    return out


def load_gates():
    out = {}
    for f in sorted(glob.glob(os.path.join(GATE, "p*.json"))):
        if f.endswith(".partial.json"):
            continue
        d = json.load(open(f))
        out[d["pattern"].split("-")[0]] = d
    return out


def ir_per_call(d, cell, opt, mode, inp):
    n = d["inputs"].get(inp, {}).get("n_iters")
    for c in d["cells"]:
        if (c["cell"], c["opt"], c["mode"]) != (cell, opt, mode):
            continue
        v = (c.get("ir") or {}).get(inp) or {}
        ke = v.get("kernel_exclusive_ir")
        if ke is None or not n:
            return None
        return ke / n
    return None


def fmt(x, w=11, p=2):
    return f"{x:{w}.{p}f}" if x is not None else f"{'-':>{w}}"


def corrected(outw, pat, lab):
    """`kernel + callees` for this pair, printed ONLY where it differs from the
    kernel-exclusive column -- so a blank cell means "measured, and the callee
    column changes nothing", not "not measured"."""
    p = outw.get(pat) or {}
    cells = []
    for inp in ("small.bin", "large.bin"):
        e = ((p.get(inp) or {}).get("pairs") or {}).get(lab)
        cells.append(None if e is None else (e["kernel_plus_callees"],
                                             e["moves_by"]))
    if all(c is None for c in cells):
        return "not measured"
    if all(c is not None and abs(c[1]) < 5e-3 for c in cells):
        return ""
    out = []
    for c, nm in zip(cells, ("small", "large")):
        if c is None:
            out.append(f"{nm} -")
        elif abs(c[1]) < 5e-3:
            out.append(f"{nm} 0.00")
        else:
            out.append(f"**{nm} {c[0]:+.2f}** ({c[1]:+.2f})")
    return " / ".join(out)


def whole_mode_census(meas):
    """Every -O3 `whole` cell/input pair, and what its kernel column is."""
    none_, kept = 0, []
    for pat, d in meas.items():
        for c in d["cells"]:
            if c["opt"] != "O3" or c["mode"] != "whole":
                continue
            for inp, v in (c.get("ir") or {}).items():
                if v.get("kernel_exclusive_ir") is None:
                    none_ += 1
                else:
                    kept.append((pat, c["cell"], inp,
                                 (v.get("kernel_functions") or ["?"])[0]))
    return none_, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out", default=os.path.join(RESULTS, "synthesis.md"))
    a = ap.parse_args()

    meas, gates = load_measurements(), load_gates()
    lic = json.load(open(LICENCE)) if os.path.exists(LICENCE) else {}
    outw = json.load(open(OUTWARD)) if os.path.exists(OUTWARD) else {}
    L = []
    w = L.append

    w("# Cross-pattern synthesis")
    w("")
    w("Generated by `synthesis/synthesize.py` from **committed records only** "
      "(`results/pNN-*.json`, `results/gate/pNN-*.json`) plus the licence "
      "sidecar. It builds nothing and measures nothing. Re-run it after any "
      "`harness/measure.py --check-stale` that is not `0 STALE`.")
    w("")
    w(f"Patterns: **{len(meas)}**. Gate records: **{len(gates)}**.")
    w("")

    # ---------------------------------------------------------------- limits
    w("## Read these four limits BEFORE the first number")
    w("")
    none_, kept = whole_mode_census(meas)
    w(f"**1. Every number below is `-O3 isolated`, and there is no `whole` "
      f"column to compare it with.** Of the {none_ + len(kept)} `-O3` "
      f"`whole`-mode cell/input pairs in the tree, **{none_} have "
      f"`kernel_exclusive_ir = None`** -- the kernel inlined into `main` and "
      f"left no symbol. That much was already known (RECAP \"Owed\" 13). "
      f"⚠ **What is sharper: all {len(kept)} that DID keep a symbol are "
      f"`kernel.part.0`**, gcc's partial-inlining remnant, and every one of "
      f"them is a `c-gcc` or `c-gcc-h` cell:")
    w("")
    w("```")
    for r in kept:
        w(f"  {r[0]:5s} {r[1]:9s} {r[2]:10s} {r[3]}")
    w("```")
    w("")
    w("So there is **not one `whole`-mode row in the tree** where the kernel "
      "column means what it means in `isolated`: it is a gcc-only column of "
      "*outlined function remainders*. Since p10 showed regressors SWAP "
      "between modes (`.memory/01-ladder.md` finding 18), everything here "
      "speaks for `isolated` and for nothing else.")
    w("")
    w("**2. The column is kernel-EXCLUSIVE, and its licence is stated per "
      "row.** `.memory/03-measurement.md`: the column is comparable only when "
      "the cells being differenced dispatch the *same* work outside the kernel "
      "symbol. `LICENSED` means their outward call sets are equal; "
      "`NOT-LIC` means the difference in this table is **known to be wrong** "
      "and the corrected value is given where it has been measured; "
      "`UNDEC` means a cell dispatches through a pointer with no static "
      "target and the question cannot be settled from the disassembly.")
    w("")
    w("⚠ **And the corrected column is LESS reproducible than the column it "
      "corrects — measured, not argued.** Two independent callgrind sweeps of "
      "the same binaries on the same blobs, differing only in the "
      "`--callgrind-out-file=` path (which is part of *valgrind's* argv and so "
      "shifts the client's stack): **kernel-exclusive `Ir`/call moved in 0 of "
      "348 (pattern, input, cell) triples; outward `Ir`/call moved in 6**, all "
      "±7.00, all glibc `memset` on p03's and p04's `safe_tuned` and `verus` "
      "cells, and the *sign* is not stable (p03 `safe_tuned` +7.00, p04 "
      "`verus` −7.00). `.memory/03-measurement.md` predicts exactly this: "
      "p03's `[0u64; 64]` lowers to a `memset` whose path length moves with "
      "the array's alignment. **So the callee column is an addition to the "
      "kernel-exclusive column and never a replacement for it**, and on p03 "
      "and p04 the kernel-exclusive column is the correct one.")
    w("")
    w("**3. `Ir` is not time, and three named mechanisms make them disagree "
      "in DIRECTION**: `rep`-string instructions counted once per repetition "
      "(p08), a hardware `div` priced at 1 (p05), and a latency-bound chain "
      "(p16). There is no wall-clock column here at all: this box's `ns` floor "
      "is a *session* property, so cross-pattern timing taken across 22 "
      "separate measurement sessions is not a measurement.")
    w("")
    w("**4. gcc's column carries mitigations clang's does not.** gcc defaults "
      "to `-fcf-protection=full`, so every gcc function opens with an "
      "`endbr64` IBT landing pad (`.memory/03-measurement.md`; on p36 that is "
      "`1.00000*nrw + 1` `Ir` per call). **Never attribute a gcc-vs-clang gap "
      "to codegen without naming it.** And two further gcc-only terms this "
      "file found: `__popcountdi2` on p09 (378.00 / 2625.00 `Ir` per call, "
      "libgcc's software popcount, absent from clang) and a 2-instruction PLT "
      "thunk on every gcc libc call (below).")
    w("")
    w("Three standing rules govern every figure: **never the word "
      "\"minimum\"** -- write *cheapest found* and name the input, because on "
      "p03 and p16 the cheapest spelling changes with the blob; **no pair "
      "interval** unless the pattern has an admissible R4 that moves (p03 and "
      "p36 do, and both intervals this project published before that were "
      "built from rungs that do not exist); and **a law owes its domain** -- "
      "glibc's `rep stosb` threshold near `n = 2048` makes `Ir` report a cost "
      "rising 6.5x at the size the real cost falls.")
    w("")

    # ------------------------------------------------------------ levels
    w("## 1. Kernel-exclusive `Ir` per call, `-O3 isolated`")
    w("")
    w("| pattern | input | " + " | ".join(RUNGS) + " |")
    w("|---|---|" + "---:|" * len(RUNGS))
    for pat in sorted(meas):
        d = meas[pat]
        for inp in ("small.bin", "large.bin"):
            vals = [ir_per_call(d, r, "O3", "isolated", inp) for r in RUNGS]
            if vals[RUNGS.index("unsafe")] is None:
                continue
            w(f"| {d['pattern']} | {inp[:-4]} | "
              + " | ".join(fmt(v, 1) for v in vals) + " |")
    w("")

    # ------------------------------------------------------------ differences
    w("## 2. The differences the project argues about -- with their licence")
    w("")
    w(LICENCE_NOTE)
    w("")
    for a_, b_, lab in PAIRS:
        show_search = lab in ("R2-R4", "R3-R4")
        w(f"### `{lab}`  (`{a_}` - `{b_}`)")
        w("")
        w("*`corrected` is blank when the callee column was measured and "
          "changes the difference by 0.00 — blank means measured-and-equal, "
          "not unmeasured. ⚠ On **p03** and **p04** a blank is run-dependent: "
          "their `memset` term is worth ±7.00 and does not reproduce between "
          "sweeps (limit 2).*")
        w("")
        if show_search:
            w("⚠ The last column is the **R3/R4 spelling search state**, and it "
              "is the reason this table cannot be read as a per-pattern "
              "property: see claim 2 in §5.")
            w("")
        w("| pattern | small | large | licence | corrected (kernel+callees)"
          + (" | R3/R4 search state |" if show_search else " |"))
        w("|---|---:|---:|---|---|" + ("---|" if show_search else ""))
        for pat in sorted(meas):
            d = meas[pat]
            v = [None, None]
            for i, inp in enumerate(("small.bin", "large.bin")):
                x = ir_per_call(d, a_, "O3", "isolated", inp)
                y = ir_per_call(d, b_, "O3", "isolated", inp)
                v[i] = None if x is None or y is None else x - y
            if v[0] is None and v[1] is None:
                continue
            pl = (lic.get(pat) or {})
            entry = (pl.get("pairs") or {}).get(lab) or {}
            verd = entry.get("verdict", "no licence recorded")
            if pl.get("gate_source_sha256") and pat in gates and \
                    pl["gate_source_sha256"] != gates[pat].get("source_sha256"):
                verd = "LICENCE STALE"
            corr = corrected(outw, pat, lab)
            s = SEARCH.get(pat)
            w(f"| {d['pattern']} | {fmt(v[0], 1)} | {fmt(v[1], 1)} | {verd} "
              f"| {corr} |"
              + (f" {s[0] if s else 'undeclared'} |" if show_search else ""))
        w("")
        if lab == "gcc-clang":
            w("⚠ **This is the pair in trouble, not `R3-R4`.** 7 of 22 are "
              "`NOT-LICENSED` and 1 more is undecidable — every C-vs-C "
              "statement in the tree runs through this column. Two gcc-only "
              "terms, both measured here and neither previously recorded:")
            w("")
            w("* **`__popcountdi2`, p09** — gcc emits a call to libgcc's "
              "software popcount that clang inlines; **378.00 / 2625.00 "
              "`Ir` per call**, against a published gap of 7322 / 25908. It "
              "is not a bulk routine, so it appears in no record.")
            w("* **a 2-instruction PLT thunk on every gcc libc call.** gcc's "
              "`memcpy@plt` is `endbr64 ; jmp *GOT`, which callgrind "
              "attributes as its own function; clang's is a bare `jmp` and is "
              "folded into the callee. Measured: **+2.00 `Ir` per libc call, "
              "gcc's column only** — p02 `+2.00` (1 call/kernel-call), p12 "
              "`+23.99` (6 × 2.00 + resolution), p11 `+299.87` (150 `strlen` "
              "calls × 2.00), with the libc work itself *identical* "
              "(`strlen` inclusive 2105.0288 gcc / 2105.0265 clang). **One of "
              "the two instructions is the `endbr64` of gcc's default "
              "`-fcf-protection=full`**, so the corrected column carries an "
              "IBT term the kernel-exclusive column never had. It is an "
              "argument for publishing both columns, not for replacing one "
              "with the other.")
            w("")

    # ------------------------------------------------- proof burden and TCB
    w("## 3. Proof burden and trusted base")
    w("")
    w("From `results/gate/*.json` (`verus`, `identity`, `verdict`). "
      "`obligations` is what Verus verified for `verus.rs`; `TCB` counts the "
      "`external_body` / `assume`d items the proof rests on and `TCB lines` "
      "their bodies. **`R4 = R5` identity is the thing the `Ir` column cannot "
      "establish**: quote the digest, not the zero (`.memory/01-ladder.md` "
      "finding 1).")
    w("")
    w("| pattern | obligations | errors | TCB items | TCB lines | "
      "R4=R5 @O3 | verdict |")
    w("|---|---:|---:|---:|---:|---|---|")
    tot_ob = tot_tcb = tot_lines = 0
    for pat in sorted(gates):
        g = gates[pat]
        vb = (g.get("verus") or {}).get("verus.rs") or {}
        items = vb.get("tcb_items") or []
        lines = sum(i.get("body_lines", 0) for i in items)
        lvl = next((e["level"] for e in g.get("identity", [])
                    if e.get("opt") == "O3"), "-")
        tot_ob += vb.get("verified", 0)
        tot_tcb += len(items)
        tot_lines += lines
        w(f"| {g['pattern']} | {vb.get('verified', '-')} | "
          f"{vb.get('errors', '-')} | {len(items)} | {lines} | {lvl} | "
          f"{g.get('verdict', '-')} |")
    w(f"| **total** | **{tot_ob}** | | **{tot_tcb}** | **{tot_lines}** | | |")
    w("")

    # --------------------------------------------------------- static shape
    w("## 4. Static shape, `-O3 isolated`")
    w("")
    w("`n_fn_nopad` is the padding-excluded instruction count of the kernel "
      "symbol at its declared `nm` extent. **A static count is not a cost "
      "model** (`.memory/03-measurement.md`): on the pilot the 32-instruction "
      "gcc kernel executed 125 019 `Ir` where the 37-instruction LLVM one "
      "executed 87 520. It is here as *assembly*, one of `CLAUDE.md`'s five "
      "axes, not as a proxy for work.")
    w("")
    w("| pattern | " + " | ".join(f"{r} n/vec" for r in RUNGS) + " |")
    w("|---|" + "---|" * len(RUNGS))
    for pat in sorted(meas):
        d = meas[pat]
        cs = []
        for r in RUNGS:
            hit = [c for c in d["cells"]
                   if (c["cell"], c["opt"], c["mode"]) == (r, "O3", "isolated")]
            st = (hit[0].get("static") or {}) if hit else {}
            if not st:
                cs.append("-")
            else:
                cs.append(f"{st.get('n_fn_nopad', '?')}"
                          + ("/" + "".join(v[0] for v in st.get("vector_regs", []))
                             if st.get("vector_regs") else ""))
        w(f"| {d['pattern']} | " + " | ".join(cs) + " |")
    w("")

    # --------------------------------------------- the three claims, scored
    w("## 5. The three claims the probe exposed, each scored")
    w("")
    w("`.temp/synth/aggregate.py` produced three provisional, unreviewed "
      "claims (RECAP \"Owed\" 13). They are re-derived here from the records.")
    w("")

    # claim 1
    bad, rows_seen = [], 0
    for pat, d in sorted(meas.items()):
        for inp in ("small.bin", "large.bin"):
            x = ir_per_call(d, "verus", "O3", "isolated", inp)
            y = ir_per_call(d, "unsafe", "O3", "isolated", inp)
            if x is None or y is None:
                continue
            rows_seen += 1
            if x != y:
                bad.append((pat, inp, x - y))
    norel = sorted(p for p, g in gates.items()
                   if any(e.get("opt") == "O3" and e["level"] != "exact"
                          for e in g.get("identity", [])))
    exact = sorted(p for p, g in gates.items()
                   if p not in norel
                   and any(e.get("opt") == "O3" for e in g.get("identity", [])))
    # where the callee column breaks the zero, this sweep
    broke = []
    for pat in sorted(outw):
        for inp in ("small.bin", "large.bin"):
            e = ((outw[pat].get(inp) or {}).get("pairs") or {}).get("R5-R4")
            if e and abs(e["kernel_plus_callees"]) >= 5e-3:
                broke.append(f"{pat} {inp[:-4]} {e['kernel_plus_callees']:+.2f}")
    w(f"**Claim 1 -- `R5 - R4 = 0.00` on every row. SCOPED, and it is a "
      f"TAUTOLOGY rather than a result.** Re-derived: **{len(bad)} of "
      f"{rows_seen}** `-O3 isolated` pattern/input rows differ from 0.00. But "
      f"at `-O3` the gate records `identity: exact` for {len(exact)} patterns "
      f"and `norel` for {len(norel)} ({', '.join(norel)}) -- and *both* levels "
      f"force `Ir` equality: `exact` means the machine code is byte-identical, "
      f"`norel` means it differs only in pc-relative **displacement fields**, "
      f"which cannot change how many instructions execute. **So p36 being "
      f"`norel` explains the row rather than breaking it, and the zero is "
      f"entailed by a check the gate already makes.** Two consequences: the "
      f"evidence for *\"a proof costs zero instructions\"* is the raw-byte "
      f"digest, not this column (`.memory/01-ladder.md` finding 1); and the "
      f"zero is column-specific -- on p16's whole-program **marginal** the "
      f"same pair reads **-1.00**, the driver's.")
    w("")
    if broke:
        w(f"⚠ **And the zero does NOT survive the fix §0 debates.** On the "
          f"kernel+callees column `R5 - R4` is non-zero on "
          f"{len(broke)} rows -- {', '.join(broke)} -- i.e. *\"the proof "
          f"costs -7 instructions\"*, from glibc `memset`'s "
          f"alignment-dependent path length between two byte-identical "
          f"kernels. Which cells carry it changes between sweeps (limit 2).")
        w("")

    # claim 2
    neg = {}
    for pat, d in sorted(meas.items()):
        for inp in ("small.bin", "large.bin"):
            x = ir_per_call(d, "safe_tuned", "O3", "isolated", inp)
            y = ir_per_call(d, "unsafe", "O3", "isolated", inp)
            if x is not None and y is not None and x - y < 0:
                neg.setdefault(pat, []).append((inp[:-4], x - y))
    w(f"**Claim 2 -- `R3 - R4` is negative on {len(neg)} of {len(meas)} "
      f"patterns. CONFIRMED as arithmetic, and the reason it was doubted is "
      f"the WRONG reason.**")
    w("")
    w("| pattern | negative on | licence for `R3-R4` | callee correction | "
      "search state |")
    w("|---|---|---|---|---|")
    for pat in sorted(neg):
        pl = (lic.get(pat) or {}).get("pairs", {}).get("R3-R4", {})
        s = SEARCH.get(pat)
        w(f"| {meas[pat]['pattern']} | "
          + ", ".join(f"{i} {v:.2f}" for i, v in neg[pat]) + " | "
          + pl.get("verdict", "-") + " | "
          + (corrected(outw, pat, "R3-R4") or "no change") + " | "
          + (s[0] if s else "undeclared") + " |")
    w("")
    w("The argument that scheduled this work said the claim rests *\"at its "
      "two biggest numbers, on the column the tree has caught reversing a "
      "comparison three times\"*, naming **p11 and p13** as *\"precisely the "
      "two patterns whose `.memory/` entries already say their rungs dispatch "
      "different work outward\"*.")
    w("")
    w("⚠ **The licence is a property of the PAIR, not of the PATTERN, and "
      "that is the whole defect.** `.memory/03-measurement.md` says of p13, "
      "verbatim: *\"`c-gcc` calls `strlen`; `c-clang` calls `strlen` + "
      "`memcpy` + `memset`; `safe_naive` calls `memset` only; **R3/R4/R5 call "
      "`memcpy` + `memset`**\"* -- R3 and R4 are grouped **together** in the "
      "sentence being cited, and the two figures p13's rule moved are "
      "`gcc-vs-clang` and **`R2 - R4`**. Likewise p11's 12.0x library factor "
      "is C-`strlen` against Rust-`memchr`, an **R1-vs-R3** factor. Measured: "
      "the callee correction to `R3 - R4` is **exactly 0.00** on p10, p12, "
      "p13 and p18, and non-zero only on **p11**, where `small` does reverse "
      "(-5768.00 -> +4053.15) and `large` does not (-24503.00 -> -17378.66).")
    w("")
    w("⚠ **What the claim does NOT survive is the SEARCH objection, which "
      "nobody raised.** `R3 - R4` differences two rungs searched to wildly "
      "different depths, and every time a side has been searched the number "
      "moved a long way: p10's -323/-603 becomes **-129/-241** against a "
      "verifying R4 candidate (60% of the margin was R4 spelling); p13's "
      "-177/-1054 becomes **+44/+77** -- *sign flip* -- against a bounded "
      "unchecked consumer that verifies 19/0 with no new trusted item; p36 "
      "refuses to publish a single number at all. **On this table two of the "
      "five negatives are known to move and three have an undeclared search "
      "state, so the honest reading is that the column is partly measuring "
      "search effort.** That is what the aggregate genuinely adds: it makes an "
      "unsearched R4 side a *systematic* problem instead of a per-pattern "
      "footnote.")
    w("")
    w("**Claim 3 -- a cross-pattern `Ir` comparison is available in "
      "`isolated` mode ONLY. CONFIRMED and SHARPENED** -- see limit 1 above. "
      "The count in RECAP (*\"of 318 `-O3` cell/input pairs, `whole` has "
      "`kernel_exclusive_ir = None` in 302\"*) reads as if 318 were the total; "
      f"it is the `whole`-mode subtotal. Today: {none_ + len(kept)} "
      f"`whole`-mode pairs, {none_} `None`, and the {len(kept)} survivors are "
      "all gcc `kernel.part.0`.")
    w("")

    # ------------------------------------------------------- provenance
    w("## 6. Where the non-derived columns come from")
    w("")
    w("Everything above except two columns is computed from "
      "`results/pNN-*.json` and `results/gate/pNN-*.json`. The exceptions, "
      "with their provenance:")
    w("")
    w("**Licence** — `synthesis/licence.json`, emitted by "
      "`synthesis/licence.py` from the built `-O3 isolated` matrix. Each entry "
      "carries the gate `source_sha256` it was taken against; a mismatch "
      "prints `LICENCE STALE` above instead of a verdict.")
    w("")
    w("**Corrected (kernel+callees)** — `synthesis/outward_ir.json`, emitted "
      "by `synthesis/outward_ir.py`, one callgrind run per cell, parsing the "
      "caller→callee edges the annotation discards.")
    w("")
    w("**R3/R4 search state** — hand-maintained in `synthesize.py::SEARCH`, "
      "because **nothing committed records it**: control registries are "
      "heterogeneous and only 8 of 22 patterns expose a `--list` "
      "(RECAP \"Owed\" 12). Every entry quotes its source, and a pattern with "
      "no entry prints `undeclared`, which is its true state:")
    w("")
    for pat in sorted(SEARCH):
        w(f"- **{pat}** — {SEARCH[pat][0]}  \n  *{SEARCH[pat][1]}*")
    w("")

    txt = "\n".join(L) + "\n"
    if a.stdout:
        sys.stdout.write(txt)
    else:
        open(a.out, "w").write(txt)
        print(f"wrote {os.path.relpath(a.out, REPO)}  ({len(txt)} bytes, "
              f"{len(L)} lines)")


if __name__ == "__main__":
    main()
