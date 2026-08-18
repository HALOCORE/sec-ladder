# TASK_023 — one sentence, six hashed declarations, measured false

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `patterns/p05-index-flatten/NOTES.md`
**§14h.3** (which flags this and says why it was left), and
`.memory/01-ladder.md`'s named-spelling-standard block, already corrected by the
manager and the wording to follow.

## The problem

All six patterns' `idiom.why` end with, byte-identically:

> *"`R3ship − R4ship` is an UPPER BOUND on the in-contract safety tax and never
> the tax itself."*

**Measured false at TASK_022.** It holds only while **one rung is held fixed**.
With both rungs free to be respelled inside the contract, p05's in-contract pair
interval is `2·nrow − 2 … 6·nrow + 20` = **36…134 / 128…410**, and the published
`123 / 399` sits **inside** it — so `6·nrow + 9` does not bound the tax from
above at all. The bottom endpoint is **exactly 0.00** (`sweep-r1c30`): an
admissible pair on which safe and unsafe cost the same.

The text is hashed into `contract_sha256`, so this is one cross-pattern edit and
six gate runs. That is the whole task.

## What to write instead

Three claims, all measured, none of which may be dropped:

1. **`R3ship − R4ship` bounds `inf(in-contract R3) − R4ship` from above** — and
   it is a bound *only because R4 is fixed by fiat*, not because it was
   minimised. Say that explicitly; it is the sentence's actual content.
2. **`min(R3 found) − min(R4 found)` is the difference of two upper bounds and
   bounds nothing in either direction.** Do not offer it as the repair. Measured
   consequence: the same edit is **−2 on R4 and +1 on R3**, so the constant does
   not cancel; and p05's third "minimum" **exceeds** its published figure for
   `nrow ≤ 3`.
3. **What to publish is the in-contract *pair interval***, with the shipped pair
   located inside it.

Keep it as short as the sentence it replaces. These `why` blocks are already
4000–7500 chars and one of them was called unreadable at review; **do not grow
them.** If you can make the replacement shorter than the original, do.

## Ride-alongs, since six gates are running anyway

- `patterns/p16-tlv-walk/controls/gen_controls.py`'s docstring still says p08's
  `#[path]` defect is *"Reported rather than fixed for p08 (TASK_021)"*.
  TASK_022 fixed it. One line, stale.
- Check no other pattern's prose asserts the refuted sentence outside the hashed
  block. Grep; do not recall.

## A question I want answered, not assumed

p05 is the only pattern whose **unsafe** side has been searched in contract. The
sentence is false *for p05*. **Is it false for the others, or merely unverified?**
p16, p17 and p02 have in-contract spreads on the R3 side only.

Cheapest decisive probe: on **one** of them, respell the unsafe rung in contract
once and see whether it moves at all. If it does not move on p16 or p17, say so —
that is a real difference between patterns and it changes how the replacement
sentence should be qualified. **Do not build a full spread**; one probe, reported
either way.

## Done when

The sentence is replaced in all six `idiom.why` blocks, byte-identically; the two
ride-alongs are done; all six gates green; `md5_fn` unchanged; `contract_sha256`
moved on all six. The probe's answer is reported whichever way it goes.

Prose first, gates last.

## Constraints

No root; no `/tmp` (scratch `.temp/p23/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose and `patterns/p16-tlv-walk/controls/gen_controls.py`
only — **nothing in `harness/`, no cell source**. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. Check `git status` before finishing.

**Expect gate-record noise and do not chase it**: p05 churns ~4 leaves per run
(two heap-OOB stdouts, two ASan PID/ASLR strings) and p08 ~8
`marginal_ir_per_call` leaves at ±0.02 on `O0`/`whole`, with identical binaries.
Both are documented in `.memory/03-measurement.md`.

Notes to `.temp/p23/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-eight
agents have contradicted the manager's written instructions and all twenty-eight
were right; the last one broke the number this task's predecessor was written to
land. What I am least sure of is **whether the replacement belongs in `why` at
all** — it is a general fact about the ladder, not about any one pattern's idiom,
and six byte-identical copies of a general fact inside six hashed blocks is how
the last one came to be wrong in six places at once. If it belongs in
`.memory/01-ladder.md` alone with a one-line pointer from `why`, say so.
