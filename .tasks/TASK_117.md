# TASK_117 — review `TASK_106`: `p23`, finding 38, and a ratio that may not survive its own caveat

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 38 in
full**, then `.tasks/TASK_106_REPORT.md`, then `.tasks/TASK_105_REPORT.md` (the
review `106` was landing), then
`patterns/p23-partition/{NOTES.md,spec.md,controls/}`.

Scratch in **`.temp/r117/`**.

⚠ **YOU ARE NOT THE ONLY AGENT RUNNING.** `TASK_114`, `TASK_115` and `TASK_116`
are live in `.temp/r114/`, `.temp/t115/` and `.temp/r116/`. **See Constraints.**

---

## Why this one

`TASK_113` triaged fifteen unreviewed tasks to three. This is the third:
**`RECAP` finding 38 is explicitly marked *"PROVISIONAL where it rests on
`TASK_106`, which is unreviewed"*.** `p23` is the 25th pattern and finding 38 is
one of the project's better results — **and it is also the finding that carries
the most self-disclosed fragility in the file.**

## §A — ⚠⚠ DOES THE 3.11× SURVIVE THE FINDING'S OWN CAVEAT? THIS IS THE DELIVERABLE.

**Finding 38's headline:** `R3 − R4` runs **`227.00 → 706.37 Ir`/call, a factor
of `3.11`**, with element count, record count and bytes copied all fixed and only
the pivot's **rank** moving.

**Finding 38 also says, sixty lines later:** a tautological conjunct restores a
cheaper in-contract R3 spelling that compiles to **the same object code**, the
in-contract R3 floor drops **`150.00 Ir`/call**, and ⚠ **"≥150 of the published
safe-side figure is SPELLING, NOT SAFETY"** — and the in-contract R3 floor ends
up **`59.00` BELOW** the in-contract R4 spelling, **so the two spans OVERLAP.**

⚠⚠ **PUT THE TWO TOGETHER AND THE HEADLINE MAY MOVE A LOT.** If the spelling
term is uniform across pivot rank, the tax at the endpoints is
`227 − 150 = 77` and `706 − 150 = 556`, and **the ratio is ≈7.2×, not 3.11×.**
If it is not uniform, the ratio is something else again. **Either way the
published `3.11` is a property of TWO SHIPPED SPELLINGS, not of the pattern.**

**Measure it.** ⚠ **Is the 150 constant in the pivot rank, or does it vary?**
**That single question decides whether `3.11×` is a fact about `p23` or about
what someone thought to write.**

⚠ **This is `p23`'s OWN rule turned on itself** — *a number quoted without its
rank is quoted without its domain* — **applied to the SPELLING axis instead of
the data axis.** ⚠ **And `p23` already broke its own rule once, on its C row.**

⚠ **If the ratio moves, say what the honest headline is.** ⚠⚠ **But do NOT
overcorrect into "so there is no shape effect" — `up + dn == mbytes` exactly at
all 109 shipped points and `sw` alone fits `0.0132`, so the SHAPE axis is real
even if its magnitude is not what is published.** **Separate the two.**

## §B — the law, and whether its fix is blind in a new place

The published law is

> `R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ_records τ(m mod 4)`,
> `τ = {0→0, 1→2, 2→3, 3→4}`, max |residual| `0.0000` over 109 shipped points.

⚠⚠ **THIS IS THE FOURTH LAW. THREE EARLIER ONES HAD ZERO IN-SAMPLE RESIDUAL AND
WERE WRONG**, all three because every band sat at `m ≡ 0 (mod 4)` and `τ` was
invisible. **The project calls this the residue-class trap and this is its third
pattern.**

1. ⚠⚠ **ASK THE QUESTION THAT CAUGHT THE FIRST THREE, ABOUT A DIFFERENT
   PARAMETER.** `τ` was found because someone finally varied `m mod 4`.
   **What is `recs`, `dn`, `sw` or `rounds` held at, and is any of THEM
   residue-degenerate across all 109 points?** ⚠ **A law repaired for one
   residue blindness is not thereby residue-complete** — and the natural failure
   is to fix the parameter you were burned on and not check the others.
2. **Is `rounds` independently defined, or is it a function of the others?** A
   term that is a linear combination of the rest can absorb an error and give a
   perfect fit for the wrong reason. ⚠ **Check the design matrix for collinearity
   before believing `0.0000`.**
3. ⚠ **`controls/sweep_fit.py` samples `want_m = [2,4,8,16,24,32,40,48]` — SEVEN
   OF EIGHT MULTIPLES OF FOUR**, leaving one non-zero residue. **That is the
   control for the very trap this pattern discovered, and it is still
   residue-degenerate.** **Say whether the shipped 109 points fix that or inherit
   it.**
4. ✅ **A genuine out-of-band prediction is the only test that has ever caught
   this.** **Run one:** pick `m` values in residues the shipped set under-samples,
   predict before measuring, and report predicted-vs-measured. ⚠ **Register the
   prediction in your notes BEFORE you measure it** — this project's one
   out-of-sample test that can fail has failed once already (`p38`).

## §C — did `TASK_106` actually land `TASK_105`?

**Standard landing review, and it is cheap.** Take `TASK_105_REPORT.md`'s
findings list and check each one **in the tree**, not in the report.
⚠ **`TASK_106`'s own report is not evidence that a correction landed** — this
project has a documented case of a commit message claiming a fix whose
exact-match edit had silently failed.

⚠ **Pay attention to the hashed block.** `spec.md`'s `slb-contract` fence is
inside `contract_sha256`; prose outside it is not. **Say whether any correction
that needed to be inside the fence landed outside it**, which would make it
unenforced. ⚠ **Recall that `p42` shipped a `spec.md` claiming three things were
pinned when NONE of the three was enforced, including the idiom the pattern is
named for** — and that **a `required` entry with NO BACKTICKS PINS NOTHING**,
while **every backtick in an `idiom` entry IS a pin, including inside
explanatory prose.**

## §D — the owed item, and it is `p23`'s

`patterns/p23-partition/controls/sweep_fit.json` is **the only `controls/*.json`
in the tree** and it is **UNPINNED** — `check.py::check_control_json_pins`
(stage 9b) SHOUTS rather than failing, because `TASK_107`'s engineer was
forbidden to edit a generator under `controls/`.

⚠ **You are a reviewer and must not fix it either.** **But say precisely what the
fix is**: which generator writes the file, which key it must carry
(`synthesis/licence.json` is the shape to copy — it carries the gate
`source_sha256` it was taken against), and confirm the cost. ✅ **The manager has
verified `controls/*.py` is in the GATE record's `source_sha256` and NOT in
`measure.py::measurement_sources` — the glob there is non-recursive — so this
costs one gate re-run and no re-measure. Check that independently.**

⚠ **And say whether the SHOUT is visible anywhere a reader would see it.** **A
shout nobody reads is a check that cannot fail, which is a named class here.**

---

## Constraints

- **`.temp/r117/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file. You are a reviewer.** ⚠⚠ **To measure an
  alternative spelling, COPY the rung into `.temp/r117/` and edit the copy** —
  every rung `.rs`, `c/*`, `model.py` and `inputs/gen.py` is
  **measurement-hashed**, so an in-place edit stales the committed record.
- ⚠⚠ **DO NOT RUN `harness/check.py`, `harness/build.py` or `harness/measure.py`**
  (except `measure.py --check-stale`) — three other agents are reading
  `results/gate/*.json`. **Use direct `clang`/`gcc`/`rustc` and `valgrind
  --tool=callgrind` under `.temp/r117/`.**
- ⚠ **Callgrind `Ir` is deterministic and immune to the other agents' load.**
  Wall clock is not.
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal — doing so is itself a documented
  failure, committed five times by the manager after writing the rule against it.**
- ⚠ **Name the OPTIMISATION LEVEL, the INLINE MODE and the `Ir` CONVENTION at
  every figure.** Finding 38's law is `-O3 isolated`, kernel-exclusive,
  debug-assertions **off**. **A figure without those four is not comparable.**
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_117_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 425.** ⚠ **`TASK_114`, `115` and `116`
are running concurrently. Report YOUR increment as a branch delta — *"425 + N on
this branch"* — and do not reconcile with them. Reconciliation is the manager's
job.**

The calls I am least sure of:

1. ⚠⚠ **That `3.11×` survives §A.** I think it does not, and I think the honest
   number is larger — **which would mean the published headline UNDERSTATES the
   effect while resting on the wrong quantity.** ⚠ **That is an unusual
   direction for this project's errors and I may be reasoning backwards. Run it.**
   **If the 150 is not uniform in the pivot rank, my whole arithmetic is wrong
   and I want to know that.**
2. **That the law is worth attacking at all.** ⚠ **It has `0.0000` residual over
   109 points AND a genuine out-of-band holdout, which is more than almost
   anything else here.** ⚠ **But three previous versions also had zero in-sample
   residual, so "zero residual" has a bad record on this exact pattern.**
   **If §B's design-matrix check comes back clean, that is a real clean negative
   and I will record it as one.**
3. ⚠ **That `TASK_106` needs reviewing rather than closing.** `TASK_113` closed
   nine of fifteen as superseded or self-checking, with a reason for each.
   ⚠ **If `106` is a straightforward landing whose corrections are all verifiably
   in the tree, SAY SO AND STOP** — that clears finding 38's PROVISIONAL marker
   honestly, and it is the last of the three.

Carry **425** forward, incremented by what you find, **as a branch delta.**
