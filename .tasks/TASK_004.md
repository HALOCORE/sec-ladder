# TASK_004 — p02, length-prefixed buffer copy (the first pattern with a real bug)

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.memory/02-bench-rules.md`,
`.memory/05-layout.md` ("adding a pattern" checklist), `patterns/p01-array-sum/`
as the worked template.

**Status: draft — do not start until the manager marks it ready.** It may be
amended by the outcome of `.tasks/TASK_003_REVIEW.md`.

## Why this pattern

p01 is a calibration kernel: no bug, an adversarial input that makes zero kernel
calls, and R4 ≡ R5 byte-identical so nothing about the harness's hard paths was
exercised. p02 is the first *real* one, and it deliberately stresses the four
things p01 could not:

1. **A genuine memory-safety bug** — attacker-controlled length copied into a
   fixed buffer. The classic OOB write.
2. **An adversarial input that actually reaches the kernel**, so the contract
   evaluation on adversarial inputs (fixed as B3 in TASK_003) is exercised for real.
3. **A likely R4 ≠ R5**, which is the case the Miri policy and the identity
   "record, don't gate" path were written for and never tested.
4. **Harness genericity** — a different kernel signature, a different payload
   layout, a different `model.py`. Every place the harness is secretly p01-shaped
   will surface here. Report each one.

## The kernel

Fixed contract, all rungs (exact signature in `spec.md`):

```
kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64
```

- Read a little-endian `u16` length prefix at `src[src_off..src_off+2]`.
- Copy that many bytes from `src[src_off+2..]` into `dst`.
- Return a value derived from what was copied (so the result is consumed and the
  copy cannot be dead-coded) — e.g. a wrapping fold over the copied bytes.

`dst` is a fixed-capacity buffer, deliberately smaller than the largest length the
prefix can express. That gap is the vulnerability.

## The rungs

Per `.memory/01-ladder.md`, plus **one addition specific to this pattern**:

| rung | behaviour |
|---|---|
| **R1 C** | idiomatic C that **trusts the length prefix** — `memcpy(dst, src+off+2, len)`. This is the bug. |
| **R1h C-hardened** | *new cell.* Same C, plus the explicit bounds check a careful C programmer writes. |
| **R2 safe-naive** | mechanical safe Rust; bounds-checked by the language. |
| **R3 safe-tuned** | `copy_from_slice` on a checked subslice, or equivalent. |
| **R4 unsafe** | `copy_nonoverlapping` / `get_unchecked`, check hoisted — correct but unverified. |
| **R5 verus** | R4's exec code with the check's sufficiency proved. |

**R1h is the point of this pattern.** With only R1, "C is faster" and "C is unsafe"
are confounded — C is faster *because* it skipped the check. R1h separates them:

- R1 vs R1h = **what the check costs, within one language**
- R1h vs R4 = what Rust's unsafe rung costs against safe C
- R1h vs R2/R3 = what Rust's *additional* machinery costs beyond the bare check

If R1h ≈ R2/R3, the honest headline is "safety costs the same in both languages,
and Rust just makes it non-optional" — a much stronger result than anything p01
could produce. Add R1h to `.memory/01-ladder.md` as a standard cell if it works;
report if it does not generalise.

## Inputs

Per `.memory/02-bench-rules.md`. Specifically:

- `small` / `large` — well-formed records, every length ≤ `dst` capacity.
  **Different residues mod 4** (this trap has been stepped in three times).
- `adversarial` — length prefix exceeding `dst` capacity. Must reach the kernel
  and must be the input the C bug fires on. Include a boundary case
  (`len == cap`, `len == cap+1`) and the maximum `u16`.

## Deliverables

Standard pattern layout, plus:

- `NOTES.md` records the **adversarial behaviour table** — per rung: exit code,
  stdout, stderr, ASan/UBSan verdict, panic or not, and for R5 what the proof
  rules out. This table is the security half of the result and it is the first
  time the project produces one.
- The R4/R5 identity level, whatever it is. **If they differ, that is a finding,
  not a failure** — record where and why. Do not contort R5 to force identity.
- Every place the harness needed a change to accept a second pattern, listed
  explicitly. That list is the real test of TASK_003's genericity claim.

## Constraints

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`, `PLAN.md`,
`pilot/README.md`. `harness/check.py p02` must be green on a **complete** run
(`results/gate/p02-buffer-copy.json`, `complete_run: true`) before you report —
and if a legitimate property of this pattern makes that impossible, say so rather
than weakening a pin to get green.
