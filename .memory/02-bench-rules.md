# Benchmark construction rules

These rules exist to stop the compiler from evaluating the benchmark away, and to
keep the five rungs comparable. A cell that breaks one of them is invalid data.

## The gate's threat model — settled, do not re-litigate

**The threat is an honest mistake, not a malicious pattern author.** Nobody is
attacking this benchmark; the pattern author, the engineer and the reviewer are
all us. Decided after TASK_010, on the user's call, when six consecutive tasks had
gone to gate hardening and 2 of 47 patterns existed.

The gate demonstrably earns its keep against *accident*. Real accidental defects
it caught, none of them constructed: the retracted O(n) bounds-check claim; a
verified-safe control cell that had never had a consuming ghost assert; five stale
identity digests; `binary_text_bytes` stale in five cells; a results table that had
been silently un-regenerable for two tasks; and the residue trap, stepped in three
separate times.

But the last rounds defended against a *deliberate* author — `unsafe` hidden in a
`macro_rules!`, a `#[cfg]`'d constant making a proof mean two different things.
Those are real holes and the fixes are built and kept, because built machinery
costs nothing to retain. **What changes is the rule for new work:**

> Before hardening the gate again, ask: **could this defect happen by accident?**
> If not, record it as a known residual, name it here, and move on to a pattern.

Known residuals we are deliberately **not** closing, all measured:

- `work_per_call` is unbounded; shrinking it 16× passes with a shout. Nothing
  checks it is denominated in the unit `work_unit_bits` names.
- `twin_justifications` is capped at 1 by a round number, not by an argument.
- A trusted `requires` that is non-trivial, mentions every parameter and is still
  too weak by one is caught only by the verified twin; a trusted `ensures` that is
  *incomplete* with respect to its body's operations is caught only partially, by
  identity plus Miri. Both remain human readings.
- A width change applied to every rung at once is invisible to the driver diff.
- `include!()` of a file outside the module graph escapes the `unsafe` scan.
- `unsafe` anywhere in `common/` is a hard failure with **no hatch**, unlike
  every other structural rule here. Correct today (no rung needs it) and it will
  have to be revisited for the pointer-backed families, p27+.
- The verified twin has never been exercised against a **generic or method-shaped**
  trusted accessor; `vparse.params_text` is documented to hard-fail there and
  nobody has re-measured since TASK_008_REVIEW. p16 is safe (a free `fn` taking
  `&[u8]`); **p17 and beyond may not be** — check it when a pattern first needs
  one, rather than discovering it mid-proof.

A reviewer should still report an adversarial hole it happens to find — it belongs
in this list. It should not become the next task.

## Anti-partial-evaluation

The failure mode: the compiler proves the whole program has a constant result and
emits `mov eax, <answer>; ret`. Then you are timing `printf`.

1. **Every byte of data and every loop bound comes from a file named in `argv`.**
   No compile-time constants, no `const` sizes, no `vec![...]` literals in a
   measured path.
2. **The result is consumed.** The driver folds every kernel return into a running
   checksum and prints it at the end. A result that is never printed is dead code.
3. **The kernel is opaque in `isolated` mode**: `#[inline(never)]` / `__attribute__((noinline))`,
   separate TU, no LTO. In `whole` mode inlining is allowed *on purpose* — that is
   the point of that mode — and rule 1 is what keeps it honest.
4. **Verify, don't assume.** Every new pattern's build is checked by
   `harness/check.py`. It checks anti-collapse **twice**, because either check
   alone is defeatable:
   - *structurally* — the kernel's disassembly must have a backward branch **or
     a call to a known bulk-memory routine**, a memory operand, and a body above
     a floor. A collapsed kernel usually has none of these, but a kernel that was
     hoisted or CSE'd still has all three. The bulk-memory alternative was added
     at TASK_005: a `memcpy`-shaped kernel has no backward branch of its own —
     measured, gcc `-O3`, 16 instructions, `has_loop=False`, `call memcpy@plt` —
     and the loop is real, it just lives in libc. Requiring a back edge
     false-failed a perfectly healthy p02 kernel *before p02 existed*;
   - *dynamically* — **marginal executed instructions per kernel call**, against
     a floor **derived** from the pattern's own `model.py`. Measured as a
     difference of two callgrind runs of the same binary on the same input with
     only `n_iters` changed (that field is at offset 0 of every input file, so
     the harness can build the probe without the pattern's help). The difference
     cancels the loader and environment terms that make an absolute
     whole-program `Ir` unquotable, and it is **symbol-independent**, so it works
     in `whole` mode where the kernel has no symbol and at `O0` where a rung's
     work lives in `core::iter` symbols rather than in `kernel`.

   **The dynamic floor is not declared in `spec.md`.** It was, until TASK_005,
   and TASK_003_REVIEW's central finding applies to it exactly: a pin that the
   pattern author writes moves with the code it constrains, so weakening it costs
   one extra edit in the same commit. (p01's was 400 against a measured minimum
   of 915 — 0.80 Ir per element against 1.83 achieved — so it caught only
   near-total collapse anyway.) Instead `model.py` exposes

       work_per_call -> int   # abstract units of work one kernel call must do
                              # on this input, from the file bytes alone

   and the gate asserts `marginal_Ir >= ALPHA_IR_PER_WORK * work_per_call`, with
   ALPHA a constant in `harness/check.py` — changing it is a harness diff that
   moves all 47 patterns at once. Given **two probe inputs of different shape**
   (`collapse.probe_inputs`) it additionally asserts the marginal rate
   `d(Ir)/d(work) >= ALPHA`, which is the assertion an author cannot satisfy by
   making the kernel do a fixed amount of work regardless of its input. A
   declared `min_marginal_ir_per_call` may still appear and can only *tighten*
   the derived floor.

   Measured on p01 after the TASK_005 barrier swap: marginal Ir 908 … 274 496
   across 56 cell/probe pairs, `d(Ir)/d(work)` 1.75 … 67.00, ALPHA = 0.25.

   **ALPHA = 0.25 Ir per byte is too high, and it forbids the kernel shape we
   want next.** Measured at TASK_004_REVIEW: glibc `memcpy` itself achieves
   **0.104 Ir/byte**, so ALPHA is 2.4× above what the fastest correct
   implementation of a bulk copy can do. A kernel dominated by a bulk copy
   *cannot* satisfy the floor — bare copy + 8-byte fold measures 0.118 Ir/byte
   (0.47× the floor, fails), and the word-wise fold that `p02/NOTES.md` §0
   recommends for future patterns sits at only 1.37× margin. Also, for p02 as
   shipped the floor is cleared by the **fold alone**, so the stage does not
   certify that the copy — the thing the pattern is about — happened at all.

   **Fixed at TASK_006.** ALPHA 0.25 remains the default; a `model.py` may declare
   `min_ir_per_work` with a `min_ir_per_work_why`. Going below the default requires
   the justification (printed on every run via `rep.shout`) **and** two probe shapes
   so the `d(Ir)/d(work)` assertion still runs. p02 declares **0.0625** — the fused
   AVX-512 lower bound: load + store + `vpsadbw` + `vpaddq` per 64-byte lane.

   Note this necessarily *loosens* the absolute floor, and that is correct rather
   than a concession: any sound rate for a byte-denominated unit must sit at or
   below glibc's measured 0.104, so **0.25 was not tight, it was wrong**. Tightness
   now comes from the rate assertion — measured margin 35.9×. Residual risk:
   `min_ir_per_work` is still a number an author writes. It is legitimate under the
   "declared pins must be checkable from `spec.md`/`model.py` prose alone" rule and
   constrained three ways, but nothing mechanically checks that 0.0625 is right.

   **TASK_006_REVIEW measured how weak that residual risk is: the only lower
   bound is `> 0`.** `min_ir_per_work = 1e-9` with `why = "see NOTES.md"` passes
   the whole gate, printing "derived floor 0.0 Ir/call" and "tightest margin
   2246270772.2×". Nothing inspects `why` — it is free text. `work_per_call` is
   a second unbounded knob in the same file, and both move in the same commit as
   the code they constrain, so TASK_003_REVIEW's self-certification argument
   applies verbatim. Even as shipped the margin is 35.9×, i.e. p02 could lose
   97% of its work and still clear the floor.

   **So do not describe this stage as an anti-collapse gate.** It rules out
   total collapse and nothing finer. What certifies that the work happened is
   step 2 — the model checksum. That was already the rule two paragraphs down;
   the measurement above is how much it matters.

   **Partly closed at TASK_008, and the new bound has its own problem.**
   `MIN_DECLARABLE_IR_PER_WORK = 0.015625` is a
   hard floor under what any `model.py` may declare (`1e-9` now fails outright),
   the achieved margin is printed beside the declared floor with what it implies,
   and a margin above `LOOSE_FLOOR_MARGIN = 100` shouts. The stage is renamed
   **"NOT-COLLAPSED smoke test"** and its own log now says step 2 is what
   certifies the work happened, so a green line cannot be over-read. p02 prints:
   *"tightest measured margin over it 35.9×, i.e. this stage tolerates a 97.2%
   loss of work before it objects."*

   **`work_per_call` is still unbounded — only made loud.** Shrinking p02's 16×
   still **passes** (margin 576.7×, two shouts, no failure). Bounding it
   mechanically would need the harness to know each pattern's unit of work,
   which is precisely what `model.py` exists to supply, and failing on a large
   margin would turn the floor into a *cap on how good a rung may be* — p01's
   honest margins run 7×–268×. So this knob is a known, documented residual.
   Reproduced at TASK_008_REVIEW, with two details worth keeping: the
   `d(Ir)/d(work)` rate assertion gets **easier** when work shrinks, so it is no
   defence at all; and the second shout is discoverable only by *being there*
   (shipped p02 prints one, the mutant prints two), because its text reads as a
   statement about the floor being loose rather than about `work_per_call` having
   been edited. Honestly documented residual — do not upgrade the claim.

   **`MIN_DECLARABLE_IR_PER_WORK` has no justification hatch, and its derivation
   presumes a unit the kernel touches once per unit.** The below-default path
   accepts a `min_ir_per_work_why`; this bound fires before any justification is
   consulted. The derivation is "4 instructions per 256 bytes", which is a
   statement about *bytes*. `.memory/06-catalogue.md` plans **p09, bit
   vector/bitset** — AVX-512 `vpopcntq` does 512 bits in ~3 instructions =
   **0.0059 Ir per bit**, below the bound, so an honest bit-denominated
   `model.py` is forbidden with no route out. Same shape for any *skipping*
   walker denominated in buffer bytes. Fix the bound before p09, not during it.

   **Fixed at TASK_009, and the fix composes into a third knob.** The bound is now
   `MIN_DECLARABLE_IR_PER_BIT (0.001953125) × model.work_unit_bits`, with a hatch
   (`min_ir_per_work_bound_why`) capped at 64×. p09's bit-denominated shape passes;
   `1e-9` still fails even hatched. But `work_unit_bits` is checked only for
   `>= 1`, so `work_unit_bits = 1` plus the hatch yields an absolute bound of
   **3.05e-5 — 512× below the pre-TASK_009 bound of 0.015625** — from two numbers
   in the same author-written `model.py` that already supplies `min_ir_per_work`
   and `work_per_call`. Nothing checks that `work_per_call` is denominated in the
   unit `work_unit_bits` names. Three composing knobs, one author, one commit.

   **Clamped at TASK_010**: `MIN_DECLARABLE_IR_PER_WORK_ABS = 0.015625/64 =
   0.000244140625` bounds the **composition**, so the reachable absolute floor is
   64× under the byte bound rather than 512×, and the effective absolute floor is
   printed every run. p09's bit-denominated shape still passes; the previously
   legal `work_unit_bits = 1` + hatch combination now fails. The third knob —
   nothing checks that `work_per_call` is denominated in the unit
   `work_unit_bits` names — is bounded only by its product with the other two.
   Documented residual, unchanged.

   **A floor can never certify that a component ran.** p02 clears any rate on its
   *fold* alone, so the stage does not show the copy happened. No rate bound on
   total kernel `Ir` can attribute cost to a part. What actually certifies the copy
   is step 2 — the model checksum folds the copied bytes. Do not ask the floor to
   do a job it structurally cannot.

## Result consumption: keep the full-extent fold (settled by measurement)

p02's result fold is ~96% of kernel cost and the copy ~4%, which looks like the
benchmark measuring its own scaffolding. TASK_004_REVIEW measured the
alternatives and the conclusion is **keep the full fold** — but the reasoning
that was originally written down for it is wrong, so do not propagate that.

- A word-wise fold cuts the kernel 10 200 → 1 399 Ir/call and lifts the copy's
  share 4.2% → ~31%. It cannot go further: **any fold that reads every copied
  byte costs at least what `memcpy` cost to write them**, so the copy caps near
  50%. An `xor` fold measures identically. A cheaper fold is not the lever.
- **The feared side effect does not exist.** The worry was that a narrow fold
  would leave most of the copy dead and let LLVM elide it in `whole` mode.
  Measured with only 8 of 4092 bytes consumed: 484.1 isolated / 472.1 whole, and
  the `memcpy` call is still present in `main` in both. Deleting the copy drops
  it to 58.0 / 0.0. LLVM does not narrow it, because `dst` is a caller-visible
  `&mut [u8]`.
- So the binding constraint on kernel design is **the harness floor above, not
  the optimiser**. Fix the floor rather than redesigning the fold.

When a pattern's scaffolding dominates its kernel, say so at the top of `NOTES.md`
and quote the **marginal** column — never present a whole-kernel delta as the cost
of the thing the pattern is named after.

5. **The barrier is pinned in `spec.md`, not inferred.** Removing the driver's
   anti-collapse barrier is *not* reliably visible in either check above:
   measured at TASK_003, replacing `off = acc % nwin` with `off = 0` in every
   rung leaves p01's marginal `Ir` at ~902/call, because LLVM does not hoist a
   whole inner loop out of an outer one. So the driver loop itself is pinned as
   a canonical token sequence in the pattern's `spec.md`, and every rung — C
   included — is normalised and diffed against **that**, not against each other.
   Diffing the rungs against each other passes happily when the mutation is
   applied to all of them.

## Input files

Format, shared by all patterns (little-endian):

```
offset 0   u64  n_iters       # times the driver calls the kernel
offset 8   u64  payload_len   # bytes following
offset 16  u8[payload_len]    # pattern-defined payload
```

- Generated by `inputs/gen.py` in each pattern dir, **deterministically from a
  fixed seed**, so inputs are reproducible and need not be committed as blobs.
  Commit `gen.py`; gitignore the `.bin`.
- Three cases minimum per pattern:
  - `small` — working set fits L1 (~16 KiB), high iteration count.
  - `large` — working set exceeds L2 (~4 MiB+), memory-bound.
  - `adversarial` — the input that triggers the C bug this pattern models.

## The checksum contract

- Driver accumulates: `acc = acc.wrapping_mul(31).wrapping_add(result)` over every
  kernel call, prints `acc` as a decimal `u64` and nothing else on stdout.
- **All five rungs must print the same checksum for `small` and `large`.** This is
  the correctness gate for the port and it catches silent UB in R1/R4. A pattern
  is not done until `harness/check.py` is green.
- **`adversarial` is exempt from checksum equality** — that is the whole point.
  Instead record the *behaviour* of each rung: exit code, stdout, stderr, and
  whether ASan/UBSan fired (C), whether it panicked (R2/R3), whether it silently
  corrupted (R4), and what the proof rules out (R5). This table is the security
  half of the result.
- **The sanitizer is allowed to fire, and sometimes must.** `model.py` declares
  `sanitizer_expect` per input, `"clean"` or `"fires"`. On a `"clean"` input any
  ASan/UBSan diagnostic is a gate failure and the exit code must match the
  model. On a `"fires"` input **silence is the failure**: if the input that is
  supposed to trigger this pattern's bug does not, the security half of the
  result is unsupported. The exit code is recorded rather than required there,
  because ASan exits 1 by default, aborts (−6) under `abort_on_error`, and a
  UBSan-only diagnostic may not change it at all. Before TASK_005 the gate
  failed on *any* hit on *any* input, which meant the first pattern modelling a
  real memory-safety bug could not be green.

## Kernel/driver split

- The kernel is the pattern. The driver is boilerplate: read file, loop, fold, print.
- **Driver logic must be identical across R2–R5** and behaviourally identical to
  the C driver. Preferred: one shared `common/driver.rs` pulled in with
  `#[path = "..."] mod driver;`, marked `#[verifier::external]` in R5. If that
  fights Verus, duplicate it — but then every copy is diffed **against the
  canonical token sequence pinned in `spec.md`**, never against another copy.
- The C copy is diffed the same way. `harness/dloop.py` normalises both
  languages (types, casts, `wrapping_*` methods, grouping parentheses, Verus
  clauses and ghost statements) to one token sequence; names that genuinely
  differ get an explicit alias table in `spec.md`. **That table renames and can
  do nothing else**: both sides must be a dotted identifier path with an
  optional `()`, so no alias can add, delete or restructure a statement. An
  unconstrained destination — an *empty* one in particular — deletes the
  statement it matches, which is enough to put the M9 prefetch/barrier payload
  back into the measured C loop with two lines of `spec.md` (TASK_003_REVIEW).
  The *set* of files that must carry an `SLB-DRIVER` region is pinned too
  (`driver.regions`), and `harness/dloop.py` raises on a second marker pair:
  otherwise a rung leaves the diff by deleting two comments, or a decoy region
  in a block comment above the real loop is what gets diffed. **Required substrings are not
  a diff**: p01's seven-substring check passed with a `__builtin_prefetch` and
  an `__asm__ __volatile__` memory barrier added to the C driver loop, which is
  precisely the cross-language asymmetry the anti-partial-evaluation rules
  forbid.
- **Ghost statements are exempt from the diff only inside the `verus!` span** —
  not "in Rust". Exactly as `invariant` and `decreases` are. Ghost code erases, so
  an R5 driver that consumes its kernel's `ensures` with an `assert` stays
  byte-identical to R4's — and R5's `ensures` should be consumed, or it is
  decoration that only mutation testing defends.

  Gating this on the *language* was wrong twice. In C, `assert(...)` is live code
  (`harness/build.py` never defines `NDEBUG`) and stripping it deleted a real
  branch from the measured loop while the diff still passed (TASK_003_REVIEW). In
  plain Rust it reopened the same M9 payload (TASK_004): `assert!(...)`,
  `let ghost = black_box(...)` and `let ghost = unsafe { _mm_prefetch(...) }` each
  normalised to the canonical sequence, kept the statement count, printed the
  right checksum, and cost 2–10 Ir/call. **`assert!` is live code in release
  Rust** — `-C debug-assertions=off` removes only `debug_assert!` — and
  `let ghost` admits an arbitrary expression including an `unsafe` block.
  `dloop.normalise()` now takes `in_verus`, defaults it `False` (fail-closed),
  refuses `in_verus=True` for C, and requires the region to sit inside
  `verus! { }` *and* inside a non-`external` item.

  **And `verus!` must be *Verus's* macro, not one the rung defines.** TASK_006_REVIEW
  put the M9 prefetch payload back into `safe_naive.rs`'s measured loop with a
  three-line `macro_rules! verus { ($($t:tt)*) => { $($t)* } }` and `verus!( ... )`
  — round brackets. `vparse.py` accepted `verus!\s*[{(\[]`, `check.py`'s
  "a file with a `verus!` block must appear in `verus.obligations`" guard matched
  only `verus!\s*\{`, and the one-character gap between the two regexes was the
  whole bypass: full green gate, `contract sha256` **identical** to the shipped
  pattern, +5 Ir/call, `prefetch` in the disassembly. A rung that is not compiled
  by Verus must never reach the ghost-stripping path — the correct test is
  "was this file verified by Verus", which is a fact the gate already has, not a
  regex over the source. Payloads inside a *genuine* `verus!` span are safe:
  Verus itself rejects all three (`assert!` → *"panic is not supported"*,
  `let ghost = <expr>` → parse error), so the harbour is sound when it is real.

  **Closed at TASK_008, semantically and fail-closed.**
  `dloop.normalise_file(..., verus_verified=)` raises `GhostHarbourError` when a
  region *claims* a `verus!` span without the caller's certificate, and
  `check.py::_verus_verified_files` issues that certificate only from Verus's own
  verdict: the file is in `verus.obligations` **and** stage 5a got `N verified,
  0 errors`, **and** `--verify-function <the item enclosing the region>
  --verify-root` reports a verified body for that item. `region_in_verus` is now
  documented as a *claim*, not a licence. All three bracket forms fail, and so
  does a fourth variant that also declares the rung in `verus.obligations` to
  dodge the pin guard — Verus refuses the file, so no certificate is issued.
  The gate now names the harbour in its log: *"ghost statements excluded in
  ['verus.rs'] — the only file(s) Verus itself verified this run"*. The regexes
  were reconciled too, but that is hygiene, not the fix.

  Independently re-attacked at TASK_008_REVIEW along four routes (paren, bracket,
  brace, and a variant that also declares the rung in `verus.obligations` to dodge
  the pin guard) — **all four fail**, as does an `external_body main`. One rough
  edge: the certificate is denied for a driver region inside a `mod`, because
  `--verify-function <name> --verify-root` cannot resolve a mod-nested function
  (*"could not find function"*), and the resulting message says *"the item
  enclosing the region has no verified body"*, which is false. Fail-closed but
  misattributed; it will bite the first pattern that puts its driver in a
  submodule. An `impl` method resolves fine. Also worth knowing: Verus itself
  does **not** object to two items sharing a name (`S::drive` and `inner::drive`
  → `--verify-function drive` silently reports `1 verified`), so `vparse`'s
  text-level duplicate-name failure is the only thing standing between the
  certificate and the wrong item.
- Kernel signature is fixed per pattern in the pattern's `spec.md`, and all five
  rungs implement exactly that contract.

## Miri policy

**Miri is mandatory for any pattern where R4 and R5 are not byte-identical**, and
only then. The reason is precise: the project's claim about R4 is that it is the
same machine code as the rung whose obligations were discharged. When the two
kernels are byte-identical, R4 inherits R5's proof exactly and a UB check adds
nothing.

**This policy needs revisiting, and TASK_009_REVIEW is why.** "R4 inherits R5's
proof" is only as good as R5's proof, and R5's trusted `ensures` need not be
**complete** with respect to the operations its trusted body performs. Measured:
`unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }` passes the
whole gate with the contract, the twin and the pins unchanged — nothing licenses
the `i + 1` read, and no Verus stage can see it, because the twin only has to
satisfy the `ensures` and the `ensures` never mentions it. **Miri is the only
backstop for that class, and this policy makes it optional exactly when
byte-identity holds** — i.e. exactly in the case the project reports as its
headline result. So the argument "identical machine code, therefore no UB check
needed" is sound about *codegen* and unsound about *the trusted base*.

**Changed at TASK_010: Miri is now derived, not declared.** It is required
whenever the pattern has any trusted item at all, `check.py` reads that from
`verus.rs` rather than from `spec.md`, and `miri.required: false` beside a trusted
item is a hard failure. The identity rule survives only as the reason it can never
be skipped when R4 ≠ R5. Cost of the change: p01 is now
`PASS-WITH-BLOCKED-ROWS` — Miri does not finish `large.bin` inside 180 s, so 8 of
9 inputs are checked and the ninth is a documented blocked row.

**And the measured answer to "does Miri catch the incomplete-`ensures` case" is
no — something else does.** Two distinct sub-cases, both measured at TASK_010:

- **R5-only drift** (the extra `i + 1` read added to `verus.rs` alone): Miri
  reports *no UB on all 9 inputs*, because `miri.sources` names **R4's** source
  and the mutation is in R5's trusted body. What catches it is **stage 3c
  identity** — `unsafe vs verus at O3: identity dropped to 'differ'`,
  `md5_fn 0e5b59364bb6 vs 1118d7679708`. So the byte-identity result is itself
  load-bearing as a *check*, not merely a finding.
- **The identical-code case** (the same extra read in `unsafe.rs` *and*
  `verus.rs`, which identity cannot see): **Miri does catch it**, on 1 of 9 p02
  inputs — `adversarial-cap.bin`, *"Undefined Behavior: `assume` called with
  `false`"*. Only that one, because it is the input where `len == dst.len()`.

So the class has a backstop, but a **two-part and partial** one: identity for
R5-only drift, Miri for the identical-code case, and Miri only on inputs that
actually reach the boundary. Neither is a proof that a trusted `ensures` is
complete. That remains a human reading — see the `SLB-TRUSTED-ARGUMENT`
requirement in `.memory/04-verus.md`. When they are not, R4 is unverified unsafe code that 47 patterns will
imitate, and nothing has checked it.

`harness/check.py` step 8 wires this. Three details, all settled at TASK_005
because between them they made the first pattern with a non-trivial proof
un-greenable by any route:

- **The threshold is `norel`, not `exact`.** `norel` means byte-identical once
  pc-relative displacement *fields* are zeroed — the same machine code linked at
  a different address. p01's own `spec.md` says exactly that about its `O0` row.
  A `call rel32` to a callee that moved is not a semantic difference and must
  not make Miri mandatory.
- **Miri is installed and actually run.** On a `nightly` toolchain beside the
  pinned one (`rustup toolchain install nightly --component miri`; see
  `TOOLCHAIN.md`). This is sound because R4 is plain unsafe Rust with **no vstd
  dependency**, and because Miri checks *source* for UB — it does not measure
  codegen, and no number in `results/` comes from it, so the toolchain
  difference is not a confound. The gate rewrites `n_iters` to 4 (Miri is
  ~1000× slower than native), runs the R4 source on **every** input including
  the adversarial ones, and checks the printed checksum against `model.py`.
  Confirmed load-bearing: R4 with its index shifted by 1600 reports
  `Undefined Behavior` and fails the stage.
- **A missing tool blocks a row, it does not fail the pattern.** If Miri cannot
  be run, the gate records a *documented failure for that row* with the
  `miri.blocked_reason` `spec.md` pins, prints it in the verdict, and the
  verdict becomes `PASS-WITH-BLOCKED-ROWS`. Failing a whole pattern on a tool
  the box does not have is how gates get switched off.

**Sizing inputs so Miri does not block the row — measured at TASK_010_REVIEW.**
Miri's cost is driven by the **payload the kernel folds**, not by the file size,
and `n_iters` is *not* the knob: `check.py:3819` rewrites it to
`MIRI_PROBE_ITERS = 4` for every Miri run, discarding whatever the pattern
declared. Measured fold throughput on this box: **5.91e-5 s per folded byte
(~16 900 B/s)**, so the 180 s budget is ≈ **3.05 M folded bytes**, i.e. a stride
of **≤ ~760 KiB per call** at 4 iterations. Size `inputs/gen.py` against that
*before* building.

Why p01 blocks and p02 does not, which is not a size story: p02's 8.38 MB
`large.bin` finishes in **1.5 s**. p01 blocks because `common/driver.rs`'s
`head_u64_body` decodes the payload **element by element** (1.5 M `le64` +
`push`) under the interpreter, while `head2_u64_bytes` / `head1_u64_bytes` are a
single `to_vec()`. **The payload decoder you pick in `common/` decides whether
your rows are Miri-checkable** — prefer a bulk `to_vec` shape.

The pair to compare is `miri.pair` in `spec.md`, not a hard-coded
`"unsafe vs verus"` string. Miri is a UB **test**, not a proof: it says nothing
about paths the probe inputs do not take, which is why the policy is "mandatory
when R4 ≠ R5" rather than "sufficient".

**Miri is no backstop at all for a too-weak trusted `requires`** — not a partial
one. `miri.sources` names **R4's** `unsafe.rs`; a weakened `requires` lives in
R5's `verus.rs`, which Miri never opens. And a weak precondition does not itself
execute UB, it only fails to forbid it. Established decisively at
TASK_010_REVIEW, and it is the argument for keeping the verified twin.

## A count-bearing `rep.ok` must state its `n`, and must never fire at `n == 0`

Promoted to a rule at TASK_010, after the shape was found **four** times and only
one instance had been caught by review. The pattern: a stage prints
*"every X is Y"* over an empty collection and the run goes green. Instances:

- `0 verified twin(s): every trusted `unsafe` item's `requires` is strong
  enough…` with both twins justified away and both known too-weak forms shipped
  (found by TASK_009_REVIEW);
- 5c's OK line counted rows *including* the `assert(false)` probe, so it could
  assert "every trusted `ensures` conjunct is load-bearing" over zero conjuncts;
- 5c-req, the same;
- 5d printed only `--` lines and **neither** an `ok` nor a `fail` when every input
  made zero kernel calls.

Two earlier instances of the same family are already recorded above: an empty
`requires` list printing "holds on all 200000 kernel calls", and a model that
returned no samples printing "re-derived on 0 sampled calls".

So: every success line that quantifies over a collection prints the size of that
collection, and a size of zero is a **failure**, not a pass. A vacuous truth in a
gate log reads exactly like a discharged obligation, and that is the single most
repeated defect in this project's history.

## Honesty rules

- Never report a perf number from an `O0` row.
- Never report a C-vs-Rust number without saying which C compiler, and whether a
  same-backend (clang) column exists.
- If a cell fails to build, verify, or agree on checksum, it is recorded as a
  failure in the results table. **Do not quietly drop it.** A missing cell that
  looks like an omission is worse than a documented failure.
- If a rung is impossible for a pattern (e.g. R5 defeated by a proof obligation),
  record *where it got stuck*. That is a finding, not a gap.

## The precondition must be structural. The attack must be data.

Settled at TASK_003_REVIEW, which found the rule below collides head-on with any
pattern that models a real bug: rule 1 says every measured input must satisfy R5's
`requires`, but a pattern's adversarial input *is* the precondition violation. p01
hid this because its adversarial inputs make zero kernel calls.

The resolution is not to exempt adversarial inputs. It is to write the contract
correctly:

- **`requires` states only structural facts** — the slices exist, the offsets are
  in range, the buffer capacities are what they are. These hold on *every* input
  the benchmark runs, adversarial included.
- **The attacker-controlled quantity is an argument, not an assumption.** A
  length prefix read from the payload is data. The kernel must handle every value
  it can take.
- **The security property lives in the `ensures`** — "no byte outside `dst` is
  written", "the return reflects only bytes inside the buffer", "the parse either
  rejects or returns an in-bounds span".

A kernel whose `requires` excludes the attack input has not solved the problem, it
has assumed it away — and it will verify, and the gate will pass it, and the
result will be worthless. This is the same failure as the pilot's `requires n <
1000`: a precondition narrow enough to make the proof easy is a precondition that
no caller can discharge.

Corollary for the C rungs: R1 omits the check (that is the bug being modelled) and
**R1h**, the hardened C cell, includes it. R1-vs-R1h isolates what the check costs
inside one language, so "C is faster" and "C is unsafe" stop being confounded.
Built at TASK_004 on p02 and now a standard optional cell — see
`.memory/01-ladder.md`. Measured there: the check is +5 (gcc) / +12 (clang)
instructions per call, flat in the size of the copy.

### Worked example: what this looks like in practice (p02)

The whole contract, for a kernel that copies a length-prefixed record into a
fixed buffer:

```
requires  src_off + 2 <= src_len                       <- structural, holds on every input
ensures   result   == copy_sum(src, src_off, dst_len)  <- the value
          dst_after == copy_dst(dst_before, src, src_off)   <- THE SECURITY PROPERTY
          dst_after_len == dst_len
```

Two things to copy from it:

- The `requires` says only "the two prefix bytes are inside the source". The
  attacker's `u16` length is an *argument*; the kernel is total in all 65 536
  values it can take, and the gate evaluates the precondition at every call on
  every input, adversarial included.
- The security clause is an equality on the **whole** destination sequence, not
  a property of the copied prefix. `copy_dst` is "the record, followed by the
  bytes that were already there" — so one clause says both "the copy is correct"
  and "nothing outside `dst[0..len)` moved", and on a record that does not fit
  it is the identity, i.e. *nothing at all was written*. Stating it over the
  prefix only would have proved the easy half.

And one thing to avoid: p02's spec functions are named in the `ensures` and
mirrored as Python helpers in `model.py`, because the gate evaluates the derived
contract with `eval` and a `forall|j: int| ...` does not translate. Push
quantifiers into a spec function and give `model.py` an independent
implementation of it.

## Proof domain must cover the measured domain

The pilot failed all four of these; TASK_001_REVIEW caught it. Its R5 kernel
carries `requires n < 1000` and `ensures r < 1000*1000`, its only call site is
inside `#[verifier::external_body] fn main`, and the published run at n = 50 000
printed `24975000` — a value its own postcondition declares impossible. The
machine code was fine; the *label* was indefensible.

1. **Every input a rung-5 cell is measured on must satisfy that cell's `requires`.**
   An R5 number produced outside the verified domain is R4's number wearing R5's
   label. Record it as an R4 row, or not at all. **"Every input" includes the
   `adversarial` ones.** The gate used to build its model set from the
   non-adversarial inputs only; p01 hid that because its adversarial inputs make
   zero kernel calls, but for most patterns the adversarial input is *by
   construction* the one aimed at the precondition, so it is the single most
   important input to evaluate this rule on.
2. **A rung-5 cell needs at least one *verified* call site.** If the kernel is only
   reachable from `#[verifier::external_body] fn main`, no precondition is ever
   discharged and the proof is decorative — it verifies, and constrains nothing.
   The driver's call into the kernel must be inside `verus!` and must verify. Only
   the argument-*reading* helper may be `external_body`, and its `ensures` must
   supply exactly the facts the kernel's `requires` needs.
3. **The `ensures` must hold on every measured run.** If the largest measured input
   falsifies a postcondition, the cell is invalid — not footnoted.
4. **`harness/check.py` enforces 1–3 per cell.** It reads the kernel's
   `requires`/`ensures` from `spec.md`, drives the pattern's own `model.py` over
   **every** input file, and evaluates the contract at every call the benchmark
   actually makes. A pattern whose R5 precondition cannot cover `large` is a
   documented failure, not a silently narrowed table.

Rule 2 is the one that matters: verifying a function proves nothing if nothing has
to satisfy its preconditions.

### How the gate enforces rule 2 — and why not with a regex

Rewritten at TASK_003 after a reviewer put an `#[verifier::external_body] fn main`
past the gate with **one blank line** (the attribute scan read
`prefix.split("\n\n")[-1]`). Three independent mechanisms now, because each
catches a different spelling of the same defect:

- **The obligation count is pinned in `spec.md`.** `external_body main` drops
  p01's count 5 → 3, and so does most tampering. **Know what it measures, or it
  will mislead you**: TASK_003_REVIEW derived it as *one Verus query per
  function, plus one per loop body*, i.e. a checksum over the function/loop
  skeleton. It is therefore invariant under exactly the semantic weakenings it
  was introduced to catch — a deleted `requires`, a tautological `ensures` — and
  it moves on benign refactors that add or remove a function or a loop. An
  unchanged count is not evidence of anything. (It also answers the open
  question of why `--verify-function main --verify-root` reports 2: the second
  query is the driver's loop body.)
- **Every item's `external` attribute, `requires` and `ensures` is pinned in
  `spec.md` and diffed** (`harness/vparse.py`), as is the item *set*. This is the
  only mechanical defence against the two mutations that leave "N verified, 0
  errors" completely unchanged: a tautological `ensures`, and a `requires`
  deleted from an `external_body` wrapper (`.memory/04-verus.md`). `vparse`
  returns a **list**: two items with one name is a hard failure, because
  whichever one the gate keeps supplies the pinned contract for whichever one
  the compiler keeps, and nothing says those are the same one. A pinned item
  must also be inside `verus! {}` and must not be `#[cfg]`-gated.
- **Verus is asked, not inspected.** `verus <file> --verify-function main
  --verify-root` reports `0 verified` when `main` has no verified body, and ≥1
  when it does. That is a semantic answer to a semantic question, and no
  attribute spelling defeats it.
- **A trusted `unsafe` item must demand something of its callers.** Structural,
  not a pin: an `#[verifier::external_body]` item whose body contains `unsafe`
  and whose `requires` is empty is an axiom that the unchecked operation is
  always defined. `spec.md` may carry a per-item justification string instead,
  and the gate prints it in the verdict on every run.

Every pattern therefore ships two more files beside its sources:
`model.py` (the independent reference implementation the gate drives — the model
used to be hard-coded into `check.py`, which would have forced 47 forks) and the
`slb-contract` block in `spec.md` carrying all of the pins above.

### Which pins are legitimate — the rule, after TASK_003_REVIEW

That review demonstrated, with a full green gate, that R5's trusted base can be
made to axiomatise "reading any index of any slice is defined and yields
`v@[i]`" by editing three lines of `verus.rs` and three of `spec.md` **in the
same commit**. Every declared pin moves with the code it constrains, and the
obligation count cannot backstop it (see above). The rule adopted at TASK_005:

> **A declared pin is acceptable only for something a reviewer can check by
> reading `spec.md` alone. Everything else is derived.**

Legitimate declared pins: which input file to probe, which files carry a driver
region, the canonical driver token sequence, the alias table, the identity level
expected of a pair. All of those a reviewer can read and judge without opening
the source.

Derived instead: the anti-collapse floor (from `model.py`'s `work_per_call`
times a harness constant); the Python `requires`/`ensures` the gate evaluates
(generated from `verus.rs`'s own clause text through a declared, reviewed
`verus.translate` table, so the two transcriptions of one predicate cannot
drift apart); the structural rule on trusted `unsafe` items. `check.py`'s Miri
cross-check — a declared value tested against a *measured* one — is the model to
copy.

The gate also **hashes the `slb-contract` block** into `results/gate/*.json`
along with a sha256 of every source it read, so weakening a pin shows up in
review as a change to the committed artefact rather than only as a source diff.

### Open gaps in the driver diff, as of TASK_005

- **`driver.regions` pins a *file*, never the code that executes — and this is
  the sixth demonstrated bypass, in both languages.** Move a rung's
  `SLB-DRIVER` markers into a dead decoy function whose body is the canonical
  loop, leave the real loop unmarked, and put a payload in it: **full gate PASS**,
  with stage 6 reporting all five loops match the pin. Demonstrated on
  `safe_naive.rs` (TASK_009, `_mm_prefetch`, marginal Ir O0 6838 → 6852) **and on
  `c/main.c`** (TASK_009_REVIEW, `__builtin_prefetch`, all 32 C cells moved
  +1…+6/call while all four Rust rungs stayed put — a pure cross-language
  asymmetry, exactly what the anti-partial-evaluation rules forbid).
  `check_driver_identity` is language-neutral about *where* the region sits, so
  **this is one mechanism to fix, not two.**

  Two derived fixes, both buildable with machinery that already exists:
  1. **Structural, and it catches both demonstrations**: the pinned kernel item
     may be called **exactly once** in each rung source, and that call must be
     inside the region. A decoy whose body is the canonical loop necessarily
     contains a second kernel call; a real measured loop cannot avoid containing
     one.
  2. **Dynamic**: the gate already runs callgrind twice per cell for the
     marginal-`Ir` probe, and callgrind records caller→callee edges. Assert that
     the callers of the kernel symbol in the `isolated` build are exactly the
     region's enclosing function, and that that function has non-zero `Ir`. A dead
     decoy has zero — that is an operational definition of "executed", measured
     rather than declared, in the same spirit as the Miri cross-check.

  For Rust alone, `_verus_verified_files` already resolves the region's enclosing
  item, so requiring it to equal `driver.call_site` closes that half — but it says
  nothing about C, which is why (1) or (2) is the actual fix.

  **Closed at TASK_010, with both fixes built.** The decoy mirrors now fail twice
  over, structurally and dynamically:

  ```
  [driver] c/main.c: 2 call(s) to the pinned kernel item `kernel()` at line(s)
    [41, 74], 1 of them inside the SLB-DRIVER region (lines 31-45).
  [driver] c-gcc O3 isolated on small.bin: `c/main.c`'s SLB-DRIVER region sits in
    `slb_decoy`, which executed **0 instructions** in this run
  ```

  The dynamic half reuses the callgrind profiles stage 3b already writes, so it
  costs nothing extra, and it is the project's second *measured* answer to a
  question that had been declared (the first being the Miri cross-check). The
  shipped patterns report `the one call to kernel() … inside the pinned region`
  and `in 16 / 14 isolated cell(s) … non-zero exclusive Ir and is the only caller
  of the kernel symbol`.

  Two soft edges, recorded rather than fixed: `--cells measured` skips sources
  with no built cell, so the dynamic count drops without a failure (that run is
  already `PARTIAL`); and `_enclosing_fn` for C is a brace walk rather than a
  parser — correct for a top-level definition, which is the only shape a region
  can sit in today, and it fails closed on anything else.
- **Casts are erased, so a width change applied to *every* rung at once is
  invisible.** `harness/dloop.py` must erase casts or `(size_t)(acc % nwin)` and
  `(acc % nwin) as usize` never reconcile, and then there is no cross-language
  diff at all. A change to one language shows up as a checksum divergence; a
  change to all of them shows up as neither. Not fixed.
- **Grouping is erased** for the same reason (`a * 31 + r` vs `a * (31 + r)`),
  but the checksum stage catches that one instantly.
- `results/gate/<pattern>.json` is the record of the last *complete* run, pass
  or fail, so a failing run does replace a passing one. Since TASK_005 it
  carries a sha256 of the contract block and of every source the gate read, so a
  stale record is at least detectable by comparing hashes against the tree.
  **But the record itself is not byte-reproducible** (TASK_010_REVIEW): a clean
  re-run on an unchanged tree differs by ~3 lines, because the `diagnostic`
  fields carry ASan PIDs and ASLR-dependent addresses. So `git diff` on a gate
  record cannot be read as "something changed" — compare the hashes and the
  verdict, not the file.

### The reference model may not run the thing under test

`model.py` is imported and driven inside an audit-hook sandbox that blocks
`subprocess`, `os.exec*`, `ctypes` and sockets, and `check.py` refuses to load a
model whose source so much as mentions them. A model whose `checksum` shells out
to the built C binary passes step 2 by construction, and the log reports the
checksum was "re-derived" (TASK_003_REVIEW). Step 2 is the gate's only
load-bearing correctness check.

Vacuity in the same stage is a failure, not evidence: an empty `requires` list
used to print "holds on all 200000 kernel calls", and a model that returned no
samples printed "re-derived on 0 sampled calls". Both now fail.

### `--skip` cannot skip an adversarial input

`check.py --skip <stem>` refuses any `adversarial*` stem outright — skipping
them un-checks the proof-domain rules while the verdict still reads PASS, which
is blocker B3 re-opened from the command line. Any other skip forces the verdict
to `PARTIAL` (exit 2), a banner, and a separate `*.partial.json`, never the
full-run record. `--no-build` additionally fails if any binary is older than the
newest source file.
