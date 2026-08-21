# TASK_056 — the batched change: gate fixes, six patterns' prose, and ONE 16-gate re-run

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_053_REPORT.md` in
full** (the gate audit — it carries the diffs), then
**`.tasks/TASK_054_REPORT.md` §3** (the sole-catcher table) and
**`.tasks/TASK_055_REPORT.md`** (p08's Route B′ and its price), then
`.memory/02-bench-rules.md`'s **threat model and rule 5**, `.memory/04-verus.md`'s
**TCB accounting** and its new `RangeTo` / `split_at_mut` entries.

**Everything here shares one cost: `check.py` is hashed into every gate record,
so any `harness/` edit makes all 16 stale.** That is why these are one task —
the ~30-minute re-run is paid **once, at the end**.

⚠ **Two of the manager's implied prescriptions were already measured wrong by
the audit. Use the AUDIT'S fixes, not the obvious ones.** They are called out
below.

---

# Part A — `harness/check.py`

Land the audit's findings **with the audit's proposed diffs**. Re-derive each
before applying it; the report has the reproduction for every one.

1. **F2 (`:2799`) — 51 of 52 shipped tautology rows are wrong, on all 16
   patterns.** `_run_taut_battery`'s tactic arm has no `pv is None` case, so a
   `by (bit_vector)` that **aborts** (which it does on any clause mentioning
   `v@.len()`) falls through to `"not a tautology"`, and every gate JSON records
   `verified: null, errors: null, tactic: "bit_vector", verdict: "not a
   tautology"`.
   ⚠ **DO NOT make this a hard failure.** The audit measured that
   `return "nocompile"` would red-line **all 16 patterns**, because `bit_vector`
   is *genuinely inapplicable* to a clause with a slice length — and there is no
   false negative to recover, since a tactic that aborts could not have proved
   the clause either. **5c-req's soundness is intact; only its claim is false.**
   Fix: record `tactics_inapplicable`, and **stop naming `bit_vector` in the `ok`
   line**.
2. **F3 (`:4405`) — the sanitizer build's stdout is bound and never compared.**
   Reproduced with the real function: a one-character off-by-one on p01 prints
   `ok small.bin clean, exit=0 (model 0)` with zero failures while the binary
   printed a wrong checksum.
   ⚠ **DO NOT compare unconditionally.** The audit ran stage 7 across all 16
   patterns: **114 rows, 37 differ, and every one of the 37 is an adversarial
   input** (6 of them declared `sanitizer_expect: "clean"`). Comparing always
   would false-fail 37 rows on 14 patterns — precisely the rows
   `check_adversarial` exists to *record* rather than require. Fix: **record
   stdout always, compare on non-adversarial inputs only.** The audit measured
   **0 new failures** on the shipped tree (77/77 match). **Confirm that yourself.**
3. **F1 (`:1822`) — 7 patterns live.** `table[name/cell]` is assigned *inside*
   the loop over `seen`, so of 4 distinct behaviours printed, 1 is recorded, with
   no opt/mode label. 22 such notes across p02/p03/p05/p06/p12/p13/p14.
   ⚠ **This changes the shape of the `adversarial` key.** The audit checked that
   nothing reads it programmatically and that the two prose citations
   (`p06/spec.md:738`, `TASK_048.md:143`) cite by key and survive. **Re-check
   before you change the shape**, and if any pattern's prose quotes a value that
   moves, fix that prose too.
4. **F4 (`:2089`) — latent, 0 live, and it defeats a rule built deliberately.**
   `vparse` returns a comment inside a `requires` list *as clause text*, so a
   parameter named only in a **comment** satisfies the parameter-coverage rule —
   the rule TASK_006_REVIEW added precisely because no verify/fail oracle can
   catch a weak trusted precondition.
   ⚠ **The audit's fix is incomplete and says so**: blanking comments closes the
   trailing-`//` and `/* */` shapes, but the comment-*before*-the-clause shape
   then hard-fails with a confusing message, because `vparse` has already glued
   the comment on and collapsed the newline. **The complete repair belongs in
   `vparse.py`** (drop comment-only clauses; strip a leading comment).
   **You may edit `harness/vparse.py` for this**, but if the change reaches
   beyond comment handling, **stop and report** — `vparse` has other consumers
   and the audit did not sweep them.
5. **F5, F6, m1, m2 (minor).** Missing `is None` arms at `:2594` and `:3520`
   (siblings at `:2645`/`:2972` have them; 0 live); `forbidden_hits` computed,
   printed, never shouted (0 of 132); two `ok` strings that overclaim on
   already-red runs. **Land them if they are as cheap as the report says.** If
   any one costs more than its value, **decline it and say so** — rule 5 is real
   and this is the fourth task in a row touching infrastructure.

## Part A′ — three small infrastructure items, same re-run

6. **`O3d` is not a first-class build mode.** `ALL_OPTS` has `O0`, `O0d`, `O3`
   and **no `-O3` + debug-assertions cell**; p18 measured that `O3d` is the
   informative one and had to build it under `controls/`. The report of a 4-line
   `build.py` change is from p18's engineer. ⚠ **`O3d` must NOT enter the default
   24 cells** and must carry `build.py:26-28`'s warning that it is **not**
   semantics-matched to C `-O0` — it is a Rust-vs-Rust axis only.
7. **`results/gate/*.partial.json` are untracked scratch, and some carry
   `FAIL`** — including a p05 record from an Aug-18 mid-edit run whose Verus
   errors look alarming and are **not live**. The manager hit this while
   surveying verdicts with a glob. **Move them under `.temp/`** (or give them a
   name no verdict survey can mistake) and say what writes them.
8. **`.temp/p54/limbs.py` should probably move into `harness/`.** It re-derives
   `check.py`'s pin comparison across **eight** limbs, it is pattern-agnostic,
   and **six patterns now need it to substantiate a published sentence** — today
   they would cite gitignored scratch, which is exactly the trap
   `p06/controls/clayout.py` exists to avoid. ⚠ **It is a reporting/repro tool,
   not a gate stage — do not wire it into `check.py`.** If you think it does not
   belong in `harness/`, say where it does belong.

---

# Part B — six patterns' prose

9. **Five patterns still publish the false sole-catcher claim**: **p03, p04,
   p11, p18**, and **p05 — which contradicts itself**, printing both
   `[proof-pin]` FAILs about twenty lines from the sentence denying them.
   TASK_054 measured all of them; **§3's table is the input**, and p12's
   corrected §9b is the model.
   ⚠ **Verify before you edit.** TASK_054 judged these five on stages 5a +
   5c-twin only, and re-derived their mutants by substitution rather than by
   running their generators. **Run each pattern's own generator**, and if a
   verdict moves, take the measurement over the table.
   The rule to write is *"the twin is the sole catcher only of a mutant that
   edits `spec.md` in the same commit"* — and say **whether `identity` moved**: a
   `requires` edit is ghost and cannot; an exec-code edit can.
10. **p12 claims to be "the second pattern to exercise this on a WRITE (p03 is
    the first)". It is the FIRST** — p03's and p04's mutants both weaken a
    **read** accessor. Measured at TASK_054, out of that task's scope. Fix p12's
    sentence.
11. **p08 carries the false *"vstd ships no spec for `copy_from_slice`"* reason
    in four places.** It is false at the pinned vstd and has been since
    TASK_048. **Fix all four regardless of what you decide about item 12.**

## Part B′ — p08's trusted item, with a hard stop

12. **TASK_055 recommends Route B′**: respell **`unsafe.rs` and `verus.rs` only**
    (p06's `idiom.required[5].rust` is the precedent — a 2-and-2 receiver split
    with its own `-O0` price published). Measured: **TCB 4 → 3**, `-O3`
    byte-identical (`md5_raw 44b63d20ccf1`, 168/166, 5 pads, +0.00 `Ir`/call),
    `-O0` identity **`exact`**, **+2.00 `Ir`/call flat at `-O0`** confined to two
    rungs. That beats p06's own outcome (+2 not +3; `exact` not `norel`).
    - ⚠ **Route B′ has NOT been through a full `check.py`** — the probe measured
      stage 3c's oracle directly. **Land it only if `check.py p08` is green on a
      complete run and `identity` reads `exact` at `-O0`. Otherwise stop and
      report**, exactly as the p02 hard stop worked.
    - **Publish the price** (`.memory/02-bench-rules.md`'s two-number rule) and
      **run the direction test in writing**: removing a trusted item shrinks the
      trusted base, which is the direction that flatters the thesis, so the
      justification has to be the measurement.
    - **Say whether the trust disappears or RELOCATES into vstd**, and classify
      the item **U-license / V-gap / infra** before and after.

---

# Part C — the re-run, last

13. **Re-run all 16 gates**, confirm `measure.py --check-stale` is clean, and
    regenerate the tables. **If any gate FAILS, stop and report the distribution
    before repairing anything** — that condition was right to have on TASK_052
    even though it did not fire, and F3 is exactly the shape that could make it
    fire this time.
14. Paste the before/after for the two record-content changes (F1 and F3) on at
    least one pattern each, so the diff is legible.

## Constraints

No root; no `/tmp` (scratch `.temp/p56/`, **per-PID paths**); **no `git
add`/`git commit`**; do not edit `pilot/` or `.memory/`. **`harness/`:
`check.py` for the named findings, `build.py` for item 6, `vparse.py` for item 4
only.** `common/`: not at all. **Patterns you may edit: p03, p04, p05, p08, p11,
p12, p18 — and only for the items above.** Verus only via `./verus_run.py`.
clang `~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. **You are now the only
agent running — wall-clock measurement is permitted, but nothing here needs it.**

The audit's scratch is `.temp/p53/` with six reproduction scripts and the
symlink-farm harness that runs a single stage function without touching a gate
JSON; `.temp/p54/limbs.py` and `.temp/p55/repro.sh` are likewise built.
**Reuse rather than rebuild.**

Notes to `.temp/p56/NOTES.md`.

**If a prescription here is wrong, say so with the measurement.** Eighty-five
agents have contradicted the manager and all eighty-five were right — the audit
you are implementing corrected **two** of the manager's implied fixes before a
line was written, and both corrections were the difference between a clean tree
and 37 false failures.

**What I am least sure of is how much of Part A is worth doing at all.**
`.memory/02-bench-rules.md` rule 5 says *prefer producing a pattern over
hardening the gate*, six tasks went to gate work before the user called a halt,
and this is the fourth consecutive task touching infrastructure. F1, F2 and F3
are live falsehoods in committed records and I think those are clearly worth it.
**F4, F5, F6, m1 and m2 are judgement calls, and I would rather you decline one
with a reason than land all five out of completeness.** Tell me which you dropped
and why.
