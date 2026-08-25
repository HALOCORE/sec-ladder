# TASK_096_REVIEW — attack the `_scan_unsafe_sites` recommendation, and the hole it found

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md` (**the reviewer checklist and the severity scale**),
then `.tasks/TASK_096.md`, then `.tasks/TASK_096_REPORT.md` (**what you are
attacking**), then `.memory/02-bench-rules.md`'s threat model,
`.memory/04-verus.md`'s TCB section, and `.memory/06-catalogue.md`'s `p15`
refusal block and `p35` row.

The engineer's artefacts are in `.temp/t96/`. Your scratch is **`.temp/r96/`** —
free, I checked. ⚠ Do not write into `.temp/t96/`.

---

## Why this review matters more than most

**The catalogue is measured out** — 48 rows = 24 built + 14 refused + 10
remaining, and `p23` is the only live build candidate. **`TASK_096`'s
recommendation is the input to a decision about whether this project builds two
more patterns or none**, and PROTOCOL rule 3 says the manager must not clear its
own gate design. **You are the different agent.**

⚠ **I have a motive and you should discount for it: I want the hatch to work,
because `p35` carries the only bug class absent from the built tree.** Attack it
accordingly.

---

## A — ⚠⚠ `check.py::_verus` DISCARDS THE RETURN CODE. Bound it.

✅ **The mechanism is MANAGER-VERIFIED and is not in question.** `_verus` regex-
matches `(\d+) verified, (\d+) errors` out of `stdout + stderr` and **never reads
`r.returncode`**. I reproduced it end to end: a `verus!` union read with
`requires v is i` and no `unsafe` block prints **`2 verified, 0 errors`** and
`verus_run.py` **exits 1** with `error[E0133]`. **So the twin oracle can certify
source that rustc rejects, and on the engineer's real gate run it did.**

**What is NOT established, and is your job:**

1. **Is it really latent?** The bound offered is *"50/50 shipped rows `rc=0`, 0
   errors"*. ⚠ **That is a statement about today's tree, not about the check.**
   Ask what an *honest mistake* looks like here — the threat model is honest
   mistake, not malicious author — and whether a plausible one produces
   `rc != 0` with a clean "N verified, 0 errors". **A verified-but-uncompilable
   twin is exactly the shape.**
2. **Is the fix safe at all 12 call sites?** The engineer says 4 need the check
   and **8 are mutants that must exit non-zero**. ⚠ **Verify that partition
   yourself.** A returncode check bolted onto a mutant call site would turn every
   mutant into a failure and the battery would go green for the wrong reason —
   which is the tautology trap this project has hit three times.
3. ⚠ **Does anything ELSE in `harness/` read a subprocess result the same way?**
   One `grep` for `subprocess.run` against `returncode` settles it. **If there is
   a second site, that is a bigger finding than the first.**

---

## B — the recommendation: *narrow the rule behind a declared hatch*

**Attack the evidence, in this order.**

1. ⚠⚠ **§A.2's central claim is ENUMERATIVE: *"everything Verus admits inside a
   verified body carries an obligation"*, from 26 constructs.** That is not a
   proof, it is a sample, and the recommendation's whole safety argument rests on
   it. **The engineer names its own gap: `unsafe impl GlobalAlloc` /
   `Allocator` were not probed.** ⚠ **Probe those, and then ask what ELSE is in
   the space** — `unsafe` in a `const`, in a trait default body, behind a
   `macro_rules!` expansion, inside `#[verifier::external_body]`'s *sibling*
   attributes, `unsafe extern` blocks, `unsafe` attributes
   (`#[unsafe(no_mangle)]`). **One obligation-free construct that Verus ADMITS
   kills the recommendation.**
2. ⚠⚠ **§A.2b says the narrowed rule ALONE would DELETE THE STRENGTH CHECK on
   the very row it admits.** `_mutation_targets`' `verified` list defaults to
   `[kernel_item]`, and the verified plant probed **4 conjuncts, identical to
   baseline — `read_i` appears NOWHERE in the gate log**, while the comply plant
   probed 5 plus the twin oracle. **So the hatch as recommended trades a hard
   refusal for a silently weaker pattern.** ⚠ **This is the finding I would most
   like confirmed or destroyed**, because it decides whether the hatch is a fix
   or a downgrade. **Is the "three enforced consequences" design actually
   sufficient to restore what is lost? Test it, do not read it.**
3. **§A.3's TCB answer.** A `p35` would publish `tcb_items = 2`, both infra —
   i.e. **a pattern whose entire memory-safety argument is a Verus obligation
   reports a trusted base of zero project-local items.** ⚠ **`.memory/04-verus.md`
   named this case IN ADVANCE at TASK_055_REVIEW** (*"a pattern built on
   `vstd::raw_ptr` … decide how such a pattern is counted BEFORE building
   one"*) and closed the policy: **one number, prose beside it, and the second
   "vstd relied upon" column REFUTED with a 402-site census and marked "must not
   be reinstated."** **Is `2` the honest number under that policy, or is the
   policy itself now the thing that is wrong?** ⚠ **If your answer is "reinstate
   the second column", you must beat the 402-site census that refused it.**
4. ✅ **The probe-4 POLARITY inversion is the most interesting thing in the
   report and I want it stress-tested.** The engineer's discriminator: **a vstd
   spec for the operation is a reason to REFUSE, not to admit** — `p35`'s
   `union` is absent from vstd (0 declarations, 0 specs) and `p15`'s licence is
   `vstd/string.rs:136`. ⚠ **That inverts the polarity of the catalogue's own
   probe 4, which is a live selection instrument.** **Does it hold on the 24
   BUILT patterns**, or does it retro-refuse a shipped row?

---

## C — ⚠ `p35` IS BLOCKED BY TWO RULES AND THE SECOND IS RUST

§A.1b: `_TWIN_BANNED` forbids `unsafe` in a twin, **and there is no safe union
read in Rust** (`error[E0133]`), so the twin must be justified away — which is
`n_twins == 0` → hard FAIL, or a `PASS-WITH-BLOCKED-ROWS` **on the row that IS
the pattern.**

⚠⚠ **This contradicts the premise I scheduled `TASK_096` on** (*"one rule blocks
two rows; fixing it is worth two patterns"*), **and the engineer flags that the
`n_twins == 0` hard-fail limb is a CODE READ, not an executed gate.** It cites
`TASK_084_REVIEW` route G rather than re-running it.

**Run it.** If `p35` really has no legal configuration, then **the hatch buys
`p15` alone** — and `p15` was refused for reasons beyond this rule, so the
honest conclusion may be **that the catalogue is finished and no hatch should be
built at all.** ⚠ **That is a perfectly good review outcome and I would rather
have it now than after a pattern is built.**

---

## D — also check, briefly

- **`results/tables/p46-bignum-mac.md` has been stale since `TASK_092`** — a
  pre-re-measure wall-clock table and a **pre-correction contract digest** — and
  **nothing regenerates `results/tables/`.** ⚠ **How many of the other 23 are
  stale?** The engineer regenerated all 24 and found this one; **confirm the
  count, and say whether any published number in `results/tables/` is wrong**,
  not merely old.
- **`results/gate/` has no `--check-stale`.** The engineer wrote one ad hoc
  (`.temp/t96/d2_gate_stale.py`) and it independently named the same 8 records.
  **Is that a check worth having in `harness/`, by the "could this happen by
  accident?" test?** It just did.
- **The 2-of-43 wrong function names**, self-caught: the engineer resolved the
  rotted **line** instead of the **sentence**. ⚠ **Spot-check a sample of the
  other 41** — that is exactly the error a reviewer is for.
- ⚠ **The engineer edited `harness/check.py` MID-SWEEP** and went 8 STALE, then
  repaired and re-gated. **Verify the repair is complete** rather than trusting
  the final `0 STALE` — a re-gate after an edit is the configuration where a
  stale record hides.

---

## Constraints

- **`.temp/r96/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `pilot/`, `harness/build.py` or `harness/asm.py`.**
- ⚠⚠ **The tree is CLEAN and COMMITTED at `3841198`, so you MAY run
  `harness/check.py`** — but it rewrites tracked records in place, so **restore
  them (`git checkout -- results/gate/`) before you finish, and say in your
  report whether you did.** ⚠ **Prefer planting into `.temp/r96/` copies.** If an
  attack needs a plant into a tracked `patterns/` file, snapshot **by bytes**,
  restore in a `finally:`, and **say so** — `TASK_084_REVIEW` did exactly this
  and it worked.
- **Do not run `harness/measure.py`.**
- Verus via `./verus_run.py`, single-file mode only.
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Give clean negatives.** A named attack that did not land is worth as much as
  a finding.

Write your report to `.tasks/TASK_096_REVIEW_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 279.** The calls I am least sure of:

1. ⚠⚠ **That the hatch is worth building at all** given C — if `p35` is blocked
   by Rust itself, the whole exercise buys one refused row.
2. **That §A.2's enumeration is sufficient** to license a soundness-relevant
   narrowing. 26 constructs is a sample.
3. **That `tcb_items = 2` is the honest number** for a pattern whose safety
   argument is entirely a Verus obligation.

Carry **279** forward, incremented by what you find.
