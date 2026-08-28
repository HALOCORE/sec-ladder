# TASK_119 — the instrument corrections `TASK_114` earned. ONE sweep, LAST.

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
**`.tasks/TASK_114_REPORT.md` in full**, then `.memory/03-measurement.md`'s
environment-pin section and `.memory/00-environment.md`'s `MIRIFLAGS` section
(⚠ **both already carry the retractions — the manager landed them; you are
fixing the CODE, not the prose**).

Scratch in **`.temp/t119/`**.

⚠⚠ **DO NOT START UNTIL `TASK_118` HAS LANDED.** It moves `p42`'s
`contract_sha256` and re-measures that pattern. **Your `check.py` edits stale
every gate record, so your sweep must come after its move, not before it** —
`TASK_096` edited `check.py` mid-pattern and went 8 STALE.

⚠ **EVERY ITEM HERE EDITS `harness/check.py` (or `limbs.py`/`report.py`), NONE OF
WHICH IS MEASUREMENT-HASHED.** ✅ **So the whole task costs ONE 26-pattern gate
sweep and NO re-measure.** **That is why they are batched. Finish every edit
before the sweep starts.**

---

## §A — ⚠⚠ THE ENV PIN IS ONE INTEGER SHORT. THIS IS THE DELIVERABLE.

**`marginal_ir_env` licenses the rule *same `bytes` and same `tuning_vars` ⇒ the
marginal must match exactly*, and `TASK_114` falsified it.** At **byte-identical
`bytes = 3520` with identical (empty) `tuning_vars`**, varying only the **number
of variables**:

```
3059.00, 3059.00, 3066.00, 3066.00        <- period 4 in the VARIABLE COUNT
```

**Mechanism, measured: a 9-rung sweep at constant `bytes = 3680` is period 4 in
the variable count = the 32-byte alignment period ÷ 8 bytes per `envp` POINTER
SLOT.** ⚠⚠ **`check.py::_env_block` records `len(/proc/self/environ)`, which is
`NAME=VALUE\0` concatenated and CONTAINS NO POINTER ARRAY.**

⚠ **`.memory/03-measurement.md` already carried the arithmetic** — its 87-byte
decomposition is `8 (envp pointer slot) + 13 + 1 + 64 + 1` and calls that leading
`8` *"the part the manager forgot entirely"*. **The pin repeats the exact error it
was written to prevent.**

✅ **Fix: record the variable COUNT too** — `nvars`, or `bytes + 8·nvars`.
⚠ **Take it from the SAME child `_env_block` already spawns** (not `os.environ`,
not `check.py`'s own `/proc/self/environ` — both are documented ways this project
has already got it wrong).

⚠⚠ **ACCEPTANCE NEEDS AN ARM THAT FIRES: reproduce the `3059/3059/3066/3066`
ladder at constant `bytes`, and show the NEW field distinguishes the four cases
where the old one did not.** ⚠ **A field that merely exists is not a fix.**

⚠ **Also write the pin's DOMAIN where the pin is read.** `TASK_114`: *"valid
within one clone location"* exists **only** in `TASK_107_REPORT.md` — **0 hits in
`check.py`, `.memory/` and the record.** ⚠ **`argv` moves the marginal ±7 too.**
**A pin whose domain is not written down where the pin is read is not a pin.**

## §B — `MIRIFLAGS`: a DECISION, not a fix. ⚠ Do not invent a mechanism.

**`MIRIFLAGS` was never the variable.** The `miri` **driver** does not parse it —
that is `cargo-miri`'s, and the gate invokes the driver. The 4.6× is an
**environment-block effect**, and a **decoy variable unrelated to Miri** selects
the fast state:

```
MIRIFLAGS unset   338.1 / 347.4 / 345.4 / 343.1 s      <- SLOW
MIRIFLAGS=""       75.1 / 75.4 s
SLB_R114_DECOY=""  74.4 / 75.9 s        $OLDPWD removed  75.3 s
                   10-rung ladder: 1 slow, 10 fast
```

⚠⚠ **`MIRI_TIMEOUT` is 180 s, so the shipped `MIRI_FLAGS = ()` can turn a green
row BLOCKED — it does not CONTROL the state, it CHANGES it.** And
`miriflags` / `miriflags_removed_ambient` / `miri_version` are **identical in
both states**, so the record cannot say which you got.

**What to do, and it is deliberately modest:**

1. ✅ **Make the state DIAGNOSABLE** — §A's variable count is very likely the
   same discriminator. **Check whether it separates the fast and slow states.**
   **If it does, say so; if it does not, say that too and record the Miri wall
   time in the record so the state is at least visible.**
2. ⚠⚠ **DO NOT WRITE A MECHANISM.** **`TASK_114` killed its own only correlation
   rather than report it — a second `base % 4 == 3` draw timed FAST — and this
   axis has already had TWO wrong mechanisms published (*"seed-vs-seed"*, then
   *"`MIRIFLAGS` presence"*).** ⚠ **A third would be worse than an open
   question.**
3. **Say whether `MIRI_FLAGS = ()` should stay.** ⚠ **It was landed to fix a
   problem that does not exist as described. It may still be right — stripping an
   ambient variable makes the gate independent of the invoking shell — but that
   is a DIFFERENT justification and the code comment should say the true one.**

## §C — the four routes the union misses (latent; fix or document, your call)

`N7aV`/`N7bV`/`N7cV`/`N8V`: the regex's three blind attribute spellings plus a
macro-argument `#[path = $p]`, **placed inside `verus!{}` where dep-info is
blind.** Confirmed: Verus reads the leaf, `_path_includes` returns `[]`, two
`unsafe` tokens invisible.

⚠ **Blast radius is ZERO today** — all 26 patterns return exactly
`['common/driver.rs']`. ⚠⚠ **Which is `TASK_114`'s sharper reading: "blast radius
zero" means THE NEW LIMB DOES NOTHING YET, not that the tree is safe.**

**Decide and defend:** extend the regex to the three attribute spellings inside
`verus!{}`, or **document the hole precisely and leave it.** ⚠ **If you leave it,
the docstring must say WHICH routes are uncovered** — this project has found nine
routes across three tasks, each after the previous table read as exhaustive, and
an undocumented hole is how the tenth and eleventh were found.

## §D — three small ones, all confirmed, all cheap

1. ⚠ **Stage 9's `MISSING` fix instruction is WRONG.** It tells the author that
   `report.py` renders **from `results/gate/<pattern>.json`**. **It does not** —
   `report.py::load` requires `results/pNN-*.json` (measure.py's record) and exits
   `p99 matches [] in results/`. ⚠⚠ **So on the brand-new-pattern case the
   message names, the two-command loop DEADLOCKS.** **Verify that yourself, then
   write the instruction that actually works.**
2. **33 `UNPINNED`/shout entries across 26 records render NOWHERE.** `p23`'s
   `controls_json` shout lives in the gate JSON (`controls_json`, `loud[1]`) and
   in no human-readable artefact; `report.py` reads neither key. ⚠ **A shout
   nobody reads is a check that cannot fail — a named class here.** **Surface
   them, or downgrade the ones that do not deserve to exist.**
3. **`harness/limbs.py:69–70` still COPIES `TWIN_PREFIX`/`TWIN_CFG`**, two lines
   below the comment explaining why copies drift — and `TASK_107` fixed the
   neighbouring `TWIN_BANNED` by importing. **They agree today.** ✅ **Import
   them.** ⚠ **Then `grep` for any OTHER copied `check.py` constant and say what
   you found — that is the general form and it has now bitten twice.**

## §E — the sweep, last

Full **26-pattern** `harness/check.py`, then
`synthesis/licence.py --emit synthesis/licence.json` **BEFORE**
`synthesis/synthesize.py` — ⚠ **mandatory order or every row publishes
`LICENCE STALE`** — then `synthesis/outward_ir.py`, then **`synthesize.py`
AGAIN** (the sidecar pin makes the second run mandatory), then
`harness/measure.py --check-stale`.

**Expect `24 PASS + 2 PASS-WITH-BLOCKED-ROWS`, 0 failures.** ⚠⚠ **BUT SEE §B:
`p42`'s blocked-row count may legitimately be 1 or 2 depending on the
environment state, and `p01`'s Miri timeout is real. Report what you got with the
`marginal_ir_env` values beside it; do NOT chase a Miri block.**
**If anything else turns red, STOP AND REPORT.**

⚠ **`results/synthesis.md` will move** (§A adds a field). **Diff it and state
exactly which lines moved and why.** ⚠ **The `< 2.00` band's `real`/`spurious`
split is ONE DRAW of the ±7 term — if it moves, that is expected and is NOT a
finding.**

---

## Constraints

- **`.temp/t119/` only. No `/tmp`.** **Notes in `.temp/t119/NOTES.md` AS YOU GO.**
  ⚠ **`TASK_118`'s first attempt died mid-task and had written no notes; the
  manager reconstructed them from artefacts. Do not repeat that.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never edit it.**
- ⚠⚠ **Do not touch `harness/build.py`, `harness/asm.py` or `harness/measure.py`**
  — all three are measurement-hashed and would cost a full re-measure.
  ⚠ **Do not touch any `patterns/*/` file.**
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- ⚠ **Every acceptance test needs an arm that FAILS.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_119_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 466** (reconciled across five branches at
`TASK_118`'s launch; ⚠ **it is a rigour signal, not a ledger — do not re-add
it**). The calls I am least sure of:

1. ⚠⚠ **That §A's variable count is the right second integer.** It is `TASK_114`'s
   proposal and it explains the measured period exactly — **but the same was true
   of `bytes`, which also explained a measured period and was still incomplete.**
   ⚠ **Try to break the NEW pin the way `TASK_114` broke the old one: hold
   `bytes` AND `nvars` fixed and see if anything still moves.** **If something
   does, say so — a third incomplete pin is much better known than assumed.**
2. **That §B should stop at "make it diagnosable".** ⚠ **A 4.6× swing on Miri
   selected by an unrelated environment variable is a genuinely strange result
   and somebody will want the mechanism. I am telling you NOT to chase it. Argue
   if you think that is wrong** — but if you do chase it, **measure, and do not
   publish a third mechanism on this axis without one.**
3. ⚠ **That §C should be fixed at all rather than documented.** **The blast
   radius is zero and the regex has needed extending three times. If your honest
   read is that the union should stay as it is and the hole should be written
   down, SAY SO** — that is a legitimate answer and cheaper than a fourth regex
   round.

Carry **466** forward, incremented by what you find.
