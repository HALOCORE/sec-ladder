# TASK_049 — p14, the tokenizer: SETTLE THE BUG CLASS FIRST, then build it

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` — **finding 15 (p06)** in full, plus **finding 9
(p11)**, **finding 14 (p13)** and **finding 7 (p08)** — then
`.memory/02-bench-rules.md` (the threshold table; **p14 is listed there as "not
as stated"** and settling it is part of this task), `.memory/03-measurement.md`
(**trap 3's new dynamic half**, and the layout modes at `:789-921`),
`.memory/04-verus.md` (**the corrected `copy_from_slice` rule and the TCB
accounting section**), then **`patterns/p06-rotate/` in full** — p06 is the
template you clone. Where this spec is silent, **do what p06 did.**

You built p06. p14 reuses its machinery: the per-call scratch copy that keeps the
driver's repeat protocol legal, the order-sensitive full-extent fold, the
whole-program column with per-rung libc call lists, `decreases b` on a
two-cursor loop, and `controls/clayout.py` for any `ns` claim.

## §0 — the bug class is a GUESS, and settling it is the first deliverable

`.memory/06-catalogue.md` says p14's bug class is *"in-place mutation +
aliasing"*. **That row was written before anyone looked at a wire format, and the
catalogue records what happened last time someone built on one: p07's guessed bug
class was wrong by a factor of 2.1e9, and the binding constraint was not the one
the manager named.** p06's was wrong too — "aliasing, permutation invariant"
turned out to be an expressiveness/TCB story plus a fold requirement.

**So the first deliverable is a decision with a measurement behind it, the way
p04's §0 worked.** Do not build five rungs before it. Candidates, with what each
would buy:

1. **The scan that a delimiter does not bound.** No terminator, so the token
   scan runs off the end. Honest, and `.memory/02-bench-rules.md` already
   suspects it reduces to p11's `i < len`. ⚠ **If it does, say so and reject
   it** — p11 exists and a second copy of it is worth little.
2. **Delimiter-run semantics: `strtok` collapses consecutive delimiters,
   `strsep` does not.** Same input, different token count, both memory-safe,
   both "correct" per their man pages. This is p13's shape — a **library
   contract surprise** rather than a missing line — but on *field boundaries*,
   which is a real protocol-parsing vulnerability class (field confusion,
   empty-field injection). It gives a library axis on **semantics**, and p11 and
   p13 already establish how to report one: **name the routine beside every
   rate.**
3. **A token that outlives the buffer it points into.** Every bug this project
   has modelled is spatial or logical; **none is a LIFETIME bug**, and a lifetime
   bug is the one class safe Rust rejects at compile time rather than at run
   time. That would be p08's structural result — "the bug safe Rust cannot
   express" — but *observably* wrong rather than unobservable, which is strictly
   stronger. ⚠ **The hard part is making it fit the harness**: a rung that does
   not compile is not a rung, and the dangling read has to happen *inside* one
   `kernel()` call for the driver's repeat protocol to hold. **If you cannot make
   it fit without contriving the C, reject it and say why** — a contrived R1 is
   the failure mode `PROTOCOL.md`'s checklist calls "Rust-in-C-syntax written to
   lose", pointed the other way.

**My ranking is 2 > 3 > 1, and I hold it loosely.** 2 is the safest good pattern;
3 is the highest-value if it fits, because it opens a bug class the ladder has
never touched. **You have built one of these; I have not built any. If the
measurement says a different one, take it** — and it is legitimate to combine 2
and 3 if one wire format carries both, the way p09 and p07 each carry two bugs.

**Deliverable for §0:** a short written decision in `NOTES.md` §0 naming the bug,
the wire format that expresses it, what it does in each of the eight cells, and
**the reason the other two were rejected**. Then build.

## What p14 must have regardless of which bug wins

- **A per-call scratch copy.** The kernel must not mutate `buf` — the driver
  calls it `n_iters` times and every call must return the same value. p06's
  `spec.md` states this; state it too.
- **An order-sensitive, full-extent fold.** Tokenising is a *partition*, so a
  fold that is insensitive to boundaries cannot see a boundary bug. Fold token
  **count**, token **lengths in order**, and token **content** — p06's finding
  was that a permutation-invariant fold is blind to a permutation bug, and the
  same argument applies one level up. This is the third independent reason for
  the full-extent-fold rule; **say so, and cite the other two.**
- **The load spelled identically in every rung**, with the per-rung libc call
  list published beside every kernel-exclusive figure. gcc inlined p06's copy
  and called no libc routine where clang and Rust called `memcpy`, which made
  the kernel-exclusive column incomparable *across compilers*. Expect it again.
- **R1h.** p14 models a bug, so it ships a hardened C cell.
- **Two in-contract R3 spellings, and quote the cheaper.** `.memory/01-ladder.md`
  finding 3 — **p06 was the fourth pattern to get this wrong and it cost a
  blocker.** Write both from the start. ⚠ And remember what p06 measured: an
  iterator-adaptor R3 can carry a per-byte term that contains **zero bounds
  checks** (`zip`/`Rev` exhaustion tests). **Check the panic pads before calling
  any per-byte term a safety cost.**
- **A sweep whose fit set is length-heterogeneous**, with **leave-one-length-out**
  as the out-of-sample test. p06 shipped the first one and it *can* fail; p13's
  could not fail, provably.
- **Attribute every per-iteration `Ir` law mnemonic by mnemonic before naming it
  after a mechanism.** 23% of one p06 law was executed alignment padding.

## Verus — budget one session, and expect this to be the hard one

The catalogue rates p14 **hard**, the only planned Family-B pattern that is.
The postcondition is a **sequence of tokens** — a `Seq<Seq<u8>>` or a sequence of
(offset, length) pairs — which is a level above p06's rotation. **A stalled proof
reported with its exact Verus error IS the deliverable for that row**
(`.memory/06-catalogue.md`'s proof-effort budget); it is a finding, not a gap,
and this project has never had one.

Land the p06 lessons: `decreases b` on a two-cursor loop; **run `./verus_run.py`
before attributing anything to the prover**; and check
`~/tools/verus/vstd/std_specs/` before recording "no spec exists" — that claim
was false for `copy_from_slice`, propagated into two patterns' comments and one
`.memory/` file, and stood from TASK_004 to TASK_048.

**TCB: one number plus the U-license / V-gap / infra classification**
(`.memory/04-verus.md`, PROVISIONAL). If p14 needs a trusted wrapper, say which
class and why — and check whether R4's spelling is what forces it, which is the
rule p02 and p06 came out on opposite sides of.

## Done when

The p06 checklist, plus §0's decision. Complete green `check.py p14`; checksums
against an independent `model.py`; adversarial rows **per rung** with distinct
harms in distinct columns; the `idiom` block written **before** the cells, every
entry backticked, shared paragraph byte-identical; sweep with its fitter
committed under `controls/`; **both** R3 numbers published with the input named;
two proof mutants failing the gate; TCB equal to the gate's own `tcb_items`.

⚠ **Price every scoped idiom entry.** An entry naming some rungs and not others
silently makes the two sides of the comparison unequal — it cost p13 the
magnitude of its headline. Build the excluded spelling on the excluded rung,
measure what the exclusion is worth, and **publish the price beside the number it
protects.** An entry the *prover* already excludes costs nothing to keep; an
entry only the *declaration* excludes is a fiat, and a fiat is legitimate but
must be priced.

## Constraints

No root; no `/tmp` (scratch `.temp/p14/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p14
seems to need a change there, stop and report it**. Do not edit any existing
pattern's sources. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **Measurements in the
FOREGROUND, interleaved by cell.** `harness/measure.py --check-stale` after
measuring. Delete binaries and blobs once the gate is green; **keep every
generator.** ⚠ `check.py` rewrites its pattern's gate JSON (ASLR addresses); know
which changes are yours before you leave the tree.

Notes to `.temp/p14/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Seventy-three
agents have contradicted the manager and all seventy-three were right — you were
one of them seven times building p06 and twice more landing its review, once on
an accounting scheme I had named as the thing I was least sure of and once on a
reading of the direction test I had argued for at length.

**What I am least sure of here is §0 itself.** I have ranked three bug classes
without having built any of them, and the catalogue's own ranking has now been
wrong on two consecutive patterns. **Treat my ranking as a prior to be
overturned, not a decision to be implemented** — and if the right answer is a
fourth thing I have not listed, that is the best outcome available from this
task.
