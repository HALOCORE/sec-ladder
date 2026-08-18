# p16 — TLV record walk

**The pattern:** walk a chain of length-prefixed records (tag, `u16` length,
value) inside a fixed-size window and fold every byte visited into a checksum.

**The bug class:** CWE-125, out-of-bounds **read**. A length field says the
value is longer than the bytes that remain, and a walker that trusts it folds
its way off the end of the buffer. p02 was the out-of-bounds *write*; this is
the read — the one that leaks rather than corrupts (Heartbleed's class) and that
no allocator rounding absorbs.

The exact contract, the pins the gate enforces and the argument for every design
decision are in `spec.md`. The findings, the adversarial table, the TCB tally
and the perf decomposition are in `NOTES.md`.

## Why this pattern exists

Three patterns in, every performance result on this project says the same thing:
**safety is cheap when the optimiser can see the loop.** R3 lands within ~+10
instructions per call of unsafe, flat in the size of the input, on p01 and p02
alike — and p02's apparent exception was refuted (its delta was a lost `memcpy`
idiom, not a bounds-check tax; `.memory/01-ladder.md` carries the retraction).

`.memory/01-ladder.md` also warns, explicitly, not to generalise that to
patterns with data-dependent indices, *because the interesting patterns are
precisely the ones where LLVM cannot hoist.*

p16 is the first kernel on this project where it cannot:

- the **trip count** comes from attacker-controlled data — the number of
  records in a window is whatever the length fields say it is;
- each record's **position** depends on every previous record's length field,
  so the walk is a serial dependence chain through the buffer's own contents;
- the value fold's **base index** is loop-carried through a value the attacker
  wrote, so there is no loop-invariant bound to hoist;
- and there is **no bulk-memory idiom to lose**: the fold is
  `acc = acc*31 + byte`, a serial Horner chain, so p02's escape route (the
  comparison was really `memcpy` versus an inline byte loop) does not exist.

Either outcome was a result. **What happened:** the safe-*naive* rung pays a
genuine O(n) tax and the safe-*tuned* rung does not.

| | vs unsafe, per call | denominated |
|---|---|---|
| R2 safe-naive | +2085 (small) / +17123 (large) Ir, **+69% / +72%** | **+4.2 Ir per folded byte — O(n)** |
| R3 safe-tuned | +27 / +77 Ir, +0.9% / +0.3% | `7 + 7·nrec` — O(records), nothing per byte |
| R5 verus | 0 | byte-identical to R4 |
| the C bounds check (R1h − R1) | +17…+54 | ~4–6 Ir per record |
| **wall clock, every rung** | **0** | latency-bound; all 16 `-O3` cells within 1.3% |

**Read that table as the SHIPPED PAIR and nothing wider.** p16's declaration
leaves the value fold's spelling free, by name — *"deliberately NOT restricted:
… and unrolling"* — and the per-byte rate is a property of that spelling. The
shipped rungs are 4×-unrolled by LLVM and run at **5.7500 Ir per folded byte**;
an admissible safe rung using `chunks_exact(32)` runs at **5.09375**, and one
using `chunks_exact(4)` at **6.50000**, *dearer* than shipped. So:

- **against the shipped R4, the cheapest in-contract safe rung is `−199` at
  `small` / `−2365` at `large`** — cheaper, on all 24 blobs. The published
  `+19 / +45` "in-contract minimum" is refuted (`NOTES.md` §10a.2). p16 is the
  second pattern after p17 where an admissible **safe** rung beats its own
  shipped **unsafe** one;
- **but at matched spelling the unsafe rung is cheaper on all nine blobs
  measured**, by `2 + 5·nrec` (22 / 52), so this is a fact about the shipped
  cell, not about the languages. `inf(R4) ≤ inf(R3)` holds by construction, and
  it is measured here;
- **and per byte the two are equal to five decimal places at every spelling
  measured** — six folds, difference exactly `0.00000`, because the reslice and
  the `get_unchecked` both sit *outside* the fold loop and the chunk body is the
  same instruction sequence on both sides. The per-byte safety tax on p16 is
  **zero**; what is not zero, and not a safety cost, is the difference between
  two *different* folds.

"Safe Rust costs zero per byte here" therefore stands **as a matched-spelling
statement** and only as one. Quote a per-byte rate with the fold that produced
it; difference two rates only between rungs that fold the same way.

`NOTES.md` §3 is the decomposition that earns the right to say that, and it
matters: the delta lives **entirely in the value fold** (changing only the fold
removes 98–99% of it; changing only the walk removes 1.5%), and **more than half
of it is not the bounds check** — it is the 4× unroll that the check's extra
loop exit prevents. p02's mechanism, a lost bulk-memory idiom, is measurably
*absent* here: writing the check additively moves the number by 0.1–0.3%.

And the honest other half: **it costs nothing in time.** The fold is a serial
`acc = acc*31 + b` Horner chain, so it is latency-bound at ~3 cycles/byte and
the extra instructions issue into idle slots. Quoting either column alone would
mislead in opposite directions.

## The six cells

| Rung | File | What it is |
|---|---|---|
| R1 | `c/kernel.c` | idiomatic C99, **with the bug**: trusts the length field |
| R1h | `c/kernel_hardened.c` | R1 plus the one `if`. The whole diff is three lines |
| R2 | `safe_naive.rs` | the mechanical safe port: `buf[i]`, `for j in 0..vlen` |
| R3 | `safe_tuned.rs` | reslice the header and the value, fold with an iterator |
| R4 | `unsafe.rs` | `get_unchecked` everywhere; the two tests survive |
| R5 | `verus.rs` | R4's exec code with every unchecked read discharged |

R1 and R1h are built with both gcc and clang, so the pattern has 32 cells rather
than 24 (`.memory/01-ladder.md`).

## The one thing to know before reading the proof

p02's security property was an `ensures`. **p16's is not, and cannot be.** This
kernel writes nothing; "no byte outside the window was read" is not a property
of the return value, because a kernel could read out of bounds and discard the
byte. For a read-only kernel the memory-safety claim rests **entirely on the
discharged `requires` of the trusted accessor** — `i < v@.len()`, proved at
every call site for indices the attacker's own length fields chose. The kernel's
`ensures` makes the proof non-vacuous and ties the value to `model.py`; it is
not the safety argument. `spec.md` and `NOTES.md` §5 say this at length because
presenting a functional postcondition as a security property would be the most
plausible way to over-claim on this pattern.

## Running it

```bash
python3 patterns/p16-tlv-walk/inputs/gen.py     # regenerate the .bin (gitignored)
harness/check.py p16                            # the gate
harness/build.py p16                            # the 32 builds
harness/measure.py p16                          # results/p16-tlv-walk.json
```
