# TASK_072 — p36, function-pointer table dispatch: the first INDIRECT CALL in a kernel

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.memory/06-catalogue.md`'s p36 re-triage** (the block beginning *"p36
(vtable dispatch) — likeliest to hit p55's wall"*, which was **rewritten at
TASK_066 and its risk cut**), then `.memory/04-verus.md`,
`.memory/03-measurement.md` (**the two `Ir` conventions, the INLINE-MODE rule,
the DOMAIN rule, the RESIDUE-CLASS rule**) and `.memory/02-bench-rules.md`'s
**last three sections**. Templates: `patterns/p22-hash-probe/` (newest) and
`patterns/p38-alias-pun/`.

⚠⚠ **THE LEADING RULE, AND IT IS NEW BECAUSE THE MANAGER BROKE IT LAST TASK.**
*"The first termination proof in the project"* was the manager's sentence in
`TASK_070.md`. It was **false** — all 20 prior patterns already carried
`decreases`, because Verus demands one on every exec loop — the engineer had no
reason to doubt it, and it shipped into **eight places, two inside
`contract_sha256`**, costing a review and a re-gate. **Every novelty claim below
is written as a QUESTION TO BE MEASURED. Treat any that is not as a bug in this
file and say so.** p22's §0 counted 73 measures in one command the moment it was
asked; the same command shape settles most of what follows.

## What p36 is, and the four claims that need settling before six rungs exist

A dispatch table: `static uint64_t (*const TABLE[N])(uint64_t)`, opcodes read
from the blob, `acc = TABLE[op](acc ^ arg)` in a loop. The bug is **no `op < N`
check**, so an out-of-table opcode loads a code pointer from past the array and
**calls it**.

**The catalogue calls this "the last of the six original axes — control-flow
integrity: every harm here is data."** ⚠ **That is a claim about the HARM. It is
not a claim about the ladder, and the ladder is what this project measures.**
The honest worry, stated plainly so you can kill it or confirm it:

> **Is p36 a bounds pattern in a costume?** The *bug* is `index >= len`, which
> is what eleven catalogued patterns model and what p01, p07 and p16 already
> ship. R2 panics on `TABLE[op]`, R3 hoists, R4 `get_unchecked`s, R5 proves
> `op < N`. If that is all p36 is, **it is the tree's twelfth bounds pattern and
> should not be built.** Four things could make it not that, and **each is a
> question, not a finding**:
>
> 1. **Does the CATCHER see the control-flow transfer, or only the array read?**
>    An out-of-table *load* from a global is an ordinary `global-buffer-overflow`.
>    If ASan fires on the load, the gate's catcher detects a **data** bug standing
>    in for a **control-flow** bug — which is a precise, publishable statement
>    about the limits of this checker set, and the opposite of what the catalogue
>    implies. **Measure which of ASan / UBSan / `-fsanitize=function` / Miri fires
>    and ON WHAT.**
> 2. **Is an indirect call a COST mechanism no kernel here has?** Every kernel in
>    the tree is straight-line or loop arithmetic. **No pattern has an indirect
>    call at all** — ⚠ **verify that with a command rather than believing this
>    sentence**; something like `grep -n 'call.*\*%\|call.*\*0x' ` over the
>    committed listings, or a `bulk_calls`/`asm.py` sweep. If it holds, the
>    dispatch is a branch-prediction and inlining barrier, and this project
>    already has `callgrind --branch-sim=yes` established on p07
>    (`.memory/00-environment.md`). **`Ir` and `ns` diverging for a named
>    microarchitectural reason would be the pattern's strongest half.**
> 3. **What does an indirect call cost the PROOF?** See the Verus section — this
>    is the item most likely to be fatal.
> 4. **Do the safe rungs even spell the same mechanism?** Rust's idiomatic
>    dispatch is `match` (direct calls, jump table) or `dyn Trait` (a real
>    vtable), not an array of `fn` pointers. ⚠ **If the safe rungs `match`, the
>    optimiser can devirtualise and inline and the rungs are no longer comparable
>    — that is the reviewer checklist's *"did a rung quietly change the
>    algorithm"* — but it may ALSO be the finding**: a `match` needs an exhaustive
>    arm, so **the language forces the check the C table omits**, which is p08's
>    *"safe Rust cannot express it"* shape arriving through exhaustiveness rather
>    than the borrow checker. **Decide, argue it, and ship the other spellings as
>    measured controls.**

**§0's deliverable is a written decision in `NOTES.md` §0 with the measurements
behind it, and the authority to say "p36 should not be built as specified".**
⚠ **The catalogue's bug-class guesses stand at three overturned, two upheld, and
p47 overturned its own row.** Treat the row as a prior.

## §0 — the order to settle them in, cheapest-fatal first

**Do these before writing any rung.** Each is minutes, not hours.

**§0a — CAN VERUS CALL A FUNCTION POINTER LOADED FROM AN ARRAY?** ⚠ **This is
the one that kills the pattern, and it is the manager's least certain call.**
The pinned vstd *does* ship function-value support — `~/tools/verus/vstd/function.rs`
(`ProofFnOnce`, `axiom_fn_mut_call_requires`, `call_requires`/`call_ensures`) —
and the guide chapter is `../LearnVeri/_VERUS_DOC_/guide/src/exec_funs_as_values.md`.
⚠ **But every example there is a GENERIC PARAMETER `F: Fn(u64) -> u64` passed to
a higher-order function.** p36 needs something different and strictly harder:

- a **`static`/`const` array of bare `fn(u64) -> u64` pointers**,
- **indexed by a runtime value**,
- **called**, with
- a **functional postcondition** — the kernel must checksum, so the proof has to
  know *which* function sits at index `op`. `call_ensures(TABLE[op], (x,), y)`
  gives you the postcondition of an unknown callee; relating it to a *value*
  needs the table's contents in the spec.

> **Write a ~20-line probe and run it through `./verus_run.py` before anything
> else.** Report the verbatim errors. Three outcomes, and all three are useful:
> **(i)** it verifies → p36 has an R5 and the proof-burden question in §0.3 is
> live and new; **(ii)** it verifies only with a `match`-shaped spec fn mirroring
> the table → say so, because *that* is the proof burden and it is quotable;
> **(iii)** `is not supported` → **p36 has no R5 and therefore no `identity` pin,
> which every one of the 21 patterns carries.** In case (iii) **STOP, report, and
> push back with `p48`** (below). Do not build four rungs and discover it.
> ⚠ **Use `~/tools/verus/vstd/`, never `../LearnVeri/_VERUS_DOC_/vstd/`** — that
> tree is an older snapshot and has already caused one false *"no spec exists"*
> that stood for 44 tasks.

**§0b — WHAT FIRES, AND ON WHAT?** The gate's stage 7 builds
`gcc -O1 -fsanitize=address,undefined` (`check.py::check_sanitizers`) — **no
CFI**. Probe, by hand, on a minimal out-of-table call:

- ASan on the **load** (`global-buffer-overflow` reading `TABLE[op]`) — does the
  redzone survive a `const` array of relocated pointers, which PIE puts in
  `.data.rel.ro`? **UNVERIFIED.**
- UBSan `-fsanitize=function` (indirect call through a wrong function type) —
  ⚠ **the box has carried this as UNVERIFIED since TASK_066. Settle it: does gcc
  13.3 accept the flag at all, and does clang?** It is *not* a matrix change if
  it is only used as a control.
- Miri on the Rust side, and valgrind.
- ⚠ **`-fsanitize=cfi` needs `-flto`, is clang-only, and is a `build.py` change
  = a FULL RE-MEASURE** (RECAP settled answer 4). **Do not reach for it as a
  rung.** Measuring it in a `controls/` probe and reporting the number is exactly
  right; changing the matrix is not.

**The bar, from the re-triage, and it is weaker than the catalogue's:** stage 2
(`check_checksums`) runs on **non-adversarial inputs only**, and stage 7's
exit-code check is short-circuited by the `expect == "fires"` branch, which
requires only that a sanitizer **fired** — not that the exit code matched. So a
**non-deterministic exit is already legal**. The binding requirement is *"a
sanitizer fires DETERMINISTICALLY"*, not *"the harm is identical"*.
⚠ **Verify that re-triage against the current `check.py` rather than trusting
it — it is a manager source-read, PROTOCOL rule 3 applies to it, and it has
never been executed.**

**§0c — IS THE HARM REAL AND REPRODUCIBLE WITHOUT A SANITIZER?** What does the
unguarded rung actually *do* on an out-of-table opcode, at each of the four
compiler × opt cells? Segfault, wrong answer, silent-correct? ⚠ **Name the cell
for every behaviour** — p02's whole security result is *"seven of eight builds
are silent"* and that only exists because someone tabulated all eight.
⚠ **And check the degenerate outcome**: if `N` is a power of two and the
compiler proves `op` is a byte, it may fold the index; if the table is small and
the adjacent object is benign, the call may return normally. **A pattern whose
adversarial row is indistinguishable from its perf row shows nothing.**

**§0d — IS THE INDIRECT CALL NEW?** The command from §0.2. If some existing
kernel already emits one, p36's cost half shrinks and the write-up must say so.

## Design defaults — take them or refute them with a measurement

- **Rungs spell the C mechanism**: R2/R3/R4/R5 all dispatch through
  `[fn(u64) -> u64; N]`, so the six cells compare like with like. **`match` and
  `dyn Trait` ship as `controls/`, measured and reported, NOT as rungs.**
  ⚠ **If §0a's outcome (ii) forces a `match`-shaped spec, say whether the exec
  code still indexes the table** — the `identity` pin is `unsafe ≡ verus, exact`
  at O3 and a spec-only difference must leave exec code alone (p22 did exactly
  this: a ghost cursor costing **0 instructions**).
- **R1h**: the source-level `if (op >= N)` check, priced. **`-fsanitize=cfi` is a
  control, not R1h** — but ⚠ **say in `NOTES.md` that the real-world hardened
  answer for this bug class is a compiler mitigation this matrix cannot price,
  and why.** That is a limit worth stating precisely, and it is p36's honest
  version of the catalogue's CFI claim.
- **Table ops must be cheap and pure** so the dispatch dominates: the finding is
  the *call*, not the callee. If the callee is expensive the indirect-call cost
  drowns and the pattern measures nothing.
- **Opcodes from the blob, one byte each**, with the operand — so the adversarial
  input is a byte edit and `inputs/gen.py` can sweep the in-table density.

## What p36 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**
  (PROTOCOL definition-of-done 6), and ⚠ **note in §11-equivalent that the
  `git show HEAD:` diff is UNAVAILABLE on a new pattern and why** — it compares
  working tree to HEAD, not first-written to shipped, so on a clean tree it
  always prints nothing and always looks like it passed. **The recorded first
  hash is the only evidence.** p22 cited that command and its disclosure has no
  artefact behind it; do not repeat it.
- **If `spec.md` is generated, fix the GENERATOR and re-run it** — three tasks in
  a row shipped an edit the generator silently reverted, one of them the task
  fixing that defect. **Read the shared named-spelling paragraph from a donor
  `spec.md`; never embed a copy.**
- ⚠ **`forbidden_hits` HARD-FAILS.** `exec_code` blanks ghost code, so `proof {}`
  and `assert(…)` are safe — **but three false-positive shapes survive**:
  substring, whitespace-collapse, and an entry that backticks the *replacement*.
  **Prefer longer, more specific spellings**, and **backtick every entry you want
  enforced** — an unbackticked entry is audited **zero** times while the verdict
  line still counts it. Recompute the denominator rather than quoting one:
  ```
  python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"
  ```
- ⚠ **SEARCH THE R4 SIDE, AND SEARCH IT BEFORE YOU PUBLISH A DIFFERENCE.**
  *"Degenerate as far as this task searched"* has now been **false on five
  consecutive patterns, and every time it flattered a rung** — p22 published
  `R3 − R4 = +2.00` against a true `+125/+1021`, **510×**. ✅ **p22 disclosed it
  before being asked, which is the standard now.** Publish the **fixed-R4 bound**
  *and* the span, the words **"cheapest found"** (never "minimum"), and **name the
  input** — on p03 and p16 the cheapest spelling changes with the blob.
- **NAME THE INLINE MODE at every figure.** p10 fitted both and the regressors
  *swapped*. Cross-pattern `Ir` is `isolated`-only: 302 of 318 `whole` cells have
  `kernel_exclusive_ir = None`.
- ⚠ **If you fit a law, it owes its DOMAIN, and check the RESIDUE CLASS of any
  parameter your bands hold constant** — p38's additivity failure was two of three
  bands sitting at `nw ≡ 0 (mod 8)`, which fits in sample and misses out of it
  with no in-sample residual to warn you.
- **No `ns` claim without a layout population**; port `controls/clayout.py` and
  ⚠ **point `OUT` and its scratch default at `.temp/p36/`** — p27's copy still
  said `.temp/p14/` and overwrote p14's `meta.json`.
- **Adversarial rows per rung**, and ⚠ **say what an adversarial row MEANS when
  the harm may be a segfault in one cell and a wrong answer in another.**
- **TCB: one number plus the U-license / V-gap / infra classification.**
- **Two proof mutants that FAIL**, and ⚠ **run the battery with
  `--multiple-errors`** — `.memory/04-verus.md` §2b prescribes it, p22 skipped it,
  and the review found a mutant failing on a different obligation than claimed
  and a third error nobody had seen. **Report the full error list per mutant.**

## Done when

§0's four decisions are written with their measurements; the p22/p38 checklist;
complete `harness/check.py p36` (**0 failures**; say up front which verdict you
expect and why); checksums against an independent `model.py`; two failing proof
mutants with `--multiple-errors` output; `measure.py --check-stale` clean.
**Paste actual output.** ⚠ Doc edits make a gate record STALE — re-run after.

## Constraints

No root; no `/tmp` (scratch `.temp/p36/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any existing pattern.
**If p36 seems to need a `harness/` change, STOP and report it** — there is
already a three-item `check.py` batch queued and a fourth would be folded into
it, not run separately. Verus only via `./verus_run.py`; `~/tools/verus/vstd/`
for vstd source. clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**;
⚠ **no self-matching `pgrep` wait-loops** — six of them cost a previous engineer
real time and the rule is `.memory/00-environment.md` constraint 2. Measurements
in the FOREGROUND. **You are the only agent running.**

Notes to `.temp/p36/NOTES.md` as you go, so a transient API death loses nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 155** — every agent that has contradicted the manager with a measurement
has been right, and the count is the evidence.

**What I am least sure of, by name: §0a — whether Verus at the pin can call a
bare `fn` pointer loaded from a static array, with a functional postcondition.**
The vstd support I found is for *generic `F: Fn` parameters*, which is a
different thing, and I did not compile anything. **If it cannot, p36 has no R5,
no `identity` pin, and is not buildable in this template — say so in §0a and
stop.**

**The named alternative, and pushing back is a legitimate outcome of this task.**
`p48` (initialisation / uninitialised-memory info leak) is the seventh axis, and
its triage is in `.memory/06-catalogue.md`. ⚠ **It is the MANAGER's own proposal
against the manager's own slate, PROTOCOL rule 3 is flagged against it in the
catalogue itself, and it is still unattacked** — so an argued preference from you
is worth more than agreement. Its own open item is whether MSan
(`-fsanitize=memory`, clang-only, needs every dependency instrumented) exists on
this box; **UNVERIFIED, and a compile probe settles it in a minute.** If §0a
kills p36, probe that and report both.
