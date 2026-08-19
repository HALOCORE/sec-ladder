# TASK_029 — report

Engineer's return message, recorded by the manager. Scratch: `.temp/p29/`.
All eight prose items landed; `check.py p07` green three times. **The finding
below (item 2) is NEW and UNREVIEWED** — it is the subject of TASK_030_REVIEW.

## Did

Prose, `patterns/p07-binary-search/`, all eight items:

1. **`NOTES.md` §3c + `README.md`** — headline scoped to **R3**; "first
   counterexample to safety is cheap" deleted and marked refuted by
   `.memory/01-ladder.md` findings 4/6, with a three-row amortisation table
   (p16/p17 per-*call* 0.00000 Ir/byte · p05 `O(nrow)`, vanishes along `ncol` ·
   p07 6.0000/probe, vanishes along nothing). Asymptote replaced by
   `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**, 47.99% *on the shipped workload*, plus
   the six-workload table.
2. **§3** — R2's two `ns` cells struck as **WITHDRAWN**; R3's stated as the pair
   that survives; the **six** unbracketed `ns` cells (both C rungs + R5) flagged
   with the reason `-align-all-functions` cannot bracket `c-gcc`.
3. **§3a** — derivation replaced by the three-path `13/12/7` + `16`/query form,
   addresses counted off the `-O3` listing. §3b's residual column named as the
   tell.
4. **`controls/gen_controls.py`** — `r4_for_twin` added (15 controls);
   `./verus_run.py .temp/p07/controls/r4_for_twin.rs` → `10 verified, 0 errors`;
   §10b rewritten; dead `.temp/p07/twin/` path fixed.
5. **§4** — `6021…216053` / `46.1x` / `11.96…131.97`, plus a note that an input
   fix invalidates every number, not just the ones it is about.
6. **35 bits at EIGHT sites**, not the six the review named — it missed
   `controls/gen_controls.py:78` and `:296`. Includes `spec.md`'s hashed
   `idiom.why`; `verus.rs:179` and `c/kernel_hardened.c:15` are comment-only.
7. **§2 / `README` / `model.py`** — 6624 bytes, 0.63%; `work_per_call` docstring
   re-derived for `nq = 92` (1656 / 6624 / 1 048 916 / 262 229).
8. **§3** — R5 is 0.0% kernel-exclusive, **−1.00 Ir/call whole-program**, with the
   convention clause.

**Ride-along** — §11 preamble and §11d now carry the `--branch-sim` table, the
`--cache-sim` locality negative, the 559-symbol isolation diff, the workload lever,
and the three "a simulator is not a counter" rules. **New §11e** carries item 2.

## Evidence

### The contradiction (item 2), and it is the main finding

Withdrawing R2's `ns` comparison is right. *"The band is 28.47% and the interval is
the honest form"* is not the reason, and the rule it rests on is not stable.

A second layout lever — **rust-lld `--symbol-ordering-file`**, which moves
`kernel` `0x15600` → `0x518f0` at unchanged `n_fn` and unchanged executed
instruction stream, where alignment moves it only inside `0x300` — gives **30
layouts per rung instead of 7**:

```
CONTROL 2 -- marginal Ir/call must be layout-invariant:
  safe_naive   small marginal Ir/call over 30 layouts: [12346.57]
  safe_tuned   small marginal Ir/call over 30 layouts: [9600.12]
  unsafe       small marginal Ir/call over 30 layouts: [6582.98]
```

**(a) It is not a band — it is two modes selected by bit 4 of the kernel's entry
address.** `safe_naive` / `small`: `%32==0` → 17.708 ms (n=18), `%32==16` →
13.931 ms (n=12). Perfect separation (slowest fast 14.766 < fastest slow 16.993),
and the largest-gap clustering and the bit-4 partition are the **same partition,
30/30**.

**(b) R2's sign flips with that bit**, so no number of reps rescues it:

```
kernel%32= 0  unsafe 14.007 ms  safe_naive 17.708 (+26.42%)  safe_tuned 15.563 (+11.12%)
kernel%32=16  unsafe 14.062 ms  safe_naive 13.931 ( -0.93%)  safe_tuned 16.505 (+17.37%)
safe_naive   mode 0 +26.42%   mode 16 -0.93%   -> SIGN FLIPS
```

**(c) No counter this box has resolves a 27% mode.** Minimal pair
`-align-all-functions=1` vs `=2` (kernel 16 bytes apart, `md5_fn_norel
bf70816958ed` both):

```
Ir 12346.57 vs 12346.57  Δ0.00 | Dr 530.71 both | Dw 6.01 both
I1mr/D1mr/D1mw/ILmr/DLmr/DLmw all 0.00 both
Bc 3482.85 both | Bcm 273.93 vs 273.92 | Bi/Bim 0 both
```

**(d) The worst-vs-best RANGE is not a converging statistic, and applied more
thoroughly it retracts the reviewer's own clean negative:**

| | 7 alignments | 30 layouts |
|---|---|---|
| `safe_naive` band, `small` | 28.91% | 30.78% |
| R2 vs R4, `small` | [−1.84%, +33.65%] OVERLAP | [−4.67%, +33.80%] OVERLAP |
| **R3 vs R4, `large`** | **[+0.72%, +3.12%] DISJOINT** | **[−0.14%, +4.42%] OVERLAP** |

Same rung, same binaries, same machine — only the sample size changed.
**Mode-matching and dominance do converge and both keep R3's sign**: R3 slower
than the *worst* R4 layout at **30/30** on `small`, **29/30** on `large`
(R2: 19/30, 23/30).

### Everything else reproduced

`.temp/r26/sweep_pathfit.py` → three-path `max|res| 0.4127` vs `10.566`,
`b = 16.0026` against a listing count of 16, deltas `+6/+6/+6` (R3) and
`+11/+11/+11` (R2). Verus twin `10 verified, 0 errors`.

**Gate** — `check.py p07: PASS` three times (`.temp/p29/gate{1,2,3}.log`), stage
3b `6021...216053 ... 46.1x ... 11.96...131.97`. Record diff vs `HEAD` is **only**
`contract_sha256`, the `idiom.why` string, 8 `source_sha256` entries and ASan PIDs:

```
identity / marginal_ir_per_call / verus / verified_twins / derived_contract /
idiom_audit / driver_loops / clause_deletion / requires_strength /
proof_domain / miri / adversarial   ALL unchanged=True
md5_fn 4f8c443684e15a1c17b9ecfc55d4d754 both rungs @O3, md5_raw_equal true
```

**`md5_fn` unchanged — the kernels are untouched.** No other gate record
references p07 sources (all 10 checked), so only p07 needed re-running.
`results/tables/p07-binary-search.md` regenerated with `harness/report.py`.

## Problems

- **`.memory/03-measurement.md`'s layout recipe was wrong for two of three
  rungs.** It said to confirm the kernel's `md5_fn` is identical at every
  alignment. R2's and R3's kernels `call` the panic path, so `md5_fn` moves with
  the displacement — **28 distinct digests over 30 layouts at constant `n_fn`**.
  `md5_fn_norel` is invariant (`bf70816958ed`). Following the recipe on a
  panicking rung, you conclude the code changed and abandon the control.
- Two clean negatives on layout levers, so nobody repeats them: a padding object
  via `-C link-arg` does **not** shift the kernel (rustc appends it after the
  crate's `.text` and passes `--gc-sections`; retained with `"axR"` it lands at
  `0x53aa3`, *after* `kernel`); and `-align-all-nofallthru-blocks=K` is **not**
  byte-identical (nops *inside* the kernel, `n_fn` 66 → 67/71/73).

## Unsure / not done

- **The mode's mechanism is narrowed, not identified.** Not I-cache geometry —
  R2's innermost loop spans the same 3 32-byte windows and 2 64-byte lines in
  *both* modes, and the one geometric difference (the `hi=mid` re-entry path, 4 vs
  3 windows) points the wrong way. Front end or an address-indexed predictor is
  what is left; neither is observable here. Published as such.
- **The C rungs are still unbracketed.** The gap is stated and the fix named
  (`--symbol-ordering-file` is linker-side and reaches gcc) but not run.
- Item 2's timings are min-of-31 on `taskset -c 3`, one CPU; the reviewer's CPU-5
  replication was not repeated at 30 layouts.
- Did not re-derive §3b's `c-gcc`/`c-clang` laws in three-path form.
- **Adjacent, not fixed:** `RECAP.md:582`'s queue block was stale (fixed by the
  manager at the landing commit).
- `harness/check.py:1753` left alone as instructed.

## Memory updates

None written (forbidden). Three landed by the manager:

1. **`.memory/03-measurement.md`** — recipe corrected to `md5_fn_norel`; the
   "publish an interval, require disjoint bands" rule replaced by mode-matching
   and dominance, with the non-convergence measured.
2. **`.memory/00-environment.md`** — `--symbol-ordering-file` as the strong layout
   lever, the two clean negatives, and the **limit of the callgrind simulators**:
   blind to a 27% wall-clock mode.
3. **`.memory/01-ladder.md` finding 8** — p07's R2 `ns` withdrawal now records the
   *mechanism* (two modes on bit 4, +26.42% / −0.93%, invisible to every counter)
   rather than the band width, and notes that R3's counterweight survives by
   mode-matching and dominance rather than by disjoint bands.
