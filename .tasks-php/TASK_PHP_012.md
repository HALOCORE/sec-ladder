# TASK_PHP_012 — adversarial review of `CATALOGUE.md`, and what we build first

**Role:** research **reviewer**. Adversarial by design.
**Under review:** `patterns-php/CATALOGUE.md` (91 rows), the **five new
reversals** and **three settled rows** in `TASK_PHP_011_REPORT.md`, and the
manager decisions in `RECAP_PHP.md` F21–F24.
**Report:** `.tasks-php/TASK_PHP_012_REPORT.md` — write the FILE.

> **A review that says "looks good" without having tried to break something is a
> failed review.** Rank `blocker` · `major` · `minor`, each with `file:line` and
> a concrete failure scenario. ⚠ **Do not pad.** ⚠ **Name your clean negatives.**

Read `.tasks/PROTOCOL.md`, then `patterns-php/CATALOGUE.md`,
`.tasks-php/TASK_PHP_011_REPORT.md`, `.tasks-php/ADJUDICATION_001.md`,
`PLAN_PHP.md` §3 §4 §6 §8, `.tasks-php/PROTOCOL_PHP.md`.

⚠⚠ **`RECAP_PHP.md` IS MANAGER-ONLY.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` is being edited by a CONCURRENT SESSION. Do not touch it, and do not
`git add -A` anything.**

**Bracket**: both staleness checks, first and last.

---

## §0 ⚠⚠ THIS TASK HAS TWO HALVES AND THE SECOND ONE MATTERS MORE

**Half one** is the review. **Half two is: name the rows we build first.**

⚠ **Eleven tasks, zero rows.** The catalogue exists to make that choice
defensible, and a review that only finds catalogue defects leaves the programme
exactly where it was. **Budget your effort accordingly** — I would rather have
a solid recommendation and six findings than twenty findings and no
recommendation.

## §1 The five reversals and the six "mechanism quality" admissions

`TASK_PHP_011` reversed five kills the **manager had upheld** (CRASH-097, 098,
133, 135, 147) and admitted **six** more that had been killed on *"mechanism
quality"*. **Both sets are unreviewed engineer work. Open them at source.**

⚠⚠ **And attack the "mechanism quality" reasoning specifically, because I think
it is the shakiest thing in the round and it is partly mine.** `PLAN_PHP.md`
§3's criterion for a kill includes *"is its **C mechanism** distinct from a built
row's?"* — **distinctness IS in the bar.** *"This is an ordinary null-deref"*
can mean two different things:

- **"mechanically identical to another row"** → that is distinctness, a
  legitimate **merge** (never a silent drop);
- **"uninteresting"** → that is **not** in the bar and is a kill the bar forbids.

**Which did the six get?** If several of them are the same C mechanism as each
other, the catalogue has traded six kills for six near-duplicate rows and should
have merged them. ⚠ **`CRASH-061, 082, 088, 126, 163, 021` — say for each
whether its mechanism is distinct from the other five, with the source.**

## §2 The catalogue itself

1. ⚠ **Part C is the half that matters** — the adjudication exists because the
   mining wave's kill list is where the defects were, and **F21 says the
   manager repeated the error one level up** by never re-opening its own upheld
   kills. **Now do it to Part C.** Every remaining kill: does its criterion
   re-derive at source? ⚠ **You are the third pass over this list and the first
   two each found rows in it.**
2. **F22's lesson, applied:** *a kill written as a set hides its members.*
   **Is any remaining Part C entry a set?** If one sentence covers N rows,
   enumerate the N **against `index.csv`**, not against the prose.
3. **Spot-check citations independently.** `TASK_PHP_011` reports 222/222
   resolving; that is **self-verification**. Take a random sample plus every
   row you intend to recommend in §3, and resolve them against the **pinned
   tarball** yourself.
4. **The three settled rows** — `ph09`/CRASH-033, `ph15`/CRASH-096
   (`zend_memnstr`'s `end -= needle_len`, a **third** answer after two agents
   gave two others) and CRASH-053. ⚠ **`ph15` especially: two prior readings
   were wrong, so a third being right is not the way to bet.**
5. **Duplication within the 91.** §3.1 admits slight variations deliberately,
   but ⚠ **`ph03` and `ph07`, `ph16` and `ph17`, `ph19`–`ph22`** read close
   from Part A alone. **Is any pair actually one kernel with two triggers?**
   Two rows for one kernel **double-count a ladder cost that is paid once**.

## §3 ⚠⚠ HALF TWO — the build order, and this is what I most want

**Recommend, with reasons from the catalogue and the source:**

**(a) THE SINGLE FIRST ROW.** It shakes out the whole pipeline on a *real PHP
kernel* for the first time — extraction, the provenance block, `kernel_hardened.c`
against the real `fix_commit`, all five rungs, the gate, the measurement.
⚠ **Optimise for DERISKING, not for interest.** The criteria I would use, and
you should argue with:
`verbatim` · no allocator · no cursor · `crashes_pristine_5_0_0 = True` · a
one-line reproducer · an `echoes` PAT row so there is something to compare
against · and a `u64` checksum that is obviously right.

⚠ **My prior, so you can attack it rather than guess it: `ph11`**
(*one-sided compare on a signed index, no lower bound*, `verbatim`, `I1/O1`,
CRASH-145, echoes `p02`). The spatial miner called it *"the smallest possible
spatial defect, and the only candidate with no arithmetic, no cursor and no
allocation"*. ⚠ **Its stated risk is that at `-O2` the compiler may hoist or
vectorise the whole loop and a bounds check may be free** — which is a finding,
but a poor property for the row that is supposed to prove the pipeline
*measures* anything. **If that risk is real, say so and name a better first
row.**

**(b) THE FIRST BATCH — about six rows, spatial**, per `PLAN_PHP.md` §8's
spatial → type → temporal order. Choose to **span mechanisms, not to rank
them**: at least one pointer-cursor row (`DP-07` — the idiom census found it in
all 22 corpus programs and **zero** of the 33 PAT kernels), at least one
allocator-dependent row (it is the first real exercise of the shim), at least
one `narrowed` row (the first real test of the extraction tiers and of
`provenance.py`'s overlap report).

**(c) What you would NOT build early, and why.** ⚠ **Name the rows whose cost
or risk you think the catalogue understates** — that is worth as much as the
picks.

## §4 Rules

- **No `git add` / `git commit`.** Read-only git is fine.
- Scratch under `.temp/php12/`. **Never `/tmp`.** ⚠ `.temp/php4–11/` hold
  earlier generators — `.temp/php11/pristine.py` is a manifest-checked tarball
  reader; **reuse it, do not rewrite it.**
- ⚠ **Citations resolve against the PINNED TARBALL only** (`SOURCES.md`), never
  a build tree.
- `timeout <N> <cmd>`. ⚠ **No `pkill`/`killall`** — exact PID via
  `/proc/<pid>/cmdline`.
- Everything claimed must have been **RUN**, output pasted.

## §5 The calls I am least sure of

1. ⚠⚠ **That "mechanism quality is not in the bar" is right** (§1). I wrote the
   opposite into `ADJUDICATION_001.md` §3b — *"a mechanism-quality judgement on
   the C, which the bar permits"* — and the engineer reversed it. **One of us is
   wrong and it changes six rows.**
2. ⚠ **That 91 rows is the right size**, and that Part B's 150-word blocks are
   read rather than skipped. The measurement says it is 3.3× denser per row than
   `.memory/06-catalogue.md`, which works — **but denser than a thing that works
   is not the same as readable.**
3. ⚠ **`ph11` as the first row** (§3a), for the reason given there.

---

**Running count: launched from 45.** `TASK_PHP_011` refuted **fourteen** things,
most against the manager — ⚠ **including the shape of the manager's own audit:
it re-examined the kills it suspected and never re-opened the ones it had
upheld, and five of those reverse at source.** It also found that **a kill
written as a set hides its members** (`CRASH-124/127/128` fell to the same
sentence as the adjudication's headline reversal, and nobody asked), and it
found **three citation defects inside the adjudication**, one of them in the
five-line exhibit arguing that a kill had priced the wrong frame.
**Reconciliation is the manager's job** — state what you refute and let the
manager carry it.
