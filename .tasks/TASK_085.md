# TASK_085 — `p15`'s contract shape: settle it with runs, before a single cell is built

**Role: research engineer (probe).** You are **not** building `p15`. You are
answering the three questions that decide whether `p15` can be built at all, and
returning a recommendation the manager can turn into a build task or a refusal.

Read `.tasks/PROTOCOL.md` first, then this file, then **`RECAP.md` "Owed" 25**
(the manager's analysis, which you are here to attack), then
`.tasks/TASK_083_REVIEW_REPORT.md` from the line `## \`p15\` — the probes` to the
end of that section, then `.memory/04-verus.md` and
`.memory/02-bench-rules.md`'s section *"The precondition must be structural. The
attack must be data."*

---

## ⚠⚠ 0. ANOTHER AGENT IS WORKING RIGHT NOW. STAY IN `.temp/t85/`.

`TASK_084` is live and is **editing `harness/vparse.py` and `harness/check.py`
and regenerating `results/synthesis.md`.** The one-agent-at-a-time rule is being
relaxed for this task **only** because it touches neither measurement nor gate
records. Therefore, absolutely:

- **Do NOT run `harness/check.py`.** It would read half-edited harness sources
  and tell you nothing true.
- **Do NOT run `harness/measure.py`.**
- **Do NOT write anything outside `.temp/t85/`.** Not `patterns/`, not
  `harness/`, not `results/`, not `.memory/`, not `common/`.
- Reading any of those is fine and expected.
- `./verus_run.py <file.rs>` in **single-file mode is safe to run concurrently**
  — it builds in a `tempfile.mkdtemp()` scratch dir per invocation. **Do not use
  `--cargo` mode**, which shares `target/`.
- If you need a number from the gate, **report that you need it**; do not take it.

`.temp/t85/` is free — I checked. ⚠ **`.temp/pNN` in this tree is ambiguous
between pattern NN and task NN**, so use `t85`, and `ls` any scratch path before
you name it.

---

## 1. Why this task exists

`TASK_083_REVIEW` selected `p15` (UTF-8 validation + decode) with three probes
passed and a **named kill-risk**: R5 must discharge `valid_utf8` over bytes read
from a file, which needs a *verified* validator, and the reviewer wrote *"I did
not build it and I do not know it closes."*

Then, writing the build task, **the manager found that the contract shape the
review prescribed cannot ship as written** — see `RECAP.md` "Owed" 25. That
analysis is **an argument from two committed rules with nothing run**, which is
precisely the shape of manager reasoning this project has refuted twice at the
cost of a task each. **You are here to run it.**

⚠ **This project's single highest-value behaviour is an agent contradicting the
manager with a measurement. It has happened 235 times and the agent has been
right every time.** Treat everything in §2 as a hypothesis with a command
attached.

---

## 2. The three questions, each with the claim to attack

### Q1 — is `requires valid_utf8(b@)` on the kernel really inadmissible?

**The manager's claim:** yes, and it is not close.
`.memory/02-bench-rules.md`'s *"The precondition must be structural. The attack
must be data"* was settled at TASK_003_REVIEW and names this failure: *"a
precondition narrow enough to make the proof easy is a precondition no caller
can discharge."* p15's adversarial inputs are invalid UTF-8 **by construction**,
so such a `requires` assumes the attack away — the pilot's `requires n < 1000`
again.

**How to attack it:** this one is a *rule reading*, not a measurement, so attack
it by counter-example from the tree. **Does any shipped pattern carry a
`requires` that an adversarial input violates?** If one does, the rule is not
what the manager thinks it is and the whole of "Owed" 25 weakens. Check the
patterns whose adversarial input is a value the kernel must handle — p02, p16,
p17, p13, p18 are the obvious ones. **Report what you find either way; a clean
negative here is worth as much as a hit** (PROTOCOL rule 6).

### Q2 — does the `identity` pin really force R4 to validate?

**The manager's claim:** yes. Measured across `results/gate/*.json`, **21 of 22
patterns pin `unsafe vs verus` at `exact`** and p36 pins `norel`; **none allows
R4 ≠ R5.** So R4's exec code *is* R5's, R5 must verify without an
attack-excluding `requires` (Q1), and therefore **R4 must be provably
memory-safe on invalid UTF-8** and may not hand unvalidated bytes to
`str::from_utf8_unchecked`. An R4 that "assumes and is UB" has **no verifying
twin and is therefore not a rung** (finding 14).

**How to attack it:** ⚠ **The interesting question is whether `identity` is
MANDATORY or merely universal-so-far.** Read the gate: does a pattern have to
pin `identity` at all, and does anything force the `unsafe vs verus` pair
specifically? **Cite the function, not a line number** — `check.py:NNNN`
citations decay and 5 of 9 in the authoritative layer were pointing at the wrong
code when last audited (`.memory/02-bench-rules.md`, *"Line citations into
`check.py` decay. Cite the FUNCTION."*). ⚠ **Note the manager's own TASK_084
file violates that convention throughout; do not copy the habit from it.**

⚠ **If `identity` turns out to be optional, say so loudly** — it would mean p15
could ship an R4 that genuinely assumes, with R5 as a *different* program, and
that reopens the whole design. It would also be a project-wide finding.

### Q3 — ⚠⚠ THE KILL-RISK. Does a verified UTF-8 validator close at the pin?

**This is the question worth the most and the one nobody has run.**

`vstd/utf8.rs` ships the vocabulary: `valid_utf8` (a recursive `open spec fn`
over `Seq<u8>` with `decreases bytes.len()`), `decode_utf8`,
`valid_first_scalar`, `pop_first_scalar`, `length_of_last_scalar`,
`is_continuation_byte`. `vstd/string.rs` ships
`assume_specification[ str::from_utf8_unchecked ](v: &[u8]) -> (res: &str)
requires valid_utf8(v@)`.

**Build, in `.temp/t85/`, an exec function**

```rust
fn is_valid_utf8(b: &[u8]) -> (res: bool)
    ensures res == valid_utf8(b@)
```

**and report `N verified, M errors` verbatim.** It is a loop over the byte
sequence, `pop_first_scalar` in the `decreases`, and the loop invariant is the
hard part. **Budget most of your session for this.**

⚠ **`ensures res == valid_utf8(b@)` is the bar, and a one-directional
`ensures res ==> valid_utf8(b@)` is NOT the same thing** — the reverse
direction is what makes the validator *complete*, i.e. what stops it rejecting
everything and trivially satisfying its own contract. **If you can only get one
direction, that is a real and reportable result, but say which direction and do
not present it as the bar met.** A validator that verifies `true ==> anything`
is the vacuity this project's reviewers look for first.

⚠⚠ **IF IT STALLS, IT STALLS — REPORT THAT AND STOP. DO NOT REACH FOR
`assume_specification`, `external_body`, `assume(...)` OR `admit(...)`.** A
hand-written axiom saying *"these bytes are valid UTF-8"* is **the strongest
possible false axiom for this pattern**, and — this is the point —
`TASK_083_REVIEW` established that **the published TCB column cannot currently
see one**. `TASK_084` is fixing exactly that hole **as you work**. Writing the
axiom would be walking through the door the other live task is closing. **A
measured "it does not close" is a GOOD deliverable here and licenses a refusal.**

---

## 3. If Q3 closes — price the three shapes

Only if you have a verified validator, and only with time left. Marginal `Ir`
per kernel call, `-O3`, isolated, `n_iters` differencing (the recipe is
`patterns/p17-http-range/NOTES.md` §2; TASK_083_REVIEW's `cost_p15.rs` under
`.temp/r83/b/` is a working example — **read it, it is the recipe already
applied to this exact question**). Buffer built at run time from `argv` so
nothing constant-folds. Two alphabets: **all-ASCII** and **2–3-byte scalars**.

| shape | R3 | R4 = R5 |
|---|---|---|
| **A** | `core::str::from_utf8` + decode | **your verified validator** + `from_utf8_unchecked` + decode |
| **B** | same | **structural-only** check (continuation shape, no overlong/surrogate rejection) + `from_utf8_unchecked` |

⚠ **The manager's prediction for A, stated so you can falsify it: R4 comes out
DEARER than R3**, because std's `from_utf8` has a word-at-a-time ASCII fast path
a hand-written verified validator is unlikely to match. **If that holds it is
not a consolation prize — it is p11's result a fourth time** (*the safe class
reaches a library the unsafe class cannot*). **If it does not hold, that is
better still and I want the number.**

⚠ **For B, the manager's guess is that `valid_utf8` is NOT derivable from a
structural-only check** (overlong encodings pass the continuation-shape test but
are not valid UTF-8), so R5 would have to add the checks back and the identity
pin breaks again. **This is a guess. One Verus run settles it** — and if B
closes, B is the more interesting pattern, because the obligation would then be
priced against exactly the checks a real decoder omits.

⚠ **Whatever you measure, the axis is a SLOPE in the fraction of non-ASCII
bytes, not a level** — declared in advance by probe 3 and by
`.memory/03-measurement.md`'s rule that a published `0.00` must name its axis and
`Ir` convention up front. And **name the inline mode at every figure**; p10
fitted both and the regressors swapped.

---

## 4. What to return

A recommendation of **exactly one** of:

- **(A)** build p15 with a verified validator in R4/R5 — with the validator's
  verification output and the priced table;
- **(B)** build p15 with a structural-only R4 — same evidence;
- **(C)** ⚠ **REFUSE the row**, with the measurement that licenses the refusal.

**(C) is a legitimate and fully acceptable outcome.** Three rows have been
refused in a row (p48, p31, p45) and **all three refusals were the right call**;
each left reusable measurements behind. **Do not build a weak pattern to avoid a
fourth.** ⚠ **But note the asymmetry: those three were refused because their
justification was false. p15's probes all PASSED** — so a refusal here would be
a *different and stronger* kind, namely *"the `identity` pin makes the
interesting unsafe rung inadmissible"*, which is finding 14's
R4-chained-to-the-prover result with p11 and p16 as prior instances. **Say which
kind you are recommending.**

⚠ **And say what survives under all three.** The manager believes p15's
**row-2 adversarial cell** does: truncated lead byte, `rustc -O`, the binary
**prints nothing and exits 0** because `unreachable_unchecked` inside
`next_code_point` let LLVM delete the program's own `println!`, with **no bounds
violation anywhere**; Miri catches it, ASan has nothing to catch. **Re-run it
and confirm or refute** — TASK_083_REVIEW measured it and it is the single most
unusual harm row anyone has produced here. ⚠ **Row 1 is the honest weakness:**
an invalid *continuation* byte is a silent wrong answer **Miri does not catch**,
which is p18's harm, and p18's harm is what killed p45.

---

## 5. Constraints

- **`.temp/t85/` only.** No `/tmp`. Keep the generator, delete the artefact:
  the `.rs`/`.c` source, the `.py` probe, the `.json`/`.log` are evidence and
  stay; binaries and `.o` go once your runs are done. If a blob has no script
  that rebuilds it, write one.
- **Notes in `.temp/t85/NOTES.md` as you go.** Agents here die to transient API
  errors; the ones who kept incremental notes lost nothing.
- **No `git add` / `git commit`.** Read-only git is fine.
- `.memory/` is manager-only — put durable facts in your report.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- Do not bump the Verus/vstd pin. Do not edit `pilot/`.
- ⚠ **Grep `~/tools/verus/vstd/` — the PINNED vstd — before saying no spec
  exists.** `../LearnVeri/_VERUS_DOC_/vstd/` is a **different, older snapshot**
  and using it produced a false "no spec" claim that stood for 44 tasks.
  **`p15`'s own selection already turned on this**: `core::str::from_utf8_unchecked`
  is `is not supported` while the **inherent** `str::from_utf8_unchecked`
  verifies `2 verified, 0 errors`. **Verus's `is not supported` is correct about
  the function you named and can still be the wrong answer to your question.**

---

⚠ **PROTOCOL rule 2's running count is 235**, carried from `TASK_083.md`.
`TASK_084` is live and its contradictions are not yet counted; this file holds
the count meanwhile. **The manager's least-sure calls in this task are, in
order: Q2's claim that `identity` is binding rather than merely universal
(§2), the §3 prediction that R4 comes out dearer than R3, and the §3-B guess
about overlong encodings.** All three are one run away from being settled.
Contradict any of them and say so plainly; carry **235** forward incremented by
what you find.
