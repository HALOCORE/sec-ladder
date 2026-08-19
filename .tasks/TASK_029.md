# TASK_029 — p07's prose owes its own review two majors and six minors

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026_REVIEW_REPORT.md`
in full** — it is your whole task — then `.memory/01-ladder.md` finding 8 (p07)
and `.memory/03-measurement.md`'s new layout-band section and
`.memory/00-environment.md`'s new branch/cache-simulator section. **All three are
already written by the manager and are the wording to follow rather than
re-invent.**

**Your headline survived.** Six workloads, monotone in every one; the laws exact
out of sample 30/30; gate, proof, identity, TCB and the three-bugs table all
reproduced. This task is the prose around it, and one hashed typo.

## The two majors

1. **Scope the claim to R3 — "first counterexample to safety is cheap" is false.**
   `NOTES.md:321` (*"Every prior pattern's answer was 'yes, to zero, per byte'"*)
   and `:347`, plus `README.md:117-118`. `.memory/01-ladder.md` finding 4 already
   carries p16's swept **R2** tax of 4.25 Ir/folded byte — whose fraction *also*
   rises, toward 73.9%, mechanism-attributed and confirmed by construction — and
   finding 6 carries p05's `O(nrow)` **R3** tax. What is true, and is the sentence
   to publish: **p07 is the first pattern where R3's tax has no axis along which
   it amortises.** p16/p17's is a per-*call* constant (0.00000 Ir/byte; the
   reslice sits outside the fold loop), p05's is `O(nrow)` and vanishes along
   `ncol`, p07's vanishes along nothing.
   Also: **the asymptote is workload-dependent.** `README.md:116` quotes 47.99% as
   if the kernel fixed it. Measured, it is `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**
   — 12.0017 Ir/probe on the pure `hi = mid` arm, 13.0026 on the pure
   `lo = mid + 1` arm. Quote it with the query distribution.

2. **Withdraw p07's R2 `ns` numbers until they are bracketed, and ship the band.**
   `NOTES.md:178,182-186`'s bolded *"+28.0% on the L1-resident input and +3.5% on
   the memory-bound one — an 8× difference in the conversion factor"* rests on
   `safe_naive`, which `§11c` never built at more than one alignment. Built at
   seven (identical `Ir/call` 12346.57 at every one), its layout band is
   **28.47%** — the widest single-rung band this project has measured — and the
   comparison intervals are `[−0.72%, +34.08%]` on `small` and `[−0.63%, +3.97%]`
   on `large`, **both spanning zero**, replicated on a second CPU. Neither figure
   has an established sign.
   **R3's counterweight survives and should be stated as the one that does**:
   `[+8.77%, +26.39%]` and `[+0.28%, +3.12%]`, bands disjoint on both inputs in
   both runs.
   You may re-measure to recover a sign if you want one, but **the interval form
   is what ships either way** (`.memory/03-measurement.md`). And note the
   reviewer's open item: `§3`'s **`c-gcc +51.9%`** has no layout band either, and
   `-align-all-functions` is an LLVM knob so the C rungs need a different lever.
   Say so rather than leaving it implied.

3. **§3a's per-probe level is a fit with a wrong mechanism** (`NOTES.md:200-222`).
   `:219` says the workload's 50/50 gives 12.5 Ir/probe matching the swept
   12.5035. Three errors: the 50/50 is the **hit/miss** ratio, not the branch
   split (measured `lo 0.4591 / hi 0.4764 / break 0.0645`); the loop has **three**
   exits, not two; and 12.5035 is an OLS slope over blobs whose break fraction
   falls 0.19 → 0.037. The three-path form — per-probe integers `13 / 12 / 7`
   pinned from the listing plus `16` per query, **two** free parameters against
   §3b's three — gives max residual **0.4127** against 10.566, a 25× improvement
   with fewer parameters, and it *confirms* the published differences by showing
   why they are exact: R3's `+6` and R2's `+11` are identical on all three arms.
   The tell was already in your own §3b table (the branchless row's residual is
   0.41 and the branchy rows' 10.57 — that is un-modelled path mix, not noise).
   **Replace the derivation; the differences do not move.**

## The minors

4. **`NOTES.md:740` "Both candidates were" is false** — `gen_controls.py`
   generates `r4_ptr_twin` only, so `r4_for`'s verdict at `:744` was an inspection
   standing beside a Verus run. The reviewer built the twin and ran it:
   **`10 verified, 0 errors`.** The verdict stands; the claim of having checked it
   did not. **Add `r4_for_twin` to `gen_controls.py`** so the next reader does not
   have to take it on trust. Also `:748` cites
   `.temp/p07/twin/r4_ptr_twin.rs`, which never existed — the file is
   `.temp/p07/controls/r4_ptr_twin.rs`.
5. **`NOTES.md:382-384` §4 quotes gate numbers from before the input fix**
   (`gate1`/`gate2`, 07:07 and 07:10; `inputs/` was regenerated at 07:30). Current
   values are `6021…216053`, `46.1x`, `11.96…131.97`. Same class of error you
   caught yourself in §1 — which is worth a sentence, because it means the fix
   did not sweep every number it invalidated.
6. **"`4·n + 4·nq` needs 36 bits" — it needs 35.** `4·(2³²−1)·2 = 34 359 738 360`,
   `bit_length` 35, `2³⁵ = 34 359 738 368`. Six sites: `NOTES.md:58`,
   `README.md:79`, `verus.rs:179`, `c/kernel_hardened.c:15`, `inputs/gen.py:332`
   and — the one that costs a gate run — **`spec.md:385`, inside the hashed
   `idiom.why`**. The conclusion is unaffected; everything else in §0's arithmetic
   checks out.
7. **Stale probe/window arithmetic.** `NOTES.md:139` says "6428 bytes probed out
   of a 1 048 916 byte window, 0.61%"; it is **6624** and **0.63%**. And
   `model.py:287-290`'s `work_per_call` docstring — which §4 calls "the argument"
   — still carries `nq = 99` numbers (1782 probes, 7128 bytes, 1 048 840-byte
   window, `0.25 × 1048840 = 262210`) against the shipped 1656 / 6624 /
   1 048 916 / 262 229.
8. **`NOTES.md:180`**: R5 is 0.0% kernel-exclusive but **−1.00 Ir/call**
   whole-program against R4. The kernel is byte-identical; the difference is
   outside it. §3b's laws are whole-program marginals and §3's table is
   kernel-exclusive, so one clause stops a reader deriving a contradiction.

## The ride-along, and it is the most valuable thing here

**§11d says the branch attribution "is an inference, not a measurement". It does
not have to be.** `callgrind --branch-sim=yes` runs on this box and reports
simulated `Bc`/`Bcm`; `--cache-sim=yes` reports `D1mr`/`DLmr`. The review closed
both of §11d's stated caveats with them:

- **0.586 simulated mispredicts per probe** on the branchy build against 0.129 on
  the branchless one (−78.1% on `small`, −89.1% on `large`) — exactly what a
  coin-flip branch should give;
- **locality ruled out rather than argued**: `D1mr` is 1076.82 on `large` for
  *both* builds, `DLmr` equal, only the branch counters move;
- **isolation by measurement**: a symbol-by-symbol instruction-stream diff of the
  two whole binaries finds 559 symbols and **exactly one different** (`kernel`,
  70 → 68 raw), which answers the "whole-program flag" caveat.

Land all three in §11d and **say what the simulator is**: a model, not this CPU's
predictor — strong about direction and ratio, weak about magnitude
(`.memory/00-environment.md`). Also worth adding, because it needs no flag at all:
changing only the **workload** makes the same binary at the same alignment execute
**+7.84% more instructions in 71.75% less time** (`allbelow` vs shipped).

## Explicitly NOT this task

`harness/check.py:1753`'s runtime string `head("3c. structural identity R4-vs-R5
(recorded as a result)")` carries the phrase TASK_028 corrected in the comments
beside it. It is real but `harness/*.py` is in **every** pattern's
`source_sha256`, so touching it re-runs all seven gates for a display string. It
is queued.

## Done when

All eight items land; `check.py p07` green (only p07 — you are touching nothing
else); `md5_fn` unchanged; `results/tables/p07-binary-search.md` regenerated with
`harness/report.py`. `spec.md` moving means `contract_sha256` moves; that is
expected and is the only structural churn you should see beyond ASan PIDs.

## Constraints

No root; no `/tmp` (scratch `.temp/p29/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose, `controls/*.py`, `inputs/gen.py`, `model.py`
and `spec.md` only — **nothing in `harness/`, no rung source**. `verus.rs:179` and
`c/kernel_hardened.c:15` are *comments*: fix the number, change no code, and say
in your report that you verified the kernels are untouched (`md5_fn`).
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. **Measurements in the FOREGROUND**, per-PID scratch paths.
Delete your binaries and blobs when the gate is green; keep scripts and notes.

Notes to `.temp/p29/NOTES.md` as you go. The reviewer's scratch is `.temp/r26/`
(180 KB, all text) and has working implementations of everything above —
`layout_r2.py`, `pathfit.py`, `branchsim.py`, `cachesim.py`, `altwork.py`,
`gen_r4_for_twin.py`. **Reuse them rather than rebuilding.**

**If a prescription here is wrong, say so with the measurement.** Thirty-eight
agents have contradicted the manager and all thirty-eight were right — you were
one of them, twice, on p07's own bug class. What I am least sure of is **item 2**:
whether withdrawing the R2 `ns` comparison outright is right, or whether a
bracketed re-measurement can recover a sign and should be attempted before
anything is withdrawn. The band is 28.47% and the point estimate was +4.37%, so my
guess is that no number of reps recovers it and the honest form is the interval —
but that is a guess about a rung whose band nobody has tried to *narrow*, and
alignment is not the only lever.
