# TASK_102_REPORT — eight new catalogue rows probed, **eight refused**, and the reason generalises

**Role: research engineer.** Scratch and every artefact: `.temp/t102/`
(`NOTES.md`, `REBUILD.sh`, all sources and logs; binaries deleted per
constraint 6, all rebuildable from `REBUILD.sh`).

**Running count: this task was launched from 309** (TASK_102.md's closing
paragraph). `TASK_100` is in flight from 301. **Reconciling the two is the
manager's job and I have not attempted a global total.** What I add below is
listed as a count of *this task's* refutations, not as a new total.

---

## Headline

I probed **eight** candidate rows — the manager's four from §B plus four of my
own — and **refused all eight, every one on a measurement**. Six died on
**probe 1 or probe 2**; two died on the harm.

⚠⚠ **And the eight refusals have ONE cause, which is the answer to the
manager's question 3 and, I think, the answer to question 1:**

> **This instrument can price a safety property if and only if some rung emits
> it as a COMPARE-AND-BRANCH and another rung omits that branch.** Every
> property I probed that is enforced by the *type system* (alignment), by a
> *library contract* (comparator transitivity), by an *absent operation*
> (format string), by a *resource limit no rung emits* (stack depth), or by a
> *compiler diagnostic* (return-of-local) has **no machine-code footprint at
> all** — and probe 2 says so, in normalised disassembly, every time.

That is not a new rule; it is the catalogue's own ladder test, restated in the
direction that predicts. It also **retires the "fifteenth `index >= len` is a
high bar" framing** — see question 3.

**Two instrument defects fell out and both are reusable:**

1. ⚠ **`.temp/t94/knorm.py` — probe 2's own tool — counts inter-function
   alignment PADDING**, and therefore reported two kernels that are the *same
   program* as 24 insns vs 22 insns, `!=`. That is a **false negative on a KILL
   criterion**, the third instrument defect in probe 2's history after the
   object-file false positive (TASK_086) and the linked-md5 false negative
   (TASK_094). Fix is four lines — truncate the listing at the last `ret`;
   `.temp/t102/b4_norm.py` does it and is a drop-in.
2. ⚠ **`harness/check.py` sets no `MIRIFLAGS`, and Miri's default alignment
   check is ADDRESS-based and therefore SEED-DEPENDENT.** Measured: the *same
   source*, `ptr::read::<u32>` at offset 1, is Miri-clean on `-Zmiri-seed=0` and
   `2` and **Undefined Behavior** on `1` and `3`; and on default flags it is
   clean at `off=1` and UB at `off=4`. Only `-Zmiri-symbolic-alignment-check`
   catches both deterministically. Nothing in the tree depends on this today
   (no pattern models alignment), but a gate row reading "Miri clean" for an
   alignment property would be a coin flip.

---

## The eight candidates, ranked, each with its novelty claim RUN

Ranking is by how close each came to being buildable. **All eight are REFUSE.**

---

### 1. B3 — recursion depth / stack exhaustion on nested input · **REFUSE as a row, KEEP as a finding**

**The C pattern.** A recursive-descent parser over nested input with no depth
limit; the fix is one compare in the descent function.

**Precedent — fetched, not cited from memory.** cJSON
(`raw.githubusercontent.com/DaveGamble/cJSON/master/`, saved as
`.temp/t102/cjson_c.txt`, `cjson_h.txt`, `cjson_ch.txt`):

- `cJSON.h:134-138` — `/* Limits how deeply nested arrays/objects can be before
  cJSON rejects to parse them. This is to prevent stack overflows. */`
  `#ifndef CJSON_NESTING_LIMIT / #define CJSON_NESTING_LIMIT 1000 / #endif`
- `cJSON.c:1502` (`parse_array`) and `cJSON.c:1667` (`parse_object`) — the
  guard itself: `if (input_buffer->depth >= CJSON_NESTING_LIMIT) { return
  false; /* to deeply nested */ }`
- `CHANGELOG.md:294` — *"Prevent a stack overflow by specifying a maximum
  nesting depth `CJSON_NESTING_LIMIT`"*.

My probe's `k_hardened` is that guard, and it independently landed on the same
constant, 1000.

**Bug class.** Resource exhaustion / DoS. **The tree HAS this class — `p22`.**

**The novelty claim, stated so it could be false, and RUN.**

> *"Verus can prove this recursive descent terminates, and the verified binary
> still dies of stack exhaustion — so R5's proof does not carry the property
> the pattern is about."*

✅ **TRUE, and this is the one thing worth keeping.** `.temp/t102/b3_verus_rec.rs`,
a recursive-descent depth counter with `decreases buf.len() - i`:

```
verification results:: 3 verified, 0 errors
n=200000   rc=0    depth-sentinel n=200000 r=199999
n=1000000  rc=134  thread 'main' (1263635) has overflowed its stack
                   fatal runtime error: stack overflow, aborting
```

**Probe 1 — a rung boundary?** Only between `R1` and `R1h`. Every Rust rung
crashes; the depth check is in no rung's automatic behaviour. That is `p22`'s
situation exactly, and `p22` shipped, so it is not fatal on its own.

**Probe 2 — do the rungs differ as machine code? ⚠⚠ NO, AND THIS IS THE KILL.**
In `b3_rust_O3`, `k_safe_naive`, `k_safe_tuned` and `k_unsafe` **all three
`call 14c80 <…g_naive>`** — the same function. `g_tuned` and `g_unsafe` do not
exist as symbols; identical-code-folded. The shared body has **no bounds check
and no panic edge**: the recursion's own `while j < buf.len()` already
discharges the index. **R2 = R3 = R4, one rung.** A shipped p-row would publish
`R3 − R4 = 0.00` from *byte-identical rungs* — the exact artefact the ladder
test's `p45` block says only probe 2 can tell from "safety is free".

**Probe 3 — the cost, on a new axis.** The one axis where B3 has content is
**depth headroom**, and it is measured two independent ways that agree to 0.5%
— the frame read from disassembly, and the survival depth bisected by running:

| rung | recursive frame (disasm) | 8 MiB ÷ frame | measured max depth |
|---|---|---|---|
| `c-gcc -O2` `g_naive` | 4 push + `sub $0x8` + 8 ret = **48 B** | 174 763 | **173 950** |
| `c-gcc -O0` `g_naive` | 1 push + `sub $0x40` + 8 = **80 B** | 104 857 | **104 523** |
| `rust -O3` `g_naive` (all three rungs) | 5 push + 8 ret = **48 B** | 174 763 | **173 950** |
| `rust -O0` | — | — | **74 768** (112 B/frame) |
| `verus -O3` `parse_group` | 3 push + 8 ret = **32 B** | 262 144 | **260 925** |

⚠ **What my probe does not model:** its `parse_group` returns `(usize, u32)`
and the C/Rust rungs return `size_t` with an out-parameter, so the Verus row's
32-byte frame is *a different function*, not the same kernel compiled by Verus.
The 48 B ≡ 48 B comparison between C and Rust *is* like-for-like.
**Consequence: the safe rung and the unsafe rung have the SAME headroom, so
this axis has no rung boundary either.**

**Probe 4 — vstd.** Not reached; the recursion needs no vstd exec spec, and the
`decreases` verified first attempt.

**Probe 5 — shipped shape.** The probe already *is* the shipped shape
(`(buf, off, len) -> u64`, payload from a blob, no saved pointer).

**The harm, RUN, positive control firing.** `.temp/t102/b3_harm.log`, 84 cells,
gcc+clang × {plain, ASan, UBSan} × O0/O2 × {naive, hard} × depth
{1e3, 1e5, 1e6}, positive control `ASan=2` in every ASan build:

| | plain | ASan | UBSan |
|---|---|---|---|
| naive, depth 1e6 | **`rc=139` SIGSEGV**, gcc and clang, O0 and O2 | **`stack-overflow`**, 3 report lines | silent (gcc), `stack-overflow` (clang) |
| hardened, depth 1e6 | rc=0 | clean | clean |

**Driver hostability.** Fine.

**VERDICT — REFUSE the row; the manager should take the Verus sentence as a
finding.** The class is `p22`'s, the Rust ladder is one rung by measurement,
and the depth axis is flat across the safe/unsafe boundary. But
***"a `decreases` proof is a proof about the MATHEMATICS of termination and says
nothing about the STACK; `3 verified, 0 errors` and `fatal runtime error: stack
overflow` are the same binary"*** is a real result, it is `p47`'s shape (the
proof certifies a program that fails the property a reader assumes it covers),
and it costs one paragraph in the synthesis rather than a pattern.

---

### 2. C3 — integer division by an attacker-controlled divisor · **REFUSE**

**The C pattern.** `acc += sum / count` where `count` is a per-record wire
field; `R1` omits `if (count == 0)`. The `INT_MIN / -1` case traps the same way.

**Bug class.** UB that is not memory unsafety — **the tree HAS it, `p18`**,
including `p18`'s detector story verbatim (UBSan names it, ASan silent).

**The novelty claim, and it is FALSE at the pin.**

> *"The tree prices Rust's bounds check fourteen times and Rust's OTHER
> automatic check — division by zero — zero times, so R4 has a new lever."*

The first half is true (`grep -rl 'unchecked_div\|unchecked_rem' patterns/`
returns nothing). ⚠⚠ **The second half is false: `unchecked_div` does not exist
at the pin.** rustc 1.97.1:

```
error[E0599]: no method named `unchecked_div` found for type `u32`
error[E0554]: `#![feature]` may not be used on the stable release channel
error[E0635]: unknown feature `unchecked_div`
```

The only stable lever is `unreachable_unchecked`, which is an **annotation, not
an operation** — an R4 that is "the safe program plus an assumption" prices the
assumption, not the unsafe idiom.

**Probe 1/2.** A boundary does exist and the rungs do differ: C `k_div` 21 insns
vs `k_div_guard` 23 (gcc -O2); clang 50 vs 24. Rust `k_safe` 28, `k_guard` 28,
`k_unsafe` 25. **This is the only candidate of the eight that passes probe 2.**

**The harm, RUN, positive control firing** (`.temp/t102/c3_harm.log`, 50 cells):
the behaviour matrix has **one column**. Every rung dies loudly on the same
input — C `rc=136` SIGFPE (gcc and clang, O0 and O2), safe Rust `rc=101`
`panicked at 'attempt to divide by zero'`, **unsafe Rust `rc=136` SIGFPE**.
There is **no silent case anywhere**, so the pattern cannot produce the kind of
result `p02`/`p46` produce.

**VERDICT — REFUSE.** Reason I would defend under review: **the unsafe rung has
no operation, only an assumption, and the behaviour matrix has one column** —
`p45`'s finding ("no unsafe rung with a job") reproduced on a third row, now
with the sharper cause that the intrinsic is *unstable at the pin* rather than
semantically absent.

---

### 3. C2 — unaligned load `*(uint32_t*)(buf+off)` · **REFUSE, killed by probe 2 twice**

**The C pattern.** The universal wire-parser idiom: cast a byte pointer to a
scalar pointer and dereference. UB when the offset is not a multiple of the
scalar's alignment; `memcpy` / `get_unaligned()` is the portable fix.

**Bug class.** Alignment UB — **absent from the tree.**

**The novelty claim, stated so it could be false, and RUN.**

> *"Safe Rust is alignment-IMMUNE (`u32::from_le_bytes` takes a `[u8;4]`, which
> has alignment 1), unsafe Rust reintroduces the bug (`ptr::read` requires
> alignment, `read_unaligned` does not), so the boundary is compile-time —
> `p08`'s shape."*

The *expressiveness* half is true. **The measurable half is false.**

**Probe 2, on the C side (gcc):** the UB spelling and the portable fix are
**normalised-identical**.

```
gcc -O2:  k_cast 19 insns 437d7f5cbf20   k_memcpy 19 insns 437d7f5cbf20   ==
gcc -O3:  k_cast 19 insns b8fdcd83ebdd   k_memcpy 19 insns b8fdcd83ebdd   ==
gcc -O3:  k_cast_sum 49 ea4a1d9f2624     k_memcpy_sum 49 ea4a1d9f2624     ==
```

**Probe 2, on the Rust side:** so are the two unsafe spellings.

```
rustc -O3: ptr::read::<u32>  58 insns 9fc2e1d8889a
           read_unaligned    58 insns 9fc2e1d8889a       ==
```

clang is the only cell where anything moves — `k_cast` 55 vs `k_memcpy` 58 —
i.e. **the UB spelling is 3 instructions CHEAPER on one compiler and free on the
other**. There is nothing to price.

**The harm, RUN, positive control firing** (`.temp/t102/c2_harm.log`, 84 cells):
**never observable without a sanitizer** — 36 plain-build cells, all `rc=0`, at
O0/O2/O3 on both compilers. The two `movaps`-family instructions gcc -O3 emits
inside `k_cast_sum` are also inside `k_memcpy_sum`, whose bytes are identical,
so they **cannot** be alignment-requiring memory loads — a claim I take from the
byte identity rather than from reading the mnemonic. UBSan's `alignment` check
fires deterministically on `cast`/`cast_sum` at `off=1` and is clean at `off=4`
and for both `memcpy` spellings.

**Probe 4 — vstd, grepping `std_specs/` SPECIFICALLY.** `read_unaligned` occurs
in the pinned vstd **exactly once, in a doc comment** (`vstd/raw_ptr.rs:128`);
there is no `assume_specification` for it and none for `ptr::read`, in
`std_specs/` or anywhere. ⚠ A miss is necessary and not sufficient (`p35`) — but
here it is **corroborated by a run already in the tree**: `p38`'s shipped hashed
`why` records that at the pinned vstd *"`as_ptr`, `add` and `read_unaligned` are
each `is not supported`"*, which is why `p38` ships its own `read_unaligned`
variant as the control `r4_pun` rather than as a rung. C2's R4 would have no
verifying twin.

⚠⚠ **And the tree has already CONSIDERED AND EXCLUDED this axis, by design.**
`p38`'s hashed `why` says so in as many words: *"WHY `rlen` COUNTS 32-BIT UNITS:
every record header then sits at an even word index, so the punning load is
ALIGNED. Misalignment is a second, different undefined behaviour, and UBSan's
`alignment` check would otherwise take credit for catching p38's bug when it
cannot see it at all."* So a C2 row would be **re-opening a sub-case a shipped
pattern deliberately designed out** — and my measurements say the reason it was
designed out (UBSan is the only thing that sees it) is the same reason it cannot
carry a row of its own.

**VERDICT — REFUSE.** Reason: **on x86-64 alignment has no machine-code
footprint** — every spelling of the load is the same `mov`, measured on both
compilers and in Rust — so the pattern would publish a `0.00` that means "one
rung"; its harm is invisible to everything except one UBSan check; its R4 has no
vstd route; and `p38` already excluded the axis on purpose. Delivered instrument
finding: **Miri's alignment verdict is seed-dependent** (above).

---

### 4. B1 — format string, `printf(user_controlled)` · **REFUSE**

**Bug class.** Uncontrolled format string. Absent from the tree.

⚠ **The manager's guessed shape and MY guessed kill were both wrong, and I ran
both.**

- Manager's guess: *"safe Rust cannot express it, so R2/R3 are 'impossible'
  rather than 'checked' — is that a degenerate ladder?"* That half is fine;
  `p08` ships exactly that shape.
- **My guess, REFUTED:** *"Verus at the pin cannot type a C variadic, so there
  is no R5"* — `p36`'s `fn(u64) -> u64` result made this look likely.
  `.temp/t102/b1_verus_variadic.rs` puts `extern "C" { fn printf(fmt: *const
  u8, ...) -> i32; }` outside `verus!` behind an `external_body` wrapper:
  **`1 verified, 0 errors`.** Verus takes it.

**What actually kills it, measured, two ways.**

1. **The harm is NONDETERMINISTIC.** The `%p` read primitive leaks stack and
   libc addresses; three runs of one binary give
   `0x7ffd829e3b2c` / `0x7ffdecfa023c` / `0x7ffc19c2f39c`, and it is stable only
   under `setarch -R`. A kernel whose output depends on ASLR cannot be checked
   against `model.py`. The `%n` **write** primitive is separately dead at the
   gate's own optimisation level: `-O2` (Ubuntu's `_FORTIFY_SOURCE` default)
   gives `*** %n in writable segment detected ***`, `rc=134`; it works only at
   `-O0`. `%s` is `rc=139`.
2. **Probe 3 — the "safety fix" is a different glibc code path, not a check.**
   Callgrind, 20 000 calls, output to `/dev/null`:
   `printf(u)` **6 107 234 Ir** vs `printf("%s", u)` **9 347 233 Ir** →
   **+162 Ir per call**, roughly **27× the largest bounds-check tax in the
   tree**, with **none of it a safety check** — it is glibc re-scanning and
   copying through the `%s` conversion. Statically the two callers are 7 and 6
   instructions, and the *fixed* one is the smaller. This is `p13`'s "the rungs
   call different libc routines" defect with the entire measured quantity
   inside libc.

**VERDICT — REFUSE.** Reason: **the harm is an output-channel property and is
ASLR-nondeterministic, and the cost axis measures glibc's `%s` converter rather
than a safety check.** Not a category error about the ladder — a category error
about the *measurement*.

---

### 5. D6 — dangling pointer to a local (stack use-after-return) · **REFUSE** *(mine)*

**The C pattern.** A helper builds a scratch array in its own frame and returns
a pointer to it; the caller reads it after another call has reused the frame.
CWE-562.

**Bug class.** Temporal — **the tree has `p27`, but `p27` is HEAP**; a
stack-temporal bug is a different mechanism (safe Rust rejects it at compile
time rather than by `p27`'s runtime `Option`/`None` route), so the class is
arguably new.

**The novelty claim, RUN, and it dies immediately.**

> *"The C rung exhibits the bug — a silent wrong answer — with no flag."*

⚠ **FALSE, and it fails before the ladder even starts: BOTH compilers diagnose
it by default, with no flag asked for.**

```
gcc   : d6_saur.c:19:12: warning: function returns address of local variable
                          [-Wreturn-local-addr]
clang : d6_saur.c:19:12: warning: address of stack memory associated with local
                          variable 'scratch' returned [-Wreturn-stack-address]
```

and gcc then **does not exhibit the bug at all** — `rc=139` SIGSEGV at O0 *and*
O2, because gcc lowers the returned local address to a trap. Only clang is
silently wrong, and its answer differs between O0 (`115254102125611`) and O2
(`10658508300921776435`). ASan on clang names it `stack-use-after-return`, 2
report lines, **without** `detect_stack_use_after_return=1`.

**VERDICT — REFUSE.** Reason: **the C rung's bug is a default compiler warning,
so the pattern's premise — an idiom a working C programmer ships — is false at
this toolchain**, and one of the two C compilers cannot exhibit it.

⚠⚠ **DISCLOSURE — one positive-control cell did NOT fire, and I only noticed
because I grep every log.** `d6_clang_asan_O2 pos` returned `rc=0 ASan=0`. The
mechanism: my control was `volatile uint8_t s = p[32];`, which makes the
**store** volatile, not the **load**, so clang -O2 is entitled to fold the
undefined load to 0 and delete it — leaving ASan nothing to instrument.
**ASan in that same binary was demonstrably live**: the `dangle` row of the same
build reports `ASan=2 SUAR=2`. Corrected control `.temp/t102/ctl_fix.c` uses a
`volatile uint8_t *` and fires **`ASan=2` on gcc and clang at -O2**. The other
seven ASan configurations across all eight candidates used the same spelling and
**did** fire, so no verdict moves; but *"a `volatile` destination does not force
a load"* belongs in the harm-probe recipe next to `env -u LD_PRELOAD` and
"grep, never head".

---

### 6. B2 — VLA / `alloca` with an attacker-derived size (stack clash) · **REFUSE**

**Bug class.** Stack clash. Absent from the tree.

**Claim 1, RUN — and the manager's worry is only HALF right.**

> *"gcc on this box emits stack probes by default, so the clash is mitigated."*

⚠ **Verified from the BYTES, not from the prose** (`-Q --help=common` says
`[enabled]`, and the alignment-control lesson says do not compute from prose).
gcc's `f_vla` prologue at `-O2`, default flags:

```
sub    $0x1000,%rsp
orq    $0x0,0xff8(%rsp)      <- the probe
cmp    %rcx,%rsp
...
orq    $0x0,-0x8(%rsp,%rdx,1)
```

With `-fno-stack-clash-protection` the probes vanish (`sub %rax,%rsp` alone).
⚠ **And clang emits NO probes at all by default** (`mov %rcx,%rsp`) — so the
manager's mitigation claim is true of gcc and **false of clang**.

**Claim 2, RUN — and it is what kills the row.**

> *"An attacker-sized VLA can jump the guard page and write into memory that is
> not the stack."*

**FALSE on this box, in every configuration, including the unprobed ones.**
`.temp/t102/b2_harm.log`, 4 builds × {`touch`, `walk`} × 4 sizes, with a 16 MiB
`malloc`'d witness region memset to `0xA5` and re-scanned afterwards:
**every oversize case is a plain `rc=139` SIGSEGV and every surviving case
reports `witness_dirty=0`.** Nothing ever lands in mapped memory — 64-bit ASLR
leaves an unmapped gap below the stack, so a clash needs a mapping placed there
that a single deterministic kernel cannot arrange.

**Probe 3 — and this is the second, independent kill.** The manager's own guess
names it: *"a rung difference in ALLOCATION STRATEGY"*. Safe Rust has no VLA, so
R2/R3 must heap-allocate, and the measured gap would then be `malloc`+`free`
against a `sub %rsp` — **`p28`'s trap verbatim**, where `108.4%` of the
published gap was the allocator and the bounds check was `9.00` with the
*opposite* sign.

**VERDICT — REFUSE.** Reason: **the harm is a plain SIGSEGV with no clash
observable in 24 of 24 cells, and the cost axis would be an allocator
difference rather than a safety difference.**

---

### 7. C1 — `qsort` with a non-transitive comparator · **REFUSE** *(mine)*

**The C pattern.** The textbook subtraction comparator
`return *(int*)a - *(int*)b;`, which overflows and is therefore not a valid
ordering. Historically this drove glibc's `_quicksort` insertion-sort tail —
whose backward walk `while (cmp(run_ptr, tmp_ptr) < 0) tmp_ptr -= size;` has no
lower bound and relies on a min-at-front sentinel — off the front of the array.

**The novelty claim, stated so it could be false, and RUN.**

> *"C is MEMORY-UNSAFE with a broken comparator (libc walks out of bounds),
> while safe Rust's sort is documented to be merely WRONG — so the boundary is
> that C's UB is Rust's wrong answer."*

⚠ **FALSE on this box, and the mechanism is a libc version.**
`.temp/t102/c1_harm.log` (48 cells: gcc+clang × {plain, ASan, UBSan} × O0/O2 ×
{subtraction comparator, cyclic mod-3 comparator, random large magnitudes}) and
`.temp/t102/c1b.log` (32 cells: a comparator that **always returns −1**, the
most adversarial possible, at n ∈ {4, 8, 16, 24, 64, 1000, 4096, 100000}):
**zero AddressSanitizer reports in all 80 cells**, with the positive control
firing `ASan=2` in **all four** ASan builds. The only thing any detector sees is
the comparator's own signed overflow, which is `p45`'s refused class.

**The mechanism, fetched.** `stdlib/qsort.c` at tag `glibc-2.39`
(`raw.githubusercontent.com/bminor/glibc/glibc-2.39/stdlib/qsort.c`, 407 lines,
saved as `.temp/t102/glibc239_qsort.c`): `qsort` is now **mergesort with a
heapsort fallback**, and every loop bound in it is a *count or an index* —
`while (n1 > 0 && n2 > 0)` in the four merge specialisations,
`while (2 * k + 1 <= n)` in `siftdown` — never a comparator-driven pointer walk.
The sentinel-dependent insertion sort is gone. `ldd --version` → **glibc 2.39**.

**VERDICT — REFUSE.** Reason: **the class was real and this box's libc has
fixed it**; C and safe Rust are now in the same place (wrong output, no UB), so
there is no boundary. This is a *dated* refusal — on a glibc older than 2.37 the
probe would very likely fire — and the row should be marked as refused **for
this box**, not in principle.

---

### 8. B4 — TOCTOU / double fetch of a length field · **REFUSE, fastest kill**

**The novelty claim, stated so it could be false, and RUN.**

> *"Two reads of the same length field, with the check between them, is a bug
> adjacent to `p38` but temporal rather than aliasing."*

**Probe 2 kills it outright.** `.temp/t102/b4_double_fetch.c` at gcc -O2:

```
k_double_fetch      22 insns  norm-text=7b0e28cdead4
k_single_fetch      22 insns  norm-text=7b0e28cdead4    ==   ONE RUNG
k_double_fetch_vol  23 insns  norm-text=f7e6122f624d    (volatile only)
```

The second fetch is CSE'd into the single `mov (%rdi),%edx`. **In a
single-threaded kernel whose payload is a file blob, the two reads cannot
differ.** The only spelling that keeps the second load is `volatile`, and a
`volatile` re-read is meaningful only with a concurrent writer, which this
harness cannot provide without breaking `model.py`'s determinism.

**And the manager's own worry was right:** it *is* `p38`. `p38`'s
`spec.md:78-79` semantics block reads
`if REC_LEN(sc+i) > room: REC_SET_LEN(sc+i, room)  # THE CLAMP, every rung` /
`n = REC_LEN(sc+i)  # THE RE-READ` — a length field written in place and read
twice. Its hashed `why` even explains the getter/setter split: *"a compiler is
entitled to answer the second call from the value the first returned. Fold the
two calls into one local and the question cannot be asked; that variant is
shipped as the control `c_once`."* **`p38` already owns the only spelling in
which the second read differs, and already ships the folded control that my
probe rediscovered.**

**VERDICT — REFUSE**, and this is the one I would have refused on argument if
the probe had cost anything; it cost one compile.

⚠ **This candidate is where `knorm.py`'s padding defect surfaced** — it reported
24 vs 22 and `!=` on the pair that `b4_norm.py` reports as identical, because it
counted the `data16 cs nopw` / `xchg %ax,%ax` after the final `ret`. Had I
trusted it, B4 would have looked like a live ladder.

---

## The three calls the manager is least sure of

### 1. *"That new rows are needed at all."* — **My probing says NO. Stop at 25 and do the synthesis.**

Eight candidates, eight refusals, all measured. Combined with the catalogue's
own position (24 built, 15 refused, `p23` the only live leftover), the evidence
is not "we picked badly" — it is **structural**, and it is the boxed rule at the
top of this report: this instrument prices a compare-and-branch that one rung
emits and another omits. Checking that against the tree rather than against my
own probes, it holds:

- what it CAN price: `index >= len` (fourteen rows), `p18`'s `shift < VBITS`,
  `p04`'s fullness test, `p09`'s `q < nbits`, `p27`'s `live[h] == 1` conjunct —
  **all compare-and-branch**;
- what it CANNOT: `p08` (overlap — unobservable, shipped as an
  expressiveness/tooling result), `p22` (non-termination — *"nothing on this
  ladder emits the capacity check"*), `p38` (aliasing — 6.00 `Ir`, gcc only,
  shipped labelled a demonstration kernel), `p31`/`p45`/`p44` (refused, one
  rung).

So the tree **already contains** the two best specimens of the "instrument
cannot price it" class (`p08` and `p22`), and a third would be a third. **The
marginal pattern is now worth less than the first cross-pattern synthesis
task, which has never been scheduled.** I would put option (iv) to the user with
this report's table as the evidence, and note that (iii) — open new rows — has
now been *tried*, at the cost of one task, and returned eight refusals.

⚠ I am **not** saying `p23` should be dropped. `p23` is a live, probe-clean
build candidate and finishing it gives a round 25.

### 2. *"That §B's four guesses are worth probing."* — **Yes, and three of the four were worth it for the reason the manager did not expect.**

- **B4 was the weakest guess and the cheapest kill** — one compile. The
  manager's own instinct ("most likely to collapse into `p38`, check that
  first") was right, and following it cost nothing.
- **B2 was worth it and the manager's stated worry was HALF WRONG**: gcc probes
  by default (true), **clang does not** (not stated), and the harm is
  unobservable for a *third* reason neither of us named — ASLR's unmapped gap,
  `witness_dirty=0` in every cell.
- **B1 was worth it and BOTH of our predicted kills were wrong.** The manager's
  degenerate-ladder worry is survivable (`p08` ships that shape); my
  "Verus can't type a variadic" was refuted at `1 verified, 0 errors`. The real
  kill is measurement, not structure.
- **B3 was the best of the four** and produced the one keeper.

My four replacements were **not** better than the manager's — three of mine
(C1, C2, D6) died faster than three of the manager's. So the honest answer to
"replacing them is encouraged" is: **my hit rate was the same, zero, and the
§B list was not the problem.**

### 3. *"That the tree having fourteen `index >= len` makes a fifteenth a high bar."* — **The manager's own suspicion is right: the bar is on the wrong quantity.**

I do not think the CVE distribution is the right argument, so I will not lean on
it — but for completeness it points the same way (CWE-787 out-of-bounds write
and CWE-125 out-of-bounds read are the two highest-ranked memory-safety
weaknesses in every recent CWE Top 25, above use-after-free, NULL deref and
integer overflow). **The stronger argument is the instrument's, and it is
first-hand:**

> The catalogue's own ladder-test block already says it —
> *"Novelty of the bug class predicts neither way. The ladder test does."*
> `p36` shipped as the **twelfth** `index >= len` and was worth building;
> `p45`'s UB class was **genuinely absent** and was not.

Eight refusals later I would sharpen that into a **replacement bar**:

> **A fifteenth `index >= len` is admissible whenever it brings a NEW MECHANISM
> — a new operator on the safety line, a new place the bound comes from, or a
> new reason the check is or is not elided. "Another `index >= len`" is not the
> question. "Another `cmp/jbe` in the same place, for the same reason" is.**

That is the criterion the tree's own fourteen already satisfy — `p06`'s division
instead of a compare, `p09`'s non-bounds guard, `p36`'s excluded *mechanism*,
`p19`'s state-range check, `p22`'s check that no rung emits. Refusing a
fifteenth on "we have fourteen" would be over-fitting to novelty exactly as the
manager suspects; refusing one because its `cmp/jbe` is `p16`'s `cmp/jbe` in
`p16`'s place is not.

---

## What I did NOT do, and what I am unsure about

- **I ran no `harness/measure.py`, no `harness/build.py`, edited no
  `harness/check.py`, created no pattern directory and touched no existing
  one.** `git status --porcelain` is empty apart from `.temp/` (gitignored) and
  this report. No `git add`, no `git commit`.
- **No `Ir` figure here is gate-grade.** Probe 3 numbers are static instruction
  counts and one whole-program callgrind run (B1). They are adequate for a
  kill/no-kill decision and **not** for publication. Per `p46`, a probe can be
  wrong in *sign*; every kill above therefore rests on probe 2 (byte-level
  identity) or on the harm matrix, never on a probe-3 number alone.
- **C1's refusal is dated, not absolute.** It rests on glibc 2.39's `qsort`
  being a mergesort. On an older glibc the row might be live. I did not test a
  second libc and there is not one on this box.
- **B3's Verus frame (32 B) is not like-for-like** with the C/Rust 48 B — the
  Verus probe's `parse_group` has a different signature. Stated inline; the
  C-vs-Rust 48 ≡ 48 comparison is like-for-like.
- **I did not build a full five-rung ladder for any candidate.** For a REFUSE
  that is the point (the probes are supposed to be cheaper than the build), but
  it means none of these verdicts has been through a gate.
- ⚠ **One positive-control cell did not fire** (D6/clang/-O2), disclosed in
  full above with its mechanism, its independent proof that ASan was live in
  that binary, and a corrected control that fires on both compilers.
- ⚠ **One typo attempted a write to `/tmp_a`** — the filesystem root, not
  `/tmp/` — while redirecting a probe. It failed (`Read-only file system`) and
  wrote nothing. No `/tmp` file was created at any point; all scratch is under
  `.temp/t102/`.
- ⚠ **`git status` shows `results/gate/p03-bounded-stack.json` modified. That is
  NOT me.** I ran no harness script; `ps` shows PIDs **1290804 / 1290805**
  running `timeout 3000 harness/check.py p03`, i.e. the concurrent `TASK_100`.
  I left it alone (no kills, and it is not mine). Flagging it so the manager
  does not attribute it to this task at commit time — and so rule 11's
  `git add -A` hazard is not walked into while that gate is live.
- **I did not probe** three further ideas I generated and judged duplicative
  before spending time: signed-length-into-`memcpy` (CWE-195; overlaps
  `p02`/`p07`), `size_t` multiplication overflow in an allocation size
  (overlaps `p07`'s width bug and would be allocator-dominated), and
  sign-extended `char` as a table index (overlaps `p03`'s underflow and `p19`'s
  storage-class result). I mention them so the next agent does not re-derive
  them; **none of the three was probed, so treat those three sentences as
  argument, not measurement.**

## Corrections owed to the authoritative layer (manager to apply)

1. **`.temp/t94/knorm.py` has a false-negative padding defect** — probe 2's
   tool. `.temp/t102/b4_norm.py` is the four-line fix. Worth a line in
   `.memory/06-catalogue.md`'s probe-2 block, which already carries two
   instrument defects.
2. **`harness/check.py` sets no `MIRIFLAGS`; Miri's default alignment check is
   seed-dependent.** Nothing in the tree depends on it today. Worth a line in
   `.memory/00-environment.md` beside the ASan/`LD_PRELOAD` entry.
3. **`volatile T s = p[n]` does not force the load** — a positive-control
   spelling that clang -O2 can delete. Worth a line beside `env -u LD_PRELOAD`
   and "grep, never head" in the harm-probe recipe.
4. **`unchecked_div` / `unchecked_rem` do not exist at the pin** (`E0599`, and
   `E0635 unknown feature`), unlike `unchecked_add/sub/mul`. Worth a line in
   `.memory/00-environment.md` or `TOOLCHAIN.md`; it constrains any future
   arithmetic row's R4.
5. **`-fstack-clash-protection` is ON by default for gcc on this box and OFF
   for clang** — verified from the emitted probe instructions, not from
   `-Q --help=common`.
6. **glibc 2.39's `qsort` is a mergesort + heapsort fallback**, so comparator-
   contract violations are no longer memory-unsafe here.

**Refutations this task produced: 5** — three against my own stated premises
(Verus cannot type a variadic; `qsort` still walks out of bounds; alignment has
a cost) and two against the manager's (`-fstack-clash-protection` mitigates it,
which is true only of gcc; and `knorm.py`'s verdict, which is unsound on
padding). **I am not carrying a total forward** — reconciliation with `TASK_100`
is the manager's job, and I was launched from 309.
