# TASK_PHP_039 — item 68: **measure the WIDTH → SPREAD LAW for family B**, and get the exponent

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_039_REPORT.md` — **write the FILE** (rule 10).

---

## §0 ⚠⚠⚠ THIS TASK INVERTS ITEM 68's OWN ORDER, AND THAT IS DELIBERATE

Open item **68** says: *"widen the pin on ONE row, **re-gate it**, and measure
what moves."* ⛔ **That is backwards and this task does not do it.**

**A re-gate at a wider `probe_iters` produces ONE draw at the wider width. One
draw does not measure a spread.** The quantity item 68 wants — *does the
cross-language spread collapse as the width grows?* — is a **spread across
several draws at each width**, which is measured by rewriting `n_iters` and
running callgrind directly, **exactly as `.temp/mgr173/ph64_draws.py` and
`.temp/php38/draws.py` already do**, with no gate run and no touch of frozen
code.

▶ **So: this task MEASURES. The re-gate is the ADOPTION step and it is
CONDITIONAL on the answer.** ⚠ If the answer is *no*, a re-gate would have been
spent on nothing; if *yes*, the re-gate should be batched with that row's owed
prose (items 56/57/59/63/65), which is a decision only the manager can make.
**Do not edit any `spec.md`. Do not run the gate.**

⭐ **The licence for measuring outside the gate is already established and you
must re-establish it**: `harness/check.py::_probe_input` (line 3248) writes
`struct.pack("<Q", n_iters) + blob[8:]`, and `n_iters` is at offset 0 of *every*
pattern's input (`.memory/02-bench-rules.md`). **§4's N2 is that check.**

---

## §1 ▶ THE QUESTION, AND IT TURNS ON ONE NUMBER

F88 established the mechanism from **committed driver source**, not inference:
`ph64`'s `c/main.c` `SLB-DRIVER` loop picks the window index as
`k = acc * nwin >> 64`, `acc = acc * 31 + r` — **a pseudo-random function of the
running accumulator.** So a slope taken over iterations `[n, n+W)` is the **mean
of the per-window costs of the `W` windows visited in that span**: deterministic,
but a *sample*.

⭐⭐⭐ **IF THAT ACCOUNT IS RIGHT, THE SPREAD OF THAT MEAN ACROSS DISJOINT SPANS
MUST FALL AS `W^(-0.5)`.** That is not a guess, it is what the mean of `W`
draws does. **And the exponent decides item 68 outright:**

| measured exponent | what it means | the decision |
|---|---|---|
| **≈ −0.5** | ordinary sampling error | ⛔ **widening is HOPELESS** — killing `8.63 pp` down to `1 pp` needs `W ≈ 7 500`, a **25×** gate-stage cost. **Item 68 answers NO and `TASK_PHP_038` §6's ruling stands: item 62 (family C) is the answer.** |
| **≈ −1 or steeper** | something beyond i.i.d. sampling | ✅ **widening WORKS** — `W ≈ 900` suffices. **Item 68 answers YES, item 62 stops being a precondition, and F90 is right against the reviewer.** |
| **≈ 0** | not a sampling effect at all | ⛔ **F88's mechanism is WRONG** and the whole thread needs re-opening. **Report this loudest of the three.** |

⚠⚠ **AND THE ALREADY-PUBLISHED NUMBERS DO NOT FIT ANY OF THEM, WHICH IS WHY
THIS IS WORTH AN HOUR.** Item 68's own table reads `8.124 → 2.092 → 1.243 pp`
at `W = 100, 200, 300`. `W^(-0.5)` predicts `8.124 → 5.74 → 4.69`. **The
published fall is far too fast**, and the manager could not tell whether that was
real or was the bias in §2. ▶ **You are measuring it again, with a design that
does not have that bias.**

---

## §2 ⛔ THE DESIGN IS MANDATORY — DO NOT "IMPROVE" IT

**The manager's own attempt at this failed, twice, and both failures had the same
cause: the statistic and the sample count moved together with the width.** From
item 68: *"sliding spans share draws and disjoint spans leave fewer samples, and
**both biases point the same way**, so only the direction and the width-100
figure are trustworthy."* ⚠ **A `1/width` fit that looked clean was two biases
meeting.**

⚠ **Why `max − min` is the trap.** The expected range of `K` samples **grows
with `K`**: ≈ `2.97σ` at `K = 9`, `2.06σ` at `K = 4`, `1.69σ` at `K = 3`. Item
68's three widths used **9, 4 and 3** disjoint spans. ▶ **So ~1.4× of that fall
is the estimator, not the physics.**

### §2.1 The span table — **`K = 8` at every width, identical start positions**

Block spacing `S = 800`. Block starts `n_j = 100 + 800 j`, `j = 0 … 7`:
**100, 900, 1700, 2500, 3300, 4100, 4900, 5700.**

For each width `W ∈ {100, 200, 400, 800}`, span `j` is **`(n_j, n_j + W)`**.

| W | the 8 spans | disjoint? |
|---|---|---|
| 100 | (100,200) (900,1000) … (5700,5800) | ✅ `W ≤ S` |
| 200 | (100,300) (900,1100) … (5700,5900) | ✅ |
| 400 | (100,500) (900,1300) … (5700,6100) | ✅ |
| 800 | (100,900) (900,1700) … (5700,6500) | ✅ |

⭐⭐ **THE PROPERTY THAT MAKES THIS THE EXPERIMENT: `K` is 8 at every width, and
the eight spans START AT THE SAME EIGHT `n` VALUES at every width. The only
thing that varies between widths is the width.** Position is not a confound —
it is held fixed by construction, not corrected for afterwards. ⓘ Span `j` at
`W = 800` **contains** span `j` at `W = 100`; that is a *paired* design and it is
intended, not a defect.

**Endpoint set to run: 33 values of `n`** — `{n_j : j = 0…8}` (100 … 6500 step
800) ∪ `{n_j + 100, n_j + 200, n_j + 400 : j = 0…7}`. **Derive it in code from
the table above; do not hand-list it.**

### §2.2 Rows, cells, pairs

| | |
|---|---|
| **rows** | `ph64` (⭐ **the one row that publishes B1**) · `ph29` (⭐ the 32 % row) · **`ph03` — THE CONTROL** |
| input | **`small.bin` only** — F88's and F89's figures are all `small` |
| cells | `c-gcc`, `safe_naive`, `safe_tuned`, `unsafe`, at **`O3/isolated`** |
| **cross-language pair** | **`c-gcc` vs `safe_naive`** — F89's pair, and F85's central sentence |
| **same-language pair** | **`safe_tuned` vs `unsafe`** — F89's pair |

Binaries are **on disk** at `.temp/php-root/.temp/build/<row>/<cell>-O3-isolated`
(manager-verified present for all three rows). ⚠⚠ **md5-verify every one against
its published record before using it**, the way
`.temp/mgr172/inclusive_ir.py::verify_binaries` does. **A sweep over a stale
binary is worth nothing and looks fine.**

### §2.3 The statistic

For span `s` and pair `(x, y)`: `pct(s) = 100 · (B_x(s) − B_y(s)) / B_y(s)`,
where `B_c(s) = (Ir_c(hi) − Ir_c(lo)) / (hi − lo)` from `PROGRAM TOTALS`.

Report, per `(row, pair, W)`: **`SD` across the 8 spans, in pp** — *and* `mean`,
`min`, `max`. ⚠ **`SD` is the headline and `max − min` is reported beside it
only so the `W = 100` cell can be tied to F89's published `8.63 pp` / `0.07 pp`.
Say which statistic F89's numbers were.**

**The fit:** `log(SD)` against `log(W)`, 4 points, per `(row, pair)`. **Report
the exponent and the residuals.** ⚠ **Four points cannot support a confidence
interval; quote the exponent with its spread across the three rows and two pairs
instead, and say that is what you are doing.**

---

## §3 ⭐ THE SECOND DELIVERABLE, AND IT IS FREE

Your sweep runs `n` from 100 to 6500, so it **measures wall-clock against `n`
directly**. The gate's collapse stage cost is linear in `lo + hi`, i.e. in
`200 + W`. ▶ **Time every run and report the cost multiplier for the `W` the
§1 table's middle row would need.**

⚠ **Do not compute it from `ph64/O3/isolated/small` alone.** The gate probes
**both** inputs at **both** opt levels in **both** modes over **eight** cells —
96 `marginal_ir_per_call` entries on `ph64`, i.e. **128 callgrind runs** — and
the `O0`/`large.bin` cells are the expensive ones (`c-gcc-h/O0/whole/large.bin`
is **580 033 `Ir`/call**, so ~50× the `O3`/`small` cell you are timing). **Scale
from the published per-call figures, state the arithmetic, and label it an
ESTIMATE.** ⓘ That is the number the manager needs to price the adoption step;
an honest estimate with its method shown is worth more than a measured figure
for the one cheap cell.

---

## §4 Must-fire negatives — **all of them, and report each verdict**

`--selftest`, and **every check must be one that can FAIL**.

| | check |
|---|---|
| **N1** | every one of the 33 × 4 × 3 runs produced a `PROGRAM TOTALS`; count the misses |
| **N2** | ⭐ **THE LICENSING CHECK.** The `(100, 200)` span reproduces the **published** `marginal_ir_per_call` for `<cell>/O3/isolated/small.bin` **to < 0.05 `Ir`** on all 12 cell-rows. ⚠ **Compute the implied `Δcalls = ΔIr / published_B` and assert it is `hi − lo`** — if a driver calls the kernel more than once per iteration, take `Δcalls` from that row's `model.py` rather than assuming |
| **N3** | ⭐⭐ **THE CONTROL.** `ph03`'s `SD` must be **near zero at every width** (F88 measured its spread at **0.03 %** against `ph29`'s 32 %). ⛔ **If `ph03` shows the same law, the effect is generic — callgrind warm-up, allocator growth — and NOT window heterogeneity, and the whole account in §1 falls.** State a **relative** floor for "near zero" and say what it is |
| **N4** | ⭐ **F89 must reproduce at `W = 100`**: the same-language `SD` must be **much smaller** than the cross-language `SD` on `ph64` (F89: `0.07 pp` against `8.63 pp`). ⛔ If it does not, you are not measuring what F89 measured — **stop and report that**, do not proceed to the fit |
| **N5** | `K == 8` at every width, and the 8 start positions are **identical** across widths. **A design assertion, checked in code** |
| **N6** | the 8 spans at each width are pairwise **disjoint** |
| **N7** | ⚠ **the spread must be NONZERO at `W = 100`** on `ph64`/`ph29`, or there is nothing for width to reduce and the fit is fitting noise |
| **N8** | every binary's `md5` matches its published record (§2.2) |

⚠⚠⚠ **AND THE F52 CONTROL — a probe whose SETUP ENCODES THE ANSWER evaluates
fine and is wrong. Nine shapes are on file and the ninth was the manager's.**
▶ **Write at least one negative whose job is to catch THIS design doing it**,
and say what it is. ⓘ A candidate, not a requirement: the `W = 800` slope is an
average of the eight `W = 100` slopes *within* it — so on `ph64` the mean over
the 8 `W = 800` spans and the mean over the 8 `W = 100` spans are over
**different** iteration sets and need not agree, while the *grand* mean over
`[100, 6500)` is fixed. **Check something that could come out wrong.**

---

## §5 Traps

1. ⚠ **`grep -a` ALWAYS** (F35 — blind to 41 corpus files).
2. ⚠⚠ **QUOTE A MAGNITUDE FLOOR WITH EVERY SIGN AND EVERY "COLLAPSED" CLAIM.**
   *"Every taxonomy written for this analysis needed a magnitude floor and none
   of them had one on the first pass"* — three times in one round, including an
   outlier test that fired on `ph03` at a spread of **0.00 pp**.
3. ⛔ **DO NOT report a percentage without saying WHICH INPUT it is on.** A
   finding published unlabelled per input had to be corrected in place last
   round, inside the finding that approvingly quotes `check.py`'s own
   *"DO NOT MAX IT OVER INPUT"*.
4. ⚠ **`.temp/` is gitignored**, so a committed claim citing your probe is
   unreachable from a fresh clone (item **65**). ▶ **Put the NUMBERS in the
   report, not a pointer to a log.**
5. ⚠ **Keep the generator, delete the artefact** (`CLAUDE.md` constraint 6).
   `.out` profiles and `.bin` probes under `.temp/php39/` are **re-derivable and
   get deleted**; the `.py`, the `.log` and `NOTES.md` **stay**. ⭐ **One
   regeneration entry point**, the way `.temp/mgr172/sweep_cg.sh` is — and
   **test it by deleting a profile and re-running**.
6. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match.
7. ⓘ `.temp/mgr173/cg/` holds `ph64` profiles from F89's nine draws. **Reuse by
   exact `(row, cell, n)` match only, or not at all** — do not assume.

---

## §6 ⛔ SCOPE — read-only outside `.temp/php39/`

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, `pilot/`.** ⛔ **In particular: no
`spec.md` edit and NO GATE RUN** (§0). **Writes go to `.temp/php39/` only.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`14/0`**, **first and
last**. Manager-verified immediately before writing this. ⚠ **Nothing in your
scope can move either. If one moves, stop and report.**

---

## §7 Definition of done

1. `.temp/php39/` holds the probe, its `--selftest` **PASS** log, its sweep log,
   `NOTES.md`, and **one** regeneration entry point that has been **tested by
   deleting a profile**.
2. The report carries, as **tables of numbers and not as prose**: the 33-point
   `Ir(n)` series per cell-row; `SD`/`mean`/`min`/`max` per
   `(row, pair, W)`; the **exponent** per `(row, pair)` with residuals; and §3's
   cost estimate with its arithmetic shown.
3. ▶ **A verdict on §1's table: which of the three rows does the measurement
   land in, on `ph64` and on `ph29` separately.** ⚠ **If the two rows disagree,
   say so and do NOT average them** — `ph64` is the row that publishes B1 and
   `ph29` is the row where `inside_share` was declared void; they are different
   questions.
4. **Every N1–N8 verdict, and the F52 control you wrote.**
5. ⭐⭐ **`UNTESTED` and `I COULD NOT TELL` ARE VALUED ANSWERS.** The last task
   in this programme *"proposed a test, ran it, reported that its own must-fire
   negative FAILED, and shipped the failure instead of the test"* — and the
   manager recorded that as the right call (item 67). ⛔ **Do not produce a tidy
   exponent you do not believe.** The previous attempt's tidy `1/width` fit was
   two biases meeting, and saying so is why this task exists.
6. ⚠ **Declare your expectations for §1's table BEFORE you run the sweep**, in
   the report, and say afterwards whether they held. ⓘ The manager's last two
   declared expectations on `ph64` were **both wrong**, which is the argument for
   writing them down rather than against it.
