# TASK_PHP_042 — SEARCH `ph53`'s **BOTH ENDPOINTS**, and batch the row's whole debt into one re-gate

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_042_REPORT.md` — **write the FILE** (rule 10).

---

## §0 Why this and not row 8 — the manager's call, stated so it can be argued with

`quota.py`: **7 built, floor 40, 33 owed, 14 of 20 families empty.** A new row is
the obvious move and **I am not taking it**, for three measured reasons:

1. ⭐⭐ **`ph53`'s R3 came out DEAREST-BUT-ONE at `-O3` against `_040` §5.6's
   prediction of *"the cheapest rung on the row"*.** That is the strongest
   single signal in the corpus that **a spelling search will move something** —
   a refuted cost prediction is a statement that the shipped spelling is not
   the natural one.
2. ⚠⚠ **DEFERRING AN ENDPOINT SEARCH HAS BEEN THE EXPENSIVE CHOICE TWICE.**
   `ph29`'s R4 moved **5.63 pp** byte-identically (F77) and `ph45`'s R4 **AND**
   R3 both moved **with the bound's SIGN REVERSING** (F87). **2 of 2 rows
   searched properly had a moving endpoint.** ▶ **And the `fixed-R4 bound` is
   this programme's headline statistic**, so *"3 of 7 rows publish a bound over
   a number nobody has tried to move"* is a live threat to it, not a tidiness
   item.
3. **Everything is fresh.** `ph53` landed minutes ago; its `controls/`
   machinery is the newest in the tree and **already carries items 57/63's
   fixes**, so there is no repair to do before searching.

⭐ **And three debts share ONE re-gate** (items **80**, **79**, and F99's
citation), which is the lesson `TASK_PHP_033` learned by failing to batch.

⛔ **NOT in scope: item 62 (family C).** It is methodology, F92 removed its
urgency, and F91/item 78 may narrow its deliverable. **Row work first.**

---

## §1 ▶ THE PRIMARY JOB: `controls/spellings.py` for `ph53`, BOTH SIDES

**`TASK_PHP_037` is your template and it is the best precedent in the tree** —
read its report in full before writing anything. It searched `ph45`'s R4 *and*
R3, priced nine shipped variants plus seven dropped, and its §H suite was **128
cases**.

**Search both endpoints:**

| side | shipped | the question |
|---|---|---|
| **R3** `safe_tuned.rs` | ⚠ **dearest-but-one at `-O3`, against a prediction of cheapest** | **Why?** `_040` §5.6 predicted `push`-as-you-go would delete both the discriminant check and the zeroing pass. **Either the prediction's mechanism is wrong or the shipped spelling is not it.** ▶ **Find out which, and the answer is the finding either way.** |
| **R4** `unsafe.rs` | four trusted accessors, and F98 says it carries a **coverage witness the C does not, at `+21.8 %`** | Is there a spelling with **fewer trusted sites at the same or lower cost**? ⚠ `ph45` found two trusted-surface reductions that came out **DEARER** (+4.07 %, +7.51 %), so *"smaller surface"* is not free — **price it, do not assume it.** |

⚠⚠ **RULINGS THAT ALREADY BIND, SO YOU NEED NOT ASK:**
* ✅ **`#[inline(always)]` IS a legitimate respelling** — decided at `_037` on
  corpus precedent (**98 shipped rung files across both programmes**, including
  `unsafe.rs` and `verus.rs`), **not on argument.**
* ⛔ **A rung is NEVER cost-selected** (`.memory/02-bench-rules.md`). **The
  search reports what exists; the shipped rung stays put** unless the manager
  moves it. **Both variants ship side by side** so the contribution is visible
  rather than buried.
* ⛔ **An R4 candidate must VERIFY, and on this row it need NOT compile
  byte-identically** — `ph53` pins `identity differ`/`differ`, so item 61's
  wider bar applies and **F77's byte-identity method is not the binding
  constraint.**

---

## §2 ⭐ BATCHED: item 79 — the **ZERO-TRUSTED-ITEM** R5, measured

`_041` §8 reports that a **`MaybeUninit<&Iface>`** representation reaches
**5 verified / 0 errors with ZERO trusted items**, against the shipped rung's
**four** trusted accessors — and **rejected it unmeasured**, because *"the
compare-only consumer needs `ptr::eq`"*.

✅ **The rejection is honest and probably right.** ▶ **But measure it anyway**,
because **the trusted surface is one of this project's measured axes** and this
is **the first row where a zero-trusted-item R5 was in reach.** Report:

1. its **cost**, against the shipped R4/R5;
2. **exactly which consumer it drops and why** — is `ptr::eq` genuinely
   unavailable, or unspecified in the pinned vstd?
3. ⚠ **whether a two-representation row is even admissible** under §B/§A1, or
   whether it would have to ship as a `controls/` variant. **State it; do not
   decide it alone if it would change what the row publishes.**

⭐ **If it is cheaper AND smaller-surface, that is the sharpest R4/R5 result in
either programme** and the manager will want to move the shipped rung. **If it
is dearer, the shipped rung's four trusted items are PRICED rather than
assumed**, which is the result the row currently lacks.

---

## §3 ⭐ BATCHED: F99's citation, and it is free-riding on the re-gate

`ph53`'s hashed contract block still cites **`.temp/php41/probe_wrap.rs`** in
`verus.obligations_note`. `_041` repaired the **two** places it knew about
(`twin_justifications`, `unsafe_justifications` → `controls/mu_unwrapped.rs`)
and missed this third.

▶ **Retarget it at `controls/mu_unwrapped.rs`.** ⚠ **And `NOTES.md` cites
`.temp/php41/probe_mu.rs` and `probe_wrap.rs` too** — commit whichever is load
bearing under `controls/` or restate the claim without the pointer.
**`PROTOCOL_PHP.md` §F6** is the rule; **`python3 .tasks-php/citecheck.py` is
how you check you are done**, and it must report **no row-specific `.temp/`
citation for `ph53`** when you finish. ⛔ **Do NOT touch the other rows' 8
hashed citations or the 3 inherited ones** — those are other rows' debt and
items 55/61's.

---

## §4 ⚠ The traps

1. ⚠⚠⚠ **`grep -a` ALWAYS** (41 corpus files exit 1 silently under plain
   `grep`; a probe script does **not** reproduce it).
2. ⛔⛔ **DO NOT EDIT `inputs/gen.py`, any `.rs` rung file, or `c/*`** unless you
   are shipping a variant — **all three are in the MEASUREMENT digest, so an
   edit costs a 32-cell RE-MEASURE**, not just a re-gate. ⚠ **`spec.md`,
   `NOTES.md` and `controls/*` are gate-only: one re-gate, no re-measure.**
   ▶ **Know which side of that line every edit you make is on, and say so.**
3. ⚠ **A magnitude floor with every sign claim.** *"Every taxonomy written for
   this analysis needed one and none had one on the first pass"* — three times
   in one round, including an outlier test that fired at **0.00 pp**.
4. ⛔ **Never publish a percentage without saying WHICH INPUT it is on**
   (`check.py`'s own *DO NOT MAX IT OVER INPUT*, which has caught the manager).
5. ⚠ **Which statistic**: the row publishes **`A1`**, named. ⭐ **F91 is why** —
   `|B/A|` is **49.6–393.9×** where two rungs differ by 1–2 instructions, so **no
   callee-inclusive statistic can resolve a small code difference**, and an
   endpoint search is exactly that regime. ⚠ **Quote the whole-program column
   too, labelled**, as `ph45` does — `_037`'s A1 spread over nine variants was
   **`0.000000` pp** against **66.7 pp** whole-program, and **that contrast was
   the finding.**
6. ⚠ **`controls/*.py` is a VALIDATOR: §H binds.** Your `spellings.py` lands
   with its must-fire negatives or it does not land. ⭐ **`ph45`'s bar was 128
   cases and it found three real defects, two in code written that task.**
7. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match. No
   `until … sleep` poller loops.
8. ⚠ **`.temp/` is gitignored** — numbers go in the report, not behind a
   pointer. **That is this task's own §3.**

---

## §5 ⛔ Scope

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`, or any `patterns-php/` row OTHER THAN
`ph53-iface-tail-uninit/`.** Scratch under `.temp/php42/`.
⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`16/0`**, **first and
last.** ⚠⚠ **BOTH MUST BE UNMOVED AT THE END.** If the php figure moves you
have staled a measurement — **stop and report**, because that means you edited
something in the measurement digest (trap 2).

---

## §6 Definition of done

1. `patterns-php/ph53-iface-tail-uninit/controls/spellings.py` + `.json`, with
   its **must-fire and must-NOT-fire negatives** and the case count stated.
2. **Both endpoints' verdicts**: for each side, the variants priced, the winner,
   and whether the endpoint is **degenerate** or **moves**. ⚠ **Record
   `r3_endpoint_degenerate` / `r4_endpoint_degenerate` explicitly**, as `ph45`
   does.
3. ⭐ **AN ANSWER ON R3: why is the shipped spelling dearest-but-one when the
   prediction said cheapest?** *"The prediction's mechanism was wrong"* and
   *"the shipped spelling is not the prediction's spelling"* are **different
   findings** — say which, with the disassembly.
4. **Item 79 measured** (§2), including which consumer it drops.
5. **F99's citation gone**, verified by `citecheck.py` reporting no
   row-specific `.temp/` citation for `ph53`.
6. **Gate green, and the brackets `66/0` / `16/0` unmoved.** Quote `verdict`,
   `failures`, `complete_run`, the `identity` levels and `contract_sha256`
   **as fields**, not as a summary. ⓘ `verus_checked` and `problems` are **not
   gate fields** — do not look for them there (F99).
7. ⚠ **What you are UNSURE of, in its own section**, and ⭐ **`UNTESTED` /
   `I could not tell` are VALUED ANSWERS.** `_039` shipped a negative's failure
   rather than hide it, `_040` shipped a defect it could not fix, and `_041`
   reported 15 uncertainties and found its own citation defect. **All three were
   the right call.**
8. ⛔ **If a search finds nothing on either side, THAT IS A RESULT** — `ph07`
   and `ph16` both found their R4 degenerate and it is on file. **Do not
   manufacture a variant to have something to report.**
