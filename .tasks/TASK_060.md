# TASK_060 — p27, the LIFETIME pattern: the one bug class this project has never had

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.tasks/TASK_055_REPORT.md` §2 and `.tasks/TASK_055_REVIEW_REPORT.md` in
full** — those two are the feasibility work this pattern rests on, and the review
overturned part of the report. Then `.memory/04-verus.md` (**the `vstd::raw_ptr`
section, its THREE build constraints, and the TCB decision**),
`.memory/03-measurement.md` (**the tcache section — the reproducibility trap**,
the DOMAIN rule, **the inline-mode rule from p10**, the layout/`ns` sections),
`.memory/02-bench-rules.md`, then **`patterns/p10-fir-stencil/` and
`patterns/p14-field-split/`** as templates.

## Why this pattern matters more than the last five

**Every bug in this tree is spatial or logical. This is the one class safe Rust
rejects at *compile* time**, and the one where safe Rust's cost is not a check at
all but a **different data structure**. No pattern here has that axis.

**The proof half is already settled and it is cheap** — do not re-derive it. The
ghost loop that splits `PointsToRaw` `n` times under an invariant into
`Map<int, PointsTo<u8>>`, joins all `n` back, and does a real `deallocate`,
verifies **7 verified / 0 errors** with **zero project-local `external_body`,
`assume` or `unsafe`**, at **150 ms / 711,948 rlimit** — and raising the bound
from `n <= 4096` to `n <= 1_000_000` gives the **identical rlimit**, because it
is proved symbolically. `.temp/p55rev/a1_ghostloop.rs` is the working file.

## §0 — settle the bug class, the shape, and ONE THING THAT COULD KILL IT

⚠ **Do `§0.1` before you write any rung.** See "the shape" below: the harness may
not be able to express this pattern at all, and the one known escape is
**unmeasured at `-O3`**.

**The bug class.** `.memory/06-catalogue.md` rates p27 *"singly linked list
(build, traverse, free) — use-after-free, leak"*. **Treat that as a prior**;
four patterns have overturned their row and two have upheld it. Two candidates
worth pricing against each other in `NOTES.md` §0:

- **The textbook list free** — `for (p = head; p; p = p->next) free(p);`, which
  reads `p->next` **out of the chunk it just freed**. One line, universally
  recognised, and the correct version is `n = p->next; free(p); p = n;`.
- **A handle table** — records `malloc`'d individually, a table of handles, a
  real `free()` on close, and a stale handle dereferenced afterwards. This is the
  formulation TASK_055 §2.8 recommends **because it forces the interesting
  ladder**: safe Rust cannot hold the pointer, so `(slot, generation)` is
  *forced*, and safe Rust's cost becomes **a wider handle plus an indirection
  plus a generation compare** rather than a bounds check.

⚠ **Whichever you pick, `free` must be a REAL `free`/`deallocate`.** If the slab
is one allocation and "free" is a freelist push, the stale read is **in bounds of
a live allocation**: Miri does not flag it, `PointsTo` licenses it, and the bug
is *logical* — which is p17's class, and the tree already has one. **That is the
difference between building the missing axis and building a seventeenth variant
of something we have.**

### §0.1 — the shape, and the measurement that gates it

The formulation wants **different signatures per rung** — `kernel(handles, k)` at
R4/R5 and `kernel(slab, handles, k)` at R1h/R2/R3. **`harness/dloop.py:361`
raises on arity**, and TASK_055_REVIEW tried ten alias/`call_args` combinations
without reconciling them.

> **The one escape measured to work is a DEAD `slab` argument on R4** (`identical?
> True` against the two-argument build). ⚠ **Whether that survives `-O3` codegen
> is UNMEASURED.** **Measure it first.** If a dead argument is optimised into a
> difference, say so and stop — **that is a `harness/` question and you must
> report it, not fix it.**

**And answer the fairness question in writing.** `.memory/02-bench-rules.md` and
the reviewer checklist ask *"are the rungs semantically equivalent, or did a rung
quietly change the algorithm?"* Here they are **deliberately different data
structures**, which no shipped pattern has needed. **State what the equivalence
argument has to establish for `R2 − R4` to mean anything**, and if you cannot
state it, say the pattern needs a different shape — now, not after five rungs.

## The reproducibility trap — read this before designing inputs

**The offset-16 fix was necessary and is NOT sufficient**, and the reason is not
a measurement problem:

```
gcc  -O0/-O1/-O2/-Os : 2582767925679282152     gcc   -O3        : 6789584477807083544
clang -O0            : 2582767925679282152     clang -O1/-O2/-O3: 6789584477807083544
```

`build.py`'s `OPTS = ["O0","O3"]` puts both in one matrix and stage 2 rejects
disagreeing cells. **And at `-O3` the stores into the recycled slab are
DEAD-STORE-ELIMINATED** — three `movups` into the *first* slab and **no store
loop into the recycled one at all** — so **the `-O3` row does not execute the bug
it claims to model.** A checksum that agreed would have been agreeing about the
wrong program.

> **Put the UAF on ADVERSARIAL inputs only**, where `check.py` records behaviour
> per rung and does not require cells to agree. Precedent:
> `results/gate/p06-rotate.json` records four behaviours in four cells for one
> input. **Every benign input must keep every rung on the defined path.**

## What p27 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell.**
- **TCB: one number plus the U-license / V-gap / infra classification, and PROSE
  saying how the rung reaches unchecked memory.** The `tcb_reach` column was
  proposed, attacked and **rejected** (`.memory/04-verus.md`). ⚠ This pattern
  will publish a **smaller** `tcb_items` than p01 while doing manual allocation.
  **Say so in the pattern's own text**; do not let the number stand alone.
- **Two proof mutants that FAIL.** Confirmed satisfiable — two gate-style mutants
  on a zero-trusted-item file give **6 verified / 1 errors** each.
  ⚠ **The R5 catcher is an ordinary `precondition not satisfied`, NOT rustc's
  move checker.** The `E0382` in the probe report is an artefact of a
  hand-unrolled two-element probe and is **retracted**; with a real permission
  map the failure is `wf(d@,*perms,n as int)`.
- **Two in-contract R3 spellings, and quote the cheaper**, input named, "cheapest
  found" not "minimum".
- **NAME THE INLINE MODE at every figure.** p10 fitted both and its regressors
  **swapped roles**; a mode-free per-call `Ir` is under-specified.
- **A law owes its DOMAIN, and the domain is usually a MISSING COLUMN.** p10 went
  3 → 4 → 6 parameters. Say which you established and that the list is not closed.
- **No `ns` claim without a layout population**; port `controls/clayout.py`.
- **Attribute per-iteration `Ir` mnemonic by mnemonic**, and **check the panic
  pads** before calling anything a safety cost.
- ⚠ **Before publishing any rung comparison, ask what the OTHER rung's spelling
  is worth.** p10 shipped *"safe Rust is cheaper than unsafe"* and 60% of it was
  an unsearched R4 side. **This is the newest trap on the project and it passed a
  green gate.**

## Verus

Budget **one session** past what is already proved. Use `~/tools/verus/vstd/` —
**not** `../LearnVeri/_VERUS_DOC_/vstd/`, which is an older snapshot missing
specs that exist (`CLAUDE.md`). `allocate`/`deallocate`/`ptr_ref`/`ptr_mut_write`
are `external_body` **inside vstd**; `split`/`join`/`into_typed` are vstd
`axiom fn`s. Gotchas already found: `align_of_u8` sits outside the broadcast
group, `Set::new` returns an `Option`, `SharedReference::new` is private
(`E0624`), and `global size_of usize == 8;` may be needed for `usize` arithmetic.

## Done when

The p10 checklist, plus §0's decisions and §0.1's measurement. Complete green
`check.py p27`; checksums against an independent `model.py`; adversarial rows
per rung with distinct harms in distinct columns; the `idiom` block written
**before** the cells; sweep with its fitter under `controls/`; both R3 numbers;
two failing proof mutants; TCB equal to the gate's own `tcb_items`;
`measure.py --check-stale` clean. **Paste actual output.**

## Constraints

No root; no `/tmp` (scratch `.temp/p27/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any existing pattern.
**If p27 seems to need a `harness/` change, STOP and report it** — that
constraint is more likely to bite here than on any previous pattern, because of
§0.1. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**. Measurements
in the FOREGROUND, interleaved by cell, per-PID scratch paths. Run
`harness/check.py p27` only. Delete binaries and blobs once green; **keep every
generator.**

Notes to `.temp/p27/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** ⚠ **PROTOCOL
rule 2's running count is 104** — 100 at TASK_059, plus four from
TASK_055_REVIEW: the offset-16 reproducibility rule was insufficient *and* the
`-O3` row did not execute the bug, the move-checker mechanism was a probe
artefact, the manager's `tcb_reach` column was refuted, and the TCB recount
command the manager had just "fixed" was wrong in the other direction.

**What I am least sure of is §0.1 — whether this pattern is expressible in the
harness at all.** The dead-argument escape is one measurement by one reviewer and
has never been through a build at `-O3`. **If it does not hold, report it and
stop**; the honest outcome is "the missing axis needs a harness change", which is
a real finding and cheaper than five rungs that cannot be compared.
