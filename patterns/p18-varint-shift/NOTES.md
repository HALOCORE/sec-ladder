# p18 — LEB128 varint decoder: findings

Read `README.md` for what the pattern is and `spec.md` for the contract. This
file is the evidence: every number below was produced by a command that is
quoted beside it, and every generator is committed under `controls/` or
`inputs/`.

**Provenance of the declaration.** `spec.md`'s `idiom` block was written after
the seven rungs, the R5 proof and the checksums existed and **before any p18
cell had been measured for perf**. What did exist is §0 below — a standalone
six-kernel C probe with no driver and no pattern. See the `why` key for the
full statement.

---

## 0 — settling the bug class, before five rungs were built on it

`.memory/06-catalogue.md` gives p18's class as *"unbounded shift, truncation"*.
**That row is UPHELD** — the first catalogue row in five patterns that is, after
p07, p06, p14 and p13 all overturned theirs. The evidence is a standalone
six-kernel C probe with no driver and no pattern
(`.temp/p18/probe/kprobe.c`, `.temp/p18/probe/gen_probe.py`), built at
gcc/clang × `-O0`/`-O3` and run over four blobs.

```
build          kernel   benign                 hostA                  hostB                  hostC
gcc-O0         noguard  3943843381207753163    1995                   13708497240779343060   33
gcc-O0         guard    3943843381207753163    11                     9223372036854775828    33
gcc-O0         cap10    3943843381207753163    42                     8716991365862673455    18446744053601349569
gcc-O0         cap9     8450954230241325735    3979                   1376601537678976719    9223371155534041152
gcc-O0         unbnd    3943843381207753163    11                     9223372036854775828    33
gcc-O0         reject   3943843381207753163    11                     20                     64
  ... and gcc-O3, clang-O0, clang-O3 reproduce every one of those 24 values EXACTLY.
```

**The bug: an unbounded shift count in the varint accumulation.**
`val |= (c & 0x7f) << shift` with `shift = 7*nb`, and no `shift < 64`. The
eleventh byte of a varint is shifted by 70; C99 6.5.7p3 makes that undefined and
x86-64's `shlq %cl` masks the count to six bits, so the payload lands in the
wrong bit position and the decoder returns a silently wrong integer.

### 0a — why this bug and not a neighbouring one

**The kernel writes nothing and reads nothing out of bounds, on any input, in
any rung.** That is the point: it is the first bug in this project that is
undefined behaviour without being a memory-safety bug. p14's per-call scratch
discipline degenerates here to "there is no scratch": `val`, `shift`, `nb`, `p`
and `acc` are scalars, nothing crosses a call boundary, and the kernel is a
function of its arguments by construction. §0c measures that rather than
asserting it.

### 0b — the four rejected candidates, each with the measurement that rejected it

| candidate | probe kernel | why rejected |
|---|---|---|
| **cap the varint at ten bytes** (`i < 10` in the loop head) instead of guarding the shift | `k_cap10` | It is a **different function** — 42 / 8716991365862673455 / 18446744053601349569 against the guarded kernel's 11 / 9223372036854775828 / 33 on hostA/B/C. And it is decisive against it as a *rung*: with `nb < 10` in the loop condition, `shift <= 63` is statically implied, so **the guard becomes dead and there is no run-time check to price**. That is p14's aliasing candidate (a compile-time rejection with nothing to measure) in a new costume. Priced anyway as `c_ncap`, §9. |
| **cap at nine** — the classic off-by-one of the cap spelling | `k_cap9` | Wrong on **benign** input (8450954230241325735 against 3943843381207753163), so no set of rungs could agree on `small`/`large` at all. It is a truncation bug, not a shift bug, and a strictly worse version of §7b's. |
| **unbounded scan** — stop only on the continue bit, not on the window | `k_unbnd` | Measured **identical to the guarded kernel on all four probe blobs**, because the harm needs a different input (one with no terminator inside the window) — and that harm is an out-of-bounds READ with p11's loop body. p14 rejected the same candidate for the same reason. p18 keeps `while (p < len)` in every rung, R1 included, so it is not p11 and not p16. |
| **reject rather than truncate** as the hardened answer | `k_reject` | It needs a second live variable and a second test, so R1-vs-R1h would stop being a one-line difference; and it is a **different function** (17654844475008 against 18446734407611127296 on `adversarial-sat`). Rejecting also deletes §7b — the row on which every rung agrees, every catcher is silent, and the answer is still wrong. Priced as `c_reject`, §9: `+1.00·varints + 2.00` Ir/call over truncating. |

**Truncation ships as the hardened answer**, which is what the Linux kernel's
`uleb128` reader, Go's `binary.Uvarint` in its non-error path and most
hand-written protobuf readers do. It is p13's shape one level up: the hardened
cell is memory-safe, well-defined, and loses data.

### 0c — the kernel is a function of its arguments, measured

p14's §0 found a candidate that was *not*, and the failure is silent. p18's
kernel has no scratch and no static state, so the check is that the driver's
repeat protocol produces a constant marginal:

```
$ python3 controls/sweep_ir.py --blobs small.bin,large.bin --cells all --n1 2000 --n2 6000
small.bin  24  112  24  0  1899.0000 2123.0000 2034.0000 2260.0000 2695.0000 2307.0000 2332.0000 2331.0000
large.bin  10   41  10  0   753.0180  835.0180  804.0180  888.0180 1053.0028  890.0027  902.0027  901.0027
```

Every cell's marginal is an integer to within 0.03 (the driver's `println!`
digit-count term, `.memory/03-measurement.md`: 0.2263 Ir per call per decimal
digit), on both blobs, for all eight cells — which it could not be if any call
after the first did different work. Gate stage 3b makes the same measurement
independently on `n_iters` 100/200 and reports `d(Ir)/d(work) 16.14...58.55`
across 64 cell/probe pairs.

---

## 0.1 — TASK_051's three unverified premises about `O0d`, measured FIRST

The task named its whole `O0d` framing as what it was least sure of and asked
for three measurements before anything was built on them. Probe:
`.temp/p18/shiftprobe/shl.rs`, a LEB128 decode with no guard, shift count
loop-carried, every byte read from a file at run time.

```
rustc --edition 2021 -C codegen-units=1 <flags> shl.rs

O0   (-C opt-level=0 -C debug-assertions=off)  v12 rc=0   18446744073709551615
O0d  (-C opt-level=0 -C debug-assertions=on )  v12 rc=101 PANIC
O3   (-C opt-level=3 -C debug-assertions=off)  v12 rc=0   18446744073709551615
O3d  (-C opt-level=3 -C debug-assertions=on )  v12 rc=101 PANIC

thread 'main' panicked at shl.rs:14:16:
attempt to shift left with overflow
```

1. **An oversized shift DOES panic under `debug-assertions=on` at
   `opt-level=0`.** Confirmed, exit 101.
2. **It DOES mask silently at `debug-assertions=off`**, at both opt levels.
   Confirmed.
3. **rustc does NOT constant-fold it when the count is loop-carried.**
   Confirmed from the `-O3 --cfg slb_isolated` disassembly — a real loop with a
   back-edge, a data load and a *variable-count* shift:

```
   14d03:  movzbl -0x1(%rdi,%rdx), %eax     <- the byte, from the buffer
   14d0b:  andl  $0x7f, %eax
   14d0e:  shlq  %cl, %rax                  <- VARIABLE-count shift, %cl loop-carried
   14d19:  addl  $0x7, %ecx                 <- shift += 7
   14d23:  jb    0x14d00                    <- the back-edge
```

**The flag discriminates and the framing survives.** All three premises hold.

## 0.2 — but TWO of the surrounding claims do NOT, and the honest headline is narrower

TASK_051 says: *"Nothing in the ladder's usual toolkit sees it — not ASan, not
Miri on the Rust side, not a memory-safety proof."* **Two thirds of that is
false**, measured at the gate's own flags.

**(a) UBSan sees it, at `harness/check.py:4390`'s exact flags.**
`-fsanitize=undefined` implies `-fsanitize=shift`, and gate stage 7 greps for
`runtime error`, so p18's own sanitizer row **fires** — on every adversarial
blob, from the shipped `c/kernel.c`:

```
== 7. C rung under ASan + UBSan (per-input expectation) ==
  ok  adversarial-many.bin      sanitizer fired as declared (exit=0):
      patterns/p18-varint-shift/c/kernel.c:72:41: runtime error:
      shift exponent 70 is too large for 64-bit type
  ok  adversarial-sat.bin       ... same
  ok  adversarial-shift11.bin   ... same
  ok  adversarial-shift20.bin   ... same
  ok  truncating.bin            clean, exit=0 (model 0)
```

ASan alone is silent on every input and every rung — nothing is ever accessed
out of bounds — so **p18 is the first pattern in this project whose sanitizer
row is UBSan's rather than ASan's.** That half of the claim holds.

**(b) Miri sees it, because Miri runs with `debug-assertions` ON.**

```
miri --sysroot /home/apt/.cache/miri --edition 2021 -Zmiri-disable-isolation \
     .temp/p18/ctl/n_noguard.rs -- .temp/p18/miri/adversarial-shift11.bin
  rc=101   thread 'main' panicked at n_noguard.rs:67:25:
           attempt to shift left with overflow
```

⚠ It is a **panic**, not `Undefined Behavior`, so `check.py`'s `ub` flag stays
false and the row would fail on the exit code instead
(`check.py:4612`). **That is a hard constraint on the design and it is why no
matrix input may make a shipped Rust rung shift out of range** — every Rust rung
carries the guard, so Miri is silent on all nine p18 inputs (gate stage 8, all
`ok`), and §7 is where it is shown firing.

**(c) Verus sees it**, first attempt, on a three-line probe
(`controls/gen_controls.py` writes `probe_shl_bare.rs`):

```
$ ./verus_run.py .temp/p18/ctl/probe_shl_bare.rs
error: possible bit shift underflow/overflow
verification results:: 2 verified, 1 errors
```

`fn shl_unconstrained(x: u64, s: u32) -> u64 { x << s }` fails; the same body
with `requires s < 64` verifies.

> **The honest headline, narrower than the task's and better specified.** The
> catchers of this bug are **UBSan** (C side), **`-C debug-assertions=on`**
> (Rust side), **Miri** (Rust side) and **Verus**. The non-catchers are **ASan,
> rustc's type system, rustc's bounds checks, and a memory-safety-only
> specification's postcondition**. Every one of the four catchers is outside the
> 24-cell matrix; three of the four non-catchers are what this project has
> called "the safety net" in fourteen previous patterns.

---

## 1 — codegen: what the safety line compiles to, and what it does not delete

Gate stage 3a, all 32 cells: a real loop, a real memory operand, body above
floor. The `isolated` cells' `bulk` column is `-` for **every one of the eight**,
and `vector_regs` is empty for every one of them — **p18's kernel calls no libc
routine and uses no vector register in any rung.** (The `whole` cells report a
`memcpy` and `xmm`, which are `main`'s payload load: in `whole` mode the kernel
is inlined into `main` and `asm.py` measures `main`.) So
`.memory/03-measurement.md`'s *"the kernel-exclusive column is comparable only
when the rungs call the SAME libc routines"* is discharged by naming the **empty
set**, which is the strongest form of that condition and is why p18's
kernel-exclusive column and its differenced marginal measure the same thing.

Static kernel instruction counts, `O3 isolated` (raw / padding-excluded):

| cell | n_fn | nopad | pad | loops |
|---|---|---|---|---|
| c-gcc | 72 | 70 | 0 | 2 |
| c-gcc-h | 74 | 72 | 0 | 2 |
| c-clang | 76 | 73 | 1 | 2 |
| c-clang-h | 82 | 79 | 1 | 2 |
| safe_naive | 115 | 112 | 9 | 2 |
| safe_tuned | 84 | 82 | 12 | 2 |
| unsafe | 71 | 69 | 13 | 2 |
| verus | 71 | 69 | 13 | 2 |

### 1a — the two compilers lower the guard differently, and one of them keeps the shift

**gcc branches around it** (`c-gcc-h`, `-O3`, inner loop at `0x19d0`):

```
   19d0:  movzbl (%r8,%rdx), %esi
   19d5:  addq   $0x1, %rax
   19d9:  addq   $0x1, %rdx
   19dd:  cmpl   $0x3f, %ecx        <-- THE SAFETY LINE, instruction 1 of 2
   19e0:  ja     0x19ee             <-- THE SAFETY LINE, instruction 2 of 2
   19e2:  movq   %rsi, %rdi
   19e5:  andl   $0x7f, %edi
   19e8:  shlq   %cl, %rdi
   19eb:  orq    %rdi, %r10
   19ee:  addl   $0x7, %ecx
   19f1:  testb  %sil, %sil
   19f4:  jns    0x19fb
   19f6:  cmpq   %r9, %rax
   19f9:  jb     0x19d0
```

**clang makes it branchless with a `cmov` — and performs the shift first**
(`c-clang-h`, `-O3`, inner loop at `0x1710`):

```
   1718:  movzbl (%r12,%r11), %ebp
   171d:  movl   %ebp, %esi
   171f:  andl   $0x7f, %ebp
   1722:  shlq   %cl, %rbp          <-- the shift, PERFORMED
   1725:  incq   %r11
   1728:  cmpl   $0x40, %ecx        <-- THE SAFETY LINE, instruction 1 of 2
   172b:  cmovaeq %rdx, %rbp        <-- THE SAFETY LINE, instruction 2 of 2
   172f:  orq    %rbp, %rbx
   1732:  addl   $0x7, %ecx
   1735:  testb  %sil, %sil
   1738:  js     0x1710
```

> **This is the answer to "is R3/R1h actually check-free, or did it just move the
> check?" — on clang it moved it PAST the shift.** The C is well-defined either
> way, because the guard is in the *source* and that is what the standard and
> UBSan read; but *"the hardened rung does not do the dangerous thing"* is a
> statement about the source and not about the instruction stream, and on this
> pattern the two differ.

### 1b — Rust's release `<<` masks EXPLICITLY at `-O0` and implicitly at `-O3`

`unsafe-O0-isolated`, inner loop, `debug-assertions=off`:

```
   17176:  movl   %ecx, %edx
   17178:  movl   0x7c(%rsp), %ecx
   1717c:  andl   $0x3f, %ecx        <-- rustc masks the count ITSELF at -O0
   1717f:  movl   %ecx, %ecx
   17181:  shlq   %cl, %rdx
```

At `-O3` the mask is gone and the hardware's own masking is relied on. So
"Rust's `<<` in release is a masked shift" is not an inference from x86
semantics on this box — it is in the instruction stream at one opt level and
delegated to the hardware at the other, and the value is the same either way
(§7).

---

## 2 — the fold, and what p18 does NOT add to the full-extent argument

Two quantities are folded per varint plus the declared count once, and each is
load-bearing against a different mutation:

| folded | what it catches | shown by |
|---|---|---|
| the decoded **value** `val` | a rung that shifted by the wrong amount or masked the wrong bits | every `adversarial-shift*` row: R1 diverges from the model |
| the **byte count** `nb`, in order | a rung that consumed a different number of bytes | `c_ncap` (§9) diverges on three blobs while its *values* would be a subset |
| the declared count `nv` | a rung that decoded a different number of varints | by construction |

**p18 supplies NO fourth independent reason for the full-extent order-sensitive
fold, and saying so is more useful than inventing one.** TASK_004_REVIEW's
reason is elision, p06's is invariance under permutation, p14's is
partition-blindness; p18's bug corrupts the decoded value itself, which the fold
reads directly, so elision alone justifies the rule here.

**What p18 adds is the counter-observation, and it belongs to the BUG and not to
the fold.** `|=` is idempotent, so a payload wrapped round into a bit that is
already set changes nothing. `adversarial-sat.bin` is a twenty-byte varint of
`0x7f` payloads: the first ten bytes already set all 64 bits, so all ten
undefined shifts are no-ops on the value.

```
== 4. adversarial inputs -- behaviour recorded, not required to agree ==
 -- adversarial-sat.bin: san=fires  -> model expects exit 0, stdout '18446734407611127296'
    c-gcc       exit=0  stdout='18446734407611127296'
    c-clang     exit=0  stdout='18446734407611127296'
    safe_naive  exit=0  stdout='18446734407611127296'
    safe_tuned  exit=0  stdout='18446734407611127296'
    unsafe      exit=0  stdout='18446734407611127296'
    verus       exit=0  stdout='18446734407611127296'
    c-gcc-h     exit=0  stdout='18446734407611127296'
    c-clang-h   exit=0  stdout='18446734407611127296'
```

**Ten undefined shifts execute, UBSan fires, and all eight cells print the same
number.** No choice of fold could repair that. It is stated in `spec.md` as a
property of the bug rather than left for a reviewer to find, and it is why the
fold entries above are justified by what they DO catch.

---

## 3 — `Ir`: the eight cells, and which column is which

`harness/measure.py p18`, kernel-exclusive `Ir` (callgrind per-function
exclusive for the `kernel` symbol), `O3 isolated`, divided by `n_iters`:

| cell | `small` (112 varint bytes, 24 varints) | `large` (41, 10) |
|---|---|---|
| c-gcc (R1) | 1884.00 | 738.00 |
| c-gcc-h (R1h) | 2108.00 | 820.00 |
| c-clang (R1) | 2020.00 | 790.00 |
| c-clang-h (R1h) | 2246.00 | 874.00 |
| safe_naive (R2) | 2681.00 | 1039.00 |
| safe_tuned (R3) | 2293.00 | 876.00 |
| unsafe (R4) | 2318.00 | 888.00 |
| verus (R5) | **2318.00** | **888.00** |

**R4 and R5 are exactly equal in the kernel-exclusive column**, and byte-identical
at `-O3` (`identity: exact`, `md5_fn 8f97546b0bdb`, `n_fn 71` both).

⚠ **The whole-program differenced marginal is NOT the same column, and on p18 it
differs between R4 and R5 by 1.00 Ir/call** (2332.00 vs 2331.00 on `small`).
That 1.00 is **outside the kernel** and the harness's own split proves it:
`main_exclusive_ir` on `small` at `O3 isolated` is 840,275 for `unsafe` and
780,274 for `verus`, a difference of 60,001 over 60,000 calls. R5 reaches
`println!` through the trusted `emit` wrapper where R4 calls `driver::emit`
directly. **Quote the kernel-exclusive column for any R4-vs-R5 claim.**

`work_per_call` is `stride` and it errs **HIGH by exactly the four header
bytes** — see `model.py`'s docstring, which states the direction rather than the
comfortable one. Derived floor 29.00 Ir/call on `small`, cleared at 65.5×
(gate stage 3b, tightest margin over 64 cell/probe pairs).

---

## 4 — the safety line's price, and it is the first one in this project that does not amortise

### 4a — `Ir`, exact, zero free parameters

`controls/sweep_ir.py --band all --cells all` over 34 blobs, fitted by
`controls/fit.py` (exact rational least squares — no numpy on this box):

| cell | per varint byte | per varint | per call | max &#124;residual&#124; |
|---|---|---|---|---|
| c-gcc | 12.0000 | 21.0000 | 51.0000 | 0.029 |
| c-gcc-h | **14.0000** | 21.0000 | 51.0000 | 0.029 |
| c-clang | 12.0000 | 27.0000 | 42.0000 | 0.029 |
| c-clang-h | **14.0000** | 27.0000 | **44.0000** | 0.029 |
| safe_naive | 18.0000 | 26.0000 | 55.0000 | 0.009 |
| safe_tuned | 17.0000 | 15.0000 | 43.0000 | 0.009 |
| unsafe | 16.0000 | 21.0000 | 36.0000 | 0.009 |
| verus | 16.0000 | 21.0000 | 35.0000 | 0.009 |

(The residual is the driver's `println!` digit-count term, not model error.)

> **`c-gcc-h − c-gcc = 2.00 · varint bytes`, exactly, with a ZERO per-varint
> term and a ZERO intercept.**
> **`c-clang-h − c-clang = 2.00 · varint bytes + 2.00`.**

**And BOTH coefficients of the gcc pair are derived from the listing with zero
fitted parameters.** Counting `c-gcc`'s `-O3 isolated` kernel (§1a) block by
block, where `b` is varint bytes and `v` varints:

```
per varint  prologue 0x19b8..0x19ca   movq xorl xorl xorl leaq addq jmp      7
            ...and the first byte's loop test 0x19f1..0x19f4  cmpq jb        2
            epilogue 0x19f6..0x19f1f  movq movq addq shlq subq addq movq
                                      shlq subq addq cmpq je cmpq jb        14
per byte    body     0x19d0..0x19ef   movzbl addq addq movq andl shlq
                                      addl orq testb jns                   10
            ...plus the NEXT byte's loop test, taken on every byte but the
            last of each varint:       cmpq jb                              2

  total = (7 + 2 + 14)·v  +  10·b  +  2·(b − v)  =  12·b + 21·v
```

**`12.00` and `21.00` are exactly the fitted coefficients**, and `c-gcc-h` adds
`cmpl $0x3f,%ecx` + `ja` to the per-byte body and nothing anywhere else, giving
`14·b + 21·v` — again exactly the fit. clang's per-byte pair is
`cmpl $0x40,%ecx` + `cmovaeq`; its per-varint term (27) is **not** derived here
and is reported as fitted only (§12).

**Nothing in either coefficient is executed padding.** `.memory/03-measurement.md`
trap 3's dynamic half has landed inside a published law three times; here the
check is direct. gcc's inner loop contains one `nopl` (at `0x19cc`) and it is
**not on the executed path** — the back-edge is `jb 0x19d0`, which jumps past
it — and clang's `nopw` at `0x1701` is the loop's alignment prologue, entered
once per varint and not per byte. The `pad` column of §1 is 0 for both gcc cells
and 1 for both clang cells, and the padding-excluded static counts (70/72,
73/79) carry the same +2 in the loop.

clang's extra `+2.00` per call is **not** in the loop: `c-clang-h` spills `nv`
to the stack in its prologue (`movq %rcx, -0x8(%rsp)` at `0x16a9`, reloaded at
`0x1763` and `0x177d`) where `c-clang` keeps it in `%rsi` — one extra store, and
one extra prologue branch from the restructured `len < 4` exit. Register
pressure from the guard's extra live constant, priced at 2.00 Ir/call flat and
independent of the input.

### 4b — the amortisation result, and it is the opposite of the project's usual one

Every earlier pattern's C hardening line runs **once per call** (p02, p17) or
**once per record** (p16, p06, p13) or **once per field** (p14). p18's runs
**once per input byte**, so its cost is a **rate** and not a constant:

| pattern | where the hardening line runs | `R1h − R1` per byte as `n → ∞` |
|---|---|---|
| p02, p17 | once per call | → 0 |
| p16, p06, p13, p14 | once per record / field | → 0 per byte |
| **p18** | **once per input byte** | **→ 2.00, exactly** |

That is the first honest counterexample in this project to *"the safety check
amortises away"* **on the C side**. It costs **11.89% (gcc) and 11.19% (clang)** of
`small`'s kernel `Ir`, and **11.11% / 10.63%** of `large`'s — i.e. **the fraction does
not shrink with the input either**, because both the numerator and the
denominator are per-byte terms.

### 4c — and in wall clock, defended by a layout population

`.memory/03-measurement.md`: no `ns` claim without a layout population, and the
statistics to quote are the **median of the cross-pair distribution** and
**`P(A > B)`**, never a range or a dominance count. `controls/clayout.py --lang c`
builds 30 layouts per C cell with a pad object (`asm(".text; .space N")` linked
first), which moves every later `.text` symbol without touching a byte of
`kernel.o`.

```
CONTROL 1 -- kernel machine code invariant modulo pc-rel: True
c-gcc      30 builds  n_fn [72]  md5_fn_norel 58cb57d61395  1 distinct  30 addrs %32=[0,16] %64=[0,16,32,48]
c-gcc-h    30 builds  n_fn [74]  md5_fn_norel e0c489f1164b  1 distinct  30 addrs %32=[0,16] %64=[0,16,32,48]
c-clang    30 builds  n_fn [76]  md5_fn_norel ff293662170d  1 distinct
c-clang-h  30 builds  n_fn [82]  md5_fn_norel e9a2cec81a70  1 distinct
```

`--time --input small --reps 15 --n-iters 60000 --cpu 5`, then `--modes`:

```
  c-gcc-h vs c-gcc
    paired by layout  n= 30  range  -1.15..+19.97   MEDIAN  +7.63%
    all cross pairs   n=900  range  -3.17..+27.76   MEDIAN  +7.14%   P(c-gcc-h>c-gcc) = 0.9756
    loop0 win32:  win32=4 med +6.70% P=0.956 | win32=5 med +8.56% P=1.000
    loop1 jcc32:  jcc32=0 med +5.91% P=0.947 | jcc32=1 med +10.09% P=1.000

  c-clang-h vs c-clang
    paired by layout  n= 30  range  +1.05..+20.14   MEDIAN +11.76%
    all cross pairs   n=900  range  -0.65..+23.29   MEDIAN +12.04%   P(c-clang-h>c-clang) = 0.9978
    loop0 win32:  win32=5 med +11.42% P=0.996 | win32=6 med +12.59% P=1.000
```

**Mode-matched, computed from the listing and not from an address bit, the sign
does not flip in any mode on either compiler.**

**The identical-copy noise floor, same protocol, same statistic** (12 byte-identical
copies per cell, `--floor 12 --reps 25`):

```
  c-gcc      within-cell  n=144 median +0.00%  P(A>B)=0.4583  range  -7.34..+7.92
  c-gcc-h    within-cell  n=144 median +0.00%  P(A>B)=0.4583  range  -4.44..+4.64
  c-clang    within-cell  n=144 median +0.00%  P(A>B)=0.4583  range -10.73..+12.02
  c-clang-h  within-cell  n=144 median +0.00%  P(A>B)=0.4583  range  -3.02..+3.11
  c-gcc-h vs c-gcc      median  +7.04%  P=1.0000   (one layout, 12 copies each)
  c-clang-h vs c-clang  median +13.67%  P=1.0000
```

The null is clean on the statistics that converge (**median +0.00%, P = 0.458**)
and wide on the one that does not (the range, ±3…12%) — which is exactly why
`.memory` retracted the range. The effect reproduces at a single layout.

⚠ **`large`'s `ns` row is much weaker and is quoted with its `P`.** On the
5.2 MB payload the within-cell spread is 48–65% and the same statistic reads
**+4.24%, P = 0.676** (gcc) and **+10.73%, P = 0.829** (clang). Mode-matched it
does not flip sign, but `P = 0.68` is not a result. **`small` is p18's quotable
`ns` row; `large`'s is reported and not leaned on.**

⚠ **`Ir` and `ns` disagree in MAGNITUDE, not in sign, and in opposite directions
on the two compilers**: gcc is +11.89% `Ir` against +7.14% `ns`, clang +11.19%
`Ir` against +12.04% `ns`. Finding 6's shape without its sign flip.

---

## 5 — `O0d`: what it is, what it costs, and the harness change I did NOT make

### 5a — the decision `spec.md` owes: rung, control, or axis

**`O0d` is a REPORTED AXIS measured on CONTROLS, and it is not a cell of the
24-cell matrix.** Precisely:

* the **shipped rungs** are built at `O0d` with `harness/build.py p18 --opt O0d`,
  which the harness already supports (`ALL_OPTS = ["O0", "O0d", "O3"]`,
  `build.py:66`) and which no pattern had ever used. Those builds are reported
  here and appear in **no** `results/*.json` cell and in **no** gate stage;
* the **delete-the-check controls** (§7) are built at `O0`, `O0d`, `O3` and
  `O3d` by `controls/build_controls.sh`;
* every number below is **Rust-vs-Rust**. `build.py:26-28` says *"This is NOT
  semantics-matched to C `-O0`: it inserts integer overflow checks. Never
  compare it to a C column."* **No C comparison is drawn from `O0d` anywhere in
  this pattern.**

### 5b — THE HARNESS CHANGE I DID NOT MAKE, reported instead

`harness/build.py`'s `ALL_OPTS` is `["O0", "O0d", "O3"]`. **There is no
`opt-level=3` + `debug-assertions=on` cell in the harness at all.** That is the
combination a *cost* claim about the safety net would need, because
`.memory/01-ladder.md` forbids a perf claim from an `O0` row and `O0d − O0` is a
difference of two `O0` rows.

**So I built `O3d` under `controls/` with a direct `rustc` invocation at
`build.py`'s own flags rather than widening `ALL_OPTS`, as TASK_051 instructs.**
Adding `"O3d"` to `ALL_OPTS` and one `elif` to `rust_flags()` would be a
four-line change and would make the axis a first-class one; **it is reported and
not made.** Nothing else in `harness/` or `common/` needed touching for p18.

**It was worth building: the `O3d` answer is the one that matters and it is not
the `O0d` answer.** See §5d.

### 5d — AT `-O3` THE SAFETY NET IS FREE, and free for a reason worth stating

`controls/build_controls.sh` builds the three shipped Rust rungs at
`-C opt-level=3 -C debug-assertions=on`; `controls/sweep_ir.py --band all` and
`controls/fit.py` give the laws over the same 34 blobs, max residual 0.009:

| rung | `-O3` (`off`, the measured cell) | `-O3` + `debug-assertions=on` | Δ |
|---|---|---|---|
| safe_naive (R2) | `18·b + 26·v + 55` | `19·b + 26·v + 57` | `+1.00·b + 2.00` |
| **safe_tuned (R3)** | `17·b + 15·v + 43` | `17·b + 15·v + 46` | **`+3.00` FLAT, `0.00` per byte** |
| unsafe (R4) | `16·b + 21·v + 36` | `19·b + 26·v + 57` | `+3.00·b + 5.00·v + 21.00` |

> **On the shipped tuned safe rung, turning on the flag that catches this bug
> costs 3.00 instructions per kernel call and NOTHING per byte — 0.13% of
> `small`'s 2307.00 and 0.34% of `large`'s 890.00.**
>
> **And the mechanism is the reason, not an accident: on a program that HAS the
> guard, the debug-assertion is provably dead.** `if shift < VBITS { … << shift }`
> gives LLVM exactly the fact the inserted `Assert(shift < 64)` needs, so it is
> folded away; likewise `p + 1` under `p < len` and `nb + 1` under `nb < len`.
> The surviving 3.00 per call is the window header's `off + 1`, `off + 2`,
> `off + 3`, which no loop guard bounds. **The check that catches the bug is free
> precisely on the programs that do not have the bug** — and on the program that
> does (`n_noguard`), it cannot be folded away and it panics (§7).

⚠ **Two things this does NOT say.** (i) On R4 the flag costs `+3.00` per byte
and `+5.00` per varint, because `assert_unsafe_precondition!` inside
`get_unchecked` is *not* provably dead — and at `-O3 -C debug-assertions=on`
**R4's fitted law becomes `19·b + 26·v + 57`, character for character
safe_naive's**, from different machine code (122 vs 116 static instructions,
`md5_fn_norel 349d35aa83a5` vs `f7dc9d243528`). **R4's whole advantage over R2
is gone once its `unsafe` is checked**, on every input, exactly. (ii) The
`*_noguard` controls' `O3d` cost is **not** published: it does not fit a linear
law over band b (max residual 10.5…15.7 Ir against 0.009 for every guarded
cell), so whatever the flag costs a program that really can shift out of range
is not a per-byte constant and I did not chase it.

### 5c — the cost, decomposed mnemonic by mnemonic, and only a third of it is the shift

`controls/sweep_ir.py --band all --opt O0d` against `--opt O0`, fitted:

| cell | per byte `O0` | per byte `O0d` | Δ per byte | Δ per varint | Δ per call |
|---|---|---|---|---|---|
| safe_naive | 42.00 | 65.00 | **+23.00** | +6.00 | +64.00 |
| safe_tuned | 41.00 | 60.00 | **+19.00** | +6.00 | +375.00 |
| unsafe | 55.00 | 93.00 | **+38.00** | +6.00 | +120.00 |
| verus | 55.00 | 93.00 | **+38.00** | +6.00 | +120.00 |

**`-C debug-assertions=on` is a BLANKET arithmetic-overflow check, not a shift
check.** In p18's kernel it can act on exactly four things — the `<<`,
`p = p + 1`, `nb = nb + 1` and the index expression `off + p` — because `shift`
steps with `wrapping_add` and the fold is `wrapping_mul`/`wrapping_add`
throughout. That is what `spec.md`'s wrapping-shift-step entry buys, and it is
what makes this axis attributable at all.

**And on the unsafe rung it acts on a FIFTH thing nobody had named**: the
standard library's own `assert_unsafe_precondition!` inside `get_unchecked`,
codegen'd from the *calling* crate's debug-assertions flag:

```
unsafe-O0d, core::slice::index::SliceIndex::get_unchecked:
   1ae89:  callq  <...SliceIndex::get_unchecked::precondition_check>

...precondition_check (executed path, 6 instructions):
   1a9b0:  pushq  %rax
   1a9b1:  movq   %rdx, (%rsp)
   1a9b5:  cmpq   %rsi, %rdi      <-- the bounds check
   1a9b8:  jb     0x1a9d2
   1a9d2:  popq   %rax
   1a9d3:  retq
```

> **`O0d` does not merely add a shift check to R4 — it turns R4's `unsafe` back
> into a CHECKED access.** So the `O0d` column is not "R4 plus a shift check"
> and must not be read as one.

The decomposition, measured with `controls/gen_controls.py`'s `*_wrapall`
controls (`p`, `nb` and `off + p` made wrapping, everything else identical, and
all four print the model's checksum on `small`):

```
$ python3 controls/sweep_ir.py --blobs sweep-b01v08.bin,sweep-b10v08.bin --cells none \
      --bins .temp/p18/ctlbin/{n,u}_wrapall-{O0,O0d}
  n_wrapall-O0   42.0000 Ir/byte      u_wrapall-O0   55.0000 Ir/byte
  n_wrapall-O0d  49.0000 Ir/byte      u_wrapall-O0d  76.0000 Ir/byte
```

| term | safe_naive | unsafe |
|---|---|---|
| the three cursor / index overflow checks | 16.00 | 17.00 |
| **the SHIFT-overflow check** | **7.00** | **7.00** |
| `assert_unsafe_precondition!` in `get_unchecked` | — | 14.00 |
| **total `O0d − O0`** | **23.00** | **38.00** |

and the residual closes exactly: `SliceIndex::get_unchecked` goes from 7 executed
instructions at `O0` to 15 at `O0d`, plus 6 in `precondition_check` — 8 + 6 = 14.

> **Only 7.00 of 23.00 (30%) on the safe rung, and 7.00 of 38.00 (18%) on the
> unsafe one, is the check p18 is about.** A reader told "turning on
> `debug-assertions` costs 38 Ir per byte to catch this bug" would be wrong by
> a factor of five.

⚠ **And 5 of those 7 are not the check either.** From the listing, the `O0d`
shift block adds eight instructions and removes one against `O0`; the check
itself is **`cmpl $0x40, %eax` and `jae`**, and the other five
(`movq %rcx,(%rsp)`, `movq %rax,0x8(%rsp)`, `movl %eax,0x14(%rsp)`,
`movq (%rsp),%rax`, `movq 0x8(%rsp),%rdx`, `movl 0x14(%rsp),%ecx`) are the
spills the extra basic block forces at `-O0`. That is trap 3's lesson in a form
it had not taken before: not executed *padding*, executed *spill code*.

⚠ **An attempted null that FAILED, recorded rather than dropped.** The intended
control was "make the shift `wrapping_shl` too, and `O0d − O0` must then be
zero on the safe rung". It reads **+13.00 Ir/byte**, not zero, for two reasons
found by measuring: `wrapping_shl` also deletes the *guard branch* (so the `O0`
baseline moves), and `wrapping_shl` routes through `unchecked_shl`, which has
its own `assert_unsafe_precondition!` under the same flag. **`wrapping_shl` is
not free of debug-assertions.** The `*_wrapall` decomposition above is the
repair and it closes against the listing instead.

---

## 6 — the trusted base: three items, one `requires`, and it has nothing to do with the bug

Gate stage 5a:

```
verus.rs: TCB items (3):
   verifier::external_body  buf_get_unchecked (1 body lines, line 227, requires=['i < v@.len()'])
   verifier::external_body  load_input        (4 body lines, line 261, requires=[])
   verifier::external_body  emit              (1 body lines, line 273, requires=[])
verus.rs: items the trusted-item rules govern: ['buf_get_unchecked']
verus.rs: 12 verified, 0 errors -- matches the pinned obligation count; 3 TCB items
```

**TCB = 3 items**, equal to the gate's own `tcb_items`, classified per
`.memory/04-verus.md`: **1 U-license** (`buf_get_unchecked`) **+ 2 infra**
(`load_input`, `emit`), **0 V-gap**. That is the smallest trusted base of any
pattern in this project, and for a structural reason rather than by cleverness:
**p18's kernel performs exactly one kind of memory access, a byte read of the
input window**, so there is exactly one accessor to trust. There is no scratch,
no output buffer, no bulk copy and no write of any kind.

### 6a — and the item has NOTHING to do with p18's bug. That is the pattern.

In every earlier pattern the trusted `requires` and R1's missing line are about
the same fact. Here they are about different facts, and two orthogonal mutants
show it (§10):

| mutant | what fires | what does not |
|---|---|---|
| `m_noguard` (safety line deleted) | `possible bit shift underflow/overflow`, **on the operator** | the accessor's `requires` is untouched — 11 verified |
| `m_weakreq` (`i < v@.len()` → `i <= v@.len()`, both copies) | the **twin** fails: `precondition not met: index in bounds` | the shift obligation is untouched — the shipped config reads **12 verified, 0 errors** |

> **A memory-safety-only specification of this kernel is VACUOUSLY TRUE OF R1**,
> because R1 accesses nothing out of bounds. What rejects R1 is Verus's
> *arithmetic definedness* obligation, which is unconditional and is not part of
> the specification at all. p18 is p09's mirror: p09's bug was invisible to the
> proof and visible to nothing; p18's is invisible to the *postcondition* and
> caught by the operator's own obligation.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) **Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. These are the same
operation with and without the language's bounds check: `<[T]>::get_unchecked`
is documented as being equivalent to indexing when `i < v.len()` and undefined
otherwise, and `v[i]` is indexing with the check. So a `requires` too weak to
license the unchecked read is too weak to license the checked one, and Verus can
see the second — which is exactly what the gate measures: weakening the shared
conjunct to `i <= v@.len()` leaves the shipped configuration at **12 verified,
0 errors** and makes the twin fail with `precondition not met: index in bounds
for this access` (`.temp/p18/ctl/m_weakreq.rs`, §10). Nothing about the twin's
body is a re-statement of the trusted one; it is written in a different language
fragment (checked indexing) that the verifier reasons about natively.

(b) **Is the `ensures` COMPLETE with respect to every unchecked operation the
body performs?** The body performs exactly one unchecked operation, a read of
element `i` of `v`, and `ensures r == v@[i as int]` describes exactly that read
and its result. It reads no other index — TASK_009_REVIEW's ×4 attack is a body
that also reads `i + 1`, which would satisfy this same `ensures` and be
invisible to Verus, to the twin and to the contract pin. The defences against it
here are (i) the body is **one line** and is printed in full by the gate every
run, and (ii) **Miri**, which interprets `unsafe.rs` — the byte-identical R4 —
over all nine inputs and reports no UB (gate stage 8, nine `ok` rows). The body
performs no write, no pointer arithmetic, no transmute and no aliasing
operation, so there is no unchecked effect the postcondition could be silent
about beyond the read itself.

(c) **Does each clause mean the same thing in both configurations?** There is
one `requires` conjunct, `i < v@.len()`, and one `ensures` conjunct,
`r == v@[i as int]`. Both are written character for character in the trusted
item and in `slb_twin_buf_get_unchecked`; neither mentions a `const`, a `cfg`, a
type alias or anything else whose meaning could differ between the shipped build
and `--cfg slb_twin`. The gate checks the stronger structural property directly:
*"the token `slb_twin` occurs nowhere but on the 1 twin `#[cfg(slb_twin)]`
attribute, so the shipped configuration and the `--cfg slb_twin` one differ in
nothing but the twin items themselves"*. `v@.len()` is the slice's view length in
both, and `v@[i as int]` its element, both from vstd's `group_slice_axioms`,
which is `broadcast use`d unconditionally.

**One honest limit on all three.** This item is *not* what makes p18 safe. It
excludes an out-of-bounds read; p18's bug is an out-of-range shift, and §6a
measures that weakening this `requires` neither admits nor excludes it. The
argument above is therefore about the soundness of R4's `unsafe`, not about the
pattern's security property — which is carried by the kernel's `ensures` and by
Verus's unconditional arithmetic obligations.

---

## 7 — the delete-the-check rows: safe Rust is C, at the flags this benchmark measures

`controls/gen_controls.py` derives `n_noguard` / `t_noguard` / `u_noguard` from
`safe_naive.rs` / `safe_tuned.rs` / `unsafe.rs` by deleting the four lines of the
safety line and nothing else; `controls/build_controls.sh` builds each at four
Rust `(opt-level × debug-assertions)` combinations. **`n_noguard` contains zero
`unsafe`.**

**On `adversarial-shift11.bin`** (checked rungs print `9722957826816`; C's R1
prints `1758263303383808`):

| control | `O0` | `O0d` | `O3` | `O3d` |
|---|---|---|---|---|
| `n_noguard` (zero `unsafe`) | `1758263303383808` | **panic, rc 101** | `1758263303383808` | **panic, rc 101** |
| `t_noguard` | `1758263303383808` | **panic, rc 101** | `1758263303383808` | **panic, rc 101** |
| `u_noguard` | `1758263303383808` | **panic, rc 101** | `1758263303383808` | **panic, rc 101** |

```
thread 'main' panicked at .temp/p18/ctl/n_noguard.rs:67:25:
attempt to shift left with overflow
```

and on **every** adversarial input, at `-O3 -C debug-assertions=off`:

```
input                      model                  n_noguard              u_noguard              c-gcc
adversarial-many.bin       9953347230944059904    7456158208145138176    7456158208145138176    7456158208145138176
adversarial-sat.bin       18446734407611127296   18446734407611127296   18446734407611127296   18446734407611127296
adversarial-shift11.bin       9722957826816          1758263303383808       1758263303383808       1758263303383808
adversarial-shift20.bin      17654844475008       7680421278058493568    7680421278058493568    7680421278058493568
degenerate.bin           306922972422813440     306922972422813440     306922972422813440     306922972422813440
large.bin              16811552480294075003   16811552480294075003   16811552480294075003   16811552480294075003
small.bin              14238010737147540887   14238010737147540887   14238010737147540887   14238010737147540887
truncating.bin          1336657309244190976    1336657309244190976    1336657309244190976    1336657309244190976
```

> **Safe Rust with the shift bound deleted is BIT-IDENTICAL to C's R1 on every
> adversarial input, at both of the opt levels this benchmark measures.** Not
> "similar": the same 64-bit integer, on four blobs, from a rung with no
> `unsafe` in it. The type system does not see this bug, the bounds checks do
> not see it, and the two columns this project publishes do not see it.
>
> **State it honestly, as `spec.md` and TASK_051 both insist**: this is not
> *"safe Rust does not catch it"*. It is *"the semantics-matched configuration
> this benchmark measures does not, and here is what the configuration that does
> costs"* — §5c, where the cost is 23.00 Ir per byte on the safe rung of which
> **7.00 is the check**.

**Miri catches all three** — and, crucially, catches them on `adversarial-sat`,
the input on which no checksum can:

```
n_noguard  small                    rc=0    17386456959601715103
n_noguard  adversarial-shift11      rc=101  attempt to shift left with overflow
n_noguard  adversarial-sat          rc=101  attempt to shift left with overflow
n_noguard  truncating               rc=0    18446725546715322496
u_noguard  small                    rc=0    17386456959601715103
u_noguard  adversarial-shift11      rc=101  attempt to shift left with overflow
u_noguard  adversarial-sat          rc=101  attempt to shift left with overflow
u_noguard  truncating               rc=0    18446725546715322496
```

⚠ Miri reports a **panic**, not `Undefined Behavior` — so a gate whose Miri stage
keyed on the `ub` flag alone would miss it. `check.py` keys on the exit code as
well and would catch it. §0.2(b).

### 7b — the SECOND bug, and nothing catches this one at all

`truncating.bin`'s varints are **ten** bytes long, so the last shift is 63 — in
range, guard never fires, no undefined behaviour anywhere — and the last byte
carries payload `0x7f`, of which only bit 0 survives a `u64`. **Six bits of the
encoded integer are discarded by the shift itself.**

| catcher | on `truncating.bin` |
|---|---|
| ASan + UBSan, gate flags | **clean, exit 0** (gate stage 7) |
| `-C debug-assertions=on` (`O0d`, `O3d`) | **clean**, same value as `O0`/`O3` |
| Miri | **clean, exit 0**, matches the model |
| all eight matrix cells | **agree with `model.py`** (gate stage 2, 32 cells) |
| R5's proof | **discharges** — `varint_fold` specifies the truncating decode |

**Every rung agrees, every catcher is silent, and the decoded number is not the
number that was written.** It is p17's limit arriving on arithmetic instead of on
a range, it is the catalogue row's *"truncation"* half, and it comes free with
the wire format. `spec.md`'s `ensures` section states the limit explicitly
rather than leaving it to be discovered: a postcondition that could see this bug
would have to specify the *encoder*, which no honest loader has.

---

## 8 — the sweep, and a hold-out that CANNOT FAIL (reported as a failed design goal)

`inputs/gen.py --sweep` emits four bands, 34 blobs, and regenerating twice is
byte-identical (`md5sum` of all 40 `.bin` files: `155a41b5…` twice). The eight
matrix blobs are unchanged by adding `--sweep` (`md5sum -c`, 3 of 3 OK), so the
band cost **one gate re-run and no re-measure**, per `.memory/05-layout.md`.

### 8a — the rank test, and p18 fails the standard TASK_051 set

```
$ python3 controls/fit.py .temp/p18/sweep_all_O3.json
  31 sweep row(s), bands ['b','v','x'], pooled design rank 3 of 3 columns ('bytes','nv','one')
    drop band b: 21 rows left, rank 3   (band b alone: 10 rows, rank 2)   <-- hold-out CANNOT fail
    drop band v: 15 rows left, rank 3   (band v alone: 16 rows, rank 2)   <-- hold-out CANNOT fail
    drop band x: 26 rows left, rank 3   (band x alone:  5 rows, rank 3)   <-- hold-out CANNOT fail
```

**TASK_051 asked for a hold-out that can fail, the way p06's does. p18's cannot,
and the reason is structural rather than an oversight I could design around:**
the model has **three** columns, so any three independent rows determine it, and
band x alone is already rank 3. Its leave-one-band-out residuals (0.008…0.027,
i.e. the `println!` term) are **not evidence** and are not quoted as any. This is
p13's and p14's defect for a third time, found by the test `.memory` added
because of them — and the honest response is not to dress the residual up.

### 8b — what replaces it: a pre-registered EXTRAPOLATION

`.memory/03-measurement.md`: *"an exact fit plus genuine out-of-sample
predictions is honest evidence; the hold-out is not."* Band `y` was added
**after** b/v/x were fitted, its shapes sit outside the **convex hull** of b/v/x
in both regressors (fit set: bytes 4…80, `nv` 1…16; band y: bytes 160…320, `nv`
16…64 — 4× beyond in each), and the predictions were written down and hashed
**before** any band-y blob was measured:

```
$ python3 controls/predict.py register .temp/p18/sweep_all_O3.json -o .temp/p18/predict_y.json
  fit: 31 rows, bands ['b','v','x'], rank 3, bytes [4, 80], nv [1, 16]
  predict y64: bytes=320 nv=64  c-gcc=5235.03 c-gcc-h=5875.03 c-clang=5610.03
               c-clang-h=6252.03 safe_naive=7479.01 safe_tuned=6443.01
               unsafe=6500.01 verus=6499.01
  sha256 ca0bbe26a2a88a641fdee37e62368268c42e400ee4312b92ad485b952b3dff61

$ python3 controls/predict.py score .temp/p18/predict_y.json .temp/p18/sweep_y_O3.json
  prediction file sha256 ca0bbe26a2a88a641fdee37e62368268c42e400ee4312b92ad485b952b3dff61
  y64  c-gcc        5235.03      5235.00     -0.0261
  ...
  worst |error| over 24 predictions: 0.0261 (C cells) / 0.0099 (Rust cells)
```

**24 out-of-hull predictions, all inside the `println!` noise term.** `small`
and `large` are also outside every band (`bytes` 112 and 41 against band b's
`nv = 8`) and are predicted exactly: `c-gcc` 1899.00 vs 1899.00, `safe_naive`
2695.00 vs 2695.00.

⚠ **`small` and `large` ARE inside the fit set's row space** (`fit.py` prints
`True` for both) — because a rank-3 design's row space is all of ℝ³. That is the
same fact as §8a and it is why the *hull* and not the *span* is the criterion
here.

### 8c — the negative control inside band x

`sweep-x08a.bin` and `sweep-x08b.bin` have **identical regressors** (`bytes` 44,
`nv` 8) and different bytes. Predicted delta: exactly 0. Measured:
747.0180 vs 747.0000 (`c-gcc`), 908.0075 vs 908.0000 (`unsafe`) — **0.018 and
0.0075**, the `println!` digit term and nothing else.

### 8d — the two in-contract R3 spellings, both published, cheaper one shipped

`.memory/01-ladder.md` finding 3, which four patterns have got wrong by
publishing a point instead of its class. **Which spelling ships was decided
before either was measured** (`safe_tuned.rs`'s header says so, and
`.memory/02-bench-rules.md`'s *"NEVER re-ship a rung because a cheaper
in-contract spelling was found"* is why the order matters):

| spelling | in contract? | per byte | per varint | per call | `small` | `large` |
|---|---|---|---|---|---|---|
| **shipped R3** — two-step reslice `buf.split_at(off).1.split_at(len).0` | yes | 17 | 15 | 43 | **2307.00** | **890.00** |
| `t_1step` — `&buf[off..off + len]` | **yes** | 17 | 15 | 44 | 2308.00 | 891.00 |
| `t_chain` — the two fold statements chained | **yes** | 17 | 15 | 43 | 2307.00 | 890.00 |
| `t_iter` — `w[p..].iter()` scan | no (does not spell `while p < len`) | 15 | 20 | 46 | 2206.00 | 861.00 |
| `t_pos` — `position(...)` then a second pass | no (`forbidden`) | 17 | 22 | 44 | 2476.00 | 961.00 |

**The shipped spelling is the cheapest of the three in-contract ones**, by
`1.00 Ir/call` flat over `t_1step` (p04's two-step-reslice lever, reproduced on
a fifth pattern) and by `0.00` over `t_chain`. The R3-side in-contract span is
therefore **`0.00 … 1.00` Ir/call, width 1.00**, which is the narrowest any
pattern here has published — and it is narrow because p18's declaration leaves
very little free: with the scan bound, the cursor guard, the mask, the continue
test, the shift step, the guard and all three fold terms pinned, the reslice and
the fold's statement structure are what is left.

⚠ **`t_iter` is OUT of contract and `spec.md`'s prose said otherwise in an early
draft.** The `idiom` block pins `while p < len` for all four Rust rungs and
`t_iter` does not spell it; the block wins, the prose was corrected, and the
number is published here anyway because **the price of a declaration is what the
declaration excludes**: `−2.00·bytes + 5.00·varints + 3.00`, i.e. `t_iter` is
101.00 Ir/call cheaper than shipped R3 on `small` and 29.00 on `large`, and
**dearer** on windows of short varints (`sweep-b01v08`: 326 vs 299).

⚠ **R3 is cheaper than R4 on both matrix inputs** — `−25.00` on `small`,
`−12.00` on `large`, law `R3 − R4 = +1.00·bytes − 6.00·varints + 7.00`, with a
crossover at `bytes/varint ≈ 6` that band b straddles exactly (`b05`: 843 vs
844; `b06`: 979 vs 972). **This is a FIXED-R4 reading and not "safe beats
unsafe"** (`.memory/01-ladder.md` finding 14): p18's R4 side has not been
searched in contract, and the only admissible R4 shown is the shipped cell. The
mechanism is visible in the coefficients: R3 pays `+1.00` per byte for the
reslice's bounds check and saves `6.00` per varint because the reslice's length
is loop-invariant where R4 recomputes `off + p`.

---

## 9 — the priced fiats, and which exclusions the PROVER already makes

`.memory/02-bench-rules.md` / TASK_049: an entry the prover already excludes
costs nothing to keep; an entry only the *declaration* excludes is a fiat and
must be priced. Measured, not asserted (`controls/gen_controls.py` writes the
probes; `verify_controls.sh` runs them):

```
$ ./verus_run.py .temp/p18/ctl/probe_shl_family.rs
error: `core::num::impl&%9::checked_shl` is not supported ...
error: `core::num::impl&%9::overflowing_shl` is not supported ...
$ ./verus_run.py .temp/p18/ctl/probe_shl_unchecked.rs
error: `core::num::impl&%9::unchecked_shl` is not supported ...
$ ./verus_run.py .temp/p18/ctl/probe_shl_bare.rs      # `wrapping_shl` alone
verification results:: 2 verified, 0 errors
```

| `forbidden` entry | prover disposition at the pinned vstd | price |
|---|---|---|
| `checked_shl` | **`is not supported`** — no R4 can use it | free to keep |
| `overflowing_shl` | **`is not supported`** | free to keep |
| `unchecked_shl` | **`is not supported`** | free to keep |
| `wrapping_shl` | **VERIFIES** — an R4 *could* use it | **a fiat: `−2.00·bytes + 1.00·varints − 1.00`**, *within the domain where the guard never fires* |
| `from_le_bytes` | `is not supported` (measured on p05/p16/p06/p14) | free to keep |
| `chunks_exact`, `take_while`, `.position(` | Rust-only fiats | `t_pos` prices the last: `+7.00·varints + 1.00` |

> **⚠ And `wrapping_shl` verifying is not just a price, it is a LIMIT on §0.2(c),
> and it is the sharpest thing p18 has to say about what a proof buys.** Verus's
> arithmetic obligation attaches to the **operator spelling**, not to the
> operation: `x << s` with an unconstrained `s` fails, and
> `x.wrapping_shl(s)` — which computes exactly x86's masked shift, i.e. R1's
> realised answer — **verifies with no obligation at all**. So the claim
> *"Verus catches this bug"* holds for a rung that spells `<<` and does **not**
> hold for a rung that spells `wrapping_shl`. What catches the latter is the
> **functional** `ensures`, and `m_wshl` (§10) demonstrates it.

⚠ **`t_wshl`'s price is quoted WITH ITS DOMAIN, and the domain is why it is a
legitimate comparison at all.** `.memory/02-bench-rules.md` forbids comparing
cost on an input where the unhardened rung commits UB. `t_wshl` is *not*
undefined — that is the whole point of `wrapping_shl` — but it does compute a
different answer once the guard would have fired
(`adversarial-shift11`: `1758263303383808`, C's number, against the shipped R3's
`9722957826816`). **Every blob the `−2.00·bytes` law is fitted on has
`over = 0`** — `controls/sweep_ir.py`'s `shape()` counts oversized shifts per
blob and prints the column, and it reads 0 on all 34 — and `t_wshl` prints the
model's checksum on `small` and `large`. So the law is the cost of the guard on
the benign domain, which is where every deployment lives, and outside it the
row is a **behaviour** row and not a cost row.

⚠ **And `t_cshl` is a CORRECT hardened spelling, not a buggy one**: it prints
`9722957826816` on `adversarial-shift11`, i.e. `checked_shl(shift).unwrap_or(0)`
is semantically the guard. Its cost is `17·b + 15·v + 43` — **byte-for-byte the
shipped R3's law** — so this `forbidden` entry costs the pattern nothing at all
even before the prover's `is not supported` is taken into account. It is
excluded because a rung using it would price `Option` codegen rather than the
branch this pattern is about, and the measurement says there is nothing to
price.

**The C analogue, and it is the control that separates "undefined" from
"wrong".** `c_mask` is `c/kernel.c` with `<< shift` replaced by
`<< (shift & 63)` — well-defined C99 that computes R1's answer on purpose:

| | `small` | `adversarial-shift11` | `adversarial-sat` | law |
|---|---|---|---|---|
| `c-gcc` (R1, undefined) | 1899.00 | 1758263303383808 | 18446734407611127296 | `12·b + 21·v + 51` |
| `c_mask-gcc` (defined) | 1899.00 | 1758263303383808 | 18446734407611127296 | `12·b + 21·v + 51` |

**Identical cost law, identical answer on every blob — and UBSan is completely
silent on `c_mask`:**

```
$ gcc -O1 -g -fsanitize=address,undefined -static-libasan -static-libubsan ... c_mask_kernel.c
$ ./c_mask-asan adversarial-shift11.bin   ->  1758263303383808   rc=0     (no diagnostic)
$ ./c_mask-asan adversarial-sat.bin       ->  18446734407611127296  rc=0  (no diagnostic)
```

> **The only thing separating R1 from `c_mask` is the word "undefined".** Same
> instruction stream cost, same wrong answer, and only one of them gets a
> sanitizer diagnostic. **The sanitizer catches the undefinedness, not the
> wrongness** — which is exactly what §7b's `truncating.bin` says from the other
> direction.

The other two C controls: `c_ncap` (ten-byte cap) is `14·b + 21·v + 51`,
**identical to `c-gcc-h`'s law** while computing a different function;
`c_reject` is `14·b + 22·v + 53`, i.e. `+1.00·varints + 2.00` over truncating —
the measured price of the hardened spelling §0b rejected.

---

## 10 — the proof, and the mutants that fail the gate

**Verus: 12 verified, 0 errors** — on the **second** attempt. The first read
`11 verified, 1 errors`, and the single error is worth recording because it is
the only thing about this proof that was not immediate:

```
error: possible arithmetic underflow/overflow
   --> verus.rs:366:18
366 |             nb = nb + 1;
```

The repair is one invariant clause, `nb < len`, which follows from
`p_before + nb == p <= len` and `p_before >= 4` and which Verus does not derive
on its own. No lemma anywhere in the file, **no `by (bit_vector)` and no
`by (nonlinear_arith)` in the kernel** — the specification is written with the
same `&` / `|` / `<<` the exec code uses, which is the design choice that makes
a bit-twiddling kernel provable in one session.

Obligations, each term measured with `--verify-function <name> --verify-root`:

```
VBITS 1 + vdec 1 + vbytes 1 + vwalk 1 + kernel 3 + main 5 = 12
u32_at 0, nv_at 0, varint_fold 0 (non-recursive spec fns)
buf_get_unchecked 0, load_input 0, emit 0 (external_body)
--cfg slb_twin: 13 = 12 + 1 (one trusted accessor twin)
```

`kernel`'s 3 = body + two loop bodies. `main`'s 5 is quoted **as measured** and
does not decompose — the same off-by-one p03, p05, p06, p07, p11, p12, p14 and
p17 record for the identical driver.

### 10a — two proof mutants that fail the gate, and they fail on ORTHOGONAL grounds

Generated by `controls/gen_controls.py` by exact-string substitution on
`verus.rs`, with the hit count asserted; they live in `.temp/p18/ctl/` because
`.memory/05-layout.md` item 11 forbids a non-verifying `verus!` file in the
pattern dir.

| mutant | shipped config | `--cfg slb_twin` | which gate stage fails |
|---|---|---|---|
| `m_noguard` — the safety line deleted | **11 verified, 1 errors**: `possible bit shift underflow/overflow` at `val = val \| (((c & 0x7f) as u64) << shift);` | — | **5a** (`n_err > 0`) |
| `m_weakreq` — `i < v@.len()` → `i <= v@.len()`, **both** the trusted item's copy and the twin's | **12 verified, 0 errors** — invisible | **12 verified, 1 errors**: `precondition not met: index in bounds for this access` at `v[i]` | **5c-twin** |

`m_weakreq` weakens **both** copies deliberately: weakening only the trusted
one never reaches the twin (which carries its own contract text in source) and
is caught earlier and more cheaply by `spec.md`'s `items` pin at stage 5a. The
attack the twin regime exists for is the author who weakens both in one commit,
and that is the mutant.

### 10b — two more mutants, and the one that decides the headline

| mutant | result |
|---|---|
| `m_noguard_ms` — safety line deleted **AND** the kernel's `ensures` weakened to `true` (and the call-site `assert` removed) | **11 verified, 1 errors — still `possible bit shift underflow/overflow`** |
| `m_wshl` — the guard replaced by `wrapping_shl`, functional `ensures` kept | **11 verified, 1 errors** — the *inner loop's* functional invariant `vdec(...) == val` fails at the loop exit |

> **`m_noguard_ms` is the one that decides p18's headline.** Weakening the
> postcondition to `true` does **not** rescue the mutant: the shift obligation is
> **intrinsic to the operator**, not derived from the specification. So a
> memory-safety-only proof of this kernel — one that says nothing about the
> answer — still rejects R1's bug. That is the mirror of p09, where a
> memory-safety-only proof discharged the bug clean, and it is why §6a says the
> obligation sits outside the specification rather than inside it.

⚠ **`m_wshl_ms` is NOT a memory-safety-only configuration and its number is
withdrawn as such.** Weakening the kernel's `ensures` leaves both loops'
*functional invariants* in place, so what fails is still a functional
obligation. That is p17's control-2 and p06's `_msonly` lesson for a third time:
**the separation needs a PROGRAM change, not a SPEC change.** The clean version
of the question is answered by `probe_shl_bare.rs` and `probe_shl_family.rs`
instead (§9): `<<` carries an unconditional obligation, `wrapping_shl` carries
none.

---

## 11 — the R4/R5 wall-clock pair is a null, and on p18 it is a weaker smoke alarm than on p06/p14

`controls/clayout.py --lang rust`, 24 layouts per cell
(`-align-all-functions` 0…8 + shipped + 14 symbol orderings):

```
CONTROL 1 -- kernel machine code invariant modulo pc-rel: True
           -- verus's kernel bytes == unsafe's: True
  unsafe  24 builds  n_fn [71]  md5_fn_norel 69b770b44102  21 distinct addrs
  verus   24 builds  n_fn [71]  md5_fn_norel 69b770b44102  21 distinct addrs

  verus vs unsafe
    paired by layout  n= 24  range  -6.76.. +7.49   MEDIAN  +1.29%
    all cross pairs   n=576  range  -7.28..+11.80   MEDIAN  +1.16%   P(verus>unsafe) = 0.6181
    loop0 win32:  win32=4 med -0.15% P=0.488 | win32=5 med +1.71% P=0.867
```

**The sign flips between modes, so it is not a sign** — `.memory/03-measurement.md`'s
own rule. Median +1.16%, `P = 0.618`: a null, confirming the smoke-alarm finding
on a third pattern.

⚠ **New: p18's shipped pair does NOT reproduce the fixed `0x20` offset p06 and
p14 both have.** Both shipped kernels land at **the same address**:

```
unsafe   addr=0x15640  %32=0 %64=0  n_fn=71  md5_fn_norel=69b770b44102
verus    addr=0x15640  %32=0 %64=0  n_fn=71  md5_fn_norel=69b770b44102
```

so the pair samples the *same* alignment class and cannot detect an alignment
contrast at all — it reads `−0.39%`, a pure timing draw. `.memory` says the
verus build's kernel lands "0x20 below the unsafe build's — the same two
addresses on p06 and p14 alike"; **on p18 the offset is 0**, so that is a
property of those two patterns' symbol sets and not a universal one.

**p18 publishes no `ns` figure for any safe-Rust cell**, because no layout
population exists for `safe_naive` / `safe_tuned` here. The only `ns` claims
p18 makes are §4c's C-vs-C hardening figures, which have one.

---

## 12 — what p18 does NOT establish

* **No `ns` claim for R2 or R3.** No layout population was built for the safe
  cells; the `spread_pct` in `results/p18-varint-shift.json` is a whole-process
  level, never a difference (`.memory/03-measurement.md`).
* **No cycles/byte.** `scaling_cur_freq` is unusable on this box and the
  dependent-chain probe is not reproducible across sessions
  (`.memory/00-environment.md`). `ns` is a measurement here; cycles is an
  inference.
* **clang's per-varint coefficient (27.00) and every intercept are FITTED, not
  derived.** Only gcc's `12·b + 21·v` and its hardened `+2·b` are read off the
  listing block by block (§4a). The clang cells' laws are exact over 34 blobs
  and predict band y to 0.026, but their per-varint term has not been counted
  out of the disassembly and is not claimed to be.
* **No branch-miss decomposition** of §4c's gcc-vs-clang divergence
  (`perf_event_paranoid = 3`). The hypothesis that gcc's branch is
  well-predicted on benign input while clang's `cmov` is unconditional work is
  **untested** and is marked as a hypothesis, not reported as a finding.
* **The R4 side has not been searched in contract**, so §8d's `R3 − R4` is a
  fixed-R4 reading and p18 publishes **no pair interval** (`spec.md`'s `why`).
* **`O0d`'s decomposition (§5c) is an `O0`-vs-`O0` reading and no perf claim
  rests on it.** It is there because it is the axis TASK_051 asked about and
  because it is the only place the `precondition_check` mechanism is visible in
  isolation. **The deployable number is §5d's, which is a `-O3`-vs-`-O3`
  reading.**
* **No `O3d` law for a cell that can actually fail.** The `*_noguard` controls
  at `O3d` do not fit a linear law over band b and their cost is not published
  (§5d).
* **`spec.md`'s prose said `t_iter` was "the second in-contract R3 spelling"**
  in the draft that was written before the controls were built; the `idiom`
  block always said otherwise and the block wins. Corrected in `safe_tuned.rs`'s
  header and in §8d, and recorded here rather than quietly fixed.
