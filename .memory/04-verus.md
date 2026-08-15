# Verus working notes

Read `../LearnVeri/PITFALLS.md` before debugging anything. Grep
`../LearnVeri/_VERUS_DOC_/vstd/` for exact signatures and available lemmas
instead of guessing; `../LearnVeri/microbench/` has 20 worked CVE proofs to lift
technique from.

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

**Count every `external_body` item, not just the interesting one.** The pilot was
published as "TCB: one 3-line `get_unchecked` wrapper"; the true tally is **3 items**
— `get_unchecked`, `out` (the `println!` wrapper) and `main`. Under-counting is how
the pilot's fatal defect hid in plain sight: `main` being `external_body` is exactly
why no precondition was ever discharged (`.memory/02-bench-rules.md`, rule 2). An
`external_body` on a *driver* is far more dangerous than one on a leaf helper,
because it deletes call-site obligations wholesale. List them individually.

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
2. **Every item's `external` attribute, `requires` and `ensures`, verbatim**, and
   the item *set*. This is what catches the two mutations that move no count at
   all: a tautological `ensures` (`r == r`) and a deleted `external_body`
   `requires`. Demonstrated at TASK_003 — both gave `5 verified, 0 errors` and a
   green gate before, and both now fail with the exact clause diff.
3. **`verus <file> --verify-function <name> --verify-root`** answers "does this
   function have a verified body?" *semantically*. It reports `0 verified` for an
   `external_body` item and ≥1 for a real one, so the "rule 2" call-site check no
   longer depends on recognising an attribute. Useful in its own right when
   debugging: it tells you which item an obligation belongs to.

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

## Proof techniques that keep coming up

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

For raw pointers and manual memory, use `vstd::raw_ptr` (`PointsTo` permissions),
`vstd::simple_pptr`, or `vstd::cell::PCell` rather than growing the TCB. Prefer a
vstd-provided permission model over another `external_body`.
