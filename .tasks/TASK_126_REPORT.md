# TASK_126 — no input can separate the Rust rungs, and the reason is not the one the manager guessed

**Role: research engineer. Deliverable: a measurement and a verdict.** No
pattern built, no catalogue row added. Everything under `.temp/t126/`
(scripts + logs kept, blobs and binaries deleted — they are regenerable by
`fuzz.py` and `harness/build.py`). Nothing under `.memory/`, `RECAP.md`,
`results/`, `patterns/` was touched; `git status` clean at start and finish; no
`git add`/`git commit` run.

---

## §A VERDICT — **STRUCTURALLY IMPOSSIBLE, and finding 43's second reading is MIS-STATED rather than merely untested**

> **No input can make two of `safe_naive` / `safe_tuned` / `unsafe` / `verus`
> disagree, and the reason is not that the harm inputs are too weak. It is that
> in this ladder's shape the adversarial input CANNOT REACH the Rust rungs'
> difference: the kernel's precondition is a THEOREM ABOUT THE DRIVER and its
> postcondition is a TOTAL FUNCTION of the window, so an "adversarial" input can
> only change bytes INSIDE a window every rung is already correct on.**

⚠⚠ **The manager's guess is HALF RIGHT, and the half that is WRONG is the half
that would have made finding 43 a tautology.** Measured with the gate's own
instrument (`harness/asm.py:identity_level`), all six pairs, both opt levels,
26 patterns — `.temp/t126/rung_asm_identity.py`, log
`.temp/t126/rung_asm_identity.log`:

```
   safe_naive  vs safe_tuned   {'differ': 52}   SAME MACHINE CODE in  0/52
   safe_naive  vs unsafe       {'differ': 52}   SAME MACHINE CODE in  0/52
   safe_naive  vs verus        {'differ': 52}   SAME MACHINE CODE in  0/52
   safe_tuned  vs unsafe       {'differ': 52}   SAME MACHINE CODE in  0/52
   safe_tuned  vs verus        {'differ': 52}   SAME MACHINE CODE in  0/52
   unsafe      vs verus        {'norel': 26, 'exact': 26}  SAME MACHINE CODE in 52/52
MUST-FIRE ARM: p16 safe_naive vs p13 safe_naive at O3 -> 'differ' OK
```

- ✅ **RIGHT: `unsafe` ≡ `verus`, 52 of 52** (pattern × opt). Two of the "four
  rungs" are one program and cannot ever differ. ⚠ **"byte-identical" is too
  strong** — 26 of 52 are `exact`, 26 are `norel` (the same machine code at a
  different link address), and `md5_raw_equal` is **false in 25 of 26 at O0**.
  ⚠ **And `norel` is not, on its own, a proof of behavioural identity**: it
  masks pc-relative displacement fields, so two `norel`-equal functions could in
  principle reach different data — the exact trap `TASK_124` §B0 hit with panic
  `&Location`. The claim survives anyway because the O3 half is `exact`, the
  exec code is the same source text, and 129 + 13 449 inputs agree; but it
  should be stated as *"the same machine code"*, not *"byte-identical"*.
- ⚠⚠ **WRONG: `safe_naive` vs `safe_tuned` is `differ` in 52 of 52.** They are
  not the same program by any instrument this project owns. **So the R2-vs-R3
  zero is a MEASUREMENT, not a tautology, and the manager's "they differ in
  spelling and not in semantics" is not supported by identity.**

⚠⚠ **The honest statement is therefore: THE TREE HAS THREE BEHAVIOURAL RUST
RUNGS, NOT FOUR AND NOT TWO.** Finding 43 quantifies over four things of which
two are one. That is a real overcount and it should be corrected — but it is
**not** the whole answer, and the answer that *is* the whole answer is below.

### A1 — the mechanism, and it is stronger than the identity pin

From `results/gate/*.json`'s own `derived_contract` and `driver_loops`
(`.temp/t126/contracts.log`), across all 26 built patterns:

| fact | count |
|---|---|
| `requires` is `off + len <= buf_len` / `<= v_len` | **26 of 26** |
| any `requires` clause mentioning the buffer's **contents** | **0 of 26** |
| `ensures` is a single total value clause `result == <fold>(buf, off, len)` | 25 of 26 (p02 adds the destination-sequence clause) |
| `driver_loops[*].matches_pin` true for **every** rung file | **26 of 26** |

and the driver loop itself, which 24 of 26 patterns share verbatim:

```rust
if stride_w >= K && stride_w <= n_blob as u64 {
    let stride: usize = stride_w as usize;
    let nwin: u64 = (n_blob / stride) as u64;
    while it < n_iters {
        let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
        let r: u64 = kernel(buf, k * stride, stride);
```

`k < nwin` (a u64×u64 product shifted right 64 is strictly below the
multiplier); `nwin * stride <= n_blob`; therefore
`off + len = k*stride + stride <= n_blob`, with **no intermediate that can
overflow**. ⚠ **The window bound is a theorem about the driver, not a property
of the input** — and the driver is `common/driver.rs` plus a token-identical
pinned loop, i.e. **the same code in all four Rust rungs**.

So the chain is:

1. `common/driver.rs` rejects every malformed *file* identically in all four
   rungs (`EXIT_TRUNCATED`, `EXIT_CAP`, `EXIT_HEADER`, …) — the kernel is not
   reached at all.
2. The pinned driver loop then guarantees `off + len <= buf_len` **on every
   call, on every input**. `check.py` stage 5d re-derives this through
   `model.py` on *every* input, adversarial included, and stage 5b makes Verus
   discharge it at R5's call site — every record carries a non-zero
   `verified_call_site` for **both** `main` and `kernel`, **26 of 26**
   (`{"main": 4..5, "kernel": 2..5}`).
3. `.memory/02-bench-rules.md` **requires** the precondition to be structural
   ("these hold on *every* input the benchmark runs, adversarial included") and
   the security property to live in the `ensures`. The `ensures` is a **total
   function of the window contents**.
4. `.memory/01-ladder.md` requires R4 to be **correct**, just unverified.

⇒ **An adversarial input can change only the bytes inside a window that all four
Rust rungs are contractually total on.** The thing that makes the input
adversarial — the missing check — exists **only in `c/kernel.c`**, whose
signature does not even carry the length (p01's own `required[1]`: *"the C
kernel takes (v, off, len) and has no length to check; the Rust kernels take
`&[u64]`, i.e. a pointer AND a length"*).

⚠⚠ **So finding 43's second reading — *"the harm inputs are not adversarial
ENOUGH"* — presupposes that an input COULD be adversarial to a Rust rung. Under
this ladder's shape it cannot be.** The only way to separate two Rust rungs is a
**bug in one of them**, which would be a defect report, not a stronger input.
**More adversarial inputs is not the fix, and it would buy nothing.**

### A2 — the empirical arm: 13 449 fresh inputs, zero Rust splits

`.temp/t126/fuzz.py --all --n 200`, logs `fuzz_all2.log` (O0/O3) and
`fuzz_o0d.log` (debug-assertions ON). Existing binaries run by hand; **no rung
source, `model.py` or `inputs/gen.py` touched**. Four blob families per pattern:
the pattern's own inputs with `n_iters` shrunk; structured extremes (payload
0–128 B × five fill bytes); header extremes (`n_iters` and `payload_len` at u64
boundaries, including `payload_len` lying about the file); random mutations of
the pattern's own adversarial seeds; uniform random payloads.

```
TOTAL fuzz inputs=13449  with ANY rung split=600  with a RUST-rung split=0
```

Per-`(opt, mode)` splits (the strictly stronger question — same config, four
rungs) are also **0** on every pattern.

**MUST-FIRE ARM A** — the same comparison over each pattern's own **committed**
adversarial blobs must reproduce the gate's recorded divergence count. **It does
exactly, on all 26 patterns, summing to 58 of 129**: 0/6, 3/7, 2/4, 1/3, 2/4,
4/5, 2/5, 0/4, 2/3, 2/4, 2/5, 3/6, 4/7, 4/5, 1/3, 4/6, 3/5, 3/5, 1/5, 5/6, 3/4,
2/4, 3/5, 0/10, 2/4, 0/4. The detector is calibrated against ground truth
before it is trusted on a null.

**MUST-FIRE ARM B** — two different programs on one blob must split: p16 vs p13
`safe_naive` → `11490021019115224707` vs `8858342074384302231`. ⚠ **The FIRST
version of this arm FAILED, and the arm was wrong, not the detector**: its blob
made both programs print `0` because neither driver guard admitted it. Recorded
in the script rather than quietly repaired.

**Clean negative worth having: it is not the build flags.** The measured matrix
builds Rust at `debug-assertions=off` at *both* opt levels, which erases exactly
the class of divergence safe Rust is famous for (integer overflow). So I built
the out-of-matrix `--opt O0d` cells (debug-assertions **ON**) for all 26
patterns and re-ran the identical corpus: **13 449 inputs, 0 Rust splits, and
ARM A still fires on 21 of 26 patterns.** (`p38` drops out at O0d because its C
divergence needs `-O3`.)

### A3 — ⚠⚠ NO RUST RUNG IN THIS TREE HAS EVER PANICKED

"No split" is not "no panic" — four rungs panicking identically would also read
as zero. So the fuzz tallies every Rust process run:

```
RUST behaviour tally over every Rust process run (107592 runs), keyed (exit, has_stderr):
   (0, False) -> 103496
   (7, True)  ->   3472        EXIT_CAP,       common/driver.rs
   (5, True)  ->    624        EXIT_TRUNCATED, common/driver.rs
   runs with an exit code that is NOT 0 / 5 / 7: 0
```

and the same is true of the committed gate records (`.temp/t126/rust_exits.log`):

```
RUST adversarial rows: 516; rows with exit!=0 or stderr!='': 24
  (exit, has_stderr): {(0,False): 492, (5,True): 20, (7,True): 4}
NON-RUST rows: 582; with exit!=0 or stderr!='': 62
  (exit, has_stderr): {(0,False):520, (5,True):19, (-6,True):8, (7,True):4,
                       (-11,False):29, (None,True):2}
```

⚠⚠ **All 24 non-zero Rust rows are the SHARED DRIVER refusing a malformed FILE
before the kernel is called. Not one is a panic.** On the same inputs the C
rungs contribute **29 SIGSEGVs, 8 aborts and 2 non-terminating runs**.

> **The harm column is 29 segfaults + 8 aborts + 2 hangs, and every one of them
> is in C. The Rust half of it is 492 identical checksums and 24 identical
> driver refusals.**

### A4 — nondeterminism is ruled out explicitly, and it is worse than `TASK_125` said

`.temp/t126/nondet.py`, 8 repetitions per (pattern, adversarial input, rung,
opt, mode), must-fire arm = a clock must read as unstable:

```
cells probed: 4080     UNSTABLE cells: 59     of which RUST rungs: 0
```

⚠ **The unstable cells span SEVEN patterns, not the two `TASK_125` named:
`p03` (16), `p27` (16), `p05` (8), `p23` (8), `p13` (4, `c-clang O0/whole`
only), `p38` (4, `c-gcc O3` only), `p06` (3).** All C. **Zero Rust cells moved
in 8 runs.** So no apparent Rust split was masked or manufactured by garbage
reads, and the `N distinct behaviours` notes-line churn has a wider footprint
than recorded.

---

## §B — THE CENSUS ITSELF. Two real defects, neither changes the zero

`.temp/t126/census2.py`, log `census2.log`.

```
TASK_124 exactly   (exit, signal, stdout), last row only
   inputs=129  any-divergence=56  RUST-divergence=0
+ all rows         (exit, signal, stdout)
   inputs=129  any-divergence=58  RUST-divergence=0
+ stderr           (exit, signal, stdout, stderr)
   inputs=129  any-divergence=58  RUST-divergence=0
+ hung             (exit, signal, stdout, stderr, hung)
   inputs=129  any-divergence=58  RUST-divergence=0
```

**B1 — what the gate captures.** `check.py:3362-3381` keys the behaviour set on
`(rc, out.strip(), err.strip()[:120], sig)` and writes rows carrying
`exit / stdout / stderr / signal / cells / hung / diverges`. **`stderr` IS
recorded (first 120 chars).**

- ⚠ **Defect 1: `TASK_124`'s census dropped `stderr`.** MUST-FIRE ARM 2b plants
  a stderr-only divergence into a copy of a real record: the `TASK_124` field
  set reports `0`, mine reports `1`. **The census was blind to a whole channel.**
  It changes nothing here — the zero holds with `stderr` and with `hung`.
- ⚠⚠ **Defect 2, and it is the sharper one: `TASK_124`'s census OVERWRITES.**
  `.temp/t124/A/rung_split_census.py` does
  `for r in runs: by[inp][rung] = (...)`, so a rung whose `opt × mode` variants
  disagree contributes **only its last row**. That is the identical shape to the
  TASK_053 F1 sweeping-up defect that `check.py:3365-3373` exists to warn
  about, reintroduced in the tool built to audit it. ⚠ **`RECAP.md` finding 43
  attributes the `56` vs `58` gap to *"a grouping tie-break, not a dispute"* —
  it is right that there is no dispute and WRONG about the cause: it is a bug in
  the script, and the correct number is 58.** It could in principle have hidden
  a Rust split; it did not, because (B2) no Rust rung is ever multi-row.
- ⚠ Nothing is folded into a checksum that the record cannot show: stdout **is**
  the checksum, and it is recorded verbatim.

**B2 — are all four rungs run on every adversarial input? YES.**

```
   c-gcc        keys= 129  rows= 160        safe_naive   keys= 129  rows= 129
   c-clang      keys= 129  rows= 170        safe_tuned   keys= 129  rows= 129
   c-gcc-h      keys= 123  rows= 123        unsafe       keys= 129  rows= 129
   c-clang-h    keys= 123  rows= 123        verus        keys= 129  rows= 129
   safe_naive_verus keys=  6  rows=   6     (p01's R2v control only)
```

**The denominator is not inflated.** And **every one of the 36 rungs whose
`opt × mode` variants disagree is a C rung** — p02×2, p03×4, p05×2, p06×4,
p12×2, p13×8, p14×4, p23×2, p27×4, p38×3, p46×1. Not one Rust rung differs from
*itself* across the four builds either.

**B3 — `skipped_inputs` is empty in all 26 records.** No adversarial input is
skipped anywhere, and `check.py:8364` refuses `--skip adversarial*` outright, so
it cannot be.

---

## §C — the per-pattern harm-column quality number (`.temp/t126/quality.py`)

```
pattern                 adv  0call  1beh  dead  div  rustdiv
p01-array-sum             6      6     6     6    0        0
p02-buffer-copy           7      3     4     3    3        0
p03-bounded-stack         4      0     2     0    2        0
p04-ring-buffer           3      0     2     0    1        0
p05-index-flatten         4      1     2     1    2        0
p06-rotate                5      1     1     1    4        0
p07-binary-search         5      1     3     1    2        0
p08-overlap-move          4      1     4     1    0        0
p09-bitset                3      0     1     0    2        0
p10-fir-stencil           4      1     2     1    2        0
p11-nul-scan              5      1     3     1    2        0
p12-strcat-fixed          6      1     3     1    3        0
p13-strncpy-trunc         7      1     3     1    4        0
p14-field-split           5      1     1     1    4        0
p16-tlv-walk              3      1     2     1    1        0
p17-http-range            6      1     2     1    4        0
p18-varint-shift          5      1     2     1    3        0
p19-state-machine         5      1     2     1    3        0
p22-hash-probe            5      1     4     1    1        0
p23-partition             6      1     1     1    5        0
p27-handle-table          4      1     1     1    3        0
p36-vtable-dispatch       4      1     2     1    2        0
p38-alias-pun             5      1     2     1    3        0
p42-goto-cleanup         10      7    10     7    0        0
p46-bignum-mac            4      1     2     1    2        0
p47-ct-compare            4      1     4     1    0        0
TOTAL                   129     36    71    36   58        0
```

`0call` = `model.py` reports **zero kernel calls**; `1beh` = every cell in the
matrix behaves identically; `dead` = both.

⚠⚠ **36 of 129 adversarial inputs (27.9%) NEVER CALL THE KERNEL AT ALL.** They
exercise `common/driver.rs`'s guard, which is shared by every rung and is not
the pattern. **71 of 129 (55%) produce one identical behaviour in every cell of
the matrix.** ⚠ **And `dead == 0call` exactly: every zero-call input is also a
zero-signal input.**

⚠ **There is a template family behind most of it: `adversarial-strideN.bin`
appears in 22 of the 26 patterns and is 0-call in every one of them** — a stride
below the driver's `stride_w >= K` guard, so the loop body never executes. It
was inherited by cloning, and it is doing no work in 22 patterns.

**The two worst harm columns:**

- ⚠⚠ **`p42-goto-cleanup`: 10 adversarial inputs, 7 of them 0-call, ZERO
  divergences.** Eight of the ten print `0` in every cell, one exits 5 in the
  driver, one prints an agreeing checksum. **Nothing in p42's adversarial block
  exercises p42's bug at any rung.**
- ⚠ **`p01-array-sum`: 6 of 6 adversarial inputs are 0-call.** This is already
  written down in `.memory/02-bench-rules.md` as the thing that *hid* two
  earlier defects; it has never been counted as a quality number.
- `p08` (1 dead of 4, 0 divergences) and `p47` (1 dead of 4, 0 divergences) also
  publish a harm column with no differential content at all.

✅ **This is the cheap actionable result of the task, and it is orthogonal to
§A:** the C half of the harm column has 36 inputs that cannot fire and 71 that
do not, and fixing that costs one `inputs/gen.py` edit per pattern (a
re-measure, so batch it).

---

## What I did NOT do, and what I am unsure about

- **I did not run `harness/check.py`.** It was not needed and would have cost a
  sweep. `harness/measure.py --check-stale` → **52 record(s) examined, 0 STALE**,
  identical to the state at launch.
- **The fuzz searches the INPUT space, not the kernel-argument space.** That is
  the question as posed ("construct an input"), and the driver loop is pinned so
  the two spaces are related by a fixed map — but a reviewer should know that a
  hand-written call into a kernel with an out-of-range window would separate the
  rungs trivially, and that is *not* reachable from any input file.
- **My corpus is structural + random, not pattern-grammar-aware.** Family 3
  mutates each pattern's own adversarial seeds, which is the best proxy I had
  without writing 26 grammars. A grammar-aware fuzzer could in principle find
  something the structural argument says cannot exist; I would bet against it,
  and I would rather the structural argument be attacked than the corpus be
  enlarged.
- **`norel` is not literally byte-identity** (see §A). I record the caveat rather
  than smoothing it, because `TASK_124` was bitten by exactly this masking.
- **The O0d cells are outside the measured matrix** and I make no perf claim from
  them; they are a control for one hypothesis only.
- **I did not check whether `safe_naive_verus` (the R2v control, p01 only) can
  diverge from `safe_naive`** — the gate's own `identity` block already pins it
  `exact` at both opt levels, so it is a fifth copy of R2, not a fifth
  behaviour.
- **Two self-caught instrument defects, disclosed rather than repaired quietly:**
  (a) `census2.py`'s first `ROOT` was one directory short and the run returned
  `0 gate records` — **MUST-FIRE ARM 1 is what caught it**, which is the whole
  reason the arm exists; (b) ARM B's first blob made both programs print `0` and
  the arm reported the detector broken when the arm was broken.

## Answering the manager's three "least sure" calls

1. ⚠⚠ **"That the `identity` pin explanation is right." — HALF RIGHT, and I am
   stating the wrong half plainly as asked.** `unsafe ≡ verus` in **52 of 52**,
   so the census was comparing **three** things and calling them four — say that
   in finding 43. But `safe_naive` vs `safe_tuned` is `differ` in **52 of 52**,
   so the R2/R3 zero is **not** a tautology and *"the tree has two behavioural
   Rust rungs"* is **false**. It has three. **The reason no input separates them
   is the contract's totality plus the driver's window theorem, not the pin.**
2. ⚠ **"That a separating input would be a GOOD result."** Moot — there is none.
   And I would go further: **had I found one it would have been a BUG REPORT**,
   not evidence of a harm-matrix gap, because all four rungs are contracted to
   the same total function on the same window. I did **not** inflate anything
   into a retroactive claim about 26 patterns; §C's numbers are about the C half
   of the harm column and are stated per pattern.
3. ⚠⚠ **"That this is worth a task at all rather than a footnote." — It was
   worth it, and not for the reason the task file gives.** The §A hunt returned
   the null the manager expected. What paid for the task is everything around
   it: the rung count is wrong (four → three), the census that produced finding
   43 has two reproducible defects, and §C found **36 dead adversarial inputs
   across 22 patterns** that nobody had counted. ⚠ **The argument you offered
   (*"a claim with an untested alternative reading"*) is the right shape and it
   held.**

## Corrections owed to `RECAP.md` finding 43 (manager's edit, not mine)

1. *"THE FOUR RUST RUNGS"* → **three distinct programs**; `unsafe` and `verus`
   are the same machine code in 52 of 52 (pattern × opt).
2. *"58 … (TASK_124 counted 56 — a grouping tie-break, not a dispute)"* → **a
   defect in `rung_split_census.py`: it keeps only the last row per rung.** 58 is
   correct; 56 came from dropping rows.
3. The untested second reading — *"the harm inputs are not adversarial
   ENOUGH"* — should be **struck and replaced**, not left open: under this
   ladder's shape **no input can be adversarial to a Rust rung**, because the
   `requires` is structural, the driver proves it, and the `ensures` is total.
   ⚠ **Rule 9 split: the CONCLUSION (no input separates the Rust rungs; the
   fix is not more inputs) rests on 13 449 fuzz inputs, 107 592 Rust runs with
   zero panics, and the contract census. The MECHANISM I name (totality + the
   window theorem) is an argument I built from the gate's own records and it has
   NOT been reviewed — mark it OPEN.**
4. Worth adding: **the harm column's C half is 29 SIGSEGVs, 8 aborts and 2
   hangs; its Rust half is 492 identical checksums and 24 shared-driver
   refusals.**

## Tree state

- `git status` **clean** at start and finish. No `git add` / `git commit`.
- `harness/check.py` **not run** (would have cost a sweep; nothing needed it).
- `harness/build.py` run for all 26 patterns (the measured matrix) plus the
  out-of-matrix `--opt O0d` cells. Binaries live in `.temp/build/` as always.
- `harness/measure.py --check-stale`: **52 record(s) examined, 0 STALE**.
- `.temp/t126/` keeps every script and log; the 13 449 blobs and the two planted
  JSON records are deleted and are regenerated by `fuzz.py` / `census2.py`.

## Branch delta

Zero tracked files changed. One new file: `.tasks/TASK_126_REPORT.md`.
Everything else is under `.temp/t126/` (gitignored).

## Running count

`566 → 583`. ⚠ **Carrying, not re-adding; reconciliation is the manager's job.**
The seventeen:

1. no input separates the Rust rungs — 13 449 fresh inputs, 0 splits (§A2);
2. `unsafe ≡ verus` in 52/52 — the manager's guess confirmed (§A);
3. ⚠ but *"byte-identical"* is too strong: 26/52 `exact`, 26/52 `norel`,
   `md5_raw_equal` false in 25/26 at O0 (§A);
4. ⚠⚠ `safe_naive` vs `safe_tuned` `differ` in 52/52 — the manager's second limb
   REFUTED, the tree has **three** behavioural Rust rungs (§A);
5. the mechanism: `requires` structural in 26/26, never mentions contents;
   `ensures` a total function; the driver's window bound is a theorem (§A1);
6. therefore finding 43's second reading is mis-stated, not merely untested
   (§A1);
7. no Rust rung has ever panicked — 107 592 fuzz runs + 516 gate rows, 0 exits
   outside {0, 5, 7}, and 5/7 are the shared driver (§A3);
8. the harm column's C half: 29 SIGSEGV + 8 abort + 2 hang (§A3);
9. `TASK_124`'s census keeps only the last row per rung — 56 vs 58 is a script
   bug, not a tie-break (§B1);
10. `TASK_124`'s census drops `stderr`, and the gate does record it (§B1);
11. all four Rust rungs run on all 129 inputs; the denominator is honest (§B2);
12. all 36 multi-row rungs are C rungs; no Rust rung differs from itself across
    `opt × mode` (§B2);
13. `skipped_inputs` empty in 26/26 (§B3);
14. **36 of 129 adversarial inputs (27.9%) make ZERO kernel calls**, and
    `dead == 0call` exactly; 71 of 129 produce one identical behaviour (§C);
15. the `adversarial-strideN.bin` template family is 0-call in 22 of 26
    patterns (§C);
16. `p42` has 10 adversarial inputs, 7 of them 0-call and 0 divergences; `p01`
    is 6 of 6 (§C);
17. the nondeterminism footprint is **seven** patterns, not the two `TASK_125`
    named, and 0 Rust cells in 4080 (§A4).

Plus two self-caught defects in my own instruments (the `ROOT` path, caught by
MUST-FIRE ARM 1; ARM B's degenerate blob), disclosed in the scripts.
