# p38 — strict aliasing / type punning

**The first bug class in this tree that unsafe Rust does not reintroduce — and
the first `c/kernel.c` here whose bounds check is *written* and ignored anyway.**

`spec.md` is the contract. `NOTES.md` has every measurement. This file is the
summary.

## What it is

A word-oriented wire format. Each window declares `nrec` records; each record's
32-bit length lives on the wire as two 16-bit halves; the parser decodes the
stream into a `uint16_t` scratch, **clamps any over-long length in place**, reads
it back through an accessor, and folds the payload.

```c
static uint32_t rec_len(const uint16_t *r) { return *(const uint32_t *)r; }   /* R1  */
static uint32_t rec_len(const uint16_t *r) { return (uint32_t)r[0] + 65536 * (uint32_t)r[1]; }  /* R1h */

if (rec_len(&sc[i]) > room)                 /* THE CLAMP -- in BOTH C rungs */
    rec_set_len(&sc[i], (uint32_t)room);    /* two uint16_t stores          */
n = (size_t)rec_len(&sc[i]);                /* THE RE-READ -- one uint32_t load */
```

The clamp stores through `uint16_t` lvalues and the re-read loads through a
`uint32_t` lvalue. C99 6.5p7 says those cannot alias, so the compiler may answer
the second `rec_len` from the value the first returned — and the stale,
attacker-controlled length then bounds the fold.

| rung | length read | immune? |
|---|---|---|
| R1 `c-gcc` | `*(const uint32_t *)r` | **no — gcc 13.3.0 `-O3` reads off the end of the scratch** |
| R1 `c-clang` | the same source | yes, and **§0d says why, mechanically** |
| R1h `c-gcc-h` / `c-clang-h` | `r[0] + 65536 * r[1]` | yes |
| R2 `safe_naive` | `sc[i] + 65536 * sc[i+1]`, indexed | **yes, by construction** |
| R3 `safe_tuned` | the same, with the fold resliced | **yes, by construction** |
| R4 `unsafe` | the same, `get_unchecked` throughout | **yes — there is nothing for `unsafe` to unlock** |
| R5 `verus` | R4 plus a proof of **spatial safety only** | yes — **and the proof is silent about the reason** |

Rust's `&mut` carries `noalias`, which is **uniqueness** — a provenance
property, not a type one. Nothing in Rust lets an optimiser assume a `u32`
access and a `u16` access do not overlap. The direct analogue of the C pun,
`ptr::read_unaligned::<u32>` on a `*const u16`, is **defined Rust**: shipped as
the control `r4_pun`, it prints the model's checksum at `-C opt-level=3` and
Miri is silent.

## The results, in four lines

1. **The check is written and deleted.** `c-gcc` at `-O3`, both inline modes, on
   `adversarial-oob.bin`: the fold reads past a 256-word stack array, ASan says
   `stack-buffer-overflow READ of size 2`, and the checksum is **different on
   every run** (stack residue under ASLR — p03's pointer-disclosure shape). The
   same source at `-O0`, on clang, or with `-fno-strict-aliasing`, clamps.

2. **The UB buys nothing, and the flag price is negative.** On clang the
   defined `memcpy` and `union` spellings and the `-fno-strict-aliasing` build
   are **byte-identical** to the UB one (`md5_fn 366e3be50428…`, 175
   instructions). On gcc, `-fno-strict-aliasing` is **−6.00 Ir/call**: what the
   type rule bought was the deletion of a reload the surrounding code then had
   to work around. **No pattern in this tree had priced a whole-program-semantics
   flag before.**

3. **Two exact laws, one failed prediction.** Fitted on two independently varying
   structural parameters and tested out of sample on pairs neither band
   contains:
   `R1h − R1 = 3.00000·nrec` (gcc) and `8.00000·nrec` (clang), max residual
   **0.00000** in and out of sample; `R3 − R4 = 17 + 1.00·nrec`, exact on 27 of
   28 sweep blobs and on both measured blobs. ⚠ **The same test FAILED for
   `R2 − R4`** (max out-of-sample residual 86.66) because R2 also pays a check
   per window byte and `nw` is a regressor neither band varies. First failure of
   this project's additivity test, and it is informative rather than a defect.

4. **TySan is the only instrument that sees the violation itself**, and its
   blind spot is **promotion, not inlining** — `NOTES.md` §6a has the three
   probes that separate them, and p38 fires in *both* inline modes because its
   scratch is a real in-memory array. UBSan has no strict-aliasing check at all
   and catches only the consequence, and only when the index leaves a
   statically-typed array. **The gate's own sanitizer stage builds at `-O1` and
   is therefore structurally blind to p38** (`model.py::sanitizer_expect`).

## Cost

Kernel-exclusive `Ir` per call, `-O3 isolated`, 20 000 calls
(`results/tables/p38-alias-pun.md`):

| rung | `small` (nrec 4) | `large` (nrec 8) |
|---|---:|---:|
| `c-gcc` (**miscompiled**) | 1028.0 | 2558.0 |
| `c-gcc-h` | 1040.0 | 2582.0 |
| `c-clang` | 1260.0 | 3175.0 |
| `c-clang-h` | 1292.0 | 3239.0 |
| `safe_naive` | 1563.0 | 3972.0 |
| `safe_tuned` | 1327.0 | 3286.0 |
| `unsafe` | 1306.0 | 3261.0 |
| `verus` | **1306.0** | **3261.0** |

`R5 = R4` to the instruction and to the byte. `R3 − R4 = +21.0 / +25.0`, i.e.
`O(1)` per record and **0.00 per payload byte**.

⚠ **Do not quote `c-gcc` as "C is faster".** It is `c-gcc-h`'s program minus a
reload the type rule let the compiler drop: **the bug is the speed.** The honest
same-backend column is `c-clang-h` against `safe_tuned`, **+35.0 / +47.0**.

## Four of eight rungs are immune, and that is the finding

R2, R3, R4 and R5 print the model's checksum on **every** adversarial input at
every optimisation level and inline mode. None of them is immune because of a
check — R4 has no checks at all — and none of them had to do anything to be
immune. `NOTES.md` §5 states what an adversarial row even *means* when the harm
is a miscompilation: the input makes the **compiler** do something wrong, and
the same source one optimisation level lower is correct on it.
