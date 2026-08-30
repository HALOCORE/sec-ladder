# p32 — free-list allocator / object pool with recycling

**`p32` and `p33` of `.memory/06-catalogue.md` are ONE ROW with TWO ARMS**, and
this is it: one C mechanism, one omitted conjunct, and the input picks the harm.

⚠⚠⚠ **This row exists because the ADMISSION BAR WAS CORRECTED**
(`CLAUDE.md` rule 6, `.memory/02-bench-rules.md` *THE ADMISSION BAR IS C-SIDE
ONLY*, RECAP findings 53 and 54). It was refused twice on the sentence *"safe
slab == buggy C bit for bit"*. **That sentence is true, it is measured here, and
it is the row's headline rather than a defect.**

| | |
|---|---|
| **Bug** | CWE-416 use-after-free **and** CWE-415 double free, both through CWE-672. FREE, READ and WRITE consume a `(slot, generation)` handle and ask only whether the handle register holds one, never whether the block is still that incarnation. |
| **Safety line** | `} else if (gen[h] != g) {` — **one conjunct, at ONE site**, because the three handle-consuming opcodes share the handle decode. `controls/safety_line.py` preprocesses both C rungs and measures the diff: **`+2 / −0`**. |
| **Rungs** | R1 `c/kernel.c` · R1h `c/kernel_hardened.c` · R2 `safe_naive.rs` · R3 `safe_tuned.rs` · R4 `unsafe.rs` · R5 `verus.rs` |
| **R5** | `15 verified, 0 errors` (twin config `18 / 0`), TCB **5 trusted items** against `p27`'s and `p29`'s seven — **p32 allocates nothing**, so no `allocate`/`deallocate`. Full functional refinement: `ensures r == pool_fold(buf@, off, len)`. |
| **Headline** | **`#![forbid(unsafe_code)]` safe Rust reproduces the buggy C BIT FOR BIT on every input — while the same C source with `malloc` storage ABORTS.** |
| **Cost** | ⚠ **NONE PUBLISHED.** p32 ships with no cost axis, like `p29`. The absence is declared; it is not a measured zero. `NOTES.md` 7. |

## The row in one table

`controls/storage_arms.py`, one algorithm, storage the only variable:

| input | C arena (bug) | C malloc (bug) | safe Rust (bug) | C fix | malloc detector |
|---|---|---|---|---|---|
| benign | 72356755880000075 | 72356755880000075 | 72356755880000075 | same | — |
| adv-stale-read | 32521 | *not reproducible* | **32521** | 38535 | `heap-use-after-free` |
| adv-recycle | 29797947 | **29797947** | **29797947** | 30032431 | **— silent in BOTH** |
| adv-doublefree | 28444101123 | `rc = -6` | **28444101123** | 35593523088 | `attempting double-free` |
| adv-alias | 895071855618 | `rc = -6` | **895071855618** | 7765691657627 | `attempting double-free` |

Three results, and each is separate:

1. **safe Rust == the buggy C arena rung on 10 of 10 (input, arm) cells**,
   including the four where the answer is wrong.
   ⚠ The `malloc` arm's stale-read cell reads freed heap, so its
   checksum is a function of the allocator and no number from it is a fact —
   `NOTES.md` 2. The arena cell is `32521` in all five builds and 1 distinct
   value in 20 runs.
2. **The same C source on `malloc` storage aborts** on two of the three harms,
   with the free list, the generations, the handle registers, the fold and the
   safety line byte-identical. A controlled two-cell experiment on **detector
   coverage**.
3. **`adv-recycle` is bit-identical and silent in both.** The use-after-recycle
   harm is storage-independent and invisible to every allocation-shaped
   instrument. That is `p33`'s arm.

⚠ And on the SHIPPED storage: **ASan, UBSan and Miri are silent on all
nine inputs**, while four of them return a wrong answer and two of them produce
two live handles naming one block. `model.py` *derives* that silence — its
simulation computes every index the buggy rung would compute and checks whether
one escapes — rather than declaring it.

## Why it is not `p27` and not `p29`

```
p27   individually malloc'd records; `live[h]` is consulted on the FREE path, so
      it CANNOT double-free; no free list, no recycling, no generation. Its
      stale read dereferences a DANGLING POINTER.
p29   a real free() of a whole record and a stale ADDRESS held across it. Its
      recycle half re-occupies a LIVE allocation -- the closest either row comes.
p32   NOTHING IS ALLOCATED AND NOTHING IS FREED.  The harm is ALIASING: two live
      handles naming one block, produced by a free list that SELF-LOOPS when a
      recycled handle is freed a second time.  Neither built row can produce it.
```

**The aliasing harm has no analogue in `p27` or `p29`, and that is the
C-mechanism distinction this row rests on.**

## Two things worth knowing before quoting anything here

* ⚠ **The R5 verifies, and an arm that DELETES the safety line from the
  exec code *and from the specification* also verifies** (`controls/
  proof_mutants.py` `M4`, `15/0`). p32 has no linear resource, so nothing forces
  the conjunct's presence; the safety line is load-bearing against the
  specification and against nothing else. `p42` is the precedent for shipping
  that as the finding. `NOTES.md` 6.
* ⚠ **R1's checksum is REPRODUCIBLE**, 1 distinct value in 20 runs on
  every input — a property neither built temporal row has, because p32's answer
  contains no heap address. Its adversarial rows are excluded from the gate's
  agreement set because they *disagree*, not because they are unstable.

## Where to look

- `c/kernel.h` — the kernel contract in pseudocode, the C-mechanism argument, and
  the invariant that makes R1h correct.
- `c/kernel.c` vs `c/kernel_hardened.c` — **the diff is the row**, and
  `controls/safety_line.py` measures it on the preprocessed files.
- `spec.md` — the machine-readable contract and the reasoning behind each pin.
- `NOTES.md` — every measurement, the TWO deviations from `TASK_143`'s
  demonstration (sections 1b and 9a) with the reason each was made and the
  control that backs it, and what was not done.
- `controls/storage_arms.py` — the two-cell storage experiment above, with a
  positive control that must fire in all ten C builds.
- `controls/forgeable.py` — why the file names a handle REGISTER: the
  file-supplied-handle variant's **hardened** kernel self-loops its own free list
  in five operations.
- `controls/proof_mutants.py` — the R5 battery: an ATTACK arm that must fail, a
  VACUITY arm that must fail, and the spec-weakening arm that must verify.
- `controls/repro.py` — 20-run reproducibility, R1 and R1h, every input.
