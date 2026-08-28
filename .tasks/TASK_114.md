# TASK_114 — review `TASK_107`, the task that changed the INSTRUMENT

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`.tasks/TASK_107_REPORT.md` in
full**, then `.memory/03-measurement.md` (the ±7 sections and the
controls-that-could-not-have-fired list) and `.memory/00-environment.md`.

Scratch in **`.temp/r114/`**.

⚠ **YOU ARE NOT THE ONLY AGENT RUNNING.** `TASK_113` is reviewing `TASK_102`
concurrently. It is read-only and confined to `.temp/r113/`. **The consequences
for you are in the Constraints section and they are hard limits, not advice.**

---

## Why this one, and why now

`TASK_102` changed the **plan**; `TASK_107` changed the **instrument**. The
manager ranked the plan first and said in `TASK_113` that the call was arguable.
**Rather than argue it, both are being reviewed. This is the instrument half.**

`TASK_107` is unreviewed and **everything published rests on it**: it rewrote
`_path_includes`, added two gate stages, added `marginal_ir_env` to all 26
records, changed Miri's configuration tree-wide, and **moved a published claim**
(`results/synthesis.md`'s `< 2.00` band went `0 real / 143 spurious` →
`4 real / 139 spurious`).

✅ **Start from the presumption that this is a GOOD report.** It contradicted
four manager premises with measurements, it caught and documented its own probe
artefact, and it reversed its own first answer on `MIRIFLAGS` when the sweep
refuted it. **That is exactly what this project asks for.** ⚠ **Which is why the
question is not "is it sloppy" but "what could a careful agent doing all that
still not have caught".** It told you where to look — §"What I did NOT do" has
seven entries and **items 2, 4, 5 and 6 are live holes the author names himself.**

## §A — ⚠⚠ THE `tuning_vars` COMPLETENESS HOLE. THIS IS THE DELIVERABLE.

The new record field licenses a **rule**, written into `check.py::main()`:

> same `bytes` **and** same `tuning_vars` ⇒ the marginal must match **EXACTLY**.

⚠ **That is a universally-quantified claim over environments, supported by ONE
measurement in the other direction.** The author says so (item 4): *"it is
derived from one measurement, and I have not shown it is complete."*

**One counterexample kills it, and a killed rule here is a real correction to a
field now in all 26 committed records.** The cheapest shapes to try, in order:

1. ⚠⚠ **Same length, same `tuning_vars`, DIFFERENT CONTENT.** The `+486.00`
   counterexample used `GLIBC_TUNABLES`, which the prefix set catches. **Try
   content the prefix set does NOT catch**, at a byte-identical child block
   length: reorder two variables; change a value's bytes without changing its
   length; vary `LANG`/`LC_ALL`, `TZ`, `PATH` contents, `HOSTNAME`. ⚠ **If ANY
   of these moves the marginal at identical `bytes` and identical `tuning_vars`,
   the rule as written is FALSE.**
2. **Env ORDER at fixed length and fixed content-multiset.** Pure permutation.
   ⚠ **This is the sharpest arm** — it holds `bytes` and `tuning_vars` exactly
   fixed by construction, so the rule *must* predict an exact match, and it needs
   no argument about what counts as a tuning variable.
3. **`argv`, which the report explicitly excludes** (*"valid within one clone
   location"*). ⚠ **Is that restriction stated anywhere a reader of the RECORD
   would see it, or only in a report and a docstring?** A pin whose domain lives
   only in prose is the `p05` failure mode.

**Use `p03`** — the report's own vehicle, `unsafe`, `-O3 isolated`, `small.bin`;
its `memset`-per-call is what makes it sensitive. ⚠ **Callgrind `Ir` is
deterministic and immune to the other agent's load — this whole section is safe
to run concurrently.**

⚠ **Every arm needs a partner that MUST FIRE.** Re-deriving the author's
`+486.00` (or the `±7` pad ladder) is your positive control: if your rig cannot
reproduce a known mover, a null result from it means nothing.

## §B — `MIRIFLAGS`: an unexplained 4.6×, and a blast radius of 20 untested patterns

**The effect:** the variable's **presence** — even `MIRIFLAGS=""` — costs ≈4.6×,
seven settings, one effect, **no mechanism** (item 2). The landed answer is
`MIRI_FLAGS = ()`, which **strips an ambient `MIRIFLAGS` from the child.**

1. ⚠ **Get the mechanism if you can.** ⚠⚠ **But `.memory/`'s standing rule is
   that an unexplained effect stays unexplained until measured — DO NOT WRITE A
   MECHANISM YOU HAVE NOT RUN.** The report says so in bold and it is right.
   Cheap discriminators: does `cargo miri` re-invoke/rebuild when the variable is
   set (a `MIRIFLAGS` change is part of cargo's fingerprint — **is the 4.6% a
   rebuild rather than a slower interpretation?**); is the cost per-run or
   per-build; does it survive a warm target dir?  ⚠ **If it is a REBUILD, the
   whole framing changes** — 4.6× on a 74 s row is ~270 s of *compilation*, and
   the fix would be a warm cache, not an unset variable.
2. **Item 6: the blast radius outside `p42` is unmeasured — 20 patterns.**
   ⚠ **The decision was taken on one pattern's row.** Spot-check a handful.
3. ⚠⚠ **The author's own first measurement does not reproduce** (`72.8 / 73.8 /
   73.6 s`, contradicted by three later repeats and the gate twice). **He recorded
   the disagreement rather than a mechanism, which is correct — but an
   unreproducible measurement in the same family as the one that decided the
   design deserves one more look.**
4. **Is `miri_version` really "the substantive replacement for the seed"?**
   The determinism claim rests on *"five timings agree to 1.9%"* and
   *"`base % 4 == 3` reproduces"*. ⚠ **`base % 4` is two bits. That is a weak
   witness for "deterministic address assignment".** Probe the full base address
   across many launches. **If it is not deterministic, a green Miri row is still
   a claim about an unrecorded draw** — the exact defect §C set out to fix.

⚠ **Miri timings are WALL CLOCK and the other agent is running.** The 4.6× is far
outside any plausible load effect on an 80-CPU box at load ~2 — but **repeat
anything that decides something, and say in your report that a second agent was
running.**

## §C — the `_path_includes` union: is the method as good as the result?

✅ **The finding is right and the reasoning is the best thing in the report:**
dep-info is exact for what rustc resolves; the regex over-approximates and is
cfg-blind and macro-blind; **replacing would have closed three routes and opened
three, and the three it opened live inside `verus!{}`, which every R5 is written
in.** Union 13/13, either limb alone 10/13.

**So attack the two things the result does not settle:**

1. ⚠⚠ **A FOURTEENTH ROUTE. THE PRIOR IS STRONG THAT ONE EXISTS** — *"nine
   routes found by three separate tasks, each after the previous table read as
   exhaustive."* **Try: `#[path]` reached through a `macro_rules!` INSIDE
   `verus!{}`; an `include!` chain (`include!` of a file that itself `mod`s); a
   SYMLINK; `#[cfg_attr]` nested in `#[cfg_attr]`; a path with `..` or a
   non-UTF-8/space-bearing name.** ⚠ **A route the UNION misses is a genuine
   finding; a route only one limb misses is not — that is the design.**
2. ⚠⚠ **THE CHANGE IS INERT ON THE SHIPPED TREE AND THE REPORT SAYS SO**: all 26
   patterns return exactly `['common/driver.rs']`, dep-info **adds 0 and misses
   0**. ⚠ **So every end-to-end acceptance arm ran on a PLANTED tree and no real
   pattern exercises any route.** **Say whether "blast radius zero" is
   reassurance or is the observation that the new limb does nothing yet.**
3. **Fail-closed:** `_dep_info_files` returns `(None, err)` ⇒ the gate FAILS. The
   claim that makes this safe is *"rustc emits the `.d` even when compilation
   fails."* ⚠ **Is that true for ALL failure modes** — a lex error, an unreadable
   file, a `#![no_std]` root, an empty file? **Find a source rustc rejects
   without writing a `.d` and you have found a way to turn a valid pattern's gate
   red.**
4. **Hygiene:** the scratch `.d` is written somewhere and was pid-tagged
   mid-task. ⚠ **Where does it land, is it removed, and could it be left inside a
   `patterns/*/` directory** — i.e. inside a hashed tree, or as an untracked file
   a later `git add -A` would sweep up?

## §D — the published claim that MOVED, and the two files that now lie

1. ⚠⚠ **`results/synthesis.md` now prints `4 miss` where it printed `0`, in what
   the file itself calls *"the dangerous direction"*.** The author attributes it
   completely to the `p03`/`p04` ±7 cells, **row by row, which is good work** —
   but **item 5 says he did not re-run the 32-pad sweep to confirm this run's
   phase.** ⚠ **Confirm or refute the attribution.** `Ir`-only, safe to run.
   ⚠ **And the second-order question is the one that matters: the band's
   rehabilitated claim now has a MEASURED counterexample rather than an argued
   one. Does any published sentence still assert the pre-move version?**
2. **Item 7 names two files that now state things that no longer hold** —
   `.memory/00-environment.md`'s seed sentence (the *"clean under 0 and 2, UB
   under 1 and 3"* premise, **which did not reproduce**) and
   `p42`'s `spec.md::miri.blocked_reason`. ⚠ **Both are manager-only; the author
   correctly flagged and did not touch them.** ✅ **Check whether the manager has
   since landed them. If not, say so precisely — the exact sentence, the exact
   file — so the manager can land it in one edit.** ⚠ **`spec.md` is inside
   `contract_sha256`, so say whether the fix costs a gate re-run.**

## §E — the cheap structural questions

- **The gate is now 20 stages.** Stage 9 `MISSING` makes a brand-new pattern's
  **first** gate run FAIL until `report.py` has run. ⚠ **Is that ergonomic cost
  correctly judged as small, given the project may build no further patterns?**
- **`check_control_json_pins` SHOUTS on `UNPINNED` rather than failing**, because
  the author was forbidden to write the generator. ⚠ **A shout nobody reads is a
  check that cannot fail** — that is a named class in this project. **Is `p23`'s
  `UNPINNED` visible anywhere a reader would see it?** *(The writer is a known
  owed item; you are judging the SHOUT, not the missing writer.)*
- **`limbs.py` now imports `check._TWIN_BANNED` instead of copying it.** ✅ Right
  fix. ⚠ **Are there other copies of a `check.py` constant elsewhere that can
  drift the same way?** One `grep` settles it.

---

## Constraints

- **`.temp/r114/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file. You are a reviewer.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py` or `measure.py`** (except
  `measure.py --check-stale`). **A gate run rewrites `results/gate/*.json`, which
  the concurrently-running `TASK_113` is READING.** ✅ **Instead, import
  `harness/check.py` as a module into a probe under `.temp/r114/` and call
  `_path_includes`, `_dep_info_files`, `_check_opaque_includes`, `_env_block`
  directly on synthetic trees you build there.** ⚠ **That is the better review
  technique anyway: it isolates the unit from the sweep, and the engineer's
  end-to-end arms already ran.** **If you conclude something can only be settled
  by a real gate run, SAY SO and stop — that is a follow-up task, not your job.**
- ⚠ **Never plant into a tracked file.** Build synthetic trees under `.temp/r114/`.
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal — doing so is itself a documented
  failure, committed five times by the manager after writing the rule against
  it.** ⚠ **And note entry 3 is `limbs.py::TWIN_BANNED`, which §E asks about.**
- Hand-run sanitizers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`.
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_114_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 414, and `TASK_113` was launched from the
same value in parallel.** ⚠ **Report YOUR increment as a branch delta —
*"414 + N on this branch"* — and do not try to reconcile with the other agent.
Reconciliation is the manager's job, and `TASK_107_REPORT` closed with exactly
that note for exactly this reason.**

The calls I am least sure of:

1. ⚠⚠ **That `TASK_107` needs reviewing at all.** It is the most self-critical
   report in the project: it refuted four of my premises, refuted **its own**
   first answer, documented a probe artefact it created, and listed seven things
   it did not do. ⚠ **If your honest finding is "this is sound, the holes are the
   ones it names, and here is which of the seven is worth a task", SAY THAT** —
   a clean review of a good task is a real result and this project has too few
   of them.
2. **That §A's `tuning_vars` hole is the most valuable target.** I picked it
   because it is a **universal rule resting on one measurement**, it is now in 26
   committed records, and a permutation arm settles it in one command. ⚠ **If
   §B's unexplained 4.6× matters more — it changed Miri's configuration
   TREE-WIDE with no mechanism — go there first and say why.**
3. ⚠ **That reviewing the instrument is worth a task at all versus declaring the
   project done.** ⚠⚠ **`TASK_113` is arguing the mirror-image question about the
   PLAN. If your answer is "the instrument is fine, stop polishing it", that is a
   perfectly good answer** — and combined with whatever `113` returns it may be
   the honest end of this programme.

Carry **414** forward, incremented by what you find, **as a branch delta.**
