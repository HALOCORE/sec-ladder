# TASK_099 — withdraw four published cells, and close the `include!()` hole

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.memory/03-measurement.md`'s last two sections** (the ±7 and its RESOLVED
block — reviewed and manager-verified) and **`.memory/02-bench-rules.md`'s
`include!()` section**, then `.tasks/TASK_098_REPORT.md` **BLOCKER 1, BLOCKER 2,
MAJOR 3 and §4A**.

Scratch in **`.temp/t99/`** — free, I checked.

⚠ **Both halves stale every gate record. ONE sweep, last.** ⚠⚠ **Finish every
edit BEFORE the sweep starts** — `TASK_096` edited `check.py` between p08 and p09
and went **8 STALE**.

---

## §A — ⚠⚠ THE TREE PUBLISHES FOUR CELLS THAT `.memory/` HAS WITHDRAWN

**This is a live contradiction and `.memory/` is the layer that wins.**
`results/synthesis.md:322-323`, the §2 `R5−R4` table:

```
| p03-bounded-stack | 0.00 | 0.00 | LICENSED | small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?** |
| p04-ring-buffer   | 0.00 | 0.00 | LICENSED | small +6.00 (+6.00) **?** / large +6.00 (+6.00) **?** |
```

**Over 32 consecutive environment sizes those cells take `{−8.00, −1.00,
+6.00}`** — support `+6.00` on **14** pads, `−8.00` on **14**, `−1.00` on **4**.
⚠ **The published value is not even the modal one; it is TIED WITH ITS OWN
SIGN-REVERSE.** The decomposition says what is actually left:
`R5−R4 = 0 (kernel) + memset ∈ {−7,0,+7} + (−1) (main)`, so **the reproducible
content is `−1.00`.**

⚠⚠ **DO NOT HAND-EDIT `results/synthesis.md`. IT IS GENERATED.** Fix
`synthesis/synthesize.py` and regenerate. **Three tasks in a row have shipped an
edit the generator silently reverted** (`.memory/05-layout.md`), and one of them
was the task fixing that defect.

**What to publish instead is yours to decide and justify** — the honest options,
cheapest first:

1. **Blank the cell** and say why in the footnote (it is not a figure).
2. **Publish the reproducible part only** — `−1.00`, from `main`'s exclusive
   count — and name the memset term as unresolvable.
3. **Publish the measured range** `{−8, −1, +6}` with its support.

⚠ **Whichever you choose, the `**?**` marker is now WRONG for these cells.** It
means *"look further"*, and there is nothing further to look at: **the quantity
has no value.** Say that.

### §A2 — two calibration claims that go with it

- ⚠⚠ **THE `< 2.00` BAND'S OWN CLAIM IS FALSE.** `results/synthesis.md`'s band
  table says the band is *"**safe**: nothing real hides below the floor"*.
  **p04's `R3 − R4` correction is blank at one environment phase and `±7` at
  another** — it hides in the safe band. **Restate the band.**
- ⚠⚠ **AND THE CONTROL BESIDE IT CANNOT FAIL: `64 mod 32 == 0`.**
  `results/synthesis.md:50` and `:188` rest on a second sweep taken under a
  *"64-byte-longer environment block"* — **which is the SAME alignment phase as
  pad 0**, because the period is 32. ⚠ **It is the FIFTH control in this project
  that could not have fired**, and the manager quoted it as the candidate
  protection one message before the review killed it. **Re-take it at a phase
  that actually differs (an odd multiple of 16), or withdraw the sentence.**

---

## §B — close the `include!()` hole

`include!("h.rs")` **outside** `verus!{}` verifies `1 verified, 0 errors` with
**`_scan_unsafe_sites` at 0 failures** and **`_path_includes` returning `[]`**.
`include!` is a **macro**, not a `#[path] mod`, so `_verus_file_list` — the one
deduped list `TASK_088` built so all three Verus-side detectors share a file set
— **never sees the file.**

> **`TASK_009_REVIEW`'s blocker x1 is re-opened by a different spelling**, and
> `_is_trusted` was rewritten specifically to close x1.

✅ **Bounded: 0 hits across the 24 shipped patterns** — latent, not live, the
same posture the `_verus` return-code hole had before `TASK_097` fixed it.

**Teach `_path_includes` (or `_verus_file_list`) to see `include!`.** ⚠ **Feed
all three detectors, not one** — that asymmetry *was* `TASK_084_REVIEW` major 1
and it took two tasks to close.

⚠⚠ **The acceptance test must run source → published number in ONE command and
must have an arm that FAILS.** `.temp/t97/b3_source_to_published.py` and
`.temp/t96/a7_source_to_published.py` are the working models. **A test with no
failing arm is what this project keeps catching itself building — five times
now, and §A2's control is the fifth.**

---

## §C — `check_marginal_ir`'s docstring is still wrong in a second way

`TASK_097` fixed the *"`-O3 isolated` is exactly invariant"* claim. ⚠ **Its
four-pattern exposed list is ALSO wrong**: `p38` and `p46`'s Rust rungs swing
**`0.00`** over 32 pads. **The measured exposed set is 2 patterns and 7 of 144
cells.** Correct it, and prefer a form that cannot go stale (compute it, or state
the measurement and its date).

---

## §D — the sweep

Full **24-pattern** `check.py`, then `synthesis/licence.py --emit
synthesis/licence.json` **BEFORE** `synthesis/synthesize.py` — ⚠ **mandatory
order or 24 `LICENCE STALE` verdicts publish** — then
`harness/measure.py --check-stale` (**48 records**: it globs `results/*.json`
**and** `results/gate/p*.json`).

**Expect 23 `PASS` + 1 `PASS-WITH-BLOCKED-ROWS`, 0 failures.** **If anything
turns red, STOP AND REPORT.**

⚠ **`results/synthesis.md` will move this time and that is the POINT** — §A
changes four cells deliberately. **Diff it and state exactly which lines moved**,
so the change is a result rather than a surprise.

---

## Constraints

- **`.temp/t99/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t99/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.** Report durable facts.
- ⚠⚠ **Do not touch `harness/build.py` or `harness/asm.py`**, and remember every
  rung `.rs`, `c/kernel.{c,h}`, **`model.py` and `inputs/gen.py`** are
  measurement-hashed (`measure.py::measurement_sources` globs them).
- ⚠ **Do not touch `check.py::_scan_unsafe_sites`** — that decision is landed.
- ⚠ **Do NOT "fix" the ±7 by pinning the gate's environment.** Cheap
  (`check.py` is not measurement-hashed) and **it makes the number
  reproducible-and-wrong.**
- ⚠ **A layout population is the WRONG instrument** and fails in the dangerous
  direction — callgrind is layout-blind, so it would return ≈0 on a term worth 7.
  **The right axis is `argv`/`envp` length; they are ONE axis. 32 pads ≈ 2
  min/pattern.**
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only. Cite `check.py` by **FUNCTION NAME**.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_099_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 299.** **The last five tasks carried it
from 270 to 299 — twenty-nine contradictions, and eight were against sentences
the manager wrote, three of them already committed into `.memory/`.** The calls
I am least sure of:

1. **That blanking the four cells is better than publishing the range.** I lean
   blank-plus-footnote; ⚠ **the range with its support may be more honest and I
   have not measured which a reader misuses less.** **Choose and defend.**
2. **That `include!` is the only macro route.** `include_str!`, `include_bytes!`,
   a `macro_rules!` that expands to a `#[path] mod`, and a build-script-generated
   file are all unprobed. ⚠ **If there is a sixth spelling, finding it now is
   worth more than closing the fifth.**
3. **That `0 hits across 24 patterns` bounds it.** That is a statement about
   today's tree, not about the check.

Carry **299** forward, incremented by what you find.
