#!/usr/bin/env python3
"""ph16 control -- **THE IN-CONTRACT SPELLING SPAN, BOTH SIDES SEARCHED.**

    python3 patterns-php/ph16-fdset-index/controls/spellings.py
    python3 patterns-php/ph16-fdset-index/controls/spellings.py --audit-only
    python3 patterns-php/ph16-fdset-index/controls/spellings.py --verus
    python3 patterns-php/ph16-fdset-index/controls/spellings.py --verus --attribute

⭐ **THE SECOND `controls/spellings.py` IN `patterns-php/`**, cloned from
`ph07-strcut-cursor/controls/spellings.py` (`TASK_PHP_018`, reviewed at
`TASK_PHP_022` §3). `../NOTES.md` §11 said this file was NOT BUILT and §8c said
the consequence in terms: *"Not a `fixed-R4 bound` with a counterpart ... the
`R3ship - R4ship` figure is the cost of THESE spellings of these rungs and
nothing more."* `TASK_PHP_028` discharges that.

WHAT SHIPS, AND WHAT THIS FILE DOES *NOT* DO
--------------------------------------------
⚠⚠⚠ **IT DOES NOT RE-SHIP A RUNG.** `.memory/02-bench-rules.md`: the shipped
rung is chosen by IDIOM, before measurement, and it stays. What a cheaper
in-contract spelling moves is the **published bound**, and TWO numbers ship,
labelled:

    fixed-R4 bound              R3ship - R4ship          both held by fiat
    cheapest-found in-contract  inf(R3 found) - R4ship   name the spelling
                                                          AND the input

and NO PAIR INTERVAL: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts
that construction in terms; this file does not resurrect it.

⚠⚠ **ON THIS ROW `R3ship - R4ship` IS NEGATIVE**, so that first line is not an
upper bound on the cost of safety -- it is a measurement, of two spellings, that
puts the safe rung under the unsafe one. **The question this file was written to
answer is whether that survives searching both sides. It does.** Stage 5 says
so and stage 6 says why.

⚠ **WHICH STATISTIC, because three of them are in circulation on this row and
they do not agree to the digit.** `.memory-php/02-ladder.md` quotes `ph07`'s
discharge as `+11.98 %`, which is the *marginal* figure -- `Ir` per window byte,
the slope through the two probe points. `TASK_PHP_028`'s own table quotes `ph16`
at `-1.22 %`, which is the *`small.bin` per-call* figure, i.e. the published
table's own ratio. On `ph07` the two agree to 0.6 pp and nobody had to choose;
here they are `-1.94 %` and `-1.22 %`. **All three are printed at every stage
and stage 5 publishes all three, labelled**, because picking one silently is how
a row acquires a headline nobody can re-derive. No conclusion below turns on the
choice: all three are negative and all three move the same way.

⚠ **AND A FOURTH KIND OF ANSWER IS RECORDED, BECAUSE FIVE OF THESE RESULTS ARE
BYTE-IDENTITY RESULTS AND A PERCENTAGE CANNOT SAY THAT.** Every variant's
`kernel` function is fingerprinted (`objdump`; operands and displacements kept,
crate hash and *addresses* normalised away -- see `kernel_fingerprint`, whose
first version got that distinction wrong, published a wrong claim on the
strength of it, and whose own negatives caught both one run later).
`r3_guard_r2`, `r3_u16`, `r4_hoistbase`, `r4_fold_index` and `r2x_guard_r3` are
not merely equal-cost: they are **the same machine code** as the rung they
respell, which is a stronger and more useful statement than `0.00 %`.
`r3_head_array` and `r3_split_at` are the other case -- different code, and
`r3_head_array` at identical cost -- and the fingerprint is what keeps the two
apart.

THE MECHANISM, AND IT IS WHY THE CANDIDATE SET LOOKS LIKE THIS
--------------------------------------------------------------
⚠⚠⚠ **THE CANDIDATES ARE NOT SPELLINGS SOMEBODY THOUGHT OF. THEY ARE THE
INSTRUCTIONS THAT ARE THERE.** `--attribute` runs callgrind with
`--dump-instr=yes` on the two shipped rungs and decomposes `R4ship - R3ship`
into **execution-count classes** -- exact, not thresholded, because the two
rungs run the same control flow on the same data, so a block's execution count
identifies it in both binaries. On `small.bin`, O3/isolated, 25 000 calls:

    R4 is CHEAPER off the entry loops  -450 686 Ir   -18.0 Ir/call
      R3's four range-slicings and its header index reads carry bounds tests
      that R4's `get_unchecked` does not. THIS IS THE SAFETY SAVING, IT IS
      REAL, AND IT IS THE ONLY PLACE R4 IS AHEAD.
    R4 is DEARER in arm 2's entry loop +1 550 414 Ir  +62.0 Ir/call
      ONE extra `lea (%rsi,%rdx,1),%rcx` per entry, because `to_fd_set(win,
      base, n)` indexes `win` ABSOLUTELY and LLVM could not fold the runtime
      `base` into the addressing mode in that ONE of three inlined copies.
      Arm 1 (`base == 0`) folds it; arm 3 is strength-reduced to a pointer;
      arm 2 is not.
    ----------------------------------------------------------------------
    net                                +1 099 728 Ir  +44.0 Ir/call

and `+1 099 728` is `89 974 452 - 88 874 724` **exactly** -- the `unsafe` minus
`safe_tuned` cell of `results-php/ph16-fdset-index.json`. ⚠ **How you would know
this candidate set were too narrow: the decomposition would not close.** It
closes to 0 Ir, and stage 6 fails the run if it ever stops closing.

⭐⭐ **AND THE ANSWER IS NOT THE ONE THAT MECHANISM PREDICTS.** Four independent
respellings of that index were built and priced -- `r4_hoistbase`,
`r4_cursor`, `r4x_endcursor` and `r4x_subslice`, the last of which is *R3's own
spelling* -- and **not one of them is cheaper than the shipped R4**: they come
in at +0.00 % (byte-identical), +3.74 %, +4.34 % and +1.80 %. The `lea` is not
an accident of how the index was written; it is what carrying `base` as an
argument costs, and every way of not carrying it costs more. **So the R4
endpoint on this row is DEGENERATE, and `R3ship - R4ship` is a spread over a
SEARCHED endpoint.**

⭐⭐⭐ **THE MIRROR CONTROL IS THE ONE THAT SETTLES WHAT THE SPREAD IS, AND IT
IS `r3_absindex`.** R3 respelled with R4's `(win, base, n)` signature and an
absolute index is **byte-identical machine code to `safe_naive.rs`** (483
instructions, same fingerprint) and measures **+31.5 %** against the shipped R4.
So the subslice signature is worth **-24.9 % (`small.bin`) / -26.9 % (slope)**
in the safe rung and **+1.8 %** in the unsafe one -- *the two rungs' cheapest
spellings are different spellings*,
and R3's minimum sits below R4's minimum. **That is a non-monotone ladder with
both endpoints searched, not a badly written R4.** ⚠ n = 1 row. Nothing here
generalises past `ph16`.

⚠⚠ **AND IT REFUTES `../NOTES.md` §8b, WHICH IS THIS ROW'S PUBLISHED MECHANISM
FOR THE R2 -> R3 GAP.** §8b, and the module comments of both `safe_naive.rs`
and `safe_tuned.rs`, say the R2 -> R3 lever is the *guard respelling*: *"in R2
the guard bounds `this_fd` and the index is `this_fd / 64`, and rustc emits a
second bounds check on `fds[..]`; in R3 the guard bounds the index itself and
there is nothing left to check."* **Measured, in both directions, and the guard
respelling emits BYTE-IDENTICAL MACHINE CODE either way**: `r3_guard_r2` (R2's
guard spelling put into R3) is the shipped R3's own fingerprint, and
`r2x_guard_r3` (R3's guard spelling put into R2) is `safe_naive.rs`'s own
fingerprint. rustc elides the second test under BOTH spellings. The whole
R2 -> R3 gap is item 2 of `safe_tuned.rs`'s module comment -- the subslice and
`chunks_exact(2)` -- and item 1 is worth **zero instructions**.
⚠ **The two rung sources are pinned into the MEASUREMENT record
(`source_sha256`, 19 files), so correcting their comments costs a 28-cell
re-measure. `../NOTES.md` is not, and carries the correction. Whether the rung
comments follow is the manager's call.**

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of.

⚠ **FOUR SIDES, and only two of them can move a published number.** `R3` and
`R4` are rung candidates. `R4x` is an **exec-only R4 control**: priced, but no
Verus twin was attempted, so it is not a rung (`../spec.md` pins
`identity: unsafe == verus`). It is admissible as *evidence* anyway and the
argument is arithmetic rather than charitable: **both `R4x` entries are DEARER
than the shipped R4, and a dearer candidate cannot move a bound whose
denominator is `R4ship` whether or not it verifies.** Had either come in
cheaper, this file would owe it a twin and would say so. `R2x` is an exec-only
R2 control and exists only to settle §8b above.

R3 side, from `../safe_tuned.rs` -- all safe, no `unsafe` token:

  `v0_shipped`      the shipped R3, unmodified.
  `r3_split_at`     ⭐ the three `&ents[a..b]` range slicings replaced by one
                    `split_at` pair: same three subslices, two bounds tests
                    instead of three, and computed UNCONDITIONALLY where the
                    shipped form computes each inside its own arm's `if`. This
                    is the cheapest R3 found: **-7.0 Ir/call, entirely in the
                    fixed term**, which is the size of lever stage 6 says exists
                    on this side.
  `r3_head_array`   the six header reads taken through one `&win[0..6]`
                    slicing. DIFFERENT machine code, IDENTICAL cost: rustc
                    already merges the six tests.
  `r3_prologue`     `r3_split_at` and `r3_head_array` composed -- they do NOT
                    compose, which is the useful part: the pair costs exactly
                    what `r3_split_at` costs alone.
  `r3_u16`          `u16::from_le_bytes([c[0], c[1]])` for the entry decode.
                    BYTE-IDENTICAL. Included because a search whose every entry
                    moves is a search that has not found its floor.
  `r3_guard_r2`     ⚠ the row's own R2 spelling of guard (b), `if this_fd <
                    FD_SETSIZE { fds[(this_fd / 64) as usize] |= ... }`. IN
                    CONTRACT -- `this_fd < FD_SETSIZE` is a `required` token of
                    `../spec.md` `idiom.required[5]`, not a banned one -- and
                    identical over all 16 384 reachable values
                    (`controls/guard_equiv.py`). Expected DEARER by §8b.
                    **Measured BYTE-IDENTICAL**, which is what refutes §8b.
  `r3_index_walk`   ⚠ THE FIRST REAL LOSER: R2's index walk (`while i + 1 <
                    run.len()`) over the same subslice, instead of
                    `chunks_exact(2)`. **+6.15 %.** So half the loop-form lever
                    is the iterator and half is the subslice.
  `r3_absindex`     ⚠⚠ THE MIRROR CONTROL AND THE BIG LOSER: R3 given R4's
                    `(win, base, n)` signature and absolute indexing. **+33.1 %
                    against the shipped R3, and byte-identical to
                    `safe_naive.rs`.** Two losers on two axes plus this one is
                    what makes the winners' margins readable, and it is the
                    control the whole non-monotonicity claim rests on.

R4 side, from `../unsafe.rs` -- ⚠⚠ **`../spec.md` pins `identity: unsafe ==
verus` (`exact` at O3), so an R4 candidate is not merely a program that MAY use
`unsafe`: it must have a `verus.rs` twin that VERIFIES.** Each `R4` variant's
substitution is applied to `../verus.rs` as well and the result is put through
Verus; one that does not verify is a CONTROL and not a rung, which is `p16`'s
`r4_hdr`, `p42`'s `endptr` and `ph07`'s `r4_nozero` precedent.

  `v0_shipped`      the shipped R4, unmodified.
  `r4_cursor`       the entry offset carried as a CURSOR beside `i`:
                    `let mut j = 6 + 2 * base;` before the loop, `j = j + 2;`
                    in it. The twin needs ONE more invariant, `j == 6 + 2 *
                    (base + i)`, and no new trusted item and no new proof term.
                    VERIFIES. **+3.74 %** -- two induction variables where LLVM
                    was already maintaining one.
  `r4_hoistbase`    the same idea spelled the other way -- `let b = 6 + 2 *
                    base;` hoisted, `let j = b + 2 * i;` inside. ⭐ **BYTE-
                    IDENTICAL machine code to the shipped R4** (LLVM already
                    re-associates it) **and its twin DOES NOT VERIFY** (14/1).
                    A free respelling that the prover cannot follow is
                    inadmissible as a rung, and that asymmetry is worth having
                    in the record: on this row `identity: exact` would have
                    held and the proof is what refuses.
  `r4_fold_index`   `s[i]` for `aget_unchecked(s, i)` in `fold_set`. `s` is a
                    `&[u64; NW]` and the loop is `while i < NW`, so rustc
                    elides the test. VERIFIES, **costs the same to the
                    instruction**, and **removes one of two uses of a trusted
                    item** -- a smaller trusted surface at the same price, which
                    is `ph07`'s `r4_index0` third kind of result and `p34`'s
                    `r4_readdirect` shape, re-derived here. ⭐ **BYTE-
                    IDENTICAL machine code to the shipped R4**, which is
                    `ph07`'s result exactly. ⚠ This entry read *"NOT
                    byte-identical, unlike ph07's"* until the negatives found
                    `kernel_fingerprint` layout-sensitive; the two digests
                    differed only in addresses.
  `r4_cursor_fold`  `r4_cursor` and `r4_fold_index` composed. VERIFIES,
                    **+3.74 %** -- it inherits the cursor's loss exactly, which
                    is the check that the two edits are independent.

R4x -- exec-only R4 controls, priced, no twin attempted, both DEARER:

  `r4x_endcursor`   the cursor with `i` DELETED: one induction variable bounded
                    by `end = 6 + 2 * (base + n)`, the closest R4 can get to
                    R3's `chunks_exact` without changing its signature.
                    **+4.34 %.**
  `r4x_subslice`    ⭐ THE DECISIVE ONE: the arm's entries taken as a SUBSLICE
                    once -- `&win[6 + 2 * base..6 + 2 * (base + n)]`, which is
                    exactly what R3 does -- with the reads still unchecked.
                    **+1.80 %.** ⚠ **This is the candidate whose failure makes
                    the R4 endpoint degenerate**: the one spelling that removes
                    arm 2's `lea` pays more for the slice than the `lea` costs.
                    A twin was not attempted because it cannot move the bound;
                    it would need `run@ =~= win@.subrange(...)` threaded through
                    `walk`'s spec, which is a spec rewrite and not a
                    substitution, and `../spec.md`'s `verus.items` pins those
                    items.

R2x -- exec-only R2 controls, for §8b and nothing else:

  `r2x_shipped`     `../safe_naive.rs`, unmodified, so `r2x_guard_r3` has a
                    baseline in this file's own statistic.
  `r2x_guard_r3`    R3's `w < NW` guard spelling put into R2. **BYTE-IDENTICAL
                    to `r2x_shipped`.** With `r3_guard_r2` this is the
                    refutation of §8b in both directions.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**. A variant
    nobody audited is a number about a different benchmark (`p05`'s lesson).
    ⚠ The token audit is not the whole admission test: `../spec.md`'s per-entry
    ENGLISH decides polarity and scope and no gate stage reproduces it, so
    `admissible` is THREE-VALUED here and the third value is a sentence.
    ⚠⚠ **AND ON THIS ROW THE AUDIT HAS TEETH, WHICH IS NOT TRUE OF EVERY PHP
    ROW.** `results-php/gate/ph16-fdset-index.json`'s `idiom_audit` counts **23**
    backticked spellings, 13 `required` and 10 `forbidden` -- against **4** on
    `ph29`, whose `required` half backticks NOTHING at all. The `forbidden` set
    here even includes the word `forbidden` itself (`idiom.forbidden[1]`
    backticks its own prose), so a variant that writes that word in EXEC CODE is
    refused. ⚠ **NOT in a comment, and a first draft of this line said
    otherwise**: `spelling_matches` matches against `exec_code(src)`, which
    blanks comments, string literals, Verus ghost code and cfg-gated code
    (`vparse.blank_noncode`, five layers, measured at TASK_069) -- so the ban is
    on the program and not on the file, and a variant could carry `volatile` in
    a comment and this audit would not see it. That is the right rule and it is
    also a hole; it is `check.py`'s rule and this file does not invent a
    stricter one. It is also the audit that DISTINGUISHES `r3_guard_r2`: that
    variant swaps which of `required[5]`'s two guard spellings it satisfies,
    which is visible in `required_absent` and is the check that the substitution
    did what it claims.
  * every variant returns the SHIPPED checksum on every one of the six inputs,
    adversarial included, compared against **R3 `v0_shipped`** rather than
    against its own side's baseline -- because the row pins every Rust rung to
    one checksum per input and the gate asserts it, so this is the stronger
    comparison. R4's and R2's agreement with R3 is asserted explicitly.
  * ⚠⚠ **`Ir` per kernel call is measured the way `harness/measure.py` MEASURES
    THE SHIPPED CELLS** -- kernel-exclusive `Ir` off the pinned callgrind on the
    SHIPPED `small.bin` and `large.bin` at their own `n_iters`, divided by
    `n_iters` -- and NOT by `check.py`'s 100-vs-200 marginal. `ph07`'s first
    draft used the 100/200 marginal and its `v0_shipped` figures came out **1 %
    from the record**. They are different statistics, not a discrepancy: the
    driver picks its window from a checksum, so 200 iterations visit a different
    SAMPLE of the 32 or 2 050 windows from 25 000. **A control that is going to
    be quoted beside the row's headline has to compute the row's headline.**
  * the pipeline reproduces the SHIPPED cells' recorded numbers before any
    variant is quoted, and prints the delta. On this row it reproduces all four
    **to the digit** -- stage 3.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**
"""

import argparse
import collections
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
SCRATCH = os.path.join(REPO, ".temp", "php28", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph16-fdset-index.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph16-fdset-index.json`
#: carries and therefore what `../NOTES.md` §8 quotes. The strides are the
#: `work_per_call` the gate derives, and `collapse.probe_inputs` names the pair.
PROBES = (("small.bin", 550, 25_000), ("large.bin", 4076, 12_000))
#: Below this, two cells are a TIE and neither is "cheaper". Inherited from
#: `ph07`, where it was set at ~15x the largest difference seen between two runs
#: of one binary. ⚠ On THIS row callgrind is deterministic to the instruction --
#: stage 3 reproduces all four shipped cells exactly -- so the only thing this
#: threshold protects against is over-reading a real but negligible margin. The
#: three ties below are byte-identity or instruction-exact, not near-misses.
TIE_PCT = 0.05
#: The side a variant's checksum and its shipped baseline come from.
BASE_FILE = {"R3": "safe_tuned.rs", "R4": "unsafe.rs", "R4x": "unsafe.rs",
             "R2x": "safe_naive.rs"}
#: Only these sides can move a published number; see the four-sides note above.
RUNG_SIDES = ("R3", "R4")

# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]})
# `file` is "rs" for the rung source and "verus" for the R5 twin; a side outside
# RUNG_SIDES never materialises a twin.

_HEAD_ARRAY = [
    ("""    let ctl: u32 = (win[0] as u32) | ((win[1] as u32) << 8);
    let split_r: u32 = (win[2] as u32) | ((win[3] as u32) << 8);
    let split_w: u32 = (win[4] as u32) | ((win[5] as u32) << 8);
""",
     """    let hd: &[u8] = &win[0..6];
    let ctl: u32 = (hd[0] as u32) | ((hd[1] as u32) << 8);
    let split_r: u32 = (hd[2] as u32) | ((hd[3] as u32) << 8);
    let split_w: u32 = (hd[4] as u32) | ((hd[5] as u32) << 8);
""", 1),
]

_SPLIT_AT = [
    ("    let ents: &[u8] = &win[6..6 + 2 * m];\n",
     "    let ents: &[u8] = &win[6..6 + 2 * m];\n"
     "    let (ents_r, ents_rest) = ents.split_at(2 * n_r);\n"
     "    let (ents_w, ents_e) = ents_rest.split_at(2 * n_w);\n", 1),
    ("        sets += to_fd_set(&ents[0..2 * n_r], ctl & 8 != 0, "
     "&mut rfds, &mut max_fd);\n",
     "        sets += to_fd_set(ents_r, ctl & 8 != 0, &mut rfds, &mut max_fd);\n",
     1),
    ("""        sets += to_fd_set(&ents[2 * n_r..2 * (n_r + n_w)], ctl & 16 != 0,
                          &mut wfds, &mut max_fd);
""",
     "        sets += to_fd_set(ents_w, ctl & 16 != 0, &mut wfds, &mut max_fd);\n",
     1),
    ("""        sets += to_fd_set(&ents[2 * (n_r + n_w)..2 * (n_r + n_w + n_e)],
                          ctl & 32 != 0, &mut efds, &mut max_fd);
""",
     "        sets += to_fd_set(ents_e, ctl & 32 != 0, &mut efds, &mut max_fd);\n",
     1),
]

#: R2's spelling of guard (b) and R3's, as one pair of strings used in BOTH
#: directions -- `r3_guard_r2` applies it one way and `r2x_guard_r3` the other,
#: which is what makes §8b decidable rather than arguable.
_GUARD_R3 = """                let w: usize = (this_fd / 64) as usize;
                if w < NW {
                    fds[w] |= 1u64 << (this_fd % 64);
                }
"""
_GUARD_R2 = """                if this_fd < FD_SETSIZE {
                    fds[(this_fd / 64) as usize] |= 1u64 << (this_fd % 64);
                }
"""

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}),
    ("r3_split_at", "R3",
     "the three `&ents[a..b]` range slicings replaced by one `split_at` pair -- "
     "same three subslices, two bounds tests instead of three, computed "
     "unconditionally. THE CHEAPEST R3 FOUND, and the whole of it is in the "
     "fixed term",
     {"rs": _SPLIT_AT}),
    ("r3_head_array", "R3",
     "the six header reads taken through one `&win[0..6]` slicing. Different "
     "machine code, identical cost -- rustc already merges the six tests",
     {"rs": _HEAD_ARRAY}),
    ("r3_prologue", "R3",
     "r3_split_at and r3_head_array composed. They do NOT compose: the pair "
     "costs exactly what r3_split_at costs alone",
     {"rs": _HEAD_ARRAY + _SPLIT_AT}),
    ("r3_u16", "R3",
     "`u16::from_le_bytes([c[0], c[1]])` for the entry decode. Byte-identical; "
     "a search whose every entry moves has not found its floor",
     {"rs": [("        let e: u32 = (c[0] as u32) | ((c[1] as u32) << 8);\n",
              "        let e: u32 = u16::from_le_bytes([c[0], c[1]]) as u32;\n",
              1)]}),
    ("r3_guard_r2", "R3",
     "the row's own R2 spelling of guard (b). In contract (`this_fd < "
     "FD_SETSIZE` is a `required` token), identical over all 16 384 reachable "
     "values, expected DEARER by NOTES.md 8b -- and measured BYTE-IDENTICAL, "
     "which is what refutes 8b",
     {"rs": [(_GUARD_R3, _GUARD_R2, 1)]}),
    ("r3_index_walk", "R3",
     "THE FIRST REAL LOSER: R2's index walk over the same subslice instead of "
     "`chunks_exact(2)`, so the per-entry index computation and its bounds test "
     "come back into the loop",
     {"rs": [("""    for c in run.chunks_exact(2) {
        let e: u32 = (c[0] as u32) | ((c[1] as u32) << 8);
""",
              """    let mut i: usize = 0;
    while i + 1 < run.len() {
        let e: u32 = (run[i] as u32) | ((run[i + 1] as u32) << 8);
""", 1),
             ("""            }
        }
    }
    1
}
""",
              """            }
        }
        i = i + 2;
    }
    1
}
""", 1)]}),
    ("r3_absindex", "R3",
     "THE MIRROR CONTROL: R3 given R4's `(win, base, n)` signature and absolute "
     "indexing. Byte-identical to safe_naive.rs, and the control the "
     "non-monotonicity claim rests on -- the subslice signature is worth -24.9% "
     "(small.bin) / -26.9% (slope) in the safe rung and +1.8% in the unsafe one",
     {"rs": [("fn to_fd_set(run: &[u8], not_an_array: bool,\n",
              "fn to_fd_set(win: &[u8], base: usize, n: usize, "
              "not_an_array: bool,\n", 1),
             ("""    for c in run.chunks_exact(2) {
        let e: u32 = (c[0] as u32) | ((c[1] as u32) << 8);
""",
              """    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
        let e: u32 = (win[j] as u32) | ((win[j + 1] as u32) << 8);
""", 1),
             ("""            }
        }
    }
    1
}
""",
              """            }
        }
        i = i + 1;
    }
    1
}
""", 1),
             ("    let ents: &[u8] = &win[6..6 + 2 * m];\n", "", 1),
             ("        sets += to_fd_set(&ents[0..2 * n_r], ctl & 8 != 0, "
              "&mut rfds, &mut max_fd);\n",
              "        sets += to_fd_set(win, 0, n_r, ctl & 8 != 0, "
              "&mut rfds, &mut max_fd);\n", 1),
             ("""        sets += to_fd_set(&ents[2 * n_r..2 * (n_r + n_w)], ctl & 16 != 0,
                          &mut wfds, &mut max_fd);
""",
              "        sets += to_fd_set(win, n_r, n_w, ctl & 16 != 0, "
              "&mut wfds, &mut max_fd);\n", 1),
             ("""        sets += to_fd_set(&ents[2 * (n_r + n_w)..2 * (n_r + n_w + n_e)],
                          ctl & 32 != 0, &mut efds, &mut max_fd);
""",
              "        sets += to_fd_set(win, n_r + n_w, n_e, ctl & 32 != 0, "
              "&mut efds, &mut max_fd);\n", 1)]}),
]

# --- R4: the index, spelled four ways, and the fold ------------------------
_CURSOR_RS = [
    ("""    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
""",
     """    let mut i: usize = 0;
    let mut j: usize = 6 + 2 * base;
    while i < n {
""", 1),
    ("""        i = i + 1;
    }
    1
}
""",
     """        i = i + 1;
        j = j + 2;
    }
    1
}
""", 1),
]
_CURSOR_VERUS = [
    ("""    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            6 + 2 * (base + n) <= win@.len(),
            win@.len() <= usize::MAX,
            fds@.len() == NW,
            walk(win@, base as int, i as int, n as int, fds@, *max_fd) == target,
        decreases n - i,
    {
        assert(6 + 2 * (base + i) <= win@.len());
        let j: usize = 6 + 2 * (base + i);
""",
     """    let mut i: usize = 0;
    let mut j: usize = 6 + 2 * base;
    while i < n
        invariant
            i <= n,
            6 + 2 * (base + n) <= win@.len(),
            win@.len() <= usize::MAX,
            fds@.len() == NW,
            j == 6 + 2 * (base + i),
            walk(win@, base as int, i as int, n as int, fds@, *max_fd) == target,
        decreases n - i,
    {
        assert(6 + 2 * (base + i) <= win@.len());
""", 1),
    ("""        i = i + 1;
    }
    1
}
""",
     """        i = i + 1;
        j = j + 2;
    }
    1
}
""", 1),
]
_HOIST_RS = [
    ("""    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
""",
     """    let mut i: usize = 0;
    let b: usize = 6 + 2 * base;
    while i < n {
        let j: usize = b + 2 * i;
""", 1),
]
_HOIST_VERUS = [
    ("""    let mut i: usize = 0;
    while i < n
""",
     """    let mut i: usize = 0;
    let b: usize = 6 + 2 * base;
    while i < n
""", 1),
    ("        let j: usize = 6 + 2 * (base + i);\n",
     "        let j: usize = b + 2 * i;\n", 1),
]
_FOLD_INDEX = [
    ("        h = h.wrapping_mul(31).wrapping_add(aget_unchecked(s, i));\n",
     "        h = h.wrapping_mul(31).wrapping_add(s[i]);\n", 1),
]

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}),
    ("r4_cursor", "R4",
     "the entry offset carried as a CURSOR beside `i`. The twin needs ONE more "
     "invariant, `j == 6 + 2 * (base + i)`: no new trusted item, no new proof "
     "term. DEARER -- two induction variables where LLVM was maintaining one",
     {"rs": _CURSOR_RS, "verus": _CURSOR_VERUS}),
    ("r4_hoistbase", "R4",
     "the same idea spelled the other way: `let b = 6 + 2 * base;` hoisted. "
     "BYTE-IDENTICAL machine code to the shipped R4 -- LLVM already "
     "re-associates it -- and its twin DOES NOT VERIFY. A free respelling the "
     "prover cannot follow is inadmissible as a rung",
     {"rs": _HOIST_RS, "verus": _HOIST_VERUS}),
    ("r4_fold_index", "R4",
     "`s[i]` for `aget_unchecked(s, i)` in `fold_set`. Verifies, costs the same "
     "to the instruction, and removes one of two uses of a trusted item -- a "
     "smaller trusted surface at the same price (ph07 `r4_index0`, p34 "
     "`r4_readdirect`). BYTE-IDENTICAL machine code to the shipped R4, which "
     "is ph07's result exactly -- this said the opposite until the negatives "
     "found kernel_fingerprint layout-sensitive",
     {"rs": _FOLD_INDEX, "verus": _FOLD_INDEX}),
    ("r4_cursor_fold", "R4",
     "r4_cursor and r4_fold_index composed. It inherits the cursor's loss "
     "exactly, which is the check that the two edits are independent",
     {"rs": _CURSOR_RS + _FOLD_INDEX,
      "verus": _CURSOR_VERUS + _FOLD_INDEX}),
]

R4X_VARIANTS = [
    ("r4x_endcursor", "R4x",
     "the cursor with `i` DELETED: one induction variable bounded by "
     "`end = 6 + 2 * (base + n)`, the closest R4 gets to R3's `chunks_exact` "
     "without changing its signature. DEARER, so no twin was attempted",
     {"rs": [("""    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
""",
              """    let mut j: usize = 6 + 2 * base;
    let end: usize = 6 + 2 * (base + n);
    while j < end {
""", 1),
             ("""        i = i + 1;
    }
    1
}
""",
              """        j = j + 2;
    }
    1
}
""", 1)]}),
    ("r4x_subslice", "R4x",
     "THE DECISIVE ONE: the arm's entries taken as a SUBSLICE once -- exactly "
     "what R3 does -- with the reads still unchecked. The one spelling that "
     "removes arm 2's `lea`, and it pays more for the slice than the `lea` "
     "costs. Its failure is what makes the R4 endpoint degenerate. No twin: it "
     "would need `run@ =~= win@.subrange(...)` threaded through `walk`'s spec, "
     "which is a spec rewrite and not a substitution, and it cannot move a "
     "bound it is DEARER than",
     {"rs": [("""    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
        let e: u32 = (get_unchecked(win, j) as u32)
                   | ((get_unchecked(win, j + 1) as u32) << 8);
""",
              """    let run: &[u8] = &win[6 + 2 * base..6 + 2 * (base + n)];
    let mut i: usize = 0;
    while i < n {
        let e: u32 = (get_unchecked(run, 2 * i) as u32)
                   | ((get_unchecked(run, 2 * i + 1) as u32) << 8);
""", 1)]}),
]

R2X_VARIANTS = [
    ("r2x_shipped", "R2x",
     "../safe_naive.rs unmodified, so r2x_guard_r3 has a baseline in this "
     "file's own statistic", {}),
    ("r2x_guard_r3", "R2x",
     "R3's `w < NW` guard spelling put into R2. BYTE-IDENTICAL to r2x_shipped; "
     "with r3_guard_r2 this is NOTES.md 8b refuted in both directions",
     {"rs": [(_GUARD_R2, _GUARD_R3, 1)]}),
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
    """`harness/measure.py`, loaded exactly the way `load_check()` loads
    `check.py`, and cached.

    ⚠⚠⚠ IMPORTED, NOT TRANSCRIBED. `ph07`'s copy of this function carries the
    argument in full and it is the reason this one exists: `TASK_PHP_022` §3.2
    measured that a transcription of `measure.py::_sum_rows` is a DIFFERENT
    function -- it took the FIRST matching annotate row and `break`ed where
    `measure.py` SUMS all of them, matched `":kernel" in line` on the whole line
    where `measure.py` matches on the FUNCTION FIELD, and did not check
    callgrind's return code -- and that both failure modes produce a PLAUSIBLE
    WRONG NUMBER rather than an error. Importing `harness/measure.py` is NOT an
    edit to it; `PLAN_PHP.md` §2.1 forbids writing under `harness/`, and reading
    is what the whole shim is built to do.
    ⚠ It is imported LAZILY so that `--audit-only`, which prices nothing, does
    not pay for `measure.py`'s own imports of `slb`, `asm` and `build`.
    """
    global _MEASURE
    if _MEASURE is None:
        _MEASURE = _load("slb_measure", ("harness", "measure.py"))
    return _MEASURE


def contract():
    txt = open(os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt,
                                re.S).group(1))


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

    ⚠ A twin is materialised for `R4` ONLY. `R4x` and `R2x` are exec-only
    controls by construction and a twin that was never attempted must not be
    confusable with one that failed."""
    os.makedirs(SCRATCH, exist_ok=True)
    src = open(os.path.join(PDIR, BASE_FILE[side]), encoding="utf-8").read()
    src = apply_subs(src, subs.get("rs", []))
    src = src.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
    p = os.path.join(SCRATCH, f"{side}_{name}.rs")
    open(p, "w", encoding="utf-8").write(src)
    vp = None
    if side == "R4":
        v = open(os.path.join(PDIR, "verus.rs"), encoding="utf-8").read()
        v = apply_subs(v, subs.get("verus", subs.get("rs", [])))
        v = v.replace('#[path = "../../common/driver.rs"]',
                      f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')
        vp = os.path.join(SCRATCH, f"{side}_{name}_verus.rs")
        open(vp, "w", encoding="utf-8").write(v)
    return p, vp


def build(rs, out):
    """`harness/build.py`'s own rustc flags for an `-O3 isolated` cell."""
    cmd = [RUSTC, "--edition", "2021", "-C", "codegen-units=1",
           "-C", "opt-level=3", "-C", "debug-assertions=off",
           "--cfg", "slb_isolated", rs, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return (out, None) if r.returncode == 0 else (None, r.stderr[-1500:])


def run(exe, path):
    r = subprocess.run([exe, path], capture_output=True, text=True, timeout=900)
    return r.stdout.strip()


def kernel_ir(exe, path, tag, dump_instr=False):
    """`(kernel_exclusive_ir, error_or_None)` off the pinned callgrind.

    ⚠⚠ THE STATISTIC IS `harness/measure.py::_sum_rows`, IMPORTED. See
    `load_measure()`. Three behaviours come with the import: annotate rows are
    SUMMED rather than first-one-wins; the needle is matched on the FUNCTION
    FIELD, so a sibling `kernel_prologue` cannot be read as `kernel`; and
    `stdout + stderr` is scanned, as `measure.py::sh` does. Callgrind's RETURN
    CODE is checked, because a crashed valgrind used to produce `None` that read
    as *"no kernel figure"* rather than as *"the measurement did not happen"* --
    probe rule 1.

    `dump_instr` adds `--dump-instr=yes` and KEEPS the output file, which is
    what `--attribute` reads. It does not change the statistic: the same
    `callgrind_annotate` sum is returned either way, and stage 6 FAILS the run
    if the per-instruction sum is not that same figure.
    """
    M = load_measure()
    out = os.path.join(SCRATCH, f"cg.{tag}")
    cmd = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out]
    if dump_instr:
        cmd.append("--dump-instr=yes")
    r = subprocess.run(cmd + [exe, path],
                       capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        if os.path.exists(out) and not dump_instr:
            os.unlink(out)
        return None, (f"callgrind exit {r.returncode} on {tag}: "
                      f"{r.stderr[-200:]}")
    ann = subprocess.run(
        [M.CG_ANNOTATE, "--threshold=100", out],
        capture_output=True, text=True, timeout=600)
    tot, names = M._sum_rows((ann.stdout + ann.stderr).strip(), "kernel")
    if os.path.exists(out) and not dump_instr:
        os.unlink(out)
    if tot is None:
        return None, (f"callgrind_annotate named no `kernel` function for "
                      f"{tag} (rc {ann.returncode})")
    return tot, None


_NAME = re.compile(r"^\((\d+)\)\s*(.*)$")


def per_instruction(cgfile, needle="kernel"):
    """`{address: Ir}` for every instruction of the `kernel` function, out of a
    callgrind file dumped with `--dump-instr=yes`.

    ⚠ FOUR THINGS THIS FORMAT WILL GET WRONG IF THEY ARE NOT HANDLED, and every
    one of them was live while this was written:

      * **name compression.** `fn=(7) foo` defines id 7 and `fn=(7)` reuses it.
        A parser that keys on the literal string attributes every later block of
        the same function to a name of `"(7)"`, and the hot function then
        appears twice with a fraction of its cost each.
      * ⚠⚠ **AND THE NAME CAN BE INTRODUCED ON A `cfn=` LINE.** `fn` and `cfn`
        SHARE the compression namespace, so a callee named for the first time as
        `cfn=(5004) R3::kernel` is thereafter referred to as a bare `fn=(5004)`
        — and a parser that learns names from `fn=` alone never resolves it and
        returns **ZERO** for the hot function. **This is not hypothetical and it
        is not stable across builds**: two dumps of the same rung, taken hours
        apart, differed in which line introduced the name, so the first version
        of this function worked on one and returned 0 on the other. It was found
        by `.temp/php28/asm/remake.py` — a script written only to regenerate a
        deleted blob — and it FAILED LOUDLY rather than silently, because of the
        arithmetic check below. That is the failure mode probe rule 1 asks for,
        and it is the reason the check is not optional.
      * **`calls=` cost lines are INCLUSIVE.** The position line immediately
        after a `calls=` line is the cost of the CALLEE, not of the caller's
        instruction, and counting it makes `main` look as though it executed
        90 M instructions itself. Skipped here.
      * **relative subpositions.** `+8`, `-4` and `*` are offsets from the last
        address in the same block, not addresses.

    The check that all four are handled is arithmetic and stage 6 runs it: the
    returned dict must sum to EXACTLY the `callgrind_annotate` figure for the
    same run, which is `measure.py`'s own statistic. **Stage 6 appends a
    `problems` entry — which fails the gate — when it does not.**
    """
    names, cur, per, last, skip = {}, None, collections.Counter(), 0, False
    for line in open(cgfile, errors="replace"):
        line = line.rstrip("\n")
        if line.startswith(("fn=", "cfn=")):
            caller = line.startswith("fn=")
            v = line.split("=", 1)[1]
            m = _NAME.match(v)
            if m:
                if m.group(2):
                    names[m.group(1)] = m.group(2)
                if caller:
                    cur = names.get(m.group(1), "?" + m.group(1))
            elif caller:
                cur = v
            if caller:
                last, skip = 0, False
            continue
        if line.startswith("calls="):
            skip = True
            continue
        if line.startswith(("fl=", "ob=", "cfi=", "cob=", "cfl=",
                            "jump=", "jcnd=")):
            continue
        m = re.match(r"^(0x[0-9a-f]+|\+\d+|-\d+|\*)\s+(\d+)\s+(\d+)", line)
        if not (m and cur):
            continue
        a = m.group(1)
        last = (int(a, 16) if a.startswith("0x")
                else last if a == "*" else last + int(a))
        if skip:
            skip = False
            continue
        if needle in cur:
            per[last] += int(m.group(3))
    return per


def disasm(exe):
    """`{address: text}` for the `kernel` function only.

    ⚠ `harness/asm.py` is *the* objdump caller in `harness/`, and this is not
    an edit to it: six PAT patterns' `controls/` disassemble directly for
    exactly this reason (`CLAUDE.md` -- *the GATE has one pipeline, not the
    tree*). What is needed here is per-INSTRUCTION text keyed by address, which
    `asm.py` does not return.
    """
    r = subprocess.run(["objdump", "-d", "--no-show-raw-insn", exe],
                       capture_output=True, text=True, timeout=600)
    out, on = {}, False
    for line in r.stdout.splitlines():
        m = re.match(r"^[0-9a-f]+ <(.*)>:$", line)
        if m:
            on = "kernel" in m.group(1)
            continue
        if not on:
            continue
        m = re.match(r"\s+([0-9a-f]+):\s+(.*)", line)
        if m:
            out[int(m.group(1), 16)] = m.group(2).strip()
    return out


_XFER = re.compile(r"^(j\w+|call\w*|loop\w*)\s+([0-9a-f]+)$")


def kernel_fingerprint(exe):
    """`(n_instructions, 12-hex digest)` of the `kernel` function's text,
    normalised so that it is a claim about CODE and not about LAYOUT.

    ⚠⚠ **THIS FUNCTION'S FIRST VERSION WAS LAYOUT-SENSITIVE AND SAID SO
    NOWHERE, AND ITS OWN MUST-FIRE NEGATIVES CAUGHT IT ONE RUN LATER**
    (`.temp/php28/negatives_spellings.py` group G, `TASK_PHP_028`). It stripped
    everything after the first `<`, which removes the crate hash in
    `<_RNvCs...6kernel+0x1a0>` -- but an absolute jump target is printed BEFORE
    that bracket, and objdump's resolved `# 553b0` for a rip-relative operand
    comes after the operand and not after a `<`. So two builds of the SAME
    source under crate names of different lengths came out with different
    digests: `r2x_guard_r3` was reported as NOT byte-identical to
    `r2x_shipped` when in fact **65 of its 483 lines differed and every one of
    them was an address** -- 51 jump targets and 14 resolved rip comments, with
    every displacement identical. The claim it exists to make is exactly the
    one it was getting wrong.

    Four rules, and each removes a layout term while keeping a code term:

      * everything from the first `<` goes -- the crate hash;
      * everything from `#` goes -- objdump's RESOLVED rip-relative address.
        The DISPLACEMENT (`0x3f546(%rip)`) stays, and it is the code;
      * a control-transfer target becomes a SIGNED OFFSET from the
        instruction's own address, so the control-flow shape survives and its
        placement does not;
      * everything else is kept, registers and immediates included, so a
        register-allocation change is still a difference. An opcode-only digest
        would call `r3_head_array` equal to the shipped R3, and it is not.

    That is what makes "byte-identical" a claim and not a hope: `r3_guard_r2`,
    `r3_u16`, `r4_hoistbase` and `r2x_guard_r3` match their rung's digest
    exactly, while `r3_head_array` costs the same to the instruction and does
    NOT match -- which is the pair of behaviours a fingerprint has to have.
    """
    txt = disasm(exe)
    body = []
    for a in sorted(txt):
        t = re.sub(r"\s+", " ", txt[a]).split("<")[0].split("#")[0].strip()
        m = _XFER.match(t)
        body.append(f"{m.group(1)} {int(m.group(2), 16) - a:+d}" if m else t)
    return len(body), hashlib.md5("\n".join(body).encode()).hexdigest()[:12]


def verus_ok(vp):
    r = subprocess.run([sys.executable, VERUS_RUN, vp],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    m = re.search(r"verification results:: (\d+) verified, (\d+) errors", txt)
    if not m:
        return False, txt.strip()[-400:]
    return m.group(2) == "0", m.group(0)


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in ../spec.md's `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics rather than a stricter invention:

      * a `forbidden` hit DISQUALIFIES -- `check.py`'s stage 0 has hard-failed
        on one since TASK_068, and its scope is universal by the key's own
        meaning, so it is decidable with no English involved;
      * a `required` miss is REPORTED and does not -- `check.py` records those
        as `pins_nothing` / `absent` and never fails on them, because which
        rungs a `required` entry scopes to lives in the entry's ENGLISH and no
        gate stage reproduces it.

    ⚠ Getting this backwards is not a conservative error, and on THIS row it is
    worse than on `ph07`: `results-php/gate/ph16-fdset-index.json` records
    **9 scoped-absent (spelling x rung) pairs** on the shipped tree, because
    `required[5]` pins BOTH spellings of guard (b) -- `this_fd < FD_SETSIZE`,
    which is R1's and R2's, and `w < NW`, which is R3's, R4's and R5's -- so
    EVERY rung misses one of them by construction. An audit that treated a
    `required` miss as disqualifying would refuse the shipped rungs themselves.
    ⭐ That same entry is what gives this audit a real discriminating power
    here: `r3_guard_r2` and `r2x_guard_r3` SWAP which of the two they satisfy,
    and stage 0 prints it, so the audit witnesses that the substitution did what
    its `why` claims.
    ⚠ `admissible` is still THREE-VALUED. The token audit decides what a grep
    can decide; the third value is a sentence, and for each variant it is in
    the `why` above."""
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


def pct(a, b):
    return None if not b else 100.0 * (a - b) / b


# ---- the two verdicts, factored so they can be ATTACKED ---------------------
# `PROTOCOL_PHP.md` §H: a validator lands with its must-fire negatives. These
# two functions ARE the file's verdict, so they are functions and not two lines
# inside `main`, and `.temp/php28/negatives_spellings.py` drives them over
# synthetic `rows` dicts -- an out-of-contract cheaper candidate, an unpriced
# one, a sub-`TIE_PCT` margin -- which is not reachable through the CLI.

def cheapest_in_contract(rows, side="R3", key="ir_per_window_byte"):
    """The cheapest IN-CONTRACT, PRICED candidate on one side, or `None`.

    ⚠ Three exclusions and each one is a defect this would otherwise publish:
    a variant that is out of contract (the audit or the checksum refused it),
    one that was never priced (`None` compares as smaller than nothing in
    Python 3 -- it raises -- but a missing key would silently pick a stale
    row), and a side that is not a rung side (`R4x`/`R2x` are controls and
    cannot move a published number)."""
    if side not in RUNG_SIDES:
        return None
    c = [r for r in rows.values()
         if r.get("side") == side and r.get("in_contract")
         and r.get(key) is not None]
    return min(c, key=lambda r: r[key]) if c else None


def cheaper_than_shipped(rows, side="R4", key="ir_per_window_byte",
                         tie_pct=TIE_PCT):
    """Every IN-CONTRACT candidate on one side that beats its shipped rung by
    MORE than `tie_pct`, cheapest first. Empty means that endpoint is
    DEGENERATE."""
    if side not in RUNG_SIDES:
        return []
    base = rows.get((side, "v0_shipped"), {}).get(key)
    if not base:
        return []
    out = [r for r in rows.values()
           if r.get("side") == side and r.get("name") != "v0_shipped"
           and r.get("in_contract") and r.get(key) is not None
           and (base - r[key]) / base * 100.0 > tie_pct]
    return sorted(out, key=lambda r: r[key])


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit; no build, no callgrind")
    ap.add_argument("--verus", action="store_true",
                    help="also put every R4 variant through Verus")
    ap.add_argument("--attribute", action="store_true",
                    help="stage 6: decompose R4ship - R3ship per machine "
                         "instruction. This is what chose the candidate set.")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    chk = load_check()
    decl = contract()["idiom"]
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("spellings.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    variants = R3_VARIANTS + R4_VARIANTS + R4X_VARIANTS + R2X_VARIANTS
    rows = {}
    print("0. THE SPELLING AUDIT -- every backticked idiom entry, "
          "harness/check.py::spelling_matches")
    for name, side, why, subs in variants:
        rs, vp = materialise(name, side, subs)
        src = open(rs, encoding="utf-8").read()
        forb, miss = audit(chk, decl, src)
        rows[(side, name)] = {"side": side, "name": name, "why": why,
                              "rs": rs, "verus_rs": vp,
                              "rung_candidate": side in RUNG_SIDES,
                              "forbidden_hits": forb, "required_absent": miss,
                              "in_contract": not forb}
        print(f"  {side:3s} {name:16s} "
              + ("IN CONTRACT" if not forb else "OUT: " + "; ".join(forb))
              + f"   required absent: "
              + (", ".join(m.split("`")[1] for m in miss) or "none"))
        if forb and name != "v0_shipped":
            print(f"      -> not quoted as a rung candidate")
    if args.audit_only:
        return 0

    print("\n1. BUILD + CHECKSUM -- a respelling that changes the answer "
          "is not one.\n   ⚠ EVERY variant is compared against R3 v0_shipped: "
          "the row pins all four Rust\n   rungs to one checksum per input and "
          "the gate asserts it, so this is stronger\n   than comparing each "
          "side with itself.")
    ref = None
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"], os.path.join(SCRATCH, f"{side}_{name}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side:3s} {name:16s} BUILD FAILED")
            problems.append(f"{side} {name} does not build: {err}")
            continue
        r["exe"] = exe
        r["kernel_insns"], r["kernel_fingerprint"] = kernel_fingerprint(exe)
        answers = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = answers
        if (side, name) == ("R3", "v0_shipped"):
            ref = answers
            print(f"  {side:3s} {name:16s} REFERENCE  "
                  + " ".join(f"{k.split('.')[0][:14]}={v[:8]}"
                             for k, v in list(answers.items())[:3]) + " ...")
            continue
        diff = [k for k, v in answers.items() if ref.get(k) != v]
        print(f"  {side:3s} {name:16s} "
              + ("ok  identical on all "
                 f"{len(answers)} inputs" if not diff
                 else f"*** DIFFERS on {diff}")
              + f"   kernel {r['kernel_insns']:3d} insn "
                f"{r['kernel_fingerprint']}")
        if diff:
            problems.append(f"{side} {name} changes the answer on {diff} "
                            f"-- it is not a respelling of this kernel")
            r["in_contract"] = False
    for side in ("R4", "R2x"):
        k = (side, "v0_shipped" if side == "R4" else "r2x_shipped")
        a = rows.get(k, {}).get("answers")
        if a is not None and ref is not None and a != ref:
            problems.append(
                f"{k[0]} {k[1]} does not agree with R3 v0_shipped on every "
                f"input, so this row's one-checksum-per-input invariant does "
                f"not hold in this pipeline and nothing below is comparable")

    print("\n2. THE PRICE -- kernel-exclusive Ir per call on the SHIPPED "
          "inputs, harness/measure.py's own statistic")
    sm_st, lg_st = PROBES[0][1], PROBES[1][1]
    print(f"  {'cell':24s} {'Ir/call small':>14s} {'Ir/call large':>14s} "
          f"{'Ir/win-byte':>12s} {'fixed/call':>11s} "
          f"{'%small':>8s} {'%large':>8s} {'%slope':>8s}")
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if not r.get("exe"):
            continue
        per = {}
        for inp, stride, nit in PROBES:
            tot, err = kernel_ir(r["exe"], os.path.join(PDIR, "inputs", inp),
                                 f"{side}.{name}.{inp}")
            if err:
                problems.append(f"{side} {name} {inp}: {err}")
            per[inp] = None if tot is None else tot / float(nit)
            r[f"ir_total_{inp.split('.')[0]}"] = tot
        r["ir_small"] = per[PROBES[0][0]]
        r["ir_large"] = per[PROBES[1][0]]
        if r["ir_small"] is None or r["ir_large"] is None:
            problems.append(f"{side} {name}: callgrind gave no kernel figure")
            continue
        slope = (r["ir_large"] - r["ir_small"]) / float(lg_st - sm_st)
        r["ir_per_window_byte"] = slope
        r["fixed_per_call"] = r["ir_small"] - slope * sm_st
    b4 = rows[("R4", "v0_shipped")]
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if r.get("ir_per_window_byte") is None:
            continue
        r["pct_vs_r4ship_small"] = pct(r["ir_small"], b4.get("ir_small"))
        r["pct_vs_r4ship_large"] = pct(r["ir_large"], b4.get("ir_large"))
        r["pct_vs_r4ship"] = pct(r["ir_per_window_byte"],
                                 b4.get("ir_per_window_byte"))
        print(f"  {side + ' ' + name:24s} {r['ir_small']:14.1f} "
              f"{r['ir_large']:14.1f} {r['ir_per_window_byte']:12.4f} "
              f"{r['fixed_per_call']:11.1f} "
              + " ".join(f"{r[k]:+7.2f}%" if r.get(k) is not None
                         else f"{'--':>8s}"
                         for k in ("pct_vs_r4ship_small",
                                   "pct_vs_r4ship_large", "pct_vs_r4ship")))

    print("\n3. DOES THIS PIPELINE REPRODUCE THE SHIPPED CELLS?")
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
        for cell, key in (("safe_tuned", ("R3", "v0_shipped")),
                          ("unsafe", ("R4", "v0_shipped")),
                          ("safe_naive", ("R2x", "r2x_shipped"))):
            for inp, k in (("small.bin", "ir_small"), ("large.bin", "ir_large")):
                w = want.get((cell, inp))
                g = rows[key].get(k)
                if w is None or g is None:
                    print(f"  {cell:12s} {inp:10s} record={w} here={g}  "
                          f"(not comparable)")
                    continue
                d = abs(w - g) / w * 100.0
                print(f"  {cell:12s} {inp:10s} record={w:10.4f} "
                      f"here={g:10.4f}  delta={d:.3f}%")
                if d > 0.5:
                    rec_ok = False
                    problems.append(
                        f"{cell}/{inp}: this pipeline measures {g:.4f} where "
                        f"the shipped record says {w:.4f} ({d:.2f}% apart) -- "
                        f"the variants below are then about a different "
                        f"benchmark from the row")
    else:
        print(f"  no measurement record at {RECORD}")

    if args.verus:
        print("\n4. R4 ADMISSIBILITY -- ../spec.md pins `identity: unsafe == "
              "verus`, so every R4 candidate needs a twin that VERIFIES")
        for name, side, why, subs in R4_VARIANTS:
            r = rows[(side, name)]
            if not r.get("verus_rs"):
                continue
            ok, msg = verus_ok(r["verus_rs"])
            r["verus_verifies"], r["verus_msg"] = ok, msg
            if not ok:
                r["in_contract"] = False
            print(f"  R4 {name:16s} {'VERIFIES' if ok else 'DOES NOT VERIFY'}"
                  f"   {msg.splitlines()[0][:90] if msg else ''}")
            if not ok and name == "v0_shipped":
                problems.append("R4 v0_shipped's twin does not verify -- this "
                                "pipeline is not measuring the shipped rung")
        print("  R4x/R2x            NO TWIN ATTEMPTED -- exec-only controls. "
              "Both R4x entries are\n                     DEARER than R4ship, "
              "and a dearer candidate cannot move a bound\n                   "
              "  whose denominator is R4ship whether or not it verifies.")
    else:
        print("\n4. R4 ADMISSIBILITY -- skipped (pass --verus). ⚠ Until it is "
              "run, no R4 variant below is a RUNG; each is a control.")
        # ⚠⚠⚠ AND THE SIDECAR MUST SAY SO, BECAUSE A RUN WITHOUT `--verus`
        # WRITES A FILE THAT LOOKS COMPLETE AND IS NOT (`TASK_PHP_022` §3.2
        # gap 5, DEMONSTRATED LIVE AT `TASK_PHP_024` §1.6 on `ph07`, where
        # regenerating without the flag flipped an R4 variant's `in_contract`
        # from false to TRUE and still wrote `"problems": []`).
        # PROBE RULE 1: a probe that CANNOT EVALUATE must say so and exit
        # non-zero.
        problems.append(
            "R4 ADMISSIBILITY WAS NOT CHECKED (no --verus), so every R4 "
            "variant's `in_contract` below is unverified: `spec.md` pins "
            "`identity: unsafe == verus`, and without a verifying twin an R4 "
            "candidate is a control and not a rung. Regenerate with "
            "`--verus`, which is what `pin.regenerate` names.")

    # ---- the two published numbers -----------------------------------------
    print("\n5. THE TWO NUMBERS THAT MAY BE QUOTED, LABELLED")
    r3s = rows[("R3", "v0_shipped")]
    r4s = rows[("R4", "v0_shipped")]
    keys = (("small.bin per call", "pct_vs_r4ship_small"),
            ("large.bin per call", "pct_vs_r4ship_large"),
            ("Ir per window byte", "pct_vs_r4ship"))
    best = cheapest_in_contract(rows, "R3")
    print("  fixed-R4 bound              R3ship - R4ship            "
          "⚠ NEGATIVE on this row, so not an upper bound on the cost of safety")
    for label, k in keys:
        print(f"      {label:22s} {r3s.get(k, float('nan')):+8.2f}%")
    if best is not None:
        print(f"  cheapest-found in-contract  inf(R3 found) - R4ship     "
              f"spelling `{best['name']}`, inputs small.bin + large.bin")
        for label, k in keys:
            print(f"      {label:22s} {best.get(k, float('nan')):+8.2f}%")
    r4c = [r for r in rows.values()
           if r.get("side") == "R4" and r.get("in_contract")
           and r.get("ir_per_window_byte") is not None]
    b4r = r4s.get("ir_per_window_byte")
    beat = cheaper_than_shipped(rows, "R4")
    print(f"  ⚠ R4 SIDE, SEARCHED ({len(r4c)} admissible rung candidate(s) of "
          f"{len(R4_VARIANTS)} tried, plus {len(R4X_VARIANTS)} exec-only "
          f"control(s)):")
    for r in sorted([r for r in rows.values()
                     if r.get("side") in ("R4", "R4x")
                     and r.get("ir_per_window_byte") is not None],
                    key=lambda r: r["ir_per_window_byte"]):
        d = (r["ir_per_window_byte"] - b4r) / b4r * 100.0 if b4r else 0.0
        verdict = ("SHIPPED" if r["name"] == "v0_shipped"
                   else ("TIE (< %.2f%%)" % TIE_PCT if abs(d) <= TIE_PCT
                         else ("CHEAPER" if d < 0 else "dearer")))
        if not r.get("in_contract"):
            verdict = "INADMISSIBLE (" + (
                "no verifying twin" if r.get("verus_verifies") is False
                else "see stage 0/1") + ")"
        elif r.get("side") == "R4x":
            verdict += "  [exec-only control]"
        print(f"      {r['name']:16s} {r['ir_per_window_byte']:.4f} "
              f"Ir/window byte  {d:+.3f}%  fixed/call "
              f"{r['fixed_per_call']:6.1f}  kernel {r['kernel_insns']:3d} insn "
              f"{r['kernel_fingerprint']}   {verdict}")
    if not beat:
        # ⚠ DERIVED, NOT NARRATED. This sentence used to hardcode "FOUR
        # respellings ... including `r4x_subslice`", and the end-to-end
        # negatives -- which run a 3-variant subset -- printed it verbatim
        # while trying ONE. A count in prose beside a table it does not read
        # is `.tasks/PROTOCOL.md` rule 13 in a control's own output.
        idx = sorted(r["name"] for r in rows.values()
                     if r.get("side") in ("R4", "R4x")
                     and r.get("name") != "v0_shipped"
                     and r.get("ir_per_window_byte") is not None)
        print(f"  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              f"DEGENERATE on this row, so\n     the spread above is over a "
              f"SEARCHED endpoint and not an unsearched one -- which\n     is "
              f"the whole point of the exercise, and it is a materially "
              f"stronger object than\n     the same number was before it was "
              f"searched. ⚠ {len(idx)} R4 respelling(s) priced here:\n     "
              + ", ".join(f"`{n}`" for n in idx)
              + " -- every one dearer or byte-identical.")
    else:
        cheap = beat[0]
        print(f"  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS (`{cheap['name']}`, "
              f"{pct(cheap['ir_per_window_byte'], b4r):+.2f}% on the slope), so "
              f"the published\n     bound MOVES and the headline was an artefact "
              f"of an unsearched R4 side. ⚠ The row\n     does NOT re-ship: "
              f"`.memory/02-bench-rules.md` chooses the rung by IDIOM, before\n"
              f"     measurement, and it stays.")
    print("  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it).")
    # The mirror control, printed where the conclusion is drawn rather than
    # left in the table -- it is the evidence for the sentence above it.
    mir = rows.get(("R3", "r3_absindex"), {})
    r2s = rows.get(("R2x", "r2x_shipped"), {})
    if mir.get("kernel_fingerprint") and r2s.get("kernel_fingerprint"):
        print(f"  ⭐ THE MIRROR CONTROL: R3 given R4's signature "
              f"(`r3_absindex`) is {mir['pct_vs_r4ship']:+.2f}% against "
              f"R4ship\n     and its kernel is "
              f"{mir['kernel_insns']} insn {mir['kernel_fingerprint']} -- "
              + ("BYTE-IDENTICAL to safe_naive.rs"
                 if mir["kernel_fingerprint"] == r2s["kernel_fingerprint"]
                 else f"NOT safe_naive.rs's "
                      f"{r2s['kernel_insns']} insn "
                      f"{r2s['kernel_fingerprint']}")
              + f".\n     So the subslice signature is worth "
                f"{pct(r3s['ir_per_window_byte'], mir['ir_per_window_byte']):+.1f}% "
                f"in the SAFE rung and "
              + (f"{pct(rows[('R4x', 'r4x_subslice')]['ir_per_window_byte'], b4r):+.1f}%"
                 if rows.get(("R4x", "r4x_subslice"), {}).get(
                     "ir_per_window_byte") else "?")
              + " in the\n     UNSAFE one: the two rungs' cheapest spellings "
                "are DIFFERENT spellings, and R3's\n     minimum sits below "
                "R4's. ⚠ n = 1 row; nothing here generalises past ph16.")
    g3 = rows.get(("R3", "r3_guard_r2"), {})
    g2 = rows.get(("R2x", "r2x_guard_r3"), {})
    if g3.get("kernel_fingerprint") and g2.get("kernel_fingerprint"):
        print(f"  ⚠⚠ ../NOTES.md §8b, TESTED IN BOTH DIRECTIONS: the guard "
              f"respelling is\n     "
              + ("BYTE-IDENTICAL"
                 if g3["kernel_fingerprint"] == r3s["kernel_fingerprint"]
                 else "NOT identical")
              + " applied to R3 and "
              + ("BYTE-IDENTICAL"
                 if g2["kernel_fingerprint"] == r2s["kernel_fingerprint"]
                 else "NOT identical")
              + " applied to R2.\n     §8b attributes the R2->R3 gap to it; "
                "on this evidence the gap is item 2 of\n     safe_tuned.rs's "
                "module comment (the subslice and `chunks_exact`) and item 1 "
                "is\n     worth ZERO instructions.")

    attrib = None
    if args.attribute:
        print("\n6. WHERE THE SPREAD IS -- R4ship - R3ship, decomposed by "
              "EXECUTION-COUNT CLASS\n   (this is what chose the candidate set; "
              "a set too narrow shows up as a residue.\n   The two rungs run "
              "the same control flow on the same data, so a block's\n   "
              "execution count identifies it in both binaries -- exact, not "
              "thresholded.)")
        attrib = {"input": PROBES[0][0], "n_iters": PROBES[0][2], "classes": []}
        got = {}
        for side, name in (("R3", "v0_shipped"), ("R4", "v0_shipped")):
            r = rows[(side, name)]
            tag = f"attr.{side}"
            tot, err = kernel_ir(r["exe"], os.path.join(PDIR, "inputs",
                                                        PROBES[0][0]),
                                 tag, dump_instr=True)
            if err:
                problems.append(f"attribute {side}: {err}")
                continue
            per = per_instruction(os.path.join(SCRATCH, f"cg.{tag}"))
            s = sum(per.values())
            print(f"  {side} annotate={tot}  per-instruction sum={s}  "
                  + ("AGREE" if s == tot else "*** DISAGREE"))
            if s != tot:
                problems.append(
                    f"attribute {side}: the per-instruction sum {s} is not the "
                    f"callgrind_annotate figure {tot}; the parser is dropping "
                    f"or double-counting cost lines and no number in stage 6 "
                    f"can be believed")
            got[side] = (per, disasm(r["exe"]), tot)
        if len(got) == 2:
            (p3, d3, t3), (p4, d4, t4) = got["R3"], got["R4"]
            c3 = collections.Counter(p3.values())
            c4 = collections.Counter(p4.values())
            nit = float(PROBES[0][2])
            print(f"  net R4 - R3 = {t4 - t3:+d} Ir over {int(nit)} calls "
                  f"= {(t4 - t3) / nit:+.1f} Ir/call")
            print(f"  {'exec count':>12s} {'per call':>9s} {'R3 insn':>8s} "
                  f"{'R4 insn':>8s} {'delta Ir':>12s} {'/call':>8s}")
            acc = 0
            for n in sorted(set(c3) | set(c4), key=lambda n: -abs(
                    n * (c4[n] - c3[n]))):
                d = n * (c4[n] - c3[n])
                acc += d
                if not d:
                    continue
                print(f"  {n:12d} {n / nit:9.1f} {c3[n]:8d} {c4[n]:8d} "
                      f"{d:+12d} {d / nit:+8.1f}")
                attrib["classes"].append(
                    {"exec_count": n, "r3_insns": c3[n], "r4_insns": c4[n],
                     "delta_ir": d})
                if abs(d) == max(abs(n2 * (c4[n2] - c3[n2]))
                                 for n2 in set(c3) | set(c4)):
                    for tag, per, dis in (("R3", p3, d3), ("R4", p4, d4)):
                        got_i = [f"{dis.get(a, '?').split('<')[0].strip()}"
                                 for a, c in sorted(per.items()) if c == n]
                        print(f"      {tag}: " + " | ".join(got_i))
            print(f"  {'NET':>12s} {'':>9s} {sum(c3.values()):8d} "
                  f"{sum(c4.values()):8d} {acc:+12d} {acc / nit:+8.1f}   "
                  + ("CLOSES" if acc == t4 - t3 else "*** RESIDUE"))
            attrib["net"] = t4 - t3
            attrib["closes"] = acc == t4 - t3
            if acc != t4 - t3:
                problems.append(
                    "attribute: the execution-count classes do not sum to the "
                    "measured net difference, so the decomposition does not "
                    "close and the candidate set has an unexplained residue")
            for tag in ("attr.R3", "attr.R4"):
                f = os.path.join(SCRATCH, f"cg.{tag}")
                if os.path.exists(f):
                    os.unlink(f)

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph16-fdset-index/controls/spellings.py "
                "--verus --attribute",
            "note":
                "The pin covers the three rung sources the variants are derived "
                "from (safe_naive.rs is one, for the NOTES.md 8b controls), "
                "verus.rs (the R4 admissibility half), spec.md (the "
                "declaration the audit runs against), inputs/gen.py (the corpus "
                "every number is measured over) and this script. It does NOT "
                "cover results-php/ph16-fdset-index.json: stage 3 compares "
                "against that record at run time and prints the delta, which is "
                "a stronger check than a hash of it. WARNING: spec.md is "
                "pinned as a FILE, so an edit anywhere in it -- including one "
                "that touches nothing this file reads -- stales this sidecar. "
                "TASK_PHP_024 4.2 measured that ph07's was the only sidecar in "
                "the tree that pinned spec.md at all; it is pinned here "
                "deliberately, so the two php sidecars are comparable, and "
                "TASK_PHP_028's report argues the pin should become the "
                "CONTRACT BLOCK rather than the file."},
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # ⚠⚠ REPO-RELATIVE KEYS, AND THE GATE MEASURES THAT.
        # `check.py` stage 9b re-hashes these paths against the REPO root and
        # refuses the run with `pins N of N source(s) that are ABSENT ... its
        # numbers are UNDATED` if it cannot find them. ph07's first draft wrote
        # ROW-relative keys and the gate caught it: the pin existed, named the
        # right files, and checked nothing.
        # ⚠ On a php row the REPO the gate runs against is the shim root, where
        # `patterns` is a symlink to `patterns-php`, so `patterns/<row>/...` is
        # the spelling that resolves in BOTH trees.
        "derived_from_sha256": {
            f"patterns/{ROW}/{rel}":
                hashlib.sha256(open(os.path.join(PDIR, rel), "rb").read()
                               ).hexdigest()
            for rel in ("safe_naive.rs", "safe_tuned.rs", "unsafe.rs",
                        "verus.rs", "spec.md", "inputs/gen.py",
                        "controls/spellings.py")},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        # ⚠ RECORDED SINCE `TASK_PHP_024`: without it, a sidecar regenerated
        # without `--verus` is indistinguishable from one regenerated with it,
        # except that its R4 `in_contract` flags mean nothing. See stage 4.
        "verus_checked": bool(args.verus),
        "attributed": bool(args.attribute),
        "attribution": attrib,
        "statistic": "kernel_exclusive_ir / n_iters on the SHIPPED inputs -- "
                     "harness/measure.py::_sum_rows itself, IMPORTED and not "
                     "transcribed, so stage 3 above compares against "
                     "results-php/ph16-fdset-index.json directly. THREE "
                     "percentages are published per cell because the row has "
                     "three statistics in circulation and they do not agree to "
                     "the digit: small.bin per call (the published table's own "
                     "ratio, -1.22% for R3ship-R4ship), large.bin per call "
                     "(-1.84%) and Ir per window byte (the marginal, -1.94%, "
                     "and the one .memory-php/02-ladder.md quotes for ph07). "
                     "All three are negative and no conclusion here turns on "
                     "which is chosen. A FOURTH kind of answer is recorded "
                     "beside them, `kernel_fingerprint`, because three of "
                     "these results are byte-identity results and a percentage "
                     "cannot say that.",
        "reproduces_shipped_record": rec_ok,
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "Every variant is in contract by harness/check.py::spelling_matches "
            "over EVERY backticked idiom entry, returns R3 v0_shipped's "
            "checksum on all six inputs, and is priced by the harness's own "
            "per-call Ir method on both probe inputs. TWO numbers ship, "
            "labelled: the fixed-R4 bound and the cheapest-found in-contract "
            "counterpart. NO PAIR INTERVAL. The R4 side is searched too and "
            "what it finds is reported whether or not it is degenerate; on this "
            "row it is degenerate, which is what makes the negative spread a "
            "result rather than a spelling artefact.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
