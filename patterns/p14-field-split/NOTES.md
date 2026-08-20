# p14 — delimiter-framed field splitter: findings

Read `spec.md` first; this file records what was measured, in the order it was
measured, and what it cost.

**Two `Ir` conventions appear here and every figure says which**
(`.memory/03-measurement.md`). The **table** column is
`results/p14-field-split.json`'s *kernel-exclusive* `Ir`; every **law and every
matched difference** is a *whole-program marginal*,
`(Ir(n_iters=6000) − Ir(n_iters=2000)) / 4000` on the same blob and the same
binary (`controls/sweep_ir.py`), which cancels start-up, the payload load and the
driver's `println!` digit term and — unlike the kernel-exclusive column —
**includes the `memcpy` body**.

## 0. THE PRE-FLIGHT — the bug class, settled by measurement before any rung existed

TASK_049 §0 named the bug class as the first deliverable and ranked three
candidates, holding the ranking loosely. **The catalogue's row and all three of
the manager's candidates were measured and all four were rejected**, on a
standalone six-kernel C probe with no driver and no pattern
(`.temp/p14/probe1_kernel.c`, `probe1_main.c`, `probe1_gen.py`, `probe1_ir.py`,
`probe1_repeat.py`) plus four `rustc` compilations (`.temp/p14/probe2_borrow.rs`).
What ships is a fourth thing.

All six probe kernels implement the same candidate wire format and the same
per-call scratch copy, so their columns are comparable:

| probe kernel | what it is | disposition |
|---|---|---|
| `k_cap` | the field-count bound PRESENT | **ships as R1h** |
| `k_bug` | the bound omitted, and nothing else | **ships as R1** |
| `k_strtok` | libc `strtok`, which COLLAPSES delimiter runs | ships as a priced control |
| `k_unbnd` | TASK_049 candidate 1: the scan bounded by a NUL sentinel instead of by `i <= m` | rejected, = p11 |
| `k_life` | TASK_049 candidate 3: descriptors are POINTERS into a callee-local scratch | rejected, = p08 |
| `k_mutate` | the CATALOGUE row: `strtok`'s in-place mutation, on `buf` | rejected — measures its own steady state, §0a |

### 0a. The catalogue's row — "in-place mutation + aliasing" — measures the WRONG WORKLOAD. It is NOT excluded by the harness.

`.memory/06-catalogue.md` gives p14's bug class as *"in-place mutation +
aliasing"*. **Neither half survives contact with this benchmark** — but the
reason the first half fails is **not** the one this section carried until
TASK_050, and the difference matters to every later pattern, so the corrected
claim is stated first:

> ⚠ **RETRACTED (TASK_049_REVIEW B2, measured).** This section used to say *"a
> rung that mutates `buf` cannot be measured at all"* and *"EXCLUDED BY THE
> HARNESS"*. **That is false.** Nothing in `harness/` enforces purity, and both
> stages a mutating rung has to pass are well defined for it. What the repeat
> protocol actually does is drive the mutation into a **one-call steady state**,
> after which the benchmark measures an *already-tokenised* buffer — a different
> workload from the one the pattern names. The measurement below stands; the
> inference did not, and it was aimed at `.memory/06-catalogue.md`, where it
> would have been recorded as a property of the *infrastructure*.

**A kernel that mutates the INPUT is not a function of its arguments.** The driver
calls `kernel(buf, k*stride, stride)` `n_iters` times, and on a one-window blob
`k` is always 0, so a pure kernel satisfies `acc(n) = r · Σ_{j<n} 31^j` exactly.
`k_mutate` writes NUL over the delimiters of `buf` itself — the textbook `strtok`
idiom — and the identity fails on the first repeat, on both compilers
(`probe1_repeat.py`, one window, `stride=516`; re-run at TASK_050 from the
committed generators into fresh scratch, **byte-for-byte identical on both
compilers**):

```
kernel                      n=1                    n=2                    n=4  repeat-pure?
cap        13685950752790025653   13675310393961133728    3120074435700344128  True
bug        13685950752790025653   13675310393961133728    3120074435700344128  True
strtok     13685950752790025653   13675310393961133728    3120074435700344128  True
unbnd      13685950752790025653   13675310393961133728    3120074435700344128  True
life       13685950752790025653   13675310393961133728    3120074435700344128  True
mutate     13685950752790025653    2980032160863588016    8033375426539182928  False
```

**What that measurement licenses, and what it does not.** It licenses *"the
checksum of a payload-mutating kernel is not `r · Σ31^j`"*. It does **not**
license *"such a kernel cannot be measured"*, and three measurements say why not:

1. **The mutating kernel reaches a steady state after exactly ONE call**, and the
   closed form is verifiable from the table above without rebuilding anything.
   With `r1 = 13685950752790025653` and
   `r2 = acc(2) − 31·r1 = 2990672519692479941`, substituting `r3 = r4 = r2` gives
   `31·(31·acc(2) + r2) + r2 = 8033375426539182928` — **`acc(4)` exactly.** After
   call 1 every delimiter in `buf` is already NUL, so every later call does the
   same thing to the same bytes. `acc(n)` is a closed form in `(r1, r2, n)`:
   deterministic and predictable, just not the *pure* one.
2. **`harness/measure.py`'s marginal is exactly defined, not meaningless.** gcc,
   the same one-window blob, `(Ir(6000) − Ir(2000))/4000`:

```
cap 9779.0180   bug 9265.0180   strtok 10356.0180   mutate 9044.0000
```

   The mutating kernel's marginal is **integral with zero residual** — *cleaner*
   than the three legal ones, whose `+0.0180` is the driver's `println!`
   digit-count term.
3. **Nothing in `harness/` enforces purity.** `check.py`'s checksum stage
   compares each cell's stdout against **`model.py`'s own simulation** and
   against the other cells; the identity `acc(n) = r·Σ31^j` appears nowhere in
   `harness/` (`grep -rn 'repeat\|idempot\|purity' harness/` returns nothing
   relevant) — it lives only in `probe1_repeat.py`, which is p14's own probe. The
   only obstacle is **p14's own `model.py:143-147`**, which memoises
   `self._win[k]`; that is a p14 design choice, not a harness constraint.

**So the honest objection is different, and it is stronger.** After call 1 the
delimiters are gone, so calls 2…n scan a line with **zero delimiters: one field
of length `m` instead of four.** The repeat protocol does not refuse to measure
an in-place tokenizer — **it measures the wrong workload**, tokenising an
already-tokenised buffer, and the gap is visible in the marginals above (9044
against `cap`'s 9779 on the same bytes).

⚠ **What the repeat protocol does and does not exclude, stated plainly, because
this reaches beyond p14.** It does **not** exclude a payload-mutating rung: a
later pattern that wants one (`strsep`, an in-place unescape, anything
CWE-787-shaped that writes into its input) is not blocked by `harness/`, and
rejecting it *on that ground* would be rejecting it on a constraint the harness
does not have. What the protocol **does** do is fix the workload of calls 2…n to
whatever call 1 left behind. Two repairs exist for that, and both are available:
write a `model.py` that **simulates the mutation** instead of memoising the
window, or **declare the steady state as the measured workload** and say so in
`spec.md`. Neither repair exists for *"the harness forbids it"* — which is the
practical reason the wrong reason was worth correcting.

⚠ **The other precise claim, because a looser one would be false.** In-place
mutation *of the scratch* is perfectly legal and is what `k_strtok` does — and
`k_strtok` agrees with `k_cap` on the perf blob to the bit. So: **an in-place
tokenizer of the SCRATCH is not a bug at all, it is the correct kernel**, and an
in-place tokenizer of the INPUT is measurable but measures its own steady state.
Either way there is nothing here for p14 to measure, which is why the decision
below is unchanged — only its reason is.

**And the "aliasing" half is a compile-time rejection, which is p08's result and
has no run-time cost to price.** `probe2_borrow.rs` puts four spellings to
`rustc` 
(`rustc --edition 2021 --crate-type lib --cfg aN probe2_borrow.rs`):

```
===== a1 =====   tokens as &[u8] into a scratch still being NUL-overwritten
error[E0506]: cannot assign to `scr[_]` because it is borrowed
===== a2 =====   tokens that outlive the scratch (TASK_049 candidate 3)
error[E0515]: cannot return value referencing local variable `scr`
===== a3 =====   (offset,length) descriptors, mutation legal
  (compiles)
===== a4 =====   (offset,length) descriptors, the FIELD-COUNT BOUND OMITTED
  (compiles)
```

**That table is the whole §0 decision.** a1 and a2 are rejected by the borrow
checker, so on those bug classes safe Rust has **no run-time check and therefore
no cost to measure** — `.memory/01-ladder.md` finding 7's exact sentence about
p08. a4 compiles, and at `-O3` with `debug-assertions=off` it *panics*:

```
thread 'main' (1471884) panicked at probe2_borrow.rs:113:13:
index out of bounds: the len is 16 but the index is 16
rc=101
```

**Only the field-count bug puts a run-time check on the Rust side of the ladder,
so only the field-count bug has a safety cost for this project to price.** That
is the criterion, and it is a measurement rather than a preference.

### 0b. Candidate 1 (the scan a delimiter does not bound) IS p11, confirmed by building it

`.memory/02-bench-rules.md`'s threshold table lists p14 as *"a delimiter is not a
bound; the sentence reaches its scan's `i < len`"*, marked **not as stated**.
Settling it was part of this task, and the answer is that the sentence is right
about the *mechanism* and that the mechanism is p11's.

`k_unbnd` drops `i < m` from the scan and stops on `DELIM` or on a NUL. On
`nonul.bin` — one 64-byte line with no delimiter and no NUL — it reads past the
scratch:

```
probe1_kernel.c:241:20: runtime error: index 64 out of bounds for type 'uint8_t [64]'
==1471193==ERROR: AddressSanitizer: stack-buffer-overflow ... READ of size 1
    #0 ... in k_unbnd ... probe1_kernel.c:241
```

and at `-O3`, on both compilers, it prints **the same answer as `k_cap`**
(`8709970208371219456`), because the byte after the array happened to be zero.

⚠ **What `k_unbnd` does, exactly — the looser sentence this paragraph carried
until TASK_050 was wrong** (TASK_049_REVIEW m3). It does **not** merely delete
`i <= m`. It replaces `while (i <= m)` with `for (;;)` **and adds a NUL
sentinel**, `if (scr[i] == 0) break;`, beside the `DELIM` exit
(`.temp/p14/probe1_kernel.c:238-249`). **The added sentinel is exactly what makes
it p11**: p11's scan is a sentinel-bounded `strlen`, and its harm is the
out-of-bounds READ that happens when the sentinel is not there — which is what
`nonul.bin` supplies. So the conclusion below is right and the one-line
description was not: the harm is an out-of-bounds READ and the loop body is
p11's `strlen` shape, but the difference from the shipped scan is a
*bound-for-sentinel substitution*, not a deletion.

**`.memory/01-ladder.md` finding 9 already
owns that measurement, including the 2.00-vs-3.00 Ir/byte constant that depends
on the loop's other exit test.** A second copy is worth little, so candidate 1 is
rejected — and the threshold-table row is settled as *the mechanism is real and
it is p11's, so p14 must put its bug in the OUTER loop*. **Every rung of the
shipped pattern therefore carries `i <= m`, and `spec.md`'s `required[8]` pins it
so the point is settled by grep.**

### 0c. Candidate 3 (a token outliving its buffer) — rejected, and NOT for the reason predicted

TASK_049 ranked this second and argued it would be *"observably wrong rather than
unobservable, which is strictly stronger"* than p08. **Both halves of that were
tested and the prediction is wrong.**

`k_life`'s helper builds the scratch in **its own frame** and hands back pointers
into it; `k_life` then folds through them after the helper has returned.

1. **It is NOT observably wrong.** At `-O3`, on both compilers, `k_life` prints
   `6394644849983628767` — byte-identical to `k_cap`'s answer on the same blob.
   The dead frame is not reused between the return and the read, so the bug
   executes and has no consequence. That is p08's result exactly
   (`.memory/01-ladder.md` finding 7: *"the UB executes and is unobservable"*).
2. **The `noinline` worry is unfounded, which is the one thing that came out
   BETTER than predicted.** Removing `__attribute__((noinline))` does not erase
   the UB: gcc at `-O1 -fsanitize=address` still reports it, as
   `stack-use-after-scope` rather than `stack-use-after-return`, and at `-O3` the
   helper symbol is gone (`nm | grep -c split_line` = 0 on both compilers) while
   the answer is unchanged. So a lifetime bug *can* be modelled without a
   measurement-distorting `noinline` helper. Recorded because it is the opposite
   of what was expected and a later pattern may want it.
3. **What actually kills it is the DESCRIPTOR TYPE, and it forks the ladder.**
   The lifetime bug exists only if the descriptor is a *pointer*. Safe Rust
   cannot hold one (`E0515`, above), so R2 and R3 must hold `(offset, length)` —
   and with offsets **there is no bug and no check**. R4 could reproduce it with
   raw pointers, but `as_ptr`, `add` and `from_raw_parts` are all
   `is not supported` at the pinned vstd (`.memory/04-verus.md`'s census), so R4
   would have no verifying R5 twin and **would not be a rung** (TASK_026 §0 item
   3). So four of the six Rust cells would change algorithm and the pattern would
   have no priceable safety line anywhere on the ladder.

   ⚠ **Re-run independently at TASK_049_REVIEW (CN5) and it holds** — this is
   *not* the "R4 is chained to the prover" wrong explanation that p13 got caught
   by: `<[T]>::as_ptr` and `core::slice::from_raw_parts` both answer
   `` is not supported ``, and `*p` / `*p.add(i)` answer *"The verifier does not
   yet support … dereferencing a raw pointer."* ⚠ **One route is untried and is
   flagged as open, not as settled**: the error text points at `vstd::raw_ptr`'s
   permissioned interface, which needs a `PointsTo` token that a stack local
   `[u8; 64]` cannot supply. Nobody has tried it. It is not expected to change
   the answer, and it has not been measured.

**Rejected, on 1 and 3.** It is p08 with an extra hazard, not a stronger p08.

### 0d. Candidate 2 (delimiter-run semantics) — kept, but PROMOTED from the bug to its TRIGGER

`strtok(3)` collapses a run of delimiters into a single separator. This kernel's
partition does not, and neither does `strsep(3)`, Rust's `<[T]>::split`, or
`bytes.split`. **Measured on real glibc `strtok`**, same bytes, same table
(`probe1-gcc`, the `run-d*` blobs; `cap` is the shipped semantics with the bound,
`bug` is without it):

```
blob         cap                    bug                    strtok
run-d01      15425333969939807232   15425333969939807232   15425333969939807232
run-d04      17202008010207032448   17202008010207032448   10745889878602438912
run-d15      1934082676653332736    1934082676653332736    10745889878602438912
run-d16      15163305334018386560   15827865575719978624   10745889878602438912
run-d20      15163305334018386560   13484424802367379456   10745889878602438912
run-d32      15163305334018386560   8115663437400302592    10745889878602438912
run-d49      15163305334018386560   4029163846808646528    10745889878602438912
```

Two readings, and both ship:

- **`strtok` diverges from `cap` at FOUR adjacent delimiters** and stays constant
  from there on, because a run of any length collapses to one separator and the
  line yields two fields whatever the run's length.
- **`bug` diverges from `cap` at SIXTEEN delimiters**, exactly `MAXTOK`, and not
  at fifteen. Under ASan+UBSan at the gate's own flags (`gcc -O1 -g
  -fsanitize=address,undefined -static-libasan -static-libubsan`):

```
run-d15    cap    rc=0    clean
run-d15    bug    rc=0    clean
run-d16    cap    rc=0    clean
run-d16    bug    rc=1    runtime error: index 16 out of bounds for type 'size_t [16]' ...
==1471085==ERROR: AddressSanitizer: stack-buffer-overflow ... WRITE of size 8
    #0 ... in k_bug ... probe1_kernel.c:131
  This frame has 2 object(s):
    [32, 160) 'tl' (line 102) <== Memory access at offset 160 overflows this variable
```

**So on `a,,,,,,,,,,,,,,,,z` the choice of library routine is the difference
between a correct parse and a stack-buffer-overflow WRITE.** That is candidate 2
with a memory-safety consequence attached, which is more than the *"library axis
on semantics"* TASK_049 asked for — and it is why `strtok(` is in `forbidden`
with a priced control rather than in a rung.

⚠ **The counterweight, which must ship with it: collapse changes WHICH inputs are
dangerous, not WHETHER the guard is needed.** An alternating line `a,a,a,...` has
no runs to collapse, so both contracts produce `⌈m/2⌉ + 1` = 33 fields on a
64-byte line — more than double `MAXTOK`. `adversarial-alt33.bin` is that row and
it exists to stop the overclaim.

### 0e. THE DECISION, and the wire format that expresses it

**p14's bug class is: an unbounded FIELD COUNT against a fixed descriptor table,
triggered by delimiter density.** The wire format is one `u32` line count, then
per line one `u32` length and its bytes; the kernel copies `m = min(llen, 64)`
bytes into a fixed `scr[64]`, splits on `,` recording one length per field into a
fixed `tl[16]`, and folds count/lengths/content. `spec.md` has it exactly.

**Why this and not the alternatives, in one sentence each.** It is the only one
of the five that leaves a *run-time check* on the safe-Rust side of the ladder
(0a); its bound is a **count of a byte value** and therefore the first bound in
this project that no length implies and no hoist can remove; and it carries
candidate 2 as its trigger, so the library-contract result comes free (0d).

**What the bug does in each of the eight cells**, measured on the shipped tree at
`-O3 isolated` (`c-gcc`/`c-clang` are R1; the rest are checked):

| input | c-gcc | c-clang | c-gcc-h | c-clang-h | safe_naive | safe_tuned | unsafe | verus |
|---|---|---|---|---|---|---|---|---|
| `small`, `large`, `degenerate`, `adversarial-stride3` | = model | = model | = model | = model | = model | = model | = model | = model |
| `adversarial-run17` (17 fields) | wrong, exit 0 | wrong, exit 0 | = model | = model | = model | = model | = model | = model |
| `adversarial-many` (8 × 21 fields) | wrong, exit 0 | wrong, exit 0 | = model | = model | = model | = model | = model | = model |
| `adversarial-alt33` (33 fields) | wrong, exit 0 | **SIGSEGV (139)** | = model | = model | = model | = model | = model | = model |
| `adversarial-full65` (65 fields) | wrong, exit 0 | **SIGSEGV (139)** | = model | = model | = model | = model | = model | = model |

p12's magnitude ladder, in a new unit: the rungs of the ladder are **descriptors
past the table**, 1 / 5 / 17 / 49, i.e. 8 / 40 / 136 / 392 bytes. §7 has the
per-rung table with the sanitizer column and the delete-the-check controls.

### 0f. The cost model, pre-registered on the probe

Marginal `Ir` per call over a 4 × 5 grid of (bytes per line `m`, fields per line
`t`) at eight lines per window, gcc `-O3`, `probe1_ir.py`. Read off the grid
rather than fitted:

- the step in `m` is **exactly 17.75 Ir per line byte** at every `t`
  (`3171 → 5442.98 → 7715.02 → 9418.98` at `t = 1`, three consecutive steps);
- the step in `t` is **exactly 15.00 Ir per field** at every `(m, t)` on the grid
  **except** `(m=16, t=16)`, where 15 of the 16 fields are EMPTY and the step is
  5.625 — i.e. an empty field costs **exactly 5.00 less** than a non-empty one;
- so `Ir(k_cap) = 779 + 8·(17.75·m + 15.00·t) − 5.00·empties`, exact on all 20
  grid points.

**And the difference between the two probe kernels is exactly**

```
k_cap - k_bug = 8*(1.00*m + 2.00*t) - 30
```

with zero residual on all 20 points. **That is the shipped pattern's gcc law,
predicted before a single rung existed**: §3a measures
`c-gcc-h − c-gcc = 1.00·bytes + 2.00·fields − 3.00` on 66 blobs the probe never
saw, and the two per-regressor coefficients are the same numbers. (The constant
differs, `−30` per 8-line call against `−3.00` flat: the probe's driver has a
`strcmp` dispatch the shipped one does not, so its per-call constant is not the
pattern's.)

Two things the probe put on the table before any rung existed, and §3a′ and §9
test both on the shipped tree:

1. **the safety line's cost has a per-BYTE component that is not the safety
   line** (`1.00·m`), which `.memory/03-measurement.md` trap 3 says must be
   attributed mnemonic by mnemonic before it is named after a mechanism — §3a′
   does, and finds `−1.00` executed NOP per line hiding inside a null
   coefficient; and
2. **at fixed total bytes, sweeping `t` sweeps the amortisation denominator
   directly.** That is the axis `sweep-t*` exists for. ⚠ **The probe did not
   predict the DIRECTION and the shipped measurement is the counter-intuitive
   one** — §9a: more fields at constant bytes makes the safety tax SMALLER,
   because R4 loses its unroll.

## 1. Every rung's scan is a SCALAR byte loop, and no rung vectorises the split

`objdump` of the shipped `-O3 isolated` kernels. The `vec` column of
`results/tables/p14-field-split.md` is `xmm` in all eight cells and **every one
of those uses is the zero-fill of `scr[64]` and `tl[16]`**, not the delimiter
search:

| cell | vector instructions inside `kernel` |
|---|---|
| `c-gcc`, `c-gcc-h` | `movaps` ×4, `pxor` ×1 |
| `c-clang`, `c-clang-h`, `safe_naive`, `safe_tuned`, `unsafe`, `verus` | `movaps` ×12, `xorps` ×1 |

No `pcmpeqb`, no `pmovmskb`, no `pcmpistri`, no AVX in any cell. That is the
measurement `model.py`'s `work_per_call` docstring rests on when it keeps the
harness's default `0.25 Ir/byte` floor, and it is checked rather than argued.

**The scan loop bodies, read off the listing** (per scanned byte, non-delimiter):

```
R2 safe_naive   inc %rcx ; cmp %rcx,%rax ; je ; cmp %rcx,%rbp ; je ;
                cmp $0x3f,%rcx ; ja <panic> ; cmpb $0x2c,0x20(%rsp,%rcx,1) ; jne     9
R4 unsafe       inc %rdx ; cmp %rdx,%rcx ; je ; cmp %rdx,%rbp ; je ;
                             cmpb $0x2c,0x30(%rsp,%rdx,1) ; jne                      7
```

**The difference is exactly `cmp $0x3f,%rcx ; ja`, 2.00 Ir per scanned byte** —
`.memory/01-ladder.md` finding 9's `2.00` constant on a fifth kernel.

⚠ **And p14 is a datum against the stated discriminator.** Finding 9 says which
of `2.00` / `3.00` you get *"is decided by the loop's OTHER exit test"*, and
p14's scan has **two** other exit tests (`i <= m` and the `i == m` virtual
delimiter) and still costs `2.00`. The mechanism the listing shows is narrower
than the rule as written: `scr` is a **fixed-size local at a compile-time-constant
frame offset**, so the checked access is `cmp $0x3f` against a *literal* and needs
no `lea` — where p11's scan indexed a runtime buffer base and did. **The
discriminator is whether the base is a constant, not how many exit tests there
are.** Stated as a sharpening, not a refutation: both p11 readings are consistent
with this one.

## 2. The fold is order-sensitive over three quantities, and each catches a
   different wrong partition — the THIRD independent reason for the rule

`spec.md` has the argument; this is the measurement. `controls/gen_controls.py`
builds two fold mutants from `safe_naive.rs` by exact-string deletion, and
`controls/verify_controls.sh` runs them against `model.py` on all eight matrix
inputs:

| mutant | what it deletes | disagrees with `model.py` on |
|---|---|---|
| `m_nolen` | `acc = acc*31 + tj` — the field LENGTH | alt33, many, run17, degenerate, large, small — **6 of 8** |
| `m_nocount` | `acc = acc*31 + nt` — the field COUNT | alt33, full65, many, run17, degenerate, large, small — **7 of 8** |

Two things worth stating precisely.

**Tokenising moves no byte**, so a fold over the concatenated *content* alone is
identical for every possible set of field boundaries. That is why the length fold
exists, and it is p14's contribution to the full-extent-fold rule:

- TASK_004_REVIEW's reason is **elision** — a fold that reads part of the result
  lets the optimiser delete the rest;
- p06's is **invariance** — three reverses compose to a permutation, so a sum- or
  xor-fold cannot see a permutation bug;
- p14's is **partition-blindness** — a content-only fold cannot see a *boundary*
  bug at all, because every partition of a line yields the same bytes in the same
  order.

Three patterns, three independent arguments, one rule. Quote all three whenever
it is quoted.

⚠ **`m_nolen` agrees with the model on `adversarial-full65`, and the reason is
not that the mutant is harmless.** That input's line is 64 delimiters, so every
one of its 16 recorded fields has length **0**; the deleted operation is
`acc = acc*31 + 0` applied to an accumulator that is still 0, which is the
identity. **A mutant's detection is input-dependent, and a mutant table without
the inputs beside it is an adjective.** `m_nocount` catches that row because the
count is 16 and not 0.

## 3. What the safety line costs — the headline, and it is a LAW

**Convention.** The table column in `results/p14-field-split.json` is
kernel-exclusive `Ir`; every law and every matched difference below is a
**whole-program marginal**, `(Ir(6000) − Ir(2000)) / 4000` on the same blob and
binary (`controls/sweep_ir.py`), which cancels start-up, the payload load and the
driver's `println!` digit term and — unlike the kernel-exclusive column —
**includes the `memcpy` body**.

⚠ **p13's blocker 3 applies here and it is load-bearing: the rungs do NOT all
call the same libc routines** (`bulk_calls` at `-O3 isolated`, from the gate's
own stage 3a):

| cell | `bulk_calls` inside the kernel symbol |
|---|---|
| `c-gcc`, `c-gcc-h` | **none** — gcc inlines the copy |
| `c-clang`, `c-clang-h` | `memcpy@plt` |
| `safe_naive`, `safe_tuned`, `unsafe`, `verus` | `memcpy@GLIBC_2.14` |

p06 predicted this would recur and it did. So the kernel-exclusive column is
comparable **within gcc**, **within clang** and **among the four Rust rungs**,
and not across those groups; every same-compiler difference is identical under
both conventions because the `memcpy` term cancels. **Every figure below is a
same-compiler or same-language difference.**

### 3a. gcc: `R1h − R1 = 1.00·bytes + 2.00·fields − 3.00`, exact on 66 blobs — WITH ITS DOMAIN, WHICH IS `nt ≤ MAXTOK` ON EVERY LINE

⚠ **State the domain first, because the law is fitted entirely inside the regime
where the safety line never executes** (TASK_049_REVIEW M1). Every one of the 66
sweep blobs has **at most `MAXTOK` fields per line**. Counted off the blobs
themselves rather than off `gen.py`: the **maximum fields on any line over the 66
sweep blobs is exactly 16**, and `small` reaches 12, `large` 3, `degenerate` 16 —
against `adversarial-run17`'s 17, `-many`'s 21, `-alt33`'s 33 and `-full65`'s 65.
A line of exactly 16 fields *fills* the table and does not trip the guard
(§7 reading 1), so **`if (nt == MAXTOK) break;` never executes anywhere in the
fit set or in any of the three perf rows.** The law is the cost of
a **never-taken branch**: `+1.00` per byte of gcc's hardened scan geometry and
`+2.00` per field of guard *evaluation*, and `0.00` of it is the guard being
*taken*. Quote the law with the clause `for inputs with at most 16 fields per
line`; §3a″ is what happens outside it and it is not a continuation of this law.

`controls/fit.py` over the whole sweep, four regressors, **max |residual|
0.0000, rms 0.0000 over 66 points**:

```
c-gcc-h - c-gcc: -3.00000*const + -0.00000*nline + 1.00000*bytes + 2.00000*fields
    max |residual| 0.0000 over 66 point(s); rms 0.0000
```

⚠ **The leave-one-length-out hold-out is NOT evidence for this law and is not
quoted as such** — it cannot fail, provably. §9c has the proof; read it before
quoting a hold-out figure from this pattern.

**What is evidence** is that the law predicts inputs it was not fitted on and
could have been wrong about. The two shipped perf rows are **not in the sweep**:

| input | `1.00·bytes + 2.00·fields − 3.00` | measured `c-gcc-h − c-gcc` |
|---|---:|---:|
| `small` (179 bytes, 31 fields) | **238.00** | **238.00** |
| `large` (52 bytes, 21 fields) | **91.00** | **91.00** |
| `degenerate` (92 bytes, 25 fields) | **139.00** | **139.000** |

`degenerate` is a third out-of-sample confirmation added at TASK_049_REVIEW: it
is in no callgrind plan and was never used to fit anything. All three are inside
the domain — no line of any of them reaches 16 fields.

### 3a′. The law attributed MNEMONIC BY MNEMONIC — and −1.00 per line is padding

`.memory/03-measurement.md` trap 3, dynamic half: *before naming a per-iteration
law after a mechanism, disassemble and attribute it.* `controls/attr.py` reads
callgrind's `--dump-instr=yes` dump for the `kernel` block and joins it against
`objdump`'s mnemonics. On two sweep blobs that differ only in field count
(8 lines × 60 bytes; 8 fields vs 128 fields), `c-gcc-h − c-gcc`:

```
                sweep-t01m60 (8 fields)      sweep-t16m60 (128 fields)
  total                  +493.00/call                +733.00/call
  lea                    +487.00                     +487.00
  jb                     +480.00                     +360.00
  je                     -472.00                     -232.00
  cmp                      +8.00                     +128.00
  jae                      +8.00                     +128.00
  jne                      -8.00                     -128.00
  nopl                     -8.00                      -8.00
  mov                      -2.00                      -2.00
```

both equal to `1.00·480 + 2.00·fields − 3.00` to the instruction. The per-field
`+2.00` is `+1 cmp +1 jae −1 jne +2 je −1 jb` over the 120 extra fields; the
per-byte `+1.00` is gcc's hardened scan replacing one `je` per scanned byte with
a `lea`+`jb` pair.

⚠ **`nopl` is `−8.00` per call on both blobs and `−6.00` on `small`, i.e. exactly
`−1.00 EXECUTED ALIGNMENT NOP PER LINE`** — and the fitted `nline` coefficient is
**exactly 0.00000**, because `+1.00` of real per-line work cancels it. So a
coefficient of *zero* concealed a padding term here, where p06's trap-3 instances
concealed one inside a *non-zero* slope. Third instance in the project, first one
inside a null.

### 3a″. OUTSIDE the domain there is NO COST COMPARISON, and that is the honest statement

⚠ **This section exists to refuse a headline, and the refusal is measured.** On
the four adversarial inputs — the ones p14 exists to model — the guard fires, and
the law does not merely lose accuracy, it **inverts sign**
(`.temp/r49/sweep_ir_r49.py`, gcc, same whole-program marginal):

| blob | bytes | fields | law predicts | measured `c-gcc-h − c-gcc` |
|---|---:|---:|---:|---:|
| `adversarial-run17` | 18 | 16 | +47.00 | **+16.036** |
| `adversarial-alt33` | 64 | 16 | +93.00 | **−551.036** |
| `adversarial-full65` | 64 | 16 | +93.00 | **−823.000** |
| `adversarial-many` | 176 | 128 | +429.00 | **−610.982** |

**It is tempting to read those minus signs as *"hardening is cheaper than the
bug"*. Do not.** Three measurements say the comparison is not a cost comparison
at all:

1. **The two cells stop computing the same function.** Past `MAXTOK` fields R1h
   truncates and R1 keeps recording, so R1h's "saving" is exactly the work of the
   fields it refuses to record. That is `spec.md`'s own pinned semantics — p13's
   shape, *the hardened cell is memory-safe and LOSES DATA* — and a program that
   does less is cheaper for the same reason a program that returns early is
   cheaper. §7's checksum column is the proof that they differ: R1 is *"wrong,
   exit 0"* on every one of these rows.
2. **R1 has already stored out of bounds before the extra work begins.** The
   ASan+UBSan column **fires** on all four rows (§7), so every instruction R1
   executes after its seventeenth descriptor — the store to `tl[16]` — is
   executed by a program with a smashed frame. Its instruction count is one legal outcome of undefined behaviour, not
   a property of "the kernel without the check".
3. **And on one of the four rows the number is not even arithmetically defined.**
   `measure.py`'s marginal presumes the kernel is a function of its arguments;
   these are one-window blobs, so that is checkable exactly as in §0a. Measured
   (`.temp/p50/r1purity.py`, shipped `-O3 isolated` cells, `acc(n)` against
   `r·Σ31^j`):

```
adversarial-run17   c-gcc True    c-clang True     c-gcc-h/c-clang-h/unsafe True
adversarial-many    c-gcc True    c-clang FALSE    (acc(2) = 10394069306267118060,
                                                    pure prediction 1803517957900145280)
adversarial-alt33   c-gcc True    c-clang rc=-11 (SIGSEGV) at every n
adversarial-full65  c-gcc True    c-clang rc=-11 (SIGSEGV) at every n
```

   **`c-clang` on `adversarial-many` is not a function of its arguments**, and
   the mechanism is readable off the checksums. Recovering each call's return
   from the driver's fold, `r_k = acc(k) − 31·acc(k−1)`:

```
r_1 = 9856192725342578836    r_2 = 0    r_3 = 0    r_4 = 0    r_5 = 0
```

   **After the first call the kernel returns 0 forever** — the overflow reaches
   the driver's own frame and one of the kernel's early exits fires on every
   later call. That is why `c-clang`'s marginal on this blob is **17.982
   Ir/call** for a kernel that folds 168 fields, and why the published
   `c-clang-h − c-clang` there would read `+4287.05`: not a hardening cost, a
   dead cell. (`c-clang`'s marginal on `alt33` and `full65` is **0.000** — it
   SIGSEGVs at the same point whatever `n_iters` says.) The failure is
   deterministic — five runs of the same binary agree — and still not a per-call
   cost. The same source at `-O3 whole` **is** repeat-pure and prints the pure
   prediction (`990332571241907456`), while `-O0` prints a third answer; `c-gcc`
   prints `13881239473904541696` in all four build variants. One source, one
   input, four builds, three answers.

**The honest statements, and they are the ones to quote:**

- **the law**, with its domain: *for inputs with at most `MAXTOK` fields per
  line, gcc's safety line costs exactly `1.00·bytes + 2.00·fields − 3.00`* — and
  that domain is where every benign input lives, so **that is the cost a
  deployment pays**;
- **outside the domain, publish behaviour and not cost.** §7's table is what p14
  has to say about the inputs that trigger the bug: silent-and-wrong under gcc at
  every magnitude, SIGSEGV under clang from 17 descriptors up, an answer that
  depends on the `-O` level, and a sanitizer that fires on all four rows. **The
  check is paid for on every benign input and repaid on the attack input in a
  currency that is not instructions.**
- **The harness already agrees, structurally.** `harness/measure.py`'s `CG_PLAN`
  is six entries and every one of them is `small.bin` or `large.bin`
  (`measure.py:56-61`), so **no adversarial input is ever in a callgrind plan on
  any pattern** and no published `Ir` figure anywhere in this project is measured
  on an input that triggers a bug. The numbers in the table above exist only
  because `controls/sweep_ir.py` can be pointed at an arbitrary blob. p02's and
  p12's adversarial sections publish behaviour-only tables for the same reason,
  and p14 keeps to it — but says why, which they do not.

**It is a gcc result even inside the domain.** clang's marginal is unusable on
`alt33`/`full65` (SIGSEGV, `0.000` Ir/call, no reading at all) and its `many`
reading is the dead cell of (3). §3b's clang result is a mechanism plus a
mnemonic table, not a law, and nothing here is generalised beyond gcc.

**Where R1 IS repeat-pure** — gcc on all four rows, and every checked cell on
every row — the numbers above are reproducible readings of *those binaries*.
They are still not a cost comparison, for reasons (1) and (2), which do not
depend on (3).

### 3b. clang: `R1h − R1 = +663.00 / +237.00` — and the mechanism is a LOST 2× UNROLL

clang's law is not linear in these regressors (rms 43 over the sweep), and the
listing says why. The two scan loops, at `-O3 isolated`:

```
R1  (c-clang, UNHARDENED)          R1h (c-clang-h, HARDENED)
  add  $0x2,%rcx                     inc  %rdx
  cmp  %rcx,%rsi                     cmp  %rdx,%rcx
  je   <epilogue>                    je   <exit>
  cmpb $0x2c,0x20(%rsp,%rcx,1)       cmp  %rdx,%r12         <- `i == m`, IN the loop
  je   <append>                      je   <append>
  cmpb $0x2c,0x21(%rsp,%rcx,1)       cmpb $0x2c,0x20(%rsp,%rdx,1)
  jne  <top>                         jne  <top>
  = 7 instructions per TWO bytes     = 7 instructions per ONE byte
```

**The unhardened scan is 2× unrolled and has the `i == m` virtual-delimiter test
PEELED OUT into an epilogue; the hardened one is neither.** 3.50 Ir per scanned
byte, and none of it is the compare the safety line adds. `attr.py` on `small`
(185 scanned bytes/call) gives `cmp +308.00, je +215.00, inc +166.00, jne +81.00,
lea +12.00, nopl +1.00, and −6.00, test −6.00, jmp −7.00, mov −14.00, add −87.00`
= **+663.00**, with no vector mnemonic anywhere.

This is `.memory/01-ladder.md` finding 4's *"a bounds check blocking a 4× unroll"*
in a new form: **here the blocked optimisation is a 2× unroll plus a loop
rotation, and the line doing the blocking is not a bounds check at all — it is a
data-dependent `break`.**

### 3c. The two hardened C spellings, and the cheaper one is INPUT-DEPENDENT

`c_hcond` hoists the bound into the loop head (`while (i <= m && nt < MAXTOK)`),
which computes the identical field table and agrees with `model.py` on all eight
matrix inputs. Whole-program marginal `Ir`/call:

| cell | `small` | `large` |
|---|---:|---:|
| `c-gcc` (R1) | 3917.9640 | 2088.9820 |
| **`c-gcc-h` (R1h, shipped)** | **4155.9640** | **2179.9820** |
| `c_hcond-gcc` | 4244.9640 | 2171.9820 |
| `c-clang` (R1) | 3025.9640 | 1945.9820 |
| **`c-clang-h` (R1h, shipped)** | **3688.9640** | **2182.9820** |
| `c_hcond-clang` | 3933.9640 | 2185.9820 |

**The shipped textbook spelling is the cheaper of the two on `small` (by 89.00
under gcc and 245.00 under clang) and the dearer on `large` under gcc (by 8.00),
while clang has it cheaper by 3.00 there.** So "the cheapest in-contract hardening
spelling" is not a property of the pattern; it is a property of the input, and
both numbers are published with the input named.

⚠ **`c_hcond` is OUT of the declared contract**, and that is worth saying rather
than burying: it spells neither `if (nt == MAXTOK)` nor `while (i <= m)`, both of
which are `required` entries. It is priced here as the price of the declaration,
not offered as an alternative rung.

## 4. R2 against R4 — and the 4.25 constant on a fourth kernel

Whole-program marginals, `Ir`/call:

| pair | `small` | `large` |
|---|---:|---:|
| `safe_naive − unsafe` (R2 − R4) | **+908.00** | **+364.00** |
| `safe_tuned − unsafe` (R3 − R4) | **+638.00** | **+425.00** |
| `verus − unsafe` (R5 − R4) | **0.00** | **0.00** |

**`verus − unsafe` is 0.00 on `small`, 0.00 on `large` and 0.0000 on all 66 sweep
blobs** (`fit.py --cell verus --diff unsafe` returns every coefficient
`-0.00000` at rms 0.0000). The proof costs nothing, swept.

### 4a. Where R2's tax is, read off the listing rather than fitted

Three loops carry it, and each rate is `body_len / K` off the disassembly:

| loop | R2 | R4 | difference |
|---|---:|---:|---:|
| the SCAN, per scanned byte | 9.00 | 7.00 | **2.00** (`cmp $0x3f ; ja`) |
| the FOLD, per folded byte, `L < 4` or in R4's epilogue | 10.00 | 8.00 | **2.00** (`cmp $0x3f ; ja`) |
| the FOLD, per folded byte, R4's unrolled body | 10.00 | **5.75** | **4.25** |

R4's fold is **4× unrolled with a scalar epilogue**; R2's is not, because the
bounds check sits in the loop body. `10.00 − 5.75 = 4.25`, and
`.memory/01-ladder.md` records `4.25 = 2.00 + 2.25` — 2.00 for the check, 2.25
for the unroll it blocks — measured on p16, p17 and p11. **p14 is the fourth
kernel**, and what is readable off p14's R4 alone is the **2.25 unroll half**:
the same function executes the *unchecked un-unrolled* body (8.00) in its
`L mod 4` epilogue and the *unchecked unrolled* body (5.75) in its main loop.

⚠ **The "first time both halves are readable in one listing" claim this section
carried until TASK_050 is WITHDRAWN, and it was contradicted by the file p14
cites for the constant** (TASK_049_REVIEW M3). `patterns/p16-tlv-walk/NOTES.md`
`:563-568` already says of the same constant that *"the cheapest [sighting of
8.00] is already in the shipped binary: R4's own remainder loop runs at 8
insns/byte — R2's body minus exactly `cmp`+`je`"*, beside p16's own 5.75 unrolled
body at `:505-515`. p16 had that at TASK_007_REVIEW. **And the sentence was
imprecise about p14 as well**: the 2.00 half needs R2's 10.00, which is a
different function, so *both* halves were never readable off one listing here
either. The reproduction on a fourth kernel is real and is what this section
claims; the priority is not.

The consequence for the swept slope, confirmed on band `m` (29 blobs, field count
held at 32, `llen` swept 4…60):

```
d(R2 - R4)/d(byte) = 4.00   while every field is shorter than the unroll factor
                   = 6.25   asymptotically  ( = 2.00 scan + 4.25 fold )
```

measured **4.00 exactly** over `llen` 8 → 14 (307 → 371 → 435 → 499, three
consecutive 16-byte steps), where every field is 1–3 bytes and R4 has no unroll
to lose, and **6.25 exactly** averaged over each complete residue cycle above
`llen = 28` (`1075 → 1875 → 2675` over two 128-byte steps). The saw-tooth
between those points has **period 16 bytes**, which is
`4 fields/line × the 4-byte unroll`, i.e. the `L mod 4` epilogue — and it is the
reason the pooled linear fit of this difference has rms 108 while the *derived*
law of §9b has residual 0.0177.

### 4b. The panic pads, DECODED — because a per-byte term is not automatically a check

p06's lesson: an iterator-adaptor R3 can carry a per-byte term containing zero
bounds checks. `patterns/p12-strcat-fixed/controls/pads.py --source`:

| cell | pads | where |
|---|---:|---|
| `safe_naive` (R2) | **13** | copy 1, window header 4, line header 4, **scan `scr[i]` 1**, **`tl[nt]` 1**, **fold `tl[j]` 1**, **fold `scr[cur+q]` 1** |
| `safe_tuned` (R3) | **11** | copy 1, the two-step reslice 2, line header 4, **scan `scr[i]` 1**, **`tl[nt]` 1**, **`tl[..nt]` 1**, **`scr[cur..cur+tj]` 1** |
| `unsafe` (R4) | **1** | `a.copy_from_slice(&src[from..from + n])` |
| `verus` (R5) | **1** | the same line |
| `t_pos` (out of contract) | **8** | copy 1, reslice 2, line header 4, `tl[..nt]` 1 |

Two readings that only the decode gives:

- **R4 is not pad-free, and its one pad is a contract cost, not a bug.**
  `spec.md` pins the bulk load identical in all seven rungs, so R4 keeps
  `copy_from_slice`'s length-equality panic. p06 paid the same price for the same
  reason.
- **R3's window pads collapse from 4 to 2** because the two-step reslice checks
  the window once instead of at every header byte — and its *line*-header pads
  stay at 4, because `p` is a runtime value. That is the whole of R3's advantage
  over R2 on `small`, and it is why R3 − R2 is **−270.00** there.
- **`t_pos` has NO `tl[nt]` pad**, because hoisting the bound into the loop head
  (`while i <= m && nt < MAXTOK`) hands LLVM the invariant and the store's check
  is elided. The shipped `break` spelling does not. p03's and p04's seeding
  result, arriving from a third direction.

### 4c. R3 is DEARER than R2 on `large`, and dearer than R4 on both

`safe_tuned` 2606.9925 against `safe_naive` 2545.9925 on `large`: **R3 costs
61.00 more than R2**. Third pattern with the inversion after p09 and p06, and
like p06's it is spelling-specific and input-specific — on `small` R3 is 270.00
*cheaper* than R2. The mechanism is in 4b: R3's saving is the window reslice, a
per-**call** constant, and `large`'s windows are 104 bytes, so the constant has
almost nothing to amortise over while the iterator fold's per-field entry cost
does not shrink.

## 5. The proof

**19 verified, 0 errors on the SECOND attempt; twin 23 verified, 0 errors.** The
first attempt was `19 verified, 2 errors` and the repair is worth recording
because it is a reusable technique rather than a p14 accident.

The scan's invariant has to say *"the partition is what the table already holds,
followed by what `toks` still has to produce"*, and it also has to carry the
bound the fold later needs, `stg[k] + tkg[k] <= m` for every recorded field. The
first draft derived both from the exec array at every step —
`tl_seq(tl@, nt) = Seq::new(nt, |k| tl@[k])` and a recursive `tstart` over it —
and Verus rejected two invariants and an assertion:

```
error: invariant not satisfied at end of loop body       (s == tstart(tl_seq(tl@, nt), nt))
error: invariant not satisfied at end of loop body       (forall|k| tstart(...) + tl@[k] <= m)
error: assertion failed                                  (toks(...).take(ntok(...)) =~= tk)
verification results:: 19 verified, 2 errors
```

**The cause is that `tstart(tl_seq(tl@, nt), k)` and
`tstart(tl_seq(tl@.update(nt, x), nt+1), k)` are `tstart` applied to two
DIFFERENT sequences**, so preserving the `forall` needs a prefix lemma at every
step. The repair is to stop deriving the sequences and start *carrying* them: two
ghost locals, `tkg` (the field lengths recorded so far) and `stg` (where each
starts, one entry longer), updated by `Seq::push` and nothing else. `push` leaves
every earlier index alone by an axiom vstd already has, so all three `forall`s
survive with no lemma at all. **Both drafts are in the tree**
(`controls/gen_controls.py` derives nothing from the first, but the error text and
the diff are here), and the rule generalises: **carry a ghost sequence, do not
re-derive one.**

What is left is **one** lemma, `lemma_scan_exit`, and it is where the safety line
meets the specification: the scan stops either with the cursor past the end (the
table IS the partition) or with the table full (the table is the partition's
`MAXTOK`-prefix — which is the truncation R1h performs and R1 does not).

Obligation decomposition, each term measured with
`./verus_run.py verus.rs --verify-function <name> --verify-root`:

```
SCR 1 + MAXTOK 1 + DELIM 1 + toks 1 + fold_bytes 1 + fold_toks 1 + walk 1
      + lemma_scan_exit 1 + scr_load 1 + kernel 5 + main 5 = 19
```

`kernel`'s 5 is 1 body + 1 per loop body (four loops: the line walk, the scan,
the fold over fields, the fold over one field's bytes). **Three `const`s carry
one query each and p14 is the first pattern here with more than one** —
`.memory/04-verus.md` records the rule from p08's `SCR` and p03's `STACK_CAP`,
and p14 declares `SCR`, `MAXTOK` and `DELIM`. `main`'s 5 is the same off-by-one
against the rule of thumb that p03, p05, p06, p07, p11, p12 and p17 all record
for the identical driver.

**No `by (nonlinear_arith)` anywhere in the kernel.** Every multiplication in the
header decode is by a literal, and the partition is specified with a cursor
rather than with division — p07's zero-nonlinear-arithmetic property, reached by
choosing the spelling.

## 6. The TCB, and the same bound discharged three ways

`results/gate/p14-field-split.json`'s own `tcb_items`: **6 items, 11 body
lines.** The classification `.memory/04-verus.md` asks for:

| item | lines | class | why |
|---|---:|---|---|
| `buf_get_unchecked` | 1 | **U-license** | the author asserts `i < v.len()` licenses `get_unchecked` |
| `scr_get_unchecked` | 1 | **U-license** | the same, on `&[u8; 64]` |
| `tl_get_unchecked` | 1 | **U-license** | the same, on `&[usize; 16]` |
| `tl_set_unchecked` | 3 | **U-license** | **the item p14 exists for**: the unchecked STORE into the field table |
| `load_input` | 4 | **infra** | argv, file I/O, payload decode; no `ensures` |
| `emit` | 1 | **infra** | `println!` |

**4 U-license, 0 V-gap, 2 infra.** No item exists because Verus cannot express
something; every one wraps an operation whose safety the author is asserting, and
each is `get_unchecked`-shaped, which the TASK_048 census found `is not supported`
at the pinned vstd and therefore not removable.

**`scr_load` is NOT trusted, and p14 is the first pattern built that way from the
start.** p06 reached it at TASK_048 by removing an item; here the bulk load is
proved from three vstd facts — `<[T]>::copy_from_slice`
(`vstd/std_specs/slice.rs:205`), `<[T]>::split_at_mut` (`:185`) and
`vstd::array::ref_mut_array_unsizing_coercion` (`vstd/array.rs:175`, which Verus
inserts itself and which never appears in source). The axiom **relocates into
vstd**; it does not vanish, and `.memory/04-verus.md`'s census is why the column
is still meaningful.

**The field-count bound, discharged three ways with three different trusted
bases** — this is p14's structural result and the analogue of p06's four-way
disjointness table:

| rung | what makes `tl[nt]` in bounds | trusted base |
|---|---|---|
| R2 `safe_naive` | rustc's bounds check on `tl[nt]`, which panics | **none** (TCB 0) |
| R3 `safe_tuned` | the same check, on the same expression | **none** (TCB 0) |
| R4 `unsafe` | the programmer's SAFETY (5) comment | the whole function |
| R5 `verus` | `tl_set_unchecked`'s discharged `i < old(v)@.len()` | **one clause** |
| R1 / R1h C | *nothing* / the source line `if (nt == MAXTOK) break;` | the programmer |

p14 has **three** bases where p06 had four, and the missing one is the
interesting absence: **there is no standard-library routine that answers this
question.** p06's R3 could hand disjointness to `split_at_mut` and buy an answer
with `core`'s own `unsafe`; a fixed-capacity append has no such door in `core`,
so R3 pays the same check R2 pays. `.memory/01-ladder.md`'s
*"the safe class reaches `core::slice::memchr` at zero TCB"* has no analogue here.

### 6a. The load's receiver is scoped 2-and-2, and the `flen` local is the -O0 price

p06's TASK_048 scoping is inherited verbatim: `safe_naive.rs` and `safe_tuned.rs`
write `dst[..n].copy_from_slice(...)`; `unsafe.rs` and `verus.rs` write the three
exec lines `let s: &mut [u8] = dst; let (a, _b) = s.split_at_mut(n);
a.copy_from_slice(...)`, because `..n` is a `RangeTo<usize>` and `RangeTo` has no
`SliceIndexSpecImpl` at the pinned vstd. **At `-O3` the price is zero** — R4 and
R5 are `md5_raw 3cfea50590f84bad0e12ea8aa1970032`, 185/178 instructions, and the
`identity` pin reads `exact`.

⚠ **What is NEW on p14 is a second, smaller instance of the same mechanism, and
it was found by the gate rather than predicted.** The first draft wrote
`tl[nt] = i - s;` in the safe rungs, `*tl.get_unchecked_mut(nt) = i - s;` in R4
and `tl_set_unchecked(&mut tl, nt, i - s)` in R5. **R5's store is a CALL and R4's
is an assignment, so the argument `i - s` is evaluated in a different order**, and
`-O0 identity` came out `differ`:

```
O0  unsafe   n_fn 289   md5_raw_norel 9641ed816dbccb53bf521b7521c81953
O0  verus    n_fn 286   md5_raw_norel aca735c40ab629610dedd9b86e2f76ad
```

with the diff showing three `mov`s reordered around the call. Binding the value
to a local first — `flen = i - s;` — in **all seven rungs** fixes it:

```
O0  unsafe   n_fn 286   md5_raw_norel d962daf7ed40a505f8d543cf159a690a
O0  verus    n_fn 286   md5_raw_norel d962daf7ed40a505f8d543cf159a690a   -> norel
O3  unsafe / verus      md5_raw       3cfea50590f84bad0e12ea8aa1970032   -> exact
```

**The `-O3` price is zero with and without it.** It is p06's wrinkle one pattern
later, in a smaller form, and it is in `spec.md`'s `required` list so that nobody
"simplifies" it away.

#### 6a′. The entry's price, measured on ALL EIGHT CELLS

⚠ **This is the one `required` entry that was added in response to a gate
measurement** (`spec.md`'s `why` says so, and TASK_049's report disclosed it).
TASK_049 priced it on R4/R5 only, which is exactly the shape p13's blocker had —
a price published for some rungs and not others. **Priced on every cell**
(TASK_050, `controls/flen_price.py` — the excluded spelling `tl[nt] = i - s;`
derived from the **committed** rung sources by exact-string substitution with an
asserted hit count, built at the shipped flags, measured with `harness/asm.py`'s
own kernel report):

| cell | `-O0` without | `-O0` with (shipped) | `-O0` price | `-O3` |
|---|---:|---:|---:|---|
| `c-gcc` | 225 | 226 | **+1** | identical (`md5_fn_norel 1ec5fb96b686`) |
| `c-gcc-h` | 229 | 230 | **+1** | identical (`75520cc35378`) |
| `c-clang` | 177 | 179 | **+2** | identical (`225c9010d85e`) |
| `c-clang-h` | 180 | 182 | **+2** | identical (`ff0e2147f37c`) |
| `safe_naive` | 352 | 349 | **−3** | identical (`2a992db908f4`) |
| `safe_tuned` | 350 | 347 | **−3** | identical (`25d6577d1e72`) |
| `unsafe` | 289 | 286 | **−3** | identical (`9bdc8469333f`) |
| `verus` | 286 | 286 | **0** | identical (`9bdc8469333f`) |

Three things this says that the R4/R5-only version did not:

- **At `-O3` the price is exactly zero on all eight cells** — `md5_fn_norel` and
  `md5_raw_norel` are identical with and without the entry in every cell — so it
  moves **no published p14 figure**, every one of which is an `-O3` marginal.
  That is the direction test (`.memory/01-ladder.md`), and it comes out at
  `0.0000`.
- **At `-O0` the price is not zero and it is not sign-neutral**: the entry makes
  the three Rust cells that move **cheaper** by 3 and the four C cells **dearer**
  by 1 or 2. If any `-O0` row were ever published as a comparison, this entry
  would flatter the Rust side of it. **No p14 claim rests on an `-O0` row** (§11)
  and none may, but the disclosure belongs beside the entry rather than in a
  reviewer's file.
- **`verus` is the cell the entry does not move at all**, which is the point:
  R4 goes 289 → 286 to *meet* R5, and that is what turns the `identity` pin from
  `differ` to `norel`.

`verus_noflen.rs` verifies **19 verified, 0 errors** (TASK_049_REVIEW CN10), so
the entry is a **fiat the prover does not force** — legitimate, whole-pattern
rather than scoped, and now priced on every rung it binds. The script's own last
line is the direction test: `identical on all 8 cells: True`.

## 7. The bug, per rung, with distinct harms in distinct columns

`c-gcc`/`c-clang` are R1. The delete-the-check controls put the same deletion in
each Rust rung (`controls/gen_controls.py`, one exact-string substitution each).
`-O3 isolated`, the gate's own flags for the sanitizer column:

| input | fields | R1 c-gcc | R1 c-clang | R1h both | R2/R3/R4/R5 | `n_nocap` (R2 −chk) | `t_nocap` (R3 −chk) | `u_nocap` (R4 −chk) | ASan+UBSan on R1 |
|---|---:|---|---|---|---|---|---|---|---|
| `small`, `large`, `degenerate` | ≤16 | = model | = model | = model | = model | = model | = model | = model | **clean** |
| `adversarial-run17` | 17 | wrong, exit 0 | wrong, exit 0 | = model | = model | **panic 101** | **panic 101** | wrong, exit 0 | **fires** |
| `adversarial-many` | 8×21 | wrong, exit 0 | wrong, exit 0 | = model | = model | **panic 101** | **panic 101** | wrong, exit 0 | **fires** |
| `adversarial-alt33` | 33 | wrong, exit 0 | **SIGSEGV 139** | = model | = model | **panic 101** | **panic 101** | **SIGSEGV 139** | **fires** |
| `adversarial-full65` | 65 | wrong, exit 0 | **SIGSEGV 139** | = model | = model | **panic 101** | **panic 101** | **SIGSEGV 139** | **fires** |

Six readings, and they are the pattern's security result:

1. **The boundary is exactly `MAXTOK` delimiters, not `MAXTOK` fields.**
   `degenerate.bin`'s fifth line has **15** delimiters — 16 fields, filling the
   table exactly — and every cell including R1 agrees on it. At 16 delimiters R1
   stores `tl[16]`. The probe measured the same step: clean at `run-d15`, ASan
   `stack-buffer-overflow WRITE of size 8` at `run-d16`.
2. **The overflow's magnitude is set by delimiter DENSITY, not by data volume.**
   `adversarial-full65` is a **72-byte window** that stores **49 `size_t`s = 392
   bytes** past a 128-byte table. Nothing in this project has previously
   overflowed by 5.4× the size of its own input.
3. **p12's ladder, in a new unit.** The rungs are descriptors past the table —
   1 / 5 / 17 / 49, i.e. 8 / 40 / 136 / 392 bytes — and the behaviour splits by
   **compiler**: gcc is silent-and-wrong at every magnitude the wire format can
   express, clang SIGSEGVs from 17 descriptors up. Second pattern after p12 where
   `c-gcc` and `c-clang` differ in *behaviour* and not only in speed.
4. **R1's answer is not even stable across the build matrix.** The gate records
   *"opt/mode variants of this rung disagree (3 distinct behaviours)"* for
   `c-clang` on three of the four rows: on `adversarial-many` the four c-clang
   builds print `4345683949288458752`, `5713554817787594988` and
   `9907162596131979264` and all exit 0. **A wrong answer that depends on `-O`
   level is worse than a crash and it is what this table exists to show.**
5. **Safe Rust converts the write into a panic, in both spellings.**
   `index out of bounds: the len is 16 but the index is 16`, exit 101, on all
   four rows and both safe rungs. Unlike p06, **no safe rung reproduces C's
   answer**: there is no in-bounds regime here, because the guard's threshold IS
   the table's extent. That is `.memory/02-bench-rules.md`'s WRITE rule, and p14
   **inherits** it where p06 did not — the threshold test decides it, and the
   consequence is that p14 **cannot have an adversarial row where the guard fires
   and the sanitizer is silent.** It does not have one.
6. **Unsafe Rust with the line deleted reproduces C, and Miri catches it.**
   `u_nocap` prints `11636796253609762304` on `run17` — bit-identical to what
   both `-O3` `c-clang` builds print, and different from what both `-O0` ones do
   (`8766835387916480640`) — and SIGSEGVs on the two large rows. Under Miri:

```
thread 'main' panicked at .temp/p14/ctl/u_nocap.rs:109:30:
unsafe precondition(s) violated: slice::get_unchecked_mut requires that the index is within the slice
error: abnormal termination: the program aborted execution
```

   while `u_nocap` on `small` prints the model's checksum and Miri is clean. The
   shipped `unsafe.rs` is Miri-clean on **all eight** inputs, `large.bin`
   included — p14 has **no blocked Miri row**, which p01 does.

## 8. The spelling spread, the priced fiats, and the in-contract R3-side span

**Not the headline.** `.memory/05-layout.md` item 13: the spread is a result
about method; the number stays the matched pair.

### 8a. Three in-contract R3 spellings, and the cheapest is INPUT-DEPENDENT

`spec.md`'s declaration leaves exactly two things free on R3: the window reslice
and the fold's loop form. Both are built:

| R3 spelling | `small` | `large` | in contract? |
|---|---:|---:|---|
| **`safe_tuned` (shipped)** — two-step reslice, iterator fold | **4291.9897** | **2606.9925** | yes |
| `t_1step` — one-step `&buf[off..off+len]`, iterator fold | 4292.9897 | 2607.9925 | yes |
| `t_idxfold` — two-step reslice, **indexed** fold | 4488.9897 | **2406.9925** | yes |
| `t_pos` — `iter().position()` scan, bound hoisted to the loop head | 3953.9898 | 2521.9925 | **no** |
| `t_split` — `scr[..m].split(...)` | 4288.9897 | 2523.9925 | **no** (`forbidden[0]`) |

**The R3-side span, in contract**: `4291.99 … 4488.99` on `small` (width 197.00)
and `2406.99 … 2607.99` on `large` (width 201.00).

**The fixed-R4 bound, quoting the CHEAPEST in-contract R3** — which
`.memory/01-ladder.md` finding 3 demands and which four patterns have now got
wrong:

| | `small` | `large` |
|---|---:|---:|
| shipped R3 − R4 | +638.00 | +425.00 |
| **cheapest in-contract R3 − R4** | **+638.00** (shipped) | **+225.00** (`t_idxfold`) |

**On `large` the shipped cell overstates the safe-side figure by 88.9%.** p14 is
the fifth pattern to owe this number and the first to publish it in the first
delivery rather than in a later audit. And the cheapest spelling is **not the
same one on both inputs**, which is a stronger statement than p06's: the
iterator fold wins where the window is large and loses where it is small, because
its saving is the reslice — a per-call constant — and `large`'s windows are 104
bytes.

`t_pos` is the price of the DECLARATION rather than of the pattern: on `small` it
is **338.00 Ir/call cheaper** than the shipped R3, and it is out of contract
because it spells none of `if nt == MAXTOK {`, `while i <= m {` or `if i == m ||`.
Its `pads.py` decode (§4b) says where the saving is: the hoisted bound elides
`tl[nt]`'s bounds check.

#### 8a′. The two out-of-contract fiats, DIRECTION-TESTED — a judgement upgraded to a measurement

TASK_049 published `c_hcond` and `t_pos` as *"a judgement I made, not a
measurement"*. **It is now a measurement** (TASK_049_REVIEW CN11), and both
exclusions go **against** p14's own interest — which is the direction
`.memory/01-ladder.md`'s direction test asks about:

| fiat | if it were ADMITTED | the published figure | direction |
|---|---|---|---|
| `c_hcond` | R1h `small` 4244.96 (gcc, **dearer**) / `large` 2171.98 (cheaper) | hardening tax +238.00 / +91.00 | excluding it **raises** the gcc `large` tax by 8.00 and lowers nothing |
| `t_pos` | R3 `small` 3953.99 / `large` 2521.99 | R3 − R4 +638.00 / +425.00 | excluding it **raises** the published safe-side tax from +300.00 → +638.00 and +340.00 → +425.00 |

For a safety-tax number the flattering direction is *down*; both exclusions push
*up*. So neither is a thumb on the scale, and both are priced beside the number
they protect (§3c, §8a). ⚠ **That does not make them right** — it makes them
legitimate fiats whose cost is known, which is all the direction test can
establish.

### 8b. The forbidden spellings, PRICED — and put through the prover, not asserted

`spec.md`'s `forbidden` list has eight entries. TASK_049: an entry the **prover**
already excludes costs nothing to keep; an entry only the **declaration**
excludes is a fiat and must be priced.

| entry | who excludes it | price |
|---|---|---|
| `` `.split(` ``, `` `.split_terminator(` ``, `` `.splitn(` `` | **the PROVER** — measured | free to keep |
| `` `from_le_bytes` ``, `` `chunks_exact` `` | the prover (p05/p16/p06, measured) | free to keep |
| `` `strtok(` `` | the declaration (C has no prover) | **+2817.00 / +2680.00** |
| `` `memchr(` `` | the declaration | **−639.00 / +170.00** |
| `` `strsep(` `` | **the declaration** | **not priced — it would measure a different workload, §0a** |

⚠ **The `strsep` row said *"the harness itself — not buildable"* until TASK_050
and that was wrong** (TASK_049_REVIEW B2). It is buildable and it is measurable;
what it is not is *comparable*, because the repeat protocol drives it into a
one-call steady state that tokenises an already-tokenised buffer. So it is a
**fiat of the declaration**, like `strtok` and `memchr` — and unlike those two it
is **not priced**, because there is no honest number to publish: any marginal it
produced would be the cost of the steady state and not of tokenising. That is
the price, stated rather than left blank.

**The prover verdict is a measurement.** `controls/gen_controls.py` derives an R5
probe that calls `scr[..m].split(|b: &u8| *b == DELIM).count()` inside `kernel`,
and `./verus_run.py` says:

```
error: `core::slice::impl&%0::split` is not supported (note: you may be able to add a Verus
       specification to this function with `assume_specification`) ...
error: `core::slice::iter::Split` is not supported ...
error: `core::slice::iter::impl&%17%default%count` is not supported ...
```

`is not supported` disqualifies (`.memory/01-ladder.md`), so an R4 using `.split`
could not have a verifying R5 twin and **would not be a rung**. p11's
R4-by-permission result on a third pattern — with the sign reversed from p11's,
because here the safe class's extra reach is worth only **−3.00 / −83.00
Ir/call**, not −35% of the kernel.

**`memchr` is the entry that would move a number, and it moves it in BOTH
directions.** `c_memchr` computes the same partition through a libc IFUNC:
**−639.00 Ir/call on `small`** (gcc; −289.00 clang) and **+170.00 on `large`**
(gcc; +210.00 clang). `small`'s fields average 5.0 bytes and `large`'s 2.0, so
the IFUNC's per-call overhead wins below ~3 bytes per field and loses above it.
p11's and p13's *"the library, not the language"* result, arriving with a **sign
change inside one pattern**.

**`strtok` is dear and it is also WRONG here**, which is why it is not a rung:
`+2817.00 / +2680.00` Ir/call, and it disagrees with `model.py` on
`adversarial-full65`, `-many`, `-run17` **and `degenerate`** — the last because
`strtok` drops leading and trailing empty fields, which `degenerate.bin` has by
construction. §0d has the run-length experiment.

### 8c. The C hardening span

`4155.96 … 4244.96` (gcc) and `3688.96 … 3933.96` (clang) on `small`; on `large`
`2171.98 … 2179.98` (gcc) and `2182.98 … 2185.98` (clang). Both endpoints are
`if (nt == MAXTOK) break;` against `while (i <= m && nt < MAXTOK)`; §3c has the
per-input reading and the note that the second is out of contract.

## 9. The sweep, the amortisation axis, and the zero-parameter fold law

**66 blobs in four bands, all `sweep-*`** (so `check.inputs_of` and
`measure.SKIP_INPUT_PREFIX` drop every one of them and no matrix number depends
on any of them — `.memory/05-layout.md`). `inputs/gen.py` is inside
`source_sha256`, and it is **deterministic**: two `--sweep` runs are byte-identical
and the **eight matrix blobs are unchanged** by adding the bands (verified by
md5, 8/8 unmoved).

| band | held fixed | swept | what it isolates |
|---|---|---|---|
| `m` (29) | 8 lines, 4 fields/line | `llen` 4…60 | the per-BYTE terms |
| `t` (16) | 8 lines, `llen` 60 | fields 1…16 | **the per-FIELD term at FIXED TOTAL BYTES** |
| `l` (16) | `llen` 32, 4 fields/line | lines 1…16 | the per-LINE constant |
| `x` (5) | — | heterogeneous within one window | full rank + a within-band negative control |

### 9a. THE AXIS THAT IS NEW: the amortisation denominator, swept on its own

Every earlier pattern here answers *"does the safety check amortise?"* by making
the input bigger. **p14 can ask a question no earlier pattern could**, because a
tokenizer's two loops multiply to a constant: band `t` holds 480 folded bytes and
8 lines FIXED and moves only the number of fields, so it sweeps *the thing a
per-field cost is divided by* and nothing else.

**R2 is exactly linear on that band: `+18.00 Ir per field`, 16 of 16 blobs, zero
residual** (10042.99, 10186.99, … 12203.00 — every step exactly +144.00 for eight
extra fields). R4 is not, because its fold is 4× unrolled and carries an
`L mod 4` epilogue; §9b's zero-parameter law predicts it instead.

**And the safety tax falls as the partition gets finer, at constant total work:**

| band-`t` blob | fields | mean field length | `R2 − R4` per call | per LINE byte (480, fixed) |
|---|---:|---:|---:|---:|
| `sweep-t01m60` | 8 | 60.0 | **3099.00** | **6.456** |
| `sweep-t02m60` | 16 | 29.5 | 2947.00 | 6.140 |
| `sweep-t04m60` | 32 | 14.3 | 2675.00 | 5.573 |
| `sweep-t06m60` | 48 | 9.2 | 2547.00 | 5.306 |
| `sweep-t08m60` | 64 | 6.6 | 2131.00 | 4.440 |
| `sweep-t12m60` | 96 | 4.1 | 2339.00 | 4.873 |
| `sweep-t14m60` | 112 | 3.4 | 1971.00 | 4.106 |
| `sweep-t16m60` | 128 | 2.8 | **1683.00** | **3.506** |

**A 1.84× range in the published per-byte safety tax with the input size, the
line count and the byte count all held exactly constant.** Nothing in this
project has previously moved a safety figure by changing only the *shape* of the
data.

⚠ **The denominator is the LINE byte (480, the quantity held fixed), not the
folded byte** — they differ because each extra delimiter removes one folded byte,
and quoting a rate against a moving denominator would hide the effect being
measured. ⚠ **And the fall is not monotone**: `t12` reads 4.873 against `t08`'s
4.440, because `t12`'s fields are 4 and 5 bytes long and `t08`'s are 6 and 7, so
`t08` pays a 2- or 3-byte epilogue where `t12` pays none — the `L mod 4` term of
§9b. Quote the endpoints and the mechanism, not a trend line.

⚠ **And the direction is the counter-intuitive one, so the mechanism matters.**
The check does not get cheaper; **the unsafe rung gets dearer.** R4's advantage is
the 4× unroll (§4a), which needs fields of length ≥ 4; sixteen 3-byte fields deny
it, so R4 falls back to the same 8.00 Ir/byte scalar body R2 runs with a check on
top, and the two converge. R2 costs `+18.00` per extra field and R4 costs
`+29.80` averaged over the band.

**What this says about `.memory/01-ladder.md` finding 8's question.** p14's tax is
`O(bytes)`, so *per byte* it is constant in the input size — it does **not**
amortise along bytes, unlike p16's and p17's per-call constants and like p05's
`O(nrow)` term along rows. What is new is that **the constant is a function of the
DATA's granularity and not only of the kernel's shape**, and p14 is the first
pattern that can separate the two, because it is the first with two nested loops
whose trip counts multiply to a fixed total.

### 9b. The fold law, DERIVED from the listing with ZERO fitted parameters

`controls/law.py` reads R4's fold off `objdump` and predicts band `t` forward:

```
fold4(0)    = 2
fold4(1..3) = 10 + 8*L
fold4(L>=4) = 13 + 23*(L div 4) + [r>0]*(2 + 8*r)        r = L mod 4
per field, outside the inner loop: 19.00
```

Predicted against measured `Ir(t_k) − Ir(t_1)` on the 15 other band-`t` blobs:

```
sweep-t02m60   +296.00 derived   +296.0000 measured   residual  0.0000
sweep-t08m60  +1976.00           +1976.0000                     0.0000
sweep-t12m60  +2344.00           +2344.0150                     0.0150
sweep-t16m60  +3576.00           +3576.0048                     0.0048
WORST |residual| over 15 blob(s): 0.0177   (ZERO fitted parameters)
```

and identically for `verus`. The residuals are the driver's `println!`
digit-count term, which `.memory/03-measurement.md` bounds at ±0.09.

⚠ **One instruction of that law is a NOP, and it is load-bearing in the
arithmetic.** The unrolled preamble is `mov ; and ; lea ; xor ; xchg %ax,%ax`,
and the `xchg` is on the fallthrough path into the loop. Drop it from the
derivation and the law is wrong by exactly 1.00 per field with `L >= 4` — so
**the law's exactness is itself the evidence that the padding executes**, rather
than a reading of the listing. `.memory/03-measurement.md` trap 3, third instance
in this project and the first where the NOP is *inside a zero-parameter
derivation* rather than inside a fitted coefficient.

### 9c. Leave-one-length-out — and on the gcc law it CANNOT FAIL, provably

⚠ **Read this before quoting p14's hold-out figure. On the exact gcc law the
hold-out is a corollary of the exactness and not independent evidence**
(TASK_049_REVIEW M2, and this is p13's mistake in a new costume).

The fit set is length-heterogeneous by construction — band `m` sweeps `llen`
4…60 and band `x` carries several `llen` inside one window — so the honest
hold-out removes **every blob containing a given `llen`**, i.e. a whole column of
the design. On the exact gcc law that is 29 hold-outs including two that remove
17 blobs each, and the worst out-of-sample error is **0.0000**.

**But it could not have been anything else.** Two facts, both re-measured:

```
law max|residual| over the 66 sweep blobs = 0.000000        (an EXACT fit)
full design rank 4;  drop all sweep-l* -> n=50 rank 4;  sweep-t* -> n=50 rank 4
                     drop all sweep-m* -> n=37 rank 4;  sweep-x* -> n=61 rank 4
and every one of the 29 llen hold-outs leaves rank 4
```

An exact fit plus a design that keeps full rank after the drop means every
hold-out's least-squares solution **is the same exact solution**, which then
predicts the held-out rows exactly. The arithmetic cannot come out any other way,
so the test distinguishes nothing.

⚠ **§9c's old paragraph does not rescue it, and is corrected here.** It said
*"this test CAN fail"* and demonstrated failure on a **different fit** —
`safe_tuned`'s own four-regressor model, rms 168.68 in sample. That shows the
*procedure* can fail on a bad model; it does not show that *this* hold-out could
have failed. Compare p06, whose leave-one-length-out **did** fail (−48.000 at
`m = 3`) precisely because its law was not exact.

**What p14's gcc law actually rests on**, and all of it could have failed:

1. the **exact** in-sample fit — `max |residual| 0.0000` over 66 blobs is not
   guaranteed by anything and would have been destroyed by one wrong regressor;
2. the **out-of-sample perf rows** `small` `+238.00` and `large` `+91.00`, plus
   `degenerate` `+139.000` (§3a), none of which is in the sweep and any of which
   could have missed;
3. the **mnemonic-by-mnemonic attribution** of §3a′, which puts each coefficient
   on named instructions;
4. and, negatively, §3a″: the law is **false outside its domain**, which is the
   sharpest evidence that it is a statement about a specific regime rather than a
   curve fitted to anything.

The `safe_tuned` demonstration stays, relabelled as what it is — a demonstration
that the *procedure* has teeth on a wrong model:

⚠ Run the same hold-out against the four-regressor fit of `safe_tuned` alone and it does fail, badly —
rms 168.68 in sample — because R3's fold is unrolled and a linear model in
`(nline, bytes, fields)` is the wrong model. ~~The hold-out passing on the gcc law
is therefore evidence about the law, not about the procedure.~~ **That last
sentence is withdrawn**: the hold-out passing on the gcc law is evidence about
neither — it is arithmetic.

## 10. The proof mutants

`.memory/05-layout.md` item 11: a deliberately-broken proof cannot live in the
pattern dir, so each is a `.temp/` artefact derived from the shipped `verus.rs`
by exact-string substitution with an asserted hit count
(`controls/gen_controls.py::verus_mutants`), run with
`./verus_run.py .temp/p14/ctl/<m>.rs [--cfg slb_twin]`.

| mutant | what it changes | shipped cfg | `--cfg slb_twin` | contract pin |
|---|---|---|---|---|
| `pm1_nocap` | THE SAFETY LINE deleted from R5, nothing else | **18 verified, 1 error** | **22 / 1** | **0 diffs — does not catch it** |
| `pm2_weakreq` | `tl_set_unchecked`'s `requires` `<` → `<=` | **19 / 0 — PASSES** | **22 / 1** | **2 diffs — catches it** |
| `pm3_msonly` | safety line deleted **and** `ensures` weakened to `true` | **18 / 1** | **22 / 1** | 0 diffs |

```
pm1_nocap:  error: invariant not satisfied at end of loop body
            error: precondition not satisfied            <- tl_set_unchecked's requires
pm2_weakreq (twin): error: precondition not met: index in bounds for this access
pm3_msonly: error: invariant not satisfied at end of loop body    <- `nt <= MAXTOK`
            error: precondition not satisfied                     <- tl_set_unchecked's requires
```

⚠ **`pm3_msonly` emits TWO errors and this block used to quote one**
(TASK_049_REVIEW m1). Re-run at TASK_050 on the shipped mutant:

```
$ ./verus_run.py .temp/p14/ctl/pm3_msonly.rs
error: invariant not satisfied at end of loop body
   --> .temp/p14/ctl/pm3_msonly.rs:587:17   |  587 |  nt <= MAXTOK,
error: precondition not satisfied
   --> .temp/p14/ctl/pm3_msonly.rs:627:17   |  627 |  tl_set_unchecked(&mut tl, nt, flen);
   (failed precondition, verus.rs:408: `i < old(v)@.len()`)
verification results:: 18 verified, 1 errors
error: aborting due to 2 previous errors
```

so it fails at **the same two obligations as `pm1_nocap`**, whose row already
lists both. Both are memory-safety obligations, so the conclusion below is
unchanged.

Three readings.

**`pm1_nocap` is R1's bug written in Rust, and the proof rejects it at exactly the
right obligation** — `tl_set_unchecked`'s `requires i < old(v)@.len()`, which is
the clause `spec.md`'s `verus.unsafe_justifications` argues for. The contract pin
does **not** catch it (0 clause diffs): the mutant changes exec code, not clause
text. So on this mutant the *proof* is the sole catcher.

**`pm3_msonly` is the p06 comparison, and p14 comes out on the opposite side.**
p06 measured that a memory-safety-only spec **accepts** its buggy kernel in
regime 1, because nothing leaves the array, and concluded that separating the two
regimes needs a *program* change rather than a *spec* change. p14's bug is a
spatial store, so there is no such regime: **weakening the postcondition to
`true` does not rescue the mutant — it still fails, at the same TWO obligations
`pm1_nocap` fails at.** `ensures true` and `ensures r == split_fold(...)` reject
the same program here.

⚠ **State what `pm3` actually tests, because the shorter summary overstates it.**
`pm3_msonly` is **not** a memory-safety-*only* specification: only the kernel's
`ensures` is weakened to `true`, and the functional loop invariants (`tkg`,
`stg`, `toks`) all remain, so the proof still knows what the partition is. The
claim it tests is precisely *"weakening the POSTCONDITION to `true` does not
rescue the mutant"*. The stronger sentence — *"memory safety alone suffices on
p14"* — is a reading of that result and not a measurement of it; a genuine
memory-safety-only spec would have to delete the functional invariants too, and
p14 did not build one. **Quote the narrow claim.** The complement to p06 survives
it: p06 has a regime where the buggy kernel stays inside its array and p14 has
none, so the discriminator is whether the bug's harm can stay inside the object —
which is a statement about the two *bugs* and does not depend on how much of
either spec was weakened.

**`pm2_weakreq` is the twin's row, and "the twin is the SOLE catcher" is FALSE
here too.** It verifies `19 / 0` in the shipped configuration — the caller can
prove the stronger fact, so weakening the precondition costs nothing there — and
fails only under `--cfg slb_twin`, where `v[i] = x` at `i == len` is out of
bounds. **But it also fails the `spec.md` contract pin**, measured with
`check.py`'s own comparator (`vparse.norm_clause` against the pinned `items`):

```
patterns/p14-field-split/verus.rs:      0 clause diff(s)
.temp/p14/ctl/pm2_weakreq.rs:           2 clause diff(s)
    tl_set_unchecked.requires:      ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
    slb_twin_tl_set_unchecked.requires: ['i <= old(v)@.len()'] != pinned ['i < old(v)@.len()']
```

so the correct claim is **Verus-level sole catcher**, which is p06's ⊘ correction
applied on a fourth pattern rather than the overclaim it corrects.

## 11. What p14 does not have, and what is open

- **No wall-clock headline, and the reason is a measured null.**
  `controls/wall_span.py`, 11 reps × 5 byte-identical copies, alternating, pinned,
  `t(200000) − t(1)`, on `small`, run twice on two different cores:

  | pair | pass 1 | pass 2 | identical-copy floor |
  |---|---:|---:|---:|
  | `c-gcc-h − c-gcc` | +7.15% | +7.39% | 0.7–1.8% |
  | `c-clang-h − c-clang` | +18.21% | +18.66% | |
  | `safe_naive − unsafe` | +13.05% | +13.28% | |
  | `safe_tuned − unsafe` | +9.93% | +10.17% | |
  | **`verus − unsafe`** | **+8.97%** | **+8.91%** | |

  **`verus` and `unsafe` have byte-identical kernels** (`md5_raw
  3cfea50590f84bad0e12ea8aa1970032`) and **exactly equal marginal `Ir` on all 66
  sweep blobs and both perf inputs**, so two cells that cannot differ read
  `+8.9%` — **larger than the gcc hardening gap and comparable to two of the
  three others.** Every p14 `ns` figure is therefore withdrawn as a claim; the
  headline is the `Ir` decomposition. ⚠ **That `+8.9%` is not "the pattern's own
  null" and 11a is why**: it is one draw from a layout distribution whose median
  is ≈ 0 and whose spread is wider still. The *conclusion* — withdraw the `ns`
  column — is unchanged and is if anything better supported.

  ⚠ **The R4/R5 pair is a SMOKE ALARM, not a floor — and the sentence that said
  otherwise is withdrawn.** Until TASK_050 this bullet read *"it varies the
  binary rather than only the inode, so it bounds layout and link effects that an
  identical-copy floor cannot see"*. **That is false, measured** (TASK_049_REVIEW
  B1, reproduced here in 11a): on p14 the pair reports **+8.95%** where the
  measured within-cell layout spread is **12.68% (`unsafe`) / 9.73% (`verus`)**,
  so it *under*-states the very quantity it claimed to bound on the cell that
  moves most, and over a layout population its median is **≈ 0**. It is a biased sample of size one, because the `verus` build's kernel
  lands `0x20` below the `unsafe` build's on p06 and p14 alike, so the pair
  measures the *same fixed alignment contrast* every time — which is why p14's
  two passes agreed to 0.06 pp. **A large value is worth having as a signal that
  says "go and measure the layout population"; it is not the population and it is
  not a floor. The floor is the population.**

### 11a. The layout population — the floor, and the `win32`/`jcc32` question ANSWERED

`controls/clayout.py`, ported at TASK_050 (p06's file of the same name populates
p06's *C* cells; p14's headline pair is Rust, so the levers are
`-align-all-functions 0…8`, 14 `--symbol-ordering-file` permutations and the
shipped build — **24 layouts per cell**, `verus` built through
`./verus_run.py --compile` with the same flags).

**CONTROL 1 holds on all 48 binaries** — every one runs the same instruction
stream and differs only in where the linker put it:

```
unsafe  24 builds  n_fn [185]  md5_fn_norel ['9bdc8469333f']  21 distinct addrs 0x15690..0x4ac60
verus   24 builds  n_fn [185]  md5_fn_norel ['9bdc8469333f']  21 distinct addrs 0x14e40..0x46560
single-valued per cell: True    verus == unsafe: True    distinct stdouts over the population: 1
```

`small`, 13 reps, cpu 5, alternating, min-of-reps:

| | ns/call | median | IQR |
|---|---|---:|---|
| `unsafe` (n=24) | 245.36 … 276.48 | 250.22 | 249.50 … 263.37 |
| `verus` (n=24) | 244.77 … 268.57 | 251.41 | 249.70 … 266.99 |

| statistic | value |
|---|---|
| `R5 − R4`, the **shipped pair** | **+8.95%** (reproduces the published +8.97%) |
| `R5 − R4` **paired by layout**, n=24 | median **−0.07%** |
| `R5 − R4` over all **576 cross pairs** | median **+0.27%**, **`P(R5 > R4) = 0.559`** |

⚠ **Quote the median and `P(A>B)`, not the range.** `.memory/03-measurement.md`
retracts worst-vs-best range and dominance as layout statistics because neither
converges in N; the ranges above are printed because the eye wants them, and the
two converging statistics are the ones that decide the question. Both say the
same thing: **`P(R5 > R4) = 0.559` is a coin flip, and the pair is a null.**

**And the verdict does not depend on the estimator.** `--estimator median` (the
median of the 13 reps per binary, instead of the min) on the same population:
shipped pair **+8.54%**, paired-by-layout median **−0.00%**, cross-pair median
**+0.77%**, **`P(R5 > R4) = 0.609`**. Same conclusion at both ends of the
estimator choice.

**A second, independent population agrees.** TASK_049_REVIEW built its own
24-layout population with a different script (`.temp/r49/laynull.py`, different
symbol-ordering seeds, p06 and p14 interleaved in one session) and read
`unsafe` 244.36…276.67 (spread 13.22%), `verus` 244.00…277.56 (13.75%), shipped
pair **+9.17%**, paired median **+0.10%**. Two populations, two scripts, same
verdict — and the two spread figures differ by ~0.5–4 points, which is exactly
the non-convergence that makes a **range** the wrong statistic to publish.

**The mode, derived from the listing and not from an address bit.** All six loops
in the kernel flip their `win32`/`jcc32` together — the whole function moves as a
unit — so p14 **cannot separate `win32` from `jcc32`**; both predicates change at
the same layouts. At the standard 32-byte fetch grid the partition is exactly
`addr % 32`: 26 binaries at `%32 == 0` (245.54…255.34, median 250.58) against 22
at `%32 == 16` (244.77…276.48, median 267.09), and mode-matched `R5 − R4` is
**+0.46% / −0.24%**.

⚠ **But the 32-byte grid is NOT the sharp predicate here, and that is a finding
about the method rather than about p14.** `.memory/03-measurement.md` says to
partition by `win32`/`jcc32` "computed from the listing, not by an address bit" —
correct — but the *grid spacing* is a parameter, and on p14 the right one is
**64**. `loopfit.kernel_report(..., boundary=64)` on loop 1 (the 46-byte loop)
gives `jcc32 == 1` for exactly the 10 binaries with `addr % 64 == 16`:

```
jcc32@64(loop1)==1   n=10   267.09..276.48   median 268.09     <- SLOW
jcc32@64(loop1)==0   n=38   244.77..267.35   median 250.15     <- FAST   (+7.2%)
loopfit.perfect() is True on the verus sub-population; the unsafe one overlaps by 0.01 ns
```

Mode-matched under **that** partition, `R5 − R4` is **+0.20%** (n=38,
`P(R5>R4) = 0.550`) and **−1.26%** (n=10, `P = 0.250`). The `%32` partition
merges the *fastest* class (`%64 == 48`, median 248.67) into the slow group with
the *slowest* (`%64 == 16`, median 268.09), which is why it separates less
sharply than an address-bit reading would.

**So the `win32`/`jcc32` question is answered, and the answer has three parts:**

1. **p14 is a strongly layout-sensitive kernel** — a 7.2% mode between two
   listing-derived classes, on top of which the within-cell spread reaches
   12.68% (`unsafe`) in this population and 13.75% (`verus`) in the review's.
2. **The shipped R4/R5 pair straddles the two extreme classes** — `unsafe` at
   `0x156b0` (`%64 == 48`, the fastest class) and `verus` at `0x15690`
   (`%64 == 16`, the slowest). The pair does not sample the distribution; it
   samples its two ends.
3. **p14 still publishes no `ns` claim**, and now for the better reason: not
   *"the null is large"* but *"the null is ≈ 0 and the layout spread of the two
   cells that were populated is 12.7–13.8%, which is at or above both Rust rung
   gaps in the withdrawn table (`safe_naive − unsafe` +13.05%, `safe_tuned −
   unsafe` +9.93%)."*
   ⚠ **Stated exactly, because the population covers two cells and not eight.**
   No layout population exists for `safe_naive`, `safe_tuned` or any C cell, so
   the two safe-Rust rows are bounded only by the `unsafe`/`verus` spreads
   measured here and **the two C rows (`c-gcc-h − c-gcc` +7.15%,
   `c-clang-h − c-clang` +18.21%) are not bounded at all** — the larger of them
   may well survive a population, and nobody has built one. That is why the
   whole `ns` column is withdrawn rather than filtered.

### 11b. The rest of what is open

- **The clang `R1h − R1` law is not solved.** §3b names the mechanism (a lost 2×
  unroll and an un-peeled `i == m` test) and gives the mnemonic attribution, but
  clang's difference is not linear in `(nline, bytes, fields)` and no
  zero-parameter form was derived for it. gcc's is exact; clang's is a mechanism
  plus a table.
- ~~**`x08b`, the within-band negative control, was never differenced.**~~
  **Checked, and it passes.** `sweep-x08a` and `sweep-x08b` have identical
  regressors by construction (verified: every column of `sweep_ir.shape` equal)
  and different bytes, so the predicted delta is exactly 0. Measured, all eight
  cells: **+0.0360** on the four C cells and **+0.0103** on the four Rust ones —
  the driver's `println!` digit-count term and nothing else, against
  per-call totals of 4208…6317. The band's regressors therefore carry the cost
  and the *data* does not, which is what a negative control is for.
- **The `-O0` rows are unexplained.** `safe_tuned` is 623.88 M `Ir` on `small` at
  `-O0` against `safe_naive`'s 507.48 M — a 23% gap that inverts at `-O3` — and no
  claim rests on it (`.memory/02-bench-rules.md` forbids one), but nobody looked.
- **`degenerate.bin` is not in the callgrind plan**, so its six edge shapes are
  checksum-checked and sanitizer-checked but never measured. That is
  `harness/measure.py`'s fixed plan, not a p14 decision.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's body is `v[i]` on the
same `&[u8]` with the same parameters and the same clause text. `v[i]` is the
*checked* form of the identical operation — `<[u8] as Index<usize>>::index`
performs the bounds test `i < v.len()` that `get_unchecked` requires the caller
to have performed — so a `requires` too weak to license the unchecked read is too
weak to license the indexed one, and Verus sees the second. Nothing else can be
substituted: there is no other safe expression whose value is `v@[i as int]`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly one operation, a read of one element,
and returns it. `r == v@[i as int]` names that element and its value. There is no
second read, no write, no aliasing and no interior mutability: `v` is `&[u8]`, so
the item cannot modify anything, and `u8` has no padding or niche that could make
"the value read" ambiguous. The completeness question TASK_009_REVIEW raises — a
body that *also* reads `i + 1` — would be invisible to this contract, and that is
why Miri is mandatory on this pattern and runs over `unsafe.rs`, which contains
the same expression inline.

**(c) Does each clause mean the same in both configurations?** There is one
`requires` and one `ensures` and both are written in terms of `v@`, `i` and `r`
only. `v@` is `<[u8]>::view`, `i` is a `usize` parameter and `r` is the return
binding; none of the three is `#[cfg]`-dependent, none mentions a constant that
`slb_twin` could redefine, and `harness/check.py` separately rejects the token
`slb_twin` anywhere except in a twin's own attribute. The two items are compiled
from the same clause text in the same module with the same imports.

## SLB-TRUSTED-ARGUMENT verus.rs scr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8; 64]`; the twin's is `v[i]` on the
same `&[u8; 64]`. The array case matters and is the reason this item is separate
from `buf_get_unchecked`: for an array the bound is the *type-level* length, so
the checked form Verus reasons about is `<[u8; 64] as Index<usize>>::index`,
whose obligation vstd derives from `array_len_matches_n`. Substituting the slice
accessor would change the type and therefore the obligation, so the twin has to
be this one.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** One read of one element of a fixed-size array of `u8`, returned.
`r == v@[i as int]` names it. `v` is a shared reference, so no write is possible;
`[u8; 64]` has no padding. The `requires` is ONE conjunct, `i < v@.len()`, and a
second conjunct `v@.len() == 64` is deliberately absent: for a `&[u8; 64]` it is
a tautology discharged from the parameter type alone, and p03's gate run rejected
exactly that draft (`.memory/04-verus.md`; p03 `NOTES.md` 5b). Absence of a
tautology is not incompleteness.

**(c) Does each clause mean the same in both configurations?** Both clauses
mention only `v@`, `i` and `r`. The array length `64` appears in the *type*, not
in a clause, and it is written as a literal in both items rather than through the
`SCR` constant — so even a `#[cfg]`-varying `SCR` could not make the two items
disagree, which is the bypass `harness/check.py`'s `slb_twin`-token rule exists to
close.

## SLB-TRUSTED-ARGUMENT verus.rs tl_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[usize; 16]` — the FIELD TABLE — and the
twin's is `v[i]` on the same type. Same argument as `scr_get_unchecked`, on a
different element type and a different length, and it is a separate item for
exactly that reason: `[usize; 16]` and `[u8; 64]` are different types with
different `Index` impls and different vstd length axioms, so one accessor cannot
stand in for the other.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** One read of one element, returned; `r == v@[i as int]` names it.
`v` is a shared reference so nothing is written. `usize` has no padding on this
target. **What this item is FOR is the fold**: it is called once per recorded
field, and its `requires` `i < v@.len()` is what forces the caller to have
proved `j < nt <= MAXTOK` — the same fact `tl_set_unchecked` forces on the
write side, read back.

**(c) Does each clause mean the same in both configurations?** Both clauses
mention only `v@`, `i` and `r`; the length `16` is in the type and is written as
a literal in both items rather than through `MAXTOK`, so a `#[cfg]`-varying
constant could not separate them.

## SLB-TRUSTED-ARGUMENT verus.rs tl_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` on a `&mut [usize; 16]`; the twin's is
`v[i] = x;` on the same type with the same clause text. `v[i] = x` is the checked
form of the identical store — `<[usize; 16] as IndexMut<usize>>::index_mut`
performs the bounds test the unchecked form requires the caller to have performed
— and weakening the shared `requires` makes Verus reject the indexed store, which
is the whole point of the twin. **This is the item p14 exists for**: it is called
once per field, and its `requires` is what excludes the store `c/kernel.c`
performs past `tl[MAXTOK]`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly one store and nothing else. The
`ensures` is a WHOLE-SEQUENCE equality, `final(v)@ == old(v)@.update(i as int,
x)`, not a statement about slot `i` alone — so it says both *"slot `i` became
`x`"* and *"nothing else moved"*. That second half is load-bearing here and not
decoration: the fold reads `tl[0 .. nt)` after the scan has written it field by
field, so a postcondition that pinned only the written slot would leave every
earlier descriptor unconstrained and the fold's specification would not compose.
A body that also wrote `i + 1` would satisfy a slot-only `ensures` and be
invisible; it does **not** satisfy this one. What this contract still cannot see
is a body that *reads* something extra, which is why Miri is mandatory and runs
over `unsafe.rs`'s inline `*tl.get_unchecked_mut(nt) = flen;`.

**(c) Does each clause mean the same in both configurations?** `requires
i < old(v)@.len()` and `ensures final(v)@ == old(v)@.update(i as int, x)` mention
only `v`, `i` and `x`. `old` and `final` are Verus's own `&mut` binders and mean
the same in both configurations by construction. The array length `16` is in the
type and is spelled as a literal in both items. `x` is unconstrained, and
`spec.md`'s `verus.unsafe_justifications` says why and the gate shouts it every
run: `x` is a pure VALUE parameter, stored and never used as an address, an index
or a length, so no precondition on it could be useful — the parameter-coverage
false positive `.memory/04-verus.md` names, on its fourth pattern.
