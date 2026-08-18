# TASK_017_REVIEW — a judgement that makes its own number look better

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_017.md`,
`.tasks/TASK_016_REVIEW_REPORT.md` (B1, M1, M2, M3 — what TASK_017 was repairing),
`git show 89f6598` and `git show 95cfa47`, `harness/check.py` stage `0b`,
`harness/report.py`'s new idiom section, and the six `patterns/*/spec.md`
`idiom` blocks.

## Context

TASK_016_REVIEW proved the idiom key's advertised mechanism false by forking p05
with the forbidden spelling and gate-passing at an identical `contract_sha256`.
TASK_017 repaired the claim, made `report.py` print each declaration above its
table, fixed three declaration defects, and disambiguated p16's `required[0]`.

All six gates are green. The thing that needs attacking is not a number.

## Part 1 — the p16 reading, which is the whole review

p16's `idiom.required[0]` was ambiguous: it requires `end - p >= 3` and
`vlen > end - (p+3)` "in every rung", while the block also called
`split_first_chunk::<3>()` — which contains neither comparison — admissible.
TASK_017 resolved it as naming **tokens**, so the cheaper spelling is now **out
of contract**.

**Both readings are true of the shipped tree** — the engineer checked, and every
rung literally contains the tokens — so no experiment decides this. It is a
judgement, and it has a direction:

> **The chosen reading makes p16's own published number look better**, by putting
> its cheaper competitor out of contract.

The engineer raised this itself and tried to neutralise it by recording, in three
places, that p16 now has **zero measured admissible alternate spellings**, so
"the shipped R3 is the cheapest admissible one" is *unestablished, not
established*. Judge whether that is sufficient.

Attack the four grounds given, each on its own merits:

1. **House convention** — `required` entries elsewhere constrain *shape*: p05's
   "written out in every rung", p02's "spelled identically in every rung", p17's
   "the one conjunctive guard, **not two `continue`s**", which rejects a
   semantically identical spelling. Is that a real convention, or three
   selectively-read strings?
2. **The tokens *are* the traversal** — pinning them is what makes `R3 − R4` a
   safety difference rather than a representation difference. Does that hold?
3. **The exclusion falls symmetrically** — the consuming *R4* control goes out
   with the consuming R3s, so the reading does not protect the shipped safe rung
   by excluding only its competitor. **Verify this**; it is the strongest of the
   four and the easiest to check.
4. **`inf(R4) <= inf(R3)`** — under the semantic reading both rungs become
   permission-defined and the pair has no fixed point (finding 14).

**Then answer the question that matters: would a disinterested party, given only
p16's `spec.md` as it stood before TASK_017, have read it the same way?** If not,
say what the honest alternative is — including "the declaration was genuinely
ambiguous and should be rewritten to say something neither reading captures".

## Part 2 — did the repair actually repair it?

- **The false mechanism sentence.** Confirm it is gone everywhere — `check.py`,
  `TASK_016.md`, `.memory/` (the manager's edits), the six `spec.md` blocks — and
  that what replaced it is *true*. Re-run TASK_016_REVIEW's fork experiment
  against the repaired tree if that is cheap: the behaviour should be unchanged
  (it still passes) and only the description should differ. If the new wording
  now over-corrects into implying the key is useless, say so.
- **`report.py`.** The declaration is printed above every table. Check it is read
  from `spec.md` and not the gate record, that all six tables regenerate with
  pure additions, and — the point of the change — that a reader quoting a number
  from `results/tables/*.md` now cannot miss what the pattern forbids. Is it
  actually prominent, or is it a header nobody reads?
- **p02's R1 carve-out** and **p05's restored bullet** — verify against the rung
  sources, not the prose.
- **The duplication decision.** TASK_017 kept the prose *and* the JSON, with each
  prose section naming the block as authoritative. Two copies that can drift, by
  choice. Was that right?

## Part 3 — the numbers TASK_017 corrected

- **M1's "the sign flips" was refuted** — no p16 delta changes sign; five of
  eight rows move (the review had omitted both hardened-C rows), by +1.42 gcc /
  +0.42 clang / −1.00 R5. **Verify the corrected table**, which now lives in
  `patterns/p16-tlv-walk/NOTES.md` §10 and `.memory/03-measurement.md`. This
  number has now been stated three times and corrected twice.
- **The env-block finding.** `marginal_ir_per_call` moves with the environment
  block on p08 (7292.26 / 7292.24 / 7292.14 at PAD 0/200/400) and is invariant on
  p16 (3009.30 ×3), attributed to glibc `memcpy`/`memmove` path length varying
  with buffer alignment. Reproduce it, and check the attribution — alignment is
  the plausible story, not a demonstrated one. If it is real, does it threaten
  any published p08 number?
- **The invariant**: 28/28 `md5_fn` unchanged, 541/564 `marginal_ir_per_call`
  unchanged with all 23 movers being p08 and ≤0.08 Ir/call. Verify from git.

## Part 4 — clean negatives

Name what you tried that did not land.

## Not in scope

Do not land a cell swap; do not edit `harness/`. Do not re-measure p01/p02.

## Deliverable

`.tasks/TASK_017_REVIEW_REPORT.md` + `PROTOCOL.md`'s format. **One line at the
top: is p16's token reading defensible, or is it a declaration written to protect
a number?**

## Constraints

No root; no `/tmp` (scratch `.temp/review017/`); **no `git add`/`git commit`**;
do not edit `pilot/`, `.memory/`, `harness/`, or `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` into `.temp/review017/`.

Notes to `.temp/review017/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty agents
have contradicted the manager's written instructions and all twenty were right.
The manager's position on Part 1 is that it **does not know** whether the token
reading is right, that it would have accepted either answer, and that the
engineer's own flagging of the risk is a point in favour of the work rather than
against it — but that a self-serving reading is exactly what a review exists to
catch, and the fact that it was self-reported does not make it correct.
