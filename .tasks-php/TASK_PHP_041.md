# TASK_PHP_041 — BUILD `ph53`, **ROW 7** and the first `T3` row

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_041_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR SPECIFICATION IS `TASK_PHP_040_REPORT.md` §5, AND IT IS NOT RESTATED
HERE.** That hunt settled the R1h, verified every C site against the pristine
tarball, wrote the kernel's three-phase C shape, the blob format, the benign
corpus, the `u64`, the adversarial input, the divergence ledger and the
provenance block. **Read §5.1–§5.6 and build to it.** This file carries only the
manager's decisions, the scope and the traps.

⚠ *Two copies of one specification is how both go stale.* **If §5 and this file
disagree, §5 wins on anything technical and this file wins on scope.** Say so if
you find a disagreement.

**Read**, in this order:

1. ⭐⭐ **`.tasks-php/TASK_PHP_040_REPORT.md` in full.** §5 is the brief. **§2 is
   why the R1h is not the one the catalogue names.** §4.3 is a defect it found
   and did not repair. ⭐ **§6 is what it is UNSURE of — read that before
   trusting §5.**
2. `.tasks/PROTOCOL.md` — rules 6, 9, 10, 11, 13, **14**.
3. `.tasks-php/PROTOCOL_PHP.md` — **§A1, §A2/§A2a, §B, §B1, ⭐ §B1a (NEW), §C,
   §F5 and §H all bind.** ⚠ **§B1a landed on 2026-09-12 and no built row has
   been through it** — see §2.4.
4. `.memory-php/` 00–04 **in full** — authoritative, and it **supersedes any
   task report it contradicts, including `_040`'s**.
5. ⭐ `patterns-php/ph45-htmlent-cache-int/` — **the most recent built row**, and
   the closest precedent (a type-axis row whose R4 endpoint was later searched).
   `patterns-php/ph07-strcut-cursor/` remains the conventions template.
   **Read them; do not touch either.**
6. `patterns-php/SOURCES.md` §2 — the tarball read recipe.
7. `patterns-php/CATALOGUE.md`'s `T3` section — ⚠ **and see §2.2 and §2.3: two
   of its statements about `ph53` are WRONG and you must not build to them.**

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`results/`, `pilot/`.** Your writes are `patterns-php/ph53-*/`, `results-php/`
(via the tools) and `.temp/php41/`.
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent session**
edits it.
⚠ **`grep -a` ALWAYS** (F35). **No `until … sleep` poller loops** — foreground
`sleep` is blocked; one tracked background job, wait for its notification.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`14/0`**, first and last.
⚠ **A new row adds TWO measure records, so expect `16/0` at the end** — and the
PAT figure must stay `66/0` throughout. **If your FIRST reading differs, do not
assume damage: check `git log` and report the figure you actually get.**

---

## §1 Why this row matters

**`T3 — initialised before read` has ZERO built rows**, and the type axis has
exactly one (`ph45`, `T1`). 15 of 20 mechanism families are empty and the floor
is 40.

⭐⭐ **And the row's own mechanism is the interesting part: an uninitialised read
that is IN BOUNDS.** CWE-824, not CWE-125 — the slot is inside the reallocated
block and nothing is freed. ▶ **No built row prices that**, and `ph32`
(sized to the *literal*, excess *past* the end) is its cross-reference and
**not** its duplicate.

---

## §2 The manager's decisions

### 2.1 ⚠⚠⚠ THE R1h IS `d09cdd9f71f34deab4b99f4e63523fb94164a724` — **NOT THE SHA THE CORPUS COLUMN GIVES**

**This is the single fact most likely to be got wrong, so it is first.**
`FIXSURVEY_001.md` and the corpus `index.csv` give **`be8daf1f47fa`** (2008).
⛔ **It is EXCLUDED, twice independently** (F94): the pre-image screen says so,
**and** the cited `erealloc` line survives `php-5.0.1`–`php-5.0.4` and is **gone
at `php-5.0.5`** — **2 years 9 months before that commit.**

▶ **Build `kernel_hardened.c` from `d09cdd9f71f3`**, which is **one hunk**:
`erealloc` → `emalloc` + `memset(…, 0, …)`, and it **applies to the pristine
5.0.0 text at zero fuzz**. ⚠ **`spec.md` must cite BOTH shas and say which is
which** (`§F5(iii)`), because the corpus column is evidence a later reader will
find and must not have to re-refute.

⭐⭐ **AND R1h DOES NOT REMOVE THE FAULT — that is the row's sharpest result and
it must be measured, not just asserted.** With the array zeroed and **no
consumer guard**, `QUERY_DEREF` becomes a **deterministic NULL dereference** and
`QUERY_CMP` becomes a **correct no-match**. ▶ **One hunk, two severities. No
built row carries this shape.** **Report R1h's behaviour on the adversarial blob
per consumer, separately.**

### 2.2 ✅ TIER — declare **`narrowed`**, not the catalogue's `verbatim`

`_040` §5.1's table is the reason: the **defect span** lifts byte-identically
(which is why R1h patches onto it), but the *mechanism* needs **three frames in
two files** and two of them do not lift. ⭐ **A tier is a COST STATEMENT, NEVER A
FILTER** (`CATALOGUE.md` §0.2), so declaring `narrowed` **refuses nothing** and
costs only honesty. ⓘ Open item **75** asks whether the catalogue's tiers are
*systematically* optimistic — **two of two examined are wrong in the same
direction.** ▶ **If you form a view while itemising, say so; do not survey.**

### 2.3 ⛔⛔ THE CATALOGUE'S `u64` IS ADDRESS-DEPENDENT AND CANNOT BE USED

`CATALOGUE.md`'s `▸ benign` line for `ph53` says *`u64` = fold of the interface
pointers read*. ⛔ **Pointers are addresses**, so that fold differs between rungs
and between runs **for reasons no rung chose** — which is precisely what the
cross-rung checksum exists to rule out. ▶ **Use `_040` §5.5's `u64`**: every
term is an **index, an id or a count**, plus `php_shim_tally()`. **No address
may enter it.** (Open item **74**.)

### 2.4 ⭐ §B1a IS NEW, AND `ph53` IS THE FIRST ROW THROUGH IT — AND ITS EXCEPTION

`PROTOCOL_PHP.md` **§B1a** landed on 2026-09-12 (open item 54): §B1.2's *"fold
the tally into the `u64`"* is free only at **O(1) allocations per kernel call**,
and `ph64` was the first row where it is O(n).

✅ **`ph53`'s precondition HOLDS** — one `erealloc` per class declaration, and
`FILL`/`QUERY` allocate nothing. ▶ **So `ph53` is the exception §B1a says is
worth remarking on, and its cross-language column needs NO allocator caveat.**
⚠ **Declare the allocation order in `spec.md` anyway** (§B1a.2) — *"declared, so
a reader does not have to re-derive it from `c/kernel.c`."*
⛔ **DO NOT EDIT `common-php/emalloc_shim.h`.** Symlink it into `c/`
unconditionally, `php_shim_reset()` at the top of every kernel call (§B1.3).

### 2.5 ⚠⚠⚠ THE ADMISSION BAR IS **C-SIDE ONLY**, AND THIS ROW WILL TEST IT

`_040` §5.6 **predicts R2 CANNOT BE WRITTEN**: a safe `Vec` cannot have length
*n* with uninitialised elements, so R2 must become `Vec<Option<&Iface>>` — **a
different program.**

▶ ⭐⭐⭐ **THAT IS THE FINDING THIS ROW EXISTS FOR. IT IS NOT A PROBLEM WITH THE
ROW.** *"Safe Rust can't express it"*, *"the program had to change"*, *"there's
no cost gradient"*, *"no column moves"* and *"Miri doesn't see it"* are **ALL
FINDINGS, NEVER KILLS** (`CLAUDE.md` rule 6, `RECAP_PHP.md` finding 53). ⚠ **This
bias produced six of ten real refusals and went uncaught for many sessions
because it lived in the ADMISSION BAR rather than in any row.**

⭐ **And §5.6 makes four LABELLED predictions. Report against each one by name**,
whether it held or not:

| | prediction |
|---|---|
| **R2** | is **PHP 5.2.0's upstream repair reinvented by the type system**, and ≈ R1h in cost |
| **R3** | `push`-as-you-go, **no window at all** — *"the cheapest rung on the row"*, which would be the headline |
| **R4** | LLVM **elides** the `MaybeUninit::uninit()` fill and R4's inner loop is byte-identical to R1's; **if it does not, R4 is DEARER than the C it models** |
| **R5** | needs **no hand-rolled ghost state** — the obligation is literally `forall\|i\| … ==> v[i].mem_contents().is_init()` |

⭐⭐ **R5's SPELLING IS ALREADY SETTLED AGAINST THE PINNED vstd AND IT CONSTRAINS
R4 — do not re-derive it, but DO re-verify it before building on it.**
`MaybeUninit::{new, uninit, assume_init, assume_init_ref, assume_init_mut}` **are
specified** in `~/tools/verus/vstd/std_specs/maybe_uninit.rs`; **`write`,
`assume_init_read`, `Vec::set_len` and `spare_capacity_mut` are NOT.** ▶ So R4's
most natural shape (`with_capacity` + `set_len` + `spare_capacity_mut`) is
**unverifiable at R5** — materialise `MaybeUninit::uninit()` elements and
initialise by **assigning `MaybeUninit::new(x)`, not `slot.write(x)`.**
⚠⚠ **GREP `std_specs/` AND THE INHERENT SPELLING, not `vstd/<mod>.rs`** — that
exact confusion has produced a false *"no spec exists"* claim **twice**
(`CLAUDE.md`). ⚠ **Residual risk `_040` flagged and did not settle**: whether
`Vec`'s `index_mut` carries a **value-level** `ensures`. **Check it first.**

### 2.6 ⚠ WHICH STATISTIC YOUR NUMBERS ARE IN — decided, and the reason is new

▶ **The headline is `A1`** — `kernel_exclusive_ir / n_iters`, **named as family
A** beside every figure.

⭐ **The reason is F91, and it is stronger than the precedent**: on the cells
where two rungs' kernels differ by 1–2 instructions, `|B/A|` is **49.6–393.9×**,
so **no callee-inclusive statistic can resolve a small code difference.** That
is the regime a `fixed-R4 bound` operates in, and it is `harness/check.py`'s own
operative rule (*"for a cross-RUNG comparison use `kernel_exclusive_ir`"*) with a
66-cell census behind it.

⚠ **For the CROSS-LANGUAGE column (R1 vs R2/R3), A is the WRONG statistic**
(F85: 29 of 38 sign flips live there). ▶ **Publish it in `B1` and LABEL IT** —
*"family B, `marginal_ir_per_call`, one draw at `probe_iters [100, 200]`"* —
**and mark it PROVISIONAL pending open item 62 (family C).** ⛔ **Do not publish
a bare C-vs-Rust number.** ⓘ `ph45` already publishes two labelled columns; copy
that shape, not `ph64`'s.

ⓘ **ADJACENT, OPTIONAL, AND ONLY IF THE ROW IS OTHERWISE DONE**: F93 found that
`ph29`'s `[100,200]` span sits on a **start-of-run transient**. **Whether `ph53`
does too is a third data point on open item 69** and the method is one probe over
existing binaries. ⛔ **Do not let it delay the row**, and say `UNTESTED` if you
do not reach it.

---

## §3 ⚠ The traps

1. ⚠⚠⚠ **`grep -a` ALWAYS.** A plain `grep` dispatches to `ugrep`, and on a file
   with **one** non-UTF-8 byte it exits `1` with no stdout and no stderr —
   indistinguishable from *"not present"*. **41 of the corpus's 1 170 `.c`/`.h`
   files.** ⚠ **A probe script does NOT reproduce it**, so you cannot test your
   way out.
2. ⚠ **Read the pristine tarball, never an extracted tree** — 12 trees on this
   box, 8 pristine. `tar -xzOf <tarball> php-5.0.0/<path> | sed -n 'a,bp'`.
3. ⛔ **`inputs/gen.py::_check_arms` must RE-DERIVE coverage from the bytes it
   just wrote** and refuse a corpus missing an arm (§A2a rule 1). *"An intention
   in a comment is what `ph03` had, and it was wrong for a task."* The arms are
   enumerated in `_040` §5.5 — **both arms of `:2570`, four query-loop arms,
   both consumers.**
4. ⛔ **`model.py::selfcheck` must construct its OWN domain** (§A2a rule 2) —
   sweep `n_decl = 0..32` × op orderings, **not** the six `.bin` files. Two
   implementations, must-fire **and** must-NOT-fire controls.
5. ⚠ **The wild pointer must be CHOSEN, not observed.** The shim's size-class
   cache hands a freed block straight back to the next same-class request, so a
   `controls/` probe should **prime** it — write chosen bytes into a same-class
   block, free it, let the `erealloc` pick it up. **A control needs a chosen
   value.**
6. ⚠ **Do not reach for the executor.** *"An extraction that reaches for the
   executor has built a different row"* (`ph49`'s warning, and it applies
   verbatim). **The blob IS the opcode stream.**
7. ⚠ **A `controls/*.py` cloned from another row carries its defects.** Open
   items **57** (`ph16`, two latent) and **63** (`ph29`'s `twin_identical`: two
   `(0, md5(""))` rows still compare **equal**) are both live and **both are in
   the machinery you will clone.** ▶ **Fix them in YOUR copy and say you did;
   do NOT edit `ph16`'s or `ph29`'s.**
8. ⚠ **Keep the generator, delete the artefact** (`CLAUDE.md` constraint 6).
   Binaries, `.o`, `.pyc` and `.bin` blobs under `.temp/` go once your gates are
   green; the `NOTES.md`, probes, sources, `.json` and `.log` stay.
9. ⚠ **`.temp/` is gitignored** — a committed file must not rest a claim on a
   `.temp/` path (open item **65**). **Put numbers in the report.**
10. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match.

---

## §4 Definition of done

1. `patterns-php/ph53-.../` complete: `spec.md` (contract + pins), `model.py`,
   `inputs/gen.py` + blobs, `c/{kernel,kernel_hardened,main}.c` + headers, the
   `emalloc_shim.h` symlink, `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`,
   `verus.rs`, `controls/`, `NOTES.md`, `README.md`.
2. **`harness-php/gate.py` GREEN**, and `harness/measure.py` run — with the
   verdict, `failures`, `complete_run`, `verus_checked`, `problems`,
   `contract_sha256` and the `identity` levels **quoted in the report**, not
   summarised.
3. **Brackets `66/0` and `16/0`** at the end (§0).
4. **Every §2.5 prediction reported by name**, held or not. ⭐ **A refuted
   prediction is a better result than a confirmed one** — say which.
5. **R1h's per-consumer behaviour on the adversarial blob** (§2.1), measured.
6. **Both shas cited in `spec.md`** with which is which (§2.1).
7. ⚠ **What you are UNSURE of, in its own section** (`PROTOCOL.md` DoD 5), and
   ⭐ **`UNTESTED` / `I could not tell` are VALUED ANSWERS** — `_039` shipped a
   negative's failure rather than hide it and `_040` shipped a defect it could
   not fix, and both were the right call.
8. ⚠ **If the row cannot be built as specified, say so with the evidence and
   stop** — ⛔ **but re-read §2.5 first: a Rust-side or Verus-side obstacle is a
   FINDING, not a reason to stop.**
