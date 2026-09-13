#!/usr/bin/env python3
"""ph52 control -- **THE IN-CONTRACT SPELLING SPAN, BOTH ENDPOINTS.**

    python3 patterns-php/ph52-concat-copy-uninit/controls/spellings.py --audit-only
    python3 patterns-php/ph52-concat-copy-uninit/controls/spellings.py --verus

⚠⚠⚠ **RUN IT WITH `--verus` OR ITS R4 COLUMN MEANS NOTHING.** An R4 respelling is
a RUNG CANDIDATE only if it has a Verus twin that VERIFIES. Without the flag this
file refuses to certify and says so in `problems` (`TASK_PHP_024` §1.6
demonstrated live on `ph07` what a sidecar that looks complete and is not does to
a later reader).

WHAT THIS ROW'S SEARCH FOUND -- the two answers
-----------------------------------------------
⚠ Figures: **A1, `inputs/small.bin`, `O3`/`isolated`**, against the named base.

  * ⭐⭐⭐ **R3 MOVES -7.42 %, AND THE SHIPPED R3-vs-R4 GAP IS A BOUNDS-CHECK
    SPELLING AND NOT THE SAFETY REPRESENTATION.** `../NOTES.md` §8c attributes
    the R2->R3 saving to four named things and §10 frames R3-vs-R4 as `Option`
    against `MaybeUninit` + witness. **Neither is what the 6.71 % gap between the
    shipped R3 and the shipped R4 is made of.** The shipped R3 pays **four per-op
    window bounds checks** -- `win[p]`, `win[p + 1]`, `win[p + 2]`, `win[p + 3]`,
    which LLVM emits as four `cmp %rdi,<stack slot>` / `je <panic>` pairs, **8
    instructions per op, 16 ops per call on `small.bin` = 128.00 Ir/call**
    against a measured gap of **131.19 Ir/call, i.e. 97.6 % of it**.
    `r3_chunks_exact` recovers **-7.42 %** of it in SAFE Rust with no `unsafe`
    token and no trusted item, taking the R3 side to **1930.232 Ir/call against
    the shipped R4's 1953.850** -- so ⭐ **the ORDERING of the published
    `fixed-R4 bound` reverses under search**, from R3 `+6.71 %` dearer to the
    cheapest R3 `-1.21 %` against the shipped R4. **Ordering, never interval.**
    ⭐⭐ **AND THE SAFE WINNER BEATS THE UNSAFE CONTROL**: `ctl_r3_unchecked` --
    the same rung with every window read through `get_unchecked` -- measures
    **1946.174**, because `chunks_exact` deletes the per-op OFFSET ARITHMETIC as
    well as the checks. That control was written as a ceiling and is not one; see
    `ctl_r3_unchecked_is_not_an_upper_bound`.
  * ⛔⛔ **R4 IS DEGENERATE ON COST -- `r4_endpoint_degenerate` is TRUE WITH AND
    WITHOUT the gate-rule filter -- AND WHAT THE SEARCH FOUND INSTEAD IS ON THE
    TCB AXIS.** Nothing priced here is cheaper than the shipped R4 by more than
    `TIE_PCT`; the best is a byte-identical tie. **But all three variants with a
    SMALLER trusted base are refused by `harness/check.py` -- two by stage
    5c-twin's `n_twins == 0` rule (F104) and one by `_scan_unsafe_sites`
    (F97)** -- which this file MEASURES with the gate's own `_is_trusted` /
    `vparse` / `_UNSAFE_RE` rather than predicting. ⭐⭐ `r4_no_wrapper` is the
    sharp one: **`external_body` 4 -> 3 at a BYTE-IDENTICAL `kernel` and 34
    verified / 0 errors, and the only thing standing in its way is a gate rule.**
    ⛔⛔ **NOTHING HERE ENLARGES THE TRUSTED BASE TO MAKE A GATE STAGE HAPPIER.**
    That is cost-selection on the TCB axis, which is the pressure F104 reports
    and which this programme publishes. The direction of travel in this file is
    the other one: every variant priced REDUCES the surface, and the result is
    that the gate refuses all three.

⛔⛔ **AND TWO OF THIS FILE'S OWN CLAIMS WERE WRONG UNTIL IT WAS RUN, WHICH IS THE
REASON BOTH LAWS IT OBEYS ARE WRITTEN AS PROCEDURE RATHER THAN AS SENTENCES:**
  1. the first draft keyed `english_verdict_problems` on the `required` ENTRY and
     fired on **all six R4 variants including the shipped rung's own spelling**,
     because `required[0].rust` quotes `` `Option` `` incidentally -- item 100's
     class, found by running `--audit-only` and reading the output
     (`WITNESS_PIN`'s note);
  2. `kernel_shape`'s digest was **path-sensitive** and produced **a false
     negative and a false positive in the same run** -- F101, live, in a fresh
     copy of the machinery rather than only on `ph29` (`_SLUGS`' note).
**Neither was found by reasoning.**

⚠⚠ **WHICH STATISTIC, AND IT IS *NOT* THE ROW'S HEADLINE -- MEASURED, NOT
ASSUMED.** `../NOTES.md` §8a/§9 publish the row in **W1** because `inside_share`
on the **C** rungs is **22.24 %**. `.memory-php/03-numbers.md`'s last entry is
that `inside_share` is **PER-CELL**: on the **Rust** rungs every helper is
`#[inline(always)]` into `kernel`, so `kernel` carries **~98.6 %** of the program
and **A1 resolves a respelling to the instruction.** ▶ **This file publishes A1
and quotes W1 labelled beside every figure.** Stage 2b recomputes `inside_share`
per cell from this pipeline's own two families, so the choice is re-derived on
every run instead of inherited. F91 is the general reason: `|B/A|` is
**49.6-393.9x** where two rungs differ by 1-2 instructions, and an endpoint
search is exactly that regime.

⚠ Every percentage in this file and in `spellings.json` is **A1 (or W1, where
labelled), `inputs/small.bin`, `O3`/`isolated`, against the named base** --
F98's four qualifiers (`.memory-php/03-numbers.md`), which a published finding
once shipped without any of.

THE BAR ON AN R4 CANDIDATE, AND IT IS READ RATHER THAN HARD-CODED
-----------------------------------------------------------------
`../spec.md` pins `identity: unsafe vs verus = O0 differ / O3 norel` and
`results-php/gate/ph52-concat-copy-uninit.json` MEASURES `differ`/`norel`.
`identity_premise()` reads the pin **and** the record; `admissibility()` is a
function of what it finds. ⚠⚠ **`norel` IS NOT `exact`, and this file does not
treat it as byte identity**: `harness/asm.py::identity_level` defines `norel` as
*byte-identical once pc-relative displacement fields are zeroed*, and it is
computed here by IMPORTING `asm.py` -- the gate's own pipeline -- rather than by
a local digest. ⭐ That also makes the comparison immune to F101: a hand-rolled
digest that keeps rip-relative displacements is **path-sensitive**, and this
file's exec and twin sources differ in path length by the six characters of
`_verus`, which is F101's exact trap. `norel` masks exactly those fields.
⚠ It reads the RECORD as well as the prose because F82's negative N6 found a PAT
row (`p25`) carrying `identity: unsafe == verus, O3 exact` as shared-block
BOILERPLATE while its real pin is `norel`.

⛔ **A rung is NEVER cost-selected** (`.memory/02-bench-rules.md`). **This file
reports what exists; the shipped rungs stay put** unless the manager moves them.
Two numbers ship, labelled, in each family:

    fixed-R4 bound   R3ship - R4ship      both endpoints held by fiat
    R3-side span     cheapest-found to dearest-found in contract, named

and **NO PAIR INTERVAL**: `min(R3 found) - min(R4 found)` differences two upper
bounds and bounds nothing in either direction. `ph03`'s hashed `why` retracts
that construction in terms and this file does not resurrect it.

THE VARIANTS -- all produced by TEXT SUBSTITUTION from the shipped rungs
-----------------------------------------------------------------------
Nothing here is a hand-copied fork: every variant is the shipped `.rs` with an
exact-string substitution applied and the **hit count asserted**, so a variant
cannot drift away from the rung it claims to be a respelling of. `apply_subs`
raises rather than guessing.

R3 side, from `../safe_tuned.rs` -- all safe, **no `unsafe` token**, which
`unsafe_tokens()` asserts for every R3 variant:

  `v0_shipped`       the shipped R3, unmodified. 412 `kernel` instructions,
                     **5 panic call sites** -- one for the window slice and
                     FOUR for the per-op reads.
  `r3_oprec_slice`   the op record as ONE 4-byte `&[u8]` sub-slice, read through
                     that. The sub-slice's length is the constant `OP_BYTES`, so
                     LLVM folds `rec[0..3]`'s four checks away and ONE range
                     check survives. 372 instructions, 2 panic sites.
                     ⚠ The panic condition is UNCHANGED: the shipped reads need
                     `p + 3 < win.len()` and the sub-slice needs
                     `p + 4 <= win.len()`, which is the same predicate.
  `r3_oprec_array`   the same lever with `&[u8; OP_BYTES]` + `try_into`, which
                     is `ph45`'s own `safe_tuned.rs` spelling. **Expected
                     byte-identical to `r3_oprec_slice`**, which
                     `oprec_array_byte_identical_to_slice` in the sidecar
                     records -- `ph45` §5.6's result (*the compile-time-constant
                     length buys nothing; the lever is elsewhere*) on a third
                     row, and here in its sharper byte-identical form.
  `r3_chunks_exact`  ⭐⭐ **THE WINNER.** `win[OPS_OFF..].chunks_exact(OP_BYTES)
                     .take(n_ops)` deletes the per-op offset arithmetic as well
                     as all four checks: **388 instructions and ONE panic site,
                     the same as the unsafe rung's.**
                     ⚠ It removes a panic path the shipped spelling HAS --
                     `take(n_ops)` cannot run off the end where `win[p]` would
                     panic -- which is unreachable on every input
                     (`n_ops = rd32(win, 0) % (cap + 1)` and `chunks_exact`
                     yields exactly `cap` chunks), and the six checksums are
                     unchanged, which stage 1 asserts.
  `r3_head_slice`    ⚠ **THE CALIBRATION NULL, and it is a null for a MEASURED
                     reason rather than by construction.** It gives the two head
                     words their own `&win[0..OPS_OFF]` sub-slice -- the same
                     lever, applied to `rd32(win, 0)` / `rd32(win, 4)`. It
                     changes **nothing**: 412 instructions and 5 panic sites,
                     identical to the shipped rung, because LLVM already proves
                     `len >= 8` from `cap = (len - OPS_OFF) / OP_BYTES` and
                     emits no check for the head reads at all. ▶ **So the four
                     surviving checks are the PER-OP reads and only those**, and
                     a search whose every entry moves is a search nobody can
                     calibrate.
  `r3_both`          `r3_oprec_slice` + `r3_head_slice`, so the null's
                     independence is checked rather than assumed.
  `r3_loop_for`      a SECOND null: `while o < n_ops { ... o = o + 1 }` becomes
                     `for _o in 0..n_ops`. Byte-identical to the shipped rung --
                     two nulls from two different directions.

R4 side, from `../unsafe.rs` (exec) and `../verus.rs` (twin), and **each one's
substitution is applied to `../verus.rs` as well and the result is put through
Verus**:

  `v0_shipped`       the shipped R4. 444 `kernel` instructions, ONE panic site,
                     4 `external_body` items (`load_input`, `emit`,
                     `win_get_unchecked`, `slot_read_unchecked`), of which
                     `harness/check.py::_is_trusted` counts **2** as trusted
                     (the other two have neither `ensures` nor `unsafe`), ONE
                     twin, twin 33 verified / 0 errors.
  `r4_slot_byval`    ⚠ **THE R4-SIDE CALIBRATION NULL.** The one trusted read
                     takes its `MaybeUninit<Pr>` BY VALUE --
                     `m.assume_init()` instead of `*m.assume_init_ref()` -- so
                     the row's own *"`assume_init_ref` plus a copy"* becomes a
                     copy plus `assume_init`. Same trusted surface, same twin
                     count, byte-identical `kernel`. **A TIE, and it is the
                     entry that says the pipeline can report a tie.**
  `r4_oprec_checked` the four per-op window reads become CHECKED `win[p]`, with
                     `rd32` left unchecked -- i.e. exactly the four checks the
                     R3 search deletes, put back into R4. **481 instructions, 5
                     panic sites, trusted surface UNCHANGED.** ▶ This is the
                     mirror that makes the R3 result legible: the same four
                     checks are worth the same in both rungs and in both
                     directions, which is what makes them the row's dominant
                     same-language term rather than an R3 quirk.
  `r4_win_checked`   ⭐ **`../NOTES.md` §8f's `-7.12 %` REPAIR, REVERSED IN THIS
                     PIPELINE.** `win_get_unchecked` is deleted outright: both
                     head reads and all four per-op reads become safe indexing.
                     **One fewer trusted item** (`_is_trusted` counts 1), and
                     ⛔ **ZERO twins, so `harness/check.py`'s stage 5c-twin
                     `n_twins == 0` rule REFUSES IT -- F104, measured on a
                     variant rather than argued.**
  `r4_win_oprec`     the same trusted-surface reduction with the R3 winner's
                     sub-slice spelling instead of four separate indexings, so
                     the surface reduction and the bounds-check spelling are
                     SEPARABLE. 464 instructions, 2 panic sites. ⛔ Refused by
                     the same `n_twins == 0` rule.
  `r4_no_wrapper`    ⭐⭐⭐ **THE SHARPEST ENTRY ON THE ROW: ONE FEWER TRUSTED
                     ITEM AT A BYTE-IDENTICAL `kernel`, AND THE ONLY OBSTACLE IS
                     A GATE RULE.** `#[verifier::external_body]` comes off
                     `slot_read_unchecked` and nothing else changes -- the name,
                     the signature, the `requires`, the `ensures` and the body
                     all stay -- so Verus CHECKS the body against the pinned
                     vstd's own `assume_specification` for
                     `MaybeUninit::assume_init_ref`
                     (`std_specs/maybe_uninit.rs:45-49`) instead of trusting it.
                     **34 verified / 0 errors** (one MORE than the shipped twin,
                     because the body is now a proof obligation) and
                     `external_body` 4 -> 3. ⛔ `harness/check.py::_scan_unsafe_sites`
                     refuses it, because the `unsafe` token now sits in a body
                     the gate does not treat as trusted -- **F97's collision,
                     measured as a rung candidate.** ⭐ `controls/mu_unwrapped.rs`
                     is the same fact in miniature and `controls/negatives.py
                     --verus` arm N2 runs it; this entry is that fact inside the
                     whole rung, which is the stronger object.
                     ⓘ It does NOT fail `required[1]`: the backticked span is
                     `slot_read_unchecked`, and the name is still there.

  `ctl_nowitness`    `../controls/r4_nowitness.rs`, the witness-free program, so
                     `../NOTES.md` §8g's witness cost can be re-priced in THIS
                     pipeline rather than across two runs. ⚠ **SIDE `CTL`, so
                     `cheapest_in_contract` and `cheaper_than_shipped` refuse it
                     by construction** -- it is not a rung and cannot become one:
                     it is `zend.c:243` with nothing between, which is the
                     defect.
  `ctl_r3_unchecked` ⚠ **THE BOUNDS-CHECK-FREE POINT AT THE SHIPPED SPELLING,
                     and it is a CONTROL and can never be a rung**: the shipped
                     R3 with `win.get_unchecked` in place of every window index.
                     A safe-tuned rung containing an `unsafe` token is not an R3
                     by definition, so this is side `CTL` and stage 1 asserts the
                     token count. It isolates the bounds-check term, which is
                     what makes the 128-of-131 Ir attribution checkable.
                     ⛔ **IT IS NOT A CEILING AND THIS FILE'S FIRST DRAFT CALLED
                     IT ONE**: `r3_chunks_exact` measures **1930.232** against
                     its **1946.174**, because `chunks_exact` deletes the per-op
                     offset arithmetic as well as the checks. ⭐ *A safe
                     respelling beats the same rung with every bounds check
                     removed by `get_unchecked`* is the stronger statement and
                     it is the measured one.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every variant is checked against `harness/check.py::spelling_matches` for
    EVERY backticked entry in `../spec.md`'s `idiom` -- required and forbidden,
    per-language entries included -- **before its number is quoted**.
    ⚠ A `forbidden` hit DISQUALIFIES; a `required` miss is REPORTED and does
    not. That is `check.py`'s own semantics and not a stricter invention: this
    row's `required` C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN
    (`required[1].c` is the upstream fix as a one-line presence test) and the
    shipped gate record reports `required_pins_nothing: 25` with
    `forbidden_hits: 0` and calls the row `PASS-WITH-BLOCKED-ROWS`.
    ⚠ `admissible` is THREE-VALUED, and on this row it is FOUR-valued: the token
    audit decides what a grep can decide; `english_verdict` is where a variant
    carries a sentence; and `gate_refusals` is a THIRD, MECHANICAL exclusion
    computed from `harness/check.py`'s own predicates. All three are separate
    fields so a reader can re-derive either verdict.
  * ⚠⚠ **ONE REFERENCE CHECKSUM FOR EVERY SIDE, AND ON THIS ROW THAT IS A
    DECLARED PROPERTY RATHER THAN A CONVENIENCE.** `ph53`'s copy needs a
    per-side reference because its R3 and R4 diverge on one input by
    declaration. **ph52's four Rust rungs agree bit for bit on every shipped
    input** -- `../spec.md`'s `idiom.required[7]` says so and `check.py` stage 2
    checks it -- so this file uses R4 `v0_shipped` as the single reference AND
    asserts that R3 `v0_shipped` agrees with it on all six inputs. If that ever
    stopped holding the assertion is the one that fires, not a variant.
  * ⚠⚠ **BOTH FAMILIES, from ONE callgrind run per (variant, input).**
    **A1** is `kernel_exclusive_ir` off the pinned callgrind with
    `measure.py::_sum_rows` **IMPORTED and never transcribed** (`TASK_PHP_022`
    §3.2 measured that the transcription was a different function and produced a
    PLAUSIBLE WRONG NUMBER rather than an error). **W1** is
    `callgrind_annotate`'s own `PROGRAM TOTALS` line.
  * stage 2b recomputes `inside_share` per cell from A1/W1, so the statistic
    decision is re-derived rather than inherited from `../NOTES.md`.
  * stage 3 reproduces the SHIPPED cells in BOTH families before any variant is
    quoted: A1 against `results-php/ph52-concat-copy-uninit.json` (four cells)
    and W1 against `../NOTES.md` §8c/§8d's committed whole-program totals.
  * ⚠⚠ stage 4 puts every R4 twin through Verus and reads the ERROR TEXT.
    `is not supported` and `does not yet support` DISQUALIFY, because they are
    what forces a new TRUSTED item; `postcondition not satisfied` and
    `invariant not satisfied` disqualify NOTHING and are proof work. Twin
    identity is then computed with `harness/asm.py::identity_level` against the
    level `../spec.md` pins, which on this row is `norel` and NOT `exact`.
    ⚠ **An R4 variant with NO twin file is NEVER admissible**, and that is a
    rule and not an accident of the loop: see `r4_no_twin_reason`.
  * ⚠ **A DIFFERENCE BELOW `TIE_PCT` IS REPORTED AS A TIE, NOT AS A WIN.**

⚠⚠⚠ §H -- THE NEGATIVES ARE **INSIDE THIS FILE**
------------------------------------------------
`PROTOCOL_PHP.md` §H: *a change to a validator lands with its must-fire
negatives, or it does not land.* ⛔ **And `RECAP_PHP.md` item 97 measured the way
that rule gets satisfied without surviving a checkout: 13 §H-at-risk citations
across 4 rows, where a committed validator cites its must-fire suite in
gitignored `.temp/`.** ▶ **This file creates none of that debt. Both batteries
are functions in this module, they run on EVERY invocation including
`--audit-only`, and their failures go into `problems`** -- which
`harness/check.py::control_json_verdict` turns into `FRESH+VERDICT-FAILED` at
gate stage 9b. So breaking a guard here is a RED GATE, not a better-looking
number.

  `english_verdict_selftest()`   **10 arms** over synthetic `rows` dicts: 4
                                 must-FIRE (the pinned witness span dropped with
                                 no verdict, that the unexcluded variant really
                                 does reach the published number, a falsy
                                 verdict string, a typo'd key) and 6
                                 must-NOT-fire (an excluded variant leaves the
                                 endpoint, ⛔ **a DIFFERENT span of the SAME
                                 entry is not a violation** -- the arm that
                                 exists because the first draft got this wrong
                                 -- the R3 half stays searched, an R3 variant
                                 missing an R4-scoped pin is not a problem, the
                                 CTL side is not judged, and the REAL
                                 declaration is consistent).
  `gate_rule_selftest()`         **8 arms** over synthetic VERUS SOURCE TEXT,
                                 driving `gate_refusals()` -- the function whose
                                 output is this row's R4 verdict. 4 must-FIRE (a
                                 stray `unsafe`, an `unsafe` in a NON-trusted
                                 body, the justified-away-with-no-twin
                                 configuration, and an unparseable source) and 4
                                 must-NOT-fire (the shipped text, a trusted item
                                 WITH its twin, an `unsafe` inside a trusted
                                 body, and a source with no trusted item at
                                 all). ⭐ **The fourth must-fire arm is the one
                                 that matters most: a detector that cannot parse
                                 its input must REFUSE, not return `[]` -- `[]`
                                 reads exactly like *admissible*.**

⚠ Neither battery touches the filesystem or Verus, so `--audit-only` pays for
both and a reader gets the §H evidence in two seconds.

⚠⚠⚠ THE HONEST CAVEAT
----------------------
**Every figure here is about `rustc 1.97.1` / `LLVM 22.1.6` and Verus
`0.2026.08.09.92f466f` on this box**, and the largest lever found is an LLVM
decision (how many bounds checks survive a sub-slice). ▶ The honest claim is
*"an admissible cheaper R3 exists and no admissible cheaper R4 was found"*,
never *"this is the cheapest R3"* and never *"no cheaper R4 exists"* --
**searched is not exhausted**, and `../NOTES.md` §8g bounds the one R4 lever
this file did NOT build: the whole two-`bool` witness is `+0.632 %` W1, so a
perfectly free witness representation could buy at most that, which is why
`ph53`'s `-11.40 %` bitmask lever has no room to repeat here. That is stated as
an UNTESTED ceiling, not as a measurement.
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
SCRATCH = os.path.join(REPO, ".temp", "php46", "spellings")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
ROW = os.path.basename(PDIR)
RECORD = os.path.join(REPO, "results-php", "ph52-concat-copy-uninit.json")
GATE_RECORD = os.path.join(REPO, "results-php", "gate",
                           "ph52-concat-copy-uninit.json")
#: `harness/measure.py`'s own probe shapes for this row -- the SHIPPED inputs at
#: their own `n_iters`, which is what `results-php/ph52-concat-copy-uninit.json`
#: carries and therefore what `../NOTES.md` §8 quotes.
PROBES = (("small.bin", 74, 25_000), ("large.bin", 181, 10_000))
#: Below this, two cells are a TIE and neither is "cheaper".
TIE_PCT = 0.05
#: Only these two sides can move a published rung number; anything else is a
#: control by construction. `ctl_nowitness` and `ctl_r3_unchecked` are `CTL` for
#: exactly this reason.
RUNG_SIDES = ("R3", "R4")
#: `harness/check.py`'s own constant, re-stated here because this file computes
#: the twin rule rather than calling the stage. `gate_rule_selftest` arm G5 is
#: what stops it drifting: it builds a source whose twin is named with this
#: prefix and requires the detector to SEE it.
TWIN_PREFIX = "slb_twin_"
#: ⚠ The two whole-program totals this row commits to prose, both `O3`/`isolated`
#: /`small.bin`, which stage 3 reproduces: `../NOTES.md` §8c's *"R3 `safe_tuned`
#: 52,829,203"* and §8d's *"R4 `unsafe` 49,549,469"*. They are NOT in any
#: `results-php/` record -- `measure.py`'s `protocol.ir` says in terms
#: *"whole-program summary deliberately not recorded"* -- so these are the two
#: figures here pinned to a committed document rather than to a committed JSON.
#: `../NOTES.md` is in this row's GATE digest, so a change to it cannot go
#: unnoticed.
#: ⚠⚠ A +-0.5 % tolerance and not equality, and `.memory-php/03-numbers.md`
#: item 99 is why it cannot be equality: over four regenerations of one row's
#: sidecar every A1 figure was bit-identical while the whole-program column moved
#: by a constant +-14-28 Ir -- the argv/env block, i.e. the path length of
#: whatever invoked the run. `../NOTES.md` §8d sees the same term as the `+40 Ir`
#: between R4 and R5.
SHIPPED_WP = {("safe_tuned", "small.bin"): 52_829_203,
              ("unsafe", "small.bin"): 49_549_469}
#: The named unchecked accessors of `../unsafe.rs`. `trusted_accessors` counts
#: CALL SITES of these, definitions subtracted. ⚠ `assume_init_ref` and
#: `assume_init` are here as well, because `r4_no_wrapper` performs the unchecked
#: operation without going through a wrapper and a census keyed on wrapper names
#: alone would score it ZERO unchecked operations.
ACCESSORS = ("win_get_unchecked", "slot_read_unchecked", "get_unchecked",
             "assume_init_ref", "assume_init")

#: ⛔⛔⛔ **EVERY SCRATCH SOURCE IS NAMED `vNN.rs` -- A FIXED-WIDTH SLUG -- AND
#: THAT IS NOT TIDINESS. IT IS F101's DEFECT, WHICH FIRED LIVE IN THIS FILE'S
#: FIRST RUN, IN BOTH DIRECTIONS.**
#:
#: `kernel_shape`'s digest deliberately KEEPS rip-relative displacements, because
#: they are code. But `rustc` embeds the SOURCE PATH in its panic-location data,
#: so a longer path moves every displacement after it. With the obvious naming
#: (`R4_<name>.rs`) the first run produced:
#:
#:   * a **FALSE NEGATIVE**: `r4_no_wrapper`'s exec source is byte-identical to
#:     `../unsafe.rs` -- its substitution list for `rs` is empty -- and its digest
#:     came out `0a7bd074f8b6` against `v0_shipped`'s `2f8fbf60a9eb`, at the same
#:     444 instructions and the same A1 to the digit;
#:   * a **FALSE POSITIVE**: `r4_slot_byval` and `r4_no_wrapper` shared a digest,
#:     because `R4_r4_slot_byval.rs` and `R4_r4_no_wrapper.rs` are the same LENGTH
#:     -- two genuinely different sources reported byte-identical.
#:
#: ▶ **A fixed-width slug makes every exec source path the same length, so the
#: term cannot vary and `kernel_shape`'s digest is a claim about code again.**
#: `main` ASSERTS the equal lengths rather than trusting the naming convention,
#: and the twin paths are deliberately allowed to differ, because the
#: exec-vs-twin question is answered at `norel` by `harness/asm.py` instead.
#: ⚠ `scratch_slug` in the sidecar is the mapping, so a reader can find the file.
_SLUGS = {}


def slug(side, name):
    return _SLUGS[(side, name)]


# ---- the substitutions -------------------------------------------------------
# (name, side, why, {file: [(old, new, hits), ...]}, english_verdict)
# `file` is "rs" for the rung source and "verus" for the R5 twin.
#
# ⚠⚠ ORDER INSIDE A LIST IS LOAD BEARING AND THE HIT COUNTS ARE WHAT SAY SO.
# `_S_LOOP` CONTAINS `_S_OPS`, so a list that ran the whole-block substitution
# after the narrower one would find its anchor gone and the count would come out
# 0 instead of 1. `apply_subs` raises rather than guessing.

# ======== R3, from ../safe_tuned.rs ==========================================
_S_OPS = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;
"""
_S_OPS_SLICE = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let rec: &[u8] = &win[p..p + OP_BYTES];
        let a1: u32 = (rec[0] as u32) % NARM;
        let x1: u32 = rec[1] as u32;
        let a2: u32 = (rec[2] as u32) % NARM;
        let x2: u32 = rec[3] as u32;
"""
_S_OPS_ARRAY = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let rec: &[u8; OP_BYTES] = (&win[p..p + OP_BYTES]).try_into().unwrap();
        let a1: u32 = (rec[0] as u32) % NARM;
        let x1: u32 = rec[1] as u32;
        let a2: u32 = (rec[2] as u32) % NARM;
        let x2: u32 = rec[3] as u32;
"""
_S_OPS_UNCH = """        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (unsafe { *win.get_unchecked(p) } as u32) % NARM;
        let x1: u32 = unsafe { *win.get_unchecked(p + 1) } as u32;
        let a2: u32 = (unsafe { *win.get_unchecked(p + 2) } as u32) % NARM;
        let x2: u32 = unsafe { *win.get_unchecked(p + 3) } as u32;
"""
_S_LOOP = """    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;
"""
_S_LOOP_CHUNKS = """    for rec in win[OPS_OFF..].chunks_exact(OP_BYTES).take(n_ops) {
        let a1: u32 = (rec[0] as u32) % NARM;
        let x1: u32 = rec[1] as u32;
        let a2: u32 = (rec[2] as u32) % NARM;
        let x2: u32 = rec[3] as u32;
"""
_S_LOOP_FOR = """    for _o in 0..n_ops {
        let p: usize = OPS_OFF + OP_BYTES * _o;
        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;
"""
_S_INC = """        o = o + 1;
    }
"""
_S_NOINC = """    }
"""
_S_HEAD = """    let n_ops: usize = (rd32(win, 0) as usize) % (cap + 1);
    let mut acc: u64 = rd32(win, 4) as u64;
"""
_S_HEAD_SLICE = """    let hd: &[u8] = &win[0..OPS_OFF];
    let n_ops: usize = (rd32(hd, 0) as usize) % (cap + 1);
    let mut acc: u64 = rd32(hd, 4) as u64;
"""
_S_RD32 = """fn rd32(w: &[u8], o: usize) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
}
"""
_S_RD32_UNCH = """fn rd32(w: &[u8], o: usize) -> u32 {
    (unsafe { *w.get_unchecked(o) } as u32)
        | ((unsafe { *w.get_unchecked(o + 1) } as u32) << 8)
        | ((unsafe { *w.get_unchecked(o + 2) } as u32) << 16)
        | ((unsafe { *w.get_unchecked(o + 3) } as u32) << 24)
}
"""

_CTL_R3_VERDICT = (
    "NOT A RUNG AND CANNOT BECOME ONE, AND THE REASON IS THE LADDER's "
    "DEFINITION AND NOT THIS ROW's CONTRACT: R3 is SAFE Rust "
    "(.memory/01-ladder.md), and this variant reads the window through "
    "`get_unchecked` inside an `unsafe` block, so it is an R4 wearing R3's "
    "name -- unsafe_tokens() counts 8 where every other R3 variant counts 0, "
    "which stage 1 asserts. Its side is CTL so cheapest_in_contract and "
    "cheaper_than_shipped refuse it by construction. PRICED ON PURPOSE: it "
    "isolates the bounds-check term AT THE SHIPPED SPELLING, which is what makes "
    "the 128-of-131 Ir attribution checkable rather than asserted. ⛔ IT IS NOT "
    "AN UPPER BOUND ON THE R3 SEARCH AND THIS FILE'S FIRST DRAFT CALLED IT ONE: "
    "r3_chunks_exact is CHEAPER than it, because chunks_exact deletes the per-op "
    "OFFSET ARITHMETIC as well as the checks. See "
    "ctl_r3_unchecked_is_not_an_upper_bound in the sidecar.")

R3_VARIANTS = [
    ("v0_shipped", "R3", "the shipped R3, unmodified", {}, None),
    ("r3_oprec_slice", "R3",
     "the op record as ONE 4-byte &[u8] sub-slice: the four per-op window "
     "bounds checks collapse to one",
     {"rs": [(_S_OPS, _S_OPS_SLICE, 1)]}, None),
    ("r3_oprec_array", "R3",
     "the same lever with &[u8; OP_BYTES] + try_into, ph45's own spelling -- "
     "expected BYTE-IDENTICAL to r3_oprec_slice",
     {"rs": [(_S_OPS, _S_OPS_ARRAY, 1)]}, None),
    ("r3_chunks_exact", "R3",
     "chunks_exact(OP_BYTES).take(n_ops) -- deletes the per-op offset "
     "arithmetic as well as all four checks, leaving ONE panic site, the same "
     "count as the unsafe rung",
     {"rs": [(_S_LOOP, _S_LOOP_CHUNKS, 1), (_S_INC, _S_NOINC, 1)]}, None),
    ("r3_head_slice", "R3",
     "the same lever on the two HEAD words -- THE CALIBRATION NULL, and a null "
     "because LLVM already emits no check for them",
     {"rs": [(_S_HEAD, _S_HEAD_SLICE, 1)]}, None),
    ("r3_both", "R3", "r3_oprec_slice + r3_head_slice, so the null's "
     "independence is checked rather than assumed",
     {"rs": [(_S_OPS, _S_OPS_SLICE, 1), (_S_HEAD, _S_HEAD_SLICE, 1)]}, None),
    ("r3_loop_for", "R3",
     "A SECOND NULL from a different direction: `while o < n_ops` becomes "
     "`for _o in 0..n_ops`",
     {"rs": [(_S_LOOP, _S_LOOP_FOR, 1), (_S_INC, _S_NOINC, 1)]}, None),
]

# ======== R4, from ../unsafe.rs (exec) and ../verus.rs (twin) =================
_U_READ = """#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> Pr {
    unsafe { *m.assume_init_ref() }
}
"""
_U_READ_BYVAL = """#[inline(always)]
fn slot_read_unchecked(m: MaybeUninit<Pr>) -> Pr {
    unsafe { m.assume_init() }
}
"""
_U_CALL = "        let p: Pr = slot_read_unchecked(slot);\n"
_U_CALL_BYVAL = "        let p: Pr = slot_read_unchecked(*slot);\n"
_U_WINDEF = """#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

"""
_U_RD32 = """fn rd32(w: &[u8], o: usize) -> u32 {
    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
}
"""
_U_RD32_CK = """fn rd32(w: &[u8], o: usize) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
}
"""
_U_OPS = """        let a1: u32 = (win_get_unchecked(win, p) as u32) % NARM;
        let x1: u32 = win_get_unchecked(win, p + 1) as u32;
        let a2: u32 = (win_get_unchecked(win, p + 2) as u32) % NARM;
        let x2: u32 = win_get_unchecked(win, p + 3) as u32;
"""
_U_OPS_CK = """        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;
"""
_U_OPS_SLICE = """        let rec: &[u8] = &win[p..p + OP_BYTES];
        let a1: u32 = (rec[0] as u32) % NARM;
        let x1: u32 = rec[1] as u32;
        let a2: u32 = (rec[2] as u32) % NARM;
        let x2: u32 = rec[3] as u32;
"""

# ---- and the same, on ../verus.rs -------------------------------------------
_V_READ_EB = """#[verifier::external_body]
#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> (r: Pr)
"""
_V_READ_NOEB = """// ⭐ NOT `external_body`: Verus CHECKS this body against the pinned vstd's own
// `assume_specification` for `MaybeUninit::assume_init_ref`
// (`std_specs/maybe_uninit.rs:45-49`), which carries exactly the `requires`
// below. The contract is unchanged -- only who is trusted to meet it.
#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> (r: Pr)
"""
_V_READ_FULL = """#[verifier::external_body]
#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> (r: Pr)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { *m.assume_init_ref() }
}
"""
_V_READ_BYVAL = """#[verifier::external_body]
#[inline(always)]
fn slot_read_unchecked(m: MaybeUninit<Pr>) -> (r: Pr)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { m.assume_init() }
}
"""
_V_CALL = "        let p: Pr = slot_read_unchecked(slot);\n"
_V_CALL_BYVAL = "        let p: Pr = slot_read_unchecked(*slot);\n"
_V_WINITEM = """#[verifier::external_body]
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

"""
_V_TWIN = """#[cfg(slb_twin)]
fn slb_twin_win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

"""
_V_RD32 = """    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
"""
_V_RD32_CK = """    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
"""
_V_OPS = """        let a1: u32 = (win_get_unchecked(win, p) as u32) % NARM;
        let x1: u32 = win_get_unchecked(win, p + 1) as u32;
        let a2: u32 = (win_get_unchecked(win, p + 2) as u32) % NARM;
        let x2: u32 = win_get_unchecked(win, p + 3) as u32;
"""
_V_OPS_CK = """        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;
"""
_V_OPS_SLICE = """        let rec: &[u8] = &win[p..p + OP_BYTES];
        assert(rec@ =~= win@.subrange(p as int, p + OP_BYTES));
        let a1: u32 = (rec[0] as u32) % NARM;
        let x1: u32 = rec[1] as u32;
        let a2: u32 = (rec[2] as u32) % NARM;
        let x2: u32 = rec[3] as u32;
"""

_U_WIN_DROP = [(_U_RD32, _U_RD32_CK, 1), (_U_WINDEF, "", 1)]
_V_WIN_DROP = [(_V_RD32, _V_RD32_CK, 1), (_V_WINITEM, "", 1), (_V_TWIN, "", 1)]

R4_VARIANTS = [
    ("v0_shipped", "R4", "the shipped R4, unmodified", {}, None),
    ("r4_slot_byval", "R4",
     "THE R4-SIDE CALIBRATION NULL: the one trusted read takes its "
     "MaybeUninit<Pr> BY VALUE -- assume_init() instead of *assume_init_ref() "
     "-- same surface, same twin count",
     {"rs": [(_U_READ, _U_READ_BYVAL, 1), (_U_CALL, _U_CALL_BYVAL, 1)],
      "verus": [(_V_READ_FULL, _V_READ_BYVAL, 1), (_V_CALL, _V_CALL_BYVAL, 1)]},
     None),
    ("r4_oprec_checked", "R4",
     "THE MIRROR OF THE R3 RESULT: the four per-op window reads become CHECKED "
     "win[p], rd32 left unchecked -- the same four checks the R3 search "
     "deletes, put back into R4, at an UNCHANGED trusted surface",
     {"rs": [(_U_OPS, _U_OPS_CK, 1)], "verus": [(_V_OPS, _V_OPS_CK, 1)]}, None),
    ("r4_win_checked", "R4",
     "NOTES.md 8f's -7.12 per cent repair REVERSED: win_get_unchecked deleted "
     "outright, one fewer trusted item and ZERO twins",
     {"rs": _U_WIN_DROP + [(_U_OPS, _U_OPS_CK, 1)],
      "verus": _V_WIN_DROP + [(_V_OPS, _V_OPS_CK, 1)]}, None),
    ("r4_win_oprec", "R4",
     "the same trusted-surface reduction with the R3 winner's sub-slice "
     "spelling, so the surface reduction and the bounds-check spelling are "
     "SEPARABLE",
     {"rs": _U_WIN_DROP + [(_U_OPS, _U_OPS_SLICE, 1)],
      "verus": _V_WIN_DROP + [(_V_OPS, _V_OPS_SLICE, 1)]}, None),
    ("r4_no_wrapper", "R4",
     "external_body comes OFF slot_read_unchecked and nothing else changes: "
     "Verus checks the body against the pinned vstd's own assume_specification "
     "for MaybeUninit::assume_init_ref. One fewer trusted item at a "
     "byte-identical kernel",
     {"rs": [], "verus": [(_V_READ_EB, _V_READ_NOEB, 1)]}, None),
]

#: ⚠ The variants that are NOT derived by substitution from a shipped rung, so
#: they are declared separately and carry their own source path. `materialise`
#: refuses to invent a substitution for them.
#: (name, side, why, relpath, english_verdict)
FILE_VARIANTS = [
    ("ctl_nowitness", "CTL",
     "the witness-free program, so NOTES.md 8g's witness cost can be re-priced "
     "in THIS pipeline instead of across two runs",
     os.path.join("controls", "r4_nowitness.rs"),
     "NOT A RUNG AND CANNOT BECOME ONE: it is zend.c:243 with nothing between, "
     "which IS the defect -- it reads a MaybeUninit with no test at all, Miri "
     "is loud on it (NOTES.md 7d) and Verus refuses it (NOTES.md 11). Its side "
     "is CTL so cheapest_in_contract and cheaper_than_shipped refuse it by "
     "construction."),
]

#: ⚠ A CTL that is derived by substitution from `../safe_tuned.rs` -- the R3
#: ceiling. It is declared here rather than in `R3_VARIANTS` so that its SIDE
#: cannot be confused with a rung side by a later reader adding an entry.
CTL_VARIANTS = [
    ("ctl_r3_unchecked", "CTL",
     "THE CEILING OF THE R3 SEARCH: the shipped R3 with win.get_unchecked in "
     "place of every window index -- what the R3 side would cost if the four "
     "per-op bounds checks did not exist",
     {"rs": [(_S_RD32, _S_RD32_UNCH, 1), (_S_OPS, _S_OPS_UNCH, 1)]},
     _CTL_R3_VERDICT),
]


# ---- machinery ---------------------------------------------------------------
def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(REPO, *relpath))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_MODS = {}


def _mod(name, relpath):
    if name not in _MODS:
        _MODS[name] = _load("slb_" + name, relpath)
    return _MODS[name]


def load_check():
    """`harness/check.py`, IMPORTED. `PLAN_PHP.md` §2.1 forbids WRITING under
    `harness/`; reading is what the shim exists to do."""
    return _mod("check", ("harness", "check.py"))


def load_vparse():
    return _mod("vparse", ("harness", "vparse.py"))


def load_asm():
    """`harness/asm.py`, IMPORTED -- and this is the one place this file does
    NOT roll its own.

    ⚠⚠ `identity_level` is the gate's own definition of `exact` / `norel` /
    `counts` / `differ`, and `../spec.md` pins this row at `norel`. A local
    digest would have to reproduce the pc-relative masking to mean the same
    thing, and F101 is what happens when one does not: `ph53`'s
    `kernel_fingerprint` KEEPS rip-relative displacements on purpose, so its
    digest is **path-sensitive**, and this file's exec and twin sources differ in
    path length by the six characters of `_verus`. Importing `asm.py` removes the
    question."""
    return _mod("asm", ("harness", "asm.py"))


def load_measure():
    """`harness/measure.py`, IMPORTED and never transcribed, and lazily so that
    `--audit-only` does not pay for its imports of `slb`, `asm` and `build`.

    ⚠⚠ `TASK_PHP_022` §3.2 measured that a transcription of `_sum_rows` is a
    DIFFERENT FUNCTION -- it took the first matching annotate row instead of
    SUMMING all of them, matched the needle on the whole line instead of on the
    function field, and did not check callgrind's return code -- and that each
    difference produces a plausible wrong number rather than an error."""
    return _mod("measure", ("harness", "measure.py"))


def contract():
    txt = open(os.path.join(PDIR, "spec.md"), encoding="utf-8").read()
    return json.loads(re.search(r"```slb-contract\s*\n(.*?)```", txt,
                                re.S).group(1))


def identity_premise():
    """`(pinned_levels, measured_levels)` for the `unsafe` vs `verus` pair.

    ⚠⚠⚠ **THIS IS THE PREMISE `admissibility()` RESTS ON AND IT IS READ, NEVER
    ASSUMED.** `ph29`'s copy of this machinery hard-codes *"`identity` pins `O3
    exact`, so a twin must be byte-identical"*. On `ph52` the pin is `norel` at
    `O3` and `differ` at `O0`, so byte identity is NOT the bar and neither is
    *anything goes* -- and a hard-coded rule would get it wrong in one direction
    or the other.

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


def admissibility(pinned, measured, levels=None):
    """`(required_level, sentence)` -- what an R4 candidate's twin must reach at
    `O3`, as one of `harness/asm.py::IDENTITY_LEVELS`.

    ⚠⚠ **`norel` IS NOT `exact` AND THIS FUNCTION IS WHERE THAT IS HONOURED.**
    `asm.py::identity_level` orders the four levels `differ < counts < norel <
    exact`, and the bar is *the level this row PINS and MEASURES*, whatever that
    is: `exact` demands byte identity, `norel` demands byte identity once
    pc-relative displacement FIELDS are zeroed, `differ` demands nothing. So if
    this row were ever re-pinned the rule tightens or loosens WITH it instead of
    silently staying where it was.

    ⚠ A disagreement between the pin and the record falls back to the WEAKER of
    the two and says so loudly, because this file cannot tell which one is
    right."""
    levels = (load_asm().IDENTITY_LEVELS if levels is None else levels)
    p, m = pinned.get("O3"), measured.get("O3")
    if p == m and p in levels:
        return p, (f"O3 is pinned AND measured `{p}`, so an R4 candidate's twin "
                   f"must reach `{p}` by harness/asm.py::identity_level -- which "
                   f"for `norel` is byte identity once pc-relative displacement "
                   f"FIELDS are zeroed, and is NOT byte identity")
    if p in levels and m in levels:
        weak = levels[min(levels.index(p), levels.index(m))]
        return weak, (f"⚠ the pin says O3 `{p}` and the record measures `{m}` -- "
                      f"they DISAGREE, so this file falls back to the WEAKER bar "
                      f"(`{weak}`) and says so loudly")
    return levels[0], (f"⚠ the pin (`{p}`) or the record (`{m}`) names no level "
                       f"harness/asm.py knows, so no identity bar could be "
                       f"derived and the weakest (`{levels[0]}`) is used")


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


def _base_for(side, name):
    """Which shipped rung a substitution variant is derived from.

    ⚠ `ctl_r3_unchecked` is side `CTL` and derives from `../safe_tuned.rs`, so
    the mapping cannot be `side == "R3"`. It is keyed on the declaration the
    variant appears in, which `materialise` passes through."""
    return "safe_tuned.rs" if side == "R3" or name.startswith("ctl_r3") \
        else "unsafe.rs"


def materialise(name, side, subs):
    """Write the variant's sources into SCRATCH, driver path absolutised.

    ⚠ An R4 variant gets TWO files: the exec rung and the R5 twin. The twin's
    substitution list is explicit and does NOT fall back to the exec one -- the
    twin's items carry a `requires`, an `ensures`, loop invariants and a
    `decreases`, so the exec anchor does not occur in it and a silent fallback
    would leave the twin unchanged while the exec variant moved."""
    os.makedirs(SCRATCH, exist_ok=True)
    base = _base_for(side, name)
    src = _absolutise(apply_subs(
        open(os.path.join(PDIR, base), encoding="utf-8").read(),
        subs.get("rs", [])))
    p = os.path.join(SCRATCH, f"{slug(side, name)}.rs")
    open(p, "w", encoding="utf-8").write(src)
    vp = None
    if side == "R4":
        v = _absolutise(apply_subs(
            open(os.path.join(PDIR, "verus.rs"), encoding="utf-8").read(),
            subs.get("verus", [])))
        vp = os.path.join(SCRATCH, f"{slug(side, name)}_twin.rs")
        open(vp, "w", encoding="utf-8").write(v)
    return p, vp


def materialise_file(name, side, relpath):
    """A variant that is a COMMITTED FILE rather than a substitution.

    ⚠ It gets NO twin, and stage 4's rule for that is explicit rather than a
    silent skip: see `r4_no_twin_reason`."""
    os.makedirs(SCRATCH, exist_ok=True)
    src = _absolutise(open(os.path.join(PDIR, relpath),
                           encoding="utf-8").read())
    p = os.path.join(SCRATCH, f"{slug(side, name)}.rs")
    open(p, "w", encoding="utf-8").write(src)
    return p, None


def build(rs, out):
    """`harness/build.py::rust_flags('O3', 'isolated', panic='unwind')`,
    character for character."""
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
    callgrind run -- the two families this file reports.

    **A1** uses `harness/measure.py::_sum_rows` IMPORTED (see `load_measure`),
    and it is the HEADLINE FOR THE SEARCH, because the Rust rungs inline
    everything into `kernel`. **W1** is `callgrind_annotate`'s own `PROGRAM
    TOTALS` line, and it is the family the ROW publishes (`../NOTES.md` §9),
    quoted labelled beside A1 on every comparison.

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


#: The `kernel` needle, and it is NOT a bare substring.
#:
#: ⚠⚠ `ph16`'s copy of this machinery tests `"kernel" in name` on the whole
#: mangled symbol. That folds **every** symbol whose name merely contains the
#: letters into the digest: a sibling `kernel_prologue`, a twin `slb_twin_kernel`,
#: or -- measured, by `ph29`'s negative D2 -- a binary built from a crate called
#: `nokernel`, whose `main` mangles to `…_8nokernel4main`.
#: `harness/measure.py::_sum_rows` does NOT have this hole.
_KERNEL_SYM = re.compile(r"(?:^|[^A-Za-z_])kernel(?:$|[^A-Za-z0-9_])")
_XFER = re.compile(r"^(j[a-z]+|call|loop[a-z]*)\s+([0-9a-f]+)$")


def disasm(exe, needle=_KERNEL_SYM):
    """`{address: text}` for the `kernel` function only.

    ⚠ `harness/asm.py` is *the* objdump caller in `harness/`, and this is not an
    edit to it: six PAT patterns' `controls/` disassemble directly for exactly
    this reason (`CLAUDE.md` -- *the GATE has one pipeline, not the tree*). What
    is needed here is per-instruction TEXT keyed by address, which `asm.py` does
    not return -- and `asm.py` IS used, for the identity question, where its
    answer is the one that decides something.

    ⚠ objdump's RETURN CODE is checked. Without it a binary that does not exist
    disassembles to nothing and a digest of the empty string is a figure-shaped
    value that two such binaries SHARE (F79)."""
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


def kernel_shape(exe, needle=_KERNEL_SYM):
    """`(n_instructions, n_panic_call_sites, 12-hex digest)` of `kernel`'s text.

    ⭐ **`n_panic_call_sites` IS THE MECHANISM FIELD AND IT IS THE REASON THIS
    FUNCTION EXISTS AT ALL** (`PROTOCOL_PHP.md` §F8: a cost with no mechanism is
    an incomplete row). A `call` inside this row's `kernel` can only be a panic
    path -- every helper is `#[inline(always)]` and the row's own `kernel` calls
    nothing else -- so the count IS the number of surviving bounds checks plus
    one for the window slice. The shipped R3 is **5**, the shipped R4 is **1**,
    and `r3_chunks_exact` is **1**: that one column carries the whole R3 finding
    without a percentage.

    The digest is normalised so that it is a claim about CODE and not LAYOUT --
    crate hash gone, objdump's resolved rip-relative ADDRESS gone (the
    DISPLACEMENT stays, and it is the code), control-transfer targets turned into
    signed offsets from their own instruction. Registers and immediates are KEPT.

    ⚠⚠ **IT IS ONLY COMPARABLE WITHIN ONE BUILD DIRECTORY AND THIS FILE ONLY
    EVER COMPARES WITHIN ONE.** F101: `rustc` embeds the source path in its
    panic-location data, so a path 38 characters longer moved the displacements
    this function deliberately keeps, on 1 of 3 spellings measured. Every
    comparison here is between two binaries built side by side in `SCRATCH`, and
    the exec-vs-twin question -- the one where the path lengths DIFFER -- is
    answered by `harness/asm.py::identity_level` at `norel` instead, which masks
    exactly those fields.
    ⚠ `n_instructions` counts every disassembled instruction in the symbol,
    INCLUDING the `int3` pad, so it is not comparable to the measurement record's
    `n_fn_nopad` (444 here against the gate record's 425)."""
    txt = disasm(exe, needle)
    if not txt:
        raise RuntimeError(
            f"no `kernel` function in the disassembly of {exe} -- this is a "
            f"measurement that did not happen, not a kernel of length 0")
    body, calls = [], 0
    for a in sorted(txt):
        t = re.sub(r"\s+", " ", txt[a]).split("<")[0].split("#")[0].strip()
        if t.startswith("call"):
            calls += 1
        m = _XFER.match(t)
        body.append(f"{m.group(1)} {int(m.group(2), 16) - a:+d}" if m else t)
    return (len(body), calls,
            hashlib.md5("\n".join(body).encode()).hexdigest()[:12])


#: md5 of the EMPTY STRING, truncated the way `kernel_shape` truncates. F79's
#: defect produced exactly this value for a binary that does not exist, and two
#: of them compare EQUAL. `disasm` raises rather than producing it;
#: `byte_identical_pair` refuses it as well, so the two guards are independent.
_EMPTY_MD5 = hashlib.md5(b"").hexdigest()[:12]

_VR = re.compile(r"verification results:: (\d+) verified, (\d+) errors")
#: ⚠⚠ **TWO NEEDLES, NOT ONE.** `ph45`'s copy looks for `is not supported` only.
#: Verus 0.2026.08.09 answers some coercions with *"The verifier does not yet
#: support the following Rust feature"*, which is the SAME CLASS of refusal -- a
#: coverage fact about the toolchain, not a proof that failed -- and a reader of
#: `is not supported` alone would score such an output as unparseable rather than
#: as a disqualification.
_UNSUPPORTED = ("is not supported", "does not yet support")


def verus_ok(vp):
    """`(ok, message)` for one twin.

    ⚠⚠ **READ THE ERROR TEXT, NOT THE EXIT CODE** -- `../spec.md`'s own hashed
    rule. `is not supported` / `does not yet support` DISQUALIFY, because they
    are what forces a new TRUSTED item; `postcondition not satisfied` and
    `invariant not satisfied` disqualify NOTHING and are proof work (`p05` went
    `11 verified, 1 errors` -> `13 verified, 0 errors` with one lemma and one
    `proof` block, at zero TCB). Both are reported distinctly, because a file
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
    both explain these wrappers at length, and `../verus.rs` quotes the literal
    string `#[cfg(slb_twin)]` inside a comment -- which a raw `count()` reads as
    a second twin."""
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in src.splitlines())


def trusted_accessors(src, names=ACCESSORS):
    """`(n_call_sites, n_defined, sorted_names_defined)` for this row's unchecked
    accessors AND the raw operations they wrap.

    ⚠ MEASURED, not asserted, and definitions are subtracted so the number is
    CALL SITES and not mentions. ⚠ It is deliberately NOT a verdict: a variant
    with a smaller trusted surface at the same price is a third kind of result
    the bench rule has no name for, and this file reports it rather than ranking
    on it.

    ⚠⚠ **`assume_init_ref` AND `get_unchecked` ARE IN `ACCESSORS` AND THAT IS
    LOAD BEARING, NOT THOROUGHNESS.** `r4_no_wrapper` performs the unchecked
    `MaybeUninit` read with no `external_body` wrapper round it, and
    `ctl_r3_unchecked` reads the window with a bare `unsafe` block; a census
    keyed on this row's wrapper NAMES alone would score both at ZERO unchecked
    operations, which is the plausible wrong number rather than an error.

    ⚠⚠⚠ **AND THE MATCH IS ON THE BARE IDENTIFIER, NOT ON `NAME(`**, because a
    `\\bNAME\\s*\\(` call regex does not match across a generic parameter list
    and a generic definition then scores 0 calls and 1 definition -- sending the
    subtraction NEGATIVE. The `assert` below is there so the next such miscount
    is an error and not a number."""
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


def external_body_items(src):
    """`#[verifier::external_body]` items in a TWIN -- the count that is
    comparable to the gate record's `verus[].tcb_items`, which on the shipped
    twin is **4**.

    ⚠ It counts EVERY such item, `load_input` and `emit` included, because
    `.memory/04-verus.md` says every `external_body` item is TCB and not just the
    interesting ones. ⚠⚠ **It is NOT the same number as
    `harness/check.py::_is_trusted`'s count**, which is 2 on the shipped twin:
    `_is_trusted` additionally requires a non-empty `ensures` or an `unsafe`
    body, and `load_input`/`emit` have neither. `gate_refusals` reports that
    second count separately, and BOTH are in the sidecar, because the two answer
    different questions -- what the row axiomatises, and what the twin rules
    govern."""
    return _strip_comments(src).count("#[verifier::external_body]")


def unsafe_tokens(src):
    """`unsafe` tokens in an exec variant -- what still makes it an R4, and what
    makes `ctl_r3_unchecked` NOT an R3."""
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
    C pins are ABSENT from `c/kernel_hardened.c` BY DESIGN -- `required[1].c` is
    the upstream fix as a one-line presence test -- and the shipped gate record
    reports `required_pins_nothing: 25` with `forbidden_hits: 0` and calls the
    row `PASS-WITH-BLOCKED-ROWS`. An audit that treated a `required` miss as
    disqualifying would refuse the row's own hardened rung."""
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


# ---- the GATE's own two structural refusals, computed with the GATE's code ---
def gate_refusals(vsrc, justifications=None):
    """`([(stage, detail), ...], facts)` -- which `harness/check.py` stage would
    REFUSE a rung built from this Verus source, computed with the gate's own
    `_is_trusted`, `vparse.parse`, `vparse.blank_noncode` and `_UNSAFE_RE`.

    ⭐⭐ **THIS IS THE FIELD THAT MAKES `ph52`'s R4 RESULT WHAT IT IS, SO IT IS A
    FUNCTION AND NOT A SENTENCE.** Two stages, chosen because they are the two a
    `spec.md` re-declaration could NOT remove:

      * **`5-tcb-unsafe`** -- `check.py::_scan_unsafe_sites`: every `unsafe`
        token in a pinned Verus source must sit inside the body of an item
        `_is_trusted` accepts. There is no hatch. This is what refuses
        `r4_no_wrapper`, whose whole substitution is to let Verus CHECK the body
        that the shipped twin axiomatises -- **F97's collision, as a rung
        candidate rather than as an argument.**
      * **`5c-twin n_twins == 0`** -- `check.py::check_trusted_twins`: if every
        trusted item is excused by `verus.twin_justifications` and NO trusted
        item has a `slb_twin_` twin, the stage *"checked the strength of
        NOTHING"* and hard-fails. There is no hatch. This is what refuses
        `r4_win_checked` and `r4_win_oprec`, whose substitution deletes the row's
        ONLY twinnable item -- **F104, measured on a variant.**

    ⛔⛔ **AND THE DIRECTION IS THE WHOLE POINT. NOTHING IN THIS FILE ADDS A
    TWINNABLE TRUSTED ITEM TO MAKE EITHER STAGE HAPPIER.** That is cost-selection
    on the TCB axis -- the exact pressure F104 reports -- and the TCB is one of
    this project's published axes. Every variant here REDUCES the surface, and
    the measured answer is that the gate refuses all three.

    ⚠⚠ **A SOURCE THIS CANNOT PARSE IS A REFUSAL AND NOT AN EMPTY LIST.**
    `vparse.parse` raises `ValueError` on a malformed source and `check.py`'s own
    stage calls that a failure; returning `[]` here would read as *admissible*,
    which is the silent-pass shape this whole file is written against. Arm `G4`
    of `gate_rule_selftest` is the must-fire for it.

    ⚠ It is NOT the whole gate. It does not reproduce the `verus.items` /
    `verus.obligations` pins, the contract-sha stages, stage 3c or Miri -- those
    a ship WOULD have to satisfy and a `spec.md` edit CAN move. These two cannot
    be moved from `spec.md` at all, which is why they are the two computed."""
    chk, vpm = load_check(), load_vparse()
    justifications = {} if justifications is None else justifications
    try:
        items = vpm.parse(vsrc)
    except Exception as e:                                       # noqa: BLE001
        return ([("5-unparseable",
                  f"harness/vparse.py cannot parse this source "
                  f"({type(e).__name__}: {str(e)[:160]}), so NO gate rule could "
                  f"be evaluated over it. That is a REFUSAL and not an empty "
                  f"verdict -- check.py's own stage calls it `rep.fail`.")],
                {"trusted": None, "twins": None, "n_twins": None,
                 "stray_unsafe_lines": None, "parse_error": str(e)[:200]})
    code = vpm.blank_noncode(vsrc)
    trusted = [i for i in items if chk._is_trusted(i)]
    names = sorted(i.name for i in trusted)
    twins = sorted(i.name for i in items if i.name.startswith(TWIN_PREFIX))
    spans = [(i.body_start, i.body_end, i.name) for i in trusted
             if i.body_start is not None]
    stray = []
    for m in chk._UNSAFE_RE.finditer(code):
        if not [nm for a, b, nm in spans if a <= m.start() < b]:
            stray.append(code[:m.start()].count("\n") + 1)
    n_twins = sum(1 for nm in names if TWIN_PREFIX + nm in twins)
    excused = sorted(nm for nm in names if nm in justifications)
    out = []
    if stray:
        out.append(("5-tcb-unsafe",
                    f"check.py::_scan_unsafe_sites: {len(stray)} `unsafe` "
                    f"token(s) at line(s) {stray[:5]} sit outside every item "
                    f"_is_trusted accepts ({names}), and that stage has NO "
                    f"hatch. This is F97's collision: the operation is specified "
                    f"by the pinned vstd, so Verus is content, and the GATE is "
                    f"not."))
    if excused and n_twins == 0:
        out.append(("5c-twin",
                    f"check.py::check_trusted_twins: every trusted item "
                    f"({names}) is excused by verus.twin_justifications "
                    f"({excused}) and n_twins == 0, so stage 5c-twin would check "
                    f"the strength of NOTHING and hard-fails. This is F104: the "
                    f"rule refuses the configuration whose trusted base is "
                    f"SMALLEST."))
    return out, {"trusted": names, "twins": twins, "n_twins": n_twins,
                 "excused_by_spec": excused, "stray_unsafe_lines": stray}


def justifications_for(con, src="verus.rs"):
    """`{item name: why}` from `../spec.md`'s `verus.twin_justifications`, for one
    source. A function so `gate_rule_selftest` can hand `gate_refusals` a
    synthetic one and see both arms of the twin rule."""
    tj = (con.get("verus") or {}).get("twin_justifications") or {}
    v = tj.get(src) or {}
    return v if isinstance(v, dict) else {}


# ---- the verdicts, factored so they can be ATTACKED --------------------------
# `PROTOCOL_PHP.md` §H: a validator lands with its must-fire negatives. These
# functions ARE this file's verdict, so they are functions and not lines inside
# `main`, and the two selftest batteries below drive them over synthetic inputs
# -- none of which is reachable through the CLI.

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
#: ⓘ **ON THIS ROW IT IS EMPTY AND THAT IS A RESULT, NOT AN OVERSIGHT.**
#: `ph53`'s copy carries three entries, because `ph53`'s `required[4]` pins a
#: witness REPRESENTATION and a cheaper bitmask witness establishes the same fact
#: by a different expression (item 83, ruled at `TASK_PHP_043` §1). **No R4
#: variant here changes a backticked `required` span at all**: `r4_no_wrapper`
#: keeps the name `slot_read_unchecked`, every variant keeps
#: `*constructed = true;` and `al.free(p.req)`, and the two CTL variants carry
#: their verdicts INLINE in their own declarations. ▶ **So the item-83 class does
#: not reach this row's endpoints, and `english_verdict_problems` is what makes
#: that a checked statement rather than an assumed one**: if a later variant DOES
#: miss `WITNESS_PIN` and carries no verdict, the consistency arm fires and the
#: gate goes red.
#:
#: ⛔⛔ **AND IT IS NOT EMPTY BECAUSE EMPTYING IT HELPED.** Nothing excluded by
#: English would have changed either endpoint here: the R3 winner satisfies every
#: `required` span its shipped rung does, and the R4 endpoint is degenerate on
#: COST before any English is applied. `.memory/02-bench-rules.md`'s *a rung is
#: never cost-selected* binds a pin the same way it binds a rung, and the test of
#: that is whether the ruling ever costs the row something -- which on `ph53` it
#: did, and here there is nothing for it to cost.
ENGLISH_VERDICTS = {}

#: The `required` entry, **THE SPAN INSIDE IT**, and the side its English scopes
#: to. `required[0].rust`'s pin is `` `*constructed = true;` `` -- *"THE WITNESS,
#: WRITTEN LAST, AFTER THE SLOT. Present in unsafe.rs and verus.rs and in no
#: other rung"* -- so an R4 variant that stops carrying that spelling has changed
#: the thing the entry pins, and owes an `english_verdict` under item 83's
#: ruling. A triple and not three literals inside a function, so
#: `english_verdict_problems` and the selftest cannot drift apart.
#:
#: ⛔⛔ **IT IS A TRIPLE AND NOT A PAIR, AND THE REASON IS A DEFECT THE AUDIT
#: FOUND IN THIS FILE'S FIRST DRAFT -- ITEM 100's CLASS, ON A THIRD ROW.** The
#: first draft keyed on the ENTRY (`required[0]`, side `R4`) and fired on **all
#: six R4 variants, the shipped rung's own spelling included**, because
#: `required[0].rust` carries a SECOND backticked span -- `` `Option` `` -- which
#: it quotes only to say that *safe_naive.rs's ordering pin is the `Option`'s own
#: discriminant*. Under `harness/check.py::spelling_matches` that incidental
#: backtick is a declared spelling matched against every Rust rung, so every
#: unsafe rung records `required[0] `Option`` in `required_absent` **by design**,
#: and an entry-indexed rule reads the entry's own English as a violation of
#: itself. ▶ **Keying on the SPAN is what makes the rule mean what its prose
#: says.** ⭐ **It was not found by reasoning. It was found by running
#: `--audit-only` and reading the output**, which is exactly what
#: `.memory-php/02-ladder.md`'s backtick law says to do.
WITNESS_PIN = ("required[0]", "*constructed = true;", "R4")


def english_verdict_problems(rows, pin=WITNESS_PIN, verdicts=None):
    """`[problem, ...]` -- is the item-83 ruling applied CONSISTENTLY?

    ⚠⚠ **THE MUST-FIRE ARM FOR `ENGLISH_VERDICTS`, AND ON THIS ROW THE EDIT IT
    EXISTS TO CATCH IS *ADDING A VARIANT THAT DROPS THE WITNESS SPELLING AND NOT
    NOTICING*.** `PROTOCOL_PHP.md` §H: a change to a validator lands with its
    must-fire negatives. This file's verdict is `cheapest_in_contract` /
    `cheaper_than_shipped`, and **nothing else in the pipeline would notice**: the
    exclusion is English, `required` is presence-only and cannot fail the gate,
    and the numbers would simply come back looking like a searched endpoint. So
    `main` runs this on the REAL rows on every invocation and appends to
    `problems`, which `harness/check.py::control_json_verdict` turns into
    `FRESH+VERDICT-FAILED` at gate stage 9b.

    ⭐ **THE RULE IS DERIVED FROM THE AUDIT, NOT FROM A NAME LIST**, which is
    what makes it a check rather than a restatement: every variant on the pinned
    side, other than that side's shipped rung, that records **the pinned SPAN**
    in `required_absent` must carry an `english_verdict`.

    ⛔ **IT IS SCOPED TO ONE SPAN, IN ONE ENTRY, ON ONE SIDE -- THREE
    NARROWINGS AND EACH ONE IS A MEASURED FAILURE MODE.** Generalising it to
    every backticked `required` span is the reading
    `harness/check.py::idiom_audit` measures at **41 misses of 158 obligations,
    all 41 non-defects and 17 of them ANTI-signal**. Generalising it to every
    span in the pinned ENTRY is the defect `WITNESS_PIN`'s own note records: the
    entry quotes `` `Option` `` incidentally and no unsafe rung carries it, so an
    entry-indexed rule fires on the shipped rung's own family. And dropping the
    side makes every R3 variant a violation of an R4-scoped pin. The SCOPE is the
    reading; this function is the bookkeeping.

    ⚠ **AND IT CHECKS THE KEYS TOO.** A typo'd key in `ENGLISH_VERDICTS` excludes
    nothing and reads exactly like a populated constant, which is the
    silent-failure shape this whole file is written against."""
    tag, span, side = pin
    verdicts = ENGLISH_VERDICTS if verdicts is None else verdicts
    out = []
    declared = {n for n, _s, _w, _su, _e in
                (list(R3_VARIANTS) + list(R4_VARIANTS) + list(CTL_VARIANTS)
                 + list(FILE_VARIANTS))}
    for k in sorted(verdicts):
        if k not in declared:
            out.append(
                f"ENGLISH_VERDICTS names `{k}`, which is not a declared "
                f"variant, so it excludes NOTHING while reading as an "
                f"exclusion -- a typo here is silent")
    needle = f"{tag} `{span}`"
    for (s, name), r in sorted(rows.items()):
        if s != side or name == "v0_shipped":
            continue
        if needle in (r.get("required_absent") or []) \
                and not r.get("english_verdict"):
            out.append(
                f"{s} {name} records `{needle}` in required_absent and carries "
                f"NO english_verdict, so it is still counted as a rung "
                f"candidate. ../spec.md's {tag}.rust pins the witness spelling "
                f"`{span}` and scopes it to unsafe.rs and verus.rs in its own "
                f"English, so under item 83's ruling (TASK_PHP_043 section 1) a "
                f"variant that drops it is out of contract on that entry. Fix: "
                f"add `{name}` to ENGLISH_VERDICTS with the reading, or respell "
                f"the variant so it keeps the span.")
    return out


def english_verdict_selftest():
    """`[problem, ...]` -- the §H battery for the exclusion PATH, on synthetic
    rows, run on every invocation because a green row exercises a validator and
    does not attack it.

    **10 arms. The four must-FIRE ones are the point**: `E1` a variant that
    drops the pinned witness span with no verdict, `E1b` that the unexcluded
    variant really does reach the published number, `E2` a falsy verdict string,
    `E3` a typo'd key. The six must-NOT-fire ones pin what the ruling may NOT
    do: `E1c` an excluded variant leaves the endpoint, `E4` the R3 half stays
    searched, `E5` an R3 variant missing the R4-scoped pin is not a problem,
    `E6` the CTL side is not judged, `E7` the shipped constant leaves no
    consistency problem on the REAL declaration, and `E8` -- ⛔⛔ **the arm the
    first draft's defect demands** -- a variant that misses a DIFFERENT span of
    the SAME entry (`` `Option` ``, which no unsafe rung carries and which
    `required[0].rust` quotes only to describe `safe_naive.rs`) is **NOT** a
    problem. `E8` is what fails if the rule is ever re-keyed on the entry index.

    ⚠ `E1` is synthetic ON PURPOSE, because no shipped variant on this row drops
    the span -- which is exactly why the arm has to exist: an arm nobody has seen
    fire is not an arm. ⚠ The variant it uses is a DECLARED name
    (`r4_slot_byval`), so the arm measures the missing-verdict path and not the
    typo'd-key path, which the first draft conflated."""
    bad = []
    tag, span, _side = WITNESS_PIN
    pin_miss = f"{tag} `{span}`"
    #: The OTHER backticked span in the same entry -- see `WITNESS_PIN`'s note.
    other_miss = f"{tag} `Option`"
    synth = "r4_slot_byval"

    def want(t, cond, why):
        if not cond:
            bad.append(f"{t}: {why}")

    def mk(absent, verdicts):
        """`rows` with one DECLARED R4 variant whose `required_absent` is
        `absent` -- so the arms can distinguish WHICH span it misses."""
        rows = {("R4", "v0_shipped"): {
            "side": "R4", "name": "v0_shipped", "ir_per_call_small": 1953.85,
            "in_contract": True, "verus_rs": "x",
            "required_absent": [other_miss], "english_verdict": None}}
        rows[("R4", synth)] = {
            "side": "R4", "name": synth, "ir_per_call_small": 1900.0,
            "in_contract": True, "verus_rs": "x",
            "required_absent": list(absent),
            "english_verdict": verdicts.get(synth)}
        return rows

    probs = english_verdict_problems(mk([pin_miss], {}), verdicts={})
    want("E1 (must-FIRE: the pinned span dropped, no verdict)",
         len(probs) == 1 and synth in probs[0],
         f"a variant that drops {tag}.rust's span with no english_verdict "
         f"reported {len(probs)} problems, want 1: {probs}")
    beat = cheaper_than_shipped(mk([pin_miss], {}), "R4")
    want("E1b (must-FIRE consequence: and it would PUBLISH an endpoint)",
         beat and beat[0]["name"] == synth,
         "the unexcluded variant did not come back as a cheaper candidate, so "
         "E1 is not measuring the path that publishes the number")
    want("E1c (must-NOT-fire: excluded, the endpoint goes away)",
         not cheaper_than_shipped(
             mk([pin_miss], {synth: "out by English"}), "R4"),
         "an english_verdict did not remove the variant from "
         "cheaper_than_shipped, so the exclusion does not reach the number")

    want("E2 (must-FIRE: a falsy verdict string)",
         len(english_verdict_problems(
             mk([pin_miss], {synth: ""}), verdicts={synth: ""})) == 1,
         "an empty-string verdict read as an exclusion; _admissible tests "
         "`not r.get('english_verdict')`, so only a TRUTHY string excludes")

    want("E3 (must-FIRE: a typo'd key)",
         any("not a declared variant" in p for p in english_verdict_problems(
             mk([], {}), verdicts={"r4_no_wrappr": "typo"})),
         "a misspelled ENGLISH_VERDICTS key was accepted silently")

    want("E8 (must-NOT-fire: a DIFFERENT span of the SAME entry)",
         not english_verdict_problems(mk([other_miss], {}), verdicts={}),
         f"missing `{other_miss}` -- which the shipped R4 misses too, by design, "
         f"because the entry quotes it to describe safe_naive.rs -- was reported "
         f"as a problem. That is this file's first-draft defect and item 100's "
         f"class: the rule must key on the SPAN, not on the entry index")

    rows = mk([], {})
    rows[("R3", "v0_shipped")] = {
        "side": "R3", "name": "v0_shipped", "ir_per_call_small": 2085.04,
        "in_contract": True, "required_absent": [pin_miss],
        "english_verdict": None}
    rows[("R3", "r3_chunks_exact")] = {
        "side": "R3", "name": "r3_chunks_exact", "ir_per_call_small": 1957.0,
        "in_contract": True, "required_absent": [pin_miss],
        "english_verdict": None}
    c3 = cheapest_in_contract(rows, "R3")
    want("E4 (must-NOT-fire: the R3 half stays SEARCHED)",
         c3 and c3["name"] == "r3_chunks_exact"
         and bool(cheaper_than_shipped(rows, "R3")),
         "the R4-scoped ruling moved the R3 endpoint")
    want("E5 (must-NOT-fire: R3 misses an R4-scoped pin)",
         not any(" r3_" in p for p in english_verdict_problems(rows)),
         "an R3 variant missing the R4-scoped required[0] was reported as a "
         "problem -- that is check.py's measured 41-of-41 failure mode")

    rows[("CTL", "ctl_nowitness")] = {
        "side": "CTL", "name": "ctl_nowitness", "ir_per_call_small": 1941.0,
        "in_contract": True, "required_absent": [pin_miss],
        "english_verdict": "not a rung"}
    want("E6 (must-NOT-fire: the CTL side)",
         not any("ctl_nowitness" in p for p in english_verdict_problems(rows)),
         "a control was judged against an R4-scoped pin")
    want("E7 (must-NOT-fire: the REAL declaration is consistent)",
         not english_verdict_problems(mk([], {})),
         "the shipped ENGLISH_VERDICTS leaves a consistency problem")
    return bad


#: ⚠ Synthetic Verus sources for `gate_rule_selftest`. They are the minimum that
#: `harness/vparse.py` parses and `check.py::_is_trusted` classifies, and they are
#: module constants so the arms quote the same text the detector is handed.
_G_TRUSTED = """use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn g_get(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}
} // verus!
"""
_G_TWIN = """
verus! {
#[cfg(slb_twin)]
fn slb_twin_g_get(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}
} // verus!
"""
_G_STRAY = """
verus! {
fn g_other(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}
} // verus!
"""
_G_PLAIN = """use vstd::prelude::*;
verus! {
fn g_safe(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
{
    v[i]
}
} // verus!
"""


def gate_rule_selftest():
    """`[problem, ...]` -- the §H battery for `gate_refusals`, over synthetic
    VERUS SOURCE TEXT, run on every invocation.

    ⚠⚠ **THIS IS THE BATTERY THAT MATTERS MOST ON THIS ROW, BECAUSE
    `gate_refusals` IS WHAT MAKES `r4_endpoint_degenerate` TRUE.** A detector
    that silently stopped finding refusals would turn three gate-refused
    variants into three admissible ones and publish a moving R4 endpoint. A green
    run over the shipped sources cannot see that: all it proves is that the
    shipped twin is clean.

    **8 arms. 4 must-FIRE:**
      `G1` a trusted item with NO twin and a justification -> `5c-twin`;
      `G2` an `unsafe` token in a NON-trusted body -> `5-tcb-unsafe`;
      `G3` both at once -> BOTH stages, so one does not mask the other;
      `G4` an unparseable source -> `5-unparseable`, **because `[]` reads as
           admissible and that is the silent pass this file is written against.**

    **4 must-NOT-fire:**
      `G5` the same trusted item WITH its `slb_twin_` twin -- which also pins
           `TWIN_PREFIX` against drift, since a wrong prefix makes `G5` fire;
      `G6` an `unsafe` token INSIDE a trusted body;
      `G7` a source with no trusted item and no `unsafe` at all;
      `G8` `../verus.rs` ITSELF, read off disk, against `../spec.md`'s real
           `twin_justifications` -- the shipped configuration must come back
           clean, or this file's own R4 column is measuring the wrong thing."""
    bad = []

    def want(tag, cond, why):
        if not cond:
            bad.append(f"{tag}: {why}")

    def stages(src, just):
        return sorted(s for s, _d in gate_refusals(src, just)[0])

    j = {"g_get": "no twin is possible"}
    want("G1 (must-FIRE: justified trusted item, no twin)",
         stages(_G_TRUSTED, j) == ["5c-twin"],
         f"want exactly ['5c-twin'], got {stages(_G_TRUSTED, j)}")
    want("G2 (must-FIRE: unsafe outside every trusted body)",
         stages(_G_TRUSTED + _G_TWIN + _G_STRAY, j) == ["5-tcb-unsafe"],
         f"want exactly ['5-tcb-unsafe'], got "
         f"{stages(_G_TRUSTED + _G_TWIN + _G_STRAY, j)}")
    want("G3 (must-FIRE: both, and neither masks the other)",
         stages(_G_TRUSTED + _G_STRAY, j) == ["5-tcb-unsafe", "5c-twin"],
         f"want both stages, got {stages(_G_TRUSTED + _G_STRAY, j)}")
    st4, facts4 = gate_refusals("verus! { fn broken(", j)
    want("G4 (must-FIRE: an unparseable source REFUSES)",
         [s for s, _ in st4] == ["5-unparseable"] and facts4.get("parse_error"),
         f"a source vparse cannot parse returned {[s for s, _ in st4]} -- an "
         f"empty list here reads as ADMISSIBLE")
    want("G5 (must-NOT-fire: the twin is SEEN)",
         stages(_G_TRUSTED + _G_TWIN, j) == [],
         f"a trusted item WITH its {TWIN_PREFIX} twin was refused, got "
         f"{stages(_G_TRUSTED + _G_TWIN, j)} -- if TWIN_PREFIX has drifted from "
         f"harness/check.py's, this is the arm that says so")
    want("G6 (must-NOT-fire: unsafe INSIDE a trusted body)",
         "5-tcb-unsafe" not in stages(_G_TRUSTED + _G_TWIN, j),
         "the trusted item's own `unsafe` was reported as stray")
    want("G7 (must-NOT-fire: nothing trusted, nothing unsafe)",
         stages(_G_PLAIN, {}) == [],
         f"a source with no trusted item was refused, got "
         f"{stages(_G_PLAIN, {})}")
    vp = os.path.join(PDIR, "verus.rs")
    if not os.path.exists(vp):
        bad.append("G8: ../verus.rs is MISSING, so the shipped configuration "
                   "could not be checked and must not read as clean")
    else:
        real = justifications_for(contract())
        got = stages(open(vp, encoding="utf-8").read(), real)
        want("G8 (must-NOT-fire: the SHIPPED ../verus.rs)", got == [],
             f"the shipped twin is refused by {got}, so either the gate record "
             f"is wrong or this detector is -- and the gate record says "
             f"PASS-WITH-BLOCKED-ROWS")
    return bad


#: ⚠⚠ **THE ONE INPUT A VARIANT IS ALLOWED TO DISAGREE ON, AND IT IS DECLARED
#: PER (VARIANT, INPUT) RATHER THAN PER SIDE.**
#:
#: `controls/r4_nowitness.rs` IS `zend.c:243` with nothing between -- the defect
#: itself -- and `inputs/adversarial-dblfree.bin` is the blob `inputs/gen.py`
#: builds to exhibit the double free (`../NOTES.md` §5). ▶ **So the control MUST
#: diverge there, and an AGREEMENT would mean it had stopped being the defect.**
#: `checksum_problems` therefore enforces the divergence in BOTH directions.
#:
#: ⛔ **A BLANKET `if side == "CTL": continue` WOULD HAVE BEEN THE EASY ROUTE AND
#: IT IS THE WRONG ONE**, for the reason `PROTOCOL_PHP.md` §B2 gives about guards
#: generally: it exempts the whole class to excuse one cell, so a control that
#: silently started answering differently on a BENIGN input -- which would make
#: every figure taken from it incomparable -- would read as expected.
#: `ctl_r3_unchecked` is on the same side and is declared to agree EVERYWHERE.
DECLARED_DIVERGENCES = {
    ("CTL", "ctl_nowitness"): ("adversarial-dblfree.bin",),
}


def checksum_problems(rows, ref, declared=None):
    """`[problem, ...]` -- every variant returns the shipped checksum on every
    input, except where a divergence is DECLARED, and a declared divergence that
    fails to happen is a problem too.

    ⚠⚠ **THE SECOND HALF IS THE ONE THAT IS EASY TO LEAVE OUT**, and it is the
    half that keeps `witness_cost` honest: `../NOTES.md` §8g's figure is the cost
    of the witness, and it is only the cost of the witness while
    `controls/r4_nowitness.rs` really is the witness-free program. If that file
    were ever quietly repaired it would start agreeing everywhere, the comparison
    would become a comparison of one program with itself, and a one-directional
    check would print `ok` on all six inputs.

    ⚠ On this row agreement is a DECLARED property of the row and not a
    convenience: `../spec.md`'s `idiom.required[7]` says the six rungs agree bit
    for bit on the measured corpus and `harness/check.py` stage 2 checks it, so a
    divergence on `R3 v0_shipped` would be this control's defect rather than a
    variant's -- which the message says, because the two need different repairs."""
    declared = DECLARED_DIVERGENCES if declared is None else declared
    out = []
    for (side, name), r in sorted(rows.items()):
        ans = r.get("answers")
        if not ans:
            continue
        ok = tuple(declared.get((side, name)) or ())
        diff = sorted(k for k, v in ans.items() if ref.get(k) != v)
        undeclared = [k for k in diff if k not in ok]
        missing = [k for k in ok if k not in diff]
        if undeclared:
            out.append(
                f"{side} {name} changes the answer on {undeclared} and that "
                f"divergence is NOT declared in DECLARED_DIVERGENCES -- it is "
                f"not a respelling of this kernel"
                + (". ⚠ And on R3 v0_shipped this is the CONTROL's defect and "
                   "not a variant's: ../spec.md's idiom.required[7] declares "
                   "that the six rungs agree bit for bit on the measured corpus"
                   if (side, name) == ("R3", "v0_shipped") else ""))
        if missing:
            out.append(
                f"{side} {name} AGREES with the shipped checksum on {missing}, "
                f"where DECLARED_DIVERGENCES says it must DISAGREE. For "
                f"ctl_nowitness that means the witness-free control has stopped "
                f"being the defect, and every figure computed against it -- "
                f"witness_cost_pct_w1 -- is then a comparison of one program "
                f"with itself rather than a cost.")
    return out


def checksum_selftest():
    """`[problem, ...]` -- the §H battery for `checksum_problems`, on synthetic
    answer maps, run on every invocation.

    **6 arms. 3 must-FIRE:** `C1` an undeclared divergence on a rung variant;
    `C2` a DECLARED divergence that did not happen -- the direction a
    one-directional check misses; `C3` a divergence on `R3 v0_shipped`, which
    must name the CONTROL as the suspect and not the variant.
    **3 must-NOT-fire:** `C4` the declared divergence happening exactly as
    declared; `C5` a variant agreeing everywhere; `C6` a variant with no
    `answers` at all -- which is a BUILD failure already reported elsewhere and
    must not be double-counted here."""
    bad = []

    def want(t, cond, why):
        if not cond:
            bad.append(f"{t}: {why}")

    ref = {"small.bin": "1", "large.bin": "2", "adversarial-dblfree.bin": "3"}

    def mk(side, name, ans):
        return {(side, name): {"side": side, "name": name, "answers": ans}}

    p = checksum_problems(mk("R4", "r4_slot_byval", dict(ref, **{"small.bin": "9"})),
                          ref, {})
    want("C1 (must-FIRE: an undeclared divergence)",
         len(p) == 1 and "NOT declared" in p[0],
         f"an undeclared divergence reported {len(p)} problems: {p}")

    p = checksum_problems(mk("CTL", "ctl_nowitness", dict(ref)), ref,
                          {("CTL", "ctl_nowitness"): ("adversarial-dblfree.bin",)})
    want("C2 (must-FIRE: a DECLARED divergence that did NOT happen)",
         len(p) == 1 and "AGREES" in p[0],
         f"a control that stopped diverging reported {len(p)} problems: {p}")

    p = checksum_problems(mk("R3", "v0_shipped", dict(ref, **{"large.bin": "9"})),
                          ref, {})
    want("C3 (must-FIRE: and it names the CONTROL as the suspect)",
         len(p) == 1 and "required[7]" in p[0],
         f"a divergence on R3 v0_shipped did not name required[7]: {p}")

    p = checksum_problems(
        mk("CTL", "ctl_nowitness", dict(ref, **{"adversarial-dblfree.bin": "9"})),
        ref, {("CTL", "ctl_nowitness"): ("adversarial-dblfree.bin",)})
    want("C4 (must-NOT-fire: the declared divergence, exactly as declared)",
         not p, f"the declared divergence was reported as a problem: {p}")
    want("C5 (must-NOT-fire: a variant that agrees everywhere)",
         not checksum_problems(mk("R3", "r3_chunks_exact", dict(ref)), ref, {}),
         "a variant agreeing on every input was reported as a problem")
    want("C6 (must-NOT-fire: no answers at all)",
         not checksum_problems({("R4", "x"): {"side": "R4", "name": "x"}},
                               ref, {}),
         "a variant that did not build was double-counted here; its build "
         "failure is reported in stage 1")
    return bad


def r4_no_twin_reason(r):
    """Why an R4 variant with no twin file is inadmissible, or `None`.

    ⚠⚠ **A RULE AND NOT A SILENT SKIP.** `ph45`'s stage 4 does
    `if not r.get("verus_rs"): continue`, which leaves `in_contract` at whatever
    the audit set -- i.e. `True` -- for an R4 candidate that was never put
    through Verus at all."""
    if r.get("side") != "R4" or r.get("verus_rs"):
        return None
    return ("R4 with NO TWIN FILE: an R4 is a program whose obligations a "
            "prover can discharge, and nothing was put through Verus for this "
            "one. Inadmissible by rule, not by measurement.")


def twin_level(r):
    """`harness/asm.py::identity_level` between a variant's exec binary and its
    twin's, or `None` if either is missing.

    ⚠ `None` is NOT agreement. A missing field must not read as *byte-identical*:
    the digest of an empty disassembly is a constant, so `None == None` is one of
    the two ways a naive check says *identical* about two things that were never
    compared."""
    a, b = r.get("exe"), r.get("verus_exe")
    if not a or not b or not os.path.exists(a) or not os.path.exists(b):
        return None, None
    A = load_asm()
    lvl, ev = A.identity_level(A.kernel(a), A.kernel(b))
    return lvl, {k: ev[k] for k in ("counts_a", "counts_b", "md5_raw_equal")}


def meets_level(level, required, levels=None):
    """Is `level` at least as strong as `required`, in `asm.py`'s own ordering?

    ⚠ `None` is FALSE, not "not applicable". `differ` as a requirement is met by
    anything, which is what makes the `O0` pin on this row vacuous and the `O3`
    one not."""
    levels = (load_asm().IDENTITY_LEVELS if levels is None else levels)
    if level not in levels or required not in levels:
        return False
    return levels.index(level) >= levels.index(required)


def byte_identical_pair(rows, a, b, side="R3"):
    """Whether two EXEC variants on one side compile to the same `kernel`, by
    `kernel_shape`'s digest AND instruction count, both built side by side in
    `SCRATCH`.

    ⭐ This is what makes `r3_oprec_array == r3_oprec_slice` a BYTE-IDENTITY
    claim rather than a tie, which is the sharper form of `ph45` §5.6's result.
    ⚠ It refuses a missing field and refuses the empty-disassembly digest, which
    two distinct non-existent binaries would SHARE."""
    ra, rb = rows.get((side, a)), rows.get((side, b))
    if not ra or not rb:
        return False
    da, db = ra.get("kernel_digest"), rb.get("kernel_digest")
    na, nb = ra.get("kernel_insns"), rb.get("kernel_insns")
    if None in (da, db, na, nb) or 0 in (na, nb) or _EMPTY_MD5 in (da, db):
        return False
    return da == db and na == nb


def _admissible(rows, side, key):
    """In-contract, English-clear, gate-clear, PRICED candidates on one side.

    ⚠⚠ **FOUR FIELDS, AND READING ANY ONE ALONE GIVES THE WRONG ANSWER**
    (`.memory-php/02-ladder.md`, item 90: `_043` read `in_contract: true` and
    concluded a variant was admitted when an `english_verdict` had already
    excluded it). `gate_refusals` is the third and it is new on this row: a rung
    `harness/check.py` would refuse cannot ship, whatever its number is."""
    return [r for r in rows.values()
            if r.get("side") == side and r.get("in_contract")
            and not r.get("english_verdict") and not r.get("gate_refusals")
            and r.get(key) is not None]


def cheapest_in_contract(rows, side="R3", key="ir_per_call_small"):
    """The cheapest ADMISSIBLE candidate on one side, or `None`.

    ⚠ `key` defaults to **A1**, and that default is MEASURED rather than
    stylistic: stage 2b computes `inside_share` per cell and it is ~98.6 % on
    every Rust cell of this row, so `kernel` carries the difference. On `ph45`
    A1 is identical for every variant on a side and a `min` over it would return
    the enumeration order; `a1_spread_pp` and `wp_spread_pp` are both in the
    sidecar so a reader can check that this default is still the right one."""
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
    """Every ADMISSIBLE candidate on one side that beats its shipped rung by MORE
    than `tie_pct`, cheapest first. Empty means that endpoint is DEGENERATE --
    which is `ph07`'s and `ph16`'s answer, and on the R4 side it is this row's."""
    if side not in RUNG_SIDES:
        return []
    base = rows.get((side, "v0_shipped"), {}).get(key)
    if not base:
        return []
    out = [r for r in _admissible(rows, side, key)
           if r.get("name") != "v0_shipped"
           and (base - r[key]) / base * 100.0 > tie_pct]
    return sorted(out, key=lambda r: r[key])


def smaller_surface(rows, side="R4", include_refused=True):
    """Candidates whose `external_body` count is strictly smaller than the
    shipped rung's, cheapest first.

    ⚠⚠ **`include_refused` DEFAULTS TO TRUE AND THAT IS THIS ROW'S RESULT, NOT A
    LOOSENING.** Every trusted-surface reduction found here is refused by a GATE
    STAGE rather than by cost or by contract, and a list that silently dropped
    them would report *"no smaller surface exists"* where the truth is *"three
    exist and the harness refuses all three"*. Each row's `gate_refusals` travels
    with it, and `_admissible` is still what decides what may be called a rung.
    ⚠ Keyed on `external_body` items and not on call sites, because an accessor
    that is defined and never called is still in the trusted base."""
    base = rows.get((side, "v0_shipped"), {}).get("external_body_items")
    if base is None:
        return []
    cand = [r for r in rows.values()
            if r.get("side") == side and r.get("in_contract")
            and not r.get("english_verdict")
            and (include_refused or not r.get("gate_refusals"))
            and r.get("external_body_items") is not None
            and r["external_body_items"] < base
            and r.get("ir_per_call_small") is not None]
    return sorted(cand, key=lambda r: r["ir_per_call_small"])


def witness_cost(rows, name="v0_shipped", key="ir_per_call_small_wp"):
    """What the coverage witness costs, against `ctl_nowitness` in THIS pipeline.

    ⭐ `../NOTES.md` §8g publishes **`+0.622 %`** W1 / **`+0.632 %`** B1 for the
    shipped two-`bool` witness against `controls/r4_nowitness.rs`, and computing
    it here from two cells of ONE run is what makes it comparable with `ph53`'s
    `+21.775 %`. ⚠ The base is a RUST control and NOT the C -- F98's four
    qualifiers."""
    base = rows.get(("CTL", "ctl_nowitness"), {}).get(key)
    r = rows.get(("R4", name), {}).get(key)
    if not base or r is None:
        return None
    return 100.0 * (r - base) / base


def inside_share(r):
    """`100 * A1 / W1` for one cell -- `.memory-php/03-numbers.md`'s own
    statistic, recomputed here per cell rather than inherited.

    ⭐ It is what decides which family can resolve a respelling, and the entry
    that matters is the last one in that file: **`inside_share` is PER-CELL, not
    per-row.** `../NOTES.md` §8a measures **22.24 %** on `c-gcc` and publishes
    the ROW in W1 on that basis, correctly; the Rust cells are a different
    number and this function is what shows it rather than asserting it."""
    a, w = r.get("ir_per_call_small"), r.get("ir_per_call_small_wp")
    if not a or not w:
        return None
    return 100.0 * a / w


def _spread(rows, key, side, only_admissible=False):
    vals = [r[key] for r in rows.values()
            if r.get("side") == side and r.get(key) is not None
            and (not only_admissible
                 or (r.get("in_contract") and not r.get("english_verdict")
                     and not r.get("gate_refusals")))]
    return None if not vals else round(max(vals) - min(vals), 6)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit-only", action="store_true",
                    help="the spelling audit and both §H batteries; no build, "
                         "no callgrind, no Verus")
    ap.add_argument("--verus", action="store_true",
                    help="stage 4: put every R4 twin through Verus and compute "
                         "its identity level against its exec rung")
    args = ap.parse_args()

    os.makedirs(SCRATCH, exist_ok=True)
    chk = load_check()
    con = contract()
    decl = con["idiom"]
    just = justifications_for(con)
    problems = []
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("spellings.py: no .bin -- run inputs/gen.py first", file=sys.stderr)
        return 1

    pinned, measured = identity_premise()
    need_level, ident_why = admissibility(pinned, measured)
    print("0a. THE `identity` PREMISE, READ FROM BOTH THE PIN AND THE RECORD")
    print(f"  ../spec.md                pinned   {pinned}")
    print(f"  results-php/gate/...json  measured {measured}")
    print(f"  -> required twin level at O3: `{need_level}`")
    print(f"     {ident_why}")
    if pinned.get("O3") != measured.get("O3"):
        problems.append(
            f"the `identity` pin (O3 {pinned.get('O3')!r}) and the gate record "
            f"(O3 {measured.get('O3')!r}) DISAGREE, so this file cannot tell "
            f"which admissibility rule applies to an R4 candidate and fell back "
            f"to the weaker one")

    variants = ([(n, s, w, subs, e) for n, s, w, subs, e in R3_VARIANTS]
                + [(n, s, w, subs, e) for n, s, w, subs, e in R4_VARIANTS]
                + [(n, s, w, subs, e) for n, s, w, subs, e in CTL_VARIANTS]
                + [(n, s, w, p, e) for n, s, w, p, e in FILE_VARIANTS])
    # ⛔⛔ THE FIXED-WIDTH SLUG -- see `_SLUGS`. Assigned in declaration order so
    # the mapping is stable across runs, and two digits because `%02d` is what
    # keeps every exec source path the SAME LENGTH, which is what makes
    # `kernel_shape`'s digest a claim about code rather than about the filename.
    assert len(variants) < 100, (
        "more than 99 variants: the `vNN` slug is no longer fixed-width, so "
        "kernel_shape's digest becomes path-sensitive again (F101). Widen the "
        "slug, do not drop the assertion.")
    _SLUGS.clear()
    for i, (n, s, _w, _su, _e) in enumerate(variants):
        _SLUGS[(s, n)] = f"v{i:02d}"
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

    # ---- §H: both batteries, on every invocation ----------------------------
    # ⚠⚠ THREE DIFFERENT CHECKS. The two selftests drive the verdict functions
    # over SYNTHETIC inputs, which is the only way to see the arms fire -- the
    # shipped tree's `problems` is empty, so a green run is not evidence that any
    # of this CAN fire (check.py's own argument for `_CONTROL_VERDICT_CASES`).
    # The consistency check then runs on the REAL rows.
    st = english_verdict_selftest()
    gt = gate_rule_selftest()
    ct = checksum_selftest()
    ev = english_verdict_problems(rows)
    print(f"\n0c. §H -- THE NEGATIVES, INSIDE THE VALIDATOR "
          f"(PROTOCOL_PHP.md §H, RECAP_PHP.md item 97).\n"
          f"  english_verdict_selftest  {'PASS' if not st else 'FAIL'}   "
          f"10 arms over synthetic rows (4 must-FIRE, 6 must-NOT-fire)\n"
          f"  gate_rule_selftest        {'PASS' if not gt else 'FAIL'}   "
          f"8 arms over synthetic verus sources (4 must-FIRE, 4 must-NOT-fire)\n"
          f"  checksum_selftest         {'PASS' if not ct else 'FAIL'}   "
          f"6 arms over synthetic answer maps (3 must-FIRE, 3 must-NOT-fire)\n"
          f"  consistency (real rows)   {'ok  ' if not ev else 'FAIL'}   "
          f"the pin is {WITNESS_PIN[0]}.rust's SPAN `{WITNESS_PIN[1]}`, scoped "
          f"to side {WITNESS_PIN[2]};\n"
          f"                                  every {WITNESS_PIN[2]} variant "
          f"that misses THAT span carries a verdict\n"
          f"  ENGLISH_VERDICTS          "
          + (", ".join(sorted(ENGLISH_VERDICTS))
             or "EMPTY -- no variant here drops a backticked `required` span; "
                "see the constant's own note"))
    for p in st + gt + ct + ev:
        print(f"    *** {p}")
    problems.extend(st)
    problems.extend(gt)
    problems.extend(ct)
    problems.extend(ev)

    if args.audit_only:
        for p in problems:
            print(f"  *** {p}", file=sys.stderr)
        return 1 if problems else 0

    print("\n1. BUILD + CHECKSUM + KERNEL SHAPE + TRUSTED SURFACE.\n"
          "   ⚠ ONE reference for every side: ../spec.md's idiom.required[7] "
          "declares that all\n   six rungs agree bit for bit on the measured "
          "corpus and check.py stage 2 checks\n   it, so R4 v0_shipped is the "
          "reference and R3 v0_shipped is ASSERTED against it.")
    ref = None
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        exe, err = build(r["rs"],
                         os.path.join(SCRATCH, f"{slug(side, name)}.bin"))
        r["built"] = exe is not None
        r["build_error"] = err
        if not exe:
            print(f"  {side} {name:18s} BUILD FAILED")
            problems.append(f"{side} {name} does not build: {err}")
            continue
        r["exe"] = exe
        (r["kernel_insns"], r["kernel_panic_calls"],
         r["kernel_digest"]) = kernel_shape(exe)
        # ⚠ RE-READ FROM THE FILE rather than reusing the `src` from the audit
        # loop: `TASK_PHP_037` §6.2 found exactly that bug in this function's
        # ancestor, where every variant reported the LAST audited variant's
        # count. A plausible wrong number, not an error.
        vsrc = open(r["rs"], encoding="utf-8").read()
        (r["trusted_call_sites"], r["accessors_defined"],
         r["accessor_names"]) = trusted_accessors(vsrc)
        r["unsafe_tokens"] = unsafe_tokens(vsrc)
        if side == "R3" and r["unsafe_tokens"]:
            problems.append(
                f"R3 {name} contains {r['unsafe_tokens']} `unsafe` token(s). An "
                f"R3 is SAFE Rust (.memory/01-ladder.md), so this is not a "
                f"respelling of safe_tuned.rs -- it belongs on the CTL side, "
                f"which is where ctl_r3_unchecked is declared.")
            r["in_contract"] = False
        if r["verus_rs"]:
            tw = open(r["verus_rs"], encoding="utf-8").read()
            r["external_body_items"] = external_body_items(tw)
            refus, facts = gate_refusals(tw, just)
            r["gate_refusals"] = [s for s, _d in refus]
            r["gate_refusal_detail"] = [d for _s, d in refus]
            r["gate_facts"] = facts
        ans = {os.path.basename(p): run(exe, p) for p in inputs}
        r["answers"] = ans
        if (side, name) == ("R4", "v0_shipped"):
            ref = ans
        print(f"  {side} {name:18s} "
              + (f"kernel {r['kernel_insns']:4d} insns, "
                 f"{r['kernel_panic_calls']} panic site(s) {r['kernel_digest']}")
              + f"   unsafe {r['unsafe_tokens']:2d}"
              + f"   accessors {r['trusted_call_sites']:2d}/"
                f"{r['accessors_defined']}"
              + (f"   eb {r['external_body_items']}"
                 if r.get("external_body_items") is not None else "")
              + ("   GATE-REFUSED: " + ",".join(r["gate_refusals"])
                 if r.get("gate_refusals") else ""))
    # ⛔⛔ THE EQUAL-LENGTH PATH INVARIANT, ASSERTED AND NOT ASSUMED -- F101.
    # `kernel_shape`'s digest keeps rip-relative displacements, and `rustc` puts
    # the source path into panic-location data, so a digest comparison between
    # two binaries built from paths of different LENGTH is not a comparison of
    # code. See `_SLUGS` for the two wrong answers this produced in this file's
    # own first run.
    lens = {len(r["rs"]) for r in rows.values() if r.get("rs")}
    print(f"\n   exec source paths: {len(lens)} distinct length(s) "
          f"{sorted(lens)} -- must be 1, or kernel_digest is path-sensitive "
          f"(F101)")
    if len(lens) != 1:
        problems.append(
            f"the scratch exec sources have {len(lens)} distinct path lengths "
            f"{sorted(lens)}, so `kernel_digest` comparisons between variants "
            f"are PATH-SENSITIVE and not claims about code (F101). The `vNN` "
            f"slug exists to make this one number; fix the naming, not this "
            f"check.")

    if ref is None:
        problems.append("R4 v0_shipped did not build, so there is NO reference "
                        "checksum and no variant's answer was compared -- that "
                        "must not read as a pass")
    else:
        print("\n   checksum against R4 v0_shipped, all "
              f"{len(ref)} shipped inputs "
              f"(⚠ declared divergences: "
              + ("; ".join(f"{s} {n} on {list(v)}"
                           for (s, n), v in sorted(DECLARED_DIVERGENCES.items()))
                 or "none") + "):")
        cp = checksum_problems(rows, ref)
        for name, side, why, subs, eng in variants:
            r = rows[(side, name)]
            if not r.get("answers"):
                continue
            diff = sorted(k for k, v in r["answers"].items() if ref.get(k) != v)
            ok = tuple(DECLARED_DIVERGENCES.get((side, name)) or ())
            bad_here = [p for p in cp if p.startswith(f"{side} {name} ")]
            r["diverges_on"] = diff
            r["declared_divergences"] = list(ok)
            print(f"     {side} {name:18s} "
                  + ("ok" if not diff
                     else (f"DIFFERS on {diff} -- DECLARED" if not bad_here
                           else f"*** DIFFERS on {diff}")))
            if bad_here:
                r["in_contract"] = False
        problems.extend(cp)

    print("\n2. THE PRICE -- BOTH FAMILIES, from ONE callgrind run per cell.\n"
          "   A1 = kernel_exclusive_ir/call (measure.py's own statistic, "
          "IMPORTED) -- THE HEADLINE\n        FOR THIS SEARCH.\n"
          "   W1 = whole-program Ir/call (callgrind's PROGRAM TOTALS) -- the "
          "family the ROW\n        publishes (../NOTES.md §9), quoted labelled "
          "beside every figure.")
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
        own = b3a if side in ("R3",) or name.startswith("ctl_r3") else b4a
        r["pct_vs_r4ship_a1"] = (100.0 * (r["ir_per_call_small"] - b4a) / b4a
                                 if b4a else None)
        r["pct_vs_r4ship_wp"] = (
            100.0 * (r["ir_per_call_small_wp"] - b4w) / b4w if b4w else None)
        r["pct_vs_own_side_a1"] = (
            100.0 * (r["ir_per_call_small"] - own) / own if own else None)
        print(f"  {side + ' ' + name:26s} {r['pct_vs_r4ship_a1']:+13.2f}% "
              f"{r['pct_vs_r4ship_wp']:+13.2f}% "
              f"{r['pct_vs_own_side_a1']:+14.2f}%")

    print("\n2b. WHICH FAMILY CAN RESOLVE THIS? `inside_share` PER CELL, "
          "recomputed here.\n    ⛔ ../NOTES.md §8a measures 22.24 % on `c-gcc` "
          "and publishes the ROW in W1 on\n    that basis, CORRECTLY. "
          "`.memory-php/03-numbers.md`: inside_share is PER-CELL.")
    shares = {}
    for name, side, why, subs, eng in variants:
        r = rows[(side, name)]
        s = inside_share(r)
        if s is None:
            continue
        shares[f"{side}_{name}"] = round(s, 4)
        r["inside_share_pct"] = round(s, 4)
    if shares:
        lo, hi = min(shares.values()), max(shares.values())
        print(f"    A1/W1 over {len(shares)} Rust cell(s): {lo:.2f} % .. "
              f"{hi:.2f} %   -> A1 is the resolving family for this search")
        if lo < 50.0:
            problems.append(
                f"inside_share falls to {lo:.2f} % on some Rust cell, so A1 "
                f"cannot be assumed to resolve this search -- the headline "
                f"choice in this file's docstring rests on it being ~98.6 %")

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
            g = rows[(side, "v0_shipped")].get(
                "ir_per_call_small_wp" if inp == "small.bin"
                else "ir_per_call_large_wp")
            if g is None:
                print(f"  W1 {cell:12s} {inp:10s} NOT MEASURED")
                rec_ok = False
                problems.append(f"W1 {cell}/{inp}: NOT MEASURED")
                continue
            w = tot / float(nit[inp])
            d = abs(w - g) / w * 100.0
            print(f"  W1 {cell:12s} {inp:10s} NOTES.md §8={w:12.4f} "
                  f"here={g:12.4f}  delta={d:.4f}%")
            if d > 0.5:
                rec_ok = False
                problems.append(
                    f"W1 {cell}/{inp}: this pipeline measures {g:.4f} Ir/call "
                    f"whole-program where NOTES.md section 8 publishes {w:.4f} "
                    f"({d:.2f}% apart)")
    else:
        print(f"  no measurement record at {RECORD}")

    if args.verus:
        print(f"\n4. R4 ADMISSIBILITY -- THREE SEPARATE QUESTIONS, ALL "
              f"RECORDED.\n"
              f"   (a) does the twin VERIFY?  ⚠ READ THE ERROR TEXT: "
              f"`is not supported` /\n       `does not yet support` disqualify; "
              f"a failed postcondition is proof work.\n"
              f"   (b) does the twin reach `{need_level}` against its exec rung, "
              f"by\n       harness/asm.py::identity_level?  ⚠ `norel` is NOT "
              f"byte identity.\n"
              f"   (c) would harness/check.py REFUSE the configuration? -- "
              f"stage 1's column.")
        for name, side, why, subs, eng in R4_VARIANTS:
            r = rows[(side, name)]
            reason = r4_no_twin_reason(r)
            if reason:
                r["in_contract"] = False
                r["verus_msg"] = reason
                print(f"  R4 {name:18s} NO TWIN          {reason[:70]}")
                continue
            ok, msg = verus_ok(r["verus_rs"])
            r["verus_verifies"], r["verus_msg"] = ok, msg
            r["verus_unsupported"] = bool(msg and msg.startswith("DISQUALIFIED"))
            if ok:
                vexe, verr = build_verus(
                    r["verus_rs"],
                    os.path.join(SCRATCH, f"{slug(side, name)}_twin.bin"))
                if not vexe:
                    r["verus_build_error"] = verr
                    problems.append(f"R4 {name}: the twin VERIFIES but does not "
                                    f"compile: {verr}")
                else:
                    r["verus_exe"] = vexe
                    (r["verus_kernel_insns"], r["verus_kernel_panic_calls"],
                     r["verus_kernel_digest"]) = kernel_shape(vexe)
            lvl, ev = twin_level(r)
            r["twin_identity_level"] = lvl
            r["twin_identity_evidence"] = ev
            r["twin_identity_meets_pin"] = meets_level(lvl, need_level)
            if not ok or not r["twin_identity_meets_pin"]:
                r["in_contract"] = False
            print(f"  R4 {name:18s} "
                  + ("VERIFIES    " if ok else "NO           ")
                  + f"{(msg.splitlines()[0][:34] if msg else ''):34s} "
                  + f"identity {str(lvl):7s} "
                  + ("meets " if r["twin_identity_meets_pin"] else "BELOW ")
                  + f"`{need_level}`"
                  + ("   GATE-REFUSED: " + ",".join(r["gate_refusals"])
                     if r.get("gate_refusals") else ""))
            if name == "v0_shipped" and not ok:
                problems.append(
                    "R4 v0_shipped's own twin does not verify -- this pipeline "
                    "is not measuring the shipped rung")
            if name == "v0_shipped" and not r["twin_identity_meets_pin"]:
                problems.append(
                    f"R4 v0_shipped's twin reaches `{lvl}` against its exec "
                    f"rung where ../spec.md pins `{need_level}` -- the bar this "
                    f"file applies to every candidate is then one the SHIPPED "
                    f"rung does not meet, which is this file's defect and not "
                    f"the candidates'")
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
                           "THE HEADLINE FOR THIS SEARCH",
                           "ir_per_call_small", "pct_vs_r4ship_a1"),
                          ("W1  (whole-program  Ir/call, small.bin) -- "
                           "the family the ROW publishes",
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
                # branch in family A1; this row does not, and the branch is kept
                # because the next row might.
                print(f"  R3-side span     ⚠ NOT COMPUTABLE IN THIS FAMILY: "
                      f"every admissible R3 variant\n                   "
                      f"measures {lo[pct]:+.2f}% here, within the {TIE_PCT}% "
                      f"tie threshold of each other.")
            else:
                print(f"  R3-side span     cheapest-found .. dearest-found in "
                      f"contract  {lo[pct]:+.2f}% .. {hi[pct]:+.2f}%"
                      f"   `{lo['name']}` .. `{hi['name']}`")
    print("\n  ⚠⚠ NO PAIR INTERVAL. `min(R3 found) - min(R4 found)` differences "
          "two upper bounds\n     and bounds nothing in either direction "
          "(ph03's hashed `why` retracts it). Where\n     this file says the "
          "ORDERING changes it means ordering, never interval.")

    beat3 = cheaper_than_shipped(rows, "R3")
    beat4 = cheaper_than_shipped(rows, "R4")
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
                  + (f"   eb {r['external_body_items']}"
                     if r.get("external_body_items") is not None else "")
                  + f"   {r['kernel_panic_calls']} panic site(s)")
        for (s, nm), r in sorted(rows.items()):
            if s == side and (not r.get("in_contract")
                              or r.get("english_verdict")
                              or r.get("gate_refusals")):
                print(f"      {nm:18s} INADMISSIBLE -- "
                      + ("GATE REFUSES IT (" + ",".join(r["gate_refusals"]) + ")"
                         if r.get("gate_refusals")
                         else (r.get("english_verdict") or r.get("verus_msg")
                               or "see stage 0b/1"))[:96]
                      + (f"   [priced: A1 {r['ir_per_call_small']:.3f}, "
                         f"{r['pct_vs_own_side_a1']:+.2f}% vs shipped {side}]"
                         if r.get("ir_per_call_small") is not None else ""))
    print("\n  ⚠ THE CONTROLS, PRICED AND NEVER RANKED (side CTL):")
    for (s, nm), r in sorted(rows.items()):
        if s != "CTL" or r.get("ir_per_call_small") is None:
            continue
        print(f"      {nm:18s} {r['ir_per_call_small']:10.3f} Ir/call A1   "
              f"{r['pct_vs_own_side_a1']:+7.2f}% vs its own side's shipped rung"
              f"   {r['kernel_panic_calls']} panic site(s)")

    if not beat4:
        print("\n  ⭐ NO CHEAPER ADMISSIBLE R4 WAS FOUND: the R4 endpoint is "
              "DEGENERATE on this row,\n     as it is on ph07 and ph16.")
    else:
        print(f"\n  ⚠⚠ A CHEAPER ADMISSIBLE R4 EXISTS -- `{beat4[0]['name']}`, "
              f"{beat4[0]['pct_vs_own_side_a1']:+.2f}% A1 against the shipped "
              f"R4.\n     ⚠ The rung does NOT move: "
              f"`.memory/02-bench-rules.md` holds R4 fixed by fiat\n     and "
              f"that fiat is what makes the bound a bound.")
    if small:
        print(f"  ⚠⚠ AND {len(small)} VARIANT(S) HAVE A SMALLER TRUSTED BASE "
              f"than the shipped rung's\n     "
              f"{r4s.get('external_body_items')} `external_body` items -- "
              f"AND THE GATE REFUSES THEM:")
        for r in small:
            print(f"      {r['name']:18s} eb {r['external_body_items']}  "
                  f"{r['pct_vs_own_side_a1']:+7.2f}% A1   "
                  + (",".join(r["gate_refusals"]) if r.get("gate_refusals")
                     else "ADMISSIBLE"))
        print("     ⛔⛔ NOTHING HERE ENLARGES THE TRUSTED BASE TO SATISFY A "
              "STAGE. That is\n        cost-selection on the TCB axis (F104, "
              "item 105) and the TCB is a published\n        axis. If a variant "
              "with a LARGER trusted base were cheaper, that would be a\n"
              "        RESULT to report and not a rung to ship.")
    if beat3:
        print(f"  ⭐⭐ AND THE R3 SIDE MOVES -- `{beat3[0]['name']}`, "
              f"{beat3[0]['pct_vs_own_side_a1']:+.2f}% A1 against the shipped "
              f"R3.\n     **THE PUBLISHED R3 ENDPOINT IS NOT A SEARCHED "
              f"ENDPOINT.**")
        c3 = cheapest_in_contract(rows, "R3")
        c4 = cheapest_in_contract(rows, "R4")
        if c3 and c4:
            print(f"     ⚠ ORDERING UNDER SEARCH (not an interval): cheapest "
                  f"R3 `{c3['name']}` {c3['ir_per_call_small']:.3f} vs cheapest "
                  f"R4\n       `{c4['name']}` {c4['ir_per_call_small']:.3f} "
                  f"Ir/call -- "
                  + ("R3 cheaper" if c3["ir_per_call_small"]
                     < c4["ir_per_call_small"] else "R4 still cheaper")
                  + f", where the shipped bound says R3 is "
                    f"{r3s['pct_vs_r4ship_a1']:+.2f}%.")

    print("\n6. THE MECHANISM, FROM THE PANIC-SITE COLUMN (§F8: a cost with no "
          "mechanism is an\n   incomplete row). Every helper is "
          "#[inline(always)], so a `call` inside `kernel` can\n   only be a "
          "panic path: the count IS the surviving bounds checks plus one for\n"
          "   the window slice.")
    ops_per_call = None
    for c in (json.load(open(RECORD)).get("inputs") or {}).items() \
            if os.path.exists(RECORD) else []:
        pass
    per = []
    for (s, nm), r in sorted(rows.items()):
        if r.get("kernel_panic_calls") is None:
            continue
        per.append((s, nm, r["kernel_panic_calls"], r["kernel_insns"],
                    r.get("ir_per_call_small")))
    for s, nm, pc, ni, a1 in per:
        print(f"    {s} {nm:18s} {pc} panic site(s)  {ni:4d} insns"
              + (f"  {a1:10.3f} Ir/call A1" if a1 else ""))
    gap = None
    if b3a and b4a:
        gap = b3a - b4a
        print(f"\n    shipped R3 - shipped R4 = {gap:.2f} Ir/call A1. The "
              f"shipped R3 carries FOUR more\n    panic sites than the shipped "
              f"R4 and each is a `cmp`/`je` pair in the hot loop:\n    "
              f"8 instructions per op. `inputs/small.bin` runs cap = "
              f"(74 - 8) / 4 = 16 ops per\n    call, so the static prediction "
              f"is 8 * 16 = 128.00 Ir/call, i.e. "
              f"{100.0 * 128.0 / gap:.1f} %\n    of the measured gap.")

    wship = witness_cost(rows)
    print("\n7. THE COVERAGE WITNESS, RE-PRICED IN ONE PIPELINE "
          "(../NOTES.md §8g).")
    print(f"  shipped two-`bool` witness   "
          + (f"{wship:+.3f}% W1" if wship is not None else "NOT MEASURED")
          + "  against ctl_nowitness   (§8g publishes +0.622 %)")
    print("  ⚠ small.bin, O3/isolated, W1, against a RUST control and NOT the "
          "C -- F98's four\n    qualifiers. ⛔ AND IT IS A CEILING ON THE ONE "
          "R4 LEVER THIS FILE DID NOT BUILD:\n    ph53's u32-bitmask witness "
          "bought -11.40 % A1 because its witness is an ARRAY,\n    one byte "
          "per slot, re-read per consumer iteration. ph52's is TWO bools for "
          "the\n    whole kernel, so a perfectly FREE witness could buy at most "
          "the figure above.\n    That is an UNTESTED bound and not a "
          "measurement of a variant.")

    doc = {
        "pin": {
            "regenerate":
                "python3 patterns-php/ph52-concat-copy-uninit/controls/"
                "spellings.py --verus",
            "note":
                "The pin covers the two rung sources the variants are derived "
                "from, verus.rs (the R4 admissibility half), spec.md (the "
                "declaration the audit runs against AND the `identity` pin the "
                "admissibility rule reads AND the twin_justifications "
                "gate_refusals reads), NOTES.md (whose sections 8c/8d carry the "
                "two whole-program totals stage 3 reproduces), inputs/gen.py "
                "(the corpus every number is measured over), the two controls/ "
                "files that are variants, and this script. It does NOT cover "
                "results-php/ph52-concat-copy-uninit.json: stage 3 compares "
                "against that record at run time and prints the delta, which is "
                "a stronger check than a hash of it."},
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
                        "controls/r4_nowitness.rs", "controls/mu_unwrapped.rs",
                        "controls/spellings.py")},
        "scratch_slug": {f"{s_}_{n_}": v for (s_, n_), v in _SLUGS.items()},
        "probes": [{"input": i, "stride": st, "n_iters": n}
                   for i, st, n in PROBES],
        "tie_pct": TIE_PCT,
        "verus_checked": bool(args.verus),
        "identity_pinned": pinned,
        "identity_measured": measured,
        "identity_required_twin_level": need_level,
        "identity_checked": ident_why,
        "statistic":
            "TWO FAMILIES, BOTH PUBLISHED, from one callgrind run per cell. A1 "
            "= kernel_exclusive_ir / n_iters -- harness/measure.py::_sum_rows "
            "itself, IMPORTED and not transcribed -- which stage 3 compares "
            "against results-php/ph52-concat-copy-uninit.json in FOUR cells. W1 "
            "= whole-program Ir / n_iters off callgrind_annotate's PROGRAM "
            "TOTALS, which stage 3 compares against NOTES.md sections 8c and 8d "
            "in TWO cells. ⭐ A1 IS THE HEADLINE FOR THIS SEARCH AND W1 IS THE "
            "HEADLINE FOR THE ROW, AND BOTH ARE RIGHT: .memory-php/03-numbers.md "
            "records that inside_share is PER-CELL, NOTES.md section 8a "
            "measures 22.24 per cent on the C rungs -- PH52_NOINLINE puts three "
            "callees in their own symbols, 62.35 per cent of the program -- and "
            "the Rust rungs inline everything, so inside_share_pct below is "
            "about 98.6 per cent on every cell this search touches. Stage 2b "
            "recomputes it rather than inheriting it, and raises a problem if it "
            "ever falls below 50 per cent. Every percentage here is small.bin, "
            "O3/isolated, against the named base -- F98's four qualifiers.",
        "headline_statistic": "ir_per_call_small",
        "row_headline_statistic": "ir_per_call_small_wp",
        "inside_share_pct_by_cell": shares,
        "reproduces_shipped_record": rec_ok,
        "reproduces_shipped_record_scope":
            "TWO Ir FAMILIES AT 0.5 PER CENT TOLERANCE, AND NOT THE STATIC "
            "COUNTS. A1 is compared against "
            "results-php/ph52-concat-copy-uninit.json in four cells "
            "(safe_tuned and unsafe, small.bin and large.bin) and W1 against "
            "NOTES.md section 8c (R3, 52829203) and section 8d (R4, 49549469). "
            "`kernel_insns` below is a raw disassembled instruction count over "
            "the `kernel` symbol INCLUDING the int3 pad and is NOT comparable "
            "to the gate record's n_fn_nopad (444 against 425). The tolerance "
            "is not equality because .memory-php/03-numbers.md item 99 measured "
            "the whole-program column moving by a constant 14-28 Ir between "
            "runs -- the argv/env block -- which NOTES.md section 8d sees as "
            "the +40 Ir between R4 and R5.",
        "r3_endpoint_degenerate": not beat3,
        "r4_endpoint_degenerate": not beat4,
        "r4_endpoint_degenerate_ignoring_gate_rules": not [
            r for r in rows.values()
            if r.get("side") == "R4" and r.get("name") != "v0_shipped"
            and r.get("in_contract") and not r.get("english_verdict")
            and r.get("ir_per_call_small") is not None and b4a
            and (b4a - r["ir_per_call_small"]) / b4a * 100.0 > TIE_PCT],
        "r4_endpoint_note":
            "BOTH FIELDS ARE TRUE ON THIS ROW AND THAT IS THE RESULT. No R4 "
            "variant priced here is cheaper than the shipped rung by more than "
            "tie_pct with OR without the gate-rule filter, so the R4 endpoint is "
            "degenerate on COST, as ph07's and ph16's are. What the gate-rule "
            "filter changes is the TRUSTED-SURFACE column, not the cost one: "
            "all three variants with a smaller external_body count are refused "
            "by harness/check.py, two by stage 5c-twin's n_twins == 0 rule "
            "(F104) and one by _scan_unsafe_sites (F97). ⛔ NOTHING HERE "
            "ENLARGES THE TRUSTED BASE TO SATISFY A STAGE: that is "
            "cost-selection on the TCB axis and the TCB is a published axis of "
            "this project.",
        "cheapest_r3_in_contract": (cheapest_in_contract(rows, "R3") or {}
                                    ).get("name"),
        "dearest_r3_in_contract": (dearest_in_contract(rows, "R3") or {}
                                   ).get("name"),
        "cheapest_r4_in_contract": (cheapest_in_contract(rows, "R4") or {}
                                    ).get("name"),
        "smaller_surface_found": [
            {"name": r["name"],
             "external_body_items": r["external_body_items"],
             "pct_vs_own_side_a1": round(r["pct_vs_own_side_a1"], 6)
             if r.get("pct_vs_own_side_a1") is not None else None,
             "gate_refusals": r.get("gate_refusals"),
             "twin_identity_level": r.get("twin_identity_level")}
            for r in small],
        # ⚠⚠ THE FIELD THAT SAYS WHICH FAMILY CAN RESOLVE THIS ROW, AND IT
        # MEASURES THE SPREAD RATHER THAN ASSUMING IT.
        #
        # ⛔⛔ THE `in_contract` FILTER QUESTION, ANSWERED EXPLICITLY IN BOTH
        # DIRECTIONS, because `TASK_PHP_043` assumed ph53 filtered and it does
        # not (`TASK_PHP_044` §3.4). `a1_spread_pp` is UNFILTERED, which is what
        # ph45's and ph53's copies publish and therefore the only figure
        # comparable with theirs: the question it answers is whether the
        # STATISTIC can rank respellings at all, which is a property of the
        # statistic and the search space and not of the contract.
        # `a1_spread_pp_admissible` is the filtered twin, added here rather than
        # left to a reader's assumption. On this row the two differ a lot on the
        # R4 side, because the dearest R4 cells are exactly the gate-refused and
        # bounds-checked ones -- which is the finding, not a defect.
        "a1_spread_pp": {s: _spread(rows, "pct_vs_r4ship_a1", s)
                         for s in RUNG_SIDES},
        "a1_spread_pp_admissible": {
            s: _spread(rows, "pct_vs_r4ship_a1", s, only_admissible=True)
            for s in RUNG_SIDES},
        "wp_spread_pp": {s: _spread(rows, "pct_vs_r4ship_wp", s)
                         for s in RUNG_SIDES},
        "wp_spread_pp_admissible": {
            s: _spread(rows, "pct_vs_r4ship_wp", s, only_admissible=True)
            for s in RUNG_SIDES},
        "in_contract_filter_note":
            "STATED RATHER THAN ASSUMED (TASK_PHP_044 section 3.4, open item "
            "102). a1_spread_pp and wp_spread_pp apply NO in_contract, NO "
            "english_verdict and NO gate_refusals filter, which is what ph45's "
            "and ph53's copies do and therefore the only figures comparable "
            "with theirs. a1_spread_pp_admissible and wp_spread_pp_admissible "
            "are the filtered twins and are published beside them so the "
            "question needs no assumption in either direction.",
        "kernel_digests_distinct": {
            s: len({r.get("kernel_digest") for r in rows.values()
                    if r.get("side") == s and r.get("kernel_digest")})
            for s in ("R3", "R4", "CTL")},
        # ⭐ FIVE BYTE-IDENTITY CLAIMS, and they are only claims about CODE
        # because every exec source path here has the SAME LENGTH -- the
        # equal-length invariant stage 1 asserts. Before the `vNN` slug landed
        # THREE of these five came out WRONG: see `_SLUGS`.
        "byte_identical_pairs": {
            # ph45 §5.6's result on a third row, in its sharper form: the
            # compile-time-constant length buys NOTHING.
            "r3_oprec_array == r3_oprec_slice":
                byte_identical_pair(rows, "r3_oprec_slice", "r3_oprec_array",
                                    "R3"),
            # THE R3 NULL, and byte-identity is a stronger statement than a tie:
            # the same sub-slice lever applied to the two HEAD words changes not
            # one instruction, because LLVM already proves len >= 8.
            "r3_head_slice == v0_shipped":
                byte_identical_pair(rows, "v0_shipped", "r3_head_slice", "R3"),
            # ... and combining the null with the lever gives exactly the lever.
            "r3_both == r3_oprec_slice":
                byte_identical_pair(rows, "r3_oprec_slice", "r3_both", "R3"),
            # THE R4 NULL: `*m.assume_init_ref()` on a reference and
            # `m.assume_init()` on a copy compile to the same kernel.
            "r4_slot_byval == v0_shipped":
                byte_identical_pair(rows, "v0_shipped", "r4_slot_byval", "R4"),
            # ⭐⭐ THE SHARPEST ONE: taking `external_body` OFF
            # slot_read_unchecked changes the TRUSTED BASE and not one byte of
            # the program, which is why the only thing refusing it is a gate
            # rule.
            "r4_no_wrapper == v0_shipped":
                byte_identical_pair(rows, "v0_shipped", "r4_no_wrapper", "R4"),
            # ... and the R4-side echo of the R3 null: once the per-op reads are
            # checked, whether the two HEAD words go through win_get_unchecked
            # makes no difference at all.
            "r4_win_checked == r4_oprec_checked":
                byte_identical_pair(rows, "r4_oprec_checked", "r4_win_checked",
                                    "R4"),
        },
        "oprec_array_byte_identical_to_slice":
            byte_identical_pair(rows, "r3_oprec_slice", "r3_oprec_array", "R3"),
        "ctl_r3_unchecked_is_not_an_upper_bound":
            "⛔ A FRAMING THIS FILE'S FIRST DRAFT GOT WRONG AND THE MEASUREMENT "
            "CORRECTED. ctl_r3_unchecked was written as the CEILING of the R3 "
            "search -- what the R3 side would cost if the four per-op bounds "
            "checks did not exist -- and it is NOT an upper bound, because "
            "r3_chunks_exact is CHEAPER than it (1930.232 against 1946.174 "
            "Ir/call A1 on small.bin at O3/isolated, i.e. -0.82 per cent). ▶ The "
            "reason is that chunks_exact deletes a SECOND term the unsafe "
            "spelling keeps: the per-op offset arithmetic. ctl_r3_unchecked still "
            "computes `p = OPS_OFF + OP_BYTES * o` and indexes from it where the "
            "iterator walks a cursor. ⭐ So the honest statement is the stronger "
            "one: A SAFE RESPELLING OF THIS ROW's R3 BEATS THE SAME RUNG WITH "
            "EVERY WINDOW BOUNDS CHECK REMOVED BY `get_unchecked`. It remains "
            "the right control -- it isolates the bounds-check term at the "
            "shipped spelling, which is what makes the 128-of-131 Ir attribution "
            "checkable -- but it bounds nothing.",
        "panic_call_sites": {f"{s}_{nm}": pc for s, nm, pc, _ni, _a1 in per},
        "r3_gap_mechanism": {
            "shipped_r3_minus_shipped_r4_ir_per_call_a1":
                None if gap is None else round(gap, 6),
            "extra_panic_sites_in_shipped_r3":
                (r3s.get("kernel_panic_calls", 0)
                 - r4s.get("kernel_panic_calls", 0)),
            "static_prediction_ir_per_call": 128.0,
            "note":
                "The shipped R3 reads win[p], win[p+1], win[p+2] and win[p+3] "
                "per op; LLVM hoists the four bounds checks into four "
                "`cmp %rdi,<stack slot>` / `je <panic>` pairs in the hot loop, "
                "which is 8 instructions per op. inputs/small.bin has stride 74, "
                "so cap = (74 - 8) / 4 = 16 ops per call and the static "
                "prediction is 8 * 16 = 128.00 Ir/call. ⭐ THE ANSWER TO "
                "*spelling or mechanism* IS SPELLING: every respelling that "
                "collapses those checks recovers it in SAFE Rust, with no "
                "unsafe token and no trusted item. r3_head_slice is the null "
                "that localises it -- the same lever applied to the two HEAD "
                "words changes nothing, because LLVM already proves len >= 8 "
                "from cap = (len - 8) / 4 and emits no check for them.",
        },
        "witness_cost_pct_w1": {
            "shipped_two_bool": (None if wship is None else round(wship, 6)),
            "note":
                "Per cent whole-program Ir/call above controls/r4_nowitness.rs "
                "on inputs/small.bin at O3/isolated, both cells from THIS "
                "pipeline. NOTES.md section 8g publishes +0.622 per cent W1 and "
                "+0.632 per cent B1. ⚠ MEASURED CORPUS ONLY: r4_nowitness is "
                "not equivalent on an uncovered blob, which is what the witness "
                "is for, so this is a cost comparison and not a ladder rung. "
                "⛔ AND IT IS THE CEILING ON THE ONE R4 LEVER NOT BUILT HERE: "
                "ph53's u32-bitmask witness bought -11.40 per cent A1 because "
                "its witness is an ARRAY, one byte per slot, re-read per "
                "consumer iteration; ph52's is two bools for the whole kernel, "
                "so a perfectly free witness representation could buy at most "
                "the figure above. UNTESTED bound, not a measured variant.",
        },
        "gate_rules_computed":
            "harness/check.py's TWO structural refusals, computed with its own "
            "_is_trusted, vparse.parse, vparse.blank_noncode and _UNSAFE_RE: "
            "5-tcb-unsafe (_scan_unsafe_sites -- every `unsafe` token in a "
            "pinned Verus source must sit inside a trusted body, no hatch) and "
            "5c-twin (check_trusted_twins -- if every trusted item is excused by "
            "verus.twin_justifications and n_twins == 0 the stage checked the "
            "strength of NOTHING, no hatch). They are the two a spec.md "
            "re-declaration could NOT remove, which is why they are the two "
            "computed; this is NOT the whole gate and does not reproduce the "
            "verus.items pins, the contract-sha stages, stage 3c or Miri. "
            "gate_rule_selftest drives the function over 8 synthetic sources on "
            "every invocation (4 must-FIRE including an unparseable source, 4 "
            "must-NOT-fire including ../verus.rs itself).",
        "toolchain": "rustc 1.97.1 / LLVM 22.1.6; Verus 0.2026.08.09.92f466f. "
                     "The largest lever found is an LLVM decision -- how many "
                     "bounds checks survive a sub-slice -- so every figure here "
                     "is about this toolchain.",
        "variants": [
            {k: v for k, v in r.items()
             if k not in ("exe", "rs", "verus_rs", "verus_exe", "build_error",
                          "verus_build_error")}
            for r in rows.values()],
        "problems": problems,
        "invariant":
            "Every variant's `forbidden_hits` is empty by "
            "harness/check.py::spelling_matches, which is what `in_contract` "
            "MEANS here (the field is literally `not forb`, and it never "
            "consults required_absent); `required_absent` is reported BESIDE it "
            "and is judged against each entry's English, because `required` is "
            "presence-only and cannot fail the gate (check.py::idiom_audit, "
            "which measures the naive every-span-in-every-rung reading at 41 "
            "misses of 158 obligations, all 41 non-defects). Where a reading has "
            "been made it is recorded in `english_verdict` and NOT in "
            "`in_contract`; where a MECHANICAL gate refusal exists it is in "
            "`gate_refusals` and in neither -- _admissible requires all three, "
            "which is .memory-php/02-ladder.md item 90's rule with a third field "
            "added. Every variant returns the SHIPPED checksum on all six "
            "inputs, R3 v0_shipped included, which on this row is a declared "
            "property (idiom.required[7]) rather than a convenience. Every "
            "variant is priced in BOTH families by one callgrind run per cell, "
            "and every R3 variant carries ZERO `unsafe` tokens, which stage 1 "
            "asserts rather than assumes -- ctl_r3_unchecked is on the CTL side "
            "for exactly that reason. Every R4 variant additionally has its "
            "substitution applied to verus.rs and is put through Verus, and the "
            "ERROR TEXT is read: `is not supported` and `does not yet support` "
            "disqualify, a failed postcondition does not. An R4 variant with NO "
            "twin file is inadmissible BY RULE (r4_no_twin_reason), which ph45's "
            "copy leaves as a silent skip. The twin must reach the identity "
            "level ../spec.md PINS and the gate record MEASURES -- `norel` on "
            "this row -- computed by harness/asm.py::identity_level, IMPORTED, "
            "and `norel` is NOT byte identity. TWO quantities ship in each "
            "family, labelled: the fixed-R4 bound and the R3-side span. NO PAIR "
            "INTERVAL.",
    }
    out = os.path.join(HERE, "spellings.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
