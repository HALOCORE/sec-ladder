# MANAGER NOTES while `TASK_PHP_047` runs — **PENDING MERGE INTO `RECAP_PHP.md`**

> ⛔⛔ **THIS FILE EXISTS BECAUSE OF RULE 11, AND IT IS DELETED ON MERGE.**
> `_047` is a reviewer whose read list covers `RECAP_PHP.md`, `.memory-php/`,
> `PROTOCOL_PHP.md`, `patterns-php/`, `harness/` and the named committed
> checkers — so while it runs, **the manager may not EDIT or COMMIT any of
> them.** Findings made in that window have nowhere to live.
>
> ⭐ **The wrong answer is `.temp/`** — that is **F99's own defect** (the
> committed claim layer resting on gitignored scratch, ten places, two already
> gone) and **item 86's class**. This file is **committed**, so it survives a
> checkout and a compaction. ▶ **On `_047`'s landing: merge into `RECAP_PHP.md`
> and DELETE this file.** ⚠ **If you are reading this and `_047` has landed,
> the merge did not happen — do it.**

---

## 1. ⭐⭐ ITEMS 91, 98 AND 103 ARE COUNTED AND **TWO OF THE THREE ANSWERS INVERT THE ITEM**

Landed as `.tasks-php/contract_audit.py` (commit `f2244f0`), **8 §H negatives
inside the validator**, `--selftest` green, and **the failing path verified to
return 1 rather than assumed to.**

### 1.1 ITEM 91 — **CLOSEABLE. There is no corpus-wide problem.**

| | count |
|---|---:|
| idiom entries scanned, both programmes | **648** |
| `rust` as the only language key | **27** |
| …of those, in **`forbidden`** | **24** ← **not the concern** |
| …of those, in **`required`** | ⭐ **3** ← the narrowed subject |

⭐ **A `rust`-only `forbidden` entry is the only sensible shape**: there is
nothing in the C to forbid when the construct does not exist in C — `HashMap`,
`transmute`, `ManuallyDrop`, `Box::leak`, `#[verifier::exec_allows_no_decreases_clause]`.
**Item 91 conflated the two fields.**

**The three `required` entries, in full:**

* `patterns/p19-state-machine required[2]` — opens *"THE RUNG BOUNDARY INSIDE THE
  SAFE CLASS, and it is one token"*
* `patterns/p46-bignum-mac required[4]` — opens *"THE RUNG BOUNDARY INSIDE THE
  SAFE CLASS, and it is one construct"*
* `patterns-php/ph53-iface-tail-uninit required[4]` — the witness, **the entry
  item 83 already ruled on**

▶ ⭐ **Two of the three DECLARE in their own opening words that they are pinning
a rung boundary, so they are declared rather than smuggled; the third is already
adjudicated.** ▶ **Item 91 closes with the count as its answer. No new field
(`rung_required`) is needed for three entries, two of which say what they are.**

### 1.2 ⭐ AN INCIDENTAL MEASUREMENT THAT MATTERS TO ITEM 107

**343 of the 648 idiom entries are PLAIN STRINGS with no language keys at all.**

| shape | count |
|---|---:|
| plain string, no language key | **343** |
| `c` + `rust` | 267 |
| `rust` only | 27 |
| `c` only | 11 |

⛔⛔ **So the `idiom` schema is HETEROGENEOUS, and a validator that assumes
per-language dicts silently skips more than half the corpus.** ⭐ **That is item
107's hazard one layer down** — item 107 says a validator reading `idiom` prose
inherits every incidental backtick; this says it may not even *see* the majority
of entries. ▶ **Add to item 107.**

### 1.3 ITEM 98 — **THE CORPUS ALREADY FOLLOWS OPTION (a). The policy RATIFIES practice.**

Splitting `c/*` provenance prose into two classes is what settles it:

* **POINTER** — *"`NOTES.md` §7 says so in terms"*, *"`controls/fortify.py`
  measures both configurations"*. **Asserts nothing, so it cannot age into
  falsehood.** **27 instances.**
* **VERDICT** — *"`preimage_screen.py` labels it `NOT-THE-REPAIR`
  independently"*. **Asserts another artefact's conclusion, and that is what
  aged.** **6 raw hits, of which ⭐ 2 are REAL** — and they are the two lines of
  **F98's own known sentence** in `ph53/c/kernel_hardened.c:8-9`.

▶ **Write policy (a)** — *a `c/*` comment may POINT at where an argument lives;
it may not STATE that argument's verdict* — **and record that it ratifies
existing practice rather than changing it.** ⓘ **No row owes a repair**; `ph53`'s
is already recorded as known in its `spec.md` and `NOTES.md`.

### 1.4 ⭐⭐ THE RATCHET CAUGHT THE MANAGER ON ITS FIRST RUN, AND THAT IS THE METHOD FINDING

**4 of the 6 VERDICT hits are classifier false positives** — `independent`
inside the compound adjective *"order-independent"*, `labels` as a **plural
noun**, and *"`diff` proves it"* where `diff` ranges over files that are
themselves in the digest.

⛔ **The tempting repair was to tune the regex until the count looked right —
the exact anti-pattern this programme keeps catching (F10, *a grepping guard has
a spelling*).** ▶ **Instead every hit is adjudicated BY HAND in an `ADJUDICATED`
table with its reason, and `N8` fails on any hit that is UNFILED *or* on any
adjudication that has gone STALE.** ⭐ **It failed immediately on a line I had
filed from memory as `:484` when the real hit was `:640`** — which is the
argument for building it that way rather than the objection to it.

### 1.5 ITEM 103 — **SETTLED: `results-php/preflight/*` IS IN NO DIGEST.**

**18** gate + measurement records scanned · **0** mention `preflight` · **0**
digest entries name a preflight path. ▶ **So taking the required bracket reading
cannot stale anything, and option (a) is free and correct.**
⚠ **The `PROTOCOL_PHP.md` sentence is OWED and was not written** — that file is
in `_047`'s read list. ▶ **Write it on merge.** `N7` fails if this ever changes.

---

## 2. ⛔⛔ A CHECKER HAS BEEN RED SINCE 2026-09-10 ON SOMETHING IT ADJUDICATES AS CORRECT

**`coverage.py` exits 1 in its intended steady state.** Its substantive claims
are all green — **`166 / 166` accounted for, `MISSING 0`, 102 Part A rows, 102
Part B blocks, no gaps** — but `bad` includes `dup`, and the two duplicates are
`LOGIC-011` and `LOGIC-022`, both `['ph77', 'ph83']`, which **the script's own
output declares ADJUDICATED in `CATALOGUE.md`** with a corroborating reason (the
ids are *sites* in `ph77` and the *mechanism* in `ph83`; they resolve to
**different fix commits**, and `PROTOCOL_PHP.md` §G1 says a distinct fix is
evidence for DIFFERENT).

⛔ **So the script prints its own adjudication and then fails on it.** Introduced
deliberately at `c10dbb9` (2026-09-10, *"carry the verdict on a double-claimed
id, instead of just the warning"*) — the intent was right, the consequence is
that **the exit code now carries no signal**: a reader cannot tell *"coverage is
fine"* from *"coverage broke"*.

⚠⚠ **AND IT BEARS ON A SENTENCE I HAVE BEEN PUBLISHING.** I have reported *"all
checkers pass"* at task boundaries. **Measured now, two of ten exit non-zero:**

| checker | exit | is it flagging owed work? |
|---|---|---|
| `boxcheck` `quota` `fixsurvey` `php_null` `task_cost` `contract_audit` `preimage_screen --selftest` `width --selftest` | **0** | — |
| `citecheck` | **1** | ✅ **YES** — the 13 §H-at-risk citations, item 97, genuinely owed |
| ⛔ **`coverage`** | **1** | ⛔ **NO** — two duplicates it adjudicates as correct |

▶ **The accurate statement is: every checker's substantive claim is green, and
two exit 1 — one legitimately.** ⭐ **Not *"all checkers pass"*.**

▶▶ **THE REPAIR, AND IT IS FREE** (`.tasks-php/*.py` is in no digest): give
`coverage.py` the same ratchet `contract_audit.py` just got — **an adjudicated
duplicate is reported and excluded from `bad`, and an UNFILED duplicate fails.**
Then a red `coverage.py` means something again.
⛔ **NOT DONE: `coverage.py` is in `_047`'s read list (rule 11).** ▶ **Do it on
merge.** → **open a new item for this.**

---

## 3. ⭐⭐⭐ ROW 9 IS SCREENED AND **ITEM 95 IS ANSWERED** — full detail in `.tasks-php/TASK_PHP_048.md`

`_048` is **written and committed but NOT dispatched** (one agent at a time).
Summary of what the screening produced, so it is not lost:

* ⭐ **ITEM 95 ANSWERED — DELIBERATE HAND-OFF, NOT A SECOND DEFECT.**
  `zend_throw_exception_internal` parks the PC at `opcodes[last-1-1]`, **one slot
  short of `ZEND_HANDLE_EXCEPTION`** (which `zend_do_end_function_declaration`
  emits last), **in anticipation of the `EX(opline)++` that the handler's own
  trailing `NEXT_OPCODE()` performs**; `zend_exceptions.c:53` reads the same
  invariant back. ▶ **`INC_OPCODE()`'s `if (!EG(exception))` guard stops the
  stride being spent twice.** ⭐ **The row needs ONE error exit, not two** —
  which is the shape question item 95 said would decide the row.
* ⭐⭐ **THREE FACTS THE CATALOGUE DID NOT HAVE.** `INC_OPCODE()` has **four**
  call sites; three are unconditional because those handlers are **statically**
  two-word, and two of the three carry a shouting comment
  (`/* assign_obj has two opcodes! */`). **The buggy handler is the ONLY one
  whose instruction width is DATA-DEPENDENT** — which is why it needs a flag and
  why it is the one with the bug. ✅ **Both siblings checked for the same defect
  and both are clean, single-exit: F50/F58's census channel is run and EMPTY.**
* ⛔ **THE PRE-IMAGE SCREEN'S VERDICT IS WEAK AND MUST NOT BE QUOTED AS
  CONFIRMATION.** `--id CRASH-023` → `CANDIDATE`, `hits [[1769,
  "NEXT_OPCODE();"]]`, `1/1` — **and `NEXT_OPCODE();` occurs 115 times in that
  file.** ✅ The screen did its job (it is an *exclusion* tool, F68/item D11, and
  it correctly declines to exclude) but it confirms almost nothing here.
  ▶ **What replaces it: three offline legs that ARE decisive** — the hunk's own
  function-context line names `zend_binary_assign_op_helper`; `increment_opline`
  is local to that function alone; and the other exit already carries the
  identical guard at 5.0.0, so a patch adding it there would be a duplicate.
* ⚠ **The R1h (`4f68f3774c34`, 3 lines) does NOT apply to 5.0.0** — HEAD had
  diverged by 2004-08-30. **Hand-backport; `git apply` fails.**
* ⚠ **Name collision, recorded so nobody is misled:** `ph55-extern`,
  `ph56-mention`, `ph57-rust` in `_005`/`_006`/`_008` are **provenance-checker
  synthetics**, not catalogue rows.

---

## 4. WHAT TO DO ON `_047`'s LANDING — the merge checklist

1. **Act on `_047`'s coverage table first** — including removing anything from
   `.memory-php/` that it refuted under an `UNREVIEWED` banner.
2. **Merge §1 and §2 of this file into `RECAP_PHP.md`**: close items **91**,
   **98**, **103**; add §1.2's heterogeneity note to item **107**; **open a new
   item for `coverage.py`'s uninformative exit code.**
3. **Write `PROTOCOL_PHP.md`'s two owed sentences**: item 103 (the preflight
   file is expected to move and is in no digest) and item 98's policy (a).
4. **Repair `coverage.py`'s ratchet** (free, no digest).
5. **Update the START HERE box** and re-run `boxcheck.py` — **20/20**.
6. ⛔ **DELETE THIS FILE** and say so in the commit message.
7. **Then dispatch `_048`** (row 9), after re-reading its §2.6 against `_047`'s
   verdicts on F97/F104/F106.
