# TASK_047 — p06, in-place rotate: the first safety line that is a DIVISION, and the first bug that safe Rust reproduces bit-for-bit on a WRITE

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` — **finding 5 (p17, the limit)**, **finding 11
(p09)**, **finding 12 (p12)**, **finding 3's two-step-reslice paragraph**, and
**the direction-test section's "IT FIRED" block in full, including the
three-row disposition table** — then `.memory/02-bench-rules.md`'s *"A WRITE bug
forces the adversarial row"* section (**p06 is a write bug; work out from the
THRESHOLD rule whether it inherits, and say which**), `.memory/03-measurement.md`,
`.memory/04-verus.md`, `.memory/05-layout.md`, then **`patterns/p12-strcat-fixed/`
in full** — p12 is the template you clone (fixed-size local destination, a write,
magnitude-dependent harm). Where this spec is silent, **do what p12 did.**

## Why this pattern

**1. Every safety line measured on this project so far is a compare-and-branch.
p06's is a division.** The kernel rotates a scratch array left by an
attacker-supplied `r`; the line C omits is `r %= m`. On this box a `div` is
**1 `Ir` and ~20–40 cycles**, so p06 is the first pattern where the project's
primary metric *understates the safety tax by construction, with a known
mechanism*. Finding 6 says `Ir` and wall clock can disagree in direction; every
instance so far was an accident. **This one is designed, and it is the most
useful methodological result p06 can produce** — it is the case where quoting
`Ir` alone would mislead, which is the sharpest available check on how every
other pattern here reports.

**2. It is the first bug whose harm safe Rust reproduces BIT-FOR-BIT on a
write.** p17 is the project's "limit" result and it is a *read*. p06's
destination is a fixed `[u32; SCR]` local, so for `m <= r < SCR` the unreduced
rotate stays **inside the array**: C, safe Rust, unsafe Rust and the proved rung
all print the **same wrong answer**, no sanitizer fires, nothing panics. Only at
`r >= SCR` does it leave the array and Rust panic. **Two regimes of one bug,
separated by a constant, one of them invisible to the entire ladder.**

**3. And it is where `_msonly` finally has something to discriminate.** The
functional `ensures` (*the result is `old` rotated left by `r mod m`*) rejects the
buggy kernel in **both** regimes; the memory-safety-only spec accepts it in
regime 1. Every prior `_msonly` mutant tested the machinery on a constructed
mutation. **This is a shipped, realistic bug on which the two specs disagree** —
and it is the complement of p09, where the bug went invisible *even to the spec*
once the spec moved with it. Say so against p09 by name; do not re-derive it.

**4. Safe Rust cannot express the C spelling at all, and the standard library's
own `unsafe` is what stands in.** Two pointers walking toward each other into one
buffer is inexpressible in safe Rust. R2 must index, R3 must use `swap` or
`split_at_mut`, R4 does the split with raw pointers, R5 proves the disjointness.
**The same disjointness fact, discharged four ways, with four different trusted
bases** — no pattern here has that, and it is a TCB result rather than a speed
one. Report the TCB of each, and note explicitly that R3's is *`std`'s* `unsafe`,
not zero.

## Kernel contract

| Rung | Signature |
|---|---|
| R1, R1h | `uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off, size_t len)` |
| R2/R3/R4/R5 | `fn kernel(buf: &[u8], off: usize, len: usize) -> u64` |

```
byte 0..4    nrec   u32 LE      -- number of records
data_start = 4
each record:  u32 LE nelem ; u32 LE r ; nelem * (u32 LE element)
SCR = 64                        -- elements; a compile-time constant in every rung
```

```
if len < 4:                        return 0
nrec from the header
if nrec == 0:                      return 0

scr: [u32; SCR] = ZEROED           # zero-initialised, every call, every rung
acc = 0 ;  p = data_start
for rec in 0 .. nrec:
    if p + 8 > len: break
    nelem = u32le(buf[off+p ..]) ; r = u32le(buf[off+p+4 ..]) ; p += 8
    m = min(nelem, SCR)                        # clamp into the scratch
    if p + 4*nelem > len: break
    copy m u32s from buf[off+p ..] into scr[0..m]      # bulk, in EVERY rung
    p += 4*nelem

    # >>> THE SAFETY LINE. R1 omits exactly this and nothing else. <<<
    if m != 0 { r = r % m } else { r = 0 }

    # --- the kernel: rotate scr[0..m] left by r, as three in-place reverses ---
    reverse(scr, 0, r)                         # [0, r)
    reverse(scr, r, m)                         # [r, m)
    reverse(scr, 0, m)                         # [0, m)

    # --- the fold: ORDER-SENSITIVE, full extent of the live region ---
    for i in 0 .. m:  acc = acc *64 31 +64 (scr[i] as u64)
    acc = acc *64 31 +64 (m as u64)
return acc *64 31 +64 (nrec as u64)
```

Load-bearing, do not "improve":

- **`scr` is a fixed-size local of `SCR` elements in all eight rungs**, never an
  allocation and never a length from the file. It is **zero-initialised on every
  call in every rung** — that is what makes regime 1 deterministic and identical
  across rungs, which is the finding. `.memory/02-bench-rules.md` already
  measured this shape as p12's counter-design; you are shipping it.
- **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
  every call must return the same value; the scratch copy is what makes an
  in-place pattern legal here at all. State this in `spec.md`.
- **The load into the scratch is the SAME bulk spelling in every rung** —
  `memcpy` in C, `copy_from_slice` in Rust, the trusted wrapper in R5. The
  measured difference must be the *rotate*, not the load. ⚠ p13's review blocker
  3: **list the libc routines each rung calls beside every kernel-exclusive
  figure**, and say which column each figure uses.
- **The fold is over the whole live region `scr[0..m]`, in order.** Order-sensitive
  is not optional here: three reverses compose to a **permutation**, so the buggy
  and correct results are the *same multiset* and a sum- or xor-fold cannot tell
  them apart. **Say that in `NOTES.md` as a second, independent reason for the
  full-extent fold rule** — TASK_004_REVIEW's reason was elision; this one is
  invariance.
- Wrapping arithmetic throughout.

```
requires:  off + len <= buf_len
ensures:   result == rotate_fold(buf, off, len)
```

## What to measure

1. **The safety line's price in both metrics, and the gap between them.** `R1h −
   R1` is one `div` per record. **Pre-register the prediction** (`Ir`: +1–3 per
   record; cycles: 20–40× that) and report both columns side by side. Then
   **span the safety line itself**, which no pattern here has done — R1h is
   normally the only hardened spelling, but this one has at least three:
   `r %= m` · `if (r >= m) r %= m;` · `while (r >= m) r -= m;`. On perf inputs
   (`r < m` always) the second predicts a predicted-not-taken branch and **near
   zero**. If that holds, p06 ships a **hardening-side span** and the honest
   headline is the cheapest in-contract hardening, not the textbook one.
   `.memory/02-bench-rules.md`'s two-number rule applies unchanged: publish the
   fixed spelling *and* the cheapest found, both labelled, with the input named.
2. **Whether R2's per-iteration checks cost the bulk lowering — p12's finding 12,
   on a different kernel.** R2's indexed swap is 4 checks per iteration on a
   two-cursor loop. Predict R2 fails to vectorize and R3/R4/R5 do, and that
   R2's gap therefore grows **linearly in the rotated extent** rather than being
   O(1) per call. **If it replicates, that is p06's second result** — this
   project has no replication of finding 12 and needs one. If it does not,
   that is a stronger result; say which.
3. **The rotate amount should not matter.** Three reverses cost
   `r + (m − r) + m = 2m` element-swaps regardless of `r`, so the law predicts
   **no `r` term at all**. Hold `m` fixed and sweep `r` across `[0, m)`: a
   coefficient on `r` that is not zero means the three-reverse decomposition is
   not what is executing (LLVM may recognise and rewrite it). Falsifiable, cheap,
   and it is the pre-registered prediction for the sweep.
4. **The two regimes, separated per rung.** `m <= r < SCR` (in-array, every rung
   agrees, nothing fires) and `SCR <= r` (out of the array; expect p12's
   magnitude-dependence — silent, canary, SIGSEGV, differing by compiler).
   **Separate adversarial rows and separate table columns**; merging them would
   merge a memory-safe wrong answer with a memory-safety failure, which is the
   distinction p17 exists to make. Prove regime 2 with ASan/UBSan per rung.
5. **The full protocol before any `ns` claim** — `common/layout/order.py` for the
   identical-copy floor (⚠ pass `--input small`, **not** `small.bin`; it appends
   the suffix), and **subtract `t(n_iters = 1)`**. Item 1 is a wall-clock claim by
   construction, so this is not optional on p06; it is the pattern's headline.

## Inputs

| stem | shape | purpose |
|---|---|---|
| `small` | L1-resident, every `nelem <= SCR`, every `r < m` | perf row |
| `large` | past L2, different `m` distribution, every `r < m` | perf row |
| `sweep-m*` | rotated-extent band at fixed `nrec` | the `2m` law |
| `sweep-n*` | `nrec` band at fixed `m` | the per-record constant |
| `sweep-r*` | **`r` band at FIXED `m`** | item 3's falsifier |
| `sweep-x*` | **every regressor non-zero at once**, with a within-band negative control | p04's band X; `.memory/03-measurement.md`, *"a law is a law in somebody's counts"* |
| `adversarial-inarray` | `m <= r < SCR` | regime 1 — **every rung prints the same wrong answer** |
| `adversarial-past` | `r >= SCR`, magnitude swept | regime 2 — the OOB write |
| `degenerate` | `m == 0`, `r == 0`, `r == m`, `nelem > SCR` | `m == 0` is a **division by zero** in the hardened rung; decide and pin the answer |

Adversarial rows are **exactly one window** (`n_blob == stride`); **window 0 must
serve something**. Name sweep bands `sweep-*`, appended **last**.

⚠ **Report the rank of your pooled design before measuring**, and **hold out a
LENGTH, not a mixture** — p13's out-of-sample test could not fail because every
held-out row was a linear combination of the fit rows. **Leave-one-`m`-out is the
real test here.** Make at least one band length-heterogeneous; queue item 11 says
no pattern has one, and p06's `nelem`-varying records are the natural place.

## Done when

The p12 checklist, plus §"What to measure" 1–5. Complete green `check.py p06`;
checksums against an independent `model.py`; the adversarial table **per rung**
with the two regimes in separate columns; the `idiom` block written **before**
the cells, **every entry backticked** (a bare-string entry is audited zero
times — `check.py:929`), shared paragraph byte-identical; a shipped sweep with
its **fitter committed under `controls/`**; an in-contract **R3-side span**
("cheapest found", **name the input**); two proof mutants failing the gate,
**one of them the `_msonly` mutant carrying the real bug** (§"Why this pattern"
3 — that is the mutant that earns its keep); **the declared TCB equal to the
gate's own `tcb_items` total**, with R2/R3/R4/R5's four different trusted bases
for the *same* disjointness fact tabulated.

**Try the two-step reslice** (`.memory/01-ladder.md` finding 3) on R3 from the
start — worth `−1 Ir/call`, zero `unsafe`, zero TCB, untried on every pattern but
p04, and p06's R3 opens with exactly the reslice it improves. It is the cheapest
outstanding correction on the project; landing it here also tells us whether it
generalises.

**Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
variant.** ⚠ And read the direction-test block's last paragraph: *"before blaming
vstd for an unsearched R4 side, run `./verus_run.py`"* — the R4-is-chained-to-the
-prover mechanism is real **and is the most available wrong explanation on this
project**. It cost p13 the magnitude of its headline.

⚠ **If you scope an idiom entry to some rungs and not others, PRICE IT.** That
is p13's blocker 1 and the newest rule in `.memory/01-ladder.md`: build the
excluded spelling on the excluded rung, measure what the exclusion is worth, and
**publish the price beside the number it protects**. p06 will be tempted to
scope — `<[T]>::reverse()` is a library call and belongs in a controls axis, not
in R3's shipped spelling, and `swap` is not available to R1 — and a *scoped*
entry silently makes the two sides of the comparison unequal where a whole-pattern
exclusion does not. Three of p13's scoped entries priced three different ways;
**price each of yours and dispose of it on what the price says.**

**Budget: one session for R5.** A stalled proof reported with its exact Verus
error IS the deliverable. Expect the work to be the **permutation `ensures`**: a
two-cursor loop whose invariant relates the already-swapped and not-yet-swapped
regions, then three of them composed into a rotation. `&mut [T]` is established
(`.memory/04-verus.md`: `old(dst)@` / `final(dst)@`, `dst[i] = v` has an
`IndexSetTrustedSpec`); there is **no** vstd spec for a bulk copy, so the load
needs the trusted wrapper p13 and p02 already use. **If the full rotation
`ensures` does not converge, ship the reverse `ensures` and report the gap** —
but do not silently weaken it to panic-freedom, which is `_msonly` and is the
thing p06 exists to distinguish from.

## Constraints

No root; no `/tmp` (scratch `.temp/p06/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p06
seems to need a change there, stop and report it**. Do not edit any existing
pattern's sources. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** `harness/measure.py --check-stale` after measuring. Delete binaries
and blobs once the gate is green; **keep every generator**.

Notes to `.temp/p06/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Sixty-four
agents have contradicted the manager and all sixty-four were right — p13's
engineer did it six times building the pattern and six more landing the review,
including one that would have published a number for a rung the tree does not
contain. **Settle these three before building five rungs on them**, the way
p04's §0 did:

- **Whether the three-reverse decomposition survives the optimiser.** If LLVM
  or gcc recognises the triple and rewrites it — to a `memmove`-style block
  rotate, or `std::rotate`-shaped code — then item 3's law is measuring
  something else and the `r`-coefficient will not be zero. **Disassemble one
  cell before generating a hundred blobs.** If it is rewritten, that is itself a
  finding (and a library axis arrives uninvited), but I need to know early
  because it changes every band.
- **Whether the `div` is even reached at `-O3`.** `r` is loaded from the file, so
  it should not fold — but if LLVM proves `r < m` from the *file's* structure it
  cannot, and if it instead turns `%` into a multiply-shift sequence (it can only
  do that for a **constant** divisor, and `m` is runtime) item 1's whole premise
  changes. **This is the prescription I am least sure of**: p06's entire
  methodological headline rests on the safety line being a real hardware divide,
  and on `Ir` counting it as ~1. **Measure the `Ir` delta AND the cycle delta on
  a single record before anything else** — if the gap is not there, say so and
  p06 becomes an ordinary compare-and-branch pattern with a good aliasing story,
  which is still worth building.
- **Whether regime 1 is actually identical across all eight rungs.** The claim
  in §"Why this pattern" 2 is the pattern's strongest, and it depends on the
  zero-init making the read of `scr[m..r]` deterministic in C *and* on Rust not
  panicking anywhere in `[m, SCR)`. **Build the adversarial blob and run all
  eight cells before writing a word of it.** If any rung diverges, the finding
  is the divergence and the headline changes.
