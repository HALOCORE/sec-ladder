# TASK_085_REVIEW — attack the `p15` probe, and attack the refusal

**Role: research reviewer.** Adversarial by design. **A review that says "looks
good" without having tried to break something is a failed review.** You do not
fix; you report. Read `.tasks/PROTOCOL.md` first (the Reviewer checklist and
Severity sections), then `.tasks/TASK_085.md` (what was asked),
`.tasks/TASK_085_REPORT.md` (what came back), then `RECAP.md` "Owed" 25.

Scratch in `.temp/r85/` — free, I checked. The probe's evidence is in
`.temp/t85/`; **`rebuild.sh` there re-derives every binary** (they were deleted
per `CLAUDE.md` "Don't" 1).

---

## ⚠⚠ 0. A THIRD AGENT IS WORKING. YOU MAY NOT RUN THE GATE.

`TASK_084` is live, editing `harness/check.py`, `harness/vparse.py`,
`synthesis/synthesize.py`, `patterns/p01-array-sum/spec.md`,
`patterns/p17-http-range/NOTES.md`, and writing `results/gate/*.json`.

- **Do NOT run `harness/check.py` or `harness/measure.py`.** Both write into
  `.temp/check`, `.temp/build` and `results/`, and would collide with a live
  sweep. **This is not negotiable and it is why §2 below is scoped away from
  the gate.**
- **Write NOTHING outside `.temp/r85/`.** Reading anything is fine.
- For any claim about `check.py`, read **`git show HEAD:harness/check.py`**, not
  the working tree — the working tree is half-edited.
- `./verus_run.py <file.rs>` **single-file mode is concurrency-safe**
  (`tempfile.mkdtemp()` per invocation). **Do not use `--cargo` mode.**
- Direct `rustc`/`clang` builds into `.temp/r85/` are fine.

**The two claims that need a real gate run are DELIBERATELY NOT YOURS** —
`identity: differ` admissibility and the end-to-end `tcb-unsafe` failure. They
are assigned to `TASK_084`'s reviewer. **Do not attempt them; say so if you
think that split is wrong.**

---

## 1. What you are reviewing

A probe that was asked whether `p15` (UTF-8 validation + decode) can be built.
It came back recommending **REFUSE**, having:

- built a **verified UTF-8 validator**, `ensures res == valid_utf8(b@)`,
  `5 verified, 0 errors`, zero trusted items, with an end-to-end call site at
  `8 verified, 0 errors`;
- **refuted the manager** on whether the `identity` pin forbids R4 ≠ R5;
- **refuted `TASK_083_REVIEW`'s row-2 harm cell** — ✅ *this one is already
  manager-verified on an independent `rustc -O` build (`exit=139` SIGSEGV, empty
  stdout) and you need not re-establish it, though you may attack its
  interpretation*;
- priced a verified validator against `core::str::from_utf8` and found the
  verified one **dearer at every alphabet, 15.58× on ASCII**;
- found that **`check.py::_scan_unsafe_sites` forbids verified unsafe**.

---

## 2. The attacks, in priority order

### ⚠⚠ A1 — THE ONE I THINK MOST LIKELY TO LAND: is the pricing table measuring the same thing on both sides?

**`kernel_exclusive_ir` counts the kernel symbol and NOT what it calls.** The
probe's own static check says `k_r3_std` is **64 instructions plus one
GOT-indirect call into libstd's `run_utf8_validation`**, while `k_a_verified` is
**130 instructions with zero calls — fully inlined**.

⚠⚠ **That is exactly p36's B2 defect**: a *reversed published comparison* found
by a reviewer summing `callgrind_annotate` rows by hand, on the one pattern whose
kernel **is** a call. `.memory/03-measurement.md`'s rule was phrased as
`@plt`/`@GLIBC` and p36 walked past it because its callees were project-local;
here the callee is **libstd**.

**So establish, with the actual numbers:**

1. **Which `Ir` convention did the probe use** — kernel-exclusive, or
   whole-program marginal by `n_iters` differencing? The report says the latter.
   **Verify it from `price.py`, do not take the sentence.**
2. **If any part of the comparison is kernel-exclusive, R3's validation cost is
   in the callee and the table understates R3 by most of its validation work** —
   which would move the headline and possibly reverse it.
3. The internal consistency check that decides it cheaply: on **pure ASCII**,
   `r3_std − ctl_assume = 1840` `Ir`/call over 4096 bytes = **0.449 Ir/byte**.
   Is that a plausible cost for a word-at-a-time ASCII validation of 4096 bytes,
   or is it the cost of *making a call* with the real work uncounted? **Do the
   arithmetic and say.** A SWAR ASCII check reads 8 bytes per iteration; 4096
   bytes is 512 iterations. Ask what per-iteration instruction count 1840 implies
   and whether a real `run_utf8_validation` could hit it.
4. `ctl_assume` is the fold-only control and every figure is a **difference
   against it**. **Is it a fair control for both sides?** If `ctl_assume`'s fold
   differs in shape from either kernel's fold, the subtraction leaves residue.

⚠ **If A1 lands, the "p11's result a fourth time" headline falls and the refusal
loses one of its three legs.** This is the highest-value hour of your session.

### A2 — is the validator's non-vacuity evidence actually independent?

`5 verified, 0 errors` on `ensures res == valid_utf8(b@)` is only as good as
`valid_utf8` and as the two non-vacuity arguments.

- **The differential oracle** (`v02_difftest.rs`, 18 499 985 cases, 0
  mismatches). ⚠ **Is it self-confirming?** If the oracle's expected value is
  computed from the *same width table / same helper* the validator uses, it tests
  the transcription and not the semantics. **The reference must be
  `core::str::from_utf8`, unmediated.** Read the file and say which it is.
- **Is `vstd::utf8::valid_utf8` the property we think?** Read it in
  `~/tools/verus/vstd/utf8.rs` — the **pinned** vstd, not
  `../LearnVeri/_VERUS_DOC_/vstd/`, which is an older snapshot that has produced
  a false claim standing 44 tasks. Does it reject **overlongs**, **surrogates
  `U+D800..U+DFFF`**, and **scalars above `U+10FFFF`**? If it does not, the
  validator is correct against a weak spec and `from_utf8_unchecked`'s real
  precondition is not met.
- **The 10-mutant battery.** ⚠ **Do all ten fail for SEMANTIC reasons?** A
  mutant that fails to *compile*, or that trips an unrelated overflow, is not
  evidence. Re-run at least the three that break only the **completeness**
  direction (m8, m9, m10) and confirm the error is `postcondition not satisfied`
  and not something else.
- **Does `5 verified` count the right five items?** Verus counts one query per
  function plus one per loop body. Say what the five are.

### A3 — attack the REFUSAL itself, and the third option the probe did not take

The probe recommends **(C) REFUSE**. Its three legs: the harm class is the
tree's fourteenth `index >= len`; the surviving row-1 harm is **p18's, which
killed p45**; and the cost result is **p11's, a fourth time**.

⚠ **But there is a third option nobody has argued, and I want it argued rather
than assumed away:** *fix `_scan_unsafe_sites` and build p15.* The rule forbids
an `unsafe` token outside an `external_body` item. p15's R5 would put a
**Verus-discharged** `from_utf8_unchecked` inside a **verified** fn — TCB
contribution **zero**. Complying would move a *proved* call into the *trusted*
column, which is backwards.

**Argue both sides and give a verdict.** Consider at least:

- `PROTOCOL` rule 5 — *prefer producing a pattern over hardening the gate* — and
  whether **softening** a rule is governed by the same test or a stricter one.
- The clean negative the probe reports: `grep -rn "get_unchecked"
  ~/tools/verus/vstd/` → **0 hits**, so all **47** existing wrappers are
  unavoidable and this rule has cost the project nothing to date. **Verify that
  grep.**
- Whether a refusal that leaves behind a verified validator, a priced alphabet
  axis and a named gate defect is *better value* than a built pattern whose harm
  class is p18's.

### ⚠⚠ A4 — A MANAGER CLAIM THAT MUST BE ATTACKED BY SOMEONE WHO IS NOT ME (rule 3)

Reasoning from the probe's census — **47 `unsafe` tokens across 22
`patterns/*/verus.rs`, all inside `external_body`, zero outside** — the manager
now believes:

> **In all 22 patterns, the unsafe operation is TRUSTED, not PROVED.** Its
> safety rests on a hand-written `ensures` in an `external_body` wrapper, not on
> an obligation Verus discharged. p15 would be the first pattern where the
> unsafe operation's precondition is **discharged from a verified
> postcondition** — the first *legitimate* zero in the TCB column.

⚠ **If that is right it re-frames finding 2** (*"the payoff arrives when the
proof licenses unsafe code"*) and the whole TCB story, and it is far too large a
claim to stand on a manager's inference from one census. ⚠ **If it is wrong, say
exactly how** — e.g. if some wrapper's `requires` is itself discharged at the
call site by verified code, then the operation is partly proved and the sentence
is too strong.

**Check it against real patterns.** p09 is the one to look at first: its
`.memory/`-recorded result is that *"the obligation that fires is a VERIFIED
item's, `load_u64`'s — not the trusted accessor's, whose `requires` is
shadowed"*, which sounds like a counter-example and may be one. p03's
`m_clamp_unsafe` (9/0, zero new trusted items) is a second place to look.

**This is the claim I am least sure of in this whole task file. Contradict it
with a measurement and say so plainly.**

### A5 — the ordinary checklist, applied

From `PROTOCOL`'s Reviewer checklist, whatever is relevant: did anything
constant-fold (the probe built buffers from `argv` — verify); is the result
consumed and printed; are the compared kernels semantically equivalent or did one
quietly do less work; **is any perf claim resting on one inline mode only**
(the probe says `isolated` only, and `.memory/03-measurement.md` requires the
inline mode be named at every figure because **p10 fitted both and the
regressors swapped**); is the alphabet axis a **slope** as declared in advance,
or was a level published.

---

## 3. What I want back

PROTOCOL's report format. Severity-ranked: `blocker` / `major` / `minor`, each
with a **concrete failure scenario**, not a vibe. **3 real blockers beat 20
nitpicks — do not pad.**

⚠ **And per PROTOCOL rule 6, give me your CLEAN NEGATIVES BY NAME** — the
attacks you ran that did *not* land. They are worth as much as the findings and
they stop the next agent re-running them. The probe supplied four; match or beat
that.

Close with **your own verdict on p15**: refuse, build-after-fixing-the-gate, or
build-as-is — **and say which of the probe's three legs you would still stand on
if A1 lands.**

---

## 4. Constraints

- `.temp/r85/` only. No `/tmp`. Keep the generator, delete the artefact.
- **Notes in `.temp/r85/NOTES.md` as you go** — agents here die to transient API
  errors; the ones who kept notes lost nothing.
- **No `git add` / `git commit`.** Read-only git is fine and you will need
  `git show HEAD:`.
- `.memory/` is manager-only. Report durable facts; do not write them.
- **You review, you do not fix.** If you find a defect in `.temp/t85/`, report
  it; do not repair it.
- `timeout <N> <cmd>` on anything long. Never `pkill`/`killall`.
- Do not bump the Verus/vstd pin. Do not edit `pilot/`.

---

⚠ **PROTOCOL rule 2's running count is 237** — the probe you are reviewing added
two, one of them against the manager. **Every agent that has contradicted the
manager with a measurement has been right, 237 times.** My least-sure calls here
are **A4** (the trusted-not-proved claim, which is mine and is large) and **A1**
(that the `Ir` convention is the crack in the pricing table). **Prove me wrong on
either and say so.** Carry the count forward incremented by what you find.
