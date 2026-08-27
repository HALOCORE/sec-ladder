# TASK_109 — review `p42-goto-cleanup`, the 26th pattern

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_104_REPORT.md` **in
full**, then `patterns/p42-goto-cleanup/` (all six rungs, `spec.md`, `NOTES.md`,
`model.py`, `inputs/gen.py`, the five `controls/`), then
`.memory/04-verus.md`'s **affine-token section** and `.memory/06-catalogue.md`'s
`p42` row.

Scratch in **`.temp/r109/`**. **You are the only agent running.**

---

## §A — ⚠⚠ THE HEADLINE. Try to make Verus state leak-freedom.

**The claim: `Tracked<Dealloc>` is AFFINE, not linear, so an R5 that forgets the
error path's `deallocate` verifies `2 verified, 0 errors`** — making `p42` **the
first pattern here whose R5 proof does not cover its own bug class.**

✅ **The control is committed and has both arms** (`controls/affine_leak.rs`):
the leaking proof verifies, the use-after-move arm is rejected. **Re-run it
first.**

⚠⚠ **BUT THE ENGINEER'S OWN SCOPE CAVEAT IS THE ATTACK SURFACE, AND IT SAID SO:
this is about the DEFAULT ENCODING, and a GHOST LEDGER and VERUS'S LINEAR MODE
were NAMED AND NOT BUILT.** **Build at least one of them.**

- **Can a ghost ledger force it?** A `Ghost<Set<addr>>` invariant that the
  function must return empty, or a token count threaded through the
  postcondition. **If a workable encoding exists, the headline weakens from
  *"Verus cannot"* to *"the natural encoding does not, and here is what does"* —
  and that is a BETTER finding, not a worse one.**
- **Does Verus have a linear (non-droppable) mode at the pin?** ⚠ **Grep
  `~/tools/verus/vstd/` and the guide — and remember `std_specs/` is where the
  specs live; a trait declaration is not a specification.** That confusion has
  produced a false *"no spec exists"* claim **twice**.
- ⚠ **If neither works, say so with the runs.** *"I tried these two encodings and
  here is how each failed"* is much stronger than the current *"named and not
  built"*, and it is what the finding needs to stand on.

## §B — ⚠⚠ THE R4 ENDPOINT, WHICH IS p23's LESSON RECURRING ONE PATTERN LATER

The report discloses: **`r4_endptr` is `162 Ir`/call cheaper and admissible in
principle, ITS R5 WAS NEVER BUILT, R4 was held fixed by fiat — and the published
spans OVERLAP.**

⚠ **`p23` shipped with exactly this defect and it took a review to find it**, and
there the cheaper spelling turned out **admissible**, moving the floor `150
Ir`/call. **Settle it here rather than leaving it disclosed.**

1. **Is `r4_endptr` in contract?** Drive `check.py::spelling_matches` on every
   `required`, and check every `forbidden`. ⚠ **Check whether a TAUTOLOGICAL
   CONJUNCT makes an out-of-contract spelling in-contract without changing the
   object code** — that is exactly how p23's floor moved, and the two spellings
   there were `md5_norm`-identical.
2. **If it is admissible, does its R5 close?** The report says it was never
   built. **Build it or say why you could not.**
3. **What does the overlap mean for the published difference?** ⚠ **A difference
   whose endpoints overlap is not a difference. Say so plainly if that is what
   this is.**

## §C — the numbers

- ⚠ **`R1 − R1h = 0.00` on gcc "differing in exactly one branch-target field"** —
  and **probe 2's fourth defect was found here**, where the normaliser discarded
  the self-relative offset and reported the two C rungs as **one rung**.
  **Confirm they are genuinely two rungs**, using `.temp/t104/probe2.py`'s fix or
  a hand disassembly. ⚠ **If the leaking and hardened C kernels really are one
  rung, the C side of this pattern has no boundary.**
- **`−4.00`/`−5.00` on clang, mechanism isolated** (two early exits merged into
  `setne`/`sete`/`or` once both target `cleanup`). ⚠ **Isolate it yourself** —
  RECAP finding 37's companion rule is *a limb claiming a new REASON owes an
  isolation*, and `p23` shipped a mechanism that failed three of them.
- ✅ **`p42` publishes TWO POINTS AND NO RATE** after an out-of-band test
  (residuals 3×–25× in-sample; `−2545 Ir`/call on its own shipped input).
  ⚠ **Check the restraint held everywhere** — `grep` `NOTES.md`, `README.md` and
  `spec.md` for any per-element or per-byte figure that sneaked back in.
  ⚠ **And the mechanism is OPEN with the allocator size class REFUTED by
  isolation — verify the refutation rather than the hypothesis.**
- **The gate's `fired` is a 4-way substring OR and cannot name the sanitizer**,
  so `controls/leak.sh` carries the real check over **88 points**. ⚠ **Does it
  have teeth? Plant a non-leak and confirm it fails.** ⚠ **And does the shipped
  `sanitizer_expect` say anything a stray ASan report would also satisfy?**

## §D — the disclosed self-corrections

**The first gate run FAILED and all four causes were the engineer's own** —
backticked words in a prose `forbidden` entry read as forbidden **spellings**;
`vparse` silently disabling 5c-req on a destructured `Tracked(pt)`; one `ensures`
not load-bearing; three missing `SLB-TRUSTED-ARGUMENT` sections. ⚠ **Verify each
fix is real rather than suppressed** — especially that the `ensures` is now
load-bearing (delete it and show the error) and that **5c-req is actually
RUNNING** on those six conjuncts now, not still silently off.

**`contract_sha256` moved twice, both disclosed with direction.** ⚠ **Verify no
pin CHANGED MEANING** — rule 6 protects against a declaration edited *after*
measuring and **not** against one measurement has since falsified (`p46`).

---

## Constraints

- **`.temp/r109/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `pilot/`, `harness/`, `synthesis/`,
  `results/` or any `patterns/*/` file.** If you must plant, snapshot **by
  bytes**, restore in a `finally:`, and say so.
- ⚠ **`harness/check.py` rewrites `results/gate/` in place.** If you run it,
  `git checkout -- results/gate/` afterwards and **say that you did**. **Do not
  run `harness/measure.py` or `harness/build.py`.**
- ⚠ **`env -u LD_PRELOAD` for hand-run sanitizers; `grep` logs, never `head`.**
- ⚠ **Every probe needs an arm that must fire.** The list of **seven** controls in
  this project that could not have failed is at the end of
  `.memory/03-measurement.md`. **Do not become the eighth.**
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_109_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 379.** ⚠ **`TASK_104` was launched from a
task file that stated the count as BOTH 368 and 324 — the manager edited the
header and left the closing line stale, which is rule 13's shape a third time.
It is reconciled; 379 is correct.** The calls I am least sure of:

1. ⚠⚠ **That "Verus cannot state leak-freedom" survives an actual attempt at a
   better encoding.** The engineer named two and built neither, and **I am
   landing a strong negative claim on that.** **If a ghost ledger works, I want
   to know now, not in the synthesis.**
2. **That `r4_endptr` being left unbuilt is acceptable.** ⚠ **On `p23` the
   equivalent disclosure turned out to hide an admissible spelling that moved the
   floor 150 `Ir`/call and made two spans overlap. p42's spans ALREADY overlap.**
   **I think this is the most likely place for a real defect.**
3. **That `p42` is worth its slot at all.** Its R5 does not cover its bug class,
   its rate is unpublishable, and its gcc rungs differ by `0.00`. ⚠ **Those are
   three negative results and I think they are the point — but if you read it as
   a row that does not earn its place, say so.** **A refusal after the build is
   allowed and has happened before.**

Carry **379** forward, incremented by what you find.
