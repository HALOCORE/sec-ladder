# TASK_057 — p10, sliding window / FIR stencil: the first kernel with more than one indexed read per iteration

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` — **finding 3** (the +8…+10 flat tax, and the
two-step reslice), **finding 9 (p16)**, **finding 12 (p12)** and **finding 6
(p05)** — then `.memory/02-bench-rules.md`, `.memory/03-measurement.md` (**the
DOMAIN section and ADDITIVITY EXTRAPOLATION at `:1243-1277`**, the post-drop rank
rule, the null-control section, the layout modes at `:789-921`, and **the `div`
pricing at `:434`**), `.memory/04-verus.md`, then **`patterns/p18-varint-shift/`
and `patterns/p14-field-split/` in full** — p18 is the template you clone. Where
this spec is silent, **do what p18 did.**

## §0 — settle the bug class first, and settle the ALGORITHM with it

`.memory/06-catalogue.md` says p10's class is *"off-by-one at boundaries"*.
**Treat that as a prior** — four patterns have overturned their catalogue row.
§0's deliverable is a written decision in `NOTES.md` §0 naming the bug, the wire
format, what it does in each cell, and **why the rejected candidates were
rejected.**

⚠ **§0 has a SECOND deliverable here that no previous pattern needed: the
algorithm.** A box-filter sliding window has an O(n) running-accumulator form
(add the entering element, subtract the leaving one) and an O(n·r) tap-loop form.
**If any rung uses a different one, every comparison in the pattern is void** —
the reviewer checklist calls this out by name. Two ways to close it, and I want
your reasoning, not just a choice:

- **Make the kernel a weighted FIR** — `acc += a[i+j-r] * w[j]` — which *cannot*
  be computed incrementally, so O(n·r) is honest in every language and the
  "you pessimised C" objection dies. This is my recommendation. It is also a
  genuinely common C shape (DSP, image blur), which the realism bar wants.
- Or use the running accumulator in all five rungs and accept that the radius
  stops being a cost parameter — which kills §2 below.

**Two hazards to price before you commit to a shape:**

- **Do not put a runtime `div` on the output path.** p06 is the pattern where a
  division became the safety line, and callgrind prices a hardware `div` at
  **1 `Ir`** (`.memory/03-measurement.md:434`) — so a per-output `div` costs
  almost nothing in the column this project publishes and a great deal in wall
  clock, and it will muddy every per-tap law you fit. Sum into a `u32` and fold
  the sums, or normalise with a shift.
- **The fold must be able to SEE the bug.** p06's lesson: a sum-fold cannot
  observe a permutation. Check yours observes whatever your §0 bug actually
  changes, and say how you checked.

## Why I think p10 is the right next pattern

**1. It is the first kernel here with more than one indexed read per iteration
at a fixed offset from the cursor.** Every pattern so far has one cursor (p16),
two (p08), or an index computed from two (p05). A `2r+1`-tap stencil has `2r+1`
reads — so the question this project has never been able to ask is: **is safe
Rust's tax proportional to the number of indexing operations, or flat?**

Finding 3 says the tax is *"flat in the size of the data"*. **Tap count is not
data size.** So a tap-proportional tax would **bound finding 3's domain without
contradicting it**, which is exactly the shape `.memory/03-measurement.md` says a
law owes.

**2. The radius is a second structural parameter, so ADDITIVITY EXTRAPOLATION is
available by construction.** Fit where `r` varies at fixed `n` and `n` varies at
fixed `r`; predict the rows where both move. That is **the only out-of-sample
test on this project that has ever been able to fail** (p18, worst error 0.0228);
every hold-out before it was provably incapable of failing. Build the sweep so
this test exists — do not discover afterwards that your bands span the row space.

**3. Safe Rust has a dedicated library idiom of exactly this shape and NO pattern
here uses it.** `grep -rn "windows(" patterns/*/*.rs` returns nothing. I believe
`slice::windows(size)` takes a **runtime** `size` — **verify that**, because the
whole R3 spelling below depends on it. That gives a three-way separation of the
kind p11 made on `memchr`, but on a different lowering (vector ALU, not a libc
string routine):

| rung | spelling | checks per output element, predicted |
|---|---|---|
| R2 | index each tap: `a[i+j-r]` | **`2r+1`** (plus `w[j]`) |
| R3 | slice the window **once**, reduce it: `a.windows(2*r+1)` or `&a[i-r..=i+r]` | **1**, flat in `r` |
| R4 | `get_unchecked` | 0 |

**4. p10's R3 opens with a window reslice, which makes it the most natural home
on the project for the two-step reslice** — backlog priority 1, worth
**−1.00 `Ir`/call**, measured on six patterns, costs zero `unsafe` and zero TCB.
`.memory/01-ladder.md` finding 3 carries the spelling and the mechanism. Try it
and report the number either way; a clean negative here retires a standing item.

## §2 — the registered prediction. This task file is committed BEFORE you measure

`.memory/03-measurement.md:1233` — *a re-derivable hash is tamper-evidence, not
pre-registration; to make it real, register in a commit that PRECEDES the
measurement commit.* The manager commits at task boundaries anyway, so this is
free, and I am spending it on the table above. **These are my predictions, made
without measuring:**

- **P1.** `R2 − R4` grows linearly in the tap count `2r+1`, slope > 0.
- **P2.** `R3 − R4` is **flat in `r`** — the window slice is one range check
  however many taps it covers.
- **P3.** At `-O3`, R3's inner reduce vectorises and R2's does not.

**Falsify these.** The most likely way they die is that LLVM hoists every tap's
check into a single `i + r < n` precondition, making R2 flat in `r` too — in
which case **P1 and P3 are wrong, the finding is a stronger version of finding 3,
and it is still worth publishing.** ⚠ **Measure the tap-count slope on day one,
before you build five rungs**, and report it against this table by name.

**Where the design could collapse instead:** if a runtime radius will not
vectorise at all, R3 and R4 both go scalar and P3 is untestable. Check that early
too. **If the fix looks like a compile-time radius**, STOP — that means one cell
per radius rather than one binary over a sweep input, which changes what the gate
covers, and it is a harness question, not yours to decide.

## What p10 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**
  (PROTOCOL definition-of-done 6). One line. If it changes later, say why.
- **Two in-contract R3 spellings, and quote the cheaper** (finding 3), with the
  input named — never the word "minimum"; write "cheapest found".
- **A length-heterogeneous sweep, and report the design's rank after dropping
  each band.** A residual of exactly zero is the signature of a test that could
  not fail. p06's can fail; that is the standard.
- **Attribute every per-iteration `Ir` law mnemonic by mnemonic** before naming
  it after a mechanism — executed alignment padding has landed inside a published
  law three times.
- **Check the panic pads before calling any per-tap term a safety cost.** p06's
  2.00 `Ir`/byte contained none.
- **No `ns` claim without a layout population.** The R4/R5 pair is a smoke alarm,
  not a floor; `controls/clayout.py` ships on p06 and p14 — port it.
- **Price every scoped idiom entry**, and run the direction test in writing on
  any declaration edit. Disclose one made in response to a measurement, the way
  p14 did; that disclosure was reviewed and upheld.
- **Adversarial rows per rung**, with distinct harms in distinct columns.
- **In-place is out of scope** — that is p08's aliasing story. Out-of-place only.

## Verus

Budget **one session**. A stalled proof reported with its exact error IS the
deliverable. The obligations are `r <= i < n - r` plus non-overflow of the
accumulator; catalogue rates it moderate. ⚠ **A runtime radius makes this a
nested loop, and `.memory/04-verus.md` records that `decreases b - a` fails on
two-cursor loops** — read that section before you fight it. **TCB: one number
plus the U-license / V-gap / infra classification.** Check
`~/tools/verus/vstd/std_specs/` before recording "no spec exists"; that claim was
false for `copy_from_slice` and stood from TASK_004 to TASK_048.

## Done when

The p18 checklist, plus §0's two decisions and §2's verdict on P1–P3. Complete
green `check.py p10`; checksums against an independent `model.py`; adversarial
rows per rung; the `idiom` block written **before** the cells, every entry
backticked, shared paragraph byte-identical; sweep with its fitter committed
under `controls/`; **both** R3 numbers published; two proof mutants failing the
gate; TCB equal to the gate's own `tcb_items`.

## Constraints

No root; no `/tmp` (scratch `.temp/p10/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p10
seems to need a change there, STOP and report it.** Do not edit any existing
pattern's sources. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **Measurements in the
FOREGROUND, interleaved by cell.** ⚠ **Per-PID scratch paths** — a shared path
corrupted a whole sweep on p14. ⚠ `check.py` rewrites its pattern's gate JSON.
`harness/measure.py --check-stale` after measuring. Delete binaries and blobs
once the gate is green; **keep every generator.**

Notes to `.temp/p10/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** **Eighty-nine**
agents have contradicted the manager and all eighty-nine were right — the last
one caught me quoting a price in the wrong `Ir` convention, off by 13×, on a
pattern whose own table already warned about it.

**What I am least sure of is the whole §2 table, and I have deliberately written
it down so it can be scored.** I have not verified that `windows` takes a runtime
size, nor that a runtime-radius reduce vectorises, nor that R2's per-tap checks
survive to `-O3` at all. **Measure those three before building anything on
them.** If the radius does not discriminate, say so plainly — p10 is then a
pattern about a library idiom this project has never used, which is still worth
building.
