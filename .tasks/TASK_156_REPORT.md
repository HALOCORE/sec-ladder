# TASK_156 — `p34`'s review corrections landed, and the row FINISHED

**Role: research engineer.** Every number below was produced by a script under
`.temp/t156/` or by the harness, and each claim names the one that produced it.
No `git add`, no `git commit`. `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`,
`pilot/` and every earlier `.temp/t*/` and `.temp/mgr*/` are untouched
(`.temp/t155/` was read and copied from, never modified).

---

## 0. The three things to read first

1. ⚠⚠⚠ **THE DESTROY-PATH PAIR IS MIS-LABELLED IN THREE PLACES, ALL THE
   MANAGER'S, AND I RE-DERIVED IT.** `TASK_156.md` E4, `RECAP.md:12` and
   `harness/tools/composition.py:198` all read *"`+160.64` (`+7.28 %`) at `-O3`
   and `+2403.83` (`+21.6 %`) at `-O0`"*. **Both of those figures are `-O3`.**
   They differ by **INPUT** — `small.bin` and `large.bin` — not by optimisation
   level. The real `-O0` pair is `+164.70` (`+5.24 %`) and `+2953.27`
   (`+18.96 %`), i.e. *smaller* in percentage terms, not larger. ⚠ **The
   reviewer labelled them correctly** (`TASK_155_REPORT` §2 says `small.bin` /
   `large.bin`); the transcription into the manager's artefacts is where it went
   wrong. §3.
2. ⚠⚠ **The corrected mechanism is better than the corrected number.** The
   destroy-side cost is `O(ntop)` **per release**, so it scales with **stack
   depth**, not with `-O0`. `large.bin` pays 15× what `small.bin` pays at the
   *same* optimisation level. §3.
3. ⚠ **Minor 1's premise is also off by a factor of eight.** The task says
   *"Three tracked `controls/*.json` sidecars carry a `measured_utc`"*. Measured:
   **all seven** of `p34`'s do, and **23 of 28** tree-wide. "Three" is the number
   the reviewer happened to re-run and revert. §7.

---

## 1. E0 — `p34` is FINISHED

```
$ python3 synthesis/licence.py --emit synthesis/licence.json
wrote synthesis/licence.json: 31 patterns, 124 pair verdicts (LICENSED, NOT-LIC, UNDEC)     rc=0

$ python3 synthesis/synthesize.py
wrote results/synthesis.md  (83534 bytes, 627 lines)                                        rc=0

$ sed -n 7p results/synthesis.md
Patterns: **31**. Gate records: **31**.

$ grep -c 'p34' results/synthesis.md
14
```

**Before: `Patterns: 30. Gate records: 30.` and `p34` mentioned ZERO times.**
Now 31/31 and 14 mentions. ⚠ **`results/SYNTHESIS.md` (CAPITALS) was NOT
touched** — it is absent from `git status`, and it still does not mention `p34`.
**Reported, not fixed: it is the manager's file and it is one row stale**, as
`TASK_155_REPORT` §11 says.

✅ **PROTOCOL rule 1's REPAIRED anchor check now passes on `p34`**, run verbatim
with the `.temp/` spelling:

```
$ awk '/^## The findings so far/,/^## Retracted/' RECAP.md | grep -E '^[0-9]+\. ' > .temp/t156/h.$$
$ for d in patterns/p*/; do id=$(basename "$d" | cut -d- -f1)
    grep -q "\b$id\b" .temp/t156/h.$$ || echo "MISSING: $id"; done
MISSING: p01
```

Only the known benign exception (the calibration row announces no result), and
`p34` has finding **59**. ⚠ **The check's own known weakness is unchanged**: it
matches a *mention* anywhere in a numbered finding, and `p34` was mentioned in
pre-build catalogue findings for forty tasks. It passes here for the right
reason, but it would have passed for the wrong one.

✅ PROTOCOL rule 10's dangling-report check: only the three `TASK_NNN` placeholders.

---

## 2. E1 — the citations that pointed at nothing (M4)

### The sweep, and it went wider than the three named

`.temp/t156/cite_sweep.py` walks every `.md`/`.py`/`.rs`/`.c`/`.h`/`.inc`/`.json`
under `patterns/p34-refcount-stack/`, extracts every path-shaped token and
resolves it against the repo root, the pattern dir, the citing file's own
directory, `controls/`, `harness/`, `harness/tools/`, `common/`, `synthesis/`
and the pinned vstd:

```
tokens examined: 1224
UNRESOLVED .py/.rs/.inc citations: 8
  NOTES.md:473                  ob_bare.rs          <- bare name, full .temp/ path given in the same sentence
  NOTES.md:486                  probe3_bad.rs       <- same
  spec.md:231                   tuned_splitat.rs    <- same
  spec.md:248                   ob_bare.rs          <- same
  controls/safety_line.py:73    ln.rs               <- `for ln in r.stdout...`, a code fragment
  controls/spellings.py:264     -verus.rs           <- an f-string suffix
  model.py:143                  ../controls/storage_arms.py    ***
  c/kernel.h:112                ../controls/storage_arms.py    ***
```

✅ **Only the two the reviewer named are real**, and the six others are false
positives I checked individually. **The reviewer's third defect is invisible to a
path sweep by construction**, because it is a citation of a *measurement*
(`safe_arms.py` "records the high-water mark"), not of a file — worth saying,
because it means the sweep above is not a general answer to *"are the citations
true?"*.

### What landed

| site | before | after |
|---|---|---|
| `c/kernel.h:112` | `../controls/storage_arms.py measures both sides of it` — **file never existed** | `../controls/safe_arms.py`, naming what branch A and branch B actually measure, plus the withdrawal |
| `model.py:143` | `../controls/storage_arms.py measures that the real allocator agrees` | see below — the claim was **rewritten**, not just re-pointed |
| `controls/arm_safe_arena.rs:34,92` | *"`safe_arms.py` records the high-water mark"* — it recorded nothing of the kind | `safe_arms.py` **now records it**: `arena_high_water` in `safe_arms.json` |

### ⚠ `model.py`'s claim was FALSE in a second way, and I measured it

The docstring said the LIFO recycle *"is the whole of the difference between
p34's checksum-blind shapes and its divergent one"* — a statement about **this
model**. `.temp/t156/recycle_probe.py` turns the recycle off entirely (every
allocation takes a fresh block) and compares every value the model publishes on
all eight shipped inputs:

```
  adversarial-blind.bin        ... IDENTICAL
  adversarial-blindread.bin    ... IDENTICAL
  adversarial-many.bin         ... IDENTICAL
  adversarial-recycle.bin      ... IDENTICAL
  adversarial-stride3.bin      ... IDENTICAL
  degenerate.bin               ... IDENTICAL
  large.bin                    ... IDENTICAL
  small.bin                    ... IDENTICAL

leaf values that MOVED when the LIFO recycle is turned off: 0 of 56
```

**The recycle decides NOTHING `model.py` publishes** — because `Model._window`
keeps only the buggy run's `uaf` FLAG and discards its checksum, and a `DUP`'d
object's *second* release reads `o->rc` out of a freed block whatever the
allocator does with the storage (`.temp/t155/dupproof.py` proves the "whether"
exhaustively). The claim is true **of the C program**, and what actually measures
it is `controls/safe_arms.py` branch B: a LIFO free list reproduces `c/kernel.c`
on `adversarial-recycle`, the input on which the two C rungs diverge. The
docstring now says that, and says what the recycle *does* buy (a faithful
diagnostic in `uaf_sites`).

### The arena high-water mark, now MEASURED

`safe_arms.py` derives an instrumented copy of `arm_safe_arena.rs` — five
substitutions, each asserted to match exactly once, adding a running `hw` and
sweeping **every** window instead of the driver's sampled ones — builds it and
takes the maximum:

```
  adversarial-blind.bin        windows=    1 max slots in use=  1  of ARENA=32
  adversarial-blindread.bin    windows=    1 max slots in use=  1  of ARENA=32
  adversarial-many.bin         windows=    1 max slots in use=  1  of ARENA=32
  adversarial-recycle.bin      windows=    1 max slots in use=  1  of ARENA=32
  adversarial-stride3.bin      windows=    0 max slots in use=  0  of ARENA=32
  degenerate.bin               windows=    1 max slots in use= 16  of ARENA=32
  large.bin                    windows=   64 max slots in use= 16  of ARENA=32
  small.bin                    windows=    8 max slots in use= 11  of ARENA=32
  worst case over every window of every input: 16 of 32 (= CAP), margin 16
```

Reproduces the reviewer's numbers exactly, and it is now in the sidecar rather
than in a report.

---

## 3. E4/M1 — the destroy-path repair, RE-DERIVED, and the labels corrected

### The probe is regenerated, not copied

`.temp/t156/csite/make_destroyfix.py` rebuilds the probe **mechanically from
`c/kernel.c`** — three substitutions, each asserted to occur exactly once, plus
two post-conditions (no retain anywhere in the comment-blanked code; no release
site reads `rc`). Its code is identical to the reviewer's
`.temp/t155/csite/kernel_destroyfix.c` apart from a variable name (`named`
against `still`) and line splitting:

```
$ diff <(comment-blanked t155 probe) <(comment-blanked t156 probe)
63c63,64
<                 size_t j; int still = 0;
---
>                 size_t j;
>                 int named = 0;
...   (variable rename and line splitting only)
```

### It is a real repair

`.temp/t156/csite/destroy_cost.py`, `destroy_cost.json`:

```
input                                            R1                    R1h             destroyfix
adversarial-blind.bin           5576862673510090752    5576862673510090752    5576862673510090752  ==R1h
adversarial-blindread.bin      12442434272084377600   12442434272084377600   12442434272084377600  ==R1h
adversarial-many.bin            5628475829885786112    2893199866468423680    2893199866468423680  ==R1h
adversarial-recycle.bin        16102462438644451328    7544618244297525248    7544618244297525248  ==R1h
adversarial-stride3.bin                           0                      0                      0  ==R1h
degenerate.bin                 12018165609759525888   12018165609759525888   12018165609759525888  ==R1h
large.bin                       7726184805965551230    7726184805965551230    7726184805965551230  ==R1h
small.bin                      13533250923909195085   13533250923909195085   13533250923909195085  ==R1h

ASan, with R1 as the POSITIVE CONTROL that must fire:
  adversarial-blind / -blindread / -many / -recycle   R1 rc=1 hits=1
  the other four inputs                               R1 rc=0 hits=0
  R1h and destroyfix                                  rc=0 hits=0 on 8/8
```

**8/8 checksum-identical to R1h, ASan-clean, and the detector is shown firing on
the same command line.**

### ⚠⚠ And here is the mislabel

```
marginal Ir/call = (Ir@200 - Ir@100)/100, gcc, isolated
  small.bin  O0  R1 3144.48   R1h 3144.48   destroyfix 3309.18
  small.bin  O3  R1 2207.59   R1h 2207.59   destroyfix 2368.23
  large.bin  O0  R1 15579.69  R1h 15579.69  destroyfix 18532.96
  large.bin  O3  R1 11106.93  R1h 11106.93  destroyfix 13510.76

  small.bin/O0/destroyfix-minus-R1     164.70   (+5.24 %)
  small.bin/O3/destroyfix-minus-R1     160.64   (+7.28 %)
  large.bin/O0/destroyfix-minus-R1    2953.27   (+18.96 %)
  large.bin/O3/destroyfix-minus-R1    2403.83   (+21.64 %)
  every R1h-minus-R1 cell                0.00   (+0.00 %)
```

**`+160.64` and `+2403.83` are BOTH `-O3`.** The published pair is
`small`/`large`, and the manager's three artefacts read it as `-O3`/`-O0`.
✅ The reviewer's two figures reproduce **to the decimal**; my `small.bin` R1
*levels* sit `0.54` Ir/call above the reviewer's (`3144.48` against `3143.94`)
because the binaries and probe inputs live at a different path — the known
environment-block level shift — and **every Δ is a within-run difference that
cancels it.** `large.bin`'s levels agree exactly.

⚠ **The mechanism the corrected labelling exposes is the better result.** The
scan is `O(ntop)` on **every release** while the retain runs only on a `DUP`,
which no benign input contains — so the destroy-side price grows with **stack
depth**. `large.bin` (64 windows, deeper stacks) pays 15× `small.bin`'s Δ at the
same `-O3`. That is *why* the acquire is idiomatic, which *"only the acquire can
be repaired"* asserted rather than explained.

### Where it landed in the pattern

`c/kernel.h` (the four-cell table and the mechanism), `spec.md`'s prose **and**
its hashed `why`, `NOTES.md` §1 (pointer) and a new **§4c**, `README.md`'s
distinction block. ⚠ `harness/tools/composition.py` is the **manager's** file and
I did not touch it — **it still carries the `-O3`/`-O0` mislabel and it is the
artefact the synthesis renders.**

### E4/M2 — the absolutist spelling, audited across the whole pattern

The task asked me to check `NOTES.md`. ✅ **`NOTES.md` was clean** — §4b's own
heading is *"predicted from the proof, **then measured**"*. But the grep found
the spelling in **four other files**, three of them measurement-hashed:

| file | the sentence | now |
|---|---|---|
| `c/kernel.h:62` | *"`0.00` BY CONSTRUCTION"*, no hedge | hedged, with the `−14.22` plant named |
| `c/kernel_hardened.c:23` | *"the gradient is `0.00` **because** the added statement is never executed"* — the causal step the plant refutes | withdrawn and replaced |
| `inputs/gen.py:38` | *"`0.00` BY CONSTRUCTION — a statement about the pattern rather than a measurement outcome"* | withdrawn and replaced |
| `README.md:147` | *"nothing can move a statement about a statement that does not run"* — **false** | withdrawn and replaced |
| `controls/no_dup.py` ×3 | the same blur, in the docstring, a problem string and the sidecar `invariant` | rewritten around the census |
| `spec.md` `why` | *"a statement about the pattern rather than a measurement outcome"* | → *"about WHICH STATEMENTS EXECUTE and never about the NUMBER"* |

⚠ **`README.md:147` is the sharpest of the six** and nobody had flagged it: it
asserted the `0.00` figure needs no spelling search *because* a dead statement
cannot move a number. The `dup` plant is a counterexample to exactly that
sentence.

---

## 4. E2 — the hashed `why`'s FALSE sentence, and the negative controls (B1)

### The controls, all three built and run (`controls/safe_arms.py`)

```
BRANCH A -- the `Rc` port: is the SEPARATION available?
  safe_naive.rs            COMPILES -          line    -
  arm_safe_rc_move.rs      REJECTED E0507      line   79   cannot move out of `*t` ...
  arm_safe_rc_borrow.rs    REJECTED E0502      line  100   cannot borrow `objs` as mutable ...

NEGATIVE CONTROLS -- a program that CANNOT have the bug must not print the same error
  arm_safe_rc_move.rs _nodup       COMPILES -        line    -  as expected
  arm_safe_rc_borrow.rs _nodup     REJECTED E0502    line  100  as expected  SAME ERROR AS THE ARM
  arm_safe_rc_borrow_frozen.rs     COMPILES -        stdout='201'
```

* The `_nodup` twins are generated **mechanically from the arm itself** — the
  whole `c % 4 == 1` arm replaced by the `SENT` fold the same file already
  writes when its guard fails. That program publishes no second reference, so it
  **cannot have `p34`'s bug**.
* ✅ **`arm_safe_rc_move.rs` survives and is now ATTRIBUTED**: its twin compiles,
  so the `E0507` is caused by the two edited lines.
* ⚠⚠ **`arm_safe_rc_borrow.rs` is NOT attributable**: its twin fails with the
  **same code at the same line** — the `objs.push` on the **NEW** path.
* ✅ **`controls/arm_safe_rc_borrow_frozen.rs`** (new, committed) takes that
  arm's DUP line character for character over an owner built once and frozen,
  and **compiles and prints `201`**.

### The hashed sentence, and what replaced it

> *"…and a borrow cannot be stored in the stack array because the borrow checker
> ties it to the array it came from."*

**False.** A second `&Obj` *can* be stored in the stack array. ✅ The replacement
is the stronger statement: **the borrow route is closed at the OWNER MUTATION,
not at the duplication — and a `free` IS an owner mutation**, so safe Rust
forbids exactly the destruction that the uncounted alias would make unsound.
`c/kernel.c`'s separation of *publish* from *count* is therefore unavailable
**in a program that also destroys the object**, which is the precise form of the
claim and is now what `spec.md`, `NOTES.md` §8, `README.md` and the two arms'
headers say.

### Why the assertions are RELATIVE, not absolute

⚠ **Two implementation traps, both found by running the thing:**

1. A generated arm must sit **exactly three directories below the repo root** or
   its `#[path = "../../../common/driver.rs"]` does not resolve. The first run
   wrote the twins to `.temp/p34ctl/` and **both twins "failed"** — on a missing
   file, with no error code at all. That would have read as a finding. Fixed
   with a `GEN = .temp/p34ctl/gen` directory and a comment saying why.
2. `arm_safe_rc_borrow.rs`'s `E0502` moved from **line 68 to line 100** because
   I extended its own header comment. So the control asserts **arm line == twin
   line**, never a pinned number, and says so in three places.

`safe_arms.json`'s `problems: []`, and both twin outcomes are asserted in both
directions — a twin that started compiling would falsify the row's published
reading and is reported as a problem.

---

## 5. E3 — `NOTES.md` §6c's cross-row comparison (M5), both sides re-derived

`p35`'s column is read out of **its own committed sidecar**
(`patterns/p35-tagged-union/controls/proof_mutants.json`, which its gate pins
`FRESH`); `p34`'s `Z1` is a **fresh Verus run** built by `.temp/t156/zmut.py`,
which deletes `i < v@.len()` / `i < old(v)@.len()` from `buf_get_unchecked`,
`arr_get_unchecked` and `arr_set_unchecked` and leaves the `#[cfg(slb_twin)]`
twins alone (asserted, not assumed — the twin is `fn slb_twin_<name>`, which the
signature match cannot reach).

```
Z1: p35's ACTUAL X1 arm, transplanted to p34
  Z1  verified=24 errors=0 rc=0 []
M0: the SHIPPED file through the same harness
  M0  verified=24 errors=0 rc=0

p35, out of patterns/p35-tagged-union/controls/proof_mutants.json:
  M0-unmutated                 verified=16 errors=0
  M3-bug-order-both            verified=15 errors=1
  M6-weaken-invariant          verified=15 errors=1
  X1-delete-variant-requires   verified=16 errors=0
```

| what is weakened | `p34` | `p35` |
|---|---|---|
| the loop invariant / the abstract machine | `X1` **22 / 2 — FAILS** | `M6` **15 / 1 — FAILS** |
| a **TRUSTED item's `requires`** | `Z1` **24 / 0 — VERIFIES** | `X1` **16 / 0 — VERIFIES** |

⚠ **The two rows behave the SAME**, and what decides whether a mutation is
caught is **which object it touches**, not which row it is on. The published
sentence claimed a difference that does not exist for the arm it named, and it is
withdrawn in `NOTES.md` §6c, `controls/proof_mutants.py`'s module docstring and
`X1` entry, and `README.md`.

✅ **There IS a real cross-row difference and it is a GATE difference, not a
proof one.** A trusted-`requires` deletion is invisible to both proofs, but on
`p34` stage `5c-twin`'s per-conjunct probe deletes each conjunct from the TWIN
and the twin FAILS — `28 verified, 1 error` for each of the three accessors, read
straight out of `results/gate/p34-refcount-stack.json`'s `verified_twins`. On
`p35` that stage is **BLOCKED for exactly the three items its `X1` mutates**.
`p34` owns five twins and none is blocked.

⚠ **`X2` is loosely mapped too and is now named precisely**: `p32`'s
`M4-spec-weaken` weakens its exec code and its **abstract machine `step`**;
`p34`'s `X2` weakens its exec code and the **loop invariant `wf`**. The
conclusion (`p32` `15/0` verifies, `p34` `22/2` fails) stands; *"X2 is p32's
arm"* is not literally true.

---

## 6. E5 — the contract move, and this time the TEXT is kept

```
as first written (all five `ensures`)   1fa98c8af297710166a2c93731f12b45be7c2c9b4dc39331fcd06203fae8f3dd
as built        (four `ensures`)        f1537d7f601175122e67f9991a107449ad7ca52520b0484f5f014685369d2762
as shipped      (TASK_156)              329c786f99c874b306d2b923815963db9aa49a40f2ffdfda9d7a4b9b098c5b4a
```

✅ **The pre-edit block is kept VERBATIM**, not only its hash:
`.temp/t156/contract_pre_edit.json` (42 327 bytes, re-hashing to `f1537d7f…`),
`.temp/t156/contract_post_edit.json`, generator `.temp/t156/edit_why.py` (five
substitutions, each asserted to match exactly once, JSON re-parsed afterwards)
plus one follow-up substitution that dropped a line number the header edit had
already invalidated.

✅ **And the move is independently reconstructible from `git` alone**
(`.temp/t156/contract_diff_p34.log`):

```
  collapse IDENTICAL · driver IDENTICAL · ensures IDENTICAL · identity IDENTICAL
  idiom ⚠ MOVED
    idiom.forbidden IDENTICAL · idiom.required IDENTICAL · idiom.why ⚠ MOVED
  kernel IDENTICAL · miri IDENTICAL · model IDENTICAL · note IDENTICAL
  requires IDENTICAL · verus IDENTICAL
   2 path(s) moved: ['idiom', 'idiom.why']
```

**Only `idiom.why` moved. No pin, no clause, no `identity`, no obligation count.**

⚠ **The `1fa98c8a… → f1537d7f…` move has NO recoverable text** and `NOTES.md`
§0a now says so plainly rather than letting the table imply otherwise: the
reviewer tried six reconstructions and all six failed, because a hash of a 42 KB
blob is not diffable and the preimage was not kept. The `git show <commit>:`
route only exists for moves made *after* the landing commit, and both pre-landing
states are gone.

---

## 7. Minors and process notes — REPORTED, NOT FIXED

### Minor 1 — `measured_utc`: the premise is wrong, and the field is unread

⚠ **The task says three sidecars carry it. Measured: `p34` has SEVEN of seven,
and the tree has 23 of 28.** "Three" is the number the reviewer re-ran.

```
$ grep -rn 'measured_utc' harness/ synthesis/
(no hits)
```

**Nothing in `harness/` or `synthesis/` reads it.** Stage 9b decides staleness
from `derived_from_sha256`, which answers the *stronger* question ("against
WHAT?") that the timestamp does not. So:

* **What it earns:** the only record of *when* a sidecar's numbers were drawn.
  For a sidecar whose numbers are *measurements* rather than derived facts
  (`spellings.json`'s callgrind rows, `detectors.json`'s sanitizer runs) that is
  a genuinely different fact from the hashes, and `.memory/03-measurement.md`
  entry 21's rule — *a record holds two kinds of leaf and `--check-stale` covers
  only one* — is exactly why it is worth having.
* **What it costs:** re-running any control dirties the tree with a timestamp-only
  diff, and a reviewer cannot tell that from a real one without diffing. Three of
  the reviewer's re-runs did this.
* ✅ **Do not remove it.** The cheap repair, if anyone wants one, is to emit
  **beside** it a `content_sha256` over the document with `measured_utc`
  removed — one field to compare instead of a diff. That is a 23-file change
  across 28 sidecars and I did not make it.

### Minor 2 — `global layout` is a sixth body-less form, and it is FOUR patterns

Confirmed: `harness/vparse.py::axiom_decls` matches `axiom fn`,
`uninterp spec fn`, `assume_specification`, `external_trait_specification` and
`external_type_specification` — and **not** `global layout`. `check.py` never
mentions it.

⚠ **Wider than `p34`:** `grep -l 'global layout' patterns/*/verus.rs` →
**`p28`, `p29`, `p32`, `p34`** — four patterns, not one.

The net is **rustc at codegen**, which the reviewer measured fires even on a
never-constructed type — but **Verus itself reports `1 verified, 0 errors` on a
lie**, so no verify-only stage is protected (`--verify-function` censuses,
`--cfg slb_twin`, the clause-mutation stages). **Defensible on all four** because
each ships a compiled, measured `verus` cell; **not** protected on any stage that
only verifies. A `check.py` change is a 31-pattern re-gate. **Reported, not
fixed.**

### Minor 3 — stage 9b hashes a sidecar and never reads its verdict

`check.py::check_control_json_pins` reads `derived_from_sha256` and
`gate_source_sha256` and nothing else; there is **no** read of `problems` or of
any verdict field anywhere in `harness/` or `synthesis/`.

```
tracked controls/*.json with a `problems` key: 13 of 28
…of which NON-EMPTY (a verdict nothing reads): []
```

**The hole is narrow but real**: run a control, let it record real problems, and
the sidecar is still `FRESH` and the gate still green. It cannot happen through
*staleness* (9b catches that); it happens when the control is re-run and its own
findings are ignored. A one-line `rep.fail` on a non-empty `problems` would close
it and would fire on **zero** sidecars today. **Reported, not fixed** — 31-pattern
re-gate.

---

## 8. The runs — one re-measure, and TWO gates

### ⚠⚠ THE "ONE RE-GATE" BUDGET WAS NOT ACHIEVABLE, AND THE REASON IS STRUCTURAL

**E2 mandates a `why` rewrite, which moves `contract_sha256`, and
`results/tables/*.md` cites the gate record's contract hash.** `report.py` reads
the gate record, so it cannot run before a gate; the gate's stages 9 and 9c then
fail on the stale table; and a green record needs a second gate. `check.py`'s own
failure text says so — *"the same two commands as stage 9: `harness/report.py
p34`, then gate again"* — and `TASK_154_REPORT` §12 records the same thing for
the build. **I ran the mandated edits, then ONE measure, then gate → report.py →
gate.** Reported rather than absorbed, and rather than half-landing E2.

### The re-measure — the prediction was written first and it HIT

Prediction (`.temp/t156/NOTES.md`, before the run): the four measurement-hashed
files I edited (`c/kernel.h`, `c/kernel_hardened.c`, `model.py`,
`inputs/gen.py`) are **comment/docstring-only**, so `96` wall-clock leaves +
`4` source hashes + `generated_utc` + `git.dirty_files` = **102, ± the
`git.commit` leaf**, and **ZERO** `Ir`, static count, md5, checksum or identity.

```
$ python3 .temp/t156/leafdiff.py .temp/t156/p34-measure-BEFORE.json results/p34-refcount-stack.json
leaves: A=1344 B=1344  compared=1344
MOVED: 103
  median_s     32     min_s        32     spread_pct   32
  commit        1     dirty_files   1     generated_utc 1
  gen.py        1     kernel.h      1     kernel_hardened.c 1     model.py  1
```

**103 — the top of the stated range.** Zero `kernel_exclusive_ir` (48 cells),
zero `main_exclusive_ir` (48), zero of the ten static-count families (32 each),
zero of the five md5 families (32 each), zero checksums, zero `input_sha256`.
⚠ **One thing inside the prediction was wrong and the count still hit:** I said
`git.commit` would stay `f67f7d15…`. It moved to `9aa425a3…` — HEAD advanced
between the previous measure and this one (the manager's commits), not during
this task.

### The gates, read out of `results/gate/p34-refcount-stack.json`

**Gate 1** (the FULL run the reviewer never made — first since the build):

```
verdict          FAIL
blocked          []
failures         [tables] x2  -- (a) the table cites contract f1537d7f6011 and spec.md
                                    now hashes to 329c786f99c8
                                (b) 40 line(s) differ from a fresh render
complete_run     True
controls_json    all 7 FRESH
loud             ['collapse-ir', 'tcb-unsafe']   <- the two every pattern in this family carries
```

**Both failures are the table lag and nothing else.** Snapshot at
`.temp/t156/gate1-record.json`.

**`harness/report.py p34`** → `wrote results/tables/p34-refcount-stack.md`,
20 lines changed.

**Gate 2** (full: no `--skip`, no `--no-build`, no `--no-callgrind`, no
`--no-verus-mutants`):

```
verdict          PASS
blocked          []
failures         []
complete_run     True
contract_sha256  329c786f99c874b306d2b923815963db9aa49a40f2ffdfda9d7a4b9b098c5b4a
controls_json    {detectors FRESH, no_dup FRESH, proof_mutants FRESH, rust_bug FRESH,
                  safe_arms FRESH, safety_line FRESH, spellings FRESH}
published_table  FRESH        table_render  FRESH (render == published, 754b22dfef5c)
identity         unsafe vs verus  O0 norel (expected norel)  counts 332/332/1817 both sides
                 unsafe vs verus  O3 norel (expected norel)
miri             required=True ran=True available=True, 8 runs
loud             ['collapse-ir', 'tcb-unsafe']
```

`check.py: PASS`.

### The tree-wide checks (run WITHOUT a pipe, so `rc` is the script's)

```
harness/measure.py --check-stale        rc=0   62 record(s) examined, 0 STALE
harness/tools/composition.py --check    rc=0   OK: published composition table matches
                                               the tree (31 patterns, 10 classes)
harness/tools/temp_citations.py         rc=0   OK (new=0 unclassified=0 resolved=6)
synthesis/licence.py --emit …           rc=0   31 patterns, 124 pair verdicts
synthesis/synthesize.py                 rc=0   83534 bytes, 627 lines
```

⚠ `temp_citations.py`'s six `RESOLVED` entries are the pre-existing `.temp/p34ctl`
baseline rows, not mine; `new=0`, so every `.temp/t156/` path this pattern now
cites resolves on this box. **I did not run `--update`** — pruning the baseline is
a manager decision.

### The controls, all seven regenerated and green — and their diffs are a second negative control

```
safety_line OK · no_dup OK · detectors OK · safe_arms OK · rust_bug OK ·
spellings OK · proof_mutants OK          (.temp/t156/controls.log)
```

⚠ **The sidecar diffs against `HEAD` measure my own comment-only edits:**

| sidecar | lines changed | what moved |
|---|---:|---|
| `spellings.json` | **2** | `gen.py`'s hash + `measured_utc`. **Every Verus and callgrind number in its six-variant table reproduced byte-identically.** |
| `rust_bug.json` | 2 | same shape; Miri rows and checksums identical |
| `safety_line.json` | 3 | two hashes + `measured_utc`; `+1 / −0` reproduced |
| `proof_mutants.json` | 3 | one hash, `measured_utc`, the corrected `X1` `why`. **All six arms reproduced: `24/0`, `23/1`, `21/1`, `22/2`, `22/2`, `23/1`.** |
| `detectors.json` | 4 | hashes + `measured_utc`; all twelve build lines reproduced |
| `no_dup.json` | 5 | hashes, `measured_utc`, the corrected `invariant` string |
| `safe_arms.json` | +89 / −7 | the new `negative_controls` and `arena_high_water` blocks |

---

## 9. What I did NOT do, and what I am unsure about

**Not done, deliberately:**

* **No edit to `harness/tools/composition.py`** — the manager's file, and the
  task scoped me to *"the pattern's own files"*. ⚠⚠ **It still carries the
  `-O3`/`-O0` mislabel of the destroy-path pair (§0.1, §3), and it is the
  artefact `results/synthesis.md` renders.** It is the one correction this task
  found and could not land.
* **No edit to `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `pilot/`** or any
  earlier `.temp/`. `RECAP.md:12` and `TASK_156.md:88` carry the same mislabel.
* **No `check.py` change** for minors 2 and 3 — a 31-pattern re-gate, as
  instructed.
* **No `temp_citations.py --update`.**
* **No `assume(false)` arm** added to the mutation battery (`TASK_155`'s `m4`).
  It was not in this task's E-items and adding one costs another
  `proof_mutants.py` run; the reviewer already measured that `p34` verifies
  `24/0` with it and that the gate's `_assume_keyword_hits` catches it.
* **No re-derivation of the reviewer's clean negatives** (`.temp/t155`'s `hot` /
  `dup` / `dup2` plants, the 33.6 M-stream enumeration, the four-spelling R3
  search, `r4pair`, the detector battery, `identity: norel`). I quote the
  `−14.22` and `34×` figures **from the review**, not from my own run, and every
  place I wrote them says `TASK_155`.

**Unsure, stated so nobody quotes it as settled:**

1. ⚠ **The `+5.24 %` / `+18.96 %` `-O0` destroy-side figures are NEW** — nobody
   has measured them before and nobody has reviewed them. The `-O3` pair
   reproduces the reviewer's to the decimal, which calibrates the run, but the
   `-O0` pair rests on my run alone.
2. ⚠ **My `small.bin` R1 levels are `0.54` Ir/call above `NOTES.md` §5a's**
   (`3144.48` against `3143.94`), and I attribute that to the environment-block
   level shift from a different scratch path. **I did not re-measure it at the
   shipped path to prove the attribution** — `large.bin`'s levels agree exactly,
   which is consistent with it but is not a proof. Every Δ I publish is a
   within-run difference and does not depend on this.
3. ⚠ **The `O(ntop)` mechanism for the destroy-side cost is an ARGUMENT, not a
   fit.** I did not vary stack depth independently of input size; `large.bin`
   differs from `small.bin` in window count *and* depth. The measured fact is
   that the cost is 15× larger on `large` at the same `-O3`; the attribution to
   depth is the obvious reading and is not measured.
4. ⚠ **`arm_safe_rc_borrow_frozen.rs` is a 30-line control, not a rung.** It
   shows *where* the borrow checker objects. It does **not** show that the bug is
   inexpressible via borrows in some third program I did not write; nobody has
   searched that space.
5. ⚠ **`Z1` deletes the `requires` from the three ACCESSORS only.** I did not run
   the analogue for `rec_alloc`/`rec_free`, whose `requires` are richer, so
   *"`p34` verifies on `p35`'s arm"* is a statement about the three accessors.
6. ⚠ **I did not verify that the `-O0` percentages in `spec.md`'s hashed `why`
   will survive a re-run of `destroy_cost.py` on a different day.** They are
   callgrind `Ir`, which is deterministic, so they should; nothing was re-run to
   check.
7. **The `dup2`/`hot` plant figures, the 33.6 M-stream count and the `p35`
   sidecar rows are quoted, not re-run.** `p35`'s rows are read out of a
   gate-pinned sidecar, which is the strongest of those three.

---

**PROTOCOL rule 2 running count: launched from 889, and this task adds THREE
claims contradicted by measurement** — *"`+160.64` at `-O3` and `+2403.83` at
`-O0`"* (both are `-O3`; they differ by input, and the true `-O0` pair is
`+164.70` / `+2953.27`), *"three tracked `controls/*.json` sidecars carry a
`measured_utc`"* (seven of seven in `p34`, 23 of 28 tree-wide), and
*"nothing can move a statement about a statement that does not run"*
(`README.md`'s own sentence, refuted by the `−14.22` plant, and nobody had
flagged it). **Running count: 892.** ⚠ Reconciliation across branches is the
manager's job, not mine.
