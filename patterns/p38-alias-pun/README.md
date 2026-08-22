# p38 — strict aliasing / type punning

**The first bug class in this tree that unsafe Rust does not reintroduce — and
the first `c/kernel.c` here whose bounds check is *written* and ignored anyway.**

`spec.md` is the contract. `NOTES.md` has every measurement. This file is the
summary.

> ⚠ **What p38 is, before anything else.** `c/kernel.c` is a **demonstration
> kernel**, not a claim about code in the field. The harm needs **four
> conjunctive conditions** (`NOTES.md` §11) and **six defined spellings of the
> same kernel are CHEAPER on gcc than the undefined one** — five of them by
> exactly 6.00 `Ir`/call. The bug class is real and ASan-confirmed; its
> *prevalence* is not measured here, and the earlier claim that "the pair is
> written this way in real parsers" was uncited and is **withdrawn**.
> The **ladder** result — R2…R5 immune by construction — is unaffected.

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

**The harm needs all FOUR of these at once. Remove any one and it goes:**

1. the getter and the setter **disagree about the access type**;
2. the getter is called a **second time** after the setter;
3. the write-back has **no consumer** other than that second read;
4. both accessors are visible in **one optimisable region**.

⚠ **(3) is structural here and is the least realistic.** `sc[i]`/`sc[i+1]` are
read by nothing else and the cursor never revisits them, so the clamp store
exists only to be re-read three lines later. The realistic reason to write a
clamp *back* is a later pass — and that shape (sanitise loop, then walk loop) is
measured **not to reproduce**, 12 of 12 cells (`NOTES.md` §0c). Two further
counterfactuals that also remove it and are not one-liners: the two-pass parser,
and putting `rec_set_len` in its own TU without LTO (it fires again under
`-flto`).

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

## The results, in five lines

1. **The undefined spelling is the DEAREST of its neighbours — p38's sharpest
   result.** Eight one-line variants of `c/kernel.c`, built and measured in one
   run (`controls/gen_controls.py --ir`, whole-program marginal `Ir`/call,
   `small.bin`, `-O3 isolated`):

   | | gcc | vs the pun | answer |
   |---|---:|---:|---|
   | **the pun (ships, UNDEFINED)** | **1043.72** | — | **WRONG** |
   | symmetric accessor pair (`c_symset`) | 1037.72 | **−6.00** | correct |
   | one `rec_len` call (`c_once`) | 1037.72 | **−6.00** | correct |
   | `-fno-strict-aliasing` (`c_nosa`) | 1037.72 | **−6.00** | correct |
   | `memcpy` / union (`c_memcpy`, `c_union`) | 1037.72 | **−6.00** | correct |
   | no write-back (`c_noback`) | 1041.72 | −2.00 | correct |
   | the two-half read (`c_halves`, = R1h) | 1055.72 | +12.00 | correct |

   **Three of those remove three *different* ones of the four conditions the
   harm needs, and each costs the same 6.00 to not have.** On clang the pun is
   not a win either: `c_once` is 8.00 cheaper and four of the rest are
   **byte-identical** to it (`md5_fn 366e3be50428…`). **No pattern in this tree
   had priced a whole-program-semantics flag before.**

2. **The check is written and deleted.** `c-gcc` at `-O3`, both inline modes, on
   `adversarial-oob.bin`: the fold reads past a 256-word stack array, ASan says
   `stack-buffer-overflow READ of size 2`, and the checksum is **different on
   every run**. The same source at `-O0`, on clang, or with
   `-fno-strict-aliasing`, clamps. ⚠ **The run-to-run variation is ASLR on
   `adversarial-stale` (deterministic under `setarch -R`) and NOT ASLR on
   `adversarial-oob`, the row this line uses — its cause is not established**
   (`NOTES.md` §2).

3. **Three exact laws, and the additivity failure is 100% attributable.** Zero
   free parameters, tested out of sample on pairs neither fitting band contains:
   `R1h − R1 = 3.00000·nrec` (gcc), `8.00000·nrec` (clang), and
   `R3 − R4 = 17 + 1.00·nrec + 1.00·nrec·[rlen == 1]` — max residual **0.00000**
   everywhere, including the one blob TASK_066 disclosed as an exception.
   ⚠ **The additivity test DID fail for `R2 − R4`, and the cause published for
   it was wrong.** It is not `nw`: `R2 − R4` is *exactly constant* in `nw`. The
   repaired law

   ```
   R2 − R4 = A(nw mod 8) − 8·nrec + 6.5·nrec·rlen
                         − 10.5·nrec·(rlen mod 2) + 6·nrec·[rlen == 1]
             A(0) = 79 ;  A(m) = 33 + 6m  for m = 1..7
   ```

   is exact — **0.00000 on all 106 measured rows** and on both matrix blobs. The
   model was missing **three** columns, **none of them the one named**: a real
   `nrec × rlen` interaction through the *parity* of `rlen`, a band-design
   defect whose column is `nw mod 8`, and a fold boundary at `rlen = 1`.
   `NOTES.md` §4c; the misspecified equation TASK_066 published as a result is
   **retracted** and its three coefficients are artefacts.

4. **TySan is the only instrument that sees the violation itself**, and its
   blind spot is **promotion, not inlining** — `NOTES.md` §6a has the four
   probes that separate them, and p38 fires in *both* inline modes because its
   scratch is a real in-memory array. More precisely: *TySan checks only the
   accesses that survive to the end of the pipeline.* UBSan has no
   strict-aliasing check at all and catches only the consequence, and only when
   the index leaves a statically-typed array.

5. **The gate's own sanitizer stage does not see p38, and the hole is ONE FLAG
   wide.** It is **flag-gated, not level-gated**: `gcc -O1 -fstrict-aliasing`
   already miscompiles and ASan already reports the overflow, so adding that one
   token to stage 7's command line makes it see p38 **at `-O1`** — raising the
   optimisation level is *not* the repair and would perturb 20 patterns.
   **Blast radius, recounted across all 20 gate records: exactly one pattern.**
   15 declare ≥1 `sanitizer_expect: "fires"` row and all 36 such rows fired at
   `-O1`; of the 5 that declare none, p01/p08 model no memory bug, p04
   overwrites in bounds and p47's harm is timing. **p38 is the only pattern
   whose declared-clean adversarial row is clean because of the gate's BUILD
   FLAGS rather than its kernel** (`model.py::sanitizer_expect`, `NOTES.md` §6b).

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

⚠ **That +21.0 / +25.0 is the FIXED-R4 bound, and the R4 side is NOT
degenerate.** One R4 spelling found cheaper than what ships — `r4_slice`, an
unchecked reslice — measures **−3.00 / −7.00**, and its Verus twin was not built
because it needs two new trusted items. So the true `R3 − inf(R4 found)` is
**+24.0 / +32.0** and **the published figure flatters the SAFE rung**, by 14% /
28% of the headline. That is `.memory/01-ladder.md` finding 18's direction and
p10's and p27's defect in kind; it is disclosed here and in `NOTES.md` §8b/§10d,
and it was **not** disclosed in this file until TASK_067.

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
