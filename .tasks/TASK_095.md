# TASK_095 — build `p29` as the 25th pattern, OR refuse it

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`RECAP.md`'s START HERE box, then **`.memory/01-ladder.md`'s allocator-guarantee
section** (the rule that selected this row), `.memory/06-catalogue.md`'s `p29`
and `p27` rows, and `.tasks/TASK_094_REPORT.md` §1 — **your starting evidence,
and it is UNREVIEWED, so attack it.**

The nearest sibling is `patterns/p27-handle-table/`. Read its `spec.md`,
`verus.rs` and `NOTES.md` §0, §0a and §0b before designing anything.

Scratch in **`.temp/t95/`** — free, I checked. ⚠ `.temp/p29/` exists and is an
older, unrelated thing. **Do not write into it.**

---

## Why this row and not another

Of 48 catalogue rows: **24 built, 13 refused, 11 remaining — and exactly TWO are
live build candidates.** `p29` is one; `p23` is the other and would be the tree's
**fifteenth `index >= len`**.

`p29` is the only row in the catalogue that answers **both** halves of the
allocator-guarantee test YES:

- **(a) the safe representation actually frees** — `allocs=2001 frees=2000`, and
  `remove_leaf` releases **one block of exactly 24 bytes = `sizeof(Node)`**,
  against `p28`'s measured `0`.
- **(b) the mechanism is NOT `p27`'s** — it is **`E0502` at COMPILE TIME**.
  `p27`'s safe rung **runs** and *"the ASKING goes missing"*; `p29`'s **does not
  compile**.

And its R5 closes at **`4 verified, 0 errors`, TCB 0** on a recursive
`Box<Tree>` with a `Set`-valued functional postcondition — **the third
first-attempt contradiction of the catalogue's retracted *"expect Family E to
defeat R5"*.**

---

## §0 — SETTLE THE BUG CLASS FIRST. YOU MAY REFUSE.

⚠⚠ **`TASK_093` refused `p28` at `§0` two days ago on the sentence *"it is
`p27`'s in a costume"*, and `p29`'s FIRST kill risk is that same sentence.**
`TASK_094` states it plainly and did **not** close it:

> **The bug class IS `p27`'s** — same ASan line, verified side by side. What is
> new is the **rejection mechanism** (compile-time vs runtime), not the class.
> §0 must carry that distinction or the row is `p27` with branches.

**So decide, in writing, before you build anything: is *"same bug class,
different rejection mechanism"* enough to carry a pattern?**

**The precedent cuts both ways and you should weigh both:**

- ✅ **FOR:** `p36` shipped with the tree's **twelfth** `index >= len` and was
  worth building, because its *mechanism*, *catcher* and *prover* stories were
  each new. `.memory/06-catalogue.md` calls that the escape hatch by name.
  A **compile-time** rejection of a **temporal** bug is `p08`'s kind of boundary
  applied to a class that has only ever been rejected at runtime here.
- ⚠ **AGAINST:** `p31` was refused partly *because* its mechanism was `p12`'s and
  its prover story was `p27`'s minus a Map. If `p29`'s only novelty is the
  compiler diagnostic, ask what the **six rungs** measure that `p27`'s do not.

⚠ **The honest framing to test:** `p27` and `p29` would then be a **matched
pair** — one temporal bug rejected at runtime by an `Option` discriminant, the
same class rejected at compile time by the borrow checker — **and a pair is worth
more than either row alone.** But that is an argument, and I want it decided
against the *measured behaviour matrix*, not against my sentence.

**If §0 concludes the row is `p27` with branches, REFUSE IT with the
measurement and stop.** That is a complete task.

---

## §1 — THE THREE KILL RISKS, AND TWO ARE UNMEASURED

`TASK_094` names three and closed none.

1. **The bug class** — §0 above.
2. ⚠⚠ **THE COST KERNEL OMITS THE `remove`.** `TASK_094`'s `k29_*_lookup` pair
   does not free anything. **That is `TASK_091`'s `p28` defect exactly**, and the
   free is where the temporal class lives. ⚠ **Note what the review established
   about that defect: it is a RUNG-PAIR problem, not a probe-shape one**
   (`.memory/03-measurement.md`) — *"probe shape = same rungs, different harness;
   different rungs = a design choice, argued not measured away."* **So measure a
   pair that frees on BOTH sides**, the way `TASK_093_REVIEW` did to get its
   `0.00` allocator term.
3. ⚠⚠ **THE PROVED FUNCTION IS NOT THE INTERESTING FUNCTION.** Only `contains`
   was proved. **`insert` and `remove` were not attempted**, and the two-child
   `remove` needs the in-order successor, must re-establish `bst()`, and must
   relate `keys()` across the mutation. **That is the real budget and it is where
   the session will go.** Proof budget is **one session per R5 cell**; if it does
   not converge, **stop and report the exact obligation** — a documented R5
   failure is a finding, not a gap.

---

## §2 — THE COST AXIS IS A DECLARED ZERO, AND THAT MUST BE WRITTEN DOWN FIRST

`TASK_094` measured **`−0.00024 Ir`/lookup** with a mechanism: **a tree walk has
no index, so there is no bounds check to remove**, and `Option<Box<T>>`'s niche
**is** the null pointer — `while let Some(n)` and `while !cur.is_null()` lower to
the same `test/je`.

⚠⚠ **PROBE 3 IS NOT OPTIONAL HERE.** `.memory/06-catalogue.md`: *"any published
`0.00` must name its AXIS and its `Ir` CONVENTION in advance."* **`p45` could have
shipped `R3 − R4 = 0.00` as *"safety is free"* when the truth was *"there is only
one rung"*.**

**Write into `spec.md` §0, BEFORE measuring, that the axis carrying this row is
the BEHAVIOUR MATRIX and COMPILE-TIME EXPRESSIVENESS, and that the cost axis is
an expected zero with a stated mechanism.** Then measure it and say whether the
mechanism held.

⚠ **And check probe 2 with the REPAIRED instrument** — the md5 form is now known
broken in **both** directions (`.memory/06-catalogue.md`'s probe block). Use
normalised-disassembly text (`.temp/t94/knorm.py`), not the linked md5, or a
kernel with a branch passes vacuously.

---

## §3 — IF §0 CLEARS IT, BUILD IT

Clone `patterns/p01-array-sum/` as the template. All six rungs, both opt levels,
both inline modes. `spec.md` with the hashed `slb-contract` block, `model.py`,
`inputs/gen.py`, `NOTES.md`, `README.md`.

**PROTOCOL rule 6: record the `slb-contract` sha256 in `NOTES.md` BEFORE building
any cell**, and say that the `git show HEAD:` diff is **vacuous on a new
pattern** rather than citing a command that cannot fire. ⚠ **Rule 6's added
step:** before finishing, re-read the hashed `why` and **every rung-source doc
comment** against your own measured numbers — `p46` shipped a `why` asserting
*"neither side is degenerate"* against numbers its own `NOTES.md` had retracted,
**with the hash matching perfectly.**

⚠⚠ **SEARCH BOTH SIDES.** Five patterns have published a headline wrong in the
flattering direction, and `p36`'s mirror image is the current lesson: it searched
R4 hard, left R3 with one lever, and R3 moved the wrong way. **Count the levers
on each side and say whether they are comparable.**

Then `harness/check.py p29-<slug>` green, `harness/measure.py`, `--check-stale`.
⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed,
a full re-measure of every record.

---

## Hazards, all measured, all cheap to hit

- ⚠⚠ **Hand-run ASan is BLIND behind this box's inherited `LD_PRELOAD`** — exit
  **1**, **zero `AddressSanitizer` lines**. **Use `env -u LD_PRELOAD`.** The gate
  is unaffected (`-static-libasan`). ✅ Manager-verified.
- ⚠ **Never truncate a sanitiser log with `head`** — `TASK_086`'s `head -4` hid
  ASan's banner for four catalogue rows. `grep`, don't `head`. **Give every harm
  probe a positive control that must fire.**
- ⚠ **`malloc_consolidate` at a 64 KiB freed chunk adds ~64 `Ir`/node to a whole
  band.** Any `Ir` sweep crossing it picks up a one-off ~262k `Ir` smeared across
  the band. Siblings: `rep movsb` at 8192 bytes, `rep stos` at 2048.
- ⚠ **Both gcc and clang delete a non-escaping `malloc`/`free` pair entirely.**
  A row that allocates in the kernel must defeat that elision or it measures
  nothing.
- ⚠ **There is NO working leak detector for the C rungs on this box** — LSan is
  silent at `-O1` and the gate builds stage 7 at `-O1`; memcheck cannot run.
  **Do not design a row whose harm is a leak.**

---

## Constraints

- **`.temp/t95/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t95/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` is manager-only.** Report durable facts; I land them after review.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

---

⚠ **PROTOCOL rule 2's running count is 270.** **Every agent that has contradicted
me with a measurement has been right — 270 times, and the last nine were in two
concurrent sessions, six of them from a reviewer taking apart an engineer's
refusal I had already half-believed.** The calls I am least sure of:

1. ⚠⚠ **That *"same bug class, different rejection mechanism"* is enough to
   carry a pattern** (§0). This decides whether the row exists, and I am aware I
   want it to be yes because it is the last live row in its family.
2. **That the `remove`-inclusive cost pair does not invert the sign** — the
   lookup pair measured `0.00`, and nobody has measured a pair that frees.
3. **That `remove`'s proof fits one session.** `contains` closing at `4/0` says
   nothing about it.

**Refuse the row if it deserves refusing.** Carry **270** forward, incremented by
what you find.
