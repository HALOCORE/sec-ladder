# TASK_044 — p04 owes its review one blocker, three majors and four minors; its headline SURVIVED and got sharper

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_042_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md` **finding 13
(p04)** and **finding 3's new two-step-reslice paragraph**,
`.memory/03-measurement.md`'s new *"A fitted law is a law in SOMEBODY's counts"*
section, and `.memory/00-environment.md`'s corrected **memcheck** entry.
**All four are already written by the manager and are the wording to follow.**

**Read the good news first: your headline is confirmed and is now stronger than
you published it.** The reviewer ran the loop/no-loop separation and found the
check deleted in straight-line code *and* across a non-loop phi at CAP=60, and
kept only in the loop — so *"does not survive the **loop-carried** phi"* is
measured rather than asserted. Every capacity prediction held. **Land the
corrections; do not re-derive what is already in the report.**

## The blocker

1. **`NOTES.md:871`, `:1076`, `README.md`: the shipped R3 is NOT the cheapest
   found, and p04's tax is `+4.00`.** Six in-contract spellings across **five
   distinct machine codes** measure `3367 / 11666` against your `3368 / 11667`,
   all at `required_miss = 0`, `forbidden_hits = 0`, `model.py` agreeing on all
   five matrix inputs. The report lists them.
   - **Delete the "a first" claim.** *"The first pattern in this project whose
     shipped R3 is the cheapest found"* is false; p04 joins p03 in having its
     cheapest-found beaten by the next lever.
   - **Restate the fixed-R4 bound as `+4.00`** and the R3-side span from `+4`.
     `R2 − R3` becomes `20·ops + 12` against the cheapest.
   - **Ship at least the two-step reslice as a control** in `controls/`, and
     state the mechanism: **register allocation, not bounds-check removal** —
     both forms keep both checks, but `off + len` needs a scratch register
     (`mov ; add ; jb ; cmp ; ja`) where `buf_len - off` is computed in place in
     `%rsi`, dead afterwards (`sub ; jb ; cmp ; ja`).
   - **Keep §13's direction test as it stands — it holds.** The `idiom` block
     pins no reslice spelling, so all six candidates are in contract *by
     construction*: it is the cheapest-found claim that failed, not the
     declaration. Say that explicitly, because it is the distinction the whole
     spelling arc exists to draw.
   - ⚠ **Decide and state whether the shipped R3 changes.** If you re-ship on the
     cheaper spelling, `contract_sha256` and every p04 number move and the gate
     must be fully re-run; if you keep the shipped rung and publish `+4.00` as
     the cheapest found, nothing moves but the prose. **Either is defensible —
     say which you chose and why**, and note that no other pattern re-shipped
     after a cheaper in-contract spelling was found.

## The three majors

2. **`NOTES.md:449-459`, `:466-467`: two of your seven laws are in R1's OWN
   counts and fail out of sample.** Band F has `epop == 0` **by construction**,
   so the licence's second and third conditions were checked exactly where they
   could not fail. A fresh blob with `dpush` *and* `epop` both non-zero — a
   combination **no shipped blob has** — misses by **−385 (gcc) / −330 (clang)**,
   and the same laws at R1's own counts land exactly. Knock-on:
   `R1h − R1 (gcc)` predicts `+1368`, measured `+1753`.
   **The fix is one sentence per row** — state the two R1 rows in R1's own
   counts, or restrict them to `epop == 0` — plus deleting *"seven exact integer
   cost models"* as a blanket claim over all seven. **The other five re-derived
   exactly** by independent exact-rational solve, the rank table reproduced, and
   the `large` out-of-sample prediction held; say so, because five of seven
   surviving an independent re-derivation is the stronger half of this item.
   ⚠ **Consider shipping the reviewer's blob as `adversarial-mixed`** (or a
   `sweep-` band that turns on every regressor at once). 99 in-sample blobs could
   not see this; one adversarial blob did, and `.memory/03-measurement.md` now
   makes that a rule.

3. **`NOTES.md:194-196`, `:49-51`, `README.md:37-39`, `safe_naive.rs:26-31`:
   "`% 60` fixes NO bits" is false, and the dichotomy is quantitative.**
   `computeKnownBits(urem x, 60)` zeroes the high 58 bits — `x % 60 < 64` — and
   **that survives the phi**: `% 60` into a `[u64; 64]` array elides both checks.
   Replace with the measured rule, which has **zero fitted parameters** and
   predicts cases you never built:

   > `urem x, C` ⟹ `x < next_pow2(C)`, and the check is elided exactly when
   > **`next_pow2(CAP) ≤ ARR_LEN`**.

   Plus the two refinements: **(a)** the source-branch wrap at CAP=**64** brings
   both checks back (86 → 101, 1 → 3 pads) at the identical provable range — this
   is what *confirms* "bits, not a range", and it is a better piece of evidence
   than anything in the shipped §1; **(b)** a **guard** in the loop destroys the
   fact for `urem` and **not** for `and`.
   ⚠ **Do not overcorrect.** Your headline sentence stands. What was wrong was
   the explanation of the 60 case, and the corrected version is a *stronger*
   result — a zero-parameter rule that predicts unbuilt configurations.

4. **`NOTES.md:1049-1059` (§12c): the invisibility is not about the modulus.**
   Delete `%` entirely — wrap with a source branch reached under the guard — and
   the memory-safety obligation is **still** two independent one-variable clauses
   (`9/0`) and the missing fullness check is **still** invisible. **The property
   is that the index bound is the array's own fixed capacity**, not that the
   update is modular. Rewrite so the next fixed-capacity container without a
   modulus is recognised as the same class.

## The minors

5. **The invisibility claim is true but is not a characterisation.** Reading
   `ring[tail]` instead of `ring[head]` — memory-safe, functionally wrong, **no
   guard touched** — also verifies `9/0`. The memory-safety-only configuration is
   blind to **every** functional change. Land that beside your relation sentence
   rather than instead of it; and add the stronger form the reviewer measured:
   **both guards deleted at once is also `9/0`**.
6. **`NOTES.md:205-206`**: "2.27 pushes per call" at CAP=60 on `large` is
   **2.23067** driver-weighted / 2.25 unweighted. Nothing rests on it.
7. **`verus.rs:24` and `spec.md`'s `note`** cite "NOTES.md 6 measures
   `nofull_msonly` at 12 verified" where §6 prints 9. **The number is right** —
   `m_nofull_msonly --cfg slb_twin` is 12/0 — **only the citation is loose.** Fix
   the citation; do not "fix" the number.
8. **Two rows you left unattributed now have mechanisms** (report §"Mechanism
   contributions"): gcc's `+717` at CAP=60 decomposes **exactly** as
   `4·237 − 3·119 + 118 + 8` (four value-byte `movzbl` sunk out of the push arm
   into the shared dispatch block), and clang's R1h-cheaper-by-1-per-pop is the
   two builds swapping which arm falls through, the out-of-line arm paying one
   unconditional `jmp`. Land both; you flagged the second against yourself.
9. **§11d says no layout population was run — one now exists** and your `ns`
   figures **survive it** (`+25.1…+26.0%` / `+9.3…+10.2%` mode-matched,
   `P(A>B) = 100%`, `R3 − R4` null with the sign flipping between modes). Update
   §11d, and record the reviewer's **minor 8** as an open curiosity: `small`'s R2
   population is **bimodal at 1.42×**, reproducible, and **neither `win32`/`jcc32`
   nor `addr%32` separates it** — the first layout mode on this project that
   finding 16's mechanism does not explain.

## Done when

Items 1–9 land; `check.py p04` green; table regenerated; `--check-stale` clean.
`contract_sha256` moves only if you touch the hashed block. **If you re-ship R3,
the whole gate re-runs and every p04 number in every file must move with it** —
including `results/` and `RECAP.md`'s finding 23, which the manager will land
from your report.

## Constraints

No root; no `/tmp` (scratch `.temp/p44/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. **Prose, `patterns/p04-ring-buffer/controls/*.py`,
and `inputs/gen.py` only** — no `harness/`, no `common/`, and no rung source
except the comment blocks named in items 3 and 5, *unless* you re-ship R3 under
item 1, which is the one change that touches a rung. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.**

The reviewer's scratch is `.temp/r42/` with **every control already built and
generated** — the 48 probe kernels, the 16 R3 candidates, the 10 Verus mutants,
the exact-rational solver, the out-of-sample blob and the 30-layout population.
**Reuse rather than rebuild.** Notes to `.temp/p44/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Fifty-six
agents have contradicted the manager and all fifty-six were right — you were one
of them, three times in one task. What I am least sure of is **item 1's
re-ship-or-not decision**: I have left it to you deliberately, because re-shipping
buys a truer headline number at the cost of a full re-measure and a moved
contract hash, and no pattern here has ever done it. **If there is a reason the
project should never re-ship on a cheaper in-contract spelling — or should always
— that is a rule worth more than p04's one instruction, and it belongs in
`.memory/02-bench-rules.md`. Say which, and why.**
