# TASK_008 — close the two gate bypasses, then harden 5c and the floor

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_006_REVIEW.md` (this task
is its remediation — **every finding below is already demonstrated there, with
the mutant and the command output**), then `.memory/02-bench-rules.md` and
`.memory/04-verus.md`, which the manager has already corrected.

**Do not re-apply the `.memory/` edits.** Your job is `harness/`, plus the p01
and p02 files named in Part E.

Both blockers were demonstrated with a **fully green `check.py` and, for
blocker 1, a `contract sha256` identical to the shipped pattern**. That is the
third and fourth time this project's gate has certified nothing. Treat the gate
as the thing under test.

The reviewer's mutants and logs are in `.temp/review006/`, including a
repo-layout mirror at `.temp/review006/patterns/p02m-buffer-copy/` that runs the
whole gate on a mutated copy without touching `patterns/`. **Reuse it** — the
harness for reproducing all four findings already exists, and rebuilding it is
wasted effort.

## Part A (blocker) — a rung can fake `verus!` and enter the ghost-strip harbour

`harness/vparse.py:149` accepts `r"\bverus!\s*[{(\[]"`. `harness/check.py:937`
guards with `r"\bverus!\s*\{"` — brace only. So:

```rust
macro_rules! verus { ($($t:tt)*) => { $($t)* } }
verus!(
fn main() { ... SLB-DRIVER-BEGIN ... );
```

makes `region_in_verus == True` in a plain-Rust rung, and is invisible to the
"a file with a `verus!` block must be listed in `verus.obligations`" check. The
M9 prefetch payload goes straight back into `safe_naive.rs`'s measured loop:
407.0 → 412.0 Ir/call on `small`, `prefetch` present in the disassembly,
checksums unchanged, **gate PASS with an identical contract hash**.

**Do not fix this with a better regex.** A third regex over the source is how
the first two were defeated — and note the *brace* form is already caught, so
the tree already contains the "add another pattern" fix and it did not
generalise. The question the gate must ask is semantic: **was this file compiled
by Verus?** The gate already knows — it runs Verus on the files in
`verus.obligations` and gets an obligation count back. Gate the ghost-stripping
path on *that fact*, so a file Verus never saw can never reach it, whatever it
spells its macros.

Fail closed: a rung claiming a `verus!` region that is not in the verified set is
a hard failure, not a downgrade to non-ghost normalisation.

Demonstrate afterwards: the paren form, the bracket form (`verus![...]` —
untested by the reviewer, the regex accepts it), and the brace form all fail,
and `patterns/p02-buffer-copy` still passes.

## Part B (blocker) — stage 5c never tests `requires`

`harness/check.py:1272` iterates `it.clauses.get("ensures")` and nothing else.
All three of these give **9 verified, 0 errors** on p02, with the obligation
count unmoved at 9:

| mutant | result |
|---|---|
| delete `from + n <= src@.len()` from `copy_bytes` | 9 verified, 0 errors |
| `get_unchecked`: `i < v@.len()` → `0 <= i` | 9 verified, 0 errors |
| `copy_bytes`: both `requires` → `n >= 0` | 9 verified, 0 errors, **full gate PASS** |

The structural rule at `check.py:866` is satisfied by the tautology and prints
it approvingly: *"trusted `unsafe` item `copy_bytes` demands `['n >= 0']` of
every caller"*. R5's trusted base then axiomatises that an arbitrary
`copy_nonoverlapping` is defined — the exact CWE-787 p02 exists to model.

**The `requires` test is the mirror image of the `ensures` test.** Deleting a
postcondition should make the file fail. Deleting a precondition makes
verification strictly *easier*, so nothing fails — the check is: delete or
weaken it, re-run, and **fail if the file still verifies**, because that means
no call site was relying on it. Implement it for every `requires` clause of
every `external_body` item and of the pinned kernel item.

A tautological `requires` must also be caught, since deletion and
`replace-with-`true`` are the same test. `n >= 0` on a `usize` is `true`; so is
`0 <= i`. You do not need a general tautology detector — the deletion test
subsumes it if you compare against the *unmutated* control, because a clause
whose removal changes nothing is exactly a clause that was doing nothing.

## Part C (major) — `&&` defeats whole-clause deletion

`vparse._clause_split` splits on top-level commas only. Re-joining a redundant
conjunct with `&&` makes 5c delete both halves at once, the file fails to
verify, and the stage certifies the clause load-bearing. Demonstrated: adding
` && final(dst)@.len() == old(dst)@.len()` back onto p02's `copy_bytes` gives
`ensures[0] load-bearing (8 verified, 1 errors)` and a green gate, while
deleting *only* that conjunct reproduces the shipped file at 9 verified, 0
errors.

Split at top-level `&&` as well as at top-level commas, for both `requires` and
`ensures`. Watch the precedence and the `==>` / `&&&` / `||` forms — a conjunct
split out of an implication's antecedent is not a deletable unit. If a form is
ambiguous, **fail rather than guess**, and say which forms you refused.

This one is latent: p02's shipped fix is a genuine deletion, not a
reformatting. Confirmed by the reviewer; do not "fix" `verus.rs` for it.

## Part D (major) — the floor's knobs are unbounded

`check.py:660-681` rejects `min_ir_per_work <= 0` and nothing else.
`min_ir_per_work = 1e-9` with `why = "see NOTES.md"` passes, printing "derived
floor 0.0 Ir/call" and "tightest margin 2246270772.2×". Nothing inspects `why`.
`work_per_call` is a second unbounded knob in the same sandboxed file.

Bound them:

- an absolute floor under `min_ir_per_work` below which the gate fails outright
  regardless of justification — the physical argument is in
  `.memory/02-bench-rules.md` (glibc `memcpy` = 0.104 Ir/byte measured; p02's
  0.0625 is the fused AVX-512 lower bound). Nothing legitimate is below that;
- **print the achieved margin next to the declared floor in the verdict**, so a
  35.9× margin and a 2.2-billion× margin do not read identically;
- a declared floor more than some factor below the *measured* rate is
  self-defeating and should at minimum shout. You choose the mechanism; say why.

**Do not present this stage as an anti-collapse gate afterwards.** It rules out
total collapse and nothing finer — step 2, the model checksum, is what certifies
that the work happened. `.memory/02-bench-rules.md` now says this; make
`check.py`'s own output say it too, so the next reader of a green log does not
over-read the line.

## Part E (minors) — fix and re-derive

1. `check.py:1204`/`:1269` — `clause_deletion_extra_items` drops unknown item
   names silently, so a misspelling exempts the kernel from 5c. Unknown name =
   hard failure.
2. **Five stale digests in p01, not one.** `patterns/p01-array-sum/NOTES.md:136-137`
   (and `.memory/01-ladder.md:71`, already corrected by the manager — do not
   touch it). Measured actuals: R2≡R2v O3 `md5_fn` `12d307f2b9d1`, `md5_raw`
   `f1e7f9511d86`; R2≡R2v O0 `bf555ac41318`; R4/R5 O0 `md5_fn`
   `78b8c557c474`/`a5bbe0c0f5ef`. Every *equality* still holds. Re-derive them
   yourself rather than pasting mine, and say which convention each is.
3. **Re-run `measure.py p01` and commit the refreshed JSON.** The kernel columns
   all reproduce — including `c-clang`/`unsafe` at exactly 143,740,000 on
   `large` — but `binary_text_bytes` is stale in 5 C cells (`common/driver.c`
   grew when p02 added `head2_u64_bytes`), and `c-gcc/O0/whole`'s `md5_raw` is
   stale with `md5_raw_norel` unchanged, i.e. link layout only. The recorded
   `git.commit` is three commits back with `dirty_files: 15`. Regenerate
   `results/tables/` too — the reviewer did not.
4. **Three overstatements to correct**, all in p02:
   - `NOTES.md:376` and `inputs/gen.py`'s docstring say the period was measured
     "over 72 consecutive lengths". The sweep is two runs of **34** (56–89,
     2040–2073). 34 rules out period 32; **72 is not a number in the data.**
     Say what was actually run and what it rules out.
   - `README.md`'s headline says R3 is "+10 at every one of [68 lengths]",
     contradicting its own `NOTES.md` §3 finding 1 and §3b table: it is **+8 at
     `len ≡ 0 (mod 8)`**, independently confirmed at 512/520/1000.
   - `NOTES.md` §3a quotes 11225.9/10210.9/10208.9/10200.9 where §3 and two
     independent re-runs give 11226.0/10210.8/10208.8/10200.8. One measurement,
     two tables, different numbers.

## Done when

- All four bypasses fail, each demonstrated with the actual gate output, and
  `check.py p01` / `check.py p02` are green on **complete** runs.
- Part A is fixed semantically (Verus's own verdict), not by a third regex, and
  all three bracket forms are shown failing.
- Part B's `requires` test flags the three mutants above; paste all three.
- Part E's numbers are re-derived by you, not copied from this file.

## Constraints

No root; no `/tmp` (scratch in `.temp/p008/`, and reuse `.temp/review006/`);
**no `git add`/`git commit`**; do not edit `pilot/` or the `.memory/` files.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N>` on long builds; a full `measure.py p01` run is ~7 minutes.

**If a prescription here is wrong, say so with the measurement.** Five engineers
have contradicted my instructions and all five were right; the last reviewer
also reported a clean negative result on one of my five predicted attacks, which
is exactly as useful. Do not manufacture agreement.
