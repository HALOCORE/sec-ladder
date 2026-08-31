# TASK_153 — land `p35`'s review corrections, bundled into ONE re-measure

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠⚠⚠ **BUNDLED BECAUSE EACH ITEM COSTS THE SAME RE-RUN.** `c/kernel_hardened.c`
and the `*.rs` rungs are in `measure.py::measurement_sources`, so **M1 and M4
cost a `p35` RE-MEASURE**; `spec.md` and `controls/*` cost a **re-gate** only.
**Budget one re-measure and one re-gate. Do not run either twice.** ⚠ **Make
every measurement-hashed edit BEFORE the measure run** — `measure.py` hashes
`measurement_sources` at line 450, **above** the loop, so a mid-run edit wastes
the whole run (`.memory/03-measurement.md` entry **20**; `TASK_150` paid two).

Read first: `.tasks/TASK_152_REPORT.md` **in full**; `.tasks/TASK_148_REPORT.md`;
`patterns/p35-tagged-union/`; `RECAP.md` finding **58**;
`.memory/03-measurement.md` entries **12, 19–22**; `PROTOCOL.md` **rule 6**.

## ⚠⚠⚠ M1 — *"R3 beats R4 by 5.3%"* FALLS. The R4 side was never searched.

**Sixth instance of this project's most-repeated defect**, and the first caught
by a review that was pointed at it on purpose.

```
record, reproduced independently   safe_tuned 3060.92   unsafe 3231.48
R4 given R3's OWN TWO LEVERS       2857.87   <- R4 WINS BY 6.6%, checksums identical
```

✅ **The honest number is what the `identity` pin COSTS R4: `373.61` Ir/call, not
`170.56`.** ⚠ **And R3's *reslice* lever DOES verify at the pin — so it was
available all along.** ✅ Only `chunks_exact` is genuinely `is not supported`
(re-measured; that half of the build's claim was right).

**Decide and justify, in `NOTES.md`:**

- **(a) RESPELL R4 with the levers** and publish the pair honestly, or
- **(b) KEEP the shipped R4 and publish `373.61` as THE PRICE OF THE `identity`
  PIN**, saying plainly that R4-with-levers wins by 6.6% and why that spelling
  is not shipped.

⚠⚠ **(b) is the manager's guess — the `identity` pin is the reason R4 is spelled
as it is, and pricing the pin is a REAL result — but the manager may be wrong.
Whichever you take, the sentence *"R3 beats R4"* must not survive in any
file.** ⚠ **Search BOTH rungs' spellings and count the levers on each side, and
say which side is the weaker-searched endpoint.**

## ⚠⚠⚠ M2 — the coin-flip band claim is FALSE, and it is inside the HASH

`idiom.why` (hashed) and `RECAP` 58 both said the four cost figures are **"all
outside the coin-flip band"**. ✅ **Manager-verified against the project's own
published standard: `|−13.71| = 13.71` is squarely INSIDE the `2.00 … 16.00`
band `results/synthesis.md` labels *"a coin flip — DO NOT QUOTE ALONE"*.**

✅ **The conclusion SURVIVES on the `O0` figures the build report never used** —
use those, and **say which band each figure is in** rather than asserting a
blanket. ⚠ **RECAP 58 is already corrected; the manager owns it. Fix the hashed
`why` and any rung header carrying it.**

✅✅ **AND THE *"MECHANISM OPEN"* HEDGE CAN GO — this is the good half.**
`32.76` was the wrong denominator; **the marginal window gives `32.90`, and with
it the mechanism CLOSES at exactly `5.0000` `Ir` per failed tag store, on ALL
FOUR `O0` cells, on BOTH compilers.** **Land the closed mechanism.**

## ⚠⚠ M3 — the variant conjunct CAN be specified away, and it makes the headline STRONGER

New arm **X1**: delete the variant conjunct from all three trusted readers'
`requires` → **`16 verified, 0 errors`**, pinned count unmoved. Planted into the
tree, the gate FAILs only on `proof-pin` — **a declaration the author writes** —
while verus `16/0`, `identity exact` and Miri `0 UB` all stay green. ⚠ **The
strength check designed for exactly this is one of the three BLOCKED rows.**

✅✅ **SO THE HEADLINE SHARPENS: configuration B RESISTS the same deletion and
configuration A does not.** **The gate does not merely force a weaker proof — it
forces the one whose central obligation can be DELETED WITHOUT THE GATE
NOTICING.** ⚠ **Add `X1` to `controls/proof_mutants.py` and re-derive its
verdict rather than quoting it. Say plainly what the shipped configuration's
obligation rests on.**

## ⚠⚠ M4 — `p46`'s defect again, in a MEASUREMENT-HASHED source

`c/kernel_hardened.c:14-16` **still carries the clause rule 6 retracted** —
*"a scheduling difference and nothing more"*. **The `TASK_148` sweep fixed the
fence, the prose and the `README` and missed this one file.**
✅ **The rule-6 disclosure itself verifies exactly** — the reviewer reconstructed
`141fb37c…` from the shipped `spec.md`, so the mechanism works and the coverage
did not. ⚠ **Grep every file for the retracted clause, not just the one the
reviewer named.**

## ⚠ M5 — the axiom is WIDER than the twin justification says

`unsafe { v.get_unchecked(i).i }` is **two** unchecked operations, and the twin
justification describes one. **Configuration C** exists, is gate-legal (the real
`_scan_unsafe_sites` → 0 failures), verifies `2/0` and `3/0` with the twin, and
**moves the index into a twinned item — the split this pattern's own WRITE side
already does.**

⚠⚠ **DECIDE: adopt configuration C, or keep the shipped one and CORRECT THE
JUSTIFICATION to name both unchecked operations.** ✅ **Either is defensible;
shipping a justification that describes one of two is not.**

## ⚠ Minors — all from `TASK_152_REPORT`

1. **The hashed `miri.reason` omits initialisedness** — measured: `Pay{o:..}`
   then reading `.i` **is** Miri-reported UB. Add it.
2. **Five stale catalogue claims, and a decayed citation `check.py:3941 →
   3972`.** ⚠ The catalogue is `.memory/` and is the MANAGER's — **list them in
   your report; do not edit that file.**
3. **`results/synthesis.md` says `Patterns: 29` and mentions `p35` ZERO times.**
   ⚠⚠ **`p35` IS THEREFORE NOT FINISHED. Regenerating it is part of this task.**

## ⚠ NOT in this task — recorded so it is not silently absorbed

- **Stage 9b hashes a control sidecar and never reads its own verdict.** ⚠ A
  `check.py` change is a **30-pattern re-gate** and is a different bundle.
  **Report it; do not fix it.**
- **`RECAP` 58 and `CAVEATS["p35"]`** — the manager owns those and has applied
  M1, M2, M3, M5 and the clean negatives already.

## Then

`harness/check.py p35` → PASS (⚠ expect `blocked = 3`, which is the row's
result) · re-measure `p35` · `harness/report.py p35` if the gate fails on
`[tables]` · then `harness/measure.py --check-stale` (expect **0 STALE**),
`harness/tools/composition.py --check`, `harness/tools/temp_citations.py`,
**`python3 synthesis/licence.py --emit synthesis/licence.json`** and then
**`python3 synthesis/synthesize.py`**. ⚠⚠ **The licence step is REQUIRED and its
`--emit` TAKES A PATH — bare `--emit` exits `rc=2` and writes nothing.**
⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER regenerate over
it.**

## Rules

- `.temp/t153/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
  **Copy from `t152/`; do not modify it.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD — never `grep` the log, not
  with a regex alternation, and not with a loop matching a prefix a log header
  shares with its verdict.** Three mechanisms, one cure
  (`.memory/03-measurement.md` 21–22, finding 58).
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`;
  every harm probe owes a positive control that must fire **in the detector
  whose column it licenses**.
- ⚠ **State your re-measure prediction BEFORE running it**, then compare.
  `TASK_150`'s was an exact hit; `TASK_147`'s too. **`*.rs` and `c/*` change
  here, so `Ir` and `md5` moves are LEGITIMATE — say which you expect first.**
- ⚠ `python3 harness/tools/contract_diff.py p35` for the rule 6 disclosure.
  ⚠⚠ **`p28` shipped with NO rule 6 disclosure and that evidence is
  unrecoverable; `p35`'s previous one verified exactly. Keep that standard.**
- Keep the generator, delete the artefact.
- ⚠ **If any item costs more than this file says, STOP AND REPORT rather than
  half-landing it.**
- Report to `.tasks/TASK_153_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_152_REPORT.md`'s closing paragraph — read it there, do not guess.**
