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
  and **−45 / −108 Ir** under clang, while the clock says **+19.5% / +57.1%**
  and **+9.8% / +10.6%**. `NOTES.md` 0b and 3. The clang sign comes from a lost
  load-merge, not from the divide: reducing `r` proves `r < 64`, which lets LLVM
  fold the four-byte header decode into one `mov`.
  Sharper still: two hardened spellings with **exactly the same `Ir`** (2646.9640
  both) differ by **8.5% in wall clock**.
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
- **The same disjointness fact, discharged four ways, with four different trusted
  bases** — rustc's bounds check (R2, TCB 0), `core`'s own `unsafe` inside
  `split_at_mut`/`ptr::swap_nonoverlapping` (R3, TCB = the standard library),
  a comment (R4), and one discharged `requires` (R5). The rung with `std`'s
  unsafe is the **most expensive of the four**. `NOTES.md` 6.
- **A verified program that is wrong on the pattern's own adversarial row.**
  `r %= SCR` — one identifier from the contract — is memory-safe on every input
  and functionally wrong on exactly regime 1; with a memory-safety-only spec it
  verifies **17/0, twin 22/0** and prints the wrong answer. With the functional
  spec it fails. `NOTES.md` 10.

## Two corrections this pattern makes to the layer above it

- **`.memory/02-bench-rules.md`'s WRITE rule does not reach p06**, and its own
  threshold test is what says so: the guard's threshold is `min(nelem, SCR)`,
  *inside* the destination's extent, so "the guard fired" and "the unguarded rung
  stored out of bounds" are independent events. p06 sits with p24, not with p12.
- **The pinned vstd DOES specify `<[T]>::copy_from_slice`**
  (`vstd/std_specs/slice.rs:205`), against what TASK_047 and
  `.memory/04-verus.md` both say. p06's trusted `scr_load` is therefore an axiom
  about the `&mut [u8; 64]` → `&mut [u8]` **reborrow**, not about the copy, and
  `split_at_mut`'s specification carries the write-back that would remove it.
  `NOTES.md` 6 and 11.

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
| `safe_tuned.rs` | R3 — two-step reslice, `split_at_mut` + `zip` + `mem::swap`, iterator fold |
| `unsafe.rs` | R4 — `get_unchecked` / `get_unchecked_mut` |
| `verus.rs` | R5 — R4's exec code plus the proof; `rev_range`/`rot_left` closed forms and three lemmas |
| `controls/gen_controls.py` | the mutants and the out-of-contract variants (families A–E) |
| `controls/build_controls.sh` | builds them at the shipped `-O3 isolated` flags |
| `controls/verify_controls.sh` | puts the Verus mutants through `./verus_run.py`, both configurations |
| `controls/sweep_ir.py` | differenced marginal `Ir` over the five sweep bands |
| `controls/fit.py` | the pooled design's rank, the laws, and leave-one-`m`-out |
| `controls/wall_span.py` | identical-copy noise floor, alternating schedule, `t(n)−t(1)` |
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
```
