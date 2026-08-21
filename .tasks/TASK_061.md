# TASK_061 — land p27's review: no blocker, and the decomposition is now CLOSED

**Role:** research engineer (you built p27; this is its corrections task — the
third task every pattern here has needed).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_060_REVIEW_REPORT.md`
in full**, then your own `patterns/p27-handle-table/NOTES.md`, then
`.memory/01-ladder.md` (**the direction test**; **finding 18 (p10)** — its
blocker was the same sentence as your major 2) and `.memory/03-measurement.md`
(the two `Ir` conventions, the inline-mode rule).

**The review found no blocker, 3 majors, 8 minors and 28 clean negatives**, and
it *closed* two things you left open. Most of p27 reproduced exactly — §3's 16
kernel-exclusive numbers, §3d's pad table, §4's three `panic_bounds_check` sites,
§5e, §7's determinism table, `r3_issome ≡ safe_naive` to the last digit. **Do not
re-measure what reproduced.**

⚠ **Two things the review settled that you should NOT re-open:**

- **A1 is a clean negative and it is the strongest result in the review.** The
  twin regime is **not** circular: four weakenings of the trusted contract, each
  editing item *and* twin together, all fail at **twin 19/1**. Weakening the
  trusted item alone verifies **20/0** — Verus does not catch it — and the
  structural `norm_clause(twin.sig) == norm_clause(t.sig)` rule does. **Both legs
  are load-bearing**, which nothing on this project had shown before.
- **A2: the TCB-vs-identity trade is not p27's to make.** **18 of 18 shipped
  `spec.md` files pin `O0: norel, O3: exact`**, so TCB 5 would make p27 the only
  pattern that cannot support ladder finding 1 — on the largest ghost state in
  the tree. **Ship 7.** Say it that way; "we chose the bigger TCB" invites the
  question that the 18-of-18 fact answers.

## The three majors

**M1 — `verus.rs:37-41` asserts four things that are false of its own file.**
*"The table is indexed CHECKED … a `get_unchecked` accessor would buy zero
instructions and cost two trusted items. ../NOTES.md 4 has the disassembly."*
The same file lists those two accessors as **trusted items 2 and 3 twenty lines
above**, and NOTES §4 is the section that **refutes** the claim. You corrected
`unsafe.rs` and not `verus.rs`. **Sweep both again and say how you swept** —
this is the second pattern running where a correction reached one source and not
its twin.

**M2 — a CHEAPER ADMISSIBLE R4/R5 PAIR EXISTS, so "degenerate as far as this
task searched" is false.** Deleting the epilogue's **dead**
`arr_set_unchecked(&mut live, j, 0u8)` (`unsafe.rs:200`) is worth
**−6.8073 / −10.4994 `Ir`/call**, whole-program and kernel alike — almost exactly
one instruction per record alive at scope exit (`nopen − nclose` = 6.75 / 10.50).
R5 with the epilogue invariant weakened to `[j, ntab)` verifies **15 verified,
0 errors**, `asm.py diff` says **`identical by raw machine-code bytes : True`**,
checksums match on all seven inputs, every `idiom.required` token is present at
the shipped count and no forbidden token appears.

> **Manager's decision, and argue with it if the measurement disagrees: SHIP
> IT.** This is not a spelling preference — **it is a dead store in R4 that R3
> does not have**, i.e. a handicap the unsafe rung was carrying. Leaving it in
> makes the safe rung look better, and that is precisely
> `.memory/01-ladder.md` finding 18's blocker: *an unsearched R4 side flatters
> the safe rung.* p10 shipped that error and p27 would be **the second pattern
> in a row**. Run the direction test **in writing**: shipping it moves the
> headline in the **unflattering** direction for safe Rust, which is the reason
> to trust it. Re-measure, republish, and **keep the before/after in NOTES.**
> Then re-state the R4 side as *"cheapest found"* with the input named — never
> "minimum" — and say what you searched.

**M3 — NOTES §11's scope note is wrong in both directions, though the churn
itself is fine.** `adversarial-many` is **exactly as non-reproducible as
`adversarial-noreuse`** (24 of 24 values distinct across 8 C cells × 3 runs), and
the gate prints **4** notes, not 2. A two-run gate-JSON diff is PASS→PASS,
0 failures, `contract_sha256` unchanged, **31 of 1290 leaves changed — 28
adversarial (16 stdouts + 12 group permutations) + 3 ASan PIDs**. **The churn is
acceptable and the review verified why**: `--check-stale` hashes sources and
blobs only, and `results/p27-handle-table.json` records `small`/`large` only.
**Fix the scope note to the measured numbers and keep the reason.**

## The addition that matters most

**The 46% you left unattributed is now attributed, and it changes what p27
claims.** The review built the missing controls; all print shipped checksums.
Kernel `Ir`/call on `small`:

```
unsafe            928.3500
r4_tabchecked     969.9715   (+41.62)
r4_bufchecked    1040.2407   (+111.89)
r4_allchecked    1081.8622   (+153.51, exactly additive)
safe_tuned       1031.1904   (+102.84)
```

> **An R4 that keeps R3's bounds checks costs `+153.51`, and R3's whole in-kernel
> excess is `+102.84` — so R3 pays `50.67` LESS of the spatial tax than an
> unsafe rung carrying the same checks. NOT ONE INSTRUCTION of `R3 − R4` is the
> lifetime guarantee.** Call targets are resolved by GOT reloc + `nm`:
> `safe_tuned::kernel` has **5** `panic_bounds_check`, `unsafe::kernel` has 0.

**And the decomposition is now closed**, by parsing the whole annotate table
rather than four named functions: `kernel` +102.8404, `drop_glue` +120.4218,
`malloc` and `free` **equal to the last digit**, `_int_malloc`, `_int_free`, the
unix shim and all three `__rust_*` also equal — and **the sum over every function
= 223.2621 = the whole-program delta.** Nothing else moved. **Write it as a
closed decomposition**, because that is a much stronger statement than four
needles agreeing.

**Also land the clang sweep** (one command; `--cells` and the fit pair already
existed): `R1h − R1 (clang)` gives `nread = 1.2235`, `nclose = 0.0370`,
`nrej = −0.9519` against gcc's `nread = 1.9408`, `nclose = 1.8017`. **The
conjunct itself differs by 1.59×, not the 4×/24× your §-note called the most
interesting unexplained number here** — gcc's unexplained `nclose` term is
confirmed as codegen churn by an independent compiler, and clang's **negative**
`nrej` is what collapses its `large` total. Both fits predict the matrix inputs
inside their residual.

## The minors

- `spec.md` and `verus.rs` still say `rec_alloc` has **"five `ensures` …
  character for character"**; three ship.
- ⚠ **`R5 − R4` `large` `+0.0132` does not reproduce and must be RETRACTED, not
  re-measured.** The review gets `+0.0020` deterministically and `+0.0104` under
  a longer scratch path — **it is a heap/argv artefact**. And the arithmetic
  never worked: `0.0132 × 5000 = 66`, not 132. **It must not reach `.memory/`.**
- **`adversarial-stride3` runs ZERO kernel calls**, so *"ASan clean on all four
  benign"* is really three. Say three, and say why the fourth is empty.
- NOTES §3d's clang inversion holds on `n_fn` and **reverses on `n_fn_nopad`**.
- NOTES §5c's identity table lacks `O3/whole` **without saying there is no
  `kernel` symbol there**.
- The `+102.84` is now attributed but not decomposed mnemonic by mnemonic; say so.
- ASan PIDs churn every gate JSON tree-wide — note it, do not fix it.

## One thing to record that is not a correction

**The direction test was verified BYTE-EXACTLY**, and this is the first time on
this project. Reconstructing the pre-build contract from your two disclosed edits
**alone** reproduces `b1f2dbb3e48542af…`, and *neither edit alone does*. So "no
`required`/`forbidden`/`obligations`/`identity`/`miri` entry moved" is **provable
rather than asserted** — which is exactly what PROTOCOL's definition-of-done 6
was added for, and the first time the recorded hash has actually been used to
verify a disclosure end to end. **Put that in NOTES §12** in those terms.

## Done when

Every claim above is corrected in `NOTES.md`, `README.md`, the shipped source
comments and `results/tables/p27-handle-table.md`; M2 is shipped and republished
with before/after; **`check.py p27` completely green** and
`measure.py --check-stale` clean. **Paste actual output.** ⚠ Editing a pattern's
docs makes its gate record STALE — re-run the gate **after** the doc edits.

## Constraints

No root; no `/tmp` (scratch `.temp/p27c/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any pattern other than p27.
Verus only via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**. Measurements in the FOREGROUND, per-PID
scratch paths. **You are the only agent running.** `harness/check.py p27` only.

**If a prescription here is wrong, say so with the measurement.**

⚠ **PROTOCOL rule 2's running count is 113** — 111 at TASK_060, plus two from
this review: `adversarial-many` is as non-reproducible as `adversarial-noreuse`
(so the task file's premise that only one row churns was wrong), and the
TCB-vs-identity "trade" is **not a choice at all** once you count that 18 of 18
patterns pin the same identity levels. **Carry 113 forward.**

⚠ **And one process failure of the manager's, recorded because the reviewer
caught it and the rule exists precisely for it:** `TASK_060_REVIEW.md` cited
`.tasks/TASK_060_REPORT.md`, which **did not exist** — your report lived only in
its return message. That is PROTOCOL rule 10's exact failure mode, second
instance. The file has been transcribed and now exists.
