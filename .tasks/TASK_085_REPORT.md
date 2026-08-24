# TASK_085 — `p15` contract probe: report

**Role: research engineer (probe). Ran concurrently with `TASK_084`.**
All work under `.temp/t85/`; nothing written outside it. **UNREVIEWED** — this
file is the probe's own report. Per PROTOCOL rule 9 nothing here enters
`.memory/` until a review lands.

**Recommendation: (C) REFUSE `p15`** — and of a **third kind**, distinct from the
two the task file named. Not *"the proof stalled"* (it did not) and not *"the
justification was false a priori"* (the p48/p31/p45 shape). **All three of the
row's justifications were measured away in one session.**

**PROTOCOL rule 2 running count: 235 → 237.**

---

## The headline: the named kill-risk is dead, and it was never the problem

`TASK_083_REVIEW` selected `p15` with one named kill-risk — R5 needs a *verified*
UTF-8 validator, *"I did not build it and I do not know it closes."*

**It closes.**

```
$ ./verus_run.py .temp/t85/v01_validator.rs --multiple-errors 8
verification results:: 5 verified, 0 errors

$ grep -n 'assume\|admit\|external\|assume_specification' .temp/t85/v01_validator.rs
3:// BOTH directions. No assume/admit/external_body/assume_specification anywhere.   <- comment only
$ sha256sum .temp/t85/v01_validator.rs
593b25e0759c511377eb25546c509cacb7e61bc48143864c0e0c80b9a444fec5
```

`fn is_valid_utf8(b: &[u8]) -> (res: bool) ensures res == valid_utf8(b@)` — the
**`==`**, not the one-directional `==>` the task file warned would not be the
bar. ~120 lines, ~10 of them proof, **zero trusted items**. Two obstacles, both
trivial: `i + 2 <= n` overflows (write `n - i >= 2`), and one `by (bit_vector)`
for `codepoint_width_1(b) <= 0x7f`. The proof is three vstd lemmas —
`partial_valid_utf8_extend` (advance), `partial_valid_partial_invalid_utf8`
(reject), `partial_valid_utf8` as the loop invariant.

**End-to-end call site**, which is the thing the review said it did not know
closes:

```
$ ./verus_run.py .temp/t85/v03_callsite.rs --multiple-errors 8
verification results:: 8 verified, 0 errors
```

`kernel` calls `unsafe { str::from_utf8_unchecked(b) }` guarded by
`is_valid_utf8(b)`; vstd's `requires valid_utf8(v@)` is discharged **by the
validator's postcondition alone**. Plus a verified `drive(buf, n_iters)`, the
rule-2 driver shape.

**Non-vacuity, two independent ways.** Differential oracle against
`core::str::from_utf8` (`v02_difftest.rs`):

```
stage1 (<=2 bytes exhaustive):        n=65793     mismatches=0
stage2 (3 bytes exhaustive):          n=16777216  cumulative=0
stage3 (4 bytes, 26-symbol alphabet): n=456976    cumulative=0
stage4 (random, 3 alphabets):         n=1200000   cumulative=0
TOTAL cases=18499985 MISMATCHES=0
```

Mutation battery, 10 mutants, **all fail** (`mutate.py`, `mutate2.py`). m1 drop
overlong-w2 / m2 drop surrogate-w3 / m3 drop max-scalar-w4 / m4 widen lead4 / m5
drop continuation check / m6 never reject / m7 drop length check → `postcondition
not satisfied` (m7: `precondition not met: index in bounds`). ⚠ **m8 reject
0x41..0x7f / m9 reject all 4-byte / m10 over-tight w3 also fail** — these three
break the **completeness** direction, which a `res ==> valid_utf8` bar would
**not** have caught. `MUTANTS THAT STILL VERIFIED (should be empty): []`

---

## Q1 — the manager's claim UPHELD, and for a better reason than the rule reading

`requires valid_utf8(b@)` is not a style objection, it is a **hard gate
failure**. `harness/check.py::check_proof_domain` (stage *"5d. rules 1 and 3 on
EVERY measured input, adversarial included"*) `eval`s every derived `requires` at
**every** kernel call of **every** model, adversarial included, and calls
`rep.fail("proof-rule1", ...)` on the first violation.

**Clean negative on the counter-example hunt: 0 of 22 patterns violate.**
Independently re-derived by driving each `model.py` over each `adversarial-*.bin`;
agrees with `results/gate/*.json` `proof_domain.*.requires_ok`. **21 of 22
kernels carry exactly one `requires`** and it is the window fact
`off + len <= buf@.len()`; p17 alone has a second (`buf_len <= i64::MAX`, a
file-size fact). The mechanism: the input aimed at the *structural* precondition
is rejected by the **verified driver guard** before any call (the
`adversarial-strideN` family, 18 of 21 patterns), and the input aimed at the
kernel is a value the kernel is **total** on. p01 is the only pattern where all
adversarial inputs make zero kernel calls; p03/p04/p09 ship none.

---

## Q2 — ⚠⚠ MANAGER CONTRADICTED. `identity` is mandatory as a MEASUREMENT; the LEVEL is free, and the gate explicitly admits R4 ≠ R5

Read from `git show HEAD:harness/check.py` (`fc8a269`), because `TASK_084` owns
the live file. **Citing functions, not lines**, per
`.memory/02-bench-rules.md`'s *"Line citations into `check.py` decay."*

- **`check_identity`** (stage 3c): `pins = contract.get("identity") or []` and
  `if not pins: rep.note(...)` — **a note, not a fail**. Per-opt, `if want is
  None: rep.note(...)`. **Stage 3c alone requires no pin at all.**
- **`check_identity` enforces a FLOOR only**: `if got_i < want_i: rep.fail(...)`,
  and stronger-than-pinned is `rep.ok(... "(stronger than pinned)")`.
  `asm.IDENTITY_LEVELS = ["differ", "counts", "norel", "exact"]`, so **`differ`
  is a legal pin value** and a pattern pinning it passes 3c at any measured
  level.
- **`check_miri` is what makes an identity measurement mandatory, transitively**:
  `a, b = (cfg.get("pair") or ["unsafe","verus"])[:2]` … `o3 = [r for r in
  identity if r["pair"] == pair and r["opt"] == "O3"]; if not o3: rep.fail("miri",
  ...)`. `check_identity` records rows only for *pinned* pairs, so no pin naming
  the R4/R5 pair ⇒ hard failure at stage 8.
- ⚠⚠ **`check_miri` treats R4 ≠ R5 as SUPPORTED**: `inherits = idx >=
  IDENTITY_LEVELS.index("norel")`; when that is false it appends *"R4 and R5
  differ at O3 (identity {level!r}), so R4 does not inherit R5's discharged
  obligations at all"* to `why_required`. **That is a reason Miri is REQUIRED,
  not a failure.**

The 22-file census is exactly as the manager measured (all pin `unsafe vs
verus`; at O3, 21 `exact` + p36 `norel`). **So *"21 of 22 pin `exact`"* is true;
*"none allows R4 ≠ R5"* is **true of the `spec.md` files and false about the
gate**.

⚠ **Consequence: RECAP "Owed" 25's second bullet is wrong as written, and the
design space it closed is open.** p15 *could* ship an R4 that genuinely assumes,
with R5 a different program and Miri as the compensating control.

---

## ⚠⚠ THE OBSTACLE NOBODY NAMED: the gate forbids VERIFIED unsafe

`harness/check.py::_scan_unsafe_sites`: in a pinned Verus source, **every
`unsafe` token must sit inside the body of an item the gate treats as trusted**
(`_is_trusted`); anywhere else is `rep.fail("tcb-unsafe", ...)`, whose message
orders you to *"Put the unchecked operation inside an `#[verifier::external_body]`
item with a `requires`, an `ensures` and a `#[cfg(slb_twin)]` twin."* And
`_is_trusted` returns `False` unless `item.external == "verifier::external_body"`.

**p15's R5 needs `unsafe { str::from_utf8_unchecked(b) }` inside a VERIFIED
fn** — precondition discharged by Verus from the validator's postcondition, TCB
contribution **zero**. Measured tree-wide with HEAD's `vparse`: **47 `unsafe`
tokens across 22 `patterns/*/verus.rs`, all inside `external_body`, zero
outside.** The rule has never met a verified-unsafe call.

Complying would (a) move a **Verus-discharged** call into the counted TCB,
(b) require a hand-written `ensures` about `&str` semantics — the axiom class
`TASK_084` is closing as this ran — and (c) require a `#[cfg(slb_twin)]` twin
with an identical signature and no `unsafe`, which is **unwritable**:

```
$ grep -rn "from_utf8" ~/tools/verus/vstd/
/home/apt/tools/verus/vstd/string.rs:136:pub assume_specification[ str::from_utf8_unchecked ](v: &[u8]) -> (res: &str)
```

One hit, the unchecked one. Result: `verus.twin_justifications` → `rep.block` →
**`PASS-WITH-BLOCKED-ROWS` on the row that IS the pattern.**

✅ **Clean negative that keeps this honest:** `grep -rn "get_unchecked"
~/tools/verus/vstd/` → **0 hits**. The tree's 47 wrappers are therefore
unavoidable and **this rule has cost the project nothing so far**. p15 would be
the **first pattern whose unsafe operation vstd actually specs.**

---

## §3-B — manager's guess UPHELD, and it understates it: shape B has no verifying R5 at all

```
$ ./verus_run.py .temp/t85/v04_structural.rs --multiple-errors 8   # ensures res == valid_utf8(b@)
verification results:: 1 verified, 3 errors
  postcondition not satisfied (x3)  +  invariant not satisfied at end of loop body

$ ./verus_run.py .temp/t85/v05_structural_callsite.rs --multiple-errors 8
error: precondition not satisfied
  --> .temp/t85/v05_structural_callsite.rs:63:26
63 |         let s = unsafe { str::from_utf8_unchecked(b) };
  --> vstd/string.rs:138:8
verification results:: 4 verified, 1 errors
```

Not *"R5 would have to add the checks back"* — **R5 cannot make the unsafe call
at all.** B collapses into A or into nothing.

---

## §3-A pricing — the manager's prediction CONFIRMED, sign and mechanism

`v06_price.rs` is compiled **by Verus** (`4 verified, 0 errors`), so the A rung
is genuinely the verified code. `-O3`, **inline mode: isolated**
(`#[inline(never)]` on every `k_*`), `-C codegen-units=1`, marginal `Ir`/call by
`n_iters` 100↔200 differencing, 4096-byte buffer built at run time from `argv`.
**Axis: fraction of non-ASCII scalars — a slope, not a level**, declared in
advance.

Static check (`objdump -dC`): `k_a_verified` **130 insns, zero calls — the
verified validator fully inlines**; `k_r3_std` 64 insns **+ one GOT-indirect call
into libstd's `run_utf8_validation`**; `k_b_structural` 129; `k_ctl_assume` 63.

```
 pct  bytes chars   r3_std   a_verified  b_structural  ctl_assume
   0   4096  4096  46921.00    73756.00      81952.00    45081.00
  10   4096  3556  57768.00    76816.00      82852.00    43821.00
  25   4096  2986  65632.30    80056.30      83872.30    42531.30
  50   4095  2328  74370.00    83751.00      84877.00    40947.00
  75   4095  1927  79447.00    86030.00      85592.00    40038.00
 100   4095  1638  81960.00    87661.00      86027.00    39337.00
```

Validation isolated (kernel − `ctl_assume`, the fold-only control):

```
 pct   R3_val    A_val    B_val   A/R3   R3 Ir/byte  A Ir/byte
   0   1840.0  28675.0  36871.0  15.58       0.449      7.001
  10  13947.0  32995.0  39031.0   2.37       3.405      8.055
  25  23101.0  37525.0  41341.0   1.62       5.640      9.161
  50  33423.0  42804.0  43930.0   1.28       8.162     10.453
  75  39409.0  45992.0  45554.0   1.17       9.624     11.231
 100  42623.0  48324.0  46690.0   1.13      10.409     11.801
Slopes (Ir/call per point of non-ASCII%): R3 +384.78, A +191.18, B +95.54
A−R3: +26835 → +5701 Ir/call  (+6.552 → +1.392 Ir/byte)
```

**A is dearer than R3 at every point, largest on pure ASCII** — exactly the
word-at-a-time fast path the manager named. std validates ASCII at **0.449
Ir/byte**; the verified validator needs **7.00**. **15.58×**, collapsing to
**1.13×** on all-non-ASCII. TASK_083's `+4.1% ASCII` reproduces (46921 vs 45081
= +4.08%). **This is p11's result a fourth time: the safe class reaches a library
the unsafe class cannot.**

---

## §4 — ⚠⚠ TASK_083_REVIEW's ROW 2 DOES NOT REPRODUCE. Two of its four cells are wrong.

Published (TASK_083_REVIEW, and repeated in RECAP "Owed" 25): *"prints NOTHING,
exit 0"*, *"ASan-equivalent: n/a"*, *"bounds violation: none"*, *"the optimiser
deleted the program's own `println!`"*.

Measured, **including a byte-for-byte replica of the review's own
`.temp/r83/b/miri/ub2.rs`**:

```
--- the REVIEW's shape (bytes are compile-time literals) ---
  arg=trunc   exit=139  stdout=''
  arg=other   exit=0    stdout='len=4 fold=100507'
--- my shape (bytes parsed from argv at run time) ---
  arg=61,F0         exit=139  stdout=''
  arg=61,C3,28,62   exit=0    stdout='len=4 fold=100507'
```

`exit 139` is **SIGSEGV, not exit 0**. 30/30 runs across `-O`,
`-O -C codegen-units=1`, `-O3`, `-O3 -C debug-assertions=off`, `-O2`, `-O1`;
nightly 1.99 `-O` also gives 139. At `-O0` it aborts 134 with *"unsafe
precondition(s) violated: `hint::unreachable_unchecked` must never be reached"*.

```
$ .temp/t85/ub2_asan trunc          # nightly -Zsanitizer=address
==158000==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x7bab647e0032 ...
READ of size 1 at 0x7bab647e0032 thread T0
$ .temp/t85/ub2_asan other
len=4 fold=100507                                            # exit 0, clean
```

**ASan catches it, and there IS a bounds violation** — a one-past-the-end heap
read. Miri reproduces exactly as published (`UB: entering unreachable code`,
`validations.rs:48:23`), and row 1 reproduces exactly.

| input | `rustc -O` | Miri | ASan | bounds violation |
|---|---|---|---|---|
| `61 C3 28 62` | `len=4 fold=100507`, exit 0 | clean | clean | none |
| `61 F0` | prints nothing, **exit 139 (SIGSEGV)** | UB | **heap-buffer-overflow READ** | **yes** |

⚠ **So row 2 is NOT a new harm class.** It is the tree's **fourteenth
`index >= len`**, now on the Rust side. What survives is **row 1** — a silent
wrong answer Miri does not catch — **which is p18's harm, and p18's harm is what
killed p45.**

---

## Bonus vstd fact `TASK_083` missed

`~/tools/verus/vstd/string.rs:465` ships
`assume_specification[ str::chars ](s: &str) -> (iter: Chars<'_>) ensures
IteratorSpec::remaining(&iter) == s@`, plus `into_iter_elts` (`:462`) and
`impl IteratorSpecImpl for Chars` (`:473`). **A verified *decode* fold over the
`&str` is available at the pin**, not just validation. Sixth instance of
*"grep the pinned vstd before claiming no spec exists"*.

---

## Problems

- `partial_valid_utf8_extend` and `partial_valid_partial_invalid_utf8` are
  directly callable as proof fns; no `broadcast use` needed. `s.spec_bytes()`
  needs `use vstd::string::StringSliceAdditionalSpecFns;` — `vstd::prelude::*`
  does **not** bring the trait in. Cost two runs.
- The A-vs-B *cost* comparison is confounded: `k_b_structural` writes the
  continuation scan as an inner `while j < w`, `k_a_verified` dispatches on width
  in a helper. Same static size (129 vs 130), different loop shape. B is dead on
  verifiability anyway, so it was not chased.
- The `-Zsanitizer=address` build needs nightly 1.99, not the pinned 1.97.1. The
  project already accepts nightly for Miri, but the codegen is not the pinned
  one.

## Unsure / not done

- ⚠ **`harness/check.py` and `harness/measure.py` were NOT run**, per the task's
  concurrency constraint. **Every gate claim in Q2 and in the
  `_scan_unsafe_sites` section is a CODE READ of `git show HEAD:harness/check.py`,
  not an executed gate.** In particular **no pattern with `identity: differ` has
  been run through the gate**; the claim that `differ` is admissible follows from
  `IDENTITY_LEVELS` containing it and `got_i < want_i` being the only failure
  path. **It deserves one real run before it enters `.memory/`.**
- No p15 `spec.md`/`model.py` was built, and whether `valid_utf8` is expressible
  as a `model.py` Python predicate for stage 5d is untested (a recursive scan, so
  probably yes).
- The `tcb-unsafe` failure was **not** demonstrated end-to-end through `check.py`
  — that needs writing a `.rs` into a pattern directory, which the task forbids.
- No fair like-for-like B pricing; no `-O0`; **one inline mode only, `isolated`**.
- No verified `chars()` decode fold was attempted; only the spec's existence was
  established.

## Reproducibility

`.temp/t85/rebuild.sh` re-derives every binary. Sources, probes, `price.json`
and logs retained; binaries deleted, per `CLAUDE.md` "Don't" 1.

## Memory updates owed (manager applies, AFTER review — rule 9)

1. **A verified UTF-8 validator closes at the pin**, `ensures res ==
   valid_utf8(b@)` bidirectional, 5/0, zero trusted items → `.memory/04-verus.md`,
   with the three vstd lemmas and the `n - i >= 2` overflow idiom.
2. **`str::chars` IS spec'd in the pinned vstd** (`string.rs:465`) →
   `.memory/04-verus.md`.
3. **Q2 correction**: `identity` is mandatory as a *measurement* (via
   `check_miri`), the *level* is a free choice, `differ` is legal, and the gate
   admits R4 ≠ R5 with Miri as the compensating control →
   `.memory/02-bench-rules.md`. ⚠ **Needs one real gate run first.**
4. **`_scan_unsafe_sites` forbids verified unsafe.** Currently costless (vstd
   specs no `get_unchecked`); p15 would be the first casualty.
5. **TASK_083_REVIEW's row-2 harm is refuted**, and RECAP "Owed" 25 repeats it.
6. `s.spec_bytes()` needs `use vstd::string::StringSliceAdditionalSpecFns;` →
   `../LearnVeri/PITFALLS.md`.

**Count 235 → 237.** Two measured contradictions: Q2's *"identity is binding"*
(the manager's), and TASK_083_REVIEW's row-2 harm (one claim, two independently
wrong cells). **Clean negatives, all upheld:** Q1's rule reading (0/22
counter-examples), the §3-A prediction (confirmed with its stated mechanism), and
the §3-B guess (confirmed and understated).
