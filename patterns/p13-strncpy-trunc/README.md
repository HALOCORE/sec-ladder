# p13 — `strncpy` truncation

**The first bug in this project that is a correctly-called library function**,
and the first whose harm lands at a **different site** from the bug.
`strncpy(dst, src, sizeof dst)` is textbook C, correct by the letter of its man
page, and still wrong: it does not NUL-terminate when the source is at least as
long as `n`, and the terminator a short string gets is a side effect of the
zero-*padding* rather than something the routine wrote on purpose.

```
window:  nstr:u32 LE, then packed NUL-terminated strings
kernel:  for each declared string
             q    = first NUL at or after p, capped at the window end
             slen = q - p
             n    = min(slen, DST_CAP)                  DST_CAP = 32
             copy buf[off+p .. off+p+n] into dst[0..n]
             zero-fill dst[n .. DST_CAP]                <<< strncpy's padding
             dst[DST_CAP - 1] = 0                       <<< R1 omits THIS LINE
             d = 0 ; while dst[d] != 0: d += 1          <<< UNBOUNDED in C
             acc = acc*31 + d
             for i in 0..DST_CAP: acc = acc*31 + dst[i] <<< FULL-EXTENT fold
         return acc*31 + nstr
```

## What is new here

- **The bug site and the harm site are different.** The copy writes exactly
  `DST_CAP` bytes into a `DST_CAP`-byte array on every input — it is memory-safe
  in R1 too. The out-of-bounds access is a **read**, of the *destination*, in
  the consumer. Every earlier pattern's bug fires where it is written.
- **The first two-site proof obligation.** R4/R5's consumer has **no bound at
  all**; what licenses the unchecked read is a fact about the array's
  *contents* — `dst@[DST_CAP - 1] == 0` — established by a different statement
  and carried across a store into a loop. p11 proved a scan terminates from a
  sentinel it was *given*; p13 has to establish one. `NOTES.md` 5a; deleting the
  store makes the proof fail rather than weaken (`NOTES.md` 9, M1).
- **One omitted line, two harms, at two expressiveness levels.** Truncation is a
  memory-safe wrong answer and **every** rung has it, R5 included; the missing
  NUL is an out-of-bounds read and **only R1** has it. `NOTES.md` 1a and 7.
- **The safety tax is a STORE, not a compare-and-branch**, and it is exactly
  **1.00000 `Ir` per string** on both compilers, on 57 blobs. `NOTES.md` 4a.
- **A bound the optimiser can SEE is worth 2.00000 `Ir` per consumed byte** —
  and the bounds check is one way of supplying it, so on this kernel *safety is
  net-negative because it is a check*. That is 73–91% of the safe-beats-unsafe
  margin, and it is p03's and p04's seeding result arriving from the other
  direction. `NOTES.md` 4c.
- **The first pattern whose rungs call DIFFERENT libc routines**, so the
  kernel-exclusive column is not comparable across them and two published
  figures move. `NOTES.md` 4b.
- **The safe library routine is the expensive one, on both compilers.**
  `strlcpy` always terminates and costs **+26.00 `Ir`/string** (gcc) / **+30.00**
  (clang) over `strncpy`; `snprintf` costs **+339.16** / **+343.00**.
  `NOTES.md` 3a.
- **Whether the bug is reproducible is a property of the binary, not of the
  compiler.** Three of `c-clang`'s four builds give different answers on
  different *runs* of the same binary; all four of `c-gcc`'s are stable — the
  exact reverse of what a two-kernel probe of the same source showed. No
  specific wrong answer is quoted anywhere, because none of them is a number.
  `NOTES.md` 0b and 7.

## Two things the task file asked for that turned out not to exist

- **An input on which truncation changes the answer while every rung stays
  memory-safe.** There is none: content is lost **iff** `slen >= DST_CAP` **iff**
  `dst` holds no NUL **iff** R1 reads out of bounds. The two harms fire on
  exactly the same inputs and separate **by rung**. What ships instead is a
  controlled triple — `adversarial-exact` (4×31 B), `adversarial-truncate`
  (4×32 B), `adversarial-truncate-alt` (4×40 B) — which destroys 0, 1 and 9
  bytes per string and prints **one checksum** in every checked rung, with the
  destination **byte-identical** across all three under a full-extent fold.
  `NOTES.md` 1a.
- **A `large` with a different truncation ratio from `small`.** Any truncating
  string puts R1 out of checksum agreement — and on some builds out of agreement
  with *itself between runs* (measured: 3 of `c-clang`'s 4). Both perf rows are
  0% truncating; the ratio axis lives in `sweep-t*` with R1 excluded.
  `NOTES.md` 1b.

## What it cannot do, and why that is a result

- **`Ir` has no exact linear cost law here** — the first pattern in this project
  of which that is true. `strncpy`'s two halves compile to size-dispatched
  vector code, so the per-string cost is a step function with a discontinuity at
  `slen == DST_CAP`. No law is published; the piecewise slopes are. ⚠ **Say
  which estimator**: exact interpolation and OLS disagree by up to 4.2× on how
  badly it fails. `NOTES.md` 8b.
- **p13's out-of-sample test could not fail, provably** — all 17 band-T rows lie
  inside the rank-5 fit set's row space, so band T is an interpolation check.
  Holding out a **length** instead gives residuals 2.7× to 95× larger.
  `NOTES.md` 8b.
- **R1's design is rank 3 of 5**, because among non-truncating rows `C == S − K`.
  ⚠ R1 *can* be measured on a truncating blob — its kernel `Ir` is bit-identical
  over reps — so the exclusion is policy, and the defensible reason is that its
  consumer reads 1–7 bytes that are not a regressor. `NOTES.md` 8a.
- **The margin depends on a fiat, and the fiat is published.** With R4's
  consumer allowed a bound, `R3 − R4` reverses to **+44 / +77 `Ir`/call**. The
  unbounded consumer is held by fiat because it *is* the pattern; the number is
  in the file so a reader can tell a language result from a contract artefact.
  `NOTES.md` 10c.
- **`strlen(` is `forbidden` in the declaration, absent from every source, and
  called by every C `-O3` cell** — both compilers turn the consumer scan into
  `strlen`. A text-level idiom pin constrains the source, not the object, and
  **p13 is the only one of thirteen patterns where the optimiser puts a
  forbidden routine back**. Priced with clang `-fno-builtin-strlen`: **the sign
  of every same-backend C-vs-Rust row flips**. `NOTES.md` 3d, 4d.

## Files

| file | what |
|---|---|
| `spec.md` | the contract, and the pins `harness/check.py` enforces |
| `model.py` | the independent Python reference (two implementations, cross-checked) |
| `inputs/gen.py` | deterministic input generation; `.bin` is gitignored |
| `c/kernel.c` | R1 — no termination store. **the bug** |
| `c/kernel_hardened.c` | R1h — one store, and that is the whole diff |
| `c/main.c` | the C driver loop |
| `safe_naive.rs` | R2 — indexed byte loops, indexed consumer (panics where C runs away) |
| `safe_tuned.rs` | R3 — two-step reslice, `copy_from_slice` + `fill`, `position` |
| `unsafe.rs` | R4 — `get_unchecked` / `get_unchecked_mut`, **unbounded** consumer |
| `verus.rs` | R5 — R4's exec code plus the proof |
| `controls/library_axis.py` | six copy routines × two `DST_CAP`s, one checksum |
| `controls/sweep_fit.py` | the design rank, the fits and the out-of-sample test |
| `controls/spellings.py` | the audited in-contract span, **both sides** |
| `controls/gen_bulk_r5.py` | the R4-side candidates' R5 twins, put through Verus |
| `controls/mutants.py` | four proof mutants and what catches each |
| `controls/oracle_hole.py` | the oracle hole the narrow fold left, and its repair |
| `NOTES.md` | what was measured |

## Running

```bash
python3 patterns/p13-strncpy-trunc/inputs/gen.py            # the 9 matrix inputs
python3 patterns/p13-strncpy-trunc/inputs/gen.py --sweep     # + the three sweep bands
python3 harness/check.py p13                                 # the gate
python3 harness/measure.py p13                               # the numbers
python3 patterns/p13-strncpy-trunc/controls/sweep_fit.py --rank   # design rank, no measuring
python3 patterns/p13-strncpy-trunc/controls/sweep_fit.py --refit  # + estimators, out-of-sample, step bases
python3 patterns/p13-strncpy-trunc/controls/spellings.py --verus  # both spans, R5 twins through Verus
python3 patterns/p13-strncpy-trunc/controls/oracle_hole.py        # the fold's oracle, before and after
```
