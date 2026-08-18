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
     TASK_016_REVIEW B1)
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
  3c structural identity R4-vs-R5 is measured and **recorded as a result**. Only
     a drop below the level `spec.md` pins fails the gate: a proof that
     legitimately costs an instruction is a finding, not a harness error
  4  `adversarial-*` behaviour is recorded per rung and compared to the model's
     expected exit/stdout
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
  8  the Miri policy: mandatory wherever the pattern has a trusted item at all,
     and never waivable when R4 and R5 are not the same machine code (`norel` or
     better); run for real on a nightly toolchain. A row Miri cannot be run on is
     a documented blocked row, not a pattern failure

Results are written to `results/gate/<pattern>.json`, with a sha256 of the
contract block and of every source read. Exit code: 0 pass, 1 fail, 2 partial.

  harness/check.py p01
  harness/check.py p01 --no-build          # reuse .temp/build/pNN
  harness/check.py p01 --skip large        # fast edit/check loop; PARTIAL verdict
  harness/check.py p01 --no-callgrind      # skip step 3's dynamic half; FAILS
  harness/check.py p01 --no-verus-mutants  # skip step 5c; FAILS
"""

import argparse
import contextlib
import difflib
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

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import build as buildmod  # noqa: E402
import vparse  # noqa: E402
import dloop  # noqa: E402
import fixture  # noqa: E402

RUN_TIMEOUT = 900
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


def run_bin(path, arg):
    try:
        r = subprocess.run([path, arg], capture_output=True, text=True,
                           timeout=RUN_TIMEOUT)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", f"<timeout after {RUN_TIMEOUT}s>"


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


# ==========================================================================
# 0b. the pattern declares the idiom its rungs implement
# ==========================================================================

IDIOM_KEYS = ("required", "forbidden", "why")


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
    (`.memory/06-catalogue.md`)."""
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
        if not isinstance(v, list) or any(not isinstance(s, str) or not s.strip()
                                          for s in v):
            probs.append(f"idiom.{k} must be a list of non-empty strings, "
                         f"got {v!r}")
    if not idi.get("required"):
        probs.append("idiom.required is empty -- name what every rung must "
                     "implement, in the pattern's own terms")
    if not isinstance(idi.get("why"), str) or not idi["why"].strip():
        probs.append("idiom.why is empty -- state what a deviating rung would "
                     "delete, and, when `forbidden` is empty, why nothing is "
                     "excluded")
    return probs


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
        for s in idi.get(k) or []:
            out += textwrap.wrap(s, 92, initial_indent=f"    idiom {tag} ",
                                 subsequent_indent=" " * 20)
        if not (idi.get(k) or []):
            out.append(f"    idiom {tag} (none declared)")
    if why:
        out += textwrap.wrap(idi.get("why") or "", 92,
                             initial_indent="    idiom WHY       ",
                             subsequent_indent=" " * 20)
    return out


def check_idiom(rep, contract):
    head("0b. the pattern declares the idiom its rungs implement")
    probs = idiom_problems(contract)
    for p in probs:
        rep.fail("idiom", p)
    if probs:
        return
    idi = contract["idiom"]
    nreq, nforb = len(idi["required"]), len(idi.get("forbidden") or [])
    rep.ok(f"idiom declared: {nreq} required, {nforb} forbidden spelling(s), "
           f"hashed into contract sha256. Presence only -- no stage here checks "
           f"that a rung honours it. Text in the verdict.")
    if nforb == 0:
        rep.shout("idiom", "this pattern forbids no spelling by name, so its "
                           "rungs are matched only by the `required` list and "
                           "its safety number is a spelling's number unless "
                           f"`why` argues otherwise: {idi['why']}")


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
        models[name] = m
    return models


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
            rep.ok(f"{name}: all {sum(1 for k in results if k[3] == name)} cells "
                   f"agree -> {vals.pop()}")
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


def _callgrind_total(binary, arg, outfile):
    """Whole-program Ir for one run. Only ever used as one half of a
    *difference*: `.memory/03-measurement.md` shows the absolute value moves
    with the size of the environment block, and every one of those terms cancels
    when the same binary is run twice in the same shell."""
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={outfile}", binary, arg],
                       capture_output=True, text=True, timeout=RUN_TIMEOUT)
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
    (`patterns/p08-overlap-move/NOTES.md` 2b, `.memory/03-measurement.md`).
    Changing only the length of the environment block moves p08's
    `unsafe/O3/whole/small.bin` marginal over **7292.14 … 7292.30**, a spread of
    **0.18**, non-periodic and non-monotone in the pad length, with 100% of the
    drift inside one glibc `memmove` whose alignment-dependent tail changes by
    ~0.04 Ir/iteration. It is a real between-session term, it is bounded and
    small, and it threatens no published number (p08's tightest, `R1h - R1 =
    0.00`, measured exactly 0.00 in 12 configurations). Two consequences: quote
    marginals **to the instruction, never to the hundredth**, across sessions;
    and if p08's 12 cells move by a few hundredths between gate runs, that is
    this effect and not a code change.

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
# 3c. structural identity -- a RESULT, not a gate condition
# ==========================================================================

def check_identity(digests, rep, contract):
    head("3c. structural identity R4-vs-R5 (recorded as a result)")
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

def check_adversarial(built, rep, adv_models, indir, cells):
    head("4. adversarial inputs -- behaviour recorded, not required to agree")
    table = {}
    for name, mod in adv_models.items():
        m_exit, m_out = sbg(mod, "expected_exit"), sbg(mod, "expected_stdout")
        print(f"    -- {name}: {sb(mod.describe)} -> model expects exit "
              f"{m_exit}, stdout {m_out.strip()!r}")
        for c in cells:
            seen = set()
            for (cc, o, m), path in sorted(built.items()):
                if cc != c or not path:
                    continue
                rc, out, err = run_bin(path, os.path.join(indir, name))
                sig = -rc if rc is not None and rc < 0 else None
                seen.add((rc, out.strip(), err.strip()[:120], sig))
            for rc, out, err, sig in sorted(seen, key=str):
                table[f"{name}/{c}"] = dict(exit=rc, stdout=out, stderr=err,
                                            signal=sig, model_exit=m_exit,
                                            model_stdout=m_out.strip())
                flag = ""
                if rc != m_exit or out != m_out.strip():
                    flag = "  <-- diverges from model"
                print(f"       {c:18s} exit={rc!s:5s} stdout={out!r:24s}"
                      f" stderr={err!r:60s}{flag}")
            if len(seen) > 1:
                rep.note(f"{name}/{c}: opt/mode variants of this rung disagree "
                         f"({len(seen)} distinct behaviours)")
    return table


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


def _path_includes(pdir, srcs):
    """Every file the given sources pull into their crate with
    `#[path = "..."] mod ...`. Those files are part of the token stream the
    compiler and Verus see, and no pattern-local check ever parsed them:
    `common/driver.rs` is `#[verifier::external]` for R5, so an `unsafe` helper
    or a `#[cfg(slb_twin)]` item in it is invisible to every rule keyed on the
    pattern's own sources."""
    out = []
    for src in srcs:
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
            continue
        # The RAW text, not `blank_noncode`: the path is a string literal, which
        # blanking erases. A commented-out `#[path]` therefore gets scanned too,
        # which is the safe direction.
        txt = open(path).read()
        cand = re.findall(r"#\[\s*path\s*=\s*\"([^\"]+)\"\s*\]", txt)
        # ...and a plain `mod foo;`, which resolves to a sibling file rather than
        # to a declared path. No pattern uses that today; leaving it out would
        # mean an `unsafe` helper or a `#[cfg(slb_twin)]` item in `foo.rs` was
        # outside both scans, which is the whole shape of the bug this exists to
        # close.
        for m in re.finditer(r"\bmod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
                             vparse.blank_noncode(txt)):
            cand += [m.group(1) + ".rs", os.path.join(m.group(1), "mod.rs")]
        for inc in cand:
            p = os.path.normpath(os.path.join(pdir, inc))
            if p not in out and os.path.exists(p):
                out.append(p)
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
            req_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", " ".join(reqs)))
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
                         f"spec.md and the verdict will shout it every run.")
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

        # --- one item per name (TASK_003_REVIEW: last wins) ----------------
        dup = vparse.duplicate_names(item_list)
        if dup:
            for nm, its in sorted(dup.items()):
                rep.fail("proof-pin",
                         f"{src}: `{nm}` is defined {len(its)}x (lines "
                         f"{[i.line for i in its]}). The gate used to key items "
                         f"by name and keep the last, so a decoy could supply "
                         f"the pinned contract for the real item -- and nothing "
                         f"says the compiler keeps the same one.")
            continue
        items = {i.name: i for i in item_list}

        # --- item set -----------------------------------------------------
        want_items = pinned_items.get(src)
        if want_items is None:
            rep.fail("proof-pin", f"{src}: no item pin in spec.md")
            continue
        got, want = set(items), set(want_items)
        if got != want:
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
        print(f"    {src}: items the trusted-item rules govern (`_is_trusted`: "
              f"external_body + an `ensures`, or `unsafe` in the body): "
              f"{sorted(i.name for i in item_list if _is_trusted(i))}")
        for kw in ("assume(", "assume_specification", "admit("):
            n = len(re.findall(re.escape(kw), vparse.blank_noncode(txt)))
            if n:
                rep.note(f"{src}: {kw} appears {n}x -- must be justified in NOTES.md")

        # --- obligation count --------------------------------------------
        r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path],
                           capture_output=True, text=True, cwd=REPO,
                           timeout=RUN_TIMEOUT)
        res = (r.stdout + r.stderr).strip()
        m = re.search(r"(\d+) verified, (\d+) errors", res)
        if not m:
            rep.fail("proof-verify", f"{src}: no verification result: {res[-500:]}")
            continue
        n_ver, n_err = int(m.group(1)), int(m.group(2))
        out[src] = {"verified": n_ver, "errors": n_err, "pinned": want_n,
                    "tcb_items": [dict(name=i.name, attr=i.external,
                                       body_lines=i.body_lines, line=i.line)
                                  for i in tcb]}
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
        else:
            rep.ok(f"{src}: {n_ver} verified, 0 errors -- matches the pinned "
                   f"obligation count; {len(tcb)} TCB items, all contracts "
                   f"identical to spec.md")
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
        nv, ne, res, resolved = _verify_function(src, name, mp)
        n = nv or 0
        out[name] = n
        if not resolved:
            rep.fail("proof-rule2",
                     f"Verus could not RESOLVE `{name}` for "
                     f"`--verify-function` (module {mp!r}) -- that is 'the gate "
                     f"could not ask the question', not 'the item has no "
                     f"verified body' (TASK_008_REVIEW major E).\n"
                     f"      {(res or '')[-300:]}")
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


def _verus(path, *extra):
    """(verified, errors, raw output). `(None, None, out)` if Verus said neither."""
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path,
                        *extra], capture_output=True, text=True, cwd=REPO,
                       timeout=RUN_TIMEOUT)
    res = (r.stdout + r.stderr).strip()
    m = re.search(r"(\d+) verified, (\d+) errors", res)
    if not m:
        return None, None, res
    return int(m.group(1)), int(m.group(2)), res


_UNRESOLVED_RE = re.compile(
    r"could not find function .*specified by --verify-function")


def _verify_function(path, name, mod_path=""):
    """(verified, errors, output, resolved) for one item, asked of Verus.

    Two answers that used to be one (TASK_008_REVIEW, major E). `--verify-root`
    restricts the query to the crate root, so a function inside a `mod` is not
    *unverified* -- it is **unnameable**: Verus replies *"could not find
    function drive specified by --verify-function; available functions are: -
    main"*, `_verus` returns `(None, None)`, and the caller reported "the item
    enclosing the region has no verified body", which is false. The file
    verifies 2/0.

    `--verify-only-module <mod> --verify-function <name>` is the query that does
    resolve it (measured: `1 verified, 0 errors`), so a mod-nested item is now
    asked properly instead of being misdiagnosed. `resolved` is False only when
    Verus says it cannot find the name at all, which is a different failure and
    must be reported as one -- an `impl` method resolves fine either way."""
    extra = (["--verify-only-module", mod_path, "--verify-function", name]
             if mod_path else ["--verify-function", name, "--verify-root"])
    nv, ne, out = _verus(path, *extra)
    return nv, ne, out, not (nv is None and _UNRESOLVED_RE.search(out or ""))


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
    """(verdict, verified, errors, output, tactic) for one `requires` conjunct.

    Verdicts: `tautology` (some tactic proved it under no hypotheses),
    `not a tautology`, `unsynthesisable` (the probe could not be built -- the
    reason is in `output`), `nocompile` (Verus produced no result at all),
    `perturbed` (the probe moved something other than the one obligation it
    added, so the conjunct was not judged). Everything but the second is a
    failure for the caller; none of them is a silent skip."""
    pv = pe = None
    po, used = "", None
    for tac in _TAUT_TACTICS:
        probe, whynot = _taut_probe(txt, item, a, b, tag, tac)
        if probe is None:
            return "unsynthesisable", None, None, whynot, tac
        open(mpath, "w").write(probe)
        pv, pe, po = _verus(mpath)
        used = tac
        if tac is None:
            if pv is None:
                return "nocompile", pv, pe, po, tac
            if pe == 0:
                return "tautology", pv, pe, po, tac
            if pe != 1 or pv != base_v:
                return "perturbed", pv, pe, po, tac
        elif pv is not None and pe == 0:
            return "tautology", pv, pe, po, tac
    return "not a tautology", pv, pe, po, used


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
                    verdict, pv, pe, po, used = _run_taut_battery(
                        txt, it, a, b, f"{it.name}_{idx}_{jdx}", mpath, base_v)
                    rows.append(dict(item=it.name, kind=why, clause=ctext,
                                     test="tautology", tactic=used,
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
                        print(f"    {src}: {it.name} requires[{idx}]"
                              + (f".conjunct[{jdx}]" if len(cj["spans"]) > 1
                                 else "")
                              + f" is not a tautology (bare Z3, "
                              + ", ".join(f"`by ({t})`" for t in _TAUT_TACTICS
                                          if t)
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
        rep.ok(f"{n} `requires` conjunct(s) probed (n={n} > 0) and {dels} "
               f"deleted, across {len(out)} file(s): no `requires` "
               f"conjunct is a tautology under bare Z3 or "
               + " or ".join(f"`by ({t})`" for t in _TAUT_TACTICS if t)
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
    copy loop (there is no vstd spec for `copy_from_slice`, so a bulk-copy twin
    is not available -- `.memory/04-verus.md`). The gate asserts the twin
    verifies against that contract.

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
            print(f"    {src}: no trusted item with an `ensures` or an `unsafe` "
                  f"body (`_is_trusted`), so no twin is required. "
                  f"external_body items: "
                  f"{sorted(i.name for i in items.values() if i.external)}")
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
        # certificate and the wrong item -- Verus itself does NOT object to two
        # items sharing a name (`S::drive` and `inner::drive` ->
        # `--verify-function drive` silently reports `1 verified`, measured at
        # TASK_008_REVIEW). It is checked FIRST and named explicitly, so the
        # refusal is attributed to the duplicate rather than to the generic
        # "no verified body" text below.
        try:
            dup = vparse.duplicate_names(vparse.parse(open(path).read()))
        except ValueError as e:
            rep.fail("driver", f"{src}: {e}")
            continue
        if dup:
            rep.fail("driver",
                     f"{src}: `{sorted(dup)}` defined more than once, so "
                     f"`--verify-function` cannot be trusted to name the item "
                     f"enclosing the driver region -- Verus does not object to "
                     f"two items with one name. No harbour certificate issued.")
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
        name = it.name
        nv, ne, out, resolved = _verify_function(path, name, it.mod_path or "")
        q = (f"--verify-only-module {it.mod_path} --verify-function {name}"
             if it.mod_path else f"--verify-function {name} --verify-root")
        if nv and not ne:
            ok.add(src)
            print(f"    {src}: `fn {name}` encloses the driver region and Verus "
                  f"reports {nv} verified for it -- ghost stripping licensed")
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

def check_sanitizers(pdir, rep, indir, models):
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
    """
    head("7. C rung under ASan + UBSan (per-input expectation)")
    out = os.path.join(REPO, ".temp", "build",
                       buildmod.pattern_id(pdir), "c-gcc-asan")
    cmd = [buildmod.GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
           "-fsanitize=address,undefined",
           # the container has an LD_PRELOAD that breaks the shared ASan
           # runtime's init ordering; static linking sidesteps it
           "-static-libasan", "-static-libubsan",
           "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
           "-I", os.path.join(pdir, "c"),
           os.path.join(REPO, "common", "driver.c"),
           os.path.join(pdir, "c", "kernel.c"),
           os.path.join(pdir, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        rep.fail("sanitizer", f"asan build failed: {(r.stdout + r.stderr)[-400:]}")
        return {}
    res = {}
    for name, mod in sorted(models.items()):
        rc, so, se = run_bin(out, os.path.join(indir, name))
        expect = sbg(mod, "sanitizer_expect")
        m_exit = sbg(mod, "expected_exit")
        fired = ("runtime error" in se or "AddressSanitizer" in se
                 or "UndefinedBehaviorSanitizer" in se or "ERROR:" in se)
        diag = re.sub(r"\s+", " ", se.strip())[:300]
        res[name] = {"exit": rc, "expected_exit": m_exit,
                     "expect": expect, "fired": fired, "diagnostic": diag}
        if expect == "fires":
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
        else:
            print(f"    ok   {name:28s} clean, exit={rc} (model {m_exit})")
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


def _trusted_items(pdir, contract):
    """{pinned Verus source: [trusted item names]} -- `_is_trusted` applied to
    every file `verus.obligations` names. Used by the Miri policy, which is now
    keyed on "does this pattern have a trusted base at all" rather than on
    whether R4 and R5 happen to be byte-identical."""
    out = {}
    for src in sorted((contract.get("verus") or {}).get("obligations") or {}):
        path = os.path.join(pdir, src)
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


def check_miri(pdir, rep, contract, identity, modmod, indir, names):
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
    out = {"pair": pair, "identity_o3": level, "inherits_proof": inherits,
           "trusted_items": trusted}

    # DERIVED, and it overrides the declared flag in one direction only: the
    # flag can add Miri, never remove it.
    why_required = []
    if n_trusted:
        why_required.append(
            f"this pattern has {n_trusted} trusted item(s) {trusted} whose "
            f"`ensures` need not be COMPLETE with respect to the unchecked "
            f"operations their bodies perform (TASK_009_REVIEW x4)")
    if not inherits:
        why_required.append(
            f"R4 and R5 differ at O3 (identity {level!r}), so R4 does not "
            f"inherit R5's discharged obligations at all")
    if cfg.get("required"):
        why_required.append("spec.md sets miri.required")
    out["required_because"] = why_required

    if not why_required:
        rep.ok(f"R4/R5 ({pair}) are the same machine code at O3 (identity "
               f"{level!r} >= 'norel') and this pattern has NO trusted item, so "
               f"there is no trusted `ensures` whose incompleteness Miri would "
               f"have to backstop -- Miri not required. spec.md: "
               f"{cfg.get('reason', '(no reason given)')}")
        out.update(required=False, ran=False)
        return out
    if n_trusted and cfg.get("required") is False:
        rep.fail("miri",
                 f"spec.md sets miri.required=false, but this pattern has "
                 f"{n_trusted} trusted item(s) {trusted}, which makes Miri "
                 f"mandatory whatever the R4/R5 identity level is "
                 f"(`.memory/02-bench-rules.md`, revised at TASK_010): a trusted "
                 f"`ensures` need not cover every unchecked operation its body "
                 f"performs, byte-identity propagates that rather than excusing "
                 f"it, and Miri is the only backstop. The gate runs Miri anyway; "
                 f"fix the pin so it does not claim otherwise.")

    out["required"] = True
    print(f"    Miri is REQUIRED because: " + "; ".join(why_required))
    srcs = cfg.get("sources") or [buildmod.RUST_SRC.get(a, f"{a}.rs")]
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
            try:
                r = subprocess.run(
                    [MIRI_BIN, "--sysroot", sysroot, "--edition", "2021",
                     "-Zmiri-disable-isolation", spath, "--", probe],
                    capture_output=True, text=True, timeout=MIRI_TIMEOUT, cwd=pdir)
            except subprocess.TimeoutExpired:
                why = (f"miri did not finish within {MIRI_TIMEOUT}s. `n_iters` "
                       f"is clamped to {MIRI_PROBE_ITERS} but the payload is "
                       f"not, and the driver decodes it element by element "
                       f"under interpretation. This input is unchecked; the "
                       f"others are not.")
                rep.block("miri", f"{s} on {nm}", why)
                runs.append(dict(source=s, input=nm, blocked=why))
                continue
            ub = "Undefined Behavior" in r.stderr or "error: unsupported" in r.stderr
            got = r.stdout.strip()
            want = (sbg(mod, "expected_stdout") or "").strip()
            rec = dict(source=s, input=nm, exit=r.returncode, ub=ub,
                       stdout=got, model_stdout=want,
                       stderr=re.sub(r"\s+", " ", r.stderr.strip())[:400])
            runs.append(rec)
            if ub:
                rep.fail("miri", f"{s} on {nm} (n_iters={MIRI_PROBE_ITERS}): "
                                 f"Miri reports UB -- {rec['stderr'][:300]}")
            elif r.returncode != 0 and sbg(mod, "expected_exit") == 0:
                rep.fail("miri", f"{s} on {nm}: miri exited {r.returncode}, "
                                 f"model expects 0 -- {rec['stderr'][:300]}")
            elif r.returncode == 0 and got != want:
                rep.fail("miri", f"{s} on {nm}: miri printed {got!r}, model "
                                 f"predicts {want!r}")
            else:
                rep.ok(f"miri {s} on {nm:28s} n_iters={MIRI_PROBE_ITERS}: no UB, "
                       f"stdout {got!r} matches the model")
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
    check_idiom(rep, contract)

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

    check_checksums(built, rep, good_models, indir)
    digests = check_no_collapse(built, rep)
    slopes = check_marginal_ir(pdir, built, rep, modmod, contract, indir,
                               not a.no_callgrind)
    identity = check_identity(digests, rep, contract)
    advtable = check_adversarial(built, rep, adv_models, indir, cells)
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
    san = check_sanitizers(pdir, rep, indir, all_models)
    miri = check_miri(pdir, rep, contract, identity, modmod, indir,
                      sorted(all_models))

    srcs = sorted(glob.glob(os.path.join(pdir, "*.rs"))
                  + glob.glob(os.path.join(pdir, "c", "*"))
                  + glob.glob(os.path.join(pdir, "*.md"))
                  + glob.glob(os.path.join(pdir, "model.py"))
                  + glob.glob(os.path.join(REPO, "common", "driver.*"))
                  + glob.glob(os.path.join(REPO, "harness", "*.py")))
    doc = {
        "pattern": os.path.basename(pdir),
        "skipped_inputs": a.skip,
        "inputs_checked": sorted(all_models),
        # TASK_005 A4: weakening a pin now shows up in review as a change to the
        # committed gate artefact, not only as a source diff.
        "contract_sha256": contract_sha,
        # TASK_016: the declared idiom, recorded so the gate artefact says what
        # the rungs were supposed to be spellings *of*. It is inside the hashed
        # block, so this is a convenience copy, not a second pin.
        "idiom": contract.get("idiom"),
        "source_sha256": {os.path.relpath(s, REPO): sha256_file(s)
                          for s in srcs if os.path.isfile(s)},
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
        "marginal_ir_per_call": slopes,
        "verus": verus_res,
        "verified_call_site": callsite,
        "clause_deletion": clausemut,
        "requires_strength": reqmut,
        "verified_twins": twins,
        "proof_domain": domain,
        "driver_loops": drivers,
        "adversarial": advtable,
        "sanitizer": san,
        "miri": miri,
        "failures": [{"section": s, "message": m} for s, m in rep.failures],
        "notes": rep.notes,
        "loud": [{"section": s, "message": m} for s, m in rep.loud],
        "blocked": rep.blocked,
    }
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
    outdir = os.path.join(REPO, "results", "gate")
    os.makedirs(outdir, exist_ok=True)
    suffix = ".partial.json" if partial else ".json"
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
        got, pv, pe, po, tac = _run_taut_battery(txt, it, a, b, "sel", mpath,
                                                 base_v)
        ok = got == expect
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label:56s} {got}"
              + (f" via `by ({tac})`" if got == "tautology" and tac else "")
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
