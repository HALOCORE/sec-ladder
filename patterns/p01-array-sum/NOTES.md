# p01 — findings, TCB tally, sticking points

Numbers here are from `results/p01-array-sum.json`; the generated table is
`results/tables/p01-array-sum.md`. Regenerate with `harness/measure.py p01`
then `harness/report.py p01`.

---

## 1. The benchmark does not evaporate — shown, not asserted

The anti-collapse mechanism is the serial dependency
`off = (acc * nwin) >> 64` in 128-bit arithmetic, where `acc` is the running
checksum. It is the same arithmetic in C and in Rust, so neither language gets a
stronger optimisation barrier than the other. No `black_box`, no `asm volatile`.

It was `acc % nwin` until TASK_005. The `div` was ~0.1 % of `Ir` — invisible to
the primary metric — but 20–40 cycles of latency on the very dependency chain
that makes this a loop, and that is a **rung-independent additive constant**,
which compresses every cross-rung wall-clock *ratio* toward 1. `mul` is 3
cycles, and `off` is still uniform over `[0, nwin)` so the cache randomisation is
unchanged. See `spec.md`, "The barrier is a multiply-shift, not a modulo".

`main`, `-O3`, `isolated`, innermost loop containing `call kernel` — every rung
has one, and it is a real loop:

```
R1 gcc (14 instructions, 0x1250 → 0x127e)      R4 unsafe (13, 0x15100 → 0x15127)
   mov    %rbx,%rax        ; acc                  mov    %r14,%rax        ; acc
   mov    %rbp,%rdi        ; v                    mul    %r12             ; acc*nwin -> rdx:rax
   add    $0x1,%r14        ; it++                 mov    %rbp,%rdi        ; v.ptr
   mul    %r12             ; acc*nwin -> rdx:rax  mov    %rbx,%rsi        ; v.len
   mov    %rdx,%rsi        ; off = high half      mov    %r15,%rcx        ; win_len
   mov    %r13,%rdx        ; win_len              call   ...6unsafe6kernel
   call   1730 <kernel>                           mov    %r14,%rcx
   mov    %rax,%rdx        ; r                    shl    $0x5,%rcx        ; acc*32
   mov    %rbx,%rax                               sub    %r14,%rcx        ;  - acc
   shl    $0x5,%rax        ; acc*32               mov    %rcx,%r14
   sub    %rbx,%rax        ;  - acc  = acc*31     add    %rax,%r14        ;  + r
   lea    (%rax,%rdx,1),%rbx ; + r                dec    %r13
   cmp    0x10(%rsp),%r14                         jne    15100            ; back edge
   jb     1250 <main+0xb0>
```

`off` is the *high* half of the 128-bit product, so it arrives in `%rdx` — which
is already the Rust kernel's third argument register. R4's loop therefore lost
five instructions in the swap (18 → 13), not one; the modulo needed an `xor
%edx,%edx` before the `div` and a `mov` to place the remainder.

Measured effect of the swap, `O3 isolated`, `small.bin`, 200 000 kernel calls:

| rung | Ir(kernel) before → after | Ir(main) before → after | per call | wall min (ms) |
|---|---|---|---:|---|
| c-gcc | 254,400,000 → **254,400,000** | 3,000,052 → 2,800,052 | −1.00 | 25.70 → 24.51 |
| c-clang | 180,000,000 → **180,000,000** | 3,800,048 → 2,600,052 | −6.00 | 15.99 → 15.08 |
| safe_naive | 182,400,000 → **182,400,000** | 3,816,284 → 2,616,286 | −6.00 | 16.98 → 16.11 |
| safe_tuned | 181,000,000 → **181,000,000** | 3,816,284 → 2,616,286 | −6.00 | 16.98 → 15.97 |
| unsafe | 180,200,000 → **180,200,000** | 3,616,285 → 2,616,286 | −5.00 | 16.20 → 15.36 |
| verus | 180,200,000 → **180,200,000** | 3,616,286 → 2,416,291 | −6.00 | 17.16 → 15.40 |

**Every kernel `Ir` is unchanged to the instruction.** The swap touched the
driver and only the driver, which is exactly the property that makes it safe to
do — the kernel column, which is where every perf claim in this pattern lives,
did not move at all.

Two honest caveats on the wall-clock column:

- `small` gets 4–6 % faster; **`large` gets 4–5 % slower** (c-gcc isolated
  35.84 → 37.51 ms). The kernel `Ir` is identical, so this is a memory-system
  effect: `off` is now derived from the *high* bits of `acc` rather than the low
  ones, so the offset *sequence* over the 12 MB array is different. Both
  sequences are uniform over `[0, nwin)`; neither is more "correct". Do not read
  it as a cost of the multiply.
- The predicted de-compression of cross-rung ratios is **real but tiny here**:
  `safe_naive / c-clang` on `small` moved 1.062 → 1.068. Wall clock on this
  bench includes ~14 ms of process start-up and file reading against a ~2 ms
  measured loop, and *that* additive constant dwarfs 20–40 cycles per call. The
  argument for the swap stands on the `Ir` column and on the principle; the
  wall-clock ratios were never going to move much until start-up is out of the
  measurement.

Read the chain: `acc` → `div` → `off` → `call kernel` → `acc`. Call *i+1* cannot
start until call *i* has returned. There is nothing for LLVM to CSE and nothing
to hoist, which is why the `call` is still there at `-O3` with the kernel's
result genuinely consumed.

(LLVM's extra `or`/`shr $0x20`/`jne` in the Rust and clang rungs is a 64-bit
divide specialised into a 32-bit one when both operands happen to fit — a real
optimisation on the *driver*, identical across R2–R5, outside the measured
kernel.)

In `whole` mode the kernel symbol is gone — inlined, on purpose — and the
vectorised sum appears as a **nested** loop inside the same driver loop. clang C
and unsafe Rust emit the identical 7-instruction body:

```
movdqu (%rax,%r9,8),%xmm2     inner loop, 7 instructions, nested inside the
paddq  %xmm2,%xmm1            0x1b42..0x1be7 (clang) / 0x15130..0x151d7 (rustc)
movdqu 0x10(%rax,%r9,8),%xmm2 driver loop that contains the `div`
paddq  %xmm2,%xmm0
add    $0x4,%r9
add    $0xfffffffffffffffc,%rdx
jne    <back edge>
```

`harness/check.py` step 3a re-derives this mechanically for all 28 cells: a
backward branch inside the symbol, a memory operand, and a body above a floor.
That is necessary and not sufficient — a kernel that was hoisted or CSE'd still
has all three — so step 3b measures the **marginal executed instructions per
kernel call**: whole-program `Ir` at 200 driver iterations minus `Ir` at 100,
over the 100 extra calls. A difference of two runs of the same binary in the
same shell, so every loader and environment term cancels, and it needs no
symbol, which is why it works in `whole` mode and at `O0`. A collapsed loop
reads ~0.

**The floor is derived, not declared** (TASK_005). `spec.md` used to pin an
absolute 400 against a measured minimum of 915 — 0.80 Ir per element against
1.83 achieved — and, worse, it was a number the pattern author could lower in
the same commit that broke the loop. `model.py` now reports `work_per_call`
(elements summed, from the input bytes alone) and `check.py` asserts
`marginal_Ir >= ALPHA * work_per_call` with ALPHA a *harness* constant, plus
`d(Ir)/d(work) >= ALPHA` across two probe shapes (`small.bin`, 501 elements;
`large.bin`, 4096). Measured after the barrier swap: marginal Ir per call
**908 … 274 496** over 56 cell/probe pairs, `d(Ir)/d(work)` **1.75 … 67.00**,
against ALPHA = 0.25.

## 2. A Verus proof costs zero instructions — both halves

`isolated`, raw machine-code bytes (`harness/asm.py`). **Quoted on the declared
symbol extent (`nm --print-size`, `md5_fn`)**, which is the function proper;
`md5_raw` is objdump's grouping and also covers the alignment padding that
follows the function, so it is given beside it with the padding stated. Both
conventions agree on every equality here (`.memory/03-measurement.md`).

| pair | O3 `md5_fn` | O3 `md5_raw` | O0 | counts `n_fn`/pad-excl (+padding) |
|---|---|---|---|---|
| R4 `unsafe` vs R5 `verus` | **equal**, `619b1d1b…` | **equal**, `fb90a96c…` | `md5_fn` differs (`1dffc20c…` vs `779a1133…`); `md5_fn_norel` **equal** `e5bc48f2…` | 36 / 34 both (+3 insn, 3 B padding) |
| R2 `safe_naive` vs R2v `safe_naive_verus` | **equal**, `f8e1fe32…` | **equal**, `6c85987d…` | **equal**, `3ab6079d…` | 49 / 47 both (+10 insn, 10 B padding) |

(TASK_002 published 39/34 and 59/47 as the "raw" counts; those are objdump's
grouping, i.e. the function *plus* its trailing padding. The function itself is
36 and 49 instructions. Neither the deltas nor the equalities move.)

and the dynamic side agrees exactly: R5's kernel `Ir` equals R4's, and R2v's
equals R2's, on both `small` and `large`, to the instruction.

The O0 R4-vs-R5 row is the interesting one and it is **not** a codegen
difference. At `-O0` the Rust kernel still calls `Iterator::next`, and a
`call rel32` encodes the distance to its callee; the crate names `6unsafe` and
`5verus` are different lengths, so every symbol shifts. The whole difference is
three `call`/`jmp` displacements and one `%rip` displacement — see
`.memory/03-measurement.md`, "The raw-byte oracle has one blind spot". Reported
as the weaker `md5_raw_norel` claim, explicitly labelled.

**Getting this to hold required writing R5's exec code *textually* identical to
R4's, not merely equivalently.** R4 as `for i in 0..len` and R5 as
`while i < len` produced the same instructions in a different order (two
independent `add`/`sub` swapped) — same count, same normalised text, different
bytes. Verus supports `for i in 0..n` with `invariant`, so both use it. This is
exactly the drift `md5_norm` cannot see, caught by the byte oracle on its first
real outing. Recorded in `.memory/04-verus.md`.

## 3. The safety tax is O(1) per call — and it is not one number

The two canonical inputs, `-O3 isolated`, callgrind per-function exclusive `Ir`
for the kernel symbol (total, and per call):

| input | calls | gcc | clang | R2 naive | R3 tuned | R4 unsafe | R5 verus | R2v |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `small` (win 501, res 1) | 200 000 | 254,400,000 | 180,000,000 | 182,400,000 | 181,000,000 | 180,200,000 | **180,200,000** | **182,400,000** |
| per call | | 1272 | 900 | 912 | 905 | 901 | 901 | 912 |
| `large` (win 4096, res 0) | 20 000 | 205,180,000 | 143,740,000 | 144,320,000 | 143,840,000 | 143,740,000 | **143,740,000** | **144,320,000** |
| per call | | 10259 | 7187 | 7216 | 7192 | 7187 | 7187 | 7216 |

R5 equals R4 exactly and R2v equals R2 exactly, on both inputs — the dynamic
half of finding 1. And the two inputs already disagree about R2's overhead
(+11/call at `win_len` 501, +29/call at 4096), which is the point of choosing
them at different residues. The full picture, from `gen.py --sweep`:

| win_len | mod 4 | gcc | clang | R2 naive | R3 tuned | R4 unsafe | R5 verus |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 500 | 0 | 1269 | 894 | 923 | 899 | 894 | 894 |
| 501 | 1 | 1272 | 900 | 912 | 905 | 901 | 901 |
| 502 | 2 | 1274 | 904 | 918 | 909 | 905 | 905 |
| 503 | 3 | 1277 | 908 | 924 | 913 | 909 | 909 |
| 512 | 0 | 1299 | 915 | 944 | 920 | 915 | 915 |
| 515 | 3 | 1307 | 929 | 945 | 934 | 930 | 930 |

Delta vs R4, across `win_len` 500–515 (`gen.py --sweep`, 16 window lengths):

| rung | residue 0 | residue 1 | residue 2 | residue 3 |
|---|---:|---:|---:|---:|
| R2 safe-naive | **+29** | +11 | +13 | +15 |
| R3 safe-tuned | +5 | +4 | +4 | +4 |
| R5 verus | 0 | 0 | 0 | 0 |
| R1 clang | 0 | −1 | −1 | −1 |
| R1 gcc | +375…+384 | +371…+380 | +369…+378 | +368…+377 |

Three things fall out:

- **The delta does not grow with `win_len`.** +29 at 500, 504, 508 *and* 512.
  The bounds check is hoisted clean out of the vectorised loop; the cost is
  per *call*, not per element. Same conclusion as the pilot, on a different
  kernel and with a data-dependent offset.
- **`.memory/01-ladder.md`'s residue trap is real and it nearly bit again.** The
  first version of `inputs/gen.py` used `win_len` 500 for `small` and 4096 for
  `large` — both ≡ 0 (mod 4), the only residue where R2 costs +29. Quoting that
  as "safe Rust costs +29 instructions per call" would have overstated it by
  ~2.4× against residues 1–3. `small.bin` now uses **501** so the two canonical
  inputs straddle residues and the default table cannot hide the effect.
- **R3 is the honest number for "what safe Rust costs": +4 to +5 instructions
  per call, on a ~900-instruction call — under 0.6%.** Never publish R2 alone.

gcc is the outlier: ~41% more executed instructions than clang on identical
source, because it vectorises 2 elements/iteration where clang does 4 with a 2×
unroll. `.memory/01-ladder.md`'s "always report a clang column" reproduces here
on a second kernel.

### … and it grows when the kernel is inlined

`whole` mode, `large.bin`, `main`-exclusive `Ir` (the kernel has no symbol left):

| rung | main Ir | minus that cell's `isolated` main Ir | vs R4 |
|---|---:|---:|---:|
| c-gcc | 205,260,109 | 204,960,057 | +61,340,056 |
| c-clang | 144,000,127 | 143,620,079 | **−1** |
| R2 safe-naive | 162,800,291 | 150,420,007 | **+6,799,927** |
| R3 safe-tuned | 156,080,286 | 143,700,002 | −19,918 |
| R4 unsafe | 155,980,286 | 143,620,001 | 0 |
| R5 verus | 155,960,285 | 143,599,999 | −20,002 |

The subtraction is necessary and is the trap in this table: `main`-exclusive
counts everything *else* inlined into `main`, and that is a different set per
language. The Rust rungs inline the whole payload decoder into `main` (~12.36 M
instructions on `large`); the C rungs leave it in `common/driver.c`'s own
symbols (~0.38 M). Comparing the raw column would report an 8% clang win that
does not exist. After subtracting, **clang and unsafe Rust are equal to within 1
instruction across 82 million additions.**

The real finding here is R2: out of line its overhead is +29 per call, inlined it
is **+340 per call**, a 12× amplification. The disassembly says why — inlined,
R2's scalar epilogue keeps a live per-element bounds check with a panic exit:

```
lea    (%rsi,%r10,1),%rdi
cmp    %rbx,%rdi
jae    15340 <panic>          <-- per element, inside the epilogue loop
inc    %rsi
add    0x0(%rbp,%rdi,8),%rax
dec    %rdx
jne    15260
```

and the driver's offset computation is rematerialised — measured at TASK_003,
when the barrier was still `acc % nwin`, R2's `whole` `main` contained **four**
`div` sites in the driver loop where R4 contained two. The barrier is a
multiply-shift since TASK_005, so re-derive this before quoting it. R3 shows neither
effect. Treat this as an observation, not a settled result: it is derived from a
difference of two builds, and only `large` (`win_len` 4096, residue 0) shows it.
It does reinforce the standing rule — **R3, not R2, is the honest number for what
safe Rust costs.**

## 4. TCB tally

Counted per `.memory/04-verus.md`: every line inside `#[verifier::external_body]`
bodies, `assume_specification`, `assume(...)`, reachable `#[verifier::external]`
items, and `unsafe` blocks. **Every item listed individually**, not just the
interesting one.

### R5 (`verus.rs`) — TCB: 6 lines across 3 items

| # | item | attribute | body lines | `requires` | `ensures` | contains `unsafe` |
|---|---|---|---:|---|---|---|
| 1 | `get_unchecked` | `external_body` | 1 | `i < v@.len()` | `r == v@[i as int]` | **yes** |
| 2 | `load_input` | `external_body` | 4 | — | **none** | no |
| 3 | `emit` | `external_body` | 1 | — | **none** | no |

Plus **`common/driver.rs`, 77 code lines**, external-by-default and reachable
from items 2 and 3. It is *not* reachable from the kernel, so the memory-safety
claim does not rest on it; the benchmark's correctness does, which is why the
same file is shared verbatim by R2–R4 and diffed by `harness/check.py`.

Zero `assume(`, zero `admit(`, zero `assume_specification` of our own.

Three deliberate choices behind that table:

- **Item 1 is the whole memory-safety TCB, and it is one line.** Its `ensures` is
  justifiable in one sentence: the standard library documents `get_unchecked` as
  yielding `v[i]` provided the caller guarantees `i < v.len()`, which is exactly
  the `requires`. Nothing weaker would license the `unsafe`; nothing stronger is
  claimed.
- **Items 2 and 3 state no `ensures` at all.** An `ensures` on a file reader would
  be an axiom about the contents of a file, which nothing can justify — and a
  wrong `ensures` on an `external_body` axiomatises a falsehood and invalidates
  everything above it. Every fact the proof needs is instead re-derived at run
  time from `vals.len()` (specified by vstd) inside verified code.
- vstd axioms used and therefore trusted transitively: `slice::group_slice_axioms`,
  `Vec::len`, `Vec::as_slice`, and the `assume_specification`s for
  `u64::wrapping_add` / `wrapping_mul`. These are vstd's TCB, not this project's,
  but they are not zero and are named here rather than assumed away.

### R2v (`safe_naive_verus.rs`) — TCB: 5 lines across 2 items

`load_input` (4) and `emit` (1). No `get_unchecked`, no `unsafe` anywhere in the
file. **A strictly smaller trusted base, and strictly worse code** (49 / 47
static on the `nm` extent vs R4's 36 / 34, +11…+29 `Ir` per call). That is
finding 2 of `.memory/01-ladder.md` stated as a trade: the proof only pays when
it licenses something.

## 5. The proof covers the measured domain — and is not vacuous

Rule 2 of `.memory/02-bench-rules.md` — the one the pilot failed — is satisfied
structurally *and* semantically: `fn main` is inside `verus! { }`, is not
`external_body`, and contains the call `kernel(vs, off, win_len)`; and
`verus verus.rs --verify-function main --verify-root` reports **2 verified**
(one query for the function, one for its loop body — see the note on the
obligation count in `spec.md`),
which is Verus itself confirming `main` has a verified body. (An `external_body`
`main` reports **0 verified** — that is the pilot's defect detected semantically
rather than by recognising an attribute, which is what a blank line defeated.)

Rules 1 and 3 are enforced numerically: `check.py` drives this pattern's own
`model.py` from the input file, then evaluates the contract in `spec.md` at
**every call the benchmark actually makes** (220 000 of them across `small` and
`large`) and re-derives the `ensures` on a sample with a second, independent
summation. **Every input is evaluated, `adversarial-*` included** — p01's
adversarial inputs all make zero kernel calls, so they are vacuously inside the
domain, but the previous gate never looked, and for a pattern whose adversarial
input is aimed at the precondition that is the one input that matters.

But a green verification proves nothing by itself, so the proof was mutated and
each mutant checked to fail. **Re-run at TASK_003**, because TASK_002 mis-quoted
M5's evidence:

| # | mutation | verifier result | caught by the gate? |
|---|---|---|---|
| M5a | `nwin = n_vals − win_len + **2**`, loop invariant left alone | **fails** — `possible arithmetic underflow/overflow` at the `nwin` line **and** `invariant not satisfied before loop`. *Not* at the call. | driver pin |
| M5b | the same, with the invariant repaired to `nwin == n_vals − win_len + 2` | **fails** — `precondition not satisfied … off + len <= v@.len()` at **`verus.rs:126:26`, the `kernel(vs, off, win_len)` call** | driver pin |
| M1 | driver guard `win_len_w <= n_vals + 1` | **fails** — underflow in `n_vals − win_len` | driver pin |
| M2 | kernel's `requires` deleted | **fails** — loop invariant not established at entry | contract pin |
| M4 | `ensures` shifted by one element (`len + 1`) | **fails** — postcondition not satisfied | contract pin |
| M6 | kernel's `ensures` **deleted entirely** | **fails** — `4 verified, 1 errors`, at the driver's ghost `assert` | contract pin |
| M7 | kernel's `ensures` replaced by `r == r` | **`5 verified, 0 errors`** with the pre-TASK_003 driver; with the ghost assert it fails | contract pin |
| M3 | **`requires` deleted from the trusted `get_unchecked`** | **VERIFIES, 7 verified 0 errors** — no diagnostic, ever | structural rule (TASK_005) |

**M5 is the evidence that the call site is load-bearing, and TASK_002 quoted the
wrong half of it.** The published mutant fails *before* the call, at the loop
invariant, so on its own it proves only that the invariant mentions `nwin`. The
real evidence needs the invariant repaired too (M5b) — and then Verus rejects it
*at the call*, naming the precondition. Substance was right, evidence was
mis-quoted.

**The `ensures` is now consumed.** The driver carries one ghost line:

```rust
let r: u64 = kernel(vs, off, win_len);
assert(r == sum_wrap(vs@, off as int, win_len as int));
```

Before it, deleting the postcondition entirely (M6) still gave `5 verified, 0
errors` — the `ensures` was free decoration defended only by mutation testing.
Ghost code erases, so R5's kernel is still byte-identical to R4's (`md5_fn`
`619b1d1b…` both, `-O3 isolated`) and the driver loop still matches the pin:
`harness/dloop.py` exempts ghost statements exactly as it exempts
`invariant`/`decreases`. The byte-identity objection TASK_002 raised against
doing this was really an objection to the gate's own textual rule.

**M3 is the warning, and the pin was not enough.** TASK_003_REVIEW showed that
the pin moves with the code: deleting `requires i < v@.len()` from `get_unchecked`
*and* the matching three characters from `spec.md` gave a full green gate,
"3 TCB items, all contracts identical to spec.md", and an R5 whose trusted base
axiomatises that reading any index of any slice is defined and yields `v@[i]`.
No declared pin can defend against an attacker who writes the pins. TASK_005
added a structural rule instead: **an `external_body` item whose body contains
`unsafe` must carry a non-empty `requires`** — a trusted item that performs an
unchecked operation and demands nothing of its callers is an axiom that the
operation is always safe. The only escape is a per-item justification string in
`spec.md` that the gate prints in the verdict on every single run.

The pin is still there and still necessary, for the reason below.
Weakening an `external_body` item's `requires` never produces an error: it
silently deletes the obligation from every caller and makes the memory-safety
claim vacuous, with the same "N verified, 0 errors" on stdout. No verification
result can catch that, because the mutant is a perfectly well-formed proof of a
weaker statement. `spec.md` therefore pins every item's `external` attribute,
`requires` and `ensures` verbatim, plus the item set and the obligation count,
and `check.py` diffs them. Demonstrated at TASK_003: the old gate reported
`check.py: PASS` on M3 and M7; the new one fails with the exact clause diff.

## 6. Proof sticking points

- **`v@.len() <= usize::MAX` is not free for a slice.** Without it, `off + i` on
  provably in-bounds indices still reports "possible arithmetic
  underflow/overflow". The fact lives in `vstd::slice::axiom_spec_len`, whose
  trigger is `spec_slice_len(slice)` — a term that never appears in ordinary
  code, so the broadcast never fires. One ghost line fixes it:
  `assert(v@.len() == vstd::slice::spec_slice_len(v));`.
- **Wrapping arithmetic removed the entire value-domain problem.** With
  `wrapping_add`, the kernel has no precondition on element *values*, so the
  input generator can emit full-range `u64`s and every measured input is inside
  the verified domain by construction. The pilot's `requires v[i] < 1000` is what
  made its published run fall outside its own postcondition. `wrapping_add` is
  `#[verifier::allow_in_spec]` in vstd, so the same call works in the `spec fn`.
- **`-C lto=fat` cannot be used for an R5 cell**: Verus links a precompiled
  `vstd` rlib with no bitcode (`Can't find section .llvmbc`). The `whole` inline
  mode is therefore defined without rustc LTO for all Rust rungs — otherwise R5
  drops out of the matrix and the comparison breaks. C still uses `-flto`,
  because C genuinely has three translation units to merge and a single-crate
  Rust binary at `codegen-units=1` does not.
- `verus_run.py` forwards unknown flags to rustc, so `--cfg slb_isolated`,
  `-C opt-level`, `-C debug-assertions` and `-C codegen-units` all work and R5
  sits on the same build axes as every other rung.

## 7. Adversarial behaviour

p01 models no memory-safety bug, so the adversarial set is degenerate *shapes* —
the inputs that catch a sloppy driver. All seven rungs behave identically on all
six, which is the expected (and required) answer for a calibration pattern:

| input | all rungs | why |
|---|---|---|
| `adversarial.bin` (`n_iters = 0`) | exit 0, prints `0` | the `while` never runs |
| `adversarial-empty.bin` (`payload_len = 0`) | exit 0, prints `0` | no head word ⇒ `win_len_w = 0` ⇒ guard skips the loop |
| `adversarial-headonly.bin` (head, no values) | exit 0, prints `0` | `win_len 8 > v_len 0` |
| `adversarial-winbig.bin` (`win_len = 2^40`) | exit 0, prints `0` | guard compares in `u64` *before* the `as usize` cast, so a truncating driver cannot sneak past |
| `adversarial-win0.bin` (`win_len = 0`) | exit 0, prints `0` | `win_len_w > 0` is checked first; otherwise `nwin` would be `v_len + 1` and `off` could equal `v_len` |
| `adversarial-shortlen.bin` (declares 4096 B, carries 40) | **exit 5**, message on stderr | `slb_load` / `driver::load` read exactly `payload_len` bytes and refuse a short file |

The C rung is clean under **ASan + UBSan** on all eight inputs
(`harness/check.py` step 7), so the shared driver has no undefined behaviour to
misattribute to a rung later.

## 8. Known gaps

- **No Miri run on R4/R5, and that is now a policy decision rather than an
  omission.** `.memory/02-bench-rules.md` makes Miri mandatory exactly when R4
  and R5 are *not* byte-identical, because that is when R4 stops inheriting R5's
  discharged obligations. p01's are byte-identical at `-O3` (`md5_fn`
  `619b1d1b…` both), so it is exempt, and `spec.md` records the exemption in
  `miri.required` where `check.py` step 8 reads it. Note Miri is **not
  installed** for the pinned stable toolchain on this box, so the first pattern
  that needs it must solve that first; the gate will say so rather than skip.
- **Whole-mode `Ir` is `main`-exclusive**, not kernel-exclusive — the kernel has
  no symbol left to attribute to. It includes the loader, so it is comparable
  across rungs within that mode and to nothing else.
- **`panic=abort` and `O0d` (debug-assertions on) were built but not measured.**
  Both are supported axes in `harness/build.py`; neither is in the 24-cell
  matrix, and neither has numbers here.
- ~~The C driver loop is checked by required substrings~~ — **fixed at
  TASK_003.** A cross-language mechanical diff *is* possible: `harness/dloop.py`
  normalises both languages (types, casts, `wrapping_*` methods, grouping
  parens, Verus clauses, ghost statements) to one token sequence, and three
  explicit aliases in `spec.md` (`n_body` ≡ `vals.len()`, `inp.n_iters` ≡
  `n_iters`, `vals` ≡ `vals.as_slice()`) reconcile the names that genuinely
  differ. All six driver loops — five Rust and the C one — normalise to the same
  12-statement sequence, and every one of them is diffed against the sequence
  pinned in `spec.md` rather than against each other. The substring check had
  passed with a `__builtin_prefetch` and an `__asm__ __volatile__` memory
  barrier added to the C loop.
- **The anti-collapse barrier does not, on this pattern, actually prevent a
  collapse.** Measured at TASK_003, when the barrier was `acc % nwin`: replacing
  it with `off = 0` in every rung left the marginal cost at ~902–908 Ir per call
  (vs 915–919 with the barrier), because LLVM does not hoist a whole inner loop
  out of an outer one. The multiply-shift barrier is cheaper still, so this gap
  is now smaller, not larger. So on p01 the barrier is insurance, not load-bearing — and it is
  the `spec.md` driver pin, not the `Ir` floor, that catches its removal. Do not
  generalise: a pattern whose kernel is a single expression is a different case.
