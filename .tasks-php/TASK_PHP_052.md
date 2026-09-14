# TASK_PHP_052 — **FINISH ROW 10 (`ph56`)**: R5, `spec.md`, gate, statistic

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_052_REPORT.md` — **write the FILE** (rule 10).

⭐⭐ **THIS IS A RESUME, NOT A RESTART. `TASK_PHP_051` DID THE HARD HALF AND
STOPPED CLEANLY, AND ITS REPORT §9 IS YOUR STARTING POINT.** ⛔ **Do NOT
re-derive the mechanism, the harm, the census or the R1h** — they are measured,
and re-deriving them spends your depth on work that is already done.

---

## §0 ⛔ READ FIRST, IN THIS ORDER

1. **`.tasks-php/TASK_PHP_051_REPORT.md` — §9 IS THE BRIEF.** Read §9 in full,
   then §1 (the harm), §2 (the census), §5 (the R1h). ⭐ **§9's *"order to
   resume in"* is the plan; follow it.**
2. `patterns-php/ph56-fetchmode-arith/` — `NOTES.md`, `model.py`, `c/*`,
   `safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `controls/`.
   ⭐ **`unsafe.rs` already isolates TEN trusted accessors, and the tenth,
   `zunwrap`, IS CRASH-041 written as a precondition.**
3. `patterns-php/ph55-opdata-stride/` — **the sibling row, finished last week,
   and the closest template you have.** Its `verus.rs`, `spec.md` and
   `controls/` are the shape to clone. ⚠ **Clone the DESIGN, not the text.**
4. `.tasks-php/PROTOCOL_PHP.md` — **§E** (the six-command sequence), **§B1a**,
   **§B5** (new — family-B publishability), **§C**, **§F6a**, **§H**.
5. `.memory-php/03-numbers.md` — the **five** things every percentage owes.

⭐ **WHAT IS ALREADY TRUE AND YOU MAY RELY ON** (`_051` §9, differentially
validated): all five existing rungs **agree on every input**; the C↔model
differential is **156 windows × 2 configurations, 0 mismatches**; `model.py` has
**three independent implementations** that agree; `inputs/gen.py`'s assertions
are green **including an assertion of the census itself**; and
`gate.py --preflight` is **rc 0** with the row present.

---

## §1 ⭐⭐⭐ THE WORK, IN `_051` §9's ORDER

### 1.1 `verus.rs` (R5)

**The obligation is already written down** (`_051` §9):

> for every `j < nops`, `ops[j].opcode == ISSET_ISEMPTY_DIM_OBJ` implies
> `ops[j].op2_type != T_UNUSED`

established as a **loop invariant of the compile pass** — which **needs** the
`BP_VAR_IS` guard, i.e. **R1h** — and consumed at `zunwrap`'s call site.
⭐⭐ **It is the direct analogue of `ph55`'s `ok_from`: a property the EMITTER
establishes and the EXECUTOR relies on without testing.** ▶ **Say that in
`NOTES.md`; with `ph55` it is `n = 2` for the family's shape.**

⛔ **`identity` pins R4 ≡ R5, so the EXEC TEXT MUST STAY ONE TEXT.**
⚠⚠ **Verus refused function-pointer types on `ph55` — a TYPE-LEVEL refusal that
no `external_body` wrapper fixes.** ▶ **If `ph56`'s representation trips the same
refusal, that is a FINDING and `n = 2`, not a blocker; report it and pick the
representation that works, as `ph55` did with `Option<u8>`.**

### 1.2 `spec.md`

Derive `requires`/`ensures` from `verus.rs`. `ensures` should name `ph56_run`,
which `model.py` already exports via `helpers`.
⛔⛔ **RUN `spellings.py --audit-only` ON THE CONTRACT PROSE BEFORE QUOTING IT.**
**A backtick in an `idiom.required`/`forbidden` entry IS a pin** — item 100,
**three instances in three consecutive tasks**, one of them in a validator.
⚠ `idiom` entries are **heterogeneous**: 343 of 648 corpus entries are plain
strings with no language key (item 91). **A rust-only `forbidden` entry is fine;
a rust-only `required` entry needs to say what it is.**

### 1.3 The gate — **the six-command sequence, `PROTOCOL_PHP.md` §E**

⚠ **Expect the FIRST gate to FAIL on tables.** That is the `gate → report →
gate` chain working, not a defect.
⛔⛔⛔ **NEVER run `harness/check.py` directly on a php row.** `_050` §2.4 found
this is **not only a provenance convention**: the shim lengthens every
REPO-relative path by **exactly 15 bytes** against an alignment window that is
**16 wide**, so a direct run measures a different alignment state.

### 1.4 The statistic

⭐⭐⭐ **`inside_share` PER CELL FIRST, published as a matrix, THEN choose.**
⛔ **A HIGH SHARE IS NOT A CERTIFICATE** — `ph55`'s C cells are **74–83 %** and
A1 still reads `0.000 %` on its own defect site, because what matters is whether
**the DIFFERENCE** lands inside the symbol.

⛔⛔ **EVERY PERCENTAGE OWES FIVE THINGS: STATISTIC · INPUT · OPT/MODE · BASE ·
and if the base is a C cell, WHICH COMPILER — with BOTH C columns**, or an
explicit statement that only one was measured. **One C column is not a number
with error bars; it is a different sign.** ⛔ **Never quote an `O0` figure as a
performance result.** ▶ Run `.tasks-php/cbaseline_check.py --ratchet`;
**adjudicate any new hit BY HAND, never widen the regex.**

⛔⛔⛔ **ANY FAMILY-B FIGURE MUST CLEAR `PROTOCOL_PHP.md` §B5's SWEEP** —
`.tasks-php/php50_align_sweep.py`, **no build, no gate, minutes** — and report
**TWO verdicts per pair: *magnitude resolvable?* and *sign stable?*** ⓘ The step
is not a constant: corpus-wide it takes `0.00`, `0.02`, `7.00` and `34.49`.

### 1.5 ⓘ `_051` §8.1's optional extra — **only if everything above is done**

Rebuild PHP with the patch and re-run the six snippets. ⭐ **Nice to have, not
owed. Skip it rather than leave §1.1–1.4 unfinished.**

---

## §2 ⭐ THE PREDICTIONS THIS TASK INHERITS, AND ONE NEW ONE

⚠ **`_051` left prediction 2 UNTESTED because no gate ran. It is yours.**

1. **Stage 5c-twin passes cleanly — no hatch, no blocked row.** ⭐ `ph55` upheld
   this at `n_twins = 8`, and F97's narrowing says the collision is a property of
   the `MaybeUninit` ITEM, not of php rows. ⛔ **If it fails here, F97's
   narrowing is wrong and that is a bigger finding than this row.**
2. **The R1h costs ~nothing at run time** — the guard is in the **COMPILER**, so
   it runs once per emitted opline, not per execution. ⚠ **`_051` upheld the
   mechanism and could not test the number, and flagged that this kernel
   compiles-and-runs in one loop** — so **say which you are measuring.**
3. ⭐ **NEW, REGISTERED NOW: `ph56`'s R3 and R4 endpoints.** `ph55` refuted my
   endpoint prediction **in both halves, signs exactly swapped**, and `ph45`/
   `ph52` both reversed their ordering under search. ▶ **I make NO prediction on
   this row's endpoints, and that is itself the position: at `n = 4` the only
   defensible prior is that search decides it.** ⓘ **An endpoint search is NOT
   owed by this task** — it is a separate task, as on every other row.

---

## §3 Traps

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NOT BE TRUNCATED AND MAY NOT MATCH ITSELF**
   (item 113, both halves earned). `pgrep` feeding a decision gets **no `head`,
   no `tail`**; a truncated one **raced `ph55`'s gate against itself**, and a
   self-matching one span forever. ▶ **Confirm `/proc/<pid>/cmdline` for an exact
   PID — best of all, need no `pgrep`.** ⭐ `_051` used none at all.
2. ⛔⛔ **`git apply --check` LIES.** It returned `0` on a path it could not
   apply, **twice now** (`_048` §4d, `_051` §5.1). **Never trust `--check`
   alone.**
3. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps.
4. ⚠⚠ **A `c/*` COMMENT MAY POINT AT AN ARGUMENT; IT MAY NOT STATE ITS VERDICT**
   (§F6a). **`c/*` is the MEASUREMENT digest — 32 cells to repair.** Provenance
   prose goes in `NOTES.md`, which is gate-only.
5. ⛔ **§H: a validator lands with its must-fire negatives INSIDE it**, feeding
   `problems`. **Never in gitignored `.temp/`.** ⭐ **If a checker is a grep,
   adjudicate by hand and ratchet — do not tune the regex.**
6. ⛔ **F101 / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and fired LIVE
   in BOTH directions.** Clone `ph52`/`ph55`'s repair.
7. ⚠ **A comment is not code.** Test behaviour.
8. ⚠ **`.temp/php52/` only.** Keep the generator, delete the artefact.
   ⓘ `.temp/php51/NOTES.md` is `_051`'s rebuild recipe — **read it before
   recreating anything.**
9. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY.** ⚠⚠⚠ **NO EDITS
   under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
   `common-php/`.** ⚠ **No `git add` / `git commit`.** Never touch `.web/`.
10. **Bracket**: `harness/measure.py --check-stale` → **`66/0`**, must NEVER
    move; `harness-php/gate.py --tool measure --check-stale` → **`20/0` now**,
    **`22/0`** once this row's two records land. ⭐ **`_051` predicted `22/0` and
    honestly reported `20/0` because the row never landed — do the same.**

---

## §4 Definition of done

1. **`verus.rs` verifying**, with the compile-pass invariant of §1.1, and
   `identity` holding R4 ≡ R5 as one exec text.
2. **`spec.md` complete** — contract, `provenance`, `idiom`, `identity`,
   `collapse`, tier — with `spellings.py --audit-only` run on its prose first.
3. **Gated: `harness-php/gate.py` green**, verdict quoted **from the gate record,
   named**, and the **php bracket at `22/0`**.
4. **`inside_share` per cell as a matrix, before the statistic is chosen**; both
   statistics labelled; **both C columns** on every cross-language figure; any
   family-B figure cleared through §B5 with **two verdicts**.
5. **The three §2 predictions scored, either way.**
6. ⭐ **The `ph55` pairing carried forward**: `_051` established *one family, one
   fix shape, two harms*; **add the R5 half — both rows' obligation is a property
   the EMITTER establishes and the EXECUTOR relies on without testing.**
7. ⭐ **WHAT YOU ARE UNSURE OF, in its own section**, and **if your depth runs
   out, STOP AND SAY EXACTLY WHERE.** ⭐⭐ **`_051` did that and it was the right
   call — a clean stopping point with a resume order cost the programme one task
   and cost it nothing else.**
8. **Brackets quoted first and last.**
