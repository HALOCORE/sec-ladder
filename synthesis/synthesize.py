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

WHAT IT READS.  Committed records: `results/pNN-*.json` (measurement) and
`results/gate/pNN-*.json` (gate).  It never builds, never runs a compiled
binary and never writes a record.

⚠ **THE CALLEE CORRECTION IS DERIVED FROM COMMITTED RECORDS** -- see
`CALLEE_NOTE`.  An earlier version of this file printed *"the licence is not in
the committed records and cannot be derived from them"*, which was false:
`results/gate/pNN.json::marginal_ir_per_call` is whole-program and therefore
symbol-independent, so `(marg[A]-marg[B]) - (kex[A]-kex[B])` is the callee
correction, from files already in `git` (TASK_075_REVIEW B1;
`.memory/03-measurement.md`, which prescribed exactly this test).

Three things here are NOT derived from a record, each declared where it prints:

  * the LICENCE TAG (`synthesis/licence.json`) -- a disassembly property, a
    different question from the magnitude, and pinned to the gate
    `source_sha256` it was taken against;
  * the CALIBRATION of the derived column against a callgrind sweep
    (`synthesis/outward_ir.json`) -- evidence for the floor, not a column;
  * the REVIEWED SEARCH VERDICT (`SEARCH_REVIEWED`), beside a *derived* control
    census this file computes by running each pattern's `controls/*.py --list`.
"""
import argparse
import glob
import json
import os
import re
import subprocess
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
# The gate records one `identity` entry per compared pair; p01 ships two at
# `-O3`.  Anything about "the proof costs zero instructions" is about this one.
R5_PAIR = "unsafe vs verus"

# ⚠ **THE SAME PATTERN'S TWO-NESS BITES A SECOND COLUMN, AND THIS PIN IS THE
# DISCLOSURE.**  `§3`'s proof-burden row reads ONE Verus source per pattern.
# The line below used to be a bare `.get("verus.rs")` inline, with no comment,
# no constant and nothing that would notice a second source appearing —
# exactly the shape `R5_PAIR` was introduced for one column earlier
# (TASK_075_REVIEW m6).
#
# **p01 pins TWO Verus sources** and is the only pattern that does (checked
# across all 22 gate records, TASK_084):
#
#     safe_naive_verus.rs   7 verified   TCB ['load_input', 'emit']
#     verus.rs              7 verified   TCB ['get_unchecked', 'load_input', 'emit']
#
# **Reading only `verus.rs` is CORRECT and summing would be wrong**, so this is
# a disclosure, not a repair: `safe_naive_verus.rs` is the R2v control that
# proves the *safe naive* rung panic-free (`.memory/01-ladder.md` finding 2,
# *"a proof alone buys nothing"*).  Its trusted base is not R5's, and adding
# the two would publish a trusted-base size that describes no rung on the
# ladder.  The column is R5's, and `TCB_SRC` says so.
#
# ⚠ **What the silence already cost, measured at TASK_084:** with two
# candidate totals in the tree — 90 over `verus.rs` and 92 over every source —
# four documents quote **92** *as the published total* (`RECAP.md:1798`,
# `.tasks/TASK_082.md:195`, `.tasks/TASK_083.md:26` and
# `.tasks/TASK_083_REVIEW_REPORT.md:268`, the last of them naming this very
# table), while this file has published **90** since it was written.  So the
# table now also emits a DERIVED footnote naming every additional Verus source
# it did not read, per pattern — which is the part that will still work when a
# second pattern grows a second source.
TCB_SRC = "verus.rs"

# --------------------------------------------------------------------------
# The search state.  TWO columns, because neither alone is honest.
#
# `R3 - R4` differences two rungs whose spellings have been searched to wildly
# different depths.  A table that puts a well-searched pattern beside an
# unsearched one and differences both is partly measuring SEARCH EFFORT, and
# the tree has three measured instances of the difference moving a long way
# when a side was finally searched.
#
# ⚠ TASK_075_REVIEW M6 prescribed DELETING the declared table and deriving the
# lever count from `controls/*.py --list` for "the 10 patterns that expose one".
# **MEASURED (`.temp/p76/list_parse_probe.py`): that cannot be done.**  Ten
# patterns expose a `--list` and only FIVE of them print a source file at all:
#
#     from <file>.rs   p10 p47          <- <file>.rs   p03 p04 p12
#     NO source column p06 p09 p22 p36 p38
#
# and p36 -- the pattern the review cited as the worked example -- is in the
# second group: its `--list` prints `r3_hdr4  rust`, the LANGUAGE, not the file.
# Deriving p36's split from the `r3_`/`r4_` NAME PREFIX instead gives 4 R3 and
# **2** R4, while `.memory/01-ladder.md` finding 23 says **3** R4 -- i.e. the
# derivation-by-convention rots in the same direction the hand table does, and
# less visibly.  So: DERIVE what is derivable (`control_census`, below, which
# degrades to "no source attribution" and can never print a wrong count), and
# keep the reviewed verdict beside it with every entry cited to a REVIEWED
# artefact.  A pattern with no entry prints `undeclared`, which is its true
# state and not a default.
# --------------------------------------------------------------------------
SEARCH_REVIEWED = {
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
            "`patterns/p47-ct-compare/NOTES.md` §8e, REVIEWED — \"Six R4 "
            "levers were built, each measured and put through "
            "`./verus_run.py`\" — and §8e's table has six rows: `unsafe` "
            "shipped, `u_base`, `u_winu`, `u_end`, `u_win`, `u_ptr`. "
            "`gen_controls.py --list` registers five `from unsafe.rs`; the "
            "sixth is the shipped rung. ⚠ TASK_075_REVIEW M6.3 read this as "
            "four and called the number unsupported; it is supported, and the "
            "citation — not the figure — was what was wrong"),
}

# The two bands of the derived column, MEASURED rather than asserted
# (`.temp/p76/derived_probe.py`, `.temp/p76/bands.txt`; see `CALLEE_NOTE`):
#   |correction| <  FLOOR      120 rows, ALL spurious -- nothing real hides here
#   FLOOR .. CONFIDENT          22 rows, 8 real / 14 spurious -- a coin flip
#   |correction| >= CONFIDENT   34 rows, ALL real, smallest 17.00
FLOOR = 2.00
CONFIDENT = 16.00

# ---- the ENVIRONMENT-PHASE census, pinned ------------------------------------
# `marginal_ir_per_call` at `-O3 isolated` is not a constant on p03 and p04: a
# per-call `memset` of a stack scratch buffer takes an alignment-dependent tail
# in `__memset_avx2_unaligned_erms`, and the initial stack pointer moves with the
# length of the environment block.  The effect is BISTABLE with a period of 32
# bytes and a window exactly 16 wide, and the phase differs per binary, so a PAIR
# can swing by 14 (`check.py::check_marginal_ir`).
#
# Below: the derived correction `(marg[A]-marg[B]) - (kex[A]-kex[B])` over 32
# consecutive environment lengths -- one full period -- as `value: pads`.
# Instrument `.temp/r98/sweep.py`, data `.temp/r98/{p03,p04}_sweep.json`
# (TASK_098, reviewed; re-derived at TASK_099).  Identical on both blobs.
#
# ⚠ This is a PIN, not a derivation: nothing in `results/` carries a sweep, and
# re-taking it costs ~2 min/pattern -- the instrument is `.temp/r98/sweep.py`,
# and `.memory/03-measurement.md`'s RESOLVED block is the reviewed write-up.
# ⚠ `common/layout/` is the WRONG instrument and fails in the dangerous
# direction: it varies the PROGRAM and measures `ns`, and callgrind is
# layout-blind, so it returns ~0 on a term worth 7.
PHASE_SWEEP = {
    ("p03", "R2-R4"): {0.00: 16, 7.00: 16},
    ("p03", "R3-R4"): {-7.00: 8, 0.00: 16, 7.00: 8},
    ("p03", "R5-R4"): {-8.00: 14, -1.00: 4, 6.00: 14},
    ("p04", "R2-R4"): {0.00: 16, 7.00: 16},
    ("p04", "R3-R4"): {-7.00: 8, 0.00: 16, 7.00: 8},
    ("p04", "R5-R4"): {-8.00: 14, -1.00: 4, 6.00: 14},
}

# ⚠⚠ WITHDRAWN: the pairs where the correction IS the whole published figure.
# R4 and R5 are byte-identical binaries, so the kernel column is exactly 0.00 and
# the printed cell is the correction alone -- there is no large true difference
# for a 7-Ir term to be a rounding error of.  `value` is the part that
# reproduces: `R5-R4 = kernel 0 + memset {-7,0,+7} + main (-1)`, attributed
# symbol by symbol at TASK_098 (`.temp/mgr98/`), so `main`'s -1.00 is all that
# survives the phase.  ⚠ It is the OPPOSITE SIGN to the `+6.00` this file
# published for five tasks.
WITHDRAWN = {
    ("p03", "R5-R4"): (-1.00, "`main` 14 vs 13"),
    ("p04", "R5-R4"): (-1.00, "`main` 14 vs 13"),
}


# ⚠ The SEVENTH exposed cell, and it is neither p03 nor p04.  A 2-pad screen
# over the whole tree (24 patterns x 6 cells x 2 blobs, pad 0 against pad 16,
# `.temp/r98/treescan_{small,large}.json`) moved 14 of 288 triples: p03's and
# p04's three Rust rungs each, AND p46's `c-clang`.  No full period was taken
# for it, so it is marked and not quantified.  ⚠ **"2 patterns, 7 of 144 cells"
# -- in `.memory/03-measurement.md`'s RESOLVED block, `TASK_098_REPORT.md`
# MAJOR 3 and `TASK_099.md` §C -- is arithmetically impossible for that reason:
# the count is THREE patterns.**
PHASE_SCREEN = {
    ("p46", "gcc-clang"):
        "`c-clang`'s marginal moves `6216.00 → 6209.00` (`small`) and "
        "`23230.66 → 23223.66` (`large`) between pad 0 and pad 16, so the "
        "correction carries the same ±7.00 — **2-pad screen only, no full "
        "period taken**. It is 8% of the `-87.00` correction and 0.34% of the "
        "`+2076.00` figure, so nothing here is withdrawn",
}


def _phase_note(pat, lab):
    """`{-8.00: 14, ...}` -> `−8.00 on 14 pads, −1.00 on 4, +6.00 on 14`."""
    if (pat, lab) in PHASE_SCREEN:
        return PHASE_SCREEN[(pat, lab)]
    sup = PHASE_SWEEP[(pat, lab)]
    return ", ".join(f"`{v:+.2f}` on {n}"
                     for v, n in sorted(sup.items())) + " of 32"

BULK_CALLS_NOTE = """\
⚠ **`static.bulk_calls` is a WHITELIST, and on three patterns the record it
produces is wrong about what the cell calls.** This is the one genuinely new
defect the licence work turned up, it is in `harness/`, and it is **not fixed
here** -- reported for the owed `harness/` batch:

* **`asm.is_bulk_symbol('bcmp')` is `False`** (measured), so
  `results/p47-ct-compare.json` records `c-gcc: ['memcmp@plt']`, `c-clang: []`
  and `safe_naive: []` for three cells that call **the same glibc entry point**
  -- both names resolve to address `0x188320`, and p47's own reviewed
  `NOTES.md` says clang rewrites `memcmp(...) == 0` into `bcmp`.
* **`__popcountdi2` is not a bulk name either**, so all eight of p09's cells
  record `[]` while `c-gcc` calls libgcc's software popcount at
  **378.00 / 2625.00 `Ir` per call**.
* **p11's four plain C cells record `[]` while calling `strlen@plt`**, which
  `is_bulk_symbol` *does* recognise -- the record predates `asm.py`'s
  `_BULK_STR_WORDS` and only the two `-h` cells are populated. (RECAP "Owed"
  6's follow-up sentence says p11's `bulk_calls` *are* populated; it is wrong
  as written.)

**And the four "adjacent findings" this work reported are, three of them,
already published by the patterns they name** (TASK_075_REVIEW M5) -- so they
are citation fixes and cost no gate re-run:

| finding | disclosed where |
|---|---|
| p27 `R2-R4`/`R3-R4` understated by `+120.33 / +130.95` | `p27/NOTES.md` §5e, as a **closed** decomposition summing to `+230.0694 / +792.7458` |
| p09's gcc column carries `__popcountdi2`, `378 / 2625` | `p09/NOTES.md` §2: *"Quote `marginal_ir_per_call` for anything involving a gcc cell"* |
| p47's `R2-R4` moves (`bcmp`) | `p47/NOTES.md` §1, "The call targets, resolved by GOT relocation and `nm`" |
| p11's `R3-R4` reverses | `p11/NOTES.md:143`, and the boilerplate in 22 of 22 `results/tables/*.md` |
| **p27's `gcc-clang` reverses on `small`, `-25.02 -> +15.00`** | **new** |

⚠ **And p27's mechanism, as this file first stated it, was wrong.** It said
*"p27's `unsafe` dispatches through `call *%r12`"* was the cause of the
`+120.33`. Measured outward `Ir` on `small`: `unsafe` pays `dealloc 917.33`;
`safe_naive` pays `dealloc 280.93 + drop_glue 756.73`. **The cost is the SAFE
side's out-of-line `drop_glue::<[Option<Box<u8>>; 32]>`**, not the unsafe
side's indirect call -- which is a second call to `__rust_dealloc` already
inside p27's decomposition. `.memory/01-ladder.md` finding 19 had this right
before this file was written and was re-confirmed against it.
*A right answer with a wrong justification propagates exactly like a wrong
answer* (`.memory/03-measurement.md`).
"""

CALLEE_NOTE = """\
**The callee correction below is DERIVED FROM COMMITTED RECORDS.**
`results/gate/pNN.json` carries **`marginal_ir_per_call`** for every
`(cell, opt, mode, input)`. That figure is whole-program -- the `n_iters`
200-minus-100 construction -- and therefore *symbol-independent*, so it already
contains exactly the callee work the kernel-exclusive column drops. For two
cells whose driver is compiled the same way the driver term cancels, and

```
(marg[A] - marg[B]) - (kex[A] - kex[B])   =   the callee correction
```

is computable from files already in `git`. This is `.memory/03-measurement.md`'s
own *"author-checkable test, which needs no disassembly"*, and the same
arithmetic is the generated boilerplate in 22 of 22 `results/tables/*.md`.

⚠ **An earlier version of this file said the opposite** -- *"the licence is not
in the committed records and cannot be derived from them"* -- and scheduled two
sidecars on the strength of it (TASK_075_REVIEW B1). Nothing in the tables moved;
the provenance sentence was the defect.

⚠ **ITS FLOOR IS 2.00 `Ir` AND THAT IS THE ONLY THRESHOLD AT WHICH IT MISSES
NOTHING.** TASK_075_REVIEW B1 and `.memory/03-measurement.md` report *"zero
misses at every threshold (2.0 -> 14 false alarms, 3.0 -> 10, 5.0 -> 9)"*.
Re-measured (`.temp/p76/derived_probe.py`), scoring the oracle at 5e-3 rather
than at the same threshold as the estimate:

| threshold | hit | **miss (false OK)** | false alarm |
|---|---:|---:|---:|
| **2.00 Ir** | 162 | **0** | 14 |
| 3.00 Ir | 164 | **2** | 10 |
| 5.00 Ir | 165 | **2** | 9 |

The review's version scores `truth = |correction| >= threshold`, which excuses
the estimator from finding exactly the corrections it is too coarse to find.
Both misses are `p02 gcc-clang`, both worth exactly **+2.00** -- one libc call
per kernel call through gcc's PLT thunk, and the only true-but-small correction
in the tree. **So this file uses 2.00, and the smallest real correction sits
exactly on it.**

**What the derived column cannot do.** It does not name a callee, and it cannot
resolve the +-7.00 `memset` term or the +2.00 PLT thunk. **Its residual is
structured, not noise**: exactly **+1.00 on 26 of 44 `gcc-clang` rows** and
exactly **-1.00 on 28 of 44 `R5-R4` rows** -- the driver-codegen term, which is
what puts the floor at 2.00 rather than at 0. It is **not** subtracted here; a
fitted correction is not a measurement.

**Where the mechanism comes from instead**: the licence column, which is a
disassembly property with zero run noise and answers a *different* question --
*may this row be differenced at all* -- and names the callee when the answer is
no. The two disagree on p03/p04 `R2-R4` (`LICENSED`, derived +7.00) and that
disagreement **is** the `memset` finding, not a defect in either.

⚠ **And that `+7.00` is one draw of a two-state variable, not a constant**: the
same cell derives `0.00` at half of the 32 environment phases (`‡` below). The
disagreement is real at every phase -- the licence says "differenceable", the
sweep says the callee moves -- but its MAGNITUDE is a phase, so quote the
support, never the draw.
"""



def _n_named(name):
    """How many published `verus.rs` TCB items carry this name. COMPUTED, because
    a hardcoded count in a generated file goes stale the moment a pattern lands
    (TASK_088: the prose said 22 with 23 patterns in the tree)."""
    import json as _j, glob as _g
    n = 0
    for f in _g.glob(os.path.join(REPO, "results", "gate", "*.json")):
        if ".partial" in f:
            continue
        vb = (_j.load(open(f)).get("verus") or {}).get("verus.rs") or {}
        n += sum(1 for i in (vb.get("tcb_items") or []) if i.get("name") == name)
    return n


def _n_verus_rs():
    import glob as _g
    return len(_g.glob(os.path.join(REPO, "patterns", "*", "verus.rs")))


def _n_broadcast():
    import glob as _g
    return sum(1 for f in _g.glob(os.path.join(REPO, "patterns", "*", "verus.rs"))
               if "broadcast use" in open(f).read())

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


def marginal(gates, pat, cell, inp, opt="O3", mode="isolated"):
    """`results/gate/pNN.json::marginal_ir_per_call` -- whole-program, so it
    carries the callee work the kernel-exclusive column drops."""
    m = (gates.get(pat) or {}).get("marginal_ir_per_call") or {}
    return m.get(f"{cell}/{opt}/{mode}/{inp}")


def derived_correction(meas, gates, pat, a_, b_, inp):
    """The callee correction for one pair on one blob, FROM COMMITTED RECORDS.

    `(marg[A] - marg[B]) - (kex[A] - kex[B])`.  Returns `None` when either
    record is missing rather than guessing."""
    ka = ir_per_call(meas[pat], a_, "O3", "isolated", inp) if pat in meas else None
    kb = ir_per_call(meas[pat], b_, "O3", "isolated", inp) if pat in meas else None
    ma, mb = marginal(gates, pat, a_, inp), marginal(gates, pat, b_, inp)
    if None in (ka, kb, ma, mb):
        return None
    return (ma - mb) - (ka - kb)


def derived(meas, gates, pat, a_, b_, lab=None):
    """The `corrected (derived)` cell: the corrected difference with the
    correction in parentheses, on both blobs.  A dash means the derived
    correction is inside the +-2.00 Ir floor, where this route cannot tell it
    from zero -- NOT that the row was not computed.

    ⚠ **Two pairs print no figure at all.**  `WITHDRAWN` above names the cells
    where the correction is a phase of the environment block rather than a
    property of the code, and where it is also the entire published figure.
    They print the measured support and the reproducible term, and they do
    **not** print `**?**`: that marker means *look further*, and there is
    nothing further to look at -- the quantity has no value.  Blanking them was
    the cheaper option and is the wrong one, because in this table BLANK ALREADY
    MEANS SOMETHING ELSE (`|correction| < 2.00`), which is the band this file
    used to call *"safe: nothing real hides below the floor"*."""
    if (pat, lab) in WITHDRAWN:
        val, prov = WITHDRAWN[(pat, lab)]
        return (f"‡ **WITHDRAWN — not a quantity.** Over 32 environment phases "
                f"the correction takes {_phase_note(pat, lab)}, identically on "
                f"both blobs; the published `+6.00` was one draw and is tied "
                f"with its own sign-reverse. Reproducible content "
                f"**{val:+.2f}** ({prov}); the `memset` term "
                f"`{{−7, 0, +7}}` is unresolvable here.")
    out, any_move, any_row = [], False, False
    for inp, nm in (("small.bin", "small"), ("large.bin", "large")):
        c = derived_correction(meas, gates, pat, a_, b_, inp)
        k = ir_per_call(meas[pat], a_, "O3", "isolated", inp)
        k2 = ir_per_call(meas[pat], b_, "O3", "isolated", inp)
        if c is None or k is None or k2 is None:
            out.append(f"{nm} no record")
            continue
        any_row = True
        if abs(c) < FLOOR:
            out.append(f"{nm} <{FLOOR:.2f}")
        elif abs(c) < CONFIDENT:
            any_move = True
            out.append(f"{nm} {k - k2 + c:+.2f} ({c:+.2f}) **?**")
        else:
            any_move = True
            out.append(f"**{nm} {k - k2 + c:+.2f}** ({c:+.2f})")
    if not any_row:
        return "no record"
    s = " / ".join(out) if any_move else ""
    # ...and the same term on a pair where it is NOT the whole figure: mark it,
    # do not withdraw it.  On p03/p04 `R2-R4` the 7.00 rides on a difference of
    # 5110.00, i.e. 0.14% -- but the MARKER is still one draw, since the same
    # cell prints blank at half the phases.
    if (pat, lab) in PHASE_SWEEP or (pat, lab) in PHASE_SCREEN:
        s = (s + " ‡") if s else "‡"
    return s


# --------------------------------------------------------------------- census
_CTL_SRC = re.compile(r"^\s*(\w[\w.]*)\s+(?:from|<-)\s+(\S+)")
_RUNG_OF = {"safe_naive.rs": "R2", "safe_tuned.rs": "R3", "unsafe.rs": "R4",
            "verus.rs": "R5"}


def control_census(pat_dir, timeout=60):
    """DERIVED control census: run every `controls/*.py` that advertises a
    `--list` and count the entries it attributes to each rung's source file.

    It can print three things and never a wrong count: the attribution, or
    `--list, no source attribution`, or `no --list`.  ⚠ Five of the ten
    patterns with a `--list` are in the middle case (p06 p09 p22 p36 p38) --
    which is why this does not replace `SEARCH_REVIEWED`."""
    scripts = [s for s in sorted(glob.glob(os.path.join(pat_dir, "controls",
                                                        "*.py")))
               if "--list" in open(s, errors="replace").read()]
    if not scripts:
        return "no `--list`"
    counts, entries = {}, 0
    for s in scripts:
        try:
            r = subprocess.run([sys.executable, s, "--list"], timeout=timeout,
                               capture_output=True, text=True, cwd=REPO)
        except (subprocess.TimeoutExpired, OSError) as e:
            return f"`--list` failed: {type(e).__name__}"
        if r.returncode != 0:
            return f"`--list` exit {r.returncode}"
        for line in r.stdout.splitlines():
            m = _CTL_SRC.match(line)
            if not m:
                continue
            entries += 1
            k = _RUNG_OF.get(os.path.basename(m.group(2)),
                             os.path.basename(m.group(2)))
            counts[k] = counts.get(k, 0) + 1
    if not counts:
        return "`--list`, **no source attribution**"
    return ", ".join(f"{k} {counts[k]}" for k in sorted(counts))


def calibrate(meas, gates, outw):
    """Score the DERIVED column against the callgrind sidecar, live.

    This is the sidecar's only remaining job in this file: it is the evidence
    for the floor, not a published column.  A `miss` is the dangerous
    direction -- the derived route saying `< floor` where callgrind measured a
    real correction."""
    if not outw:
        return None
    s = {"rows": 0, "hit": 0, "miss": 0, "false alarm": 0}
    # TASK_107 §F: the staleness pin `outward_ir.json` did not have. Same
    # comparison `licence.json` already gets 20 lines below -- the sidecar
    # carries the gate `source_sha256` it was taken against, and a mismatch
    # means its rows describe sources that are no longer in the tree. It was
    # found THREE PATTERNS STALE (22 entries against 25) with nothing able to
    # say so, and `results/synthesis.md` printed the ABSENCE of the pin as a
    # caveat in its own text -- a warning is not a detector.
    s["stale"] = sorted(
        p for p, d in outw.items()
        if isinstance(d, dict) and d.get("gate_source_sha256")
        and p in gates and d["gate_source_sha256"] != gates[p].get("source_sha256"))
    s["unpinned"] = sorted(
        p for p, d in outw.items()
        if isinstance(d, dict) and not d.get("gate_source_sha256"))
    # bands[name] = [rows, real, spurious, smallest |correction| in the band]
    bands = {b: [0, 0, 0, None] for b in ("low", "mid", "high")}
    resid, misses = [], []
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            for a_, b_, lab in PAIRS:
                o = (((outw.get(pat) or {}).get(inp) or {})
                     .get("pairs") or {}).get(lab)
                c = derived_correction(meas, gates, pat, a_, b_, inp)
                if o is None or c is None:
                    continue
                s["rows"] += 1
                resid.append(abs(c - o["moves_by"]))
                pred, truth = abs(c) >= FLOOR, abs(o["moves_by"]) >= 5e-3
                if pred == truth:
                    s["hit"] += 1
                elif truth and not pred:
                    s["miss"] += 1
                    misses.append(f"{pat} {inp[:-4]} {lab} "
                                  f"{o['moves_by']:+.2f}")
                else:
                    s["false alarm"] += 1
                b = bands["low" if abs(c) < FLOOR
                          else "mid" if abs(c) < CONFIDENT else "high"]
                b[0] += 1
                b[1 if truth else 2] += 1
                b[3] = abs(c) if b[3] is None else min(b[3], abs(c))
    resid.sort()
    s["max_resid"] = resid[-1] if resid else None
    s["p95_resid"] = resid[int(.95 * len(resid))] if resid else None
    s["median_resid"] = resid[len(resid) // 2] if resid else None
    s["misses"] = misses
    s["bands"] = bands
    return s


def calibrate_licence(meas, lic, outw):
    """Score the LICENCE TAG against the same sidecar, live.

    `LICENSED` is a prediction that including the callees moves the pair
    difference by 0.00.  ⚠ This is recomputed on every run rather than quoted,
    because the score is a property of the sweep AND of the rule, and the rule
    has been corrected once already (TASK_075_REVIEW M4)."""
    if not outw or not lic:
        return None
    s = {"hit": 0, "false LICENSED": 0, "false alarm": 0, "abstain": 0}
    smallest = None
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            for _, _, lab in PAIRS:
                e = ((lic.get(pat) or {}).get("pairs") or {}).get(lab)
                o = (((outw.get(pat) or {}).get(inp) or {})
                     .get("pairs") or {}).get(lab)
                if e is None or o is None:
                    continue
                moves = abs(o["moves_by"]) >= 5e-3
                v = e["verdict"]
                if v not in ("LICENSED", "NOT-LIC"):
                    s["abstain"] += 1
                    continue
                if v == "NOT-LIC":
                    smallest = (abs(o["moves_by"]) if smallest is None
                                else min(smallest, abs(o["moves_by"])))
                if (v == "LICENSED") != moves:
                    s["hit"] += 1
                elif v == "LICENSED":
                    s["false LICENSED"] += 1
                else:
                    s["false alarm"] += 1
    s["smallest_NOT-LIC_move"] = smallest
    return s


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
    w("Generated by `synthesis/synthesize.py` from **committed records** "
      "(`results/pNN-*.json`, `results/gate/pNN-*.json`). It builds nothing and "
      "measures nothing. Re-run it after any `harness/measure.py --check-stale` "
      "that is not `0 STALE`.")
    w("")
    w("**Both `Ir` columns are derived from those records, including the callee "
      "correction** — see §2. Three things are not, and each says so where it "
      "prints: the **licence tag** (`synthesis/licence.json`, a disassembly "
      "property pinned to the gate `source_sha256`), the **calibration** of the "
      "derived correction against a callgrind sweep "
      "(`synthesis/outward_ir.json`, evidence for a floor rather than a "
      "column), and the **reviewed search verdict**, which prints beside a "
      "control census this file derives by running each pattern's "
      "`controls/*.py --list`.")
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
      "symbol. The licence tag answers **only** that question — *may this row "
      "be differenced* — and never *by how much*; the magnitude is §2's derived "
      "column. Five tags, and **each is a distinct condition**:")
    w("")
    w("| tag | means |")
    w("|---|---|")
    w("| `LICENSED` | the two cells' live outward call multisets are **equal** |")
    w("| `NOT-LIC` | they are not: the difference in this table is **known to "
      "be wrong**, and the `why` under the table names what only one side calls |")
    w("| `UNDEC` | **both** sides dispatch through a pointer with no static "
      "target — a genuine limit of the disassembly |")
    w("| `NO-KSYM` | a cell has **no kernel symbol** (inlined away), so there "
      "is no column to license |")
    w("| `NOT-BUILT` | the `-O3 isolated` binary is **absent** — a tooling "
      "state, not a property of the pattern. **It cannot appear in this "
      "table**: `licence.py --emit` refuses to write a sidecar containing one |")
    w("")
    w("⚠ **The last two used to print as `UNDEC` under this legend's first "
      "sentence** (TASK_075_REVIEW M2). `.temp/build/` is gitignored and "
      "`CLAUDE.md` rule 1 tells agents to delete exactly those blobs, so "
      "re-emitting the licence on a cleaned tree turned all 88 verdicts into "
      "`UNDEC` — and this file republished them under a legend asserting all "
      "88 dispatched through an unresolvable pointer, with nothing failing "
      "anywhere because none of it is gate-checked. Now `--emit` exits **2** "
      "and writes nothing, naming the cells.")
    w("")
    w("⚠ **The callee-inclusive figure is LESS reproducible than the "
      "kernel-exclusive one it corrects — measured, not argued.** Two "
      "independent callgrind sweeps of the same binaries on the same blobs, "
      "differing only in **one added environment variable** "
      "(`SLB_ALIGN_PAD=z*64`, i.e. **+87 bytes** of environment block once the "
      "`envp` slot, the name and the NUL are counted — ⚠ **not +64**, and that "
      "difference is what made someone call this control vacuous; see the "
      "calibration section): **kernel-exclusive `Ir`/call moved in 0 of 348 "
      "(pattern, input, cell) triples; outward `Ir`/call moved in 11** — p03 "
      "and p04 `safe_tuned` on both blobs (`50.00 → 43.00`, glibc `memset`'s "
      "alignment-dependent path length, re-measured at TASK_099) and **p08 on "
      "seven cells** (`+0.0627`/`+0.0676` on `small`, `+0.0065` on `large` "
      "`unsafe`). p08's offset cancels within a language and so moves no "
      "verdict today; p03's and p04's does not.")
    w("")
    w("⚠ **The knob that produced the first version of this paragraph was "
      "INERT.** It said the two sweeps *\"differ only in the "
      "`--callgrind-out-file=` path, which is part of valgrind's argv and so "
      "shifts the client's stack\"*. Valgrind **strips its own options before "
      "building the client stack**: replicating the two paths at their exact "
      "lengths (97 and 99 characters) gives identical kernel-exclusive *and* "
      "identical outward figures. The environment block is the knob that works "
      "(`.memory/03-measurement.md`, `check.py::check_marginal_ir`). ⚠ **This "
      "line used to add *\"and it is scatter, not a trend\"*. That is p08's "
      "behaviour, not p03's and p04's**: theirs is **bistable with a 32-byte "
      "period and a 16-wide window** (`‡`, below), which is why a two-pad "
      "screen 16 apart detects all of it and a single contrast can miss "
      "nothing. The published `6 of 348` was a floor and its exposed-pattern "
      "list was short by one (TASK_075_REVIEW M1). "
      "**So the callee correction is an addition to the kernel-exclusive "
      "column and never a replacement for it**, and on p03 and p04 the "
      "kernel-exclusive column is the correct one.")
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
    w("⚠ **And a per-process constant hiding inside a per-call column, which "
      "is why the thunk rows never read as a clean multiple of 2.00.** A "
      "one-off lazy-binding / IFUNC resolver call (**725–794 `Ir` per "
      "process**, present in clang's and rustc's binaries and not gcc's) is "
      "charged to whichever call site triggers it, and it scales as "
      "`1/n_iters` — **0.0065 … 0.5293 `Ir` per call** across this tree. It is "
      "why p11's thunk term reads `+299.87` where `150 × 2.00 = 300.00`, and "
      "it is the shape `.memory/03-measurement.md` already condemns for `ns`. "
      "The `large`-blob rows are quieter than the `small` ones for the same "
      "reason.")
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
    w("*A `-` is a cell the pattern does not ship, not a missing measurement: "
      "the `-h` columns are the hardened C rungs, and p01 ships none.*")
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
    w(CALLEE_NOTE)
    w("")
    cal = calibrate(meas, gates, outw)
    if cal is None:
        w(f"⚠ **`synthesis/outward_ir.json` is absent, so the bands are "
          f"QUOTED and not recomputed.** Every corrected figure below is still "
          f"present — the derived column needs no sidecar at all. As last "
          f"measured (TASK_076, 176 rows): `<{FLOOR:.2f}` **120 rows, 0 real**; "
          f"`{FLOOR:.2f}–{CONFIDENT:.2f}` **22 rows, 8 real / 14 spurious**; "
          f"`≥{CONFIDENT:.2f}` **34 rows, all real, smallest 17.00**. "
          f"Re-emit the sidecar (`synthesis/outward_ir.py --emit`, ~4m40s) to "
          f"make this line live again.")
    else:
        w(f"**Calibration, recomputed on every run of this file** — the "
          f"derived column scored against `synthesis/outward_ir.json`, a "
          f"callgrind caller→callee sweep, at the {FLOOR:.2f} `Ir` floor: "
          f"**{cal['rows']} rows, {cal['hit']} hit, {cal['miss']} miss "
          f"(the dangerous direction), {cal['false alarm']} false alarm**; "
          f"residual median **{cal['median_resid']:.2f}**, p95 "
          f"**{cal['p95_resid']:.2f}**, max **{cal['max_resid']:.2f}**."
          + (f" ⚠ Misses: {', '.join(cal['misses'])}." if cal["misses"] else ""))
        w("")
        w("**So the column has three bands, and they are measured on every "
          "run rather than chosen** — each row sorted by `|correction|` "
          "against whether the sweep says the row moves at all:")
        w("")
        w("| band | rows | real | spurious | smallest \\|correction\\| | "
          "reading |")
        w("|---|---:|---:|---:|---:|---|")
        for key, lo, hi, mark, read in (
                ("low", None, FLOOR, "blank / `<2.00`",
                 "**not safe — this is one environment phase.** ⚠ See `‡`"),
                ("mid", FLOOR, CONFIDENT, "marked **?**",
                 "**a coin flip — do not quote alone**"),
                ("high", CONFIDENT, None, "**bold**",
                 "**every one is real**")):
            n, real, spur, small = cal["bands"][key]
            rng = (f"< {hi:.2f}" if lo is None
                   else f"≥ {lo:.2f}" if hi is None
                   else f"{lo:.2f} … {hi:.2f}")
            w(f"| `{rng}` ({mark}) | {n} | {real} | {spur} | "
              + (f"{small:.2f}" if small is not None else "-") + f" | {read} |")
        w("")
        w("⚠⚠ **THE `< 2.00` BAND'S OWN CLAIM WAS FALSE, AND THIS IS THE "
          "CORRECTION.** It read *\"safe: nothing real hides below the "
          "floor\"*, scored `0 real / 120 spurious`. Both numbers are right "
          "**about the environment this run was taken in**, and the adjective "
          "was not: **p03's and p04's `R3-R4` correction is `0.00` — blank, in "
          "this band — at 16 of 32 environment phases and `±7.00` at the other "
          "16**, three and a half times the floor. A band scored at one draw "
          "cannot certify the absence of a term that is invisible at that "
          "draw. The rows that carry it are marked `‡` below; the band is "
          "otherwise unchanged and still means *the derived route cannot "
          "resolve this*.")
        w("")
        w("⚠ **The middle band is where p03, p04, p07 and p22 live.** On p03 "
          "and p04 `R5-R4` the derived route was reporting `+6.00`, one draw "
          "from `{−8.00, −1.00, +6.00}` — **tied with its own sign-reverse** — "
          "and those four cells are now **withdrawn** rather than marked "
          "**?**: `?` means *look further*, and there is nothing further to "
          "look at. Treat a surviving **?** as *\"look with the licence or a "
          "callgrind run\"*, never as a figure.")
        w("")
        # TASK_107 §F. This paragraph used to read "⚠ That sidecar is the only
        # thing in this file with no staleness pin", which was true and was a
        # WARNING rather than a DETECTOR -- the sidecar was found three patterns
        # stale (22 entries against 25) with nothing able to report it. It now
        # carries `gate_source_sha256` per pattern, the same key
        # `licence.json` has, and the status is computed on every run.
        if cal["stale"] or cal["unpinned"]:
            w(f"⚠⚠ **`synthesis/outward_ir.json` IS STALE against the gate "
              f"records, so the calibration above is scored partly on rows "
              f"taken against sources that have since moved.**"
              + (f" **STALE: {', '.join(cal['stale'])}.**" if cal["stale"]
                 else "")
              + (f" **No pin at all (emitted before TASK_107): "
                 f"{', '.join(cal['unpinned'])}.**" if cal["unpinned"] else "")
              + f" Re-emit with `synthesis/outward_ir.py --emit "
              f"synthesis/outward_ir.json` against a fully built `.temp/build/` "
              f"(352 callgrind runs), then re-run this file.")
        else:
            w(f"✅ **`synthesis/outward_ir.json` is FRESH** — all "
              f"{len(outw)} entries carry the gate `source_sha256` they were "
              f"taken against and every one still matches (TASK_107 §F; the "
              f"key and the check are copied from `licence.json`, which is why "
              f"`LICENCE STALE` and this line now mean the same thing). It was "
              f"once found **three patterns stale, 22 entries against 25**, "
              f"and this file's own text said the pin did not exist — a "
              f"warning where a detector was wanted. Re-emitting costs 352 "
              f"callgrind runs against a fully built `.temp/build/`, which is "
              f"why it calibrates a column here and no longer **is** one.")
        w("")
        lc = calibrate_licence(meas, lic, outw)
        if lc:
            w(f"**And the LICENCE TAG scored against the same sweep, also "
              f"recomputed here**: **{lc['hit']} hit, "
              f"{lc['false LICENSED']} false `LICENSED` (the dangerous "
              f"direction), {lc['false alarm']} false alarm, "
              f"{lc['abstain']} abstain**. The smallest movement under a "
              f"`NOT-LIC` verdict is "
              f"**{lc['smallest_NOT-LIC_move']:.2f} `Ir`/call**, so "
              f"*0 false alarms* is robust to any tolerance below that and is "
              f"not an artefact of the 5e-3 cut.")
            w("")
            w("⚠ **`0 false alarms` is a statement about this sweep, not about "
              "the rule** (TASK_075_REVIEW M4) — which is why this line is "
              "recomputed rather than quoted. Correcting one thing the rule "
              "got right for a contradicted reason (`kernel.cold`, below) "
              "moved the score from `156 / 10 / 0 / 10` to "
              "`154 / 12 / 0 / 10` **in this task**, by converting p27's "
              "`gcc-clang` from a lucky `NOT-LIC` into an honest false "
              "`LICENSED`. The false-alarm zero survived; the hit count did "
              "not. A second sweep under a **longer environment block** reads "
              "`152 / 14 / 0 / 10`, the excess being p03's and p04's `memset` "
              "term — **so the published triple is one draw and "
              "`0 false alarms` is the part that holds across both of them.**")
            w("")
            w("⚠ **That control was called VACUOUS on an arithmetic slip, and "
              "it is not** (TASK_098 BLOCKER 2, TASK_099 §A2; re-measured "
              "here). The reading was *\"a 64-byte pad is `64 mod 32 == 0`, "
              "i.e. the same alignment phase as pad 0, so the second sweep "
              "could not have moved\"*. But the sweep does not lengthen an "
              "existing variable — `.temp/p75rev/envsweep.py` **adds** one, "
              "`SLB_ALIGN_PAD=z*64`, so the block grows by "
              "`8 (envp slot) + 14 (\"SLB_ALIGN_PAD=\") + 64 + 1 (NUL) = 87` "
              "bytes and `87 mod 32 = 23`. **Measured directly at TASK_099** "
              "(`.temp/t99/a2_phase.py`, one callgrind run per environment): "
              "the block grows by exactly **+87 bytes**, and p03 `safe_tuned`'s "
              "glibc `memset` goes **300129 → 258129 Ir** whole-process, "
              "which is `129 + 50.00*6000` against `129 + 43.00*6000` at "
              "`n_iters = 6000` — **exactly the `50.00 → 43.00` per kernel "
              "call** that this "
              "paragraph is about, reproduced in a different session. **The "
              "control fired.** ⚠ It is still ONE contrast rather than a "
              "period, which is what `‡` is for.")
    w("")
    w(BULK_CALLS_NOTE)
    w("")
    for a_, b_, lab in PAIRS:
        show_search = lab in ("R2-R4", "R3-R4")
        w(f"### `{lab}`  (`{a_}` - `{b_}`)")
        w("")
        w(f"*`corrected (derived)` is blank when **both** blobs' derived "
          f"corrections are inside the ±{FLOOR:.2f} `Ir` floor; a cell marked "
          f"**?** is in the {FLOOR:.2f}–{CONFIDENT:.2f} band and means *look "
          f"further*, not a figure; **bold** is ≥{CONFIDENT:.2f}. The three "
          f"bands are scored above. ⚠ **`‡` marks a cell whose correction is a "
          f"phase of the environment block rather than a property of the "
          f"code** — see the note under the table.*")
        w("")
        if show_search:
            w("⚠ The last column is the **R3/R4 spelling search state**, and it "
              "is the reason this table cannot be read as a per-pattern "
              "property: see claim 2 in §5.")
            w("")
        w("| pattern | small | large | licence | corrected (derived)"
          + (" | R3/R4 search state |" if show_search else " |"))
        w("|---|---:|---:|---|---|" + ("---|" if show_search else ""))
        whys = []
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
            # ⚠ Include LICENSED rows whose `why` carries an UNPRICED warning:
            # p27's `gcc-clang` is exactly the row where a LICENSED verdict is
            # known to be wrong, and dropping its `why` would hide that.
            if entry.get("why") and (verd != "LICENSED"
                                     or "UNPRICED" in entry["why"]):
                whys.append(f"- **{pat}** `{verd}` — {entry['why']}")
            corr = derived(meas, gates, pat, a_, b_, lab)
            s = SEARCH_REVIEWED.get(pat)
            w(f"| {d['pattern']} | {fmt(v[0], 1)} | {fmt(v[1], 1)} | {verd} "
              f"| {corr} |"
              + (f" {s[0] if s else 'undeclared'} |" if show_search else ""))
        w("")
        marked = sorted({p for (p, l) in list(PHASE_SWEEP) + list(PHASE_SCREEN)
                         if l == lab})
        if marked:
            w(f"⚠ **`‡` — the environment-phase term, and it is not noise.** "
              f"The derived correction is a **whole-program** figure, so it "
              f"contains the callees; a per-call `memset` of a **stack** array "
              f"takes an alignment-dependent tail in "
              f"`__memset_avx2_unaligned_erms`, and the initial stack pointer "
              f"moves with the **length of the environment block**. The effect "
              f"is bistable, period **32 bytes**, window exactly **16 wide**, "
              f"and the phase differs per binary — so one rung can sit high "
              f"while another sits low and **a pair swings by 14, not 7**. "
              f"Per row, with its instrument:")
            w("")
            for p in marked:
                src = ("2-pad screen `.temp/r98/treescan_*.json`"
                       if (p, lab) in PHASE_SCREEN
                       else "32-pad sweep `.temp/r98/sweep.py`, one full "
                            "period, both blobs")
                w(f"- **{p}** `{lab}` — {_phase_note(p, lab)} "
                  f"*({src}; TASK_098, reviewed)*"
                  + ("  ⟵ **WITHDRAWN above**"
                     if (p, lab) in WITHDRAWN else ""))
            w("")
            w(f"**The kernel-exclusive columns beside them are immune** — a "
              f"callee is not in a per-function exclusive count, and under the "
              f"same perturbation **0 of 288** (pattern, input, cell) triples "
              f"moved on that column while **14 of 288** marginals did. So "
              f"where the two disagree on "
              f"{', '.join('**' + p + '**' for p in marked)}, **the "
              f"kernel-exclusive column is the one that reproduces** "
              f"(`.memory/03-measurement.md`, "
              f"`check.py::check_marginal_ir`).")
            w("")
        if whys:
            w(f"⚠ **Why each non-`LICENSED` row is not licensed, plus every "
              f"`LICENSED` row carrying an unpriced term** — the `why` string "
              f"`licence.py` recorded. An earlier version of this file printed "
              f"the tag and dropped this, which is how three different "
              f"conditions came to share one tag (limit 2). "
              f"`⚠ UNPRICED` counts **live** `@plt` sites and means the row "
              f"carries gcc's 2-instruction PLT thunk at `+2.00 Ir` per "
              f"*dynamic* libc call — a count no static check can have:")
            w("")
            for x in whys:
                w(x)
            w("")
        if lab == "gcc-clang":
            tags = [((lic.get(p) or {}).get("pairs") or {})
                    .get(lab, {}).get("verdict") for p in sorted(meas)]
            w(f"⚠ **This is the pair in trouble, not `R3-R4`.** "
              f"{tags.count('NOT-LIC')} of {len(meas)} are `NOT-LIC` and "
              f"{tags.count('UNDEC')} more is undecidable — every C-vs-C "
              f"statement in the tree runs through this column. Two gcc-only "
              f"terms, both measured here and neither previously recorded:")
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
            w("⚠ **Two `gcc-clang` verdicts were right for reasons the "
              "measurement contradicts** (TASK_075_REVIEW M4), and the thunk "
              "is what actually carried both. It is a **dynamic** term — "
              "`2.00 × libc calls per kernel call` — and the licence is a "
              "**static** check, so it cannot see it at all.")
            w("")
            w("* **p27** was `NOT-LIC` because *\"only `c-gcc` calls "
              "`kernel.cold`\"*. `kernel.cold`'s entire body is "
              "`call abort@plt` — it executes **zero** times in any accepted "
              "run — **and it matches `measure.py::_sum_rows`'s own kernel "
              "needle** `(?:^|::)kernel(?:$|[^A-Za-z0-9_])`, so if it ever "
              "executed its cost would land *inside* `kernel_exclusive_ir`, "
              "not outside it. It cannot make the column incomparable in "
              "either state. `licence.py` now filters kernel siblings, and "
              "**p27's `gcc-clang` is `LICENSED` — which is an honest false "
              "`LICENSED`**, because the row does move, by `+40.02` = 20 libc "
              "calls × 2.00, all of it thunk.")
            w("* **p47** is `NOT-LIC` on `memcmp@plt` against `bcmp@plt`. With "
              "call counts those are **literally the same address "
              "`0x188320`** — glibc aliases them and p47's own reviewed "
              "`NOTES.md` says clang rewrites `memcmp(...) == 0` into `bcmp` — "
              "and the entire `+7.96` the row moves by is the thunk (4 calls "
              "× 2.00 − the resolver). The verdict is **kept**: a static check "
              "cannot know that two dynamic names resolve to one address, and "
              "an alias whitelist is the shape this check exists to avoid. "
              "But the `why` no longer stands alone.")
            w("")
            w("The `why` strings above now carry an **`⚠ UNPRICED`** clause "
              "wherever a `gcc-clang` pair has an `@plt` call site, whichever "
              "way the verdict went. The call **sites** are static and "
              "countable; the per-call **count** is not.")
            w("")

    # ------------------------------------------------- proof burden and TCB
    w("## 3. Proof burden and trusted base")
    w("")
    w("From `results/gate/*.json` (`verus`, `identity`, `verdict`). "
      f"`obligations` is what Verus verified for `{TCB_SRC}`; `TCB` counts the "
      "`external_body` / `assume`d items the proof rests on and `TCB lines` "
      "their bodies. **`R4 = R5` identity is the thing the `Ir` column cannot "
      "establish**: quote the digest, not the zero (`.memory/01-ladder.md` "
      "finding 1). The `R4=R5 @O3` column is the entry whose `pair` is "
      f"`{R5_PAIR}` — p01 ships **two** `-O3` identity pairs and an earlier "
      "version of this file took whichever came first (TASK_075_REVIEW m6).")
    w("")
    w("⚠ **`axioms` is a SEPARATE column and is deliberately not folded into "
      "`TCB items`, because the two are not the same kind of thing.** A TCB "
      "item is **usually** an `#[verifier::external_body]` wrapper with a body "
      "a reviewer can read and an `ensures` that can be checked against real "
      "Rust semantics. ⚠ **Two corrections, both measured (TASK_084_REVIEW "
      "major 2), because an earlier version of this paragraph overstated "
      "both:** since TASK_084 a bodied `#[verifier::external_fn_specification]` "
      "*also* counts as a TCB item — and `.memory/05-layout.md` records that it "
      "and `assume_specification` are **one mechanism**, so the split between "
      "these two columns is *has a reviewable body*, not *is a different kind "
      "of trust*. And the twin-and-`(a)/(b)/(c)` requirement does NOT cover "
      "every published item: `load_input` and `emit` "
      f"({_n_named('load_input')} and {_n_named('emit')}, one per pattern) are "
      "`external_body` with **no `ensures`**, so `_is_trusted` is "
      "false and nothing is demanded of them. ⚠ **These counts are COMPUTED "
      "from the records every run — an earlier version hardcoded them and went "
      "stale the moment a pattern was added.** An "
      "**axiom** is a hand-written claim about code Verus never compiles: "
      "`assume_specification`, `axiom fn`, `uninterp spec fn`, "
      "`#[verifier::external_trait_specification]`. It has **no body**, so it "
      "adds **0** to `TCB lines`; it adds no verified function, so "
      "`obligations` does not move; it emits no instructions, so `R4=R5 @O3` "
      "does not move; and the form Verus's own error message prints for you "
      "to paste carries **no `requires` and no `ensures` at all**, which "
      "verifies a 1 MiB out-of-bounds read and a null dereference at "
      "`4 verified, 0 errors` (`.memory/04-verus.md`). One column would let a "
      "7-line reviewed wrapper be traded for a zero-line unconditional axiom "
      "**at par**, and nothing in the table would move.")
    w("")
    w("**So the trusted base of a row is `TCB items` + `axioms`, and the "
      "totals below are reported that way rather than summed.** ⚠⚠ **The "
      "`axioms` column counts PATTERN-LOCAL declarations only, and reading `0` "
      "does NOT mean this tree rests on no hand-written axiom — an earlier "
      "version of this paragraph claimed exactly that and it is FALSE "
      "(TASK_084_REVIEW major 2).** All "
      f"**{_n_broadcast()}** of the **{_n_verus_rs()}** `verus.rs` carry "
      "`broadcast use`, and `vstd::slice::group_slice_axioms` alone is six "
      "`broadcast axiom fn`s in the pinned vstd (`vstd/slice.rs:186`); ten also "
      "import `group_array_axioms`, and `lemma_u128_shr_is_div` appears 23 "
      "times. **Every published number here rests on hand-written axioms. They "
      "are vstd's, they are pinned, and they are outside this column by "
      "construction** — a `0` says *this pattern's author wrote none of their "
      "own*, which is a narrower and still worth-having claim. ⚠ **A USED vstd "
      "`assume_specification` declares nothing locally and is invisible here "
      "too** (RECAP \"Owed\" 0, sixth route). The gate has carried "
      "`axiom_decls` per Verus source since TASK_082; nothing published read "
      "it, so a byte-identical regeneration was **not** evidence that nothing "
      "moved (TASK_083_REVIEW major 4).")
    w("")
    w("| pattern | obligations | errors | TCB items | TCB lines | axioms | "
      "R4=R5 @O3 | verdict |")
    w("|---|---:|---:|---:|---:|---:|---|---|")
    tot_ob = tot_tcb = tot_lines = tot_ax = 0
    # ⚠ **THE TOTALS DEDUPE THE `#[path]`-INCLUDED ROWS** (`TASK_084_REVIEW`
    # minor 1). `common/driver.rs` is included by all 23 `verus.rs`, so ONE
    # axiom or ONE trusted item there lands in all 23 records. The per-row `1`
    # is right -- every one of those patterns' binaries executes it -- but the
    # column total then reads 23 for one item, and the prose below tells the
    # reader to quote the total. Distinct key: `(source, name, line)`.
    shared_ax, shared_tcb = set(), {}
    extra_srcs = {}
    for pat in sorted(gates):
        g = gates[pat]
        vall = g.get("verus") or {}
        vb = vall.get(TCB_SRC) or {}
        # R5's trusted base: `verus.rs`'s own items and axioms, plus everything
        # in the files it `#[path]`-includes. The gate keys an included file by
        # its path relative to the repo root and flags it `path_included`
        # (`check.py::_verus_file_list`); an axiom or an `external_body` in
        # `common/driver.rs` is licensed by this pattern's proof and executed by
        # this pattern's binary, so it belongs in this row.
        #
        # ⚠ **`tcb_items` on an included row is TASK_088**, and it is what makes
        # a planted `external_body ... ensures r == 0` in an included module
        # MOVE THIS TABLE. Before it, route J of `TASK_084_REVIEW` shipped green
        # with `grep -c <name> gate.log` == 0 and a byte-identical
        # `synthesis.md`: the gate did not look and this column could not see.
        own_ax = list(vb.get("axiom_decls") or [])
        own_items = list(vb.get("tcb_items") or [])
        inc_ax, inc_items = [], []
        for k, v in sorted(vall.items()):
            if v.get("path_included"):
                inc_ax += [dict(d, src=k) for d in (v.get("axiom_decls") or [])]
                inc_items += [dict(d, src=k) for d in (v.get("tcb_items") or [])]
        ax = own_ax + inc_ax
        items = own_items + inc_items
        lines = sum(i.get("body_lines", 0) for i in items)
        others = {k: v for k, v in sorted(vall.items())
                  if k != TCB_SRC and not v.get("path_included")}
        if others:
            extra_srcs[g["pattern"]] = others
        lvl = next((e["level"] for e in g.get("identity", [])
                    if e.get("opt") == "O3"
                    and e.get("pair") == R5_PAIR), "-")
        tot_ob += vb.get("verified", 0)
        tot_tcb += len(own_items)
        tot_lines += sum(i.get("body_lines", 0) for i in own_items)
        tot_ax += len(own_ax)
        for d in inc_ax:
            shared_ax.add((d.get("src"), d.get("name"), d.get("line")))
        for d in inc_items:
            shared_tcb[(d.get("src"), d.get("name"), d.get("line"))] = \
                d.get("body_lines", 0)
        w(f"| {g['pattern']} | {vb.get('verified', '-')} | "
          f"{vb.get('errors', '-')} | {len(items)} | {lines} | {len(ax)} | "
          f"{lvl} | {g.get('verdict', '-')} |")
    n_shared_ax, n_shared_tcb = len(shared_ax), len(shared_tcb)
    tot_ax += n_shared_ax
    tot_tcb += n_shared_tcb
    tot_lines += sum(shared_tcb.values())
    w(f"| **total** | **{tot_ob}** | | **{tot_tcb}** | **{tot_lines}** | "
      f"**{tot_ax}** | | |")
    w("")
    w(f"**Trusted base, all {len(gates)} rows: {tot_tcb} items ({tot_lines} "
      f"lines) and {tot_ax} axioms.** Quote both numbers; there is no single "
      f"one.")
    w("")
    w(f"⚠ **The totals are DISTINCT counts, not column sums, and the rows are "
      f"not** (`TASK_084_REVIEW` minor 1, fixed at TASK_088). Every pattern's "
      f"`verus.rs` `#[path]`-includes the same `common/driver.rs`, so one "
      f"trusted item or one axiom there is real in every row and would be "
      f"counted {len(gates)} times in a column sum. The rows above add the "
      f"shared file's items because that row's binary executes them; the "
      f"totals add each `(source, name, line)` **once**. Today the shared file "
      f"contributes **{n_shared_tcb} item(s)** and **{n_shared_ax} axiom(s)**, "
      f"so the two agree — the dedupe is measured inert and is here for the "
      f"day it is not.")
    w("")
    # ---- the DERIVED disclosure of every Verus source this table skipped ----
    w(f"*This table reads **one** Verus source per pattern, `{TCB_SRC}` — the "
      "R5 rung's. The list below is derived from the records on every run, so "
      "a pattern that grows a second pinned source announces itself here "
      "instead of being silently dropped.*")
    w("")
    if not extra_srcs:
        w(f"*No pattern pins a Verus source other than `{TCB_SRC}`.*")
    else:
        w("| pattern | other pinned Verus source | obligations | TCB items | "
          "axioms | why it is not in the row above |")
        w("|---|---|---:|---:|---:|---|")
        for pat in sorted(extra_srcs):
            for src, v in sorted(extra_srcs[pat].items()):
                why = ("the **R2v control**: safe Rust carrying the same "
                       "proof, which holds up `.memory/01-ladder.md` finding "
                       "2 (*a proof alone buys nothing*). It is not a rung "
                       "and is not in the measured 6-cell matrix, so its "
                       "trusted base is not R5's and summing the two would "
                       "publish a number describing no rung."
                       if src == "safe_naive_verus.rs" else
                       "**not a known control — this source is unclassified "
                       "and its trusted base is unaccounted for above.**")
                w(f"| {pat} | `{src}` | {v.get('verified', '-')} | "
                  f"{len(v.get('tcb_items') or [])} | "
                  f"{len(v.get('axiom_decls') or [])} | {why} |")
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
    w("*Each cell is `n_fn_nopad`, then `/` and **the first letter of every "
      "entry in the record's `static.vector_regs`**. Every populated entry in "
      "the tree today is `[\"xmm\"]`, so the only suffix that appears is `/x`; "
      "a `/xy` would be `xmm` and `ymm`. No `/` means the record lists no "
      "vector register. A `-` is a cell the pattern does not ship.*")
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
                   if any(e.get("opt") == "O3" and e.get("pair") == R5_PAIR
                          and e["level"] != "exact"
                          for e in g.get("identity", [])))
    exact = sorted(p for p, g in gates.items()
                   if p not in norel
                   and any(e.get("opt") == "O3" and e.get("pair") == R5_PAIR
                           for e in g.get("identity", [])))
    # where the callee correction breaks the zero, DERIVED from the records
    broke = []
    for pat in sorted(meas):
        for inp in ("small.bin", "large.bin"):
            c = derived_correction(meas, gates, pat, "verus", "unsafe", inp)
            k = ir_per_call(meas[pat], "verus", "O3", "isolated", inp)
            k2 = ir_per_call(meas[pat], "unsafe", "O3", "isolated", inp)
            if c is None or k is None or k2 is None or abs(c) < FLOOR:
                continue
            # ⚠ Do NOT reprint a figure §2 withdrew. This list is *which rows
            # clear the floor*, which is still true of them at this phase; the
            # number is what has no value.
            broke.append(f"{pat} {inp[:-4]} "
                         + ("**WITHDRAWN** `‡`" if (pat, "R5-R4") in WITHDRAWN
                            else f"{k - k2 + c:+.2f}"))
    w(f"**Claim 1 -- `R5 - R4 = 0.00` on every row. SCOPED, and it is a "
      f"TAUTOLOGY rather than a result.** Re-derived: **{len(bad)} of "
      f"{rows_seen}** `-O3 isolated` pattern/input rows differ from 0.00. But "
      f"at `-O3` the gate records `identity: exact` for the `{R5_PAIR}` pair "
      f"on {len(exact)} patterns and `norel` for {len(norel)} "
      f"({', '.join(norel)}) -- and *both* levels force `Ir` equality here. "
      f"`exact` means the machine code is byte-identical, so the entailment is "
      f"immediate.")
    w("")
    w("⚠ **`norel` does NOT entail it in general, and this file used to say it "
      "did** (TASK_075_REVIEW m3). `md5_fn_norel` **zeroes branch-displacement "
      "fields**, so `je +0x10` and `je +0x20` normalise to the same digest — a "
      "`norel` pair *can* differ in control flow and therefore in how many "
      "instructions execute. What licenses the claim is a **check on the one "
      f"pattern it applies to**: p36's six differing instruction texts are "
      "five branches at **identical relative offsets** (`+0xa7 +0x64 +0x8d "
      "+0x40 +0x64`) plus one rip-relative `lea` to the dispatch table. So the "
      "zero holds for p36 by inspection, not by entailment.")
    w("")
    w("Two consequences: the evidence for *\"a proof costs zero "
      "instructions\"* is the raw-byte digest, not this column "
      "(`.memory/01-ladder.md` finding 1); and the zero is column-specific -- "
      "on p16's whole-program **marginal** the same pair reads **-1.00**, the "
      "driver's.")
    w("")
    if broke:
        w(f"⚠ **And the zero does NOT survive the callee correction.** On the "
          f"derived callee-corrected column `R5 - R4` clears the "
          f"±{FLOOR:.2f} floor on {len(broke)} rows -- {', '.join(broke)} -- "
          f"i.e. *\"the proof costs instructions\"* between two "
          f"**byte-identical** kernels.")
        w("")
        w(f"**Every one of those rows is in the uncertain "
          f"{FLOOR:.2f}–{CONFIDENT:.2f} band, and the two halves resolve "
          f"differently.** On **p03** and **p04** there is a real term — glibc "
          f"`memset`'s alignment-dependent path length between two "
          f"byte-identical kernels — but **it has no value**: over 32 "
          f"environment phases the correction takes `{{−8.00, −1.00, +6.00}}` "
          f"with support 14 / 4 / 14, so the `+6.00` this file used to print "
          f"was one draw **tied with its own sign-reverse**, and the four "
          f"cells are withdrawn in §2 (`‡`). The part that reproduces is "
          f"`main`'s **−1.00**. On **p02** the sweep measures **0.00**: the "
          f"derived `−2.00` is the driver residual and nothing else. **The "
          f"kernel-exclusive zero is the correct reading on all six**, and on "
          f"p03/p04 it is the only one of the two columns that reproduces at "
          f"all.")
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
    w("| pattern | negative on | licence for `R3-R4` | callee correction "
      "(derived) | search state |")
    w("|---|---|---|---|---|")
    for pat in sorted(neg):
        pl = (lic.get(pat) or {}).get("pairs", {}).get("R3-R4", {})
        s = SEARCH_REVIEWED.get(pat)
        w(f"| {meas[pat]['pattern']} | "
          + ", ".join(f"{i} {v:.2f}" for i, v in neg[pat]) + " | "
          + pl.get("verdict", "-") + " | "
          + (derived(meas, gates, pat, "safe_tuned", "unsafe", "R3-R4")
             or f"inside the ±{FLOOR:.2f} floor") + " | "
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
      "is C-`strlen` against Rust-`memchr`, an **R1-vs-R3** factor.")
    w("")
    w("Derived from committed records, by the arithmetic at the top of this "
      "section — **no disassembly, no callgrind, no sidecar**:")
    w("")
    w("```")
    w(f"{'':5s} {'':6s} {'kernel-excl':>12s} {'correction':>12s} "
      f"{'corrected':>12s}")
    for pat in ("p10", "p11", "p12", "p13", "p18"):
        for inp in ("small.bin", "large.bin"):
            c = derived_correction(meas, gates, pat, "safe_tuned", "unsafe", inp)
            k = ir_per_call(meas[pat], "safe_tuned", "O3", "isolated", inp)
            k2 = ir_per_call(meas[pat], "unsafe", "O3", "isolated", inp)
            if c is None or k is None or k2 is None:
                continue
            w(f"{pat:5s} {inp[:-4]:6s} {k - k2:12.2f} {c:12.2f} "
              f"{k - k2 + c:12.2f}"
              + ("   <- SIGN FLIPS" if (k - k2) * (k - k2 + c) < 0 else ""))
    w("```")
    w("")
    w("**Four of the five named patterns are unaffected, exactly.** Only "
      "**p11** moves, and only its `small` row reverses. The independent "
      "callgrind sweep puts p11's correction at `+9821.15 / +7124.34` against "
      "the derived `+9815.56 / +7116.78` — 0.06% and 0.11% apart, which is the "
      "one-off resolver term (limit 4) that the marginal construction cancels "
      "and the single-run figure does not. **So the defect is real and it is "
      "ONE pattern, not five**, and the pattern the argument called *\"the one "
      "that established the rule\"* (p13) is a clean 0.00 on both blobs by both "
      "routes.")
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
    w("**Both `Ir` columns above are derived from committed records**, "
      "including the callee correction (§2). Three things are not:")
    w("")
    w("**Licence tag and `why`** — `synthesis/licence.json`, emitted by "
      "`synthesis/licence.py` from the built `-O3 isolated` matrix. Each entry "
      "carries the gate `source_sha256` it was taken against; a mismatch "
      "prints `LICENCE STALE` above instead of a verdict. It answers *may this "
      "row be differenced*, never *by how much* — a different question from "
      "the derived column, not a second route to it.")
    w("")
    w("**Calibration of the derived column** — `synthesis/outward_ir.json`, "
      "emitted by `synthesis/outward_ir.py`, one callgrind run per cell, "
      "parsing the caller→callee edges the annotation discards. It is scored "
      "against the derived column on every run of this file (§2) and supplies "
      "**no published figure**. ⚠ Until TASK_107 it carried **no staleness pin "
      "at all**; it now carries the gate `source_sha256` per pattern, the same "
      "key `licence.json` uses, and §2 prints its status on every run. It "
      "stays a calibration rather than a column because re-emitting it needs "
      "352 callgrind runs against a fully built `.temp/build/`.")
    w("")
    w("**R3/R4 search state** — two things side by side, because neither alone "
      "is honest.")
    w("")
    w("*Derived*, by running each pattern's `controls/*.py --list` (this is "
      "the only place this file executes anything, and it executes committed "
      "Python, never a compiled binary):")
    w("")
    w("| pattern | controls registered, by source file |")
    w("|---|---|")
    for pat in sorted(meas):
        pdir = os.path.join(REPO, "patterns", meas[pat]["pattern"])
        w(f"| {pat} | {control_census(pdir)} |")
    w("")
    w("⚠ **TASK_075_REVIEW M6 prescribed deriving the lever count this way for "
      "\"the 10 patterns that expose a `--list`\" and deleting the declared "
      "table. Measured, that cannot be done.** Ten patterns expose a `--list` "
      "and **five of them print no source file at all** (p06 p09 p22 p36 p38); "
      "the other five split two ways (`from x.rs` on p10 and p47, `<- x.rs` on "
      "p03, p04 and p12). **p36 — the review's own worked example — is in the "
      "first group**: its `--list` prints `r3_hdr4  rust`, the *language*. "
      "Deriving p36's split from the `r3_`/`r4_` **name prefix** instead gives "
      "4 R3 and **2** R4, while `.memory/01-ladder.md` finding 23 says **3** "
      "R4 — so the derivation-by-convention rots in the same direction the "
      "hand table does and less visibly. The census above is therefore built "
      "to degrade to *\"no source attribution\"* rather than to a wrong count.")
    w("")
    w("*Declared*, in `synthesize.py::SEARCH_REVIEWED`, every entry cited to a "
      "**reviewed** artefact. A pattern with no entry prints `undeclared`, "
      "which is its true state:")
    w("")
    for pat in sorted(SEARCH_REVIEWED):
        w(f"- **{pat}** — {SEARCH_REVIEWED[pat][0]}  \n  "
          f"*{SEARCH_REVIEWED[pat][1]}*")
    w("")
    w("⚠ **Three corrections to this section's own provenance, and the "
      "paragraph that carried them predicted exactly this rot** "
      "(TASK_075_REVIEW M6, two of whose three items do not survive "
      "re-checking):")
    w("")
    w("1. **`8 of 22` was wrong and is gone.** RECAP records *\"8 of **20** "
      "patterns have a `--list`\"*, from when the tree had 20 patterns; the "
      "synthesis re-based the denominator to 22 and did not recount the "
      "numerator. Measured: `grep -l -- '--list' patterns/*/controls/*.py` is "
      "**11 files across 10 patterns** (p03 p04 p06 p09 p10 p12 p22 p36 p38 "
      "p47). The table above now derives it instead of quoting it.")
    w("2. **The `RECAP \"Owed\" 12` citation was RIGHT and the review's "
      "correction to it is wrong.** RECAP item 12 spans `RECAP.md:1808-1863` "
      "(item 13 opens at `:1864`) and the `--list` census at `:1847-1852` is "
      "inside it. RECAP \"Owed\" **6** is the `source_sha256` item, whose tail "
      "is the p11 `bulk_calls` sentence — which is a *different* citation this "
      "file also makes, correctly. The two were swapped.")
    w("3. **`p47`'s \"six levers\" checks out, and its citation did not.** "
      "The figure was cited to `.tasks/TASK_075.md`, unreviewed manager prose, "
      "and that was the defect. The number is supported by "
      "`patterns/p47-ct-compare/NOTES.md` §8e — *\"Six R4 levers were "
      "built\"*, a six-row table — and `gen_controls.py --list` registers five "
      "`from unsafe.rs`, the sixth being the shipped rung. TASK_075_REVIEW "
      "M6.3 counted the four non-baseline rows and called the figure "
      "unsupported.")
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
