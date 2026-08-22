# RECAP — state of the research programme

## START HERE — the next action, in one screen

**You are the research manager.** Read `.tasks/PROTOCOL.md` next (it carries the
manager's own rules), then `.memory/` 00–06 as you need them. Everything below
this box is reference; this box is what to *do*.

| | |
|---|---|
| **Patterns** | **20 exist, all green. 19 reviewed; p38 is IN REVIEW. 0 STALE.** Count both ends rather than trusting either: `ls -d patterns/p*/ | wc -l` and `grep -c '^| p[0-9]' .memory/06-catalogue.md` (**the denominator moved from 47 to 48 at TASK_066**, which is why it is no longer written here — a spelled-out numerator sat on this line reading *"thirteen"* against a sixteen-row table). |
| **Do this next** | **Land p38's review.** `.tasks/TASK_066_REVIEW.md` was dispatched; when its report arrives, write **`TASK_067`** (p38 corrections) and only then the `.memory/` findings — **rule 9**. ⚠ **p38's engineer refuted SIX manager prescriptions**, so the review was pointed at the *replacement* claims. The two calls the manager is least sure of are named in the review task: **is p38's C rung idiomatic** (the whole security claim rests on it) and **is the first-ever additivity failure real or a band that never varied `nw`** — those are very different findings and the write-up implies the larger one. |
| **After that** | `.memory/06-catalogue.md`'s section **"The waves order by FAMILY…"** — the missing axes, the order (**lifetime ✅ → p47 ✅ → p38 ✅ → p22 → p36**), and a **feasibility triage** naming what would kill each. ⚠ **Three things moved at TASK_066, all PROVISIONAL and all needing a different agent to attack them** (rule 3): **p22's harness question is ANSWERED** — a hang is already in the gate's vocabulary and only `RUN_TIMEOUT = 900` kills it, so it needs a `check.py` change and is the **batching partner** the owed `forbidden_hits` fix was waiting for; **p36's row cited the wrong function and overstates its risk** (the bar is "a sanitizer fires deterministically", not "the harm is identical"); and there is a **SEVENTH axis, `p48` (initialisation), which was not in the catalogue at all** — the pinned vstd already forbids the bug (`ptr_ref`/`ptr_mut_read` both `requires perm.is_init()`). **Push back with the pattern you would rather build.** |
| **Three rules for writing that task** | ⚠ **Settle the bug class as the FIRST deliverable** — overturned on four patterns, upheld on two. ⚠ **A law owes its DOMAIN** (usually *missing columns*, not a caveat), and the only out-of-sample test here that has ever been able to fail is **additivity extrapolation**. ⚠ **Name the INLINE MODE at every figure** — p10 fitted both and the regressors *swapped*. All three in `.memory/03-measurement.md`. |
| **The trap that keeps firing** | **A headline can be wrong in the FLATTERING direction and pass a green gate.** p10 published *"safe Rust cheaper than unsafe"*: 60% was an **unsearched R4 side**, the rest **index-expression bookkeeping C pays more of than either Rust rung**. **p27 repeated it one pattern later** — a dead store in R4 that R3 did not have. **p47 is the first pattern to search the R4 side properly** (six levers, each measured *and* run through Verus). ⚠ **Before publishing any rung comparison, ask what the OTHER rung's spelling is worth.** |
| **The loop** | build → review once → land corrections. **Three tasks per pattern is the measured cost.** Per `PROTOCOL.md` rule 9, write `.memory/` **only after** the review. |
| **Git** | Commit at task boundaries; subagents never commit. ⚠ **There is a GitHub remote** (`origin`, `HALOCORE/sec-ladder`). **Do not push unless the user asks.** |
| **Before quoting any number** | `harness/measure.py --check-stale` (exit 1 on STALE). |

**Four settled answers that cost real time to get. Do not re-litigate them; each
is written up in `.memory/`.**

- **The R4/R5 pair is not a null control** — the `verus` kernel sits at a fixed
  offset from the `unsafe` one, and **that offset is a source-path-length
  artefact** (it moves if you clone elsewhere), so the pair is a **biased draw of
  size one**. *The floor is the layout population.* p06's own floor is **±4.6%**.
- **The TCB column is not gameable — retrospectively.** The census found two
  exposed items; **both have since been relocated, so the measured exposure is
  now `0`.** ⚠ Do not quote *"3.4% across the 16 patterns"* — that was this
  line, and it is wrong twice: the census ran over **14** patterns, and its
  numerator is closed (`.memory/04-verus.md`, which ships the recount).
  ⚠ **Prospectively the column IS gameable**: a `raw_ptr` pattern needs
  zero project-local trusted items. Ship **one number plus the U-license / V-gap
  / infra classification**; the two-number proposal was refuted by census.
- **`-C debug-assertions=on` also enables `assert_unsafe_precondition!` inside
  `get_unchecked`**, and 15 of 16 R4s rest on it. *"R4's advantage over R2
  disappears"* was **refuted** (true on p18/p01, false on p16). What holds on
  3 of 3: **at `-O3` with debug-assertions on, R4 becomes dearer than R3.**
- **`build.py` is hashed into the MEASUREMENT records, not just the gate
  records.** So "one harness edit, one 30-minute gate re-run" is true of
  `check.py` and **false of `build.py`** — that costs a full re-measure and
  churns published timing prose. It is why `O3d` was built, measured inert, and
  **reverted**; land it bundled with a pattern being re-measured anyway.

**The three things most likely to waste your time**, all learned the hard way:

1. **Ask to be corrected, not obeyed.** **Every agent that has contradicted the
   manager with a measurement has been right** — p13's engineer did it six times
   in one task, then six more while landing the review of it. Put your least
   certain call in every task file *by name* and ask for the measurement. The
   single highest-yield sentence in this project's history is some version of
   "I think X; prove me wrong." (Running count: the closing paragraph of the
   newest `.tasks/TASK_NNN*.md`, and nowhere else — two copies went stale here.)
2. **A green gate is evidence about the gate.** Reviews have found real defects
   past a fully green run repeatedly — including in `.memory/` text written one
   task earlier, and in the manager's own tooling.
3. **Never write a finding into `.memory/` before its review lands** (rule 9).
   It is the only reason several overclaims were caught in RECAP rather than
   asserted as authoritative.

---

For a manager picking this up cold. Read this, then `.tasks/PROTOCOL.md` (which
now carries **the manager's own rules**), then `.memory/` 00–06.

**The `.memory/` files are authoritative and supersede any task report they
contradict** — several reports contain claims that were later refuted, and the
refutations live in `.memory/`.

## What this is

A micro-benchmark for the performance ↔ memory-safety tension. Each common C
pattern is built at five rungs — C, safe Rust (naive), safe Rust (tuned), unsafe
Rust, unsafe Rust + Verus proof — plus a sixth **R1h** hardened-C cell, across two
optimisation levels and two inline modes, and compared on assembly, executed
instructions, timing, proof burden and trusted-base size.

**48** patterns are catalogued in `.memory/06-catalogue.md` — 47 until TASK_066
added `p48` (the initialisation axis, which was missing entirely). **The ones that exist
are the table below — all green, all reviewed.** ⚠ A spelled-out count used to
sit on this line and it read *"thirteen"* against a sixteen-row table; count the
rows, or run `ls -d patterns/p*/ | wc -l`.

| | pattern | what it is here for |
|---|---|---|
| p01 | array reduce | calibration; the template every later pattern clones |
| p02 | length-prefixed copy | **the security result** — idiomatic C silent in 7 of 8 builds |
| p05 | 2-D index flatten | the first vectorised kernel; the proof→performance link |
| p08 | overlapping move | the bug safe Rust **cannot express** |
| p16 | TLV walker | the first data-dependent bound |
| p17 | HTTP suffix range | **the limit** — provably memory-safe and still leaking |
| p07 | binary search | the first kernel where R3's tax **never amortises** |
| p11 | NUL scan | library vs spelling vs safety, separated three ways |
| p03 | bounded stack | the proof's own invariant, handed to LLVM, closes the gap |
| p09 | bitset | **one character** between a bug everything catches and one nothing does |
| p12 | `strcat` fixed | the first **write**; a per-iteration check costs the bulk lowering |
| p04 | ring buffer | known **bits** survive a loop-carried phi where a range does not — `next_pow2(CAP) ≤ ARR_LEN` |
| p13 | `strncpy` truncation | a bound the optimiser can **see** outweighs the check that supplies it — and the contract pinned one side of the comparison |
| p06 | in-place rotate | **the `Ir` column is sign-wrong** — clang's hardened rung executes *fewer* instructions and runs *slower* |
| p14 | field split | **an exact law, fitted where the guard never fires** — and why "hardening is cheaper than the bug" is not publishable |
| p18 | LEB128 varint | **UB that is not memory-unsafety** — four catchers, all outside the measured matrix |
| p10 | weighted FIR stencil | **a headline wrong in the flattering direction** — safe beats unsafe, and none of it is safety |
| p27 | handle table | **the first TEMPORAL bug** — and the lifetime guarantee costs zero; safe Rust pays *less* spatial tax than unsafe |
| p47 | constant-time compare | **the proof certifies a LEAKING kernel** — identical contract, and the obligation count does not move |
| p38 | strict aliasing / type punning | ⚠ **IN REVIEW, unreviewed — do not quote from here yet.** **A MISCOMPILE is the harm**: gcc reads a record length before the clamp that narrows it and never reloads, so `-O3` overflows where `-O0` is correct. Also the project's **first failed additivity extrapolation** |

**If you read only one thing after this file**, read `.tasks/TASK_026.md` §0 — the
distilled rules from the thirteen-task spelling arc. Every pattern built after it
needed only prose corrections, and every pattern built before it needed
re-measurement.

## The findings so far — this is the actual output

**TWO numbering schemes — here is the map, so you never have to guess.** This
file's list is **RECAP's own digest**; `.memory/01-ladder.md` has a *different*
list, **one entry per pattern**, and **that one is authoritative**. They were
confused repeatedly before this table existed.

⚠ **The ranges that used to be written here were wrong** — this file claimed
`1–24` for itself and `1–12` for the ladder when the true counts were 25 and 14,
and the ladder's own warning claimed the mirror image. **Both guards against
citation drift had drifted.** Print the counts rather than trusting a constant;
the commands are in `.memory/01-ladder.md`'s numbering warning.

| pattern | `.memory/01-ladder.md` | RECAP (this file) |
|---|---|---|
| p16 | **4** | 9 |
| p17 | **5** | 10 |
| p05 | **6** | 12 |
| p08 | **7** | 13 |
| p07 | **8** | 15 |
| p11 | **9** | 17 |
| p03 | **10** | 18 |
| p09 | **11** | 19 |
| p12 | **12** | 21 |
| p04 | **13** | 23 |
| p13 | **14** | 25 |
| p06 | **15** | 26 |
| p14 | **16** | 27 |
| p18 | **17** | 28 |
| p10 | **18** | 29 |
| p27 | **19** | 30 |
| p47 | **20** | 31 |
| p01, p02 | findings 1–3 | 1–8 |

Cross-cutting entries exist only here: **14** (every rung is a spelling), **16**
(code layout / the 32-byte fetch grid), **20** and **24** (measurement and
infrastructure defects), **22** (decode panic pads).

⚠ **AND THERE IS NOW A LIVE COLLISION: "finding 14".** In
`.memory/01-ladder.md` it is **p13**; in this file it is the cross-cutting
*"every rung is a spelling"* entry. Both are cited often and they are
**unrelated**. The same trap exists at "13" (ladder = p04, here = p08).

**When you write a task file, name the pattern — *"p05's causal claim"* — never
the number.** Two task files have already sent an agent to the wrong finding.

1. **A Verus proof costs exactly zero instructions.** The proven binary is
   byte-identical to the unproven one; ghost code fully erases. Verified on raw
   machine code on all three patterns, at both opt levels.
2. **A proof alone buys nothing.** Proving safe Rust panic-free leaves every bounds
   check in place — rustc never learns what the prover knew. The payoff arrives
   only when the proof *licenses unsafe code*: R5 is R4's machine code with the
   obligations discharged.
3. **Safety is cheap — and finding 9 says it stays cheap even when the optimiser
   *cannot* see the loop.** Tuned safe Rust is **+4…+5 instructions per call on
   p01 and +10 on p02** versus unsafe — flat in the size of the data, not a
   percentage. ⚠ **This line said `+8…+10` for both until TASK_058**; p01's
   gate marginals are `safe_tuned 918.3 / 7205.3` against `unsafe 914.3 /
   7200.3`, and `p01/NOTES.md:262` and `.memory/01-ladder.md:500` both say +4/+5.
   Only p02's half was ever `+10`.
   Hardened C's check is +5 (gcc) / +12 (clang), also flat. **Always quote R3;
   R2 alone overstates safe Rust by 3.7× on p01 and by ~75× on p16.**
4. **The security result (p02), the strongest thing here.** On a one-byte
   overflow, idiomatic C prints a plausible answer and exits 0 in **seven of eight
   builds** — silent heap corruption absorbed by glibc's chunk rounding. The eighth
   aborts only because Ubuntu defaults `_FORTIFY_SOURCE 3`. Every Rust and
   hardened-C cell handles it. Control: delete the check from safe Rust and it
   panics rather than corrupting, so "Rust makes the check non-optional" is a
   measurement.
5. **Static instruction counts are not a cost model.** The ranking inverted twice.
   gcc emits fewer instructions than clang and executes 43% more.
6. **`Ir` and wall clock can disagree in direction** — gcc 10% fewer instructions,
   23% slower (p02).
7. **The same-backend comparison, which is the one that counts.** clang 22.1.6 is
   bit-for-bit rustc 1.97.1's LLVM. On p01 `large`, C-clang and unsafe Rust execute
   **exactly 143,740,000** kernel instructions. Static gap +2, an
   induction-variable choice, not an ABI cost. **Every C-vs-Rust claim needs the
   clang column**; gcc stays as the "what a distro ships" baseline.
8. **p02's residue curve predicts.** R2−R4 is a sawtooth, amplitude 179 Ir,
   resetting at `len ≡ 1 (mod 16)`, on a 0.21 Ir/byte linear term — re-derived at
   seven unsampled lengths and 8× the scale (178.9, 0.2125). The only model here
   tested by prediction rather than re-measurement.
9. **p16 — safety is cheap *even where it should not be*, and the one place it
   isn't, the check is only half the reason.** A TLV walker with a
   data-dependent bound, nothing hoistable, no bulk idiom to lose: the case p01
   said not to generalise to. **R3 idiomatic safe Rust is 5.7500 Ir/folded byte —
   R4's rate exactly, zero per byte**, its whole cost O(1) per call and shrinking
   with size. **The null is the result and it is now SWEPT** (TASK_025_REVIEW):
   fold both rungs the same way and safe−unsafe is a *single integer per call* at
   every length — over **127 consecutive `vlen`**, slope of the difference
   `0.0000000` Ir/byte, max residual 0.00, at six spellings. The mechanism is why
   it cannot be otherwise: the reslice (R3) and the `get_unchecked` (R4) both sit
   **outside** the fold loop, so the chunk body is mnemonic-identical at
   K = 4, 8, 16, 32 and 64. **p16's per-byte safety tax is 0.00000, and that is
   the sentence to quote.**
   ⚠ **What must NOT be quoted is a bare rate, or a difference of rates across
   unmatched folds.** In contract, one exact-string substitution apart, p16's rate
   ranges **5.04688 … 6.62500** (5.7500 shipped; 6.50000 and 6.62500 for
   `chunks_exact(4)` / `(8)`; a seventh spelling at 5.37500) — a 31% spread — and
   the measured rates carry ±0.01 Ir/byte from the driver's `println` term, which
   does not cancel within a binary and is 20× the gap between two published rates.
   The cross-spelling figure that reached four files as a headline was
   ~~−0.5625~~ and is **−0.65625**: the published value was the K=16 number left
   pointing at the K=32 rung when the sentence was re-aimed. It is a codegen
   difference between two folds and was never a safety cost. "O(1) per call" is
   separately corrected to `7 + 5·nrec` / `7 + 7·nrec` (TASK_015_REVIEW). See
   `patterns/p16-tlv-walk/NOTES.md` §10a.2 and `.tasks/TASK_025_REVIEW_REPORT.md`.
   Only the *naive indexed spelling* is O(n): +4.25 Ir/byte, +69/+72%.
   Of that 4.25, a rolled-vs-rolled control (`-unroll-count=1`, a bit-for-bit
   no-op on R2) shows **exactly 2.00 is the check and 2.25 is the 4× unroll it
   forecloses**, zero residual. And it costs **+0.27% wall clock** — the fold is
   latency-bound at 3.03 cycles/byte, identical on L1- and L3-resident inputs, so
   memory bandwidth is ruled out rather than merely unconsidered.
   **Fourth pattern in a row where R3 is the honest number.**

10. **p17 — the limit, and the most important artefact here.** A suffix-range
   parser (CVE-2017-7529). One missing `start >= 0`; the served range is the last
   `s` bytes, so one attacker `u16` picks the harm. For `content_len < s <= len`
   the bad read is **inside the allocation** — ASan clean, exit 0, and **safe Rust
   with the check deleted prints C's value bit-for-bit**. Only for `s > len` does
   it leave the allocation and Rust panic.
   Then the artefact. Guard the **slice**-relative index —
   `start >= -((off + body_start) as i64)`, which is exactly what a bounds check
   buys, no more — and Verus gives **9 verified, 1 error, the single error being
   the *functional* invariant; every access obligation discharges** (10/0 with the
   functional spec stripped). It reads a **neighbouring window's** bytes: output
   tracks the victim's secret, no panic, no `unsafe`. **A provably memory-safe
   program that leaks.** Memory safety and correctness are different properties
   and this is the measurement.
   **Two corrections are baked in above, both from TASK_011_REVIEW** — the
   shipped `adversarial-leak` row discloses only the *attacker's own* request
   table, so it shows memory-safe-but-wrong, not disclosure; and the delivered
   `start >= -(body_start as i64)` guard is strictly *stronger* than a bounds
   check, which is what made its leak vacuous. The distinction is one token and
   it is the whole finding: write "what a bounds check buys" **slice**-relative.
11. **4.25 Ir/element is a property of rustc, not of a pattern — and so is its
   2.00 + 2.25 split.** p17 reproduced p16's swept constant exactly (10.0000 /
   5.7500 once the driver's `println!` digit-count term is differenced out); p05
   reproduced it a third time on a non-Horner fold, *and* reproduced the
   decomposition — 2.00 check + 2.25 foreclosed unroll — from its own no-op
   control. ~~R3 is free for five patterns and then stops.~~ **The second
   sentence is retracted** — see finding 13. **No pattern has yet shown safe
   Rust paying an unavoidable per-element price.**
12. **p05 — safety on a vectorised loop, and the first causal link from proof to
   performance.** Per element inside the vector body the check is free (1.375000,
   five rungs identical). But it is hoisted into a 22-instruction per-row
   trip-count computation and survives in the scalar epilogue, so the cost is
   `O(nrow)`, not zero — and **wider lanes make it worse**: at AVX2 the gap is
   4.58× against SSE2's 1.42×, with safe Rust absolutely slower. `ncol ≡ 0 mod 8`
   pays a *full extra vector iteration*, so every power-of-two dimension is the
   worst case.
   The cause: the kernel already checks `nrow*ncol <= avail`, so R2's panic is
   dead on every run — but LLVM cannot eliminate it, because
   `nrow*ncol <= avail ⟹ i*ncol+j < avail` is **nonlinear**, which is exactly the
   obligation R5 discharges with `lemma_mul_inequality`. Linearising the guard in
   an isolated compilation deletes the whole per-row apparatus, so nonlinearity
   **is** the blocker for this kernel — confirmed at TASK_014_REVIEW against the
   manager's suspicion that p08 refuted it. But it is **not a general law** (p08
   keeps a dead *linear* check for a *relational* reason), and
   ~~"the safety cost is the price of the optimiser failing the lemma the proof
   proves"~~ is **retracted as written**: what those instructions price is two
   *spellings*, not safety. See finding 13.

   **REINSTATED at TASK_021_REVIEW, restricted to the row-scaled term**, in
   exactly these words: *"On p05, the `O(nrow)` part of the in-contract safety
   tax is the price of the optimiser failing the lemma the proof proves."* The
   in-contract respelling removes exactly one instruction per row — the `add`
   that makes the row base buffer-absolute — and the five that survive are the
   reslice's bounds check, whose deletion needs `(i+1)·ncol <= nrow·ncol`, the
   nonlinear fact `lemma_mul_inequality` discharges. Not true of the constants,
   not a statement about safety in general.
   **But p05 has no minimum, and neither does any pattern.** Three were
   published and all three refuted, each by the first lever the next agent
   pulled: `5·nrow + 6` → `5·nrow + 11` (respell the header) → `5·nrow + 13`
   (delete a redundant zero-check). Each had been reached by several independent
   machine-code bodies, so **"reached by many spellings" is not evidence of a
   floor**. And the quantity is unsound, not just unlucky: **`min(R3) − min(R4)`
   is the difference of two upper bounds and bounds nothing in either
   direction** — measured, the same edit is −2 on R4 and +1 on R3, and
   `5·nrow + 13` *exceeds* the published `6·nrow + 9` for `nrow < 4`.
   ~~Publish the in-contract **pair interval** (`36…134 / 128…410`, with the
   published 123/399 inside it)~~ and, if one number is wanted, the fixed-R4
   bound. ~~**An admissible pair has a tax of exactly 0.00**, so p05 does not
   support "safety costs something here" over free pairings.~~
   **Both struck at TASK_028** — the interval's endpoints and the `0.00`
   pairing are `r4_dataslice` and `c4_hu16_nz`, neither of which is a rung.
   Publish the **fixed-R4 bound** and the **R3-side span** (`5·nrow + 6` …
   `6·nrow + 13` = 101…127 / 331…403); see item 1 of "Priority" below, and note
   that this paragraph is the site that survived the first correction sweep.

13. **p08, and the retraction it forced — safe Rust beat unsafe Rust on p05.**
   p08's own result is structural: overlapping `memcpy` is UB that safe Rust
   **cannot express** (borrow checker, compile time, no runtime check and so
   nothing to measure), `unsafe` re-opens it via `copy_nonoverlapping`, and
   **R5 does not close it** — substituting `copy_nonoverlapping` into the trusted
   body verifies 11/0 and 15/0 under the twin, invisible to Verus, the twin and
   the contract pins; only Miri and the O3 identity pin catch it. On this libc
   the UB **executes and is unobservable**: glibc 2.39 `memcpy` *is* `memmove`,
   so R1 ≡ R1h at **0.00 Ir/call** — a *libc* property, never to be quoted as
   "memmove is free". ASan sees the overlap, but **`_FORTIFY_SOURCE` blinds it**
   under clang as well as gcc, because the check lives in the `memcpy`
   interceptor and not in `__memcpy_chk`.
   Then the blocker, which is about **p05**: `data.chunks_exact(ncol)` — one
   idiomatic safe expression, zero `unsafe`, no proof — is **`nrow − 7`
   instructions per call cheaper than the unsafe rung**, exactly, on every input,
   with identical output on all 150 committed p05 inputs. p05's shipped R3
   reslices by hand and pays `6·nrow + 9`. **Three patterns have now priced a
   spelling as safety's cost** (p02, p16, p05).

14. **Every rung is a spelling, the gap does not converge, and "safe beats
   unsafe" was never available as a language fact.** (TASK_015 +
   TASK_015_REVIEW. The programme's central methodological result, and the one
   that shapes the writeup.)
   The audit found **all three shipped R3s beaten**, each beater also cheaper
   than **its own R4**. The control that answered it — apply the same
   consumed-slice idiom to the *unsafe* rung — put unsafe back on top at
   **+11.00 Ir/call flat**. Then the review ran **one more round on each side**:
   replace the unsafe loop counter with the canonical C test `while rp < end`
   and it becomes **`nrow + 9`** — swept exactly over all 144 blobs, zero
   residual, with a second unrelated unsafe spelling landing on the identical
   figure. **`O(1)` became `O(nrow)` and the sign of the conclusion flipped on
   the first thing a reader would try. The gap does not converge.**
   ~~And it never could, for a reason available without measuring: R4 is defined
   by *permission*, not obligation, so every safe program is an admissible R4 and
   `inf(R4) <= inf(R3)` **by construction**.~~
   ⚠ **THAT ARGUMENT IS REFUTED — TASK_025_REVIEW, and it is the most consequential
   correction in this file.** The "reason available without measuring" was wrong
   *because* nobody measured it. **All six patterns pin
   `identity: unsafe ≡ verus, O3 exact`**, so an R4 is not a program that *may*
   use `unsafe` — it is a program that **must have a byte-identical R5 twin that
   Verus verifies**. R4 is bounded by what vstd can express; R3 is bounded by
   nothing. The classes are **incomparable, not nested**, and the inclusion runs
   the opposite way from the one that was published.
   Measured instance: p16's `chunks_exact(32)` fold is admissible as R3 at **zero
   TCB** and inadmissible as R4 — `chunks_exact`, `ChunksExact`, `by_ref`,
   `TryFromSliceError` and `get_unchecked` are each unsupported at the pin, so
   shipping it needs **five** new trusted items on a pattern whose whole claim
   rests on *one*. So "safe Rust beats unsafe Rust" is **not** disposed of by the
   definitions, and on p16 it has a mechanism instead: **the safe class can reach
   spellings the unsafe class cannot, because the unsafe class is chained to the
   prover.** Whether the infimum gap is positive is open on every pattern.
   What *is* still available a priori is nothing at all — which is the lesson.
   **Both spellings that drove this were out of contract.** p05's `spec.md`
   forbids `chunks_exact` and the running row pointer by name — either deletes
   the `i*ncol + j` multiply, which *is* the pattern — and **two consecutive
   tasks measured them and reported them as p05's numbers**, the manager's own
   retraction among them. The declaration was right both times and failed only
   by being **invisible**: it is prose, and the hashed block starts 240 lines
   later. So p05's `6·nrow + 9` **stands as a contract-relative number**, and the
   retraction of it is itself retracted.
   **And that contract-relative number bounds `inf(in-contract R3) − R4ship`
   and nothing else** — a bound only because R4 is held fixed by fiat, and the
   search for what it bounds has now failed three times
   (`patterns/p05-index-flatten/NOTES.md` §14). TASK_021 reported a *two-sided*
   floor, `5·nrow + 6`, on the ground that six in-contract unsafe spellings gave
   one instruction count. They had all decoded the header the shipped way, so it
   measured the header. TASK_021_REVIEW respelled that and got `5·nrow + 11`
   from 13 unsafe spellings; TASK_022 deleted a semantically redundant
   zero-guard and got `5·nrow + 13` from 46. **Each value had been reached by
   4–10 independent machine-code bodies, and two of the three were broken
   anyway** — so "reached by many spellings" is not evidence of a floor, and
   nothing here should ever again be published as one. See finding 12.
   TASK_021's companion claim — that the *unsafe* side "does not
   move at all" (six spellings, four distinct machine-code bodies, zero
   difference) — was **refuted** at TASK_022 on the ground that respelling the
   header moves R4 by 7 flat. ⚠ **That refutation is itself refuted**
   (TASK_027_REVIEW): the respelling needs `read_unaligned` and is not an
   admissible rung at the pinned vstd, and every alternative route to it is
   unsupported too. **TASK_021's claim was right for the wrong reason** — the
   unsafe side does not move, not because six agents happened to spell the header
   the same way, but because the `identity` pin leaves them nothing else to
   spell it with. Its
   functional form, its sign
   and its `O(nrow)` conclusion all survive under that stated pairing, but the
   "21%/18% of the tax lives in unpinned spelling" figure is the **R3 side
   alone**; over free pairs the interval is 80%/71% of the published tax. (That
   was then called "the loosest of the set"; the comparison put a *pair*
   interval next to p16's **R3-only** span. TASK_023's replacement — "p16's
   own pair interval is 111%/109%, wider" — is refuted in turn: measured, p16's
   is −239…+236 / −2449…+2244, i.e. 1759%/6095%, negative at the bottom on all
   24 blobs. **Both are withdrawn and neither is re-pointed** — a 2-lever p16
   search is not the peer of a 46-spelling p05 one.) The `nrow` axis it is swept on
   ships too: `inputs/gen.py` band D, 33 blobs, and `source_sha256` covers
   `gen.py` from TASK_021 so the law is re-derivable from a hashed file.
   **The policy, decided and implemented (TASK_016–018).** "Compare idiom-matched
   rungs" **does not work** — "same idiom" has no fixed point, its members
   differing by `O(nrow)` — and a published spread **cannot carry a safety number
   at all**, per the theorem above. What ships is a **named-spelling standard**:
   every pattern's hashed contract block carries an `idiom` object naming the
   tokens each rung must spell literally, uniform across all six, **labelled as a
   policy adopted after measuring**, with one measured clause — a rung spells the
   same operands the way its language forces — without which eight shipped cells
   fall out of contract.

   **What the pin buys is decidability, not attributability, and that was
   measured.** On p17 the excluded and an admissible spelling compile to the
   **same 478 bytes**; on p16, 42 of 77 Ir/call sit inside the unpinned part.
   What it does buy is a contract a `grep` can settle instead of one only an
   argument can settle — and a *boundary*, without which the spread is unbounded
   below on both sides.

   **The conclusion that follows, and it governs every number this project
   publishes: `R3ship − R4ship` bounds `inf(in-contract R3) − R4ship` and
   nothing else — a bound only because R4 is held fixed BY FIAT rather than
   minimised. It is NOT an upper bound on the in-contract safety tax**, which is
   what this line said until TASK_023. p16's `+27/+77` has a cheapest-found
   in-contract R3 of **−199 at `small` and −2545 at `large`** against the shipped
   R4 — the value having moved four times (~~`+19/+45`~~ TASK_023,
   ~~`−199/−2365`~~ TASK_024, ~~`−127/−2545`~~ the manager at TASK_025_REVIEW,
   who paired one rung at both inputs), and **no single spelling is cheapest on
   both blobs**: `chunks_exact(64)` is 72 Ir/call *dearer* than `(32)` at `small`
   and 180 cheaper at `large`, because a larger `K` leaves a longer scalar
   remainder tail. **A cheapest-found figure must name its input as well as its
   spelling**, which is why the word is "cheapest found" and never
   "minimum"; p17's `+32` has an in-contract respelling measuring
   **−19** against
   the shipped R4, byte-identical to the row an earlier task had excluded. Both
   patterns ship an R3 measurably off the floor of their own contract, so "the
   shipped R3 is the cheapest admissible spelling" is **false, not
   unestablished**. ⚠ **But "the unsafe rung is a spelling too" is now REFUTED on
   both of the two patterns that were said to show it** (TASK_027_REVIEW).
   ~~p05's R4 moves 7 flat (TASK_022)~~ and ~~p16's R4 moves `4·nrec` via
   `r4_hdr`~~ are **the same lever and it is not admissible on either**: at the
   pinned vstd, `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
   `TryFromSliceError` and `from_le_bytes` are each `is not supported`, so every
   route to respelling a header read needs a **new trusted item** — and the
   `identity` pin makes a rung without a verifying twin not a rung. **Neither
   pattern's R4 side has ever moved by a single admissible instruction**, while
   the R3-side levers cost zero TCB and are large. Report the fixed-R4 bound —
   **`R3ship − R4ship` bounding `inf(in-contract R3) − R4ship`, R4 held by
   fiat** — and **do not report a pair interval until someone has built an
   admissible R4 that moves**; both published ones were built from rungs that do
   not exist. And **never a per-byte difference across unmatched fold
   spellings**.

15. **p07 — the first pattern where R3's tax has NO axis along which it
   amortises.** (TASK_026, reviewed at TASK_026_REVIEW: headline **confirmed**,
   two majors and five minors against the surrounding prose.)
   Binary search: `Θ(log n)` probes, no inner loop. **R3 costs `6.0000` Ir per
   probe with `probes = nq·⌈log2 n⌉`, so its share of kernel `Ir` rises in both
   `n` and `nq`** — 42.53% → 46.63% over `n` = 7 … 16 385. The asymptote is
   `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**, 47.99% on the shipped 50/50 workload:
   fixed by the kernel *and* the query distribution, not by the kernel alone.
   **Confirmed across six deliberately different workloads** — all-hit, all-miss,
   all-below, all-above, clustered, shipped — monotone rising in every one, so it
   is not an artefact of the query mix. The laws are exact integers verified
   **out of sample** on 30 fresh blobs with an independent probe-count
   implementation: `R3 − R4 = 9 + 4·nq + 6·probes`,
   `R2 − R4 = 36 + 11·nq + 11·probes`, 30/30 exact.
   ⚠ **What this is NOT: "the first counterexample to safety is cheap".** That was
   the manager's sentence and `.memory/01-ladder.md` already refuted it — p16/p17
   carry a swept **R2** tax of 4.25 Ir/folded byte whose fraction also rises
   (toward 73.9%), and p05 an `O(nrow)` **R3** tax. What is new is the *R3*
   scoping and the *no axis* part: p16/p17's R3 tax is a per-**call** constant
   (0.00000 Ir/byte, the reslice sits outside the fold loop) and p05's is
   `O(nrow)`, which vanishes along `ncol`. p07's vanishes along nothing.
   **The `Ir`-vs-`ns` half is real and was tightened, not broken.** Disabling
   LLVM's `X86CmovConverterPass` on unchanged source gives +10.07% `Ir` → −18.13%
   `ns`, and the review closed both of the delivery's own caveats: a
   symbol-by-symbol diff of the two whole binaries found **559 symbols, exactly
   one different**, and `--cache-sim` showed the lever locality-neutral (`D1mr`
   1076.82 on both). **Branch misprediction is measurable on this box after all**
   — `callgrind --branch-sim=yes` — see `.memory/00-environment.md`.
   Sharper still, with no compiler flag: changing only the *workload* makes the
   same binary execute **+7.84% more instructions in 71.75% less time**.
   ⚠ **Do not quote p07's R2 `ns` numbers.** `safe_naive`'s layout band is
   **28.47%** — the widest single-rung band this project has measured — so the
   "+28.0% small / +3.5% large, an 8× conversion factor" claim has **no
   established sign** and is withdrawn pending a bracketed re-measurement. R3's
   counterweight (+13.0% / +1.6%) *does* survive: bands disjoint on both inputs,
   in two independent runs.
   Two more, both confirmed: p07's R4 side is **degenerate, third pattern
   running** (`r4_ptr` measures −460/−1605 and its twin dies on *"dereferencing a
   raw pointer is not supported"*); and the catalogue's stated bug was **wrong** —
   midpoint overflow is unreachable by 2.1e9 because the `u32` header field binds
   long before RAM, while the reachable overflow is in the length check.

16. **Code layout moves wall clock by up to 27% at an unchanged instruction
   stream, and it is the 32-byte fetch grid.** (TASK_026 → TASK_029 →
   TASK_030_REVIEW, measured on all seven patterns.) Two binaries from identical
   source, differing only in where the linker put the kernel — same `n_fn`, same
   `md5_fn_norel`, same executed instructions — differ by up to 27% of wall clock,
   and the difference **flips the sign of a rung-to-rung comparison**.
   **The mechanism is identified and is static**: `win32` (the loop body occupies
   one more 32-byte fetch window — p01's 30-byte SSE loop sits inside one window
   at one residue and straddles two at the other) or `jcc32` (a loop branch
   crosses a 32-byte boundary, so the chunk is not DSB-cached — this box is
   Cascade Lake carrying Intel's **SKX102** JCC erratum). Both computable from the
   disassembly with **zero fitted parameters**, and both confirmed **out of sample
   on 20 pre-registered layouts** whose predictions were SHA-256'd before timing.
   **It does not hit everything.** Real on **p07 and p01**, marginal on p08,
   **absent on p02, p05, p16, p17** — the geometry flips on all seven, but only a
   front-end-bound loop pays for it.
   **The honest summary is three-part** (TASK_031, which refined it): *the signs
   survive on four patterns* — p02's +18.04% and p08's +105.16% come through
   mode-matching, and their entire 30-layout populations are 0.84–3.66% wide, so
   nothing in them could move a gap that size; *no magnitude survives to two
   decimals anywhere it was checked* — p08's `large` R2 is +50.91% published
   against +61.93% over the population, 11 points that layout does **not**
   explain; and *the C and R5 rungs of all seven patterns remain unbracketed.*
   **p01's and p05's `small` wall-clock rows are withdrawn**, for different
   reasons. **p01's sign flips: +5.80% / −3.61% (R2) and +7.10% / −5.45% (R3)** —
   re-measured at TASK_032 with the fixed timer, every number within 0.6 points of
   the blocked-timer values and no sign moved, plus a **fresh out-of-sample
   pre-registration using one directional rule (`win32@0`) with no per-rung
   tuning**, which held with perfect separation on all three rungs across two
   passes. The committed `common/layout/data/predictions_p01oos.json`'s own
   sha256 *is* the hash printed before timing — `sha256sum` it. ⚠ **p05's
   published reason was itself wrong** — the "shipped binary is the slowest layout of 31" ranking was a
   **blocked-round-robin artefact**, reproduced at TASK_031 with *zero* layout
   variation on byte-identical copies. p05's real defect: its `small` noise floor
   on byte-identical binaries is **5–45%**, wider than any gap read off it. Under
   the project's own alternating protocol its numbers are stable and positive.
   **What to publish**: mode-matched comparison, and pairwise `P(A > B)` over all
   layout pairs. Both converge. ~~Worst-vs-best range~~ and ~~dominance~~ are
   **both retracted** — both are extrema, neither converges, and the second was
   introduced as the fix for the first.
   And the instruments: callgrind's simulators are address-*sensitive* but model
   no part of the front end, so across a 27% mode they move by **≤6 events in
   10⁸**. Use them to attribute a mechanism, never to detect or rank a layout
   effect.
   **The methodological result, which outlives the finding: interleave by CELL,
   never by block, and measure the noise floor with byte-identical copies before
   believing any effect.** A probe that gives each cell a contiguous block of every
   rep — rather than alternating, as `harness/measure.py` does — flipped a sign on
   its own, and manufactured every reading that was attributed to p05's layout.
   p01's and p07's modes survived only because they are **protocol-insensitive**
   (p07 reads +27.4…+27.8% blocked *and* alternating), which is how they were told
   apart from the artefact. **All seven patterns now carry the protocol control
   and p05 is the only sensitive one** — so the bug reached no surviving published
   verdict, and p16's and p17's "gap < 1% either way" are clean negatives under
   both protocols, which had not been established before.
   **The tool ships**: `common/layout/` (hashed into all seven `source_sha256`),
   with the population data for p01 committed under `common/layout/data/` so the
   published table reproduces with **zero measurement** —
   `python3 common/layout/survives.py --dir common/layout/data p01`.

17. **p11 — the safe class reaches a library the unsafe class cannot, and it is
   worth 35% of the kernel.** (TASK_033, **reviewed** at TASK_033_REVIEW:
   headline confirmed by independent re-measurement, two majors and six minors
   against the prose, **no blockers**.) Family B's first
   pattern, and the first kernel whose **loop bound is not known before the loop**
   — a NUL scan runs until it finds a sentinel that may not be there.
   **The decomposition, which is the pattern's point** (all rates `body_len / K`
   off the listing, `vector_regs` empty on 8 of 8 kernels):

   | scan spelling | lowers to | Ir/byte |
   |---|---|---:|
   | C `strlen` | glibc IFUNC → **AVX2** | **0.078125** |
   | `CStr::from_bytes_until_nul` (R3) | `core::slice::memchr`, SWAR 2×u64 | **0.937500** |
   | `iter().position()` | scalar byte loop | 5.00000 |
   | R4 `get_unchecked` | scalar byte loop | 6.00000 |
   | R2 indexed | + `lea;cmp;jae` | 9.00000 |

   **12.0× is IFUNC+AVX2 vs baseline SWAR; 5.3× is which Rust spelling; 3.00000
   Ir/byte is the bounds check** — a library difference, a spelling difference and
   a safety cost, separated, where the naive report would have been one ratio.
   **The swept law**, zero residual over 61 points, all four residues:
   `R2 − R4 = 7.25000` Ir per string byte `= 4.25000` (fold) `+ 3.00000` (scan).
   **4.25 = 2.00 check + 2.25 unroll is p16's and p17's constant, reproduced a
   third time with the split included.** ⚠ **3.00000 is new and is the finding to
   attack**: the *same* check costs one instruction more because the scan's
   induction variable is window-relative where the fold's was hoisted to
   blob-absolute. **A bounds check costs 2 or 3 Ir/byte depending on what the loop
   already holds.**
   **And it is the largest instance of finding 14's R4-chained-to-the-prover
   result**: `r4_cstr` would be **−17 526 Ir/call (−35%)** on `large` and is
   rejected with **four** `is not supported` errors. The safe class reaches
   `core::slice::memchr` at **zero TCB**; the unsafe class cannot reach it at all.
   R3−R4 changes sign at string length 17–18, at `memchr`'s 16-byte threshold, and
   `small`/`large` are specified on opposite sides of it.
   ⚠ **And the correction that makes it a better result** (TASK_033_REVIEW major
   1): p11 discharges an overflow obligation with one line in the *program*
   (`if q >= len { break; }`) where p17 had to buy a second `requires` — and p11
   shipped calling that **free**. It is not: it costs **1.00000 Ir per scanned
   byte, 8.5% of R4**, because the guard forces the scan's exit reason into a
   register. **The real trade is 8.5% of the kernel instead of a precondition**,
   and that is more interesting than the claim it replaces. Neither route is free;
   see `.memory/04-verus.md`.

18. **p03 — the safety tax IS the price of the optimiser failing the invariant
   the proof proves; it is NOT a fact about Rust; and it retires "nobody has built
   an admissible R4 that moves".** (TASK_036, reviewed at TASK_036_REVIEW: causal
   claim **confirmed** with three negative controls, two blockers and two majors
   against the prose.) First kernel whose **control flow is attacker-chosen**,
   first whose safety law is per *executed operation*.

   **The control that does it.** `m_clamp` = R3 plus a **dead**
   `if sp > STACK_CAP { return 0; }` — R5's own invariant handed to LLVM. Safe
   17 → 13 Ir per executed pop, unsafe 14 → 13, **gap exactly zero on both sides**,
   zero fitted parameters. **It is the invariant and not range propagation**:
   `sp > 1000` is byte-identical to shipped R3 (nothing), `sp > 65` leaves the
   check standing *and* is dearer, and a non-dead early return saying nothing
   about `sp` is dearer with the check standing.
   **This generalises finding 12's reinstated p05 sentence from a NONLINEAR fact
   to a linear one** — nonlinearity was p05's whole stated excuse. ⚠ **With two
   qualifications that change what it says, both measured:** it is **not
   Rust-specific** (clang keeps a manual C bounds check at exactly 4.00000
   Ir/executed pop, gcc keeps it too, and *both* delete 100% of it given the
   identical clamp, byte-identically — two middle-ends, and gcc shares none with
   rustc); and **LLVM does eventually derive the fact** (the clamp is gone from
   the output and the `sp > 64` path is treated as unreachable), so it is analysis
   **seeding**, not inability to prove the lemma.

   **The laws**, max residual 0.0000 over 89 blobs: `R1h − R1 = 2.00000 · xpop`
   exact and **identical on gcc and clang**; `R3ship − R4ship = 3.00000 · xpop + 5`;
   and **0.00000 on push, dropped push and empty pop** — the same check deleted on
   one side of one function and kept on the other. ⚠ **The `3.00000` is the
   shipped spelling's rate, not the class's**: in contract the class runs from
   **+3.00000 to −1.00000** per executed pop, so p03's R3-side span is
   **−113 … +5110** / **−202 … +17237**. The lever is `assert!(sp <= STACK_CAP)`
   — one line, zero `unsafe`, zero TCB, admissible (the gate's own matcher takes
   it and `.memory/01-ladder.md`'s R3 definition names *"hoisted length
   assertions"*) — **and WHERE it goes is worth 2 Ir twice** (TASK_037): on the
   loop's **back edge** it is `−1.00000·xpop` with no dropped-push cost and is
   cheapest on **both** blobs; at the loop **head** it is byte-identical to
   `m_clamp` but costs `+2.00000·dpush`, because LLVM then materialises the
   now-known `sp == STACK_CAP` on that edge; in the **pop arm** it survives as a
   runtime `cmp $0x41`. Two published cheapest-founds refuted on this one
   pattern, the second after a review had confirmed the first.
   ⚠ **"The guard must be in the same basic block" is REFUTED** — hoisting it into
   the loop head is byte-identical to shipped R3 (that control is itself out of
   contract, so it refutes the *mechanism* and is not a spelling of the class).
   The real discriminator is that
   the **push** guard supplies the *upper* bound the access needs, locally, while
   the **pop** guard supplies only the lower bound and the upper must come from
   the loop-carried invariant.

   **And the standing question in finding 14 is ANSWERED.** `m_clamp_unsafe` — R4
   plus the same dead clamp — verifies **9/0 with zero new trusted items**, holds
   the `identity` pin byte-for-byte, and measures **−118 / +497** against
   `R4ship`; on the back edge (`m_clamp_unsafe_tail`, also **9/0**, identity
   byte-for-byte) it measures **−118 / −207**. **The project's first admissible
   R4s that move**, so p03 has its first non-degenerate pair interval — the R4
   endpoint now has measured width, 2884…3002 on `small` and 8177…8881 on
   `large`. (The two class minima are 5 apart on both blobs; that is the per-call
   constant and **not** a tax — `min(R3) − min(R4)` differences two upper bounds.) Paired with the asymmetry: `assert!` on the
   unsafe side is `error: panic is not supported`, so **the safe class reaches a
   spelling the unsafe class cannot** — third instance of the R4-by-permission
   result, first where the safe lever is one line.

   **The bug** is not a wild address: `sp−1` at 0 wraps to `stack−1`, inside the
   kernel's own frame. It does not fault; it returns a wrong answer, and **R1's
   checksum is not reproducible across runs** — a *pointer*-disclosure shape,
   distinct from p17's data disclosure. UBSan beats ASan (static array type); a
   sustained underflow faults at exactly the 8 MiB `ulimit -s`. **Verus 9/0 first
   run**, no lemma. And the gate caught a **tautological conjunct on a trusted
   item** via 5c-twin's per-conjunct probe — its first fire on shipped code.

19. **p09 — one character, in one position, separates a bug everything catches
   from a bug nothing catches.** (TASK_038, reviewed at TASK_038_REVIEW:
   invisibility **confirmed against four vacuity attacks**; one blocker and five
   majors against the prose, two of them project-wide.)

   ```
   words[q >> 6]   shipped
   words[q >> 5]   caught by memory safety ALONE, on every input
   words[q >> 7]   caught by NOTHING — no bounds check, no ASan/UBSan,
                   no Miri, no memory-safety proof
   ```

   `q >> 7` is `q/128 ≤ q/64`, so under the guard it is **always a legal word
   index**: `19 verified, 0 errors` with the functional spec stripped, `20/0` once
   the spec moves to match. **Zero instructions** (6691.70 vs 6692.30), and
   **the whole 368-byte R4 kernel differs in ONE BYTE** (offset 156, `06` → `07`;
   TASK_039). All five builds print the same wrong answer **on `small`, p09's
   headline blob** — not only on thin windows; ASan+UBSan are silent on *every*
   input and Miri is `exit=0 UB=no`.
   ⚠ **And it is a CLASS of ≥ 9, not an instance**: the obligation reduces to
   `C·(nwords−1) + 8 ≤ 8·nwords`, so every shift digit above 6 and every scale
   below 8 qualifies. Second member measured — `4 * (q >> 6)`, again one differing
   byte (the SIB scale), and its `_msonly` verifies **18/0 with no ghost line at
   all** where `q >> 7` needs one. `q >> 7` is the headline only because it is the
   one member in `q >> 5`'s own character position. ⚠ **This is the example to quote, not
   `q & 31`**, which is a *two*-character edit costing +32% on R4 — p09 shipped
   calling both "one-character bugs" and that is wrong on both counts.
   **The probe is not blind**: `_msonly` survived `assert(false)` in three places
   and guard deletion, so a proof that still catches R1's spatial bug discharges
   these clean.

   **The obligation that fires is a VERIFIED item's**, `load_u64`'s — not the
   trusted accessor's, whose `requires` is *shadowed*. p09 is the only pattern
   with decoder wrappers, so this is the first time the memory-safety obligation
   sits **outside the TCB boundary**. TCB is **7 lines / 4 items**, the
   second-smallest here.

   ⚠ **The reslice hazard, and it is the whole of p09's R3 > R2 inversion** (the
   first in this project). LLVM loses the 8-byte load-merge idiom on exactly one
   of eight loops: **reslice + a data-derived index + a multi-byte decode at it**.
   R2 keeps the merge on the *same* access. `+21` lost merge, `+1` spill, `−5`
   cheaper checks = `+17`. **Half of the p03-style seeding win here is the
   restored load idiom, not deleted checks**, and `q & 31`'s cost is the same
   mechanism — which unifies p09's two cost stories. **p03's seeding control does
   not transplant**: the failed inference is the composition through the
   **multiply**, not the shift.

   The three-check decomposition has **zero free parameters** — every coefficient
   is a loop-body instruction count off the listing, and out of sample it predicts
   `large` to within **1.13 Ir of 73404**. `q >> 6` ≡ `q / 64` on all three
   compilers, so that `forbidden` entry moves no number.

20. **Two measurement defects found in passing, both project-wide.**
   (TASK_038_REVIEW.)
   **(a) `measure.py`'s `ns` column is a whole-process LEVEL, never a
   difference** — the per-process constant (argv, file I/O, payload decode) is
   inside every published wall-clock number, and on p09 it is **55% of `small`
   and 73% of `large`**. Subtract `t(n_iters = 1)` before quoting any ratio. **A
   whole mechanism died on this**: p09's "the extra instructions retire cheaper
   than average" (ILP) came from a 2–4× `Ir`-vs-`ns` gap, and corrected **the
   largest surviving factor is 1.5×**. ⚠ Name the blob (TASK_039): R3's `ns`
   penalty exceeds its `Ir` penalty **on `small` only**; on `large` it stays
   below (+179…+183% against +199.4%). The correction's own error bar is **±9
   points** — `R5 − R4`, which must be 0, reads −0.9…+8.7% across four runs — so
   quote a corrected ratio only where the effect clears it, as p09's do by 11–25×.
   See `.memory/03-measurement.md`.
   **(b) A `forbidden` entry without backticks is audited ZERO times**, while the
   verdict line two above still counts it (**`check_idiom`** keys on `_TICK`,
   `check.py:1103-1105`; this read `:929` until TASK_066). p09
   shipped 5 forbidden entries and 0 audited spellings — its "forbidden: 0 hits"
   was kept **by auditing nothing**. Backtick every entry you want enforced.

21. **p12 — the bulk-copy lowering needs BOTH ends of the copy free of a
   per-iteration check; and a write bug forces the *adversarial* row, not the
   perf row.** (TASK_040, reviewed at TASK_040_REVIEW: two blockers, three
   majors; headline **confirmed and sharpened**, two published numbers moved.)
   First bug here that is a **write** safe Rust cannot express; first time
   `c-gcc` and `c-clang` differ in **behaviour**.

   **Confirmed by the control p12 did not build**: a *safe byte loop* with no bulk
   call anywhere in its source lowers to `memcpy` — so the recovery is about
   **where the check is**, not about `copy_from_slice` carrying its own bound. ⚠
   **But "on the destination" is not the rule**: checking only the *source* per
   byte also kills it. **Both ends must be free.** Consequence: `R2 − R4` has no
   per-byte law, and precisely — R2 alone is **exactly linear at 24.75 Ir per
   copied byte**; the non-law is entirely **R4's `memcpy` size dispatch**.

   ⚠ **THE STRUCTURAL CLAIM WAS TOO STRONG, and the reviewer built the row p12
   said could not exist.** What is forced, with no read analogue: *for a write bug
   whose guard's threshold **is the destination's ALLOCATED EXTENT**, every input
   on which the guard fires is one on which the unguarded rung executes an
   out-of-bounds store.*
   Whether that input can **also** be a checksum-agreeing perf row is a **design
   choice** — fold the destination at *fixed extent* and put rejection exactly at
   capacity, and checked and unchecked print identical checksums at every
   `n_iters` while ASan still fires. The price: **the perf row executes UB on
   every call**, usable only in the silent regime (≤ +8 B here).
   ⚠⚠ **AND THE PREMISE DOES NOT REACH THREE OF THE FIVE PATTERNS IT WAS WRITTEN
   FOR** (TASK_041, measured: `p12/NOTES.md` 1b, probe under ASan+UBSan). Hold
   everything fixed but the guard's threshold: at `n == sizeof dst` the guard
   fires and the unguarded rung stores OOB; at a **caller-supplied** `n < sizeof
   dst` the guard fires just as loudly — the checksums differ — and the unguarded
   rung is **ASan- and UBSan-clean**. So **p13** (`strncpy`'s `n` is
   caller-supplied, and its bug is the missing NUL and the OOB *read* downstream)
   and **p24** (`child < n`, a live length below capacity) do **not** inherit it;
   **p14**'s delimiter is not a bound at all and it is the scan's `i < len` the
   sentence reaches; **p23** and **p25** do inherit it. The generalisation is
   about the **threshold**, not about the write: a threshold at the allocation's
   extent makes "the guard fired" and "the unguarded rung committed UB" the same
   event; a threshold inside the allocation makes them independent, and then the
   write patterns behave exactly like the read patterns.
   See `.memory/02-bench-rules.md`.

   ⚠ **`−26.00` is a FIXED-R4 figure.** p12 called its pair interval degenerate on
   an *inference*; the reviewer **built** the cheaper R4 (route A) and it verifies
   **15/0, twin 18/0**, holds `R4 ≡ R5 exact`, and is **17.00 / 92.00 cheaper**.
   On `large` that **flips the sign** — shipped R3 is **+66.00 dearer** than the
   cheapest verifying R4. The fourth "safe beats unsafe" instance is fixed-R4
   only. And the `identity` pin's price is **3.00 Ir per string walked**, not the
   `+2` published — that was a static `n_fn` delta wearing a per-string label.

   Observability is a function of **magnitude and compiler**: **+1…+8 B silent
   and wrong on both**, then gcc's canary and clang's caller-frame corruption,
   then clang's SIGSEGV. ⚠ **Quote the regime, not the constant**: the two upper
   boundaries are frame-layout properties and move with the binary — step-1 on
   p12's own probe they are **+9** and **+57** (TASK_041), step-4 on the shipped
   kernel the review read them as +12 and +64, and the first publication's coarse
   grid gave +16 and +64. The **+8** boundary is the one that reproduces.
   `-fno-stack-protector` would be **both a thumb on the scale and unnecessary**.

22. **Attribute a surviving panic pad by DECODING its `core::panic::Location`.**
   (TASK_040_REVIEW.) Counting pads says *how many* checks survived, never
   **which** — and on p12 the difference overturned a published mechanism and a
   rung's source comment on the day it was written. `dst[..dlen]` contributes
   **zero** pads in all three fold spellings, so "the count stays at 2" was
   evidence the fold **never** contributed one, read as the opposite. The decoded
   survivors are the window reslice and the source reslice, which gives a sharper
   discriminator than p03's locality story and does **not** transplant it: a bound
   from a **constant** LLVM can see is elided; a bound from a **runtime value** is
   not. **Tool, now committed: `patterns/p12-strcat-fixed/controls/pads.py`**
   (TASK_041 — the review's `.temp/r40/pads.py` is gitignored, and its `%rcx`-only
   `lea` match under-counted R2 by 2 of 7; the shipped one matches any register,
   validates the decoded struct, resolves the file name through the
   `R_X86_64_RELATIVE` addend, and prints the guarded expression with a caret).
   See `.memory/03-measurement.md`.

23. **p04 — known BITS survive a loop-carried phi where a range does not, and the
   rule is `next_pow2(CAP) ≤ ARR_LEN`.** (TASK_042, reviewed at
   TASK_042_REVIEW: **the headline was confirmed by a stronger test than I asked
   for, and its stated mechanism was refuted**; one blocker, three majors.)

   **The three-operator series closes, and the closing sentence survives.** p05
   asked whether a bound survives a **multiply** (no — nonlinear), p09 a **shift**
   (yes alone; no through the composition with a multiply), p04 a **modulus**.
   The evidence that settles it is the control nobody asked for: spell the wrap as
   a **source-level branch** and both ring checks come back **at `RING_CAP = 64`
   as well as at 60** (86 → 101 instructions, 1 → 3 pads), at the identical
   provable cursor range. **So the range is never what carries; what carries is
   known bits contributed by the operator.**
   ⚠ **What was FALSE is p04's published explanation of the 60 case** — *"`% 60`
   fixes no bits"*. It fixes `< 64` (`computeKnownBits(urem x, 60)` zeroes the
   high 58), **and that survives the phi**: `% 60` into a `[u64; 64]` array
   elides. The measured rule, zero fitted parameters, is **`urem x, C` ⟹
   `x < next_pow2(C)`, and `next_pow2(CAP) ≤ ARR_LEN` is NECESSARY for elision
   and sufficient only ABSENT a cursor-relating guard** — the necessary half
   reproduces every capacity p04 built *and* the mixed cases it never built
   (`% 32` into `[u64;64]`, `% 64` into `[u64;96]`: both elide). ⚠ The qualifier
   is load-bearing: `% 60` into `[u64;64]` **with** p04's two guards is 2 pads,
   not 1 — the store check goes, the load check stays. A guard destroys the fact
   for `urem` and **not** for `and`, which is what separates the two operators.
   **`RING_CAP = 60` is still the largest single effect**: at matched execution
   counts `R3 − R4` goes **+5 → +479**, p03's dead clamp takes it back exactly,
   and three middle-ends agree in both directions — **the operator, not safe
   Rust.**

   ⚠ **THE SHIPPED R3 IS NOT THE CHEAPEST FOUND — and that yields TWO numbers,
   not a correction to one.** Six in-contract spellings across **five distinct
   machine codes** measure `3367 / 11666` against the shipped `3368 / 11667`.
   p04 **did not re-ship** (now a project rule — `.memory/02-bench-rules.md`,
   "never re-ship a rung because a cheaper spelling was found"), so the
   **fixed-R4 bound stays `+5.00`** and the **cheapest-found in-contract bound is
   `+4.00`**. Publish both, labelled; I briefly told the engineer to overwrite the
   first with the second and it refused, correctly. *"The first pattern whose
   shipped R3 is the cheapest found"* is **false** either way — beaten by the next
   lever, exactly as on p03. **The lever is new**: a **two-step reslice**
   (`split_at(off).1.split_at(len).0`), whose mechanism is **register allocation,
   not bounds-check removal** — `off + len` needs a scratch register,
   `buf_len − off` is computed in place. **Untried on every pattern before p04,
   and most patterns' R3 opens with the reslice it improves.** The `idiom` block
   pins no reslice spelling, so it is the *cheapest-found* claim that failed and
   not the declaration; p04's direction test holds.

   ⚠ **Two of the seven "exact integer cost models" fail out of sample, and no
   in-sample blob could have shown it.** The two R1 rows were fitted over 99 blobs
   on a licence verified only on band F — **where `epop == 0` by construction**.
   One fresh blob with `dpush` *and* `epop` both non-zero misses by **−385 / −330**;
   the same laws in *R1's own* counts land exactly. The other five re-derive by
   independent exact-rational solve, rank 5/5 reproduces, and the `large`
   out-of-sample prediction holds. See finding 20 and `.memory/03-measurement.md`.

   **The bug is invisible to memory safety — both guards, and both at once.**
   `m_nofull_msonly`, `m_noempty_msonly` and both-deleted all verify **9/0** with
   the functional spec stripped, against five positive controls that correctly
   fail. Second instance of finding 19, on a **container** rather than an index:
   drop the fullness check and a push overwrites the oldest element with **no OOB
   access at all**.
   ⚠ **But the published characterisation is too specific, twice.** *"The relation
   between the cursors is exactly the part of the state the obligation does not
   need"* is true and **is not a characterisation** — reading `ring[tail]` instead
   of `ring[head]`, memory-safe and functionally wrong with **no guard touched**,
   also verifies 9/0. **The memory-safety-only configuration is blind to every
   functional change.** ⚠ **And it is not about the modulus**: delete `%` entirely
   and wrap with a source branch under the guard, and the obligation is *still*
   two independent one-variable clauses and the bug *still* invisible. **The
   property is that the index bound is the array's own fixed capacity.**

   Sound and unchanged: R4 ≡ R5 `exact`, R5 **9/0 first try, no lemma**; TCB 10/5
   matching the gate; `p1_weak_requires` caught **only** by the twin; pair
   interval **degenerate** (the opposite of p03, because the clamp seeds a fact
   LLVM already has); R1's wrong answer **reproducible** across 880 runs; and the
   `ns` figures **survive a real 30-layout population** the delivery had declined
   to build (`+25.1…+26.0%` / `+9.3…+10.2%`, `P(A>B) = 100%`).
   `R2 − R3 = 20.00000·ops + 11` is p03's law exactly — and the **boundary is
   named**: it reproduces for the **opcode stream** (identical 5-byte record) and
   not for the **container** (p03's pop guard supplies only a lower bound, p04's
   `%` supplies both cursors' upper bounds unconditionally).

24. **Two defects in my own infrastructure, both found by a pattern task.**
   **(a) `.memory/00-environment.md` constraint 6's documented sweep rule was
   destructive and never described the sweep that ran.** *"delete the non-`text/*`
   ones"* deletes every `.json` — `file` reports JSON as `application/json` — so
   it would delete **every gate record it is pointed at**. The actual 2026-08-18
   script used a **deny-list** of six binary mime types; documentation and
   execution had diverged. Replaced with a keep-list by extension, which cannot
   fail open. It cost p04's engineer three evidence files.
   **(b) `common/layout/order.py` appends `.bin`**, so `--input small.bin` times
   `small.bin.bin`, every rung measures process startup, and `R2 − R4` reads
   **+0.15%** — a clean publishable-looking null from a file that does not exist,
   exit 3. **Caught only by cross-checking the `Ir` column**, which is now the
   rule: +141% `Ir` against a +0.15% `ns` null is not a conversion factor, it is a
   broken measurement.

25. **p13 — a bound the optimiser can SEE is worth more than the check costs;
   and a contract that pinned one side of its own comparison.** (TASK_043,
   reviewed at TASK_045_REVIEW, corrected at TASK_046: **three blockers, six
   majors, and six more manager prescriptions refuted while landing them.**
   ⚠ **The headline's sign, magnitude and stated mechanism ALL moved.**)
   `strncpy` truncation — the first bug here that is a **correctly-called library
   function** rather than an omitted line, and the first whose **harm lands at a
   different site from the bug**.

   **The corrected mechanism, and it is a better result than the published one.**
   p13 shipped the safe-beats-unsafe gap as *"R3 gets `memcpy`/`memset`, R4 has
   byte loops"*. **R4 makes the same two library calls at the same cost.** 72%
   (`small`) and 91% (`large`) of the gap is the **consumer scan**, and its
   direction is the reverse of the published one: **a consumer whose bound LLVM
   can see fully unrolls to 2 Ir/byte; an unbounded walk stays a 4-instruction
   loop at 4** — `+2.00000` Ir per consumed byte at matched spelling.
   ⚠ **The discriminator is the BOUND, not the check**: an *unchecked but
   bounded* scan costs exactly what safe `position()` costs, to the instruction.
   A bounds check is one way of supplying the bound and is not what is paid for.
   **This is p03's
   and p04's seeding result from the other direction** — there the invariant had
   to be handed to LLVM as dead code; here the safety check supplies it as a side
   effect and more than pays for itself.

   ⚠ **The margin was inflated by p13's own contract, and this is the DIRECTION
   TEST's first fire.** `spec.md` pinned the byte-loop copy and fill in
   `unsafe.rs`/`verus.rs` and **exempted `safe_tuned.rs` by name** — only the
   safe rung could use the winning spelling. An admissible bulk R4 exists and
   verifies (`copy_nonoverlapping` + `write_bytes`, **17/0, twin 24/0**,
   `identity: exact`, TCB 5→7): the pin was worth **52% (small) / 16% (large)**
   of the margin. ⚠ **AND THE SIGN DOES NOT SURVIVE.** Allow R4 a
   *bounded* unchecked consumer — which verifies **19/0, twin 22/0, with no new
   trusted items**, excluded by nothing but `spec.md`'s English — and
   `R3ship − R4` is **+44.00 / +77.00**. **p13's "safe beats unsafe" is the price
   of a bound, and it reverses the moment the unsafe rung is allowed one.**
   Three numbers ship: fixed-R4 **−177 / −1054**, cheapest-found **−85 / −885**,
   and **+44 / +77** once the fiat goes.
   ⚠ **A scoped entry is not automatically a thumb.** p13 had three and measuring
   each gave three answers: copy/fill was a thumb (relaxed), `position()` is
   excluded by vstd one layer down (kept, free), the consumer *bound* is pure
   fiat (kept and **priced**). Price every scoped entry; publish the price beside
   the number it protects.
   ⚠ **p13 blamed the prover for the unsearched R4 side and the prover did not
   bind.** The R4-is-chained-to-the-prover mechanism (finding 14) is real and is
   now also **the most available wrong explanation here.** Run `verus_run.py`
   before invoking it.

   ⚠ **Two published figures move because the kernel-exclusive column is not
   comparable across p13's rungs** — the first pattern whose rungs call
   *different* libc routines. On the corrected tree the gcc-vs-clang `small` gap
   reads **1769** on the kernel column and **1463** on totals, and `R2 − R4`
   goes **+33.34%/+28.98% → +25.59%/+24.93%** — the difference being `memcpy`'s
   190/264 Ir/call **exactly**, which R2 never calls and R4 does. See `.memory/03-measurement.md`.
   ⚠ **And C's whole advantage is a LIBRARY difference**: every C `-O3` cell
   calls glibc `strlen` for the consumer and no Rust cell does. With clang
   `-fno-builtin-strlen`, **the sign of every same-backend C-vs-Rust row flips**.
   Consequence for the gate: `strlen(` is `forbidden`, absent from every source,
   audited at **0 hits**, and in every C object — **a text pin binds the source,
   not the object.** Across every pattern in the tree, **p13 is the only one where the
   optimiser reintroduces a forbidden spelling** (8 of 16 objects; p12 0 of 16).
   ⚠ That audit is only right **scoped to `kernel` + `main`** — unscoped it flags
   p12 too, because `std::env`, the backtrace machinery and `io::Error`'s
   `Display` call `strlen` in every Rust binary of every pattern.

   Sound: Verus **19/0** (twin **22/0**), `R4 ≡ R5 exact`, TCB 5 = the gate's own
   count, Miri 9/9. ⚠ **Said `17/0 first attempt` until TASK_058** — the delivery
   counts, superseded by TASK_046's fold repair; the pins are 19 and 22. The **termination store is `1.00000` Ir per string on both
   compilers** and is *not* DSE'd, because the fill's extent is a runtime value —
   I predicted DSE and was wrong. **`strlcpy` is dearer than `strncpy` and
   `snprintf` far dearer, on both compilers: the unsafe routine is the cheapest.**
   The two harms **separate by rung, not by input** — an adversarial row that
   truncates while every rung stays memory-safe is **unsatisfiable**, because
   content lost ⟺ no NUL in `dst` ⟺ R1 reads OOB.
   **No cost law**: `strncpy` lowers to size-dispatched vector code, every
   natural step basis is **singular** on a length-homogeneous fit set, and the
   "no law" residuals are **estimator-dependent by 3×**. Its out-of-sample band
   **could not fail, provably** — see finding 20 and the new
   `.memory/03-measurement.md` rule: hold out a **length**, not a **mixture**.

26. **p06 — the `Ir` column is SIGN-WRONG, and the deterministic metric is the
   one that misleads.** (TASK_047, reviewed at TASK_047_REVIEW — **2 blockers,
   3 majors, 5 minors and 14 clean negatives** — corrected at TASK_048.
   Authoritative version: `.memory/01-ladder.md` **finding 15**.)

   An in-place rotate by three reverses over a fixed `[u8; 64]` scratch; the
   omitted line is `r %= m`. It was built to make `Ir` *understate* a safety tax,
   because a `div` is **1.00 `Ir` and ~20–40 cycles**. It does worse: **on clang
   the hardened rung executes 45–108 FEWER instructions and runs 10–20% SLOWER.**
   An `and` control with no divide isolates the mechanism at −12.00 Ir/record —
   reducing `r` proves `r < 64`, the value stays 32-bit, and clang's
   7-instruction LE decode collapses to one `mov`. **Finding 6 finally has a
   designed instance with a named mechanism instead of an accident.**

   **The best thing in the cycle is a clean negative.** The review did not argue
   about the missing layout population — it **built** it (30 layouts/cell, both
   `%32` residues, every loop's `win32`/`jcc32` flips) and the headline survived:
   **`P(A>B) = 900/900`**, both compilers, both inputs, mode-matched, no sign
   flip. A `d_cmp` control puts **91.6% of gcc's +88.08 ns on the divide**. The
   manager's arithmetic objection to the headline was **wrong** — it divided by
   the probe's `+1.00 Ir/record` instead of the shipped law's `+8.00`.

   ⚠ **And 23% of that `+8.00·nrec` law is EXECUTED ALIGNMENT PADDING**, with
   only 1.000 of it the divide. `.memory/03-measurement.md`'s padding trap was
   static-only until now; it happened **twice on this one pattern**.

   **Two blockers, both about publishing a point as though it were a class.**
   The shipped R3 is `2.00000 Ir/byte`; an in-contract zero-`unsafe` control is
   **0.00000 Ir/byte**, and **none of the 2.00 is a bounds check** — it is the
   `zip`/`Rev` adaptor's exhaustion tests, with identical panic pads. **Fourth
   pattern to make this mistake, and finding 3 needed no correction: it says
   quote the cheaper of two in-contract R3 spellings, and p06 did not.** The
   second blocker removed a trusted item at zero `-O3` cost (**TCB 6 → 5,
   18/0, twin 23/0**) — but **not** free at `-O0`, where the gate caught
   `identity` dropping to `differ`.

   **p17's limit, arriving on a WRITE.** For `m < r ≤ SCR` (**not** `r ≥ SCR`)
   the unreduced rotate stays inside the scratch and C, safe Rust, unsafe Rust
   and the proved rung **all print the same wrong answer**, ASan and UBSan clean
   — including three delete-the-check controls, one with zero `unsafe`.

   **`_msonly` cannot separate the regimes, and the reason generalises**:
   deleting the check *and* weakening the spec to memory-safety-only **still
   fails**, because a proof quantifies over all inputs and regime 2 is genuinely
   unsafe. **The separation needs a program change, not a spec change** — p17's
   control-2 lesson, second instance.

   **Two parameter-free laws**, both exact: `swaps(m,r) = m + [m even AND r odd]`
   (so the rotate amount **does** enter the cost — the manager predicted no `r`
   term), and the per-record law at period **4, not 8**, exact on 45/45.

   ⚠ **"The twin is the sole catcher" was false on SIX patterns**, not two —
   see the audit note in the queue. **All six are now fixed** (p06 and p12
   first, then p03, p04, p05, p11 and p18 at TASK_054/056, each naming the task
   in its own `NOTES.md`). ⚠ This line said the last five were *not* fixed and
   the queue section said they were; TASK_058 caught the contradiction and the
   queue was right.

   ⚠ **p06's floor is ±4.6%, not the ±3% it published** (TASK_049_REVIEW).
   Headline intact — the clang column clears it at ~2.1×.

27. **p14 — an EXACT law, fitted entirely where the guard never fires.**
   (TASK_049, reviewed at TASK_049_REVIEW — **2 blockers, 3 majors, 4 minors,
   17 clean negatives** — corrected at TASK_050. Authoritative:
   `.memory/01-ladder.md` **finding 16**.)

   A CSV-style field split into a fixed descriptor table; the bound is
   `nt < MAXTOK`, **the first bound here that is a count of a byte value rather
   than a length.**

   **Its task made settling the bug class the FIRST deliverable, and the
   engineer rejected all four candidates it was handed** — the manager's three
   and the catalogue's — and shipped a fifth. **Fourth pattern to overturn its
   own catalogue row.** The lifetime candidate, which would have been the
   ladder's first, is *not observably wrong at `-O3`* on either compiler (p08
   exactly) and its pointer descriptors leave R4 unprovable.

   **The result is a methodology result.** `c-gcc-h − c-gcc = 1.00·bytes +
   2.00·fields − 3.00` is **exact — max residual 0.0000 over 66 blobs** — and
   **contains zero fitted inputs where the guard fires**. On the inputs p14
   exists to model it inverts: **−551, −823, −611** against +93, +93, +429.
   **The manager wanted that as the headline *"hardening is cheaper than the
   bug"*; the engineer refused it and was right** — past the cap the two cells
   compute different functions, the unhardened rung is already committing UB,
   and on one blob its `c-clang` cell **is not a function of its arguments**
   (`r₂…r₅ = 0`, marginal 17.982 `Ir` for 168 folded fields). Ships as **the law
   with its domain**, and **behaviour, not cost, outside it.**
   ⚠ **The project already keeps that rule structurally**: `measure.py`'s
   `CG_PLAN` is six entries, all `small.bin`/`large.bin`, so **no published `Ir`
   figure anywhere is measured on a bug-triggering input.** p14 would have been
   the first exception.

   ⚠ **Its leave-one-length-out cannot fail** (exact fit, rank 4 survives
   dropping any band) — p13's mistake in a new costume. ⚠ **And the R4/R5 pair
   is not a null control**; see the START HERE box.

   Sound: **19/0** (twin 23/0), `R4 ≡ R5 exact` / `norel`, **Miri 8/8**,
   **TCB 6 = 4 U-license + 2 infra** — TASK_048's classification's first use on
   a new pattern, and it survived review.

28. **p18 — UB that is not memory-unsafety, and four catchers all outside the
   measured matrix.** (TASK_051, reviewed at TASK_051_REVIEW — **1 blocker,
   7 majors, 5 minors, 15 clean negatives** — corrected at TASK_052.
   Authoritative: `.memory/01-ladder.md` **finding 17**.)

   A LEB128 varint decoder with the shift bound removed. **The first bug here
   that is UB but not a memory-safety bug**: it touches no memory and **ASan is
   silent**. §0 **upheld the catalogue's guess — the first row in five patterns
   to survive it.**

   **Four things catch it — UBSan, `-C debug-assertions`, Miri and Verus — and
   every one is outside the 24-cell matrix.** The manager published *"ASan, Miri
   and a proof are all blind"* and was wrong on two of three. ⚠ **Miri catches it
   as a PANIC, not a `Undefined Behavior` report**, so a gate keying on the `ub`
   flag alone calls it clean.

   **The row it exists for:** safe Rust with the guard deleted — **zero
   `unsafe`** — at `-O3 -C debug-assertions=off` is **bit-identical to C's R1 on
   every adversarial blob**.

   **`R1h − R1 = 2.00·bytes`, zero fitted parameters, and it does not
   amortise** — 11.89% of `small`'s kernel `Ir` *and* 11.11% of `large`'s.
   p07's never-amortises result on a new axis.

   ⚠ **`-C debug-assertions=on` also re-enables `assert_unsafe_precondition!`
   inside `get_unchecked`, and 15 of 16 R4s rest on it.** The manager's reading
   (*"R4's advantage over R2 vanishes"*) was **refuted** — true on p18 and p01,
   **false on p16**. What holds on 3 of 3: **at `-O3` with debug-assertions on,
   R4 becomes dearer than R3.**

   ⚠ **"Verus catches this bug" is spelling-conditional** — `wrapping_shl`
   verifies. **And the sanitizer catches the undefinedness, not the wrongness**:
   a *defined* `<< (shift & 63)` control has R1's cost law and R1's wrong answer
   with UBSan silent.

   **Two infrastructure results.** Its blocker — an exact law with an unstated
   domain, falsified by a **committed matrix input** — produced
   `.memory/03-measurement.md`'s domain rule and **the first out-of-sample test
   here that could have failed and did not** (additivity extrapolation: fit where
   two parameters never co-occur, predict where both fire; 40 predictions, worst
   error 0.0228). And it closed a **demonstrated gate hole** — `check.py`'s Miri
   stage never compared exit code or stdout when `expected_exit != 0` — with a
   committed regression check. **A second hole of the same shape is open.**

29. **p10 — the safe rung beats the unsafe one, and none of it is safety.**
   (TASK_057, reviewed at TASK_057_REVIEW — **1 blocker, 5 majors, 5 minors,
   21 clean negatives** — corrected at TASK_059. Authoritative:
   `.memory/01-ladder.md` **finding 18**.)

   A weighted FIR stencil; **the first kernel here with more than one indexed
   read per iteration** at a fixed offset from the cursor. Bug class **upheld**,
   second of six settled.

   **Safety's own cost is a two-part answer, not a number: `0.00` `Ir` per
   VECTORISED tap and `+3.00` per SCALAR-EPILOGUE tap.** And the `+3.00` is not
   *"the check costs 3"* — R2 spends **5** instructions on two bounds checks and
   **saves 2**, because indexed addressing off one induction variable replaces
   the unsafe rung's three pointer bumps.

   ⚠ **Its headline was wrong in the FLATTERING direction and the corrected one
   is bigger.** It shipped as `R3 − R4 = −323/−603`, *"safe Rust cheaper than
   unsafe"*, blamed on panic pads. Pads can only explain the per-tap coefficient
   and that coefficient is **0.00**. **60% of the margin was R4 spelling** — the
   rejected candidate verifies once one invariant clause is added — and the rest
   is **index-expression bookkeeping in any language**: `c-clang`, with the same
   index expression as the unsafe rung, is **dearer than both Rust rungs**, and
   there is no bounds check in any of the three. **Safe Rust beats every LLVM
   cell and does not beat gcc on `large`. Quote the backend and the blob.**

   **Three transferable results, all in `.memory/03-measurement.md`.** A law
   fitted in one **inline mode** is not the law in the other — `nout` and
   `scaltap` **swap roles** between `isolated` and `whole`, both fits rank-full
   and exact. An **`identity: exact` pin excludes every candidate R4 carrying a
   panic pad**, which bounds the R4 search space on *every* pattern. And p18's
   domain rule reproduced on an **eighth** pattern, with the diagnostic
   quantified: the old columns refitted over all rows go to residuals **9.19 …
   1606.73**, which a caveat would have hidden.

30. **p27 — the first TEMPORAL bug, and the lifetime guarantee costs ZERO.**
   (TASK_060, reviewed at TASK_060_REVIEW — **no blocker**, 3 majors, 8 minors,
   **28 clean negatives** — corrected at TASK_061. Authoritative:
   `.memory/01-ladder.md` **finding 19**.)

   A handle table over **per-record `malloc`/`free`**; R1 omits one conjunct on
   the READ path and dereferences a freed record. Every other bug here is
   spatial or logical; this is the class safe Rust rejects at **compile** time.

   **`R3 − R4 = +230.07 / +792.75` and NONE of it is temporal safety.** A
   decomposition closed over *every* function — not four chosen ones — gives
   `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, with `malloc`,
   `free`, `_int_malloc`, `_int_free` and all three `__rust_*` **equal to the
   last digit** between the rungs. And the spatial tax runs backwards: an R4
   that *keeps* R3's bounds checks costs **+153.51** against R3's **+109.65**,
   so **safe Rust pays 43.86 LESS of it**. The rest is drop glue.

   > **The lifetime guarantee's cost is zero and its shape is structural: the
   > free and the invalidation are ONE operation in safe Rust and TWO in C, and
   > the bug is neither of them going wrong — it is the THIRD, the *asking*,
   > going missing.**

   ⚠ **Two predictions this file carried for weeks were both wrong.** Safe Rust
   is **not** forced onto `(slot, generation)` — the handle comes out of a
   **file**, so it is an integer in every rung, and safe Rust is forced onto
   `Option<Box<u8>>`, niche-optimised into the hardened-C representation
   (verified on the shipped binary). And `tcb_items` is **7**, not the 2 this
   file called the prospective gameability alarm: right in substance (the
   allocation adds **zero** project-local axioms), wrong in its number.
   **TCB 7 is forced, not chosen** — `identity: exact` is an **18-of-18**
   invariant and the minimal-TCB variant's R4/R5 pair is `differ`.

   **Two methodological results, both in `.memory/`.** The **verified twin
   works and both its legs are load-bearing** — four weakenings caught at twin
   19/1, and the one-sided case caught **structurally** by signature equality
   where Verus verifies it 20/0. And the **direction test was verified
   byte-exactly for the first time**: the pre-build contract reconstructed from
   the disclosed edits alone reproduces the recorded hash, and no single edit
   does.

31. **p47 — the proof certifies a LEAKING kernel and its obligation count does
   not move.** (TASK_064, reviewed at TASK_064_REVIEW — 3 majors, 6 minors,
   **32 clean negatives** — corrected at TASK_065. Authoritative:
   `.memory/01-ladder.md` **finding 20**.)

   Constant-time compare, and the first pattern whose security property the
   ladder is structurally unable to measure. `m_leak` is `verus.rs` plus an early
   exit: **14 verified, 0 errors**, `kernel`'s obligation count **unchanged at
   3**, identical checksums on all 32 cells, **+7088.000 `Ir`** of leak.

   ⚠ **The precise reason is stronger than "Verus can't see timing".** The diff
   touches **no `requires` and no `ensures`** — the contracts are **identical**,
   and the shipped proof is a *strictly stronger intermediate* under the same
   contract. **A property of the TRACE is invisible to a logic about the VALUE**,
   and both numbers this project publishes for proof burden are blind to it.

   **`Ir` under callgrind IS the side channel** — the only pattern here whose
   primary metric is literally the harm. Spread in first-mismatch position:
   **184.000** for C, hardened C and safe Rust's `==`; **0.000** for every
   constant-time rung, identical at both inline modes.

   ⚠ **Catalogue bug class REFUTED — third overturned against two upheld.** The
   optimiser never reintroduces the branch, across LTO, PGO trained 100% on
   mismatch-at-byte-0, AVX2, AVX-512, `__builtin_expect` and a branching caller.
   **The adversary is the idiom, not the optimiser** — so `volatile` buys nothing
   and costs **6.75× / 9.68×**, inverting the standard advice.

## Retracted — do not reinstate

- **"Safe Rust pays an O(n) bounds-check tax"** (p02). The indexed fold's bounds
  checks cost *zero*; the whole delta was one spelling of an overflow check
  defeating LLVM's `memcpy` idiom recognition. Restated as a **codegen fragility**
  finding: one spelling loses the idiom, three others are +10 flat.
- **"C beats Rust"** (pilot). A **gcc-only** measurement generalised to "C"; the
  sign was backwards. The clang result was never affected.
- **"gcc's byte loop beats glibc `memcpy`"** — mislabelled; it beats R4, not gcc's
  own memcpy build.
- **"p16 is the first true O(n) *safety* cost"** — written by the manager from an
  engineer's report **without re-measuring**, and corrected at TASK_007_REVIEW.
  R3's per-byte rate equals R4's exactly, so the O(n) cost belongs to one
  *spelling*, not to safety. This file's own rule — *never publish a safety-cost
  claim without R3* — was broken by the person who wrote it, one pattern later.
- **"gcc is 36% behind clang on p16"** — a flag default, not a codegen limit.
  With `-funroll-loops` gcc reaches 2823 and **beats** clang's 2993. Reproduced on
  p17: 7065 → 4813, past clang again.
- **"The cost of the check is the conversion, not the comparison"** (manager's
  prediction for p17). False: `i128` index arithmetic costs +4.0000 Ir/byte, but
  **signedness itself is 4 Ir per call, flat — 0.17% of the gap.**
- **"The twin's value accrues from p17 on"** — p17's accessor is single-clause
  too, and for a structural reason: its interesting harm is not a memory error.
  The twin's value starts at the first *multi-clause trusted accessor*, a property
  of the wrapped intrinsic (p27+), not of the pattern number.
- **"p17's leak is an information disclosure"** — as shipped it is not; the excess
  bytes are the attacker's own request table. Corrected to a *slice*-relative
  guard, which does disclose a neighbour window. See finding 10.
- **"`scaling_cur_freq` shows the clock"** — it reported 800 MHz for six seconds
  while the core ran at 3.80–3.89 GHz. Measure the clock with a dependent chain,
  interleaved — and even then it spans ±15% within one session.
- **"On a vectorised loop the bounds check costs 0.0000 Ir/element"** and **"the
  wider the lane, the cheaper safety gets"** (p05, manager). The first is true
  only of the vector steady state — the check is hoisted into a per-row
  trip-count computation and survives in the scalar epilogue, an `O(nrow)` cost.
  The second is **refuted**: at AVX2 the gap is 4.58× against SSE2's 1.42×.
- **"`chunks_exact` refutes p05's R3 cost"** (TASK_014_REVIEW's blocker, which
  the manager landed as a retraction). **The retraction is itself retracted**:
  `chunks_exact` is forbidden by p05's own `spec.md`, so it measures a different
  kernel. p05's `6·nrow + 9` stands **as a contract-relative number**. What does
  not stand is reading it as "what safe Rust costs" — finding 14.
- **"Safe Rust beat unsafe Rust"**, and its repair **"p05's idiom-matched safety
  number is +11.00 Ir/call, flat, `O(1)`"**. One more unsafe round makes it
  `nrow + 9`. Both spellings were out of contract. (This entry used to add "and
  `inf(R4) <= inf(R3)` holds by construction anyway" — **that half is itself
  retracted at TASK_025_REVIEW**; see finding 14. The retraction of "safe beats
  unsafe" stands on the out-of-contract ground, which is the measured one.)
- **"`inf(R4) ≤ inf(R3)` by construction, so safe-beats-unsafe is never available
  as a language fact"** (manager, offered as "a reason available without
  measuring", carried for six patterns in three files). **All six patterns pin
  `identity: unsafe ≡ verus, O3 exact`**, so an R4 must have a byte-identical R5
  that Verus verifies: R4 is bounded by what vstd can express and R3 by nothing.
  The classes are **incomparable**. Measured on p16 — the same fold is admissible
  as R3 at zero TCB and needs five trusted items as R4. See finding 14.
- **"Compare idiom-matched rungs"** (manager, one turn after inventing it).
  "Same idiom" has no fixed point; its members differ by `O(nrow)`.
- **"p17's R3 costs +32 Ir/call, flat"** — flat *per byte*, not per call. Both
  published bands happen to have `nsuf = 3`; swept, `R3ship − R4` runs 18…63.
  p17 ships no sweep inputs, which is how a two-point constant became a law.
- **"p16's R3 cost is O(1) per call"** — `7 + 5·nrec` at `vlen ≡ 0 (mod 4)`,
  `7 + 7·nrec` otherwise. `O(nrec)`, and the two published points were nrec 4
  and 10.
- **"Overlap UB is not caught by ASan"** (manager, in the catalogue since it was
  written). It is caught — `memcpy-param-overlap`, exact to the byte — unless
  the call site is fortified to `__memcpy_chk`, which blinds ASan under clang as
  well as gcc.
- **"The bug is not expressible at R5"** (p08's own README). It is, and it
  verifies clean: a proof of a `requires` is not a proof that the trusted body
  honours it.
- **"p08 undermines p05's nonlinearity claim"** (manager, TASK_014_REVIEW Part 3).
  Refuted with disassembly: p08's retained check is blocked by a *relational*
  deduction, not a nonlinear one, and p05's linearisation counterfactual goes the
  manager's way. p05's cost claim fell for an unrelated reason.

## Working method

See `.tasks/PROTOCOL.md` for the full rules. The short version: manager writes
specs and `.memory/`, one subagent at a time alternating engineer → reviewer,
manager lands `.memory/` corrections and commits.

**Do not write a finding into `.memory/` before its review lands** —
`.tasks/PROTOCOL.md` rule 9. Four consecutive reviews caught the manager
overclaiming, every time from the same cause. Engineer writes `NOTES.md`, manager
commits it, reviewer attacks it, *then* `.memory/`.

**Ask to be corrected, not obeyed.** Every agent that has contradicted the
manager's written instructions with a measurement has been right. Two were
prescriptions that could not have worked at all; one overturned three premises in
a single review; p04's engineer refuted three of the manager's prescriptions in
one task. Say so in every task file, and **name the call you are least sure of**.
⚠ **The running count lives in one place — the closing paragraph of the newest
`.tasks/TASK_NNN*.md`** — because it was duplicated here and in `PROTOCOL.md`
and both copies went stale (13 and 7 against the task files' 55).

## The recurring traps

- **A green gate is evidence about the gate.** Four reviews found defects past a
  fully green run, twice with an unchanged contract hash.
- **A vacuous truth in a log reads like a discharged obligation.** Six instances of
  "every X is Y" printed over an empty collection. Now a rule: a count-bearing
  success line prints its `n`, and `n == 0` fails.
- **Checks fail open.** Three times a malformed mutant that failed to *compile* was
  read as "the check passed".
- **Declared pins are self-certifying** — they move in the same commit as the code
  they constrain. Derive where possible; the Miri cross-check and the new
  callgrind "did this code run" check are the models.
- **Residues.** p01 tripped mod 4 three times; p02's real modulus was 16. Sweep two
  full cycles; never sample two points.
- **Attribute nothing without decomposing.** Change one loop at a time. This is
  what killed the O(n) claim.
- **Say which columns a staleness argument covers.** "The kernels are identical so
  the numbers stand" was right about kernel columns, wrong about whole-binary ones.
- **Residues bite at whatever width the codegen chose, and the round numbers are
  the worst case.** p01 mod 4, p02 mod 16, p16 mod 4, p05 mod 8 with **residue 0
  the outlier** — so every power-of-two dimension pays a full extra vector
  iteration. The size a benchmark author reaches for first is the trap.
- **`ns` is a measurement on this box; `cycles` is an inference.** The clock is
  set by other tenants and spans ±15% even measured interleaved in one session.
- **A finding needs a mechanism, not just a number.** "It vanished" was p05's
  first answer; the real one was a hoisted trip-count computation and a surviving
  scalar epilogue, and it changed the conclusion.
- **You are measuring a spelling until you have written two — and then you are
  still measuring a spelling.** Three retractions (p02, p16, p05) came from one
  plausible R3 published as what *safe Rust* costs. Writing a second spelling
  does not fix it: on p05 the spread across eleven exceeds the safe-vs-unsafe
  gap, and the unsafe rung has spellings too. Only a matched pair under a
  **declared, pre-registered** idiom carries a safety number (finding 14).
- **Read the pattern's `spec.md` before believing a cross-pattern rule.** Two
  consecutive tasks measured spellings p05's `spec.md` forbids **by name**, in a
  section titled "Load-bearing, do not improve", and neither cited it — because
  `.memory/01-ladder.md`'s R3 definition listed the forbidden spelling as a
  technique. A general file and a pattern file disagreed and the general one
  won twice.
- **A tool that reports nothing may be a tool that cannot see.** ASan is silent
  on p08's overlap not because there is none but because fortify rewrote the call
  to `__memcpy_chk`. A gate row records `clean` for both reasons identically.
- **Two files, two numbering schemes** — now with a **map** at the head of the
  findings list, which is the fix this entry asked for three times. Name the
  pattern, never the number.
  **And one task file is misnumbered**: `.tasks/TASK_025_REVIEW.md` reviews
  **TASK_024**, not TASK_025 (there is no TASK_025). Every other
  `TASK_NNN_REVIEW` reviews `TASK_NNN`; `TASK_027_REVIEW` restores the
  convention. Cite reviews by what they *found*, not by their number.
  (This file also *shipped findings 13 and 14 twice*, with divergent text, from
  an insert-where-a-replace-was-meant. One copy asserted p05's `5·nrow + 6`
  floor as a narrowing result while the other recorded its refutation. Deduped
  and merged 2026-08-18. When you edit a finding, `grep` its opening words first.)
- **Never publish a bare per-byte rate, or a difference of rates across unmatched
  spellings. Publish only matched-spelling differences.** (TASK_024,
  TASK_025_REVIEW — the answer to "is K-dependence a finding or a surrender" is
  *both*, split.) A bare rate is **not a property of the kernel**: p16's ranges
  5.04688 … 6.62500 in contract, one exact-string substitution apart, and is not
  even measurable past ±0.01 because the driver's `println` term does not cancel
  within a binary. So p16's 5.7500, p17's 10.0000/5.7500, p05's 1.375000 and
  finding 11's 4.25 are all quoting a free parameter. A **cross-spelling
  difference** of two such rates is worse — that is exactly what −0.65625 is, and
  it reached four files as a headline with the wrong arithmetic on top. But the
  **matched-spelling difference is a property of the kernel**: 0.0000000 Ir/byte
  over 127 consecutive lengths × 6 spellings, with the mechanism visible. Note
  what this means: **the rule TASK_024 adopted — "name the fold beside the rate" —
  does not catch its own headline figure.** A mechanical backstop was costed at
  ~90 lines (`spec.md` pins the shipped fold's chunk-body instruction count;
  `check.py` asserts `body_len / K` equals the published rate) and is **not yet
  proposed as gate work** — it would have to pass "could this happen by
  accident?" first, and it has happened by accident twice.
- **A cited artefact can refute the claim it is cited for.** `.temp/p24/foldbody.py`
  is named in p16's `NOTES.md` as the evidence for mnemonic identity; re-run as
  committed it prints `identical=False` at every `K`. The claim is *true* — a
  reviewer re-derived it — but for a year nobody would have known which. Re-run
  the artefact, do not cite it.
- **Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
  variant.** Every `identity`-pinned rung is chained to the prover, so an
  unsafe-side "cheaper spelling" that vstd cannot express is not a rung and its
  number means nothing. This one check would have caught p16's `u_c32`, p16's
  `r4_hdr`, p05's `c4_hu16_nz`, p05's `r4_dataslice` and both endpoints of p05's
  published pair interval — five published figures, across two patterns, over
  four tasks. It costs about eleven minutes.
  **And read the error text, not the exit code**: `is not supported` disqualifies
  (it forces a new *trusted* item); *"postcondition not satisfied"* disqualifies
  nothing — measured on p05, the same exec code went from `11 verified, 1 errors`
  to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB.

## Priority — read this before planning

**Fifty-six tasks in, 16 of 47 patterns exist**, and the ratio is the thing to
watch. Six tasks went to gate hardening before the user called it; **T015–028 —
thirteen consecutive tasks — went to the spelling problem** and produced no new
pattern. Both arcs paid for themselves, and neither was on anyone's plan. But the
honest reading is that **this project is better at discovering its own numbers are
wrong than at producing new ones**, and the correction is simple: **alternate
build → review, and make a methodology proposal argue for itself against a
pattern.**

**Since T033 the loop has held** — p11, p03, p09, p12, p04, p13, p06, p14, p18
each built and reviewed, every one green on its first complete run, and every one produced a
finding no one predicted. That is the working mode; do not drift off it.
⚠ **The last five each needed a THIRD task to land their corrections** (T044, T046,
T048, T050, T052), and all five were worth it: p04's review moved its headline number,
p13's reversed its headline's sign, and p06's corrected two published laws and a
`.memory/` claim that had stood since TASK_004. **Budget build → review → land,
not build → review.** Three tasks per pattern is the real cost; plan with it.

The gate's threat model is **honest mistake, not malicious author**
(`.memory/02-bench-rules.md`, top section, with the residuals deliberately left
open). **New gate work must pass "could this happen by accident?" first** — and
`check.py` is ~5460 lines against 19 patterns, so the next gate proposal should
have to beat that ratio.

**Review each pattern once; do not review each fix to each check.** The two
highest-yield review targets, measured across every review so far: a claim the
engineer *flagged against itself*, and a mechanism asserted without a control.

## Immediate queue

**`TASK_055_REVIEW` is the next task, and it is already written.** See the START HERE
box; this section is the standing backlog, not the next action.

⚠ **The concurrency rule, so it is not read as blanket licence.** One agent at a
time is the default. It is relaxed **only** for work that touches neither
**measurement** — concurrent CPU load corrupts a `ns` column, and two timing jobs
corrupt each other — nor **gate JSONs**, which `check.py` rewrites in place.
`TASK_058` qualifies because it is forbidden from executing anything at all.
`TASK_055_REVIEW` does **not** qualify: it runs valgrind and Verus. Deterministic
`Ir` under callgrind is immune to contention; wall clock is not, and the failure
is silent.

### CLOSED at TASK_053–056 — history, not work

The gate audit swept all **18** stages and found **6** defects; every one is now
fixed or declined with a reason, on a tree that re-ran 16/16 green.
**Do not re-open these:** the second sanitizer hole (F3) is **fixed**, and **every
sanitizer row carries `stdout`** — 114/114 when that was written against 16
patterns, **135/135 re-verified at TASK_066 across 19**; the invariant is the
*zero missing*, not the count; the tautology battery (F2) no longer lets an aborting
tactic overwrite a real verdict; the adversarial key (F1) records all behaviours
with their cells; the comment-in-a-clause bypass (F4) is repaired in `vparse`;
`forbidden_hits` (F6) was **declined** and is now **RE-OPENED** (TASK_062 found a real defect it could see; TASK_063 settled the defect and recommends **fail, batched** — `.memory/02-bench-rules.md`, PROVISIONAL). It was recorded as a known residual with the
measurement. p12's, p03's, p04's, p05's, p11's and p18's sole-catcher prose is
corrected; p08 is TCB 4 → 3 with `identity: exact` at both levels; `limbs.py`
lives in `harness/`; the `.partial.json` trap is gone (they now write to
`.temp/gate-partial/`).

✅ **Clean negative, TASK_066: this section re-verifies.** After item 6 below
turned out to have been closed by a command that matched prose, four of this
list's checkable claims were re-derived from the tree — `harness/limbs.py`
present, **no `.partial.json` under `results/`**, **135/135 sanitizer rows carry
`stdout`**, **p08 `tcb_items` = 3** (`move_right`, `load_input`, `emit`). All
four hold. **The CLOSED list is trustworthy; item 6 was the anomaly, and it was
in "Owed", not here.** Do not re-run this check.
⚠ **`O3d` was built, measured inert, and REVERTED** — see
`.memory/03-measurement.md`: `build.py` is hashed into the *measurement* records
too, so landing it costs a full re-measure and would churn ten patterns' timing
prose. **Land it bundled with a pattern that is being re-measured anyway.**

**New, from p10's cycle:**

- **p10's R4-side span is a LOWER BOUND ON ITS OWN WIDTH.** `u_win` is the
  cheapest admissible R4 found (194.00 / 362.00 below shipped), but it carries a
  panic pad, so `identity: exact` excludes it. **Nobody has looked for an R4 that
  is both cheaper and PAD-FREE**, which is the one that could actually ship.
- **p10's `-O3 whole` laws have no registered out-of-sample test** — band `e` was
  registered for the `isolated` column only, so for `whole` it is an ordinary
  hold-out.
- **p10's whole-mode per-output coefficients are not decomposed** mnemonic by
  mnemonic, and its padding caveat applies to them.
- **`u_win` was never run through `check.py` as a rung** — its `required`
  spellings were checked by reading.
- **`measure.py p10` was re-run at TASK_059** (comment edits touch
  `source_sha256`). Every deterministic metric was diffed and is identical; the
  wall column moved ~8% and one cell now trips the 10% spread threshold.

**Still open, from p18's cycle:**

- **p18's controls were never re-swept over its new band `t`** — `t_1step`,
  `t_chain`, `t_iter`, `t_pos`, `t_wshl`, `t_cshl`, `c_mask`, `c_ncap`,
  `c_reject`, every `*_noguard` rung and every `O0d`/`O3d` law are still
  `cut = brk = 0` laws. **p18's own largest remaining gap**, recorded in its §8d
  and §12. `cut`/`brk` are also `-O3 isolated` only.
- **p18 publishes no pair interval and its R4 side is unsearched in contract**;
  its `R3 − R4` is a fixed-R4 reading only. Same standing gap as p01 and p08.
- **p18 has no `ns` figure for R2 or R3** (no layout population for the safe
  cells), and its `large` `ns` row is weak (P = 0.676 / 0.829) and quoted with
  its P.

**New, from p14's cycle:**

- **No C or safe-Rust cell on p14 has a layout population**, so its whole `ns`
  column stays **withdrawn rather than filtered**. `c-clang-h − c-clang`
  (+18.21%) may well survive one. `controls/clayout.py` now ships on both p06
  and p14; porting it is cheap.
- **p06's `adversarial-past48` `c-clang` stdout moved between BUILDS**
  (`497` → `6008526198855114936`), and the same binary prints `497` on three
  consecutive runs. p06 §7 records that cell as `0, 497`. The `c-gcc` instability
  beside it is documented (six observations); **this one is new and undocumented,
  and build-varying is a different mechanism from run-varying.**
- ✅ **THE LIFETIME PATTERN IS UNBLOCKED AND UNBUILT — the biggest open
  opportunity here, and it is now the NEXT ACTION.** `vstd::raw_ptr` works
  (TASK_055, **reviewed at TASK_055_REVIEW**): a heap kernel verifies with **zero
  project-local trusted items**, and the ghost split loop the probe never
  wrote — the one thing the whole pattern was blocked on — verifies **7/0** at
  **150 ms**, with the **identical rlimit** at `n <= 1_000_000`, so the slot
  count is free. p14's rejection reason is refuted (`add`/`offset` unsupported,
  **`addr`/`with_addr` supported**); stack locals are out
  (`SharedReference::new` is private). Formulation: a **slab with pointer
  handles at R4/R5 and `(slot, generation)` at R1h/R2/R3**, so safe Rust's cost
  is a **representation change, not a check** — an axis this project has never
  had.
  ⚠ **Three measured constraints, all in `.memory/04-verus.md`, none fatal:**
  the UAF must live on **adversarial inputs only** (at `-O3` the stores into the
  recycled slab are **dead-store-eliminated**, so that row does not execute the
  bug and the checksums disagree across `-O` level — the offset-16 fix was
  necessary and **not sufficient**); **`dloop.py:361` raises on rung-signature
  arity**, and the one escape measured to work is a **dead `slab` argument** on
  R4, whose `-O3` survival is unmeasured; and the R5 catcher is an **ordinary
  SMT obligation, not linearity** — that claim is retracted.
  ⚠ **TCB counting is SETTLED**: the manager's `tcb_reach` column was proposed,
  attacked and **rejected** — keep one number, add prose, and the residual is
  live and named.
- **p14's `-O0` rows are unexplained** (R3 dearer than R2 there, sign inverting
  at `-O3`) and **clang's `R1h − R1` law is unsolved** — mechanism and mnemonic
  table only, no closed form. No claim rests on either.

**Closed by p06:** the two-step reslice (old item 1) is now measured on a sixth
pattern at **exactly −1.00 Ir/call**, and p06 shipped the first
**length-heterogeneous** fit set (old item 11), whose leave-one-`m`-out **can
fail** — it misses by −48.000 at `m=3`, which is how the domain got established.
Both retired.

**New, from p06's cycle:**

- **`b_nored`'s Verus failure is a resource-exhaustion, not an obligation**, and
  `--rlimit 30/60` does not convert it. A mutant that dies of rlimit is a weaker
  control than one that fails on a named obligation, and the pinned counts hide
  the difference.
- **p02 keeps a trusted wrapper it does not strictly need**, with the price now
  measured (`+5.00 Ir/call`, one extra panic pad, breaks `identity: exact`). Not
  a defect — the hard stop working — but someone will ask why p06 removed one and
  p02 did not.

### Owed, in priority order

1. **The two-step reslice is untried on most patterns**, and most patterns' R3
   opens with the window reslice it improves. It costs zero `unsafe` and zero
   TCB, and its mechanism is register allocation rather than bounds-check
   removal, so it is *not* the lever any prior spelling search ran. **One
   substitution per pattern, gate re-run, no re-measurement of anything else.**
   `.memory/01-ladder.md` finding 3 carries the spelling and the mechanism.
   ⚠ **Do NOT quote "−1 `Ir`/call, confirmed on seven patterns" — the manager
   did, and it levels two very different pieces of evidence.** On p04 the
   −1 was **20% of the whole published tax**. On p10 it is **one instruction**
   (3268 against 3269), which `.memory/03-measurement.md` requires be called
   **instruction-count-only and stopped there** — it does not retire this item
   on its own, and TASK_059 retracted the claim that it did.
2. **p03's span rests on one unreviewed measurement.** TASK_037's `a_tail` is
   swept (`maxres 0.000000`, 19 blobs) and its admissibility comes from the gate's
   own decidable matcher, which is why it was landed — but it refuted a number a
   review had just confirmed. **And the `+5` per-call constant has never been
   searched at all**; it is the whole remaining gap between p03's two class
   minima, and the belief that safe Rust must pay it is an argument, not a
   measurement.
3. **p01 and p08 owe an in-contract R3-side span.** Do **not** let either publish
   a pair interval — both this project published were built from R4s that are not
   rungs — and never the word "minimum"; write "cheapest found" and name the
   input, because on p03 and p16 the cheapest spelling changes with it.
4. **p17 ships no sweep inputs**, which is how its "+32 Ir/call flat" was
   published from two bands that both had `nsuf = 3`. A `sweep-*` band appended
   last costs **one gate re-run, not a re-measure** (`.memory/05-layout.md`).
5. **`check.py`'s `harness/*.py` glob is over-broad** — it imports five modules
   but hashes all of them, so a `measure.py` edit costs eight gate re-runs (13 min
   measured) for a file the gate never executes. Judgement call; belt-and-braces
   cannot under-cover.
6. ⚠ **RE-OPENED at TASK_066. It was marked ✅ CLOSED on the strength of a
   command that cannot tell the hash from a sentence ABOUT the hash.**

   The item claimed *"every pattern record now carries `source_sha256`; the only
   file without one is `results/p02-residue-sweep.json`, a side record"*.
   **Measured today: six files lack the top-level key, five of them real
   patterns** — `p02-buffer-copy`, `p05-index-flatten`, `p07-binary-search`,
   `p11-nul-scan`, `p17-http-range`, plus the side record. That is the *original*
   count this item said the re-measures had cleared. **Nothing was cleared.**

   **The mechanism, and it is worth remembering.** The closing one-liner was
   `'source_sha256' not in open(f).read()` — a substring search over raw text. In
   all five files the string occurs exactly once, inside `/git/note`, in a
   sentence advising *"Use `results/gate/*.json`'s `source_sha256`"*.
   **The note telling you where to find the hash is what convinced the checker
   the hash was there.** Third instance of TASK_065's lesson: *a wrong command is
   worse than a wrong constant, because it looks self-verifying.* Parse the JSON:

   ```bash
   python3 -c "import json,glob;print([f for f in sorted(glob.glob('results/*.json')+glob.glob('results/gate/*.json')) if 'source_sha256' not in json.load(open(f))])"
   ```

   **What it actually means — and it is narrower than it sounds.**
   `measure.py --check-stale` prints `NO BASELINE` for those five and **does not
   count them as `bad`**, so the run says `38 record(s) examined, 0 STALE` and
   **exits 0**. ⚠ **"0 STALE" is therefore not "everything is verified"**: five
   of nineteen *measurement* records cannot be checked by hash at all, and they
   include **p02 (the project's strongest security result)** and **p17**.
   ✅ **Mitigating, and verified: all 19 GATE records DO carry `source_sha256`**
   — which is exactly what that `/git/note` sentence is pointing at. So the gap
   is in the **measurement layer only**, and provenance for those five exists one
   file over.

   **The fix is a re-measure of those five**, which is the expensive operation
   (settled answer 4) and must not run concurrently with anything. Queue it
   behind pattern work; do not let it displace a pattern.
   ⚠ The old sub-claim that `p11-nul-scan.json` was *"recorded stale on
   `bulk_calls`"* is **not checkable as written** — with no baseline there is
   nothing to compare — and p11's `bulk_calls` are populated today
   (`memchr@plt` on the C rungs). Re-derive it after the re-measure, or drop it.
7. **p04's `small` R2 layout population is bimodal at 1.42× and unexplained**
   (TASK_042_REVIEW minor 8): 27 layouts at 6.43–7.17 ms, four at 9.30–9.88 ms,
   reproducible across both passes, and **neither `analyze.py`'s `(loop,
   property)` pairs nor `addr%32` separates it**. All four outliers are `order|*`
   builds and are among the *fastest* on `large`, so a startup-side effect is
   plausible. Finding 16 says every layout mode found so far is `win32` or
   `jcc32`; **this one is neither**, and it is the first counterexample to that.
   It does not move a published verdict (the mode-matched `R2 − R4` figures agree
   with the shipped ones), so it is a curiosity — but it is a *named* one.
8. **p13's `controls/library_axis.py` deliberately keeps the OLD narrow fold**,
   because `strlcpy`/`snprintf` do not zero-fill and a full-extent fold would
   make the six routines print six checksums for a non-cost reason. Its *levels*
   are therefore not comparable with p13's §4; every *difference* inside it is.
   Documented in the control — but it is the only place in the tree where two
   folds coexist, so check it before quoting across the boundary.
9. **p13's corrected wall-clock ratios (+7.64 / −5.39) do not clear the ±9-point
   bar**, so its quotable timing evidence is the raw *level* under the
   identical-copy protocol. Not a defect — the rule working — but it means p13
   has no corrected-ratio row and someone will look for one.
10. **`check.py::spelling_matches` does not blank `#[cfg(slb_twin)]` bodies**, so
   a Verus rung's idiom audit can be satisfied by code no build contains
   (constructed instance `False → True`). **Blast radius on the shipped tree is
   0 of 15 pins**, so it is hygiene, not a live defect — and it must pass "could
   this happen by accident?" before it becomes gate work.
11. **A length-heterogeneous sweep band is what a step-basis test actually
   needs**, and no pattern has one. p13's fit blobs are all length-homogeneous,
   which makes every natural step basis *singular* — so p13 could not have
   fitted the step law even if one exists. Whoever next hits a size-dispatched
   library routine will need this.
12. **`check.py:NNNN` citations in the PATTERN docs have decayed — 22 of them
    across 12 patterns**, audited at TASK_066 and **not yet fixed**. The
    `.memory/` half *is* fixed (5 of 9 were wrong; the convention and the audit
    aid are at the end of `.memory/02-bench-rules.md`). Spot-checks: p04 and p09
    `spec.md` cite `:929`, now a **blank line**; p05 and p17 `NOTES.md` cite
    `:1446`, now `return {}`; p10 cites `:1254-1292`, now an unrelated comment.
    **Not all are wrong** — p47's `:1755-1760` is still right, and the newest
    patterns' citations are the healthiest, which is the drift signature.

    ⚠ **DO NOT do this as a standalone task, and the reason is a scheduling
    fact worth keeping.** A pattern's gate record globs **`pdir/*.md`**
    (`check.py:5197`), so editing any `NOTES.md`/`README.md`/`spec.md` makes
    that gate record STALE — 12 gate re-runs. But `measure.py`'s `provenance()`
    (`:226-235`) does **not** glob `*.md`, so **it costs no re-measure at all.**

    > **Batch it with the `check.py` edit** that is already owed —
    > `forbidden_hits` fail-vs-print plus p22's per-input timeout
    > (`.memory/02-bench-rules.md`, `.memory/06-catalogue.md`'s p22 triage).
    > That edit stales **every** gate record anyway via the `harness/*.py` glob
    > (item 5 above), so the doc fixes ride along for free.
    > ⚠ **A FOURTH joined the batch at TASK_066_REVIEW and it is one line**:
    > stage 7 builds C at `-O1` **without `-fstrict-aliasing`**, so it cannot see
    > a flag-gated UB class. **It is one flag wide, not one opt level wide** —
    > adding `-fstrict-aliasing` at `check.py:4738` makes stage 7 see p38 at
    > `-O1` (ASan `stack-buffer-overflow READ of size 2`). **Blast radius
    > measured across all 20 gate records: exactly one pattern.** 16 patterns
    > declare a `fires` input and **all 16 already fire at `-O1`**, p18 included.
    > ⚠ Do **not** raise stage 7's optimisation level instead — that perturbs 20
    > patterns to fix one.
    > **Four owed changes, one sweep.**

    ⚠ **Extend the doc sweep to CONTROL NAMES while you are in there.** Same
    class, found by the same review: `s_asan_O3` is cited in **three** committed
    p38 files (`NOTES.md`, `model.py`, `spec.md`, hence its generator) and
    **does not exist** — the `-O3` ASan build is anonymous inside
    `do_sanitizers()` and cannot be selected by name. **A doc referring to a
    control nobody can run is PROTOCOL rule 10's failure inside the hashed
    layer.** No cross-pattern audit has been done; control registries are
    heterogeneous (p38 a dict plus hardcoded prints, p47 a `VARIANTS` list), so
    it wants `--list` per pattern rather than a grep.

13. **There is NO cross-pattern synthesis, and that is the project's stated
    purpose.** 20 per-pattern tables under `results/tables/`, nothing that
    compares them — while `CLAUDE.md` describes the project as patterns
    *"compared on assembly, instruction count, timing, proof burden and
    trusted-base size"*. A working aggregation probe exists at
    **`.temp/synth/aggregate.py`** (kept per the keep-the-generator rule; it
    reads only committed records, runs in seconds, and needs no measurement).

    ⚠ **It must NOT live in `harness/`** — `check.py` hashes `harness/*.py` into
    every gate record (`check.py:5200`), so a file there stales all 20 gates for
    a script the gate never executes. `common/` and `common/layout/` are hashed
    too. Pick the location deliberately.

    **Three things it already exposes — all PROVISIONAL, none reviewed:**

    - **`R5 − R4 = 0.00` on all 40 rows**, both inputs, every pattern. The
      `identity: exact` invariant, visible whole for the first time.
    - **`R3 − R4` is NEGATIVE on 5 of 20 patterns** — p10 (−323/−603), p11
      (−5768/**−24503**), p12 (−26 large), p13 (−177/−1054), p18 (−25/−12). So
      *"safe tuned Rust is dearer than unsafe"* fails on a quarter of the tree.
      ⚠ **Do not quote that as a result.** Several of those patterns have an
      **unsearched R4 side** — the trap in the START HERE box — so the sign may
      be an artefact of R4's spelling. **What the aggregate genuinely adds is
      making that a systematic problem rather than a per-pattern footnote.**
    - ⚠ **A cross-pattern `Ir` comparison is available in `isolated` mode ONLY.**
      Measured: of 318 `-O3` cell/input pairs, `whole` mode has
      `kernel_exclusive_ir = None` in **302** — the kernel is inlined and has no
      symbol. Since **p10 showed regressors SWAP between modes**, any synthesis
      can only ever speak for the mode where that swap was observed. **State that
      limit before the first number, not after the table.**

### Deferred with a stated reason

- **The mechanical rate-vs-disassembly backstop** (~90 lines, prototype exists).
  Deferred twice, and the second time the engineer's own session was the argument:
  every defect that actually occurred was a class-membership or arithmetic error
  no `body_len / K` assertion would catch.
- **`harness/check.py:1766`'s display string** (stage 3c's `head()`; cited as `:1753` until TASK_058) still says "recorded as a result";
  the comments beside it were corrected. Free to fix on any task that already
  re-runs all gates.

### Closed arcs — history, not work

- **Gate hardening** (T001–T010). Closed by the user's call.
- **The spelling arc** (T015–028, thirteen tasks). Produced the named-spelling
  standard, four refuted floors, p16's sign error, and the
  **R4-is-chained-to-the-prover** result. Its distilled rules are
  `.tasks/TASK_026.md` §0 — **the shortest statement of what this project knows
  about reporting spellings, and worth reading before writing any task file.**
- **The layout arc** (T026 → 029 → 030_REVIEW → 031). Produced finding 16 and
  `common/layout/`.

## State

**Verified at this handoff** — re-run these four before trusting anything below:

```bash
harness/measure.py --check-stale          # the invariant is "0 STALE"; the record
                                          # count moves with every pattern added
harness/check.py p13                      # or any pattern; every one is green
grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
  | sort -u | while read f; do [ -e "$f" ] || echo "MISSING: $f"; done
# the shared named-spelling paragraph must be ONE hash across all patterns:
python3 -c "import hashlib,glob;print({hashlib.sha256(open(f).read()[open(f).read().find('NAMED-SPELLING STANDARD'):open(f).read().find('p01 and p08 neither')+19].encode()).hexdigest()[:12] for f in glob.glob('patterns/*/spec.md')})"
```

- **Every pattern green**: p01 is `PASS-WITH-BLOCKED-ROWS` (Miri policy on its
  `large.bin`, documented, not a regression) and **every other pattern is
  `PASS`, with 0 failures tree-wide.** ⚠ **A list of pattern names used to sit
  here and it went stale twice.** Print it:

  ```bash
  python3 -c "
  import json,glob
  for f in sorted(glob.glob('results/gate/*.json')):
      d=json.load(open(f))
      print(f.split('/')[-1][:-5], d['verdict'], len(d.get('failures') or []))"
  ```
- **The shared named-spelling paragraph is byte-identical across every**
  `idiom.why` block — currently one hash, `59748cce2db5`, 11 003 bytes.
  ⚠ **The value depends on how you slice the span**, so trust the *command*
  above (all patterns equal) and not a copied constant: this line previously
  recorded `c3d36c92a28a` for the same intact invariant, measured over a span one
  byte longer. **What matters is that the set has size 1.**
- `harness/` — `check.py` (**18** stages; this line said 17 and
  `.memory/05-layout.md` said 16 — enumerate them with
  `grep -o 'head("[0-9][^"]*"' harness/check.py | sort -u | wc -l`, do not copy a
  constant. ⚠ **The `sort -u` is load-bearing and the first version of this
  command lacked it**, returning 19: `head("1. build the matrix")` appears
  **twice**, two entry points into one stage. TASK_058 caught
  it — a command that is wrong is worse than a constant that is right, because it
  looks self-verifying. ⚠ The two line numbers written here were `:1218`/`:4903`
  and had drifted to **`:1404`/`:5104`** by TASK_066 — **which is the point:
  the command is still right, and the constants beside it rotted.** Run
  `grep -n 'head("1\. build' harness/check.py` rather than trusting either),
  `asm.py`, `dloop.py`, `vparse.py`,
  `build.py`, `measure.py` (now writes `source_sha256` + `input_sha256` and has
  `--check-stale`), `report.py`, `fixture.py`. `common/layout/` ships the layout
  harness and `common/layout/data/` its p01 population, so finding 16 is
  **auditable without re-measuring**.
- **Reports exist for every task whose report is cited.** Six recent tasks
  (T036, T038–T042) have **no `_REPORT.md`** — nothing cites them, and their
  content lives in the commit messages and the patterns' own `NOTES.md`, which
  the gate hashes. **Write one before citing it** (PROTOCOL rule 10); that rule
  exists because the manager once cited a report it never wrote.
- **Toolchain**: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6,
  valgrind 3.27.1, nightly+Miri, all in `~/tools`, no root. `TOOLCHAIN.md`.
- **Gitignored blobs outside `.temp/`**: `patterns/*/inputs/*.bin`. All
  regenerable from each pattern's `inputs/gen.py`, all verified deterministic by
  regenerate-and-diff. `rm` outside `.temp/` stalls on review, so they are the
  user's call.
- **`.temp/`** is scratch and is swept periodically. ⚠ Read
  `.memory/00-environment.md` constraint 6 **as it now stands** — its first
  written form was destructive.
- **Commits run through the p04 landing. Tree clean.** ⚠ **A GitHub remote exists
  (`origin`, `HALOCORE/sec-ladder`) and the local branch runs ahead of it. Do not
  push unless the user asks.**

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
