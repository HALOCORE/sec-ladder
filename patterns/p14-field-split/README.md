# p14 — delimiter-framed field splitter

**The first bound in this project that is a COUNT OF A BYTE VALUE rather than a
length**, and the first pattern whose two loops multiply to a constant, so the
amortisation denominator can be swept on its own. The kernel copies a line into a
fixed `uint8_t scr[64]`, splits it on `,` into fields, and appends one descriptor
per field to a fixed `size_t tl[16]`. R1 never asks whether the table is full.

```
window:  nline:u32 LE, then lines of  llen:u32 ; llen bytes
kernel:  for each declared line
             m = min(llen, SCR)                 <<< the CLAMP, in EVERY rung
             memcpy m bytes into scr[0..m]      <<< BULK, in EVERY rung
             nt = 0 ; s = 0 ; i = 0
             while i <= m:                      <<< BOUNDED, in EVERY rung
                 if i == m or scr[i] == DELIM:   ('i == m' = a VIRTUAL delimiter)
                     if (nt == MAXTOK) break;   <<< R1 omits THIS LINE
                     flen = i - s ; tl[nt] = flen ; nt++ ; s = i + 1
                 i++
             for j in 0..nt: acc = fold(tj, scr[cur..cur+tj], acc); cur += tj + 1
             acc = acc*31 + nt
         return acc*31 + nline
```

## What is new here

- **The bound is a count of a byte value, so no length implies it and no hoist
  removes it.** `nt` is one more than the number of commas in `scr[0..m)`: a
  64-byte line holds between 1 and 65 fields against a 16-entry table.
  `adversarial-full65` is a **72-byte window that stores 392 bytes past the
  table** — 5.4× its own size. Every earlier guard here compares a *declared
  length* against a *buffer extent*.
- **The library contract decides whether an input is dangerous.** `strtok(3)`
  collapses runs of delimiters and this kernel does not, so `a,,,,,,,,,,,,,,,,z`
  is **2 fields** under one contract and **17** under the other, against the same
  16-entry table — a correct parse against a stack-buffer-overflow WRITE, on
  byte-identical input, measured on real glibc (`NOTES.md` 0d). ⚠ **And collapse
  changes WHICH inputs are dangerous, not WHETHER the guard is needed**:
  `adversarial-alt33` has no runs and gives 33 fields under both.
- **The amortisation denominator, swept at constant work.** Band `t` holds 480
  folded bytes and 8 lines fixed and moves only the field count, so it sweeps the
  thing a per-field cost is divided by and nothing else. The safety tax reads
  **6.456 Ir per line byte at one 60-byte field per line and 3.506 at sixteen
  ~3-byte fields** — a **1.84× range with the input size unchanged**. The
  direction is the counter-intuitive one and the mechanism is named: the check
  does not get cheaper, **R4 loses the 4× unroll it was winning with**
  (`NOTES.md` 9a).
- **An exact, zero-parameter, LISTING-DERIVED fold law**, predicted forward onto
  15 blobs it was not derived from with **worst residual 0.0177**:
  `fold4(L>=4) = 13 + 23·(L div 4) + [r>0]·(2 + 8r)`. ⚠ **One of those
  instructions is a NOP** — `xchg %ax,%ax` on the unrolled preamble's fallthrough
  — and the law is wrong by exactly 1.00 per field without it, so *the law's
  exactness is the evidence that the padding executes*. `.memory/03-measurement.md`
  trap 3, third instance, first one inside a derivation rather than a fit.
- **gcc's hardening law is exact and out-of-sample exact.**
  `R1h − R1 = 1.00·bytes + 2.00·fields − 3.00`, max residual **0.0000 over 66
  blobs**, worst leave-one-length-out error **0.0000 over 29 hold-outs**, and it
  predicts both shipped perf rows (`+238.00` / `+91.00`) which are not in the
  sweep. ⚠ **Its `nline` coefficient is exactly 0.00 and that null hides
  `−1.00 executed alignment NOP per line`** cancelled by `+1.00` of real work.
- **clang's safety line costs `+663.00 Ir/call` on `small`, and none of it is the
  compare.** The *unhardened* scan is **2× unrolled with the `i == m` test peeled
  into an epilogue**; the hardened one is neither. 3.50 Ir per scanned byte for a
  lost optimisation, and the blocking line is a data-dependent `break`, not a
  bounds check (`NOTES.md` 3b).
- **`4.25 = 2.00 + 2.25` on a fourth kernel, and the first time both halves are
  readable in ONE listing.** R4's fold runs the *unchecked un-unrolled* body
  (8.00 Ir/byte) in its `L mod 4` epilogue and the *unchecked unrolled* body
  (5.75) in its main loop, while R2 runs the *checked un-unrolled* one (10.00)
  throughout. The scan gives the other 2.00 (`cmp $0x3f ; ja`).
- **A measured NULL for the wall-clock column that the whole project can reuse.**
  `verus` and `unsafe` are byte-identical kernels with exactly equal marginal `Ir`
  on all 66 sweep blobs, and they differ by **+8.97% / +8.91%** in differenced,
  alternating, pinned wall clock over two passes — **larger than the gcc hardening
  gap (+7.2%) and comparable to two of the other three rung comparisons.** So
  p14 publishes no `ns` claim, and the R4/R5 pair is proposed as a free null
  control every pattern already has and none has used (`NOTES.md` 11).
- **The same bound discharged THREE ways, and the missing fourth is the finding.**
  p06 had four bases for its disjointness fact because `core` sells one
  (`split_at_mut`). **There is no standard-library routine that bounds a
  fixed-capacity append**, so R3 pays exactly the check R2 pays and p14's table
  has a hole where p06's had `std`'s `unsafe` (`NOTES.md` 6).
- **The cheapest in-contract R3 is a different spelling on the two inputs.** The
  shipped cell on `small`, `t_idxfold` on `large` — where it is **200.00 Ir/call
  cheaper**, so the shipped figure overstates the safe-side number by **88.9%**.
  Fifth pattern to owe `.memory/01-ladder.md` finding 3's number and the first to
  publish it in the first delivery (`NOTES.md` 8a).
- **Verus 19/0 on the second attempt (twin 23/0), and the failed first attempt is
  the reusable part.** Deriving the ghost sequences from the exec array
  (`Seq::new(nt, |k| tl@[k])`) fails two invariants and an assertion; **carrying**
  them and growing them by `Seq::push` needs no lemma at all, because `push`
  leaves earlier indices alone by an axiom vstd already has (`NOTES.md` 5).
- **`pm3_msonly` is p06's comparison and p14 comes out on the other side.**
  Weakening the postcondition to `true` does **not** rescue the
  safety-line-deleted mutant: it still fails, at the same obligation. **Memory
  safety alone suffices here and did not on p06**, and the discriminator is
  whether the bug's harm can stay inside the object.

## Three corrections this pattern makes to the layer above it

- **`.memory/06-catalogue.md`'s bug class for p14 — *"in-place mutation +
  aliasing"* — is not merely wrong, it is EXCLUDED BY THE HARNESS.** A `strtok`
  that tokenises the driver's payload is not a function of its arguments: on a
  one-window blob the checksum stops satisfying `acc(n) = r·Σ31^j` at the first
  repeat, measured on both compilers. The repair — a per-call scratch copy —
  deletes the mutation. And the aliasing half is `E0506` / `E0515`, i.e. p08's
  compile-time rejection with no run-time check to price. `NOTES.md` 0a.
- **`.memory/02-bench-rules.md`'s threshold table lists p14 as *"a delimiter is
  not a bound; the sentence reaches its scan's `i < len`"*, marked "not as
  stated". Settled by building it: the sentence is right and the mechanism is
  p11's**, so p14 puts its bug in the OUTER loop and pins `while (i <= m)` in
  every rung. p14 **inherits** the WRITE rule (its guard's threshold IS the
  table's extent) where p06 did not, and the consequence — no adversarial row can
  have the guard fire while the sanitizer is silent — holds. `NOTES.md` 0b, 7.
- **`.memory/01-ladder.md` finding 9's `2.00`-vs-`3.00` discriminator is narrower
  than written.** p14's scan has **two** other exit tests and still costs `2.00`,
  because `scr` is a fixed-size local at a constant frame offset so the check is
  `cmp $0x3f` against a literal. The discriminator is whether the base is a
  compile-time constant. `NOTES.md` 1.

## Files

| file | what |
|---|---|
| `spec.md` | the contract, and the pins `harness/check.py` enforces |
| `model.py` | the independent Python reference — a `bytes.split()` partition and a cursor walk mirroring the Verus spec, cross-checked |
| `inputs/gen.py` | deterministic input generation; `.bin` is gitignored |
| `c/kernel.c` | R1 — no field-count bound. **the bug** |
| `c/kernel_hardened.c` | R1h — one `if`, and that is the whole diff |
| `c/main.c` | the C driver loop |
| `safe_naive.rs` | R2 — indexed scan, indexed fold |
| `safe_tuned.rs` | R3 — two-step reslice, `tl[..nt].iter()`, `iter().fold()` |
| — | *(R2/R3 load with `dst[..n].copy_from_slice`; R4/R5 with `split_at_mut` — `NOTES.md` 6a)* |
| `unsafe.rs` | R4 — `get_unchecked` / `get_unchecked_mut` |
| `verus.rs` | R5 — R4's exec code plus the proof; `toks` is a recursion, not a closed form |
| `controls/gen_controls.py` | the priced fiats, the second and third in-contract R3 spellings, the delete-the-check family, the fold mutants and the three proof mutants |
| `controls/build_controls.sh` | builds them at the shipped `-O3 isolated` flags |
| `controls/verify_controls.sh` | checksums them against `model.py`; puts `<[T]>::split` through `./verus_run.py` |
| `controls/sweep_ir.py` | differenced marginal `Ir` over the four sweep bands |
| `controls/fit.py` | the laws and **leave-one-LENGTH-out**; refuses a singular design |
| `controls/law.py` | the **zero-parameter** fold law, derived from the listing and predicted forward |
| `controls/attr.py` | a law attributed MNEMONIC BY MNEMONIC, from callgrind `--dump-instr=yes` |
| `controls/wall_span.py` | identical-copy noise floor, alternating schedule, `t(n)−t(1)` |
| `NOTES.md` | what was measured |

## Running

```bash
python3 patterns/p14-field-split/inputs/gen.py            # the 8 matrix inputs
python3 patterns/p14-field-split/inputs/gen.py --sweep     # + the four sweep bands
python3 harness/check.py p14                               # the gate
python3 harness/measure.py p14                             # the numbers
python3 patterns/p14-field-split/controls/gen_controls.py  # the variants
bash    patterns/p14-field-split/controls/build_controls.sh
bash    patterns/p14-field-split/controls/verify_controls.sh
python3 patterns/p14-field-split/controls/sweep_ir.py --band all --cells all --json out.json
python3 patterns/p14-field-split/controls/fit.py out.json --cell c-gcc-h --diff c-gcc --lolo
python3 patterns/p14-field-split/controls/law.py out.json --cell unsafe
python3 patterns/p14-field-split/controls/attr.py \
    .temp/build/p14/c-gcc-O3-isolated .temp/build/p14/c-gcc-h-O3-isolated --input small
python3 patterns/p14-field-split/controls/wall_span.py --input small --reps 11
for m in pm1_nocap pm2_weakreq pm3_msonly; do
  ./verus_run.py .temp/p14/ctl/$m.rs; ./verus_run.py .temp/p14/ctl/$m.rs --cfg slb_twin
done
```

⚠ **Do not run two `sweep_ir.py` jobs at once.** They shared a scratch path in the
first attempt here and both produced silent nonsense — byte-identical `unsafe` and
`verus` kernels reading 3654 and 11550 Ir/call. The path is per-PID now; the
lesson is TASK_026 §0 item 7's and it cost a full re-measure.
