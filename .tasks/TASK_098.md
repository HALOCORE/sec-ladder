# TASK_098 — the ±7 blast radius: which PUBLISHED numbers does it move?

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`.memory/03-measurement.md`'s
newest section** (*"`-O3 isolated` IS NOT INVARIANT"* — landed and
manager-verified), then `.tasks/TASK_097_REPORT.md`, then
`check.py::check_marginal_ir`'s docstring in full, then `RECAP.md`'s **settled
answer 1** (the R4/R5 pair as a biased draw of size one) and its **finding 16**
(code layout / the 32-byte fetch grid).

Scratch in **`.temp/r98/`** — free, I checked.

---

## What is established, so you do not re-derive it

✅ **MANAGER-VERIFIED with a one-variable experiment** (`.temp/mgr97/README.md`
rebuilds it): same binary, same input, same shell, only the **length of one
environment variable** varied. p03, `-O3 isolated`, marginal `Ir`/call,
`small.bin`:

```
 envpad   unsafe   verus    pair
      0     3059    3065     +6
     15     3066    3058     -8    <-- BOTH FLIP, IN OPPOSITE DIRECTIONS
     63     3059    3065     +6
```

**Bistable, not monotone. The pair swings by 14.** `check_marginal_ir`'s
docstring calls `-O3 isolated` *"exactly invariant … the only cell class no
probe has moved"*, and **`synthesize.py::marginal` DEFAULTS to `O3/isolated`
because of that rule.**

**Do not re-prove this. Your job is what it COSTS.**

---

## §1 — ⚠⚠ THE AUDIT: every published pair difference under |Δ| = 14

**This is the deliverable.** The project publishes rung differences —
`R3 − R4`, `R2 − R4`, `derived_correction`, per-element rates, fitted laws — and
a `-O3 isolated` difference now carries **±7 per rung**.

1. **Enumerate every published pair difference** in `results/`,
   `patterns/*/NOTES.md` and `results/tables/`, with its magnitude and its `Ir`
   convention. ⚠ **Two conventions exist** (kernel-exclusive and whole-program
   marginal) and the exposure may differ between them — **say which are
   exposed and which are not, and why.**
2. **Flag every one whose magnitude is under 14**, and separately every one
   under 7. ⚠ **Some headline findings are small integers by design** — p01's
   *"+4…+5 instructions per call"*, p16's *"a single integer per call"*, p46's
   *"`0.00000` per-MAC tax"*. **Are those results now unresolvable, or are they
   protected by something?** ⚠⚠ **Look hard for the protection before concluding
   they are dead** — several were swept over many lengths with **zero residual**,
   and a term that is constant in `n` behaves differently under this effect than
   one that scales. **A slope may survive where a level does not.**
3. **Is the effect PER-RUNG-PAIR or PER-BINARY?** p03's `unsafe` and `verus`
   moved in **opposite** directions at the same pad. **Does a rung's direction
   depend on the rung, the pad, or their interaction?** This decides whether a
   pair difference is `±14` or something better-behaved.

## §2 — the unprobed patterns

The measurement is **`p03` only**. `TASK_097` names `p04`, `p38` and `p46` as
unprobed. **Probe at least three patterns, chosen for exposure rather than
convenience**, and say whether the effect is universal, pattern-specific, or
keyed to something (a `memset`, a panic pad, an alignment-sensitive prologue).

⚠ **`.temp/build/<pattern>/` already holds built cells** for several patterns —
check before rebuilding, and **do not run `harness/build.py`** (measurement-
hashed).

## §3 — does the layout harness answer it?

`common/layout/` exists and `p06` used it to build a **layout population** —
that is how p06's **±4.6%** floor was established, and `common/layout/data/`
ships p01's population so **finding 16 is auditable without re-measuring**.

- **Is a layout population the right instrument here**, or is the environment
  block a *different* axis from the source-path-length one p06 measured?
  ⚠ **RECAP's settled answer 1 says the R4/R5 offset "moves if you clone
  elsewhere" — that is the SAME family. Is it the same variable?**
- **What would it cost** to run it on every `-O3 isolated` pair? Give a number,
  not an adjective.
- ⚠ **Is there a cheaper instrument?** A `±7` bistable term with a known
  mechanism might be *pinned* rather than *averaged* — e.g. by fixing the
  environment the gate runs under. **If so, say exactly what would have to be
  pinned and what it would cost to re-measure.** ⚠ **`build.py` is
  measurement-hashed; `check.py` is not.** That asymmetry decides which fixes
  are cheap.

## §4 — attack the rest of `TASK_097`

- **§A's answer (`p35` is dead, the catalogue closes).** ✅ I verified
  `_is_trusted` requires `external_body` and `_TWIN_BANNED` bans it. ⚠ **But the
  four-route table is the engineer's; a fifth route is what a reviewer is for.**
  **Is there a spelling that reaches a legal `p35` that neither of us thought
  of?** If yes, that reopens the catalogue and is the most valuable thing you
  could find.
- **§B's `_verus` fix.** New stage `check.py::check_verus_exit_codes`. ⚠ **5 of
  the 11 sites are mutants that MUST exit non-zero** — **verify the new stage
  does not fire on them**, and that the mutant battery still has teeth. **The
  tautology trap has fired four times on this project.**
- ⚠⚠ **The engineer LEFT THE SWEEP'S `p03` GATE RECORD IN THE TREE** and warned:
  *"that is also the record that reproduces HEAD's `synthesis.md`, so do not read
  that byte-identity as evidence about the tree."* **Establish what the tree's
  p03 record actually is and whether anything published depends on which one is
  committed.**
- `harness/limbs.py::TWIN_BANNED` is **missing `"external_body"`** (`\bexternal\b`
  does not match it), so the re-derivation tool under-reports `5ct-cfg`.
  Reported, not fixed — **confirm.**

---

## Constraints

- **`.temp/r98/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `pilot/`, `harness/build.py` or
  `harness/asm.py`.** You are a reviewer: **do not fix anything.**
- **Do not run `harness/measure.py`** (it rewrites measurement records) and **do
  not run `harness/build.py`**. `harness/check.py` rewrites `results/gate/` in
  place — **prefer not to run it; if you must, `git checkout -- results/gate/`
  afterwards and say so.**
- Verus via `./verus_run.py`, single-file mode only.
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Give clean negatives.** A named attack that did not land is worth as much as
  a finding.

Write your report to `.tasks/TASK_098_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 291.** **The last four tasks carried it
from 270 to 291 — twenty-one contradictions, and six were against sentences I
wrote, two of them already committed into `.memory/`, the layer this project
calls authoritative.** The calls I am least sure of:

1. ⚠⚠ **That the ±7 is survivable at all.** I have landed it as *"the known
   layout population reaching the class declared immune"*, which is a framing
   that makes it sound bounded. **If a headline result is actually unresolvable,
   say so plainly — that is a finding, not a failure**, and this project's
   strongest results have come from exactly that move (`p06`'s sign-wrong `Ir`
   column, `p10`'s flattering headline).
2. **That `p03` is representative.** One pattern.
3. **That `p35` is really dead** (§4). I would rather be wrong about this one.

Carry **291** forward, incremented by what you find.
