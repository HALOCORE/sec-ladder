# TASK_134 — probe FOUR non-spatial candidates, in ONE task, BEFORE any row is written

**Role: research engineer.** Deliverable is **four probe verdicts and their
measurements**, not a pattern. ⚠⚠ **You are explicitly forbidden to build a
pattern in this task.** Two manager-proposed axes have been refused after being
scheduled, and **both died on a claim one `grep` plus one run would have
settled**. This task is that `grep` and that run, done first, for four
candidates at once.

Read first: `RECAP.md` START HERE box, `.tasks/PROTOCOL.md`,
`.memory/02-bench-rules.md` **last section** (the priority shift and the bar's
new fourth limb), `.memory/01-ladder.md`'s four-outcome law **and its scope
note**, `.memory/06-catalogue.md` rows `p25` and `p35`.

## The setting

The corpus is **15 spatial / 3 logical / 1 temporal (`p27`) / 1 type (`p38`) /
1 resource / 1 side-channel / 1 UB-not-mem / 1 non-termination / 1 aliasing /
1 calibration**, out of 26. **The user has forbidden new spatial rows.** A row
whose bug is *an access outside the object* is REFUSED ON SIGHT.

The bar now has a fourth limb: **a row is admissible if it MAPS A BOUNDARY OF THE
INSTRUMENT — a rung that cannot EXPRESS the program, a proof that cannot STATE
the obligation, or a safe rung that is SILENTLY WRONG.** A non-cost result is a
shippable result. `p17`, `p36`, `p42` and `p08` are all already of that shape.

## The structural constraint every candidate must clear FIRST

A shipped kernel takes a flat blob — C
`kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)`, Rust
`kernel(buf: &[u8], off: usize, len: usize) -> u64` — and **the driver loop is
pinned identical across all seven rungs**, so there is nowhere rung-specific to
build a structure, and no pointer can be passed in.

✅ **`p27` is the existence proof that a temporal row still fits**: its slab and
handle table live **inside** the kernel and the blob carries an **opcode
stream**. Its `spec.md` records that the alternative — the slab as an argument —
dies on `harness/dloop.py:361`'s arity check, and that the dead-argument escape
is free at `-O3` and `+3.00 Ir`/call at `-O0`.

⚠ **For each candidate, the FIRST question is: can the bug survive being driven
by an opcode stream inside a single kernel call?** A bug that needs a pointer to
outlive the kernel invocation is not portable here, and that is a finding, not a
failure.

## The four candidates

### (1) `p25` — dynamic array with `realloc` growth. THE FRONT-RUNNER.

⚠⚠ **The one row on which this project has run NOTHING.** Temporal, canonical,
and **outside the four-outcome law's scope** — that law is about POINTER-BACKED
structures and `p25` is a **flat growable buffer**, so it cannot be refused by
citing it.

⚠⚠⚠ **FIRST DELIVERABLE, BEFORE ANY OTHER WORK ON THIS ROW: SETTLE THE
ADDRESSING MODE.** **A stale INDEX is not a stale POINTER.** If the natural port
uses indices, the bug vanishes into `p04`'s class and **the row is dead**.
`TASK_124` refused `CVE-2021-23017` for exactly this kind of port choice. Decide
it with a compiled, run artefact, not by reading.

Then: safe Rust's `Vec` makes a stale `&T` across a `push` a **compile error**,
so the safe rung may be unable to EXPRESS the bug — `p08`'s shape, admissible on
limb 4. ⚠ **Is that true of `&T`, of a raw pointer taken from `as_ptr()`, and of
an index? Three different answers are possible and the row depends on which.**

⚠ Also open and worth one measurement: `growth overflow` is the OTHER half of
this row's bug column and it is **arithmetic, not spatial** — `cap * 2` or
`cap * sizeof(T)` overflowing. Ask whether that half is `p05`'s class.

### (2) A stack-lifetime row — returning/retaining a pointer to a dead frame.

Outside the four-outcome law's scope (it is not about the allocator at all).
⚠ **The hard question is expressibility under the pinned kernel shape**: the
classic bug needs the pointer to escape the function. Ask whether an
opcode-driven variant inside one kernel call is still the same bug or a
different, weaker one. **If it is weaker, say so and kill it** — do not ship a
diluted port.

### (3) Iterator invalidation — mutating a container while iterating it.

⚠ **This is the candidate I expect to be most interesting and I am least sure
of.** Safe Rust rejects it at COMPILE TIME at **zero instructions**, which is
the mechanism the four-outcome law does not contain (that law's four outcomes
all name RUNTIME mechanisms — see the scope note). ⚠⚠ **So this candidate is
also a test of the law itself: if the borrow checker is a second temporal
mechanism, the law is INCOMPLETE, and that is a finding independent of whether
the row ships.**
⚠ Ask honestly whether the C rung's bug is genuinely temporal or is a
*re-derivation of a stale bound* — if the latter it is spatial and REFUSED ON
SIGHT.

### (4) `p35` — tagged union / discriminated dispatch. **TYPE, and BLOCKED, not refused.**

The type axis has **one** row (`p38`). ⚠ **`p35` is blocked by TWO rules and the
premise it was last scheduled on is REFUTED** — read the cell and
`.memory/02-bench-rules.md`'s decision block; `_scan_unsafe_sites` **stays as it
is** and will not be changed for this row. **So the probe is: is there a
spelling of `p35` that is not blocked at all?** If the answer is no, that is a
clean instrument-boundary finding and the row dies for a stated reason.

## What a probe verdict must contain

For each of the four:
1. **Expressibility** — does it fit the pinned kernel shape? Evidence, run.
2. **The bug, demonstrated** — a C rung that actually does the wrong thing, with
   a detector firing (`valgrind`/ASan/Miri as appropriate) **and a positive
   control that must also fire**.
3. **What each Rust rung does** — compiles? refuses? silently wrong? Under
   `#![forbid(unsafe_code)]` for the safe rungs.
4. **Which limb of the bar it would be admitted on**, if any. Limb 4 is
   legitimate; a cost gradient is a bonus, not a requirement.
5. **Duplication check against the 26 built rows** — the largest single family of
   catalogue kills, 6 of 22. Name the row it would duplicate and say why it does
   not, or concede.

⚠⚠ **Rank the survivors and recommend ONE.** If none survives, say so plainly —
*"the non-spatial candidates are exhausted"* is a real and publishable result,
and it is the honest outcome if that is what you measure. **Do not manufacture a
survivor to satisfy the priority.**

## Rules

- `.temp/t134/` only. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** You may not `git add`/`git commit`. Read-only git is
  fine. **Do not create `patterns/p25-*/` or any pattern directory.**
- **Do not run `harness/check.py` or `harness/measure.py`** — a concurrent agent
  is running and those touch shared records.
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- ⚠ **Grep `~/tools/verus/vstd/std_specs/` specifically** before claiming no
  spec exists — a trait declaration in `vstd/<mod>.rs` is NOT the specification,
  and that confusion has produced a false *"no spec exists"* claim **twice**.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_134_REPORT.md`. **PROTOCOL rule 2: you carry 634.**
  Close with your branch delta and the sum. ⚠ **A concurrent branch also carries
  634; reconciliation is the manager's, not yours.**
