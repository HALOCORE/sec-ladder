# TASK_047 report — p06, in-place rotate

**Role:** research engineer. **Status:** delivered; `check.py p06` PASS, complete
run, `failures []`, 28 records 0 STALE. **Not yet reviewed** — every number here
is PROVISIONAL until `TASK_047_REVIEW` lands (PROTOCOL rule 9).

**Seven of the manager's prescriptions were contradicted with a measurement.**
They are marked ⊘ below. Running count after this task: **71**.

## Delivered

`patterns/p06-rotate/` — `spec.md`, `model.py`, `inputs/gen.py`,
`c/{kernel.c,kernel_hardened.c,kernel.h,main.c}`, `safe_naive.rs`,
`safe_tuned.rs`, `unsafe.rs`, `verus.rs`, `README.md`, `NOTES.md`, and six
control scripts `controls/{gen_controls.py,build_controls.sh,verify_controls.sh,
sweep_ir.py,fit.py,wall_span.py}`. Plus `results/p06-rotate.json`,
`results/gate/p06-rotate.json`, `results/tables/p06-rotate.md`.

Nothing touched in `pilot/`, `.memory/`, `harness/`, `common/`, or any other
pattern. No `git add`/`commit`.

```
check.py: PASS   verdict PASS | complete_run True | failures []
idiom_audit {'spellings':45,'rungs':6,'pairs':136,'present':92,
             'forbidden_spellings':14,'forbidden_hits':0,
             'required_pins_nothing':0,'required_absent':2,'no_rung_entries':0}
contract_sha256 4df6391285417e6a7abab8cfdaeaf867d23fd1befcf5c6c9ba044dd723147c6a
harness/measure.py --check-stale  ->  28 record(s) examined, 0 STALE
```

`required_absent: 2` are `r %= m;` and `if (m != 0)` missing from `c/kernel.c` —
the bug itself. **`required_pins_nothing: 0`**; the six existing patterns have 11
between them.

## The three pre-registered questions, settled before any rung was built

### ⊘ 1. `R1h − R1` is SIGN-WRONG in `Ir` under clang

Pre-registered: `+1–3 Ir/record`, cycles 20–40× that. Measured on a standalone
six-kernel C probe, per record, `nelem=32, r=7`:

```
clang:  mod - bug = -11.00 = -12.00 (narrowing) + 1.00 (the div)
gcc:    mod - bug =  +1.00 =   0.00 (narrowing) + 1.00 (the div)
```

The `and` control (`rr &= 63`, no divide) isolates it: **−12.00/record** clang,
**0.00** gcc. Mechanism is p09's lost load-merge — reducing `r` proves `r < 64`,
the value stays 32-bit, and clang's 7-instruction LE decode collapses to one
`mov`. **`Ir` prices the `div` at exactly 1.00 on both compilers.**

Shipped tree, whole-program marginals, wall clock via `controls/wall_span.py`
(5 byte-identical copies, alternating, `t(200000) − t(1)`, cpu 5):

| | `Ir`/call | ns/call |
|---|---|---|
| gcc `R1h−R1` small / large | **+41.00 (+1.17%) / +95.00 (+4.74%)** | **+45.63 (+19.46%) / +88.10 (+57.09%)** |
| clang `R1h−R1` small / large | **−45.00 (−1.67%) / −108.00 (−5.65%)** | **+21.78 (+9.78%) / +15.35 (+10.56%)** |
| `R5−R4` (byte-identical kernels — the null) | 0.00 exactly | +3.00% / −1.41% |

`d_cmp-clang` and `c-clang-h` execute **2646.9640 `Ir` both** — different
programs (167 vs 164 insns, `md5_fn c0965f763fee` vs `5844f1e091cf`) — and differ
**8.5% in wall clock**.

**Hardening-side span** (`small`, both numbers per the two-number rule): shipped
`r %= m` = **+19.30% (gcc) / +10.04% (clang)**; cheapest in contract
`if (r >= m) r %= m;` = **+1.20% / +0.64%**. Factor of 16.

### ⊘ 2. Item 3's law is false; the correction is exact and parameter-free

Swept `r` 0…31 at `m=32`: **4225.00** (`r` even ≥2) / **4289.00** (`r` odd) /
**4217.00** (`r=0`), exactly, 32/32 blobs. At `m=31`: **4257.00** flat for every
`r ≥ 1`. `4289 − 4225 = 64 = 8 records × 8 Ir` = one extra swap.

A reverse of a half-open range of length `L` runs `ceil(L/2)` iterations — not
`L/2`, not `L` — so

> `swaps(m, r) = m + [m even AND r odd]`

zero fitted parameters. **The `r` coefficient is not zero and the three-reverse
decomposition is intact**; the prescribed falsifier would have fired on a
correct build.

### ⊘ 3. The regime boundary is `r > SCR`, not `r >= SCR`

`reverse(scr, 0, r)`'s highest index is `r − 1`. `adversarial-inarray`'s third
record sits at `r == 64` exactly.

## Regime 1 is identical across all eight cells

On `adversarial-inarray`: both C rungs print `12407484466270198528`; all six
checked cells print the model's `5453190234444350336`; exit 0; ASan + UBSan
**clean**. The delete-the-check controls (`controls/gen_controls.py` family A)
print **the same `12407484466270198528`** in `safe_naive`, `safe_tuned` (zero
`unsafe`) and `unsafe`. In regime 2 both safe controls panic (exit 101) at
`safe_naive.rs:102:25` / `safe_tuned.rs:105:40` while C walks p12's ladder —
silent / gcc canary 134 / SIGSEGV 139 on both compilers.

## ⊘ 4. TASK_047 item 2 refuted, in the direction it asked for

`R2 − R4 = 32.00·nrec + 13.00`, **0.00000 `Ir` per rotated byte**, `269.00` flat
over all 46 `m` in 3…48, identical at `m=31` and `m=32`. One loop at a time:

| control | unchecked loop | `R2 − control` | kernel `md5_fn` |
|---|---|---|---|
| `e_revonly` | the three reverses | **0.0000/rec, 0.0000 flat** | `48e508ddf075` — **byte-identical to shipped R2** |
| `e_foldonly` | the fold | **0.0000/rec, 0.0000 flat** | `48e508ddf075` — **byte-identical to shipped R2** |
| `e_hdronly` | the header decode | **32.0000/rec, +13.0000 flat** | `897c52ff4005` — **byte-identical to shipped R4** |

rustc emits the *same bytes* for `scr[a]` and `get_unchecked(a)` in the rotate.
Delete the reduction and safe Rust's tax **triples** (32 → 102 per record). So
**`r %= m` is the range hint that lets rustc delete safe Rust's checks** —
p03/p04's seeding result on a runtime-divisor modulus, from the opposite
direction. R3 by contrast is genuinely `O(n)`: `R3 − R4 = 2.00000 Ir/byte`
exactly (`m ≥ 4`).

## Proof

**`17 verified, 0 errors`; twin `22 / 0`; `R4 ≡ R5 exact`** (`md5_raw` equal,
`md5_fn 897c52ff4005`, 208 insns). The **functional** postcondition (rotation,
not panic-freedom) converged, because `rev_range` / `rot_left` are `Seq::new`
**closed forms** rather than recursions — all three lemmas first try, zero
`by (nonlinear_arith)` in the kernel. **TCB 6 items / 11 body lines**, recounted
against the gate's own `tcb_items`.

## ⊘ 5. Mutants — the `_msonly` design in TASK_047 does not work

| mutant | shipped | twin | caught by |
|---|---|---|---|
| `b_nored` (check deleted) | 16/1 | 21/1 | Verus |
| `b_nored_msonly` (deleted **+ ms-only spec**) | **16/1 — still fails** | 21/1 | Verus |
| `b_scrmod` (`r %= SCR`) | 16/1 | 21/1 | Verus |
| **`b_scrmod_msonly`** | **17/0** | **22/0** | **only `spec.md`'s pin** |
| `b_weakreq` (item **and** twin) | 17/0 undetected | **21/1** | **the twin alone** |
| `b_tautology` | 16/1 | 21/1 | the driver's consuming assert |

Deleting the check and weakening the spec **still fails** — a proof quantifies
over all inputs and regime 2 is *genuinely* unsafe. The separation needs a
**program** change (p17's control-2 lesson, second instance). `r %= SCR` — one
identifier from the contract — is memory-safe on every input and wrong on
exactly regime 1; compiled, it prints `415744194194585216` on
`adversarial-inarray` against the model's `5453190234444350336` while agreeing
on `small` / `large` / `degenerate`.

## Sweep

140 blobs, five bands, appended last; generator determinism verified (148 blobs
byte-identical across two runs). Pooled rank **5/5**; per band 2, 3, 4, 4.
`sweep-x08a`/`x08b` negative control: identical regressors, different bytes,
**0.003 Ir** apart on all eight cells.

**Leave-one-`m`-out** (`controls/fit.py`): worst miss **0.000** for `R1h−R1`
(both compilers), `R2−R4` and `R3−R4` on `m ≥ 4` — **and it can fail**: at
`m ≥ 3` it misses `R3−R4` by **−48.000 at m=3**, which is how the domain was
established. Out of sample on the length-heterogeneous `small` (five distinct
`m`, none in any band): predicted 173 / 334 / 41 / −45, measured **173.00 /
334.00 / 41.00 / −45.00**.

## Priced fiats

`.reverse()` / `.rotate_left()` are both **`is not supported`** at the pinned
vstd, so the *prover* already excludes them from R4 — p13's "keep, one layer
down" disposition. Price published anyway: excluding them costs the safe side
**1031 Ir/call** on `small`, **0** on `large`. Direction test: the exclusion
makes the published figure **larger** → against interest, **passes**.

The **two-step reslice** is worth exactly **1.00 Ir/call** on both blobs (sixth
pattern). In-contract R3-side span **+80…+490 (small) / +172…+286 (large)**;
cheapest found differs by blob. R4 side **degenerate** (the one variant breaks
the `identity` pin). The identity pin's own price: **4.00 / 8.00 Ir per call,
flat**.

## Problems

- ⊘ **`.memory/04-verus.md` and TASK_047 are both WRONG that vstd has no spec for
  a bulk copy.** `~/tools/verus/vstd/std_specs/slice.rs:205` ships
  `assume_specification` for `<[T]>::copy_from_slice` with
  `requires old(dst)@.len() == src@.len()`, `ensures final(dst)@ == src@`.
  Measured (`.temp/p06/vstdprobe/cfs4.rs`): with the preconditions established
  **all four obligations discharge**; what fails is carrying the mutation back
  through the `&mut [u8;64] → &mut [u8]` **range reborrow**
  (`<[T;N]>::index_mut`'s existential). So p06's `scr_load` axiomatises the
  *reborrow write-back*, not the copy — a TCB item that should not exist.
  `<[T]>::split_at_mut` **is** specified with the write-back spelled out
  (`slice.rs:185`) and is the route that would delete it. **Not taken**, because
  it changes the exec text of four rungs after every number was measured.
  **p02's `copy_bytes` comment carries the same false claim.**
- ⊘ **Deviation from the kernel contract: elements are `u8`, not `u32`.** Forced
  by the `identity` pin — `copy_from_slice` from `&[u8]` into `&mut [u32]` does
  not typecheck, and every non-bulk `u8→u32` LE route (`chunks_exact`,
  `try_into`, `from_le_bytes`) is `is not supported`, so with `u32` R4 could not
  have a verifying twin *and* the load could not have one spelling in every
  rung. Measured safe before building: with `u8` the reverses are still three
  scalar swap loops on both compilers, no `pshufb`. Documented in `spec.md`'s
  Window layout and `NOTES.md` 10a.
- **p06 does NOT inherit `.memory/02-bench-rules.md`'s WRITE rule.** Its
  threshold is `min(nelem, SCR)`, *inside* the destination's extent, so
  guard-fires and UB are independent — p06 sits with p24, not p12. First
  application of that test to a pattern being built.
- **`c-gcc` / `c-gcc-h` call NO libc routine** (gcc inlines the copy) where clang
  and Rust call `memcpy`, so the kernel-exclusive column is **not** comparable
  across compilers here (`c-gcc − R4` = +853 kernel-exclusive vs +791
  whole-program). p13's blocker 3, second pattern. Every cross-compiler figure in
  `NOTES.md` is whole-program and the file says so at the top.
- **`decreases b - a` is rejected on a two-cursor loop** (the cursors cross);
  `decreases b` is the measure that works. Every two-cursor loop here will hit
  it.

## Unsure / not done

- **No 30-layout population.** `common/layout/order.py` knows only the three Rust
  cells and p06's headline is C-vs-C, so `controls/wall_span.py` re-implements
  the identical-copy floor and the alternating schedule but **not** the
  `win32`/`jcc32` mode split. The `R1h−R1` effects are 3–19× the null, so a
  layout mode is implausible as the cause — **but that is an argument, not a
  measurement.**
- **`safe_naive − unsafe` (+6.44% / +13.39%) and `safe_tuned − unsafe`
  (+5.95% / +0.60%) in ns are reported and NOT headlined** — they are ~2× the
  ±3% null.
- **`scr_load` may be removable** (see Problems). Probes committed to
  `.temp/p06/vstdprobe/`; stopped after three attempts rather than re-measure the
  whole pattern.
- **`R3 − R4`'s per-record constant has an `m mod 8` structure** (α ∈ {3,5,19,22})
  reported per-residue rather than explained; the 2.00 Ir/byte term is exact and
  mechanism-free in the write-up.
- **No R4 variant that moves in contract was built**, so the R4 endpoint is
  stated as "degenerate", not "unavailable".
- **The `Ir`/ns sign result is one box, two compilers.** The `Ir` side is
  simulator-exact and portable; the ns side is not.
- **`patterns/p06-rotate/inputs/*.bin` (7.9 MB, 148 blobs) left in place** —
  gitignored but outside `.temp/`, so the manager's call. `.temp/p06` swept
  140 MB → 1.1 MB with an explicit keep-list (`.temp/p06/cleanup.sh`); every
  generator, probe source, `.json` and `.log` kept, plus `probe1_repro.sh` which
  rebuilds the deleted probe blobs and binaries.

## Memory updates

**None written — subagents may not edit `.memory/`.** Five corrections proposed
for the manager to land **after review**:

1. `.memory/04-verus.md` — the `copy_from_slice`-has-no-vstd-spec claim is false
   at the pinned vstd; the real limitation is the array→slice range reborrow.
   Affects p02's `copy_bytes` comment and p06's `scr_load`.
2. `.memory/04-verus.md` — `decreases b - a` fails on a two-cursor loop; use
   `decreases b`.
3. `.memory/01-ladder.md` — p06's entry.
4. `.memory/02-bench-rules.md` — the threshold table gains p06 in the "does
   **not** inherit" column; first *build-time* application of the test.
5. `.memory/03-measurement.md` — `d_cmp-clang` vs `c-clang-h`: same `Ir` to four
   decimals, 8.5% apart in wall clock, on two different programs.
