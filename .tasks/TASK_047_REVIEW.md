# TASK_047_REVIEW — p06's headline is a WALL-CLOCK claim with no layout population, and R3 is dearer than R2 per byte

**Role:** research reviewer. **You find what is wrong; you do not fix.**
**Read first:** `.tasks/PROTOCOL.md` (the reviewer checklist and the severity
rules), then **`.tasks/TASK_047.md`** (what was asked) and
**`.tasks/TASK_047_REPORT.md`** (what came back), then
`patterns/p06-rotate/NOTES.md` and `spec.md` in full, then `.memory/01-ladder.md`
findings 3, 5, 9, 11, 12 and **the direction-test "IT FIRED" block**,
`.memory/02-bench-rules.md`'s threshold table, `.memory/03-measurement.md`,
`.memory/04-verus.md`, and **the layout modes at `.memory/03-measurement.md:789-921`**
(`win32` / `jcc32`; they are `RECAP.md`'s "finding 16" — ⚠ this line first cited
them to `.memory/05-layout.md`, which is repo layout and naming and contains no
numbered findings at all: the 27th instance of the trap both numbering warnings
exist to prevent, committed by the manager who wrote them).

⚠ **The manager designed p06's kernel, its wire format, its bug and its two
regimes.** PROTOCOL rule 3: designer-validates-own-design is the configuration
this project keeps finding defects in. **Attack the design, not just the
execution.** The engineer already refuted seven of the manager's prescriptions
and was right seven times; assume there is an eighth.

**A green gate is evidence about the gate.** `check.py p06` is PASS on a complete
run with `failures []` and `required_pins_nothing: 0`. Four reviews have found
real defects past exactly that.

## The six things most worth your time

Ranked. Do not pad — **three real blockers beat twenty nitpicks.**

### 1. p06's headline is wall clock, and there is NO layout population

The pattern exists to show that `Ir` misprices a division. Its `Ir` side is
simulator-exact. **Its ns side is the entire result** — `R1h − R1` at
**+19.46% / +57.09% (gcc)** and **+9.78% / +10.56% (clang)** — and the engineer
flagged, against itself, that `controls/wall_span.py` re-implements the
identical-copy floor and the alternating schedule but **not** the `win32` /
`jcc32` mode split, because `common/layout/order.py` knows only the three Rust
cells and p06's headline is **C-vs-C**. Its stated defence is that the effects
are 3–19× the `R5−R4` null — **"an argument, not a measurement"**, its words.

Finding 16 says every layout mode found so far is `win32` or `jcc32` and that
they move wall clock. **Build the population for the C cells, or establish
precisely what stops you and what it would take.** A self-flagged claim is one of
the two highest-yield review targets measured across every review here.

⚠ **And reconcile the two columns arithmetically, which nobody has done.** gcc
`large`: `+95.00 Ir/call` at `+4.74%` ⇒ baseline ≈ 2004 `Ir`/call; the per-record
`Ir` delta is `+1.00`, so ≈ **95 records/call**. `+88.10 ns` ⇒ ≈ **0.93 ns ≈ 2.8
cycles per added divide**. **That is below the documented throughput of an x86
integer divider.** Either the record count is not 95, the divides overlap more
than the divider unit permits, or the ns delta is not measuring the divide.
Baseline is also 2004 `Ir` in ≈463 cycles = **IPC 4.33**, which is high enough to
be worth confirming rather than assuming. **Get the actual records-per-call and
the box's divider numbers and say which of the three it is.** If it does not
reconcile, p06's headline mechanism is not established.

### 2. R3 is DEARER than R2 per byte, and the report does not flag it

`R2 − R4 = 32.00·nrec + 13.00` with **0.00000 Ir/byte**. `R3 − R4 = 2.00000
Ir/byte` exactly. **So the tuned safe rung costs 2 Ir/byte that the naive one
does not**, and on a long record R3 is strictly worse than R2. This is reported
as a fact and never named as an anomaly.

Finding 3 says *always quote R3, because R2 alone overstates safe Rust*. **On
p06 quoting R3 would OVERSTATE the tax and quoting R2 would understate it**, and
that inverts the project's standing reporting rule on this pattern. p09 is the
one prior pattern where R3 was dearer than R2 — **check p06 against it and say
whether it is the same mechanism or a different one.**

Then attack the spelling: **is p06's R3 actually tuned, or is it a badly chosen
spelling wearing R3's label?** The in-contract R3 span is reported as
**+80…+490 (small)**, a 6× range — so the shipped R3 is one point in a wide
class. If a cheaper in-contract R3 removes the 2.00 Ir/byte, the published
figure moves and `.memory/02-bench-rules.md`'s two-number rule applies. ⚠ **Do
not re-ship a rung** — that rule says never — but **price it.**

### 3. The whole `R2 − R4` gap is the HEADER DECODE, not the rotate

`md5_fn(e_revonly) == md5_fn(e_foldonly) == md5_fn(R2)` and
`md5_fn(e_hdronly) == md5_fn(R4)`. Taken at face value: safe Rust's checks in the
three reverse loops and the fold are **byte-identically free**, and every
instruction of p06's safe-vs-unsafe gap lives in the `u32` LE header decode —
which is **not what p06 is about**.

**So: is R2's header decode spelled the same as R4's?** If R4's decode differs by
anything other than a bounds check, the `32.00 Ir/record` is a **spelling
artefact, not a safety tax** — that is p13's blocker 1 wearing different clothes,
and it is the exact shape the direction test was written to catch. Read both
sources, diff the decode, and if it is a real check, **say what check and why the
rotate's checks vanish while the decode's survive.** "It vanished" is not a
mechanism (PROTOCOL rule 11).

### 4. The vstd correction is project-wide and is not yet verified by anyone

The engineer reports that `.memory/04-verus.md`'s *"there is no vstd spec for
`copy_from_slice`"* is **false** at the pinned vstd
(`~/tools/verus/vstd/std_specs/slice.rs:205`), that the real limitation is the
`&mut [u8;64] → &mut [u8]` **range reborrow**, and that `<[T]>::split_at_mut` is
specified with the write-back and **would delete p06's `scr_load` from the TCB**.

**Verify it independently — read the vstd source and re-run the probe** at
`.temp/p06/vstdprobe/`. This decides three things: whether the manager lands a
correction to the layer this project calls authoritative, whether **p02's
`copy_bytes` comment carries the same false claim**, and whether **p06 ships a
trusted item that should not exist**. TCB size is one of the five axes this
project compares, so a removable TCB item is a **blocker**, not hygiene.

⚠ Read the direction-test block's last paragraph before you write this up: the
R4-is-chained-to-the-prover mechanism is real *and* is the most available wrong
explanation here. It cost p13 the magnitude of its headline.

### 5. The `u8` deviation, and whether it changed the pattern's subject

The contract said `u32` elements; p06 ships `u8`, forced (the engineer says) by
the `identity` pin. That is plausibly correct and well argued — **check it
anyway**, because it changes what "rotate" means here and it moves the pattern
onto the one element type with a specialised library path.

- Is `<[u8]>::reverse`'s std implementation specialised (chunked byte-swap)? If
  so, is the **1031 Ir/call** price of excluding `.reverse()` right, and does
  the exclusion still pass the direction test?
- Re-run the `is not supported` claims for `.reverse()`, `.rotate_left()`,
  `chunks_exact`, `try_into`, `from_le_bytes` at the pinned vstd. **Run
  `./verus_run.py`; do not read it off a report.**
- Does `spec.md` document the deviation where a reader meets it, or only in
  `NOTES.md` 10a?

### 6. The mutants, and whether the surviving one survives for the stated reason

`b_scrmod_msonly` verifies **17/0, twin 22/0** and is caught by `spec.md`'s pin
alone. Two things to break: **is the ms-only spec genuinely a memory-safety spec
rather than a vacuous one** (`.memory/04-verus.md`: *panic-freedom ≠
correctness*, and a `requires` nobody can satisfy proves anything), and **is
`r %= SCR` really memory-safe on every input** — including `m == 0`,
`nelem > SCR`, and the `degenerate` blob? One counterexample and the report's
`_msonly` conclusion inverts.

Also confirm the engineer's refutation of the manager's `_msonly` design — that
`b_nored_msonly` *still fails* because a proof quantifies over all inputs. If
that is right it is a general result about this project's mutant machinery and
belongs in `.memory/`; if it is wrong the manager is about to record a falsehood.

## Also check, briefly

- **The `swaps(m,r) = m + [m even AND r odd]` law.** Zero fitted parameters and
  claimed exact on 32/32 blobs. Re-derive it and test one `m` the engineer did
  not sweep. A parameter-free law that holds is strong evidence; one that holds
  *in sample only* is p13's mistake.
- **Regime 1's identity across all eight cells.** The claim that C, safe Rust,
  unsafe Rust and the proved rung all print `12407484466270198528` is p06's
  second-strongest result. Re-run it. Check ASan/UBSan really are clean rather
  than not run, and that the zero-init is what makes it deterministic.
- **`required_absent: 2`.** Confirm both are the bug's own lines and neither is a
  pin that pins nothing under a different name.
- **`m == 0`.** TASK_047 asked for the division-by-zero answer to be decided and
  pinned. Was it, and does the `degenerate` blob actually reach it in every rung?
- **The kernel-exclusive column.** The engineer reports gcc inlines the copy and
  calls no libc routine where clang and Rust call `memcpy`, so cross-compiler
  kernel-exclusive figures are incomparable (p13's blocker 3, second instance).
  Verify the file uses whole-program throughout and says so.
- **`R3 − R4`'s `m mod 8` structure** (α ∈ {3,5,19,22}) is reported per-residue
  and explicitly not explained. Is there a mechanism, or is the reported 2.00
  Ir/byte hiding a step?

## Clean negatives are worth as much as findings

PROTOCOL rule 6. **Name every attack you ran that did NOT land**, so the next
agent does not re-run it. Reviews here have produced results as strong from a
failed attack as from a successful one — p04's headline was *confirmed by a
stronger test than was asked for*, and that is on the record because the reviewer
wrote the negative down.

## Deliverable

**Write `.tasks/TASK_047_REVIEW_REPORT.md` yourself, before your final message**
(PROTOCOL rule 10 — the manager once cited a report that was never created, and
three dangling citations landed in `.memory/`). Findings ranked
`blocker` / `major` / `minor`, each with **file:line and a concrete failure
scenario**, plus the clean-negatives section. Your final message summarises it.

## Constraints

No root; no `/tmp` (scratch `.temp/r47/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, **or `patterns/p06-rotate/` —
you review, you do not fix.** Building controls under `.temp/r47/` is expected
and encouraged; that is how p04's and p13's reviews found what they found.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** Notes to `.temp/r47/NOTES.md` as you go — five agents have died to
transient API errors and none lost work, because the notes survived.

**If a prescription here is wrong, say so with the measurement.** Seventy-one
agents have contradicted the manager and all seventy-one were right — p06's
engineer did it seven times in one task, including on the sign of the pattern's
own headline and on a claim in `.memory/04-verus.md` that had stood since
TASK_004. **What I am least sure of is item 2**: I read "R3 dearer than R2 per
byte" as an anomaly worth a blocker, but it may be the honest behaviour of a
correctly-tuned rung on a kernel whose safe checks are already free — in which
case the finding is that **p06 is the pattern where finding 3's "always quote
R3" gives the wrong answer**, and that is a `.memory/` correction rather than a
defect in the pattern. **Tell me which, with the measurement.**
