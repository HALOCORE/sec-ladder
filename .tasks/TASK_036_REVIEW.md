# TASK_036_REVIEW — `m_clamp` either generalises p05's causal claim or is dead code inserted to move a number

**Role:** research reviewer. You do **not** fix; you report.
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_036.md` (the spec), then
**`patterns/p03-bounded-stack/NOTES.md` in full**, then its `spec.md`, `model.py`,
`inputs/gen.py`, `controls/gen_controls.py`, and `.memory/01-ladder.md` finding 6
(p05's causal claim, and the nonlinearity argument this pattern bears on).

p03 is the ninth pattern: gate `PASS` on a complete run, R5 **9/0 on the first
run**, R4 ≡ R5 `exact`, and **unreviewed** — per rule 9 none of its findings are
in `.memory/`. This review decides what goes in.

## The claim that matters most, and the engineer flagged it against itself

`m_clamp` is R3 plus a **dead** `if sp > STACK_CAP { return 0; }` — R5's invariant
handed to LLVM. Safe goes 17 → 13 Ir per executed pop, unsafe 14 → 13, and **the
gap goes to exactly zero on both sides**, zero fitted parameters.

If that holds, it **generalises p05's reinstated causal claim** — *"the `O(nrow)`
part of the in-contract safety tax is the price of the optimiser failing the lemma
the proof proves"* — from a *nonlinear* fact to a **linear** one, and p05's stated
excuse for why LLVM could not do it was precisely nonlinearity
(`.memory/01-ladder.md` finding 6). That would be one of this project's larger
results.

The engineer's own words: *"`m_clamp` is `idiom`-legal in letter but is dead code
inserted to move a number; I report it as a control and did not ship it. A
reviewer should attack that reading."* **Take the invitation.** Specifically:

- Is `m_clamp` measuring the *invariant*, or is it measuring **any** early return
  that narrows `sp`'s range? Build the controls that separate them — e.g. a clamp
  with a *different* bound, an `assume`-shaped hint, a `debug_assert!`, or the
  same test placed where it is *not* dead. If a semantically-irrelevant early
  return does the same thing, the claim is about range propagation and not about
  the proof's lemma.
- **Does the C rung admit the same edit?** If `m_clamp`'s trick works on `c-clang`
  too, then what it prices is an optimiser limitation shared by both languages,
  which is a *different* sentence from the one p05 published.
- Is `stack[sp & 63]` really removing only 1.00000 of the 3? That decomposition is
  load-bearing for "masking is not the same as the invariant".

## The other claims, in the order I would attack them

1. **The push/pop asymmetry** — `R3 − R4` is `0.00000` on push and `3.00000` per
   executed pop, in one function with one compile-time bound. Re-derive both from
   the listing. Is the discriminator really basic-block locality, or is it that
   the push guard's bound is a *constant* while the pop guard's is `0` compared
   against a value LLVM tracks differently?
2. **"Per executed pop, not per POP opcode"** — the regressors are visit-weighted
   from `model.py`, and the engineer notes that **band A alone and band B alone are
   each rank-deficient**, with band B returning garbage *at zero residual*. That is
   a fit whose design matters more than its residual. **Check the pooled design
   identifies what it claims**, and that the four regressors are not collinear in
   the shipped bands.
3. **R5 at 9/0 on the first run, with Z3 taking the invariant across the
   attacker-chosen branch with no lemma.** Recount the obligations per function.
   Recount the TCB (claimed 10 lines / 5 items). Does R5's exec code match R4's?
4. **The two defects the gate found on a trusted item** — a tautological
   `v@.len() == 64` on a `&[u64; 64]`. Confirm the repair is complete and that the
   remaining conjuncts are not *also* tautologies; a trusted accessor whose
   `requires` is vacuous is this project's worst failure mode.
5. **`r4_slicestack` could not be built** — claimed to fail *borrow*-checking, not
   just typechecking. If true it is the first time Rust's borrow checker, rather
   than vstd, bounds the unsafe class, and it belongs in `.memory/`. Verify it,
   and say whether a third spelling exists that the engineer did not try.
6. **The `Ir`-vs-`ns` reversal on `small`** — R3 faster than R4 while executing
   **+11.96%** more instructions. The engineer says this is 1.5–3× the
   identical-copy floor **on a box in its noisy regime** and asks for a quiet
   session. ⚠ **Check the current noise floor first with
   `common/layout/order.py`**; if the box is still noisy, say the direction is
   unresolved rather than forcing it either way. p03 is **protocol-sensitive**
   (it joins p05), so blocked scheduling alone moves `R3−R4` from −10.9% to −4.4%.

## Also worth ten minutes

`results/p03-bounded-stack.json`'s rates are **kernel-exclusive**, which is the
*opposite* of p11's answer — because p03's `[0u64; 64]` lowers to a `memset` whose
path length depends on the array's alignment, which moves with the probe file's
path length. Confirm that, because it makes the discriminator **"does the callee
have a data-dependent path length"** rather than p11's "does the kernel call out",
and both patterns' `NOTES.md` now assert different rules.

## Clean negatives are worth as much as findings

PROTOCOL rule 6. And **if `m_clamp` survives, say so plainly** — "handing the
optimiser the proof's own invariant, as dead code, closes the safe-vs-unsafe gap
to exactly zero" is a sentence this project has been circling since p05, and
hedging it would be its own failure.

## Constraints

No root; no `/tmp` — scratch `.temp/r36/`, and per constraint 6 delete your
binaries and blobs when you finish. **No `git add`/`git commit`** — read-only git.
Do not edit `pilot/`, `.memory/`, or anything under `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; confirm an exact PID's full command
line before any kill, **and no monitor wait-loops with self-matching `pgrep`
patterns** — three agents have now left loops that could not exit.
**Measurements in the FOREGROUND, interleaved by cell.** Run
`harness/measure.py --check-stale` before quoting any record.

Notes to `.temp/r36/NOTES.md` as you go.

Report in PROTOCOL's format, severity-ranked, file:line and a concrete failure
scenario per finding. Paste actual command output.

**Contradicting the manager with a measurement is the highest-value thing you can
do.** Forty-six agents have and all forty-six were right — p03's own engineer
refuted both premises I gave it, including my guess that the underflow would be a
wild address. I have no independent view of its numbers; I am relaying them.
