# TASK_112 — land `TASK_111` into the synthesis. **B2 FIRST.**

**Role: research writer/engineer.** Read `.tasks/PROTOCOL.md`, then this file,
then **`.tasks/TASK_111_REPORT.md` in full**, then `results/SYNTHESIS.md`.

Scratch in **`.temp/t112/`**. **You are the only agent running.**

⚠⚠ **THE REVIEW'S CLOSING INSTRUCTION: *"Do not let anyone quote this document
until B2 lands"* — its R4 definition is affirmatively wrong at this pin, and
wrong in the FLATTERING direction for every `R3 − R4` figure it prints. DO B2
FIRST.**

---

## The shape of what you are fixing

✅ **The arithmetic is sound** — every figure was checked against the committed
record, the overwhelming majority reproduce exactly, and **no `‡ WITHDRAWN` cell
reaches the document.** ⚠⚠ **The defect is what was left out, and EVERY
SIGNIFICANT OMISSION RUNS IN ONE DIRECTION: the pro-safety half of the ledger.**

**That is the mirror image of the failure this project trained against.** Nineteen
retractions taught it to distrust *"safety is cheap"*; the reflex then dropped
four reviewed results showing safety earning its keep. ⚠ **The manager built the
asymmetry in** — the brief asked for *"where safe Rust does not help"* and had no
counterpart item. **Result: eight measured places where safety buys nothing, two
unmeasurable where it buys something, ZERO measured where it demonstrably buys
everything.**

⚠⚠ **DO NOT OVERCORRECT.** The fix is **restoring coverage**, not adding
advocacy. **Every restored item must carry its conditions and its scope exactly
as the record states them**, and the document's honest, deflationary voice is
correct and must survive. **If you find yourself writing a sentence that reads as
reassurance, you have gone too far.**

## §1 — B2, and do it first (two sentences plus a table cell)

§1 defines R4 as *"whatever reaches C's codegen. **Correct, just unverified**"*.
**That is affirmatively wrong at this pin.** An R4 here **must have a
byte-identical R5 twin that Verus verifies** — `identity: exact` on 25 of 26,
`norel` on the 26th.

**So R4 is bounded by what `vstd` can express and R3 is bounded by nothing:
the classes are INCOMPARABLE, NOT NESTED** (RECAP finding 14, which RECAP calls
*"the programme's central methodological result"* and which the document omits).
**Measured instance to cite: `p11`'s `r4_cstr` would be `−17 526 Ir`/call
(`−35%`) and is rejected with four `is not supported`.**

⚠ **This holds R4 above its true floor, so it flatters every `R3 − R4` in the
document.** ⚠ **§2's existing caveat is about SEARCH DEPTH and is weaker and
different: search depth says nobody looked hard enough; finding 14 says one side
is NOT ALLOWED TO LOOK.** **Say both.**

## §2 — B1: the strongest pro-safety result is absent (one paragraph)

**RECAP finding 4, which RECAP calls *"the strongest thing here"*, appears
nowhere.** On `p02`'s one-byte overflow, **C prints a plausible answer and exits
0 in seven of eight builds**; the eighth aborts only under `_FORTIFY_SOURCE 3`.
Every Rust and hardened-C cell handles it. **Control: delete the check from safe
Rust and it PANICS rather than corrupting.**

**Put it in §3, as the measured counterweight that section does not have.**

## §3 — the other dropped results, in falling order of loss

| finding | what to restore |
|---|---|
| **7** | On `p01 large`, `c-clang` and `unsafe` execute **exactly `143 740 000`** kernel instructions — the cleanest *"Rust codegen IS C codegen"* datapoint in the tree. |
| **32** (price half) | **On gcc the undefined spelling is the DEAREST of its six neighbours; every fix saves exactly `6.00 Ir`/call.** The UB buys nothing and costs 6. |
| **35** | `p19`'s **sign flip**: the buggy C rung is `5071 Ir`/call cheaper at `small` and `3569` dearer at `large`, zero at `m ≈ 2509` — ⚠ *"a percentage quoted at either input is wrong in SIGN at the other"*. |
| **34** | *"the prover excludes the MECHANISM, not a spelling"*, at `3.00000 Ir`/dispatch. |
| **8, 23, 21, 5, 22, 17** | ⚠ **Judgement calls — the review says so.** **8** is the only model tested by *prediction*, which is the positive control §6 trap 2 otherwise never gets. **23** is the mechanism behind one of the nine "flat" rows currently quoted without one. **21** — `p12` is mentioned **once in the whole document**, in a list. **Restore what earns its place; say which you declined and why.** |

## §4 — the nine majors

| # | fix |
|---|---|
| **M1** | §2's `p09` row says *"half is a lost 8-byte load-merge idiom, not deleted checks"*. **No artefact says that.** The `NOTES` "half" is half of **`m_clampb`'s** win; the `+21/+1/−5` decomposition is the **R3-vs-R2 inversion**. ⚠ **`.memory/01-ladder.md` says of `R3 − R4` specifically: the three checks decompose with ZERO free parameters, predicted `48885.00` against measured `48885.00`.** **The record attributes it to checks; the document attributes half of it away. `p09` is the largest `R3 − R4` in the tree.** |
| **M2** | ⚠⚠ **Two do-not-reinstate figures used at their retracted values.** `p22` at `+2.00` — **the 510× retraction, which THIS DOCUMENT reports in §6 trap 1, 400 lines later, with no cross-reference** — and `p17` at `+32` (retracted *as a law*: swept, `R3ship − R4` runs `18…63`, and an in-contract R3 respelling measures `−19.00` flat). **Applying the record, the headline distribution becomes `8 / 4 / 10`.** |
| **M3** | *"All 20 survivors are gcc partial-inlining remnants"* is **false**: `p46`'s four `c-gcc`/`c-gcc-h` rows are `kernel`, and ⚠ **`results/synthesis.md` prints them four lines above the sentence.** So *"there is not one `whole`-mode row where the kernel column means what it means in `isolated`"* is false for those four. ⚠ **`results/synthesis.md` limit 1 and §5 claim 3 carry the same false sentence independently — fix `synthesize.py`, not the generated file.** |
| **M4** | `p27`'s `+230.07 / +792.75` is a **whole-program marginal** printed under §1's kernel-exclusive banner. Kernel-exclusive is **`+109.98 / +661.82`** — the reader gets **2.09×** what the convention promises. |
| **M5** | §7's unreviewed list **omits `TASK_100` and `TASK_098`**, both `Role: research reviewer` with no `*_REVIEW*` file — the same criterion by which it includes `TASK_109`. ⚠ **`TASK_100` is the source of the `p34` correction §3 rests on.** |
| **M6** | §4's `p42` result carries **no PROVISIONAL body marker** though it rests entirely on `TASK_109`+`TASK_110`, both unreviewed, and RECAP finding 39 marks it so. **p46, the stack-overflow case, §5 and p34 all carry body markers; the sharpest claim in §4 does not.** |
| **M7** | §2's new `9/4/9` aggregate is derived by `.temp/t108/census.py`, which is **gitignored and untracked** — **not re-derivable from a clone**, and `CLAUDE.md` rule 1 tells the next agent to delete it. **Move it to `synthesis/` (86 lines, reads one committed file).** |
| **M8** | §1 says the two `Ir` conventions disagree *"where the rungs call different library routines"* — **too narrow.** The two largest disagreements are neither: `p27`'s is the **safe side's out-of-line `drop_glue`**, and `p36`'s dispatch targets run `512/384/0 Ir` per call and **reverse** the control. |
| **M9** | gcc's **`endbr64` CFI term** is absent while gcc figures are quoted — `1.00000·nrw + 1 Ir` per call, gcc's column only. ⚠ **§1 exists to stop misuse and does not carry it.** |

## §5 — the twelve minors and one adjacent fix

**Take them all from `TASK_111_REPORT.md`'s minors list.** The ones with teeth:
**m1** `check.py` is **8434** lines, not *"~5 400"* — ⚠ **another stale cached
derivation, and its source sentence names its own denominator (19 patterns)**;
**m4** the `1.05×`–`3 536×` range mixes two populations and the cited census
prints `0.74×` as its low; **m5** `9+4+9=22` reads as a partition but `p18` is in
two buckets and **`p16` in none**; **m9** the bold lead *"Safe Rust can be worse
than C"* is a **refused headline verbatim** — the body retracts it correctly, but
**the bold is what gets quoted**, and no C rung was ever measured.

⚠⚠ **AND THE ADJACENT FIX THAT CHANGES A PUBLISHED CLAIM:
`synthesis/synthesize.py::SEARCH_REVIEWED` has 8 entries and is missing THREE
reviewed search results** — `p22` (`r4_reslice`, in contract, `20/0`,
byte-identical, `+125/+1021`), `p17` (`−19.00` flat, swept `18…63`) and `p06`
(`c_idx` at `0.00000 Ir`/byte). **So *"18 of 26 print `undeclared`, only five
report a real search"* is true of the table and UNDERSTATES THE RECORD BY THREE.**
⚠ **This is a `synthesize.py` edit ⇒ regenerate; it does not touch the gate.**

---

## Constraints

- **`.temp/t112/` only. No `/tmp`.** **Notes in `.temp/t112/NOTES.md`.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only** — the manager has landed the
  direction-bias trap and the two cross-file fixes already.
- ⚠⚠ **`results/synthesis.md` is GENERATED — never edit it. Fix
  `synthesis/synthesize.py` and regenerate**, then `licence.py --emit` **before**
  `synthesize.py`, then `outward_ir.py`, then **`synthesize.py` AGAIN** (its
  sidecar pin makes the second run mandatory).
- ⚠ **Do not run `check.py`, `build.py` or `measure.py`** except
  `measure.py --check-stale`. **No gate stage changes here; nothing you touch is
  measurement-hashed.**
- ⚠ **Read the RECORD for every number you restore, not the report.**
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_112_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 409.** The calls I am least sure of:

1. ⚠⚠ **That restoring coverage does not become advocacy.** The document's
   deflationary voice is its best feature and I am asking you to add six
   pro-safety items to it. **If a restored item does not survive its own
   conditions, LEAVE IT OUT and say so** — a synthesis that overclaims for safety
   is no better than one that overclaims against it, and this project has spent
   nineteen retractions learning that in one direction only.
2. **That §3's judgement calls (findings 8, 23, 21, 5, 22, 17) are worth
   restoring at all.** ⚠ **The review says explicitly that whether these *should*
   be represented is arguable, and only 4 and 14 are not.** **Decline freely;
   the report is where you say which and why.**
3. **That the document should stay one file.** ⚠ **It is 636 lines and about to
   grow. If the honest structure is a short argument plus a longer evidence
   appendix, say so** — but ⚠ **do not solve a length problem by cutting
   coverage again, which is the exact failure you are repairing.**

Carry **409** forward, incremented by what you find.
