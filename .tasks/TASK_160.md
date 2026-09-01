# TASK_160 — re-adjudicate the two admitted CVEs against the 32-row tree, BY RUNNING THEM

**Role: research engineer.** ⚠⚠ **You are the only agent running.**

⚠⚠⚠ **THE HEADLINE FACT, AND IT DECIDES THE SHAPE OF THIS TASK: NEITHER CVE HAS
EVER BEEN RUN BY THIS PROJECT.** `TASK_143_REPORT.md` says so in terms —
*"`CVE-2021-3518`, `CVE-2022-40304`: **Not touched.** The corpus ships `rust/`
and `rust-formal2/` with `cargo verus` proofs, which this project cannot
reproduce… **an unrun risk, not a measured one.**"* **Both admissions rest on a
CODE READING.** ⚠ **`RECAP.md`'s standing rule is the opposite: RUN A ROW'S C
DEMONSTRATION BEFORE WRITING THE ROW.** ✅ **So deliverable 1 is to run them.**

Read first: `.tasks/TASK_143_REPORT.md` lines ~440–490 (the admissions and the
ranking); `CLAUDE.md` **rule 6**; `.memory/02-bench-rules.md`'s *THE ADMISSION
BAR IS C-SIDE ONLY*; `RECAP.md` findings **53–54** (why the bar changed) and
**56, 59, 60** (the three rows these two must now be distinct from);
`.memory/06-catalogue.md` — ⚠ **note the CVEs have NO catalogue row; the task
reports are the only source, which is itself worth reporting.**

## ⚠⚠⚠ THE BAR, AND IT IS THE WHOLE OF IT

**A CVE is admitted SOLELY on its C program**: correct on benign inputs (so
performance is measurable), exhibits the target error on an adversarial input
with a **detector firing and a positive control firing**, its **C MECHANISM
distinct from a BUILT row's**, and it fits the pinned kernel signature.

> ⚠⚠⚠ **NOTHING about Rust, Verus, Miri, a cost gradient, or what the ladder can
> "price" may EVER refuse a row. *"Safe Rust can't express it"*, *"safe Rust
> reproduces it bit-identically"*, *"the R5 can't state the obligation"*, *"no
> column moves"*, *"Miri doesn't see it"* are ALL FINDINGS.**
> ✅ **C-SIDE DUPLICATION OF A BUILT ROW IS THE ONLY LEGITIMATE KILL.**

⚠ **This bias has produced real refusals before — six of ten temporal ones — and
it went uncaught for many sessions because it lived IN THE BAR rather than in any
row.** ⚠⚠ **The ports ship `rust/` and `rust-formal2/` with `cargo verus`
proofs this project CANNOT reproduce (single-file mode only, never `--cargo`).
That is a note about what cannot be INHERITED, NOT a reason to refuse.**

## What exists — and it is ANOTHER PROJECT'S REPOSITORY, READ ONLY

`../LearnVeri/microbench/CVE-2021-3518/` and `../LearnVeri/microbench/CVE-2022-40304/`,
each with `lib.c`, `io.c`, `server.c`, `Makefile`, `exploit.py`, `normal.py`,
`UB_confirm.py`, `root-cause.md` (and `CVE-2022-40304/orig-detailed-chain.md`).
⚠⚠ **COPY INTO `.temp/t160/`; DO NOT WRITE ANYTHING UNDER `../LearnVeri/`.**

## ⚠⚠ THE TWO DUPLICATION RISKS, AND BOTH GREW SINCE THE ADMISSION

Both were ranked when `p28`, `p32`, `p34` and `p25` were **candidates**. **All
four are now BUILT ROWS.** That is the entire reason this re-adjudication is
owed, and each CVE has one sharp exposure:

1. ⚠⚠⚠ **`CVE-2021-3518` vs `p28` — THE SHARPEST.** It was admitted as *"same
   family as `p28` (incomplete destroy → heap-resident dangling link),
   **distinguished by ONE sharp property: the guard IS the UB**, so the check
   cannot be written at the point of use."* `xmlFreeDtd` frees the entity
   declarations, entity-ref nodes keep their `children` pointers, and the
   traversal's own guard `(cur->children->type != XML_ENTITY_DECL)`
   **dereferences the dangling pointer**. **It was ranked LAST of seven.**
   ⚠ **A whole admission resting on one fine property, against a row that is now
   BUILT. Attack it: is "the guard is the UB" a different C MECHANISM, or the
   same mechanism with the check in a different place?** ⚠ **`p34` is the other
   comparison to make — its repair site is also not at the point of use.**
2. ⚠⚠⚠ **`CVE-2022-40304` vs `p32` — AND `TASK_143` SAID SO ITSELF.** Its
   ranking note reads *"its harm chain **lands on `p32`'s ground**, which is why
   it ranks below it."* Entity content under 5 bytes is **interned** in a shared
   dict; the cycle-breaker zeroes `ent->content[0]` **in place**, corrupting the
   dict's hash key while `okey` still holds the old hash; the entry is lost,
   **freed twice, duplicated on the free list, and two owners alias.**
   ⚠⚠ **`p32`'s SHIPPED HARM IS "two live handles naming one block" and its
   structure IS a free list. Read `CAVEATS["p32"]` and `patterns/p32-free-list-pool/`
   before deciding.** ✅ **The stated distinction is that the alias comes from
   **DEDUPLICATION** and the corruption is of a **hash KEY**, not a lifetime
   tag — `p32`'s is a generation counter. **Is that a distinct C mechanism or a
   distinct vocabulary?**
   ⚠ **Also compare against `p34`** (double release driving a count to zero
   twice) — it did not exist when this was ranked.

## ⚠⚠ THE SIGNATURE QUESTION, WHICH IS PART OF THE BAR AND NOT AN ASIDE

Both ports are **server-shaped** (`server.c` + `io.c`), and this tree's kernels
are `kernel(buf: &[u8], off: usize, len: usize) -> u64`, driven by a pinned loop.
**Ask, and answer with a reduction rather than an opinion: does a kernel-shaped
reduction PRESERVE the mechanism, or does reducing it turn it into a different
program?** ⚠ **If reducing `CVE-2022-40304` to a kernel loses the shared dict,
it loses the deduplication — and the deduplication IS the stated distinction.**
✅ **Say which, and show the reduction you tried.**

## Deliverables

1. ⚠⚠⚠ **RUN BOTH, and this is the deliverable the admissions never had.**
   For each CVE: build the C, run the benign path (`normal.py`) and the
   adversarial path (`exploit.py`), and record **per (arm × input × build)**:
   the answer, whether it is reproducible (`n` distinct in 20 runs), and what
   each detector says. ⚠⚠ **RUN THE DETECTOR ON EVERY ARM INCLUDING THE FIXED
   ONE** — `p28d` SEGVed on a benign input in the hardened arm because its
   verification only ever ran the buggy one. ⚠ **Every harm probe owes a
   POSITIVE CONTROL that must fire, IN THE DETECTOR WHOSE COLUMN IT LICENSES**
   — an ASan-shaped control cannot license a UBSan column (`p35`, and the same
   gap was found again in `p25`'s demonstration).
   ⚠ Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate with `head`**.
2. **Name each CVE's SAFETY LINE** — the one thing the buggy C omits or
   misorders that the fixed C has — and **count it in preprocessed lines**, the
   way `difflines.sh` does in `.temp/mgr149/` and `.temp/mgr155/`. ⚠ **If there
   is no single safety line, that is a finding and it must be said plainly**;
   `p28`'s is a nine-line splice and `p35`'s is a reordering, so "not one line"
   does not refuse anything.
3. ⚠⚠ **A VERDICT PER CVE, and only two are available: `BUILD` or `REFUSE ON
   C-SIDE DUPLICATION OF <built row>`.** For `BUILD`: name the C mechanism and
   **show** it distinct from `p27 p28 p29 p32 p34 p25` — the six temporal rows —
   and from `p08` (aliasing). For `REFUSE`: name the built row and the shared
   mechanism, and **quote the C from both**. ⚠⚠ **A verdict of *"refuse because
   the ladder can't price it"* or any Rust/Verus-side reason is FORBIDDEN and is
   the specific failure this bar exists to prevent.**
4. ⚠ **State the reproducibility and the environment honestly.** `p29` ships
   with 20 distinct values in 20 runs and is gated on an invariant; a
   non-reproducible adversarial answer **does not refuse a row**, it changes what
   can be pinned.
5. ⚠ **Report what a build would OWE if the verdict is `BUILD`** — in
   particular stage **`7h`** (the hardened arm must be sanitizer-CLEAN on EVERY
   input, and it cannot be declared away) and a **`verus.assumptions`**
   declaration if any rung would use `assume(`/`admit(`.
6. ⚠ **Report the process gap**: these two have **no `.memory/06-catalogue.md`
   row**, so their entire status lives in task reports the project's own rules
   say not to trust over the catalogue. **Propose the cells; do not write them.**

## Rules

- `.temp/t160/` for scratch. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/`, `synthesis/`, or `patterns/`.**
  No `git add`/`git commit`.
- ⚠⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.** Copy in;
  never write out.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
- ⚠ **Do not run `harness/check.py` or `harness/measure.py`.** Nothing here is
  a pattern yet, and the tree is green — leave it that way.
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING.** A waiter's own command line
  contains the string it greps for, so its exit condition can never be true;
  `TASK_157` left five polling forever. **Use `wait <pid>` or a `.done`
  sentinel** (`.memory/00-environment.md` has the entry and a reproduction).
- ⚠ **`rc=$?` after a PIPE reads the LAST command's status, not the script's.**
- **Keep the generator, delete the artefact** ⚠ **and a generator that edits
  source by string substitution MUST ASSERT ITS SUBSTITUTION COUNT** — `p28d`
  shipped an uninitialised pointer because a `str.replace()` silently matched
  nothing.
- Report to `.tasks/TASK_160_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 911**
(`.tasks/TASK_159_REPORT.md`: 906 + 5). Carry it forward in your closing
paragraph. ⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **The manager has been refuted in each of the last five tasks, three times
inside one derivation. The call to attack here is the manager's reading that
`CVE-2022-40304` is the likelier REFUSAL of the two — say so if the measurement
disagrees.**
