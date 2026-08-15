# TASK_006 — retract p02's perf claim, close the reopened bypass, fix the floor

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_004_REVIEW.md` (this task is its
remediation — it has every measurement and variant already built), then
`patterns/p02-buffer-copy/NOTES.md`.

## Why

p02's **security** result survived review intact and is the project's first real
finding. Its **performance** headline — "safe-naive Rust pays an O(n)
bounds-check tax" — was refuted. The mechanism written into `NOTES.md` is false,
and a reviewer demonstrated it by changing one loop at a time.

The manager has already corrected `.memory/01-ladder.md`, `.memory/02-bench-rules.md`
and `.memory/04-verus.md`. **Do not re-apply those.** Your job is the pattern's own
files, the harness, and the one new gate stage.

## Part A — retract and restate p02's perf claim

`NOTES.md:36-38`, `:216-220`, `:218` and `README.md` where it repeats.

The refutation, all measured (`-O3 isolated`, marginal Ir/call, all
checksum-identical to `model.py`):

| variant | 61 B | 4092 B | vs R4 |
|---|---:|---:|---|
| R2 as shipped | 407.0 | 11226.0 | +178 / +1025 |
| `copy_from_slice`, **indexed fold kept** | 239.0 | 10210.8 | +10 / +10 |
| indexed copy kept, **one `&src[a..b]` reslice** | 239.0 | 10210.8 | +10 / +10 |
| R2 verbatim, check written **additively** | 237.0 | 10208.8 | +8 / +8 |

Changing only the fold moves nothing; changing only the copy removes all of it.
R2's and R4's fold loops are the *same* 19-instruction unrolled body — **the
indexed fold's bounds checks cost zero.** The cause is that
`len > src.len() - (src_off + 2)` (subtraction-first, which `spec.md:44-48`
mandates for sound overflow reasons) leaves LLVM unable to prove the index bound,
so loop-idiom recognition never forms a `memcpy`. One operator flips
`bulk_calls []` → `['memcpy@GLIBC_2.14']`, 118 → 87 instructions.

So the comparison was inline SSE2 copy vs `call memcpy` — different algorithms —
and **C written the same way pays the same** (clang +532; gcc's byte loop is 94 Ir
*faster* than glibc's memcpy).

Rewrite the claim as what it is: **rustc failed to idiom-recognise one spelling of
a byte-copy loop; three other spellings, including the reslice a competent Rust
programmer writes, are +10 flat.** That is a codegen-fragility finding and worth
publishing as one. Keep the shipped R2 (it is a *fair* naive port — a real
programmer does write that), but report it beside the variants so the number is
never read as a safety tax.

Also fix the two-point slope: `gen.py` pins residues mod 4 and mod 8, but this
codegen's epilogue swings **±175 Ir on `len mod 16`** — 2048→2049 makes R2 174
instructions *cheaper*. Extend the residue rule to mod 16, **run `gen.py --sweep`**
(it exists and was never run), and publish the curve, not two points.

## Part B — close the reopened driver-loop bypass (major 3)

`harness/dloop.py:139`, `:466`. `_GHOST_RE` is applied to **every Rust rung**, not
only inside `verus! {}`. Three payloads insert into `safe_naive.rs`'s measured
loop, normalise to the canonical sequence, keep `statements = 13`, and print the
correct checksum:

| payload | marginal Ir (baseline 407.0) |
|---|---:|
| `assert!(k < nrec as usize);` | 409.0 |
| `let ghost = black_box(src[k * stride]);` | 411.0 |
| `let ghost = unsafe { _mm_prefetch(...) };` | **417.0** |

The third is the M9 prefetch payload, back again. `assert!` is **live code in
release Rust** — `-C debug-assertions=off` removes only `debug_assert!` — and the
argument that got `assert` excluded from the C path was applied C-only. `let ghost`
is worse: it admits an arbitrary expression including an `unsafe` block.

Fix: gate `_GHOST_RE` on `vparse.verus_span` rather than on `lang == "rust"`.
Demonstrate all three payloads failing afterwards.

## Part C — clause-deletion mutation as a gate stage (major 4)

The M7 write-up was wrong and the manager has corrected `.memory/04-verus.md`:
the mutant is **not** vacuous (`assert(false)` remains unprovable), it is a silent
*strengthening* that injects a usable false fact. Also: **neither of `copy_bytes`'s
two `ensures` clauses is individually load-bearing** — deleting either leaves
9 verified / 0 errors.

Implement the check the reviewer measured as working: **for each `ensures` clause
of each `external_body` item, delete it, re-run Verus, and fail if the file still
verifies with 0 errors.** Derived, not declared, so it does not inherit the
self-certification problem. ~20 s per Verus run; 4 runs on p02. Add the
`assert(false)` probe alongside it (it catches genuine vacuity) but do not present
it as the detector for this class.

Then fix p02's `copy_bytes` so each retained clause is load-bearing, or collapse
the two into one strong clause.

## Part D — the anti-collapse floor (major 5)

ALPHA = 0.25 Ir/byte is **2.4× above what glibc `memcpy` achieves** (0.104
measured), so a bulk-copy-dominated kernel cannot satisfy the floor: bare copy +
8-byte fold is 0.118 (fails at 0.47×), and the word-wise fold is only 1.37× clear.
Worse, p02 as shipped clears the floor on the **fold alone** — the stage never
certifies the copy happened.

Fix per `.memory/02-bench-rules.md`: derive ALPHA per pattern from `model.py` (a
declared *cheapest legitimate* Ir per work unit — a claim about the algorithm, not
about this kernel), or denominate `work_per_call` in a unit whose cheapest correct
implementation exceeds ALPHA. **Do not simply lower ALPHA**; that removes the only
thing the stage does.

Note the fold question is settled and needs no action: keep the full-extent fold.
The feared elision does not happen (measured — LLVM will not narrow a copy into a
caller-visible `&mut [u8]`), and the copy can never exceed ~50% of any kernel that
folds every byte.

## Part E — minors

`harness/asm.py:83` — `is_bulk_symbol` returns `False` for
`__memcpy_avx_unaligned_erms`, `__memcpy_chk`, `__memmove_chk`, `__memset_chk`.
This box's gcc default-enables `_FORTIFY_SOURCE 3`, so a kernel emitting
`__memcpy_chk@plt` is a **live** false-fail. Fix and add cases to the selftest.
`NOTES.md:479-483` overstates the relaxation's necessity (exactly one of 32 cells
needs it, an `O0` row, and it needs the v0-mangling extension rather than the bulk
regex). `NOTES.md:107-113` misattributes `_FORTIFY_SOURCE`: this is Ubuntu 24.04,
gcc 13.3.0, level **3**. `NOTES.md` §0 understates gcc's fold vectorisation — gcc
*does* fully vectorise it (`movdqu` + unpack ladder into 4 `paddq`), which is a
codegen-grounded hypothesis for the 10%-fewer-Ir / 23%-more-wall-clock inversion.

## Done when

The perf claim is restated with the variant table and a swept residue curve; all
three Part B payloads fail the driver diff; the clause-deletion stage exists and
flags `copy_bytes`'s redundant clause; the floor no longer forbids a bulk-copy
kernel; `check.py p01` and `check.py p02` both green on **complete** runs.

## Constraints

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`,
`PLAN.md`, `pilot/README.md`, or the three `.memory/` files the manager just
corrected. If a prescription here is wrong, say so with the measurement — four
engineers have now done that and all four were right.
