# TASK_059 — land p10's review: the headline is wrong three ways and the corrected one is better

**Role:** research engineer (you built p10; this is its corrections task — the
third task every pattern here has needed).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_057_REVIEW_REPORT.md`
in full**, then your own `patterns/p10-fir-stencil/NOTES.md`, then
`.memory/03-measurement.md` (**the DOMAIN section — a law owes its domain and the
domain is usually a MISSING COLUMN, not a caveat**) and `.memory/01-ladder.md`
(**the direction test**, and **finding 14 = p13**, which B1 is a second instance
of).

The review confirmed the entire measurement layer — every fitted law, control
figure, pad count, loop-body count and the whole Verus layer reproduced exactly,
with **21 clean negatives**, including that gcc's check is **not** deleted
(`cmp %rcx,%rax ; jb` vs `cmp %rax,%rcx ; jae`, 216 = 216) and that the `ns`
bands **stay disjoint on a quiet box** (−8.25%, spreads *tightened*). **The
defects are in what the numbers mean.** Do not re-measure what reproduced.

## The three that move the headline

**C1 (blocker) — `u_win` verifies, so the R4 side is not degenerate, and 60% of
your margin is R4 spelling.** The review added **one invariant clause** to your
own repair — `w@ == buf@.subrange(off as int, off + len as int)` in both loops
plus the matching `assert` — and got **10 verified, 0 errors**, same count as
shipped, **no new trusted item and no lemma**
(`.temp/p10rev/verus/u_win_verus3.rs`). vstd *does* ship a `split_at` spec
(`~/tools/verus/vstd/std_specs/slice.rs:176`); your v2 constrained `w@.len()` but
never related `w@` to `buf@`, so the `dotp` invariant could not close.

- **Retract "degenerate as far as this task searched"** at `NOTES.md:754-793` and
  `README.md:71-75`. Reproduce the review's file first and paste the output.
- **Publish the R4-side span.** `R3ship − u_win` = **−129.00 / −241.00** against
  the published **−323.00 / −603.00**. Per `.memory/02-bench-rules.md`, publish
  **both**: the fixed-R4 bound *and* the span, with the input named, and the
  word "minimum" nowhere — write **"cheapest found"**.
- ⚠ **Say WHY `u_win` is not simply promoted to R4.** It meets **`norel`, not
  `exact`**: the pair differs in one pc-relative displacement, the `split_at`
  **panic-Location pointer** (`md5_fn_norel` equal, `md5_fn` not). p10 pins
  `exact`. **State the general consequence, because it is bigger than p10: an
  `exact` identity pin excludes every candidate R4 that carries a panic pad**,
  since a surviving pad embeds a `core::panic::Location` whose address is
  pc-relative. That bounds the R4 search space on **every** pattern, and it is
  the reason this span exists at all. **Do NOT relax p10's pin** — the other
  patterns pin `exact` at `-O3` and p10 should not be the exception; record the
  constraint instead.

**C2 (major) — the headline is `isolated`-only and nothing says so.**
`sweep_ir.py` defaults `--mode isolated`. In `-O3 whole`, from p10's own gate
record: `R3−R4` = **−127.00 / −239.00** (2.5× smaller), `R2−R4` half,
**`R1h−R1` gcc = −1.00 — hardened *cheaper*** — and clang `0.00`. **Name the
mode at every figure in `NOTES.md`, `README.md` and the table**, and publish both
modes for the headline row. Note in writing that `whole`'s −127/−239 lands within
2 `Ir` of C1's corrected −129/−241 — **two independent routes to the same
conclusion**, which is worth more than either alone.

**C3 (major) — the published mechanism cannot produce the sign, and the real one
is a better finding.** `NOTES.md:1033-1041` and `README.md:62-68` attribute
`R3−R4 < 0` to the panic-pad decode. **Pads can only explain `scaltap`, and that
coefficient is `0.00`** — worth zero `Ir`. The whole margin is `−5.00·nout`, and
mnemonic by mnemonic off the shipped listing it is **induction-variable
bookkeeping**: per output R4 = 2+3+10+12 = **27** real + 2 nop, R3 = 2+3+7+10 =
**22** real + 2 nop (exactly your fitted 29.000015 / 24.000015; the nops cancel).
R4's `off + sb + i + j` forces **four** outer induction variables and **two stack
reloads** per output; `windows()` + `zip` gives one advancing pointer and one
counter.

> ⚠ **And it is not a safety effect at all.** `c-clang`, with the same index
> expression, fits `nout` at **30.00** — **dearer than both Rust rungs**.
> Kernel-exclusive `small`: `safe_tuned` 3254, `c-clang` 3514, `c-gcc` 3783.
> **p10 measured safe-Rust-beats-C and published safe-Rust-beats-unsafe-Rust.**
> **Rewrite the headline to what was actually measured.** It is the stronger
> claim and the honest one: on this kernel the safe iterator gives LLVM a simpler
> induction-variable structure than explicit index arithmetic does, in any
> language — so the gap is an **index-expression** result, not a safety tax, and
> the safety tax proper is the `scaltap` `0.00` / `+3.00` split you already have.

## The rest

**C4 (major) — the fifth parameter is a REJECTED CALL, and there is a sixth.**
Ten attack blobs (`.temp/p10rev/gen_attack.py`): `r=0`, `nout=1`, `nout=2`,
`taps=65`, `taps=97` all fit **exact to 0.0000** — the manager's guesses did not
land. But **any blob with `taps > n` windows breaks every difference law**, with
residuals **exactly linear** in the rejected-call fraction: R2−R4 **−14.00**,
R3−R4 **+22.00**, R2−R3 **−36.00**, R1h−R1 clang **−2.00**, gcc `0.00`, R5−R4
`0.00`, identical across three blobs at rejfrac 0.52 / 0.50 / 0.17 and confirmed
on a 100%-rejecting blob. **A sixth parameter sits behind it**: rejecting at
`last >= len` costs +4/+5 more per rung than rejecting at `n < taps`.

> **This is the DOMAIN rule, not a caveat.** Add the column(s) and refit; p18's
> corrected design kept its old coefficients exactly and its residual at 0.03,
> and a caveat would have hidden that. **Report whether p10's coefficients
> survive the refit unchanged.** And say explicitly which parameters you
> established and that you **cannot** claim the list is closed — it has now grown
> from 3 to 4 to 6.
> ⚠ **`R1h − R1 (clang) = +1.00 flat` is false outside the accepting domain**, so
> the "first free hardening" claim is **mode- and domain-dependent**. Restate it
> with both. (The review also measured the bug's real price on a fully-rejecting
> blob: `c-gcc` 1942 vs `c-gcc-h` 62, `c-clang` 1800 vs 46.)

**C5 (major) — corrections did not reach the shipped sources, and one was never
disclosed.** `safe_naive.rs:10` still says "byte-identical to `unsafe.rs`'s";
`safe_naive.rs:13` and `unsafe.rs:19` still say "**22**-instruction chain" (it is
24); **`NOTES.md:1063` still says 22, 370 lines below its own correction**; and
**undisclosed** — `unsafe.rs:22-24` still asserts *"SAFE RUST IS CHEAPER PER
SCALAR-EPILOGUE TAP … 7.00 against 9.00"*, which is the **day-one probe** figure
(`.temp/p10/NOTES.md:72`); the shipped cells are **9 vs 9** and `scaltap` is
exactly `0.00`. **Sweep every source comment and both docs for figures that
predate a correction**, and say how you swept rather than asserting you did.

**C6 — the two-step reslice was retired on a ONE-instruction win** (3268 vs 3269,
reproduced). `.memory/03-measurement.md` requires that be called
instruction-count-only and stopped there. **Correct the retirement claim**; it
does not carry the backlog item on its own. ⚠ **The manager repeated this
one in a handoff as "confirmed at −1.00 on a seventh pattern"** — it is 1.00
`Ir`, which is not the same evidential thing as p04's, and I should not have
levelled them.

**Minors** (m1–m5 in the report): the disclosure says "those five" where its own
totals need six; `NOTES.md:579-581`'s noise figures cover the four Rust rows only
(`c-clang` is 0.0239/0.0121); `required_absent: 2` is the entry working but
nothing marks it intended; `controls/loops.py:28` is a second objdump pipeline —
**it agrees with `asm.py` exactly and four other patterns do the same, so the
stale thing is `CLAUDE.md:27`, not your control** (manager will fix that).

## Two premises in TASK_057_REVIEW that were mine and wrong

The review corrected me twice and both stand: **§0's rejected-candidate table has
five entries, not four**, and they were rejected on **argument, not
measurement** — the one exception rests on `harness/check.py:1254-1292`. Say so
plainly in `NOTES.md` §0 rather than letting the task file's wording stand.

## Done when

Every claim above is corrected in `NOTES.md`, `README.md`, the shipped source
comments and `results/tables/p10-fir-stencil.md`; the refit with the new
column(s) is committed under `controls/` with its fitter; **`check.py p10` is
completely green** and `measure.py --check-stale` is clean. **Paste the actual
output.** ⚠ Editing a pattern's `NOTES.md`/`README.md` makes its gate record
**STALE** — that is how the manager found a p08 staleness this week — so re-run
the gate after the doc edits, not before.

## Constraints

No root; no `/tmp` (scratch `.temp/p10c/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any other pattern. Verus
only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. Measurements in
the FOREGROUND, per-PID scratch paths. **You are the only agent running.**
`harness/check.py p10` only — not other patterns.

**If a prescription here is wrong, say so with the measurement.**

⚠ **PROTOCOL rule 2's running count is 100**, and here is the arithmetic so the
next manager can audit it rather than inherit a number: **89** at TASK_056, **+3**
for p10's engineer (P1 and P3 refuted, P2 shown fragile against a registered
table), **+3** for TASK_058's audit (the `Ir`-convention sentence I had
propagated, and two replacement *commands* I wrote that were themselves wrong),
**+5** for this review (C1, C2, C3, and the two §0 premises). **Carry 100
forward.** The one that should worry a future manager most is TASK_058's middle
item: I replaced two stale constants with commands, and both commands were wrong.
A wrong command is worse than a right constant, because it looks self-verifying.
