# TASK_047_REVIEW — report on p06 (in-place rotate)

**Role:** research reviewer. **I did not fix anything.** Nothing under
`patterns/`, `harness/`, `common/`, `pilot/` or `.memory/` was edited. One
committed file was touched as a side effect and restored — see *Housekeeping*.

**Gate re-run independently: `check.py p06` → PASS**, complete run, `failures []`,
sanitizers as declared, Miri clean, `R4 ≡ R5 exact`, TCB 6 items
(`.temp/r47/gate.log`, 888 lines). **Four reviews have found real defects past
exactly that, and so does this one.**

**Reproduction: everything below is in `.temp/r47/`** —
`clayout.py` (the C layout population), `cgins.py` (per-instruction callgrind),
`oos_swaplaw.py` (the out-of-sample swap law), `vstd/*.rs` (the Verus probes),
`ctl/*` (the rung variants), `clay/times_*.json`, `NOTES.md`.

---

## Blockers

### B1 — `scr_load` is removable from the TCB at ZERO cost, and the recorded reason for not removing it is FALSE

`patterns/p06-rotate/verus.rs:423-425`, `NOTES.md:510`, `NOTES.md:947-949`,
`TASK_047_REPORT.md:186` all say the same thing:

> `<[T]>::split_at_mut` … **is the route that would delete this item; taking it
> changes the exec text of four rungs**, so it is recorded as open …

**Measured, and it does not.** The engineer identified the route and did not
take it; I took it.

1. **vstd already ships the missing write-back.**
   `~/tools/verus/vstd/array.rs:175` is
   `ref_mut_array_unsizing_coercion`, whose `ensures` is exactly
   `out.view() == old(r).view()` **and** `final(out).view() == final(r).view()`
   — the `&mut [u8;64] → &mut [u8]` reborrow write-back the file says is
   unavailable. Verus inserts it for an *implicit* coercion, so no hidden vstd
   API has to be named.

2. **p06's exact contract discharges** (`.temp/r47/vstd/sam3.rs`,
   p06's two `requires` and its `ensures`, character for character):

   ```
   let s: &mut [u8] = dst;
   let (a, b) = s.split_at_mut(n);
   a.copy_from_slice(&src[from..from + n]);
   →  verification results:: 2 verified, 0 errors
   ```

3. **The whole R5 verifies** with `scr_load` no longer `external_body`
   (`.temp/r47/ctl/v_scrload_verified2.rs`):

   ```
   shipped cfg     : 18 verified, 0 errors     (was 17)
   --cfg slb_twin  : 23 verified, 0 errors     (was 22)
   ```

4. **The exec text does not move — by one byte.** Compiled at the gate's own
   `-O3 isolated` flags:

   | binary | `n_fn`/nopad | `md5_raw` | `md5_fn` |
   |---|---|---|---|
   | shipped `unsafe` (R4) | 216 / 208 | `6608a63b5c52` | `897c52ff4005` |
   | shipped `verus` (R5) | 216 / 208 | `6608a63b5c52` | `897c52ff4005` |
   | **R5 with `scr_load` VERIFIED** | **216 / 208** | **`6608a63b5c52`** | **`897c52ff4005`** |
   | **R4 with the same body** (`.temp/r47/ctl/r4_splitat`) | **216 / 208** | **`6608a63b5c52`** | **`897c52ff4005`** |
   | **R2 with the same body** (`.temp/r47/ctl/r2_splitat`) | 303 / 294 | — | `48e508ddf075` = shipped R2 |

   Checksums identical on `small`, `large`, `degenerate`, `adversarial-inarray`.
   The `identity: unsafe == verus, O3 exact` pin holds unchanged.

**Failure scenario.** TCB size is one of the five axes this project compares.
p06 publishes **6 items / 11 body lines** (`NOTES.md:475`, README, and the
gate's `tcb_items`) and the four-trusted-bases table (`NOTES.md:520-528`) is
p06's *structural* result. Five suffice. If the manager lands the report's
`.memory` correction 1 as written, `.memory/04-verus.md` gains a true sentence
about the vstd spec and keeps a **false** one about the remedy being unaffordable,
and p06's TCB number — the axis the pattern says is its point — stays 20% high
for no measured reason.

**The drop-in**, for the record: delete `#[verifier::external_body]` from
`verus.rs:449`, replace the one-line body with the five lines above (plus the
existing `assert(src@.len() == vstd::slice::spec_slice_len(src));` idiom and a
`let ghost d0 = dst@; … assert(dst@ =~= load_into(...));`), and re-pin
`verus.obligations` 17→18, `verus.twin_obligations` 22→23,
`verus.items.scr_load.external` → `null`.

⚠ **The honest caveat, which the write-up must carry**:
`ref_mut_array_unsizing_coercion` is itself `#[verifier::external_body]` *inside
vstd*, so the axiom **relocates to vstd rather than vanishing** — the same
category as relying on `copy_from_slice`'s own `assume_specification`. By this
project's counting convention (pattern-local `external_body` items are the TCB;
vstd's `assume_specification`s are the trusted platform) that is a genuine
reduction, but it is a convention and the manager should say so out loud rather
than bank a 6→5 without the sentence.

**Project-wide, and it decides `.memory/04-verus.md`.** `.memory/04-verus.md:813`
says *"There is **no** vstd spec for `copy_from_slice`, so a rung that wants the
bulk copy verified needs its own trusted wrapper around `ptr::copy_nonoverlapping`"*
and `:133` repeats it for p08's `copy_in`. **Both halves are false at the pinned
vstd** (`0.2026.08.09.92f466f`): `vstd/std_specs/slice.rs:205` specifies
`copy_from_slice`, and **p02's `copy_bytes` contract discharges too** —
`.temp/r47/vstd/p02cb.rs`, p02's exact `requires`/`ensures`, body
`dst.split_at_mut(n)` + `copy_from_slice`, → **`2 verified, 0 errors`**, no
`external_body`, no `unsafe`. So the correction is not "the spec exists"; it is
**"the trusted wrapper is not needed on either pattern"**. (I did not re-spell
p02 — out of scope, and its body is `copy_nonoverlapping`, so its codegen may
move where p06's does not.)

### B2 — "R3 IS `O(n)` at 2.00 Ir/byte" is a property of ONE spelling; the cheapest in-contract R3 has NO per-byte term at all, and its law is exact

`NOTES.md:248` (the law table) and `NOTES.md:420-425`:

> **R3, by contrast, IS `O(n)`.** `R3 − R4 = 2.00000 Ir per byte of the live
> extent` … the project's **second R3 > R2 inversion after p09's**.

Measured on band M (`controls/sweep_ir.py`, whole-program marginal, `nrec = 8`,
`sum_m` 64 → 384, i.e. a 6× range):

| difference | at `sum_m=64` | at `sum_m=384` | Ir per byte |
|---|---:|---:|---|
| `safe_naive − unsafe` (R2) | 269.00 | 269.00 | **0.00000** |
| `safe_tuned − unsafe` (R3 shipped) | 281.00 | 921.00 | **2.00000** |
| **`c_idx − unsafe`** (in contract, zero `unsafe`) | **105.00** | **105.00** | **0.00000** |
| `c_swap − unsafe` | 401.00 | 1361.00 | 3.00000 |

`c_idx` is the engineer's own control — R3's two-step reslice and iterator fold
with R2's indexed swap. It is in contract (`spec.md` says in terms *"the SPELLING
OF THE SWAP is deliberately NOT pinned"*), contains no `unsafe`, and agrees with
the model on `small`/`large`/`degenerate`/`adversarial-inarray`.

**And its law is exact and parameter-free, which the shipped R3's is not.**
Swept over `m` 9…16 (`.temp/r47/resid.json`):

```
c_idx − R4  =  Σ_records α'(m mod 4)  +  1 ,    α' = {0:13, 1:15, 2:16, 3:17}
```

Out of sample on both shipped blobs, with **zero fitted parameters**:

```
small  m = 13,47,29,61,7   → 15+17+15+15+17 + 1 = 80    measured  +80.00
large  m = 3,5,1,7,2,6,4,8,3,5,1,7        → 186 + 1 = 187   measured +187.00
```

**The mechanism, because "it vanished" is not one** (PROTOCOL rule 11). Per-
instruction callgrind on `sweep-m48n08` (384 swap iterations/call,
`.temp/r47/cg/*.m48.out`): the whole of `R3ship − R4` is
`cmpq +425 · je +416 · jne +360 · jb −391` — the
`front.iter_mut().zip(back.iter_mut().rev())` adaptor's **two exhaustion tests
per item**, ≈ +2 instructions per swap against the two-cursor indexed loop's 8.
**None of it is a bounds check**: decoding the surviving panic pads with p12's
`controls/pads.py` gives `safe_tuned` and `c_idx` the **identical 11 pads at
identical `line:col`**. So p06's per-byte "safety" term contains no safety.

**Failure scenario.** `.memory/01-ladder.md` finding 3: *"this project has now
published a spelling's cost as safety's cost **three times** — p02, p16, p05"*,
and the rule that followed is *"write at least two independent in-contract R3
spellings and quote the cheaper."* p06 does measure them (`NOTES.md` §8 publishes
the span `+80…+490`), but its **law table, its prose and its README** all carry
the shipped spelling's number as *the* R3 result. If p06's `.memory/01-ladder.md`
entry is written from `NOTES.md:420` it records "p06's tuned safe rung is O(n) at
2 Ir per rotated byte, the second R3 > R2 inversion" — a fourth instance of the
failure finding 3 exists to prevent. The correct sentences are: *the cheapest
in-contract R3 costs 13–17 Ir per record and nothing per byte, less than half the
naive rung's 33.6*; and *the R3 > R2 inversion is `small`-only and is a property
of `split_at_mut`+`zip`+`mem::swap`, not of tuned safe Rust.*

⚠ **Scope, stated so it is not over-claimed.** This is an `Ir` result. On
`small`, wall clock cannot see it: `safe_naive` 250.93 / `safe_tuned` 249.90 /
`c_idx` 248.13 / `unsafe` 235.44 ns, against a `verus − unsafe` null of **+3.10%**
(`controls/wall_span.py`, 5 identical copies, alternating, 9 reps). And on
`large` the shipped R3 (+172) is *cheaper* than `c_idx` (+187) — `NOTES.md` §8
already says the cheapest found differs by blob, and it is right.

---

## Majors

### M1 — the two-number rule is satisfied on `small` only, and `large` carries the headline

`NOTES.md:325-346` publishes the hardening-side span on `small` alone, and says
of it *"this span is a `small`-and-`large`-shaped statement, not a universal
one"* — while measuring only `small`. p06's largest published number is the
`large` one, **+57.09%**.

I built the population and the missing rows (`.temp/r47/clayout.py`, 30 layouts
per cell, medians of min-of-7-reps, alternating, `taskset -c 5`,
`t(200000) − t(1)`):

| `large` | Ir/call (kernel-excl) | ns/call | Δ Ir | Δ ns |
|---|---:|---:|---:|---:|
| `c-gcc` (R1, the bug) | 1988.00 | 152.37 | — | — |
| **`c-gcc-h` (`r %= m`, SHIPPED)** | 2083.00 | 240.45 | +4.78% | **+57.80%** |
| `d_cmp-gcc` (`if (r>=m) r %= m;`) | 2099.00 | 159.78 | +5.58% | **+4.86%** |
| `d_sub-gcc` | 2105.00 | 160.77 | +5.89% | +5.51% |
| `c-clang` (R1) | 1707.00 | 144.70 | — | — |
| **`c-clang-h` (SHIPPED)** | 1599.00 | 160.73 | −6.33% | **+11.08%** |
| `d_cmp-clang` | 1599.00 | 134.29 | −6.33% | **−7.19%** |
| `d_sub-clang` | 1623.00 | 137.28 | −4.92% | −5.12% |

Two things `NOTES.md` does not say:

- **the factor on `large` is 11.9×** (57.80 → 4.86), not the 16× quoted for
  `small`; and
- **under clang on `large` the cheapest in-contract hardening is 7.2% FASTER
  than the unhardened bug.** That is a stronger version of p06's own thesis and
  it is missing.

`.memory/02-bench-rules.md`'s two-number rule is *publish the fixed spelling and
the cheapest found, both labelled, with the input named*. On `large` only one
number is published.

### M2 — 23% of gcc's published `+8.00·nrec` law is EXECUTED ALIGNMENT PADDING, and only 1.00/record is the divide

`NOTES.md:245` pins `R1h − R1, gcc = +8.00·nrec − 1.00·rzero + 1.00`, *"max
residual 0.0000 over all 77 blobs"*, and `NOTES.md:254` reads it as *"what a
per-record check should cost"*.

Per-instruction callgrind (`--dump-instr=yes`, `.temp/r47/cgins.py`), `large`,
12 records/call, the gate's own flags — the delta is +95.00/call exactly:

```
divq     0.00 →  12.00    +12.00/call   +1.000/rec   <-- THE SAFETY LINE
movzbl 282.00 → 330.00    +48.00/call   +4.000/rec
nopl/nop 25.00 → 47.00    +22.00/call   +1.833/rec   <-- EXECUTED .p2align PADDING
movb   130.00 → 154.00    +24.00/call   +2.000/rec
xorl    29.00 →  40.00    +11.00        cmpq −12.00   jae −12.00   movq +2.00
```

Rebuild both C rungs with a flag that changes no semantics and no work:

| gcc flag | R1 Ir/call | R1h Ir/call | Δ | Δ/rec | executed nops R1 / R1h |
|---|---:|---:|---:|---:|---|
| shipped (`-O3`) | 1988.00 | 2083.00 | **+95.00** | +7.917 | 25 / 47 |
| `-fno-align-loops` | 1963.00 | 2036.00 | **+73.00** | +6.083 | 0 / 0 |
| `-falign-loops=1` | 1963.00 | 2036.00 | +73.00 | +6.083 | 0 / 0 |
| `-falign-loops=32` | 2058.00 | 2153.00 | +95.00 | +7.917 | 95 / 117 |

**A semantics-free flag moves p06's exact, zero-residual, out-of-sample-validated
law by 23%.** `.memory/03-measurement.md:234` records the *static* nop caveat
("the raw count overstates the gap"); the **dynamic** one — executed alignment
padding inside a hot loop landing in a published `Ir` law — is nowhere.

Related and unreconciled in the file: `NOTES.md:62` (the pre-flight probe)
measures gcc `mod − bug = **+1.00**/record and `NOTES.md:245` measures
**+8.00**/record on the shipped tree, 8× apart, with no sentence joining them.
The honest decomposition is: **1.00 the divide, ≈1.83 executed padding, ≈5.08
the register pressure the `div` and its guard put on the header decode** (gcc
spills the decoded bytes: `mov %r15b,0x17(%rsp)`).

⚠ **The attribution of the *wall clock* to the divide survives, and I confirmed
it with the control `NOTES.md` §3b never ran** — see clean negative CN-2.

### M3 — "the twin is the SOLE catcher" and "caught by nothing but `spec.md`'s pin" are both false

`NOTES.md:592` (*"on p06 the twin is the **sole** catcher, which is the third
pattern where that has happened"*), `NOTES.md:871`, `NOTES.md:894-897`, and
`NOTES.md:870` (`b_scrmod_msonly` → *"nothing but `spec.md`'s contract pin"*).

I ran `harness/check.py`'s own comparison (`check.py:2209-2238`,
`vparse.by_name` + `norm_clause`) against `spec.md`'s pinned `verus.items`:

```
SHIPPED verus.rs   0 diffs
b_weakreq          2 diffs   scr_set_unchecked.requires      ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
                             slb_twin_scr_set_unchecked.requires   same
b_scrmod_msonly    1 diff    kernel.ensures ['r == r'] != pinned ['r == rotate_fold(...)']
b_tautology        1 diff    (same)
b_nored_msonly     1 diff    (same)
```

So **`b_weakreq` fails the `verus_contract` stage**, which runs *before*
`trusted_twins`. And `b_scrmod_msonly` **also breaks the `identity` pin** —
`n_fn` 174/166, `md5_fn 779c99de203c` against R4's 216/208 `897c52ff4005`
(`.temp/r47/ctl/b_scrmod_msonly.bin`, compiled 17/0).

The measured premise (*the shipped Verus configuration still reports 17/0*) is
true; the conclusion drawn about the **gate** is a non sequitur, and `NOTES.md`'s
own "caught by" column uses gate-level vocabulary in the very next row.

**Failure scenario.** "Third pattern where the twin is the sole catcher" is
exactly the shape that goes into `.memory/04-verus.md` as a durable fact about
the gate's detection surface. It would be false, and it would be the third
recorded instance of a claim that may be false on the earlier two patterns for
the same reason (any clause weakening in a pinned item is caught by the contract
pin unless the pin is edited in the same commit). **Worth re-checking p02's and
p12's versions of this claim before recording p06's.**

Correct statement: *the twin is the sole **Verus-level** catcher; the contract
pin catches it too, and a clause weakening only reaches the twin stage if the
`spec.md` pin was edited in the same commit.*

---

## Minors

- **m1 — the task file's own citation.** `TASK_047_REVIEW.md:10` sends the
  reviewer to *"`.memory/05-layout.md` (**finding 16** — the layout modes)"*.
  `.memory/05-layout.md` is repo layout and naming; it contains no numbered
  findings and no `win32`/`jcc32`. The layout modes are
  `.memory/03-measurement.md:789-921`; "finding 16" is `RECAP.md`'s numbering.
  `.memory/01-ladder.md:348` warns about precisely this ("Numbering warning — 26
  stale citations exist"); this is the 27th.
- **m2 — `controls/verify_controls.sh`'s header documents controls that do not
  exist and expectations the pattern refutes.** Its comment block promises
  `a_nored_verus` and `b_msonly` (neither is generated) and states
  *"`b_msonly` MUST VERIFY … a memory-safety-only proof of this kernel accepts a
  bug that stays inside the scratch"* and *"`b_tautology` MUST VERIFY in both
  configurations"*. `NOTES.md` §10 measures the opposite of both.
  `.memory/05-layout.md` rule 11 makes this script the mutants' reproduction
  path, so its docstring is evidence, not decoration.
- **m3 — `b_scrmod`'s recorded error does not reproduce.** `NOTES.md:869` records
  *`precondition not satisfied` (at `lemma_three_reverses`) + `assertion failed`*.
  Two consecutive runs give **`Resource limit (rlimit) exceeded`** on the while
  loop (counts still 16/1). A mutant that fails by resource exhaustion is a
  weaker control than one that fails on an obligation, and the difference is
  invisible in the pinned counts.
- **m4 — `.copy_within(` is a forbidden spelling that the prover does NOT
  exclude, and it is not priced.** `spec.md`'s `idiom.why` claims *"IT IS STILL A
  FIAT AND ITS PRICE IS STILL PUBLISHED"*, and `NOTES.md` §8 prices `.reverse()`,
  `.rotate_left()` and `<[T]>::swap()`. `<[T]>::copy_within` **is** specified at
  the pinned vstd (`vstd/std_specs/slice.rs:235`; my probe returns
  `precondition not satisfied`, i.e. supported), so it is p13's *third* bucket —
  fiat, price unpublished. The stated reason is also inaccurate: `copy_within` is
  `ptr::copy` **within one slice**, not "the out-of-place rotate (rotate through
  a temporary)". (`from_le_bytes` and `chunks_exact` *are* excluded one layer
  down — I re-measured both — so those two are correctly disposed of.)
- **m5 — one committed gate figure is not reproducible.**
  `results/gate/p06-rotate.json`'s `adversarial-past48.bin/c-gcc` stdout is
  `5645006182206458263`; my run gives `1380113329433944552`. That row reads
  uninitialised frame bytes past `scr`, so this is the pattern's own point rather
  than a defect — but a gate record carrying a number that changes every run
  should say so.

---

## Clean negatives — attacks that did NOT land (PROTOCOL rule 6)

**CN-1 — the missing layout population. BUILT, and p06's headline survives it
intact.** `common/layout/order.py:48` and `layout_gen.py:59` hardcode
`CELLS = ["safe_naive","safe_tuned","unsafe"]` and build with `rustc`, so the
engineer is right that neither can touch a C cell. I built one anyway
(`.temp/r47/clayout.py`): the lever is a **pad object**
(`asm(".text\n.space N")` linked first, `N = 0,16,…,464`), which shifts every
later `.text` symbol without touching a byte of `kernel.o`. Controls, exactly the
ones `layout_gen` asserts: `n_fn` single-valued per cell (190/200/175/171 —
matching `NOTES.md` §1), `md5_fn_norel` single-valued, 30 distinct kernel
addresses spanning both `addr % 32` residues. Every loop's `(win32, jcc32)`
geometry flips over the population, so it is a genuine layout population and not
a null.

| | `small` median | `large` median |
|---|---:|---:|
| `c-gcc` / `c-gcc-h` | 234.55 / 277.75 | 152.37 / 240.45 |
| `c-clang` / `c-clang-h` | 219.48 / 241.39 | 144.70 / 160.73 |

```
R1h − R1  gcc    +18.15% (small)   +57.95% (large)     [NOTES: +19.46 / +57.09]
R1h − R1  clang  +10.36% (small)   +11.03% (large)     [NOTES:  +9.78 / +10.56]
pairwise P(A>B)  900/900 = 100.0%, both compilers, both inputs
worst case (min hardened vs max buggy)  +15.50 / +8.41 (small), +53.68 / +5.32 (large)
mode-matched by addr%32  gcc small 17.8% vs 20.2%; no sign flips anywhere
```

**No layout in the population makes the effect disappear, shrink below the
±3% inter-binary null, or change sign.** Item 1's worry is closed; the
engineer's "argument, not a measurement" is now a measurement and it agrees with
the argument. Do not re-run this.

**CN-2 — the mechanism for the wall clock. CONFIRMED by the control `NOTES.md`
§3b never ran on `large`.** `d_cmp-gcc` contains the guard *and* the `div`
instruction but never executes the `div` on either perf input. On `large` it
costs **+7.40 ns** where `c-gcc-h` costs **+88.08 ns**, so **91.6% of gcc's
`large` hardening cost is the executed divide** — 6.72 ns per record for one
`div r64`. The throughput column makes it plainer than a cycle estimate does:
`c-gcc` 13.05 Ir/ns, `d_cmp-gcc` **13.14** Ir/ns, `c-gcc-h` **8.66** Ir/ns.
(This also disposes of item 1's IPC worry: the two div-free gcc cells run at the
*same* instructions-per-nanosecond, so there is no anomalous IPC to explain; and
the cycle count in `NOTES.md:315` — "≈21–28 cycles at this box's 2.8–3.9 GHz
band" — rests on an unmeasured frequency, which the control makes unnecessary.)

**CN-3 — item 1's arithmetic in the task file is wrong.** `TASK_047_REVIEW.md:43`
derives *"the per-record `Ir` delta is +1.00, so ≈ 95 records/call"*. The shipped
gcc law is **+8.00/record**, not +1.00. Read out of the blobs: `small` = 5
records / 157 bytes / stride 201 / 64 identical windows; `large` = **12 records**
/ 52 bytes / stride 152 / 50 000 identical windows. `8·12 + 1 − 2 = 95` ✓, and
`88.10 ns / 12 = 7.34 ns/record`. Nothing needs 95 records and nothing needs
overlapping divides. The columns reconcile.

**CN-4 — item 3's "spelling artefact" suspicion does not land; the `32 Ir/record`
is a real bounds-check tax.** R2 writes `buf[off + p + k]`; R4 writes
`unsafe { *buf.get_unchecked(off + p + k) }` — the same expression with and
without the check, in the same order, with the same operands
(`safe_naive.rs:70-89` vs `unsafe.rs:75-97`). Confirmed with an oracle the
engineer did not use, p12's `controls/pads.py` `core::panic::Location` decoder:

```
safe_naive  pads=14   59:34 (scr_load's reslice) + the TWELVE header indexes
unsafe      pads= 2   65:34 (scr_load's reslice ONLY)
e_hdronly   pads= 2   59:34                          == R4's set
e_revonly   pads=14   == R2's set     e_foldonly  pads=14  == R2's set
ZERO pads anywhere for scr[a], scr[b-1] or scr[i], in any rung.
```

**The mechanism, not "it vanished":** `scr` is `[u8; 64]`, a compile-time
constant length; `r %= m` with `m = min(nelem, SCR)` hands LLVM `r < m ≤ 64`, so
every cursor in the three reverses satisfies `a < b ≤ 64` and all four checks per
swap fold to constants — no landing pad survives. `buf` is a runtime-length slice
indexed at the file-derived `off + p`, which nothing bounds, so twelve pads
survive. The byte-identity claims reproduce exactly: `e_revonly`/`e_foldonly`
`md5_fn 48e508ddf075` = shipped R2; `e_hdronly` `897c52ff4005` = shipped R4 = R5.

**CN-5 — every kernel-exclusive `Ir` figure in `NOTES.md` §1 reproduces
EXACTLY.** All eight: 3477 / 3518 / 2615 / 2570 / 2797 / 2958 / 2624 / 2624
(`small`) and 1988 / 2083 / 1707 / 1599 / 2120 / 1897 / 1725 / 1725 (`large`).
So does §1's cross-compiler caveat (`c-gcc − R4` = **+853** kernel-exclusive,
**+791** whole-program on `small`), and `R5 − R4 = 0.00` exactly on both.
So does the whole of §8's spelling-spread table, to the instruction:
`c_idx +80/+187`, `R3ship +334/+172`, `c_oneshot +335/+173`, `c_swap +490/+286`,
`c_reverse −358/+320`, `c_rotate −951/+314`, `c_r4inline −4/−8`, `e_hdronly +0/+0`.

**CN-6 — the parameter-free swap law holds OUT OF SAMPLE at two `m` nobody
swept.** Band R visits only `m = 32` and `m = 31`. I generated the same shape at
**`m = 20`** and **`m = 17`** (`.temp/r47/oos_swaplaw.py`, predictions written in
the docstring before the run) and measured R4's differenced marginal `Ir`:

```
m=20 (even)  r=0 : 2889.00      r even≥2 : 2897.00 (9/9)   r odd : 2961.00 (10/10)
             odd − even = 64.00 = 8 records × 8 Ir       even − (r=0) = 8.00
m=17 (odd)   r=0 : 2673.00      every r≥1 : 2681.00 flat (16/16)
             flat − (r=0) = 8.00 ; no parity term at all
```

Both predictions hit exactly. `swaps(m,r) = m + [m even AND r odd]` is real, has
zero fitted parameters, and is not in-sample-only.

**CN-7 — regime 1's identity across all eight cells reproduces, and so does
regime 2.** `adversarial-inarray`: `c-gcc` and `c-clang` both
`12407484466270198528`; the six checked cells and the model
`5453190234444350336`; `a_nored_safe_naive`, `a_nored_safe_tuned` (zero `unsafe`)
and `a_nored_unsafe` all print C's wrong value, exit 0. The gate's own
ASan+UBSan stage is **clean** on `adversarial-inarray`, `degenerate`, `small`,
`large` and **fires as declared** on all three `past` rows (`.temp/r47/gate.log`
:523-531). Regime 2 reproduces row for row: past1 `0 / 0 / 101 / 101 / 0`,
past48 `134 (canary) / 0 / 101 / 101 / 0`, pastfar `139 / 139 / 101 / 101 / 139`.

**CN-8 — `degenerate.bin` really reaches the `m == 0` division by zero, and the
`if (m != 0)` arm is load-bearing.** All eight cells agree on `degenerate`
(`3109437583815045504`). The same gcc hardened rung with that arm deleted
(`.temp/r47/ctl/kernel_noguard.c`) dies **SIGFPE, rc = 136** on `degenerate.bin`
and returns normally on `small.bin`. The pin is not decoration and the blob is
not a formality.

**CN-9 — the `_msonly` spec is NOT vacuous.** Two `assert(false)` probes into
`b_scrmod_msonly` — immediately after the mutated reduction and at the top of
`kernel` — both report `16 verified, 1 errors: assertion failed`
(`.temp/r47/vac/`). Together with `b_nored_msonly` genuinely failing
(`invariant not satisfied before loop`, reproduced in both configurations), the
memory-safety skeleton rejects a real bug and its context is consistent.

**CN-10 — `r %= SCR` really is memory-safe on every input.** After the mutation
`r ∈ [0, 63]`; `reverse(scr,0,r)` touches at most index `r−1 ≤ 62`;
`reverse(scr,r,m)` and `reverse(scr,0,m)` touch at most `m−1 ≤ 63`; the fold
reads `i < m ≤ 64`. `SCR` is a non-zero constant, so `m == 0` cannot divide by
zero. No counterexample exists at `m == 0`, `nelem > SCR` or on `degenerate`, and
the compiled mutant confirms it: `17 verified, 0 errors`, prints
`415744194194585216` on `adversarial-inarray` against the model's
`5453190234444350336`, and agrees on `small` / `large` / `degenerate`. The
engineer's refutation of the manager's `_msonly` design (**a proof quantifies
over all inputs, so a weaker spec cannot rescue an unsafe program — the
separation needs a PROGRAM change**) is **correct** and is worth recording.

**CN-11 — every `is not supported` claim in the report is true at the pinned
vstd**, re-run through `./verus_run.py` rather than read off the report:
`<[T]>::reverse`, `<[T]>::rotate_left`, `<[T]>::swap`, `chunks_exact`
(`ChunksExact`), `try_into` (`TryFromSliceError`), `u32::from_le_bytes` — all
`is not supported`. `core::mem::swap` → `2 verified, 0 errors`;
`split_at_mut` and `copy_from_slice` → supported (`precondition not satisfied`
only). So the `u8`-instead-of-`u32` deviation is genuinely forced, and `spec.md`
documents it where a reader meets it (`spec.md:37-48`, in the Window layout
block, not buried in `NOTES.md` 10a).

**CN-12 — the `.reverse()` exclusion price and its direction test hold.**
`<[u8]>::reverse` is not "specialised" in std, but LLVM **auto-vectorises** it:
`c_reverse`'s kernel is 512 instructions with `movdqa`/`movdqu`/`pshufd`, where
every shipped rung's rotate is scalar. `c_rotate` additionally calls
`memmove@GLIBC_2.2.5`, a routine no other rung calls. The measured prices
(`−358 / +320` and `−951 / +314`) reproduce, so the 1031 Ir/call figure is right,
and the direction test passes: excluding them makes p06's published safety figure
**larger**, i.e. against the author's thesis.

**CN-13 — `required_absent: 2` is exactly the bug's own two lines.**
`required[0]` `r %= m;` and `required[1]` `if (m != 0)`, both scoped `c`, both
missing from `c/kernel.c` and present in `c/kernel_hardened.c`.
`required_pins_nothing: 0`, `forbidden_hits: 0`, `no_rung_entries: 0`. Nothing is
a pin wearing another name.

**CN-14 — `d_cmp-clang` vs `c-clang-h` is real and is BIGGER than published.**
`NOTES.md:347` calls it *"the tightest statement of 'instruction counts are not a
cost model' this project has produced"* on `small` (identical `Ir`, 8.5% apart).
Kernel-exclusive, on the population: **2570.00 both** on `small` (−8.34% in ns)
and **1599.00 both** on `large` (**−16.45%**). Two different programs
(`n_fn` 175 vs 171, distinct `md5_fn_norel`), one instruction count, a 16% time
difference. The claim survives and doubles.

---

## The manager's least-sure call, item 2 — answered with the measurement

> *"I read 'R3 dearer than R2 per byte' as an anomaly worth a blocker, but it may
> be the honest behaviour of a correctly-tuned rung … in which case the finding
> is that p06 is the pattern where finding 3's 'always quote R3' gives the wrong
> answer, and that is a `.memory/` correction rather than a defect in the
> pattern. Tell me which."*

**Neither. It is a defect in the pattern, and finding 3 gives exactly the right
answer on p06 — it is p06 that does not follow it.**

Finding 3's rule is not "always quote R3"; it is *"write at least two independent
in-contract R3 spellings and **quote the cheaper**"* (`.memory/01-ladder.md:435`).
Applied to p06, the cheaper in-contract R3 is `c_idx` at **13–17 Ir per record and
0.00000 per byte**, against R2's 33.6 per record and the shipped R3's
`2·bytes + α(m mod 8)·nrec + 1`. So:

- quoting the **cheapest in-contract R3** understates nothing and overstates
  nothing — it is *less* than R2, which is the ordinary shape;
- the "R3 > R2 inversion" exists only for the shipped spelling and only on
  `small`;
- the `2.00 Ir/byte` term is the `zip`/`Rev` adaptor's exhaustion tests and
  contains **zero** bounds checks (identical panic-pad sets).

**No `.memory/` correction to finding 3 is warranted. `NOTES.md:248`,
`NOTES.md:420-425` and `README.md:41-47` need one, and p06's `.memory` entry must
not be written from them.** The prescription in item 2 was right to smell an
anomaly and wrong about where it was: the anomaly is not "R3 is dearer than R2",
it is "the shipped R3 is one point in a class whose cheapest member has a
different asymptotic shape, and the pattern published the point."

---

## What I did NOT do, and what I am unsure about

- **I did not re-spell any rung.** `c_idx`, `r4_splitat`, `r2_splitat` and
  `v_scrload_verified2.rs` are controls under `.temp/r47/`; nothing in
  `patterns/p06-rotate/` changed. `.memory/02-bench-rules.md` forbids re-shipping
  a rung because a cheaper in-contract spelling was found — B2 is a **reporting**
  finding, not a request to change R3.
- **I did not price p02's or p08's trusted copy wrappers.** B1 shows p02's
  *contract* discharges without one; whether p02's exec text moves is unmeasured
  (its body is `copy_nonoverlapping`, p06's is `copy_from_slice`, and only p06's
  is measured byte-identical).
- **I did not re-check p02's and p12's "the twin is the sole catcher" claims.**
  M3 makes them suspect for the same reason; somebody should.
- **The `α(m mod 8)` structure of `R3ship − R4` still has no mechanism.** I
  measured that `c_idx` has an `m mod 4` structure instead
  (`α' = {13,15,16,17}`), which is the fold's unroll boundary rather than
  anything about safety, but I did not disassemble the fold to prove it.
- **The Rust-side wall clock is inside the null on `small`** and I did not build
  a Rust layout population — `common/layout/` already can, and `NOTES.md` §11
  already declines to headline those rows.
- **The frequency of the box is not measured**, so no cycle count here is
  independent; I quote ns and Ir/ns instead.
- **`b_scrmod`'s rlimit failure** (m3) I did not chase with `--profile`.

## Housekeeping

Running `harness/check.py p06` rewrote the committed
`results/gate/p06-rotate.json` (ASLR-dependent UBSan addresses and the
nondeterministic `adversarial-past48/c-gcc` stdout — m5). **I restored it with
`git checkout -- results/gate/p06-rotate.json`; `git status --porcelain` is
clean.** My run's copy is kept at `.temp/r47/gate-p06-reviewer-run.json` and its
log at `.temp/r47/gate.log`. No `git add`, no `git commit`, no history-mutating
command was run.
