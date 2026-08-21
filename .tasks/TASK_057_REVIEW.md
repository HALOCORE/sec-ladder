# TASK_057_REVIEW — p10, whose headline says safe Rust is CHEAPER than unsafe

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
**`.tasks/TASK_057.md`** — the build spec, including the **§2 prediction table
registered in commit `97286d2`, which precedes every p10 measurement** — then
**`patterns/p10-fir-stencil/NOTES.md` in full**, then `.memory/03-measurement.md`
(the DOMAIN section, additivity extrapolation, post-drop rank, the two `Ir`
conventions at `:479`/`:508`, the layout/`ns` sections) and `.memory/04-verus.md`.

p10 is **gate-green and independently re-run by the manager** (`check.py p10` →
`PASS`, `34 records, 0 STALE`). **PROTOCOL rule 9 means nothing from p10 is in
`.memory/` yet** — it goes in only after you land. Four `.memory/` candidates are
listed at the end of the engineer's report; **they are what you are gatekeeping.**

⚠ **PROTOCOL rule 3.** The §2 prediction table and the weighted-FIR
recommendation are **the manager's**. All three predictions were scored **FALSE,
TRUE-but-fragile, FALSE**. That is the outcome I asked for, so **do not treat the
engineer's refutation of me as the thing to check** — check the *replacement*,
which is the engineer's own and has had no adversary.

## The attacks I most want run, in priority order

**A1 — the headline sign. `R3 − R4 = −323.00 / −603.00 Ir/call`: safe Rust
CHEAPER than unsafe, by a lot.** This project has published a sign-wrong headline
twice (p06's `Ir` column, p13's whole headline) and both times a review caught
it. The stated support is a **panic-pad count**: R2 = 10 pads, R3 = **2** (both
the window reslice, none from the tap loop), R4 = 0 — from which the engineer
concludes `scaltap = 0.00` for R3.

> **Pads explain why R3 pays nothing per tap. They do not explain why R3 pays
> NEGATIVE 5.00 per output against R4.** PROTOCOL rule 11: *"it vanished" is not
> a mechanism, and a finding without one is the finding a reader disbelieves.*
> **Get the mechanism, mnemonic by mnemonic, or report that there isn't one.**
> Specifically: what is R4's `get_unchecked` path doing that R3's `windows`
> iterator is not? Is R4 dearer because `get_unchecked` defeats a loop
> transformation the iterator enables? **And check the convention** — `−323` is
> in whose counts, kernel-exclusive or marginal? p08 diverges 13× between them.

**A2 — is the hardened C rung actually hardened?** `c-gcc-h − c-gcc = 0.00`, with
**every fitted coefficient exactly zero**, published as *"the first free
hardening in the project"*.

> **The alternative explanation is that the compiler proved the check redundant
> and deleted it**, in which case R1h is not a hardened rung and the headline is
> "no hardening", not "free hardening". The bug is `last > len` versus
> `last >= len` — **one character** — so the two objects should differ by a
> `setcc`/`jcc`, and if they do not, say what the object actually contains.
> Disassemble both. The adversarial rows say `fencepost` reaches ASan in R1 and
> is rejected by R1h, so *something* differs; establish **what**, and whether the
> zero is a real price or a deleted check. clang's `+1.00` is attributed to a
> `jmp` from tail-merging `return 0` — verify that too, because *"the extra
> instruction is not a check"* is exactly the claim that makes the cost free.

**A3 — the `ns` populations were taken on a contended box, and that is the
manager's fault.** The engineer flagged it: other agents were active during the
run. **I ran a read-only doc audit concurrently and made my own tool calls, and
I decided that was safe.** The published claim is `safe_tuned` **207.55–215.39**
against `unsafe` **229.38–233.59** — **disjoint bands, −8.4% medians**, which is
A1's headline in wall clock.

> **Re-take both populations with nothing else running** and report whether the
> bands stay disjoint. Spreads of 1.6–3.8% against a gap of 8.4% is a wide
> margin, so I expect it survives — **but that is a prediction, not a result**,
> and `.memory/03-measurement.md` says the `ns` floor is a *session* property.
> If it does not survive, the `ns` half of p10's headline is withdrawn.

**A4 — the law's parameter list is open, and the engineer says so.** `R2 − R4 =
65 + 41.00·nout + 3.00·scaltap − 7.00·novecout`, `max|resid| 0.0000` over 26
blobs. But **`novecout` was found only because band `h` refused the model** — the
three-parameter version fitted `r` and `o` at 0.0000 and missed `h` by 15.6 `Ir`.

> **That is p18's lesson repeating**: the domain was named as one parameter and
> measured as two. **Go looking for the fifth.** Construct a blob that turns on
> something none of the 26 fit blobs varies — an `n` that leaves a different
> epilogue remainder, a `taps` value straddling the `mod 8` period, a degenerate
> `r = 0` or `taps > n`. **If you break the law, that is the finding.** And check
> the engineer's own disclosure that band `e` is **rank 4 of 4, inside the fit
> set's row space, so it cannot fail from linearity alone** — the report says so
> plainly; confirm it, and say whether the 40 committed predictions therefore
> prove anything.

**A5 — P2 is true at the shipped spelling and false at another, and the
direction test governs that.** A day-one probe with a **different guard
structure** measured R3 at 7.00 against R4's 9.00 per scalar tap — **not flat**.
The shipped spelling gives `scaltap = 0.00` exactly, which is what makes P2 true.

> **When was the shipped R3 spelling chosen, before or after that probe?** If
> after, a declaration edit moved a published figure in the flattering direction
> and `.memory/01-ladder.md`'s direction test applies. The engineer disclosed the
> probe rather than burying it, which is the behaviour the project wants — **so
> this is not an accusation, it is the check the disclosure exists to enable.**
> Use the `slb-contract` sha256 recorded in `NOTES.md` before the build
> (PROTOCOL definition-of-done 6) and say whether it moved.

## Also in scope

- **`global size_of usize == 8;`** — the engineer's new Verus fact: Verus treats
  `usize` as architecture-independent, so `2*r+1` from four header bytes is
  `possible arithmetic underflow/overflow` without it, and `assert(r <=
  0xffff_ffff)` does not help. **Claimed to carry no obligation and no TCB —
  verify both.** It is an assumption about the target: is it a **fiat** the gate
  should see, and would the proof be unsound on a 32-bit target? p07 dodged the
  identical obligation via `u64`; check that p10 really cannot.
- **The two overclaims the engineer caught and corrected before shipping**
  ("byte-identical" → mnemonic-identical; a 22-instruction chain that is 24 in
  the shipped cell). **Check the corrections are complete everywhere**, not just
  at the headline — that is the exact failure mode PROTOCOL rule 9 exists for.
- **`u_win` (the R4-side lever, −194/−362) reported as "degenerate as far as this
  task searched"**, with `precondition not satisfied` ×2 on `buf_get_unchecked`
  and one failed repair round. It is **not** `is not supported`, so it may be
  admissible with more budget. **Try to close it or confirm it is stuck** — the
  R4-side span is a standing project-wide gap (p01, p08, p18 all owe one).
- **No gcc level law** (best `max|resid| 45.3` across five designs), published as
  a clean negative while gcc's *difference* law is exact at 0.00. Is the negative
  honest, or is there a three-regime design nobody tried?
- **Two `required` entries pin nothing** (`required_absent: 2` in the idiom
  audit). Say whether that is a defect or a scoped entry doing its job.
- **The catalogue class is reported UPHELD** — the second upheld of six settled.
  Check `NOTES.md` §0's four rejected candidates actually were rejected on
  measurements, not on argument.

## Clean negatives are wanted

PROTOCOL rule 6: **a named attack that did not land is worth as much as a
finding.** p06's review returned fourteen and p14's seventeen; that is the bar.
List every attack you ran with its outcome.

## Constraints

No root; no `/tmp` (scratch `.temp/p10rev/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under
`patterns/` — **you are a reviewer, you report and do not fix.** You may write
probe sources, logs and re-measurements under `.temp/p10rev/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell**, per-PID scratch paths. ⚠ **You may re-run `harness/check.py p10`** —
it rewrites only p10's gate JSON and the manager has a clean baseline — but **do
not run it on any other pattern.** **You are the only agent running; the box is
quiet, which is what A3 needs.**

**Write `.tasks/TASK_057_REVIEW_REPORT.md` before you finish** (PROTOCOL rule 10
— a review's citations once pointed at a file that was never created), then
return the same content in the report format.

Rank findings `blocker` · `major` · `minor`, with file:line and a concrete
failure scenario. **Do not pad — 3 real blockers beat 20 nitpicks.**

**If a premise here is wrong, say so with the measurement.** **Ninety-three**
agents have contradicted the manager and all ninety-three were right — p10's
engineer alone did it three times in one task, by killing all three of my
registered predictions.
