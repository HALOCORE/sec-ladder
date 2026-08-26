# p23 — in-place Hoare partition of a fixed scratch

**The 25th pattern.** One record declares an element count and a **pivot byte**;
the kernel copies the elements into a fixed 64-byte local and partitions them in
place with Hoare's two-cursor **nested scan**, then folds the partitioned prefix
and the partition point.

```
i = 0 ; j = m
while i < j:
    while (i < j &&) scr[i]     <= pv:  i++      <<< SAFETY LINE, half 1
    while (i < j &&) scr[j - 1] >= pv:  j--      <<< SAFETY LINE, half 2
    if i < j: swap(scr[i], scr[j-1]) ; i++ ; j--
```

`c/kernel.c` omits the two `i < j` conjuncts and nothing else.
`c/kernel_hardened.c` is that file plus those two conjuncts.

## Why this row exists

**The bound on one cursor is the other cursor, and both move.** Every earlier
bound in this tree comes from outside the loop — a header field (p05, p07, p16,
p17, p19, p36), a compile-time capacity (p03, p06, p12), a live length (p04,
p14). Here the guard compares two loop variables, and what replaces it when it
is deleted is not a wrong length but a **property of the data**: an element
strictly above the pivot for the upward scan, one strictly below it for the
downward one. Textbook Hoare partition gets that property free by taking the
pivot *from* the sub-array; this kernel is handed one, so it does not — and the
code that relies on it looks identical.

The bug class is the tree's fifteenth `index >= len`. That is not the reason to
build it; the three limbs of RECAP's replacement bar are (see `NOTES.md` 0).

## The results, in one screen

| | |
|---|---|
| gate | `PASS`, 32/32 cells, 0 failures |
| Verus | **16 verified, 0 errors, first attempt**; twin 19/0; **zero `proof fn`s** |
| TCB | 5 `external_body` items, 3 contract-bearing |
| identity | `unsafe ≡ verus` **exact** at `-O3` (`md5_fn 43acbc727fc6`, 157 insns), `norel` at `-O0` |
| R3 − R4 | **+305.74** `Ir`/call on `small`, **+443.55** on `large` … **and see below** |
| R1 − R1h | **−39.10 / −60.34** on gcc — **the guard has a NEGATIVE price**; clang flips sign between inputs |
| harm | SIGSEGV in both directions; **silent on a one-element record, with eight C cells printing eight different wrong numbers**; **silent and sanitiser-clean** in the in-bounds middle regime |

### ⚠ The headline is a domain warning, not a number

`R3 − R4` runs from **227.00 to 706.37 `Ir`/call — a factor of 3.11 — with the
element count, the record count and the copied-byte count all held constant.**
The only thing that moves is the **pivot's rank**. The two-term law in
(records, bytes) fitted on the extent band predicts 416.32 for every one of
those points. **p23 is the first pattern here whose safety tax is a function of
the data's SHAPE rather than its SIZE.**

### ⚠ And the mechanism is a new one

Isolating the two scans: **LLVM already elides the upward scan's bounds check
and does not elide the downward one's.** `scr[i]` is free because `i` is a
monotonically increasing induction variable with a proven bound; `scr[j - 1]`
costs ≈2.00 `Ir` per step because `j` *decreases* from a runtime value and the
index is an unsigned subtraction. **The whole of p23's scan-side safety tax is
which way the cursor walks.**

## Files

| | |
|---|---|
| `spec.md` | the kernel contract and the machine-readable pins |
| `c/kernel.c` · `c/kernel_hardened.c` · `c/kernel.h` · `c/main.c` | R1, R1h, the shared declaration, the driver |
| `safe_naive.rs` · `safe_tuned.rs` · `unsafe.rs` · `verus.rs` | R2 … R5 |
| `model.py` | the independent reference — nested scan in the simulation, single-step rule in the helper |
| `inputs/gen.py` | the generator; `--sweep` adds the extent, record-count, **pivot-rank** and mixed bands |
| `controls/` | `guard_equiv.py` (the refuted claim), `guard_variants.c` + `run.sh` (harm + guard spellings), `sweep_fit.py` (the law, re-fitted) |
| `NOTES.md` | every measurement, the trusted-item arguments, and what is not measured |

## Reproduce

```sh
python3 patterns/p23-partition/inputs/gen.py            # matrix inputs
python3 patterns/p23-partition/inputs/gen.py --sweep    # + the four bands
python3 harness/build.py p23
harness/check.py p23
harness/measure.py p23 --cells all
patterns/p23-partition/controls/run.sh
python3 patterns/p23-partition/controls/guard_equiv.py
python3 patterns/p23-partition/controls/sweep_fit.py
```
