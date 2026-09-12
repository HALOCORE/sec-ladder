#!/usr/bin/env python3
"""ph45 control -- **THE IN-CONTRACT SPELLING SPAN. NEITHER ENDPOINT IS
DEGENERATE, AND A1 CANNOT SEE ANY OF IT.**

    python3 patterns-php/ph45-htmlent-cache-int/controls/spellings.py --audit-only
    python3 patterns-php/ph45-htmlent-cache-int/controls/spellings.py --verus

⚠⚠⚠ **RUN IT WITH `--verus` OR ITS R4 COLUMN MEANS NOTHING.** An R4 respelling is
a RUNG CANDIDATE only if it has a Verus twin that VERIFIES. Without the flag this
file refuses to certify and says so in `problems` (`TASK_PHP_024` §1.6
demonstrated live on `ph07` what a sidecar that looks complete and is not does to
a later reader).

⚠⚠ **AND ON THIS ROW THAT IS THE WHOLE BAR, WHICH IS NOT TRUE OF `ph29`.**
`ph29`'s copy of this file requires a twin that verifies **AND** compiles to a
byte-identical `kernel`, because `ph29` pins `identity: unsafe == verus, O3
exact`. **`ph45` pins `differ` at BOTH levels and the gate MEASURES `differ`**
(`../spec.md` `identity`; `results-php/gate/ph45-htmlent-cache-int.json`
`identity[].level`), so byte-identity is **recorded here as information and is
not a bar**. `identity_premise()` below reads both sources and `admissibility()`
is a function of what it finds -- so if a later edit ever made this row `exact`,
this file's rule tightens with it instead of silently staying loose.

⚠ The shared `why` block in `../spec.md` argues R4 admissibility from *"All six
patterns pin `identity: unsafe == verus, O3 exact`"*. **That antecedent is false
on this row** -- it is PAT-side boilerplate (`RECAP_PHP.md` F82, open item 61).
This file does not edit it; it reads the pin and the record instead.

WHAT THIS ROW'S SEARCH FOUND, AND IT IS A THIRD ANSWER
------------------------------------------------------
`ph07` and `ph16` searched their R4 side and found it **DEGENERATE**. `ph29`'s
**moved** (F77). ⭐ **On `ph45` BOTH SIDES MOVE, and the shipped ordering
REVERSES**: the row publishes `R3ship - R4ship` with R3 cheaper, and under the
cheapest spelling found on each side R4 is cheaper. **Neither published endpoint
is a searched endpoint.**

⚠⚠⚠ **AND THE SINGLE MOST IMPORTANT THING IN THIS FILE IS A NEGATIVE RESULT
ABOUT THE ROW'S OWN HEADLINE STATISTIC.** `../NOTES.md` §8a: `kernel_exclusive_ir`
sees **9.5 %** of this row, because `dec` is a separate symbol carrying ~90 % of
every rung's instructions. **Every lever below lives in `dec`. So A1 reports
EVERY variant on a side as EXACTLY `0.00 %` against that side's shipped rung,
with an identical `kernel` fingerprint -- while the whole-program figure moves
over a 70-point range.** ▶ **A control that priced this row in A1 alone would
report BOTH endpoints degenerate, and it would be wrong for a reason that has
nothing to do with Rust.** That is why `headline_statistic` here is
`ir_per_call_small_wholeprogram` and not `ir_per_call_small`, and why both are
printed for every variant.

⚠⚠ **AND IT STILL DOES NOT RE-SHIP EITHER RUNG.** `.memory/02-bench-rules.md`
holds the shipped rungs fixed by fiat -- chosen by IDIOM, before measurement --
and that fiat is exactly what makes `R3ship - R4ship` a BOUND. What a cheaper
in-contract spelling moves is what the bound may be CALLED, not which program
ships. Two numbers ship, labelled, in each family:

    fixed-R4 bound   R3ship - R4ship      both endpoints held by fiat
    R3-side span     cheapest-found to dearest-found in contract, named

and **NO PAIR INTERVAL**: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts
that construction in terms and this file does not resurrect it.

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of.

R3 side, from `../safe_tuned.rs` -- all safe, no `unsafe` token:

  `v0_shipped`       the shipped R3, unmodified.
  `r3_subslice`      ⭐⭐ THE ONE THAT REFUTES THE ROW'S OWN STATED MECHANISM.
                     `../safe_tuned.rs`'s header says the lever is that *"the
                     bound LLVM gets free from the TYPE is worth more than the
                     check it removes"*. This variant changes **only the type** --
                     a plain `&[u8]` sub-slice of the same bytes at the same
                     place, no conversion -- and it is a **TIE**. So the lever is
                     the HOIST of the work-buffer base out of the 251-entity
                     scan, not the fixed-size type. Measured three times
                     independently: here, on `r4_buf_slice` vs `r4_buf_array`
                     (identical to the instruction), and in `.temp/php37/`.
  `r3_arena_index`   R2's own spelling: no hoist at all, `ctx.arena[buffer+1+j]`
                     inside the compare loop. ⚠ A CALIBRATION LOSER, kept on
                     purpose: a spelling search with no losing entry is a search
                     nobody can calibrate.
  `r3_namecmp_fn`    ⭐ the compare lifted into a forced-inline helper over the
                     hoisted `&[u8]`. **Cheaper than the shipped R3**, so the R3
                     side of this row was unsearched too.

R4 side, from `../unsafe.rs`, and **each one's substitution is applied to
`../verus.rs` as well and the result is put through Verus**:

  `v0_shipped`       the shipped R4, unmodified.
  `r4_buf_slice`     `name_eq` takes the work buffer as a hoisted `&[u8]` and
                     reads it with a CHECKED index instead of `bget`, so TWO of
                     the row's twelve unchecked dereference call sites go away.
                     ⚠ The twelve is MEASURED per variant into
                     `trusted_call_sites` below, not asserted -- `../unsafe.rs`'s
                     header says *"eleven"* and means `dec`'s own, while the rung
                     as a whole has twelve counted with the two accessor
                     definitions excluded. ⚠ DEARER without the inline hint, and
                     that is the point of shipping it beside the next entry: the
                     hoist alone is not the win.
  `r4_buf_slice_inline`
                     ⭐⭐ **THE CANDIDATE THIS ROW TURNED ON.** The same, plus
                     `#[inline(always)]` on the helper. **Cheaper than the
                     shipped R4 and cheaper than the shipped R3**, with a twin
                     that verifies at the shipped rung's own count and **two
                     fewer trusted call sites**. ⚠ The 40-point swing between
                     this and the entry above is ONE ATTRIBUTE, which is stated
                     rather than hidden: see THE HONEST CAVEAT below.
  `r4_buf_array`     the same lever with `&[u8; REQ]` and `try_into`, which is
                     `../safe_tuned.rs`'s own spelling. ⚠ EXPECTED INADMISSIBLE
                     and priced anyway: `core::array::TryFromSliceError` is
                     `is not supported` at the pinned vstd. **Stage 4 reproduces
                     that error text rather than inheriting a claim of it.**
                     ⭐ Its exec cost is identical to `r4_buf_slice`'s **to the
                     instruction**, which is the second of the three measurements
                     refuting the type mechanism.
  `r4_mirror_unchecked`
                     ⭐⭐ **THE MIRROR CONTROL, AND IT IS WHAT SETTLES THE ROW.**
                     `r4_buf_slice_inline`'s shape exactly -- same signature,
                     same hoist, same inline hint -- with the arena reads left
                     as `bget`, i.e. `get_unchecked`. **It is far DEARER than the
                     checked spelling.** So on this row, in this loop shape, the
                     bounds-checked index is not merely free: the unchecked one
                     is the expensive spelling, because reading through the whole
                     arena at a computed offset is what blocks the hoist.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**. A variant
    nobody audited is a number about a different benchmark.
    ⚠ A `forbidden` hit DISQUALIFIES; a `required` miss is REPORTED and does not.
    That is `check.py`'s own semantics and not a stricter invention: this row's
    three `required` Rust pins are present in all four Rust rungs, and its three
    `required` C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN -- the
    shipped gate record carries those three absences and calls the row
    `PASS-WITH-BLOCKED-ROWS`.
    ⚠ `admissible` is THREE-VALUED. The token audit decides what a grep can
    decide; the third value is a sentence, and `english_verdict` below is where a
    variant carries one. **Exactly one variant uses it and it is declared, not
    inferred.**
  * every variant prints the SHIPPED checksum on every one of the eight inputs,
    adversarial included. A respelling that changed the answer is not one. ⚠ The
    reference is **R3 `v0_shipped`** and not each side's own shipped rung,
    because this row pins all four Rust rungs to one checksum per input.
  * ⚠⚠ **BOTH FAMILIES, from ONE callgrind run per (variant, input).**
    **A1** is `kernel_exclusive_ir` off the pinned callgrind with
    `measure.py::_sum_rows` **IMPORTED and never transcribed** (`TASK_PHP_022`
    §3.2 measured that the transcription was a different function and produced a
    PLAUSIBLE WRONG NUMBER rather than an error). **W1** is
    `callgrind_annotate`'s own `PROGRAM TOTALS` line, which is the column
    `../NOTES.md` §8b publishes as *"whole-program `Ir`"*.
  * stage 3 reproduces the SHIPPED cells in BOTH families before any variant is
    quoted: A1 against `results-php/ph45-htmlent-cache-int.json`, W1 against
    `../NOTES.md` §8b's published totals (`SHIPPED_WP` below).
  * ⚠⚠ stage 4 puts every R4 twin through Verus and reads the ERROR TEXT.
    `is not supported` DISQUALIFIES; `postcondition not satisfied` does not.
    Byte-identity of the twin's `kernel` is RECORDED and, on this row, is not a
    bar -- `identity_premise()` is what decides that, from the pin and the record.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**

⚠⚠⚠ THE HONEST CAVEAT, AND IT IS LARGE ON THIS ROW
---------------------------------------------------
**Inlining is an LLVM heuristic and on this row it is worth more than anything
else measured here.** `r4_buf_slice` and `r4_buf_slice_inline` differ by one
attribute and by roughly forty percentage points; `#[inline(always)]` applied to
the SHIPPED `name_eq`, without the hoist, is a **pessimisation**
(`.temp/php37/explore2.log`). So the two levers are not separable and neither is
a property of Rust: **every number in this file is about `rustc 1.97.1` /
`LLVM 22.1.6` on this box.** ▶ The honest claim is *"an admissible cheaper R4
exists"*, never *"this is the cheapest"* -- **R4 searched is not R4 exhausted**,
and nine spellings are what was tried. `.temp/php37/explore*.log` carries seven
more that were priced and dropped before any twin was written for them.

⚠ `kernel_fingerprint` HERE IS `ph29`'s GUARDED COPY, NOT `ph16`'s. `ph16`'s
ignores objdump's return code, so a binary that does not exist disassembles to
nothing and fingerprints as `(0, 'd41d8cd98f00')`, the md5 of the empty string --
**two such compare IDENTICAL** -- and its symbol needle is a bare substring, so a
crate named `nokernel` fingerprints its own `main`. Both were found by `ph29`'s
own must-fire negatives (F79) and both are guarded here. `ph16` is NOT edited
(open item 57). This file's negatives are `.temp/php37/negatives_spellings.py`.
"""

import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(PDIR, "..", ".."))
SCRATCH = os.path.join(REPO, ".temp", "php37", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph45-htmlent-cache-int.json")
GATE_RECORD = os.path.join(REPO, "results-php", "gate",
                           "ph45-htmlent-cache-int.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph45-htmlent-cache-int.json`
#: carries and therefore what `../NOTES.md` §8 quotes.
PROBES = (("small.bin", 560, 1_500), ("large.bin", 4086, 200))
#: Below this, two cells are a TIE and neither is "cheaper".
TIE_PCT = 0.05
#: Only these two sides can move a published rung number; anything else is a
#: control by construction.
RUNG_SIDES = ("R3", "R4")
#: ⚠ The whole-program totals `../NOTES.md` §8b publishes, O3/isolated, which
#: stage 3 reproduces. They are NOT in any `results-php/` record --
#: `measure.py::callgrind_ir` keeps two EXCLUSIVE needles and no program total --
#: so this is the one figure here that is pinned to a committed document rather
#: than to a committed JSON. `../NOTES.md` is in this row's GATE digest, so a
#: change to it cannot go unnoticed.
#: ⚠⚠ A ±0.5 % tolerance, not equality: `.memory-php/03-numbers.md` records that
#: no two php runs are comparable to the digit unless the invoking shell matches,
#: and the measured drift here is ~300 Ir in 82 M (0.0004 %).
SHIPPED_WP = {("safe_tuned", "small.bin"): 79_512_064,
              ("unsafe", "small.bin"): 82_019_981}


# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]}, english_verdict)
# `file` is "rs" for the rung source and "verus" for the R5 twin.

# ======== R3, from ../safe_tuned.rs ==========================================
_S_LEVER = """            let b: &[u8; REQ] = (&ctx.arena[buffer..buffer + REQ])
                .try_into()
                .unwrap();
"""
_S_LEVER_SUB = "            let b: &[u8] = &ctx.arena[buffer..buffer + REQ];\n"
_S_SCAN = """            let mut i = 0usize;
            while i < ENT.len() {
                let nm: &[u8] = ENT[i].name;
                let n: usize = nm.len();
                if n + 2 > REQ {
                    i += 1;
                    continue;
                }
                let mut j = 0usize;
                let mut eq = true;
                while j < n {
                    if b[1 + j] != nm[j] {
                        eq = false;
                        break;
                    }
                    j += 1;
                }
                if eq && b[1 + n] == 0 {
                    ent = ENT[i].code;
                    break;
                }
                i += 1;
            }
"""
_S_SCAN_ARENA = """            let mut i = 0usize;
            while i < ENT.len() {
                let nm: &[u8] = ENT[i].name;
                let n: usize = nm.len();
                if n + 2 > REQ {
                    i += 1;
                    continue;
                }
                let mut j = 0usize;
                let mut eq = true;
                while j < n {
                    if ctx.arena[buffer + 1 + j] != nm[j] {
                        eq = false;
                        break;
                    }
                    j += 1;
                }
                if eq && ctx.arena[buffer + 1 + n] == 0 {
                    ent = ENT[i].code;
                    break;
                }
                i += 1;
            }
"""
_S_SCAN_FN = """            let mut i = 0usize;
            while i < ENT.len() {
                if namecmp(b, ENT[i].name) {
                    ent = ENT[i].code;
                    break;
                }
                i += 1;
            }
"""
_S_ANCHOR_FN = "fn is_entity_char"
_S_NAMECMP = """#[inline(always)]
fn namecmp(b: &[u8], name: &[u8]) -> bool {
    let n: usize = name.len();
    if n + 2 > REQ {
        return false;
    }
    let mut i: usize = 0;
    while i < n {
        if b[1 + i] != name[i] {
            return false;
        }
        i = i + 1;
    }
    b[1 + n] == 0
}

fn is_entity_char"""

# ======== R4, from ../unsafe.rs ==============================================
_U_NE = """fn name_eq(ctx: &Ctx, buffer: usize, name: &[u8]) -> bool {
    let n: usize = name.len();
    if n + 2 > REQ {
        return false;
    }
    let mut i: usize = 0;
    while i < n {
        if bget(&ctx.arena, buffer + 1 + i) != name[i] {
            return false;
        }
        i = i + 1;
    }
    bget(&ctx.arena, buffer + 1 + n) == 0
}
"""


def _u_ne(attr, body_checked, btype="&[u8]"):
    """`name_eq`'s exec replacement: the signature gains the hoisted buffer.

    ⚠ `let _ = (ctx, buffer);` is in the EXEC substitution and NOT in the twin's,
    because in `../verus.rs` both are live -- they appear in the `requires`, the
    `ensures` and the loop invariant. It is a no-op at codegen and it is here so
    that the exec rung compiles without an unused-variable diagnostic while
    keeping the SAME signature and the SAME call site as the twin."""
    read = ("b[1 + i]" if body_checked else "bget(&ctx.arena, buffer + 1 + i)")
    tail = ("b[1 + n] == 0" if body_checked
            else "bget(&ctx.arena, buffer + 1 + n) == 0")
    return (attr + "fn name_eq(ctx: &Ctx, b: " + btype
            + ", buffer: usize, name: &[u8]) -> bool {\n"
            "    let _ = (ctx, buffer, b);\n"
            "    let n: usize = name.len();\n"
            "    if n + 2 > REQ {\n"
            "        return false;\n"
            "    }\n"
            "    let mut i: usize = 0;\n"
            "    while i < n {\n"
            "        if " + read + " != name[i] {\n"
            "            return false;\n"
            "        }\n"
            "        i = i + 1;\n"
            "    }\n"
            "    " + tail + "\n"
            "}\n")


_U_SCAN = """            let tbl: &[Ent] = ent_table();
            let mut i: usize = 0;
            while i < tbl.len() {
                if name_eq(ctx, buffer, tbl[i].name) {
"""
_U_SCAN_SUB = """            let tbl: &[Ent] = ent_table();
            let b: &[u8] = &ctx.arena[buffer..buffer + REQ];
            let mut i: usize = 0;
            while i < tbl.len() {
                if name_eq(ctx, b, buffer, tbl[i].name) {
"""
_U_SCAN_ARR = """            let tbl: &[Ent] = ent_table();
            let b: &[u8; REQ] = (&ctx.arena[buffer..buffer + REQ]).try_into().unwrap();
            let mut i: usize = 0;
            while i < tbl.len() {
                if name_eq(ctx, b, buffer, tbl[i].name) {
"""
_U_DRIVER = '#[path = "../../common/driver.rs"]'
_U_TRYINTO = "use std::convert::TryInto;\n" + _U_DRIVER

# ======== R4's twin, from ../verus.rs ========================================
_V_NE = """fn name_eq(ctx: &Ctx, buffer: usize, name: &[u8]) -> (r: bool)
    requires
        wf_c(*ctx),
        buffer + BLOCK <= ASZ,
    ensures
        r == s_name_eq(ctx.arena@, buffer as int, name@),
{
    let n: usize = name.len();
    if n > REQ - 2 {
        return false;
    }
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n + 2 <= REQ,
            buffer + BLOCK <= ASZ,
            ctx.arena@.len() == ASZ,
            n == name@.len(),
            forall|k: int| 0 <= k < i ==> ctx.arena@[buffer + 1 + k] == name@[k],
        decreases n - i,
    {
        if bget(&ctx.arena, buffer + 1 + i) != name[i] {
            return false;
        }
        i = i + 1;
    }
    bget(&ctx.arena, buffer + 1 + n) == 0
}
"""


def _v_ne(attr, body_checked, btype="&[u8]"):
    """`name_eq`'s TWIN replacement.

    ⭐ The whole proof obligation the new signature creates is one equation --
    `b@[1 + k] == ctx.arena@[buffer + 1 + k]` -- and it comes off
    `Seq::subrange`'s own index axiom, which is why the twin needs **no lemma and
    no new trusted item**: `1 + i <= REQ - 1 < REQ` follows from the `n + 2 <= REQ`
    guard the rung already carries for `strcmp`'s missing bound. The two `assert`s
    are what trigger it; an `assert` is proof work, not an `assume`.
    ⚠ For `&[u8; REQ]` the `requires` is unchanged -- `vstd/array.rs`'s
    `array_len_matches_n` gives the length -- but the CALL SITE cannot be proved,
    because the pinned vstd ships no `TryFrom<&[T]> for &[T; N]`. Stage 4
    measures that rather than asserting it."""
    read = ("b[1 + i]" if body_checked else "bget(&ctx.arena, buffer + 1 + i)")
    tail = ("b[1 + n] == 0" if body_checked
            else "bget(&ctx.arena, buffer + 1 + n) == 0")
    sub = ("        b@ == ctx.arena@.subrange(buffer as int, "
           "buffer + REQ as int),\n")
    inv_sub = ("            b@ == ctx.arena@.subrange(buffer as int, "
               "buffer + REQ as int),\n            b@.len() == REQ,\n")
    return (attr + "fn name_eq(ctx: &Ctx, b: " + btype
            + ", buffer: usize, name: &[u8]) -> (r: bool)\n"
            "    requires\n"
            "        wf_c(*ctx),\n"
            "        buffer + BLOCK <= ASZ,\n"
            + (sub if body_checked else "")
            + "    ensures\n"
              "        r == s_name_eq(ctx.arena@, buffer as int, name@),\n"
              "{\n"
              "    let n: usize = name.len();\n"
              "    if n > REQ - 2 {\n"
              "        return false;\n"
              "    }\n"
              "    let mut i: usize = 0;\n"
              "    while i < n\n"
              "        invariant\n"
              "            i <= n,\n"
              "            n + 2 <= REQ,\n"
              "            buffer + BLOCK <= ASZ,\n"
              "            ctx.arena@.len() == ASZ,\n"
            + (inv_sub if body_checked else "")
            + "            n == name@.len(),\n"
              "            forall|k: int| 0 <= k < i ==> "
              "ctx.arena@[buffer + 1 + k] == name@[k],\n"
              "        decreases n - i,\n"
              "    {\n"
            + ("        assert(b@[1 + i as int] == "
               "ctx.arena@[buffer + 1 + i as int]);\n"
               if body_checked else "")
            + "        if " + read + " != name[i] {\n"
              "            return false;\n"
              "        }\n"
              "        i = i + 1;\n"
              "    }\n"
            + ("    assert(b@[1 + n as int] == "
               "ctx.arena@[buffer + 1 + n as int]);\n"
               if body_checked else "")
            + "    " + tail + "\n"
              "}\n")


_V_SCAN = """            let t: &[Ent] = ent_table();
            let mut i: usize = 0;
            let mut found: bool = false;
            while i < t.len() && !found
                invariant
                    i <= t.len(),
                    t@ == tbl(),
                    buffer == f.cache as usize,
                    buffer + BLOCK <= ASZ,
                    wf_c(*ctx),
                    ctx.g() == (G { a: g0.a.update(buffer + f0.status as int, 0), ..g0 }),
                    !found ==> ent == 0,
                    !found ==> s_lookup(tbl(), ctx.arena@, buffer as int, 0)
                        == s_lookup(tbl(), ctx.arena@, buffer as int, i as int),
                    found ==> ent == s_lookup(tbl(), ctx.arena@, buffer as int, 0),
                decreases t.len() - i, if found { 0int } else { 1int },
            {
                if name_eq(ctx, buffer, t[i].name) {
"""


def _v_scan(hoist, checked):
    inv = ("                    b@ == ctx.arena@.subrange(buffer as int, "
           "buffer + REQ as int),\n" if checked else "")
    return ("""            let t: &[Ent] = ent_table();
""" + hoist + """            let mut i: usize = 0;
            let mut found: bool = false;
            while i < t.len() && !found
                invariant
                    i <= t.len(),
                    t@ == tbl(),
"""
            + inv +
            """                    buffer == f.cache as usize,
                    buffer + BLOCK <= ASZ,
                    wf_c(*ctx),
                    ctx.g() == (G { a: g0.a.update(buffer + f0.status as int, 0), ..g0 }),
                    !found ==> ent == 0,
                    !found ==> s_lookup(tbl(), ctx.arena@, buffer as int, 0)
                        == s_lookup(tbl(), ctx.arena@, buffer as int, i as int),
                    found ==> ent == s_lookup(tbl(), ctx.arena@, buffer as int, 0),
                decreases t.len() - i, if found { 0int } else { 1int },
            {
                if name_eq(ctx, b, buffer, t[i].name) {
""")


_V_HOIST_SUB = "            let b: &[u8] = &ctx.arena[buffer..buffer + REQ];\n"
_V_HOIST_ARR = ("            let b: &[u8; REQ] = "
                "(&ctx.arena[buffer..buffer + REQ]).try_into().unwrap();\n")
_V_DRIVER = '#[path = "../../common/driver.rs"]'
_V_TRYINTO = "use std::convert::TryInto;\n" + _V_DRIVER

_INL = "#[inline(always)]\n"

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}, None),
    ("r3_subslice", "R3",
     "⭐⭐ THE VARIANT THAT REFUTES THIS ROW'S OWN STATED MECHANISM. The shipped "
     "R3's header argues the lever is that LLVM gets the bound free from the "
     "TYPE. This changes ONLY the type -- the same bytes, at the same place, as "
     "a plain sub-slice with no conversion -- and it is a TIE. The lever is the "
     "HOIST out of the 251-entity scan, not the fixed-size type",
     {"rs": [(_S_LEVER, _S_LEVER_SUB, 1)]}, None),
    ("r3_arena_index", "R3",
     "R2's own spelling: no hoist at all, the whole arena re-indexed inside the "
     "compare loop. A calibration LOSER kept on purpose -- a search with no "
     "losing entry is one nobody can calibrate",
     {"rs": [(_S_LEVER, "", 1), (_S_SCAN, _S_SCAN_ARENA, 1)]}, None),
    ("r3_namecmp_fn", "R3",
     "⭐ the compare lifted out of `dec` into a forced-inline helper over the "
     "hoisted sub-slice. CHEAPER than the shipped R3, which is what says the R3 "
     "side of this row was unsearched too",
     {"rs": [(_S_LEVER, _S_LEVER_SUB, 1), (_S_SCAN, _S_SCAN_FN, 1),
             (_S_ANCHOR_FN, _S_NAMECMP, 1)]}, None),
]

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}, None),
    ("r4_buf_slice", "R4",
     "`name_eq` takes the work buffer as a hoisted `&[u8]` and reads it with a "
     "CHECKED index instead of `bget`, so two of the row's eleven unchecked "
     "dereferences go away. ⚠ DEARER without the inline hint, and shipped beside "
     "the next entry for exactly that reason: the hoist ALONE is not the win",
     {"rs": [(_U_NE, _u_ne("", True), 1), (_U_SCAN, _U_SCAN_SUB, 1)],
      "verus": [(_V_NE, _v_ne("", True), 1),
                (_V_SCAN, _v_scan(_V_HOIST_SUB, True), 1)]}, None),
    ("r4_buf_slice_inline", "R4",
     "⭐⭐ THE CANDIDATE THIS ROW TURNED ON: the same, plus `#[inline(always)]` on "
     "the helper. Cheaper than the shipped R4 AND cheaper than the shipped R3, "
     "with a twin that verifies at the shipped rung's own count and two fewer "
     "trusted call sites. ⚠ The gap to the entry above is ONE ATTRIBUTE and "
     "inlining is an LLVM heuristic -- the same attribute WITHOUT the hoist is a "
     "pessimisation",
     {"rs": [(_U_NE, _u_ne(_INL, True), 1), (_U_SCAN, _U_SCAN_SUB, 1)],
      "verus": [(_V_NE, _v_ne(_INL, True), 1),
                (_V_SCAN, _v_scan(_V_HOIST_SUB, True), 1)]}, None),
    ("r4_buf_array", "R4",
     "the same lever with `&[u8; REQ]`, which is `../safe_tuned.rs`'s own "
     "spelling. ⚠ EXPECTED INADMISSIBLE and priced anyway: the pinned vstd ships "
     "no conversion from a slice to an array reference. Stage 4 reproduces the "
     "error text. ⭐ Its exec cost is identical to `r4_buf_slice`'s to the "
     "instruction, which is the second of three measurements refuting the type "
     "mechanism",
     {"rs": [(_U_NE, _u_ne(_INL, True, "&[u8; REQ]"), 1),
             (_U_SCAN, _U_SCAN_ARR, 1), (_U_DRIVER, _U_TRYINTO, 1)],
      "verus": [(_V_NE, _v_ne(_INL, True, "&[u8; REQ]"), 1),
                (_V_SCAN, _v_scan(_V_HOIST_ARR, True), 1),
                (_V_DRIVER, _V_TRYINTO, 1)]}, None),
    ("r4_mirror_unchecked", "R4",
     "⭐⭐ THE MIRROR CONTROL, AND IT IS WHAT SETTLES THE ROW. "
     "`r4_buf_slice_inline`'s shape exactly -- same signature, same hoist, same "
     "inline hint -- with the arena reads left UNCHECKED. Far DEARER than the "
     "checked spelling, so on this row the unchecked read is the expensive one: "
     "going through the whole arena at a computed offset is what blocks the "
     "hoist",
     {"rs": [(_U_NE, _u_ne(_INL, False), 1), (_U_SCAN, _U_SCAN_SUB, 1)],
      "verus": [(_V_NE, _v_ne(_INL, False), 1),
                (_V_SCAN, _v_scan(_V_HOIST_SUB, False), 1)]}, None),
]


# ---- machinery ---------------------------------------------------------------
def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(REPO, *relpath))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_check():
    return _load("slb_check", ("harness", "check.py"))


_MEASURE = None


def load_measure():
    """`harness/measure.py`, IMPORTED and never transcribed, and lazily so that
    `--audit-only` does not pay for its imports of `slb`, `asm` and `build`.

    ⚠⚠ `TASK_PHP_022` §3.2 measured that a transcription of `_sum_rows` is a
    DIFFERENT FUNCTION -- it took the first matching annotate row instead of
    SUMMING all of them, matched the needle on the whole line instead of on the
    function field, and did not check callgrind's return code -- and that each
    difference produces a plausible wrong number rather than an error. Importing
    `harness/measure.py` is not an edit to it: `PLAN_PHP.md` §2.1 forbids
    WRITING under `harness/`, and reading is what the shim exists to do."""
    global _MEASURE
    if _MEASURE is None:
        _MEASURE = _load("slb_measure", ("harness", "measure.py"))
    return _MEASURE


def contract():
    txt = open(os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt,
                                re.S).group(1))


def identity_premise():
    """`(pinned_levels, measured_levels)` for the `unsafe` vs `verus` pair.

    ⚠⚠⚠ **THIS IS THE PREMISE `admissibility()` RESTS ON AND IT IS READ, NEVER
    ASSUMED.** `ph29`'s copy of this file hard-codes *"`identity` pins `O3
    exact`, so a twin must be byte-identical"*. On `ph45` the pin is `differ` at
    both levels, so byte-identity is not a bar -- and a hard-coded rule would
    either refuse every candidate here or, if this row were ever re-pinned to
    `exact`, silently admit one it should refuse.

    ⭐ It reads BOTH the declaration and the MEASURED level, because F82's
    negative N6 found a row (`p25`) whose `spec.md` contains the string
    `identity: unsafe == verus, O3 exact` as shared-block BOILERPLATE while its
    real pin is `norel`. **Read the record, not the prose.**"""
    pinned = {}
    for e in contract().get("identity") or []:
        if {e.get("a"), e.get("b")} == {"unsafe", "verus"}:
            for lvl in ("O0", "O3"):
                if e.get(lvl):
                    pinned[lvl] = e[lvl]
    measured = {}
    if os.path.exists(GATE_RECORD):
        for e in json.load(open(GATE_RECORD)).get("identity") or []:
            if e.get("pair") == "unsafe vs verus" and e.get("opt"):
                measured[e["opt"]] = e.get("level")
    return pinned, measured


def admissibility(pinned, measured):
    """`(needs_byte_identity, sentence)` -- what an R4 candidate must satisfy.

    Byte-identity is required **iff** this row pins AND measures `exact` at O3.
    Anything else -- `differ`, `norel`, a disagreement between the two, or a
    missing record -- and the bar is *"the twin verifies"*, which is the bar
    `.memory/01-ladder.md` actually needs: an R4 is a program whose obligations
    a prover can discharge."""
    p, m = pinned.get("O3"), measured.get("O3")
    if p == "exact" and m == "exact":
        return True, ("O3 `exact` is BOTH pinned and measured, so an R4 "
                      "candidate needs a twin that verifies AND compiles to a "
                      "byte-identical kernel")
    if p != m:
        return False, (f"⚠ the pin says O3 `{p}` and the record measures "
                       f"`{m}` -- they DISAGREE, so this file falls back to the "
                       f"weaker bar (the twin must verify) and says so loudly")
    return False, (f"O3 is pinned AND measured `{p}`, so this row has no "
                   f"byte-identity obligation between R4 and R5 and an R4 "
                   f"candidate needs only a twin that VERIFIES. Byte-identity "
                   f"is recorded below as information (RECAP_PHP.md F82, open "
                   f"item 61)")


def apply_subs(src, subs):
    for old, new, hits in subs:
        n = src.count(old)
        assert n == hits, (f"spellings.py: expected {hits} occurrence(s) of\n"
                           f"{old!r}\nfound {n}. The shipped rung has moved "
                           f"under this variant; fix the substitution rather "
                           f"than the assertion.")
        src = src.replace(old, new)
    return src


def materialise(name, side, subs):
    """Write the variant's sources into SCRATCH, driver path absolutised.

    ⚠ An R4 variant gets TWO files: the exec rung and the R5 twin. The twin's
    substitution list is explicit and does NOT fall back to the exec one -- the
    twin's `name_eq` carries a `requires`, an `ensures`, a loop invariant and a
    `decreases`, so the exec anchor does not occur in it and a silent fallback
    would leave the twin unchanged while the exec variant moved."""
    os.makedirs(SCRATCH, exist_ok=True)
    base = "safe_tuned.rs" if side == "R3" else "unsafe.rs"
    src = open(os.path.join(PDIR, base), encoding="utf-8").read()
    src = apply_subs(src, subs.get("rs", []))
    src = src.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
    p = os.path.join(SCRATCH, f"{side}_{name}.rs")
    open(p, "w", encoding="utf-8").write(src)
    vp = None
    if side == "R4":
        v = open(os.path.join(PDIR, "verus.rs"), encoding="utf-8").read()
        v = apply_subs(v, subs.get("verus", []))
        v = v.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
        vp = os.path.join(SCRATCH, f"{side}_{name}_verus.rs")
        open(vp, "w", encoding="utf-8").write(v)
    return p, vp


def build(rs, out):
    """`harness/build.py::rust_flags('O3', 'isolated')`, character for
    character."""
    cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
           "-C", "opt-level=3", "-C", "debug-assertions=off",
           "--cfg", "slb_isolated", rs, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return (out, None) if r.returncode == 0 else (None, r.stderr[-1500:])


def build_verus(rs, out):
    """`harness/build.py::build_verus`: the same flags through `verus_run.py`,
    minus `--edition`, which Verus fixes itself."""
    cmd = [sys.executable, VERUS_RUN, "--compile", rs, "-o", out,
           "-C", "codegen-units=1", "-C", "opt-level=3",
           "-C", "debug-assertions=off", "--cfg", "slb_isolated"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO,
                       timeout=3600)
    return (out, None) if r.returncode == 0 else (None,
                                                  (r.stdout + r.stderr)[-1500:])


def run(exe, path):
    r = subprocess.run([exe, path], capture_output=True, text=True, timeout=900)
    return r.stdout.strip()


_TOTAL = re.compile(r"^([\d,]+)\s+\(100\.0%\)\s+PROGRAM TOTAL")


def both_ir(exe, path, tag):
    """`(kernel_exclusive_ir, whole_program_ir, error_or_None)` from ONE
    callgrind run -- the two families this row must publish.

    **A1** uses `harness/measure.py::_sum_rows` IMPORTED (see `load_measure`).
    **W1** is `callgrind_annotate`'s own `PROGRAM TOTALS` line, which is what
    `../NOTES.md` §8b's *"whole-program `Ir`"* column carries.

    ⚠ Callgrind's RETURN CODE is checked, and so is the presence of the totals
    line: probe rule 1, a probe that CANNOT EVALUATE must say so rather than
    return a figure-shaped `None`."""
    M = load_measure()
    out = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        "--callgrind-out-file=" + out, exe, path],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        if os.path.exists(out):
            os.unlink(out)
        return None, None, (f"callgrind exit {r.returncode} on {tag}: "
                            f"{r.stderr[-200:]}")
    ann = subprocess.run([M.CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=600)
    txt = (ann.stdout + ann.stderr).strip()
    if os.path.exists(out):
        os.unlink(out)
    tot, _names = M._sum_rows(txt, "kernel")
    wp = None
    for ln in txt.splitlines():
        m = _TOTAL.match(ln.strip())
        if m:
            wp = int(m.group(1).replace(",", ""))
            break
    if tot is None:
        return None, wp, (f"callgrind_annotate named no `kernel` function for "
                          f"{tag} (rc {ann.returncode})")
    if wp is None:
        return tot, None, (f"callgrind_annotate printed no `PROGRAM TOTALS` "
                           f"line for {tag} -- the whole-program family cannot "
                           f"be computed and must not be reported as 0")
    return tot, wp, None


_XFER = re.compile(r"^(j[a-z]+|call|loop[a-z]*)\s+([0-9a-f]+)$")
#: The `kernel` needle, and it is NOT a bare substring.
#:
#: ⚠⚠ `ph16`'s copy tests `"kernel" in name` on the whole mangled symbol. That
#: folds **every** symbol whose name merely contains the letters into the digest:
#: a sibling `kernel_prologue`, a twin `slb_twin_kernel`, or -- measured, by
#: `ph29`'s negative D2 -- a binary built from a crate called `nokernel`, whose
#: `main` mangles to `…_8nokernel4main`. `harness/measure.py::_sum_rows` does NOT
#: have this hole: it matches `(?:^|::)kernel(?:$|[^A-Za-z0-9_])` on the function
#: field. This is the same discipline on the fingerprint side. The leading class
#: admits a digit because Rust's v0 mangling length-prefixes the component -- the
#: real symbol ends `...6kernel` -- and excludes letters and `_` so that
#: `nokernel` and `slb_twin_kernel` do not match.
_KERNEL_SYM = re.compile(r"(?:^|[^A-Za-z_])kernel(?:$|[^A-Za-z0-9_])")


def disasm(exe, needle=_KERNEL_SYM):
    """`{address: text}` for the `kernel` function only.

    ⚠ `harness/asm.py` is *the* objdump caller in `harness/`, and this is not an
    edit to it: six PAT patterns' `controls/` disassemble directly for exactly
    this reason (`CLAUDE.md` -- *the GATE has one pipeline, not the tree*). What
    is needed here is per-instruction text keyed by address, which `asm.py` does
    not return.

    ⚠⚠ **TWO GUARDS HERE ARE NOT IN `ph16`'s COPY AND BOTH WERE FOUND BY
    MUST-FIRE NEGATIVES RATHER THAN BY READING IT** (F79):

      * objdump's RETURN CODE is checked. Without it a binary that does not
        exist disassembles to nothing and `kernel_fingerprint` returns
        `(0, md5(""))` -- a figure-shaped value, and two of them compare EQUAL.
        On a function whose whole job is to say *byte-identical*, the failure
        mode is a FALSE POSITIVE.
      * the needle is `_KERNEL_SYM` and not `"kernel" in name`."""
    r = subprocess.run(["objdump", "-d", "--no-show-raw-insn", exe],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"objdump failed on {exe} (rc {r.returncode}): "
                           f"{r.stderr.strip()[:200]}")
    out, on = {}, False
    for line in r.stdout.splitlines():
        m = re.match(r"^[0-9a-f]+ <(.*)>:$", line)
        if m:
            on = bool(needle.search(m.group(1)))
            continue
        if not on:
            continue
        m = re.match(r"\s+([0-9a-f]+):\s+(.*)", line)
        if m:
            out[int(m.group(1), 16)] = m.group(2).strip()
    return out


def kernel_fingerprint(exe, needle=_KERNEL_SYM):
    """`(n_instructions, 12-hex digest)` of `kernel`'s text, normalised so that
    it is a claim about CODE and not about LAYOUT.

    Three rules, and each removes a layout term while keeping a code term:
      * everything from the first `<` goes -- the crate hash;
      * everything from `#` goes -- objdump's RESOLVED rip-relative address. The
        DISPLACEMENT stays, and it is the code;
      * a control-transfer target becomes a SIGNED OFFSET from the instruction's
        own address, so the control-flow shape survives and its placement does
        not.
    Registers and immediates are KEPT, so a register-allocation change is still a
    difference.

    ⚠ It raises on an empty disassembly. A `kernel` that disassembles to nothing
    is a measurement that did not happen, and `(0, md5(""))` is the same value
    for every such binary.

    ⚠⚠ **ON THIS ROW THIS FUNCTION IS INFORMATION AND NOT A VERDICT**, because
    `../spec.md` pins `identity: differ`. It is kept and reported for two
    reasons: `dec` carries ~90 % of the work and `kernel` carries the rest, so a
    variant whose `kernel` digest MOVES has changed something outside `dec` and a
    reader should know; and the A1 column is computed over exactly this symbol,
    so an unchanged digest is the mechanical explanation for an unchanged A1."""
    txt = disasm(exe, needle)
    if not txt:
        raise RuntimeError(
            f"no `kernel` function in the disassembly of {exe} -- this is a "
            f"measurement that did not happen, not a kernel of length 0")
    body = []
    for a in sorted(txt):
        t = re.sub(r"\s+", " ", txt[a]).split("<")[0].split("#")[0].strip()
        m = _XFER.match(t)
        body.append(f"{m.group(1)} {int(m.group(2), 16) - a:+d}" if m else t)
    return len(body), hashlib.md5("\n".join(body).encode()).hexdigest()[:12]


#: md5 of the EMPTY STRING, truncated the way `kernel_fingerprint` truncates.
#: F79's defect (a) produced exactly this value for a binary that does not
#: exist, and two of them compare EQUAL. `disasm` raises rather than producing
#: it; `twin_identical` refuses it as well, so the two guards are independent.
_EMPTY_MD5 = hashlib.md5(b"").hexdigest()[:12]

_VR = re.compile(r"verification results:: (\d+) verified, (\d+) errors")


def verus_ok(vp):
    """`(ok, message)` for one twin.

    ⚠⚠ **READ THE ERROR TEXT, NOT THE EXIT CODE** -- `../spec.md`'s own hashed
    rule. `is not supported` DISQUALIFIES, because it is what forces a new
    TRUSTED item; `postcondition not satisfied` and `invariant not satisfied`
    disqualify NOTHING and are proof work (`p05` went `11 verified, 1 errors` ->
    `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB).
    Both are reported distinctly, because a row that conflates them refuses
    candidates for the wrong reason -- and on THIS row that distinction decides
    `r4_buf_array`: the `&[u8; REQ]` lever is refused for
    `core::array::TryFromSliceError is not supported`, which is a fact about the
    pinned vstd's COVERAGE, and NOT for any proof that failed."""
    r = subprocess.run([sys.executable, VERUS_RUN, vp],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    if "is not supported" in txt:
        line = next((ln for ln in txt.splitlines()
                     if "is not supported" in ln), "")
        return False, "DISQUALIFIED -- is not supported: " + line.strip()[:220]
    m = _VR.search(txt)
    if not m:
        return False, txt.strip()[-400:]
    return m.group(2) == "0", m.group(0)


_TRUSTED_CALL = re.compile(r"\b(?:bget|bset)\s*\(")
_TRUSTED_DEF = re.compile(r"\bfn\s+(?:bget|bset)\s*\(")


def trusted_call_sites(src):
    """How many `bget`/`bset` CALL SITES this variant has -- i.e. how wide its
    unchecked-dereference surface is.

    ⚠ MEASURED, not asserted, and line comments are stripped first, because
    `../unsafe.rs` and `../verus.rs` both NAME these accessors in prose that
    explains them and a raw count would fold the prose into the surface. The two
    `fn` definitions are subtracted, so the number is call sites and not
    mentions. ⚠ It is deliberately NOT a verdict: a variant with a smaller
    trusted surface at the same price is a THIRD kind of result the bench rule
    has no name for (`ph07`'s `r4_index0`), and this file reports it rather than
    ranking on it."""
    code = "\n".join(re.sub(r"//.*$", "", ln) for ln in src.splitlines())
    return (len(_TRUSTED_CALL.findall(code))
            - len(_TRUSTED_DEF.findall(code)))


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in `../spec.md`'s `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics rather than a stricter invention:

      * a `forbidden` hit DISQUALIFIES -- `check.py`'s stage 0 has hard-failed on
        one since TASK_068, and its scope is universal by the key's own meaning,
        so it is decidable with no English involved;
      * a `required` miss is REPORTED and does not, because which rungs a
        `required` entry scopes to lives in the entry's ENGLISH and no gate stage
        reproduces it.

    ⚠ Getting this backwards is not a conservative error. This row's three
    `required` C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN -- removing
    `(int)mbfl_malloc` IS the upstream fix -- and the shipped gate record carries
    those three absences and calls the row `PASS-WITH-BLOCKED-ROWS`. An audit
    that treated a `required` miss as disqualifying would refuse the row's own
    hardened rung."""
    forb, miss = [], []
    for key, sink in (("required", miss), ("forbidden", forb)):
        for i, e in enumerate(decl.get(key) or []):
            txt = e.get(lang) if isinstance(e, dict) else e
            if not isinstance(txt, str):
                continue
            for tok in re.findall(r"`([^`]+)`", txt):
                hit = chk.spelling_matches(tok, src, lang=lang)
                if key == "forbidden" and hit:
                    sink.append(f"forbidden[{i}] `{tok}` PRESENT")
                elif key == "required" and not hit:
                    sink.append(f"required[{i}] `{tok}`")
    return forb, miss


# ---- the verdicts, factored so they can be ATTACKED --------------------------
# `PROTOCOL_PHP.md` §H: a validator lands with its must-fire negatives. These
# functions ARE this file's verdict, so they are functions and not lines inside
# `main`, and `.temp/php37/negatives_spellings.py` drives them over synthetic
# `rows` dicts -- an out-of-contract cheaper candidate, an unpriced one, a
# sub-`TIE_PCT` margin, a candidate excluded by ENGLISH, a twin that verifies but
# is not byte-identical, and an `identity` premise that has moved -- none of
# which is reachable through the CLI.

#: The `problems` entry a run WITHOUT `--verus` carries. A module constant and
#: not a literal inside `main`, so `.temp/php37/negatives_spellings.py` can hand
#: it to `harness/check.py::control_json_verdict` and prove that the GATE would
#: refuse such a sidecar -- which is the claim, and it is not the same claim as
#: "this script appends a string".
NO_VERUS_PROBLEM = (
    "R4 ADMISSIBILITY WAS NOT CHECKED (no --verus), so every R4 variant's "
    "`in_contract` above is unverified: an R4 is a program whose obligations a "
    "prover can discharge, and without a twin that VERIFIES an R4 candidate is "
    "a control and not a rung. Regenerate with `--verus`, which is what "
    "`pin.regenerate` names.")

#: ⚠ The ONE variant excluded by English rather than by grep, and the sentence is
#: the row's own. It is a module constant so a negative can assert that the
#: exclusion actually reaches `cheapest_in_contract`.
ENGLISH_VERDICTS = {}


def twin_identical(r):
    """Whether a variant's twin compiles to the same `kernel` as its exec rung.

    ⚠ It compares BOTH the digest and the instruction count, and it is FALSE
    when either is missing. A missing field must not read as agreement: the
    digest of an empty disassembly is a constant, so `None == None` and
    `'d41d8cd98f00' == 'd41d8cd98f00'` are the two ways this check can say
    *byte-identical* about two things that were never compared. `disasm` raises
    on the second; this function refuses the first.

    ⚠⚠ **ON `ph45` THIS IS INFORMATION, NOT A BAR** -- see `admissibility()`.
    `ph29`'s copy uses it as a gate because `ph29` pins `O3 exact`."""
    a, b = r.get("kernel_fingerprint"), r.get("verus_kernel_fingerprint")
    na, nb = r.get("kernel_insns"), r.get("verus_kernel_insns")
    if a is None or b is None or na is None or nb is None:
        return False
    # ⚠⚠⚠ THE THIRD WAY THIS CAN SAY *byte-identical* ABOUT NOTHING, AND
    # `ph29`'s COPY DOES NOT REFUSE IT -- found by this file's own negative D1b.
    # F79 fixed `disasm` so that a missing binary RAISES instead of returning
    # `(0, md5(""))`, and `twin_identical` was given the `None` refusal above.
    # Neither covers the VALUE: hand this function two `(0, 'd41d8cd98f00')`
    # rows and `ph29`'s copy returns True. The guard upstream means the value
    # cannot arise from THIS file today -- so it is latent, exactly as F79's two
    # were on `ph16` -- but a verdict function whose safety depends on its
    # caller is one respelling away from a false positive. A kernel of length
    # ZERO is a measurement that did not happen.
    if na == 0 or nb == 0 or _EMPTY_MD5 in (a, b):
        return False
    return a == b and na == nb


def cheapest_in_contract(rows, side="R3", key="ir_per_call_small_wp"):
    """The cheapest IN-CONTRACT, PRICED candidate on one side, or `None`.

    Four exclusions and each one is a defect this would otherwise publish: a
    variant that is out of contract by GREP, one that is out of contract by
    ENGLISH, one that was never priced, and a side that is not a rung side.

    ⚠ `key` defaults to the WHOLE-PROGRAM family and not to A1, because on this
    row A1 is identical for every variant on a side (`../NOTES.md` §8a) -- so a
    `min` over A1 would return whichever variant happened to be enumerated
    first, which is a figure-shaped value and not a minimum."""
    if side not in RUNG_SIDES:
        return None
    c = [r for r in rows.values()
         if r.get("side") == side and r.get("in_contract")
         and not r.get("english_verdict") and r.get(key) is not None]
    return min(c, key=lambda r: r[key]) if c else None


def dearest_in_contract(rows, side="R3", key="ir_per_call_small_wp"):
    """The other end of the R3-SIDE SPAN, which is the second of the two
    quantities that may be published."""
    if side not in RUNG_SIDES:
        return None
    c = [r for r in rows.values()
         if r.get("side") == side and r.get("in_contract")
         and not r.get("english_verdict") and r.get(key) is not None]
    return max(c, key=lambda r: r[key]) if c else None


def cheaper_than_shipped(rows, side="R4", key="ir_per_call_small_wp",
                         tie_pct=TIE_PCT):
    """Every IN-CONTRACT candidate on one side that beats its shipped rung by
    MORE than `tie_pct`, cheapest first. Empty means that endpoint is
    DEGENERATE -- which is `ph07`'s and `ph16`'s answer and is NOT this row's."""
    if side not in RUNG_SIDES:
        return []
    base = rows.get((side, "v0_shipped"), {}).get(key)
    if not base:
        return []
    out = [r for r in rows.values()
           if r.get("side") == side and r.get("name") != "v0_shipped"
           and r.get("in_contract") and not r.get("english_verdict")
           and r.get(key) is not None
           and (base - r[key]) / base * 100.0 > tie_pct]
    return sorted(out, key=lambda r: r[key])


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit; no build, no callgrind")
    ap.add_argument("--verus", action="store_true",
                    help="stage 4: put every R4 twin through Verus")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    chk = load_check()
    decl = contract()["idiom"]
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("spellings.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    pinned, measured = identity_premise()
    need_ident, ident_why = admissibility(pinned, measured)
    print("0a. THE `identity` PREMISE, READ FROM BOTH THE PIN AND THE RECORD")
    print(f"  ../spec.md                pinned  {pinned}")
    print(f"  results-php/gate/...json  measured {measured}")
    print(f"  -> {ident_why}")
    if pinned.get("O3") != measured.get("O3"):
        problems.append(
            f"the `identity` pin (O3 {pinned.get('O3')!r}) and the gate record "
            f"(O3 {measured.get('O3')!r}) DISAGREE, so this file cannot tell "
            f"which admissibility rule applies to an R4 candidate and fell back "
            f"to the weaker one")

    variants = R3_VARIANTS + R4_VARIANTS
    rows = {}
    print("\n0b. THE SPELLING AUDIT -- every backticked idiom entry, "
          "harness/check.py::spelling_matches")
    for name, side, why, subs, eng in variants:
        rs, vp = materialise(name, side, subs)
        src = open(rs, encoding="utf-8").read()
        forb, miss = audit(chk, decl, src)
        rows[(side, name)] = {
            "side": side, "name": name, "why": why,
            "rs": rs, "verus_rs": vp,
            "rung_candidate": side in RUNG_SIDES,
            "forbidden_hits": forb, "required_absent": miss,
            "in_contract": not forb,
            "english_verdict": eng or ENGLISH_VERDICTS.get(name)}
        print(f"  {side} {name:22s} "
              + ("IN CONTRACT" if not forb else "OUT: " + "; ".join(forb))
              + "   required absent: "
              + (", ".join(m.split("`")[1] for m in miss) or "none")
              + ("   ⚠ OUT BY ENGLISH" if rows[(side, name)]["english_verdict"]
                 else ""))
    if args.audit_only:
        return 0

    print("\n1. BUILD + CHECKSUM + KERNEL FINGERPRINT -- a respelling that "
          "changes the answer is not one.\n   ⚠ EVERY variant is compared "
          "against R3 v0_shipped on all "
          f"{len(inputs)} inputs: this row pins all\n   four Rust rungs to one "
          "checksum per input and the gate asserts it.")
    ref = None
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"], os.path.join(SCRATCH, f"{side}_{name}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side} {name:22s} BUILD FAILED")
            problems.append(f"{side} {name} does not build: {err}")
            continue
        r["exe"] = exe
        r["kernel_insns"], r["kernel_fingerprint"] = kernel_fingerprint(exe)
        # ⚠ RE-READ, and it is not defensive: an earlier draft passed the `src`
        # left over from the stage-0b audit loop and every variant -- including
        # the three SAFE R3 ones, which contain no `bget` at all -- reported the
        # LAST audited variant's count of 12. It was a plausible wrong number
        # rather than an error, and what caught it was a SAFE rung reporting a
        # trusted surface.
        r["trusted_call_sites"] = trusted_call_sites(
            open(r["rs"], encoding="utf-8").read())
        ans = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = ans
        if (side, name) == ("R3", "v0_shipped"):
            ref = ans
            print(f"  {side} {name:22s} REFERENCE  "
                  f"kernel {r['kernel_insns']:3d} {r['kernel_fingerprint']}"
                  f"   trusted sites {r['trusted_call_sites']:2d}")
            continue
        diff = [k for k, v in ans.items() if ref.get(k) != v]
        print(f"  {side} {name:22s} "
              + ("ok  identical on all "
                 f"{len(ans)} inputs" if not diff
                 else f"*** DIFFERS on {diff}")
              + f"   kernel {r['kernel_insns']:3d} {r['kernel_fingerprint']}"
              + f"   trusted sites {r['trusted_call_sites']:2d}")
        if diff:
            problems.append(f"{side} {name} changes the answer on {diff} "
                            f"-- it is not a respelling of this kernel")
            r["in_contract"] = False

    print("\n2. THE PRICE -- BOTH FAMILIES, from ONE callgrind run per cell.\n"
          "   A1 = kernel_exclusive_ir/call (measure.py's own statistic, "
          "IMPORTED).\n   W1 = whole-program Ir/call (callgrind's PROGRAM "
          "TOTALS -- NOTES.md §8b's column).\n   ⚠⚠ A1 SEES 9.5 % OF THIS ROW "
          "AND EVERY LEVER HERE IS IN THE OTHER 90 %.")
    print(f"  {'cell':30s} {'A1 small':>11s} {'A1 large':>11s} "
          f"{'W1 small':>11s} {'W1 large':>11s}")
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        if not r.get("exe"):
            continue
        for inp, _stride, nit in PROBES:
            kx, wp, err = both_ir(r["exe"], os.path.join(PDIR, "inputs", inp),
                                  f"{side}.{name}.{inp}")
            if err:
                problems.append(f"{side} {name} {inp}: {err}")
            tag = "small" if inp == PROBES[0][0] else "large"
            r[f"ir_per_call_{tag}"] = None if kx is None else kx / float(nit)
            r[f"ir_per_call_{tag}_wp"] = None if wp is None else wp / float(nit)
        if (r.get("ir_per_call_small") is None
                or r.get("ir_per_call_small_wp") is None):
            problems.append(f"{side} {name}: callgrind gave no figure for one "
                            f"of the two families")
            continue
        print(f"  {side + ' ' + name:30s} {r['ir_per_call_small']:11.1f} "
              f"{r['ir_per_call_large']:11.1f} "
              f"{r['ir_per_call_small_wp']:11.1f} "
              f"{r['ir_per_call_large_wp']:11.1f}")
    b4a = rows[("R4", "v0_shipped")].get("ir_per_call_small")
    b4w = rows[("R4", "v0_shipped")].get("ir_per_call_small_wp")
    print(f"\n  {'cell':30s} {'A1 vs R4ship':>14s} {'W1 vs R4ship':>14s}")
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        if r.get("ir_per_call_small") is None:
            continue
        r["pct_vs_r4ship_a1"] = (100.0 * (r["ir_per_call_small"] - b4a) / b4a
                                 if b4a else None)
        r["pct_vs_r4ship_wp"] = (
            100.0 * (r["ir_per_call_small_wp"] - b4w) / b4w if b4w else None)
        print(f"  {side + ' ' + name:30s} {r['pct_vs_r4ship_a1']:+13.2f}% "
              f"{r['pct_vs_r4ship_wp']:+13.2f}%")

    print("\n3. DOES THIS PIPELINE REPRODUCE THE SHIPPED CELLS? -- BOTH "
          "FAMILIES.")
    rec_ok = None
    if os.path.exists(RECORD):
        rec = json.load(open(RECORD))
        want = {}
        nit = {i: n for i, _, n in PROBES}
        for c in rec.get("cells", []):
            if c.get("opt") == "O3" and c.get("mode") == "isolated":
                for inp, blk in (c.get("ir") or {}).items():
                    if inp in nit and blk and blk.get("kernel_exclusive_ir"):
                        want[(c["cell"], inp)] = (blk["kernel_exclusive_ir"]
                                                  / float(nit[inp]))
        rec_ok = True
        for cell, side in (("safe_tuned", "R3"), ("unsafe", "R4")):
            for inp, key in (("small.bin", "ir_per_call_small"),
                             ("large.bin", "ir_per_call_large")):
                w = want.get((cell, inp))
                g = rows[(side, "v0_shipped")].get(key)
                if w is None or g is None:
                    print(f"  A1 {cell:12s} {inp:10s} record={w} here={g}  "
                          f"(not comparable)")
                    continue
                d = abs(w - g) / w * 100.0
                print(f"  A1 {cell:12s} {inp:10s} record={w:12.4f} "
                      f"here={g:12.4f}  delta={d:.4f}%")
                if d > 0.5:
                    rec_ok = False
                    problems.append(
                        f"A1 {cell}/{inp}: this pipeline measures {g:.4f} where "
                        f"the shipped record says {w:.4f} ({d:.2f}% apart) -- "
                        f"the variants above are then about a different "
                        f"benchmark from the row")
        for (cell, inp), tot in sorted(SHIPPED_WP.items()):
            side = "R3" if cell == "safe_tuned" else "R4"
            n = nit[inp]
            g = rows[(side, "v0_shipped")].get(
                "ir_per_call_small_wp" if inp == "small.bin"
                else "ir_per_call_large_wp")
            if g is None:
                print(f"  W1 {cell:12s} {inp:10s} NOT MEASURED")
                continue
            w = tot / float(n)
            d = abs(w - g) / w * 100.0
            print(f"  W1 {cell:12s} {inp:10s} NOTES.md §8b={w:12.4f} "
                  f"here={g:12.4f}  delta={d:.4f}%")
            if d > 0.5:
                rec_ok = False
                problems.append(
                    f"W1 {cell}/{inp}: this pipeline measures {g:.4f} Ir/call "
                    f"whole-program where NOTES.md §8b publishes {w:.4f} "
                    f"({d:.2f}% apart)")
    else:
        print(f"  no measurement record at {RECORD}")

    if args.verus:
        print("\n4. R4 ADMISSIBILITY -- the twin must VERIFY. ⚠ READ THE ERROR "
              "TEXT:\n   `is not supported` disqualifies; a failed "
              "postcondition is proof work.\n   ⚠⚠ Byte-identity is RECORDED "
              "and is NOT a bar on this row -- see stage 0a.")
        for name, side, why, subs, eng in R4_VARIANTS:
            r = rows[(side, name)]
            if not r.get("verus_rs"):
                continue
            ok, msg = verus_ok(r["verus_rs"])
            r["verus_verifies"], r["verus_msg"] = ok, msg
            r["verus_unsupported"] = bool(msg and msg.startswith("DISQUALIFIED"))
            if ok:
                vexe, verr = build_verus(
                    r["verus_rs"], os.path.join(SCRATCH, f"{side}_{name}_v.bin"))
                if not vexe:
                    r["verus_build_error"] = verr
                    problems.append(f"R4 {name}: the twin VERIFIES but does not "
                                    f"compile: {verr}")
                else:
                    n, dg = kernel_fingerprint(vexe)
                    r["verus_kernel_insns"], r["verus_kernel_fingerprint"] = n, dg
            r["identity_exact"] = twin_identical(r)
            if not ok or (need_ident and not r["identity_exact"]):
                r["in_contract"] = False
            state = ("VERIFIES" if ok else "DOES NOT VERIFY")
            print(f"  R4 {name:22s} {state:16s} "
                  f"{msg.splitlines()[0][:74] if msg else ''}"
                  + (f"   twin kernel {r.get('verus_kernel_insns')} "
                     f"{r.get('verus_kernel_fingerprint')}"
                     f"  {'== exec' if r['identity_exact'] else '!= exec'}"
                     if r.get("verus_kernel_fingerprint") else ""))
            if name == "v0_shipped" and not ok:
                problems.append(
                    "R4 v0_shipped's own twin does not verify -- this pipeline "
                    "is not measuring the shipped rung")
    else:
        print("\n4. R4 ADMISSIBILITY -- skipped (pass --verus). ⚠ Until it is "
              "run, no R4 variant\n   above is a RUNG; each is a control.")
        # ⚠⚠⚠ AND THE SIDECAR MUST SAY SO, BECAUSE A RUN WITHOUT `--verus`
        # WRITES A FILE THAT LOOKS COMPLETE AND IS NOT (`TASK_PHP_022` §3.2
        # gap 5, DEMONSTRATED LIVE AT `TASK_PHP_024` §1.6 on `ph07`, where
        # regenerating without the flag flipped the one R4 variant that does NOT
        # verify from `in_contract: false` to `true`, dropped every
        # `verus_verifies` field, and still wrote `"problems": []` and exited 0).
        # PROBE RULE 1: a probe that CANNOT EVALUATE must say so and exit
        # non-zero. `pin.regenerate` names `--verus` for this reason.
        problems.append(NO_VERUS_PROBLEM)

    # ---- the two published numbers, in BOTH families ------------------------
    print("\n5. WHAT MAY BE QUOTED. TWO QUANTITIES, IN TWO LABELLED FAMILIES.")
    r3s, r4s = rows[("R3", "v0_shipped")], rows[("R4", "v0_shipped")]
    for fam, key, pct in (("A1  (kernel-exclusive Ir/call, small.bin)",
                           "ir_per_call_small", "pct_vs_r4ship_a1"),
                          ("W1  (whole-program  Ir/call, small.bin)",
                           "ir_per_call_small_wp", "pct_vs_r4ship_wp")):
        print(f"\n  ---- family {fam} ----")
        print(f"  fixed-R4 bound   R3ship - R4ship   "
              f"{r3s.get(pct, float('nan')):+.2f}%   "
              f"({r3s.get(key, 0):.1f} vs {r4s.get(key, 0):.1f} Ir/call)")
        lo = cheapest_in_contract(rows, "R3", key)
        hi = dearest_in_contract(rows, "R3", key)
        if lo is not None and hi is not None:
            if abs(hi[pct] - lo[pct]) <= TIE_PCT:
                # ⚠⚠ NOT A SPAN AT ALL. On this row family A1 gives every
                # in-contract R3 variant the SAME figure, so `min` and `max`
                # return whichever was enumerated first and naming them would
                # be a figure-shaped value. Say so instead.
                print(f"  R3-side span     ⚠ NOT COMPUTABLE IN THIS FAMILY: "
                      f"all {len([r for r in rows.values() if r.get('side') == 'R3' and r.get('in_contract') and r.get(pct) is not None])}"
                      f" in-contract R3 variants\n"
                      f"                   measure {lo[pct]:+.2f}% here, within "
                      f"the {TIE_PCT}% tie threshold of each other. A `min` over "
                      f"a\n                   set of equal values is the "
                      f"enumeration order, not a minimum.")
            else:
                print(f"  R3-side span     cheapest-found .. dearest-found in "
                      f"contract  {lo[pct]:+.2f}% .. {hi[pct]:+.2f}%"
                      f"   `{lo['name']}` .. `{hi['name']}`")
    print("\n  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it).")

    beat = cheaper_than_shipped(rows, "R4")
    beat3 = cheaper_than_shipped(rows, "R3")
    r4c = [r for (s, _n), r in rows.items()
           if s == "R4" and r.get("in_contract") and not r.get("english_verdict")
           and r.get("ir_per_call_small_wp") is not None]
    print(f"\n  ⚠ R4 SIDE, SEARCHED ({len(r4c)} admissible of "
          f"{len(R4_VARIANTS)} tried), W1:")
    for r in sorted(r4c, key=lambda r: r["ir_per_call_small_wp"]):
        d = r["pct_vs_r4ship_wp"]
        verdict = ("SHIPPED" if r["name"] == "v0_shipped"
                   else (f"TIE (< {TIE_PCT}%)" if abs(d) <= TIE_PCT
                         else ("CHEAPER" if d < 0 else "dearer")))
        print(f"      {r['name']:22s} {r['ir_per_call_small_wp']:10.1f} "
              f"Ir/call  {d:+.2f}%   {verdict}")
    for (s, nm), r in sorted(rows.items()):
        if s == "R4" and (not r.get("in_contract") or r.get("english_verdict")):
            print(f"      {nm:22s} INADMISSIBLE -- "
                  + (r.get("english_verdict") or r.get("verus_msg")
                     or "see stage 0b/1")[:100])
    if not beat:
        print("  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              "DEGENERATE on this row.")
    else:
        print(f"  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS -- `{beat[0]['name']}`, "
              f"{beat[0]['pct_vs_r4ship_wp']:+.2f}% on W1. THE R4 SIDE OF THIS "
              f"ROW\n     WAS UNSEARCHED, and the headline `fixed-R4 bound` "
              f"above is a bound over an\n     UNSEARCHED endpoint. ⚠ The rung "
              f"does NOT move: `.memory/02-bench-rules.md` holds\n     R4 fixed "
              f"by fiat and that fiat is what makes the bound a bound.")
        base_ts = r4s.get("trusted_call_sites")
        cand_ts = beat[0].get("trusted_call_sites")
        if (base_ts is not None and cand_ts is not None
                and cand_ts < base_ts):
            print(f"     ⭐ AND IT IS NOT MERELY CHEAPER: its unchecked-"
                  f"dereference surface is {cand_ts} call\n        site(s) "
                  f"against the shipped rung's {base_ts} -- MEASURED, not "
                  f"asserted -- so it is cheaper AND\n        "
                  f"{base_ts - cand_ts} trusted call site(s) smaller. That is a "
                  f"STRONGER claim than the price\n        and it is stated "
                  f"separately.")
        elif base_ts is not None and cand_ts is not None:
            print(f"     ⚠ AND IT IS ONLY CHEAPER: its unchecked-dereference "
                  f"surface is {cand_ts} call site(s)\n        against the "
                  f"shipped rung's {base_ts}, so there is no trusted-surface "
                  f"claim to make.")
    if beat3:
        print(f"  ⚠⚠ AND THE R3 SIDE MOVES TOO -- `{beat3[0]['name']}`, "
              f"{beat3[0]['pct_vs_r4ship_wp']:+.2f}% on W1 against R4ship, "
              f"which is\n     cheaper than the shipped R3. **NEITHER published "
              f"endpoint is a searched endpoint.**")

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph45-htmlent-cache-int/controls/"
                "spellings.py --verus",
            "note":
                "The pin covers the two rung sources the variants are derived "
                "from, verus.rs (the R4 admissibility half), spec.md (the "
                "declaration the audit runs against AND the `identity` pin the "
                "admissibility rule reads), NOTES.md (whose section 8b carries "
                "the whole-program totals stage 3 reproduces), inputs/gen.py "
                "(the corpus every number is measured over) and this script. It "
                "does NOT cover results-php/ph45-htmlent-cache-int.json: stage 3 "
                "compares against that record at run time and prints the delta, "
                "which is a stronger check than a hash of it."},
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # ⚠⚠ REPO-RELATIVE KEYS, AND THE GATE MEASURES THAT (check.py stage 9b
        # re-hashes these against the REPO root). On a php row the REPO the gate
        # runs against is the shim root, where `patterns` is a symlink to
        # `patterns-php`, so `patterns/<row>/...` resolves in BOTH trees.
        "derived_from_sha256": {
            f"patterns/{ROW}/{rel}":
                hashlib.sha256(open(os.path.join(PDIR, rel), "rb").read()
                               ).hexdigest()
            for rel in ("safe_tuned.rs", "unsafe.rs", "verus.rs", "spec.md",
                        "NOTES.md", "inputs/gen.py", "controls/spellings.py")},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        "verus_checked": bool(args.verus),
        "identity_pinned": pinned,
        "identity_measured": measured,
        "identity_requires_byte_identity": need_ident,
        "identity_checked": ident_why,
        "statistic":
            "TWO FAMILIES, BOTH PUBLISHED, from one callgrind run per cell. A1 = "
            "kernel_exclusive_ir / n_iters -- harness/measure.py::_sum_rows "
            "itself, IMPORTED and not transcribed -- which stage 3 compares "
            "against results-php/ph45-htmlent-cache-int.json. W1 = whole-program "
            "Ir / n_iters off callgrind_annotate's PROGRAM TOTALS, which is the "
            "column NOTES.md section 8b publishes and which stage 3 compares "
            "against it. ⚠⚠ A1 SEES 9.5 % OF THIS ROW: `dec` is a separate "
            "symbol carrying ~90 % of every rung's instructions, every lever "
            "searched here lives in `dec`, and A1 therefore reports EVERY "
            "variant on a side as exactly 0.00 % with an unchanged kernel "
            "fingerprint. A control that priced this row in A1 alone would "
            "report both endpoints degenerate and would be wrong for a reason "
            "that has nothing to do with Rust.",
        "headline_statistic": "ir_per_call_small_wp",
        "reproduces_shipped_record": rec_ok,
        # ⚠ WHAT THAT BOOLEAN IS AND IS NOT ABOUT, because the field name reads
        # broader than what stage 3 verifies. It covers the two Ir FAMILIES at a
        # 0.5 % tolerance -- A1 against results-php/<row>.json and W1 against
        # NOTES.md section 8b -- and NOTHING ELSE. It says nothing about the
        # STATIC counts: `kernel_insns` here is 320 where the measurement
        # record's O3/isolated `n_fn_nopad` is 308, because this file counts
        # every disassembled instruction in the symbol while `asm.py` reports a
        # non-pad count, and because `dec_flush` inlines into `kernel`.
        # ⭐ The DELTA is what carries the meaning and it agrees exactly: 320-318
        # here against 308-306 in the record, i.e. -2 both ways.
        "reproduces_shipped_record_scope":
            "TWO Ir FAMILIES AT 0.5 % TOLERANCE, AND NOT THE STATIC COUNTS. A1 "
            "is compared against results-php/ph45-htmlent-cache-int.json and W1 "
            "against NOTES.md section 8b. `kernel_insns` below is a raw "
            "disassembled instruction count over the `kernel` symbol and is NOT "
            "comparable to the record's `n_fn_nopad` (320 vs 308): this file "
            "counts pad, `asm.py` does not, and `dec_flush` inlines into "
            "`kernel`. What IS comparable is the exec-vs-twin DELTA, which "
            "agrees with the record exactly at -2.",
        "r4_endpoint_degenerate": not beat,
        "r3_endpoint_degenerate": not beat3,
        # ⚠⚠ THE FIELD THAT SAYS A1 CANNOT RESOLVE THIS ROW, AND IT MEASURES
        # THE A1 SPREAD RATHER THAN THE FINGERPRINT. An earlier draft asked
        # whether every variant's `kernel` digest was equal; it is NOT -- three
        # of the four R3 variants and four of the five R4 variants have distinct
        # `kernel` code, because `dec_flush` is inlined into `kernel` and the
        # rip-relative displacement to `dec` moves when `dec`'s size does.
        # ⭐ The `kernel` symbol's CODE changes and its EXECUTED count does not
        # move at all, which is a sharper statement than the one the digest
        # supports and is the one the A1 column actually rests on.
        "a1_spread_pp": {
            side: (None if not vals else round(max(vals) - min(vals), 6))
            for side, vals in (
                (s, [r["pct_vs_r4ship_a1"] for r in rows.values()
                     if r.get("side") == s
                     and r.get("pct_vs_r4ship_a1") is not None])
                for s in RUNG_SIDES)},
        "kernel_digests_distinct": {
            side: len({r.get("kernel_fingerprint") for r in rows.values()
                       if r.get("side") == side and r.get("kernel_fingerprint")})
            for side in RUNG_SIDES},
        "wp_spread_pp": {
            side: (None if not vals else round(max(vals) - min(vals), 6))
            for side, vals in (
                (s, [r["pct_vs_r4ship_wp"] for r in rows.values()
                     if r.get("side") == s
                     and r.get("pct_vs_r4ship_wp") is not None])
                for s in RUNG_SIDES)},
        "toolchain": "rustc 1.97.1 / LLVM 22.1.6; Verus 0.2026.08.09.92f466f. "
                     "Inlining and unrolling are LLVM heuristics and on this row "
                     "the inline hint is worth ~40 percentage points, so every "
                     "figure here is about this toolchain.",
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "build_error",
                          "verus_build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "Every variant is in contract by harness/check.py::spelling_matches "
            "over EVERY backticked idiom entry, returns the shipped checksum on "
            "all eight inputs, and is priced in BOTH families by one callgrind "
            "run per cell. Every R4 variant additionally has its substitution "
            "applied to verus.rs and is put through Verus, and the ERROR TEXT is "
            "read: `is not supported` disqualifies, a failed postcondition does "
            "not. Byte-identity between an R4 variant and its twin is RECORDED "
            "and is not a bar, because spec.md pins `identity: differ` at both "
            "levels and the gate record measures `differ` -- both are read at run "
            "time by identity_premise() rather than assumed. TWO quantities ship "
            "in each family, labelled: the fixed-R4 bound and the R3-side span. "
            "NO PAIR INTERVAL.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
