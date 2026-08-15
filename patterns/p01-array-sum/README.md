# p01 — array sum over a window

**Calibration pattern. It models no bug.** Its job is to establish that the
harness, the driver, the input format and the five-rung ladder all work, and to
give every later pattern a number to be compared against. It supersedes
`pilot/`, which is frozen.

The kernel: sum `v[off .. off+len)` with wrapping `u64` addition. The full
contract, including the payload layout and the driver loop, is in
[`spec.md`](spec.md).

## Why this pattern is worth building even though nothing is broken

Three things it settles, none of which is about array summing:

1. **The benchmark does not evaporate.** A pure kernel called `n_iters` times on
   the same data is exactly what LLVM CSEs away. Here the window offset is
   derived from the running checksum — `off = acc % nwin` — so call *i+1*
   depends on call *i*'s result. `harness/check.py` proves the loop survived by
   disassembling every one of the 28 built cells and requiring a backward
   branch, a memory operand and a body above a floor. No `black_box`, no
   `asm volatile`, and therefore no C-vs-Rust asymmetry in the barrier.

2. **A Verus proof costs zero instructions, and buys nothing on its own.** R5's
   kernel is byte-identical to R4's, and the R2v control (`safe_naive_verus.rs`,
   safe Rust + the same proof) is byte-identical to R2's. Both halves of
   `.memory/01-ladder.md` finding 1, on a real kernel rather than the toy.

3. **The proof covers what is measured.** R5's `requires` is
   `off + len <= v.len()` — a shape property the driver establishes at run time —
   and its `ensures` is full functional correctness under wrapping addition.
   There is deliberately no precondition on element *values*, so `small`,
   `large` and every `adversarial-*` input is inside the verified domain by
   construction. The pilot got this wrong in both directions; see
   `.memory/02-bench-rules.md`.

## The rungs

| Rung | File | What it is |
|---|---|---|
| R1 | `c/kernel.c` | `acc += v[off + i]`. No length, no check. Built with gcc **and** clang. |
| R2 | `safe_naive.rs` | `acc.wrapping_add(v[off + i])` — checked index, zero `unsafe`. |
| R3 | `safe_tuned.rs` | `v[off..off+len].iter().fold(...)` — one reslice, then no per-element check. Zero `unsafe`. |
| R4 | `unsafe.rs` | `get_unchecked(off + i)`. Correct; nothing checks that. |
| R5 | `verus.rs` | R4's exec code plus the proof that discharges it. |
| R2v | `safe_naive_verus.rs` | **Control, not a rung.** R2's exec code plus the same proof. Not in the measured matrix. |

Never report R2 as "the cost of safe Rust" without R3 beside it — on the pilot
that overstated the cost by ~3.7x (`.memory/01-ladder.md`).

## Inputs

`python3 inputs/gen.py` (deterministic, seed `0x5EC1ADDE`; the `.bin` files are
gitignored).

| file | shape | why |
|---|---|---|
| `small.bin` | 2 000 u64 = 16 kB, win **501**, 200 000 iters | working set fits L1; 501 not 500 so `small` and `large` sit at different `win_len mod 4` (`inputs/gen.py`, `.memory/01-ladder.md` residue trap) |
| `large.bin` | 1 500 000 u64 = 12 MB, win 4 096, 20 000 iters | past L2/L3, memory-bound |
| `adversarial.bin` | `n_iters = 0` | the loop must never run |
| `adversarial-empty.bin` | `payload_len = 0` | no header word at all |
| `adversarial-headonly.bin` | head word, no values | `win_len > v_len` with `v_len = 0` |
| `adversarial-shortlen.bin` | declares 4 096 bytes, carries 40 | the length field lies |
| `adversarial-winbig.bin` | `win_len = 2^40` | too big, and too big for `u32` |
| `adversarial-win0.bin` | `win_len = 0` | empty window; `nwin` would be `v_len + 1` |

p01 models no memory-safety bug, so its adversarial set is the degenerate
*shapes* — the inputs that catch a sloppy driver rather than a sloppy kernel. All
seven rungs agree on all of them (they are shape errors, and every rung rejects
or skips identically); the per-rung behaviour table is `harness/check.py`
section 4.

## Running it

```bash
python3 patterns/p01-array-sum/inputs/gen.py
python3 harness/build.py p01 --all        # 28 builds -> .temp/build/p01/
python3 harness/check.py p01              # the gate
python3 harness/measure.py p01            # -> results/p01-array-sum.json
python3 harness/report.py p01             # -> results/tables/p01-array-sum.md
```

Findings, TCB tally and proof sticking points: [`NOTES.md`](NOTES.md).
