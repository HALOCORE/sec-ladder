# TASK_040_REVIEW — p12 says a write bug cannot have a benign perf row. That constrains five future patterns.

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_040.md` (the spec), then
**`patterns/p12-strcat-fixed/NOTES.md` in full**, then its `spec.md`, `model.py`,
`inputs/gen.py`, `controls/`, and `.memory/01-ladder.md` finding 2 (p02 — the
retraction p12's headline mechanism echoes) and the "R4 is defined by permission"
paragraph.

p12 is the eleventh pattern: gate `PASS` on its first complete run, R5 15/0, R4 ≡
R5 `exact`, TCB 10/5 matching the gate's own count, **unreviewed**.

## Attack the structural claim first — it is the one with reach

p12 says: **the gate requires every cell including R1 to match `model.py` on every
non-adversarial input; R1 omits the capacity check; therefore any window where the
check fires makes R1 diverge; therefore a write bug has no benign row on which the
bug fires, perf rows are forced to 100% accept, and they are rank-deficient for
the "per what?" axis by construction.**

If that is right it constrains **p13, p14, p23, p24 and p25** before they are
written, and it belongs in `.memory/02-bench-rules.md`. If it is wrong — or if it
is a *design* choice dressed as a constraint — five future patterns get a worse
shape than they need.

- **Is it really forced?** Could a window be built where the check fires and R1
  still agrees — e.g. by making the truncated tail unreachable in the fold, or by
  folding `dlen` in a way both rungs share? Try to build the row p12 says cannot
  exist.
- **Does the rank-deficiency actually follow?** With 100% accept, "per string" and
  "per accepted string" are the same regressor — but that is a statement about
  *those two* regressors, not about the whole design. Check what the pooled rank
  5/5 claim rests on and whether band N's 2/5 is what makes it work.

## Then the headline mechanism

**"A per-byte bounds check on the destination blocks the bulk-copy lowering; moving
it to once per string recovers it at zero `unsafe`."** Four cells differing in one
thing is the right shape of control — verify it is really one thing. In
particular: is the recovery due to *where the check is*, or to `copy_from_slice`
being a different call that carries its own bound? Those are different sentences
and only the first supports the finding as written.

And check the consequence: **`R2 − R4` has no per-byte law and p12 publishes
none.** Confirm the max residual really precludes one (548 of ~2400 is quoted)
rather than the fit being mis-specified.

## The rest, in order

1. **The sign result.** `−4.00` Ir/string under gcc, `+2.00` under clang and
   rustc — a *middle-end* property. Re-derive both from the listing. p03's
   result had the opposite polarity, so this either extends it or contradicts it.
2. **Out-of-sample prediction**: `−125.00 / +57.00 / −26.00` predicted and
   measured, 3.5× outside the band. That is the strongest form of evidence this
   project accepts; confirm it independently.
3. **"The shipped safe rung beats the shipped unsafe rung on `large`" (−26.00).**
   Fourth claimed instance of R4-by-permission. Check the pair is matched and that
   the R4 side really cannot move — p12 calls its pair interval **degenerate on
   the basis of an inference**, not a build (route A "= 0 instructions" was never
   built). **Build it**, or say what it would cost.
4. **The observability table** (+1…+8 silent on both; +16…+48 gcc canary / clang
   corrupts `main`'s locals; +64…+128 gcc canary / clang SIGSEGV). This is the
   first behavioural C-vs-C split here. Reproduce it, and check the claim that
   `-fno-stack-protector` is *unnecessary* — i.e. that the silent row genuinely
   exists at shipped flags.
5. **The two poisoned sweep blobs.** Clang's overflowing R1 destroyed the driver's
   loop state, so its checksum is identical at `n_iters` 1…1000 and the marginal
   is 0 by construction. `sweep_ir.py::usable()` now rejects a 0 marginal. **Is
   rejecting it enough, or does an overflowing R1 poison every measurement it
   appears in?** This is a gate-adjacent question and I want a view.
6. **Verus**: 15/0, twin 18, four mutants failing four different ways, and `p1`
   failing on the **write bound** rather than the postcondition. Recount the
   obligations per item. And check `n1_uchar_sum` — a capacity check in
   `unsigned char` that reads correctly and aborts identically to no check at all.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. And if the structural claim holds, **say so plainly and in
general terms** — "for a bug that writes, no input on which the bug fires can also
be a checksum-agreeing row" is a sentence that should govern five patterns, and
hedging it would be its own failure.

## Constraints

No root; no `/tmp` — scratch `.temp/r40/`, delete binaries and blobs when done.
**No `git add`/`git commit`** — read-only git. Do not edit `pilot/`, `.memory/`,
or anything under `patterns/`. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &` background jobs**; no self-matching `pgrep` wait-loops.
**Measurements in the FOREGROUND, interleaved by cell**; subtract `t(n_iters=1)`
before any wall-clock ratio (±9-point error bar); `harness/measure.py
--check-stale` before quoting a record.

Notes to `.temp/r40/NOTES.md`. Report in PROTOCOL's format, severity-ranked, with
file:line and a concrete failure scenario per finding.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Fifty-two agents have and all fifty-two were right — p12's own engineer
refuted both premises I gave it and corrected my claim that it shipped this
project's first write precondition. I have no independent view of its numbers.
