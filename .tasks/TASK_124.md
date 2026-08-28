# TASK_124 — `CVE-2021-23017`: is the four-way split a property of the BUG or of the PORT?

**Role: research engineer.** ⚠ **Your deliverable is a DECISION with a
measurement behind it — BUILD or REFUSE. Do not build the pattern in this task.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 42 and the
endgame box row**, then **`.tasks/TASK_123_REPORT.md` §C and §D in full**, then
`.memory/06-catalogue.md`'s probe descriptions, then
**`.tasks/TASK_055_REPORT.md` §2.8 caveat 2** (⚠ **it is the trap this task is
about, and the manager has already misquoted §2.8 once — read it, do not take my
summary**).

Scratch in **`.temp/t124/`**.

---

## The state, and it is better than any candidate this project has had

**`TASK_123` enumerated 20 worked CVEs. Nineteen died. `CVE-2021-23017`
survived, and — ⚠ for the first time on any axis this project has considered —
ITS NOVELTY CLAIM WAS MEASURED BEFORE THE ROW WAS PROPOSED.**

```
the mechanism   a SIZING pass under-counts a separator the WRITING pass emits,
                so THE BOUND COMES FROM AN EARLIER PASS OVER THE SAME INPUT
bound census    14 destination buffers across all 26 built kernels
                13 `#define` capacities + 1 input extent + ZERO prior-pass counts
                (must-fire arm fires on the candidate)
probe 1         C = ASan `heap-buffer-overflow WRITE of size 1`
                R2 = panic
                R3 (`Vec::push`) = CORRECT        <-- the interesting one
                R4 = silent OOB write, Miri UB
probe 2         three distinct kernels
probe 3         R2 - R4 = +63.00 Ir/call
probe 4         `get_unchecked` 0 hits at the pin
```

⚠ **Only LIMB 2 of the reviewed bar is claimed (*a new source of the bound*).
Limb 3 has NO isolation and `TASK_123` correctly did not claim it.**

## §A — ⚠⚠ THE DECIDING QUESTION, AND IT IS SHARPER THAN THE ONE THE REPORT NAMED

**`TASK_123` disclosed that the row's spatial character depends on the
ALLOCATION SHAPE** — per-name allocation is `p02`'s class and buildable; the
corpus's own shared-arena port is `p04`'s class (in-bounds wrap) and dead —
**and said the choice is the engineer's, not the CVE's.** ✅ **That is correct and
it is the blocker.** ⚠⚠ **BUT IT IS AN INSTANCE OF A LARGER QUESTION, AND THE
LARGER ONE IS WHAT DECIDES THE ROW:**

> ⚠⚠⚠ **IS THE FOUR-WAY BEHAVIOUR SPLIT A PROPERTY OF THE BUG, OR OF THE PORT?**

**`R3` coming out *CORRECT* — not "safe", not "panics", but RIGHT — is the most
interesting single cell in this report and no built row has it.** ⚠ **And it is
exactly the cell most likely to be an artefact**, because a growable `Vec::push`
has **no bound to violate**: it does not survive the bug, **it deletes the bug's
precondition**. **If C writes into a fixed buffer and R3 grows a `Vec`, the two
rungs are not the same program and the split is a REPRESENTATION difference, not
a safety measurement.**

⚠⚠ **`TASK_055` §2.8 caveat 2 is this exact trap, already paid for once:
*"R2/R3 are not 'R4 plus a check', they are a different representation"*, and on
`p27` that was the pattern's whole point rather than a defect. DECIDE WHICH IT IS
HERE.** **Three outcomes, all respectable:**

1. ✅ **The split is a property of the BUG** — the fixed-capacity destination is
   forced by the CVE (a reserved region adjacent to a field that gets corrupted),
   and R3's correctness is a real consequence of the safe idiom. **→ BUILD.**
2. ⚠ **The split is a property of the PORT** — R3 was handed a growable buffer
   the other rungs did not get. **→ either re-port R3 to the same
   fixed-capacity destination and RE-MEASURE, or REFUSE.**
3. ⚠ **The fixed-capacity destination cannot be written without making the row
   `p02`** (attacker length field into a `#define` buffer). **→ REFUSE, and say
   so; the bound census is then measuring a distinction the ladder cannot
   carry.**

⚠ **State which one, with the measurement. Do not reason your way to it.**

## §B — if §A says BUILD, then LIMB 2 STILL HAS TO SURVIVE CONTACT

**The census says *a bound computed by a previous pass* is absent from 26 built
kernels. ⚠ That is a census of what EXISTS, not proof that the ladder can PRICE
it.** **So, before anyone writes a `spec.md`:**

1. ⚠⚠ **Does the two-pass structure survive at R4/R5 AT ALL?** **A sizing pass
   and a writing pass that must agree is a two-call kernel, and every built
   pattern is one call.** **Check `common/driver.*` and `harness/dloop.py`:
   ⚠ if the driver can only time ONE kernel call, the "two passes disagree"
   mechanism may not be expressible in this harness — WHICH WOULD BE A REAL
   FINDING and is cheap to establish.**
2. **Can R5 state it?** ⚠ **The obligation is *the sizing pass's count bounds the
   writing pass's writes*, i.e. a relation BETWEEN TWO LOOPS.** ⚠⚠ **`p42` has
   just burned THREE encodings on an obligation Verus would not carry the way the
   author expected. Spend ONE probe here, not three** — and ⚠ **if it does not go
   in one, SAY SO AND STOP; "R5 is open" is a legitimate row property, not a
   failure** (`p42` ships that way).
3. ⚠ **`get_unchecked` is 0 hits at the pin (probe 4), so R4 needs a spelling
   that is BOTH unsafe AND has a verifying R5 twin** — the `identity` pin binds.
   **Name the spelling before committing to the row.**

## §C — the clean negatives that are cheap and worth having either way

- ✅ **`TASK_123` caught THREE of its own instrument defects with must-fire arms,
  two of which would have handed it a free refusal** (an `argv` bug giving
  `0.00000 Ir`/call from zero iterations; per-iteration `match` dispatch making
  byte-identical kernels read `43/50/37`, **which changed a sign**; C loop
  hoisting giving `n1 == n2`). ⚠⚠ **RE-RUN ITS ARMS BEFORE BUILDING ON ITS
  NUMBERS.** **`.temp/t123/C/REBUILD.sh` regenerates.**
- ⚠ **`+63.00 Ir`/call is `R2 − R4`. The project publishes `R3 − R4`.**
  **Get the R3 figure, and search the R4 side** — this file's own trap row says a
  difference is only as honest as its weaker-searched endpoint, and **five
  patterns have now published a headline that moved when somebody searched the
  other rung.**

---

## Constraints

- **`.temp/t124/` only. No `/tmp`.** **Notes in `.temp/t124/NOTES.md` AS YOU GO.**
  Keep the generator, delete the artefact.
- ⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.** Copy what
  you need into `.temp/t124/`.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/` or any
  `patterns/*/` file.** **You are deciding, not building.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py` or `measure.py`** unless the
  manager says the tree is free. **Build probes with direct `clang`/`gcc`/`rustc`
  under `.temp/t124/`.**
- ⚠ **Every probe needs an arm that MUST FIRE.** **Read the failure-class list at
  the end of `.memory/03-measurement.md` — ⚠ it carries no usable count; read the
  list, and derive a number where you write it if you need one.**
- ⚠⚠ **Probe 2 has SIX known defects and `.temp/t104/probe2.py` carries the
  sixth.** **Take the symbol extent from the ELF symbol table.**
- Hand-run ASan needs `env -u LD_PRELOAD`; **never truncate a sanitiser log with
  `head`**. ⚠ **`TASK_086` lost four harm cells to a `head -4`.**
- Verus via `./verus_run.py` only, single-file mode, never `--cargo`. Do not bump
  the pin.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_124_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 536** (⚠ **a rigour signal, not a ledger —
do not re-add it**). The calls I am least sure of:

1. ⚠⚠ **That `R3 = CORRECT` is real.** **It is the cell that would make this row
   worth building and it is the cell most likely to be a port artefact. I think
   it is PROBABLY an artefact of a growable `Vec` — and I have been wrong on this
   class of call repeatedly, most recently on this very corpus, where my mapping
   of this exact CVE onto `p12` was refuted by measurement.** **Prove me wrong.**
2. ⚠ **That the row is worth building even if §A comes out clean.** **The bar it
   meets is limb 2 alone, and `p23` — the only row ever admitted on the reviewed
   bar — shipped a headline that was later corrected from `3.11×` to `1.315×`.**
   ⚠ **A row that meets one limb is not a row that will produce a good finding.
   If your read after §A and §B is *"admissible but it will publish nothing"*,
   SAY THAT** — it is a legitimate and cheap outcome.
3. ⚠⚠ **That this project should build a 27th pattern at all rather than write
   up what it has.** **There is no measured reason to STOP** (finding 41 died)
   **and that is NOT the same as a reason to CONTINUE.** ⚠ **The standing user
   mandate is *"as many realistic C patterns as possible"*, so the default is
   build — but if this row is weak, the honest recommendation is the IDIOM
   enumeration instead, which is the question `TASK_113` actually asked and which
   no corpus in this repo answers.**

Carry **536** forward, incremented by what you find.
