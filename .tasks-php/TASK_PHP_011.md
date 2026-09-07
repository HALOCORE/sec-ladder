# TASK_PHP_011 — build `patterns-php/CATALOGUE.md`, and attack the adjudication behind it

**Role:** research engineer. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_011_REPORT.md` — write the FILE.

Read `.tasks/PROTOCOL.md`, then `PLAN_PHP.md` §3 §4 §6 §8,
`.tasks-php/PROTOCOL_PHP.md`, **`.tasks-php/ADJUDICATION_001.md`** (the manager's
adjudication of the mining wave — your primary input), and the three
`.tasks-php/TASK_PHP_001_REPORT_*.md` with their evidence under
`.tasks-php/TASK_PHP_001_MINE/`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY.** Everything goes in your report.
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**

**Bracket**: `python3 harness/measure.py --check-stale` → `66 record(s)
examined, 0 STALE`, first and last command, both pasted. Also
`python3 harness-php/gate.py --tool measure --check-stale` → `2 record(s)`.

---

## §1 What you are building

**`patterns-php/CATALOGUE.md` — the complete, honest account of what the PHP
5.0.0 corpus offers this programme.** It is the artefact that makes the choice of
what to *build* visible and defensible. It is **not** a build order.

⚠⚠ **SIZE IS A DESIGN CONSTRAINT, NOT A PREFERENCE.** `.web/CLAUDE.md` records
that the costliest defect in this project's reporting is *"a document that is
correct, fully qualified and unreadable"*, and `RECAP_PAT.md` reached 560 KB and
stopped being read. **The format below is mandatory and is what keeps ~80 rows
legible.**

### The format

**Part A — one table, every row, sortable, ONE LINE EACH.** Columns exactly:

`| id | axis | mechanism (≤ 12 words) | tier | inv/obl | corpus rows | echoes | status |`

- `id` — `ph01`… assigned **in catalogue order**, which is *axis then mechanism
  family*, not rank. ⚠ Do **not** reuse the miners' rank numbers as ids.
- `axis` — `spatial` / `type` / `temporal`. ⚠ **Some rows move** — the
  adjudication reassigns CRASH-158, CRASH-123 and CRASH-056. Apply it.
- `status` — `catalogued` (default) · `unresolved` (you could not settle it) ·
  `killed` (with a C-side criterion, see §3).
- `echoes` — the `pNN` PAT row with the same mechanism, **as a cross-reference,
  never a filter** (`PLAN_PHP.md` §3.1).

**Part B — one block per row, HARD CAP 150 words**, in table order:
the pristine citation(s), the mechanism in 2–3 sentences, the adversarial
trigger, the benign behaviour and its `u64`, the blob shape, and the **one risk
most likely to make an extraction wrong**. Anything longer goes in the row's
future `NOTES.md`, not here.

**Part C — the kill list.** Every corpus row not catalogued, with the criterion
(1, 2, 3 or 4 from `PLAN_PHP.md` §3) it fails and one sentence of evidence.
⚠ **This part is as important as Part A** — the adjudication exists because the
mining wave's kill list is where the defects were.

## §2 The work, in order

1. ⚠⚠ **Verify every citation you catalogue against the pristine tarball**
   (sha256 `5783e0c0…d6919`, read recipe in `patterns-php/SOURCES.md`) — **never
   against a build tree**. This is the bulk of the task. Report the count checked
   and every discrepancy. `RECAP_PHP.md` F2: the CSV is authoritative, the
   reproducer `.php` comment is **not**.
2. **Settle the three the adjudication could not**: CRASH-033 (the manager could
   not see the OOB from `zend_object_handlers.c:199-201`), CRASH-053 (the real
   defect is inside `make_real_object`, not at `:1632`), CRASH-096 (does the
   harmful step survive as a pure computation over a blob, or does it die on
   criterion 3 like CRASH-097/098?).
3. **Apply the adjudication's splits and merges** (§2 item 6, §4 of that file)
   and say if any is wrong.
4. **Assign `tier` per `PLAN_PHP.md` §4** — `verbatim` / `narrowed` / `modelled`.
   ⚠ **Tier is a cost statement, never a filter.** The adjudication's whole
   finding is that this distinction was lost once already.
5. **Fill Part C**, re-deriving the criterion for every kill.

## §3 ⚠⚠⚠ THE BAR, AND THE MISTAKE THAT HAS ALREADY BEEN MADE ONCE

**Admission is decided SOLELY on the C program** (`PLAN_PHP.md` §3): correct on
benign input, exhibits the error on an adversarial one, fits the kernel shape,
and `kernel_hardened.c` differs by the real fix.

⚠ **Nothing about Rust, Verus, Miri or cost gradients may kill a row.** The three
miners all honoured this and said so.

⚠⚠ **BUT THE WAVE STILL LOST ~17 ROWS, AND THE ADJUDICATION FOUND OUT HOW:
EXTRACTION COST WAS WRITTEN AS A CRITERION-3 FAILURE.** Criterion 3 is about the
**kernel shape** — flat blob in, `u64` out. It is *not* about how much C you must
carry; that is the **tier**. *"The surrounding machinery is the program"*,
*"mutually recursive over a 4000-line file"*, *"the blob would have to encode a
backtrace"* are **tier assignments wearing a kill's clothes**. Twelve were opened
at source and every one refuted its own kill — two of them are **five lines**.

**So: before you write any kill into Part C, open the defect in the tarball and
ask whether a faithful kernel of THE DEFECT needs the machinery you are about to
cite.** ⚠ Price the cost at the **defect site**, not at the frame the defect
flows into — that is `RECAP_PHP.md` F1 with cost substituted for citation.

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php6/`. **Never `/tmp`.** Keep the generator, delete the
  artefact; anything the catalogue cites is evidence and stays.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — confirm an exact PID via
  `/proc/<pid>/cmdline`.
- **Everything you claim must have been RUN**, output pasted. A citation you did
  not open is a citation you did not check — say which those are.
- **Do not widen scope**: no kernels, no `spec.md`, no gates. This task ends at
  the catalogue.

## §5 The calls I am least sure of — please refute them

`PROTOCOL.md` rule 2. **Every agent that has contradicted the manager with a
measurement has been right**, on both programmes.

1. ⚠⚠ **The whole §3 finding is the manager auditing how three agents applied a
   bar the manager wrote.** If *"criterion 3"* vs *"tier"* is not as crisp as the
   adjudication makes it, **~17 reversals are wrong and the catalogue is inflated
   by a fifth.** Attack this first, with source, not argument.
2. ⚠ **`≈80` rows may be the wrong size for a readable catalogue.** If Part B at
   150 words × 80 is unreadable, **say so and propose the format that works** —
   that judgement is worth more than compliance.
3. ⚠ **The rank-12 KEEP and the #4/#13 MERGE are the manager overruling a
   miner's own recommendation**, in both directions, and the manager read neither
   set of sites in full.
4. ⚠ **The CRASH-158 → type reassignment invents a third answer** where two
   agents gave two. It rests on a pairing with `sp#10` that the manager reasoned
   from two candidate descriptions and **did not measure**.

---

**Running count: launched from 31.** ⚠ **The mining wave's three agents each
refuted the manager claim they were named to attack, and the adjudication then
found ~17 rows their own honest reject tables had lost.** Both facts are the same
rigour signal: the wave documented its kills well enough that the audit was
possible at all. **Reconciliation is the manager's job** — state what you refute
and let the manager carry it.

---

## §6 ADDENDUM — what the adjudication learned AFTER this task was drafted

`ADJUDICATION_001.md` §7a/§7b settled its last two unresolved rows, and the way
they settled changes an instruction above.

### ⚠⚠ Three different frames, and the provenance block must name the right one

**For a given row the DEFECT site, the GUARD site and the FAULTING site can be
three different places, and the corpus's own fields point at different ones.**

| row | corpus points at | the defect actually is |
|---|---|---|
| CRASH-033 | `zend_object_handlers.c:199-201` (*"missing guard"*) | `zend_compile.c:2611-2622` — `zend_unmangle_property_name`, 12 lines |
| CRASH-053 | `zend_execute.c:1632` (*"unchecked `make_real_object`"*) | ⚠ **that label is wrong twice**: `:1635` *does* check, and `make_real_object` is correct. `object_ptr` was never valid |
| CRASH-002 | `array.c:1062` (the faulting frame) | `zend_hash.h:88` (F1) |

**Rule for this task: `provenance.c_file` / `c_lines` name the DEFECT site.**
The guard site and the faulting site go in the row's notes, labelled. ⚠ **Where
the corpus's `root_cause_id` is wrong, say so in the catalogue** — two are
already known wrong and that is corpus-quality evidence worth keeping.

### ⚠ And pricing extraction cost has the same failure

**Four rows in the audit were killed by pricing the machinery of a frame
ADJACENT to the defect** (CRASH-136, CRASH-157, CRASH-033, CRASH-053).
`TASK_PHP_011` §3's instruction stands and this is the evidence for it:
**open the defect in the tarball before writing any kill.**

### Pairs the catalogue must not split

Found while settling the above; each is one kernel with two limbs, and two rows
would double-count a ladder cost that is paid once:

| pair | why |
|---|---|
| **CRASH-053 + CRASH-056** | the **same `temp_variable` union**: one call site invents a discriminant from a sibling member's NULL-ness, the other omits the test entirely. ⚠ Neither reached the type axis — 056 was routed to spatial, 053 killed on cost |
| **ty#4 + ty#13** | the same `HASH_OF` helper, misused in opposite directions |
| **sp#3 + sp#7** | one extracted kernel (`php_url_parse_ex`), two triggers |
| **CRASH-158 + sp#10** | *not* one kernel — but the **same C shape** producing different vulnerability classes depending on which of two numbers the storage was sized from. Cross-reference, do not merge |

### One more thing to check that nobody has

⚠ **`ADJUDICATION_001.md` is UNREVIEWED manager work and this task is its
review.** In particular §1's whole finding — that extraction cost was written as
a criterion-3 failure — rests on the manager's reading of three miners' reject
tables plus fourteen rows opened at source. **If the criterion-3-versus-tier
distinction does not hold up, ~17 reversals are wrong and the catalogue is
inflated by a fifth.** Attack that before cataloguing anything.


---

## §7 ⚠ FOLDED REVIEW — `TASK_PHP_010` is unreviewed, and you are its review

**Stated, not hidden.** `PROTOCOL.md` rule 1 alternates engineer → reviewer, and
`TASK_PHP_010` (four majors, six minors) has had no adversarial pass. Rather than
spend an eleventh infrastructure cycle on four mechanical fixes, **the manager
has folded that review into this task.** It is a compression and it may be the
wrong call — ⚠ **if you think these fixes need a review of their own, say so and
I will run one.**

**Verify these four, cheaply — the controls already exist and are named:**

| fix | must-fire | must-NOT-fire |
|---|---|---|
| M1 one row enumeration (`_row_dirs`) | `.temp/php9/a1_row_enum.py` case 3; `gate.py --preflight .ph93` → **rc=2** | all 33 PAT rows still admitted |
| M2 `ROW_DIRS = {c, inputs, controls}` | `.temp/php9/a2_upward_include.py` | ⚠ **all 33 PAT rows — every one carries `__pycache__/`, which the fix as first specified refused** |
| M3+M4 per-row coverage | `.temp/php9/a4_orphan_deadlock.py` | the bracket returns `rc=0` under a planted orphan |
| `MAX_RUNS` bounds evidence-carrying runs | `.temp/php10/` | — |

⚠⚠ **And one thing to attack rather than verify: `#include "../../shared/x.h"`
escapes the row entirely, compiles, runs the outside allocator, and is in NO
digest** (`RECAP_PHP.md` F20). It was reported and **deliberately not fixed** —
both repairs are worse than the risk. **Your job is to say whether any row in
this catalogue would plausibly want a shared directory.** If several would, the
manager's "latent, leave it" is wrong and needs to be scheduled now, before rows
are built around it. ⭐ **This is exactly the kind of question a catalogue can
answer and an infrastructure task cannot.**
