# TASK_064_REVIEW — p47, where a denominator was changed to make a gate stage pass

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_064.md`, then **`patterns/p47-ct-compare/NOTES.md` in full**, then
`.memory/03-measurement.md` (the `rep`-string counting at `:411`, the `div`
pricing at `:434`, "name the routine" at `:551`, the two `Ir` conventions, the
INLINE-MODE rule, the DOMAIN rule) and `.memory/01-ladder.md` (**the direction
test** — A1 is exactly its shape).

p47 is **gate-green** (`PASS`, 0 failures, complete run, 38 records 0 STALE, R5
**12/0 first run with no lemma**, `R4 ≡ R5` `exact` at O3 / `norel` at O0,
TCB 3, Miri 7/7). **PROTOCOL rule 9 holds everything out of `.memory/` until you
land**; four candidates are named at the end of the engineer's report.

⚠ **The engineer corrected ten written claims with measurements, including the
catalogue's own bug class.** That is the behaviour this project wants, and it
means **the replacement claims are the ones with no adversary.** Attack those,
not the ones already dead.

## A1 — a MEASUREMENT DEFINITION was changed to make a gate stage pass. Blocker if it is wrong.

The engineer reports that `work_per_call` denominated in **window bytes** made
the vectorised rungs read 0.189–0.245 `Ir`/byte and **fail `collapse-ir` on 10 of
16 `-O3` cells while doing the whole job** — and fixed it by denominating in
**byte comparisons** (0.413) instead, on the ground that one work unit consumes
two window bytes.

> **This is the direction test's exact shape**: a definitional change, made after
> a measurement, that moves a number across a threshold in the direction that
> makes the pattern pass. **It may well be right** — a denominator that counts
> each byte once when the kernel compares two is arguably just wrong — **but it
> has had no adversary, and the engineer chose it over the alternative they
> name (`min_ir_per_work`), which would have been a visible declaration edit.**
>
> **Establish which it is.** Is "byte comparisons" the honest unit for *this*
> kernel, and would it have been chosen the same way if the gate had passed?
> Check whether any *other* pattern's `work_per_call` counts a unit that
> consumes more than one input byte, and what it does. **If p47 is the only one
> and the change is local to it, say whether the anti-collapse threshold is now
> load-bearing on a per-pattern definition — because that would make
> `collapse-ir` a check each pattern can define its way past.**

## A2 — the punchline, on the binary. Verify it or kill it.

`m_leak` = `verus.rs` + an early exit + one ghost lemma → **`14 verified, 0
errors`**, `kernel`'s own obligation count **unchanged at 3**, identical
checksums on all 8 cells × 2 opts × 2 modes, and **+7088.000 `Ir` between `k=0`
and `k=127`**.

> **This is the whole pattern and it must be exactly right.** Re-run it. Then
> attack the framing: is `m_leak` genuinely *the same program modulo the leak*,
> or does the added ghost lemma do work that changes what was proved? **Does the
> shipped `verus.rs` prove anything that `m_leak` does not?** If the answer is
> "no", the sentence *"the proof certifies a leaking kernel"* is exactly right
> and this is the strongest negative result on the project. If it proves
> something weaker, say what.

## A3 — a strong negative claim from a finite search

*"The optimiser never reintroduces a branch"* — 5 accumulate spellings × {gcc
13.3, clang 22.1} × {`-O1 -O2 -O3 -Os -Oz`}, plus rustc at 5 opt levels, inlined
and not, fixed and runtime length. **This overturns the catalogue's bug class**,
which is a big claim to rest on one engineer's search.

> **Try to break it.** The obvious gaps: **LTO**, **PGO / profile-guided
> specialisation** (the classic case where a compiler *does* specialise a hot
> path), `-march=native` and wider vector ISAs, `__builtin_expect`, and a caller
> that already branches on the result. **If you cannot break it either, that is a
> much stronger clean negative than the delivery's** — say so and name what you
> tried.

## Also in scope

- **`main`'s Verus obligation term is 5, not 4** — the engineer says the
  off-by-one *"ten patterns record for the identical driver"* does not transfer.
  **One of those two statements is wrong about ten patterns.** Recount on at
  least two other patterns and say which.
- **`Ir(k)` constant is NECESSARY, NOT SUFFICIENT** for constant time — the
  engineer says so in `NOTES.md` §14 and backs the rest off the disassembly
  (branchless, data-independent addresses). **Is the published claim scoped to
  what was measured?** A pattern whose headline overstates its own metric is the
  p10 failure.
- **clang rewrites `memcmp(…)==0` → `bcmp`, the same symbol rustc emits for
  `a == b`.** Verify, and check the consequence is stated: `c-clang` vs
  `safe_naive` is a **library** result, not a language one.
- **The R4-side search** — six levers, each measured *and* run through Verus,
  concluding nothing moves it down at `identity: exact`. **This is the first
  pattern to do that properly.** Spot-check two: `u_win` (−24.000, `norel` not
  `exact`) and `u_winu` (`exact`, but needs a fourth trusted item). Is the
  fourth item really forced?
- **The wall-clock claim**: `P(R3>R4) = 1.000` over 576 cross pairs, median
  +21.62%, `P = 1.000` in all four mode-matched partitions. Check the population
  and the partitioning; two `ns` rows on this project are withdrawn for less.
- **`volatile` costs 6.75× / 9.68× for nothing** — verify, since it inverts the
  standard advice and will be quoted.
- The engineer **deleted `.temp/p14/clay`** after discovering p27's control
  writes into p14's scratch directory. **The manager has repointed p27's control
  and re-run its gate.** Confirm no p14 figure depended on what was deleted.

## Clean negatives are wanted

PROTOCOL rule 6. p10's review returned twenty-one, p27's twenty-eight. **List
every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch `.temp/p47rev/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under
`patterns/`. Probes and logs under `.temp/p47rev/`, plus your report file.
⚠ **Use your own scratch subdirectory** — the defect above is exactly what
happens when two things share one. Verus only via `./verus_run.py`;
`~/tools/verus/vstd/` for vstd source. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. **You may re-run
`harness/check.py p47`** — not any other pattern. **You are the only agent
running.**

**Write `.tasks/TASK_064_REVIEW_REPORT.md` before you finish** (rule 10 — a
review's citations once pointed at a file that was never created, and the manager
repeated that failure at TASK_060), then return the same content in the report
format. Rank findings `blocker` · `major` · `minor`, with file:line and a
concrete failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** The running count is
**128** — p47's engineer contributed ten in one task, including refuting the
catalogue's bug class and my claim that `Ir(k)` would be linear (it is a 32-byte
staircase, and above 128 bytes not even uniform).
