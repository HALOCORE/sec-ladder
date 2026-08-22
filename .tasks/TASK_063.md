# TASK_063 — p27 forbids a spelling both its own C rungs write

**Role:** research engineer (you built p27 and corrected it twice; this is the
last thing outstanding on it).
**Read first:** `.tasks/PROTOCOL.md`, then **`.memory/01-ladder.md`'s
named-spelling standard block at `:81`** (unnumbered — do not cite it by a
number; the manager did and got it wrong, see the warning above it), then
**`.memory/02-bench-rules.md`'s `forbidden_hits` residual**, which TASK_062
re-opened on the strength of this defect, then `patterns/p27-handle-table/spec.md`.

## The defect

`idiom.forbidden[0]` is `` `memset(tab` ``. **Both C rungs write it:**
`c/kernel.c:66-67` and `c/kernel_hardened.c:46-47` contain
`memset(tab, 0, sizeof tab);`. The gate has recorded this since p27 landed:

```
forbidden_hits: 2
  {"entry": "forbidden[0]", "lang": "c", "spelling": "memset(tab", "rung": "c/kernel.c"}
  {"entry": "forbidden[0]", "lang": "c", "spelling": "memset(tab", "rung": "c/kernel_hardened.c"}
```

`forbidden`'s scope is universal by the key's own meaning — `idiom_audit`'s
docstring calls it *"decidable: no rung may spell a forbidden token"* — so **both
C rungs are out of p27's own contract.** And `idiom.why` **never says what
`memset(tab` is forbidden FOR**, though it explains every other forbidden entry.
`NOTES.md:441` separately records, as a measured fact, that gcc and clang inline
*"the two `memset`s of the table and the liveness array"*.

**This is the only pattern in eighteen with a nonzero `forbidden_hits`, and it
survived three tasks and two adversarial reviews with the number printed in the
verdict the whole time.**

## §1 — settle which side is wrong, and say so before you edit anything

Exactly one of these is true, and **the deliverable is the decision with its
evidence, not a green gate**:

- **(a) The entry is right and the rungs violate it.** Then the rungs must stop
  spelling `memset(tab` — and you must say what they do instead and what it
  costs, because zeroing the table is not optional.
- **(b) The entry is wrong.** Most likely it was meant to forbid something
  narrower (a *bulk* clear standing in for the per-slot invalidation the pattern
  is about, say) and it caught the initialisation too. Then **removing or
  narrowing it is a DECLARATION EDIT** and owes the direction test in writing
  plus a `contract_sha256` disclosure with the byte-provable undo — the shape you
  used at TASK_061 and TASK_062.

⚠ **Do not resolve it by widening `why` to bless the hits.** Prose that
retro-justifies a violation is exactly the self-certification the direction test
exists to catch. If (b), narrow or delete the *entry*.

⚠ **And check the neighbours before you decide.** Does any other pattern forbid
a spelling that appears in a rung under a different name, i.e. is p27's `2 of
162` really the only one? The manager believes it is — **that is measured across
the current tree, not argued** — but you are closer to the audit than I am.

## §2 — the decision this defect re-opened, and I want your measurement, not your opinion

`.memory/02-bench-rules.md` declined making `forbidden_hits` fail (TASK_053 →
TASK_056), on the ground that the incident cited as its accident-test precedent
was **structurally invisible** to the check. **That premise no longer holds:**
this defect *is* visible to it — the hits are rung sources — and it shipped.

**But TASK_062 measured something that cuts the other way**, and you should weigh
it: the `2` has been **printed in the verdict, written into the gate JSON, and
transcribed into `NOTES.md`**, across three tasks and two reviews, and **nobody
acted on it.** *A number that is printed is not a check.*

> **So the question is fail-vs-print, not shout-vs-silent.** Give me the
> measurement that decides it: **with §1 resolved, what is `forbidden_hits`
> across all 18 patterns?** If it is 0 everywhere, a failing check has **zero**
> false-positive surface today and the cost is a few lines — say so. If any
> legitimate hit exists, a failing check needs an exemption mechanism, which is
> a much bigger change and probably not worth it. **Run it before recommending.**
> ⚠ **The manager decides; you measure and recommend.** And note TASK_062's
> engineer already won the equivalent argument against me with a ratio, so make
> the ratio argument if it favours doing nothing.

## Done when

§1's decision is written into `NOTES.md` with its evidence and, if (b), its
disclosure; `forbidden_hits` is whatever §1 makes it and **the number is
explained rather than merely reported**; §2's measurement is in the report;
`check.py p27` green; `measure.py --check-stale` clean. **Paste actual output.**
⚠ Editing p27's docs makes its gate record STALE — re-run the gate afterwards.

⚠ **If §1 is (b) and you touch `harness/check.py` for §2, that is a full 18-gate
sweep** (`.temp/t60-sweep.sh`, ~35 min). **Do not touch `check.py` unless the
manager's decision comes back to do so — report the recommendation and stop.**

## Constraints

No root; no `/tmp` (scratch `.temp/t63/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `common/`, or any pattern other than p27. **Do not
edit `harness/` on this task** — recommend, do not implement. `timeout <N> <cmd>`.
Never `pkill`/`killall`; **no `nohup … &`**. **You are the only agent running.**
clang `~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH; Verus only via `./verus_run.py`.

**If a prescription here is wrong, say so with the measurement.** The running
count is **117** — 115, plus TASK_062's engineer refusing my "keep it out of the
gate" ratio argument with five measurements, plus their catching that I cited the
named-spelling standard as *"finding 3"* when it is an **unnumbered block**. That
last one is my third numbering-collision error in a day and the warning in
`01-ladder.md` now carries the unnumbered-block case explicitly.
