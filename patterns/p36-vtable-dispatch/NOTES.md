# p36 — function-pointer table dispatch: findings

Built at TASK_072. Read `spec.md` first; this file records what was measured, in
the order it was measured. Every `Ir` figure is **kernel-exclusive `Ir` per call
at `-O3`, `isolated` inline mode**, unless it says otherwise —
`.memory/03-measurement.md`'s INLINE-MODE rule, and p36 quotes `isolated`
everywhere because that is the mode in which the kernel is its own symbol.

---

## 0. §0 — the four decisions, settled before any rung existed

`.tasks/TASK_072.md` gave this pattern four questions with the authority to stop
it. All four were answered by measurement before a line of `c/kernel.c` was
written, and one of them **changed the pattern**.

### 0a. Can Verus call a function pointer loaded from an array? **NO.**

This was the task's own least-certain call and it decides whether p36 has an R5
at all. The probe is `.temp/p36/probe_a1.rs`, twenty lines, run before anything
else:

```
$ ./verus_run.py .temp/p36/probe_a1.rs
error: The verifier does not yet support the following Rust feature: function pointer types
  --> probe_a1.rs:20:1
   |
20 | const TABLE: [fn(u64) -> u64; 2] = [op_inc, op_dbl];
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
error: The verifier does not yet support the following Rust feature: function pointer types
  --> probe_a1.rs:25:13
   |
25 |     let f = TABLE[op];
   |             ^^^^^
error: aborting due to 2 previous errors
```

**The error is on the DECLARATION**, not on the call. `spec.md`'s `identity` pin
makes that fatal for the rung: an R4 is a program that must have a verifying R5
twin (`.memory/01-ladder.md` finding 14), so a bare `fn`-pointer table is not an
admissible rung.

⚠ **But that is outcome (iii) for the SPELLING, not for the PATTERN**, and the
task's instruction to stop was conditioned on there being no route at all.
**Fourteen probes**, all under `.temp/p36/probe_a*.rs`, all run — count them
with `ls .temp/p36/probe_a*.rs | wc -l`:

| probe | shape | result |
|---|---|---|
| a1 | `const [fn(u64) -> u64; 2]` | `does not yet support ... function pointer types` |
| a2 | `&[&dyn Fn(u64) -> u64]` | `does not yet support ... dyn with more that one trait` — `Fn` has supertraits |
| a3 | `&[&dyn Op]`, hand-rolled single trait | **4 verified, 0 errors** |
| a4 | local `[&dyn Op; 2]` + functional postcondition `op_spec(i, x)` | **4 verified, 0 errors** |
| a4_mut | a4 with `op_spec` mutated | `postcondition not satisfied` — **not vacuous** |
| a5 | `pub static TABLE: [&dyn Op; 2]` | `only spec functions can be marked open/closed` (Verus's parser) |
| a5b | `static TABLE: [&dyn Op; 2]` | rustc `E0277`: `(dyn Op + 'static) cannot be shared between threads safely` |
| a5d | `static TABLE: [&(dyn Op + Sync); 2]` | `does not yet support ... dyn with more that one trait` |
| **a5c** | **`const TABLE: [&'static dyn Op; 2]`** | **5 verified, 0 errors** |
| a6 | bare `fn` table behind `#[verifier::external_body]` | verifies, **and the unguarded call site fails `precondition not satisfied`** |
| a7 | the whole R5 shape end to end | only *proof* errors (my invariants), **no `is not supported`** |
| **a8** | `tab_get_unchecked(i) -> &'static dyn Op` with `ensures r == TABLE@[i as int]`, then `f.apply(x)` proving `op_spec(i, x)` | **8 verified, 0 errors** |
| a8_mut | a8 with `op_spec` mutated at `i == 2` | `postcondition not satisfied` — **not vacuous** |
| a9 | a8 with one `impl<const K: u8> Op for OpTag<K>` instead of eight impls | **5 verified, 0 errors** |

**Three conclusions, and the middle one is why p36 exists.**

1. **A `const` array of trait objects works; a `static` one does not**, and it
   fails for two *independent* reasons that stack — rustc requires `Sync` for a
   `static`, and adding it makes the type `dyn Op + Sync`, which Verus rejects.
   C's table is a `static`; the Rust rungs' is a `const`.
2. **Verus keeps the DYNAMIC TYPE of each slot** through the `const` array
   literal *and* through an `external_body` accessor whose `ensures` is
   `r == TABLE@[i as int]`, so a *functional* postcondition — which a checksum
   needs — is provable. Mutation-tested twice (a4_mut, a8_mut), so it is not
   vacuous.
3. **The bare-`fn` route survives only by putting the whole dispatch inside a
   trusted item** (a6). It works, and it is not vacuous either — the guarded
   call site verifies and the unguarded one reports `precondition not
   satisfied`. But its `ensures` would axiomatise all eight function bodies. It
   is not shipped; §8c.

**The decision, and its authority: p36 IS BUILT, with the R2..R5 dispatch
mechanism changed from a function-pointer table to a single-trait object.** That
is the one place a p36 rung does not spell C's mechanism, it is disclosed in
`spec.md`'s `idiom.why` and in all four Rust rungs' module docs, and §8a prices
it at **exactly 3.00000 Ir per dispatch**.

### 0b. What fires, and on what? **The load. Never the call — except under CFI.**

The gate's stage 7 builds `gcc -O1 -fsanitize=address,undefined
-static-libasan -static-libubsan`. On the shipped `c/kernel.c` it fires on both
out-of-table rows, and this is the gate's own output:

```
ok  adversarial-oob.bin     sanitizer fired as declared (exit=1):
    .../c/kernel.c:89:20: runtime error: index 8 out of bounds for type '<unknown> *[
ok  adversarial-oobmax.bin  sanitizer fired as declared (exit=1):
    .../c/kernel.c:89:20: runtime error: index 255 out of bounds for type '<unknown>
```

and on the minimal probe (`.temp/p36/probe_c.c`, `run_c_probe.sh`) the whole
report is visible:

```
--- gcc asan+ubsan op=8 ---   rc=1
probe_c.c:37:17: runtime error: index 8 out of bounds for type '<unknown> *[8]'
probe_c.c:37:17: runtime error: load of address 0x561d9ca94aa0 with insufficient
                 space for an object of type '<unknown> *'
=================================================================
==3544901==ERROR: AddressSanitizer: global-buffer-overflow on address 0x561d9ca94aa0
READ of size 8 at 0x561d9ca94aa0 thread T0
    #0 0x561d9ca558d3 in dispatch .temp/p36/probe_c.c:37
0x561d9ca94aa0 is located 0 bytes after global variable 'TABLE' ... of size 64
```

**Every diagnostic names the ARRAY READ.** `index 8 out of bounds`,
`insufficient space for an object`, `global-buffer-overflow ... 0 bytes after
global variable 'TABLE'`, `READ of size 8`. Not one of them mentions a control
transfer. **The gate's catcher set detects a DATA bug standing in for a
CONTROL-FLOW bug**, which is the opposite of what the catalogue's *"every harm
here is data"* row implies for this axis.

⚠ **`-fsanitize=function`, UNVERIFIED on this box since TASK_066, is settled,
and both halves of the answer matter.**

```
$ /usr/bin/gcc -std=c99 -O1 -fsanitize=function .temp/p36/probe_c.c -o x
gcc: error: unrecognized argument to '-fsanitize=' option: 'function'
$ ~/tools/llvm/bin/clang -std=c99 -O1 -fsanitize=function .temp/p36/probe_c.c -o x
$                                                     # accepted, builds, runs
```

**gcc 13.3.0 does not implement it at all; clang 22.1.6 does.** The gate builds
stage 7 with gcc, so it is unreachable without a `check.py` change, and it is
clang-only, so it is a `controls/` measurement and not a matrix change.

**It works** — the positive control `.temp/p36/probe_fnsan.c` calls a real
`void(void)` through a `uint64_t(*)(uint64_t)`:

```
probe_fnsan.c:26:42: runtime error: call to function (unknown) through pointer
  to incorrect function type 'unsigned long (*)(unsigned long)'
```

**But it does NOT fire on p36's bug** (`controls/cfi_probe.py`), and the
mechanism is exact:

```
=== clang-fnsan: clang + -fsanitize=function
    adversarial-oob.bin     rc=1  UndefinedBehaviorSanitizer:DEADLYSIGNAL |
        ERROR: UndefinedBehaviorSanitizer: SEGV on unknown address 0xfffffffffffffff9
    adversarial-oobmax.bin  rc=1  ... SEGV on unknown address 0xfffffffffffffff8
```

`0xfffffffffffffff9` is `target - 7`: the check reads a type-signature word
placed *before* the callee's entry, and the loaded garbage is not a function, so
the signature read faults before the check can compare anything.

⚠ **ONE THING ON THIS BOX DOES NAME THE CALL, AND IT IS `-fsanitize=cfi-icall`.**
`controls/cfi_probe.py` builds it and it is the pattern's cleanest single line
of evidence:

```
=== clang-cfi: -O1 -g -flto -fuse-ld=lld -fvisibility=hidden -fsanitize=cfi-icall
    small.bin               rc=0  out=195445626134389610
    adversarial-oob.bin     rc=0  out=8585011895663472192
        .../c/kernel.c:89:15: runtime error: control flow integrity check for
        type 'unsigned long (unsigned long)' failed during indirect function call
    adversarial-oobmax.bin  rc=1  (same diagnostic)
```

Note the second line: under `-fsanitize-recover` the program **does not
crash** — CFI *prevented* the transfer and the run continued to a (wrong)
answer. That is what a mitigation looks like as opposed to a detector.

⚠ **Two independent reasons it cannot be a rung, and both are measured, not
argued.** (1) `-flto` + `-fsanitize=cfi-icall` is a `harness/build.py` flag
change, and `build.py` is hashed into the MEASUREMENT records, so one flag costs
a full re-measure of every pattern in the tree (RECAP, settled answer 4); CFI is
also a *whole-program* property, which an `isolated` build cannot express at
all. (2) It does not even LINK with the default driver on this box —

```
/usr/bin/ld: .../lib/LLVMgold.so: error loading plugin: ... cannot open shared
object file: No such file or directory
```

— because LLVM 22.1.6 no longer ships the gold plugin; `-fuse-ld=lld` is
required, which is a third build-system change. **p36 prices the source-level
range test and reports CFI as a control with its number** (§8d), and claims
nothing about what CFI would cost inside the matrix.

`valgrind --tool=memcheck` cannot start on a dynamic binary here
(`must-be-redirected ... memcmp in ld-linux-x86-64.so.2`, wants `libc6-dbg`,
which needs root) — already in `.memory/00-environment.md`, reconfirmed.

### 0c. Is the harm real and reproducible without a sanitizer? **Yes: 24/24 SIGSEGV.**

`.temp/p36/run_c_probe.sh`, two compilers × four optimisation levels × three
out-of-table opcodes:

```
gcc    O0  op=3    exit0     13573471050264795 1
gcc    O0  op=8    SIGSEGV
gcc    O0  op=40   SIGSEGV
gcc    O0  op=200  SIGSEGV
... identical for gcc O1/O2/O3 and clang O0/O1/O2/O3 ...
clang  O3  op=200  SIGSEGV
```

**24 of 24 out-of-table runs SIGSEGV; 8 of 8 in-table runs exit 0 with the same
answer.** The shipped kernel behaves the same way — the gate's stage 4 records
`exit=-11` for `c-gcc` and `c-clang` on both out-of-table rows, in all four
(opt × mode) cells each, and `exit=0` with the model's checksum for the other
six rungs.

The catalogue's *"p36 is likeliest to hit p55's wall — the harm is not
reproducible"* is therefore **refuted for the measured matrix**, and this is
another catalogue feasibility guess overturned by the §0 that was asked to check
it.

⚠ **It is NOT refuted across builds, and that is the honest caveat.** Under
`-fsanitize=address,undefined` the redzones change what sits after `TABLE`:

```
--- gcc asan+ubsan op=40 ---  rc=0
probe_c.c:37:17: runtime error: index 40 out of bounds for type '<unknown> *[8]'
140734419419416 1              <-- returned normally, WRONG ANSWER, exit 0
```

So the sanitized binary can *survive* an out-of-table call the measured binary
dies on. `model.py`'s `sanitizer_expect` therefore declares **"fires"** — *a
sanitizer reports, deterministically* — which is exactly the bar the TASK_066
re-triage derived from `check.py`'s `expect == "fires"` branch, and never *"the
harm is identical"*.

⚠ **The degenerate outcome the task warned about does not occur.** `NOPS` is a
power of two and the opcode is a byte, but neither compiler folds the index at
any level: there is no mask in the source and none appears in the object code.
The adversarial rows are distinguishable from the perf rows on every cell.

### 0d. Is the indirect call new? **YES — 0 of 534, counted.**

`.temp/p36/sweep_indirect.py` disassembles the kernel symbol of **every already
built cell of every other pattern** through `harness/asm.py` and classifies
every indirect transfer:

```
kernels disassembled                      : 534
binaries with no kernel symbol (skipped)  : 159
reg    :    32 insns in  10 cells, patterns ['p08', 'p27']
jmpr   :     0 insns in   0 cells, patterns []
got    :  1297 insns in 167 cells, patterns [all 21]
jmpgot :     0 insns in   0 cells, patterns []
```

⚠ **The 32 `reg` hits are NOT computed dispatches**, and checking that is the
whole point of the second pass (`.temp/p36/sweep_reg_detail.py`): every one is a
GOT slot materialised into a register one or two instructions earlier, i.e. an
ordinary call to a single dynamic symbol.

```
p08/unsafe-O0-isolated @17409 call *%rax <- ('GOT', 'mov 0x4374f(%rip),%rax  # <memmove@GLIBC_2.2.5>')
p27/unsafe-O3-isolated @158b1 call *%r12 <- ('GOT', 'mov 0x4139a(%rip),%r12  # <_DYNAMIC+0x240>')
...
call *%reg from a GOT slot (one fixed symbol) : 32
call *%reg genuinely computed                : 0
```

**0 computed-target calls and 0 register-target jumps in 534 kernels across 21
patterns.** p36 is the first — and, because `r_match` lowers to `jmp *%r12`
(§6b), even a *jump table* would be new here.

⚠ **The task file asserted this as fact (*"No pattern has an indirect call at
all"*) and asked for it to be verified. It is right about computed calls and
WRONG as literally written**: 1297 `call *0x..(%rip)` instructions exist in 167
kernel cells across all 21 patterns. The distinction between "an indirect call"
and "a computed-target call" is the whole of it, and a sweep that did not draw
it would have reported p36's novelty as false.

---

## 1. The kernel, and what each rung compiles to

All eight rungs agree with `model.py` on every non-adversarial input; the two
out-of-table rows are where they part. The dispatch, from
`harness/asm.py show --raw` on the `-O3 isolated` cells:

| cell | the dispatch |
|---|---|
| `c-gcc` / `c-clang` | `call *0x0(%r13,%rax,8)` — one scaled load, straight into the call |
| `safe_naive` / `safe_tuned` / `unsafe` / `verus` | `shl $0x4,%ecx` ; `lea 0x…(%rip),%rT` ; `mov 0x8(%rcx,%rT,1),%rcx` ; `call *0x18(%rcx)` — `%rT` is whichever register the allocator picked (`%rsi` in `safe_naive`, `%r12` in `unsafe`) |

C reaches its target with **one** instruction; the Rust trait-object table needs
**three** (index × 16, materialise `&TABLE`, load the vtable pointer out of the
fat pointer) plus a second dependent load inside the `call`. §8a prices exactly
that at 3.00000 Ir per dispatch.

⚠ **The `lea` that materialises `&TABLE` is INSIDE the loop, not hoisted**, in all four Rust
rungs, and it is also the one instruction that makes R4 and R5 not
byte-identical (§5).

---

## 2. Miri

Gate stage 8, on `unsafe.rs`, `n_iters` clamped to 4, all seven inputs:

```
ok   miri unsafe.rs on adversarial-nrecbig.bin   n_iters=4: no UB, exit 0 and stdout ... match the model
ok   miri unsafe.rs on adversarial-oob.bin       n_iters=4: no UB, exit 0 and stdout ... match the model
ok   miri unsafe.rs on adversarial-oobmax.bin    n_iters=4: no UB, exit 0 and stdout ... match the model
ok   miri unsafe.rs on adversarial-stride5.bin   n_iters=4: no UB, exit 0 and stdout '0' both match the model
ok   miri unsafe.rs on degenerate.bin            n_iters=4: no UB, exit 0 and stdout ... match the model
ok   miri unsafe.rs on large.bin                 n_iters=4: no UB, exit 0 and stdout ... match the model
ok   miri unsafe.rs on small.bin                 n_iters=4: no UB, exit 0 and stdout ... match the model
```

**Silence on every input, including both out-of-table rows, and that is
correct**: the Rust rungs write `op < NOPS` by hand, so they never dispatch out
of table and have no UB for an interpreter to find. It is §0b's statement made
from inside the language. No row is blocked; p36's verdict is `PASS`, not
`PASS-WITH-BLOCKED-ROWS`.

---

## 3. The `Ir` floor

`model.py` declares `work_per_call = stride` (window bytes) and no
`min_ir_per_work`, so the harness default of 0.25 Ir/byte applies. Measured, the
kernel executes 13 Ir per 2-byte record ≈ 6.5 Ir/byte at R4, so the margin is
about 26×. The gate prints the per-cell margins; none is near the floor.

---

## 4. The laws — exact integers, zero residual, out-of-sample confirmed

`controls/sweep_ir.py --band n`, twelve blobs, `nrw` (records actually walked
per window) from 8 to 512, six windows each, `-O3 isolated`. **Every rung is
exactly linear in `nrw` with an integer slope and zero residual over all twelve
points**, and each law is then confirmed **out of sample** on `small.bin`
(`nrw = 128`) and on `large.bin` (`nrw = 1024`, twice the band's top):

| cell | law, Ir per call | `small` predicted / measured | `large` predicted / measured |
|---|---|---|---|
| `c-gcc` R1 | `10.00000·nrw + 39` | 1319 / **1319** | 10279 / **10279** |
| `c-gcc-h` R1h | `12.00000·nrw + 38` | 1574 / **1574** | 12326 / **12326** |
| `c-clang` R1 | `11.00000·nrw + 31` | 1439 / **1439** | 11295 / **11295** |
| `c-clang-h` R1h | `15.00000·nrw + 31` | 1951 / **1951** | 15391 / **15391** |
| `safe_naive` R2 | `27.00000·nrw + 42` | 3498 / **3498** | 27690 / **27690** |
| `safe_tuned` R3 | `13.00000·nrw + 46` | 1710 / **1710** | 13358 / **13358** |
| `unsafe` R4 | `13.00000·nrw + 31` | 1695 / **1695** | 13343 / **13343** |
| `verus` R5 | `13.00000·nrw + 31` | 1695 / **1695** | 13343 / **13343** |

⚠ **Domain and residue class**, per `.memory/03-measurement.md` after p38's
additivity miss. Domain: `nrw ∈ [8, 512]` in band, extended to 1024 out of
sample; one window shape (`stride = 4 + 2·nrw`, six windows); every opcode in
table; `-O3`, `isolated`. Band n's `nrw` values are
`{8, 18, 32, 46, 61, 96, 128, 151, 192, 257, 384, 512}`, which span residues
**{0, 1, 2, 5, 6, 7} mod 8** and **{0, 1, 2} mod 3** — `inputs/gen.py` prints
both on every row, so a class-dependent fit would be visible before it was
published. What is NOT in the domain: any window with an out-of-table opcode
(the sentinel arm has a different instruction count), `-O0`, and `whole` mode.

**The three differences that follow, and each is a matched pair.**

| difference | law | small | large |
|---|---|---|---|
| **`R3 − R4`, the safety column** | **`15`, flat** | +15 | +15 |
| `R2 − R4`, the naive spelling | `14.00000·nrw + 11` | +1803 | +13995 |
| `R1h − R1`, gcc's source check | `2.00000·nrw − 1` | +255 | +2047 |
| `R1h − R1`, clang's source check | `4.00000·nrw + 0` | +512 | +4096 |

**`R3 − R4 = 15.00 Ir per CALL and 0.00000 Ir per RECORD.** The bounds checks
are entirely outside the loop.** The mechanism is in the listing rather than
inferred: R3 reslices once (`&buf[off+4 .. off+4+2·nw]`), and its loop body is

```
movzbl (%r14,%r12,2),%edx      ; arg
shl    $0x4,%ecx               ; op*16
mov    0x8(%rcx,%r15,1),%rcx   ; vtable
xor    %rdx,%rax
mov    $0x1,%edi
mov    %rax,%rsi
call   *0x18(%rcx)
inc    %r12
cmp    %r12,%rbx
je     ...
movzbl -0x1(%r14,%r12,2),%ecx  ; next op
cmp    $0x8,%rcx
jb     ...
```

— **no `cmp`/`jae` against a length anywhere in it.** LLVM proves
`2t + 1 < 2·nw` from `t < nw` and `rec.len() == 2·nw`, so both per-record checks
are eliminated. That is p16's and p17's result (a per-call constant, zero per
element) reproduced on a kernel with an *indirect call* in the loop, which is a
shape neither of them had. **Fifth pattern in a row where R3 is the honest
number.**

⚠ **R2's `27.00000` is more than twice R4's `13.00000`, and none of the
difference is dispatch.** R2 indexes the whole blob (`buf[off + p]`) and keeps
the per-record cursor test; it carries **6** panic call sites in its kernel
against R3's **5** and R4's **0**.

---

## 5. ⚠ A `spec fn` DECLARED IN A TRAIT OCCUPIES A VTABLE SLOT — a new Verus fact

**This is the first thing in this project that would have made a proof move the
object code, and the `identity` pin caught it.**

`trait Op` has two items: the exec `apply` and the ghost `spec_apply`. The
control is `controls/gen_controls.py --verus`'s `v_specfirst`, which is the
shipped `verus.rs` with those two declarations swapped and nothing else:

```
$ ./verus_run.py --compile .temp/p36/controls/v_specfirst.rs ... -C opt-level=3
verification results:: 12 verified, 0 errors
shipped R4  n_fn 55 bytes 170 md5_fn_norel d2cea805e5489d2f7f6e5d32fcd0e9cb
spec-first  n_fn 55 bytes 170 md5_fn_norel 2155d3100b80f5f2003e1895dfa864fd
md5_fn_norel equal: False
  R4:         call   *0x18(%rcx)
  spec-first: call   *0x20(%rcx)
```

**Same 55 instructions, same 170 bytes, same normalised text, the same
`12 verified, 0 errors` — and not equal even under `md5_fn_norel`.** Verus's
erasure leaves a vtable slot where the ghost method was, in declaration order,
so `apply` moves from slot 0 to slot 1 and the load offset moves 0x18 → 0x20.

Swapping the two declarations is the entire fix. `verus.rs` therefore declares
`apply` first and says so at the site. (The finding was first hit on the
eight-`impl` version of this file, at `19 verified, 0 errors` —
`.temp/p36/v_reorder.rs` — and it reproduces unchanged on the shipped
const-generic one, which is the run quoted above.)

**What survives and what does not.** `.memory/01-ladder.md` finding 1 — *a Verus
proof costs exactly zero instructions* — **survives**: 55 = 55 instructions,
170 = 170 bytes, in both orders. What is new is that a ghost *declaration* can
move a *byte* of the object code, through a vtable slot, and that the mechanism
is trait-item ORDER.

### 5a. ⚠ p36's O3 identity level is `norel`, not `exact`, and that is a disclosure

**All 22 `unsafe vs verus` identity pins in this tree read `O0: norel`, and 21
of the 22 read `O3: exact`. p36 is the one that does not** — counted across
`patterns/*/spec.md`, not asserted. The gate records why:

```
{"pair": "unsafe vs verus", "opt": "O3", "level": "norel", "expected": "norel",
 "counts_a": [55, 54, 170], "counts_b": [55, 54, 170], ...}
```

Same instruction count, same non-padding count, same byte count. **Exactly one
instruction of the fifty-five differs:**

```
A  lea    0x3f6af(%rip),%r12
B  lea    0x3f70f(%rip),%r12
```

— the pc-relative address of `TABLE`. **p36 is the first pattern here whose
kernel references a global object at all**, and the displacement to it depends
on where the linker put a `const` in each binary, which is the
source-path/crate-name layout artefact RECAP's settled answer 1 already names.
`md5_fn_norel` is **equal**, so every byte that is not a pc-relative
displacement is identical. `exact` is unavailable for a reason that has nothing
to do with the proof, and `norel` is the level that says so precisely.

---

## 6. What the op set buys, measured

All eight ops are one 64-bit constant and one arithmetic operation. That is
checked rather than asserted, from `nm --print-size` on the shipped `-O3`
binaries:

```
$ nm --print-size --defined-only .temp/p36/bin/k_gcc | grep ' t op'
0000000000001950 0000000000000012 t op0      <- 0x12 = 18 bytes
...  op1 .. op7, every one 0000000000000012 ...

$ nm --print-size --defined-only .temp/p36/bin/k_unsafe | grep OpTag
0000000000015a60 000000000000000e t _RNvX…INtB2_5OpTagKh0_ENtB2_2Op5applyB2_  <- 0x0e = 14 bytes
...  Kh1_ .. Kh7_, every one 000000000000000e ...
```

**Eight distinct code addresses on both sides, all of one size.** The
const-generic `OpTag<K>` really does monomorphise into eight separate functions.

That uniformity is load-bearing for §7: it is why the swept bands can hold `Ir`
*exactly* constant while the branch behaviour changes, and it is measured rather
than assumed — see the `sweep-t*` rows in §7, where the opcode multiset is *not*
held fixed and `Ir` is nevertheless identical to the instruction on all four
blobs, in all six rungs.

### 6b. `match` is not a dispatch table, and that is why it is forbidden

`.temp/p36/probe_rs.rs` builds the three Rust spellings side by side at `-O3`;
all three print the same checksum (`18178528368736651862`).

| spelling | what it lowers to |
|---|---|
| `[fn(u64) -> u64; 8]` | `call *(%r13,%rcx,8)` — C's shape exactly |
| `[&'static dyn Op; 8]` | `shl $0x4,%ecx` ; `mov 0x8(%rcx,%r13,1),%rcx` ; `call *0x18(%rcx)` |
| `match op { .. }` | `movslq (%r10,%r14,4),%r14` ; `add %r10,%r14` ; **`jmp *%r14`** — a jump table with **all eight arms inlined**, and no call at all |

The task's suspicion is confirmed: **the idiomatic safe-Rust spelling
devirtualises and inlines.** Shipping it as a rung would put a devirtualisation
inside p36's safety column.

⚠ **And it is DEARER, which was not the expected direction.** The shipped
control `r_match` (derived from R3 by exact-string substitution,
`controls/gen_controls.py`) measures **2035.7726 / 15923.0000** against R3's
1710 / 13358 — about **+2.5 Ir per record**. `c_switch`, the same edit on the C
side, measures **2411.5795 / 19099.0000** against `c-gcc-h`'s 1574 / 12326.

⚠ **`r_match`'s `Ir` is not an integer, and that is itself the finding**: a jump
table's arms have different lengths (one falls through, the others need a `jmp`
back), so the executed instruction count becomes **opcode-dependent** where the
table spelling's is exactly constant. Measured over the `sweep-t*` band,
`r_match` reads 4147.0000 at t = 1, 2 and 4 and **4021.5980 at t = 8**, with
`Bi` dropping from 513089 to 450388; the table rungs read one number across the
whole band. So the `match` spelling would have destroyed §7's control as well as
the comparison.

---

## 7. ⚠ `Ir` EXACTLY CONSTANT, WALL CLOCK 3.17× — the pattern's strongest half

`inputs/gen.py`'s `sweep-t*` band varies **the number of distinct indirect-call
targets** (1, 2, 4, 8) at a fixed record count, and `sweep-mix*` holds the
opcode **multiset** exactly fixed and varies only its **order**. Both are read
by `controls/sweep_ir.py`, which uses `callgrind --branch-sim=yes` for `Bi`
(indirect branches executed) and `Bim` (mispredicted).

**The wall-clock half compares ONE BINARY on SEVERAL INPUTS**, so code layout is
identical by construction and no layout population is the relevant control —
p07's *"changing only the workload"* shape (`.memory/01-ladder.md` finding 15).
`controls/clayout.py` is shipped anyway for any future rung-to-rung `ns` claim.

**The noise floor, measured first** (`sweep_ir.py --floor 5`, five
byte-identical copies of one blob under different names, 31 reps each,
`n_iters` rescaled to 200 000 so the per-process constant is under 1% —
`.memory/03-measurement.md` finding 20a):

```
copy0 805.06   copy1 811.56   copy2 838.83   copy3 834.81   copy4 829.02
floor: min=805.06 max=838.83 spread=4.19% of min
```

**Band `t`, `unsafe` cell, `-O3 isolated`, 31 reps, min:**

| blob | targets | `Ir`/call | `Bim/Bi` (simulated) | min ns/call |
|---|---|---:|---:|---:|
| `sweep-t1` | 1 | **3359.0000** | 0.0008 | **439.07** |
| `sweep-t2` | 2 | **3359.0000** | 0.4848 | 648.91 |
| `sweep-t4` | 4 | **3359.0000** | 0.7336 | 1255.87 |
| `sweep-t8` | 8 | **3359.0000** | 0.8581 | **1390.91** |

**`Ir` is identical to the instruction on all four; wall clock is 3.17× apart**,
monotone in the number of targets, against a 4.19% floor: the effect is
**(3.168 − 1) / 0.0419 = 51.7 times** the noise floor.

**And it is not a Rust fact.** The same band on `c-gcc-h`:

| blob | `Ir`/call | min ns/call |
|---|---:|---:|
| `sweep-t1` | **3110.0000** | 373.78 |
| `sweep-t2` | **3110.0000** | 439.16 |
| `sweep-t4` | **3110.0000** | 768.87 |
| `sweep-t8` | **3110.0000** | 1182.23 |

**3.16×, against Rust's 3.17×.** The effect is a property of *an indirect call
with k targets*, measured twice in two languages from one script.

`Ir` is exactly constant across this band in **all eight cells**, measured
rather than assumed from the op sizes:

| cell | `Ir`/call, identical at t = 1, 2, 4, 8 |
|---|---:|
| `c-gcc` | 2599.0000 |
| `c-clang` | 2847.0000 |
| `c-gcc-h` | 3110.0000 |
| `c-clang-h` | 3871.0000 |
| `safe_naive` | 6954.0000 |
| `safe_tuned` | 3374.0000 |
| `unsafe` | 3359.0000 |
| `verus` | 3359.0000 |

⚠ The `t` band does **not** hold the opcode multiset fixed, so this is not true
by construction — it holds because all eight op bodies are the same size (§6),
and that is why §6 measures the sizes rather than asserting them.

**Band `mix`, same binary, opcode multiset held exactly fixed:**

| blob | `Ir`/call | `Bi` | `Bim` | `Bim/Bi` | min ns/call (run 1 / run 2) |
|---|---:|---:|---:|---:|---:|
| `sweep-mixrun032` | 3359.0000 | 513089 | 16415 | 0.0320 | 509.40 / 531.10 |
| `sweep-mixrun016` | 3359.0000 | 513089 | 32415 | 0.0632 | 610.84 / 630.80 |
| `sweep-mixrun008` | 3359.0000 | 513089 | 64415 | 0.1255 | 448.06 / 464.14 |
| `sweep-mixrun004` | 3359.0000 | 513089 | 128415 | 0.2503 | 454.30 / 477.57 |
| `sweep-mixrun002` | 3359.0000 | 513089 | 256415 | 0.4997 | 465.67 / 489.40 |
| `sweep-mixrun001` | 3359.0000 | 513089 | 512415 | 0.9987 | 454.40 / 477.05 |
| `sweep-mixrand` | 3359.0000 | 513089 | 444415 | 0.8662 | 795.67 / 837.88 |

`Bim − 415 = 512000 / R` **exactly**, for every run length `R`, where 512000 is
the total number of dispatches and 415 is the driver's own indirect branches:
the simulator predicts perfectly inside a run and misses at every boundary.

⚠⚠ **AND THE SIMULATED MISPREDICTION RATE DOES NOT ORDER THE WALL CLOCK. THIS
IS A CLEAN NEGATIVE ABOUT AN INSTRUMENT THIS PROJECT RELIES ON.**
`sweep-mixrun001`, which callgrind says mispredicts **99.87%** of indirect
branches, is among the **fastest** blobs; `sweep-mixrand`, at 86.6%, is the
**slowest**, by 1.75×. Callgrind's indirect predictor is a **last-value BTB**;
this box's Cascade Lake has a history-indexed indirect predictor that learns a
period-8 cycle perfectly and cannot learn a random permutation.

`.memory/00-environment.md` records that *branch behaviour IS measurable here by
simulation*, established on p07's **conditional** branches (`Bc`/`Bcm`). **p36
measures that the INDIRECT half (`Bi`/`Bim`) does not track wall clock at all**,
and that is a scoping correction to a standing project claim rather than a new
one. `Bi` is exact and useful (it counts); `Bim` is a model, and on this
workload the model is wrong in direction.

**What is robust, reproduced in two independent runs and clear of the 4.19%
floor:** a *random* opcode order is **1.75–1.80× slower** than the fastest
structured one, at an identical instruction stream. Within the structured
orders, `run001`, `run002`, `run004` and `run008` are mutually indistinguishable
at the floor; `run016` (610.84 / 630.80) and `run032` (509.40 / 531.10) sit
above them, reproducibly, and **p36 does not attribute that** — it needs
hardware counters this box does not have (`perf_event_paranoid = 3`).

⚠ **One design difference between the two bands, disclosed because it bounds the
mix band's magnitude.** In `sweep-mix*` all six windows carry the **same**
256-opcode sequence (only the operand stream differs), so a history-based
predictor has 256 positions to learn; in `sweep-t*` each of the six windows
carries a **different** sequence, so it has 1536. That is why `sweep-t8`
(1390.91 ns) is slower than `sweep-mixrand` (795.67 ns) although both are eight
randomly ordered targets — and it means the `mix` band understates the effect
rather than overstating it.

---

## 8. The spelling spread, and what the prover costs

⚠ **SEARCHED BEFORE PUBLISHING ANY DIFFERENCE.** *"Degenerate as far as this
task searched"* has been false on five consecutive patterns and every time it
flattered a rung. Every control below is derived from a shipped rung by
exact-string substitution with an asserted hit count
(`controls/gen_controls.py`), and every R4-side candidate was **run through
Verus** before its number was used (`.tasks/TASK_026.md` §0.3).

| control | what it is | small | large | admissible R4? |
|---|---|---:|---:|---|
| `unsafe` (**shipped R4**) | hoisted count, unchecked | **1695** | **13343** | yes — `12 verified, 0 errors` |
| `r4_cursor` | + the per-record cursor test (the R2-shaped unsafe rung) | 2717 | 21533 | **yes** — `v_r4_cursor`, `12 verified, 0 errors` |
| `r4_reslice` | shipped R4 + R3's single reslice | 1700 | 13348 | not run through Verus — see below |
| `r_fnptr` | C's bare `fn`-pointer table | 1311 | 10271 | **NO** — see §8a |
| `safe_tuned` (**shipped R3**) | hoisted count, reslice, checked | **1710** | **13358** | — |
| `r3_idx` | R3 without the hoist | 2232 | 17464 | — |
| `safe_naive` (**shipped R2**) | naive indexing | **3498** | **27690** | — |
| `r2_nodead` | R2 with **only** the table access unchecked | 3498 | 27690 | — |
| `r_match` | R3 with `match op { .. }` | 2035.7726 | 15923 | — |
| `c_switch` | R1h with `switch (op)` | 2411.5795 | 19099 | — |

### 8a. ⚠ THE PRICE OF THE PROVER, AND IT IS AN EXACT INTEGER

`r_fnptr` is the shipped R4 with `[&'static dyn Op; NOPS]` replaced by
`[fn(u64) -> u64; NOPS]` — **C's own mechanism**, in Rust. It measures
**1311 / 10271**, i.e. `10.00000·nrw + 31`. The shipped R4 is
`13.00000·nrw + 31`.

> **Same intercept. Slope 13.00000 against 10.00000.
> The trait object costs EXACTLY 3.00000 Ir per dispatch over the function
> pointer, and nothing else.**

**And it is not a rung.** `controls/gen_controls.py --verus` derives the R5 twin
and runs it:

```
=== v_r_fnptr: C's bare `fn`-pointer table, as an R5 twin
error: The verifier does not yet support the following Rust feature: function pointer types
   --> v_r_fnptr.rs:117:1
117 | pub const TABLE: [fn(u64) -> u64; NOPS] = [fop0, ...];
error: The verifier does not yet support the following Rust feature: function pointer types
   --> v_r_fnptr.rs:254:1
254 | fn tab_get_unchecked(i: usize) -> (r: fn(u64) -> u64)
error: The verifier does not yet support the following Rust feature: function pointer types
   --> v_r_fnptr.rs:368:19
368 |             acc = (tab_get_unchecked(op))(acc ^ arg);
   [exit 1]
```

`is not supported`, on the declaration, on the accessor's signature and on the
call. Read the error text and not the exit code (`.memory/01-ladder.md`): **`is
not supported` disqualifies**, because it forces a new *trusted* item.

**So this is `.memory/01-ladder.md` finding 14's sixth instance and its
sharpest.** Elsewhere the prover has excluded a *spelling* of a kernel — p16's
`chunks_exact`, p11's `core::slice::memchr`, p05's and p16's header reads. Here
it excludes the kernel's **central mechanism**, on the pattern whose entire
subject is that mechanism, and the price is a clean 3.00000 Ir per dispatch.

⚠ **A second reading of the same number, and it is the C-vs-Rust one.**
`r_fnptr`'s slope (10.00000) is **exactly `c-gcc`'s** (10.00000), and `r_fnptr`
carries the `op < NOPS` test that `c-gcc` omits. Against the *hardened* C rung
`c-gcc-h` (12.00000·nrw + 38), a guarded Rust `fn`-pointer table is **2.00000
Ir per dispatch cheaper**. That comparison needs the clang column to be a
language claim, and clang's is `11.00000` unguarded / `15.00000` hardened — so
the ordering holds against both C compilers. It is a *control*, not a rung, and
it is quoted as one.

### 8b. ⚠ THE R4 SIDE MOVES, AND CHOOSING R4 WAS A DECISION — disclosed

`r4_cursor` is the R2-shaped unsafe rung: the per-record `len - p < 2` cursor
test restored, the hoisted count removed. **It is what every other pattern in
this tree ships as its R4**, it **verifies** as an R5 twin
(`v_r4_cursor: 12 verified, 0 errors`, same obligation count, no new trusted
item), and it measures **2717 / 21533** — `+1022 / +8190` against the shipped
R4.

> **Had p36 shipped `r4_cursor` as R4, its headline would have been
> `R3 − R4 = −1007 / −8175`: SAFE RUST BEATS UNSAFE RUST — 37.1% of the
> unsafe rung on `small` (1007 / 2717) and 38.0% on `large`. Every
> instruction of that is loop structure and none of it is safety.** That is the
> trap RECAP names as *"the trap that keeps firing"* — p10, p27, p38, p22 — and
> p36 is the first pattern in this tree to have been able to fall into it and
> not.

**So the shipped R4 is R3's loop structure with the checks removed**, which
makes `R3 − R4` a matched-spelling difference and therefore the only kind of
difference `.tasks/TASK_026.md` §0.1 allows to be published. Both numbers ship:
the fixed-R4 bound `R3ship − R4ship = +15.00 flat`, and the R4-side span.

**p36's R4-side span is `1695 … 2717` on `small` and `13343 … 21533` on
`large`** — width **1022 / 8190** — with **two members verified admissible**
(the shipped rung and `r4_cursor`). That makes p36 only the **second** pattern
in this project with a non-degenerate, admissible R4-side width; p03 was the
first. `r4_reslice` (1700 / 13348) sits inside the span and its Verus twin was
**not built** — it needs `vstd::slice::slice_subrange` and the subrange-indexing
proof that goes with it, which is real work this task did not do. **Its number
is therefore reported and NOT counted in the span**, per the project's own rule.

**The R3-side span is `1710 … 2232` / `13358 … 17464`** (shipped R3 to
`r3_idx`), width 522 / 4106. The shipped R3 is the **cheapest found** in
contract, on **both** blobs — a phrase, not a floor: four published floors on
this project have been refuted and *"cheapest found"* names the input
(`small.bin` and `large.bin`) as well as the spelling.

### 8c. The `external_body` dispatch — the route not taken, and its TCB

`.temp/p36/probe_a6.rs` is the alternative R5: a bare `fn(u64) -> u64` table
declared **outside** `verus!` and read through an `external_body` wrapper whose
`ensures` is `r == op_spec(i, x)`. It verifies, and it is not vacuous — the
guarded call site verifies and the unguarded one reports

```
error: precondition not satisfied
  --> probe_a6.rs:52:5
   |
34 |         op < 2,
   |         ------ failed precondition
...
52 |     call_table(op, x)
   |     ^^^^^^^^^^^^^^^^^
verification results:: 2 verified, 1 errors
```

so the bounds obligation still binds. **What it costs is the TCB**: its
`ensures` axiomatises eight function bodies that the verifier then never checks,
and it has no verifiable twin at all — a twin would have to *call* the `fn`
pointer, which is the thing Verus cannot type. The shipped design pays
**3.00000 Ir per dispatch** (§8a) to keep those eight bodies verified. That is
the trade, priced.

### 8d. What CFI costs

`controls/cfi_probe.py`, clang `-O3` with and without
`-flto -fuse-ld=lld -fvisibility=hidden -fsanitize=cfi-icall`:

```
small.bin    clang-cfi-O3= 2589.0000  clang-plain-O3= 1439.0000  delta=+1150.0000 (+79.92%)
large.bin    clang-cfi-O3=20509.0000  clang-plain-O3=11295.0000  delta=+9214.0000 (+81.58%)
```

`(9214 − 1150) / (1024 − 128) = 9.00000` exactly, so **CFI costs
`9.00000·nrw − 2` Ir per call — 9.00 instructions per dispatch, +80%.** Set
against the *source-level* range test in the same compiler
(`R1h − R1 = 4.00000·nrw` on clang, `2.00000·nrw − 1` on gcc), the compiler
mitigation is **2.25× the clang check and 4.5× the gcc check, per dispatch**.

⚠ **This is a control and it is not comparable to the ladder's columns.** It is
built with different flags, a different linker and a different visibility model,
and `-fsanitize-recover` is on so it continues rather than trapping. It is here
because `.tasks/TASK_072.md` asked for the real-world hardened answer to be
named and priced somewhere, and because the honest version of the catalogue's
*"R1h has a real answer (`-fsanitize=cfi`) that no pattern has priced"* is
*"here is the number, and here is why it cannot be a rung"*.

---

## 9. Verus

### 9a. The proof

`12 verified, 0 errors` shipped; `14 verified, 0 errors` under `--cfg
slb_twin`. The decomposition is in `spec.md`'s `verus.obligations_note`; every
term was measured with `--verify-function <name> --verify-root` and the terms
sum to the pin:

```
NOPS 1 + SENT 1 + TABLE 1 + OpTag::apply 1 + run 1 + kernel 2 + main 5 = 12
```

`TABLE` carrying an obligation of its own is worth noting: it is a `const`
**array of trait objects** and nothing else in this tree has one.

The one interesting obligation is `tab_get_unchecked`'s `requires i < NOPS`,
discharged at the single call site from the exec test `op < NOPS`. **It is the
only precondition in this tree whose violation is a control transfer rather than
a value** — and it is an ordinary bounds obligation, which `spec.md`'s `note`
says plainly rather than dressing up.

### 9b. ⚠ EIGHT `impl` BLOCKS VERIFY AND THE GATE REFUSES THEM

The first `verus.rs` used eight separate `impl Op for OpN` blocks. It verified —
**`19 verified, 0 errors`** shipped and `21 verified, 0 errors` under
`--cfg slb_twin` — and every rung agreed with `model.py` on all seven inputs.

It cannot ship, because `harness/vparse.py::duplicate_names` fails any pinned
file that defines a name more than once, and eight impls define `apply` eight
times (and `spec_apply` eight times). That check exists for a good reason —
`check.py::check_verus_contract`: *"the gate used to key items by name and keep
the last, so a decoy could supply the pinned contract for the real item"* — and
it is not a defect.

The repair is **one `impl<const K: u8> Op for OpTag<K>` with eight
monomorphisations**, which gives eight distinct types, eight distinct vtables
and eight distinct code addresses while defining `apply` exactly once. It
verifies, it needs **no `harness/` change**, and §6 measures that the eight
monomorphised bodies really are eight separate 14-byte functions.

⚠ Recorded rather than worked around silently, because it is a real constraint
on what a Verus pattern in this tree may look like: **a pinned `verus.rs` may
not define one item name twice, so per-type trait impls must be expressed as one
generic impl.**

---

## 10. Proof mutants

`controls/mkmutants.py`, derived from the shipped `verus.rs` by exact-string
substitution with asserted hit counts, **always run with `--multiple-errors
20`** (`.memory/04-verus.md` §2b — p22 skipped it and its review found a mutant
failing on a different obligation than claimed). Full error lists below;
`.temp/p36/mutants.log` has them verbatim.

⚠ **The `file:line` columns are stripped from the quotes below on purpose.** The
mutants are regenerated from the shipped `verus.rs`, so every line number in
them moves whenever a comment in `verus.rs` moves — this file's first draft
quoted numbers that were already two lines stale by the time the rungs settled.
`.memory/06-catalogue.md`'s rule is *cite the function, not the line*; the error
MESSAGE and the CLAUSE are what identify an obligation, and those are quoted in
full.

### m1 — delete `op < NOPS`: `c/kernel.c`'s bug written into R5

```
verification results:: 11 verified, 1 errors
error: invariant not satisfied at end of loop body
    | run(buf@, off as int, len as int, t as int, nrec as int, p as int, acc) == run(...)

error: precondition not satisfied
    |         i < NOPS,
    |         -------- failed precondition
    |         acc = tab_get_unchecked(op).apply(acc ^ arg);
    |               ^^^^^^^^^^^^^^^^^^^^^
[exit 1]
```

**The second error is p36's obligation**: with the test gone, nothing licenses
the table read whose result the program calls.

⚠ **It fails on TWO obligations, not one, and saying so is the point of
`--multiple-errors`.** Deleting the test also changes the *function* — the
sentinel arm disappears — so the functional invariant breaks as well. **No
mutant here isolates the memory-safety obligation on its own**, and the
defensible claim is the narrower one: *the obligation is real, it is checked,
and it cannot be discharged without the test.*

### m2 — a wrong functional spec: `op_spec`'s constant at opcode 3

```
verification results:: 11 verified, 1 errors
error: postcondition not satisfied
    |               r == self.spec_apply(x),
    |               ^^^^^^^^^^^^^^^^^^^^^^^ failed this postcondition
...
    | /         if K == 0 {
    | |_________- at the end of the function body
[exit 1]
```

⚠ **It fails at `OpTag::apply`, not at `kernel`**, which is a fact about the
const-generic shape worth recording: `spec_apply` for `OpTag<K>` is *defined* as
`op_spec(K, x)`, so moving `op_spec` breaks the impl's own postcondition before
the kernel is ever considered.

### m3 — an inconsistent TRUSTED postcondition: `tab_get_unchecked`'s `ensures` shifted one slot

```
--- shipped
verification results:: 11 verified, 1 errors
error: invariant not satisfied at end of loop body   (the `run` relation)
--- --cfg slb_twin
verification results:: 13 verified, 1 errors
error: invariant not satisfied at end of loop body   (the same one)
[exit 1 in both]
```

`.memory/05-layout.md` item 5 asks every pattern for a mutant that makes a
trusted postcondition **inconsistent** rather than merely weaker. This is p36's.

⚠ **THE PREDICTION MADE ABOUT IT WAS WRONG AND IS RECORDED RATHER THAN QUIETLY
CORRECTED.** It was written expecting the mutant to VERIFY in the shipped
configuration — the item is `external_body`, so Verus never reads its body — and
to be caught only by the twin. Measured, it fails in **both**: p36's functional
`ensures` ties slot `op` to `op_spec(op, ..)` through `run`, so an `ensures`
that hands back the wrong slot breaks the loop invariant immediately. That is a
*stronger* result than the one predicted.

### m4 — a trusted PRECONDITION weakened off by one, and the one the twin exists for

```
--- shipped
verification results:: 12 verified, 0 errors            <-- SILENT
[exit 0]
--- --cfg slb_twin
verification results:: 13 verified, 1 errors
error: precondition not met: index in bounds for this access
    |     v[i]
    |     ^^^^
[exit 1]
```

`buf_get_unchecked`'s `requires i < v@.len()` becomes `i <= v@.len()`. In the
shipped configuration the file verifies cleanly while the accessor now claims a
one-past-the-end read is licensed — an axiomatised falsehood, with **the same
obligation count and no diagnostic**. `--cfg slb_twin` swaps in the checked body
`v[i]` and it fails. This is `.memory/04-verus.md`'s *"a `requires` deleted from
an external_body wrapper — same count, no diagnostic, and every caller's
obligation silently gone"*, in its off-by-one form.

⚠ **THE WEAKENING HAS TO BE APPLIED TO BOTH COPIES, AND FINDING THAT OUT WAS
ITSELF A MEASUREMENT.** The first version of this mutant changed the *trusted
item's* `requires` only. Result: `12 verified, 0 errors` shipped **and
`14 verified, 0 errors` under the twin** — because the twin carries its own copy
of the contract text and kept `i < v@.len()`, so it verified against the strong
precondition while the trusted item shipped the weak one. What catches *that*
shape is not Verus: it is the **gate**, whose stage 5c-twin requires the twin's
signature and contract to equal the trusted item's. **The twin regime has two
independent teeth**, and only the second of them is Verus.

---

## 7bis. TCB

**Four `external_body` items, two of them contract-bearing.**

| item | contract | class |
|---|---|---|
| `buf_get_unchecked` | `requires i < v@.len()`, `ensures r == v@[i as int]` | **V-gap** — vstd ships no spec for `<[T]>::get_unchecked` |
| `tab_get_unchecked` | `requires i < NOPS`, `ensures r == TABLE@[i as int]` | **V-gap** — same, for `<[T; N]>::get_unchecked`, on a `const` array of trait objects |
| `load_input` | none | **infra** — argv, file I/O, decoding |
| `emit` | none | **infra** — `println!` |

Per RECAP's settled answer 2, one number plus the classification: **4 trusted
items, 2 with contracts; 2 V-gap, 2 infra, 0 U-license, 0 exposed.** Both
contract-bearing items have verified twins.

SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) The twin's body is `v[i]`, the checked stand-in for `*v.get_unchecked(i)` in
the exact sense the twin regime asks for: same value, same type, same aliasing,
and the *only* difference is the bounds check that `requires i < v@.len()`
exists to license. Verus verifies the twin's body against that precondition, so
a `requires` too weak to license the unchecked read is too weak to license the
checked one and the twin run fails — measured, as mutant m4 above, which is
`12 verified, 0 errors` shipped and `precondition not met: index in bounds for
this access` under `--cfg slb_twin`.
(b) The `ensures` is complete with respect to every unchecked operation the body
performs, because the body performs exactly one: a single-byte read at index
`i`. There is no `i + 1`, no length arithmetic, no store and no second slice —
the whole body is `*v.get_unchecked(i)`, so `r == v@[i as int]` says everything
about it. This is the completeness question TASK_009_REVIEW x4 raises, and the
answer here is structural rather than promissory: the body is one expression and
the contract names its one index.
(c) Each clause means the same in both configurations. `v@` is the sequence view
of the same `&[u8]` in the shipped build and in the twin; `i` is the same
`usize`; `v@.len()` is `spec_slice_len`, a property of the slice and not of the
accessor. No `#[cfg]`-varying constant appears in either clause — the `slb_twin`
token occurs only in the twin's own `#[cfg]` attribute, which `check.py` verifies
independently.

SLB-TRUSTED-ARGUMENT verus.rs tab_get_unchecked

(a) The twin's body is `TABLE[i]`, the checked stand-in for
`*TABLE.get_unchecked(i)`. Same table, same index, same `&'static dyn Op`
result; the only difference is the bounds check against `NOPS`, which is exactly
what `requires i < NOPS` licenses, and Verus verifies the twin's body under it.
The twin is a *real* checked read and not a re-statement: `TABLE[i]` on a
`[T; N]` is Verus-visible through `vstd::array`, which is why the twin
configuration verifies at all (`14 verified, 0 errors`).
(b) The `ensures` is complete with respect to every unchecked operation the body
performs, and completeness needs saying carefully here, because this is the item
that licenses an INDIRECT CALL. The body performs exactly one unchecked
operation: a read of slot `i` of a fixed-extent `const` array. It does not call
anything, does not dereference the reference it returns, and does not touch
`i + 1`. `r == TABLE@[i as int]` therefore says everything the body does: the
value returned is the reference the table holds at `i`. Everything about what
*calling* that reference does comes from `Op::apply`'s own `ensures`, which is
VERIFIED for the one `impl<const K: u8> Op for OpTag<K>` and is not trusted at
all. The alternative wrapper — one whose `ensures` were `r == op_spec(i, x)`,
i.e. one that axiomatised the callee's behaviour — is deliberately not shipped,
because it would move all eight function bodies into the TCB; it is built and
measured as a control in §8c, and mutant m3 shows what an inconsistent `ensures`
on THIS item costs.
(c) Each clause means the same in both configurations. `NOPS` is a plain
`const usize` with no `#[cfg]` anywhere near it, `TABLE` is the same `const`
array in both, and `TABLE@` is vstd's array view of it; `i` is the same `usize`.
The twin is gated only by its own `#[cfg(slb_twin)]`, and no measured build sets
that cfg, so the twin costs zero instructions structurally rather than by
measurement.

---

## 11. Housekeeping, and the disclosures this file owes

### 11a. The `slb-contract` sha256

**As first written, before any cell was built:**
`f8d00370a630affec9063635141b9f8c13b196adc48a82a74399c9823d658b64`
(recorded in `.temp/p36/NOTES.md` immediately after `controls/mkcontract.py`
first wrote `spec.md`, and before `harness/build.py p36` had ever run).

**As shipped:**
`ffb7fc4a68e73342b3efe0c2e17b44ea0df5542c83822737a580d42991b3b1d2`

⚠ **IT MOVED TWICE, AND HERE IS EXACTLY WHY, EDIT BY EDIT.**

**Edit 1** (`f8d00370…` → `57b16147a318e1adac7d46093115673836651dab1fd0ce85da1be1a780b9e556`).
The first gate run's idiom audit reported

```
audit  required : 1 pin nothing, 6 scoped-absent pair(s)
audit    pins nothing  required[3]  rust 0 of 4 rung(s)  `min(nrec, (len - 4) / 2)`
audit    absent        required[1]  rust unsafe.rs        `TABLE[op]`
audit    absent        required[1]  rust safe_naive.rs    `tab_get_unchecked(op)`
```

Three backticked spans in the *prose* of two `required` entries were pinning
things the entries themselves say are deliberately NOT pinned — the hoisted
expression (which no rung spells that way) and the two table-access spellings
(which are the safety axis). The generator was edited to state them in prose
instead, and `spec.md` was regenerated. **Nothing enforced moved**: `required`
entries are reporting-only and cannot fail the gate; the `forbidden` list, the
`verus` pins, the `identity` levels, the `driver` pin and the `collapse` pin are
byte-identical across the two hashes. The edit happened **before any number in
`results/` was produced**.

**Edit 2** (`57b16147…` → `430c64b9…`), and this one IS after measurement, so it
is exactly what `.memory/01-ladder.md`'s direction test governs. It replaced
**adjectives with the numbers that had by then been measured**, in four places
in `idiom.why`, and changed the rung scope of one `required` entry's prose
because the R4 spelling changed (§8b):

| what changed in `idiom.why` | before | after |
|---|---|---|
| the price of the trait object | *"../NOTES.md 8 gives the instruction counts"* | `10.00000·nrw + 31` vs `13.00000·nrw + 31`, **3.00000 Ir per dispatch** |
| the `match` control | *"what it costs against the table is one of the two numbers"* | 2035.7726 / 15923 against 1710 / 13358, and the non-integer-`Ir` finding |
| the op set's uniformity | *"identical by construction"* | the 3.17× / 3.16× wall-clock result and the 4.19% floor |
| **the R4 side** | (absent) | the `r4_cursor` disclosure: it verifies, it is 1022 / 8190 dearer, and shipping it would have published *safe beats unsafe by 1007 / 8175 Ir per call* |
| `required[3]`'s rust prose | *"safe_naive.rs, unsafe.rs and verus.rs write the same subtraction-first guard"* | *"safe_naive.rs writes it; safe_tuned.rs, unsafe.rs and verus.rs hoist"* — a **factual correction**, because R4/R5 changed |

**Edit 3** (`430c64b9…` → `f00aeb26…`), one word. The gate's audit reported

```
audit  required : 1 pin nothing
audit    pins nothing  required[1]  rust 0 of 4 rung(s)   `required`
```

— edit 2's new sentence *"a backtick in a `required` entry PINS a spelling"*
contained a backticked word, and the audit correctly treated it as a spelling
that no rung writes. The backticks were removed and the sentence now says so.
**That is the third false-positive shape `.tasks/TASK_072.md` warned about —
backticking the replacement — caught by the mechanism that exists for it, on
text written to explain the mechanism.** The audit is now
`required_pins_nothing: 0`, `required_absent: 2` (both genuine: `c/kernel.c`
lacks the safety line and the sentinel arm), `forbidden_hits: 0` over 11
forbidden spellings.

**Edit 4** (`f00aeb26…` → `de149ffb…`), three words: *"in ALL SIX RUNGS"* became
*"in ALL EIGHT CELLS"*, because the `Ir`-invariance claim was then measured on
`c-gcc` and `c-clang` as well and holds on all eight (§7). A count correction in
the strict direction.

**Edit 5** (`de149ffb…` → `ffb7fc4a…`), a percentage replaced by the two
absolute figures it was rounded from: *"safe Rust beats unsafe Rust by 60%"*
became *"by 1007 / 8175 Ir per call"*. `1007 / 2717 = 37.1%` of the unsafe rung
and `1007 / 1710 = 58.9%` of the safe one, so *"60%"* was a rounded reading of
one of two possible denominators and named neither. The same correction was made
in `unsafe.rs`, `README.md` and this file. **A percentage whose denominator is
ambiguous is exactly the shape `.memory/03-measurement.md` warns about; the
absolutes are unambiguous.**

**The direction test.** Nothing was *weakened*: no `forbidden` entry was
removed or narrowed, no `verus` pin moved, no `identity` level was relaxed, no
`required` entry lost a backticked spelling. Four entries gained measured
numbers where they had promises, one gained a disclosure that did not exist
before, and one was corrected to describe the shipped tree. **The declaration
got stricter and more falsifiable, not looser** — and the one thing that would
have made this edit suspect, moving `identity` from `exact` to `norel` after
seeing a failure, is not what happened: `norel` was pinned in edit 1, before any
measurement, from the §5 finding.

⚠ **`git show HEAD:patterns/p36-vtable-dispatch/spec.md | diff - …` IS
UNAVAILABLE HERE AND CITING IT WOULD BE A FALSE DISCLOSURE.** That command
compares the **working tree to HEAD**, not *first written* to *shipped*. p36
lands in **one commit**, so on a clean tree it prints nothing and always looks
like it passed — which is what happened on p22, whose `1f29b02e… → 044f02cd…`
disclosure has no artefact behind it (TASK_070_REVIEW). **The two hashes above
are the only evidence**, which is why PROTOCOL definition-of-done 6 demands the
first be written before any cell is built.

### 11b. What is generated

`spec.md` is GENERATED by `controls/mkcontract.py`; edit the generator and
re-run it. `--check` re-derives the file byte for byte and is part of the
reproduction recipe in `README.md`. The shared named-spelling paragraph (11 003
chars) is READ out of `patterns/p22-hash-probe/spec.md` at generation time and
never embedded (`.memory/05-layout.md`).

`inputs/*.bin` are generated by `inputs/gen.py`, which is deterministic:
regenerated twice into two scratch directories and `diff -r` is empty, and the
second run reproduces the committed blobs exactly. The gate hashes `gen.py` and
never the blobs, so that determinism is the whole basis of the claim.

### 11c. What was NOT done

- `r4_reslice`'s Verus twin was not built (§8b): it needs
  `vstd::slice::slice_subrange` and the subrange-indexing proof. Its number is
  reported and is **not** counted in the R4-side span.
- `controls/clayout.py` is ported and its paths are checked (`.temp/p36/`, not
  `.temp/p14/`), but **no layout population was run**, because p36 publishes no
  rung-to-rung `ns` figure. Every wall-clock number here is one binary on
  several inputs. Run `clayout.py` before quoting any p36 `ns` number that
  compares two cells.
- The `sweep-mix*` band's non-monotone middle (`run016` slower than `run032`,
  reproducibly) is **not attributed**. It needs hardware counters this box does
  not have.
