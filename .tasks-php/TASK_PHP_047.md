# TASK_PHP_047 — THE REVIEW ROUND: **7 unreviewed findings**, and **ONE OF THEM IS ASKING THE USER FOR A DECISION**

**Role:** research **reviewer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_047_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** Every task in this programme
told to *try to break* a prior headline has succeeded: `_030` turned *"closes to
the digit with no residue"* into an arithmetic identity true of any input pair
(F78); `_038` refuted three manager claims in one report; **`_043` refuted the
manager's route to its own biggest result and cost the published record one
headline and four qualifiers**; `_044` then refuted `_043` three times and found
two more manager errors. ▶ **Four rounds, four refutations of the thing that
looked settled. Assume the same of what you review.**

⚠⚠ **AND THE SUBJECT IS THREE ENGINEER TASKS THE MANAGER HAS ALREADY LANDED
INTO `.memory-php/`.** `_044`, `_045` and `_046` have had the **engineer half
only**; the manager landed their material into the authoritative layer and then
caught it in a pre-handoff audit, so it now sits there under an explicit
`UNREVIEWED` banner. ▶ **Your coverage table is what decides whether those
banners come off or the entries come out.**

---

## §0 ⛔⛔ READ THIS FIRST: THE STOP INSTRUCTION

**Seven findings are unreviewed: F96 · F97 · F102 · F103 · F104 · F105 · F106.**
`_043` took 1408 lines to review twelve, and **`_038` took 840 for five**.

▶ **WORK THE SECTIONS IN ORDER. WHEN YOUR DEPTH RUNS OUT, STOP AND SAY WHERE.**

⭐⭐ **A round that reviews 4 of 7 honestly and names the other 3 as UNREVIEWED
is worth strictly more than one that claims 7**, because the manager's next move
is routed off your coverage list and **a falsely-closed cycle lets a wrong
finding into `.memory-php/`, which is the one error this process exists to
prevent.** `UNTESTED` and `I could not tell` are **valued answers** — `_039`
shipped a negative's failure rather than hide it, `_040` shipped a defect it
could not fix, `_046` retracted its own control's framing in its own sidecar.
**All three were the right call.**

**Read**, in this order:

1. `RECAP_PHP.md` — the **RULE-9 STATE block** (it names your scope and its
   ranking), then **F96, F97, F102, F103, F104, F105, F106**, then open items
   **97, 103, 105, 107, 108, 109**. ⚠ Read F104 **and** F106 together: F106 is
   F104 measured on rung candidates rather than argued.
2. `.tasks-php/PROTOCOL_PHP.md` — **§H** (a validator change lands with its
   must-fire negatives), **§B1a**, **§C**, **§F5**, **§F6**, **§H1**.
3. `.tasks/PROTOCOL.md` — rules 6, **9**, 10, 11, 13, **14**. **Rule 9 is why
   this task exists.**
4. `.tasks-php/STATISTICS_001.md` — the statistic argument, **including its new
   §7** (the settled axis, and the rule that a statistic finding lands there in
   the same commit as it lands in RECAP).
5. `.memory-php/02-ladder.md`, `03-numbers.md`, `04-process.md` — **the
   `UNREVIEWED, MANAGER, 2026-09-13` banners mark exactly the material you are
   reviewing.** ▶ **If you REFUTE something under a banner, say so in those
   words, because the manager must then remove text from the layer.**
6. `patterns-php/ph52-concat-copy-uninit/` — `controls/spellings.json`,
   `controls/spellings.py`, `verus.rs`, `NOTES.md`, `spec.md`.
7. `.tasks-php/TASK_PHP_044_REPORT.md`, `_045_REPORT.md`, `_046_REPORT.md`.
8. The committed checkers: `.tasks-php/{boxcheck,citecheck,coverage,quota,
   fixsurvey,preimage_screen,php_null,task_cost,width}.py` and
   `.tasks-php/asan_fill_byte.c`. ⭐ **Run every `--selftest` you rely on and say
   so.** ⚠⚠ **`.temp/` is GITIGNORED — a number you want to survive goes in YOUR
   REPORT, not behind a pointer** (F99's own defect; do not reproduce it).

---

## §1 ⭐⭐⭐ PRIORITY 1 — F106 / ITEM 105: **IS THE `4 → 3` A REAL TCB REDUCTION, OR AN AXIOM RELOCATED INTO vstd?**

**Why this is first.** ⛔ **It is the only finding on file that asks the USER for
a decision**, and the decision (fork a gate rule between two programmes, or
re-gate 33 PAT patterns, or leave a verified improvement out of the corpus)
rests entirely on `_046`'s reading of `harness/check.py`'s internals. **If the
reading is wrong, the decision evaporates and the manager must withdraw the
question.**

### 1.1 The three refusals, MANAGER-VERIFIED FROM THE ARTEFACT — reproduce them, do not inherit them

**From `patterns-php/ph52-concat-copy-uninit/controls/spellings.json`**, field
`smaller_surface_found` and the per-variant records (**the manager read these
directly and is telling you which file**, F99):

| variant | `external_body_items` | `gate_facts.n_twins` | `gate_refusals` | `pct_vs_own_side_a1` | `kernel_digest` | `verus_msg` |
|---|---:|---:|---|---:|---|---|
| `v0_shipped` (R4) | **4** | 1 | `[]` | 0.0 | `2f8fbf60a9eb` | `33 verified, 0 errors` |
| ⭐⭐ **`r4_no_wrapper`** | **3** | 1 | **`5-tcb-unsafe`** | **0.0** | **`2f8fbf60a9eb`** ← **identical** | ⭐ **`34 verified, 0 errors`** |
| `r4_win_oprec` | **3** | **0** | **`5c-twin`** | 4.084792 | `6fc9d5fdcfdb` | `33 verified, 0 errors` |
| `r4_win_checked` | **3** | **0** | **`5c-twin`** | 7.769824 | `5749e68502da` | `33 verified, 0 errors` |

`byte_identical_pairs` records **`"r4_no_wrapper == v0_shipped": true`**.
`gate_refusal_detail` for `r4_no_wrapper` reads: *"1 `unsafe` token(s) at
line(s) [548] sit outside every item `_is_trusted` accepts
(`['win_get_unchecked']`), and that stage has NO hatch."*

▶ **ATTACK ALL OF IT:**

1. **Re-derive the two refusals from `harness/check.py` itself**, not from
   `spellings.py`'s reimplementation of it. `spellings.py`'s
   `gate_rules_computed` says it drives `_is_trusted`, `vparse.parse`,
   `vparse.blank_noncode` and `_UNSAFE_RE`, with a `gate_rule_selftest` over 8
   synthetic sources (4 must-fire, 4 must-not-fire). ⛔ **A reimplementation that
   calls the real functions can still assemble them wrongly.** ▶ **Run
   `gate_rule_selftest`; then construct the refusal by the path `check.py`
   itself takes** (`check_trusted_twins` at `check.py:6969`, the `n_twins == 0`
   branch at `:7420-7426`; `_scan_unsafe_sites` at `:4925`).
2. ⭐ **The `33 → 34 verified` is a free independent corroboration — check that
   it means what it looks like.** Removing `external_body` should make Verus
   *check* one more item rather than trust it, i.e. **`+1` verified item is
   exactly the signature of an axiom becoming a proof obligation.** ▶ **If the
   `+1` is something else, F106's headline is wrong.**
3. ⚠ **Is `external_body_items` the right TCB metric at all?** It counts items.
   ▶ **Does the project's published trusted-surface axis count items, lines,
   call sites, or `unsafe` tokens?** `v0_shipped` and `r4_no_wrapper` have the
   same `unsafe_tokens` (2) and the same `trusted_call_sites` (11).
   **If the published axis is not `external_body` count, F106 is measuring a
   quantity nobody publishes.**

### 1.2 ⭐⭐⭐ THE QUESTION THE MANAGER FOUND WHILE WRITING THIS, WHICH IS **NOT** IN F106 — AND IT POINTS THE WAY THAT MAKES ITEM 105 **MORE** URGENT, WHICH IS EXACTLY WHY YOU MUST ATTACK IT

⛔⛔ **THE OBVIOUS COUNTER TO F106 IS *"`4 → 3` DOES NOT REDUCE THE TCB, IT
RELOCATES ONE AXIOM INTO vstd"*** — because `r4_no_wrapper`'s body is
`unsafe { *m.assume_init_ref() }`, and `assume_init_ref` is specified in the
pinned vstd by an `assume_specification`, **which is itself an axiom.**

**What the manager measured, with the exact text, so you can attack the
inference rather than hunt for the evidence** (rule 14):

> **`~/tools/verus/vstd/std_specs/maybe_uninit.rs:45-49`**
> ```
> pub assume_specification<T>[ MaybeUninit::<T>::assume_init_ref ](m: &MaybeUninit<T>) -> (ret: &T)
>     requires m.mem_contents().is_init(),
>     ensures ret == m.mem_contents().value(),
>     opens_invariants none
>     no_unwind;
> ```
> **`patterns-php/ph52-concat-copy-uninit/verus.rs:537-546`**
> ```
> #[verifier::external_body]
> #[inline(always)]
> fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> (r: Pr)
>     requires m.mem_contents().is_init(),
>     ensures  r == m.mem_contents().value(),
> { unsafe { *m.assume_init_ref() } }
> ```

⭐ **The manager's reading — OFFERED TO BE ATTACKED, NOT AS A RULING:** the row's
hand-written axiom is a **verbatim restatement of a vstd axiom that is already in
the TCB of every row in both programmes**, so deleting it is a **strict**
reduction and not a relocation — nothing new enters the trusted base, one
hand-written duplicate leaves it. ⓘ The row's own comment at `verus.rs:527-536`
says the same thing and adds that **`controls/mu_unwrapped.rs` verifies that
shape at 0 trusted items**.

⛔⛔ **THREE WAYS THAT READING COULD BE WRONG, AND YOU ARE BEING HANDED THEM
BECAUSE THE MANAGER WANTS IT TO BE TRUE:**

* **(i)** The `requires`/`ensures` are **not** verbatim-equivalent — a `&T`
  returned by reference versus a `Pr` returned by value is a **copy**, and the
  wrapper's `ensures` quantifies over the copy. ▶ **Is the wrapper's contract
  strictly implied by vstd's, or does it add something?**
* **(ii)** ⭐ **Does the project's TCB accounting already count vstd?** If it does
  **not** — if the published axis is *axioms this repository wrote* — then the
  two configurations are **not** comparable on that axis and F106's *"one fewer
  axiom"* is a category error.
* **(iii)** **Verify `mu_unwrapped.rs` actually verifies at 0 trusted items**,
  by running it, not by reading the comment about it. ⚠ **A comment is not
  code** — that is `spelling_matches`'s own lesson and it has now caught this
  programme three times.

### 1.3 ⭐⭐ AND THE REFRAMING THAT WOULD CHANGE WHAT THE REPAIR EVEN SAYS

`_scan_unsafe_sites`'s rule is *every `unsafe` token in a pinned Verus source
must sit inside a trusted body*. Its premise is that **an `unsafe` token marks
code the TCB accounting cannot see.** ▶ ⛔ **Here that premise is false: the
token's contents are specified by a pinned `assume_specification` and Verus
checks the call against it.** ⭐⭐ **So the candidate finding is not *"this row
wants an exemption"* — it is *`_scan_unsafe_sites` conflates `unsafe` the TOKEN
with unverified the PROPERTY, and a vstd `assume_specification` is exactly where
they come apart.*** ▶ **Rule on whether that reframing holds.** It matters
because it changes what option (b) would have to say, and a rule forked between
two programmes on a **wrong** diagnosis is worse than no fork.

⛔⛔ **TWO THINGS YOU MAY NOT DO.**
* ⛔⛔⛔ **DO NOT EDIT `harness/` — not to test this, not for one line.** It is
  hashed into all 33 PAT gate records; an edit costs a 33-pattern re-gate.
  **Copy what you need into `.temp/php47/` and drive it there.**
* **Do NOT take the decision.** Options (a)/(b)/(c) are the **user's** call and
  the manager has explicitly declined to take (b) unasked. ▶ **Your deliverable
  is whether the PREMISE survives**, plus — if it does — **the exact condition
  text** you would put in `harness-php/`, drafted, so one decision routes one
  edit.

---

## §2 ⭐⭐ PRIORITY 2 — F105's **128.00 OF 131.19 Ir/call**: A 97.6 % ATTRIBUTION TO ONE NAMED TERM IS **F83's SHAPE**

**F83 is the finding that attributed a difference to the wrong term**, and it
stood until someone brought a second method. **This is the same shape at a
higher confidence**, so it gets the same treatment.

**The claim, from `controls/spellings.json`'s `r3_gap_mechanism`
(manager-quoted, re-read it):** shipped-R3 minus shipped-R4 is
**`131.18748 Ir/call`**; the static prediction is **`128.00`** = 8 instructions
per op × 16 ops, where `extra_panic_sites_in_shipped_r3 = 4` and
`cap = (74 − 8) / 4 = 16` on `inputs/small.bin`'s stride 74.

▶ **FOUR ATTACKS, IN ORDER OF CHEAPNESS:**

1. ⭐⭐ **THE ARITHMETIC MAY BE AN IDENTITY.** `_030` found exactly this: a
   number that "closes with no residue" because the closure was true of any
   input. ▶ **Is `8 × 16 = 128` a *prediction*, or is it recoverable from the
   same measurement it is being checked against?** **Check it on `large.bin`,
   where the stride and `cap` differ** — `ir_per_call_large` is recorded for
   every variant. ⛔ **A model that fits one input and is never tested on the
   second is not 97.6 % attributed; it is unfalsified.**
2. **Count the instructions yourself.** `harness/asm.py` is the gate's only
   objdump pipeline. ▶ **Are there really four `cmp`/`je` pairs at 8
   instructions, in the hot loop, at `O3/isolated`?** `panic_call_sites` records
   R3 `v0_shipped` **5**, R4 `v0_shipped` **1**, `r3_chunks_exact` **1** — ⚠
   **5 − 1 = 4 is the panic-site delta, and the claim needs the four to be the
   four in the loop**, not four anywhere in the symbol.
3. ⭐ **The two nulls are the strongest part — test that they are nulls.**
   `r3_head_slice` records `kernel_digest` byte-identical to R3 `v0_shipped`,
   and `r4_oprec_checked` puts the checks back at `+7.77 %`. ▶ **`+7.769824 %`
   of what? Re-derive it in Ir/call and check it against 128.00.** If putting
   the checks *back* costs a different number from taking them *out*, the term
   is not isolated.
4. ⚠ **The residual is `3.19 Ir/call` and the finding does not name it.** ▶
   **Is 2.4 % unattributed, or is it the sign that a second term is present and
   partly cancelling?** ⓘ The row itself found a second term —
   `ctl_r3_unchecked_is_not_an_upper_bound` says `chunks_exact` also deletes
   **per-op offset arithmetic**. **If offset arithmetic is worth anything, it is
   in this 3.19 and the 128 is over-attributed.**

⭐ **AND THE HEADLINE RESTING ON THIS:** *a **safe** respelling beats the same
rung with every bounds check removed, by 0.82 %* (`r3_chunks_exact` 1930.232 vs
`ctl_r3_unchecked` 1946.174 Ir/call, `small.bin`, `O3/isolated`, **A1**). ▶
**Re-derive the 0.82 % and say whether it survives on `large.bin`.** ⛔ **A
magnitude floor with every sign claim** — 0.82 % is small and this programme has
had an outlier test fire at `0.00 pp`.

---

## §3 ⭐⭐ PRIORITY 3 — F103's WITNESS **DECOMPOSITION**: IT REPLACED A MANAGER LAW, AND ITS AUTHOR SAYS IT CANNOT SEPARATE ITS OWN TWO MECHANISMS

**What happened:** the manager's *"the cost of a safety witness is O(the number
of slots)"* was **refuted** — 3× the slots gives **8.19×** the cost — and
replaced by **`(slots) × (per-slot cost)`**, with the per-slot term itself
**2.73×** higher on `ph53` than `ph52`.

| | `ph53` | `ph52` | ratio |
|---|---:|---:|---:|
| witness, Ir per kernel call | **+101.59** | **+12.41** | **8.19×** |
| slots | 6 typical | 2 | 3× |
| Ir per slot per call | 16.93 | 6.21 | **2.73×** |

▶ **THE ATTACKS:**

1. ⛔⛔ **A DECOMPOSITION WITH A FREE PARAMETER EXPLAINS ANY TWO POINTS.**
   `(slots) × (per-slot)` has the per-slot term fitted from the same two rows it
   is explaining. ▶ **Is it a model, or is it `8.19 / 3 = 2.73` written as a
   product?** ⭐ **This is the single question that decides whether it belongs in
   `.memory-php/` at all** — and it is currently in `02-ladder.md` under a
   banner.
2. **The engineer already declared the limit** (*read count* and *indexed vs
   register* point the same way; normalising by reads gives 1.59 vs 0.39
   Ir/read, neither isolated). ✅ **That declaration is the right behaviour.**
   ▶ **Your job is to check the declaration is COMPLETE — is there a third
   candidate neither names?** ⓘ Consider: `ph53`'s witness is in a loop nested
   `n_ops × n_decl`; `ph52`'s is tested twice per op. **Is the difference
   *indexed vs register*, *read count*, or simply **loop nesting depth**?**
3. ⚠ **`6 typical` is not a number.** ▶ **`ph53`'s slot count is input-dependent
   — what is it on the cell the `+101.59` was measured on?** If the 3× is really
   2.4× or 4×, the 2.73× moves and so does every statement built on it.
4. ⭐ **The `+12.41 Ir/call (+0.632 %)` itself**: which input, which statistic,
   and does B1/W1's `+0.622 %` agreement mean two methods or one measurement
   twice? ⛔ **Never publish a percentage without saying WHICH INPUT and WHICH
   STATISTIC** — four families are in use and three are published.

---

## §4 ⚠⚠ PRIORITY 4 — F97, STILL UNREVIEWED AND NOW **LOAD-BEARING THREE TIMES**

F97 — *two **sound** gate rules are **jointly unsatisfiable** for a
`MaybeUninit` read* — has been unreviewed since `_043` and **F104, F106 and
§1 above all rest on it.** ▶ **It is the oldest debt in the backlog and the
cheapest to discharge now, because `ph52` gave it a second instance.**

**The bar:** **(i)** re-derive the joint unsatisfiability from `check.py`'s two
stages on **both** rows (`ph53`, 4 trusted items; `ph52`, 1) — ⭐ **two rows with
opposite trusted-base sizes is the second method F97 never had**; **(ii)** check
the *"no safe exec route from `MaybeUninit<T>` to `T`"* claim against the
**pinned** vstd, **grepping `std_specs/` specifically AND the inherent
spelling** (this exact confusion has produced a false *"no spec exists"* claim
twice in this project); **(iii)** a verdict.

⚠ **F100 promoted F97 from argument to a MEASURED FLOOR on three arms nobody has
re-run.** ▶ **Re-run them or mark F97 `UNTESTED` on that half and say which
half.** ⓘ You need `verus_run.py` (`TOOLCHAIN.md`) and
`patterns-php/ph52-concat-copy-uninit/controls/r4_nowitness.rs`.

---

## §5 THE BOUNDED PASS — **F96 · F102 · F104**

**Only if §§1–4 are done.** ⛔ **Do NOT skip §§1–4 to get coverage here.**

**The bar per finding, deliberately low:** **(i)** re-derive the headline NUMBER
from an artefact you **name**, or write **UNTESTED**; **(ii)** one sentence on
whether the CLAIM is scoped to what was measured; **(iii)** a verdict of
**UPHELD / UPHELD-NARROWED / REFUTED / UNREVIEWED**.

* **F104** — you will have done most of it in §1; what remains is the **perverse
  incentive** claim (*the rule pressures a row to ENLARGE its TCB*). ▶ **Is that
  a real incentive or a rhetorical one?** `ph52` found a legitimate way out
  (`win_get_unchecked`, a fidelity repair worth `−7.12 %`) **that it owed
  anyway**, which is evidence *against* the pressure being binding. **Say which.**
* **F102** — `ph52` is admitted on the C, and *the defect is silent on a clean
  stack*. ⚠ **F103 §3.1 says F102's *"five named cases out of a byte"* is wrong
  in three ways.** ▶ **A finding partially refuted by the row built on it needs
  its SURVIVING half stated exactly.** ⓘ `.tasks-php/asan_fill_byte.c` is
  committed and re-runnable; `0xbe` is ASan's **runtime option default**, not a
  property of the shipped build.
* **F96** — `ph53` built, 3 of 4 predictions refuted. ⓘ It is a build record plus
  a prediction ledger with no cheap second method, which is why it has sat
  unreviewed through two rounds. ▶ **If the honest answer is still UNREVIEWED,
  say UNREVIEWED** — but check first whether `ph52` has since supplied the
  second method for any of its four predictions.

---

## §6 ⛔ Scope, brackets, traps

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, or `pilot/`.** ⭐ **This task
measures and argues; it edits nothing that is hashed.** Scratch under
`.temp/php47/`. ⚠ **No `git add` / `git commit`.** Never touch `.web/` — a
concurrent session owns it.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`18/0`**, **first and
last.** **Both verified by the manager immediately before writing this.**
⚠⚠ **Nothing in your scope can move either.** ⓘ **The php bracket covers GATE
records as well as measurement records**, so it can legitimately read `18/1`
mid-task if a gate-only file moves — **but nothing in your scope should move
even that.** If either moves, **stop and report**.

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35): 41 corpus files exit 1 silently under plain
   `grep`, and a probe script does **not** reproduce it. ⭐ **AND a line-based
   grep cannot find a prose phrase that WRAPS** — that error has been made twice
   here, once by the manager asserting an absence.
2. ⛔ **Never publish a percentage without saying WHICH INPUT and WHICH
   STATISTIC.** Four families are in use and three are published.
3. ⚠ **A magnitude floor with every sign claim.**
4. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; no
   `until … sleep` poller loops. ⛔ Confirm a full command line for an exact PID
   before killing anything.
5. ⚠ **A truncated `ls`/`head` is not evidence of absence.**
6. ⓘ **`verus_checked` and `problems` are NOT gate-record fields** — they live in
   `controls/spellings.json`, and `problems` is also a **preflight** field.
   **NAME THE FILE EVERY FIELD CAME FROM** (F99, item 84).
7. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` DRAFT IS A PIN** (item
   100, **three instances in three tasks**). **If you draft any contract prose,
   run `spellings.py --audit-only` on it before quoting it.**
8. ⚠ **`.temp/php47/`: keep the generator, delete the artefact.** Binaries,
   `.o`, `.bin` go once your gates are green; the `.py`, `.rs`, `.json`, `.log`
   and `NOTES.md` stay. **If a blob has no script that rebuilds it, write one.**

---

## §7 Definition of done

1. ⭐⭐⭐ **A VERDICT ON F106's PREMISE** — the three refusals reproduced from
   `check.py` itself, **plus a ruling on §1.2's relocation question and §1.3's
   reframing.** ▶ **And if the premise survives: the exact `harness-php/`
   condition text, drafted.** ⛔ **Do not take the decision.**
2. **F105: the 128-of-131 attribution, tested on a SECOND input**, and the
   0.82 % safe-beats-unchecked result re-derived with its magnitude floor.
3. **F103: a ruling on whether the decomposition is a model or a restatement**,
   and whether the engineer's declared limit is complete.
4. **F97: a verdict, with the pinned-vstd grep done properly** (`std_specs/`
   **and** the inherent spelling).
5. **§5's bounded pass as far as you got**, bar (i)–(iii) satisfied per finding.
6. ⛔⛔ **A COVERAGE TABLE: every one of F96, F97, F102, F103, F104, F105, F106,
   and for each exactly one of UPHELD / UPHELD-NARROWED / REFUTED /
   UNREVIEWED.** ▶ **This table is how the manager decides what may enter
   `.memory-php/` and what must come OUT of it**, so an honest `UNREVIEWED` is
   as useful as a verdict and a falsely-closed cycle is the one unrecoverable
   error.
7. ⭐ **AN EXPLICIT LIST OF WHAT MUST BE REMOVED FROM `.memory-php/`** if you
   refuted anything under an `UNREVIEWED` banner — quote the sentence.
8. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `_041` reported 15
   uncertainties and found its own citation defect; that is the standard.
9. **Brackets `66/0` / `18/0`, unmoved, quoted first and last.**
10. ⛔ **If a finding survives everything you can throw at it, THAT IS A RESULT.**
    `_038` upheld F85 and F86 while refuting three other claims. **Do not
    manufacture a refutation to have something to report.**
