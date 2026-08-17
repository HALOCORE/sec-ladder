# TASK_011_REVIEW — is p17's "provably memory-safe and still leaks" real?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_011.md` (the spec),
`patterns/p17-http-range/NOTES.md` (889 lines — the delivery), `git show a58ca64`,
and **`.memory/01-ladder.md` finding 5 (p17)**, which is the manager's write-up
and is itself under review. One pattern ago the manager wrote a finding from an
engineer's report without re-measuring and it overclaimed; assume the same risk
here.

## The one claim that matters

p17's headline is **not** a performance number. It is:

> A program can be **provably memory-safe and still leak**, and here is one.

Evidence offered: `verus_absguard.rs` — the sign check replaced by a guard on the
*absolute* index (`start >= -(body_start as i64)`), which is what a bounds check
buys you — gives **`9 verified, 1 errors`**, the single error being the
*functional* invariant, with **every `get_unchecked` precondition discharging**.
Built as plain safe Rust it prints the leaked value on `adversarial-leak` and the
correct answer on `adversarial-oob`.

If that holds, it is the most important artefact this project has produced. **Your
first job is to try to destroy it.** Specifically:

1. **Re-run it and paste your own output.** Do not trust the report's.
2. **Is "1 error" really only the functional obligation?** Verus reports the first
   failure per query; confirm no access obligation is merely *hidden* behind it.
   `--verify-function <name> --verify-root` per item is the tool
   (`.memory/04-verus.md`). A memory-safety obligation that fails second still
   falsifies the claim.
3. **Is the absolute-index guard a fair stand-in for "what a bounds check
   buys"?** This is the crux and it is a judgement call. A skeptic would say the
   manager and engineer chose a mutant *designed* to separate the two obligations,
   and that a real bounds check gives you something subtly stronger or weaker.
   Argue it either way, with the Verus output.
4. **Does the "leak" actually leak anything meaningful**, or is it reading bytes
   that happen to be in the same window and would be visible anyway? The claim is
   an *information disclosure*: bytes the caller was not entitled to. Check what
   is actually being disclosed — the suffix table is attacker-supplied, which
   would make the "leak" a disclosure of the attacker's own data and **much
   weaker than claimed**. If so, say so loudly; it is the sharpest possible
   correction and it would force a restatement of finding 5.

Point 4 is the attack I would run first.

## Part 2 — the safe-Rust control

`safe_naive_nocheck.rs` prints `1395842226496950656`, reported bit-identical to
C's leaked value.

- Reproduce both numbers yourself.
- **Is bit-identity meaningful or coincidental?** Both compute the same fold over
  the same bytes, so identity is expected *if* they read the same range. Confirm
  they do, rather than agreeing by accident.
- The claim "safe Rust does not fix this" rests on the read being in-bounds *of
  the Rust slice*, not merely of the allocation. Verify that distinction — Rust's
  bound is the slice, C's is the malloc region, and they are not the same object.
  **If the Rust read is in-bounds only because the slice is the whole blob, say
  what that means for the generality of the finding.**

## Part 3 — standard pattern validity

`PROTOCOL.md`'s checklist; skip what the gate already certifies. Priorities:

- **Are R1 and R1h really one conjunct apart?** The engineer restructured
  `continue` into `if start < end && start >= 0` because Verus `for` loops reject
  `continue`. Confirm R1 drops exactly the second conjunct and nothing else.
- **Is R2 a fair naive port?** p16's review tested four alternative naive
  spellings and found R2 tied-cheapest. Do the equivalent here — a +69.6% claim
  needs it.
- **The `abs = len - s` identity** was verified by the manager in Python, not
  against the built kernels. Confirm the shipped C and Rust actually implement it.
- **`work_per_call` under-estimates by 1.72×/1.75×** here (p16's over-estimated),
  so the derived floor is *loose* — margin 40.3×, ~97.5% work loss tolerated. Is
  the floor still doing anything on this pattern? If not, say so; it is a
  documented residual, not a blocker.
- The kernel gained a second `requires` (`buf@.len() <= isize::MAX`) because vstd
  has no such axiom. Check that the driver's matching guard conjunct really
  discharges it and is not vacuous.

## Part 4 — the numbers

- **R2−R4 = 4.2500 Ir/folded byte, claimed to reproduce p16's constant to four
  decimals on a different kernel.** This is a strong claim about rustc rather than
  about a pattern. Re-derive it from one raw callgrind run. Two patterns agreeing
  to 4 d.p. is either a real invariant or a methodology artefact — which?
- **gcc's default rolled fold at exactly 8.0000** — same question, since p16's
  review derived 8.00 as the rolled-unchecked constant.
- Wall clock: 0.784–0.791 ns/byte, no cycles/byte claimed because CPU 3's clock
  was seen ramping 800→902 MHz. **That is a bigger deal than it looks** — p16's
  wall-clock analysis assumed a stable 3.85 GHz on CPU 5. Are p16's cycles/byte
  figures still safe? Check whether the two patterns were measured on differently
  governed CPUs, and say whether anything in `.memory` needs qualifying.

## Part 5 — clean negatives

Name what you tried that did not land.

## Not in scope

Not a gate-bypass hunt (`.memory/02-bench-rules.md`, top). Nothing in `harness/`.
Do not re-review p02's Part 0 re-measurement beyond confirming `git diff` on
`p02/NOTES.md` matches the new JSON.

## Deliverable

`.tasks/TASK_011_REVIEW_REPORT.md` + `PROTOCOL.md`'s report format. Severities
with file:line and a concrete failure scenario. **State in one line at the top:
does `.memory/01-ladder.md` finding 5 overclaim, underclaim, or is it right?**

## Constraints

No root; no `/tmp` (scratch `.temp/review011/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, or `patterns/` — you report, I fix.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. **A gate run on a mirror writes into the tracked
`results/gate/`** — check `git status` before finishing and move anything you
created into `.temp/review011/`.

Notes to `.temp/review011/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Ten agents have
now contradicted the manager's written instructions and all ten were right — the
most recent one replaced a broken experiment of mine with the correct one, which
is why this pattern has a result at all.
