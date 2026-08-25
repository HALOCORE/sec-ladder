# TASK_088 — report: `p19`'s corrections, then the gate work

**Role: research engineer.** **UNREVIEWED.** Both parts complete and green.
**PROTOCOL rule 2 running count: 249 → 253.**

```
measure.py --check-stale      46 record(s) examined, 0 STALE   (exit 0)
verdicts: {'PASS': 22, 'PASS-WITH-BLOCKED-ROWS': 1}  n=23  total failures 0
p19 contract_sha256 db6e6c51…  (UNMOVED)
p01 contract_sha256 5360d6f3…  (UNMOVED)
```

✅ **Manager-verified independently:** 23 records, `{'PASS': 22,
'PASS-WITH-BLOCKED-ROWS': 1}`, **0 failures**.

---

## ⚠⚠ THE ACCEPTANCE TEST — one command, source → published number, WITH A NEGATIVE CONTROL

`.temp/t88/accept.py`. **One real `#[verifier::external_body] fn t88_lie(x:u64)
-> (r:u64) ensures r == 0 { x }`** in **one real `#[path]`-included module**,
included by **two** patterns; real gate; real records; `licence.py --emit` then
`synthesize.py`; diff.

| | pre-fix harness (`--head`) | fixed harness |
|---|---|---|
| p01 / p09 verdict | **PASS-WITH-BLOCKED-ROWS / PASS** | FAIL / FAIL |
| gate failures | **0** | 1, **and it names the plant** |
| `grep -c t88_lie gate.log` | **0 / 0** | 6 / 6 |
| p01 published `TCB items` | **3 → 3** | 3 → 4 |
| p09 published `TCB items` | **4 → 4** | 4 → 5 |
| **total** published `TCB items` | **93 → 93** | **93 → 94** (not 95) |
| `results/synthesis.md` | **BYTE-IDENTICAL** | **differs** |

`accept.py` → **`ACCEPTANCE: PASS` (9/9)**. `accept.py --head` → **`ACCEPTANCE:
FAIL`**, reproducing `TASK_084_REVIEW` route J **from scratch**. `93 → 94`
rather than `95` is **minor 1 fixed, end-to-end**.

⚠⚠ **THE ENTIRE PUBLISHED DIFF FROM ALL OF PART B IS 3 INSERTIONS / 1 DELETION**
— *"all 22 rows"* → *"all 23 rows"*, plus the dedupe paragraph. **No published
number moved — and the acceptance test is why that is a RESULT rather than a
TAUTOLOGY.** That is the lesson `TASK_084` cost us, landed.

---

## PART A — `p19`'s corrections

- **A1** — uniqueness claim struck at `NOTES.md`, `spec.md`, `README.md`; p19 is
  now the **third** instance, citing **p36** (`forbidden[2]/[3]/[5]/[6]`) and
  **p03** (`forbidden[1]`) with their `idiom.why` verbatim. **Practice kept.**
- **A2** — both laws re-fitted **from the committed blobs** (`.temp/t88/refit.py`,
  the engineer's own, not the review's). New closed forms in `NOTES.md` §12,
  `inputs/gen.py`'s docstring and `safe_tuned.rs`, plus §12a's mechanism read off
  the disassembly. **Zero residual over all 19 committed lengths:**

  ```
  R2 - R4 = 6.25*m - 6 - 2.25*(m mod 4) - 4*[m mod 4 != 0]
  R3 - R4 = 1.00*m + 4                  - 1*[m mod 4 != 0]
  mod 4 == 0: n=10  -6.0     EXACT  |  +4.0  EXACT
  mod 4 == 1: n= 5  -12.25   EXACT  |  +3.0  EXACT
  mod 4 == 2: n= 2  -14.5    EXACT  |  +3.0  EXACT
  mod 4 == 3: n= 2  -16.75   EXACT  |  +3.0  EXACT
  2-param OLS slopes 6.250530 / 1.000035  (= the review's numbers exactly)
  ```
- **A3** — CVE attribution fixed at **all five** sites. **Route (i): p19
  re-measured.**
- **A4** — the three minors; **p38's identical mis-citation reported, not
  fixed** (`patterns/p38-alias-pun/NOTES.md:328`).
- ✅ **Also struck: the manager's refuted A6 claim**, which was standing in
  `NOTES.md` §7 (*"p19 is the only pattern … that calls a vstd exec
  `external_body`"*). **The task body did not list it; the engineer caught it
  from the preamble.**

## PART B — the gate work

- `harness/check.py`: new **`_verus_file_list`** — *one deduped file list*;
  `_trusted_items` and `_axiom_items` both use it; new `_axiom_keyword_shout`;
  new `_check_included_tcb` (declared count `verus.included_tcb`, default 0).
  **The `#[path]` loop now feeds all three detectors.**
- `harness/vparse.py`: new `_match_bracket_back`; `trait_spans` steps over
  `pub(crate)` / `pub(in path)`; **3 new selftest pins**.
- `synthesis/synthesize.py`: §3 rows add included files' `tcb_items`; **totals
  dedupe on `(src, name, line)`**.
- `patterns/p01-array-sum/spec.md`: `check.py:NNNN` → **function names**.

**minor 4** probe: HEAD `trait_spans → ['ExBaz']`; now
`['ExFoo','ExBar','ExBaz','PlainVis']` with `PlainVis` an axiom in neither.
**minor 5** probe (was a code read): HEAD keyed the same file **twice**, total
**2** for one axiom; now **1**.

✅ **The manager's call (b) — CONFIRMED by measurement.** `_path_includes`
returns exactly `common/driver.rs` for all 23; `vparse.parse` gives 10 items,
**0 with `.external`**; `axiom_decls` `[]`. **All three widenings inert. Nothing
turned red.**

Sweep 41 min. `licence.json`: 23 patterns, 92 pair verdicts, **zero `LICENCE
STALE`**.

---

## ⚠ Four contradictions of the task file

- **#250 — A3's route (ii) CANNOT EXIST AS WRITTEN.** *"Leave a one-line pointer
  in the two C files' comments"* — **any** edit to `c/kernel.{c,h}` stales the
  measurement record, so (ii) does not avoid the re-measure. (And there are
  **three** non-measurement sites, not four.) **Route (i) taken. Cost measured:
  `measure.py p19` = 1 m 17 s**, and the structural diff is
  `min_s`/`median_s`/`spread_pct` × 32 cells + `generated_utc` + `git` + the 4
  source hashes. **Zero `Ir`, zero static/md5, zero checksum, zero identity.**
  p19 publishes no wall clock.
- **#251 — A5's *"expect `0 STALE`"* is wrong for the GATE record even under A2
  alone.** After the `gen.py` docstring edit: **`GEN-ONLY` on the measurement
  record, `STALE` on the gate record.** Cause: `check_stale`'s `gen_only` branch
  requires `"input_sha256" in rec` and **gate records carry none**; they also
  hash `NOTES.md`/`README.md`/`spec.md`. A `check.py p19` re-run clears it.
  **The manager's call (a) is upheld for the C files and needs this footnote for
  `gen.py`.**
- **#252 — A2's site list was incomplete.** `safe_tuned.rs:27` **also** published
  `R3 − R4 = 1.00000 * m − 2`. **Named by neither the review nor the task file.**
  Fixed.
- ⚠⚠ **#253 — A2's mechanism is incomplete and its attribution is HALF WRONG.**
  **(a)** *"worth 2.25 per epilogue byte"* explains the 2.25 steps but not the
  first: **R4's excess is `2.25·r + 4·[r≠0]`**, the flat 4 being the **epilogue
  preheader** (6 instructions taken vs 2 not taken); R3's is `2.25·r + 3·[r≠0]`,
  and the `−1` in `R3 − R4` is **one named instruction, R4's `add %rsi,%rdx`**.
  Every coefficient counted off `asm.py … --raw`.
  **(b) THE RESIDUE CLASS IS NOT THE WHOLE CAUSE.** The 5-length probe sampled
  **only `m ≡ 0 (mod 4)`**, where the correct law is `6.25m − 6` / `1.00m + 4`;
  it published `−8` / `−2`. **The delta is exactly `+2` and `+6` at all ten
  `m ≡ 0 (mod 4)` points — a FIXED PER-PROGRAM OFFSET.** **The probe was a
  different binary (`.temp/t87/cost.rs`); only the SLOPE ever transfers.**

## ⚠ A confound the engineer found in its own test and removed

The first `--head` run reported 3 `[clause-mut]` / `[req-mut]` / `[twin]` FAILs.
**Not detections:** stage 5 **copies** the pattern to
`.temp/clausemut/<pid>/patterns/<slug>/`, and a `pdir`-relative `#[path]` does
not resolve from there. **Same class as the *"7 failures, all diagnostic-mode"*
the review recorded for route J** — ⚠ **so RECAP's summary *"fully green with no
gate output at all"* is LOOSER than the review's own text.** An **absolute**
`#[path]` resolves from both directories; with it the control is clean (0
failures, PASS, byte-identical).

## Unsure / not done

- **39 other `check.py:<line>` citations across 21 files** (census run). ⚠ **Two
  are INSIDE `patterns/p09-bitset/spec.md`'s fenced block**, so fixing them moves
  `contract_sha256`. Most pair the function name with the line, i.e. **the
  retracted "line as a hint" convention.** Reported, not fixed.
- **`TASK_084_REVIEW` majors 2 and 3 untouched** (the §3 prose overclaims;
  `check_miri`'s `if not why_required` branch). Not in Part B. ⚠ Noted that
  `synthesize.py`'s §3 prose still hardcoded *"All **22** `verus.rs`"* and
  *"(22 each)"* — **stale at 23 patterns.** ✅ **FIXED BY THE MANAGER, and made
  COMPUTED rather than corrected**, so it cannot go stale again: `_n_named`,
  `_n_verus_rs`, `_n_broadcast`. Now renders *"All **23** of the **23**"* and
  *"(23 and 23, one per pattern)"*; totals unmoved at 295 / 93 / 194 / 0.
- **B4 (the sixth route — *used* vstd `assume_specification`s) is STILL OPEN.**
- `_check_included_tcb` and `_axiom_items` will both see an
  `external_fn_specification` in an included file — mirrors what already happens
  for `verus.rs`; noted, not changed.
- `--head` proves the gate/publish chain, **not** that HEAD's Verus behaviour is
  unchanged; the plant verifies at the pin either way.
- Did not run `report.py` for any pattern but p19; did not touch `.memory/`,
  `pilot/`, `build.py` or `asm.py`; no `git add`/`commit`.

## Memory updates owed (manager applies, AFTER review)

1. **`check_stale`'s `GEN-ONLY` verdict cannot fire on a GATE record**, because
   gate records have no `input_sha256`. → `.memory/03-measurement.md`.
2. ⚠⚠ **An intercept measured on a PROBE binary does not transfer to the shipped
   one; only the SLOPE does.** p19's `+2` / `+6`, exact at ten lengths. **A
   second, independent failure mode alongside the residue rule, and invisible to
   a residue-covering band.** → `.memory/03-measurement.md`.
3. **A `#[path]` include used in a gate test must be an ABSOLUTE path**, because
   stage 5's clause-mutation arms copy the pattern elsewhere. →
   `.memory/05-layout.md`.
4. **Key convention extended:** `verus.included_tcb[<repo-relative path>]`,
   sibling to `verus.axioms`; **`_verus_file_list` is the single deduped list all
   Verus-side detectors share.** → `.memory/05-layout.md`.
5. **`p19` is the SECOND pattern, after `p27`** — re-derived independently.
   **Per the review, do NOT land this as a finding**; `.memory/04-verus.md`
   already covers both.
6. Both p19 CVEs re-verified at `cveawg.mitre.org`.
