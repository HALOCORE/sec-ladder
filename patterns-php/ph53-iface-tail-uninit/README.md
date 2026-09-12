# ph53 — storage grown to the COUNT, and the tail is never written

**PHP 5.0.0 · `Zend/zend_compile.c:2569-2572` · corpus row CRASH-158 ·
CWE-824 · tier `narrowed` · the first `T3` row (*initialised before read*).**

`ce->num_interfaces` is advanced once per `implements` clause **at compile
time** and no slot is written (`:2591`); `:2570-2571` then grows the storage to
that count and leaves it indeterminate. A consumer that runs before every
`ZEND_ADD_INTERFACE` has executed reads a slot nobody wrote.

⚠⚠⚠ **The read is IN BOUNDS.** Inside the reallocated block, nothing freed:
**CWE-824**, not CWE-125. No built row in either programme prices that. `ph32`
is the cross-reference and not the duplicate — same C shape, sized to the
*literal*, so its excess is past the end.

## Read these three things, in this order

1. **`NOTES.md` §5** — *what the 2005 upstream fix actually buys, per
   consumer.* `d09cdd9f71f3` (`erealloc` → `emalloc` + `memset`) adds **no
   consumer guard**, so it turns a wild-pointer dereference into a
   **deterministic NULL dereference** at `zend_operators.c:1535` and a
   **correct answer** at `zend_compile.c:1951`. **One hunk, two severities.**
   Measured under ASan+UBSan in `controls/r1h_consumers.py`, and then sharpened
   in `controls/wild_choice.py`, which *chooses* the wild value instead of
   observing it and shows the comparing consumer giving a **silent wrong
   answer** on R1 that the fix really does remove.
2. **`NOTES.md` §11** — *the obligation is not dischargeable over a faithful
   R4.* Coverage is a property of the op stream, i.e. of attacker data, and the
   pinned driver loop offers no call site at which to establish it, so **a rung
   that reproduces the defect cannot be verified and a rung that verifies does
   not reproduce it.** The shipped R4/R5 therefore carry a one-byte-per-slot
   witness the C does not have; `controls/r4_nowitness.rs` is the faithful
   program, measured, Miri'd and refused by Verus with its error text.
3. **`NOTES.md` §8** — the numbers, each with its mechanism, and the four
   predictions `TASK_PHP_040_REPORT` §5.6 made. **Three of the four are
   refuted** and §8d, §8f, §8g and §11 say how.

## The ladder, in one table

Four answers to one question — *was this slot written?* A1
(`Ir(kernel)/call`, `O3 / isolated`, `small.bin`), against R1 = `c-gcc`:

| rung | how it answers | A1 vs R1 |
|---|---|---:|
| **R1** `c/kernel.c` | it does not; the tail is indeterminate | — |
| **R1h** `c/kernel_hardened.c` | zeroes the storage and **still faults** | **+0.231 %** |
| **R2** `safe_naive.rs` | `Option<u32>` — 8 bytes per slot, a discriminant load and a branch per read | +6.967 % |
| **R3** `safe_tuned.rs` | it does not need to: `Vec::len()` carries it — php-5.2.0's own repair | +0.809 % |
| **R4** `unsafe.rs` | one byte per slot in a stack array | −18.858 % |
| **R5** `verus.rs` | the same, plus the proof that the byte is enough | −19.875 % |

⭐ **R2 is not *"php-5.0.5's repair reinvented"* — it is that `memset` PLUS the
consumer guard upstream never added**, because `if let Some(p)` is the only
expression that reaches the value at all.
⭐ **The proved rung is cheaper than the unsafe one at both levels**, with no
search: `−1.253 %` A1. Third row in the corpus where that happens; `NOTES.md`
§10 says why it is a register-allocation fact and not a cost of proof.

## What is here

| | |
|---|---|
| `spec.md` | the contract and the pins. `contract_sha256` as first written is in `NOTES.md`'s first box |
| `c/kernel.c` | R1 — PHP 5.0.0, narrowed. **The bug** |
| `c/kernel_hardened.c` | R1h — plus `d09cdd9f71f3` whole. ⚠ **NOT the sha the corpus column gives**; both are cited in `spec.md` and both patches are in `controls/` |
| `safe_naive.rs` `safe_tuned.rs` `unsafe.rs` `verus.rs` | R2–R5 |
| `model.py` | three independent implementations, a 90-window synthetic sweep, and three must-fire mutants of the sweep itself |
| `inputs/gen.py` | the corpus, with `_check_arms` re-deriving its coverage from the bytes it just wrote |
| `controls/r1h_consumers.py` | §5a — what the fix buys, per consumer, under the gate's own sanitizer line |
| `controls/wild_choice.{c,py}` | §5b — the wild value **chosen** rather than observed, by priming the shim's size-class cache |
| `controls/negatives.py` | four must-fire Verus mutants, TWO must-NOT-fire, four Miri arms, the witness's cost, and a guarded kernel fingerprint |
| `controls/mu_unwrapped.rs` | ⭐ the obligation **unwrapped** — the same `MaybeUninit` operations with **no trusted item at all**, letting vstd's own spec carry it, 7/0. It is what stands in for `slot_read_unchecked`'s twin, which cannot exist (`NOTES.md` §11.5) |
| `controls/r4_nowitness.rs` | the faithful unsafe port — **a control, never a rung** |
| `NOTES.md` | the measurements and the four trusted-item arguments |

## ⚠ What this row does not have

* **No `controls/spellings.py`.** The R3 and R4 endpoints are **UNSEARCHED**,
  so every figure in `NOTES.md` §8c is a `fixed-R4 bound` over an unsearched
  endpoint and must be quoted as one. `ph03`, `ph45` and `ph64` carry the same
  debt; this row makes it **4 of 7**. ⭐ The named candidate for a cheaper R4 is
  a **`u32` bitmask witness** — `n_decl ≤ 16` fits in one word — and `NOTES.md`
  §8e is the number it has to beat.
* **No `adversarial-deref.bin`, and there cannot be one.** `check.py` stage 7h
  requires R1h clean on every input in `inputs/`, and the fix does not remove
  the fault, so the input that shows the row's headline would fail the gate.
  That is `.memory-php/02-ladder.md` **F31** binding on a real row for the
  first time; the evidence is in `controls/`. `NOTES.md` §5.
* **No claim that the tier is measured.** `narrowed` is a judgement and
  `NOTES.md` §2 gives the argument for `modelled` that was not taken.
