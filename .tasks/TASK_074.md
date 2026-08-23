# TASK_074 — p48, uninitialised memory: and §0 opens by deciding whether to build it

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.memory/06-catalogue.md`'s `p48` triage** (the section *"p48 — the
seventh axis, and why the manager is proposing it against the slate"*), then
`.memory/04-verus.md`, `.memory/03-measurement.md` (**the two `Ir` conventions,
the INLINE-MODE rule, the DOMAIN rule, the RESIDUE-CLASS rule, the
OUTWARD-DISPATCHED-WORK rule** — that last one is new and it broke two of p36's
published figures) and `.memory/01-ladder.md` **findings 1 (and its new scope
clause), 7 (p08), 19 (p27) and 23 (p36)**. Templates:
`patterns/p36-vtable-dispatch/` (newest) and `patterns/p27-handle-table/` (which
already ships `vstd::raw_ptr` code).

⚠⚠ **RULE 3 IS FLAGGED AGAINST THIS PATTERN IN THE CATALOGUE ITSELF.** `p48` was
proposed by **the manager**, from source reads and `vstd` greps, **against the
manager's own slate**, and it has been **unattacked since TASK_066**. PROTOCOL
rule 3 says designer-validates-own-design is the configuration this project keeps
finding defects in. **So §0's first deliverable is not a measurement. It is an
argument, and "do not build this" is a legitimate outcome.**

⚠ **State novelty claims as questions to be measured.** *"The first termination
proof in the project"* was the manager's sentence in `TASK_070.md`; it was false
and shipped into eight places, two inside `contract_sha256`. Everything below is
written as a question. **Treat any sentence that is not as a bug in this file.**

## What p48 would be

`malloc` a record, fill some fields, write the whole record out. ⚠ **The killer
sub-case is PADDING**: initialise every *field* of a `struct` and the padding
bytes are **still** uninitialised, so the obvious fix does not work and only a
whole-object `memset` does. That is the real CVE shape — kernel `copy_to_user`
infoleaks. The harm is **in bounds, live, owned, and never written**: not
spatial (p17), not temporal (p27), not a trace (p47).

## §0 — the argument first, then four measurements

**§0a — SHOULD THIS BE BUILT? Argue it, and the manager is not to be deferred
to.** Four objections the manager can see, none of them answered:

1. ⚠ **Is p48 p08 in a costume?** p08's result is *"safe Rust cannot express
   it"* — borrow checker, compile time, nothing to measure. **p48's safe-Rust
   answer is the same shape**: `Vec::with_capacity(n)` has `len 0`, and reaching
   the residue needs `set_len`, which is `unsafe`. The catalogue's defence is
   that *"unlike p08, the C bug is not exotic"*. **Is "the bug is more common"
   enough to justify a second pattern with the same ladder shape?** ⚠ **p36 just
   asked itself the equivalent question and answered "the bug class is the
   tree's twelfth" — and was worth building anyway, for reasons that had nothing
   to do with the bug class.** Find p48's version of that, or say there isn't
   one.
2. ⚠ **Is the R5 obligation a new KIND, or a new LABEL?** The catalogue claims
   p27's precondition is about **ownership** (*do you hold the permission?*)
   while `is_init` is about **contents of memory you already own**. **Both are
   `requires` clauses on a `vstd::raw_ptr` operation.** Is the distinction real
   enough to carry a pattern? **Read `~/tools/verus/vstd/raw_ptr.rs` and p27's
   `verus.rs` and say.** ⚠ **And it is NOT "the first axis where R5 wins" —
   p27's R5 already catches its use-after-free** (`patterns/p27-handle-table/NOTES.md`,
   the `precondition not satisfied` passage). The manager wrote that claim here
   and self-caught it; do not let it back in.
3. **What is the COST axis?** Every pattern here has one, and p48's is not
   stated. The manager's candidate, offered as a question: *what does "no
   uninitialised memory" cost?* — the `memset` of the padding, `vec![0; n]`
   against `MaybeUninit`, i.e. the most-argued real performance complaint about
   safe Rust. **If that is the cost axis it is a good one and no pattern has it.
   Confirm or replace it.**
4. ⚠ **NEW, from p36, and it may be the sharpest objection: `Ir` cannot measure
   this harm.** p48's harm is a **value**, not a count — the leaked bytes. The
   project's primary metric is deterministic instruction count, and a leak of
   residue executes the *same instructions* as a leak of zeros. **p47 solved the
   analogous problem by making `Ir` literally the side channel. What is p48's
   equivalent, and if there isn't one, what carries the security half?**

**Write the decision in `NOTES.md` §0a with the argument. If it is "do not
build", stop there and report — that is a successful task**, and the named
alternatives are at the bottom of this file.

**§0b — CAN THE HARM BE MADE DETERMINISTIC?** ⚠ **Fresh `mmap` pages are
zero-filled by the kernel**, so a first-touch `malloc` leaks zeros and the
pattern shows nothing. The manager's design, **unmeasured and therefore a
prior**: allocate record A, write a **known sentinel** into it, **free** it,
allocate B, fill B **partially**, emit B — the harm is then *"A's sentinel
appears in B's output"*, which is program-controlled and so deterministic across
allocator state **and** opt level.

> ⚠ **The hazard to settle FIRST: the store of the sentinel into A must not
> itself be dead**, or DSE removes the very thing the pattern detects. A must be
> genuinely read before the free.
> ⚠ **And p27 already paid for adjacent knowledge**: a freed chunk's first 16
> bytes are glibc tcache metadata, and reading past them is deterministic
> run-to-run **but varies across `-O` LEVEL**, because DSE changes what was
> stored before the free (`.memory/03-measurement.md`). The sentinel design is
> meant to sidestep that. **Verify it does.**

**§0c — WHAT CATCHES IT, AND CAN IT BE A RUNG?** ✅ **MSan is confirmed present**
— clang, **with origin tracking**; **gcc has no `-fsanitize=memory`**
(`.temp/p48probe/NOTES.md`, probed at TASK_072 and spot-checked by its
reviewer). ⚠ **One recorded omission: the probe exits 1 and that was not written
down — read the exit code before building an expectation on it.**

> ⚠ **MSan requires EVERY dependency to be instrumented**, and this project's
> cells link `common/driver.c`. **Settle whether MSan can see the kernel through
> the shipped driver**, and whether it is a **matrix** build or a **control**.
> **Stage 7 builds `gcc -O1 -fsanitize=address,undefined` — gcc cannot do MSan
> at all**, so if MSan is the only catcher it is a control, exactly as
> `-fsanitize=cfi-icall` is on p36. ⚠ **`build.py` is a full re-measure — do not
> reach for it.** Also probe **valgrind's `--track-origins=yes`**, which needs no
> instrumentation at all and may be the better answer here.

**§0d — WHERE DOES THE WORK LIVE?** ⚠ **New rule, and p36 was broken by its
absence.** `kernel_exclusive_ir` counts the kernel symbol and **not what it
calls** — and the rule used to be phrased as *"check the `@plt`/`@GLIBC` calls
match"*, which p36 walked past because **its callees were project-local**. p48
will call `memset`/`memcpy` and possibly differ across rungs in **which**.
**List the outward-dispatched work per cell and check the lists are equal before
quoting the kernel column for any cross-rung difference.**
⚠ **And gcc defaults to `-fcf-protection=full`**, so every gcc cell carries
`endbr64` landing pads the other compilers do not — `1.00000·nrw + 1` `Ir` per
call on p36. **Name it before attributing a gcc-vs-clang gap to codegen.**

## What p48 must have, if §0 says build it

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**
  (definition-of-done 6), and ⚠ **say that the `git show HEAD:` diff is
  UNAVAILABLE on a new pattern and why** — it compares working tree to HEAD, not
  first-written to shipped, so on a clean tree it always looks like it passed.
  **The recorded first hash is the only evidence.**
- **If `spec.md` is generated, fix the GENERATOR and re-run it.** Read the shared
  named-spelling paragraph from a donor `spec.md`; never embed a copy.
  ⚠ **p36 changed its `WHY_HEAD` opener to NAME the *every rung is a spelling*
  finding instead of citing a bare number** — that is the convention now
  (RECAP: *name the pattern, never the number*; finding 14 is a live collision).
  **Follow p36, not p22/p27/p38.**
- ⚠ **SEARCH BOTH SIDES, AND COUNT THE LEVERS ON EACH.** The trap has been
  restated: *a difference is only as honest as its WEAKER-SEARCHED endpoint.*
  **p36 searched R4 first and correctly — and then published against an R3 side
  with one lever, which moved R3 the wrong way; `+15.00` was `+7`.** Publish the
  **fixed-R4 bound**, the **span**, the words **"cheapest found"**, the **input
  named**, and **the lever count per side**.
- **NAME THE INLINE MODE at every figure.** Cross-pattern `Ir` is
  `isolated`-only.
- ⚠ **If you fit a law it owes its DOMAIN, and check the RESIDUE CLASS of any
  parameter your bands hold constant.**
- **No `ns` claim without a layout population**; port `controls/clayout.py` and
  ⚠ **point `OUT` and its scratch default at `.temp/p48/`** — p27's copy still
  said `.temp/p14/` and overwrote p14's `meta.json`.
- **Adversarial rows per rung**, **TCB as one number plus the U-license / V-gap
  / infra classification**, and **two proof mutants that FAIL** — ⚠ **run the
  battery with `--multiple-errors`**; p22 skipped it and the review found a
  mutant failing on a different obligation than claimed.
- ⚠ **`forbidden_hits` HARD-FAILS**, and **backtick every entry you want
  enforced** — an unbackticked entry is audited **zero** times. Recompute the
  denominator rather than quoting one:
  ```
  python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"
  ```

## Done when

§0a's decision is written with its argument — **and if it is "do not build",
that plus §0b–d's measurements IS the deliverable.** Otherwise: the p36
checklist; complete `harness/check.py p48` (**say up front which verdict you
expect and why**); checksums against an independent `model.py`; two failing proof
mutants with `--multiple-errors` output; `measure.py --check-stale` clean.
**Paste actual output.** ⚠ Doc edits make a gate record STALE — re-run after.

## Constraints

No root; no `/tmp` (scratch `.temp/p48/`; `.temp/p48probe/` is readable, **not
writable**); **no `git add`/`git commit`**; do not edit `pilot/`, `.memory/`,
`harness/`, `common/`, or any existing pattern. **If p48 seems to need a
`harness/` change, STOP and report it** — there is a **five-item** `check.py`
batch queued and a sixth would be folded into it, not run separately. Verus only
via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source — **never**
`../LearnVeri/_VERUS_DOC_/vstd/`, an older snapshot that caused one false *"no
spec exists"* that stood for 44 tasks. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; ⚠ **no self-matching `pgrep` wait-loops**
— one was orphaned two tasks ago and fired a spurious completion. Measurements
in the FOREGROUND. **You are the only agent running.**

Notes to `.temp/p48/NOTES.md` as you go, so a transient API death loses nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 165** — the last five entries include **four manager errors**, two of them
in the task file that forwarded the rule against them. **The count is the
evidence that this instruction is not a courtesy.**

**What I am least sure of, by name: §0a objection 1 — whether "safe Rust cannot
express it" being the answer AGAIN makes p48 a second p08.** The catalogue's
defence is that the C bug is ordinary where p08's is exotic, and **I do not know
whether that is a research difference or a marketing one.** p36 was worth
building despite a duplicate bug class, but only because its *mechanism*,
*catcher* and *prover* stories were each new. **Check p48 against all three
before agreeing with me.**

**If you refuse it, the named alternatives, in the manager's order:** (a) the
**five-item `harness/` batch** — three of the five are now *measured* defects,
which is the TASK_068 override's own standard; (b) **cross-pattern synthesis**
(RECAP "Owed" 13), which is the project's stated purpose and has no artefact,
with a working probe already at `.temp/synth/aggregate.py`; (c) **a different
catalogue row you argue for.** ⚠ **(c) is the one the manager most wants to
hear** — the slate is the manager's and RECAP has invited push-back on it since
TASK_066 with no taker.
