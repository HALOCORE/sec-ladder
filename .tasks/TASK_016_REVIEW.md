# TASK_016_REVIEW — are the six declarations honest, and would the key have caught the thing it exists for?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_016.md`,
`.tasks/TASK_015_REVIEW_REPORT.md` **B2** (the defect the key exists to prevent),
`git show 4bd7deb`, `harness/check.py` stage `0b`, and the six
`patterns/*/spec.md` `idiom` blocks.

This is a `harness/` change implementing **the manager's own design**, so
`PROTOCOL.md` rule 3 applies: a different agent has to attack it.

## Part 1 — the failure mode a self-declared idiom actually has

`.memory/02-bench-rules.md` warns that a declared-and-then-measured constraint is
self-certifying. TASK_015_REVIEW argued the risk is answered by declaring
*before* measuring — which is true of p05 and p17, whose text was written at
TASK_013 and TASK_011. **It is not true of p01, p02, p08 and p16, whose
declarations were written at TASK_016, after every one of their numbers was
published.**

So: **are those four declarations honest descriptions of what the rungs do, or
post-hoc rationalisations of what they happen to be?** Read each rung's source
against its `idiom.required` / `idiom.forbidden` and judge. Two specific probes:

- **Is anything declared `required` that a rung does not actually do?** That is a
  declaration written from the spec's prose rather than from the code.
- **Is anything *conspicuously absent*** — a spelling choice that visibly drives
  that pattern's headline number and is not mentioned? That is the shape that
  matters, because it leaves the number unprotected while looking protected.
  p02's `memcpy` idiom and p16's unroll are the ones I would check first.

The engineer says nothing was invented and that p01's and p16's `why` state which
spellings are *not* restricted. Verify that claim rather than accepting it.

## Part 2 — run the counterfactual, which is the only real test

The key was built to stop this: two consecutive tasks measured a spelling p05's
`spec.md` forbade **by name**, and reported it as p05's number.

**Would it now be caught?** Work it through concretely, and prefer a
demonstration to an argument:

- The check does **not** stop an agent from *building* a forbidden spelling — by
  design; it only requires, prints and hashes the declaration. So the mechanism
  is entirely "the reviewer sees it". **Does the verdict output actually surface
  it?** Run a gate and look at where `idiom` appears relative to everything else
  a reviewer scans.
- If your honest answer is "an agent in a hurry would still miss it", say so —
  that is a real finding, and better learned now than after the next retraction.
  A cheap suggestion (e.g. printing the `forbidden` list in the *failure* summary
  too, or in `report.py`'s tables) is welcome; do not implement one.

## Part 3 — does the check have teeth?

- Re-run the 8 selftests, then attack the check itself: a vacuous one-word `why`;
  `required` containing an empty-ish string; a declaration that contradicts the
  prose two hundred lines above it in the same file; `forbidden` listing
  something no rung could ever use. Which of these pass, and should they?
- **Confirm the empty-`forbidden` path shouts and does not fail** — and confirm
  that is right. `MAX_TWIN_JUSTIFICATIONS` was deleted for hard-failing an honest
  pattern; check the new key cannot do the same.
- The engineer reports **+145/−0 lines, ~65 net logic**. Confirm nothing else in
  `check.py` changed behaviour — this is the first `harness/` edit since the
  hardening arc closed and it must not have moved anything else.

## Part 4 — the invariant, verified independently

The claim is **28/28 `md5_fn` unchanged and 564/564 `marginal_ir_per_call` cells
unchanged**, with `contract_sha256` moved in all six. Check it from git rather
than from the report: `git show 9272a41^:results/gate/<p>.json` against the
committed one. A single moved `md5_fn` means a cell source changed and the whole
"no measured column moved" claim fails.

## Part 5 — the owed decision, which I want adjudicated not just noted

p16 and p17 declare no restriction on the fold/walk spelling, so a cheaper
**admissible** R3 exists for both — p16's `split_first_chunk::<3>()` measures
`10·nrec + 9` cheaper than the shipped R3.

That means p16's and p17's published R3 numbers are *spellings' numbers by their
own declaration*, which is exactly what finding 14 says may not be headlined.
**Adjudicate: swap the cells, or state the limitation in each `NOTES.md`?**
Argue it, with the retrofit cost. Do not land either.

Related: the engineer chose **not** to add a restriction to p16 that would have
excluded the cheaper spelling retroactively. Was that the right call?

## Part 6 — the two smaller claims

- **Two mis-targeted cross-references, not one** (p05's and p08's `collapse.note`
  both said "NOTES.md 4"/"7" and meant §9). The engineer swept all 15 by
  *content* where the previous review swept by existence. Spot-check the sweep.
- **Two `Ir` conventions in shipped patterns** — p16's `NOTES.md` §2 is
  kernel-exclusive, p05's and p17's whole-program marginal, uniform +14.30 offset
  on p16. Verify the offset and that **no published delta moves**.
- The engineer struck p05's `NOTES.md`/`README.md` "+11.00 flat, `O(1)`" claims,
  which were still unstruck. Confirm nothing refuted survives unstruck anywhere
  in `patterns/`, and check `RECAP.md` and any top-level `README.md` too — the
  engineer explicitly did not audit those.

## Part 7 — clean negatives

Name what you tried that did not land.

## Not in scope

Do not land a cell swap. Do not implement a check.py change — report it.

## Deliverable

`.tasks/TASK_016_REVIEW_REPORT.md` + `PROTOCOL.md`'s format. Severities with
file:line and a concrete failure scenario. **Two lines at the top: (a) are the
four post-hoc declarations honest, yes or no; (b) would the key have caught the
TASK_014/015 defect, yes or no.**

## Constraints

No root; no `/tmp` (scratch `.temp/review016/`); **no `git add`/`git commit`**;
do not edit `pilot/`, `.memory/`, `harness/`, or `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` into `.temp/review016/`.

Notes to `.temp/review016/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Eighteen agents
have contradicted my written instructions and all eighteen were right — the last
one overturned my objection to its own task design using git history. What I am
least sure of here is **Part 2**: I suspect the honest answer is that the key
would *not* have caught it, because nothing forces a reviewer to read the
declaration, and if so I would rather know that than ship a check that makes us
feel protected.
