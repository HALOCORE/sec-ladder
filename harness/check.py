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
       - an `external_body` item whose body contains `unsafe` must carry a
         non-empty `requires`, or a justification `spec.md` states and the
         verdict prints
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
  6  every rung's driver loop, C included, normalises to the token sequence
     pinned in `spec.md`; the *set* of files carrying a region is pinned too
  7  the C rung matches `model.py`'s per-input `sanitizer_expect`: "clean" means
     no ASan/UBSan diagnostic and the predicted exit, "fires" means a diagnostic
     is REQUIRED (p02's adversarial input is defined as the one that trips ASan)
  8  the Miri policy: mandatory wherever R4 and R5 are not the same machine code
     (`norel` or better), run for real on a nightly toolchain; a row Miri cannot
     be run on is a documented blocked row, not a pattern failure

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
    rung's work lives in `core::iter` symbols rather than in `kernel`) and
    cancels the loader and environment terms exactly.

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
        if rate < MIN_DECLARABLE_IR_PER_WORK:
            rep.fail("collapse-ir",
                     f"model.py declares min_ir_per_work={rate}, below the "
                     f"harness's absolute bound {MIN_DECLARABLE_IR_PER_WORK}. "
                     f"Until TASK_008 the only bound was `> 0`, and "
                     f"TASK_006_REVIEW put 1e-9 with why=\"see NOTES.md\" past "
                     f"the whole gate -- 'derived floor 0.0 Ir/call', 'tightest "
                     f"margin 2246270772.2x', nothing inspects `why`. The bound "
                     f"is physical: the tightest rate argued for in this project "
                     f"is p02's 0.0625 Ir/byte (load+store+vpsadbw+vpaddq per "
                     f"64-byte AVX-512 lane), and {MIN_DECLARABLE_IR_PER_WORK} "
                     f"is the same four instructions across a vector four times "
                     f"wider than anything that exists. Below it, this is not a "
                     f"claim about an algorithm; it is a claim that the work "
                     f"does not happen, and no justification string repairs "
                     f"that.")
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
    for nm, _, dcalls, work in shapes:
        print(f"    probe {nm:16s} n_iters {lo}/{hi} -> +{dcalls} kernel calls, "
              f"work_per_call={work}  => derived floor "
              f"{rate * work:.1f} Ir/call")
    if len(shapes) < 2 or len(works) < 2:
        rep.shout("collapse-ir",
                  f"only one probe *shape* ({names}, work={works}); the marginal "
                  f"d(Ir)/d(work) assertion did not run. A kernel that does a "
                  f"fixed amount of work regardless of its input passes the "
                  f"absolute floor. Add a second `collapse.probe_inputs` entry "
                  f"with a different work_per_call.")
    print(f"    rate  = {rate} Ir per unit of work, from {src_of_rate} "
          f"(harness default {ALPHA_IR_PER_WORK}; NOT settable from spec.md); "
          + (f"spec.md's advisory floor {declared} can only tighten it"
             if declared else "spec.md declares no additional floor"))
    if why:
        print(f"    why   = {why}")

    out, ratios = {}, []
    for (c, o, m), path in sorted(built.items()):
        if not path:
            continue
        per_shape = {}
        for nm, pr, dcalls, work in shapes:
            ir = {}
            for n in (lo, hi):
                ir[n] = _callgrind_total(
                    path, pr[n],
                    os.path.join(scratch, f"cg.{c}-{o}-{m}.{nm}.{n}.out"))
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
           if not k.endswith("d_ir_d_work") and k != "_rate"]
    if tight is not None:
        out["_tightest_margin"] = tight
        if rate < ALPHA_IR_PER_WORK and why:
            rep.shout("collapse-ir",
                      f"this pattern's anti-collapse floor is {rate} Ir per "
                      f"unit of work, BELOW the harness default "
                      f"{ALPHA_IR_PER_WORK} (bound {MIN_DECLARABLE_IR_PER_WORK}"
                      f"). Declared floor {rate * min(works):.1f}...{rate * max(works):.1f} "
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
    if len(out) > 1 and not any(f[0] == "collapse-ir" for f in rep.failures):
        rep.ok(f"{len(per)} cell/probe pairs: marginal Ir per call "
               f"{min(per):.0f}...{max(per):.0f}, all above the derived floor "
               f"(tightest margin {tight:.1f}x over a declared "
               f"{rate} Ir/work); "
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
    `spec.md` and the verdict shouts it on every run."""
    for i in tcb:
        if not _UNSAFE_RE.search(i.body or ""):
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
                         f"{src}:{i.line} trusted `unsafe` item `{i.name}` "
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
            rep.ok(f"{src}: trusted `unsafe` item `{i.name}` demands "
                   f"{reqs} of every caller, constraining every parameter its "
                   f"body uses ({used})")
            continue
        why = justifications.get(i.name)
        if not why:
            rep.fail("tcb-unsafe",
                     f"{src}:{i.line} `{i.name}` is {i.external}, its body "
                     f"contains `unsafe`, and it has **no `requires`**. It is "
                     f"therefore an axiom that the unchecked operation is "
                     f"always defined"
                     + (f", and it asserts {_clauses(i, 'ensures')} about the "
                        f"result" if _clauses(i, "ensures") else "")
                     + f". Give it the precondition its callers must discharge, "
                       f"or declare "
                       f"verus.unsafe_justifications[{src!r}][{i.name!r}] in "
                       f"spec.md -- which the gate then prints in every "
                       f"verdict.")
        else:
            rep.shout("tcb-unsafe",
                      f"{src}:{i.line} `{i.name}` is a trusted `unsafe` item "
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
            if it.cfg_gated:
                diffs.append(f"gated by {it.cfg_gated} -- it may not be in the "
                             f"build at all, while the item that is goes "
                             f"unpinned")
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
        r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), src,
                            "--verify-function", name, "--verify-root"],
                           capture_output=True, text=True, cwd=REPO,
                           timeout=RUN_TIMEOUT)
        res = (r.stdout + r.stderr).strip()
        m = re.search(r"(\d+) verified, (\d+) errors", res)
        n = int(m.group(1)) if m else 0
        out[name] = n
        if not m or int(m.group(2)) or n < 1:
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
    n = sum(len(v["mutants"]) for v in out.values())
    if out and not any(f[0] == "clause-mut" for f in rep.failures):
        rep.ok(f"{n} Verus mutants across {len(out)} file(s): every trusted "
               f"`ensures` conjunct is load-bearing, and `assert(false)` at the "
               f"call site is unprovable. Derived, not declared -- this does not "
               f"inherit the self-certification problem of a `spec.md` pin.")
    return out


def _taut_probe(txt, item, a, b, tag):
    """`txt` with a `proof fn` appended inside `verus! {}` whose only obligation
    is the clause at `txt[a:b]`, under no hypotheses but the parameter types.

    If that verifies, the clause is a **tautology**: it is `true` for every
    value its parameters can take, so demanding it of a caller demands nothing.
    `n >= 0` on a `usize` and `0 <= i` on a `usize` are both of this shape, and
    both walked past the gate at TASK_006_REVIEW while the structural rule
    printed them approvingly."""
    vs = vparse.verus_span(txt)
    if vs is None:
        return None
    fn = (f"\nproof fn slb_taut_probe_{tag}{vparse.params_text(item)}\n"
          f"    ensures\n        {txt[a:b]},\n{{\n}}\n")
    return txt[:vs[1]] + fn + txt[vs[1]:]


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
                    probe = _taut_probe(txt, it, a, b, f"{it.name}_{idx}_{jdx}")
                    if probe is None:
                        rep.fail("req-mut", f"{tag}: no `verus! {{}}` span to "
                                            f"put the tautology probe in")
                        continue
                    open(mpath, "w").write(probe)
                    pv, pe, po = _verus(mpath)
                    rows.append(dict(item=it.name, kind=why, clause=ctext,
                                     test="tautology", verified=pv, errors=pe))
                    if pv is None:
                        rep.fail("req-mut",
                                 f"{tag}: the tautology probe did not compile, "
                                 f"so this conjunct was not judged at all. Fix "
                                 f"the probe rather than skipping the "
                                 f"clause.\n      {(po or '')[-300:]}")
                    elif pe == 0:
                        rep.fail("req-mut",
                                 f"{tag} is a TAUTOLOGY: `{ctext}` is provable "
                                 f"from the parameter types alone ({pv} "
                                 f"verified, 0 errors -- control {base_v}), so "
                                 f"it demands nothing of any caller. "
                                 + ("A trusted `unsafe` item whose precondition "
                                    "is `true` is the axiom that the unchecked "
                                    "operation is always defined -- `n >= 0` on "
                                    "a `usize` is exactly this, and it passed "
                                    "the whole gate at TASK_006_REVIEW."
                                    if why == "trusted" else
                                    "A verified item's precondition that holds "
                                    "always constrains no call site."))
                    elif pe != 1 or pv != base_v:
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
                              + f" is not a tautology ({pv} verified, {pe} "
                                f"errors) -- {ctext[:52]}")
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
    n = sum(len(v["mutants"]) for v in out.values())
    if out and not any(f[0] == "req-mut" for f in rep.failures):
        rep.ok(f"{n} Verus mutants across {len(out)} file(s): no `requires` "
               f"conjunct is a tautology, and every *verified* item's "
               f"precondition fails the file when deleted. Note what is NOT "
               f"claimed: deleting a trusted item's precondition can never fail "
               f"a file (measured -- it only removes obligations from callers), "
               f"so a *missing* one is caught by the parameter-coverage rule in "
               f"5a, not here.")
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
      * **and** `verus --verify-function <the item enclosing the region>
        --verify-root` reports a verified body for that item, so the answer is
        about the code being normalised rather than about the file in general.

    The second query is what makes this different in kind from the pin: an item
    Verus never compiled cannot report a verified body, whatever its file
    spells its macros. Returns the set of file names that earned the harbour."""
    vcfg = contract.get("verus") or {}
    pinned_obl = vcfg.get("obligations") or {}
    ok = set()
    for src in sorted(pinned_obl):
        r = verus_res.get(src) or {}
        if r.get("errors") or not r.get("verified"):
            continue
        path = os.path.join(pdir, src)
        if not os.path.exists(path):
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
        name = max(inner, key=lambda i: i.body_start).name
        nv, ne, out = _verus(path, "--verify-function", name, "--verify-root")
        if nv and not ne:
            ok.add(src)
            print(f"    {src}: `fn {name}` encloses the driver region and Verus "
                  f"reports {nv} verified for it -- ghost stripping licensed")
        else:
            rep.fail("driver",
                     f"{src}: the driver region is inside `fn {name}`, which "
                     f"claims a `verus!` span, but "
                     f"`verus --verify-function {name} --verify-root` reports "
                     f"{nv} verified / {ne} errors. Ghost statements are "
                     f"stripped from the driver diff only for code Verus "
                     f"actually verified.\n      {(out or '')[-300:]}")
    return ok


def check_driver_identity(pdir, rep, contract, verus_ok=frozenset()):
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


def check_miri(pdir, rep, contract, identity, modmod, indir, names):
    """`.memory/02-bench-rules.md`: Miri is mandatory for any pattern whose R4
    and R5 are **not** byte-identical, because that is exactly when R4 stops
    inheriting R5's discharged obligations.

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
    out = {"pair": pair, "identity_o3": level, "inherits_proof": inherits}

    if inherits and not cfg.get("required"):
        rep.ok(f"R4/R5 ({pair}) are the same machine code at O3 (identity "
               f"{level!r} >= 'norel'), so R4 inherits R5's proof -- Miri not "
               f"required. spec.md: {cfg.get('reason', '(no reason given)')}")
        out.update(required=False, ran=False)
        return out
    if not inherits and not cfg.get("required"):
        rep.fail("miri", f"R4 and R5 differ at O3 (identity {level!r}), so R4 is "
                         f"unverified unsafe code that does not inherit R5's "
                         f"proof. `.memory/02-bench-rules.md` makes Miri "
                         f"mandatory here; spec.md sets miri.required=false.")
        out.update(required=True, ran=False)
        return out

    out["required"] = True
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
                    help="skip step 5c; the run then FAILS, by design")
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
    reqs, enss = derive_contract(pdir, rep, contract)
    domain = check_proof_domain(rep, all_models, reqs, enss)
    verus_ok = _verus_verified_files(pdir, rep, contract, verus_res)
    drivers = check_driver_identity(pdir, rep, contract, verus_ok)
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
                             "collapse_floor_min_declarable":
                                 MIN_DECLARABLE_IR_PER_WORK,
                             "collapse_tightest_margin":
                                 slopes.pop("_tightest_margin", None)},
        "identity": identity,
        "marginal_ir_per_call": slopes,
        "verus": verus_res,
        "verified_call_site": callsite,
        "clause_deletion": clausemut,
        "requires_strength": reqmut,
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
        print("\ncheck.py: FAIL")
        return 1
    print(f"\ncheck.py: {verdict}")
    return 2 if partial else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ModelSandboxError as e:
        # No JSON: a run whose reference model reached outside itself certifies
        # nothing at all, so there is no partial result worth recording.
        print(f"\n    FAIL [model-sandbox] {e}\n\ncheck.py: FAIL")
        sys.exit(1)
