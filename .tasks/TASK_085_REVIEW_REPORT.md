# TASK_085_REVIEW — report

**Role: research reviewer.** Reviewed `.tasks/TASK_085_REPORT.md` (the `p15`
contract probe) against `.tasks/TASK_085_REVIEW.md`'s attacks A1–A5. All scratch
in `.temp/r85/`; nothing written outside it. **The gate was NOT run**, per the
concurrency constraint — every `check.py` claim is read from `git show HEAD:`.

**Verdict: REFUSE `p15` — but not for the reason RECAP gave.**
**PROTOCOL rule 2 running count: 237 → 239.**

⚠ **Both of the manager's named least-sure calls were refuted with
measurements — A1 and A4. The asking worked.**

---

## A1 — DOES NOT LAND. The manager's named highest-value attack was wrong.

The hypothesis was that the pricing table used `kernel_exclusive_ir`, hiding
libstd's `run_utf8_validation` in a callee — p36's B2 defect.

**It did not.** `price.py` parses valgrind's **`I refs:`** line — whole-program,
which is what `.memory/03-measurement.md` prescribes for a kernel that calls
out. Six cells re-measured on an independently rebuilt binary reproduce
**bit-identically** (46921.00 / 81960.00 / 73756.00 / 87661.00 / 45081.00 /
39337.00). Decomposing the *same delta* per function settles it directly:

```
r3_std pct=0    k_r3_std self 45072  + core::str::converts::from_utf8  1815
r3_std pct=100  k_r3_std self 39328  + core::str::converts::from_utf8 42600
a_verified 0    k_a_verified self 73736   (no callee)
ctl_assume 0    k_ctl_assume self 45062   (no callee)
```

**libstd's validation is inside the published number, and at pct=100 it is the
larger half.** GOT-indirect calls resolved by relocation: `k_r3_std →
core::str::converts::from_utf8`, `k_b_structural →
core::panicking::panic_bounds_check`.

- **A1.3** (*"1840 is the cost of making a call with the work uncounted"*) —
  refuted: **1815 of it is `from_utf8`'s own self cost**, ~10 is call setup.
  That is 7.09 `Ir` per 16-byte SWAR block, against `.memory/03-measurement.md`'s
  glibc-`memcpy` datum of 0.104 `Ir`/byte.
- **A1.4** (*"`ctl_assume` is an unfair control"*) — refuted: `k_r3_std` and
  `k_ctl_assume` self-costs differ by **10 instructions at both ends of the
  axis**.

## A2 — DOES NOT LAND, and the vacuity control is now measured rather than asserted

- The differential oracle is `core::str::from_utf8(v).is_ok()`, **unmediated** —
  not self-confirming.
- The **pinned** `vstd/utf8.rs` rejects **overlongs** (`:206`), **surrogates**
  (`:214`) and **> U+10FFFF** (the `len == 4 ⇒ ≤ 0x10ffff` clause).
- An **independent** battery — lead-4 sweep hitting `F4 90 80 80`, lead-3 sweep,
  all-`(a,b)`+`8080`, the Kuhn capability vectors, 200 k long random strings,
  every prefix of a 10 kB valid string — **316 602 cases, 0 mismatches**.
- *"5 verified"* decoded **empirically** (`count_probe.rs`): a plain fn +1, a
  `while` loop +1, an `assert by (bit_vector)` +1. So v01's 5 =
  `first_scalar_len` + its bit-vector query + `is_valid_utf8` + its loop +
  `main`; v03's 8 adds `kernel` + `drive` + `drive`'s loop. Both re-ran 5/0 and
  8/0.

⚠⚠ **VACUITY CONTROL, MEASURED:** `ensures res ==> valid_utf8(b@)` with body
**`false`** verifies **`2 verified, 0 errors`**. **The `==` bar is
load-bearing**, and a one-directional bar would have certified a validator that
rejects everything.

---

## blocker 1 — *"TCB contribution zero"* is an artefact of the counter, and `_scan_unsafe_sites` is the only thing stopping the gate printing a FALSE sentence about p15

`check.py::_axiom_items` scans the pattern's own sources with
`vparse.axiom_decls`, which matches **declarations**. **It cannot see a USE of a
vstd `assume_specification`.**

p15's R5 in the probe's shape has zero `external_body` items and zero axiom
declarations, so `_trusted_items` = 0 and `_axiom_items` = 0. With identity
`exact` and `miri.required` unset, `check_miri`'s `if not why_required` branch
fires and **prints**:

> *"this pattern has NO trusted item and NO hand-written axiom, so there is no
> trusted `ensures` whose incompleteness Miri would have to backstop — Miri not
> required."*

**That sentence is false.** The executed call is licensed by
`~/tools/verus/vstd/string.rs:135-139`:

```rust
assume_specification[ str::from_utf8_unchecked ](v: &[u8]) -> (res: &str)
    requires valid_utf8(v@),
    ensures  res.spec_bytes() =~= v@,
```

— **verbatim the `ensures` a wrapper would write, and verbatim `_axiom_items`'
own definition of an axiom.**

⚠⚠ **So the probe's argument (b) is BACKWARDS.** It said *"complying would
require a hand-written `ensures` about `&str` semantics"*. **Not complying rests
on the same hand-written `ensures`, in vstd, uncounted.**

**Failure scenario:** a later task softens `_scan_unsafe_sites` and builds p15;
the gate certifies a pattern with `axioms 0`, `TCB 0` and *Miri not required*,
over a proof whose executed unchecked call rests entirely on a vstd axiom.
**That is RECAP "Owed" 0's hole, on the one row that walks through it.**

Confirmed the axioms column is `TASK_084`'s **live** work:
`git show HEAD:synthesis/synthesize.py | grep -c axiom` → **0**; working tree →
**17**, and its text says *"the trusted base of a row is `TCB items` +
`axioms`"* and that today's 0 *"is a result, not spare real estate"*.

## blocker 2 — the manager's A4 claim is REFUTED by a named counter-example: p27

The claim: *"in all 22 patterns the unsafe operation is TRUSTED, not PROVED; p15
would be the first whose precondition is discharged from a verified
postcondition."*

`patterns/p27-handle-table/verus.rs:516` — `rec_free` is
`#[verifier::external_body]` wrapping `unsafe { std::alloc::dealloc(p, layout) }`
with a **six-clause `requires`** (`:524-530`). Its call site is `rec_close`
(`:596-610`), a **verified** fn, which discharges it from tracked permissions
whose facts come from the **verified** `rec_open`'s `ensures` (`:571-580`). **So
the shape already exists in the tree.**

Weaker instances: **p36**'s `tab_get_unchecked` (`requires i < NOPS`, discharged
purely from the exec guard the C rung omits — in-source comment
`// THE SAFETY LINE`), **p03**'s `stack_set_unchecked`, **p09** (the obligation
that fires is verified `load_u64`'s).

⚠ **The census is right and the conclusion drawn from it is not.** 47 tokens,
all inside `external_body`, and **all 45 unsafe-bearing wrappers carry a
non-empty `requires`** (structurally enforced by `_check_trusted_unsafe`). **What
is trusted is the IMPLICATION; the ANTECEDENT is already Verus-discharged at
~130 call sites.**

⚠ **And a live precedent the probe's Q2 finding does not mention:**
`patterns/p27-handle-table/NOTES.md:686-705` records a **built, verified,
measured vstd-pure control** (`r5_vstdpure.rs`, `15 verified, 0 errors`) with
**two fewer trusted items**, **rejected because R4-vs-R5 measured `differ`.**
The project has already chosen identity over a smaller TCB once.

## major 3 — the published `15.58×` is a RESIDUAL ratio dressed as a RUNG ratio

`RECAP.md:13` and `:2365` carry *"a verified validator is dearer than
`core::str::from_utf8` at every alphabet — 15.58× on ASCII"*, **with no `Ir`
convention and no inline mode at the figure.**

`15.58 = A_val / R3_val`, and **both are differences against `ctl_assume`, which
is neither rung.** The **rung-level marginal `Ir`/call** is 73756 vs 46921 =
**1.57× on ASCII** and **1.07×** on all-non-ASCII.

**Failure scenario:** a later task quotes 15.58× as the R3→R4 penalty and
concludes verified validation is catastrophic, when the measured kernel penalty
is **+57%**.

## major 4 — the mutant attribution is wrong for m6, and the battery has a silent accept-on-compile-error path

The report groups m6 with *"→ `postcondition not satisfied`"*, carving out only
m7. Measured (`.temp/r85/m6_full.log`): m6 fails with **`decreases not satisfied
at end of loop`** + `precondition not satisfied`, and the word *"postcondition"*
appears **zero** times in the whole output. **m6 is a termination failure, not an
`ensures` failure** — weaker evidence than claimed.

Separately, `mutate.py:53` classifies a mutant as good whenever the verdict lacks
`"0 errors"` — and a **compile** error produces exactly that string, so a
non-semantic mutant would pass silently. None of the 13 run took that path, but
the hole is real.

## minor 5 — the axis is labelled two ways in one file, and the slopes are an OLS fit over a concave curve

`v06_price.rs:137` says *"fraction of NON-ASCII **bytes**"*; `:221` and
`price.py:4` say **scalars**. They are not the same — pct=10 (scalars) is ~21.9%
by bytes — and every published slope reads *"per point of non-ASCII%"*. The
slopes (+384.78 / +191.18 / +95.54, reproduced) are OLS over a strongly concave
curve: R3 runs **1210 Ir/pt** over 0→10 and **129 Ir/pt** over 75→100, and the
fit is off by **−7210 at pct=0, which is where the headline ratio lives.**

## minor 6 — `k_b_structural` is not call-free and keeps its bounds checks

Given as "129" beside `k_a_verified` "130 insns, zero calls"; it has one call, to
`core::panicking::panic_bounds_check`. Confounds A-vs-B further than the
loop-shape difference the report disclosed. (B is dead on verifiability, so no
result moves.)

## ⚠ minor 7 — ADJACENT AND REPORT-ONLY: the false vstd claim is ALIVE IN THE HARNESS

`git show HEAD:harness/check.py` ~`:4851`, inside the **5c-twin stage's own
docstring**: *"there is no vstd spec for `copy_from_slice`, so a bulk-copy twin
is not available"*. The pinned vstd ships
`assume_specification<T: Copy>[ <[T]>::copy_from_slice ]` at
`std_specs/slice.rs:205`. `patterns/p02-buffer-copy/NOTES.md:692` already
corrects it; **the gate's explanation of its own rule does not.**

⚠ **This is the exact claim `CLAUDE.md` says stood 44 tasks — a third site, and
the one an engineer reads while writing a twin.**

## minor 8 — a coverage gap in the probe's oracle, closed

`v02_difftest.rs`'s 26-symbol stage-3 alphabet omits `0x90`, so the tightest
max-scalar boundary `F4 90 80 80` is never tested there. **Closed by the
reviewer's own battery, 0 mismatches.**

## minor 9 — a surviving equivalent mutant

Dropping the surrogate test from the **width-4** branch still verifies `5
verified, 0 errors`, because a 4-byte encoding already has `cp ≥ 0x10000`. **The
priced validator carries one provably dead comparison.** Not exercised by the
pricing alphabet (2- and 3-byte only), so **no published number moves**.

---

## Clean negatives, by name

**CN1** A1's core hypothesis (kernel-exclusive convention hiding libstd) —
refuted from `price.py` *and* from the callee's `Ir` inside the delta.
**CN2** A1.3 — refuted, 1815 of the 1840 is `from_utf8`'s self cost.
**CN3** A1.4 (`ctl_assume` unfair) — refuted, 10 `Ir` apart at both ends.
**CN4** "the numbers don't reproduce" — 6/6 cells bit-identical.
**CN5** oracle self-confirming — refuted.
**CN6** `vstd::utf8::valid_utf8` a weak spec — refuted (overlongs, surrogates,
> U+10FFFF all rejected).
**CN7** validator disagrees with std somewhere — refuted on 316 602 fresh cases.
**CN8** *"5 verified"* counts the wrong five — decoded empirically; it counts
exactly the right five.
**CN9** a mutant failed to compile rather than semantically — 0 of 13.
**CN10** constant folding — refuted; marginal scales with both `pct` and `n`.
**CN11** result not consumed — printed.
**CN12** *"R3 keeps a call boundary A doesn't, so `isolated` is unfair"* — real,
~10 `Ir`, and **in A's favour**, so the headline direction is robust.
**CN13** row 2 — reproduced independently: `trunc` → exit 139, empty stdout;
`other` → exit 0, `len=4 fold=100507`.
**CN14** `grep -rn "get_unchecked" ~/tools/verus/vstd/` → **0 hits**, and
`from_utf8` → exactly one line, the unchecked one. Both verified.

## Unsure / not done

- **The gate was not run**, per §0. The split is right — `identity: differ`
  admissibility genuinely needs a run. ⚠ **One addition for `TASK_084`'s
  reviewer: when they run it, also exercise `check_miri`'s `if not why_required`
  branch, because blocker 1 lives there and a code read is not enough for a
  PRINTED sentence.**
- The *"fourteenth `index >= len`"* ordinal is bookkeeping not audited (p36 is
  recorded as twelfth, `06-catalogue.md:1092` as thirteenth; fourteenth is
  plausible).
- The compliant p15 shape (`external_body` wrapper + `twin_justifications`) was
  not run end-to-end — writing into `patterns/` is forbidden here. The claim that
  it lands at `PASS-WITH-BLOCKED-ROWS` is a code read of `rep.block`.
- ⚠ `_is_trusted`'s condition is `external_body` **and** (`ensures` or `unsafe`
  in body), **not `external_body` alone** as the probe's report states. Same
  conclusion for p15; recorded so nobody re-derives it.

## Verdict on `p15`

**REFUSE — and `_scan_unsafe_sites` is NOT backwards; it is load-bearing, and
p15 is the case that proves it.**

A1 did not land, so all three of the probe's legs stand, **and there is a fourth
which is the real one**: the shape that would make p15 worth building — zero
counted TCB, unsafe discharged by proof — is **precisely the shape whose trusted
base this gate cannot see**, and the shape the gate *does* admit makes p15 the
**23rd instance of a wrapper the tree already has 45 of**, with a blocked twin
row.

⚠ **Softening `_scan_unsafe_sites` is admissible only AFTER the axiom counter
learns to see USED vstd axioms** — i.e. after `TASK_084` lands and is extended.
**Doing it first is not "preferring a pattern over hardening the gate"; it is
un-hardening the gate on the one row that exploits the gap.**

Had A1 landed, legs 1 (row 2 is not a new harm class; row 1 is p18's) and 2
(shape B has no verifying R5) would still stand, and leg 3 would drop pending a
re-price. It did not: **the cost result is sound as measured and only mislabelled
at the headline.**
