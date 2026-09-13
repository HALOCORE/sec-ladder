# TASK_PHP_044 — **FIVE DEBTS, ONE `ph53` RE-GATE**: the pin item 83 ruled, the exclusion that is now one route, the fifth shared-control defect, and a detector's fill byte

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_044_REPORT.md` — **write the FILE** (rule 10).

⚠⚠ **YOUR SPECIFICATION FOR §2 AND §5 IS `TASK_PHP_043_REPORT.md` §1.8, AND IT IS
NOT RESTATED IN FULL HERE.** Read it. **If §1.8 and this file disagree on anything
technical, §1.8 wins; this file wins on scope.**

---

## §0 Why all five at once, and why that is the whole point

⛔⛔ **A SHIPPED ROW IS CURRENTLY PUBLISHING A RETRACTED PIN.** `TASK_PHP_043`
ruled item 83: `ph53`'s `idiom.required[4]` **pins the witness REPRESENTATION**,
so `r4_bitmask`, `r4_bitmask_pool` and `r4_bitmask_min` are **out of contract**,
`r4_endpoint_degenerate` is **true**, and F100's *"both endpoints move"* headline
keeps only its **R3** half. **`RECAP_PHP.md` says all that. `patterns-php/ph53-…/`
does not.**

⭐ **`spec.md`, `NOTES.md` and `controls/*` are GATE-ONLY: this is ONE re-gate and
NO re-measure.** ⚠⚠ **`TASK_PHP_033` learned the cost of not batching, and five
debts land on the same row.** ▶ **So the five below go together or the row goes out
internally inconsistent — a `spec.md` that pins a representation beside a
`spellings.json` that still reports the bitmask as in-contract is worse than
either error alone.**

| | item | what |
|---|---|---|
| §2 | **83** | `idiom.required[4]` restated so the pin is explicit |
| §3 | **83** | `controls/spellings.py`'s `ENGLISH_VERDICTS` **populated** — it is `{}` and was built for exactly this |
| §4 | **90** | `r3_no_capacity` — ⚠ **the test of whether the repair is a RULE or a patch** |
| §5 | **89** | the `invariant` clause, **`ph53` only** — the **fifth** shared-control defect |
| §6 | **85** | *"EXCLUDED, twice independently"* → **once**, and `:1945` → `:1944` |
| §7 | **96** | the `0xbe` clause — **it is ASan's fill byte, not the row's** |

---

## §2 ▶ ITEM 83 — `idiom.required[4]`, AND THE REPLACEMENT IS ALREADY DRAFTED

**Use `TASK_PHP_043_REPORT.md` §1.8's drafted text.** Read it there and apply it;
do not retype it from memory.

⚠⚠ **THREE THINGS ABOUT IT THAT ARE NOT NEGOTIABLE:**

1. ⛔⛔ **IT MUST NOT BE WEAKENED TO MATCH A WINNER.** The ruling is the reading
   under which the **cheaper** variants LOSE. `.memory/02-bench-rules.md`'s *a
   rung is never cost-selected* **applies to its pins**. ▶ **If you find yourself
   drafting something that lets the bitmask back in because it is cheaper, stop
   and report instead.**
2. ⭐ **The clause that decides it is the LEADING APPOSITIVE** — *"THE
   ONE-BYTE-PER-SLOT WITNESS"* defines **what the backticked span IS**. The draft
   makes that explicit and adds `[bool; MAXD]`. **Keep that structure.**
3. ⚠ **`PROTOCOL_PHP.md` §H1: never backtick a spelling containing a character
   literal.** Nothing in the draft should, but check.

✅ **AND ONE THING YOU NEED NOT RE-ARGUE:** the ruling's *route*. `_043` §1.2
settles it, and it also records that **the manager's route was an over-read** —
`harness/check.py::idiom_audit` (`:2198-2212`) measures the naive
every-span-in-every-rung reading at **41 misses of 158 obligations, all 41
non-defects, 17 ANTI-signal**. ▶ **Do not reintroduce that reasoning anywhere in
the row's prose.**

---

## §3 ▶ ITEM 83 (b) — `ENGLISH_VERDICTS` IS `{}` AND WAS BUILT FOR THIS

`controls/spellings.py` carries **`ENGLISH_VERDICTS = {}`** with a comment saying
*"A module constant so a negative can assert the exclusion actually reaches
`cheapest_in_contract`."* ⭐ **The mechanism exists, is unused, and is the right
place — so use it rather than inventing a second one.**

**Populating it must, mechanically:**
* flip **`r4_endpoint_degenerate` → `true`**;
* exclude `r4_bitmask`, `r4_bitmask_pool`, `r4_bitmask_min` from
  `cheapest_r4_in_contract`;
* leave **`r3_endpoint_degenerate` false** and
  **`cheapest_r3_in_contract = r3_chunks_mask`** — ⛔ **the R3 half of F100 is
  UNTOUCHED by this ruling and must stay that way.**

⚠⚠ **§H BINDS: the change lands with its must-fire negatives.** `_043` says the
existing suite already covers the path — ▶ **verify that claim rather than
inheriting it, and if it does not, write the negative.** ⭐ **The negative that
matters is the one that fails if `ENGLISH_VERDICTS` is emptied again**, because
that is the edit a later agent will make by accident.

⚠ **`a1_spread_pp` WILL MOVE on the R4 side** — `_043` computes
**`45.313019 → 33.917949`** (R3 **unchanged**). ✅ **Expected, and it does not
touch item 82's conclusion: tens of pp either way.** ▶ **Report the number you
get and say whether it matches `_043`'s.** ⓘ `_043` notes `a1_spread_pp` is
computed **with no `in_contract` filter**, so whether it *should* move is a real
question — **state which you implemented and why.**

---

## §4 ⚠⚠ ITEM 90 — `r3_no_capacity`, AND IT IS THE TEST OF WHETHER THIS WAS A RULE

`_043` §1.4 reports a **second** in-contract violation, independent of the witness
dispute: **`r3_no_capacity` records `required_absent` on `required[0]`
`` `Vec::with_capacity(num_interfaces)` ``**, whose English scopes it to the
R3/R4 rungs.

⭐⭐ **WHY THIS MATTERS MORE THAN ITS SIZE: apply the ruling only to the three
bitmask variants and the repair is a patch on the variants that embarrassed the
headline. Apply it here too and it is a rule.**

⛔⛔ **BUT VERIFY THE SCOPE FIRST, BECAUSE THE REVIEWER FLAGGED THIS AS ITS OWN
BIGGEST UNCERTAINTY** (`_043` §7.1): *"the English-scope transcription is MINE, by
hand … no gate stage reproduces this."* ▶ **Read `required[0]`'s English yourself
and decide whether it really scopes to R3.** ⓘ Its Rust key says
`safe_naive.rs` *"writes a vector of None instead and does NOT match this
entry"* — **so the entry contemplates a non-matching rung, which cuts both ways.
Argue it.**
✅ **Item 83's primary result does NOT depend on this** — it needs only
`required[4]` scoped to R4, which the entry states in so many words. ▶ **So if you
conclude `r3_no_capacity` is fine, say so and leave it; that is a result, not a
failure to fix something.**

---

## §5 ▶ ITEM 89 — THE `invariant` CLAUSE, **`ph53` ONLY**

`controls/spellings.json`'s `invariant` opens *"Every variant is in contract by
`harness/check.py::spelling_matches` over **EVERY** backticked idiom entry"* —
**and that is false as written in 5 of 5 php rows**, because `required_absent` is
non-empty on variants the row ships, **including on R3's `v0_shipped`**.

**Suggested replacement for the opening clause is in `_043` §1.8 item 3.** The
substance: `in_contract` means **`forbidden_hits` empty**; `required_absent` is
**reported beside it** and is **judged against each entry's English**, because
`required` is **presence-only and cannot fail the gate**
(`check.py::idiom_audit`).

⛔⛔ **`ph53` ONLY. DO NOT TOUCH `ph07`, `ph16`, `ph29` or `ph45`** — each costs its
own re-gate and batches with that row's next task (item 89). ⓘ PAT's two copies
do not carry the clause; **`patterns/` is frozen regardless.**

⭐ **This is item 81's law holding a FIFTH time, and it was PREDICTED.** ▶ **So
expect your own new negatives to find a SIXTH. Write new ones; do not clone.**

---

## §6 ▶ ITEM 85 — *"EXCLUDED, TWICE INDEPENDENTLY"* IS NOW **ONCE**

**Two sites, both in `spec.md`: `:23` and `:68`** (`idiom.required[5]`). Both
assert the two-route exclusion of `be8daf1f47fa` and both name the screen route.
⛔ **The screen route is gone** — `preimage_screen.py`'s `same_function` soundness
repair correctly demoted that record to **`INAPPLICABLE-SAME-FILE`**, which the
screen prints as *"NOT exclusions … says nothing about these"*.

✅✅ **THE EXCLUSION ITSELF STANDS, ON THE TAG WALK ALONE** — the cited `erealloc`
line survives php-5.0.1–5.0.4 and is **gone at php-5.0.5**, **2 y 9 mo before** the
commit. ▶ **So this is a bookkeeping repair and NOT a change to the row's R1h.**
⚠ **Also `:1945` → `:1944`** for the inheritance-merge survivor — **check it
against the tarball yourself**, because the manager's own reading of that line
needed a correction once already.

⭐ **Worth one sentence in the row's prose, because it is the transferable
lesson:** *a repair to a screen can silently withdraw a route a finding is still
citing, and nothing re-checks the finding.*

---

## §7 ▶ ITEM 96 — `0xbe` IS **ASan's FILL BYTE**, NOT THE ROW'S

`cwe_note` (inside the hashed block) reports R1 faulting with *"member access
within misaligned address **`0xbebebebebebebebe`**"*. **Measured on this box
(`.temp/mgr176/asanfill.c`): a fresh `malloc(64)` under
`clang -O1 -fsanitize=address` reads `be be be be be be be be`; WITHOUT ASan it
reads zero.** ⛔ **The shim does not produce it** — it **zeroes** fresh blocks and
poisons **`0x5a` on free**.

▶ **Add ONE clause saying whose pattern it is.** ✅ **Nothing about the row's
verdict changes**: the slot genuinely is indeterminate and ASan genuinely reports
it. ⚠ **Do NOT rewrite the finding** — the defect is that a detector-dependent
observation reads as a row property, and one clause fixes it.
⭐ **Re-measure it yourself before writing the clause.** The generator is committed
under `.temp/mgr176/` — ⚠ **but `.temp/` is GITIGNORED, so if you rely on it,
the number goes in YOUR REPORT and the clause must not cite that path**
(`PROTOCOL_PHP.md` §F6).

---

## §8 ⚠ The traps

1. ⛔⛔ **KNOW WHICH DIGEST EVERY EDIT TOUCHES AND SAY SO.** `spec.md`, `NOTES.md`
   and `controls/*` are **gate-only → one re-gate**. ⚠⚠ **`inputs/gen.py`, the
   four `.rs` rungs and `c/*` are in the MEASUREMENT digest — an edit there costs
   a 32-cell RE-MEASURE.** ▶ **This task should touch NONE of them.**
2. ⚠⚠⚠ **`grep -a` ALWAYS** (41 corpus files exit 1 silently under plain `grep`).
   ⭐ **And a line-based grep cannot find a prose phrase that WRAPS** — which is
   how `:23`'s copy of the *"twice independently"* claim could be missed.
3. ⛔ **Never publish a percentage without WHICH INPUT and WHICH STATISTIC.**
4. ⓘ **`verus_checked` and `problems` are NOT gate-record fields** — they live in
   `controls/spellings.json`; `problems` is also a **preflight** field.
   ⭐ **And F100's `31/0` / `32/0` are in `NOTES.md:550` and `:741`, not in
   `spellings.json`** (item 84). **Name the file for every field you quote.**
5. ⚠ **`PROTOCOL_PHP.md` §F6**: `spec.md` / `NOTES.md` must not cite `.temp/`.
   **`python3 .tasks-php/citecheck.py` must report NO row-specific `.temp/`
   citation for `ph53` when you finish** — it reports none today, so **you must
   not introduce one** (§7 is where that risk lives).
6. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; no
   `until … sleep` poller loops.
7. ⚠ **A truncated `ls`/`head` is not evidence of absence.**

**Scope:** ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`, or any `patterns-php/` row OTHER THAN
`ph53-iface-tail-uninit/`.** Scratch under `.temp/php44/`.
⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Brackets**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`16/0`**, **first and
last**, both verified by the manager immediately before writing this.
⛔⛔ **BOTH MUST BE UNMOVED AT THE END. If the php figure moves you have staled a
measurement — STOP AND REPORT**, because it means you edited something in the
measurement digest (trap 1).

---

## §9 Definition of done

1. **All five debts landed in ONE re-gate**, and `contract_sha256` quoted
   **before and after** so the re-gate is visible.
2. **Gate green.** Quote `verdict`, `failures`, `complete_run`, the `identity`
   levels and `contract_sha256` **AS FIELDS**, not as a summary.
3. ⭐ **`r4_endpoint_degenerate` = `true` and `r3_endpoint_degenerate` = `false`**,
   read out of the regenerated `controls/spellings.json`, with
   `cheapest_r3_in_contract` still **`r3_chunks_mask`**.
4. **Your `ENGLISH_VERDICTS` negatives, with the case count**, including the one
   that fires if it is emptied.
5. **Item 90 decided either way, with the English quoted** — *"`r3_no_capacity`
   is fine and here is why"* is a valid answer.
6. **`a1_spread_pp` reported**, with whether it matches `_043`'s
   `33.917949`, and **which filter you implemented**.
7. **`citecheck.py` clean for `ph53`**, and the brackets `66/0` / `16/0` unmoved.
8. ⚠ **WHAT YOU ARE UNSURE OF, in its own section.** ⭐ **`UNTESTED` and *"I could
   not tell"* are VALUED ANSWERS** — `_039` shipped a negative's failure, `_040` a
   defect it could not fix, `_041` fifteen uncertainties and its own citation
   defect, `_043` two harness bugs of its own. **All four were the right call.**
9. ⛔ **If any of the five turns out not to need the edit, THAT IS A RESULT.**
   **Do not manufacture a change to have landed all five.**
