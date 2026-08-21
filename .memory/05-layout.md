# Repo layout & naming

```
sec-ladder/
  CLAUDE.md                 # entry point: links + DON'Ts only, keep it ~30 lines
  PLAN.md                   # research plan, feasibility argument, decisions
  TOOLCHAIN.md              # install record, how to run Verus, what's missing
  verus_run.py              # the only sanctioned way to invoke Verus
  .memory/                  # durable context for agents (this dir)
  .tasks/                   # TASK_NNN.md specs + PROTOCOL.md + reports
  .temp/                    # scratch, gitignored, one subdir per category
  pilot/                    # calibration kernel, 5 rungs — frozen, do not edit
  common/
    driver.rs               # shared Rust driver (see .memory/02-bench-rules.md)
    driver.c  driver.h      # shared C driver
    slb.py                  # input-file format read/write helper
  harness/
    build.py                # build one/all cells of a pattern
    check.py                # correctness gate: checksums, anti-collapse, proof
                            #   domain, driver pin, sanitizers, Miri policy
    asm.py                  # extract + normalise + diff kernel assembly
    vparse.py               # Verus/Rust items, attributes, requires/ensures
                            #   clauses. `python3 harness/vparse.py selftest`
    dloop.py                # the driver loop -> a language-neutral token
                            #   sequence, so C and Rust are diffed mechanically
    fixture.py              # builds .temp/build/docrepro, the fixture
                            #   `asm.py selftest` measures. Run it on a fresh
                            #   checkout; check.py runs it for you
    measure.py              # instruction counts, callgrind, timing -> results JSON
    report.py               # results JSON -> markdown tables
  patterns/pNN-<slug>/
    README.md               # what the pattern is, the C bug, expected findings
    spec.md                 # the exact kernel contract all 5 rungs implement,
                            #   incl. a ```slb-contract block check.py parses.
                            #   That block is a set of PINS: obligation count,
                            #   every verus item's requires/ensures, the driver
                            #   loop, the Ir floor, identity levels, Miri policy
    model.py                # MANDATORY. The independent Python reference
                            #   implementation of spec.md; check.py imports it
                            #   and drives it over every input. See p01's for
                            #   the required API -- the model used to be
                            #   hard-coded in check.py, which would have forced
                            #   47 forks of the gate
    inputs/gen.py           # deterministic input generation (.bin gitignored)
    c/kernel.c  c/kernel.h  # the kernel, its own TU
    c/kernel_hardened.c     # OPTIONAL R1h: the same C kernel WITH the bounds
                            #   check. Ship it for every pattern that models a
                            #   bug -- without it "C is faster" and "C is
                            #   unsafe" are the same sentence. Its presence is
                            #   what creates the `c-gcc-h` / `c-clang-h` cells;
                            #   nothing is declared. See .memory/01-ladder.md
    c/main.c                # the C driver loop, a second TU so `isolated`
                            #   builds put a real call between them
    safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
    safe_naive_verus.rs     # OPTIONAL R2v control: safe Rust + the same proof.
                            #   Not a rung, not in the measured 6-cell matrix;
                            #   built via `build.py --cell safe_naive_verus`.
                            #   It exists to hold up finding 2 in 01-ladder.md.
    NOTES.md                # per-rung findings, proof sticking points, TCB tally
  results/
    pNN-<slug>.json         # raw measurements, committed
    gate/pNN-<slug>.json    # what check.py *found* on a COMPLETE run, committed:
                            #   identity levels, marginal Ir per call, obligation
                            #   counts, TCB inventory, per-input requires/ensures
                            #   coverage, adversarial behaviour, the verdict
    gate/pNN-<slug>.partial.json   # the same, from a run that certified less
                            #   (`--skip`, `--no-build`, `--no-callgrind`,
                            #   `--cells measured`). A diagnostic run must never
                            #   overwrite the record of a full one — at TASK_003
                            #   a `--skip small --skip large --no-callgrind` run
                            #   clobbered a passing artefact with its own
                            #   deliberate FAIL. Both files carry
                            #   `complete_run` and the exact `invocation`.
    tables/                 # generated markdown, regenerable
```

## Naming

- Pattern dirs: `pNN-<slug>`, zero-padded, slug in kebab-case (`p17-http-range`).
- The measured function is named **`kernel`** in every rung and every language, so
  `harness/asm.py` can find it by substring across mangling schemes.
- Rung file stems are fixed: `c/`, `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`,
  `verus.rs`. Do not invent variants; add an axis to `harness/build.py` instead.
- Build outputs go to `.temp/build/pNN/<cell>-<opt>-<mode>[-abort]` — never into
  the pattern dir, never into git. Cell names are `c-gcc`, `c-clang`,
  `safe_naive`, `safe_tuned`, `unsafe`, `verus` (+ `safe_naive_verus` control).
- **The driver loop is duplicated, on purpose, once per rung**, between
  `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END` markers. It cannot be shared: R5's copy
  has to sit inside `verus!` so the kernel call site is verified
  (`.memory/02-bench-rules.md` rule 2). `harness/check.py` step 6 normalises
  every copy — the C one included — with `harness/dloop.py` and diffs each
  against the canonical token sequence pinned in `spec.md`. **Never
  copy-against-copy**: that passes when the mutation is applied to all of them,
  demonstrated at TASK_003 by deleting the anti-collapse barrier from all five
  Rust rungs and watching the old gate print "5 Rust rungs share a
  byte-identical driver loop". `common/driver.{c,rs}` holds only the parts that
  *can* be shared: argv, file I/O, payload decoding, and printing.

## Adding a pattern — what the gate needs from you

`harness/check.py` is generic; everything pattern-specific lives in two files.
In order:

1. **`spec.md`** — prose contract, then the ```slb-contract``` block. Start by
   copying p01's (no bug, `&[u64]` in and a `u64` out) or **p02's** (a real bug,
   a `&mut [u8]` output buffer, an R1h cell) and changing every value. The
   block's fields:
   `kernel`, `model`, `requires`, `ensures`, `verus.{call_site, kernel_item,
   translate, obligations, items, unsafe_justifications}`,
   `driver.{statements, c_source, regions, aliases, call_args, canonical}`,
   `collapse.{probe_inputs, probe_iters}`, `identity`,
   `miri.{pair, sources, required, reason, blocked_reason}`.

   `driver.call_args` (added at TASK_004) declares which argument *positions* of
   a named call are the canonical ones, per language: `{"c": {"kernel": [0, 2,
   3]}}`. Needed as soon as the C kernel takes the slice lengths Rust carries
   inside `&[T]`, which no alias can reconcile — an alias's two sides are both a
   dotted identifier path, so it renames and does nothing else. `dloop` refuses
   to drop anything that is not a single bare identifier.

   `requires`/`ensures` are **derived** by the gate from `verus.rs`'s own clause
   text through `verus.translate`; the copies in the block must equal the
   derivation exactly, and the gate fails if they do not. The collapse floor is
   derived from `model.py`'s `work_per_call` and is not settable here at all.
   `collapse.probe_inputs` should name **two inputs with different
   `work_per_call`**, or the marginal-rate assertion cannot run.
2. **`model.py`** — a *second* implementation of `spec.md` in Python, from the
   file bytes alone. Required API is documented at the top of p01's. It must not
   share code with the rungs beyond `common/slb.py`.

   Two lessons from p02's, the first non-p01-shaped one. **The bindings are
   yours to choose** — p01 binds `v/off/len/v_len/result`, p02 binds
   `src/src_off/src_len/dst_len/dst_after_len/dst_before/dst_after/result`,
   because a kernel that *writes* needs the buffer before and after to state its
   security property. And **argue for the unit of `work_per_call` in the
   docstring rather than assuming it**: ALPHA is justified in 64-bit-lane terms,
   so "bytes" is only safe if the kernel really does ≥0.25 instructions per
   byte. p02 measured 2.2–6.7 and kept bytes; a bare-`memcpy` kernel would have
   to denominate in 64-bit words and say so.

   If a payload shape is new, add its decoder to `common/` in all three
   languages (`slb_head2_u64_bytes` / `driver::head2_u64_bytes` /
   `slb.head2_u64_bytes` is p02's) — never to the pattern. Anything the driver
   allocates from an attacker-controlled size must be range-checked identically
   in C and Rust before allocating (`SLB_MAX_CAP`, exit 7), or the two languages
   diverge on `calloc`-returns-NULL vs allocator-aborts and it reads as a rung
   difference.
3. Generate the driver pin: `python3 harness/dloop.py <rung>.rs` prints the
   canonical token sequence; paste it into `driver.canonical`. Run it on
   `c/main.c` too and add `driver.aliases.c` entries until the two agree.
4. Get the pins right by running the gate and reading what it says the values
   are: obligation counts, identity levels, the derived `Ir` floor and the
   translated contract are all reported before they are asserted. Do **not**
   re-pin an obligation count without first finding out which item moved
   (`verus_run.py <file> --verify-function <name> --verify-root`) — the count is
   a skeleton checksum, not a semantic one.
5. **Then mutate your own proof and check the gate fails.** A pattern whose
   `spec.md` pins are copied from p01 without being re-derived is a pattern
   whose gate certifies p01. Include at least one mutant that makes a *trusted*
   postcondition **inconsistent** rather than merely weaker — p02's M7 verified
   cleanly and only the `spec.md` pin caught it (`.memory/04-verus.md`).

### The five demands steps 1–5 predate

Steps 1–5 were written at TASK_004. TASK_008/009/010 added checks that a pattern
author must satisfy **before** the gate will go green, and that nothing above
mentions. Budget for them up front; each has cost an engineer a surprise.

6. **Every trusted item needs a verified twin.** "Trusted" is keyed on
   `#[verifier::external_body]` + (a non-empty `ensures` **or** `unsafe`) — not on
   `unsafe` alone. For each such item write `fn slb_twin_<name>` with the **same
   signature and the same contract text**, body being the *checked* stand-in
   (`v[i]` for `*v.get_unchecked(i)`), gated `#[cfg(slb_twin)]`. Pin both counts:
   `verus.obligations.<src>` (shipped) and `verus.twin_obligations.<src>`
   (`--cfg slb_twin`). p02: 9 and 12, for two trusted items.
   - The token `slb_twin` may appear **only** inside a twin's own
     `#[cfg(slb_twin)]` attribute — anywhere else in the pinned file or anything
     it includes is a hard failure. A `#[cfg]`-varying `const` used in a
     `requires` was the bypass this closes.
   - `verus.twin_justifications` is the escape hatch, uncapped and shouted every
     run. (`MAX_TWIN_JUSTIFICATIONS = 1` existed briefly and was **deleted at
     TASK_007** — a manager-invented round number, redundant against the separate
     "every twin justified away" rule, and the only knob in the twin regime that
     could hard-fail an honest pattern with no route out.)
7. **Every trusted item needs a written human argument in `NOTES.md`**, marked
   `SLB-TRUSTED-ARGUMENT <src> <name>`, ≥200 chars, containing the literal labels
   `(a)`, `(b)`, `(c)`: (a) is the twin body the right checked stand-in;
   (b) is the `ensures` **complete** with respect to every unchecked operation the
   body performs; (c) does each clause mean the same in both configurations.
   The gate checks the marker, the labels and the length, prints the text in full,
   and cannot judge it. (b) is the one no oracle covers — a body that also reads
   `i + 1` passes the contract pin, the twin and the `--cfg` run unchanged.
8. **Miri is mandatory whenever the pattern has any trusted item**, not only when
   R4 ≠ R5 — the old rule made it optional exactly when byte-identity holds, which
   is the project's headline. `MIRI_PROBE_ITERS = 4`, `MIRI_TIMEOUT = 180`.
   `n_iters` can be clamped from the file header; **the payload cannot**, so a big
   input times out and becomes a documented blocked row (p01's `large.bin`).
   **Size the inputs with this in mind** — it is an `inputs/gen.py` decision, and
   cheaper to make before the build than after.
9. **The driver region must be code that runs.** Two rules, both added because a
   dead decoy region passed a full gate in *both* languages:
   - Structural: the pinned kernel item is called **exactly once** per rung
     source, and that call is inside the `SLB-DRIVER` region.
   - Dynamic: the region's enclosing function must have non-zero exclusive `Ir`
     and be the kernel's **only** caller, read from the callgrind profiles stage
     3b already writes.
10. **The `Ir` floor's composition is clamped.** It derives from `model.py`'s
   `work_per_call` × `work_unit_bits`, with an absolute clamp; the gate prints the
   effective absolute floor. `work_per_call`'s *unit* is still your argument to
   make in `model.py`'s docstring (step 2) — nothing checks that
   `work_per_call` is denominated in the unit `work_unit_bits` names.

11. **A Verus control that does not verify cleanly cannot live in a pattern dir
   at all** — measured at TASK_012, and it is a consequence of two existing rules
   meeting. `check.py:1446` requires *every* `.rs` in the pattern dir containing a
   `verus!` block to be pinned in `verus.obligations`, and `:1549` fails the gate
   for any pinned file reporting `n_err > 0`. `build.py`'s `--cell` list is closed
   `choices`, so the file cannot be built either. So a **deliberately broken**
   proof — the most valuable kind of control, the one that shows what an obligation
   is load-bearing *for* — has nowhere to live.

   Ship it as a `.temp/` artefact with (a) a **committed generator** that derives
   it from the shipped `verus.rs` by exact-string substitution and asserts its own
   hit count, so it cannot drift, and (b) a `NOTES.md` section carrying the diff,
   the commands and the measured output. p17 §1c is the model.

12. **The `slb-contract` block requires an `idiom` object** (TASK_016, gate stage
   `0b`): `required` — a non-empty list of what every rung must spell out;
   `forbidden` — spellings that would delete the pattern, **allowed to be empty**
   but shouted when it is; `why` — non-empty prose. Unknown keys are rejected, so
   a mistyped `forbid` cannot be silently empty. The gate checks **nothing
   semantic** — it requires the key, prints it in the verdict and in
   `results/tables/*.md` (via `report.py`, TASK_017), and hashes it.

   **Be exact about what the hash buys, because the first version of this entry
   was not.** *Editing or weakening the declaration* moves `contract_sha256`.
   **Changing a rung does not** — `read_contract()` hashes `spec.md`'s fenced
   block and nothing else; rung sources are covered by `source_sha256`. Nothing
   here prevents a forbidden respelling and nothing can without semantic
   checking, which the threat model forbids. TASK_016_REVIEW proved it by
   forking p05 with the forbidden spelling and gate-passing at an identical
   `contract_sha256`.

   What earns the mechanism its lines is **not** the hash: it is that the
   declaration is *structured*, so it can be printed next to every published
   number, and that consolidating six declarations into one diffable object made
   three latent specification defects visible at its first review.

   This exists because the declaration used to be prose. p05's `spec.md` forbade
   `chunks_exact` **by name** and two consecutive tasks measured it anyway and
   published the result as p05's number — the pin was at line 69 and the hashed
   block started at line 309. See `.memory/01-ladder.md` finding 14.

13. **A spelling-spread section in `NOTES.md` is mandatory for any pattern with
   more than one measured spelling.** At least two alternates per rung; the
   shipped, contract-conformant cell marked; deltas given as laws where swept and
   **flagged as interpolations where not**; and an explicit *"not the headline"*
   line. The spread is a result **about method** — the number stays the
   matched pair. p05 §13 (11 spellings), p16 §10 and p17 §10 are the models.

   The alternative — move the *specification* to match the mutant so it verifies
   `10 verified, 0 errors` with a load-bearing postcondition, giving "a program
   proved to meet its specification, whose specification is the bug" — is a
   genuinely better artefact, but it costs a second pinned Verus file with its own
   twin, `SLB-TRUSTED-ARGUMENT` block and `driver.regions` entry, on every gate
   run. Recorded as an open option, not taken.

Stage list, so a failure name maps to a function: `selftests`, `build`,
`checksums`, `no_collapse`, `marginal_ir`, `identity`, `adversarial`,
`verus_contract`, `call_site`, `clause_deletion`, `requires_strength`,
`trusted_twins`, `proof_domain`, `driver_identity`, `sanitizers`, `miri`,
**`idiom`** (stage 0b, reporting-only) and **`derive_contract`** (stage 5d0).

⚠ **This list said SIXTEEN until TASK_053 and there are EIGHTEEN** — the two in
bold were missing, and the sweep that found them found live defects in three
other stages at the same time. **If you are auditing the gate, enumerate from
`check.py`'s `head()` calls, not from this list.**

## What is committed

Committed: sources, `spec.md`, `README.md`, `NOTES.md`, `inputs/gen.py`,
`results/*.json`, harness code, `.memory/`, `.tasks/`.

Gitignored: `.temp/`, `inputs/*.bin`, build outputs, `results/tables/` is
regenerable but **is** committed for reviewability.

## Adding a sweep band costs a gate re-run, not a re-measure

**Measured at TASK_027, and nothing written down said so** — two earlier tasks
avoided shipping a sweep partly for fear of the cost, which is how p17's
"+32 Ir/call flat" got published from two bands that both had `nsuf = 3`.

Append the new band **last** in `inputs/gen.py` (TASK_020's argument: the
pre-existing blobs stay byte-identical — verified on p16, 95 of 95 matched, 0
changed lines). Then:

- `check.inputs_of` drops `sweep-*` from `inputs_checked`, and
  `measure.SKIP_INPUT_PREFIX = "sweep-"` drops them from the measurement matrix;
- so **no matrix input, no `inputs_checked` entry and no number in
  `results/pNN.json` depends on any sweep blob**;
- the only thing that moves is `source_sha256[inputs/gen.py]`.

**Cost: one `check.py pNN` run.** There is no reason for a pattern not to ship
the sweep its laws are derived from, and `gen.py` being inside `source_sha256` is
what makes those laws re-derivable from a hashed file.

Two conditions the rule depends on, both verified at TASK_027_REVIEW against the
harness rather than argued:

- **The `sweep-` prefix IS the mechanism**, hardcoded in two module-level
  literals (`check.py:459-460`, `measure.py:60`) with no pattern-specific input
  and no `spec.md` key that selects inputs. **A band named anything else enters
  the measurement matrix and costs a full re-measure.** Name it `sweep-*`.
- **The gate hashes `gen.py` and never the blobs**, so a sweep-derived law's
  reproducibility rests entirely on `gen.py` being *deterministic*. Verify that
  by regenerating twice and diffing, as p16 did (two runs byte-identical, and the
  95 pre-existing blobs unchanged) — it is one command and it is the whole basis
  of the claim.

## An input generator's RNG is a shared sequential stream — and it can re-converge

**Measured at TASK_034.** `inputs/gen.py` draws every blob from one advancing
RNG, so removing or adding a draw shifts every *later* blob. That much is
obvious. What is not: **`random.shuffle`'s rejection sampling makes word
consumption data-dependent, so the streams can re-CONVERGE** — after p11's
one-line generator fix only **three** blobs moved (`zerotail` as intended,
`stride3` which makes 0 kernel calls, and `sweep-len01k24` whose band-A lengths
are constant so no law could move), and the Mersenne Twister state was **equal**
from that point on (index 343 vs 339 immediately before, identical after).

**So: diff the blob set before and after any generator edit and say which moved.
Never assume "only the ones I edited", and never assume "everything after".**
Both guesses were available here and both were wrong.

## Editing rules

- `pilot/` is frozen evidence for `PLAN.md`. Do not edit it; p01 is its successor.
- `CLAUDE.md` stays minimal — links and DON'Ts. New prose goes in a topic doc and
  gets a link line, never inline.
- Any agent that learns a durable fact (a Verus workaround, a measurement gotcha)
  writes it to the right `.memory/` file or `../LearnVeri/PITFALLS.md` and says so
  in its report. Facts that live only in a chat log are lost.
