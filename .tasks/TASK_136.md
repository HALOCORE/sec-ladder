# TASK_136 — `p29`: settle the degree split, then build it if and only if it settles

**Role: research engineer.** ⚠⚠ **You are the ONLY agent running.** You may use
`harness/check.py` and `harness/measure.py`. Nothing else is touching the gate
records.

`p29` is **the only live row in this project.** Every other non-spatial candidate
is dead (`TASK_134`, finding 48) and the catalogue is otherwise closed.

Read first: `RECAP.md` findings **48 and 49** and the START HERE box;
`.tasks/PROTOCOL.md`; `.tasks/TASK_133_REPORT.md` §3a–3c (the measurements this
task builds on) and `.tasks/TASK_095_REPORT.md` (the verified BST artefact);
`.memory/02-bench-rules.md` **last section** (the priority, the bar's fourth
limb, and the temporal-R5 attack-arm rule); `.memory/06-catalogue.md`'s `p29`
cell; `patterns/p01-array-sum/` as the template and
`patterns/p27-handle-table/` as the only other temporal row.

## Deliverable 1 — THE DEGREE SPLIT. Do this before anything else.

⚠⚠⚠ **THE R1/R1h CONVENTION EVERY PATTERN USES SILENTLY FAILS ON `p29`, AND A
GREEN GATE WOULD NOT CATCH IT.** Every pattern here ships `c/kernel.c` and
`c/kernel_hardened.c` differing by **exactly one conjunct** — *"R1 omits exactly
this and nothing else"*. ⚠ **`TASK_133` measured that the obvious conjunct,
`if (t == g_saved) g_saved = NULL;`, FIXES 3 OF 5 INPUTS AND REPRODUCES THE
BUGGY CHECKSUM ON THE OTHER 2.**

**The mechanism, measured, from `TASK_133` §3b** — fixed tree `10/5/20/15/25`,
five inputs differing only in which key is removed, same binary, same source
line `acc = acc*31 + saved->val`:

```
victim  children  rc  ASan   kind                  buggy checksum   hardened checksum
    10         2   0     0   use-after-RECYCLE       8684676078980       8684676083620
     5         0   1     2   heap-use-after-free    (aborted)            8684676083620
    20         2   0     0   use-after-RECYCLE       8684676081220       8684676083620
    15         0   1     2   heap-use-after-free    (aborted)            8684676083620
    25         0   1     2   heap-use-after-free    (aborted)            8684676083620
```

**Two bug classes out of ONE line, selected by attacker data.** A two-child
victim is **never freed** — the in-order-successor splice **overwrites it in
place** and frees the *successor* — so `saved` points into a **live** allocation
whose **occupant has changed**. ASan cannot see it; only the checksum can.

> ⚠⚠ **THE QUESTION: is there a single conjunct whose omission produces ALL of
> this, and whose presence fixes ALL FIVE inputs?** Find it and the row is
> buildable on the normal convention. **If there is not, DO NOT INVENT A
> TWO-LINE R1h TO MAKE THE ROW HAPPEN.**

⚠ **`p27` solves its analogue with a `live[]` array and its safety line is
`&& live[h] == 1` on the READ path. Ask what `p29`'s analogue is** — the
property needed is not *"the node is still allocated"* but *"the node still
holds the value `saved` was taken from"*, and those differ exactly on the
two-child case.

⚠⚠ **IF THE SPLIT DOES NOT SETTLE, STOP AND REPORT. That is a real result — *the
R1/R1h convention has a boundary, and it is at inputs that select between bug
classes* — and it is worth more than a forced build.** Say so plainly; do not
spend the rest of the budget building something the convention cannot express.

## Deliverable 2 — build `p29`, ONLY if deliverable 1 settles

Clone `patterns/p01-array-sum/`'s structure. Seven rungs, `spec.md` with the
machine-readable `slb-contract` pins, an independent `model.py`, `inputs/gen.py`,
`NOTES.md`, `controls/`. **`harness/check.py p29` must pass.**

⚠⚠ **THE R5 OWES AN ATTACK ARM THAT MUST FAIL TO VERIFY, NOT JUST A DELETION
ARM** (`.memory/02-bench-rules.md`). **`p42`'s ghost ledger verified `18/0`
while leaking**; a temporal R5 that appears to state its obligation and does not
is the failure mode this rule exists for. ✅ **You start from a real artefact**:
`.tasks/TASK_095_REPORT.md` embeds a fully verified BST — recursive `Box<Tree>`,
three-case `remove` with in-order successor, `ensures res.bst() && res.keys() =~=
self.keys().remove(key)`, **`9 verified, 0 errors`, TCB 0**, re-verified at
`TASK_133` with a new mutant M5 that fails.

⚠ **`p29`'s row property is limb 4 clause 3 — *the safe rung is SILENTLY
WRONG*** — **not a cost gradient.** `.memory/02-bench-rules.md` settled in
advance that such a row ships. **Do not manufacture a performance headline.**
⚠⚠ **AND SEARCH BOTH RUNGS' SPELLINGS BEFORE PUBLISHING ANY DIFFERENCE** —
five patterns have published a headline that was wrong in the flattering
direction, and `p36` fell into the mirror image by searching R4 and leaving R3
with one lever. **Count the levers on each side and say whether they are
comparable.**

## What is already known — do not re-derive it

- **All five structures are expressible** under the pinned kernel shape.
  `dloop.py:361` constrains **declarations, not arity**.
- ✅ *"The shipped kernel cannot host a pointer"* is **false**:
  `patterns/p27-handle-table/unsafe.rs:156` is `[*mut u8; TABCAP]`.
  **A file cannot name a pointer, but it can name an operation that saves one.**
- **Three safe spellings were already searched**: `Option<Box<Node>>` + saved
  `&Node` → `2 error[E0502]`; index arena and `Rc<RefCell>` → both compile, both
  **bit-identical to buggy C** on the ASan-silent inputs and **silently wrong**
  where C aborts.
- ⚠ **The borrow checker is an ALIASING mechanism, not a temporal one** (finding
  48). **Do not pitch any rung on *"safe Rust cannot express the bug"*** — that
  claim has now been refuted three times in this project.

## Rules

- `.temp/t136/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- ⚠ Grep `~/tools/verus/vstd/std_specs/` **specifically** before claiming no spec
  exists.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; every harm probe owes a **positive control that must fire**.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.**
- ⚠ **Adding a pattern changes what `harness/tools/composition.py` derives.**
  Do not edit that file; tell the manager the bug class and the manager
  classifies it.
- Report to `.tasks/TASK_136_REPORT.md`. **PROTOCOL rule 2: you carry 645** —
  the manager reconciled three concurrent branches (634 base; `TASK_133` +9,
  `TASK_134` +4, `TASK_135` +11, overlapping, reconciled to 645). Close with
  your branch delta and the sum.
