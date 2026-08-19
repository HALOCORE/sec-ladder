# TASK_026 — p07 binary search: the first kernel where the clock is set by branches, not instructions

> **ADDENDUM, written at dispatch.** This file was drafted before TASK_025_REVIEW,
> TASK_027_REVIEW and TASK_028 landed, and it is **numbered out of order** — it
> was queued as 026 and dispatched after 028. Everything below stands; §0 is what
> those three tasks changed, and where §0 and the body disagree, **§0 wins.**
>
> ## §0 — what changed while this file sat in the queue
>
> 1. **Never publish a bare per-byte (or per-element) rate, and never a difference
>    of rates across unmatched spellings. Publish only matched-spelling
>    differences.** A bare rate is not a property of the kernel — p16's ranges
>    5.04688…6.62500 in contract, one exact-string substitution apart. This
>    supersedes §2 item 4's weaker "name the spelling beside the rate", which
>    demonstrably did not catch its own author's headline.
> 2. **A five-decimal rate must come from the DISASSEMBLY (`body_len / K`), never
>    from a marginal.** The driver's `println!` costs 0.2263 Ir/call/digit and a
>    matched pair divides it by only the folded bytes, so a measured slope carries
>    `0.2263·Δ(Δdigits)/(bytes)` — **±0.09 Ir/byte on p16's shipped fold**. A
>    matched-spelling *difference* is exempt and exact, because both rungs print
>    the same checksum. Applies directly to §3 item 1's "Ir per search".
> 3. **RUN `./verus_run.py` ON AN R5 TWIN BEFORE DIFFERENCING ANY UNSAFE-SIDE
>    VARIANT.** p07 pins `identity` like every other pattern, and **a rung covered
>    by an `identity` pin is chained to the prover**: an R4 candidate that vstd
>    cannot express at the pinned version is not a rung, and its number means
>    nothing. This check would have caught five published figures across two
>    patterns over four tasks; it costs about eleven minutes. **Read the error
>    text, not the exit code** — `is not supported` disqualifies (it forces a new
>    *trusted* item); *"postcondition not satisfied"* disqualifies nothing.
> 4. **No pair interval.** §2 item 3 says "an interval, not a minimum" — correct
>    about the minimum, wrong about the interval. Both pair intervals this project
>    published were built from R4s that are not rungs. What p07 ships is the
>    **fixed-R4 bound** (`R3ship − R4ship`, R4 held by fiat) and an **R3-side
>    span**. If you search the R4 side and find it does not move, say so as
>    **"degenerate"** — the pair interval collapses onto the R3-side span — which
>    is falsifiable, where "unavailable" is not.
> 5. **Name the sweep band `sweep-*` and nothing else.** That prefix is the whole
>    mechanism (`check.py:459-460`, `measure.py:60`), and a band named otherwise
>    enters the measurement matrix. Appended last, a `sweep-*` band costs **a gate
>    re-run only, not a re-measure** — so §2 item 2 is cheap, and there is no
>    excuse for the p17 failure it exists to prevent. **Verify `gen.py` is
>    deterministic by regenerating twice and diffing**; the gate hashes `gen.py`
>    and never the blobs, so that determinism is the entire basis of the claim.
> 6. **`.memory/01-ladder.md`'s direction test is flagged BROKEN** with a
>    PROVISIONAL repair. Do not cite it for anything.
> 7. **Housekeeping now mandatory** (`.memory/00-environment.md` constraint 6):
>    delete your binaries and generated blobs once the gate is green, keep scripts
>    and notes. **Run measurements in the FOREGROUND** — background `nohup` jobs on
>    this box are reported "completed" while still running, which corrupted a data
>    point two tasks ago. Per-PID scratch paths.

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.memory/01-ladder.md` (findings 3–5 **and**
the named-spelling-standard block including the direction test),
`.memory/02-bench-rules.md`, `.memory/03-measurement.md`, `.memory/04-verus.md`,
`.memory/05-layout.md` ("Adding a pattern"), then **`patterns/p05-index-flatten/`
in full** — p05 is the template you clone (it is the most recent full build and
carries the idiom block in its mature form). Where this spec is silent, **do what
p05 did.**

TASK_025_REVIEW, TASK_027_REVIEW and TASK_028 have all landed. **Start now**, and
read §0 above first.

## Why this pattern, and why now

**Ten consecutive tasks (TASK_015–024) went to the spelling problem and produced
no new pattern.** That arc paid — the named-spelling standard, four refuted
floors, a sign error caught in p16's headline — but six patterns exist out of 47
and the ratio is now the thing to watch. p07 is the first pattern to be **built
to that standard natively** rather than retrofitted with it, and that is half the
point of doing it next.

The other half is scientific, and it is genuinely new:

**1. Every kernel this project has measured is a linear fold, and every one of
them amortises the safety cost to ~0 per byte.** p01, p02, p05, p08, p16 and p17
are all `for each byte: acc = f(acc, b)`. A per-call constant divided by `n`
bytes goes to zero, which is *why* "safety is cheap" keeps coming out. **Binary
search has `⌈log2 n⌉` iterations per call and no inner loop at all.** A
per-iteration bounds check is `O(log n)` per call against a kernel that does
almost nothing else, so the check is a large *fraction* rather than a vanishing
constant. If safety is still free here, that is the strongest form of the
project's main finding. If it is not, it is the first honest counterexample —
**and either way it is the first pattern where R3's cost cannot be amortised
away by making the input bigger.**

**2. It is the first kernel whose wall clock is set by branch misprediction.**
Binary search is *the* canonical unpredictable-branch benchmark. This directly
tests two of the project's own findings — *"static instruction counts are not a
cost model"* (finding 5) and *"`Ir` and wall clock can disagree in direction"*
(finding 6) — on a kernel designed to make them disagree, rather than on one
where they happened to. Expect `Ir` to be nearly rung-independent while `ns` is
not, which would be the sharpest evidence yet that this project must not publish
`Ir` alone.

**This box has `perf_event_paranoid = 3` and therefore no branch-miss counter**
(`.memory/00-environment.md`; still owed by the user). Do not let that stop you —
**it makes a control mandatory instead of optional**, which is better science
anyway. See §4.

## The bug class, and a claim in the catalogue I want you to check

`.memory/06-catalogue.md` lists p07's bug as **midpoint overflow `(lo+hi)/2`**.
**I think that is untestable on this box and I want you to settle it before you
build anything.** With `uint32_t` indices `(lo + hi)` wraps only above 2³¹
elements; with `size_t` it cannot wrap at any size that fits in RAM. And a
declared count large enough to reach it is rejected by the length check that
every rung must have. So either there is a spelling where it *is* reachable at a
testable size — find it and use it — or **the catalogue row is wrong and the
correction is a deliverable of this task.** Report which, with the arithmetic.

The reachable bug, and my proposal unless you refute it, is the classic C one:
**unsigned underflow of the upper bound.** `size_t hi = n - 1` with `n == 0`
gives `SIZE_MAX`, and `hi = mid - 1` with `mid == 0` does the same. The search
then reads far outside the buffer. It is realistic, it fires at `n = 0`, and it
is a genuinely *different* shape from p16's (forward, unsigned, one step past the
end) and p17's (backward, signed, wrong-but-in-bounds): this one is an index that
is **wildly** out of bounds, so it should be the easiest bug in the project for a
sanitiser to catch and the hardest for a checksum to hide. Say in `NOTES.md`
whether that prediction held — a sanitiser row that fires on every build would be
the first in this project, and p02's whole result is that it usually does not.

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

### Window layout and semantics

```
byte 0..4     n       u32 LE      -- declared element count
byte 4..8     nq      u32 LE      -- number of queries to run in this window
data_start  = 8
avail       = len - 8
```

The elements are `u32 LE`, **sorted ascending**, `n` of them starting at
`data_start`; the `nq` queries follow them, also `u32 LE`. Write the generator so
the sortedness is a property of the *file*, not of the kernel — no rung sorts
anything.

```
if len < 8:                                   return 0
n, nq from the header
if n == 0 || nq == 0:                         return 0

# >>> THE CHECK. R1 omits exactly this line and nothing else. <<<
if 4*n + 4*nq > avail:                        return 0     # computed in u64/size_t

acc = 0
for q in 0 .. nq:
    key = load_u32(data_start + 4*n + 4*q)
    lo  = 0 ;  hi = n - 1                      # <-- the underflow site
    found = NOT_FOUND
    while lo <= hi:
        mid = lo + (hi - lo)/2                 # SPELL IT THIS WAY, see below
        v   = load_u32(data_start + 4*mid)
        if v == key:   found = mid ; break
        if v <  key:   lo = mid + 1
        else:          hi = mid - 1            # <-- the second underflow site
    acc = acc *64 31 +64 (found +64 1)
return acc *64 31 +64 (n *64 nq)
```

Load-bearing, do not "improve":

- **`nq` queries per window is what makes the per-call constant measurable.**
  One search per window would put the driver's own overhead on top of a kernel
  that executes ~40 instructions. Choose `nq` so the search dominates and say in
  `NOTES.md` what fraction of kernel `Ir` the loop accounts for — **derive it,
  do not assert it.**
- **The keys are drawn so that hits and misses are both present**, in a ratio you
  state in `gen.py`. A pure-miss workload takes the same path every time and a
  pure-hit one exits early; either would flatter one rung. State the ratio and
  keep it identical across all inputs used for a rung-to-rung comparison.
- **`mid = lo + (hi - lo)/2`, spelled exactly that way in every rung**, and it
  goes in the `idiom.required` list as a named token. It is the overflow-safe
  spelling; `(lo + hi)/2` is the `forbidden` one and it is the bug the catalogue
  claims. Pinning it means the midpoint question is settled by `grep`, which is
  the whole point of the standard.
- **`found + 1` is folded**, so a rung that returns a different index cannot
  produce the same checksum, and `n * nq` is folded so a rung that runs a
  different number of searches cannot either.
- Wrapping arithmetic throughout, as every prior pattern.

### Contract

```
requires:  off + len <= buf_len
ensures:   result == bsearch_fold(buf, off, len)
```

## What you must ship that p01 and p08 still owe

This is the part that makes p07 the first native-standard pattern. **All four
land in the first delivery, not in a later audit.**

1. **The `idiom` block, written before the cells** — `required`, `forbidden`,
   and a `why` carrying the byte-identical named-spelling-standard paragraph the
   other six share. Diff it against p05's to confirm it is byte-identical; the
   gate's stage 0b checks the mechanism, not the wording.
2. **A shipped sweep, from day one.** p17's *"+32 Ir/call flat"* became a
   published law from two bands that both happened to have `nsuf = 3`, because
   p17 ships no sweep inputs at all. `inputs/gen.py` must emit a sweep band over
   `n` (and therefore over `⌈log2 n⌉`), and `gen.py` is inside `source_sha256`,
   so the law is re-derivable from a hashed file. **Sweep two full cycles of
   whatever modulus the codegen chose; never sample two points.** Note that for
   this kernel the natural axis is `log2 n`, so include the powers of two **and
   the values just below them**, where the trip count steps.
3. **An in-contract spelling spread, published as an INTERVAL and never as a
   floor.** Four floors have been published on this project and four were
   refuted, each by the first lever the next agent pulled. Give a pair interval
   with the shipped pair located inside it. If you find yourself writing the word
   "minimum", write "cheapest found" instead.
4. **Every per-element or per-iteration rate quoted with the spelling that
   produced it.** TASK_024 measured p16's per-byte rate ranging 5.04688…6.62500
   across six admissible folds of one kernel, and a rate differenced across two
   *different* spellings put a sign error in p16's headline. That rule is under
   review at TASK_025_REVIEW; **apply it regardless, and if the review has
   invalidated it by the time you read this the manager will tell you.**

## What to measure that no prior pattern could

Beyond the standard table, these are the deliverable:

1. **`Ir` per *search* and `ns` per *search*, both swept over `n`, plotted
   against `log2 n`.** The prediction to test: `Ir` is linear in `⌈log2 n⌉` with a
   rung-dependent slope, and that slope *is* the per-iteration safety cost — the
   first per-iteration rather than per-byte number in this project.
2. **The branch control, which is mandatory here** because the box has no
   branch-miss counter. Build a **branchless** variant of the *same* rung — the
   standard `cmov` formulation, `lo += (v < key) * (mid + 1 - lo)` or equivalent,
   confirmed `cmov` in the disassembly rather than assumed — and measure it
   against the branchy one at the same `n`. The gap between them at fixed `Ir` is
   your branch-misprediction signal, inferred by construction rather than
   asserted. **Report both, and say explicitly that this is an inference and what
   it rests on.**
3. **The `Ir`-vs-`ns` disagreement, stated as a direction.** If two rungs execute
   within a few instructions of each other and differ measurably in `ns`, that is
   the result. If they do not, say so — a clean null here is worth as much,
   because it would mean binary search is *not* the counterexample I am
   predicting and finding 5 rests on p01/p02 alone.
4. **Whether R3's cost amortises.** Every prior pattern's answer was "yes, to
   zero, per byte". State p07's as a function of `n` and say whether it goes to
   zero, to a constant, or grows.
5. **No cycles/element unless you measure the clock interleaved with the wall
   reps** (`.memory/00-environment.md`). ns is a measurement on this box; cycles
   is an inference that spans ±15% within one session.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, `n` a few hundred | perf row |
| `large` | past L2, `n` large enough that the search misses cache | perf row; the interesting one, because the tree walk is pointer-chasing-like |
| `sweep-n*` | the `log2 n` band of §2 above | the swept laws |
| `adversarial-zero` | `n == 0` with `nq > 0` | **the bug**: `hi = n - 1` underflows; R1 must read far out of bounds and ASan must fire |
| `adversarial-count` | `4*n + 4*nq` far exceeding `avail` | the omitted check; R1 walks off the end |
| `adversarial-unsorted` | data *not* sorted | every rung must stay in bounds and agree with `model.py`; this is a correctness-not-safety row and it is here to show the difference |

Adversarial rows are **exactly one window** (`n_blob == stride`), for the reason
p16, p17 and p05 all record: `k` is pseudo-random, so with several windows the
malformed one is hit probabilistically and an overrun from a middle window stays
inside the allocation.

**Window 0 must serve something** — a window returning 0 pins `acc` at 0 and the
driver's Lemire index `k = (acc*nwin) >> 64` then has an absorbing state at 0.
Check your generated inputs actually visit the windows you think they do.

Miri budget: 180 s per input. Binary search touches few bytes per call, so Miri
should be *cheap* here for the first time — p01's `large.bin` is the only blocked
row in the project. Report the actual Miri wall time; if p07 is cheap enough to
Miri at `large`, say so, because it is evidence about the policy.

## Done when

The p05 checklist, unchanged, plus §2's four items and §3's five. In particular:
a complete green `check.py p07`; checksums against an independent `model.py`; the
adversarial table **per rung** with `adversarial-zero` firing ASan on R1; the
decomposition naming a loop with **R3 quoted first**; two proof mutants failing
the gate; the TCB tally; the `#[cfg(slb_twin)]` twin with
`verus.twin_obligations` **and its arithmetic written out**; an
`SLB-TRUSTED-ARGUMENT` block with labels (a)(b)(c) ≥200 chars; and an explicit
statement of whether the twin is idle (it will be, if the accessor is
single-clause — say so; do not manufacture a multi-clause one).

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error is the deliverable for that row, not a gap. Expect the loop invariant
`lo <= hi + 1 && hi < n` and the termination measure `hi - lo` to be the work;
`.memory/04-verus.md` and p05's nonlinear lemmas are the starting point. A
binary search invariant is a *classic* Verus exercise, so if it stalls, the
sticking point is likely to be the `usize` underflow reasoning at `mid = 0`,
which is also the bug — say so precisely, because "the proof is hard exactly
where the bug is" would be a finding.

## Constraints

No root; no `/tmp` (scratch `.temp/p07/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; the manager lands them); do not
touch `harness/` or `common/` — if p07 seems to need a change there, **stop and
report it**. Do not edit any existing pattern's sources. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill. Per `.memory/00-environment.md` constraint 6, **delete your
binaries and generated blobs when your gate is green and keep your scripts,
notes and results** — `.temp/` was swept from 12 GB to 574 MB on 2026-08-18 and
the rule applies to everyone now.

Notes to `.temp/p07/NOTES.md` as you go, so you can be resumed if you die to a
transient API error. Two consecutive agents on the previous arc did.

**If a prescription here is wrong, say so with the measurement.** Thirty-one
agents have contradicted the manager's written instructions and all thirty-one
were right. The two things I am least sure of:

- **whether the catalogue's midpoint-overflow bug is reachable at a testable size
  at all** (§"The bug class" — I think it is not, and I would rather be told than
  have you build around it); and
- **whether binary search is branch-bound enough on this box to make `Ir` and
  `ns` disagree.** If `ns` tracks `Ir` here, p07 measures nothing new on that
  axis and I would rather change the kernel — a `nq`-query batch over a *shared*
  array is the fallback that increases cache pressure — than publish a null I
  designed for.
