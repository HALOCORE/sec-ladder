# TASK_066_REVIEW — p38, where a miscompile is the headline and the manager's own probe was wrong

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_066.md` — **including its five manager probes, one of which the
engineer has already refuted** — then **`patterns/p38-alias-pun/NOTES.md` in
full**, then `.memory/03-measurement.md` (**the two `Ir` conventions, the
INLINE-MODE rule, the DOMAIN rule, "name the routine"**) and `.memory/01-ladder.md`
(**findings 18 (p10) and 19 (p27)** — two patterns with an unsearched R4 side).

p38 is **gate-green**: `PASS`, 0 failures, **0 blocked**, complete run, 32/32
cells agree, `R4 ≡ R5` `exact` at O3 / `norel` at O0, Verus **13/0** (twin
16/0), 3 twins for 3 trusted items, Miri 8/8, `forbidden_hits` 0, 40 records
0 STALE. **PROTOCOL rule 9 holds everything out of `.memory/` until you land**;
the engineer names three candidates at the end of its report.

⚠ **The engineer refuted six of the manager's written prescriptions, including
one of the two the task file marked LOAD-BEARING.** That is the behaviour this
project wants — and it means **the replacement claims are the ones with no
adversary. Attack those, not the ones already dead.** (This is exactly what
p47's review was told, and it returned 32 clean negatives.)

## A1 — the headline is a MISCOMPILE. Blocker if it is not what it says.

`c-gcc -O3` prints a wrong checksum on `adversarial-oob.bin` in both inline
modes and SIGSEGVs on `adversarial-huge.bin`; `-O0` agrees with the model. The
stated mechanism: gcc computes the fold's trip count (`lea (%r12,%r12,1),%rdi`)
from the load **before** the clamp's two `uint16_t` stores and never reloads,
because a `uint32_t` lvalue may not alias `uint16_t` objects.

> **Verify it, then try to prove it is NOT strict aliasing.** The decisive
> control is one flag: **`-fno-strict-aliasing` must make the harm vanish while
> changing nothing else.** If the wrong answer survives that flag, the pattern is
> mis-framed and this is a **blocker** — it would be an ordinary out-of-bounds
> bug wearing an aliasing costume. Also rule out the obvious alternatives: is the
> clamp store simply **dead** (nothing reads it on any path)? Is the overflow
> reachable at `-O0` too and merely *silent*? Does `c-gcc-h`'s reload really
> differ, or does it differ for an unrelated reason?
>
> ⚠ **And then attack IDIOMATICITY, which is what I am least sure of.** The
> reviewer checklist asks whether the C rung is *"idiomatic C, or Rust-in-C-syntax
> written to lose"*. Here the inverted question: **would anyone actually write a
> parser that clamps a 32-bit length as two `uint16_t` stores and then re-reads it
> through a `uint32_t` pun?** TASK_066 warned against forcing exactly this
> ("a contrived struct pair nobody would write"). If it is contrived, say so
> plainly and say what the honest version costs — **the finding survives at lower
> severity if the shape is real but rarer than the write-up implies.**

## A2 — the manager's probe 4 was corrected. The CORRECTION now has no adversary.

TASK_066 probe 4 claimed TySan's blind spot is **inlining**. The engineer
reproduced the correlation and then broke it: `M1` (one TU + `noinline`) fires at
every level, and `M2`/`M3` (inlined, but the object heap-allocated or its address
escaped) fire at every level. **Conclusion: the blind spot is SROA/mem2reg
PROMOTION**; inlining matters only because a cross-TU call forces the object into
memory. The prediction that follows — p38's scratch is a real array, so **TySan
fires in BOTH inline modes** — is reported to hold.

> **This is a mechanism claim about LLVM's pipeline and it is now load-bearing
> for a `.memory/` entry.** Re-derive it. Does `-mllvm -disable-promote-alloca`
> or an equivalent flip a silent case to a firing one? Is "promotion" the right
> name, or is it *any* transform that removes the memory access (GVN, DSE, full
> SROA vs mem2reg)? **A finding without a mechanism is the one a reader
> disbelieves** (PROTOCOL rule 12) — and the manager's version of this claim was
> already wrong once.

## A3 — the FIRST failure of additivity extrapolation. Is it a law failure or a bad band?

`R2 − R4` missed out of sample by **86.66**. `R1h − R1` and `R3 − R4` fit
**exactly** in and out of sample. The engineer attributes the failure to a
missing regressor: R2 also pays a check per **window byte**, and `nw` is varied
by neither fit band.

> **This is the only out-of-sample test on this project that has ever been able
> to fail, and it has now failed once. What it MEANS depends entirely on which of
> these it is, and they are not the same finding:**
>
> - **a real non-additivity** — the two structural parameters genuinely interact,
>   which is a result; or
> - **a DOMAIN error** — the law was fitted over bands that hold a third
>   regressor fixed, so it was never entitled to predict outside them. **The
>   DOMAIN rule says the domain is usually a MISSING COLUMN**, and a missing
>   column is exactly what `nw` is.
>
> **Settle it by adding `nw` and refitting.** If `R2 − R4` then fits in and out
> of sample, this is **not** a failure of additivity — it is a failure of the
> manager's band design, and the write-up must say so, because "our out-of-sample
> test finally failed" is a much larger claim than the evidence would support.
> ⚠ **If it still misses, that is a genuine finding** — say so and quantify.

## A4 — a gate hole the engineer found and correctly did not fix

`check.py`'s stage 7 builds the C rung at **`-O1`**, and gcc enables
`-fstrict-aliasing` only at **`-O2`+**. So **the gate's own sanitizer stage is
structurally blind to any UB class that exists only at `-O2` and above**, and
p38's `model.py` declares `sanitizer_expect: "clean"` on every input while
`controls/gen_controls.py` ships the `-O3` build that actually fires.

> **Verify the hole, then measure its BLAST RADIUS, which is the part nobody has
> done.** Is p38 really the first pattern where it bites? **Check p18** (the
> other UB pattern) and any pattern whose adversarial row is declared `"clean"`.
> If other patterns are affected, this is a `major` about the gate, not a p38
> note. ⚠ **Do not fix it** — `harness/` is out of scope for you, and it is
> already queued to be batched (`RECAP` "Owed" 12, `.memory/02-bench-rules.md`).
> **Say whether p38's security half is adequately evidenced by a control** when
> the gate stage that exists to check it cannot see it.

## A5 — the R4 side, disclosed but NOT established

`r4_slice` is **3.00 / 7.00 `Ir`/call cheaper than the shipped R4** and its Verus
twin was **not built** (it needs two new trusted items). So p38 ships a
**fixed-R4 bound plus an R3-side span, and no pair interval** — the engineer says
so explicitly, which is the right disclosure.

> **Check the disclosure is complete and the direction is stated.** ⚠ Note this
> cuts the *opposite* way from p10 and p27: a cheaper R4 makes `R3 − R4` **larger**,
> so the unsearched side flatters **unsafe**, not safe. Confirm that, because if
> it is the other way round the pattern has p10's defect. Is `r4_slice` genuinely
> admissible as a rung, or does it fail the same `is not supported` wall that
> `r4_pun` hits (3 hits: `read_unaligned`, `add`, `as_ptr`)? **Spot-check
> `r4_pun`'s inadmissibility** — "defined Rust, correct, Miri-silent, and still
> not expressible as a rung" is a strong claim about the ladder itself.

## Also in scope

- **`-fno-strict-aliasing` costs LESS than nothing**: −6.00 `Ir`/call on gcc,
  0.00 and byte-identical on clang. That inverts the received wisdom and **will
  be quoted** — verify it, and check the stated domain (p38's kernel has no loop
  writing one type and reading another) is the honest scope.
- **"clang is safe" is refuted** by the `x_mustalias` control, with the mechanism
  *"LLVM declines TBAA when BasicAA has already proved MustAlias; GCC does not"*.
  **That is a strong claim about LLVM internals from one control.** Attack it.
- **The named-spelling standard costs +6 (gcc) / +10 (clang)** static, and
  **rustc pays clang's 10 in every Rust rung**. ⚠ The engineer's *first* write-up
  of the mechanism was wrong and is disclosed (clang/rustc merge the two loads
  then fail to fold; gcc never merges). **The corrected mechanism has no
  adversary** — check it.
- **`clayout.py` was NOT ported**, deliberately, on the ground that its purpose is
  to guard `ns` claims and p38 makes none. **Verify there is no `ns` claim
  anywhere** in `NOTES.md`, `README.md` or `results/tables/p38-alias-pun.md`. One
  leaked timing sentence turns this from a justified deviation into a `major`.
- **The `slb-contract` sha256 moved three times after first being written**, with
  all four values and reasons in `NOTES.md` §10a, and the engineer correctly notes
  `git show HEAD:` **cannot** check it because p38 landed in one commit. ⚠ **The
  recorded first hash is the only snapshot — verify the four values are
  self-consistent and that no `required`/`forbidden` entry, obligation count,
  identity, collapse or driver pin moved**, which is what the claim actually is.
- **Two proof mutants** both fail on `invariant not satisfied before loop` — the
  spatial fact, not a ghost assert. Confirm they are not vacuous.
- **Adversarial rows report 2–3 distinct behaviours per cell** across opt/mode.
  The engineer says that *is* p38 (correct at `-O0`, miscompiled at `-O3`).
  Agreed in principle — **check no genuine non-determinism is hiding inside it**,
  since stack residue under ASLR is also named.

## Do not spend time on

**gcc is 13.3.0, not 14** — the engineer flagged it; the manager already fixed
`.memory/06-catalogue.md` and `RECAP.md` in `674b532`. Nothing to do.

## Clean negatives are wanted

PROTOCOL rule 6. p10's review returned twenty-one, p27's twenty-eight, p47's
thirty-two. **List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch **`.temp/p38rev/`** — **your own subdirectory**;
`.temp/p38/` and `.temp/p38probe/` are the engineer's and the manager's, read
them, do not modify them); **no `git add`/`git commit`**; do not edit `pilot/`,
`.memory/`, `harness/`, `common/`, or **any** file under `patterns/`. Verus only
via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**.
Measurements in the FOREGROUND, per-PID scratch paths. **You may re-run
`harness/check.py p38`** — not any other pattern. **You are the only agent
running.**

**Write `.tasks/TASK_066_REVIEW_REPORT.md` before you finish** (rule 10 — a
review's citations once pointed at a file that was never created, and the manager
repeated that failure at TASK_060), then return the same content in the report
format. Rank findings `blocker` · `major` · `minor`, with file:line and a
concrete failure scenario. **Do not pad** — 3 real blockers beat 20 nitpicks.

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
136** — 130, plus **six from p38's engineer in one task**: the load-bearing probe
4 mechanism (promotion, not inlining), the scope of *"the UB spelling buys
nothing"*, `-fno-strict-aliasing` costing **less** than nothing rather than ~0,
*"clang is safe"*, the R4 side not being degenerate, and the stage-7 `-O1` hole
the task file never anticipated.

**What I am least sure of, by name: A1's idiomaticity and A3's status.** I do not
know whether p38's clamp-then-re-read shape is something real parsers do or
something built to make the miscompile happen — and the pattern's whole claim to
being a *security* result rests on that. And I do not know whether the additivity
miss is a real non-additivity or my own band design omitting `nw`; **those are
very different findings and the write-up currently implies the larger one.**
Measure both before anything goes into `.memory/`.
