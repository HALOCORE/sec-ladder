# TASK_092 — land `p46`'s corrections, and settle the question its framing rests on

**Role: research engineer.** Read `.tasks/PROTOCOL.md` (**rule 6 now has a new
step — read it**), then this file, then `.tasks/TASK_089_REVIEW_REPORT.md`,
which is the whole of Part A.

Scratch in `.temp/t92/`. No other agent is running; you own the repo.

---

## ⚠⚠ PART A0 — THE QUESTION EVERYTHING ELSE DEPENDS ON. DO IT FIRST.

`TASK_089_REVIEW` **B1** refuted the *reason* p46 excluded its cheapest unsafe
spelling, **but not the conclusion.** The pinned vstd **does** specify a mutable
sub-slice at the value level (`~/tools/verus/vstd/std_specs/slice.rs`,
`assume_specification[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with
`final(r)@ == final(slice)@.subrange(...)` — ✅ manager-verified).

**So: does `r4_mutreslice`'s FULL R5 close?** Build it and report
`N verified, M errors`.

⚠ **This is not a detail. It decides p46's headline.** `r4_mutreslice` beats the
shipped R4 **and every safe spelling** by **697…2597 `Ir`/call**. If it is
admissible:

- **"both spans degenerate" FAILS** — the R4 span is ~2600, not 3;
- **"safe Rust beats unsafe" may invert**, because the cheapest admissible
  unsafe spelling would be cheaper than every safe one;
- and p46's `spec.md` `why`, `NOTES.md` 0c/8b, `README.md` and two rung sources
  all need rewriting rather than patching.

**If it does NOT close, say exactly where it stalls** — that is a *different and
still publishable* reason for the same exclusion, and it is `.memory/01-ladder.md`
finding 14's shape with a number on it. ⚠⚠ **Either way, do NOT reach for
`assume`/`admit`/`external_body` to force it, and do not leave the current
stated reason standing — it is false.**

⚠ **`controls/census.py --mutsub` currently EXITS NON-ZERO UNLESS PROBE 4
FAILS**, so the committed control enforces the wrong verdict. **Fix the control
to match whatever you measure.**

---

## PART A — the rest of the review's findings

**M1 — three rung sources and the HASHED `why` describe the retracted pre-build
world.** ⚠ **This is the new rule-6 step in action, so treat it as the template,
not a chore.**
- `c/kernel.c:13–22` — *"THE HARM IS LOUD HERE … five of six"* against
  `NOTES.md` 0a's measured **6 of 8 silent**, citing the section that retracts
  it. ⚠ **`c/kernel.{c,h}` are MEASUREMENT-hashed: a comment fix costs a
  re-measure.** Decide, do it, and **report the cost** (p19's was 1 m 17 s and
  moved only wall-clock cells).
- `safe_naive.rs:5–25` — the retracted `7.00`/MAC, *"LLVM still cannot remove
  them"*, and **"186 against 111"** when the gate says **179/150**. ⚠ **No
  pipeline yields 111 — find where it came from or strike it.**
- `safe_tuned.rs:17–33` — a *"2×2 grid"* not in `NOTES.md`; `−1.5`/MAC is
  against **R4**, not "this rung".
- `spec.md`'s hashed `why` — *"span **9490** … **2750**; NEITHER SIDE IS
  DEGENERATE"*, against `NOTES.md` 8b's **both degenerate, spans 2 and 3**, and
  `grep -c '9490\|2750' NOTES.md` = **0**. ⚠ **Moves `contract_sha256`.
  Disclose it under rule 6 and say what moved and why.**

**M2 — "four hardening strategies with four asymptotics" is THREE.** R3's
claimed *"one reslice check per row, `O(n)`"* **does not exist in the machine
code**: `safe_tuned`'s conditional-branch multiset is **identical** to
`safe_naive`'s, and the `2n` is **address arithmetic** (`lea` + `add $0x8`).
⚠ **Re-derive it yourself before rewriting** — the review confirmed the
mechanism from both sides, including why the law has two branches on `m` parity.
Sites: `NOTES.md` §1 and §8e, `README.md`, `safe_tuned.rs`, `spec.md`'s `why`.

**M3** — `verus.rs:39` says `14 verified, 1 errors`; it is **`20 verified, 1
errors`**.

**m1** — §8's summary says *"+4.00 flat, WITH TWO MEASURED EXCEPTIONS"* under a
header declaring the **whole-program marginal** convention, where there is
**one**. §8d's second is real under **kernel-exclusive**. **Name the convention
at each.**

**m2** — the committed gate record is **not bit-reproducible**: `check.py p46`
moves 33 stage-3b `-O0`/`whole` marginals by ±7 `Ir`/call (identical shift on
both inputs, so **every `d_ir_d_work` is unchanged**) plus two ASan addresses.
✅ **No `-O3 isolated` figure moves.** ⚠ **Investigate only if cheap; if not,
report it and leave it.** It is not p46-specific.

**Re-gate, and re-publish**: `check.py p46`, then `licence.py --emit` **before**
`synthesize.py`, and `measure.py --check-stale`.

---

## PART B — the queue's exposure, which is now the project's biggest open risk

`TASK_089_REVIEW` **B2** replaced the manager's false `black_box` mechanism with
the true one: **a probe whose kernel SIGNATURE differs from the shipped
kernel's loses the range facts the shipped kernel derives from its input
header.** p46's probe was wrong **in sign** for that reason.

**Ranked exposure, from the probe sources** (`.memory/03-measurement.md`):
**p24 HIGH** (same linear shape — expect the same sign flip), **p26 HIGH**,
**p35 MEDIUM**, **p23 LOW and structurally robust** (its bounds check **IS** its
termination bound), **p28 not exposed**.

⚠ **Nobody has built a shipped-shape kernel for any of the four.** **Do it for
`p24` and `p26`** — the two HIGH rows — as throwaway kernels in `.temp/t92/`:
give them the shipped signature (fixed-capacity scratch, dimensions derived from
an input header) and re-measure. **Report whether the sign holds.**

⚠ **If p24's sign flips, its queue position and its stated finding both change**,
and that is far cheaper to learn now than after a build session.

---

## Constraints

- `.temp/t92/` only. **No `/tmp`.** Keep the generator, delete the artefact.
- **Notes in `.temp/t92/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Durable facts go in your report.
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`.**
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- ⚠ **Grep `~/tools/verus/vstd/std_specs/` specifically** — `CLAUDE.md` now says
  why: a `vstd/<mod>.rs` **trait declaration is not the specification**, and that
  confusion has produced a false *"no spec exists"* claim **twice**.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never `check.py:NNNN`.**

---

⚠ **PROTOCOL rule 2's running count is 261** (259 when this file was written; `TASK_092` added two — the re-measure cost model for rung `.rs` doc comments, and Part B's *"expect the same sign flip"* for `p24`, which is a collapse to byte-identity, with `p26` the more exposed row). **Carry 261 forward.** **Every agent that has contradicted
the manager with a measurement has been right — 259 times, and the last review
refuted two claims the manager had already committed into `.memory/`.** ⚠ **My
prediction record is poor and getting more specific: 0 for 3 on which Verus
obligation stalls, and on p46 I ranked A1 as the likeliest defect and all three
of its limbs survived while the real one was a finding I had listed BELOW it.**
**So treat my ranking in Part B as a prior, not a plan — if `p26` looks more
exposed than `p24` when you get there, say so.** Carry **259** forward.
