# TASK_070_REVIEW_REPORT — p22, hash probe

Reviewer, adversarial. p22 at `b7cd39b`, tree clean. **54 named attacks; 1
blocker, 3 major, 4 minor.** Gate re-run reproduced bit-for-bit and
**`results/gate/p22-hash-probe.json` was restored with `git checkout --`**
(verified byte-identical to a pre-run backup). No file under `patterns/`,
`.memory/`, `harness/`, `common/` or `pilot/` was touched. `.temp/p22/controls/`
was created by running the pattern's own control scripts and has been removed,
restoring `.temp/p22/` to its pre-review state.

---

## A0 — SETTLED. The premise is false, the narrowed claim is real, and the
## false version is pinned into `contract_sha256`

**Measured** (`.temp/p22rev/decr.py`, over all 21 `patterns/*/verus.rs`):

```
exec-loop measures: 73   spec/proof-fn measures: 56
exec-loop measures MENTIONING A GHOST BINDING: 1
```

So the tree contains **72 prior exec-loop termination obligations**, all
discharged. "No R5 here has ever proved termination" is false by a wide margin,
and the manager already knew that. The question was whether the *narrowed* claim
survives. It does, and this is its exact form:

> **Of the 73 exec-loop `decreases` in this tree, p22's probe loop carries the
> only measure that is not arithmetic over the loop's own exec bindings.** Every
> other one is `B − c` for a loop-invariant bound `B` and a monotone exec cursor
> `c`, or a bare monotone-decreasing exec variable. p22's `i0 as int + d - u`
> is built from ghost state (`u`, `d`) plus an existence lemma, and the loop's
> own control variable `i` does not appear in it at all — because `i` wraps.

The candidates that could have shrunk this were checked individually and none
does: p07:356 `hi - lo` (binary search, both cursors move), p06:641/670/695
`decreases b` (two-cursor swap), p16:255 `end - p` (data-dependent step),
p38:442 `2 * n - k`, p14:622 `m + 1 - i`, p13:591 `DST_CAP - d`. All are exec
arithmetic. p09:377 `decreases y` is exec but lives inside a
`#[cfg(slb_twin)]` twin, and is a bare exec variable anyway.

### F1 — `blocker` — "THE FIRST TERMINATION PROOF IN THE PROJECT" ships in five files, one of them the hashed contract

| file:line | text |
|---|---|
| `patterns/p22-hash-probe/verus.rs:5` | "one obligation … that **no other R5 in this tree has**: `decreases` on the probe loop" |
| `patterns/p22-hash-probe/verus.rs:8` | "⚠⚠ **THIS IS THE FIRST TERMINATION PROOF IN THE PROJECT.** Every other R5 here proves that an access is in bounds, that a pointer is live, or that a fold computes the declared function." |
| `patterns/p22-hash-probe/spec.md:192` | "**That is the first termination obligation in this project and it is p22's whole subject**" |
| `patterns/p22-hash-probe/spec.md:532` | "`exact` at O3 is what says **the first termination proof in this tree** cost zero instructions" |
| `patterns/p22-hash-probe/NOTES.md:258` | same sentence |
| `patterns/p22-hash-probe/README.md:47` | table row: "every other pattern | a spatial or temporal obligation ‖ p22 | **a TERMINATION obligation**" |
| `.memory/06-catalogue.md:636` | "the first termination obligation" |

Generator sites: `controls/mkcontract.py:239,306`.

**The two `spec.md` sites are inside `contract_sha256`.** Measured: the
```` ```slb-contract ```` block spans `spec.md:182–548` and its body hashes to
`044f02cded64694e54484df7b69cda3154019e0d350cf049e55dac07199bd5da`, the value in
the gate record. So correcting the sentence **moves the pin and costs a re-gate**
— the manager needs to plan that, and `mkcontract.py` is the file to edit, not
`spec.md`.

**Failure scenario.** PROTOCOL rule 9's exact loop: the manager writes
`.memory/01-ladder.md` from p22's shipped text, and the authoritative layer
acquires a claim that 72 exec-loop measures in the same tree contradict. The
correction above is one sentence and is measured.

`NOTES.md:157–163` already contains the true statement ("Verus requires a
termination measure on every exec loop by default"), one paragraph below the
headline that contradicts it — the same shape as the four prior rule-9 findings.

---

## A1 — SETTLED. The headline is a finding, not a tautology. The *forbid* is
## over-broad and the published R3 span is 16.8× too narrow

The manager's worry was that "nothing on this ladder emits the capacity check"
survives only because `spec.md` forbids its counterexample. **It does not.**
Measured (`.temp/p22rev/spread.py`, -O3 isolated, whole-program marginal,
checksums at `timeout 8`):

| spelling | small | large | `adversarial-full.bin` checksum | other 7 inputs |
|---|---:|---:|---|---|
| `R3ship` | 4401.6100 | 37120.9600 | `8190810770250117165` | — |
| `r3_bounded_kept` | 4569.2600 | 38356.9200 | **`8190810770250117165` (SAME)** | all agree |
| `r3_bounded` | 3960.7700 | 33276.9200 | **`8190810770250110748` (DIFFERS)** | all agree |
| `R4ship` | 4399.6100 | 37118.9600 | `8190810770250117165` | all agree |
| `r4_reslice` | 4276.6100 | 36099.9600 | `8190810770250117165` | all agree |

- **`r3_bounded` — the bound *instead of* the conjunct, i.e. the only spelling
  that could refute the headline — really is a different function**, and it is
  different on exactly the input the pattern is about. The forbid is legitimate
  for it. `R3ship − r3_bounded = +440.84 / +3844.04`, so the manager's third
  refuted prescription ("the careful programmer pays for the bound") is
  reproduced: the bound is **faster**.
- **`r3_bounded_kept` — the bound *plus* the conjunct — is the same function on
  all eight inputs**, and it writes `nfill < TABCAP` by hand too. So it
  *confirms* the headline rather than refuting it.

**Verdict for the manager: the headline is a finding.** It does not rest on the
contract.

### F3 — `major` — the contract's stated reason for the forbid is false of one of the two spellings it forbids

`spec.md:265` (inside `contract_sha256`) and `NOTES.md:95–99` / `README.md:87–92`
justify `forbidden[0]` (`for _ in 0..TABCAP`) and `forbidden[1]` (`(0..TABCAP)`)
on one ground:

> "a bounded trip count also makes the loop terminate, it is idiomatic safe
> Rust, and it is a **DIFFERENT FUNCTION** — it finds a key that is present in a
> full table"

That is true of `r3_bounded` and **false of `r3_bounded_kept`**, which the same
two entries also exclude. The engineer's own generator says so —
`controls/gen_controls.py:142-146` docstring: *"the function is identical to the
shipped R3 on every input"* — and I confirmed it on all eight matrix inputs.

**Failure scenario, quantified.** `NOTES.md:634` publishes *"Span (in contract):
4401.6100 … 4411.6100, width 10.00"*. Admitting the semantically-identical
`r3_bounded_kept` takes that to **4401.6100 … 4569.2600, width 167.65 on small
and 1235.96 on large — 16.8× the published width.** A reader who takes the
published span as the in-contract R3 spread is out by that factor.

**Direction: this does not flatter.** `r3_bounded_kept` is *dearer*, so `R3ship`
remains the cheapest in-contract R3 found and `R3 − R4 = +2.00` is unaffected.
The repair is to the `why` (say the two spellings are excluded for two different
reasons — one semantic, one that the bound is a spelling of the trip count the
pattern exists to leave unbounded), and to the span, which should be published
with the exclusion named.

### Clean negatives on the pattern's spine (all reproduced independently)

`controls/gen_controls.py --run hang --miri`:

```
r2_noguard -O0/-O3  adversarial-full.bin  rc=None  <timeout after 8s>
r3_noguard -O0/-O3  adversarial-full.bin  rc=None  <timeout after 8s>
r4_noguard -O0/-O3  adversarial-full.bin  rc=None  <timeout after 8s>
c_asan (gcc -O1 -fsanitize=address,undefined) adversarial-full.bin rc=None stderr=''
miri r2_noguard adversarial-full.bin  DID NOT TERMINATE in 90s -- no diagnostic, no output
```

Six safe-Rust cells hang at both opt levels; ASan+UBSan stderr **empty**; Miri
**silent**. §0b holds exactly as written. "Memory-safe DoS" is a measurement.

---

## A2 — the R4 disclosure is complete and correct. Clean negative.

`r4_reslice` re-measured and re-verified end to end:

```
r4_reslice through Verus:    verification results:: 20 verified, 0 errors
r4_reslice R4/R5 pair at O3: md5_fn ea06db04c435c4db66a2fb9fca2cdca3 vs
                             ea06db04c435c4db66a2fb9fca2cdca3 -> IDENTICAL; md5_raw equal
r4_reslice checksums:        identical to R4ship on all 8 matrix inputs
R3ship - r4_reslice        = +125.0000 / +1021.0000    (510x the shipped +2.00)
```

- Admissible: in contract, same checksums everywhere, twin verifies, pair
  byte-identical. **Nothing the engineer did not check fails.**
- The disclosure **does reach `README.md`** (`README.md:107–114`), not only
  `NOTES.md` §4d. The `510×` figure and the `1·nkw − 5` law are both in the
  summary.
- **Direction: it flatters safe Rust**, and `NOTES.md:318` says so in its own
  heading. Shipped `R3 − R4 = +2.00` understates the gap against the cheapest
  admissible R4 by 510× on the large band.
- `r4_checked_tab` and `r4_onecmp` re-built: both `md5_fn
  4ac4bd132a501dd2cdd211096c7eda28`, byte-identical to `R4ship`, so §4d's "the
  table check is already dead" and §7's "`arr_get_unchecked` buys NOTHING at
  -O3" are both reproduced.

---

## A3 — the termination argument is REAL. But the mutant battery does not
## isolate it, and a `.memory/`-prescribed probe was not run

### The measure is genuinely checked (reviewer-built mutants, `.temp/p22rev/mut.py`)

| mutant | edit | result |
|---|---|---|
| `ctrl` (relocated, unmutated) | — | `20 verified, 0 errors` |
| `rev_m6_naivemeasure` | `decreases i0 as int + d - u` → `decreases TABCAP - i` | **`error: decreases not satisfied at end of loop` at `:592` — the probe loop** |
| `rev_m9_measure_const` | → `decreases 1int` | **`error: decreases not satisfied at end of loop` at `:592`** |
| `rev_m8_nocursor` | delete `i as int == u % (TABCAP as int)` | 2 × invariant not satisfied |
| `rev_m10_assertfalse_afterlemma` | `assert(false)` after `lemma_exists_empty` | **FAILS** — context is not vacuous |
| `rev_m11_assertfalse_inloop` | `assert(false)` in the probe-loop body | **FAILS** — the loop body is reachable |
| `rev_m12_lemma_selfassume` | delete `count_ne(s, TABCAP) < TABCAP` from the lemma's `requires` | **FAILS** at `:311`, the lemma's own `assert(false)` — the lemma does **not** assume what it proves |
| `rev_m13_hash_live` | `% TABCAP + 1` (m5's live twin) | **FAILS** — so `m5_wronghash`'s `+ 0` is a genuine no-op control, and the site is live |

So: **yes, mutants fail on the MEASURE itself**, at the probe loop, with the
guard intact and everything else unchanged. `lemma_exists_empty` is sound and
load-bearing, its `requires` is satisfiable, the call site is reachable, and
`m5_wronghash` is a real no-op control and not a second live mutant. TCB
recounted from the gate record: **5 items** — `buf_get_unchecked`,
`arr_get_unchecked`, `arr_set_unchecked` (3 U-license), `load_input`, `emit`
(2 infra), 0 V-gap. Matches `NOTES.md` §7. `grep 'assume\|external_body\|
external\b\|assume_specification'` returns exactly those 5 attributes and **no
`assume` anywhere**. The kernel `ensures` is consumed by the driver's ghost
`assert(r == key_fold(...))` at `verus.rs:698`.

### F2 — `major` — `.memory/04-verus.md` §2b's prescribed `--multiple-errors` probe was never run, and it changes two of the four mutant rows

Verus printed the instruction itself, on both runs:

```
note: while loop: not all errors may have been reported; rerun with a higher
value for --multiple-errors to find other potential errors in this function
```

`.memory/04-verus.md` §2b: *"Verus reports the first failure per query, so a
mutant that reports one error may be concealing others — and **if a claim rests
on which obligation failed (p17's whole result does), that ambiguity is
fatal**."* **p22's whole result rests on which obligation failed.** Re-run with
`--multiple-errors 20`:

| mutant | `NOTES.md` §10 says | measured with `--multiple-errors 20` |
|---|---|---|
| `m1_noguard` | 2 errors: lemma precondition + the functional invariant | **3 errors**: `nfill <= TABCAP` (`:516`), the `run` invariant (`:521`), lemma precondition (`:570`) |
| `m3_noempty` | "two *invariant not satisfied* — the witness stops being a witness" | **3 errors, and the FIRST is `decreases not satisfied at end of loop` at `:592`** |
| `m4_nofill` | precondition not satisfied | **1 error only** (`:569`) — clean, as reported |

Two consequences, pulling opposite ways, and both belong in the write-up:

1. **In p22's favour, and `NOTES.md` undersells it.** `m3` — a mutant already in
   the shipped battery — **fails on the `decreases` at the probe loop.** So the
   engineer's own battery already contained a mutant that fails on the measure;
   the single-error default hid it, and §10's "two *invariant not satisfied*" is
   what got recorded. §10's caveat *"`m1` is the one to read carefully … Verus
   reports the first unprovable obligation on the path to it"* is right, but the
   sharper mutant was already there.
2. **Against p22.** `m1`'s third error, `nfill <= TABCAP` at `:516`, is a
   **non-termination** obligation and is not mentioned. I built
   `rev_m14_specmatched` — `m1` plus the same conjunct deleted from the *spec*
   function `run` (`verus.rs:215`), so the functional obligation becomes
   satisfiable — and it still reports **2 errors: `nfill <= TABCAP` (`:516`) and
   the lemma precondition (`:570`)**. So **no shipped mutant shows the capacity
   conjunct is required *only* for termination**; it is independently required
   for an arithmetic invariant. The defensible claim is the narrower one: *the
   `decreases` obligation is real, is checked, and cannot be discharged without
   the conjunct* — not *the conjunct is needed because of termination*.

**Failure scenario.** `NOTES.md` §10's summary sentence — *"Two of the four
failing mutants fail on the termination argument and not on a safety clause"* —
is read as an audit of which obligations fire. Two of its four rows are
incomplete, in opposite directions, and the correction is one flag.

### F8 — `minor` — a loop invariant that is not load-bearing

`rev_m7_nolowerbound`: deleting `u - i0 as int <= d,` (`verus.rs:608`) still
gives **`20 verified, 0 errors`**. It is implied by `i0 as int <= u <= i0 as int
+ d` (`verus.rs:596`), two lines above. Harmless, but `NOTES.md` §0e and
`verus.rs:588–609` present the invariant set as the termination argument, and
one of its clauses does nothing. Gate stage 5c deletes `ensures` conjuncts on
trusted items, not loop invariants, so nothing catches this.

---

## Also in scope

### F4 — `major` — `check_miri`'s block reason is structurally false for every pattern in this tree, not just p22

Confirmed by measurement — the row the gate blocks, run by hand:

```
miri SHIPPED unsafe.rs adversarial-full.bin rc=0 UB=False out='15820751917455319872'
```

`harness/check.py:6086-6090` writes *"so R4 does not return under Miri either"*.
On p22 `c/kernel.c` hangs and `unsafe.rs` returns.

**Scope: it is false for every pattern that could ever declare
`expected_hang`.** `.memory/01-ladder.md`'s rung table puts the bug in **R1
only**, and `miri.sources` names a Rust rung, so on any pattern following the
ladder's own rung definition the Miri source is a rung that carries the fix. The
condition that would make the block correct — the *Rust* rung hanging — is the
one the ladder forbids. `expected_hang` is a per-**input** bool in `model.py`
with no per-rung axis, so `check.py` cannot express the right condition today.
Cost is one unnecessarily blocked Miri row per declared-hang input, and it lands
on `PASS-WITH-BLOCKED-ROWS` rather than `PASS`. The engineer reported this and
did not work around it, correctly; I am confirming it and widening the scope
from "a p22 note" to "a gate defect needing a per-rung axis".

### F5 — `minor` — `_confirm_hang` confirms the O0 cell and never the O3 cell, and the proposed strengthening does not fix that

`harness/check.py:3081` picks `sorted(hung_cells)[0]`; labels are
`f"{c} {o}/{m}"`, so on p22 that is **`c-clang O0/isolated`** — confirmed in my
gate run:

```
ok   adversarial-full.bin: confirmed -- c-clang O0/isolated still had not
     terminated at 20.0s (10x the pinned budget)
```

The cell where the hang is *least* assured is **`c-clang O3`**: `NOTES.md:31-33`
raises exactly this — C11 6.8.5p6 and LLVM `mustprogress` let a compiler assume
a loop with a non-constant controlling expression terminates, which is why §0a
had to measure it. The spot check picks the cell least at risk.

**Is the engineer's proposed strengthening strictly better? No.** Picking one
cell per **distinct rung** gives `c-clang O0/isolated` + `c-gcc O0/isolated` —
**still both O0**. It doubles the cost (40 s) and covers none of the risk. The
axis that matters on this bug class is **opt level**, so the cheap correct
version is one cell per distinct (rung × opt) = 4 cells, 80 s.

**Would either have caught anything here? No.** §0a measured all four
(compiler × opt) hanging, and my gate run re-recorded 8 hung cells across
`c-gcc` and `c-clang` at both levels. Leaving `_confirm_hang` at one cell is a
defensible call; the *reason* given for it should be the one above, not "all 8
hung cells are the same two programs".

### F6 — `minor` — `inputs/gen.py`'s residue-class diagnostic uses the regressor `sweep_ir.py` explicitly warns against

`inputs/gen.py:344` prints `nk%8={(stride - HDR) % 8}` — i.e. `stride - 4`.
`controls/sweep_ir.py:84-89` says: *"⚠ **Not `stride - 4`.** … The first version
of this script used `stride - 4` and reported residuals up to 992 against a law
whose residual is actually 0.00."*

All six band-x blobs share `stride = 304`, so `gen.py` prints `nk%8=4` for the
**whole band**. A reader auditing the residue-class design from the generator's
own output would conclude band x sits at a **single** residue — p38's exact
failure mode — when the true regressor `nkw` spans `{0, 4, 6}`.

**The design is correct; only the diagnostic is wrong.** Verified out of sample
(`sweep_ir.py --band x h`):

```
sweep-h1.bin   nkw  98.24 %8=2   R2-R3 213.48  pred 213.48  resid  0.00  R3-R4 2.00
sweep-h2.bin   nkw 183.04 %8=7   R2-R3 383.08  pred 383.08  resid -0.00  R3-R4 2.00
sweep-h3.bin   nkw 124.00 %8=4   R2-R3 265.00  pred 265.00  resid  0.00  R3-R4 2.00
sweep-x040n06  nkw  40.00 %8=0 … sweep-x150n10 nkw 150.00 %8=6 … all resid 0.00
R3 - R4 over 9 sweep blob(s): distinct values [2.0]
R2 - R3 against `2*nkw + 17`: max |residual| = 0.00 over 9 blob(s)
```

**The residue-class claim is upheld** — off-residue points at `nkw mod 8 ∈
{2, 4, 6, 7}` all predict exactly, and `R3 − R4` is `2.00` flat. First
prospective use of the p38 rule, and it holds.

### F7 — `minor` — NOTES §4e's clang mechanism is a presumption, and the presumption is wrong

`NOTES.md:403` says clang pays 5× *"presumably by restructuring the key loop
around it"*. Derived instead, by disassembly
(`harness/asm.py diff .temp/build/p22/c-clang-O3-isolated
.temp/build/p22/c-clang-h-O3-isolated --sym kernel`):

```
  unhardened (3 insns/key)      hardened (8 insns/key)
  movzbl (%rdi,%rsi,1),%r11d    movzbl (%rdi,%rsi,1),%r10d
  test %r11,%r11                test %r10,%r10
  je   TGT                      setne %r11b        <-- (k != EMPTY) into a byte
                                cmp  $,%rdx        <-- nfill vs TABCAP
                                setb %bl           <-- (nfill < TABCAP) into a byte
                                and  %r11b,%bl
                                cmp  $,%bl
                                jne  TGT
```

**+5 exactly, matching the measured 5.00/key.** The loop is *not* restructured —
clang declines to **short-circuit** the `&&` and materialises both conjuncts into
byte registers. gcc short-circuits with a second conditional branch (`cmp $,%r11;
ja`) and recovers one instruction by re-associating the Horner shift, giving the
measured **+1.00/key**. Static counts corroborate: gcc `n_nopad` 87 → 89, clang
69 → 74. This is still a compiler result and not a language one, exactly as §4e
says; only the mechanism sentence needs replacing.

### `contract_sha256` disclosure — ran it, and it proves less than §11c implies

`git show HEAD:patterns/p22-hash-probe/spec.md | diff - patterns/…/spec.md` →
**identical**. But p22 landed in **one commit** and the tree is clean, so
`git show HEAD:spec.md` *is* the shipped file: the command can only detect an
uncommitted working-tree edit. It does **not** test the `1f29b02e… →
044f02cd…` disclosure, and no artefact behind `1f29b02e…` exists.
`controls/mkcontract.py --check` prints **"spec.md matches the generator"** (and
reads the 11003-char shared paragraph from `patterns/p38-alias-pun/spec.md` at
run time, never embedded), so there is no artefact-vs-generator skew — but the
*content* of the two disclosed prose edits remains unverifiable, which is the
limit PROTOCOL's definition-of-done note already anticipates. §11c should say
that rather than pointing at a command that cannot fire.

### `inputs/gen.py` cannot be fooled — clean negative

Regenerated into `.temp/p22rev/inputs/`: **all 38 blobs byte-identical to the
committed ones**, audit silent. `sim()`'s hang oracle (`gen.py:156-160`) is
sound: guarded and unguarded rungs evolve the *table* identically (neither
inserts once full, because a full table has no EMPTY slot), so `k not in tab`
is the right test at every step and cannot drift. The `sweep-*` blobs are out of
the matrix — the gate record's `inputs_checked` lists exactly the 8 non-sweep
inputs. The `.bin` files are gitignored; only `gen.py` is tracked.

---

## Reproduction and gate

```
gate re-run: PASS-WITH-BLOCKED-ROWS, failures [], complete_run True
             29 of 29 record keys IDENTICAL to the committed record,
             contract_sha256 equal
harness/measure.py --check-stale: 42 record(s) examined, 0 STALE; p22 FRESH
idiom_audit: 39 spellings, 15 forbidden, 116 pairs, forbidden_hits 0,
             required_absent 2 (both the R1/R1h safety-line pair, explained)
```

`results/gate/p22-hash-probe.json` **restored with `git checkout --`** and
byte-compared against a pre-run backup: identical. `git status` clean.

---

## The 54 attacks, with outcomes

**A0 (6).** 1 `decreases` census over 21 files — **LANDED F1**. 2 exec-loop vs
spec/proof split, 73/56 — **LANDED F1**. 3 ghost-mention test on all 73, 1 hit —
narrowed claim **REAL**. 4 propagation grep — **LANDED F1**, 6 shipped sites +
catalogue. 5 is the false claim inside `contract_sha256`? — **yes**, block spans
`spec.md:182–548`. 6 recompute `contract_sha256` — matches `044f02cd…` — clean.

**A1 (8).** 7 `r3_bounded` faster? — reproduced 440.84/3844.04 — clean. 8
`r3_bounded` a different function? — differs on `adversarial-full` only — clean,
**the forbid is legitimate for it**. 9 `r3_bounded_kept` same function? — agrees
on all 8 — **LANDED F3**. 10 its cost direction — +167.65/+1235.96 dearer, span
16.8× — **LANDED F3**. 11 `r{2,3,4}_noguard` hang at O0 and O3 — 6 cells —
clean. 12 ASan+UBSan silence — stderr empty — clean. 13 Miri on `r2_noguard` —
90 s, no diagnostic — clean. 14 noguard checksums on `small`/`nearfull` — agree
— clean.

**A2 (7).** 15 `r4_reslice` checksums, 8 inputs — identical — clean. 16 its
Verus — 20/0 — clean. 17 its R4/R5 byte identity — `ea06db04c435`, `md5_raw`
equal — clean. 18 its Ir delta — +125.00/+1021.00 — clean. 19 disclosure reaches
README? — `README.md:107–114` — clean. 20 direction — flatters safe, stated —
clean. 21 `r4_checked_tab`/`r4_onecmp` vs `R4ship` — all `4ac4bd13` — clean.

**A3 (17).** 22 `rev_m6` naive measure — **fails ON the measure at `:592`** —
**LANDED**. 23 `rev_m9` constant measure — same — clean. 24 `rev_m8` delete the
cursor invariant — 2 failures — clean. 25 `rev_m7` delete `u - i0 <= d` —
**still 20/0** — **LANDED F8**. 26 `rev_m10` `assert(false)` after the lemma —
fails — clean. 27 `rev_m11` `assert(false)` in the loop — fails — clean. 28
`rev_m12` delete the lemma's hypothesis — fails at `:311` — **lemma is sound** —
clean. 29 `rev_m13` `+1` vs m5's `+0` — fails — **m5 is a genuine no-op** —
clean. 30 `m1` with `--multiple-errors 20` — 3 errors not 2 — **LANDED F2**. 31
`m3` likewise — first error is `decreases` — **LANDED F2**. 32 `m4` likewise — 1
error — clean. 33 `rev_m14` spec-matched no-guard — isolates a non-termination
failure — **LANDED F2**. 34 TCB recount — 5 items, 3/0/2 — clean. 35
`assume`/`external` grep — 5 attrs, no `assume` — clean. 36 is the kernel
`ensures` consumed? — `verus.rs:698` — clean. 37 R4/R5 exec-code diff — ghost
and formatting only — clean. 38 relocated unmutated control — 20/0 — clean.

**Harness and also-in-scope (16).** 39 Miri on shipped `unsafe.rs` on the
blocked input — `rc=0 UB=False` — **LANDED F4**. 40 scope of the `check_miri`
defect — structural, every pattern — **LANDED F4**. 41 `_confirm_hang` cell
selection — `c-clang O0/isolated` — **LANDED F5**. 42 would per-distinct-rung
have caught anything? — **no** — clean. 43 residue class out of sample, bands
x+h — resid 0.00 on 9/9 — clean. 44 `R3 − R4` on the 9 sweep blobs — one
distinct value `2.0` — clean. 45 `gen.py` regeneration — 38/38 byte-identical —
clean. 46 `gen.py` residue diagnostic — **LANDED F6**. 47 `sim()`'s hang oracle
faithfulness — sound — clean. 48 `sweep-*` excluded from the matrix — 8 inputs —
clean. 49 clang 5.00/key mechanism — derived — **LANDED F7**. 50 gcc 1.00/key
mechanism — derived — supports F7. 51 `git show HEAD:spec.md` — identical but
**vacuous on a one-commit pattern** — reported. 52 `mkcontract.py --check` — no
generator skew — clean. 53 gate re-run — 29/29 keys identical — clean. 54
`measure.py --check-stale` — 42 records, 0 STALE — clean.

---

## Summary of findings

| # | rank | where | what |
|---|---|---|---|
| F1 | **blocker** | `verus.rs:5,8`; `spec.md:192,532`; `NOTES.md:258`; `README.md:47`; `mkcontract.py:239,306`; `.memory/06-catalogue.md:636` | "the first termination proof in the project" is false — 72 prior exec-loop measures. Two sites are inside `contract_sha256`, so the fix moves the pin. The narrowed claim (first measure not expressible in exec variables, 1 of 73) is measured and true. |
| F2 | major | `NOTES.md:720,722` (§10) | `--multiple-errors 20` was never run, on the one pattern whose result is a claim about which obligation fires. `m3` actually fails on the `decreases` (undersold); `m1` has a third, non-termination error (overclaimed). |
| F3 | major | `spec.md:265`; `NOTES.md:95–99`; `README.md:87–92` | the forbid's stated reason ("a DIFFERENT FUNCTION") is false of `r3_bounded_kept`, which agrees with R3ship on all 8 inputs; the published in-contract R3 span is 16.8× too narrow. |
| F4 | major | `harness/check.py:6086-6090` | the Miri block's reason is false on p22 and structurally false for every pattern in this tree; `expected_hang` needs a per-rung axis. |
| F5 | minor | `harness/check.py:3081` | `_confirm_hang` confirms `c-clang O0`, never O3 — the cell least at risk; per-distinct-**rung** would not fix it, per (rung × opt) would. |
| F6 | minor | `inputs/gen.py:344` | the residue diagnostic uses `stride - 4`, the regressor `sweep_ir.py:84` warns against; it prints one residue for the whole off-residue band. |
| F7 | minor | `NOTES.md:403` | clang's 5.00/key is `setne`/`setb`/`and` — a refusal to short-circuit — not "restructuring the key loop". Derived. |
| F8 | minor | `verus.rs:608` | the invariant `u - i0 as int <= d` is not load-bearing; deleting it still gives 20/0. |
