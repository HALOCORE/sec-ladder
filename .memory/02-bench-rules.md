# Benchmark construction rules

These rules exist to stop the compiler from evaluating the benchmark away, and to
keep the five rungs comparable. A cell that breaks one of them is invalid data.

## Never compare COST on an input where the unhardened rung commits UB

**Asked at TASK_050 and answered against the manager, who wanted to publish
*"hardening is cheaper than the bug"* as p14's headline.** On p14's four
adversarial blobs the hardened C rung really is cheaper than the unhardened one —
by −551, −823 and −611 `Ir` where the law predicted +93, +93 and +429 — and
**the comparison is meaningless**, for three independent reasons in increasing
order of finality:

1. **Semantics.** Past the cap the two cells stop computing the same function:
   the hardened one truncates, the unhardened one keeps going. **The "saving"
   IS the work it refuses to do.** A program is not cheaper for being hardened
   if it is cheaper for returning early — and the checksum column already shows
   they differ.
2. **UB.** The unhardened rung has already stored out of bounds before the extra
   work starts; ASan and UBSan fire on every row. The count is *one legal
   outcome of undefined behaviour*: **one source, one input, four builds, three
   answers.**
3. **Arithmetic — the marginal does not exist.** On `adversarial-many` p14's
   `c-clang` rung **is not a function of its arguments**: `r₂ = r₃ = r₄ = r₅ = 0`,
   it returns 0 on every call after the first, and its per-call marginal reads
   **17.982 `Ir`** for a kernel that folds 168 fields. Two other blobs read
   `0.000` (SIGSEGV). Differencing against that publishes `+4287.05`.

> **Publish a cost law WITH ITS DOMAIN — the regime where the guard does not
> fire, which is where every benign input lives and is the cost a deployment
> actually pays. Outside the domain publish BEHAVIOUR, not cost.**

**The project already keeps this rule structurally, which is why no published
figure is affected**: `harness/measure.py`'s `CG_PLAN` (`measure.py:56-61`) is
six entries and **every one is `small.bin` or `large.bin`** — no adversarial
input is ever in a callgrind plan on any pattern. p14's adversarial numbers exist
only because `controls/sweep_ir.py` can be pointed at any blob. **p14 would have
been the first exception.** Before adding an adversarial blob to any measurement
plan, re-read this section.

## A WRITE bug forces the adversarial row; it does NOT force the perf row

**p12, corrected at TASK_040_REVIEW — the general form p12 shipped is refuted by a
built row.** Land the first half; the second half is a design choice.

> **Forced, and with no read analogue:** for a write bug whose guard's
> **THRESHOLD IS THE DESTINATION'S ALLOCATED EXTENT**, every input on which the
> guard fires is an input on which the unguarded rung executes an out-of-bounds
> store.

⚠ **It is about the THRESHOLD, not about the write — and as first written it did
not reach three of the five patterns it was written for** (TASK_041, measured with
everything held fixed but the threshold):

```
   n  slen  guard  rc    sanitizer     what
 128   140      1   0        clean     threshold == sizeof dst, guard PRESENT
 128   140      0   1    OOB WRITE     threshold == sizeof dst, guard DELETED
  64   100      1   0        clean     threshold  < sizeof dst, guard PRESENT
  64   100      0   0        clean     threshold  < sizeof dst, guard DELETED
```

The guard fires in **both** pairs — the checksums differ — but only at
`threshold == sizeof dst` does firing force UB. **A threshold at the allocation's
extent makes "the guard fired" and "the unguarded rung committed UB" the same
event; a threshold inside the allocation makes them independent, and then write
patterns behave exactly like read patterns.**

| pattern | guard | inherits? |
|---|---|---|
| p12, **p23**, **p25** | `dlen + slen <= DST_CAP`, `i < len`, `len < cap` | **yes** |
| **p13** | caller-supplied `n` — `n < sizeof dst` is the *correct* case; its bug is the missing NUL and the OOB **read** downstream | **no** |
| **p24** | `child < n`, a live length below capacity — firing means logically wrong, still in bounds | **no** |
| **p06** | `min(nelem, SCR)` — a threshold *inside* the destination's extent, so guard-fires and UB are independent | **no** — and this is the test's **first use at build time**, on p06 (T047), rather than as a retrospective classification |
| **p14** | `nt < MAXTOK` — the descriptor table's own extent | **YES** (T049, settling the "not as stated" row above). The sentence's mechanism *is* real and *is* p11's, so p14 puts its bug in the **outer** loop instead: the bound is a **count of a byte value**, not a length, and its threshold is the destination's extent — so guard-fires and OOB stores are the same event |
| **p14** | a delimiter is not a bound; the sentence reaches its scan's `i < len` | not as stated |

> **NOT forced:** whether such an input can *also* be a checksum-agreeing perf
> row. That depends on whether the checksum is a function of state the OOB store
> cannot reach.

p12's is not — it folds `dlen` and `dst[0..dlen]`, and its own task file mandated
that. **The counter-design was built and measured**: zero-initialise the
destination, fold it at **fixed extent** (`dst[0..CAP]`), drop `dlen` from the
result, and put the rejection point exactly at capacity. Checked and unchecked
rungs then print **identical** checksums at every `n_iters` (1…1000), and ASan
confirms the bug still fires:

```
kernel_capfold    (capacity check DELETED)  9617137326358488304
kernel_capfold_h  (capacity check KEPT)     9617137326358488304   IDENTICAL
runtime error: index 128 out of bounds for type 'uint8_t [128]'
AddressSanitizer: stack-buffer-overflow  WRITE of size 1
```

⚠ **The price is that the perf row executes UB on every call.** It is only usable
while the overflow stays in the *silent* regime (≤ +8 bytes on this box, both
compilers), and that is a property of the frame layout, not a guarantee. **A
pattern built this way must pin the overflow at ≤ +8, assert the marginal is
non-zero, and say in `spec.md` that the R1 row executes UB by construction.**
The counter-design **ships**: `p12/controls/gen_controls.py`'s `k1`/`k2` pair plus
`fillreject_blob()`, and the threshold probe is
`p12/controls/threshold_probe.py` — both re-derivable from the tree rather than
from gitignored scratch.

**Two scope corrections while you are here** (both measured): the gate's
checksum-agreement requirement binds the **matrix** inputs only —
`check.py::inputs_of` and `measure.py`'s `SKIP_INPUT_PREFIX` drop `sweep-*` entirely, so a sweep band is
never checksum-checked. And where an unguarded rung is excluded from a sweep band,
check *why*: on p12's band A it is the **crash**, not the checksum.

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

- **`forbidden_hits` is computed, printed, and never shouted** — the idiom audit
  reports it and no stage fails on it. **Proposed as a fix at TASK_053 and
  DECLINED at TASK_056, with a measurement**, and the reason
  generalises: the audit cited p05's `chunks_exact` accident as its
  could-this-happen-by-accident precedent, and **`idiom_audit` structurally
  cannot see that accident.** It scans `rung_sources(pdir)` only
  (`check.py::rung_sources` — `c/kernel*.c` plus `MEASURED_CELLS + CONTROL_CELLS`;
  this read `:820-834` until TASK_066),
  while p05's measurements lived in `.temp/` and control variants. So
  `forbidden_hits` was **0 throughout the accident**, exactly as it is 0 today,
  and shouting would not have caught it.
  ⚠ **The general form is worth more than the residual: before citing an
  incident as an accident-test precedent, check that the proposed check could
  have SEEN it.** p05's own `why` already says the gate does not verify that a
  rung honours its declaration.

  ⚠⚠ **THE EVIDENCE HAS CHANGED AND THIS RESIDUAL IS RE-OPENED** (measured at
  TASK_062; **settled at TASK_063, PROVISIONAL — not yet reviewed**). The count
  above said **0 of 132**; at TASK_062 it was **2 of 162**, and the two were a
  **real defect that shipped**: p27 forbids `` `memset(tab` `` and
  **both of its own C rungs write it** (`c/kernel.c:66-67`,
  `c/kernel_hardened.c:46-47`), so both are out of p27's own contract, and
  `idiom.why` never says what the entry is forbidden *for* — it explains every
  other one. **The decline rested on "shouting would not have caught it", and
  here shouting WOULD have.** The check can see it: `forbidden_hits` is computed
  from `rung_sources(pdir)` and these hits *are* rung sources.
  ⚠ **But do not conclude "make it fail" too quickly, because the same task
  measured the stronger fact**: this `2` has been **printed in the verdict,
  written into the gate JSON, and transcribed into `NOTES.md`** across three
  tasks and two adversarial reviews, and **nobody acted on it**. *A number that
  is printed is not a check.* So the live question is not shout-vs-silent, it is
  **fail-vs-print** — and the defect itself must be settled first: either p27's
  rungs violate the contract, or the `forbidden` entry is wrong and its removal
  is a declaration edit owing the direction test.

  ✅ **SETTLED at TASK_063 as the second: the ENTRY was wrong and is deleted**,
  as a declaration edit with a byte-provable undo. Three measured reasons: all
  seven rungs zero the table (**the four Rust rungs are FORCED to**, so a
  universal-scope `forbidden` excluded an operation every rung performs); the
  admissible respelling costs **0.0000 `Ir`/call on clang with identical `n_fn`**,
  so the entry constrained **typography, not the program**; and the hazard it was
  aimed at is **not expressible as a token** — a CLOSE-arm bulk clear and the
  initialisation spell the same characters and `spelling_matches` has no notion
  of position — while two `required` entries already exclude it.

  **`forbidden_hits` is now `0` across every pattern** (the invariant is the **zero**; the denominator grows with every pattern and **must not be written here** — it has been wrong three times. Recompute: `python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"`).

  > **Recommendation from TASK_063, PROVISIONAL: MAKE IT FAIL, batched with the
  > next `check.py` change** — zero false-positive surface today.
  > ⚠ **A batching partner has since been identified: p22's per-input timeout**
  > (`.memory/06-catalogue.md`'s p22 triage, also PROVISIONAL). `RUN_TIMEOUT = 900`
  > makes a deliberately non-terminating adversarial cell cost 3–5 hours per gate
  > run, and the fix is a contract-declared timeout — another `check.py` edit.
  > **Land the two together: one edit, one full-tree sweep.** Neither is worth a
  > sweep alone.
  > **Two figures to carry with it.** (1) The same sweep with comments, string literals and
  > ghost clauses **not** blanked gives **29 hits across 11 patterns**.
  > ⚠ **BOTH numbers in this paragraph are WRONG, re-measured at
  > TASK_068_REVIEW M3**: the sweep gives **40 hits across 13 patterns** (no
  > decomposition yields 29/11), and the denominator is **197 forbidden
  > spellings, not 183** — verified independently by summing the 20 gate records.
  > **Both were cited as the evidence for making `forbidden_hits` fail.**
  > (2) `rung_sources` includes `CONTROL_CELLS`, today `["safe_naive_verus"]`,
  > ⚠ **and the words "which no pattern ships" that stood here were FALSE** —
  > `patterns/p01-array-sum/safe_naive_verus.rs` exists (5688 B) and
  > `results/gate/p01-array-sum.json` records `idiom_audit.rungs: 6`, the control
  > cell being p01's sixth audited rung. **One `ls` refutes it, and it stood in
  > the authoritative layer and was copied into `check.py::rung_sources`' docstring.**
  > ⚠ **And the strongest argument against is the engineer's own**: a failing
  > check here would have been dischargeable by the *wrong* fix — respell at
  > 0.0000 `Ir`/call — leaving the real defect (an entry whose purpose `why`
  > never stated) in place. **Weak forcing still beats none**, because a rung
  > respelling at least moves `source_sha256` in a commit.

- ~~`source_sha256` omits `patterns/*/inputs/gen.py` and `common/slb.py`~~ —
  **CLOSED at TASK_021**, with a demonstrated record move (a comment-only
  `gen.py` edit now changes `source_sha256`; before the fix it changed nothing).
  The glob also gained `patterns/*/controls/*.py` and **`verus_run.py`**, a
  fourth uncovered file nobody had named: it is R5's compiler driver *and* the
  process every proof stage asks for a verdict, so it decides both what R5's
  machine code is and what "verified" meant in that run — and it sits at the repo
  root, which `harness/*.py` never covered.
- ~~A control generator can emit sources that compile against a gitignored copy
  of `common/`~~ — **CLOSED at TASK_022** for p08 (`PATH_FIX`, proven on a
  simulated fresh clone) and at TASK_023 for p16. Kept because the shape
  recurs: p08's `controls/gen_controls.py` leaves the shipped
  `#[path = "../../common/driver.rs"]` in its output, which from
  `.temp/p08/controls/` resolves to `.temp/common/driver.rs`. Byte-identical
  today, so it works **by luck**; on a fresh clone p08's controls do not compile.
  Same "stale or absent reproduction path" family as the entry above. p16's new
  generator rewrites the path to the real, hashed file; p08's is not fixed.

- `work_per_call` is unbounded; shrinking it 16× passes with a shout. Nothing
  checks it is denominated in the unit `work_unit_bits` names. **And it can err
  in either direction**: p16's `work_per_call = stride` *over*-estimated the bytes
  folded (headers skipped), so the floor was strict; p17's *under*-estimates by
  1.72×/1.75×, because several sub-requests read the same body — so the same
  convention made the floor **loose** (margin 40.3×, ~97.5% work loss tolerated).
  When a kernel can read the same byte twice, say which way the estimate errs.
  p05 errs *strict* again (by the 4 header bytes). Three patterns, three
  directions — **state the direction, never assume it.**
- **The `ALPHA = 0.25` floor constant needs a fresh argument for a vectorising
  kernel.** It is justified in 64-bit-lane terms; a vectorised byte fold achieves
  **1.375 / 1.0625 Ir per element** at SSE2 and an AVX-512 `vpsadbw` form would
  reach ~0.0625, which is below the constant. Nothing on this box builds with
  `-march`, so it is not live — but a pattern that adds one must re-argue ALPHA
  rather than inherit it.
  ⚠⚠ **AND ON THIS BOX IT CANNOT BE MEASURED AT ALL** (p47, TASK_065, measured).
  **`-march=native` binaries SIGILL under valgrind 3.27.1** (EVEX), so `Ir` — the
  only deterministic instrument here — **does not exist for such a build.**
  Sharper still, and the reason this is a trap rather than a limitation:
  **the failure is INPUT-DEPENDENT.** 7 of 9 compiler × input cells died; clang
  survived `small` and `large` and died on one adversarial input, rustc survived
  `small` only, gcc died on all three. **So a partial `-march` `Ir` table looks
  complete.** Do not re-argue ALPHA for such a pattern — say the figure cannot
  be taken.

- ⚠ **`work_per_call` must count the WORK UNIT, not the input bytes — and three
  patterns have had to re-denominate.** p07 counts probes (4 B/unit), p10 taps
  (2 B/unit), p47 byte comparisons (2 window B/unit); `check.py::check_marginal_ir`
  prescribes the repair verbatim. **This looks like defining a threshold away and
  on p47 it was checked and is not**: the tag loops run 11 instructions per 64
  window bytes (R3) and 12 (R4) — **0.172–0.188 `Ir` per window byte
  asymptotically** — so the 0.25 floor **forbids the shipped kernel outright**
  under the wrong unit. **The test to apply is whether the alternative unit is
  arithmetically impossible or merely inconvenient**; the first is a forced move,
  the second is the direction test firing.
  ⚠ **Report `collapse_tightest_margin` when you redenominate.** p47's is
  **2.93×, the tightest of all 19 patterns** (next 7.02, p27 134.45), which is
  the honest cost of the choice and is not visible from a PASS.
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
   moves every catalogued pattern at once. Given **two probe inputs of different shape**
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
requirement in `.memory/04-verus.md`. When they are not, R4 is unverified unsafe code that every catalogued pattern will
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
and `n_iters` is *not* the knob: `check.py`'s Miri stage (`MIRI_PROBE_ITERS` is defined at `:311` and applied at `:4769`; this said `:3819`, which is neither -- **cite the SYMBOL, line numbers rot**) rewrites it to
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

## NEVER re-ship a rung because a cheaper in-contract spelling was found

Settled at TASK_044, which was handed the decision open and argued it closed.
The manager's task file said either answer was defensible; it is not.

> **The shipped rung is chosen by IDIOM, before measurement, and it stays.** A
> cheaper in-contract spelling moves the **published bound** —
> `inf(in-contract found) − R4ship`, with the spelling named — and ships as a
> **control**. Re-ship only for a reason that is not the rung's cost: the shipped
> spelling turns out to be **out of contract**, **semantically wrong**, or **not
> the idiom it claims to be**.

Four reasons, and the first is the one that generalises:

1. **Selecting the rung by measured cost is the same move as narrowing the
   declaration to protect a number, one level over.** The direction test
   (`.memory/01-ladder.md`) catches an edit to the *declaration*; it does not
   catch an edit to the *rung*. A project that re-ships on cost has a
   cost-selected R3 and a decidable-looking contract, which is the worst
   combination available.
2. **It is asymmetric in practice.** R4 is a spelling too, and the R4 side is
   chained to the prover (**RECAP finding 14**, *"every rung is a spelling"* — not
   `01-ladder.md`'s 14, which is p13) — so it usually cannot move. Applying
   re-shipping to whichever side happens to be free systematically shrinks the
   published tax in one direction.
3. **It makes the shipped rung a function of how hard the last reviewer
   searched.** Five published "minimums" on this project have been overturned by
   the next search; a rung that moves with each of them has no stable meaning.
4. **It buys nothing measurable.** The cheapest-found bound is `+4.00` on p04
   whether or not the rung moves. **All the information is in the bound, not in
   which spelling is nailed to the mast.**

**Precedent was already consistent and three-deep before the rule existed**: p16,
p05 and p03 each found cheaper in-contract spellings and each kept its shipped
rung. p04 is the fourth.

⚠ **The corollary for reporting.** When the shipped rung is not the cheapest
found — which is now the case on four patterns — **publish both numbers,
labelled**, and never let one stand in for the other:

| quantity | definition | held fixed by |
|---|---|---|
| **fixed-R4 bound** | `R3ship − R4ship` | the shipped R3 *and* R4, both by fiat |
| **cheapest-found in-contract bound** | `inf(in-contract found) − R4ship` | R4 by fiat; **name the spelling and the input** |

On p04 they are `+5.00` and `+4.00`. Writing either alone loses information, and
`.memory/01-ladder.md` briefly instructed an engineer to overwrite the first with
the second — which would have published a number for a rung the tree does not
contain. The engineer refused it.

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
  ⚠ **A `forbidden` entry without BACKTICKS is audited zero times, and the
  verdict line still counts it** (TASK_038_REVIEW). The audit inside
  **`check_idiom`** keys on `_TICK.findall` (in `check.py::spelling_matches`), so
  a bare-string entry is invisible to it while the line two
  above still reports *"N forbidden spelling(s)"*.
  ⚠ **This citation read `:929`, then `:1103-1105`, and both had rotted.**
  **Cite the FUNCTION and give NO line number at all** — see the audit note at
  the end of this file for why the "line as a hint" compromise was abandoned. p09 shipped 5 forbidden entries
  and **0 audited spellings** — its "forbidden: 0 hits" was kept by auditing
  nothing. **Backtick every `forbidden` and `required` entry you want enforced**,
  and read `audit  forbidden: N spelling(s)` — not the declaration line — as the
  count that matters. **p09 was backticked at TASK_039 and the audit now reports
  `10 spelling(s), 0 hit(s)` — the 0 is earned.** Note the two numbers legitimately
  differ: the *verdict* line counts **entries** (5) and the *audit* line counts
  **spelling × language** (10). And the `_blank_ghost` exposure is real but did not
  fire: p09's spec fns spell `q as int / 64`, and the doc comments that do contain
  `q / 64` are blanked as comments.

  ⚠ **"Detectable" was detectable BY HAND until TASK_035; now it is one
  command**, and it covers the measurement records too, which never had a hash
  block at all:

  ```bash
  harness/measure.py --check-stale     # exit 1 on STALE
  ```

  It reports `STALE` / `GEN-ONLY` / `NO BASELINE` / `MISSING` / `FRESH` / `SKIP`
  over **both** `results/*.json` and `results/gate/*.json`. Run it before quoting
  a number. **Do not make it a gate stage** — only `measure.py` can refresh a
  measurement record and `measure.py` is inside the gate's own hash, so a stage
  would couple gate greenness to a full matrix re-measure
  (`.memory/03-measurement.md`).

  Two consequences worth knowing before choosing where a tool lives: the
  re-run tax is **per edit event, not per file** (shipping 8 files costs what
  shipping 4 costs, and batching N edits into one sweep costs one sweep), and a
  tool the gate never *imports* cannot invalidate anything **inside** a record —
  only a claim in a pattern's `NOTES.md`, which `glob(pdir/*.md)` already hashes.
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

## Line citations into `check.py` decay. Cite the FUNCTION.

**Audited at TASK_066: 5 of 9 distinct `check.py:NNNN` citations in the
authoritative layer pointed at the wrong code**, and two of the five were
duplicated into a second file, so the same wrong line had to be fixed twice.
Every insertion above a citation moves it, and `check.py` grows every task —
**5460 → 5884 → 6605 lines across TASK_066–071 alone.** Do not write a line
count here either; run `wc -l harness/check.py`.

What was wrong, and what it should have been:

| cited | actually | the real target |
|---|---|---|
| `:929` (×2) | a `named_spelling_problem` selftest comment | **`check_idiom`**, `:1103-1105` (`_TICK` at `:993`) |
| `:1249` (×2) | an `idiom_problems` selftest | **`check_checksums`**, `:1440-1476` / **`build_models`**, `:1433` |
| `:820-834` | the pinned-constant rationale comment | **`rung_sources`**, `:996-1010` |
| `:1218`/`:4903` | mid-string in a `rep.ok` | `head("1. build the matrix")` at `:1404`/`:5104` |

⚠ **One of them had drifted TWICE** — `:566` until TASK_058, then `:1247-1249`
until TASK_066. A citation that has been "fixed" is not thereby stable.

⚠⚠ **THE "LINE AS A HINT" COMPROMISE WAS TRIED AND IT FAILED INSIDE ONE
SESSION. The rule is now: name the FUNCTION and give NO LINE NUMBER AT ALL —
`` `check.py::check_checksums` ``.**

TASK_066 fixed every citation in this layer to *"function name, line beside it as
a hint"*. **By TASK_071 every one of those hints was wrong again** — `check.py`
went 5460 → 5884 → 6605 lines in three tasks, and the re-audit found the hints
had drifted onto *unrelated functions*: `:1440-1476`, written as
**`check_checksums`**, now lands inside `idiom_lines`; `:4738-4739`, written as
the stage-7 build, lands inside `check_trusted_twins`.

**A hint that is wrong is worse than no hint**, because a reader who checks it
lands somewhere plausible and concludes the citation is fine. **The two lines
directly above this paragraph were themselves the surviving example of the
failed convention** and are the reason it is retracted here.

⚠ **A function name cannot rot silently**: rename it and `grep` returns nothing,
which is a loud failure. That is the whole argument.

**The audit is an eyeball aid, not a checker** — nothing can know what a citation
*meant*, so it prints each target for a human to judge. It found all five above:

```bash
grep -rno 'check\.py:[0-9]\+' .memory/ RECAP.md .tasks/PROTOCOL.md | sort -u \
| while IFS=: read -r f l ref; do n=${ref#check.py:}; \
    printf '%-34s -> %s\n' "$f:$l" "$(sed -n "${n}p" harness/check.py | cut -c1-72)"; done
```

⚠ **Dedupe on `file:line:ref`, not on `ref`.** The first version of this sorted
`-u -t: -k3`, which collapsed the duplicated citations and reported 4 of the 5.
*A wrong command is worse than a wrong constant, because it looks
self-verifying* — TASK_065's own lesson, reproduced here inside the fix for it.

⚠ **Clean negative, same audit: the OTHER harness files' citations are fine.**
`measure.py:56` (`CG_PLAN`), `measure.py:64` (`SKIP_INPUT_PREFIX`) and
`dloop.py:361` (`if keep[-1] >= len(args):`, the arity raise, cited twice) all
still point at what they claim. **Only `check.py` decays**, because it is the one
file that grows every task. Do not re-run this half; swap the filename in the aid
above if a new harness file starts growing.

⚠ **The PATTERN docs have the same decay and it is NOT yet fixed: 22 citations
across 12 patterns** (p04, p05, p06, p09, p10, p12, p13, p16, p17, p18, p27,
p47). Audited at TASK_066, queued as RECAP "Owed" item 12 rather than fixed,
because of a scheduling fact worth keeping:

- a pattern's **gate** record globs `pdir/*.md` (in `check.py::main`), so editing any
  `NOTES.md`/`README.md`/`spec.md` makes that gate record **STALE**;
- but `measure.py`'s `provenance()` (`:226-235`) does **not** glob `*.md`, so the
  same edit costs **no re-measure** — the expensive half is not triggered.

**So batch the doc fixes with the owed `check.py` edit** (`forbidden_hits`
fail-vs-print + p22's per-input timeout), which stales every gate record anyway
through the `harness/*.py` glob. **Three owed changes, one sweep.**

## A gate hole that is one FLAG wide — stage 7 and flag-gated UB

**Found by p38's engineer, scoped by its review, recounted at TASK_067.**
`check_sanitizers` builds the C rung `gcc -std=c99 -O1 -g
-fsanitize=address,undefined` (`check.py::check_sanitizers`). **gcc enables
`-fstrict-aliasing` only at `-O2` and above**, so stage 7 cannot see a UB class
that the flag gates.

⚠ **"Structurally blind to any UB class that only exists at `-O2` and above" —
p38's first wording, which the manager repeated — is WRONG, and dangerously so:
it implies the repair is to raise stage 7's optimisation level, which would
perturb 20 patterns to fix one.** The class is **flag-gated, not level-gated**:
`gcc -O1 -fstrict-aliasing` already prints the wrong checksum, and ASan already
reports `stack-buffer-overflow READ of size 2` **at `-O1`**.

✅ **Blast radius, recounted across all 20 gate records: EXACTLY ONE PATTERN.**
**36 `fires` rows across 15 patterns, and all 36 already fire at `-O1`** —
including **p18, the other UB pattern, on all four rows**. ⚠ The review first
reported 15/5 as *16/4*; it missed **p04-ring-buffer**, whose adversarial rows
are sanitizer-clean because the missing fullness check **overwrites in bounds** —
p17's reason, a *kernel* reason. **The conclusion is unchanged: p38 is the only
pattern whose declared-clean adversarial row is clean because of the gate's BUILD
FLAGS rather than its kernel.**

**The fix is one token — `-fstrict-aliasing` in `check.py::check_sanitizers`' build line.** ⚠ **Batch
it**; it is the fourth `check.py` change waiting on one sweep (RECAP "Owed" 12).

## `forbidden_hits` HARD-FAILS since TASK_068, and `exec_code` blanks ghost CODE

**The check now fails the gate.** Rule 5's accident test was applied and answered
**yes**: p27 forbade `` `memset(tab` `` and both its own C rungs spelled it, and
the printed `2` survived three tasks and two adversarial reviews with nobody
acting on it. ⚠ **Denominators are RECOMPUTABLE, not constants** — today
**recompute both, never quote them** — `python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"` (it read 183, then 197, and p22 moved it again). The unblanked sweep gave **40 hits across 13 patterns** when last run. *(Both figures were wrong when first written — 183 and "29 across
11" — and both were cited as the evidence for the hard fail.)*

⚠ **It shipped with a false-positive surface understated by five shapes and
TASK_068_REVIEW found them: 11 of 14 honest shapes hard-failed.** The strongest
evidence that it was real: **`patterns/p09-bitset/spec.md`'s `idiom.why`, inside
`contract_sha256`, documents the trap**, and p09's author spelled its spec
functions `q as int / 64` to dodge it. **That contortion of the SPECIFICATION was
briefly the only thing keeping p09 green.**

### `exec_code` blanks in five layers (TASK_069), and the boundary is principled

comments/strings → **items gated on a cfg no cell sets** → `spec fn`/`proof fn`
items → ghost clauses → ghost statements (`proof {}`, `assert`/`assume`,
`let ghost`/`let tracked`, `Ghost(…)`/`Tracked(…)`). `spelling_matches`/`exec_code`
take a `lang`, so the Rust-only layers never touch C (a C `assert(` is exec).

> **The item level IS structural and the statement level is NOT, and that was
> measured rather than assumed.** `vparse.parse` already returns item kinds and
> offsets, and the built cfg set is derivable from `build.py`, so
> **`#[cfg(slb_twin)]` and `#[cfg(test)]` fall OUT of the rule instead of being
> named by it** — two of seven special cases dissolve. Statement level cannot be:
> `proof`/`assert`/`ghost` are statements *inside exec bodies* and `vparse`
> models items and clauses only. ⚠ **Verus was checked as an oracle and cannot
> answer** — `--log` offers `vir|air|smt|triggers|call-graph` and **no
> erased-Rust dump at all**, a run costs minutes per pattern, and it would speak
> for `verus.rs` only while the audit spans six rungs. **So layer 5 is an
> enumeration — but a CLOSED one taken from the Verus ghost grammar, not from
> incident history.**

**Three false-positive shapes SURVIVE deliberately** (`fp_probe` 11/14 → 6/14),
each an entry quoting a span genuinely present in exec code: **substring**
(`split` vs `split_first()`, `position(` vs `rposition(`), **whitespace-collapse**
(`q / 64` vs `freq / 64`), and an entry that **backticks the replacement** rather
than the banned spelling. Token-aware matching would break the standard itself —
most spellings are **expressions** (`2 + 2*nsuf > len`), not
identifiers, and whitespace deletion is **forced by p17**. **0 fire today,
the route out is a longer spelling (which sharpens the declaration), and all
three are named in the failure text.**

⚠ **`CODEGEN_CFGS` is a WHITELIST**: an unknown cfg is treated as unbuilt and
**blanked**. That direction only weakens the audit (the other hard-fails an
honest pattern), so it is the right default — **but a new `--cfg` in `build.py`
must be added here or its code silently leaves the audit, and NOTHING ENFORCES
THAT COUPLING.**

### `run.timeout_s` was the first pin that was neither judgeable nor cross-checked

Every other `slb-contract` pin is **prose-judgeable** (`driver.statements`,
`identity`, `collapse.probe_inputs`) or **cross-checked against a measurement**
(`verus.obligations`, identity digests, `miri.required`). `run.timeout_s` was
neither, reproducing `min_ir_per_work`'s `> 0`-only weakness that TASK_006_REVIEW
drove through the whole gate at `1e-9`.

**Closed by TWO mechanisms, and the review's prescribed one was insufficient
alone.** `_confirm_hang` re-runs one hung cell at `min(10 × budget, RUN_TIMEOUT)`
and fails if it terminates — ⚠ **but 10× a sub-startup budget is still
sub-startup, so the re-run never catches `1e-9`.** Hence **`RUN_BUDGET_FLOOR =
1.0 s`**, justified by measurement: `/bin/true` startup **1.13–2.17 ms**, slowest
shipped `O0` cell on `large.bin` **198 ms** — so 1.0 s is ~5× the slowest honest
cell and 900× below `RUN_TIMEOUT`.
⚠ `_confirm_hang` checks **one** cell (first in sorted matrix order): it proves
the budget is not absurdly short, **not** that every recorded `hung=True` is
right. One-line change if a pattern needs all of them.

## Two gate defects the hang machinery shipped with, both measured twice

**Found on p22, the mechanism's first user. Neither is fixed; both need
`harness/` edits and are queued (RECAP "Owed").**

**1. `check_miri`'s block reason is structurally false for EVERY pattern here.**
It says *"R4 does not return under Miri either"*. Measured on p22: `miri` on the
shipped `unsafe.rs` gives **`rc=0 UB=False`** — the hanging rung is `c/kernel.c`.
⚠ **This is not a p22 quirk.** `expected_hang` is per-**input**, but its Miri
consequence assumes the hanging rung is the one Miri runs — and
**`.memory/01-ladder.md` puts the bug in R1 only**, so `miri.sources` *always*
names a rung carrying the fix. **Cost: one unnecessarily blocked Miri row per
declared hang, i.e. a genuinely unchecked row.** Repair needs a **per-rung axis**
on `expected_hang`; `model.py` has a per-input bool only.

**2. `_confirm_hang` selects on the wrong axis.** It confirms the first cell in
sorted matrix order — on p22, `c-clang O0` — and **never an `-O3` cell**, which
is the one C11 6.8.5p6 puts at risk of being optimised away.
⚠ **The obvious repair is REFUTED**: picking one cell per distinct **rung** would
still have chosen two `O0` cells and **would have caught nothing on p22**. **The
right axis is (rung × opt).**

⚠ **A related limit worth knowing before you write a `forbidden` entry.** p22
excludes a bounded-loop spelling that writes `while n < TABCAP`, which matches
**neither** backticked entry (`for _ in 0..TABCAP`, `(0..TABCAP)`). A review
assumed the entries excluded it; **they do not.** It is excluded only by a
`required` entry's **prose**, and **no grep settles it** — which is the honest
boundary of the idiom mechanism: it decides *spellings*, and a semantic exclusion
has to be argued in `why` and checked by a human.
