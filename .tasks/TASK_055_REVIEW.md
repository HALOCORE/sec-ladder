# TASK_055_REVIEW — the `raw_ptr` probe, and the TCB decision it forces

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_055.md` and **`.tasks/TASK_055_REPORT.md` in full**, then
`.memory/04-verus.md` (the TCB accounting section — **the manager edited it at
`3a0458d`, and that edit is in scope for you**), `.memory/03-measurement.md`
(the null-control section at `:802`, and `:784` on tcache metadata), and
`.memory/02-bench-rules.md`.

The probe's sources and logs are under `.temp/p55/` — `repro.sh [all|probe1|probe2]`
regenerates every number. **Probe 1 is LANDED and not under review** (p08 is TCB
4 → 3, gate-green, `identity: exact` at both levels). **Probe 2 is under review**,
and nothing from it has been built.

## Why this review exists

The probe concludes *"a lifetime bug CAN have a full six-rung ladder"*, and
RECAP now calls that **the biggest open opportunity on the project**. It is
`.memory/`-recorded as **PROVISIONAL / unreviewed** precisely because no one has
attacked it. **Nothing gets built on it until you have.**

⚠ **PROTOCOL rule 3 applies to part of this.** The *formulation* in §2.8 (a slab
with pointer handles at R4/R5 and `(slot, generation)` at R1h/R2/R3) is the
**engineer's**, not the manager's — attack it freely. But the **TCB decision in
§ below is the manager's own**, and it is the thing the pattern is blocked on, so
say explicitly whether you are clearing the manager's design.

## The five attacks I most want run, in priority order

**A1 — the zero-trusted-items claim rests on scaffolding the probe did not
replace.** §2.5 concludes a `raw_ptr` rung contains no project-local
`external_body` at all, and therefore publishes `tcb_items = 2`. But the report's
own *"What I did NOT do"* says the permission map in `p2d_loop.rs` is populated
by `Tracked::assume_new()` inside an `external_body main`, and that **a real
pattern needs a ghost loop that splits the `PointsToRaw` `n` times under an
invariant, which was never written.**

> **Write that loop, or show it cannot be written at the pinned vstd.** If it
> needs a project-local `external_body`, or an `assume`, the entire §2.5 alarm is
> an artefact of the scaffolding and the TCB decision below is moot. If it
> verifies clean, the alarm is real and the decision is forced. **This one
> question decides whether the next pattern is buildable.** Report the SMT cost
> too — the probe flags a 4096-slot map as unmeasured.

**A2 — reproducibility was never tested under the tool the gate actually uses.**
§2.7's fold-from-offset-16 result was measured on **native** runs. The gate reads
`Ir` under **callgrind**, and valgrind replaces the allocator wholesale, so
glibc's tcache metadata may never be written into the freed chunk at all.

> Run the §2.7 binaries under `~/tools/valgrind/bin/valgrind` and compare the
> checksum to the native one. **If they differ, stage 2's cross-cell agreement
> breaks and the pattern is not buildable as specified** — that would be a
> blocker, and it is one nobody has named. While you are there: check stability
> across ASLR (`setarch -R` vs not) and across a changed environment block, since
> `.memory/03-measurement.md:1099` records that the environment block does not
> always cancel.

**A3 — is the R5 story new, or is it p08 wearing a different hat?** §2.6 says the
UAF is rejected by **rustc's move checker (E0382)**, not by a failed SMT
obligation. Two consequences to test, not to reason about:

- p08 is already *"the bug safe Rust cannot express"*. If R5's catcher is
  linearity, is this a **second instance of p08's finding** rather than a new
  class? Argue it either way, with the mechanism.
- **The gate requires two proof mutants that FAIL.** If no obligation ever fails
  — because the bug is a type error, not a verification error — **can a mutant
  fail the gate at all?** Check `check.py`'s mutant stages against a
  linearity-caught bug. A pattern that cannot produce a failing mutant does not
  clear the gate, and that is a build blocker, not a prose issue.

**A4 — §2.4's "byte-identical" is a draw of size one.**
`.memory/03-measurement.md:802`: the R4/R5 pair is a **smoke alarm, not a null
control**, and the offset between them is a **source-path-length artefact**. The
probe ran its comparison at one path under `.temp/p55/w1755898/`. Does the
identity survive a path-length change? If not, say what §2.4 actually licenses.

**A5 — the semantic-equivalence question, which the probe raises and leaves
open.** §2.8 caveat 2: R2/R3 are **not "R4 plus a check", they are a different
data structure**. The reviewer checklist asks *"are the five rungs semantically
equivalent, or did a rung quietly change the algorithm?"* and the proposed answer
is a functional-equivalence argument rather than a diff.

> Is that admissible under `.memory/02-bench-rules.md`? If it is, **what exactly
> would the argument have to establish** for the resulting `R2 − R4` number to
> mean anything? If it is not, the pattern needs a different formulation and you
> should say so now rather than after five rungs exist. Note also caveat 1: only
> a **real `deallocate`** makes this the missing class — a freelist push makes it
> p17's logical-bug class, which the tree already has.

## The manager's TCB decision, for you to attack

The problem, if A1 survives: `tcb_items` would rank a **raw-pointer kernel as
safer than a bounds-checked one** (2, versus p02's 4), while the verified-twin
regime goes idle and prints *the same sentence the known macro bypass produces*.

**My proposal — the smallest thing I can find that fixes it:** keep `tcb_items`
as one number, and publish beside it a **`tcb_reach`** naming *how the rung
reaches unchecked memory* — `safe`, `local-external-body`, or `vstd-axiom`. p01
becomes `2 / safe`, p02 `4 / local-external-body`, a `raw_ptr` pattern
`2 / vstd-axiom`. The number stops being comparable across reach classes, which
it never was.

**Attack it.** Specifically: (a) is `tcb_reach` decidable from the source, or does
it need a judgement call per item — the property that killed the two-number
proposal by census? (b) does it need `harness/` work, and does that work pass
*"could this happen by accident?"*, or is it a reported field where that test does
not apply? (c) is there a cheaper answer that is only prose? (d) does the idle
twin regime need a **separate** fix regardless, since a legitimate `raw_ptr`
pattern and the macro bypass becoming indistinguishable is a soundness-reporting
problem independent of the column?

## Also in scope

- **The manager's `.memory/04-verus.md` edit at `3a0458d`** — I claimed both
  named exposures are closed, recounted the denominator to 62 items over 16
  patterns from `results/gate/*.json`, and said the numerator is not recountable.
  **Recount it yourself.** If p08's `copy_in` relocation makes some *other*
  item newly exposed, or if my recount is wrong, that is a finding against the
  authoritative layer.
- The withdrawn `Vec`-growth explanation (§2.7's parenthetical) — was the
  withdrawal complete, or does the wrong explanation survive anywhere?
- §2.7's two fiats (the 16-byte constraint is a glibc detail; `same_chunk` is not
  portable, gcc printing `1` where clang and rustc print `0`). Would a `spec.md`
  actually be able to carry those, and what does the gate do with a fiat?

## Clean negatives are wanted

PROTOCOL rule 6: **a named attack that did not land is worth as much as a
finding**, and stops the next agent re-running it. p06's review returned
fourteen; that is the bar. List every attack you ran, with its outcome.

## Constraints

No root; no `/tmp` (scratch `.temp/p55rev/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, `common/`, or any pattern's sources —
**you are a reviewer, you report and do not fix.** You may write probe sources
and logs under `.temp/p55rev/`. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`;
**no `nohup … &`**; no self-matching `pgrep` wait-loops. ⚠ **Do not run
`harness/check.py` on any pattern** — it rewrites that pattern's gate JSON and
another agent is working in this tree. Read `results/gate/*.json`; do not
regenerate them.

**Write your report to `.tasks/TASK_055_REVIEW_REPORT.md` before you finish** —
PROTOCOL rule 10 exists because a review's citations once pointed at a file that
was never created. Then return the same content in the report format.

Rank findings `blocker` · `major` · `minor`, with file:line and a concrete
failure scenario. **Do not pad — 3 real blockers beat 20 nitpicks.**
