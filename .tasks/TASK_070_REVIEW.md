# TASK_070_REVIEW — p22, where the manager's premise about `decreases` was wrong

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_070.md`, then **`patterns/p22-hash-probe/NOTES.md` in full**, then
`.memory/04-verus.md`, `.memory/03-measurement.md` (**the two `Ir` conventions,
the INLINE-MODE rule, the DOMAIN rule, the RESIDUE-CLASS rule**) and
`.memory/01-ladder.md` (**findings 18, 19 and 21 — three patterns with an
unsearched or under-searched R4 side**).

p22 is **gate-green**: `PASS-WITH-BLOCKED-ROWS` (expected — a declared-hang input
blocks a Miri row), **0 failures**, complete run, 32/32 cells agree on all three
good inputs, `R4 ≡ R5` `exact` at O3, Verus **20/0** (twin 23/0), 3 twins for 3
trusted items, `forbidden_hits` 0, 42 records 0 STALE. **PROTOCOL rule 9 holds
everything out of `.memory/` until you land.**

⚠ **The engineer settled both of the manager's named uncertainties with
measurements and refuted three prescriptions.** Those are dead. **Attack the
replacements.**

## A0 — the manager's own premise was FALSE, and it is in the task file and the catalogue

`TASK_070.md` says *"only R5 catches it, as a `decreases` obligation — a
termination proof, which no R5 here has ever had. Every existing R5 proves
safety."* The catalogue says the same.

**Measured by the manager while p22 was building: all 21 patterns' `verus.rs`
carry `decreases`** — p01 3, p02 5, p05 6, p06 9, p09 9, p13 13, p22 22, …
**zero patterns without one.** And the engineer found why: **Verus requires
`decreases` on every exec loop by default** (`error: loop must have a decreases
clause`), with an opt-out attribute that the pinned vstd itself uses in
`rwlock.rs`. **So every R5 in this tree has always proved termination.**

> **This is the review's first job, because the pattern's headline depends on
> it.** If p22 is not "the first termination obligation", **what is actually
> novel?** The candidate answer is that it is the first **non-trivial** measure —
> every other pattern's loop decreases on an obvious arithmetic expression, while
> a probe sequence needs a ghost unwrapped cursor, a ghost witness and a counting
> lemma. **Test that**: sample three or four existing `verus.rs` and characterise
> their `decreases` expressions. **If they are all `n - i`-shaped and p22's is
> not, the narrowed claim is real and should be stated precisely. If any existing
> pattern already carries a non-trivial measure, p22's novelty shrinks again and
> the write-up must say so.**

## A1 — the reframed headline. Is it a finding or a tautology?

The catalogue's *"R2/R3/R4 all hang"* was **reframed**: true of a mechanical
port, false of the shipped ladder. The published claim is now *"nothing on this
ladder EMITS the capacity check — five rungs write it by hand"*, with the bounded
spelling (`for _ in 0..TABCAP`) **forbidden by `spec.md`** on the ground that it
is a different function on a full table.

> ⚠ **A claim that survives only because the contract forbids its counterexample
> needs a hard look.** Is the forbid legitimate — is `for _ in 0..TABCAP`
> genuinely a *different function*, or merely a *safer* one? **If a reader would
> call the bounded loop the obvious way to write this, then "nothing emits the
> check" is a statement about p22's contract, not about Rust**, and the honest
> headline is smaller. **Say which, and quote the contract's `why`.**
>
> ✅ **The measurements that make this worth checking rather than dismissing:**
> `r3_bounded` is **440.84 / 3844.04 `Ir`/call FASTER** than shipped R3, so the
> bound is not being excluded on cost. Verify that, and verify the ASan/UBSan and
> Miri silence on the no-guard rungs (`rc=124`, empty stderr, 90 s spin) — that
> silence is what makes "memory-safe DoS" true.

## A2 — the R4 side, disclosed but 510× wide

`r4_reslice` is **in contract**, **verifies 20/0**, its **R4/R5 pair is
byte-identical at O3** (`md5_fn ea06db04c435`), and is **`1·nkw − 5` cheaper**.
So the published `R3 − R4 = +2.00` is a **fixed-R4 bound**, and against the
cheapest admissible R4 the same difference is **+125.00 / +1021.00 — 510× the
shipped figure on `large.bin`.**

> **This is the FIFTH consecutive pattern with an under-searched R4 side**
> (p10, p27, p38, p47 searched properly, p22). ⚠ **The difference here is that it
> was disclosed proactively** — verify the disclosure is complete and reaches
> `README.md`, not only `NOTES.md` §4d. **Then check the direction**: does the
> gap flatter safe or unsafe? And is `r4_reslice` genuinely admissible — same
> checksums, in contract, twin verifying — or does it fail something the
> engineer did not check?

## A3 — the proof. Is the termination argument real, or is the mutant lying?

Route (a′): a **ghost** unwrapped cursor `u` with `i == u % TABCAP`, a **ghost**
witness `e` for an EMPTY slot from a counting lemma, `decreases i0 + d - u`, and
**nothing added to exec code** so `R4 ≡ R5` stays `exact` — i.e. the termination
proof costs **0 instructions**.

> ⚠ **The engineer flagged this themselves and it is the sharpest thing to
> check**: `m1_noguard` fails on **`lemma_exists_empty`'s precondition, not on the
> `decreases` line**. **Is p22's proof actually a termination result, or a safety
> result that happens to be spelled as one?** Read the failure. `m2_nodecreases`
> failing with *"loop must have a decreases clause"* is Verus's **default**, not
> p22's achievement — **say whether any mutant fails on the MEASURE itself.**
> - **Is `lemma_exists_empty` sound**, or does it assume what it proves? Recount
>   the TCB (claimed **5**). Are the `requires` satisfiable — does a real call
>   site verify, or is it vacuous?
> - **`m5_wronghash` is the no-op control at 20/0** — confirm it is genuinely a
>   no-op and not a second live mutant.

## Also in scope

- ⚠ **HARNESS FINDING, reported not fixed — verify and scope it.**
  `check_miri`'s block text says *"R4 does not return under Miri either"*, which
  is **false on p22**: `c/kernel.c` hangs, `unsafe.rs` returns (`rc=0 UB=False`,
  run by hand). `expected_hang` is per-**input**, but its Miri consequence
  assumes the hanging rung is the one Miri runs. **Is that false for every
  pattern shaped like p22 — i.e. every pattern whose bug is in R1?** If so it is
  a `major` about the gate, not a p22 note, and the repair needs a per-rung axis.
- **`_confirm_hang` at ONE cell**: the engineer recommends leaving it, because all
  8 hung cells are the same two programs × opt × mode and checking all costs
  160 s against 20 s. ⚠ **They also propose a cheap strengthening — pick the cell
  per DISTINCT RUNG rather than first-in-sorted-order.** **Is that strictly
  better, and would it have caught anything here?**
- **The laws**: `R2 − R3 = 2·nkw + 17` (residual 0.00 on 30/30),
  `R3 − R4 = 2.00` flat (32/32), decomposed as reslice `2·nkw + 11` + iterator
  `6` flat. ✅ **Additivity passed AND the residue class was tested** — the p38
  lesson applied. **Verify the residue-class claim specifically**; it is the first
  time that rule has been used prospectively.
- **`c-clang-h − c-clang = 5.00/key` against gcc's `1.00/key`** — the mechanism
  is **stated as a presumption** and not disassembled. **Either derive it or
  confirm it stays labelled.**
- **`contract_sha256` moved once**, prose only, disclosed in §11c. ⚠ **The
  `git show HEAD:` check is runnable NOW** (p22 is committed at `b7cd39b`) where
  it was not when written — **run it.**
- **`inputs/gen.py` audits every window by simulating the unguarded rung and
  refuses to write an undeclared hang.** Nice; **check it cannot be fooled**, and
  that the 30 sweep blobs are excluded from the matrix as `sweep-*`.

## Clean negatives are wanted

PROTOCOL rule 6. Recent reviews returned 21, 28, 32, 35 and 38 named attacks.
**List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch **`.temp/p22rev/`** — your own subdirectory; read
`.temp/p22/` but do not modify it); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under `patterns/`.
⚠ **p22 deliberately builds programs that never return — always `timeout <N>`,
never background, never `pkill`.** You may re-run `harness/check.py p22`; **a
gate run rewrites `results/gate/p22-hash-probe.json`, so restore it with
`git checkout --` and say that you did.** Verus only via `./verus_run.py`;
`~/tools/verus/vstd/` for vstd source. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none but gcc on PATH. **You are the only agent running.**

**Write `.tasks/TASK_070_REVIEW_REPORT.md` before you finish** (rule 10), then
return the same content in the report format. Rank findings `blocker` · `major` ·
`minor`, with file:line and a concrete failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** ⚠ **Running count
151** — 148, plus three from p22's engineer: the hung-cell count (**8**, not the
manager's 12–20), the Verus route (**neither (a) nor (b)** — a ghost cursor plus
a counting lemma, costing 0 instructions), and *"the careful programmer pays for
the bound"*, which is **false** — the bounded probe is **faster**.

**What I am least sure of, by name: A0 and A1, and they are connected.** I wrote
that no R5 here had ever proved termination and **that was false on all 20
patterns** — I checked it myself, after writing the task. So p22's novelty rests
entirely on the measure being *non-trivial*, and its headline rests on a spelling
its own contract forbids. **Both could be right. Both could also be a pattern
that is mostly a contract.** Settle them before anything reaches `.memory/`.
