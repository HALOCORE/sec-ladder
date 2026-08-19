# TASK_028 — delete a refuted sentence from six hashed blocks, and stop publishing a pair interval

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_027_REVIEW_REPORT.md`
in full** — its Q2 blocker is this task — then `.memory/01-ladder.md`'s
R4-by-permission paragraph and its p05 entry, **both already corrected by the
manager and the wording to follow rather than re-invent**, and
`patterns/p05-index-flatten/NOTES.md` §14.

`.memory/` and `RECAP.md` are done. **The six patterns' hashed blocks and p05's
prose still carry the refuted text, and `.memory/` is the one to believe** until
you land this.

## This is a deletion, not an investigation

Every number below is already measured and reproduced in the review report, with
Verus logs. **Do not re-derive them.** The work is finding every site and
removing refuted text without breaking the byte-identical shared paragraph. It is
the thirteenth task on the spelling problem and the last one: the next task is a
new pattern.

## What was measured

The sentence *"it moves the UNSAFE rung too, by the same lever: p16's by `4·nrec`
(TASK_023), p05's by 7 flat (TASK_022)"* names **one lever** — respelling the
header read — and **it is not admissible on either pattern**. All six patterns pin
`identity: unsafe ≡ verus, O3 exact`, so a rung needs a byte-identical R5 that
Verus verifies, and at the pinned vstd every route to that respelling is
`is not supported`: `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
`TryFromSliceError`, `from_le_bytes`. Seven twins, `rc` and error text in the
report. It costs a **new trusted item**, which is exactly what disqualified
`r4_hdr` on p16.

Consequences, all of which are published today:

- **"p05's R4 moves 7 flat" has no rung behind it.** The cheapest *measured and
  admissible* p05 R4 is the shipped cell, at 0.
- **Both endpoints of p05's pair interval `2·nrow − 2 … 6·nrow + 20`
  (36…134 / 128…410) are inadmissible R4s** — `r4_dataslice` (dearest) and
  `c4_hu16_nz` (cheapest). Substituting the admissible class gives
  `5·nrow + 6 … 6·nrow + 13` = **101…127 / 331…403**, width `nrow + 7` = 26 / 72,
  which is *exactly* the R3-side-only span the pair interval was introduced to
  replace.
- **"An admissible pair exists whose tax is exactly 0.00"** (`sweep-r1c30`) —
  **withdrawn**; that pairing's R4 is `r4_dataslice`.
- **TASK_021's original claim was right for the wrong reason.** The unsafe side
  does not move — not because six agents happened to spell the header the same
  way, but because the `identity` pin leaves them nothing else to spell it with.

## What to land

**Prose first, gates last.** `source_sha256` globs `patterns/*.md`, `harness/*.py`,
`common/*`, `controls/*.py`, `inputs/gen.py` and `verus_run.py`.

1. **The shared sentence, in all six hashed `why` blocks.** It is **byte-identical
   across the six by design** — `diff` them before and after; if your replacement
   is not byte-identical in all six you have broken the property the block
   asserts about itself. Replace it with what the measurement supports: the lever
   is *not admissible on either pattern*, neither R4 side has moved by a single
   admissible instruction, and the reason is the `identity` pin rather than
   anything about the patterns.
2. **Stop publishing a pair interval, everywhere.** Both that this project has
   published were built from R4s that are not rungs. What ships is the **fixed-R4
   bound** — `R3ship − R4ship` bounds `inf(in-contract R3) − R4ship`, R4 held by
   fiat — and an **R3-side span**. Say plainly that a pair interval is not
   available until someone builds an admissible R4 that moves.
3. **p05's `NOTES.md` §14 and `README.md`**: the interval, the `0.00` free
   pairing, the `−7`/`−5`/`−2` decomposition, and the "R4 moves 7 flat"
   sentences. Sites in the report's Q2 memory-update list; **grep rather than
   trusting it**. Keep the history — this project's files record refutations, they
   do not erase them — but make the current claim unmissable.
4. **p16's `spec.md` R4-expressibility sentence needs "AT THE PINNED VSTD".** The
   `r4_hdr` instance three lines away already carries it; the general sentence
   does not, and as written it is a hashed claim about a tool version with no
   version in it. Add beside it the distinction the review measured: **`is not
   supported` disqualifies (it forces a new trusted item); "postcondition not
   satisfied" disqualifies nothing** — the same p05 exec code went from
   `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one
   `proof` block, at zero TCB.
5. **`harness/check.py:56` and `:1723`** say the identity pin is *"a RESULT, not a
   gate condition"*. That is **false** — `rep.fail` at `:1763` makes it
   `verdict = "FAIL"` at `:4826` — and it is the one sentence in the tree that
   argues against the step everything above rests on. **Comments only; change no
   logic.** This is the single exception to the usual no-`harness/` rule and it is
   free here, because `harness/*.py` is inside `source_sha256` and you are
   re-running all six gates anyway.
6. **p16's two minors from the review.** `NOTES.md:1535` says "reproduce the whole
   table" and `foldcmp.py` reproduces **8 of 10 rows** — the two manual-unroll
   rows carry `—` and are not derivable from the committed tree, so either mark
   them or generate them. And `controls/gen_controls.py`'s docstring says both
   "eighteen" and "sixteen" variants; **18** is right.

## Explicitly NOT this task

**Do not build the unbuilt spellings.** p05's `−2` residue (delete the redundant
zero-guard, keep the shipped header — verifies at zero TCB, `13 verified, 0
errors`, but was never compiled because all 26 of TASK_022's round-3 variants pair
it with `read_unaligned`) and p16's hand-unrolled 32× fold with explicit indices
are **queue item 2a**. They are the open question and they deserve their own task,
not a ride-along on a correction sweep. Say in your report which of the two you
would build first and why, in one paragraph.

## Done when

All six items land; **all six gates green** (this is the first task since TASK_016
to re-run the whole set — budget for it); the six `why` blocks diff byte-identical
on the shared paragraph; `md5_fn` unchanged everywhere; `results/tables/*.md`
regenerated with `harness/report.py`, never hand-edited.

Expect gate-record churn on an unchanged tree — ~32 leaves, p08 alone contributing
23 across four opt/mode combinations to ±0.08 (`.memory/03-measurement.md`).
**Subtract that before attributing anything to your edit**, and note that
`harness/check.py` moving puts a new `source_sha256` entry in all six records
legitimately.

## Constraints

No root; no `/tmp` (scratch `.temp/p28/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. Prose, `controls/*.py`, `inputs/gen.py`, and
**`harness/check.py` comments only per item 5** — no harness logic, no cell
source. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill.

**Run measurements in the FOREGROUND** — background `nohup` jobs on this box are
reported "completed" while still running. Per-PID scratch paths.

Per `.memory/00-environment.md` constraint 6, **delete your binaries and generated
blobs when the gates are green and keep your scripts, notes and results.**

Notes to `.temp/p28/NOTES.md` as you go so you can be resumed; three agents on
this arc have died to transient API errors.

**If a prescription here is wrong, say so with the measurement.** Thirty-four
agents have contradicted the manager and all thirty-four were right. The last one
proved that a refutation *I* landed at TASK_022 was itself wrong, which means
TASK_021's original claim had been right all along and I overturned it on a
spelling that cannot exist. What I am least sure of here is **item 2** — whether
"no pair interval until someone builds an admissible R4 that moves" is the honest
position or an over-correction that will read as evasion. The alternative is to
publish the pair interval over the *admissible* class, which is currently a single
point on both patterns and therefore identical to the fixed-R4 bound. If you think
that framing is better, argue it.
