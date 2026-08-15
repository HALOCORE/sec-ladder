# p01 — findings, TCB tally, sticking points

Numbers here are from `results/p01-array-sum.json`; the generated table is
`results/tables/p01-array-sum.md`. Regenerate with `harness/measure.py p01`
then `harness/report.py p01`.

---

## 1. The benchmark does not evaporate — shown, not asserted

The anti-collapse mechanism is the serial dependency `off = acc % nwin`, where
`acc` is the running checksum. It is the same arithmetic in C and in Rust, so
neither language gets a stronger optimisation barrier than the other. No
`black_box`, no `asm volatile`.

`main`, `-O3`, `isolated`, innermost loop containing `call kernel` — every rung
has one, and it is a real loop:

```
R1 gcc (15 instructions, 0x1210 → 0x1240)      R4 unsafe (18, 0x15150 → 0x15187)
   mov    %rbx,%rax        ; acc                  mov    %r14,%rax        ; acc
   xor    %edx,%edx                               xor    %edx,%edx
   mov    %r12,%rdi        ; v                    div    %rbp             ; acc % nwin
   add    $0x1,%r14        ; it++                 mov    0x28(%rsp),%rdi  ; v
   div    %rbp             ; acc % nwin           mov    %r15,%rsi        ; off
   mov    %rdx,%rsi        ; off = remainder      mov    %rbx,%rcx        ; win_len
   mov    %r13,%rdx        ; win_len              call   ...6unsafe6kernel
   call   1660 <kernel>                           mov    %r14,%rcx
   mov    %rax,%rdx        ; r                    shl    $0x5,%rcx        ; acc*32
   mov    %rbx,%rax                               sub    %r14,%rcx        ;  - acc
   shl    $0x5,%rax        ; acc*32               mov    %rcx,%r14
   sub    %rbx,%rax        ;  - acc  = acc*31     add    %rax,%r14        ;  + r
   lea    (%rax,%rdx,1),%rbx ; + r                dec    %r13
   cmp    0x10(%rsp),%r14                         je     ...
   jb     1210 <main+0xb0>                        mov    %r14,%rax
                                                  or     %rbp,%rax
                                                  shr    $0x20,%rax
                                                  jne    15150            ; back edge
```

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

`harness/check.py` step 3 re-derives this mechanically for all 28 cells: a
backward branch inside the symbol, a memory operand, and a body above a floor.

## 2. A Verus proof costs zero instructions — both halves

`isolated`, raw machine-code bytes (`harness/asm.py`, `md5_raw`):

| pair | O3 `md5_raw` | O0 `md5_raw` | raw / padding-excluded |
|---|---|---|---|
| R4 `unsafe` vs R5 `verus` | **equal**, `fb90a96c…` | differs; `md5_raw_norel` **equal** `0f0060ce…` | 39 / 34 both |
| R2 `safe_naive` vs R2v `safe_naive_verus` | **equal**, `6c85987d…` | **equal**, `e68a5b96…` | 59 / 47 both |

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

and the driver's `acc % nwin` is rematerialised — R2's `whole` `main` contains
**four** `div` sites in the driver loop where R4 contains two. R3 shows neither
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
file. **A strictly smaller trusted base, and strictly worse code** (59/47 static
vs R4's 39/34, +11…+29 `Ir` per call). That is finding 2 of
`.memory/01-ladder.md` stated as a trade: the proof only pays when it licenses
something.

## 5. The proof covers the measured domain — and is not vacuous

Rule 2 of `.memory/02-bench-rules.md` — the one the pilot failed — is satisfied
structurally: `fn main` is *inside* `verus! { }`, is *not* `external_body`, and
contains the call `kernel(vs, off, win_len)`. `harness/check.py` step 5 asserts
all three by parsing `verus.rs`, so it cannot regress silently.

Rules 1 and 3 are enforced numerically: `check.py` simulates the driver in Python
from the input file, then evaluates the contract in `spec.md` at **every call the
benchmark actually makes** (220 000 of them across `small` and `large`) and
re-derives the `ensures` on a sample with a second, independent summation.

But a green verification proves nothing by itself, so the proof was mutated and
each mutant checked to fail:

| # | mutation | result |
|---|---|---|
| M5 | `nwin = n_vals − win_len + **2**` (so `off` can reach one past the last window) | **fails** — `precondition not satisfied … off + len <= v@.len() … at kernel(vs, off, win_len)` |
| M1 | driver guard `win_len_w <= n_vals + 1` | **fails** — underflow in `n_vals − win_len` |
| M2 | kernel's `requires` deleted | **fails** — loop invariant not established at entry |
| M4 | `ensures` shifted by one element (`len + 1`) | **fails** — postcondition not satisfied |
| M3 | **`requires` deleted from the trusted `get_unchecked`** | **VERIFIES, 5 verified 0 errors** |

M5 is the evidence that the call site is load-bearing: perturb the driver's
arithmetic by one and Verus rejects it *at the call*, naming the precondition.

One honest caveat: **the kernel's `ensures` is verified but not *consumed*.**
`main` folds the return value into the checksum without asserting anything about
it, so nothing downstream depends on `r == sum_wrap(...)`. Its non-triviality
rests on mutation M4 (perturb it and verification fails), not on a call-site
obligation the way the `requires` does. Consuming it would mean a ghost
assertion inside the driver loop, which would break the loop's byte-identity
with the other four rungs — a worse trade for a calibration pattern. Patterns
that model an actual bug should make the `ensures` load-bearing.

M3 is the warning. Weakening an `external_body` item's `requires` never produces
an error — it silently deletes the obligation from every caller and makes the
memory-safety claim vacuous, with the same "N verified, 0 errors" on stdout.
`check.py` cannot catch it (the mutant is a perfectly well-formed proof of a
weaker statement); only reading the trusted signatures can. Written up in
`.memory/04-verus.md`.

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

- **No Miri run on R4/R5.** `get_unchecked` correctness is argued from the
  proof (R5) and by inspection (R4), and ASan/UBSan cover only the C side.
- **Whole-mode `Ir` is `main`-exclusive**, not kernel-exclusive — the kernel has
  no symbol left to attribute to. It includes the loader, so it is comparable
  across rungs within that mode and to nothing else.
- **`panic=abort` and `O0d` (debug-assertions on) were built but not measured.**
  Both are supported axes in `harness/build.py`; neither is in the 24-cell
  matrix, and neither has numbers here.
- The C driver loop is checked against the Rust one by required substrings, not
  by a mechanical diff — a cross-language diff is not possible. The equivalence
  argument is in `spec.md`.
