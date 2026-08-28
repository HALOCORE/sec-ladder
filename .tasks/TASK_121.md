# TASK_121 — the LAST owed item: a published sidecar nothing can tell is stale

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`harness/check.py::_check_controls_json`'s docstring (stage `9b` — ⚠ **cite it by
FUNCTION NAME, never a line number**), then `.memory/05-layout.md`'s sidecar
section, then `patterns/p23-partition/controls/sweep_fit.py` in full.

Scratch in **`.temp/t121/`**.

⚠ **RUN AFTER `TASK_119`.** Both move gate records. **`TASK_119` sweeps all 26;
this one needs `harness/check.py p23` ONLY** (see §A.3), so ordering it second
costs one pattern's gate run rather than a second full sweep.

---

## ⚠⚠ EVERY PREMISE BELOW WAS RUN BY THE MANAGER BEFORE BEING WRITTEN HERE

**PROTOCOL rule 14. The commands are given so you can re-run them, not so you can
trust them** — ⚠ **and the manager already got one of these wrong once in this
same session and corrected it (see §A.2). Re-run them.**

| premise | how it was checked |
|---|---|
| `sweep_fit.json` is the ONLY `.json` sidecar in any `controls/` | `ls patterns/*/controls/*.json` |
| **it HAS a generator** — ⚠ the queue said *"a reader and no writer"* and that was **wrong** | `sweep_fit.py`'s `json.dump` |
| stage `9b` reads it, keys on `gate_source_sha256`, and **SHOUTS rather than fails** when absent | its own docstring + `rep.shout` |
| `controls/*.py` is in the GATE record's `source_sha256` and **NOT** in `measurement_sources` | ⚠ **read the glob in `harness/measure.py::measurement_sources`, not the docstring asserting it** |
| ⚠⚠ **`SKIP_INPUT_PREFIX = "sweep-"`, so `inputs/sweep-*.bin` is hashed by NEITHER `source_sha256` NOR `input_sha256`** | `grep -n SKIP_INPUT_PREFIX harness/measure.py` |

## §A — THE PIN. ⚠ THE OBVIOUS ANSWER AND THE MANAGER'S SECOND ANSWER ARE BOTH WRONG.

`p23`'s `sweep_fit.json` carries **26 measured rows and two fits**, quoted in
`patterns/p23-partition/NOTES.md`. **Nothing in the tree can tell whether those
numbers were taken against the sources that are in the tree now.**

**1. ⚠ The obvious fix is wrong and `.memory/05-layout.md` already says why.**
Pinning against the **gate** `source_sha256` would stale the sidecar on every
later `NOTES.md` prose edit and demand ~30 minutes of callgrind to clear it. **A
pin that fires on prose is a pin that gets switched off.**

**2. ⚠⚠ THE MANAGER'S REPLACEMENT WAS ALSO WRONG, AND IT IS THE INSTRUCTIVE ONE.**
The manager wrote into `RECAP.md` that the narrower digest *"has a name:
`measurement_sources`"* — **and that is incomplete in exactly the shape
`TASK_114` had just falsified on the environment pin: a digest that explains most
of the dependency and silently misses one term.**

```
sweep_fit.py's numbers depend on:
   p23 *.rs, c/*            -> in measurement_sources   ok
   harness/build.py, asm.py -> in measurement_sources   ok
   inputs/sweep-*.bin       -> in NEITHER digest        <-- THE MISSED TERM
```

**`SKIP_INPUT_PREFIX = "sweep-"` is CORRECT for `measure.py`** — it never
measures those blobs, so they cannot change a number in *its* record. ⚠ **It is
wrong only for a sidecar that DOES measure them.**

**3. So the design call is yours, and it is a real one. State it, defend it, run it:**

- **(a)** hash the sweep blobs the script actually opened, or
- **(b)** hash `inputs/gen.py` alone and accept the gap — ⚠ **but `measure.py`'s
  own comment already rejects that reasoning for matrix blobs:** *"the generator
  hash cannot tell 'the inputs changed' from 'a comment changed'"*. **If you pick
  (b), you must say why the argument that fails for matrix blobs succeeds here.**
- ⚠ **And WHICH KEY**: stage `9b` currently keys on `gate_source_sha256`. **If
  the pin is no longer the gate digest, that key name becomes a lie** — rename
  it, or make the stage accept a named alternative. **Do not leave a key whose
  name says one thing and whose contents say another; this project has a finding
  about exactly that.**

**4. ⚠⚠ ACCEPTANCE NEEDS AN ARM THAT FIRES, AND THE STAGE MAKES THIS EASY:**
stage `9b`'s **mismatch half already FAILS** (only the *absent* case shouts).
**So: stamp the pin, confirm the gate is green, then perturb ONE hashed input and
show `check.py p23` goes RED.** ⚠ **Then perturb something that must NOT stale it
— a `NOTES.md` word — and show it stays green.** **Both arms, or the pin is
untested.** ⚠ **A field that merely exists is not a fix** (`TASK_119` §A's lesson,
one task earlier).

## §B — ⚠ THE GENERAL FORM, AND IT IS WHY THIS IS WORTH A TASK AT ALL

**One sidecar is a chore. The class is the finding.** `.memory/`'s own rule is
*before quoting any number, `measure.py --check-stale`* — **and that command
cannot see this file.**

**So: `grep` the tree for OTHER published artefacts that carry numbers and no
staleness pin.** Candidates to check, and add any you find:

- `patterns/*/controls/*.log` — **`p23` ships `controls.log`**; is anything in it
  quoted?
- `synthesis/licence.json` — ✅ **this one is the SHAPE TO COPY** (it carries its
  digest and `synthesize.py` prints `LICENCE STALE`). **Confirm it still works;
  do not assume.**
- `results/tables/*.md` — generated, pinned via stage 9. **Confirm.**
- ⚠⚠ **THE BIG ONE, AND THE MANAGER HAS MEASURED IT SO YOU DO NOT HAVE TO
  RE-DERIVE IT — ONLY DECIDE IT.** `.temp/` is **gitignored** (`.gitignore:3`),
  and the authoritative layer cites it **105 times**: `RECAP.md` 31,
  `.memory/06-catalogue.md` 28, `00-environment.md` 17, `03-measurement.md` 12,
  `05-layout.md` 10, `01-ladder.md` 3, `04-verus.md` 2, `02-bench-rules.md` 2.
  ✅ **`results/SYNTHESIS.md` cites it ZERO times — the outward document is
  clean, which is the good news and probably not an accident.**

  ```
  67 distinct .temp/ paths cited by RECAP.md + .memory/
  65 exist on this box   (the 2 "missing" are the `pNN` doc PLACEHOLDERS,
                          not real citations -- a CLEAN NEGATIVE)
  1.2 MB total for all 65
  ```

  ⚠ **So there are no dangling citations ON THIS BOX. The defect, if it is one,
  is that NONE OF THE 65 IS IN THE REPOSITORY** — a fresh clone can check no
  claim in the authoritative layer that rests on them, **and there is a GitHub
  remote.**

  ⚠⚠ **DO NOT COMMIT ANYTHING UNDER `.temp/` — THIS IS A REPO-POLICY DECISION
  THAT BELONGS TO THE USER AND THE MANAGER IS SURFACING IT, NOT TAKING IT.**
  `CLAUDE.md` rule 1 puts evidence in `.temp/` deliberately and rule 3 says
  checks run locally, so *"local artefact by design"* is a coherent reading.
  **Your job is to state the trade-off with the numbers above and RECOMMEND —
  not to act.** ⚠ **1.2 MB is small enough that "too big" is not the argument;
  if you want to argue against, argue the policy.**

⚠ **Report the LIST even if you fix only `p23`.** **An undocumented hole is how
this project found routes ten and eleven** (`TASK_119` §C).

---

## Constraints

- **`.temp/t121/` only. No `/tmp`.** **Notes in `.temp/t121/NOTES.md` AS YOU GO.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never edit it.**
- ✅ **You MAY edit `patterns/p23-partition/controls/*` and `harness/check.py`.**
  ⚠⚠ **Do NOT touch `harness/{build,asm,measure}.py` or `verus_run.py`** — all
  measurement-hashed, and a re-measure is not in this task's budget.
  ⚠ **Do not touch any other pattern, and no `patterns/p23-partition/` file
  outside `controls/`** — `*.rs`, `c/*`, `model.py` and `inputs/gen.py` are all
  measurement-hashed.
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- ⚠ **Every acceptance test needs an arm that FAILS.** **The list at the end of `.memory/03-measurement.md` is the catalogue of
  named failure classes — ⚠ **READ THE LIST; IT CARRIES NO USABLE COUNT.**
  ⚠⚠ **Its own entry says a count is a cached derivation that goes stale like
  any other cached number, and that count has now rotted THREE times — most
  recently because this manager added an entry after writing the old figure
  into three task files. If you need a number, derive it where you write it.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_121_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 488** (⚠ **a rigour signal, not a ledger —
do not re-add it**). ⚠ **This file was written carrying 466 and was updated to 488
when `TASK_120` landed, BEFORE it ran** — rule 2 says the count lives in one place
and stale copies are the failure mode. The calls I am least sure of:

1. ⚠⚠ **That option (a) is right.** **Hashing the blobs is the complete answer and
   it is also the one that makes the sidecar stale whenever somebody adds a sweep
   band — which `.memory/05-layout.md` measured as costing a gate re-run and NO
   re-measure, i.e. the cheap direction.** ⚠ **But I have now been wrong TWICE in
   one session about what this pin should hash. Treat my third answer with the
   suspicion the first two earned, and if (b) plus a written-down gap is the
   honest engineering call, SAY SO.**
2. ⚠ **That this is worth doing at all rather than DELETING the sidecar.**
   **`sweep_fit.json` is regenerable in one command. If its numbers are quoted
   only in `NOTES.md` prose that already names the regeneration line, the honest
   fix might be to delete the committed blob and keep the script.** ⚠ **That
   would close the item with LESS machinery, and this project has a standing
   preference for that. Check what actually cites it before you build anything.**
3. ⚠ **That §B's `.temp/` citation point is a real defect.** **A committed
   document citing a gitignored path is either a real hole or a deliberate
   convention I have not found written down. `grep` before you agree with me.**

Carry **488** forward, incremented by what you find.
