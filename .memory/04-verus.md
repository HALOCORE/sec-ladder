# Verus working notes

Read `../LearnVeri/PITFALLS.md` before debugging anything. Grep
`../LearnVeri/_VERUS_DOC_/vstd/` for exact signatures and available lemmas
instead of guessing; `../LearnVeri/microbench/` has 20 worked CVE proofs to lift
technique from.

## A proof-enabling program change is not automatically free

**Measured at TASK_033 / TASK_033_REVIEW, and it is a trade rather than a win.**

p11's scan can stop at `q == len`, so `p = q + 1` cannot be proved overflow-free
(vstd has no `isize::MAX` slice-length axiom and `usize` may be 32-bit). **p17
paid for the same fact with a second `requires` clause plus a driver conjunct.**
p11 instead writes one line *before* the step:

```rust
if q >= len { break; }
```

That removes the obligation at **zero preconditions and zero driver statements**,
and the line is semantically the right statement — *"a string with no terminator
is the last string in the window"*, which is precisely the case R1 cannot
represent.

⚠ **But it is not free in instructions, and p11 shipped saying it was.** Deleting
it (checksums unchanged on every input):

```
kernel 123 -> 114 insns; scan body 6 -> 5
marginal small  19084.00 -> 17481.00   (+8.4% of R4)
marginal large  50174.00 -> 45909.00   (+8.5% of R4)
guard = 24*L + 97 at k=24  =  1.00000 Ir per scanned byte + 3 per string + 1 per call
                              (zero residual, four string lengths)
```

**Mechanism**: with the guard the scan loop must carry its *exit reason* out in a
register — the `sete %bpl` exists only so the post-loop `test; je` can implement
`if q >= len`. Without it the loop falls through and the `sete` disappears.

**So the two ways of discharging an overflow obligation price differently, and
neither is free:**

| route | preconditions | driver | instructions |
|---|---|---|---|
| p17 — a second `requires` | **+1 clause** | +1 conjunct | **0** |
| p11 — a guard in the program | 0 | 0 | **+1.00000 Ir/scanned byte, 8.5%** |

**Quote the trade, never "it was free."** And note where the cost lands: the C
rungs do not pay it per byte, because their scan is a libcall that already returns
the length — so of p11's R4 6.00000 Ir/byte scan, **1.00000 is bookkeeping that
`strlen`/`memchr` get for free.**

## Running

```bash
./verus_run.py file.rs                                   # verify
./verus_run.py file.rs --crate-type=lib                  # verify a lib
./verus_run.py --compile file.rs -o out -C opt-level=3   # verify + compile
./verus_run.py --keep --compile file.rs                  # keep scratch to inspect artefacts
./verus_run.py --info                                    # resolved paths + versions
```

Clean run prints `verification results:: N verified, 0 errors`. **Always report
the obligation count** after a proof edit — a count that drops unexpectedly means
code stopped being verified, not that the proof got easier.

## Flags and codegen (established at TASK_002 on p01)

- **`verus_run.py` forwards unrecognised flags to rustc verbatim.** `--cfg
  slb_isolated`, `-C opt-level=N`, `-C debug-assertions=off`, `-C
  codegen-units=1` all work, so `#[cfg_attr(slb_isolated, inline(never))]`
  inside `verus!` gives R5 the same isolated/whole axis as the other rungs.
- **`-C lto=fat` is impossible for an R5 cell.** Verus links a precompiled
  `vstd` rlib with no bitcode: `error: failed to get bitcode from object file
  for LTO (Can't find section .llvmbc)`. So the `whole` inline mode must be
  defined *without* rustc LTO, or R5 drops out of the matrix and the rungs stop
  being comparable. `harness/build.py` defines `whole` for Rust as
  "single crate, codegen-units=1, no `#[inline(never)]`", which is what `-flto`
  buys the three-TU C build.
- **R5's exec code must be *textually* identical to R4's, not merely
  equivalent.** Writing R4 as `for i in 0..len` and R5 as `while i < len`
  produced the same instructions in a different *order* (two independent
  `add`/`sub` swapped) and broke byte identity while leaving the normalised
  text identical. Verus supports `for i in 0..n` with `invariant` (no
  `decreases` needed — it is inferred for a range), so use the same loop form.
- At `-O0` a Rust kernel still calls `Iterator::next`, so R4-vs-R5 `md5_raw`
  differs on link layout alone. See `.memory/03-measurement.md`,
  "The raw-byte oracle has one blind spot".

## Conventions

- File starts `use vstd::prelude::*;`, verified code inside `verus! { ... }`.
- Loops need **both** `invariant` and `decreases`. Verus infers neither.
- `int`/`nat` are spec-only. Exec code uses `u64`/`usize`/…; cross with `as int`.
- `spec fn` cannot be called from exec code. Mirror with an exec fn whose
  `ensures` ties back to the spec.
- `&mut` postconditions need `old(x)` / `*final(x)`, never a bare `*x`.
- Unverifiable exec code (`println!`, `get_unchecked`) → `#[verifier::external_body]`
  helper. There is no statement-level skip; smallest unit is a whole item.
- Byte literals (`b'x'`) are unsupported inside `verus!` — use `0x68` or named consts.

## The trusted computing base — count it honestly

R5's entire value proposition is "the unsafe preconditions are discharged by the
verifier". Anything the verifier *doesn't* check is TCB and must be counted and
justified. **TCB lines = every line inside:**

- `#[verifier::external_body]` function bodies
- `assume_specification` / `external_fn_specification` blocks
- `assume(...)` in proofs — **any `assume` is a red flag; justify or remove**
- `#[verifier::external]` items that are reachable from measured code
- `unsafe` blocks (which, in R5, should only ever appear inside `external_body`)

Report as: `TCB: N lines across M items`. A rung-5 cell with a large TCB is not a
win and must not be presented as one.

**A proof of a `requires` is not a proof that the trusted body honours it, and
p08 measures exactly how invisible the gap is.** Substituting
`core::ptr::copy` → `core::ptr::copy_nonoverlapping` inside p08's trusted
`move_right` — a body whose whole safety contract *is* the non-overlap, and
which then commits the pattern's own UB — verifies **`11 verified, 0 errors`
shipped and `15 verified, 0 errors` under `--cfg slb_twin`**. Invisible to
Verus, to the **verified twin**, to the `spec.md` contract pin (textually
unchanged), and to gate stages 5c and 5c-req. What catches it is the `O3`
identity pin against R4 (the call target differs) and **Miri**. So never write
that R5 "rules the bug out" or that the bug is "not expressible at R5" — the
correct claim is that the *caller's* obligation is discharged, and the trusted
body is trusted. This is why Miri is mandatory for any pattern with a trusted
item, and it is the sharpest justification that rule has.

**An `external_body` item need not contain `unsafe`.** p08's `copy_in` wraps a
perfectly safe `copy_from_slice`; it is trusted because the verifier does not
check its body, not because it is dangerous. The TCB tally must count it anyway —
"trusted" means "unchecked by the verifier", not "unsafe".

⚠ **The reason given here until TASK_048 — *"vstd has no spec for
`copy_from_slice`"* — was FALSE, and it had stood since TASK_004.** The pinned
vstd specifies it at `vstd/std_specs/slice.rs:205`
(`requires old(dst)@.len() == src@.len()`, `ensures final(dst)@ == src@`), along
with `split_at_mut` (`:185`), `copy_within` (`:235`), and the write-back for the
array→slice coercion (`vstd/array.rs:175 ref_mut_array_unsizing_coercion`, which
**Verus inserts itself and which never appears in source**). A bulk copy can be
verified with no trusted wrapper at all: p06 removed one and shipped
`18 verified, 0 errors` with **byte-identical `-O3` machine code**.

**The rule that replaces it, and it is about R4, not about the copy:**

> A bulk copy needs a trusted wrapper when **R4's spelling** is unsupported, not
> when the copy is. The `identity` pin forces R5 to match R4's bytes, so an R4
> written with `copy_nonoverlapping` / `as_ptr` / `as_mut_ptr` / `ptr::add` —
> **all `is not supported` at the pinned vstd** — drags the wrapper back in even
> though the *same copy* spelled `copy_from_slice` verifies clean.

⚠ **"Byte-identical" is an `-O3` claim and does not carry to `-O0`** (TASK_055
probe 1, on p08; **unreviewed**). `split_at_mut` returns a **4-word tuple via
`sret`** where `index_mut` returns 2 words in `rax:rdx`, so the respelling costs
**+2.00 `Ir`/call flat at `-O0`** and drops `identity` to `differ` against a
pinned `norel`. It is **not** a check — both keep one bounds check and the same
panic pads. **The repair is p06's own precedent**: respell **only the rungs that
need it** (p06's `idiom.required[5].rust` records a 2-and-2 receiver split and
its own `-O0` price of +3 instructions). On p08 that route gives TCB 4 → 3,
`-O3` unchanged and `-O0` identity **`exact`**.

⚠ **And `RangeTo<usize>` has no `SliceIndexSpecImpl`** (only `usize` at
`std_specs/slice.rs:14` and `Range` at `:31`), so a rung spelling `dst[..n]` is
**unverifiable as written** — p08's shipped R4 is exactly that. `dst[0..n]` gets
past the precondition and then fails its *postcondition*. Use `split_at_mut`.

Measured on both sides at TASK_048. **p06's R4 already spelled
`copy_from_slice`, so its wrapper came out at zero cost (TCB 6 → 5). p02's R4
spells `copy_nonoverlapping`, so removing its wrapper moves codegen 72/70 → 81/79,
`+5.00 Ir/call` flat, one extra panic pad — it BREAKS `identity: exact`, and p02
keeps the wrapper with the price recorded** (`p02/NOTES.md` §5b). Before
recording "no spec exists", check `~/tools/verus/vstd/std_specs/` — this claim
propagated into two patterns' source comments and one `.memory/` file.

**Count every `external_body` item, not just the interesting one.** The pilot was
published as "TCB: one 3-line `get_unchecked` wrapper"; the true tally is **3 items**
— `get_unchecked`, `out` (the `println!` wrapper) and `main`. Under-counting is how
the pilot's fatal defect hid in plain sight: `main` being `external_body` is exactly
why no precondition was ever discharged (`.memory/02-bench-rules.md`, rule 2). An
`external_body` on a *driver* is far more dangerous than one on a leaf helper,
because it deletes call-site obligations wholesale. List them individually.

### How the TCB column is counted, and whether it can be gamed (TASK_048)

**PROVISIONAL — the census and the classification are measured; the accounting
decision itself has not yet been through a review.**

The question that forced this: removing a trusted wrapper does not always delete
the trust, it can **relocate it into vstd**. Trusted-base size is one of the five
axes this project compares, so if a pattern can shrink its published TCB by
picking a spelling whose axioms live upstream, the column means something other
than what it says.

⚠ **The manager proposed reporting two numbers — author-written trusted items,
and "vstd assumed specifications relied upon". That was refuted with a census
and must not be reinstated.** The pinned vstd holds **402 `assume_specification`
sites, 272 `external_body` items and 545 `broadcast` proof fns across 44 files**;
"relied upon" is **undecidable from the text**, because Verus inserts some
coercions itself (`ref_mut_array_unsizing_coercion` never appears in source) and
`broadcast use` pulls whole families at once. Every rung depends on the same
vstd core, so the second column would be near-identical for every row — it
does not discriminate, and it measures the wrong thing.

**What ships instead: one headline number — the gate's own `tcb_items` — plus a
three-way classification of what each item is.**

| class | what it is | why it matters |
|---|---|---|
| **U-license** | wraps an operation whose safety the *author* is asserting | the author can be wrong, and the error is local to this pattern |
| **V-gap** | exists only because the verifier cannot express something | the error travels to every pattern using that operation |
| **infra** | driver/print plumbing | deletes call-site obligations wholesale — see above |

Census at TASK_048, 14 patterns: **57 items / 118 lines — 25 U-license, 2 V-gap,
30 infra.**

⚠ **"NOT GAMEABLE" IS TRUE RETROSPECTIVELY AND FALSE PROSPECTIVELY** (TASK_055
probe 2, measured; **unreviewed**). The census below is a fact about the patterns
that existed when it ran — **14 of them, at TASK_048**, before p14 and p18; the
line above says 14 and this sentence used to say 16 — all of which reach
unchecked memory through
`get_unchecked`-shaped accessors. **A pattern built on `vstd::raw_ptr` does
not**: a verified `raw_ptr` kernel needs **zero project-local trusted items**, so
it would publish `tcb_items = 2` — **fewer than p01's array sum** — while the
twin regime goes idle and prints the same sentence a macro bypass would.
**Decide how such a pattern is counted BEFORE building one**, not after; the
whole point of the classification is that the number means something.

#### DECIDED (TASK_055_REVIEW): keep one number, add PROSE, and do NOT build a column

The manager proposed a **`tcb_reach`** field beside `tcb_items` — `safe` /
`local-external-body` / `vstd-axiom` — so a `raw_ptr` pattern's `2` would stop
being comparable with p01's `3`. **The review attacked it and it does not
survive. It is rejected, and the manager is NOT clearing its own design here.**

- **It is undecidable for the same reason the two-number proposal was.** p01 is
  **not** `safe`: its own `NOTES.md:481` lists the vstd axioms it rests on
  (`u64::wrapping_add`, `wrapping_mul`). Every pattern reaches *some* axiom, so
  the discriminator is a **per-item judgement**, which is exactly the property
  the 402-site census killed the earlier proposal for.
- **As a `spec.md` pin it fails `.memory/02-bench-rules.md`'s own rule** for what
  may be pinned.
- **The prose fix is cheaper and half-landed already** — say, in the pattern's
  own text, how the rung reaches unchecked memory.
- **The twin regime needed a separate fix regardless, and it was WORSE than the
  probe reported.** The probe said stage 5c-twin *"prints the same sentence a
  macro bypass would"*. It printed **nothing at all**: the `continue` preceded
  both `out[src]` assignments, so the stage emitted no `ok`/`fail`/`shout` and
  the file vanished from the gate record. That is **silence**, not a wrong
  sentence. **Fixed** — it now `shout`s and records the file. ⚠ **A shout does
  not make the two cases distinguishable**; it stops the gate reporting nothing.
  Blast radius when landed was one file, p01's `safe_naive_verus.rs`.

> **So the residual is live and named: a legitimate zero-trusted-item pattern
> and the known macro bypass produce the same gate output.** It is now a *loud*
> same output instead of a silent one. **Do not read a `raw_ptr` pattern's
> `tcb_items` as comparable with a bounds-checked pattern's** — say how the rung
> reaches memory, in words, beside the number.

**With that caveat, the gameability question is answered by measurement, not by
policy: across the patterns that exist the column is NOT gameable, because the
relocation almost never exists.**
`<[T]>::get_unchecked`, `<[T]>::get_unchecked_mut`, `u64::count_ones`,
`core::ptr::copy_nonoverlapping`, `<[T]>::as_ptr`, `<[T]>::as_mut_ptr` and
`<*const T>::add` are **all `is not supported` at the pinned vstd**. Measured
exposure was **2 of 58 items (3.4%)** — p06's `scr_load` (removed, TCB 6 → 5) and
p08's `copy_in`. p09's `popcount64` is a genuine V-gap. Every other pattern's TCB
is unchanged by the question.

⚠ **BOTH named exposures are now CLOSED, so the measured exposure is `0`, and the
denominator moved too.** p08's `copy_in` was tried at TASK_055 and landed at
TASK_056: p08 is **TCB 4 → 3**, and its gate record now reads `identity: exact`
at **both** opt levels — at `-O0` that is *better* than the `norel` its own
`spec.md` expects. The census's own numbers therefore no longer describe the
tree. **Recount rather than quoting `58` or `3.4%`:**

```bash
python3 -c "
import json,glob
n=0
for f in sorted(glob.glob('results/gate/*.json')):
    d=json.load(open(f))['verus']
    n+=len(d['verus.rs']['tcb_items'])          # R5 ONLY -- see the warning
print(n,'items')"
```

⚠⚠ **THIS COMMAND HAS NOW BEEN WRONG TWICE, IN OPPOSITE DIRECTIONS, AND THE
THIRD VERSION IS ABOVE. Three plausible commands give three different totals:**

| version | p01 counted as | total | verdict |
|---|---|---:|---|
| return on first `tcb_items` found | **2** (`safe_naive_verus.rs`) | 62 → **65** | **wrong** — p01 is the only pattern with two verified files and its `verus.rs` was dropped |
| sum **every** occurrence | **5** (both files) | **68** | **wrong** — double-counts `load_input` and `emit`, declared in both |
| **`verus.rs` only** | **3** | **66** | ✅ **matches every pattern's published TCB** |

> **The lesson is that it was never a counting question.** All three commands
> count correctly; they disagree about **which files are the pattern's trusted
> base**, and only the R5 file is. p01's `safe_naive_verus.rs` is a second
> verified cell whose `load_input`/`emit` are *the same infra items re-declared*.
> **Before replacing a constant with a command, check the command against one
> pattern by hand** — a wrong command is worse than a right constant, because it
> looks self-verifying. (TASK_058 caught version 1; TASK_055_REVIEW caught
> version 2, which was TASK_058's own repair.)

Dated reading from the corrected command: **66 items across 17 patterns**, **76 across 19**. **Run it; do not quote either.** ⚠ **The denominator is recountable and the
NUMERATOR is not** — "is
there a vstd relocation for this item" is a judgement made against a pinned
vstd, and the two that existed were found by hand. Do not report a fresh
percentage without redoing that audit; report the count of items and say the
relocation audit is as of TASK_048.

### The tautology battery's tactics ABORT more often than the gate used to admit

**TASK_053 found it, TASK_056 measured its true extent; unreviewed.** Stage 5c-req
tries each `requires` conjunct under three tactics to check it is not a
tautology. Two of the three **abort** — producing no `N verified, M errors` line
at all — on shapes that are everywhere in this project:

- **`by (bit_vector)` aborts on any clause mentioning `v@.len()`.**
- **`by (nonlinear_arith)` aborts on any clause mentioning `old(...)`** — i.e.
  on **every write accessor's precondition**: 8 clauses across 8 patterns (p02's
  `copy_bytes`, p08's `move_right`, and the `*_set_unchecked` of p03, p04, p06,
  p12, p13, p14).

Until TASK_056 an aborting tactic **overwrote the real verdict**, so **51 of 52
shipped rows recorded `verified: null, errors: null, tactic: "bit_vector",
verdict: "not a tautology"`** on all 16 patterns. **The soundness was never
affected** — a tactic that aborts could not have proved the clause either — but
the record asserted a check it had not made.

⚠ **The repair is NOT to fail on an abort.** That would red-line all 16 patterns,
because the tactics are *genuinely inapplicable* to those shapes. The gate now
records `tactics_ran` / `tactics_inapplicable` and names only tactics that ran.
Current distribution: **41 rows ran [bare Z3, `nonlinear_arith`], 8 ran bare Z3
alone, 1 ran all three.**

**The lesson for any future battery: distinguish "the tactic said no" from "the
tactic never ran", and never let the second overwrite the first.**

### Test the proof by breaking it — a green run proves nothing on its own

Verification succeeding is not evidence that the specification says anything. Run
mutants and check that each one *fails*. TASK_002 did this on p01 (mutants kept
in the report, not the tree):

| mutation | expected | actual |
|---|---|---|
| driver's guard weakened so `off` can reach one past the last window | fail | **fail** — `precondition not satisfied ... off + len <= v@.len()` *at the `kernel(...)` call site* |
| kernel's `requires` deleted | fail | **fail** — loop invariant not established |
| kernel's `ensures` shifted by one element | fail | **fail** — postcondition not satisfied |
| **`requires` deleted from the `external_body` `get_unchecked` wrapper** | fail | **VERIFIES CLEANLY** |

The last row is the one to remember. **Weakening an `external_body` item's
`requires` never causes a verification error — it silently deletes the callers'
obligations.** A wrapper whose `requires` drifts turns the whole proof vacuous
with no diagnostic at all. This is the same class of defect as the pilot's
`external_body main`, and neither is detectable from "N verified, 0 errors".
Prefer wrappers with **no `ensures` at all** (a trusted item that asserts
nothing cannot axiomatise a falsehood) wherever the proof can re-derive the fact
at run time instead.

**Superseded at TASK_010 for any item a security argument rests on — see the
verified-twin section below.** A trusted item with no `ensures` cannot have a twin
with teeth, because there is nothing to force the twin's body to do the work, and
the sharpest fix for the macro bypass keys the whole regime on a non-empty
`ensures`. The advice above still holds for trusted items that contain no `unsafe`
and carry no weight (`load_input`, `emit`).

**And a pin is not enough for this one.** TASK_003_REVIEW deleted the `requires`
from p01's `get_unchecked` *and* the matching three characters from `spec.md`,
in one commit, and got a full green gate reporting "3 TCB items, all contracts
identical to spec.md" — an R5 whose trusted base axiomatises that reading any
index of any slice is defined and yields `v@[i]`. The pin is written by the same
author as the code, so no declared pin defends against this. The rule since
TASK_005 is **structural**:

> An `#[verifier::external_body]` item whose body contains `unsafe` must carry a
> non-empty `requires`.

A trusted item that performs an unchecked operation and demands nothing of its
callers *is* the axiom that the operation is always safe. `harness/check.py`
fails on it outright; the only escape is a per-item justification string in
`spec.md`'s `verus.unsafe_justifications`, which the gate then prints in the
verdict on every single run, where a reviewer reads it.

The corollary for writing R5: **give every trusted `unsafe` wrapper the
precondition its callers must discharge, and keep the `ensures` as weak as the
proof can live with.** `get_unchecked`'s pair — `requires i < v@.len()`,
`ensures r == v@[i as int]` — is the shape to copy.

### The mechanical defences (added at TASK_003)

TASK_002 recorded "`check.py` cannot catch it; only reading the trusted
signatures can". Half right: no *verification* result catches it, but a **pin**
does. Every pattern's `spec.md` now carries, and `harness/check.py` diffs:

1. **The obligation count**, per Verus source file. `external_body main` drops
   p01's from 5 to 3. Pinning it turns "always report the obligation count after
   a proof edit" from a discipline into a gate — but **know what it measures**.
   TASK_003_REVIEW derived it: *one Verus query per function, plus one per loop
   body*. It is a checksum over the function/loop skeleton, so it is invariant
   under precisely the semantic weakenings it was introduced to catch (a deleted
   `requires`, a tautological `ensures`) and it moves on benign refactors that
   add or remove a function or a loop. An unchanged count is evidence of
   nothing. It also explains why `--verify-function main --verify-root` reports
   2 for one function: the second query is the driver's loop body.

   **The rule of thumb is incomplete — corrected at TASK_007.** "One query per
   function plus one per loop body" predicts **7** for p16; the true count is
   **10**. It does not account for `by (nonlinear_arith)` / `by { .. }`
   sub-proofs, each of which is its own query, and p16's driver has four. **Do not
   derive a pin from the formula — measure each term** with
   `--verify-function <name> --verify-root` and write the decomposition into
   `spec.md` beside the pin, as p16 does. A pin a reviewer cannot re-derive from
   `spec.md` alone is a declared pin, which `.memory/02-bench-rules.md` forbids.

   **A `const` inside `verus!` is its own query** — found at TASK_014, measured
   two ways and confirmed at review (`SCR` → `1 verified`). p08's 11 is
   `SCR 1 + kernel 3 + main 5 + …`, so a pattern that introduces a capacity
   constant will see the count move for a reason that has nothing to do with the
   proof. Add it to the terms you measure rather than being surprised by it.
2. **Every item's `external` attribute, `requires` and `ensures`, verbatim**, and
   the item *set*. This is what catches the two mutations that move no count at
   all: a tautological `ensures` (`r == r`) and a deleted `external_body`
   `requires`. Demonstrated at TASK_003 — both gave `5 verified, 0 errors` and a
   green gate before, and both now fail with the exact clause diff.
2b. **"Is this error hiding another one?"** Verus reports the first failure per
   query, so a mutant that reports one error may be concealing others — and if a
   claim rests on *which* obligation failed (p17's whole result does), that
   ambiguity is fatal. Two probes, both used at TASK_011_REVIEW:
   **`--multiple-errors 20`** to force the rest out, and **strip the functional
   spec and re-run** — if the memory-safety obligations then give `N verified,
   0 errors`, nothing was hidden behind the functional failure.

   **The positive control is not optional, and its strongest form was measured at
   TASK_012.** Strip the functional spec from a mutant that *does* break memory
   safety and confirm it **still fails**: p17's `nocheck_msonly` gives
   `9 verified, 1 errors`, the single error being `0 <= base`, a memory-safety
   obligation. Without that control, a `10 verified, 0 errors` after stripping
   proves nothing — it is equally consistent with the probe being blind.
3. **`verus <file> --verify-function <name> --verify-root`** answers "does this
   function have a verified body?" *semantically*. It reports `0 verified` for an
   `external_body` item and ≥1 for a real one, so the "rule 2" call-site check no
   longer depends on recognising an attribute. Useful in its own right when
   debugging: it tells you which item an obligation belongs to.

   ⚠ **IT HAS THREE ANSWERS, NOT TWO, AND `check.py` HANDLED TWO** (TASK_077,
   corrected at TASK_078). A `check.py` comment claimed an ambiguous
   `--verify-function` *"silently reports 1 verified"*. **Measured at the pin, it
   does not — it errors and refuses to pick:**

   ```
   error: more than one match found for --verify-function apply
      matched results are: A::apply, A::spec_apply, B::apply ...
   ```

   **The three answers are: resolved-and-verified, `could not find function`, and
   AMBIGUOUS.** The gate's `_UNRESOLVED_RE` matched only the second, so an
   ambiguous query returned `resolved=True, verified=None` and printed *"Verus
   resolved the item and has no verified body for it"* — **TASK_008_REVIEW major
   E's false diagnosis, one answer over.** A branch now exists.

   ⚠⚠ **AND THE TRAP IS SUBSTRING MATCHING, NOT DUPLICATE NAMES.**
   `--verify-function apply` matches **`spec_apply`**, so ambiguity fires with
   **one `impl` and no duplicate item name at all**. **All 22 `verus.rs` files
   already carry a substring-ambiguous pair** — `slb_twin_*`, `shift_round` /
   `shift_rounds`, `popcnt` / `lemma_popcnt_le`, `toks` / `fold_toks`,
   `suf_at` / `nsuf_at`, `apply` / `spec_apply`. **Qualify the name, and never
   assume a bare one selects what you meant.**

4. **The Python contract the gate evaluates is generated from the Verus clause
   text**, through a declared `verus.translate` table in `spec.md` (TASK_005).
   `contract["requires"]` and `verus.items[...]["requires"]` used to be two
   independent transcriptions of one predicate with nothing checking they
   corresponded, so the proof's precondition could be weakened while the gate
   went on evaluating the strong one over every input and printing that it held.

5. **`vparse.parse` returns a list and duplicate item names are a hard
   failure.** The gate keyed items by name and kept the last, so a decoy
   `fn kernel` inside a `#[cfg(any())] mod` could supply the pinned contract
   while the real, weakened kernel was the one measured and the one compiled.
   Pinned items must also be inside `verus! {}` and not `#[cfg]`-gated.

Attribute detection itself is `harness/vparse.py` now, not a regex over
`prefix.split("\n\n")[-1]` — that split let **one blank line** between
`#[verifier::external_body]` and `fn main` hide the attribute completely, and
`#[cfg_attr(all(), verifier::external_body)]` was invisible to it in any layout.
vparse walks backwards over the real token stream and matches `external_body`
anywhere inside an attribute. It also blanks comments and string literals first,
because `// calls kernel(...)` used to satisfy the "there is a call site" check
on its own.

### Make the `ensures` load-bearing, or it is decoration

Deleting p01's kernel `ensures` outright used to give the same `5 verified, 0
errors` — nothing consumed it. The fix is one ghost line in the driver:

```rust
let r: u64 = kernel(vs, off, win_len);
assert(r == sum_wrap(vs@, off as int, win_len as int));   // consumes the ensures
```

With it, deleting the `ensures` fails at `4 verified, 1 errors`. **Ghost code
erases**, so R5's kernel stays byte-identical to R4's (re-checked at TASK_003:
`md5_fn` `619b1d1b…` both, O3 isolated) — the byte-identity objection to doing
this was really an objection to the gate's own textual driver diff, and that now
exempts ghost statements. Do this in every pattern.

### An *inconsistent* `ensures` on a trusted item is a second vacuity mode

Found at TASK_004 by a mutant that was expected to fail and did not. p02's
`copy_bytes` wrapper carries two `ensures` clauses:

```rust
final(dst)@.len() == old(dst)@.len(),
final(dst)@ =~= src@.subrange(from as int, from + n as int)
               + old(dst)@.subrange(n as int, old(dst)@.len() as int),
```

Delete the `+ old(dst)@.subrange(...)` — i.e. stop saying the tail is unchanged —
and the remaining clause additionally asserts `dst.len() == n`. The file still
gives `9 verified, 0 errors`, with no diagnostic.

**It is not vacuity, and the first write-up of this said it was.** Measured at
TASK_004_REVIEW: with the mutant in place `assert(false)` after the call is
*still* unprovable, so callers are not vacuous. What actually happens is a
**silent strengthening** — the trusted item injects an extra false fact
(`dst.len() == n`) that is consistent in context and happens to make the security
postcondition provable. A false axiom that is *usable* is worse than one that
collapses the context, because nothing downstream looks wrong.

Consequences, both measured:

- **The `assert(false)` reachability probe does not detect this.** Add it anyway
  (it catches genuine vacuity), but do not expect it to catch this class.
- **One of `copy_bytes`'s two `ensures` clauses was redundant** — deleting the
  *length* clause leaves 9 verified / 0 errors, because the tail clause implies
  it. Deleting the *tail* clause gives 8 verified / **1 error**. Implication runs
  one way, so only the weaker clause is free. (TASK_004_REVIEW reported both as
  redundant and TASK_006 measured otherwise; the corrected version is here.) A
  spec can look like two obligations and be one — but check which one.

**The mechanical defence — clause deletion, implemented as gate step 5c.** For
each `ensures` clause of each `external_body` item (plus the pinned kernel item):
delete it, re-run Verus, and **fail if the file still verifies with 0 errors**.
Derived, not declared, so it does not inherit the self-certification problem.
Mutants are built in a repo-layout mirror under `.temp/clausemut/`, never in
`patterns/`. A relocated unmutated control and an `assert(false)` reachability
probe run alongside.

It found three real defects on first run — p02's redundant length clause, p02's
third kernel clause, and p01's `safe_naive_verus.rs`, which had never had a
consuming ghost `assert` at all.

**It narrows this class; it does not close it.** Step 5c deletes *whole* clauses,
so it catches redundant and decorative ones. The mutant above **rewrites** a
clause and still verifies, so it survives. Do not describe 5c as closing the
inconsistent-`ensures` hole.

**Three further limits, all measured at TASK_006_REVIEW. Know them before
quoting 5c as a defence.**

1. **5c tests `ensures` only, and the `requires` hole is the dangerous one.**
   It iterates `it.clauses.get("ensures")` and nothing else. Deleting
   `from + n <= src@.len()` from p02's trusted `copy_bytes`, or weakening
   `get_unchecked`'s `i < v@.len()` to `0 <= i`, each gives **9 verified, 0
   errors** — the obligation count does not move, and the structural
   "a trusted `unsafe` item must demand something" rule is satisfied by the
   tautology `n >= 0`, which the gate then *prints approvingly*. Full green.
   That is TASK_003_REVIEW's finding re-opened on the one item p02 exists to be
   about, and it leaves R5 axiomatising that an arbitrary
   `copy_nonoverlapping` is defined.

   **There is no mirror-image deletion oracle for a trusted item, and TASK_008
   measured it.** The obvious fix — "delete the `requires`, confirm some call
   site now fails" — does not work, because deleting a precondition from an
   `external_body` item only *removes* obligations from its callers. Nothing
   anywhere fails:

   | mutant on p02 `verus.rs` | result |
   |---|---|
   | control | 9 verified, 0 errors |
   | delete `copy_bytes` `requires[0]` | **9 verified, 0 errors** |
   | `get_unchecked`: `i < v@.len()` → `0 <= i` | **9 verified, 0 errors** |
   | `copy_bytes`: both `requires` → `n >= 0` | **9 verified, 0 errors** |
   | delete the **kernel's** `requires[0]` (a *verified* item) | 8 verified, 1 errors |

   Deletion is a valid test only on the last row's kind. Had it been applied to
   trusted items it would have reported every trusted precondition in the
   project as not-load-bearing. **Three checks replace it (TASK_008):**

   - **A tautology probe** — synthesise `proof fn <params verbatim> ensures
     <conjunct>, { }` inside `verus! {}` and run it. If it verifies, the
     conjunct is a tautology and constrains no caller. Catches `0 <= i` and
     `n >= 0`. `old(dst)` and `&mut [u8]` both work in such a probe. A probe
     that fails to *compile* is a hard failure ("this conjunct was not judged"),
     never a silent skip.

     **Two limits, both measured at TASK_008_REVIEW.** (i) `vparse.params_text`
     copies the parameter list and nothing else, so the probe **hard-fails** on
     a generic (`<T: Copy>`, `where` clause), a `self` receiver, a lifetime
     parameter, or a trigger-less quantifier — fail-closed and therefore correct,
     but the consequence is that *a pattern with a generic or method-shaped
     trusted accessor cannot be greened at all*. (ii) The oracle is "Z3 proved
     it", so a tautology that needs a trigger or a lemma reads as meaningful.
     `v@.len() <= usize::MAX` — this file's own documented "not free" tautology —
     passes as "not a tautology". Partial mitigation, measured: a tautology the
     probe cannot discharge usually cannot be discharged at the *call site*
     either, so the exploitable subset is clauses the caller can prove and the
     bare probe cannot. `v@.len() <= usize::MAX` is exactly one of those, because
     the kernel's `assert(src@.len() == spec_slice_len(src))` fires the axiom and
     the probe has no such line.
   - **Deletion, for verified items only** — where the mirror test really works.
   - **Parameter coverage** — every parameter a trusted `unsafe` body *uses*
     must appear in its `requires`. This is the only one of the three that
     catches a **missing** precondition, which has no verification signature at
     all. Escape hatch is the existing `verus.unsafe_justifications`, shouted
     every run.

   Known false-positive shape for the third: a pure *value* parameter (written,
   never used as an address or a length) legitimately needs no precondition.
   Nothing in the tree exercises it yet.

   **Still open, and the most dangerous hole in the project.** A `requires` that
   is non-trivial, mentions every parameter, and is nonetheless **too weak by
   one**. Two measured forms, both with a full-gate PASS at TASK_008_REVIEW:

   - `get_unchecked`: `i < v@.len()` → **`i <= v@.len()`**. One character. 5a
     prints it approvingly (*"demands `['i <= v@.len()']` of every caller,
     constraining every parameter its body uses"*), the tautology probe cannot
     see it (it is not a tautology), parameter coverage cannot see it (both
     parameters appear), and deletion is not applied to trusted items by
     construction. R5's trusted base then axiomatises that **reading one byte
     past the end of a slice is defined and equals `v@[i]`** — which is CWE-125,
     the bug class p16 exists to model.
   - `copy_bytes`: `from + n <= src@.len() + 1`, the same shape on a copy.

   The three checks judge *triviality* and *mention*. Neither is *strength*, and
   strength is the whole property. **Do not describe 5c-req's guarantee as
   "strong enough" — it is "not `true`".**

   **The mechanism that does judge strength: the verified twin (TASK_009).**
   Beside each trusted `unsafe` item sits `#[cfg(slb_twin)] fn slb_twin_<name>`
   with the *same* contract, implemented in checked code — `get_unchecked`'s twin
   is `{ v[i] }`, `copy_bytes`'s is an indexed copy loop. Gate stage `5c-twin`
   re-runs Verus with `--cfg slb_twin` and requires 0 errors. A `requires` too
   weak to license the real operation is too weak to license the checked one, so
   `i <= v@.len()` fails with *"precondition not met: index in bounds"*. The
   `#[cfg]` keeps it out of every measured build, so it costs no instructions.

   The contract is **lifted from the trusted item and compared**, not declared,
   so weakening the item while leaving the twin alone is a signature mismatch —
   note that Verus *alone* passes that mutant at 12 verified / 0 errors, so the
   comparison is doing real work.

   ⚠ **Stage 5c-twin has TWO LIMBS and a mutation report must say which one
   fired** (TASK_045_REVIEW). They are (i) **signature identity** —
   `vparse.norm_clause(twin.sig)` against the trusted item's — and (ii) **the
   twin verifying under `--cfg slb_twin`**. A mutant that weakens the item *and*
   its twin together keeps limb (i) and is caught by (ii) (p04's
   `p1_weak_requires`, which passes the shipped configuration at 9/0). A mutant
   that weakens only the item trips limb (i) — p13's M2, measured
   `signature_identical = False` where shipped and M2b are `True`.
   **p13's `NOTES.md` reported M2 as caught by `spec.md`'s item pin alone; it is
   caught twice**, and the control script reproduced only stage 5a, so its
   verdict column understated the gate. **Report the limb, not just the pass** —
   otherwise a report cannot distinguish "the twin has teeth here" from "the
   contract pin happened to cover it". Eight mutants fail for eight distinct reasons,
   including two beyond the original design: a twin missing its `#[cfg]` (it
   would compile into the measured binaries) and a twin whose body calls
   `get_unchecked` (it re-uses the axiom it exists to check).

   The copy twin is an indexed loop and it **verifies**, so a failure there is
   weakness, not a missing spec — and the gate prints the Verus diagnostic so the
   two can be told apart. (This paragraph used to attribute the wrinkle to
   `copy_from_slice` having no vstd spec; it has one — see above. The twin's
   argument is unaffected.)

   Shipped obligation counts: p02 9 → 12, p01 7 → 8, with the pins unmoved.

   **The load-bearing part is not the twin verifying — it is the twin *failing*
   when the trusted precondition is deleted**, re-checked on every run
   (`slb_twin_get_unchecked` / `slb_twin_copy_bytes` → 11 verified, 1 error).
   A twin that verifies proves nothing on its own; a twin that still verifies
   with the precondition deleted **never used it**, and certifies nothing about
   strength. Two independent toothless-twin attacks were built and **both are
   caught by that one check**:

   - a trusted item with a `requires` and **no `ensures`** — the shape this file
     actively *recommends* — twinned by an **empty body**. Verus: clean.
   - a twin whose body is `loop { }` under
     `#[verifier::exec_allows_no_decreases_clause]`, so it never returns and
     satisfies **any** postcondition vacuously. Verus: 13 verified, 0 errors.
     (Without that attribute Verus itself rejects it: *"loop must have a
     decreases clause"* — and then helpfully names the attribute that disables
     the check.)

   Both give `FAIL [twin] … still verifies with the precondition DELETED`. That
   generalises the way an enumeration of bad twin shapes would not: it tests the
   twin's *dependence* on the precondition rather than guessing at how a body
   might dodge it.

   **The twin earned its keep at p08 — the first demonstration in six patterns,
   and it is now the mechanism's whole case.** Every trusted item before p08 was
   a single-clause `get_unchecked`, so the twin had never been exercised on the
   case it was designed for. p08's `move_right` is the first genuinely
   multi-clause contract, and mutant M2 — weakening `0 < dr <= m` to `<= m + 1`
   in the item **and** its twin — gives **`11 verified, 0 errors` shipped** and
   **`14 verified, 1 errors` under `--cfg slb_twin`** (*invariant not satisfied
   before loop*). Reproduced independently at review, against an `11`/`15`
   control. **Nothing else in the gate catches it**: the count pins move, but
   only because the twin is what moves them. Keep the twin.

   Note precisely what it does *not* catch, so a writeup does not overreach:
   dropping an `ensures` conjunct (M4/M5) fails ordinary Verus anyway, and the
   `copy_nonoverlapping` substitution above passes the twin cleanly. **The
   twin's unique catch is a weakened `requires`, and only that.**

   **But the deletion probe is not the mechanism's perimeter.** TASK_009_REVIEW
   found three bypasses that never reach it and one blind spot that survives it.
   Do not describe the twin as closing the strength class.

   - **Stage 5a's parameter-coverage rule has a second false-positive family,
     found in the tree at TASK_014**: a parameter whose *type* already fixes
     everything sayable about it. `move_right(v: &mut [u8; SCR], ...)` is
     rejected — *"demands … which constrains nothing about `['v']`"* — because
     the rule asks syntactically whether the `requires` mentions `v`, and with a
     fixed-size array there is nothing left to say: the real safety fact,
     `m <= SCR`, *is* stated and *is* about `v`'s length, just not syntactically.
     Worked around by widening to `&mut [u8]`, **and the widening cost the
     contract the length fact** — with a real slice a caller cannot prove
     `v@.len()` survives the call (`assertion failed`, 1 verified 1 errors),
     where the array signature gives it free (`3 verified, 0 errors`). So the
     three-clause `ensures` does **not** partition the buffer, and the more
     general contract is here the *weaker* one. Do not repeat p08's `NOTES.md`
     claim that the widening was "a fix rather than a workaround".

   - **Scope is decided by a regex on a function body.** `_UNSAFE_RE` is
     `\bunsafe\b` searched against `item.body`, and `vparse` parses **`fn` items
     only**. Move the `unsafe` into a `macro_rules!` and the item is invisible to
     *both* 5a's structural rule and 5c-twin's trusted list: `requires` deleted,
     twin deleted, **full gate PASS** with *"no trusted `unsafe` item, so no twin
     is required"*. That is TASK_003_REVIEW's blocker fully re-opened. `unsafe` in
     a `common/driver.rs` helper is the same hole without a macro, because the
     gate never parses that file. **Key the trusted-item rules on
     `external_body` + a non-empty `ensures`, not on `unsafe`** — that is the
     shape that can axiomatise a falsehood, per this file's own argument.
   - **The twin is verified in a different configuration than the shipped proof.**
     `--cfg slb_twin` changes the meaning of the whole file, and the
     "only a twin may be `#[cfg]`-gated" check is enforced over `fn` items, so a
     cfg'd `const`/`use`/`type`/`static` is invisible. With
     `#[cfg(slb_twin)] const SLACK: usize = 0;` / `#[cfg(not(...))] … = 1;` and a
     `requires in_bounds(v, i)` shared character-for-character by item and twin,
     the twin is checked against `i < v@.len() + 0` while R5 ships
     `i < v@.len() + 1`. Measured: `get_unchecked(v, v.len())` **verifies in the
     shipped config**. Fix: the token `slb_twin` may appear in a pinned Verus file
     only inside a twin's own `#[cfg(slb_twin)]`, and pin the twin-config
     obligation count too.
   - **`verus.twin_justifications` is uncapped free text**, and with every twin
     justified away the gate still prints `0 verified twin(s): every trusted
     `unsafe` item's `requires` is strong enough…` — a sentence that asserts the
     property at *n = 0*, while both known too-weak forms ship.

   **The blind spot that survives every check: a trusted `ensures` need not be
   complete with respect to the operations its body performs.** The twin only has
   to satisfy the `ensures`, so
   `unsafe { let _peek = *v.get_unchecked(i + 1); *v.get_unchecked(i) }` passes
   with the contract, the twin and the pins all unchanged — nothing licenses the
   `i + 1` read, and the twin cannot see it because the `ensures` never mentions
   it. Nothing mechanical checks this. **The only backstop is Miri on R4, which
   `.memory/02-bench-rules.md` makes mandatory only when R4 ≠ R5 — i.e. optional
   exactly when this project's headline byte-identity result holds.** Revisit that
   policy; and see the per-item argument requirement below.

   Also, from the code rather than a mutant: the deletion probe deletes **all** of
   a twin's `requires` clauses and requires one failure, so a twin needing only 1
   of N clauses still reports that the implementation "genuinely needs it". Make
   it per-conjunct before a multi-clause accessor arrives.

   Note the interaction with the "prefer wrappers with no `ensures`" advice above —
   a trusted item with no `ensures` cannot have a twin with teeth, because there
   is nothing to force the body to do the work. **That tension is worse than it
   first looked: the sharpest fix for the `_UNSAFE_RE` bypass is to key the
   trusted-item rules on a non-empty `ensures`, which pulls the same way.** Where
   a pattern's security rests on a trusted item, give it an `ensures` and a twin.

   **What a human must still read, after every fix** — put this per item in the
   pattern's `NOTES.md`: (a) is the twin's body the right checked stand-in for the
   unchecked operation (`v[i]` for `*v.get_unchecked(i)`)? — declared, and the
   gate cannot judge it; (b) is the trusted `ensures` **complete** with respect to
   every unchecked operation the body performs? — the blind spot above; (c) does
   the clause mean the same thing in the shipped configuration as in the twin's?

   **All three bypasses closed at TASK_010, and (a)–(c) are now mandatory text.**
   The per-conjunct fix above landed too, and was verified *by construction* at
   TASK_010_REVIEW rather than by reading: a redundant second conjunct on both
   item and twin is now reported as still-verifying with that single conjunct
   deleted, while p02's two real `copy_bytes` conjuncts each give 11 verified / 1
   error.

   **Is the twin worth its weight? Adjudicated at TASK_010_REVIEW — keep it.**
   The manager designed the mechanism and wrote this entry, so an independent
   agent was asked, and told to treat "delete it" as a welcome answer. It said
   keep, on a structural argument rather than a preference:

   - **Nothing else covers this class.** Miri never opens `verus.rs`, and a weak
     precondition does not execute UB, it only fails to forbid it. So for a
     too-weak trusted `requires` the twin is not the best backstop, it is the
     **only** one. `.memory/02-bench-rules.md` now records this.
   - **What it uniquely catches is a *missing conjunct*** in a multi-clause
     trusted `requires` — the archetypal honest mistake when wrapping an
     intrinsic that has three documented preconditions and the author encodes
     two. p02's own comment admits it carries two of three. Deletion of a trusted
     precondition cannot fail Verus, parameter coverage passes, and the tautology
     probe passes; only the twin moves.
   - **Cost is not the objection.** 5c-twin is five Verus runs on p02 at ~1.7 s
     each, ~8.5 s of a ~4-minute gate. Maintenance surface is the real cost.
   - **Honest caveat, and it must be stated when reporting p16:** there is **no
     recorded accidental instance** of a too-weak trusted `requires` on this
     project — both known forms were reviewer-built. And the twin is **idle on
     p16**, whose accessor is the same single-clause `i < v@.len()` p01 and p02
     ship. A green 5c-twin on p16 is not evidence that anything hard was checked.

   **"Its value accrues from p17 on" was wrong — corrected at TASK_011.** p17's
   accessor is *also* single-clause, and for a structural reason worth knowing:
   p17's interesting harm is **not a memory error at all**, so no amount of
   accessor strength addresses it. The twin's value accrues from the first pattern
   that needs a **multi-clause trusted accessor**, which is a property of the
   *intrinsic being wrapped* — raw-pointer families p27+ — not of the pattern
   number. **Four patterns in (p01, p02, p16, p17, p05 — all single-clause), the
   mechanism has never been exercised on the case it was built for.** That is a
   fact to state when reporting it, not a reason to remove it (see the
   adjudication above) — but it is now a standing item: if p27+ arrives and the
   accessor is *still* single-clause, reopen the keep/delete question.

   **`MAX_TWIN_JUSTIFICATIONS` was deleted at TASK_007**, on the same review's
   recommendation: it was the manager's round number, it is redundant (the
   separate "every twin justified away" rule already fails that case), and it was
   the one knob in the twin regime that could hard-fail an honest pattern with no
   route out. The escape hatch remains, uncapped but shouted every run.

   - **The regime is keyed on `external_body` + (non-empty `ensures` **or**
     `unsafe` in body)**, not on `unsafe` alone. Additionally every `unsafe` token
     in a pinned Verus source must lie inside a trusted item's body, and `unsafe`
     in any `#[path]`- or `mod`-included `common/` file is a hard failure — the
     macro bypass *and* the no-macro variant (`unsafe` moved into
     `common/driver.rs`) both fail now. Watch the trap the engineer hit building
     this: `blank_noncode` erases the `#[path = "..."]` string literal, so an
     include scan must read **raw** text or it silently scans nothing.
   - **`slb_twin` may appear only inside a twin item's own `#[cfg(slb_twin)]`**,
     in the pinned file *and every file it includes*, checked before any Verus
     call; and `verus.twin_obligations` is pinned (p02 12, p01 8) rather than
     merely requiring the count to rise. The engineer's soundness argument for why
     a token scan is *complete* rather than heuristic, which is worth keeping:
     Rust conditional compilation is driven by `cfg`/`cfg_attr` predicates that
     must **name** the flag in the token stream — there is no cfg aliasing and no
     computed predicate — so if the token occurs nowhere else, the two
     compilations differ in nothing but the twins. Residual: an `include!()` of a
     file outside the module graph would not be found.
   - **`twin_justifications` is capped at 1**, justifying away *every* trusted
     item is a separate hard failure, each justified item `rep.block`s the run,
     and the OK line states its `n` and refuses to fire at zero. Note the
     engineer's own objection, which stands: "1" is a round number, and a hatch
     with a hard cap and no route out is the exact shape that made
     `MIN_DECLARABLE_IR_PER_WORK` forbid p09. If a pattern legitimately has two
     untwinnable trusted items, the cap becomes "fewer than all".
   - **The deletion probe is per-conjunct**, demonstrated on a synthetic third
     conjunct: `from <= src@.len()` deleted alone still verifies (12/0) and now
     fails the stage, while each of p02's two real conjuncts gives 11/1.
   - **(a)–(c) are required text.** Each trusted item needs an
     `SLB-TRUSTED-ARGUMENT <src> <item>` block in `NOTES.md` carrying all three
     labels, ≥200 chars, printed in full on every run. The gate can require that
     the argument exists; only a human can judge it.

   **The tension is now resolved, in the opposite direction to the old advice.**
   Because the regime is keyed on `ensures`-or-`unsafe`, a trusted `unsafe` item
   with no `ensures` is still inside it — and its only possible twin is an empty
   body, which the deletion probe catches. So **a trusted `unsafe` item must in
   practice carry an `ensures`**, and "prefer wrappers with no `ensures`" is
   **wrong** for any item a security argument rests on. It remains right for
   `load_input`/`emit`, which contain no `unsafe` and stay outside the regime.
2. **`&&` defeats whole-clause deletion — still open.** TASK_008 made 5c delete
   *conjuncts* (`vparse.top_level_ops` / `conjunct_spans` / `delete_conjunct`),
   and a clause carrying a top-level `==>`, `||` or `<==>` is **refused rather
   than guessed at**, with the refusal shouted. `item.clauses` stays comma-split
   so no `spec.md` pin moved. The reviewer's original `&&`-merged mutant is now
   caught (`ensures[0].conjunct[1] is NOT load-bearing`).

   **But one pair of parentheses reopens it, silently.** `top_level_ops` reports
   operators at bracket depth 0 only, and "no operators found" is treated as
   *atomic with `refused=None`*. So `( A && B )` is neither split nor refused —
   no shout, no failure, full gate PASS, and the redundant trusted axiom is back
   (measured at TASK_008_REVIEW: deleting only the conjunct gives 9 verified /
   0 errors, i.e. it was never load-bearing). Cost to an author: two characters.

   The contrast is the defect. The `==>` path *is* loud; the design assumes
   "anything unsplittable gets shouted about", and the parenthesised case escapes
   both branches. Note p02 as shipped exercises neither path (`SHOUTS: 0`), so
   the refusal branch is untested by the tree — strip redundant outer brackets
   before deciding a clause is atomic, and treat "atomic" as a claim to be
   justified rather than a default.

   **Fixed at TASK_009**, which also found the splitter was *unsound* in a second
   way nobody had specified: splitting a `forall` body at its inner `&&` produced
   a fragment with the bound variable free, so the mutant failed to **compile**,
   and a compile failure was being read as *"the conjunct is load-bearing"*. A
   check that fails open on malformed input, in the direction of reporting health.
   A top-level quantifier binder is now refused (and therefore shouted), and the
   `vparse` selftest covers all three shapes at gate step 0.
3. ~~**`clause_deletion_extra_items` can silently un-check the kernel.**~~
   **Closed at TASK_008** — an unknown item name is a hard failure.

A Verus run on p02's `verus.rs` measures **1.7 s**, not the ~20 s an earlier
docstring claimed, so mutation stages are far cheaper than they were budgeted at.

Meanwhile, for any `external_body` item with more than one `ensures` clause:
prefer one strong clause to several overlapping ones, and state beside the item
why each clause is true of the real operation — that comment is the only thing
between the proof and a false axiom.

### Consuming a postcondition about `&mut` state

`.memory/04-verus.md` already says the `ensures` must be consumed or it is
decoration. For a `&mut` postcondition the consuming assert needs the *pre*
state, and the only way to hold it is a ghost binding:

```rust
let ghost d0: Seq<u8> = dst@;
let r: u64 = kernel(src, k * stride, dst);
assert(dst@ =~= copy_dst(d0, src@, (k * stride) as int));   // consumes it
```

Both lines erase, so R4/R5 byte identity survives (measured on p02: `md5_fn`
`0e5b5936…` both, `-O3 isolated`). `harness/dloop.py` had to learn that
`let ghost` / `let tracked` are ghost statements before this was possible —
before that the snapshot showed up in the driver diff as a real statement, so
the only way to keep the driver pin was not to consume the postcondition.
Without the assert, replacing p02's security clause with a tautology verified
cleanly.

**Also: this Verus rejects a bare `dst@` in a postcondition** —
*"to dereference a mutable reference parameter in a postcondition, disambiguate
by wrapping it in either `old` or `final`"*. The spelling that works is
`final(dst)@`, no `*`.

### Vacuity is the failure mode that silently ruins everything

A proof of a false or unreachable statement verifies happily. Guard against:

- **Unsatisfiable `requires`** (`requires false`, or contradictory clauses) makes
  the function verify trivially and it is never callable. Check the *call site*
  verifies too.
- **A wrong `ensures` on an `external_body` helper axiomatises a falsehood** and
  everything above it is worthless. Each such `ensures` needs a written argument
  for why it matches the real Rust semantics.
- **Trivial `ensures`** (`ensures true`, or restating an input) proves nothing.
  The postcondition must state the property the pattern is about.
- A function nobody calls, or a `spec fn` that is never `assert`ed against, is
  decoration.

The reviewer agent checks all of the above by grep + reading. See `.tasks/PROTOCOL.md`.

### The verified twin WORKS, and both of its legs are load-bearing — measured

**p27, TASK_060_REVIEW.** The twin regime is the manager's own design and has
never been tested against a determined attempt to make it vacuous. It was, four
ways, and it holds — this is the strongest positive result the mechanism has.

p27 ships two trusted items (`rec_alloc`, `rec_free`) that are local
`#[inline(always)]` copies of vstd's allocator API, **licensed by twins whose
bodies are that vstd API**. The obvious worry is circularity: a twin that calls
the function it exists to check is **re-stating the axiom rather than
re-deriving it**, which is what `_TWIN_BANNED` prevents one level up.

**It is not circular, and the two halves catch different things:**

| attack | caught by | verdict |
|---|---|---|
| weaken the trusted `requires` **and** the twin together (4 variants) | **Verus** | shipped 15/0, **twin 19/1** every time, failing at `slb_twin_rec_alloc`'s `allocate(size, align)` → `vstd/raw_ptr.rs:915` |
| weaken the trusted item **alone** | **the gate, structurally** | Verus verifies it **20/0 — it does NOT catch it**; `norm_clause(twin.sig) == norm_clause(t.sig)` goes `True → False` |

> **So: a twin whose body is ANOTHER CRATE's `external_body` API is a valid
> strength oracle** — it proves contract *refinement* against that crate's
> axiom. What it does **not** prove is body equivalence, and on p27 that gap is
> closed separately and uniquely by `#[inline(always)]` plus
> `md5_fn(unsafe::kernel) == md5_fn(verus::kernel)` plus Miri. **Do not reuse
> this shape without closing the gap the same way.**

### `identity: exact` is an 18-of-18 invariant, so TCB-vs-identity is NOT a trade

**p27, TASK_060_REVIEW.** p27 can be built at **`tcb_items = 5`**
(`r5_vstdpure`, verifies 15/0) instead of 7 — but that variant's R4/R5 pair is
**`differ` at both opt levels**, because `vstd::raw_ptr::allocate`/`deallocate`
carry **no `#[inline]`**, so an R5 that calls them emits a GOT-indirect
cross-crate call R4 cannot produce. Cost of the minimal TCB: **+130.11 / +416.00**
`Ir`/call whole-program marginal (**−30.03 kernel + 150.13 `vstd::allocate`
+ 10.01 `vstd::deallocate`** — so it is the *call*, not the kernel).

**Count before treating it as a choice: 18 of 18 shipped `spec.md` files pin
`O0: norel, O3: exact`.** A pattern at TCB 5 would be the only one unable to
support **ladder finding 1** (the proof costs exactly zero instructions), on the
largest ghost state in the tree. **Ship the larger TCB and say why** — "we chose
the bigger number" invites a question the 18-of-18 fact already answers.

### The driver's `main` obligation term is **5** — there is no `main 4` anywhere

**p47 + TASK_065, measured across the whole tree.** `grep -o 'main [0-9]'
patterns/*/spec.md`: **17 patterns record `main` 5** (p01 and p02 record no
term). **p27 recorded 4 and was wrong**, provably from its own arithmetic — its
pinned decomposition read `… + kernel 3 + main 4 = 15` and **summed to 14**,
against a pinned *and measured* 15. `./verus_run.py verus.rs --verify-function
main --verify-root` on p27's own file returns **`5 verified, 0 errors`**.

⚠ **And the "shared off-by-one" several patterns mention is a claim about the
RULE OF THUMB, not about the value.** The prediction *body + driver loop + one
per `by`-block* gives **6**; Verus reports **5**. p27's note inverted that into
*"Verus reports 4"* and then named eight patterns as recording the same thing —
**none of them does**. Both errors shipped through a build, an adversarial review
and two corrections tasks, and were caught only because a **different** pattern
recounted the same driver.

> **Recount the term, do not inherit it.** It is one `verus_run.py` invocation,
> and the arithmetic check is free: **the per-item terms must sum to the pinned
> total.** p27's did not, in a `spec.md` the gate had passed nineteen times.

### `global size_of usize == 8;` — Verus's `usize` is ARCHITECTURE-INDEPENDENT

**p10, TASK_059; reviewed and cleared to land as-is (TASK_057_REVIEW).** Verus
does not assume a 64-bit `usize`. So

```rust
let taps: usize = 2 * r + 1;        // r built from four header bytes
```

is `possible arithmetic underflow/overflow` — **on a hypothetical 32-bit
target**, where `2·(2³²−1)+1` really does overflow.

⚠ **Bounding the VALUES does not help.** `assert(n <= 0xffff_ffff); assert(r <=
0xffff_ffff);` verify *themselves* and the two errors stand (measured both ways),
because the missing bound is on **`usize::MAX`**, not on `n` or `r`. This is the
kind of obligation that looks like an input-range problem and is not.

Two routes, and the choice is forced by the pattern's own declaration:

- **Widen the arithmetic.** p07 met the identical obligation and computed its
  length check in `u64`. **p10 could not**: `spec.md` pins the spelling
  `2 * r + 1` in all seven rungs, so an `(r as u64)` cast would put R5 outside
  its own pattern's contract — `.memory/01-ladder.md`'s idiom pin reaching into
  the proof, which is the R4-is-chained-to-the-prover mechanism running the
  other way.
- **`global size_of usize == 8;`** — one line, and the file goes to
  `10 verified, 0 errors`.

> **It costs NOTHING and that is measured, not argued.** It is **checked by
> Verus against the actual compilation target**, not assumed — a `== 4` fails to
> compile with **`E0080`**, so a 32-bit build cannot be produced at all. It adds
> **no trusted item** and **no obligation of its own**: the count summing to
> exactly 10 is the check.

⚠ **Once it is in, value-bounding `assert`s of the kind above go DEAD** — verify
identically with and without them. Remove them; a dead `assert` in a proof reads
as load-bearing to the next person.

## Proof techniques that keep coming up

- **Four traps a parser proof hits, all measured on p17 (TASK_011).** Full
  write-ups in `../LearnVeri/PITFALLS.md`.
  - **`continue` is not expressible in a Verus `for` loop** — *"for-loops do not
    yet support continue"*. `while` + `continue` verifies but needs the increment
    placed above the guard. Usually the better fix is to restructure into a
    guarded `if`, which p17 did: `if start < end && start >= 0 { … }`. That also
    made the R1↔R1h difference a single conjunct, which is what the ladder wants.
  - **vstd has no axiom that a slice is at most `isize::MAX` bytes**, and Verus
    models `usize` as possibly 32-bit. A kernel doing signed index arithmetic
    therefore needs an explicit `requires buf@.len() <= 0x7fff_ffff_ffff_ffff`,
    discharged by a matching conjunct in the driver's guard. Budget for it — it is
    not a proof failure, it is a missing library fact.
  - **A loop invariant cuts the pre-loop context.** Facts established before the
    loop are not visible inside it unless restated in the invariant.
- **A *product* index (`i*ncol + j`) — the p05 shape (TASK_013).** Needs
  `lemma_mul_inequality` plus one `by (nonlinear_arith)`. The non-obvious part:
  **the nonlinear conjunct cannot live in the outer loop's invariant**, because it
  is false at `i == nrow`. Re-derive it at the top of the loop *body* and restate
  it in the inner invariant. Verus will prove `nrow*ncol <= 0xffff_ffff` from
  `nrow, ncol <= 65535` even with `usize` modelled as possibly 32-bit, so the
  bound itself is not the work — placing it is.
- **A parser loop with `break` proves cleanly** — established on p16 (TASK_007),
  where R5 verified **first try in ~2 s** and the one-session budget went unused.
  Two ingredients: `invariant_except_break` for the facts that hold on every
  normal iteration, plus a loop `ensures` for what must hold on *both* exits.
  The invariant shape that does the work is **"the walk from here is the whole
  walk"** — relate the accumulator so far, plus the spec function applied to the
  *remaining* input, to the spec function applied to the whole. Two ghost
  accumulator snapshots carry it across the break. That shape should transfer to
  every parser in Family C.
- **`decreases` catches a real bug with no test run.** p16's `p += vlen` variant —
  a common spelling of the walker — fails at `decreases not satisfied at end of
  loop`, because `vlen == 0` makes no progress. Built as plain Rust it **hangs**
  on a zero-length-record input the shipped kernel handles. That is the cheapest
  honest demonstration on this project of something a proof gives that a test
  suite does not: no input had to be guessed.
- **Representation invariant**: `spec fn well_formed(&self) -> bool` tying
  `self.buf@.len()` to the logical sizes; thread it through every method's
  `requires`/`ensures` and the constructor's `ensures`. One invariant usually
  discharges all the bounds and overflow obligations at once.
- **Compose contracts**: one fn's `ensures` should be the next fn's `requires`, so
  a pipeline verifies with no re-checking at call sites.
- **Nonlinear arithmetic** (`*`, `/` in invariants) does not auto-prove — use
  `by (nonlinear_arith)` or rephrase to avoid it.
- **`exists|...| P`** needs a `#[trigger]` and a witness in scope; often prove the
  witness `by (compute)` immediately before the `assert`.
- **`checked_add`/`checked_sub`** return `Option` and never panic — often easier
  than proving raw `+` cannot overflow.
- **Wrapping arithmetic has full specs**: `x.wrapping_add(y)` etc. are
  `assume_specification`'d in `vstd::std_specs::num` and marked
  `#[verifier::allow_in_spec]`, so the *same call* is usable inside a `spec fn`.
  Writing a kernel with wrapping ops removes the overflow precondition entirely,
  which is usually the right move: it leaves only the memory-safety obligation,
  and it stops the `requires` from depending on facts about input *values* that
  no honest loader can supply. Spec-level forms live in `vstd::wrapping`
  (`u64_specs::wrapping_add`, ...).
- **`v@.len() <= usize::MAX` for a slice is not free.** It comes from
  `vstd::slice::axiom_spec_len`, whose trigger is `spec_slice_len(slice)` — a
  term that never appears in normal code. Without it, `off + i` on in-bounds
  indices still reports "possible arithmetic underflow/overflow". Fix:
  `assert(v@.len() == vstd::slice::spec_slice_len(v));` once, before the loop.
  Ghost-only, erases.
- **Slices (`&[T]`) are well specified** — `View`, `spec_index`, `len`,
  `slice_subrange`, `slice_index_get`, and exec `v[i]` all work. Prefer `&[u64]`
  over the pilot's `&Vec<u64>`: it is idiomatic Rust and costs nothing.
- **`&mut [T]` works too** (established at TASK_004 on p02): `old(dst)@` /
  `final(dst)@`, `Vec::as_mut_slice` is `assume_specification`'d with a
  prophecy, and `dst[i] = v` has an `IndexSetTrustedSpec`. ⚠ **This bullet used
  to end *"there is no vstd spec for `copy_from_slice`"*; that is false and was
  corrected at TASK_048** — see the `external_body`-need-not-contain-`unsafe`
  section above for what actually decides it (**R4's spelling, not the copy's**).
  `copy_from_slice`, `split_at_mut` and `copy_within` are all specified; a
  wrapper is needed when R4 spells the copy with raw pointers, because
  `copy_nonoverlapping` / `as_ptr` / `as_mut_ptr` / `ptr::add` are unsupported
  and the `identity` pin forces R5 to match R4.
- ⚠ **`RangeTo<usize>` has no `SliceIndexSpecImpl`** at the pinned vstd
  (`std_specs/slice.rs:14,30`), so `dst[..n]` fails with `precondition not
  satisfied` while `dst[0..n]` gets past the precondition and then fails its
  *post*condition (`index_mut`'s `call_ensures` is never instantiated). Use
  `split_at_mut`. Found at TASK_048, and it is why removing p06's wrapper forced
  an **idiom** edit rather than being a pure measurement.
- **`decreases b - a` is rejected on a two-cursor loop** whose cursors cross;
  `decreases b` is the measure that works. Every two-cursor kernel here will hit
  it (TASK_047).
- **Dividing a length by a stride needs lemmas.** `n / s >= 1` from `s <= n`
  needs `vstd::arithmetic::div_mod::lemma_div_non_zero`; `(n / s) * s <= n`
  needs `lemma_fundamental_div_mod`; `k * s <= (nrec - 1) * s` from `k < nrec`
  needs `lemma_mul_inequality` (broadcast) and one `by (nonlinear_arith)` to
  join them. Three ghost lines, all erasing.
- **Decode a little-endian prefix with `+`, not `|`.** `b0 + 256*b1` and
  `b0 | (b1 << 8)` are the same function on bytes and compile to the same
  instruction, but only the first is linear arithmetic; the second drags in
  `by (bit_vector)`. Choosing the spelling that is cheaper to prove is fine.
  Choosing a weaker *specification* is not.
- **Panic-freedom ≠ correctness.** Clamping an index silences the bounds panic and
  leaves the logical bug. The security property needs a *functional* `ensures`.

## The R5 unsafe-licensing idiom

vstd ships no spec for `<[T]>::get_unchecked`, so the standard move is a minimal
trusted wrapper — this is the pilot's entire TCB:

```rust
#[inline(always)]
#[verifier::external_body]                    // body trusted, not verified
fn get_unchecked(v: &Vec<u64>, i: usize) -> (r: u64)
    requires i < v.len(),                     // ...but every caller must prove this
    ensures  r == v[i as int],
{ unsafe { *v.get_unchecked(i) } }
```

### `vstd::raw_ptr` WORKS, and it unlocks the bug class this project lacks

**TASK_055 probe 2 — measured, unreviewed.** Every bug modelled here is spatial
or logical; **none is a LIFETIME bug**, the one class safe Rust rejects at
compile time. p14 rejected a lifetime candidate on the reasoning that R4 could
not be a rung. **That reasoning is refuted.**

- **`add` / `offset` are unsupported, but `addr` / `with_addr` ARE** — so pointer
  arithmetic has a supported spelling. This is the specific claim p14 got wrong.
- **A heap buffer works.** A 64-byte loop kernel over `&[*mut u8]` with
  `Tracked<&Map<int, PointsTo<u8>>>` verifies **3/0** and is **`exact` at O3 /
  `norel` at O0** against its plain-unsafe twin — p08's own pinned levels — with
  **zero project-local trusted items**.
- **A stack local does NOT work, and the reason is exact**:
  `SharedReference::new` is **private** (`E0624`), and `allocate()` is vstd's
  sole origin of pointer permission. There is no `Vec` bridge.
- ⚠⚠ **RETRACTED (TASK_055_REVIEW, measured): the use-after-free is NOT caught
  by rustc's move checker in the formulation that would actually be built.** The
  `E0382` is an **artefact of the hand-unrolled two-element probe**. With a real
  permission map and the kernel called after `deallocate`, the failure is
  `error: precondition not satisfied … wf(d@,*perms,n as int)` — **an ordinary
  SMT obligation, no `E0382` anywhere**. So *"the proof catches it"* is the
  RIGHT sentence after all, and the *"linearity, not SMT — a structurally
  different R5 story"* paragraph this file carried is withdrawn. It was written
  from a probe whose shape did not survive being generalised, and it had already
  reached `RECAP.md`.
- ✅ **The ghost loop a real pattern needs EXISTS and is cheap** (TASK_055_REVIEW,
  A1 — the question the whole pattern was blocked on). Splitting `PointsToRaw`
  `n` times under an invariant into `Map<int, PointsTo<u8>>`, joining all `n`
  back, with a real `deallocate`: **7 verified, 0 errors, zero project-local
  `external_body` / `assume` / `unsafe`.** SMT cost **150 ms / 711,948 rlimit**,
  and the report's worry about a 4096-slot map is empty: raising the bound to
  `n <= 1_000_000` gives the **identical rlimit**, because it is proved
  symbolically. **So the TCB alarm above is REAL and not a scaffolding
  artefact.**
- **Gotchas**: `align_of_u8` sits outside the broadcast group; `Set::new` returns
  an `Option`; and see the TCB caveat above — a `raw_ptr` pattern would publish a
  *smaller* TCB than p01.
- ⚠ **Reproducibility is solvable but NOT the way this said.** Folding from
  offset 16 removes run-to-run variation and leaves variation **across `-O`
  level**, which `build.py` puts in one matrix — and at `-O3` the writes into the
  recycled slab are **dead-store-eliminated**, so that row does not execute the
  UAF at all. **Put the UAF on adversarial inputs only.** Full measurement and
  the general lesson: `.memory/03-measurement.md`, the tcache section.

**The formulation to build** (probe report §2.8): a **slab with pointer handles**
at R4/R5 and **`(slot, generation)`** at R1h/R2/R3 — so safe Rust's cost is a
**representation change, not a check**. No pattern here has that axis.

⚠ **THREE CONSTRAINTS ON BUILDING IT, all measured at TASK_055_REVIEW. None is
fatal; all three are cheaper to know now than after five rungs exist.**

1. **The UAF must live on ADVERSARIAL inputs only.** At `-O3` the stores into
   the recycled slab are dead-store-eliminated, so that row does not execute the
   bug at all, and the `-O0`/`-O3` checksums differ — which stage 2 rejects.
   `.memory/03-measurement.md`'s tcache section has the numbers and the general
   lesson. Precedent for per-cell divergence: p06's `adversarial-past48`.
2. **The harness cannot express rungs with different SIGNATURES.** The
   formulation wants `kernel(handles, k)` at R4/R5 and `kernel(slab, handles,
   k)` at R1h/R2/R3, and `harness/dloop.py:361` **raises on arity**; ten
   alias/`call_args` combinations were tried and none reconciles them. **The one
   escape measured to work: give R4 a DEAD `slab` argument** (`identical? True`
   against the two-argument build). ⚠ Whether that survives `-O3` codegen is
   **unmeasured** — check it in `§0` before committing to the shape.
3. **The R5 catcher is an ordinary SMT obligation**, not linearity — see the
   retraction above. Two gate-style mutants on a zero-trusted-item file **do
   fail** (6 verified / 1 errors each), so the two-failing-mutant requirement is
   satisfiable, which was an open question.

**The proof half is SETTLED and cheap**: the ghost split loop verifies 7/0 with
zero project-local trusted items at 150 ms, and the cost does not grow with the
slot count.

For raw pointers and manual memory, use `vstd::raw_ptr` (`PointsTo` permissions),
`vstd::simple_pptr`, or `vstd::cell::PCell` rather than growing the TCB. Prefer a
vstd-provided permission model over another `external_body`.

## A guard cannot be isolated as "needed only for termination" — and the reason is structural

**p22, TASK_071.** The obvious mutant — delete the capacity conjunct and expect
`decreases not satisfied` — **can never work**, and it is not a p22 quirk:

> **The guard reaches the measure through a LEMMA'S PRECONDITION, and Verus
> assumes a callee's POSTCONDITION even when its precondition fails.** So
> deleting the guard fails at the call site and the measure is never reached.
> The control is `m8_nolemma`: its invariant fails **before** the loop and it
> still produces **no `decreases` error at all**.

**Only breaking an invariant the measure itself consumes reaches the measure.**
p22's `m3_noempty` does, and fails **first** on
`decreases not satisfied at end of loop`. Measured with the full battery:
`m1` 3 errors (the first, `nfill <= TABCAP`, is **not** a termination
obligation), `m2` `loop must have a decreases clause`, `m3` 2 with the measure
first, `m7_isolate` surfaces an **arithmetic overflow** once the conjunct is
peeled — the conjunct is load-bearing three ways, so *"required only for
termination"* is not merely unproven, it is **false**.

⚠ **`--multiple-errors` is not optional on any pattern whose result is a claim
about WHICH obligation fires.** Verus prints *"not all errors may have been
reported"* and stops at one; p22 published a mutant battery twice before anyone
ran with the flag. Set it **module-level** in the control so it cannot be dropped
at a call site.

## `decreases` on a ring loop: the ghost unwrapped cursor

This file's open problem — *"`decreases b - a` fails on two-cursor loops"* — has
an answer for **wrapping** loops (p22). A probe index `i = (i + 1) % CAP` does not
decrease in any direction, so:

- carry a **ghost** unwrapped cursor `u` with the invariant `i == u % CAP`;
- obtain a **ghost witness** for the terminating condition (p22: an EMPTY slot,
  from `nfill < CAP` by a counting lemma);
- `decreases i0 as int + d - u`.

**All ghost, so `R4 ≡ R5` stays `exact` and the termination proof costs ZERO
instructions.** ⚠ **And it is not free in a different currency**: the exec-code
alternative (a bounded probe counter) is **334.16 `Ir`/call CHEAPER** on p22's
large band, so *"the ghost proof saves instructions"* is **false**. What the
ghost route buys is that **R4 and R5 remain the same program**.

## Function pointers and trait objects (p36, TASK_072/073)

**`fn(u64) -> u64` IS NOT SUPPORTED AT THE PIN, AND THE ERROR IS ON THE
DECLARATION.**

```
error: The verifier does not yet support the following Rust feature:
       function pointer types
   |   const TABLE: [fn(u64) -> u64; 2] = [op_inc, op_dbl];
```

Not on the call — on the **type**. So a C function-pointer table has **no
admissible Rust rung** in this project, because the `identity` pin makes an R4 a
program that must have a verifying R5 twin. ⚠ **Do not read
`vstd/function.rs`'s `call_requires`/`call_ensures` as covering this**: that
machinery is for a **generic `F: Fn(..)` parameter**, and the guide chapter
(`exec_funs_as_values.md`) shows only that shape. It was the manager's premise
that it would reach a bare `fn` in an array, and it does not.

**The route that works, settled over fourteen probes:**

- `const TABLE: [&'static dyn Op; N]` — a **single**-trait object. It verifies,
  and it keeps each slot's dynamic type through an `external_body` accessor
  whose `ensures` is `r == TABLE@[i as int]`, i.e. it claims the **slot's
  identity only**; what calling it does comes from `Op::apply`'s own *verified*
  `ensures`. (The alternative — an `external_body` wrapper claiming
  `r == op_spec(i, x)` — also verifies and **axiomatises all eight bodies into
  the TCB**. Prefer the identity-only accessor.)
- ⚠ **A `static` is impossible twice over**: rustc wants `Sync` (`E0277`), and
  `dyn Op + Sync` is `dyn with more that one trait`. It must be a `const`.
- **Cost**: two dependent loads where C has one — **exactly `3.00000` `Ir` per
  dispatch**, measured, mechanism derived with zero fitted parameters.

⚠ **A `spec fn` DECLARED IN A TRAIT OCCUPIES A VTABLE SLOT IN THE ERASED
BUILD, IN DECLARATION ORDER.** Declare the exec method **first**, or R5's
dispatch becomes `call *0x20(%rcx)` where R4's is `*0x18(%rcx)` and the
`identity` pin fails at every level. Even declared correctly it costs 8 bytes of
`.data.rel.ro` per implementing type plus one emitted stub — see
`.memory/01-ladder.md` finding 1's **scope clause**, which this measurement
forced.

⚠ **`harness/vparse.py::duplicate_names` keys by BARE NAME**, so a pinned
`verus.rs` cannot define `apply` once per implementing type — eight
`impl Op for OpN` blocks **verify 19/0 and the gate refuses them**. Use one
generic `impl<const K: u8> Op for OpTag<K>`. This is a harness limitation, not a
Verus one (`parse()` already computes each item's enclosing impl); it is queued.

**And the twin regime has TWO teeth, which is easy to miss**: weakening only the
*trusted* item's `requires` leaves Verus silent (`12 verified, 0 errors`) and is
caught by the **gate**, under `--cfg slb_twin`. A mutant battery that only reads
Verus's exit status will score it as a no-op.

## Raw-pointer arenas: carving one permission into many (p31, TASK_079 — the axis was REFUSED, the vstd facts stand)

**Recorded because the probes verify and the next `raw_ptr` pattern will want
them, not because a pattern shipped.** All from `~/tools/verus/vstd/raw_ptr.rs`
at the pin. ✅ **The `6 verified, 0 errors` below is manager-verified** (re-ran
`./verus_run.py` on the probe); the surrounding readings are **PROVISIONAL —
not yet reviewed**.

**`PointsToRaw::split`/`join` are axioms and nothing in the tree uses them**
(`grep -rn '\.split(\|\.join(' patterns/*/verus.rs` → empty). They are also
**easy**. The full arena chain —

```
allocate(CAP, 8) -> (base, PointsToRaw, Dealloc)
expose_provenance(base) -> IsExposed
loop { raw.split(Set::range(lo, lo+8)) -> into_typed::<u64>(addr)
       with_exposed_provenance::<u64>(addr, exposed) -> ptr_mut_write }
```

— with a 6-conjunct loop invariant and an accumulating `Map<int, PointsTo<u64>>`
verifies **`6 verified, 0 errors`** with **zero lemmas, zero
`by(nonlinear_arith)`, zero set-theory lemmas**. `split`'s own
`range.subset_of(self.dom())` and `into_typed`'s `is_range` extensional equality
**discharge with no ghost help at all**. ⚠ **So "the tree has never split a
permission" is a statement about the tree, not about difficulty** — the proof is
**smaller than p27's** 15/0.

⚠ **`layout_of_primitives` gives `size_of` and says NOTHING about `align_of`.**
The one obligation that does *not* discharge is `into_typed`'s
`start as int % align_of::<V>() as int == 0`. The fix is one line:

```rust
global layout u64 is size == 8, align == 8;
```

Five patterns already ship a `global size_of usize == 8` directive (p10, p22,
p36, p38, p47); **only the `align ==` clause is new**, and vstd's own
`layout.rs` comment points at the directive. **Reach for `global layout` the
moment an alignment precondition appears** — it is not a lemma problem.

⚠ **The pinned vstd has NO exec pointer-offset function at all.** `raw_ptr`'s
exec surface is casts, read/write/ref, expose / with-exposed, and
allocate/deallocate. So an exec bump allocator must either thread an
**`IsExposed`** token (`expose_provenance` / `with_exposed_provenance` — **0 hits
tree-wide**, genuinely unused) or add a project-local `external_body` offset
wrapper at **+1 TCB**. The token threads exactly like p27's `Dealloc`, so it is
a new **clause**, not a new **kind** — which is what refused the axis.

## ⚠⚠ `is not supported` IS escapable — and the escape Verus PRINTS FOR YOU is VACUOUS

**Found at TASK_080 while refusing p45, and REVIEWED at TASK_081_REVIEW, which
found the recorded version wrong in the direction that matters.** The TASK_080
entry read *"`is not supported` is a TCB price for simple arithmetic intrinsics"*
plus *"Verus itself prints the fix"*. ⚠ **Both halves fail on the memory
operations, which are the ones finding 14 is about.** Manager-verified re-runs
below.

### The trap, first, because it is the part that can ship a false result

`assume_specification` **axiomatises** a function's contract, and **nothing in
Verus or in this project's gate checks it against anything.** Verus's help text
prints only the **signature** — no `requires`, no `ensures` — so a declaration
shaped like the printed one asserts the operation has **no precondition at all**.

Pasted as printed for `as_ptr` / `add` / `read_unaligned`, this verifies:

```
verification results:: 4 verified, 0 errors
```

and the four include **a 1 MiB out-of-bounds read off a possibly-empty slice**
and **a null-pointer dereference**. ✅ **Manager-re-run.** The reviewer
checklist's *"a wrong one axiomatises a falsehood"* lands here as
**"a missing one axiomatises everything"**.

⚠ **And it is one omitted line away on the arithmetic case that looked safe.**
Delete the `requires` from TASK_080's `unchecked_add` declaration, keep the
`ensures`, and `assert(false)` **verifies**. Compiled, a function whose `ensures`
says it returns `false` returns `true`, and the binary aborts with
`unsafe precondition(s) violated: i32::unchecked_add cannot overflow`.
**Verus verified a program that hits real UB on its first call.**

> **The rule: an `assume_specification` is a TRUSTED ITEM in the strongest sense
> — it is an axiom about real Rust semantics, written by hand, checked by
> nothing. Never paste the printed declaration. Write the `requires` first and
> prove it bites with a deliberately bad call site**, which is the one test that
> distinguishes an escape from a hole.

### What it actually costs, per item

**All six of finding 14's items are confirmed `is not supported` at the pin.**
The price is **not** `+1`:

| what you want | trusted items | note |
|---|---|---|
| a safe fn or an arithmetic intrinsic, one-line contract | **1** | `unchecked_add`, `unchecked_shl`; the `requires` bites |
| `from_raw_parts` | **1** | works first try and bites |
| **memory safety alone** on a pointer read | **4** | 1 `uninterp spec fn` + 3 `assume_specification`; `ensures` is empty, so the value read is unconstrained — **useless for a kernel with a functional postcondition** |
| **memory safety AND the value** | **6** | adds a cross-type little-endian representation axiom |
| `from_le_bytes` | **unreachable** | the array-length const has no writable spelling |

⚠ **The `+6` route cannot be avoided by monomorphising.** `assume_specification`
must match the real signature exactly — providing `(*const u64) -> u64` against
`for<T> (*const T) -> T` is refused — so relating a `u64` read to `u8` slice
bytes **forces** a hand-written representation axiom about real Rust memory,
which is the item carrying the most risk in the whole list.

⚠ **Three of the six printed help texts do not even parse** (`read_unaligned`,
`add`, `as_ptr`), one is malformed Rust (`from_le_bytes`) and one is rejected
(`TryFromSliceError`). `<*const T>::read_unaligned` *does* parse — **but you have
to know that**, and the message does not say it.

### What this does to finding 14

- ✅ **Finding 14's pricing stands** — the escape *is* the new trusted item, and
  at 4–6 items it is a **larger** price than the entry first recorded, not a
  smaller one.
- ⚠ **But its stated REASON is refuted**: *"every route to respelling a header
  read needs a new trusted item"* is false. **`vstd::slice::slice_subrange` +
  `vstd::bytes::u64_from_le_bytes` reads an arbitrary-offset LE `u64` with its
  value at ZERO author-written trusted items** — `2 verified, 0 errors`,
  manager-re-run. ⚠ **Its `Ir` cost is UNMEASURED** and `u64_from_le_bytes`
  wraps `try_into().unwrap()`, so it may be dearer than the shipped spelling.
  **Measure before claiming the R4 side moves.** See `RECAP.md` finding 14.
- ⚠ **p11's `r4_cstr` — the −35% case — DOES escape, all four items, first
  try** (`2 verified, 0 errors`). **But two of the four are TYPES, not
  `assume_specification`, and both functions are SAFE, so there is no `requires`
  to bite at all.** The supported sentence is therefore **"the unsafe class
  reaches `core::slice::memchr` at four hand-written axioms that no gate stage
  checks"** — **not** *"cannot reach it at all"*, and **not** that p11's finding
  flips. ⚠ `patterns/p11-nul-scan/NOTES.md` already contains **both** sentences,
  which is a contradiction that now matters.

## ⚠ `is not supported` may be right about the FUNCTION YOU NAMED and wrong about the question

(TASK_083_REVIEW, on p15. ✅ **Manager-verified — both runs.**)

**The same operation has a FREE path and an INHERENT path, and vstd may spec one
and not the other:**

```
core::str::from_utf8_unchecked(v)   ->  error: ... is not supported
str::from_utf8_unchecked(v)         ->  verification results:: 2 verified, 0 errors
```

`~/tools/verus/vstd/string.rs:136` ships
`pub assume_specification[ str::from_utf8_unchecked ](v: &[u8]) -> (res: &str)`
with `requires valid_utf8(v@)` and `ensures res.spec_bytes() =~= v@`, and
`~/tools/verus/vstd/utf8.rs:272` ships `pub open spec fn valid_utf8` as a full
recursive spec with `decode_utf8`.

⚠⚠ **So the diagnostic is CORRECT and the conclusion drawn from it can still be
false.** *"`from_utf8_unchecked` is not supported"* was true of the path that was
typed and false of the operation. **Before recording an item as unreachable,
grep the pinned vstd for the INHERENT spelling as well as the free one** —
`grep -rn 'assume_specification\[ *TYPE::NAME' ~/tools/verus/vstd/`.

**This is the same family as the 44-task false *"vstd has no spec for
`copy_from_slice`"***: a negative about the library asserted from one probe.
⚠ **Four patterns' R4 triages (p05, p07, p11, p18) rest on `is not supported`
messages that nobody re-ran against the inherent path.**

### Two smaller pins from the same task

- **A postcondition cannot mention a bare `v@` for a `&mut` parameter** at this
  pin — use `old(v)` / `final(v)`. Costs a run to rediscover.
- **`uninterp` with a body is a Verus error**, which is why body-less trusted
  declarations cannot be given twins — and therefore why feeding them to
  `_is_trusted` would make a legal declaration unpassable. ✅ Verified.

## ⚠⚠ A one-directional `ensures` on a validator is VACUOUS, and here is the measurement

(TASK_085 + TASK_085_REVIEW, on the `p15` probe. The row was refused; **this
result is independent of that and is the reusable half.**)

Writing a validator, the natural-looking contract is

```rust
fn is_valid_utf8(b: &[u8]) -> (res: bool)
    ensures res ==> valid_utf8(b@)          // ⚠ SOUNDNESS ONLY
```

⚠⚠ **A body of `false` satisfies it: `2 verified, 0 errors`, measured.** The
implication says *"if I accepted, it was valid"* and says **nothing** about
rejecting. A validator that rejects every input is certified by it.

**The bar is the equality:**

```rust
    ensures res == valid_utf8(b@)           // soundness AND completeness
```

**And that bar is reachable.** A verified UTF-8 validator closes at the pinned
vstd: **`5 verified, 0 errors`, ~120 lines of which ~10 are proof, ZERO trusted
items** — no `assume`, no `admit`, no `external_body`, no `assume_specification`.
The three vstd lemmas that do the work:

| lemma | role |
|---|---|
| `partial_valid_utf8_extend` | advance the prefix by one scalar |
| `partial_valid_partial_invalid_utf8` | reject |
| `partial_valid_utf8` | the **loop invariant** |

Both are directly callable proof fns — **no `broadcast use` needed**. Two
obstacles, both trivial and both worth knowing: **`i + 2 <= n` overflows** (write
`n - i >= 2`), and one `assert ... by (bit_vector)` is needed for
`codepoint_width_1(b) <= 0x7f`.

**How the obligation count decodes** (measured empirically, not assumed): a plain
`fn` is +1, a `while` loop is +1, and an `assert by (bit_vector)` is **+1**. So
the 5 above are `first_scalar_len` + its bit-vector query + `is_valid_utf8` + its
loop + `main`.

⚠ **The end-to-end call site is the part that was doubted and it closes too:**
`8 verified, 0 errors` for a kernel that calls
`unsafe { str::from_utf8_unchecked(b) }` guarded by the validator, with vstd's
`requires valid_utf8(v@)` discharged **from the validator's postcondition
alone**, plus a verified `drive(buf, n_iters)`.

**Non-vacuity, three ways, and the third is the one to copy.** A differential
oracle against **unmediated** `core::str::from_utf8` (18 499 985 + 316 602
independent cases, **0 mismatches**); a 10-mutant battery, **all 10 failing**,
of which **three break only the completeness direction**; and the `false`-body
control above. ⚠ **Do NOT build the oracle's expected value from the validator's
own width table** — that tests the transcription, not the semantics.

⚠ **One surviving equivalent mutant, recorded so nobody re-derives it:** dropping
the surrogate test from the **width-4** branch still verifies, because a 4-byte
encoding already has `cp >= 0x10000`. The validator carries one provably dead
comparison.

✅ **The pinned `vstd/utf8.rs` is a real spec, not a shape check** — it rejects
**overlongs** (`:206`), **surrogates** (`:214`) and **> U+10FFFF**. A
*structural-only* validator (continuation shape, no overlong/surrogate
rejection) **cannot** discharge it: `1 verified, 3 errors`, and its call site
fails `precondition not satisfied` outright — **R5 cannot make the unsafe call at
all.**

## ⚠⚠ The gate forbids VERIFIED unsafe — and that rule is LOAD-BEARING

(TASK_085_REVIEW blocker 1. ⚠ **The reasoning is a code read plus a tree census;
the end-to-end gate demonstration is still owed.**)

`check.py::_scan_unsafe_sites` requires **every `unsafe` token in a pinned Verus
source to sit inside an `#[verifier::external_body]` item**. Census: **47
`unsafe` tokens across 22 `patterns/*/verus.rs`, all inside `external_body`, zero
outside**, and **all 45 unsafe-bearing wrappers carry a non-empty `requires`**
(structurally enforced by `_check_trusted_unsafe`).

⚠ **It looks backwards** — an operation whose precondition Verus *discharged*
gets pushed into the *trusted* column. **It is not.** `_axiom_items` matches
**declarations**, so a pattern that merely **calls** a vstd
`assume_specification` declares nothing, shows `trusted 0 / axioms 0`, and
`check_miri` then **prints** *"no trusted `ensures` whose incompleteness Miri
would have to backstop — Miri not required."* Over a call licensed by
`vstd/string.rs`'s `assume_specification[str::from_utf8_unchecked] … ensures
res.spec_bytes() =~= v@`, **that sentence is false**, and the `ensures` in
question is verbatim what a wrapper would have written. **`_scan_unsafe_sites` is
the only thing standing between that hole and a green verdict.**

✅ **Why it has cost nothing so far:** `grep -rn "get_unchecked"
~/tools/verus/vstd/` → **0 hits**. vstd specs **none** of the operations the tree
uses, so all 47 wrappers were unavoidable. **`p15` is the first row where vstd
DOES spec the operation — which is exactly why it is the first row the rule
bites, and why it is refused** (`.memory/06-catalogue.md`).

⚠ **Correction to a claim made in passing:** `_is_trusted` requires
`external_body` **AND** (`ensures` **or** `unsafe` in the body) — **not
`external_body` alone.**

⚠⚠ **AND THE MANAGER'S INFERENCE FROM THE CENSUS WAS WRONG.** From *"47 tokens,
all inside wrappers"* the manager concluded *"in all 22 patterns the unsafe
operation is TRUSTED, not PROVED."* **Refuted by name:**
`patterns/p27-handle-table/verus.rs`'s `rec_free` wraps
`unsafe { std::alloc::dealloc(p, layout) }` behind a **six-clause `requires`**,
and its call site `rec_close` is a **verified** fn that discharges it from
tracked permissions whose facts come from **verified** `rec_open`'s `ensures`.
Weaker instances: p36's `tab_get_unchecked`, p03's `stack_set_unchecked`, p09's
shadowed accessor. **What is trusted is the IMPLICATION; the ANTECEDENT is
already Verus-discharged at ~130 call sites.** That is the correct sentence.

- ⚠ **`str::chars` IS spec'd in the pinned vstd** — `string.rs:465`,
  `assume_specification[ str::chars ] … ensures IteratorSpec::remaining(&iter)
  == s@`, plus `into_iter_elts` (`:462`) and `impl IteratorSpecImpl for Chars`
  (`:473`). **A verified DECODE fold over a `&str` is available**, not just
  validation. Sixth instance of *"grep the pinned vstd first"*.
- `s.spec_bytes()` needs `use vstd::string::StringSliceAdditionalSpecFns;` —
  **`vstd::prelude::*` does not bring the trait in.** Costs two runs.

## ⚠⚠ WHEN A VERUS OBLIGATION IS HARD, IT IS ALMOST NEVER THE MATHEMATICS. IT IS THE CONTRACT SHAPE OR THE API SHAPE.

**PROVISIONAL — three probes, TASK_086 / TASK_090 / TASK_091, unreviewed.**
**This is the manager's prediction record turned into something useful: 0 for 3,
and the three misses have ONE shape.**

| row | the manager predicted the hard part was | what it actually cost | where the difficulty really was |
|---|---|---|---|
| **p23** quicksort partition | the two-index multiset loop invariant | **`4 verified, 0 errors` FIRST ATTEMPT** | nowhere — it was the easy part |
| **p24** binary heap | `heapify`'s loop invariant | **no proof at all**; one `assert` before the loop | `sift_down`'s invariant is **not inductive** — the swap raises `v[i]` and can break `heap_at(parent(i))`, needing a **parent-dominance conjunct** |
| **p28** intrusive DLL | the address-**injectivity** conjunct | **one 8-line `proof fn`, one `if`, no loop, no induction** | (1) the struct needed **EXEC fields** it only had in ghost — a **contract change**; (2) `is_disjoint` takes **`&mut self`** and so **cannot be called inside `assert forall|i| … by`** |

**The rule that falls out, and it is actionable when SCOPING a row, not after:**

- ⚠ **Ask what EXEC STATE the proof needs that the contract does not yet
  carry.** p28's `push_front` had to branch on *"is the list empty?"* and the
  length existed only in `Ghost`. **That is a `spec.md` change, and it is
  invisible if you only look at the invariant.**
- ⚠⚠ **Ask whether the vstd API can be CALLED WHERE YOU NEED IT.** A `&mut
  self` method cannot appear inside a quantified `assert forall … by`. **This is
  not a hint problem and no amount of proof-hint fiddling fixes it** — it is a
  goal-reformulation problem, and p28's probe called it *"the trap that would
  have burned a session."* **The fix was to reduce a per-element quantified goal
  to a single `dom` fact.**
- **The mathematical invariant is usually the part Z3 is good at.** Three for
  three, the "obviously hard" invariant was not the cost.

⚠ **A corollary worth pricing in: STRENGTHENING an invariant to make one proof
legal makes every OTHER proof over it harder.** p28's extra key-discipline
conjunct made `unlink` — already proved — need new work to survive.

## ⚠ The anti-vacuity clause is never the headline clause

**Three instances now, and in each the clause whose deletion admits a degenerate
body is NOT the one the row is about:**

| row | the headline `ensures` | the clause actually carrying the anti-vacuity weight | what passes without it |
|---|---|---|---|
| **p15** | `res == valid_utf8(b@)` | **the `==` rather than `==>`** | a body of `false` — `2 verified, 0 errors` |
| **p24** | `is_heap(final(v)@)` | **the multiset clause** | a body that **zeroes the array** |
| **p28** | `wf()` preserved by `unlink` | **the address-injectivity conjunct** | **ONE node with `prev = next = itself`**, declared `len = 3`, `ptrs@ = [p,p,p]` — and it discharges `unlink`'s *entire* precondition |

⚠ **So the vacuity probe is not "is the postcondition true?" but "what is the
CHEAPEST body that satisfies it?"** Write that body and run it. **Every one of
these three was found by a probe that tried, and none by reading the
postcondition.**

## ✅ A MUTABLE SUB-SLICE IS USABLE AT THE PIN — and the bridge is one lemma

**TASK_089_REVIEW + TASK_092, manager-verified. This entry exists because the
opposite was claimed and landed.**

`~/tools/verus/vstd/std_specs/slice.rs` ships

```rust
pub assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>::index_mut ]
    (i: Range<usize>, slice: &mut [T]) -> (r: &mut [T])
    ensures  r@ == old(slice)@.subrange(i.start as int, i.end as int),
             final(r)@ == final(slice)@.subrange(i.start as int, i.end as int),
             forall|j: int| !(i.start <= j < i.end) ==> final(slice)@[j] == old(slice)@[j],
```

— **a full VALUE-LEVEL specification**, plus `<[T]>::split_at_mut` and
`ref_mut_array_unsizing_coercion`.

⚠⚠ **`vstd/slice.rs`'s `ExSliceIndex` TRAIT DECLARATION carries a `requires` and
no `ensures`, AND IT IS NOT THE SPECIFICATION.** Reading it and concluding *"the
pin cannot specify a mutable sub-slice — frame provable, value not"* is the
**`copy_from_slice` failure mode recurring**, and it reached a shipped
`spec.md`'s hashed `why`. **`CLAUDE.md` now names `std_specs/` for this reason.**

**The recipe, from a full R5 that closes at `21 verified, 0 errors`:**

- take a **ghost mirror** `let ghost gout = out@;` **before** the borrow;
- carry `row@ == gout.subrange(i, i + m + 1)` **plus a frame clause** in the loop
  invariant;
- call **`vstd::seq::lemma_seq_subrange_index`** once per use, and **once more
  after the borrow ends** to turn `final(r)@ == final(slice)@.subrange(..)` back
  into `out@ =~= gout`.

⚠ **The path is `vstd::seq::`, not `vstd::seq_lib::` — the latter is private.**

⚠ **What DOES disqualify such a spelling, measured on p46, and neither reason is
a specification gap:** it needs **`get_unchecked`, which has 0 hits anywhere in
the pinned vstd**, so R5 must add two new trusted items (TCB 5/3 → 7/5); **and**
its R4/R5 pair measures **`differ` at `-O3`** against an `identity: exact` pin.

## ⚠⚠ RETRACTED AT TASK_109 (REVIEW): VERUS **CAN** STATE LEAK-FREEDOM — A GHOST LEDGER DOES IT AT ZERO COST

> ~~**VERUS AT THE PIN CANNOT STATE LEAK-FREEDOM**~~ — **FALSE.** The heading
> below is kept because its *premise* is true and its *conclusion* is not.

**The affine premise holds and reproduces**: `Tracked<Dealloc>` really is
affine, a proof really may drop it, and the committed control's two arms behave
exactly as published. ⚠⚠ **What does not follow is "Verus cannot".**

✅ **THE ENCODING THAT WORKS, and it is the better finding: NEVER HOLD A BARE
`Tracked<Dealloc>`.** Escrow it into a **tracked `Map<int, Dealloc>`** —
`led_alloc` deposits, `led_free` withdraws — and the function's `ensures` says
**the ledger's domain comes back empty**, checked on every exit including early
returns.

```
verus_ledger_nosig.rs                        -> 18 verified, 0 errors
verus_ledger_nosig.rs --cfg p42_ledger_leak  -> 17 verified, 1 errors
    postcondition not satisfied: final(led).dom() =~= Set::<int>::empty()
    at this exit:  return 0;          <- exactly the error path's dropped release
```

⚠ **The non-obvious step: KEYING BY ADDRESS FAILS.** `vstd`'s `allocate` never
promises the address is not already escrowed, so both exits fail. **A ghost `int`
key works**, and `!old(led).dom().contains(k)` is discharged by the caller for
free. ⚠ **Neither wrapper is `external_body`** — both are verified functions over
the pattern's existing trusted `dig_alloc`/`dig_free`.

**It costs nothing measurable:**

| | shipped R5 | ledger R5 |
|---|---|---|
| verification | 15 verified, 0 errors | **18 verified, 0 errors** |
| `external_body` / axioms | 5 / 0 | **5 / 0 — unchanged** |
| `md5_fn`, `md5_raw` | — | **IDENTICAL to the shipped R5, and to the shipped R4** |
| identity | — | **`exact`, `md5_raw_equal: True`** |

**The only pin that moves is `verus.obligations`, 15 → 18.** ⚠ **And the stated
obstacle — *"it changes the kernel's signature"* — is avoidable in three lines**:
keep the ledger a local inside `kernel` and push the obligation onto an
`#[inline(always)]` body, leaving the pinned signature and `driver.canonical`
untouched.

⚠⚠ ~~**THE HONEST CLAIM, and it is more interesting than the retracted one:**~~
**RETRACTED AT `TASK_116`, MANAGER-VERIFIED. THE SENTENCE BELOW IS FALSE.**

> ~~**The natural encoding does not state leak-freedom; escrowing the token does —
> and the residual trust is that nobody bypasses the wrapper. That is a
> MODULE-LEVEL DISCIPLINE, not a global guarantee.**~~

⚠⚠ **ESCROWING DOES NOT STATE IT EITHER. THE LEDGER'S `ensures` IS SATISFIED BY
A LEAKING PROGRAM**, and the substitution is one line in place of `led_free`:

```rust
proof { let tracked _dl = led.tracked_remove(0int); }   // drop the token, never free
```

`18 verified, 0 errors`; `21 verified, 0 errors` under `--cfg slb_twin`;
**obligations, twin count and axioms all UNCHANGED**; leaks exactly
`n_err × win_len` = `model.py::leak_bytes`. ⚠⚠ **And its `-O3` kernel is
BYTE-IDENTICAL to the shipped R4 with p42's bug planted — `md5_fn
d3f1194cb10bce2057e0e1f3e28c1e21`, `n_fn 128`, both.** ✅ **Manager re-ran all
four; `.temp/mgr115/p42/REBUILD.sh` regenerates them.**

**The mechanism:** `Map::tracked_remove` is the call `led_free` itself makes.
⚠⚠ **WRAPPING AN AFFINE RESOURCE IN A MAP DOES NOT MAKE IT LINEAR — IT MAKES THE
DROP TAKE ONE MORE LINE.** Assigning `Map::tracked_empty()` over the ledger
verifies as well, which refutes *"a proof cannot drop the MAP that holds it"* in
its own words.

⚠ **WHAT IS NOW TRUE, stated carefully so this is not retracted a third time:**
**one ENCODING is refuted; INEXPRESSIBILITY IS NOT PROVEN and is OPEN.** ✅ **The
live repair lead, measured: a module-local `Tracked<Freed>` receipt is FORGEABLE
in proof mode (`3 verified, 0 errors`); a PRIVACY-SCOPED one is NOT — rustc
rejects the forgery. Unbuilt.** ⚠ **A `Tracked<T>` obligation is only as strong
as the smallest scope that can construct a `T`** — that is the reusable rule, and
it is what both failed encodings missed.

✅ **CLEAN NEGATIVE, and it SURVIVED the review on stronger evidence: THERE IS NO
LINEAR (must-consume) TRACKED MODE AT THE PIN.** `strings ~/tools/verus/rust_verify |
grep -oE 'verifier::[a-z_0-9]+'` gives **22 attributes and none is one** (⚠ **this
said 23; corrected at `TASK_110`, and the correction did not reach this file
until `TASK_116` caught it**); `grep -rn affine ~/tools/verus/vstd/` → **0 hits**,
confirmed against `vstd/std_specs/` as well; the guide's *"linear ghost state"* is
a name, not a mode. **That was the second route named at TASK_104 and it genuinely
does not exist.** ⚠ **But note what the negative does and does not buy: no linear
mode means the ledger CANNOT be repaired by an attribute — the repair has to come
from PRIVACY, which is a Rust-level mechanism, not a Verus-level one.**

⚠⚠ **THE FAMILY OF THREE SURVIVES, AND `p42`'s MEMBERSHIP IS NOW
UNCONDITIONAL.** `p47` and the stack-overflow case are untouched. **`p42`'s
shipped R5 does not cover its own bug class — that was true when the sentence
was hedged and it is true now**, ⚠ **but the REASON has been retracted twice and
must NOT be restated as either *"the prover cannot"* or *"the encoding chosen"*.
Both were asserted and both fell.** ✅ **The supportable form, UPDATED AT `TASK_118`: ~~TWO~~ **THREE** encodings have
been tried and **ALL THREE** admit a leaking program that verifies.** ⚠⚠ **THE
PRIVACY-SCOPED LEAD WAS BUILT AND IT FAILS.** It blocks every attack that killed
encoding 2 — `atk_remove` is `error[E0616]: field `m` … is private`, **blocked by
RUSTC and not by Verus** — and then loses to a different one:

```
mustfire_err2        18 verified, 1 errors   escrow in a ledger kbody WAS HANDED   -> REJECTED
atk_decoy_err        19 verified, 0 errors   escrow in a ledger kbody MINTS ITSELF -> ACCEPTED
atk_decoy_err_freed  19 verified, 0 errors   same local ledger, BOTH paths free    -> floor
leaked 1284 / 1652 / 1028 / 1044 vs a constant 1028 floor == model.py::leak_bytes, all four inputs
```

✅ **Manager re-ran this; `.temp/t118/decoy_err.py` regenerates it.** ⚠ **Two arms
differ in exactly ONE respect — WHICH LEDGER — and the one that mints its own
verifies while leaking.**

⚠⚠ **THE RULE, and it is the shape of all three failures — PROVISIONAL,
`TASK_118`'s reading, UNREVIEWED (rule 9; the CONCLUSION is manager-verified, the
RULE is not): PRIVACY MAKES A LEDGER'S *CONTENTS* UNFORGEABLE AND CANNOT MAKE THE
LEDGER *UNIQUE*.** **The postcondition certifies only that the author wrote
*something* on each exit that empties a map the author controls — the gap is one
proof line wide, in three places.** ⚠ **The ledger's PRICE was always right (+3
obligations, 0 TCB, 0 `Ir`); its PRODUCT is nothing.**

⚠⚠ **WHETHER A FOURTH WORKS IS STILL OPEN, AND THREE DATA POINTS ARE NOT AN
IMPOSSIBILITY PROOF.** ⚠ **Do NOT write that Verus cannot state it — that exact
sentence is retraction 1 and restating it would be the fourth.** **One unbuilt
lead is recorded rather than pursued: `dig_alloc` + `led_new` private to
`mod res`, with `res::run`.**

⚠ **Do not cite `p42` as evidence that a prover cannot express a resource
property** — and equally, ⚠⚠ **do not cite it as evidence that a ghost ledger
CAN. That is the claim that just failed.**

⚠⚠ **AND THE STRUCTURAL LESSON IS THE ONE TO CARRY, because it is not about
`p42`: NOTHING IN THE GATE CHECKS THAT AN `ensures` MEANS WHAT ITS PROSE SAYS.**
The gate was green, the record reproduced, `verus.obligations` was pinned and
matched, the twin count matched, the identity pin held — **and the central
positive claim was false.** ✅ **The shipped tree was safe anyway, and it is
worth knowing why: the `identity` pin catches the attacked R5 at both pinned
levels. THE PIN PROTECTED `p42`, NOT THE PROOF.** ⚠ **An obligation count tells
a reader how many things were proved and nothing at all about what they say** —
which is exactly what a reader assumes it tells them, and is the same lesson
`p42` already carried in the other direction (deleting the ledger's
leak-freedom `ensures` still gave `18 verified, 0 errors`).

---

**Superseded text, kept because its premise is right:**

## ~~VERUS AT THE PIN CANNOT STATE LEAK-FREEDOM~~ — `Tracked<Dealloc>` IS AFFINE, NOT LINEAR

**TASK_104 (p42), PROVISIONAL — unreviewed.** ⚠ **This contradicts the manager's
task file, which asserted the route was "precedented" because `p27` already
proves a deallocation obligation.**

**Measured, with a committed must-fail control (`controls/affine_leak.rs`): an
R5 that FORGETS the error path's `deallocate` verifies with `0 errors`.** The
ownership tokens are **move-only (affine)**, so **dropping one is legal**.
⚠ **`p27` proves deallocation is LEGAL — that there is no double-free and no
use-after-free. It never proves deallocation HAPPENS.**

> ⚠⚠ **`p42` IS THE FIRST PATTERN IN THIS TREE WHOSE R5 PROOF DOES NOT COVER ITS
> OWN BUG CLASS.** The proof is sound and says nothing about the defect the
> pattern exists to exhibit. **Miri is what stands behind the Rust side**, so the
> deleted-`dig_free` positive control ships with the pattern and fires.

⚠⚠ **THIS COMPLETES A FAMILY OF THREE, AND THE FAMILY IS THE RESULT — the proof
discharges exactly what it says and the program is still broken:**

1. **`p47`** — the proof certifies a **leaking** kernel (finding 31).
2. **A termination proof does not bound the STACK** — `decreases` verifies
   `3 verified, 0 errors` and the binary dies of `fatal runtime error: stack
   overflow` at depth 1e6 (`TASK_102`).
3. **`p42`** — an affine deallocation token does not force deallocation.

**Each is a resource the type of the obligation simply does not mention.**
⚠ **Before claiming a proof covers a bug class, ask which resource the
obligation quantifies over.**

⚠⚠ **SCOPE, AND IT IS THE ENGINEER'S OWN CAVEAT — DO NOT OVERSTATE THIS.** The
claim is about **the default encoding**, not about Verus. **A ghost ledger and
Verus's linear mode were both NAMED AND NOT BUILT.** The measured statement is:
*at the pin, with `Tracked<Dealloc>` as `p27` uses it, a dropped token verifies.*
**Whether leak-freedom is expressible by some other encoding is OPEN.**

## Pinned-vstd gaps found while building `p42` (TASK_104, PROVISIONAL)

- **`from_raw_parts` — 0 hits anywhere**, including `std_specs/slice.rs`. **There
  is no route from a raw allocation to a `&mut [T]`**, so R4/R5 must use
  `PointsToRaw` / `PointsTo` directly — `p27`'s route, with no slice shortcut.
- **No `size_of::<[T; N]>()` axiom**, which closes the cheap R5 route.
- **`with_addr` and `addr` ARE specified; `add` and `offset` are NOT.**
