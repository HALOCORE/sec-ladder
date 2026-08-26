# TASK_101 — build `p23`, in-place quicksort partition

**Role: research engineer.** Read `.tasks/PROTOCOL.md`, then this file, then
`patterns/p01-array-sum/` **in full** (it is the template every pattern clones —
`spec.md` carries the kernel contract *and* the machine-readable pins the gate
enforces; `model.py` is the independent reference the gate drives; **both are
mandatory**), then `.tasks/TASK_086_REPORT.md` **§3 (`p23`) and its "Unsure / not
done" list**, then `.memory/06-catalogue.md`'s **THE THREE PROBES + probe 4**.

Scratch in **`.temp/t101/`**. Pattern dir is **`patterns/p23-partition/`**.

**This is the 25th pattern.** The catalogue was declared closed at 24 with `p23`
named as the one live build candidate; you are building it.

---

## §0 — settle the bug class and the novelty claim FIRST. This is deliverable 1.

⚠ **Both are stated here as QUESTIONS TO BE MEASURED, not as facts.** The
project has shipped a false novelty claim into eight places including two hashed
contract blocks, and RECAP's rule 4 exists because **both manager-proposed axes
died on a novelty claim one `grep` would have settled.**

**The novelty claim to settle:** *`p23`'s R5 obligation is a **multiset /
permutation** property, and no built pattern has one — every other proof
obligation in the tree is a bound or an exact positional postcondition.*

✅ **The manager ran the first pass so you do not repeat it, and it did NOT come
out clean the first time.** `grep -l 'multiset\|permut' patterns/*/verus.rs`
returns **`p14`**, and `grep -l 'sorted' patterns/*/verus.rs` returns **`p07`** —
so the claim looks dead on its face. On inspection both are false alarms:

- **`p07`'s hits are all comments saying the spec does NOT assume sortedness**
  (`"Nothing here says the elements are sorted"`). No order obligation.
- **`p14`'s single hit is a comment** at `patterns/p14-field-split/verus.rs:179`
  that says *"p06's is invariance under permutation"* — ⚠ **and that phrase is
  about why a CHECKSUM FOLD must be order-sensitive, not about a proof
  obligation.**
- **`p06`'s actual `ensures` is positional** — `rot_left(s, m, r)`, an exact
  sequence equality, not a permutation property.

⚠⚠ **Do not take that as settled — it is a manager grep over one file per
pattern, and `verus.rs` is not the only place an obligation can live.** Check
`spec.md`'s pinned `ensures` for all 24, not just `verus.rs`. **If you find a
multiset obligation anywhere, the claim dies and you say so** — that outcome is
worth more than the row.

**The bug class to settle:** the catalogue guesses *"aliasing, permutation
invariant"*; `TASK_086` measured the bug as **the unsentinelled scan running off
the range = `index >= len`, sharing with `p07`.** ⚠ **The catalogue's guess has
been OVERTURNED on four patterns and UPHELD on two** — settle it with
alternatives rejected by measurement, the way `p10` §0 rejected five and `p18` §0
rejected four. **Say how many `index >= len` patterns that makes; `TASK_086`
memory-update 6 says the count was `twelve BUILT, not fourteen` and two patterns
have shipped since.**

---

## §1 — what is already measured, and how far you may trust it

From `TASK_086` (⚠ **nothing below has been through `check.py`; every number is
from throwaway kernels, and the R3 spellings were not searched**):

- ✅ **R5 PROBE RUNS: `4 verified, 0 errors`, FIRST ATTEMPT** —
  **`.temp/t86/v23_partition.rs`, which still exists.** Two moving indices,
  `decreases j - i`, invariant = multiset preserved + `∀k<i: v[k] ≤ pivot` +
  `∀k≥j: v[k] ≥ pivot`, postcondition = multiset preserved + both sides
  partitioned. **Only `external_body` is `print_u64`. No `assume`, no `admit`.**
- **Two gotchas that cost two runs, so do not rediscover them:**
  `broadcast use group_to_multiset_ensures` needs an explicit
  `use vstd::seq_lib::group_to_multiset_ensures;`, and postconditions need
  `final(v)@`.
- **Probe 3:** `63247.00` vs `57756.00` → `+5491` = **`+1.34 Ir`/element** at
  `n=4096`. ⚠ **This includes a common clone**, so it is not a kernel-exclusive
  figure — **do not publish it as one.**
- **Probe 4:** `ptr::swap` 0 hits, `::get_unchecked` 0 hits. ⚠ `core::mem::swap`
  **is** spec'd (`std_specs/core.rs`) but it is **safe**, so it leaves no
  `unsafe` token. **That means R4 needs a real lever found, not assumed** — see
  §3.
- ⚠ **Probe 2's numbers here are from the KNOWN-BROKEN form.** `TASK_086` #238
  found object-file md5 **false-positives on relocations**, and probe 2 is now
  known broken in **both** directions (linked md5 **false-negatives** on any
  kernel with a branch or a global). **The only form that works is normalised
  disassembly text.** Re-run it that way or drop it.

---

## §2 — ⚠⚠ THE KILL RISK, AND IT IS A REAL TENSION, NOT A CAVEAT

`TASK_086` names it: **"`p23`'s verified spelling is not the spelling its cost
kernels implement."** The verified probe is the **single-loop two-index** form.
The cost kernels implement the **nested-scan Hoare** form, whose inner loops need
their own invariants and termination measures. **That spelling was never run.**

⚠⚠ **AND THE MANAGER BELIEVES THE TENSION IS SHARPER THAN `TASK_086` STATED,
WHICH IS EXACTLY THE CALL I WANT MEASURED RATHER THAN BELIEVED:**

> **The bug may live in the form that does NOT verify easily.** The
> unsentinelled-scan `index >= len` bug in §0 is a **Hoare-form** bug — it is the
> inner `while v[j] > pivot { j -= 1 }` running off the end when no sentinel
> stops it. A Lomuto-style single-loop two-index partition **may not host that
> bug at all**; its natural bug is a different one (the `i`/`j` bound), which may
> already be `p05`'s or `p04`'s shape.

**So there are three outcomes and you must say which one you got:**

1. **The Hoare form verifies too.** Ship it; the tension was imaginary. **Best
   outcome — and the probe's own success at `4 verified, 0 errors` first attempt
   makes it more likely than `TASK_086`'s "kill risk" framing suggests.**
2. **The Hoare form does not verify in budget, and the two-index form hosts a
   bug that is genuinely `p23`'s.** Ship the two-index form and **declare the
   substitution loudly in `spec.md`**, with what was given up.
3. **The Hoare form does not verify AND the two-index form's bug is another
   pattern's shape.** ⚠ **Then `p23` is a REFUSAL, and that is a fine outcome** —
   fifteen rows have been refused and every refusal was the right call. **Do not
   invent a spelling to keep the row alive.** ⚠ **But write the refusal's REASON
   to the standard of a finding:** `TASK_093`'s refusal reason was rejected by
   its own review, and RECAP's rule is *"a refusal's reason is what gets reused
   on the next row."*

**Decide this EARLY.** Do not build five rungs and then discover the R5 spelling
does not host the bug.

---

## §3 — search BOTH sides, and count the levers on each

⚠⚠ **This is the trap that has now caught FIVE patterns** — p10, p27, p38, p22
(at **510×**) and p36 in mirror image. **A difference is only as honest as its
weaker-searched endpoint.**

- **R4's problem is specific and named by probe 4:** `mem::swap` is **safe**, so
  the obvious unsafe lever leaves no `unsafe` token and buys nothing. ⚠ **If R4
  has no real lever, then `R3 − R4` is measuring nothing and you should say so
  rather than publish a difference.** `get_unchecked` on the two indexed reads
  is the candidate; **measure it, do not assume it.**
- **R3 has more levers than R4 here** (iterator forms, `split_at_mut`,
  `swap` via indices vs slices, bounds-check elision by binding the length).
  ⚠ **p36 published `+15.00 flat` and the first in-contract R3 respelling made
  it `+7`, then `+2`.** **Count the levers on each side and state whether they
  are comparable.**
- ⚠ **`-C debug-assertions=on` also enables `assert_unsafe_precondition!` inside
  `get_unchecked`**, and what holds on 3 of 3 patterns is: **at `-O3` with
  debug-assertions on, R4 becomes dearer than R3.** Name the setting at every
  figure.

---

## §4 — rules that govern the numbers

- ⚠ **Name the INLINE MODE at every figure.** p10 fitted both and the regressors
  swapped.
- ⚠ **Never publish a "minimum"** — write *"cheapest found"* and **name the
  input**. ⚠ **Do not publish a pair interval.**
- ⚠ **Extract kernel bytes from the LINKED binary** — a relocated field is zero
  in a `.o`.
- ⚠ **A law owes its DOMAIN, and check the RESIDUE CLASS of every parameter your
  bands hold constant.** p38's additivity failure was 100% attributable to three
  missing columns, none of them the one named. ⚠ **For a partition the obvious
  hidden parameter is the PIVOT'S RANK** — a partition's work depends on how the
  data splits, not only on `n`. **If your bands hold the pivot at the median,
  say so, and sweep at least one band that does not.**
- ⚠ **Ship a sweep band** so every law is re-derivable from committed inputs and
  a hashed generator — **then actually re-fit from it before publishing.** p19
  shipped a band and published a law it had never re-fitted against.
- ⚠ **The R4/R5 pair is not a null control** — the offset is a source-path-length
  artefact, so the pair is a **biased draw of size one**. p06's own floor is
  **±4.6%**.

---

## §5 — Constraints

- **`.temp/t101/` only. No `/tmp`.** Keep the generator, delete the artefact.
  **Notes in `.temp/t101/NOTES.md` as you go.**
- **No `git add` / `git commit`.** Read-only git is fine.
- **`.memory/` and `RECAP.md` are manager-only.** Durable facts go in your report.
- ⚠⚠ **Do not touch `harness/build.py` or `harness/asm.py`** — measurement-hashed.
  ⚠ **And every rung `.rs`, `c/kernel.{c,h}`, `model.py` and `inputs/gen.py` are
  measurement-hashed too** (`measure.py::measurement_sources` globs them).
  ⚠ **A COMMENT-ONLY edit to `c/kernel.c` after measuring stales the record.
  There is no comment-only escape. Get the C comments right before you measure.**
- Do not edit `pilot/`. Do not bump the Verus/vstd pin. Verus via
  `./verus_run.py` only (single-file mode; never `--cargo`).
- ⚠ **Cite `check.py` by FUNCTION NAME, never a line number.**
- ⚠ **`env -u LD_PRELOAD` for any hand-run sanitizer**, and **`grep` the log,
  never `head` it.** **Every harm probe needs a positive control that must
  fire** — five controls in this project could not have failed.
- `timeout <N> <cmd>`; never `pkill`/`killall`.
- **Finish every edit BEFORE the final gate sweep**, then run `harness/check.py
  p23` and report the verdict.

Write your report to `.tasks/TASK_101_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is `MANAGER-FILLS-AT-LAUNCH`.** The calls I
am least sure of, by name:

1. ⚠⚠ **§2 — that the bug lives in the Hoare form and the verified form may not
   host it.** **This is my reasoning, not a measurement, and `TASK_086`'s probe
   succeeding first try is evidence against me.** If the two-index form hosts a
   perfectly good `index >= len` bug, **say so plainly and I am wrong.**
2. **§0 — that no built pattern has a multiset obligation.** I grepped one file
   per pattern and two hits came back that I then talked myself out of. ⚠ **If
   the pinned `ensures` in some `spec.md` carries one, my dismissal of `p14` and
   `p06` was motivated reasoning and I want to know.**
3. **That `p23` is worth building at all** rather than going straight to the
   synthesis. It is the 25th pattern and the marginal value of pattern 25 is
   lower than pattern 5. ⚠ **If §0 or §2 says the row is a duplicate of `p07`
   plus `p05`, REFUSE IT** — that answer is worth more than a green gate.

Carry that count forward, incremented by what you find.
