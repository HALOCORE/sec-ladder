# TASK_068_REVIEW — the gate grew a new HARD-FAIL path and a way to declare a hang

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (**rule 5's "could this happen by accident?"
test is the standard item 1 must meet**), then `.tasks/TASK_068.md`, then
`.temp/p68/NOTES.md` (the engineer's raw log), then the diff:
`git show ce06c21 -- harness/check.py`.

**State:** 19 `PASS` + p01 `PASS-WITH-BLOCKED-ROWS` (pre-existing, documented),
**0 failures tree-wide, 40 records 0 STALE, no measurement record moved.**
`check.py` went **5463 → 5884 lines (+421)**.

⚠ **This task changed the GATE, not a pattern — so a defect here is a defect in
the instrument every other result is measured with.** Two of its changes are
higher-risk than anything a pattern does:

- **`forbidden_hits` now FAILS.** A false positive now **blocks a pattern**.
- **A pattern can now declare that a cell HANGS** and have the gate accept it.

⚠ **The engineer refuted the manager's design in two places and the corrections
are the claims with no adversary.** Attack those, not the ones already dead.

## A1 — a new hard-fail path. Try to false-positive it.

`forbidden_hits` moved from printing to **failing**. The accident test was
applied and answered *yes, it happens by accident* (p27 forbade `` `memset(tab` ``
and both its own C rungs spelled it). TASK_063's counter-argument is recorded as
*"right about strength, wrong about direction"*. Split into `forbidden_verdict()`
with **4 new selftests**; two known false-positive shapes (`#[cfg(slb_twin)]`
bodies, `CONTROL_CELLS`) are named in the failure text.

> **Construct an HONEST pattern that this now blocks.** That is the whole
> question — the check is only worth its risk if an honest pattern cannot trip
> it. The named shapes are a start, not the search: try a `forbidden` spelling
> that appears in a **comment** that `spelling_matches` fails to blank, in a
> **string literal**, in a **ghost/proof-only** block, inside `#[cfg(test)]`, in a
> **control cell** that is not a rung, and as a **substring** of a longer
> identifier. **`.memory/02-bench-rules.md` records that `spelling_matches` does
> NOT blank `#[cfg(slb_twin)]` bodies** — 0 of 15 pins today, but this change
> converts that from hygiene into a **live hard-fail**. Say whether it still
> reads as hygiene.
>
> **Then check the 4 selftests actually constrain the function** rather than
> restating it, and that `forbidden_verdict()` is reachable from the real path
> and not just from tests.

## A2 — a pattern can now declare a HANG. Try to abuse it.

New optional contract block `"run": {"timeout_s": …, "why": …}` plus optional
`model.expected_hang`; `check_hang_declarations` requires **both**; stage 4
records `hung` **and requires ≥1 cell to have hung**; stage 7 accepts a declared
hang; stage 8 blocks a declared-hang Miri row up front. **7/7 guards fired** in
the worked example (`.temp/p68/hang_demo.py`), 5.0 s against the shipped 900.

> **This is a mechanism for telling the gate "do not expect an answer here", and
> that is exactly the shape of a gate bypass. Attack it as one.**
>
> - **Can a pattern declare a SHORT `timeout_s` on a legitimate input** so a
>   slow-but-correct cell reads as a declared hang and skips a check it would
>   otherwise fail? What is the smallest `timeout_s` accepted, and is there a
>   floor?
> - **Stage 4 now REQUIRES ≥1 cell to have hung.** What if none does — on a
>   faster box, or after an optimisation change? **Is that a hard fail, and can
>   it false-fail an honest pattern?** A gate condition that depends on wall-clock
>   timing is a new species here; every other one is deterministic.
> - **Can `expected_hang` be declared on a NON-adversarial input?** The engineer
>   added a guard and then **scoped their own claim down**, saying it is
>   *"fail-closed defence in depth, not the closure of a live hole"* because
>   `check_checksums` requires `rc == 0` and reads no model expectation.
>   **Verify that scoping** — if the hole *is* live, the guard is load-bearing and
>   the write-up understates it.
> - **Does a declared hang leak into the MEASUREMENT path?** `measure.py` is
>   supposed never to execute an adversarial input. Confirm on this new code.

## A3 — the manager's design was refuted twice. Check the replacements.

1. **`expected_exit = None` is refuted by the code**: `diverges = (rc != m_exit or
   out != m_out)` would score the *hanging* cell as **not** diverging and the
   *terminating* one as diverging — printing p22's headline upside down, since
   **R5 is the rung that ends**. So the hang got its own field and `expected_exit`
   keeps describing conforming behaviour.
2. **"Should declaring a hang move `contract_sha256`?" → yes, but there are TWO
   declarations**: the *prediction* stays in `model.py` (derived from the blob's
   bytes; *"a `spec.md` pin must be checkable by reading `spec.md` alone, and
   'does this blob loop forever' is not"*), the *budget* is a resource pin in the
   contract.

> **Both arguments are good and neither has been attacked.** Is the split
> actually enforced — can you declare one without the other and still go green?
> And is the stated principle (*a `spec.md` pin must be checkable from `spec.md`
> alone*) true of the **existing** pins, or is it a new rule invented here that
> the tree already violates? **Check two or three existing contracts against it.**

## A4 — item 3 was NOT landed, and the reason is a claim about cost

The token turns p38's gate **RED**: `p38/model.py::sanitizer_expect` returns
`"clean"` unconditionally, so two adversarial rows fire on an input declared
clean. The engineer says fixing it edits a **measurement-hashed** file → stales
`results/p38-alias-pun.json` → forces a re-measure → which re-takes the
wall-clock block, whose `ns` floor is a **session** property (≈18% shift measured
on p08 for unchanged cells). **Recommendation: land token + `sanitizer_expect` +
p38 re-measure as one unit.**

> **Verify the trap is real, because it is now scheduling policy.** Is
> `model.py` genuinely in `measure.py`'s source list? Is there truly **no** route
> that avoids the re-measure — a contract-side override, a stage-7-only
> expectation, anything? The engineer says stage 7 reads `sanitizer_expect` from
> the model only; **confirm that by reading the code, not the report.** And
> **spot-check the ≈18% session-shift figure** — it is doing a lot of work in
> this argument.
>
> ✅ **Also confirm the negative that makes this safe:** p02's and p11's apparent
> diffs are **ELF BuildId inside the ASan text, not behaviour**. If any of those
> five rows is a real behaviour change, the blast radius is not one pattern and
> the whole item needs rethinking.

## Also in scope

- **The citation sweep: 25 re-cited across 13 patterns.** Spot-check that they
  now point at what they claim, using the aid at the end of
  `.memory/02-bench-rules.md`. ⚠ **p09's `contract_sha256` MOVED** — verify the
  disclosure in `patterns/p09-bitset/NOTES.md` against
  `git show ce06c21^:patterns/p09-bitset/spec.md`, and that **no `required`/
  `forbidden` entry, obligation count, identity, collapse or driver pin moved**.
- ⚠ **6 citations were deliberately LEFT stale** because they live in
  `model.py`/`inputs/gen.py`, which are measurement-hashed (p12, p13 ×3, p16 ×2,
  p38). **Confirm that list is complete** — a seventh left unrecorded is worse
  than six recorded.
- **p01 (1 entry) and p05 (2 entries) ship `forbidden` entries with ZERO
  backticked spellings**, so their "forbidden: 0 hits" audits an **empty set** —
  the p09 defect fixed on p09 only. Now shouted, not failed, on the ground that
  backticking is a **declaration** edit owing the direction test. **Is shout the
  right severity now that `forbidden_hits` FAILS?** And **is the list complete
  across all 20?**
- ⚠ **`.temp/t60-sweep.sh` read `rc=$?` after a PIPELINE**, capturing `tail`'s
  status — so it could never report a failing gate. **Does any committed claim
  rest on a sweep run with it?** Check whether the per-pattern verdict text would
  have exposed a failure anyway; if so this is hygiene, if not it is a major.
- **`check.py` grew +421 lines for this task.** PROTOCOL rule 5 prefers a pattern
  over gate hardening. **Is the addition proportionate**, and is any of it
  re-implementing something the file already had?

## Clean negatives are wanted

PROTOCOL rule 6. p10's review returned 21, p27's 28, p47's 32, p38's 35.
**List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch **`.temp/p68rev/`** — your own subdirectory; read
`.temp/p68/` but do not modify it); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under `patterns/`.
⚠ **You MAY run `harness/check.py` on any pattern** — this task changed the gate,
so a single-pattern check is not enough — **but a gate run REWRITES that
pattern's `results/gate/*.json`. Restore it with `git checkout --` afterwards and
say that you did.** Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. **You are
the only agent running.**

**Write `.tasks/TASK_068_REVIEW_REPORT.md` before you finish** (rule 10), then
return the same content in the report format. Rank findings `blocker` · `major` ·
`minor`, with file:line and a concrete failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
146** — 143, plus three from TASK_068: the `expected_exit = None` design, the
manager's overstated claim that the non-adversarial guard closes a live hole, and
the assumption that item 3 was a one-token change that could land in this batch.

**What I am least sure of, by name: whether item 1 should have shipped at all.**
It is the first change here that can **hard-fail a pattern on a typographic
property of its own source**, and PROTOCOL rule 5 exists because that trade has
gone wrong before. The accident test was answered *yes* — which is an argument
for the check and **also** an argument that the false-positive surface is real.
**If you can build an honest pattern that this blocks, that is a blocker and I
want to know before another pattern is written against it.**
