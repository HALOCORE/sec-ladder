# TASK_093_REVIEW — attack the `p28` refusal, and try to SAVE the row

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md` (**the reviewer checklist and the severity scale**),
then `.tasks/TASK_093.md` (the task), then `.tasks/TASK_093_REPORT.md` (**the
refusal you are attacking**), then `.memory/06-catalogue.md`'s `p28` and `p27`
rows, `.memory/03-measurement.md`'s probe-shape section, and
`patterns/p27-handle-table/NOTES.md` §0, §0a, §0b and §7a.

The engineer's evidence is in `.temp/t93/`; **`.temp/t93/build.sh` regenerates
every number.** `.temp/t91/`'s binaries are also still present and the engineer
explicitly did **not** re-run them.

Your scratch is **`.temp/r93/`** — free, I checked. ⚠ Do not write into
`.temp/t93/`, `.temp/t91/` or `.temp/p28/`.

---

## Your job, in one sentence

**A row was killed. Find the `p28` that survives, or establish that none does.**

The engineer's verdict is that every shape is `p27`'s use-after-free in a costume
or is not temporal at all, and that the cost ladder is structurally dishonest.
**That verdict removes a pattern from a catalogue whose remaining rows I have
just told the user are thin, so it needs to be right.**

⚠ **Refusal is a load-bearing outcome here, not a failure** — three previous
refusals were each the correct call. **But three of the four rows this project
refused were refused for reasons that turned out to be right; one (`p31`) was
right in its VERDICT and wrong in EVERY CLAUSE OF ITS REASON.** A refusal whose
reasoning is wrong is a landmine, because the reason is what gets written into
`.memory/` and reused on the next row.

---

## The four things I most want attacked

### A — the structural claim, which is the whole kill

> *"Safe Rust cannot express an intrusive doubly linked list with owned nodes"*
> — `E0382: use of moved value` + `E0499: cannot borrow as mutable more than
> once`, from `.temp/t93/rs/boxdll.rs` under `#![forbid(unsafe_code)]`.

**This is one compile of one program.** A compile error proves *that* spelling
fails; it does not prove the class is empty. **Attack it.** Named routes the
engineer did not try, none of which I have run:

- **`Vec<Node>` with `Option<NonZeroU32>` links but a real free list** — the
  engineer's `a3` showed `Vec<Node>` releases 0 heap blocks, but a *slot* free
  list recycles slots without releasing pages. Is *"the slot is recycled while a
  stale index still names it"* a temporal class the tree does not have? ⚠ That is
  the `p33` row's own pitch (*"use-after-recycle"*), so if it works, the finding
  may belong to `p33` and not `p28` — **say which.**
- **A generation-tagged handle** (`(slot, gen)`), which is exactly what
  `RECAP.md`'s p14-cycle entry proposes for the lifetime pattern and which `p27`
  did **not** ship.
- **`&'a Node` arena with lifetimes** (typed-arena shape) — no free at all, but
  does it change the `E0499` half?
- **Split-borrow spellings**: `slice::split_at_mut`, `Vec::swap`, or index-based
  `&mut` acquired one at a time. `E0499` is about *simultaneous* `&mut`; an
  unlink that takes them **in sequence** may compile.

**If any of these compiles and frees, §0.3's table is incomplete and the kill is
unsound.**

### B — the "identical at the rung boundary" step for candidate 2b

The engineer concedes **2b (double unlink from a cached triple) is DISTINCT at
the C detector** — `attempting double-free`, abort 134, not `p27`'s SIGSEGV —
and that `p27/NOTES.md` §0b **agrees it is a different bug in a different
class**. It is then killed on two grounds:

1. **Miri collapses it** to the same `has been freed, so this pointer is
   dangling` string on the unsafe-Rust rung.
2. The safe rungs that prevent it do so by `p27`'s mechanism.

⚠ **Attack ground 1 specifically.** Is Miri's *string* the same, or is its
*diagnosis* the same? Check the error **kind** and whether it is reported at the
`dealloc` call rather than at a load — a double-free reported inside `dealloc` is
arguably a different Miri finding from a dangling read, and the engineer read one
line of output. Also: **does `-Zmiri-tree-borrows` change it?** And does UBSan or
glibc's own `MALLOC_CHECK_`/`tcache` diagnosis give the pattern a **detector the
tree does not already have** — `p27` has no `abort 134` row.

### C — the cost decomposition, and whether the kill follows from it

The closed decomposition is `−9.00` check `−16.00` index→pointer `+321.00`
allocator `= +296.00 exact`, and the conclusion drawn is *"the only internally
consistent `p28` is an `index >= len` pattern, the fifteenth."*

- **Re-run it.** `build.sh` is supposed to regenerate every number; the engineer
  reports the intercept moving `+19 Ir` between invocations and only slopes being
  quoted. **Verify that the slopes reproduce for you**, on your own invocation.
- ⚠ **Is `rawptr` (per-node `malloc`) even the right R4?** `.memory/06-catalogue.md`'s
  `p31` entry records that **both gcc and clang DELETE a non-escaping
  `malloc`/`free` pair entirely**, giving `2.00 Ir/object` where the true figure
  is `140.00`. **Check whether `rawptr`'s 321 is a real allocator cost or a
  measurement artefact in the other direction**, and whether
  `-fno-builtin-malloc` / the Rust equivalent moves it.
- **Does the conclusion actually follow?** `p27` ships a pattern whose R1 and R4
  both `malloc` per record and whose safe rungs do too — so *"an allocator term
  makes the ladder dishonest"* would have killed `p27`, which shipped and
  published `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, a
  **closed decomposition of exactly this problem.** ⚠ **Why can `p28` not do what
  `p27` did?** If it can, the cost half of the refusal falls.

### D — the generalisation I am about to act on, and it is MINE, not the engineer's

I am reading this refusal as evidence about the **whole pointer-backed family**:
that safe Rust's answer to every such structure is either *an arena that never
frees* or *`p27`'s mechanism*, and therefore that `p29`/`p30`/`p32`/`p33`/`p34`
may be **one finding, not five.**

⚠⚠ **The engineer did not claim that and I have not measured it. It is exactly
the kind of armchair generalisation that has cost this project two refused axis
proposals** (RECAP time-waster 4). A concurrent task (`TASK_094`) is probing it.
**If you can refute it cheaply from p28's own evidence, say so** — it changes what
gets built next far more than the p28 row itself does.

---

## Also check, briefly

- ⚠ **Rule 10 / rule 3:** the report's §0 candidate list is **mine**. The
  engineer refused all four of my candidates and added a fifth of its own
  (`Rc`/`Weak`). **Did it steelman mine, or refuse the weakest reading?**
- **`p01` in the count of 14.** The engineer says the enumerated `index >= len`
  list in `p46/NOTES.md:26` includes `p01`, *"whose catalogue bug-class column
  reads `none (calibration)`"*, so 14 carry the axis and 13 model a bug.
  **Verify** — three files assert an ordinal built on that list.
- **The unexplained `box_arena` band jump** (`408.078` → `472.050`). The engineer
  flagged it and did not chase it. Is it the `Vec` growth doubling? If so the
  number is an artefact of the band, not of the rung.
- **`env -u LD_PRELOAD`.** ✅ **Manager-verified already** — `.temp/mgr93/uaf.c`
  rebuilds it; behind the inherited `LD_PRELOAD` an ASan binary exits **1** with
  **zero `AddressSanitizer` report lines**, printing only *"ASan runtime does not
  come first"*. `harness/check.py` uses `-static-libasan` and is unaffected.
  **Do not re-verify this; do check whether any OTHER hand-run probe in `.temp/`
  or in a committed `controls/` script is exposed to it.**

---

## Constraints

- **`.temp/r93/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `pilot/`, `harness/build.py` or `harness/asm.py`.**
- ⚠⚠ **Do not run `harness/check.py` or `harness/measure.py`** — both rewrite
  tracked records in place, and `TASK_094` is running concurrently under the same
  prohibition. Neither of you may touch a record; that is what makes the
  concurrency legal (`RECAP.md`, the concurrency rule).
- ⚠ **Do not plant into tracked `patterns/` files.** If an attack needs one,
  report the recipe instead; the manager will schedule it alone.
- Verus only via `./verus_run.py`, single-file mode (concurrency-safe).
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Give clean negatives.** A named attack that did not land is worth as much as
  a finding and stops the next agent re-running it.

---

⚠ **PROTOCOL rule 2's running count is 264.** The engineer carried it 261 → 264
in one session, all three against me. **The calls I am least sure of now:**

1. ⚠⚠ **That the structural claim in A is a CLASS result and not a
   ONE-SPELLING result.** One compile does not empty a class, and this is the
   load-bearing beam of the whole refusal.
2. **That `p28` cannot do what `p27` did with its allocator term** (C).
3. **That the family generalisation in D holds at all** — mine, unmeasured, and I
   am about to schedule on it.

Carry **264** forward, incremented by what you find.
