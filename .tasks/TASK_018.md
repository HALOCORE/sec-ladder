# TASK_018 — one standard for all six declarations, adopted openly

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_017_REVIEW_REPORT.md`
**in full** — its blocker B1 and its "disinterested party" finding are this
task's entire basis — plus `.memory/01-ladder.md` finding 14 and the rung
definitions at the top of that file.

## The decision, which is mine and which you should attack if it is wrong

TASK_017 read p16's `idiom.required[0]` as naming **tokens**. TASK_017_REVIEW
found that the same commit **refused that standard for p17**: `tuned_suffix.rs`
has no `end` binding in code at all, and TASK_017 nonetheless wrote into p17's
`NOTES.md` that it *"satisfies all four of p17's `required` entries: i64
endpoints, the one conjunctive `if start < end && start >= 0`"* — false of the
file. p17 is the very precedent p16's own `why` cites for the token standard.

**Resolution: adopt the token standard, uniformly, across all six patterns.**
My reasons, and I want them tested, not implemented on authority:

1. It is the reading that makes `R3 − R4` a **safety** difference rather than a
   **representation** difference, which is the only thing the declaration exists
   to buy.
2. The suspicion that it is self-serving was **measured and refuted**: it makes
   p16's published safety tax **4.5× larger** (+27/+77 shipped against +7/+17
   for the excluded matched consuming pair).
3. It is the only reading that partitions cleanly — the review notes the
   ambiguity was arguably three-way, with one variant satisfying the property
   *vacuously*.

**Three conditions are not optional**, and they are the review's findings, not
my preferences:

- **Label it as a policy adopted at TASK_018 after measuring**, in every `why`.
  It is **not** a disambiguation of what the text always meant, and presenting it
  as one is the self-certification the whole mechanism exists to prevent.
- **Restore p16's deleted disclosure.** The pre-TASK_017 `why` said the walk's
  spelling was *"NOT restricted"* and that a consuming spelling *"is admissible
  under this declaration"*. TASK_017 deleted that and kept *"declare the walk's
  spelling here BEFORE measuring"* verbatim — which is incoherent under the new
  reading, and the deleted sentence is what TASK_016_REVIEW's honesty verdict
  rested on. Restore it as an explicit **"this is what the declaration used to
  say, and this is when and why it changed"** note.
- **Accept the cost out loud.** Under one standard, **p16 and p17 both have zero
  measured admissible alternate spellings**, so "the shipped R3 is the cheapest
  admissible one" is **unestablished for both**. Say so in both `NOTES.md`, and
  correct p17's false "row 3 satisfies all four" claim and its §10 line.

If you think the *semantic* reading is right instead, say so with the argument
and build that — but then it must also go in all six, and both patterns' cheaper
spellings become admissible and must be reported as such.

## Two false mechanism sentences, both landed by tasks that were fixing one

1. **`harness/report.py:105-107` and `:13-16`** assert that printing the idiom
   into `results/tables/*.md` addresses the observed failure. It does not:
   `.temp/review014/NOTES.md` and `.temp/p05r3/NOTES.md` have **zero** hits for
   `results/tables`. What actually happened is in `.memory/01-ladder.md:15-22` —
   two consecutive tasks quoted **`.memory/01-ladder.md`'s own permissive R3
   rung list** as licence. Keep the feature (it is cheap and it is good); fix the
   claim about what it fixes.
2. **`harness/check.py:868`** still says the marginal `Ir` "cancels the loader
   and environment terms exactly", refuted by TASK_017's own p08 measurement:
   0.18 Ir/call of spread, non-periodic and non-monotone, 100% of it inside one
   `memmove`. Correct it.

You may edit `harness/report.py` and `harness/check.py` for these two sentences
**and nothing else**.

## Done when

All six `idiom` blocks state the same standard and say when and why it was
adopted; p16's disclosure is restored; p17's false claims are corrected; both
`NOTES.md` say "cheapest admissible is unestablished"; the two mechanism
sentences are true; all six gates green; `md5_fn` unchanged 28/28. **p08's
`marginal_ir_per_call` will drift by up to ~0.18 Ir/call and that is expected**
(`.memory/03-measurement.md`) — report it, do not chase it.

Prose first, gates last: `source_sha256` globs `patterns/*.md`.

## Constraints

No root; no `/tmp` (scratch `.temp/p18/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/` (report durable facts; I land them). No cell source
may change — if you believe one must, stop and report. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing.

Notes to `.temp/p18/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-one
agents have contradicted my written instructions and all twenty-one were right.
The thing I am least sure of is **whether a declaration that pins tokens is
worth having at all**, as opposed to pinning nothing and reporting the spread
honestly. A token pin makes `R3 − R4` attributable, but it also means the
project reports a number for *one spelling the author chose*, and finding 14
says that is exactly what cannot be generalised. I have chosen attributability
over generality; argue me out of it if the measurements support that.
