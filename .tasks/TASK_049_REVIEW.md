# TASK_049_REVIEW — p14 measured a wall-clock null that may reach back into p06's headline, and its contract has a self-disclosed edit

**Role:** research reviewer. **You find what is wrong; you do not fix.**
**Read first:** `.tasks/PROTOCOL.md` (reviewer checklist, severity rules), then
**`.tasks/TASK_049.md`** (what was asked) and **`.tasks/TASK_049_REPORT.md`**
(what came back), then `patterns/p14-field-split/NOTES.md` **§0 first** and
`spec.md` in full, then `.memory/01-ladder.md` **finding 15 (p06)** and
**findings 7, 9, 14** and **the direction-test "IT FIRED" block**,
`.memory/02-bench-rules.md`'s threshold table, `.memory/03-measurement.md`
(**trap 3's dynamic half; the layout modes at `:789-921`**), `.memory/04-verus.md`
(**the TCB classification, PROVISIONAL**).

⚠ **The manager wrote §0's candidate list and ranked it. The engineer rejected
all four and shipped a fifth.** PROTOCOL rule 3 — attack the *rejections*, not
just what was built. **A wrong rejection means this project skipped a bug class
it could have had**, and rejections are the one kind of claim that leaves no
artefact to inspect.

**A green gate is evidence about the gate.** `check.py p14` is PASS on a complete
run with Miri 8/8 and `identity` holding at both opt levels. Four reviews have
found real defects past exactly that.

## The five things most worth your time

Ranked. **Three real blockers beat twenty nitpicks.**

### 1. The R4/R5 null is 8.97%, and p06 defended its headline against 3%

p14 reports that `verus − unsafe` — **byte-identical kernels, exactly equal
`Ir`** — differ by **+8.97% / +8.91%** in differenced alternating pinned wall
clock over two passes, and correctly publishes **no `ns` claim** as a result.

**p06 measured the same pair at `+3.00% / −1.41%` and used it as the floor its
whole headline clears.** p06's published clang figures are **+9.78% and
+10.56%** — the same order as p14's null. Its gcc figures (+19.46%, +57.09%) are
much larger, and p06 separately survived a 30-layout population at 900/900, so
**the answer is not obvious and I am not asserting p06 is wrong.**

**Measure p06's R4/R5 null with p14's protocol** and say which of these holds:
the null is pattern-dependent and p06's 3% is right for p06; or p06's null was
under-measured and **its clang column does not clear it** (its gcc column and its
layout result would still stand); or p14's 8.97% is an artefact of its own
protocol. **This is the highest-value item in the review** — it is the first
time this project has had two independent measurements of the same null, and
whichever way it falls it changes how every future `ns` claim is floored.

The engineer proposes the R4/R5 pair as **a free null control the project already
has and has never used.** Attack that proposal too: is a byte-identical *kernel*
pair really a null when the surrounding binaries differ?

### 2. §0's four rejections — attack each one

Each is a claim with no shipped artefact:

- **"The catalogue's bug class is EXCLUDED BY THE HARNESS."** The argument is
  that a payload-mutating `strtok` is not a function of its arguments, so the
  checksum stops satisfying `acc(n) = r·Σ31^j` at the first repeat. **Re-run
  `.temp/p14/probe1_repeat.py`.** If true this is a finding about the *harness*,
  not about p14 — it says the driver's repeat protocol makes an entire bug class
  unbuildable — and it belongs in `.memory/`, so it must be right.
- **"Candidate 1 is p11."** Check `k_unbnd` really has p11's loop body and that
  a second copy would have bought nothing.
- **"Candidate 3's R4 would not be a rung."** The stated reason is that pointer
  descriptors make `as_ptr` / `add` / `from_raw_parts` un-provable. ⚠ **This is
  the R4-is-chained-to-the-prover mechanism, which is real AND is the most
  available wrong explanation on this project** — it cost p13 the magnitude of
  its headline, and p06's engineer was wrong about a neighbouring vstd claim that
  had stood since TASK_004. **Run `./verus_run.py` on the spellings yourself.**
  If a provable R4 exists, the ladder's first lifetime bug was rejected for a
  false reason.
- **"Candidate 3 is not observably wrong at `-O3`."** Both compilers print the
  correct answer. Verify — this refutes the manager's own stated ranking.

### 3. A `required` idiom entry was added IN RESPONSE to a gate measurement

`flen = i - s;` went into `spec.md`'s `required` set **because the gate reported
`-O0 identity: differ`**. The engineer disclosed this in the `why` rather than
letting the "written before anything was measured" sentence stand, **and
explicitly asked a reviewer to judge whether the disclosure is adequate.**

This is the direction test's exact shape and it is self-flagged — the two
highest-yield review targets on this project are a claim the engineer flagged
against itself and a mechanism asserted without a control. **Price the entry**
(build the excluded spelling on the excluded rung), **run the direction test in
writing**, and say whether disclosure is sufficient or whether the entry has to
go. p13's precedent: an entry only the *declaration* excludes is a fiat, fiats
are legitimate, **but the price must be published beside the number it
protects.**

Same treatment for **`c_hcond` and `t_pos`, which are out of contract and priced
as the declaration's cost** — the engineer says whether the declaration should
have permitted them is *"a judgement I made, not a measurement."*

### 4. A law with residual exactly 0.0000 — can its hold-out test fail?

`c-gcc-h − c-gcc = 1.00·bytes + 2.00·fields − 3.00` has **max residual 0.0000
over 66 blobs** and **leave-one-length-out worst error 0.0000 over 29
hold-outs**, and predicts both perf rows out of sample.

That is either a genuinely exact law or p13's mistake in a new costume — p13's
out-of-sample test **could not fail, provably**, because every held-out row was a
linear combination of the fit rows. **p06's LOLO could fail** (it missed by
−48.000 at `m=3`). **Establish that p14's can**: find the blob or the domain edge
where it breaks, or show the design's rank makes failure impossible. A law that
cannot be falsified by its own hold-out is not evidence.

Same question for the **zero-parameter fold law** (worst residual 0.0177 over 15
blobs) and for **`verus − unsafe = 0.0000` on all 66 blobs**.

### 5. The corrupted sweep, and whether the re-measurement is complete

The engineer self-reported running two `sweep_ir.py` jobs concurrently on shared
scratch, producing **byte-identical rungs reading 3654 and 11550 Ir/call** — a
plausible-looking table of nonsense. It says everything was re-measured after
making scratch per-PID.

**Spot-check that no number from the corrupted run survived** into `NOTES.md`,
`README.md`, `spec.md` or the results JSON. The engineer's own cross-check ("26
published numbers re-verified against the JSON, 0 mismatches") checks
*consistency*, not *provenance* — both could be corrupt together.

## Also check, briefly

- **`pm3_msonly` shows memory safety ALONE SUFFICES here where it did not on
  p06.** That contrast is a `.memory/`-grade claim. Is the ms-only spec
  non-vacuous, and is the mutant genuinely memory-safe on every input?
- **Band `t`'s new axis** — safety tax `6.456 → 3.506` Ir per line byte at
  **constant input size**, attributed to R4 losing its unroll. Is the mechanism
  controlled, or asserted? (PROTOCOL rule 11.)
- **`4.25 = 2.00 + 2.25` on a fourth kernel**, claimed as the first time both
  halves are in one listing. Verify against p16's original.
- **TCB 6 items = 4 U-license + 2 infra** under the TASK_048 classification,
  which is **PROVISIONAL and has never been reviewed**. This is its first use on
  a new pattern. Does the classification survive contact, and is `scr_load`
  really verified-not-trusted?
- **No layout population was built** and the engineer says the `win32`/`jcc32`
  question is "unasked, not answered". With no `ns` claim published there may be
  nothing to defend — **confirm that no published figure depends on it.**
- **The `-O0` rows are unexplained** (R3 23% dearer than R2, sign inverting at
  `-O3`). Confirm no claim rests on them (PROTOCOL: *any perf claim resting on an
  `O0` row?*).

## Clean negatives are worth as much as findings

PROTOCOL rule 6. **Name every attack that did NOT land.** p06's review is the
model: it built the layout population the report said was missing, the headline
survived 900/900, and that negative is now the strongest evidence p06 has.

## Deliverable

**Write `.tasks/TASK_049_REVIEW_REPORT.md` yourself, before your final message**
(PROTOCOL rule 10). Findings ranked `blocker` / `major` / `minor`, each with
**file:line and a concrete failure scenario**, plus the clean-negatives section.
Your final message summarises it.

## Constraints

No root; no `/tmp` (scratch `.temp/r49/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, **or any pattern — you review,
you do not fix.** ⚠ **Item 1 requires you to MEASURE p06**, which is reading and
building under `.temp/r49/`, not editing `patterns/p06-rotate/`; p06's
`controls/clayout.py` and `controls/wall_span.py` are the tools and
`.temp/r47/repro.sh` rebuilds the review's own artefacts. Building controls under
`.temp/r49/` is expected. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **Measurements in the
FOREGROUND, interleaved by cell.** ⚠ **Use per-PID scratch paths** — the engineer
corrupted a whole sweep by not doing so. ⚠ `check.py` rewrites its pattern's gate
JSON; restore with `git checkout --` and know what you changed. Notes to
`.temp/r49/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Seventy-five
agents have contradicted the manager and all seventy-five were right — p14's
engineer rejected the manager's entire ranked candidate list and refuted the
stated reason for its second choice. **What I am least sure of is item 1's
premise**: I am treating p14's 8.97% and p06's 3.00% as comparable measurements
of the same quantity, and they may simply not be — different kernels, different
binaries, possibly different protocols. **If they are not comparable, say so and
say what the right null is**, because every `ns` claim this project has left will
be floored against whatever you conclude.
