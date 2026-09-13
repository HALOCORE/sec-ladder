# TASK_PHP_047 REPORT — the review round: 7 unreviewed findings

**Role:** research **reviewer**, one agent, alone. **Job: falsify.**
**Scope:** F96 · F97 · F102 · F103 · F104 · F105 · F106.
**Nothing under `harness/`, `common/`, `common-php/`, `patterns/`, `patterns-php/`,
`results/`, `results-php/`, `pilot/`, `.memory-php/`, `RECAP_PHP.md` or `.web/` was
edited.** All scratch is `.temp/php47/`. No `git add`, no `git commit`.

---

## §0 BRACKETS — FIRST AND LAST, BOTH UNMOVED

| | first (before any work) | last (after all work) |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | **`66 record(s) examined, 0 STALE`** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **`18 record(s) examined, 0 STALE`** | **`18 record(s) examined, 0 STALE`** |

`git status --porcelain` is **empty** at the end of the task — not one tracked file
moved, and `.temp/` is gitignored so it does not even appear.

**Selftests I relied on and ran, with their own output:**

| tool | result |
|---|---|
| `patterns-php/ph52-concat-copy-uninit/controls/spellings.py --audit-only` | `english_verdict_selftest PASS` (10 arms) · **`gate_rule_selftest PASS` (8 arms, 4 must-FIRE, 4 must-NOT-fire)** · `checksum_selftest PASS` (6 arms) · `consistency (real rows) ok` |
| `patterns-php/ph52-concat-copy-uninit/controls/tag_sweep.py --selftest` | `15 assertions (9 must-fire claims, 6 must-NOT-fire)` — **PASS** |

⚠ **Per §6 trap 7, I drafted no `idiom.required`/`forbidden` prose**, so no backtick
pin could be created. The §1.4 draft below is *gate-condition* text for
`harness-php/`, not contract prose, and carries no backticked idiom span.

---

## §1 ⭐⭐⭐ F106 / ITEM 105 — **THE PREMISE SURVIVES EVERYTHING I THREW AT IT, AND SURVIVES BETTER THAN THE MANAGER ARGUED IT. THE RECOMMENDATION DOES NOT: ⛔ OPTION (b) DOES NOT EXIST (§1.7).**

### 1.1 The three refusals, re-derived from `check.py` ITSELF

Driver: **`.temp/php47/repro_gate.py`**, output **`.temp/php47/repro_gate.json`**.
It imports `harness/check.py` read-only, rebuilds each variant's `verus.rs` by
**literal substitution transcribed by hand from `patterns-php/ph52-concat-copy-uninit/verus.rs`**
(it does **not** call `spellings.py::materialise`), drops the copy into
`.temp/php47/pdir/`, and calls `check._scan_unsafe_sites` and
`check.check_trusted_twins` directly.

| variant | `_is_trusted` (check.py's own predicate) | `external_body` items | twins | 5-tcb-unsafe | 5c-twin |
|---|---|---:|---|---|---|
| `v0_shipped` | `['slot_read_unchecked','win_get_unchecked']` | 4 | 1 | **0 fails** | **0 fails**, 1 BLOCKED |
| ⭐ `r4_no_wrapper` | `['win_get_unchecked']` | **3** | 1 | ⛔ **1 FAIL at `verus.rs:548`** | 1 FAIL (obligation-count pin, see below) |
| `r4_win_checked` | `['slot_read_unchecked']` | **3** | **0** | 0 fails | ⛔ **1 FAIL — `n_twins == 0`** |

▶ **ALL THREE REFUSALS REPRODUCE, by `check.py`'s own code path**, and the
`r4_no_wrapper` message names **line 548** — exactly what
`controls/spellings.json`'s `gate_refusal_detail` records. I checked the line
number is not a transcription error: the shipped `unsafe` token is at
`verus.rs:545` (`grep -an unsafe`), the substitution replaces one attribute line
with four comment lines, net **+3**, so 545 → 548. ✓

Both `r4_win_*` variants fail through `check.py:7420-7426`'s
`if justified: if n_twins == 0: rep.fail(...)`. I read the other branch too: a
trusted item with **no** twin and **no** justification takes `rep.fail("twin", …)`
at `check.py:7178`. **So both branches are hard failures and F104's *"a pattern
with ONE untwinnable trusted item has no legal configuration either"* is CORRECT
as written.**

⚠ **ONE THING F106 DOES NOT SAY, FOUND BY DOING IT PROPERLY.** `r4_no_wrapper` is
refused by **two** stages, not one. The second is 5c-twin reporting
*"`--cfg slb_twin` reports 35 verified, spec.md pins `verus.twin_obligations`=34
(34 verified without the cfg, pinned 33)"*. ✅ **This is NOT a blocker** — it is
the obligation-count pin, and a `spec.md` re-declaration removes it, which is
exactly the class `spellings.json`'s `gate_rules_computed` says it deliberately
does not compute (*"the two a spec.md re-declaration could NOT remove"*). The
field is honest. ⭐ **But it is also a free third corroboration of the `33 → 34`,
from `check.py`'s own Verus invocation rather than from `spellings.py`.**

### 1.2 ⭐⭐ The `33 → 34` is EXACTLY what it looks like — and I have a negative arm to prove it

Driver: **`.temp/php47/verus_probe.py`**, output **`.temp/php47/verus_probe.json`**.
Four arms through `./verus_run.py … --crate-type=lib`:

| arm | result |
|---|---|
| **A** shipped `verus.rs` | `33 verified, 0 errors` |
| **B** `external_body` off `slot_read_unchecked` | **`34 verified, 0 errors`** |
| **C** B **with the `requires m.mem_contents().is_init()` conjunct deleted** | ⛔ **`33 verified, 1 errors`**, `error: precondition not satisfied` at the body's `*m.assume_init_ref()`, **pointing at `vstd/std_specs/maybe_uninit.rs:46:13`, `failed precondition`** |
| **D** `controls/mu_unwrapped.rs` | `6 verified, 0 errors` |

⭐⭐⭐ **ARM C IS THE TEST THE TASK ASKED FOR AND IT PASSES DECISIVELY.** Deleting
the precondition drops the count **back to 33** and produces an error **at the
vstd `assume_specification` site**. So the `+1` verified item is precisely
`slot_read_unchecked` being checked against `vstd/std_specs/maybe_uninit.rs:45-49`.
**It is not an accounting artefact and it is not something else: an axiom became a
proof obligation, and the obligation is discharged by the caller's witness.**
⓵ The `+1` is additive with the twin's `+1` (34 without the cfg → 35 with), which
is a fourth consistency check.

### 1.3 ⚠ Is `external_body_items` the right TCB metric? **YES on this project's published axis — and F106 UNDER-STATES the reduction**

`.memory/04-verus.md:207`: *"**What ships instead: one headline number — the gate's
own `tcb_items`** — plus a three-way classification of what each item is."*
`:296` confirms the counting rule (`verus.rs` only) *"matches every pattern's
published TCB"*. `:115`: *"Report as: `TCB: N lines across M items`."*

From **`results-php/gate/ph52-concat-copy-uninit.json`**, field
`/verus/verus.rs/tcb_items`: **4 items** — `load_input` (4 body lines), `emit` (1),
`win_get_unchecked` (1), `slot_read_unchecked` (1) — **TCB 7 lines across 4 items**.

▶ So `external_body_items = 4` **is** the published number, and `r4_no_wrapper`'s
**3 items / 6 lines** is a reduction on **both halves** of the published axis.
⭐ **And on `check.py`'s own `_is_trusted` predicate the drop is 2 → 1**, because
`_is_trusted` deliberately excludes `emit` and `load_input` ("trusted I/O with no
postcondition", `check.py:4332-4374`). **F106's `4 → 3` is therefore the
CONSERVATIVE framing; the security-bearing count halves.**

⚠ The other two published trusted-surface numbers **do not move**:
`unsafe_tokens` stays **2** and `trusted_call_sites` stays **11**
(`controls/spellings.json`, `variants[]`). F106 does not claim they do, and the
manager was right to flag it, but the report should say so: the reduction is on
`tcb_items`/TCB-lines only.

### 1.4 ⛔⛔ §1.2's RELOCATION QUESTION — **IT IS ALREADY ADJUDICATED IN `.memory/04-verus.md`, AND THE MANAGER DID NOT CITE IT**

The manager offered its reading to be attacked. I attacked it and it survives —
but the decisive evidence is **not** the argument the manager gave. It is a
section of the authoritative PAT layer that asks this exact question and answers
it, `.memory/04-verus.md` §*"How the TCB column is counted, and whether it can be
gamed (TASK_048)"*:

> *"The question that forced this: removing a trusted wrapper does not always
> delete the trust, it can **relocate it into vstd**."*

Its three rulings, all against the relocation objection:

1. ⛔ **The two-number proposal (author-written items + "vstd assumed
   specifications relied upon") was REFUTED with a census and "must not be
   reinstated"** — the pinned vstd holds *"402 `assume_specification` sites, 272
   `external_body` items and 545 `broadcast` proof fns across 44 files"*, "relied
   upon" is undecidable from the text, and *"every rung depends on the same vstd
   core, so the second column would be near-identical for every row — it does not
   discriminate."*
2. ⛔ **The `tcb_reach` column (`safe` / `local-external-body` / `vstd-axiom`) was
   also proposed and REJECTED at TASK_055_REVIEW**, for the same undecidability.
3. ⭐⭐ **THE PRECEDENT IS EXACT.** *"p06 removed one and shipped `18 verified, 0
   errors` with **byte-identical `-O3` machine code**"*, `copy_from_slice`,
   **TCB 6 → 5** — a hand-written `external_body` wrapper deleted because the
   pinned vstd already specified the operation, at byte-identical code. **That is
   `r4_no_wrapper`'s shape line for line, and the project counted it as a
   reduction and published it.**

▶ **RULING ON §1.2 (ii): the published axis does NOT count vstd, by an explicit,
measured, census-backed decision. So the two configurations ARE comparable on it
and F106's claim is not a category error.**

▶ **RULING ON §1.2 (i) — is the wrapper's contract strictly implied by vstd's, or
does it add something? IT ADDS NOTHING, AND THE PROOF IS ARM B, NOT AN ARGUMENT.**
`r4_no_wrapper` **verifies at 34/0 with the contract textually unchanged.** That is
a machine proof that `requires m.mem_contents().is_init() / ensures
r == m.mem_contents().value()` on a by-**value** `Pr` is derivable from vstd's
by-**reference** `&T` specification plus the `*` copy. Had the wrapper's `ensures`
quantified over anything the vstd spec does not give, Verus would have refused the
body. **The hand-written axiom was a theorem. Deleting a theorem that was being
asserted as an axiom is a strict reduction, not a relocation.**

⭐⭐ **AND THE REDUCTION IS LARGER THAN "ONE FEWER AXIOM", WHICH F106 DOES NOT
CLAIM AND SHOULD.** `.memory/04-verus.md` measures what an `external_body` body
hides: substituting `core::ptr::copy → copy_nonoverlapping` inside p08's trusted
`move_right` — *"a body whose whole safety contract **is** the non-overlap, and
which then commits the pattern's own UB"* — verifies `11 verified, 0 errors`
shipped and `15 verified, 0 errors` under the twin cfg, **invisible to Verus, to
the verified twin, to the contract pin and to stages 5c and 5c-req**. Removing
`external_body` removes exactly that hole for this item. So the improvement is
qualitative as well as numerical.

⚠ **THE ONE QUALIFIER I WOULD ATTACH.** `.memory/04-verus.md` marks the whole
accounting section **"PROVISIONAL — the census and the classification are
measured; the accounting decision itself has not yet been through a review."**
So F106 rests on a published axis whose *accounting rule* is itself flagged
provisional in the PAT layer. That does not weaken the measurement; it means
F106 should say *"a reduction on the published `tcb_items` axis"* and not
*"a reduction in the trusted base"* full stop.

### 1.5 ⭐ §1.2 (iii) — `mu_unwrapped.rs` DOES verify at 0 trusted items, **measured**

`.temp/php47/f97.py` / `verus_probe.py`, using `check._is_trusted` and `vparse`
on the real file:

```
patterns-php/ph52-concat-copy-uninit/controls/mu_unwrapped.rs
  items: 5   external: []   _is_trusted: []   unsafe tokens: 1
  Verus: 6 verified, 0 errors
```

▶ **0 trusted items, 0 `external` items, 1 `unsafe` token, 6/0.** The comment at
`verus.rs:527-536` is correct. ⓘ RECAP F97 cites *"7 verified / 0 errors"* for
`mu_unwrapped.rs`; that is **`ph53`'s** file, which I re-ran at **7/0**. Both
numbers are right; they are different files. No defect.

### 1.6 ⭐⭐ §1.3's REFRAMING — **IT HOLDS, AND `mu_unwrapped.rs` IS A COMMITTED DEMONSTRATION OF IT**

`_scan_unsafe_sites`'s own docstring states its premise: the rule exists so the gate
knows about `unsafe` *"that is not inside any parsed item at all — a `macro_rules!`,
a `const`/`static` initialiser, an `unsafe impl`, a nested closure outside a `fn`,
or a helper in the shared `common/driver.rs`"*, each of which *"performs an
unchecked operation that **no `requires` demands and no twin checks**."*

▶ **On `r4_no_wrapper` that premise is false, and arm C proves it: a `requires`
DOES demand it — vstd's — and Verus DOES check the call against it.** The rule is
a sound over-approximation that refuses on the **token**; the property it is about
is *unverified*, and a vstd `assume_specification` is where the two come apart.
**The reframing holds.**

⭐⭐ **AND THERE IS A SECOND, ALREADY-COMMITTED INSTANCE THE MANAGER DID NOT USE:
`controls/mu_unwrapped.rs` is a file with an `unsafe` token in a **verified,
non-trusted** body at **0 trusted items, 6/0**. If `_scan_unsafe_sites` were
applied to it, it would refuse a file Verus has fully verified.** That is the
conflation demonstrated on a committed control rather than argued — and it is
sitting inside the very row that reported the collision.

⛔ **BUT THE REFRAMING DOES NOT LICENSE A BLANKET RELAXATION, AND THIS IS WHERE I
WOULD NARROW OPTION (b).** The rule also scans `common/` files pulled in by
`#[path]`, which are `#[verifier::external]` for R5 and which Verus never verifies;
an `unsafe` there is genuinely unchecked and must stay refused. Any condition must
therefore be scoped to items Verus actually **counted**.

### 1.7 ⛔⛔⛔ **OPTION (b) DOES NOT EXIST — AND THAT REFUTES ITEM 105's RECOMMENDATION**

**This is the single most consequential thing in the round, and it is not in
F106.** The task told me to draft the `harness-php/` condition *if the premise
survives*. The premise survives. **But before drafting it I checked whether
`harness-php/` can host such a condition at all — and it cannot, on three
independent grounds, all of them already written down in the committed tree.**

**Ground 1 — `harness-php/gate.py`'s own design statement forbids it, in a banner
headed "WHAT THIS FILE IS, AND WHAT IT IS FORBIDDEN TO BE":**

> *"It is a PREFLIGHT plus an `exec`. **It REIMPLEMENTS NO GATE STAGE and must
> never grow one**: the whole value of `PLAN_PHP.md` §2.1a is that the php rows
> are **judged by the SAME code as the 33 PAT rows**, so a php-only stage here
> would be **a second, unvalidated gate wearing the first one's name**. If a php
> row needs a check the PAT gate does not have, **it goes in that row's
> `controls/` or in a separate tool**, and the report says which."*

A php-side exemption to `_scan_unsafe_sites` is exactly a php-only gate stage.

**Ground 2 — even if one were added, NO ARTEFACT COULD WITNESS IT.** The same
header, under *"WHAT THIS SCRIPT DOES NOT ENFORCE"*: *"**it cannot make itself
mandatory.** `grep -c preflight harness/{check,measure,report}.py` is `0 0 0` …
Nothing in a gate record says whether this wrapper ran — the `invocation` field is
`check.py`'s own argv and is byte-identical either way. **Closing that needs a
`harness/` edit and a 33-pattern re-gate.**"
**I re-ran both greps myself rather than inherit them:**

```
preflight refs:  check.py 0   measure.py 0   report.py 0
harness/*.py references to common-php / patterns-php / harness-php / emalloc_shim:  (none)
```

▶ **An exemption that a gate record cannot record, applied by a wrapper the gate
cannot tell ran, is not a gate rule.**

**Ground 3 — the "rebind" `CLAUDE.md` cites is PATH rebinding and nothing else.**
`harness-php/root.py:2-24` builds `.temp/php-root/`, *"the SYMLINK SHIM the
UNMODIFIED PAT gate is run out of … it runs the real thing out of a directory of
symlinks"*, and the entire mechanism is that `REPO =
os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` plus
*"`os.path.abspath` **does not resolve symlinks**"*, so *"every REPO-relative path
follows."* **It rebinds roots. It cannot change a stage's verdict.**

⛔⛔ **SO ITEM 105's RECOMMENDATION IS REFUTED.** It reads: *"My recommendation is
(b), on the grounds `CLAUDE.md`'s banner already gives — the php programme imports
`harness/` and rebinds at run time precisely so it need not re-gate 33 patterns."*
**The banner is about path roots; the manager read it as verdict override.** On
the tree's own account the option set is **two**, not three:

| | what it actually is | price |
|---|---|---|
| **(a)** | edit `harness/check.py` | 33-pattern re-gate, PAT side re-verified — **the same price `gate.py`'s header already names** for making the preflight mandatory |
| ~~(b)~~ | ⛔ **not available** — forbidden by `gate.py`'s design statement, unwitnessable in any gate record, and not what `root.py` rebinds | — |
| **(c)** | leave it; the demonstration lives in `controls/` and the report says which | what both rows did; **and it is the route `gate.py`'s header itself prescribes** |

▶ **The manager must withdraw (b) from the question put to the user, and say that
(c) is not merely "honest" but is the documented design answer.** ⚠ **The
decision itself is still the user's** — (a) buys the ability to *publish* the
smaller TCB in the corpus, which (c) cannot; that trade is a judgement, not a
measurement, and I am not taking it.

### 1.8 ⭐ THE CONDITION TEXT, DRAFTED ANYWAY — because (a) needs it too

The task asked for drafted condition text so one decision routes one edit. Since
(b) is gone, **this is the text for option (a)**, i.e. for
`harness/check.py::_scan_unsafe_sites` itself. It is written as an **exemption to
the verdict, not to the scan** — the site must still be reported:

> **`_unsafe_site_is_verified(src, item, contract)` — a narrowing of
> `check.py::_scan_unsafe_sites`'s VERDICT, applied ONLY when every one of the
> following holds. If any fails, the original hard failure stands.**
>
> 1. The token's host item is one `vparse.parse` resolved inside the pattern's
>    **own** pinned `verus.obligations` source. **`common/` includes and
>    `#[path]` files are never exempt** — they are `#[verifier::external]` for R5
>    and Verus never checks them.
> 2. The host item is **inside `verus!{}`** (`item.in_verus`) and carries
>    **neither** `verifier::external_body` **nor** `verifier::external`, i.e. it
>    is an item Verus counts in its `verified` total.
> 3. The pattern's `verus.obligations` pin for that source **rose by exactly the
>    number of items so exempted** relative to the configuration with those
>    attributes restored — the pin is what makes (2) enforceable rather than
>    declarative.
> 4. `spec.md` declares `verus.unsafe_justifications[src][item]` naming the
>    **pinned vstd `assume_specification` file and line** that specifies the
>    operation, and a `controls/` negative exists that **deletes the discharging
>    precondition and shows Verus refusing AT THAT vstd SITE**. (For ph52 that
>    negative is already written: `.temp/php47/verus_probe.py` arm C, which the
>    row would commit as a `controls/` arm.)
> 5. The token is not lexically inside a `macro_rules!` body — TASK_009_REVIEW's
>    blocker x1 is a macro bypass and (2) alone does not close it.
> 6. The stage **shouts** every exempted site with its vstd citation, so the
>    exemption is loud in the gate record and never silent.

⭐ Condition 4 is what turns the exemption from a promise into a measurement, and
condition 3 is what stops it drifting. ⚠ **Conditions 1, 5 and 6 are mine, not the
manager's**, and they exist because without them the reframing would re-open the
exact blocker the rule was written for.

---

## §2 ⛔⛔ F105 — **THE `128.00` OF `131.19` IS A TWO-ERROR CANCELLATION, AND IT DOES NOT SURVIVE THE SECOND INPUT**

Driver: **`.temp/php47/attrib.py`**, log **`.temp/php47/attrib.log`**. **Every
figure comes from `patterns-php/ph52-concat-copy-uninit/controls/spellings.json`,
fields `variants[].ir_per_call_small` and `variants[].ir_per_call_large`, family
**A1**, `O3/isolated`.** The two strides come from
`patterns-php/ph52-concat-copy-uninit/inputs/gen.py:94-95` —
`SMALL_STRIDE = 74  # cap 16`, `LARGE_STRIDE = 181  # cap 43` — with
`cap_of(stride) = (stride - 8) // 4` at `:105-106`, and `tiled()` at `:236-241`
fills every window to `cap`, so ops-per-call **is** `cap`.

### 2.1 Attack 1 — the second input, and the residual CHANGES SIGN

| input | cap | F105's prediction `8 × cap` | measured `R3 v0_shipped − R4 v0_shipped` | prediction / gap | residual |
|---|---:|---:|---:|---:|---:|
| `small.bin` | 16 | 128.00 | **131.18748** | **97.57 %** | **+3.187** |
| `large.bin` | 43 | 344.00 | **335.79390** | **102.44 %** | **−8.206** |

⛔ **The `97.6 % attributed` is a property of `small.bin`, not of the mechanism.**
On the second input the same construction **over**-predicts. There is no stable
"2.4 % unattributed" and **no 3.19 Ir second term to name** — the residual flips
sign. A two-point fit of the gap gives **slope 7.578 Ir/op, intercept +9.939
Ir/call**, so the gap is not `8 × cap` at all.

### 2.2 Attack 4 — the row's OWN control measures the same term, and it over-explains the gap on BOTH inputs

`ctl_r3_unchecked` is the shipped R3 with `win.get_unchecked` in place of every
window index; `panic_call_sites` **5 → 1** (`spellings.json`), i.e. the same four
sites the model is about.

| | `small.bin` | `large.bin` | slope | intercept |
|---|---:|---:|---:|---:|
| **checks term** `R3 v0_shipped − ctl_r3_unchecked` | **138.86404** | **354.47250** | **7.9855 Ir/op** | **+11.096 Ir/call** |
| **as % of the gap it explains** | **105.85 %** | **105.56 %** | | |
| **R4's own excess** `ctl_r3_unchecked − R4 v0_shipped` | **−7.67656** | **−18.67860** | −0.4075 | −1.157 |

The decomposition closes exactly on both inputs:
`138.86404 + (−7.67656) = 131.18748`; `354.47250 + (−18.67860) = 335.79390`.

⛔⛔ **SO THE `97.6 %` IS TWO ERRORS CANCELLING.** The static `128.00`
**under**-states the directly measured checks term by **10.86 Ir/call (7.8 %)**,
and the gap **under**-states the same term by **7.68 Ir/call** because R4 carries
a second, opposite-signed term. The two are close in size and opposite in sign, so
the ratio lands near 100 % **on `small.bin`**. On `large.bin` the same two errors
are 10.47 and 18.68 and the ratio lands at 102.4 %.

⭐⭐ **AND THE SECOND TERM IS NOT A ROUNDING RESIDUE — IT IS A SIGN REVERSAL THE
FINDING NEVER STATES: `ctl_r3_unchecked` is CHEAPER than the shipped R4 on both
inputs** (1946.174 vs 1953.850 on `small.bin`; 5245.999 vs 5264.678 on
`large.bin`). The R3 rung with its window checks removed beats the unsafe rung.

✅ **WHAT SURVIVES, AND IT IS THE BETTER HALF.** The two-input slope of the
**direct control** is **7.9855 Ir/op against a predicted 8.00 — 0.18 % — and
that is a genuine two-input confirmation that eight instructions execute per op.**
The mechanism sentence (*four `cmp`/`je` pairs, in the hot loop*) is right; a
hoisted check would give a slope near zero. What is wrong is (a) the **+11.1
Ir/call fixed per-call term** the model omits, and (b) checking the model against
the **R3−R4 gap** instead of against the control that isolates the term.

### 2.3 Attack 3 — the two nulls, and the two directions DO NOT agree

| direction | `small.bin` | `large.bin` | slope |
|---|---:|---:|---:|
| take the checks **out of R3** (`ctl_r3_unchecked`) | 138.86404 | 354.47250 | **7.9855 Ir/op** |
| put the checks **back into R4** (`r4_oprec_checked`) | 151.81072 | 387.00120 | **8.7108 Ir/op** |

⛔ **8.7108 / 7.9855 = 1.0908 — a 9.1 % asymmetry.** Adding the four checks to R4
costs 9.1 % more per op than removing them from R3 saves. **The term is not
isolated**, which is exactly what §2 attack 3 predicted.
⓵ The `+7.769824 %` I re-derived to the digit from `r4_oprec_checked` vs
`R4 v0_shipped` on **`small.bin`, A1**; on **`large.bin`** the same variant is
**`+7.350900 %`**. The row does label the input; the RECAP entry does not always.
✅ The other null is clean: `r3_head_slice` is byte-identical to `R3 v0_shipped`
(`kernel_digest 4664d8975683`, same Ir on both inputs, `panic_call_sites` 5 = 5).

### 2.4 ⭐ THE `0.82 %` HEADLINE — **UPHELD, AND IT GETS BIGGER ON THE SECOND INPUT**

| input | `r3_chunks_exact` | `ctl_r3_unchecked` | safe is cheaper by | magnitude |
|---|---:|---:|---:|---:|
| `small.bin`, A1, `O3/isolated` | 1930.23228 | 1946.17372 | **+0.8191 %** | **15.9414 Ir/call** |
| `large.bin`, A1, `O3/isolated` | 5192.67400 | 5245.99940 | **+1.0165 %** | **53.3254 Ir/call** |

**Magnitude floor.** `reproduces_shipped_record_scope` in `spellings.json` names
W1 R3 = 52,829,203; with `ir_per_call_small_wp = 2113.17568` that is
**n_iters = 25,000**. `.memory-php/03-numbers.md`'s item-99 run-to-run drift of
**14–28 Ir per run** is therefore **0.00056–0.00112 Ir/call**. The effect is
**~14,000×** the known drift, same sign on both inputs, magnitude rising.
▶ **The sign claim clears its floor decisively. UPHELD.**
⚠ State the comparison honestly: `ctl_r3_unchecked` is `side = CTL`,
`rung_candidate = false`, and `spellings.py --audit-only` marks it **"⚠ OUT BY
ENGLISH"**. That is correct and deliberate — it is a control, not a rung — but the
sentence must read *"beats a control built as the ceiling"*, not *"beats a rung"*.

---

## §3 ⛔⛔⛔ F103's WITNESS DECOMPOSITION — **IT IS A RESTATEMENT, NOT A MODEL, AND ITS ph53 NUMBER CONTRADICTS ITS OWN NAMED MECHANISM**

### 3.1 Attack 1 — `(slots) × (per-slot)` is `8.19 / 3` written as a product

Because `per-slot := total / slots` **by definition**, the ratio of per-slot terms
is forced:

```
(101.59 / 6) / (12.41 / 2)  =  (101.59 / 12.41) × (2 / 6)  =  8.186 / 3  =  2.7287
```

and the published figures are 16.93, 6.21, **2.73** — the identity to three
significant figures. ▶ **The decomposition carries exactly zero information beyond
the two totals and the two slot counts.** It is `_030`/F78's shape: an arithmetic
identity presented as a closure.
▶ **RULING: a restatement. It does not belong in `.memory-php/` as a model.** What
*is* a result is the refutation it replaced — *"the cost of a safety witness is
O(the number of slots)"* is false, 3× slots gives 8.19× cost. **Keep the
refutation; drop the product.**

### 3.2 ⛔⛔ Attack 2 — the declaration is NOT complete, and worse, **the number used excludes one of the two candidates it names**

F103 names ph53's witness as *"an **indexed array read** re-read on every consumer
iteration"* and prices it at **+101.59**. But `patterns-php/ph53-iface-tail-uninit/NOTES.md:582-591`
says where +101.59 comes from:

| | A1 Ir/call | above `r4_nowitness` |
|---|---:|---:|
| `controls/r4_nowitness.rs` | 888.082 | — |
| **`r4_bitmask` (register-resident witness)** | 989.670 | **+101.59** |
| R4 as shipped (`[bool; MAXD]`, memory-resident) | 1 116.947 | +228.87 |

> *"+101.6 Ir/call is the witness AS SUCH; the remaining +127.3 is the array being
> in MEMORY."*

⛔⛔ **+101.59 IS THE `r4_bitmask` ARM — the row's own word for it is
"register-resident", which is the SAME CLASS AS ph52's.** F103 uses a number from
which the *indexed-vs-register* term has already been subtracted, and then names
*indexed vs register* as one of the two candidate mechanisms the 2.73× might be.
**The data do not fail to separate the two candidates — the chosen number
EXCLUDES one of them.** The like-for-like shipped-vs-shipped ratio is
**228.87 / 12.41 = 18.4×**, not 8.19×.

⭐⭐ **AND THE THIRD CANDIDATE NEITHER SIDE NAMES, WHICH I MEASURED: "Ir per
kernel call" IS NOT A ROW-INVARIANT UNIT.** On `ph52` alone, changing only the
input moves the witness cost from **12.23816 Ir/call (`small.bin`, cap 16)** to
**28.92490 Ir/call (`large.bin`, cap 43)** — a **2.36×** move on one row, one
rung, one spelling (`.temp/php47/attrib.log`; A1 and W1 give the identical
difference). **That 2.36× is 79 % of the 3× the "slots" term is supposed to
explain.** Until both rows' figures are stated on inputs with comparable per-call
work, the 8.19× is partly a statement about input shape. The engineer's declared
limit (*read count* vs *indexed vs register*) is therefore **incomplete on a third
axis that is bigger than either.**

### 3.3 Attack 3 — `6 typical` is not a number, and it moves the answer

`patterns-php/ph52-concat-copy-uninit/NOTES.md:958` — slots *"up to 16, **6** on
15/16 measured windows"*; `ph53`'s NOTES:319 — *"one window in sixteen has
`n_decl == 0`"*. So on the cell the +101.59 was measured on, the **mean** slots
per call is `15 × 6 / 16 = 5.625`, not 6. Feeding that through:
`101.59 / 5.625 = 18.06` against `6.205`, i.e. **2.91×, not 2.73×** — a 6.6 % move
from one defensible choice of the same word. ▶ **Which confirms §3.1: the 2.73× is
whatever you divide by, because it is a division.**

### 3.4 Attack 4 — the `+12.41 Ir/call (+0.632 %)`: which input, which statistic

- The **+12.41 / +0.632 %** is **B1** (`marginal_ir_per_call`, the
  `probe_iters [100, 200]` difference), `small.bin`, `O3/isolated`, against
  `controls/r4_nowitness.rs` — `NOTES.md` §8g, table at `:768-773`.
- The **+0.622 %** is **W1**, same input, same level, same base — `NOTES.md` §8g.
- ⚠ **These are the SAME measurement expressed twice, not two methods.** §8g's own
  note says the B1 figure *"is bit-identical to the gate's own
  `marginal_ir_per_call`"* and that *"the control was driven through the same
  `probe_iters [100, 200]` difference **by hand**"*. A B1/W1 agreement on one run
  is an arithmetic consistency check, **not corroboration**.
- ⛔ **AND THE THIRD FAMILY DISAGREES.** From
  `controls/spellings.json` (`R4 v0_shipped` minus `CTL ctl_nowitness`), **both A1
  and W1 in that pipeline give `12.23816 Ir/call`, not `12.41`** — a **1.4 %**
  discrepancy on the numerator of the 8.19×. Both are `small.bin`, `O3/isolated`.
  **The row publishes two different numbers for one quantity in two files and
  neither cites the other.**

---

## §4 ⭐⭐ F97 — **UPHELD, NARROWED, AND NOW PROVED BY CONSTRUCTION RATHER THAN ARGUED**

Driver: **`.temp/php47/f97.py`**, output **`.temp/php47/f97.json`**.

### 4.1 (i) The two stages on BOTH rows — the second method F97 never had

| row | `_is_trusted` | twins | justified | 5-tcb-unsafe | 5c-twin |
|---|---|---:|---|---|---|
| `ph53-iface-tail-uninit` | 4 (`pool_get_unchecked`, `slot_read_unchecked`, `slot_set_unchecked`, `win_get_unchecked`) | **3** | `slot_read_unchecked` | 0 fails | 0 fails, **1 BLOCKED** |
| `ph52-concat-copy-uninit` | 2 (`slot_read_unchecked`, `win_get_unchecked`) | **1** | `slot_read_unchecked` | 0 fails | 0 fails, **1 BLOCKED** |
| `ph52` variant `r4_win_checked` | 1 (`slot_read_unchecked`) | **0** | `slot_read_unchecked` | 0 fails | ⛔ **HARD FAIL** |

⚠⚠ **THE NARROWING, AND IT MATTERS.** *As shipped*, **neither row hard-fails.**
The joint unsatisfiability is a property of the **item**, not of the pattern: the
`MaybeUninit` read can never have a twin, and the only escape is the
`twin_justifications` hatch, which costs a **BLOCKED row**. It becomes a
**pattern-level hard failure only when that item is the LAST trusted item**, which
is `ph52`'s `r4_win_checked`. ▶ **F97 should read *"jointly unsatisfiable for the
operation; a blocked row where another twinnable item exists, a hard failure where
it does not."*** The two rows with opposite trusted-base sizes are exactly what
shows this, and that is the second method the finding was owed.

### 4.2 (ii) "No safe exec route from `MaybeUninit<T>` to `T`" — **measured against the pinned vstd, `std_specs/` AND the inherent spelling**

`grep -an` over `~/tools/verus/vstd/std_specs/maybe_uninit.rs` gives the whole
surface: **exactly five `assume_specification` entries** —
`MaybeUninit::<T>::new` (:29), `::uninit` (:34), `::assume_init` (:39),
`::assume_init_ref` (:45), `::assume_init_mut` (:51) — all in the **inherent**
spelling, plus `spec fn mem_contents` (uninterp, :19) and
`open spec fn as_option` (:21). A repo-wide `grep -ran MaybeUninit` over the
pinned vstd finds nothing else offering a value out.

Then I **wrote the twin `check.py` demands** — same signature, same contract — and
let the toolchain rule:

| arm | result |
|---|---|
| **A** `*m.assume_init_ref()` without `unsafe` | ⛔ rustc **`error[E0133]`**: *call to unsafe function … is unsafe and requires unsafe function or block* |
| **B** `c.assume_init()` without `unsafe` | ⛔ rustc **`error[E0133]`**, same class |
| **C** `m.as_option().unwrap()` | ⛔ Verus: *cannot call function `…MaybeUninitAdditionalSpecFns::as_option` with **mode spec*** |
| **D** control: the same body **with** `unsafe` | ✅ **`3 verified, 0 errors`** |

▶ **The three vstd routes are all `unsafe fn`, the only other surface is
spec-mode, and the positive control proves the twin exists iff it carries
`unsafe`.** Combined with §1.1's reproduction (an `unsafe` token in a non-trusted
body is a `5-tcb-unsafe` hard failure, and `check.py:7200` fails a twin that is
itself `external`), **the pair is jointly unsatisfiable. UPHELD.**

⚠ **ONE HONEST NARROWING I OWE IT.** The pinned vstd *does* contain a safe exec
route from uninitialised memory to a value — `vstd::cell::PCell<V>` and
`vstd::cell::pcell_maybe_uninit`, which wrap `UnsafeCell<MaybeUninit<V>>` and
expose a **safe** API through a ghost `PointsTo` permission. It is unavailable
here only because **a twin must have the same signature**, and this one takes
`&MaybeUninit<Pr>`. ▶ **So the correct statement is *"no safe exec route for a
function whose parameter type is `&MaybeUninit<T>`"*, which is as much a fact
about the twin rule's same-signature requirement as about the type.** F97's
sweeping *"that is what the type MEANS"* is one step too strong.

### 4.3 (iii) F100's three arms — **TWO RE-RUN AND REPRODUCED, ONE I COULD NOT TEST**

| arm | my result | verdict |
|---|---|---|
| `ph53/controls/mu_ref.rs` | **`8 verified, 0 errors`** | ✅ reproduces item 79's `8/0` |
| `ph53/controls/mu_ref_cmp.rs` | ⛔ **`The verifier does not yet support the following Rust feature: dereferencing a pointer (here the dereference is implicit)`** | ✅ **the must-FIRE refusal FIRES, and the named feature matches item 79's *"the `&T → *const T` coercion"*** |
| `ph53/controls/mu_ref_exec.rs` | ⚠ **`verus_builtin crate was not imported`** | ⛔ **UNTESTED BY ME** — this is an **exec** control (`//! ../unsafe.rs with the slot representation changed`), not a Verus file; my `verus_run.py --crate-type=lib` invocation is simply wrong for it. It needs the harness build path. |
| `ph53/controls/mu_unwrapped.rs` | **`7 verified, 0 errors`** | ✅ matches F97's `7/0` |
| `ph53/controls/r4_nowitness.rs`, `ph52/controls/r4_nowitness.rs` | ⚠ same missing-prelude error | ⛔ **UNTESTED BY ME** — both are *"`unsafe.rs` with the witness deleted"*, i.e. **plain Rust R4 files**. The claim *"Verus refuses it"* means *substituting that body into `verus.rs` is refused*, which my arm did not do. |

▶ **So F100's promotion of F97 to a MEASURED FLOOR is re-run on 2 of 3 arms and
UNTESTED on the third.** Per the task: **F97 is `UPHELD-NARROWED` on the argument
half and the `mu_ref`/`mu_ref_cmp` half; `UNTESTED` on the `mu_ref_exec` cost arm.**

---

## §5 THE BOUNDED PASS — F104 · F102 · F96

### F104 — **UPHELD on the mechanism, NARROWED on the incentive**

(i) **Number re-derived, artefact named.** From `.temp/php47/repro_gate.json`
driving `check.py:7420-7426`: `r4_win_checked` and `r4_win_oprec` both carry
`external_body_items = 3` (`controls/spellings.json`) and **both hard-fail
`n_twins == 0`**, while the 4-item `v0_shipped` passes. ▶ **The gate mechanically
accepts the larger trusted base and refuses both smaller ones. The claim is
literally true of this row's option set.**
I also confirmed the other branch: no twin **and** no justification takes
`rep.fail("twin", …)` at `check.py:7178`. **There is no legal configuration.** ✅
F104's quotation of `check.py`'s own deleted-`MAX_TWIN_JUSTIFICATIONS` comment is
accurate.

(ii) **Is the claim scoped to what was measured?** The *perverse incentive* is
**real but did not bind on this row**. Evidence for real: two of three
smaller-TCB configurations are refused solely for having no twinnable item left.
Evidence for not binding: `ph52` kept `win_get_unchecked` for an **independent
fidelity reason it owed anyway** — `−7.12 %`, *"every window read in the C is an
unchecked array access"* — so no TCB was added to satisfy a stage, and
`r4_endpoint_note` says so in the artefact. ▶ **Publish it as *"the rule creates
the incentive; on the one row that reached it the row had an independent reason
not to act on it"*, not as *"the rule pressures rows to enlarge their TCB"*
unqualified.**

(iii) **UPHELD-NARROWED.**

### F102 — **the surviving half, stated exactly**

(i) **Number re-derived from a named, re-runnable artefact.**
`patterns-php/ph52-concat-copy-uninit/controls/tag_sweep.py` (`--selftest`: *15
assertions, 9 must-fire, 6 must-NOT-fire*, **PASS**; and it cross-checks against
`tag_sweep.c` — *"ok: tag_sweep.c and this file agree"*):

```
no-op                          244 / 256  (95.312 %)
TOTAL TEARING                   12 / 256  ( 4.688 %)  [3,4,5,7,8,9,131,132,133,135,136,137]
of which reach efree/free        8 / 256  ( 3.125 %)  [3,4,8,9,131,132,136,137]
```

(ii) **Scope.** ⛔ F102's *"five named cases out of a byte, widened by the mask"*
(= 10 of 256) is **REFUTED three ways**, as `_045` §3.1 says and as the committed
control's must-fire arm N1 asserts: **six** named cases not five (`IS_RESOURCE`
missing), **12** of 256 not ten, and F102's stated reason — *"`_zval_dtor` … has
**no** `case IS_NULL`"* — is false (`zend_variables.c:75` **is** `case IS_NULL:`).
✅ **What survives is the claim that mattered**: *the harm is conditional on the
garbage value and the condition is small and countable* — **now measured at
4.688 % of the byte, 3.125 % reaching the allocator**, which is a better answer
to *"why do uninitialised-read bugs survive for years"* than the wrong figure was.
✅ Also surviving: admission on the C, and *the defect is silent on a clean stack*
(the conclusion holds; F102's reason does not). ⚠ `0xbe` is ASan's **runtime
option default**, already on file as item 96.

(iii) **UPHELD-NARROWED** — the headline half survives with the number replaced;
the *"five named cases"* sentence is refuted and must not be quoted again.

### F96 — **UNREVIEWED, and I checked first whether `ph52` supplied the missing second method**

(i) I did **not** re-derive F96's numbers. F96 is `ph53`'s build record plus a
four-prediction ledger (R2, R3, R4, R5), verified by the manager from
`results-php/gate/ph53-iface-tail-uninit.json`.
(ii) **I checked the task's specific question — has `ph52` since supplied a second
method for any of the four predictions? NO, and the reason is structural.**
`ph52` is a **different row with a different kernel**; a prediction about `ph53`'s
R2/R3/R4/R5 cannot be re-tested on it. What `ph52` supplies is a second
**instance** of the *family-level* claims (F97/F98 recurrence), which F103 already
records and which I reviewed in §4 — not a second method for F96's ledger.
⓵ The two things I *did* touch that bear on `ph53` both came out clean:
`mu_unwrapped.rs` **7/0** and `mu_ref.rs` **8/0**, both re-run.
(iii) ⛔ **UNREVIEWED.** It has now sat through three rounds and the honest reason
is unchanged: no cheap second method exists. The cheapest route I can see is
re-running `ph53`'s own `controls/spellings.py` and re-deriving the R3/R4
predictions from its variant table; that is a task, not a paragraph.

---

## §6 ⛔⛔ COVERAGE TABLE — ONE VERDICT PER FINDING

| finding | verdict | one-line reason |
|---|---|---|
| **F96** | ⛔ **UNREVIEWED** | build record + 4-prediction ledger; `ph52` does **not** supply the second method (different row, different kernel); no cheap route found |
| **F97** | ⚠ **UPHELD-NARROWED** | jointly unsatisfiable **for the operation**, proved by construction (3 vstd routes all `unsafe fn`, `as_option` spec-mode, `unsafe` control verifies); narrowed to *blocked row* vs *hard fail*, and *"that is what the type MEANS"* is one step too strong — `vstd::cell::PCell` is a safe route at a different signature. F100's `mu_ref_exec` cost arm **UNTESTED by me** |
| **F102** | ⚠ **UPHELD-NARROWED** | the countability claim survives and is now **measured at 12/256 tearing, 8/256 reaching the allocator**; *"five named cases out of a byte"* is **refuted three ways** and must not be requoted |
| **F103** | ⛔ **REFUTED** (the decomposition) / ✅ upheld (the refutation it replaced) | `(slots) × (per-slot)` is `8.19 / 3` written as a product — an identity, zero information; and the ph53 number used (**+101.59**) is the **register-resident `r4_bitmask`** arm, which **excludes** one of the two candidate mechanisms F103 names |
| **F104** | ⚠ **UPHELD-NARROWED** | the `n_twins == 0` hard fail reproduces from `check.py` on both smaller-TCB variants, and both branches fail so there is no legal configuration; the **perverse incentive is real but did not bind** — `ph52` had an independent `−7.12 %` fidelity reason |
| **F105** | ⛔ **REFUTED** (the `97.6 %`) / ✅ **UPHELD** (the `0.82 %` and the 8-instructions-per-op mechanism) | `128.00 / 131.19` is a **two-error cancellation** and the residual **changes sign on `large.bin`** (102.4 %); the row's own control measures the term at **105.8 % / 105.6 %** of the gap; the two directions disagree by **9.1 %**. The `0.82 %` survives and grows to `1.02 %` on `large.bin`, ~14,000× the noise floor |
| **F106** | ✅ **UPHELD** (the finding) / ⛔ **REFUTED** (item 105's recommendation) | **Premise survives everything**: all three refusals reproduced from `check.py` itself; `33 → 34` confirmed **three independent ways** including a negative arm failing **at the vstd spec site**; the published axis **is** `tcb_items` and **does not count vstd**, census-backed, with `p06`'s `copy_from_slice` (TCB 6 → 5, byte-identical `-O3`) as an exact precedent; §1.3's reframing **holds**. ⛔ **But item 105's recommended option (b) DOES NOT EXIST** — `harness-php/gate.py`'s own header forbids it hosting a gate stage, it cannot make itself mandatory (`grep -c preflight` = `0 0 0`, re-run), and `root.py` rebinds **paths**, not verdicts. §1.7 |

---

## §7 ⛔ WHAT MUST COME **OUT** OF `.memory-php/`

I refuted one thing that sits under an `UNREVIEWED, MANAGER, 2026-09-13` banner.
**In those words: I REFUTE the following sentence and the manager must remove text
from the layer.**

**`.memory-php/02-ladder.md:774-778`**, inside the block banner'd at `:711`:

> `ph52`: **spelling** — four per-op window bounds checks, `8 instructions × 16 ops = 128.00 Ir/call` against a measured
> `131.19`, **97.6 % attributed**, with two independent nulls localising it (one
> variant **byte-identical** to the shipped rung; the mirror puts the same checks
> back into R4 at `+7.77 %`).

⛔ **REFUTED in the `97.6 % attributed` clause.** Suggested replacement, all
figures from `controls/spellings.json`, A1, `O3/isolated`:

> `ph52`: **spelling** — four per-op window bounds checks. Measured directly by
> the row's own `ctl_r3_unchecked` control at **138.86 Ir/call on `small.bin`** and
> **354.47 on `large.bin`**, a two-input slope of **7.99 instructions per op**
> against a predicted 8, plus a fixed **+11.1 Ir/call** the model omits. ⚠ **That
> term is 105.8 % / 105.6 % of the R3−R4 gap it is offered to explain**, because
> R4 carries an opposite-signed second term: the R3 rung with its window checks
> removed is **cheaper than the shipped R4** on both inputs. ⛔ **Do not quote
> `128.00 of 131.19 = 97.6 %`** — that ratio is two errors cancelling on
> `small.bin`; on `large.bin` the same construction gives **102.4 %** and the
> residual changes sign.

**`.memory-php/02-ladder.md:767-768`**, in the `0.82 %` entry:

> it isolates the bounds-check term *at the shipped spelling*, which is what makes
> that row's `128.00` of `131.19 Ir/call` attribution checkable

⚠ **The clause is fine as a statement about the CONTROL and wrong in its
citation.** The control is indeed what makes the term checkable — **and checking it
is what refutes the `128.00 of 131.19`.** Replace the trailing citation with
*"…which is what makes that row's bounds-check attribution checkable — and the
check refutes the `128.00 of 131.19` framing."*
✅ **The rest of that entry — the `0.82 %` itself, and *"`get_unchecked` is not a
ceiling on the safe side"* — is UPHELD and gets stronger: `1.02 %` on `large.bin`.**

⛔⛔ **AND ONE WITHDRAWAL OWED IN `RECAP_PHP.md`, NOT IN THE LAYER.**
`RECAP_PHP.md`'s open item **105** currently reads:

> *"⭐ **My recommendation is (b)**, on the grounds `CLAUDE.md`'s banner already
> gives — the php programme imports `harness/` and rebinds at run time precisely
> so it need not re-gate 33 patterns — but it is the user's call because it forks
> a rule, and I am not taking it unasked."*

⛔ **REFUTED (§1.7).** Option (b) is not available: `harness-php/gate.py`'s
committed header forbids it hosting a gate stage, no gate record could witness the
exemption, and `root.py` rebinds **paths**, not verdicts. **The question put to
the user must be (a) or (c), and the recommendation withdrawn.** ⓘ The same three
options are restated in item 105's own "original framing" column and in F104's
closing paragraph; both need the same correction.

⭐ **Nothing else in my scope is in `.memory-php/`.** I grepped: the F103
`(slots) × (per-slot)` decomposition is **not** in the layer (it is in
`RECAP_PHP.md` F103 only), so §3's refutation costs a RECAP edit, not a layer
removal. `.memory-php/03-numbers.md:70`'s `+101.59 of +228.87` is in the
**reviewed** part of that file (above the `:92` banner) and is **correct** — it is
F103's *use* of that number that is wrong, not the number.

⚠ **AND ONE THING THAT SHOULD BE ADDED RATHER THAN REMOVED.** If F106 lands,
`.memory-php/` should carry the sentence `.memory/04-verus.md` already implies and
nobody has written down for the php side: **the published trusted-surface axis is
the gate's own `tcb_items` (items AND lines), it deliberately does not count vstd,
and the accounting decision behind it is flagged PROVISIONAL in the PAT layer.**
Without that sentence F106's `4 → 3` reads as a claim about "the trusted base"
rather than about a named, bounded column.

---

## §8 ⭐ WHAT I AM UNSURE OF — 14 items

1. **§2 attack 2, the disassembly, IS NOT DONE.** I did not run `objdump` and
   count four `cmp`/`je` pairs in the hot loop. I substituted two weaker checks:
   the **two-input slope of 7.9855 Ir/op** on the direct control (which a hoisted
   check could not produce), and the static `kernel_insns` delta from
   `spellings.json` — `R3 v0_shipped` **412** → `ctl_r3_unchecked` **385**, i.e.
   **−27 static instructions**, consistent with 4×(`cmp`+`je`) = 8 in-loop plus
   four panic blocks. **Consistent is not the same as counted.** If you want the
   literal claim *"four `cmp %rdi,<stack slot>` / `je <panic>` pairs"* verified,
   it is still open.
2. I did **not** verify that the four panic sites deleted by `ctl_r3_unchecked`
   are the *same four* as those added by `r4_oprec_checked`. `panic_call_sites`
   gives ±4 on both, but `ctl_r3_unchecked` changes `rd32` **and** the op reads
   while `r4_oprec_checked` changes only the op reads (`spellings.py:709-712`).
   **The 9.1 % asymmetry in §2.3 could be partly this rather than a real
   directional effect.** I state the asymmetry; I do not fully explain it.
3. The **+11.1 Ir/call** intercept in §2.2 is a two-point fit. Two points cannot
   distinguish an affine model from a curved one. It is a residual with a number,
   not a mechanism.
4. §3.2's claim that `+101.59` is the `r4_bitmask` arm rests on reading
   `ph53/NOTES.md:582-591`. I did **not** re-run `ph53`'s `r4_bitmask` control.
   If that table is itself wrong, my refutation of F103's mechanism falls with it.
5. I did not re-measure `ph53`'s slot count on the `+101.59` cell. My 5.625 is
   arithmetic over two sentences (`ph52/NOTES.md:958`, `ph53/NOTES.md:319`), not
   an instrumented count.
6. The `12.23816` vs `12.41` discrepancy in §3.4: I believe it is A1/W1-in-one-run
   against B1-from-a-`probe_iters` difference, but I did **not** run B1 myself, so
   I cannot say which is right — only that the row publishes two.
7. §1.4's drafted condition is **untested**. I wrote no code for it and ran
   nothing. Conditions 3 and 5 in particular I believe are necessary and have not
   demonstrated.
8. ✅ **CLOSED — this was going to be my largest gap and I closed it, see §1.7.**
   `harness-php/` **cannot** host the condition. What I did **not** do is measure
   the blast radius of option (a): I did not check how many of the 33 PAT
   patterns carry an `unsafe` token that the narrowed rule would newly exempt, so
   **I cannot say whether a 33-pattern re-gate would change any PAT verdict.**
   `.memory/04-verus.md` says `get_unchecked`, `copy_nonoverlapping`, `as_ptr`,
   `as_mut_ptr` and `<*const T>::add` are all `is not supported` at the pinned
   vstd, which suggests the exempt set on the PAT side is **small or empty** —
   but that is an inference from a different census, not a measurement.
9. My `r4_win_checked` reconstruction in `repro_gate.py` drops the twin item by
   regex when its subject is deleted. `spellings.py` does it by a substitution
   list (`_V_WIN_DROP`). The `gate_facts` I got (`trusted: ['slot_read_unchecked']`,
   `twins: []`, `n_twins: 0`) match `spellings.json` exactly, so I think the
   reconstruction is faithful — but it is *a* reconstruction.
10. I did not verify that `Pr: Copy` is what makes §1.4's contract-implication
    argument work in Verus's semantics rather than in mine. Arm B verifying is my
    evidence, and it is evidence about this type, not a general rule.
11. `mu_ref_exec.rs`, `ph53/r4_nowitness.rs` and `ph52/r4_nowitness.rs` are
    **UNTESTED by me** (§4.3). I reported the invocation error rather than
    dressing it as a result, but the F100 "measured floor" is therefore only
    two-thirds re-run.
12. I read `spec.md`'s `slb-contract` block and `verus.rs`'s trusted region, but
    **not** `ph52`'s 101 KB `spec.md` in full, nor its 75 KB `NOTES.md` in full.
    A contradiction in a part I did not read would not have been caught.
13. I did not run the committed checkers `boxcheck.py`, `citecheck.py`,
    `coverage.py`, `quota.py`, `fixsurvey.py`, `preimage_screen.py`,
    `php_null.py`, `task_cost.py` or `width.py`, nor `asan_fill_byte.c`. The task
    listed them as reading; I relied only on `spellings.py --audit-only` and
    `tag_sweep.py --selftest`, and I ran both. **If a defect lives in one of the
    others, this round did not look.**
14. I read `.memory-php/02-ladder.md`'s banner'd block and `03-numbers.md`'s, but
    only grepped `04-process.md`'s. If a refuted claim of mine is restated there
    in different words, I would have missed it. ⚠ **A line-based grep cannot find
    a phrase that wraps** — §6 trap 1 — and my `.memory-php/` sweep was grep-based
    for everything except `02-ladder.md:711-791`.

---

## §9 WHERE MY DEPTH RAN OUT

**§§1–4 are complete to the bar the task set.** §5's bounded pass is complete for
**F104** and **F102** and **honestly incomplete for F96**, which I am returning as
`UNREVIEWED` with the specific check the task asked for (has `ph52` supplied the
second method? **no, and structurally it cannot**) done rather than skipped.

**I stopped after §5**, plus one out-of-order excursion I judged worth the depth:
reading `harness-php/gate.py` and `root.py` to test whether option (b) exists.
It does not (§1.7), and that is the round's largest single result, so I am glad I
did not stop one step earlier.

**The three things I would do next, in order:**

1. ⭐⭐ **Price option (a)'s blast radius on the PAT side** — how many of the 33
   patterns carry an `unsafe` token the narrowed rule would newly exempt, and
   whether any PAT verdict moves. §8 item 8. **This is now the only unpriced side
   of the user's decision.**
2. **The objdump count** (§8 item 1) and the panic-site identity (§8 item 2),
   which together would close §2's last gap.
3. **F96**, which needs `ph53`'s own `controls/spellings.py` re-run to give its
   four-prediction ledger a second method. That is a task, not a paragraph.

---

## §10 SCRATCH

`.temp/php47/` holds only generators and evidence — no binaries, no `.o`, no
`.bin`:

| file | what it is |
|---|---|
| `repro_gate.py` / `repro_gate.json` | §1.1 — the three refusals from `check.py` itself |
| `verus_probe.py` / `verus_probe.json` | §1.2 — the four Verus arms incl. the decisive negative |
| `attrib.py` / `attrib.log` | §2, §3.2 — the two-input arithmetic |
| `f97.py` / `f97.json` | §4 — two rows through both stages, four twin attempts, F100's arms |
| `vwork/*.rs`, `f97work/*.rs` | the sources those two scripts generate; each is rebuilt by its script |

**Every number in this report that came from `.temp/` is also written out in the
report itself** — F99's defect, not reproduced.
