# TASK_106 — land `TASK_105`'s corrections into `p23`

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`.tasks/TASK_105_REPORT.md` **in full** (it is the review you are landing), then
`patterns/p23-partition/{NOTES.md,README.md,spec.md}`.

Scratch in **`.temp/t106/`**.

⚠ **This is the third task of `p23`'s three-task loop** (build → review → land).
**The manager writes RECAP finding 38 after you land**, so your report is what
that finding gets written from — **be precise about numbers and their
conditions.**

---

## What is already done, so you do not redo it

✅ **The manager has already landed the `.memory/06-catalogue.md` half** of M1,
M2, M4, M5, A.2 and m5. **`.memory/` and `RECAP.md` are manager-only — do not
touch them.** Your job is the **pattern files**.

## The eight corrections

| # | file(s) | what |
|---|---|---|
| **M1** | `NOTES.md` §7 ×3, `README.md:44` | **SEVEN** distinct wrong checksums over eight C cells (**gcc 3, clang 4**), not eight. ⚠⚠ **And `NOTES.md` describes the two gate runs IN REVERSE ORDER** — it quotes `gate2.log`'s numbers as the headline and then calls `gate_final.log` (the LATER run, the one that produced the committed record) *"an earlier gate run"*. **Quote the committed record.** ✅ The qualitative claim (exit 0, silent, all wrong, unstable across builds) is untouched. |
| **M2** | `NOTES.md` ~:155 | The prose says the hardened kernel is *"cheaper (−39.10 / −60.34)"* while the **table at :148 says `+39.10 / +60.34`**. ⚠ **The substance is right — hardened gcc IS cheaper and smaller — and the SIGN NOTATION is inverted.** `R1 − R1h = +39.10` *means* R1h is cheaper. **Fix the notation, keep the claim.** ⚠ **The manager copied the prose into `.memory/` and shipped the error; that is why this one matters.** |
| **M3** | `NOTES.md` §3 | ⚠⚠ **The gcc guard's price FLIPS SIGN TWICE across p23's own rank band** — `+168.48` at 0.03, `−144.59` at 0.50, `+139.87` at 0.97, **two zero crossings**. The shipped inputs sit at mean ranks **0.44 and 0.28**, both inside the negative window, and **`gen.py::_check_residues` ENFORCES they straddle 0.35**. So *"the safety line has a negative price on gcc, on both inputs"* is **a property of the two inputs' ranks, not of the kernel.** ⚠ **p23's own rule — *"any number quoted without its rank is quoted without its domain"* — must be applied to its own C row.** **AND THE MECHANISM IS REFUTED:** §3 predicts a saving proportional to scan steps; fitted, `dn` alone is **R²=0.023** and `sw` alone **R²=0.973**. The price is ≈ **`+195` flat `− 5.2 Ir` per exchange**. ⚠ **The review offers a disassembly reading consistent with that regression but explicitly NOT proved — land it as a candidate, not as the mechanism.** |
| **M4** | `NOTES.md` §9d **and `spec.md`'s `identity[0].why`** | **Land the phenomenon, mark the cause OPEN.** `k_up == k_r3c` and `k_dn == k_r4b` reproduced to the instruction independently — **keep that.** ⚠⚠ **But *"the direction of the cursor is the whole tax"* FAILED BOTH ISOLATIONS**: making the induction variable ascend costs `+816`/`+1614`/`+1313` instead of recovering the elision, and removing the unsigned subtraction recovers `16`/`12`/`20` of a `488`/`184` gap. ⚠⚠ **`spec.md` IS INSIDE THE HASHED CONTRACT — this moves `contract_sha256`. DISCLOSE IT EXPLICITLY and record the before/after**, per rule 6. ✅ `spec.md` is **not** in `measurement_sources`, so this costs a `check.py p23` re-run and **NOT** a re-measure. |
| **M5** | `NOTES.md` §9b | **The published R3-side span's floor is wrong by ≥150 `Ir`/call.** A fully safe, zero-`unsafe` R3 spelling reaches **`2991.00`** — 150 below the cheapest published in-contract R3, **59 below the in-contract R4 spelling**, and **inside the published R4 span**. It passes `check.py::spelling_matches` on every `required` and hits no `forbidden`; **admissibility turns on one `required`'s ENGLISH, which no gate stage reproduces.** ⚠ **You must decide and defend: either it is admissible (and the tax is overstated by ≥150), or p23's R3 endpoint is fixed by prose alone — in which case say so with the same disclosure p23 already makes for R4.** **Do not quietly keep the old floor.** |
| **A.2** | `NOTES.md` §0 | **Strike *"the multiset is separable"*.** ⚠ **The experiment behind it was measuring a VACUOUS postcondition**: the multiset-deleted probe accepts a body that zeroes the live prefix and never looks at the pivot (`4 verified, 0 errors`), while the same body with the multiset kept gives `3 verified, 1 errors`. ✅ **The CONCLUSION stands on better evidence and you should say so: the SHIPPED `ensures` is an exact value equality and refuses all NINE mutants, 9/9, with 3/3 controls verifying — the strongest mutation result in the tree.** |
| **m1** | `NOTES.md` rule-6 section | Its **headline** asserts *"no `required` … entry changed meaning"* while **row 1 of its own table** says `required[7]` lost its backticks and that this *"makes the declaration weaker in exactly one direction: fewer pins"* — and by the declaration's own standard **backticks are the trigger**. ⚠ **The edit is defensible; the headline is not.** **Rule 6 is explicit that a false disclosure is worse than the thing it describes**, and this is also `PROTOCOL` rule 13's shape (a summary asserting what its body refutes). |
| **m5** | `NOTES.md` §10 | The missing `-C debug-assertions=on` column **does hide a sign flip, and its location is now known**: R3−R4 is `+574` (rank 3%), `+1334` (50%), **`−246` (97%) — R4 dearer.** ⚠ **Also worth landing: `r4dn` becomes EXACTLY EQUAL to `base` under debug-assertions — `assert_unsafe_precondition!` reinstates precisely the check `get_unchecked` was bought to remove.** **The shipped ranks are outside the flipping region, so say the headline survives AND say where it would not.** |

## ✅ And one thing to ADD, because the review made it stronger

⚠⚠ **`NOTES.md` 9c currently says the band-K fit has ±30 residuals and must not
be quoted as a law. TASK_105 produced an EXACT one and it should replace it:**

> **`R3 − R4 = 242 + 2·dn + 2·sw − 3·rounds` `Ir`/call — max residual `0.00`
> over all 31 band points; holdout (fit on 16 odd `nlow`, predict 15 even) max
> |error| `0.0000`.**

Per record: `30.25` + `2` per downward-scan step + `2` per exchange − `3` per
outer round. **The shipped `187.3 + 16.01·(m − nlow)` is that law with two terms
dropped.** ⚠ **RE-DERIVE IT YOURSELF before landing it** — a law owes its domain,
and this one is fitted on band K only. ⚠ **Also land `up + dn = 256.00` exactly
at every point** — total cursor work is constant and only its split moves, which
is what makes the axis clean. ⚠ **And the swap-count confound is REFUTED, not
merely absent**: at the endpoints swaps are `7.63` vs `7.75` (within 1.6%) while
the tax differs `3.11×`; `sw` alone fits R²=0.013, `dn` alone R²=0.987.

---

## Constraints

- **`.temp/t106/` only. No `/tmp`.** **Notes in `.temp/t106/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.**
- ⚠⚠ **`NOTES.md` and `README.md` are NOT measurement-hashed — those edits are
  free.** **`spec.md` is NOT in `measurement_sources` either**, so M4 costs a
  `check.py p23` re-run, **not** a re-measure. ⚠ **But `c/kernel*.c`, every rung
  `.rs`, `model.py` and `inputs/gen.py` ARE measurement-hashed, and a
  COMMENT-ONLY edit to any of them stales the record.** **If a correction tempts
  you into one of those files, stop and say so in the report instead.**
- ⚠ **Do not touch `harness/build.py` or `harness/asm.py`.** Do not edit
  `harness/check.py` — its three known defects are being batched separately.
- Verus via `./verus_run.py` only, single-file mode. Do not bump the pin.
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Finish every edit, then run `harness/check.py p23`** and report the verdict
  and the new `contract_sha256`.

Write your report to `.tasks/TASK_106_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 356.** ⚠⚠ **`TASK_105` returned 13, and
the two that matter most here are both corrections to text the MANAGER had
already written into `.memory/` from a report rather than from a record** — an
inverted sign, and a "separable" claim whose supporting experiment was measuring
a vacuous postcondition. **You are landing corrections; the same failure mode is
available to you.** ⚠ **Read the RECORD, not the report, for every number you
write.** The calls I am least sure of:

1. ⚠⚠ **M5 — whether the `2991.00` spelling is admissible.** I have not decided
   and I am not going to decide it for you. **If it is admissible, `p23`'s
   headline tax is overstated and the row's central number moves.** That is a
   real possibility and **it must not be resolved by choosing the reading that
   keeps the headline.**
2. **M3's replacement mechanism.** The review offers a disassembly reading and
   says plainly it is *"consistent with the regression, not proved"*. ⚠ **Land it
   as a candidate. Do not promote it, and do not drop it either** — the regressor
   (`sw`, R²=0.973) is measured and that part IS landable.
3. **That the exact four-term law generalises beyond band K.** It has a `0.0000`
   holdout **within** band K. ⚠ **Bands N and X are unfitted and band M reads 8
   of 47 — if the law fails off band K, that is a finding and it is better found
   now than quoted in the synthesis.**

Carry **356** forward, incremented by what you find.
