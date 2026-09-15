# TASK_PHP_054 — **SCREEN ROW 11**: read each empty family's OWN entry and OWN R1h

**Role:** research **investigator**. **THREE agents, in parallel, on DISJOINT
family sets.** Each writes **its own report file** (rule 10) and **never** edits
another agent's.

| agent | families | rows | report file |
|---|---|---|---|
| **A** | **E2 · E3 · E4** | ph65–ph76 (12) | `.tasks-php/TASK_PHP_054_REPORT_E2E3E4.md` |
| **B** | **E5 · E6 · E7 · E8** | ph77–ph91 (15) | `.tasks-php/TASK_PHP_054_REPORT_E5E6E7E8.md` |
| **C** | **S4 · S5 · S6 · T2 · T4 · T6** | ph32–ph38, ph47, ph48, ph54, ph59, ph60, ph96–ph102 (19) | `.tasks-php/TASK_PHP_054_REPORT_S4S5S6T2T4T6.md` |

⭐⭐⭐ **THE DELIVERABLE IS A RANKED SHORTLIST WITH EVIDENCE, NOT A DECISION.**
The manager picks row 11. **Your job is to make the pick CHECKABLE** — and to
make a *wrong* pick expensive to make, which is the thing that failed last time.

---

## §0 ⛔ WHY THIS TASK EXISTS — read this before anything else

⛔⛔ **ROW 9's FIRST PICK WAS WRONG, AND THE REASON IS THE WHOLE DESIGN OF THIS
TASK.** `RECAP_PHP.md` item **94**: the manager surveyed the then-14 empty
families and recommended **`ph32`** — **off ONE LINE of another row's `why`.**
Reading `ph32`'s **own catalogue entry** said the opposite about cost: **three
short tables**, not the one the corpus records, and an R1h of **FOUR COMMITS**,
one of them *invisibly incomplete* (`56adfe1f3cf1` rewrites the table to 65 and
leaves `/* 376 (0x0178)` unterminated **in the same hunk**, so it compiles to 41;
`bd07142b9128` then "fixes the `/*`-within-comment warning" by closing it
**after** the swallowed block — **silencing GCC while keeping the defect**).

▶ **THE RULE THIS TASK ENFORCES: read each candidate's OWN Part B entry and its
OWN R1h. A one-line summary of a row — including the one in this task file —
IS NOT EVIDENCE ABOUT THAT ROW.**

⚠ Item 94 also says, in terms: *"the §5.2 ranking of the other 12 families is
UNRELIABLE."* **That ranking is what you are replacing.**

### ⛔⛔⛔ AND THE ADMISSION BAR IS C-SIDE ONLY — `CLAUDE.md` "Don't" rule 6

**NEVER refuse or down-rank a candidate for a Rust-side, Verus-side or
ladder-side reason.** *"Safe Rust can't express it"*, *"safe Rust reproduces the
bug bit-identically"*, *"there's no cost gradient"*, *"the R5 can't state the
obligation"*, *"no column moves"*, *"Miri doesn't see it"* and *"the bug is
in-bounds so it's logical, not temporal"* are **ALL FINDINGS, NEVER KILLS.**
This bias shaped **six of ten** real temporal refusals and went uncaught for many
sessions **because it lived in the admission bar rather than in any single row.**

⚠⚠ **C-SIDE DUPLICATION IS *NOT* A KILL IN `patterns-php/`.** That corpus is
FRESH and stands on its own (`PLAN_PHP.md` §3, `CLAUDE.md` rule 6's last line).
**Do not down-rank a row because it resembles a built row or a `patterns/` row.**
If it does resemble one, **say so as a fact** — a near-twin is often the
*cheapest* row to build, because the harness shape is already proven.

**What decides admission, and it is only this:**
1. Is the C **correct on benign inputs**, so performance is measurable?
2. Does it **exhibit the target error on an adversarial input**?
3. Can the **C mechanism** be lifted into a kernel at a declarable tier?

**What this task adds on top is COST, not admission.** A row that passes 1–3 and
is expensive is **admissible and expensive** — rank it low, never kill it.

---

## §1 ⛔ READ FIRST, IN THIS ORDER

1. **`patterns-php/CATALOGUE.md` Part B, YOUR families' sections, EVERY ROW.**
   ~150 words each. This is the primary source and there is no substitute.
   ⚠ **Part A's table line is a POINTER, not the entry.**
2. `patterns-php/CATALOGUE.md` **§0.1–§0.4** — three frames per row; `tier` is a
   **COST STATEMENT, NEVER A FILTER**; `echoes`; the format deviation.
3. `.tasks-php/FIXSURVEY_001.md` — **the R1h survey, already run for the whole
   catalogue** (F40). ⚠⚠ **Read its "WHAT THIS ANSWERS AND WHAT IT DOES NOT" box:
   a `same` verdict is a STARTING POINT, NEVER A LICENCE.** F38 found **3 of 5
   hand-checked commits are LATER fixes**.
4. `.tasks-php/PROTOCOL_PHP.md` — **§A1** (tiers), **§A2a** (the oracle's domain
   is not the corpus), **§B** + **§B1a** (the allocator rule and its O(1)
   precondition), **§C** + its *"which `fix_commit` when a row's ids name
   several"* subsection, **§G** + **§G1** (duplication, and the upstream-fix
   asymmetry).
5. `RECAP_PHP.md` — the **START HERE** box, **item 94**, and findings
   **F38 · F46 · F49 · F50 · F58 · F64 · F68 · F95** (what a fix commit does and
   does not prove) and **F3** (`crashes_pristine_5_0_0 = False` is **not**
   evidence of absence).
6. **The two rows that prove the rubric**: `patterns-php/ph55-opdata-stride/NOTES.md`
   (cheap: no zvals, no allocator, no garbage determinism, no stack layout) and
   `RECAP_PHP.md` F105 + item 94's `ph52` notes (expensive: **silent on a clean
   stack**, so the harm depends on stack garbage).

---

## §2 ⭐ THE MECHANICAL PRE-SCREEN IS ALREADY DONE — CHECK IT, DO NOT REDO IT

The manager ran `fixsurvey.py --offline` on 2026-09-15. **Your families' R1h
one-id lines** (`row | id | sha | year | files | same-file? | subject`):

```
A (E2/E3/E4)
  ph65 CRASH-121 1ac4d8f2c632  2013 ⚠late  5f  same     shutdown segfault due to serialize
  ph66 LOGIC-001 b73349dbe4e9  2006       1f  same     wrong element deleted
  ph67 CRASH-160 c3a317117ad8  2014 ⚠late  1f  same     helper for updating bucket contents
  ph68 CRASH-030 d7b30e457a3d  2007       2f  same     uncaught exception from a stream wrapper
  ph69 CRASH-131 631da59b5032  2005       3f  same     preg_match_all named capturing groups
  ph70 CRASH-047 41ae8de13666  2006       3f  same     memory corruption, indirect
  ph71 CRASH-004 4f161fe28997  2005       3f  same     assigning array element by reference
  ph72 CRASH-074 37d7df72a62e  2012 ⚠late  3f  same     array_walk_recursive third param
  ph73 CRASH-052 3d7b0bab28e7  2005       5f  same     magic object handling alloc bugs
  ph74 CRASH-139 9a98904ddd0e  2006       4f  same     wrong "type" arg to read_property()
  ph75 CRASH-161 ed4c0245c7ca  2014 ⚠late  1f  same     partial fix, zend_mm_heap corrupted
  ph76 CRASH-012 1d33a3e95e4e  2005       5f  same     array_splice on $GLOBALS crashes

B (E5/E6/E7/E8)
  ph77 CRASH-151 f5f8cba8e978  2008       4f  same     indexed+reference assignment to props
  ph78 CRASH-042 41ad9b4d1fdd  2008       2f  same     invalid write changing property
  ph79 CRASH-038 6319efa013ec  2005       3f  same     segfault with callbacks (array_map)
  ph80 CRASH-084 336b5f59b6c4  2014 ⚠late  2f  same     putenv with empty variable
  ph81 CRASH-142 8df40bdb313d  2006       2f  same     consistent arg_stack during freeing
  ph82 LOGIC-002 625e06f454d6  2005       1f  ⚠OTHER   FE_RESET/FE_FETCH
  ph83 LOGIC-011 07b7ba8b4004  2011 ⚠late  8f  ⚠OTHER   ternary operator performance
  ph84 LOGIC-015 7628da98c481  2010 ⚠late  5f  same     removed break/continue $var syntax
  ph85 LOGIC-006 196e54fc43dd  2005       1f  same     plug leak of 1/2 bytes on convert
  ph86 CRASH-065 89e53d5ab231  2005       2f  same     passing array or non array of objects
  ph87 CRASH-068 1ea22c90046b  2004       1f  same     Zend constant warning uses memory after free
  ph88 CRASH-062 2e1a2438b5e6  2007       3f  ⚠OTHER   class declarations may not be nested
  ph89 CRASH-034 e0b0ae9ce7c5  2005       2f  ⚠OTHER   error handler, modifying 5th arg
  ph90 CRASH-029 32c2e664a6ec  2005       1f  ⚠OTHER   all incarnations of bug #30266
  ph91 CRASH-071 e8359d3f904c  2009       2f  same     exception thrown from ... ⚠ SEE §3.6

C (S4/S5/S6/T2/T4/T6)
  ph32 CRASH-089 bd2e99ee50ed  2005       1f  same     html_decode_entities  ⛔ SEE ITEM 94
  ph33 CRASH-128 b7259b71b430  2016 ⚠late  3f  same     mbc_to_code() out of bounds read
  ph34 CRASH-122 9daaedc12526  2005       2f  same     ctype corrupts memory
  ph35 CRASH-130 ae57857ebac7  2009       2f  same     >127 named subpatterns
  ph36 CRASH-005 (bison-regen)  —         —   ⚠⚠NO SHA
  ph37 CRASH-018 7d109bc62761  2006       1f  same     sscanf() reading past array
  ph38 CRASH-077 ff1687731dee  2005       2f  same     range('', 'z')
  ph47 CRASH-104 cd32b4e2bb54  2007       3f  same     substr_replace() same variable
  ph48 LOGIC-017 af05ce0af6d3  2008      17f  same     is_callable/call_user_func mess
  ph54 CRASH-143 fc96c7f7fa18  2005       5f  ⚠OTHER   foreach optimization
  ph59 CRASH-082 f046cdf3fa15  2005       3f  same     array_map() + exception
  ph60 CRASH-088 60fc9c050a44  2004       1f  same     opendir() with ftp:// wrapper segfault
  ph96–ph102: ⚠ NOT IN THE PER-ROW TABLE — it was built at 91 rows and these came
              in the 91→102 expansion. ▶ RUN `fixsurvey.py --offline` YOURSELF
              and report what it says for them; if it says nothing, SAY SO.
```

⚠⚠ **THESE ARE ONE-ID LINES AND 30 OF 102 ROWS CARRY IDS NAMING *DIFFERENT*
COMMITS.** In your sets that is at least **ph70 ph71 ph73 ph75 ph76 ph77 ph78
ph79 ph80 ph82**. ▶ **For any row you shortlist, run the full survey and report
`n ids → n distinct commits`. A row with 5 ids and 5 commits owes an R1h
DECISION before a build task, not inside one** (`PROTOCOL_PHP.md` §C).

⭐ **The manager's own reading of the above — REGISTERED SO YOU CAN REFUTE IT:**
the best R1h *shapes* in the empty families are **ph87 (2004/1f/same)**,
**ph60 (2004/1f/same)**, **ph85 (2005/1f/same)**, **ph66 (2006/1f/same)** and
**ph37 (2006/1f/same)** — the shape `ph55` scored best in the catalogue on.
⛔ **This is exactly the kind of one-line ranking that produced `ph32`. Treat it
as a HYPOTHESIS TO ATTACK, and attack it with the rows' own entries.**

---

## §3 ⭐⭐⭐ THE WORK

### 3.1 Stage 1 — EVERY row in your set, from its OWN Part B entry

One table row per candidate, these columns, **all sourced from the entry**:

| col | what |
|---|---|
| `row` | `phNN` |
| `tier` | `verbatim` / `narrowed` / `modelled` — **a cost statement, never a filter** (§0.2) |
| `defect site` | the `c_file_line` as the entry gives it |
| `harm` | crash / silent wrong answer / leak / UAF-read / UAF-write — **name it** |
| `needs` | ⭐ the cost column. Tick every one that applies: **zvals · the allocator · HashTable · the executor/VM · userland re-entry · stack garbage · a HASH PREIMAGE or other precomputation · failure injection · >1 subsystem** |
| `deterministic?` | does the harm reproduce without depending on uninitialised memory? **`ph52` was SILENT ON A CLEAN STACK and that is what made it dear** |
| `observable by` | checksum divergence / NULL deref / ASan / Miri / allocator ledger `(allocs,frees)` |
| `R1h` | year · files · same-file? · **ids→commits** |
| `entry's own ⚠ risk line` | **quote it** — the catalogue states the known trap per row and it is usually right |

⛔ **COUNT YOUR ROWS AND PRINT THE COUNT.** The manager's first extraction regex
silently dropped **5 of 102** rows (`ph92 ph27 ph35 ph54` among them) because
their titles contain markup it did not match — **F35's class, on this very
file, on 2026-09-15.** ▶ `grep -ac '^\*\*ph' <section>` and reconcile against
`python3 .tasks-php/quota.py`'s per-family `n`.

### 3.2 Stage 2 — DEEP VERIFICATION of the **top candidate in each of your families**

(One per family. If two are genuinely tied, do both and say why.)

**a) Every `file:line` in the entry, checked against the PRISTINE 5.0.0 C.**

```sh
T=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
sha256sum "$T"   # MUST be 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
tar -xzOf "$T" php-5.0.0/Zend/zend_hash.c > .temp/php54/zend_hash.c
```

⚠ **5.0.0 comes from the PINNED TARBALL, never from GitHub** (`SOURCES.md`).
▶ **Quote the actual line text you found at each cited line number**, not
"confirmed". A citation that is off by a line or two is common and benign; a
citation whose text says something else is a **finding**.

**b) ⚠⚠ THE `▸ trigger` LINE IS THE UNRELIABLE HALF — F46 measured it.**
`_020` found the mechanism sentences right and the `▸ trigger` lines wrong, and
F49's stop condition fired when **3 of 9** new rows' triggers failed.
▶ **For your top candidate, say whether the trigger is (i) verified to reach the
cited site by reading the C, (ii) plausible but unverified, or (iii) WRONG.**
**(ii) is an honest answer. Inventing (i) is not.**

**c) The R1h, read as bytes.**
```sh
python3 .tasks-php/fixsurvey.py --offline              # the full per-id survey
python3 .tasks-php/preimage_screen.py --row phNN --verbose
```
⚠ Network was reachable from this box on 2026-09-15 (`raw.githubusercontent.com`
and `github.com/php/php-src/commit/<sha>.patch` both returned **200**), and
**163 patches are already cached** under `.temp/mgr/batch/patches/`. ▶ **Prefer
the cache; if you fetch, say you fetched.**
⛔⛔ **`preimage_screen.py` has FOUR outcomes and only ONE is a proof.**
`NOT-THE-REPAIR` is the proof of exclusion; `INAPPLICABLE` and
`INAPPLICABLE-SAME-FILE` say **NOTHING** about the commit. **Do not cite an
`INAPPLICABLE-SAME-FILE` as an exclusion** — F68/F95, and `ph53` was
mis-published on exactly that confusion.
▶ **Read the patch and say what it actually changes**, in one sentence. Item
94's `ph32` disaster was a commit whose *shape* looked perfect.

**d) ⭐ Does the fix commit look like a CENSUS?** F50/F58: a fix commit patches
its defect's **siblings**, and a **named wrapper** carries signal while a
"≥5 files" selector does not. ▶ **If the patch touches >1 site in the defect's
file, list the sites.** That is free sibling evidence for the build task.

### 3.3 ⭐ The cost verdict — say it in these words

For each family, one of:

- **CHEAP** — lifts at `verbatim`/`narrowed`, needs ≤1 of the `needs` ticks,
  harm is deterministic and observable, R1h is 1–2 files/same-file/one commit.
- **MEDIUM** — admissible, but names a specific thing that will cost a task.
  **Name it.**
- **DEAR** — admissible, and here is the concrete reason it is dear.
- ⛔ **BLOCKED-ON-A-DECISION** — the row cannot be dispatched until the manager
  picks something (typically *which* R1h, when ids name several). **Say what the
  decision is.** This is not a kill.

⛔ **THERE IS NO "KILL" VERDICT IN THIS TASK.** If you believe a row fails the
C-side bar (§0), that is a **finding with evidence**, written as
*"criterion N fails because \<C evidence\>"* — and it must be about the **C**.

### 3.4 ⭐⭐ THE RANKING, AND THE THING THAT MAKES IT USEFUL

End with **your families ranked**, best first, and for **each** give the ONE
sentence a build-task author would need. ▶ **Then answer this explicitly: WHICH
ONE OF YOUR FAMILIES WOULD YOU ENTER FIRST, AND WHAT WOULD CHANGE YOUR MIND?**

### 3.5 ⭐ SCORE THE MANAGER'S THREE REGISTERED PREDICTIONS

Registered **before dispatch**, 2026-09-15, so they are falsifiable:

1. **P1 — at least ONE of the five top mechanical picks (ph87, ph60, ph85, ph66,
   ph37) fails deep verification**, on the `ph32` precedent. ▶ Score the ones in
   *your* set; the manager combines.
2. **P2 — row 11 is a TEMPORAL row** (an `E` family). Grounds: 3 of the 5 best
   shapes are temporal, and temporal is **1 of 10 built rows against 7 of 20
   families**. ▶ Agent **C**, you are the control: **if an `S`/`T` family beats
   them, say so loudly** — that refutes P2 and is worth more than agreeing.
3. **P3 — `▸ trigger` lines fail on roughly a third of rows deep-verified**
   (F46/F49's 3-of-9). ▶ Report **verified / plausible / wrong** per deep check
   so this can be counted.

### 3.6 ⚠ ONE ROW CARRIES A KNOWN UNRESOLVED LABEL — agent B

**`ph91` / CRASH-071** is marked in the catalogue as ***"UNRESOLVED, the corpus
label and its citation disagree"***. ▶ **Do not resolve it as a side quest.**
Report the disagreement precisely (what the label says, what the citation
points at) and mark the row **BLOCKED-ON-A-DECISION**.

---

## §4 ⛔ TRAPS

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps, and
   `CATALOGUE.md` wraps constantly. **Read sections, do not grep for verdicts.**
2. ⛔ **A one-line summary of a row is not evidence about that row** — §0. This
   includes **every one-line summary in THIS task file**.
3. ⛔ **`F3`: `crashes_pristine_5_0_0 = False` is NOT evidence of absence.** It
   records what one harness saw once.
4. ⚠⚠ **`tier` is a COST STATEMENT, NEVER A FILTER** (§0.2). `modelled` does not
   disqualify a row; it prices it.
5. ⛔ **No `/tmp` scratch — use `.temp/php54<A|B|C>/`**, one subdir per agent.
   **Keep the generator, delete the artefact**: extracted `.c` files are
   re-derivable from the tarball, so write the one-line `tar` command into your
   `NOTES.md` and delete the blobs when you finish. `.py`/`.md`/`.log` evidence
   stays.
6. ⛔ **No `git add` / `git commit` / any history-mutating git.** Read-only git
   is fine. ⚠⚠ **NO EDITS to `RECAP_PHP.md`, `.memory-php/`, `harness/`,
   `common/`, `patterns/`, `results/`, `pilot/`, `common-php/`, `.web/`,
   or `patterns-php/CATALOGUE.md`.** You **read** the catalogue; the manager
   writes it. **Write only your own report file and your own `.temp/` subdir.**
7. ⛔ **Never `pkill`/`killall`/substring-match a process.** Confirm the full
   command line of an exact PID. Prefer `timeout <N> <cmd>`.
8. ⚠ **A comment is not code**, and **a catalogue sentence is not the C.**
   Everything in §3.2 is checked against the tarball or it is not checked.
9. ⚠ **Do not run `harness/check.py` or any gate.** This task builds nothing.
10. ⚠ **Three agents are running.** Your report file is yours alone; do not read
    or wait on the others'. **The manager reconciles.**

---

## §5 DEFINITION OF DONE

1. **Stage 1 table complete for EVERY row in your set**, with the row count
   printed and reconciled against `quota.py`.
2. **Stage 2 deep verification for the top candidate in each of your families** —
   cited lines quoted from the pristine tarball, trigger classified
   verified/plausible/wrong, `preimage_screen.py` run and its outcome named with
   the right one of the four labels, `ids→commits` reported.
3. **A cost verdict per family** in §3.3's four words.
4. **Your families RANKED**, with the one sentence per family, and **an explicit
   answer to "which family first, and what would change your mind"**.
5. **The three predictions scored** for the rows in your scope.
6. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** Anything you could not
   verify goes here **named**, not omitted. ⚠ *"Plausible but unverified"* is a
   deliverable; a confident sentence you did not check is a defect.
7. ⭐⭐ **IF YOUR DEPTH RUNS OUT, STOP AND SAY EXACTLY WHERE.** `_051` did that
   and it cost the programme one task and nothing else. A truncated table with
   an honest boundary beats a complete one with invented cells.
8. **Anything that surprised you about the CATALOGUE ITSELF** — a wrong line
   number, a mis-filed family, a `▸ trigger` that cannot fire — goes in a
   section called **"catalogue defects found"**, even when it is not your row.
   That section has paid for itself on every task that had one.
