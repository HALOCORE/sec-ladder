# TASK_133 — re-adjudicate the five unreviewed TEMPORAL refusals against the AMENDED bar

**Role: research reviewer.** You are reviewing the *manager's* adjudications, not
an engineer's build. Your deliverable is a verdict per row plus **the finding**.

Read first: `RECAP.md` START HERE box, `.tasks/PROTOCOL.md`,
`.memory/02-bench-rules.md` **last section** (the priority shift — read it
before anything else), `.memory/01-ladder.md`'s four-outcome law **and its new
scope note**, and `.memory/06-catalogue.md` rows `p29 p30 p32 p33 p34`.

## Why this task exists, and what changed under these five rows

`p29`, `p30`, `p32`, `p33`, `p34` are **the entire temporal wing of the
catalogue** and all five carry `PROVISIONAL, UNREVIEWED`. They were refused at
`TASK_093`–`TASK_100`.

⚠⚠ **They were refused under a bar that has since been AMENDED.** The bar at the
time admitted a row that brings a new MECHANISM — a new operator on the safety
line, a new source of the bound, or a new reason the check is or is not elided.
**All three limbs presuppose a COST GRADIENT to price**, and most temporal
candidates have none — which is exactly how these five died, and dying that way
was the RIGHT verdict under the OLD bar.

**A fourth limb now exists** (`.memory/02-bench-rules.md`):

> a row is admissible if it **MAPS A BOUNDARY OF THE INSTRUMENT** — a rung that
> cannot EXPRESS the program, a proof that cannot STATE the obligation, or a safe
> rung that is SILENTLY WRONG.

**And the user has forbidden new SPATIAL rows.** The corpus is 15 spatial / 1
temporal / 1 type out of 26. The budget goes to temporal and type.

⚠ **So the question this task answers is NOT *"were these refusals right?"*** It
is: **does any of the five become admissible on the fourth limb, given that a
non-cost result is now a shippable result?** A refusal can have been correct in
2093 and wrong today without anybody having made a mistake.

## The manager's position, stated so you can refute it

⚠⚠ **Put my least certain call in your report by name and measure it.** Every
agent that has contradicted me with a measurement has been right.

**I think `p29` is the one that flips, and I think `p32`/`p33` is the one that
should not.** My reasoning, which may be wrong:

- **`p29`** — outcome 5, the only *good* outcome of the four-outcome law. Its
  refusal's limb (b) was **already refuted three ways by me** (see the cell), so
  the row today rests on limb (a) plus *"the shipped kernel cannot host a
  pointer"*. It carries a **fully verified BST** — `9 verified, 0 errors, TCB 0`,
  recursive `Box<Tree>`, three-case `remove` with in-order successor, 3-of-4
  mutants failing — embedded in `.tasks/TASK_095_REPORT.md`. That artefact is
  the most expensive thing this project has ever built and then not shipped.
- **`p32`/`p33`** — outcome 3, *the type system is silent*. This is a **fourth-limb
  bullseye on its face** (*a safe rung that is SILENTLY WRONG*, Miri-clean, under
  `#![forbid(unsafe_code)]`). But I believe it is **`p04`'s shipped class** and
  therefore a duplicate, not a boundary. ⚠ **I am least sure of this one.** If
  the silence is a *temporal* silence and `p04`'s is a *logical* one, they are
  not duplicates and I am wrong.
- **`p30`** — I expect the refusal to stand; its own second limb is already
  struck for reusing the retracted `E0382`/`E0499` sentence.
- **`p34`** — outcome 4, *the safe rung is WORSE than C* (`Rc` cycle leaks,
  `Weak` does not; manager-re-run: `miri cycle` → 5 `memory leaked`, `miri weak`
  → 0). Fourth limb again. ⚠ **But `p42` already ships *provably memory-safe and
  still leaking*, so ask whether this is `p17`/`p42`'s result with a new
  vocabulary.**

## The structural constraint that decides expressibility — RUN IT, DO NOT ASSUME

⚠⚠ **A shipped kernel takes a flat blob**: C
`kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)`, Rust
`kernel(buf: &[u8], off: usize, len: usize) -> u64`, and the driver loop is
**pinned identical across all seven rungs**, so there is nowhere rung-specific
to build a structure.

✅ **`p27` shows this is not fatal to a temporal row**: its slab and handle table
live **inside** the kernel and the blob carries an OPCODE STREAM. Its `spec.md`
records that the alternative — passing the slab as an argument — dies on
`harness/dloop.py:361`'s arity check.

⚠ **`p29`'s cell asserts *"22 of 24 patterns take their payload from a file blob,
so the shipped kernel cannot host a pointer"*. That count is stale (26 patterns
now) and the CONCLUSION does not obviously follow from it, since `p27` hosts
pointers fine.** **Re-derive the count and re-test the conclusion.** This is the
single most load-bearing sentence under three of the five refusals.

## Deliverables

1. **Per row, a verdict**: `REFUSAL STANDS` / `REFUSAL STANDS, REASON CORRECTED`
   / `RE-OPENED — ADMISSIBLE ON LIMB 4`. Each with the evidence that decided it.
   A right verdict on a wrong reason is `p31`'s failure mode and must be called.
2. **The expressibility question, measured**: can a kernel of the pinned shape
   host each of these five structures? `p27` is your existence proof; find where
   the boundary actually is.
3. **At most ONE row re-opened.** If two look admissible, rank them and say why
   the loser loses. Build budget is the scarce thing, not candidates.
4. ⚠ **If a row re-opens, it does NOT get built here.** You hand back a
   candidate with its first deliverable named — the way `p25`'s cell names
   *"settle the addressing mode first"*.

## Rules

- `.temp/t133/` only. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. You may not
  `git add`/`git commit`. Read-only git is fine.
- **Do not run `harness/check.py` or `harness/measure.py`** — a concurrent agent
  is running and those touch shared records. Compile, run, `valgrind`, `miri`
  and `verus_run.py` in `.temp/t133/` are all fine.
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; every harm probe owes a **positive control that must fire**.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_133_REPORT.md`. **PROTOCOL rule 2: you carry 634.**
  Close with your branch delta and the sum.
