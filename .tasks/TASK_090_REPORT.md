# TASK_090 — probe `p24`'s R5: report

**Role: research engineer (probe).** Ran concurrently with `TASK_089`.
**UNREVIEWED.** All work in `.temp/t90/`; no `check.py`, no `measure.py`, no
`--cargo`, no writes outside it.

**PROTOCOL rule 2 running count: 253 → 256.**

---

## ✅ IT CLOSES. IT DID NOT STALL.

```
v24_sift.rs                 4 verified, 0 errors
v24_heapify.rs              6 verified, 0 errors
v24_specsanity.rs           2 verified, 0 errors
v24_r5.rs                   6 verified, 0 errors
v24_r5.rs --cfg slb_twin    8 verified, 0 errors
```

**The bar, precisely.** `heapify(v: &mut [u64])` **requires nothing about heap
order** (only `old(v)@.len() <= usize::MAX/2 - 2`, an overflow bound) and
ensures, **unconditionally and in the POSITIVE direction — not `res ==> …`**:

```
final(v)@.len()        == old(v)@.len(),
final(v)@.to_multiset() =~= old(v)@.to_multiset(),
is_heap(final(v)@),      // forall i: 0 <= i < len ==> heap_at(final(v)@, i)
```

⚠ **Whole array, not a subtree** — mutant **M6**, weakened to the subtree-only
`heap_at(final(v)@, start)`, **fails**, so the whole-range form is exactly what
`heapify` consumes. A real call site verifies; `assert(false)` after it fails;
the compiled R5 binary prints `top = 9` for `[1,9,5,3,7]`.

**Mutants, control 6/0 — 7 of 8 fail:** `assert(false)`; sift never swaps;
comparison flipped; **p24's own `2*i+2 <= n` bug** (*precondition not
satisfied*); heapify starts at 0; **parent-dominance invariant deleted**;
subtree-only postcondition. ⚠ **M7 is the intended TASK_085-style vacuity
control and PASSES: with the multiset clause deleted, a body that ZEROES THE
ARRAY still satisfies `is_heap`.** **The multiset clause is what carries the
anti-vacuity weight.**

**Twin teeth — all three weakenings pass ordinary Verus and only the twin moves:**
deleting `get_unchecked`'s `requires` → twin `7 verified, 1 errors`; same for
`set_unchecked`; `i < len` → `i <= len` → twin `6 verified, 2 errors`.

**Burden:** 141 non-comment lines, **28 proof/ghost, 25 exec**. Obligations
`swap_two` 1 + `sift_down` 2 + `heapify` 2 + `main` 1 = 6.

---

## Three contradictions

**(a) ⚠ The manager's named least-sure call is WRONG — and nothing stalls.**
heapify's invariant is `forall j: s <= j < n ==> heap_at(v@, j)`, *exactly*
`sift_down`'s pre/post pair shifted by one, so **the loop body needed no proof at
all** — one hint, `assert(2*(n as int/2) >= n-1)`, before the loop. **The real
content is inside `sift_down`:** the invariant `forall j != i ==> heap_at` is
**not inductive**, because the swap raises `v[i]` and can break
`heap_at(parent(i))`. It needs a **parent-dominance conjunct** with a ghost
parent index. **M5 proves it load-bearing.**

**(b) ⚠⚠ THE ASan/UBSan HYPOTHESIS IS WRONG — AND SO IS `TASK_086`'s UNDERLYING
MEASUREMENT.** It is not p19's storage-class artefact, and **it is not an
asymmetry at all.** 48 cells (heap / `.bss` / stack × length-visible /
laundered × 4 detector configs × gcc / clang): **ASan reports it in ALL THREE
storage classes, BOTH compilers** (`heap-` / `global-` / `stack-buffer-overflow`,
exit 1); **UBSan alone reports nothing anywhere**; plain `-O2` silent everywhere.
p19's effect needs a read far enough past the object to leave the page; **p24's
is one element past, inside the page in every storage class.**

⚠⚠ **The cause is a REPORTING BUG in `.temp/t86/harms.sh`: it does `head -4`,
gcc's UBSan report for this row is exactly 4 lines, and ASan's banner is on lines
5–6.** Re-running **TASK_086's own unmodified binary** gives exit 1 and one
`ERROR: AddressSanitizer: heap-buffer-overflow`. ⚠ **The truncation is NOT
p24-only** — re-reported with `grep`, rows **p21, p24, p26 and p41** each fire
*both* detectors, **so TASK_086's harm table could only ever show the UBSan half
for four rows.**

**(c) `+7.85 Ir`/element SURVIVES the residue check; `+22.1%` does NOT.**
18 lengths on TASK_086's own binary and convention; n=4096 reproduces to 1 `Ir`.
**No `n mod 2` effect** (even 7.857, odd 7.881, overlapping), **no power-of-two
effect**. A five-seed control at a single `n` gives a spread of **358**, and the
affine fit's max residual is 366 — **so the residual is data scatter, not a
residue class.** Honest figure: **≈7.9 ± 0.1 `Ir`/element**, with 7.85 at the
bottom of the band.

⚠ **But the PERCENTAGE steps from 27.5 % (n ≤ 1024) to 22.2 % (n ≥ 1025), and
the step is in the DENOMINATOR** — `cost.rs` clones the input inside the measured
loop, and that clone costs **1.15 `Ir`/element at n ≤ 1024 vs 8.34 at n ≥ 1025**.
`GLIBC_TUNABLES=glibc.cpu.x86_rep_movsb_threshold=1000000` collapses it
(n=2048: 16740 → 1951 `Ir`). **It is glibc `memcpy` switching to `rep movsb`,
which callgrind charges ≈1 `Ir` per byte moved.**

---

## Unsure / not done

- **Not proved:** that `v[0]` is the array maximum, sortedness, or heapsort as a
  whole. **Only heapify.**
- `heapify` carries a real extra precondition `len <= usize::MAX/2 - 2` for the
  `2*i+2` overflow. **A shipped pattern needs a driver conjunct for it** — the
  p17 route, **not free**.
- Both R5 accessors are single-clause `i < len`, so **the twin is still not
  exercised on a multi-clause contract**.
- Functional testing of the R5 exec code is one 5-element input plus the
  mutants; **no randomised differential run against a model**.
- Did not re-derive `TASK_086`'s probe-2 hashes or probe-4 vstd grep.
- ⚠ **Could not check whether the `rep movsb` effect reaches a shipped number**,
  because `measure.py` was forbidden. ✅ **Manager-resolved below.**

## Manager's disposition of (c)'s tree-wide worry

✅ **The phenomenon is ALREADY DOCUMENTED** — `.memory/03-measurement.md`
(TASK_074, PROVISIONAL): glibc picks the byte-wise `rep` paths only above a size
threshold, `memcpy`/`memmove` stay on the vector path at **0.104 `Ir`/byte** up
to *"somewhere between 8 KiB and 16 KiB"*, `memset` flips at 3 KiB — and it
records **"Blast radius checked and empty"**, p02's copies being 61 B and 4092 B.

**What this probe ADDS, and it is a real contribution:** the crossover is
**8192 bytes**, not a range — pinned by the `GLIBC_TUNABLES` control, which is a
cleaner instrument than a bisection.

⚠ **What remains genuinely open, and it is now RECAP "Owed" 28:** *"blast radius
checked and empty"* was established at **TASK_074**, and **six patterns have
landed since**. The probe's worry conflated *input size* with *copy size* — the
shipped 16 KB and 12 MB inputs are not themselves copied — **but nobody has
re-run the check over the patterns added since.**
