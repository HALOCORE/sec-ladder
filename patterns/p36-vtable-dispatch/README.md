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
| **no checker in the matrix sees that.** ASan says `global-buffer-overflow … 0 bytes after global variable 'TABLE'`; UBSan says `index 8 out of bounds`. Both name the *array read*. gcc has no `-fsanitize=function` at all; clang's has it but is defeated here (the garbage is not a function, so the signature read faults first). **`-fsanitize=cfi-icall` is the only thing on this box that names the call** — and it needs `-flto` *and* `-fuse-ld=lld`, so it cannot be a rung | §0b, §8d |
| **the indirect call is a cost mechanism nothing here has had** — 0 computed-target `call`s in 534 built kernel symbols across the other 21 patterns, counted | §0d |
| **the pinned Verus cannot type C's declaration.** `const TABLE: [fn(u64) -> u64; N]` is `does not yet support ... function pointer types`, so the Rust rungs use a trait object, and that costs **exactly 3.00000 Ir per dispatch** | §0a, §8a |

## The rungs, and the numbers

`Ir` per call at `-O3`, `isolated`. Every law is exact over twelve swept points
with **zero residual**, and confirmed out of sample at `nrw = 1024`:

| rung | file | law, Ir/call | `small` | `large` |
|---|---|---|---:|---:|
| R1 | `c/kernel.c` | `10.00000·nrw + 39` | 1319 | 10279 |
| R1h | `c/kernel_hardened.c` | `12.00000·nrw + 38` | 1574 | 12326 |
| R2 | `safe_naive.rs` | `27.00000·nrw + 42` | 3498 | 27690 |
| R3 | `safe_tuned.rs` | `13.00000·nrw + 46` | 1710 | 13358 |
| R4 | `unsafe.rs` | `13.00000·nrw + 31` | 1695 | 13343 |
| R5 | `verus.rs` | `13.00000·nrw + 31` | 1695 | 13343 |

**`R3 − R4 = 15.00 Ir per CALL and 0.00000 per record** — the bounds checks are
entirely outside the loop, and the listing shows no `cmp`/`jae` against a length
in R3's loop body at all.

⚠ **The R4 side was searched before that was published, and it changed what
ships.** The R2-shaped unsafe rung — what every other pattern here uses as its
R4 — verifies and is **1022 / 8190 Ir/call dearer**; shipping it would have
published *safe Rust beats unsafe Rust by 1007 / 8175 Ir per call*, all of it
loop structure.
`NOTES.md` §8b.

## The headline measurement

`Ir` **exactly constant**, wall clock **3.17×**, one binary, several inputs
(`NOTES.md` §7):

| targets | `Ir`/call | min ns/call (Rust R4) | min ns/call (C R1h) |
|---:|---:|---:|---:|
| 1 | 3359.0000 / 3110.0000 | 439.07 | 373.78 |
| 2 | 3359.0000 / 3110.0000 | 648.91 | 439.16 |
| 4 | 3359.0000 / 3110.0000 | 1255.87 | 768.87 |
| 8 | 3359.0000 / 3110.0000 | 1390.91 | 1182.23 |

Noise floor on byte-identical copies: **4.19%**. And a clean negative:
**callgrind's simulated indirect-misprediction rate does not order the wall
clock** — the blob it says mispredicts 99.87% is among the fastest.

## Two things a reader should not miss

1. **A Verus `spec fn` declared in a trait occupies a vtable slot in the erased
   build.** Declare the ghost item *after* the exec one or R5's dispatch is
   `call *0x20(%rcx)` where R4's is `call *0x18(%rcx)` — same instruction count,
   same byte count, different bytes. `NOTES.md` §5.
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
python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band t --wall
python3 patterns/p36-vtable-dispatch/controls/sweep_ir.py --band mix --floor 5
python3 patterns/p36-vtable-dispatch/controls/cfi_probe.py
```
