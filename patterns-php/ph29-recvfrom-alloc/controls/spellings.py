#!/usr/bin/env python3
"""ph29 control -- **THE IN-CONTRACT SPELLING SPAN, AND THE R4 SIDE IS NOT
DEGENERATE.**

    python3 patterns-php/ph29-recvfrom-alloc/controls/spellings.py --audit-only
    python3 patterns-php/ph29-recvfrom-alloc/controls/spellings.py --verus

⚠⚠⚠ **RUN IT WITH `--verus` OR ITS R4 COLUMN MEANS NOTHING.** `../spec.md` pins
`identity: unsafe == verus, O3 exact`, so an R4 respelling is a RUNG CANDIDATE
only if it has a Verus twin that (a) VERIFIES and (b) compiles to a
BYTE-IDENTICAL `kernel`. Without the flag this file refuses to certify and says
so in `problems` (`TASK_PHP_024` §1.6 demonstrated live on `ph07` what a sidecar
that looks complete and is not does to a later reader).

WHAT THIS ROW'S SEARCH FOUND, AND IT IS THE OPPOSITE OF `ph07`'s AND `ph16`'s
-----------------------------------------------------------------------------
`ph07` and `ph16` both searched their R4 side and found it **DEGENERATE** -- no
admissible R4 moved the number, so their `fixed-R4 bound` was a bound over a
SEARCHED endpoint. ⭐ **`ph29`'s is not.** `r4_fold_iter` -- R3's `for` over
`read_buf[0..recvd].iter()`, put into R4 -- verifies at the pinned Verus and the
pinned vstd with **no new trusted item**, and its `kernel` is byte-identical to
the unsafe variant's. So this row's headline `R3ship - R4ship` was measured
against an **UNSEARCHED** R4 endpoint, and that is a fact about the published
number rather than about Rust.

⚠⚠ **AND IT STILL DOES NOT RE-SHIP THE RUNG.** `.memory/02-bench-rules.md` holds
the shipped rung fixed by fiat -- chosen by IDIOM, before measurement -- and that
fiat is exactly what makes `R3ship - R4ship` a BOUND. What a cheaper in-contract
spelling moves is what the bound may be CALLED, not which program ships. Two
numbers ship, labelled:

    fixed-R4 bound   R3ship - R4ship      both endpoints held by fiat
    R3-side span     cheapest-found to dearest-found in contract, named

and **NO PAIR INTERVAL**: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts
that construction in terms and this file does not resurrect it.

⚠ **WHICH STATISTIC, AND IT IS NOT THE ONE `ph07`/`ph16` HEADLINE.** Two are
computed and both are printed:

  * **A1 -- `kernel_exclusive_ir / n_iters` on `small.bin`.** THE HEADLINE here.
    The decider is the null control: `identity` pins R4 and R5 byte-identical, so
    `verus - unsafe` has a known true value of **0**, and A1's null is `0.000 %`
    across every row of both programmes while the whole-program marginal's
    reaches `+3.65 %`. ⚠ A1 is the headline only where the two compared cells
    have comparable callee share, which R3-vs-R4 on this row does
    (`inside_share` 0.655 vs 0.669); it is NOT right for this row's C-vs-Rust
    column (0.927 vs 0.655) and that comparison is not made here.

    ⛔⛔ **THOSE FOUR NUMBERS SHIPPED NAKED AND `TASK_PHP_058` DRESSED THEM.**
    They were right -- all four reproduce to the digit -- but they named
    NEITHER the cell, NOR the compiler, NOR which of the two quantities called
    `inside_share` they are. **F108 asks for five things and this carried
    none of them.** In full:

        cell        `large.bin` / `O3` / `isolated`  (NOT `small.bin`, which
                    is the input the A1 headline above is quoted on -- so the
                    share and the headline it qualifies are different cells)
        definition  **F74's** share, `(kernel_exclusive_ir / n_iters) /
                    marginal_ir_per_call` -- NOT the `W` share this row's own
                    `controls/inside_share.py` computes. On `c-gcc`/`small.bin`
                    the two read 0.8045 and 0.8933; they are not interchangeable
        R3-vs-R4    `safe_tuned` 0.6551 vs `unsafe` 0.6690
        C-vs-Rust   `c-gcc` 0.9266 vs `safe_tuned` 0.6551.  ⚠ **`c-clang` is
                    0.9122** -- one compiler stood in for both, and F108's fifth
                    thing is WHICH COMPILER, with both columns

    ⭐ **THE DISCLAIMER IS RIGHT AND MUST NOT BE NARROWED.** `.memory-php/02-ladder.md`
    states F74's corrected two-condition bar -- (i) `min(inside_share)` HIGH and
    (ii) `|Δinside_share| <= 0.02` -- and this pair's Δ is **0.2715**, over
    thirteen times the bar. It fails on `c-clang` too (**0.2571**).

    ⛔⛔⛔ **AND `RECAP_PHP.md` PUBLISHES A COMPARISON THIS DISCLAIMER DOES NOT
    EVEN COVER.** Its *which statistic* cell reads *"on `ph29/large` A says C is
    +33 % dearer than naive safe Rust"* -- **`safe_naive`, one rung off the
    `safe_tuned` named here**. That pair's Δ is **0.2355**, and it fails the bar
    too. ⚠ **The `+33.01 %` itself reproduces exactly; what it lacks is the
    other C column -- `c-clang` reads `-4.36 %`, the OPPOSITE SIGN.**
  * **the two-point slope, `Ir` per window byte**, kept because `ph07` and
    `ph16` publish it and a reader comparing the three rows needs the same
    column. ⚠ **THE TWO DISAGREE ON THIS ROW AND NEITHER IS WRONG**:
    `r4_fold_iter` is about **-5.6 %** on A1 and about **-6.5 %** on the slope,
    because the two spellings differ in their FIXED per-call term as well as in
    their marginal. Quote one, name it, and do not average them.

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of. The candidate
set is not intuition -- it is `TASK_PHP_033` §4's per-instruction attribution of
`R4ship - R3ship`, which put **91 %** of the gap in the fold loop and nothing
anywhere else above 10 %.

R3 side, from `../safe_tuned.rs` -- all safe, no `unsafe` token:

  `v0_shipped`      the shipped R3, unmodified.
  `r3_fold_index`   ⭐ THE MIRROR. R4's index walk, spelled safely: `read_buf[i]`
                    in a `while` instead of a `for` over a subslice iterator.
                    This is R2's own fold. If the gap is the fold spelling, this
                    is where R3 loses it.
  `r3_fold_fold`    `.iter().fold(..)` instead of a `for` over `.iter()` -- the
                    same traversal written as a combinator. ⚠ NOT free, and that
                    is the surprise: two spellings a reader would call the same
                    thing are ~6 % apart, because the combinator does not get the
                    `for` loop's unroll factor.
  `r3_copy_loop`    R2's byte copy loop instead of `copy_from_slice`. ⚠ A
                    CALIBRATION LOSER, kept on purpose: a spelling search with no
                    losing entry is a search nobody can calibrate.
  `r3_head_shift`   R2's shift-loop header decode instead of `from_le_bytes`.
                    Prices the FIXED per-call term rather than the marginal.

R4 side, from `../unsafe.rs`, and **each one's substitution is applied to
`../verus.rs` as well and the result is put through Verus AND fingerprinted**:

  `v0_shipped`      the shipped R4, unmodified.
  `r4_fold_iter`    ⭐⭐ THE CANDIDATE THIS ROW TURNED ON. R3's `for` over
                    `read_buf[0..recvd].iter()`, put into R4. It replaces
                    `vget_unchecked`'s ONLY call site with a checked slice index,
                    so if it is admissible it is **cheaper AND one trusted call
                    site smaller**. ⚠ Written `0..recvd` and never `..recvd`: the
                    pinned vstd gives `SliceIndexSpecImpl` to `usize` and
                    `Range<usize>` and to NOTHING ELSE, so `RangeTo` fails with an
                    undischargeable `precondition not satisfied` -- and the two
                    spellings are byte-identical machine code, so the provable one
                    is free (`TASK_PHP_033` §5.1, re-derived by stage 4 below).
  `r4_fold_slice`   the index walk kept, but read through a `&[u8]` from
                    `as_slice()` with the EXISTING trusted `get_unchecked` instead
                    of `vget_unchecked` on the `Vec`. If free, it is a smaller
                    trusted surface at the same price -- `ph07`'s `r4_index0` /
                    `ph16`'s `r4_fold_index` shape.
  `r4_head_array`   R3's `from_le_bytes` header decode in R4. ⚠ EXPECTED
                    INADMISSIBLE and priced anyway: `../spec.md`'s own hashed
                    `why` records `from_le_bytes` as `is not supported` at the
                    pinned vstd, which is what forces a NEW TRUSTED ITEM. Stage 4
                    reproduces that error text rather than inheriting it.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**. A variant
    nobody audited is a number about a different benchmark.
    ⚠ A `forbidden` hit DISQUALIFIES; a `required` miss is REPORTED and does not.
    That is `check.py`'s own semantics and not a stricter invention: this row's
    `required[1]` pins `vset_unchecked(&mut read_buf, recvd, 0)`, which the two
    SAFE rungs cannot contain, so an audit that treated a `required` miss as
    disqualifying would refuse the shipped rungs themselves. The shipped gate
    record carries those two absences and calls the row `PASS`.
    ⚠ `admissible` is THREE-VALUED. The token audit decides what a grep can
    decide; the third value is a sentence, and for each variant it is in the
    `why` above.
  * every variant prints the SHIPPED checksum on every one of the six inputs,
    adversarial included. A respelling that changed the answer is not one. ⚠ The
    reference is **R3 `v0_shipped`** and not each side's own shipped rung,
    because this row pins all four Rust rungs to one checksum per input.
  * ⚠⚠ **`Ir` is measured the way `harness/measure.py` MEASURES THE SHIPPED
    CELLS** -- `kernel_exclusive_ir` off the pinned callgrind on the SHIPPED
    inputs at their own `n_iters` -- with `measure.py::_sum_rows` **IMPORTED and
    never transcribed** (`TASK_PHP_022` §3.2 measured that the transcription was
    a different function, and produced a PLAUSIBLE WRONG NUMBER rather than an
    error, on two synthetic shapes).
  * stage 3 reproduces the SHIPPED cells' recorded numbers before any variant is
    quoted, and prints the delta against
    `results-php/ph29-recvfrom-alloc.json`.
  * ⚠⚠ stage 4 checks BOTH HALVES of `identity`. `ph07`'s and `ph16`'s controls
    check only that the twin verifies; `../spec.md` says `O3 exact`, so a twin
    that verifies and compiles to a DIFFERENT kernel is not a rung either, and
    that half was unchecked until this file. It has never yet fired -- all three
    admissible twins here come back byte-identical -- and a check that has never
    fired is worth exactly what its negatives are worth, which is why
    `.temp/php35/negatives_spellings.py` mutates a twin to make it fire.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**

⚠ `kernel_fingerprint` HERE IS GUARDED AND `ph16`'s IS NOT. `ph16`'s -- and the
copy in `.temp/php33/probe_b.py` -- ignores objdump's return code, so a binary
that does not exist disassembles to nothing and fingerprints as
`(0, 'd41d8cd98f00')`, the md5 of the empty string. **Two such compare
IDENTICAL**, which is the exact false-equality this file's stage 4 exists to
rule out. Found by this file's own must-fire negative N1
(`.temp/php35/negatives_spellings.py`), not by inspection. It is guarded here
and `ph16` is NOT edited -- its own call sites are all downstream of a build
that is checked -- but a later row that clones the unguarded copy inherits the
hole, so it is written down.
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
SCRATCH = os.path.join(REPO, ".temp", "php35", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph29-recvfrom-alloc.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph29-recvfrom-alloc.json`
#: carries and therefore what `../NOTES.md` §8 quotes.
PROBES = (("small.bin", 550, 25_000), ("large.bin", 4076, 12_000))
#: Below this, two cells are a TIE and neither is "cheaper".
TIE_PCT = 0.05
#: Only these two sides can move a published rung number; anything else is a
#: control by construction.
RUNG_SIDES = ("R3", "R4")


# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]})
# `file` is "rs" for the rung source and "verus" for the R5 twin.

_R4_FOLD_INDEX = """        let mut i: usize = 0;
        while i < recvd {
            h = h.wrapping_mul(31).wrapping_add(vget_unchecked(&read_buf, i) as u64);
            i = i + 1;
        }
"""
_R4_FOLD_ITER = """        for v in read_buf[0..recvd].iter() {
            h = h.wrapping_mul(31).wrapping_add(*v as u64);
        }
"""
_R4_FOLD_SLICE = """        let rb: &[u8] = read_buf.as_slice();
        let mut i: usize = 0;
        while i < recvd {
            h = h.wrapping_mul(31).wrapping_add(get_unchecked(rb, i) as u64);
            i = i + 1;
        }
"""
_HEAD_SHIPPED_U = """    let tr: u64 = (get_unchecked(win, 0) as u64) | ((get_unchecked(win, 1) as u64) << 8)
        | ((get_unchecked(win, 2) as u64) << 16) | ((get_unchecked(win, 3) as u64) << 24)
        | ((get_unchecked(win, 4) as u64) << 32) | ((get_unchecked(win, 5) as u64) << 40)
        | ((get_unchecked(win, 6) as u64) << 48) | ((get_unchecked(win, 7) as u64) << 56);
"""
_HEAD_ARRAY_U = """    let mut head8: [u8; 8] = [0u8; 8];
    head8.copy_from_slice(&win[0..8]);
    let tr: u64 = u64::from_le_bytes(head8);
"""

# ---- the R5 twins, and these are the whole question the row turned on ---------
# `../verus.rs`'s shipped fold loop, and the two replacements that VERIFY.
# ⚠ Both were closed at TASK_PHP_035 and neither costs a trusted item; the
# obstacle that had stopped the first attempt is recorded on `_V_FOLD_ITER`.

_V_FOLD_SHIP = """        let ghost target = foldb(read_buf@, 0, 0, recvd as int, 0u64);
        let mut i: usize = 0;
        while i < recvd
            invariant
                i <= recvd,
                recvd <= read_buf@.len(),
                foldb(read_buf@, 0, i as int, recvd as int, h) == target,
            decreases recvd - i,
        {
            h = h.wrapping_mul(31).wrapping_add(vget_unchecked(&read_buf, i) as u64);
            i = i + 1;
        }
"""
# ⚠⚠ TWO FACTS MAKE THIS VERIFY AND BOTH WERE MEASURED RATHER THAN GUESSED
# (`.temp/php35/v/diag2.rs`, one question per function so that a failed
# `assert` -- which Verus then ASSUMES -- cannot answer the next one):
#   * Verus's for-loop runs under LOOP ISOLATION, so the enclosing `requires`
#     and every fact proved above the loop are NOT available inside it. That is
#     why `recvd <= read_buf@.len()` is an INVARIANT and not an inherited fact,
#     and why the first attempt failed on a subrange length it had already
#     established four lines higher.
#   * inside the body `it.index()` is the **PRE-`next`** value, so the free fact
#     is `*x == sub[it.index()]`. `sub[it.index() - 1]` -- the post-`next`
#     reading, and the one the first attempt asserted -- FAILS.
#     `VerusForLoopWrapper::next`'s `ensures` in
#     `~/tools/verus/vstd/std_specs/iter.rs` is where that is written down.
# The invariant is the REMAINING form, `foldb(.., index, n, h) == target`, and
# not the prefix form, because the remaining form steps straight off `foldb`'s
# own recursion and needs no extend-at-the-end lemma. It is the same shape the
# shipped index-walk loop above already uses, which is why the twin adds no
# lemma and no trusted item.
_V_FOLD_ITER = """        let ghost target = foldb(read_buf@, 0, 0, recvd as int, 0u64);
        for x in it: read_buf[0..recvd].iter()
            invariant
                it.seq().unref() =~= read_buf@.subrange(0, recvd as int),
                recvd <= read_buf@.len(),
                foldb(read_buf@, 0, it.index(), recvd as int, h) == target,
        {
            let ghost i0 = it.index();
            assert(0 <= i0 < recvd);
            assert(*x == read_buf@.subrange(0, recvd as int)[i0]);
            assert(read_buf@.subrange(0, recvd as int)[i0] == read_buf@[i0]);
            h = h.wrapping_mul(31).wrapping_add(*x as u64);
        }
"""
_V_FOLD_SLICE = """        let ghost target = foldb(read_buf@, 0, 0, recvd as int, 0u64);
        let rb: &[u8] = read_buf.as_slice();
        let mut i: usize = 0;
        while i < recvd
            invariant
                i <= recvd,
                rb@ =~= read_buf@,
                recvd <= rb@.len(),
                foldb(read_buf@, 0, i as int, recvd as int, h) == target,
            decreases recvd - i,
        {
            h = h.wrapping_mul(31).wrapping_add(get_unchecked(rb, i) as u64);
            i = i + 1;
        }
"""

_R3_FOLD_ITER = """        for v in read_buf[..recvd as usize].iter() {
            h = h.wrapping_mul(31).wrapping_add(*v as u64);
        }
"""
_R3_FOLD_INDEX = """        let mut i: usize = 0;
        while i < recvd as usize {
            h = h.wrapping_mul(31).wrapping_add(read_buf[i] as u64);
            i += 1;
        }
"""
_R3_FOLD_FOLD = """        h = read_buf[..recvd as usize].iter()
            .fold(0u64, |a, v| a.wrapping_mul(31).wrapping_add(*v as u64));
"""
_R3_COPY_SHIPPED = \
    "        read_buf[..n].copy_from_slice(&win[HEAD..HEAD + n]);\n"
_R3_COPY_LOOP = """        let mut ci: usize = 0;
        while ci < n {
            read_buf[ci] = win[HEAD + ci];
            ci += 1;
        }
"""
_R3_HEAD_SHIPPED = """    let mut head8: [u8; 8] = [0u8; 8];
    head8.copy_from_slice(&win[0..8]);
    let to_read: i64 = i64::from_le_bytes(head8);
"""
_R3_HEAD_SHIFT = """    let mut trh: u64 = 0;
    let mut bh: usize = 0;
    while bh < 8 {
        trh |= (win[bh] as u64) << (8 * bh);
        bh += 1;
    }
    let to_read: i64 = trh as i64;
"""

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}),
    ("r3_fold_index", "R3",
     "⭐ THE MIRROR CONTROL. R4's INDEX-WALK fold, spelled safely: `read_buf[i]` "
     "in a `while` instead of a `for` over a subslice iterator. This is R2's own "
     "fold. If the R3/R4 gap is the fold spelling, this is where R3 loses it",
     {"rs": [(_R3_FOLD_ITER, _R3_FOLD_INDEX, 1)]}),
    ("r3_fold_fold", "R3",
     "`.iter().fold(..)` instead of a `for` over `.iter()` -- the same traversal "
     "written as a combinator. ⚠ NOT free: two spellings a reader would call the "
     "same thing are ~6 % apart",
     {"rs": [(_R3_FOLD_ITER, _R3_FOLD_FOLD, 1)]}),
    ("r3_copy_loop", "R3",
     "R2's byte copy loop instead of `copy_from_slice`. A calibration LOSER: a "
     "search with no losing entry is one nobody can calibrate",
     {"rs": [(_R3_COPY_SHIPPED, _R3_COPY_LOOP, 1)]}),
    ("r3_head_shift", "R3",
     "R2's shift-loop header decode instead of `from_le_bytes`. Prices the FIXED "
     "per-call term rather than the marginal",
     {"rs": [(_R3_HEAD_SHIPPED, _R3_HEAD_SHIFT, 1)]}),
]

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}),
    ("r4_fold_iter", "R4",
     "⭐⭐ R3's `for` over `read_buf[0..recvd].iter()`, put into R4. It replaces "
     "`vget_unchecked`'s ONLY call site with a checked slice index, so it is "
     "cheaper AND one trusted call site smaller. Written `0..recvd` because "
     "`RangeTo` has no spec at the pinned vstd and the two spellings are "
     "byte-identical machine code",
     {"rs": [(_R4_FOLD_INDEX, _R4_FOLD_ITER, 1)],
      "verus": [(_V_FOLD_SHIP, _V_FOLD_ITER, 1)]}),
    ("r4_fold_slice", "R4",
     "the index walk kept, but read through a `&[u8]` from `as_slice()` with the "
     "EXISTING trusted `get_unchecked` instead of `vget_unchecked` on the `Vec`. "
     "If free, it is a smaller trusted surface at the same price",
     {"rs": [(_R4_FOLD_INDEX, _R4_FOLD_SLICE, 1)],
      "verus": [(_V_FOLD_SHIP, _V_FOLD_SLICE, 1)]}),
    ("r4_head_array", "R4",
     "R3's `from_le_bytes` header decode in R4, replacing eight `get_unchecked` + "
     "shift + or. ⚠ EXPECTED INADMISSIBLE and priced anyway: `../spec.md`'s own "
     "hashed `why` records `from_le_bytes` as `is not supported` at the pinned "
     "vstd, which is what forces a NEW TRUSTED ITEM",
     {"rs": [(_HEAD_SHIPPED_U, _HEAD_ARRAY_U, 1)],
      "verus": [(_HEAD_SHIPPED_U, _HEAD_ARRAY_U, 1)]}),
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
    substitution list is explicit and does NOT fall back to the exec one --
    `../verus.rs`'s fold loop carries invariants and a `decreases`, so the exec
    anchor does not occur in it and a silent fallback would raise inside a
    `try` somebody later widens."""
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


def kernel_ir(exe, path, tag):
    """`(kernel_exclusive_ir, error_or_None)` off the pinned callgrind, with
    `harness/measure.py::_sum_rows` IMPORTED -- see `load_measure`.

    ⚠ Callgrind's RETURN CODE is checked: probe rule 1, a probe that CANNOT
    EVALUATE must say so rather than return a figure-shaped `None`."""
    M = load_measure()
    out = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        "--callgrind-out-file=" + out, exe, path],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        if os.path.exists(out):
            os.unlink(out)
        return None, (f"callgrind exit {r.returncode} on {tag}: "
                      f"{r.stderr[-200:]}")
    ann = subprocess.run([M.CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=600)
    tot, _names = M._sum_rows((ann.stdout + ann.stderr).strip(), "kernel")
    if os.path.exists(out):
        os.unlink(out)
    if tot is None:
        return None, (f"callgrind_annotate named no `kernel` function for "
                      f"{tag} (rc {ann.returncode})")
    return tot, None


_XFER = re.compile(r"^(j[a-z]+|call|loop[a-z]*)\s+([0-9a-f]+)$")
#: The `kernel` needle, and it is NOT a bare substring.
#:
#: ⚠⚠ `ph16`'s copy -- and `.temp/php33/probe_b.py`'s -- tests `"kernel" in
#: name` on the whole mangled symbol. That folds **every** symbol whose name
#: merely contains the letters into the digest: a sibling `kernel_prologue`, a
#: twin `slb_twin_kernel`, or -- measured, by this file's own negative D2 -- a
#: binary built from a crate called `nokernel`, whose `main` is
#: `_RNvCs..._8nokernel4main` and which therefore fingerprinted as though it had
#: a kernel. `harness/measure.py::_sum_rows` does NOT have this hole: it matches
#: `(?:^|::)kernel(?:$|[^A-Za-z0-9_])` on the function field, and
#: `TASK_PHP_022` §3.2 measured what the looser reading costs on the Ir side
#: (9,100,000 where the truth is 900,000). This is the same discipline on the
#: fingerprint side. The leading class admits a digit because Rust's v0 mangling
#: length-prefixes the component -- the real symbol ends `...6kernel` -- and
#: excludes letters and `_` so that `nokernel` and `slb_twin_kernel` do not
#: match.
_KERNEL_SYM = re.compile(r"(?:^|[^A-Za-z_])kernel(?:$|[^A-Za-z0-9_])")


def disasm(exe):
    """`{address: text}` for the `kernel` function only.

    ⚠ `harness/asm.py` is *the* objdump caller in `harness/`, and this is not an
    edit to it: six PAT patterns' `controls/` disassemble directly for exactly
    this reason (`CLAUDE.md` -- *the GATE has one pipeline, not the tree*). What
    is needed here is per-instruction text keyed by address, which `asm.py` does
    not return.

    ⚠⚠ **TWO THINGS HERE ARE NOT IN `ph16`'s COPY, AND BOTH WERE FOUND BY THIS
    FILE'S OWN MUST-FIRE NEGATIVES RATHER THAN BY READING IT.**

      * objdump's RETURN CODE is checked. Without it a binary that does not
        exist disassembles to nothing and `kernel_fingerprint` returns
        `(0, md5(""))` -- a figure-shaped value, and two of them compare EQUAL.
        On a function whose whole job is to say *byte-identical*, the failure
        mode is a FALSE POSITIVE.
      * the needle is `_KERNEL_SYM` and not `"kernel" in name`. See its
        docstring; negative D2 built a crate called `nokernel` and the loose
        reading fingerprinted its `main`."""
    r = subprocess.run(["objdump", "-d", "--no-show-raw-insn", exe],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"objdump failed on {exe} (rc {r.returncode}): "
                           f"{r.stderr.strip()[:200]}")
    out, on = {}, False
    for line in r.stdout.splitlines():
        m = re.match(r"^[0-9a-f]+ <(.*)>:$", line)
        if m:
            on = bool(_KERNEL_SYM.search(m.group(1)))
            continue
        if not on:
            continue
        m = re.match(r"\s+([0-9a-f]+):\s+(.*)", line)
        if m:
            out[int(m.group(1), 16)] = m.group(2).strip()
    return out


def kernel_fingerprint(exe):
    """`(n_instructions, 12-hex digest)` of `kernel`'s text, normalised so that
    it is a claim about CODE and not about LAYOUT.

    ⚠⚠ TRANSCRIBED from `patterns-php/ph16-fdset-index/controls/spellings.py`
    -- which is a statistic-shaped transcription and therefore flagged -- but it
    is not a STATISTIC: it is a normalisation whose only consumer is the equality
    test below, and stage 4 checks it against a pair whose answer is known
    (`R4 v0_shipped` vs `R5 v0_shipped`, which `../spec.md`'s `identity` pins
    EQUAL and the shipped record measures equal). `ph16` records the four repairs
    that made it layout-insensitive; this copy keeps all four and adds the
    empty-disassembly guard in `disasm`.

    Three rules, and each removes a layout term while keeping a code term:
      * everything from the first `<` goes -- the crate hash;
      * everything from `#` goes -- objdump's RESOLVED rip-relative address. The
        DISPLACEMENT stays, and it is the code;
      * a control-transfer target becomes a SIGNED OFFSET from the instruction's
        own address, so the control-flow shape survives and its placement does
        not.
    Registers and immediates are KEPT, so a register-allocation change is still a
    difference: an opcode-only digest would call `r4_head_array` equal to the
    shipped R4, and it is not.

    ⚠ It raises on an empty disassembly. A `kernel` that disassembles to nothing
    is a measurement that did not happen, and `(0, md5(""))` is the same value
    for every such binary."""
    txt = disasm(exe)
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


_VR = re.compile(r"verification results:: (\d+) verified, (\d+) errors")


def verus_ok(vp):
    """`(ok, message)` for one twin.

    ⚠⚠ **READ THE ERROR TEXT, NOT THE EXIT CODE** -- `../spec.md`'s own hashed
    rule. `is not supported` DISQUALIFIES, because it is what forces a new
    TRUSTED item; `postcondition not satisfied` and `invariant not satisfied`
    disqualify NOTHING and are proof work (`p05` went `11 verified, 1 errors` ->
    `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB).
    Both are reported distinctly, because a row that conflates them refuses
    candidates for the wrong reason -- and on THIS row that distinction is the
    whole result: the first five attempts at `r4_fold_iter` all failed, none of
    them with `is not supported`, and the sixth verified."""
    r = subprocess.run([sys.executable, VERUS_RUN, vp],
                       capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    if "is not supported" in txt:
        line = next((ln for ln in txt.splitlines()
                     if "is not supported" in ln), "")
        return False, "DISQUALIFIED -- is not supported: " + line.strip()[:200]
    m = _VR.search(txt)
    if not m:
        return False, txt.strip()[-400:]
    return m.group(2) == "0", m.group(0)


def audit(chk, decl, src, lang="rust"):
    """Every backticked spelling in `../spec.md`'s `idiom`, against one variant,
    with `harness/check.py`'s OWN semantics rather than a stricter invention:

      * a `forbidden` hit DISQUALIFIES -- `check.py`'s stage 0 has hard-failed on
        one since TASK_068, and its scope is universal by the key's own meaning,
        so it is decidable with no English involved;
      * a `required` miss is REPORTED and does not, because which rungs a
        `required` entry scopes to lives in the entry's ENGLISH and no gate stage
        reproduces it.

    ⚠ Getting this backwards is not a conservative error. This row's
    `required[1]` pins `vset_unchecked(&mut read_buf, recvd, 0)` on the Rust side
    and the two SAFE rungs cannot contain it -- the shipped gate record carries
    those two absences and calls the row `PASS` -- so an audit that treated a
    `required` miss as disqualifying would refuse the shipped rungs themselves."""
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
# three functions ARE this file's verdict, so they are functions and not lines
# inside `main`, and `.temp/php35/negatives_spellings.py` drives them over
# synthetic `rows` dicts -- an out-of-contract cheaper candidate, an unpriced
# one, a sub-`TIE_PCT` margin, a twin that verifies but is NOT byte-identical --
# none of which is reachable through the CLI.

#: The `problems` entry a run WITHOUT `--verus` carries. A module constant and
#: not a literal inside `main`, so `.temp/php35/negatives_spellings.py` can hand
#: it to `harness/check.py::control_json_verdict` and prove that the GATE would
#: refuse such a sidecar -- which is the claim, and it is not the same claim as
#: "this script appends a string".
NO_VERUS_PROBLEM = (
    "R4 ADMISSIBILITY WAS NOT CHECKED (no --verus), so every R4 variant's "
    "`in_contract` above is unverified: `../spec.md` pins `identity: unsafe == "
    "verus, O3 exact`, and without a twin that verifies AND is byte-identical "
    "an R4 candidate is a control and not a rung. Regenerate with `--verus`, "
    "which is what `pin.regenerate` names.")


def twin_identical(r):
    """The `O3 exact` half of `identity`, over one variant's row.

    ⚠ It compares BOTH the digest and the instruction count, and it is FALSE
    when either is missing. A missing field must not read as agreement: the
    digest of an empty disassembly is a constant, so `None == None` and
    `'d41d8cd98f00' == 'd41d8cd98f00'` are the two ways this check can say
    *byte-identical* about two things that were never compared. `disasm` raises
    on the second; this function refuses the first."""
    a, b = r.get("kernel_fingerprint"), r.get("verus_kernel_fingerprint")
    na, nb = r.get("kernel_insns"), r.get("verus_kernel_insns")
    if a is None or b is None or na is None or nb is None:
        return False
    return a == b and na == nb


def cheapest_in_contract(rows, side="R3", key="ir_per_call_small"):
    """The cheapest IN-CONTRACT, PRICED candidate on one side, or `None`.

    Three exclusions and each one is a defect this would otherwise publish: a
    variant that is out of contract, one that was never priced, and a side that
    is not a rung side."""
    if side not in RUNG_SIDES:
        return None
    c = [r for r in rows.values()
         if r.get("side") == side and r.get("in_contract")
         and r.get(key) is not None]
    return min(c, key=lambda r: r[key]) if c else None


def dearest_in_contract(rows, side="R3", key="ir_per_call_small"):
    """The other end of the R3-SIDE SPAN, which is the second of the two
    quantities that may be published."""
    if side not in RUNG_SIDES:
        return None
    c = [r for r in rows.values()
         if r.get("side") == side and r.get("in_contract")
         and r.get(key) is not None]
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
                    help="stage 4: put every R4 variant through Verus AND "
                         "check `identity: unsafe == verus, O3 exact`")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    chk = load_check()
    decl = contract()["idiom"]
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("spellings.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    variants = R3_VARIANTS + R4_VARIANTS
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
        print(f"  {side} {name:16s} "
              + ("IN CONTRACT" if not forb else "OUT: " + "; ".join(forb))
              + "   required absent: "
              + (", ".join(m.split("`")[1] for m in miss) or "none"))
    if args.audit_only:
        return 0

    print("\n1. BUILD + CHECKSUM + KERNEL FINGERPRINT -- a respelling that "
          "changes the answer is not one.\n   ⚠ EVERY variant is compared "
          "against R3 v0_shipped: this row pins all four\n   Rust rungs to one "
          "checksum per input and the gate asserts it.")
    ref = None
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"], os.path.join(SCRATCH, f"{side}_{name}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side} {name:16s} BUILD FAILED")
            problems.append(f"{side} {name} does not build: {err}")
            continue
        r["exe"] = exe
        r["kernel_insns"], r["kernel_fingerprint"] = kernel_fingerprint(exe)
        ans = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = ans
        if (side, name) == ("R3", "v0_shipped"):
            ref = ans
            print(f"  {side} {name:16s} REFERENCE  "
                  + " ".join(f"{k.split('.')[0][:14]}={v[:8]}"
                             for k, v in list(ans.items())[:3]) + " ..."
                  + f"   kernel {r['kernel_insns']:3d} "
                    f"{r['kernel_fingerprint']}")
            continue
        diff = [k for k, v in ans.items() if ref.get(k) != v]
        print(f"  {side} {name:16s} "
              + ("ok  identical on all "
                 f"{len(ans)} inputs" if not diff
                 else f"*** DIFFERS on {diff}")
              + f"   kernel {r['kernel_insns']:3d} {r['kernel_fingerprint']}")
        if diff:
            problems.append(f"{side} {name} changes the answer on {diff} "
                            f"-- it is not a respelling of this kernel")
            r["in_contract"] = False

    print("\n2. THE PRICE -- kernel-exclusive Ir on the SHIPPED inputs at their "
          "own n_iters,\n   harness/measure.py's own statistic. ⚠ TWO columns "
          "and they DISAGREE on this row:\n   A1 (per call, small.bin) is the "
          "headline; the slope is kept for ph07/ph16 comparability.")
    sm_st, lg_st = PROBES[0][1], PROBES[1][1]
    print(f"  {'cell':26s} {'Ir/call small':>14s} {'Ir/call large':>14s} "
          f"{'Ir/win-byte':>12s} {'fixed/call':>11s}")
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if not r.get("exe"):
            continue
        per = {}
        for inp, _stride, nit in PROBES:
            tot, err = kernel_ir(r["exe"], os.path.join(PDIR, "inputs", inp),
                                 f"{side}.{name}.{inp}")
            if err:
                problems.append(f"{side} {name} {inp}: {err}")
            per[inp] = None if tot is None else tot / float(nit)
        r["ir_per_call_small"] = per[PROBES[0][0]]
        r["ir_per_call_large"] = per[PROBES[1][0]]
        if r["ir_per_call_small"] is None or r["ir_per_call_large"] is None:
            problems.append(f"{side} {name}: callgrind gave no kernel figure")
            continue
        slope = ((r["ir_per_call_large"] - r["ir_per_call_small"])
                 / float(lg_st - sm_st))
        r["ir_per_window_byte"] = slope
        r["fixed_per_call"] = r["ir_per_call_small"] - slope * sm_st
        print(f"  {side + ' ' + name:26s} {r['ir_per_call_small']:14.1f} "
              f"{r['ir_per_call_large']:14.1f} {r['ir_per_window_byte']:12.4f} "
              f"{r['fixed_per_call']:11.1f}")
    b4a = rows[("R4", "v0_shipped")].get("ir_per_call_small")
    b4s = rows[("R4", "v0_shipped")].get("ir_per_window_byte")
    print(f"\n  {'cell':26s} {'A1 vs R4ship':>14s} {'slope vs R4ship':>16s}")
    for name, side, why, subs in variants:
        r = rows[(side, name)]
        if r.get("ir_per_call_small") is None:
            continue
        r["pct_vs_r4ship_a1"] = (100.0 * (r["ir_per_call_small"] - b4a) / b4a
                                 if b4a else None)
        r["pct_vs_r4ship_slope"] = (
            100.0 * (r["ir_per_window_byte"] - b4s) / b4s if b4s else None)
        print(f"  {side + ' ' + name:26s} {r['pct_vs_r4ship_a1']:+13.2f}% "
              f"{r['pct_vs_r4ship_slope']:+15.2f}%")

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
        for cell, side in (("safe_tuned", "R3"), ("unsafe", "R4")):
            for inp, key in (("small.bin", "ir_per_call_small"),
                             ("large.bin", "ir_per_call_large")):
                w = want.get((cell, inp))
                g = rows[(side, "v0_shipped")].get(key)
                if w is None or g is None:
                    print(f"  {cell:12s} {inp:10s} record={w} here={g}  "
                          f"(not comparable)")
                    continue
                d = abs(w - g) / w * 100.0
                print(f"  {cell:12s} {inp:10s} record={w:10.4f} "
                      f"here={g:10.4f}  delta={d:.4f}%")
                if d > 0.5:
                    rec_ok = False
                    problems.append(
                        f"{cell}/{inp}: this pipeline measures {g:.4f} where "
                        f"the shipped record says {w:.4f} ({d:.2f}% apart) -- "
                        f"the variants above are then about a different "
                        f"benchmark from the row")
    else:
        print(f"  no measurement record at {RECORD}")

    if args.verus:
        print("\n4. R4 ADMISSIBILITY -- ../spec.md pins `identity: unsafe == "
              "verus, O3 exact`,\n   so an R4 candidate needs a twin that "
              "VERIFIES *and* compiles to the SAME kernel.")
        for name, side, why, subs in R4_VARIANTS:
            r = rows[(side, name)]
            if not r.get("verus_rs"):
                continue
            ok, msg = verus_ok(r["verus_rs"])
            r["verus_verifies"], r["verus_msg"] = ok, msg
            r["identity_exact"] = None
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
            if not (ok and r["identity_exact"]):
                r["in_contract"] = False
            state = ("VERIFIES + IDENTICAL" if ok and r["identity_exact"]
                     else "VERIFIES but NOT byte-identical" if ok
                     else "DOES NOT VERIFY")
            print(f"  R4 {name:16s} {state:30s} "
                  f"{msg.splitlines()[0][:70] if msg else ''}"
                  + (f"   twin kernel {r.get('verus_kernel_insns')} "
                     f"{r.get('verus_kernel_fingerprint')}"
                     if r.get("verus_kernel_fingerprint") else ""))
            if name == "v0_shipped" and not (ok and r["identity_exact"]):
                problems.append(
                    "R4 v0_shipped's twin does not verify byte-identically -- "
                    "this pipeline is not measuring the shipped rung, and "
                    "`../spec.md`'s `identity` says it must")
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

    # ---- the two published numbers ------------------------------------------
    print("\n5. THE TWO NUMBERS THAT MAY BE QUOTED, LABELLED. "
          "STATISTIC: A1, per call on small.bin.")
    r3s, r4s = rows[("R3", "v0_shipped")], rows[("R4", "v0_shipped")]
    print(f"  fixed-R4 bound   R3ship - R4ship   "
          f"{r3s.get('pct_vs_r4ship_a1', float('nan')):+.2f}%   "
          f"({r3s.get('ir_per_call_small', 0):.1f} vs "
          f"{r4s.get('ir_per_call_small', 0):.1f} Ir/call, small.bin)")
    lo = cheapest_in_contract(rows, "R3")
    hi = dearest_in_contract(rows, "R3")
    if lo is not None and hi is not None:
        print(f"  R3-side span     cheapest-found .. dearest-found in contract  "
              f"{lo['pct_vs_r4ship_a1']:+.2f}% .. {hi['pct_vs_r4ship_a1']:+.2f}%"
              f"   `{lo['name']}` .. `{hi['name']}`, small.bin")
    print("  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it).")

    beat = cheaper_than_shipped(rows, "R4")
    r4c = [r for (s, _n), r in rows.items()
           if s == "R4" and r.get("in_contract")
           and r.get("ir_per_call_small") is not None]
    print(f"\n  ⚠ R4 SIDE, SEARCHED ({len(r4c)} admissible of "
          f"{len(R4_VARIANTS)} tried):")
    for r in sorted(r4c, key=lambda r: r["ir_per_call_small"]):
        d = r["pct_vs_r4ship_a1"]
        verdict = ("SHIPPED" if r["name"] == "v0_shipped"
                   else (f"TIE (< {TIE_PCT}%)" if abs(d) <= TIE_PCT
                         else ("CHEAPER" if d < 0 else "dearer")))
        print(f"      {r['name']:16s} {r['ir_per_call_small']:10.1f} Ir/call  "
              f"{d:+.2f}%   {verdict}")
    for (s, nm), r in sorted(rows.items()):
        if s == "R4" and not r.get("in_contract"):
            print(f"      {nm:16s} INADMISSIBLE -- "
                  + (r.get("verus_msg") or "see stage 0/1")[:96])
    if not beat:
        print("  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              "DEGENERATE on this row.")
    else:
        print(f"  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS -- `{beat[0]['name']}`, "
              f"{beat[0]['pct_vs_r4ship_a1']:+.2f}% on A1. THE R4 SIDE OF THIS "
              f"ROW\n     WAS UNSEARCHED, and the headline `fixed-R4 bound` "
              f"above is a bound over an\n     UNSEARCHED endpoint. ⚠ The rung "
              f"does NOT move: `.memory/02-bench-rules.md` holds\n     R4 fixed "
              f"by fiat and that fiat is what makes the bound a bound. What "
              f"moves is\n     what the number may be CALLED.")
        for r in beat:
            if r["name"] == "r4_fold_iter":
                print("     ⭐ AND IT IS NOT MERELY CHEAPER: `r4_fold_iter` "
                      "replaces `vget_unchecked`'s ONLY\n        call site with "
                      "a checked slice index, so it is cheaper AND one trusted "
                      "call\n        site smaller. That is a STRONGER claim than "
                      "the price and it is stated separately.")

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph29-recvfrom-alloc/controls/"
                "spellings.py --verus",
            "note":
                "The pin covers the two rung sources the variants are derived "
                "from, verus.rs (the R4 admissibility half -- BOTH halves of it: "
                "the twin must verify AND compile to the same kernel), spec.md "
                "(the declaration the audit runs against), inputs/gen.py (the "
                "corpus every number is measured over) and this script. It does "
                "NOT cover results-php/ph29-recvfrom-alloc.json: stage 3 "
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
                        "inputs/gen.py", "controls/spellings.py")},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        "verus_checked": bool(args.verus),
        "identity_checked": "verifies AND byte-identical kernel at O3/isolated",
        "statistic": "A1 = kernel_exclusive_ir / n_iters on the SHIPPED inputs "
                     "-- harness/measure.py::_sum_rows itself, IMPORTED and not "
                     "transcribed -- so stage 3 compares against "
                     "results-php/ph29-recvfrom-alloc.json directly. The "
                     "two-point slope (Ir per window byte) is also recorded, "
                     "because ph07 and ph16 publish it; the two DISAGREE on this "
                     "row by about one point and neither is wrong.",
        "headline_statistic": "ir_per_call_small",
        "reproduces_shipped_record": rec_ok,
        "r4_endpoint_degenerate": not beat,
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "build_error",
                          "verus_build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "Every variant is in contract by harness/check.py::spelling_matches "
            "over EVERY backticked idiom entry, returns the shipped checksum on "
            "all six inputs, and is priced by harness/measure.py's own statistic "
            "on both shipped inputs. Every R4 variant additionally has its "
            "substitution applied to verus.rs, is put through Verus, and has its "
            "twin's kernel fingerprinted against the exec variant's -- spec.md "
            "pins `identity: unsafe == verus, O3 exact` and BOTH halves are "
            "checked. TWO numbers ship, labelled: the fixed-R4 bound and the "
            "R3-side span. NO PAIR INTERVAL.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
