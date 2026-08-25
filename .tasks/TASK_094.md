# TASK_094 — batched probe of the nine unprobed rows, and one structural question

**Role: research engineer (selection probe).** Read `.tasks/PROTOCOL.md`, then
this file, then `.memory/06-catalogue.md` — **especially "THE LADDER TEST" and
"The three probes"** (probe 4 is in that block too, out of numeric order) — then
`.tasks/TASK_086_REPORT.md` as the **model for what a good output looks like**,
then `.tasks/TASK_093_REPORT.md` (**it is UNREVIEWED and a review is running
concurrently; treat its conclusions as hypotheses, not facts**).

Scratch in **`.temp/t94/`** — free, I checked. ⚠⚠ **`.temp/p29/`, `.temp/p32/`,
`.temp/p34/`, `.temp/p37/`, `.temp/p39/`, `.temp/p43probe/` and `.temp/p44/`
ALL ALREADY EXIST and are older, unrelated things.** `.temp/pNN/` is a live
collision between PATTERN and TASK directories — **`ls` any scratch path before
you name it.**

**Deliverable: a RANKED QUEUE**, in `.tasks/TASK_094_REPORT.md`, in
`TASK_086_REPORT.md`'s format. **Every ranked row must carry at least one thing
that was RUN.** You have authority to **REFUSE rows with a measurement**; three
prior refusals were each the right call.

---

## The nine rows

Every one is `planned` and **none has been probed.** These are all that remain
unexamined; the rest of the catalogue is built, refused, deferred or queued.

| row | catalogue pitch | my prior, which is a claim and not a fact |
|---|---|---|
| `p29` | BST insert/lookup — recursive ownership | a tree is **not** cyclic, so safe `Box` children compile. Likeliest of the five to have a real safe rung |
| `p30` | chained hash table — *"combines p22 + p27"* | the catalogue's own column says it is two shipped patterns. **Probably a duplicate; prove it either way** |
| `p32` | free-list allocator — double free, corruption | `TASK_093` measured a safe index arena in which **the double free COMPILES and becomes aliasing + non-termination, Miri clean, exit 0** (`a2 x=2 y=2 aliased=true`). That is `p04` + `p22` — but it is also a *safe-Rust-does-not-help* result, which the tree has exactly one of |
| `p33` | object pool with recycling — use-after-recycle | ⚠ **the slot is recycled while a stale index still names it.** The memory is **live and owned**, so this is NOT a UAF and no sanitiser has anything to fire on. If that holds it is a class the tree does not have |
| `p34` | reference counting — leak, premature free | `TASK_093` measured `Rc`/`Weak` reproducing **`p27`'s published sentence verbatim**. Likely refused |
| `p37` | callback with `void*` userdata — type confusion | nearest are `p35` (blocked) and `p36` (built). Ask whether it is `p36` with a data payload |
| `p39` | bitfield pack/unpack — shift/mask off-by-one | `p09` already ships `q & 31` as *"one character between a bug everything catches and one nothing does"*. Ask what is not `p09`'s |
| `p43` | CRC over an untrusted length | ⚠ **the catalogue itself says *"p43 is p16's shape"***. Refuse it or find what is not |
| `p44` | fixed-point arithmetic — overflow, rounding | `p45` was refused because it **had no unsafe rung with a job**. Ask that question FIRST; if the answer is the same, it is one probe and done |

⚠ **Every prior in that right-hand column is mine, written from reading. Both
axis proposals I have made from reading were refused after one `grep` and one
run.** Run the thing; contradict me.

---

## The five probes, and the fifth is new

**1–3 and 4** are in `.memory/06-catalogue.md`'s probe block. In brief:
**(1)** a rung boundary must exist *somewhere* and the row must NAME it — not
necessarily R3-vs-R4; **(2)** the rungs must differ **as machine code**, ⚠ **from
the LINKED binary, or read `readelf -rW`** (the object-file form false-positives
and produces exactly `p45`'s verdict); **(3)** any published `0.00` must name its
axis and `Ir` convention **in advance**; **(4)** does the row's unsafe operation
have a `vstd` spec — **necessary, not sufficient**, and the test that actually
decides it is *"does an `unsafe` token end up inside a VERIFIED body"*
(`.temp/t86/scan_unsafe_probe.py` drives the real rule).

⚠⚠ **5 — MEASURE AT SHIPPED SHAPE, OR SAY YOU DID NOT.** `TASK_092` re-measured
two probed rows at shipped shape and **both probe numbers were wrong**: `p24`'s
`+7.85 Ir`/element collapsed to **`0.00` with byte-identical kernels**, and
`p26`'s **sign inverts** with run length. `TASK_093` then found a **third**
mechanism: `TASK_091`'s `p28` probe **omitted the `deallocate`** — the operation
its own bug class requires — and reported `R3 − R4` with **the wrong sign**
(`+12.50` against a true `−296.00`).

**So for every cost number you report, state which of these it is exposed to:**
- does your probe kernel's **signature** give it range facts the shipped kernel
  would not have, or deny it ones it would (`p46`/`p24`)?
- does your **input band** hold a parameter at one residue or one magnitude
  (`p26`, and `p38`'s additivity failure)?
- does your kernel **omit an operation the bug class requires** (`p28`)?

**A probe number with no exposure statement is not usable and I will not rank
on it.**

---

## ⚠⚠ THE STRUCTURAL QUESTION — ask it of `p29`, `p30`, `p32`, `p33`, `p34`

`TASK_093` refused `p28` on a structural ground, not a detector one:

> Safe Rust cannot express an owned intrusive doubly linked list, so `p28`'s safe
> rungs have three spellings and **each destroys a different half of the
> pattern** — the index arena **never frees** (temporal class structurally
> absent, measured: 0 heap blocks released), and both spellings that *do* free
> catch the bug by **`p27`'s exact mechanism** (*"the free and the invalidation
> are one operation in safe Rust and two in C, and the bug is the third — the
> ASKING — going missing"*).

⚠⚠ **I AM READING THAT AS A FAMILY RESULT AND I HAVE NOT MEASURED IT.** My
working hypothesis is that `p29`–`p34` may be **one finding, not five**, and that
`p27` already published it. **That is an armchair generalisation from a single
unreviewed row and it is the call I am least sure of in this file.**

**So for each of the five, answer this in two lines, with a compile:**

> **(a)** Does safe Rust have a representation of this structure that actually
> **frees** — measured, not argued (count released heap blocks, or `allocs`
> vs `frees`)?
> **(b)** If it does, does it catch the row's bug by a mechanism that is **NOT**
> `p27`'s single-operation free-and-invalidate? **Name the mechanism.**

**A row that answers (a) NO or (b) NO is a duplicate or a null, and should be
refused with the measurement.** ✅ **A row that answers (a) YES and (b) YES is
the most valuable thing left in this catalogue — say so loudly.**

⚠ **`p33`'s recycle is the one I would bet on**, because a recycled *slot* is
live, owned, in-bounds memory: nothing is freed, so `p27`'s mechanism has nothing
to fire on and neither does any sanitiser. ⚠ **But that is a bet, and the same
sentence about `p28` was written from a source read and survived eight days
before a compile killed it.**

---

## Hazards, all measured, all cheap to hit

- ⚠⚠ **Hand-run ASan is BLIND on this box behind the inherited `LD_PRELOAD`.**
  ✅ **Manager-verified** (`.temp/mgr93/uaf.c` rebuilds it): exit **1**, **zero
  `AddressSanitizer` report lines**, only *"ASan runtime does not come first in
  initial library list"*. **Use `env -u LD_PRELOAD`.** `harness/check.py` uses
  `-static-libasan` and is unaffected.
- ⚠ **Never truncate a sanitiser log with `head`.** `TASK_086` used `head -4`;
  gcc's UBSan report is exactly 4 lines and ASan's banner is on lines 5–6, so
  **four rows of that report showed only half the detectors.** `grep`, don't
  `head`.
- ⚠ **Both gcc and clang DELETE a non-escaping `malloc`/`free` pair entirely** —
  `2.00 Ir/object` measured where the true figure is `140.00`. Any row that puts
  allocation in the kernel must defeat that elision or it measures nothing
  (`.memory/03-measurement.md`).
- ⚠ **`rep movsb` / `rep stos`**: callgrind charges ≈1 `Ir` per byte moved, and
  glibc switches at **8192 bytes** (`memcpy`) — so `Ir` can report a cost
  **rising** at exactly the size the real cost **falls**. Any row that copies or
  fills in bulk must state its domain.
- **Verus**: `./verus_run.py` single-file only (concurrency-safe); `--cargo` is
  **not** and a review is running concurrently.

---

## Constraints

- **`.temp/t94/` only. No `/tmp`.** Keep the generator, delete the artefact:
  binaries, `.o` and `.bin` go once your numbers are green; the `.c`/`.rs`/`.py`
  sources, `NOTES.md`, `.json` and `.log` are the evidence and stay. **If a blob
  has no script that rebuilds it, write one before you finish.**
- **Notes in `.temp/t94/NOTES.md` as you go** — five agents have died to
  transient API errors and none lost work, because they wrote as they went.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠⚠ **Do not run `harness/check.py` or `harness/measure.py`** — both rewrite
  tracked records in place, and `TASK_093_REVIEW` is running concurrently under
  the same prohibition. Neither of you may touch a record; that is what makes the
  concurrency legal.
- ⚠ **Do not edit `.memory/`, `pilot/`, `patterns/`, `harness/build.py` or
  `harness/asm.py`.** Report durable facts; the manager lands them after review.
- Do not bump the Verus/vstd pin. `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Nine rows is a lot. If you run out of session, rank what you finished and say
  which rows you did not reach** — a ranked queue of five with honest gaps beats
  nine rows of reading.

---

⚠ **PROTOCOL rule 2's running count is 264.** **Every agent that has contradicted
me with a measurement has been right — 264 times, and the last three were all in
one session, on this exact subject.** The calls I am least sure of:

1. ⚠⚠ **That `TASK_093`'s structural finding generalises to the family at all.**
   Unmeasured, mine, and I am scheduling on it.
2. **That `p33`'s recycled-slot bug is a class the tree does not have.**
3. **That `p30` and `p43` are duplicates** — both are the catalogue's own words,
   and the catalogue has been wrong about a row's bug class **four times**.

Carry **264** forward, incremented by what you find.
