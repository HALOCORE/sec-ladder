# TASK_050 — p14's corrections: a hardening law fitted where the guard never fires, and a null control that is one biased draw

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_049_REVIEW_REPORT.md`
in full — it is your whole task** — then `.tasks/TASK_049.md` and
`.tasks/TASK_049_REPORT.md`, then `.memory/03-measurement.md` (**trap 3's
dynamic half; the layout modes at `:789-921`**), `.memory/01-ladder.md`
**finding 15 (p06)** and **the direction-test "IT FIRED" block**, and
`.memory/02-bench-rules.md`'s two-number corollary.

**Read the good news first.** **Your provenance is clean** — the reviewer
independently re-measured 8 cells × 8 sweep blobs plus 8 cells × 2 perf blobs
and every value matches `sweep_all.json` and the published tables to four
decimals, including the `x08a`/`x08b` negative control. **Nothing from the
corrupted sweep survived anywhere**, which is the outcome your own self-report
made checkable. The gate, the proof counts, Miri and `contract_sha256` all
reproduce. **17 clean negatives** are recorded; read them before re-running
anything.

**And your instinct to publish no `ns` claim was right, for a better reason than
you gave.**

## The two blockers

### 1. The R4/R5 pair is one biased draw, not a null — and it is biased the same way on TWO patterns

Your proposal (report memory item 5) was that the byte-identical R4/R5 pair is a
free null control. **It is not, and the mechanism is measured.** p14's kernel is
bimodal in `addr % 64` (`%64==16` costs 264–277 ns, `%64==48` costs 244–248), and
**the `verus` build's kernel lands 0x20 below the `unsafe` build's — at the same
two addresses, on p06 and p14 alike.** So the pair samples one *fixed alignment
contrast* every time. That is why your two passes agreed to 0.06 pp: you
re-sampled the same draw. Over a 24-layout population the pair's median is
**≈0 on both patterns**, and on p14 your 9.2% **under-states** the 13.22%
within-cell layout spread it claimed to bound.

- **Restate it as: a smoke alarm, not a floor.** The floor is the **layout
  population**. Land that wording in `NOTES.md`; the manager will lift it.
- **Port `clayout.py`** and publish p14's population. The reviewer built one
  under `.temp/r49/` (`align-all-functions` + `--symbol-ordering-file`, `n_fn`
  and `md5_fn_norel` single-valued, 21 distinct addresses) — **reuse it.** You
  said the `win32`/`jcc32` question was "unasked, not answered"; answer it.
- ⚠ **You may edit `patterns/p06-rotate/NOTES.md:353` for this and nothing
  else**: *"±3% as the honest inter-binary floor"* should be **±4.6%** (p06's
  measured layout spread is 4.02%/5.10%, its R5−R4 cross-pair range −4.31%…
  +4.61%). **p06's headline is intact** — its clang column clears ±4.6% at ~2.1×
  and its 30-layout C population defends it independently. Change the number, do
  not touch the conclusion, and do not re-measure p06.

### 2. "EXCLUDED BY THE HARNESS" is false, and the better objection is yours to write

§0a says the harness excludes a payload-mutating tokenizer. **It does not.** The
mutating kernel reaches a steady state after exactly **one** call (`r2=r3=r4`,
closed form verified), so `measure.py`'s marginal is **exactly 9044.0000 Ir/call
with zero residual**, and `check.py` compares against `model.py`'s own
simulation — **nothing in `harness/` enforces purity.** The only actual obstacle
is **your own `model.py:143-147` memoisation.**

**The real objection is better than the one you published and you should say
it:** after call 1 every delimiter is NUL, so the steady state measures an
**already-tokenised buffer** — a different workload from the one the pattern
names. Rewrite §0a on that basis.

⚠ **This one matters beyond p14.** The false claim was aimed at
`.memory/06-catalogue.md` and would have been recorded as a property of the
*infrastructure* — that the repeat protocol makes an entire bug class
unbuildable. It is not in `.memory/` **only because rule 9 held the write until
the review landed.** Say plainly in `NOTES.md` what the repeat protocol does and
does not exclude.

## The three majors

### 3. The exact gcc law was fitted entirely where the safety line never executes

`c-gcc-h − c-gcc = 1.00·bytes + 2.00·fields − 3.00` has max residual 0.0000 over
66 blobs — **and the fit set contains zero inputs where the guard fires.** On the
inputs p14 exists to model it breaks with an **inverted sign**:

| blob | predicted | measured |
|---|---|---|
| `degenerate` | +139.00 | **+139.000** (a new out-of-sample hit) |
| `run17` | +47 | **+16.04** |
| `alt33` | +93 | **−551.04** |
| `full65` | +93 | **−823.00** |
| `many` | +429 | **−610.98** |

**Publish the law with its domain stated**, and publish the adversarial numbers
beside it. ⚠ **And notice what they say: on every input p14 exists to model,
hardening is CHEAPER than the bug.** That is a headline in its own right — the
safety check pays for itself on exactly the inputs that matter — and it is
currently nowhere in the file. Give it the prominence the law has.

**It is a gcc result**: clang's marginal is unusable on `alt33`/`full65`
(SIGSEGV) and reads +17.98 on `many` because the overflow smashes the C driver's
own frame. Say so rather than generalising.

### 4. The leave-one-length-out test cannot fail, provably

`max|residual| = 0.0` exactly and the design keeps **rank 4 after dropping any
whole band**, so every hold-out reproduces the same exact solution by linear
algebra. **This is p13's mistake in a new costume** and the task file suspected
it. Either **add a band that breaks the rank** so the test can fail, or state
plainly that it cannot and that the law's evidence is the exact fit plus the
out-of-sample perf-row predictions — **not** the hold-out. Do not leave a
hold-out in the file implying a test it did not perform.

### 5. `"the first time both halves are readable in ONE listing"` is false

`README.md:66-70`, contradicted by **`p16/NOTES.md:563-568` — the very file p14
cites for `4.25 = 2.00 + 2.25`.** Fix the claim; the constant is fine.

## The four minors

6. **`pm3_msonly` emits two errors**, not one (`invariant not satisfied` at
   `nt <= MAXTOK` plus the precondition) — identical to `pm1_nocap`, whose row
   lists both. Both are memory-safety obligations so **the conclusion survives**;
   *"the same obligation"* → *"the same two obligations"*. ⚠ **And `pm3` is not
   literally a memory-safety-only spec** — only the kernel's `ensures` is
   weakened; the functional loop invariants remain. The claim it actually tests
   is *"weakening the postcondition to `true` does not rescue the mutant"*.
   **Fix the `.memory/`-facing summary**, which is the one place it overstates.
7. **`"the omitted line is literally i < m"` is not what `k_unbnd` does**
   (`NOTES.md:123`, `spec.md:130`) — it replaces `while (i <= m)` with `for (;;)`
   **and adds** a NUL sentinel, and the sentinel is what makes it p11. The
   conclusion is right, the sentence is not.
8. **The `flen` entry's price is published for R4/R5 only.** Measured on all
   eight cells: `-O3` **zero everywhere**; `-O0` **+3 static instructions** on
   `safe_naive` (349→352), `safe_tuned` (347→350) and `unsafe` (286→289), 0 on
   `verus`. Land the R2/R3 half. ⚠ **This is the entry you disclosed as having
   been added in response to a gate measurement** — the review did not fault the
   disclosure, so keep it, and now that the price is measured on every rung,
   **publish it beside the number it protects** (p13's fiat rule).
9. Check the remaining review minors and the 17 clean negatives for anything
   whose *wording* needs to move even though its conclusion held.

## Done when

Items 1–9 land; `check.py p14` green on a complete run; `check.py p06` green if
you touched p06's `NOTES.md` (the gate hashes it); `--check-stale` clean; tables
regenerated; `contract_sha256` moves if you touch the hashed block. Every figure
that moved is restated **everywhere it appears** — `NOTES.md`, `README.md`,
`spec.md` prose, results tables.

## Constraints

No root; no `/tmp` (scratch `.temp/p50/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/`.** **The only
patterns you may edit are p14 and — for item 1's single number only — p06.**
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** ⚠ **Per-PID scratch paths** — you corrupted a sweep without them.
⚠ `check.py` rewrites its pattern's gate JSON; know what you changed.

The reviewer's scratch is `.temp/r49/` with the **24-layout populations for both
patterns**, the steady-state probe, the adversarial re-measurement and the rank
analysis **already built** — **reuse rather than rebuild.** Notes to
`.temp/p50/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Seventy-six
agents have contradicted the manager and all seventy-six were right — p14's
reviewer refuted the manager's stated doubt about item 1 *and* all three answers
the task offered for it, and the correct answer (the layout population is the
null; the R4/R5 pair is a biased sample of size one) was not among them.

**What I am least sure of is item 3's framing.** I am calling *"hardening is
cheaper than the bug on every input p14 models"* a headline. It may instead be
an artefact of what the unhardened rung does on those inputs — it overflows, and
a smashed frame is not a fair performance baseline; the `many` row's clang
reading is explicitly that. **If the comparison is not meaningful on inputs where
R1 commits UB, say so and say what the honest statement is** — that question
reaches p12 and p02 as well, and nobody here has asked it.
