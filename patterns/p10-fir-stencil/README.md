# p10 — weighted FIR / sliding-window stencil

**The first kernel here with more than one indexed read per iteration at a fixed
offset from the cursor** — a `2r+1`-tap dot product, with the radius read out of
the input file at run time — and therefore the first that can ask whether safe
Rust's tax is proportional to the **number of indexing operations** or flat.

**The answer is neither.** At `-O3` the tap loop vectorises in *every* spelling,
including the naive indexed one, to the same seventeen-instruction SSE2 body
(same mnemonic sequence, different register allocation — not byte-identical).
The per-tap bounds checks survive only in the scalar epilogue that runs
`taps mod 8` times per output:

> **0.00 Ir on every tap the vectoriser reached, +3.00 Ir on every tap it did
> not**, plus a 41.00 Ir per-output constant whose largest identified component is a
> 24-instruction `cmp`/`cmov` chain computing how many taps may be vectorised
> safely.

The two per-iteration coefficients are loop-body counts off the shipped
listing with **zero alignment `nop`s inside either loop** (`controls/loops.py`);
the per-output ones are not, and `NOTES.md` 8c says so rather than naming them
after a mechanism.

That bounds `.memory/01-ladder.md` finding 3's domain by naming a *mechanism*
rather than a data size, and it reproduces p05's `O(nrow)` hoisted-guard result
on a kernel whose obligation is **linear** where p05's excuse was that its own
was nonlinear.

## The bug: one character, and exactly one byte

`.memory/06-catalogue.md`'s guess — *off-by-one at boundaries* — is **upheld**,
and it is not an omitted line:

```c
size_t last = 8 + taps + n - 1;   /* window offset of the LAST sample byte */
if (last >  len) return 0;        /* c/kernel.c            THE BUG */
if (last >= len) return 0;        /* c/kernel_hardened.c   correct  */
```

`last` is an **index**, so `last == len` is already one past the window. Every
other line of the two C cells is character for character identical.

**Three consequences, all measured:**

1. **Hardening is FREE.** `c-gcc-h − c-gcc` is `0.00` Ir/call — every fitted
   coefficient exactly zero over 33 blobs; the two kernels differ in a swapped
   `cmp` and an inverted `jcc`. On clang it is `+1.00` flat, and the extra
   instruction is a **`jmp`** from tail-merging the `return 0`, not a check.
   Every earlier R1 in this project omits a *line*, so its hardening adds
   instructions; p10's already performs the comparison.
2. **The harm is exactly one byte.** `adversarial-farover.bin` declares `n`
   far beyond the window and **R1 and R1h reject it alike** — an off-by-one
   buys one byte and nothing more.
3. **Whether that byte is observable is a property of the ALLOCATION.**
   `adversarial-fencepost.bin` puts the window at the end of the payload and
   ASan reports `heap-buffer-overflow ... READ of size 1`;
   `adversarial-fenceslack.bin` is the **same window** with three trailing
   payload bytes and the identical off-by-one is ASan-clean, UBSan-clean,
   exit 0 and wrong. p02's result on the read side, at the smallest possible
   magnitude.

## Safe Rust beats unsafe Rust here, in `Ir` and in wall clock

`R3 − R4 = −3 − 5.00·nout + 0.00·scaltap − 1.00·novecout`: **−323.00 Ir/call on
`small`, −603.00 on `large`**, and the `scaltap` coefficient is *exactly zero* —
`slice::windows(taps)` is one range check however many taps it covers, and its
tap loop contributes **zero** panic landing pads where R2's contributes two.
A 24-layout population puts `safe_tuned` at 207.55–215.39 ns/call against
`unsafe`'s 229.38–233.59 — **disjoint bands**, −8.4% at the medians.

⚠ This is a **fixed-R4** statement (`.memory/01-ladder.md` finding 14): one
cheaper R4 lever was built (`u_win`, −194/−362) and **its Verus twin does not
verify**, so it is a control and not a rung. The R4 side is reported
**degenerate as far as this task searched**, with the exact error text in
`NOTES.md` 8e.

## Firsts

- **`slice::windows()` — the first use in this project.**
  `grep -rn "windows(" patterns/*/*.rs` returned nothing before p10. It takes a
  **runtime** size (verified, not assumed) and costs **no `div`**, where
  `chunks_exact` with a runtime chunk size does.
- **`global size_of usize == 8;`** — the first pattern that has to say this.
  Verus treats `usize` as architecture-independent, so `2 * r + 1` on a `usize`
  built from four header bytes is `possible arithmetic underflow/overflow`
  without it. p07 dodged the same obligation by computing in `u64`; p10 cannot,
  because its contract pins the spelling. `NOTES.md` 6b.
- **The first hardening in this project that costs nothing**, and for a
  structural reason rather than a libc one.
- **The first byte-identical R4/R5 pair whose whole-program marginals differ**
  (by 1.00 Ir/call, in `main`, not in the kernel). Quote the kernel-exclusive
  column for an identity claim. `NOTES.md` 7c.

## The registered predictions, scored

`.tasks/TASK_057.md` §2 was committed before any measurement. **P1 false, P2
true with the opposite sign, P3 false** — `NOTES.md` 13.

And a genuinely out-of-sample test: 40 predictions for sweep band `e`, hashed
(`da05048c…`) before band `e` was measured. **40/40 hold, worst |error| 0.0200,
and all 20 difference predictions exact to 0.0000.** `NOTES.md` 8f states
precisely what that test can and cannot fail on.

## Files

```
spec.md          the contract, incl. the hashed `slb-contract` block
NOTES.md         the evidence
model.py         the independent reference model (two implementations)
inputs/gen.py    the generator; deterministic, verified by regenerating twice
c/               R1 (kernel.c), R1h (kernel_hardened.c), the shared driver
safe_naive.rs    R2 -- index every tap
safe_tuned.rs    R3 -- `windows(taps)` + `iter().zip()`
unsafe.rs        R4 -- `get_unchecked`
verus.rs         R5 -- R4 plus the proof; 10 verified, 0 errors
controls/        mkcontract.py, gen_controls.py, sweep_ir.py, fit.py,
                 predict.py, clayout.py
```

Reproduce: `harness/check.py p10`, then `harness/measure.py p10`, then
`harness/report.py p10-fir-stencil`.
