# TASK_104 — build `p42`, leak on the error path (`goto cleanup`)

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`patterns/p01-array-sum/` **in full** (the template every pattern clones —
`spec.md` carries the kernel contract *and* the machine-readable pins the gate
enforces; `model.py` is the independent reference the gate drives; **both are
mandatory**), then `.tasks/TASK_100_REPORT.md` **§A4, §A5 and §A6**, then
`.memory/00-environment.md`'s leak section, then `.memory/06-catalogue.md`'s
`p42` row and **THE THREE PROBES + probe 4 + probe 5**.

Scratch in **`.temp/t104/`**. Pattern dir is **`patterns/p42-goto-cleanup/`**
unless you can argue a better name.

**This is the 26th pattern** (or the 25th, if `p23` has not landed when you
start — check `ls -d patterns/p*/ | wc -l` and say which).

---

## Why this row, when eight others were just refused

⚠⚠ **`TASK_102` probed eight candidate rows and refused all eight**, and its
generalisation is now RECAP **finding 37**:

> **This benchmark can price a safety property IFF some rung emits it as a
> compare-and-branch and another rung omits it.**

**`p42` passes that test and it is the reason it survived where eight did not:**
the safe rungs get `Drop` glue emitted by the compiler, the C and unsafe rungs
get a hand-written `free` on every path **and one path where the author forgot
it**. ⚠ **Probe 1's boundary is REAL here — RAII against `goto cleanup` — but you
must still MEASURE it rather than inherit it from this paragraph.**

✅ **Already established by `TASK_100`, so do not re-derive it:**

- **The detector works at the gate's own stage-7 flags with NO hook.** A
  synthetic pdir built from the real `common/driver.c` + p01's C rung, with
  `goto cleanup` skipping one `free`: **clean arm `exit=0 fired=no` on both
  inputs; leak arm `exit=1 fired=YES`, `16000 byte(s) leaked in 1 allocation`
  (small) and `12000000 byte(s)` (large).**
- ⚠ **A leak whose root stays on the STACK is invisible at `-O1`/`-O2`** because
  inlining keeps the root live. **p42's shape avoids it** (the pointer is dead by
  the time `cleanup:` is reached) — ⚠ **but VERIFY that for YOUR kernel, and if it
  bites, the one-line fix is `__lsan_default_options()` returning
  `"use_stacks=0"` in `c/main.c`, which is `Ir`-neutral to the instruction.**
- ⚠⚠ **DO NOT use a `--wrap=malloc` counter in a measured cell — it costs
  `+2210`/`+2250 Ir`.** Harm probe only.
- ✅ **The bug class is genuinely absent from the tree** — a 24-pattern census
  finds **zero** leak rows, and `p27` is built **not** to leak *by contract*
  (`p27/spec.md:372`, forbidding `ManuallyDrop`/`mem::forget`/`Box::leak`/
  `Box::into_raw`). ⚠ **Re-run that census as your §0 rather than trusting it.**

---

## §0 — settle the bug class and the framing FIRST

1. **Confirm the census.** Is `leak` really absent? ⚠ **`p27` is the row most
   likely to collide** — it is the tree's only temporal pattern and it ships
   `allocate`/`deallocate`. **Say exactly what `p42` adds that `p27` does not**,
   and expect that answer to be *"p27 frees on every path by contract; p42's
   whole subject is the path where it does not."*
2. ⚠⚠ **THE FRAMING MUST BE CONDITIONAL AND THE CONDITIONS MUST BE PINNED AS
   `forbidden` ENTRIES**, the way `p19` and `p46` pin theirs. The obvious ones:
   the allocation must be **heap** (a stack buffer cannot leak), and the error
   path must be **reachable from the input**. ⚠ **A leak that no committed input
   reaches is a dead row** — `p31` died on exactly that shape.
3. **Real precedent, fetched and quoted.** `goto cleanup` with a missed `free` on
   one branch is one of the most common real C defects; **name a CVE or a named
   project's code and read it.** ⚠ **Do not cite from memory** — a previous
   pattern quoted a paraphrase inside quotation marks and misattributed a CVE,
   and it took a full re-measure to fix at five sites.

## §1 — ⚠⚠ THE AXIS IS A BEHAVIOUR MATRIX, NOT A COST. SAY SO IN `spec.md`.

**A skipped `free` has no per-element price.** There is no `Ir`/byte here and
**you must not manufacture one.**

- **What IS measurable:** the cost of `Drop` glue against a hand-written `free`
  on the success path, the cost of the error path's *cleanup* itself, and any
  code-size difference. **Measure those and name them for what they are.**
- ⚠ **If the rungs turn out to differ by `0.00`, that is a RESULT and this
  project has published several** (`p24` at shipped shape is byte-identical).
  **Do not go looking for a spelling that manufactures a gap.**
- ⚠ **SEARCH BOTH SIDES ANYWAY, and count the levers on each.** The trap has
  caught **five** patterns. R2/R3 have `Vec`, `Box`, and early-return-with-`?`;
  R1/R4 have single-exit `goto cleanup`, multiple-return, and a cleanup helper.
  **State whether the two sides are comparably searched.**

## §2 — the R5 question, and it is the interesting one

**Can Verus state *"this allocation is released on every path, including the
error path"*?**

- ✅ **The route is precedented:** `p27` ships `Tracked<Dealloc>` and already
  proves a deallocation obligation. **Read `p27`'s `verus.rs` before designing
  yours.**
- ⚠ **The obligation is a LINEARITY/leak-freedom property, not a bound**, which
  would make it the tree's **second non-bound obligation** (`p23`'s multiset
  being the first, if `p23` landed). ⚠ **STATE THAT AS A QUESTION AND CHECK IT** —
  `grep` the pinned `ensures` of all built patterns; the manager has been wrong
  about "first in the tree" claims **twice**, and both shipped into hashed
  contract blocks.
- ⚠ **If Verus cannot express it in budget, say so and ship R5 with a weaker,
  honestly-labelled postcondition.** Do **not** write an `assume`.

## §3 — rules that govern the numbers

- ⚠ **Name the INLINE MODE and the optimisation level at every figure.**
- ⚠ **Never publish a "minimum"** — write *"cheapest found"* and **name the
  input**. ⚠ **Do not publish a pair interval.**
- ⚠ **Extract kernel bytes from the LINKED binary** — a relocated field is zero
  in a `.o`. ⚠⚠ **AND `.temp/t94/knorm.py` — probe 2's normaliser — COUNTS
  INTER-FUNCTION ALIGNMENT PADDING**, which produced a false *"these differ"* on
  a pair that was the same program. **Use `.temp/t102/b4_norm.py`'s fix, or
  verify your symbol extents by hand.**
- ⚠⚠ **`harness/check.py` PASSES NO `MIRIFLAGS`, AND MIRI'S ALIGNMENT CHECK IS
  SEED-DEPENDENT** — the same source is clean on `-Zmiri-seed=0,2` and reports UB
  on `1,3`. **If your Rust rungs lean on Miri for the leak story, sweep several
  seeds and report which you ran.** Do **not** write *"Miri: N of N, no UB"* as
  though it were seed-independent.
- ⚠ **Every harm probe needs a positive control that must fire**, `env -u
  LD_PRELOAD`, and `grep` on the log — **never `head`**. ⚠ **Read
  `.memory/03-measurement.md`'s consolidated list of the six controls in this
  project that could not have failed, and do not become the seventh.** The most
  recent was an `if (acc & 1)` guard where `acc` was even for every input.

## §4 — Constraints

- **`.temp/t104/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t104/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.** Durable facts go in your report.
- ⚠⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed.
  ⚠ **Every rung `.rs`, `c/kernel.{c,h}`, `model.py` and `inputs/gen.py` are
  measurement-hashed too**, and **a COMMENT-ONLY edit after measuring stales the
  record. Get the C comments right before you measure.**
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only, single-file mode, never `--cargo`.
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Finish every edit BEFORE the final gate run**, then `harness/check.py p42`.

Write your report to `.tasks/TASK_104_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 324** (299 + 8 `TASK_099` + 12 `TASK_100`
+ 5 `TASK_102`; ⚠ **the manager's own +2 was WITHDRAWN when `TASK_100` showed the
"contradiction" was manufactured**). **If another task is in flight when you
finish, state what you found and what you started from and leave the
reconciliation to the manager.** The calls I am least sure of:

1. ⚠⚠ **That `model.py` and the gate can express a leak expectation at all.**
   `sanitizer_expect` has never been used for a leak in this tree. **If
   `check.py::check_sanitizers` cannot distinguish *"LSan fired"* from *"ASan
   fired"* in the way this row needs, that is a gate limitation and it may block
   the row — find it EARLY, before five rungs exist.** `TASK_100` drove a
   synthetic pdir, **not the real gate.**
2. **That the behaviour matrix is enough of an axis to justify a pattern.** Every
   other row here prices something. ⚠ **If `p42` ends up as "the rungs are
   byte-identical and the difference is entirely in whether a `free` exists",
   say whether that is a finding or a non-row** — I think it is a finding, and
   `p24`'s byte-identical result is the precedent, **but I would rather be told
   I am wrong than have a row built to please me.**
3. **That the error path can be driven from a file blob.** 22 of 24 patterns take
   their payload from one. ⚠ **If reaching the error path needs a failed
   allocation or an I/O error rather than a malformed input, the row may not be
   hostable** — settle that in §0, not after building.

Carry **324** forward, incremented by what you find.
