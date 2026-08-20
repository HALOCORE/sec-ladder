# p04 — ring buffer over an attacker-chosen opcode stream

A bounded FIFO ring: `uint64_t ring[64]`, two live cursors, and an opcode stream
from the file deciding per step whether to enqueue or dequeue. **The bug is a
missing fullness check, and every index it forms stays inside the array.**

```
window:  nops u32 LE, then `nops` operations of 5 bytes -- op u8, val u32 LE
RING_CAP = 64                                  a compile-time constant,
                                               A POWER OF TWO
for each operation:
    if PUSH:  if (tail + 1) % RING_CAP != head:   <<< R1 omits exactly this line
                  ring[tail] = val; tail = (tail + 1) % RING_CAP
    else:     if head != tail:                    <<< in EVERY rung
                  acc = acc*31 + ring[head]; head = (head + 1) % RING_CAP
return ((acc*31 + head)*31 + tail)*31 + nops
```

## Three reasons this pattern exists, and what each answered

### 1. The index is modular — the third operator, and it CARRIES the bound

p05 asked whether LLVM carries a bound through a **multiply**; p09 through a
**shift**, and found that the composition through a multiply is what fails. p04
asks through **`%`**, twice per operation, on two cursors that are both live
state.

**Answer: at a power-of-two capacity the bound survives completely.** The safe
indexed `ring[tail]` and `*ring.get_unchecked_mut(tail)` compile to the **same
machine-code bytes**; R3's only surviving panic landing pad is the window
reslice, decoded rather than counted; and the whole in-contract safety tax is
**`5.00000` Ir per call and `0.00000` per operation**, swept over 99 blobs with
zero residual.

The unifying statement the third data point buys:

> **What LLVM carries around a loop-carried phi is known BITS, not a range.**
> `% 64` lowers to `and $0x3f` and fixes six low bits. `% 60` fixes none — its
> fact is the range `[0, 59]` — and the range does not survive the phi.

**And the non-power-of-two control is the pattern's largest single effect.**
One edit to one constant (`controls/gen_controls.py`, `RING_CAP = 60`, with the
execution counts held fixed on `small`):

```
R3 - R4  at RING_CAP = 64 :    +5      per RING ACCESS: 0.00000
R3 - R4  at RING_CAP = 60 :  +479      per RING ACCESS: 2.00000
```

p03's dead-clamp control — hand LLVM the invariant the proof carries — takes the
CAP=60 gap back to **exactly +5**, with zero fitted parameters, and is a
**byte-identical no-op** at 64 because there is nothing left to seed. Both C
compilers behave the same way in both directions: a manual `if (head >=
RING_CAP) trap();` on the ring read is deleted byte-for-byte at 64 by gcc *and*
clang, and kept by both at 60. **Three independent middle-ends, one answer** —
so this is a fact about the operator, not about safe Rust. NOTES.md 1, 1a–1c.

### 2. Two live cursors — and the memory-safety invariant is NOT relational

`head` and `tail` are both state and both guards are *relations* between them:
`head == tail` is empty, `(tail + 1) % RING_CAP == head` is full. TASK_042
predicted that the R5 invariant would be the work.

**It is not, and it is not relational.** What the two trusted accessors need is

```
head < RING_CAP,
tail < RING_CAP,
```

two **independent one-variable** clauses, each discharged from its own
`% RING_CAP` and from no guard at all. Verus takes the whole file **`9 verified,
0 errors` on the first run**, with no lemma, no `by (nonlinear_arith)` and no
proof block beyond the two the shared driver already needs.

### 3. The bug stays in bounds — and that is the SAME fact as (2)

Drop the fullness check and a push onto a full ring stores into the one slot the
checked kernel keeps reserved, then advances `tail` onto `head`: the ring reads
**empty** and 63 live elements become unreachable. No index leaves
`[0, RING_CAP)` in any rung, on any input. So:

| mechanism | verdict on `adversarial-overwrite.bin` |
|---|---|
| ASan + UBSan (the gate's own flags) | **clean, exit 0** |
| Miri on `unsafe.rs` | **no UB** |
| safe Rust's bounds check | **never trips** |
| the R5 proof's **memory-safety** obligations | **`9 verified, 0 errors`** with the check deleted |
| the R5 proof's **functional** `ensures` | **fails** — *invariant not satisfied at end of loop body* |
| the checksum | **2153 against R1's 448** |

The `_msonly` probe is p09's, and it is **not blind**: five positive controls
fail it — `assert(false)` in three separate places, `ring[tail + 1]`, and the
same guard-free push with the `%` removed (which fails on the very invariant the
bug satisfies).

**And (2) and (3) are one sentence, which is the pattern's result:**

> **The relation between `head` and `tail` is exactly the part of the state the
> memory-safety obligation does not need — which is precisely why deleting
> either guard is invisible to it.** A ring buffer's indices cannot run away;
> that is why it is the data structure you reach for, and it is why memory
> safety has nothing to say about it going wrong.

Second instance of p09's result, and the first where the mechanism is visible in
the invariant rather than inferred from a probe. It is also stronger than p09's
in one respect: **both** of p04's guards are invisible, not one substitution.

## The ladder, `-O3 isolated`, kernel-exclusive Ir per call

| rung | small | large | vs R4 | what it is |
|---|---:|---:|---:|---|
| R1 c-gcc | 3842 | 13336 | +14.2% | no fullness check — THE BUG |
| R1h c-gcc-h | 4318 | 15004 | +28.4% | the same file plus that one `if` |
| R1 c-clang | 2872 | 9979 | −14.6% | |
| R1h c-clang-h | 3230 | 11234 | −4.0% | |
| **R2 safe-naive** | **8119** | **28278** | **+141.4%** | indexed `buf[..]`, five checks per operation |
| **R3 safe-tuned** | **3368** | **11667** | **+0.149%** | one window reslice; the ring index is free |
| **R4 unsafe** | **3363** | **11662** | 0 | `get_unchecked` throughout |
| **R5 verus** | **3363** | **11662** | **0.00%** | byte-identical to R4 (`md5_raw 1be5994704b2`) |

Swept over 99 blobs in four bands, **max residual 0.0000**, pooled design **rank
5/5** (no band and no *pair* of bands identifies the terms — the pooling is
load-bearing):

```
  safe_tuned (R3)  = 13·xpush + 9·dpush + 15·xpop + 8·epop + 51
  unsafe     (R4)  = 13·xpush + 9·dpush + 15·xpop + 8·epop + 46
  R3 - R4          = 5.00000, FLAT
  R1h - R1         = +4.00000 per accepted push, both compilers
  R2 - R3          = 20.00000 per operation + 11      <-- p03's law, exactly
```

`large` is 3.5× outside every band and the laws predict it to the instruction.

Wall clock (`common/layout/order.py` first, 31 byte-identical copies, two
passes, three schedules): **R2 is +25.7% on `small` and +9.7% on `large`** for
+141% of instructions — a conversion factor of 5.5× / 14.7× — and **`R3 − R4` is
a clean null** (−0.30…+0.71% against a 0.64…6.03% floor), which is the null the
`Ir` column predicts. NOTES.md 11.

## What is here

| file | |
|---|---|
| `spec.md` | the contract, the hashed `slb-contract` block, the `idiom` declaration |
| `model.py` | the independent Python reference — two implementations, checked against each other |
| `inputs/gen.py` | 5 matrix blobs + 4 sweep bands (99 blobs), deterministic, verified byte-identical over two runs |
| `c/` | R1 (`kernel.c`, the bug), R1h (`kernel_hardened.c`), the driver |
| `safe_naive.rs` `safe_tuned.rs` `unsafe.rs` `verus.rs` | R2–R5 |
| `controls/gen_controls.py` | 31 controls: the `RING_CAP = 60` build, the R3/R4 spelling searches, the C-side bounds check, four proof mutants and the eight-file `_msonly` family |
| `NOTES.md` | every number, with the command that produced it |

**TCB: 10 lines across 5 items, three of them `unsafe`** — the gate's own
`tcb_items` total, re-read from `results/gate/p04-ring-buffer.json` rather than
counted by hand. Two accessors and one **store**; NOTES.md 5 has the tally and
the three `SLB-TRUSTED-ARGUMENT` blocks.
