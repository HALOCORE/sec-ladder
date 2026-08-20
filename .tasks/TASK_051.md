# TASK_051 — p18, LEB128: a bug whose only catcher is a build flag this project has never measured

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then `.memory/01-ladder.md` — **finding 16 (p14)** and **finding 15 (p06)**, both
of which you built, plus **finding 11 (p09)** and **finding 5 (p17)** — then
`.memory/02-bench-rules.md` (**the new "never compare COST on an input where the
unhardened rung commits UB" section**, and the threshold table),
`.memory/03-measurement.md` (**the new null-control section**, the hold-out rank
rule, trap 3's dynamic half, the layout modes at `:789-921`),
`.memory/04-verus.md`, then **`patterns/p14-field-split/` in full** — p14 is the
template you clone. Where this spec is silent, **do what p14 did.**

## §0 — settle the bug class first, again

**Four patterns have now overturned their own catalogue row** (p07, p06, p14,
and p13 in part), and on p14 you rejected all four candidates you were handed.
`.memory/06-catalogue.md` says p18's class is *"unbounded shift, truncation"*.
**Treat that as a prior.** §0's deliverable is the same as p14's: a written
decision in `NOTES.md` §0 naming the bug, the wire format, what it does in each
cell, and **why the rejected candidates were rejected**.

## Why I think p18 is the right next pattern — and where it might collapse

A LEB128 / varint decoder: `val |= (b & 0x7f) << shift; shift += 7;`. Drop the
`shift < 64` guard and a hostile 10-byte varint shifts past the width.

**1. It is the first bug here that is UB but NOT a memory-safety bug.** Every
bug this project models is spatial (OOB read/write) or logical. An oversized
shift is undefined behaviour that touches no memory: C's `<<` is UB by the
standard, x86's `shl` masks the count to 6 bits in practice, so the program
computes a **silently wrong integer** and keeps going. **Nothing in the ladder's
usual toolkit sees it** — not ASan, not Miri on the Rust side, not a
memory-safety proof.

**2. And here is the thing that makes it worth building — I checked this in the
tree before writing it.** In Rust, an oversized shift is caught by
**`debug-assertions`** and by nothing else. **Every measured cell in this project
has `debug-assertions=off`** (`build.py:143-148`; `OPTS = ["O0", "O3"]`). There
is a third mode, **`O0d`**, that turns them on — it has existed since p01, it is
documented as "not in the default 24", and **it has never been measured on any
pattern** (`p01/NOTES.md:697`).

> So p18 is plausibly the pattern where **the safety net exists in the toolchain
> and every column this project publishes has it switched off** — and `O0d`
> finally has a reason to be measured.

⚠ **State it honestly if it holds**: the claim is *not* "safe Rust does not catch
it". It is "the semantics-matched configuration this benchmark measures does not,
and here is what the configuration that does costs." `O0d` is **not**
semantics-matched to C `-O0` (`build.py:26-28`: *"Never compare it to a C
column"*) — so it is a **Rust-vs-Rust** number, and any C comparison drawn from
it is invalid.

**3. Verus should catch it at the other end**, because shift overflow is an
arithmetic precondition. If so, p18 is **p09's mirror**: p09's bug was invisible
to the proof; p18's would be visible to **the proof and to one build flag, and to
nothing else**. That is the sharpest safety-net result available here.

**Where it might collapse, and I want this settled in §0 before you build five
rungs:**

- **If rustc's release `<<` is a plain masked shift and `O0d`'s check is a
  panic**, the two Rust columns differ in *behaviour*, not just cost — check
  what that does to the checksum agreement the gate requires across rungs.
  **This is the failure mode most likely to kill the design**: if the O0 and O0d
  Rust cells cannot agree with `model.py` on the same blob, decide whether the
  benign inputs keep `shift < 64` so all columns agree and the divergence is
  confined to the adversarial rows. That is p13's and p06's shape and it is
  probably the answer, but **measure it, do not assume it.**
- **If C's `shl` masking is not stable across gcc and clang at both opt levels**,
  the "silently wrong integer" claim is really "one legal outcome of UB" — which
  is p14's lesson (*one source, one input, four builds, three answers*). Run all
  eight cells before writing a word about it.
- **If Verus does not catch it**, item 3 evaporates and p18 is a smaller pattern.
  **Run `./verus_run.py` early.** ⚠ And do not attribute anything to the prover
  without running it — that mechanism is real *and* is the most available wrong
  explanation on this project.

**The truncation half** (a varint encoding more than 64 bits' worth) is a second,
memory-safe, wrong-answer bug of p17's shape. Take it if one wire format carries
both, the way p09 and p07 each carry two; drop it if it dilutes.

## What p18 must have regardless

- **Settle whether `O0d` is a rung, a control, or a reported axis** — and say
  which. It is not in the 24-cell matrix, so shipping it changes what the gate
  covers. **If `harness/` would need a change, STOP and report it** rather than
  making one.
- **A per-call scratch/accumulator discipline** that keeps the driver's repeat
  protocol honest — p14's §0 measured what happens when a kernel is not a
  function of its arguments, and the failure is silent.
- **Two in-contract R3 spellings, and quote the cheaper** (finding 3). p06 was
  the fourth pattern to get this wrong. And **check the panic pads before calling
  any per-byte term a safety cost** — p06's 2.00 Ir/byte contained none.
- **A length-heterogeneous sweep, and report the design's rank after dropping
  each band.** A hold-out on a full-rank design cannot fail; p13 and p14 both
  shipped one that couldn't. p06's can, and that is the standard.
- **Attribute every per-iteration `Ir` law mnemonic by mnemonic** before naming
  it after a mechanism — executed alignment padding has landed inside a published
  law three times now.
- **No `ns` claim without a layout population.** The R4/R5 pair is a **smoke
  alarm, not a floor** (`.memory/03-measurement.md`); `controls/clayout.py` ships
  on p06 and p14 — port it.
- **Price every scoped idiom entry**, and run the direction test in writing on
  any declaration edit. If an entry gets added *in response to* a measurement,
  disclose it the way p14 did — that disclosure was reviewed and upheld.

## Verus

Budget **one session**. A stalled proof reported with its exact error IS the
deliverable. Catalogue rates p18 easy–moderate, so a stall would itself be
informative. **TCB: one number plus the U-license / V-gap / infra
classification** (`.memory/04-verus.md`); p14 was its first use on a new pattern
and it survived review. Check `~/tools/verus/vstd/std_specs/` before recording
"no spec exists" — that claim was false for `copy_from_slice` and stood from
TASK_004 to TASK_048.

## Done when

The p14 checklist, plus §0's decision. Complete green `check.py p18`; checksums
against an independent `model.py`; adversarial rows **per rung** with distinct
harms in distinct columns; the `idiom` block written **before** the cells, every
entry backticked, shared paragraph byte-identical; sweep with its fitter
committed under `controls/`; **both** R3 numbers published with the input named;
two proof mutants failing the gate; TCB equal to the gate's own `tcb_items`.

## Constraints

No root; no `/tmp` (scratch `.temp/p18/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`; **do not touch `harness/` or `common/` — if p18
seems to need a change there, STOP and report it.** ⚠ That constraint is more
likely to bite here than usual: `O0d` sits outside the 24-cell matrix, and the
temptation will be to widen the harness. Report it instead. Do not edit any
existing pattern's sources. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **Measurements in the
FOREGROUND, interleaved by cell.** ⚠ **Per-PID scratch paths** — a shared path
corrupted a whole sweep on p14. ⚠ `check.py` rewrites its pattern's gate JSON.
`harness/measure.py --check-stale` after measuring. Delete binaries and blobs
once the gate is green; **keep every generator.**

Notes to `.temp/p18/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Seventy-seven
agents have contradicted the manager and all seventy-seven were right — you
refused a headline I asked for on p14 and gave three independent reasons, and the
rule that came out of it now governs every pattern.

**What I am least sure of is the whole `O0d` framing above.** I checked
`build.py` and `p01/NOTES.md` and I am confident about the *flags*; I have **not**
verified that an oversized shift actually panics under `debug-assertions=on` at
`opt-level=0`, nor that it silently masks at `-O3`, nor that rustc does not
constant-fold the whole thing when the shift count is loop-carried. **Measure
those three before building anything on them.** If the flag does not discriminate,
say so plainly — p18 is then an ordinary UB-without-memory-unsafety pattern,
which is still a first for this project and still worth building.
