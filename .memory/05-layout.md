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
   meeting. `check.py::check_verus_contract` (stage 5a) requires *every* `.rs` in the
   pattern dir containing a `verus!` block to be pinned in `verus.obligations`,
   and fails the gate for any pinned file reporting `n_err > 0`. ⚠ **This
   sentence carried `:1446`, then `:2197`/`:1549`, and every one of them
   rotted** -- `:2197` now lands at module level and `:1549` inside
   `idiom_audit`. **This is demand 11, the ORIGINAL that three pattern files
   quote**, so a rotted hint here propagates. `build.py`'s `--cell` list is closed
   `choices`, so the file cannot be built either. So a **deliberately broken**
   proof — the most valuable kind of control, the one that shows what an obligation
   is load-bearing *for* — has nowhere to live.

   Ship it as a `.temp/` artefact with (a) a **committed generator** that derives
   it from the shipped `verus.rs` by exact-string substitution and asserts its own
   hit count, so it cannot drift, and (b) a `NOTES.md` section carrying the diff,
   the commands and the measured output. p17 §1c is the model.

   ⚠⚠ **COROLLARY, AND THE RULE ABOVE DOES NOT COVER IT: a REFUSED row has no
   pattern dir, so it has neither a generator to derive from nor a `NOTES.md` to
   put the diff in — and `.gitignore` contains `.temp/`, so every `.temp/` path
   its refusal block cites is ABSENT FROM A FRESH CLONE.** The rule above
   silently assumes a shipped `verus.rs` exists to substitute into.

   **So: a refused row's reusable artefact is EMBEDDED VERBATIM in its committed
   `.tasks/TASK_NNN_REPORT.md`, with its `sha256` and its verification output
   beside it**, and the catalogue's refusal block cites **that section**, never
   the `.temp/` path. **`p15` is the instance and the reason this corollary
   exists**: its refusal block was written citing
   `.temp/t85/v01_validator.rs` — a **verified UTF-8 validator, `5 verified, 0
   errors`, zero trusted items**, and the most reusable thing the row produced —
   and that path does not survive a clone. ⚠ **Check this whenever you refuse a
   row: the more valuable the residue, the more likely it is sitting in
   `.temp/`.**

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
   block started at line 309. See `.memory/01-ladder.md` **finding 3** (the named-spelling / two-step reslice entry). ⚠ This said "finding 14", which in that file is **p13**; the `chunks_exact` content is finding 3.

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
  literals (`check.py`'s inline `sweep-` test, in `check.py::inputs_of` -- it has **no**
  module-level literal, despite this line having claimed `:459-460` and then
  `:474`, which now lands in `Report.ok` -- and `measure.py::SKIP_INPUT_PREFIX`) with no pattern-specific input
  and no `spec.md` key that selects inputs. **A band named anything else enters
  the measurement matrix and costs a full re-measure.** Name it `sweep-*`.
- **The gate hashes `gen.py` and never the blobs**, so a sweep-derived law's
  reproducibility rests entirely on `gen.py` being *deterministic*. Verify that
  by regenerating twice and diffing, as p16 did (two runs byte-identical, and the
  95 pre-existing blobs unchanged) — it is one command and it is the whole basis
  of the claim.

## ⚠ A generator that EMBEDS shared text will silently revert a cross-pattern amendment

**p27, TASK_063, found by running the generator rather than by reading it.**
`CLAUDE.md` constraint 6 says *keep the generator, delete the artefact* — a
pattern's `spec.md` is meant to be re-derivable from `controls/mk*.py`. p27's
generator **embedded its whole `idiom.why` as a literal**, and one task earlier
TASK_062 had appended the 11 003-byte shared named-spelling paragraph to that
`why` **in `spec.md` only**.

> **So running the documented regeneration path DELETED the paragraph** — a `why`
> of 2 602 bytes where the committed one is 13 607 — reverting, silently, a fix
> that had landed the previous task and cost a full 18-pattern sweep.

**The shape that does not do this**: slice the shared text out of a **donor**
`spec.md` at run time and assert its `sha256` against
`check.NAMED_SPELLING_SHA256`, so the generator **fails closed** if the donor
moves. p10's and p18's `mkcontract.py` already did it that way; **p27's was the
outlier**, and it is now repaired and reproduces `spec.md` byte for byte.

**The general rule, and it is not only about this paragraph:** *any text shared
across patterns must be READ by a generator, never embedded in one.* An embedded
copy makes the generator a nineteenth copy of an invariant that is supposed to
have one, and the failure is invisible until somebody runs it.

⚠ **What caught it was the gate check added the task before** — without
`named_spelling_problem`, the regenerated `spec.md` would have passed. **A check
added for one accident caught a second, of a different shape, one task later.**
That is worth remembering the next time the accident test is argued.

✅ **Owed and now CLOSED (manager, at the TASK_063 boundary).** p10's and p18's
generators were only *reported* to read from a donor. Both were re-run:
`p18 .../mkcontract.py --check` prints *"spec.md matches the generator"*, and
p10's `--write` reproduces its `spec.md` **byte for byte** (backed up, run,
`diff` empty, restored, sha256 verified). **Neither has p27's defect.**

⚠ **And running them surfaced a discrepancy that looks like an invariant break
and is not — check which SPAN a claim is about before believing it.** p18's
generator prints *"shared paragraph: 11004 chars, byte-identical in 15
pattern(s); differing/absent in ['p16-tlv-walk', 'p17-http-range']"*, while the
standing one-liner reports **one hash across every pattern**. Both are right:

| measurement | span | what it asserts |
|---|---|---|
| the standing one-liner, and `check.py::named_spelling_problem` | `MARK` … `'p01 and p08 neither'+19` | the paragraph is **present and verbatim**, anywhere in `why` |
| p18's `shared_why()` | `MARK` … **end of `why`** | the paragraph is present **and is the LAST thing in `why`** |

**p16 and p17 carry pattern text AFTER the paragraph**, which the first accepts
and the second does not. **Position is not the invariant** — the gate check was
deliberately built not to require it. The two counts (11003 vs 11004) differ for
the same reason. This is the third time a "shared paragraph" number has been
compared across incompatible slices; **quote the span with the number.**

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

## What is hashed, what is generated, and which layer nothing watches

⚠ **`patterns/*/*.md` IS in the gate `source_sha256`** (TASK_077_REVIEW M6,
manager-verified: p22's record hashes its `NOTES.md`, `README.md` and
`spec.md`). **So a PROSE fix to any pattern doc costs a gate re-run** — a cost
column that answers only *"is it inside the `slb-contract` block?"* will say
"free" for eight sites that are not. `measure.py`'s `provenance()` does **not**
glob `*.md`, so the same edit costs **no re-measure**.

⚠⚠ **AND THERE IS A GENERATED, UNHASHED LAYER THAT NOTHING WATCHES.**
`results/tables/*.md` and `results/synthesis.md` are produced from the records
and are in **no** hash set — so `--check-stale` cannot see them, no gate stage
validates them, and they rot silently. Measured at TASK_077/078: **`p22`'s
verdict stayed wrong in `results/synthesis.md` after the gate had been fixed**,
and **4 of 22 tables were content-stale** — three citing a superseded
`contract_sha256`, two publishing pre-TASK_069 audit counts.

- ⚠ **"22 of 22 tables are stale" was an ARTEFACT**: `report.py --stdout` emits
  one trailing blank line the file writer does not, so a naive diff flags every
  table. **Compare content, not bytes.**
- ⚠ **`results/synthesis.md` cannot simply be regenerated after a gate sweep.**
  `synthesis/licence.json` pins each gate record's `source_sha256`, so a naive
  re-run publishes **22 `LICENCE STALE` verdicts** — worse than the one wrong
  row it was meant to fix. **Re-emit the sidecar first, then the artefact.**

**Regenerating both costs no gate run and no re-measure.** Do it whenever a
verdict, a contract hash or an audit count moves.

## ⚠ `vparse.parse()` DROPS BODY-LESS ITEMS ON PURPOSE — widening it turns p36 red

(TASK_082. **The manager predicted the opposite and was wrong; this is the
measurement.**)

`harness/vparse.py::parse()` keys on `fn NAME` **with a body** and skips anything
body-less. When TASK_081 found that the gate therefore cannot see an
`assume_specification`, the obvious repair was to delete that skip. ⚠⚠ **It
breaks a green pattern, today, and not because of axioms at all.**

**A trait method DECLARATION is body-less.** `patterns/p36-vtable-dispatch/verus.rs`
declares `fn apply` and `spec fn spec_apply` in the trait and defines them in the
impl:

```
:141  fn apply(&self, x: u64) -> (r: u64)        <- trait decl, body-less
:146  spec fn spec_apply(&self, x: u64) -> u64;  <- trait decl, body-less
:166  fn apply(...) { ... }                      <- the impl
:186  open spec fn spec_apply(...) { ... }       <- the impl
```

Keep the declarations and `vparse.by_name` — which is **bare-keyed** — raises
`ValueError: duplicate item name(s): apply at lines [166, 141], spec_apply at
[186, 146]`, and **six consumers turn that into a gate failure** (RECAP "Owed"
20 is the record of this map's fragility). **p36 goes red in six stages, and its
other three rung sources declare `apply` the same way.**

⚠ **And it would count the wrong thing anyway**: a trait method declaration is
**not** a trusted item — it is proved by its impl.

⚠⚠ **AND THERE ARE AT LEAST FIVE BODY-LESS TRUSTED FORMS, NOT THREE — TASK_082
COUNTED THREE AND TASK_083_REVIEW FOUND TWO MORE PLUS A PATH HOLE.** All
manager-verified. **A body-less trusted declaration is any construct that makes
Verus believe something about code it never checks**, and the keyword list is:

| form | counted at TASK_082? | why it is missed |
|---|---|---|
| `assume_specification` | ✅ | — |
| `axiom fn` / `broadcast axiom fn` | ✅ | — |
| `uninterp spec fn` | ✅ | — |
| **`#[verifier::external_trait_specification]`** | ❌ | **54× in the pinned vstd**; the attribute sits on a `struct`/`trait`, so **no item carries `.external`** and the TCB inventory is empty |
| **`#[verifier::external_fn_specification]`** | ❌ | `\bverifier::external\b` **does not match** — the next character is `_` — so `.external` is `None` and in `verus.items` it is **indistinguishable from a verified function** |

**Demonstrated:** Verus reports `2 verified, 0 errors` proving `r == 0`; the
compiled program **prints 7**; `axiom_decls` returns `[]`; 5c-twin shouts *"no
trusted item"*. ⚠ **And Verus PRINTS the `external_type_specification` line for
you to paste**, which is the same accident vector as `assume_specification`'s.

⚠⚠ **A THIRD HOLE THAT IS NOT ABOUT KEYWORDS: `os.listdir` IS FLAT.** The axiom
scan runs over the obligation set and its one directory guard does not recurse,
so **an axiom in a `#[path]`-included SUBDIR module is invisible**. ⚠ **This
vector is live in all 22 patterns** — every `verus.rs` `#[path]`-includes
`common/driver.rs`. `_scan_unsafe_sites` already walks `_path_includes` for
exactly this threat; **copy that walk.**

⚠ **And the PUBLISHED column still cannot see any of it**: `synthesize.py` reads
**`tcb_items`**, and *"axiom"* appears **zero times** in `synthesis/*.py` or
`results/synthesis.md`. **A `results/synthesis.md` that regenerates
byte-identical after adding `axiom_decls` is NOT evidence that nothing moved —
it is evidence the published column never reads the field.**

> **The rule: `parse()`'s skip is load-bearing. To make a NEW class of item
> visible, add a separate keyword-keyed matcher — do not widen `parse()`.**
> That is what `vparse.axiom_decls()` is, and `vparse.py selftest` now pins
> **both** directions: body-less trait decls stay out of `parse()` *and* are not
> counted as axioms. ⚠ Note `assume_specification` has **no `fn` token at all**,
> so `parse()` never had a route to it — widening the skip would have paid p36's
> price and still not found the thing it was aimed at.

## Editing rules

- `pilot/` is frozen evidence for `PLAN.md`. Do not edit it; p01 is its successor.
- `CLAUDE.md` stays minimal — links and DON'Ts. New prose goes in a topic doc and
  gets a link line, never inline.
- Any agent that learns a durable fact (a Verus workaround, a measurement gotcha)
  writes it to the right `.memory/` file or `../LearnVeri/PITFALLS.md` and says so
  in its report. Facts that live only in a chat log are lost.

## The axiom scan: key convention, the disjointness rule, and a span-guard trap

(TASK_084, closing RECAP "Owed" 0's routes B1–B3. ⚠ **UNREVIEWED —
`TASK_084_REVIEW` attacks it next.**)

**Key convention for an axiom outside the pattern dir: the path RELATIVE TO THE
REPO ROOT.** `verus.axioms["common/driver.rs"] = 1`, not
`"../../common/driver.rs"` — that spelling has many forms normalising to one
file, it moves if the pattern dir moves, and repo-relative is what
`_scan_unsafe_sites` already prints. **It cannot collide with a
`verus.obligations` key**, because those are bare filenames with no `/`. Hits
land as `record["verus"][<relpath>] = {"path_included": true, "axiom_decls":
[...]}`, so `synthesize.py`'s `.get("verus.rs")` is untouched.

⚠ **The blast radius is the whole tree and that is the point:** one axiom planted
in the **real** `common/driver.rs` takes **0 of 22 → 22 of 22 patterns failing**.
Every `verus.rs` `#[path]`-includes it, and before this the scanned file list was
`sorted(pinned_obl)`, so **the module was never opened.**

**THE DISJOINTNESS RULE — body-less → `axiom_decls`, bodied → `.external`.**

| form | has a body? | seen by |
|---|---|---|
| `assume_specification` | no `fn` token at all | `axiom_decls` |
| `broadcast axiom fn`, `uninterp spec fn` | body-less | `axiom_decls` |
| `external_trait_specification` methods | body-less | `axiom_decls` |
| `external_type_specification` | declaration | `axiom_decls` |
| `external_fn_specification` | **must have one** | `parse().external` |

⚠ **`external_fn_specification` CANNOT be written body-less** — measured, not
assumed: Verus rejects it twice, `error[E0308]: ... implicitly returns () as its
body has no tail`, and on a unit return `error: assume_specification encoding
error: body should end in call expression`.

⚠⚠ **And Verus's own error message calls an `external_fn_specification` an
"assume_specification".** They are **one mechanism**, which is the argument for
treating the bodied form as trusted-not-verified.

⚠⚠ **`impl_spans`' LIMIT 2 GUARD SHAPE IS A LIVE TRAP FOR ANY NEW SPAN
FUNCTION.** `trait_spans` was written by copying that guard and **missed every
ATTRIBUTED trait** — i.e. **every external-trait declaration, the entire target**
— because the guard does not allow `]` in the preceding item position and an
attribute ends in `]`. **Caught by a probe, not by reading it.** Copy
`impl_spans` and you inherit its documented limit silently; **if a new span
function must see attributed items, allow `]`.**

## ⚠ The published TCB total is 90, and the "92" that four documents quote is a DIFFERENT SUM

`results/synthesis.md` prints **90 items / 188 lines**. That is the sum over
**`verus.rs` only**, which is what `synthesize.py` reads (`TCB_SRC`, pinned the
way `R5_PAIR` is). **92 is the sum over ALL pinned Verus sources**, and the
difference is **p01's `safe_naive_verus.rs`** (`['load_input','emit']`) — p01
being the only pattern with two.

⚠ **Both numbers are real; the error is the LABEL.** `RECAP.md`, `TASK_082.md`,
`TASK_083.md` and `TASK_083_REVIEW_REPORT.md` all quote **92 as the published
total**, and the last one **names this very table while doing so**. ✅
**Manager-verified: `results/synthesis.md` `| **total** | ... | **90** |`, and
the all-sources sum recomputed from `results/gate/*.json` is 92.**

⚠ **Summing them would be WRONG, not merely different**: `safe_naive_verus.rs`
proves the **R2** rung panic-free, so its trusted base is not R5's, and the sum
describes no rung. **Reading one source is correct; failing to SAY SO is the
defect** — which is why the table now carries a footnote computed from the
records every run, so a second pattern growing a second Verus source
**announces itself** rather than being silently dropped.

## ⚠ A `spec.md` prose fix outside the fenced block costs a GATE RE-RUN, not a contract move

`read_contract()` hashes **`spec.md`'s fenced block and nothing else**. p01's
`| identity |` row is in the **prose above the fence**, so correcting it left
`contract_sha256` at `5360d6f3…` **byte-identical** and moved only
`source_sha256[patterns/p01-array-sum/spec.md]`.

⚠⚠ **DO NOT WRITE THE CHARACTER OFFSETS HERE, AND THE FIRST VERSION OF THIS
PARAGRAPH DID.** It said *"the row sits at 5473 and the fence opens at 5676 —
**203 characters** outside it"*. ⚠ **All three numbers were stale before the
commit that recorded them**: the edit being described **lengthened the row by 405
characters**, so the post-edit gap is **592**, and 5676-vs-5660 is the difference
between the fence *marker* and the fence *content* start — **two people measuring
two things and both being right** is exactly how the `check.py:NNNN` citations
rotted. **This is "line citations decay" in numeric form.** State the
**invariant** — *the row is in the prose, before the fence* — and give the
command, never the offsets:

```python
s = open('patterns/pNN-x/spec.md').read()
s.find('| `identity` |') > s.find('```slb-contract')   # False ⇒ outside the hash
```

**The practical rule: an edit to `spec.md` PROSE costs one gate re-run; an edit
inside the fence costs a contract move and everything that hangs off it.** Check
which side of the fence you are on before budgeting — a manager task file
budgeted this one as a contract move and it was not.

## ⚠ A `#[path]` include used in a GATE TEST must be an ABSOLUTE path

**PROVISIONAL — measured at TASK_088.** Stage 5's clause-mutation arms **copy
the pattern** to `.temp/clausemut/<pid>/patterns/<slug>/`, so a `pdir`-relative
`#[path]` **does not resolve from there** and the run reports
`[clause-mut]` / `[req-mut]` / `[twin]` failures that are **artefacts, not
detections**.

⚠ **This is the same class as the *"7 failures, all diagnostic-mode"* recorded
for `TASK_084_REVIEW` route J — so RECAP's summary of that route,
*"fully green with no gate output at all"*, is LOOSER than the review's own
text.** With an **absolute** `#[path]` the control is clean: 0 failures, `PASS`,
byte-identical.

**Key convention, extended at TASK_088:** `verus.included_tcb[<repo-relative
path>]` declares bodied trusted items in `#[path]`-included files, sibling to
`verus.axioms`. **`_verus_file_list` is now the single DEDUPED file list every
Verus-side detector shares** — `_trusted_items`, `_axiom_items`, the
`assume(`/`admit(` shout and `_check_included_tcb`. Before that, `_axiom_items`
had been widened alone and the other three still iterated `verus.obligations`,
which is how a false `ensures` one hop away shipped green.
