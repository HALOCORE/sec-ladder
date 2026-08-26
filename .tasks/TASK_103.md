# TASK_103 — review `TASK_099`, and the claim that must not stand unchecked is C7

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then `.tasks/TASK_099_REPORT.md` **in
full**, then `.memory/03-measurement.md`'s ±7 sections (⚠ **the manager has
already landed TASK_099's retractions there as PROVISIONAL — so if you refute
one, you are refuting the AUTHORITATIVE LAYER, and that is exactly what this
task is for**).

Scratch in **`.temp/r103/`**.

---

## Why this review is urgent rather than routine

`TASK_099` returned **eight contradictions, two of them blockers against
sentences the manager had committed into `.memory/`**. ⚠⚠ **The manager landed
both retractions into `.memory/` BEFORE this review, on the argument that leaving
a known-false claim in the authoritative layer is worse than marking it
PROVISIONAL.** That argument may be right, **but it means a wrong retraction is
now sitting in the layer that supersedes everything else.** ⚠ **`PROTOCOL` rule 9
exists precisely to stop unreviewed findings landing there, and the manager made
an exception. Test the exception.**

✅ **One of the two is already independently confirmed and you may take it as
settled:** C1's `87` decomposes exactly as `8` (envp pointer slot) `+ 13`
(`SLB_ALIGN_PAD`) `+ 1` (`=`) `+ 64` (pad) `+ 1` (NUL), and `87 mod 32 = 23`.
**Manager-verified by arithmetic. Do not spend time re-deriving it.**

**C7 is the one that matters and it is NOT confirmed.**

---

## §A — ⚠⚠ C7: "the ±7 is selected by HOW THE GATE WAS LAUNCHED"

`TASK_099` reports **three whole-gate `check.py p03` runs on an unchanged tree,
no environment variable set, environment block identical at 3672 bytes down every
path, client stdio inert** — giving **`A = C ≠ B` on 3 of 4 cells**, `unsafe +7`
and `verus −7`, so `R5 − R4` moves **`+6.00 → −8.00`**.

**The consequence it draws is a METHOD claim, and it is why this must be right:**

> ***"Re-run the gate and compare" is not a reproduction test for these cells.***

⚠ **That invalidates an argument this project has used as evidence at least
twice**, including a byte-identical-`synthesis.md` claim in a commit message.
**If C7 is right it is one of the most important results in the file. If it is
wrong, the manager has just broken a true sentence in `.memory/`.**

**Attack it. Named ways it could be wrong, and there will be others:**

1. ⚠⚠ **`n = 3` with a claimed pattern of `A = C ≠ B` is one bit of evidence.**
   **Run it enough times to distinguish "launch method selects the phase" from "a
   two-state term flips at some rate under identical launches."** Those are very
   different claims and the second is much weaker. **If it is the second, C7's
   method conclusion still survives** — an unreproducible cell is unreproducible
   either way — ⚠ **but the stated MECHANISM would be wrong, and a wrong
   mechanism in `.memory/` is what rule 9 protects against.**
2. **Is the environment really identical?** `3672 bytes` was measured — **how,
   and at what point?** A shell function, an exported `_`, `SHLVL`, `OLDPWD` or
   the terminal's `COLUMNS`/`LINES` differ between an interactive shell and a
   spawned one **and can change between two runs in the same shell.** ⚠ **The
   previous claim in `.memory/` was that env LENGTH is the whole story; C7 says
   it is not. Settle it by measuring `/proc/<pid>/environ` of the actual
   callgrind child, not of the launching shell.**
3. **What else differs between runs that is not the environment?** The `auxv`
   (`AT_RANDOM`, `AT_EXECFN`), the stack randomisation, the argv **contents**
   (an absolute vs relative path is a different length), and **the current
   working directory**, which lands in the same page as argv/envp. ⚠ **CWD is the
   one the manager would bet on and has not tested** — the project already knows
   the R4/R5 offset is a **source-path-length** artefact (RECAP settled answer 1).
   **Is C7 just that, seen from a different angle?**
4. ⚠ **Is `kernel_exclusive_ir` really immune?** `.memory/` now says it is
   structurally immune, `0 of 288 triples`, and the manager has just told readers
   to **reproduce against that column instead**. **If that immunity has a hole,
   the advice is worse than the problem.** **Test it directly across your runs.**

**Then answer: what IS a valid reproduction test for an `-O3 isolated` marginal
in this tree?** ⚠ **That is the deliverable of §A, more than a verdict on C7.**
The honest options include pinning nothing and quoting a range, reproducing only
`kernel_exclusive_ir`, or declaring the column unreproducible and saying so in
`synthesis.md`. **Pick one and defend it.**

## §B — the `check.py` changes

`_path_includes` is now a **transitive fixed point**; `_check_opaque_includes` is
new; `_scan_unsafe_sites` was correctly left alone.

- ⚠⚠ **Does the fixed point TERMINATE on a cycle?** `a.rs` includes `b.rs`
  includes `a.rs` is legal to write and a naive fixed point hangs the gate.
  **Build it and run it.** A gate that hangs is worse than a gate that misses.
- **Does `_check_opaque_includes` FALSE-POSITIVE?**
  `include!(concat!(env!("OUT_DIR"), "/gen.rs"))` is *the* standard build-script
  idiom. It is correctly refused as unresolvable — ⚠ **but is the failure message
  good enough that a future author knows what to do**, and is a legitimate use
  now impossible? **0 patterns use it today, so this is latent; say how it bites
  when it does.**
- ⚠ **The report discloses `_path_includes` still tests `exists` and not
  `isfile`**, found after the sweep started and deliberately not edited
  mid-sweep. **Is a directory named `foo.rs` reachable, and what happens?**
- ⚠ **A SEVENTH route.** Six are now closed (four macro spellings, transitive
  `#[path]`, and `macro_rules!`-emitting-`#[path]` which was already caught).
  **`TASK_099` found the sixth after the manager said there were five.** ⚠ **Look
  for the seventh — `#[cfg_attr]`-gated `#[path]`, a `mod` inside a function
  body, `#[cfg]`-selected paths, or a symlink — and if you find one, that is the
  most valuable thing in this task.**

## §C — the withdrawal, and the rest

- **Did any NUMBER move that should not have?** The report claims **0
  `marginal_ir_per_call` keys moved across 24,179 gate leaves**, with 24
  `source_sha256`, 40 ASan PIDs and 95 pre-existing UB-cell rows accounted for.
  ⚠ **Verify the accounting rather than the headline** — *"nothing moved"* has
  been quoted past a real change in this project before, and the sharpest case
  was a byte-identical file whose generator could not see the field at all.
- ⚠ **Three `synthesis/`-only text edits landed DURING the sweep**, disclosed,
  with a hash-glob argument that `synthesis/` is in neither hash set. **Check
  that argument.** `TASK_096` edited `check.py` mid-sweep and went 8 STALE.
- **C3 said the exposed set is 3 patterns, not 2, `p46`'s `c-clang` being the
  seventh cell.** ⚠ **Confirm the seven and name them** — the manager has now
  published "7 of 144 across three patterns" twice and has never listed them.

---

## Constraints

- **`.temp/r103/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/r103/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `pilot/`, `harness/`, `synthesis/`,
  `results/` or any `patterns/*/` file.** You are a reviewer: **do not fix
  anything.**
- ⚠ **`harness/check.py` rewrites `results/gate/` in place.** You will need to run
  it for §A. **`git checkout -- results/gate/` afterwards and say that you did.**
  **Do not run `harness/measure.py` or `harness/build.py` at all.**
- ⚠ **`env -u LD_PRELOAD` for hand-run sanitizers; `grep` logs, never `head`.**
- **Every probe needs an arm that must fire.** ⚠ **Five controls in this project
  could not have failed, and the most recent was an alignment argument computed
  from the PROSE describing a control instead of from the bytes the process
  receives.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Give clean negatives.** A named attack that did not land is worth as much as
  a finding.

Write your report to `.tasks/TASK_103_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2: this task is launched from 309**, and ⚠ **`TASK_100` and
`TASK_102` are in flight from 301 and 309 respectively. Reconciliation is the
MANAGER'S job — state what you found and what you started from, and do not
compute a global total.** The calls I am least sure of:

1. ⚠⚠ **That landing TASK_099's retractions into `.memory/` before this review
   was the right call at all.** I broke rule 9 deliberately and said so in the
   commit. **If C7 is wrong, that decision put a false sentence into the
   authoritative layer and the correct answer was to wait.** **Say so plainly if
   that is what you find** — the process verdict is worth as much as the
   technical one.
2. **That C7's mechanism ("the launching method") is right rather than just its
   conclusion ("these cells do not reproduce").** §A.1 is how they come apart,
   and I think the conclusion is much better supported than the mechanism.
3. **That `kernel_exclusive_ir` is the column to reproduce against.** I have told
   readers to rely on it on the strength of `0 of 288 triples`, **which is one
   sweep on a subset of patterns.**

Carry your own count forward and say what it was.
