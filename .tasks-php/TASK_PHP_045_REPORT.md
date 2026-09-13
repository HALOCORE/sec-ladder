# TASK_PHP_045 — REPORT: row 8 = `ph52`, an unconstructed caller slot destructed on an early exit

**Role:** research engineer, one agent alone.

> ## ⭐⭐⭐ THE SHORT VERSION, FOR ROUTING
>
> **`ph52` IS BUILT, AND `T3` IS CLOSED.** Six rungs, 32 cells, the model agreeing with
> all of them on every input except the one that is supposed to separate R1.
>
> **SIX OF THE TEN REGISTERED HYPOTHESES IN §2.3–§2.9 ARE REFUTED** (§9's ledger),
> including the registered prediction about `isolated`/`whole`, *"a clean stack slot
> reads zero"*, `_zval_dtor`'s *"no `case IS_NULL`"*, fallback (a) as stated, F102's
> *"five named cases"*, and §2.6's ASan prediction — **that one three ways over.**
>
> **THE THREE RESULTS TO CARRY:**
> 1. ⭐⭐⭐ **The sanitizer fires on the row's BENIGN inputs and is silent on its
>    adversarial one** (§12), because ASan's fake stack recycles 1 frame in 283. **A
>    detector manufacturing the defect it was asked to find.** F102's `0xbe` correction
>    with the sign reversed.
> 2. ⭐⭐⭐ **Open item 76 is `0.00 %` in family A and `−0.3497 %` in B1** (§5) — the
>    upstream fix is **profitable**, and family A's zero is **blindness**
>    (`inside_share` 22.24 %, the difference 100 % outside the kernel symbol).
> 3. ⭐⭐ **§2.9(2)'s O(slots) law is refuted and replaced by a decomposition** (§6.2):
>    `+12.41 Ir/call` against ph53's `+101.59`, **8.19× for 3× the slots**, because the
>    per-slot term is itself **2.73×**.
>
> **ONE `harness/` PROPERTY, REPORTED NOT REPAIRED:** `check.py::check_trusted_twins`'s
> `n_twins == 0` rule hard-fails a row whose only contract-bearing trusted item is
> genuinely untwinnable — the objection `TASK_007` accepted one item down, and **ph52
> is the first row to reach it because its trusted surface is the smallest** (§8.1).
>
> **THE LARGEST OMISSION:** no `controls/spellings.py`, so the row has **no in-contract
> spread** and **open item 81 is untested by it** (§10.1, §13.1).

---

## §0 BRACKETS — OPENING

```
python3 harness/measure.py --check-stale
  -> 66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale
  -> 16 record(s) examined, 0 STALE
```

Both quoted verbatim from the run at the top of this task. The closing bracket is §13.

---

## §1 ⭐⭐⭐ DELIVERABLE #0 — STACK DETERMINISM. **SETTLED, ON ALL CELLS, AND IT BREAKS FIVE OF THE MANAGER'S STATEMENTS**

### 1.0 What was measured, and with what

A faithful miniature of the `ph52` shape. ⭐ **It is COMMITTED, at
`patterns-php/ph52-concat-copy-uninit/controls/d0_stack.{c,py}` with
`controls/d0_noinl.h`** — `PROTOCOL_PHP.md` §F6 and `.memory-php/04-process.md` law 13:
a finding whose only evidence is a gitignored probe will not survive a clean checkout.
Every number in this section is reproducible with
`python3 patterns-php/ph52-concat-copy-uninit/controls/d0_stack.py [--selftest|--sanitizers]`.
It reproduces, with upstream's own line numbers in the comments:

* `concat_function` (`zend_operators.c:1146-1153`) declaring **`zval op1_copy;`** bare
  and passing `&op1_copy` to
* `zend_make_printable_zval` (`zend.c:188-265`), whose `IS_OBJECT` + `EG(exception)`
  arm calls **`zval_dtor(expr_copy)` at `:243`** on the unwritten slot, then writes
  `:244-245` `len = 0; val = empty_string` and `break`s to
* `:263 expr_copy->type = IS_STRING;` — **the tag written last** —
* and `_zval_dtor` (`zend_variables.c:36-80`) with its real `if (type == IS_LONG) return;`
  at `:38`, its `switch (type & ~IS_CONSTANT_INDEX)` at `:41` and its six teardown arms.

Swept over **16 configurations**: `{gcc 13.3.0, clang 22.1.6} × {O0, O3} ×
{isolated, whole} × {callee noinline, callee inlinable}`. The first three axes are
`harness/build.py`'s own (`-DSLB_ISOLATED` vs `-flto`, plus `-fuse-ld=lld` for
clang/whole, which `build.py:168-171` inserts and without which clang + `-flto`
does not link on this box — `LLVMgold.so` is absent). The fourth axis is mine and
§1.3 is why it has to exist.

The driver alternates two windows, `k = i & 1`:
window 0 → `IS_ARRAY` (a **converting** arm: `estrndup`, a real heap pointer),
window 1 → `IS_OBJECT` with the exception flag set (**the faulting arm**).

### 1.1 ⭐ THE RESULT: THE DEFECT IS DETERMINISTIC ON **14 OF 16** CELLS, AND THE FAULT IS A REAL DOUBLE FREE

Shipped flags, no sanitizer:

| cells | outcome |
|---|---|
| **14 of 16** | `free(): double free detected in tcache 2`, **exit 134** |
| `clang-O3-isolated-inl`, `clang-O3-whole-inl` | **exit 0, `n243 = 0`** — the `:243` teardown is **gone**, and the answer changes (`acc = 4874798859`) |

With the `:243` teardown made observation-only (so the run survives to report), **all
16 cells agree exactly**:

```
:243[0] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90
:243[1] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90     <- SAME slot address
:243[2] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90     <- SAME slot address
acc=4530891183                                    <- bit-identical in all 16 cells
```

`tag = 3` is `IS_STRING`; `ptr` is the **previous** op's `estrndup` block, which
`zend_operators.c:1188`'s own `zval_dtor(op1)` has already freed. So `:243` takes
`case IS_STRING` → `STR_FREE_REL` → `efree` of an already-freed pointer.

Under ASan with the frame relocation turned off, the diagnostic is exact
(`gcc -O0 -fsanitize=address -static-libasan`,
`ASAN_OPTIONS=detect_stack_use_after_return=0` — `controls/d0_stack.py --sanitizers`
drives the sweep):

```
==2354129==ERROR: AddressSanitizer: attempting double-free on 0x502000000010 in thread T0:
    #0 __interceptor_free.part.0
    #1 ph_zval_dtor                  <- zend_variables.c:45  STR_FREE_REL
    #2 ph_make_printable_zval        <- zend.c:243
    #3 kernel                        <- zend_operators.c:1152
    #4 main
```

### 1.2 ⛔ REFUTED #1 — **"A CLEAN STACK SLOT READS ZERO"** IS AN **ASan** PROPERTY, NOT A PROPERTY OF THE SHIPPED BUILD

§2.3's table says an un-initialised `stack[64]` reads `00 00 …` **with and without**
the sanitizer, and concludes *"a clean stack slot reads zero, zero is `IS_NULL`, and
`zval_dtor` is a no-op on it."*

**Measured on the FIRST call of the 16 cells, shipped flags** (the probe's round-1
shape, which traces the tag rather than acting on it), the tag the first `:243` sees
is:

| cell | tag at call 1 |
|---|---|
| gcc-O0-isolated, gcc-O3-isolated, gcc-O3-whole-*, clang-O0-isolated-* | `0` |
| gcc-O0-whole-noinl | **235** (`0xeb`) |
| gcc-O0-whole-inl | **94** (`0x5e`) |
| gcc-O3-isolated-inl | **113** (`0x71`) |
| clang-O3-isolated-noinl | **82** (`0x52`) |

So **4 of the 16 read non-zero on the very first call**, and the value is a
build-configuration artefact of whatever the C runtime's own startup left at that
offset. None of the four masks into a freeing case (`235 & 0x7f = 107`,
`94`, `113`, `82` — none in `{3,4,5,7,8,9}`), so the *conclusion* happened to
hold; the *premise* does not.

⭐ **Why the manager's table says zero: his probe was built `-fsanitize=address`, and
ASan hands out a freshly zeroed frame.** §1.5 measures that mechanism. ▶ **The
table is right about ASan and does not transfer.** This is `.memory-php/04-process.md`
law 15's shape again — a property of the observation taken for a property of the
program.

### 1.3 ⛔⛔ REFUTED #2 — THE LOAD-BEARING BOUNDARY IS **NOT** THE HARNESS'S `isolated`/`whole`. IT IS THE **CALLEE** INLINE BOUNDARY, AND `build.py` DOES NOT CONTROL IT

§2.3 hypothesis 2 registers: *"PREDICTION, REGISTERED: the defect may be PRESENT in
`isolated` and OPTIMISED AWAY in `whole`."*

**Measured, shipped flags: the `isolated`/`whole` axis moves nothing.** Grouping the
16 cells:

| callee | isolated | whole |
|---|---|---|
| `noinline` | **double free** (gcc O0/O3, clang O0/O3) | **double free** (gcc O0/O3, clang O0/O3) |
| inlinable | double free (gcc O0/O3, clang O0) · **DELETED** (clang O3) | double free (gcc O0/O3, clang O0) · **DELETED** (clang O3) |

The only axis that moves the outcome is whether `zend_make_printable_zval` can be
**inlined into `concat_function`**. At `clang -O3` with it inlinable, clang sees that
`op1_copy.type` is never stored before `:243`, treats the `switch` operand as `undef`,
**deletes the `zval_dtor` call entirely** (`n243 = 0`) and emits a different answer.
`gcc -O3` does not do this; `clang -O0` does not either.

⚠ **And `-DSLB_ISOLATED` / `-flto` cannot control that boundary**, because
`harness/build.py:161-165` compiles exactly three TUs and both the caller and the
callee live in `c/kernel.c`. ▶ **So the row must carry `__attribute__((noinline))`
on the lifted `zend.c` / `zend_variables.c` functions, and that is a declared
`substitution` modelling the real `zend_operators.c` ↔ `zend.c` ↔ `zend_variables.c`
translation-unit boundaries — three TUs upstream, one here.** Measured: with it,
the defect is present in **all 16** configurations.

⭐ **The finding is better than the prediction it replaces.** It is not *"a defect
whose existence depends on the TU boundary"* as an oddity of this row — it is
*upstream's own build configuration is load-bearing for this defect's reachability,
and a whole-program compiler deletes the bug*. PHP 5.0.0 is built without LTO; that
is why the bug was reachable at all.

### 1.4 ⛔ REFUTED #3 — FALLBACK (a) AS STATED **DOES NOT FIRE**. THE CALL HISTORY NEEDS **TWO DIFFERENT ARMS**, NOT A REPEATED ONE

§2.3's fallback (a): *"iteration 2+ reads the previous iteration's `IS_STRING` and
frees the previous iteration's already-freed pointer."*

**Measured with a single repeated window on the exception arm: `free calls = 0` in
every cell that kept the teardown.** The reason is two lines of
the arm the manager quotes: `:244-245` write `len = 0; val = empty_string`, and
`zend.h:469 STR_FREE(ptr)` is `if (ptr && ptr != empty_string) efree(ptr)`. ▶ **A
call that takes the exception arm leaves `IS_STRING + empty_string` in the slot,
which is permanently safe to "free".** So a repeated exception arm is *self-defusing*.

✅ **Corrected, fallback (a) holds and is stronger.** The adversarial call history is
**an allocating arm followed by the exception arm**:

1. call *k* takes a converting arm (`zend.c:213-215 IS_ARRAY`, or `:248-249 IS_OBJECT`
   without an exception, or the `:259-261 default`) → `value.str.val` is a real
   `emalloc` block and `:263` writes `type = IS_STRING`;
2. back in `concat_function`, `:1187-1189 if (use_copy1) zval_dtor(op1)` **frees that
   block**, leaving `IS_STRING` + a **dangling** pointer in the slot;
3. call *k+1* takes the exception arm → `:243` reads `IS_STRING` + the dangling
   pointer → `efree` → **double free**.

⭐ **And that is MORE faithful than the manager's version, not less:** it is two
different `.` operations on two different operand types, which is what a PHP script
does, and it is why the bug is reachable.

### 1.5 ⚠ REFUTED #4 — ASan DELETES THE DEFECT, AND **NOT** BY POISONING. IT **RELOCATES THE FRAME**

> ⛔⛔ **READ §12 BEFORE BELIEVING THIS SECTION'S HEADLINE.** *"ASan deletes the
> defect"* is what a short probe shows and it is **only 282/283 of the story**: on the
> full 25,000-iteration measured corpus the fake stack recycles one frame in 283 and
> ASan reports a `heap-use-after-free` **it caused itself**. §12 is the measurement and
> it supersedes the reading here; this section is kept because it is what the
> Deliverable-#0 probe legitimately showed and because the *mechanism* it names —
> relocation, not poisoning — is the one §12 rests on.

§2.3 hypothesis 4 says *"`-ftrivial-auto-var-init`, stack poisoning, or any
`-fsanitize` stack mode DELETES the defect."* Upheld as a conclusion; the mechanism
is not poisoning.

`-fsanitize=address -static-libasan`, default `ASAN_OPTIONS` (13 of 16 cells):

```
:243[0] tag=0 ptr=(nil) slotaddr=0x7b2d5b0f0120
:243[1] tag=0 ptr=(nil) slotaddr=0x7b2d5b0f0320    <- +0x200
:243[2] tag=0 ptr=(nil) slotaddr=0x7b2d5b0f0520    <- +0x200
```

**The slot address moves by 0x200 on every call.** That is ASan's **fake stack**
(`detect_stack_use_after_return`, whose default is `1` in both of these builds): the
frame is allocated from a heap pool, freshly zeroed, so **no two calls share the
offset** and the tag is always `0 = IS_NULL`. Setting
`ASAN_OPTIONS=detect_stack_use_after_return=0` restores the real stack and ASan then
**reports the double free** with the stack trace in §1.1, on every cell tried.

⚠ The three ASan cells that report it even at the default are
`gcc-O3-whole-{noinl,inl}` and `clang-O3-whole-noinl` — in `whole` mode `-flto`
inlines `kernel` into `main`, so the slot becomes a `main`-frame local, `main`'s frame
is entered once, and the fake stack never re-rolls it.

⭐⭐ **That is the manager's prediction 2 firing — with the sign reversed and only
under a sanitizer:** under ASan the defect is **present in `whole` and suppressed in
`isolated`**, the exact opposite of what was registered. Under the shipped flags
neither mode suppresses it.

And `-ftrivial-auto-var-init=zero` / `=pattern`: **all 16 cells clean, `n243 = 3`,
`nfree = 3`, `acc = 4530891183`** — the defect is gone and the answer moves. Both
flags are absent from `harness/build.py::c_flags` (`-std=c99 -Wall -Wextra -O0|-O3`
plus `-DSLB_ISOLATED` or `-flto`), so the shipped matrix is unaffected; the row
records them as the compiler-side form of the catalogue's tidying trap.

### 1.6 ✅ UPHELD — HYPOTHESIS 3 IS THE ONE THAT SURVIVES: THE OFFSET **IS** EXACT

§2.3 hypothesis 3: *"Stack reuse may not be exact … Verify the offset, do not
assume it."* Verified, and it **is** exact: the same `slotaddr` on every call in
every one of the 16 cells under the shipped flags, at both `-O0` and `-O3`, in both
modes, on both compilers. The only configuration in which it is not exact is ASan's
fake stack (§1.5).

### 1.7 ▶ THE CONSEQUENCE FOR THE ROW, AND IT IS THE BEST OF THE FOUR FALLBACKS

Because §1.4's chain is **intra-frame and slot-local**, it can be made a property of
the **blob** instead of a property of the driver's iteration count — which is what
settles Deliverable #0 as **fallback (a), corrected**, with no synthetic prior call
(b), no relegation of the benign path to `controls/` (c), and no move to the heap (d).

The kernel runs a **sequence of `concat_function` calls** decoded from the window —
which is faithful: `concat_function` is PHP's `.` operator and a script calls it
repeatedly — and `zval op1_copy, op2_copy;` are locals of `ph52_concat_function`, so
successive ops in one window share the offset exactly (§1.6). Then:

* **the adversarial property is `allocating op immediately followed by exception op`,
  visible in the bytes `gen.py` just wrote**;
* **the benign property is its negation**, plus one rule for the program's very first
  call, where the slot holds C-runtime garbage (§1.2): **no window may carry an
  exception-arm op at position 0.** With that, every `:243` in the measured corpus is
  preceded, in the same window, by an op whose arm left `IS_STRING + empty_string`
  or a live-then-freed-by-nobody slot, and the tag is known.

Both are assertions `inputs/gen.py` can re-derive from the bytes, which is §A2a
rule 1's own shape.


---

## §2 ⭐ §2.1's R1h ARGUMENT, TOKEN BY TOKEN — and it is now a CHECK, not prose

`7412202c43e7` — Antony Dovgal, **2006-05-11**, *"no need to destroy the zval
here"*, `Zend/zend.c`, **1 file, 1 hunk, 0 insertions, 1 deletion**. Committed at
`patterns-php/ph52-concat-copy-uninit/controls/7412202c43e7.patch`, sha256
`32e8526ebfe684d9ae80e32df0f453c018f954dd0694f1cd5cbc7d30891adfbf`, 746 B.

✅ **The corpus column and `FIXSURVEY_001.md:242` AGREE on this sha**, so unlike
`ph53` there is no wrong commit to exclude and §F5(iii) needs no release-tag walk.

### 2.1 The deleted statement is byte-identical up to ONE TAB

```
the commit's removed line, `-` stripped   (od -c)
  \t \t \t \t  z v a l _ d t o r ( e x p r _ c o p y ) ; \n      4 tabs
pristine 5.0.0 Zend/zend.c:243            (od -c)
  \t \t \t \t \t  z v a l _ d t o r ( e x p r _ c o p y ) ; \n    5 tabs
```

By 2006 the arm had lost a level of nesting. **That tab is the whole of the
difference in the statement.**

### 2.2 ⛔ Why `patch -p1` cannot apply: two CONTEXT tokens do not exist in 5.0.0

The 2006 hunk's context lines name **`STR_EMPTY_ALLOC()`** and
**`E_RECOVERABLE_ERROR`**. Measured over the pristine tarball:

| token | `Zend/zend.h` | `zend_variables.h` | `zend_API.h` | `zend_operators.h` | `zend_errors.h` |
|---|---|---|---|---|---|
| `STR_EMPTY_ALLOC` | 0 | 0 | 0 | 0 | — |
| `E_RECOVERABLE_ERROR` | — | — | — | — | **ABSENT** |

5.0.0's own arm is `if (EG(exception)) { … expr_copy->value.str.val =
empty_string; break; }`. ▶ **So `patch` has nothing to match, the hand
reconstruction is the deletion of that one statement, and every token that
differs is accounted for.**

### 2.3 ⭐ AND THE DELETION IS COMPLETE — which is the OPPOSITE of `ph53`'s result

Every `expr_copy` use in `zend.c:188-265`, enumerated from the tarball
(`awk 'NR>=188 && NR<=265 && /expr_copy/'`):

| line(s) | use | written earlier on the same path? |
|---|---|---|
| `:196 :197 :201 :202 :204 :205 :209 :213 :244 :245 :249` | writes | — |
| `:210 :214 :250` | read a field written 1 line above | ✅ |
| `:222` | `zend_std_cast_object_tostring(expr, expr_copy, …)` | **inside the `#if 0` at `:220-228`** — dead |
| `:229 :236` | pass the pointer to a callee | the declared projection |
| **`:243`** | **`zval_dtor(expr_copy)`** | ⛔ **NO** |
| `:253 :258` | `*expr_copy = *expr` — whole-struct writes | — |
| `:254 :259 :260` | read, 1-2 lines after `:253`/`:258` | ✅ |
| `:263` | `expr_copy->type = IS_STRING` — **after the switch** | — |

▶ **`:243` is the ONLY line in the function that reads `expr_copy` with no write
to it earlier on the same path**, and `:263` sits after the switch so every path
that leaves the function has written the tag. **Deleting `:243` leaves no path
that tears down an unconstructed slot.** `_040` §2.1's *"complete"* is confirmed,
and by a stronger route than the one it gave (it argued from `:263`'s position
alone; this enumerates every other read).

⭐⭐ **TWO CONSEQUENCES THAT `ph53` COULD NOT HAVE**, and they are why this row is
shaped differently:
1. **R2–R5 ARE ports of R1h.** `ph53`'s fix was incomplete, so a safe-Rust rung
   built to it would have had to panic and *"a rung that panics is not a
   translation of the C"*. ph52's R1h is memory-safe.
2. **The adversarial input CAN ship in `inputs/`.** Stage 7h requires R1h clean on
   every input; R1h has no `:243` at all.

### 2.4 ⭐ The argument as a CHECK

`controls/r1h_onelinedel.py` derives `c/kernel_hardened.c` from `c/kernel.c` and
prints

```
  code lines only in R1  : 1  ['ph52_zval_dtor(expr_copy);']
  code lines only in R1h : 0   []
  ok: R1h is R1 minus exactly one statement
  --selftest: 11 cases (8 must-fire, 3 must-NOT-fire)
  --selftest PASS
```

Its must-fire arms include **a hardened kernel that added a guard instead of
deleting the call** — which stage 7h would not have noticed — one that deleted
`:1188` as well, the statement restored in the code while the comment still names
it, and a comment-only edit that must still fail the derivation.

---

## §3 ⭐⭐ §2.5's TAG SWEEP — MEASURED, and F102's figure is wrong in THREE ways

`controls/tag_sweep.c` transcribes `Zend/zend_variables.c:36-80` over the whole
byte (all six arms, including the two `c/kernel.c` does not lift);
`controls/tag_sweep.py` re-derives the same table from the `#define`s and the
`switch` independently, and the two must agree.

| arm | tag values | of 256 |
|---|---|---|
| **no-op** | 244 values | **95.312 %** |
| `STR_FREE` → `efree` | 3, 8, 131, 136 | 1.562 % |
| hash destroy + `FREE_HASHTABLE` | 4, 9, 132, 137 | 1.562 % |
| object `del_ref` | 5, 133 | 0.781 % |
| `zend_list_delete` | 7, 135 | 0.781 % |
| **TOTAL TEARING DOWN** | **12** | **4.688 %** |
| **of which reach `efree`/`free`** | **8** | **3.125 %** |
| live in `c/kernel.c` (2 arms unlifted) | 8 | 3.125 % |

⭐⭐⭐ **THE PUBLISHABLE SENTENCE: 95.3 % of byte values make `zend.c:243` a
no-op, and `IS_NULL` is `0`, which is the likeliest residue of all.** That is why
the defect shipped in every 5.0.x release and was fixed in 2006 as a tidiness
change.

### 3.1 ⛔ The three ways F102's *"five named cases"* is wrong

1. **SIX named cases, not five.** F102 lists `IS_STRING`, `IS_CONSTANT`,
   `IS_ARRAY`, `IS_CONSTANT_ARRAY`, `IS_OBJECT` and **misses `IS_RESOURCE`** —
   `zend_variables.c:64-71`, whose arm calls
   `zend_list_delete(zvalue->value.lval)` on a `long` read out of the same
   unwritten slot.
2. **TWELVE of 256, not ten.** The `& ~IS_CONSTANT_INDEX` mask doubles each of
   the six residues `{3, 4, 5, 7, 8, 9}`.
3. ⛔ **`_zval_dtor` DOES have `case IS_NULL`.** §2.3 of the task file says it
   *"has **no** `case IS_NULL`"*. `zend_variables.c:75` **is** `case IS_NULL:`,
   sitting beside `default:` at `:76`. **The conclusion — a zero tag no-ops —
   holds; the reason given for it does not.**

### 3.2 ⭐ The sweep's own must-fire suite: 15 assertions, PASS

The arm worth reading is **N5**: `0x01` no-ops via the `:38` early return and
`0x81` no-ops via the switch's own `case IS_LONG:` at `:72` — **two different
reasons, one outcome**, and a checker that conflated them would be right by
accident. **N9** then measures that the `:38` early return is **redundant for the
count**, which is a fact about upstream's code the row would otherwise have
asserted.

---

## §4 ⭐⭐⭐ §2.8 — WHICH STATISTIC. `inside_share` MEASURED FIRST, AND IT DECIDES **W1**

`.memory-php/03-numbers.md`: *family A resolves a code difference exactly to the
extent the difference lands INSIDE THE KERNEL SYMBOL.* Measured, `c-gcc`,
`O3/isolated`, `small.bin`, callgrind per-function exclusive Ir:

| function | Ir | share |
|---|---:|---:|
| `ph52_make_printable_zval` | 37,617,282 | **25.74 %** |
| `ph52_concat_function` | 33,766,427 | **23.10 %** |
| **`kernel`** | **32,509,505** | **22.24 %** |
| `ph52_zval_dtor` | 19,745,701 | **13.51 %** |
| libc (`malloc` + one more) | 16,244,129 | 11.11 % |
| **PROGRAM TOTAL** | **146,152,976** | 100 % |

⛔⛔ **`inside_share` IS 22.24 %, AND THE DIFFERENCE THE ROW IS ABOUT LANDS
ENTIRELY OUTSIDE IT.** `PH52_NOINLINE` puts `ph52_make_printable_zval`,
`ph52_concat_function` and `ph52_zval_dtor` in their own symbols — **62.35 % of the
program** — and `:243` lives in the first of them. ▶ **So this row publishes in W1
(whole-program marginal), not A1.** ⭐ `ph45` at 9.5 % published W1, `ph53` at
89.5 % published A1; ph52 at 22.24 % is the third data point and it lands on
`ph45`'s side.

⚠ **And the reason `inside_share` is low is the SAME declared substitution that
makes the row reproducible at all** (§1.3): the three-TU boundary. A row that let
the callees inline would have a high `inside_share` and no defect in 2 of 16 cells.
**That coupling is worth recording: `inside_share` is not independent of the
extraction's fidelity choices.**

---

## §5 ⭐⭐⭐ ITEM 76 **TESTED**, AND IT IS REFUTED IN THE COLUMN THAT CAN SEE IT

Item 76 predicts *the R1h column is `0.00 %`*. Measured on `small.bin`,
`O3/isolated`:

⚠ **F99: every field below is named with its file.** `A1` is
`ir.<input>.kernel_exclusive_ir` from **`results-php/ph52-concat-copy-uninit.json`**;
`B1` is `marginal_ir_per_call` from **`results-php/gate/ph52-concat-copy-uninit.json`**,
the gate's own field; `W1` is a one-shot `callgrind_annotate` `PROGRAM TOTALS` I ran by
hand.

| statistic | R1 (`c-gcc`) | R1h (`c-gcc-h`) | Δ |
|---|---:|---:|---:|
| **A1** | 32,509,505 | 32,509,505 | **0, i.e. exactly `0.00 %`** |
| **B1** ⭐ published | 5833.79 | 5813.39 | **`−0.3497 %`** |
| W1 | 146,152,976 | 145,653,146 | `−0.342 %` |

and on clang:

| statistic | R1 (`c-clang`) | R1h (`c-clang-h`) | Δ |
|---|---:|---:|---:|
| **A1** | 27,465,935 | 27,465,935 | **0** |
| **B1** ⭐ published | 5430.26 | 5389.36 | **`−0.7532 %`** |
| W1 | 136,056,404 | 135,049,431 | `−0.740 %` |

⭐ **B1 and W1 agree to within rounding**, which is the cross-check the two statistics
exist for, and `large.bin` gives `−0.2372 %` (gcc) / `−0.6396 %` (clang).

⭐⭐⭐ **SO ITEM 76 IS UPHELD IN FAMILY A AND REFUTED IN W1 — and family A's zero
is BLINDNESS, not absence.** The per-function split says exactly where the
difference is, and the `kernel` symbol is not in the list:

| function | R1 | R1h | Δ |
|---|---:|---:|---:|
| `ph52_make_printable_zval` | 37,617,282 | 37,499,674 | **−117,608** (the deleted call site) |
| `ph52_zval_dtor` | 19,745,701 | 19,363,475 | **−382,226** (the calls that no longer happen) |
| `ph52_concat_function` | 33,766,427 | 33,766,427 | 0 |
| `kernel` | 32,509,505 | 32,509,505 | **0** ← why A1 reads zero |
| | | | **−499,834 ≈ the −499,830 total** |

⭐ `ph45`'s **`BLIND`** class (F86: *A is exactly `0` while the whole-program figure
is not*, 14 of 366) with a named mechanism, and on a row where the blind quantity
is the row's own headline.

### 5.1 ⭐⭐ AND THE SIGN IS THE RESULT: THE UPSTREAM FIX IS NOT FREE, IT IS **PROFITABLE**

`−0.342 %` / `−0.740 %`: **R1h is CHEAPER than R1.** The mechanism is the whole of
it — R1 calls `ph52_zval_dtor` once per faulting-arm op and R1h does not, so the fix
removes the callee's instructions *and* the call site's setup.

⭐⭐⭐ **What that publishes, and it is the thing the task hoped for, with the sign
the task did not predict:** *the upstream fix for a whole CLASS of defect — the
unreached-error-path teardown — is not merely free, it pays for itself, and the
ladder can put a number on it.* ⚠ The figure is **small** (a third to three
quarters of one per cent), and it is small for a reason worth stating: the faulting
arm is a minority of the op stream and the teardown it removes is a handful of
instructions per call. ⛔ **A `0.00 %` column would have been a finding and not a
disqualification** (`CLAUDE.md` rule 6); a **negative** one is a better finding and
the row did not have to choose.

⚠⚠ **WHICH INPUT, WHICH STATISTIC, WHICH LEVEL, WHAT AGAINST** (F98's four
qualifiers): every figure above is **`small.bin`**, **`O3/isolated`**, **W1 or A1 as
labelled**, **R1h against R1** — same language, same allocator, so §B1a.3's
cross-language caveat does **not** apply to this column. It is the second-cleanest
column the row has.

---

## §6 ⭐⭐ §2.9 — BOTH PREDICTIONS TESTED

### 6.1 ✅ §2.9(1) **UPHELD**, and the reproduction is STRONGER than on `ph53`

`controls/negatives.py --verus`, 7 arms, **all as expected**:

| arm | verdict |
|---|---|
| N1 `verus.rs` | 33 verified, 0 errors (34 under `--cfg slb_twin`) |
| N2 `controls/mu_unwrapped.rs` | **6 verified, 0 errors** — the same obligation with NO trusted item |
| **V1** `if *constructed` deleted | **`precondition not satisfied`** |
| V2 the caller's `is_init` `requires` conjunct deleted | `precondition not satisfied` |
| V3 `zval_dtor`'s witness-agreement conjunct deleted | `postcondition not satisfied` |
| V4 the tag written on a path that did not write the value | `postcondition not satisfied` |
| V5 a cosmetic rewrite (`== true`) | 33 verified, 0 errors — **must-NOT-fire** |

⭐ **V1 is the prediction.** Deleting `if *constructed` is `zend.c:243` exactly, and
Verus refuses it. ▶ **F97/F98's *a rung that reproduces the defect cannot be
verified and a rung that verifies does not reproduce it* RECURS on a second row.**

⭐⭐ **AND THE REPRODUCTION IS BIT-EXACT HERE, WHICH `ph53` COULD NOT MANAGE.**
`controls/r4_nowitness.rs` prints **`272040826665440682`** on
`adversarial-dblfree.bin` — **R1's answer, not R1h's** — because the
`MaybeUninit<Pr>` retains the previous op's value exactly as the stack slot does.
ph53's witness-free control *answered correctly* where its R1 faulted.

⚠ **And Miri is where the READ itself shows**, `--miri`, 8 arms, all as expected:
M3 (`r4_nowitness.rs` on a generated op-0-faulting blob) gives
`error: Undefined Behavior: reading memory at alloc…[0x0..0x8], but memory is
uninitialized at [0x0..0x8]`; M4 (the shipped rung, same blob) is **silent**.
⭐ **M2 is the arm that teaches something**: the witness-free control is silent on
every *shipped* input, because `gen.py`'s rules R1/R3 mean no `:243` in the measured
corpus ever sees a slot that was never constructed. ▶ **Its divergence on
`adversarial-dblfree.bin` is the DOUBLE FREE, not the uninitialised read — the two
halves of this defect are separable and the corpus separates them.**

### 6.2 ⚠ §2.9(2) **UPHELD IN DIRECTION, REFUTED AS "~FREE", AND THE LAW REPLACED BY A DECOMPOSITION**

`marginal_ir_per_call`, `small.bin`, `O3/isolated`, shipped R4 against
`controls/r4_nowitness.rs` — **the same base F98 used, a RUST control and NOT the C**.
The control was driven through the same `probe_iters [100, 200]` difference by hand;
the shipped R4's figure is **bit-identical to the gate's own field**:

| | B1 `Ir/call` | W1 (one-shot) |
|---|---:|---:|
| `controls/r4_nowitness.rs` (no witness) | **1962.75** | 49,243,214 |
| shipped `unsafe.rs` (2-bool witness) | **1975.16** | 49,549,469 |
| `verus.rs` | **1975.16** | 49,549,509 |
| **Δ (the witness)** | **+12.41 = `+0.632 %`** | `+0.622 %` |

⭐⭐ **Two methods, one answer.** And the absolute figure is the mechanism, which §F8
asks for: **`+12.41 Ir per kernel call` over 16 ops = `~0.78 Ir per op`** — two `bool`
tests and two stores, register-resident.

⚠ **A THIRD figure, and it is the one that moved when `win_get_unchecked` landed
(§12):** `A1` (`ir.small.bin.kernel_exclusive_ir` from
`results-php/ph52-concat-copy-uninit.json`) for `unsafe` and `verus` went
**52,641,525 → 48,846,257** — and the two rungs are **equal to the last digit in A1 as
well as in B1**, which is `identity: norel` showing up in a third place. ⛔ **The
pre-repair A1 figure is superseded**: the live record carries only 48,846,257, and the
row's published R4/R5 headline columns are B1 and W1, both from post-repair binaries.

⭐⭐ **AND THAT MOVEMENT BOUGHT AN INDEPENDENT CONFIRMATION OF §8f's `−7.12 %`, WHICH IS
WHY NOTES §8f NOW CARRIES AN A1 COLUMN BESIDE ITS W1 ONE** (the one place in the row a
superseded A1 figure is quoted, labelled `before`). W1 is a callgrind total I took by
hand; A1 is the harness's own field, measured in a separate run I did not drive. The
repair's Δ is `−3,795,320` in W1 and `−3,795,268` in A1 — so the **out-of-kernel
remainder** `W1 − A1` is `703,264` before and `703,212` after, **a drift of 52 Ir out of
3.8 M moved (`0.0074 %`)**. ▶ **Two different instruments on two different runs agree
that the repair moved work INSIDE the `kernel` symbol and moved essentially nothing
outside it** — which is exactly what "a bounds check in the window read" predicts, and
is a claim neither figure could make alone. ⚠ The percentages read `7.12` (W1) and
`7.21` (A1) because the same absolute Δ is divided by a smaller base; that is
arithmetic, not disagreement.

⭐⭐⭐ **AND BOTH ROWS HAVE AN ABSOLUTE `Ir/call` FIGURE, SO THE TWO-ROW COMPARISON
DOES NOT HAVE TO GO THROUGH A PERCENTAGE:**

| | ph53 | ph52 | ratio |
|---|---:|---:|---:|
| witness cost, **Ir per kernel call** | **+101.59** (F98's own attribution: `+101.59` of `+228.87`) | **+12.41** | **8.19×** |
| slots | **6** typical (`n_decl` 0..16) | **2** | 3× |
| **Ir per slot per call** | **16.93** | **6.21** | **2.73×** |

▶ **VERDICT: the prediction's DIRECTION is UPHELD and its word is not** — `+12.41
Ir/call` is not *"~FREE"*, it is a real and reproducible cost an order of magnitude
under ph53's.

⛔⛔ **AND THE HOPED-FOR LAW IS REFUTED AS STATED.** *"The cost of a safety witness is
O(the number of slots)"* predicts 3× the slots → 3× the cost. Measured: **3× the slots
→ 8.19× the cost**, because the **per-slot** cost is itself **2.73× higher** on ph53.
⭐ **The cost decomposes as (slots) × (per-slot cost), and the per-slot term is what
moves** — ph53's `wrote[i]` is an **indexed array read**, re-read on every consumer
iteration (`n_ops × n_decl` per call), where ph52's is a **register-resident `bool`**
tested twice per op (`2 × n_ops`).

⚠⚠ **AND THE DATA CANNOT SEPARATE THE TWO CANDIDATE MECHANISMS AT n = 2.** Normalising
by *reads* instead of slots gives ph53 ~`1.59` Ir/read against ph52's ~`0.39` — a 4×
gap — so *read count* and *indexed vs register* both point the same way and neither is
isolated. ▶ **The row publishes the decomposition and the two candidates, not a law.**
A third `T3` row would separate them; `quota.py` says three remain (`ph49`, `ph50`,
`ph51`).

⚠ `ph53`'s `+21.775 %` is **not** the number to compare against directly: it is W1 on
its own corpus with its own denominator, and F98's own qualifier is that only ~44 % of
it is the witness. **The `Ir/call` row above is the comparison that does not depend on
either row's denominator**, and it is the one this report rests on.

## §7 ⭐ §2.2 — THE TIER, AND MY DIRECTION ON OPEN ITEM 75

**Declared `narrowed`. `CATALOGUE.md:146` also says `narrowed`.** ⭐ **So this row
AGREES with the catalogue, and open item 75's *"is the whole catalogue optimistic in
the same direction?"* is now 2 of 3 rather than 3 of 3.** `_040` §5.1 judged ph52's
label optimistic too; on the evidence it was right about `ph53` and **wrong about
ph52**. ▶ **My direction on item 75: the two-row signal does not survive a third
row, and the item should be carried as "sometimes" rather than closed as "yes".**

The itemisation is in the row's `NOTES.md` §2. The one entry worth repeating here:
⚠ `provenance.py` reports the kernel overlap at **19 % against a `narrowed`
expectation of 25 %**, and §F9 requires me to say what I think of it. **I think the
heuristic is right about the text and wrong about the row**: the kernel is 10 cited
spans across 4 files plus ~90 lines of row-specific scaffolding the citation cannot
contain — the window decode, the op loop, the digest constants, the `Alloc` reset —
so a 19 % line overlap is what a faithful `narrowed` extraction of a *small* defect
span into a *driven* kernel looks like. ⚠ **It is also a number I could move by
padding the kernel with cited text, which is why it is reported and not enforced
(`TASK_PHP_008` §2), and I am not going to move it.** The `unevaluable_conditionals`
count is **1** (`#ifndef PH52_KERNEL_H`), so the residual is a header guard.

---

## §8 ⛔⛔⛔ TWO GATE FINDINGS THE ROW PRODUCED, AND ONE IS A `harness/` PROPERTY

### 8.1 ⭐⭐⭐ `check.py::check_trusted_twins`'s `n_twins == 0` RULE HARD-FAILS A ROW WHOSE TRUSTED BASE IS **SMALLEST**

**The first gate run FAILED on stage 5c-twin:**

> `[twin] every trusted item in this pattern (['verus.rs:slot_read_unchecked']) is
> excused by verus.twin_justifications, so stage 5c-twin checked the strength of
> NOTHING. A hatch that can be applied to the whole of its own stage is an off
> switch …`

⭐ **And it was RIGHT about my row**: with `slot_read_unchecked` as the only
contract-bearing trusted item, and that item genuinely untwinnable (there is no safe
exec route from `MaybeUninit<T>` to `T`, so any twin's body would carry an `unsafe`
token outside a trusted body and `_scan_unsafe_sites` refuses it), **nothing whatever
checked the strength of the row's one trusted precondition.**

⚠⚠ **But the rule also reproduces, at n = 1, exactly the defect `TASK_007` deleted
`MAX_TWIN_JUSTIFICATIONS` for**, and `check.py`'s own comment says so:

> *"It was the only knob in the twin regime that could hard-fail an **honest**
> pattern with no route out. A pattern with two genuinely untwinnable trusted items
> had no legal configuration."*

▶ **A pattern with ONE genuinely untwinnable trusted item and no other has no legal
configuration either**, and `n_twins == 0` is what does it. ⭐⭐ **`ph52` is the
first row in either programme to reach that, because it is the first whose trusted
surface is SMALL enough** — `ph53` passes the stage precisely because its trusted
base is **larger** (four items, three of them twinnable `get_unchecked` accessors on
a `Vec`). ⚠⚠ **So the rule puts pressure on a row to ENLARGE its trusted base**,
which is `.memory/02-bench-rules.md`'s *a rung is never cost-selected* one axis over.

⛔ **NOT worked around.** The fix is a `harness/` edit and a 33-pattern re-gate, and
it is recorded here and in the row's `NOTES.md` §11f rather than repaired.
⭐ **The pressure is latent rather than live on this row, because §8.2 is a
legitimate way out.**

### 8.2 ⭐⭐ HOW THE ROW ANSWERED IT, AND IT TURNED INTO A **−7.12 %** FIDELITY REPAIR

`win_get_unchecked` was added to R4/R5. ⭐ **It is a fidelity repair the row owed
anyway, not a TCB inflation to satisfy a gate:**

* **every window read in the C is an unchecked array access** — `win[p]`,
  `win[p+1..3]` and `ph52_rd32`'s four bytes. C has no bounds check, and nothing in
  `concat_function` or `zend_make_printable_zval` verifies that the op record is
  inside the window; the kernel's structural precondition is discharged **at the call
  site**.
* ▶ **So the shipped R4 had been paying a bounds check the C does not — worth
  `−3,795,320 Ir = −7.12 %` of the whole program on `small.bin` at `O3/isolated`** —
  and it was flattering safe Rust in the R2/R3-vs-R4/R5 comparison by exactly that.
* ⭐ **And it IS twinnable**, because `v[i]` is the checked stand-in. `ph53`'s
  `win_get_unchecked` is the precedent, character for character.

⚠⚠ **That is `PROTOCOL_PHP.md` §A2a's lesson verbatim:** *a gate stage that refuses
your row is a hypothesis about your row before it is a hypothesis about the gate.*
**It refused for a reason that looked unrelated and found a real 7 % error.**

⛔ **The routes NOT taken, and why:** making `rd32` trusted *without* a twin, or
adding an unchecked accessor the kernel does not need, would both have satisfied the
stage by enlarging the axiom surface. This one **shrinks** the gap between R4 and the
C instead.

### 8.3 ⛔⛔ THE `idiom` BACKTICK LAW FIRED, BECAUSE I DID NOT RUN THE AUDIT ON THE DRAFT

`.memory-php/02-ladder.md`: *a backtick in an `idiom.required`/`forbidden` entry **IS**
a pin, including around a filename, a type name or a field name — so **any draft of
that prose goes through `idiom_audit` before it lands.*** **I did not.** The second
gate run charged **ten `forbidden_hits`**, every one refusing a rung for carrying its
own correct code:

| entry | span | refused |
|---|---|---|
| `forbidden[0].rust` | the Option type name | `safe_naive.rs`, `safe_tuned.rs` |
| `forbidden[1]` | the Vec type name, and `Vec<u8>` | `verus.rs` |
| `forbidden[2]` | Option, Some, bool — named **in order to say the Rust rungs legitimately carry them** | all four |

⭐ **And the second-order instance is the one worth recording: the sentence I added
to EXPLAIN the repair re-backticked the Option type name and fired again.** That is
`.memory-php/02-ladder.md`'s own worked example verbatim. **Neither was found by
reasoning; both were found by running the audit and reading the output.**

### 8.4 ⚠ A SECOND, WORSE DEFECT THE SAME AUDIT FOUND — IN `required`, WHERE THE GATE CANNOT SEE IT

⛔⛔ **`required[4]`, `[5]`, `[6]` and `[7]` each ended with *"NO BACKTICKED SPELLING
IN THIS ENTRY"* and each contained a dozen.** `required[6]`, the R1h entry, carried
~30 — including bare `` `1` `` and `` `0` ``, which match every rung. ▶ **`required`
cannot fail the gate, so this would have SHIPPED.**

⚠⚠ **That is `ph53`'s own defect — an entry whose appositive and whose summary
disagree about what is pinned — reproduced on the very next row, and `ph53`'s is
costing a whole re-gate.** Repaired by stripping every backtick from those four,
which is what their English always claimed.

**The residual, measured:**

| | |
|---|---|
| `forbidden` spans that would fail the gate | **0** |
| `required` spans matching **every** rung (ANTI-signal) | **7**, all in entries whose English says *"Present in BOTH C rungs"* — intentional |
| `required` spans matching **no** rung (pins nothing) | **25**, all filenames, line citations and upstream spellings — `p42`'s known class |

⭐ **The three pins that DISCRIMINATE, which is what the declaration is for:**
`required[0].rust` `` `*constructed = true;` `` → `unsafe.rs` + `verus.rs` only;
`required[1].rust` `` `slot_read_unchecked` `` → the same two;
`required[1].c` `` `ph52_zval_dtor(expr_copy);` `` → **`c/kernel.c` only**, which is
the upstream fix as a one-line presence test.

### 8.5 ⚠ Two smaller ones, for completeness

* **`model.py::helpers` must be a `@property`.** `check.py::check_proof_domain` reads
  `mod.helpers` as an attribute and then `ns.update(helpers)`; a bare method gives
  `TypeError: 'method' object is not iterable` and the gate **dies with a traceback
  rather than a verdict**, mid-stage, after printing `ok` for stage 5d's first input.
  ⚠ A gate that aborts is not a gate that failed, and nothing in the record says
  which. `ph53`'s copy is a `@property`; the template does not say so anywhere.
* **Six `check.py:<line>` citations** — in `spec.md`, `NOTES.md`, `model.py` and
  `controls/negatives.py` — refused by `[doc-citation]`. Replaced with
  `check.py::<function>`. ⭐ The stage is right and the reason is in its own message:
  *a line citation into check.py rots (it has grown every task)*.

---

## §9 ⭐ EVERY HYPOTHESIS OF THE TASK FILE'S §2.3–§2.5 / §2.9 THAT I BROKE — **NAMED**

The task file says in terms: *"EVERYTHING IN §2.3–§2.5 AND §2.9 IS THE MANAGER'S
ANALYSIS … NONE OF IT HAS BEEN COMPILED … the engineer's first job is to break
them."* Ten statements; **six refuted, three upheld, one upheld-narrowed.**

| # | the statement | verdict | where |
|---|---|---|---|
| 1 | §2.3 *"A CLEAN STACK SLOT READS ZERO … with and without the sanitizer"* | ⛔ **REFUTED** — 4 of 16 cells read `235` / `94` / `113` / `82` on the first call under the shipped flags. The table was measured under ASan, where the fake stack hands out a zeroed frame, and generalised | §1.2 |
| 2 | §2.3 *"`_zval_dtor` … has **no** `case IS_NULL`"* | ⛔ **REFUTED** — `zend_variables.c:75` **is** `case IS_NULL:`, beside `default:` at `:76`. The conclusion holds; the reason does not | §3.1 |
| 3 | §2.3 hypothesis 2, REGISTERED: *"the defect may be PRESENT in `isolated` and OPTIMISED AWAY in `whole`"* | ⛔ **REFUTED** — the harness's `isolated`/`whole` axis moves **nothing**. The load-bearing boundary is the **callee** inline boundary, which `build.py` does not control. Under ASan it is the other way round (present in `whole`) | §1.3, §1.5 |
| 4 | §2.3 fallback (a), as stated: *"iteration 2+ … frees the previous iteration's already-freed pointer"* | ⛔ **REFUTED as stated, UPHELD corrected** — a repeated faulting arm is self-defusing, because `:244-245` writes `empty_string`. The history needs **two different arms** | §1.4 |
| 5 | §2.3 hypothesis 3: *"Stack reuse may not be exact … verify the offset"* | ✅ **UPHELD — it IS exact**, on all 16 cells, both opts, both modes, both compilers | §1.6 |
| 6 | §2.3 hypothesis 4: *"any `-fsanitize` stack mode DELETES the defect"* | ✅ **UPHELD, mechanism REFUTED** — it is not poisoning, it is ASan **relocating the frame** into a zeroed fake stack, +0x200 per call | §1.5 |
| 7 | §2.5 / F102: *"five named cases out of a byte, widened by the mask"* | ⛔ **REFUTED three ways** — SIX named cases (`IS_RESOURCE` missing), **12** of 256 not ten, and the `case IS_NULL` error above | §3 |
| 8 | §2.6: *"expect ASan to fire on the double free where the corpus says silent — state the divergence"* | ⛔ **REFUTED twice over** — ASan does **not** fire: the fake stack hides the read, and PHP's size-class cache means the second `efree` never reaches `free()`. There is no divergence to state; there is an explanation | §7 of `NOTES.md` |
| 9 | §2.9(1): *"the faithful R4 is again a `controls/` program and not a rung, and the shipped R4 again carries a witness the C does not"* | ✅ **UPHELD**, and the reproduction is **stronger**: the witness-free control prints **R1's** answer, not R1h's — `ph53`'s answered *correctly* | §6.1 |
| 10 | §2.9(2): *"Predicted: the witness is ~FREE here"* and *"the cost of a safety witness is O(the number of slots)"* | ⚠ **DIRECTION UPHELD, WORD REFUTED, LAW REFUTED** — `+0.622 %` is not free; and 3× the slots buys **15–35×** the cost, so the driver is the number of witness **READS** and whether they are **INDEXED** | §6.2 |

### 9.1 ⭐ And two the task file did not register, which the row found anyway

* ⭐⭐ **§2.7's guess was right for the wrong reason, and the conclusion is the
  opposite.** §2.7: *"the benign path `estrndup`/`emalloc`s the printable string and
  the teardown frees it, so **O(1) per call looks right**"*. ⛔ **It is O(n_ops)** —
  up to five `emalloc`s and three `efree`s **per concat op** — so §B1a's precondition
  **fails** and §B1a.3 binds. ▶ `ph53` is the O(1) exception at **1 of 2**, not 2 of 2,
  and this row is the second where the cross-language column carries the caveat.
* ⭐⭐⭐ **`:243`'s cost is invisible to family A and the row's headline therefore
  moves column.** `inside_share` is **22.24 %** and the difference is 100 % outside
  it, which is why item 76 reads `0.00 %` in A1 and `−0.342 %` in W1.

---

## §10 ⛔ WHAT THIS ROW DOES **NOT** SHIP, STATED RATHER THAN LEFT TO BE NOTICED

### 10.1 ⛔⛔ NO `controls/spellings.py` — SO OPEN ITEM 81 IS **UNTESTED BY THIS ROW**

`ph45`'s respelling suite is 128 cases, `ph53`'s 161, and item 81 predicts a sixth
would find a **fifth** defect in the shared machinery. **This row has none.**

**What that costs, concretely:**
* **the row publishes its headlines with NO in-contract spread beside them.** §5's
  `−0.3497 %` and §6.2's `+12.41 Ir/call` are the *shipped* cells' figures; how much of either
  survives a search over the variants the declaration leaves free is **unmeasured**.
  `.memory-php/02-ladder.md` is explicit that *every pattern owes an in-contract
  spread beside its headline*.
* **item 81's monotone-in-suite-size law (54 → 2 missed, 75 → 1, 128 → 1 found, 161 →
  the fourth, `_043` → the fifth) gets no sixth data point from here.**
* ⚠ The task file asked for it under §3.4 and §1.3 and **I did not write it.** It is
  the largest single omission in the row and I am not going to dress it as a
  judgement: it is scope I ran out of, and the row's other controls (`d0_stack.py`,
  `tag_sweep.py`, `r1h_onelinedel.py`, `negatives.py`) each landed with their own
  must-fire and must-NOT-fire negatives as §H requires — **six controls and `model.py`'s own
  sweep, 85 arms in total** (§11's table) — so the §H obligation on what *did* land is met.

⭐ **One thing the absence did buy, recorded because it is the only thing it bought:**
the `.temp/` audit I wrote instead (`idiom_audit`, §8.3/§8.4) found **two** defects in
the declaration — ten live `forbidden_hits` and four self-contradicting `required`
entries — and the second class **cannot fail the gate**, so without it the row would
have shipped `ph53`'s own defect.

### 10.2 ✅ `controls/dblfree.py`, `digest.py`, `firstcall.py` and `tu_boundary.sh` — WRITTEN, because they were CITED (see §17)

The first draft of this report said these files did not exist and that `NOTES.md` §5b
carried a citation defect. **Both halves were right, and §17 is the repair and the
finding it produced.** They exist now, two of them with real content and their own
must-fire suites, and every cited path in the row resolves.

### 10.3 ✅ EVERY OTHER CITED PATH IN THE ROW RESOLVES

Checked mechanically after §17's repair: the **only** cited path in the row that does not
resolve is `controls/spellings.py`, in `NOTES.md` §9's *"`controls/spellings.py` DOES NOT
EXIST IN THIS ROW"* — a statement **of** the absence rather than a pointer at a file.
§10.1 is the cost of that absence.

---

## §11 THE ROW, AS BUILT

```
patterns-php/ph52-concat-copy-uninit/
  spec.md                      the hashed contract
  NOTES.md                     every measurement, each with its mechanism
  README.md                    the reader's entry point
  model.py                     3 implementations · 69 synthetic windows · 4 must-fire mutants · 1 must-NOT-fire
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  c/kernel.c  c/kernel_hardened.c  c/kernel.h  c/main.c
  c/emalloc_shim.h -> ../../../common-php/emalloc_shim.h      (§B2, unconditional)
  inputs/gen.py + small.bin large.bin adversarial-{dblfree,safe,nowin,trunc}.bin
  controls/
    d0_stack.{c,py}            DELIVERABLE #0's 16-cell table, 5 selftest arms
    d0_noinl.h                 the TU-boundary macro the probe shares with the kernel
    tag_sweep.{c,py}           the 12-of-256 figure, 15 assertions
    r1h_onelinedel.py          §C's owed argument AS A CHECK, 11 cases
    negatives.py               --verus (7 arms) --miri (8 arms) --firstcall (16 cells)
    mu_unwrapped.rs            the obligation with NO trusted item, 6/0
    r4_nowitness.rs            the faithful witness-free R4 — it REPRODUCES the defect
    7412202c43e7.patch         the upstream commit, committed
```

**Control selftests, all PASS — 85 arms over 6 controls plus `model.py`'s own sweep:**

| control | arms | what the must-fire half is |
|---|---:|---|
| `r1h_onelinedel.py --selftest` | **11** | 8 must-fire, 3 must-NOT-fire; incl. a hardened kernel that **added a guard** instead of deleting the call |
| `negatives.py --firstcall` | **16** | 16 C cells, R1 vs R1h on the blob `inputs/` cannot carry; **recorded, not required** |
| `tag_sweep.py --selftest` | **15** | 9 must-fire claims, 6 must-NOT-fire; incl. the `0x01`-vs-`0x81` *two reasons, one outcome* arm |
| `digest.py --selftest` | **10** | 5 must-fire, 5 must-NOT-fire; incl. the **palindrome** arm that refuted my own assertion (§17) |
| `dblfree.py --selftest` | **8** | 4 must-fire, 4 must-NOT-fire; `n_iters ∈ {1,2,8,64}` × 4 cells |
| `negatives.py --miri` | **8** | 7 must-NOT-fire, 1 must-fire: **the read itself** |
| `negatives.py --verus` | **7** | 2 must-NOT-fire, 4 must-fire, 1 cosmetic must-NOT-fire; **V1 is §2.9(1)** |
| `d0_stack.py --selftest` | **5** | N2/N4 must-fire, N1 must-NOT-fire, N3 recorded, **N5 checked against `harness/build.py` itself** |
| `model.py` selfcheck | **5** mutants | 69 synthetic windows × 3 implementations; 4 must-fire, 1 must-NOT-fire |
| **total** | **85** | |

`controls/tu_boundary.sh` and `controls/firstcall.py` are documented entry points and
carry no arms of their own (§17).

**§F6:** `python3 .tasks-php/citecheck.py` reports **0 `.temp/` citations** for this
row in `spec.md`, `NOTES.md` or `controls/*`. ⚠ It found one on the first pass —
`NOTES.md -> .temp/php45/neg` — and it was repaired by restating the claim without the
pointer, which is §F6's own prescription.

---

## §12 ⭐⭐⭐ THE BIGGEST SINGLE FINDING OF THE TASK, AND IT CAME FROM A GATE STAGE REFUSING THE ROW

**ASan fires on the row's two BENIGN inputs and is SILENT on its adversarial one.**
Measured under `check.py::_san_build`'s own line
(`gcc -O1 -g -fsanitize=address,undefined -static-libasan -DSLB_ISOLATED`), both C
rungs, all six inputs:

| input | R1 | R1h |
|---|---|---|
| **`small.bin`** | ⛔ **`heap-use-after-free`**, exit 1 | ✅ clean |
| **`large.bin`** | ⛔ **`heap-use-after-free`**, exit 1 | ✅ clean |
| `adversarial-dblfree.bin` | ✅ clean | ✅ clean |
| `adversarial-safe.bin` | ✅ clean | ✅ clean |
| `adversarial-nowin.bin` | ✅ clean | ✅ clean |
| `adversarial-trunc.bin` | exit 5 | exit 5 |

### 12.1 The diagnostic and the trace

```
ERROR: AddressSanitizer: heap-use-after-free on address 0x503000000050
READ of size 4 at 0x503000000050 thread T0
  #0 php_shim_efree            c/emalloc_shim.h:414   <- real_size = REAL_SIZE(p->size)
  #1 ph52_zval_dtor            c/kernel.c:139         <- zend_variables.c:45 STR_FREE_REL
  #2 ph52_make_printable_zval  c/kernel.c:209         <- zend.c:243  THE DEFECT
  #3 ph52_concat_function      c/kernel.c:271         <- zend_operators.c:1152
  #4 kernel                    c/kernel.c:326
freed by thread T0 here:
  #1 php_shim_reset            c/emalloc_shim.h:269   <- the top of a LATER kernel call
```

A tracing build of the same kernel, instrumented per dtor site:

```
OP 13  site=1188 val=0x506000010718   site=1191 val=<ph52_empty_string>
OP 14  arms 0/0                       <- the PASS-THROUGH arm on BOTH sides: this call
                                         writes neither slot and tears down neither
OP 15  arms 1/4 aux 214/75            <- the faulting arm on side 1
       site=243 type=3 val=0x503000000058     <- a pointer from several ops back
```

### 12.2 ⭐⭐ The mechanism: ASan's fake stack breaks the row's assumption in **both** directions

| | measured |
|---|---|
| `:243`-reaching calls on `small.bin` under ASan | **283** |
| of which read a freshly **ZEROED** fake frame (`type=0 val=(nil)`) | **282** |
| of which read a **RECYCLED** frame carrying an older call's bytes | **1** |

▶ **ASan CREATES the fault on an input the real stack keeps clean.** And on the real
stack the corpus is benign, measured over the whole run rather than argued: the same
tracing kernel at `-O1 -DSLB_ISOLATED` **without** `-fsanitize`, over all **25,000**
iterations of `small.bin`, shows **every** `:243` reading
`type=3 val=<ph52_empty_string>` — one unique value, `nm` confirms the symbol — so
`STR_FREE` skips and nothing is freed. ✅ **That is what the published u64 rests on.**

### 12.3 ⛔ And the adversarial blob is silent for TWO FURTHER independent reasons

1. **`n_iters = 1` and two ops is far too few for the fake stack to recycle**, so
   `:243` reads a freshly zeroed frame and the defect the blob exists to trigger does
   **not happen under ASan at all**.
2. **Even when it does, PHP's own allocator swallows it**: `php_shim_efree` of a block
   under 88 bytes never reaches `free()` (`zend_alloc.c:270-279`) — `PROTOCOL_PHP.md`
   §B1.1's measured fact on a third row.

### 12.4 ⛔⛔ SO §2.6's PREDICTION IS REFUTED **THREE WAYS**

*"Expect ASan to fire on the double free where the corpus says silent — state the
divergence, with the exact diagnostic."*

1. **ASan never reports the double free**, on any input.
2. **What it reports is a use-after-free it CAUSED ITSELF**, on the *benign* inputs.
3. **The mechanism is frame recycling**, which has nothing to do with the allocator
   the prediction was about.

⭐⭐ **And it is F102's own `0xbe` correction with the SIGN REVERSED.** F102 records
that `ph53`'s `0xbe` was *a detector-dependent observation presented as a row
property*. Here the detector does not **reveal** the defect — it **manufactures** one.
▶ **The row caught it before publishing only because a gate stage refused it.** My
own §7 had written the opposite, from a short probe, and would have shipped.

### 12.5 ⚠⚠ AND IT MEANS `inputs/gen.py`'s THREE RULES ARE RULES ABOUT THE **REAL STACK**

No blob property can repair this: any corpus that exercises an allocating arm leaves a
dangling slot at *some* call boundary, and a recycling fake stack can read it from an
arbitrary distance back. ▶ The row **states** that rather than restricting the corpus
to the three non-allocating arms, which would cost §A2a rule 1's coverage.
⭐ **`.memory-php/02-ladder.md` F31's limitation, in a new form.**

⚠ `model.py::sanitizer_expect` therefore returns **`fires`** for `small.bin` and
`large.bin` and `clean` for the four adversarial blobs, and its docstring plus the
row's `NOTES.md` §7 carry the whole argument — ⛔ **with an explicit *do not read
`fires` as "the benign corpus exercises the defect"***, because on the binaries every
number in `results-php/` was taken with, it does not.

---

## §13 ⚠ WHAT I AM UNSURE OF — its own section, as §4.8 asks

⭐ **`UNTESTED` and *"I could not tell"* are valued answers.** In rough order of how
much they would change the row:

1. ⛔⛔ **NO RESPELLING SEARCH — the row publishes headlines with no in-contract
   spread beside them.** §10.1. `ph45`'s suite is 128 cases, `ph53`'s 161, and open
   item 81's prediction of a **fifth** machinery defect gets **no data point** from
   here. I ran out of scope; I am not dressing it as a judgement. ⚠ It also means
   `.memory-php/02-ladder.md`'s *every pattern owes an in-contract spread beside its
   headline* is **unmet on this row**.
2. ⚠⚠ **I DO NOT KNOW HOW REPRODUCIBLE THE 1-IN-283 ASan RECYCLING IS.** §12's
   inversion is measured on this box, this glibc, this gcc, this link order. The
   *existence* of the mechanism is solid (the trace shows the recycled frame and the
   freed block); the **frequency** is one observation and ASan's fake-stack size
   classes are not something I characterised. ▶ A reviewer who re-runs it and sees a
   different count has not refuted anything; one who sees **clean** has, and
   `model.py::sanitizer_expect` would then be wrong in the other direction.
3. ⚠ **§6.2's two-row law rests on n = 2.** *The cost of a safety witness tracks the
   number of witness READS and whether they are indexed, not the number of slots.*
   Three `T3` candidates remain (`ph49`, `ph50`, `ph51`). ⛔ **Do not quote it as a
   law.**
4. ⚠ **I could not tell whether `inside_share` being 22.24 % is a property of the row
   or of my extraction.** It is caused by the `PH52_NOINLINE` substitution, which is
   forced by fidelity (§1.3) — so the two are entangled, and *"ph52 publishes in W1"*
   is downstream of a decision that could have gone the other way if `build.py`
   compiled more TUs. ⭐ **That coupling is worth a reviewer's eye: `inside_share` is
   not independent of the extraction's fidelity choices**, and the statistic rule
   treats it as if it were.
5. ⚠ **§8e's cross-language ratio (C is 2.95× the Rust) is not a safety figure and I
   cannot make it one.** §B1a.3's label is applied; the underlying comparison — a real
   allocator against simulated counters — is not repairable at this row's allocation
   order.
6. ⚠ **`identity` is `norel` at `-O3` and `differ` at `-O0`.** I did not chase why
   `-O0` differs by exactly 3 instructions. The pin states what was measured and the
   explanation in its `why` is labelled a reading.
7. ⚠ **The kernel-overlap heuristic reads 19 % against a `narrowed` expectation of
   25 %** (§7). I think it is right about the text and wrong about the row, and I give
   the reason — but it is a judgement a reviewer may take the other way, and it is the
   **first `narrowed` php row where the demoted floor would have fired**.
8. ⚠ **`controls/negatives.py --firstcall` measured R1 == R1h on the op-0-faulting
   blob** (the 95.3 % outcome). **Recorded and not required**: a different libc,
   kernel or link order could put one of the 12 freeing tags there. The corpus does
   not rest on it (rule R1 is what makes that true) but the control's output will
   change without notice.
9. ⚠ **`--miri` ran 8 arms and all behaved, but Miri's `n_iters` is 4** in the gate
   (and 1 in `negatives.py`'s blob). **Miri has not been run at a scale where ASan's
   recycling analogue could appear**, and I do not know whether Miri's own stack
   model reuses frames the way the real stack does.
10. ⚠ **`model.py`'s `_dumb` shares the *semantics* of the other two by construction,
    not by derivation.** It is a third spelling of the same understanding, and if my
    understanding of `:1188`'s ordering were wrong, all three would be wrong together.
    The C is the only independent check, and it agrees on every measured window —
    which is the strongest thing I can say and is not the same as *verified*.
11. ⓘ **`verus_checked`, `problems` and `forbidden_hits` are NOT gate-record fields**
    (F99). Everything quoted in this report comes from: `results-php/ph52-*.json`
    (`ir`, `checksum`), `results-php/gate/ph52-*.json` (the verdict fields), the gate
    log at `.temp/php45/gate*.log`, direct `callgrind_annotate` runs, and the
    controls' own stdout. **Each figure's source is named where it is quoted.**

---

## §14 ⭐ WHAT THE ROW PUBLISHES THAT NO OTHER php ROW DOES

Recorded compactly so the manager can route it, and **every item has its measurement
above**:

1. ⭐⭐⭐ **THE DEFECT IS IN THE PUBLISHED u64.** `inputs/adversarial-dblfree.bin` and
   `inputs/adversarial-safe.bin` differ in **one op byte**; R1 prints
   `272040826665440682` and R1h `272040826666539789` on the first and all six rungs
   agree at `254123829775225275` on the second. ⚠ `ph53`'s own `idiom.why` records
   that *"the published u64 carries no evidence whatever that the defect exists"*.
2. ⭐⭐⭐ **THE SANITIZER FIRES WHERE THE ROW IS BENIGN AND IS SILENT WHERE IT IS
   ADVERSARIAL** (§12), and the mechanism — ASan's fake stack recycling 1 frame in 283
   — is traced. **A detector manufacturing the defect it was asked to find.**
3. ⭐⭐ **THE UPSTREAM FIX IS PROFITABLE, NOT FREE.** `−0.342 %` (gcc) / `−0.740 %`
   (clang) in W1 on `small.bin` at `O3/isolated`, and **exactly `0.00 %` in family A
   because family A cannot see it** — open item 76 upheld in one column and refuted in
   the other (§5).
4. ⭐⭐ **THE WITNESS-FREE R4 REPRODUCES THE C's DEFECT BIT FOR BIT** — it prints R1's
   answer, not R1h's. `ph53`'s answered *correctly* (§6.1).
5. ⭐⭐ **R4 AND R5 ARE THE SAME MACHINE CODE AT `-O3`** (`identity: norel`, 433
   instructions each, equal `md5_raw_norel`). No other php row reports that.
6. ⭐ **95.3 % OF TAG BYTES MAKE THE DEFECT A NO-OP** — 12 of 256 tear anything down, 8
   of 256 reach `efree` (§3). **The answer to *why do uninitialised-read bugs survive
   for years in shipped code*.**
7. ⭐ **THE UPSTREAM FIX IS COMPLETE**, enumerated over every `expr_copy` read in the
   function — which is what lets R2–R5 be ports of R1h and the adversarial input ship.
   `ph53` could do neither (§2.3).
8. ⭐ **R3 IS A PORT OF R1h, MADE STRUCTURAL** — returning the printable makes the
   deleted line *unwriteable*, not merely absent, and R2-vs-R3 is therefore *the
   upstream fix measured in safe Rust* at `−6.385 %` (§8c of `NOTES.md`).
9. ⭐ **THE C's SLOT HAS FOUR STATES AND SAFE RUST HAS THREE** — `take()` makes the
   dangling state unrepresentable — and that is **not** `Option` reinventing the
   upstream fix: the fix deletes the teardown and keeps the states; `Option` keeps the
   teardown and deletes the state.
10. ⚠ **§B1a's PRECONDITION FAILS HERE**, so `ph53`'s O(1) exception stands at **1 of
    2** rather than 2 of 2, and `ph64` gains a sibling.
11. ⚠ **THE TIER AGREES WITH THE CATALOGUE**, so open item 75 is **2 of 3** rather
    than 3 of 3 and should be carried as *sometimes* rather than closed as *yes*
    (§7).
12. ⛔ **A `harness/` PROPERTY:** `check.py::check_trusted_twins`'s `n_twins == 0`
    rule hard-fails a row whose **only** contract-bearing trusted item is genuinely
    untwinnable — the same objection `TASK_007` accepted when it deleted
    `MAX_TWIN_JUSTIFICATIONS`, one item down. **ph52 is the first row in either
    programme to reach it, because it is the first whose trusted surface is small
    enough** (§8.1).

---

## §15 THE SIX-RUNG CROSS-CHECK, ALL 32 CELLS × ALL 6 INPUTS

Driven directly against `model.py`, independently of the gate:

| input | model | distinct values over the 32 cells | verdict |
|---|---|---|---|
| `small.bin` | `15768976536999838170` exit 0 | **1** | ✅ all 32 == the model |
| `large.bin` | `2957760381129677675` exit 0 | **1** | ✅ all 32 == the model |
| **`adversarial-dblfree.bin`** | `272040826666539789` exit 0 | **2** | ⭐ the **8 R1 cells** give `272040826665440682`; the other **24** give the model's value |
| `adversarial-safe.bin` | `254123829775225275` exit 0 | **1** | ✅ all 32 == the model |
| `adversarial-nowin.bin` | `0` exit 0 | **1** | ✅ |
| `adversarial-trunc.bin` | `''` exit 5 | **1** | ✅ |

⭐⭐ **Exactly one input separates exactly one rung, and it is the right one.** R1
diverges; R1h, R2, R3, R4 and R5 all agree with `model.py`. That is stage 2 satisfied
on the measured corpus and stage 4 recording the adversarial divergence, and it is
what §12's first claim rests on.

---

## §16 ⚠ THE ROW CARRIES ONE **BLOCKED** ROW, AND IT IS THE RIGHT ONE

Stage 5c-twin's shout, quoted as a field:

> `!! [twin] stage 5c-twin ran but certified 1 twin(s) for 2 trusted item(s), with 1
> justified away (['verus.rs:slot_read_unchecked']). No strength claim is being made
> about the justified ones.`

and `rep.block("twin", "verus.rs `slot_read_unchecked` (strength unchecked)")`.

⭐ **That is `check.py`'s own design working as intended and it is what an unchecked
trusted precondition actually is — a row nothing verified.** The verdict is therefore
**PASS-WITH-BLOCKED-ROWS** and not a bare PASS, which is honest: `slot_read_unchecked`'s
`requires` is **trusted**, and §11d's collision is why it cannot be twinned.

⚠⚠ **What IS checked in its place, and it is written out in
`verus.twin_justifications` inside the hashed block:**

1. it is **not vacuous** — 5a confirms it constrains every parameter its body uses;
2. it is **not a tautology** — 5c-req probed 4 `requires` conjuncts and deleted 2;
3. **deleting the caller's guard breaks the proof** — `negatives.py --verus` V1/V2/V3;
4. **`controls/mu_unwrapped.rs` verifies the unwrapped shape at 6/0 with NO trusted
   item**, so the contract asserted here is *demonstrably the one vstd asserts* —
   ⭐ a stronger statement than a hand-written twin would have made;
5. **Miri is silent on the shipped rung and loud on the witness-free control**, on a
   blob `inputs/` cannot carry.

⚠ **And `win_get_unchecked` IS twinned**, which is the whole reason the stage ran at
all rather than refusing the row (§8.1, §8.2).

---

## §17 ⛔⛔ FOUR CITATION DEFECTS I FOUND IN MY OWN COMMITTED FILES — AND LAW 14 DECIDED THE REPAIR

⚠ **Found by a script that asks *does every cited path resolve*, not by reading** — and
after I had already re-read all of it once. Four paths were cited by committed files and
did not exist:

| cited path | cited by | digest |
|---|---|---|
| `controls/digest.py` | `c/kernel.c`, `c/kernel.h`, `c/kernel_hardened.c`, **all four `.rs` rungs** | **MEASUREMENT** |
| `controls/tu_boundary.sh` | `c/kernel.c`, `c/kernel_hardened.c` | **MEASUREMENT** |
| `controls/dblfree.py` | `inputs/gen.py` | **MEASUREMENT** |
| `controls/firstcall.py` | `inputs/gen.py` | **MEASUREMENT** |

⭐⭐ **ALL FOUR ARE IN THE MEASUREMENT DIGEST, WHICH IS `.memory-php/04-process.md`
LAW 14 LANDING ON A ROW FOR THE SECOND TIME**: *a C kernel's comments are hashed at
MEASUREMENT price, so provenance prose inside one is effectively frozen.* ⚠ Law 14's
first instance is `ph53`'s `c/kernel_hardened.c:8-9`, which **cannot be repaired at all**
at re-gate price. ▶ **ph52's instance has a repair law 14 does not mention: correcting
the POINTERS costs a 32-cell re-measure, and WRITING THE NAMED FILES costs ONE RE-GATE,
because `controls/*` is gate-only.** ⭐ **So the cheap repair and the honest repair were
the same one.**

⚠ **Two of the four are thin and say so in their own headers.**
`controls/tu_boundary.sh` is four lines that `exec` `d0_stack.py`; `controls/firstcall.py`
calls `negatives.py::arm_firstcall`. ⛔ **Neither is a second implementation and neither
may become one** — two copies of a measurement is how they disagree, which is
`harness/asm.py`'s founding lesson.

⭐⭐ **The other two are real controls the row wanted anyway, and `digest.py` found a
defect in MY OWN reasoning within minutes of existing.** Its arm **N3c** asserted that
folding the object handle's decimal digits most-significant-first differs from
least-significant-first on every handle ≥ 10. **It does not: a PALINDROME folds the same
either way, and the agreeing set is exactly the 35 palindromic handles in a byte** (10
one-digit, 9 two-digit, 16 three-digit). ▶ **A corpus whose handles were all palindromic
would be blind to the digit order on 35 of 256 values** — `ph03`'s monoculture with a
different shape — and `inputs/gen.py` spans all three digit counts but does **not**
assert non-palindromic handles. ⚠ **Recorded in `NOTES.md` §13.7 rather than claimed as
covered**, and the assertion was fixed to say what is true (*the agreeing set is exactly
the palindromes*) rather than weakened.

| control | arms |
|---|---|
| `controls/digest.py --selftest` | **10** (5 must-fire, 5 must-NOT-fire) — the three constants against their literals, all 256 handles three ways, the palindrome set, and the 4-digit bound |
| `controls/dblfree.py --selftest` | **8** (4 must-fire, 4 must-NOT-fire) — `n_iters ∈ {1,2,8,64}` × `{gcc,clang}` × `{O0,O3}` |

⭐ **And `dblfree.py` turned `NOTES.md` §5b from prose into a table:** R1 exits 0 at
`n_iters = 1` with `272040826665440682` and **aborts with `free(): double free detected`
at every `n_iters ≥ 2` in all four cells**, while R1h exits 0 at every count. ▶ **So
`gen.py`'s `n_iters = 1` is measurably the only value at which R1 completes** — the
choice is load-bearing rather than tidy, and I had asserted that from a different
probe's shape.

---

## §18 ⚠ `model.py` IS IN THE **MEASUREMENT** DIGEST, SO CHANGING THE ORACLE COSTS A 32-CELL RE-MEASURE

Measured, not assumed. `harness-php/gate.py --tool measure --check-stale` after the
`sanitizer_expect` repair (§12):

```
STALE   results/gate/ph52-concat-copy-uninit.json  patterns/ph52-concat-copy-uninit/NOTES.md
STALE   results/gate/ph52-concat-copy-uninit.json  patterns/ph52-concat-copy-uninit/README.md
STALE   results/ph52-concat-copy-uninit.json       patterns/ph52-concat-copy-uninit/model.py
18 record(s) examined, 2 STALE
```

⭐ **Two different prices in one listing**, and the task's trap 5 asks which side of the
line each edit is on:

| file | digest | price of an edit |
|---|---|---|
| `NOTES.md`, `README.md`, `controls/*` | gate | **one re-gate** |
| `spec.md` (the contract block) | gate, **and `contract_sha256`** | one re-gate, and the hash moves |
| `c/*`, `inputs/gen.py`, the four `.rs` rungs | **measurement** | **32-cell re-measure** |
| ⚠ **`model.py`** | **measurement** | **32-cell re-measure** |

⛔⛔ **THE LAST ROW IS THE ONE WORTH RECORDING.** `model.py` is the **oracle** — it
computes no cell's number, and `sanitizer_expect` is a *declaration about what a
sanitizer does*, which cannot move an `Ir` count. ▶ **Changing it still costs a full
re-measure**, because `measure.py::measurement_sources` hashes it. ⭐ **That is
`.memory-php/04-process.md` law 14's family with a new member: the law is written about
a C kernel's COMMENTS, and `model.py`'s DECLARATIONS are in the same digest for the same
reason and at the same price.** ⚠ On this row the repair was forced by a gate stage
(§12) and so was unavoidable; the observation is that **a row which discovers something
about its own sanitizer behaviour after measuring pays 32 cells for saying so.**

⚠ **So the row's command sequence was NINE, not six**: `build → measure → report →
gate → report → gate` (the documented six of `PROTOCOL_PHP.md` §E), then
`measure → report → gate` **again**, because §12's finding changed `model.py` and
`model.py` is in the measurement digest. ⭐ **And the six in §E are a FLOOR, not a
count**: this row ran the gate **eight** times, and every extra run was a stage
refusing it and being right — 5c-twin (§8.1), `idiom-forbidden` (§8.3), `doc-citation`
(§8.5), `sanitizer` (§12), plus the `[tables]` chain §E itself documents. **Recorded so
the next row budgets for it.**

---

## §19 DEFINITION OF DONE — ITEM BY ITEM

| § 4 item | where | state |
|---|---|---|
| **1** Deliverable #0 first and in writing, all four C cells, with the fallback taken and why | §1 (16 cells, not four) | ✅ and **five refutations** |
| **2** the row built and gated; `verdict`, `failures`, `complete_run`, `identity`, `contract_sha256` as fields | §20 | ✅ |
| **3** §2.1's R1h argument, token by token | §2, and `controls/r1h_onelinedel.py` makes it a **check** | ✅ |
| **4** item 76 tested; if not `0.00 %`, where the cost came from | §5 | ✅ **both answers**, with the mechanism read off the per-function split |
| **5** §2.9's two predictions, each UPHELD or REFUTED with the evidence | §6.1 (upheld, strengthened), §6.2 (direction upheld, word refuted, law replaced) | ✅ |
| **6** §2.5's tag sweep as a `controls/` program with its own negatives, and the measured count | §3 — `controls/tag_sweep.{c,py}`, 15 assertions, **12 of 256** | ✅ |
| **7** §2.2's tier with its itemisation, and my direction on item 75 | §7 — `narrowed`, **agrees** with the catalogue, item 75 → **2 of 3** | ✅ |
| **8** what I am unsure of, in its own section | §13, eleven items | ✅ |
| **9** every §2.3–§2.5/§2.9 hypothesis I broke, named | §9's ten-row ledger, **6 refuted** | ✅ |

## §20 THE GATE RECORD, **AS FIELDS** — definition-of-done item 2

Read out of `results-php/gate/ph52-concat-copy-uninit.json` after the last gate run,
by `json.load` and not by eye:

| field | value |
|---|---|
| `pattern` | `ph52-concat-copy-uninit` |
| `invocation` | `ph52-concat-copy-uninit` |
| **`verdict`** | **`PASS-WITH-BLOCKED-ROWS`** |
| **`failures`** | **`[]`** — the empty list, length 0 |
| **`complete_run`** | **`true`** |
| **`contract_sha256`** | **`d73ab3298ecd44f26a3288a500241134eef0ffc1f8dc6363d5f47525a0641fe3`** |
| `blocked` | 1 entry — `section: "twin"`, `row: "verus.rs ``slot_read_unchecked`` (strength unchecked)"` (§16) |
| `expected_hang` | `[]` |
| `run_timeout_s` | `{}` — nothing needed a per-input timeout |
| `controls_json` | `{}` |

⚠ **`verdict` is `PASS-WITH-BLOCKED-ROWS` and `failures` is empty, and those are two
different facts.** A blocked row is an obligation the gate has decided it **cannot
test**, recorded with the reason; it is not a failure it is tolerating. §16 argues the
one this row carries is the right one.

### §20.1 `identity`, both levels, as fields

| `pair` | `opt` | **`level`** | `expected` | `md5_raw_equal` | `counts_a` / `counts_b` |
|---|---|---|---|---|---|
| `unsafe vs verus` | `O0` | **`differ`** | `differ` | `false` | `[773, 773, 4458]` / `[770, 770, 4441]` |
| `unsafe vs verus` | `O3` | **`norel`** | `norel` | `false` | **`[433, 425, 1685]` / `[433, 425, 1685]` — equal in all three, `pad` `[11, 11]` both** |

Both match `expected`, which is what `spec.md`'s `identity` block pinned. ⭐ **The `O3`
`norel` is the row's headline on this axis** (README, §14): R4 and R5 are the same
machine code once relocations are masked — **`md5_raw_equal` is `false` and the level
is still `norel`, which is the whole point of the level**: `md5_fn_a`
(`6a3cf1cbd998…`) and `md5_fn_b` (`adcd3542592f…`) differ because the two binaries
place the same code at different addresses, while the relocation-masked digest agrees
and **all three instruction counts are equal — `433 / 425 / 1685` on both sides** —
so the proof costs **zero instructions** at `-O3` while costing 3 instructions at `-O0`
(`773 → 770`, and the `verus` cell is the *smaller* one, which is the `#[verifier::…]`
attributes' effect on the unoptimised prologue rather than anything the proof adds).

### §20.2 `marginal_ir_per_call` — B1, `O3/isolated/small.bin`, all eight rungs

| rung | B1 Ir/call |
|---|---:|
| `c-gcc` | 5833.79 |
| `c-gcc-h` | 5813.39 |
| `c-clang` | 5430.26 |
| `c-clang-h` | 5389.36 |
| `safe_naive` | 2250.88 |
| `safe_tuned` | 2105.88 |
| **`unsafe`** | **1975.16** |
| **`verus`** | **1975.16** |

⭐⭐ **`unsafe` and `verus` agree to the last published digit in B1 as well as in the
disassembly** — `identity: norel` showing up in a second instrument. ⛔⛔ **AND THE C
ROWS ARE 2.8× THE RUST ROWS IN THIS COLUMN, WHICH IS NOT A SAFETY FIGURE**: §B1a's
O(1)-allocation precondition fails on this row (O(n_ops) `emalloc`/`efree` per kernel
call), so §B1a.3 binds and the cross-language comparison is labelled everywhere it
appears — NOTES §8e states it, and the C figure is largely `malloc`/`free` against the
Rust rungs' counters-only simulation of `php_shim_tally()`. **The same-language
comparisons (R1-vs-R1h, R2-vs-R3-vs-R4-vs-R5) are unaffected** and are where every
claim in this report lives.

⚠ `marginal_ir_env` is recorded with the record: `envp_stack_bytes: 3698`,
`nvars: 49`, `repo_path_bytes: 48`, `tuning_vars: {"LD_PRELOAD": ".../libstdbuf.so"}`.
Its own `domain` string says comparability against another record needs all four to
match, and calls that **necessary, not proved sufficient**. I did not compare this
row's B1 against any other row's.

### §20.3 the other fields I checked rather than assumed

| field | value | why it mattered |
|---|---|---|
| `verus.verus.rs.verified` / `.errors` | **33 / 0** (`pinned: 33`) | and **34/0** under `--cfg slb_twin`; `spec.md` pins both |
| `verified_twins` | 1 twin, `win_get_unchecked` → `slb_twin_win_get_unchecked`, `signature_identical: true` | §12 — this is the repair that was also worth −7.12 % |
| `requires_strength` | `control_verified: 33`, mutants ran with `nonlinear_arith`; `bit_vector` recorded `inapplicable` | the `requires` are non-vacuous |
| `proof_domain` | `requires_ok: true` on all six inputs; `calls: 1` on the two adversarial blobs that reach the kernel, `0` on `adversarial-nowin.bin` | ⚠ a `0` here is honest and is why that blob is a **reachability negative**, not a measurement input |
| `idiom_audit` | `spellings: 68`, `pairs: 196`, `present: 36`, `forbidden_spellings: 27`, **`forbidden_hits: 0`**, `hits: []` | §17's 10-hit episode ended here |
| `published_table` | `verdict: "FRESH"`, `cited: ["d73ab3298ecd"]` | matches `contract_sha256` |
| `table_render` | `verdict: "FRESH"`, `render_sha256 == published_sha256` (`5103c9b27251…`) | stage 9c — the *content*, not just the declaration |
| `sanitizer` / `sanitizer_hardened` | `fired: false` on all four adversarial blobs, `exit == expected_exit` | ⭐ the inversion of §11: ASan fires on the two **benign** inputs and is clean on the adversarial ones |
| `loud` | **4 advisories** (`doc-citation-other`, `collapse-ir`, `twin`, `twin`), **0 failures** | incl. `doc-citation-other`: **4 line citations into `build.py` that I chose NOT to repair**, because they sit in measurement-hashed files and re-citing a pointer by function costs a 32-cell re-measure (§18, RECAP item 38) |
| `codegen_cfgs` | `verdict: "OK"`, `build_py_cfgs: ["slb_isolated"]`, `missing: []`, `unresolved: 0` | ⚠ so the `#[cfg(slb_twin)]` twin is **not** a cfg `build.py` passes — it is reached by stage 5c-twin's own `--cfg`, which is why the shipped count is 33 and the twin count 34 |
| `verus_exit_anomalies` | `[]` | no Verus invocation exited oddly while reporting success |
| `tcb_items` | 4 `#[verifier::external_body]` items: `load_input`, `emit`, `win_get_unchecked`, `slot_read_unchecked` | ⚠ **only the last two are trusted items the rules govern** (`_is_trusted` wants `external_body` **plus an `ensures`**); `load_input`/`emit` are the I/O boundary every row has. `body-less trusted declarations: 0`, and `spec.md` declares 0 |

## §21 ⭐ THE W1 FIGURES RE-DERIVED FROM THE RAW CALLGRIND OUTPUT, AND THE ONE CROSS-CHECK THAT IMPRESSED ME

Before deleting `.temp/php45/cg/` under CLAUDE.md rule 1 I re-read every `summary:`
line out of the 25 callgrind files and checked it against what the row publishes.
Distilled to `.temp/php45/cg_totals.json`; rebuildable by `.temp/php45/w1_rebuild.sh`.

| NOTES.md claim | figure | raw `summary:` | |
|---|---:|---:|---|
| §8e R1 `c-gcc` W1 | 146,152,976 | `n-c-gcc.out` 146,152,976 | ✅ |
| §8f R4 **after** the repair | 49,549,469 | `n-unsafe.out` 49,549,469 | ✅ |
| §8f R4 **before** | 53,344,789 | `unsafe.out` 53,344,789 | ✅ |
| §8g `verus` | 49,549,509 | `n-verus.out` 49,549,509 | ✅ |
| §8g `r4_nowitness` | 49,243,214 | `n-r4nw.out` 49,243,214 | ✅ |
| §8g witness Δ W1 | `+0.622 %` | `+306,255 / 49,243,214` = `+0.6219 %` | ✅ |

⭐⭐⭐ **AND THE ONE THAT IS WORTH THE SECTION.** §8g claims the hand-driven B1 is
*"bit-identical to the gate's own `marginal_ir_per_call`"*. That is now checked
arithmetically rather than by eye — I patched `small.bin`'s `n_iters` header word
(`common/driver.c:38`, LE64 at offset 0) to 100 and to 200, ran callgrind on each, and
differenced:

| cell | `(Ir@200 − Ir@100)/100`, by hand | the gate's field | |
|---|---:|---:|---|
| `unsafe` | `(747,081 − 549,565)/100` = **1975.16** | **1975.16** | ✅ **equal** |
| `verus` | `(747,111 − 549,595)/100` = **1975.16** | **1975.16** | ✅ **equal** |
| `r4_nowitness` | `(744,473 − 548,198)/100` = **1962.75** | *(a control; the gate does not measure it)* | — |

⭐ **Two independent pipelines — my shell loop and `harness/measure.py` — land on the
same two-decimal figure for both rungs**, so the witness cost `+12.41 Ir/call`
(`+0.632 %`) is not an artefact of how I drove the probe. ⚠ **And note the raw
totals: `unsafe` and `verus` differ by exactly 30 Ir at both probe points** (549,565 vs
549,595; 747,081 vs 747,111) — a **constant** offset that cancels in the difference,
which is why B1 is bit-identical while W1 differs by 40. That constant is startup, not
kernel work, and it is the cleanest demonstration in the row of *why* B1 is the right
family for a per-call cost.

## §22 THE BRACKETS, CLOSED — quoted first and last as the dispatch requires

**Opening readings** (§0, taken before I touched anything):

```
66 record(s) examined, 0 STALE          # harness/measure.py --check-stale
16 record(s) examined, 0 STALE          # harness-php/gate.py --tool measure --check-stale
```

**Closing readings**, just now, after the last gate:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
  ok   every php record has a CERTIFYING preflight record beside it
18 record(s) examined, 0 STALE
```

| bracket | opened | closed | required | |
|---|---|---|---|---|
| `harness/measure.py` (PAT) | **66 / 0 STALE** | **66 / 0 STALE** | 66/0 first and last | ✅ **unmoved** |
| `harness-php/gate.py --tool measure` (PHP) | **16 / 0 STALE** | **18 / 0 STALE** | 16 → 18, nothing else | ✅ |

⭐ **The `+2` is exactly this row's two records and nothing else.** The closing listing
names them — `results/gate/ph52-concat-copy-uninit.json` (43 sources) and
`results/ph52-concat-copy-uninit.json` (19 sources + 6 inputs) — and the other eight
php rows (`ph00`, `ph03`, `ph07`, `ph16`, `ph29`, `ph45`, `ph53`, `ph64`) appear with
their own source counts, all **FRESH**. ⚠ **The PAT side examined the same 66 records
and none went stale**, which is the load-bearing half: the PHP programme reaches
`harness/*.py` through `.temp/php-root` and rebinds the roots at run time, so a
mistake there would have shown up as PAT staleness and did not. **No file under
`harness/`, `common/`, `patterns/`, `results/`, `pilot/`, `.web/`, `RECAP_PHP.md` or
`.memory-php/` was edited at any point.**

⚠⚠ **I hit `2 STALE` once, and it is worth recording because it is the §18 price rule
biting in practice.** Late in the task two edits landed together: one to `NOTES.md` and
`README.md` (**gate-only**) and one to `model.py` (**measurement**). The next
`--check-stale` read `2 STALE` — the gate record on the docs, the measurement record on
the oracle — and clearing it cost a full 32-cell re-measure, not a re-gate. **That
re-measure is what moved R4/R5's A1** (§8.2), which is how the A1-vs-W1 cross-check in
NOTES §8f came to exist at all. ▶ **`model.py` is in the measurement digest and it does
not look like it is**; §18 is the standing note.

### §22.1 ⚠ ONE FILE MOVED THAT IS NOT MINE, AND I AM DISCLOSING IT RATHER THAN LETTING A REVIEWER FIND IT

`git status --porcelain` at the end of the task:

```
 M results-php/preflight/_norow.preflight.json
?? patterns-php/ph52-concat-copy-uninit/
?? results-php/gate/ph52-concat-copy-uninit.json
?? results-php/ph52-concat-copy-uninit.json
?? results-php/preflight/ph52-concat-copy-uninit.preflight.json
?? results-php/tables/ph52-concat-copy-uninit.md
?? .tasks-php/TASK_PHP_045_REPORT.md
```

Everything `??` is the row, its four records and this report — the one new directory
under `patterns-php/` the dispatch grants, plus the records the brackets require to
land. **The `M` is the thing to look at.**

⭐ **`_norow.preflight.json` is an APPEND-ONLY, DE-DUPLICATING LEDGER, and the bracket
command itself is what appends to it.** Checked, not assumed: `runs` went **21 → 23**,
the diff is **216 insertions and 0 deletions**, and the first 21 entries are
**byte-identical** to `HEAD`'s. ▶ **So closing the bracket is itself a write, and there
is no way to take the required reading without making it.** I hand-edited nothing in
that file and nothing in it was removed or rewritten.

⭐⭐ **And the `+2` is only 2 for a reason worth knowing: it is NOT one entry per
invocation.** I ran the no-row command **four** times over the task and the ledger
still holds 23, because it **collapses identical entries**. The two new ones differ in
exactly one field — `tool_returncode`, **`1` then `0`** — and that `1` is the run that
found the **`2 STALE`** described below. ⚠ **So the ledger records distinct OUTCOMES,
not attempts**, and a reviewer counting `runs` to count gate invocations would undercount.
I did not set out to learn this; I learned it by re-reading the file after two extra
bracket reads and finding the number had not moved.

⚠ **`results-php/` is NOT on the dispatch's no-edit list** (`results/` is — the PAT
side), and it could not be: the brackets are *defined* as this row's two records
appearing there. **`results/` is untouched, which is what bracket 1's unmoved 66/0
proves.**

▶ **For whoever commits this**: the `M` belongs with the row's commit, not separately —
it is provenance for the gate runs the records describe.

## §23 STATE AT HANDOFF

**The row is built, gated and measured. `verdict: PASS-WITH-BLOCKED-ROWS`,
`failures: []`, `complete_run: true`. Both brackets closed at their required readings
(66/0 unmoved, 16 → 18).** Nothing under `harness/`, `common/`, `common-php/`,
`patterns/`, `results/`, `pilot/`, `.web/`, `RECAP_PHP.md` or `.memory-php/` was edited.
No `git add`/`git commit` was run. `.temp/php45/` went **97 M → 1.4 M**, keeping every
generator, log and `.json`, and carrying a rebuild script for the one artefact family
that had none (`w1_rebuild.sh`, for the callgrind blobs behind NOTES §8e–§8g).

**If you read only one thing, read §1** — Deliverable #0, where five of the registered
statements are refuted on 16 compiled cells, including *"a clean stack slot reads
zero"* (that is an **ASan** property, not a stack property) and the registered
prediction that the `isolated`/`whole` axis would decide stack determinism (**it decides
nothing**; `noinline` decides it, and without it 2 of 16 cells answer differently
because `-O3` folds a teardown it can prove is `undef`).

**If you read two, read §12** — the gate stage that refused the row for an apparently
unrelated reason and turned out to be right about something else entirely: R4/R5 had
been paying a bounds check the C does not pay, **worth −7.12 %**, which had been
flattering safe Rust in every R2/R3-vs-R4/R5 comparison by that amount.

### What a follow-up task should pick up, in priority order

| | item | why it is next |
|---|---|---|
| **1** | **`controls/spellings.py` does not exist in this row** | NOTES §13's first item and the row's clearest omission: the headline ships with **no in-contract spread beside it**. Every PAT pattern with one found the headline was not robust to respelling; this row cannot say either way. ⚠ It is a **measurement**-digest change if it adds a rung variant, gate-only if it only reads. |
| **2** | **the `slot_read_unchecked` twin collision, now seen TWICE** | §16. `ph53` found it (F97), this row is instance two, and on a row with **one** trusted item instead of four — so it is a property of the RULE PAIR, not of a row. Two sound rules (`a twin must be a verified exec fn`; `no unsafe outside a trusted body`) are **jointly unsatisfiable** for any `MaybeUninit<T> → T`. That is a `harness/` design question and I was scoped out of `harness/`. |
| **3** | **the 4 `build.py` line citations I deliberately left rotting** | §18. They sit in measurement-hashed files, so repairing a *pointer* costs a 32-cell re-measure. **Free to fix the next time this row is re-measured for any other reason** — and item 1 may well be that reason. |
| **4** | **the `digest.py` corpus blind spot** | §17. The agreeing set for the two digit orders is exactly the **35 palindromic bytes**, so a bug that transposed the handle digits would be invisible on any palindromic handle. The corpus does not deliberately include a non-palindromic one. |
| **5** | **`model.py` is in the MEASUREMENT digest and does not look like it** | §18, and it cost this task a 32-cell re-measure to learn. Worth a line in `.memory-php/03-numbers.md` by whoever owns that layer — **I am scoped out of `.memory-php/`**, so this is a request, not a change. |

⚠⚠ **And the honest caveat on the whole report: §13 lists eleven things I could not
settle, and `UNTESTED` appears there rather than being quietly resolved in the row's
favour.** The three that would most change a conclusion if someone broke them:
**(a)** whether the `noinline` that Deliverable #0 needs is load-bearing at `-O3` for
reasons beyond the one I measured; **(b)** whether the ASan fake-stack recycling rate
(1 frame in 283) is stable across ASan versions, since §7's inversion is stated as a
*property of the detector* on the strength of one version; **(c)** whether `+12.41
Ir/call` survives a respelling search — i.e. item 1 above, which is why it is item 1.
