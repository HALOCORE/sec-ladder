# p36 — function-pointer table dispatch (vtable-like)

**The first computed-target indirect call in this tree, and the first harm that
is a control transfer rather than a value.**

A one-byte bytecode interpreter. Each record is an (opcode, operand) pair; the
opcode indexes a table of eight callables and the interpreter **calls** what it
finds:

```c
acc = TABLE[op](acc ^ arg);          /* c/kernel.c — no `op < NOPS` */
```

`c/kernel_hardened.c` tests `op < SLB_P36_NOPS` and folds a sentinel otherwise.
`c/kernel.c` omits exactly that, so an out-of-table opcode loads a code pointer
from past the end of `TABLE` and jumps to it.

## What is new, and what is not

⚠ **The bug class is not new: this is the tree's twelfth `index >= len`.** Four
other things are, and each is measured in `NOTES.md` §0:

| | |
|---|---|
| **the harm is a control transfer** — deterministic SIGSEGV on 24 of 24 out-of-table runs across gcc/clang × O0/O1/O2/O3 | §0c |
| **no checker in the matrix sees that.** ASan says `global-buffer-overflow … 0 bytes after global variable 'TABLE'`; UBSan says `index 8 out of bounds`. Both name the *array read*. gcc has no `-fsanitize=function` at all; clang's has it but is defeated here (the garbage is not a function, so the signature read faults first). **`-fsanitize=cfi-icall` is the only thing on this box that names the call** — and it needs `-flto` *and* `-fuse-ld=lld`, so it cannot be a rung. ⚠ **But the converse costs nothing**: there is no p36 input where the array read is in bounds and the call is wrong, so all of them fire on the *same input set* — the matrix is blind in **vocabulary**, not in **coverage** | §0b, §8d, §8e |
| **the indirect call is a cost mechanism nothing here has had** — 0 computed-target `call`s in 534 built kernel symbols across the other 21 patterns, counted | §0d |
| **the pinned Verus cannot type C's declaration.** `const TABLE: [fn(u64) -> u64; N]` is `does not yet support ... function pointer types`, so the Rust rungs use a trait object, and that costs **exactly 3.00000 Ir per dispatch** | §0a, §8a |

## The rungs, and the numbers

`Ir` per call at `-O3`, `isolated`. Every law is exact over twelve swept points
with **zero residual**, and confirmed out of sample at `nrw = 1024`:

⚠ **These are KERNEL-EXCLUSIVE**, and on the one pattern whose kernel *is* a
call that is a limitation rather than a unit: the eight dispatch targets are
outside every figure and they are **not equal across cells** (4.00 Ir/record in
gcc's column, 3.00 in clang's and rustc's, 0.00 for the `match`/`switch`
controls). The `kern+targets` column is the comparable one —
`.memory/03-measurement.md`'s p13 rule. `NOTES.md` §0e.

| rung | file | law, Ir/call (kernel-excl) | kern+targets | `small` | `large` |
|---|---|---|---|---:|---:|
| R1 | `c/kernel.c` | `10.00000·nrw + 39` | `14.00000·nrw + 39` | 1319 | 10279 |
| R1h | `c/kernel_hardened.c` | `12.00000·nrw + 38` | `16.00000·nrw + 38` | 1574 | 12326 |
| R1 clang | `c/kernel.c` | `11.00000·nrw + 31` | `14.00000·nrw + 31` | 1439 | 11295 |
| R1h clang | `c/kernel_hardened.c` | `15.00000·nrw + 31` | `18.00000·nrw + 31` | 1951 | 15391 |
| R2 | `safe_naive.rs` | `27.00000·nrw + 42` | `30.00000·nrw + 42` | 3498 | 27690 |
| R3 | `safe_tuned.rs` | `13.00000·nrw + 46` | `16.00000·nrw + 46` | 1710 | 13358 |
| R4 | `unsafe.rs` | `13.00000·nrw + 31` | `16.00000·nrw + 31` | 1695 | 13343 |
| R5 | `verus.rs` | `13.00000·nrw + 31` | `16.00000·nrw + 31` | 1695 | 13343 |

⚠ **The gcc-vs-clang C gap is not a compiler difference: it is gcc's default
`-fcf-protection=full`.** Every dispatch target opens with an `endbr64` IBT
landing pad — 49 in each gcc binary against 5 in every other — costing exactly
`1.00000·nrw + 1` Ir per call. `10` vs `11` becomes **`14` vs `14`**. So this
matrix has been pricing a CFI mitigation invisibly, in one language column, all
along. `NOTES.md` §0e, §8d.

**`R3 − R4` is a per-CALL constant and 0.00000 per record** — the bounds checks
are entirely outside the loop, and the listing shows no `cmp`/`jae` against a
length in R3's loop body at all. ⚠ **Which constant depends on the pairing, and
p36 publishes four numbers rather than one** (`NOTES.md` §8b):

| quantity | value |
|---|---|
| **fixed-R4 bound, cheapest in-contract R3 found** (`r3_window − R4ship`) | **+7.00 flat** |
| **matched-spelling pair** (`R3ship − r4_reslice`, admissible to admissible) | **+10.00 flat** |
| fixed-R4 bound, shipped R3 (`R3ship − R4ship`) — retained, a looser bound on the same quantity | +15.00 flat |
| R3-side span `r3_window … r3_idx` / R4-side span, 3 verified members | 1702 … 2232 / 1695 … 2717 |

⚠ **`+15.00 flat` shipped alone at TASK_072 and it was neither the matched pair
nor the tightest bound** (TASK_072_REVIEW B1). **Both sides are now searched.**
The R2-shaped unsafe rung — what every other pattern here uses as its R4 —
verifies and is **1022 / 8190 Ir/call dearer**; shipping it would have published
*safe Rust beats unsafe Rust by 1007 / 8175 Ir per call*, all of it loop
structure. And on the safe side `r3_window` reslices the window once and is
**8 Ir/call cheaper** than the shipped R3, in contract and with zero `unsafe`.

## The headline measurement

`Ir` **exactly constant — program totals too, 8,635,685 on all four** — wall
clock **3.13×**, one binary, several inputs (`NOTES.md` §7). Interleaved,
31 reps:

| targets | `Ir`/call | min ns/call (Rust R4) | min ns/call (C R1h, blocked) |
|---:|---:|---:|---:|
| 1 | 3359.0000 / 3110.0000 | 421.47 | 373.78 |
| 2 | 3359.0000 / 3110.0000 | 606.66 | 439.16 |
| 4 | 3359.0000 / 3110.0000 | 1194.04 | 768.87 |
| 8 | 3359.0000 / 3110.0000 | 1319.32 | 1182.23 |

⚠ **Noise floor on five byte-identical copies: 0.19–0.55% on this band**, from
eight independent floors over two sessions and both rep protocols. **The 4.19%
this README shipped does not reproduce** (TASK_072_REVIEW m2).

**A larger version of the same effect sits on the band where `Ir`-constancy is
true BY CONSTRUCTION**: `sweep-mixrand6` against `sweep-mixrun008` is **4.18×**
at an identical opcode multiset.

And a clean negative: **callgrind's simulated indirect-misprediction rate does
not order the wall clock** — `sweep-mixrand` and `sweep-mixrand6` sit **0.8%
apart** in simulated mispredict rate (0.8662 vs 0.8730), with identical `Ir` and
identical `Bi`, and **2.33× apart in wall clock**.

## Two things a reader should not miss

1. **A Verus `spec fn` declared in a trait occupies a vtable slot in the erased
   build, and it is NOT free.** Declare the ghost item *after* the exec one or
   R5's dispatch is `call *0x20(%rcx)` where R4's is `call *0x18(%rcx)` — same
   instruction count, same byte count, different bytes. ⚠ **Even in the shipped
   order it costs 64 bytes of `.data.rel.ro` (R4's vtables are 32 bytes, R5's
   are 40) plus one folded 26-byte `.text` stub**, so *"ghost code fully erases"*
   and *"the proven binary is byte-identical"* need scoping to executable paths
   and to the kernel symbol's bytes. `NOTES.md` §5.
1b. **And `identity` is blind to p36's dispatch table at every level, `exact`
   included** — permute `TABLE` and `md5_fn` is unchanged while the checksum
   moves. The gate is not unsound; the *checksum* stage is what catches it.
   `controls/identity_probe.py`, `NOTES.md` §5b.
2. **Eight `impl Op for OpN` blocks verify and the gate refuses them**
   (`vparse.duplicate_names`). The shipped shape is one
   `impl<const K: u8> Op for OpTag<K>` with eight monomorphisations, which is
   what makes p36 expressible with no `harness/` change. `NOTES.md` §9b.

## Reproducing

```bash
python3 patterns/p36-vtable-dispatch/inputs/gen.py --sweep
harness/build.py p36
harness/check.py p36
harness/measure.py p36
python3 patterns/p36-vtable-dispatch/controls/mkcontract.py --check
python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --run all
python3 patterns/p36-vtable-dispatch/controls/gen_controls.py --verus
python3 patterns/p36-vtable-dispatch/controls/mkmutants.py --run all
python3 patterns/p36-vtable-dispatch/controls/r3_contract.py
python3 patterns/p36-vtable-dispatch/controls/identity_probe.py
python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band t --wall --reps 31
python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band mix --wall --reps 31
python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band t --floor 5 --reps 31
python3 patterns/p36-vtable-dispatch/controls/cfi_probe.py
```

`sweep_ir.py` writes scratch under `$SLB_P36_SCRATCH` (default `.temp/p36/`) and
takes `--protocol {interleaved,blocked}`; interleaved is the default and the
rule, blocked reproduces the column `NOTES.md` §7 shipped at TASK_072.
