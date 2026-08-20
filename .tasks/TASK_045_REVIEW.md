# TASK_045_REVIEW — p13 says safe Rust beats unsafe by 17%, and never searched the unsafe side

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_043.md` (the spec — note
the engineer refuted **six** of its prescriptions and was right each time), then
**`patterns/p13-strncpy-trunc/NOTES.md` in full**, then its `spec.md`,
`model.py`, `inputs/gen.py`, `controls/`, and `.memory/01-ladder.md`
**finding 9 (p11 — the library/spelling/safety separation)**, **finding 12
(p12)**, **finding 14 (R4 is chained to the prover; "safe beats unsafe" has been
claimed four times and qualified every time)**, and
`.memory/02-bench-rules.md`'s **"Result consumption: keep the full-extent
fold"**.

p13 is the thirteenth pattern: gate `PASS`, Verus **17/0 first attempt** (twin
20/0), `R4 ≡ R5 exact`, TCB 5 items matching the gate's own count, Miri clean
9/9, 26 records 0 stale, shared idiom paragraph byte-identical across all
thirteen. **Unreviewed.**

Its `NOTES.md` is candid about its own gaps — it declines to publish a cost law,
states its R1 design is rank 3/5 and can never be more, and says outright that
the R4 side was never searched. **Treat that as a map of where to dig, not as
work already done.**

## 1. The fold is narrow, the oracle hole follows from it, and BOTH the spec and the report mis-attribute it

`c/kernel.c:72-73` folds **only** `d` and `dst[0]`. Everything in `dst[1..]` is
invisible to the checksum. That is why `controls/oracle_hole.py`'s mutant — write
`0xFF` into `dst[1..n]` — agrees on **9/9 inputs** and walks past stage 2 *and*
stage 5d.

**Two attributions to check, and I believe both published ones are wrong:**

- `NOTES.md` reports this as a limit of *the gate's* pinned fold. But
  `.memory/02-bench-rules.md` has said **"keep the full-extent fold"** since
  TASK_004_REVIEW, with the reason stated in the same words the hole disproves:
  *"what actually certifies the copy is step 2 — the model checksum folds the
  copied bytes."* p12 folds its whole destination; p13 does not.
- **The narrow fold came from `TASK_043.md`, which I wrote.** So the finding is
  real and the *cause* is a manager spec error against a rule that already
  existed — not a gate defect. **Confirm or refute that attribution**, because it
  decides whether the outcome is a gate change (expensive, must pass "could this
  happen by accident?") or a one-line kernel fix (cheap, and the rule is already
  written).

Then cost the fix, which is the part that actually matters:

- **Does a full-extent fold of `dst[0..DST_CAP]` change any p13 conclusion?**
  It moves every checksum and every `Ir` number, so it is not free. Specifically:
  does it break the engineer's **"the two harms separate by rung, not by input"**
  construction (§1's `exact` / `truncate` / `truncate-alt` triple, which prints
  one shared checksum across every checked rung)? That design is good and I do
  not want it lost to a fold change — **say whether the two survive together.**
- Does the narrow fold let LLVM elide any part of the copy in `whole` mode?
  TASK_004_REVIEW measured that it does not on p02 (`dst` is a caller-visible
  `&mut [u8]`), but p13's `dst` is a **fixed local array**, which is the case that
  reasoning does not cover. **Check it rather than inheriting it.**

## 2. "Safe Rust beats unsafe by 13.6–17.3%" — with the R4 side never searched

`NOTES.md:450-461`. This is the **fifth** claimed instance, and the previous four
were all qualified, one of them **sign-flipped by a reviewer who built the R4 the
delivery had inferred was impossible** (p12, route A: verified 15/0, twin 18/0,
17.00/92.00 cheaper, and shipped R3 turned out `+66.00` *dearer*).

p13 does the qualifying honestly — it names the routines, and
`controls/spellings.py` v3 prices the same R3 with byte loops back above R4. But
`NOTES.md:842` says plainly: **the R4 side is not searched and no pair interval
is published.** So the whole `−1126.00` rests on one unsafe spelling nobody tried
to improve.

**Build the cheaper R4.** The obvious candidate is the one the finding is about:
R4 spells the copy and the fill as unchecked byte loops while R3 gets `memcpy`
and `memset`. **`copy_nonoverlapping` is expressible and verifies** — p08 ships
it at 11/0, and 15/0 under the twin. So:

- Build an R4 whose copy is `ptr::copy_nonoverlapping` (or
  `copy_from_slice` on an unsafe-side slice) and whose fill is `write_bytes` or
  the equivalent, **and run `./verus_run.py` on its twin BEFORE differencing
  anything** — `.memory/01-ladder.md` records five published figures killed by
  skipping exactly this step, and it costs about eleven minutes.
- **Read the error text, not the exit code.** `is not supported` disqualifies;
  *"postcondition not satisfied"* disqualifies nothing.
- If it verifies and lands at or below R3, **the headline flips** and p13 joins
  p12 in having its sign corrected at review. If every route is `is not
  supported`, that is the *other* publishable result — the fifth and cleanest
  instance of finding 14's **R4-is-chained-to-the-prover** mechanism, on a
  pattern where the safe class reaches two glibc routines the unsafe class
  cannot. **Either outcome is worth the session; a silence is not.**

## 3. Does `strlen@plt` make the C-vs-Rust rows a LIBRARY comparison?

`NOTES.md:353-371`. Every C `-O3` cell calls glibc `strlen` — both compilers
recognise `d = 0; while (dst[d] != 0) d++;` and rewrite it — while `NOTES.md:370`
asserts **no Rust cell does**, because R2's consumer is a bounds-checked index
and R3's a bounded iterator.

p11 measured glibc `strlen` at **0.078125 Ir/byte** (IFUNC → AVX2) against Rust's
scans at 0.9375 (`memchr`) to 9.0 (indexed) — a **12×** library gap that p11
exists to separate from safety. **p13 has that same gap inside its C-vs-Rust
rows and does not decompose it.**

- **How much of p13's C-vs-Rust difference is the consumer scan?** Price it and
  say. If it is a material fraction, the C rows need p11's three-way treatment
  (library / spelling / safety) and **the routine must be named beside every
  rate**, which is finding 9's rule.
- Then the gate question, which is separable and reaches other patterns:
  **`strlen(` is a `forbidden` spelling, is absent from every source, and the
  audit reports `forbidden: 14 spelling(s), 0 hit(s)`.** A text pin binds the
  source, not the object. Is that a real limitation, and **which other patterns
  have `forbidden` tokens a compiler can synthesise?** (`memcpy`, `memset`,
  `memchr`, `strlen` are the obvious family.) A `forbidden` entry that the
  compiler can reintroduce is reporting a clean negative it has not earned —
  which is the shape of `.memory/01-ladder.md` finding 20(b), where five
  forbidden entries audited nothing.

## 4. The termination store, and the two laws that ARE published

`R1h − R1 = +1.00000 Ir per string` on **both** compilers, `+13.0000` on `small`,
`+24.0000` on `large`, and `== 8.00` on all 31 band-L blobs.

- Re-derive it off the listing, not from a marginal. The task file predicted the
  store might be **dead-store-eliminated where the zero-fill runs** and cost
  something only on the truncating path; the delivery reports the opposite
  (per *string*, not per *truncated* string). One of those is wrong about the
  mechanism even if the number is right — **which?**
- Band L is 31 blobs at a constant `8.00`. A constant across a band is what a
  rank-deficient design produces (p03, p09, p12, p04 all hit this). **Check the
  rank of p13's pooled design**, and check whether band L holds `K` constant.
- `NOTES.md` says **R1's design is rank 3/5 and can never be more**, because R1
  cannot run on a truncating blob and among non-truncating rows `C == S − K`.
  Verify the impossibility argument — it is a strong claim and if it is right it
  should be quoted, because it means the two C rungs have **no** fitted law at
  all and that is an honest structural limit rather than a gap.

## 5. The un-published cost law — is the step basis really untried?

`NOTES.md` 8b declines to publish any law: worst in-sample residual 115–888,
because `strncpy` lowers to size-dispatched vector code, so cost is a **step
function** with a discontinuity at the dispatch threshold. It names
`ceil(F/32)` as the untried candidate and stops.

**Try it.** A step basis is one column in the design matrix. If a
`ceil(F/32)`-style basis fits at low residual, p13 gets its laws back and the
"no law" finding becomes "the law is a step function, and here it is" — a better
result. If it does not fit, the negative is worth stating with the residual, and
p13's honesty is confirmed rather than assumed.

⚠ And check the consequence the engineer flagged against itself: **band T's
out-of-sample residuals (5.10 / 12.24) are SMALLER than in-sample**, so the
mandated out-of-sample test **falsifies nothing**. A test that cannot fail is not
a test — is that because band T is inside the same regime, and what would a real
out-of-sample point look like?

## 6. The rest, in order

1. **Reproducibility is claimed to be a per-binary property**: 60 runs each, all
   four `c-gcc` builds stable, **3 of 4 `c-clang`** unstable — which *reverses*
   phase 0's gcc-unstable/clang-stable reading. Reproduce it. The gate note
   (`adversarial-truncate.bin/c-clang: opt/mode variants disagree, 3 distinct
   behaviours`) should be consistent with whatever you find.
2. **The `idiom` block was written AFTER the rung sources**, before any perf
   measurement. That is not the mandated ordering. **Apply the direction test**:
   does any exclusion move a published figure, and by how much? p04's moved by
   exactly 0.00, which is what a clean answer looks like.
3. **Mutant M2** — weakening the trusted `requires` — verifies **17/0 and 20/0**
   and is caught **only** by `spec.md`'s item pin. On p04 the equivalent mutant
   was caught by the **twin**. Why the difference? If p13's twin cannot see a
   weakened `requires`, that is a gap in the mechanism `.memory/04-verus.md`
   describes, and it matters more than p13.
4. **The library axis has no clang column** (gcc only) and the routines are
   claimed matched by a shared checksum. Verify the matching, and check whether
   `strlcpy` being **+26.00 dearer** than `strncpy` — *"the unsafe routine is the
   cheapest"* — survives on clang. It is a nice result and it is currently
   single-compiler, which `.memory/` forbids for C-vs-C claims.
5. **`work_per_call` was redefined** to `DST_CAP·K + S` after the default gave a
   **negative** `d(Ir)/d(work)` in 16 of 32 cells, and `gen.py` now asserts
   `large` dominates `small` componentwise. Confirm the anti-collapse stage still
   certifies something after the redefinition rather than being tautological.
6. **Wall clock is NOT withdrawn here** (floor 0.63–1.86%, effects 4.6–14× it).
   That is unusual on this project. Check the `t(n_iters = 1)` correction was
   applied and that `R5 − R4` — which must be 0 — is inside the error bar.

## Clean negatives are worth as much as findings

PROTOCOL rule 6 — name what did not land so nobody re-runs it. In particular, if
the R4 side really cannot move, **say so in general terms**: that is the fifth
instance of a mechanism this project cares about, and hedging a confirmed
negative is its own failure.

## Constraints

No root; no `/tmp` — scratch `.temp/r45/`, delete binaries and blobs when done,
**keep the generators**. **No `git add`/`git commit`** — read-only git. Do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or anything under `patterns/`.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell**; subtract `t(n_iters=1)` before any wall-clock ratio (±9 points);
`harness/measure.py --check-stale` before quoting a record.
⚠ `common/layout/order.py` **appends `.bin`** — pass `--input small`.
⚠ **memcheck works on a STATIC build** for uninitialised-value questions
(`.memory/00-environment.md`), and p13's engineer measured it **blind** to this
pattern's in-frame overread of initialised bytes — so ASan, not memcheck, is the
instrument here.

Notes to `.temp/r45/NOTES.md`. Report in PROTOCOL's format, severity-ranked,
with file:line and a concrete failure scenario per finding.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Fifty-seven agents have and all fifty-seven were right — p13's own engineer
refuted six of my prescriptions in one task, including one that was
unsatisfiable. What I am least sure of, and what I most want measured, is **§2:
whether an admissible R4 with bulk spellings exists.** If it does, p13's headline
is wrong by 17 points and I would rather find that here than after it is
published. And **§1 is my error** — I specified the narrow fold against a rule
this project settled nine tasks before p13 existed; tell me how much it costs to
put right.
