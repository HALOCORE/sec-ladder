# TASK_076 — land the synthesis review: the fix was in `git` the whole time

**Role:** research engineer (you built `synthesis/`; this is its corrections
task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_075_REVIEW_REPORT.md`
in full**, then your own `.temp/p75/NOTES.md` and `synthesis/README.md`.
⚠ **`.memory/03-measurement.md` and `.memory/01-ladder.md` finding 19 have
ALREADY been updated from this review — read them before you start**, because
three of the items below are now written there and you should cite rather than
re-derive.

**The review ran 48 named attacks and returned 1 blocker, 6 majors, 7 minors and
41 clean negatives.** ⚠ **Do not re-measure the 41.**

✅ **What SURVIVED, first, because the blocker reads like a demolition and is
not one:**

- **The artefact stands.** Every number in `results/synthesis.md` is unaffected
  by B1 — it invalidates a *provenance sentence* and §0's premise, not a figure.
- **`outward_ir.py` IS a sound oracle**, proven by two probes with independently
  known answers: callgrind records a **tail `jmp` as a `calls=` edge** (the blind
  spot you and the manager both suspected **does not exist**), and a
  two-call-site-plus-transitive case sums to `950,000` exactly matching
  `callgrind_annotate --inclusive=yes`, with the shared callee counted once.
- **Your attack on the scheduling argument is UPHELD and is not too strong** —
  p10/p12/p13/p18's `R3−R4` correction is **exactly 0.00** derived
  independently, and the `gcc-clang` census is upheld for **all seven**, not the
  three spot-checked.
- **Your reproducibility headline is CONFIRMED AND HARDENED** (see M1) — under a
  knob that actually works, it is `0 of 348` against `11 of 348`.
- **The search objection is sound**, and nothing in the file presents an
  entailment as a finding.

## F1 — BLOCKER. `synthesize.py::LICENCE_NOTE` says the licence cannot be derived from committed records. It can.

§2 prints *"The licence is not in the committed records and cannot be derived
from them."* **`results/gate/pNN.json` carries `marginal_ir_per_call`** per
`(cell, opt, mode, input)` — whole-program, therefore symbol-independent — so

```
(marg[A] − marg[B]) − (kex[A] − kex[B])   =   the callee correction
```

Scored over **176 rows**: **zero misses at every threshold** (2.0 Ir → 14 false
alarms, 3.0 → 10, 5.0 → 9), and it reproduces **every** large correction
independently — p11 `+9815.56/+7116.78`, p08 `−4152.92/−4488.90`, p09
`+379/+2626`, p13 `−190/−264`, p27 `+120.33/+130.95`, p47 `+88.37/+166.00`, p36
`+129/+1025`. Residual is **structured**: constant `+1.00` on every `gcc-clang`
row, `−1.00` on `R5−R4`. ⚠ **This is `.memory/03-measurement.md`'s own
prescribed *"author-checkable test, which needs no disassembly"*, and it is the
boilerplate in 22 of 22 `results/tables/*.md` — the same boilerplate you quoted
for p11.**

> **Make the marginal-derived correction the PRIMARY route**: `synthesize.py`
> computes it from committed gate records, so **the artefact becomes
> self-contained from `git`** and needs neither sidecar to produce a licence.
> ⚠ **Do NOT delete the sidecars** — the review is explicit that its
> recommendation is *derived column primary, sidecars as refinements*. The
> marginal route has a **±2 Ir floor (±16 on p07 and p22**, whose per-call work
> is data-dependent) and **demonstrably cannot resolve the ±7 `memset` or the
> +2 PLT thunk**. **State the floor beside the column.**
> **And fix the sentence**, which is the actual blocker: a false provenance
> claim in an un-gated artefact is what the next reader trusts instead of
> checking.

## The six majors

**M1 — the perturbation knob is INERT and "6 of 348" is a floor.** Valgrind
**strips its own options before building the client stack**, so lengthening
`--callgrind-out-file=` changes nothing; the review replicated your two paths at
exact length (97 vs 99 chars) and got identical `kex` *and* `outward`.
✅ **Re-run with the ENVIRONMENT BLOCK and your headline gets STRONGER:**

```
348 triples across two ENV sweeps
  kernel-EXCLUSIVE  moved in  0 of 348
  OUTWARD           moved in 11 of 348
    p03/p04 safe_tuned both blobs  50.00 -> 43.00
    p08 x6 small +0.0627/+0.0676 ; p08 large unsafe +0.0065
```

⚠ **p08 is a THIRD exposed pattern** (its offset cancels within a language, so
it changes no verdict *today*). **Correct the claim in all three places it
appears** — limit 2, `licence.py`'s docstring, `README.md` — **and adopt the
env knob as the stated method.** ⚠ **Also restate the score as ONE DRAW**:
sweep A `156/10/0/10`, sweep C `152/14/0/10`. *`0 false alarms` survives both* —
say that, it is the part that matters.

**M2 — `UNDEC` conflates three conditions and §2 defines it as one.**
`licence.py::verdict` returns `None` for genuine indirect dispatch, for *"no
kernel symbol"*, **and for NOT BUILT** — and `synthesize.py::main` prints the tag
while dropping the `why`. ⚠ **The failure is live and silent**: `README.md`
documents re-emitting `licence.json` as a one-liner, so running it after
`.temp/build/` is cleaned — **which CLAUDE.md rule 1 tells agents to do** — yields
**88 `UNDEC`s under a legend asserting all 88 dispatch through an unresolvable
pointer**, and nothing fails because nothing is gate-checked. **Separate the
three, surface the `why`, and make NOT-BUILT loud.**

**M3 — `licence.py::is_noreturn`'s `_NORETURN` list contains `copy_from_slice`,
which RETURNS**, under a docstring claiming *"this is an argument, not a
heuristic — all of them are `-> !`"*. **It is the one place the licence can emit
a silent false `LICENSED`.** It fires on 0 of the 31 distinct outward names
today and `len_mismatch` already covers the panic helper, so it is **redundant
and unsound** — one word. Same function, harmless direction: `\babort\b` misses
`_RNvNt…3std7process5abort`, because there is no word boundary after a v0 length
prefix.

**M4 — 2 of the 7 `gcc-clang` `NOT-LIC` verdicts are right for reasons the
measurement contradicts.** p27's `why` names `kernel.cold` — which is
`call abort@plt` (never executes) **and** matches `measure.py`'s own kernel
regex, so it is inside the measured symbol set either way. p47's `why` says
`memcmp` vs `bcmp`; with call counts **both are literally address `0x188320`**,
and the whole difference is the PLT thunk at exactly `2.00`/call. ⚠ **So
*"0 false alarms"* is a statement about the SWEEP, not about the RULE — write it
that way**, and fix both `why` strings to name the mechanism that actually
carries them.

**M5 — p27's mechanism is wrong, and 3 of your 4 "adjacent findings" are already
disclosed.** Measured p27 `small` outward: unsafe `dealloc 917.33`; safe
`dealloc 280.93 + drop_glue 756.73` → **+120.33 is the SAFE side's out-of-line
drop glue**, not the unsafe side's `call *%r12`. ⚠ **`.memory/01-ladder.md`
finding 19 already said so and has been re-confirmed against your claim** —
read it. Disclosure status: **p27 yes with the numbers** (`NOTES.md` §5e's
closed decomposition), **p09 yes with the rule**, **p47 yes**, **p11 yes twice**.
**So three of four are CITATION FIXES, not corrections — no gate re-run, and
the manager has cancelled the four re-runs you implied.** ✅ Only **p27's
`gcc-clang` reversal** (`−25.02 → +15.00`) is new, and it is landed.
⚠ **What IS a real defect and is NOT yours to fix**: `asm.is_bulk_symbol('bcmp')`
is `False`, so p47's record lists `c-gcc:['memcmp@plt']`, `c-clang:[]`,
`safe_naive:[]` for three cells calling **the same entry point**; p09 records all
`[]`; p11's four plain C cells record `[]` while calling `strlen@plt`. **Record
it and the manager will queue it — `harness/asm.py` is out of scope.**

**M6 — §6's provenance is wrong three ways, in the paragraph that predicts
exactly this rot.** (a) It cites RECAP **"Owed" 12** (decayed `check.py:NNNN`
citations); the `--list` census is **"Owed" 6**. (b) It says *"8 of 22"*; RECAP
says *"8 of 20"* — **the denominator was re-based and the numerator was not
recounted.** Measured: **11 files across 10 patterns** (p03 p04 p06 p09 p10 p12
p22 p36 p38 p47). (c) `SEARCH["p47"] = "R4 searched, six levers"` cites
`.tasks/TASK_075.md` — **unreviewed manager prose** — and **six checks out
nowhere**: p47's `NOTES.md` §8e lists **four** searched R4 candidates and its
`--list` shows **five** `from unsafe.rs`.

> ✅ **A DERIVABLE PROXY EXISTS and the review found it: `--list` already prints
> the R3/R4 split** (`from safe_tuned.rs` / `from unsafe.rs`), and p36's gives
> `r3_hdr4 r3_idx r3_iter r3_window` = your hand table's *"4 R3 levers"*
> exactly. **Derive it for the 10 patterns that expose `--list`, print
> `undeclared` for the other 12, and DELETE the hand table** — you predicted it
> would rot and it rotted before the review finished.

## The seven minors

**m1** `licence.py --all` is **43.4 s**, not *"~2 s for the tree"* — 2 s is one
pattern. **The figure is in three files.**
**m2** `README.md`'s *"the probe blobs are `small.bin`"* — every pattern declares
`probe_inputs: [small.bin, large.bin]`, and `.temp/check/p13/` holds **64 small
+ 64 large** `.out`, so route (a′) covers both.
**m3** claim 1's *"`norel` … cannot change how many instructions execute"* is
**over-strong** (`md5_fn_norel` zeroes branch-displacement fields); it is true
**for p36 by direct check** — five branches at identical relative offsets plus
one rip-relative `lea`. **Say the checked version.**
**m4** the six thunk rows carry an unnamed third term — a one-off
lazy-binding/IFUNC resolver (`725–794` Ir/process, **clang and rustc only**)
scaling as `1/n_iters`, `0.0065 … 0.5293` Ir/call. **It is why p11 reads
`299.8727` and not `150 × 2.00 = 300.00`.** Now in `.memory/03-measurement.md`.
**m5** `parse_cg` discards `calls=<n>`, **so the sidecar cannot check its own
per-call attribution** — every exact verification in the review needed it.
**m6** `synthesize.py::main` classifies `norel`/`exact` with `any()`/`next()`
over all O3 identity entries rather than `pair == "unsafe vs verus"`; p01 ships
two.
**m7** §1's `-` for p01's hardened columns and §4's `/x` notation are
undocumented.

## Done when

F1's derived column is primary with its floor stated and the false provenance
sentence gone; six majors and seven minors addressed **or explicitly declined
with a reason**; `synthesis/*.py` re-run and `results/synthesis.md` regenerated;
`measure.py --check-stale` clean and **no record moved** — this task must touch
no measurement. **Paste actual output.** ⚠ **Re-run `licence.py --emit` from a
CLEAN `.temp/build/` at least once** and paste what happens — that is M2's
failure scenario and it should now be loud.

## Constraints

No root; no `/tmp` (scratch `.temp/p76/`; ⚠ **`ls` any scratch path before
writing — `.temp/pNN/` collides between patterns and tasks**; `.temp/p75/` and
`.temp/p75rev/` are readable, **not writable**); **no `git add`/`git commit`**;
do not edit `pilot/`, `.memory/`, `harness/`, `common/`, or any pattern. ⚠ **The
`asm.is_bulk_symbol('bcmp')` defect and the empty `bulk_calls` lists are
`harness/` work — REPORT them, do not fix.** clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; **no self-matching `pgrep` wait-loops.**
**You are the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 180** — 174, plus this review's six: B1's derivability, the inert knob,
`copy_from_slice` in a `-> !` list, *"0 false alarms"* being a property of the
sweep, p27's mechanism plus the already-disclosed status of three findings, and
§6's three provenance errors — **one of which cites the manager's own unreviewed
task prose as authority for a number that checks out nowhere.**

**What I am least sure of, by name: how far F1 should go.** The review
recommends *derived primary, sidecars as refinements*, and I have written that
above — but a two-tier column with a ±2 Ir floor and two refinement paths is
**three ways to compute one number**, and this project's own history says the
thing that rots is the one nobody re-runs. ⚠ **If a single route is defensible —
derived-only, with the sidecars demoted to `.temp/` probes — argue for it.**
**I would rather have one number that is always recomputed than three that
disagree in a year.**

---

## Outcome (recorded by the manager at the task boundary)

**Landed.** `synthesis/` + `results/synthesis.md` only; **44 records, 0 STALE,
no measurement touched, no gate re-run needed** (nothing changed sits in any of
`check.py`'s eleven globs — verified by evaluating them literally). **22
patterns unchanged and green.**

⚠ **The engineer refuted FOUR prescriptions, three of them the REVIEW's, and one
of those had already reached `.memory/` in the manager's hand.**

1. ⚠⚠ ***"Zero misses at every threshold"* was a SCORING ARTEFACT.** The review
   set `truth = |cg| >= th`, i.e. **scored the oracle at the same threshold as
   the estimate**, which makes a miss impossible by construction. Against a fixed
   truth threshold there are **2 misses at 3.0 and at 5.0** — both `p02
   gcc-clang` at exactly `+2.00`, the PLT thunk sitting on the boundary. **The
   manager had already copied the false version into
   `.memory/03-measurement.md`; it is corrected there, together with the ±16
   floor guess (measured max residual 15.79).** ✅ **And the replacement is
   better than either**: three measured bands, of which the top one —
   `|corr| >= 16.00`, 34 rows — is **34 real, 0 spurious**.
2. **M6a is refuted: the delivery's citation was RIGHT.** RECAP "Owed" 12 spans
   `:1808–1863` and the `--list` census at `:1847-1852` is inside it —
   manager-verified. The review swapped it with "Owed" 6.
3. **M6c is refuted**: `patterns/p47-ct-compare/NOTES.md:865` says *"**Six** R4
   levers were built"* and §8e's table has six rows. Only the **citation** was
   wrong — which was the manager's unreviewed task prose.
4. **M6's remedy cannot be executed as written.** Only **5 of 10** `--list`s
   print a source file, and **p36 — the review's own worked example — prints
   none**; name-prefix derivation gives p36 2 R4 levers against finding 23's 3.

**Three manager decisions:**

1. **The engineer's split of the manager's question is ACCEPTED and is better
   than the question.** *"Three routes to one number"* was the wrong frame:
   there is **one magnitude** (now single-route and derived, recomputed every
   run) and **two different questions**. So `outward_ir.json` was demoted to
   publishing **nothing** — it only calibrates, live — while `licence.py` was
   **kept**, because it answers *may this row be differenced* rather than *by how
   much*, has zero run noise, and is the only thing producing the **mechanism**
   (PROTOCOL rule 12). ✅ **Verified self-containment: `synthesize.py` run with
   both sidecars pointed at nonexistent paths still writes every corrected
   figure, including p11's `+9815.56` reversal.**
2. **A published score was allowed to get WORSE, deliberately.** Fixing M4's
   symbol boundary to match `measure.py`'s own needle turns p27's lucky
   `NOT-LIC` into an honest **false `LICENSED`**, moving `156/10/0/10` →
   `154/12/0/10`. **Matching the harness's real boundary beats keeping the
   number**, and the artefact says so out loud.
3. **The `bcmp` alias was NOT whitelisted**, on the engineer's argument that a
   static check cannot know two dynamic names resolve to one address and that an
   alias list is the shape the licence's own docstring exists to reject. p47's
   `gcc-clang` stays `NOT-LIC` **with the mechanism named beside it**.

⚠ **PROTOCOL rule 2's running count is 184:** 180 at TASK_076's writing, **+4**
from this task — the threshold artefact, M6a, M6c, and M6's underivable remedy.
**Carry 184 forward.**

**The single most useful thing in this block.** ⚠ **A scoring artefact travelled
from a review, through the manager's hand, into `.memory/` — the layer this
project calls authoritative — in one commit.** Rule 9 exists to stop unreviewed
*findings* reaching `.memory/`; this one **had** been reviewed, and the review
was the thing that was wrong. **The defence that worked was the next agent
re-deriving the number instead of citing it**, and it is the same defence that
caught `183` forbidden spellings, the spelled-out *"thirteen"*, and *"the six
original axes are complete"*. **A number in `.memory/` is a claim, not a
citation; re-derive before you quote.**
