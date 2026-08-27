# TASK_110 — land `TASK_109`'s corrections into `p42`, and SHIP TWO NEW RUNGS

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`.tasks/TASK_109_REPORT.md` **in full**, then `patterns/p42-goto-cleanup/`.

Scratch in **`.temp/t110/`**. **You are the only agent running.**

⚠ **The manager writes RECAP finding 39's final form from your report.**

---

## The decision, taken by the manager, with its reasoning

`TASK_109` returned **two blockers** and recommended *"a re-write, not a
re-build"*. ⚠⚠ **I am overruling half of that, and you should tell me if I am
wrong.**

**Ship BOTH new rungs**, because in each case the currently-shipped rung causes
the pattern to publish something false:

1. **The ghost-ledger R5.** The shipped R5 makes `p42` *"the first pattern whose
   R5 does not cover its own bug class"* — **and that is now a property of the
   encoding, not of the prover.** The ledger costs **zero object code**
   (`md5_fn`/`md5_raw` identical), **zero new trusted items**, and moves only
   `verus.obligations` 15 → 18. **Shipping it converts a false negative result
   into a true positive one at no measurable cost.**
2. **`r4_foldonly` as the R4.** The shipped R4 makes the pattern publish
   *"safe-tuned beats unsafe"*, **which is refuted** — the sign flips
   `−36.00`/`−2036.00` → `+12.00`/`+11.00`. **Leaving it is publishing a number
   the project knows is wrong.**

⚠ **BOTH edit measurement-hashed files (`verus.rs`, `unsafe.rs`), so both cost a
re-measure of `p42` — ONE pattern, ~1–2 minutes. That is cheap and it is the
right trade.** ⚠ **Neither has been through Miri, `spec.md`, the twin regime or
the gate. That is your job, and it is where this could still fail.**

⚠⚠ **IF EITHER FAILS ITS FULL REGIME, DO NOT SHIP IT — report the failure and
land the prose correction instead.** Specifically: **the ledger must pass
`--cfg slb_twin` and `check.py::_is_trusted`** (untested by the review), and
**`r4_foldonly` must pass Miri and the full gate.** **A refusal here is a
result, not a failure.**

## §A — the ghost-ledger R5

**The recipe is in `TASK_109_REPORT` §A and it verifies `18 verified, 0 errors`**
with the leak arm at `17 verified, 1 errors`. ⚠ **Key by a ghost `int`, NOT by
address** — `vstd`'s `allocate` never promises the address is not already
escrowed, and address-keying fails on both exits. ⚠ **Keep the ledger a LOCAL
inside `kernel` and push the obligation onto an `#[inline(always)]` body**, so
the pinned signature and `driver.canonical` do not move.

**Then verify what the review did not:** `--cfg slb_twin`; `check.py::_is_trusted`
and `_scan_unsafe_sites`; Miri; and that `identity unsafe ≡ verus` still reads
`exact`. ⚠ **Update `verus.obligations` 15 → 18 in `spec.md` — that MOVES
`contract_sha256`. Disclose before/after per rule 6.**

## §B — `r4_foldonly` as the shipped R4

A do-while fold that never leaves the allocation; all four operations are
specified at the pin. **Verify: `15 verified, 0 errors`, `identity exact`,
`md5_raw_equal`, agreement with the model on all 12 committed inputs, Miri, and
the full gate.**

⚠⚠ **AND FIX THE CLAIM, NOT JUST THE RUNG.** `NOTES` 11b differences **two
minima and calls them "the two INFIMA"**, which they are not — **and p42's own
hashed shared paragraph forbids exactly that construction**: *"`min(R3 found) −
min(R4 found)` is NOT the repair — two upper bounds differenced bound nothing in
either direction."* ✅ **What is licensed is `R3ship − R4ship` on two shipped
cells.** ⚠ **The R4 span now OVERLAPS R3 at both ends. Say that a difference
whose endpoints overlap is not a difference — do not narrow the claim a second
time.**

## §C — the majors and minors

| # | what |
|---|---|
| **M3** | ⚠⚠ **`spec.md:63` says *"three things are pinned in the block below"* and NONE of the three is enforced.** `required[1]` (`goto cleanup`) and `required[2]` carry **no backticks**, so `_TICK` yields **zero spellings** — **the idiom the pattern is NAMED FOR is unenforced** — and `required[3]`'s `` `dig[len-1]` `` matches **0 of 4 rungs**. The gate confirms all 16 spellings come from elsewhere. **`p02` backticks its per-language entries; copy that.** ⚠ **This moves `contract_sha256`.** |
| **parity** | **The clang effect is window PARITY, not size**: `−5.00` even, `−4.00` odd, **zero size dependence over a 32× range**; the two shipped inputs are 97 (odd) and 4096 (even) and were read as small-vs-large. **Three terms: `+3` the `setne`/`sete`/`or` merge, `+1` an alignment `nopw` once per call, `+1` on even windows only from the odd-remainder guard.** **Land all three.** |
| **352** | **`leak.sh` runs 352 points (`2 × 4 × 44`), not 88** — wrong in the script header, its own success message, `NOTES` 3 and `README`. ✅ It has teeth (planted non-leak → exit 1, 12 rows flagged); only the count is wrong. |
| minor | `controls/spellings.py` cannot run in a fresh clone (its variants keep `#[path = "../../common/driver.rs"]`, resolving into gitignored `.temp/`). |
| minor | `.temp/t104/allocclass/iso.py` has **no rebuild script** for the two binaries it consumes (constraint 6), and `main_shim.c` is **0 bytes**. |
| minor | The `dig_free` trusted argument still says *"p42's leak claim rests on Miri and not on this contract"* — **false once §A lands.** |

## §D — the retraction, which is the biggest text change

*"Verus at the pin cannot state leak-freedom"* is **false** and sits in **eight
places**, including **the hashed block TWICE** (`idiom.why`, `identity[0].why`),
`verus.rs`'s module comment, `unsafe.rs`'s SAFETY (5), `NOTES` 6, the `dig_free`
trusted argument, `README.md`, and `affine_leak.rs`'s header.

✅ **Replace it with the true and better claim:** *the natural encoding does not
state leak-freedom; escrowing the token does, and the residual trust is that
nobody bypasses the wrapper — a module-level discipline, not a global
guarantee.* ✅ **Keep `affine_leak.rs`** — its premise is true and its two arms
are the evidence for the *encoding* half. ✅ **Land the clean negative too: there
is NO linear must-consume tracked mode at the pin** (23 verifier attributes, none
is one; `grep -rn affine vstd/` → 0 hits), **so nobody re-runs that search.**

---

## Constraints

- **`.temp/t110/` only. No `/tmp`.** **Notes in `.temp/t110/NOTES.md`.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only** — the manager has already landed
  the `.memory/` half. Do not touch them.
- ⚠⚠ **`verus.rs` and `unsafe.rs` ARE measurement-hashed**, so §A and §B require
  **`harness/measure.py p42`**. **Get every comment in every measurement-hashed
  file right BEFORE measuring** — a comment-only edit afterwards stales it again.
  ✅ `NOTES.md`, `README.md` and `spec.md` are **not** in `measurement_sources`.
- ⚠ **Do not touch `harness/build.py`, `harness/asm.py` or `harness/measure.py`.**
  ⚠ **Do not edit `harness/check.py`** — its known defects are batched into
  `TASK_107`.
- ⚠ **Every probe needs an arm that must fire.** The list of **seven** controls
  that could not have failed is at the end of `.memory/03-measurement.md`.
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- **Finish every edit, then `harness/check.py p42` and `harness/measure.py
  --check-stale`.** Report both verdicts and the new `contract_sha256`.

Write your report to `.tasks/TASK_110_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 389.** ⚠⚠ **`TASK_109` refuted BOTH of
`p42`'s headlines, and both were calls the manager had named as least-sure — so
naming them worked, and the manager was wrong twice in one pattern.** The calls I
am least sure of now:

1. ⚠⚠ **That shipping both rungs is right at all.** The reviewer recommended
   *"a re-write, not a re-build"* and I am overruling half of that. **If the
   ledger R5 fails the twin or `_is_trusted`, or `r4_foldonly` fails Miri or the
   gate, I am simply wrong and the prose fix is the answer.** **Tell me.**
2. **That the ledger belongs in `verus.rs` rather than in `controls/`.** ⚠ **An
   argument exists for shipping it as a CONTROL and leaving the simpler R5 in
   place** — it keeps the rung readable and still records the finding. **I think
   shipping it is right because the alternative publishes a false negative, but
   argue if you disagree.**
3. **That `r4_foldonly` is really admissible.** The review drove
   `spelling_matches` on it, ⚠ **but `p23` showed a spelling can pass every pin
   and still be a tautology away from meaningless. Check it is not admissible by
   accident.**

Carry **389** forward, incremented by what you find.
