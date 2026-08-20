# TASK_051 report — p18, LEB128 varint shift

**Role:** research engineer. **Status:** delivered; `check.py p18` PASS, complete
run, `failures []`, 32 records 0 STALE. **Not yet reviewed** — every number here
is PROVISIONAL until `TASK_051_REVIEW` lands (PROTOCOL rule 9).

Running count of agents that contradicted the manager with a measurement: **78**.

## §0 — the catalogue row is UPHELD, the first in five patterns

`"unbounded shift, truncation"` survives. Six-kernel C probe
(`.temp/p18/probe/kprobe.c` + `gen_probe.py`), 4 builds × 4 blobs, **all 24
values reproduce exactly** across gcc/clang × O0/O3. Four candidates rejected
with measurements (`NOTES.md` 0b):

- **`cap10`** — a different function, *and* it makes the guard statically dead,
  so there is nothing to price.
- **`cap9`** — wrong on benign input.
- **`unbnd`** — identical to guarded on all four blobs; it is p11.
- **`reject`** — a different function, needs a second live variable; priced at
  `+1.00·varints + 2.00`.

## The manager's three unverified premises: all three hold

```
O0   -C debug-assertions=off  v12 rc=0   18446744073709551615
O0d  -C debug-assertions=on   v12 rc=101 "attempt to shift left with overflow"
O3   -C debug-assertions=off  v12 rc=0   18446744073709551615
14d0e:  shlq %cl, %rax    <- variable-count, %cl loop-carried; real back-edge at 14d23
```

## ⊘ But two surrounding claims are FALSE, at the gate's own flags

- **UBSan sees it.** `-fsanitize=undefined` implies `-fsanitize=shift`; gate
  stage 7 fires on all four adversarial blobs from the shipped `c/kernel.c`
  (`shift exponent 70 is too large`). **ASan is silent**, so p18 is the first
  pattern here whose sanitizer row is UBSan's.
- **Miri sees it**, because Miri runs with debug-assertions on. ⚠ **It *panics*,
  it does not report `Undefined Behavior`** — so a gate keying on the `ub` flag
  alone would miss it.

**Honest headline: four catchers — UBSan, `debug-assertions`, Miri, Verus — all
outside the 24-cell matrix.** Not "nothing sees it".

## The row the pattern exists for

Safe Rust with the guard deleted (`n_noguard`, **zero `unsafe`**) at
`-O3 -C debug-assertions=off` is **bit-identical to C's R1 on every adversarial
blob**: `1758263303383808` / `7456158208145138176` / `7680421278058493568`, and
panics rc=101 at O0d/O3d. Same for `t_noguard` and `u_noguard`.

## Gate

```
check.py: PASS | complete_run true | invocation "p18" | 0 failures | 32/32 cells
32 cells agree on all four non-adversarial inputs
identity unsafe vs verus O3: exact
Verus 12 verified, 0 errors (twin 13/0), matching the pins
Miri 9/9 no UB | ASan/UBSan 9/9 as declared
measure.py --check-stale -> 0 STALE
```

Proof reached 12/0 on the **second** attempt (one missing invariant, `nb < len`),
well inside the one-session budget.

## Laws — exact over 34 blobs

Max residual **0.03** (the `println!` digit term).

```
c-gcc    12·b + 21·v + 51
c-gcc-h  14·b + 21·v + 51      =>  R1h − R1 = 2.00·bytes, zero intercept,
                                                          zero per-varint
```

**Both gcc coefficients derived block-by-block from the listing with zero fitted
parameters** (`NOTES.md` 4a); clang's per-varint 27 is **fitted only** and
flagged as such.

⚠ **The safety line runs once per input byte, so it does not amortise** —
**11.89%** of `small`'s kernel `Ir` *and* **11.11%** of `large`'s.

`ns`, **30-layout population per C cell**, mode-matched from the listing:
**+7.14% gcc (P = 0.976)**, **+12.04% clang (P = 0.998)**, sign stable in every
mode; identical-copy null median +0.00%, P = 0.458.

## The `O0d` decision, and why `O3d` is the number that matters

Shipped as a **reported axis on controls**, not a cell.

**Harness gap reported, not made:** `ALL_OPTS = ["O0","O0d","O3"]` has **no
`-O3` + debug-assertions cell**, so `O3d` was built under `controls/`. A 4-line
`build.py` change would make it first-class.

- At `-O3`, `debug-assertions=on` costs the shipped R3 **3.00 `Ir` per call and
  0.00 per byte** (0.13% of `small`) — on a program that *has* the guard the
  inserted assertion is provably dead.
- On R4 it costs `+3·b + 5·v + 21`, and **R4's fitted law becomes
  character-for-character `safe_naive`'s**, because `-C debug-assertions=on` also
  turns on `assert_unsafe_precondition!` inside `get_unchecked` (named function
  `…get_unchecked::precondition_check`, 14.00 `Ir`/byte at O0, closing the
  decomposition exactly).
- ⚠ **So `O0d` is NOT "R4 + a shift check"**: only 7.00 of 23.00 (safe) /
  38.00 (unsafe) `Ir`/byte is the shift check, and 5 of those 7 are `-O0` spill
  code.

## Problems

1. ⚠ **A design goal I failed and am reporting as failed: the leave-one-band-out
   CANNOT FAIL.** The design is **3 columns**, so it stays rank 3 after dropping
   any band (`fit.py` prints it). **p13's and p14's defect for a third time.**
   Replaced with a **hashed pre-registered extrapolation** — band `y`, outside
   the convex hull 4× in both regressors, **24 predictions registered at
   `sha256 ca0bbe26…` before measurement**, worst error **0.026**.
2. ⚠ **`wrapping_shl` VERIFIES at the pinned vstd** (`checked_shl` /
   `overflowing_shl` / `unchecked_shl` are `is not supported`). **So Verus's
   obligation attaches to the OPERATOR SPELLING, not to the operation**:
   *"Verus catches this bug"* holds for a rung spelling `<<` and **not** for one
   spelling `wrapping_shl`. Priced as a fiat, with its domain.
3. **`c_mask`** (`<< (shift & 63)`, defined C) has **the same cost law and the
   same wrong answer as R1, and UBSan is completely silent on it.** The sanitizer
   catches the **undefinedness**, not the **wrongness**.
4. **`adversarial-sat.bin`**: ten undefined shifts execute, UBSan fires, and
   **all eight cells print the same number** — no fold can see this bug on that
   input. Stated in `spec.md` as a property of the *bug*.
5. **`m_wshl_ms` is not a memory-safety-only configuration** and its number is
   withdrawn as such (the loop invariants stay functional) — **p17's control-2
   lesson, third instance**. The clean answer comes from standalone probes.
6. **`.temp/p18/` was already in use** by an earlier task (`bak-p*.md`,
   `gate-p*.log`, Aug 18 — a spec-editing pass over p01/p02/p05/p08/p16/p17).
   `cleanup.sh` keeps by extension so its `.md`/`.py`/`.log` survived.
7. **I corrected my own declaration once after building a control**: an early
   `why` sentence said the scan-loop spelling was unpinned while `required[2]`
   pins `while p < len`. **No entry moved**; the prose now matches. Disclosed in
   the hashed `why` itself, in `spec.md`, `safe_tuned.rs` and `NOTES.md` 12.

## Unsure / not done

- **No `ns` figure for R2 or R3** — no layout population for the safe cells.
  Only the C-vs-C hardening `ns` is claimed.
- **`large`'s `ns` row is weak** (P = 0.676 gcc / 0.829 clang, 48–65% within-cell
  spread) and is reported **with its P**, not leaned on.
- **`R3 − R4 = +1·b − 6·v + 7`** (R3 cheaper on both matrix inputs) is a
  **fixed-R4** reading, not "safe beats unsafe"; **p18's R4 side has not been
  searched in contract** and p18 publishes no pair interval.
- **No `O3d` law for the `*_noguard` controls** — they do not fit a linear law
  over band `b` (residual 10.5…15.7).
- **No branch-miss data** (`perf_event_paranoid = 3`); the gcc-branch-vs-clang-
  `cmov` explanation for the `Ir`/`ns` magnitude divergence is **marked a
  hypothesis**.
- **`panic=abort` axis not built.** No `wall_span.py` port.

## Memory updates

**None written** (subagents are forbidden). Candidates for the manager **after
review**:

1. The two refuted TASK_051 claims — **UBSan and Miri both catch it**, Miri as a
   **panic** rather than `ub`.
2. **`-C debug-assertions=on` re-enables `assert_unsafe_precondition!` in
   `get_unchecked`**, so `O0d`/`O3d` are not "a shift check" and **R4's advantage
   over R2 vanishes under them**.
3. **Verus's arithmetic obligation is spelling-conditional** (`<<` vs
   `wrapping_shl`).
4. **A 3-column design makes every leave-one-band-out unable to fail**, so the
   rank test needs a **column-count** caveat.
5. **p18's R4/R5 pair lands at the SAME address** (offset 0, not p06's and
   p14's 0x20) — **that offset is not universal.**
