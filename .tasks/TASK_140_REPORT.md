# TASK_140 — review of `p29`. It is NOT gate-green today, the headline FALLS on a measurement, and so does the `.memory/04-verus.md` update the build asked for.

> ## ⚠⚠⚠ BLOCKER, READ THIS FIRST: `p29` IS NOT REPRODUCIBLY GATE-GREEN, AND THE DEFECT IS VISIBLE IN `HEAD` WITHOUT RUNNING ANYTHING
>
> `harness/check.py p29`, run today: **`check.py: FAIL`, 1 failure, `[tables]`.**
>
> **This is not a flake and I did not cause it.** It is decidable from commit
> `d41ba6c` alone, with no build and no gate run:
>
> ```
> git show HEAD:results/gate/p29-bst-delete.json  ->  controls_json: all four FRESH
>                                                     verdict: PASS, failures: []
>                                                     table_render: render == published
> git show HEAD:results/tables/p29-bst-delete.md  ->  FOUR lines saying those same
>                                                     four sidecars are `STALE`
> harness/report.py p29 --stdout                  ->  ZERO `STALE` lines
> ```
>
> The published table is **one gate-run behind**. `TASK_139`'s `gate3` PASS is a
> **one-run-behind artefact**: stage 9c compares the published table against a
> render taken from the **PREVIOUS** run's record — `gate2`'s, in which the four
> sidecars really were `STALE` — so table and render agreed, the stage went
> green, and the same run then wrote `FRESH` into the record. Every subsequent
> run renders `FRESH` and fails on those four lines. **The gate's own failure
> message says this**, and names the precedent: *"`p23` published a sentence
> that had become false in exactly that gap (TASK_121)."*
>
> **The false sentence here is load-bearing.** It sits under a heading that reads
> *"These did not fail the gate and are **not defects**"*, and it says of all
> four control sidecars: *"`STALE`: … nothing can date its numbers against the
> sources in the tree. **Treat every figure quoted from it as undated.**"* Those
> four sidecars are where **every number this row publishes** lives —
> `arms.json`, `miri_arms.json`, `proof_mutants.json`, `repro.json`.
>
> **Fix — the two commands the gate itself prints:** `harness/report.py p29`,
> then `harness/check.py p29`. Nothing about the kernel, the model, the proof,
> the sanitizers, Miri or the identity pin is implicated.
>
> ⚠ **`results/gate/p29-bst-delete.json` is now dirty in the working tree** —
> my run overwrote it with the FAIL record. I did not restore it, because the
> FAIL is the true current state and the fix regenerates the file anyway. `git
> diff` it if you want the delta; `git checkout` it if you want HEAD's PASS
> back, but the next gate run will fail again until `report.py` is re-run.
>
> ⚠⚠ **Consequences for the record.** `RECAP` 52, the `p29` catalogue cell and
> this task's own *"already manager-verified — do not re-derive"* all rest on a
> `PASS` that does not reproduce. `failures: []` and `blocked: []` were read out
> of a record that was correct **about `blocked`** — `blocked` is still `[]` on
> my run — and stale about the table.
>
> ✅ **Blast radius: ONE ROW.** I rendered all 27 patterns with
> `harness/report.py <id> --stdout` (writes nothing) and diffed each against its
> published table: **26 are byte-identical; `p29` differs by exactly those four
> lines.** So the repair is one row plus a note about `check.py`'s stage 9c,
> not a tree-wide re-render.

**Role: research reviewer.** No file under `patterns/`, `.memory/`, `RECAP.md`,
`results/SYNTHESIS.md` or `results/tables/` was written. Nothing was planted
into `patterns/p29-bst-delete/` — every arm is built from a **copy** by textual
substitution, so no restore was needed. No `git add` / `git commit`. Scratch is
`.temp/t140/`. **`git status` shows exactly two entries:** `.tasks/TASK_140_REPORT.md`
(new) and `M results/gate/p29-bst-delete.json`, which `harness/check.py p29`
rewrote as a side effect of the run the task file authorises — see the blocker
box.

---

## VERDICT IN ONE SCREEN

| item | verdict |
|---|---|
| **1 — the headline, a COUNTING claim** | ⚠⚠⚠ **FALLS.** `p29`'s read path CAN be spelled with **ONE** conjunct, and I measured **two** such spellings: `wrong 0/500`, `ASan lines 0`, agreeing with the shipped R1h **on all eight committed inputs**, on `controls/arms.py`'s own corpus and seed. One of them (`livetag`) **adds no state at all** — it widens `live[]` from a bit to the occupant tag, which is what `p27`'s own `c/kernel.c` calls *"[a] generation counter with slot reuse removed"*. **The R1↔R1h diff stays ONE LINE, ONE CONJUNCT.** ⚠ The row is **not** thereby a duplicate — see below — but *"`p27` needs one, `p29` needs two"* is false as written, and it is in **ten committed files** (`RECAP.md` ×5, `spec.md` ×5 incl. the hashed `why`, `NOTES.md` ×5, `c/kernel.h` ×3, `06-catalogue.md`, `SYNTHESIS.md`, `results/tables/p29-*.md`, `README.md`, `c/kernel.c`, `c/kernel_hardened.c` ×2 each). |
| **2 — safe rungs CORRECT by design** | **SURVIVES, NARROWED.** The call is right and its best reasons were not given. ⚠ But the four-mechanism table's **safe-Rust row is the one row with NO control anywhere in the tree** — the engineer fixed exactly this hole for the Miri row and left it open for the safe-Rust row. **Cheap fix, no rung change, no re-gate of the rungs:** a `controls/safe_arms.py` in `miri_arms.py`'s shape. |
| **3 — the instrument claim** | **SURVIVES, NARROWED, and one clause is FALSE.** ✅ The limit is real and structural: `miri.sources == ["unsafe.rs"]` on **27 of 27**, **202 of 202** Miri rows across all gate records read `ub: false`. ⚠ It is narrower than written — the gate **can** substantiate *"Miri is silent on the correct rung"* (`p38` and p29's own `miri.reason` use it) and IS the declared backstop for a mutation planted in `unsafe.rs` (`p02`/`p16`/`p17`). ⚠⚠ **FALSE: *"no other pattern in the tree has one"*.** `p42/controls/miri_seeds.sh`, `p42/controls/miri_leak_key.py`, `p18/controls/miri_exit_hole.py` and `p22/controls/gen_controls.py --miri` are dedicated Miri arms, and **`miri_seeds.sh` already states this exact hole in writing**. |
| **4 — vacuity beyond `M6`** | **SURVIVES.** I planted `assert(false)` at **seven** sites the battery does not cover. **All seven are LIVE** (`24 verified, 1 errors`, `assertion failed`), including the arm the second conjunct exists for and the two-child splice. ⚠ Note the gate already ships one such probe (`clause_deletion` → `main`, `assert(false) probe`). |
| **5 — `identity: differ`** | **SURVIVES, and I chased it to its last instruction** — the thing §8 disclosed as not done. `asm.py diff` at `-O0`: **7 hunks, +42 instructions, −0**. R5 is a strict **superset** of R4: 21 dead `mov (%rsp),%r / mov %r,(%rsp)` pairs round-tripping the 4-byte `Rec` through vstd's wrappers. `899 − 857 = 42` exactly. At `-O3`, `normalised text identical`. **Legitimate, not a defect.** |
| **6 — `model.py` independence** | ⚠⚠ **FALLS AS STATED, and the file itself is honest while the report, `RECAP` 52 and the catalogue cell are not.** `model.py` has **two** implementations. Implementation 1 is the functional tree the claim describes. **Implementation 2 — `_run_spec`, which is what `bst_fold` and therefore the derived `ensures` are evaluated against — carries ALL TWELVE of `kernel.c`'s control variables**: `cur dup goleft guard lv ntab par root sgoleft sp sst steps` (AST census, `.temp/t140/probes/model_census.py`). ✅ The design is still sound — impl 2 is cross-checked against impl 1 by `selfcheck()` on every gate run — but the published sentence is false of the half that matters most. |
| **7 — no cost axis** | ⚠⚠ **PARTLY DISHONEST, and the missing number is the row's own subject.** The count-the-levers reason is good for an R3-side safety claim and **is not a reason at all for `R1 vs R1h`**, which `.memory/01-ladder.md` defines as *"what the check costs, inside one language"*, in one file, on the one line `spec.md` pins. It is measured and sitting in the gate record: **gcc `−17.53` / `+7.65`, clang `−27.17` / `−89.14` Ir/call** at `-O3 isolated`. **p29's two-conjunct safety line costs nothing measurable, and that is a result, not an absence.** |
| **DELIVERABLE 4 item 1 — *"a `struct` inside `verus!` is its own obligation"*** | ⚠⚠⚠ **FALSE. DO NOT LAND IT.** A bare `struct` carries **ZERO**. Adding one to a copy of p29's own `verus.rs` gives **25**, not 26; adding three gives **25**. The obligation is carried by **`#[derive(Clone)]`** — measured five ways. ⚠ The engineer's probe `.temp/t139/verus/probe_ob.rs` adds `Rec2` **with `#[derive(Clone, Copy)]`**, which the report and the **hashed** `obligations_note` both describe as *"one further **bare** `#[repr(C)] struct Rec2 { a: u8 }`"*. ✅ **Cross-checked against the tree: `p36`'s shipped census counts `pub struct OpTag<const K: u8>` as ZERO and sums exactly to its pinned 12** — consistent with the corrected rule, inconsistent with the proposed one. ⚠ And *"p29 is the first pattern to declare a struct inside `verus!`"* is false: `p36/verus.rs:163`. |
| **Is `p29` FINISHED?** | ⚠⚠⚠ **NO, TWICE OVER.** *(a)* **It is not gate-green** — see the blocker box; the published table is one gate-run stale and carries four false sentences about its own evidence. *(b)* **Its numbers are not findable**: `results/synthesis.md`, the file `SYNTHESIS.md` sends you to for *"the numbers"*, still reads **`Patterns: 26. Gate records: 26`** and contains **zero** occurrences of `p29`. ✅ `measure.py --check-stale` is `0 STALE`, 54 records; `composition.py --check` is `OK … 27 patterns`. Both defects are one command each. |
| **Gate, re-run** | ⚠ **`check.py: FAIL`, 1 failure, `[tables]`; `blocked: []` as expected.** See §9. |
| **Running count** | base **679**, branch delta **+8**, **= 687**. |

---

## 1 — ITEM 1: THE HEADLINE FALLS. ONE CONJUNCT IS ENOUGH, AND I BUILT IT TWICE.

The claim under attack, in `RECAP` 52, `.memory/06-catalogue.md`'s p29 cell,
`spec.md` (twice — the prose and the **hashed** `why`), `c/kernel.h`,
`c/kernel_hardened.c`, `README.md` and `results/SYNTHESIS.md` §7:

> **`p27`'s read-path safety line needs ONE conjunct (LIVENESS); `p29`'s needs
> TWO (LIVENESS *and* OCCUPANT IDENTITY).**

`.temp/t140/probes/onecon.py` builds two single-conjunct arms out of the
**shipped** `c/kernel.c` by substitution (the file is opened read-only), and
scores them exactly the way `controls/arms.py` scores its own arms — same
generator, same `fuzz_ops`, same seed `20260830`, same 500 windows, same
`env -u LD_PRELOAD`, ASan counted with `count('AddressSanitizer')` and never
with `head`.

```
livetag   `live[]` stops being a BIT and becomes the occupant tag: 0 = dead,
          key+1 = live and holding `key`.  NO NEW ARRAY, NO NEW VARIABLE.
          Walks read `live[cur] != 0`; the insert writes `live[ntab] = a+1`;
          the two-child splice retags the slot it overwrites.
          USE:  if (g_saved != NULL && live[g_slot] == (uint16_t)(g_key + 1))

gentag    a separate `gen[]` counter, bumped at the free AND at the payload
          copy; FIND saves `g_gen`.
          USE:  if (g_saved != NULL && gen[g_slot] == g_gen)
```

**Result** (`.temp/t140/onecon.json`, `.temp/t140/logs/onecon.log`):

```
window classes: UAF 104   RECYCLE 18   benign 378     <- arms.json's split, exactly

arm        wrong  on 104 UAF  on 18 RECYCLE  ASan lines  class
R1           122     104/104      18/18         208      heap-use-after-free
R1h (2 conj)   0       0/104       0/18           0      --
livetag        0       0/104       0/18           0      --      <- ONE conjunct
gentag         0       0/104       0/18           0      --      <- ONE conjunct
compiler warnings under -Wall -Wextra: none
ASan positive control: rc=1 hits=2 heap-use-after-free
```

`R1`'s row reproduces `controls/arms.json` **digit for digit** (122 / 104 / 18 /
208), so this is the same corpus the row's own numbers come from.

**And on the pattern's own eight committed inputs** — `livetag` and `gentag`
agree with `R1h` on every one, including `adversarial-recycle.bin` at
`6826524771972934656`, which is `model.py`'s value in the gate's stage-4 table:

```
input                     R1                    R1h / livetag / gentag
adversarial-many.bin      5459764144629796864   12727551634606393344
adversarial-recycle.bin   10466247628510718976   6826524771972934656
adversarial-succ.bin     15920169411516035072   3300925633855656960
adversarial-uaf.bin       8775379295093329920  17864705736200262656
degenerate / large / small / stride3        all four agree with R1h
```

**The `livetag` R1 ↔ R1h diff is one line and one conjunct**, verified by
`difflib`: 2 changed lines, of which one is the `if`. And the `livetag` R1
rung still has **both** bug classes — ASan `heap-use-after-free` on
`adversarial-uaf.bin`, silent-and-wrong `10466247628510718976` on
`adversarial-recycle.bin`, which is the same wrong value all eight of the
shipped buggy C cells print.

### 1a — the engineer's rejection reasoning, tested

> *"A record with the links in slot arrays would … make the two-child splice a
> choice rather than a consequence of the algorithm, which is why it was
> rejected."*

The **conclusion** is right; the **reason** is a non-sequitur, and `c/kernel.c`
states it as a causal fact:

> *"The links are inside the record because that is what makes the two-child
> delete copy the payload rather than move a pointer."*

That is false. CLRS's `TREE-DELETE` **transplants the successor node** into the
victim's position; it does not copy the payload, and it does that with links
inside the node, which is exactly p29's layout. Hibbard's copy-the-payload
variant and the transplant variant are both textbook, both available at p29's
layout, and the row **chooses** the one that recycles an occupant. That is a
legitimate benchmark choice and it is disclosed in `NOTES.md` §8 — but it is a
choice, and the shipped comment says it is a consequence.

(The conclusion holds: under transplant, a record's occupant never changes, so
the check collapses to `live[g_slot] == 1` and the row *would* be `p27`. So the
rejection was correct. It is the stated reason that is wrong.)

### 1b — what survives, and what the row should say instead

**The row is NOT a duplicate of `p27`.** What survives my attack, untouched:

- **the mechanism claim**, which is the row's real content: one omitted line,
  two bug classes selected by the victim's degree, and the second class is
  invisible to *every allocation-shaped* instrument — ASan (gate stage 7),
  Miri (`controls/miri_arms.json`), the `Option` discriminant, and a linear
  `PointsTo` (`M3b`). `p27` has one bug class. That is a different row.
- **the currencies result** (`NOTES.md` §2b): 208 ASan lines / 7-of-104 wrong
  against 0 ASan lines / 18-of-18 wrong. Both single-conjunct spellings inherit
  it — dropping the single conjunct produces *both* harms at once, which is if
  anything a sharper statement.
- **limb 1 of the reviewed bar** — *a new operator on the safety line*. An
  **occupant-identity** test is new whether it is spelled as a second conjunct
  or fused into a tag; no other pattern's safety line asks it.

**What falls, and what has to fall with it:**

1. the *"ONE vs TWO"* counting sentence, in all six places;
2. **`NOTES.md` §6c / `spec.md` / the catalogue cell's *"AT R5 THE `&&` ORDERING
   IS FORCED"*** — with one conjunct there is no ordering. The `M2b`
   measurement (`precondition not satisfied` at `tracked_borrow`) is real and
   reproduces; what it shows is narrower: *given the two-conjunct spelling*,
   the order is forced. It is not a fact about the pattern.

### 1c — the one thing that does prefer the shipped spelling, and it was never weighed

`base`'s tie between exec and ghost state is
`forall j. st.lv[j] <==> live[j] == 1u8`. Under `livetag` that becomes
`st.lv[j] <==> live[j] != 0` **plus a new conjunct** `st.lv[j] ==> live[j] ==
st.ky[j] + 1`, which the insert and **the two-child splice** must re-establish —
the splice being the operation that changes `st.ky`. Under `gentag` you need a
ghost monotonicity invariant plus the value recorded at FIND.

So the honest comparison is: **the shipped two-conjunct spelling buys a free
`wf` at the price of a second conjunct.** That is precisely the trade the
engineer argues for `tab[]` in §2.2 — *"not nulling is what makes the cache
invariant free"* — applied to `live[]`, and it was not made because the tag
spelling was never considered. ⚠ **Argued, not measured:** building a `livetag`
R5 means rewriting `base`, `run`, `step` and nine `assert forall` blocks in a
1486-line file, which is past a review's budget. I flag it as an argument, in
the same words the report uses for its own `H2` R5 argument.

---

## 2 — ITEM 2: THE SAFE-RUNG CALL IS RIGHT. THE HOLE IT LEAVES IS A MISSING CONTROL, NOT A MISSING RUNG.

**The gate would have passed the broken rung.** `inputs/gen.py`'s benign
invariant guarantees no benign window USEs a stale record, so a safe rung
missing `rec.key == g_key` agrees with `model.py` on `small`, `large`,
`degenerate` and `stride3`, and diverges only on the adversarial rows —
which `check.py` stage 4 **records** and does not require to agree
(`check.py:3341`, `[adversarial: recorded, not required to agree]`). So this was
a free choice, not a constraint.

**Two reasons for the engineer's call that the report does not give, and they
are stronger than the one it does:**

1. `.memory/01-ladder.md` puts the modelled bug in **R1 only**; `check.py`'s own
   Miri comment relies on it by name (*"every Rust rung carries the fix"*). A
   silently-wrong R2/R3 would be the tree's first, and `check_miri`'s reasoning
   is written against its negation.
2. **You cannot argue §4d and then break it.** §4d justifies eleven
   never-firing terms by *"they are in EVERY rung, so no rung-to-rung comparison
   is confounded by them"*. A safe rung missing a twelfth term is a **different
   program**, and every `R3 − R4` and `R2 − R1h` number in the published table
   would be a comparison of two different kernels.

**Against, and it is real:** `.memory/02-bench-rules.md`'s nine-candidate table
still reads **`p29 ADMITTED limb 4 clause 3, the safe rung is SILENTLY WRONG`**.
The shipped artefact does not exhibit that, and the catalogue cell now says the
row *"SHIPS ON LIMB 1, NOT LIMB 4"*. **Two committed documents disagree about
why the row exists.** That is a `.memory/` update owed and it is not on the
engineer's list of five.

**The concrete hole.** `NOTES.md` §2a's four-mechanism table has four rows.
Three are substantiated in the tree — ASan by gate stage 7, Verus by
`proof_mutants.py` `M3b`, Miri by the new `controls/miri_arms.py`. **The
safe-Rust row is substantiated by nothing in `patterns/p29-bst-delete/`.** Its
evidence is in `.temp/t136/` and `.temp/t137/`, which are **gitignored**. This
is the identical defect the engineer found and fixed for the Miri row, one row
over.

> **RECOMMENDATION (cheap, and it does not touch a rung):** ship
> `controls/safe_arms.py` in `miri_arms.py`'s exact shape — `safe_naive.rs`
> with `&& tab[g_slot].as_ref().unwrap().key == g_key` deleted, scored against
> `model.py` on the adversarial inputs, with the shipped file as the
> must-be-correct control. That restores the limb-4 evidence to the tree and
> costs one control, not a re-gate of the rungs.

⚠ **The `p32`/`p33` comparison in the task file is about a different arm.** The
`Vec<Node>` + freelist spelling is bit-identical to buggy C on **both** halves.
The wrong-by-one-conjunct arm is correct on the UAF half (`0/71`) and wrong on
the recycle half only. They are not the same risk, and the engineer's §7 bullet
keeps them apart correctly.

---

## 3 — ITEM 3: THE INSTRUMENT LIMIT IS REAL, AND ONE SENTENCE OF IT IS FALSE

**Verified structurally, not on p29 alone.** `spec.md`'s `miri.sources` is
`["unsafe.rs"]` on **27 of 27** patterns; `check.py` fails closed on anything
`RUST_SRC` does not map. Across all 27 gate records: **202 Miri rows, 202 with
`source == "unsafe.rs"`, 202 with `ub: false`.** So the engineer's *"all eight
rows read `no UB`"* generalises to the whole tree, and the observation belongs
in `.memory/03-measurement.md`.

**Three narrowings before it is written down:**

1. **The gate CAN substantiate a *"does not see"* row** — when the operation in
   question is one the *correct* rung performs. `p38`'s `spec.md` leans on
   exactly that (*"On p38 Miri is expected to be, and is, entirely silent about
   the pattern's bug"*), and so does p29's own `miri.reason`. Legitimate.
2. **The gate's Miri stage is not inert.** `p02/NOTES.md:841`,
   `p16/NOTES.md:825` and `p17/NOTES.md:992` all name step 8 as the declared
   backstop against *a second unchecked read added to `unsafe.rs`* — a mutation
   of the rung the gate does run. `p02` even records the diagnostic it produces
   (`Undefined Behavior: 'assume' called with 'false'`, on 1 of 9 inputs).
3. ⚠⚠ **The novelty clause is FALSE.** *"no other pattern in the tree has one"*
   (TASK_139 §6.4) and *"`p29` ships … the tree's only dedicated arm"*
   (`RECAP` 52). Committed counter-examples:
   - `patterns/p42-goto-cleanup/controls/miri_seeds.sh` — its own header:
     *"Two things this answers that the gate's own Miri stage does not"*, with
     the positive control being *"the shipped `unsafe.rs` with the ERROR PATH's
     `dig_free` deleted, generated here by substitution so it cannot drift"* —
     **`miri_arms.py`'s design, already shipped**. It even states the hole:
     *"`spec.md`'s `miri.sources` is `["unsafe.rs"]`, so R5 is never
     Miri-checked directly."*
   - `patterns/p42-goto-cleanup/controls/miri_leak_key.py`
   - `patterns/p18-varint-shift/controls/miri_exit_hole.py` — the shape p42's
     script says it copied
   - `patterns/p22-hash-probe/controls/gen_controls.py --miri`

✅ **The p29 arm itself is sound.** I read `controls/miri_arms.json`: `r1line`
UB on `adversarial-uaf` and `adversarial-succ`, silent on
`adversarial-recycle` printing `2751827421526092736` against the correct
`2755550117516839872`, shipped `unsafe.rs` clean on all four. Positive and
negative controls both present and both behave.

⚠ **Nit in `miri_arms.py`:** `fix = lambda t: t.replace('#[path = "../../common/driver.rs"]', '#[path = "../../common/driver.rs"]')`
is an identity replacement under a comment saying *"the variant lives one
directory deeper than `unsafe.rs`"*. It does not — `.temp/p29miri/` and
`patterns/p29-bst-delete/` are the same depth, which is why it works. Harmless
today; it breaks silently if `WDIR` ever moves.

---

## 4 — ITEM 4: VACUITY. SEVEN NEW SITES, ALL LIVE.

`.temp/t140/probes/vacuity.py` plants `assert(false)` at seven sites in a copy
of `verus.rs`. `verified, 0 errors` would mean the site is dead and everything
downstream of it vacuous.

```
V1-kernel-top          24/1  live   is the exec path reachable under the `requires`?
V2-use-identity-HIT    24/1  live   the arm that folds a record value
V3-use-identity-MISS   24/1  live   <- THE ARM THE SECOND CONJUNCT EXISTS FOR
V4-use-guard-MISS      24/1  live   the arm where liveness is false (the UAF half)
V5-splice-copy         24/1  live   <- the two-child payload copy, the recycle class
V6-free-arm            24/1  live   the 0-or-1-child arm, the only one that frees
V7-main-callsite       24/1  live   is main's call to kernel reachable?
```

All seven fail with `assertion failed`. No dead code, no vacuous branch, and in
particular **the two branches the row's two bug classes live in are both
reachable in the proof** — which is what makes `M3b`'s refinement failure mean
something.

⚠ **The gate already ships one of these**, which neither the report nor
`NOTES.md` mentions: `results/gate/p29-bst-delete.json`'s `clause_deletion`
carries `{"item": "main", "kind": "assert(false) probe", "verified": 24,
"errors": 1}`. My V7 is that probe; V1–V6 are new.

**The other two classes named in the task:**

- *a `requires` nothing can discharge* — `proof_domain` in the gate record
  reports `requires_ok: true` with `ensures_checked: 128` on every non-empty
  input, i.e. the precondition is evaluated against `model.py`'s real bindings
  and holds. Combined with V1 (the body under the `requires` is reachable) and
  V7 (the call site is reachable), the class is closed.
- *a postcondition true of the wrong program* — `M5` (fold multiplier) and `M6`
  (constant body) both fail, and `requires_strength` in the gate record judges
  every trusted clause `not a tautology`. Closed.

---

## 5 — ITEM 5: `differ` IS LEGITIMATE, AND I CHASED IT TO ITS LAST INSTRUCTION

§8 discloses *"the `-O0` `differ` was not chased to its last instruction"*.
It is 42 instructions and they are all the same instruction.

```
harness/asm.py diff  unsafe-O0-isolated  verus-O0-isolated
  7 hunks   +42 lines   -0 lines
  +18x  mov (%rsp),%ecx / mov %ecx,(%rsp)
  + 3x  mov (%rsp),%edx / mov %edx,(%rsp)
```

**R5 is a strict superset of R4**: nothing is removed, 21 dead
reload-then-store pairs of the 4-byte `Rec` are added at seven sites, and
`899 − 857 = 42` exactly. They are `-O0` copy-elision absence inside vstd's
`ptr_ref` / `ptr_mut_write` wrappers. At `-O3` every one is gone —
`identical with pc-rel fields masked: True`, *"normalised text identical"*,
counts `596/587` on both sides.

**So `differ` here is not codegen divergence, not proof cost and not a defect
being pinned; it is a strict-superset relation of no-ops at the one
optimisation level `.memory/02-bench-rules.md` forbids performance claims at.**
That is a stronger statement than the report's *"three spellings built and none
is 900"*, and it should replace it.

✅ **The `870 / 886 / 900` figures reproduce**, and so do all four `md5_raw`
digests and `md5_raw_norel 9f816ce2…` on both `-O3` sides. ⚠ **One presentation
nit:** `NOTES.md` §5 quotes `n_raw` alone (870 / 900 / 611), which includes
trailing padding; `asm.py`'s own docstring says *"Report `n_raw` and `n_nopad`
together"* because padding *"overstates the … gap"*. Here it **under**states it:
`n_nopad` is `857` vs `899`, so the real gap is 42 and the published one is 30.
The gate record carries `n_nopad` (`counts_a`/`counts_b`), so a reader who
cross-checks §5 against `results/gate/p29-bst-delete.json` finds four numbers
that do not match and no note saying why. §5 also has **no entry in `NOTES.md`
§10's reproduce list**.

✅ **`p27`'s fix genuinely does not transfer, and it was genuinely applied.**
`unsafe.rs::rec_open` already writes `*q = v` (not `core::ptr::write`), with
p27's reason in the comment, and it still differs. The claim stands.

---

## 6 — ITEM 6: `model.py`'s INDEPENDENCE — TRUE OF ONE HALF, FALSE OF THE HALF THE `ensures` USES

The published sentence (TASK_139, `RECAP` 52, and the catalogue cell, in
almost identical words):

> *a purely functional BST, recursive three-case delete, tree shape held
> OUTSIDE the record, and a REACHABILITY WALK as the read test: **no cursor, no
> `par`, no `goleft`, no guard, no liveness array**.*

`model.py` contains **two** implementations and says so at line 304:

> *"the second, independent implementation … **This is what the derived
> `ensures` is evaluated against**, so it must not be the simulation in
> disguise. It mirrors the *Verus* spec function (`../verus.rs` `run`) and keeps
> the tree in five parallel slot sequences with liveness beside the payload."*

**AST census of the two, mechanical and not by reading the docstring**
(`.temp/t140/probes/model_census.py`; the 12 names are every local in
`c/kernel.c`'s three walks and its deletion loop):

```
Model._window     1/12   ['root']
                  impl 1 -- the functional tree, drives stage-2 checksums
Model._run_spec  12/12   ['cur','dup','goleft','guard','lv','ntab','par',
                          'root','sgoleft','sp','sst','steps']
                  impl 2 -- `bst_fold`, drives the DERIVED `ensures`
```

**All twelve.** `while cur != NIL and lv[cur] == 1 and steps < TABCAP` appears
three times in `_run_spec`, character-for-character the shape of `kernel.c`'s
walks, and the deletion carries `guard`, `sp`, `s`, `sgoleft`, `sst`.

**This is not a defect in the artefact.** Impl 2 has to mirror `verus.rs`'s
`run` — that is what makes the `ensures` evaluable in Python — and `selfcheck()`
cross-checks it against impl 1 on 8 sampled calls on every gate run, which is
`p23`'s hazard properly mitigated. **What is wrong is the published sentence**,
which describes half the file as if it were the whole, in the one deliverable
`TASK_137` called *"the review's sharpest instruction"*. The manager should
restate it as: *implementation 1 is written from the contract and has none of
those; implementation 2 mirrors `verus.rs`'s `run` and has all of them; the gate
runs both against each other.*

---

## 7 — ITEM 7: A COST CLAIM IS AVAILABLE, AND IT IS THE ROW'S OWN SUBJECT

The published table and the gate record already carry the numbers. From
`results/gate/p29-bst-delete.json`'s `marginal_ir_per_call`, `-O3 isolated`:

```
                        small.bin    large.bin
c-gcc                     3641.00     17411.70
c-gcc-h                   3623.47     17419.35      R1h - R1  =  -17.53 /   +7.65
c-clang                   3697.09     18056.83
c-clang-h                 3669.92     17967.69      R1h - R1  =  -27.17 /  -89.14
safe_naive                4049.40     20285.61      R2  - R4  = +220.35 / +1190.87
safe_tuned                4022.58     20187.25      R3  - R4  = +193.53 / +1092.51
unsafe                    3829.05     19094.74      R4  - R1h = +205.58 / +1675.39
verus                     3829.05     19094.72      R5  - R4  =   +0.00 /    -0.02
```

**The count-the-levers reason is good for the R3 side and does not apply to the
C side at all.** `.memory/01-ladder.md` defines R1-vs-R1h as *"what the check
costs, **inside one language**"*; `.memory/02-bench-rules.md` says the cell
exists so that *"'C is faster' and 'C is unsafe' stop being confounded"*, and
publishes p02's `+5 (gcc) / +12 (clang)` for exactly this. There is no spelling
search to do: the two files are character-identical apart from one line, and
that line is pinned in `spec.md`'s `required[0]`.

> **p29's two-conjunct safety line measures free-to-negative — `−17.53` to
> `+7.65` Ir/call on gcc, `−27.17` to `−89.14` on clang.** On a row whose whole
> subject is that safety line, *that is the number a reader comes for*, and the
> row does not print it.

⚠ **The sign needs a sentence, not suppression.** All benign windows pass the
check, so R1h does strictly more work and should be dearer; it is not, and at
0.5% of 3641 the effect is register allocation, not arithmetic. Publishing it
with that caveat is the honest move; publishing nothing lets the reader assume
a cost that is not there.

⚠ **And the standard is being applied unevenly.** `RECAP` 47 publishes p27's
`R3 − R4 = +109.98 / +661.82` as *"THE TEMPORAL SAFETY TAX IS REAL AND LARGE"*
with no lever search on either side. p29's is **larger** (`+193.53 / +1092.51`)
and is withheld on a rule p27's number does not satisfy either. Pick one.

✅ **The absence is correctly flagged in three places** (`NOTES.md` §8, `RECAP`
52, the catalogue cell) with *"do not read the absence as a zero"*. That part is
right and should stay.

---

## 8 — DELIVERABLE 4: THE FIVE `.memory/` UPDATES, PLUS TWO THE LIST MISSES

| # | update | endorse? |
|---|---|---|
| **1** | `.memory/04-verus.md` — *"a `struct` inside `verus!` is its own obligation"* | ⚠⚠⚠ **REJECT. IT IS FALSE.** Replace with the measured rule below. |
| **2** | `.memory/02-bench-rules.md` `identity` section — the `differ` debt is discharged | ✅ **ENDORSE**, and strengthen: the `-O0` divergence is `R5 ⊃ R4` by 42 no-ops at 7 sites (§5), which is more than *"one real run"* owed. Also correct: p27's `*base = v` fix is record-shape-specific and **was applied** here and still differs. |
| **3** | `.memory/02-bench-rules.md` composition — p29 is TEMPORAL, total 27 | ✅ **ALREADY DONE.** `composition.py --check` prints `OK: … 27 patterns, 10 classes`. |
| **4** | `.memory/03-measurement.md` — the gate's Miri stage runs the correct rung | ✅ **ENDORSE THE LIMIT, REWRITE THE SCOPE.** Land the structural facts (`miri.sources == ["unsafe.rs"]` 27/27; 202/202 rows `ub: false`); land the three narrowings in §3; and **strike *"no other pattern has one"*** — p18, p22 and p42 do, and p42's `miri_seeds.sh` already states the hole. |
| **5** | `RECAP` 51 / the p29 catalogue cell — settled, built, Miri row measured | ✅ **ENDORSE**, with the corrections in §10. |
| **6** | ⚠ **NOT ON THE LIST:** `.memory/02-bench-rules.md`'s nine-candidate table still reads `p29 ADMITTED limb 4 clause 3, the safe rung is SILENTLY WRONG` | **OWED.** The shipped safe rungs are correct and the row ships on limb 1. Two committed documents disagree about why the row exists (§2). |
| **7** | ⚠ **NOT ON THE LIST:** `results/synthesis.md` is one pattern stale | **OWED.** See §11. |
| **8** | ⚠⚠ **NOT ON THE LIST:** `check.py`'s stage 9c compares the published table against a render built from the **previous** run's record, so a run that changes `controls_json` / `loud` / `idiom_audit` passes itself and poisons the next run | **OWED, in `.memory/03-measurement.md` beside the Miri entry.** The stage's own message documents the ordering; what is not written down anywhere is that **a green stage 9c is not evidence the published table matches the record that run wrote.** `p29` is the first row to exhibit it and, as of today, the only one. |

### 8a — the obligation rule, measured five ways

Every run is `./verus_run.py <file>`, single-file mode, never `--cargo`.
Sources are kept in `.temp/t140/verus/`.

```
MINIMAL FILES  (baseline `fn main(){}` alone = 1 verified)

  ob_empty            fn main only                                  1     +0
  ob_struct           + bare #[repr(C)] struct                      1     +0  <-- STRUCT IS FREE
  ob_struct2          + 4 type decls (repr(C), plain, generic, enum) 1    +0
  ob_layout           + struct + `global layout Rec is size == 4`   1     +0  <-- LAYOUT IS FREE
  ob_const            + one `const`                                 2     +1  (the known rule)
  ob_derive           + struct with #[derive(Clone, Copy)]          2     +1  <-- THE OBLIGATION
  ob_d_Clone          + #[derive(Clone)]                            2     +1
  ob_d_Debug          + #[derive(Debug)]                            1     +0
  ob_d_PartialEq      + #[derive(PartialEq)]                        1     +0
  ob_derive2          derived struct + a SECOND bare struct         2     +0  <-- bare adds nothing
  ob_dl2              derived struct + global layout + bare struct  2     +0

ON p29's OWN verus.rs

  p29_base            shipped                                      25
  p29_plus1           + BARE `#[repr(C)] struct Rec2 { a: u8 }`     25     +0   <-- NOT 26
  p29_plus3           + THREE more bare type decls                  25     +0
  p29_plus1_derive    + `Rec2` WITH #[derive(Clone, Copy)]          26     +1
  .temp/t139/verus/probe_ob.rs   the engineer's own probe           26
```

**`diff patterns/p29-bst-delete/verus.rs .temp/t139/verus/probe_ob.rs` shows the
added struct carries `#[derive(Clone, Copy)]`.** The report and the hashed
`obligations_note` both call it *"one further **bare** `#[repr(C)] struct Rec2
{ a: u8 }`"*. The arithmetic is correct — the probe really does print 26 — and
the reading is wrong. That is `.memory/03-measurement.md` entry 12's class
exactly, one task after that entry was written.

> **THE CORRECTED RULE, for `.memory/04-verus.md`:** a `struct`, `enum` or
> `global layout` inside `verus!` carries **zero** obligations. **A derived
> `Clone` impl carries one** — the derived `clone` body is its own query — so
> `#[derive(Clone, Copy)]` costs 1 and `#[derive(Debug)]` / `#[derive(PartialEq)]`
> cost 0. p29's 25th term is the **derive on `Rec`**, not `Rec`.

**Independent confirmation from the shipped tree.** `p36-vtable-dispatch`
declares `pub struct OpTag<const K: u8>;` inside `verus!` (line 163) and its
`obligations_note` sums to its pinned 12 **without counting it**:
`NOPS 1 + SENT 1 + TABLE 1 + OpTag::apply 1 + run 1 + kernel 2 + main 5`. Under
the proposed rule p36 would owe 13 and its own census would be wrong. Under the
corrected rule both patterns are consistent.

⚠ **Two consequences for the manager.**
1. `spec.md`'s `obligations_note` is **inside the hashed `slb-contract` fence**,
   so the correction moves `contract_sha256` and needs a re-gate. `NOTES.md`
   §6a and `TASK_139_REPORT` §6.1 need the same edit.
2. *"p29 is the first pattern in the tree to declare a struct inside `verus!`"*
   (`NOTES.md` §6a) is **false**; `p36` is.

---

## 9 — THE GATE, RE-RUN: `FAIL`

`harness/check.py p29`, log `.temp/t140/logs/gate-t140.log`. Read out of
`results/gate/p29-bst-delete.json`, **never grepped**:

```
verdict   FAIL                      <- HEAD's committed record says PASS
failures  1  [tables]  "results/tables/p29-bst-delete.md is STALE IN ITS
             CONTENT: 4 line(s) differ from what `harness/report.py p29`
             renders from this tree"
blocked   []          <- p29 = 0, as the task file expects; p01 = 1, p42 = 1
verus     verus.rs 25 verified / 0 errors, pinned 25, tcb_items 7
tcb names buf_get_unchecked load_input emit arr_get_unchecked
          arr_set_unchecked rec_alloc rec_free      <- identical to p27's seven
identity  O0 differ (expected differ)  O3 norel (expected norel)
contract  f77972d2d5da…  matching spec.md
controls  arms FRESH  miri_arms FRESH  proof_mutants FRESH  repro FRESH
miri      8 rows, all source=unsafe.rs, all ub=false
```

**Everything else in the gate is green.** The kernel, the model, the proof, the
checksums, the sanitizers, Miri, the driver loop, the identity pin, the
obligation count, the twin, the clause-deletion battery, the tautology probe,
`requires_strength` and `proof_domain` all pass. The one failure is the
published table, and the mechanism is in the blocker box.

**Reproduced from `HEAD` with no gate run at all**, so it cannot be attributed
to my session:

```
git show HEAD:results/gate/p29-bst-delete.json  ->  controls_json all FRESH
git show HEAD:results/tables/p29-bst-delete.md  ->  4 lines: those 4 are STALE
harness/report.py p29 --stdout                  ->  0 STALE lines
```

(The record's `diagnostic` strings, `miri.runs[].seconds`, adversarial group
order and the *"N distinct behaviours"* note are not byte-reproducible and
nothing here is attributed to them. This failure is none of those: it is a
content diff against a deterministic render.)

**Other checks re-run, read out of their own output:**

```
harness/tools/composition.py --check   OK: … matches the tree (27 patterns, 10 classes)
harness/measure.py --check-stale       54 record(s) examined, 0 STALE
./verus_run.py verus.rs                25 verified, 0 errors
```

---

## 10 — DELIVERABLE 3: WHAT `RECAP` 52 AND THE CATALOGUE CELL OVERSTATE

The manager wrote both from the engineer's report plus its own re-runs, and
re-running a script checks the arithmetic, not the reading.

| # | as written | what I measured |
|---|---|---|
| **1** | *"`p27`'s read-path safety line needs ONE conjunct; `p29`'s needs TWO … the two temporal rows are therefore NOT the same shape, which is what makes the second one a row rather than a duplicate."* | ⚠⚠⚠ **The first clause is false (§1). The second clause survives, on a different ground** — the rows differ in *bug classes*, not in *conjunct count*. Also in `spec.md` ×2 (one hashed), `c/kernel.h`, `c/kernel_hardened.c`, `README.md`, `SYNTHESIS.md` §7. |
| **2** | *"`model.py` WAS WRITTEN FROM THE CONTRACT — … no cursor, no `par`, no `goleft`, no guard, no liveness array. ⚠ This was the review's sharpest instruction and it was followed."* | ⚠⚠ **True of impl 1, false of impl 2 — the one the `ensures` is evaluated against, which has all twelve (§6).** `model.py` itself says so at line 304; the summary drops the qualifier. |
| **3** | *"`p29` ships `controls/miri_arms.py`, the tree's only dedicated arm"* | ⚠⚠ **FALSE.** p42 ×2, p18, p22 (§3). |
| **4** | *"C's `&&` short-circuit ordering, recovered as a TYPE-SYSTEM FACT"* | **Narrows with §1.** The `M2b` measurement is real; it is a fact about the two-conjunct spelling, not about the pattern. |
| **5** | *"THE ATTACK ARM IS NOW THE STRONGEST IN THE TREE"* | **Soft but defensible** — 10 named mutants is the largest count I can find (p01/p02 are 8). ⚠ Count is the wrong axis: p42 ships `ledger_leak.py` as *acceptance* arms against a proof that verified `18/0` while leaking. Prefer *"the largest mutation battery in the tree"* to *"the strongest attack arm"*. |
| **6** | *"TCB is 7 — the same seven `p27` ships"* | ✅ **VERIFIED**, name for name, out of both gate records. |
| **7** | *"`p27`'s one-line `-O0` fix provably does not transfer"* | ✅ **VERIFIED and now explained** (§5): the fix is applied in the shipped `rec_open`, and the residual is 42 vstd wrapper no-ops. |
| **8** | *"adding `tab[cur] = NULL` moves the control's sanitizer class from `heap-use-after-free` to `SEGV`"* | ✅ Consistent with `controls/arms.json`. ⚠ Read it precisely: **one arm of six moves** (`keyonly`), and the shipped `R1h` and `H2` do not move at all. `RECAP` 52's *"the control's"* reads as though there were one control. |
| **9** | *"NO COST AXIS IS PUBLISHED … deliberate"* | ⚠ **Half right (§7).** Deliberate and defensible on the R3 side; the R1h−R1 number needs no lever search, is defined by `.memory/01-ladder.md`, and is the row's own subject. |
| **10** | ⚠ `.memory/06-catalogue.md`'s p29 row still names the pattern *"binary search tree insert/lookup"* with mechanism *"recursive ownership"* | **Stale.** The shipped row is delete-with-a-cached-lookup over a slot table of raw pointers. Cosmetic, but it is the row a reader greps for. |
| **11** | ⚠ `RECAP` 47's *"`identity` is PINNED `exact` at `-O3` … in 26 of 26"* | **Now 25 of 27** (`p36` and `p29` are `norel`). The paragraph's conclusion still holds — at `-O3` p29's counts are equal, `596/587` both sides — but the count is stale, and so is `results/synthesis.md`'s Claim 1 (*"`exact` … on 25 patterns and `norel` for 1 (p36)"*). |
| **12** | ⚠⚠⚠ *"`check.py: PASS` — `failures: []`, `blocked: []`, read out of `results/gate/p29-bst-delete.json` and not grepped"*, in `RECAP` 52, the catalogue cell, `README`-adjacent prose and this task file's *"already manager-verified"* | ⚠⚠⚠ **The `PASS` does not reproduce.** `blocked: []` does. **The manager read the right key out of the right file and the file was one gate-run stale** — which is a sharper instance of `.memory/03-measurement.md` entry 12 than the struct one: here even *re-reading the record* could not see it, because the record is the thing that moved. Only re-**running** the gate, or diffing the published table against `report.py --stdout`, exposes it. |

---

## 11 — IS `p29` FINISHED? NO, TWICE OVER.

*Gate-green is not finished; a pattern is finished when a reader can find its
result.* **`p29` fails both halves of that sentence today.**

**(a) It is not gate-green.** See the blocker box and §9. One command
(`harness/report.py p29`) plus a re-gate.

**(b) A reader cannot find its result where the project tells them to look.**

- ✅ `results/gate/p29-bst-delete.json`, `results/p29-bst-delete.json`,
  `results/tables/p29-bst-delete.md` all present; `measure --check-stale` is
  `0 STALE` over 54 records; `composition.py --check` is `OK`, 27 patterns.
- ✅ `RECAP` 52, the catalogue cell and `SYNTHESIS.md` §7 all name the row.
- ⚠⚠ **`results/synthesis.md` — the file `SYNTHESIS.md` sends the reader to for
  *"the numbers"* — still says `Patterns: **26**. Gate records: **26**` and
  contains ZERO occurrences of `p29`.** Its Claim 1 still reads *"`exact` … on
  25 patterns and `norel` for 1 (p36)"*, which p29 makes wrong. It is generated
  from committed records by `synthesis/synthesize.py` and builds nothing, so the
  fix is one re-run.

**So a reader who follows this project's own signposting from `SYNTHESIS.md`
to the numbers finds 26 patterns and no p29** — and if they instead open
`results/tables/p29-bst-delete.md`, the first thing it tells them about the
row's four evidence files is *"treat every figure quoted from it as undated"*,
which is false. Both are one command each.

⚠ Minor, for the same reader: `README.md`'s *"who sees it"* column prints
**`nothing`** for the recycle class. `RECAP` 49/51's sharpest sentence is the
opposite — *"the half nothing sees is the half that REPRODUCES"* — and the
gate's own stage 4 sees it (all eight buggy C cells print one wrong value). The
column means *"of the four allocation-shaped mechanisms"*; say so, or the row
loses its best inversion.

---

## 12 — CLEAN NEGATIVES: attacks that did NOT land. Do not re-run these.

1. **"The `-O3` `norel` hides a real codegen difference."** No.
   `asm.py diff` prints *"normalised text identical"*, `md5_raw_norel
   9f816ce2e5ce…` on both sides, and `counts` `596/587/2785` identical.
2. **"`M6` is the only vacuity arm and the R5 has a dead branch."** No — seven
   further `assert(false)` sites, all live (§4), including both bug classes'
   own branches.
3. **"The `keyonly` arm's ASan lines are an artefact of the corpus."** No —
   reproduced independently at 208 on the same 500 windows, with the positive
   control firing (`rc=1 hits=2 heap-use-after-free`).
4. **"TCB 7 is not the same seven as `p27`."** It is, name for name.
5. **"`model.py` impl 2 is uncross-checked."** It is not — `selfcheck()`
   compares it against impl 1 on 8 sampled calls and `check.py:2387` runs it.
6. **"`gen.py`'s benign invariant is circular because it cannot import
   `model.py`."** Disclosed by the engineer and true of `p27` too; but impl 2 of
   `model.py` is a *third* implementation of the same semantics and the gate
   runs all three against each other, so the circle is not closed.
7. **"`adversarial-recycle.bin`'s wrong value is compiler-specific."** No — my
   `livetag` R1 (a different source, different `live[]` width, different walk
   spelling) prints the same `10466247628510718976`.
8. **"The `differ` pin lets a proof cost hide at `-O0`."** It could in
   principle; here it does not — the 42 added instructions are dead stack
   round-trips inside vstd's wrappers, not proof residue, and they are absent at
   `-O3`.

---

## 13 — WHAT I DID NOT DO, AND WHAT I AM UNSURE OF

- **No `livetag` R5 was built.** §1c's proof-cost argument is an ARGUMENT, in
  the same sense the report's `H2` R5 argument is. It would take rewriting
  `base`, `run`, `step` and nine `assert forall` blocks.
- **No safe-Rust arm was built.** §2's recommendation is a design
  recommendation; I did not measure the wrong-by-one-conjunct safe rung myself
  and am relying on `TASK_137` §4a's numbers for it.
- **The `livetag`/`gentag` arms were scored on `arms.py`'s corpus and the eight
  committed inputs, not on a fresh independent corpus.** That is deliberate —
  matching the corpus is what makes the comparison against `arms.json` exact —
  but it means the two spellings have been tested on 500 windows, not 1500.
- **I did not measure whether `livetag` changes the published `Ir`.** It widens
  `live[]` from 32 B to 64 B and turns a byte compare into a halfword compare;
  the effect is probably small and is unmeasured.
- **The item-5 attribution is by disassembly diff, not by source mapping.** I
  showed the 42 instructions are dead stack round-trips of a 4-byte value at
  seven sites; I did not prove which vstd item emits each one.
- **`.temp/t139/` was read and never written.** I ran the engineer's
  `probe_ob.rs` in place through `verus_run.py`, which does not modify it.
- **I did not re-render `results/tables/p29-bst-delete.md`** or re-run
  `synthesis/synthesize.py`; §11 and the blocker box are observations about the
  committed files, not changes to them. Every `report.py` call I made used
  `--stdout`; `git status results/tables/` is clean.
- ⚠ **`results/gate/p29-bst-delete.json` IS dirty** — running `check.py p29`
  overwrote it with the FAIL record. That is the one tracked file this review
  changed, it changed as a side effect of a run the task file authorised, and I
  left it rather than restoring HEAD's `PASS`, because the `PASS` is the thing
  that does not reproduce. `harness/report.py p29 && harness/check.py p29`
  regenerates it green.
- **I did not re-gate after the render sweep.** The 27-pattern render diff
  (`.temp/t140/render/`) is a static comparison; I did not run `check.py` on any
  pattern but `p29`.

---

## 14 — PROTOCOL rule 2 running count. Base **679** (as given). Branch delta **+8**:

0. **`p29` is not reproducibly gate-green, and `check.py`'s stage 9c has a
   one-run-behind hole that manufactured its `PASS`.** The stage compares the
   published table against a render taken from the *previous* run's record, so a
   run that changes `controls_json`, `loud` or `idiom_audit` **passes itself and
   poisons the next run**. `TASK_139`'s `gate3` is the instance: it went green
   against `gate2`'s `STALE` record and wrote `FRESH`, leaving four false
   sentences in the published table under a heading that calls them *"not
   defects"*. ⚠ **The hole is a `check.py` property, not a p29 property**, but
   I swept the tree and **only `p29` is currently in the bad state**: I rendered
   all 27 patterns with `harness/report.py <id> --stdout` into `.temp/t140/render/`
   and diffed each against its published table — **26 are byte-identical, `p29`
   differs by exactly those four lines.** So this is one row to fix and one
   `check.py` weakness to record, not a tree-wide repair.
1. **A `struct` inside `verus!` carries ZERO obligations; `#[derive(Clone)]`
   carries one.** Measured eleven ways in minimal files and four ways on p29's
   own `verus.rs`; the engineer's own probe is confounded by a `derive` its
   description omits. Confirmed against `p36`'s shipped census, which counts a
   struct as zero and sums exactly.
2. **`p29`'s read-path safety line CAN be spelled with ONE exact conjunct** —
   two spellings, `0/500` wrong, `0` ASan lines, agreeing with R1h on all eight
   committed inputs; one of them adds no state, widening `live[]` from the bit
   `p27`'s own kernel calls a degenerated generation counter. **The row's
   counting headline is false; the row is not a duplicate.**
3. **The `-O0` `differ` is `R5 ⊃ R4` by exactly 42 dead stack round-trips at 7
   sites, and 0 at `-O3`** — the disclosed gap in §8, closed, and a stronger
   statement than *"three spellings, none is 900"*.
4. **The gate's Miri limit is structural (27/27 `miri.sources`, 202/202 rows
   `ub: false`) but it is not new and p29's arm is not the tree's first** —
   `p42/controls/miri_seeds.sh` ships the identical design and already states
   the `miri.sources == ["unsafe.rs"]` hole in writing.
5. **`model.py`'s independence holds for the checksum half and fails for the
   `ensures` half**: `_run_spec` carries all twelve of `kernel.c`'s control
   variables, by AST census. The artefact is fine; three committed summaries are
   not.
6. **A cost claim that needs no lever search is available and unpublished**:
   `R1h − R1` is `−17.53 / +7.65` (gcc) and `−27.17 / −89.14` (clang) Ir/call —
   **p29's own safety line measures free** — while `R3 − R4` at `+193.53 /
   +1092.51` is *larger* than the `p27` figure `RECAP` 47 publishes with no
   lever search at all.
7. **`p29` is not findable in the project's numbers file.**
   `results/synthesis.md` still reads `Patterns: 26. Gate records: 26`, contains
   zero occurrences of `p29`, and states an `identity` census p29 falsifies —
   while `SYNTHESIS.md` sends every reader there for the numbers.

**679 + 8 = 687.**

---

## 15 — SCRATCH

`.temp/t140/` — generators and evidence kept, binaries deleted.

```
probes/onecon.py       the two single-conjunct arms (§1)     -> onecon.json
probes/vacuity.py      the seven assert(false) sites (§4)    -> vacuity.json
probes/model_census.py the model.py AST census (§6)
verus/*.rs             every obligation and vacuity probe, as source (§4, §8a)
render/*.md          all 27 patterns rendered with report.py --stdout, for the
                     published-table diff sweep (blocker box)
logs/onecon.log  logs/gate-t140.log  logs/asm-diff-O0.log
b/k_*.c              the four generated kernels, as source
```

Everything regenerates:

```sh
python3 .temp/t140/probes/onecon.py            # §1
python3 .temp/t140/probes/vacuity.py           # §4  (7 Verus runs, ~15 min)
python3 .temp/t140/probes/model_census.py      # §6
python3 harness/build.py p29 --cell unsafe --opt O0 --mode isolated
python3 harness/build.py p29 --cell verus  --opt O0 --mode isolated
python3 harness/asm.py diff .temp/build/p29/unsafe-O0-isolated \
                            .temp/build/p29/verus-O0-isolated  # §5
for f in .temp/t140/verus/ob_*.rs; do ./verus_run.py "$f"; done # §8a
./verus_run.py .temp/t140/verus/p29_plus1.rs                    # §8a  -> 25
./verus_run.py .temp/t140/verus/p29_plus1_derive.rs             # §8a  -> 26
harness/check.py p29                                            # §9   -> FAIL
# the blocker, with NO gate run and NO build:
git show HEAD:results/gate/p29-bst-delete.json | grep -o '"controls_json".\{0,120\}'
git show HEAD:results/tables/p29-bst-delete.md | grep -c 'controls/.*STALE'
harness/report.py p29 --stdout | grep -c 'STALE'
```
