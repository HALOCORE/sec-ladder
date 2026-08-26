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
| in-contract R3 span | **2991.00 … 3719.00** probe-`Ir`/call, twelve spellings, median band — ⚠ **both endpoints corrected at TASK_106**; the cheapest in-contract R3 sits **inside** the R4 span (`NOTES.md` 9b′) |
| R1 − R1h | **+39.10 / +60.34** on gcc — i.e. **the guard's price is −39.10 / −60.34, NEGATIVE, on these two inputs**; clang flips sign between them, and the gcc sign flips **twice** across p23's own rank band (`NOTES.md` 3a) |
| harm | SIGSEGV in both directions; **silent on a one-element record, where the eight C cells print seven or eight different wrong numbers and every cell's number moves on every rebuild** (`NOTES.md` 7 — the values are deliberately not transcribed anywhere, because they cannot be); **silent and sanitiser-clean** in the in-bounds middle regime |

### ⚠ The headline is a domain warning, not a number

`R3 − R4` runs from **227.00 to 706.37 `Ir`/call — a factor of 3.11 — with the
element count, the record count and the copied-byte count all held constant.**
The only thing that moves is the **pivot's rank**. The two-term law in
(records, bytes) fitted on the extent band predicts 416.32 for every one of
those points. **p23 is the first pattern here whose safety tax is a function of
the data's SHAPE rather than its SIZE.**

Measured at all **109** shipped points — every point of all four sweep bands
plus `small` and `large` — the tax closes exactly:

> **`R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ τ(m mod 4)`**, `τ = {0,
> 2, 3, 4}`, **max |residual| 0.0000 `Ir`/call**, with the coefficients fitted on
> two bands and the other 38 points predicted to 0.0000.

⚠ **Its band-K spelling, `242 + 2·dn + 2·sw − 3·rounds`, is exact on band K and
wrong by up to 480 `Ir`/call off it.** `NOTES.md` 9c″ is about why, and it is the
sharper half of the domain lesson.

### ⚠ And the mechanism is a new one — as a PHENOMENON. Its CAUSE is open.

Isolating the two scans: **LLVM already elides the upward scan's bounds check
and does not elide the downward one's** — unchecking the downward read alone
produces the same disassembly as unchecking both. **An elision asymmetry between
two scans of the same array under the same bound is new in this tree.**
⚠ **Why is OPEN.** The explanation this row shipped with — *"`j` decreases from a
runtime value and the index is an unsigned subtraction"* — **failed both of its
isolations**: making the cursor ascend costs **+816 / +1614 / +1313**, removing
the subtraction recovers **16 / 12 / 20** of a **488 / 184 / −14** gap, and —
the third measurement, and it points the opposite way — giving the *upward* scan
that same descending, subtracting shape makes it **512 / 262 / 15 probe-`Ir`/call
CHEAPER** on the same band, and cheaper than the fully unchecked kernel at two of
the three ranks. See `NOTES.md` 9d.

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
