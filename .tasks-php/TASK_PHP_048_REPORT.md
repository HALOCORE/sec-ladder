# TASK_PHP_048 — REPORT: ROW 9, `ph55-opdata-stride`, family T5

**Role:** research engineer, one agent. **Row:** `patterns-php/ph55-opdata-stride/`.
**Date:** 2026-09-14.

---

## 0. BRACKETS — first and last

| | at start | at end |
|---|---|---|
| `harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | **`66 record(s) examined, 0 STALE`** ✅ unmoved |
| `harness-php/gate.py --tool measure --check-stale` | **`18 record(s) examined, 0 STALE`** | **`20 record(s) examined, 0 STALE`** ✅ 18 + this row's 2 |

Both opening readings are exactly what `TASK_PHP_048` §3.12 predicted.

---

## 1. WHAT WAS BUILT, AND THE GATE VERDICT

`patterns-php/ph55-opdata-stride/` — **five rungs + R1h**, 28 cells, 7 inputs,
and **seven controls**, each carrying its must-fire negatives **inside it**
feeding `problems` (**63 selftest arms** in total; the gate's stage 9b reads
every one of the seven `problems` lists). None is in gitignored `.temp/`.

```
results-php/gate/ph55-opdata-stride.json
  verdict          PASS
  failures         0
  complete_run     True
  contract_sha256  c08504352b33964aa88766c0f46737a8a86bfc72702759636f4d8d94fab30d24
  source_sha256    42 path(s)
  verus            verus.rs  53 verified, 0 errors  (pinned 53)   10 TCB items
  identity         O0/differ expected differ, O3/differ expected differ
  miri             ran=True available=True runs=7
```

**Definition-of-done coverage** is item-by-item in §9.

---

## 2. ⭐⭐⭐ THE HEADLINE — the two adversarial inputs, priced separately

`controls/stride_bug.py`. The two blobs differ in **one byte** — the opcode
field of the trailing data word — and `inputs/gen.py` **asserts** that rather
than describing it (`diff == [16]`).

| rung | `adversarial-nullcall.bin` | `adversarial-opdatalive.bin` |
|---|---|---|
| **R1h and every shipped rung** | `15498615717350492160` | `15498615717350492160` |
| `c/kernel.c` (C, the bug) | ⛔ **SIGNAL 11** | `17484701542569762048` — **wrong, exit 0** |
| `safe_naive.rs` + the bug | ⛔ **PANIC** | `17484701542569762048` — **== C, bit for bit** |
| `safe_tuned.rs` + the bug | ⛔ **PANIC** | **== C** |
| `controls/fnptr_dispatch.rs` (`Option<fn>`) + the bug | ⛔ **PANIC** | **== C** |
| `unsafe.rs` (`unwrap_unchecked`) + the bug | **`11370550710093900800`** | **== C** |

### What safe Rust does, in each case — the explicit statement §4.2 asks for

* **`adversarial-nullcall.bin`** — C dies of a signal; a **safe** Rust port
  carrying the same bug **panics** on the `Option`. A real difference, and a
  **finding, not the row's purpose**.
* **`adversarial-opdatalive.bin`** — C answers `17484701542569762048` and a
  **safe** Rust port carrying the same bug answers **the same value**.
  ⛔ **The `Option` caught the NULL. It did not catch the wrong PC.**
  `model.py::sanitizer_expect` declares this input **`clean`** — and it is:
  there is no memory error, only a wrong answer. **ASan, UBSan and Miri all
  have nothing to say.**

### ⭐⭐ AND A THIRD BEHAVIOUR NOBODY PREDICTED

`unsafe.rs` **with the bug does not crash on the NULL case.**
`unwrap_unchecked` on a `None` is UB, LLVM took it, and the program ran to
completion printing `11370550710093900800` — a **third** value, agreeing with
neither C nor R1h. ▶ **On that input, unsafe Rust carrying the bug is strictly
worse than C: C at least segfaults.** That is the `unwrap_unchecked` lever's
real price, and it is why `miri.required` is `true`.

⚠ The Rust rows are **mutants, not rungs** — every shipped Rust rung implements
R1h and never mis-strides. Each mutant is the shipped `.rs` with
`4f68f3774c34`'s three lines deleted by exact-string substitution, **hit count
asserted**. (The assertion earned its keep twice: it refused a `fnptr_dispatch`
mutant that matched **both** exits, which would have measured a different bug.)

---

## 3. PREDICTIONS AND PREMISES — scored

| # | what was predicted | outcome |
|---|---|---|
| §2.6 | stage 5c-twin passes cleanly; `n_twins ≥ 1`, no hatch, no blocked row | ✅ **UPHELD**, by a wider margin than predicted |
| §2.8 (1) | R3 endpoint **degenerate**, R4 endpoint **moves** | ⛔ **REFUTED IN BOTH HALVES**, signs exactly swapped |
| §2.8 (2) | the upstream fix costs a measurable, non-zero amount | ⛔ **REFUTED** — free under clang, *profitable* under gcc |
| §2.7 (guess) | `inside_share` high on every cell; A1 resolves the row | ⛔ **REFUTED for the C cells** (74–83 %) |
| §2.4 | the catalogue's tier (`narrowed`) | ⛔ **REFUTED by measurement**; the row declares `modelled` |
| §2.3 | `git apply` fails | ✅ **CONFIRMED** (after my own control got it backwards — §5) |
| §2.3 | `NEXT_OPCODE();` occurs **115** times | ⚠ **117.** Off by two; the control counts it |
| — | *my own* `unsafe.rs` / `safe_naive.rs`: "R4 and R5 produce the same machine code" | ⛔ **REFUTED by this row's first gate run**, and repaired at re-measure price — §4e |
| — | *my own* prose: the `= NULL` is in "a 200-line block" | ⚠ counted: **168 lines, 130 assignments, one `= NULL`** |
| §2.1 | all nine mechanism facts | ✅ **all nine re-read and confirmed** on the pinned tarball |
| §2.2 | item 95: deliberate hand-off, not a second defect | ✅ **CONFIRMED** and closed |

### 3a. §2.6 — the twin prediction, **UPHELD**

`n_twins = 8`. Every twin is a safe body with the trusted item's signature
character for character; the twin configuration verifies at **61 / 0**;
`twin_justifications` is **empty**; **no hatch is taken and no row is blocked.**
▶ **F97's narrowing survives this row**: the joint unsatisfiability is a
property of the ITEM (`MaybeUninit`), not of php rows, and ph55 is the control
that shows it. The one non-index trusted item — `hunwrap: Option<u8> -> u8` —
twins to `t.unwrap()` in one line, exactly as predicted.

### 3b. §2.8 prediction 1 — **REFUTED IN BOTH HALVES**

`controls/spellings.py --verus`, seven variants, all in contract. A1, against
each side's shipped rung (the control's own build; see `NOTES.md` §11 for the
flags caveat):

* **The R3 endpoint is NOT degenerate.** `r3_nobind` is **`−1.82 %` / `−2.76 %`
  cheaper** than the shipped R3 — and what it reverts is `safe_tuned.rs`'s **own
  headline lever**, the `let o: Op = ops[pc];` bind the file calls *"the lever
  that is about the row"*. ⚠ **The lever is a pessimisation**: LLVM already
  proves `pc < MAX_OPS`, so the re-index costs no check, while binding a 16-byte
  `Op` by value costs a copy. *"Fewer bounds checks"* and *"cheaper"* came apart.
* **The R4 endpoint does NOT move.** All four R4 variants are **dearer**
  (`+0.35 %` … `+28.07 %`); no cheaper admissible R4 was found. **Reducing the
  trusted surface is never free on this row** — the opposite of `ph53`'s
  `r4_bitmask_min`.

⭐ **Two numbers worth carrying:** `r4_safe_slots` **halves the trusted surface
(8 → 4 accessors) for `+0.35 %` (a TIE) / `+0.84 %`**, admissible at 57/0; and
`r4_safe_hunwrap` **prices this row's own `unsafe`** — making *only* the handler
`unwrap` checked costs **`+2.20 %` / `+3.67 %`**.

⭐ **The decomposition is the useful half.** Of `safe_tuned.rs`'s three levers,
**lever 3 does all the work** (`+15.96 %` / `+18.39 %` to revert), **lever 2
does nothing** (a TIE in both families on both inputs), **lever 1 costs
1.8–2.8 %**. Reporting `R2 → R3` as one number would have hidden all three.

⛔ **Neither rung is re-shipped** — the fiat is what makes `R3ship − R4ship` a
bound. `NOTES.md` §13 item 16 carries the declared debt: `safe_tuned.rs`'s
comment is a framing this measurement undercut, and repairing it costs a full
re-measure for a paragraph.

### 3c. §2.8 prediction 2 — **REFUTED**, and the mechanism was wrong too

| statistic | input | `c-gcc` → `c-gcc-h` | `c-clang` → `c-clang-h` |
|---|---|---|---|
| **A1** | `small.bin` | `0.000 %` | `0.000 %` |
| **A1** | `large.bin` | `0.000 %` | `0.000 %` |
| **W1** | `small.bin` | **`−1.041 %`** ✅ resolvable | **`0.000 %` ± 7.00 Ir/call** ⛔ not resolvable |
| **W1** | `large.bin` | **`−1.290 %`** ✅ resolvable | **`0.000 %` ± 7.00 Ir/call** ⛔ not resolvable |

*(`O3/isolated`; W1 medians over `controls/argv_align.py`'s eight-length sweep.)*

▶ **Under gcc the fix is PROFITABLE. Under clang it is FREE and below the
alignment step, so no percentage may be quoted for it.** ⚠ The prediction's
mechanism was also wrong: the branch is not *"in a hot dispatch loop"* — it is
in the **error exit of one handler**, which the benign corpus reaches only
through the ONE-WORD form, where `increment_opline` is `0`.

⭐⭐⭐ **AND FAMILY B — the GATE'S OWN statistic — settles both halves.**
`marginal_ir_per_call` is a **slope**, so the one-shot loader term cancels by
construction; it was taken by the gate itself, in the gate's own environment,
by a different tool:

| pair | `O3/iso` small | `O3/iso` large | `O3/whole` small | `O3/whole` large |
|---|---|---|---|---|
| `c-gcc → c-gcc-h` | **`−20.07`** = `−1.061 %` | **`−66.14`** = `−1.300 %` | `−20.07` | `−66.14` |
| `c-clang → c-clang-h` | `+7.00` **or** `+0.00` | `+7.00` **or** `+0.00` | **`+0.00`** | **`+0.00`** |

* **The gcc figure is corroborated to three significant figures** (`−1.061 %` /
  `−1.300 %` against W1's `−1.041 %` / `−1.290 %`). The refutation does not rest
  on one statistic. ⭐ It is also **stable to the digit across every gate record
  this row produced**, which is what makes the contrast below mean something.
* ⛔⛔ **The clang figure is the artefact, shown FOUR ways:** `+7.00` is
  **exactly** the alignment step (140 058 Ir / 20 000 = 7.0029); it is
  **identical on two inputs whose work differs by 4×**, which a real per-call
  cost cannot be; the **same two binaries under `whole` give `+0.00`**; and
  ⭐⭐⭐ **the `isolated` cell itself moved from `+7.00` to `+0.00` under a
  re-run of byte-identical binaries** — `md5_fn` unchanged, every
  `kernel_exclusive_ir` unchanged, nothing different but the run.
  ▶ Family B on this row reports where two binaries' frames landed. ⚠ **A slope
  cancels a FIXED term; it does not cancel a PER-CALL one** — and that is
  `.memory-php/03-numbers.md`'s warning in its sharpest form, because here the
  two records were taken by the SAME tool in the SAME run.

⚠⚠ **THE FOURTH WAY IS A LATE CATCH AND I NEARLY SHIPPED THE POINT VALUE.**
`NOTES.md` §8c-2 printed `+7.00` flat, from one gate record, and it survived
five gate rounds. What caught it was `.temp/php48/verify_famB.py` — a throwaway
script whose only job is to re-read the published table out of the **live** gate
record instead of trusting the prose. ▶ The table now publishes the observed
**set**, §8c-2 carries the fourth argument, and the checker pins a set for clang
and **deliberately still pins a POINT for gcc**, because widening gcc to quiet
the script would have thrown away the contrast the section is built on. The
checker grew seven must-fire arms in the process — including one that refuses a
hypothetical *third* clang mode, since bimodality is the claim.

ⓘ `ph52` refuted the analogous prediction the same way (item 76: *profitable*,
`−0.342 %`). **`n = 2` toward a real law, from two different mechanisms.** It is
`n = 2`, not a law.

---

## 4. ⭐⭐⭐ SEVEN THINGS THE ROW FOUND THAT NOBODY ASKED FOR

### 4a. VERUS DOES NOT SUPPORT FUNCTION POINTER TYPES — and that is this row's mechanism

```
error: The verifier does not yet support the following Rust feature:
       function pointer types
```

`controls/fnptr.rs` is a **must-fire negative**, run by
`controls/negatives.py --verus` on every invocation. It is a **type-level**
refusal, not a proof failure: a `#[verifier::external_body]` wrapper does not
help, because any Verus-visible signature mentioning `[Option<fn(..)>; N]` is
refused, so the op_array itself would have to be opaque — and an opaque op_array
cannot carry `ok_from` or the value postcondition.

▶ **All four Rust rungs therefore store an `Option<u8>` handler ID and dispatch
with a `match`.** It is not a choice R4 could have made differently: `identity`
pins R4 == R5, so **a representation R5 cannot express is one R4 may not use
either.** ⭐ **It changes no answer** — `Option<fn>` and `Option<u8>` are `None`
for exactly the same opcode, measured on the adversarial pair (§2).

**The price**, `controls/fnptr_cost.py`, byte-identical checksums on all seven
inputs asserted first: `+14.40 %` / `+12.41 %` whole-program (W1) — in the
direction that **favours** the shipped rungs.

### 4b. ⛔ A1 IS STRUCTURALLY BLIND TO THIS ROW'S OWN DEFECT SITE

`c/kernel.c` and `c/kernel_hardened.c` compile to a **byte-identical `kernel`
symbol** under both compilers — `md5_fn 11d21e546a4f5cfd` (gcc, 460 insns) and
`55caf689768d03e5` (clang, 168 insns), `asm.py` level **`exact`** — and yet
**one of the two binaries SEGVs on `adversarial-nullcall.bin` and the other
answers.**

▶ **The defect is not in `kernel`. It is in `ph55_binary_assign_op_helper`**,
which is reached through the function-pointer table and therefore cannot be
inlined. A1 reports the upstream fix at **`0.000 %`** on every C cell.

⭐⭐ **And the lesson is about the rule, not about this row.** `inside_share` on
the C cells is **74–83 %** — *high* — and A1 is **still** blind, because what
matters is not how much of the cell A sees but whether **the DIFFERENCE** lands
inside it. `STATISTICS_001.md` §4 says exactly that; this row is a clean worked
instance. ▶ **Do not read a high `inside_share` as a certificate.**

### 4c. ⛔⛔ W1 ON THIS ROW MOVES WITH THE LENGTH OF `argv[1]`

`NOTES.md` §8b-2's table was first computed with a **relative** input path and
gave `c-clang → c-clang-h = −0.0007 Ir/call`. Recomputed with an **absolute**
path, the same two binaries gave **`−7.004 Ir/call` = `−0.398 %`**. Nothing was
rebuilt; `md5sum` on both is identical across the two runs. **A `−0.398 %` "the
fix is profitable under clang" was one paste away from being published.**

`controls/argv_align.py` sweeps eight `argv[1]` lengths over the same binaries
and the same input bytes, and reports **two** verdicts per pair — *magnitude
resolvable?* and *sign stable?* ⭐ The split is a correction the control forced:
`c-clang-h → safe_tuned` is `+216 k` or `+76 k` Ir depending on which side of
the step `c-clang-h` lands, **both positive**, so the magnitude is not quotable
and the sign is — and §8d's F108 headline needs only the sign. A single verdict
would have thrown away a real result to avoid quoting an unreal one.

**Mechanism** (inferred from the size and shape of the step, **not proven**): a
longer `argv[1]` shifts the stack pointer and with it the alignment of the
1 024-byte `[Op; 64]` and the 42-slot zval store this kernel zeroes on **every
call**; 7 Ir/call over 20 000 calls is 140 000 Ir, 0.4 % of the program.

⚠⚠ **AND IT BIT THIS ROW'S PROSE A SECOND TIME, AFTER THE CONTROL EXISTED.**
`NOTES.md` §8h published the gcc↔clang gap as `−7.42 %` / `−3.06 %` flat, from
one run. The last round re-measured the **same byte-identical binaries** and got
`−7.79 %` / `−3.20 %`. ▶ **§8h now publishes a RANGE** — `−7.79 … −7.42 %` and
`−3.20 … −3.06 %` — over the whole sweep, with `c-gcc`'s own level moving
`0.0033` Ir/call and `c-clang`'s **7.00**. ⭐ **The sign and the band survive;
the third digit does not exist**, and the control is what said so. ✅ The other
two W1 pairs were re-checked the same way and are stable:
`controls/fnptr_cost.py` reproduces `+14.40 %` / `+12.41 %` to `±0.004`
Ir/call, and **every A1 figure in `controls/spellings.py`'s nine-variant table
is byte-identical across two independent regenerations.**

### 4d. ⛔ `git apply --check` RETURNS 0 ON A GITIGNORED PATH

`controls/r1h_backport.py`'s first version used `git apply --check` in a scratch
dir under `.temp/`. **`git apply` silently SKIPS a patch whose target path is
gitignored in the enclosing repository and returns exit 0** — so `--check` said
`0`, the control printed **APPLIED**, and nothing had been applied. Reproduced
on every run by `gitignore_trap()`: `path_is_gitignored=True`, `--check`
**rc 0**, `bytes_moved=False`; the same patch in a standalone `git init` repo
gives `error: patch does not apply`.

▶ **`--check` is not the test. The bytes are.** ⚠ **Any control in this
programme that scratches under `.temp/` and trusts `git apply --check` is
unsound for the same reason.** No sweep of the other rows was done — `NOTES.md`
§13 item 20.

### 4e. ⛔⛔ AND TWO FALSE CLAIMS THE ROW SHIPPED, CAUGHT BY ITS OWN GATE, AND REPAIRED AT RE-MEASURE PRICE

`unsafe.rs` said *"R4 and R5 **must** produce the same machine code"* and
`safe_naive.rs` said *"`identity` **makes** R4 and R5 the same machine code"*.
**This row's own first gate run refuted both** (§11a): `identity` is `differ` at
both levels, 876 instructions against 872, `norel` differing too. The `identity`
pin in `spec.md` was corrected immediately; **the two rung comments were not,
because they are in the MEASUREMENT digest.**

⚠⚠ **A loose adjective can be declared and left. A false VERDICT in a hashed
source cannot** — `PROTOCOL_PHP.md` §F6a's at-risk class, and **F98's defect
exactly**, which is a sentence still sitting in `ph53/c/kernel_hardened.c`
because nobody paid for it. ▶ **So this row paid: both comments were repaired
and the row was fully re-built, re-measured, re-controlled and re-gated.**

⭐ **The repair costs nothing but time, and that was CHECKED rather than
assumed**: a comment-only edit produces byte-identical binaries, so the final
step of the round diffs the new measurement record against the old and asserts
that **every checksum, every `md5_fn` and every `kernel_exclusive_ir` is
identical**. ▶ **It did not.** `NCELLS 32 before, 32 after`, and
**`NOTHING MOVED — every checksum, md5_fn and kernel Ir is identical`**, across
both re-measures this row paid for (the comment repair, then the clean re-run of
§4f). ⭐ The same diff was run a third time over the `NOTES.md` §8c-2 repair,
which is prose-only and cost no re-measure at all — `NOTES.md` is in the **gate**
record's `source_sha256` and **not** in the measurement record's, which was
checked rather than assumed.

⚠ **What was NOT repaired, and is declared instead** (`NOTES.md` §13 item 21):
`c/kernel.c`'s *"200-line block"* is an **approximation** of a 168-line,
130-assignment function — loose, not false — and the counted figures now appear
in `spec.md`'s hashed block, `NOTES.md` and `README.md`. That one is worth a
declaration, not a second re-measure.

### 4f. ⛔⛔⛔ `pgrep … | head` HID A LIVE PROCESS, AND I RACED THIS ROW'S GATE AGAINST ITSELF

**This is mine, it is the worst process error in the task, and it nearly
shipped a false FAIL into this report.**

`final2.sh` was running in the background. I checked for live processes with
`pgrep -af 'final2.sh|check.py|gate.py' | head` — and **`head` cut the list.**
Every line it printed was a stale watcher loop belonging to *other sessions*
(`check.py ph45`, an hours-old `wordpress.py eco`); `sh .temp/php48/final2.sh`
was alive the whole time, ten lines further down, **and was never displayed.**
On that evidence I concluded the run had been killed at compaction and launched
`final3.sh` to resume it.

▶ **Two `check.py` runs then executed concurrently on the same row**, sharing
`.temp/php-root/`, sharing `.temp/clausemut/ph55/`, and truncating each other's
`gate8.log` and `gate9.log`. Both reported `check.py: FAIL`, and **the two
failures were different**:

| log | stage | message |
|---|---|---|
| `gate8` | `[req-mut]` | *"the UNMUTATED copy at `.temp/clausemut/ph55/…/verus.rs` does not verify (49 verified, 4 errors), so every mutant below would 'fail' for the wrong reason"* |
| `gate9` | `[clause-mut]` | *"`oset` `ensures[0]` is NOT load-bearing: deleting it still gives 53 verified, 0 errors"* |

⭐ **The first names the shared directory in its own message**, so it is a race
artefact beyond argument — and note what the gate did there: **it refused to
grade the mutants rather than report a result it could not stand behind.**
That stage caught my error, not me.

⚠⚠ **THE SECOND I DID NOT ASSUME AWAY EITHER — AND THEN THE NUMBERS PROVED IT.**
`gate5`, run alone, records at its stage 5c:

```
verus.rs: oset ensures[0] load-bearing (49 verified, 4 errors)
```

▶ So **`49 verified, 4 errors` is the MUTANT's reading** and `53 / 0` is the
baseline's. Now read the two raced messages again: `gate9` reports `53 / 0`
**as the mutant's** result, and `gate8` reports `49 / 4` **as the baseline's**.
⭐⭐ **The two processes swapped exactly those two readings between them** —
one wrote the mutated `verus.rs` into the shared tree while the other read it
as its own unmutated baseline. That is not a plausible interpretation of the
race; it is a *fingerprint* of it, and it rules out the failure being real.

Belt and braces anyway: the row was re-run from `build` with a **preflight that
is `pgrep` with no `head`**, refusing to start if anything on this row is alive
(`.temp/php48/final4.sh`, which also deletes `.temp/clausemut/ph55` first). The
verdict in §1 is that run's, alone.

**The lesson is not "be careful".** It is that `| head` on a liveness check is
a **silent** truncation of exactly the evidence the check exists to find, and
that the failure mode it produces — a second copy of an expensive job — is
invisible in the logs, because both copies write the same filenames.

### 4g. ⚠ A REPRODUCTION WITH THE WRONG FLAGS *REFUTED A TRUE CLAIM*

`c/kernel.c` and `NOTES.md` §8 publish a count: gcc's `-Wstringop-overflow`
fires **twice** without the `if (nops >= 2u)` guard and **zero** times with it,
which is the evidence that the guard is a stated precondition and not
defensive padding. That number had been measured once, so I wrote
`.temp/php48/wstringop_count.sh` to make it re-derivable.

**The first draft measured `0` on both arms** — i.e. it refuted the published
claim. The script was wrong, not the claim: it used `-std=c11`, two TUs and
**no `-flto`**, which is the `isolated` shape. The warning only exists when LTO
inlines the decoder into the driver loop and `nops >= 2` stops being derivable.
▶ Rebuilt with `harness/build.py::c_flags("O3", "whole")` verbatim
(`-std=c99 -Wall -Wextra -O3 -flto`) over `build_c`'s exact three sources,
`common/driver.c` included: **`without 2, with 0` — the published count,
exactly.** The trap is written into the script's header so the next reader does
not re-dig it, and the script carries two must-fire arms (it fails if
`k_orig.c` ever gains the guard, or if the shipped kernel ever loses it).

⚠ `k_orig.c` is the pre-guard snapshot and is **why that scratch file is kept**:
it is the only artefact on the box that can produce the "without" half.

---

## 5. R1h — hand backport, `git apply`, and the three legs

`controls/r1h_backport.py` runs it. The upstream patch is **REFUSED**:

```
error: while searching for:
			AI_USE_PTR(EX_T(opline->result.u.var).var);
		}
		FREE_OP_VAR_PTR(free_op1);
		NEXT_OPCODE();
error: patch failed: Zend/zend_execute.c:1942
```

— the `FREE_OP_VAR_PTR(free_op1);` that 5.0.0's `:1765-1770` does not have.
✅ **The task's premise is confirmed.**

⭐ **And the row ships the POSITIVE control that makes that verdict worth
anything**: `controls/4f68f3774c34-backport-5.0.0.patch`, the **same three `+`
lines, character for character**, with 5.0.0's own context. It applies cleanly
and moves the bytes at `:1765-1770`.

**The three legs, each re-measured on every run, and NOT the screen:**

1. the hunk's `@@` context names `zend_binary_assign_op_helper` ✅;
2. `increment_opline` occurs **exactly three times** in `Zend/zend_execute.c`
   (`:1728`, `:1749`, `:1792`) and **all three are inside `:1724-1796`** ✅;
3. the other exit **already carries the identical guard at 5.0.0** ✅, so a patch
   adding it there would be adding a duplicate.

⛔ `preimage_screen.py --id CRASH-023` returns **`CANDIDATE`** on the strength of
one `NEXT_OPCODE();` line, and `NEXT_OPCODE();` occurs **117** times in that
file. The screen has done its job — it is an EXCLUSION tool and it correctly
declines to exclude — and the row **does not quote it as confirmation**.

---

## 6. ITEM 95 — **CLOSED**

`NOTES.md` §3, and the `provenance.divergences` entry that pins it.
`INC_OPCODE()`'s own `if (!EG(exception))` guard is **not** a second instance of
the defect. `zend_throw_exception_internal` parks the PC at
`opcodes[last-1-1]` (`Zend/zend_exceptions.c:58`), and `last-1-1` is `last-2`
while `ZEND_HANDLE_EXCEPTION` is the last opcode —
`zend_do_end_function_declaration` emits `zend_do_return` then
`zend_do_handle_exception` (`Zend/zend_compile.c:1091-1092`; the emitter body at
`:1078-1085`). ▶ **The throw parks the PC one slot SHORT of the handler, in
anticipation of the `EX(opline)++` the handler's own trailing `NEXT_OPCODE()`
performs**, and `:53` reads the same invariant back. ✅ All re-verified on the
pinned tarball.

▶ The guard stops the stride being spent **twice**. It is a **correction**, not
an omission. **The row builds ONE faulting exit**, `PH55_EXCEPTION` is pinned to
`0`, and `NOTES.md` §3 records that it was considered and why it is out.

⭐ And it strengthens the row: the same function guards its stride correctly
against **two** hazards on one exit and against **neither** on the other, 23
lines earlier.

---

## 7. THE STATISTIC — `inside_share` per cell, both families published

`controls/statistic.py`. Measured **before** the column was chosen.

| cell | `small.bin` | `large.bin` |
|---|---|---|
| `c-gcc` | **81.75 %** | **73.97 %** |
| `c-gcc-h` | **82.61 %** | **74.94 %** |
| `c-clang` | **76.20 %** | **74.37 %** |
| `c-clang-h` | **76.20 %** | **74.37 %** |
| `safe_naive` | 96.66 % | 98.91 % |
| `safe_tuned` | 96.16 % | 98.71 % |
| `unsafe` | 95.88 % | 98.58 % |
| `verus` | 95.89 % | 98.58 % |

⛔ **The manager's §2.7 guess is refuted for the C cells.** `|Δinside_share|`
between the C and Rust columns is up to **25 pp** — an order of magnitude past
`STATISTICS_001.md`'s `≤ 0.02` condition.

⭐⭐ **And the cause is the row's own mechanism.** In C the handlers are reached
through a **function pointer**, so they cannot be inlined and each is its own
symbol: 17–26 % of a C cell's instructions are in callees `kernel_exclusive_ir`
never sees. In Rust the `match` arms are inlined into `kernel`.

▶ **So the row publishes its cross-language column in W1** and its same-language
Rust ratios in A1 (`|Δinside_share|` across the four Rust cells is 0.78 pp /
0.33 pp). **Both statistics are published, labelled**, in `NOTES.md` §8d and by
`controls/statistic.py`, which prints the A1 column beside the W1 one and marks
it `[A1 is the BLIND column here]`.

### 7a. Both C columns, and one cell CHANGES SIGN

`O3/isolated`, W1 Ir/call, against **R1h**:

| `small.bin` | vs `c-gcc-h` = 1880.374 | vs `c-clang-h` = 1752.194 … 1759.194 |
|---|---|---|
| `safe_naive` 2017.645 | `+7.30 %` | `+14.69 … +15.15 %` |
| `safe_tuned` 1763.005 | **`−6.24 %`** | **`+0.22 … +0.62 %`** |
| `unsafe` 1644.393 | `−12.55 %` | `−6.53 … −6.15 %` |
| `verus` 1645.520 | `−12.49 %` | `−6.46 … −6.09 %` |

⛔⛔ **`safe_tuned` on `small.bin` is 6.24 % FASTER than `c-gcc-h` and slower
than `c-clang-h` on every one of the eight sweep points.** F108's class, live.
**A row that had published only the gcc column would have published *"safe Rust
beats C"*.** The flip is **SIGN-STABLE** across the alignment sweep and
`controls/argv_align.py` fails if it stops being.

`large.bin` is in `NOTES.md` §8d. ⚠ **No `O0` figure is quoted as a performance
result anywhere in `NOTES.md`, `README.md` or this report.**

### 7b. `cbaseline_check.py --ratchet`

Run. It fired on three new hits, **all three in this row's `NOTES.md`, all three
FALSE**, and they are **adjudicated by hand in the checker's own table** with
the ratchet moved `63 → 66`. ⛔ **The regex was not widened.** Two are a **new
class the file did not have a name for — A SHARE IS NOT A CROSS-LANGUAGE
FIGURE** (`inside_share` is `A1/W1` *within* one cell, so it names no baseline
because there is none); the third is the **unit-size** class the file already
documents, in its sharpest form yet (§13 is a 15-item list with no blank lines,
so item 5's share marries item 1's R4-vs-R5 instruction counts).

⭐ **A reviewer should decide** whether `MAG` should exclude a unit whose only
magnitudes are shares — `inside_share` became a published per-cell quantity at
`TASK_PHP_043` and ph52/ph53 already publish one. I did not widen it: widening
the checker to make my own text pass is the anti-pattern it exists to resist.

---

## 8. THE TIER — the catalogue says `narrowed`; the build declares `modelled`

`provenance.py` reports **14 % (13/93)** over the union of six cited spans and
**16 % (7/45)** over the defect site alone, where `narrowed` leads a reader to
expect 25 %.

**What IS lifted one for one — the control flow, which is what the row
measures:** the flag and its single assignment; `op_data = opline + 1`; both
exits in upstream's order, 23 lines apart; both stride macros with upstream's
bodies including `NEXT_OPCODE()`'s trailing `return 0;`; `pass_two`'s handler
copy; the `= NULL` table entry; and a dispatch loop with nothing between the
`handler` field and the call.

**What is RE-EXPRESSED, which is what `modelled` names:** zvals become
`(kind, val)` pairs in a flat store and `zval **` becomes an index; the hash
container is gone; the opcode set is ten opcodes standing for the **130** `zend_opcode_handlers[...]` entries `zend_init_opcodes_handlers()` fills (counted, `:4276-4443`); and
the compiler's emitter guarantee is supplied by a run-time pass.

⚠ **A tier is a COST and never a filter, and a tier read as STRONGER than it is
is the dangerous direction.** ⓘ `patterns-php/CATALOGUE.md` still says
`narrowed` for `ph55`; I did not edit it — the catalogue is manager bookkeeping
and `ph53` set the precedent of leaving its own status column untouched. **It is
a discrepancy the manager owns.**

---

## 9. DEFINITION OF DONE — item by item

| § | requirement | status |
|---|---|---|
| 1 | five rungs + R1h, gated, verdict quoted **from the gate record, named** | ✅ §1 — `PASS`, 0 failures, from `results-php/gate/ph55-opdata-stride.json` |
| 2 | the two adversarial inputs priced separately, with what safe Rust does in each | ✅ §2 |
| 3 | `inside_share` per cell as a matrix, before the statistic is chosen; both statistics published, labelled | ✅ §7, `NOTES.md` §8a/§8d |
| 3a | every cross-language figure carries **both** C columns; `cbaseline_check --ratchet` run; no `O0` figure as a performance result | ✅ §7a, §7b |
| 4 | item 95 recorded CLOSED in `NOTES.md`, with the reasoning and the note that the exception path is out | ✅ §6, `NOTES.md` §3 |
| 5 | the two §2.8 predictions scored, either way | ✅ §3b, §3c — **both refuted** |
| 6 | the stage-5c-twin prediction reported | ✅ §3a — **upheld** |
| 7 | `NOTES.md` records the hand backport, that `git apply` fails, and the three legs — **not** the screen's `CANDIDATE` | ✅ §5, `NOTES.md` §5 |
| 8 | what I am unsure of, in its own section | ✅ `NOTES.md` §13 — **21 items** |
| 9 | brackets first and last | ✅ §0 |
| 10 | if a prediction survives, say so plainly | ✅ §3a says so |

---

## 10. THE ROW'S OWN FILES — what each is for

```
c/kernel.c            R1, and nine pinned facts in its header
c/kernel_hardened.c   R1h = kernel.c + THREE LINES. Diff them.
c/main.c              the driver; the three stride_w guards are STRUCTURAL and
                      the comment says why each is not a check in the executor
safe_naive.rs         R2   the mechanical port
safe_tuned.rs         R3   three levers (⚠ see §3b on lever 1)
unsafe.rs             R4   8 trusted items; ts deliberately still CHECKED
verus.rs              R5   ok_from + the value postcondition; NO rlimit attribute
model.py              three independent implementations + a synthetic sweep that
                      ALREADY CAUGHT A REAL DEFECT (an evaluation-order
                      disagreement in ADD, on a window no input file contains)
inputs/gen.py         the corpus + its arm-coverage assertions + the one-byte
                      assertion on the adversarial pair
spec.md               six pinned provenance spans; tier `modelled`
NOTES.md              13 sections; §13 is 21 uncertainties
README.md             the reader's entry point
controls/_pin.py      the staleness pin every sidecar carries
controls/argv_align.py      ⭐ §4c
controls/fnptr.rs           ⭐ §4a — MUST FAIL to verify
controls/fnptr_dispatch.rs  the Option<fn> variant
controls/fnptr_cost.py      what the Verus limitation costs
controls/negatives.py       four Verus mutants, all must FAIL. All do.
controls/r1h_backport.py    ⭐ §4d, §5
controls/spellings.py       the respelling search, §3b
controls/statistic.py       ⭐ §4b, §7
controls/stride_bug.py      ⭐ §2
controls/rlimit_bisect.sh   the proof-budget table
controls/4f68f3774c34.patch                 the upstream commit
controls/4f68f3774c34-backport-5.0.0.patch  the hand backport, and the positive
                                            control for §5
```

**Every control ships its must-fire negatives INSIDE it, feeding `problems`**
(§H): 9 + 10 + 7 + 7 + 9 + 12 + 9 = **63 selftest arms** across seven scripts,
and the gate's stage 9b reads every `problems` list. None is in gitignored
`.temp/`.

---

## 11. THE PROOF

```
requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_OPS
ensures   r == ph55_fold(buf@, off as int, len as int)
```

`ph55_fold` composes six recursive spec functions, so the postcondition is the
**value** over the whole machine state. `model.py::ph55_run` re-derives it from
a different decomposition.

⭐⭐⭐ **The obligation the row is about is `ok_from`** — *starting at `p` and
striding by each instruction's own width, every word the PC lands on is an
instruction word and never a data word, and every stride stays inside the
op_array.* It is the dispatch loop's invariant, it discharges `hunwrap`'s
`requires t.is_some()`, and **it is exactly the invariant the error exit
breaks.** ▶ **That is a better statement than `handler != NULL`**, and §2's
second column is the measurement that shows why.

⭐ It is established by the **emitter**, not the executor — `emit_from`, written
as **tail recursion** so its postcondition is `ok_from`'s own unfolding: two
`reveal_with_fuel` asserts and no lemma. A `while` loop needs an invariant
quantified over instruction starts plus a glue lemma. **The shape of the
property decided the shape of the code, in every Rust rung.**

⭐⭐ **NO `#[verifier::rlimit]`, AND THAT IS A MEASUREMENT.** `controls/rlimit_bisect.sh`:

| rlimit | plain | `--cfg slb_twin` |
|---|---|---|
| **1** | 53 / 0 | **60 verified / 1 ERROR** |
| **2** | 53 / 0 | **61 / 0** |
| 3, 4, 5, 10, 30 | 53 / 0 | 61 / 0 |

An interpreter, ten handlers, a value postcondition over the entire machine
state and **eight verified twins** need **2**, against Verus's default of 10.
⚠ Compare `ph16`, whose obligation is a single index bound with no loop in it
and which had to ship `#[verifier::rlimit(30)]` because its twin build **FAILED
at 8**. ⭐ **The reason is structural: every obligation here is ONE unfolding of
a recursive definition whose shape the exec code mirrors, so Z3 never searches.
A proof about a bigger program is not a more expensive proof; a proof whose spec
does not mirror its code is.**

### 11a. ⚠ The `identity` pin was declared `exact` and **refuted by the first gate run**

Measured: `unsafe` 876 instructions / `md5_fn 37f8a672831f6774`; `verus` 872 /
`30602b986da0f05b`; `norel` also differs. The exec code is character-identical
apart from the `verus!` block; what differs is **register allocation and
scheduling**, and R5 is the **shorter** of the two while costing `+0.071 %`.
⛔ **The cause is NOT identified** — three hypotheses, none distinguished
(`NOTES.md` §10d, §13 item 1). ⭐ **Consequence:** `.memory/02-bench-rules.md`
makes Miri **non-waivable** when R4 and R5 are not the same machine code, so
this row's `miri.required` is load-bearing twice over.

### 11b. The trusted surface, and the trade NOT taken

**Eight** `#[verifier::external_body]` items with contracts, plus `load_input`
and `emit` — more than any row in either programme. ⚠ **Six of the eight are
index accessors on FOUR arrays**, because this kernel keeps `zval.type` and
`zval.value.lval` in **parallel arrays**. A single `[Zv; 42]` would have taken
the surface from eight to six. **It was not taken**, and the reason is honest
rather than principled: the rungs were built, measured and verified when the
count was noticed. `NOTES.md` §10d-2 and §13 item 4.

---

## 12. ⚠ WHAT I AM UNSURE OF, AND WHERE I STOPPED

`NOTES.md` §13 carries **twenty-one** items. The five a reviewer should look at
first, **plus two this report adds that arrived too late for §13** (adding an
item to `NOTES.md` costs a gate round, and these are already stated here in
full — §3c and §4f):

1. **Why R4 and R5 differ at O3.** Three hypotheses, none eliminated. UNTESTED.
2. **The `argv_align` mechanism is INFERRED**, not proven: what is measured is
   that a cell's total takes exactly two values and which one depends on the
   path length. The `memset`-alignment explanation fits the size and shape of
   the step and was not independently confirmed.
3. **`inside_share` was measured at `O3/isolated` only.** Four of the eight
   `O3/whole` cells have no `kernel` symbol at all, so A1 is undefined there.
4. **The A1-blindness of §4b is demonstrated, not bounded.** How much of *other*
   rows' A1 figures sit in the same trap is not something this row can say.
5. ⭐ **The `git apply --check` / gitignore trap may affect other rows' controls.
   No sweep was done.**
6. ⚠⚠ **`marginal_ir_per_call` — the GATE'S OWN statistic — is bimodal on this
   row's clang cells, and I do not know how far that generalises.** Two gate
   records over byte-identical binaries disagree by the full `7.00` Ir/call
   alignment step (§3c). Every `ph*` row's family-B figures are differences of
   two cells from one record, so **any of them could carry the same artefact**,
   and the only reason this row noticed is that it happened to have a control
   measuring the step. ▶ **No sweep of other rows was done. This is the single
   most transferable thing here and it is UNTESTED elsewhere.**
7. ⚠ **Whether the clang mode is predictable at all.** `+7.00` and `+0.00` are
   both reproducible readings; I never found what selects between them **across
   gate runs** (the `argv[1]`-length mechanism of §4c explains the *existence*
   of two modes, not which one a given gate run lands in). Two modes is what was
   observed, not what was proven — `verify_famB.py` carries a must-fire arm that
   would refuse a third.

**Where I stopped:** nowhere short of the definition of done. Everything in §9
is complete. The searches are **bounded and say so**: seven respelling variants
(R4 searched is not R4 exhausted), eight argv lengths on `small.bin` and six on
`large.bin`, and two probe shapes. ⚠ **And the row cost three more gate rounds
than it should have** — one for the two false comments (§4e), one for the race
I caused (§4f), one for the family-B point value (§3c). All three were caught,
none by luck, but the first and third were caught *after* they had survived
several green gates, which is the honest characterisation of how much
confidence a `PASS` on this row buys.

---

## 13. FOR THE MANAGER — the small bookkeeping

* `patterns-php/CATALOGUE.md` still files `ph55` as **`narrowed`** and status
  **`catalogued`**. The build declares **`modelled`** (§8) and the row is built.
  ⓘ `ph53` has the same stale status, so the convention is already not being
  maintained; I did not edit the catalogue.
* `.tasks-php/cbaseline_check.py` — **I edited it**, to file three
  hand-adjudicated false positives and move `RATCHET 63 → 66`, exactly as §2.7
  instructs. **No regex was widened.** The new SHARE class is flagged for a
  reviewer's decision.
* **Nothing else outside `patterns-php/ph55-opdata-stride/` was written.** No
  `git add`, no `git commit`. `RECAP_PHP.md` and `.memory-php/` untouched.
  `.web/` untouched.
* `results-php/preflight/*.preflight.json` and `results-php/ph55-*.json` /
  `results-php/gate/ph55-*.json` / `results/tables/ph55-*.md` moved, as a new
  row requires.

---

## 14. The running count

`PROTOCOL.md` rule 2's *"number of times an agent refuted the manager with a
measurement"*, PHP programme. ⚠ **I could not find a stated value to launch
from**: `.tasks-php/README.md` says the count lives in the closing paragraph of
the newest `TASK_PHP_NNN*.md` and **neither `TASK_PHP_047.md` nor
`TASK_PHP_048.md` carries one**, which is itself worth the manager's attention —
a count that lives in exactly one place and is then omitted is a count that has
stopped existing. This task adds, by my own tally, **nine**: the tier (§8), `inside_share` on the C cells
(§7), prediction 1's two halves (§3b), prediction 2 and its mechanism (§3c), the
`NEXT_OPCODE();` count (§3), the `identity: exact` pin (§11a), and **this row's
own published family-B point value for clang, refuted by its own re-run** (§3c)
— plus **seven**
findings nobody predicted (§4), **two of which are refutations of my own work
rather than the manager's**: the two false claims this row shipped and repaired
(§4e), and the gate race I caused by truncating a liveness check (§4f). ⚠ **The
manager reconciles the count; I do not carry it.**
