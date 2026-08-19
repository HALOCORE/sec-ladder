# p03 — bounded stack over an attacker-chosen opcode stream

**The first pattern in this project whose CONTROL FLOW is in the file.** Eight
patterns came before it and in all eight the sequence of operations is fixed by
the code and only the data varies: p01/p02/p05/p16/p17 fold, p07 searches, p11
scans, p08 moves. Here the file decides, per step, whether the kernel pushes or
pops — which is what a protocol state machine or a bytecode interpreter actually
looks like, and it is why the safety obligation is a **loop invariant that has
to survive a branch the attacker picks**.

## What the kernel does

A window declares a count of 5-byte operations. Each one either pushes a `u32`
onto a fixed 64-slot stack or pops one and folds it into a hash.

```
byte 0..4   nops   u32 LE    DECLARED operation count    ATTACKER DATA
byte 4..    operations, 5 bytes each: op u8 (0 = PUSH, else POP), val u32 LE
STACK_CAP = 64

uint64_t stack[STACK_CAP] ; sp = 0 ; acc = 0
for k in 0 .. nops:
    op = buf[off+4+5*k] ; val = load_u32(off+5+5*k)
    if op == 0:  if sp < STACK_CAP: stack[sp] = val ; sp += 1   # PUSH GUARD
    else:        if sp > 0: sp -= 1 ; acc = acc*31 + stack[sp]  # POP GUARD
return (acc*31 + sp)*31 + nops
```

Full contract, and the pins the gate enforces: `spec.md`. Findings and the
proof's sticking points: `NOTES.md`.

## The C bug — a missing emptiness check, and the index goes NEGATIVE

R1 (`c/kernel.c`) has the push guard and not the pop guard. `sp` is `size_t`, so

```
sp - 1  at  sp == 0   ==   SIZE_MAX
stack + SIZE_MAX      ==   stack - 1        (wraps mod 2^64)
```

**It is not a wild address.** The read lands **8 bytes below a 512-byte local
array, inside the kernel's own stack frame**, so a plain build does not fault —
it returns a wrong answer. That is arithmetic and `NOTES.md` §0 checks it on the
disassembly. Three things follow that no earlier pattern in this project could
show:

1. **A single stray POP disables the stack for the whole call.** `sp` becomes
   `SIZE_MAX`, so `sp < STACK_CAP` is false for every later PUSH.
2. **What it reads is ASLR-dependent.** Three runs give three answers;
   `setarch --addr-no-randomize` makes it bit-stable. The checksum leaks
   something derived from a stack address (`NOTES.md` §7).
3. **A sustained underflow walks DOWN the stack** 8 bytes per POP and faults at
   exactly the 8 MiB `ulimit -s` — 1 000 000 pops survive, 1 050 000 do not.

`adversarial-underflow.bin` is the input. ASan fires on both compilers and at
the gate's own `-O1` build:

```
ERROR: AddressSanitizer: stack-buffer-underflow ... READ of size 8
  [32, 544) 'stack' (line 33) <== Memory access at offset 24 underflows this variable
```

R1h (`c/kernel_hardened.c`) is the same file with `if (sp > 0) { ... }` and
nothing else.

## The headline

Every rate below is `Δ` on the **kernel-exclusive** `Ir` column, fitted with
zero residual over 77–89 sweep blobs in three bands. `xpop` is the number of
POPs that actually pop.

| quantity | value | what it is |
|---|---|---|
| `R1h − R1` | **2.00000 Ir per executed POP** | what the *emptiness check* costs, inside C, **identical in gcc and clang** |
| `R3 − R4` | **3.00000 Ir per executed POP**, 0 on every other operation | what safe Rust's surviving *bounds check* costs |
| `R2 − R3` | **20.00000 Ir per operation** | the opcode-stream bounds checks one reslice removes |
| push-side check | **0.00000** | LLVM deletes it: the guard is in the same basic block as the index |

**One array, one compile-time bound, one function, two answers** — and the
discriminator is whether the guard sits in the same basic block as the index or
a loop invariant away from it. The pop's needs `sp <= STACK_CAP` carried across
the attacker-chosen `if op == 0` branch; **Z3 takes that in one invariant clause
with no lemma, LLVM does not take it at all**, and a dead `if sp > STACK_CAP`
handed to the optimiser drops the safe rung from 17 to 13 Ir per pop and the
unsafe one from 14 to 13 — the gap goes to **exactly zero**. That is p05's
sentence *"the price of the optimiser failing the lemma the proof proves"* on a
fact that is **linear**, which p05's could not claim.

## Rungs

| Rung | File | The stack access |
|---|---|---|
| R1 | `c/kernel.c` | `stack[sp]` with **no** `sp > 0`. The bug. |
| R1h | `c/kernel_hardened.c` | the same, guarded. |
| R2 | `safe_naive.rs` | `buf[off + ..]` and `stack[sp]`, all checked |
| R3 | `safe_tuned.rs` | window resliced once, then `w[..]` and `stack[sp]` |
| R4 | `unsafe.rs` | `get_unchecked` / `get_unchecked_mut` throughout |
| R5 | `verus.rs` | R4's exec code, plus the proof. `9 verified, 0 errors`, first run. |

## Inputs

| stem | shape |
|---|---|
| `small` | 12 windows × 1189 B (L1), 237 ops, **50% POPs**, stack half full |
| `large` | 2000 windows × 4154 B (past L2), 830 ops, **25% POPs**, stack runs full |
| `adversarial-underflow` | POP as operation 0 — **R1 reads below the array** |
| `adversarial-allpop` | every operation a POP — R1 walks 1600 B down the stack |
| `adversarial-overflow` | 96 pushes into 64 slots — the guard R1 **has**; all cells agree |
| `adversarial-count` | `5*nops` past the window — the check R1 **has**; all cells return 0 |
| `sweep-n*` | operation count 8..71 |
| `sweep-d*` | POP density 0..50%, every POP popping |
| `sweep-e*` | POP density 54..100%, the pop guard **taken** |
| `sweep-bpred`, `sweep-brand` | the branch lever: identical counts, different ORDER |

The last pair is what makes p03's branch experiment cleaner than a compiler
flag: same operation count, same POP count, same executed counts, same values,
**identical `Ir` and identical `D1mr`** — only the order of the op bytes moves,
and simulated `Bcm` goes from 0.0043 to 0.5002 per operation.
