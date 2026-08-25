# TASK_093 — build `p28` as the 25th pattern, OR refuse it with a measurement

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`RECAP.md`'s START HERE box, then `.memory/` 00–06 (**06's `p28` row and its
`p27` row, side by side**), then `.tasks/TASK_091_REPORT.md` (**your own
starting evidence — and it is UNREVIEWED, so attack it**) and
`.tasks/TASK_086_REPORT.md` §5.

Scratch in **`.temp/t93/`** — free, I checked. ⚠ **`.temp/p28/` ALREADY EXISTS
and is a different, older thing. Do not write into it.**

The nearest sibling is `patterns/p27-handle-table/`. Read its `spec.md`,
`verus.rs` and `NOTES.md` §0 before you design anything.

---

## §0 — SETTLE THE BUG CLASS FIRST, AND YOU HAVE AUTHORITY TO REFUSE THE ROW

⚠ **This is the whole task until it is answered.** Do not write a rung, a
`spec.md` or an input generator until §0 is settled and written down.

The catalogue's `p28` row says the bug class is **temporal** — *"dangling
`prev`/`next` after an unlink"* — and that it *"shares with p27, the only
temporal pattern in the tree."* **That is the entire reason I am scheduling
it**: the tree has **fourteen** built `index >= len` patterns and **one**
temporal one, so a second temporal row is the scarcest thing p28 can add.

⚠⚠ **AND I AM NOT SURE IT SURVIVES CONTACT, FOR A REASON THIS PROJECT HAS
ALREADY KILLED A ROW WITH.** `TASK_083_REVIEW` refused `p25` in one sentence:
*"the stale-pointer harm is **p27's in a costume** — at the detector."* **Ask
whether p28's is too.** If p28's shipped bug is *"read a handle whose block was
freed"*, that is p27's use-after-free with a different container around it, and
the row should be **refused with the measurement**, not built. Three refusals
have been the right outcome; a duplicate 25th pattern would not be.

**So §0's job is to find the shape — if one exists — where p28's temporal bug is
NOT p27's.** Candidates, none of which I have run, none of which you should
trust me on:

1. **The stale NEIGHBOUR link.** `unlink(b)` from `a↔b↔c` and forget to write
   `c.prev = a`. Now `c.prev` points at a node that is still **allocated and
   live** — the list is corrupt but nothing is freed. That is a **wf/aliasing**
   bug, not a UAF, and no detector in the gate's set (ASan, UBSan, Miri) has
   anything to fire on. ⚠ **If nothing fires, the harm row is silent and you are
   in p22's territory — which is a real finding, but it is a DIFFERENT finding
   from "temporal" and the row must then be re-pitched, not quietly relabelled.**
2. **The double unlink.** `unlink(b)` twice: the second one reads `b.prev`/
   `b.next` that the first already stripped, and writes through them. If `b` was
   freed by the first, this is a genuine **double-free / UAF write** — p27 has a
   UAF **read** and no double-free, so *"the write path"* may be the
   distinguishing half.
3. **Unlink-then-traverse.** The dangling pointer is dereferenced by the *list
   walk*, not by a handle lookup — so the harm site is `O(n)` away from the bug
   site, which is **p13's shape** (*"the harm lands at a different site from the
   bug"*) applied to a temporal bug for the first time.

**Reject the ones that do not survive, name the one that does, and say WHY it is
not p27.** If none survives: **write the refusal, with the measurement that kills
it, and stop.** That is a complete task and a publishable outcome.

⚠ **The novelty claim in the paragraph above is MINE and it is a claim, not a
fact.** *"Fourteen `index >= len` and one temporal"* — **count it yourself**
before you lean on it. `TASK_086` #240 caught me miscounting this exact number
once already (I wrote fourteen when the built tree carried twelve).

---

## §1 — THE `deallocate` QUESTION, WHICH IS WHERE THE BUG CLASS ACTUALLY LIVES

`TASK_091` proved `wf` **preserved** (`4/0`) and **establishable** (`8/0`, first
attempt, zero TCB, and it compiles and runs). ⚠⚠ **But its probe drops
`Tracked<Dealloc>` and LEAKS — there is NO `deallocate` anywhere in it.** The
catalogue row says so in capitals and it is the honest risk.

**A temporal bug class needs a free.** So:

- Thread `Dealloc` the way `patterns/p27-handle-table/verus.rs` does, and make
  `unlink` actually **deallocate** the victim node.
- ⚠ **`TASK_091` added a key-discipline conjunct to `wf`**
  (`m.dom().contains(a) ==> m[a].ptr().addr() == a`) to make the injectivity
  `assert forall` legal. **A `deallocate` REMOVES a key from that map.** Nobody
  has checked that `wf` survives a removal, and `TASK_091`'s own §2 records that
  strengthening `wf` made `unlink` *harder*, not easier. **Budget for this.**
- If `deallocate` does not close within your session, **that report is the
  deliverable** (`.memory/02-bench-rules.md`: a documented R5 failure is a
  finding). State the exact obligation, do not `assume` past it.

---

## §2 — THE RUNG DESIGN, AND THE MISATTRIBUTION TRAP I CANNOT DESIGN AROUND

The catalogue's `p28` row carries this warning and I do not know the answer to
it:

> ⚠ **4.0 of the 12.5 `R3→R4b` gap is INDEX SCALING, not checking** — three
> `shl $0x4` a pointer list does not pay — **so a p28 whose R3 is a safe index
> arena would misattribute it.**

**And a safe Rust doubly linked list is an index arena** (`Vec<Node>` with
`Option<usize>` links); the alternatives are `Rc<RefCell<_>>`, which is a
different algorithm with a different complexity, or nothing.

⚠ **So I do not think this trap can be avoided — I think it has to be
DECOMPOSED and DISCLOSED.** That is a design call and it is yours. Whatever you
choose, the pattern must publish the split — how much of `R3 − R4` is the bounds
check, how much is index scaling, how much is register pressure — the way
`TASK_091` already split its own 8.5 (`6` + `~1` + `~1.5`). **A single `R3 − R4`
number on this pattern would be dishonest and I will not ship one.**

⚠⚠ **SEARCH BOTH SIDES.** Five patterns have now published a headline wrong in
the flattering direction (p10, p27, p38, p22, and p36's mirror image), and p36's
lesson is the current one: **it searched R4 hard, left R3 with one lever, and R3
moved the wrong way.** Count the levers on each side and say whether they are
comparable.

---

## §3 — MEASURE AT SHIPPED SHAPE, NOT PROBE SHAPE

⚠⚠ **This is new and it is the most recently-learned thing in the project.**
`TASK_092` re-measured two probed rows at *shipped* shape and **both probe
numbers were wrong**: `p24`'s `+7.85 Ir`/element **collapsed to `0.00` with
byte-identical kernels**, and `p26`'s **sign inverts** with run length. The
mechanism is `p46`'s: **a probe kernel whose SIGNATURE differs loses the range
facts the shipped kernel derives from its input header**, so a probe can lose the
**slope**, not just the intercept (`.memory/03-measurement.md`).

`TASK_091`'s `7.507` / `11.503` / `20.003` are **probe-shape numbers**.
`.memory/03-measurement.md`'s ranked blast-radius table says **p28 is "not
exposed"** — ⚠ **that is MY ranking and it is the call I am second-least sure
of. Re-measure at shipped shape and tell me if I am wrong.** Two of my four
rankings in that table have already been refuted.

State your `Ir` convention (kernel-exclusive or whole-program marginal) **in
advance**, and note that `.memory/06-catalogue.md`'s p48 and p13 entries both
record the kernel-exclusive column **erasing or reversing** a comparison on a
pattern that allocates.

---

## §4 — IF §0 CLEARS IT, BUILD IT

Clone `patterns/p01-array-sum/` as the template. All six rungs, both opt levels,
both inline modes. `spec.md` with the hashed `slb-contract` block, `model.py`,
`inputs/gen.py`, `NOTES.md`, `README.md`. **PROTOCOL rule 6: record the
`slb-contract` sha256 in `NOTES.md` BEFORE you build any cell**, and note that
the `git show HEAD:` diff is vacuous on a new pattern — say so rather than
citing a command that cannot fire.

⚠ **Rule 6's new step:** before you finish, re-read the hashed `why` and **every
rung-source doc comment** against your own measured numbers. `p46` shipped a
`why` asserting *"neither side is degenerate"* with two numbers its own
`NOTES.md` had already retracted, **and the hash matched perfectly.**

`harness/check.py p28-<slug>` green, then `harness/measure.py`, then
`--check-stale`. ⚠ **Do not touch `harness/build.py` or `harness/asm.py`** —
measurement-hashed, a full 43-minute re-measure of every record.

---

## Constraints

- **`.temp/t93/` only. No `/tmp`.** Keep the generator, delete the artefact
  (`.memory/00-environment.md` constraint 6). Notes in `.temp/t93/NOTES.md` as
  you go — five agents have died to transient API errors and none lost work.
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` is manager-only.** Report durable facts; I land them after review.
- Do not edit `pilot/`. Do not bump the Verus/vstd pin.
- Verus only via `./verus_run.py`. Single-file mode is concurrency-safe;
  `--cargo` is not.
- `timeout <N> <cmd>` on anything long. **Never `pkill`/`killall`** — confirm the
  full command line of an exact PID.
- Proof budget: **one session per R5 cell**, then stop and report where it stuck.

---

⚠ **PROTOCOL rule 2's running count is 261.** **Every agent that has contradicted
me with a measurement has been right — 261 times.** The calls I am least sure of,
in order:

1. ⚠⚠ **That p28's temporal bug is NOT `p27`'s in a costume** (§0). This is the
   one that decides whether the row exists. `p25` died on exactly this sentence.
2. **That p28 is "not exposed" to the probe-shape defect** (§3). My ranking, two
   of four already refuted.
3. **That the index-scaling confound can only be decomposed and not avoided**
   (§2). If you find an R3 that is neither an index arena nor a different
   algorithm, that is a better answer than mine.

**Refuse the row if it deserves refusing.** Carry **261** forward, incremented by
what you find.
