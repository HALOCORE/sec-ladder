# The ladder — five rungs, precisely defined

Every pattern is implemented five times. The rungs must be **semantically
equivalent on well-formed input** (same checksum) and differ only in what
enforces memory safety.

| Rung | Dir/file stem | Definition |
|---|---|---|
| **R1 C** | `c/` | Idiomatic C99. No bounds checks. Written the way a competent systems programmer writes it — *including* the bug class the pattern is about, if the pattern models one. |
| **R2 safe-naive** | `safe_naive.rs` | The mechanical port a working Rust programmer writes first: `for i in 0..n { ... v[i] ... }`, indexing, `Vec`, no cleverness. Must contain **zero** `unsafe`. |
| **R3 safe-tuned** | `safe_tuned.rs` | Same semantics, rewritten to help LLVM elide checks: iterators, `chunks_exact`, `zip`, slice reslicing, `split_at`, hoisted length assertions. Still **zero** `unsafe`. |
| **R4 unsafe** | `unsafe.rs` | `get_unchecked`, raw pointers, `from_raw_parts` — whatever it takes to reach C's codegen. Unsound-by-inspection is not allowed: it must be *correct*, just unverified. |
| **R5 verus** | `verus.rs` | R4's exec code, plus Verus specs and proofs discharging every unsafe precondition. Ships the same machine code as R4. |

### R1h — the hardened C cell (optional, added at TASK_004)

| Rung | Dir/file stem | Definition |
|---|---|---|
| **R1h C-hardened** | `c/kernel_hardened.c` | R1's kernel plus the bounds check a careful C programmer writes. Same signature, same calling convention, same driver — the *only* difference is the check. |

**Ship it for every pattern that models a bug.** With only R1, "C is faster" and
"C is unsafe" are the same sentence, because C is faster precisely in that it
skipped the check. R1h separates them:

- R1 vs R1h = what the check costs, **inside one language**
- R1h vs R4 = what Rust's unsafe rung costs against *safe* C
- R1h vs R2/R3 = what Rust's additional machinery costs beyond the bare check

`harness/build.py` creates the `c-gcc-h` / `c-clang-h` cells for any pattern that
ships `c/kernel_hardened.c` and for no other — presence of the file is the
switch, there is nothing to declare. A pattern with R1h builds 32 cells, not 24.
Use `buildmod.measured_cells(pdir)` / `all_cells(pdir)`, never the module-level
`MEASURED_CELLS` / `ALL_CELLS`, which exist only for argparse.

Measured on p02 (`-O3`, marginal Ir per call, both `small` and `large`): the
check costs **+5 instructions with gcc and +12 with clang, per call, independent
of the size of the copy** — 2.2% and 5.4% of the call on the L1-resident input,
0.05% and 0.12% on the memory-bound one. So the headline p02 supports is *safety
costs about the same in both languages, and Rust makes it non-optional*, which
is a much stronger claim than any p01 could produce.

## The structural findings (established by `pilot/`, do not re-litigate)

1. **A Verus proof costs zero instructions.** Ghost code, `requires`, `ensures`,
   invariants, `decreases` all erase. Established at the pilot, corrected at
   TASK_001, and independently re-derived at TASK_001_REVIEW **on the raw
   machine-code bytes** — the only oracle that can establish this (normalised text
   collides; see `.memory/03-measurement.md`):

   | | static raw | static padding-excl | raw-byte md5 |
   |---|---|---|---|
   | R2 safe / R2 verified-safe | 57 / 57 | 46 / 46 | `935221a8…` both |
   | R4 unsafe / R5 verified-unsafe | 37 / 37 | 33 / 33 | `98e4a665…` both |

   Executed instructions (`Ir`) equal too. *(The pilot's published 58/38/33 are
   each one too high — the old pipeline counted the symbol header line.)*

   **Two digest conventions exist; always say which.** `935221a8…`/`98e4a665…`
   are `harness/asm.py`'s `md5_raw`, which includes trailing alignment padding;
   `e5310297…`/`a23e076c…` are the `nm --print-size` extent, i.e. the function
   proper. Both are reproducible (TASK_002 claimed the latter was not — it was
   wrong, TASK_002_REVIEW re-derived them first try). The counts and the
   equalities are unaffected either way. See `.memory/03-measurement.md`.

   Reproduced independently on p01 (TASK_002), `-O3 isolated`, and re-derived at
   TASK_003 under **both** conventions:

   | pair | `md5_raw` (objdump grouping) | `md5_fn` (`nm` extent) | counts |
   |---|---|---|---|
   | R4 ≡ R5 | `fb90a96c…` | `619b1d1b…` | 36 / 34 (+3 insn padding) |
   | R2 ≡ R2v | `f1e7f951…` | `12d307f2…` | 49 / 47 (+10 insn padding) |

   The R2≡R2v digests were `6c85987d…`/`f8e1fe32…` and went stale at the TASK_005
   barrier swap; re-measured at TASK_006_REVIEW. The R4≡R5 pair is unchanged and
   current. **Every *equality* held throughout** — only the absolute digests
   moved — but `.memory/03-measurement.md` requires an identity claim to cite a
   reproducible raw-byte digest, and for three tasks these two were not. p01's
   `NOTES.md` carried the same stale pair plus three more (the `O0` rows).
   The instruction counts in this table have **not** been re-verified since the
   swap; treat them as unconfirmed until something re-measures them.

   TASK_002 published the counts as 39/34 and 59/47; those are objdump's
   grouping, i.e. the function *plus* its trailing padding. Quote `md5_fn` for
   identity — `harness/asm.py` now reads padding separately so a benign relink
   at a different alignment cannot be mistaken for "the proof cost something".
2. **A proof buys nothing on its own.** Proving R2 panic-free leaves every bounds
   check in place — rustc never learns what Z3 knew. The win only materialises
   when the proof *licenses unsafe code* (R5 = R4 codegen + discharged obligations).

3. **The static safe-vs-unsafe gap is mostly not a dynamic gap, and the tuned safe
   rung nearly closes it.** (TASK_001, corrected at TASK_001_REVIEW.) On the pilot
   kernel at `-O3`, LLVM hoists the bounds check clean out of the vectorised loop,
   so the safety tax is **O(1) per call, not O(n)** — confirmed across
   n = 999 … 100 000. The static delta is prologue, panic landing pad and padding.

   Magnitudes, per call, versus unsafe R4:

   | rung | static raw | static padding-excl | executed `Ir` delta |
   |---|---|---|---|
   | R2 safe-naive (`v[i]`) | +20 | +13 | **+7 … +22** |
   | R3 safe-tuned (iterator) | +24 (largest of *all* rungs) | +16 | **+6 … +8** |

   Three traps here, all of which bit the first write-up:

   - **The delta is not a constant.** It varies with `n mod 4`: 22 / 7 / 9 / 11 for
     residues 0 / 1 / 2 / 3. R2's vectoriser peels a 4-element scalar epilogue when
     `n % 4 == 0`; R4 does not. The original "+22, independent of n" came from three
     data points that were all ≡ 0 (mod 4). Quote a range, or state the residue.
   - **Quote the padding-excluded static number**, or say which you are quoting.
     `.memory/03-measurement.md` calls the raw count overstated; do not then
     headline the raw gap.
   - **R3 is the honest comparison for "what safe Rust costs."** Idiomatic
     iterator code lands within ~6 instructions per call of unsafe while being
     *statically the largest cell in the ladder* — a sharper refutation of
     static-count-as-proxy than the gcc/clang one. Reporting R2 alone overstates
     safe Rust's cost by ~3.7×. **Never publish a safety-cost claim without R3.**
   - **…and the corollary, which cost us three retractions: without the *best*
     R3.** A safety-cost claim is a claim about the *language*, so it is only as
     good as the best spelling anyone can find — and this project has now
     published a spelling's cost as safety's cost **three times**: p02 (a lost
     `memcpy` idiom, retracted), p16 ("only the naive indexed spelling is O(n)",
     caught at review), p05 (`chunks_exact` beats the *unsafe* rung, caught at
     TASK_014_REVIEW). The failure mode is always the same — one plausible R3 is
     written, measured, and reported as what safe Rust costs.
     **Before any safety-cost headline, write at least two independent R3
     spellings and quote the cheaper.** The iterator/slice-consuming forms
     (`chunks_exact`, `split_at`, `iter().zip()`) are the ones that keep winning,
     because they hand the optimiser a length it does not have to re-derive.
   - **…and that rule is still not enough. PROVISIONAL — not yet reviewed
     (TASK_015).** The audit measured **four** safe spellings of p05's kernel —
     `+35 + nrow·(29+3r)`, `+6·nrow + 9`, `+nrow + 7`, `−nrow + 7` — and **the
     spread across them is larger than the safe-versus-unsafe gap itself.**
     Quoting "the cheaper of two" still publishes a number that the third
     spelling moves. Worse, **R4 is a spelling too**, and the audit's R4′ control
     put unsafe back on top on both p05 and p16.

     So the rule that actually follows is: **compare idiom-matched rungs, or
     publish the spread rather than a cell.** A single number per rung is only
     meaningful when every rung was written the same way; otherwise the ladder is
     measuring the author, not the language. This is the most important
     methodological result the project has, and it is not yet reflected in the
     reporting format — see `.memory/06-catalogue.md`.

   Reproduced on p01 at TASK_002, with the residue effect measured properly this
   time (16 window lengths, `inputs/gen.py --sweep`), `-O3 isolated`, per call:

   | rung | res 0 | res 1 | res 2 | res 3 |
   |---|---:|---:|---:|---:|
   | R2 safe-naive | **+29** | +11 | +13 | +15 |
   | R3 safe-tuned | +5 | +4 | +4 | +4 |
   | R5 verus | 0 | 0 | 0 | 0 |
   | R1 gcc | +368 … +384 (≈ +41%) | | | |

   Constant in `win_len` within a residue class (+29 at 500, 504, 508 *and* 512),
   so the tax is per call, not per element. **Give every pattern's `small` and
   `large` inputs different residues mod 4** — p01's first draft used 500 and
   4096, both ≡ 0, which is the single worst residue for R2 and would have
   overstated it 2.4×. That is the third time this trap has been stepped in.

   One new caveat: the +29 is the *out-of-line* figure. In `whole` mode on
   `large`, R2's inlined kernel costs ≈ **+340** per call — its scalar epilogue
   keeps a live per-element bounds check and the driver's `div` is
   rematerialised. R3 and R5 show no such amplification. Derived from a
   difference of two builds, so: an observation, not a settled result.

   Do **not** generalise any of this to patterns with data-dependent indices — the
   interesting patterns are precisely the ones where LLVM cannot hoist, and that is
   where the ladder earns its keep.

   **p02 first appeared to be that case and was not.** The claim published at
   TASK_004 — "R2 pays an O(n) bounds-check tax on a data-dependent copy,
   +178 at 61 B and +1025 at 4092 B" — was **refuted at TASK_004_REVIEW**. Keep
   the refutation, not the claim; it is the most instructive result so far.

   | rung | 61 B | 4092 B | vs R4 |
   |---|---:|---:|---|
   | R2 safe-naive, as first written | 407.0 | 11226.0 | +178 / +1025 |
   | …`copy_from_slice`, indexed fold kept | 239.0 | 10210.8 | **+10 / +10** |
   | …indexed copy kept, one `&src[a..b]` reslice added | 239.0 | 10210.8 | **+10 / +10** |
   | …identical but the check written *additively* | 237.0 | 10208.8 | **+8 / +8** |
   | R3 safe-tuned | 239.0 | 10210.8 | +10 / +10 |

   The decomposition that kills it: changing **only the fold** moves nothing;
   changing **only the copy** removes 100% of the tax. R2's and R4's fold loops
   are the *same* 19-instruction unrolled body — the indexed fold's bounds checks
   cost **zero**. The real cause is that `len > src.len() - (src_off + 2)`
   (subtraction-first) leaves LLVM unable to prove the index bound, so
   loop-idiom recognition never forms a `memcpy`; one operator change flips
   `bulk_calls []` → `['memcpy@GLIBC_2.14']`, 118 insns → 87. So the comparison
   was **inline SSE2 copy vs `call memcpy`** — two different algorithms — and C
   written the same way pays the same (clang +532; gcc's byte loop is 94 Ir
   *faster* than glibc's memcpy).

   The honest claim: *rustc failed to idiom-recognise one spelling of a byte-copy
   loop; three other spellings, including the reslice a competent Rust programmer
   writes, are +10 flat.* That is a codegen fragility finding, not a safety-cost
   finding — still worth publishing, but not as a safety tax.

   Note also that "gcc's byte loop beats glibc `memcpy`" — briefly believed — is a
   mislabelled comparison. gcc's byte loop is faster than **R4** (10106 vs 10201),
   not than gcc's own `memcpy` build (9200). *Within* one compiler the byte loop is
   dearer: gcc +906, clang +528. The conclusion survives and is stronger.

   **Two rules follow.** (1) Before attributing a cost to bounds checking,
   decompose: change one loop at a time and re-measure. A whole-kernel delta
   attributes nothing. (2) Residues bite harder than recorded. Swept over 68
   lengths at two scales (TASK_006), R2−R4 is a **sawtooth of constant amplitude
   179 Ir, resetting at `len ≡ 1 (mod 16)`**, on a linear term of 0.21 Ir/byte —
   so copying *one more byte* (2048→2049) made R2 174 instructions *cheaper*.
   `gen.py` pinned residues mod 4 and mod 8; the modulus that mattered was 16, and
   it now checks mod 16 before writing any input. Sweep, do not sample — and sweep
   **two full cycles**: the first sweep design used 16 lengths per band and could
   not distinguish period 16 from period 64.

   **R3 remains the honest number** — +10 per call, flat — the third pattern in a
   row where that is the finding.

   Also from p02, against p01's gcc-vs-clang result: **gcc executed ~10% fewer
   instructions than clang here and took 23% longer** (8765 vs 9764 Ir per call;
   30.8 vs 25.0 ms). Neither compiler is reliably ahead, and instruction count
   and wall clock disagreed in *direction* on the same source. Report both
   columns; do not let `Ir` stand in for time without saying so.

4. **p16 is the case p01 said not to generalise to. One *spelling* of safe Rust
   pays an O(n) cost there; idiomatic safe Rust still does not.** (TASK_007,
   corrected at TASK_007_REVIEW — the first write-up of this said "first real O(n)
   safety cost" and that **overclaimed**.) A TLV walker: trip count from attacker
   data, each record's position depending on every previous length field, nothing
   hoistable, nothing idiom-recognisable.

   **The number that settles it: R3's marginal rate is 5.7500 Ir per folded byte,
   which is R4's exactly.** Idiomatic safe Rust costs **zero per byte** here. Its
   whole cost is O(1) per call (+27 / +77), which *shrinks* as a fraction of the
   call with size — 0.90% on `small`, 0.32% on `large`. Only the naive indexed
   spelling is O(n). This file already said, at finding 3: *"Never publish a
   safety-cost claim without R3."* The rule was violated by its own author on the
   next pattern. **Lead with R3 or do not lead.**

   `-O3 isolated`, marginal `Ir`/call:

   | rung | small (508 B win) | large (4090 B win) | vs R4 |
   |---|---:|---:|---|
   | c-clang / c-clang-h | 2993 / 3017 | 23761 / 23815 | check = +24 / +54 |
   | c-gcc / c-gcc-h | 4062 / 4079 | 32694 / 32735 | check = +17 / +41 |
   | **R2 safe-naive** | **5095** | **40921** | **+2085 (+69%) / +17123 (+72%)** |
   | R3 safe-tuned | 3037 | 23875 | +27 / +77 |
   | R4 unsafe / R5 verus | 3010 / 3010 | 23798 / 23798 | 0 |

   **R2's cost is per byte, not per call** — 10.00 Ir per folded byte against
   R3/R4's 5.75, over 68 consecutive value lengths in two bands 18× apart, exactly
   4.25 apart in both. The sweep is *exactly* linear (least-squares residual
   **0.00** over 34 points per band) and `R2 = 10·folded + 21·nrec + 11`
   reproduces both shipped totals to the instruction. Measured, not fitted.

   **Decompose before calling it a bounds-check tax — the same trap as p02.**
   Changing **only the fold** removes 98.0% / 99.3% of the gap; changing **only
   the walk** removes 1.5% / 0.5%; the two sum to 2091 against the whole gap's
   2085, so there is no interaction term. The cost is entirely in the inner byte
   fold: R2's is a rolled 10-instruction body, R4's is 4×-unrolled at 23 insns per
   4 bytes.

   **The attribution was then confirmed by construction at TASK_007_REVIEW**,
   which is why it is safe to state. `-C llvm-args=-unroll-count=1` rolls R4's
   fold and is a **bit-for-bit no-op on R2** (so it is not silently changing both
   sides). Rolled R4 and rolled R2 then differ by exactly `cmp %rax,%rsi ; je
   <panic>`:

   | fold | band A | band B |
   |---|---:|---:|
   | R2, rolled + checked | 10.0000 | 10.0000 |
   | R4 shipped, 4×unrolled + unchecked | 5.7500 | 5.7500 |
   | **R4, rolled + unchecked** | **8.0000** | **8.0000** |
   | **gap R2 − R4-rolled = the check alone** | **2.0000** | **2.0000** |

   So 4.2500 = 2.0000 + 2.2500 with **zero residual**. The 8.00 rolled-unchecked
   constant has four independent sightings, the best of which is free: **R4's own
   remainder loop in the shipped binary** is 8 insns/byte — R2's body minus
   exactly `cmp`+`je`. (The `shl $0x5` site count offered in `NOTES.md` is *not*
   independent corroboration — both counts follow from the same unroll factor.)

   **The split is exact but path-dependent, and the counterfactual is not what it
   looks like.** Forcing LLVM to unroll the *checked* loop
   (`-unroll-runtime-multi-exit -unroll-count=4`) gives **9.50**, not 7.75: four
   copies need four exit tests, `mov,or,cmp,je` = 15 insns = 3.75/byte. So
   unrolling R2 would recover **0.50, not 2.25**. `NOTES.md`'s "would have
   amortised" is a false counterfactual. The right word is the stronger one:
   **the check does not merely cost 2.00, it forecloses an optimisation worth
   2.25 that it could not have amortised anyway.**

   **The transferable lesson: a safety tax must be attributed to a mechanism,
   never to a comparison** — and the mechanism here is only half the check. Same
   shape as p02's retraction (a lost `memcpy` idiom), arriving this time at a real
   cost rather than a spurious one.

   **Three further things p16 establishes:**
   - **`Ir` and wall clock disagree in *magnitude*, not just direction: +72% `Ir`
     → +0.27% time.** Spreads are 0.96–2.31%, well inside the 10% discard
     threshold, so unlike p02's timing this is a *usable* null. **The null itself
     is safe** — it is a ratio taken inside one session — and so is the ns figure.
     The fold is a serial Horner chain, latency-bound: differencing `n_iters`
     gives **3.027–3.055 cycles/byte** for every rung on `large`, 3.03–3.08 on
     `small`.

     ⚠ **That cycles/byte figure is an inference, not a measurement, and it is
     now qualified (TASK_012).** It converts a wall time measured in TASK_007
     with a clock measured in TASK_007_REVIEW — *different sessions* — and this
     box's clock is set by other tenants: the same probe read 3.80–3.89 GHz in one
     session and 2.55–2.86 GHz in another (`.memory/00-environment.md`). At
     all-core turbo the same ns figure is ~2.2 cycles/byte.
     What survives independently: the Horner chain `(acc<<5) - acc + b` has a
     **hard 3-cycle serial latency floor**, so *if* the chain is the limiter the
     clock during measurement must have been ≥ ~3.8 GHz. Consistent, and it is
     why 3.03 looked so clean — but it is a consistency argument, not an
     independent confirmation. **Do not publish cycles/byte for p16 without an
     interleaved clock measurement.**
     Because L1-resident `small` gives the same rate as L3-resident `large`, the
     obvious alternative — memory-bandwidth-bound, which would equally hide a
     +70% `Ir` gap — is **ruled out**, not merely unconsidered.
     **This is a property of this kernel, not of bounds checks**: a kernel with
     independent inner iterations would turn the same 4.25 Ir/byte into time.
     *(The first write-up's cycle arithmetic was wrong — it implied 3.30 GHz while
     CPU 5 turbos to 3.85 GHz, and 13% / 21% of the quoted wall times is fixed
     overhead outside the kernel. Two errors that cancelled. **Always difference
     `n_iters`; never divide a total wall time by a byte count.**)*
   - **Vectorisation is not a confound, but "nothing vectorises in any rung" is
     false** — it is **23 of 32 cells**; the 9 with `['xmm']` are all `whole`-mode
     `main`, i.e. the driver, not the fold. The *fold* is scalar in every rung, so
     the gap is measured on a scalar loop on both sides. Quote the 23/32.
   - **R3 survives, and is now the *fourth* pattern in a row** — see the opening
     of this finding. `7 + 7·nrec` (`7 + 5·nrec` when vlen ≡ 0 mod 4) is a
     **zero-degrees-of-freedom interpolation**, and only `large` is genuinely
     out-of-sample; do not call it a prediction. **The residue modulus that
     matters here is 4** — the unroll factor — amplitude 1.5%. p01's was 4, p02's
     was 16; do not assume.
   - **gcc's 36% deficit is a flag default, not a codegen limit.** `c-gcc` is 4062
     against clang's 2993 on `small` — but with `-funroll-loops` gcc reaches
     **2823 and beats clang**. Not a fortify/ssp artefact. Before reporting any
     gcc-vs-clang gap, establish whether it is a default or a capability.

   Security half, and it was **directly demonstrated** at TASK_007_REVIEW rather
   than inferred: `end - p` wraps to `0xfffffffffffff03d` and the walk ran
   **200 MiB / 6459 records past the window without terminating** — only the
   reviewer's own cap stopped it. Equivalence was fuzzed too: 210 random
   adversarial chains × 12 binaries against `model.py`, **0 mismatches**.
   R1 does not merely over-read, it **walks unboundedly**. Once `p`
   passes `end`, `end - p` underflows `size_t` and the loop condition stays true
   forever, so R1 parses memory until it faults — SIGSEGV in both gcc and clang
   plain builds, ASan `heap-buffer-overflow` READ 0 bytes past a 3072-byte region.
   R1h and all four Rust rungs print the model's answer. Delete-the-check controls:
   C → SIGSEGV, unsafe Rust → SIGSEGV, safe Rust → **exit 101, index out of
   bounds**, Verus → will not compile. A missing check in a chained parser
   compounds; carry this to p17+.

5. **p17 — the limit. A program can be provably memory-safe and still leak, and
   we now have one.** (TASK_011.) A suffix-range parser mirroring CVE-2017-7529.
   `start = content_len - s` in **signed** arithmetic, guarded only by
   `start < end`. The served range is `[len - s, len)` — the last `s` bytes — so
   one attacker `u16` selects the harm:

   | `s` | the unchecked read | ASan on R1 | safe Rust |
   |---|---|---|---|
   | `≤ content_len` | correct | — | correct |
   | `content_len < s ≤ len` | the window's own header, **in bounds** | **clean, exit 0** | **reads it identically** |
   | `> len` | before the allocation | `6 bytes before 64-byte region` | panics, exit 101 |

   The two adversarial inputs are **the same 64 bytes with one suffix field 64 vs
   70**. Both C rungs exit 0 with a plausible answer on both.

   **Control 1 — safe Rust with the sign conjunct deleted.** On the leak input it
   prints `1395842226496950656`, **bit-identical to C's value, no panic** (the
   reviewer confirmed identity is structural: an identical 130-byte index
   sequence, derived independently, not a coincidence); on the OOB input it
   panics. So bounds checking kills exactly one of the two harms.

   **The shipped `adversarial-leak` row is *not* an information disclosure, and
   the first write-up of this finding said it was.** Corrected at
   TASK_011_REVIEW. R1 folds 130 bytes over window indices `[0,63]` where the
   checked rungs fold 66 over `[8,63]`; the excess is exactly indices `{0..7}` —
   `nsuf` plus the three suffix `u16`s, i.e. **the attacker's own request table**
   (`inputs/gen.py` literally labels it `ATTACKER DATA`). Structural, not an
   artefact of this input: the regime reads `[len-s, len)` with
   `len-s ∈ [0, body_start)`, so the excess is *always* a suffix of the
   attacker-written header, bounded by `2 + 2*nsuf` bytes. p17 as shipped
   demonstrates **provably memory-safe and functionally wrong** — real, and worth
   publishing — but not disclosure. p17's own `NOTES.md` said the true thing one
   paragraph below the headline that contradicted it.

   **Control 2 — the artefact, and it is one token away from what shipped.**
   The manager's first design (delete the sign check from R5) fails *both*
   obligations, because a proof quantifies over all inputs and that mutant admits
   both harms — **the separation needs a program change, not an input.** The
   engineer then built `start >= -(body_start as i64)`, which verifies with only
   the functional obligation failing. But that guard is **strictly stronger than
   what a bounds check buys**, and calling it "exactly what a bounds check buys"
   was the error that made the leak vacuous. The driver hands the kernel the
   **whole blob**, so bounds checking permits any *slice*-relative index ≥ 0:

   > `start >= -((off + body_start) as i64)`

   That verifies identically — **`9 verified, 1 errors`, functional only; `10
   verified, 0 errors` once the functional spec is stripped** — and it **does**
   disclose. On a two-window probe the output tracks the *victim window's* secret
   (`14940305438379539953` vs `10930790086150322769`), with no panic and no
   `unsafe`.

   **That is the real artefact: a program with no `unsafe`, whose memory-safety
   obligations all discharge, that reads another window's bytes.** It is
   Heartbleed's shape — a lawful read of a neighbour's buffer inside one
   allocation — and it puts a measurement under finding 2: the obligation that
   catches it is the functional `ensures`, never the access obligation. **The
   guard being one token weaker is the whole point**, and it is why "what a bounds
   check buys you" must be written *slice*-relative, not window-relative.

   **Independently reproduced at TASK_012 on shipped-format inputs**, with a
   committed input pair `adversarial-crosswin-{lo,hi}` differing in exactly 28
   bytes of window 0's secret and nowhere else. Every checked rung prints
   `15118011540968580209` on both; C, and the two slice-guarded variants, print
   two *different* values that track the secret. ASan+UBSan clean, exit 0, on
   both files.

   **And the sharpest part was not in the original claim: `safe_naive_sliceguard`
   does it too — plain safe Rust, zero `unsafe`, no proof.** So this is not a
   statement about a trusted accessor or about Verus at all. **It is a statement
   about what a bounds check *is*:** the language's bound is the slice it was
   given, and if the caller hands you the whole blob, "in bounds" spans every
   other client's data in it. Rust enforces that bound perfectly and the leak
   goes straight through it.

   Two design lessons from building the input, both non-obvious and both now in
   p17's `spec.md`: **window 0 must serve something**, because a window returning
   0 pins `acc` at 0 and `k = (acc*nwin) >> 64` is then 0 for ever — **the
   driver's Lemire index has an absorbing state**, and the first design never
   visited the attacker window; and the malicious suffix must keep `abs >= 0`, so
   that every rung including R1 stays in bounds and ASan must stay *silent* —
   which is what makes it a disclosure demonstration rather than a crash.

   **Perf — R3 is free for the fifth pattern in a row** (+32 Ir/call flat, 0 per
   byte; +0.61% / +0.08%). And **R2−R4 = 4.2500 Ir per folded byte, reproducing
   p16's swept constant on a completely different kernel** — *exactly*, in fact:
   the delivered 9.9991 / 5.7491 were contaminated by the driver's final
   `println!` (its digit count varies per input); the zero-residue lag-4 pair
   gives **10.0000 / 5.7500 exactly**. The constants reproduce *better* than
   claimed — so
   4.25 is a property of *rustc's checked indexed byte fold*, not of p16. Two
   further reproductions: gcc's default-vs-`-funroll-loops` deficit (2nd pattern —
   `-funroll-loops` takes gcc past clang again), and gcc's default rolled fold at
   **exactly 8.0000 Ir/byte**, the rolled-unchecked constant p16's review derived.
   Decomposition again puts 98.5% / 99.8% of R2's gap in the inner byte fold.

   **Two manager predictions killed by measurement**, both worth keeping:
   `i128` index arithmetic costs +4.0000 Ir/byte, but **signedness itself costs
   4 Ir per *call*, flat — 0.17% of the gap.** "The cost of the check is the
   conversion, not the comparison" is **false**.

   Wall clock: every rung folds a byte in **0.784–0.791 ns**, 0.9% spread across a
   73% `Ir` gap. **p17 quotes no cycles/byte, and that is correct** — a manager
   instruction to quote 3.02–3.05 was overturned at TASK_012 with the measurement
   that killed it. `scaling_cur_freq` is unusable (it reads 800 MHz under load),
   *and* the dependent-chain probe is not reproducible across sessions on this
   shared box: 3.80–3.89 GHz in one, 2.55–2.86 GHz in another, same code, same
   cores. The same ns figure is 2.2 or 3.1 cycles/byte depending on when you ask.
   **ns is a measurement here; cycles is an inference.** See
   `.memory/00-environment.md`.

6. **p05 — on a vectorised loop the cost is `O(nrow)` for two *spellings* of safe
   Rust and *negative* for a third. Safe Rust is not slower here; two ways of
   writing it are.** (TASK_013, corrected at TASK_013_REVIEW, and its headline
   **refuted at TASK_014_REVIEW** — see the "R3 is not free" bullet below, which
   was wrong. The first write-up also said "the check costs 0.0000 Ir/element"
   and "the wider the lane the cheaper safety gets"; **the first is true only of
   the steady state and the second is refuted by measurement.**)

   2-D index flattening, `a[i*ncol + j]`, associative inner sum so the loop can
   vectorise, Horner once per row.

   **What is exactly true.** In the vectorised steady state the per-element rate
   is **1.375000** (= 11/8, an 11-instruction body over 8 elements) for c-clang,
   safe-naive, safe-tuned and unsafe **alike**, six decimals, both bands; c-gcc
   `1.062500` (= 17/16). Five rungs emit identical mnemonics. Per *element*,
   inside the vector body, the check really is free.

   **Where the check actually went — the mechanism, supplied at review.** It is
   hoisted into a **22-instruction per-row trip-count computation** (a
   `cmova`/`cmovb` min-max chain computing `N = min(ncol, len − rowbase)`), and it
   **survives in the scalar epilogue** at 8 Ir/element against R4's 5. So the cost
   is `O(nrow)`, not zero. **"Per element" is a marginal derivative, not an
   average** — the average gap on shipped inputs is ~34%.

   **`f(0) = 84` is explained**, and it is the sharpest small result here:
   `mov $0x8,%r11d ; cmove %r11,%r8` — **a remainder of zero is forced to a full
   vector width**, because R2's loop is multi-exit and must keep a scalar
   epilogue. `84 = 29 + 64 − 11 + 2`. Every power-of-two `ncol` pays a full extra
   vector iteration it does not need.

   **The model has zero fitted parameters.** Derived at review from the listings
   alone: `R4 = 37 + nrow·(27+11q+5r)`, `R3 = 46 + nrow·(33+11q+5r)`,
   `R2 = 72 + nrow·(56+11V+8e)`, reproducing every measured point to the
   instruction. The published `35 + nrow·f(ncol mod 8)` form is the same thing with
   the structure hidden; `f` absorbs nothing. **Domain: `ncol > 8`** — the model is
   false below that (34755 measured against 41699 predicted at 496×8).

   **Four corrections that matter, all measured:**
   - **Wider lanes make safety *worse*, not better.** At AVX2 the gap at
     `ncol ≡ 0 (mod 32)` is **14601 Ir/call against SSE2's 4487**, ratio 1.42× →
     **4.58×**, and safe Rust is **absolutely slower** (18674 vs 15177). The peel
     is VF elements long, so it grows with the lane.
   - **The hypothesis is not inverted in general — it holds at `ncol = 8`.** R2's
     vector guard is `N >= 9` where R4's is `ncol >= 8`, so there the check **does**
     block vectorisation, and costs **2.94×**. p05 has both regimes in one kernel.
   - ~~**R3 is *not* free here.** +16.7% at 496×8, +4.7% at shipped `large` — an
     `O(nrow)` cost. The "R3 free" streak ends at five patterns, not six.~~
     **RETRACTED at TASK_014_REVIEW, and this is the blocker of that review.**
     What was measured is p05's *shipped* R3, which reslices by hand. One
     idiomatic safe expression — `data.chunks_exact(ncol)`, a spelling this
     file's own R3 definition **names** — is `nrow − 7` instructions per call
     **cheaper than R4**, exactly, on every input in both residue classes
     (−12 at nrow 19, −34 at 41, −58 at 65), with identical stdout and exit
     against R4 on all **150** committed p05 inputs, and +1.78% wall against
     R4's +2.22% for shipped R3 and +31.2% for R2. Zero `unsafe`, no proof.
     The mechanism: `chunks_exact` hands each row a slice whose length **is**
     `ncol` by construction, so the vector/scalar split is computed once per
     *call* rather than once per row (no `cmov` at all, against R2's five), the
     epilogue is R4's unchecked 5-instruction body, and both `f(0) = 84`
     mechanisms — the `cmp $9` guard and the `cmove` forcing a zero remainder to
     a full vector width — disappear.

     **…and then the next task refuted the framing of *that*, so read the
     amendment before quoting any of it. PROVISIONAL — not yet reviewed
     (TASK_015).** "Safe Rust beat unsafe Rust" is an **idiom mismatch, not a
     language fact.** R4 is a spelling too: rewrite the *unsafe* rung with the
     same consumed-slice idiom (a row pointer advanced by `ncol`, ten lines) and
     unsafe is back on top. p05's honest idiom-matched safety number is
     **+11.00 Ir/call, flat — nrow 19, 41 and 65 all exactly +11, so `O(1)` and
     not `O(nrow)`.** p16's is `nrec + 3`. The shipped R4 maintains **two** row
     bases (one for the vector body, one for the scalar epilogue) and
     `chunks_exact` collapses them to one pointer; that single `add` per row
     **is** the `−1·nrow` slope, and it is R4's to fix.

     **And the `−(nrow − 7)` is `Ir`-only.** `chunks_exact` with a runtime chunk
     size emits a hardware `div` per call (`len − len % chunk_size`), which
     callgrind prices at **1 instruction**. Interleaved wall clock on `small`
     says **+0.47%** where `Ir` says −0.87%, at an 8.61% min-to-median spread —
     the worst of the five cells and the only one near the discard threshold.
     Quote it as an instruction-count result or not at all.

     Two smaller corrections to the review's own write-up: its static counts mix
     conventions (105 is `n_fn`; 171 and 97 are `n_raw` — matched, 105/168/87 or
     109/171/97), and **shipped R3 also has zero `cmov`** — the five are R2's
     alone.
   - **4.2500 is not "the check".** The `-unroll-count=1` no-op control *does*
     exist here (bit-for-bit identical R2, `md5_fn 76d7c2380278`), and gives
     rolled+checked 7.0000, rolled+unchecked 5.0000, novec-unrolled 2.7500 →
     **4.25 = 2.00 check + 2.25 unroll**, the *identical split* TASK_007_REVIEW
     derived on p16. So the third reproduction is of the constant **and its
     decomposition**, which is stronger than the constant alone.

   **Why the check cannot be eliminated — and what that is worth.** R2's panic is
   dead on every execution, and LLVM keeps it: `nrow*ncol <= avail ⟹ i*ncol + j <
   avail` is **nonlinear**, which is exactly the obligation R5 discharges with
   `lemma_mul_inequality` and one `by (nonlinear_arith)`. Linearising that guard
   in an isolated compilation deletes the entire per-row apparatus — 5 `cmov` → 0,
   166 → 125 instructions, the `cmp $9` and residue `cmove` gone, an unchecked
   epilogue (TASK_014_REVIEW, `probe2.rs`, which also reproduces the shipped
   mechanism independently). So nonlinearity is the blocker **for this kernel**.

   It is **not necessary in general**: p08 keeps a provably-dead `copy_within`
   range check whose implication is purely *linear*, at 26.00 Ir/call, because
   the fact it needs is **relational** across the loop induction variable rather
   than nonlinear — LLVM's value-range machinery is per-value. Restating the
   relation inside p08's loop deletes the check outright (3 panic refs → 0).

   **And the cost is not intrinsic to safe Rust** — see the retracted bullet
   above. What the `29 + 3r` per row prices is the *indexed and the
   manually-resliced spellings*, not the missing lemma.

   Two further caveats, both measured at TASK_014_REVIEW. The linearisation
   counterfactual does **not** survive the shipped binary build: as a real p05
   cell, LLVM's induction-variable simplification re-derives `i*ncol` and the
   linearised R2 measures **2366 Ir/call against R2's 2081** — *worse*. And the
   whole question is moot for the headline, because a spelling with no lemma at
   all beats R4.

   ~~"The `29 + 3r` Ir per row is the price of the optimiser failing the lemma
   the proof proves."~~ **Retracted.** It is the price of two spellings; a third
   pays nothing. The sentence remains true of the *obligation* and false as a
   statement about safety, which is the distinction it elided.

   **Two things that stand unchanged:** `Ir` converts to time on this kernel
   (+34.4% `Ir` → **+32.9%** wall — the review's own remeasurement; the delivered
   +30.5% was over-precise), confirming a prediction p16's `NOTES.md` made that a
   kernel with independent inner iterations would convert where its latency-bound
   Horner chain did not (+72% → +0.27%). And the `u32` row accumulator deviation is
   **sound, and better justified than the delivery argued**: `ncol <= 65535` × `u8`
   caps a row sum at 16 711 425 < 2³², so `u32` and `u64` are equal on *every
   representable input*, confirmed by identical checksums.

7. **p08 — the first structural Rust win, and a bug that executes without
   consequence.** (TASK_014, reviewed at TASK_014_REVIEW.) A fixed buffer shifted
   right to make room; R1 spells the move `memcpy`, R1h `memmove`, and **that one
   token is the whole difference**. Every rung carries the same bounds guard, so
   this is the project's first result that is not about a bounds check.

   **`memcpy` *is* `memmove` on this libc.** glibc 2.39 x86-64: one function, one
   address, with a `dst-src < n → backward copy` branch — and the `_chk` forms
   alias too (`__memcpy_chk == __memmove_chk`), which matters because gcc's
   fortified cells call those. So the UB **executes and is unobservable**: 320
   runs across every size regime with zero divergence, all 32 builds print the
   model's answer, exit 0, no diagnostic. **R1 ≡ R1h at 0.00 Ir/call** — the same
   machine code with one different call target. That is a **libc** property, not
   a language or compiler one, and must never be quoted as "memmove is free".

   **What sees it.** ASan's `memcpy-param-overlap` fires, exact to the byte
   (`d=2045` fires, `d=2046` silent) — **but not when the call site is
   fortified**, because the check lives in the `memcpy` interceptor and ASan does
   not intercept `__memcpy_chk`. The discriminator is `_chk`, **not gcc**: clang
   at `-D_FORTIFY_SOURCE=3` is blind too. Miri catches the Rust mutant
   (`copy_nonoverlapping called on overlapping ranges`), the first time the
   gate's Miri stage has been aimed at aliasing UB rather than spatial. valgrind
   memcheck is unavailable on this box entirely.

   **The structural claim, stated precisely.** Safe Rust cannot express the bug —
   the borrow checker rejects it at compile time, and rustc even suggests
   `split_at_mut`. There is **no runtime check** and therefore no cost to
   measure. `unsafe` re-opens it exactly via `copy_nonoverlapping`. **What R5
   does *not* do is rule it out**: substituting `copy_nonoverlapping` into the
   trusted body verifies `11/0` shipped and `15/0` under the twin, invisible to
   Verus, to the twin, to the contract pin and to stages 5c/5c-req. Only the O3
   identity pin against R4 and Miri catch it. A proof of a `requires` is not a
   proof that the trusted body honours it.

   **The honest counterweight, which must ship with the claim**: safe Rust
   prevents the *UB*, not the *wrongness*. The forward-loop control compiles,
   does not panic, and silently replicates the buffer.

   **R3 == R4 flat at 26 Ir/call** (a dead, purely linear range check LLVM keeps),
   so R3 is free again — but this is the **sixth** pattern only if p05's shipped
   R3 is counted as the failure, and after TASK_014_REVIEW's blocker the honest
   count is that **no pattern has yet shown safe Rust paying an unavoidable
   per-element price.** Do not write "p08 restores the streak"; there was no
   break.

So the research question is **not** "does verification cost performance" (it
doesn't). It is: *what must move into the trusted base to reach C's assembly, how
much proof keeps that base sound, and which C patterns resist this treatment.*

## Build matrix

Primary, per pattern: **6 cells × 2 opt levels × 2 inline modes = 24 builds** —
the 5 rungs, with R1 built twice (gcc and clang).

| Axis | Values |
|---|---|
| opt | `O0` (non-opt, for reading the lowering) and `O3` (for perf claims) |
| inline mode | `isolated` and `whole` — **defined by effect, not by flags** (below) |

### The inline modes are defined by *effect*

Settled at TASK_002_REVIEW. The two modes are not "these flags" — they are two
observable states of the build, and each language reaches them its own way:

| mode | the effect that defines it | C | Rust (R2–R5) |
|---|---|---|---|
| `isolated` | the kernel survives as its own symbol and is reached through a real `call` | own TU, `__attribute__((noinline))`, no LTO | `#[inline(never)]` via `--cfg slb_isolated` |
| `whole` | the kernel **may** inline into the driver loop | `-flto` across the three TUs | single crate, `codegen-units=1`, no `#[inline(never)]` |

The flags differ because the languages start from different places, and matching
the *flags* would not match the experiment: **C without `-flto` does not reach
`whole` at all** — the kernel survives as its own symbol and the cell collapses
into `isolated` (verified at TASK_002_REVIEW). Meanwhile `-C lto=fat` is
impossible for R5, because Verus links a precompiled `vstd` rlib with no bitcode
(`.memory/04-verus.md`), and a single-crate Rust binary at `codegen-units=1`
already has the kernel and the driver in one module — which is exactly what
`-flto` buys the three-TU C build.

Matched on effect, the two columns are publishable side by side. Matched on
flags, they would not be the same experiment. `harness/check.py` checks the
effect directly: in `whole` it looks for the loop in `main`, and step 3b's
marginal-`Ir` floor is symbol-independent precisely so it works in both modes.

Flags:

- **C**: `-std=c99 -Wall -Wextra` + `-O0` / `-O3`. Build with **both** `/usr/bin/gcc`
  (13.3.0) and `~/tools/llvm/bin/clang` (22.1.6) — clang is the same-backend
  baseline and is mandatory for any C-vs-Rust claim; gcc is the "what a distro
  ships" baseline.
- **R2–R4**: `rustc -C opt-level=0 -C debug-assertions=on` / `-C opt-level=3 -C debug-assertions=off`.
- **R5**: `./verus_run.py --compile verus.rs -o <out> -C opt-level=N ...` (same flags as R2–R4).
- `-C codegen-units=1` everywhere for reproducible codegen.
- `panic=unwind` is the default. `panic=abort` is a **secondary axis** (it deletes
  landing pads and is a real safety-cost lever) — build it, report it separately.

### Two traps that invalidate the comparison

- **Debug Rust ≠ C `-O0`.** Debug Rust inserts *integer-overflow checks* — a
  semantic difference, not an unoptimised lowering. So also build R2–R5 at
  `opt-level=0 -C debug-assertions=off` as the semantics-matched `O0` column.
  Never make a perf claim from an `O0` row.
- **gcc ≠ LLVM — confirmed, and it is large.** TASK_001 settled the pilot's
  C-vs-unsafe-Rust gap: it is a *backend* artefact. Same `pilot/k.c`, same `-O3`:

  | compiler | static raw | static padding-excl | kernel `Ir` @ n=50 000 | loop shape |
  |---|---|---|---|---|
  | gcc 13.3.0 | 32 | 30 | **125,019** | SSE2, 2 elems/iter, 5 instrs, no unroll |
  | clang 22.1.6 | 33 | 31 | **87,518** | SSE2, 4 elems/iter, 7 instrs, 2× unroll |
  | rustc 1.97.1 unsafe | 37 | 33 | **87,520** | *the same 7-instruction loop body* |

  clang and rustc emit the identical loop body (modulo register allocation and
  addressing-mode scale). The real clang→rustc static delta is **+2 instructions**
  (`lea (,%rdx,8),%rax` + `and $-32,%rax`), not 4 — the other 2 are padding slots.
  And the cause is **not** an `&Vec<u64>` ptr+len reload (LLVM promotes the `&Vec`
  argument in both rungs): rustc's vector loop uses scale-1 *byte* addressing where
  clang uses scale-8 index addressing, so it computes a byte-count bound. An
  induction-variable choice, not an ABI cost. Worth exactly +2 executed
  instructions per call, measured at n = 999 / 4001 / 12345 / 50000.

  **Always report a clang column.** A gcc-only C baseline overstates C's dynamic
  cost here by 43% — gcc emits *fewer* instructions and executes 42.9% *more*.
