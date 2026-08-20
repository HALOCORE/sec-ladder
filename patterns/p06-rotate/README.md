# p06 — in-place rotate

**The first safety line in this project that is a DIVISION**, and the first bug
whose harm safe Rust reproduces bit-for-bit on a **write**. The kernel copies a
record's bytes into a fixed local `uint8_t scr[64]` and rotates the live prefix
left by an attacker-supplied `r`, spelled as the classic three in-place
reverses. R1 never reduces `r`.

```
window:  nrec:u32 LE, then records of  nelem:u32 ; r:u32 ; nelem bytes
kernel:  for each declared record
             m = min(nelem, SCR)                  <<< the CLAMP, in EVERY rung
             memcpy m bytes into scr[0..m]        <<< BULK, in EVERY rung
             if m != 0 { r %= m } else { r = 0 }  <<< R1 omits THIS LINE
             reverse(scr,0,r) ; reverse(scr,r,m) ; reverse(scr,0,m)
             acc = fold(scr[0..m], acc) ; acc = acc*31 + m
         return acc*31 + nrec
```

## What is new here

- **`Ir` gets the sign wrong, by construction and with a named mechanism.**
  Every earlier safety line here is a compare-and-branch. This one is a hardware
  `div`, which callgrind prices at exactly **1 Ir** and Cascade Lake at tens of
  cycles. Measured on the shipped tree: `R1h − R1` is **+41 / +95 Ir** under gcc
  and **−45 / −108 Ir** under clang, while the clock says **+18.8% / +57.9%**
  and **+10.3% / +11.6%** over a 30-layout population. `NOTES.md` 0b, 3 and 3c′.
  The clang sign comes from a lost load-merge, not from the divide: reducing `r`
  proves `r < 64`, which lets LLVM fold the four-byte header decode into one
  `mov`.
  Sharper still: two hardened spellings with **exactly the same `Ir`**
  (2646.9640 both on `small`, 1802.0000 both on `large`) differ by **8.5%** and
  **16.5%** in wall clock.
- **On `large` under clang, HARDENING IS FASTER THAN THE BUG.** The cheapest
  in-contract hardening (`if (r >= m) r %= m;`) runs **6.9% faster** than the
  unhardened kernel, and the worst layout pair in a 30-layout population is
  still 2.5% faster. On `small` the repeated-subtraction spelling is 1.1%
  faster. Against the textbook `r %= m`'s **+57.9% (gcc, `large`)**, the two
  numbers the two-number rule asks for are **42.8× apart on `small` and 11.6×
  apart on `large`**. `NOTES.md` 3c′.
- **23% of gcc's exact, zero-residual safety law is EXECUTED ALIGNMENT
  PADDING.** `R1h − R1 = +8.00·nrec + 1 − rzero` holds with max residual 0.0000
  over 77 blobs — and per record only **1.000** of that 8 is the `divq`;
  **1.833** is executed `.p2align` `nop`s and ≈5.08 is the register pressure the
  divide puts on the header decode (two named byte spills). `-fno-align-loops`,
  which changes no semantics and no work, moves the law to **+73.00**.
  `NOTES.md` 3a′ — and the same phenomenon reaches a *second* p06 law
  independently (`NOTES.md` 9a).
- **Two regimes of one bug, separated by a constant, and only one is a
  memory-safety event.** `reverse(scr,0,r)`'s highest index is `r−1`, so for
  `m <= r <= SCR` the unreduced rotate stays *inside* the array. On
  `adversarial-inarray` **five unchecked programs — C under gcc, C under clang,
  two safe-Rust rungs with the check deleted and zero `unsafe`, and unsafe Rust —
  print the same wrong answer, exit 0, ASan+UBSan clean, nothing panics.** Above
  `SCR` the safe rungs panic and C walks p12's silent/canary/SIGSEGV ladder.
  `NOTES.md` 7. **(The boundary is `r > SCR`, one past where the task file put
  it.)**
- **The safety line PAYS FOR ITSELF in safe Rust.** `R2 − R4` is
  `32.00·nrec + 13.00` and **`0.00000` Ir per rotated byte**, swept over 46
  values of `m`. Decomposed one loop at a time, **100% of it is the record-header
  decode**: writing `get_unchecked` in the three reverse loops and in the fold
  produces the **byte-identical** kernel, because `r %= m` bounds every cursor by
  the array's own constant capacity. Delete the reduction and the tax triples.
  `NOTES.md` 4.
- **A tuned-safe rung's `O(n)` term with NO SAFETY IN IT — and it belongs to one
  spelling, not to R3.** The shipped R3 costs `2.00000 Ir` per rotated byte;
  decoded with a `core::panic::Location` reader it has the **identical 11 panic
  pads at identical `line:col`** as the cheaper spellings, so **none** of that
  term is a bounds check — it is the `zip`/`Rev` adaptor's two exhaustion tests
  per item. An equally in-contract R3 with zero `unsafe` (`c_idx`) has **no
  per-byte term at all** and costs 13–17 `Ir` per *record*. Both numbers are
  published, labelled, with the input named. `NOTES.md` 4a and 8.
- **The same disjointness fact, discharged four ways, with four different trusted
  bases** — rustc's bounds check (R2, TCB 0), `core`'s own `unsafe` inside
  `split_at_mut`/`ptr::swap_nonoverlapping` (R3, TCB = the standard library),
  a comment (R4), and one discharged `requires` (R5). The rung with `std`'s
  unsafe is the **most expensive of the four**. `NOTES.md` 6.
- **A TCB that went DOWN while the obligation count went UP.** `scr_load` was
  trusted for a reason that turned out to be false; verifying it takes p06 from
  **6 `external_body` items to 5** and the obligations from **17 → 18** (twin
  22 → 23), with the compiled kernel **byte-identical** — same `md5_raw`, same
  216/208 instructions, `identity: exact` holding. The axiom does not vanish, it
  **relocates into three vstd items**, and `NOTES.md` 6b says what that does and
  does not mean for the TCB column: across 14 patterns and 58 trusted items,
  exactly **2** were removable this way (now 1 in 57), because `get_unchecked`,
  `get_unchecked_mut`, `count_ones`, `copy_nonoverlapping`, `as_ptr`,
  `as_mut_ptr` and `<*const T>::add` are all `is not supported` at the pinned
  vstd. `NOTES.md` 6a and 6b. ⚠ **It is free at `-O3` and not at `-O0`**: R5
  cannot spell `dst[..n].copy_from_slice(...)` at all (`RangeTo<usize>` has no
  `SliceIndexSpecImpl`), so R4 follows it to `split_at_mut` to keep the identity
  pin — zero cost at `-O3` in every rung, `+3` static instructions in R4's `-O0`
  kernel. That is the `identity` pin transmitting the **verifier's
  expressiveness limit** into R4's source, which is a new form of
  `.memory/01-ladder.md`'s finding 14.
- **A verified program that is wrong on the pattern's own adversarial row.**
  `r %= SCR` — one identifier from the contract — is memory-safe on every input
  and functionally wrong on exactly regime 1; with a memory-safety-only spec it
  verifies **18/0, twin 23/0** and prints the wrong answer (and is caught by the
  contract pin *and* the `identity` pin — `NOTES.md` 10b). With the functional
  spec it fails. `NOTES.md` 10.

## Two corrections this pattern makes to the layer above it

- **`.memory/02-bench-rules.md`'s WRITE rule does not reach p06**, and its own
  threshold test is what says so: the guard's threshold is `min(nelem, SCR)`,
  *inside* the destination's extent, so "the guard fired" and "the unguarded rung
  stored out of bounds" are independent events. p06 sits with p24, not with p12.
- **`.memory/04-verus.md:133` and `:813` are false in both halves, and the
  correction is not the obvious one.** They say there is no vstd spec for
  `copy_from_slice` and that a verified bulk copy therefore needs a trusted
  wrapper around `ptr::copy_nonoverlapping`. The spec exists
  (`vstd/std_specs/slice.rs:205`), and **`split_at_mut`'s carries the array→slice
  write-back** (`:185`), so p06's `scr_load` needs no wrapper at all — 6 TCB
  items → 5, at byte-identical codegen. But p02's `copy_bytes` contract also
  discharges and p02 **must keep** its wrapper: its verified spelling costs +9
  instructions and +5.00 `Ir`/call and breaks `identity: exact`. **The
  discriminator is what R4's body is** — `copy_from_slice` (p06) or
  `copy_nonoverlapping` (p02), and the raw-pointer route is `is not supported`.
  `NOTES.md` 6a/6b and p02's `NOTES.md` 5b.
- **"The verified twin is the sole catcher" is a Verus-level claim, not a gate
  claim.** p06's clause-weakening mutant also fails the `spec.md` contract pin
  with two diffs, and its memory-safety-only mutant also breaks the `identity`
  pin. The same sentence is **false on p12** for the same reason and **absent
  from p02**, which states the pin edit explicitly. `NOTES.md` 10b.

## Files

| file | what |
|---|---|
| `spec.md` | the contract, and the pins `harness/check.py` enforces |
| `model.py` | the independent Python reference — a three-reverse simulation and a **closed-form** rotation, cross-checked |
| `inputs/gen.py` | deterministic input generation; `.bin` is gitignored |
| `c/kernel.c` | R1 — no reduction. **the bug** |
| `c/kernel_hardened.c` | R1h — one `if`, and that is the whole diff |
| `c/main.c` | the C driver loop |
| `safe_naive.rs` | R2 — indexed four-statement swap |
| — | *(R2/R3 load with `dst[..n].copy_from_slice`; R4/R5 with `split_at_mut` — `NOTES.md` 6a)* |
| `safe_tuned.rs` | R3 — two-step reslice, `split_at_mut` + `zip` + `mem::swap`, iterator fold |
| `unsafe.rs` | R4 — `get_unchecked` / `get_unchecked_mut` |
| `verus.rs` | R5 — R4's exec code plus the proof; `rev_range`/`rot_left` closed forms and three lemmas |
| `controls/gen_controls.py` | the mutants and the out-of-contract variants (families A–E) |
| `controls/build_controls.sh` | builds them at the shipped `-O3 isolated` flags |
| `controls/verify_controls.sh` | puts the Verus mutants through `./verus_run.py`, both configurations |
| `controls/sweep_ir.py` | differenced marginal `Ir` over the five sweep bands |
| `controls/fit.py` | the pooled design's rank, the laws, and leave-one-`m`-out |
| `controls/wall_span.py` | identical-copy noise floor, alternating schedule, `t(n)−t(1)` |
| `controls/clayout.py` | the 30-layout population for the **C** cells (a pad object shifts `.text`; `common/layout/` can only do the Rust ones) |
| `NOTES.md` | what was measured |

## Running

```bash
python3 patterns/p06-rotate/inputs/gen.py            # the 8 matrix inputs
python3 patterns/p06-rotate/inputs/gen.py --sweep     # + the five sweep bands
python3 harness/check.py p06                          # the gate
python3 harness/measure.py p06                        # the numbers
python3 patterns/p06-rotate/controls/gen_controls.py  # the variants
bash    patterns/p06-rotate/controls/build_controls.sh
bash    patterns/p06-rotate/controls/verify_controls.sh
python3 patterns/p06-rotate/controls/sweep_ir.py --band m --cells all --json out.json
python3 patterns/p06-rotate/controls/fit.py --diff=safe_naive,unsafe out.json
python3 patterns/p06-rotate/controls/wall_span.py --input small
python3 patterns/p06-rotate/controls/clayout.py --build
python3 patterns/p06-rotate/controls/clayout.py --time --input large --reps 5
```
