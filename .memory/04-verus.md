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
   comparison is doing real work. Eight mutants fail for eight distinct reasons,
   including two beyond the original design: a twin missing its `#[cfg]` (it
   would compile into the measured binaries) and a twin whose body calls
   `get_unchecked` (it re-uses the axiom it exists to check).

   The `copy_from_slice`-has-no-vstd-spec wrinkle resolves cleanly: the copy twin
   is an indexed loop and it **verifies**, so a failure there is weakness, not a
   missing spec — and the gate prints the Verus diagnostic so the two can be told
   apart.

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

   **But the deletion probe is not the mechanism's perimeter.** TASK_009_REVIEW
   found three bypasses that never reach it and one blind spot that survives it.
   Do not describe the twin as closing the strength class.

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
     Its value accrues from p17 on.

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
- **`&mut [T]` works too** (established at TASK_004 on p02): `old(dst)@` /
  `final(dst)@`, `Vec::as_mut_slice` is `assume_specification`'d with a
  prophecy, and `dst[i] = v` has an `IndexSetTrustedSpec`. There is **no** vstd
  spec for `copy_from_slice`, so a rung that wants the bulk copy verified needs
  its own trusted wrapper around `ptr::copy_nonoverlapping` — which is the right
  answer anyway, because that wrapper *is* the pattern's trusted base and its
  contract is what a reviewer should attack.
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

For raw pointers and manual memory, use `vstd::raw_ptr` (`PointsTo` permissions),
`vstd::simple_pptr`, or `vstd::cell::PCell` rather than growing the TCB. Prefer a
vstd-provided permission model over another `external_body`.
