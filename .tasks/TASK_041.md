# TASK_041 — p12 owes its review two blockers, three majors, and a rung comment that is wrong

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_040_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md` **finding 12
(p12)**, `.memory/02-bench-rules.md`'s new *"A WRITE bug forces the adversarial
row; it does NOT force the perf row"* section, and `.memory/03-measurement.md`'s
new *"Attribute a surviving panic pad by DECODING its `core::panic::Location`"*
section. **All three are already written by the manager and are the wording to
follow.**

**Your headline mechanism survived and got sharper.** Everything below is already
measured in the report — land it, do not re-derive it.

## The two blockers

1. **Your structural claim is true for p12 and false as published.** `README.md:45-47`
   and `NOTES.md:83-88` say a row on which a write bug fires cannot also be a
   checksum-agreeing row. **The reviewer built one**: zero-initialise `dst`, fold
   `dst[0..DST_CAP]` at *fixed extent*, drop `dlen` from the result, put rejection
   exactly at capacity — checked and unchecked print **identical** checksums at
   every `n_iters`, and ASan still reports the `stack-buffer-overflow`.
   Land the **first half only**: *for a write bug whose guard is the destination's
   own bound, every input on which the guard fires is one on which the unguarded
   rung executes an OOB store* — forced, no read analogue. The second half is a
   **design choice**, and its price is that the perf row **executes UB on every
   call**, usable only in the silent regime (≤ +8 B here).
   Fix the two scope errors with it: the gate's checksum requirement binds the
   **matrix** inputs (`check.py:469` and `measure.py:64` drop `sweep-*`), and on
   band A your R1 exclusion is caused by the **crash**, not the checksum.

2. **§4's mechanism is contradicted by the attribution you declined to do**, and
   the conclusion reached `safe_tuned.rs:24-33` as a source comment. Decoded:
   **neither surviving pad is a destination check.** `dst[..dlen]` contributes
   **zero** pads in all three fold spellings, so "the count stays at 2" is evidence
   the fold **never** contributed one. The survivors are `&buf[off..off+len]` and
   `&w[p..q]`. **The discriminator is not locality** — `dlen ≤ DST_CAP` is bounded
   by a **constant** LLVM sees; `q ≤ len` by a **runtime value**. It does **not**
   transplant p03. Rewrite §4, fix the rung comment, and **ship a pad-decoder**
   in `controls/` (the reviewer's `.temp/r40/pads.py` is the model) so the next
   author does not have to choose between counting and guessing.

## The three majors

3. **The pair interval is not degenerate.** Route A **verifies** — `15/0`, twin
   `18/0`, `R4 ≡ R5 exact` — and is **17.00 / 92.00 cheaper** than the shipped R4.
   On `large` that is 3.5× the `−26.00` headline and **flips its sign**: shipped R3
   is **+66.00 dearer** than the cheapest-found verifying R4. Ship route A as a
   control. **`−26.00` must never appear without the words "against the shipped
   R4"**, and the fourth "safe beats unsafe" claim carries the same qualifier.
4. **"+2 instructions per string" is a static `n_fn` delta wearing a per-string
   label.** Measured **`3.00·K − 1.00`**, exact at four `K` including two your
   inputs never visit. The `identity` pin costs **3.00 Ir per string walked**.
5. **"On the destination" is not the rule.** Your mechanism is confirmed as *where
   the check is* — a safe byte loop with no bulk call in its source lowers to
   `memcpy` — but a cell with the destination **unchecked** and only the *source*
   per-byte checked also loses the lowering. **Both ends must be free.** Ship
   `m1`/`m4` as controls. And sharpen §3d: the `R2 − R4` non-law is entirely
   **R4's `memcpy` size dispatch** — at constant `nacc`, **R2 alone is exactly
   linear at 24.75 Ir per copied byte**.

## The minors

6. **§0's regime boundaries are one step off**: gcc is silent to +8 and fires from
   **+12** (you wrote +8 → +16); clang's loop is destroyed **+12…+48** and
   SIGSEGVs from +64.
7. **`NOTES.md:173-174`** quotes *"within 0.4% of the unsafe rung on wall clock"*
   in the §3a headline. Two fresh sessions straddle zero (+3.89%, −1.05%) with
   `R5 − R4` — which must be 0 — reading **+5.89% / +5.94%**. Delete the clause or
   move it behind §3e's own caveat, which was right.
8. **`c-gcc-h`'s "6 loops"** is 4 real loops plus 2 out-of-line re-entries from the
   guarded block — worth one clause so nobody reads it as a codegen difference.

## Done when

Items 1–8 land; `check.py p12` green; `md5_fn` unchanged; table regenerated;
`--check-stale` clean. `contract_sha256` moves if you touch the hashed block.

## Constraints

No root; no `/tmp` (scratch `.temp/p41/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **Prose and `patterns/p12-strcat-fixed/controls/*.py`
only — nothing in `harness/`, no rung source except `safe_tuned.rs`'s comment
block in item 2.** Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved by
cell.**

The reviewer's scratch is `.temp/r40/` with every control already built and
generated — **reuse rather than rebuild**. Notes to `.temp/p41/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Fifty-three
agents have contradicted the manager and all fifty-three were right. What I am
least sure of is **item 1's replacement wording**: I have written the forced half
as being about a guard that *is* the destination's own bound, but p13's guard
(`strncpy`'s `n`) is a **caller-supplied** bound and p14's is a delimiter, so the
sentence may not reach either. **If it does not generalise as written, say what
does** — five patterns are going to be built on it.
