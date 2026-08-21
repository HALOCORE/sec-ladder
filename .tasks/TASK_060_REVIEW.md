# TASK_060_REVIEW — p27, where the minimal TCB and the identity pin are in tension

**Role:** research reviewer. **Adversarial by design.** You do **not** fix; you
report. A review that says "looks good" without having tried to break something
is a failed review.

**Read first:** `.tasks/PROTOCOL.md` (roles, reviewer checklist, severity), then
`.tasks/TASK_060.md` (the build spec — **large parts of it were refuted, see
below**), then **`patterns/p27-handle-table/NOTES.md` in full**, then
`.memory/04-verus.md` (the `raw_ptr` section, the TCB decision, the twin regime),
`.memory/03-measurement.md` (the tcache section, the two `Ir` conventions, the
inline-mode rule) and `.memory/02-bench-rules.md`.

p27 is **gate-green** (`PASS`, 0 failures, 36 records 0 STALE, R5 **15/0 first
run**, `R4 ≡ R5` `exact` at O3 / `norel` at O0, two proof mutants failing).
**PROTOCOL rule 9 holds everything out of `.memory/` until you land**; three
candidates are named at the end of the engineer's report and you are gatekeeping
them.

⚠ **PROTOCOL rule 3, and it cuts unusually deep here.** The formulation this task
specced was **the manager's, inherited from TASK_055 §2.8, and the engineer
refuted it with a measurement** — safe Rust is *not* forced onto
`(slot, generation)`, because the handle comes out of a file and is an integer in
every rung. **So do not spend the review re-checking my formulation; it is
already dead.** What has no adversary is **the replacement framing, which is the
engineer's own**, and the two structural decisions below.

## The three attacks I most want run

**A1 — the twin regime may be circular here, and that would be a blocker.**
`vstd::raw_ptr::allocate`/`deallocate` carry no `#[inline]`, so an R5 calling
them emits a GOT-indirect cross-crate call R4 cannot produce, and the pair
measures **`differ` at both opt levels**. The engineer's fix: ship local
`#[inline(always)]` copies as trusted items, **whose verified twins are vstd's
own API**.

> **Does that twin check anything?** The twin exists to test that a trusted
> `requires` is **strong enough to license the operation**
> (`.memory/04-verus.md`, TASK_009_REVIEW). If the twin's body *is* the vstd
> function the trusted item is a copy of, the twin may be **re-stating the axiom
> rather than re-deriving it** — which is precisely what `_TWIN_BANNED` and the
> "its body calls the trusted item" check exist to prevent, one level up.
> **Weaken `rec_alloc`'s or `rec_free`'s `requires` and see whether the twin
> catches it.** If it does not, p27's two extra trusted items are unchecked and
> that is a blocker. If it does, say so — it is a strong clean negative and it
> licenses the whole shape.

**A2 — is publishing TCB 7 to buy `identity: exact` the right trade, or is it
gaming in the other direction?** `r5_vstdpure` verifies **15/0 with
`tcb_items = 5`** and its pair is `differ`, at +130.11/+416.00 `Ir`/call. p27
ships **7**.

> This project publishes `tcb_items` as a headline metric and has spent two tasks
> on whether it is gameable. **p27 chose the LARGER TCB.** Argue it both ways
> with the numbers: is `identity: exact` worth two trusted items, given that the
> identity pin's whole purpose is to prove R5's ghost code erases? ⚠ Note the
> engineer disclosed this rather than shipping only the flattering half — **that
> disclosure is what makes the check possible**, so this is not an accusation.
> **And check the `+130.11` is in the convention it claims.**

**A3 — the headline framing, which is new and unattacked.** *"The free and the
invalidation are one operation in safe Rust and two in C, and the bug is the
third — the asking — going missing."* Supporting claim: `Option<Box<u8>>` is
**niche-optimised to the hardened-C representation**.

> **Verify the niche optimisation on the shipped binary**, not from the language
> reference — `size_of::<Option<Box<u8>>>() == size_of::<*mut u8>()` is the
> claim, and what matters is what the *shipped* R2/R3 actually store and test.
> Then ask the mechanism question (PROTOCOL rule 11): if safe Rust's invalidation
> is free because it is the same store, **where does `R3 − R4 = +223.26` come
> from?** The engineer decomposes it as **+102.84 kernel, +120.42 drop glue,
> +0.0000 allocator**, with `malloc` and `free` equal *to the last digit* between
> the rungs. **Check that decomposition** — it is the most load-bearing number in
> the pattern, and "54% of the safety tax is an epilogue asymmetry" is a claim
> this project has never made before.

## Also in scope

- **The one number the engineer calls the most interesting and could not
  explain**: `c-clang`/`c-clang-h` were **not swept**, so a **4×/24× compiler
  disagreement on one conjunct** (`+4.95`/`+3.76` against gcc's
  `+19.83`/`+91.01`) has no band behind it. **Sweep the two clang cells** if it
  is cheap, or say what it would take.
- **`adversarial-noreuse`'s two C cells are deliberately non-reproducible across
  runs**, so p27's gate JSON churns on every run. **Is that acceptable?** Check
  it does not interact badly with `--check-stale`, with diffing gate runs, or
  with the `source_sha256` machinery. If it does, that is a real defect in a
  pattern that is otherwise clean.
- **The two contract edits** (`b1f2dbb3…` → `a0e83e2f…`), disclosed with reasons:
  two `rec_alloc` `ensures` not load-bearing, and `rec_free`'s `Tracked(pt)`
  pattern making six `requires` conjuncts unjudgeable. **Run the direction test
  in writing.** The engineer says both tighten the gate and no
  `required`/`forbidden` entry moved — **verify the second half independently**,
  since the hash recorded before the build is what makes that checkable.
- **The bug must be temporal, not logical.** Confirm `free` is a real `free` in
  every C cell and that a stale read is genuinely out of a *dead* allocation —
  if it lands inside a live one, p27 is p17's class and the whole point is gone.
  ASan is claimed to fire on all 3 adversarial rows and be clean on all 4 benign.
- **`R5 − R4 = 0.0000` kernel-exclusive** on the first kernel here that
  allocates — finding 1 reconfirmed. Re-measure one cell.
- **The R4 side is "degenerate as far as this task searched"** and R2 was not
  searched at all. p10's blocker was exactly this sentence turning out to be
  false after one more invariant clause. **Try once.**
- **The level fit is not a law** and the domain is admitted open (a tcache
  hit/miss column cuts the residual 17% and does not close it). Honest, or is
  there a design nobody tried?

## Clean negatives are wanted

PROTOCOL rule 6. p06's review returned fourteen, p14's seventeen, p10's
twenty-one. **List every attack you ran with its outcome.**

## Constraints

No root; no `/tmp` (scratch `.temp/p27rev/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, `common/`, or **any** file under
`patterns/` — **you report, you do not fix.** Probes and logs under
`.temp/p27rev/`, plus your report file. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. Use `~/tools/verus/vstd/` for vstd source,
**not** `../LearnVeri/_VERUS_DOC_/vstd/`. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**. Measurements in the FOREGROUND, per-PID
scratch paths. **You may re-run `harness/check.py p27`** — not any other pattern.
**You are the only agent running.**

**Write `.tasks/TASK_060_REVIEW_REPORT.md` before you finish**, then return the
same content in the report format. Rank findings `blocker` · `major` · `minor`,
with file:line and a concrete failure scenario. **Do not pad.**

**If a premise here is wrong, say so with the measurement.** The running count is
**111**, and p27's engineer contributed **seven** of those in one task — including
catching that my *"the proof half is already settled, do not re-derive it"* was
unusable, because the ghost loop the previous review proved splits one allocation
`n` ways, which makes "free" a freelist push: **the exact thing that same
review's own blocker forbids.** I passed it along without noticing the two halves
contradicted each other. **Assume this task file contains one more of those.**
