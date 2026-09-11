# TASK_PHP_035 — `ph29` STAGE B: close or refute `r4_fold_iter`, then discharge the spellings debt

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_035_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR SPECIFICATION IS `TASK_PHP_033_REPORT.md` §4, §5 AND §6, AND IT IS
NOT RESTATED HERE.** That report decomposed the gap to the digit, ran five Verus
attempts and said exactly what is left. **Read §4–§6 and build to them.** This
file carries only the manager's decisions on it, the scope, and the traps.

⚠ *Two copies of one specification is how both go stale.* **If §4–§6 and this
file disagree, the report wins on anything technical and this file wins on
scope.** Say so if you find a disagreement.

**Read**, in this order:
1. **`.tasks-php/TASK_PHP_033_REPORT.md` in full.** §5 is the question the row
   turns on; §5.1 is a spelling fact that is **free, do not re-derive it**;
   §5.2 says what a closure would and would not mean; §6 is what is left.
2. `.tasks/PROTOCOL.md` — rules 6, 9, 10, 11, 13, **14**.
3. `.tasks-php/PROTOCOL_PHP.md` — **§H binds the control you ship.**
4. `.memory-php/02-ladder.md` **in full** — authoritative. ⚠ **It is STALE on
   `ph29`'s audit numbers** (it says `4 / 4 / 0`; the record says **12 / 4 / 8,
   `present` 22**). The manager owes that correction and it is not yours.
5. `.memory/02-bench-rules.md`'s **`fixed-R4 bound`** rule, and its **reason 2**.
6. ⭐ `patterns-php/ph07-strcut-cursor/controls/spellings.py` + `spellings.json`
   — **the template**, and `ph16`'s is the **bar**: it shipped **54** must-fire
   negatives. **Read them; do not touch either row.**
7. `../LearnVeri/PITFALLS.md` before debugging any Verus error.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent session**
edits it.
⚠⚠ **`TASK_PHP_034` IS RUNNING** — an `ph45` R1h hunt, read-only, reading the
corpus and the pinned tarball. **Do not touch the corpus, `.temp/php34/`, or any
`ph45` row directory** — that row is not built yet and this task does not open
it. (Written without a path on purpose: a glob for a directory that does not
exist is a citation `citecheck.py` rightly cannot resolve in a LIVE doc.)
⚠ Scratch under `.temp/php35/`. ⭐ **`.temp/php33/` holds `probe_b.py`, the nine
variants, the disassembly and the five Verus logs — REUSE IT, do not re-derive.**
⚠ **`grep -a` ALWAYS** (F35). **No `until … sleep` poller loops** — foreground
`sleep` is blocked and one task leaked ~60 shells that way; use **one** tracked
background job and wait for its notification.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`12/0`**, first and last.
Both measured by the manager at 2026-09-11 **after `_033` landed**.

---

## §1 The one question, and both answers are publishable

> **Does `r4_fold_iter` have a byte-identical Verus twin that verifies?**

`spec.md` pins `identity: unsafe == verus, O3 exact`, so this is what decides
whether the candidate is a **rung** or merely a **control**.

* **If it verifies** — `ph29`'s R4 side was **unsearched**, the −6.06 % is an
  artefact of that, and (§5.2) the candidate is **6.5 % cheaper AND one trusted
  call site smaller**, because it replaces `vget_unchecked`'s **only** call site
  with a checked slice index. ⚠ **That is a stronger claim than "cheaper" and it
  must be stated separately from the bound.**
* **If it cannot** — the row is `.memory/02-bench-rules.md` **reason 2** in its
  purest form, *the R4 side is chained to the prover*, and the negative spread
  is a **result about the ladder** rather than about Rust.

⚠⚠⚠ **NEITHER ANSWER IS A FAILURE, AND YOU MUST NOT PREFER ONE.** `CLAUDE.md`
rule 6: *"the R5 can't state the obligation"* and *"no column moves"* are
**findings, never kills**. A task that reaches the second answer and reports it
cleanly has done the whole job.

⭐ **`_033` got `4 verified, 0 errors` with `assume(false)`**, so the `requires`,
the `ensures`, the iterator plumbing and the pre-loop invariant all discharge.
**What is left is the inductive step**, and `_033` names the obstacle precisely:
inside the body `it.index()` is the **pre-`next`** value. ▶ **Its own advice is
to re-read `VerusForLoopWrapper::next`'s `ensures` before writing more
invariants. Start there.**

⚠ **Read the ERROR TEXT, not the exit code.** `is not supported` disqualifies,
because it forces a new TRUSTED item. `postcondition not satisfied` and
`invariant not satisfied` disqualify **nothing** — `p05` went `11 verified,
1 errors` → `13 verified, 0 errors` with one lemma and one `proof` block, at
**zero** TCB. ✅ `_033` measured that **`is not supported` appears in none of the
five attempts**, and that the pinned vstd ships `assume_specification[<[T]>::iter]`,
`IteratorSpecImpl` and `VerusForLoopWrapper`.

⚠ **GREP `~/tools/verus/vstd/std_specs/` SPECIFICALLY.** A `vstd/<mod>.rs` trait
declaration is **not** the specification — that confusion has produced a false
*"no spec exists"* twice in this project.

---

## §2 What to ship

1. **The verdict on `r4_fold_iter`**, with the full error text of the final
   attempt whichever way it goes.
2. `controls/spellings.py` + `controls/spellings.json`, under
   `patterns-php/ph29-recvfrom-alloc/` — ⚠ **path split on purpose; written
   whole it is a forward reference and `citecheck.py` flags those.**
   **§H binds: it lands with its must-fire negatives or it does not land.**
   ⚠ **`ph16` shipped 54. `_033`'s draft had 9 and it was right not to ship it.**
3. ⭐⭐ **`NOTES.md`'s §0 disclosure table, in the SAME re-gate.** It owes a
   **sixth** `contract_sha256` move (`28a92facffb3…` → `a5dfc7d473a2…`,
   `TASK_PHP_033`), and the entry should carry §3.1's finding. ⚠ **`NOTES.md` is
   in `source_sha256`** — the manager checked — **so it costs a re-gate on its
   own, and is FREE inside yours.** `PROTOCOL.md` rule 6.
4. **Two labelled quantities and never three**: `R3ship − R4ship` (the
   `fixed-R4` bound) and the **R3-side span**, cheapest-found to dearest-found
   in contract. **NO PAIR INTERVAL.** `min(R3 found) − min(R4 found)` is **not**
   the repair — two upper bounds differenced bound nothing in either direction.
5. ⚠ **Do not re-ship a rung for a cheaper spelling.** R4 is held fixed by fiat;
   that is what makes the bound a bound.

---

## §3 ⚠ The manager's decision on WHICH STATISTIC — new, and UNREVIEWED

`ph29`'s bound depends on which family it is quoted in: **A1 −6.06 %**
(kernel-exclusive, per call, `small.bin`) against **B1 −4.51 %** (whole-program
marginal). The manager measured the question this round
(`.temp/mgr170/NOTES.md` §1, three probes, all `--selftest` PASS) and decided:

> ▶ **Quote `A1`, and name it.** The decider is the **null control**:
> `identity` pins R4 and R5 byte-identical, so `verus − unsafe` has a known true
> value of **0**. **Family A's null is `0.000 %` across all 39 rows of both
> programmes; family B's reaches `+3.65 %` (PHP) and `+5.01 %` (PAT)** — and on
> `ph03`/`small.bin` **B's null exceeds the effect B is being used to measure.**

⚠ **The condition matters as much as the rule**: A is the headline **only where
the two compared cells have comparable callee share**. For `ph29`'s R3-vs-R4
they do (`inside_share` 0.655 vs 0.669, Δ = 0.014), so A1 is right here.
⚠⚠ **It is NOT right for this row's C-vs-Rust column** (C 0.927 vs Rust 0.655,
Δ = 0.27), and a sweep found **31 sign flips in 310 comparisons, every one with
callee asymmetry > 0.02 and none below it.** ▶ **If you publish a C-vs-Rust
number for `ph29`, publish BOTH families, labelled.**

⚠ **This decision has had no review.** If your measurements contradict it, say
so — that is worth more to me than compliance.

---

## §4 ⚠ The traps

1. ⚠⚠ **`idiom_problems` refuses any `required`/`forbidden` key outside
   `IDIOM_LANGS`.** `_033`'s first draft used a `"note"` key and would have hard
   failed; **this row has already paid for that once** (`NOTES.md` §12 item 0).
   If you touch the declaration at all, the keys are `c` and `rust`. **Nothing
   else.**
2. ⚠⚠ **Never backtick a span containing a character literal** — `exec_code`
   blanks them, so the pin is dead on arrival. **0 such spellings exist in
   either programme today; do not create the first.**
3. ⚠ **In a `forbidden` entry every backticked span becomes a ban**, including
   one you quote in order to *explain* it. That trap has now caught three
   people on this row, the manager among them.
4. ⚠ **Write `0..recvd`, never `..recvd`** — §5.1: `RangeTo` has **no** vstd
   spec, `Range<usize>` does, and the two are **byte-identical machine code**.
   This is free; do not spend a probe on it.
5. ⚠ **`_033`'s §4 mechanism is UNVERIFIED by the manager.** It closes to the
   digit with no residue, which is unusually clean — **that is a reason to try
   to break it, not to trust it.** ⭐ F52's shape is *"a probe whose setup
   encodes the answer evaluates fine and is wrong"*, and *too clean* is the only
   warning it gives. **Try to falsify §4.1 before building on it.**
6. ⚠ A `controls/*.py` addition re-gates the row. Budget for it, and batch §2.3
   into the same run.

---

## §5 Definition of done

1. The `r4_fold_iter` verdict, with final error text, **either way**.
2. `controls/spellings.py` + `spellings.json`, §H-compliant, or an explicit
   statement of why not with what is missing.
3. `NOTES.md` §0's sixth row, in the same re-gate.
4. `ph29` re-gated **green**, verdict read **out of `results-php/gate/`**.
5. Both brackets, first and last.
6. ⚠⚠ **Your headline and your gate are two separate claims, and only the gate
   record settles the second.** A task reported "built" while its own gate was
   still running, and that gate then failed twice before passing. **Do not write
   a verdict you have not read out of the record.**
7. Anything that contradicts this file or `_033`'s report — say so. §3 is the
   manager's own unreviewed work.
