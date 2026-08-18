# TASK_025_REVIEW — attack TASK_024, and the manager's landing of it

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_024.md` (the spec),
then `patterns/p16-tlv-walk/NOTES.md` **§10a, §10a.1 and §10a.2 in full** (the
deliverable), then `.memory/01-ladder.md`'s p16 entry — specifically the
`⚠ CONTESTED — PROVISIONAL` block, which records this disagreement without
picking a side. Picking the side is what this review is for.

## Why this review is not optional

Two of PROTOCOL's rules bite at once. Rule 1: every review so far has found real
defects in work that reported success, four of them past a fully green gate.
Rule 3: **the engineer died to an API error before reporting, and the manager
reconstructed and committed its landing** — so a landing the manager finished is
in the tree, and a different agent has to attack it. That is you.

There is a third reason. TASK_024's engineer was sent to land a correction and
instead **refuted the correction**, in a task whose own spec invited exactly
that. The refutation is now p16's headline. Nobody has checked it.

## What is being claimed

p16's `NOTES.md` §10a.2, `README.md`, and the hashed `spec.md` `idiom.why` now
assert, on TASK_024's measurements:

- **A.** `5 + 3/K` is not a law: `chunks_exact(4)` = 6.50000 and `(8)` = 6.62500
  Ir/folded byte, both *dearer* than the shipped 5.75000, so the family is not
  monotone in `K`; the mechanism is `try_into::<[u8;K]>()` letting LLVM fold `K`
  byte loads into one word load plus extraction at `K ≤ 8`, and giving up at
  `K ≥ 16` where the body is `5K + 3`.
- **B.** The **matched-spelling null**: safe-minus-unsafe per-byte slope is
  **exactly 0.00000** at all six folds, in three residue-matched bands, because
  the reslice (R3) and the `get_unchecked` (R4) both sit *outside* the fold loop
  — so the chunk body is the same machine code on both sides (identical
  instruction counts 26/53/83/163/323, identical mnemonic sequence at K 16/32/64).
- **C.** Therefore **−0.5625 Ir/byte is a cross-spelling codegen difference, not
  a safety cost**, and p16's published "zero per byte" is not sign-wrong but
  *spelling-conditional* and exactly true at matched spelling.
- **D.** Twelve probes, one exact-string substitution each from shipped
  `safe_tuned.rs` / `unsafe.rs`, are **in contract** ("by the gate's own
  matcher": req1 = req2 = True, forb1 = forb2 = False), **95/95 equivalent** in
  stdout and exit status to the shipped R4, and the six unsafe ones **Miri-clean**.
- **E.** TASK_023_REVIEW's `51·nrec − 5` / `48·nrec − 5` is **domained wrong** —
  fixed-`vlen` slices (124, 126), not residue classes; predicts 475 at `large`
  against a measured 2365.
- **F.** The unroll factor is **not** pinned, on the direction test, and what is
  pinned instead is a reporting rule: *a per-byte rate is quoted with its fold
  named; a difference of rates only between rungs that fold the same way.*

## Attacks I want run, in this order

The first four are where I think this is most likely to be wrong. Run them even
if an earlier one lands.

1. **The unsafe probes may not be admissible R4s, by TASK_024's own argument.**
   §10a.1 disqualifies `r4_hdr` as a p16 rung because vstd cannot verify
   `read_unaligned` and this pattern's `identity` pin demands R5 ≡ R4 exactly, so
   it would need a fourth trusted item. **`u_c32` is an unsafe rung too.** Does
   Verus at the pinned vstd verify a `chunks_exact` + `try_into::<[u8;K]>()` fold
   inside the R5 twin, at all, let alone to R5 ≡ R4 byte-identity at -O3? Nobody
   ran it. If it does not, the same argument disqualifies `u_c32`, claim B's
   unsafe column has no rung behind it, and "at matched spelling the unsafe rung
   is cheaper" — statement 2 of §10a.2, the sentence that keeps claim C honest —
   loses its footing. `./verus_run.py`; the R5 cell and the identity pin are the
   evidence, not an argument about them.

2. **The slopes are two-point differences, and this file's own trap list forbids
   that.** *"Residues bite at whatever width the codegen chose… Sweep two full
   cycles; never sample two points."* Every number in claim B's table is a
   **binary-differenced marginal between two blobs**. Three bands is three pairs,
   not a sweep. Re-derive at least one slope from a genuine sweep — enough
   consecutive lengths to cover two full cycles of whatever modulus that fold has
   — and say whether 0.00000 survives, and to how many decimals. If the six
   spellings need six different moduli, that is itself the finding.

3. **"In contract by the gate's own matcher" is weaker than "in contract", and
   the gap is two `required` entries.** p16 declares four: the two comparison
   tokens (which `spelling_matches` checks), plus *"the tag byte is folded, and
   folded BEFORE the fit test"* and *"nrec is folded into the result"* (which, as
   far as I can tell, nothing machine-checks). Do the twelve probes honour those
   two? Check the *chunked* ones specifically — a `chunks_exact` fold restructures
   the value loop, and the ordering constraint is about what happens around it.
   This project has twice measured a spelling its own `spec.md` forbade and
   published it as the pattern's number. Do not let it be three.

4. **The mnemonic-identity claim is asserted at K 16/32/64 and conspicuously not
   at K 4/8**, where only the instruction *count* is given (26, 53). Disassemble
   and say whether the K=4 and K=8 bodies are mnemonic-identical safe-vs-unsafe.
   If they are not, "the chunk body is the same machine code on both sides" is
   over-stated at exactly the two spellings that carry claim A.

5. **Band A's `+0.00469`** is explained as the driver's `println!` digit-count
   term and dismissed because it is "the same offset on all ten binaries". That
   is an explanation, not a control. Build the control — vary the digit count
   without varying the fold — or report that the offset is unexplained.

6. **Claim E's arithmetic.** Re-measure the two laws at `vlen` 56 and 88 and at
   `large`. Confirm or refute 31 / 115 / 2365 and the 5× miss. Cheap, and it
   decides whether a published law is mislabelled or wrong.

7. **The direction test, applied to claim F.** TASK_024 refuses to pin the unroll
   factor because excluding the chunked fold would shrink the admissible class
   *and* raise p16's published figure from −199 to +19. Is that reasoning sound,
   or is the direction test being used to launder a number nobody likes? And is
   the replacement — a *reporting* rule — enforceable by anything, or is it
   another sentence in prose that a `grep` cannot settle? Note that this project
   has already measured what happens to load-bearing prose: p05's declaration was
   right twice and lost twice because it was invisible.

8. **The reproduction gap.** §10a.2's twelve probes and every number in it come
   from `.temp/p24/*.py`, which is gitignored scratch. `controls/*.py` is inside
   `source_sha256` precisely so a control's reproduction path ships. Say what
   exactly needs to move into `patterns/p16-tlv-walk/controls/` for §10a.2 to be
   re-derivable from the committed tree, and whether the scripts as written would
   run there. **Do not move them** — that is the next engineer's task.

## The question behind all of it

TASK_024 answered *"is accept-K-dependence a finding or a surrender?"* with
**finding**, on the ground that naming the fold makes every rate publishable.
The competing reading is that a per-byte rate whose value is a free parameter of
an unpinned spelling is **not a property of the kernel at all**, and this project
should stop publishing per-byte rates — which would be a larger result than any
pattern's number, and would reach p16's 5.7500, p17's 10.0000/5.7500, p05's
1.375000 and finding 11's 4.25 all at once. **Say which reading the measurements
support.** If it is the second, say so plainly; it invalidates four published
numbers and I would rather learn it from you than from a reader.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. For every attack above that does **not** land, say so explicitly
and give the evidence, so the next agent does not re-run it. A review that says
"looks good" without having tried to break something is a failed review.

## Constraints

No root; no `/tmp` — scratch under `.temp/r25/`, and per `.memory/00-environment.md`
constraint 6 **delete your binaries and blobs when you are done, keep your
scripts and notes**. **No `git add` / `git commit`** — read-only git only. Do not
edit `pilot/` or `.memory/`; report durable facts and the manager lands them. You
may edit nothing in `patterns/` either — you report, you do not fix. Verus only
via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill.

Keep running notes in `.temp/r25/NOTES.md` as you go, so you can be resumed if
you die to a transient API error — the last two agents on this arc both did.

Report in PROTOCOL's format (`## Did / ## Evidence / ## Problems / ## Unsure /
not done / ## Memory updates`), severity-ranked, with file:line and a concrete
failure scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do here.** Thirty-one agents have done it and all thirty-one were right. The last
one was sent to land a correction and refuted it instead — and I committed its
refutation as p16's headline without anyone checking it. That is the specific
thing you are here to fix.
