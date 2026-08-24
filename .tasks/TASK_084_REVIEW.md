# TASK_084_REVIEW — attack the gate work, the manager's two calls, and two inherited claims

**Role: research reviewer.** Adversarial by design. **A review that says "looks
good" without having tried to break something is a failed review.** You do not
fix; you report. Read `.tasks/PROTOCOL.md` first (Reviewer checklist, Severity),
then `.tasks/TASK_084.md` (what was asked), then `.tasks/TASK_084_REPORT.md`
(what came back), then `.memory/05-layout.md`'s `vparse.parse()` section.

Scratch in `.temp/r84/` — free, I checked.

> **§0 is filled in at launch with what the engineer actually delivered and
> where it departed from the spec. Everything below §0 is fixed and was written
> before the report arrived, deliberately — so the attacks are not shaped by the
> answer.**

---

## §0 — what came back

✅ **`.tasks/TASK_084_REPORT.md` now exists**; the forward citation noted here
before launch is satisfied. **All eight deliverables done, every acceptance limb
reported passing, sweep 45 min, 21 `PASS` + p01 `PASS-WITH-BLOCKED-ROWS`, 0
failures, `contract_sha256` moved `[]`, `0 STALE`.** Read the report; the
headlines you must attack:

- **D4 took route (b)**, a separate `axioms` column — **the manager's lean.**
  §2 M2 is therefore live and is *your* job, not a formality.
- **D5 took disclose-and-pin** (`TCB_SRC = "verus.rs"`, mirroring `R5_PAIR`)
  **plus a footnote computed from the records every run**, and **declined a gate
  check** under PROTOCOL rule 5. §2 M1 asks whether that closes the complaint.
- **B3's key convention is the path RELATIVE TO THE REPO ROOT** —
  `verus.axioms["common/driver.rs"]`. §4 asks whether it is unambiguous and
  survives two patterns including the same file.
- ⚠ **Two contradictions of the manager, both inside acceptance limbs, both
  landed:** **#236** the published TCB total is **90, not 92** (92 is the
  all-sources sum; four documents had the label wrong), and **#237** D7's edit
  **does not** move `contract_sha256` — the `identity` row is **203 characters
  outside the fence**, so the cost is a gate re-run. ⚠ **Re-derive both. They
  are now in `.memory/05-layout.md` as authoritative and a wrong one there is
  expensive.**
- ⚠ **The engineer reports one thing it fixed that reads like a near-miss:**
  `trait_spans` copied `impl_spans`' guard and **missed every attributed trait —
  the entire target of B1** — caught by a probe, not by reading. **Ask what else
  that guard shape touches.**
- ✅ **Already closed by the manager, do not re-report:** RECAP "Owed" 23, the
  three content-stale `results/tables/*.md` the engineer flagged as adjacent
  (`report.py p09 p12 p27`, 9+/10−, all three now cite their record's hash).

---

## 1. ⚠⚠ THE META-ATTACK, AND IT IS THE POINT OF THIS REVIEW

`TASK_084` exists because `TASK_082` shipped a fix whose acceptance test the
manager verified by regenerating `results/synthesis.md`, getting a
**byte-identical** file, and quoting that as *"the change moved no published
number."* **It is byte-identical because `synthesize.py` reads `tcb_items` and
the word "axiom" appears ZERO times in `synthesis/`.** The check could not have
failed.

So, for **every** limb of `TASK_084`'s acceptance test:

> **Ask what would have made this limb FAIL, and then make it fail.**

⚠ **Limb 3 is the one to go at.** It requires four planted axioms — one per
route — each caught, **and the published column to MOVE**. Verify by planting
your own, in `.temp/r84/`, **not by reading the engineer's transcript**. If a
plant does not move `results/synthesis.md`, that is a **blocker** and it is the
same defect this whole task exists to close.

⚠ **A green gate is evidence about the gate.** Reviews here have found real
defects past a fully green run repeatedly, including in the manager's own
tooling and in `.memory/` text written one task earlier.

---

## 2. ⚠⚠ TWO MANAGER CALLS — PROTOCOL RULE 3 SAYS A DIFFERENT AGENT MUST ATTACK THESE

**The manager never clears its own design.** Both of these are the manager's and
neither has been attacked.

### M1 — the "fifth route", which the manager found and nobody has checked

`synthesis/synthesize.py` reads `vb = (g.get("verus") or {}).get("verus.rs")` —
a **hardcoded single key, with no comment**. **p01 pins two Verus sources**:

```
safe_naive_verus.rs   7 verified, 0 errors, tcb ['load_input','emit'],            5 lines
verus.rs              7 verified, 0 errors, tcb ['get_unchecked','load_input','emit'], 6 lines
```

so the published p01 row reports 7 / 3 / 6 and silently drops a second verified
source with 7 more obligations, 2 more items and 5 more lines.

⚠ **The manager explicitly did NOT ask for these to be summed** — `safe_naive_verus.rs`
proves the **R2** rung panic-free, and its TCB is not R5's TCB, so summing would
publish a number describing no rung. **The claimed defect is that the choice is
SILENT.** ⚠ **There is precedent one paragraph above the offending line**: the
same file documents that *"p01 ships two `-O3` identity pairs and an earlier
version of this file took whichever came first (TASK_075_REVIEW m6)"* and fixed
it by pinning `R5_PAIR`.

**Attack it:** Is the manager's framing right? Is *"disclose and pin"* the right
repair, or is the whole `verus.rs` convention load-bearing somewhere else such
that pinning it is a no-op or a hazard? **Is p01 really the only pattern with two
— re-derive that, do not trust it.** And: would a *third* pattern growing a
second Verus source tomorrow be caught by anything at all after this task?

### M2 — the manager's design lean on how an axiom should appear in the published column

The manager leaned **(b) a separate `axioms` column**, over **(a) folding axioms
into `tcb_items`**, on the ground that (a) *"equates a 7-line `external_body`
wrapper whose `ensures` a reviewer has read against real Rust semantics with a
zero-line hand-written axiom that is strictly stronger."*

⚠ **The manager also stated the counter-argument and did not resolve it:** a
column reading `0` in all 22 rows is real estate spent on a hypothetical, and
**the TCB *total* — the number a reader actually quotes — is still an undercount
under (b) unless the prose says so.**

**Attack it with the regenerated table in front of you.** Whichever the engineer
implemented, say whether it is right, and **specifically: does a reader of
`results/synthesis.md` who quotes the TCB total get a true number under the
shipped design?** If not, that is a **major** regardless of which option was
chosen.

---

## 3. TWO CLAIMS INHERITED FROM `TASK_085`, WHICH COULD NOT RUN THE GATE

`TASK_085` (the p15 probe) ran concurrently and was **barred from `check.py`**.
Two of its findings are therefore **code reads of `git show HEAD:harness/check.py`,
not executed gates**, and it said so itself. **You have the gate. Settle them.**

### G1 — is `identity: differ` really admissible?

The probe's reading: `check_identity` enforces a **floor only** (`got_i <
want_i` is the sole failure path) and `rep.note`s when a pattern pins nothing;
`asm.IDENTITY_LEVELS = ["differ", "counts", "norel", "exact"]`, so **`differ` is
a legal pin**. What makes an identity measurement mandatory is `check_miri`,
transitively — no pin naming the R4/R5 pair is a hard failure at stage 8. And
`check_miri` treats R4 ≠ R5 as **supported**, appending *"R4 and R5 differ at O3
…, so R4 does not inherit R5's discharged obligations at all"* to
`why_required` — **a reason Miri is REQUIRED, not a failure.**

⚠ **This refuted the manager**, whose claim was *"none allows R4 ≠ R5"* — true
of the `spec.md` files, false about the gate. **Run it**: take a pattern into
`.temp/r84/`, pin `identity: differ`, and put it through the gate. Does it pass?
**If the probe is wrong, the p15 design space closes again and that matters.**

### G2 — does `_scan_unsafe_sites` really forbid VERIFIED unsafe, end-to-end?

The probe's reading: every `unsafe` token in a pinned Verus source must sit
inside a `#[verifier::external_body]` item or it is a hard `tcb-unsafe` failure.
Census: **47 `unsafe` tokens across 22 `patterns/*/verus.rs`, all inside
`external_body`, zero outside.** ⚠ **Correction already landed by
`TASK_085_REVIEW`: `_is_trusted` requires `external_body` AND (`ensures` **or**
`unsafe` in the body), not `external_body` alone** — the probe's report states it
the loose way. Same conclusion; recorded so you do not re-derive it.

⚠⚠ **AND `TASK_085_REVIEW` ASKED FOR ONE SPECIFIC THING FROM YOU, BY NAME:
exercise `check_miri`'s `if not why_required` branch.** Its blocker 1 lives
there and **a code read is not enough for a PRINTED sentence.** The claim: a
pattern that merely *calls* a vstd `assume_specification` declares nothing, so
`_trusted_items` = 0 and `_axiom_items` = 0, and the gate then **prints** *"this
pattern has NO trusted item and NO hand-written axiom, so there is no trusted
`ensures` whose incompleteness Miri would have to backstop — Miri not
required."* **Make that sentence print over a proof that rests on a vstd axiom,
or show that it cannot.** This is **RECAP "Owed" 0's sixth route** and it is the
widest one found so far.

**The probe could not demonstrate the failure end-to-end** because that needs
writing a `.rs` into a pattern directory. **You can — in a `.temp/r84/` copy.**
Put an `unsafe` block whose precondition Verus **discharges from a verified
postcondition** into a verified fn, and report what the gate says.

⚠ **This is not academic.** If it is right, it means p15 — and any future row
whose unsafe operation vstd specs — cannot ship an R5 whose unsafe operation is
*proved* rather than *trusted*. ✅ **Clean negative to verify:** `grep -rn
"get_unchecked" ~/tools/verus/vstd/` → **0 hits**, so all 47 existing wrappers
were unavoidable and the rule has cost the project nothing to date.

---

## 4. The ordinary attacks

- **Over-breadth.** Each of B1/B2/B3 widens a matcher. **Does any widening
  refuse a legal construct?** ⚠ **p36 is the live negative control**: it declares
  body-less `fn apply` / `spec fn spec_apply` in a trait and defines them in the
  impl, and the *originally prescribed* repair for this item would have turned it
  **red in six stages**. B1 matches `external_trait_specification` traits, whose
  methods are *also* body-less. **Confirm p36 is green and confirm you understand
  why.**
- **Under-breadth.** The engineer fixed the forms the manager named. **Is there a
  sixth?** `grep` the pinned vstd for attribute spellings and for
  `broadcast group` / `uninterp` / `assume_specification` variants. A form that
  exists in vstd and not in the matcher is the same hole again.
- **B3's key convention.** An axiom in a `#[path]`-included subdir needs a
  declaration key. Is the chosen convention unambiguous, and does it survive two
  patterns including the same shared file?
- **D6 — p17 `NOTES.md` §10b.** Does the replacement law
  `R3ship − R4 = 11 + 7·nsuf − 2·#{i : s_i ≡ 0 (mod 4)}` appear correctly, is
  `6.50/request` gone, and is the **mechanism** now the inner byte fold rather
  than a 4×-unrolled table walk? **Spot-check one prediction yourself.**
- **D7 — `p01/spec.md`.** Only p01's `contract_sha256` should move.
  `git status --porcelain patterns/` is the check. **And per PROTOCOL rule 6,
  verify the engineer's disclosure against `git show`** — a *false* disclosure is
  worse than the stale thing it describes, because a disclosure is what a
  reviewer trusts **instead of** re-checking.
- **Staleness.** `harness/measure.py --check-stale` must report **0 STALE**.
  `check.py`/`vparse.py` are gate-hashed; `build.py`/`asm.py` are
  **measurement**-hashed and touching either costs a 43-minute re-measure of 17
  records. **Confirm neither was touched.**
- **Citations.** ⚠ The manager's `TASK_084.md` cites `check.py:NNNN` line
  numbers throughout, violating `.memory/02-bench-rules.md`'s *"Line citations
  into `check.py` decay. Cite the FUNCTION."* — **5 of 9 in the authoritative
  layer pointed at the wrong code when last audited.** Did that habit propagate
  into anything the engineer wrote that will outlive the task? Report it if so.

---

## 5. What I want back

PROTOCOL's report format, severity-ranked, each finding with a **concrete
failure scenario**. **3 real blockers beat 20 nitpicks — do not pad.**

⚠ **PROTOCOL rule 6: give me your CLEAN NEGATIVES BY NAME** — attacks you ran
that did not land. They are worth as much as findings and stop the next agent
re-running them.

---

## 6. Constraints

- `.temp/r84/` only. No `/tmp`. Keep the generator, delete the artefact.
- **Notes in `.temp/r84/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only. Report durable facts; do not write them.
- **You review, you do not fix.**
- `timeout <N> <cmd>` on anything long — a full gate sweep is **~45 minutes**
  (2593 s and 2672 s measured), not the 13 min an older note claimed. Never
  `pkill`/`killall`.
- Do not bump the Verus/vstd pin. Do not edit `pilot/`.

---

⚠ **PROTOCOL rule 2's running count is 237.** **M1 and M2 are the manager's own
and rule 3 exists because designer-validates-own-design is the configuration
this project keeps finding defects in.** Contradict either with a measurement and
say so plainly. Carry the count forward incremented by what you find.
