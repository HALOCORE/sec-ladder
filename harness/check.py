#!/usr/bin/env python3
"""The correctness gate. A pattern is not done until this is green.

Rewritten at TASK_003, because the version before it reported 28/28 PASS on p01
while a reviewer walked six distinct defects past it -- including the pilot's own
fatal defect, an `#[verifier::external_body] fn main` hidden by a single blank
line. Forty-seven patterns will clone this file, so the rule it now follows is:

    where a check was textual, replace it with something semantic; where that is
    impossible, pin the expected value in `spec.md` and diff mechanically.

Rewritten again at TASK_005, because TASK_003_REVIEW showed the *pin model* was
self-certifying: every declared pin moves with the code it constrains, so
weakening one costs one extra edit in the same commit. It demonstrated that with
a full green gate on an R5 whose trusted base axiomatises "reading any index of
any slice is defined". The rule now:

    a declared pin is acceptable only for something a reviewer can check by
    reading `spec.md` alone. Everything else is DERIVED.

What it enforces, in order:

  0  the extractor still reproduces the pilot numbers in `.memory/` (both digest
     conventions), and the three structural parsers pass their own selftests
  0b the pattern DECLARES the idiom its rungs implement, inside the hashed
     contract block. Presence only -- the gate never checks that a rung honours
     it (that check would fail open). What the key buys is that the declaration
     is required, printed in the verdict and hashed, so *weakening or editing
     the declaration* moves `contract_sha256`. It does NOT detect a rung that
     violates the declaration: rung sources are covered by `source_sha256`, and
     a forbidden respelling passes this gate (proved by experiment,
     TASK_016_REVIEW B1). An entry may be a plain string or an object keyed by
     language (TASK_019); `spelling_matches` below DEFINES what matching one
     means. TASK_020 adds a REPORTING-ONLY audit here -- where every backticked
     spelling is and is not, across every rung of the languages it declares,
     printed and written to `results/gate/*.json`. It exists so TASK_019's
     "0 of 82" is reproducible from the committed tree instead of from a
     scratch file. **Since TASK_068 a `forbidden` HIT FAILS the run** -- its
     scope is universal by the key's own meaning, so it is decidable with no
     English involved; the `required` numbers stay presence, not compliance,
     and never fail -- see `idiom_audit`. **TASK_069 made that fail SAFE**: the
     hard fail shipped with `exec_code` blanking ghost CLAUSES only, so
     `proof {}`, `assert(...)`, `spec fn`/`proof fn` bodies, `let ghost` and
     `#[cfg(slb_twin)]` bodies could all fire it -- 11 of 14 honest shapes
     blocked, on constructs present in 20 of 20 shipped `verus.rs`
     (TASK_068_REVIEW B1). TASK_062 adds
     the one thing in this stage that DOES fail on the declaration's text:
     `idiom.why` must carry the shared named-spelling paragraph verbatim,
     because that paragraph is where a backticked pin's MEANING is written
     down, and p27 shipped 62 pinned spellings without it past three tasks and
     two adversarial reviews (`named_spelling_problem`)
  1  every cell of the matrix builds (and under `--no-build`, that no binary
     predates the newest source)
  2  every cell prints the checksum the pattern's own `model.py` predicts. The
     model is driven inside an audit-hook sandbox: it may not start a process,
     because a model that can run the binary under test agrees by construction
  3  no cell collapsed: structurally (a backward branch **or** a bulk-memory
     call, a memory operand, a body above a floor) *and* dynamically -- marginal
     executed instructions per kernel call, measured as a difference of two
     callgrind runs, above a floor DERIVED from `model.py`'s `work_per_call`
     times a harness constant, plus `d(Ir)/d(work)` across two probe shapes.
     **This is a smoke test for total collapse and nothing finer** -- it bounds
     the kernel's total cost, so it cannot attribute cost to a component and
     p02 clears its own floor 35.9x over. What certifies that the work happened
     is step 2. The verdict now prints the achieved margin beside the declared
     floor so a 35.9x and a 2.2-billion-x margin cannot read the same
  3c structural identity R4-vs-R5 is measured, recorded as a result, **and
     enforced**. A level at or above the one `spec.md` pins is a result; a drop
     below it calls `rep.fail` and the run's verdict is FAIL. So a proof that
     legitimately costs an instruction is a finding only while the pin allows
     it -- against an `exact` pin it is a gate failure, not a harness error.
     **This entry read "recorded as a RESULT, not a gate condition" until
     TASK_028, and that was false** (`check_identity` -> `rep.fail("identity",
     ...)`, and `if rep.failures: verdict = "FAIL"`). It mattered beyond
     tidiness: it was the one sentence in the tree arguing that an `identity`
     pin constrains a shipped pair of files rather than the class of programs
     that could occupy the rung, which is the step that disqualifies an
     unverifiable R4 candidate (`.memory/01-ladder.md`, TASK_027_REVIEW Q1)
  4  `adversarial-*` behaviour is recorded per rung and compared to the model's
     expected exit/stdout. A cell that DOES NOT TERMINATE is one of those
     behaviours: `model.py` may declare `expected_hang` on an adversarial input
     and the contract's `run.timeout_s` then pins how long the gate waits
     (TASK_068 -- `RUN_TIMEOUT` is 900 s, which for a deliberately
     non-terminating cell is hours per gate run). The prediction is derived and
     the budget is pinned, they are required to agree, and `diverges` is still
     computed against the CONFORMING `expected_exit` -- see `run_budgets`.
     TASK_069 makes the budget itself checkable: it has a floor
     (`RUN_BUDGET_FLOOR`), and one hung cell is RE-RUN at 10x it and must still
     not terminate, because before that a 3.5 s cell under a 2 s budget was
     accepted as a hang -- which switched stage 7's sanitizer expectation and
     stage 8's Miri row off for that input (TASK_068_REVIEW B2)
  5  the "Proof domain must cover the measured domain" rules:
       - the Verus obligation count equals the number pinned in `spec.md`
       - every item's `external` attribute, `requires` and `ensures` match
         `spec.md` exactly, and the item set matches too; no duplicate item
         names, and no pinned item outside `verus!` or behind a `#[cfg]`
       - a **trusted** item -- `external_body` plus either a non-empty
         `ensures` or `unsafe` in its body (`_is_trusted`) -- must carry a
         non-empty `requires`, or a justification `spec.md` states and the
         verdict prints. Keyed on `external_body` + `ensures` since TASK_010,
         because one `macro_rules!` holding the `unsafe` deleted the whole
         regime while the pins moved in the same commit
       - every `unsafe` token in a pinned Verus source sits inside a trusted
         item's body, and the `common/` files the rungs `#[path]`-include carry
         none at all -- otherwise the unchecked operation is outside every rule
       - every BODY-LESS trusted declaration -- `assume_specification`,
         `axiom fn`, `uninterp spec fn` -- is COUNTED and its count is declared
         in `spec.md`'s `verus.axioms` (TASK_082, RECAP "Owed" 0). These are
         axioms about real Rust semantics that Verus does not prove; they add no
         verified function, emit no instructions and carry no `external_body`,
         so the obligation count, the `identity` pin and the TCB tally are all
         blind to them, and `vparse.parse` could not even see them. The gate
         SHOUTS every one in every verdict; it does not forbid them
       - ⚠ **`assume(` and `admit(` in a pinned or `#[path]`-included Verus
         source FAIL unless `spec.md`'s `verus.assumptions` declares the count**
         (TASK_151). Until then they were a SHOUT, and a shout is not a failure:
         `assume(false);` at the top of the kernel verifies at the SHIPPED
         FILE'S OWN obligation count -- p32 `15/0` (TASK_145 arm X4), p28 `23/0`
         (TASK_149 B1) -- with the clause pin and the `identity` pin both
         unmoved, so a rung could ship a VACUOUS proof and pass. Visibility, not
         prohibition, as above: declaring one moves `contract_sha256`. Exposure
         when it landed was ZERO across all 118 committed `.rs` files, which is
         why it owes the stage-0 must-fire arm `_ASSUME_CASES` rather than a
         green sweep as its evidence
       - Verus itself confirms the call site verifies (`--verify-function`),
         rather than a regex confirming it looks like it might
       - the Python `requires`/`ensures` are GENERATED from `verus.rs`'s clause
         text through `spec.md`'s translation table, then evaluated on **every
         measured input**, adversarial included. Vacuous ones fail
  5c every `ensures` CONJUNCT of every `external_body` item is DELETED in turn
     and Verus re-run: a file that still verifies with 0 errors is carrying a
     trusted claim nothing depends on. Conjunct, not clause -- re-joining a
     redundant clause with `&&` used to defeat the stage. Plus an
     `assert(false)` reachability probe at the kernel call site, which catches
     genuine vacuity
  5c-req the mirror for `requires`, which is a different oracle: deleting a
     precondition from a *trusted* item can never fail a file (it only removes
     obligations from callers -- measured), so each conjunct instead gets a
     synthesised `proof fn` with the item's parameters and that conjunct as its
     only `ensures`. If that verifies, the conjunct is `true` and demands
     nothing. Deletion is still run for *verified* items, where it does bite
  5c-twin every trusted item has a `#[cfg(slb_twin)]` verified twin with the
     same contract, lifted and compared; the twin verifies, its obligation count
     in the twin configuration is pinned too, and it FAILS when any single
     conjunct of the trusted `requires` is deleted. The token `slb_twin` may
     appear nowhere but on a twin's own `#[cfg]`, so the two configurations
     cannot disagree about anything else. `NOTES.md` must carry a per-item
     argument for the three things no stage here can judge, and the verdict
     prints it. The justification hatch is capped and may not cover every
     trusted item
  6  every rung's driver loop, C included, normalises to the token sequence
     pinned in `spec.md`; the *set* of files carrying a region is pinned too;
     the pinned kernel item is called **exactly once** per region-carrying
     source and that call is inside the region; and callgrind's own
     caller->callee edges say the region's enclosing function executed
     (non-zero exclusive `Ir`) and is the only caller of the kernel symbol in
     every `isolated` cell -- a region pinned in a dead decoy function passed
     everything else, in both languages
  7  the C rung matches `model.py`'s per-input `sanitizer_expect`: "clean" means
     no ASan/UBSan diagnostic and the predicted exit, "fires" means a diagnostic
     is REQUIRED (p02's adversarial input is defined as the one that trips ASan)
  7h **the HARDENED C rung (R1h) under the same sanitizers, expected clean on
     EVERY input, adversarial included** -- TASK_151. Stage 7 builds
     `c/kernel.c` only, so until then **no gate stage ran a detector on
     `c/kernel_hardened.c` in ANY pattern**, which is the cell the `p28d`
     variant SEGVed in on a BENIGN input while its verification was not looking
     (TASK_146 §1). The expectation is not per-input and cannot be declared
     away: R1h is the arm that carries the check. Exit and stdout are compared
     to `model.py` on NON-adversarial inputs only -- 72 of 72 such rows are
     identical between the arms, while **74 of 139 adversarial rows differ, and
     that difference is the result**
  8  the Miri policy: mandatory wherever the pattern has a trusted item or a
     hand-written axiom at all,
     and never waivable when R4 and R5 are not the same machine code (`norel` or
     better); run for real on a nightly toolchain. A row Miri cannot be run on is
     a documented blocked row, not a pattern failure

Results are written to `results/gate/<pattern>.json`, with a sha256 of the
contract block and of every source read. Exit code: 0 pass, 1 fail, 2 partial.
A **partial** run (`--skip` / `--no-build` / `--no-callgrind` /
`--no-verus-mutants` / `--cells` != all) certifies strictly less and writes
`.temp/gate-partial/<pattern>.partial.json` instead -- scratch, not evidence,
and deliberately not in `results/gate/` where a verdict survey would find it
(TASK_056).

  harness/check.py p01
  harness/check.py p01 --no-build          # reuse .temp/build/pNN
  harness/check.py p01 --skip large        # fast edit/check loop; PARTIAL verdict
  harness/check.py p01 --no-callgrind      # skip step 3's dynamic half; FAILS
  harness/check.py p01 --no-verus-mutants  # skip step 5c; FAILS
"""

import argparse
import contextlib
import difflib
import functools
import glob
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys
import textwrap
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import build as buildmod  # noqa: E402
import vparse  # noqa: E402
import dloop  # noqa: E402
import fixture  # noqa: E402
# TASK_127, stage 9c. ⚠ The gate importing the REPORTER is deliberate and it is
# FREE: `source_sha` below globs `harness/*.py`, so `report.py` is already in
# every gate record's digest and this adds no file to it. ⚠ The thing that would
# NOT be free is importing from `harness/tools/`, which the non-recursive glob
# does not reach and which is outside the digest by design (TASK_125).
import report as reportmod  # noqa: E402

RUN_TIMEOUT = 900

#: Smallest `run.timeout_s` a contract may pin, and the multiplier the
#: confirmation re-run uses (TASK_069, from TASK_068_REVIEW B2). Measured on
#: this box: bare process startup 1.1-2.2 ms, the slowest shipped O0 cell on
#: `large.bin` 198 ms (p01) -- so 1.0 s is ~5x the slowest honest cell and ~500x
#: startup, while still being 900x below `RUN_TIMEOUT`. Below the floor,
#: "did not terminate within the budget" stops carrying information at all.
RUN_BUDGET_FLOOR = 1.0
RUN_BUDGET_CONFIRM = 10

ENSURES_SAMPLE = 128  # calls re-checked with the model's independent summation
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

# --- harness constants: the things `spec.md` is NOT allowed to set ----------
#
# TASK_003_REVIEW's central finding: every declared pin moves with the code it
# constrains, so weakening a pin costs one extra edit in the same commit. The
# rule adopted at TASK_005 is
#
#     a declared pin is acceptable only for something a reviewer can check by
#     reading `spec.md` alone. Everything else is derived.
#
# "Which input file to probe" is checkable by reading spec.md. "How many
# instructions per element counts as not-collapsed" is not -- it is a fact
# about the machine -- so it lives here, where changing it is a harness diff
# that touches all 47 patterns at once.
#
# ALPHA is instructions executed per abstract unit of work the pattern's own
# `model.py` says the kernel must do. The widest 64-bit SIMD lane count on this
# box is 4 (AVX2), and a load+add pair over 4 lanes is 2 instructions per 4
# elements = 0.5; 0.25 is one further doubling of headroom for a hypothetical
# 8-lane machine. Measured across p01's 28 cells the *minimum* is 1.83 Ir per
# element, so this leaves >7x margin while still sitting ~100x above a
# collapsed loop (which scores ~0 by construction).
#
# **It is the DEFAULT rate, not the only one** (TASK_006 D, from
# TASK_004_REVIEW). 0.25 is sound for a unit of work that is a 64-bit *element*
# and unsound for one that is a *byte*: glibc `memcpy` moves a byte in 0.104
# instructions (re-measured at TASK_006: a 4092-byte copy costs 425.7 Ir), so a
# bulk-copy kernel scores 0.118 Ir/byte and this constant would fail it at 0.47x
# the floor while it is perfectly healthy. A floor that forbids the fastest
# correct implementation is not a floor, it is a bug that happens not to have
# fired yet.
#
# So a pattern's `model.py` may expose
#
#     min_ir_per_work      -> float   # cheapest legitimate Ir per unit of work
#     min_ir_per_work_why  -> str     # the argument for that number
#
# and the gate uses it in place of ALPHA. This is a claim about the *algorithm*
# ("no correct implementation of this can be cheaper than X per unit"), not
# about this kernel, which is what makes it a legitimate declared value under
# the TASK_005 rule: a reviewer judges it by reading the argument, not by
# reading the rung. Declaring a rate BELOW ALPHA additionally requires the
# justification string, which the verdict then prints on every single run (the
# `verus.unsafe_justifications` design), and requires two probe shapes so that
# the un-gameable half of the stage -- `d(Ir)/d(work) >= rate` -- actually runs.
#
# Note what this stage does *not* do, on any setting: it bounds the kernel's
# total cost, so it cannot certify that one *component* of the kernel happened.
# p02 clears any rate on its fold alone. What certifies that p02's copy happened
# is step 2 -- the reference model's checksum depends on every copied byte.
ALPHA_IR_PER_WORK = 0.25

# ...and there is a hard floor under what `min_ir_per_work` may declare, because
# until TASK_008 the only bound was `> 0`. TASK_006_REVIEW put
# `min_ir_per_work = 1e-9` with `min_ir_per_work_why = "see NOTES.md"` past the
# whole gate; it printed "derived floor 0.0 Ir/call" and "tightest margin
# 2246270772.2x" and nothing objected, because nothing inspects `why` -- it is
# free text. `work_per_call` is a second unbounded knob in the same sandboxed
# file, and the floor is their *product*, so either one alone can zero it.
#
# The bound is physical, not conventional. The tightest legitimate rate anyone
# has argued for in this project is p02's 0.0625 Ir per byte: on this box's
# AVX-512 units a fused copy-and-fold is load + store + `vpsadbw` + `vpaddq` per
# 64-byte lane, i.e. 4 instructions per 64 bytes. (Measured reality is looser
# still: glibc `memcpy` moves a byte in 0.104 Ir.) A vector unit four times
# wider than anything that exists would put the same four instructions across
# 256 bytes and land at 1/64. So:
#
#     no algorithm can be cheaper than 0.015625 instructions per unit of work,
#     for any unit of work small enough to be worth denominating in.
#
# A pattern that wants to declare less than that is not making a claim about an
# algorithm; it is saying the work does not happen, and no `why` string can fix
# that. Changing this is a harness diff that moves all 47 patterns at once.
MIN_DECLARABLE_IR_PER_WORK = 0.015625
#
# ...but read that derivation again: "four instructions per 256 **bytes**". It
# is a statement about a byte-denominated unit, and it fired *before* any
# justification was consulted, unlike the below-default path which accepts a
# `min_ir_per_work_why`. TASK_008_REVIEW found the pattern it forbids:
# `.memory/06-catalogue.md` plans **p09, bit vector / bitset** -- AVX-512
# `vpopcntq` does 512 bits in ~3 instructions = **0.0059 Ir per bit**, below
# 1/64, with no route out. An honest bit-denominated `model.py` could not be
# greened at all.
#
# The bound is therefore expressed per **bit** of whatever unit `model.py`
# denominates in, which is the only unit-awareness that is physical rather than
# conventional:
#
#     MIN_DECLARABLE_IR_PER_BIT * work_unit_bits
#
# `model.py` declares `work_unit_bits` (default 8 -- a byte, so no existing
# pattern moves and p02's bound is still exactly 0.015625) and `work_unit` (a
# name, printed). p09 declares 1 and gets 0.001953, which `vpopcntq`'s 0.0059
# clears 3x. This is unit-*awareness*, not a hatch: nothing has to be argued.
MIN_DECLARABLE_IR_PER_BIT = MIN_DECLARABLE_IR_PER_WORK / 8
#
# Unit-awareness does not cover everything, and the residue is worth naming. A
# *skipping* walker -- a TLV parser denominated in buffer bytes -- touches one
# byte in `stride`, so its honest Ir-per-byte is unbounded below and no physical
# argument fixes it, because the rate is then a fact about the input rather than
# about the algorithm. The right answer there is to re-denominate the unit in
# the thing the kernel actually touches (records, not bytes), and the failure
# message says so. For the case where an author is sure otherwise there is a
# justification hatch -- `min_ir_per_work_bound_why`, shouted on every run like
# its sibling -- but it is capped: it may lower the unit-aware bound by at most
# 64x, the same "a vector four times wider than anything that exists, three
# times over" argument. Without a cap the hatch is `> 0` again and
# TASK_006_REVIEW's `1e-9` walks back in behind a free-text string.
MIN_BOUND_HATCH_FACTOR = 64.0
#
# ...and the two knobs above COMPOSE, which TASK_009_REVIEW measured as Part F.
# `work_unit_bits` is checked only for `>= 1`, so `work_unit_bits = 1` plus the
# hatch yields an absolute bound of **3.05e-5 -- 512x below the pre-TASK_009
# bound of 0.015625** -- out of two numbers in the same author-written `model.py`
# that already supplies `min_ir_per_work` and `work_per_call`. Three composing
# knobs, one author, one commit; and nothing checks that `work_per_call` is
# denominated in the unit `work_unit_bits` names, so the third knob can absorb
# any factor the other two cannot.
#
# So the *product* is bounded, not just each factor. The unit-aware bound and
# the hatch may each apply in full, but their composition may not take the
# absolute floor below one hatch-factor under the byte-denominated bound:
#
#     bound = max(MIN_DECLARABLE_IR_PER_BIT * work_unit_bits [/ hatch],
#                 MIN_DECLARABLE_IR_PER_WORK / MIN_BOUND_HATCH_FACTOR)
#
# p09's bit-denominated unit still clears it unhatched (0.001953 > 0.000244) and
# so does a hatched byte unit (0.000244), which are the two cases either
# mechanism was introduced for. What is now impossible is stacking them, and the
# effective absolute floor is printed on every run so a reviewer sees which
# number the run actually enforced.
MIN_DECLARABLE_IR_PER_WORK_ABS = (MIN_DECLARABLE_IR_PER_WORK
                                  / MIN_BOUND_HATCH_FACTOR)

# Above this ratio of measured Ir to the derived floor, the floor is loose
# enough that it certifies nothing but total collapse, and the verdict says so.
# It is a `shout`, not a `fail`: a legitimately fast kernel on a conservative
# unit of work has a large margin honestly (p01 runs 7x-268x), and failing on it
# would make the floor a cap on how good a rung is allowed to be. What it must
# not do is read the same as a tight one -- 35.9x and 2246270772.2x printed
# identically before TASK_008.
LOOSE_FLOOR_MARGIN = 100.0

MIRI_PROBE_ITERS = 4       # kernel calls Miri interprets per input
# Per-input wall limit. `n_iters` can be clamped from the file header, but the
# *payload* cannot: p01's `large.bin` is 1.5 M u64s and the driver decodes them
# one at a time, which Miri interprets at ~1000x. A timeout is recorded as a
# blocked row for that input, never as a pattern failure -- otherwise the size
# of an input file decides whether the gate is green.
MIRI_TIMEOUT = 180
NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
CARGO = os.path.expanduser("~/.cargo/bin/cargo")

# ⚠⚠ TASK_107 §C. `check.py` USED TO PASS NO `MIRIFLAGS` AND TO RECORD NOTHING
# ABOUT IT, so every *"Miri: N of N, no UB"* line in this tree was a statement
# about a configuration nobody had written down. `miri` takes these only through
# the environment, not on its command line.
#
# ⚠⚠⚠ **AND THE OBVIOUS FIX -- PIN A SEED -- IS STILL THE ONE THING THAT MUST
# NOT BE DONE HERE, BUT ~~BECAUSE SETTING `MIRIFLAGS` AT ALL COSTS 4.6x ON THIS
# TREE~~ IS THE WRONG REASON AND IS RETRACTED. The right reason is below: the
# driver never reads the variable, so a pinned seed would not arrive anyway.**
# ~~TASK_107 chose `MIRIFLAGS="-Zmiri-seed=0 -Zmiri-symbolic-alignment-check"`,
# swept with it, and the sweep itself refuted the choice: p42 gained a SECOND
# blocked Miri row. Measured afterwards on p42's `adversarial-wincap.bin`, the
# gate's own probe file, `cwd=pdir`, the exact `check_miri` command line:
#
#     MIRIFLAGS unset                                   74.6 / 73.4 / 74.0 / 73.8 s
#     MIRIFLAGS="-Zmiri-seed=0"                        340.4 / 338.3 s
#     MIRIFLAGS="-Zmiri-seed=0 -Zmiri-symbolic-…"      342.7 / 339.0 s
#     MIRIFLAGS="-Zmiri-symbolic-alignment-check"      337.8 / 337.0 s
#     MIRIFLAGS=""      <-- SET BUT EMPTY               339.8 s
#
# **The empty string costs the same 4.6x as any flag, so the trigger is the
# VARIABLE BEING PRESENT, not its content.**~~
#
# ⚠⚠⚠ **THE STRUCK PARAGRAPH IS RETRACTED (`TASK_114` B2, landed here at
# `TASK_119`), AND THIS IS THE SECOND WRONG MECHANISM ON THIS AXIS.** `MIRIFLAGS`
# is not the variable at all:
#
#   * the `miri` **rustc driver** -- which is what the `subprocess.run` in
#     `check_miri` invokes -- **never parses `MIRIFLAGS`.** A bogus value in the
#     environment gives `rc=0` and is ignored; the same flag on the command line
#     gives `rc=1 unknown unstable option`. `MIRIFLAGS` is `cargo-miri`'s.
#   * re-measured on the same probe, **the direction REVERSES**, three repeats
#     each way plus two more of the ambient block:
#
#         MIRIFLAGS unset              338.1 / 347.4 / 345.4 / 343.1 s  <- SLOW
#         MIRIFLAGS=""                  75.1 / 75.4 s                   <- fast
#         SLB_R114_DECOY=""             74.4 / 75.9 s   <- A DECOY, NOT MIRI'S
#         $OLDPWD removed               75.3 s
#
#   * so the 4.6x is an **environment-block** effect -- the same axis as
#     `_env_block`'s +-7 -- and a variable with no relation to Miri selects it.
#
# ⚠⚠ **THE MECHANISM IS OPEN AND MUST STAY OPEN.** Two have been published and
# both were wrong ("seed-vs-seed", then "`MIRIFLAGS` presence"). `TASK_114`
# killed its own only surviving correlation rather than report it -- a second
# `miri base % 4 == 3` draw timed FAST -- so **do not chase the address
# residue**, and do not write a third mechanism without measuring it.
# ✅ `TASK_119` asked whether `marginal_ir_env`'s new `envp_stack_bytes`
# separates the two states, precisely so the record could answer; the arms and
# the answer are in `.temp/t119/b1_miri_state.py` and `TASK_119_REPORT.md`.
# **What the record does now carry either way is `miri.runs[].seconds`.**
#
# `MIRI_TIMEOUT` is 180 s and the two states are ~75 s and ~340 s, i.e. **the
# timeout sits between them**, so the same row can be green or BLOCKED on the
# invoking shell alone -- and p42's own `spec.md` calls Miri *"load-bearing for
# the pattern's own subject on the R4 side"*, because R4 has no proof and Miri's
# exit-time leak report is the only mechanical check that it does not leak.
#
# **What the seed does and does not buy, also measured** (`.temp/t107/c2_miriflags.py
# --probe`, two families x 12 seeds; `.temp/t107/c1_miri_cost.py`):
#
#   * a `Vec<u32>` (alignment 4 by construction) gives clean/UB/UB/clean at byte
#     offsets 0/1/2/4 under unset, under every seed 0..11, and with the symbolic
#     check: **0 misses, 0 false positives, 0 nondeterminism**;
#   * a `Vec<u8>` (alignment 1) + `ptr::read::<u32>` at byte 1 is the only
#     seed-sensitive class, and there the split is **unset=CLEAN vs every seed
#     0..11=UB** -- i.e. unseeded-vs-seeded, NOT seed-vs-seed;
#   * `0 of 40` p01 rows and `0 of 20` p09 rows change UB verdict or timeout
#     status with the seed, and a 4-seed sweep costs exactly 4.00x
#     (p01's Miri stage 182.0 s -> 728.0 s, of which 720 s is one row hitting
#     `MIRI_TIMEOUT` four times).
#
# ⚠ `.memory/00-environment.md`'s *"clean under seed 0 and 2 and UB under 1 and
# 3"* **does not reproduce** at this toolchain; seeds 0..11 agree and
# 0/1/2/3/7/100/1000/12345/999999 all give the same `base % 4`. Its CONCLUSION
# -- that a green Miri row was a claim about an unwritten-down configuration --
# stands, and this is the answer to it.
#
# **So: run at Miri's default, and RECORD THE CONFIGURATION instead of pinning
# it.** The default is deterministic (four timings above agree to 1.6%, and the
# address probe reproduces `base % 4 == 3`); what actually moved between
# TASK_102 and TASK_107 is the **miri version**, so that is what the record now
# carries beside the flags.
#
# ⚠⚠ **WHY `MIRI_FLAGS` IS EMPTY, RE-JUSTIFIED AT `TASK_119` BECAUSE THE
# ORIGINAL JUSTIFICATION WAS RETRACTED.** ~~An ambient `MIRIFLAGS` is REMOVED,
# not inherited: leaving it would let the invoking shell silently cost 4.6x~~ --
# **false**, and the reverse of what was measured next: it is the *removal* that
# sat in the slow state when `TASK_114` re-ran it. **Emptying `MIRI_FLAGS` does
# not CONTROL the fast/slow state; it CHANGES it, in a direction nobody can
# predict.**
#
# ✅ **It stays anyway, on a DIFFERENT and much duller argument that survives
# the retraction:** the gate must not inherit a flag set from the invoking
# shell, because `MIRIFLAGS` *is* read by `cargo miri` and by any future call
# site that uses it, and a row certified under an ambient
# `-Zmiri-ignore-leaks` would be a silently weaker check than the record claims.
# **Stripping it makes the configuration a property of `check.py` rather than of
# whoever ran it.** That argument is about REPRODUCIBILITY, not about speed, and
# it does not depend on any mechanism for the 4.6x. What was removed is
# recorded (`miriflags_removed_ambient`), and how long each row actually took is
# recorded too (`miri.runs[].seconds`), which is the part that was missing.
MIRI_FLAGS = ()          # empty => `MIRIFLAGS` is UNSET in the child, not ""


# ==========================================================================
# the model sandbox
# ==========================================================================
#
# TASK_003_REVIEW bypass: a `model.py` whose `checksum` shells out to the built
# C binary passes step 2, and the log cheerfully reports the checksum was
# "re-derived". Step 2 is the gate's only load-bearing correctness check; it
# must not be satisfiable by running the thing under test.
#
# An audit hook is the enforcement, not the grep: hooks cannot be removed once
# installed, so no amount of cleverness inside `model.py` gets a subprocess out.
# The grep below it is the part a *reviewer* can see.

class ModelSandboxError(RuntimeError):
    pass


_MODEL_ACTIVE = [False]
_MODEL_FORBIDDEN = ("subprocess.", "os.system", "os.exec", "os.spawn",
                    "os.posix_spawn", "os.fork", "os.forkpty", "pty.spawn",
                    "ctypes.", "socket.", "urllib.", "webbrowser.",
                    "shutil.copy", "os.putenv")

_MODEL_SOURCE_BAN = re.compile(
    r"\bsubprocess\b|\bctypes\b|\bsocket\b|os\.system|os\.popen|os\.exec|"
    r"\bpopen\b|\brun_bin\b|\.temp/build|\bcffi\b", re.I)


def _model_audit(event, args):
    if not _MODEL_ACTIVE[0]:
        return
    if any(event.startswith(p) for p in _MODEL_FORBIDDEN):
        raise ModelSandboxError(
            f"model.py attempted {event!r} while the gate was driving it. The "
            f"reference model must be an *independent* implementation derived "
            f"from the input bytes; a model that can run the binary under test "
            f"agrees with it by construction and step 2 certifies nothing.")


sys.addaudithook(_model_audit)


@contextlib.contextmanager
def model_sandbox():
    prev = _MODEL_ACTIVE[0]
    _MODEL_ACTIVE[0] = True
    try:
        yield
    finally:
        _MODEL_ACTIVE[0] = prev


def sb(fn, *a, **kw):
    """Call model code with the sandbox on."""
    with model_sandbox():
        return fn(*a, **kw)


def sbg(obj, name):
    """Read one model attribute with the sandbox on. Model API members are
    often `@property`, so reading one runs pattern code."""
    with model_sandbox():
        return getattr(obj, name)


def sbg_opt(obj, name, default=None):
    """Read an *optional* model attribute with the sandbox on.

    `hasattr` outside the sandbox would evaluate a `@property` unsandboxed, so
    existence and evaluation happen together and inside."""
    with model_sandbox():
        return getattr(obj, name, default)


def sb_iter(it):
    """Consume a model generator with the sandbox on for each `next()`."""
    while True:
        with model_sandbox():
            try:
                v = next(it)
            except StopIteration:
                return
        yield v


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ==========================================================================
# helpers
# ==========================================================================

class Report:
    def __init__(self):
        self.failures = []
        self.notes = []
        self.loud = []      # things the verdict must shout, pass or fail
        self.blocked = []   # rows that could not be checked, with a reason
        self.results = {}

    def fail(self, section, msg):
        self.failures.append((section, msg))
        print(f"    FAIL [{section}] {msg}")

    def ok(self, msg):
        print(f"    ok   {msg}")

    def note(self, msg):
        self.notes.append(msg)
        print(f"    --   {msg}")

    def shout(self, section, msg):
        """A caveat that survives to the verdict. Used for the things that are
        legitimate but must never be quietly true: a trusted `unsafe` item with
        no precondition, a row Miri could not be run on."""
        self.loud.append((section, msg))
        print(f"    !!   [{section}] {msg}")

    def block(self, section, row, reason):
        """One row could not be checked. `.memory/02-bench-rules.md`: a rung
        that is impossible is a documented failure *for that row*, not a
        pattern-wide gate failure -- failing a whole pattern on a missing tool
        is how gates get switched off."""
        self.blocked.append(dict(section=section, row=row, reason=reason))
        print(f"    !!   [{section}] BLOCKED {row}: {reason}")


def head(title):
    print(f"\n== {title} " + "=" * max(0, 66 - len(title)))


def run_bin(path, arg, timeout=None):
    """Run one cell on one input. `(exit, stdout, stderr)`, with `exit is None`
    meaning *it did not terminate inside the budget*.

    `timeout` defaults to `RUN_TIMEOUT` (900 s), which is a ceiling for a cell
    that is merely slow. A pattern whose adversarial input is a **deliberate
    non-terminating loop** pays that ceiling on every cell of every gate run --
    for a hash-probe pattern, 12 to 20 cells x 900 s = 3 to 5 hours, paid again
    on every doc edit because `pdir/*.md` is in `source_sha256`. So the
    `slb-contract` block may shorten the budget per input; see `run_budgets`."""
    t = RUN_TIMEOUT if timeout is None else timeout
    try:
        r = subprocess.run([path, arg], capture_output=True, text=True,
                           timeout=t)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", f"<timeout after {t}s>"


def inputs_of(pdir, skip=()):
    d = os.path.join(pdir, "inputs")
    # `sweep-*` files are diagnostic (a per-call cost measured at one window
    # length is a coincidence, not a number -- see inputs/gen.py). They are not
    # part of the matrix and would multiply the gate's runtime for nothing.
    names = sorted(f for f in os.listdir(d)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    names = [n for n in names if n[:-4] not in skip]
    good = [n for n in names if not n.startswith("adversarial")]
    adv = [n for n in names if n.startswith("adversarial")]
    return d, good, adv


def read_contract(pdir):
    """Pull the ```slb-contract block out of spec.md.

    Returns (contract, raw_block_text). The raw text is hashed into the gate
    JSON so that weakening a pin shows up in review as a *contract change* --
    a one-line diff in the committed artefact -- rather than as an unremarkable
    source diff somebody has to notice (TASK_005 A4)."""
    txt = open(os.path.join(pdir, "spec.md")).read()
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    if not m:
        raise SystemExit("check.py: spec.md has no ```slb-contract block")
    return json.loads(m.group(1)), m.group(1)


def run_budgets(contract, rep, all_stems):
    """`{input stem: seconds}` from the contract's optional `run` block.

    ```json
    "run": {"timeout_s": {"adversarial-full": 5},
            "why": "R1..R4's probe loop does not terminate on a full table; ..."}
    ```

    **Where this lives, and why -- settled at TASK_068, which was handed the
    question open.** The manager's proposal was one declaration in `model.py`
    (an optional per-input `run_timeout_s`, with `expected_exit = None` meaning
    "expected not to terminate"), and asked the deciding question: *should
    declaring a hang move `contract_sha256`?* The answer is **yes -- but there
    are TWO declarations here, not one, and they belong in different files**:

      * **Which inputs do not terminate is a SEMANTIC PREDICTION**, derivable
        from the blob's own bytes (a full table and an absent key), and it is
        `model.py`'s job to derive it -- `model.py` is the *independent
        reference*, and `sanitizer_expect` / `expected_exit` / `expected_stdout`
        are already there. `.memory/02-bench-rules.md`'s rule on declared pins
        is *"acceptable only for something a reviewer can check by reading
        `spec.md` alone"*; whether a given blob makes a probe loop run forever
        is emphatically not that. So it stays derived: `model.expected_hang`.
      * **How many seconds the gate waits before calling it a hang is a RESOURCE
        PIN.** It is not a function of the input bytes at all -- it is a claim
        that the hang is *detectable* in that long -- and it is exactly what a
        reviewer can judge from prose. It is also the knob that could quietly
        turn a slow-but-honest cell into a "declared hang", which is the edit
        that must show up in review. So it is a pin, here, hashed into
        `contract_sha256`.

    The two are **required to agree** (`check_hang_declarations`): a model that
    declares a hang must have a budget, and a budget must name an input the
    model declares. That is what makes the answer to the deciding question a
    *yes* mechanically -- a hang cannot be declared without moving
    `contract_sha256` -- while leaving the prediction itself derived.

    ⚠ **A NON-adversarial input may never carry either half.** Enforced twice
    (here, and on the model side in `build_models`) because it is the accident
    this design could enable: stage 2's checksum agreement is the gate's only
    load-bearing correctness check, and a pattern that could declare its `small`
    or `large` cell non-terminating would be declaring its way out of it.
    ⚠ **Honest scope**: as the code stands today that accident is already
    caught, because `check_checksums` requires `rc == 0` and reads no model
    expectation at all -- a hanging good cell fails "run" whatever it declared.
    This guard is therefore fail-closed defence in depth against a *later* edit
    that teaches stage 2 about `expected_hang`, not the closure of a live hole.
    Do not upgrade the claim.

    ⚠ **`timeout_s` shipped with no lower bound, and that made it the first pin
    in a `slb-contract` block that is NEITHER prose-judgeable NOR cross-checked
    against a measurement** (TASK_068_REVIEW B2 -- the general point, and it is
    worth more than the bug). Every other pin is one or the other:
    `driver.statements`, `driver.regions`, `identity` and
    `collapse.probe_inputs` are judged by reading them; `verus.obligations`,
    the identity digests and `miri.required` are diffed against something the
    gate measures. `run.timeout_s` was self-certifying, and it reproduced
    `min_ir_per_work`'s known weakness exactly -- bounded only by `> 0`, which
    TASK_006_REVIEW drove through the whole gate at `1e-9`
    (`.memory/02-bench-rules.md:345-360`). Measured on the shipped code:
    `timeout_s = 1e-9` was accepted, and a real gcc binary that terminates in
    3.5 s, declared with `timeout_s: 2`, was recorded as a declared hang with
    **0 failures** -- after which stage 7 skipped its sanitizer expectation and
    stage 8 raised the row BLOCKED. Two things convert it into a cross-checked
    pin, and both are needed:

      * **`RUN_BUDGET_FLOOR` (below).** 10x a budget smaller than process
        startup is still smaller than process startup, so the re-run alone does
        not catch `1e-9`.
      * **the confirmation re-run in `check_adversarial`**: one hung cell is
        re-run at `min(10 x budget, RUN_TIMEOUT)` and the pattern FAILS if it
        terminates. That is declared-vs-measured, which is the model
        `.memory/02-bench-rules.md` names as the one to copy."""
    run = contract.get("run")
    if run is None:
        return {}
    if not isinstance(run, dict):
        rep.fail("run-budget", "contract `run` must be an object with "
                               "`timeout_s` and `why`")
        return {}
    unknown = sorted(set(run) - {"timeout_s", "why"})
    if unknown:
        rep.fail("run-budget", f"contract `run` has unknown key(s) {unknown}; "
                               f"a mistyped key is silently empty")
    if not (run.get("why") or "").strip():
        rep.fail("run-budget", "contract `run.why` is empty. A shortened run "
                               "budget is a pin, and a pin whose reason is not "
                               "written down is not checkable by reading "
                               "`spec.md` alone.")
    tos = run.get("timeout_s")
    if not isinstance(tos, dict) or not tos:
        rep.fail("run-budget", "contract `run.timeout_s` must be a non-empty "
                               "object {input stem: seconds}")
        return {}
    out = {}
    for stem, secs in sorted(tos.items()):
        if stem not in all_stems:
            rep.fail("run-budget", f"`run.timeout_s` names {stem!r}, which is "
                                   f"not an input of this pattern")
            continue
        if not stem.startswith("adversarial"):
            rep.fail("run-budget",
                     f"`run.timeout_s` names {stem!r}, which is not an "
                     f"adversarial input. A shortened budget is only ever for a "
                     f"deliberately non-terminating cell, and those are "
                     f"adversarial by construction; on a matrix input it would "
                     f"be a way to declare out of stage 2's checksum "
                     f"agreement.")
            continue
        if not isinstance(secs, (int, float)) or isinstance(secs, bool) \
                or not RUN_BUDGET_FLOOR <= secs <= RUN_TIMEOUT:
            rep.fail("run-budget",
                     f"`run.timeout_s[{stem}]` is {secs!r}, want a number in "
                     f"[{RUN_BUDGET_FLOOR}, {RUN_TIMEOUT}]. The floor is not "
                     f"decoration: below it, 'did not terminate in the budget' "
                     f"stops distinguishing a hang from an ordinary cell -- "
                     f"bare process startup on this box measures 1-2 ms and the "
                     f"slowest shipped O0 cell on `large.bin` 198 ms "
                     f"(`.temp/p69/NOTES.md`) -- and the confirmation re-run "
                     f"cannot catch it either, since 10x a sub-startup budget "
                     f"is still sub-startup. `timeout_s = 1e-9` was accepted "
                     f"before TASK_069 (TASK_068_REVIEW B2).")
            continue
        out[stem] = secs
    return out


def load_model(pdir, contract):
    """Import the pattern's own reference model (`model.py`).

    Before TASK_003 this was hard-coded into check.py and every one of 47
    patterns would have had to fork the gate to get its own (M8). The API the
    module must expose is documented at the top of `patterns/p01-array-sum/model.py`.

    Imported and driven inside `model_sandbox()`: a model that can start a
    process can agree with the rungs by *being* them (TASK_003_REVIEW)."""
    name = contract.get("model", "model.py")
    path = os.path.join(pdir, name)
    if not os.path.exists(path):
        raise SystemExit(f"check.py: {path} missing -- every pattern ships a "
                         f"reference model; see patterns/p01-array-sum/model.py "
                         f"for the API")
    src = open(path).read()
    hits = sorted(set(m.group(0) for m in _MODEL_SOURCE_BAN.finditer(src)))
    if hits:
        raise SystemExit(
            f"check.py: {name} mentions {hits} -- the reference model must be "
            f"an independent implementation from the input bytes alone. A model "
            f"that shells out to the built binary agrees by construction and "
            f"step 2 then certifies nothing.")
    spec = importlib.util.spec_from_file_location(
        f"slb_model_{buildmod.pattern_id(pdir)}", path)
    mod = importlib.util.module_from_spec(spec)
    with model_sandbox():
        spec.loader.exec_module(mod)
    if not hasattr(mod, "build"):
        raise SystemExit(f"check.py: {path} does not define build(path)")
    return mod


REQUIRED_MODEL_ATTRS = ("n_iters", "truncated", "checksum", "expected_exit",
                        "expected_stdout", "n_calls", "iter_calls",
                        "sample_calls", "helpers", "describe", "selfcheck",
                        # TASK_005 A1: the collapse floor is derived from this,
                        # not declared in spec.md.
                        "work_per_call",
                        # TASK_005 B5: p02's adversarial input is *defined* as
                        # the one that trips ASan, so "the sanitizer fired" has
                        # to be an expectation, not an automatic failure.
                        "sanitizer_expect")


# ==========================================================================
# 0. the extractor and the parsers still do what `.memory/` says
# ==========================================================================

def check_selftests(rep):
    head("0. extractor + parsers reproduce .memory/ and their own selftests")
    if not fixture.ensure():
        rep.fail("fixture", "could not build .temp/build/docrepro "
                            "(harness/fixture.py) -- step 0 cannot run")
        return
    rc = asm.selftest()
    if rc == 77:
        rep.fail("asm-selftest", "pilot fixture still missing after a build "
                                 "attempt")
    elif rc != 0:
        rep.fail("asm-selftest", "harness/asm.py no longer matches .memory/")
    if vparse._selftest() != 0:
        rep.fail("vparse-selftest", "harness/vparse.py fails its own bypass "
                                    "cases -- attribute detection is unsound")
    if dloop._selftest() != 0:
        rep.fail("dloop-selftest", "harness/dloop.py fails its own bypass "
                                   "cases -- driver normalisation is unsound")
    for label, got, want in _IDIOM_CASES:
        if got != want:
            rep.fail("idiom-selftest",
                     f"idiom_problems: {label}: got {got}, want {want}")
    for label, got, want in _MATCH_CASES:
        if got != want:
            rep.fail("spelling-selftest",
                     f"spelling_matches: {label}: got {got}, want {want}")
    for label, got, want in _AUDIT_CASES:
        if got != want:
            rep.fail("audit-selftest",
                     f"idiom_audit: {label}: got {got}, want {want}")
    for label, got, want in _FORBIDDEN_VERDICT_CASES:
        if got != want:
            rep.fail("forbidden-verdict-selftest",
                     f"forbidden_verdict: {label}: got [fail,ok,shout]={got}, "
                     f"want {want}")
    for label, got, want in _NAMED_SPELLING_CASES:
        if got != want:
            rep.fail("named-spelling-selftest",
                     f"named_spelling_problem: {label}: got {got}, want {want}")
    # TASK_151's must-fire arm for the vacuity check. It is HERE, run on every
    # invocation, because the repair is PROSPECTIVE: no shipped `verus.rs`
    # spells `assume(` or `admit(`, so a green sweep says nothing about whether
    # the check can fire. `got[0] == "RAISED"` means `_axiom_keyword_scan`
    # threw -- reported, not crashed (`.memory/03-measurement.md` entry 19).
    for label, got, want in _ASSUME_CASES:
        if got != want:
            rep.fail("assume-selftest",
                     f"_axiom_keyword_scan: {label}: got [fail,shout]={got}, "
                     f"want {want}")
    # TASK_164's must-fire arm for stage 9b's VERDICT read, here for exactly the
    # same reason: all 30 shipped `problems` lists are EMPTY and all 5 shipped
    # `summary` blocks are `as_expected == n`, so a green 33-pattern sweep says
    # nothing about whether the check can fire. `got[0] == "RAISED"` means
    # `control_json_verdict` threw -- reported, not crashed.
    for label, got, want in _CONTROL_VERDICT_CASES:
        if got != want:
            rep.fail("control-verdict-selftest",
                     f"control_json_verdict: {label}: got [verdict,n]={got}, "
                     f"want {want}")


# ==========================================================================
# 0b. the pattern declares the idiom its rungs implement
# ==========================================================================

IDIOM_KEYS = ("required", "forbidden", "why")

#: languages an `idiom` entry may be keyed by. A `required`/`forbidden` entry is
#: either a plain string (applies to every rung) or an object with these keys
#: (each rung is read against its own language's spelling). TASK_019.
IDIOM_LANGS = ("c", "rust")

_GHOST_KW = re.compile(r"\b(requires|ensures|recommends|decreases|invariant"
                       r"|opens_invariants|no_unwind|returns|when)\b")


def _blank_ghost(code):
    """Blank Verus ghost clauses, preserving offsets and line numbers.

    A clause keyword at bracket depth 0 opens a region that runs to the `{` or
    `;` that ends it -- which covers a function's `requires`/`ensures` list and
    a loop's `invariant`/`decreases` header alike. `vparse.clause_spans` does
    not: it reads an item's *signature* only, and the spelling that forced this
    to exist is a **loop** invariant (below)."""
    out, i, n, depth = list(code), 0, len(code), 0
    while i < n:
        c = code[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0:
            m = _GHOST_KW.match(code, i)
            if m:
                j, d2 = m.end(), 0
                while j < n:
                    ch = code[j]
                    if ch in "([":
                        d2 += 1
                    elif ch in ")]":
                        d2 -= 1
                    elif d2 == 0 and ch in "{;":
                        break
                    j += 1
                for k in range(i, j):
                    if out[k] != "\n":
                        out[k] = " "
                i = j
                continue
        i += 1
    return "".join(out)


#: cfg names some cell this project actually BUILDS or RUNS sets. Everything
#: else names code that reaches no codegen unit here, so `exec_code` blanks it.
#:
#: Derived, not enumerated from failures: the first entry is the only `--cfg`
#: `build.py` passes (`build.py:150`, isolated mode), the second is set by the
#: interpreter stage 8 runs, and the rest are rustc's own, defined for every
#: compilation by the target rather than by any flag of ours (Rust reference,
#: "Conditional compilation"). `test` is deliberately NOT here: nothing in this
#: repo ever passes `--test`, so a `#[cfg(test)]` module is dead in every cell
#: that is built, measured or interpreted.
CODEGEN_CFGS = frozenset({
    "slb_isolated", "miri",
    "unix", "windows", "panic", "debug_assertions", "overflow_checks",
    "target_arch", "target_os", "target_family", "target_env", "target_endian",
    "target_pointer_width", "target_vendor", "target_feature",
    "target_has_atomic", "target_abi", "target_thread_local",
})

_CFG_ATTR = re.compile(r"#!?\[\s*cfg\s*\(")
_ATTR_START = re.compile(r"#!?\[")
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_CFG_WORDS = frozenset({"cfg", "all", "any", "not"})

#: Verus ghost STATEMENTS. `assert`/`assume` are matched only as bare
#: identifiers, so Rust's `assert!`, `assert_eq!` and `debug_assert!` macros --
#: which do reach codegen -- are untouched.
_GHOST_STMT = re.compile(r"\b(proof|assert|assume)\b(?!\s*!)")
_GHOST_LET = re.compile(r"\blet\s+(?:mut\s+)?(?:ghost|tracked)\b")
_GHOST_CTOR = re.compile(r"\b(?:Ghost|Tracked)\s*(?:::\s*(?:new|assume_new))?\s*\(")


def _blank_span(out, a, b):
    """Blank `out[a:b]` in place, preserving offsets and line numbers."""
    for k in range(max(a, 0), min(b, len(out))):
        if out[k] != "\n":
            out[k] = " "


def _bracket_end(code, i):
    """Index just past the bracket group opening at `code[i]`, or None."""
    try:
        return vparse._match_bracket(code, i)
    except (ValueError, IndexError):
        return None


def _item_end(code, i):
    """End of the item that starts at `code[i]`: the `;` or the `{...}` that
    closes it, whichever comes first at depth 0. Attribute-agnostic, so it works
    for `mod x { }`, `fn f() { }`, `const X: u8 = 3;` and `use a::{b, c};`
    alike -- it is the token structure that decides, not a list of item kinds."""
    j, n, depth = i, len(code), 0
    while j < n:
        c = code[j]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and c == ";":
            return j + 1
        elif depth == 0 and c == "{":
            e = _bracket_end(code, j)
            return None if e is None else e
        j += 1
    return None


def _cfg_reaches_codegen(attr):
    """Does `#[cfg(P)]`'s predicate `P` mention a cfg any cell here sets?

    Direction matters and is deliberate. Answering "no" for code that IS built
    only WEAKENS the audit (a real forbidden spelling goes uncounted, which is
    the state the whole check was in before TASK_068). Answering "yes" for code
    that is NOT built HARD-FAILS an honest pattern -- TASK_068_REVIEW B1. So the
    unknown name is treated as unbuilt."""
    return any(w in CODEGEN_CFGS for w in _IDENT_RE.findall(attr)
               if w not in _CFG_WORDS)


def _blank_unbuilt_cfg(code):
    """Blank every item gated on a `#[cfg(...)]` no cell here compiles.

    This closes RECAP "Owed" 10 (`#[cfg(slb_twin)]` twin bodies: 43 attributes
    across 20 of 20 `verus.rs`) and the `#[cfg(test)]` shape TASK_068_REVIEW
    found beside it, and it closes them the same way, by asking *"does any cell
    set this cfg?"* rather than by naming the two attributes. `slb_isolated` is
    the one cfg a build does set, so an item gated on it is exec code and stays.

    It was hygiene while a hit only moved a printed counter; since TASK_068 a
    hit fails the run, which inverts the harm: a spelling that exists only in a
    trusted twin no build contains would block the pattern that discloses it."""
    out, i, n = list(code), 0, len(code)
    while i < n:
        m = _CFG_ATTR.match(code, i)
        if not m:
            i += 1
            continue
        end = _bracket_end(code, code.index("[", m.start()))
        if end is None:
            i = m.end()
            continue
        if _cfg_reaches_codegen(code[m.start():end]):
            i = end
            continue
        # skip any further attributes stacked on the same item
        j = end
        while True:
            k = j
            while k < n and code[k].isspace():
                k += 1
            a = _ATTR_START.match(code, k)
            if not a:
                break
            nxt = _bracket_end(code, code.index("[", a.start()))
            if nxt is None:
                break
            j = nxt
        stop = _item_end(code, j)
        _blank_span(out, m.start(), stop if stop is not None else n)
        i = stop if stop is not None else n
    return "".join(out)


def _blank_ghost_items(text, code):
    """Blank every `spec fn` / `proof fn` item, signature and body.

    Structural, not syntactic: `vparse.parse` already classifies items by kind
    and returns absolute offsets, so this asks the parser the gate's other
    stages ask rather than adding two more regexes. TASK_068_REVIEW B1 measured
    127 `spec fn` and 10 `proof fn` surviving into the audit, over 21 of 21
    Rust rung sources."""
    out = list(code)
    try:
        items = vparse.parse(text)
    except Exception:
        return code
    for it in items:
        if it.kind in ("spec fn", "proof fn") and it.start is not None \
                and it.body_end is not None:
            _blank_span(out, it.start, it.body_end + 1)
    return "".join(out)


def _blank_ghost_stmts(code):
    """Blank Verus ghost STATEMENTS inside exec bodies.

    `proof { ... }` blocks, `assert(...)` / `assert ... by { ... }` /
    `assume(...)`, `let ghost` / `let tracked` bindings and `Ghost(...)` /
    `Tracked(...)` constructions. Every one erases before codegen, which is
    `spelling_matches`' own stated reason for blanking clauses.

    ⚠ This is the one part of `exec_code` that is NOT structural -- see
    `exec_code`'s docstring for why, and for what would be."""
    out, i, n = list(code), 0, len(code)
    while i < n:
        m = _GHOST_LET.match(code, i)
        if m:
            j, depth = m.end(), 0
            while j < n:
                c = code[j]
                if c in "([{":
                    depth += 1
                elif c in ")]}":
                    if depth == 0:
                        break
                    depth -= 1
                elif c == ";" and depth == 0:
                    j += 1
                    break
                j += 1
            _blank_span(out, i, j)
            i = j
            continue
        m = _GHOST_CTOR.match(code, i)
        if m:
            e = _bracket_end(code, m.end() - 1)
            if e is not None:
                _blank_span(out, i, e)
                i = e
                continue
        m = _GHOST_STMT.match(code, i)
        if not m:
            i += 1
            continue
        kw, j = m.group(1), m.end()
        while j < n and code[j].isspace():
            j += 1
        if kw == "proof":
            # `proof fn` is an item and was blanked above; only `proof { ... }`
            # is a statement.
            if j >= n or code[j] != "{":
                i = m.end()
                continue
            e = _bracket_end(code, j)
            if e is None:
                i = m.end()
                continue
            _blank_span(out, m.start(), e)
            i = e
            continue
        # assert / assume: consume bracket groups, `forall`/`by`/`implies`
        # words and one trailing block, and stop at the `;` or at the `}` that
        # closes the enclosing body.
        j, stop = m.end(), None
        while j < n:
            c = code[j]
            if c.isspace():
                j += 1
            elif c in "([":
                e = _bracket_end(code, j)
                if e is None:
                    break
                j = e
            elif c == "{":
                e = _bracket_end(code, j)
                stop = j if e is None else e
                break
            elif c == ";":
                stop = j + 1
                break
            elif c in ")]}" or c == ",":
                stop = j
                break
            elif _IDENT_RE.match(code, j) or c in "|&<>=!+-*/%.:_":
                w = _IDENT_RE.match(code, j)
                j = w.end() if w else j + 1
            else:
                stop = j
                break
        _blank_span(out, m.start(), stop if stop is not None else j)
        i = (stop if stop is not None else j) or m.end()
    return "".join(out)


@functools.lru_cache(maxsize=512)
def exec_code(src, lang="rust"):
    """`src` with everything that does not reach a codegen unit blanked.

    Offset- and line-preserving, so a hit's line number is still the source's.
    Five layers, in order:

      1. comments and string/char literals (`vparse.blank_noncode`);
      2. items gated on a `#[cfg(...)]` no cell here builds (`CODEGEN_CFGS`);
      3. `spec fn` / `proof fn` items, by kind, from `vparse.parse`;
      4. Verus ghost CLAUSES -- `requires`/`ensures`/`invariant`/`decreases`
         and the rest of `_GHOST_KW`, on items and on loop headers alike;
      5. Verus ghost STATEMENTS -- `proof {}`, `assert`/`assume`, `let ghost`,
         `let tracked`, `Ghost(...)`, `Tracked(...)`.

    Layers 2-5 are Rust-only and skipped for `lang="c"`; blanking a C `assert(`
    would be wrong, since C's is exec code.

    **Why layers 2-5 exist at all, and it is one sentence, this function's
    own**: they erase before codegen, so they cannot carry the property a
    `forbidden` spelling is forbidden for. Layer 4 shipped with that
    justification (`spelling_matches` below quotes it verbatim); layers 2, 3
    and 5 are the same argument applied to the constructs it did not cover, and
    TASK_068_REVIEW B1 measured what they were worth once a hit began to FAIL:
    **11 of 14 honest shapes blocked**, with 275 `assert(`, 127 `spec fn`, 78
    `proof {` and 43 `#[cfg(slb_twin)]` surviving the audit across 21 of 21
    Rust rung sources. `patterns/p09-bitset/spec.md`'s `idiom.why` -- inside
    `contract_sha256` -- documents the trap and says p09's spec functions spell
    an index `q as int / 64` to dodge it: **the specification was contorted to
    keep an audit count at zero**, and after TASK_068 that contortion was the
    only thing keeping p09 green.

    ⚠ **Structural where the parser can answer, enumerated where it cannot, and
    the boundary is worth knowing** (TASK_069, answering the question the task
    file asked by name). Layers 2 and 3 are *structural*: "which items reach
    codegen" is answered by `vparse.parse`'s item kinds plus the cfg set
    `build.py` passes, so neither is a special case and neither grew out of a
    failure. Layer 5 cannot be: `proof`/`assert`/`ghost` are STATEMENTS inside
    an exec body, `vparse` models items and clauses only, and Verus's real
    exec/ghost boundary is a mode judgement made by its front end. The
    enumeration in `_blank_ghost_stmts` is closed and comes from the language's
    ghost grammar rather than from this project's incident history -- which is
    the difference that matters -- but it IS an enumeration. The only true
    oracle is Verus itself, and it is not available cheaply: the pinned build
    has no erased-source dump (`--log` offers VIR/AIR/SMT, no Rust), a Verus
    run costs minutes per pattern, and it would answer for `verus.rs` only
    while the audit spans all six rungs."""
    code = vparse.blank_noncode(src)
    if lang == "c":
        return code
    code = _blank_unbuilt_cfg(code)
    code = _blank_ghost_items(src, code)
    return _blank_ghost_stmts(_blank_ghost(code))


def spelling_matches(spelling, src, lang="rust"):
    """Does `src` spell `spelling`? The named-spelling standard's matching rule.

    This is the DEFINITION the standard's word "literal" refers to, and since
    TASK_068 it is also a gate check: `idiom_audit` calls it against every rung
    source and a `forbidden` hit FAILS the run (`forbidden_verdict`). Before
    TASK_068 nothing in this file called it against a rung source and this
    docstring said so; it was true then and is false now, and TASK_068_REVIEW
    m1 found it still saying it. It lives
    here, selftested at stage 0 and therefore inside `source_sha256`, because
    the standard's word "literal" was undefined for three tasks and **twenty
    shipped obligations turned on the gap** (TASK_018_REVIEW B1, TASK_019). A
    convention that lives only in prose drifts; one that is code and hashed
    cannot.

    Three parts, each forced by a shipped cell rather than chosen:

      * **whitespace is deleted from both sides.** `patterns/p17-http-range/spec.md`
        declares `2 + 2*nsuf > len`; all six p17 rungs write `2 + 2 * nsuf > len`.
        Six cells were out of their own contract on two space characters.
      * **comments and string literals are blanked**
        (`vparse.blank_noncode`). `patterns/p02-buffer-copy/c/kernel_hardened.c:10`
        and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own
        pattern's `forbidden` spelling in the comment that explains why they do
        not use it; and `patterns/p17-http-range/c/kernel.c` matches
        `2 + 2*nsuf > len` on raw text only because a comment spells it that way
        while the code writes the spaced form -- a match for the wrong reason.
      * **Verus ghost code is blanked.** It erases before codegen and its
        arithmetic is over unbounded `int`, so it cannot carry the overflow an
        additive spelling is forbidden for. Without this,
        `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end`
        makes p16's own R5 violate p16's `forbidden[0]` -- on the one pattern
        TASK_018_REVIEW called decidable. ⚠ **That sentence shipped covering
        CLAUSES only** while the same argument holds verbatim of `proof {}`
        blocks, `assert(...)`, `spec fn`/`proof fn` bodies, `let ghost` and
        code gated on a cfg no cell sets -- TASK_068_REVIEW B1, closed at
        TASK_069; `exec_code` above has the measurement and the five layers.

    What it does NOT decide, and no code can: the POLARITY of a quoted span
    (p02's `|`, p08's `&`, p17's `continue` are quoted in order to be absent)
    and the SET OF RUNGS an entry scopes to. Both live in the entry's English.

    ⚠ **Nor does it decide what a SUBSTRING is.** Matching is substring
    matching after whitespace deletion, so a `forbidden` entry that backticks
    `strlen(` also matches an honest `slb_strlen(`, `position(` matches
    `rposition(`, `split` matches `split_first`, and `q / 64` matches
    `freq / 64`. Those are not false positives of the blanking -- they are the
    entry quoting a span that is genuinely present -- so they are the author's
    to write more specifically (`= strlen(`, ` v.split(`), and
    `forbidden_verdict`'s failure text names them."""
    return _WS.sub("", spelling) in _WS.sub("", exec_code(src, lang))


_WS = re.compile(r"\s+")


def idiom_entry_text(entry, lang=None):
    """One entry's text: the string itself, or the per-language spelling.

    With `lang=None` an object entry renders as `c: ... | rust: ...` so the
    verdict prints every spelling a reviewer would have to check."""
    if isinstance(entry, str):
        return entry
    if lang is not None:
        return entry.get(lang, "")
    return " | ".join(f"{k}: {entry[k]}" for k in sorted(entry))


def idiom_problems(contract):
    """Structural check on the `idiom` key. Presence, never semantics.

    TASK_016, from TASK_015_REVIEW B2. `patterns/p05-index-flatten/spec.md`
    forbids `chunks_exact` and a strength-reduced row pointer **by name**, and
    says a rung that deviates "is a different benchmark and its numbers are not
    comparable" -- but it says it in prose at line 69 while the hashed block
    starts at line 309, so `contract_sha256` was blind to it. Two consecutive
    tasks then measured a forbidden spelling and published the result as p05's
    number. This is the only check in the gate whose "could this happen by
    accident?" answer is *it already did, twice, to two different agents*.

    What this does NOT do is check that a rung honours its idiom. Grepping
    `safe_tuned.rs` for `chunks_exact` fails open -- a strength-reduced row
    pointer has no token to grep for -- and the threat model is honest mistake,
    not malicious author (`.memory/02-bench-rules.md`).

    TASK_016 claimed here that "changing a rung's idiom must now move
    `contract_sha256`". **That is false and TASK_016_REVIEW B1 proved it by
    experiment**: a p05 fork whose `safe_tuned.rs` was swapped for the
    *forbidden* `chunks_exact` spelling produced a complete green run -- `PASS`,
    `complete_run: true`, `failures: []` -- with `contract_sha256`
    byte-identical to the shipped pattern's, certifying `R3 - R4 = -12/-58` as
    p05 while printing the declaration that forbids it three lines above the
    PASS. `read_contract()` hashes `spec.md`'s fenced block and nothing else.

    What the key actually buys, which is narrower and still worth having:

      * the declaration is REQUIRED, so a pattern cannot ship without stating
        what its rungs are spellings *of*;
      * it is VISIBLE -- printed in the verdict and in the failure summary, and
        copied into every committed `results/gate/*.json`;
      * it is HASHED, so *weakening or editing the declaration* -- the move that
        licenses a swap -- shows up as a one-line `contract_sha256` change in a
        committed artefact, which is a signal review already reads.

    Rung sources are covered by `source_sha256`, not by this key. Nothing here
    prevents a forbidden respelling and nothing can without semantic checking,
    which the threat model forbids. Say that, and do not restore the stronger
    sentence.

    `forbidden` MAY be empty. A pattern with no meaningful spelling restriction
    must be able to say so and pass -- `MAX_TWIN_JUSTIFICATIONS` was deleted at
    TASK_007 precisely because it could hard-fail an honest pattern with no
    route out -- so an empty `forbidden` is shouted, not failed. `required` may
    not be empty: with nothing required there is no matched pair, and a
    matched-pair delta is the only thing that can carry a safety number
    (`.memory/06-catalogue.md`).

    TASK_019 admits a second entry shape: an object keyed by language
    (`IDIOM_LANGS`) instead of a string, matched per rung against its own
    language's spelling. One string cannot name a check whose operands are
    `src_len` in C and `src.len()` in Rust -- the C signature carries a length
    parameter the Rust signature does not -- and the prose clause that used to
    paper over that was measured not to fire (TASK_018_REVIEW B1). The keys are
    closed and every declared key must be non-empty, because the accident this
    shape invites is a typo'd language key that silently pins nothing: the same
    accident `forbid`-for-`forbidden` invites, and the reason that case is in
    `_IDIOM_CASES`. Still presence only -- no stage matches an entry against a
    rung."""
    idi = contract.get("idiom")
    if not isinstance(idi, dict):
        return ["spec.md's slb-contract block has no `idiom` object. Every "
                "pattern declares the idiom its rungs implement, inside the "
                "hashed block -- see patterns/p05-index-flatten/spec.md -- as "
                '{"required": [...], "forbidden": [...], "why": "..."}']
    probs = []
    unknown = sorted(set(idi) - set(IDIOM_KEYS))
    if unknown:
        probs.append(f"idiom has unknown key(s) {unknown}; expected exactly "
                     f"{list(IDIOM_KEYS)} -- a mistyped key is silently empty")
    for k in ("required", "forbidden"):
        v = idi.get(k, [])
        if not isinstance(v, list):
            probs.append(f"idiom.{k} must be a list, got {v!r}")
            continue
        for e in v:
            if isinstance(e, str):
                if not e.strip():
                    probs.append(f"idiom.{k} has an empty entry -- that is a "
                                 f"typo, not a declaration")
            elif isinstance(e, dict):
                bad = sorted(set(e) - set(IDIOM_LANGS))
                if bad:
                    probs.append(
                        f"idiom.{k} entry has unknown language key(s) {bad}; "
                        f"expected a subset of {list(IDIOM_LANGS)} -- a "
                        f"mistyped language key pins nothing for that language")
                if not e:
                    probs.append(f"idiom.{k} has an empty per-language entry")
                if any(not isinstance(s, str) or not s.strip()
                       for s in e.values()):
                    probs.append(f"idiom.{k} per-language entry {sorted(e)} has "
                                 f"an empty spelling")
            else:
                probs.append(f"idiom.{k} entries must be a non-empty string or "
                             f"an object keyed by {list(IDIOM_LANGS)}, got {e!r}")
    if not idi.get("required"):
        probs.append("idiom.required is empty -- name what every rung must "
                     "implement, in the pattern's own terms")
    if not isinstance(idi.get("why"), str) or not idi["why"].strip():
        probs.append("idiom.why is empty -- state what a deviating rung would "
                     "delete, and, when `forbidden` is empty, why nothing is "
                     "excluded")
    return probs


#: The shared NAMED-SPELLING STANDARD paragraph, located by its own first and
#: last words. Every pattern's `idiom.why` ends with it (p17 carries pattern text
#: after it), byte-identical, and it is the text that DEFINES what a backticked
#: `required`/`forbidden` entry means: that it pins THAT SPELLING, and the
#: three-part matching rule `spelling_matches` implements. A pattern that pins a
#: backticked spelling without carrying it has pins its own contract never
#: defines.
NAMED_SPELLING_BEGIN = "NAMED-SPELLING STANDARD"
NAMED_SPELLING_END = "p01 and p08 neither"

#: sha256 of that paragraph, MEASURED at TASK_062 over the 17 patterns that
#: carried it -- p01..p14, p16, p17, p18 -- on 2026-08-22, and 11003 bytes long.
#: p27 is the eighteenth and did not carry it at all: it shipped at TASK_060 with
#: 2607 bytes of its own `why` and no paragraph, pinning 62 backticked spellings
#: whose meaning its own contract therefore did not state, and it survived three
#: tasks and two adversarial reviews before the manager's standing one-liner
#: found it.
#:
#: WHY A PINNED CONSTANT AND NOT A CROSS-PATTERN READ. Reading the paragraph out
#: of a sibling `spec.md` at run time is self-maintaining, and it was rejected for
#: three measured reasons:
#:
#:   * it FAILS OPEN in the one direction that matters. If the paragraph is
#:     dropped from every pattern -- or from whichever one the reader picks --
#:     the comparison succeeds against nothing and 18 gates go green on a tree
#:     where the standard has evaporated. Vacuous success is the exact failure
#:     this check exists to close.
#:   * it puts a pattern's verdict outside that pattern's record. `check.py pNN`
#:     hashes `harness/*.py` plus pNN's own files into `source_sha256`; a sibling
#:     `spec.md` is in neither list, so the text a run was judged against would
#:     not be recoverable from the run's own artefact. The constant IS in that
#:     list -- editing this line moves `source_sha256["harness/check.py"]` in all
#:     18 committed gate records, which is a diff review already reads.
#:   * it makes a single-pattern gate depend on 17 files the pattern does not
#:     own, so a mid-edit `spec.md` anywhere moves an unrelated verdict.
#:
#: The cost of a constant is that an amendment to the standard must move this
#: line too. That is not rot, it is the point: the standard has been amended
#: twice (TASK_019's repair, TASK_028's withdrawal), each time across every
#: pattern at once and each time paying a full sweep because `contract_sha256`
#: moves everywhere anyway. One extra line in that same commit buys detection of
#: a PARTIAL amendment -- 17 patterns edited and one forgotten -- which is p27's
#: accident with the sign flipped and which nothing else in the tree would see.
NAMED_SPELLING_SHA256 = \
    "59748cce2db5c57258677242cd59ff7e9766817bb659e7a874038d21f7150a7d"
NAMED_SPELLING_LEN = 11003

#: Reproduces this pin from the tree; printed in the failure so the repair is in
#: the message. It reads raw `spec.md` text, which equals the parsed `idiom.why`
#: span because the paragraph contains no character JSON escapes (measured:
#: 11003 bytes, all ASCII, no `"` and no backslash).
NAMED_SPELLING_ONELINER = (
    "python3 -c \"import hashlib,glob;print({hashlib.sha256(open(f).read()"
    "[open(f).read().find('NAMED-SPELLING STANDARD'):open(f).read()"
    ".find('p01 and p08 neither')+19].encode()).hexdigest()[:12] "
    "for f in glob.glob('patterns/*/spec.md')})\"   # -> a set of size 1")


def named_spelling_problem(contract, want=NAMED_SPELLING_SHA256):
    """Does this pattern's `idiom.why` carry the shared paragraph, verbatim?

    TASK_062. Returns a message or `None`. `want` is a parameter only so the
    selftest can exercise the matching branch without a second copy of 11 KB of
    prose in this file; every caller uses the pin.

    **This is stricter than the one-liner it mechanises, in the one way that
    matters.** The one-liner greps `spec.md` as a file, so it is satisfied by a
    copy pasted into the prose ABOVE the fenced block -- which is
    `patterns/p05-index-flatten/spec.md`'s original accident exactly: a
    declaration that lived at line 69 while the hashed block started at line 309,
    so `contract_sha256` was blind to it and two tasks published a forbidden
    spelling as p05's number (`idiom_problems`). This reads
    `contract["idiom"]["why"]`, i.e. the parsed value inside the hashed block, so
    a paragraph outside it does not count.

    **The accident test (`PROTOCOL.md` rule 5) has an instance, not an
    argument**, and the instance passes `.memory/02-bench-rules.md`'s own
    follow-up rule -- *before citing an incident as an accident-test precedent,
    check that the proposed check could have SEEN it.* This one sees p27
    directly: p27's `idiom.why` is 2607 bytes of pattern-specific text with no
    `NAMED-SPELLING STANDARD` in it, so the first branch below fires on the
    shipped tree at `676f685`. That is the contrast with `forbidden_hits`, which
    was proposed as a hardening at TASK_053 and DECLINED at TASK_056 because it
    was structurally blind to the accident it cited.

    Hard failure, not a shout, because there is no honest pattern that cannot
    comply -- `.memory/02-bench-rules.md` warns against a new hard failure with
    no route out, and the route out here is `cp` from any sibling. The two
    patterns that pin no spelling at all, p01 and p05, both carry it, and the
    paragraph's own text is about them (`required` in p01 and p05 contains no
    backticks at all), so it is load-bearing even where `spellings == 0`."""
    idi = contract.get("idiom")
    why = idi.get("why") if isinstance(idi, dict) else None
    if not isinstance(why, str):
        return None                 # `idiom_problems` has already failed on it
    i, j = why.find(NAMED_SPELLING_BEGIN), why.find(NAMED_SPELLING_END)
    if i < 0 or j < 0:
        return (f"idiom.why does NOT carry the shared named-spelling paragraph "
                f"({NAMED_SPELLING_LEN} bytes, "
                f"sha256 {NAMED_SPELLING_SHA256[:12]}..., from "
                f"'{NAMED_SPELLING_BEGIN}' to '{NAMED_SPELLING_END}'). Every "
                f"pattern's `why` ends with it, byte-identical, and it is what "
                f"DEFINES what a backticked `required`/`forbidden` entry pins -- "
                f"that spelling, not merely the property -- and the three-part "
                f"matching rule `spelling_matches` implements. Without it this "
                f"pattern's backticked pins are undefined by its own contract. "
                f"Copy it verbatim from any other pattern's `idiom.why`, "
                f"INCLUDING its stale 'all six patterns' phrase, which is "
                f"historical and inside the hashed block. Reproduce this pin "
                f"with:\n      {NAMED_SPELLING_ONELINER}")
    got = why[i:j + len(NAMED_SPELLING_END)]
    h = hashlib.sha256(got.encode()).hexdigest()
    if h != want:
        return (f"idiom.why carries the named-spelling paragraph but it is "
                f"ALTERED: {len(got)} bytes, sha256 {h[:12]}..., against the "
                f"pinned {want[:12]}.... The "
                f"paragraph is byte-identical in every pattern by construction, "
                f"so either this copy drifted or the standard was amended in "
                f"ONE pattern instead of all of them. If the amendment is "
                f"intended, apply it to every `spec.md` and move "
                f"`NAMED_SPELLING_SHA256` in the same commit; the sweep is owed "
                f"either way, because `contract_sha256` moves everywhere. "
                f"Diff against a sibling with:\n      "
                f"{NAMED_SPELLING_ONELINER}")
    return None


#: `named_spelling_problem` selftests (TASK_062). A synthetic paragraph, so the
#: matching branch is covered without a nineteenth copy of the real text; the
#: real text's positive case is every one of the 18 gate runs.
_NS_SYN = (f"{NAMED_SPELLING_BEGIN} -- synthetic, for the selftest only. "
           f"... and on the R4 side ONLY p05 and p16, and {NAMED_SPELLING_END}")
_NS_SYN_SHA = hashlib.sha256(_NS_SYN.encode()).hexdigest()

_NAMED_SPELLING_CASES = [
    ("absent is a failure -- p27 at 676f685",
     bool(named_spelling_problem(
         {"idiom": {"why": "POLICY ADOPTED AFTER MEASURING: the tokens above "
                           "must appear literally."}})), True),
    ("present and byte-identical passes",
     named_spelling_problem({"idiom": {"why": f"prose. {_NS_SYN}."}},
                            want=_NS_SYN_SHA), None),
    ("present with pattern text after it still passes -- p17's shape",
     named_spelling_problem({"idiom": {"why": f"prose. {_NS_SYN}. WHAT THE "
                                              f"STANDARD SAYS ABOUT p17..."}},
                            want=_NS_SYN_SHA), None),
    ("one word changed inside it is ALTERED, not absent",
     "ALTERED" in (named_spelling_problem(
         {"idiom": {"why": _NS_SYN.replace("ONLY", "only")}},
         want=_NS_SYN_SHA) or ""), True),
    ("a truncated copy is ALTERED too",
     "ALTERED" in (named_spelling_problem(
         {"idiom": {"why": _NS_SYN[:40] + " " + NAMED_SPELLING_END}},
         want=_NS_SYN_SHA) or ""), True),
    # Shape errors belong to `idiom_problems`; this one must not double-report.
    ("a non-string why is idiom_problems' business, not this check's",
     named_spelling_problem({"idiom": {"why": 3}}), None),
    ("no idiom key at all is idiom_problems' business too",
     named_spelling_problem({}), None),
]


def idiom_lines(contract, keys=("required", "forbidden"), why=True):
    """The declaration itself, for the verdict: a reviewer reading a run sees
    what was declared without opening `spec.md`.

    `keys`/`why` narrow it: the failure summary reprints the `forbidden` list
    alone, because a failing run is the output somebody copies out of a
    terminal and the declaration has to travel with it (TASK_017 Part 2)."""
    idi = contract.get("idiom") or {}
    out = []
    for k, tag in (("required", "REQUIRED "), ("forbidden", "FORBIDDEN")):
        if k not in keys:
            continue
        for e in idi.get(k) or []:
            out += textwrap.wrap(idiom_entry_text(e), 92,
                                 initial_indent=f"    idiom {tag} ",
                                 subsequent_indent=" " * 20)
        if not (idi.get(k) or []):
            out.append(f"    idiom {tag} (none declared)")
    if why:
        out += textwrap.wrap(idi.get("why") or "", 92,
                             initial_indent="    idiom WHY       ",
                             subsequent_indent=" " * 20)
    return out


#: A backticked span inside an entry, which is what the standard's own trigger
#: names: "where a `required` entry quotes an expression **in backticks** it
#: pins THAT SPELLING".
_TICK = re.compile(r"`([^`]+)`")


def rung_sources(pdir):
    """`[(relpath, language)]` for every rung source this pattern ships.

    Derived from `build.py`'s cell tables, not from a list here, so a pattern
    that ships no `c/kernel_hardened.c` or no `safe_naive_verus.rs` reports on
    what it has -- the same "presence of the file is the whole switch" rule
    `build.all_cells` follows."""
    out = [(os.path.join("c", "kernel.c"), "c")]
    if buildmod.has_hardened(pdir):
        out.append((buildmod.HARDENED_KERNEL, "c"))
    for cell in buildmod.MEASURED_CELLS + buildmod.CONTROL_CELLS:
        rel = buildmod.RUST_SRC.get(cell)
        if rel and os.path.exists(os.path.join(pdir, rel)):
            out.append((rel, "rust"))
    return [(r, l) for r, l in out if os.path.exists(os.path.join(pdir, r))]


def forbidden_only_sources(pdir):
    """Sources audited for `forbidden` but NOT for `required`.

    `c/kernel.h` is `#include`d into the C rung and compiled with it, so a
    kernel body moved into a `static inline` there would leave the audit
    entirely -- the honest-refactor escape route TASK_068_REVIEW m7 named. It
    is closed for the half where scope is decidable, and only that half:

      * `forbidden` is universal by the key's own meaning -- *no* compiled code
        may spell the token -- and the header is compiled code, so scanning it
        adds hits and nothing else. Measured at TASK_069: **0 hits over 197
        spellings**, and no `kernel.h` in the tree contains a `static inline`
        yet;
      * `required` is scoped by the entry's English, and a header holds
        prototypes rather than implementations, so every C spelling would be
        "absent" from it. Measured: adding `c/kernel.h` to `rung_sources`
        outright takes `required_absent` from **94 to 301** tree-wide, 207 rows
        of noise in the one bucket whose value is that a non-zero is worth
        reading. Adding `c/main.c` as well takes it to **507**. Declined for
        that half, deliberately, and the measurement is the reason.

    `c/main.c` is not here either: it is the driver, identical in shape across
    all 20 patterns, and it implements no kernel."""
    return [(r, "c") for r in (os.path.join("c", "kernel.h"),)
            if os.path.exists(os.path.join(pdir, r))]


def idiom_audit(contract, rungs, extra=()):
    """Where each declared spelling is, and is not, in the tree.

    `rungs` is `[(relpath, language, source_text)]`; `extra` is the same shape
    for sources audited against `forbidden` ONLY -- today `c/kernel.h`, see
    `forbidden_only_sources` for why that split is measured rather than chosen.
    `extra` deliberately does NOT enter `pairs` or `present`, which are
    `required`'s numbers and are compared against committed records.
    This function itself is
    pure: it computes and returns, it never calls `rep`. **Its `forbidden_hits`
    are failed by `check_idiom`** (TASK_068); everything else it returns is an
    observation printed into the record so that a reviewer can read it, and so
    that `results/gate/*.json` carries a number whose movement a diff shows.

    **Why this exists.** TASK_019 audited all six declarations against every
    rung and found **20 raw / 15 comment-stripped / 9 normalised violations of
    78 obligations**, then repaired them to 0 of 82. That audit lived in a
    hand-transcribed table in a gitignored scratch file, so "0 of 82" was a
    claim nothing in the tree reproduced -- the self-certifying-pin trap, one
    level up. "Could this happen by accident?" is answered by the twenty.

    **Why `forbidden` gets a verdict and `required` does not.** This is the one
    asymmetry that makes the line readable, and it is measured rather than
    chosen. `forbidden`'s scope is universal by the key's own meaning: no rung
    may spell it, in any language it declares, so `forbidden_hits` is decidable
    with no English involved -- and it has teeth, because on the shipped tree
    raw substring matching gives **5** hits and `spelling_matches` gives **0**;
    the five are two hardened-C comments quoting the spelling they refuse,
    p16's verus.rs GHOST loop invariant, and p17's `Range:` inside a comment and
    a format string. That 0 is the reproducible core of TASK_019's number.

    **FAIL, not print -- settled at TASK_068, and here is the accident test.**
    `.memory/02-bench-rules.md`'s threat model requires a new gate check to
    answer *"could this defect happen BY ACCIDENT?"* first. Answer: **yes, and
    it is not hypothetical -- it happened, it shipped, and it was invisible for
    three tasks.** p27 forbade `` `memset(tab` `` and both of its own C rungs
    spelled it (`c/kernel.c:66-67`, `c/kernel_hardened.c:46-47`): nobody wrote
    that on purpose, and the entry itself turned out to be the wrong half --
    every rung must zero the table, the four Rust rungs are FORCED to, so a
    universal-scope `forbidden` excluded an operation the whole ladder performs
    (TASK_063 deleted the entry as a declaration edit with a byte-provable
    undo). Two further facts decided the direction:

      * **A number that is printed is not a check.** That `2` was printed in the
        verdict, written into `results/gate/p27-handle-table.json` and
        transcribed into `NOTES.md`, across three tasks and two adversarial
        reviews, and nobody acted on it.
      * **The false-positive surface is nil today**: `forbidden_hits` is **0**
        across all 20 patterns. ⚠ **Every denominator below is RECOMPUTABLE and
        none of them is a constant** -- `.temp/p69/audit_probe.py` prints the
        whole table from the committed tree, and TASK_068 shipped this
        paragraph quoting *183 spellings* and *29 hits across 11 patterns*,
        both transcribed rather than measured and both wrong against artefacts
        in their own commit (TASK_068_REVIEW M3). Re-measured at TASK_069:
        **197 backticked forbidden spellings over 111 entries**, and the same
        sweep on RAW text gives **40 hits across 13 patterns** (blanking
        comments and string literals only leaves **2 across 2**). The invariant
        is the ZERO; the 40 is what `exec_code` is worth, and it is what a
        naive implementation would fail on.

    ⚠ **The counter-argument, recorded because it is right about strength and
    wrong about direction** (TASK_063's own engineer): a failure here is
    dischargeable by the WRONG fix -- respell the rung at 0.0000 `Ir`/call --
    leaving the real defect (an entry whose `why` never said what it forbids
    *for*) in place. True. But a respelling at least moves `source_sha256` in a
    commit, whereas the printed number moved nothing for three tasks; **weak
    forcing beats none**, and the check is not being asked to judge the entry's
    English, only to make the contradiction impossible to walk past.

    ⚠ **The false-positive shapes, corrected at TASK_069, because TASK_068
    named two and there were at least seven.** Both of the two it named were
    wrong on their own terms: the `#[cfg(slb_twin)]` one was real and is now
    CLOSED (`exec_code` layer 2), and the other said `rung_sources` includes
    `CONTROL_CELLS` *"which no pattern ships"* -- **p01 ships
    `safe_naive_verus.rs` and it is p01's 6th audited rung**, which one `ls`
    refutes (TASK_068_REVIEW M1; `.memory/02-bench-rules.md:196`, where it was
    copied from, is corrected too). What remains, and what a debugger reading a
    hit should check in this order:

      * **a hit in the CONTROL cell.** `safe_naive_verus.rs` is a control, not
        a rung of the ladder -- by construction a different implementation --
        so a `forbidden` entry scoped to the ladder can hit it honestly. p01
        ships one; 0 tokens hit it today.
      * **substring matching**, which `spelling_matches` documents: `strlen(`
        matches `slb_strlen(`, `position(` matches `rposition(`, `split`
        matches `split_first`, `q / 64` matches `freq / 64` after whitespace
        deletion. The entry is quoting a span that really is present; write a
        longer one.
      * **an entry that backticks its REPLACEMENT.** `required` entries are
        written that way all over the tree (`written `%` and not `&`), and in a
        `forbidden` entry *every* backticked span becomes a banned token, so
        `` `strcpy(` -- use `memcpy(` instead `` forbids `memcpy(` too.

    Ghost code, cfg-gated code, comments and string literals are NOT on this
    list any more: `exec_code` blanks all five layers, measured at TASK_069.

    `required` has no such scope. Which rungs an entry applies to lives in its
    English -- "R1 has no fit check at all", "R1 omits only `&& start >= 0`" --
    and TASK_020 measured what happens if you ignore that and assert every
    backticked span in every rung of the declared languages: **41 misses out of
    158 obligations, and all 41 are non-defects** (the tree was at 0 violations
    when it was measured). Worse than noise, 17 of the 41 are ANTI-signal: a
    `required` entry may quote a span in order to say it is ABSENT --
    p08's "written `%` and not `&`", p17's "not two `continue`s", p02's "with
    `+`, not `|`" -- and for those the verdict inverts. The naive line prints
    `&` as a MISS on p08's two C rungs, which are the rungs that are right, and
    counts it MATCHED on the four Rust rungs where every hit is a reference
    sigil; **9 of its 117 "matched" are matched for the exactly wrong reason**
    (p02's `|` in `c/kernel_hardened.c` and all four Rust rungs -- it is in the
    `||` of the guard -- plus p08's `&` in four). So `required` is reported as
    PRESENCE, in two shapes, and the reader judges against the entry beside it:

      * `pins_nothing` -- present in **no** rung of a language it declares.
        This is the class that carries real defects, and it catches both ruler
        bugs TASK_019 found: run against the pre-repair declarations at
        `9e2f9f6`, p17's ellipsis `if start < end && start >= 0 { ... }` pins
        nothing in either language, and p02's single-string `required[0]` pins
        nothing on Rust in three of its spellings -- exactly the per-language
        defect the repair fixed. The count moved **16 -> 11** across it.
      * `absent` -- present in some rungs of that language and not others, i.e.
        the entry is scoped and the reader should check the scope.

    The residual `pins_nothing` on the shipped tree are all expected. ⚠ **The
    count is 16 as of TASK_069 and it is RECOMPUTABLE, not a constant** --
    `.temp/p69/audit_regress.py` prints it and the per-entry rows beside the
    committed records; this paragraph said *"11 ... split 6/5"* while the tree
    summed to 15, because p27, p38 and p47 shipped after it was written. They
    split **11 / 5**: eleven are prose references that happen to be backticked
    (`c/kernel.c`, `adversarial-overrun.bin` twice, `md5_fn e207ec6c8697...`,
    the word `why` twice, p27's `vstd::raw_ptr::deallocate`, `deallocate`,
    `malloc` and `align <= 8`, p47's `bcmp`) and five are spans quoted in order
    to be absent (`src_len`, `dst_cap`, `&`, `continue` twice). **A non-zero
    here is normal**; what is worth reading is a change.

    ⚠ **Two of those rows arrived at TASK_069 and they are the ghost-blanking
    fix working on the `required` half**, which is worth knowing because that
    half is presence-only and cannot fail: p27's `deallocate` was spelled in
    exactly one place in the whole tree, its `#[cfg(slb_twin)]` verified twin
    (`verus.rs:558`), and a twin is in no build -- so the entry read as PRESENT
    on the strength of code no cell compiles, which is precisely the false
    *satisfaction* RECAP "Owed" 10 predicted. ⚠ **That finding now lives in
    `patterns/p27-handle-table/NOTES.md` 13e, where a reader of p27 will meet
    it** (TASK_082, RECAP "Owed" 18); it sat in this docstring alone for
    thirteen tasks. p12's `.wrapping_add(nstr as u64)`
    was matched only inside `spec fn fin` (`verus.rs:178`) and is now correctly
    scoped-absent on `verus.rs`. Tree-wide, `required_absent` moved 96 -> 94 and
    `pins_nothing` 15 -> 16; no `forbidden_hits` moved, from 0.

    **`no_rung` -- a fourth bucket, closed at TASK_021.** A per-language entry
    may name a language this pattern ships no rung for. Before TASK_021 that
    key was dropped by the `if l in langs` filter with no trace: the entry
    would print as pinning whatever its *other* key pins, and the declaration
    would read as constraining six rungs while constraining three. It is
    **unreachable on the shipped tree** -- all six patterns ship both languages,
    so `langs == ['c', 'rust']` everywhere and this bucket is 0 in all six
    records -- and that is exactly the argument for closing it now: it is
    invisible until the first Rust-only (or C-only) pattern, and on that day it
    is silent rather than loud. It reports rather than fails, because a
    declaration written against a rung the pattern deliberately does not ship
    (a pattern whose C rung is the *point* and whose Rust side is future work)
    is an honest state, and the threat model is honest mistake
    (`.memory/02-bench-rules.md`: a new hard failure with no route out is how
    gates get switched off). It is deliberately **not** folded into
    `pins_nothing`: that bucket means "no rung of a language this pattern HAS
    spells this", which is a defect in the ruler; this one means "there is no
    rung to ask", which is a fact about the pattern's shape."""
    langs = sorted({l for _, l, _ in rungs})
    text = {(r, l): s for r, l, s in rungs}
    xtext = {(r, l): s for r, l, s in extra}
    n_sp = n_pair = n_present = n_forb_sp = 0
    pins_nothing, absent, hits, no_rung, unaudited = [], [], [], [], []
    for key in ("required", "forbidden"):
        for i, e in enumerate(contract.get("idiom", {}).get(key) or []):
            per = ({l: e for l in langs} if isinstance(e, str)
                   else {l: v for l, v in e.items() if l in langs})
            if isinstance(e, dict):
                # The dropped keys, named instead of discarded (TASK_021).
                for lang in sorted(set(e) - set(langs)):
                    if lang not in IDIOM_LANGS:
                        continue        # a typo; `idiom_problems` already failed
                    no_rung.append({"entry": f"{key}[{i}]", "lang": lang,
                                    "spellings": _TICK.findall(e[lang])})
            n_entry_sp = 0
            for lang in sorted(per):
                for tok in _TICK.findall(per[lang]):
                    here = [r for r, l in sorted(text) if l == lang]
                    on = [r for r in here
                          if spelling_matches(tok, text[(r, lang)], lang)]
                    off = [r for r in here if r not in on]
                    n_sp += 1
                    n_entry_sp += 1
                    n_pair += len(here)
                    n_present += len(on)
                    row = {"entry": f"{key}[{i}]", "lang": lang,
                           "spelling": tok}
                    if key == "forbidden":
                        n_forb_sp += 1
                        for r in on:
                            hits.append(dict(row, rung=r))
                        for r, l in sorted(xtext):
                            if l == lang and spelling_matches(
                                    tok, xtext[(r, l)], l):
                                hits.append(dict(row, rung=r))
                    elif not on:
                        pins_nothing.append(dict(row, of_rungs=len(here)))
                    else:
                        for r in off:
                            absent.append(dict(row, rung=r))
            # TASK_069, from TASK_068_REVIEW M2. PER ENTRY, because the shout
            # this feeds used to fire only when EVERY entry lacked a backtick:
            # p08 (3 of 4), p16 (1 of 2) and p17 (2 of 3) took the `ok` branch
            # and printed "0 hit(s) over N forbidden spelling(s) ... Decidable
            # and ENFORCED" while most of the declaration was audited zero
            # times. The list of 2 was a list of 5.
            if key == "forbidden" and n_entry_sp == 0:
                unaudited.append({"entry": f"forbidden[{i}]",
                                  "text": idiom_entry_text(e)})
    return {"spellings": n_sp, "rungs": len(rungs), "pairs": n_pair,
            "present": n_present, "languages": langs,
            "forbidden_only_sources": sorted(r for r, _ in xtext),
            "forbidden_spellings": n_forb_sp, "forbidden_hits": len(hits),
            "hits": hits,
            "forbidden_unaudited_entries": len(unaudited),
            "forbidden_unaudited": unaudited,
            "required_pins_nothing": len(pins_nothing),
            "pins_nothing": pins_nothing,
            "required_absent": len(absent), "absent": absent,
            "no_rung_entries": len(no_rung), "no_rung": no_rung}


def idiom_audit_lines(au):
    """The audit as text for the verdict. Every list is printed in full so a
    miss travels with its reason. The `required` half is data -- no `FAIL`, no
    `!!`. The `forbidden` half is a verdict since TASK_068 and `check_idiom`
    raises it separately, so a FORBIDDEN HIT line below always has a
    `rep.fail("idiom-forbidden", ...)` beside it."""
    # NOT `spellings x rungs`: a per-language entry is read against its own
    # language's rungs only, so the product is not the pair count.
    out = [f"    audit  {au['spellings']} backticked spelling(s) over "
           f"{au['rungs']} rung(s) -> {au['pairs']} (spelling, rung) pair(s), "
           f"{au['present']} present  [the `required` numbers never fail]",
           f"    audit  forbidden: {au['forbidden_spellings']} spelling(s), "
           f"{au['forbidden_hits']} hit(s), "
           f"{au.get('forbidden_unaudited_entries', 0)} entry/entries with NO "
           f"backticked spelling  "
           f"(decidable: no rung may spell a forbidden token -- a hit FAILS; "
           f"also scanned, for `forbidden` only: "
           f"{au.get('forbidden_only_sources') or 'none'})",
           f"    audit  required : {au['required_pins_nothing']} pin nothing, "
           f"{au['required_absent']} scoped-absent pair(s)  "
           f"(NOT decidable -- an entry's rung scope is its English; a "
           f"non-zero here is normal, read it against the entry)",
           f"    audit  languages: rungs in {au.get('languages', [])}; "
           f"{au.get('no_rung_entries', 0)} per-language entry/entries name a "
           f"language this pattern ships NO rung for "
           f"(TASK_021: reported, not dropped)"]
    for n in au.get("no_rung") or []:
        out.append(f"    audit    NO RUNG       {n['entry']:<13}{n['lang']:<5}"
                   f"pattern ships no {n['lang']} rung  "
                   f"{n['spellings'] or 'no backticked spelling'}")
    for h in au["hits"]:
        out.append(f"    audit    FORBIDDEN HIT {h['entry']:<13}{h['lang']:<5}"
                   f"{h['rung']:<22}`{h['spelling']}`")
    for u in au.get("forbidden_unaudited") or []:
        out.append(f"    audit    NOT AUDITED   {u['entry']:<13}{'':<5}"
                   f"{'no backticked span':<22}{u['text'][:44]}")
    for p in au["pins_nothing"]:
        out.append(f"    audit    pins nothing  {p['entry']:<13}{p['lang']:<5}"
                   f"0 of {p['of_rungs']} rung(s){'':<9}`{p['spelling']}`")
    for x in au["absent"]:
        out.append(f"    audit    absent        {x['entry']:<13}{x['lang']:<5}"
                   f"{x['rung']:<22}`{x['spelling']}`")
    return out


def check_idiom(rep, pdir, contract):
    head("0b. the pattern declares the idiom its rungs implement")
    probs = idiom_problems(contract)
    for p in probs:
        rep.fail("idiom", p)
    if probs:
        return None
    # TASK_062. The shared paragraph is what makes a backticked pin MEAN
    # something; a pattern that pins spellings without it pins nothing its own
    # contract defines. Reported after the structural problems so a broken
    # `idiom` does not produce two failures for one cause, and NOT returning --
    # the run continues and the record is complete, the way every other
    # `rep.fail` in this stage behaves.
    ns = named_spelling_problem(contract)
    if ns:
        rep.fail("idiom-named-spelling", ns)
    else:
        rep.ok(f"named-spelling standard present in idiom.why, verbatim "
               f"({NAMED_SPELLING_LEN} bytes, sha256 "
               f"{NAMED_SPELLING_SHA256[:12]}...) and therefore inside "
               f"contract sha256 -- so what this pattern's backticked pins MEAN "
               f"is hashed alongside the pins themselves.")
    idi = contract["idiom"]
    nreq, nforb = len(idi["required"]), len(idi.get("forbidden") or [])
    nlang = sum(1 for k in ("required", "forbidden")
                for e in idi.get(k) or [] if isinstance(e, dict))
    rep.ok(f"idiom declared: {nreq} required, {nforb} forbidden spelling(s), "
           f"{nlang} of them per-language, hashed into contract sha256. "
           f"Presence only -- no stage here checks that a rung honours it. "
           f"Text in the verdict.")
    if nforb == 0:
        rep.shout("idiom", "this pattern forbids no spelling by name, so its "
                           "rungs are matched only by the `required` list and "
                           "its safety number is a spelling's number unless "
                           f"`why` argues otherwise: {idi['why']}")
    # The audit (TASK_020). Its `required` half never fails, never blocks,
    # never shouts -- `rep.ok` and plain prints, because that half is data. Its
    # `forbidden` half became a verdict at TASK_068; `idiom_audit`'s docstring
    # carries the accident test and the counter-argument.
    rungs = [(r, l, open(os.path.join(pdir, r)).read())
             for r, l in rung_sources(pdir)]
    extra = [(r, l, open(os.path.join(pdir, r)).read())
             for r, l in forbidden_only_sources(pdir)]
    au = idiom_audit(contract, rungs, extra)
    if au["spellings"] == 0:
        rep.ok("idiom spelling audit: this declaration backticks NO spelling, "
               "so the named-spelling standard's own trigger never fires here "
               "and there is nothing for the audit to report. Its rungs are "
               "matched by the entries' English alone (TASK_019, TASK_020).")
    else:
        rep.ok("idiom spelling audit follows. The `required` numbers are "
               "REPORTING ONLY -- they cannot fail the gate; a `forbidden` hit "
               "FAILS it (TASK_068). It exists so that TASK_019's '0 of 82' is "
               "reproducible from the committed tree rather than from a "
               "scratch file.")
        for ln in idiom_audit_lines(au):
            print(ln)
    forbidden_verdict(rep, au, nforb)
    return au


def forbidden_verdict(rep, au, nforb):
    """TASK_068. Fail, don't print.

    A `forbidden` entry's scope is universal by the key's own meaning, so this
    is decidable with no English involved, and the tree's own history says the
    defect happens by accident: p27 forbade a spelling both of its C rungs used,
    the `2` was printed for three tasks and two adversarial reviews, and nothing
    moved. `idiom_audit`'s docstring carries the whole argument;
    `.memory/02-bench-rules.md` carries the residual it retires.

    Split out of `check_idiom` so `_FORBIDDEN_VERDICT_CASES` can drive it with a
    stub report -- the check that TASK_053/TASK_056 declined and TASK_063
    recommended is worth a selftest of its own, not just of the counter it
    reads.

    ⚠ **The vacuity shout is PER ENTRY, not all-or-nothing** (TASK_069, from
    TASK_068_REVIEW M2). TASK_068 reached it only when `forbidden_spellings`
    was 0, i.e. when *every* entry lacked a backtick, so it named p01 and p05
    and missed p08 (3 of 4 entries unaudited), p16 (1 of 2) and p17 (2 of 3) --
    which took the `ok` branch and printed *"0 hit(s) over N forbidden
    spelling(s) ... Decidable and ENFORCED"* over a declaration most of which
    is audited zero times. **The list of 2 was a list of 5.**

    ⚠ **And the obvious repair does not work on every entry**, which is why
    this shouts rather than fails: p05's `forbidden[1]` is *"a running row
    pointer"*, a structural property with **no token to backtick at all**.
    Backticking p05's other entry would move it out of the loud all-vacuous
    state into a quiet partly-vacuous one -- the exact regression this split
    exists to prevent. An entry that cannot be backticked is legitimate; an
    entry that is silently unaudited is not."""
    if au["forbidden_hits"]:
        for h in au["hits"]:
            rep.fail("idiom-forbidden",
                     f"{h['rung']} spells `{h['spelling']}`, which this "
                     f"pattern's own idiom.{h['entry']} ({h['lang']}) forbids. "
                     f"Two routes out, and they are not equivalent: respell "
                     f"the rung (moves `source_sha256`), or fix the entry -- "
                     f"narrow its scope, make it per-language, or delete it -- "
                     f"which is a DECLARATION edit and owes the direction test "
                     f"(`.memory/01-ladder.md`). If the entry is what is wrong, "
                     f"say so in `why`; p27's said nothing about what the "
                     f"spelling was forbidden FOR, and that is how it survived.")
        rep.shout("idiom-forbidden",
                  f"{au['forbidden_hits']} forbidden hit(s) over "
                  f"{au['forbidden_spellings']} forbidden spelling(s). If one "
                  f"of these looks wrong, these are the shapes that are the "
                  f"HARNESS's fault or the ENTRY's, not the rung's, and none "
                  f"of them is ghost code any more (`exec_code` blanks comments,"
                  f" string literals, ghost clauses, `proof`/`assert`/`let "
                  f"ghost` statements, `spec fn`/`proof fn` bodies and items "
                  f"gated on a cfg no cell builds): (1) the hit is in "
                  f"`safe_naive_verus.rs`, a CONTROL cell rather than a rung of "
                  f"the ladder -- p01 ships one; (2) the spelling is a SUBSTRING "
                  f"of an honest longer one (`strlen(` in `slb_strlen(`, "
                  f"`position(` in `rposition(`, `q / 64` in `freq / 64` after "
                  f"whitespace deletion); (3) the entry backticks its own "
                  f"REPLACEMENT (`` `strcpy(` -- use `memcpy(` ``) and so "
                  f"forbids both. All were 0 on the whole tree at TASK_069.")
    elif au["forbidden_spellings"]:
        rep.ok(f"idiom forbidden: 0 hit(s) over {au['forbidden_spellings']} "
               f"forbidden spelling(s) x the rungs of the language(s) each "
               f"declares. Decidable and ENFORCED since TASK_068 -- a hit is a "
               f"gate failure, not a printed number.")
    # The p09 shape, and it is exactly the vacuous-truth defect
    # `.memory/02-bench-rules.md` calls this project's most repeated one: a
    # `forbidden` entry with no BACKTICKED span is audited zero times, so its
    # share of "0 hits" is earned by auditing nothing. Never silent, and
    # reached whether or not the pattern's OTHER entries are audited.
    for u in au.get("forbidden_unaudited") or []:
        rep.shout("idiom-forbidden",
                  f"idiom.{u['entry']} has NOT ONE backticked spelling, so the "
                  f"enforced audit never ranges over it and its share of the "
                  f"0 hits above is vacuous: {u['text'][:160]}. Backtick the "
                  f"spelling if it has one (p09 shipped 5 entries and 0 audited "
                  f"spellings; TASK_038_REVIEW) -- and if it has none, because "
                  f"the entry forbids a STRUCTURE rather than a token (p05's "
                  f"'a running row pointer'), say so in `why`: this line is "
                  f"then permanent and correct, and it is what stops the "
                  f"pattern's `ok` above from reading as enforcement it "
                  f"does not have.")
    if nforb and not au.get("forbidden_unaudited") and \
            not au["forbidden_spellings"]:
        # Defensive: entries exist, none is unaudited, and yet nothing was
        # audited -- unreachable while `forbidden_unaudited` is computed from
        # the same loop, and loud rather than silent if that ever changes.
        rep.shout("idiom-forbidden",
                  f"this pattern declares {nforb} forbidden entry/entries and "
                  f"the audit ranges over an EMPTY set, with no entry named as "
                  f"unaudited. That combination is a harness defect.")


class _StubReport:
    """Counts `fail`/`ok`/`shout` without printing. Selftest use only."""

    def __init__(self):
        self.n = {"fail": 0, "ok": 0, "shout": 0}

    def fail(self, section, msg):
        self.n["fail"] += 1

    def ok(self, msg):
        self.n["ok"] += 1

    def shout(self, section, msg):
        self.n["shout"] += 1


def _fv(req, forb=(), rungs=None):
    """(fails, oks, shouts) from `forbidden_verdict` on a synthetic pattern."""
    au = _aud(req, forb, rungs)
    r = _StubReport()
    forbidden_verdict(r, au, len(list(forb)))
    return [r.n["fail"], r.n["ok"], r.n["shout"]]


_IDIOM_CASES = [
    ("no idiom key at all", bool(idiom_problems({})), True),
    ("required + forbidden + why",
     idiom_problems({"idiom": {"required": ["i*ncol + j written out"],
                               "forbidden": ["chunks_exact"],
                               "why": "it deletes the flattened index"}}), []),
    # The p01/p08 shape: nothing excluded, and that must PASS -- see the
    # docstring on why a hard failure with no route out is the wrong shape.
    ("empty forbidden is legal",
     idiom_problems({"idiom": {"required": ["wrapping addition"],
                               "forbidden": [], "why": "no spelling of an "
                               "associative fold deletes this pattern"}}), []),
    ("empty required is not",
     len(idiom_problems({"idiom": {"required": [], "forbidden": ["x"],
                                   "why": "y"}})), 1),
    ("empty why is not",
     len(idiom_problems({"idiom": {"required": ["x"], "forbidden": [],
                                   "why": "   "}})), 1),
    # A mistyped key is silently empty, which is the accident this check exists
    # to make loud in the first place.
    ("`forbid` is not `forbidden`",
     len(idiom_problems({"idiom": {"required": ["x"], "forbid": ["y"],
                                   "why": "z"}})), 1),
    ("a bare string is not a declaration",
     bool(idiom_problems({"idiom": "do not use chunks_exact"})), True),
    ("an empty entry in a list is a typo, not a declaration",
     len(idiom_problems({"idiom": {"required": ["x", ""], "forbidden": [],
                                   "why": "z"}})), 1),
    # TASK_019: a per-language entry is legal, and a mistyped language key is
    # the same accident as `forbid`-for-`forbidden` -- silently pins nothing.
    ("a per-language entry is legal",
     idiom_problems({"idiom": {"required": [{"c": "len > src_len - 2",
                                             "rust": "len > src.len() - 2"}],
                               "forbidden": [], "why": "y"}}), []),
    ("one language key is legal (an entry may pin one side only)",
     idiom_problems({"idiom": {"required": [{"c": "memcpy"}],
                               "forbidden": [], "why": "y"}}), []),
    ("`rst` is not `rust`",
     len(idiom_problems({"idiom": {"required": [{"rst": "x"}],
                                   "forbidden": [], "why": "y"}})), 1),
    ("an empty per-language spelling is a typo",
     len(idiom_problems({"idiom": {"required": [{"c": "x", "rust": "  "}],
                                   "forbidden": [], "why": "y"}})), 1),
    ("a list of lists is not a declaration",
     len(idiom_problems({"idiom": {"required": [["x"]], "forbidden": [],
                                   "why": "y"}})), 1),
]

#: `spelling_matches` selftests. Each case is a shipped situation, named -- see
#: the docstring for which cell forced which part (TASK_019).
_MATCH_CASES = [
    ("whitespace is not a spelling",
     spelling_matches("2 + 2*nsuf > len", "    if 2 + 2 * nsuf > len {\n"), True),
    ("a different spelling is still a different spelling",
     spelling_matches("end - p >= 3", "    while p + 3 <= end {\n"), False),
    ("a C comment quoting the forbidden spelling is not the code using it",
     spelling_matches("src_off + 2 + len > src_len",
                      "/* written subtraction-first rather than\n"
                      " * `src_off + 2 + len > src_len` because ... */\n"
                      "if (len > src_len - (src_off + 2)) return 0;\n"), False),
    ("...and the subtraction-first spelling in the same file does match",
     spelling_matches("len > src_len - (src_off + 2)",
                      "/* rather than `src_off + 2 + len > src_len` */\n"
                      "if (len > src_len - (src_off + 2)) return 0;\n"), True),
    ("a Rust line comment is not code either",
     spelling_matches("start >= 0",
                      "// R1h has `&& start >= 0` here; this rung does not.\n"
                      "if start < end {\n"), False),
    ("a string literal is not code",
     spelling_matches("Range:", 'println!("Range: {}", n);\n'), False),
    ("a loop invariant is ghost, so a forbidden spelling there is not a use",
     spelling_matches("p + 3 + vlen <= end",
                      "while j < vlen\n    invariant\n        j <= vlen,\n"
                      "        p + 3 + vlen <= end,\n    decreases vlen - j,\n"
                      "{\n    j = j + 1;\n}\n"), False),
    ("...and the exec comparison in the same loop still matches",
     spelling_matches("vlen > end - (p + 3)",
                      "while end - p >= 3\n    invariant end <= buf@.len(),\n"
                      "    decreases end - p,\n{\n"
                      "    if vlen > end - (p + 3) { break; }\n}\n"), True),
    ("a function's requires/ensures is ghost too",
     spelling_matches("off + len <= v.len()",
                      "fn kernel(v: &[u64]) -> u64\n"
                      "    requires off + len <= v.len(),\n"
                      "{\n    0\n}\n"), False),
    ("the exec loop condition before an invariant survives",
     spelling_matches("end - p >= 3",
                      "while end - p >= 3\n    invariant end - p >= 0,\n"
                      "{\n    p = p + 1;\n}\n"), True),
    # ---- TASK_069, from TASK_068_REVIEW B1: the four ghost shapes the clause
    # blanker did not cover, each measured surviving into the audit on 20 of 20
    # shipped `verus.rs`, and each a HARD FAIL since TASK_068. The negative
    # cases below them are the over-blanking guard: this must not eat exec code.
    ("a `proof {}` block is ghost (p22 discharges its `decreases` this way)",
     spelling_matches("i + step <= cap",
                      "while i < cap {\n"
                      "    proof { assert(i + step <= cap); }\n"
                      "    i = i + step;\n}\n"), False),
    ("a `spec fn` body is ghost -- p09 respelled its SPECIFICATION to dodge this",
     spelling_matches("q / 64",
                      "spec fn word_of(q: nat) -> nat { q / 64 }\n"
                      "fn kernel(v: &[u64]) -> u64 { v[0] }\n"), False),
    ("a statement-level `assert(...)` is ghost",
     spelling_matches("p + 3 + vlen <= end",
                      "fn kernel() -> u64 {\n"
                      "    assert(p + 3 + vlen <= end);\n    0\n}\n"), False),
    ("a `let ghost` binding is ghost",
     spelling_matches("acc + v[i]",
                      "fn kernel() -> u64 {\n"
                      "    let ghost before = acc + v[i];\n    0\n}\n"), False),
    ("a `#[cfg(slb_twin)]` body is in no build (RECAP 'Owed' 10)",
     spelling_matches("get_unchecked",
                      "fn kernel(v: &[u64]) -> u64 { v[0] }\n"
                      "#[cfg(slb_twin)]\nfn twin(v: &[u64]) -> u64 {\n"
                      "    unsafe { *v.get_unchecked(0) }\n}\n"), False),
    ("a `#[cfg(test)]` module is in no build either",
     spelling_matches("chunks_exact",
                      "fn kernel(v: &[u8]) -> u64 { 0 }\n"
                      "#[cfg(test)]\nmod tests {\n    #[test]\n"
                      "    fn oracle() { DATA.chunks_exact(8).count(); }\n}\n"),
     False),
    # --- and the four things that must NOT be blanked ---
    ("`#[cfg(slb_isolated)]` IS built (build.py:150) and still matches",
     spelling_matches("v.get_unchecked",
                      "#[cfg(slb_isolated)]\nfn kernel(v: &[u64]) -> u64 {\n"
                      "    unsafe { *v.get_unchecked(0) }\n}\n"), True),
    ("Rust's `assert!` macro is exec code and still matches",
     spelling_matches("assert!(n > 0)",
                      "fn kernel(n: usize) -> u64 { assert!(n > 0); 0 }\n"),
     True),
    ("exec code after a `proof {}` block survives",
     spelling_matches("i = i + step",
                      "while i < cap {\n    proof { assert(i <= cap); }\n"
                      "    i = i + step;\n}\n"), True),
    ("a C `assert(` is exec code -- the ghost layers are Rust-only",
     spelling_matches("assert(len < cap)",
                      "uint64_t kernel(void) { assert(len < cap); return 0; }\n",
                      "c"), True),
]

#: `idiom_audit` selftests (TASK_020). Synthetic two-rung patterns, one per
#: shape the shipped declarations actually contain, so the reporting line's
#: three buckets are pinned in code and inside `source_sha256`.
_AUD_RUNGS = [("c/kernel.c", "c", "if (len > cap - 2) return 0;\n"),
              ("c/kernel_hardened.c", "c",
               "/* not `2 + len > cap` */\nif (len > cap - 2) return 0;\n"),
              ("safe_tuned.rs", "rust", "if len > cap - 2 { return 0; }\n"),
              ("verus.rs", "rust",
               "while i < n\n    invariant 2 + len > cap,\n{\n    i = i + 1;\n}\n"
               "if len > cap - 2 { return 0; }\n")]


#: The same pattern with its Rust rungs removed -- the shape no shipped pattern
#: has and every future one might (TASK_021's `no_rung` bucket).
_AUD_RUNGS_C = [r for r in _AUD_RUNGS if r[1] == "c"]


def _aud(req, forb=(), rungs=None):
    return idiom_audit({"idiom": {"required": list(req),
                                  "forbidden": list(forb), "why": "w"}},
                       _AUD_RUNGS if rungs is None else rungs)


_AUDIT_CASES = [
    # No backticks anywhere -> the standard's trigger never fires. This is p01
    # and p05 as shipped, and the line must say so rather than print "0 of 0".
    ("an entry with no backticks pins nothing and reports nothing",
     _aud(["the fit check is subtraction-first"])["spellings"], 0),
    # A plain-string entry is read once per language, against that language's
    # rungs only: 2 spellings, 2 C pairs + 2 Rust pairs.
    ("a spelling every rung has is present everywhere and prints no row",
     [_aud(["`len > cap - 2`"])[k]
      for k in ("spellings", "pairs", "present", "required_pins_nothing",
                "required_absent")], [2, 4, 4, 0, 0]),
    # p17's ellipsis: `if start < end && start >= 0 { ... }` matched no rung in
    # any language, and this is the bucket that would have printed it.
    ("a spelling no rung has PINS NOTHING, once per language",
     [_aud(["`if (len > cap) { ... }`"])[k]
      for k in ("required_pins_nothing", "required_absent")], [2, 0]),
    # p02/p16/p17's shape: the entry's English scopes it to some rungs.
    ("a spelling only one rung has is scoped-absent, not pins-nothing",
     [_aud([{"c": "`return 0;`", "rust": "`while i < n`"}])[k]
      for k in ("required_pins_nothing", "required_absent")], [0, 1]),
    # forbidden is decidable: universal by the key's own meaning.
    ("a forbidden spelling nobody uses is 0 hits",
     _aud(["`len > cap - 2`"], ["`2 + len > cap`"])["forbidden_hits"], 0),
    # ...and it is 0 only because of the matching rule. Both of the two rungs
    # that contain the token contain it as a comment / as a ghost invariant --
    # p02+p16's hardened C and p16's verus.rs, exactly.
    ("a forbidden spelling in exec code IS a hit",
     _aud(["`len > cap - 2`"], ["`len > cap - 2`"])["forbidden_hits"], 4),
    ("a per-language entry pins only its own language's rungs",
     _aud([{"c": "`return 0;`"}])["pairs"], 2),
    # TASK_021, the residual TASK_020 reported and did not close. On a pattern
    # that ships no Rust rung the `rust` key used to vanish: 1 spelling, 2
    # pairs, and NOTHING said the other half of the entry had been discarded.
    ("a per-language key naming an unshipped language is REPORTED, not dropped",
     [_aud([{"c": "`return 0;`", "rust": "`while i < n`"}],
           rungs=_AUD_RUNGS_C)[k]
      for k in ("spellings", "pairs", "no_rung_entries",
                "required_pins_nothing", "required_absent")], [1, 2, 1, 0, 0]),
    ("...and the dropped key's spellings travel with the report",
     _aud([{"c": "`return 0;`", "rust": "`while i < n`"}],
          rungs=_AUD_RUNGS_C)["no_rung"],
     [{"entry": "required[0]", "lang": "rust", "spellings": ["while i < n"]}]),
    # A dropped key with no backticks pins nothing either way, but the entry
    # still says something about a language that is not there -- report it.
    ("a dropped key with no backticked spelling is still reported",
     _aud([{"c": "`return 0;`", "rust": "no cleverness"}],
          rungs=_AUD_RUNGS_C)["no_rung_entries"], 1),
    ("forbidden entries get the same treatment",
     _aud(["`len > cap - 2`"], [{"rust": "`chunks_exact`"}],
          rungs=_AUD_RUNGS_C)["no_rung_entries"], 1),
    # ...and on a pattern that DOES ship both languages nothing is dropped, so
    # all six shipped records must print 0 here.
    ("both languages shipped -> nothing is dropped",
     _aud([{"c": "`return 0;`", "rust": "`while i < n`"}])["no_rung_entries"],
     0),
    ("a plain-string entry can never hit this bucket",
     _aud(["`len > cap - 2`"], rungs=_AUD_RUNGS_C)["no_rung_entries"], 0),
    # TASK_069: the per-entry vacuity counter `forbidden_verdict` shouts from.
    # Counted PER ENTRY, so a declaration that is half audited reports 1 rather
    # than 0 (TASK_068_REVIEW M2 -- p08 3 of 4, p16 1 of 2, p17 2 of 3).
    ("an unbackticked forbidden entry is counted even beside a backticked one",
     [_aud(["`len > cap - 2`"], ["`2 + len > cap`", "a running row pointer"])[k]
      for k in ("forbidden_spellings", "forbidden_unaudited_entries")], [2, 1]),
    ("a fully backticked forbidden list has nothing unaudited",
     _aud(["`len > cap - 2`"],
          ["`2 + len > cap`"])["forbidden_unaudited_entries"], 0),
    ("a per-language forbidden entry backticked on ONE side is audited",
     _aud(["`len > cap - 2`"],
          [{"c": "`2 + len > cap`", "rust": "no cleverness"}]
          )["forbidden_unaudited_entries"], 0),
]


#: `forbidden_verdict` selftests (TASK_068). The counter above was printed and
#: not acted on for three tasks; these pin that it is now a FAILURE, and that
#: the three no-hit shapes are told apart rather than all reading as a pass.
_FORBIDDEN_VERDICT_CASES = [
    # The p27 shape: an entry both C rungs spell. 4 hits -> 4 fails + 1 shout.
    # This is the case TASK_053 proposed, TASK_056 declined and TASK_063
    # recommended; before TASK_068 it produced 0 fails.
    ("a forbidden spelling in exec code FAILS, once per hit",
     _fv(["`len > cap - 2`"], ["`len > cap - 2`"]), [4, 0, 1]),
    # ...and the blanking half is what keeps it at 0 on the shipped tree: the
    # hardened C rung's comment and verus.rs's ghost invariant both spell the
    # token and neither is a hit.
    ("a forbidden spelling only in a comment / ghost clause is NOT a hit",
     _fv(["`len > cap - 2`"], ["`2 + len > cap`"]), [0, 1, 0]),
    # A pattern that forbids nothing must not get a count-bearing `ok` over an
    # empty set. ⚠ NO SHIPPED PATTERN HAS `nforb == 0`: p01 declares 1 entry and
    # p08 declares 4, and TASK_068 cited both here as if they were this case
    # (TASK_068_REVIEW m3). `idiom_problems` permits it -- `MAX_TWIN_JUSTIFICATIONS`
    # is why -- so the shape is legal and untested on the tree, which is exactly
    # what a selftest is for.
    ("forbidding nothing is legal and earns no ok",
     _fv(["`len > cap - 2`"]), [0, 0, 0]),
    # The p09 shape: entries with no backticked span are audited zero times, so
    # "0 hits" would be vacuous. Shout, never ok.
    ("a forbidden entry with no backticks SHOUTS instead of passing",
     _fv(["`len > cap - 2`"], ["chunks_exact, spelled out in English"]),
     [0, 0, 1]),
    # TASK_069, TASK_068_REVIEW M2: the branch NO selftest constrained, and the
    # one 3 of the 5 affected patterns are in. One entry audited, one not: the
    # `ok` is earned for the first and the second must still shout. Before this
    # the whole pattern took `ok` and printed "Decidable and ENFORCED".
    ("a PARTLY unaudited declaration shouts for the unaudited entry AND oks",
     _fv(["`len > cap - 2`"], ["`2 + len > cap`", "a running row pointer"]),
     [0, 1, 1]),
    # ...and the shout is per entry, so two unbackticked entries shout twice.
    ("two unaudited entries shout twice, not once",
     _fv(["`len > cap - 2`"], ["a running row pointer", "a strength-reduced "
                               "induction variable"]), [0, 0, 2]),
]


# ==========================================================================
# 1. build
# ==========================================================================

def check_build(pdir, rep, cells, opts, modes):
    head("1. build the matrix")
    built = {}
    for c in cells:
        for o in opts:
            for m in modes:
                ok, out, log = buildmod.build_cell(pdir, c, o, m, quiet=True)
                built[(c, o, m)] = out if ok else None
                if not ok:
                    rep.fail("build", f"{c} {o} {m}\n{log}")
    n_ok = sum(1 for v in built.values() if v)
    print(f"    {n_ok}/{len(built)} cells built")
    return built


# ==========================================================================
# 2. checksums against the pattern's own model
# ==========================================================================

def build_models(modmod, indir, names, rep):
    models = {}
    for name in names:
        m = sb(modmod.build, os.path.join(indir, name))
        missing = [a for a in REQUIRED_MODEL_ATTRS if not hasattr(m, a)]
        if missing:
            rep.fail("model", f"{name}: model.py's Model lacks {missing}")
            continue
        for p in sb(m.selfcheck):
            rep.fail("model", f"{name}: {p}")
        se = sbg(m, "sanitizer_expect")
        if se not in ("clean", "fires"):
            rep.fail("model", f"{name}: sanitizer_expect is {se!r}, want "
                              f"'clean' or 'fires'")
        # TASK_068. `expected_hang` is OPTIONAL and defaults False, so no
        # existing model.py moves. It is the termination analogue of
        # `sanitizer_expect: "fires"`: the input on which a rung that omits this
        # pattern's guard does not terminate. See `run_budgets` for why the
        # prediction is derived here and the seconds are pinned in the contract.
        eh = sbg_opt(m, "expected_hang", False)
        if not isinstance(eh, bool):
            rep.fail("model", f"{name}: expected_hang is {eh!r}, want a bool")
        elif eh and se == "fires":
            # TASK_069, TASK_068_REVIEW M4. The two were validated
            # independently and never against each other, so one input could
            # carry both -- and the hang arm of `check_sanitizers` runs first,
            # which discharged the "fires" obligation silently. Refused here as
            # well as there, because a declaration that cannot be honoured
            # should fail where it is written and not four stages later.
            rep.fail("model",
                     f"{name}: model.py declares BOTH expected_hang and "
                     f"sanitizer_expect='fires'. A sanitizer that fires aborts "
                     f"the process, so this input cannot both trip the bug and "
                     f"run forever in the same C cell; whichever is true, the "
                     f"other is unobservable and would be skipped rather than "
                     f"checked.")
        elif eh and not name.startswith("adversarial"):
            rep.fail("model",
                     f"{name}: expected_hang is True on a NON-adversarial "
                     f"input. Stage 2's checksum agreement is the gate's only "
                     f"load-bearing correctness check and every matrix input "
                     f"must reach it; an input that declares it does not "
                     f"terminate is declaring its way out of it.")
        models[name] = m
    return models


def stem_of(name):
    """`adversarial-full.bin` -> `adversarial-full`. The contract's
    `run.timeout_s` is keyed by stem and the models by file name, and this
    expression was written out three times (TASK_068_REVIEW m6)."""
    return name[:-4] if name.endswith(".bin") else name


def check_hang_declarations(rep, all_models, budgets):
    """The two halves of a declared hang must agree (TASK_068).

    `model.expected_hang` predicts; `contract.run.timeout_s` budgets. Neither is
    allowed without the other, which is what makes *declaring a hang move
    `contract_sha256`* -- the deciding question the design was handed -- true
    mechanically rather than by convention. It also stops the two silent
    failure modes: a prediction with no budget still costs `RUN_TIMEOUT` per
    cell (the whole cost this exists to avoid, and it would be invisible), and a
    budget with no prediction is a shortened timeout on an input nobody said
    hangs, which is how a slow honest cell gets recorded as a hang.

    ⚠ **Retrofitting a hang declaration onto an EXISTING pattern costs a
    re-measure**, and a pattern author should know that before starting:
    `expected_hang` lives in `model.py`, `model.py` is in
    `measure.py::measurement_sources`, so adding it clears that pattern's
    `source_sha256` and `measure.py --check-stale` reports STALE. Re-measuring
    re-takes the WALL-CLOCK block, and this box's timing floor is a session
    property -- a same-day p08 re-measure read ~18% lower on every `large` cell
    including cells that had not changed by a byte, and a p10 one ~8% -- so the
    pattern's published timing rows move with it. Free for a pattern that has
    not been measured yet; a scheduled unit for anything else
    (`.memory/03-measurement.md`, TASK_068_REVIEW m6)."""
    declared = sorted(n for n, m in all_models.items()
                      if sbg_opt(m, "expected_hang", False))
    stems = {stem_of(n) for n in declared}
    for s in sorted(stems - set(budgets)):
        rep.fail("run-budget",
                 f"model.py declares {s}.bin non-terminating (expected_hang) "
                 f"and the contract gives it no `run.timeout_s` budget, so "
                 f"every cell would still be waited on for {RUN_TIMEOUT}s.")
    for s in sorted(set(budgets) - stems):
        rep.fail("run-budget",
                 f"contract `run.timeout_s` shortens {s}.bin to {budgets[s]}s "
                 f"but model.py does not declare it non-terminating "
                 f"(expected_hang). A shortened budget on a terminating input "
                 f"records a slow cell as a hang.")
    if declared and stems == set(budgets):
        # Only when the two halves AGREE -- otherwise the `ok` would be printed
        # beside its own failure, and the count it quantifies over would include
        # an input with no budget at all.
        rep.ok(f"{len(declared)} input(s) declared non-terminating "
               f"({declared}), each with a contract budget "
               f"({ {s: budgets[s] for s in sorted(stems)} } s) -- so the "
               f"declaration is inside `contract_sha256`.")
    return declared


def check_checksums(built, rep, models, indir):
    head("2. checksum agreement across every cell (vs the pattern's model.py)")
    if not models:
        rep.fail("coverage", "no non-adversarial input left to check a checksum "
                             "against -- `--skip` removed them all, so this run "
                             "certifies nothing")
        return {}
    for name, mod in models.items():
        print(f"    {name}: {sb(mod.describe)}")
    results = {}
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        for name, mod in models.items():
            rc, out, err = run_bin(path, os.path.join(indir, name))
            results[(c, o, m, name)] = (rc, out.strip(), err.strip())
            if rc != 0:
                rep.fail("run", f"{c} {o} {m} on {name}: exit {rc} "
                                f"stderr={err.strip()[:200]}")
            elif out.strip() != str(sbg(mod, "checksum")):
                rep.fail("checksum", f"{c} {o} {m} on {name}: got {out.strip()}, "
                                     f"model says {sbg(mod, 'checksum')}")
    for name in models:
        vals = {v[1] for k, v in results.items() if k[3] == name and v[0] == 0}
        if len(vals) == 1:
            # Count the cells whose value is actually IN `vals`. The old count
            # was every row for this input, including cells that exited non-zero
            # and were therefore excluded from the agreement set -- so "all N
            # cells agree" over-reported N on exactly the runs where a cell had
            # crashed (TASK_053 m1; red-run only, which is why it is a minor).
            agreed = sum(1 for k, v in results.items()
                         if k[3] == name and v[0] == 0)
            total = sum(1 for k in results if k[3] == name)
            rep.ok(f"{name}: all {agreed} of {total} cells that exited 0 agree "
                   f"-> {vals.pop()}")
        elif vals:
            rep.fail("checksum", f"{name}: cells disagree: {sorted(vals)}")
    return results


# ==========================================================================
# 3. anti-collapse -- structural AND dynamic
# ==========================================================================

def check_no_collapse(built, rep):
    head("3a. anti-collapse, structural: the kernel loop survived optimisation")
    rows, digests, bad = [], {}, 0
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        # In `isolated` builds the kernel is its own symbol. In `whole` builds it
        # is inlined on purpose, so the loop has to be found in main instead.
        needle = "kernel" if m == "isolated" else "main"
        k = asm.try_kernel(path, needle)
        if k is None:
            bad += 1
            rep.fail("collapse", f"{c} {o} {m}: no symbol containing {needle!r}")
            continue
        floor = 8 if m == "isolated" else 20
        loads = [i for i in k.insns if re.search(r"\(%r[a-z0-9]+", i.text)]
        bulk = k.bulk_calls
        problems = []
        # A backward branch **or** a call to a bulk-memory routine. p02's kernel
        # is a `memcpy`, and gcc -O3 compiles it to 11 instructions with no
        # backward branch at all: the loop is real, it is just in libc. Requiring
        # a backward branch here false-failed a healthy kernel (TASK_003_REVIEW,
        # measured before p02 existed). The dynamic check in 3b is what actually
        # establishes the work happened, and it is unaffected either way.
        if not k.has_loop and not bulk:
            problems.append("no backward branch and no bulk-memory call")
        if k.n_fn_nopad < floor:
            problems.append(f"body {k.n_fn_nopad} < floor {floor}")
        if not loads and not bulk:
            problems.append("no memory operand anywhere")
        rows.append((c, o, m, k.n_fn, k.n_fn_nopad, k.pad_insns,
                     len(k.backward_branches),
                     ",".join(sorted({n for _, n in bulk})) or "-",
                     k.md5_fn[:8], k.md5_raw[:8]))
        digests[(c, o, m)] = k
        if problems:
            bad += 1
            rep.fail("collapse", f"{c} {o} {m}: " + ", ".join(problems))
    print(f"    {'cell':18s} {'opt':4s} {'mode':9s} {'n_fn':>5s} {'nopad':>6s} "
          f"{'pad':>4s} {'loops':>6s} {'bulk':14s} {'md5_fn':8s} md5_raw")
    for c, o, m, nfn, nopad, pad, nloop, bulk, md5fn, md5raw in rows:
        print(f"    {c:18s} {o:4s} {m:9s} {nfn:5d} {nopad:6d} {pad:4d} {nloop:6d}"
              f" {bulk:14s} {md5fn}  {md5raw}")
    if rows and not bad:
        rep.ok(f"{len(rows)} cells: a real loop (backward branch or bulk-memory "
               f"call), a real memory operand, body above floor. Counts/digests "
               f"are the `nm --print-size` extent; `pad` is what objdump's "
               f"grouping adds on top.")
    return digests


def _probe_input(src, n_iters, out):
    """The same input file with `n_iters` rewritten.

    `n_iters` is at offset 0 of *every* pattern's input file
    (`.memory/02-bench-rules.md`), so this is a format-level operation and needs
    no help from the pattern."""
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


# The environment variables that can change a libc code path PER CALL without
# changing the block's length. Derived from a measurement, not from a list:
# `.temp/t107/d1_env.py content` holds the block length EXACTLY equal at 3332 B
# and moves p03's marginal by 486 Ir/call with `GLIBC_TUNABLES`. `LD_*` is here
# because `LD_PRELOAD` can replace `memcpy` outright and `LD_BIND_NOW` changes
# the PLT; `MALLOC_*` because it re-tunes the allocator the kernels call.
_ENV_TUNING_PREFIXES = ("GLIBC_TUNABLES", "LD_", "MALLOC_")


def _env_block():
    """The environment block the MEASURED CHILDREN are handed, measured in a
    real child rather than computed from a Python dict.

    Returns `{"bytes", "nvars", "envp_stack_bytes", "tuning_vars",
    "repo_path_bytes", "domain"}`, or `None` if the probe child could not be
    run.

    ⚠⚠ **THREE WAYS TO GET THIS WRONG, AND THE PROJECT HAS ALREADY MADE TWO OF
    THEM.**

    1. **`len(os.environ)`-style arithmetic is wrong** -- that is control entry
       7 in `.memory/03-measurement.md` (`TASK_099`'s `a3_launcher.py`
       "measured the block length from `os.environ` (a Python dict)"). A
       variable does not cost its value: it costs an envp pointer slot, its
       name, an `=`, its value and a NUL, and the 87-vs-64 decomposition that
       corrected TASK_099 turns on exactly those four forgotten terms.
    2. **Reading `check.py`'s OWN `/proc/self/environ` is wrong** for a subtler
       reason: that block is frozen at *this* process's `execve`, while what a
       child receives is `environ` as libc holds it now. They agree only while
       nothing mutates `os.environ` -- true today (`check.py` mutates none;
       `build.py` only reads three `SLB_*` overrides) and not a property anyone
       should have to re-verify. So the child reads its own.
    3. **This is NOT the forbidden pin.** It does not force an environment; it
       records which draw was taken, so a disagreement becomes diagnosable
       (`.memory/03-measurement.md`, the reproduction protocol decided at
       TASK_103). Pinning would make the number reproducible-and-wrong.

    ⚠ **WHAT THE INTEGER IS NOT: it is not the client's block under valgrind.**
    `_callgrind_total` runs the binary under `valgrind`, which appends its own
    `vgpreload` entries to `LD_PRELOAD` and synthesises the client's stack
    itself, so the client's block is this number plus a deterministic function
    of it. That is fine for the job: the pin's rule is *"same recorded length =>
    the marginal must match EXACTLY"*, and a deterministic offset preserves it.
    Verified on the axis that matters (`.temp/t107/d1_env.py length`): four pads
    give child blocks 3290 / 3298 / 3306 / 3314 B and marginals
    3066 / 3059 / 3059 / 3066 -- the documented +-7, bistable, period 32, window
    16 wide, and the recorded integer separates the two states.

    ⚠⚠ **AND ONE INTEGER IS NOT ENOUGH, WHICH IS WHY `tuning_vars` IS HERE.**
    `TASK_103` settled launcher-vs-environment and explicitly did **not**
    separate LENGTH from CONTENT; `TASK_107` measured it and the length alone is
    a **lossy** pin. Two environments of *byte-identical block length* (3332 B,
    both read from a real child):

        GLIBC_TUNABLES=glibc.cpu.x86_rep_stosb_threshold=64   marginal 3545.00
        SLB_T107_FILLER=<35 z>                                marginal 3059.00

    **+486.00 Ir/call at the same length -- 69x the +-7 this pin exists to
    diagnose.** p03 `memset`s a stack array per call and the tunable picks a
    different `memset` path, so the change lands in the per-call term the
    marginal measures rather than in the start-up constant that cancels. A
    length-only record would have read "same length, so the marginal must
    match", and it does not. `tuning_vars` is the smallest thing that makes that
    case diagnosable instead of silent.

    ⚠⚠ **AND `bytes` WAS ITSELF LOSSY BY EXACTLY THE TERM THIS PROJECT HAD
    ALREADY WRITTEN DOWN AS FORGOTTEN -- `TASK_114` B1, fixed here at
    `TASK_119`.** The rule the field licensed was *same `bytes` and same
    `tuning_vars` => the marginal must match EXACTLY*, and it is **false**:

        1 filler var(s)   bytes=3520  nvars=49  marginal=3059.00
        2 filler var(s)   bytes=3520  nvars=50  marginal=3059.00
        3 filler var(s)   bytes=3520  nvars=51  marginal=3066.00
        4 filler var(s)   bytes=3520  nvars=52  marginal=3066.00
            byte-identical `bytes`, identical (empty) `tuning_vars`

    A nine-rung sweep at a constant `bytes = 3680` is **period 4 in the
    variable count**, which is the +-7's 32-byte period divided by the **8
    bytes of one envp POINTER SLOT**. `/proc/self/environ` is `NAME=VALUE\\0`
    concatenated and **contains no pointer array at all**, so `bytes` captures
    four of the five terms in this file's own 87-byte decomposition
    (`.memory/03-measurement.md`) and drops the one it calls *"the part the
    manager forgot entirely"*. **The pin repeated the arithmetic error it was
    written to prevent.**

    So the child now returns the **count** as well, read from the same blob in
    the same child, and `envp_stack_bytes = bytes + 8*nvars` is the single
    integer the comparison rule uses. ⚠ **`envp_stack_bytes` is the envp
    contribution ONLY** -- `argv`, `auxv` and the `AT_EXECFN` path string sit
    on the same initial stack and are **not** in it, which is what
    `repo_path_bytes` and the `domain` string below exist to say.

    ⚠⚠ **DOMAIN, AND IT IS RECORDED RATHER THAN LEFT IN PROSE BECAUSE THAT IS
    THE DEFECT `TASK_114` §A.3 FOUND.** `TASK_107` established the pin as
    *"valid within one clone location"* and that sentence existed **only in a
    task report** -- zero hits in this file, in `.memory/` and in the record
    itself. Measured, environment held byte-identical and only `argv[1]`'s
    length varied:

        argv[1] len=57 -> 3066.00   len=58 -> 3066.00
        argv[1] len=59 -> 3059.00        <- +2 characters, -7.00 Ir/call

    `repo_path_bytes` is `len(REPO)`, the term every measured child's `argv`
    and `AT_EXECFN` carry, so *"same clone location"* becomes checkable from
    the record instead of assumed.

    ⚠⚠ **AND THE RULE IS STATED AS NECESSARY, NOT SUFFICIENT, ON PURPOSE.**
    `bytes` also explained a measured period, was believed sufficient, and was
    not. Three equal fields mean *"this record cannot tell the two draws
    apart"*, which is what licenses a comparison; they do **not** prove the two
    draws are the same. **Sufficiency is OPEN.** ✅ What is measured
    (`.temp/t119/a1_nvars_pin.py`, arm `split`): at fixed `bytes` **and** fixed
    `nvars`, redistributing the same byte budget over the same number of
    variables does **not** move the marginal -- so the count is not merely one
    more thing that happens to vary."""
    try:
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys;b=open('/proc/self/environ','rb').read();"
             "sys.stdout.write('%d %d' % (len(b), b.count(b'\\x00')))"],
            capture_output=True, text=True, timeout=60)
        n, nvars = (int(x) for x in r.stdout.split())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return {"bytes": n,
            # ⚠ the term `bytes` drops: one envp POINTER SLOT per variable.
            "nvars": nvars,
            "envp_stack_bytes": n + 8 * nvars,
            "tuning_vars": {k: v for k, v in sorted(os.environ.items())
                            if k.startswith(_ENV_TUNING_PREFIXES)},
            # the clone-location term, so the domain below is checkable.
            "repo_path_bytes": len(REPO),
            "domain": (
                "Comparable ONLY against a record with the same "
                "`envp_stack_bytes` (= bytes + 8*nvars), the same "
                "`tuning_vars` and the same `repo_path_bytes`. That is a "
                "NECESSARY condition, not a proved sufficient one: `bytes` "
                "alone was believed sufficient and TASK_114 falsified it at "
                "+-7 Ir/call. argv beyond the repo prefix, and anything else "
                "on the initial stack, are not recorded here. When the three "
                "differ, compare `kernel_exclusive_ir` in results/pNN-*.json "
                "instead -- structurally immune, 0 of 288 triples moved.")}


def _callgrind_total(binary, arg, outfile):
    """Whole-program Ir for one run. Only ever used as one half of a
    *difference*: `.memory/03-measurement.md` shows the absolute value moves
    with the size of the environment block, and the CONSTANT part of that
    cancels when the same binary is run twice in the same shell.

    ⚠ **The PER-CALL part does not cancel, and this docstring used to say
    "every one of those terms cancels"** (TASK_077_REVIEW m8). Whatever the
    environment block does to the initial stack pointer, it does the same way in
    both runs of a difference -- so a *constant* start-up cost is removed. But a
    kernel that `memset`s a stack array pays an alignment-dependent cost **per
    call**, and that term scales with the call count and therefore survives the
    subtraction. Measured across **four** patterns at **7 Ir/call** (p03, p04,
    p38, and p46 at TASK_092, which `memset`s TWO stack arrays per call and so
    moves by `-14 = 2 x 7`); see `check_marginal_ir`'s docstring for the size,
    the bistability and the rule."""
    try:
        r = subprocess.run([VALGRIND, "--tool=callgrind",
                            f"--callgrind-out-file={outfile}", binary, arg],
                           capture_output=True, text=True, timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        # TASK_069, TASK_068_REVIEW m5. `run.timeout_s` does not reach here, so
        # a probe input that does not terminate would take `RUN_TIMEOUT` and
        # then kill the gate with an uncaught traceback instead of failing the
        # stage. `check_marginal_ir` refuses such an input up front now; this is
        # the backstop for a cell that is merely slower than 900 s.
        return None
    if r.returncode != 0:
        return None
    for line in open(outfile):
        if line.startswith("summary:") or line.startswith("totals:"):
            return int(line.split()[1])
    return None


def check_marginal_ir(pdir, built, rep, modmod, contract, indir, enabled):
    """The dynamic half of anti-collapse: does the loop still do work per call?

    A kernel that got constant-folded, hoisted or CSE'd away still has a
    backward branch somewhere in its symbol, so the structural check above
    cannot see it. Executed instructions per kernel call can. Measured as a
    slope -- Ir at N calls minus Ir at N/2 calls, over the difference in calls --
    which is symbol-independent (so it works in `whole` mode, and at O0 where a
    rung's work lives in `core::iter` symbols rather than in `kernel`).

    **The loader and environment terms cancel to about 0.2 Ir/call, not
    exactly** -- corrected at TASK_018 from TASK_017's own p08 measurement
    (`patterns/p08-overlap-move/NOTES.md` 2b, `.memory/03-measurement.md`), and
    requoted at TASK_020, where the interval this paragraph used to give
    (`7292.14 … 7292.30`) was believed to have no reproduced endpoint. **It has
    two, and the 0.2 headline is right** -- but for a reason the interval alone
    does not say, so state the reason:

      * **within one build**, changing only the length of the environment block
        moves p08's `unsafe/O3/whole/small.bin` marginal by about **0.10**, and
        three probes agree: 21 pad lengths 0…900 at TASK_020 give
        7292.12 … 7292.22, six lengths at TASK_019 give 7292.12 … 7292.22, five
        at TASK_018_REVIEW give 7292.10 … 7292.22. Non-periodic and non-monotone
        in the pad length -- it is SCATTER, not a trend.
      * **across builds the level itself moves**, and that is the larger half.
        TASK_017 and TASK_017_REVIEW probed a *different* build of the same
        source and got 7292.14 … 7292.30 (five points, recorded at
        `patterns/p08-overlap-move/NOTES.md` 2b) -- an interval that does not
        even overlap the current build's maximum. This is the p02 mechanism
        (NOTES 10b): two binaries of different size land their buffers at
        different alignments, so glibc's `memmove` takes a different path while
        the kernel's own self-cost is identical.

    Union over all five probes: **7292.10 … 7292.30**, spread **0.20**, of which
    ~0.10 is the environment and the rest is the build. 100% of the drift is
    inside one glibc `memmove` whose alignment-dependent tail changes by ~0.04
    Ir/iteration.

    ⚠ **EVERY NUMBER IN THE THREE PARAGRAPHS ABOVE IS p08's, AND p08 IS THE
    SMALL CASE. Read the next paragraph before quoting `±0.20` at another
    pattern** (TASK_077_REVIEW m8). This docstring used to close *"it is bounded
    and small, and it threatens no published number"*, on the strength of p08's
    `R1h - R1 = 0.00` in 12 configurations. There are patterns at **±7 Ir/call**,
    35x that bound.

    ⚠⚠ **THE EXPOSED SET IS A MEASUREMENT, SO IT IS QUOTED AS ONE -- WITH ITS
    INSTRUMENT, ITS DATE AND ITS DENOMINATOR.** Every earlier version of this
    paragraph asserted a pattern list instead, and every one of them was wrong:
    *three* until TASK_096, *four* until TASK_099, and **`-O3 isolated` is
    invariant** until TASK_097 refuted it with a one-variable experiment. The
    honest form is the census, and re-taking it costs ~90 minutes:

    ⚠⚠⚠ **THE CENSUS BELOW IS DATED `2026-08-22` AND ITS DENOMINATOR IS 24
    PATTERNS. THE TREE HAS 33.** It has NOT been re-taken, and the ~90 minutes
    it costs bought nothing TASK_164 needed. **Read every figure in it as a
    statement about 24 of 33 rows, made on 2026-08-22.**

    ⚠ **The nine it does not cover are DERIVED, not remembered** -- the census
    artefact is still on this box and names its own subjects
    (`.temp/r98/treescan_large.json`, 24 keys of the form `pNN/large.bin`).
    TASK_164 read it rather than reconstructing the list from landing dates,
    **because the first attempt at this sentence guessed and got two of the
    nine wrong** (it named `p27` and `p47`, which ARE in the census, and missed
    `p23` and `p42`):

        in the census (24)  p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12
                            p13 p14 p16 p17 p18 p19 p22 p27 p36 p38 p46 p47
        NOT in it     (9)   p23 p25 p28 p29 p32 p34 p35 p42 p49

    **It is not evidence about those nine in either direction.** ⚠ And the gap
    is not a random nine: **seven of them are the temporal, type and aliasing
    rows** (`harness/tools/composition.py --check`: temporal p25 p28 p29 p32
    p34, type p35, aliasing p49), which is the half of the tree the SECOND
    mechanism below has its largest nulls on. p23 and p42 are the other two.

        2026-08-22, `.temp/r98/treescan.py` (TASK_098, reviewed), 24 patterns
        x 6 cells x 2 blobs at `-O3 isolated`, pad 0 against pad 16:

              288 (pattern, input, cell) triples
              marginal_ir_per_call        moved in  14
              kernel_exclusive_ir         moved in   0   <- structurally immune
              exposed (pattern, cell) pairs:   7 of 144
                p03 {safe_tuned, unsafe, verus}
                p04 {safe_tuned, unsafe, verus}
                p46 {c-clang}      <- NOT a Rust rung, NOT the memset story

      * ⚠ **SO "TWO PATTERNS, 7 OF 144 CELLS" IS ARITHMETICALLY IMPOSSIBLE and
        it is in `.memory/03-measurement.md`'s RESOLVED block, in
        `TASK_098_REPORT.md` MAJOR 3 and in `TASK_099.md` §C.** The seventh cell
        is p46's `c-clang`, so the count is **three patterns**; what is true --
        and is what those sentences were reaching for -- is that **p38 and p46's
        RUST rungs swing `0.00` over 32 pads**, which is what kills the
        four-pattern list.
      * ⚠ **`-O3 isolated` IS NOT INVARIANT.** The line here used to read
        *"invariant (0.00 across every probe to date)"* and the closing
        paragraph called it *"the only cell class no probe has moved"*.
        TASK_097 refuted both and `.memory/03-measurement.md` records the fix
        as **owed and not done**; this is it. What the evidence supports:

              -O3 isolated  p03/p04's Rust rungs move by 7 per rung, 14 per
                            pair; 137 of 144 cells do not move
              -O3 whole     moves by 7 per per-call stack `memset`  (p03, p04,
                            p38, p46 -- measured at TASK_077/TASK_092, and NOT
                            re-measured since, so it is the older claim)
              -O0           moves in BOTH modes
              kernel_exclusive_ir   immune in every mode probed (0 of 288)

        p46 `memset`s **two** stack arrays per call, so its `unsafe`/`verus`
        `O3 whole` cells move by `-14 = 2 x 7`: **a pattern's step is
        `7 x (per-call stack arrays)`, not a flat 7.**
      * **It is BISTABLE with a PERIOD OF 32 BYTES and a WINDOW EXACTLY 16 WIDE,
        and the phase differs per binary.** ⚠ This bullet said the
        discriminator was the **presence** of an environment variable *"not its
        size"* (TASK_077_REVIEW A2 #32). **False at `-O3 isolated`**: over a
        full period (`.temp/r98/{p03,p04}_sweep.json`, 32 pads, and reproduced
        independently at TASK_099 in a different session at pads 0/8/16/24),

              p03 unsafe      3066 for pads  6..21, else 3059
              p03 verus       3058 for pads  8..23, else 3065
              p03 safe_tuned  3425 for pads 14..29, else 3418

        so pad 1 and pad 7 disagree on the same binary. Two consequences worth
        having: **the pair swing is 14, not 7**, because `unsafe` and `verus`
        have different phases and can sit in opposite states (that is TASK_097's
        `+6.00 -> -8.00` sign flip); and **a 16-apart two-pad screen is a
        COMPLETE detector, not a lower bound**, because a 16-wide window in a
        32-period puts `p` and `p+16` in opposite states always -- which is why
        the census above only needed two pads. ⚠ That completeness argument
        rests on the 16-wide window, verified on p03's and p04's six Rust cells
        only.
      * **The mechanism is a stack array, not a heap one.** p03, p04, p38 and
        p46 all `memset` a stack scratch buffer per call; the environment block
        shifts the initial stack pointer, which shifts that array's alignment,
        which picks a different tail in `__memset_avx2_unaligned_erms` --
        `patterns/p03-bounded-stack/NOTES.md` 3b names the same 7 Ir, and
        TASK_098 attributed **100% of the swing** to that one libc symbol by
        per-symbol differencing. p08's work is a heap `memmove`, which is why
        p08 moves in hundredths.

    ⚠⚠⚠ **EVERYTHING ABOVE IS ONE MECHANISM AND THERE ARE TWO. THE SECOND IS
    LARGER, IT IS NOT DRIFT, AND UNTIL TASK_164 THIS DOCSTRING DID NOT NAME
    IT.** The two are routinely conflated -- *"leads with ±0.20 and warns of ±7
    against a measured 269.52"* is a sentence somebody wrote about this
    docstring, and it puts three numbers from two different quantities in one
    interval. They are not comparable:

        | | mechanism | magnitude | what varies |
        |---|---|---|---|
        | above | the environment block shifts the stack pointer -> a per-call
          stack array's alignment -> a different tail in
          `__memset_avx2_unaligned_erms` | ±0.20 (p08); ±7 per stack array
          (p03/p04/p38/p46) | **two runs of the SAME build** |
        | below | `marginal_ir_per_call` is a **WHOLE-PROGRAM SLOPE**, so it
          charges everything the kernel calls -- glibc malloc internals above
          all | up to **269.52** at `-O3 isolated` | **R4 against R5 INSIDE ONE
          RUN**, on a pair `identity` pins to `exact` |

    **So the R4/R5 pair has a NON-ZERO NULL CONTROL.** `identity` forces R4's
    and R5's kernels to agree byte for byte, so their marginal difference is a
    measured null -- and it is not zero, because the slope is deliberately
    symbol-independent and therefore includes the callees.
    `.memory/03-measurement.md` entry 23 is the authority; the table below is
    **re-derived from `results/gate/p*.json` at TASK_164**
    (`.temp/t164/r45_null.py`), not copied from it.

    ⚠⚠⚠ **A NULL IS A PROPERTY OF A CELL. DO NOT MAX IT OVER MODE, OVER LEVEL,
    OR OVER INPUT.** Entry 23 records that this table was published wrong TWICE,
    both times by maxing across a dimension that mattered -- `p28 1732.73` and
    `p29 425.80` are **`-O0`** cells and were printed under an `-O3` heading.
    ⚠ **And they are `large.bin` cells: on `small.bin` p25's and p42's nulls are
    `0.00` in every mode and level.** So the axis is `(level, mode, INPUT)`:

        verus - unsafe, `marginal_ir_per_call`, per (level, mode, input) cell
                    O0/iso            O3/iso           O0/whole          O3/whole
                 small    large    small    large    small    large    small    large
        p25       0.00  +269.52    0.00  +269.52    0.00  +269.52    0.00  +269.52
        p28    +281.28 +1732.73    0.00    +1.01 +281.28 +1732.73  +46.02  +211.87
        p29    +113.76  +425.80    0.00    -0.02 +113.76  +425.80 +101.77  +465.55
        p42       0.00   -31.00    0.00   -31.00    0.00   -31.00   -2.00   -33.00
        p11       0.00     0.00   -1.00    -1.00    0.00     0.00 -494.00  -166.00

        at -O3 ISOLATED -- the column corrections are published in -- the
        WHOLE tree, 66 (pattern, input) cells over 33 patterns:
            |null| >= 2.00 in  8: p25 large +269.52 . p42 large -31.00 .
                                  p03 +6.00 (both) . p04 +6.00 (both) .
                                  p02 -2.00 (both)
            1.00 <= |null| < 2  35   (34 of them exactly -1.00; p28 large 1.01)
            |null| < 1.00       23
        at -O0 ISOLATED, |null| >= 2.00 in 10 of 66:
            p28 large +1732.73 . p29 large +425.80 . p28 small +281.28 .
            p25 large +269.52  . p29 small +113.76 . p42 large  -31.00 .
            p19 -6.00 (both)   . p46 -3.00 (both)

    ⚠⚠ **AND `whole` IS NOT A NULL AT ALL.** `check_identity` compares
    **`isolated`** digests only (the `digests.get((a, o, "isolated"))` line in
    `check_identity`), so at a `whole` cell there is no `kernel` symbol pinned
    and the difference is `unsafe::main` against `verus::main` -- genuinely
    different programs. p11's `-494.00` is that: `O3/whole/small.bin`, where the
    static traces are 751 against 747 non-pad instructions. **A null control is
    only a null in the MODE ITS IDENTITY PIN COVERS.** For the record, 37 of 66
    `-O3 whole` cells clear 2.00 and 15 clear 20.00 (p11 -494.00/-166.00,
    p29 +465.55/+101.77, p25 +269.52, p28 +211.87/+46.02, p49 +55.57,
    p35 +36.47, p14 +34.00, p42 -33.00, p17 +30.00 both, p18 -25.00,
    p13 +22.00) -- and none of that is a defect, because nothing pins them
    equal.

    ✅ **THE OPERATIVE RULE, AND IT IS WIDER THAN THE ONE THIS DOCSTRING USED TO
    GIVE:** *for a cross-RUNG comparison use `kernel_exclusive_ir`; use
    `marginal_ir_per_call` for anti-collapse, which is what it was built for.*
    The narrow version named only p03 and p04, on the strength of the ±7
    mechanism. The rule binds every pattern whose kernel calls out of itself,
    and on any such pattern a published correction must be compared against
    **that pattern's OWN R5 - R4 null** before it is quoted in a band -- entry
    23 records three published numbers sitting below their own pattern's null,
    `p25 large gcc-clang +19.42` against `+269.52` being the worst at 13.9x.
    `kernel_exclusive_ir` is structurally immune to BOTH mechanisms: 0 of 288
    moved in the pad census above, and it is symbol-scoped so it never charges a
    callee.

    Three consequences. Quote marginals **to the instruction, never to the
    hundredth**, across sessions. **`-O3 isolated` is the least bad column and
    is what `synthesis/synthesize.py::marginal` defaults to, but on p03 and p04
    it is not a quantity** -- there the immune column is `kernel_exclusive_ir`,
    and `results/synthesis.md` withdraws the four cells where the correction
    *is* the whole figure. And if p08's 12 cells move by a few hundredths, or
    p03/p04's `-O3 isolated` cells or p03/p04/p38/p46's `whole` cells move by
    exactly 7 (14 for p46), or any `-O0` cell moves in either mode, between gate
    runs, that is this effect and not a code change.

    ⚠ **Do NOT "fix" this by pinning the gate's environment.** It is cheap --
    `check.py` is not in `measure.py::measurement_sources` -- and it makes the
    number reproducible-and-wrong: one arbitrary draw from a two-state
    distribution, permanently, with nothing marking it as such.

    **The floor is derived, not declared** (TASK_005 A1). `spec.md` used to pin
    an absolute `min_marginal_ir_per_call`, which is a number the pattern author
    can lower in the same commit that breaks the loop -- and p01's was 400
    against a measured minimum of 915, i.e. 0.80 Ir/element against 1.83
    achieved, catching only near-total collapse. Instead:

      * the pattern's `model.py` reports `work_per_call` -- abstract units of
        work the kernel must do on this input, from the input bytes alone;
      * the gate asserts `marginal_Ir >= ALPHA_IR_PER_WORK * work_per_call`,
        with ALPHA a *harness* constant (see the top of this file);
      * given two probe inputs of different shape it also asserts the
        **marginal** rate `d(Ir)/d(work) >= ALPHA`, which is the assertion an
        author cannot satisfy by making the kernel do a fixed amount of work
        regardless of the input.

    A declared floor may still appear in `spec.md`, but it can only *tighten*
    the derived one; lowering it to zero changes nothing."""
    head("3b. NOT-COLLAPSED smoke test: marginal Ir per kernel call vs a "
         "derived floor")
    cfg = contract.get("collapse")
    if not cfg:
        rep.fail("collapse-ir", "spec.md declares no `collapse` section -- "
                                "TASK_003 M4 requires one")
        return {}
    if not enabled:
        rep.fail("collapse-ir", "--no-callgrind given: the dynamic anti-collapse "
                                "assertion did not run, so this gate run does "
                                "not certify that the loop survived")
        return {}
    if not os.path.exists(VALGRIND):
        rep.fail("collapse-ir", f"valgrind missing at {VALGRIND}")
        return {}
    names = cfg.get("probe_inputs") or [cfg.get("probe_input")]
    names = [n for n in names if n]
    if not names:
        rep.fail("collapse-ir", "spec.md's `collapse` names no probe input")
        return {}
    lo, hi = cfg["probe_iters"]
    declared = cfg.get("min_marginal_ir_per_call") or 0
    scratch = os.path.join(REPO, ".temp", "check", buildmod.pattern_id(pdir))

    shapes = []          # (name, {n: probe_path}, dcalls, work_per_call)
    rates = {}           # nm -> (rate, why)
    units = {}           # nm -> (unit name, bits per unit, bound hatch why)
    for nm in names:
        src = os.path.join(indir, nm)
        if not os.path.exists(src):
            rep.fail("collapse-ir", f"probe input {nm} not found")
            return {}
        pr = {n: _probe_input(src, n, os.path.join(scratch, f"probe.{nm}.{n}.bin"))
              for n in (lo, hi)}
        mods = {n: sb(modmod.build, pr[n]) for n in (lo, hi)}
        if any(sbg_opt(mods[n], "expected_hang", False) for n in (lo, hi)):
            # TASK_069, TASK_068_REVIEW m5. `run.timeout_s` is applied by stage
            # 4 only, so a declared-hang probe input would be handed to
            # callgrind with the full `RUN_TIMEOUT` and the stage would die
            # after 900 s rather than say why. No shipped pattern names one --
            # all 20 probe `["small.bin", "large.bin"]` -- so this is closed
            # before the first pattern that could reach it, not after.
            rep.fail("collapse-ir",
                     f"{nm}: model.py declares this input non-terminating "
                     f"(expected_hang), so it cannot be a `collapse.probe_"
                     f"inputs` entry -- the marginal-Ir probe runs it under "
                     f"callgrind twice and no `run.timeout_s` applies there. "
                     f"Probe a terminating input; the hang is stage 4's to "
                     f"record.")
            return {}
        dcalls = sbg(mods[hi], "n_calls") - sbg(mods[lo], "n_calls")
        work = sbg(mods[hi], "work_per_call")
        rates[nm] = (sbg_opt(mods[hi], "min_ir_per_work"),
                     sbg_opt(mods[hi], "min_ir_per_work_why", ""))
        units[nm] = (sbg_opt(mods[hi], "work_unit", "byte"),
                     sbg_opt(mods[hi], "work_unit_bits", 8),
                     sbg_opt(mods[hi], "min_ir_per_work_bound_why", ""))
        if dcalls <= 0:
            rep.fail("collapse-ir", f"{nm}: probe iters {lo}->{hi} produce no "
                                    f"extra kernel calls -- pick another probe")
            return {}
        if not work or work <= 0:
            rep.fail("collapse-ir", f"{nm}: model.py reports work_per_call="
                                    f"{work!r}; a probe input on which the "
                                    f"kernel has nothing to do cannot bound "
                                    f"anything")
            return {}
        shapes.append((nm, pr, dcalls, work))
    works = sorted({w for _, _, _, w in shapes})

    # --- the rate: the harness default, or the algorithm's own lower bound ---
    declared_rates = {r for r, _ in rates.values()}
    if len(declared_rates) > 1:
        rep.fail("collapse-ir",
                 f"model.py reports different min_ir_per_work per probe input "
                 f"({ {k: v[0] for k, v in rates.items()} }). The rate is the "
                 f"cheapest legitimate cost of the *algorithm*; one that varies "
                 f"with the input is a fact about the input.")
        return {}
    # --- the unit, and therefore the bound under the declarable rate ---------
    declared_units = {u for u in units.values()}
    if len(declared_units) > 1:
        rep.fail("collapse-ir",
                 f"model.py reports different work units per probe input "
                 f"({units}). The unit of work is a property of the pattern, "
                 f"not of the input.")
        return {}
    unit_name, unit_bits, bound_why = (next(iter(declared_units))
                                       if declared_units else ("byte", 8, ""))
    try:
        unit_bits = int(unit_bits)
    except (TypeError, ValueError):
        unit_bits = 0
    if unit_bits < 1:
        rep.fail("collapse-ir",
                 f"model.py declares work_unit_bits={unit_bits!r}; it is how "
                 f"many bits one unit of work is (a byte is 8) and it sets the "
                 f"absolute bound under min_ir_per_work. It must be an integer "
                 f">= 1.")
        return {}
    unit_bound = MIN_DECLARABLE_IR_PER_BIT * unit_bits
    bound, hatched, clamped = unit_bound, False, False
    if bound_why:
        bound, hatched = unit_bound / MIN_BOUND_HATCH_FACTOR, True
    if bound < MIN_DECLARABLE_IR_PER_WORK_ABS:
        bound, clamped = MIN_DECLARABLE_IR_PER_WORK_ABS, True

    rate, why = next(iter(rates.values())) if rates else (None, "")
    if rate is None:
        rate, src_of_rate = ALPHA_IR_PER_WORK, "harness default"
    else:
        try:
            rate = float(rate)
        except (TypeError, ValueError):
            rep.fail("collapse-ir", f"model.py's min_ir_per_work is {rate!r}, "
                                    f"which is not a number")
            return {}
        if rate < bound:
            rep.fail("collapse-ir",
                     f"model.py declares min_ir_per_work={rate} Ir per "
                     f"{unit_name}, below the harness's absolute bound {bound} "
                     f"({MIN_DECLARABLE_IR_PER_BIT} Ir/bit x work_unit_bits="
                     f"{unit_bits}"
                     + (f", already lowered {MIN_BOUND_HATCH_FACTOR:.0f}x by "
                        f"model.py's min_ir_per_work_bound_why" if hatched
                        else "")
                     + (f", then CLAMPED back up to "
                        f"{MIN_DECLARABLE_IR_PER_WORK_ABS} because the two knobs "
                        f"compose: work_unit_bits={unit_bits} and the hatch "
                        f"together would give {unit_bound / MIN_BOUND_HATCH_FACTOR}, "
                        f"{MIN_DECLARABLE_IR_PER_WORK / (unit_bound / MIN_BOUND_HATCH_FACTOR):.0f}x "
                        f"under the byte-denominated "
                        f"{MIN_DECLARABLE_IR_PER_WORK}, out of two numbers in the "
                        f"same author-written model.py that also supplies "
                        f"min_ir_per_work and work_per_call" if clamped else "")
                     + f"). Until TASK_008 the only bound was `> 0`, and "
                     f"TASK_006_REVIEW put 1e-9 with why=\"see NOTES.md\" past "
                     f"the whole gate -- 'derived floor 0.0 Ir/call', 'tightest "
                     f"margin 2246270772.2x', nothing inspects `why`. The bound "
                     f"is physical: the tightest rate argued for in this project "
                     f"is p02's 0.0625 Ir/byte (load+store+vpsadbw+vpaddq per "
                     f"64-byte AVX-512 lane), and {MIN_DECLARABLE_IR_PER_WORK} "
                     f"is the same four instructions across a vector four times "
                     f"wider than anything that exists -- per bit, "
                     f"{MIN_DECLARABLE_IR_PER_BIT}. If your kernel really is "
                     f"cheaper than that per unit, the unit is one it does not "
                     f"touch once per unit (a skipping walker denominated in "
                     f"buffer bytes is the shape), and the fix is to "
                     f"**re-denominate work_per_call in the thing the kernel "
                     f"touches** -- records, not bytes. Lowering the floor "
                     + ("further " if hatched else "")
                     + f"instead just stops it saying anything.")
            return {}
        src_of_rate = "model.py"
        if rate < ALPHA_IR_PER_WORK:
            if not why:
                rep.fail("collapse-ir",
                         f"model.py declares min_ir_per_work={rate} below the "
                         f"harness default {ALPHA_IR_PER_WORK} and gives no "
                         f"`min_ir_per_work_why`. Below-default is allowed -- "
                         f"0.25 is unsound for a byte-denominated unit -- but "
                         f"only as an argued claim about the algorithm's "
                         f"cheapest correct implementation, which the verdict "
                         f"then prints on every run.")
            if len(works) < 2:
                rep.fail("collapse-ir",
                         f"min_ir_per_work={rate} is below the harness default "
                         f"and only one probe *shape* is declared, so the one "
                         f"assertion an author cannot satisfy with fixed work "
                         f"-- d(Ir)/d(work) >= rate -- does not run. A loosened "
                         f"absolute floor needs the marginal one.")
    if hatched:
        rep.shout("collapse-ir",
                  f"model.py invoked `min_ir_per_work_bound_why` to lower the "
                  f"harness's ABSOLUTE bound from {unit_bound} to {bound} Ir per "
                  f"{unit_name} -- the hatch under the bound, not the bound "
                  f"under the default. Capped at {MIN_BOUND_HATCH_FACTOR:.0f}x, "
                  f"because an uncapped hatch is `> 0` again"
                  + (f", and CLAMPED at {MIN_DECLARABLE_IR_PER_WORK_ABS} because "
                     f"work_unit_bits={unit_bits} had already lowered it "
                     f"{8 / unit_bits:.0f}x: the two knobs compose, and "
                     f"work_unit_bits=1 plus a full hatch used to give 3.05e-5, "
                     f"512x under the byte bound" if clamped else "")
                  + f". model.py's argument: {bound_why}")
    elif clamped:
        rep.shout("collapse-ir",
                  f"model.py declares work_unit_bits={unit_bits}, which would "
                  f"put the absolute bound at {unit_bound} Ir per {unit_name}; "
                  f"clamped up to the composition bound "
                  f"{MIN_DECLARABLE_IR_PER_WORK_ABS}.")
    for nm, _, dcalls, work in shapes:
        print(f"    probe {nm:16s} n_iters {lo}/{hi} -> +{dcalls} kernel calls, "
              f"work_per_call={work} {unit_name}(s)  => derived floor "
              f"{rate * work:.1f} Ir/call")
    if len(shapes) < 2 or len(works) < 2:
        rep.shout("collapse-ir",
                  f"only one probe *shape* ({names}, work={works}); the marginal "
                  f"d(Ir)/d(work) assertion did not run. A kernel that does a "
                  f"fixed amount of work regardless of its input passes the "
                  f"absolute floor. Add a second `collapse.probe_inputs` entry "
                  f"with a different work_per_call.")
    print(f"    unit  = 1 {unit_name} = {unit_bits} bit(s); EFFECTIVE ABSOLUTE "
          f"FLOOR under min_ir_per_work = {bound} Ir per {unit_name} "
          f"(= {MIN_DECLARABLE_IR_PER_BIT} Ir/bit x work_unit_bits={unit_bits}"
          + (f" / hatch {MIN_BOUND_HATCH_FACTOR:.0f}" if hatched else "")
          + (f", CLAMPED UP to the composition bound "
             f"{MIN_DECLARABLE_IR_PER_WORK_ABS}" if clamped else "")
          + f"); byte-denominated reference {MIN_DECLARABLE_IR_PER_WORK}, so "
          f"this run's floor sits "
          f"{MIN_DECLARABLE_IR_PER_WORK / bound:.0f}x below it")
    print(f"    rate  = {rate} Ir per {unit_name}, from {src_of_rate} "
          f"(harness default {ALPHA_IR_PER_WORK}; NOT settable from spec.md); "
          + (f"spec.md's advisory floor {declared} can only tighten it"
             if declared else "spec.md declares no additional floor"))
    if why:
        print(f"    why   = {why}")

    out, ratios = {}, []
    cg_files = {}
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        per_shape = {}
        for nm, pr, dcalls, work in shapes:
            ir = {}
            for n in (lo, hi):
                cgp = os.path.join(scratch, f"cg.{c}-{o}-{m}.{nm}.{n}.out")
                cg_files[(c, o, m, nm, n)] = cgp
                ir[n] = _callgrind_total(path, pr[n], cgp)
                if ir[n] is None:
                    rep.fail("collapse-ir",
                             f"{c} {o} {m} on {nm}: callgrind produced no total")
                    break
            else:
                slope = (ir[hi] - ir[lo]) / dcalls
                per_shape[nm] = (slope, work)
                out[f"{c}/{o}/{m}/{nm}"] = slope
                floor = max(rate * work, declared)
                if slope < floor:
                    rep.fail("collapse-ir",
                             f"{c} {o} {m} on {nm}: {slope:.0f} Ir per kernel "
                             f"call is below the derived floor {floor:.1f} "
                             f"({rate} x work_per_call={work}) -- "
                             f"the loop is not doing the work the benchmark "
                             f"claims to measure (Ir {ir[lo]:,} -> {ir[hi]:,} "
                             f"over {dcalls} calls)")
        if len(per_shape) >= 2:
            a = min(per_shape.values(), key=lambda t: t[1])
            b = max(per_shape.values(), key=lambda t: t[1])
            if b[1] > a[1]:
                r = (b[0] - a[0]) / (b[1] - a[1])
                ratios.append(r)
                out[f"{c}/{o}/{m}/d_ir_d_work"] = r
                if r < rate:
                    rep.fail("collapse-ir",
                             f"{c} {o} {m}: d(Ir)/d(work) = {r:.3f} < rate "
                             f"{rate}. Ir per call barely moves "
                             f"when the model says the work does "
                             f"({a[0]:.0f} Ir at work {a[1]} -> {b[0]:.0f} at "
                             f"{b[1]}), so the measured loop is not doing this "
                             f"pattern's work.")
    out["_rate"] = rate
    out["_bound"] = bound
    out["_work_unit"] = unit_name
    # TASK_107 §D, decided at TASK_103. Taken HERE rather than in `main()` so it
    # is the environment the callgrind children above actually ran under, in the
    # same process and the same session. Popped in `main()` into
    # `marginal_ir_env`, beside `marginal_ir_per_call`.
    out["_env_block"] = _env_block()
    # Stage 6's dynamic half reuses these profiles rather than running callgrind
    # again -- `_check_region_runs`. Popped in `main()` before the record is
    # written; a path is not a measurement.
    out["_cg_files"] = cg_files
    out["_cg_probe"] = (names[0], hi)
    # --- the achieved margin, printed beside the declared floor --------------
    #
    # TASK_006_REVIEW D: the verdict printed "tightest margin 2246270772.2x" for
    # a floor of 1e-9 in exactly the same words it printed "35.9x" for p02 as
    # shipped, and nothing distinguished them. The margin is the ratio of what
    # was *measured* to what was *declared*, so it bounds both knobs at once --
    # shrink `min_ir_per_work` or shrink `work_per_call` and it explodes either
    # way.
    margins = [v / max(rate * w, declared)
               for (nm, _, _, w) in shapes
               for k, v in out.items() if k.endswith("/" + nm)]
    tight = min(margins) if margins else None
    per = [v for k, v in out.items()
           if not k.endswith("d_ir_d_work") and not k.startswith("_")]
    if tight is not None:
        out["_tightest_margin"] = tight
        if rate < ALPHA_IR_PER_WORK and why:
            rep.shout("collapse-ir",
                      f"this pattern's anti-collapse floor is {rate} Ir per "
                      f"{unit_name}, BELOW the harness default "
                      f"{ALPHA_IR_PER_WORK} (absolute bound {bound})"
                      f". Declared floor {rate * min(works):.1f}...{rate * max(works):.1f} "
                      f"Ir/call; tightest measured margin over it {tight:.1f}x, "
                      f"i.e. this stage tolerates a "
                      f"{100 * (1 - 1 / tight):.1f}% loss of work before it "
                      f"objects. model.py's argument for the rate: {why}")
        if tight > LOOSE_FLOOR_MARGIN:
            rep.shout("collapse-ir",
                      f"the derived floor is {tight:.0f}x below the tightest "
                      f"cell actually measured, so it rules out total collapse "
                      f"and essentially nothing else -- a cell could lose "
                      f"{100 * (1 - 1 / tight):.2f}% of its work and still pass "
                      f"this stage. Read it as a smoke test, not as evidence "
                      f"that the work happened.")
    if per and not any(f[0] == "collapse-ir" for f in rep.failures):
        rep.ok(f"{len(per)} cell/probe pairs: marginal Ir per call "
               f"{min(per):.0f}...{max(per):.0f}, all above the derived floor "
               f"(tightest margin {tight:.1f}x over a declared "
               f"{rate} Ir/{unit_name}); "
               + (f"d(Ir)/d(work) {min(ratios):.2f}...{max(ratios):.2f} "
                  f"(rate {rate})" if ratios else
                  "no second shape, so no marginal-rate assertion"))
        print("    what this stage certifies: that no cell COLLAPSED. It "
              "bounds the kernel's\n    total cost from below, so it cannot "
              "attribute cost to a component and cannot\n    tell a kernel "
              "doing 3% of its work from one doing all of it (p02 clears "
              "its\n    floor on the fold alone). What certifies that the work "
              "happened is step 2 --\n    the reference model's checksum "
              "(`.memory/02-bench-rules.md`).")
    return out


# ==========================================================================
# 3c. structural identity -- a RESULT *and* a gate condition
#
# This header said "a RESULT, not a gate condition" until TASK_028. That was
# FALSE: `check_identity` below calls `rep.fail("identity", ...)` whenever the
# measured level is weaker than the one `spec.md` pins, and `rep.failures`
# makes the run's verdict "FAIL". What is a result and not a gate condition is
# the *level itself* -- the gate records `exact`/`multiset`/`norel` for every
# pair whether or not a pin exists, and a level STRONGER than the pin is
# reported, never failed.
#
# The distinction is load-bearing, not cosmetic. Because the pin is enforced,
# an `identity: unsafe == verus, O3 exact` entry does not merely assert
# something about the two files that ship: it constrains what may occupy the
# R4 role at all, since a candidate R4 with no byte-identical R5 twin that
# Verus verifies could not pass this stage. That is the step by which
# `.memory/01-ladder.md` disqualifies unverifiable R4 candidates from the
# admissible class (TASK_027_REVIEW Q1), and the old comment was the strongest
# textual argument against it anywhere in the tree.
# ==========================================================================

def check_identity(digests, rep, contract):
    head("3c. structural identity R4-vs-R5 (recorded as a result AND enforced)")
    pins = contract.get("identity") or []
    if not pins:
        rep.note("spec.md pins no identity expectations")
    recorded = []
    for pin in pins:
        a, b = pin["a"], pin["b"]
        for o in buildmod.OPTS:
            ka, kb = digests.get((a, o, "isolated")), digests.get((b, o, "isolated"))
            if not ka or not kb:
                rep.note(f"{a}/{b} {o}: one side missing, skipped")
                continue
            level, ev = asm.identity_level(ka, kb)
            want = pin.get(o)
            rec = dict(pair=f"{a} vs {b}", opt=o, level=level, expected=want,
                       md5_fn_a=ev["md5_fn_a"], md5_fn_b=ev["md5_fn_b"],
                       md5_raw_equal=ev["md5_raw_equal"],
                       counts_a=ev["counts_a"], counts_b=ev["counts_b"],
                       pad_a=ev["pad_a"], pad_b=ev["pad_b"])
            recorded.append(rec)
            if want is None:
                rep.note(f"{a} vs {b} {o}: measured {level!r}, spec.md pins "
                         f"nothing")
                continue
            if want not in asm.IDENTITY_LEVELS:
                rep.fail("identity", f"{a} vs {b} {o}: spec.md pins {want!r}, "
                                     f"which is not one of "
                                     f"{asm.IDENTITY_LEVELS}")
                continue
            got_i = asm.IDENTITY_LEVELS.index(level)
            want_i = asm.IDENTITY_LEVELS.index(want)
            if got_i < want_i:
                # A *regression* against the pin. Not "the proof cost
                # something" -- that would be a result; this is the tree no
                # longer matching what spec.md says about itself.
                _, _, d = asm.diff(ka.binary, kb.binary)
                rep.fail("identity", f"{a} vs {b} at {o}: identity dropped to "
                                     f"{level!r}, spec.md pins {want!r}\n"
                                     f"      md5_fn {ev['md5_fn_a'][:12]} vs "
                                     f"{ev['md5_fn_b'][:12]}, counts "
                                     f"{ev['counts_a']} vs {ev['counts_b']}\n{d}")
            else:
                extra = "" if got_i == want_i else "  (stronger than pinned)"
                rep.ok(f"{a} vs {b} {o}: {level} "
                       f"(md5_fn {ev['md5_fn_a'][:12]}; md5_raw equal="
                       f"{ev['md5_raw_equal']}, padding "
                       f"{ev['pad_a'][1]}/{ev['pad_b'][1]} B){extra}")
    return recorded


# ==========================================================================
# 4. adversarial behaviour
# ==========================================================================

def check_adversarial(built, rep, adv_models, indir, cells, budgets=None):
    """`.memory/02-bench-rules.md`: the adversarial row RECORDS per-rung
    behaviour rather than requiring agreement.

    **A cell that does not terminate is one of those behaviours** (TASK_068),
    and it was already representable -- `run_bin` returns `exit=None` and this
    stage folds it into an ordinary row without crashing. What was not viable
    was the COST: `RUN_TIMEOUT` per cell. `budgets` is `{stem: seconds}` from
    the contract (`run_budgets`); an input the model declares `expected_hang`
    gets its budget here, and the row carries `hung` so the table says which
    rungs ran forever instead of leaving it to be inferred from `exit=None`.

    ⚠ **`diverges` is still computed against the model's `expected_exit`, and
    that is deliberate.** The proposal this replaced was `expected_exit = None`
    meaning "expected not to terminate"; it inverts this column. `model.py` is
    the *independent reference* and its `expected_exit`/`expected_stdout` are
    what a CONFORMING implementation does -- and the conforming implementation
    (the Python model itself, and the R5 rung whose `decreases` obligation is
    the whole point of such a pattern) TERMINATES. Under `expected_exit = None`
    the hanging rungs would read `diverges=False` and the one rung that
    terminates would read `diverges=True`: the headline result, printed upside
    down. So the hang is declared in its own field and the divergence column
    keeps its meaning."""
    head("4. adversarial inputs -- behaviour recorded, not required to agree")
    budgets = budgets or {}
    table = {}
    for name, mod in adv_models.items():
        m_exit, m_out = sbg(mod, "expected_exit"), sbg(mod, "expected_stdout")
        stem = stem_of(name)
        budget, hangs = budgets.get(stem), sbg_opt(mod, "expected_hang", False)
        print(f"    -- {name}: {sb(mod.describe)} -> model expects exit "
              f"{m_exit}, stdout {m_out.strip()!r}"
              + (f"  [declared NON-TERMINATING; budget {budget}s]"
                 if hangs else ""))
        n_hung = n_cell = 0
        hung_cells = []
        for c in cells:
            seen = {}
            for (cc, o, m), path in sorted(built.items()):
                if cc != c or not path:
                    continue
                rc, out, err = run_bin(path, os.path.join(indir, name),
                                       timeout=budget)
                n_cell += 1
                n_hung += rc is None
                if rc is None:
                    # (rung, opt, mode, path). Structured rather than a label,
                    # because `_confirm_hang` selects on (rung x opt) and a
                    # pre-formatted string would have to be re-parsed to do it.
                    hung_cells.append((c, o, m, path))
                sig = -rc if rc is not None and rc < 0 else None
                seen.setdefault((rc, out.strip(), err.strip()[:120], sig),
                                []).append(f"{o}/{m}")
            # A LIST, always. `table[f"{name}/{c}"]` used to be ASSIGNED inside
            # this loop, so a rung whose opt/mode variants disagree had N-1 of
            # its behaviours dropped and the survivor was whichever sorted last
            # by `str()` -- with no `opt`/`mode` label saying which cell it came
            # from, while `rep.note` below said only how many were lost.
            # TASK_053 F1: live on 7 patterns (p02/p03/p05/p06/p12/p13/p14),
            # 22 notes, up to 4 behaviours collapsed to 1. PROTOCOL.md's own
            # reviewer checklist asks "adversarial behaviour recorded per rung
            # rather than swept up?" -- this was the sweeping-up.
            rows = []
            for (rc, out, err, sig), where in sorted(seen.items(), key=str):
                rows.append(dict(exit=rc, stdout=out, stderr=err, signal=sig,
                                 cells=sorted(where), model_exit=m_exit,
                                 model_stdout=m_out.strip(), hung=rc is None,
                                 diverges=(rc != m_exit
                                           or out != m_out.strip())))
            table[f"{name}/{c}"] = rows
            for r in rows:
                flag = "  <-- diverges from model" if r["diverges"] else ""
                flag += "  [DID NOT TERMINATE]" if r["hung"] else ""
                print(f"       {c:18s} {','.join(r['cells']):24s} "
                      f"exit={r['exit']!s:5s} stdout={r['stdout']!r:24s}"
                      f" stderr={r['stderr']!r:60s}{flag}")
            if len(seen) > 1:
                rep.note(f"{name}/{c}: opt/mode variants of this rung disagree "
                         f"({len(seen)} distinct behaviours)")
        # Silence is the failure, exactly as it is for `sanitizer_expect:
        # "fires"`: an input declared non-terminating on which every cell
        # terminated means the DoS this pattern exists to model is not being
        # exercised, and the security half of the result is unsupported. Stated
        # with its `n`, and `n == 0` cannot reach the `ok` branch -- this is the
        # count-bearing-`rep.ok` rule (`.memory/02-bench-rules.md`).
        if hangs and n_cell == 0:
            rep.fail("hang", f"{name}: declared non-terminating and no cell was "
                             f"run at all, so the declaration was checked "
                             f"against nothing")
        elif hangs and n_hung == 0:
            rep.fail("hang",
                     f"{name}: model.py declares expected_hang, but all "
                     f"{n_cell} cell(s) terminated inside the {budget}s "
                     f"budget, so no rung ran forever and the declaration is "
                     f"false -- or it was true of a rung this matrix no longer "
                     f"builds. (It cannot be a budget that is too SHORT: a "
                     f"short budget makes cells look like they hang, which is "
                     f"the other branch. A budget that is too LONG is not a "
                     f"failure here either, only slower.)")
        elif hangs and _confirm_hang(rep, name, hung_cells, budget, indir):
            # Only when the confirmation re-run AGREES. Otherwise this `ok`
            # would be printed beside its own failure and would quantify over a
            # cell the gate has just proved terminates -- the same rule
            # `check_hang_declarations` follows.
            rep.ok(f"{name}: declared non-terminating and {n_hung} of {n_cell} "
                   f"cell(s) did not terminate within {budget}s "
                   f"(RUN_TIMEOUT is {RUN_TIMEOUT}s; the budget is a "
                   f"`contract_sha256` pin).")
    return table


def _confirm_hang(rep, name, hung_cells, budget, indir):
    """Re-run **every** hung cell at `10 x budget` and fail if any terminates.

    TASK_069, from TASK_068_REVIEW B2. Without this, "hang" and "slow" are
    indistinguishable to the gate: a real gcc binary that finishes in 3.5 s,
    declared with `timeout_s: 2`, was recorded as a declared hang with **0
    failures**, and being "hung" then switched two checks OFF for that input --
    stage 7 skips the whole `sanitizer_expect` arm (`check_sanitizers`) and
    stage 8 raises the row BLOCKED, unchecked for UB. The budget was the
    author's own number and nothing measured against it.

    ⚠ **THE AXIS IS (rung x opt), AND IT USED TO BE "the first cell in sorted
    matrix order"** (TASK_077, RECAP "Owed" 19b). Sorted order picked
    `c-clang O0` on p22 and **never an `-O3` cell**, which is the one at risk:
    C11 6.8.5p6 lets a compiler assume a side-effect-free loop terminates, so
    the `-O3` build is exactly where a declared hang can quietly stop being
    one. ⚠ **The obvious repair -- one cell per distinct RUNG -- is REFUTED**:
    on p22 that still selects two `O0` cells (`c-gcc O0`, `c-clang O0`) and
    would have caught nothing. Opt level is the axis the risk runs along, and
    rung is the axis the *reason* runs along, so the product is what gets
    confirmed.

    ⚠ **AND THE `mode` COLLAPSE IS GONE TOO, because it was the same unmeasured
    argument in a smaller costume** (TASK_077_REVIEW m3). TASK_077 kept one
    representative per `(rung, opt)`, and `sorted()` made it the **isolated**
    cell every time -- so the `whole` cell, where the kernel is inlined into
    `main` and the C11 6.8.5p6 licence is MOST available, was never re-run. The
    docstring then asserted *"the remaining collapse is over `mode` ... which is
    a linkage difference and not a licence to delete a loop"*, which is an
    argument of exactly the shape this item had just refuted for `rung`. An
    axis is either measured or it is not; this one now is.

    **So the cost is `10 x budget x n_hung`, the number RECAP "Owed" 17
    priced.** Measured on p22, the only pattern that declares a hang: **8** hung
    cells (`c-gcc`/`c-clang` x `O0`/`O3` x `isolated`/`whole`) at a 2.0 s
    budget, so confirmation goes 20 s -> 80 s -> **160 s**. ⚠ "Owed" 17's
    *"p22 hangs 12-20 cells"* is a pre-measurement estimate; it is 8.
    The worst case the matrix allows is 8 rungs x 2 opts x 2 modes = 32 cells,
    which at a 2 s budget is 640 s -- if a pattern ever gets there, the cheap
    lever is `run.timeout_s`, not another collapse.

    Cells are keyed by `(rung, opt, mode)`, which is unique per cell, so the
    dict is a deterministic ordering rather than a selection.

    A failure here is about the BUDGET, not the declaration: the input may
    still make some other rung run forever.

    Returns True when every selected cell is confirmed, so the caller can
    withhold its own `ok` rather than print one beside this failure."""
    if not hung_cells:
        return False
    # Every hung cell. The key is the whole cell coordinate, so this is a sort,
    # not a choice (TASK_078, from TASK_077_REVIEW m3).
    chosen = {}
    for rung, opt, mode, path in sorted(hung_cells):
        chosen.setdefault((rung, opt, mode), path)
    longer = min(RUN_BUDGET_CONFIRM * budget, RUN_TIMEOUT)
    good = []
    for (rung, opt, mode), path in sorted(chosen.items()):
        label = f"{rung} {opt}/{mode}"
        rc, out, _ = run_bin(path, os.path.join(indir, name), timeout=longer)
        if rc is None:
            good.append(label)
            continue
        rep.fail("hang",
                 f"{name}: {label} was recorded as NON-TERMINATING at the "
                 f"pinned {budget}s budget, but it TERMINATED in under "
                 f"{longer}s ({RUN_BUDGET_CONFIRM}x that budget) with exit "
                 f"{rc}, stdout {out.strip()[:60]!r}. The budget is too short "
                 f"to tell a hang from a slow cell, and `run.timeout_s` is the "
                 f"one pin nothing else cross-checks -- so raise it until this "
                 f"cell really does run forever, or drop the `expected_hang` "
                 f"declaration. Note what the short budget was buying: a "
                 f"'hung' row makes stage 7 skip this input's sanitizer "
                 f"expectation and stage 8 report it BLOCKED for Miri.")
    if len(good) != len(chosen):
        return False
    rep.ok(f"{name}: confirmed -- all {len(good)} hung cell(s) "
           f"{good} still had not terminated at {longer}s "
           f"({RUN_BUDGET_CONFIRM}x the pinned budget), so the {budget}s budget "
           f"is measuring a hang and not a slow cell. Every (rung x opt x mode) "
           f"is in that list: no axis is collapsed, which matters most for the "
           f"-O3/whole cells C11 6.8.5p6 puts at risk.")
    return True


# ==========================================================================
# 5. proof domain must cover the measured domain
# ==========================================================================

def _clauses(item, kw):
    return item.clauses.get(kw, []) if item else []


_UNSAFE_RE = re.compile(r"\bunsafe\b")

TWIN_PREFIX = "slb_twin_"
TWIN_CFG = "slb_twin"

# `MAX_TWIN_JUSTIFICATIONS = 1` used to live here and was DELETED at TASK_007,
# on TASK_010_REVIEW's recommendation. Three reasons, in order of weight:
#
#   1. It was a round number, not an argument -- the same shape as
#      `MIN_DECLARABLE_IR_PER_WORK`, which forbade p09's honest bit-denominated
#      `model.py` outright (`.memory/02-bench-rules.md`).
#   2. It was redundant. The case it was introduced for (TASK_009_REVIEW's x3:
#      justify away BOTH of p02's trusted items, ship both known off-by-one
#      weakenings, get a green gate) is already a hard failure under the
#      separate `n_twins == 0` rule below -- "every trusted item in this pattern
#      is excused ... so stage 5c-twin checked the strength of NOTHING".
#      Re-measured at TASK_007 with the cap gone: x3 still FAILS.
#   3. It was the only knob in the twin regime that could hard-fail an *honest*
#      pattern with no route out. A pattern with two genuinely untwinnable
#      trusted items had no legal configuration.
#
# The hatch itself stays: uncapped, `rep.block`ed per item, and shouted every
# run, so a reviewer reads every use of it.


def _is_trusted(item):
    """Is this item part of the trusted base the twin/`requires` rules govern?

    **Not** "its body contains `unsafe`", which is what TASK_005 through
    TASK_009 used and what TASK_009_REVIEW's blocker x1 defeated with three
    lines:

        macro_rules! slb_raw_get { ($v:expr,$i:expr) =>
            { unsafe { *$v.get_unchecked($i) } } }        // outside verus! {}
        fn get_unchecked(...) ensures r == v@[i as int] { slb_raw_get!(v, i) }

    `vparse` parses `fn` items only, so the `macro_rules!` is invisible, and
    `_UNSAFE_RE` searched `item.body`, which now contains no `unsafe` token at
    all. Both the 5a rule ("a trusted `unsafe` item must demand something") and
    5c-twin's trusted list went empty: `requires` deleted, twin deleted, pins
    moved in the same commit, **full gate PASS** printing *"no trusted `unsafe`
    item, so no twin is required"*. That is TASK_003_REVIEW's blocker fully
    re-opened -- R5's trusted base axiomatising that reading any index of any
    slice is defined and equals `v@[i]`. `unsafe` in a `common/driver.rs` helper
    is the same hole without a macro, because the gate never parsed that file.

    The predicate is therefore keyed on the shape that can **axiomatise a
    falsehood**, which is the property the rules are actually about
    (`.memory/04-verus.md`: "a trusted item that asserts nothing cannot
    axiomatise a falsehood"):

        `#[verifier::external_body]`  AND  a non-empty `ensures`

    -- plus the old `unsafe`-in-body limb, kept as a *disjunct* rather than
    replaced, because a trusted body that performs an unchecked operation is UB
    in the shipped binary whether or not it asserts anything about the result.
    Neither limb can be dodged by moving code: hiding the `unsafe` leaves the
    `ensures` (x1), and dropping the `ensures` leaves nothing for the axiom to
    say. `load_input` and `emit` have neither, so they stay out, which is the
    intended behaviour -- they are trusted I/O with no postcondition.

    Note the consequence, which `.memory/04-verus.md` records as a tension and
    this decides: "prefer trusted wrappers with no `ensures`" and "a trusted
    item needs an `ensures` to be checkable" now pull the same way. Where a
    pattern's security rests on a trusted item, give it an `ensures` and a
    twin; a trusted item with neither `ensures` nor `unsafe` is outside the
    regime *and outside the security argument*, and `_scan_unsafe_sites` below
    is what stops the second half of that from being a lie."""
    if item.external != "verifier::external_body":
        return False
    return bool(_clauses(item, "ensures")) or bool(_UNSAFE_RE.search(item.body or ""))


# `include!("h.rs")` -- a MACRO, not a `#[path] mod`, and the fifth route past
# the Verus-side detectors (TASK_098 §4A / MAJOR 4, `.memory/02-bench-rules.md`).
# Rust accepts `include!` with any bracket, and the argument may be a raw string.
_INCLUDE_LIT_RE = re.compile(
    r"\binclude!\s*[(\[{]\s*"
    r"(?:r(?P<hashes>\#*)\"(?P<raw>.*?)\"(?P=hashes)|\"(?P<plain>[^\"]*)\")",
    re.S)
_INCLUDE_ANY_RE = re.compile(r"\binclude!\s*[(\[{]")

# `#[path = "..."]`, and the two other spellings rustc accepts for the SAME
# attribute (TASK_114 M4, closed at TASK_119):
#
#     #[path = "h.rs"]                       the template's spelling
#     #[path = r"h.rs"]                      a RAW string literal
#     #[cfg_attr(all(), path = "h.rs")]      `path` nested in another attribute
#
# ⚠⚠ **WHY THIS HAD TO BE GENERALISED RATHER THAN LEFT AS A RESIDUAL, AND IT IS
# A DESIGN ARGUMENT, NOT WHACK-A-MOLE.** `_path_includes`'s two limbs divide the
# work as *"dep-info is EXACT for what rustc resolves, which is every attribute
# spelling -- and attribute spellings are where the regex kept losing"*.
# **That division FAILS INSIDE `verus!{}`**, where rustc cannot expand the macro
# and dep-info returns nothing, so the regex stands alone. TASK_114 composed the
# two failure families TASK_107 had measured separately and got four routes the
# UNION misses -- and three of them are just these spellings written one
# construct deeper. So the regex must be spelling-insensitive **wherever** the
# other limb can go blind, which is exactly what this covers.
#
# ⚠ **ANCHORED TO AN ATTRIBUTE ON PURPOSE.** The obvious broadening -- match
# `path = "..."` anywhere in the raw text -- is UNSAFE here, because
# `_path_includes` reads RAW text (comments included, deliberately) and the
# emitted file set is then SCANNED by stages that FAIL the gate. A doc comment
# reading `path = "spec.md"` would pull `spec.md` into `_scan_unsafe_sites`,
# which would find the word `unsafe` in prose and turn the gate red. The `#[`
# anchor keeps the over-approximation inside a construct that is at least
# attribute-shaped.
_PATH_ATTR_RE = re.compile(
    r"#!?\[[^\]]*?\bpath\s*=\s*"
    r"(?:r(?P<hashes>\#*)\"(?P<raw>.*?)\"(?P=hashes)|\"(?P<plain>[^\"]*)\")",
    re.S)


def _include_literals(txt, code=None):
    """The string literal argument of every `include!` in `txt`, plus the count
    of `include!`s whose argument is NOT a plain literal.

    The second number is what stops this being a whack-a-mole regex: an
    `include!(concat!(...))` or `include!(env!("OUT_DIR"))` resolves to no path
    a static reader can name, so the honest answer is "I cannot see this file",
    which `_check_opaque_includes` turns into a gate failure rather than into
    the silence that TASK_098 measured.

    ⚠ **`code` is an OFFSET-PRESERVING blanked copy used to FIND the sites; the
    literal is always read back out of the RAW `txt`.** They cannot be the same
    string and the reason is a trap TASK_107 walked into first:
    `vparse.blank_noncode` blanks string literals as well as comments, so
    `include!("h.rs")` becomes `include!(        )` and a check run on the
    blanked text alone would classify **every legitimate literal include as
    OPAQUE** -- turning a false positive on comments into a false positive on
    real code. Offsets survive blanking (`blank_noncode` substitutes spaces of
    equal length), so finding in one string and matching in the other is exact.

    Default `code=None` means "search the raw text", which is what
    `_path_includes` wants: over-approximating a *file set* is safe, so it
    deliberately follows a commented-out include too."""
    lits, n_opaque = [], 0
    for m in _INCLUDE_ANY_RE.finditer(code if code is not None else txt):
        lit = _INCLUDE_LIT_RE.match(txt, m.start())
        if lit is None:
            n_opaque += 1
            continue
        lits.append(lit.group("raw") if lit.group("raw") is not None
                    else lit.group("plain"))
    return lits, n_opaque


# rustc's dep-info runs, memoised on (path, mtime_ns, size). A gate run calls
# `_path_includes` from four places over the same roots; without this each
# pattern would re-invoke rustc ~20 times for one answer. 0.075 s per call
# measured, so this is thrift rather than necessity.
_DEP_INFO_CACHE = {}

# The cfg sets dep-info is asked under. Two runs, and the pair is chosen rather
# than exhaustive: `--cfg slb_isolated` is `build.py::rust_flags`'s isolated
# mode and `--cfg slb_twin` is stage 5c-twin's, so the second run resolves every
# `#[cfg(slb_*)]` module the tree actually builds, while the first (no flags)
# resolves the `#[cfg(not(...))]` side. ⚠ It is NOT a complete cover of `cfg`,
# and it does not need to be -- the regex limb below is cfg-BLIND and therefore
# over-approximates across every combination at once. See `_path_includes`.
_DEP_INFO_CFGS = ((), ("slb_isolated", "slb_twin"))


def _dep_info_files(path, cfgs=()):
    """rustc's OWN module resolution for one root, via `--emit=dep-info`.

    Returns `(files, err)`: `files` is the absolute path of every source rustc
    says the crate reads (the root included), or `None` when rustc wrote no
    dep-info file at all, in which case `err` says why and the caller must FAIL
    CLOSED rather than fall back to the regex silently.

    ⚠ **rustc emits the `.d` even when compilation FAILS**, which is what makes
    this usable here at all: a Verus source does not compile under plain rustc
    (`error[E0433]: cannot find module or crate 'vstd'`), and the dep-info is
    written regardless because module resolution happens before name
    resolution. Measured on all 26 shipped patterns: 0 roots produced no `.d`
    (`.temp/t107/a2_census.py`)."""
    try:
        key = (os.path.realpath(path), os.stat(path).st_mtime_ns,
               os.stat(path).st_size, cfgs)
    except OSError as e:
        return None, str(e)
    if key in _DEP_INFO_CACHE:
        return _DEP_INFO_CACHE[key]
    scratch = os.path.join(REPO, ".temp", "check", "depinfo")
    os.makedirs(scratch, exist_ok=True)
    # PID in the name: two `check.py` processes sharing one `.d` would read each
    # other's answer and the gate would certify the wrong file set. The project
    # runs one agent at a time, so this is prophylaxis -- but a shared mutable
    # scratch path is the kind of thing that only bites once somebody
    # parallelises the sweep, which is exactly when nobody is looking.
    # ⚠ `line.split()` below assumes no whitespace in any source path; rustc
    # backslash-escapes those in a `.d` and this does not un-escape them. No
    # path in this tree has one.
    dot_d = os.path.join(scratch, f"dep.{os.getpid()}.d")
    if os.path.exists(dot_d):
        os.remove(dot_d)
    cmd = [buildmod.RUSTC, "--edition", "2021", f"--emit=dep-info={dot_d}"]
    for c in cfgs:
        cmd += ["--cfg", c]
    cmd.append(os.path.abspath(path))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                           cwd=REPO)
    except (OSError, subprocess.TimeoutExpired) as e:
        res = (None, f"{buildmod.RUSTC} did not run: {e}")
        _DEP_INFO_CACHE[key] = res
        return res
    if not os.path.exists(dot_d):
        res = (None, f"{buildmod.RUSTC} wrote no dep-info (rc={r.returncode}): "
                     f"{(r.stdout + r.stderr).strip()[-200:]}")
        _DEP_INFO_CACHE[key] = res
        return res
    files = []
    for line in open(dot_d):
        if line.startswith(dot_d + ":"):
            files = [os.path.abspath(os.path.join(REPO, f))
                     for f in line.split(":", 1)[1].split()]
    res = (files, "")
    _DEP_INFO_CACHE[key] = res
    return res


def _path_includes(pdir, srcs, errors=None):
    """Every file the given sources pull into their crate with
    `#[path = "..."] mod ...` **or `include!("...")`**, TRANSITIVELY. Those
    files are part of the token stream the compiler and Verus see, and no
    pattern-local check ever parsed them: `common/driver.rs` is
    `#[verifier::external]` for R5, so an `unsafe` helper or a
    `#[cfg(slb_twin)]` item in it is invisible to every rule keyed on the
    pattern's own sources.

    ⚠ **Two holes closed at TASK_099, both latent (0 hits over the 24 shipped
    patterns) and both reaching every detector this feeds** -- the three
    Verus-side ones through `_verus_file_list`, plus `_scan_unsafe_sites` and
    `_check_twin_cfg_hygiene`, which call it directly:

    1. **`include!` is a macro, not a module declaration**, so neither pattern
       below matched it and the walk never saw the file. TASK_098 §4A measured a
       `verus.rs` whose `unsafe` lived in an `include!`d sibling: `1 verified, 0
       errors`, `_scan_unsafe_sites` 0 failures, `_path_includes` `[]` -- which
       is TASK_009_REVIEW's blocker x1 reached by a different spelling.
    2. **The walk was ONE LEVEL DEEP.** `verus.rs` -> `#[path]` -> `driver.rs`
       was seen; anything `driver.rs` itself pulled in was not, because the
       loop only ever read `srcs`. That is the same hole with no new spelling at
       all, and it needs no macro. It is now a fixed point, and
       `.temp/t99/b3_routes.py` shows it live at HEAD:
       `#[path]`-of-`#[path]` verifies `1 verified, 0 errors` with the leaf
       unscanned.

    Include paths resolve against **the directory of the file that names them**
    (both `#[path]` on a file-level `mod` and `include!` are relative to the
    including file), which is what makes the transitive step correct rather than
    merely deeper: a `mod` inside `common/driver.rs` names a file beside
    `driver.rs`, not beside `verus.rs`.

    ⚠ **A file that is BOTH a root and an include target is still returned**,
    and the two sets are tracked separately for that reason. `srcs` are read for
    *their* includes, but being readable is not being scanned: callers scan
    `verus.obligations` plus what this returns, and `pdir/*.rs` is passed in as
    a root purely so a stray sibling's `#[path]` is followed. Folding the roots
    into the emitted set would drop exactly TASK_098 §4A's measured route --
    `verus.rs` `include!`ing a **sibling** `.rs`, which is in `pdir/*.rs` and
    therefore a root -- and this function returned `[]` for it in the first
    version of this fix.

    ⚠⚠ **TASK_107: THE REGEX WALK IS NOW ONE OF *TWO* LIMBS, AND THE SECOND IS
    THE COMPILER. `--emit=dep-info` DOES NOT REPLACE THIS WALK, IT UNIONS WITH
    IT -- BECAUSE VERUS IS A DIFFERENT FRONT END AND REPLACEMENT WOULD OPEN
    THREE ROUTES IT CLOSES TWO OF.** `.memory/02-bench-rules.md` proposes
    replacement, on the (correct) ground that nine routes have been found by
    three tasks and a regex approximation of rustc's module resolution will not
    converge. Measured before rewriting (`.temp/t107/a1_routes.py`, 14 routes x
    3 instruments, every arm run):

        route                       Verus reads it   dep-info   regex walk
        R1..R4  include! x4              yes            yes         yes
        R5      #[path] mod              yes            yes         yes
        R6      #[path]-of-#[path]       yes            yes         yes
        R7      macro_rules! -> #[path]  yes            yes         yes
        R7a     #[cfg_attr(all(),path)]  yes            yes         NO -> yes
        R7b     #[path = r"h.rs"]        yes            yes         NO -> yes
        R7c     mod x { mod m; }         yes            yes         NO -> yes
        N1      #[path] INSIDE verus!{}  yes            NO          yes
        N2      include! INSIDE verus!{} yes            NO          yes
        N3      #[cfg(slb_twin)] #[path] yes            NO*         yes
        CONTROL no include at all         -              -           -

    * with `--cfg slb_twin` set, dep-info does list it; without, it does not.
    ⚠ The `NO -> yes` cells are TASK_119's; the table as TASK_107 measured it
    read `NO`. See the residuals below for what is still `NO`.

    **N1 and N2 are the finding, and they are new.** rustc cannot expand the
    `verus!` proc macro (`error: cannot find macro 'verus' in this scope`), so
    a `mod` declared inside `verus!{}` never becomes a module rustc resolves --
    while Verus, whose macro it is, splices the file in and reports
    `1 verified, 0 errors` with the leaf's `unsafe` unscanned. **dep-info
    answers for RUSTC's module graph; the gate's question is about VERUS's.**

    So the division of labour, and each half is doing what it is good at:

      * **dep-info is EXACT for what rustc resolves**, which is every attribute
        spelling -- and attribute spellings are where the regex kept losing.
      * **the regex is CFG-BLIND and MACRO-BLIND, which over-approximates**, and
        over-approximating a *file set* is the safe direction (this docstring's
        own rule, unchanged). That is exactly what covers N1/N2/N3.

    ~~Union of the two: 13 of 13 routes. Either alone: 10 of 13.~~
    ⚠ **On the 26 shipped patterns the union is a NO-OP** -- dep-info adds 0
    files and misses 0 (`.temp/t107/a2_census.py`), so this is latent, like
    every earlier limb of this walk.

    ⚠⚠ **`13 OF 13` WAS TRUE OF THE TABLE AND FALSE OF THE PROBLEM (TASK_114
    M4).** The table has two failure families -- the regex loses on attribute
    spellings, dep-info loses on anything inside `verus!{}` -- and **no row
    composes them**. Compose them and the union misses four:

        N7aV  #[cfg_attr(all(), path = "h.rs")] mod m;   inside verus!{}
        N7bV  #[path = r"h.rs"] mod m;                   inside verus!{}
        N7cV  mod x { mod m; }   (leaf x/m.rs)           inside verus!{}
        N8V   macro_rules! taking the path as an ARGUMENT (`#[path = $p]`,
              so no literal ever sits beside `path` in the raw text),
                                                         inside verus!{}

    Each reaches `1 verified, 0 errors` with the leaf's `unsafe` unscanned --
    TASK_098 §4A's shape at a fourteenth, fifteenth, sixteenth and seventeenth
    spelling. ⚠ **N8 and N9 (the same macro, and a SYMLINKED leaf, at TOP
    level) are both CAUGHT, by dep-info** -- which is the division of labour
    working, and the reason only the `verus!{}` column matters.

    **TASK_119 closed the first three, and the argument is a design one rather
    than another round of whack-a-mole:** the division of labour above says the
    regex may lose on attribute spellings *because dep-info is exact for them*,
    and **that premise is void inside `verus!{}`, where the regex stands
    alone.** So the regex is now spelling-insensitive (`_PATH_ATTR_RE`, raw
    strings and nested attributes) and resolves one level of inline `mod`
    nesting. ✅ Two measurements, because the change has two claims:
    `.temp/t119/c1_union_routes.py` shows the three routes are now FOUND and
    N8V still is not, with both controls holding; `.temp/t119/c2_census.py`
    shows the widening is a **strict no-op on the shipped tree** -- all 26
    patterns' union byte-identical to what `git show HEAD:harness/check.py`
    computes, still exactly `['common/driver.rs']`, and its own must-fire arm
    proves the two implementations really differ.

    ⚠⚠ **NAMED RESIDUALS -- WHAT IS STILL UNCOVERED, SO THE NEXT READER DOES
    NOT HAVE TO REDISCOVER IT.** This project has found nine routes across
    three tasks plus four more at TASK_114, **each after the previous table
    read as exhaustive**, so the honest posture is a named list, not a claim of
    completeness:

    1. **N8V -- a `#[path]` whose value arrives as a MACRO ARGUMENT, inside
       `verus!{}`.** Structurally different from the other three: there is no
       literal in the text to resolve, so no regex can see it and the fix is
       not a spelling. It is the `include!(concat!(...))` class, which
       `_check_opaque_includes` refuses outright -- and the same refusal cannot
       be applied here without failing the gate on every `macro_rules!` in the
       tree. **Open.**
    2. **Inline `mod` nesting DEEPER THAN ONE LEVEL** (`mod a { mod b { mod m;
       } }` -> `a/b/m.rs`), inside `verus!{}`. One level is covered above; two
       is not, and the correct fix is brace tracking rather than a wider
       over-approximation.
    3. **Anything requiring `cfg` evaluation that `_DEP_INFO_CFGS` does not
       enumerate**, when the construct also sits inside `verus!{}`. The regex
       limb is cfg-BLIND, which is what covers N3 today; the residual is any
       route where BOTH limbs need the cfg.

    ⚠ **All three are DELIBERATE-AUTHOR routes, and `.memory/02-bench-rules.md`
    settles the posture: the gate's threat is an honest mistake.** All 26
    patterns spell this one way -- `#[path = "../../common/driver.rs"] mod
    driver;`, at top level, copied from the p01 template -- and nobody reaches
    for a macro-argument module path by accident.

    A dep-info run that produces no `.d` at all is **not** silently absorbed:
    `errors` collects it and `_check_opaque_includes` turns it into a gate
    failure. Falling back to the regex quietly would reproduce the hole under a
    new name."""
    out, queue, walked, emitted = [], [], set(), set()
    for src in srcs:
        p = os.path.join(pdir, src)
        if os.path.exists(p):
            queue.append(p)
            walked.add(os.path.realpath(p))
    # --- limb 2: ask the compiler, once per root, before walking -------------
    # Seeded into `queue` as well as into `out`, so a file dep-info finds is
    # then walked by the regex for whatever IT pulls in -- the two limbs
    # compose rather than sitting side by side.
    for src in srcs:
        p = os.path.join(pdir, src)
        if not os.path.exists(p):
            continue
        for cfgs in _DEP_INFO_CFGS:
            files, err = _dep_info_files(p, cfgs)
            if files is None:
                if errors is not None:
                    errors.append((os.path.relpath(p, REPO), cfgs, err))
                continue
            for f in files:
                real = os.path.realpath(f)
                if real == os.path.realpath(p) or not os.path.isfile(f):
                    continue
                rel = os.path.relpath(f, os.path.dirname(p) or ".")
                if real not in emitted:
                    emitted.add(real)
                    out.append(os.path.normpath(os.path.join(
                        os.path.dirname(p) or ".", rel)))
                if real not in walked:
                    walked.add(real)
                    queue.append(f)
    while queue:
        path = queue.pop(0)
        base = os.path.dirname(path) or "."
        # The RAW text, not `blank_noncode`: the path is a string literal, which
        # blanking erases. A commented-out `#[path]` therefore gets scanned too,
        # which is the safe direction.
        txt = open(path).read()
        cand = [m.group("raw") if m.group("raw") is not None else m.group("plain")
                for m in _PATH_ATTR_RE.finditer(txt)]
        cand += _include_literals(txt)[0]
        # ...and a plain `mod foo;`, which resolves to a sibling file rather than
        # to a declared path. No pattern uses that today; leaving it out would
        # mean an `unsafe` helper or a `#[cfg(slb_twin)]` item in `foo.rs` was
        # outside both scans, which is the whole shape of the bug this exists to
        # close.
        code = vparse.blank_noncode(txt)
        # ⚠ `mod x { mod m; }` resolves to `x/m.rs`, NOT to `m.rs` beside the
        # file -- route N7cV (TASK_114 M4), closed at TASK_119. The declaration
        # was always FOUND; it was RESOLVED to the wrong path and then dropped
        # by the `os.path.exists` filter below, which is a miss that looks
        # exactly like a clean scan. Rather than track brace nesting (a parser),
        # every inline `mod NAME {` in the file is offered as a candidate
        # PREFIX, which over-approximates -- the safe direction for a file set,
        # and the `os.path.exists` filter throws the rest away.
        # ⚠ ONE LEVEL of nesting. `mod a { mod b { mod m; } }` -> `a/b/m.rs`
        # is still uncovered; see this function's residuals.
        # ✅ Strictly a no-op on the shipped tree: `grep -E '\bmod\s+\w+\s*\{'`
        # over `patterns/**/*.rs` and `common/*.rs` returns NOTHING, so no
        # prefix is ever generated and the 26-pattern census is unchanged.
        prefixes = [""] + [m.group(1) for m in
                           re.finditer(r"\bmod\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{",
                                       code)]
        for m in re.finditer(r"\bmod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", code):
            for pre in prefixes:
                cand += [os.path.join(pre, m.group(1) + ".rs"),
                         os.path.join(pre, m.group(1), "mod.rs")]
        for inc in cand:
            p = os.path.normpath(os.path.join(base, inc))
            if not os.path.exists(p):
                continue
            real = os.path.realpath(p)
            if real not in emitted:
                emitted.add(real)
                out.append(p)
            if real not in walked:
                walked.add(real)
                queue.append(p)
    return out


def _check_opaque_includes(rep, pdir, contract):
    """`include!` whose argument no static reader can resolve: refuse it.

    `_path_includes` closes `include!("h.rs")` by resolving the literal. The
    residue is `include!(concat!(env!("OUT_DIR"), "/gen.rs"))` and friends,
    where there is no path to resolve and the honest verdict is a refusal
    rather than an empty list -- the same posture as `--emit` refusing to write
    a `NOT-BUILT` licence sidecar. **This is the only new failure mode TASK_099
    adds, and the "could this happen by accident?" test is why it is safe: the
    24 shipped patterns contain ZERO `include!` of any spelling**, and no
    honest author of a five-rung micro-benchmark reaches for a generated
    include when `harness/build.py` invokes `rustc` directly with no build
    script and no `OUT_DIR` in the environment.

    ⚠⚠ **TASK_107 FIXES THREE THINGS THAT MADE THIS CHECK FAIL THE GATE ON
    PROSE, AND THE ACCIDENT ROUTE WAS ONE DOC COMMENT AWAY.**

    1. **It read the RAW text, so 5 of 5 comment/string shapes turned the gate
       RED**: a line comment, a `//!` doc comment, a block comment, the idiom
       inside a string literal, and a commented-out `include!` of a real path
       (`.memory/02-bench-rules.md`). `_path_includes` reads raw text
       *deliberately* -- over-approximating a **file set** is safe -- but for a
       check that FAILS the gate over-approximation is the unsafe direction.
       Fixed by locating sites in `vparse.blank_noncode(txt)`.
       ⚠ **The literal is still read from the RAW text**, because blanking
       erases string literals and would make every real include look opaque;
       `_include_literals`'s docstring has the trap in full.
       ⚠ **The accident was NEAR**: `include!(concat!(env!("OUT_DIR"),
       "/gen.rs"))` is the canonical example sentence in this docstring, in
       `.memory/02-bench-rules.md` and in two task reports -- **the first author
       who quoted it in a rung source's doc comment failed the gate.**
    2. **The diagnostic asked for the one impossible thing.** For the
       build-script idiom there IS no literal path, so *"Use a literal path"*
       was unactionable. It now says what to do instead.
    3. **SCOPE: EXTENDED to the pattern's own `*.rs` roots** (TASK_107; the gap
       was reported at TASK_103 as pre-existing and undecided). It used to
       cover the `verus.obligations` sources plus everything the walk reached,
       so an opaque `include!` in `safe_tuned.rs` was not refused. The reason
       given for leaving it was that no stage scans the safe rungs for `unsafe`
       tokens -- true, and **not the only thing at stake**: stage 0b's spelling
       audit, `dloop`'s driver-loop diff and `exec_code` all read rung sources,
       and an unresolvable `include!` hides tokens from every one of them, so
       the audit would report on a file set missing the spliced code. Cost of
       extending: zero rows, the 26 shipped patterns contain no `include!` of
       any spelling.

    It also adjudicates the dep-info limb of `_path_includes`: **if rustc
    produced no dep-info for a root the gate must judge, that is a FAILURE, not
    a silent fallback to the regex.**"""
    vcfg = contract.get("verus") or {}
    srcs = sorted(vcfg.get("obligations") or {})
    roots = srcs + sorted(f for f in os.listdir(pdir) if f.endswith(".rs"))
    files, seen = [], set()
    for r in roots:                       # scope limb 3: the roots themselves
        p = os.path.join(pdir, r)
        if os.path.realpath(p) not in seen:
            seen.add(os.path.realpath(p))
            files.append((r, p))
    dep_errors = []
    for p in _path_includes(pdir, roots, errors=dep_errors):
        if os.path.realpath(p) not in seen:
            seen.add(os.path.realpath(p))
            files.append((os.path.relpath(p, REPO), p))
    for rel, path in files:
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        lits, n_opaque = _include_literals(txt, code=vparse.blank_noncode(txt))
        for lit in lits:
            if not os.path.exists(os.path.normpath(
                    os.path.join(os.path.dirname(path) or ".", lit))):
                rep.fail("tcb-unsafe",
                         f"{rel}: `include!(\"{lit}\")` names a file that does "
                         f"not exist, so the gate cannot scan what the compiler "
                         f"splices in. Point it at a real file or delete it.")
        if n_opaque:
            rep.fail("tcb-unsafe",
                     f"{rel}: {n_opaque} `include!` whose argument is not a "
                     f"string literal. The gate resolves `include!(\"h.rs\")` "
                     f"and walks the file (TASK_099); a computed argument -- "
                     f"`concat!`, `env!`, a `macro_rules!` expansion -- names no "
                     f"path a static reader can follow, so every Verus-side "
                     f"detector would report on a file set that is missing the "
                     f"spliced tokens. That is TASK_098 §4A's route with the "
                     f"resolution step removed. WHAT TO DO: if the argument is "
                     f"a literal you can write, write it. If it is the "
                     f"build-script idiom (`concat!`/`env!(\"OUT_DIR\")`) there "
                     f"is no literal to write and there is no build script "
                     f"either -- `build.py` invokes rustc directly and sets no "
                     f"`OUT_DIR` -- so the generated file cannot be part of a "
                     f"rung at all: commit the generated code as a real `.rs` "
                     f"in the pattern directory (its generator belongs in "
                     f"`controls/`, which the gate hashes) and `include!` THAT "
                     f"by a literal path. If you are QUOTING the idiom to "
                     f"explain it, put it in a comment or a string -- since "
                     f"TASK_107 this check reads code only and will not see "
                     f"it.")
    # LAST, so that a root with a concrete include defect is diagnosed by the
    # message that names the defect and this one reads as the corollary it is:
    # a root rustc cannot expand produces no `.d`, and a broken `include!`/`mod`
    # in that root is the commonest cause.
    for rel, cfgs, err in dep_errors:
        rep.fail("tcb-unsafe",
                 f"{rel}: `{buildmod.RUSTC} --emit=dep-info"
                 + ("".join(f' --cfg {c}' for c in cfgs))
                 + f"` produced no dep-info file, so the compiler's own module "
                 f"resolution is unavailable for this root and the gate would "
                 f"be judging it on the REGEX WALK ALONE. That walk is known "
                 f"to miss `#[cfg_attr(all(), path=...)]`, `#[path = "
                 f"r\"...\"]` and `mod x {{ mod m; }}` (TASK_103, re-measured "
                 f"at TASK_107), so this run cannot certify the file set: "
                 f"FAILING CLOSED rather than falling back silently. Note "
                 f"rustc writes the `.d` even when compilation FAILS -- all 26 "
                 f"patterns' Verus sources produce one despite `E0433: cannot "
                 f"find module or crate 'vstd'` -- so the causes that reach "
                 f"here are a root rustc cannot PARSE or EXPAND (a broken "
                 f"`include!`/`mod` above is the commonest, and will have its "
                 f"own failure line), or rustc itself being absent. rustc "
                 f"said: {err}")


def _verus_file_list(pdir, srcs):
    """`[(key, path)]` for every file a Verus-side check must read: the pinned
    `verus.obligations` sources keyed by their bare names, then every file the
    rungs `#[path]`-include, keyed **repo-relative**.

    One list, so the detectors that share a threat stop having different file
    sets. That divergence is `TASK_084_REVIEW` major 1 and RECAP "Owed" 0's
    seventh route: `_check_axiom_decls` and `_axiom_items` walked the includes
    and `_trusted_items`, the TCB inventory and the `assume(`/`admit(` shout did
    not.

    ⚠ **Deduplicated by real path, the pinned key winning**
    (`TASK_084_REVIEW` minor 5). `_path_includes` resolves `#[path]` targets
    against `pdir`, so an include that lands *inside* the pattern directory --
    `#[path = "helper.rs"] mod helper;` where `helper.rs` is also a pinned
    obligation source -- used to arrive **twice**, once as `helper.rs` and once
    as `patterns/pNN-x/helper.rs`. Every caller then demanded two declarations
    for one file and counted its axioms and its trusted items twice.
    `.memory/05-layout.md`'s *"the two key spaces cannot collide"* is true;
    *"cannot duplicate"* was not, and this is where it is fixed."""
    seen, out = set(), []
    for src in srcs:
        path = os.path.join(pdir, src)
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        out.append((src, path))
    for p in _path_includes(pdir, list(srcs) + sorted(
            f for f in os.listdir(pdir) if f.endswith(".rs"))):
        real = os.path.realpath(p)
        if real in seen:
            continue
        seen.add(real)
        out.append((os.path.relpath(p, REPO), p))
    return out


def _scan_unsafe_sites(rep, pdir, contract):
    """Every `unsafe` token in the proof's source, not one `fn` body at a time.

    `_is_trusted` above fixes *which items* the rules govern. This fixes the
    other half of x1: the gate must know about `unsafe` that is not inside any
    parsed item at all -- a `macro_rules!`, a `const`/`static` initialiser, an
    `unsafe impl`, a nested closure outside a `fn`, or a helper in the shared
    `common/driver.rs`, which no pattern-local parse ever reads. Each of those
    performs an unchecked operation that no `requires` demands and no twin
    checks.

    Rule: in a pinned Verus source, every `unsafe` token must sit inside the
    body of an item this gate treats as trusted (`_is_trusted`), so that the
    5a `requires` rule and the 5c-twin rule reach it. Anywhere else is a hard
    failure naming the line. The same scan runs over the `common/` files the
    pattern pulls in with `#[path = "../../common/..."]`, where `unsafe` is a
    hole with no macro required."""
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    n_ok = 0
    for src in sorted(pinned_obl):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        code = vparse.blank_noncode(txt)
        try:
            items = vparse.parse(txt)
        except ValueError as e:
            rep.fail("tcb-unsafe", f"{src}: {e}")
            continue
        spans = [(i.body_start, i.body_end, i.name) for i in items
                 if _is_trusted(i) and i.body_start is not None]
        for m in _UNSAFE_RE.finditer(code):
            # `unsafe fn` / `unsafe impl` modifiers and `unsafe` blocks alike:
            # the question is only whether the token is inside a trusted body.
            host = [nm for a, b, nm in spans if a <= m.start() < b]
            if host:
                n_ok += 1
                continue
            rep.fail("tcb-unsafe",
                     f"{src}:{txt.count(chr(10), 0, m.start()) + 1} an `unsafe` "
                     f"token sits outside every trusted item's body, so no "
                     f"`requires` rule and no verified twin governs it. This is "
                     f"TASK_009_REVIEW's blocker x1: a `macro_rules!` holding "
                     f"`unsafe {{ *$v.get_unchecked($i) }}` is invisible to "
                     f"`vparse` (which parses `fn` items only), so the trusted "
                     f"item's body contained no `unsafe` token, 5a said nothing "
                     f"and 5c-twin reported \"no trusted `unsafe` item, so no "
                     f"twin is required\" -- with the `requires` and the twin "
                     f"both deleted and the pins moved in the same commit. Put "
                     f"the unchecked operation inside an "
                     f"`#[verifier::external_body]` item with a `requires`, an "
                     f"`ensures` and a `#[cfg({TWIN_CFG})]` twin.")
    # ...and the shared driver, which is `#[verifier::external]` for R5 and so
    # is never parsed by any pattern-local check. An `unsafe` helper there is
    # x1 without needing a macro: the trusted item's body just calls it.
    seen_common = _path_includes(
        pdir, sorted(pinned_obl) + sorted(f for f in os.listdir(pdir)
                                          if f.endswith(".rs")))
    for p in seen_common:
        code = vparse.blank_noncode(open(p).read())
        rel = os.path.relpath(p, REPO)
        for m in _UNSAFE_RE.finditer(code):
            rep.fail("tcb-unsafe",
                     f"{rel}:{code.count(chr(10), 0, m.start()) + 1} `unsafe` in "
                     f"a shared driver file the rungs `#[path]`-include. The "
                     f"gate never parses this file, so nothing requires a "
                     f"precondition of it and no twin checks it -- a trusted "
                     f"item whose body is `driver::raw_get(v, i)` has the whole "
                     f"of x1's effect with no macro. Keep unchecked operations "
                     f"in the pattern's own `#[verifier::external_body]` items.")
    if seen_common:
        print(f"    scanned for `unsafe` outside a trusted body: "
              f"{sorted(pinned_obl)} + {[os.path.relpath(p, REPO) for p in seen_common]}"
              f" ({n_ok} token(s) inside a trusted body)")


def _check_trusted_unsafe(rep, src, tcb, justifications):
    """TASK_005 A3, and the whole reason TASK_005 exists.

    TASK_003_REVIEW made R5's trusted base axiomatise "reading any index of any
    slice is defined and yields `v@[i]`" by deleting three lines from
    `verus.rs` and three from `spec.md` in one commit: `get_unchecked` kept its
    `ensures r == v@[i as int]` and lost its `requires i < v@.len()`. The proof
    then establishes nothing about memory safety, every `N verified, 0 errors`
    is unchanged, and the pinned-contract diff passes because the pin moved
    too.

    No *declared* pin can catch that, because the attacker writes the pins. So
    this is a structural rule instead: **an `external_body` item whose body
    contains `unsafe` must carry a non-empty `requires`.** A trusted item that
    performs an unchecked operation and demands nothing of its callers is an
    axiom that the operation is always safe.

    The escape hatch is deliberately expensive to use: `spec.md` may carry a
    per-item justification string, and the gate then prints it in the verdict
    every single run, where a reviewer reads it.

    **TASK_006_REVIEW re-opened this on the item p02 exists to be about.** A
    *non-empty* `requires` satisfies the rule above and says nothing:
    `copy_bytes` weakened to `requires n >= 0` -- which is `true` for a `usize`
    -- gave 9 verified, 0 errors, did not move the obligation count, and this
    very function printed it approvingly ("trusted `unsafe` item `copy_bytes`
    demands `['n >= 0']` of every caller"). Deleting `from + n <= src@.len()`
    outright did the same. **No verify/fail oracle can catch either** -- measured
    at TASK_008: deleting a precondition from a trusted item makes every call
    site strictly easier, so nothing ever fails (control 9/0, M1 9/0, M2 9/0,
    M3 9/0; the same deletion applied to the *verified* `kernel` gives 8/1).

    So there is a second structural rule, and it is the one that catches all
    three: **every parameter the trusted body uses must be constrained by the
    `requires`.** A trusted item that performs an unchecked operation on `src`
    and `from` while demanding nothing about either is the axiom that the
    operation is defined for all values of them. Not `ensures` -- `get_unchecked`
    weakened to `requires 0 <= i` keeps `ensures r == v@[i as int]`, so a
    requires-or-ensures reading would pass it.

    Known false positive, and the reason the justification hatch covers this
    rule too: a pure *value* parameter (`fn write(dst, i, v)` -- `v` is written,
    never used as an address) genuinely needs no precondition. Say so in
    `spec.md` and the verdict shouts it on every run.

    **TASK_010 A: the scope is `_is_trusted`, not `unsafe`-in-the-body.** One
    `macro_rules!` deleted this whole regime at TASK_009_REVIEW (blocker x1) --
    read `_is_trusted` for why the predicate is now `external_body` plus either
    a non-empty `ensures` or `unsafe` in the body, and `_scan_unsafe_sites` for
    the `unsafe` this function can no longer be the only reader of."""
    for i in tcb:
        if not _is_trusted(i):
            continue
        reqs = _clauses(i, "requires")
        if reqs:
            try:
                pars = vparse.param_names(i)
            except ValueError as e:
                rep.fail("tcb-unsafe", f"{src}:{i.line} `{i.name}`: {e}")
                continue
            body_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", i.body or ""))
            # A COMMENT IS NOT CLAUSE TEXT. This rule is a bag of every
            # identifier-shaped token in the joined clause text, so before
            # TASK_053 F4 a parameter named only in a `//` or `/* */` beside the
            # clause counted as constrained: `requires i < v@.len(), // n is
            # bounded by the caller` on an item whose body reads `i + n` passed
            # this rule, and the same item with the comment deleted fails it.
            # The repair is in `vparse._clause_split`, which now blanks comments
            # before splitting, so `reqs` cannot contain comment text at all;
            # the second blanking here is belt-and-braces and costs nothing.
            req_ids = set(re.findall(
                r"[A-Za-z_][A-Za-z0-9_]*",
                " ".join(vparse.blank_comments(c) for c in reqs)))
            used = [p for p in pars if p in body_ids]
            bare = [p for p in used if p not in req_ids]
            if bare and not justifications.get(i.name):
                rep.fail("tcb-unsafe",
                         f"{src}:{i.line} trusted item `{i.name}` "
                         f"demands {reqs} of its callers, which constrains "
                         f"nothing about {bare} -- parameter(s) its own trusted "
                         f"body uses. That is the axiom that the unchecked "
                         f"operation is defined for every value of {bare}, "
                         f"which is exactly how `requires n >= 0` on a `usize` "
                         f"passed the gate at TASK_006_REVIEW. No verification "
                         f"result can catch it: deleting a precondition from a "
                         f"trusted item makes every call site strictly easier, "
                         f"so the file still reports 0 errors. If the parameter "
                         f"is a pure value that needs no precondition, declare "
                         f"verus.unsafe_justifications[{src!r}][{i.name!r}] in "
                         f"spec.md and the verdict will shout it every run. "
                         f"AND: if the constraint is stated in a COMMENT beside "
                         f"the clause, it is not stated -- comments are blanked "
                         f"before this rule reads the clause text (TASK_053 F4).")
                continue
            if bare:
                rep.shout("tcb-unsafe",
                          f"{src}:{i.line} `{i.name}`'s `requires` constrains "
                          f"nothing about {bare}, which its trusted body uses. "
                          f"spec.md justifies it: {justifications[i.name]}")
                continue
            rep.ok(f"{src}: trusted item `{i.name}` demands "
                   f"{reqs} of every caller, constraining every parameter its "
                   f"body uses ({used})")
            continue
        why = justifications.get(i.name)
        if not why:
            rep.fail("tcb-unsafe",
                     f"{src}:{i.line} `{i.name}` is {i.external}"
                     + (", its body contains `unsafe`"
                        if _UNSAFE_RE.search(i.body or "") else "")
                     + (f", it asserts {_clauses(i, 'ensures')} about its result"
                        if _clauses(i, "ensures") else "")
                     + f", and it has **no `requires`**. It is "
                     f"therefore an axiom that the unchecked operation is "
                     f"always defined"
                     + f". Give it the precondition its callers must discharge, "
                       f"or declare "
                       f"verus.unsafe_justifications[{src!r}][{i.name!r}] in "
                       f"spec.md -- which the gate then prints in every "
                       f"verdict.")
        else:
            rep.shout("tcb-unsafe",
                      f"{src}:{i.line} `{i.name}` is a trusted item "
                      f"with NO precondition. spec.md justifies it: {why}")


def _check_axiom_decls(rep, src, txt, vcfg):
    """Body-less TRUSTED declarations: count them, print them, and require the
    count to be DECLARED. Returns the list, for the gate record.

    **RECAP "Owed" 0 / TASK_081_REVIEW blocker 1.** `assume_specification`,
    `axiom fn` and `uninterp spec fn` were invisible to every mechanism here:
    `vparse.parse` drops body-less items and `assume_specification` has no `fn`
    token at all, so the published TCB column (`tcb_items` above), the pinned
    obligation count, the `identity` pin, `check_miri`'s *"NO trusted item, so
    Miri is not required"* and stages 5c / 5c-req / 5c-twin all missed them.
    Demonstrated on p01's real `verus.rs` plus **two deliberately false axioms
    on safe std functions**: `7 verified, 0 errors` (the pinned count, unmoved),
    the same seven item names, `_is_trusted` unchanged, and a byte-identical
    kernel (`md5 e3e4441313c93057730ab568fb000846`).

    **Why this is a declared count and not a prohibition.** The threat model in
    `.memory/02-bench-rules.md` is accident, and the accident here is the tool's
    own help text: Verus prints an `assume_specification` declaration and
    invites you to paste it, and the printed form carries **no `requires` and no
    `ensures`**, so it verifies a 1 MiB out-of-bounds read and a null
    dereference at `4 verified, 0 errors` (`.memory/04-verus.md`, final
    section). An author who writes an axiom and *says so* is doing nothing
    wrong; an author who writes one and does not notice has silently added the
    strongest kind of trusted item there is. So the rule is: declare
    `verus.axioms[<src>]` -- an integer, or the list of names -- and the gate
    prints every one of them in every verdict.

    ⚠ **These are deliberately NOT fed to `_is_trusted`.** 5c-twin would then
    demand a verified twin of an item that has no body to twin, which turns a
    legitimate declaration into an unpassable gate -- exactly the shape
    `MAX_TWIN_JUSTIFICATIONS` was deleted for. Visibility, not prohibition.

    ---- TASK_084 --------------------------------------------------------

    Two more forms and one more FILE SET, all from TASK_083_REVIEW:

      * `#[verifier::external_trait_specification]` (blocker 1) and
        `#[verifier::external_type_specification]` -- the attribute sits on a
        `trait`/`struct`, so `vparse.parse()`'s `fn`-keyed attribute walk could
        not reach it and its method declarations are body-less. 54 uses in the
        pinned vstd. `vparse.axiom_decls` matches them now.
      * `#[verifier::external_fn_specification]` (blocker 2) is **bodied**, so
        it is classified by `vparse.parse()` instead and lands in the `tcb`
        inventory above; it is not double-counted here.
      * ⚠ **`src` MAY NOW BE A FILE OUTSIDE THE PATTERN DIRECTORY** (blocker
        3). `os.listdir` is flat and `_check_axiom_decls` used to run only over
        `verus.obligations`, so an axiom in a `#[path]`-included module was
        invisible -- and every pattern's `verus.rs` `#[path]`-includes
        `common/driver.rs`, which makes it the one vector here whose blast
        radius is all 22 patterns from a single edit.

    **The key convention for a file outside `pdir`, because `verus.axioms` is
    otherwise keyed by a `verus.obligations` source NAME:** the path
    **relative to the repository root**, e.g.

        verus.axioms["common/driver.rs"] = 1

    Chosen over a `pdir`-relative `"../../common/driver.rs"` because that has
    many spellings that normalise to one file (`../..//common/driver.rs`,
    `./../../common/driver.rs`) and because it moves if the pattern dir does. A
    repo-relative key has exactly one spelling -- `os.path.relpath(p, REPO)`,
    which is what `_scan_unsafe_sites` already prints -- and it cannot collide
    with a `verus.obligations` key, since those are bare file names with no
    `/`. The gate prints the exact key in its failure message either way.

    ---- TASK_164 item B: `global` is SEEN here and DECLARED nowhere ---------

    ⚠⚠ **`vparse.axiom_decls` reports `global layout` / `global size_of` since
    TASK_164 (10 of 33 patterns), and they are DELIBERATELY PARTITIONED OUT of
    the `verus.axioms` comparison, the `tcb-axiom` shout and `_axiom_items`.**
    Two reasons, and the first is the one that decides it:

      * **A `global` is NOT an unchecked axiom.** The other five forms are
        trusted because *nothing* checks them. A `global` is const-evaluated by
        rustc: measured at TASK_164 on four probes
        (`.temp/t164/globalprobe/`), a FALSE `global layout S is size == 24` on
        a 6-byte struct and a FALSE `global size_of usize == 4` each give
        `2 verified, 0 errors` **and then** `error[E0080]: evaluation panicked:
        does not have the expected size`, exit 1 -- in a plain verify-only
        `verus_run.py` run, on a never-constructed type, and with
        `--crate-type=lib`. `_verus` already turns `errors == 0 && rc != 0`
        into a stage `5e` FAILURE, so the gate catches a lie here today; and
        `build.py::build_verus` compiles the R5 rung, which is a second net.
        Putting them in the axiom count would say Verus trusts them, and it
        does not have to.
      * **The cost, stated rather than hidden.** `verus.axioms` lives inside
        the `slb-contract` fence, so counting `global` there would demand a
        declaration on 10 patterns -- 10 `contract_sha256` moves, 10 stale
        published tables, a `report.py` per pattern and a SECOND full sweep.
        That is a real repair somebody may still want; it is not this one, and
        the visibility it would add over what lands here is a DECLARED integer
        rather than a RECORDED one.

    ✅ What lands instead: the directives are **printed** on their own line and
    **returned**, so `check_verus_contract` writes them to the gate record's
    `global_decls`, and `vparse.GLOBAL_KINDS` names the partition in one
    place."""
    all_decls = vparse.axiom_decls(txt)
    axioms = [d for d in all_decls if d["kind"] not in vparse.GLOBAL_KINDS]
    globals_ = [d for d in all_decls if d["kind"] in vparse.GLOBAL_KINDS]
    if globals_:
        print(f"    {src}: `global` layout/size_of directives (body-less, "
              f"hand-written, and CONST-EVALUATED BY RUSTC -- a false one gives "
              f"`N verified, 0 errors` and then `error[E0080]`, which stage 5e "
              f"fails on): {len(globals_)}")
        for d in globals_:
            print(f"       {d['kind']:22s} {d['name']:36s} (line {d['line']}, "
                  f"in_verus={d['in_verus']})")
    want = (vcfg.get("axioms") or {}).get(src, 0)
    want_n = len(want) if isinstance(want, (list, tuple)) else int(want)
    print(f"    {src}: body-less trusted declarations "
          f"(`assume_specification` / `axiom fn` / `uninterp spec fn` / "
          f"`external_trait_specification` / `external_type_specification`): "
          f"{len(axioms)} (spec.md declares {want_n})")
    for d in axioms:
        print(f"       {d['kind']:22s} {d['name']:36s} (line {d['line']}, "
              f"in_verus={d['in_verus']})")
    got_names = sorted(d["name"] for d in axioms)
    if isinstance(want, (list, tuple)) and got_names != sorted(want):
        rep.fail("proof-axiom",
                 f"{src}: spec.md declares verus.axioms {sorted(want)} but the "
                 f"source declares {got_names}")
    elif len(axioms) != want_n:
        rep.fail("proof-axiom",
                 f"{src}: {len(axioms)} body-less trusted declaration(s) "
                 f"{[(d['kind'], d['name'], d['line']) for d in axioms]}, but "
                 f"spec.md's verus.axioms declares {want_n}. An "
                 f"`assume_specification` / `axiom fn` / `uninterp spec fn` is "
                 f"an AXIOM about real Rust semantics: Verus does not prove it, "
                 f"it adds NO verified function so the obligation count does not "
                 f"move, it emits no instructions so the `identity` pin does not "
                 f"move, and it carries no `#[verifier::external_body]` so the "
                 f"TCB tally above does not move either. The declaration Verus "
                 f"prints for you to paste has no `requires` and no `ensures`, "
                 f"and pasting it verifies a 1 MiB out-of-bounds read and a null "
                 f"dereference at `4 verified, 0 errors` "
                 f"(`.memory/04-verus.md`). Declare it -- "
                 f"`verus.axioms[{src!r}] = {len(axioms)}` or the list of names "
                 f"-- and count it in this pattern's NOTES.md TCB tally, with "
                 f"the `requires` that makes it bite and a deliberately bad call "
                 f"site proving that it does.")
    if axioms:
        rep.shout("tcb-axiom",
                  f"{src}: {len(axioms)} hand-written axiom(s) "
                  f"{[d['name'] for d in axioms]} that NOTHING checks -- not "
                  f"Verus, not the obligation count, and no gate stage. They "
                  f"are part of this pattern's trusted base and must be in its "
                  f"TCB tally.")
    return axioms, globals_


#: The three keywords the axiom scan below looks for, and the regexes are
#: WORD-ANCHORED where the old `re.escape("assume(")` was not -- promoting a
#: check to a FAIL means a false positive now stops the gate, and
#: `re.escape` would have matched `reassume(`. `\s*\(` also catches
#: `assume (false)`, which the literal spelling missed.
_ASSUME_KEYWORDS = {
    "assume(": r"\bassume\s*\(",
    "admit(": r"\badmit\s*\(",
    "assume_specification": r"\bassume_specification\b",
}

#: ⚠⚠ **The two that can make a proof VACUOUS, and they are the two this stage
#: FAILS on.** `assume_specification` is deliberately NOT here: it is a body-less
#: trusted DECLARATION, `vparse.axiom_decls` sees it, and `_check_axiom_decls`
#: already `rep.fail`s unless `verus.axioms` declares it. Promoting it here as
#: well would double-report one item under two contract keys.
_VACUITY_KEYWORDS = ("assume(", "admit(")


def _assume_keyword_hits(txt):
    """`{keyword: [line, ...]}` over CODE ONLY -- `vparse.blank_noncode` blanks
    comments and string literals first, so `// assume(false)` is not a hit while
    a ghost `proof { assume(false); }` is.

    A **pure function of the text**, which is what lets `check_selftests` drive
    it (`_ASSUME_CASES`) without a pattern, a contract or a Verus run."""
    code = vparse.blank_noncode(txt)
    out = {}
    for kw, rx in _ASSUME_KEYWORDS.items():
        lines = [code.count("\n", 0, m.start()) + 1
                 for m in re.finditer(rx, code)]
        if lines:
            out[kw] = lines
    return out


def _axiom_keyword_scan(rep, src, txt, vcfg):
    """The `assume(` / `admit(` / `assume_specification` keyword scan.

    ⚠ Named `_axiom_keyword_shout` until TASK_151, and renamed because it no
    longer only shouts; `TASK_145_REPORT` §3 and `TASK_149_REPORT` §6 cite the
    old name.

    Split out of `check_verus_contract` at TASK_088 so it can run over
    `#[path]`-included files as well as over `verus.obligations`. It used to run
    over `sorted(pinned_obl)` only, which is `TASK_084_REVIEW` major 1's third
    detector: route C planted `assume(x==0); admit();` in a proof fn of an
    included module and **the axiom stage was silent** -- the plant was caught
    only because it happened to move the obligation count, which a plant in an
    `#[verifier::external]` file would not.

    ⚠⚠⚠ **AND UNTIL TASK_151 IT ONLY SHOUTED, WHICH IS NOT A FAILURE, SO A RUNG
    COULD SHIP A VACUOUS PROOF AND PASS.** Measured on two shipped rows, both
    times by a reviewer planting `assume(false);` at the top of the kernel:

        p32   TASK_145 §3 arm `X4`   verifies  15/0   <- the shipped file's count
        p28   TASK_149 §6 arm `B1`   verifies  23/0   <- the shipped file's count

    **The obligation count is therefore NOT a discriminator** -- both plants
    verify at exactly the pinned number -- the `verus.items` clause pin does not
    move (the clauses are untouched), and the `identity` pin does not move
    either (an `assume` is ghost and emits no instructions). The keyword scan
    was the whole textual trace, and it was advisory.

    ⚠ **This is PROSPECTIVE, and the exposure figure belongs with it: when this
    landed, `assume(` / `admit(` appeared ZERO times in code across all 118
    committed `.rs` files, `common/driver.rs` included.** So there is no shipped
    row this breaks, which is exactly why it owes the must-fire arm in
    `_ASSUME_CASES` rather than a green sweep as its evidence.

    **VISIBILITY, NOT PROHIBITION** -- the same design as `_check_axiom_decls`
    and `_check_included_tcb` immediately below, chosen over a flat ban for the
    reason `check_sanitizers`' docstring gives about a gate that cannot be
    passed honestly. An author who genuinely needs an `assume` declares
    `verus.assumptions[<src>] = <int>` **inside the `slb-contract` block**, so
    the declaration moves `contract_sha256`, `harness/tools/contract_diff.py`
    prints exactly what moved, and `PROTOCOL.md`'s definition-of-done item 6
    already requires them to disclose it. **A one-line diff in review beats a
    line of log nobody reads.**"""
    hits = _assume_keyword_hits(txt)
    for kw, lines in sorted(hits.items()):
        rep.shout("tcb-axiom",
                  f"{src}: {kw} appears {len(lines)}x (line(s) "
                  f"{lines[:8]}{' …' if len(lines) > 8 else ''}) -- must be "
                  f"justified in NOTES.md and counted in this pattern's TCB "
                  f"tally")
    n_vac = sum(len(hits.get(k, [])) for k in _VACUITY_KEYWORDS)
    want = (vcfg.get("assumptions") or {}).get(src, 0)
    try:
        want = int(want)
    except (TypeError, ValueError):
        rep.fail("proof-vacuity",
                 f"{src}: spec.md's `verus.assumptions[{src!r}]` is {want!r}; "
                 f"it must be an integer count of `assume(` + `admit(` "
                 f"occurrences in this file.")
        return hits
    if n_vac != want:
        detail = ", ".join(f"{k} x{len(hits[k])} at line(s) {hits[k][:8]}"
                           for k in _VACUITY_KEYWORDS if k in hits) or "none"
        rep.fail("proof-vacuity",
                 f"{src}: {n_vac} vacuity keyword(s) ({detail}), but spec.md's "
                 f"`verus.assumptions` declares {want}. `assume(` and `admit(` "
                 f"DISCHARGE A PROOF OBLIGATION WITHOUT PROVING IT, so one of "
                 f"them can make a whole rung's proof true of the empty "
                 f"program while every other stage stays green: `assume(false)` "
                 f"at the top of the kernel verifies at the SAME "
                 f"`N verified, 0 errors` as the shipped file -- p32 15/0 "
                 f"(TASK_145 arm X4), p28 23/0 (TASK_149 B1) -- so the "
                 f"obligation count cannot tell them apart, the `verus.items` "
                 f"clause pin does not move, and the `identity` pin does not "
                 f"move because ghost code emits no instructions. Until "
                 f"TASK_151 this stage only `rep.shout`ed, and a shout is not a "
                 f"failure. If the assumption is deliberate, DECLARE it -- "
                 f"`verus.assumptions[{src!r}] = {n_vac}` inside the "
                 f"`slb-contract` block, which moves `contract_sha256` and so "
                 f"makes it a one-line diff a reviewer sees -- and count it in "
                 f"this pattern's NOTES.md TCB tally with the argument for why "
                 f"the assumed proposition is true of real Rust. Exposure when "
                 f"this check landed was ZERO across all 118 committed `.rs` "
                 f"files.")
    elif n_vac:
        rep.shout("tcb-axiom",
                  f"{src}: {n_vac} DECLARED `assume(`/`admit(` "
                  f"(`verus.assumptions` = {want}). Verus proves NOTHING about "
                  f"these: they are hand-written axioms in this pattern's "
                  f"trusted base and every claim downstream of them is "
                  f"conditional on them.")
    return hits


def _ak(text, declared=None):
    """One `_ASSUME_CASES` cell: `[fails, shouts]` from `_axiom_keyword_scan`.

    ⚠ **An exception becomes a THREE-element list**, which can never equal a
    two-element expectation, so a broken detector REPORTS at stage 0 instead of
    killing the import. `.memory/03-measurement.md` entry 19: three of `p32`'s
    four planted mutations failed by crashing and the diagnostic was lost."""
    src = "verus.rs"
    rep = _StubReport()
    vcfg = {} if declared is None else {"assumptions": {src: declared}}
    try:
        _axiom_keyword_scan(rep, src, text, vcfg)
    except Exception as e:                                       # noqa: BLE001
        return ["RAISED", type(e).__name__, str(e)[:120]]
    return [rep.n["fail"], rep.n["shout"]]


#: ⚠⚠ **THE MUST-FIRE ARM FOR THE VACUITY CHECK (TASK_151), and it exists
#: because the repair is PROSPECTIVE: exposure across the shipped tree is ZERO,
#: so a green sweep is not evidence that this can fire at all.** Seven cells,
#: covering both guards -- the KEYWORD SCAN (does it see code, and only code?)
#: and the DECLARATION COMPARISON (does a mismatch fail, and a match not?).
#: Run by `check_selftests` at stage 0 on **every** gate invocation, which is
#: the shape `TASK_147`'s `detector_selftest()` established.
_ASSUME_CASES = [
    # --- guard 1: the keyword scan -------------------------------------------
    ("an undeclared `assume(` in code FAILS", _ak("proof { assume(false); }"),
     [1, 1]),
    ("an undeclared `admit(` in code FAILS", _ak("proof fn p() { admit(); }"),
     [1, 1]),
    # The blanking half. Every hardened C rung and half the `.rs` doc comments
    # in this repo mention `assume`; if comments were hits the gate would be
    # unpassable, and TASK_151 measured 3 `.rs` files that name
    # `assume_specification` in a comment alone.
    ("`assume(` in a COMMENT is not a hit", _ak("// proof { assume(false); }\n"),
     [0, 0]),
    ("`assume(` in a STRING literal is not a hit",
     _ak('let s = "assume(false)";'), [0, 0]),
    # `reassume(` is why the regex is `\b`-anchored rather than `re.escape`.
    ("a keyword that merely ENDS in `assume(` is not a hit",
     _ak("let x = reassume(y);"), [0, 0]),
    # --- guard 2: the declaration comparison ---------------------------------
    ("a DECLARED `assume(` passes and shouts twice",
     _ak("proof { assume(false); }", declared=1), [0, 2]),
    ("declaring MORE than the file spells also FAILS",
     _ak("proof fn p() { }", declared=1), [1, 0]),
    # --- and the boundary: `assume_specification` has its OWN key -------------
    ("`assume_specification` shouts but does NOT fail here "
     "(`verus.axioms` owns it)",
     _ak("assume_specification[ core::mem::swap ](a, b);"), [0, 1]),
    ("a clean file is silent", _ak("fn main() { }"), [0, 0]),
]


def _check_included_tcb(rep, src, txt, vcfg):
    """BODIED trusted items in a `#[path]`-included file: inventory them, print
    them, and require the count to be DECLARED. Returns the list.

    **`TASK_084_REVIEW` major 1, the second of the three detectors the `#[path]`
    walk did not feed, and the one with the measured exploit.** The TCB
    inventory inside `check_verus_contract` is
    `tcb = [i for i in item_list if i.external]` over `verus.obligations` only,
    so route J -- a real
    `#[verifier::external_body] fn r84_lie(x: u64) -> (r: u64) ensures r == 0`
    in a `#[path]`-included module -- shipped **fully green with no gate output
    at all**: `grep -c r84_lie gate.log` was **0**, the verdict said *"3 TCB
    items"*, and `results/synthesis.md` regenerated **byte-identical**.

    ✅ **What bounds the vector, and it is why this is about `ensures` rather
    than about `unsafe`:** an `unsafe` token in an included module IS caught,
    by `_scan_unsafe_sites`, which has walked `_path_includes` since TASK_069
    (route I: `[tcb-unsafe] .temp/r84/plant/ax_mod.rs:9`). What was left was
    **false claims about SAFE operations** -- exactly the threat
    `_check_axiom_decls`' own docstring names.

    **Visibility, not prohibition**, the same design as `_check_axiom_decls`
    and for the same reason: declaring the item is not the wrong thing to do,
    not noticing it is. Declare `verus.included_tcb[<repo-relative path>]` --
    an integer or the list of names -- and every verdict prints them.

    ⚠ **A separate key from `verus.axioms` on purpose.** These items are
    **bodied**, so `vparse.parse` classifies them and `vparse.axiom_decls`
    deliberately does not; putting them in one key would make the declared count
    unreadable and would double-count an `external_fn_specification`, which is
    bodied and reaches both. Nothing in the tree declares either today: the only
    `#[path]`-included file any pattern has is `common/driver.rs`, which carries
    no `external` item, so this stage is measured inert across all 23."""
    try:
        items = vparse.parse(txt)
    except ValueError as e:
        rep.fail("tcb-included", f"{src}: {e}")
        return []
    tcb = [i for i in items if i.external]
    want = (vcfg.get("included_tcb") or {}).get(src, 0)
    want_n = len(want) if isinstance(want, (list, tuple)) else int(want)
    print(f"    {src}: bodied trusted items in a `#[path]`-included file "
          f"(`external_body` / `external_fn_specification`): {len(tcb)} "
          f"(spec.md declares {want_n})")
    for i in tcb:
        print(f"       {i.external:32s} {i.name:16s} "
              f"({i.body_lines} body lines, line {i.line}, "
              f"ensures={_clauses(i, 'ensures') or '[]'})")
    got_names = sorted(i.name for i in tcb)
    if isinstance(want, (list, tuple)) and got_names != sorted(want):
        rep.fail("tcb-included",
                 f"{src}: spec.md declares verus.included_tcb {sorted(want)} "
                 f"but the file declares {got_names}")
    elif len(tcb) != want_n:
        rep.fail("tcb-included",
                 f"{src}: {len(tcb)} bodied trusted item(s) "
                 f"{[(i.external, i.name, i.line) for i in tcb]} in a file the "
                 f"rungs `#[path]`-include, but spec.md's verus.included_tcb "
                 f"declares {want_n}. An `#[verifier::external_body]` here is "
                 f"in this pattern's trusted base exactly as one in verus.rs "
                 f"is -- Verus takes its `ensures` on trust and the binary "
                 f"executes its body -- but until TASK_088 no stage looked: the "
                 f"TCB inventory, `_trusted_items` and the `assume(`/`admit(` "
                 f"shout all ran over `verus.obligations` alone, so a planted "
                 f"`ensures r == 0` shipped green with `grep -c <name> "
                 f"gate.log` == 0 and a byte-identical synthesis.md "
                 f"(TASK_084_REVIEW major 1, route J). Declare it -- "
                 f"`verus.included_tcb[{src!r}] = {len(tcb)}` or the list of "
                 f"names -- and count it in this pattern's NOTES.md TCB tally "
                 f"with the argument for why its `ensures` matches real Rust "
                 f"semantics.")
    if tcb:
        rep.shout("tcb-included",
                  f"{src}: {len(tcb)} bodied trusted item(s) {got_names} in a "
                  f"`#[path]`-included file. Their `ensures` are HAND-WRITTEN "
                  f"claims Verus never proves, and this file is shared -- an "
                  f"item here is in EVERY pattern that includes it.")
    return [dict(name=i.name, attr=i.external, body_lines=i.body_lines,
                 line=i.line) for i in tcb]


def check_verus_contract(pdir, rep, contract):
    """B1 + B2: obligation count, item set, and every `requires`/`ensures`
    diffed against the pin in spec.md.

    This is the only mechanical defence against the two failure modes that
    produce `N verified, 0 errors` regardless:
      * a tautological `ensures` (`r == r`) -- same count, no diagnostic;
      * a `requires` deleted from an `external_body` wrapper -- same count, no
        diagnostic, and every caller's obligation silently gone
        (`.memory/04-verus.md`)."""
    head("5a. the Verus contract matches the pin in spec.md")
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    pinned_items = vcfg.get("items") or {}
    justif = vcfg.get("unsafe_justifications") or {}
    if not pinned_obl or not pinned_items:
        rep.fail("proof-pin", "spec.md pins no `verus.obligations` / "
                              "`verus.items` -- TASK_003 B1/B2 require both")
        return {}
    # The pinned file list is author-chosen, so dropping an entry un-checks a
    # whole source. Every file in the pattern that opens a `verus!` block must
    # be in it.
    #
    # This used to be `re.search(r"\bverus!\s*\{")` while `vparse.verus_span`
    # accepted `verus!\s*[{(\[]`, and the one-character gap between the two was
    # TASK_006_REVIEW's blocker A. It is written in terms of `verus_span` now so
    # the two cannot disagree -- but note that is *hygiene, not the fix*: a
    # third regex is what was defeated. The fix is `_verus_verified_files`,
    # which asks Verus.
    _scan_unsafe_sites(rep, pdir, contract)
    # ...and the one thing `_path_includes` cannot resolve for it (TASK_099).
    _check_opaque_includes(rep, pdir, contract)
    for f in sorted(os.listdir(pdir)):
        if f.endswith(".rs") and vparse.verus_span(open(os.path.join(pdir, f)).read()):
            if f not in pinned_obl:
                rep.fail("proof-pin", f"{f} contains a `verus!` block but is not "
                                      f"in spec.md's verus.obligations -- an "
                                      f"author-chosen file list un-checks a "
                                      f"source by omission")
    out = {}
    for src, want_n in sorted(pinned_obl.items()):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            rep.fail("proof-pin", f"{src} pinned in spec.md but not in the tree")
            continue
        txt = open(path).read()
        item_list = vparse.parse(txt)

        # --- one item per SCOPED name (TASK_003_REVIEW: last wins) ---------
        # ⚠ Keyed by (mod path, impl Self type, name) since TASK_077, not by
        # bare name (RECAP "Owed" 20). Keying by bare name made a pinned
        # `verus.rs` unable to define one name twice, so p36's eight
        # `impl Op for OpN` blocks -- which verified `19/0` -- were refused by
        # the gate and it shipped one generic impl instead
        # (`patterns/p36-vtable-dispatch/NOTES.md` 9b).
        #
        # The decoy this check exists to stop is stopped by TWO things now, and
        # the second is what makes widening the first safe:
        #
        #   * a duplicate that no scope distinguishes still fails HERE (two
        #     `fn kernel` in one module is still `defined 2x`);
        #   * a duplicate that a scope DOES distinguish gets two distinct
        #     labels from `vparse.unique_names`, and the pinned item-set check
        #     20 lines below then fails with `added=['decoy::kernel']`. That
        #     pin is inside `contract_sha256`, so admitting the eight-impl
        #     spelling costs the pattern an explicit, hashed declaration of
        #     every qualified name -- which is the honest price and the reason
        #     "Owed" 20 was never a one-liner.
        #
        # `unique_names` degrades to the bare name wherever it is unambiguous,
        # so every `verus.rs` in the tree today keys exactly as it did before
        # and no `spec.md` item pin moves.
        #
        # ⚠ **AND THE EIGHT-IMPL SPELLING STILL DOES NOT SHIP -- THIS STAGE
        # ADMITS IT AND FIVE OTHERS REFUSE IT** (TASK_077_REVIEW B1, measured
        # again at TASK_078). `vparse.by_name` is bare-keyed on purpose and is
        # called by `check_call_site`, `check_clause_deletion`,
        # `check_requires_strength`, `check_trusted_twins` and
        # `derive_contract`, plus `harness/limbs.py`; each turns its
        # `ValueError` into a failure reading *"duplicate item name(s):
        # apply"*. So do NOT read the sentence below as "write eight impls and
        # the gate is happy": it is not, and RECAP "Owed" 20 is NARROWED, not
        # closed. The remaining work is in `vparse.by_name`'s docstring.
        dup = vparse.duplicate_names(item_list, qualified=True)
        if dup:
            for nm, its in sorted(dup.items()):
                rep.fail("proof-pin",
                         f"{src}: `{nm}` is defined {len(its)}x (lines "
                         f"{[i.line for i in its]}) with nothing to tell them "
                         f"apart -- same module, same impl. The gate used to "
                         f"key items by name and keep the last, so a decoy "
                         f"could supply the pinned contract for the real item "
                         f"-- and nothing says the compiler keeps the same "
                         f"one. Two items in DIFFERENT impls or modules are "
                         f"fine and get qualified names.")
            continue
        try:
            items = vparse.unique_names(item_list)
        except ValueError as e:
            rep.fail("proof-pin", f"{src}: {e}")
            continue

        # --- item set -----------------------------------------------------
        want_items = pinned_items.get(src)
        if want_items is None:
            rep.fail("proof-pin", f"{src}: no item pin in spec.md")
            continue
        got, want = set(items), set(want_items)
        # Per-source drift counter for the `ok` line at the bottom, which used
        # to assert "all contracts identical to spec.md" without being gated on
        # the per-item failures raised 60 lines below (TASK_053 m2). It can only
        # lie on a run that is already FAIL, which is why it is a minor -- but
        # the two `ok` strings this project has already been burnt by were
        # dangerous precisely because they lied.
        drifted = 0
        if got != want:
            drifted += 1
            rep.fail("proof-pin", f"{src}: item set differs from spec.md; "
                                  f"added={sorted(got - want)} "
                                  f"removed={sorted(want - got)}")
        # --- per-item attributes and clauses ------------------------------
        for name in sorted(want & got):
            w, it = want_items[name], items[name]
            diffs = []
            # A pinned item must be the one Verus actually verifies: inside
            # `verus!`, and not hidden behind a `#[cfg]` that may exclude it
            # from the build entirely.
            if not it.in_verus:
                diffs.append("outside `verus! {}` -- Verus never sees it, so "
                             "its pinned contract constrains nothing")
            # A verified twin (stage 5c-twin) is *required* to be cfg'd out of
            # every build -- that is what makes it cost zero instructions
            # structurally. 5c-twin checks the exact cfg spelling and that the
            # twin's signature is the trusted item's, so the item it stands
            # beside is not left unpinned.
            if it.cfg_gated and not name.startswith(TWIN_PREFIX):
                diffs.append(f"gated by {it.cfg_gated} -- it may not be in the "
                             f"build at all, while the item that is goes "
                             f"unpinned")
            elif it.cfg_gated and it.cfg_gated != "own #[cfg(...)]":
                diffs.append(f"is a verified twin but is gated by "
                             f"{it.cfg_gated} rather than by its own "
                             f"#[cfg({TWIN_CFG})]")
            if (it.external or None) != (w.get("external") or None):
                diffs.append(f"external: {it.external!r} != {w.get('external')!r}")
            for kw in ("requires", "ensures"):
                gotc = _clauses(it, kw)
                wantc = [vparse.norm_clause(c) for c in w.get(kw, [])]
                if gotc != wantc:
                    diffs.append(f"{kw}: {gotc!r} != pinned {wantc!r}")
            if diffs:
                drifted += 1
                rep.fail("proof-pin", f"{src}:{it.line} `{name}` drifted from "
                                      f"spec.md -- " + "; ".join(diffs))

        # --- TCB inventory, from the fixed parser -------------------------
        tcb = [i for i in item_list if i.external]
        print(f"    {src}: TCB items ({len(tcb)}):")
        for i in tcb:
            print(f"       {i.external:32s} {i.name:16s} "
                  f"({i.body_lines} body lines, line {i.line}, "
                  f"requires={_clauses(i, 'requires') or '[]'})")
        _check_trusted_unsafe(rep, src, tcb, justif.get(src) or {})
        # TASK_084 / TASK_083_REVIEW blocker 2. An
        # `#[verifier::external_fn_specification]` now reaches the inventory
        # above (`vparse.parse` recognises the attribute), which is what makes
        # the `verus.items` pin able to tell it from an ordinary verified
        # function and what moves the published TCB column. But it is NOT
        # `_is_trusted` -- there is no checked stand-in for a std function, so
        # demanding a twin would make a legal declaration unpassable -- and so
        # `_check_trusted_unsafe` above says nothing about it. Without this
        # line the loudest of the four routes would be the only one with no
        # sentence in the verdict.
        for i in tcb:
            if not (i.external or "").endswith("_specification"):
                continue
            rep.shout("tcb-axiom",
                      f"{src}:{i.line} `{i.name}` is {i.external} -- its "
                      f"`ensures` {_clauses(i, 'ensures') or '[]'} is a "
                      f"HAND-WRITTEN claim about a function Verus never "
                      f"compiles, and Verus's own error message for a "
                      f"malformed one calls it an `assume_specification`. It "
                      f"is in the TCB inventory above and must be in this "
                      f"pattern's NOTES.md TCB tally with the argument for "
                      f"why the clause matches real Rust semantics.")
        print(f"    {src}: items the trusted-item rules govern (`_is_trusted`: "
              f"external_body + an `ensures`, or `unsafe` in the body): "
              f"{sorted(i.name for i in item_list if _is_trusted(i))}")
        # `rep.note` until TASK_082, i.e. informational and gone by the time the
        # verdict is read. RECAP "Owed" 0: these three keywords are the whole
        # textual trace the gate had of an axiom, and an axiom is the one shape
        # that can verify a false program at an unmoved obligation count.
        # TASK_088 moved the body into `_axiom_keyword_shout` so the
        # `#[path]`-included files get it too (TASK_084_REVIEW major 1, route C).
        # ⚠ TASK_151 renamed it `_axiom_keyword_scan` and made `assume(` /
        # `admit(` a FAILURE unless `verus.assumptions` declares them: a shout
        # is not a failure, and `assume(false)` verifies at the shipped file's
        # own obligation count (p32 15/0, p28 23/0).
        _axiom_keyword_scan(rep, src, txt, vcfg)
        axioms, gdecls = _check_axiom_decls(rep, src, txt, vcfg)

        # --- obligation count --------------------------------------------
        #
        # ⚠ **`_verus`, not a fourth inline copy of it.** This was a
        # byte-for-byte duplicate of `check.py::_verus`'s body -- same command,
        # same regex, same `cwd`, same timeout -- and it inherited the same
        # defect: it never read `subprocess.CompletedProcess.returncode`, so a
        # `verus.rs` that Verus verifies and rustc rejects was recorded here as
        # `N verified, 0 errors` and printed an `ok` line (TASK_096_REVIEW
        # MAJOR 2, which named this as "the primary certificate site" -- it is
        # the run that fills every gate record's `verified`, `errors` and
        # `tcb_items`). Calling `_verus` fixes it and deletes the duplicate in
        # one edit; `_verus` is defined below this function, which is fine
        # because Python resolves globals at call time.
        #
        # This site *is* backstopped -- `build.py::build_verus` passes
        # `--compile` and does check `rc`, and every pinned obligation source
        # is a built cell -- but the backstop is stage `[build]`, which
        # `--no-build` skips, and a diagnostic that points at the wrong stage
        # is how the finding stayed invisible for 96 tasks.
        n_ver, n_err, res = _verus(path)
        if n_ver is None:
            rep.fail("proof-verify", f"{src}: no verification result: {res[-500:]}")
            continue
        out[src] = {"verified": n_ver, "errors": n_err, "pinned": want_n,
                    "tcb_items": [dict(name=i.name, attr=i.external,
                                       body_lines=i.body_lines, line=i.line)
                                  for i in tcb],
                    "axiom_decls": axioms,
                    # TASK_164 item B. A SEPARATE key, not folded into
                    # `axiom_decls`: `results/synthesis.md`'s section-3 "axioms"
                    # column is `len(axiom_decls)` and its prose says a `0`
                    # means "this pattern's author wrote no axiom of their
                    # own". A `global` is rustc-checked, so putting it there
                    # would move a published column and make it say something
                    # else. Count either without re-deriving the census:
                    # `vparse.GLOBAL_KINDS` carries the `kind` spellings.
                    "global_decls": gdecls}
        if n_err:
            rep.fail("proof-verify", f"{src}: {n_ver} verified, {n_err} errors")
        elif n_ver != want_n:
            rep.fail("proof-obligations",
                     f"{src}: {n_ver} verified, spec.md pins {want_n}. This "
                     f"count is one Verus query per function plus one per loop "
                     f"body (derived at TASK_003_REVIEW), i.e. a checksum over "
                     f"the function/loop *skeleton*. A drop usually means an "
                     f"item stopped being verified -- an `external_body` on a "
                     f"driver does exactly this -- but a benign refactor that "
                     f"adds or removes a function or a loop moves it too. "
                     f"Diagnose with `verus_run.py {src} --verify-function "
                     f"<name> --verify-root` per item before re-pinning; the "
                     f"count is *not* sensitive to any semantic weakening, so "
                     f"an unchanged count is not evidence of anything.")
        elif drifted:
            print(f"    {src}: {n_ver} verified, 0 errors -- matches the pinned "
                  f"obligation count, but {drifted} pinned item(s) drifted "
                  f"above, so no `ok` line is printed for this source")
        else:
            rep.ok(f"{src}: {n_ver} verified, 0 errors -- matches the pinned "
                   f"obligation count; {len(tcb)} TCB items, all contracts "
                   f"identical to spec.md")

    # --- and the files the rungs `#[path]`-include, which are NOT in pdir ---
    #
    # TASK_083_REVIEW blocker 3. `os.listdir(pdir)` above is FLAT and the loop
    # that just ended runs only over `verus.obligations`, so an axiom one
    # directory down -- or in the shared `common/driver.rs` that every pattern's
    # `verus.rs` `#[path]`-includes -- was invisible to the stage built for it.
    # Demonstrated at `.temp/t84/probe/p_hidden.rs`: an `assume_specification`
    # in `macro/ax_mod.rs` proves `x.count_ones() == 0` at `2 verified, 0
    # errors` while the program prints `3`, and `axiom_decls` on the top file
    # returns `[]`.
    #
    # `_scan_unsafe_sites` already walks exactly this file list for exactly this
    # threat (`_path_includes`); the two stages had the same threat and
    # different file lists. This is that walk, and the key convention for
    # declaring one of these is in `_check_axiom_decls`' docstring: the path
    # relative to the REPO root.
    #
    # ⚠ **TASK_088: this loop now feeds ALL THREE detectors, not one.**
    # `TASK_084_REVIEW` major 1 measured the other two missing, on real gate
    # runs: the bodied TCB inventory (route J -- an `external_body` with
    # `ensures r == 0`, green, `grep -c` == 0, byte-identical `synthesis.md`)
    # and the `assume(`/`admit(` keyword shout (route C -- silent). The file
    # list is `_verus_file_list`, which is also DEDUPED, so an include that
    # resolves back inside `pdir` no longer arrives under two keys
    # (`TASK_084_REVIEW` minor 5).
    included = [(k, p) for k, p in _verus_file_list(pdir, sorted(pinned_obl))
                if k not in pinned_obl]
    if included:
        print(f"    scanned `#[path]`-included files for hand-written axioms, "
              f"bodied trusted items and assume/admit: {[k for k, _ in included]}")
    for rel, p in included:
        txt = open(p).read()
        ax, gd = _check_axiom_decls(rep, rel, txt, vcfg)
        itcb = _check_included_tcb(rep, rel, txt, vcfg)
        _axiom_keyword_scan(rep, rel, txt, vcfg)
        if ax or itcb or gd:
            out[rel] = {"path_included": True, "axiom_decls": ax,
                        "global_decls": gd, "tcb_items": itcb}
    return out


def check_call_site(pdir, rep, contract):
    """Rule 2, asked of Verus rather than of a regex.

    `--verify-function <name> --verify-root` reports how many obligations that
    *one* function contributed. An `#[verifier::external_body] fn main` reports
    `0 verified` -- there is no body to verify, so no call inside it discharges
    anything. That is the pilot's defect, detected semantically."""
    head("5b. rule 2: Verus confirms the call site is a verified call site")
    vcfg = contract.get("verus") or {}
    site = vcfg.get("call_site", "main")
    kname = vcfg.get("kernel_item", "kernel")
    src = os.path.join(pdir, "verus.rs")
    if not os.path.exists(src):
        rep.fail("proof-rule2", "no verus.rs")
        return {}
    try:
        items = vparse.by_name(open(src).read())
    except ValueError as e:
        rep.fail("proof-rule2", str(e))
        return {}
    out = {}

    it = items.get(site)
    if it is None:
        rep.fail("proof-rule2", f"verus.rs has no `fn {site}`")
    else:
        if not it.in_verus:
            rep.fail("proof-rule2", f"`fn {site}` is outside `verus! {{}}` -- the "
                                    f"kernel call site is unverified (the pilot's bug)")
        if it.external:
            rep.fail("proof-rule2", f"`fn {site}` is {it.external} -- no "
                                    f"precondition is ever discharged")
        if not it.calls(kname):
            rep.fail("proof-rule2", f"`fn {site}` contains no call to {kname}() "
                                    f"(comments and string literals do not count)")

    for name in (site, kname):
        mp = (items.get(name).mod_path or "") if items.get(name) else ""
        nv, ne, res, resolved, ambiguous = _verify_function(src, name, mp)
        n = nv or 0
        out[name] = n
        if not resolved:
            rep.fail("proof-rule2",
                     f"Verus could not RESOLVE `{name}` for "
                     f"`--verify-function` (module {mp!r}) -- that is 'the gate "
                     f"could not ask the question', not 'the item has no "
                     f"verified body' (TASK_008_REVIEW major E).\n"
                     f"      {(res or '')[-300:]}")
        elif ambiguous:
            # TASK_078 / TASK_077_REVIEW M5. Verus's third answer. Without this
            # arm the `elif` below reports `0 verified` -- "Verus has no
            # verified body for `{name}`" -- about a query Verus refused to
            # answer. That is major E's false diagnosis, one answer over.
            rep.fail("proof-rule2",
                     f"`--verify-function {name}` is AMBIGUOUS: Verus matches "
                     f"by substring over the qualified path and more than one "
                     f"item matched, so it refused to pick and verified "
                     f"nothing. This is 'the gate could not ask the question' "
                     f"again -- NOT 'the item has no verified body'. Give "
                     f"spec.md's `verus.{'call_site' if name == site else 'kernel_item'}` "
                     f"a name that identifies one item (a `Type::name` "
                     f"qualification, or a name that is not a proper substring "
                     f"of another item's).\n      {(res or '')[-300:]}")
        elif nv is None or ne or n < 1:
            rep.fail("proof-rule2",
                     f"`verus --verify-function {name}` reports {n} verified: "
                     f"Verus has no verified body for `{name}`. If it is "
                     f"`external_body`, every obligation inside it -- including "
                     f"the kernel's `requires` at the call site -- is discarded "
                     f"(`.memory/02-bench-rules.md` rule 2).\n      {res[-300:]}")
        else:
            rep.ok(f"verus --verify-function {name}: {n} verified -- `{name}` "
                   f"has a real verified body")
    return out


#: Every `_verus` run whose SUMMARY said "0 errors" and whose PROCESS said
#: otherwise. Module-level rather than threaded through eleven call sites
#: because three of them (`_verify_function`, `_run_taut_battery`,
#: `_probe_selftest`) have no `rep` to fail on, and because
#: `check_verus_exit_codes` must be able to fail the run even if some future
#: caller swallows the `(None, None, ...)` this makes `_verus` return.
_VERUS_RC_ANOMALIES = []


def _verus(path, *extra):
    """(verified, errors, raw output). `(None, None, out)` if Verus said neither.

    ⚠⚠ **THE RETURN CODE IS PART OF THE ANSWER, AND THIS FUNCTION DISCARDED IT
    UNTIL TASK_097** (TASK_096_REVIEW MAJOR 2/3, manager-verified end to end).
    `verus_run.py` prints Verus's `N verified, M errors` summary and *then*
    lets rustc finish the compilation. Verus can be entirely satisfied while
    rustc rejects the file, and the canonical instance is the one the gate's
    own rules produce:

        #[cfg(slb_twin)] fn slb_twin_read_i(v: Slot) -> u64
            requires v is i, { v.i }

    Verus makes the correct-variant obligation first class and discharges it
    from `requires v is i` -- `2 verified, 0 errors` -- while rustc emits
    `error[E0133]: access to union field is unsafe` and `verus_run.py` exits
    **1**. Reading only the summary, stage 5c-twin then printed *"`slb_twin_x`
    verifies against `x`'s own contract"* and *"13 verified, 0 errors with
    `--cfg slb_twin` -- matches the pinned verus.twin_obligations"* **about
    source that does not compile** (`.temp/t96/a3_gate_comply.log:424-425`, a
    real gate run). `--cfg slb_twin` is compiled by nothing else, so the twin
    oracle is the unbackstopped one.

    ⚠ **A BARE RETURNCODE CHECK WOULD BE WORSE THAN THE HOLE.** Of the eleven
    `_verus` call sites, **five are mutants that MUST exit non-zero** -- the
    `assert(false)` reachability probe and the three deletion loops -- and
    failing them on `rc != 0` turns the whole mutant battery green for the
    wrong reason. That is the tautology trap, which this project has now hit
    four times. So the condition is the narrow one:

        the summary PARSED  and  errors == 0  and  returncode != 0

    which no mutant site can reach, because `errors == 0` at a mutant site is
    already a `rep.fail`. The answer is then downgraded to "Verus said
    neither", which every call site already treats as a failure, and the reason
    is APPENDED to the output (not prepended -- callers print `out[-300:]`) so
    the tail a failure message quotes carries it. `check_verus_exit_codes`
    turns the recorded anomalies into a named stage failure as well, so the
    diagnostic points at the right thing rather than at "no verification
    result"."""
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path,
                        *extra], capture_output=True, text=True, cwd=REPO,
                       timeout=RUN_TIMEOUT)
    res = (r.stdout + r.stderr).strip()
    m = re.search(r"(\d+) verified, (\d+) errors", res)
    if not m:
        return None, None, res
    nv, ne = int(m.group(1)), int(m.group(2))
    if ne == 0 and r.returncode != 0:
        _VERUS_RC_ANOMALIES.append(
            {"file": os.path.relpath(path, REPO), "flags": list(extra),
             "verified": nv, "errors": ne, "returncode": r.returncode,
             "output_tail": res[-800:]})
        return None, None, res + (
            f"\n\n      [check.py::_verus] SUMMARY SUPPRESSED: verus_run.py "
            f"exited {r.returncode} while reporting `{nv} verified, 0 errors` "
            f"for {os.path.relpath(path, REPO)} {list(extra)}. Verus was "
            f"satisfied and the COMPILER was not, so the summary is not a "
            f"certificate: this file does not build. Look for a rustc error "
            f"above (`error[E0133]` is the one the twin rules produce, because "
            f"`_TWIN_BANNED` forbids the `unsafe` keyword in a twin and some "
            f"operations have no safe spelling).")
    return nv, ne, res


def check_verus_exit_codes(rep):
    """Stage 5e. Did any Verus run this gate believed exit non-zero?

    `_verus` already downgrades such a run to `(None, None, ...)`, and every
    call site treats that as a failure -- but "every call site" is a claim
    about eleven call sites, and one of them (`_run_taut_battery`, when a
    tactic is named) deliberately reads `(None, None)` as *"the tactic could
    not be applied"* and `continue`s. That arm is correct for what it was
    written for (`by (bit_vector)` aborts on any clause mentioning a slice
    length -- TASK_053 F2, 51 of 52 conjuncts) and it would swallow this.

    So the anomaly is ALSO recorded module-side and failed here, where no
    caller's local interpretation can absorb it. Fires at `n > 0` only; at
    `n == 0` it prints nothing, because an `ok` line asserting a property over
    an empty set is the shape `.memory/02-bench-rules.md` forbids."""
    if not _VERUS_RC_ANOMALIES:
        return []
    head("5e. every Verus run's EXIT CODE, not just its summary")
    for a in _VERUS_RC_ANOMALIES:
        rep.fail("verus-exit",
                 f"{a['file']} {a['flags']}: verus_run.py exited "
                 f"{a['returncode']} while reporting `{a['verified']} "
                 f"verified, 0 errors`. Verus discharged every obligation and "
                 f"the COMPILER REJECTED THE FILE, so the summary certifies "
                 f"nothing -- there is no binary and, for a `--cfg "
                 f"{TWIN_CFG}` run, nothing else in the gate compiles that "
                 f"configuration. On the run that found this the gate printed "
                 f"`13 verified, 0 errors with --cfg {TWIN_CFG} -- matches the "
                 f"pinned verus.twin_obligations` about source rustc refuses "
                 f"(TASK_096_REVIEW MAJOR 2/3).\n      {a['output_tail'][-700:]}")
    return list(_VERUS_RC_ANOMALIES)


_UNRESOLVED_RE = re.compile(
    r"could not find function .*specified by --verify-function")

# TASK_078, from TASK_077_REVIEW M5. Verus's THIRD answer.
_AMBIGUOUS_RE = re.compile(
    r"more than one match found for --verify-function")


def _verify_function(path, name, mod_path=""):
    """(verified, errors, output, resolved, ambiguous) for one item, asked of
    Verus.

    **THREE answers, not two, and the third was measured in the same commit
    that failed to add it** (TASK_077, caught by TASK_077_REVIEW M5).

    1. **verified** -- `N verified, M errors`.
    2. **unnameable** (TASK_008_REVIEW, major E). `--verify-root` restricts the
       query to the crate root, so a function inside a `mod` is not *unverified*
       -- Verus replies *"could not find function drive specified by
       --verify-function; available functions are: - main"*, `_verus` returns
       `(None, None)`, and the caller reported "the item enclosing the region
       has no verified body", which is false. The file verifies 2/0.
       `--verify-only-module <mod> --verify-function <name>` is the query that
       does resolve it (measured: `1 verified, 0 errors`), so a mod-nested item
       is asked properly instead of being misdiagnosed.
    3. **ambiguous by SUBSTRING.** Verus matches `--verify-function` against a
       substring of the qualified path and refuses to pick:

           error: more than one match found for --verify-function apply,
                  consider using wildcard *apply* to verify all matched
                  results, or specify a unique substring for the desired
                  function, matched results are:
                    - A::apply    - A::spec_apply

       ⚠ **This fires on a file with NO duplicate item name at all** --
       measured at the pinned Verus on one `impl A` defining `apply` and
       `spec_apply` (`.temp/p78/vprobe/subambig.log`, TASK_078). So
       `vparse.duplicate_names(qualified=True)` is not a guard for it: `apply`
       and `spec_apply` are two different names, and one contains the other.
       Without this branch `_verus` returns `(None, None)`, `_UNRESOLVED_RE`
       does not match, `resolved` comes back **True**, and the caller prints
       *"Verus resolved the item and has no verified body for it"* -- major E's
       false diagnosis exactly, one answer over.

       Latent today: the label handed to `--verify-function` is `main` on 23 of
       23 verus-bearing files. But **22 of 22 `verus.rs` files already carry a
       substring-ambiguous name pair** -- every `slb_twin_*`/base pair, plus
       `shift_round`/`shift_rounds` (p08), `popcnt`/`lemma_popcnt_le` (p09),
       `toks`/`fold_toks` (p14), `suf_at`/`nsuf_at` (p17),
       `apply`/`spec_apply` (p36) -- so the first pattern whose driver region
       sits outside `fn main` reaches it.

    `resolved` is False only for answer 2; `ambiguous` is True only for answer
    3. They are reported separately because the fix differs: answer 2 wants a
    different query, answer 3 wants a longer name."""
    extra = (["--verify-only-module", mod_path, "--verify-function", name]
             if mod_path else ["--verify-function", name, "--verify-root"])
    nv, ne, out = _verus(path, *extra)
    unresolved = nv is None and bool(_UNRESOLVED_RE.search(out or ""))
    ambiguous = nv is None and bool(_AMBIGUOUS_RE.search(out or ""))
    return nv, ne, out, not unresolved, ambiguous


def _mutant_path(pdir, src):
    """Where to write a mutated copy of `pdir/src` so it still compiles.

    A rung file carries `#[path = "../../common/driver.rs"]`, which rustc
    resolves relative to the *file's own directory*. So the mutant cannot go in
    a flat scratch dir: it goes into a mirror of the repo layout under
    `.temp/clausemut/<pattern>/`, with `common` symlinked back. The pattern
    directory itself is never written to -- a crashed gate run must not be able
    to leave a mutated source in the tree.

    The mirror is `<root>/patterns/<dirname>/`, **not** `os.path.relpath(pdir,
    REPO)`: the latter assumed every pattern sits exactly two levels below the
    repo root, so running the gate on a mutated copy under `.temp/` (which is
    how every bypass in this project has been demonstrated) put the mutant at a
    depth where `../../common` resolved to nothing and the stage failed with
    "the UNMUTATED copy does not verify" instead of doing its job."""
    root = os.path.join(REPO, ".temp", "clausemut", buildmod.pattern_id(pdir))
    d = os.path.join(root, "patterns", os.path.basename(pdir))
    os.makedirs(d, exist_ok=True)
    link = os.path.join(root, "common")
    if not os.path.islink(link) and not os.path.exists(link):
        os.symlink(os.path.join(REPO, "common"), link)
    return os.path.join(d, src)


def _insert_false_probe(txt, items, site, kname):
    """`txt` with `assert(false);` inserted after the first call to `kname` in
    `site`, or None if there is no such call.

    A reachability probe: if `assert(false)` *verifies* there, the verification
    context at the call site is contradictory and every caller is vacuous."""
    it = items.get(site)
    if it is None or it.body_start is None:
        return None
    code = vparse.blank_noncode(txt)
    m = re.search(r"\b" + re.escape(kname) + r"\s*\(", code[it.body_start:])
    if not m:
        return None
    i = it.body_start + m.end() - 1
    depth = 0
    while i < len(code):
        if code[i] == "(":
            depth += 1
        elif code[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    j = code.find(";", i)
    if j < 0:
        return None
    return txt[:j + 1] + "\n            assert(false);" + txt[j + 1:]


def _mutation_targets(items, also, src, rep, resolved):
    """(trusted, verified) items that the mutation stages must cover in `src`.

    `trusted` is every `#[verifier::external_body]` item -- derived, so nothing
    can be dropped from it. `verified` is `spec.md`'s
    `verus.clause_deletion_extra_items`, which defaults to `[kernel_item]`.

    That list used to be filtered with `if n in items`, so a **misspelled name
    was silently dropped** and declaring `"kernal"` exempted the real kernel's
    `ensures` from the whole stage while the log still printed a green line
    (TASK_006_REVIEW, minor 1). Names are resolved across all pinned files and
    anything never resolved is a hard failure -- see `_unresolved`."""
    trusted = [i for i in items.values()
               if i.external == "verifier::external_body"]
    verified = []
    for n in also:
        it = items.get(n)
        if it is None:
            continue
        resolved.add(n)
        if it.external == "verifier::external_body":
            continue          # already in `trusted`
        if it.external:
            rep.fail("clause-mut",
                     f"{src}: `{n}` is declared in "
                     f"verus.clause_deletion_extra_items but is {it.external}, "
                     f"so Verus never verifies it and mutating its clauses "
                     f"tests nothing")
            continue
        verified.append(it)
    return trusted, verified


def _unresolved(also, resolved, rep, section):
    missing = sorted(set(also) - resolved)
    if missing:
        rep.fail(section,
                 f"verus.clause_deletion_extra_items names {missing}, which "
                 f"exist in none of the pinned Verus files. The list used to be "
                 f"filtered with `if n in items`, so one typo exempted the "
                 f"kernel from mutation testing and the stage still printed a "
                 f"green line (TASK_006_REVIEW minor 1). An unknown name is a "
                 f"hard failure.")


def check_clause_deletion(pdir, rep, contract, enabled=True):
    """5c. Every trusted `ensures` clause must be load-bearing. DERIVED.

    `.memory/04-verus.md`, after TASK_004_REVIEW: p02's `copy_bytes` carries two
    `ensures` clauses and **neither is individually load-bearing** -- deleting
    either leaves `9 verified, 0 errors`, because the tail clause implies the
    length clause. Worse, the mutant that deletes half of the tail clause (M7)
    is not vacuous but a silent *strengthening*: it injects `dst.len() == n`,
    which is false of `copy_nonoverlapping`, consistent in context, and usable.
    A false axiom that is usable is worse than one that collapses the context,
    because nothing downstream looks wrong.

    Nothing the verifier reports distinguishes any of that from a healthy run,
    and the only defence was the declared `ensures` pin in `spec.md` -- which
    TASK_003_REVIEW showed moves with the code it constrains. So this stage
    *derives* the property instead:

        for each `ensures` **conjunct** of each `external_body` item: delete
        it, re-run Verus, and fail if the file still verifies with 0 errors.

    A clause whose deletion changes nothing was either implied by its
    neighbours (delete it, or merge them) or consumed by nobody (it is
    decoration). Either way the tally in NOTES.md is overstating what the
    trusted base actually says.

    **Conjunct, not clause** (TASK_006_REVIEW C). `vparse._clause_split` splits
    on top-level commas, so `ensures a, b` was two deletable units and
    `ensures a && b` was one: re-joining a redundant conjunct with `&&` made
    this stage delete both halves at once, the file failed, and the stage
    certified the clause load-bearing. One character, and the check is satisfied
    by reformatting. `vparse.conjunct_spans` splits at top-level `&&` / `&&&`
    and **refuses** any clause whose top level also carries `==>`, `||` or
    `<==>`, because a conjunct lifted out of an implication is not a deletable
    unit. Every refusal is shouted into the verdict rather than passed over.

    The `assert(false)` reachability probe runs beside it because it catches
    *genuine* vacuity -- an unsatisfiable `requires`, a contradictory context.
    It is **not** the detector for the clause class above: measured at
    TASK_004_REVIEW, `assert(false)` after the call is still unprovable with the
    M7 mutant in place.

    `requires` is **not** tested here; it needs a different oracle entirely and
    gets its own stage (`check_requires_strength`).

    Cost: one Verus run per conjunct plus two controls per file (1.7 s each on
    p02's verus.rs, measured at TASK_008)."""
    head("5c. clause deletion: is every trusted `ensures` conjunct load-bearing?")
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    site = vcfg.get("call_site", "main")
    kname = vcfg.get("kernel_item", "kernel")
    also = list(vcfg.get("clause_deletion_extra_items") or [kname])
    resolved = set()
    out = {}
    if not enabled:
        rep.fail("clause-mut", "--no-verus-mutants given: the clause-deletion "
                               "stage did not run, so nothing checked that this "
                               "pattern's trusted `ensures` clauses say anything")
        return out
    if not pinned_obl:
        rep.fail("clause-mut", "spec.md pins no verus.obligations, so there is "
                               "no file list to mutate")
        return out
    for src in sorted(pinned_obl):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        try:
            items = vparse.by_name(txt)
        except ValueError as e:
            rep.fail("clause-mut", f"{src}: {e}")
            continue
        mpath = _mutant_path(pdir, src)
        rows = []

        # --- control: the unmutated copy, at the scratch path ---------------
        # Without this, a stage that silently fails to compile anything would
        # report every clause as load-bearing and print a green line.
        open(mpath, "w").write(txt)
        base_v, base_e, base_out = _verus(mpath)
        if base_v is None or base_e:
            rep.fail("clause-mut",
                     f"{src}: the UNMUTATED copy at {os.path.relpath(mpath, REPO)} "
                     f"does not verify ({base_v} verified, {base_e} errors). "
                     f"Every mutant would then 'fail' for the wrong reason and "
                     f"this stage would certify nothing.\n      {base_out[-400:]}")
            continue
        print(f"    {src}: control (unmutated, relocated) -> {base_v} verified, "
              f"0 errors")

        # --- the assert(false) reachability probe ---------------------------
        probe = _insert_false_probe(txt, items, site, kname)
        if probe is None:
            rep.note(f"{src}: no `{kname}(` call inside `{site}`, so the "
                     f"assert(false) reachability probe did not run")
        else:
            open(mpath, "w").write(probe)
            pv, pe, po = _verus(mpath)
            rows.append(dict(item=site, kind="assert(false) probe", clause=None,
                             verified=pv, errors=pe))
            if pv is not None and pe == 0:
                rep.fail("clause-mut",
                         f"{src}: `assert(false)` immediately after the "
                         f"`{kname}(...)` call in `{site}` VERIFIES ({pv} "
                         f"verified, 0 errors). The verification context there "
                         f"is contradictory, so every obligation the call site "
                         f"discharges is vacuous and the proof constrains "
                         f"nothing.")
            elif pv is None:
                # `_verus` returns `(None, None)` whenever Verus emits no
                # `N verified, M errors` line at all. Without this arm the
                # `else` below reported a successful NEGATIVE result -- "the
                # call site's context is satisfiable" -- from a run that
                # produced no result. The clause-mutant loop 25 lines down and
                # 5c-req's deletion loop both have this arm; these two did not
                # (TASK_053 F5). Latent on the shipped tree: all 17 probe rows
                # in the committed records carry real numbers.
                rep.fail("clause-mut",
                         f"{src}: Verus produced no result for the "
                         f"`assert(false)` reachability probe, so the call "
                         f"site's context was never tested for satisfiability "
                         f"and this stage certified nothing about it.\n"
                         f"      {(po or '')[-300:]}")
            else:
                print(f"    {src}: assert(false) after `{kname}(...)` is "
                      f"unprovable ({pv} verified, {pe} errors) -- the call "
                      f"site's context is satisfiable")

        # --- one mutant per `ensures` conjunct ------------------------------
        targets, extra = _mutation_targets(items, also, src, rep, resolved)
        for it, why in ([(i, "trusted") for i in targets]
                        + [(i, "verified") for i in extra]):
            for idx, cj in enumerate(vparse.conjunct_spans(it, "ensures")):
                if cj["refused"]:
                    rep.shout("clause-mut",
                              f"{src} {it.name} ensures[{idx}] carries "
                              f"{cj['refused']}, so this stage refused to split "
                              f"it into conjuncts and deleted it whole. A "
                              f"redundant conjunct inside it would be "
                              f"undetectable here: "
                              f"{txt[cj['spans'][0][0]:cj['spans'][0][1]][:70]}")
                for jdx, (a, b) in enumerate(cj["spans"]):
                    ctext = vparse.norm_clause(txt[a:b])
                    open(mpath, "w").write(
                        vparse.delete_conjunct(txt, it, "ensures", idx, jdx))
                    mv, me, mo = _verus(mpath)
                    rows.append(dict(item=it.name, kind=why, clause=ctext,
                                     verified=mv, errors=me))
                    tag = (f"{src} {it.name} ensures[{idx}]"
                           + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1 else ""))
                    if mv is not None and me == 0:
                        rep.fail("clause-mut",
                                 f"{tag} is NOT load-bearing: deleting "
                                 f"`{ctext}` still gives {mv} verified, 0 errors. "
                                 + ("A trusted item's `ensures` is an axiom; one "
                                    "that nothing depends on is an unchecked claim "
                                    "about real Rust semantics carried for free, "
                                    "and the TCB tally counts it as an obligation "
                                    "the reviewer must judge. Merge it into the "
                                    "clause that implies it, or delete it."
                                    if why == "trusted" else
                                    "Nothing consumes this postcondition, so it is "
                                    "decoration: replacing it with a tautology "
                                    "would verify too (`.memory/04-verus.md`). "
                                    "Consume it with a ghost `assert` at the call "
                                    "site."))
                    elif mv is None:
                        rep.fail("clause-mut", f"{tag}: Verus produced no result "
                                               f"for the mutant\n      {mo[-300:]}")
                    else:
                        print(f"    {src}: {it.name} ensures[{idx}]"
                              + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1
                                 else "")
                              + f" load-bearing ({mv} verified, {me} errors)"
                                f" -- {ctext[:58]}")
        open(mpath, "w").write(txt)      # leave the scratch copy unmutated
        out[src] = {"control_verified": base_v, "mutants": rows}
    if out:
        _unresolved(also, resolved, rep, "clause-mut")
    # `n` counts CLAUSE mutants, not rows: the `assert(false)` probe is a row
    # too, so `len(rows)` is >= 1 whenever the stage ran at all and a green line
    # keyed on it would assert "every trusted `ensures` conjunct is
    # load-bearing" over zero conjuncts. TASK_009_REVIEW's x3 was exactly this
    # shape one stage over -- `0 verified twin(s): every trusted `unsafe` item's
    # `requires` is strong enough ...` -- so every count-bearing `rep.ok` in
    # this file now states its `n` and refuses to fire at zero (TASK_010 C).
    n = sum(1 for v in out.values() for r in v["mutants"] if r["clause"])
    probes = sum(1 for v in out.values() for r in v["mutants"] if not r["clause"])
    if out and not n:
        rep.fail("clause-mut",
                 f"this stage deleted 0 `ensures` conjuncts across "
                 f"{sorted(out)} ({probes} reachability probe(s) only), so it "
                 f"certified nothing about any trusted postcondition. Either no "
                 f"trusted item states an `ensures` -- in which case say so in "
                 f"spec.md and check `verus.items` -- or the conjunct splitter "
                 f"found nothing to delete.")
    elif out and not any(f[0] == "clause-mut" for f in rep.failures):
        rep.ok(f"{n} `ensures` conjunct(s) deleted across {len(out)} file(s) "
               f"(n={n} > 0), plus {probes} reachability probe(s): every trusted "
               f"`ensures` conjunct is load-bearing, and `assert(false)` at the "
               f"call site is unprovable. Derived, not declared -- this does not "
               f"inherit the self-certification problem of a `spec.md` pin.")
    return out


_SLICE_TY_RE = re.compile(r"^&\s*(?P<mut>mut\s+)?\[")

# Tactics the tautology probe tries, in order, before it will say "this clause
# constrains a caller". The bare probe's oracle is "Z3 proved it", so a
# tautology that needs a decision procedure reads as meaningful without them:
# TASK_008_REVIEW measured `off <= (off | 1)` and `(off & 0xff) <= 255` as
# "not a tautology" against the bare probe, and both are `true` for every
# `usize`. One extra Verus run per tactic, and only for a conjunct the previous
# tactic failed on, so the shipped tree pays for all of them and a tautological
# one pays for one.
_TAUT_TACTICS = (None, "nonlinear_arith", "bit_vector")


def _ambient_facts(item):
    """The facts a real call site has and a bare `proof fn` does not.

    TASK_008_REVIEW, major D: the probe reported this project's own documented
    tautology `v@.len() <= usize::MAX` as "not a tautology", because it comes
    from `vstd::slice::axiom_spec_len` whose trigger is `spec_slice_len(slice)`
    -- a term that appears nowhere in normal code. p02's kernel fires it with
    one ghost `assert`; the probe had no such line, so a clause the *caller* can
    discharge and the bare probe cannot was the exploitable residual.

    So the probe now opens with the same two moves: bring the slice axioms in by
    `broadcast use`, and mention `spec_slice_len` once per slice parameter to
    fire the trigger. `broadcast use` of a group the file already broadcasts is
    not an error (measured), and a parameter that is not a slice gets nothing --
    `spec_slice_len` on a `&Vec<T>` would not type-check."""
    out = ["broadcast use vstd::slice::group_slice_axioms;"]
    for nm, ty in vparse.params(item):
        if nm == "self":
            continue
        m = _SLICE_TY_RE.match(re.sub(r"\s+", " ", ty).strip())
        if not m:
            continue
        # a `&mut [T]` parameter is only nameable as `old(x)` in this position
        ref = f"old({nm})" if m.group("mut") else nm
        out.append(f"assert({ref}@.len() == vstd::slice::spec_slice_len({ref}));")
    return out


def _taut_probe(txt, item, a, b, tag, tactic=None):
    """(`txt` with a synthesised `proof fn` whose only obligation is the clause
    at `txt[a:b]`, None), or (None, why it could not be synthesised).

    If that verifies, the clause is a **tautology**: it is `true` for every
    value its parameters can take, so demanding it of a caller demands nothing.
    `n >= 0` on a `usize` and `0 <= i` on a `usize` are both of this shape, and
    both walked past the gate at TASK_006_REVIEW while the structural rule
    printed them approvingly.

    Three things travel with the parameter list, all measured as hard failures
    without them at TASK_008_REVIEW (major C) -- fail-closed, but the
    consequence was that *a pattern with a generic or method-shaped trusted
    accessor could not be greened at all*:

      * the **generic list** (`<T: Copy>` -> E0425 cannot find type `T`);
      * the **`where` clause** (same error);
      * **lifetimes** (`<'a>` -> E0261 undeclared lifetime `'a`).

    A `self` receiver is the fourth, and it cannot be fixed by copying more of
    the signature -- *"`self` parameter is only allowed in associated
    functions"*. The probe is synthesised **inside the item's own `impl`
    block** instead, where `self`, `Self` and the impl's generics are all in
    scope. An item with a `self` receiver and no `impl` the parser could find is
    refused *by name*, not by an opaque compile error."""
    vs = vparse.verus_span(txt)
    if vs is None:
        return None, "the file has no `verus! {}` span to put the probe in"
    try:
        gen, prm, whr = vparse.sig_prefix(item)
        pars = vparse.params(item)
    except ValueError as e:
        return None, str(e)
    at = vs[1]
    if item.impl_span is not None:
        at = item.impl_span[1]
    elif any(n == "self" for n, _ in pars):
        return None, (f"`{item.name}` takes a `self` receiver but vparse found "
                      f"no enclosing `impl` block, so there is nowhere to "
                      f"synthesise an associated function")
    body = _ambient_facts(item)
    if tactic:
        body.append(f"assert({txt[a:b]}) by ({tactic});")
    fn = (f"\nproof fn slb_taut_probe_{tag}{gen}{prm}{' ' + whr if whr else ''}\n"
          f"    ensures\n        {txt[a:b]},\n{{\n"
          + "".join(f"    {l}\n" for l in body) + "}\n")
    return txt[:at] + fn + txt[at:], None


def _run_taut_battery(txt, item, a, b, tag, mpath, base_v):
    """(verdict, verified, errors, output, tactic, tactics) for one `requires`
    conjunct.

    Verdicts: `tautology` (some tactic proved it under no hypotheses),
    `not a tautology`, `unsynthesisable` (the probe could not be built -- the
    reason is in `output`), `nocompile` (Verus produced no result at all),
    `perturbed` (the probe moved something other than the one obligation it
    added, so the conjunct was not judged). Everything but the second is a
    failure for the caller; none of them is a silent skip.

    `tactics` is `{"ran": [...], "inapplicable": [...]}`: which tactics actually
    produced a verdict on THIS clause and which could not be applied to it at
    all, so the caller can stop claiming the second group judged anything
    (TASK_053 F2, landed at TASK_056)."""
    pv = pe = None
    po, used = "", None
    tactics = {"ran": [], "inapplicable": []}
    for tac in _TAUT_TACTICS:
        probe, whynot = _taut_probe(txt, item, a, b, tag, tac)
        if probe is None:
            return "unsynthesisable", None, None, whynot, tac, tactics
        open(mpath, "w").write(probe)
        rv, re_, ro = _verus(mpath)
        if tac is not None and rv is None:
            # THE TACTIC COULD NOT BE APPLIED -- not a negative result, and not
            # a failure. `by (bit_vector)` refuses any assertion mentioning
            # `v@.len()`; Verus then emits no `N verified, M errors` line at all
            # and `_verus` returns `(None, None)`. A tactic that aborts could
            # not have proved the clause either, so there is no false negative
            # to recover and 5c-req's SOUNDNESS is untouched. What was wrong was
            # the CLAIM: this arm did not exist, control fell through to
            # `return "not a tautology"`, and the record carried
            # `verified: null, errors: null, tactic: "bit_vector"` while the
            # transcript named `by (bit_vector)` as a tactic that had judged the
            # clause. TASK_053 F2 measured 51 of the project's 52 shipped
            # conjuncts landing here, on all 16 patterns; the only exception is
            # p08's `0 < dr <= m`, the one conjunct with no `@` in it. Making
            # this a hard failure would red-line all 16 patterns for Verus
            # behaving correctly (measured, TASK_053), so it is RECORDED and the
            # `ok` line below no longer names a tactic that never ran.
            #
            # `pv`/`pe`/`po`/`used` are deliberately NOT overwritten: the record
            # must carry the last tactic that actually produced a verdict.
            tactics["inapplicable"].append(tac)
            continue
        pv, pe, po = rv, re_, ro
        used = tac
        tactics["ran"].append(tac)
        if tac is None:
            if pv is None:
                return "nocompile", pv, pe, po, tac, tactics
            if pe == 0:
                return "tautology", pv, pe, po, tac, tactics
            if pe != 1 or pv != base_v:
                return "perturbed", pv, pe, po, tac, tactics
        elif pe == 0:
            return "tautology", pv, pe, po, tac, tactics
    return "not a tautology", pv, pe, po, used, tactics


def check_requires_strength(pdir, rep, contract, enabled=True):
    """5c-req. Does every `requires` conjunct demand anything of a caller?

    TASK_006_REVIEW's blocker B: stage 5c iterated `it.clauses.get("ensures")`
    and nothing else, and the `requires` hole is the dangerous one. All three of
    these gave **9 verified, 0 errors** on p02, with the obligation count
    unmoved at 9 and the full gate green:

      * delete `from + n <= src@.len()` from the trusted `copy_bytes`;
      * weaken `get_unchecked`'s `i < v@.len()` to `0 <= i`;
      * replace both of `copy_bytes`'s preconditions with `n >= 0`.

    **The task specified the mirror of the `ensures` test -- delete the clause,
    re-run, fail if the file still verifies -- and that oracle does not exist
    for a trusted item.** Measured at TASK_008 on p02's `verus.rs`:

        control                                9 verified, 0 errors
        delete copy_bytes.requires[0]  (M1)    9 verified, 0 errors
        get_unchecked requires -> 0 <= i (M2)  9 verified, 0 errors
        copy_bytes requires -> n >= 0  (M3)    9 verified, 0 errors
        delete kernel.requires[0]              8 verified, 1 errors

    Deleting a precondition from an `external_body` item removes an obligation
    from its call sites, which makes verification *strictly easier*; nothing can
    fail. Implementing the prescription as written would report every trusted
    precondition in the project as "not load-bearing" on every run. The last row
    is why the deletion test is still run -- for a **verified** item the deleted
    precondition is an assumption its own body was using, so the file does fail,
    and that is a real mirror image.

    So this stage runs three checks, and the third is the one that catches all
    three mutants:

      1. **deletion**, for the `requires` of *verified* items only: delete the
         conjunct, and fail if the file still verifies;
      2. **tautology probe**, for every item: a synthesised `proof fn` with the
         item's parameters and the conjunct as its sole `ensures`. If that
         verifies under no hypotheses, the conjunct is `true` and demands
         nothing. Catches M2 and M3;
      3. **parameter coverage** for trusted `unsafe` items, in stage 5a
         (`_check_trusted_unsafe`) because that is where its sibling rule lives.
         Catches M1, M2 and M3.

    Nothing here is declared, so none of it inherits the self-certification
    problem of a `spec.md` pin."""
    head("5c-req. precondition strength: does every `requires` conjunct "
         "demand anything?")
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    kname = vcfg.get("kernel_item", "kernel")
    also = list(vcfg.get("clause_deletion_extra_items") or [kname])
    resolved = set()
    out = {}
    n_inapp = 0          # (clause, tactic) pairs where the tactic never ran
    if not enabled:
        rep.fail("req-mut", "--no-verus-mutants given: the precondition-strength "
                            "stage did not run, so nothing checked that this "
                            "pattern's trusted `requires` clauses demand "
                            "anything")
        return out
    if not pinned_obl:
        rep.fail("req-mut", "spec.md pins no verus.obligations, so there is no "
                            "file list to mutate")
        return out
    for src in sorted(pinned_obl):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        try:
            items = vparse.by_name(txt)
        except ValueError as e:
            rep.fail("req-mut", f"{src}: {e}")
            continue
        mpath = _mutant_path(pdir, src)
        open(mpath, "w").write(txt)
        base_v, base_e, base_out = _verus(mpath)
        if base_v is None or base_e:
            rep.fail("req-mut",
                     f"{src}: the UNMUTATED copy at "
                     f"{os.path.relpath(mpath, REPO)} does not verify "
                     f"({base_v} verified, {base_e} errors), so every mutant "
                     f"below would 'fail' for the wrong reason\n"
                     f"      {base_out[-400:]}")
            continue
        rows = []
        targets, extra = _mutation_targets(items, also, src, rep, resolved)
        for it, why in ([(i, "trusted") for i in targets]
                        + [(i, "verified") for i in extra]):
            for idx, cj in enumerate(vparse.conjunct_spans(it, "requires")):
                if cj["refused"]:
                    rep.shout("req-mut",
                              f"{src} {it.name} requires[{idx}] carries "
                              f"{cj['refused']}, so it was not split into "
                              f"conjuncts: a vacuous conjunct inside it is "
                              f"invisible to this stage.")
                for jdx, (a, b) in enumerate(cj["spans"]):
                    ctext = vparse.norm_clause(txt[a:b])
                    tag = (f"{src} {it.name} requires[{idx}]"
                           + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1 else ""))
                    # --- 2. tautology probe (every item) --------------------
                    # Bare Z3 first, then a decision procedure per tactic. Each
                    # is only reached because the previous one failed, so a
                    # genuine tautology usually costs one run and only a clause
                    # that survives all of them costs three.
                    verdict, pv, pe, po, used, tacs = _run_taut_battery(
                        txt, it, a, b, f"{it.name}_{idx}_{jdx}", mpath, base_v)
                    inapp = tacs["inapplicable"]
                    n_inapp += len(inapp)
                    rows.append(dict(item=it.name, kind=why, clause=ctext,
                                     test="tautology", tactic=used,
                                     # TASK_053 F2: which tactics actually
                                     # produced a verdict on THIS clause, and
                                     # which aborted without one.
                                     tactics_ran=tacs["ran"],
                                     tactics_inapplicable=inapp,
                                     verified=pv, errors=pe, verdict=verdict))
                    if verdict == "unsynthesisable":
                        rep.fail("req-mut",
                                 f"{tag}: the tautology probe could not be "
                                 f"synthesised, so this conjunct was not judged "
                                 f"at all -- {po}. Fix the probe rather than "
                                 f"skipping the clause.")
                    elif verdict == "nocompile":
                        rep.fail("req-mut",
                                 f"{tag}: the tautology probe did not compile, "
                                 f"so this conjunct was not judged at all. Fix "
                                 f"the probe rather than skipping the "
                                 f"clause.\n      {(po or '')[-300:]}")
                    elif verdict == "tautology":
                        rep.fail("req-mut",
                                 f"{tag} is a TAUTOLOGY: `{ctext}` is provable "
                                 f"from the parameter types alone ({pv} "
                                 f"verified, 0 errors -- control {base_v}"
                                 + (f", via `by ({used})`" if used else "")
                                 + f"), so it demands nothing of any caller. "
                                 + ("A trusted `unsafe` item whose precondition "
                                    "is `true` is the axiom that the unchecked "
                                    "operation is always defined -- `n >= 0` on "
                                    "a `usize` is exactly this, and it passed "
                                    "the whole gate at TASK_006_REVIEW."
                                    if why == "trusted" else
                                    "A verified item's precondition that holds "
                                    "always constrains no call site."))
                    elif verdict == "perturbed":
                        rep.fail("req-mut",
                                 f"{tag}: the tautology probe gave {pv} "
                                 f"verified, {pe} errors against a control of "
                                 f"{base_v}/0. Exactly one new obligation was "
                                 f"added, so anything but {base_v}/1 means the "
                                 f"probe broke something else and this "
                                 f"conjunct was not judged.\n"
                                 f"      {(po or '')[-300:]}")
                    else:
                        ran = [t for t in _TAUT_TACTICS
                               if t and t not in inapp]
                        print(f"    {src}: {it.name} requires[{idx}]"
                              + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1
                                 else "")
                              + f" is not a tautology (bare Z3"
                              + ("".join(f", `by ({t})`" for t in ran))
                              + ("; INAPPLICABLE here, never ran: "
                                 + ", ".join(f"`by ({t})`" for t in inapp)
                                 if inapp else "")
                              + f") -- {ctext[:52]}")
                    # --- 1. deletion, for verified items only ---------------
                    if why != "verified":
                        continue
                    open(mpath, "w").write(
                        vparse.delete_conjunct(txt, it, "requires", idx, jdx))
                    mv, me, mo = _verus(mpath)
                    rows.append(dict(item=it.name, kind=why, clause=ctext,
                                     test="deletion", verified=mv, errors=me))
                    if mv is not None and me == 0:
                        rep.fail("req-mut",
                                 f"{tag} is NOT load-bearing: deleting it from "
                                 f"a *verified* item still gives {mv} verified, "
                                 f"0 errors, so its own body never used the "
                                 f"assumption and no call site had to discharge "
                                 f"it. It is decoration.")
                    elif mv is None:
                        rep.fail("req-mut", f"{tag}: Verus produced no result "
                                            f"for the deletion mutant\n"
                                            f"      {(mo or '')[-300:]}")
                    else:
                        print(f"    {src}: {it.name} requires[{idx}] is "
                              f"load-bearing when deleted ({mv} verified, {me} "
                              f"errors)")
        open(mpath, "w").write(txt)
        out[src] = {"control_verified": base_v, "mutants": rows}
    if out:
        _unresolved(also, resolved, rep, "req-mut")
    # Count what was actually judged, and refuse the green line at zero
    # (TASK_010 C -- a count-bearing `rep.ok` must state its `n`).
    n = sum(1 for v in out.values() for r in v["mutants"]
            if r["test"] == "tautology")
    dels = sum(1 for v in out.values() for r in v["mutants"]
               if r["test"] == "deletion")
    if out and not n:
        rep.fail("req-mut",
                 f"this stage judged 0 `requires` conjuncts across "
                 f"{sorted(out)}, so nothing was tested for triviality. A "
                 f"pattern whose trusted items and kernel all have empty "
                 f"preconditions has no obligations for a caller to discharge, "
                 f"which is the pilot's defect, not a clean run.")
    elif out and not any(f[0] == "req-mut" for f in rep.failures):
        # The tactic list is per-run, not the constant `_TAUT_TACTICS`: a tactic
        # that ABORTED on a clause judged nothing, and naming it here is exactly
        # the false claim TASK_053 F2 found in all 16 transcripts.
        rep.ok(f"{n} `requires` conjunct(s) probed (n={n} > 0) and {dels} "
               f"deleted, across {len(out)} file(s): no `requires` "
               f"conjunct is a tautology under bare Z3"
               + "".join(f" or `by ({t})`" for t in _TAUT_TACTICS
                         if t and any(t in (r.get("tactics_ran") or [])
                                      for v in out.values()
                                      for r in v["mutants"]
                                      if r["test"] == "tautology"))
               + (f". {n_inapp} (conjunct, tactic) pair(s) are NOT claimed: the "
                  f"tactic could not be applied to that clause and produced no "
                  f"verdict at all -- see `tactics_inapplicable` per row "
                  f"(TASK_053 F2: `by (bit_vector)` aborts on any clause "
                  f"mentioning a slice length)" if n_inapp else "")
               + f", and every *verified* item's "
               f"precondition fails the file when deleted. Note what is NOT "
               f"claimed: (a) deleting a trusted item's precondition can never "
               f"fail a file (measured -- it only removes obligations from "
               f"callers), so a *missing* one is caught by the "
               f"parameter-coverage rule in 5a, not here; (b) this stage judges "
               f"TRIVIALITY, not STRENGTH -- `i <= v@.len()` is not a tautology "
               f"and is still one byte past the end. Strength is stage 5c-twin.")
    return out


# ==========================================================================
# 5c-twin. the verified twin: is the trusted `requires` STRONG ENOUGH?
# ==========================================================================

# Anything that would let a twin pass without Verus actually checking the
# operation. `unsafe` and `external_body` would make the twin a second copy of
# the axiom; `assume`/`admit` would let the author write the precondition they
# wish they had; calling the trusted item itself is the degenerate cheat.
_TWIN_BANNED = ("unsafe", "assume", "admit", "assume_specification",
                "external_body", "external")

_TWIN_CFG_TOKEN_RE = re.compile(r"\b" + TWIN_CFG + r"\b")
_TWIN_CFG_ATTR_RE = re.compile(r"#!?\[\s*cfg\s*\(\s*" + TWIN_CFG + r"\s*\)\s*\]")


def _check_twin_cfg_hygiene(rep, src, txt, items, extra=()):
    """The twin must be verified in the **shipped** configuration.

    TASK_009_REVIEW's blocker x2. `check.py` verifies the twins with
    `_verus(path, "--cfg", TWIN_CFG)`, and that cfg changes the meaning of the
    *whole file*, not just the twin items. The "only a verified twin may be
    `#[cfg]`-gated" rule in 5a is enforced over `vparse` items -- i.e. `fn`s --
    so a cfg'd `const`, `use`, `type`, `static` or `mod` is invisible to it.
    Measured mirror:

        #[cfg(slb_twin)]      pub const SLACK: usize = 0;
        #[cfg(not(slb_twin))] pub const SLACK: usize = 1;
        pub open spec fn in_bounds(v: &[u8], i: usize) -> bool
            { i < v@.len() + SLACK }

    used as the `requires` of **both** `get_unchecked` and its twin, so
    `norm_clause(sig)` compares equal character for character. The twin was then
    checked against `i < v@.len() + 0` while R5 ships `i < v@.len() + 1`;
    `get_unchecked(v, v.len())` verifies in the shipped config (11 verified, 0
    errors) and fails only under `--cfg slb_twin`. Gate: PASS, 0 failures, 0
    shouts.

    The rule: **the token `slb_twin` may appear in a pinned Verus source only
    inside a twin item's own `#[cfg(slb_twin)]` attribute.** Anything else is a
    hard failure.

    Why this is a complete check and not a heuristic: Rust's conditional
    compilation is driven by `cfg`/`cfg_attr` predicates, and a predicate that
    depends on `slb_twin` must **name** it in the crate's token stream -- there
    is no indirection (no aliasing of cfg names, no computed predicates). So if
    the token occurs nowhere but on the twins' own attributes, the two
    compilations agree on every item except the twins, which is exactly the
    property x2 broke. The token stream includes what `#[path]`-included files
    contribute, so those are scanned too (`extra`); `slb_twin_<name>` itself
    does not match, because `_` is a word character.

    It is checked *before* any Verus run in this stage, so a file that fails it
    never gets a twin certificate at all."""
    code = vparse.blank_noncode(txt)
    twin_names = {i.name for i in items.values()
                  if i.name.startswith(TWIN_PREFIX)}
    allowed = []
    for i in items.values():
        if i.name not in twin_names or i.start is None or i.sig_start is None:
            continue
        for a, b in vparse.attribute_spans(code):
            if i.start <= a and b <= i.sig_start and _TWIN_CFG_ATTR_RE.fullmatch(
                    code[a:b].strip()):
                allowed.append((a, b))
    bad = [m.start() for m in _TWIN_CFG_TOKEN_RE.finditer(code)
           if not any(a <= m.start() < b for a, b in allowed)]
    for off in bad:
        rep.fail("twin",
                 f"{src}:{txt.count(chr(10), 0, off) + 1} the token "
                 f"`{TWIN_CFG}` appears outside any twin item's own "
                 f"`#[cfg({TWIN_CFG})]` attribute: "
                 f"`{vparse.norm_clause(txt[max(0, off - 40):off + 40])}`. "
                 f"5c-twin verifies this file with `--cfg {TWIN_CFG}`, which "
                 f"changes the meaning of the WHOLE file, so any other use of "
                 f"the token lets the twin be checked against a contract R5 "
                 f"does not ship. TASK_009_REVIEW measured it: "
                 f"`#[cfg({TWIN_CFG})] const SLACK: usize = 0;` with "
                 f"`#[cfg(not({TWIN_CFG}))] ... = 1;` inside a spec fn shared as "
                 f"the `requires` of both the trusted item and its twin gives a "
                 f"character-identical signature comparison, a clean twin run, "
                 f"and a shipped `requires` of `i < v@.len() + 1` -- reading one "
                 f"past the end, verified. The `#[cfg]` on a `const` is "
                 f"invisible to the item-set pin because `vparse` parses `fn` "
                 f"items only.")
    for path in extra:
        ecode = vparse.blank_noncode(open(path).read())
        for m in _TWIN_CFG_TOKEN_RE.finditer(ecode):
            rep.fail("twin",
                     f"{os.path.relpath(path, REPO)}:"
                     f"{ecode.count(chr(10), 0, m.start()) + 1} the token "
                     f"`{TWIN_CFG}` appears in a file `{src}` `#[path]`-includes. "
                     f"It is part of the same crate, so it changes what "
                     f"`--cfg {TWIN_CFG}` compiles -- the twin would be verified "
                     f"against a configuration no build ships.")
    if not bad and allowed:
        print(f"    {src}: the token `{TWIN_CFG}` occurs nowhere but on the "
              f"{len(allowed)} twin `#[cfg({TWIN_CFG})]` attribute(s), so the "
              f"shipped configuration and the `--cfg {TWIN_CFG}` one differ in "
              f"nothing but the twin items themselves")


_ARG_MARK = "SLB-TRUSTED" "-ARGUMENT"
_ARG_RE = re.compile(r"^.*" + _ARG_MARK + r"\s+(\S+)\s+(\S+)\s*$", re.M)
_ARG_MIN_CHARS = 200


def _check_trusted_arguments(rep, pdir, trusted_by_src):
    """The part no mechanism can judge, required to exist and printed.

    TASK_009_REVIEW's deepest finding (x4): **a trusted `ensures` need not be
    complete with respect to the operations its body performs.** Replace
    `get_unchecked`'s body with

        unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }

    and the contract, the twin and the pins are all still exactly right: nothing
    licenses the `i + 1` read, and no Verus stage can see it, because the twin
    only has to satisfy the `ensures` and the `ensures` never mentions it.

    Three of the four questions that decide whether a trusted item is sound are
    outside every oracle this gate has:

      (a) is the twin's body the right *checked stand-in* for the unchecked
          operation (`v[i]` for `*v.get_unchecked(i)`)?
      (b) is the `ensures` **complete** with respect to every unchecked
          operation the body performs?
      (c) does each clause mean the same thing in the shipped configuration as
          in the twin's?

    So the gate requires the argument to *exist*, per item, in the pattern's
    `NOTES.md`, and prints it in full on every run where a reviewer reads it --
    the same design as `verus.unsafe_justifications`, applied to the question
    that has no mechanical answer. It checks the marker, the three labels and a
    minimum length; it cannot check the reasoning, and says so. Judging it is
    the human's job and this is the paragraph they are meant to read."""
    path = os.path.join(pdir, "NOTES.md")
    txt = open(path).read() if os.path.exists(path) else ""
    blocks, hits = {}, list(_ARG_RE.finditer(txt))
    for i, m in enumerate(hits):
        # The block ends at the next marker, the next markdown heading, or the
        # next horizontal rule -- whichever comes first. Without the last two,
        # the final marker in the file swallows the rest of NOTES.md and the
        # gate log prints 31 kB of unrelated prose, which is the opposite of
        # making one paragraph impossible to skip.
        ends = [hits[i + 1].start()] if i + 1 < len(hits) else []
        for pat in (r"^#{1,6} ", r"^---\s*$"):
            nxt = re.search(pat, txt[m.end():], re.M)
            if nxt:
                ends.append(m.end() + nxt.start())
        blocks[(m.group(1), m.group(2))] = txt[m.end():min(ends or [len(txt)])].strip()
    for src, names in sorted(trusted_by_src.items()):
        for name in sorted(names):
            body = blocks.get((src, name))
            if body is None:
                rep.fail("twin",
                         f"NOTES.md carries no `{_ARG_MARK} {src} {name}` "
                         f"section. Every trusted item needs a written, per-item "
                         f"argument for the three things no stage of this gate "
                         f"can judge: (a) is the twin's body the right checked "
                         f"stand-in for the unchecked operation; (b) is the "
                         f"`ensures` COMPLETE with respect to every unchecked "
                         f"operation the body performs; (c) does each clause "
                         f"mean the same thing in the shipped configuration as "
                         f"in the twin's. (b) is TASK_009_REVIEW's x4: a body "
                         f"that also reads `i + 1` passes the contract pin, the "
                         f"twin and the `--cfg {TWIN_CFG}` run unchanged. The "
                         f"gate requires the text and prints it; only a human "
                         f"can judge it.")
                continue
            missing = [l for l in ("(a)", "(b)", "(c)") if l not in body]
            if missing or len(body) < _ARG_MIN_CHARS:
                rep.fail("twin",
                         f"NOTES.md's `{_ARG_MARK} {src} {name}` section is "
                         f"{len(body)} chars and is missing {missing or 'nothing'} "
                         f"-- all three of (a) the twin as a checked stand-in, "
                         f"(b) the `ensures`'s COMPLETENESS with respect to every "
                         f"unchecked operation in the body, and (c) the clause "
                         f"meaning the same in both configurations must be "
                         f"argued, in at least {_ARG_MIN_CHARS} characters.")
                continue
            print(f"    HUMAN MUST JUDGE -- {src} `{name}`, from NOTES.md "
                  f"({len(body)} chars):")
            for line in body.splitlines():
                print(f"      | {line}")


def check_trusted_twins(pdir, rep, contract, enabled=True):
    """Does the trusted `requires` actually **license the operation**?

    TASK_008_REVIEW's blocker: `get_unchecked`'s `requires i < v@.len()`
    weakened to **`i <= v@.len()`**, with the `spec.md` pin moved in the same
    commit, passes the entire gate -- PASS, complete_run True, 0 failures. 5a
    prints it approvingly (*"demands `['i <= v@.len()']` of every caller,
    constraining every parameter its body uses"*); 5c-req's tautology probe
    cannot see it, because it is not a tautology; parameter coverage cannot see
    it, because both parameters appear; deletion is not applied to trusted items
    and cannot be (TASK_008 measured that deleting a trusted precondition only
    *removes* obligations, so nothing ever fails). R5's trusted base then
    axiomatises that **reading one byte past the end of a slice is defined and
    equals `v@[i]`** -- CWE-125, the bug class the next pattern exists to model.
    The same shape on the copy is `from + n <= src@.len() + 1`.

    Those three checks judge *triviality* and *mention*. Neither is *strength*,
    and strength is the whole property.

    **The mechanism: a verified twin.** Beside every trusted `unsafe` item,
    `verus.rs` carries `slb_twin_<name>` -- the *same signature and the same
    contract, character for character*, implemented in checked code instead of
    `unsafe`. `get_unchecked`'s twin is `{ v[i] }`; `copy_bytes`'s is an indexed
    copy loop. The gate asserts the twin verifies against that contract.

    ⚠⚠⚠ **THE PARENTHESIS THAT USED TO SIT ON THAT SENTENCE WAS FALSE, AND THIS
    WAS THE THIRD AND WORST SITE OF IT.** It read *"there is no vstd spec for
    `copy_from_slice`, so a bulk-copy twin is not available --
    `.memory/04-verus.md`"*. The pinned vstd ships

        ~/tools/verus/vstd/std_specs/slice.rs:205
        pub assume_specification<T: Copy>[ <[T]>::copy_from_slice ]
            (dst: &mut [T], src: &[T])
            requires old(dst)@.len() == src@.len(),
            ensures  final(dst)@ == src@;

    and has since before p02 was built. `CLAUDE.md` records this exact claim as
    having stood from TASK_004 to TASK_048; `patterns/p02-buffer-copy/NOTES.md`
    5b, `patterns/p06-rotate/NOTES.md` 6a and three p06 rung sources all carry
    the correction, and **the gate's own explanation of its rule did not** --
    which made this the site an engineer reads *while being told to write a
    twin*. ⚠ The `.memory/04-verus.md` citation was dangling as well: that file
    now carries only the CORRECTION (`:691`, `:1149`), so the parenthesis cited,
    as its authority, a file that says the opposite.

    ✅ **A BULK-COPY TWIN IS AVAILABLE, AND TASK_164 BUILT ONE RATHER THAN
    ARGUING ABOUT IT** (`.temp/t164/twinprobe/`, generators kept). Replacing
    only `slb_twin_copy_bytes`'s BODY with
    `let (a, _b) = dst.split_at_mut(n); a.copy_from_slice(&src[from..from + n]);`
    -- keeping the shipped twin's own `assert(src@.len() ==
    vstd::slice::spec_slice_len(src));`, which fires `axiom_spec_len` so
    `from + n` cannot overflow:

        shipped indexed loop, `--cfg slb_twin`          12 verified, 0 errors
        bulk-copy twin,       `--cfg slb_twin`          11 verified, 0 errors
        bulk-copy twin + the documented weakening       10 verified, 1 errors
          (`from + n <= src@.len()` -> `... + 1`, in BOTH the trusted item and
           the twin) -> `precondition not satisfied` at `&src[from..from + n]`

    **So the bulk twin is a working strength oracle, not merely compilable.**
    It is one obligation cheaper because the `while` loop is gone.

    ⚠ **p02 is NOT changed here, and the reason is a cost rather than an
    impossibility.** `verus.twin_obligations` is `{"verus.rs": 12}` INSIDE the
    `slb-contract` fence, so swapping the twin moves `contract_sha256`, stales
    the published table and costs a `report.py` plus a second gate. The indexed
    loop also remains the more independent check -- it re-derives the copy
    element by element from `v[i]`-style indexing rather than leaning on one
    more vstd `assume_specification`. **Reported at TASK_164, not built.**
    ⚠⚠ **What does NOT apply here is the `identity` argument**: p02 keeps its
    `external_body` wrapper on the SHIPPED `copy_bytes` because the verified
    spelling is 81/79 instructions against R4's 72/70, `+5.00 Ir`/call, and
    breaks `identity: exact` (p02 `NOTES.md` 5b). A twin is `#[cfg(slb_twin)]`
    and no build compiles it, so it costs zero instructions either way. The two
    questions are different and the old parenthesis blurred them.

    Why this is an oracle for strength: a precondition too weak to license the
    unchecked operation is too weak to license the checked one, and the checked
    one is the one Verus can see. Measured on p02:

        shipped (`i < v@.len()`, `from + n <= src@.len()`)  12 verified, 0 errors
        `i <= v@.len()`, twin edited to match                11 verified, 1 errors
              error: precondition not met: index in bounds for this access -> v[i]
        `from + n <= src@.len() + 1`, ditto                  10 verified, 2 errors
              error: precondition not met: index in bounds -> src[from + j]
        weakened + a *defensive* twin `if i < v.len() {v[i]} else {0}`
                                                             11 verified, 1 errors
              error: postcondition not satisfied -> r == v@[i as int]

    The last row is the reason this is not just another pin: the twin has to
    satisfy the trusted item's `ensures` as well, so an author cannot rescue a
    weakened `requires` by making the twin defensive. It is the `model.py` move
    -- an independent implementation -- applied to the trusted base.

    Four structural rules keep it honest, each closing a way to write a twin
    that passes without checking anything:

      * **the twin's signature must be identical to the trusted item's**,
        modulo whitespace. Otherwise the attacker weakens the trusted item and
        leaves the twin alone -- measured: that variant gives 12 verified, 0
        errors, so Verus alone does *not* catch it;
      * **the twin must be `#[cfg(slb_twin)]`**, which is a cfg no build ever
        sets. rustc strips it before codegen, so the mechanism costs zero
        instructions *structurally* rather than by hope, and the pinned
        obligation count does not move (p02 stays at 9; the twin run reports
        12);
      * **the twin body may not contain** `unsafe`, `assume`, `admit`,
        `assume_specification` or `external`, and may not call any
        `external_body` item in the file. Each of those would let the twin
        inherit the axiom it is supposed to be an independent check on;
      * **a trusted `unsafe` item with no twin is a failure**, with the usual
        expensive escape hatch: `verus.twin_justifications`, shouted every run.

    What this does NOT establish: that the twin is the right stand-in for the
    unchecked operation. That is the declared half, and it is declared *as code
    Verus checks* rather than as a number the author asserts -- which is why it
    is legitimate under `.memory/02-bench-rules.md`'s "a declared pin is
    acceptable only for something a reviewer can check by reading `spec.md`
    alone": `get_unchecked` <-> `v[i]` is exactly that judgement, and the
    contract half is lifted from the source, so the two cannot drift.

    Nor does a twin *failure* prove weakness on its own: it can also mean the
    checked equivalent needs a spec vstd does not ship. The two are told apart
    by Verus's own diagnostic, which the stage prints in full -- `precondition
    not met`/`postcondition not satisfied` is weakness, `no method named` /
    `cannot find function` is a missing spec."""
    head("5c-twin. verified twin: does the trusted `requires` license the "
         "operation?")
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    justif = vcfg.get("twin_justifications") or {}
    out = {}
    if not enabled:
        rep.fail("twin", "--no-verus-mutants given: the verified-twin stage did "
                         "not run, so nothing checked that this pattern's "
                         "trusted preconditions are strong enough to license "
                         "the operations they stand for")
        return out
    if not pinned_obl:
        rep.fail("twin", "spec.md pins no verus.obligations, so there is no "
                         "file list to check twins in")
        return out
    pinned_twin_obl = vcfg.get("twin_obligations") or {}
    justified, n_trusted, trusted_by_src = [], 0, {}
    for src in sorted(pinned_obl):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        try:
            items = vparse.by_name(txt)
        except ValueError as e:
            rep.fail("twin", f"{src}: {e}")
            continue
        _check_twin_cfg_hygiene(rep, src, txt, items,
                                _path_includes(pdir, [src]))
        trusted = [i for i in items.values() if _is_trusted(i)]
        ext_names = {i.name for i in items.values() if i.external}
        if not trusted:
            # TASK_055_REVIEW. This was a bare `print` followed by `continue`,
            # so the stage emitted no ok/fail/shout AND never set out[src] --
            # the file vanished from the gate record entirely. That is SILENCE,
            # not a verdict, and it is exactly the silence a legitimate
            # `vstd::raw_ptr` pattern would produce, where no rung has a
            # project-local trusted item at all: the reviewer measured that a
            # zero-trusted-item file and TASK_009_REVIEW's macro bypass are
            # indistinguishable here. A shout does not make them
            # distinguishable -- see `.memory/04-verus.md` -- but it stops the
            # gate reporting nothing at all, and it puts the file in the record
            # so the omission is checkable from outside.
            # Blast radius when landed: ONE file, p01's `safe_naive_verus.rs`.
            ext = sorted(i.name for i in items.values() if i.external)
            rep.shout("twin", f"{src}: no trusted item with an `ensures` or an "
                              f"`unsafe` body (`_is_trusted`), so no twin is "
                              f"required and NOTHING in this stage checked this "
                              f"file. external_body items: {ext}")
            out[src] = {"twins": [], "verified": None, "errors": None,
                        "no_trusted_item": True, "external_body_items": ext}
            continue
        n_trusted += len(trusted)
        trusted_by_src[src] = [t.name for t in trusted]
        rows, ok_here = [], True
        for t in trusted:
            twin = items.get(TWIN_PREFIX + t.name)
            why = (justif.get(src) or {}).get(t.name)
            if twin is None:
                ok_here = False
                if why:
                    justified.append(f"{src}:{t.name}")
                    # A shout is not enough on its own: TASK_009_REVIEW's x3
                    # shipped BOTH known off-by-one weakenings with both twins
                    # deleted and two `"see NOTES.md"` justifications, and the
                    # gate printed `PASS  failures 0  loud 3`. `rep.block`
                    # additionally forces the verdict to
                    # PASS-WITH-BLOCKED-ROWS, which is what an unchecked
                    # trusted precondition actually is: a row nothing verified.
                    rep.block("twin", f"{src} `{t.name}` (strength unchecked)",
                              f"trusted item `{t.name}` has NO verified twin "
                              f"`{TWIN_PREFIX}{t.name}`, so its `requires` "
                              f"{_clauses(t, 'requires')} was never tested for "
                              f"STRENGTH -- only for triviality (5c-req) and "
                              f"parameter mention (5a), both of which "
                              f"`i <= v@.len()` passes. spec.md justifies it: "
                              f"{why}")
                    rep.shout("twin",
                              f"{src}:{t.line} trusted item "
                              f"`{t.name}` has NO verified twin "
                              f"`{TWIN_PREFIX}{t.name}`. spec.md justifies it: "
                              f"{why}")
                else:
                    rep.fail("twin",
                             f"{src}:{t.line} trusted item `{t.name}` "
                             f"({t.external}, ensures={_clauses(t, 'ensures')}) "
                             f"has no verified twin. Nothing then checks that "
                             f"its `requires` {_clauses(t, 'requires')} is "
                             f"strong enough to license the unchecked "
                             f"operation its body performs -- only that the "
                             f"clause is non-trivial and mentions every "
                             f"parameter, which `i <= v@.len()` also is and "
                             f"does. Add `#[cfg({TWIN_CFG})] fn "
                             f"{TWIN_PREFIX}{t.name}` with the same signature "
                             f"and a checked body, or declare "
                             f"verus.twin_justifications[{src!r}][{t.name!r}] "
                             f"in spec.md -- which the gate then shouts every "
                             f"run.")
                continue
            probs = []
            if twin.external:
                probs.append(f"it is {twin.external}, so Verus never checks its "
                             f"body and it re-states the axiom instead of "
                             f"testing it")
            if not twin.in_verus:
                probs.append("it is outside `verus! {}`")
            if not any(re.fullmatch(r"#!?\[\s*cfg\s*\(\s*" + TWIN_CFG +
                                    r"\s*\)\s*\]", a.strip()) for a in twin.attrs):
                probs.append(f"it is not `#[cfg({TWIN_CFG})]`, so it would be "
                             f"compiled into the measured binaries -- the twin "
                             f"must cost zero instructions structurally, not by "
                             f"hope")
            gs, ts = vparse.norm_clause(twin.sig), vparse.norm_clause(t.sig)
            if gs != ts:
                probs.append(f"its signature is not the trusted item's:\n"
                             f"        twin:    {gs}\n"
                             f"        trusted: {ts}\n"
                             f"      A twin with its own contract is a second "
                             f"declaration, not a check: weakening the trusted "
                             f"`requires` and leaving the twin alone verifies "
                             f"cleanly (measured, 12 verified / 0 errors)")
            bcode = vparse.blank_noncode(twin.body or "")
            for w in _TWIN_BANNED:
                if re.search(r"\b" + w + r"\b", bcode):
                    probs.append(f"its body contains `{w}`, which would let it "
                                 f"inherit the very axiom it exists to check")
            called = sorted(n for n in ext_names
                            if re.search(r"\b" + re.escape(n) + r"\s*\(", bcode))
            if called:
                probs.append(f"its body calls the trusted item(s) {called}, so "
                             f"it re-uses the axiom instead of re-deriving it")
            if probs:
                ok_here = False
                rep.fail("twin", f"{src}:{twin.line} `{twin.name}` is not a "
                                 f"usable twin for `{t.name}`: "
                         + "; ".join(probs))
            rows.append(dict(trusted=t.name, twin=twin.name,
                             signature_identical=gs == ts,
                             requires=_clauses(t, "requires"),
                             ensures=_clauses(t, "ensures"),
                             body_lines=twin.body_lines))
        if not ok_here:
            out[src] = {"twins": rows, "verified": None, "errors": None}
            continue
        base_v, base_e, _ = _verus(path)
        tv, te, to = _verus(path, "--cfg", TWIN_CFG)
        out[src] = {"twins": rows, "verified": tv, "errors": te,
                    "without_twins": base_v}
        if tv is None or te:
            rep.fail("twin",
                     f"{src}: with `--cfg {TWIN_CFG}` Verus reports {tv} "
                     f"verified, {te} errors ({base_v} verified without the "
                     f"twins). At least one trusted precondition is not strong "
                     f"enough to license the checked equivalent of the "
                     f"operation its body performs -- or the checked "
                     f"equivalent needs a spec vstd does not ship, which the "
                     f"diagnostic below distinguishes (`precondition not met` / "
                     f"`postcondition not satisfied` is weakness; `cannot find` "
                     f"/ `no method named` is a missing spec).\n"
                     f"      {(to or '')[-900:]}")
        elif base_v is not None and tv <= base_v:
            rep.fail("twin",
                     f"{src}: `--cfg {TWIN_CFG}` reports {tv} verified, which "
                     f"is not more than the {base_v} verified without it, so "
                     f"the twins were not compiled at all and this stage "
                     f"checked nothing.")
        elif src not in pinned_twin_obl:
            # `tv > base_v` only says *something* extra was compiled. The twin
            # configuration is a second configuration of the same file and it
            # gets the same treatment as the shipped one: a pinned obligation
            # count, so that a twin quietly losing its loop body, or an extra
            # item appearing only under `--cfg slb_twin`, moves a number a
            # reviewer can read in `spec.md` (TASK_009_REVIEW blocker x2, second
            # half).
            rep.fail("twin",
                     f"{src}: spec.md pins verus.obligations={pinned_obl[src]} "
                     f"for the shipped configuration but no "
                     f"verus.twin_obligations for the `--cfg {TWIN_CFG}` one, "
                     f"which is where the twins are actually checked. This run "
                     f"measured {tv} verified / 0 errors with the cfg and "
                     f"{base_v} without; pin `\"twin_obligations\": {{{src!r}: "
                     f"{tv}}}` in the slb-contract block. Without it the only "
                     f"assertion about the twin configuration is `{tv} > "
                     f"{base_v}`.")
        elif tv != pinned_twin_obl[src]:
            rep.fail("twin",
                     f"{src}: `--cfg {TWIN_CFG}` reports {tv} verified, spec.md "
                     f"pins verus.twin_obligations={pinned_twin_obl[src]} "
                     f"({base_v} verified without the cfg, pinned "
                     f"{pinned_obl[src]}). One Verus query per function plus one "
                     f"per loop body: a twin that lost its loop, or an item that "
                     f"exists only in the twin configuration, moves this and "
                     f"nothing else does.")
        else:
            for r in rows:
                print(f"    {src}: `{r['twin']}` verifies against "
                      f"`{r['trusted']}`'s own contract "
                      f"(requires={r['requires']}) in {r['body_lines']} lines "
                      f"of checked code")
            print(f"    {src}: {tv} verified, 0 errors with `--cfg {TWIN_CFG}` "
                  f"-- matches the pinned verus.twin_obligations "
                  f"({base_v} without it, pinned {pinned_obl[src]}; the twins "
                  f"are cfg'd out of every build, so they cost zero "
                  f"instructions)")
            # --- the twin must NEED the precondition ------------------------
            #
            # The oracle above has teeth only in proportion to what the contract
            # says. A trusted item with a `requires` and **no `ensures`** -- which
            # `.memory/04-verus.md` recommends, because a trusted item that asserts
            # nothing cannot axiomatise a falsehood -- can be twinned by an *empty
            # body*, and an empty body verifies under any precondition whatever.
            # So: delete the twin's `requires` and re-run. If it still verifies,
            # the checked implementation never used the precondition and the twin
            # certifies nothing about it.
            #
            # This is the deletion oracle that does not exist for the trusted item
            # (deleting a trusted precondition only removes obligations from
            # callers, so nothing fails -- TASK_008). It exists here precisely
            # because the twin is *verified* code.
            #
            # **Per conjunct, not all-at-once** (TASK_009_REVIEW, from the code
            # rather than a mutant). The first version deleted *every* `requires`
            # clause of the twin and demanded one failure, so a twin that needs 1
            # of N clauses still reported that the implementation "genuinely
            # needs it" -- and the other N-1 clauses of the trusted item were
            # then unchecked for strength. p02 does not exhibit it (both of
            # `copy_bytes`'s clauses are load-bearing, measured below); a
            # multi-clause accessor would. The conjunct split is `vparse`'s, so
            # a clause carrying a top-level `==>`/`||`/quantifier is refused and
            # shouted rather than guessed at, exactly as in 5c.
            for t in trusted:
                twin = items.get(TWIN_PREFIX + t.name)
                if twin is None or not _clauses(twin, "requires"):
                    continue
                try:
                    cspans = vparse.conjunct_spans(twin, "requires")
                except ValueError as e:
                    rep.fail("twin", f"{src}: `{twin.name}` requires: {e}")
                    continue
                probes, needed = [], 0
                for ci, cs in enumerate(cspans):
                    if cs.get("refused"):
                        rep.shout("twin",
                                  f"{src}:{twin.line} `{twin.name}`'s "
                                  f"`requires[{ci}]` could not be split into "
                                  f"conjuncts ({cs['refused']}), so it is "
                                  f"deleted whole. A clause that is really "
                                  f"several obligations joined by an implication "
                                  f"is checked only as a unit.")
                    for ji in range(len(cs["spans"])):
                        mt = vparse.delete_conjunct(txt, twin, "requires", ci, ji)
                        mpath = _mutant_path(pdir, src)
                        open(mpath, "w").write(mt)
                        dv, de, do = _verus(mpath, "--cfg", TWIN_CFG)
                        open(mpath, "w").write(txt)
                        frag = vparse.norm_clause(
                            txt[cs["spans"][ji][0]:cs["spans"][ji][1]])
                        probes.append(dict(conjunct=frag, verified=dv, errors=de))
                        if dv is not None and de == 0:
                            rep.fail("twin",
                                     f"{src}:{twin.line} `{twin.name}` still "
                                     f"verifies with the single conjunct "
                                     f"`{frag}` DELETED from its `requires` "
                                     f"({dv} verified, 0 errors). The checked "
                                     f"implementation never used that conjunct, "
                                     f"so nothing tests whether `{t.name}`'s "
                                     f"matching clause is strong enough -- and "
                                     f"the all-at-once version of this probe "
                                     f"reported the whole `requires` "
                                     f"'genuinely needed' as long as ONE "
                                     f"conjunct was load-bearing. Give the twin "
                                     f"a body that performs the operation that "
                                     f"conjunct licenses, or drop the conjunct "
                                     f"from both.")
                        elif dv is None:
                            # `_verus` gives `(None, None)` when Verus emits no
                            # `N verified, M errors` line at all -- a parse
                            # error in the mutant, or any environmental
                            # no-verdict. Without this arm the `else` counted
                            # such a run as LOAD-BEARING and incremented the
                            # `load_bearing` counter that goes into the gate
                            # JSON. `delete_conjunct`'s own docstring names this
                            # symptom, and the 5c and 5c-req deletion loops both
                            # report it (TASK_053 F5). Latent today: no
                            # `vacuity_probe.per_conjunct` row in any committed
                            # record has a null `verified`.
                            rep.fail("twin",
                                     f"{src}:{twin.line} Verus produced no "
                                     f"result for the mutant that deletes "
                                     f"`{frag}` from `{twin.name}`'s "
                                     f"`requires`, so that conjunct was NOT "
                                     f"tested -- and this arm used to count it "
                                     f"as load-bearing.\n"
                                     f"      {(do or '')[-300:]}")
                        else:
                            needed += 1
                            print(f"    {src}: `{twin.name}` fails when the "
                                  f"conjunct `{frag}` alone is deleted from "
                                  f"`{t.name}`'s `requires` ({dv} verified, "
                                  f"{de} errors) -- the checked implementation "
                                  f"genuinely needs it")
                for r in rows:
                    if r["twin"] == twin.name:
                        r["vacuity_probe"] = {"per_conjunct": probes,
                                              "load_bearing": needed,
                                              "conjuncts": len(probes)}
    _check_trusted_arguments(rep, pdir, trusted_by_src)
    # --- the justification hatch is capped, and the OK line may not lie ------
    #
    # TASK_009_REVIEW x3: `verus.twin_justifications` was uncapped free text
    # nobody reads, and with BOTH twins deleted, BOTH known too-weak forms
    # shipped and two entries reading `"see NOTES.md"`, the gate printed
    #
    #     ok  0 verified twin(s): every trusted `unsafe` item's `requires` is
    #         strong enough ...
    #     check.py: PASS   failures 0   loud 3
    #
    # -- a green sentence asserting the property at **n = 0**. Two changes
    # survive: justifying away *every* trusted item is a hard failure (the hatch
    # has then become an off switch for the whole stage), and the OK line below
    # states its `n`, refuses to fire at `n == 0`, and refuses to fire at all if
    # anything was justified away. The third -- a numeric cap on how many items
    # may be justified away -- was deleted at TASK_007 as redundant with the
    # first; see the comment where `MAX_TWIN_JUSTIFICATIONS` used to be defined.
    n_twins = sum(len(v["twins"]) for v in out.values())
    if justified:
        if n_twins == 0:
            rep.fail("twin",
                     f"every trusted item in this pattern "
                     f"({sorted(justified)}) is excused by "
                     f"verus.twin_justifications, so stage 5c-twin checked the "
                     f"strength of NOTHING. A hatch that can be applied to the "
                     f"whole of its own stage is an off switch, and the stage "
                     f"used to print `0 verified twin(s): every trusted "
                     f"`unsafe` item's `requires` is strong enough ...` in that "
                     f"configuration.")
    if out and n_twins and not justified and not any(
            f[0] == "twin" for f in rep.failures):
        rep.ok(f"{n_twins} verified twin(s) for {n_trusted} trusted item(s), "
               f"n={n_twins} > 0 and none justified away: every trusted item's "
               f"`requires` is strong enough to license a *checked* "
               f"implementation of the same contract. This is the only stage "
               f"that judges STRENGTH rather than triviality -- 5a and 5c-req "
               f"both pass `i <= v@.len()`. The twins are "
               f"`#[cfg({TWIN_CFG})]`, so no build compiles them. What it does "
               f"NOT judge: whether the trusted `ensures` is COMPLETE with "
               f"respect to every unchecked operation the trusted body performs "
               f"-- a body that also reads `i + 1` passes every stage here, and "
               f"the backstops are stage 3c identity and step 8 Miri.")
    elif out and not any(f[0] == "twin" for f in rep.failures):
        rep.shout("twin",
                  f"stage 5c-twin ran but certified {n_twins} twin(s) for "
                  f"{n_trusted} trusted item(s), with {len(justified)} justified "
                  f"away ({sorted(justified)}). No strength claim is being made "
                  f"about the justified ones.")
    return out


def translate_clause(text, table):
    """One Verus clause -> one Python expression, through `table`.

    Keys are applied longest-first so `v@.len()` beats `v@`. An identifier-
    shaped key is replaced on word boundaries; anything else is a literal
    substring. Deliberately dumb: the table has to be *readable*, because it is
    the reviewed artefact that makes the two transcriptions one."""
    for k in sorted(table, key=len, reverse=True):
        v = table[k]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k):
            text = re.sub(r"\b" + re.escape(k) + r"\b", v, text)
        else:
            text = text.replace(k, v)
    return re.sub(r"\s+", " ", text).strip()


def derive_contract(pdir, rep, contract):
    """TASK_005 A2: `requires`/`ensures` generated from `verus.rs`, not
    transcribed beside it.

    `contract["requires"]` (Python, evaluated against `model.py`'s bindings) and
    `verus.items[...]["requires"]` (Verus text, diffed against the source) were
    two independent transcriptions of one predicate, and **nothing checked they
    corresponded**. A pattern could therefore weaken the predicate the proof
    discharges while the gate went on evaluating the strong one over every
    input, printing `requires holds on all 200000 kernel calls` about a
    precondition the proof no longer has.

    So there is now one source: the clause text `vparse` reads out of
    `verus.rs`, pushed through a declared translation table. The table is a pin,
    but it is the *right kind* of pin -- a reviewer checks it by reading
    `spec.md` alone, without reference to the code it constrains.

    Returns (requires, ensures) as Python expression strings."""
    head("5d0. the Python contract is derived from verus.rs, not transcribed")
    vcfg = contract.get("verus") or {}
    table = vcfg.get("translate")
    kname = vcfg.get("kernel_item", "kernel")
    src = os.path.join(pdir, "verus.rs")
    if table is None:
        rep.fail("contract-source",
                 "spec.md declares no `verus.translate` table, so "
                 "contract.requires/ensures are an unchecked second "
                 "transcription of the Verus clauses (TASK_005 A2)")
        return contract.get("requires") or [], contract.get("ensures") or []
    if not os.path.exists(src):
        rep.fail("contract-source", "no verus.rs to derive the contract from")
        return contract.get("requires") or [], contract.get("ensures") or []
    try:
        items = vparse.by_name(open(src).read())
    except ValueError as e:
        rep.fail("contract-source", str(e))
        return contract.get("requires") or [], contract.get("ensures") or []
    it = items.get(kname)
    if it is None:
        rep.fail("contract-source", f"verus.rs has no `fn {kname}`")
        return contract.get("requires") or [], contract.get("ensures") or []

    derived = {}
    for kw in ("requires", "ensures"):
        got = []
        for clause in _clauses(it, kw):
            py = translate_clause(clause, table)
            try:
                compile(py, "<derived>", "eval")
            except SyntaxError as e:
                rep.fail("contract-source",
                         f"{kw} {clause!r} translates to {py!r}, which is not a "
                         f"Python expression ({e.msg}) -- fix verus.translate")
                py = None
            if py is not None:
                got.append(py)
            print(f"    {kw:9s} verus: {clause}")
            print(f"    {'':9s}   ->   {py}")
        derived[kw] = got
        want = contract.get(kw)
        if want is not None and [vparse.norm_clause(w) for w in want] != got:
            rep.fail("contract-source",
                     f"spec.md's contract.{kw} {want!r} is not what verus.rs's "
                     f"`{kname}` says under the declared translation table "
                     f"({got!r}). These are supposed to be one predicate.")
    if not any(f[0] == "contract-source" for f in rep.failures):
        rep.ok(f"contract.requires/ensures regenerated from verus.rs `{kname}` "
               f"through the {len(table)}-entry table in spec.md and identical "
               f"to the declared copy")
    return derived["requires"], derived["ensures"]


def check_proof_domain(rep, models, reqs, enss):
    """Rules 1 and 3, on **every** measured input.

    The previous version built its model set from the non-adversarial inputs
    only (B3). p01 hides that -- its adversarial inputs make zero kernel calls --
    but for the 47 downstream patterns the adversarial input is by construction
    the one aimed at the precondition, so it is precisely the input on which
    these rules must be evaluated.

    `reqs`/`enss` come from `derive_contract`, i.e. from `verus.rs` itself.

    Vacuity is a failure here, not evidence (TASK_003_REVIEW): an empty
    `requires` list used to print "holds on all 200000 kernel calls", and a
    model that yielded no samples printed "re-derived on 0 sampled calls". Both
    read as the strongest line in the log and neither checked anything."""
    head("5d. rules 1 and 3 on EVERY measured input, adversarial included")
    if not reqs:
        rep.fail("proof-vacuous",
                 "the kernel's `requires` is empty. Either the proof genuinely "
                 "demands nothing of its callers -- in which case say so in "
                 "spec.md and drop the clause from the pin deliberately -- or "
                 "the predicate was lost. An empty list evaluates true on every "
                 "call and used to print as the gate's strongest evidence.")
    if not enss:
        rep.fail("proof-vacuous",
                 "the kernel's `ensures` is empty, so nothing checks the "
                 "kernel computes what spec.md says it computes "
                 "(`.memory/02-bench-rules.md`: the security property lives in "
                 "the `ensures`)")
    stats = {}
    for name, mod in sorted(models.items()):
        if sbg(mod, "n_calls") == 0:
            print(f"    {name}: 0 kernel calls (degenerate shape) -- vacuously "
                  f"inside the domain")
            stats[name] = dict(calls=0, requires_ok=True, ensures_checked=0)
            continue
        bad_req, n = None, 0
        offs = []
        for env in sb_iter(mod.iter_calls()):
            n += 1
            if "off" in env:
                offs.append(env["off"])
            for expr in reqs:
                if not eval(expr, {"__builtins__": {}}, dict(env)):
                    bad_req = (expr, {k: v for k, v in env.items() if k != "v"})
                    break
            if bad_req:
                break
        if bad_req:
            rep.fail("proof-rule1", f"{name}: requires {bad_req[0]!r} violated at "
                                    f"{bad_req[1]}")
        elif reqs:
            rng = f", off {min(offs)}..{max(offs)}" if offs else ""
            rep.ok(f"{name}: `requires` {reqs} holds on all {n} kernel "
                   f"calls{rng}")
        # ensures, re-derived with the model's independent implementation
        sample = sb(mod.sample_calls, ENSURES_SAMPLE)
        bad_ens = None
        with model_sandbox():
            helpers = mod.helpers
            for env in sample:
                ns = dict(env)
                ns.update(helpers)
                for expr in enss:
                    if not eval(expr, {"__builtins__": {}}, ns):
                        bad_ens = (expr, {k: v for k, v in env.items() if k != "v"})
                        break
                if bad_ens:
                    break
        if bad_ens:
            rep.fail("proof-rule3", f"{name}: ensures {bad_ens[0]!r} violated at "
                                    f"{bad_ens[1]}")
        elif not sample:
            rep.fail("proof-vacuous",
                     f"{name}: {n} kernel calls but model.py's sample_calls() "
                     f"returned none, so `ensures` was re-derived on nothing. "
                     f"This printed as a green line.")
        elif enss:
            rep.ok(f"{name}: `ensures` re-derived independently on "
                   f"{len(sample)} sampled calls")
        stats[name] = dict(calls=n, requires_ok=bad_req is None,
                           ensures_checked=len(sample))
    # The same "green at n = 0" class one level up (TASK_010 C). Every input
    # being degenerate prints a `--` line per input and neither a failure nor an
    # `ok`, so the stage disappears from the verdict rather than objecting -- and
    # p01's adversarial inputs really are 0-call, so the shape is not
    # hypothetical, it is just not universal today.
    tot = sum(v["calls"] for v in stats.values())
    chk = sum(v["ensures_checked"] for v in stats.values())
    if stats and not tot:
        rep.fail("proof-vacuous",
                 f"all {len(stats)} measured input(s) make ZERO kernel calls, so "
                 f"rules 1 and 3 were evaluated on nothing at all. Every line "
                 f"this stage printed reads 'vacuously inside the domain'.")
    elif stats and not chk:
        rep.fail("proof-vacuous",
                 f"{tot} kernel call(s) across {len(stats)} input(s), but the "
                 f"`ensures` was re-derived on 0 of them.")
    elif stats:
        print(f"    totals: {tot} kernel call(s) across {len(stats)} input(s), "
              f"`requires` evaluated on all of them, `ensures` re-derived "
              f"independently on {chk}")
    return stats


# ==========================================================================
# 6. the driver loop
# ==========================================================================

def _verus_verified_files(pdir, rep, contract, verus_res):
    """Which `.rs` files did **Verus** compile and verify, this run?

    TASK_006_REVIEW's blocker A. `harness/dloop.py` strips ghost statements
    inside a `verus!` span, which is sound only if the span is Verus's. A rung
    that writes

        macro_rules! verus { ($($t:tt)*) => { $($t)* } }
        verus!( fn main() { ... SLB-DRIVER-BEGIN ... } );

    got the harbour for free: `vparse.verus_span` accepts
    `verus!\\s*[{(\\[]` and the guard in stage 5a matched `verus!\\s*\\{` only,
    so the round bracket was the whole bypass -- +5.0 Ir/call of `_mm_prefetch`
    in `safe_naive.rs`'s measured loop, unchanged checksums, and a `contract
    sha256` identical to the shipped pattern.

    The answer is not a fourth regex over the source (the tree already contains
    the third, and it did not generalise). It is Verus's own verdict, which this
    gate already has:

      * the file is in `spec.md`'s `verus.obligations`, so stage 5a ran
        `verus_run.py` on it and got `N verified, 0 errors` back;
      * **and** `verus --verify-function <the item enclosing the region>`
        reports a verified body for that item, so the answer is about the code
        being normalised rather than about the file in general.

    The second query is what makes this different in kind from the pin: an item
    Verus never compiled cannot report a verified body, whatever its file
    spells its macros. Returns the set of file names that earned the harbour.

    Three refusals, deliberately distinguished (TASK_008_REVIEW, major E):
    **duplicate name** (the query cannot be trusted to name the right item),
    **unresolvable name** (Verus cannot find it -- the file may verify
    perfectly; a mod-nested driver used to land here and be reported as having
    no verified body, which was false), and **no verified body** (Verus found
    it and it has none). `_verify_function` asks a mod-nested item with
    `--verify-only-module`, so the second case is now rare rather than
    routine."""
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    ok = set()
    for src in sorted(pinned_obl):
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        # The duplicate-name failure is the only thing standing between this
        # certificate and the wrong item.
        #
        # ⚠ **THE REASON WRITTEN HERE UNTIL TASK_077 WAS REFUTED BY RE-RUNNING
        # IT.** It said *"Verus itself does NOT object to two items sharing a
        # name (`S::drive` and `inner::drive` -> `--verify-function drive`
        # silently reports `1 verified`, measured at TASK_008_REVIEW)"*. At the
        # PINNED Verus (0.2026.08.09.92f466f) it objects loudly. The probe is
        # ten lines -- a `verus!` block with `trait Op { fn apply(..); }` and
        # two `impl Op for {A,B}`, each defining `apply` and `spec_apply`:
        #
        #   $ ./verus_run.py dupname.rs --verify-root --verify-function apply
        #   error: more than one match found for --verify-function apply,
        #          consider using wildcard *apply* ... matched results are:
        #            - A::apply
        #            - A::spec_apply
        #            - B::apply    ...
        #   $ ./verus_run.py dupname.rs --verify-root --verify-function A::apply
        #   verification results:: 1 verified, 0 errors (partial verification)
        #
        # So the query resolves fine given a name that identifies ONE item, and
        # matching is by SUBSTRING over the qualified path. That is why the
        # refusal is now scoped to duplicates that qualification cannot
        # separate, and why the name handed to `--verify-function` below is
        # `vparse.unique_names`' label -- bare wherever it is unambiguous,
        # which is every pattern in the tree today, and `Type::name` where it
        # is not (TASK_077, RECAP "Owed" 20).
        #
        # It is checked FIRST and named explicitly, so the refusal is
        # attributed to the duplicate rather than to the generic "no verified
        # body" text below.
        #
        # ⚠ **IT IS NOT THE WHOLE OF THE AMBIGUITY, and TASK_077's comment read
        # as if it were** (TASK_077_REVIEW M5). The refusal fires only on
        # duplicates qualification cannot separate. Verus matches by SUBSTRING,
        # so `apply` is ambiguous against `spec_apply` in the same impl -- two
        # DIFFERENT names, `duplicate_names(qualified=True)` returns `{}`, and
        # `unique_names` correctly hands back the bare `apply`. The `ambiguous`
        # answer from `_verify_function` is what covers that, in the branch
        # below.
        try:
            dup_items = vparse.parse(open(path).read())
            dup = vparse.duplicate_names(dup_items, qualified=True)
        except ValueError as e:
            rep.fail("driver", f"{src}: {e}")
            continue
        if dup:
            rep.fail("driver",
                     f"{src}: `{sorted(dup)}` defined more than once with "
                     f"nothing to tell them apart -- same module, same impl -- "
                     f"so `--verify-function` cannot be given a name that "
                     f"identifies the item enclosing the driver region. "
                     f"(Verus matches by substring over the qualified path and "
                     f"errors on more than one match, so it will not pick "
                     f"either; the gate refuses first so the reason is stated "
                     f"rather than inferred from an aborted run.) No harbour "
                     f"certificate issued.")
            continue
        r = verus_res.get(src) or {}
        if r.get("errors") or not r.get("verified"):
            continue
        txt = open(path).read()
        try:
            sp = dloop.region_span(txt, src)
        except dloop.RegionError:
            continue
        if sp is None or not dloop.region_in_verus(txt, src):
            continue
        # Which item encloses the region? Ask Verus whether *that* item has a
        # verified body -- `--verify-function` reports 0 for anything Verus did
        # not compile as verified code.
        try:
            items = vparse.parse(txt)
        except ValueError as e:
            rep.fail("driver", f"{src}: {e}")
            continue
        inner = [i for i in items
                 if i.body_start is not None and i.body_end is not None
                 and i.body_start <= sp[0] and sp[1] <= i.body_end]
        if not inner:
            continue
        it = max(inner, key=lambda i: i.body_start)
        # The label `--verify-function` is given: the bare name wherever it
        # identifies one item, `Type::name` where it does not. On every pattern
        # in the tree today this is `it.name` unchanged (TASK_077).
        try:
            labels = {id(v): k for k, v in vparse.unique_names(items).items()}
        except ValueError as e:
            rep.fail("driver", f"{src}: {e}")
            continue
        name = labels.get(id(it), it.name)
        nv, ne, out, resolved, ambiguous = _verify_function(
            path, name, it.mod_path or "")
        q = (f"--verify-only-module {it.mod_path} --verify-function {name}"
             if it.mod_path else f"--verify-function {name} --verify-root")
        if nv and not ne:
            ok.add(src)
            print(f"    {src}: `fn {name}` encloses the driver region and Verus "
                  f"reports {nv} verified for it -- ghost stripping licensed")
        elif ambiguous:
            # TASK_078 / TASK_077_REVIEW M5. THE THIRD ANSWER, and the one the
            # duplicate refusal above does NOT cover: Verus matches by
            # substring, so `apply` is ambiguous against `spec_apply` in the
            # SAME impl -- two different names, no duplicate at all, and
            # `vparse.unique_names` correctly hands back the bare `apply`.
            # Measured at the pinned Verus: `.temp/p78/vprobe/subambig.log`.
            rep.fail("driver",
                     f"{src}: the driver region is inside `fn {name}`, and "
                     f"`verus {q}` is AMBIGUOUS -- Verus matches "
                     f"`--verify-function` by SUBSTRING over the qualified "
                     f"path, more than one item matched, and it refused to "
                     f"pick. No certificate is issued, and the reason is that "
                     f"the gate could not ask the question -- not that the item "
                     f"has no verified body. Rename the enclosing item so its "
                     f"name is not a proper substring of another item's (a "
                     f"`spec_` twin of the same base name is the usual "
                     f"cause).\n      {(out or '')[-300:]}")
        elif not resolved:
            rep.fail("driver",
                     f"{src}: the driver region is inside `fn {name}`"
                     + (f" (module `{it.mod_path}`)" if it.mod_path else "")
                     + f", and Verus could not RESOLVE that name: `verus {q}` "
                       f"says the function does not exist. This is not the same "
                       f"answer as 'the item has no verified body' -- the file "
                       f"may verify perfectly well -- so no certificate is "
                       f"issued and the reason is that the gate could not ask "
                       f"the question. Move the region into an item "
                       f"`--verify-function` can name, or teach "
                       f"`_verify_function` the query that "
                       f"reaches it.\n      {(out or '')[-300:]}")
        else:
            rep.fail("driver",
                     f"{src}: the driver region is inside `fn {name}`, which "
                     f"claims a `verus!` span, but `verus {q}` reports "
                     f"{nv} verified / {ne} errors -- Verus resolved the item "
                     f"and has no verified body for it. Ghost statements are "
                     f"stripped from the driver diff only for code Verus "
                     f"actually verified.\n      {(out or '')[-300:]}")
    return ok


_TOK_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\S")

# Identifier-shaped tokens that may legitimately sit immediately before a call.
# Anything *else* identifier-shaped before `kernel(` is a return type or `fn`,
# i.e. a definition or a prototype, not a call.
_CALL_KEYWORDS = {"return", "in", "else", "as", "await", "yield", "and", "or",
                  "not", "sizeof"}


def _kernel_calls(code, kname):
    """Offsets of every *call* to `kname` in comment-blanked `code`.

    Language-neutral by design: it has to work on `c/main.c` and on four Rust
    rungs, and the thing being counted is the same in both. A definition
    (`fn kernel(`, `uint64_t kernel(`) or a prototype has an identifier-shaped
    token immediately before the name; a call has `=`, `(`, `,`, `;`, an
    operator, or one of `_CALL_KEYWORDS`."""
    out = []
    for m in re.finditer(r"\b" + re.escape(kname) + r"\s*\(", code):
        toks = _TOK_RE.findall(code[:m.start()])
        prev = toks[-1] if toks else ""
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", prev) and prev not in _CALL_KEYWORDS:
            continue                        # `fn kernel(` / `uint64_t kernel(`
        out.append(m.start())
    return out


def _check_region_executes(pdir, rep, contract, files):
    """The pinned region must be **the code the benchmark runs**.

    `.memory/02-bench-rules.md`, "Open gaps in the driver diff": `driver.regions`
    pins a *file*, never the code that executes, and that is the sixth
    demonstrated bypass -- in **both** languages, one mechanism rather than two.
    Move a rung's `SLB-DRIVER` markers into a dead decoy function whose body is
    the canonical loop verbatim, leave the real loop unmarked, and put a payload
    in it:

      * `safe_naive.rs` + `_mm_prefetch` (TASK_009): full gate PASS, stage 6
        reporting all five loops match the pin, marginal Ir O0 6838 -> 6852;
      * `c/main.c` + `__builtin_prefetch` (TASK_009_REVIEW): full gate PASS,
        `prefetch` in three C cells' disassembly, **all 32 C cells moved
        +1...+6 Ir/call while all four Rust rungs stayed put** -- a pure
        cross-language asymmetry, which is exactly what the
        anti-partial-evaluation rules forbid.

    The structural fix, and it catches both demonstrations: **the pinned kernel
    item may be called exactly once in each region-carrying source, and that
    call must be inside the region.** A decoy whose body is the canonical loop
    necessarily contains a second kernel call, and a real measured loop cannot
    avoid containing one -- the kernel *is* the pattern, so a driver that does
    not call it in the region is not the driver.

    It is a check on the source rather than on the binary, so it is not an
    operational definition of "executed" by itself; `_check_region_runs` is the
    dynamic half, and it is the one that measures. This half is what makes the
    dynamic half's question well posed, by fixing which function the region
    belongs to."""
    kname = (contract.get("verus") or {}).get("kernel_item", "kernel")
    for f in sorted(files):
        path = os.path.join(pdir, f)
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        code = vparse.blank_noncode(txt)
        try:
            sp = dloop.region_span(txt, f)
        except dloop.RegionError:
            continue                        # already failed in the caller
        if sp is None:
            continue
        calls = _kernel_calls(code, kname)
        inside = [o for o in calls if sp[0] <= o < sp[1]]
        lines = [txt.count("\n", 0, o) + 1 for o in calls]
        if len(calls) != 1 or not inside:
            rep.fail("driver",
                     f"{f}: {len(calls)} call(s) to the pinned kernel item "
                     f"`{kname}()` at line(s) {lines}, {len(inside)} of them "
                     f"inside the SLB-DRIVER region (lines "
                     f"{txt.count(chr(10), 0, sp[0]) + 1}-"
                     f"{txt.count(chr(10), 0, sp[1]) + 1}). Exactly one call is "
                     f"required, and it must be the one in the region. "
                     f"`driver.regions` pins a FILE, never the code that runs, "
                     f"and moving the markers into a dead decoy function whose "
                     f"body is the canonical loop -- while the real, unmarked "
                     f"loop carries a `__builtin_prefetch` -- passed the whole "
                     f"gate twice, on `safe_naive.rs` and on `c/main.c`. A decoy "
                     f"whose body is the canonical loop necessarily contains a "
                     f"second call to `{kname}`; a real measured loop cannot "
                     f"avoid containing one.")
        else:
            print(f"    {f}: the one call to `{kname}()` in this file is at "
                  f"line {lines[0]}, inside the pinned region "
                  f"({txt.count(chr(10), 0, sp[0]) + 1}-"
                  f"{txt.count(chr(10), 0, sp[1]) + 1})")


def _cg_parse(path):
    """`(names, callers, excl)` from one callgrind output file.

    `names[id] -> symbol`, `callers[id] -> {caller id}` from the `cfn=` edges
    callgrind records inside each `fn=` context, `excl[id] -> exclusive Ir`.
    Callgrind names a function once and refers to it by id afterwards, so the
    name table has to be built as the file is read."""
    names, callers, excl, cur = {}, {}, {}, None
    for line in open(path):
        line = line.rstrip("\n")
        m = re.match(r"^fn=\((\d+)\)\s*(.*)$", line)
        if m:
            if m.group(2).strip():
                names[m.group(1)] = m.group(2).strip()
            cur = m.group(1)
            continue
        m = re.match(r"^cfn=\((\d+)\)\s*(.*)$", line)
        if m:
            if m.group(2).strip():
                names[m.group(1)] = m.group(2).strip()
            callers.setdefault(m.group(1), set()).add(cur)
            continue
        if cur and line[:1].isdigit():
            p = line.split()
            if len(p) >= 2:
                try:
                    excl[cur] = excl.get(cur, 0) + int(p[1])
                except ValueError:
                    pass
    return names, callers, excl


def _enclosing_fn(txt, off, lang):
    """Name of the function whose body contains offset `off`.

    Rust goes through `vparse` (which knows about `verus!`, `impl` blocks and
    `mod`s). C walks the brace structure backwards to the outermost unmatched
    `{` and reads the identifier before the parameter list -- enough for a
    top-level function definition, which is the only shape a driver region can
    sit in."""
    if lang != "c":
        inner = [i for i in vparse.parse(txt)
                 if i.body_start is not None and i.body_end is not None
                 and i.body_start <= off < i.body_end]
        return max(inner, key=lambda i: i.body_start).name if inner else None
    code = vparse.blank_noncode(txt)
    opens, depth, i = [], 0, off
    while i > 0:
        i -= 1
        if code[i] == "}":
            depth += 1
        elif code[i] == "{":
            if depth:
                depth -= 1
            else:
                opens.append(i)
    if not opens:
        return None
    j = opens[-1] - 1
    while j >= 0 and code[j] in " \t\r\n":
        j -= 1
    if j < 0 or code[j] != ")":
        return None
    d = 0
    while j >= 0:
        if code[j] == ")":
            d += 1
        elif code[j] == "(":
            d -= 1
            if d == 0:
                break
        j -= 1
    k = j - 1
    while k >= 0 and code[k] in " \t\r\n":
        k -= 1
    m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", code[:k + 1])
    return m.group(1) if m else None


def _cg_name_matches(sym, want):
    """Does callgrind's symbol `sym` name the source-level function `want`?

    Rust mangles to `<crate>::main`; C emits `main`. The suffix form is
    deliberately narrow -- `::main` only, never a bare substring, so `slb_decoy`
    cannot be matched by `xslb_decoy`."""
    return sym == want or sym.endswith("::" + want)


def _check_region_runs(pdir, rep, contract, files, built, cg_files, probe):
    """The dynamic half of Part E: is the region's function **executed**, and is
    it the only thing that calls the kernel?

    `_check_region_executes` above is structural, and structural checks are read
    off the attacker's own text. This one is measured. `.memory/02-bench-rules.md`
    asked for exactly this: *"assert that the callers of the kernel symbol in the
    `isolated` build are exactly the region's enclosing function, and that that
    function has non-zero `Ir`. A dead decoy has zero -- that is an operational
    definition of 'executed', measured rather than declared, in the same spirit
    as the Miri cross-check."*

    It costs no extra runs: stage 3b already ran callgrind twice per cell for
    the marginal-`Ir` probe, and callgrind records caller->callee edges, so this
    re-reads profiles that are already on disk.

    `isolated` cells only. In `whole` mode the kernel is inlined on purpose, so
    there is no symbol and no edge to check -- which is also why the structural
    half is not redundant."""
    cmain = (contract.get("driver") or {}).get("c_source",
                                              os.path.join("c", "main.c"))
    kname = (contract.get("verus") or {}).get("kernel_item", "kernel")
    nm, n = probe
    want = {}
    for f in sorted(files):
        path = os.path.join(pdir, f)
        lang = "c" if f.endswith((".c", ".h")) else "rust"
        txt = open(path).read()
        try:
            sp = dloop.region_span(txt, f)
        except dloop.RegionError:
            continue
        if sp is None:
            continue
        fn = _enclosing_fn(txt, sp[0], lang)
        if fn is None:
            rep.fail("driver",
                     f"{f}: could not resolve the function enclosing the "
                     f"SLB-DRIVER region, so the gate cannot ask whether the "
                     f"region's code is the code that runs.")
            continue
        want[f] = fn
    checked, ran = 0, set()
    n_kernel_syms, n_caller_edges = 0, 0
    for (c, o, m), binp in sorted(built.items()):
        if m != "isolated" or not binp:
            continue
        src = buildmod.RUST_SRC.get(c, cmain)
        fn = want.get(src)
        if fn is None:
            continue
        cgp = cg_files.get((c, o, m, nm, n))
        if not cgp or not os.path.exists(cgp):
            rep.fail("driver",
                     f"{c} {o} {m}: no callgrind profile at {cgp} -- stage 6's "
                     f"dynamic half cannot run, so nothing measured whether the "
                     f"pinned region is the code that executes.")
            continue
        names, callers, excl = _cg_parse(cgp)
        host = [i for i, s in names.items() if _cg_name_matches(s, fn)]
        ir = sum(excl.get(i, 0) for i in host)
        # The kernel *function*, not everything whose mangled name contains it.
        # `measure.py`'s row matcher is `(?:^|::)kernel(?:$|\W)`, which also
        # matches `safe_tuned::kernel::{closure#0}` -- and at O0 that closure is
        # called from `Iterator::fold` and from `kernel` itself, so a caller-set
        # assertion written with that regex false-fails on a perfectly healthy
        # cell (measured on p02 safe_tuned O0 isolated). An anchored match is
        # what "the kernel symbol" means here.
        kids = [i for i, s in names.items()
                if re.fullmatch(r"(?:.*::)?" + re.escape(kname), s)]
        callers_of_k = sorted({names.get(x, x) for k in kids
                               for x in callers.get(k, ())})
        bad = [s for s in callers_of_k if not _cg_name_matches(s, fn)]
        if not host or ir == 0:
            rep.fail("driver",
                     f"{c} {o} {m} on {nm}: `{src}`'s SLB-DRIVER region sits in "
                     f"`{fn}`, which executed **{ir} instructions** in this run "
                     f"({'no such symbol in the profile' if not host else 'zero exclusive Ir'}). "
                     f"The pinned region is therefore not the code the benchmark "
                     f"runs. This is the decoy-region bypass measured rather "
                     f"than argued: markers moved into a dead "
                     f"`static void slb_decoy(void)` whose body is the canonical "
                     f"loop, the real loop left unmarked with a "
                     f"`__builtin_prefetch` in it, full gate PASS and all 32 C "
                     f"cells +1..+6 Ir/call while the Rust rungs stood still.")
        elif not kids or not callers_of_k:
            # TASK_010_REVIEW / TASK_007 Part 0.1. Without this arm `kids == []`
            # makes `callers_of_k` and `bad` empty too, the cell is counted as
            # CHECKED, and the OK line below announces that `fn` "is the only
            # caller of the `kernel` symbol" -- over a set with no members. That
            # is the fifth instance of the rule TASK_010 itself promoted (a
            # count-bearing `rep.ok` must state its `n` and must never fire at
            # `n == 0`), and it silences precisely the limb added to catch a live
            # decoy. Reproduced in `.temp/review010/cgvac.py` by renaming the
            # symbol to `kernel.constprop.0` -- the shape of a gcc IPA clone --
            # which gave `failures=0 shouts=0` and an identical green line.
            #
            # `callers_of_k == []` with `kids` non-empty is the same vacuity one
            # step later (the symbol is in the profile but callgrind recorded no
            # edge into it), so both are refused here rather than one.
            rep.fail("driver",
                     f"{c} {o} {m} on {nm}: "
                     + (f"no callgrind symbol fullmatches the pinned kernel item "
                        f"`{kname}`"
                        if not kids else
                        f"the `{kname}` symbol is in the profile but callgrind "
                        f"recorded no caller edge into it")
                     + f" in an **isolated** build, where "
                       f"`#[inline(never)]`/`SLB_NOINLINE` is supposed to keep "
                       f"the kernel as its own called symbol. The 'only caller' "
                       f"assertion would therefore have been made over an empty "
                       f"set and passed vacuously (n=0). Causes to check, in "
                       f"order: the compiler cloned or renamed it (gcc "
                       f"`{kname}.constprop.0`/`.isra.0`, LLVM `.llvm.<hash>`), "
                       f"`verus.kernel_item` names something the binary does not "
                       f"contain, or the kernel was inlined away despite the "
                       f"isolated flags. Symbols in this profile whose name "
                       f"contains `{kname}`: "
                       f"{sorted({s for s in names.values() if kname in s})[:8]}")
        elif bad:
            rep.fail("driver",
                     f"{c} {o} {m} on {nm}: the kernel symbol is called from "
                     f"{callers_of_k}, but `{src}`'s SLB-DRIVER region is inside "
                     f"`{fn}`. The diffed loop is not the loop that calls the "
                     f"kernel, so what stage 6 compared against the pin is not "
                     f"what ran.")
        else:
            checked += 1
            n_kernel_syms += len(kids)
            n_caller_edges += len(callers_of_k)
            ran.add(f"{src}:{fn}")
    if checked:
        print(f"    dynamic: in {checked} isolated cell(s) on {nm} "
              f"(n_iters={n}), the function enclosing the region "
              f"({sorted(ran)}) has non-zero exclusive Ir and is the only "
              f"caller of the `{kname}` symbol -- 'executed' measured from "
              f"callgrind's own caller->callee edges, not declared. "
              f"n={n_kernel_syms} matching kernel symbol(s) over those cells "
              f"and {n_caller_edges} caller edge(s) into them; a cell where "
              f"either is 0 now FAILS rather than passing this line vacuously")
    elif built:
        rep.shout("driver",
                  "stage 6's dynamic half checked no cell: no isolated-mode "
                  "callgrind profile matched a region-carrying source, so "
                  "nothing measured that the pinned region is the code that "
                  "runs.")


def check_driver_identity(pdir, rep, contract, verus_ok=frozenset(),
                          built=None, cg_files=None, cg_probe=None):
    head("6. every driver loop matches the token sequence pinned in spec.md")
    cfg = contract.get("driver") or {}
    canon = cfg.get("canonical")
    if not canon:
        rep.fail("driver", "spec.md pins no `driver.canonical` token sequence -- "
                           "generate one with `harness/dloop.py <rung>.rs` and "
                           "paste it into the slb-contract block")
        return {}
    ref = "\n".join(canon)
    aliases = cfg.get("aliases") or {}
    for lang, table in sorted(aliases.items()):
        for p in dloop.validate_aliases(table, f"spec.md driver.aliases.{lang}"):
            rep.fail("driver", p)
    # `driver.call_args` -- which argument positions of a named call are the
    # canonical ones, per language. Needed as soon as a pattern's C kernel takes
    # the slice lengths Rust carries inside `&[T]` (p02:
    # `kernel(src, src_len, src_off, dst, dst_cap)` vs `kernel(src, src_off,
    # dst)`), which no alias can express. Printed in the log every run, because
    # it is a pin a reviewer has to read against the C source.
    call_args = cfg.get("call_args") or {}
    for lang, table in sorted(call_args.items()):
        for p in dloop.validate_call_args(table, f"spec.md driver.call_args.{lang}"):
            rep.fail("driver", p)
        for fn, keep in sorted(table.items()):
            print(f"    call_args[{lang}] {fn}(): canonical arguments are at "
                  f"positions {keep}; every other argument of that call must be "
                  f"a bare name and is dropped before the diff")
    # The *set* of files that must carry a region is pinned. Without it,
    # deleting the two marker comments makes a rung vanish from the diff
    # silently -- the old code only required that >= 2 regions were found
    # anywhere (TASK_003_REVIEW).
    want_files = cfg.get("regions")
    if not want_files:
        rep.fail("driver", "spec.md pins no `driver.regions` -- the set of "
                           "files that must carry an SLB-DRIVER region. Without "
                           "it a rung drops out of the diff by deleting two "
                           "comments and nothing objects.")
        return {}
    found, seen_files = {}, []
    cmain = cfg.get("c_source", os.path.join("c", "main.c"))
    candidates = [f for f in sorted(os.listdir(pdir)) if f.endswith(".rs")]
    candidates.append(cmain)
    for f in candidates:
        path = os.path.join(pdir, f)
        lang = "c" if f.endswith((".c", ".h")) else "rust"
        if not os.path.exists(path):
            if f in want_files:
                rep.fail("driver", f"{f} is pinned in driver.regions but is not "
                                   f"in the tree")
            continue
        try:
            r = dloop.normalise_file(path, lang, aliases.get(lang),
                                     call_args.get(lang),
                                     verus_verified=(f in verus_ok))
        except dloop.GhostHarbourError as e:
            rep.fail("driver", str(e))
            seen_files.append(f)
            continue
        except dloop.RegionError as e:
            rep.fail("driver", str(e))
            seen_files.append(f)
            continue
        except ValueError as e:
            rep.fail("driver", f"{f}: {e}")
            continue
        if r is not None:
            found[f] = r
            seen_files.append(f)
    got, want = set(seen_files), set(want_files)
    if got != want:
        rep.fail("driver",
                 f"the set of files carrying an SLB-DRIVER region is "
                 f"{sorted(got)}, spec.md pins {sorted(want)} "
                 f"(missing={sorted(want - got)} unexpected={sorted(got - want)})")
    if len(found) < 2:
        rep.fail("driver", "fewer than two driver regions found")
        return {}
    _check_region_executes(pdir, rep, contract, found)
    if cg_files and cg_probe:
        _check_region_runs(pdir, rep, contract, found, built or {}, cg_files,
                           cg_probe)
    else:
        rep.shout("driver",
                  "no callgrind profiles were available, so stage 6's DYNAMIC "
                  "half did not run: nothing measured that the region's "
                  "enclosing function executed and is the kernel's only caller. "
                  "Only the structural one-call-inside-the-region rule ran.")
    want_stmts = cfg.get("statements")
    out = {}
    for name, body in sorted(found.items()):
        n = dloop.statement_count(body)
        out[name] = {"statements": n, "matches_pin": body == ref}
        if body != ref:
            d = "\n".join(difflib.unified_diff(
                ref.splitlines(), body.splitlines(),
                "spec.md:driver.canonical", name, lineterm=""))
            rep.fail("driver", f"{name} driver loop differs from the pin in "
                               f"spec.md ({n} statements vs {want_stmts}):\n{d}")
        elif want_stmts is not None and n != want_stmts:
            rep.fail("driver", f"{name}: {n} statements, spec.md pins {want_stmts}")
    if not any(f[0] == "driver" for f in rep.failures):
        rep.ok(f"{len(found)} driver loops ({sorted(found)}) all normalise to "
               f"the pinned {want_stmts}-statement token sequence; Verus "
               f"clauses and ghost statements excluded in "
               f"{sorted(verus_ok) or 'no file'} -- the only file(s) Verus "
               f"itself verified this run, which is what licenses the strip")
    return out


# ==========================================================================
# 7. sanitizers
# ==========================================================================

def _san_build(pdir, rep, kernel, tag):
    """The ASan+UBSan build line, once, for one C kernel TU. `None` on failure.

    ⚠ **Factored out at TASK_151 so the HARDENED arm is built by THE SAME LINE
    as the plain one and cannot drift from it.** Two copies of a compiler
    invocation is how `-fstrict-aliasing` came to be missing from one of them
    (see the caller's docstring), and stage `7h` exists precisely to compare two
    kernels under identical flags.

    ⚠ `-static-libasan` / `-static-libubsan` are **gcc spellings and clang
    rejects them**; a hand-run battery that did not check `build_errors` claimed
    a clean result for four columns it never compiled (`TASK_149` §6). This
    stage is gcc-only, as it always was, so the trap is recorded rather than
    hit -- but a future clang column must not copy this line."""
    out = os.path.join(REPO, ".temp", "build", buildmod.pattern_id(pdir), tag)
    # This stage compiles its own binary and used to rely on `build.py` having
    # created the directory earlier in the same run. Under `--no-build` on a
    # fresh clone it died with a raw `ld: cannot open output file` (TASK_053).
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = [buildmod.GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
           "-fsanitize=address,undefined",
           # See the caller's docstring: gcc turns this on at -O2, this stage
           # builds at -O1, and without it stage 7 cannot see a flag-gated UB
           # class.
           "-fstrict-aliasing",
           # the container has an LD_PRELOAD that breaks the shared ASan
           # runtime's init ordering; static linking sidesteps it
           "-static-libasan", "-static-libubsan",
           "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
           "-I", os.path.join(pdir, "c"),
           os.path.join(REPO, "common", "driver.c"),
           os.path.join(pdir, "c", kernel),
           os.path.join(pdir, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        rep.fail("sanitizer",
                 f"asan build failed for c/{kernel}: "
                 f"{(r.stdout + r.stderr)[-400:]}")
        return None
    return out


def _san_fired(se):
    """Did ASan or UBSan say anything? One spelling of the predicate, used by
    both arms."""
    return ("runtime error" in se or "AddressSanitizer" in se
            or "UndefinedBehaviorSanitizer" in se or "ERROR:" in se)


def check_sanitizers(pdir, rep, indir, models, budgets=None):
    """ASan/UBSan on the C rung, with a **per-input expectation**.

    The previous version failed the gate on any sanitizer hit on any input. p02
    -- a length-prefixed copy with an attacker-controlled length -- has an
    adversarial input that is *defined* as the one that triggers the OOB write,
    and `.memory/02-bench-rules.md` says the adversarial row **records** whether
    the sanitizer fired. Under the old rule the first pattern that models a real
    bug could not be green, which is how a gate gets switched off.

    So `model.py` declares `sanitizer_expect` per input:

      "clean" -- no diagnostic, and the exit code the model predicts. Any hit is
                 a failure; this is every well-formed input, and it is what
                 keeps the sanitizer honest.
      "fires" -- the sanitizer **must** report. Silence is the failure, because
                 it means the bug this pattern exists to model is not being
                 exercised and the whole security half of the result is
                 unsupported. The exit code is recorded, not required: ASan
                 exits 1 by default, aborts (-6) under `abort_on_error`, and a
                 UBSan-only build may continue to 0.

    ⚠ **`-fstrict-aliasing` is passed EXPLICITLY** (TASK_077, RECAP "Owed" 14).
    gcc enables it at `-O2` and above and this stage builds at `-O1`, so
    without the token the stage was structurally unable to see a UB class that
    the flag gates -- p38's type pun, whose whole harm is a MISCOMPILE. The
    hole is **one FLAG wide, not one optimisation level wide**, and that
    distinction is the whole reason the repair is a token here rather than
    `-O2` in the line above: raising the level would perturb every pattern's
    sanitizer rows to fix one (`.memory/02-bench-rules.md`, "A gate hole that
    is one FLAG wide").

    Blast radius, RE-DERIVED at TASK_077 rather than carried:
    **158 rows, 3 differ, all 3 on p38, so exactly one pattern moves.**
    (TASK_068 measured "153 rows x 20 patterns" and its review re-derived 143;
    both predate p22 and p36. **Recount rather than quote.**) The probe is this
    function's own build line twice, with and without the token, over every
    pattern and every input, comparing `(exit, fired, stdout, diagnostic)` --
    ⚠ **mask the ELF BuildId hex, the ASan pid and pointers out of the
    diagnostic before comparing**, or p02 and p11 read as differing when only
    the BuildId moved (TASK_068_REVIEW attack 32). Of p38's three:

      adversarial-huge, adversarial-oob   UBSan `index 256 out of bounds for
                                          type 'uint16_t [256]'` -- these are
                                          why p38's model now says "fires"
      adversarial-stale                   checksum 10509230270850152637 ->
                                          16931469174358590653 with **no
                                          diagnostic at all**: the miscompile
                                          reads uninitialised scratch that is
                                          still INSIDE the array, so neither
                                          sanitizer has anything to say. It
                                          stays `sanitizer_expect: "clean"`,
                                          and it is the row that shows why a
                                          sanitizer is not a miscompile
                                          detector.

    ⚠⚠ **THIS ARM BUILDS `c/kernel.c` ONLY, AND THAT WAS THE WHOLE GATE UNTIL
    TASK_151.** The R1h kernel is now stage `7h`
    (`check_sanitizers_hardened`); read that function for why the gap mattered.
    """
    head("7. C rung under ASan + UBSan (per-input expectation)")
    out = _san_build(pdir, rep, "kernel.c", "c-gcc-asan")
    if out is None:
        return {}
    budgets = budgets or {}
    res = {}
    for name, mod in sorted(models.items()):
        stem = stem_of(name)
        hangs = sbg_opt(mod, "expected_hang", False)
        rc, so, se = run_bin(out, os.path.join(indir, name),
                             timeout=budgets.get(stem))
        got = so.strip()
        expect = sbg(mod, "sanitizer_expect")
        m_exit = sbg(mod, "expected_exit")
        want_out = (sbg(mod, "expected_stdout") or "").strip()
        fired = _san_fired(se)
        diag = re.sub(r"\s+", " ", se.strip())[:300]
        res[name] = {"exit": rc, "expected_exit": m_exit,
                     "expect": expect, "fired": fired, "diagnostic": diag,
                     "declared_hang": hangs, "hung": rc is None,
                     # TASK_053 F3: `so` was bound here and dropped on the floor
                     # since the stage was written. Recorded unconditionally so
                     # a reviewer can diff it; compared only where a comparison
                     # is meaningful -- see the `elif` below.
                     "stdout": got, "model_stdout": want_out}
        if hangs and rc is None:
            # TASK_068. Whether the *C* rung is one of the rungs that runs
            # forever is a per-rung fact and this stage only ever builds
            # `c/kernel.c`; the load-bearing "at least one rung really did hang"
            # check is stage 4's, which sees every rung. Without this branch the
            # `rc != m_exit` test below would fail every declared hang, since
            # `expected_exit` keeps describing the CONFORMING behaviour.
            #
            # ⚠ But it is NOT a free pass, and TASK_068 made it one
            # (TASK_068_REVIEW M4): this arm precedes `elif expect == "fires"`,
            # so a model declaring BOTH on one input had its
            # `sanitizer_expect: "fires"` obligation discharged by a bare
            # `print`, which does not even appear in the verdict's counts. The
            # "fires" case now fails -- an obligation that cannot be evaluated
            # is not an obligation that is met -- and the "clean" case is a
            # `rep.note`, which is recorded rather than printed and lost.
            # `build_models` also refuses the combination up front.
            if expect == "fires":
                rep.fail("sanitizer",
                         f"{name}: model.py declares sanitizer_expect='fires' "
                         f"AND expected_hang, and the ASan+UBSan C cell did not "
                         f"terminate within {budgets.get(stem)}s -- so the "
                         f"'fires' obligation was not observed, it was skipped. "
                         f"A sanitizer that fires aborts the process, so the "
                         f"two declarations cannot both hold of this cell: "
                         f"declare the hang on an input whose C rung is not the "
                         f"one that trips the bug.")
            else:
                rep.note(f"{name:28s} did not terminate within "
                         f"{budgets.get(stem)}s, as declared "
                         f"[adversarial: recorded, not required; its "
                         f"sanitizer_expect={expect!r} is UNCHECKED on this "
                         f"input]")
        elif expect == "fires":
            if not fired:
                rep.fail("sanitizer",
                         f"{name}: model.py declares sanitizer_expect='fires', "
                         f"but ASan+UBSan reported nothing (exit {rc}). The "
                         f"adversarial input is supposed to be the one that "
                         f"triggers this pattern's bug; if it does not, the "
                         f"security half of the result is unsupported.")
            else:
                rep.ok(f"{name:28s} sanitizer fired as declared "
                       f"(exit={rc}): {diag[:140]}")
        elif fired:
            rep.fail("sanitizer", f"{name}: sanitizer fired on an input declared "
                                  f"clean: {diag}")
        elif rc != m_exit:
            # the old version printed the exit code and ignored it entirely
            rep.fail("sanitizer", f"{name}: exit {rc}, model expects {m_exit}")
        elif not name.startswith("adversarial") and got != want_out:
            # This is the ONLY C configuration anywhere in the gate at `-O1` and
            # the only one built with `-fsanitize`, and it is not in `built`, so
            # stage 2 (`OPTS = ["O0", "O3"]`) cannot reach it: its answer was
            # compared to nothing and recorded nowhere. Reproduced at TASK_053
            # with a one-character off-by-one in p01's `c/kernel.c`, which
            # printed a wrong checksum under a GREEN stage 7.
            #
            # SCOPED TO NON-ADVERSARIAL INPUTS DELIBERATELY, and the scope is a
            # measurement, not caution: across all 16 patterns stage 7 produces
            # 114 rows, 37 of them differ from `model.py`, and every one of the
            # 37 is an `adversarial-*` input -- including six declared
            # `sanitizer_expect: "clean"` (p04 `-overwrite`, p06 `-inarray`,
            # p09 `-edge`, p17 `-crosswin-hi`/`-lo`/`-leak`), which are the
            # silent-wrong-answer rows those patterns are ABOUT. On an
            # adversarial input the C rung diverging from the model IS the
            # result (`.memory/02-bench-rules.md`; `check_adversarial` exists to
            # record rather than require it), so comparing unconditionally would
            # false-fail 37 rows on 14 patterns. 77 of 77 non-adversarial rows
            # match today, so this costs zero new failures.
            rep.fail("sanitizer",
                     f"{name}: the ASan+UBSan build printed {got!r}, model says "
                     f"{want_out!r}. Nothing else in the gate runs a C binary "
                     f"at -O1 or under -fsanitize, so no other stage can see "
                     f"this.")
        else:
            print(f"    ok   {name:28s} clean, exit={rc} (model {m_exit}), "
                  f"stdout {got!r}"
                  + ("  [adversarial: recorded, not required to agree]"
                     if name.startswith("adversarial")
                     else " matches the model"))
    return res


def check_sanitizers_hardened(pdir, rep, indir, models, budgets=None):
    """⚠⚠ **THE R1h ARM UNDER ASan + UBSan — AND UNTIL TASK_151 THE GATE NEVER
    RAN A DETECTOR ON IT, FOR ANY PATTERN.**

    `check_sanitizers` above builds `c/kernel.c` / gcc / `-O1` and nothing else,
    so `c/kernel_hardened.c` — **28 of the 29 patterns ship one** — was
    structurally outside the gate. Found at `TASK_149` §6, and it is not a
    hypothetical:

      * **It already cost a wrong manager instruction.** The `p28d` variant
        SEGVed **in the hardened arm on a BENIGN input** and its verification
        never looked (`TASK_146` §1). ⚠ **Admission question 1 — is the C
        program correct on benign inputs, so performance is measurable? — is a
        question about exactly this arm**, and R1h is half of the R1-vs-R1h
        comparison every "C is faster *because* it skipped the check" claim
        rests on (`build.py`'s module docstring).
      * `TASK_149` then hand-ran the missing cell for `p28` and found it
        **clean over 88 (arm x detector x input) cells** — so this is a GATE
        GAP, not a live defect, and the repair is what tells anyone whether the
        other 27 rows are clean too.

    **THE EXPECTATION, AND IT IS NOT PER-INPUT.** The plain arm reads
    `model.sanitizer_expect` because an adversarial input is *defined* as the
    one that trips the bug. **R1h is the rung that does NOT have the bug**, so
    the expectation is `clean` on **EVERY** input, adversarial included — that
    is what R1h *means*, and a per-input declaration here would let a pattern
    declare its way out of the only thing this stage asks. **A row that fires
    here is a real finding.**

    **What is compared, and the scoping is measured rather than cautious**
    (`.temp/t151/hardened_stdout.py`, all 28 hardened patterns):

      any diagnostic, any input   FAIL.  Measured 0 over **2027** (pattern x
                                  input) cells before this landed, so it costs
                                  zero new failures today.
      NON-adversarial exit+stdout FAIL on a mismatch. **72 of 72 non-adversarial
                                  rows are byte-identical between the two arms**,
                                  and the plain arm's are already checked against
                                  `model.py`, so this is inherited, not assumed.
      adversarial exit+stdout     RECORDED, never required — **74 of 139
                                  adversarial rows DIFFER between the arms, and
                                  that difference IS the result.** Requiring
                                  agreement here would false-fail 74 rows.
      a declared hang             RECORDED either way. ⚠ **`expected_hang` is a
                                  claim about the BUGGY rung**: `p22`'s R1 runs
                                  past the 120 s budget on `adversarial-full`
                                  and its **R1h finishes in a second**. Neither
                                  outcome is an error here.

    ⚠ **Cost, measured before it was written rather than after** (the task file
    predicted this would roughly double stage 7 and be the repair most likely
    to blow the budget): the second build is **~0.3 s** and the extra runs are
    **~3.9 s** per pattern, **117 s over all 28** — and that figure is an upper
    bound, because the probe ran every `sweep-*` blob and this stage does not.
    Against a sweep in which `check.py p28` alone takes 33 minutes it is
    **noise**, so the narrowed fallback the task file offered — hardened arm on
    non-adversarial inputs only — was **not** taken."""
    head("7h. R1h (hardened C kernel) under ASan + UBSan -- clean on EVERY input")
    if not buildmod.has_hardened(pdir):
        # p01 is the whole population of this branch today: it models no bug,
        # so there is no check to add back and no R1h to build.
        print("    this pattern ships no c/kernel_hardened.c -- nothing to run")
        return {}
    out = _san_build(pdir, rep, "kernel_hardened.c", "c-gcc-h-asan")
    if out is None:
        return {}
    budgets = budgets or {}
    res = {}
    nfired = 0
    for name, mod in sorted(models.items()):
        stem = stem_of(name)
        hangs = sbg_opt(mod, "expected_hang", False)
        rc, so, se = run_bin(out, os.path.join(indir, name),
                             timeout=budgets.get(stem))
        got = so.strip()
        m_exit = sbg(mod, "expected_exit")
        want_out = (sbg(mod, "expected_stdout") or "").strip()
        fired = _san_fired(se)
        diag = re.sub(r"\s+", " ", se.strip())[:300]
        adversarial = name.startswith("adversarial")
        res[name] = {"exit": rc, "expected_exit": m_exit, "expect": "clean",
                     "fired": fired, "diagnostic": diag,
                     "declared_hang": hangs, "hung": rc is None,
                     "adversarial": adversarial,
                     "stdout": got, "model_stdout": want_out}
        if fired:
            nfired += 1
            rep.fail("sanitizer-hardened",
                     f"{name}: ASan/UBSan fired on the HARDENED C rung: {diag}. "
                     f"R1h is the arm that carries the check, so it is expected "
                     f"clean on EVERY input including the adversarial ones -- "
                     f"that is what the R1-vs-R1h comparison means. This is a "
                     f"real finding about the pattern, not a gate false alarm: "
                     f"the whole of stage 7h measured 0 firings over 2027 cells "
                     f"across all 28 hardened patterns when it landed "
                     f"(TASK_151). Report it; do not silence it.")
        elif rc is None:
            # No requirement in either direction -- see the docstring. Recorded
            # so a reader can see WHICH arm ran forever, which is the axis
            # `expected_hang` does not have.
            rep.note(f"{name:28s} R1h did not terminate within "
                     f"{budgets.get(stem)}s [declared_hang={hangs}; recorded, "
                     f"not required]")
        elif adversarial:
            print(f"    ok   {name:28s} R1h clean, exit={rc}, stdout {got!r}"
                  f"  [adversarial: recorded, not required to agree]")
        elif rc != m_exit:
            rep.fail("sanitizer-hardened",
                     f"{name}: R1h exited {rc} on a NON-adversarial input, "
                     f"model expects {m_exit}. The hardened rung must be "
                     f"correct on benign inputs -- that is admission question 1 "
                     f"and it is what `p28d` failed while the gate was not "
                     f"looking (TASK_146 §1).")
        elif got != want_out:
            rep.fail("sanitizer-hardened",
                     f"{name}: R1h printed {got!r} on a NON-adversarial input, "
                     f"model says {want_out!r}. R1 and R1h must agree wherever "
                     f"the bug is not exercised, or the R1-vs-R1h cost "
                     f"comparison is between two different programs.")
        else:
            print(f"    ok   {name:28s} R1h clean, exit={rc} (model {m_exit}), "
                  f"stdout {got!r} matches the model")
    if res and not nfired:
        rep.ok(f"R1h clean under ASan+UBSan on all {len(res)} input(s), "
               f"adversarial included -- the arm no gate stage ran until "
               f"TASK_151")
    return res


# ==========================================================================
# 8. Miri policy
# ==========================================================================

def _miri_sysroot():
    """Miri's sysroot, built once by `cargo +nightly miri setup`. Cached on
    disk by cargo, so this is a fast no-op after the first run."""
    r = subprocess.run([CARGO, f"+{NIGHTLY}", "miri", "setup", "--print-sysroot"],
                       capture_output=True, text=True, timeout=RUN_TIMEOUT)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _miri_version():
    """`miri --version`, recorded beside the Miri verdicts.

    TASK_107. Miri runs at its DEFAULT configuration (see `MIRI_FLAGS`; the
    4.6x measurement that was read as forbidding `MIRIFLAGS` here is retracted,
    and the reason the variable stays unset is now reproducibility rather than
    speed), and that default's
    address assignment is deterministic **for a given miri** -- so the version
    is the thing a future reader needs in order to know whether a green row is
    reproducible. It is also, concretely, what went stale:
    `.memory/00-environment.md`'s seed sentence was measured at TASK_102 and
    does not reproduce now, and the miri build is the only thing that moved."""
    try:
        r = subprocess.run([MIRI_BIN, "--version"], capture_output=True,
                           text=True, timeout=120)
        return r.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _trusted_items(pdir, contract):
    """{pinned Verus source: [trusted item names]} -- `_is_trusted` applied to
    every file `verus.obligations` names. Used by the Miri policy, which is now
    keyed on "does this pattern have a trusted base at all" rather than on
    whether R4 and R5 happen to be byte-identical.

    ⚠ **TASK_088 widens the file list to `_path_includes`, the way
    `_axiom_items` was widened at TASK_084.** `TASK_084_REVIEW` major 1: D3
    widened `_check_axiom_decls` and `_axiom_items` and left this function --
    *the one immediately below it, same shape, same purpose* -- iterating
    `verus.obligations` only. Measured consequence (route J, a planted
    `#[verifier::external_body] fn r84_lie(x:u64)->(r:u64) ensures r==0 { x }`
    in a `#[path]`-included module): `grep -c r84_lie gate.log` -> **0**, the
    gate printed *"3 TCB items"*, and `synthesis.md` came out **byte-identical**.
    A false `ensures` about a SAFE operation was the whole vector -- `unsafe` in
    an included module was already caught by `_scan_unsafe_sites`, which walks
    this same list.

    Keys for included files are **repo-relative**, the convention
    `_check_axiom_decls`' docstring fixes and `_axiom_items` already uses, so a
    `common/driver.rs` item cannot collide with a bare `verus.obligations` name.
    ⚠ Because the include list is shared, one item in `common/driver.rs` lands
    in every pattern's dict; that is right for the Miri policy (every pattern's
    binary executes it) and WRONG for a published total, which is why
    `synthesize.py` dedupes -- see `TASK_084_REVIEW` minor 1."""
    out = {}
    srcs = sorted((contract.get("verus") or {}).get("obligations") or {})
    for src, path in _verus_file_list(pdir, srcs):
        if not os.path.exists(path):
            continue
        try:
            items = vparse.parse(open(path).read())
        except ValueError:
            continue
        got = sorted(i.name for i in items if _is_trusted(i))
        if got:
            out[src] = got
    return out


def _axiom_items(pdir, contract):
    """{pinned Verus source: [axiom names]} -- the body-less trusted
    declarations `_is_trusted` structurally cannot see (`_check_axiom_decls`).

    The Miri policy's *"this pattern has NO trusted item, so there is no trusted
    `ensures` whose incompleteness Miri would have to backstop"* was one of the
    five mechanisms RECAP "Owed" 0 measured blind. An `assume_specification` on
    a **safe** std function leaves no `unsafe` token for `_scan_unsafe_sites` to
    find and no `external_body` for `_is_trusted` to key on, so that sentence
    could be printed over a proof resting on a hand-written axiom. Miri is a
    real backstop for exactly that: the axiom is ghost, but the call it licenses
    is executed.

    ⚠ **TASK_084 widens this in two directions, and the widening is what stops
    the fix to stage 5a from opening a hole here.**

      * **`#[path]`-included files.** Same argument as blocker 3: an axiom in
        `common/driver.rs` or in a subdirectory module is licensed by the
        pattern's proof and executed by the pattern's binary, so it must make
        Miri mandatory in exactly the same way. The file list is
        `_path_includes`, the one `_scan_unsafe_sites` already uses.
      * **`#[verifier::external_fn_specification]` items.** These are *bodied*,
        so `vparse.axiom_decls` deliberately does not report them (they are
        classified by `vparse.parse()` instead) -- but `_is_trusted` keys on
        `external_body` alone, so without this line a pattern could ship a
        false `ensures` about a **safe** std function and print the
        "no trusted item, so Miri is not required" sentence over it. Verus's
        own error message for a malformed one reads *"assume_specification
        encoding error"*, which is the tool saying the two forms are one
        mechanism."""
    out = {}
    vcfg = contract.get("verus") or {}
    srcs = sorted(vcfg.get("obligations") or {})
    # TASK_088: one shared, DEDUPED file list (`_verus_file_list`). This used to
    # build its own and could hand the same file back under two keys --
    # `TASK_084_REVIEW` minor 5.
    for key, path in _verus_file_list(pdir, srcs):
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        # TASK_164: `global layout` / `global size_of` are excluded. This set
        # MANDATES MIRI, on the argument that "the axiom is ghost but the call
        # it licenses is executed" -- and Miri is not the backstop for a
        # `global`. rustc is: a false one const-evaluates to `error[E0080]`,
        # which `_verus` + stage 5e already fail on (measured, TASK_164;
        # `vparse.axiom_decls`' docstring has the four probes). Including them
        # would put a rustc-checked fact in a list captioned "axioms that
        # NOTHING checks".
        got = [d["name"] for d in vparse.axiom_decls(txt)
               if d["kind"] not in vparse.GLOBAL_KINDS]
        try:
            got += [i.name for i in vparse.parse(txt)
                    if (i.external or "").startswith(
                        "verifier::external_fn_specification")]
        except ValueError:
            pass
        if got:
            out[key] = sorted(set(got))
    return out


def _hung_rungs(advtable, input_name):
    """`(hung, measured)` for `input_name` as stage 4 measured it, or **None**
    when stage 4 has nothing to say about this input.

      * `hung`     -- rungs with at least one row recorded `hung`
      * `measured` -- rungs stage 4 actually produced at least one row for

    This is the **per-rung axis** `expected_hang` does not have. `model.py`
    declares a hang per INPUT, and a per-input bool cannot say WHICH rung runs
    forever; stage 4 runs every cell of every rung at both opt levels and both
    modes and records `hung` per row, so the axis already exists as a
    measurement and only needed reading (TASK_077, RECAP "Owed" 19a).

    ⚠ **`measured` IS THE HALF TASK_077 LEFT OUT, and the omission made the
    caller print a sentence stage 4 never said** (TASK_077_REVIEW m2,
    demonstrated by deleting `adversarial-full.bin/unsafe` from p22's stage-4
    table and again by setting it to `[]`). The first version returned a bare
    set of hung rungs, so a rung whose key was **absent** and a rung that
    **terminated** were the same answer -- `rung not in hung` -- and the gate
    ran Miri on the strength of a measurement that did not exist, announcing
    *"stage 4 measured the hang in [...] and NOT in 'unsafe'"* when stage 4 had
    measured nothing about `unsafe` at all. The distinction is the same one
    `None` already made one level up, applied one level down.

    An empty row list counts as NOT measured: `check_adversarial` writes the
    key before it runs the rows, so `[]` means the rows are missing, not that
    the rung was silent. If **no** rung has a row, this returns `None` rather
    than `(set(), set())` -- there is nothing to read either way, and the caller
    already handles `None` conservatively.
    """
    if not advtable:
        return None
    pre = f"{input_name}/"
    keys = [k for k in advtable if k.startswith(pre)]
    if not keys:
        return None
    measured = {k[len(pre):] for k in keys if advtable[k]}
    if not measured:
        return None
    hung = {k[len(pre):] for k in keys
            if any(r.get("hung") for r in (advtable[k] or []))}
    return hung, measured


# ==========================================================================
# 9. the PUBLISHED sidecars -- `results/tables/` and `controls/*.json`
# ==========================================================================

# `harness/report.py::audit_section` writes exactly this line into every table,
# and this is the only 12-hex string in the file whose meaning is fixed:
#
#   Measured by the gate, ... from `results/gate/<pattern>.json`, contract
#   `<12 hex>`.
#
# ⚠ MATCH THAT LINE, NOT "any 12-hex token in the file". A table's `why` block
# quotes md5 prefixes (`e207ec6c8697`, `da08af26d9b1`, ...), so a loose scan
# both false-positives and false-negatives -- and computing from the prose
# instead of from the artefact is the exact failure `.memory/03-measurement.md`
# records against the manager's own 64-vs-87 arithmetic.
_TABLE_CONTRACT_RE = (r"from `results/gate/{pat}\.json`, contract "
                      r"`([0-9a-f]{{12}})`")


def check_published_tables(pdir, rep, contract_sha):
    """Is this pattern's published table present, and does it cite THIS
    contract?

    RECAP owed-item 23 predicted its own recurrence in those words -- *"nothing
    will detect the NEXT three: `results/tables/` is still in no hash set, so
    `--check-stale` remains blind to it. This item will recur."* **It recurred,
    and it took 16 tasks**: `results/tables/p09-bitset.md` cited `0a37c0cd1418`
    while its record said `ea0295eaea6a`, two contract moves later. Then `p23`
    shipped with **no table at all** and nothing noticed.

    ⚠⚠ **WHY THIS IS HERE AND NOT IN `measure.py`.** `measure.py::check_stale`
    is the natural home -- it already globs `results/*.json` and
    `results/gate/p*.json` and nothing else -- and it is the WRONG home, because
    `measure.py` is inside `measure.py::measurement_sources`. An edit there
    makes every `results/pNN-*.json` stale and costs a full matrix re-measure,
    which re-takes the wall-clock block and moves published timing prose, for a
    **bookkeeping** check. `check.py` is not measurement-hashed, so this costs
    the gate sweep that a `check.py` edit was already going to cost.

    ⚠ **ITERATE OVER PATTERNS, NOT OVER TABLES.** `.temp/mgr99/tables_stale.py`
    globbed `results/tables/*.md` and so reported *"24 checked, 0 STALE"* on a
    25-pattern tree: a checker that can only see the files it is checking cannot
    report an absent one. Living in a per-pattern gate stage makes that
    structural rather than remembered -- the iteration IS the pattern list, and
    a pattern with no table fails its own gate.

    **Each failure mode names its own fix, and ⚠ THEY ARE NOT THE SAME FIX --
    this docstring said they were, and the `MISSING` half was wrong** (TASK_114
    m8, fixed at TASK_119; `PROTOCOL.md` rule 13's shape again, a summary line
    above a body that had moved on).

      * `STALE` / `UNPINNED` -- the measurement record already exists, so the
        loop really is *gate -> `harness/report.py pNN` -> gate*, twice, with
        no re-measure and no `contract_sha256` move. `check.py` writes
        `results/gate/<pattern>.json` even when the verdict is FAIL (only a
        `--skip`/`--no-*` PARTIAL run is diverted to `.temp/`), so the middle
        step does not need a green run. ⚠ **That last sentence is true of THIS
        stage and was ALMOST false of stage `9c`**: `9c` compares the whole
        rendered table, and until TASK_127 the render contained the record's
        `verdict`, so re-rendering from a FAIL record baked `FAIL` into the
        table. Fixed at the source -- `report.py::read_gate_loud` no longer
        reads `verdict` -- rather than by adding an ordering rule nobody would
        remember.

    ⚠ **THIS STAGE PINS THE DECLARATION, NOT THE CONTENT, AND TASK_121 CAUGHT
    IT IN THE ACT**: `results/tables/p23-partition.md` published a sentence that
    had become false while this stage reported `FRESH`, because
    `contract_sha256` had not moved. Stage `9c` (`check_table_render`) is the
    content pin and it **subsumes all three verdicts below** -- a fresh render
    always carries the current contract line, so `UNPINNED` and `STALE` both
    show up as a byte difference, and `MISSING` is handled by 9c deferring to
    this stage. It is kept anyway, deliberately: it needs no import, it survives
    a broken `report.py`, and its three messages each name a *different* fix
    (`MISSING` in particular needs three commands, not two). ⚠ **Two pins, ONE
    property: do not read a green 9 as independent evidence about content.**
      * `MISSING` -- ⚠ **the two-command loop DEADLOCKS on exactly the case
        this verdict is about.** `report.py::main` calls `load(pid)` first and
        `load` requires `results/pNN-*.json`, **`measure.py`'s** record,
        discriminated by carrying a `cells` list. The gate record is read only
        by `report.py::read_gate_audit`, for the audit section. On a brand-new
        pattern there is no measurement record, so:

            $ python3 harness/report.py p99
            report.py: p99 matches [] in results/

        The working loop is three commands: `harness/measure.py pNN` (the full
        matrix), `harness/report.py pNN`, gate.

    **"Could this happen by accident?"** -- the threat model's first question
    (`.memory/02-bench-rules.md`). It happened by accident twice, which is the
    point; and it fires on **nobody** in the tree as it stands: 26 of 26 tables
    exist and 26 of 26 cite the current contract, verified before landing this.
    """
    head("9. the published table cites THIS contract")
    pat = os.path.basename(pdir)
    tbl = os.path.join(REPO, "results", "tables", f"{pat}.md")
    out = {"table": os.path.relpath(tbl, REPO), "contract_sha256": contract_sha}
    if not os.path.exists(tbl):
        out["verdict"] = "MISSING"
        rep.fail("tables",
                 f"results/tables/{pat}.md does NOT EXIST. The pattern is "
                 f"built and gated and a reader has nowhere to find its "
                 f"result -- which is `PROTOCOL.md` rule 1's fourth step, and "
                 f"`p23` shipped exactly this way with nothing noticing. "
                 f"Fix, and it is THREE commands here, not two: "
                 f"`harness/measure.py {pat.split('-')[0]}` (the full matrix), "
                 f"then `harness/report.py {pat.split('-')[0]}`, then gate "
                 f"again. ⚠ `report.py` renders from `results/"
                 f"{pat.split('-')[0]}-*.json` -- MEASURE.PY's record, which "
                 f"it loads FIRST and exits without if it is absent -- and NOT "
                 f"from `results/gate/{pat}.json`, which it reads only for the "
                 f"stage-0b audit section. On a brand-new pattern, which is "
                 f"the case this message is about, there is no measurement "
                 f"record yet and `report.py` cannot run at all.")
        return out
    cited = re.findall(_TABLE_CONTRACT_RE.format(pat=re.escape(pat)),
                       open(tbl).read())
    out["cited"] = cited
    if not cited:
        out["verdict"] = "UNPINNED"
        rep.fail("tables",
                 f"results/tables/{pat}.md cites no `contract_sha256` at all, "
                 f"so nothing can tell whether its numbers describe this "
                 f"declaration or a superseded one. `report.py::audit_section` "
                 f"emits that line on every render, so a table without it "
                 f"predates the mechanism. Fix: `harness/report.py "
                 f"{pat.split('-')[0]}`.")
    elif contract_sha[:12] not in cited:
        out["verdict"] = "STALE"
        rep.fail("tables",
                 f"results/tables/{pat}.md is STALE: it cites contract "
                 f"{cited} and `spec.md`'s `slb-contract` block now hashes to "
                 f"{contract_sha[:12]}. The declaration above the numbers and "
                 f"the numbers themselves are describing DIFFERENT "
                 f"declarations -- `p09` shipped two contract moves stale for "
                 f"16 tasks. Fix: `harness/report.py {pat.split('-')[0]}` "
                 f"(no gate re-run needed for the render itself, no "
                 f"re-measure, and `contract_sha256` does not move).")
    else:
        out["verdict"] = "FRESH"
        rep.ok(f"results/tables/{pat}.md exists and cites contract "
               f"{contract_sha[:12]}, which is this run's")
    return out


def check_table_render(pdir, rep, tables, gate_now):
    """9c. Is `results/tables/<pattern>.md` byte-identical to what
    `harness/report.py` renders from this tree TODAY, **against the record THIS
    RUN IS ABOUT TO WRITE**?

    **The gap this closes.** Stage 9 above pins the table on `contract_sha256`
    -- the *declaration*. `TASK_121` caught the consequence live:
    `results/tables/p23-partition.md` was publishing *"`sweep_fit.json` carries
    NO staleness pin ... treat every figure quoted from it as UNDATED"* **after
    that sentence had become false**, and stage 9 said `FRESH` on every run,
    correctly, because the contract had not moved. `TASK_125` §D had already
    named the shape of the fix: this is not a missing KIND of instrument, it is
    the known instrument pointed at the wrong input.

    **Why recompute rather than hash.** `report.py` reads exactly three things
    (verified by reading it, not by assuming):

      * `results/pNN-<slug>.json` -- `load()`, the measurement record
      * `patterns/<pattern>/spec.md` -- `read_idiom()`, re-read LIVE on purpose
      * `results/gate/<pattern>.json` -- `read_gate_audit` / `read_gate_loud`,
        deliberately NOT recomputed

    ⚠⚠ **A `derived_from_sha256` over those three paths -- the obvious spelling,
    and the one this stage was first designed as -- IS DEAD, AND IT IS DEAD BY
    MEASUREMENT.** A gate record is not byte-reproducible
    (`.memory/03-measurement.md`); comparing the committed records against
    `TASK_125`'s second sweep of the same tree, **21 of 26 differ**, so a
    whole-file pin on the gate record would report `STALE` on 21 of 26
    patterns' own gate run. A pin that fires on its own gate run is strictly
    worse than no pin. Everything that moves -- sanitizer `diagnostic` strings
    (20 patterns), `miri.runs[].seconds` (14), `adversarial` group order (7),
    the `N distinct behaviours` `notes` line (2) -- is **outside** the set
    `report.py` reads, which is why re-rendering works where hashing does not:
    over the same two draws the rendered table is **identical in 26 of 26**.
    ⚠ **Re-derive both figures rather than trusting this paragraph** --
    `python3 harness/tools/table_render_inputs.py --against <second-sweep-gate-dir>`,
    and `--reads` for the read set, which is MEASURED by mutation rather than
    read off `report.py`'s source (it is
    `{contract_sha256, controls_json, idiom_audit, loud}`, 26 of 26).

    Recomputing also needs no projection function, no path list to rot, and it
    answers the actual question (*would a fresh render differ?*) instead of a
    proxy for it. It is the only spelling that also notices a `report.py`
    change that alters the output.

    ⚠⚠ **THE TRAP, AND IT IS SELF-REFERENCE, NOT VOLATILITY.** Until TASK_127
    `report.py::shout_section` printed the record's `verdict` into the table.
    `verdict` is an **output of the gate run this stage runs in**, so the
    naive design writes its own input and oscillates with period 2, starting
    the first time it fires:

        run N    fires -> `rep.fail` -> verdict FAIL -> record says FAIL
        report.py      -> table prints ``verdict `FAIL```
        run N+1  render(FAIL record) == table -> FRESH -> verdict PASS
        run N+2  render(PASS record) != table -> FIRES AGAIN -> ...

    Measured before the fix: **19 of 26 tables changed bytes when the record's
    `verdict` changed.** Fixed in `report.py` by not rendering `verdict` at
    all, and the regression detector is
    `python3 harness/tools/table_render_inputs.py --selfref`, which exits 1 if
    any key OUTSIDE ITS ALLOW-LIST reaches the render. ⚠ **The rule that
    generalises: this stage may never `rep.shout`** -- `loud` IS rendered, so a
    shout here is the same defect wearing a milder verb. `rep.fail` only, and
    `failures` is not rendered (measured, not assumed: `--reads`).

    ⚠⚠ **THAT DETECTOR WAS A HAND-WRITTEN DENY-LIST UNTIL TASK_151 AND IT WAS
    BLIND TO THIS STAGE'S OWN VERDICT.** Its tuple named 9 of the record's 34
    keys, so a `report.py` rendering `table_render` measured `26/26 READ` while
    `--selfref` printed `0` and passed (`TASK_132`, `RECAP` finding 46 (iii)).
    It is now a census over every key each record carries, with an allow-list of
    four and a `--selftest` must-fire arm. ⚠ **Note what that means for anything
    added to the gate record from here on -- including TASK_151's own
    `sanitizer_hardened`: a new key is FORBIDDEN in the render by default, and
    the detector covers it without anyone remembering to list it.**

    ⚠⚠⚠ **THE ONE-RUN LAG. IT WAS REAL, THIS DOCSTRING CALLED IT *"THE STATUS
    QUO, NOT A NEW DEFECT"*, AND THAT DEFENCE WAS WRONG -- IT THEN COST TWO
    PATTERNS A RUN EACH IN ONE SESSION.** Until TASK_141 this stage rendered
    from whatever `results/gate/<pattern>.json` was on disk, which is the
    PREVIOUS run's record. So a run that changed `loud`, `idiom_audit` or
    `controls_json` **compared the table against a record it was about to
    overwrite**: it went green on the agreement between two stale things, wrote
    the new values, and the NEXT run failed. `p16` hit it at TASK_138 and `p29`
    at TASK_139 -- `p29` shipped a record saying all four control sidecars were
    `FRESH` beside a published table saying all four were `STALE`, under a
    heading reading *"these are not defects"*, and the manager published
    *"green"* off that record (`RECAP` 52, `.memory/03-measurement.md` 15).
    ⚠ **A GREEN 9c WAS NOT EVIDENCE THAT THE TABLE MATCHED THE RECORD THAT RUN
    WROTE**, which is the only thing it was ever asked.

    ✅ **CLOSED at TASK_141 by passing the run's own values in**, not by moving
    the stage: `main` snapshots `{contract_sha256, controls_json, idiom_audit,
    loud}` as `gate_now` -- after stage 9b, which had to move above 9c for
    `controls_json` to exist yet -- and `report.py::gate_record` prefers them
    over the file. `_check_render_inputs_final` then re-compares the snapshot
    against the record actually written, so an ordering change fails loudly
    instead of silently reopening the lag.

    ⚠ **Why NOT "just move the stage after the record write", which is the
    obvious spelling.** The failure would then have to change a record already
    on disk, so either the record's `verdict` lies about the run or the stage
    has to rewrite it -- and rewriting it is the `verdict` self-reference this
    stage was fixed for. Passing the values forward has neither problem: the
    four keys are deterministic functions of the committed sources, and nothing
    run-scoped reaches the render.

    ⚠ **Stage 9 does NOT have the same shape, and this docstring used to claim
    it did.** Stage 9 compares LIVE `spec.md` against the table, so its
    detection never lagged; 9c's lag was in the detection itself (TASK_132).

    ⚠ **What still reaches the render and is a function of the RUN**: nothing,
    after the `verdict` removal. `blocked` is not read; `loud`, `controls_json`,
    `idiom_audit` and `contract_sha256` are deterministic functions of the
    committed sources. The residual to watch is a future `report.py` that
    starts rendering a run-scoped field -- `read_gate_loud`'s docstring carries
    the rule.

    ⚠ **Do not "improve" this into a `--stdout` diff.** `report.py --stdout`
    uses `print(md)` and the file writer uses `write(md)`, so a `--stdout`
    capture carries one extra trailing newline and reports 26 of 26 tables
    moved. That artefact has now misled twice (`.memory/05-layout.md`, RECAP).
    This stage compares `build()`'s return value against the file's bytes, so
    it cannot see it."""
    head("9c. the published table is a fresh render of THIS tree")
    pat = os.path.basename(pdir)
    pid = pat.split("-")[0]
    out = {"table": os.path.join("results", "tables", f"{pat}.md")}
    if tables.get("verdict") == "MISSING":
        out["verdict"] = "SKIPPED-NO-TABLE"
        print("    stage 9 already failed MISSING; there is no table to "
              "compare a render against, and its fix is the three-command one.")
        return out
    try:
        doc, name = reportmod.load(pid)
        # ⚠ `gate_now`, NOT the file: see the one-run-lag paragraph above. A
        # `None` here silently restores the lag, so it is asserted rather than
        # defaulted.
        if not isinstance(gate_now, dict) or set(gate_now) != set(
                RENDER_INPUT_KEYS):
            raise ValueError(
                f"stage 9c was handed {sorted(gate_now) if isinstance(gate_now, dict) else type(gate_now).__name__} "
                f"instead of this run's {list(RENDER_INPUT_KEYS)}; it cannot "
                f"compare the table against the record this run writes")
        fresh = reportmod.build(doc, name, gate_now)
    except SystemExit as e:
        # `report.load` exits when there is no `results/pNN-*.json`, or when it
        # is ambiguous. Stage 9 cannot see either: a table can exist and cite a
        # current contract while the record it was rendered from is gone.
        out["verdict"] = "NO-RECORD"
        rep.fail("tables",
                 f"`harness/report.py {pid}` cannot render at all: {e}. The "
                 f"published table cannot be checked against anything. Fix: "
                 f"`harness/measure.py {pid}` (the full matrix), then "
                 f"`harness/report.py {pid}`, then gate again.")
        return out
    except Exception as e:                      # noqa: BLE001 - see below
        # A reporting stage must not crash the gate: a malformed record is a
        # reporting failure, and the run's correctness stages have already
        # decided everything they decide.
        out["verdict"] = "RENDER-ERROR"
        rep.fail("tables",
                 f"`harness/report.py {pid}` raised {type(e).__name__}: {e}. "
                 f"The table cannot be checked. Fix the record or the reporter, "
                 f"then re-run `harness/report.py {pid}` and gate again.")
        return out
    want = name.replace(".json", ".md")
    out["renders_to"] = os.path.join("results", "tables", want)
    if want != f"{pat}.md":
        # Cannot happen on this tree (26 of 26 record stems equal the pattern
        # directory name) and is checked rather than assumed, because stage 9
        # would then be watching a file `report.py` never writes.
        rep.fail("tables",
                 f"`report.py` renders {pat} to results/tables/{want}, but "
                 f"stage 9 checks results/tables/{pat}.md. One of them is "
                 f"watching a file nothing writes.")
    tbl = os.path.join(REPO, "results", "tables", want)
    if not os.path.exists(tbl):
        out["verdict"] = "MISSING"
        rep.fail("tables",
                 f"results/tables/{want} does not exist"
                 + ("" if want == f"{pat}.md" else
                    f" (stage 9 was checking results/tables/{pat}.md, which is "
                    f"a different file)")
                 + f", and stage 9 did not report MISSING for this pattern, so "
                 f"the two stages disagree about which file is the published "
                 f"table. Fix: `harness/report.py {pid}`, then gate again.")
        return out
    cur = open(tbl, encoding="utf-8").read()
    out["render_sha256"] = hashlib.sha256(fresh.encode()).hexdigest()
    out["published_sha256"] = hashlib.sha256(cur.encode()).hexdigest()
    if fresh == cur:
        out["verdict"] = "FRESH"
        rep.ok(f"results/tables/{want} is byte-identical to a fresh render "
               f"({out['render_sha256'][:12]}) of the measurement record, "
               f"spec.md and the gate record")
        return out
    out["verdict"] = "STALE-CONTENT"
    d = list(difflib.unified_diff(cur.splitlines(), fresh.splitlines(),
                                  "results/tables/" + want, "fresh render",
                                  n=0, lineterm=""))
    moved = [ln for ln in d
             if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]
    out["lines_moved"] = len(moved)
    rep.fail("tables",
             f"results/tables/{want} is STALE IN ITS CONTENT: "
             f"{len(moved)} line(s) differ from what `harness/report.py {pid}` "
             f"renders from this tree. Stage 9 above can be GREEN while this "
             f"is red -- it pins the DECLARATION (`contract_sha256`), this "
             f"pins what the table SAYS, and `p23` published a sentence that "
             f"had become false in exactly that gap (TASK_121). Fix, and it is "
             f"the same two commands as stage 9: `harness/report.py {pid}`, "
             f"then gate again. ⚠ Since TASK_141 this stage renders against "
             f"THIS run's `contract_sha256`, `controls_json`, `idiom_audit` "
             f"and `loud`, not the previous run's, so a red 9c means the "
             f"committed table really does disagree with the record being "
             f"written now -- and `harness/report.py {pid}` reads that record "
             f"only after this run has written it, which is why `report.py` "
             f"comes after the gate and not before. First differing lines:\n      "
             + "\n      ".join(ln[:200] for ln in d[2:14]))
    return out


#: The gate-record keys `harness/report.py` renders into `results/tables/*.md`.
#: MEASURED BY MUTATION, not read off `report.py`'s source:
#: `python3 harness/tools/table_render_inputs.py --reads` flips each key of each
#: record and re-renders, and these four are the ones that move the bytes, on
#: 26 of 26 patterns. Stage 9c must supply all four from THIS run or its verdict
#: is a statement about the previous run (TASK_141).
RENDER_INPUT_KEYS = ("contract_sha256", "controls_json", "idiom_audit", "loud")


def _check_render_inputs_final(doc, gate_now, rep):
    """Did the record being written really carry what stage 9c rendered from?

    ⚠⚠ **This is the must-not-drift half of the TASK_141 repair, and it exists
    because the repair is an ORDERING invariant that nothing else enforces.**
    Stage 9c compares the published table against a render built from
    `gate_now` -- four keys snapshotted between stage 9b and stage 9c. That is
    only the record THIS run writes if no stage after 9c touches any of them.
    `contract_sha256`, `idiom_audit` and `controls_json` are handed to their
    keys unchanged, so the reachable one is `loud`: **every `rep.shout` in the
    file appends to it**, there are ~26 shout sites over 12 sections, and a
    stage added below 9c would silently put the one-run lag back.

    So this compares, and `rep.fail`s on a mismatch rather than trusting the
    ordering to be remembered. ⚠ It may never `rep.shout`: `loud` is rendered,
    so a shout here would itself falsify the thing it is checking."""
    drift = [k for k in RENDER_INPUT_KEYS if doc.get(k) != gate_now.get(k)]
    if not drift:
        return
    rep.fail("tables",
             f"THE STAGE-9c RENDER IS NOT A RENDER OF THIS RUN'S RECORD: "
             f"{drift} changed between stage 9c and the record write, so 9c's "
             f"verdict describes a record that is not the one on disk. This is "
             f"the one-run lag TASK_141 closed, reopened by a stage running "
             f"after 9c -- `loud` is the reachable key, because every "
             f"`rep.shout` appends to it. Fix: move that stage ABOVE the "
             f"`gate_now` snapshot in `main`, the way stage 9b was moved.")


#: TASK_164 item A. The verdict conventions the 46 tracked sidecars ACTUALLY
#: use, censused before anything was written (`.temp/t164/keys_sidecars.py`):
#:
#:     `problems`: [...]                 30 of 46, ALL EMPTY today
#:     `summary`: {n, as_expected}        5 of 46, all `proof_mutants.json`
#:     neither                           11 of 46
#:
#: ⚠ **`problems` is a VERDICT and not a note field, and that is measured, not
#: judged: 30 of 30 generators that write the key EXIT 1 when it is non-empty.**
#: So `rep.fail` is what the tree already means by it.
#: ⚠ **No third convention is invented here** -- but four of the 11 do carry a
#: verdict in a bespoke shape (`p35/proof_mutants.json`'s
#: `arms_as_designed`/`arms_total`, `p35/union_oracle.json`'s
#: `cells_ok`/`cells_total`, `p32/forgeable.json`'s `hardened_kernel_broke`,
#: and `unstable_cells` on `p28`/`p32`'s `repro.json`), and this stage still
#: cannot read any of them. That is reported in `TASK_164_REPORT.md`, not fixed.
def control_json_verdict(doc):
    """`(verdict, [detail, ...])` -- what did this control sidecar CONCLUDE?

    `verdict` is one of:

      * **`"FAILED"`** -- a verdict field is present and says something is
        wrong. `details` quotes it.
      * **`"CLEAN"`** -- a verdict field is present and says nothing is wrong.
      * **`"NO-VERDICT"`** -- the document carries neither convention.

    ⚠ **A PURE FUNCTION OF THE DOCUMENT**, with no filesystem and no `rep`, which
    is what lets `check_selftests` drive it directly on synthetic documents
    (`_CONTROL_VERDICT_CASES`) on **every** invocation. That is not decoration:
    the repair is **PROSPECTIVE** -- all 30 shipped `problems` lists are EMPTY
    and all 5 shipped `summary` blocks are `as_expected == n` -- so a green
    33-pattern sweep says **nothing** about whether this can fire. An arm nobody
    has seen fail is not an arm (`TASK_151`; `.memory/03-measurement.md`
    entry 19).

    ⚠⚠ **AND THE HOLE THIS CLOSES IS INVISIBLE TO THE PIN ABOVE IT.** 0 of 46
    sidecars pin THEMSELVES in `derived_from_sha256`, so editing `problems`
    from `[]` to `["the control failed"]` moves nothing stage 9b hashes: the
    stage printed `FRESH` and the gate stayed green. The `summary` half is the
    *"regenerated at 7 of 9"* case -- a proof-mutant battery that regressed
    reads `FRESH` today.

    **`problems` MUST BE A LIST, and a non-list is a FAILURE rather than a
    silent pass.** `[]` is the one spelling of *"no problems"* the tree uses (30
    of 30). A string, a number, `null` or a dict is a generator typo or a hand
    edit, and the failure mode it creates is the bad one: a reader sees a
    `problems` key and reads "reported and clean", while `if doc["problems"]:`
    in the generator would have read a non-empty string as a FAILURE. Pinning
    the shape costs nothing (it fires on zero sidecars) and removes the
    ambiguity.

    **A `summary` with `as_expected != n` fails in BOTH directions.**
    `as_expected < n` is the battery that regressed; `as_expected > n` is
    incoherent and can only be a generator bug, and calling it clean would be
    the same silence in the other direction."""
    if not isinstance(doc, dict):
        return "FAILED", [f"the sidecar is a {type(doc).__name__}, not a JSON "
                          f"object, so no verdict field can be read from it"]
    bad, seen = [], False
    if "problems" in doc:
        p = doc["problems"]
        if isinstance(p, list):
            seen = True
            if p:
                bad.append(f"`problems` is NON-EMPTY -- {len(p)} entry/entries: "
                           f"{[str(x)[:160] for x in p[:5]]}")
        else:
            bad.append(f"`problems` is a {type(p).__name__} ({str(p)[:80]!r}), "
                       f"not a list. Every one of the 30 sidecars that carries "
                       f"this key writes a LIST and its generator exits 1 when "
                       f"the list is non-empty; `[]` is the only spelling of "
                       f"'no problems'.")
    if doc.get("summary") is not None:
        s = doc["summary"]
        if not isinstance(s, dict):
            bad.append(f"`summary` is a {type(s).__name__} ({str(s)[:80]!r}), "
                       f"not an object with `n` and `as_expected`")
        elif "n" in s or "as_expected" in s:
            n, ae = s.get("n"), s.get("as_expected")
            ints = all(isinstance(v, int) and not isinstance(v, bool)
                       for v in (n, ae))
            if not ints:
                bad.append(f"`summary` carries n={n!r} as_expected={ae!r}; both "
                           f"must be integers for the count to mean anything")
            else:
                seen = True
                if ae != n:
                    bad.append(f"`summary` says {ae} of {n} arms behaved AS "
                               f"EXPECTED -- {n - ae} did not"
                               if ae < n else
                               f"`summary` says {ae} of {n} arms behaved as "
                               f"expected, and {ae} > {n} is incoherent")
    if bad:
        return "FAILED", bad
    return ("CLEAN" if seen else "NO-VERDICT"), []


def _cv(doc):
    """One `_CONTROL_VERDICT_CASES` cell: `[verdict, n_details]`.

    ⚠ **An exception becomes `["RAISED", <type>, <msg>]`**, a THREE-element list
    that can never equal a two-element expectation -- so a malformed document is
    REPORTED at stage 0 instead of killing the gate's import
    (`.memory/03-measurement.md` entry 19: three of `p32`'s four planted
    mutations failed by CRASHING and the diagnostic was lost)."""
    try:
        v, d = control_json_verdict(doc)
    except Exception as e:                                       # noqa: BLE001
        return ["RAISED", type(e).__name__, str(e)[:120]]
    return [v, len(d)]


#: ⚠⚠ **THE MUST-FIRE ARM FOR THE SIDECAR VERDICT READ (TASK_164 item A).**
#: Exposure across the shipped tree is ZERO -- 30 empty `problems`, 5 clean
#: `summary` blocks -- so a green 33-pattern sweep is not evidence that this can
#: fire at all. Same shape as `_ASSUME_CASES` above and `TASK_147`'s
#: `detector_selftest()`: synthetic in-memory documents, run by
#: `check_selftests` on **every** invocation.
_CONTROL_VERDICT_CASES = [
    # --- the two firing arms, which is the whole point of the item ----------
    ("a NON-EMPTY `problems` FAILS",
     _cv({"problems": ["the hardened arm segfaulted on small.bin"]}),
     ["FAILED", 1]),
    ("`summary` {n: 9, as_expected: 7} FAILS (the regressed battery)",
     _cv({"summary": {"n": 9, "as_expected": 7}}), ["FAILED", 1]),
    # --- and the silent ones, or the arm would fire on the whole tree -------
    ("`summary` {n: 9, as_expected: 9} is silent",
     _cv({"summary": {"n": 9, "as_expected": 9}}), ["CLEAN", 0]),
    ("`problems: []` is silent -- and it is 30 of 46 sidecars today",
     _cv({"problems": []}), ["CLEAN", 0]),
    # --- the SHAPE pin: a generator typo must not read as "no problems" -----
    ("`problems` as a STRING FAILS rather than passing",
     _cv({"problems": "none"}), ["FAILED", 1]),
    ("...an EMPTY string too -- falsy is not the same as `[]`",
     _cv({"problems": ""}), ["FAILED", 1]),
    ("`problems` as a NUMBER FAILS", _cv({"problems": 0}), ["FAILED", 1]),
    ("`problems: null` FAILS -- 'not computed' is not 'none found'",
     _cv({"problems": None}), ["FAILED", 1]),
    ("`summary` with non-integer counts FAILS",
     _cv({"summary": {"n": "9", "as_expected": "9"}}), ["FAILED", 1]),
    ("`summary` with as_expected > n FAILS (incoherent, not clean)",
     _cv({"summary": {"n": 7, "as_expected": 9}}), ["FAILED", 1]),
    ("half a `summary` FAILS", _cv({"summary": {"n": 9}}), ["FAILED", 1]),
    # --- both channels at once, and both must be reported -------------------
    ("a doc that fails BOTH ways reports BOTH",
     _cv({"problems": ["x"], "summary": {"n": 9, "as_expected": 7}}),
     ["FAILED", 2]),
    # --- the no-verdict disposition, PINNED so it cannot drift silently -----
    ("a sidecar with NEITHER field is NO-VERDICT, not FAILED "
     "(11 of 46 today -- see the stage's docstring for why it is not a shout)",
     _cv({"derived_from_sha256": {}, "rows": []}), ["NO-VERDICT", 0]),
    ("`summary: null` alone is NO-VERDICT, not a malformed summary",
     _cv({"summary": None}), ["NO-VERDICT", 0]),
    ("a `summary` of some OTHER shape does not silently pass as a verdict",
     _cv({"summary": {"windows": 20000}}), ["NO-VERDICT", 0]),
    # --- and the malformed-input arms: REPORTED, never a crash --------------
    ("a sidecar that is a LIST, not an object, FAILS rather than raising",
     _cv([1, 2, 3]), ["FAILED", 1]),
    ("...and a `None` document too", _cv(None), ["FAILED", 1]),
]


def check_control_json_pins(pdir, rep, source_sha):
    """`patterns/*/controls/*.json` -- does a published sidecar say what it was
    taken against, **and what did it conclude?**

    `harness/measure.py --check-stale` globs `results/*.json` and
    `results/gate/p*.json` **and nothing else**, so a tracked cache of measured
    numbers under `patterns/*/controls/` is invisible to it. `p23` ships
    `controls/sweep_fit.json` -- 15 measured rows and two fits, quoted in its
    `NOTES.md` 9c -- and until TASK_121 it carried nothing.

    **Two accepted keys, and a sidecar needs exactly one of them:**

    * ⚠⚠ **`derived_from_sha256`** -- a `{repo-relative path: sha256}` dict the
      sidecar writes for ITSELF. This stage just re-hashes the named paths, so
      it needs no knowledge of what any generator does and it generalises to
      any future sidecar in any pattern. **This is the key to prefer.**
    * **`gate_source_sha256`** -- equal to this run's gate `source_sha256`, the
      `synthesis/licence.json` shape. Kept for a sidecar that genuinely derives
      from the whole gate record. ⚠ **It is the WRONG key for anything that
      derives from a narrower set**, because the gate digest covers
      `patterns/*/*.md`: pinning against it reports `STALE` on a prose fix, and
      a pin whose `STALE` does not mean "the numbers are wrong" is a pin that
      gets switched off. That is why `sweep_fit.json` does not use it.
      ⚠ The cost argument this used to be justified by -- "~30 minutes of
      callgrind to clear it" (`.memory/05-layout.md`) -- is FALSE: TASK_121
      timed a full `sweep_fit.py` regeneration at **47 s**, byte-identical
      output. The reason to pin narrowly is the SIGNAL, not the price.

    **Verdicts.** A sidecar with neither key is SHOUTED, not failed, because a
    red gate nobody can clear is how gates get switched off (`check_miri`'s own
    "a missing tool blocks a row, it does not fail the pattern"). A hash that
    MOVED is a FAIL. A hashed path that is ABSENT is a SHOUT, not a fail, and
    for the same reason `measure.py::check_stale` separates MISSING from STALE:
    `sweep_fit.json` pins gitignored `inputs/sweep-*.bin`, so a fresh clone
    that has not run `gen.py --sweep` must not be painted red for it. ⚠ **The
    hole that leaves is real and is named here rather than hidden: deleting a
    hashed blob downgrades the check from FAIL to SHOUT.** It is loud, it
    survives to the verdict, and it reaches `results/tables/`.

    ⚠ Every committed `controls/` file EXCEPT `.json` and `.log` is in the GATE
    record's `source_sha256` (`main`'s `srcs` list; it read `controls/*.py`
    until TASK_142) and **none** of `controls/` is in
    `measure.py::measurement_sources`, so writing the pin costs one gate re-run
    and no re-measure. ✅ Measured, not read: `controls/*` appears in **0 of 27**
    measurement records and `controls/*.py` in **96 entries over 27 of 27** gate
    records, set equal to the disk (TASK_141 §3, re-derived at TASK_142).
    ⚠⚠ The two excluded extensions are excluded so that the files THIS STAGE
    evaluates stay out of the digest that certifies the run evaluating them --
    see `main`'s `srcs` comment for the `gate_source_sha256` fixpoint that
    would otherwise be one sidecar away.

    ---- TASK_164 item A: the stage now reads the VERDICT, not only the PIN ---

    ⚠⚠⚠ **UNTIL TASK_164 THIS STAGE READ `derived_from_sha256` AND
    `gate_source_sha256` AND NOTHING ELSE.** It answered *"were these numbers
    taken against this tree?"* and never *"what did the control conclude?"*, and
    `grep -rn 'problems\\|invariant\\|measured_utc' harness/ synthesis/` found
    **zero** reads of any verdict field anywhere. **Run a control, let it record
    real problems, and the sidecar was still `FRESH` and the gate still green.**
    ⚠ It cannot happen through STALENESS -- the pin catches that -- it happens
    when a control is re-run and its own findings are ignored, and **0 of 46
    sidecars pin THEMSELVES**, so editing `problems` from `[]` to
    `["it failed"]` moves nothing this stage hashes.

    `control_json_verdict` above is the read; its docstring carries the census
    and the shape rules. Two things this stage decides, and both are decisions
    rather than oversights:

      * ⚠⚠ **A sidecar with NO verdict field is SILENT (printed, not shouted,
        not failed), and the reason is measured rather than aesthetic.**
        `controls_json` -- this function's return value -- and `loud` are two of
        the FOUR keys `report.py` renders into `results/tables/*.md`
        (`RENDER_INPUT_KEYS`), and `report.py::shout_section` prints a line for
        **every `controls_json` entry whose value is not `"FRESH"`**. So a
        `rep.shout` here, or a new verdict string for the 11 no-verdict
        sidecars, makes the published table of **p23, p28, p29, p32 and p35**
        STALE -- stage 9c then FAILS, which costs a `report.py` per pattern and
        a SECOND full sweep for a stage that has found nothing. The substance
        agrees with the price: a pin-only document (`p23/controls_pin.json`) or
        a table of rows (`p29/miri_arms.json`) has no verdict to give, and a red
        gate nobody can clear is how gates get switched off -- the same
        argument this docstring already makes for an unpinned sidecar.
        ⚠ **Promoting it to a SHOUT is a one-line change and it is the
        manager's call, not a defect here.**
      * **A FAILED verdict APPENDS to the pin verdict rather than replacing
        it** (`FRESH+VERDICT-FAILED`). Losing "the numbers are current" in order
        to say "the numbers are bad" would trade one fact for another; a reader
        of `controls_json` needs both. It fires on **zero** sidecars today,
        which is exactly why the must-fire arm is in `check_selftests` and not
        in this sweep.

    ⚠ **`measured_utc` (41 of 46) and `invariant` (41 of 46) are deliberately
    NOT wired in.** Nothing reads either; an unread timestamp is untidy, not
    unsound, and `derived_from_sha256` already answers the stronger question the
    timestamp does not (*against WHAT?*)."""
    head("9b. controls/*.json staleness pins AND verdicts")
    cdir = os.path.join(pdir, "controls")
    out = {}
    if not os.path.isdir(cdir):
        print("    no controls/ directory")
        return out
    blobs = sorted(f for f in os.listdir(cdir) if f.endswith(".json"))
    if not blobs:
        print("    controls/ ships no .json sidecar")
        return out
    noverdict = []
    for f in blobs:
        rel = os.path.relpath(os.path.join(cdir, f), REPO)
        try:
            doc = json.load(open(os.path.join(cdir, f)))
        except (OSError, ValueError) as e:
            out[f] = "UNREADABLE"
            rep.fail("tables", f"{rel}: not readable as JSON ({e})")
            continue
        # THE VERDICT READ (TASK_164 item A), taken from the RAW document --
        # before the coercion below turns a non-object into `{}` -- so a sidecar
        # that is not a JSON object is reported rather than silently emptied.
        # Wrapped, because a malformed document must be REPORTED, not crash the
        # gate (`.memory/03-measurement.md` entry 19).
        try:
            vverdict, vdetail = control_json_verdict(doc)
        except Exception as e:                                   # noqa: BLE001
            vverdict, vdetail = "FAILED", [
                f"reading this sidecar's verdict raised "
                f"{type(e).__name__}: {str(e)[:200]}"]
        doc = doc if isinstance(doc, dict) else {}
        meta = doc.get("pin") if isinstance(doc.get("pin"), dict) else {}
        fix = meta.get("regenerate") or "re-run its generator in `controls/`"
        pin = doc.get("derived_from_sha256")
        gpin = doc.get("gate_source_sha256")
        if isinstance(pin, dict):
            moved = sorted(k for k, v in pin.items()
                           if os.path.exists(os.path.join(REPO, k))
                           and sha256_file(os.path.join(REPO, k)) != v)
            gone = sorted(k for k in pin
                          if not os.path.exists(os.path.join(REPO, k)))
            if moved:
                out[f] = "STALE"
                rep.fail("tables",
                         f"{rel} is STALE: {len(moved)} of "
                         f"{len(pin)} pinned source(s) moved under it "
                         f"({moved[:5]}), so its numbers were NOT taken "
                         f"against this tree. Fix: {fix}")
            elif gone:
                out[f] = "MISSING-SOURCES"
                rep.shout("tables",
                          f"{rel} pins {len(gone)} of {len(pin)} source(s) "
                          f"that are ABSENT, so its pin cannot be checked and "
                          f"its numbers are UNDATED: {gone[:5]}"
                          + (f". Restore with: {meta['restore_missing']}"
                             if meta.get("restore_missing") else ""))
            else:
                out[f] = "FRESH"
                rep.ok(f"{rel} pins {len(pin)} source(s) by "
                       f"`derived_from_sha256`, all matching this tree")
        elif isinstance(gpin, dict):
            if gpin != source_sha:
                out[f] = "STALE"
                moved = sorted(k for k in set(gpin) | set(source_sha)
                               if gpin.get(k) != source_sha.get(k))
                rep.fail("tables",
                         f"{rel} is STALE: it was taken against a different "
                         f"gate `source_sha256` ({len(moved)} file(s) moved: "
                         f"{moved[:5]}). Fix: {fix}")
            else:
                out[f] = "FRESH"
                rep.ok(f"{rel} pins this run's gate `source_sha256`")
        else:
            out[f] = "UNPINNED"
            rep.shout("tables",
                      f"{rel} carries NO staleness pin, so nothing can tell "
                      f"whether its numbers were taken against the sources "
                      f"that are in the tree now. Write a top-level "
                      f"`derived_from_sha256` -- a `{{repo-relative path: "
                      f"sha256}}` dict naming everything the numbers derive "
                      f"from -- from the generator that emits the file; "
                      f"`patterns/p23-partition/controls/sweep_fit.py::"
                      f"derived_from` is the shape to copy. Until then treat "
                      f"every figure quoted from it as UNDATED.")
        # --- and what the sidecar CONCLUDED (TASK_164 item A) --------------
        if vverdict == "FAILED":
            out[f] = f"{out[f]}+VERDICT-FAILED"
            rep.fail("tables",
                     f"{rel} REPORTS A FAILURE OF ITS OWN and nothing read it "
                     f"until TASK_164: "
                     + " | ".join(vdetail)
                     + f". The staleness pin above says only that these numbers "
                       f"were taken against THIS tree -- it says nothing about "
                       f"what they SAY, and 0 of 46 sidecars pin themselves, so "
                       f"a control that starts reporting problems moves nothing "
                       f"this stage hashes and prints FRESH. `problems` is a "
                       f"verdict and not a note field: 30 of 30 generators that "
                       f"write it exit 1 when it is non-empty. Fix the thing the "
                       f"control found, or -- if the entry is stale -- re-run its "
                       f"generator: {fix}")
        elif vverdict == "NO-VERDICT":
            noverdict.append(f)
    if noverdict:
        # PRINTED, not shouted: `controls_json` and `loud` are both rendered
        # into `results/tables/*.md`, so a shout here would make five patterns'
        # published tables stale and cost a second full sweep. See the docstring.
        print(f"    no verdict field (neither `problems` nor a "
              f"`summary` with `n`/`as_expected`) in {len(noverdict)} of "
              f"{len(blobs)} sidecar(s): {noverdict} -- their pins are checked "
              f"above, but nothing here reads a conclusion from them")
    return out


def check_miri(pdir, rep, contract, identity, modmod, indir, names,
               advtable=None):
    """`.memory/02-bench-rules.md`: Miri is mandatory for any pattern that has a
    trusted `unsafe` item at all, and *may never be skipped* when R4 and R5 are
    not byte-identical.

    **The second clause used to be the whole policy, and TASK_009_REVIEW showed
    why that was wrong.** "R4 and R5 are the same machine code, so R4 inherits
    R5's proof" is sound about codegen and unsound about the trusted base: R5's
    proof is only as good as its trusted `ensures`, and a trusted `ensures` need
    not be **complete** with respect to the operations its body performs.
    Measured (mirror x4):

        unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }

    with the contract, the twin and the pins all unchanged -- nothing licenses
    the `i + 1` read and no Verus stage can see it. Miri is the only backstop for
    that class, and the old policy made it optional **exactly when byte-identity
    holds**, i.e. exactly in the case this project reports as its headline
    result. Miri over all inputs costs about a minute, so the resolution is to
    run it whenever there is a trusted item, and keep the identity rule as the
    reason it can never be waived when R4 != R5.

    Three things changed at TASK_005, because between them they meant that the
    first pattern with a non-trivial proof could not be green by any route
    (TASK_003_REVIEW blocker 3):

    * **`norel` counts as byte-identical.** `norel` is "the same machine code
      linked at a different address" -- p01's own `spec.md` says exactly that
      about its O0 row. Requiring `exact` failed R4/R5 pairs that differ only in
      a `call rel32` displacement, which is not a semantic difference at all.
    * **Miri is actually run**, on a `nightly` toolchain installed beside the
      pinned one. R4 is plain unsafe Rust with no vstd dependency, so nightly's
      Miri can interpret its source; Miri checks *source* for UB and does not
      measure codegen, so the toolchain difference is not a confound. See
      TOOLCHAIN.md.
    * **A missing tool blocks a row, it does not fail the pattern.** Failing a
      whole pattern on a tool this box does not have is how gates get switched
      off; the row is recorded as a documented failure with the reason
      `spec.md` pins, and the verdict prints it.
    """
    head("8. Miri policy")
    cfg = contract.get("miri") or {}
    a, b = (cfg.get("pair") or ["unsafe", "verus"])[:2]
    pair = f"{a} vs {b}"
    o3 = [r for r in identity if r["pair"] == pair and r["opt"] == "O3"]
    if not o3:
        rep.fail("miri", f"no identity measurement for the R4/R5 pair {pair!r} "
                         f"at O3, so the Miri policy cannot be evaluated. "
                         f"spec.md's `miri.pair` must name a pair that "
                         f"`identity` also measures.")
        return {"required": None, "ran": False, "pair": pair}
    level = o3[0]["level"]
    idx = asm.IDENTITY_LEVELS.index(level)
    inherits = idx >= asm.IDENTITY_LEVELS.index("norel")
    trusted = _trusted_items(pdir, contract)
    n_trusted = sum(len(v) for v in trusted.values())
    axioms = _axiom_items(pdir, contract)
    n_axioms = sum(len(v) for v in axioms.values())
    out = {"pair": pair, "identity_o3": level, "inherits_proof": inherits,
           "trusted_items": trusted, "axiom_decls": axioms,
           # TASK_107 §C: WHAT RAN. The old defect was not the seed; it was that
           # nothing recorded which seed answered, so *"no UB"* meant "no UB at
           # whatever draw miri felt like". `overridden_ambient` is here because
           # the flags are set, not appended: if the invoking shell exported its
           # own `MIRIFLAGS` the record must say the gate ignored it, or the
           # recorded string would be a claim about a run that did not happen.
           # `null` means the variable is UNSET in the child, which is not the
           # same configuration as `""` -- the two time ~4.6x apart on p42.
           # ⚠ WHICH of the two is slower is not a property of `MIRIFLAGS`;
           # TASK_114 measured it the other way round from TASK_107 and a decoy
           # variable behaves the same. See `MIRI_FLAGS` and `runs[].seconds`.
           "miriflags": " ".join(MIRI_FLAGS) or None,
           "miriflags_removed_ambient": os.environ.get("MIRIFLAGS"),
           # The thing that actually moved between TASK_102 and TASK_107. Miri's
           # unseeded default address assignment is deterministic *for a given
           # miri*, so the version is what makes a green row reproducible; the
           # seed sentence in `.memory/00-environment.md` went stale because
           # this string changed, not because a draw did.
           "miri_version": _miri_version()}

    # DERIVED, and it overrides the declared flag in one direction only: the
    # flag can add Miri, never remove it.
    why_required = []
    if n_trusted:
        why_required.append(
            f"this pattern has {n_trusted} trusted item(s) {trusted} whose "
            f"`ensures` need not be COMPLETE with respect to the unchecked "
            f"operations their bodies perform (TASK_009_REVIEW x4)")
    if n_axioms:
        why_required.append(
            f"this pattern declares {n_axioms} hand-written axiom(s) {axioms} "
            f"about real Rust semantics that Verus does not check and no gate "
            f"stage probes (RECAP \"Owed\" 0); the axiom is ghost but the call "
            f"it licenses is executed, so Miri is the only backstop")
    if not inherits:
        why_required.append(
            f"R4 and R5 differ at O3 (identity {level!r}), so R4 does not "
            f"inherit R5's discharged obligations at all")
    if cfg.get("required"):
        why_required.append("spec.md sets miri.required")
    out["required_because"] = why_required

    if not why_required:
        # ⚠⚠ THE SENTENCE THIS BRANCH USED TO PRINT WAS TOO STRONG, AND IT WAS
        # MADE TO PRINT (`TASK_084_REVIEW` major 3, route G; narrowed here at
        # TASK_096). It read:
        #
        #     "... this pattern has NO trusted item and NO hand-written axiom,
        #      so there is no trusted `ensures` whose incompleteness Miri would
        #      have to backstop -- Miri not required."
        #
        # Both counts above are PATTERN-LOCAL. `_trusted_items` keys on
        # `#[verifier::external_body]` in this pattern's own (and
        # `#[path]`-included) sources, and `_axiom_items` matches
        # DECLARATIONS. **A proof that merely CALLS a vstd
        # `assume_specification` declares nothing**, so both are 0 and the old
        # sentence's second clause -- "there is no trusted `ensures`" -- is
        # false of it. The pinned vstd's
        # `assume_specification[str::from_utf8_unchecked] requires
        # valid_utf8(v@) ensures res.spec_bytes() =~= v@` is verbatim the
        # `ensures` a local wrapper would write, and
        # `std_specs/slice.rs`'s `assume_specification<T>[ <usize as
        # SliceIndex<[T]>>::index ]` is what licenses every `v[i]` in every
        # verified body in this tree. That is RECAP "Owed" 0's SIXTH ROUTE.
        #
        # Two things are NOT changed here, deliberately:
        #
        #   * **it is still not a failure.** The policy is a derived one and
        #     the honest derivation says only that no *pattern-local* trusted
        #     `ensures` exists. Failing here would hard-fail a legitimate
        #     zero-trusted-item pattern with no route out, which is the shape
        #     `MAX_TWIN_JUSTIFICATIONS` was deleted for.
        #   * **`_axiom_items` is not widened to "vstd specs used".** That was
        #     refuted by census: the pinned vstd holds 402 `assume_specification`
        #     sites, "relied upon" is undecidable from the text (Verus inserts
        #     coercions that never appear in source), and every rung depends on
        #     the same vstd core (`.memory/04-verus.md`, TASK_055_REVIEW -- the
        #     second column "must not be reinstated").
        #
        # What changes is that the sentence now says what it can support and
        # SHOUTS the residual, so the branch cannot be read as a clean bill of
        # health. Zero patterns reach it today: all 24 gate records carry
        # `n_trusted >= 1` (censused at TASK_096), so this moves no verdict.
        rep.ok(f"R4/R5 ({pair}) are the same machine code at O3 (identity "
               f"{level!r} >= 'norel') and this pattern declares NO "
               f"PATTERN-LOCAL trusted item and NO PATTERN-LOCAL hand-written "
               f"axiom, so there is no trusted `ensures` OF THIS PATTERN'S OWN "
               f"whose incompleteness Miri would have to backstop -- Miri not "
               f"required by the derived policy. spec.md: "
               f"{cfg.get('reason', '(no reason given)')}")
        rep.shout("miri",
                  f"...and that `ok` is a claim about PATTERN-LOCAL "
                  f"declarations ONLY. A proof that merely CALLS a vstd "
                  f"`assume_specification` declares nothing, so it counts 0 "
                  f"here while its executed call rests entirely on an upstream "
                  f"`ensures` -- RECAP \"Owed\" 0's sixth route. Set "
                  f"`miri.required: true` in spec.md for any pattern whose "
                  f"kernel reaches memory through a vstd-specified operation "
                  f"rather than through a local wrapper; the flag can only ADD "
                  f"Miri, never remove it. This shout is the only thing "
                  f"standing between that route and a silent green verdict, "
                  f"and no pattern in the tree reaches this branch today.")
        out.update(required=False, ran=False, local_only=True)
        return out
    if (n_trusted or n_axioms) and cfg.get("required") is False:
        rep.fail("miri",
                 f"spec.md sets miri.required=false, but this pattern has "
                 f"{n_trusted} trusted item(s) {trusted} and {n_axioms} "
                 f"hand-written axiom(s) {axioms}, which makes Miri "
                 f"mandatory whatever the R4/R5 identity level is "
                 f"(`.memory/02-bench-rules.md`, revised at TASK_010): a trusted "
                 f"`ensures` need not cover every unchecked operation its body "
                 f"performs, byte-identity propagates that rather than excusing "
                 f"it, and Miri is the only backstop. The gate runs Miri anyway; "
                 f"fix the pin so it does not claim otherwise.")

    out["required"] = True
    print(f"    Miri is REQUIRED because: " + "; ".join(why_required))
    print(f"    MIRIFLAGS = "
          + (" ".join(MIRI_FLAGS) if MIRI_FLAGS else
             "<UNSET>  -- deliberately, not by omission: the gate must not "
             "inherit the invoking shell's flag set. ⚠ It does NOT pin the "
             "run: p42's Miri row is a two-state function of the environment "
             f"block, ~75 s vs ~340 s with a {MIRI_TIMEOUT}s budget between "
             "them, and setting or unsetting this variable CHANGES that state "
             "without controlling it (mechanism OPEN, and two published ones "
             "were wrong). Read `miri.runs[].seconds` in the gate record for "
             "which state this run got. See MIRI_FLAGS.")
          + (f"   (REMOVING the ambient MIRIFLAGS="
             f"{os.environ['MIRIFLAGS']!r})"
             if os.environ.get("MIRIFLAGS") else "")
          + f"\n    miri      = {_miri_version()}")
    srcs = cfg.get("sources") or [buildmod.RUST_SRC.get(a, f"{a}.rs")]
    # source file -> the matrix rung stage 4 measured, so a per-input hang
    # declaration can be tested against the rung Miri is about to interpret
    # rather than against the pattern as a whole.
    #
    # ⚠ THE SENTENCE THAT USED TO BE HERE WAS FALSE, in the function TASK_069
    # already had to de-falsify a comment in (TASK_077_REVIEW m1). It said
    # *"`verus.rs` is not in the measured-cell set for this purpose only when a
    # pattern renames it; the map is `build.py`'s, so the two cannot drift."*
    # `verus.rs` IS a measured cell (`build.py::RUST_SRC` maps it to the
    # `verus` rung), a pattern CANNOT rename it (`RUST_SRC` is module-level and
    # takes no per-pattern input), and the two things that really can drift are
    # `spec.md`'s `miri.sources` and `RUST_SRC`, which are independent pins --
    # `miri.sources` is a free list of file names and nothing requires its
    # entries to be rung sources at all. Today it is `['unsafe.rs']` on 22 of
    # 22 patterns.
    #
    # The drift is handled, but by the CODE rather than by that argument:
    # `rung_of.get(s)` returns None for any name `RUST_SRC` does not carry, and
    # `rung is None` blocks the row. Fail-closed, and the block reason names the
    # file.
    rung_of = {v: k for k, v in buildmod.RUST_SRC.items()}
    blocked = cfg.get("blocked_reason")
    sysroot = _miri_sysroot() if os.path.exists(MIRI_BIN) else None
    if sysroot is None:
        why = (blocked or
               f"miri not found at {MIRI_BIN}; install with `rustup toolchain "
               f"install {NIGHTLY} --component miri` (see TOOLCHAIN.md)")
        for s in srcs:
            rep.block("miri", s, why)
        out.update(ran=False, available=False, blocked_reason=why)
        return out

    scratch = os.path.join(REPO, ".temp", "check", buildmod.pattern_id(pdir),
                           "miri")
    os.makedirs(scratch, exist_ok=True)
    runs = []
    for s in srcs:
        spath = os.path.join(pdir, s)
        if not os.path.exists(spath):
            rep.fail("miri", f"miri.sources names {s}, which is not in the tree")
            continue
        for nm in names:
            probe = _probe_input(os.path.join(indir, nm), MIRI_PROBE_ITERS,
                                 os.path.join(scratch, f"miri.{nm}"))
            mod = sb(modmod.build, probe)
            # --- does the rung MIRI RUNS hang on this input? -----------------
            # TASK_077, RECAP "Owed" 19a. `expected_hang` is per INPUT; its
            # Miri consequence is per RUNG, and until now the code assumed the
            # two were the same thing.
            #
            # ⚠ THE REASON THIS BLOCK USED TO PRINT WAS STRUCTURALLY FALSE FOR
            # EVERY PATTERN THIS TREE CAN HOLD. It said "so R4 does not return
            # under Miri either". `.memory/01-ladder.md` puts the modelled bug
            # in **R1 only** -- every Rust rung carries the fix -- so
            # `miri.sources` always names a rung that TERMINATES, and the row
            # was blocked for a reason that could not apply. Measured on p22,
            # the only pattern that declares a hang: `miri` on the shipped
            # `unsafe.rs` over the clamped `adversarial-full.bin` probe gives
            # **rc=0, no UB, 0.2 s**, printing 15820751917455319872, which is
            # exactly what `model.py` predicts. Stage 4 agrees and says which
            # rungs really hang: `c-gcc` and `c-clang` at both opt levels, and
            # no Rust rung at all. **Cost of the old reading: one genuinely
            # unchecked Miri row per declared hang.**
            #
            # So the block is now conditioned on a MEASUREMENT rather than on a
            # declaration -- `_hung_rungs` reads stage 4's own `hung` column --
            # and it still fires, unchanged, in the case it was written for: an
            # input on which the rung Miri interprets is itself one of the
            # rungs that ran forever. `None` means stage 4 said nothing about
            # this input (it is not adversarial, or the matrix was empty), in
            # which case the declaration is all there is and the conservative
            # answer is the old one.
            #
            # ⚠ **AND THE ROW IS BLOCKED WHEN STAGE 4 MEASURED NOTHING FOR THIS
            # RUNG**, which TASK_077 did not do (TASK_077_REVIEW m2). The first
            # version tested `rung not in hung`, so "this rung terminated" and
            # "this rung was never measured" were the same answer and the gate
            # ran Miri on the strength of a measurement that did not exist. Now
            # `_hung_rungs` returns `measured` as well and there are FOUR
            # outcomes: no stage-4 rows at all (block), the rung is not in the
            # measured set (block), the rung is in the hung set (block), or the
            # rung was measured and terminated (run).
            declared = sbg_opt(mod, "expected_hang", False)
            stage4 = _hung_rungs(advtable, nm) if declared else None
            hung, measured = stage4 if stage4 else (None, None)
            rung = rung_of.get(s)
            if declared and (stage4 is None or rung is None
                             or rung not in measured or rung in hung):
                # Blocked UP FRONT rather than after MIRI_TIMEOUT: a rung that
                # does not terminate natively will not terminate under an
                # interpreter either, and `MIRI_PROBE_ITERS` cannot help -- it
                # clamps the number of kernel CALLS, and the first call is the
                # one that never returns. Waiting 180 s to learn that, then
                # reporting a payload-size reason that is false, is worse than
                # saying so. A BLOCKED row, so the verdict reads
                # PASS-WITH-BLOCKED-ROWS and the row is loud.
                #
                # ⚠ TASK_068 asserted here that this "cannot be used to skip a
                # Miri check quietly, because only an `adversarial*` input may
                # declare a hang and stage 4 fails the declaration unless a
                # cell really did run forever". **That was FALSE as written**
                # (TASK_068_REVIEW B2): "really did run forever" was only ever
                # evaluated against the author's own `run.timeout_s`, which had
                # no floor, so a 3.5 s cell under a 2 s budget satisfied stage
                # 4 with 0 failures and switched this check off. It is true
                # NOW, and only because of what TASK_069 added: a
                # `RUN_BUDGET_FLOOR` on the pin, and `_confirm_hang`, which
                # re-runs a hung cell per (rung x opt) at 10x the budget and
                # FAILS if any terminates. A false comment is what the next
                # reader trusts instead of reading the code, so it is fixed
                # here as well as in the code it described.
                common = (f"model.py declares this input non-terminating "
                          f"(expected_hang) and ")
                tail = ("Blocked conservatively. This input is unchecked for "
                        "UB; the others are not.")
                if stage4 is None:
                    why = (common + f"stage 4 recorded no per-rung result for "
                           f"it, so the gate cannot tell whether the rung Miri "
                           f"runs ({s}) is one of the rungs that hangs. " + tail)
                elif rung is None:
                    why = (common + f"miri.sources names {s}, which is not a "
                           f"file `build.py::RUST_SRC` maps to a matrix rung "
                           f"({sorted(rung_of)}), so stage 4's per-rung hang "
                           f"column cannot be indexed for it. " + tail)
                elif rung not in measured:
                    why = (common + f"stage 4 produced NO ROW for the rung Miri "
                           f"runs ({s} -> {rung!r}); it measured "
                           f"{sorted(measured)}. That is not the same answer as "
                           f"'{rung} terminated' and must not be read as one "
                           f"(TASK_077_REVIEW m2). " + tail)
                else:
                    why = (common + f"stage 4 measured "
                           f"{sorted(hung)} as the rung(s) that did not "
                           f"terminate, which includes the rung Miri runs "
                           f"({s} -> {rung!r}). n_iters is clamped to "
                           f"{MIRI_PROBE_ITERS} but the FIRST kernel call is "
                           f"the one that hangs. This input is unchecked for "
                           f"UB; the others are not.")
                rep.block("miri", f"{s} on {nm}", why)
                runs.append(dict(source=s, input=nm, blocked=why,
                                 hung_rungs=None if hung is None
                                 else sorted(hung),
                                 measured_rungs=None if measured is None
                                 else sorted(measured)))
                continue
            if hung:
                print(f"    {s} on {nm}: input declares expected_hang, and "
                      f"stage 4 measured {sorted(measured)}: the hang is in "
                      f"{sorted(hung)} and NOT in {rung!r} -- running Miri "
                      f"instead of blocking the row (TASK_077).")
            try:
                # ⚠ `MIRIFLAGS` is REMOVED when `MIRI_FLAGS` is empty, and SET
                # (never appended) when it is not. Both halves matter and the
                # first is the surprising one: `MIRIFLAGS=""` is a DIFFERENT
                # configuration from `MIRIFLAGS` unset -- the two time ~4.6x
                # apart on p42's `adversarial-wincap.bin` -- so
                # `menv["MIRIFLAGS"] = " ".join(())` would NOT be equivalent to
                # popping the key. ⚠⚠ **WHICH of the two is the slow one is
                # NOT a property of `MIRIFLAGS`**: `TASK_114` measured the
                # assignment the other way round from `TASK_107`, three repeats
                # each way, and a DECOY variable unrelated to Miri behaves
                # identically. See `MIRI_FLAGS`; the mechanism is OPEN and the
                # per-row wall time is recorded so the state is at least
                # visible. An ambient value from the invoking shell is
                # discarded so the configuration belongs to `check.py` and not
                # to the shell, and is recorded in `miriflags_removed_ambient`.
                menv = dict(os.environ)
                menv.pop("MIRIFLAGS", None)
                if MIRI_FLAGS:
                    menv["MIRIFLAGS"] = " ".join(MIRI_FLAGS)
                t0 = time.time()
                r = subprocess.run(
                    [MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
                     "-Zmiri-disable-isolation", spath, "--", probe],
                    capture_output=True, text=True, timeout=MIRI_TIMEOUT,
                    cwd=pdir, env=menv)
                secs = round(time.time() - t0, 1)
            except subprocess.TimeoutExpired:
                why = (f"miri did not finish within {MIRI_TIMEOUT}s. `n_iters` "
                       f"is clamped to {MIRI_PROBE_ITERS} but the payload is "
                       f"not, and the driver decodes it element by element "
                       f"under interpretation. This input is unchecked; the "
                       f"others are not.")
                rep.block("miri", f"{s} on {nm}", why)
                # `seconds` here is the CAP, not a measurement -- see the key's
                # comment below for why a Miri wall time is recorded at all.
                runs.append(dict(source=s, input=nm, blocked=why,
                                 seconds=float(MIRI_TIMEOUT)))
                continue
            ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr
            # ⚠ TASK_118 §E, from TASK_116 MINOR 6. A Miri LEAK is neither
            # "Undefined Behavior" nor "error: unsupported", so `ub` read
            # `False` for one and the leak was caught only by the NEXT branch,
            # on the exit code. The VERDICT was right; the RECORD showed
            # nothing. A reader auditing `results/gate/*.json` by the `ub` key
            # -- the key you would search -- could not tell a leaking tree from
            # a clean one, and the pattern where that matters most is p42,
            # whose entire subject is a leak and whose Miri run is the only
            # mechanical leak check either of its top two rungs has.
            #
            # `leak` is recorded UNCONDITIONALLY, so the record answers the
            # question on every row rather than only on the failing ones, and
            # it gets its own failure branch ABOVE the exit-code branch so the
            # message names what happened instead of saying "miri exited 1,
            # model expects 0".
            #
            # ⚠ It also closes a small hole rather than only improving prose,
            # and the hole passes `.memory/02-bench-rules.md`'s "could this
            # happen by accident?" test: on an input whose model declares a
            # NON-ZERO expected exit, a leaking rung whose exit happened to
            # equal that code used to reach `got != want` and PASS. No
            # committed row is in that position today -- 186 rows expect 0,
            # five expect 5, one expects 7, and no committed stderr contains
            # `memory leaked` -- so this changes no shipped verdict. It is a
            # trap laid for the next pattern, not a repair of this one.
            #
            # Regression control, with an arm that MUST FIRE (it runs THIS
            # `check_miri` and `git show <pre-fix>:harness/check.py`'s side by
            # side on a mutant of p42's `unsafe.rs` and shows the old record
            # had no `leak` key at all while its `ub` read False):
            # `patterns/p42-goto-cleanup/controls/miri_leak_key.py`.
            # ⚠ This comment cited `.temp/t119/miri_leak_key.py` until
            # TASK_121. TASK_123 promoted the probe into p42's `controls/`; the
            # old path was gitignored, so the citation pointed at nothing a
            # fresh clone has. Corrected here rather than in its own task
            # because ANY `check.py` edit stales all 26 gate records
            # (TASK_119 measured 0 -> 25 from a one-line docstring edit), so a
            # comment fix is batched into a change that is already paying for
            # the sweep.
            leak = "memory leaked" in r.stderr
            got = r.stdout.strip()
            want = (sbg(mod, "expected_stdout") or "").strip()
            want_exit = sbg(mod, "expected_exit")
            rec = dict(source=s, input=nm, exit=r.returncode,
                       expected_exit=want_exit, ub=ub, leak=leak,
                       # ⚠⚠ TASK_119 §B, from TASK_114 B2.3. WALL CLOCK, AND
                       # IT IS HERE FOR ONE REASON: p42's Miri row is a
                       # TWO-STATE function of the environment block -- ~75 s
                       # against ~340 s, 4.6x, reproduced four times each way
                       # -- and `MIRI_TIMEOUT` sits at 180 s BETWEEN the two
                       # states. So the same source, the same input and the
                       # same interpreter can be a green row or a BLOCKED one
                       # depending on the invoking shell, and `miriflags`,
                       # `miriflags_removed_ambient` and `miri_version` are
                       # IDENTICAL in both states: the record could not say
                       # which one you got. The mechanism is OPEN and this
                       # project has already published TWO wrong ones for it
                       # ("seed-vs-seed", then "`MIRIFLAGS` presence"), so
                       # this key does not explain the state -- it makes the
                       # state VISIBLE, which is the whole claim.
                       # ⚠ It is deliberately the only wall-clock number in
                       # the gate record, so it will differ on every re-gate.
                       # That churn is the price of the row above being
                       # readable at all; nothing compares it, nothing hashes
                       # it, and no verdict depends on it.
                       seconds=secs,
                       stdout=got, model_stdout=want,
                       stderr=re.sub(r"\s+", " ", r.stderr.strip())[:400])
            # TASK_078, from TASK_077_REVIEW m4: the record has to show what
            # UN-blocked the row, not only what blocked one. Until now
            # `hung_rungs` was written on the `rep.block` branch alone, so
            # p22's `miri.runs[1]` carried `ub`/`exit`/`stdout` and no trace of
            # the stage-4 measurement that let Miri run at all -- a reviewer
            # reading `results/gate/` could not tell a row that was never
            # blocked from one this change un-blocked. TASK_068 added
            # `run_timeout_s` and `expected_hang` to the record for exactly this
            # reason. `expected_hang` False -> both keys absent, as before.
            if declared:
                rec.update(expected_hang=True,
                           hung_rungs=None if hung is None else sorted(hung),
                           measured_rungs=(None if measured is None
                                           else sorted(measured)))
            runs.append(rec)
            # The exit code is compared to the MODEL'S, and stdout is compared
            # unconditionally. TASK_051_REVIEW M6: until then the chain read
            # `returncode != 0 and expected_exit == 0` / `returncode == 0 and
            # got != want`, so on an input whose model expects a NON-ZERO exit
            # neither the code nor stdout was ever compared -- and the `ok` line
            # below asserted that stdout "matches the model" anyway. The
            # reviewer demonstrated it with a real Miri run of p01's R4 over
            # `adversarial-shortlen.bin` from a mutant driver that panics
            # instead of exiting 5: rc=101, no `Undefined Behavior`, reported
            # green. Reachable on p01 and p02, whose adversarial inputs declare
            # `expected_exit` 5 and 7 and are Miri-stage inputs.
            #
            # It passes `.memory/02-bench-rules.md`'s "could this happen by
            # accident?" test: a rung that panics for the wrong reason, dies of
            # a signal, or exits with a different non-zero code is an honest
            # mistake, and Miri runs with debug-assertions ON, so an arithmetic
            # overflow that the -O3 cells mask is a panic here (p18's own bug
            # class). Regression check:
            # `patterns/p18-varint-shift/controls/miri_exit_hole.py`.
            if ub:
                rep.fail("miri", f"{s} on {nm} (n_iters={MIRI_PROBE_ITERS}): "
                                 f"Miri reports UB -- {rec['stderr'][:300]}")
            elif leak:
                rep.fail("miri", f"{s} on {nm} (n_iters={MIRI_PROBE_ITERS}): "
                                 f"Miri reports a MEMORY LEAK at process exit "
                                 f"(miri exited {r.returncode}, model expects "
                                 f"{want_exit}) -- {rec['stderr'][:300]}")
            elif r.returncode != want_exit:
                rep.fail("miri", f"{s} on {nm}: miri exited {r.returncode}, "
                                 f"model expects {want_exit} -- "
                                 f"{rec['stderr'][:300]}")
            elif got != want:
                rep.fail("miri", f"{s} on {nm}: miri printed {got!r}, model "
                                 f"predicts {want!r}")
            else:
                rep.ok(f"miri {s} on {nm:28s} n_iters={MIRI_PROBE_ITERS}: no UB, "
                       f"exit {r.returncode} and stdout {got!r} both match the "
                       f"model")
    out.update(ran=True, available=True, sysroot=sysroot,
               probe_iters=MIRI_PROBE_ITERS, runs=runs)
    return out


# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--skip", action="append", default=[],
                    help="input stem to skip, e.g. --skip large")
    ap.add_argument("--cells", default="all", choices=["all", "measured"])
    ap.add_argument("--no-callgrind", action="store_true",
                    help="skip step 3b; the run then FAILS, by design")
    ap.add_argument("--no-verus-mutants", action="store_true",
                    help="skip steps 5c, 5c-req and 5c-twin; the run then "
                         "FAILS, by design")
    a = ap.parse_args()

    pdir = buildmod.pattern_dir(a.pattern)
    # Per-pattern, not module-level: the R1h cells exist only for a pattern
    # that ships `c/kernel_hardened.c` and the R2v control only for one that
    # ships `safe_naive_verus.rs` (`.memory/05-layout.md` calls it OPTIONAL,
    # but the module-level ALL_CELLS treated it as mandatory and failed four
    # builds on any pattern without one).
    cells = (buildmod.all_cells(pdir) if a.cells == "all"
             else buildmod.measured_cells(pdir))
    opts, modes = buildmod.OPTS, buildmod.MODES

    # `--skip` used to re-open blocker B3 from the command line: skipping the
    # adversarial stems meant the contract was never evaluated on them, nothing
    # was recorded, and the verdict was PASS. The adversarial inputs are the
    # ones the proof-domain rules exist for.
    all_stems = [f[:-4] for f in os.listdir(os.path.join(pdir, "inputs"))
                 if f.endswith(".bin")]
    bad_skip = sorted(s for s in a.skip if s.startswith("adversarial"))
    if bad_skip:
        raise SystemExit(
            f"check.py: --skip {bad_skip} refused. The adversarial inputs are "
            f"precisely the ones `.memory/02-bench-rules.md` rule 1 exists to "
            f"evaluate ('every input includes the adversarial ones'), and "
            f"skipping them silently un-checks the proof domain while the "
            f"verdict still reads PASS.")
    unknown = sorted(s for s in a.skip if s not in all_stems)
    if unknown:
        raise SystemExit(f"check.py: --skip {unknown}: no such input stem")

    indir, good, adv = inputs_of(pdir, skip=a.skip)
    contract, contract_raw = read_contract(pdir)
    contract_sha = hashlib.sha256(contract_raw.encode()).hexdigest()
    modmod = load_model(pdir, contract)

    print(f"check.py: {os.path.basename(pdir)}")
    print(f"  cells   {cells}")
    print(f"  opts    {opts}   modes {modes}")
    print(f"  inputs  good={good} adversarial={adv}")
    print(f"  model   {contract.get('model', 'model.py')}")
    print(f"  contract sha256 {contract_sha}")
    if a.skip:
        print(f"  SKIPPED {a.skip} -- this run does not certify those inputs")

    rep = Report()
    check_selftests(rep)
    audit = check_idiom(rep, pdir, contract)
    budgets = run_budgets(contract, rep, all_stems)
    if budgets:
        # `.get`, not `[...]`: `run_budgets` FAILS on a missing `why` and still
        # returns the budgets it parsed, so indexing here turned a clean gate
        # failure into a Python traceback with no verdict and no
        # `results/gate/*.json` at all -- the author lost the very message the
        # guard was written to print (TASK_068_REVIEW M5).
        print(f"  run budgets {budgets} s (RUN_TIMEOUT {RUN_TIMEOUT}s "
              f"otherwise) -- {contract['run'].get('why')}")

    if a.no_build:
        built = {}
        for c in cells:
            for o in opts:
                for m in modes:
                    p = buildmod.out_path(pdir, c, o, m, "unwind")
                    built[(c, o, m)] = p if os.path.exists(p) else None
        head("1. build the matrix")
        print(f"    --no-build: reusing {sum(1 for v in built.values() if v)}"
              f"/{len(built)} existing binaries")
        for k, v in built.items():
            if v is None:
                rep.fail("build", f"{k} missing and --no-build given")
        # Provenance: `--no-build` measures whatever is on disk, which may
        # predate the sources it is being checked against.
        srcs = ([os.path.join(pdir, f) for f in os.listdir(pdir)
                 if f.endswith((".rs", ".c", ".h"))]
                + glob.glob(os.path.join(pdir, "c", "*")) +
                glob.glob(os.path.join(REPO, "common", "driver.*")))
        newest = max((os.path.getmtime(s) for s in srcs if os.path.isfile(s)),
                     default=0)
        stale = sorted(os.path.basename(v) for v in built.values()
                       if v and os.path.getmtime(v) < newest)
        if stale:
            rep.fail("build", f"--no-build: {len(stale)} binary/binaries are "
                              f"older than the newest source file "
                              f"({stale[:6]}{'...' if len(stale) > 6 else ''}) "
                              f"-- this run would certify a source tree that "
                              f"was never compiled")
    else:
        built = check_build(pdir, rep, cells, opts, modes)

    good_models = build_models(modmod, indir, good, rep)
    adv_models = build_models(modmod, indir, adv, rep)
    all_models = dict(good_models)
    all_models.update(adv_models)
    hangs = check_hang_declarations(rep, all_models, budgets)

    check_checksums(built, rep, good_models, indir)
    digests = check_no_collapse(built, rep)
    slopes = check_marginal_ir(pdir, built, rep, modmod, contract, indir,
                               not a.no_callgrind)
    identity = check_identity(digests, rep, contract)
    advtable = check_adversarial(built, rep, adv_models, indir, cells,
                                 budgets)
    verus_res = check_verus_contract(pdir, rep, contract)
    callsite = check_call_site(pdir, rep, contract)
    clausemut = check_clause_deletion(pdir, rep, contract,
                                      not a.no_verus_mutants)
    reqmut = check_requires_strength(pdir, rep, contract,
                                     not a.no_verus_mutants)
    twins = check_trusted_twins(pdir, rep, contract, not a.no_verus_mutants)
    reqs, enss = derive_contract(pdir, rep, contract)
    domain = check_proof_domain(rep, all_models, reqs, enss)
    verus_ok = _verus_verified_files(pdir, rep, contract, verus_res)
    drivers = check_driver_identity(pdir, rep, contract, verus_ok, built,
                                    slopes.pop("_cg_files", None),
                                    slopes.pop("_cg_probe", None))
    san = check_sanitizers(pdir, rep, indir, all_models, budgets)
    # TASK_151. The same detector on the OTHER C arm -- until then no gate stage
    # ran one on `c/kernel_hardened.c` in any pattern, which is the cell that
    # already cost a wrong manager instruction (`p28d`, TASK_146 §1).
    san_h = check_sanitizers_hardened(pdir, rep, indir, all_models, budgets)
    # `advtable` carries stage 4's per-rung `hung` column, which is the
    # per-rung axis `model.expected_hang` does not have (TASK_077, "Owed" 19a).
    # Stage 4 runs at :6271 above, so the measurement is in hand by here.
    miri = check_miri(pdir, rep, contract, identity, modmod, indir,
                      sorted(all_models), advtable)
    # LAST of the Verus-facing stages, because it adjudicates every `_verus`
    # run the stages above made: `check_verus_contract`, `check_call_site`,
    # `check_clause_deletion`, `check_requires_strength`,
    # `check_trusted_twins` and `check_driver_identity` all reach it.
    verus_rc = check_verus_exit_codes(rep)

    # What `source_sha256` covers, and why each line is here. The rule is: a
    # file whose contents a committed claim depends on must be hashed, or a
    # stale record is undetectable -- which is the whole reason the key exists
    # (`.memory/02-bench-rules.md`, "a stale record is at least detectable by
    # comparing hashes against the tree").
    #
    # The last four lines were added at TASK_021, on the third sighting of the
    # gap. It stopped being hygiene at TASK_020:
    #
    #   * `inputs/gen.py` -- the inputs are gitignored and the GENERATOR is what
    #     is committed, so it is the only reproduction path for anything measured
    #     on a sweep blob. `patterns/p16-tlv-walk/NOTES.md` 10a states four
    #     swept `nrec` laws that are re-derivable ONLY by running this file; an
    #     edit changing what the sweep produces moved nothing in any gate
    #     artefact, because `check.inputs_of` also drops `sweep-*` from
    #     `inputs_checked`. Both halves of the record were blind to it at once.
    #   * `common/*.py` -- `slb.py`, imported by all six `model.py`s to decode
    #     the payload. Step 2 (the model checksum) is the gate's only
    #     load-bearing correctness check and this file sits inside it.
    #   * `controls/*` MINUS `.json` and `.log` -- committed control GENERATORS
    #     (`patterns/p08-overlap-move/controls/gen_controls.py`); same argument
    #     as `inputs/gen.py`, for cells that are not p05-style rungs.
    #     ⚠⚠ THIS GLOB READ `controls/*.py` UNTIL TASK_142, AND THE EXTENSION
    #     WHITELIST LEFT **TEN** COMMITTED CONTROL SOURCES IN NO DIGEST AT ALL:
    #     `build_controls.sh` (p06, p14, p18, p27), `verify_controls.sh` (p06,
    #     p14, p18) and p42's `affine_leak.rs`, `leak.sh`, `miri_seeds.sh`.
    #     They are not hygiene: those scripts carry the FLAG STRINGS the
    #     published control numbers were taken at, and `p42/NOTES.md` publishes
    #     two tables straight out of two of them -- the 352-point LSan sweep
    #     (section 3) and the seeds-0..7 Miri table with its must-fire arm
    #     (section 11c) -- so editing one without re-running it silently undates
    #     a published number and nothing fires. `.memory/05-layout.md`'s own
    #     adjudication of the p23 deviation already settled the principle in as
    #     many words: *"the convention was never Python only, it was a
    #     GENERATOR, not an ARTEFACT"*. The `.py` filter was the accident, and
    #     it under-delivered against that rule the moment a `.sh` arrived.
    #     ⚠⚠ `.json` AND `.log` ARE EXCLUDED ON PURPOSE, and the reason is not
    #     tidiness. They are control OUTPUTS, and stage 9b
    #     (`check_control_json_pins`) is the mechanism built for outputs: it
    #     re-hashes each sidecar's own `derived_from_sha256`. Hashing a
    #     GENERATED sidecar into the same run's `source_sha256` would put a file
    #     that this run's own stage 9b evaluates inside the digest certifying
    #     the run -- and for any sidecar using 9b's OTHER accepted key,
    #     `gate_source_sha256`, it is an unreachable fixpoint: writing the
    #     sidecar moves `source_sha256`, so the value it must record can never
    #     equal the value the next run computes. (No sidecar uses that key
    #     today -- all six use `derived_from_sha256` -- but 9b still accepts it,
    #     so the hazard is one sidecar away.) `p23/controls/controls.log` is out
    #     for the same reason plus its own: its `controls_pin.json` declares it
    #     deliberately un-hashable, because it embeds ASLR addresses, PIDs,
    #     BuildIds and absolute repo paths.
    #   * `common/layout/*.py` -- TASK_032. The code-layout control
    #     (`common/layout/README.md`): the population builder, the
    #     interleaved-schedule rule, the identical-copy noise floor, the
    #     32-byte loop-geometry fit and the pre-registration harness. The gate
    #     never imports it, but every withdrawn wall-clock row and RECAP
    #     finding 16 rest on what it measures, and it is the ONLY reproduction
    #     path for them -- the populations themselves live in gitignored
    #     `.temp/`. Same argument as `inputs/gen.py`: the generator is what is
    #     committed. `common/*.py` is non-recursive and does not reach it, so
    #     it needs its own line.
    #   * `verus_run.py` -- THE THIRD FILE, and it is named here rather than
    #     left implicit because it was not in the reported gap. It is R5's
    #     compiler driver (`build.py:VERUS_RUN`, `fixture.py`) *and* the process
    #     stages 5/5a-5d ask for Verus's verdict, so it decides both what R5's
    #     machine code is and what "verified" meant in this run. It is at the
    #     repo root, so `harness/*.py` never covered it.
    srcs = sorted(glob.glob(os.path.join(pdir, "*.rs"))
                  + glob.glob(os.path.join(pdir, "c", "*"))
                  + glob.glob(os.path.join(pdir, "*.md"))
                  + glob.glob(os.path.join(pdir, "model.py"))
                  + glob.glob(os.path.join(REPO, "common", "driver.*"))
                  + glob.glob(os.path.join(REPO, "harness", "*.py"))
                  + glob.glob(os.path.join(pdir, "inputs", "gen.py"))
                  + [p for p in glob.glob(os.path.join(pdir, "controls", "*"))
                     if not p.endswith((".json", ".log"))]
                  + glob.glob(os.path.join(REPO, "common", "*.py"))
                  + glob.glob(os.path.join(REPO, "common", "layout", "*.py"))
                  + glob.glob(os.path.join(REPO, "verus_run.py")))
    source_sha = {os.path.relpath(s, REPO): sha256_file(s)
                  for s in srcs if os.path.isfile(s)}
    # TASK_107 §E. LAST, and after `source_sha` exists because 9b compares
    # against it. These are PUBLISHING checks, not correctness ones -- see
    # `check_published_tables` for why they are in `check.py` rather than in
    # `measure.py` (measurement-hashed) or in a standalone script (nothing runs
    # it, which is how item 23 recurred twice).
    tables = check_published_tables(pdir, rep, contract_sha)
    # ⚠⚠ TASK_141: 9b MOVED ABOVE 9c, AND THE ORDER IS NOW LOAD-BEARING, NOT
    # COSMETIC. `controls_json` is one of the four keys `report.py` renders, so
    # 9c cannot compare the published table against THIS run's record until 9b
    # has decided them. With 9b after 9c -- the order until TASK_141 -- stage 9c
    # rendered from the PREVIOUS run's `controls_json` and a run that moved it
    # passed itself and poisoned the next. `p29` is the instance and it also
    # cost `p16` a run. See `check_table_render`.
    ctljson = check_control_json_pins(pdir, rep, source_sha)
    # THE FOUR KEYS `report.py` READS, as THIS run computes them -- measured by
    # mutation, not read off the source: `harness/tools/table_render_inputs.py
    # --reads` gives `{contract_sha256, controls_json, idiom_audit, loud}` on
    # 26 of 26. Everything here is a deterministic function of the committed
    # sources; `verdict`, `blocked` and `failures` are functions of the RUN and
    # are deliberately absent, because rendering one of those would make the
    # table an input to its own checker (`report.py::read_gate_loud`).
    # ⚠ `loud` is a SNAPSHOT taken here. `_check_render_inputs_final` below
    # re-compares it against the record actually written, so a future stage that
    # shouts after this point fails loudly instead of silently reopening the lag.
    gate_now = {"contract_sha256": contract_sha,
                "idiom_audit": audit,
                "controls_json": ctljson,
                "loud": [{"section": s, "message": m} for s, m in rep.loud]}
    # TASK_127. The CONTENT half of stage 9, and it must stay BEFORE the record
    # is written: see `check_table_render`'s docstring for why moving it after
    # the write reintroduces the self-reference it exists without.
    tabrender = check_table_render(pdir, rep, tables, gate_now)
    doc = {
        "pattern": os.path.basename(pdir),
        "skipped_inputs": a.skip,
        "inputs_checked": sorted(all_models),
        # TASK_005 A4: weakening a pin now shows up in review as a change to the
        # committed gate artefact, not only as a source diff.
        "contract_sha256": contract_sha,
        # TASK_068: the per-input run budgets this run actually used, and the
        # inputs `model.py` declared non-terminating. Both are empty on every
        # pattern that has neither, so the key is a no-op until a pattern needs
        # it -- and on one that does, the record says how long the gate was
        # willing to wait, which is otherwise invisible from `exit: null`.
        "run_timeout_s": budgets,
        "expected_hang": hangs,
        # TASK_016: the declared idiom, recorded so the gate artefact says what
        # the rungs were supposed to be spellings *of*. It is inside the hashed
        # block, so this is a convenience copy, not a second pin.
        "idiom": contract.get("idiom"),
        # TASK_020: where each declared spelling is and is not, measured against
        # the shipped rungs. The `required` numbers are REPORTING ONLY -- they
        # never fail and never enter the verdict. `forbidden_hits` DOES fail
        # since TASK_068, so a record with a non-zero one is a record of a
        # failed run. It is here so the audit is reproducible from the committed
        # tree and so a diff shows when the count moves; `idiom_audit`'s
        # docstring says why `forbidden` carries a verdict and `required`
        # cannot.
        "idiom_audit": audit,
        "source_sha256": source_sha,
        "derived_contract": {"requires": reqs, "ensures": enss,
                             # the harness default, and the rate actually used:
                             # a pattern's model.py may declare its own
                             # `min_ir_per_work` and p02 does (0.0625). Both are
                             # recorded, because reading only the first would
                             # misstate the floor this run enforced.
                             "alpha_ir_per_work": ALPHA_IR_PER_WORK,
                             "collapse_rate_ir_per_work":
                                 slopes.pop("_rate", ALPHA_IR_PER_WORK),
                             # what the floor was actually worth this run: the
                             # ratio of the tightest measured cell to the
                             # declared floor. 35.9x and 2.2e9x used to print
                             # identically (TASK_006_REVIEW D).
                             "collapse_work_unit":
                                 slopes.pop("_work_unit", "byte"),
                             "collapse_floor_min_declarable":
                                 slopes.pop("_bound",
                                            MIN_DECLARABLE_IR_PER_WORK),
                             "collapse_tightest_margin":
                                 slopes.pop("_tightest_margin", None)},
        "identity": identity,
        # TASK_107 §D (decided TASK_103), CORRECTED AT TASK_119 from TASK_114
        # B1: WHICH DRAW THIS RUN TOOK on the axis `marginal_ir_per_call` moves
        # along. `-O3 isolated` is NOT invariant -- it moves +-7 per rung with
        # the initial stack layout, and the pair swing is 14 -- so "re-run the
        # gate and compare" is not a reproduction test unless the two runs'
        # environments are known.
        #
        # ⚠⚠ THIS COMMENT USED TO SAY `same bytes AND same tuning_vars => the
        # marginal must match EXACTLY`, AND THAT RULE IS FALSE. It is now in 26
        # committed records. TASK_114 measured 3059/3059/3066/3066 at a
        # byte-identical `bytes = 3520` with identical (empty) `tuning_vars`,
        # varying only the NUMBER of variables -- period 4 in the count, being
        # the 32-byte period over the 8 bytes of one envp POINTER SLOT, which
        # `len(/proc/self/environ)` does not contain. See `_env_block`.
        #
        # The rule the key enables, restated on `envp_stack_bytes`
        # (= `bytes + 8*nvars`) and as a NECESSARY condition only:
        #   any of `envp_stack_bytes` / `tuning_vars` / `repo_path_bytes`
        #       differs  => the two runs took DIFFERENT draws and the marginals
        #       are NOT comparable. Compare `kernel_exclusive_ir` (in
        #       `results/pNN-*.json`, structurally immune: 0 of 288 triples
        #       moved) or re-run at the recorded layout. Measured sizes:
        #       +-7 Ir/call for the layout terms, +486.00 Ir/call for
        #       `tuning_vars` at an identical block length.
        #   all three equal => this record CANNOT TELL THE TWO DRAWS APART, so
        #       a mismatch is worth investigating as a real change. ⚠ That is
        #       NOT a proof that the draws are identical: `bytes` alone was
        #       believed sufficient and was falsified. SUFFICIENCY IS OPEN.
        # ⚠ It records; it does not pin. See `_env_block` for the domain, which
        #   the record now also carries as `marginal_ir_env.domain`.
        "marginal_ir_env": slopes.pop("_env_block", None),
        "marginal_ir_per_call": slopes,
        "verus": verus_res,
        "verified_call_site": callsite,
        "clause_deletion": clausemut,
        "requires_strength": reqmut,
        "verified_twins": twins,
        # TASK_097. Empty on every healthy run -- the key exists so that a run
        # in which Verus was satisfied and rustc was not says so in the record,
        # not only in the transcript. `.temp/t96/b1_verus_exit_census.py`
        # measured 50/50 shipped rows at rc=0, so this is latent on this tree.
        "verus_exit_anomalies": verus_rc,
        "proof_domain": domain,
        "driver_loops": drivers,
        "adversarial": advtable,
        "sanitizer": san,
        # TASK_151, stage 7h. ⚠ Its OWN key rather than a field of `sanitizer`,
        # for the same reason `table_render` is not a field of
        # `published_table`: the two arms are held to DIFFERENT expectations --
        # `sanitizer` is per-input from `model.sanitizer_expect`, this one is
        # `clean` on every input -- and merging them would make a reader think
        # one verdict covered both. `{}` for a pattern with no R1h (p01 only).
        "sanitizer_hardened": san_h,
        "miri": miri,
        # TASK_107 §E: the two published sidecars nothing had a detector for.
        # RECAP owed-item 23 predicted its own recurrence and was right twice.
        "published_table": tables,
        # TASK_127, stage 9c. ⚠ Its OWN key, not a field of `published_table`,
        # because the two verdicts mean different things and merging them would
        # make a reader think one `verdict` covered both. ⚠⚠ AND NOTE WHAT IS
        # SAFE ABOUT IT: `report.py` does not read this key, or `published_table`,
        # or `failures`, so recording the content verdict here cannot change the
        # render it is a verdict ABOUT. Anything added to `report.py` that reads
        # a key `check.py` writes recreates the oscillation this stage was fixed
        # for -- `report.py::read_gate_loud` carries the rule.
        "table_render": tabrender,
        "controls_json": ctljson,
        "failures": [{"section": s, "message": m} for s, m in rep.failures],
        "notes": rep.notes,
        "loud": [{"section": s, "message": m} for s, m in rep.loud],
        "blocked": rep.blocked,
    }
    # ⚠⚠ THE "OR FAIL LOUDLY WHEN IT CANNOT" HALF OF THE TASK_141 REPAIR.
    # Stage 9c rendered against `gate_now`, a snapshot of four keys taken at
    # 9b/9c time. This asserts that the record now being written carries exactly
    # those four values, i.e. that the comparison 9c made really was against
    # THIS run's record. It can only fire if a future stage is inserted after
    # 9c and moves one of them -- `loud` is the reachable one, since any
    # `rep.shout` appends to it -- and if it ever does, the one-run lag is back
    # and this says so instead of the next run finding out.
    _check_render_inputs_final(doc, gate_now, rep)
    # Re-derived, because the guard above may have appended to `rep.failures`
    # after the dict literal read it. ⚠ `failures` is NOT rendered by
    # `report.py` (measured, `--reads`), so re-deriving it cannot invalidate the
    # comparison stage 9c just made; `loud` would, which is why the guard is
    # allowed to `rep.fail` and forbidden to `rep.shout`.
    doc["failures"] = [{"section": s, "message": m} for s, m in rep.failures]
    # A diagnostic run must never overwrite the record of a full one. `--skip`
    # and `--no-callgrind` both make the run certify strictly less, so they get
    # their own file; only a complete run writes `<pattern>.json`. (Learned the
    # hard way at TASK_003: a `--skip small --skip large --no-callgrind` run,
    # used to *demonstrate* that those flags now fail the gate, clobbered the
    # passing artefact with its own deliberate FAIL.)
    partial = (bool(a.skip) or a.no_callgrind or a.no_build
               or a.no_verus_mutants or a.cells != "all")
    if rep.failures:
        verdict = "FAIL"
    elif partial:
        verdict = "PARTIAL"
    elif rep.blocked:
        verdict = "PASS-WITH-BLOCKED-ROWS"
    else:
        verdict = "PASS"
    doc["verdict"] = verdict
    doc["complete_run"] = not partial
    doc["invocation"] = " ".join(sys.argv[1:])
    # A partial record is SCRATCH and now lives under `.temp/`, not beside the
    # committed evidence. It used to be written to `results/gate/` with a
    # `.partial.json` suffix and gitignored, which is enough for `measure.py`
    # (it skips the suffix by name) and not enough for a human: six of them were
    # sitting there, four carrying `FAIL`, including a p05 record from an Aug-18
    # mid-edit run whose Verus errors are not live -- and the manager hit them
    # while surveying verdicts with a `results/gate/*.json` glob (TASK_056).
    # Nothing but a full run may write into `results/gate/` at all now.
    if partial:
        outdir = os.path.join(REPO, ".temp", "gate-partial")
        suffix = ".partial.json"
    else:
        outdir = os.path.join(REPO, "results", "gate")
        suffix = ".json"
    os.makedirs(outdir, exist_ok=True)
    outp = os.path.join(outdir, f"{os.path.basename(pdir)}{suffix}")
    with open(outp, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False, default=str)

    head("verdict")
    print(f"    results -> {os.path.relpath(outp, REPO)}")
    # The declared idiom, in full: every number below is a matched-pair delta
    # under it, and a rung that deviates is a different benchmark (TASK_016).
    for ln in idiom_lines(contract):
        print(ln)
    bar = "#" * 70
    if partial:
        print(f"\n{bar}\n#  PARTIAL RUN -- this certifies LESS than a full one "
              f"and its verdict\n#  is not a pass. Skipped inputs: "
              f"{a.skip or 'none'}; callgrind: "
              f"{'OFF' if a.no_callgrind else 'on'}; verus mutants: "
              f"{'OFF' if a.no_verus_mutants else 'on'}; build: "
              f"{'REUSED' if a.no_build else 'fresh'}; cells: {a.cells}.\n"
              f"#  Written beside the full-run record, never over it.\n{bar}")
    for s, m in rep.loud:
        print(f"    !!  [{s}] {m}")
    for bl in rep.blocked:
        print(f"    !!  BLOCKED [{bl['section']}] {bl['row']}: {bl['reason']}")
    for n in rep.notes:
        print(f"    note: {n}")
    if rep.failures:
        print(f"    {len(rep.failures)} FAILURE(S):")
        for s, m in rep.failures:
            print(f"      [{s}] {m}")
        # And the forbidden list again, beside the failures. A failing run is
        # the output that gets pasted into a report; the verdict header above it
        # is often scrolled past. The gate cannot tell whether a rung honours
        # the declaration -- printing it where the reader is looking is the
        # whole of what stage 0b can do about that (TASK_017 Part 2).
        for ln in idiom_lines(contract, keys=("forbidden",), why=False):
            print(ln)
        print("\ncheck.py: FAIL")
        return 1
    print(f"\ncheck.py: {verdict}")
    return 2 if partial else 0


_PROBE_CASES = [
    # (label, item source, item name, expected verdict)
    #
    # --- the baseline: the rig itself works ------------------------------
    ("plain / meaningful", """
#[verifier::external_body]
fn f(v: &[u8], i: usize) requires i < v@.len(), { unsafe { let _ = v[i]; } }
""", "f", "not a tautology"),
    ("plain / trivial", """
#[verifier::external_body]
fn f(v: &[u8], i: usize) requires 0 <= i, { unsafe { let _ = v[i]; } }
""", "f", "tautology"),
    # --- TASK_008_REVIEW major C: four shapes that HARD-FAILED the probe --
    ("generic <T: Copy>", """
#[verifier::external_body]
fn f<T: Copy>(v: &[T], i: usize) -> (r: T) requires i < v@.len(), { unsafe { *v.get_unchecked(i) } }
""", "f", "not a tautology"),
    ("where clause", """
#[verifier::external_body]
fn f<T>(v: &[T], i: usize) -> (r: T) where T: Copy
    requires i < v@.len(),
{ unsafe { *v.get_unchecked(i) } }
""", "f", "not a tautology"),
    ("lifetime <'a>", """
#[verifier::external_body]
fn f<'a>(v: &'a [u8], i: usize) -> (r: u8) requires i < v@.len(), { unsafe { *v.get_unchecked(i) } }
""", "f", "not a tautology"),
    ("&self receiver in an impl", """
pub struct Buf { pub b: Vec<u8> }
impl Buf {
    #[verifier::external_body]
    pub fn f(&self, i: usize) -> (r: u8)
        requires i < self.b@.len(),
    { unsafe { *self.b.get_unchecked(i) } }
}
""", "f", "not a tautology"),
    ("&self receiver, trivial clause -- still judged", """
pub struct Buf { pub b: Vec<u8> }
impl Buf {
    #[verifier::external_body]
    pub fn f(&self, i: usize) -> (r: u8)
        requires 0 <= i,
    { unsafe { *self.b.get_unchecked(i) } }
}
""", "f", "tautology"),
    # --- TASK_008_REVIEW major D: "Z3 could not prove it" was read as -----
    #     "it constrains a caller"
    ("slice len <= usize::MAX (needs the axiom a call site fires)", """
#[verifier::external_body]
fn f(v: &[u8], i: usize) requires v@.len() <= usize::MAX, { unsafe { let _ = v[i]; } }
""", "f", "tautology"),
    ("&mut slice len <= usize::MAX", """
#[verifier::external_body]
fn f(dst: &mut [u8], n: usize) requires old(dst)@.len() <= usize::MAX, { unsafe { let _ = dst[n]; } }
""", "f", "tautology"),
    ("bit-or bound (needs by (bit_vector))", """
#[verifier::external_body]
fn f(v: &[u8], off: usize) requires off <= (off | 1), { unsafe { let _ = v[off]; } }
""", "f", "tautology"),
    ("bit-and bound (needs by (bit_vector))", """
#[verifier::external_body]
fn f(v: &[u8], off: usize) requires (off & 0xff) <= 255, { unsafe { let _ = v[off]; } }
""", "f", "tautology"),
    ("nonlinear identity", """
#[verifier::external_body]
fn f(v: &[u8], n: usize) requires n as int * n as int >= 0, { unsafe { let _ = v[n]; } }
""", "f", "tautology"),
    # --- the residual this does NOT close: too weak, but not trivial ------
    ("off-by-one -- NOT a tautology, and 5c-twin is what catches it", """
#[verifier::external_body]
fn f(v: &[u8], i: usize) requires i <= v@.len(), { unsafe { let _ = v[i]; } }
""", "f", "not a tautology"),
]


def _probe_selftest():
    """End-to-end fixtures for the `requires`-tautology probe, one Verus run per
    tactic per case. Not part of the gate (it costs ~30 Verus runs); run it
    after touching `_taut_probe`, `_ambient_facts` or `vparse.sig_prefix`:

        harness/check.py selftest-probe
    """
    scratch = os.path.join(REPO, ".temp", "check", "probe-selftest")
    os.makedirs(scratch, exist_ok=True)
    mpath = os.path.join(scratch, "probe.rs")
    head("tautology-probe selftest")
    bad = 0
    for label, src, iname, expect in _PROBE_CASES:
        txt = "use vstd::prelude::*;\n\nverus! {\n" + src + "\nfn main() {}\n} // verus!\n"
        base = os.path.join(scratch, "base.rs")
        open(base, "w").write(txt)
        base_v, base_e, base_out = _verus(base)
        if base_v is None or base_e:
            bad += 1
            print(f"  FAIL {label:56s} the fixture itself does not verify "
                  f"({base_v}/{base_e})\n       {(base_out or '')[-300:]}")
            continue
        it = [i for i in vparse.parse(txt) if i.name == iname][0]
        cj = vparse.conjunct_spans(it, "requires")
        a, b = cj[0]["spans"][0]
        got, pv, pe, po, tac, tacs = _run_taut_battery(txt, it, a, b, "sel",
                                                       mpath, base_v)
        ok = got == expect
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label:56s} {got}"
              + (f" via `by ({tac})`" if got == "tautology" and tac else "")
              + (f"  [inapplicable: {tacs['inapplicable']}]"
                 if tacs["inapplicable"] else "")
              + ("" if ok else f"  (want {expect})"))
        if not ok and po:
            print(f"       {po[-400:]}")
    print("tautology-probe selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest-probe":
        sys.exit(_probe_selftest())
    try:
        sys.exit(main())
    except ModelSandboxError as e:
        # No JSON: a run whose reference model reached outside itself certifies
        # nothing at all, so there is no partial result worth recording.
        print(f"\n    FAIL [model-sandbox] {e}\n\ncheck.py: FAIL")
        sys.exit(1)
