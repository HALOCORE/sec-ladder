#!/usr/bin/env python3
"""ph53 control -- **THE IN-CONTRACT SPELLING SPAN. BOTH ENDPOINTS MOVE, THE
`fixed-R4 bound`'s SIGN REVERSES, AND THE CHEAPEST R4 IS ALSO THE ONE WITH THE
SMALLEST TRUSTED SURFACE.**

    python3 patterns-php/ph53-iface-tail-uninit/controls/spellings.py --audit-only
    python3 patterns-php/ph53-iface-tail-uninit/controls/spellings.py --verus

⚠⚠⚠ **RUN IT WITH `--verus` OR ITS R4 COLUMN MEANS NOTHING.** An R4 respelling is
a RUNG CANDIDATE only if it has a Verus twin that VERIFIES. Without the flag this
file refuses to certify and says so in `problems` (`TASK_PHP_024` §1.6
demonstrated live on `ph07` what a sidecar that looks complete and is not does to
a later reader).

⚠⚠ **THE BAR ON THIS ROW IS *THE TWIN VERIFIES* AND NOT BYTE-IDENTITY.**
`../spec.md` pins `identity: unsafe vs verus = differ` at BOTH levels and
`results-php/gate/ph53-iface-tail-uninit.json` MEASURES `differ` at both
(764/758 against 746/741). `identity_premise()` reads the pin **and** the record
and `admissibility()` is a function of what it finds, so if this row were ever
re-pinned to `exact` the rule tightens with it instead of silently staying loose.
It reads the record as well as the prose because F82's negative N6 found a PAT row
(`p25`) carrying `identity: unsafe == verus, O3 exact` as shared-block
BOILERPLATE while its real pin is `norel`.

WHAT THIS ROW'S SEARCH FOUND
----------------------------
`ph07` and `ph16` searched their R4 side and found it DEGENERATE. `ph29`'s moved
(F77). `ph45`'s R4 **and** R3 both moved (F87). ⭐ **On `ph53` both move as well,
and by the largest margins in either programme:**

  * **R3** the cheapest in-contract spelling found is **`r3_chunks_mask` at
    −32.08 % A1** against the shipped R3, and three more are within 3 points of
    it (`r3_both` −30.61 %, `r3_chunks_exact` −30.14 %, `r3_oprec_slice`
    −28.99 %). ⭐⭐ **The shipped R3 was DEAREST-BUT-ONE of the six rungs against
    `TASK_PHP_040_REPORT` §5.6's prediction that it would be the cheapest; under
    search it is CHEAPER THAN THE SHIPPED R4.** So the `fixed-R4 bound` goes
    from **+24.238 %** to an ORDERING with the opposite sign.
    ⚠ All four move the SAME term and it is not the one the prediction was
    about: the shipped rung pays NINE window bounds checks per op record
    (281.8 Ir/call, 20.3 % of the rung) and each of these collapses them to one.
    `../NOTES.md` §8g.
  * **R4** `r4_bitmask` is **−11.40 % A1** -- and it is `../NOTES.md` §8e's OWN
    NAMED CANDIDATE (*"a bitmask witness (`n_decl <= 16` fits one `u32`) is the
    obvious candidate for a cheaper spelling and is not built"*), so the row
    predicted its own cheaper R4 and did not price it.
  * ⭐⭐⭐ **AND `r4_bitmask_min` IS CHEAPER *AND* HAS A SMALLER TRUSTED SURFACE
    AT THE SAME TIME**: **−3.12 %** with **ONE** trusted accessor against the
    shipped rung's **four** (`#[verifier::external_body]` items 3 against 6),
    twin at **32 verified / 0 errors**, no `assume`, no `is not supported`.
    `ph45`'s two trusted-surface reductions both came out DEARER; this one does
    not.

⚠⚠ **AND THE ROW'S LARGEST SINGLE NUMBER MOVES WITH IT.** `../NOTES.md` §8e
publishes the witness -- the one-byte-per-slot `wrote[]` that makes R4 provable at
all -- at **+21.775 %** whole-program against `controls/r4_nowitness.rs`. This
file reproduces that figure to the digit **and** measures the bitmask witness at
**+9.67 %**. ▶ *"The cheapest witness that makes R4 provable costs 21.8 %"* is
withdrawn; the measured figure is **9.7 %**.
⛔⛔ **AND SO IS §8e's MECHANISM, WHICH AN EARLIER DRAFT OF THIS DOCSTRING
REPEATED.** It said the 21.8 % was *"lost vectorisation, not the byte"*.
**Nothing vectorises inside a scan loop in any rung of this row**: 5 `xmm`
instructions in R3, 23 in R4, 17 in `r4_nowitness`, 21 in `r4_bitmask`, and
**not one of them executes more than ONCE per call** -- they are the `pool`,
`idx` and `wrote` array zero-fills. What the measurement supports instead:
the witness TEST costs **39.42 Ir/call in BOTH spellings** (12 `cmpb` sites
against 2 `bt` sites, summing identically), so of the shipped witness's
+228.87 Ir/call over `r4_nowitness`, **+101.59 is the witness and +127.28 is the
array being in MEMORY**. `../NOTES.md` §8e carries the struck sentence and the
replacement.

⚠ **IT STILL DOES NOT RE-SHIP EITHER RUNG.** `.memory/02-bench-rules.md` holds the
shipped rungs fixed by fiat -- chosen by IDIOM, before measurement -- and that
fiat is what makes `R3ship - R4ship` a BOUND. Two numbers ship, labelled, in each
family:

    fixed-R4 bound   R3ship - R4ship      both endpoints held by fiat
    R3-side span     cheapest-found to dearest-found in contract, named

and **NO PAIR INTERVAL**: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts that
construction in terms and this file does not resurrect it. Where this file states
that the ORDERING reverses it says ordering and never interval.

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of. ⚠ The hit counts
are load bearing and they have already caught three ordering mistakes in this
file's own substitution lists (`../NOTES.md` §13b).

R3 side, from `../safe_tuned.rs` -- all safe, no `unsafe` token:

  `v0_shipped`       the shipped R3, unmodified.
  `r3_oprec_slice`   ⭐⭐ **THE WINNER, AND IT IS THE ANSWER TO WHY THE SHIPPED
                     R3 IS DEAR.** The op record is taken as ONE 9-byte `&[u8]`
                     sub-slice and read through that. The shipped rung reads
                     `win[p]`, `rd32(win, p+1)` and `rd32(win, p+5)` -- NINE
                     separate indexings of a dynamically-sized slice -- and LLVM
                     emits NINE bounds checks per op, as nine
                     `cmp <threshold>,%r13 / je <panic>` pairs, executed 391 385
                     times each on `small.bin` = **281.8 Ir/call, 20.3 % of the
                     rung**. The sub-slice collapses them to ONE.
                     ⚠ The panic condition is UNCHANGED: the shipped reads need
                     `p + 8 < win.len()` and the sub-slice needs
                     `p + 9 <= win.len()`, which is the same predicate.
  `r3_oprec_array`   the same lever with `&[u8; OP_BYTES]` and `try_into`, which
                     is `ph45`'s own `safe_tuned.rs` spelling. ⭐⭐ **IT IS
                     BYTE-IDENTICAL TO `r3_oprec_slice`** -- same instruction
                     count, same `kernel` digest, same Ir in both families -- so
                     `ph45`'s §5.6 result (*the compile-time-constant length buys
                     nothing; the lever is elsewhere*) reproduces on a second row
                     and here it reproduces BYTE-IDENTICALLY rather than within a
                     tie threshold.
  `r3_pool_mask`     the SECOND check: `pool[slots[i] as usize]` indexes a
                     fixed-size array with a value that came out of the blob, so
                     a `cmp $0x7 / ja` survives per slot read. `& (MAXP - 1)` is
                     a no-op on every reachable value (`slots[i] = b % n_pool`
                     with `n_pool <= MAXP`) and deletes it. **−1.34 %.**
  `r3_both`          `r3_oprec_slice` + `r3_pool_mask`. **−30.6 %**, the cheapest
                     in-contract R3 found.
  `r3_slice_param`   `&[u32]` instead of `&Vec<u32>` in both consumers. ⚠ A
                     CALIBRATION NULL, kept on purpose: it is a TIE (+0.03 %),
                     and a search whose every entry moves is a search nobody can
                     calibrate.
  `r3_no_capacity`   `Vec::new()` instead of `Vec::with_capacity(n_decl)`, i.e.
                     php-5.2.0's own grow-as-you-add schedule rather than this
                     rung's single reservation. ⛔ **OUT OF CONTRACT BY ENGLISH**
                     -- `idiom.required[8]` DECLARES the allocation order as O(1)
                     per kernel call and `PROTOCOL_PHP.md` §B1a's precondition
                     for this row's cross-language column rests on it.
                     ⭐ Priced anyway, because `TASK_PHP_041` §8.6 records *"did
                     not measure what the 5.2.0 schedule would cost"* as an open
                     uncertainty: **A1 −1.30 % and W1 +28.6 %.**
                     ⚠⚠ **AND THAT PAIR IS THIS ROW'S OWN DEMONSTRATION THAT A1
                     CANNOT SEE AN ALLOCATOR TERM** (F85's mechanism, on this
                     row, from this row's own variant): the allocator work is in
                     `malloc`, not in `kernel`, so A1 reports the O(n) schedule
                     as slightly CHEAPER while the program pays 28.6 % more.
                     ⚠ It is a LOWER BOUND on 5.2.0's cost, not 5.2.0: `Vec`
                     doubles, so this is O(log n) allocations where
                     `erealloc(..., ++n)` is O(n).

R4 side, from `../unsafe.rs`, and **each one's substitution is applied to
`../verus.rs` as well and the result is put through Verus**:

  `v0_shipped`       the shipped R4. 4 trusted accessors, 6 `external_body`
                     items, twin 27 verified / 0 errors.
  `r4_bitmask`       ⭐⭐ **`../NOTES.md` §8e's NAMED CANDIDATE, BUILT.** The
                     witness becomes a `u32` bitmask -- `wrote |= 1 << idx[d]`,
                     read as `(wrote >> i) & 1 == 1`, which LLVM emits as a
                     single `bt` against a REGISTER where the shipped
                     `[bool; MAXD]` is 16 stack bytes with a `movdqa` zero-fill
                     and a `cmpb` per slot. **−11.40 % A1**, `kernel` 296
                     instructions against 766. Twin **31 verified / 0 errors**
                     and the whole proof cost is TWO `by (bit_vector)` lemmas
                     (`lemma_set_bit`, `lemma_zero_bit`), no new trusted item, no
                     `assume`. ⚠ It does NOT carry `idiom.required[4]`'s
                     backticked `wrote[i]`, which is reported as a `required`
                     miss and -- per `harness/check.py`'s own semantics -- does
                     not disqualify. A reader who thinks the shipped witness
                     spelling is part of the contract should read that miss as
                     the argument against this variant.
  `r4_bitmask_pool`  the bitmask plus a CHECKED pool read, i.e. one fewer trusted
                     accessor. **−8.37 %**, twin 31/0, 5 `external_body`.
                     Cheaper AND smaller-surface.
  `r4_bitmask_min`   ⭐⭐⭐ **THE SHARPEST ENTRY: CHEAPER *AND* ONE TRUSTED
                     ACCESSOR INSTEAD OF FOUR.** −3.12 %, twin **32 verified /
                     0 errors**, 3 `external_body` items against the shipped 6.
                     Only the `MaybeUninit` read stays trusted, because there is
                     no safe exec expression from `MaybeUninit<T>` to `T` -- that
                     is what the type means, and it is `../NOTES.md` §11.5.
  `r4_min_trusted`   the same trusted-surface reduction with the SHIPPED witness,
                     so the two effects are separable: **+6.60 %**, twin 28/0,
                     3 `external_body`. ▶ **On the shipped witness a smaller
                     trusted surface COSTS 6.6 %; on the bitmask witness it is
                     free enough to stay under the shipped rung.**
  `r4_pool_checked`  `pool_get_unchecked` -> `pool[p]`. **+3.03 %**, one fewer
                     accessor. `ph45`'s result (a trusted-surface reduction that
                     comes out DEARER) on a second row.
  `r4_set_checked`   `slot_set_unchecked` -> `slots[i] = x`, which is exactly
                     what this row's own `slb_twin_slot_set_unchecked` does, so
                     vstd's `vec_index_mut` value-level `ensures` carries it
                     (`TASK_PHP_041` §3.4). **+0.50 %**, one fewer accessor --
                     the cheapest single reduction on the row.
  `r4_win_oprec`     `win_get_unchecked` -> the R3 winner's 9-byte sub-slice.
                     **+2.99 %**, one fewer accessor.
  `r4_win_checked`   ⚠ **THE MIRROR, AND IT IS THE CALIBRATION LOSER THAT MAKES
                     THE R3 RESULT LEGIBLE**: the same reduction WITHOUT the
                     sub-slice, i.e. the nine window bounds checks restored into
                     R4. **+33.9 %.** ▶ The window-check spelling is worth
                     ~30 % in BOTH rungs and in both directions, which is what
                     makes it the row's dominant term rather than an R3 quirk.
  `r4_mu_ref`        ⭐ **OPEN ITEM 79, MEASURED.** `Vec<MaybeUninit<&u64>>`: the
                     slot holds a REFERENCE INTO THE POOL, as the C's slot holds
                     a `ph53_iface *`. **+1.79 % A1**, and it returns the shipped
                     checksum on all seven inputs -- so `TASK_PHP_041` §8.12's
                     *"the reference representation can express the faulting
                     consumer and NOT the comparing one"* is **FALSE ON THE EXEC
                     SIDE**: `core::ptr::eq` expresses it and gives the same
                     answer, because distinct pool elements have distinct
                     addresses. ⛔ **OUT OF CONTRACT BY ENGLISH, twice over**,
                     and the Verus half is in `mu_ref.rs` / `mu_ref_cmp.rs`,
                     which stage 4 RUNS.

  `ctl_nowitness`    `../controls/r4_nowitness.rs`, the witness-free program, so
                     the witness can be re-priced in this pipeline rather than
                     across two. ⚠ **SIDE `CTL`, so `cheapest_in_contract` and
                     `cheaper_than_shipped` refuse it by construction** -- it is
                     not a rung and cannot become one: it answers differently on
                     an uncovered blob, which is what the witness is for.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**.
    ⚠ A `forbidden` hit DISQUALIFIES; a `required` miss is REPORTED and does not.
    That is `check.py`'s own semantics and not a stricter invention: this row's
    `required` C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN and the
    shipped gate record carries 10 such absences and calls the row
    `PASS-WITH-BLOCKED-ROWS`. (It was 8 until `TASK_PHP_044` added `[bool; MAXD]`
    to `required[4]`, which is absent from the two safe rungs and present in the
    two unsafe ones -- i.e. the entry's declared scope, reported as absence.)
    ⚠ `admissible` is THREE-VALUED. The token audit decides what a grep can
    decide; the third value is a sentence, and `english_verdict` is where a
    variant carries one. **Two variants use it and both are declared.**
  * ⚠⚠ **THE REFERENCE CHECKSUM IS PER SIDE, AND ON THIS ROW THAT IS NOT A
    STYLISTIC CHOICE.** `ph45`'s copy compares every variant against R3
    `v0_shipped` because that row pins all four Rust rungs to one checksum per
    input. **`ph53` does not**: on `inputs/adversarial-cmp.bin` the shipped R3
    prints `2278006814366746624` and the shipped R4 prints
    `17836723469995822080`, because R3 is php-5.2.0's push-as-you-go and its
    array is only as long as the fills it saw, so it examines ONE slot where the
    other five examine two. That divergence is DECLARED (`../safe_tuned.rs`'s
    header, `check.py` stage 4) and the record's `expected` is R4's. A
    cross-side reference here would fail every R3 variant on one input and the
    failure would be the CONTROL's, not the variant's.
  * ⚠⚠ **BOTH FAMILIES, from ONE callgrind run per (variant, input).**
    **A1** is `kernel_exclusive_ir` off the pinned callgrind with
    `measure.py::_sum_rows` **IMPORTED and never transcribed** (`TASK_PHP_022`
    §3.2 measured that the transcription was a different function and produced a
    PLAUSIBLE WRONG NUMBER rather than an error). **W1** is
    `callgrind_annotate`'s own `PROGRAM TOTALS` line.
    ⚠ **A1 IS THE HEADLINE HERE, WHICH IS THE OPPOSITE OF `ph45`.** On `ph45`
    A1's spread over nine variants was `0.000000` pp because `dec` is a separate
    symbol carrying ~90 % of the work. On `ph53` everything is `#[inline(always)]`
    into `kernel` and A1 carries **89.5 %** of the whole program, so A1 resolves
    the search -- `a1_spread_pp` below is ~55 pp on the R3 side. The row
    publishes A1 (`../NOTES.md` §8) and F91 is why. **Both families are printed
    for every comparison anyway**, and `r3_no_capacity` is the variant that shows
    why: it is the one cell where they disagree in SIGN.
  * stage 3 reproduces the SHIPPED cells in BOTH families before any variant is
    quoted: A1 against `results-php/ph53-iface-tail-uninit.json` (four cells) and
    W1 against `../NOTES.md` §8e's committed whole-program total.
  * ⚠⚠ stage 4 puts every R4 twin through Verus and reads the ERROR TEXT.
    `is not supported` and `does not yet support` DISQUALIFY, because they are
    what forces a new TRUSTED item; `postcondition not satisfied` and
    `invariant not satisfied` disqualify NOTHING and are proof work. Byte-identity
    of the twin's `kernel` is RECORDED and, on this row, is not a bar --
    `identity_premise()` is what decides that, from the pin and the record.
    ⚠ **An R4 variant with NO twin file is NEVER admissible**, and that is a
    rule and not an accident of the loop: see `r4_no_twin_reason`.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**

⚠⚠⚠ THE HONEST CAVEAT
----------------------
**Every figure here is about `rustc 1.97.1` / `LLVM 22.1.6` and Verus
`0.2026.08.09.92f466f` on this box**, and the two largest levers found are both
LLVM decisions (how many bounds checks survive a sub-slice; whether a witness
lives in a register or on the stack). ▶ The honest claim is *"an admissible
cheaper R4 and an admissible cheaper R3 exist"*, never *"these are the
cheapest"* -- **searched is not exhausted**, and the report lists what was priced
and dropped.

⚠ `kernel_fingerprint` HERE IS `ph45`'s GUARDED COPY (itself `ph29`'s), carrying
F79's two fixes and `TASK_PHP_037` §6.2's third: objdump's return code is
checked, the symbol needle is not a bare substring, and `twin_identical` refuses
a zero-length kernel and the empty-string digest. `ph16`, `ph29` and `ph45` are
NOT edited (open items 57/63). This file's must-fire negatives are
`.temp/php42/negatives_spellings.py` and the case count is in the report.
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
SCRATCH = os.path.join(REPO, ".temp", "php42", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph53-iface-tail-uninit.json")
GATE_RECORD = os.path.join(REPO, "results-php", "gate",
                           "ph53-iface-tail-uninit.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph53-iface-tail-uninit.json`
#: carries and therefore what `../NOTES.md` §8 quotes.
PROBES = (("small.bin", 221, 25_000), ("large.bin", 439, 10_000))
#: Below this, two cells are a TIE and neither is "cheaper".
TIE_PCT = 0.05
#: Only these two sides can move a published rung number; anything else is a
#: control by construction. `ctl_nowitness` is `CTL` for exactly this reason.
RUNG_SIDES = ("R3", "R4")
#: ⚠ The ONE whole-program total this row commits to prose: `../NOTES.md` §8e's
#: *"R4 as shipped 31 997 489"*, `O3`/`isolated`/`small.bin`, which stage 3
#: reproduces. It is NOT in any `results-php/` record -- `measure.py`'s
#: `protocol.ir` says in terms *"whole-program summary deliberately not
#: recorded"* -- so this is the one figure here pinned to a committed document
#: rather than to a committed JSON. `../NOTES.md` is in this row's GATE digest,
#: so a change to it cannot go unnoticed.
#: ⚠⚠ A ±0.5 % tolerance, not equality. And `../NOTES.md` publishes TWO
#: whole-program totals for this same cell -- §8e's 31 997 489 and §8f's
#: 31 997 125, 364 Ir apart (0.0011 %), with kernel counts 760 and 762 -- because
#: they come from two different `controls/negatives.py` runs. Neither is wrong;
#: they are not the same build. The §8e figure is used because §8e is the
#: section this file corrects.
SHIPPED_WP = {("unsafe", "small.bin"): 31_997_489}
#: The four named unchecked accessors of `../unsafe.rs`. `trusted_accessors`
#: counts CALL SITES of these, definitions subtracted.
ACCESSORS = ("win_get_unchecked", "slot_read_unchecked", "slot_set_unchecked",
             "pool_get_unchecked", "mu_read")


# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]}, english_verdict)
# `file` is "rs" for the rung source and "verus" for the R5 twin.
#
# ⚠⚠ ORDER INSIDE A LIST IS LOAD BEARING AND THE HIT COUNTS ARE WHAT SAID SO.
# `_V_DECL` and `_V_FILL` both CONTAIN `#[trigger] wrote@[j]` and
# `abst(slots@, wrote@,`, so if the two whole-block substitutions ran after the
# global renames their anchors would no longer exist and the counts would come
# out 6/10 instead of 5/8. `apply_subs` raises rather than guessing.

# ======== R3, from ../safe_tuned.rs ==========================================
_S_READ = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win[p] as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
"""
_S_READ_SLICE = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let rec: &[u8] = &win[p..p + OP_BYTES];
        let op: u32 = (rec[0] as u32) % 3;
        let a: u32 = rd32(rec, 1);
        let b: u32 = rd32(rec, 5);
"""
_S_READ_ARRAY = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let rec: &[u8; OP_BYTES] = (&win[p..p + OP_BYTES]).try_into().unwrap();
        let op: u32 = (rec[0] as u32) % 3;
        let a: u32 = rd32(rec, 1);
        let b: u32 = rd32(rec, 5);
"""
_S_POOL = "        let id: u64 = pool[slots[i] as usize];\n"
_S_POOL_MASK = "        let id: u64 = pool[(slots[i] as usize) & (MAXP - 1)];\n"
_S_SIG_D = ("fn instanceof_ex(slots: &Vec<u32>, pool: &[u64; MAXP], "
            "target_id: u64)")
_S_SIG_D_SLICE = ("fn instanceof_ex(slots: &[u32], pool: &[u64; MAXP], "
                  "target_id: u64)")
_S_SIG_C = "fn inherit_scan(slots: &Vec<u32>, target: u32) -> usize {"
_S_SIG_C_SLICE = "fn inherit_scan(slots: &[u32], target: u32) -> usize {"
#: ⚠⚠ A THIRD SPELLING OF THE SAME LEVER, and unlike the first two it is NOT a
#: tie: `chunks_exact` deletes the per-op offset arithmetic as well as eight of
#: the nine bounds checks, and it is 1.63 % cheaper than the sub-slice spelling.
#: ⚠ It also removes a panic path the shipped spelling HAS -- `take(n_ops)`
#: cannot run off the end where `win[p]` would panic -- which is unreachable on
#: every input (`n_ops = rd32(win, 8) % (cap + 1)` and `chunks_exact` yields
#: exactly `cap` chunks), and is the same class of change as `r3_pool_mask`.
#: The seven checksums are unchanged, which is what stage 1 asserts.
_S_LOOP = """    let mut acc: u64 = 0;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win[p] as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
"""
_S_LOOP_CHUNKS = """    let mut acc: u64 = 0;
    let mut o: usize = 0;
    for rec in win[OPS_OFF..].chunks_exact(OP_BYTES).take(n_ops) {
        let op: u32 = (rec[0] as u32) % 3;
        let a: u32 = rd32(rec, 1);
        let b: u32 = rd32(rec, 5);
"""
_S_CAP = "    let mut slots: Vec<u32> = Vec::with_capacity(num_interfaces);\n"
_S_NOCAP = "    let mut slots: Vec<u32> = Vec::new();\n"

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}, None),
    ("r3_oprec_slice", "R3",
     "the op record as ONE 9-byte &[u8] sub-slice: nine per-op window bounds "
     "checks collapse to one",
     {"rs": [(_S_READ, _S_READ_SLICE, 1)]}, None),
    ("r3_oprec_array", "R3",
     "the same lever with &[u8; OP_BYTES] + try_into, ph45's own spelling -- "
     "expected BYTE-IDENTICAL to r3_oprec_slice",
     {"rs": [(_S_READ, _S_READ_ARRAY, 1)]}, None),
    ("r3_pool_mask", "R3",
     "& (MAXP - 1) on the pool index: deletes the per-slot-read cmp/ja that "
     "survives because the index came out of the blob",
     {"rs": [(_S_POOL, _S_POOL_MASK, 1)]}, None),
    ("r3_both", "R3", "r3_oprec_slice + r3_pool_mask",
     {"rs": [(_S_READ, _S_READ_SLICE, 1), (_S_POOL, _S_POOL_MASK, 1)]}, None),
    ("r3_chunks_exact", "R3",
     "the THIRD spelling of the op-record lever -- chunks_exact(9).take(n_ops), "
     "which deletes the offset arithmetic as well as the checks, and is NOT a "
     "tie with the other two",
     {"rs": [(_S_LOOP, _S_LOOP_CHUNKS, 1)]}, None),
    ("r3_chunks_mask", "R3", "r3_chunks_exact + r3_pool_mask -- the cheapest "
     "in-contract R3 found",
     {"rs": [(_S_LOOP, _S_LOOP_CHUNKS, 1), (_S_POOL, _S_POOL_MASK, 1)]}, None),
    ("r3_slice_param", "R3",
     "&[u32] instead of &Vec<u32> in both consumers -- the CALIBRATION NULL",
     {"rs": [(_S_SIG_D, _S_SIG_D_SLICE, 1), (_S_SIG_C, _S_SIG_C_SLICE, 1)]},
     None),
    ("r3_no_capacity", "R3",
     "Vec::new() instead of Vec::with_capacity(n_decl) -- php-5.2.0's own "
     "grow-as-you-add schedule, a LOWER BOUND on it (Vec doubles; erealloc "
     "does not)",
     {"rs": [(_S_CAP, _S_NOCAP, 1)]},
     "OUT OF CONTRACT BY ENGLISH, ON TWO INDEPENDENT ENTRIES. (i) "
     "idiom.required[8] DECLARES the allocation order as O(1) per kernel call "
     "and PROTOCOL_PHP.md B1a's precondition for this row's cross-language "
     "column rests on it. (ii) ⭐ ADDED AT TASK_PHP_044, AND IT IS THE TEST OF "
     "WHETHER ITEM 83's RULING WAS A RULE OR A PATCH: idiom.required[0]'s rust "
     "key backticks `Vec::with_capacity(num_interfaces)` and its English says "
     "\"present in safe_tuned.rs, unsafe.rs and verus.rs\" and then \"The set of "
     "rungs lives in this English\", so the entry is R3-scoped AMONG OTHERS and "
     "safe_tuned.rs IS the R3 rung -- and this variant's whole substitution is "
     "to delete that spelling. required_absent records the miss. ⚠ The entry "
     "also names a rung that does NOT match (safe_naive.rs \"writes a vector of "
     "None instead\"), which cuts both ways, and the reading is that it does NOT "
     "weaken the pin: the two PAT precedents for a non-discriminating required "
     "entry (p19-state-machine/required[2], p46-bignum-mac/required[4]) both "
     "carry the sentence \"that is the declaration working, not failing\", and "
     "this entry says the OPPOSITE -- \"which is the R2/R3 distinction this row "
     "exists to price\". It declares its discriminating power rather than "
     "disclaiming it. ⛔ NOTHING MECHANICAL MOVES ON (ii): this variant already "
     "carried (i), so it was already outside _admissible, and its A1 of 1369.65 "
     "is interior to the R3 span either way -- which is an INDEPENDENT "
     "corroboration that item 83's ruling does not reach the R3 endpoint. "
     "Priced because TASK_PHP_041 section 8.6 left the 5.2.0 schedule's cost as "
     "an open uncertainty, and reported because A1 and W1 disagree in SIGN "
     "on it."),
]

# ======== R4, from ../unsafe.rs (exec) and ../verus.rs (twin) =================
_U_RD32 = """fn rd32(w: &[u8], o: usize) -> u32 {
    (win_get_unchecked(w, o) as u32)
        | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
}
"""
_U_RD32_CHECKED = """fn rd32(w: &[u8], o: usize) -> u32 {
    (w[o] as u32)
        | ((w[o + 1] as u32) << 8)
        | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
}
"""
_U_WIN_DEF = """/// `v[i]` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

"""
_U_POOL_DEF = """/// `a[i]` with no bounds check. Sound iff `i < MAXP`.
#[inline(always)]
fn pool_get_unchecked(a: &[u64; MAXP], i: usize) -> u64 {
    unsafe { *a.get_unchecked(i) }
}

"""
_U_SET_DEF = """/// `v[i] = x` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize,
                      x: MaybeUninit<u32>) {
    unsafe { *v.get_unchecked_mut(i) = x };
}

"""
_U_OP = """        let op: u32 = (win_get_unchecked(win, p) as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
"""
_U_OP_OPREC = """        let rec: &[u8] = &win[p..p + OP_BYTES];
        let op: u32 = (rec[0] as u32) % 3;
        let a: u32 = rd32(rec, 1);
        let b: u32 = rd32(rec, 5);
"""
_U_OP_CHECKED = "        let op: u32 = (win[p] as u32) % 3;\n"
_U_OP_ONLY = "        let op: u32 = (win_get_unchecked(win, p) as u32) % 3;\n"
_U_POOL_D = "            let id: u64 = pool_get_unchecked(pool, p as usize);\n"
_U_POOL_D_NEW = "            let id: u64 = pool[p as usize];\n"
_U_POOL_K = "            let tid: u64 = pool_get_unchecked(&pool, t);\n"
_U_POOL_K_NEW = "            let tid: u64 = pool[t];\n"
_U_SET = ("                slot_set_unchecked(&mut slots, idx[d], "
          "MaybeUninit::new(pi));\n")
_U_SET_NEW = "                slots[idx[d]] = MaybeUninit::new(pi);\n"
_U_READ = """#[inline(always)]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> u32 {
    unsafe { (*v.get_unchecked(i)).assume_init() }
}
"""
_U_READ_SPLIT = """#[inline(always)]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> u32 {
    mu_read(v[i])
}

/// `m.assume_init()`. Sound iff `m` was written. THE ONE OPERATION ON THIS ROW
/// FOR WHICH THERE IS NO SAFE EXEC EXPRESSION AT ALL, which is what
/// `MaybeUninit` means -- so ONE trusted accessor is the FLOOR for a rung that
/// passes `check.py::_scan_unsafe_sites`, and zero is reachable only in a
/// control (`controls/mu_unwrapped.rs`, `../NOTES.md` §11.5).
#[inline(always)]
fn mu_read(m: MaybeUninit<u32>) -> u32 {
    unsafe { m.assume_init() }
}
"""
_U_BM = [
    ("fn instanceof_ex(slots: &Vec<MaybeUninit<u32>>, wrote: &[bool; MAXD],\n"
     "                 pool: &[u64; MAXP], target_id: u64) -> (u64, u64, u64) {",
     "fn instanceof_ex(slots: &Vec<MaybeUninit<u32>>, wrote: u32,\n"
     "                 pool: &[u64; MAXP], target_id: u64) -> (u64, u64, u64) {",
     1),
    ("fn inherit_scan(slots: &Vec<MaybeUninit<u32>>, wrote: &[bool; MAXD],\n"
     "                target: u32) -> usize {",
     "fn inherit_scan(slots: &Vec<MaybeUninit<u32>>, wrote: u32,\n"
     "                target: u32) -> usize {", 1),
    ("        if wrote[i] {\n", "        if (wrote >> i) & 1 == 1 {\n", 2),
    ("    let mut wrote: [bool; MAXD] = [false; MAXD];\n",
     "    let mut wrote: u32 = 0;\n", 1),
    ("                wrote[idx[d]] = true;\n",
     "                wrote = wrote | (1u32 << (idx[d] as u32));\n", 1),
    ("                instanceof_ex(&slots, &wrote, &pool, tid);\n",
     "                instanceof_ex(&slots, wrote, &pool, tid);\n", 1),
    ("            let i: usize = inherit_scan(&slots, &wrote, t);\n",
     "            let i: usize = inherit_scan(&slots, wrote, t);\n", 1),
]
_U_POOL_CHECKED = [(_U_POOL_D, _U_POOL_D_NEW, 1), (_U_POOL_K, _U_POOL_K_NEW, 1),
                   (_U_POOL_DEF, "", 1)]
_U_SET_CHECKED = [(_U_SET, _U_SET_NEW, 1), (_U_SET_DEF, "", 1)]
_U_WIN_OPREC = [(_U_RD32, _U_RD32_CHECKED, 1), (_U_WIN_DEF, "", 1),
                (_U_OP, _U_OP_OPREC, 1)]
_U_WIN_CHECKED = [(_U_RD32, _U_RD32_CHECKED, 1), (_U_WIN_DEF, "", 1),
                  (_U_OP_ONLY, _U_OP_CHECKED, 1)]
_U_MIN = _U_WIN_OPREC + _U_POOL_CHECKED + _U_SET_CHECKED + [
    (_U_READ, _U_READ_SPLIT, 1)]

# ---- and the same, on ../verus.rs -------------------------------------------
_V_BITS_ANCHOR = ("/// The abstraction function from the EXEC slot state to "
                  "the spec's.")
_V_BITS_DEFS = """/// Bit `j` of the `u32` witness word -- `../NOTES.md` §8e's named candidate
/// for a cheaper witness than `[bool; MAXD]`.
///
/// ⚠ EVERY CALLER MUST HAVE `0 <= j < 32`. A shift by the width is not the
/// fact anyone wants, and the two lemmas below carry `j < 32` as a `requires`.
pub open spec fn wbit(w: u32, j: int) -> bool {
    (w >> (j as u32)) & 1u32 == 1u32
}

/// Setting bit `i` sets bit `i` and no other. ⭐ THE WHOLE PROOF COST OF THE
/// BITMASK WITNESS IS THIS LEMMA AND THE NEXT: two `by (bit_vector)` facts, no
/// new trusted item, no `assume`.
pub proof fn lemma_set_bit(w: u32, i: u32, j: u32)
    requires
        i < 32,
        j < 32,
    ensures
        wbit(w | (1u32 << i), j as int) <==> (wbit(w, j as int) || i == j),
{
    assert(((w | (1u32 << i)) >> j) & 1u32 == 1u32 <==> (((w >> j) & 1u32 == 1u32) || i == j))
        by (bit_vector)
        requires
            i < 32,
            j < 32,
    ;
}

/// The empty witness has no bit set -- the `[false; MAXD]` of this
/// representation.
pub proof fn lemma_zero_bit(j: u32)
    requires
        j < 32,
    ensures
        !wbit(0u32, j as int),
{
    assert((0u32 >> j) & 1u32 == 0u32) by (bit_vector) requires j < 32;
}

/// The abstraction function from the EXEC slot state to the spec's."""
_V_ABST = ("pub open spec fn abst(slots: Seq<MaybeUninit<u32>>, wrote: "
           "Seq<bool>, n: int) -> Seq<Option<u32>> {")
_V_ABST_NEW = ("pub open spec fn abst(slots: Seq<MaybeUninit<u32>>, wrote: "
               "u32, n: int) -> Seq<Option<u32>> {")
_V_ABST_BODY = """            if wrote[i] {
                Some(slots[i].mem_contents().value())"""
_V_ABST_BODY_NEW = """            if wbit(wrote, i) {
                Some(slots[i].mem_contents().value())"""
_V_DECL = """    let mut wrote: [bool; MAXD] = [false; MAXD];
    assert(forall|j: int| 0 <= j < MAXD ==> !(#[trigger] wrote@[j]));
    assert(abst(slots@, wrote@, n_decl as int) =~= Seq::new(n_decl as nat, |i: int| None::<u32>));
"""
_V_DECL_NEW = """    let mut wrote: u32 = 0;
    proof {
        assert forall|j: int| 0 <= j < MAXD implies !wbit(wrote, j) by {
            lemma_zero_bit(j as u32);
        }
    }
    assert(abst(slots@, wrote, n_decl as int) =~= Seq::new(n_decl as nat, |i: int| None::<u32>));
"""
_V_FILL = """            if n_decl > 0 {
                slot_set_unchecked(&mut slots, idx[d], MaybeUninit::new(pi));
                wrote[idx[d]] = true;
                assert(idx@[d as int] == d);
                assert(abst(slots@, wrote@, n_decl as int) =~= a0.update(d as int, Some(pi)));
            }
"""
_V_FILL_NEW = """            if n_decl > 0 {
                let ghost w_old = wrote;
                slot_set_unchecked(&mut slots, idx[d], MaybeUninit::new(pi));
                assert(idx@[d as int] == d);
                assert(idx@[d as int] < 32);
                wrote = wrote | (1u32 << (idx[d] as u32));
                proof {
                    assert forall|j: int| 0 <= j < MAXD implies (wbit(wrote, j) <==> (wbit(
                        w_old,
                        j,
                    ) || j == d as int)) by {
                        lemma_set_bit(w_old, d as u32, j as u32);
                    }
                }
                assert(abst(slots@, wrote, n_decl as int) =~= a0.update(d as int, Some(pi)));
            }
"""
_V_BM = [
    (_V_BITS_ANCHOR, _V_BITS_DEFS, 1),
    (_V_ABST, _V_ABST_NEW, 1),
    (_V_ABST_BODY, _V_ABST_BODY_NEW, 1),
    ("wrote: &[bool; MAXD]", "wrote: u32", 2),
    # the two whole blocks, BEFORE the global ghost renames -- see the note at
    # the top of the substitution section
    (_V_DECL, _V_DECL_NEW, 1),
    (_V_FILL, _V_FILL_NEW, 1),
    ("#[trigger] wrote@[j]", "#[trigger] wbit(wrote, j)", 5),
    ("            wrote@.len() == MAXD,\n", "", 3),
    ("abst(slots@, wrote@,", "abst(slots@, wrote,", 8),
    ("        if wrote[i] {\n", "        if (wrote >> (i as u32)) & 1u32 == 1u32 {\n", 2),
    ("instanceof_ex(&slots, &wrote, &pool, tid)",
     "instanceof_ex(&slots, wrote, &pool, tid)", 1),
    ("inherit_scan(&slots, &wrote, t)", "inherit_scan(&slots, wrote, t)", 1),
]
_V_RD32 = """    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16) | ((win_get_unchecked(w, o + 3) as u32)
        << 24)
"""
_V_RD32_NEW = """    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16) | ((w[o + 3] as u32)
        << 24)
"""
_V_WIN_ITEM = """// ------------------------------------------------------- TRUSTED, item 1/6 --
// `v[i]` with no bounds check. The `requires` is what makes it sound and the
// `ensures` is what makes it useful; both are trusted, and `../NOTES.md` §11
// argues each one.
#[verifier::external_body]
fn win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both
// and diffs them, so a trusted item whose contract drifted from what a safe
// implementation can meet is caught.
#[cfg(slb_twin)]
fn slb_twin_win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

"""
_V_POOL_ITEM = """// ------------------------------------------------------- TRUSTED, item 4/6 --
// ⚠ `a: &[u64; MAXP]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its
// length is in its TYPE, so there is nothing about it left for a `requires` to
// say beyond the index: `a@.len() == MAXP` holds for every `a` this signature
// admits, by `vstd::array::array_len_matches_n`.
#[verifier::external_body]
fn pool_get_unchecked(a: &[u64; MAXP], i: usize) -> (r: u64)
    requires
        i < MAXP,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_pool_get_unchecked(a: &[u64; MAXP], i: usize) -> (r: u64)
    requires
        i < MAXP,
    ensures
        r == a@[i as int],
{
    a[i]
}

"""
_V_SET_ITEM = """// ------------------------------------------------------- TRUSTED, item 3/6 --
// ⚠ `x: MaybeUninit<u32>` is a PURE VALUE and needs no precondition: every
// inhabitant is a legal store into a slot of that type, initialised or not.
// The `ensures` names the WHOLE post-state -- `old(v)@.update(i, x)` -- so a
// body that also clobbered `v[i + 1]` could not satisfy it. That completeness
// is the thing a write wrapper's contract can get wrong, and it is why Miri is
// required on this row (../spec.md `miri`).
#[verifier::external_body]
fn slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize, x: MaybeUninit<u32>)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe { *v.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize, x: MaybeUninit<u32>)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

"""
_V_READ = """#[verifier::external_body]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
        v@[i as int].mem_contents().is_init(),
    ensures
        r == v@[i as int].mem_contents().value(),
{
    unsafe { (*v.get_unchecked(i)).assume_init() }
}
"""
_V_READ_NEW = """// ⭐ SPLIT: the INDEX is now safe and only the `MaybeUninit` read is trusted,
// so this item's `requires` loses its `i < v@.len()` conjunct. That conjunct is
// `../unsafe.rs`'s header's *"PRICE OF THE REPRESENTATION"*, and this is what
// paying it back costs.
#[verifier::external_body]
fn mu_read(m: MaybeUninit<u32>) -> (r: u32)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { m.assume_init() }
}

#[inline(always)]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
        v@[i as int].mem_contents().is_init(),
    ensures
        r == v@[i as int].mem_contents().value(),
{
    mu_read(v[i])
}
"""
_V_OP = """        let op: u32 = (win_get_unchecked(win, p) as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
"""
_V_OP_OPREC = """        let rec: &[u8] = &win[p..p + OP_BYTES];
        assert(rec@ =~= win@.subrange(p as int, p + OP_BYTES));
        let op: u32 = (rec[0] as u32) % 3;
        let a: u32 = rd32(rec, 1);
        let b: u32 = rd32(rec, 5);
        assert(rd32s(rec@, 1) == rd32s(win@, p + 1));
        assert(rd32s(rec@, 5) == rd32s(win@, p + 5));
"""
_V_OP_CHECKED = "        let op: u32 = (win[p] as u32) % 3;\n"
_V_POOL_D = "            let id: u64 = pool_get_unchecked(pool, p as usize);\n"
_V_POOL_D_NEW = "            let id: u64 = pool[p as usize];\n"
_V_POOL_K = "            let tid: u64 = pool_get_unchecked(&pool, t);\n"
_V_POOL_K_NEW = "            let tid: u64 = pool[t];\n"
_V_SET = ("                slot_set_unchecked(&mut slots, idx[d], "
          "MaybeUninit::new(pi));\n")
_V_SET_NEW = "                slots[idx[d]] = MaybeUninit::new(pi);\n"
_V_POOL_CHECKED = [(_V_POOL_D, _V_POOL_D_NEW, 1), (_V_POOL_K, _V_POOL_K_NEW, 1),
                   (_V_POOL_ITEM, "", 1)]
_V_SET_CHECKED = [(_V_SET, _V_SET_NEW, 1), (_V_SET_ITEM, "", 1)]
_V_WIN_OPREC = [(_V_RD32, _V_RD32_NEW, 1), (_V_WIN_ITEM, "", 1),
                (_V_OP, _V_OP_OPREC, 1)]
_V_WIN_CHECKED = [(_V_RD32, _V_RD32_NEW, 1), (_V_WIN_ITEM, "", 1),
                  (("        let op: u32 = (win_get_unchecked(win, p) "
                    "as u32) % 3;\n"), _V_OP_CHECKED, 1)]
_V_MIN = _V_WIN_OPREC + _V_POOL_CHECKED + _V_SET_CHECKED + [
    (_V_READ, _V_READ_NEW, 1)]

_MU_REF_ENGLISH = (
    "OUT OF CONTRACT BY ENGLISH, TWICE OVER, AND MEASURED ANYWAY (open item "
    "79). (i) spec.md's u64 is ADDRESS-FREE by construction -- TASK_PHP_041 "
    "section 5.5, which dropped a redundant `||` disjunct from the C for "
    "exactly this reason -- and `core::ptr::eq` makes an ADDRESS a "
    "control-flow decision every rung would have to agree on. (ii) There is no "
    "verus.rs for it: Verus 0.2026.08.09 refuses the `&T` -> `*const T` "
    "coercion outright (`does not yet support ... dereferencing a pointer`), "
    "in BOTH the `core::ptr::eq` and the `as *const` spelling, and even with a "
    "pointer in hand nothing in the pinned vstd relates `&arr[i]`'s address to "
    "`i`, so the compare-only consumer's index-level `ensures` could not close "
    "either. controls/mu_ref.rs and controls/mu_ref_cmp.rs are those two facts "
    "as runnable objects and stage 4 runs both.")

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}, None),
    ("r4_bitmask", "R4",
     "NOTES.md 8e's named candidate: a u32 bitmask witness instead of "
     "[bool; MAXD]. Two by (bit_vector) lemmas, no new trusted item",
     {"rs": _U_BM, "verus": _V_BM}, None),
    ("r4_bitmask_pool", "R4", "the bitmask plus a CHECKED pool read",
     {"rs": _U_BM + _U_POOL_CHECKED, "verus": _V_BM + _V_POOL_CHECKED}, None),
    ("r4_bitmask_min", "R4",
     "the bitmask plus ONE trusted accessor instead of four -- cheaper AND "
     "smaller-surface at the same time",
     {"rs": _U_BM + _U_MIN, "verus": _V_BM + _V_MIN}, None),
    ("r4_min_trusted", "R4",
     "ONE trusted accessor with the SHIPPED witness, so the two effects are "
     "separable",
     {"rs": _U_MIN, "verus": _V_MIN}, None),
    ("r4_pool_checked", "R4", "pool_get_unchecked -> pool[p]",
     {"rs": _U_POOL_CHECKED, "verus": _V_POOL_CHECKED}, None),
    ("r4_set_checked", "R4",
     "slot_set_unchecked -> slots[i] = x, carried by vstd's vec_index_mut",
     {"rs": _U_SET_CHECKED, "verus": _V_SET_CHECKED}, None),
    ("r4_win_oprec", "R4",
     "win_get_unchecked -> the R3 winner's 9-byte sub-slice",
     {"rs": _U_WIN_OPREC, "verus": _V_WIN_OPREC}, None),
    ("r4_win_checked", "R4",
     "THE MIRROR: the same reduction WITHOUT the sub-slice, i.e. the nine "
     "window bounds checks restored into R4 -- the calibration loser that "
     "makes the R3 result legible",
     {"rs": _U_WIN_CHECKED, "verus": _V_WIN_CHECKED}, None),
]

#: ⚠ The variants that are NOT derived by substitution from a shipped rung, so
#: they are declared separately and carry their own source path. `materialise`
#: refuses to invent a substitution for them.
#: (name, side, why, relpath, english_verdict)
FILE_VARIANTS = [
    ("r4_mu_ref", "R4",
     "open item 79: Vec<MaybeUninit<&u64>> -- the slot holds a REFERENCE INTO "
     "THE POOL, as the C's slot holds a ph53_iface *",
     os.path.join("controls", "mu_ref_exec.rs"), _MU_REF_ENGLISH),
    ("ctl_nowitness", "CTL",
     "the witness-free program, so the witness can be RE-PRICED in this "
     "pipeline instead of across two runs",
     os.path.join("controls", "r4_nowitness.rs"),
     "NOT A RUNG AND CANNOT BECOME ONE: it answers differently on an uncovered "
     "blob, which is what the witness is for (NOTES.md 8e). Its side is CTL so "
     "cheapest_in_contract and cheaper_than_shipped refuse it by construction."),
]

#: The two item-79 Verus objects stage 4 runs, and what each must do.
#: (relpath, must_fire, needle)
MU_REF_ARMS = (
    (os.path.join("controls", "mu_ref.rs"), False, None),
    (os.path.join("controls", "mu_ref_cmp.rs"), True,
     "does not yet support"),
)


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
    exact`, so a twin must be byte-identical"*. On `ph53` the pin is `differ` at
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
                           f"{old!r}\nfound {n}. Either the shipped rung has "
                           f"moved under this variant or two substitutions in "
                           f"this list are out of order -- one anchor "
                           f"CONTAINING another's is how this fires. Fix the "
                           f"substitution, never the assertion.")
        src = src.replace(old, new)
    return src


def _absolutise(src):
    return src.replace('#[path = "../../common/driver.rs"]',
                       f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]'
                       ).replace(
        '#[path = "../../../common/driver.rs"]',
        f'#[path = "{os.path.join(REPO, "common", "driver.rs")}"]')


def materialise(name, side, subs):
    """Write the variant's sources into SCRATCH, driver path absolutised.

    ⚠ An R4 variant gets TWO files: the exec rung and the R5 twin. The twin's
    substitution list is explicit and does NOT fall back to the exec one -- the
    twin's items carry a `requires`, an `ensures`, a loop invariant and a
    `decreases`, so the exec anchor does not occur in it and a silent fallback
    would leave the twin unchanged while the exec variant moved."""
    os.makedirs(SCRATCH, exist_ok=True)
    base = "safe_tuned.rs" if side == "R3" else "unsafe.rs"
    src = _absolutise(apply_subs(
        open(os.path.join(PDIR, base), encoding="utf-8").read(),
        subs.get("rs", [])))
    p = os.path.join(SCRATCH, f"{side}_{name}.rs")
    open(p, "w", encoding="utf-8").write(src)
    vp = None
    if side == "R4":
        v = _absolutise(apply_subs(
            open(os.path.join(PDIR, "verus.rs"), encoding="utf-8").read(),
            subs.get("verus", [])))
        vp = os.path.join(SCRATCH, f"{side}_{name}_verus.rs")
        open(vp, "w", encoding="utf-8").write(v)
    return p, vp


def materialise_file(name, side, relpath):
    """A variant that is a COMMITTED FILE rather than a substitution.

    ⚠ It gets NO twin, and stage 4's rule for that is explicit rather than a
    silent skip: see `r4_no_twin_reason`."""
    os.makedirs(SCRATCH, exist_ok=True)
    src = _absolutise(open(os.path.join(PDIR, relpath),
                           encoding="utf-8").read())
    p = os.path.join(SCRATCH, f"{side}_{name}.rs")
    open(p, "w", encoding="utf-8").write(src)
    return p, None


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
    callgrind run -- the two families this row publishes.

    **A1** uses `harness/measure.py::_sum_rows` IMPORTED (see `load_measure`),
    and it is this row's HEADLINE: `kernel` carries 89.5 % of the program here,
    because every helper is `#[inline(always)]`. **W1** is
    `callgrind_annotate`'s own `PROGRAM TOTALS` line, quoted labelled beside it
    because `r3_no_capacity` is a cell where the two disagree in SIGN.

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
#: field. This is the same discipline on the fingerprint side.
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
    `../spec.md` pins `identity: differ`. It is kept and reported because it is
    what makes `r3_oprec_array == r3_oprec_slice` a BYTE-IDENTITY claim rather
    than a tie, which is the sharper form of `ph45` §5.6's result.
    ⚠ It is NOT comparable to the measurement record's `n_fn_nopad`: this counts
    every disassembled instruction in the symbol, including the `int3` pad, and
    `asm.py` reports a non-pad count (766 here against 758 there).

    ⚠⚠⚠ **AND IT IS ONLY COMPARABLE WITHIN ONE BUILD DIRECTORY. MEASURED, NOT
    SUSPECTED, AND VARIANT-DEPENDENT.** The `r3_oprec_slice` source built in two
    directories whose paths differ by 38 characters gives **282 instructions both
    times and two DIFFERENT digests** (`452842362705`, `0abc7468b349`): `rustc`
    embeds the source path in its panic-location data, a longer path moves
    everything after it, and the rip-relative DISPLACEMENTS this function
    deliberately keeps move with it.
    ⚠⚠ **AND IT DOES NOT HAPPEN TO EVERY SPELLING, WHICH IS THE SHARPER
    STATEMENT: 1 of 3 measured.** `v0_shipped` and `r3_chunks_exact` come out
    IDENTICAL across the same two directories -- so a check that looked at one
    spelling would have concluded either way, and the usable rule is **never
    compare a digest across directories**, not *it always differs*. The three
    measurements are the negatives' cases `D18a`, `D18a2`, `D18a3`.
    ▶ `oprec_array_byte_identical_to_slice` is sound because both variants are
    built side by side in `SCRATCH` -- **and it was verified in BOTH directories
    as well, so that claim is not an artefact.**
    ⚠ **ON `ph53` THIS IS HARMLESS AND ON `ph29` IT WOULD NOT BE.** Here
    `twin_identical` is information (`identity: differ`). `ph29` pins `O3 exact`
    and uses the same function as a BAR, and its exec and twin sources differ in
    path length by the six characters of `_verus` -- so the failure mode there is
    a FALSE `!= exec`, i.e. refusing an admissible candidate and reporting an
    endpoint as degenerate when it is not. ⛔ `ph29` is NOT edited (open item
    57/63's scope); this is reported for routing."""
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
#: ⚠⚠ **TWO NEEDLES, NOT ONE, AND THIS ROW IS WHY.** `ph45`'s copy looks for
#: `is not supported` only. Verus 0.2026.08.09 answers the `&T` -> `*const T`
#: coercion with *"The verifier does not yet support the following Rust
#: feature"*, which is the SAME CLASS of refusal -- a coverage fact about the
#: toolchain, not a proof that failed -- and a reader of `is not supported`
#: alone would have scored `controls/mu_ref_cmp.rs` as an unparseable output
#: rather than as a disqualification.
_UNSUPPORTED = ("is not supported", "does not yet support")


def verus_ok(vp):
    """`(ok, message)` for one twin.

    ⚠⚠ **READ THE ERROR TEXT, NOT THE EXIT CODE** -- `../spec.md`'s own hashed
    rule. `is not supported` / `does not yet support` DISQUALIFY, because they
    are what forces a new TRUSTED item; `postcondition not satisfied` and
    `invariant not satisfied` disqualify NOTHING and are proof work (`p05` went
    `11 verified, 1 errors` -> `13 verified, 0 errors` with one lemma and one
    `proof` block, at zero TCB). Both are reported distinctly, because a row
    that conflates them refuses candidates for the wrong reason."""
    r = subprocess.run([sys.executable, VERUS_RUN, vp],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    for needle in _UNSUPPORTED:
        if needle in txt:
            line = next((ln for ln in txt.splitlines() if needle in ln), "")
            return False, f"DISQUALIFIED -- {needle}: " + line.strip()[:220]
    m = _VR.search(txt)
    if not m:
        return False, txt.strip()[-400:]
    return m.group(2) == "0", m.group(0)


def _strip_comments(src):
    """Line comments out, `//!` and `///` included, so that PROSE THAT NAMES AN
    ACCESSOR is not counted as a use of it. `../unsafe.rs` and `../verus.rs`
    both explain these wrappers at length."""
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in src.splitlines())


def trusted_accessors(src, names=ACCESSORS):
    """`(n_call_sites, n_defined, sorted_names_defined)` for this row's named
    unchecked accessors.

    ⚠ MEASURED, not asserted, and definitions are subtracted so the number is
    CALL SITES and not mentions. ⚠ It is deliberately NOT a verdict: a variant
    with a smaller trusted surface at the same price is a THIRD kind of result
    the bench rule has no name for (`ph07`'s `r4_index0`), and this file reports
    it rather than ranking on it.

    ⚠⚠ **THE THREE RETURN VALUES ANSWER DIFFERENT QUESTIONS AND THE ROW NEEDS
    BOTH.** `r4_win_oprec` DELETES `win_get_unchecked`, so its call sites AND
    its definition go; a variant that merely stopped CALLING an accessor would
    still carry it in the TCB, because `.memory/04-verus.md` counts every
    `external_body` item and not just the reached ones.

    ⚠⚠⚠ **AND THE MATCH IS ON THE BARE IDENTIFIER, NOT ON `NAME(`, BECAUSE THE
    FIRST DRAFT OF THIS FUNCTION RETURNED **−1** ON A GENERIC DEFINITION.**
    `controls/mu_ref_exec.rs` declares `fn slot_read_unchecked<'a>(` and
    `fn slot_set_unchecked<'a>(`; a `\\bNAME\\s*\\(` call regex does not match
    across `<'a>`, so each generic accessor scored 0 calls and 1 definition and
    the subtraction went NEGATIVE -- and the variant reported **7** call sites
    where it has **9**. A plausible wrong number and not an error, which is
    `TASK_PHP_037` §6.2's shape in the same function one generation on. Found by
    group I's generic-definition case, not by reading. The `assert` below is
    there so the next such miscount is an error."""
    code = _strip_comments(src)
    calls = defined = 0
    present = []
    for nm in names:
        d = len(re.findall(r"\bfn\s+" + nm + r"\b", code))
        c = len(re.findall(r"\b" + nm + r"\b", code)) - d
        assert c >= 0, (f"trusted_accessors: {nm} scored {c} call site(s), "
                        f"which is not a count. The definition regex matched "
                        f"more often than the identifier did -- fix the regex, "
                        f"not the assertion.")
        calls += c
        defined += d
        if d:
            present.append(nm)
    return calls, defined, sorted(present)


def trusted_items(src):
    """`#[verifier::external_body]` items in a TWIN -- the TCB count, and the
    one that is comparable to the gate record's `verus[].tcb_items`.

    ⚠ It counts EVERY such item, including `load_input` and `emit`, because
    `.memory/04-verus.md` says every `external_body` item is TCB and not just
    the interesting ones. The shipped twin is **6**: four accessors plus those
    two."""
    return _strip_comments(src).count("#[verifier::external_body]")


def unsafe_tokens(src):
    """`unsafe` tokens in an exec variant -- what still makes it an R4."""
    return len(re.findall(r"\bunsafe\b", _strip_comments(src)))


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in `../spec.md`'s `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics rather than a stricter invention:

      * a `forbidden` hit DISQUALIFIES -- `check.py`'s stage 0 has hard-failed on
        one since TASK_068, and its scope is universal by the key's own meaning,
        so it is decidable with no English involved;
      * a `required` miss is REPORTED and does not, because which rungs a
        `required` entry scopes to lives in the entry's ENGLISH and no gate stage
        reproduces it.

    ⚠ Getting this backwards is not a conservative error. This row's `required`
    C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN and the shipped gate
    record carries 10 `required_absent` pairs and calls the row
    `PASS-WITH-BLOCKED-ROWS` (8 until `TASK_PHP_044`; see the module docstring).
    An audit that treated a `required` miss as disqualifying would refuse the
    row's own hardened rung."""
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
# `main`, and `.temp/php42/negatives_spellings.py` drives them over synthetic
# `rows` dicts -- an out-of-contract cheaper candidate, an unpriced one, a
# sub-`TIE_PCT` margin, a candidate excluded by ENGLISH, an R4 with no twin, a
# twin that verifies but is not byte-identical, and an `identity` premise that
# has moved -- none of which is reachable through the CLI.

#: The `problems` entry a run WITHOUT `--verus` carries. A module constant and
#: not a literal inside `main`, so the negatives can hand it to
#: `harness/check.py::control_json_verdict` and prove that the GATE would refuse
#: such a sidecar -- which is the claim, and it is not the same claim as "this
#: script appends a string".
NO_VERUS_PROBLEM = (
    "R4 ADMISSIBILITY WAS NOT CHECKED (no --verus), so every R4 variant's "
    "`in_contract` above is unverified: an R4 is a program whose obligations a "
    "prover can discharge, and without a twin that VERIFIES an R4 candidate is "
    "a control and not a rung. Regenerate with `--verus`, which is what "
    "`pin.regenerate` names.")

#: ⚠ Variants excluded by English rather than by grep. A module constant so a
#: negative can assert the exclusion actually reaches `cheapest_in_contract`.
#:
#: ⭐⭐ **POPULATED AT `TASK_PHP_044`, ON `TASK_PHP_043` §1's RULING OF OPEN
#: ITEM 83, AND IT COSTS THIS ROW ITS R4 HEADLINE.** `../spec.md`'s
#: `idiom.required[4]` pins the witness **REPRESENTATION** -- its leading
#: appositive is *"THE ONE-BYTE-PER-SLOT WITNESS, `[bool; MAXD]`"*, and since
#: `TASK_PHP_044` the entry says so in terms -- so a `u32` bitmask witness, one
#: BIT per slot, is out of contract on that entry even though it discharges the
#: identical obligation, and `required_absent` records the miss on exactly these
#: three and on no other R4 variant.
#:
#: ⛔⛔ **THE PIN WAS NOT WEAKENED TO MATCH A WINNER, AND THE DIRECTION IS THE
#: PROOF**: all three excluded variants are CHEAPER than the shipped R4
#: (-11.40 %, -8.37 %, -3.12 % A1) and two of them also have a SMALLER trusted
#: surface, so applying the ruling makes `r4_endpoint_degenerate` TRUE and
#: deletes the row's *"both endpoints move"* headline.
#: `.memory/02-bench-rules.md`'s *a rung is never cost-selected* binds a pin the
#: same way it binds a rung, and it binds in the expensive direction here.
#:
#: ⚠ **WHAT THIS IS NOT.** It is not a mechanical reading of `required_absent`.
#: `harness/check.py::idiom_audit` (`:2198-2212`) measures the naive
#: every-span-in-every-rung reading at **41 misses of 158 obligations, all 41
#: non-defects and 17 of them ANTI-signal**, so a ruling can never be read off
#: the presence report. The SCOPE comes from each entry's English and is a
#: reading; `english_verdict_problems()` below only enforces that a reading, once
#: made, is applied to every variant it reaches.
#:
#: ⓘ `r3_no_capacity` is excluded too and is NOT here: its verdict is declared
#: inline in `R3_VARIANTS` because it predates this ruling and rests on a second,
#: independent entry (`required[8]`). `english_verdict` is
#: `eng or ENGLISH_VERDICTS.get(name)`, so the inline declaration wins.
_BITMASK_VERDICT = (
    "OUT OF CONTRACT BY ENGLISH (open item 83, ruled at TASK_PHP_043 section 1, "
    "applied at TASK_PHP_044): ../spec.md's idiom.required[4] pins the witness "
    "REPRESENTATION -- `wrote[i]`, THE ONE-BYTE-PER-SLOT WITNESS, `[bool; "
    "MAXD]` -- and not merely the role, so a u32 bitmask witness at one BIT per "
    "slot establishes the same slot-coverage fact by a DIFFERENT expression and "
    "is out of contract on that entry even though its twin verifies and even "
    "though it is CHEAPER. The named-spelling standard in idiom.why names this "
    "exact case and resolves it against the challenger; the entry's own English "
    "agrees with its backticks, because \"indexed SAFELY on purpose\" also fails "
    "on a witness that performs no indexed access. PRICED AND REPORTED ANYWAY: "
    "required_absent records the miss, witness_cost_pct_w1 keeps the cost, and "
    "variants[].trusted_items keeps the surface, so this is a CONTROL-CLASS "
    "result -- a witness-representation change that would be cheaper and "
    "smaller-surface is out of this row's contract -- and not an endpoint.")

ENGLISH_VERDICTS = {
    "r4_bitmask": _BITMASK_VERDICT,
    "r4_bitmask_pool": _BITMASK_VERDICT,
    "r4_bitmask_min": _BITMASK_VERDICT,
}

#: The entry the ruling turns on, and the side its English scopes to. A pair and
#: not two literals inside a function, so `english_verdict_problems` and the
#: selftest cannot drift apart.
WITNESS_PIN = ("required[4]", "R4")


def english_verdict_problems(rows, pin=WITNESS_PIN, verdicts=None):
    """`[problem, ...]` -- is the item-83 ruling applied CONSISTENTLY?

    ⚠⚠ **THE MUST-FIRE ARM FOR `ENGLISH_VERDICTS`, AND THE EDIT IT EXISTS TO
    CATCH IS *EMPTYING THE CONSTANT AGAIN*.** `PROTOCOL_PHP.md` §H: a change to
    a validator lands with its must-fire negatives. This file's verdict is
    `cheapest_in_contract` / `cheaper_than_shipped`, `ENGLISH_VERDICTS` is now
    the only thing standing between the bitmask variants and the R4 endpoint,
    and **nothing else in the pipeline would notice its removal** -- the
    exclusion is English, `required` is presence-only and cannot fail the gate,
    and the numbers would simply come back looking like a searched endpoint.
    So `main` runs this on the REAL rows on every invocation and appends to
    `problems`, which `harness/check.py::control_json_verdict` turns into
    `FRESH+VERDICT-FAILED` at gate stage 9b.

    ⭐ **THE RULE IS DERIVED FROM THE AUDIT, NOT FROM A NAME LIST**, which is
    what makes it a check rather than a restatement: every variant on the pinned
    entry's own side, other than that side's shipped rung, that records
    `required[4]` in `required_absent` must carry an `english_verdict`. That
    fires if the constant is emptied AND it fires for a FOURTH bitmask variant
    somebody adds later and forgets to exclude -- which a hardcoded name list
    would not.

    ⛔ **IT IS DELIBERATELY SCOPED TO ONE ENTRY AND ONE SIDE.** Generalising it
    to every backticked `required` span is the reading `check.py::idiom_audit`
    measured at 41 misses of 158 obligations, all 41 non-defects -- every R3
    variant misses `required[4]` because the entry is R4-scoped, and
    `ctl_nowitness` misses it because it has no witness at all, and neither is a
    defect. The SCOPE is the reading; this function is the bookkeeping.

    ⚠ **AND IT CHECKS THE KEYS TOO.** A typo'd key in `ENGLISH_VERDICTS`
    excludes nothing and reads exactly like a populated constant, which is the
    silent-failure shape this whole file is written against."""
    tag, side = pin
    verdicts = ENGLISH_VERDICTS if verdicts is None else verdicts
    out = []
    declared = {n for n, _s, _w, _su, _e in
                (list(R3_VARIANTS) + list(R4_VARIANTS) + list(FILE_VARIANTS))}
    for k in sorted(verdicts):
        if k not in declared:
            out.append(
                f"ENGLISH_VERDICTS names `{k}`, which is not a declared "
                f"variant, so it excludes NOTHING while reading as an "
                f"exclusion -- a typo here is silent")
    for (s, name), r in sorted(rows.items()):
        if s != side or name == "v0_shipped":
            continue
        missed = any(m.startswith(tag + " ")
                     for m in (r.get("required_absent") or []))
        if missed and not r.get("english_verdict"):
            out.append(
                f"{s} {name} records `{tag}` in required_absent and carries NO "
                f"english_verdict, so it is still counted as a rung candidate. "
                f"../spec.md's {tag} pins the witness REPRESENTATION (open item "
                f"83, ruled at TASK_PHP_043 section 1) and that ruling is "
                f"either applied to every variant it reaches or it is a patch "
                f"on the three that embarrassed the headline. Fix: add "
                f"`{name}` to ENGLISH_VERDICTS.")
    return out


def english_verdict_selftest():
    """`[problem, ...]` -- the §H battery for the exclusion PATH, on synthetic
    rows, run on every invocation because a green row exercises a validator and
    does not attack it.

    Seven arms. The three must-FIRE ones are the point: **E1** the emptied
    constant, **E2** a falsy verdict string, **E3** a typo'd key. The four
    must-NOT-fire ones pin what the ruling may NOT do: **E4** the R3 half stays
    searched with `r3_chunks_mask` cheapest, **E5** the inline `R3_VARIANTS`
    declaration still beats `ENGLISH_VERDICTS`, **E6** an R3 variant missing the
    R4-scoped pin is not a problem, **E7** `ctl_nowitness` is not either.

    ⚠ **The A1 figures are the row's own committed ones** so that E1's "the
    endpoint comes back" is the real arithmetic and not a toy: the shipped R4 is
    1116.94724 and the three bitmask variants are the only R4 cells below it."""
    A1 = {"v0_shipped": 1116.94724, "r4_bitmask": 989.67032,
          "r4_bitmask_pool": 1023.46856, "r4_bitmask_min": 1082.0678,
          "r4_set_checked": 1122.58028, "r4_win_checked": 1495.79284}

    def mk(verdicts):
        rows = {}
        for n, a in A1.items():
            rows[("R4", n)] = {
                "side": "R4", "name": n, "ir_per_call_small": a,
                "in_contract": True, "verus_rs": "x",
                "required_absent": (["required[4] `wrote[i]`"]
                                    if "bitmask" in n else []),
                "english_verdict": verdicts.get(n)}
        return rows
    bad = []

    def want(tag, cond, why):
        if not cond:
            bad.append(f"{tag}: {why}")

    full = {k: "out by English" for k in ENGLISH_VERDICTS}
    rows = mk(full)
    want("E0 (must-NOT-fire)", not english_verdict_problems(rows),
         "the shipped constant leaves a consistency problem")
    want("E0b (must-fire consequence)", not cheaper_than_shipped(rows, "R4"),
         "with the three excluded, an R4 candidate still beats shipped")

    rows = mk({})
    probs = english_verdict_problems(rows, verdicts={})
    want("E1 (must-FIRE: the constant emptied)", len(probs) == 3,
         f"emptying ENGLISH_VERDICTS reported {len(probs)} problems, want 3 "
         f"(one per bitmask variant)")
    beat = cheaper_than_shipped(rows, "R4")
    want("E1b (must-FIRE: and the endpoint comes back)",
         beat and beat[0]["name"] == "r4_bitmask",
         "emptying the constant did not restore r4_bitmask as the cheaper "
         "candidate, so E1 is not measuring the path that publishes the number")

    rows = mk({k: "" for k in ENGLISH_VERDICTS})
    want("E2 (must-FIRE: a falsy verdict string)",
         len(english_verdict_problems(
             rows, verdicts={k: "" for k in ENGLISH_VERDICTS})) == 3,
         "an empty-string verdict read as an exclusion; `_admissible` tests "
         "`not r.get('english_verdict')`, so only a TRUTHY string excludes")

    want("E3 (must-FIRE: a typo'd key)",
         any("not a declared variant" in p for p in english_verdict_problems(
             mk(full), verdicts=dict(full, r4_bitmsak="typo"))),
         "a misspelled ENGLISH_VERDICTS key was accepted silently")

    r3 = {"v0_shipped": 1387.67508, "r3_chunks_mask": 942.47724,
          "r3_slice_param": 1388.13536}
    rows = mk(full)
    for n, a in r3.items():
        rows[("R3", n)] = {
            "side": "R3", "name": n, "ir_per_call_small": a,
            "in_contract": True,
            "required_absent": ["required[4] `wrote[i]`"],
            "english_verdict": None}
    c3 = cheapest_in_contract(rows, "R3")
    want("E4 (must-NOT-fire: the R3 half is UNTOUCHED)",
         c3 and c3["name"] == "r3_chunks_mask"
         and bool(cheaper_than_shipped(rows, "R3")),
         "the ruling moved the R3 endpoint; item 83 does not reach it and "
         "F100's R3 half must stay searched")
    want("E6 (must-NOT-fire: R3 misses an R4-scoped pin)",
         not any(" r3_" in p for p in english_verdict_problems(rows)),
         "an R3 variant missing the R4-scoped required[4] was reported as a "
         "problem -- that is check.py's measured 41-of-41 failure mode")

    rows[("CTL", "ctl_nowitness")] = {
        "side": "CTL", "name": "ctl_nowitness", "ir_per_call_small": 888.082,
        "in_contract": True, "required_absent": ["required[4] `wrote[i]`"],
        "english_verdict": "not a rung"}
    want("E7 (must-NOT-fire: the CTL side)",
         not any("ctl_nowitness" in p for p in english_verdict_problems(rows)),
         "the witness-free control was judged against an R4-scoped pin")

    inline = [e for n, _s, _w, _su, e in R3_VARIANTS if n == "r3_no_capacity"]
    want("E5 (must-NOT-fire: inline beats the constant)",
         inline and inline[0]
         and (inline[0] or ENGLISH_VERDICTS.get("r3_no_capacity"))
         == inline[0],
         "`eng or ENGLISH_VERDICTS.get(name)` no longer prefers the inline "
         "R3_VARIANTS declaration, so r3_no_capacity's two independent grounds "
         "cannot both be recorded")
    return bad


def r4_no_twin_reason(r):
    """Why an R4 variant with no twin file is inadmissible, or `None`.

    ⚠⚠ **A RULE AND NOT A SILENT SKIP.** `ph45`'s stage 4 does
    `if not r.get("verus_rs"): continue`, which leaves `in_contract` at whatever
    stage 0b set -- i.e. `True` -- for an R4 candidate that was never put
    through Verus at all. That row had no such variant so the hole was latent;
    this row HAS one (`r4_mu_ref`, open item 79), so the hole would have been
    live and would have published a figure for a candidate with no proof."""
    if r.get("side") != "R4" or r.get("verus_rs"):
        return None
    return ("R4 with NO TWIN FILE: an R4 is a program whose obligations a "
            "prover can discharge, and nothing was put through Verus for this "
            "one. Inadmissible by rule, not by measurement.")


def twin_identical(r):
    """Whether a variant's twin compiles to the same `kernel` as its exec rung.

    ⚠ It compares BOTH the digest and the instruction count, and it is FALSE
    when either is missing. A missing field must not read as agreement: the
    digest of an empty disassembly is a constant, so `None == None` and
    `'d41d8cd98f00' == 'd41d8cd98f00'` are the two ways this check can say
    *byte-identical* about two things that were never compared. `disasm` raises
    on the second; this function refuses the first.

    ⚠⚠ **ON `ph53` THIS IS INFORMATION, NOT A BAR** -- see `admissibility()`.
    `ph29`'s copy uses it as a gate because `ph29` pins `O3 exact`."""
    a, b = r.get("kernel_fingerprint"), r.get("verus_kernel_fingerprint")
    na, nb = r.get("kernel_insns"), r.get("verus_kernel_insns")
    if a is None or b is None or na is None or nb is None:
        return False
    # ⚠⚠⚠ THE THIRD WAY THIS CAN SAY *byte-identical* ABOUT NOTHING, AND
    # `ph29`'s COPY DOES NOT REFUSE IT -- `TASK_PHP_037` §6.2, open item 63.
    # A kernel of length ZERO is a measurement that did not happen.
    if na == 0 or nb == 0 or _EMPTY_MD5 in (a, b):
        return False
    return a == b and na == nb


def byte_identical_pair(rows, a, b, side="R3"):
    """Whether two EXEC variants on one side compile to the same `kernel`.

    ⭐ This is what makes `r3_oprec_array == r3_oprec_slice` the sharp form of
    `ph45` §5.6's result: there the `&[u8; N]` type was a TIE *within a
    threshold*, here it is byte-identical. Same refusals as `twin_identical`."""
    ra, rb = rows.get((side, a)), rows.get((side, b))
    if not ra or not rb:
        return False
    return twin_identical({"kernel_fingerprint": ra.get("kernel_fingerprint"),
                           "verus_kernel_fingerprint":
                               rb.get("kernel_fingerprint"),
                           "kernel_insns": ra.get("kernel_insns"),
                           "verus_kernel_insns": rb.get("kernel_insns")})


def _admissible(rows, side, key):
    return [r for r in rows.values()
            if r.get("side") == side and r.get("in_contract")
            and not r.get("english_verdict") and r.get(key) is not None]


def cheapest_in_contract(rows, side="R3", key="ir_per_call_small"):
    """The cheapest IN-CONTRACT, PRICED candidate on one side, or `None`.

    Four exclusions and each one is a defect this would otherwise publish: a
    variant that is out of contract by GREP, one that is out of contract by
    ENGLISH, one that was never priced, and a side that is not a rung side.

    ⚠ `key` defaults to **A1** here and to the whole-program family in `ph45`'s
    copy, and the difference is measured rather than stylistic: on `ph45` A1 is
    identical for every variant on a side, so a `min` over it would return the
    enumeration order; on `ph53` `kernel` carries 89.5 % of the program and A1's
    spread over the R3 side is ~55 pp. `a1_spread_pp` and `wp_spread_pp` are
    both in the sidecar so a reader can check that this default is still the
    right one."""
    if side not in RUNG_SIDES:
        return None
    c = _admissible(rows, side, key)
    return min(c, key=lambda r: r[key]) if c else None


def dearest_in_contract(rows, side="R3", key="ir_per_call_small"):
    """The other end of the R3-SIDE SPAN, which is the second of the two
    quantities that may be published."""
    if side not in RUNG_SIDES:
        return None
    c = _admissible(rows, side, key)
    return max(c, key=lambda r: r[key]) if c else None


def cheaper_than_shipped(rows, side="R4", key="ir_per_call_small",
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


def smaller_surface(rows, side="R4"):
    """In-contract candidates whose TCB is strictly smaller than the shipped
    rung's, cheapest first. ⚠ Keyed on `trusted_items` (the `external_body`
    count in the TWIN) and not on call sites, because an accessor that is
    defined and never called is still in the trusted base."""
    base = rows.get((side, "v0_shipped"), {}).get("trusted_items")
    if base is None:
        return []
    return sorted((r for r in _admissible(rows, side, "ir_per_call_small")
                   if r.get("trusted_items") is not None
                   and r["trusted_items"] < base),
                  key=lambda r: r["ir_per_call_small"])


def witness_cost(rows, name, key="ir_per_call_small_wp"):
    """What one variant's coverage witness costs, against `ctl_nowitness` in
    THIS pipeline.

    ⭐ `../NOTES.md` §8e publishes **+21.775 %** for the shipped witness and
    calls it *"the row's largest single number"*, measured across two
    `controls/negatives.py` runs. Computing it here from two cells of one run is
    what lets the bitmask witness be compared with it on equal terms."""
    base = rows.get(("CTL", "ctl_nowitness"), {}).get(key)
    r = rows.get(("R4", name), {}).get(key)
    if not base or r is None:
        return None
    return 100.0 * (r - base) / base


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit; no build, no callgrind")
    ap.add_argument("--verus", action="store_true",
                    help="stage 4: put every R4 twin through Verus, and run "
                         "the two open-item-79 controls")
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
    print(f"  ../spec.md                pinned   {pinned}")
    print(f"  results-php/gate/...json  measured {measured}")
    print(f"  -> {ident_why}")
    if pinned.get("O3") != measured.get("O3"):
        problems.append(
            f"the `identity` pin (O3 {pinned.get('O3')!r}) and the gate record "
            f"(O3 {measured.get('O3')!r}) DISAGREE, so this file cannot tell "
            f"which admissibility rule applies to an R4 candidate and fell back "
            f"to the weaker one")

    variants = ([(n, s, w, subs, e) for n, s, w, subs, e in R3_VARIANTS]
                + [(n, s, w, subs, e) for n, s, w, subs, e in R4_VARIANTS]
                + [(n, s, w, p, e) for n, s, w, p, e in FILE_VARIANTS])
    rows = {}
    print("\n0b. THE SPELLING AUDIT -- every backticked idiom entry, "
          "harness/check.py::spelling_matches")
    for name, side, why, subs, eng in variants:
        if isinstance(subs, str):
            rs, vp = materialise_file(name, side, subs)
        else:
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
        print(f"  {side} {name:18s} "
              + ("IN CONTRACT" if not forb else "OUT: " + "; ".join(forb))
              + "   required absent: "
              + (", ".join(m.split("`")[1] for m in miss) or "none")
              + ("   ⚠ OUT BY ENGLISH" if rows[(side, name)]["english_verdict"]
                 else ""))

    # ---- §H: the exclusion PATH, attacked and then checked ------------------
    # ⚠⚠ TWO DIFFERENT CHECKS AND BOTH RUN ON EVERY INVOCATION. The selftest
    # drives the verdict functions over SYNTHETIC rows, which is the only way to
    # see the arms fire -- the shipped tree's `problems` is empty, so a green run
    # is not evidence that any of this CAN fire (check.py's own argument for
    # `_CONTROL_VERDICT_CASES`). The consistency check then runs on the REAL
    # rows, and it is the one that fires if ENGLISH_VERDICTS is emptied again.
    st = english_verdict_selftest()
    ev = english_verdict_problems(rows)
    print(f"\n0c. THE ITEM-83 EXCLUSION (`ENGLISH_VERDICTS`), §H.\n"
          f"  selftest   {'PASS' if not st else 'FAIL'}   "
          f"7 arms over synthetic rows (3 must-FIRE, 4 must-NOT-fire)\n"
          f"  consistency {'ok  ' if not ev else 'FAIL'}  "
          f"{WITNESS_PIN[0]} is {WITNESS_PIN[1]}-scoped; every "
          f"{WITNESS_PIN[1]} variant that misses it carries a verdict\n"
          f"  excluded    "
          + (", ".join(sorted(ENGLISH_VERDICTS)) or "NOTHING -- see §H"))
    for p in st + ev:
        print(f"    *** {p}")
    problems.extend(st)
    problems.extend(ev)

    if args.audit_only:
        for p in problems:
            print(f"  *** {p}", file=sys.stderr)
        return 1 if problems else 0

    print("\n1. BUILD + CHECKSUM + KERNEL FINGERPRINT + TRUSTED SURFACE.\n"
          "   ⚠⚠ THE REFERENCE CHECKSUM IS PER SIDE: this row's R3 and R4\n"
          "   DISAGREE on inputs/adversarial-cmp.bin by declaration "
          "(safe_tuned.rs's\n   header, check.py stage 4), so a cross-side "
          "reference would fail every R3\n   variant on one input and the "
          "failure would be this control's.")
    ref = {}
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"], os.path.join(SCRATCH, f"{side}_{name}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side} {name:18s} BUILD FAILED")
            problems.append(f"{side} {name} does not build: {err}")
            continue
        r["exe"] = exe
        r["kernel_insns"], r["kernel_fingerprint"] = kernel_fingerprint(exe)
        # ⚠ RE-READ FROM THE FILE, and it is not defensive: `TASK_PHP_037` §6.2
        # found this exact function reading the `src` left over from the
        # stage-0b audit loop, so every variant reported the LAST audited
        # variant's count -- 12 for three SAFE rungs containing no accessor at
        # all. A plausible wrong number, not an error.
        vsrc = open(r["rs"], encoding="utf-8").read()
        (r["trusted_call_sites"], r["accessors_defined"],
         r["accessor_names"]) = trusted_accessors(vsrc)
        r["unsafe_tokens"] = unsafe_tokens(vsrc)
        if r["verus_rs"]:
            r["trusted_items"] = trusted_items(
                open(r["verus_rs"], encoding="utf-8").read())
        ans = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = ans
        refside = "R4" if side == "CTL" else side
        if name == "v0_shipped":
            ref[side] = ans
            print(f"  {side} {name:18s} REFERENCE  "
                  f"kernel {r['kernel_insns']:4d} {r['kernel_fingerprint']}"
                  f"   accessors {r['trusted_call_sites']:2d} call site(s), "
                  f"{r['accessors_defined']} defined"
                  + (f", TCB {r['trusted_items']}" if r.get("trusted_items")
                     else ""))
            continue
        base = ref.get(refside)
        if base is None:
            problems.append(f"{side} {name}: no {refside} v0_shipped reference "
                            f"to compare against -- the checksum check did not "
                            f"happen and must not read as a pass")
            continue
        diff = [k for k, v in ans.items() if base.get(k) != v]
        print(f"  {side} {name:18s} "
              + ("ok  identical on all "
                 f"{len(ans)} inputs" if not diff
                 else f"*** DIFFERS on {diff}")
              + f"   kernel {r['kernel_insns']:4d} {r['kernel_fingerprint']}"
              + f"   accessors {r['trusted_call_sites']:2d}/"
                f"{r['accessors_defined']}"
              + (f" TCB {r['trusted_items']}" if r.get("trusted_items") else ""))
        if diff:
            problems.append(f"{side} {name} changes the answer on {diff} "
                            f"-- it is not a respelling of this kernel")
            r["in_contract"] = False

    print("\n2. THE PRICE -- BOTH FAMILIES, from ONE callgrind run per cell.\n"
          "   A1 = kernel_exclusive_ir/call (measure.py's own statistic, "
          "IMPORTED) -- THE HEADLINE.\n   W1 = whole-program Ir/call "
          "(callgrind's PROGRAM TOTALS), quoted labelled.")
    print(f"  {'cell':26s} {'A1 small':>11s} {'A1 large':>11s} "
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
        print(f"  {side + ' ' + name:26s} {r['ir_per_call_small']:11.3f} "
              f"{r['ir_per_call_large']:11.3f} "
              f"{r['ir_per_call_small_wp']:11.3f} "
              f"{r['ir_per_call_large_wp']:11.3f}")
    b3a = rows[("R3", "v0_shipped")].get("ir_per_call_small")
    b4a = rows[("R4", "v0_shipped")].get("ir_per_call_small")
    b4w = rows[("R4", "v0_shipped")].get("ir_per_call_small_wp")
    print(f"\n  {'cell':26s} {'A1 vs R4ship':>14s} {'W1 vs R4ship':>14s} "
          f"{'A1 vs own side':>15s}")
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        if r.get("ir_per_call_small") is None:
            continue
        own = b3a if side == "R3" else b4a
        r["pct_vs_r4ship_a1"] = (100.0 * (r["ir_per_call_small"] - b4a) / b4a
                                 if b4a else None)
        r["pct_vs_r4ship_wp"] = (
            100.0 * (r["ir_per_call_small_wp"] - b4w) / b4w if b4w else None)
        r["pct_vs_own_side_a1"] = (
            100.0 * (r["ir_per_call_small"] - own) / own if own else None)
        print(f"  {side + ' ' + name:26s} {r['pct_vs_r4ship_a1']:+13.2f}% "
              f"{r['pct_vs_r4ship_wp']:+13.2f}% "
              f"{r['pct_vs_own_side_a1']:+14.2f}%")

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
                    rec_ok = False
                    problems.append(
                        f"A1 {cell}/{inp}: NOT COMPARABLE (record={w}, "
                        f"here={g}) -- stage 3 did not run and must not read "
                        f"as a pass")
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
                rec_ok = False
                problems.append(f"W1 {cell}/{inp}: NOT MEASURED")
                continue
            w = tot / float(n)
            d = abs(w - g) / w * 100.0
            print(f"  W1 {cell:12s} {inp:10s} NOTES.md §8e={w:12.4f} "
                  f"here={g:12.4f}  delta={d:.4f}%")
            if d > 0.5:
                rec_ok = False
                problems.append(
                    f"W1 {cell}/{inp}: this pipeline measures {g:.4f} Ir/call "
                    f"whole-program where NOTES.md §8e publishes {w:.4f} "
                    f"({d:.2f}% apart)")
    else:
        print(f"  no measurement record at {RECORD}")

    mu_ref_arms = []
    if args.verus:
        print("\n4. R4 ADMISSIBILITY -- the twin must VERIFY. ⚠ READ THE ERROR "
              "TEXT:\n   `is not supported` and `does not yet support` "
              "disqualify; a failed\n   postcondition is proof work. ⚠⚠ "
              "Byte-identity is RECORDED and is NOT a\n   bar on this row -- "
              "see stage 0a.")
        for name, side, why, subs, eng in R4_VARIANTS + [
                (n, s, w, p, e) for n, s, w, p, e in FILE_VARIANTS]:
            r = rows[(side, name)]
            if side != "R4":
                continue
            reason = r4_no_twin_reason(r)
            if reason:
                r["in_contract"] = False
                r["verus_msg"] = reason
                print(f"  R4 {name:18s} NO TWIN          {reason[:74]}")
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
            print(f"  R4 {name:18s} {state:16s} "
                  f"{msg.splitlines()[0][:60] if msg else ''}"
                  + (f"   TCB {r.get('trusted_items')}"
                     f"   twin kernel {r.get('verus_kernel_insns')} "
                     f"{r.get('verus_kernel_fingerprint')}"
                     f"  {'== exec' if r['identity_exact'] else '!= exec'}"
                     if r.get("verus_kernel_fingerprint") else ""))
            if name == "v0_shipped" and not ok:
                problems.append(
                    "R4 v0_shipped's own twin does not verify -- this pipeline "
                    "is not measuring the shipped rung")

        print("\n4b. OPEN ITEM 79 -- the MaybeUninit<&Iface> representation's "
              "Verus half, as\n    TWO RUNNABLE ARMS rather than a sentence. "
              "⚠ The second MUST FAIL.")
        for rel, must_fire, needle in MU_REF_ARMS:
            p = os.path.join(PDIR, rel)
            if not os.path.exists(p):
                problems.append(f"open item 79 arm {rel} is MISSING -- the "
                                f"claim it carries is then unchecked")
                continue
            ok, msg = verus_ok(p)
            fired = not ok
            good = (fired == must_fire
                    and (not needle or not must_fire or needle in msg))
            mu_ref_arms.append({"file": rel, "must_fire": must_fire,
                                "fired": fired, "as_declared": good,
                                "message": msg})
            print(f"    {rel:28s} must_fire={must_fire!s:5s} "
                  f"fired={fired!s:5s} {'OK' if good else '*** NOT AS DECLARED'}"
                  f"\n      {msg.splitlines()[0][:110] if msg else ''}")
            if not good:
                problems.append(
                    f"open item 79 arm {rel}: must_fire={must_fire} but "
                    f"fired={fired}"
                    + (f" / needle {needle!r} absent" if needle
                       and must_fire and needle not in msg else "")
                    + f" -- {msg[:200]}")
    else:
        print("\n4. R4 ADMISSIBILITY -- skipped (pass --verus). ⚠ Until it is "
              "run, no R4 variant\n   above is a RUNG; each is a control.")
        # ⚠⚠⚠ AND THE SIDECAR MUST SAY SO, BECAUSE A RUN WITHOUT `--verus`
        # WRITES A FILE THAT LOOKS COMPLETE AND IS NOT (`TASK_PHP_022` §3.2
        # gap 5, DEMONSTRATED LIVE AT `TASK_PHP_024` §1.6 on `ph07`). PROBE
        # RULE 1: a probe that CANNOT EVALUATE must say so and exit non-zero.
        problems.append(NO_VERUS_PROBLEM)

    # ---- the two published numbers, in BOTH families ------------------------
    print("\n5. WHAT MAY BE QUOTED. TWO QUANTITIES, IN TWO LABELLED FAMILIES.")
    r3s, r4s = rows[("R3", "v0_shipped")], rows[("R4", "v0_shipped")]
    for fam, key, pct in (("A1  (kernel-exclusive Ir/call, small.bin) -- "
                           "THE HEADLINE",
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
                # ⚠⚠ NOT A SPAN AT ALL: a `min` over a set of equal values is
                # the enumeration order, not a minimum. `ph45` reaches this
                # branch in family A1; this row does not, and the branch is
                # kept because the next row might.
                print(f"  R3-side span     ⚠ NOT COMPUTABLE IN THIS FAMILY: "
                      f"every in-contract R3 variant\n                   "
                      f"measures {lo[pct]:+.2f}% here, within the {TIE_PCT}% "
                      f"tie threshold of each other.")
            else:
                print(f"  R3-side span     cheapest-found .. dearest-found in "
                      f"contract  {lo[pct]:+.2f}% .. {hi[pct]:+.2f}%"
                      f"   `{lo['name']}` .. `{hi['name']}`")
    print("\n  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it). Where\n     this file says the "
          "ORDERING reverses it means ordering, never interval.")

    beat = cheaper_than_shipped(rows, "R4")
    beat3 = cheaper_than_shipped(rows, "R3")
    small = smaller_surface(rows, "R4")
    for side in RUNG_SIDES:
        adm = _admissible(rows, side, "ir_per_call_small")
        tried = len([1 for r in rows.values() if r.get("side") == side])
        print(f"\n  ⚠ {side} SIDE, SEARCHED ({len(adm)} admissible of {tried} "
              f"tried), A1:")
        for r in sorted(adm, key=lambda r: r["ir_per_call_small"]):
            d = r["pct_vs_own_side_a1"]
            verdict = ("SHIPPED" if r["name"] == "v0_shipped"
                       else (f"TIE (< {TIE_PCT}%)" if abs(d) <= TIE_PCT
                             else ("CHEAPER" if d < 0 else "dearer")))
            print(f"      {r['name']:18s} {r['ir_per_call_small']:10.3f} "
                  f"Ir/call  {d:+7.2f}% vs shipped {side}   {verdict}"
                  + (f"   TCB {r['trusted_items']}"
                     if r.get("trusted_items") is not None else ""))
        for (s, nm), r in sorted(rows.items()):
            if s == side and (not r.get("in_contract")
                              or r.get("english_verdict")):
                print(f"      {nm:18s} INADMISSIBLE -- "
                      + (r.get("english_verdict") or r.get("verus_msg")
                         or "see stage 0b/1")[:96]
                      + (f"   [priced: A1 {r['ir_per_call_small']:.3f}, "
                         f"{r['pct_vs_own_side_a1']:+.2f}% vs shipped {side}]"
                         if r.get("ir_per_call_small") is not None else ""))
    if not beat:
        print("\n  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              "DEGENERATE on this row.")
    else:
        print(f"\n  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS -- `{beat[0]['name']}`, "
              f"{beat[0]['pct_vs_own_side_a1']:+.2f}% A1 against the shipped "
              f"R4.\n     THE R4 SIDE OF THIS ROW WAS UNSEARCHED, and the "
              f"headline `fixed-R4 bound`\n     above is a bound over an "
              f"UNSEARCHED endpoint. ⚠ The rung does NOT move:\n     "
              f"`.memory/02-bench-rules.md` holds R4 fixed by fiat and that "
              f"fiat is what\n     makes the bound a bound.")
    if small:
        print(f"  ⭐ AND {len(small)} IN-CONTRACT CANDIDATE(S) HAVE A SMALLER "
              f"TRUSTED BASE than the shipped\n     rung's "
              f"{r4s.get('trusted_items')} `external_body` items:")
        for r in small:
            print(f"      {r['name']:18s} TCB {r['trusted_items']}  "
                  f"{r['pct_vs_own_side_a1']:+7.2f}% A1   "
                  + ("⭐ CHEAPER *AND* SMALLER-SURFACE"
                     if r["pct_vs_own_side_a1"] < -TIE_PCT
                     else "dearer, so the surface reduction is PRICED"))
    if beat3:
        print(f"  ⚠⚠ AND THE R3 SIDE MOVES TOO -- `{beat3[0]['name']}`, "
              f"{beat3[0]['pct_vs_own_side_a1']:+.2f}% A1 against the shipped "
              f"R3.\n     **NEITHER published endpoint is a searched "
              f"endpoint.**")
        c3 = cheapest_in_contract(rows, "R3", "ir_per_call_small")
        c4 = cheapest_in_contract(rows, "R4", "ir_per_call_small")
        if c3 and c4:
            print(f"     ⚠ ORDERING UNDER SEARCH (not an interval): cheapest "
                  f"R3 `{c3['name']}` {c3['ir_per_call_small']:.3f} vs "
                  f"cheapest R4\n       `{c4['name']}` "
                  f"{c4['ir_per_call_small']:.3f} Ir/call -- "
                  + ("R3 cheaper" if c3["ir_per_call_small"]
                     < c4["ir_per_call_small"] else "R4 cheaper")
                  + f", where the shipped bound says R3 is "
                    f"{r3s['pct_vs_r4ship_a1']:+.2f}% DEARER. THE SIGN "
                    f"REVERSES.")

    wship = witness_cost(rows, "v0_shipped")
    wbm = witness_cost(rows, "r4_bitmask")
    print("\n6. THE COVERAGE WITNESS, RE-PRICED IN ONE PIPELINE "
          "(../NOTES.md §8e).")
    print(f"  shipped [bool; MAXD] witness   {wship:+.3f}% W1 against "
          f"ctl_nowitness   (§8e publishes +21.775 %)")
    print(f"  u32 bitmask witness            {wbm:+.3f}% W1 against "
          f"ctl_nowitness")

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph53-iface-tail-uninit/controls/"
                "spellings.py --verus",
            "note":
                "The pin covers the two rung sources the variants are derived "
                "from, verus.rs (the R4 admissibility half), spec.md (the "
                "declaration the audit runs against AND the `identity` pin the "
                "admissibility rule reads), NOTES.md (whose section 8e carries "
                "the whole-program total stage 3 reproduces), inputs/gen.py "
                "(the corpus every number is measured over), the four "
                "controls/ files that are variants or open-item-79 arms, and "
                "this script. It does NOT cover "
                "results-php/ph53-iface-tail-uninit.json: stage 3 compares "
                "against that record at run time and prints the delta, which "
                "is a stronger check than a hash of it."},
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
                        "NOTES.md", "inputs/gen.py",
                        "controls/mu_ref.rs", "controls/mu_ref_cmp.rs",
                        "controls/mu_ref_exec.rs", "controls/r4_nowitness.rs",
                        "controls/spellings.py")},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        "verus_checked": bool(args.verus),
        "identity_pinned": pinned,
        "identity_measured": measured,
        "identity_requires_byte_identity": need_ident,
        "identity_checked": ident_why,
        "statistic":
            "TWO FAMILIES, BOTH PUBLISHED, from one callgrind run per cell. A1 "
            "= kernel_exclusive_ir / n_iters -- harness/measure.py::_sum_rows "
            "itself, IMPORTED and not transcribed -- which stage 3 compares "
            "against results-php/ph53-iface-tail-uninit.json in FOUR cells. W1 "
            "= whole-program Ir / n_iters off callgrind_annotate's PROGRAM "
            "TOTALS, which stage 3 compares against NOTES.md section 8e's one "
            "committed whole-program total. A1 IS THE HEADLINE ON THIS ROW and "
            "that is the opposite of ph45: every helper here is "
            "inline(always) into `kernel`, so `kernel` carries 89.5 per cent "
            "of the program and A1 resolves the search (a1_spread_pp below is "
            "tens of percentage points, where ph45's was 0.000000). Both "
            "families are printed for every comparison anyway, and "
            "r3_no_capacity is the cell that shows why: it is the one variant "
            "where they disagree in SIGN, because the allocator work it adds "
            "is outside `kernel`.",
        "headline_statistic": "ir_per_call_small",
        "reproduces_shipped_record": rec_ok,
        "reproduces_shipped_record_scope":
            "TWO Ir FAMILIES AT 0.5 PER CENT TOLERANCE, AND NOT THE STATIC "
            "COUNTS. A1 is compared against "
            "results-php/ph53-iface-tail-uninit.json in four cells (safe_tuned "
            "and unsafe, small.bin and large.bin) and W1 against NOTES.md "
            "section 8e. `kernel_insns` below is a raw disassembled "
            "instruction count over the `kernel` symbol INCLUDING the int3 pad "
            "and is NOT comparable to the record's n_fn_nopad (766 against "
            "758). ALSO NOT IN SCOPE: NOTES.md publishes two different "
            "whole-program totals for the same shipped R4 cell -- section 8e's "
            "31 997 489 and section 8f's 31 997 125, 0.0011 per cent apart, "
            "with kernel counts 760 and 762 -- because they come from two "
            "different controls/negatives.py runs. This file pins section 8e.",
        "r4_endpoint_degenerate": not beat,
        "r3_endpoint_degenerate": not beat3,
        "cheapest_r3_in_contract": (cheapest_in_contract(rows, "R3") or {}
                                    ).get("name"),
        "cheapest_r4_in_contract": (cheapest_in_contract(rows, "R4") or {}
                                    ).get("name"),
        "dearest_r3_in_contract": (dearest_in_contract(rows, "R3") or {}
                                   ).get("name"),
        "smaller_surface_in_contract": [
            {"name": r["name"], "trusted_items": r["trusted_items"],
             "pct_vs_own_side_a1": round(r["pct_vs_own_side_a1"], 6)}
            for r in small],
        # ⚠⚠ THE FIELD THAT SAYS WHICH FAMILY CAN RESOLVE THIS ROW, AND IT
        # MEASURES THE SPREAD RATHER THAN ASSUMING IT. On ph45 a1_spread_pp is
        # 0.000000 on both sides and the whole-program family is the only one
        # that can rank anything; here A1's spread is the larger of the two on
        # the R3 side. The default key of cheapest_in_contract is A1 BECAUSE of
        # this number, and a negative pins that.
        #
        # ⛔⛔ NO `in_contract` AND NO `english_verdict` FILTER, DELIBERATELY,
        # AND TASK_PHP_044 LEFT IT THAT WAY RATHER THAN BY OVERSIGHT. The
        # question this field answers is whether the STATISTIC can rank
        # respellings at all -- i.e. whether A1 is respelling-blind the way ph45
        # found it to be -- and that is a property of the statistic and the
        # search space, not of the contract. Filtering it would make it answer a
        # different question, would stop it comparing with ph45's copy (which
        # does not filter either), and would couple a measurement-resolution
        # diagnostic to a contract ruling so that restating an idiom entry moved
        # a number about instruction counts. ⚠ THE CONSEQUENCE, STATED SO IT IS
        # NOT READ AS A RESULT: item 83's ruling excludes the three CHEAPEST R4
        # variants, so the R4 figure here (45.313019) is over a population that
        # includes three out-of-contract cells and one never-verified one, and
        # the in-contract R4 spread is 33.917949 pp. TASK_PHP_043 section 1.9
        # quotes the latter. BOTH ARE TENS OF pp, so item 82's conclusion -- that
        # A1 is not respelling-blind on this row, against ph45's 0.000000 -- is
        # insensitive to the choice, which is why the choice is recorded rather
        # than defended as load-bearing.
        "a1_spread_pp": {
            side: (None if not vals else round(max(vals) - min(vals), 6))
            for side, vals in (
                (s, [r["pct_vs_r4ship_a1"] for r in rows.values()
                     if r.get("side") == s
                     and r.get("pct_vs_r4ship_a1") is not None])
                for s in RUNG_SIDES)},
        "wp_spread_pp": {
            side: (None if not vals else round(max(vals) - min(vals), 6))
            for side, vals in (
                (s, [r["pct_vs_r4ship_wp"] for r in rows.values()
                     if r.get("side") == s
                     and r.get("pct_vs_r4ship_wp") is not None])
                for s in RUNG_SIDES)},
        "kernel_digests_distinct": {
            side: len({r.get("kernel_fingerprint") for r in rows.values()
                       if r.get("side") == side and r.get("kernel_fingerprint")})
            for side in RUNG_SIDES},
        # ⭐ ph45 section 5.6's result on a SECOND row and in its sharper form:
        # there the &[u8; N] type was a TIE within a threshold, here it is
        # BYTE-IDENTICAL, so the claim needs no threshold at all.
        "oprec_array_byte_identical_to_slice":
            byte_identical_pair(rows, "r3_oprec_slice", "r3_oprec_array", "R3"),
        "witness_cost_pct_w1": {
            "shipped_bool_array": (None if wship is None
                                   else round(wship, 6)),
            "u32_bitmask": None if wbm is None else round(wbm, 6),
            "note":
                "Per cent whole-program Ir/call above controls/r4_nowitness.rs "
                "on inputs/small.bin at O3/isolated, both cells from THIS "
                "pipeline. NOTES.md section 8e publishes +21.775 per cent for "
                "the shipped witness and calls it the row's largest single "
                "number; the bitmask witness is the cheaper spelling section "
                "8e itself names and does not build. ⚠ MEASURED CORPUS ONLY: "
                "r4_nowitness is not equivalent to either on an uncovered "
                "blob, which is what the witness is for, so this is a cost "
                "comparison and not a ladder rung.",
        },
        "open_item_79_arms": mu_ref_arms,
        "toolchain": "rustc 1.97.1 / LLVM 22.1.6; Verus 0.2026.08.09.92f466f. "
                     "The two largest levers found are both LLVM decisions -- "
                     "how many bounds checks survive a sub-slice, and whether "
                     "the coverage witness lives in a register or on the stack "
                     "-- so every figure here is about this toolchain.",
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "build_error",
                          "verus_build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "⚠⚠ REPAIRED AT TASK_PHP_044 (open item 89) AND THE CLAUSE IT "
            "REPLACES WAS FALSE AS WRITTEN. It read \"Every variant is in "
            "contract by harness/check.py::spelling_matches over EVERY "
            "backticked idiom entry\", which is false on this file's own data: "
            "13 of 20 variants record a non-empty required_absent, INCLUDING "
            "R3's v0_shipped. What is true: every variant's `forbidden_hits` is "
            "empty by harness/check.py::spelling_matches, which is what "
            "`in_contract` MEANS here (the field is literally `not forb`, and "
            "it never consults required_absent); `required_absent` is reported "
            "BESIDE it and is judged against each entry's English, because "
            "`required` is presence-only and cannot fail the gate "
            "(check.py::idiom_audit, which measures the naive "
            "every-span-in-every-rung reading at 41 misses of 158 obligations, "
            "all 41 non-defects). Where a reading has been made it is recorded "
            "in `english_verdict` and NOT in `in_contract` -- `_admissible` "
            "requires both -- so the two halves stay distinguishable. ⭐ THE "
            "CLAUSE WAS BYTE-IDENTICAL IN ALL FIVE PHP ROWS' spellings.json and "
            "is repaired HERE ONLY, because each of the other four costs its own "
            "re-gate and batches with that row's next task; RECAP_PHP.md item 89 "
            "carries them. It entered with the php copy and was cloned four "
            "times, which is F101's law at a fifth generation. AND THE REST OF "
            "THE INVARIANT STANDS AS WRITTEN: every variant returns ITS OWN "
            "SIDE's shipped checksum on all seven inputs (this row's R3 and R4 diverge on "
            "adversarial-cmp.bin by declaration, so a cross-side reference "
            "would be this control's defect and not a variant's), and is priced "
            "in BOTH families by one callgrind run per cell. Every R4 variant "
            "additionally has its substitution applied to verus.rs and is put "
            "through Verus, and the ERROR TEXT is read: `is not supported` and "
            "`does not yet support` disqualify, a failed postcondition does "
            "not. An R4 variant with NO twin file is inadmissible BY RULE "
            "(r4_no_twin_reason), which ph45's copy leaves as a silent skip. "
            "Byte-identity between an R4 variant and its twin is RECORDED and "
            "is not a bar, because spec.md pins `identity: differ` at both "
            "levels and the gate record measures `differ` -- both are read at "
            "run time by identity_premise() rather than assumed. TWO "
            "quantities ship in each family, labelled: the fixed-R4 bound and "
            "the R3-side span. NO PAIR INTERVAL.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
