# p36 — function-pointer table dispatch: findings

Built at TASK_072, **corrected at TASK_073 on TASK_072_REVIEW** (2 blockers,
5 majors, 7 minors, 36 clean negatives). Read `spec.md` first; this file records
what was measured, in the order it was measured. Every `Ir` figure is
**kernel-exclusive `Ir` per call at `-O3`, `isolated` inline mode**, unless it
says otherwise — `.memory/03-measurement.md`'s INLINE-MODE rule, and p36 quotes
`isolated` everywhere because that is the mode in which the kernel is its own
symbol.

⚠⚠ **AND ON THIS PATTERN "KERNEL-EXCLUSIVE" IS NOT A UNIT, IT IS A
LIMITATION — READ §0e BEFORE ANY NUMBER BELOW.** p36's kernel *is* a call, the
eight dispatch targets are outside every kernel-exclusive figure, and the
excluded work is **not equal across cells**. §0e prices it and names the three
published claims that moved.

## What TASK_073 changed, in one place

| what | was | is | where |
|---|---|---|---|
| the safety number | `R3 − R4 = +15.00 flat`, called matched-spelling | **fixed-R4 bound with the cheapest R3 found: `+7.00 flat`**; **matched-spelling pair: `+10.00 flat`**; both spans published; `+15.00` retained as the fixed-R4 bound with the shipped R3 | §8b |
| *"the shipped R3 is the cheapest found in contract"* | asserted | **false as measured** — `r3_window` is 1702 / 13350 | §8b |
| `r_match` *"and it is DEARER"* | inside the hashed `idiom.why` | **reversed** on the comparable column: `r_match` is CHEAPER by 58.2274 / 507.00; the forbid now rests on the two grounds that survive | §0e, §6b |
| gcc vs clang, C | 10.00000 vs 11.00000 | **14.00000 vs 14.00000** — the gap was gcc's `endbr64` | §0e, §4 |
| §8a vs `c-gcc-h` | 2.00000 cheaper | **3.00000 cheaper** | §8a |
| `r4_reslice`'s twin | *"not built"* | **built, `12 verified, 0 errors` first try** — three verified R4s | §8b, §11c |
| `identity.why` / `verus.rs` | *"60 instructions, 193 bytes"*, `%rsi` | **55 / 54 / 170**, `%r12` — the old numbers were `r4_cursor`'s | §5a, §11a |
| *"first pattern whose kernel references a global at all"* | | **false** — ten do; the true claim is *"…that R4 and R5 place at different distances"* | §5a |
| *"ghost code fully erases"* | | **scoped**: 64 bytes of `.data.rel.ro` + 26 of `.text` | §5 |
| *"the identity pin caught it"* | | **scoped to the kernel function's bytes**; the pin is blind to `TABLE` at `exact` too | §5, §5a |
| the noise floor | 4.19% | **0.19 – 1.22%**, eight floors, two sessions, two protocols | §7 |
| the `Bim` clean negative | 0.9987 vs 0.8662 across 1.75× | **0.8730 vs 0.8662 across 2.33×** (`sweep-mixrand6`) | §7 |
| `sweep-t*` `Ir`-constancy | kernel-exclusive only | **program totals identical too: 8,635,685 ×4** | §7 |
| band-n residue classes in `gen.py` | `{0,2,4,6}` mod 8 | **`{0,1,2,5,6,7}`** — the docstring was wrong, the printed rows never were | `inputs/gen.py` |

**What did NOT move, stated first because two headlines did:** ✅ **the
`3.00000` Ir per dispatch the trait object costs over a `fn` pointer** — 13 vs
16 on the corrected column, 10 vs 13 on the kernel-exclusive one, +3.00000
either way (§8a); ✅ the §7bis TCB tally (4 items, 2 contract-bearing); ✅ all
four proof mutants; ✅ `gen.py`'s determinism; ✅ all seven shipped control
figures.

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
twin (the *every rung is a spelling* finding — RECAP finding 14; named rather
than numbered, because 14 in `.memory/01-ladder.md` is p13), so a bare
`fn`-pointer table is not an
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

### 0e. ⚠⚠ THE KERNEL-EXCLUSIVE COLUMN, ON THE ONE PATTERN WHOSE KERNEL IS A CALL — and gcc's invisible CFI tax

**Added at TASK_073; TASK_072_REVIEW B2 found it and it is the more useful half
of that blocker.** `.memory/03-measurement.md`'s p13 rule governs — *"the
kernel-exclusive column is comparable only when the rungs call the SAME
routines … it is the wrong column when the rungs dispatch DIFFERENT work
outward"* — and p36 stated the exclusion in its header without ever checking
its consequence. Measured (`.temp/p36c/callee_ir_{small,large}.log`, `-O3
isolated`, 20 000 calls, `callgrind_annotate` rows for `op0..op7` /
`<OpTag<K>>::apply` summed):

| cell | kern-excl/call | dispatch targets | TOTAL/call | kern+targets law |
|---|---:|---:|---:|---|
| `c-gcc` | 1319 / 10279 | **512 / 4096** | 1855.3740 | `14.00000·nrw + 39` |
| `c-gcc-h` | 1574 / 12326 | **512 / 4096** | 2110.3749 | `16.00000·nrw + 38` |
| `c-clang` | 1439 / 11295 | 384 / 3072 | 1846.2514 | `14.00000·nrw + 31` |
| `c-clang-h` | 1951 / 15391 | 384 / 3072 | 2358.2508 | `18.00000·nrw + 31` |
| `safe_naive` R2 | 3498 / 27690 | 384 / 3072 | 3914.2004 | `30.00000·nrw + 42` |
| `safe_tuned` R3 | 1710 / 13358 | 384 / 3072 | 2126.1998 | `16.00000·nrw + 46` |
| `unsafe` R4 | 1695 / 13343 | 384 / 3072 | 2111.1905 | `16.00000·nrw + 31` |
| `verus` R5 | 1695 / 13343 | 384 / 3072 | 2111.1986 | `16.00000·nrw + 31` |
| `r_fnptr` | 1311 / 10271 | 384 / 3072 | 1727.1863 | `13.00000·nrw + 31` |
| `r3_window` | 1702 / 13350 | 384 / 3072 | 2118.1932 | `16.00000·nrw + 38` |
| `r_match` | 2035.7726 / 15923 | **0 / 0** | 2067.9569 | — (non-integer) |
| `c_switch` | 2411.5795 / 19099 | **0 / 0** | 2435.9527 | — (non-integer) |

**The excluded work is 4.00 Ir per record for gcc, 3.00 for clang and rustc, and
0.00 for `r_match` and `c_switch`, which have no callees at all.**

⚠⚠ **THE CAUSE IS A CFI MITIGATION, AND THIS MATRIX HAS BEEN PRICING IT
INVISIBLY ALL ALONG.** Debian's gcc 13.3.0 defaults to
**`-fcf-protection=full`**, so every function gets an `endbr64` IBT landing pad
and every one of the eight `opN` opens with one — **49 `endbr64` in each gcc
binary against 5 in all six others** (`.temp/p36c/cet_probe.log`, and the
disassembly of `op0` shows `endbr64 ; movabs ; xor ; ret` against clang's and
rustc's `movabs ; xor ; ret`). Rebuilt with `harness/build.py`'s own flag list
plus `-fcf-protection=none` and nothing else, same checksum:

```
build                                     endbr64   kern-excl   targets       TOTAL
c-gcc   default (-fcf-protection=full)         49   1319.0000  512.0000   1855.3740
c-gcc-h default (-fcf-protection=full)         49   1574.0000  512.0000   2110.3749
c-gcc   -fcf-protection=none                    5   1318.0000  384.0000   1726.3331
c-gcc-h -fcf-protection=none                    5   1573.0000  384.0000   1981.3325
   ... and on large.bin: 10279 -> 10278 kernel, 4096 -> 3072 targets
```

> **gcc's default IBT costs `1.00000·nrw + 1` Ir per call on p36 — exactly.**
> 129.0409 on `small` and 1025.0408 on `large`, i.e. `nrw + 1` plus the one-time
> pads in `main`/`driver` amortised over 20 000 calls. **1.00 Ir per dispatch,
> and 1 Ir per call for the kernel's own pad.**

⚠ **Note where each half lands.** The per-call `+1` is the kernel's own landing
pad and is therefore **inside** every published gcc figure; the per-dispatch
`1.00` is **outside** all of them. So §8d's *"the real-world hardened answer for
this bug class is a compiler mitigation this matrix cannot price"* is **wrong,
and it was wrong when it was written**: the matrix prices **two** points of the
CFI curve already — IBT landing pads at 1.00 Ir/dispatch, in gcc's column only,
undeclared; and `cfi-icall` at 9.00 Ir/dispatch as a control (§8d). This is a
finding and not an erratum: **a compiler default put a control-flow-integrity
mitigation into one language column of a cross-language benchmark, and nothing
in the harness declares it.**

**Three published claims move, and none of them is the `3.00000`.**

1. **`r_match` reverses** — §6b and the hashed `idiom.why`. On kernel+targets it
   is **cheaper** than the shipped R3 by **58.2274 / 507.00** (2035.7726 /
   15923.0000 against 2094.0000 / 16430.0000; program totals agree, 2067.96 vs
   2126.20 and 15958.79 vs 16465.81). See §6b for what the forbid now rests on.
2. **The gcc-vs-clang C gap vanishes**: `10.00000` vs `11.00000` becomes
   `14.00000` vs `14.00000`. The whole gap was the landing pad.
3. **§8a's C-vs-Rust figure was understated by 1**: `c-gcc-h` is
   `16.00000·nrw + 38` and `r_fnptr` is `13.00000·nrw + 31`, so the guarded Rust
   `fn`-pointer table is **3.00000** Ir per dispatch cheaper, not 2.00000.

✅ **What does NOT move: §8a's `3.00000` Ir per dispatch for the trait object.**
`r_fnptr` and the shipped R4 dispatch the *same* 3.00 Ir outward, so the
difference is `13 → 16` on this column and `10 → 13` on the kernel-exclusive
one — **+3.00000 either way.** A reader who meets this section first should not
assume p36's structural result fell; it did not.

⚠ **The `Ir` values themselves are correct AS KERNEL-EXCLUSIVE and nothing was
re-measured to write this section.** What was wrong is the interpretation and
the three derived claims above.

⚠ **AND THE GOVERNING RULE IS TOO NARROW AS WRITTEN — a `harness/` question,
reported and not built.** `.memory/03-measurement.md`'s p13 rule says *"list the
`@plt`/`@GLIBC` calls of every cell"*. p36 is the first pattern where the
outward-dispatched work goes to the pattern's **own** functions, so the rule as
spelled would not have fired. And `results/p36-vtable-dispatch.json` carries
only `kernel_exclusive_ir` (plus `main_exclusive_ir`); there is **no totals
column and no per-cell callee marginal**, so the table above was computed by
summing `callgrind_annotate` rows in a scratch probe. **Whether the harness
should record a callee or total column is a `harness/` decision and TASK_073 did
not take it** — the constraint was explicit. It is queued for the manager.

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

⚠ **Every slope above is kernel-EXCLUSIVE. On the comparable column (§0e) add
4.00 to each gcc row and 3.00 to every other row**, which turns `c-gcc`'s
`10.00000` and `c-clang`'s `11.00000` into **`14.00000` and `14.00000`** and
deletes the C-compiler gap entirely. The Rust rows all shift by the same 3.00,
so **no R2/R3/R4/R5 difference below changes**.

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
| `R3ship − R4ship`, fixed-R4 bound with the shipped R3 | **`15`, flat** | +15 | +15 |
| **`r3_window − R4ship`, fixed-R4 bound with the cheapest R3 found** | **`7`, flat** | **+7** | **+7** |
| **`R3ship − r4_reslice`, the matched-spelling pair** | **`10`, flat** | **+10** | **+10** |
| `R2 − R4`, the naive spelling | `14.00000·nrw + 11` | +1803 | +13995 |
| `R1h − R1`, gcc's source check | `2.00000·nrw − 1` | +255 | +2047 |
| `R1h − R1`, clang's source check | `4.00000·nrw + 0` | +512 | +4096 |
| gcc's DEFAULT IBT (§0e), outside every figure | `1.00000·nrw + 1` | +129.04 | +1025.04 |

⚠ **THE FIRST ROW SHIPPED ALONE, AS `+15.00 flat`, AND IT SHOULD NOT HAVE**
(TASK_072_REVIEW B1). It is neither the matched-spelling pair nor the tightest
bound; §8b has the four numbers and the argument. What is true of **all three**
safety rows is the shape:

**`R3 − R4` is a per-CALL constant and 0.00000 Ir per RECORD, on every pairing.
The bounds checks are entirely outside the loop, and the slope is `13.00000` in
every in-contract R3 and every admissible R4.** The mechanism is in the listing
rather than inferred: R3 reslices once (`&buf[off+4 .. off+4+2·nw]`), and its
loop body is

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
object code, and the `identity` pin caught it — *the pin over the KERNEL
FUNCTION'S BYTES*, which is a scope clause TASK_073 added and §5b is why it
matters.**

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

**What survives and what does not** — ⚠ **rewritten at TASK_073; the first
version of this paragraph was too generous to finding 1 and TASK_072_REVIEW M4
measured why.** `.memory/01-ladder.md` finding 1 has two clauses and they do not
fare the same:

- ✅ *a Verus proof costs exactly zero instructions* — **survives, scoped**: zero
  EXECUTED instructions, and zero instructions in the kernel symbol. 55 = 55
  instructions and 170 = 170 bytes in both declaration orders.
- ❌ *ghost code fully erases* and *the proven binary is byte-identical to the
  unproven one* — **FALSE here**, and at `md5_fn` the two differ
  (`60e41a42f72a8d80143b5494d8b267a9` against
  `244e6712a9870fa1f0289f875ec9bdd3`).

**Measured** (`.temp/p36c/vtable_probe.py`, which reads `TABLE`'s address out of
the kernel's own `lea` through `harness/asm.py` and then resolves the
`R_X86_64_RELATIVE` relocations — these are PIE binaries, so `.data.rel.ro` is
zeroed in the file image and reading the raw bytes gives eight null pointers):

```
unsafe-O3-isolated   TABLE@0x54f98   8 distinct vtables 0x54e98 … 0x54f78
                     gaps 32,32,…    -> VTABLE = 32 BYTES
                     vtable[0] slot3 = 0x15a40  <OpTag<0> as Op>::apply  size=14
verus -O3-isolated   TABLE@0x55108   8 distinct vtables 0x54fc8 … 0x550e0
                     gaps 40,40,…    -> VTABLE = 40 BYTES
                     vtable[0] slot3 = 0x15b70  <OpTag<0> as Op>::apply       size=14
                     vtable[0] slot4 = 0x15b50  <OpTag<0> as Op>::spec_apply  size=26
   all eight R5 vtables' slot4 -> 0x15b50 ; distinct ghost targets: 1
```

> **In the shipped configuration the proof costs 64 bytes of `.data.rel.ro`
> (8 types × 8) plus one folded 26-byte `.text` stub that R4 does not have.**

**The scope clause, in the form to record:** *a Verus proof costs zero executed
instructions and zero instructions in the kernel symbol; ghost code erases from
executable paths, but a `spec fn` declared in a **trait** is codegenned as a stub
and occupies a vtable slot in every implementing type — 8 bytes per type of
`.data.rel.ro`, plus one emitted stub — and its declaration position is part of
the vtable ABI.* That is strictly stronger than *"a ghost declaration moved a
byte of the object code"*, which is only observable when the ghost is declared
first; the 64 bytes are there in the **shipped**, `identity`-green build.

**And it is the same fact as §5a.** `TABLE` sits immediately after the eight
vtables — 0x54e98 + 8·32 = 0x54f98 in R4, 0x54fc8 + 8·40 = 0x55108 in R5 — so
the extra slot pushes `TABLE` **exactly 64 bytes further along the section**
(0x100 → 0x140 past `vtable[0]`), while `.text` grows by a different amount.
Code and data cannot shift together, which is why the pc-relative displacement
moves at all. Arithmetic, all measured: `TABLE` +368, `kernel` 0x158b0 → 0x159c0
= +272, and 368 − 272 = **96** = the displacement shift `0x3f6af → 0x3f70f`.

### 5b. ⚠ THE `identity` PIN IS BLIND TO p36's TABLE — at `exact`, not just `norel`

**TASK_072_REVIEW M5, reproduced at TASK_073 with a shipped reproducer,
`controls/identity_probe.py`.** Take `unsafe.rs`, reverse the eight entries of
`TABLE`, change nothing else:

```
A_ship       n_fn=55 nopad=54 bytes=170
             md5_fn      (level `exact`) = 60e41a42f72a8d80143b5494d8b267a9
             md5_fn_norel(level `norel`) = d2cea805e5489d2f7f6e5d32fcd0e9cb
             small.bin checksum          = 195445626134389610
B_permuted   n_fn=55 nopad=54 bytes=170
             md5_fn      (level `exact`) = 60e41a42f72a8d80143b5494d8b267a9
             md5_fn_norel(level `norel`) = d2cea805e5489d2f7f6e5d32fcd0e9cb
             small.bin checksum          = 11308767923991984952

A vs B: md5_fn(EXACT) eq=True  md5_fn_norel(NOREL) eq=True  checksum eq=False
```

**The kernel is byte-identical and the program computes a different answer**,
because p36's whole dispatch mechanism is *data* outside the kernel symbol.

✅ **The gate is NOT unsound**: stage 2 compares every rung's checksum against
`model.py` and fails immediately. But *"the `identity` pin caught it"* (§5) and
*"`norel` is the level that says so precisely"* (§5a) both need the clause **"of
the kernel function's bytes"**. On this pattern the pin's coverage of the thing
the pattern is *about* is **zero at every level**, and what carries it is the
CHECKSUM stage — a different stage, and worth saying because a reader would
otherwise take `identity` as the guarantee that R5 computes what R4 computes.

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

— the pc-relative address of `TABLE`. `md5_fn_norel` is **equal**, so every byte
that is not a pc-relative displacement is identical, and `norel` is the level
that says so precisely **about the kernel function's bytes** (§5b).

⚠⚠ **THE CAUSE THIS SECTION USED TO GIVE IS FALSE AND IS WITHDRAWN**
(TASK_072_REVIEW M3). It read *"p36 is the first pattern here whose kernel
references a global object at all"*. Measured across the tree's `-O3` `unsafe`
kernels, **ten other patterns carry rip-relative operands** — p08 16, p06 5,
p27 5, p14 3, p13 2, and p02/p03/p04/p12/p38 one each — and **p06, p08 and p14
`lea` a `.data.rel.ro` object with exactly p36's instruction form**. Spot-checked
again at TASK_073 (`.temp/p36c/riprel_spotcheck.log`, `harness/asm.py`'s
pipeline):

```
p06   md5_fn eq=True   R4 lea 0x3f4dd(%rip),%rcx -> .data.rel.ro | R5 same disp
p08   md5_fn eq=True   R4 lea 0x3f579(%rip),%rcx -> .data.rel.ro | R5 same disp
p14   md5_fn eq=True   R4 lea 0x3f4d0(%rip),%rcx -> .data.rel.ro | R5 same disp
p36   md5_fn eq=False  R4 lea 0x3f6af(%rip),%r12 | R5 lea 0x3f70f(%rip),%r12
```

**All three hold `exact`, because their R4 and R5 displacements are EQUAL** —
the object moves with the kernel. So the true statement is:

> **p36 is the first pattern whose kernel references a global that R4 and R5
> place at DIFFERENT distances.**

⚠ **Do not read this as *"a kernel that references a global cannot hold
`exact`"* — three patterns do, today**, and the difference is not the linker's
whim. The mechanism is §5: p36's proof adds **64 bytes of `.data.rel.ro` and 26
bytes of `.text`**, two unequal amounts, so code and data cannot shift together
and the displacement cannot survive. p06, p08 and p14's proofs add nothing to
either section, so theirs does. **`exact` is unavailable for a reason that has
everything to do with the proof and nothing to do with what the proof COSTS to
run** — which is the honest form of the disclosure, and it is stricter than the
one it replaces.

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

⚠⚠ **THE SENTENCE THAT USED TO STAND HERE — *"And it is DEARER, which was not
the expected direction"* — IS FALSE ON THE COLUMN THE PROJECT'S OWN RULE NAMES,
AND IT WAS QUOTED INSIDE THE HASHED `idiom.why` AS THE JUSTIFICATION FOR
`forbidden[0]`.** TASK_072_REVIEW B2; this is p22's F3 recurring — a `forbidden`
entry whose stated reason is false of what it forbids.

The shipped control `r_match` (derived from R3 by exact-string substitution,
`controls/gen_controls.py`) measures **2035.7726 / 15923.0000** kernel-exclusive
against R3's 1710 / 13358. But **`match` has no callees at all** while the table
spelling dispatches 3.00 Ir per record outward (§0e), so the kernel-exclusive
column credits the table spelling for work it moved out of the symbol. On kernel
+ the eight dispatch targets:

| | small | large |
|---|---:|---:|
| `r_match` (kernel + targets) | 2035.7726 | 15923.0000 |
| shipped R3 (kernel + targets) | 2094.0000 | 16430.0000 |
| **difference** | **−58.2274** | **−507.00** |

**`r_match` is CHEAPER than the shipped R3**, by 58.2274 / 507.00 Ir per call,
and the program totals agree exactly (2067.9569 vs 2126.1998; 15958.7936 vs
16465.8089).

> ⚠ **THE FORBID STANDS, AND IT IS RE-GROUNDED RATHER THAN RE-PRICED.** Two
> routes were open — restate the `why` on the corrected column, or rest the
> entry on the grounds already in it that survive. **The first is not honest
> here**: an entry that reads *"forbidden, and by the way it is cheaper"* invites
> the reader to conclude p36 excluded the cheaper spelling to protect a number,
> which is exactly the accusation a `forbidden` list exists to pre-empt. So the
> entry now rests on the two grounds that were always in it and that a cost
> column cannot touch:
>
> 1. **`match op { .. }` is not a dispatch table.** It lowers to
>    `movslq (%r10,%r14,4),%r14 ; add %r10,%r14 ; jmp *%r14` — a jump table with
>    **all eight arms inlined and no call at all**. p36's entire subject is a
>    computed-target CALL; a rung without one is a different program, not a
>    cheaper spelling of this one. (That it is cheaper is *expected* once you
>    say this: inlining eight 14-byte bodies removes the call, the return and
>    the vtable load.)
> 2. **Its `Ir` is not an integer**, which destroys the `sweep-t*` control the
>    pattern's strongest half depends on — see below.
>
> **And the corrected number is published here rather than dropped**, because a
> `forbidden` entry whose cost claim quietly disappeared would be worse than one
> that was wrong.

`c_switch`, the same edit on the C side, measures **2411.5795 / 19099.0000**
against `c-gcc-h`'s 1574 / 12326 kernel-exclusive — and **on kernel+targets it
is still DEARER**, 2411.5795 / 19099.0000 against 2086.0000 / 16422.0000, by
**+325.58 / +2677**. So the direction claim survives for C and reverses for
Rust, and the reason is exactly §0e: `c_switch` also has no callees, but C's
table rung is paying gcc's `endbr64` on every dispatch and the Rust one is not.

⚠ **`r_match`'s `Ir` is not an integer, and that is itself the finding**: a jump
table's arms have different lengths (one falls through, the others need a `jmp`
back), so the executed instruction count becomes **opcode-dependent** where the
table spelling's is exactly constant. Measured over the `sweep-t*` band,
`r_match` reads 4147.0000 at t = 1, 2 and 4 and **4021.5980 at t = 8**, with
`Bi` dropping from 513089 to 450388; the table rungs read one number across the
whole band. So the `match` spelling would have destroyed §7's control as well as
the comparison.

---

## 7. ⚠ `Ir` EXACTLY CONSTANT, WALL CLOCK 3.13× — the pattern's strongest half

`inputs/gen.py`'s `sweep-t*` band varies **the number of distinct indirect-call
targets** (1, 2, 4, 8) at a fixed record count, and `sweep-mix*` holds the
opcode **multiset** exactly fixed and varies only its **order**. Both are read
by `controls/sweep_ir.py`, which uses `callgrind --branch-sim=yes` for `Bi`
(indirect branches executed) and `Bim` (mispredicted).

**The wall-clock half compares ONE BINARY on SEVERAL INPUTS**, so code layout is
identical by construction and no layout population is the relevant control —
p07's *"changing only the workload"* shape (RECAP finding 15, which is
`.memory/01-ladder.md` finding **8**; in that file 15 is p06, so the finding is
named here rather than numbered — TASK_072_REVIEW m5).
`controls/clayout.py` is shipped anyway for any future rung-to-rung `ns` claim.

⚠ **PROTOCOL, DISCLOSED BECAUSE IT CHANGED AT TASK_073.** The tables below were
first taken with `sweep_ir.py`'s original **blocked-by-blob** rep ordering — all
31 reps of one blob, then all 31 of the next — which is what
`.memory/03-measurement.md`'s interleave rule forbids (TASK_072_REVIEW m2).
`sweep_ir.py` now takes `--protocol {interleaved,blocked}` and defaults to
interleaved. **It changed no ordering and no conclusion**, which is itself the
useful result: three independent runs across two sessions and both protocols
give the same band, the same monotonicity and the same ratio to within 2%.

### 7a. ⚠ THE NOISE FLOOR IS NOT 4.19%, AND THE CORRECTION MAKES THE CLAIM STRONGER

The shipped floor was one measurement, `sweep_ir.py --floor 5` on
`sweep-mixrand`, blocked:

```
copy0 805.06   copy1 811.56   copy2 838.83   copy3 834.81   copy4 829.02
floor: min=805.06 max=838.83 spread=4.19% of min      <- DOES NOT REPRODUCE
```

**It does not reproduce, in either protocol, in either of two sessions.** Eight
independent floors, five byte-identical copies × 31 reps each, `n_iters`
rescaled to 200 000 (`.memory/03-measurement.md` finding 20a):

| blob | protocol | TASK_073 (this session) | TASK_072_REVIEW |
|---|---|---:|---:|
| `sweep-t1` | interleaved | **0.24%** | 0.31% |
| `sweep-t8` | interleaved | **0.19%** | 0.19% |
| `sweep-t1` | blocked | **0.34%** | 0.55% |
| `sweep-mixrand` | blocked | **1.22%** | 0.79% |

⚠ **This is the correction to be most careful with, because it makes p36's only
significance claim ~4–20× stronger, so it is re-derived rather than replaced by
the biggest available number.** Three things follow and they are separated on
purpose:

1. **The floor is a property of the BLOB, not of p36.** `mixrand` — the blob
   whose own behaviour depends most on the branch predictor — has the widest
   floor in both sessions and both protocols (1.22% / 0.79%). The `t` band, on
   which the headline is claimed, floors at **0.19–0.55%** across both
   sessions (0.19–0.34% in this one).
2. **Quote the floor of the band the claim is about.** The effect is measured on
   `sweep-t*`, so the denominator is 0.19–0.55%, not `mixrand`'s.
3. **The shipped form of the statistic is re-derived, not re-scaled.** With the
   band's own floor, `(3.130 − 1) / 0.0055 = 387×` at the conservative end
   (the worst `t`-band floor either session measured) and
   `(3.130 − 1) / 0.0019 = 1121×` at the sharp one — against the published
   **51.7×**. **The absolute form is
   plainer and is what should be quoted**: the band's ends differ by **897.85 ns**
   per call (421.47 → 1319.32), and five byte-identical copies of either end
   differ by **1.01 ns at the fast end and 2.51 ns at the slow end**.

**Band `t`, `unsafe` cell, `-O3 isolated`, 31 reps, min ns/call:**

| blob | targets | `Ir`/call | `Bim/Bi` (simulated) | TASK_073 interleaved | TASK_072_REVIEW interleaved | TASK_072 blocked |
|---|---|---:|---:|---:|---:|---:|
| `sweep-t1` | 1 | **3359.0000** | 0.0008 | **421.47** | 424.15 | 439.07 |
| `sweep-t2` | 2 | **3359.0000** | 0.4848 | 606.66 | 610.38 | 648.91 |
| `sweep-t4` | 4 | **3359.0000** | 0.7336 | 1194.04 | 1198.34 | 1255.87 |
| `sweep-t8` | 8 | **3359.0000** | 0.8581 | **1319.32** | 1320.48 | 1390.91 |
| **ratio** | | **1.0000** | | **3.130×** | 3.113× | 3.168× |

**`Ir` is identical to the instruction on all four, in all three runs; wall clock
is 3.11–3.17× apart**, monotone in the number of targets, against a floor of
0.19–0.55% on the same band.

**And it is not a Rust fact.** The same band on `c-gcc-h`:

| blob | `Ir`/call | min ns/call |
|---|---:|---:|
| `sweep-t1` | **3110.0000** | 373.78 |
| `sweep-t2` | **3110.0000** | 439.16 |
| `sweep-t4` | **3110.0000** | 768.87 |
| `sweep-t8` | **3110.0000** | 1182.23 |

**3.16×, against Rust's 3.13–3.17×.** The effect is a property of *an indirect
call with k targets*, measured twice in two languages from one script. (The C
column was taken blocked and has not been re-run interleaved; the Rust column
says what that protocol change is worth, which is ~1%.)

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

⚠ **The reason first given for this was wrong for the metric quoted**
(TASK_072_REVIEW m1). It read: *"the `t` band does not hold the opcode multiset
fixed, so this is not true by construction — it holds because all eight op
bodies are the same size (§6)."* The quoted number is **kernel-exclusive**,
which excludes the eight callees entirely, so **for that number it IS true by
construction** and §6's size measurement is not what carries it.

✅ **The stronger claim is true and is what §6 is load-bearing for: the PROGRAM
TOTAL is identical across the band too.** Measured (`.temp/p36c/ir_totals.py`,
`unsafe-O3-isolated`, the shipped `n_iters = 2000`):

```
blob                      calls   PROGRAM TOTAL  kern-excl/call  callees/call
sweep-t1.bin               2000         8635685       3359.0000      768.0000
sweep-t2.bin               2000         8635685       3359.0000      768.0000
sweep-t4.bin               2000         8635685       3359.0000      768.0000
sweep-t8.bin               2000         8635685       3359.0000      768.0000
```

**8,635,685 instructions, to the instruction, on all four** — and
`callees/call = 768.0000 = 256 × 3.00` on all four, which is the fact §6's
uniform op sizes actually buy. Quote the totals, not the kernel column, whenever
the *"not true by construction"* argument is being made.

**Band `mix`, same binary, opcode multiset held exactly fixed.** Interleaved,
31 reps, TASK_073; ⚠ **`sweep-mixrand6` is new at TASK_073** (see §7c):

| blob | `Ir`/call | `Bi` | `Bim` | `Bim/Bi` | min ns/call | (TASK_072 blocked) |
|---|---:|---:|---:|---:|---:|---:|
| `sweep-mixrun032` | 3359.0000 | 513089 | 16415 | 0.0320 | 506.46 | 509.40 / 531.10 |
| `sweep-mixrun016` | 3359.0000 | 513089 | 32415 | 0.0632 | 606.49 | 610.84 / 630.80 |
| `sweep-mixrun008` | 3359.0000 | 513089 | 64415 | 0.1255 | **441.29** | 448.06 / 464.14 |
| `sweep-mixrun004` | 3359.0000 | 513089 | 128415 | 0.2503 | 455.41 | 454.30 / 477.57 |
| `sweep-mixrun002` | 3359.0000 | 513089 | 256415 | 0.4997 | 462.85 | 465.67 / 489.40 |
| `sweep-mixrun001` | 3359.0000 | 513089 | 512415 | 0.9987 | 455.47 | 454.40 / 477.05 |
| `sweep-mixrand` | 3359.0000 | 513089 | 444415 | 0.8662 | 789.86 | 795.67 / 837.88 |
| **`sweep-mixrand6`** | **3359.0000** | **513089** | **447918** | **0.8730** | **1843.56** | — |

`Bim − 415 = 512000 / R` **exactly**, for every run length `R`, where 512000 is
the total number of dispatches and 415 is the driver's own indirect branches:
the simulator predicts perfectly inside a run and misses at every boundary.
(`mixrand` and `mixrand6` are permutations and have no `R`.)

⚠ **On this band the program totals differ, by at most 48 instructions in
8.6 million** (8,635,721 … 8,635,769) — the kernel and callee halves are
identical to the instruction, and the residue is one-time output formatting of a
different checksum value. Said here because §7's constancy claim is exact on
`sweep-t*` and *not* exact on `sweep-mix*`, and the difference is 0.0006%.

⚠⚠ **AND THE SIMULATED MISPREDICTION RATE DOES NOT ORDER THE WALL CLOCK. THIS
IS A CLEAN NEGATIVE ABOUT AN INSTRUMENT THIS PROJECT RELIES ON.**
`sweep-mixrun001`, which callgrind says mispredicts **99.87%** of indirect
branches, is among the **fastest** blobs. Callgrind's indirect predictor is a
**last-value BTB**; this box's Cascade Lake has a history-indexed indirect
predictor that learns a period-8 cycle perfectly and cannot learn a random
permutation.

⚠⚠ **AND THE SHARPEST FORM OF IT IS `mixrand` AGAINST `mixrand6`, WHICH HOLDS
`Bim` ALL BUT CONSTANT AND MOVES TIME BY 2.33×.** The version shipped at
TASK_072 compared 0.9987 against 0.8662 across 1.75× — a large `Bim` difference
and a moderate time difference. The pair below is much harder to explain away:

| blob | `Ir`/call | `Bi` | `Bim/Bi` | min ns/call |
|---|---:|---:|---:|---:|
| `sweep-mixrand` | 3359.0000 | 513089 | **0.8662** | 789.86 |
| `sweep-mixrand6` | 3359.0000 | 513089 | **0.8730** | **1843.56** |

**Identical `Ir`, identical `Bi`, simulated mispredict rates 0.8% apart — and
2.334× in wall clock.** `Bim` is not merely mis-ordered on this workload; it is
flat where time triples.

`.memory/00-environment.md` records that *branch behaviour IS measurable here by
simulation*, established on p07's **conditional** branches (`Bc`/`Bcm`). **p36
measures that the INDIRECT half (`Bi`/`Bim`) does not track wall clock at all**,
and that is a scoping correction to a standing project claim rather than a new
one. `Bi` is exact and useful (it counts); `Bim` is a model, and on this
workload the model is wrong in direction.

**What is robust, reproduced in three independent runs across two sessions and
clear of the band's 0.19–1.22% floors:** a *random* opcode order is
**1.78–1.81× slower** than the fastest structured one (`mixrand` against
`mixrun008`: 789.86/441.29 = 1.790 interleaved; 795.67/448.06 = 1.776 and
837.88/464.14 = 1.805 blocked) at an identical instruction stream, and a random
order with a **different permutation per window** is **4.177×** slower.
Within the structured orders, `run001`, `run002`, `run004` and `run008` are
mutually indistinguishable at the floor; `run016` (606.49) and `run032` (506.46)
sit above them, reproducibly. §7d bounds the mechanism.

### 7c. `sweep-mixrand6` — the disclosure turned into a measurement

⚠ **One design difference between the two bands was DISCLOSED at TASK_072 with
an asserted direction and no control.** In `sweep-mix*` all six windows carried
the **same** 256-opcode sequence (only the operand stream differed), so a
history-based predictor has 256 positions to learn; in `sweep-t*` each of the six
windows carries a **different** sequence, so it has 1536. The disclosure said
this makes the mix band **understate** the effect. That is a mechanism claim and
TASK_072_REVIEW built the control it needs; TASK_073 lands it in `inputs/gen.py`
as **`sweep-mixrand6`** — six *different* permutations of the *same* multiset,
one per window, same operand seeds as the rest of the band.

- **The disclosure is confirmed, and its magnitude is 2.334×** (789.86 →
  1843.56 ns) at an identical `Ir` and an identical `Bi`.
- **The band's own headline is now larger than `sweep-t*`'s**:
  `mixrand6 / mixrun008 = 4.177×`, on the band where `Ir`-constancy holds **by
  construction** (the multiset is fixed per window), against 3.130× on the band
  where it has to be argued (§7's ⚠ above). **That is the stronger of the two
  and it should be the one quoted**, precisely because it needs no argument
  about op-body sizes at all.
- Adding it cost **no re-measure**: `sweep-*` blobs are outside `input_sha256`
  (`measure.py:SKIP_INPUT_PREFIX`) and a `gen.py` edit that leaves every matrix
  blob byte-identical reports **GEN-ONLY**, not STALE. Measured, not assumed —
  §11d.

### 7d. The mechanism, bounded — and the two hypotheses p36's own inputs exclude

**TASK_072 left the non-monotone middle unattributed. It is still not fully
attributed, but three of the four candidate mechanisms are now excluded by p36's
own blobs, with zero fitted parameters.** All figures interleaved, 31 reps,
`unsafe-O3-isolated`, TASK_073.

1. **I-cache / DSB footprint is NOT the mechanism.** `sweep-mixrun008` touches
   **all eight** callees (multiset fixed, 32 of each per window) at **441.29 ns**;
   `sweep-t1` touches **one** at **421.47 ns**. Same binary, same blob shape
   (3096 bytes, 6 windows, 256 records, stride 516), same `n_iters`. **8 targets
   against 1 costs 4.70%. The effect being explained is 3.13×.**
2. **Switching FREQUENCY is not the mechanism either.** `sweep-mixrun001` is a
   period-8 cycle — a *different target on every single dispatch* — and runs at
   **455.47 ns**, indistinguishable from `run004` and `run008`.
3. **Callee identity is not the mechanism**: all eight bodies are 14 bytes and
   one operation (§6), and the multiset is held fixed across the whole mix band.

**What is left is predictability, and its SHAPE is zero-parameter**: once the
history predictor cannot learn the sequence, the last-value fallback is right
`(R−1)/R` of the time inside a run of length `R`, so a *longer* run mispredicts
*less*. That predicts `run032` faster than `run016` — which is exactly the
non-monotone middle — and it predicts the crossover to sit at a learnable period
of roughly 64, between R = 8 and R = 16. Both hold: `run008` 441.29 <
`run032` 506.46 < `run016` 606.49, reproducibly and in both protocols.

⚠ **LABEL WHICH HALF IS FITTED.** The *shape* above is zero-parameter and
predicts the ordering. Turning it into ns needs a per-mispredict penalty, and
the only way to get one here is to fit it from two points (`run016`, `run032`),
which gives ≈9–10 ns — **a fitted constant from two observations, quoted for
completeness and load-bearing on nothing.** This box has
`perf_event_paranoid = 3` and no hardware counters, so the penalty is not
independently measurable and p36 does not claim it.

---

## 8. The spelling spread, and what the prover costs

⚠ **SEARCHED BEFORE PUBLISHING ANY DIFFERENCE.** *"Degenerate as far as this
task searched"* has been false on five consecutive patterns and every time it
flattered a rung. Every control below is derived from a shipped rung by
exact-string substitution with an asserted hit count
(`controls/gen_controls.py`), and every R4-side candidate was **run through
Verus** before its number was used (`.tasks/TASK_026.md` §0.3).

⚠⚠ **AND AT TASK_072 THAT DISCIPLINE WAS APPLIED TO THE R4 SIDE ONLY.** The R4
side got two levers plus an inadmissibility probe and every candidate went
through Verus; the R3 side got **one** lever, `r3_idx`, which moves R3 the
**dearer** way. TASK_072_REVIEW B1 found the missing half in the first place a
reviewer would look. **Three R3-side levers were added at TASK_073** and the
cheapest of them beats the shipped rung. The full set:

| control | what it is | small | large | admissible R4? |
|---|---|---:|---:|---|
| `unsafe` (**shipped R4**) | hoisted count, unchecked | **1695** | **13343** | yes — `12 verified, 0 errors` |
| `r4_reslice` | shipped R4 + R3's record reslice — **the matched-spelling partner of the shipped R3** | 1700 | 13348 | **yes** — `v_r4_reslice`, `12 verified, 0 errors` (**TASK_073**) |
| `r4_cursor` | + the per-record cursor test (the R2-shaped unsafe rung) | 2717 | 21533 | **yes** — `v_r4_cursor`, `12 verified, 0 errors` |
| `r_fnptr` | C's bare `fn`-pointer table | 1311 | 10271 | **NO** — see §8a |
| **`r3_window`** | **R3 + the WINDOW resliced once at the top** | **1702** | **13350** | — (**cheapest in-contract R3 found**) |
| `r3_hdr4` | R3 + only the 4-byte header resliced | 1704 | 13352 | — |
| `r3_iter` | `r3_window` + `chunks_exact(2)` | 1705 | 13353 | — |
| `safe_tuned` (**shipped R3**) | hoisted count, record reslice, checked | **1710** | **13358** | — |
| `r3_idx` | R3 without the hoist | 2232 | 17464 | — |
| `safe_naive` (**shipped R2**) | naive indexing | **3498** | **27690** | — |
| `r2_nodead` | R2 with **only** the table access unchecked | 3498 | 27690 | — |
| `r_match` | R3 with `match op { .. }` | 2035.7726 | 15923 | — |
| `c_switch` | R1h with `switch (op)` | 2411.5795 | 19099 | — |

**Every one of the four R3-side controls is in contract by the gate's own
matcher** — `controls/r3_contract.py` pulls the backticked spellings out of
`spec.md`'s hashed block and runs `check.py::spelling_matches`, the same
definition stage 0 selftests:

```
=== r3_window  (11 required rust spelling(s), 6 forbidden)
  ... every required spelling: control=True  shipped=True ...
  divergences from the shipped R3: 0   forbidden hits: 0   `unsafe` in exec code: False
=== r3_hdr4 / r3_iter / r3_idx : the same, 0 / 0 / False
every control above is in contract by the gate's own matcher
```

⚠ **All four produce identical checksums on both blobs**, and the three added at
TASK_073 have **slope `13.00000`** exactly like the shipped rung, so the whole
spread among them lives in the intercept:

| R3-side member | law | small | large |
|---|---|---:|---:|
| `r3_window` | `13.00000·nrw + 38` | 1702 | 13350 |
| `r3_hdr4` | `13.00000·nrw + 40` | 1704 | 13352 |
| `r3_iter` | `13.00000·nrw + 41` | 1705 | 13353 |
| `safe_tuned` (shipped) | `13.00000·nrw + 46` | 1710 | 13358 |
| `r3_idx` | **`17.00000·nrw + 56`** | 2232 | 17464 |

**`r3_idx` is the one exception and it is the reason the span is not a per-call
constant**: it puts a bounds test back *inside* the loop, which is a change of
slope and not of prologue. Every other in-contract R3 found differs from the
shipped rung by a per-call constant of at most 8 Ir on 1710 — **0.47%**, and
**0.00000 Ir per record**.

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

**So this is the sixth instance of the *EVERY RUNG IS A SPELLING* finding
(RECAP finding 14 — named, not numbered: 14 in `.memory/01-ladder.md` is p13,
and the collision has already sent agents to the wrong finding), and its
sharpest.** Elsewhere the prover has excluded a *spelling* of a kernel — p16's
`chunks_exact`, p11's `core::slice::memchr`, p05's and p16's header reads. Here
it excludes the kernel's **central mechanism**, on the pattern whose entire
subject is that mechanism, and the price is a clean 3.00000 Ir per dispatch.

✅ **AND THIS IS THE ONE FIGURE THAT SURVIVES §0e UNCHANGED.** `r_fnptr` and the
shipped R4 dispatch the *same* 3.00 Ir per record outward, so on kernel + the
eight targets they read `13.00000·nrw + 31` and `16.00000·nrw + 31` and the
difference is **still exactly 3.00000**. Prologue and epilogue are
instruction-identical, both intercepts are 31, and the three instructions are
nameable: the fat-pointer index scale (`shl $0x4,%ecx`), the vtable load
(`mov 0x8(%rcx,%r12,1),%rcx`) and the ZST `self` (`mov $0x1,%edi`) against the
`fn` pointer's `mov %rax,%rdi`. **A reader who meets §0e or §8b first should not
assume p36's structural result fell; it is the thing that did not move.**

⚠ **A second reading of the same number, and it is the C-vs-Rust one —
CORRECTED AT TASK_073.** `r_fnptr`'s kernel-exclusive slope (10.00000) is
exactly `c-gcc`'s (10.00000), and `r_fnptr` carries the `op < NOPS` test that
`c-gcc` omits. **But that coincidence is an artefact of the kernel-exclusive
column** (§0e): on kernel+targets `c-gcc` is `14.00000·nrw + 39` and `r_fnptr`
is `13.00000·nrw + 31`, because gcc pays an `endbr64` on every dispatch that
rustc does not.

Against the *hardened* C rung `c-gcc-h`, the corrected comparison is
`16.00000·nrw + 38` against `r_fnptr`'s `13.00000·nrw + 31`, so a guarded Rust
`fn`-pointer table is **3.00000 Ir per dispatch cheaper — not the 2.00000 this
section shipped.** The clang column keeps it a language claim rather than a
compiler one: `c-clang` is `14.00000·nrw + 31` and `c-clang-h` is
`18.00000·nrw + 31`, so the ordering holds against both C compilers, and
**gcc's and clang's unguarded C rungs are now the same number** (14.00000
against 14.00000, where the kernel-exclusive column said 10 against 11). It is a
*control*, not a rung, and it is quoted as one.

⚠ **1.00 of the 3.00 is a CFI mitigation, not a language difference**, and a
cross-pattern C-vs-Rust table that quotes p36 must say so or it attributes
gcc's `-fcf-protection=full` to C. §0e.

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

⚠⚠ **AND THE SENTENCE THAT FOLLOWED THIS AT TASK_072 IS RETRACTED.** It read:
*"So the shipped R4 is R3's loop structure with the checks removed, which makes
`R3 − R4` a matched-spelling difference … the fixed-R4 bound
`R3ship − R4ship = +15.00 flat`."* **Both halves are wrong** (TASK_072_REVIEW
B1), and the two files that ship them **contradicted each other inside one
commit**: `gen_controls.py::c_r4_reslice`'s docstring called `r4_reslice`'s
difference *"the MATCHED-SPELLING safety number"* (+10) while this file called
`R3ship − R4ship` the matched-spelling difference (+15), **and the number that
shipped as the headline was the larger of the two.**

**1. `R3ship − R4ship` is NOT a matched-spelling difference.** Read the two
kernels: the shipped R4 carries a second induction variable and reads
`buf_get_unchecked(buf, off + p)` with `p = p + 2`, where R3 reads `rec[2 * t]`
out of a reslice. Those are not one loop written twice. The control that IS R3's
spelling with the checks removed is **`r4_reslice`**, and since TASK_073 it is a
**verified** R4 — so the matched-spelling number is

> **`R3ship − r4_reslice` = +10.00 flat, admissible to admissible.**

**2. The shipped R3 is NOT the cheapest in contract.** `r3_window` measures
`13.00000·nrw + 38` = **1702 / 13350** against the shipped `+46` = 1710 / 13358:
identical checksums, zero `unsafe`, 11/11 required spellings matched exactly as
the shipped R3 matches them and 0 forbidden hits. The mechanism is in the two
listings and needs no fitting: the shipped R3 bounds-checks `buf[off]`,
`buf[off+1]`, `buf[off+2]` and `buf[off+3]` **separately** (11 instructions —
`cmp %rsi,%rdx ; jae` then 3× `lea/cmp/jae`); reslicing the window first makes
`w.len() == len >= 4` visible and LLVM collapses all four into the single
reslice test (`mov %rcx,%rax ; add %rdx,%rax ; jb ; cmp %rsi,%rax ; ja`). The
loop body is unchanged, 13 instructions, identical.

**WHAT p36 PUBLISHES NOW — FOUR NUMBERS AND NO INTERVAL:**

**WHAT p36 PUBLISHES NOW — FIVE QUANTITIES AND NO INTERVAL**, named exactly as
`.memory/01-ladder.md` names them so that nothing is quietly redefined:

| quantity | value | what it is |
|---|---|---|
| **fixed-R4 bound, SHIPPED R3** (`R3ship − R4ship`) | `+15.00 flat` | `.memory/01-ladder.md`'s defined quantity — one number, bounding `inf(in-contract R3) − R4ship`. **Retained, as a loose bound and not as the headline.** |
| **fixed-R4 bound, CHEAPEST R3 FOUND** (`r3_window − R4ship`) | **`+7.00 flat`** | the same quantity, bounded tighter because a cheaper in-contract R3 exists. **This is the number to quote.** |
| **matched-spelling pair** (`R3ship − r4_reslice`) | **`+10.00 flat`** | one loop written twice, admissible to admissible |
| **R3-side span** | `1702 … 2232` / `13350 … 17464` | `r3_window` … `r3_idx`, **cheapest FOUND** on `small.bin` and `large.bin`, both named |
| **R4-side span** | `1695 … 2717` / `13343 … 21533` | **three** verified members: `unsafe` 1695, `r4_reslice` 1700, `r4_cursor` 2717 |

⚠ **Neither bound is a matched pair and neither pair is a bound**, and mixing
the two is exactly what B1 caught. `+7` bounds the CLASS with R4 held by fiat;
`+10` compares two spellings that differ in nothing but the bounds checks. They
answer different questions and both are published.

> ### ⚠ THE DECISION: KEEP THE SHIPPED R3, PUBLISH THE SPAN. Here is the argument, including against itself.
>
> **The alternative was to reship `r3_window` as R3.** Both routes are honest and
> the one not taken has a real case. What decided it is **not** cost:
>
> ⚠ **The cost argument against reshipping does not hold, and TASK_073 measured
> that rather than repeating it.** The stated objection was that reshipping
> stales `results/p36-vtable-dispatch.json` and re-takes the wall-clock block,
> and that p36's headline is a wall-clock claim. **p36's wall-clock headline is
> not in that record.** `measure.py::SKIP_INPUT_PREFIX` excludes every `sweep-*`
> blob from the matrix, and `measure.py::measurement_sources` excludes
> `<pattern>/controls/*.py` — so §7's bands are produced entirely outside the
> hashed measurement record. And a re-measure **was** taken this task (the
> `verus.rs` comment fix at §11a forced it): **0 of 32 cells moved a static
> column, a checksum or an `Ir`; only the wall block moved, by −0.90% to
> +0.98%, median −0.16%.** So reshipping would have cost ~8 minutes and nothing
> else. **The reasons below are what actually decide it.**
>
> 1. **Reshipping would make the published difference WORSE, not better.**
>    `r3_window − R4ship = +7` is **not** a matched-spelling pair — `r3_window`
>    reslices the window and the shipped R4 does not — so shipping it as R3 would
>    hand p36 a headline that mixes a spelling change with the safety axis, which
>    is exactly the defect being repaired. The matched pair on the shipped
>    spelling (+10) and the tightest bound (+7) are both publishable **without
>    moving a rung**, because they are properties of the in-contract CLASS and
>    not of which file is nailed down as R3.
> 2. **The window reslice has NO unsafe-side counterpart, which is the finding
>    rather than an obstacle.** It exists only to make bounds checks cheap; an
>    R4 has no checks for it to make cheap, so there is no `r4_window` to pair it
>    with and building one would be inventing a rung to justify a number.
>    ⚠ **This is a fourth measured instance of the R4-by-permission asymmetry**
>    (`.memory/01-ladder.md`, p03's `assert!(sp <= STACK_CAP)` where the unsafe
>    side gets `panic is not supported`): *the safe class reaches a spelling the
>    unsafe class has no use for.* p03's instance was about what Verus refuses;
>    p36's is about what an unchecked loop has no need of.
> 3. **The slope does not move, so nothing structural is at stake.** Every
>    in-contract R3 found is `13.00000·nrw + c` and every admissible R4 is
>    `13.00000·nrw + c`. The entire R3-side lever is **8 Ir per call on 1710 —
>    0.47% — and 0.00000 per record.** Reshipping would move a constant and leave
>    p36's structural result (§8a, §7) untouched.
> 4. **Precedent, and it is explicit.** p16 and p17 both ship an R3 measurably
>    off their own contract's floor and publish *"cheapest found"* **naming the
>    input** — never "minimum", because on p03 and p16 the cheapest spelling
>    changes with the blob. p36 now does the same.
> 5. **`r3_window` is the reviewer's spelling and has not been through the
>    gate.** TASK_072_REVIEW says so itself: it was measured and contract-checked
>    but never gated as a rung. Landing it as a rung **in the corrections task
>    for the pattern under review** would put an unreviewed rung in the tree
>    under cover of a review, which inverts the ordering PROTOCOL rule 3 exists
>    for.
>
> ⚠⚠ **AND THE DIRECTION TEST CUTS THE UNUSUAL WAY, SO SAY IT OUT LOUD.**
> Correcting `+15 → +7` (or +10) makes **safe Rust look cheaper**, which is this
> project's recurring headline direction and the one it keeps catching itself
> flattering. **A correction that flatters the house narrative deserves the same
> scrutiny as one that flatters a rung**, and that is why what ships is the
> **bound *and* the span** rather than a single new number, why the shipped-rung
> pair `+15.00` is retained in the table above rather than deleted, and why
> `r3_window`, `r3_hdr4` and `r3_iter` are in `gen_controls.py` where anyone can
> re-run them instead of in a report.

**Why NOT a pair interval, asked and answered.** `.memory/01-ladder.md` says the
project publishes none because the pair interval is **degenerate** — it collapses
onto the R3-side span, since every admissible R4 measures exactly `R4ship` — and
that *"it stops being degenerate the day somebody builds an admissible R4 that
moves"*, which p03 did. **p36's R4 side is non-degenerate too**, and has been
since TASK_072: `r4_cursor` is verified and 1022 / 8190 away. ⚠ **`v_r4_reslice`
does not change that**, because 1700 is *interior* to `1695 … 2717` and the
endpoints do not move; it changes the R4-side count from two verified members to
three and it makes the matched pair admissible-to-admissible.

**p36 still publishes no pair interval, and here is the measured reason.** The
interval would be `min(R3) − max(R4)` … `max(R3) − min(R4)` =
**`1702 − 2717 = −1015` … `2232 − 1695 = +537`**. Its lower endpoint reads
*"safe Rust beats unsafe Rust by 1015 Ir per call"* — manufactured by pairing the
cheapest R3 spelling against the dearest R4 spelling, which is **precisely the
artefact the `r4_cursor` disclosure above exists to refuse**, now wearing an
interval's authority. `.memory/01-ladder.md` finding 6 already settles the
arithmetic: differencing two class extrema bounds nothing in either direction.
**Four numbers, no interval.**

#### 8b-i. `v_r4_reslice` — the twin TASK_072 said it had not built, built

§11c used to read *"`r4_reslice`'s Verus twin was not built: it needs
`vstd::slice::slice_subrange` and the subrange-indexing proof … which is real
work this task did not do."* ⚠ **`slice_subrange` exists at the pinned vstd, and
the proof is four `assert` lines and two `invariant` lines.** Derived from
`verus.rs` by exact-string substitution
(`controls/gen_controls.py::v_r4_reslice`) it verifies **first run**:

```
=== v_r4_reslice: the matched-spelling R4, as an R5 twin -- TASK_073, on TASK_072_REVIEW M1
    .temp/p36c/controls/v_r4_reslice.rs
    verification results:: 12 verified, 0 errors
    [exit 0]
```

**Same obligation count as the shipped R5 (12), and no new trusted item in this
pattern** — `verus.rs` and `v_r4_reslice.rs` both carry exactly 4
`#[verifier::external_body]` items, 0 `assume`, 0 `assume_specification`,
0 `admit`. ⚠ **Stated precisely, because it is a TCB claim**: the reslice's
contract comes from `vstd::slice::slice_subrange`, whose body is `&slice[i..j]`
and which is `#[verifier::external_body]` **inside the pinned vstd** — i.e. in
the trusted base every pattern in this tree already stands on, not in p36's own
tally. Compiled with the same flags as the control:

```
binary                      n_fn  nopad  bytes   md5_fn(exact)  md5_fn_norel
r4_reslice   (R4 ctrl)        65     64    229   633cbdc6…      331866716dd75a12ed735fc73b20e938
v_r4_reslice (R5 twin)        65     64    229   ead7a406…      331866716dd75a12ed735fc73b20e938
md5_fn_norel(NOREL) equal: True     small/large checksums equal: True / True
```

**It holds p36's own `norel` identity pin**, and differs at `exact` for the same
`TABLE` `lea` reason the shipped R4/R5 pair does (§5a). So `r4_reslice` is an
**admissible R4**, the R4-side span has three verified members, and the
matched-spelling pair is admissible-to-admissible.

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

### 8d. What CFI costs — TWO points of the curve, and one of them was already in the matrix

⚠⚠ **THIS SECTION SHIPPED SAYING *"the real-world hardened answer for this bug
class is a compiler mitigation this matrix cannot price"*. THAT IS FALSE, AND IT
WAS FALSE WHEN IT WAS WRITTEN.** The matrix has been pricing **IBT landing pads
at 1.00 Ir per dispatch, in gcc's column only, undeclared**, since the pattern
was built — because Debian's gcc 13.3.0 defaults to `-fcf-protection=full`.
§0e has the measurement and the exact law (`1.00000·nrw + 1` Ir per call). So
p36 prices **two** points of the CFI curve:

| mitigation | what it enforces | cost, per dispatch | how it got here |
|---|---|---:|---|
| **IBT (`endbr64`)** | the target is a *declared* indirect-call landing pad | **1.00000** | **gcc's DEFAULT**, in the shipped matrix, undeclared until TASK_073 |
| `-fsanitize=cfi-icall` | the target has the *right function type* | 9.00000 | an opt-in control, below |

**The IBT point is the more interesting of the two and it is a finding, not an
erratum:** a compiler default put a control-flow-integrity mitigation into one
language column of a cross-language benchmark, nothing in `harness/build.py`
declares it, and it is invisible to every published figure because it lands in
the callees. On a pattern whose bug *is* a control transfer, that is the
mitigation the bug class is actually about. **⚠ Note also what IBT does NOT buy
here**: p36's out-of-table target is whatever data follows `TABLE`, so an
`endbr64` check would fault on it — but §0c measures that the unguarded rung
SIGSEGVs on 24 of 24 runs *without* IBT, so on this input set IBT changes the
diagnosis and not the outcome. `cfi-icall` is the one that reports (§0b).

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
*"here is the number, and here is why it cannot be a rung"*. ⚠ The IBT row above
is **not** in that category: it is in the shipped, measured matrix already.

### 8e. ⚠ THE CONVERSE OF §0b, and it turns the finding from a complaint into a result

**Added at TASK_073; TASK_072_REVIEW A0(a) is a clean negative worth keeping.**
§0b measures that every checker in this matrix names the **array read** and none
names the control transfer, and reads as a complaint about the checker set. The
converse is what makes it a result:

> **On p36 there is NO input on which the array read is in bounds and the call
> is wrong.** `TABLE[op]` for `op < 8` is always a correctly-typed
> `uint64_t (*)(uint64_t)`, and the only way to reach a wrong target is to index
> past the table. So ASan/UBSan (which name the read) and `cfi-icall` (which
> names the transfer) fire on **exactly the same input set**.

**The CFI column is therefore honest about VOCABULARY and adds nothing in
COVERAGE**, on this bug class. Stated the useful way: *the checkers this project
runs can name a control-flow bug only as the data read that precedes it; on this
bug class that costs no coverage, and the reason it costs no coverage is that
the two events are the same event.* ⚠ **Which is exactly why the finding does
not generalise**: a bug class where the two come apart — a corrupted vtable
pointer in a validly-sized object, a type-confused `&dyn` — would have the array
read in bounds and the call wrong, and this matrix would then be blind in
coverage and not only in vocabulary. p36 does not exhibit that class and cannot
speak to it.

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

> ⚠ **STATUS, TASK_078: still refused, and the REASON HAS MOVED. Read
> "What changed at TASK_077/078" at the end of this section before quoting
> anything above it** — the mechanism this section names as the refusal was
> fixed and is no longer the one that fires. p36 needs no change either way.

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

⚠ **AND IT IS A `harness/` LIMITATION RATHER THAN A SOUNDNESS REQUIREMENT —
REPORTED HERE, NOT FIXED** (TASK_072_REVIEW m7; TASK_073 was explicitly barred
from touching `harness/`). `harness/vparse.py::duplicate_names` keys items by
**bare name**, although `vparse.parse` already computes each item's enclosing
`impl` (`in_impl` / `inner_impl`, built there from `impl_spans`). Rust has no
ambiguity between `<OpN as Op>::apply` and `<OpM as Op>::apply`; the gate's
name→item map does. Keying by `(impl, name)` would admit the eight-impl
spelling, which is the shape a reader of `c/kernel.c` would write.
**It is not a one-liner and PROTOCOL rule 5's *"could this happen by accident?"*
test applies**: `spec.md`'s `verus.obligations` keys are bare names too, so they
would have to be qualified in every pattern, and the decoy attack the check
exists to stop (*"the gate used to key items by name and keep the last, so a
decoy could supply the pinned contract for the real item"*) has to keep being
stopped. **Queued for the manager; p36 needs no `harness/` change to ship.**

#### What changed at TASK_077/078 — the refusal moved, it did not lift

⚠ **Everything above is HISTORY from here down.** *"a pinned `verus.rs` may not
define one item name twice"* was true when it was written and is now the wrong
statement of a constraint that still exists.

**TASK_077 (RECAP "Owed" 20) did the keying work this section asked for.**
`vparse.duplicate_names(qualified=True)` keys by `(mod path, impl Self type,
name)`; `vparse.unique_names` hands back the **bare** name wherever it is
unambiguous and `Type::name` where it is not, so the eight impls key as
`Op0::apply` … `Op7::apply` and **no `spec.md` item pin in the tree moved** —
`unique_names` is the identity on 25 of 25 verus-bearing files. `check.py`'s
per-item contract stage and its `--verify-function` label were switched to it.
The decoy is still caught by both keyings, because a `mod` path is part of the
scope: `decoy::kernel` and `kernel` are two labels, so the pinned item **set**
fails with `added=['decoy::kernel']`, and that pin is inside `contract_sha256`.

**TASK_077_REVIEW B1 then measured that the spelling is still refused, by five
other stages.** `vparse.by_name` returns `{name: Item}` and stays bare-keyed on
purpose — a qualified duplicate would silently drop one of the two and re-open
the decoy — and it is called by `check_call_site`, `check_clause_deletion`,
`check_requires_strength`, `check_trusted_twins` and `derive_contract`, plus
`harness/limbs.py`. Each turns its `ValueError` into a failure, so the
eight-impl file now collects **five `FAIL`s and a fired limb** whose text still
reads *"duplicate item name(s): apply"*.

**TASK_078 measured the route to closing that and declined it**
(`.temp/p78/f1_probe.py`), because *"thread `qualified=True` through five call
sites"* is not what it costs:

1. `check_trusted_twins` and `limbs.py` build the twin's key by **string
   concatenation**, `TWIN_PREFIX + t.name`, from the bare name. In a
   qualified map that key misses on every trusted method inside an `impl`
   (`slb_twin_apply` looked up in a map holding `Op0::slb_twin_apply`), so
   every trusted item would report `NO TWIN` — a failure saying the opposite of
   the truth. Scope-aware key construction is a change to the **twin rule**,
   not to a dict key.
2. `harness/limbs.py` is a sixth consumer and is not a gate stage, but six
   patterns' published `NOTES.md` sentences rest on what it reports.
3. the clause-deletion and precondition-strength stages label every recorded row
   with the bare `it.name`, so an eight-impl file writes eight rows all labelled
   `apply` into `results/gate/*.json` — a record-schema change on top.
4. and **the qualification would not even separate the twins**: `vparse.
   impl_spans` only recognises `impl` at item position (`pre[-1] not in "{};"`),
   and `#[cfg(slb_twin)]` ends in `]`, so an attribute-preceded `impl` is
   invisible and its methods qualify to the bare name. Measured: two
   `#[cfg(slb_twin)] impl OpN { fn slb_twin_apply … }` blocks both qualify to
   `slb_twin_apply` and `unique_names` **raises** — on the very file the fix
   exists for.

**So the honest status is: the *contract* stage was widened, the *spelling* is
still refused, and RECAP "Owed" 20 is NARROWED rather than closed.** The
remaining work is those six call sites, the twin-key construction, the row
labels, and `impl_spans`' attribute gap. p36 still needs no `harness/` change,
and the const-generic shape is still the right one to ship.

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

⚠ **AND THE GENERATOR'S DOCSTRING OVER-CLAIMED WHAT THIS MUTANT SHOWS, WHERE
THIS PARAGRAPH DID NOT** (TASK_072_REVIEW m6, fixed at TASK_073).
`controls/mkmutants.py::m2` said the mutant exists *"to show … that `op_fold`
really is pinned to the dynamic types in `TABLE`"*. It does not: it never
reaches the kernel. ✅ **`m3` is the mutant that establishes that** — shift the
trusted `ensures` by one slot and the failure is `invariant not satisfied` in
the `run` relation, i.e. inside the kernel. So the property IS demonstrated, by
a different mutant than the one that claimed it, and the generator now says so.

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

**As shipped at TASK_072 (commit `207a83e`):**
`ffb7fc4a68e73342b3efe0c2e17b44ea0df5542c83822737a580d42991b3b1d2`

**As shipped at TASK_073 (this tree):**
`5bd8b4ad42f49d0f2d55c9f6ca107faa26523e1880a5cf6400bf060c8058ddc1`

⚠ **IT MOVED FIVE TIMES BEFORE TASK_072 SHIPPED, AND A SIXTH AT TASK_073.**
⚠ **THE HEADING HERE SAID *"IT MOVED TWICE"* AND THEN LISTED FIVE EDITS**
(TASK_072_REVIEW m4). Only the heading was wrong — the arithmetic was right, and
the reviewer recomputed `sha256(slb-contract block + "\n") = ffb7fc4a68e7…`
against the gate's `contract_sha256` and got a match. The edits, one by one:

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

**Edit 6** (`ffb7fc4a…` → `5bd8b4ad…`), **TASK_073, and it is the largest of the
six.** Two `why` fields were rewritten: `idiom.why` (17 379 → 23 286 chars) and
`identity[…].why` (1 656 → 3 860 chars). What went in: the `r_match` `why`
re-grounded on the two claims that survive B2 (§6b); the R3-side search, the
four published numbers and the argument for not reshipping (§8b); the corrected
`55 / 54 / 170` and `%r12` in place of `r4_cursor`'s `60 / 193` and `%rsi`; the
withdrawal of *"the first pattern whose kernel references a global at all"*
(M3); the vtable-slot cost and the `identity`-blindness scope clauses (M4, M5);
the kernel-exclusive/callee-column limitation and gcc's IBT (§0e); the measured
noise floors in place of `4.19%`.

### 11a-i. ⚠ THE DIRECTION TEST — and this time the diff is REAL

**PROTOCOL definition-of-done 6 says `git show HEAD:… | diff -` is VACUOUS on a
new pattern**: it compares the working tree to HEAD, a pattern lands in one
commit, so on a clean tree it always prints nothing and always looks like it
passed. That is why TASK_072 refused to cite it and why the two hashes above
were its only evidence. ⚠ **p36 is now committed at `207a83e`, so for TASK_073's
edit the command is real for the first time — run against THAT commit, not
`HEAD`** (`.temp/p36c/contract_diff.py`, `git show 207a83e:…`):

```
207a83e  contract_sha256 = ffb7fc4a68e73342b3efe0c2e17b44ea0df5542c83822737a580d42991b3b1d2
tree     contract_sha256 = 5bd8b4ad42f49d0f2d55c9f6ca107faa26523e1880a5cf6400bf060c8058ddc1

--- ENFORCED STRUCTURE (a change here is a change to what the gate checks)
  kernel / model / requires / ensures / driver / collapse / miri : identical=True
  verus.call_site / items / kernel_item / obligations / translate  : identical=True
  verus.obligations_note / twin_obligations / twin_obligations_note: identical=True
  verus.unsafe_justifications                                      : identical=True
  idiom.required   identical=True      idiom.forbidden  identical=True
  identity  O0: 'norel' -> 'norel'     O3: 'norel' -> 'norel'
            a: 'unsafe' -> 'unsafe'    b: 'verus' -> 'verus'
  note      identical=True

--- idiom.required / idiom.forbidden, ENTRY BY ENTRY
  required: 10 -> 10 entries, 19 -> 19 backticked spellings
  forbidden: 9 -> 9 entries,   9 ->  9 backticked spellings
  spellings REMOVED: none      spellings ADDED: none

--- what DID move
  idiom.why          17379 -> 23286 chars
  identity[0].why     1656 ->  3860 chars
```

> **Two prose `why` fields moved and NOTHING ELSE.** Not one enforced field
> changed: no `forbidden` entry removed or narrowed, no `required` spelling
> lost, no `verus` pin touched, no `identity` level relaxed, no `driver` or
> `collapse` pin altered. **Zero spellings removed, zero added, on either list.**

**The direction, stated against itself.** Edit 6 was made in the task that
corrects p36, so the suspicious shape would be *a declaration edited to make a
number defensible after the number was attacked*. Three things bear on it and
they are checkable rather than promised:

1. **Every edit is a RESTRICTION or a DISCLOSURE, never a relaxation.** The
   `r_match` entry lost its cost justification and kept the forbid — the entry
   binds exactly as many spellings as before and rests on narrower, structural
   grounds. `identity` stayed at `norel` in both slots.
2. ⚠ **The largest single correction runs in the direction that flatters this
   project's own narrative** (safe Rust cheaper: `+15 → +7`), and it is
   published **as a bound alongside a span, with the old number retained**,
   precisely because of that. §8b argues it.
3. **The stale text removed was flattering to nothing** — `60 / 193 / %rsi` was
   simply `r4_cursor`'s, i.e. a copy the §8b rung change never reached. Removing
   it makes the pin's justification checkable against the binaries, which it was
   not before.

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
**Re-checked at TASK_073 after the `gen.py` edits: 30 of 30 committed blobs
byte-identical**, plus the one new `sweep-mixrand6.bin`.

### 11d. ⚠ EDITING `inputs/gen.py` DID NOT FORCE A RE-MEASURE, AND THAT IS MEASURED

TASK_073 was told that `gen.py` is measurement-hashed, so fixing its residue
docstring (m3) and adding `sweep-mixrand6` (§7c) would force a re-measure and
should be deferred. **Measured, that is false**, and `harness/measure.py` says so
itself: `check_stale` has a **GEN-ONLY** branch — *"`inputs/gen.py` moved and
every matrix blob it produces is byte-identical: a sweep band, not a
re-measure"* — and **STALE is the only verdict that sets the exit code.** Run
immediately after the `gen.py` edits and before anything else:

```
$ harness/measure.py p36 --check-stale
GEN-ONLY    results/p36-vtable-dispatch.json    patterns/p36-vtable-dispatch/inputs/gen.py
            moved; 7 matrix blob(s) byte-identical -- no re-measure needed
2 record(s) examined, 1 STALE          <- the GATE record, which a gate re-run refreshes
```

The reason it works: `measure.py:SKIP_INPUT_PREFIX = "sweep-"`, so no `sweep-*`
blob is in `input_sha256` at all, and a band appended to `gen.py` leaves all
seven matrix blobs identical. `.memory/05-layout.md` had already measured this;
p36 is the second instance.

### 11c. What was NOT done

- **`controls/clayout.py`** is ported and its paths are checked (`.temp/p36/`,
  not `.temp/p14/`), but **no layout population was run**, because p36 publishes
  no rung-to-rung `ns` figure. Every wall-clock number here is one binary on
  several inputs. Run `clayout.py` before quoting any p36 `ns` number that
  compares two cells.
- **The per-mispredict penalty is fitted from two points** (§7d). The *shape* of
  the branch model is zero-parameter and predicts the ordering including the
  non-monotone middle; the ≈9–10 ns constant is not independently measured and
  nothing rests on it. `perf_event_paranoid = 3` on this box.
- **A cheaper admissible R4 was not constructed.** The R4-side search found none
  below 1695 and `r_fnptr` at 1311 is inadmissible, but `13.00000·nrw + 31` is
  *not shown* to be the floor.
- **No `r4_window`.** §8b argues that the window reslice has no unsafe-side
  counterpart worth building; that is an argument, not a proof that no such R4
  exists.
- **The `sweep-n` band was not re-run across all eight cells at TASK_073.** §4's
  twelve-point laws stand on their TASK_072 measurement plus the `small`/`large`
  endpoints reproducing exactly for every cell and control this task rebuilt.
- **The C column of §7's band `t` was not re-run interleaved** — only the Rust
  column was. The Rust column measures that the protocol change is worth ~1%.
- **`harness/` was not touched**, by instruction. Two items are queued for the
  manager: `vparse.py::duplicate_names` keying by bare name (§9b), and whether
  `results/*.json` should carry a callee or total `Ir` column (§0e).
- **`.memory/` was not touched**, by instruction — the corrections that belong
  there (the finding-1 scope clause, the p13 column rule, the M3 causal claim,
  the `Bim` scoping, `identity`'s coverage) are the manager's to land from this
  reviewed text.
