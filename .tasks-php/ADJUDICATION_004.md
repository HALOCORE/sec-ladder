# ADJUDICATION_004 — **open item 119: six rows' recorded `fix_commit` is not the repair of their cited site**

**Manager, 2026-09-15.** ⚠ **UNREVIEWED.** Written while `TASK_PHP_056` was
running; it edits no file that task reads or writes.

**The item:** `TASK_PHP_054`'s three agents each found rows whose
`index.csv` `fix_commit` does not repair the site the row cites — **`ph67`,
`ph72`, `ph74`, `ph54`, `ph90`, `ph101`** — and ⛔ **`preimage_screen.py` returns
`CANDIDATE` for three of the six**, which is the first measurement of what that
label costs. The item says: *"A row whose R1h is on this list is
BLOCKED-ON-A-DECISION, not killed. None of the six fails the C-side bar."*

---

## §1 ⭐⭐⭐ THE HEADLINE: FIVE OF THE SIX ARE NOT BLOCKED ON A DECISION AT ALL. THEY ARE BLOCKED ON A **SEARCH**.

**I set out to make a rule and found that four of the six rows have simply never
been searched for their real repair, and a fifth has already been searched and
answered.** Triaged from what is on file:

| row | state | what is actually owed |
|---|---|---|
| **`ph90`** | ✅ **SOLVED ALREADY** — agent B found `0542a6f2c2a5` (2005-02-10, Rob Richards, 1 file, 3+/1−, at `array.c:1045-1046`) and **applied it to the pinned tarball with `git apply` strict, bytes verified moved** | **Nothing. Adopt it.** The row's R1h is that commit |
| **`ph54`** | ⛔ recorded commit **measured** not-the-repair (**0** occurrences of `get_current_data`; does **not touch** `Zend/zend_execute.c` at all; the faulting deref and the depth-1 guard both survive it) | **A search.** Nobody has looked for the real one |
| **`ph67`** | ⛔ the 2014 commit is a **pure refactor**; the destructor still runs on a linked bucket | **A search** |
| **`ph72`** | ⛔ six hunks, all about `userdata`, **none touches the cited `key`** | **A search** |
| **`ph101`** | ⛔ the only genuine `NOT-THE-REPAIR` **exclusion** among C's nineteen | **A search** |
| **`ph74`** | ⚠ `NOT-THE-REPAIR`, **and by 2006 the defect was already gone** — `MAKE_STD_ZVAL` + `dup=1` + `zval_ptr_dtor` were in the tree | ⭐ **The only one that might need a rule** — see §4 |

▶ ⭐⭐ **SO ITEM 119 IS MIS-FRAMED, AND THE RE-FRAMING IS THE DELIVERABLE: it is
not one decision the manager owes, it is ONE BOUNDED TASK the programme owes** —
the same search `FIXSURVEY_001` ran once for the whole catalogue, re-run for four
sites with the *"is this commit the repair of THIS LINE?"* test that `_054`
applied by hand and that the survey's own guard could not make.

⚠ **And the four are NOT urgent**, because **none of the four is a candidate for
the next several rows.** ▶ **The task is scheduled with the row that needs it,
not now** — a survey run against rows nobody is building is how `_015` stalled.

---

## §2 ⭐⭐ THE ONE REAL DEFECT, AND IT IS IN `PROTOCOL_PHP.md` §C

§C's headline is right: **"R1h is the real upstream fix."** Its **§F5 spelling**
then operationalises it as a lookup:

> *R1h is the `fix_commit` of the id whose `c_file_line` the row's kernel
> EXTRACTS. Singular. A kernel extracts one site; that site is one id's
> `c_file_line`; that id has one `fix_commit`.*

⛔⛔ **THAT CHAIN HAS A BROKEN LINK, AND THE PROGRAMME HAS MEASURED IT TWICE.**
**F38**: *"the `fix_commit` was a COLUMN IN THE CORPUS INDEX, and it is not
always THE fix"* — 3 of 5 hand-checked commits were **later** fixes. **F118**
measured the same thing wider: **six rows**, from three independent agents.

▶ **The correction is one clause, and it is a CORRECTION rather than an
extension:**

> **R1h is the upstream commit that REPAIRS THE CITED SITE. The `fix_commit`
> column is the best available EVIDENCE for which commit that is — it is not a
> definition of it, and on the corpus's own measurement it is wrong often enough
> to matter.** ▶ **A build task verifies the binding against the bytes before
> relying on it**, which is what every row since `ph55` has in fact done.

⚠ **Note what this does NOT change:** *singular* stands, the *"why not the union
of the commits"* argument stands, and the sibling-ids-are-census rule stands.
**Only the final inference — column ⇒ R1h — is replaced by column ⇒ evidence.**

⭐ **And it makes a tool's silence readable.** `preimage_screen.py` has four
outcomes and **only `NOT-THE-REPAIR` is a proof**; `CANDIDATE` and the two
`INAPPLICABLE` labels say nothing (F68/F95, item D11). **Three of these six
screen as `CANDIDATE`.** ▶ Under the old spelling that looked like weak support
for the column; under the corrected one it is **exactly what it is: silence.**

---

## §3 WHAT LANDS

| | |
|---|---|
| ✅ **`PROTOCOL_PHP.md` §C** | the §2 clause, **applied in place, not appended** (item 73 — seven instances of a correction appended instead of applied) |
| ✅ **`RECAP_PHP.md` item 119** | re-framed per §1: **one search task, scheduled with the row that needs it**, and `ph90`'s answer adopted |
| ⏳ **the four searches** | **NOT run now.** Scheduled with the row |
| ⏳ **`ph74`** | **ROUTED, not decided — §4** |
| ⛔ **`CATALOGUE.md`** | **UNTOUCHED.** No row's `fix_commit` column is edited; the column is the corpus's record of what the corpus said, and editing it would destroy the evidence for F38 and F118 |
| ⛔ **`.memory-php/`** | **NOTHING.** Unreviewed manager work; rule 9 |

---

## §4 ⛔⛔ `ph74` — WHERE I STOPPED, AND WHY STOPPING IS THE RIGHT ANSWER

`ph74`'s note says the defect *"was already gone by 2006"* through changes that
were not a fix for it. **If that holds, no single upstream commit repairs the
cited site, and the row has no R1h to build.**

✅ **MEASURED, and it is permitted by the machinery**: R1h is **optional at the
gate**. `harness/check.py` stage 7h reads

```
if not buildmod.has_hardened(pdir):
    print("    this pattern ships no c/kernel_hardened.c -- nothing to run")
```

and `rung_sources` derives the rung list from *"the presence of the file is the
whole switch"*. ⚠ **`p01` is the entire population of that branch today, and it
ships none because it MODELS NO BUG** — which is not `ph74`'s situation.

### ⛔ SO WHY AM I NOT WRITING THE RULE?

**Because §C's own history says this is exactly where a manager goes wrong, and
it says it about this same subsection:**

> ⚠ *Two drafts of this passage were written as a **PERMISSION** and both were
> refused* — `TASK_PHP_018` §4.1 refused the manager's, `TASK_PHP_022` §5.1
> refused the manager's re-wording of it. *The asymmetry is the reason: an
> under-stated observation costs one task when a second row needs it; an
> **over-stated norm is what has to be un-landed**.*

⭐⭐ **A rule saying *"a row may ship without R1h when no upstream commit repairs
the site"* is a PERMISSION, and it is the most abusable one available**, because
***"no repair exists" is far easier to assert than to disprove***. It is the same
hazard §C already names about tagged configurations — *"lets an engineer scan
tags until one suits"* — one step worse, since a failed search and a
non-existent fix look identical from the inside.

▶ **WHAT I RECORD INSTEAD, as an observation and explicitly not a permission:**

> **If a row reaches the point of needing this, the distinction that has to be
> made is between `NO REPAIR EXISTS` and `NOT SEARCHED`, and only the FIRST is a
> result.** ⭐ `ph74`'s note is already in the positive form that could support
> the first — it names the three specific things that were in the tree by 2006
> (`MAKE_STD_ZVAL`, `dup=1`, `zval_ptr_dtor`) and says the defect was gone
> **because of them**. **That is a claim about upstream code, testable against
> upstream code**, and it is the shape any such finding must take: *not* "I
> looked and found nothing."

⚠⚠ **And it must be brought to the manager as a PROPOSAL by the row that needs
it, with its upstream artefact, exactly as §C requires for `ph07`'s shape.**
**`ph74` is not scheduled. Nothing is owed today.**

---

## §5 WHAT I AM UNSURE OF

1. ⚠ **I have not read the C for any of the six.** Every fact in §1 is quoted
   from `_054`'s three reports and item 119, one of which (`ph54`) the manager
   re-measured and five of which it did not. **Law 12 applies to this document.**
2. ⚠ **I do not know that the four searches are cheap.** `_054` agent B found
   `ph90`'s real repair in the course of a broader task and made it look easy;
   **n = 1 for that**, and a search that fails is the expensive kind.
3. ⛔ **I do not know whether `ph74`'s *"already gone by 2006"* is right.** It is
   one agent's sentence and §4 rests on it being the *shape* of a testable
   claim, **not on it being true**.
4. ⚠ **The §2 correction is a manager construction landing in a subsection whose
   own banner says the manager has twice taken one party's construction into a
   standing document unattacked.** ▶ **It is smaller than those — it replaces an
   inference with the evidence relation the rest of §C already assumes — but it
   goes to the next reviewer whose task touches R1h, and `TASK_PHP_057` §3.1
   already has `F115`, which is the same subject.**
