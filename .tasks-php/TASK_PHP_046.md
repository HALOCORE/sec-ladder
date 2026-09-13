# TASK_PHP_046 — SEARCH `ph52`'s **BOTH ENDPOINTS**, and build the control the row shipped without

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_046_REPORT.md` — **write the FILE** (rule 10).

---

## §0 Why this and not row 9 — and the cost argument is now measured

`TASK_PHP_045` §23 names it: **`ph52` ships with no `controls/spellings.py`, so its
headline has no in-contract spread beside it and `controls_json` is `{}`.** Four
reasons this is next:

1. ⭐⭐ **THE ENDPOINT SEARCH HAS FOUND SOMETHING ON 3 OF 3 ROWS PROPERLY
   SEARCHED.** `ph29`'s R4 moved **5.63 pp byte-identically** (F77); `ph45`'s R4
   **and** R3 both moved **with the bound's sign reversing** (F87); `ph53`'s R3
   moved **−32.08 %** (F100). ⛔ **And `ph07`/`ph16` found their R4 degenerate,
   which is also on file** — so the prior is "it moves", not "it must move".
2. ⭐⭐⭐ **THE `fixed-R4 bound` IS THIS PROGRAMME'S HEADLINE STATISTIC**, and a row
   publishing a bound over a number nobody has tried to move is a live threat to
   it. **`ph52` is currently such a row.**
3. ⭐ **Everything is fresh** — the row landed hours ago, so its machinery is the
   newest in the tree and you are cloning `ph53`'s **post-repair** control, which
   already carries items 83/89/97's fixes.
4. ⚠⚠ **AND IT IS MEASURED DEBT, NOT TIDINESS.** `task_cost.py` now separates
   searched from unsearched rows: **`ph52` landed at `1.00` tasks, the cheapest
   figure in the series, because it skipped this task** — and the comparable
   marginal is **3.23, not 2.75**. ▶ **Three rows owe a search (`ph03`, `ph64`,
   `ph52`); this is the one where it also buys the missing spread.** (Item 102.)

---

## §1 ▶ THE PRIMARY JOB: `controls/spellings.py`, BOTH SIDES

**`patterns-php/ph53-iface-tail-uninit/controls/spellings.py` is your template and
it is the best in the tree** — it is the one `TASK_PHP_044` repaired. Read
`TASK_PHP_042_REPORT.md` (the search that produced it) and
`TASK_PHP_044_REPORT.md` §3 (what was wrong with it) before writing anything.

| side | shipped | the question |
|---|---|---|
| **R3** `safe_tuned.rs` | A1 `52,125,944`, i.e. **6.7 % dearer than R4** | **Is that gap a spelling or a mechanism?** `ph53`'s R3 answer was *the prediction's MECHANISM was wrong* — nine window bounds checks worth more than the whole R3−R4 gap. ▶ **Look for the same shape here**: this row now has `win_get_unchecked` on the unsafe side and **checked** window reads on the safe side, so the safe side is paying for bounds checks the C never had. **Price them.** |
| **R4** `unsafe.rs` | **ONE trusted item** (`slot_read_unchecked`), A1 `48,846,257`, `identity O3 norel` with `verus.rs` | Is there a spelling with the **same or lower cost**? ⚠ `ph45` found two trusted-surface reductions that came out **DEARER** (+4.07 %, +7.51 %) and `ph53` found one **cheaper and smaller** that was **out of contract** — so *"smaller surface"* is neither free nor automatically admissible. **Price it; do not assume it.** |

⚠⚠ **RULINGS THAT ALREADY BIND, SO YOU NEED NOT ASK:**
* ✅ **`#[inline(always)]` IS a legitimate respelling** — decided at `_037` on
  corpus precedent (98 shipped rung files), not on argument.
* ⛔ **A rung is NEVER cost-selected** (`.memory/02-bench-rules.md`). **The search
  reports what exists; the shipped rung stays put** unless the manager moves it.
  **Both variants ship side by side** so the contribution is visible.
* ⛔ **`identity` is pinned `O0 differ` / `O3 norel`** — so an R4 candidate must
  **verify** and needs `norel` equality with its twin at `O3`, **not byte
  identity**. ⚠ **`norel` is NOT `exact`: read `check.py`'s own definition before
  you assume what it permits.**

### 1.1 ⛔⛔ AND ONE THING THIS ROW'S R4 SEARCH MUST NOT DO

**F104**: the gate's `n_twins == 0` rule hard-failed this row because its trusted
base is the **smallest in the corpus**, and `ph53` passes the same stage only
because **its base is larger**. ▶ ⛔⛔ **SO DO NOT "IMPROVE" THE R4 BY ADDING A
TWINNABLE TRUSTED ITEM TO MAKE A GATE STAGE HAPPIER.** That would be
cost-selection on the TCB axis — the exact pressure F104 reports — and the TCB is
one of this project's **published** axes. ⭐ **If a variant with a LARGER trusted
base is cheaper, that is a RESULT to report, not a rung to ship.**

---

## §2 ⭐⭐⭐ WHICH STATISTIC — **A1, AND IT IS *NOT* THE ROW'S HEADLINE. THIS IS MEASURED, NOT ASSUMED.**

⛔⛔ **THE ROW PUBLISHES W1 AND YOUR SEARCH MUST PUBLISH A1, AND BOTH ARE RIGHT.**
`.memory-php/03-numbers.md` (landed this session): **`inside_share` is PER-CELL,
not per-row.** Measured on `ph52`, `O3/isolated`, `small.bin`:

| cells | `inside_share` | why | the column |
|---|---:|---|---|
| **C rungs** (`c-gcc`, `c-gcc-h`, …) | **22.24 %** | `PH52_NOINLINE` puts three callees in their own symbols — **62.35 % of the program** — and the R1/R1h difference lands **entirely** there | **W1** ✅ what the row publishes |
| ⭐ **Rust rungs** (`safe_tuned`, `unsafe`, `verus`) | **≈98.6 %** | they inline everything: `unsafe` A1 **48,846,257** against W1 **49,549,469** | ⭐ **A1** ◀ **your search** |

▶ **A respelling of `safe_tuned.rs` or `unsafe.rs` changes code inside a symbol
that carries 98.6 % of its own program, so A1 resolves it to the instruction.**
⭐ **F91's reason applies in full here**: `|B/A|` is **49.6–393.9×** where two rungs
differ by 1–2 instructions, so **no callee-inclusive statistic can resolve a small
code difference**, and an endpoint search is exactly that regime.

⚠⚠ **VERIFY BOTH FIGURES YOURSELF BEFORE YOU RELY ON THEM** — they are the
manager's, read from `results-php/ph52-concat-copy-uninit.json` and `_045` §4/§6.2.
⚠ **Quote the whole-program column beside A1, labelled**, as `ph45` and `ph53` do:
`_037`'s A1 spread over nine variants was **`0.000000` pp** against **66.7 pp**
whole-program, **and that contrast was the finding.**
⛔ **Never a percentage without WHICH INPUT, WHICH STATISTIC, WHICH LEVEL, AND WHAT
AGAINST** — F98 shipped missing all four (item 84).

---

## §3 ⛔⛔ TWO LAWS THAT BIND YOU AS *STEPS*, NOT AS SENTENCES

**Both were broken by the last two tasks — a reviewer, then an engineer — which is
why they are here as procedure.**

1. ⛔⛔ **A BACKTICK IN AN `idiom.required` / `forbidden` ENTRY *IS* A PIN, INCLUDING
   AROUND A FILENAME OR A TYPE NAME.** ▶ **IF YOU TOUCH THAT PROSE AT ALL, RUN
   `controls/spellings.py --audit-only` ON THE DRAFT AND READ THE OUTPUT BEFORE
   LANDING IT.** `_043` drafted three spans it did not mean to pin (`` `u32` ``
   matched every rung — the **ANTI-signal** class `idiom_audit` measures at **17 of
   41**; two others matched none); `_045` then did it again on its own row, and
   **`_045` §8.4 found a second, worse one in `required` where the gate cannot see
   it.** ⭐ **Neither was found by reasoning. Both were found by running the audit.**
   (Item 100.) ⓘ **You may not need to touch `idiom` at all — if so, say so.**
2. ⛔⛔ **§H's NEGATIVES GO *INSIDE* THE VALIDATOR, NOT IN A `.temp/` PROBE.**
   `citecheck.py` now reports **13 §H-at-risk citations across 4 rows**: a committed
   validator whose must-fire suite lives in gitignored `.temp/` satisfies §H **in a
   way that does not survive a checkout** (item 97). ▶ **Do what `_044` did for
   `ph53`: put the arms in `controls/spellings.py` so they run on every invocation
   and feed `problems`** — then breaking the guard is a **red gate** (stage 9b
   `FRESH+VERDICT-FAILED`), not a better-looking number. ⭐ **Do not create this
   row's share of that debt.** ⚠ `python3 .tasks-php/citecheck.py` must report **no
   new §H-subclass citation for `ph52`** when you finish.

---

## §4 ⚠ Batched, and both are cheap

1. **Item 104** — four `harness/build.py` **line-number** citations in this row have
   rotted, and repairing a pointer costs a re-measure because the citing files are
   in the **measurement** digest. ▶ **Check whether anything you do forces a
   re-measure. If it does, fix them in the same run; if not, leave them and say so.**
   ⭐ **And the general repair is item 98's: a file in the measurement digest carries
   no pointer that can age — cite a SYMBOL NAME, not a line number.**
2. **Item 102's second half** — the row's in-contract **spread** is what this task
   delivers. **Report `a1_spread_pp` and the whole-program spread**, and ⚠ **state
   whether you apply an `in_contract` filter**: `_043` assumed `ph53` filtered and
   **it does not** (`_044` §3.4), so the question is live and the answer must be
   explicit either way.

---

## §5 ⚠ The traps

1. ⚠⚠⚠ **`grep -a` ALWAYS** (41 corpus files exit 1 silently). ⭐ **And a
   line-based grep cannot match a prose phrase that WRAPS** — that has now cost two
   censuses.
2. ⛔⛔ **KNOW WHICH DIGEST EVERY EDIT TOUCHES AND SAY SO.** `spec.md`, `NOTES.md`
   and `controls/*` are **gate-only → one re-gate**. ⚠⚠ **`inputs/gen.py`, the four
   `.rs` rungs and `c/*` are in the MEASUREMENT digest → a 32-cell RE-MEASURE** —
   **which is the expected cost IF you ship a variant**, so say which you are doing.
3. ⚠ **A magnitude floor with every sign claim.** An outlier test in this programme
   once fired at `0.00 pp`.
4. ⓘ **`verus_checked` and `problems` are NOT gate-record fields** — they live in
   `controls/spellings.json`; `problems` is also a **preflight** field. ⭐ **And a
   twin's `verified/errors` counts live in `NOTES.md`, not in `spellings.json`**
   (item 84). **Name the file for every field you quote.**
5. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; no
   `until … sleep` poller loops.
6. ⚠ **A truncated `ls`/`head` is not evidence of absence.**
7. ⓘ **`results-php/preflight/_norow.preflight.json` DE-DUPLICATES** and taking a
   bracket reading writes to it (item 103) — **expected; not your defect.**

**Scope:** ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`, or any `patterns-php/` row OTHER THAN
`ph52-concat-copy-uninit/`.** ⛔⛔ **AND DO NOT TOUCH `harness/check.py` TO RELIEVE
F104** — item 105 prices that and it is the manager's call.
Scratch under `.temp/php46/`. ⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Brackets**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`18/0`**, **first and last**,
both verified by the manager immediately before writing this.
⚠ **`18/0` → `18/1` while you edit gate-only files and back to `18/0` after the
re-gate is EXPECTED and is not a problem** — that bracket covers gate records too.
⛔ **`66/0` moving, or a MEASUREMENT record going stale without your having shipped
a variant, is the real tripwire. Stop and report.**

---

## §6 Definition of done

1. `patterns-php/ph52-concat-copy-uninit/controls/spellings.py` + `.json`, **with
   its must-fire AND must-NOT-fire negatives INSIDE the validator** (§3.2), and the
   case count stated.
2. **Both endpoints' verdicts**: for each side, the variants priced, the winner, and
   whether the endpoint is **degenerate** or **moves**. ⚠ **Record
   `r3_endpoint_degenerate` / `r4_endpoint_degenerate` explicitly.**
3. ⭐ **AN ANSWER ON R3: is the 6.7 % R3−R4 gap a SPELLING or a MECHANISM?** Those
   are different findings — say which, with the disassembly. ▶ **`ph53`'s answer was
   *mechanism*, and the bounds-check shape is present here too.**
4. **§2's statistic decision confirmed by your own measurement**, with `a1_spread_pp`
   and the whole-program spread both reported, and the `in_contract` filter question
   answered explicitly.
5. **Gate green**, `contract_sha256` before and after, and **`verdict`, `failures`,
   `complete_run`, the `identity` levels** quoted **AS FIELDS**.
6. **`citecheck.py` clean for `ph52`, including no new §H-subclass citation.**
7. ⚠ **WHAT YOU ARE UNSURE OF, in its own section.** ⭐ **`UNTESTED` and *"I could
   not tell"* are VALUED ANSWERS** — the last five tasks each shipped a defect, a
   failure or an uncertainty it could have hidden, and each was right to.
8. ⛔ **IF A SEARCH FINDS NOTHING ON EITHER SIDE, THAT IS A RESULT.** `ph07` and
   `ph16` both found their R4 degenerate and it is on file. **Do not manufacture a
   variant to have something to report.**
