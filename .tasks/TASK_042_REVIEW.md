# TASK_042_REVIEW — p04 claims a general LLVM mechanism from ONE pair of capacities

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_042.md` (the spec — note
it was contradicted in three places and the engineer was right each time), then
**`patterns/p04-ring-buffer/NOTES.md` in full**, then its `spec.md`, `model.py`,
`inputs/gen.py`, `controls/gen_controls.py`, `controls/sweepfit.py`, and
`.memory/01-ladder.md` findings 6 (p05 — the multiply), 10 (p03 — the dead
clamp) and 11 (p09 — the shift, and the invisible bug).

p04 is the twelfth pattern: gate `PASS`, Verus `9/0` first run, twin `12/0`,
`R4 ≡ R5 exact`, TCB 10 lines / 5 items matching the gate's own count, 99 sweep
blobs at max residual 0.0000, **unreviewed**. Its `NOTES.md` is unusually
self-critical — it flags its own `order.py` `.bin` bug, its own unexplained row,
and its own missing layout population. **Treat that as a reason to look harder,
not softer**: the two highest-yield review targets on this project have been a
claim the engineer flagged against itself, and a mechanism asserted without a
control.

## 1. The headline is a general claim about LLVM built from N = 1. Attack it.

> **What LLVM carries around a loop-carried phi is known BITS, not a range.**

That sentence (`NOTES.md` §0a, §1, §4b, and `safe_naive.rs`'s doc comment) is
the unifying statement for a three-pattern series, and **it rests on exactly one
comparison: `RING_CAP = 64` against `RING_CAP = 60`.** Those two builds differ
in *at least* three things at once — the operator's lowering (`and $0x3f` vs a
magic-number division on one cursor and `cmp/cmovne` on the other), whether the
surviving fact is bits or a range, and whether the check is inside a loop at
all. **The published mechanism names one of the three.**

Three falsification experiments, in order of how much they would cost the
headline:

- **Is it the phi, or is the check simply never elided at 60?** Take the CAP=60
  kernel and put a single ring access in **straight-line** code with the same
  `% 60` immediately before it — no loop, no phi. If the check is deleted there
  and kept in the loop, "does not survive the phi" is earned. **If it is kept in
  both, the phi is not the mechanism** and the sentence is about
  range-propagation generally, which is a weaker and differently-shaped claim.
- **Separate the operator from the fact.** Spell the CAP=60 wrap as
  `if tail == 60 { tail = 0 } else { tail += 1 }` — a source-level branch that
  produces the identical `[0,59]` range with **no division and no `cmov`**. If
  the check now goes away, the 60-vs-64 gap was about the *lowering*, not about
  bits-vs-range. If it stays, the claim survives its sharpest test.
- **Get a third point on the axis.** Bits-vs-range predicts something specific
  and checkable: a **power-of-two capacity with a non-power-of-two array**, or
  `% 32` indexing a `[u64; 64]`, should still elide (bits give
  `tail < 32 < 64`); and a capacity like **96 or 48** — where the range is
  wide but the value is still not bit-constrained — should behave like 60 and
  not like 64. Two more capacities is one edit to `gen_controls.py`.

Also check the arithmetic that the mechanism is quoted from:
**`479 − 5 = 474 = 2.00000 × 237`**, with 237 = 119 writes + 118 reads on
`small`. Re-derive both counts from `model.py` yourself. And §1a's whole
cross-capacity comparison is licensed by *"`small`'s execution counts are
unchanged by the edit"* — **verify that replay independently**; if a 60-slot
ring rejects even one push on `small`, every CAP=60 number in the file is
comparing two different programs.

**And check the pads.** §0a and §1 say `ring[tail]`/`ring[head]` contribute
**zero** pads in every rung and that R3's single pad is the window reslice.
That is a `pads.py` `--source` decode, which is exactly the tool that overturned
p12's published mechanism *after* a count had been read the other way
(`.memory/03-measurement.md`). Re-decode it; do not re-count it.

## 2. "The shipped R3 is the cheapest found — a first" is a claim about a SEARCH

`NOTES.md` §10a says four in-contract spellings land on `+5`, and then says the
quiet part itself: **they land on the same number because they land on the same
machine code** (`md5_fn_norel b5040cb5d805`, all four). So the R3-side search is
**one point written four ways plus one dearer outlier**. On p03 a cheapest-found
was refuted twice, the second time *after a review had confirmed the first*.

The whole published tax is `+5.00`, flat, and `NOTES.md` attributes all of it to
**one window-reslice bounds check**. So the question is narrow and answerable:
**is there an in-contract R3 spelling that removes the reslice check?** Try at
least `&buf[off..][..len]`, `split_at`, `chunks_exact` on the *window* rather
than on the record, `get(..).unwrap()`, hoisting the reslice above the `len < 4`
guard, and an `assert!` on `off + len <= buf.len()` (p03's lever, which §10a
reports as byte-identical *at the loop head* — try it **before the reslice**,
which is a different position and is where p03's mattered). **If any of them
verifies as in-contract and measures `+0`, p04's headline number is 0.00 and
"the tax is one reslice check" becomes "there is no tax".** That is a better
result than the one shipped, not a worse one — say so plainly if you find it.

Check the exclusions against `.memory/01-ladder.md`'s direction test yourself.
§13 claims both exclusions move the published figure by **exactly 0.00** because
`m_mask` and `cap64_r3_clamp` are byte-identical to the shipped rung. Verify the
two `md5_fn_norel` values rather than accepting the table.

**Do not accept the R4 side as degenerate on three candidates.** Every one is
byte-identical to shipped R4. That is a plausible *result* here — the clamp
seeds a fact LLVM already has — but three candidates is a thin search, and
`.memory/01-ladder.md` records five published figures killed by the
*"run `verus_run.py` on the twin first"* rule, which p04 did follow. Try one or
two more admissible unsafe spellings; a fourth byte-identical result strengthens
the degeneracy claim rather than weakening it.

## 3. The invisibility result, and the unification that was NOT asked for

`m_nofull_msonly` and `m_noempty_msonly` both `9 verified, 0 errors`, against
five positive controls. This is the second instance of p09's result and the
first where the mechanism is claimed to be *visible in the invariant*:

> The relation between `head` and `tail` is exactly the part of the state the
> memory-safety obligation does not need — which is precisely why deleting
> either guard is invisible to it.

- **Vacuity first**, the way p09's review did it. Confirm each `_msonly` mutant's
  substitution actually landed (the exec code differs from `m_control_msonly`),
  that the kernel is still reachable from a verified `main`, and that the item
  counts match the control at 9. Then attack it your own way — p09's probe
  survived four vacuity attacks and was stronger for it. A named attack that
  does **not** land is worth as much as one that does (rule 6).
- **Is the unification a fact or a spelling of the invariant?** The claim is that
  *nothing* relates the cursors in the memory-safety argument. That is true of
  **this** kernel because every cursor update is `(x + 1) % RING_CAP`,
  unconditionally. **Construct the counter-shape**: a ring whose wrap comes from
  the guard instead of the operator (`if tail == CAP - 1 { tail = 0 } else
  { tail += 1 }` reached only under the fullness test, or a `head`
  that advances without its own `%`). If a memory-safety-only proof of *that*
  ring needs the relation, then §12c's *"a container whose indices are modular
  puts every interesting bug in the second class"* is a statement about **the
  modular update**, not about ring buffers — and the sentence that reaches
  `.memory/` should say so.
- `p1_weak_requires` **passes the shipped configuration at 9/0** and is caught
  only by `--cfg slb_twin`. That is the twin's second load-bearing catch on this
  project. Reproduce it, and check the claim that no other gate mechanism sees it
  (tautology probe, parameter coverage, deletion-not-applied-to-trusted-items).

## 4. The swept laws — seven models, zero residual, and one band-F licence

Re-derive at least two of the seven coefficient rows independently of
`controls/sweepfit.py` (a second implementation, or exact rational elimination on
a subset). Then the three things the fit rests on:

1. **Rank.** `POOLED 5/5`, every single band ≤ 3/5, **every pair ≤ 4/5**. That is
   the strongest form of the rank check anyone here has shipped — confirm it, and
   confirm the corollary the engineer used to contradict the task file: the two
   bands `TASK_042.md` specified (`sweep-n*`, `sweep-f*`) really are 4/5 and
   would not have identified the design.
2. **The band-F licence for the two R1 cells.** R1 has no fullness check, so on
   band F it does not run the model's program; the fit is justified by *"R1's own
   execution counts satisfy `pushes = xpush + dpush` on all 104 band-F windows"*
   plus the self-check that **R1's `xpush` and `dpush` coefficients come out
   equal** (18/18 gcc, 9/9 clang). Check the simulation, and check whether the
   equality is a real test or an artefact of a rank-deficient column pair — i.e.
   **could the fit have produced unequal coefficients at all, on this design?**
   If not, the "measured rather than asserted" claim is weaker than it reads.
3. **Out of sample.** `13·417 + 15·413 + 46 = 11662` against a measured 11662,
   3.5× outside every band. This is the evidence form this project weighs most
   heavily; confirm it on a *fresh* blob you generate, not on `large`.

`R2 − R3 = 20.00000·ops + 11` is claimed as **p03's law reproduced exactly on a
different kernel**. It is (`p03/NOTES.md:320` is character-identical). But p03's
`R2 − R4` carries an extra `3.00000·xpop` that p04's does not — **say what that
difference is**, because a cross-pattern reproduction that holds for one
difference and not its neighbour needs the boundary named.

## 5. The rest, in order

1. **§7.3: "R1's answer IS reproducible across runs."** The argument is that
   nothing R1 reads depends on an address because the ring is fully initialised
   before any pop. **Do not accept the argument — test it.** Run R1 under
   `valgrind --tool=memcheck` on `adversarial-overwrite` and on both matrix
   inputs (C's `uint64_t ring[64]` is *not* initialised), and re-run the binary
   enough times to make the reproducibility claim measured rather than reasoned.
   p03's analogous claim went the other way and it is one of that pattern's
   sharper findings.
2. **§1c's gcc row is unattributed.** At CAP=60 clang keeps the manual C check at
   exactly `1.00000` Ir per executed pop and **gcc costs `+717` Ir/call with no
   per-pop decomposition**. The three-middle-end claim is the strongest form
   p03's sentence has been given, so the one row that does not decompose is worth
   ten minutes on the listing.
3. **§4a's unexplained row**, flagged by the engineer: clang's R1h is `1.00000`
   Ir per executed pop *cheaper* than clang's R1, on an arm the check does not
   touch. Exact, small, and nothing rests on it — but it is exactly the shape
   that turns out to be a mismeasurement. Attribute it or confirm it is real.
4. **§11: p04 ships no layout population**, so there is **no mode-matched
   verdict** — and `small`'s published `R2 − R4` (+25.7%) is a *median over
   byte-identical copies*, i.e. read off the noise-floor control rather than a
   layout population. `.memory/03-measurement.md` and finding 16 are specific
   about what may be published from what. **Is that figure quotable as shipped?**
   The `R3 − R4` null is separately defensible (the `Ir` column predicts it) —
   check the two claims apart from each other. Also confirm the `t(n_iters=1)`
   correction and the decision to discard `small`'s corrected column entirely.
5. **TCB recount** (10 lines / 5 items) and the three SLB-TRUSTED-ARGUMENT
   blocks. `ring_set_unchecked`'s whole-sequence `ensures`
   (`final(v)@ == old(v)@.update(i, x)`) is claimed to be load-bearing *because
   R1's bug is a store to a slot the checked kernel does not write* — test that
   by weakening it to a slot-`i`-only clause and confirming what stops failing.
6. **§13's direction test and the phase-0 timing claim.** `spec.md`'s `idiom`
   block is claimed to have been written after the §0 probes and **before** any
   rung, input or `model.py` existed. You cannot verify wall-clock ordering from
   the tree — say so — but you *can* check that everything §13 lists as "known
   when it was written" is in fact only §0 material, and that nothing in the
   block pins a spelling whose number appears first in §3/§4/§10/§11.
7. **Is R2 a fair naive port?** (Reviewer checklist.) It is 20 Ir per operation
   dearer than R3 and that gap is the pattern's second-largest number. Read
   `safe_naive.rs` against what a working Rust programmer writes first.

## Clean negatives are worth as much as findings

PROTOCOL rule 6 — name the attacks that did not land so the next agent does not
re-run them. And if the bits-vs-range mechanism survives §1's three experiments,
**say so plainly and in general terms**: it is the closing statement of a
three-pattern series and hedging a confirmed mechanism is its own failure.

## Constraints

No root; no `/tmp` — scratch `.temp/r42/`, delete binaries and blobs when done,
keep the generators. **No `git add`/`git commit`** — read-only git. Do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, or anything under `patterns/`.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &` background jobs**;
no self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND,
interleaved by cell**; subtract `t(n_iters=1)` before any wall-clock ratio (±9
points); `harness/measure.py --check-stale` before quoting a record.
⚠ `common/layout/order.py` **appends `.bin`** — pass `--input small`, not
`small.bin`, or you will time a file that does not exist (`NOTES.md` §11).

Notes to `.temp/r42/NOTES.md`. Report in PROTOCOL's format, severity-ranked,
with file:line and a concrete failure scenario per finding.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Fifty-five agents have and all fifty-five were right — p04's own engineer
refuted three of my prescriptions (the invariant is not relational, two sweep
bands do not identify the design, and the interesting proof work does not exist).
What I am least sure of, and what I most want measured, is **§1: whether
"known bits, not a range" survives being separated from the 64-vs-60 codegen
difference.** I wrote that sentence into RECAP as the closing statement of the
multiply → shift → modulus series. If it is really "the check is not elided at a
non-power-of-two capacity, for reasons that include the lowering", the series
still has a result but it is a smaller one, and I would rather publish the
smaller true sentence.
