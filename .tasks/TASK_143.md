# TASK_143 — re-adjudicate six temporal rows on the C SIDE ONLY

**Role: research engineer.** ⚠⚠ **You are the only agent running.**

## The bar changed. Read it before anything else.

`.memory/02-bench-rules.md`, section **THE ADMISSION BAR IS C-SIDE ONLY**, and
`RECAP.md` finding **53**. `CLAUDE.md` rule **6** states it too.

> ⚠⚠⚠ **A PATTERN IS ADMITTED, OR NOT, SOLELY ON WHETHER THE C PROGRAM MAKES
> SENSE. NOTHING about Rust, Verus, Miri, a cost gradient, or what the ladder can
> "price" may EVER remove a row.**

**The four questions, and they are the whole bar:**

1. Is the **C kernel correct on benign inputs**, so performance is measurable?
2. Does it **exhibit the temporal error on at least one adversarial input** —
   detector firing, with a **positive control that must also fire**?
3. Is its **C MECHANISM** distinct from every built row's C mechanism?
   ⚠ Judged on **what the C code does**, never on *"the published result would
   look similar"*.
4. Does it fit the pinned kernel signature — flat blob in, `u64` out, shared
   driver loop? ✅ **`p27` proves a structure can live INSIDE the kernel driven by
   an opcode stream; `p27/unsafe.rs` holds 32 raw pointers.**

⚠⚠⚠ **THINGS YOU MAY NOT USE AS A KILL, ON PAIN OF REPEATING THE EXACT DEFECT
THIS TASK EXISTS TO REPAIR:** *"safe Rust can't express it"*, *"safe Rust
reproduces the bug bit-identically"*, *"there's no cost gradient"*, *"the R5
can't state the obligation"*, *"no column moves"*, *"Miri doesn't see it"*,
*"the bug is in-bounds so it's logical, not temporal"*. **Every one is a
FINDING. Several are the most interesting findings this project has.**

## The six rows, and the ground each was wrongly refused on

| row | the old kill | why it is void |
|---|---|---|
| **`p28`** intrusive doubly linked list | *"safe Rust's answer is an arena that never frees, or `p27`'s mechanism"* | pure RUST-side |
| **`p32`/`p33`** free-list allocator / object pool | *"safe slab == buggy C bit for bit"* + duplication | the first half is RUST-side and is **the result** |
| **`p34`** reference counting | *"no inversion — C's own refcount leaks identically"* | LADDER-side: a claim about the story, not the C program |
| **`p35`** tagged union | a trusted item owes a twin; a union read has no safe twin | pure VERUS-side |
| **`p25`** `realloc` growth | *"`realloc` never moves"* | ⚠ **a DRIVER heap-topology artefact, NOT a fact about C.** Regime C moves 9/12 |
| **the SEVEN temporal CVEs** | *"ported as a generational arena index, so the bug is LOGICAL, not temporal"* | a CLASSIFICATION — and **`p29` shipped that exact shape and four mechanisms split on it** |

**The CVEs:** `CVE-2024-25062`, `CVE-2016-4658`, `CVE-2022-23308`,
`CVE-2022-40304`, `CVE-2021-3518`, `Issue-15143`, `Issue-15192`
(`.tasks/TASK_123_REPORT.md` §B and its table rows 13–19).
⚠ **`TASK_123` spent NO MEASUREMENT on these — it says so in terms.** They were
closed on a citation. **Measure them.**

## Deliverables

1. **Per row: `ADMIT` / `REFUSE — C-side reason` / `DUPLICATE OF <row>, on the C
   mechanism`.** ⚠ **A refusal must name which of the four questions failed. If
   you cannot, it is an ADMIT.**
2. **For every `ADMIT`, a working C demonstration**: a kernel of the pinned
   shape, correct on a benign input, exhibiting the error on an adversarial one,
   with a detector firing and a positive control. ⚠ **This is the evidence a
   build task needs; it is not the build.**
3. ⚠⚠ **RANK the admits by how distinct their C mechanism is from `p27`'s and
   `p29`'s**, and say plainly how many rows you think this yields. **Do not
   trim the list to a comfortable number** — if five are admissible, say five.
4. ⚠ **Report what the Rust and Verus rungs look like for each admit** — as
   information for the build tasks, clearly labelled **NOT a criterion**.

⚠⚠ **DO NOT BUILD ANY PATTERN IN THIS TASK.** Verdicts and demonstrations only.
**Do not create `patterns/pNN-*/`.**

## Rules

- `.temp/t143/` only. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/`** — cited evidence.
- ⚠ **Do not run `harness/check.py` or `harness/measure.py`** — nothing here
  needs them and the tree is green; leave it that way.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; **every harm probe owes a positive control that must fire.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo` — and only for
  the *informational* Rust/Verus notes, never to decide admission.
- Keep the generator, delete the artefact (`.memory/00-environment.md`
  constraint 6).
- Report to `.tasks/TASK_143_REPORT.md`. **PROTOCOL rule 2: you carry 704.**
