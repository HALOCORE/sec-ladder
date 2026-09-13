# ph52 — NOTES

⚠ **`PROTOCOL.md` definition-of-done rule 6, recorded BEFORE ANY CELL WAS BUILT.**

> The `slb-contract` block's sha256 **as first written, before any measurement**:
> `22b3e510bacb8f0ebb28f19af9e142c39b9f2fc78d44f191dc81380f8bd68c55`
>
> ⚠ The `git show HEAD:… | diff -` test rule 6 describes is **VACUOUS ON A NEW
> PATTERN** — a pattern lands in one commit, so on a clean tree it always prints
> nothing and always looks like it passed (`TASK_070_REVIEW`). The recorded hash
> above is the only evidence, which is why it is written here first.
>
> ⚠⚠ **It moved FOUR times before the gate went green, and §1a itemises each**
> (`PROTOCOL.md` rule 6's *"if the hash changes later, say so and say why"*). **Every
> move was forced by a measurement or by a gate stage, and none of them changed what
> the row claims.**

---

## §1 What this row is, in one paragraph

`Zend/zend_operators.c:1148` declares **`zval op1_copy, op2_copy;`** — bare stack
locals, no `= {0}`, no `INIT_ZVAL`, no `memset` — and `:1152`/`:1153` hand their
addresses to `zend_make_printable_zval`. That function writes
`expr_copy->value.str.*` on every arm and `expr_copy->type` **exactly once, at
`zend.c:263`, after the switch**. The `EG(exception)` early exit at `:242-247`
tears the slot down **before** anything has constructed it:

```c
if (EG(exception)) {                          /* zend.c:242 */
    zval_dtor(expr_copy);                     /*       :243  ⛔ THE DEFECT */
    expr_copy->value.str.len = 0;             /*       :244 */
    expr_copy->value.str.val = empty_string;  /*       :245 */
    break;                                    /*       :246 */
}
```

and `_zval_dtor` (`zend_variables.c:36-80`) dispatches on
`zvalue->type & ~IS_CONSTANT_INDEX` and **releases a pointer read out of the same
uninitialised slot**. ⚠ On the common path (`:190-193`, `expr` already a string)
`expr_copy` is never written at all, so the function's own convention is
*constructed only if `*use_copy`* — and this arm destructs it regardless.

### §1a What moved in the contract before the gate, and why

| # | sha256 | what moved |
|---|---|---|
| 1 | `22b3e510bacb8f0e…` | **as first written**, before any cell was built |
| 2 | `1c8ab40758a51123…` | `identity[0].why` — a `PLACEHOLDER` until R4 and R5 had been **disassembled**, because the pin must state what was measured and nothing can be measured before `build.py` has run |
| 3 | `8e5dc3d7199678c4…` | `verus.{items,obligations,twin_obligations,twin_justifications,unsafe_justifications}` — **forced by a gate stage**: §11f, the `n_twins == 0` refusal, and §11g's `win_get_unchecked` repair |
| 4 | `4bd1636d89032c4f…` | `identity[0].why` again — the repair moved the instruction counts (467 → 433); **the LEVEL did not move** |
| 5 | `d73ab3298ecd44f2…` | `idiom.why`, `provenance.cwe_note`, `miri.reason` — **forced by a gate stage**: §7's measured ASan inversion, which refuted what the previous text said |
| — | **as shipped** | see the table above |

⭐ **Moves 3 and 5 are the two a reviewer should read**: both were a gate stage
refusing the row and being **right**, and both produced a finding the row would not
otherwise have had (§11f/§11g and §7).

---

## §2 The tier, and the third data point on open item 75

**Declared `narrowed`. `CATALOGUE.md:146` also says `narrowed`.** ⭐ So this row
**AGREES** with the catalogue, which is the third hand-examined tier on
`RECAP_PHP.md` open item 75 and **it goes the other way from the first two**:
`_040` §5.1 judged both row-7 candidates' labels optimistic and judged ph52's
optimistic too. On the evidence below that judgement was **right about ph53 and
wrong about ph52** — so the item's *"is the whole catalogue optimistic in the same
direction"* is now **2 of 3**, not 3 of 3, and the sample is not a trend.

**What the extraction actually needs, itemised:**

| | |
|---|---|
| the defect span `zend.c:242-247` | lifts essentially verbatim — six lines, one statement deleted by the fix |
| `zend.c:263`'s tag write | lifts verbatim |
| `zend_variables.c:36-80` `_zval_dtor` | lifts **4 of 6 teardown arms**; `:61`'s `del_ref` needs `zend_objects_store` and `:69`'s `zend_list_delete` needs `zend_list` |
| `zend_make_printable_zval`'s switch | lifts **5 of 8 arms**; `:207-212` needs `zend_list`, `:253-256` needs `zend_locale_sprintf_double`, `:258-261` needs `convert_to_string`'s `smart_str` |
| `EG(exception)` + the `cast_object`/`get` dispatch at `:229-241` | **projection** onto one attacker byte |
| `zend_operators.c:1182-1184`'s stores and `:250`'s `sprintf` | **narrowed** to a content digest (see §2a) |
| `zval` itself | lifts, minus the union's `obj` member |

### §2b ⚠ THE KERNEL-OVERLAP NUMBER, AND WHAT I THINK OF IT — §F9's OWED JUDGEMENT

`harness-php/provenance.py ph52-concat-copy-uninit` reports:

```
kernel overlap 19% (15/78 excerpt lines in kernel.c, kernel.h, kernel_hardened.c)
tier=narrowed is expected to clear 25% -- REPORTED, NOT ENFORCED
⚠⚠ THE OVERLAP IS BELOW WHAT tier=narrowed LEADS A READER TO EXPECT (19% < 25%)
```

⚠ **§F9 requires me to say which of the three explanations it offers I take** — *the
citation is wrong*, *the tier is wrong*, or *the heuristic is wrong about this row*.
**I take the third, and the tool's own per-span breakdown is why:**

| span | lines | overlap | what it is |
|---|---:|---:|---|
| `zend.c:242-247` — **the defect** | 5 | **40 %** | the primary; the arm lifts |
| `zend.h:275-293` — the `zval` | 15 | **40 %** | the struct lifts, minus `obj` |
| `zend.c:248-265` — the tag write | 20 | 25 % | `:263` lifts; `:253-261` do not |
| `zend_operators.c:1179-1194` | 12 | 25 % | the teardown lifts; `:1182-1184` do not (§2a) |
| `zend.c:188-216` | 20 | 25 % | 4 of 5 arms lift; `:207-212` does not |
| `zend_operators.c:1146-1153` — `:1148` | 5 | 20 % | the declaration lifts; `TSRMLS_DC` and the in-place arm do not |
| `zend_variables.c:36-80` — `_zval_dtor` | 24 | **12 %** | **4 of 6 arms lift**; the other two need `zend_list` / `zend_objects_store` |
| `zend_variables.c:29-33` — `empty_string` | 1 | **0 %** | the kernel **implements** it, it does not copy it |
| `zend.h:467-470` — `STR_FREE` | 1 | **0 %** | ditto: the macro is *expanded* in the kernel, not quoted |
| `zend.h:386-399` — the IS_* codes | — | n/a | |

▶ **The two 0 % spans are the tell.** `empty_string` and `STR_FREE` are cited because
the row's whole benign corpus rests on them (§4d, §6), and the kernel carries
`ph52_empty_string` and an *expanded* `if (ptr && ptr != ph52_empty_string)` — which is
the faithful thing to do and scores zero on a line-overlap heuristic. ⭐ **A row that
`#define`d `STR_FREE` verbatim would score higher and be no more faithful.**

⚠⚠ **AND IT IS A NUMBER I COULD MOVE BY PADDING THE KERNEL WITH CITED TEXT**, which is
exactly why `TASK_PHP_008` §2 demoted it from a floor to a report — and I am not going
to move it. `unevaluable_conditionals` is **1** (`#ifndef PH52_KERNEL_H`), so the
residual is a header guard. ⚠ **ph52 is the first `narrowed` php row where the demoted
floor would have fired**, so this judgement is the first real test of that demotion and
a reviewer may take it the other way.

⭐ **Why the tier is `narrowed` and not `modelled`:** the mechanism the row prices —
a caller slot declared uninitialised, a callee that destructs it on an early exit,
and a teardown that dispatches on the unwritten byte — lifts **whole**. What does
not lift is adjacent machinery (`zend_list`, `zend_objects_store`, the object
handler table) and `.memory-php/01-extraction.md` F8 is explicit that extraction
cost is priced at the **defect site**.

### §2a ⚠ The one narrowing that changes the number, and the argument for it

`zend.c:250`'s `sprintf("Object id #%ld")` and `zend_operators.c:1182-1184`'s two
`memcpy`s and NUL store are **not lifted**. The kernel allocates exactly the blocks
upstream allocates — `:249`'s `sizeof("Object id #")-1 + MAX_LENGTH_OF_LONG` = 31
bytes and `:1181`'s `total + 1` — and folds the same content as a 131-digest
instead of materialising it.

⚠ **It changes the u64**, so it is declared `kind: "narrowed"` and not
`"substitution"`; §A2 says a divergence that changes behaviour is a `modelled`
tier, and ph53's `instanceof_function` narrowing already drew the distinction that
applies here: **what changes is the answer, not the mechanism.**

⭐ **The reason is `ph64`'s lesson one level over.** Keeping the stores would put a
`Seq<u8>` concatenation in `verus.rs`'s postcondition and would make the
cross-language column a comparison of `rep movsb` against a Rust `while` loop — a
**memcpy** comparison, not a safety comparison, on a row whose cross-language
column already carries an allocator caveat (§9). What the narrowing does **not**
touch: the allocator request sequence, the slot state machine, the teardown
dispatch, or the number of `:243` calls. `model.py::selfcheck` checks each digest
constant against the literal it stands for, and `_dumb` spells the object arm from
the literals rather than from the constants, so the constants are checked too.

---

## §3 ⭐ The R1h argument, token by token — §C's owed writing

`7412202c43e7` — Antony Dovgal, **2006-05-11**, *"no need to destroy the zval
here"*, `Zend/zend.c`, **1 file, 1 hunk, 0 insertions, 1 deletion**. Committed at
`controls/7412202c43e7.patch`, sha256 `32e8526ebfe684d9…`, 746 B.

⭐ **The corpus column and `FIXSURVEY_001.md:242` agree on this sha**, so unlike
ph53 there is no wrong commit to exclude and §F5(iii) is satisfied without a
release-tag walk.

### §3a ⛔ It cannot `patch -p1`, and here is every token that differs

**The deleted statement is byte-identical up to ONE TAB.** `od -c` of both:

```
the commit's removed line (4 tabs)
  \t \t \t \t  z v a l _ d t o r ( e x p r _ c o p y ) ; \n

pristine 5.0.0 Zend/zend.c:243 (5 tabs)
  \t \t \t \t \t  z v a l _ d t o r ( e x p r _ c o p y ) ; \n
```

By 2006 the arm had lost one level of nesting. **That tab is the whole of the
difference in the statement.**

**What does not match is the CONTEXT, and it cannot:** the 2006 hunk's context
lines name `STR_EMPTY_ALLOC()` and `E_RECOVERABLE_ERROR`, and **both tokens are
absent from the entire 5.0.0 tarball** — measured, 0 occurrences across
`Zend/zend.h`, `Zend/zend_variables.h`, `Zend/zend_API.h`,
`Zend/zend_operators.h` and `Zend/zend_errors.h`. 5.0.0's own arm is
`if (EG(exception)) { … expr_copy->value.str.val = empty_string; break; }`. So
`patch` has nothing to match, and the hand reconstruction is *the deletion of that
one statement*.

### §3b ⭐ And the deletion is COMPLETE — the opposite of ph53's result

`zend.c:243` is the **only** line in `zend_make_printable_zval` that reads
`expr_copy` with no write to it earlier on the same path. Every `expr_copy` use in
`:188-265`, enumerated from the tarball:

| line | use | written first? |
|---|---|---|
| `:196`, `:197`, `:201`, `:202`, `:204`, `:205`, `:209`, `:213` | writes | — |
| `:210` | reads `value.str.val`, written at `:209` | ✅ |
| `:214` | reads `value.str.len`, written at `:213` | ✅ |
| `:222` | `zend_std_cast_object_tostring(expr, expr_copy, …)` | **inside the `#if 0` at `:220-228`** — dead |
| `:229`, `:236` | passes the pointer to a callee | the projection (§2) |
| **`:243`** | **`zval_dtor(expr_copy)`** | ⛔ **NO** |
| `:244`, `:245`, `:249` | writes | — |
| `:250` | reads `value.str.val`, written at `:249` | ✅ |
| `:253`, `:258` | `*expr_copy = *expr` — whole-struct writes | — |
| `:254`, `:259`, `:260` | read, one line after `:253`/`:258` | ✅ |
| `:263` | `expr_copy->type = IS_STRING` — **after the switch** | — |

▶ **So deleting `:243` leaves no path that tears down an unconstructed slot.**
⭐ This is why R2–R5 *are* ports of R1h and why `inputs/adversarial-dblfree.bin`
*can* ship: ph53 could do neither, because `d09cdd9f71f3` left the fault standing.

### §3c The argument as a CHECK rather than as prose

`controls/r1h_onelinedel.py` derives `c/kernel_hardened.c` from `c/kernel.c` and
prints:

```
  code lines only in R1  : 1  ['ph52_zval_dtor(expr_copy);']
  code lines only in R1h : 0   []
  ok: R1h is R1 minus exactly one statement
```

`--selftest`: **11 cases (8 must-fire, 3 must-NOT-fire), PASS.** The must-fire arms
include a hardened kernel that **added a guard instead of deleting the call** —
which stage 7h would not have noticed — one that deleted `:1188` as well, a
statement restored inside the code while the comment still names it, and a
comment-only edit that must still fail the derivation.

⚠ **2006 is after every 5.0.x release**, so the defect shipped in all of them and
the fix is in none — which is consistent with the patch not applying.

---

## §4 ⭐⭐⭐ DELIVERABLE #0 — stack determinism, and the five things it broke

ph52's uninitialised datum is on the **stack**, and every mechanism this tree has
for uninitialised memory is an **allocator** shim. So before any rung existed the
row had to settle whether `:243` reads anything reproducible. `controls/d0_stack.c`
is a faithful miniature — one `concat_function` with one bare `zval op1_copy;`, the
IS_ARRAY and IS_OBJECT arms, and `_zval_dtor` with its real `:38` early return,
real `:41` masked switch and real `STR_FREE` test — linking
`common-php/emalloc_shim.h`, which is what the measured binaries do.
`controls/d0_stack.py` drives **16 cells**: `{gcc 13.3.0, clang 22.1.6}` ×
`{-O0, -O3}` × `{isolated, whole}` × `{callee noinline, callee inlinable}`.

⚠ The fourth axis is not the harness's. `harness/build.py` compiles exactly three
TUs for the whole row where upstream has `zend_operators.c`, `zend.c` and
`zend_variables.c` as **three separate ones** and links **without LTO**.

### §4a ✅ The offset IS exact

The slot address is the **same on every call in every one of the 16 cells**, at
both opt levels, in both modes, on both compilers. The early trace (`--addr`):

```
:243[0] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90
:243[1] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90
:243[2] tag=3 ptr=0x…2a0 slot=0x7fff34f21b90
```

⭐ **So the trigger is a CALL HISTORY**, and because `ph52_concat_function` is
`noinline` the history is controlled entirely by the op stream inside one window —
which makes the adversarial input a property of the **blob** after all.

### §4b ⛔⛔ The load-bearing boundary is the CALLEE inline boundary, and `build.py` does not control it

`controls/d0_stack.py`, shipped flags:

| | u64 |
|---|---|
| the 8 `noinline` cells | **1 distinct value** (`140458863534`) |
| the 8 `inlinable` cells | **3 distinct values** |
| `gcc -O3 isolated`, inlinable | `140464218697` |
| `clang -O3 whole`, inlinable | `151158572205` |

⭐⭐ **And the mechanism is named, not guessed: `140464218697` is also what
`-ftrivial-auto-var-init=zero` gives in all 16 cells.** gcc at `-O3` treats the
unwritten tag as `undef` and picks the arm a **zeroed** slot would have picked.
clang picks a third thing. **One undefined behaviour, three answers.**

⚠⚠ **The harness's own `isolated`/`whole` axis moves nothing** — `noinline` cells
agree in both modes and `inlinable` cells break in both. ▶ So `c/kernel.h` defines
`PH52_NOINLINE`, declared as a `substitution` with this 16-cell differential behind
it.

⛔ **The manager's registered prediction — *the defect may be PRESENT in
`isolated` and OPTIMISED AWAY in `whole`* — is REFUTED.** The finding that
replaces it is better: **upstream's own build configuration is load-bearing for
this defect's reachability, and a whole-program compiler deletes the bug.** PHP
5.0.0 is built without LTO; that is why the bug was reachable at all.

### §4c ⛔ *"A clean stack slot reads ZERO"* is an ASan property, not a shipped-build one

The manager's §2.3 table says an un-initialised `stack[64]` reads `00 00 …` **with
and without** the sanitizer. Measured on the **first** `:243` of the 16 cells under
the shipped flags, the tag is `0` in 12 cells and **`235` (0xeb), `94` (0x5e),
`113` (0x71), `82` (0x52)** in the other four — the C runtime's own startup
residue, and build-configuration dependent. ⭐ None of the four masks into a
freeing case, so the *conclusion* held; the *premise* does not. **The table was
measured under `-fsanitize=address`, where ASan hands out a freshly zeroed frame
(§7a), and generalised.** That is `.memory-php/04-process.md` law 15's shape.

### §4d ⛔ Fallback (a) as stated does not fire — the history needs TWO arms

The manager's fallback (a) is *"iteration 2+ reads the previous iteration's
`IS_STRING` and frees the previous iteration's already-freed pointer"*. **Measured
with a single repeated faulting arm: `free calls = 0` in every cell.** The reason
is two lines of the arm he quotes — `:244-245` write `len = 0; val = empty_string`
— and `zend.h:469 STR_FREE(ptr)` is `if (ptr && ptr != empty_string) efree(ptr)`.
▶ **A call that takes the faulting arm leaves the slot PERMANENTLY SAFE, so the
arm is self-defusing on repetition.**

✅ **Corrected, fallback (a) holds and is stronger.** The adversarial history is
**a converting arm followed by the faulting arm**:

1. call *k* takes `:202`, `:214` or `:249` → `value.str.val` is a real `emalloc`
   block and `:263` writes `type = IS_STRING`;
2. `:1187-1189 if (use_copy1) zval_dtor(op1)` **frees that block**, leaving
   `IS_STRING` + a dangling pointer;
3. call *k+1* takes the faulting arm → `:243` reads it → `efree` → **double free**.

⭐ **And that is MORE faithful, not less:** two different `.` operations on two
different operand types is what a PHP script does, and it is why the bug was
reachable.

### §4e ⚠ Hypothesis 4 upheld, mechanism refuted

`-ftrivial-auto-var-init=zero` and `=pattern` delete the defect in **all 16**
cells and change the answer. ⭐ Neither flag is in `harness/build.py::c_flags` —
checked by `d0_stack.py` N5 against the harness source rather than assumed — so
the measured matrix is unaffected. §7a has ASan's, which is **not** poisoning.

### §4f What the row took

**Fallback (a), corrected** — not (b) a synthetic prior call, not (c) relegating
the benign path to `controls/`, not (d) the heap. Because §4a's reuse is
intra-frame and slot-local, the adversarial property is *an allocating arm
immediately followed by the faulting arm, in the same window*, and
`inputs/gen.py::_check_history` re-derives it from the bytes. ⚠ **One input did go
to `controls/`** and `gen.py` says so in terms: a window whose op 0 is the faulting
arm reads the C runtime's residue, so its u64 is not a function of the blob.
`controls/negatives.py --firstcall` is that blob, run over all 8 C configurations
with **R1 and R1h compared** — the observable that says whether the residue was a
freeing tag. Measured: R1 == R1h, i.e. the 95.3 % outcome (§6), **recorded and not
required**.

---

## §5 The fix, the u64, and the abort

### §5a ⭐⭐ The defect is in the published checksum

`inputs/adversarial-dblfree.bin` and `inputs/adversarial-safe.bin` differ in **one
op byte** — arm 3 (`estrndup("Array")`) against arm 1 (IS_NULL) on side 0 of op 0 —
so in one the faulting arm's `:243` reads a **dangling** slot and in the other a
**safe** one.

| input | R1 (4 cells) | R1h (4 cells) | R2 · R3 · R4 · R5 | `model.py` |
|---|---|---|---|---|
| `small.bin` | `15768976536999838170` | same | same | same |
| `large.bin` | `2957760381129677675` | same | same | same |
| `adversarial-safe.bin` | `254123829775225275` | same | same | same |
| **`adversarial-dblfree.bin`** | **`272040826665440682`** | **`272040826666539789`** | `…666539789` | `…666539789` |

⭐⭐⭐ **ph53's `idiom.why` records that *"the published u64 carries no evidence
whatever that the defect exists"*. This row's does.** The mechanism: `:243`'s
teardown is observable only through the allocator, and `php_shim_tally()` is folded
into the return (§B1.2), so the extra `efree` moves `n_free` and the u64 with it.

### §5b ⚠ `n_iters = 1` on both adversarial blobs, and it is load-bearing

The second `efree` pushes the **same header** into `cache[1]` twice
(`zend_alloc.c:270-279`), so nothing reaches `free()` during the call. The **next**
call's `php_shim_reset()` (`emalloc_shim.h:267-269`) then frees that header twice
and glibc aborts:

```
free(): double free detected in tcache 2          exit 134
```

measured on **14 of 16** configurations of the `controls/d0_stack.c` shape under
plain `free`. ▶ At `n_iters = 1` there is no next call, R1 runs to completion, and
the defect lands in the **number** instead of in a signal — which is the stronger
artefact, because a number is what the gate compares across six rungs.

### §5c ⭐ R1 is the only rung that diverges, and R1h is clean — so the input can ship

Stage 7h requires R1h sanitizer-clean on **every** input. R1h has no `:243` at all,
so it is clean on `adversarial-dblfree.bin` and the blob ships. ⚠ **ph53 is the
contrasting case and `.memory-php/02-ladder.md` F31 is the rule**: its fix was
incomplete, so *every* blob on which its R1 faulted was one on which its R1h
NULL-dereferenced, and the evidence had to live in `controls/`. **The difference is
entirely that this fix is complete (§3b).**

---

## §6 ⭐⭐ The tag sweep — the number this row publishes

`controls/tag_sweep.c` transcribes `_zval_dtor` over the whole tag byte, including
the two arms `c/kernel.c` does not lift, and `controls/tag_sweep.py` re-derives the
same table independently from the `#define`s and the `switch`:

| arm | tags | of 256 |
|---|---|---|
| **no-op** | 244 values | **95.312 %** |
| `STR_FREE` (`efree`) | 3, 8, 131, 136 | 1.562 % |
| hash destroy + `FREE_HASHTABLE` | 4, 9, 132, 137 | 1.562 % |
| object `del_ref` | 5, 133 | 0.781 % |
| `zend_list_delete` | 7, 135 | 0.781 % |
| **TOTAL TEARING DOWN** | **12 values** | **4.688 %** |
| **of which reach `efree`/`free`** | **8 values** | **3.125 %** |
| live in `c/kernel.c` (2 arms unlifted) | 8 values | 3.125 % |

⭐⭐⭐ **That is the answer to *why do uninitialised-read bugs survive for years in
shipped code*: 95.3 % of byte values make `zend.c:243` a no-op, and `IS_NULL` is
`0`, which is the likeliest residue of all.** The defect shipped in every 5.0.x
release and was fixed in 2006 as a tidiness change, not as a security fix.

### §6a ⛔ `RECAP_PHP.md` F102's figure is wrong in three ways

F102 says *"five named cases out of a byte, widened by the `& ~IS_CONSTANT_INDEX`
mask"*, explicitly UNTESTED. Measured:

1. **SIX named cases, not five.** F102 lists `IS_STRING`, `IS_CONSTANT`,
   `IS_ARRAY`, `IS_CONSTANT_ARRAY`, `IS_OBJECT` and **misses `IS_RESOURCE`** —
   `zend_variables.c:64-71`, whose arm calls `zend_list_delete(zvalue->value.lval)`
   on a `long` read out of the same unwritten slot.
2. **TWELVE of 256, not ten.** The mask doubles each of the six residues
   `{3, 4, 5, 7, 8, 9}`.
3. ⛔ **`_zval_dtor` DOES have `case IS_NULL`.** F102 says it *"has no
   `case IS_NULL`"*; `zend_variables.c:75` **is** `case IS_NULL:`, sitting beside
   `default:` at `:76`. The conclusion — a zero tag no-ops — holds; the reason F102
   gives for it does not.

`controls/tag_sweep.py --selftest`: **15 assertions (9 must-fire claims, 6
must-NOT-fire), PASS.** ⭐ Its N5 is the arm worth reading: `0x01` no-ops via the
`:38` early return and `0x81` no-ops via the switch's own `case IS_LONG:` at `:72`
— **two different reasons, one outcome**, and a checker that conflated them would
be right by accident. N9 then measures that the `:38` early return is **redundant
for the count**, which is a fact about upstream's code the row would otherwise have
asserted.

---

## §7 §A4 — the fidelity answer, and what the sanitizers do NOT see

The corpus records `vuln_class = uninit-read-silent` for LOGIC-007. ⚠
**ATTRIBUTION, because F87's defect was exactly this:** that string is verified
directly in `.tasks-php/TASK_PHP_001_MINE/type/NOTES.md:398`. The
*`n/a (non-crash class)`* phrasing in circulation is `TASK_PHP_040_REPORT.md:221`
quoting `index.csv`, **which is not in this repository**, and this row rests nothing
on it.

**THREE independent measured reasons the wild run is silent**, and §6 is the first.

### §7a ⛔⛔⛔ ASan FIRES ON THE **BENIGN** INPUTS AND IS SILENT ON THE ADVERSARIAL ONE — AND THE SANITIZER IS WHAT *CAUSES* IT

`check.py::_san_build` is `gcc -O1 -g -fsanitize=address,undefined -static-libasan
-static-libubsan -DSLB_ISOLATED`, with no `ASAN_OPTIONS`. Measured on this box, both
C rungs, all six inputs:

| input | R1 under ASan+UBSan | R1h under ASan+UBSan |
|---|---|---|
| **`small.bin`** | ⛔ **`heap-use-after-free`**, exit 1 | ✅ clean, exit 0 |
| **`large.bin`** | ⛔ **`heap-use-after-free`**, exit 1 | ✅ clean, exit 0 |
| `adversarial-dblfree.bin` | ✅ clean | ✅ clean |
| `adversarial-safe.bin` | ✅ clean | ✅ clean |
| `adversarial-nowin.bin` | ✅ clean | ✅ clean |
| `adversarial-trunc.bin` | exit 5 | exit 5 |

⭐⭐⭐ **THE INVERSION IS THE FINDING: the sanitizer fires where the row is benign and
is silent where the row is adversarial.** `model.py::sanitizer_expect` declares
`fires` on the two measured inputs and `clean` on the four adversarial ones, and its
docstring carries the whole of the reason. **The diagnostic, in full:**

```
ERROR: AddressSanitizer: heap-use-after-free on address 0x503000000050
READ of size 4 at 0x503000000050 thread T0
  #0 php_shim_efree            c/emalloc_shim.h:414     <- real_size = REAL_SIZE(p->size)
  #1 ph52_zval_dtor            c/kernel.c:139           <- zend_variables.c:45  STR_FREE_REL
  #2 ph52_make_printable_zval  c/kernel.c:209           <- zend.c:243  THE DEFECT
  #3 ph52_concat_function      c/kernel.c:271           <- zend_operators.c:1152
  #4 kernel                    c/kernel.c:326
freed by thread T0 here:
  #1 php_shim_reset            c/emalloc_shim.h:269     <- the top of the NEXT kernel call
```

### §7b ⭐⭐ THE MECHANISM, TRACED — ASan's FAKE STACK BREAKS THE ROW'S ASSUMPTION IN **BOTH** DIRECTIONS

The two slots are STACK locals, and the row's benignness is a property of the stack
being **reused at the same offset** (§4a) — which is what `inputs/gen.py`'s three
call-history rules exploit. ASan's fake stack
(`detect_stack_use_after_return`, default **1** in both compilers here) does not
honour that:

* **usually it hands out a freshly ZEROED frame**, so `:243` reads `type = 0 =
  IS_NULL` and `_zval_dtor` no-ops. Measured with a tracing build of the same
  kernel: **282 of the 283** `:243`-reaching calls on `small.bin` read
  `type=0 val=(nil)`.
* ⭐ **and 1 in 283 it hands back a RECYCLED frame carrying an older call's bytes.**
  The trace, at the firing call:

  ```
  OP 13  site=1188 val=0x506000010718   site=1191 val=<empty_string>
  OP 14  arms 0/0                       <- the PASS-THROUGH arm on BOTH sides:
                                           this call writes neither slot and tears
                                           down neither
  OP 15  arms 1/4 aux 214/75            <- the faulting arm on side 1
         site=243 type=3 val=0x503000000058   <- a pointer from several ops back
  ```

  and `0x503000000058` is a block `php_shim_reset()` freed at the top of a later
  call. ▶ **ASan CREATES the fault on an input the real stack keeps clean.**

⭐⭐ **On the REAL stack the corpus is benign and that is measured over the whole
run, not argued:** the same tracing kernel at `-O1 -DSLB_ISOLATED` without
`-fsanitize`, over all **25,000** iterations of `small.bin`, shows **every** `:243`
reading `type=3 val=<ph52_empty_string>` — one unique value, `nm` confirms the
symbol — so `STR_FREE` skips and nothing is freed. ✅ **That is what the published
u64 rests on and what R1 == R1h == `model.py` on `small.bin` means.**

⚠⚠⚠ **SO `inputs/gen.py`'s THREE RULES ARE RULES ABOUT THE REAL STACK AND CANNOT BE
MADE TO HOLD UNDER A FRAME-RELOCATING ALLOCATOR**, and no blob property can fix it:
any corpus that exercises an allocating arm leaves a dangling slot at *some* call
boundary, and a recycling fake stack can read it from an arbitrary distance back.
⭐ **That is `.memory-php/02-ladder.md` F31's limitation in a new form** — the row
states it rather than restricting the corpus to the three non-allocating arms, which
would cost §A2a rule 1's coverage.

⭐ **And it is the same class as F102's `0xbe` correction** — *a detector-dependent
observation must not be recorded as a row property* — **with the sign reversed**: the
detector does not reveal the defect, it manufactures one. The row caught it before
publishing because a gate stage refused the row for it.

### §7c ⚠⚠ AND THE ADVERSARIAL INPUT IS SILENT FOR **TWO** INDEPENDENT MEASURED REASONS

1. **`n_iters = 1` and two ops is far too few for the fake stack to recycle**, so
   `:243` reads a freshly zeroed frame and **the defect the blob exists to trigger
   does not happen under ASan at all.**
2. **Even when it does happen, PHP's own allocator swallows it.**
   `php_shim_efree` of a block under 88 bytes pushes it into the size-class cache and
   never reaches `free()` (`zend_alloc.c:270-279`), so there is nothing for ASan to
   intercept — `PROTOCOL_PHP.md` §B1.1's measured fact arriving on a third row, and a
   **property of PHP** rather than of the probe.

⛔ **So the manager's §2.6 — *"expect ASan to fire on the double free where the corpus
says silent — state the divergence, with the exact diagnostic"* — is REFUTED, and in
a way no one predicted.** ASan never reports the double free on any input. What it
reports instead is a `heap-use-after-free` **it caused itself, on the benign inputs,
through a third mechanism (frame recycling) that has nothing to do with the
allocator.** ▶ Three independent mechanisms, none of them the predicted one.

⭐ **And `ASAN_OPTIONS=detect_stack_use_after_return=0` is the one-flag confirmation**:
with the real stack back, the `d0_stack.c` probe's double free appears and ASan
reports it (§4), and the benign corpus stops firing because the offset is stable again.

### §7d ⭐ Miri is the only detector in this tree that sees the read

`controls/negatives.py --miri`, 8 arms, **all as expected**:

| arm | input | verdict |
|---|---|---|
| M1 `unsafe.rs` | `small`, `adversarial-dblfree`, `adversarial-safe` | silent, and the u64 matches native |
| M2 `r4_nowitness.rs` | the same three | **silent** — see below |
| **M3 `r4_nowitness.rs`** | `op0-faulting` (generated) | **`error: Undefined Behavior: reading memory at alloc1924[0x0..0x8], but memory is uninitialized at [0x0..0x8]`** |
| M4 `unsafe.rs` | `op0-faulting` | silent |

⭐ **M2 is the arm that teaches something.** The witness-free control is silent on
every shipped input, and that is a *measured consequence of `gen.py`'s rules*: R1
and R3 mean no `:243` in the measured corpus ever sees a slot that was never
constructed, so even the faithful port reads only **initialised** memory. Its
divergence on `adversarial-dblfree.bin` is the **double free**, not the
uninitialised read. ▶ The two halves of this defect are separable and the corpus
separates them.

⭐ **M3 against M4 is the one bit earning its keep**, measured on the same blob.

---

## §8 The numbers

### §8.0 ⭐ THE GATE'S OWN FIELD — `marginal_ir_per_call`, FROM `results-php/gate/ph52-concat-copy-uninit.json`

⚠ **F99: name the file every field came from.** The table below is
`marginal_ir_per_call` out of **`results-php/gate/ph52-concat-copy-uninit.json`** —
the gate's own B1 field, `(Ir@200 − Ir@100)/100`, which differences out the one-shot
loader terms. `O3/isolated`:

| rung | `small.bin` | `large.bin` |
|---|---:|---:|
| R1 `c-gcc` | 5833.79 | 13977.67 |
| R1h `c-gcc-h` | **5813.39** | **13944.52** |
| R1 `c-clang` | 5430.26 | 13018.12 |
| R1h `c-clang-h` | **5389.36** | **12934.86** |
| R2 `safe_naive` | 2250.88 | 6003.74 |
| R3 `safe_tuned` | **2105.88** | **5620.77** |
| R4 `unsafe` | 1975.16 | 5282.62 |
| R5 `verus` | **1975.16** | **5282.62** |

| comparison | `small.bin` | `large.bin` |
|---|---:|---:|
| **R1h vs R1, gcc** | **`−0.3497 %`** | `−0.2372 %` |
| **R1h vs R1, clang** | **`−0.7532 %`** | `−0.6396 %` |
| **R3 vs R2** | **`−6.4419 %`** | `−6.3782 %` |
| **R5 vs R4** | **`+0.000000 %`** — *bit-identical* | **`+0.000000 %`** |
| R4 vs R1 gcc (⚠ cross-language) | `0.3386×`, i.e. the C is **2.95×** the Rust | `0.3779×` |

⭐ **R4 == R5 to the last digit in B1**, where the one-shot whole-program total differs
by `+40 Ir` — which is `.memory-php/03-numbers.md` item 99's argv/env term made
visible: the marginal differences it out and the total does not. ⚠ **That is the
reason item 99 says do not quote a whole-program total to more than 2 dp**, and this
row is an instance.

⚠⚠ **EVERY FIGURE BELOW NAMES FOUR THINGS** — the statistic, the input, the
opt/mode level, and the base it is against (`.memory-php/03-numbers.md`, F98's four
qualifiers). All of them are **`small.bin`, `O3/isolated`**; `W1` is whole-program
callgrind Ir and `A1` is `kernel_exclusive_ir`.

### §8a ⛔⛔ `inside_share` IS **22.24 %**, SO THIS ROW PUBLISHES IN **W1**

`.memory-php/03-numbers.md`: *family A resolves a code difference exactly to the
extent the difference lands INSIDE THE KERNEL SYMBOL.* Measured on `c-gcc`, per
function:

| function | Ir | share |
|---|---:|---:|
| `ph52_make_printable_zval` | 37,617,282 | **25.74 %** |
| `ph52_concat_function` | 33,766,427 | **23.10 %** |
| **`kernel`** | **32,509,505** | **22.24 %** |
| `ph52_zval_dtor` | 19,745,701 | **13.51 %** |
| libc (`malloc` + one more) | 16,244,129 | 11.11 % |
| **PROGRAM TOTAL** | **146,152,976** | 100 % |

⭐ `PH52_NOINLINE` puts the three lifted callees in their own symbols — **62.35 % of
the program** — and `zend.c:243` lives in the first of them. ▶ **Family A cannot see
the difference the row is about, so the headline is W1.** `ph45` at 9.5 % published
W1 and `ph53` at 89.5 % published A1; ph52 at 22.24 % lands on `ph45`'s side.

⚠ **And `inside_share` is not independent of the extraction's fidelity choices**,
which is worth recording: the low figure is caused by the *same* declared
substitution that makes the row reproducible at all (§4b).

### §8b ⭐⭐⭐ THE R1h COLUMN — AND THE FIX IS **PROFITABLE**, NOT FREE

| statistic | R1 `c-gcc` | R1h `c-gcc-h` | Δ |
|---|---:|---:|---:|
| **A1** (`kernel_exclusive_ir`) | 32,509,505 | 32,509,505 | **0 — exactly `0.00 %`** |
| **B1** (`marginal_ir_per_call`) | 5833.79 | 5813.39 | **`−0.3497 %`** |
| W1 (one-shot total) | 146,152,976 | 145,653,146 | `−0.342 %` |

| statistic | R1 `c-clang` | R1h `c-clang-h` | Δ |
|---|---:|---:|---:|
| **A1** | 27,465,935 | 27,465,935 | **0** |
| **B1** | 5430.26 | 5389.36 | **`−0.7532 %`** |
| W1 | 136,056,404 | 135,049,431 | `−0.740 %` |

⭐ **B1 and W1 agree to within rounding** (`−0.3497` vs `−0.342`), which is the
cross-check the two statistics are for: B1 differences out the loader terms and W1
does not. **B1 is the published figure** because it is the gate's own field.

⭐ **`RECAP_PHP.md` open item 76 predicted `0.00 %`. It is exactly `0.00 %` in
family A and `−0.342 %` / `−0.740 %` in W1 — and family A's zero is BLINDNESS, not
absence.** The mechanism, read off the per-function split:

| function | R1 | R1h | Δ |
|---|---:|---:|---:|
| `ph52_make_printable_zval` | 37,617,282 | 37,499,674 | **−117,608** — the deleted call site |
| `ph52_zval_dtor` | 19,745,701 | 19,363,475 | **−382,226** — the calls that no longer happen |
| `ph52_concat_function` | 33,766,427 | 33,766,427 | 0 |
| `kernel` | 32,509,505 | 32,509,505 | **0** ← why A1 reads zero |

⭐ That is `ph45`'s **`BLIND`** class (F86: *A is exactly `0` while the whole-program
figure is not*, 14 of 366) with a named mechanism, on a row where the blind quantity
**is** the headline.

⭐⭐⭐ **What it publishes: the upstream fix for a whole CLASS of defect — the
unreached-error-path teardown — is not merely free, it pays for itself.** ⚠ The
figure is **small**, a third to three quarters of one per cent, and for a stated
reason: the faulting arm is a minority of the op stream and the teardown it removes
is a handful of instructions per call. ⛔ A `0.00 %` column would have been a finding
and not a disqualification (`CLAUDE.md` rule 6); a negative one is better and the row
did not have to choose. ✅ **Same language, same allocator, so §B1a.3's caveat does
NOT apply to this column.**

### §8c ⭐ R2 vs R3 — the cleanest column the row has

| | W1 | A1 |
|---|---:|---:|
| R2 `safe_naive` | 56,432,368 | 55,729,109 |
| R3 `safe_tuned` | 52,829,203 | 52,125,944 |
| **Δ** | **−3,603,165 = `−6.385 %`** | `−6.468 %` |

✅ **Same language, and the two rungs allocate IDENTICALLY** (`:243` never frees
anything on the measured corpus), **so the allocator term cancels exactly** —
§B1a.4. **The mechanism is the four things R3 removes** (module header): the `Option`
discriminant living in a memory slot, `take()`'s write-back, the `:243` teardown call
itself, and the `bool` + `Pr` pair collapsing into one value. ⭐ **And R3 is a port of
R1h**, so this column is also *the upstream fix measured in safe Rust* — where §8b
measures it in C.

### §8d ⭐⭐ R4 vs R5 — `0.000000 %` in B1, and the `+40 Ir` in W1 is the argv residual

| | **B1** `Ir/call` | W1 (one-shot total) |
|---|---:|---:|
| R4 `unsafe` | **1975.16** | 49,549,469 |
| R5 `verus` | **1975.16** | 49,549,509 |
| Δ | **`+0.000000 %` — bit-identical** | `+40 Ir = +0.00008 %` |

⭐ Consistent with `identity: norel` at `-O3`: the kernels are the same machine code.
⚠ The 40 is the per-call stack-alignment / argv-block term `.memory-php/03-numbers.md`
item 99 names (*A is reproducible and the whole-program column is not*), and it is why
that item says **do not quote a whole-program figure to more than 2 dp**.

### §8e ⚠⚠ THE CROSS-LANGUAGE COLUMN, LABELLED AS §B1a.3 REQUIRES

| | W1 |
|---|---:|
| R1 `c-gcc` | 146,152,976 |
| R4 `unsafe` | 49,549,469 |
| ratio | **C is 2.95× the Rust** |

⛔⛔ **THIS IS LARGELY A COMPARISON OF AN ALLOCATOR AGAINST ARITHMETIC AND MUST NOT
BE READ AS A SAFETY FIGURE.** §B1a's precondition fails on this row — up to five
`emalloc`s and three `efree`s **per op**, i.e. O(n_ops) per kernel call — so the C
rung runs the real `emalloc_shim` over real `malloc`/`free` (**16.2 M Ir, 11.11 % of
the C cell, in libc alone**) where the four Rust rungs reproduce `php_shim_tally()`
with a counters-only simulation (§B forbids them the shim). ▶ **`ph64` is the
precedent and this is the SECOND row where §B1a.3 binds**, so `ph53`'s O(1) exception
stands at **1 of 2**, not 2 of 2. ⭐ The same-language columns (§8b, §8c, §8d) are
unaffected.

### §8f ⭐⭐ THE `win_get_unchecked` REPAIR WAS WORTH **−7.12 %**, AND THAT IS A REAL BOUNDS CHECK

§11g's fidelity repair moved R4/R5:

| | W1 | A1 `kernel_exclusive_ir` | W1 − A1 (the out-of-kernel remainder) |
|---|---:|---:|---:|
| R4 before, safe-indexed window reads | 53,344,789 | 52,641,525 | 703,264 |
| R4 after, `win_get_unchecked` | 49,549,469 | 48,846,257 | 703,212 |
| **Δ** | **−3,795,320 = `−7.12 %`** | **−3,795,268 = `−7.21 %`** | **−52** |

⭐ **So the shipped R4 had been paying a bounds check the C does not pay, worth 7 %
of the whole program — and it was flattering safe Rust in the R2/R3-vs-R4/R5
comparison by exactly that amount.**

⭐⭐ **AND THE TWO STATISTICS CONFIRM EACH OTHER TO 52 Ir OUT OF 3.8 M MOVED.** W1 is
a callgrind whole-program total taken by hand; A1 is
`ir.small.bin.kernel_exclusive_ir` read out of
`results-php/ph52-concat-copy-uninit.json`, which the harness measured on its own and
which I did not touch. They are **different instruments on different runs**, and the
**out-of-kernel remainder is the same to 52 Ir in 703,2xx (`0.0074 %`)** — so the
repair moved work that is *inside the `kernel` symbol* and **moved nothing else**,
which is exactly the claim "a bounds check in the window read" predicts and is not
something either figure establishes alone. ⚠ **The A1 column here is the ONE place
this row quotes a superseded A1 figure, and it is labelled `before`**: the live record
carries only the `after` row. ⚠⚠ **The percentages differ in the second digit
(`7.12` vs `7.21`) for the arithmetic reason that the same absolute Δ is divided by a
smaller base**, not because the two instruments disagree; the row's headline is the W1
one because §9 chose W1, and §B1a.3 does not bind here — both columns are
Rust-against-Rust. ⚠ It was found by a gate stage refusing the row
for an apparently unrelated reason (§11f), which is `PROTOCOL_PHP.md` §A2a's lesson
verbatim: *a gate stage that refuses your row is a hypothesis about your row before
it is a hypothesis about the gate.*

### §8g ⭐⭐⭐ THE WITNESS — §2.9(2)'s PREDICTION, MEASURED

| | **B1** `marginal_ir_per_call` | W1 (one-shot total) |
|---|---:|---:|
| `controls/r4_nowitness.rs` (no witness) | **1962.75** | 49,243,214 |
| shipped `unsafe.rs` (2-bool witness) | **1975.16** | 49,549,469 |
| `verus.rs` | **1975.16** | 49,549,509 |
| **Δ (witness)** | **+12.41 Ir/call = `+0.632 %`** | `+0.622 %` |

⭐⭐ **TWO METHODS, ONE ANSWER** (`+0.632 %` B1, `+0.622 %` W1), and the shipped R4's
B1 figure is **bit-identical to the gate's own `marginal_ir_per_call`** for that cell
— the control was driven through the same `probe_iters [100, 200]` difference by hand.

⭐⭐⭐ **AND THE ABSOLUTE NUMBER IS THE MECHANISM, WHICH IS WHAT §F8 ASKS FOR:
`+12.41 Ir per kernel call` over **16 ops**, i.e. `~0.78 Ir per op` — two `bool` tests
and two stores, register-resident.** That is not a figure that needs a story.

⚠ **`small.bin`, `O3/isolated`, W1, against `controls/r4_nowitness.rs` — a RUST
control and NOT the C**, which is the same base F98 used for ph53. §11c is the
two-row comparison and §11c's verdict is that the prediction's *direction* holds and
its word *"~FREE"* does not.

⚠ **Pre-repair figures, recorded because the ratio is what the prediction is about
and it did not turn on them:** before §11g, R4 was 53,344,789 and its witness-free
control 52,559,156, i.e. `+785,633 = +1.495 %`.

## §9 Which statistic, and why

**W1, measured first and not assumed** — §8a. `inside_share` is **22.24 %**, the
difference the row is about lands entirely outside the `kernel` symbol, and family A
reads it as **exactly zero** (§8b). ▶ Every headline in §8 is W1, with the A1 figure
beside it and labelled, per `.memory-php/03-numbers.md`'s *quote both, labelled,
always*.

⚠ **A row's spread over respellings is a fact about its variants, not about the
statistic** (item 82) — `ph45`'s A1 spread is `0.000000` pp over nine and `ph53`'s is
`39.9`/`45.3` pp over 20. **Neither is evidence about family A and this row quotes
neither.** ⚠⚠ **AND THIS ROW SHIPS NO RESPELLING SEARCH AT ALL**, which is a gap and is §13's
first item: **`controls/spellings.py` DOES NOT EXIST IN THIS ROW** — that is a
statement of absence and the only such citation in the row — so the row publishes a
headline with **no in-contract spread beside it**. That is a real omission measured
against `ph45`'s 128-case and `ph53`'s 161-case suites, and open item 81's prediction
that a new suite would find a fifth shared defect is therefore **UNTESTED by this
row**.

## §10 The ladder — four answers to one question

*Has this slot been constructed?*

| rung | answer | what it costs |
|---|---|---|
| **R1** | it does not ask | the defect |
| **R1h** | ⭐ it **deletes the question**: `7412202c43e7` removes the one line that asks, and `:263` makes the deletion complete | §8 |
| **R2** | `Option<Pr>` + `slot.take()` — the **fourth slot state is unrepresentable** | a discriminant word and a write-back |
| **R3** | ⭐ **a port of R1h, made structural**: `make_printable_zval` *returns* the printable, so the deleted line cannot be written | — |
| **R4/R5** | **one bit per slot**, `constructed: bool`, two for the whole kernel | §11 |

### §10a ⚠ The C's slot has FOUR states and safe Rust has THREE

| the C | R2 |
|---|---|
| UNCONSTRUCTED (the stack byte) | `None` |
| `IS_STRING` + `empty_string` | `Some(Pr { req: 0, .. })` |
| `IS_STRING` + a live `emalloc` block | `Some(Pr { req: n, .. })` |
| `IS_STRING` + a pointer `:1188` has FREED | ⛔ **UNREPRESENTABLE** |

The fourth state is the defect, and `take()` leaves `None` the moment the block is
released. ⚠ **That is a FINDING and never a kill** (`CLAUDE.md` rule 6): admission
is decided on the C, and what safe Rust can and cannot say about it is the result.

⚠⚠ **And it is NOT *"`Option` reinvents the upstream fix"*.** `7412202c43e7`
deletes the **teardown** and keeps the states; `Option` keeps the teardown and
deletes the **state**. Two different repairs, and only one of them was available to
the C.

---

## §11 The Verus side

`verus.rs`: **33 verified / 0 errors**, and **34** under `--cfg slb_twin` — **four
trusted items and one twin**. §11f is the gate finding that produced that shape and
§11g is why the repair is a fidelity repair rather than a TCB inflation.

### §11a ⭐ §2.9(1)'s prediction is UPHELD, and the reproduction is now bit-exact

`controls/negatives.py --verus`, 7 arms, **all as expected**:

| arm | verdict |
|---|---|
| N1 `verus.rs` | 33 verified, 0 errors (34 under `--cfg slb_twin`) |
| N2 `controls/mu_unwrapped.rs` | 6 verified, 0 errors — the same obligation with **no trusted item at all** |
| **V1** `if *constructed` deleted | **`precondition not satisfied`** at `std_specs/maybe_uninit.rs` |
| V2 the caller's `is_init` `requires` conjunct deleted | `precondition not satisfied` |
| V3 `zval_dtor`'s witness-agreement conjunct deleted | `postcondition not satisfied` |
| V4 the tag written on a path that did not write the value | `postcondition not satisfied` |
| V5 a cosmetic rewrite (`== true`) | **33 verified, 0 errors** — must-NOT-fire |

⭐ **V1 is the whole finding:** deleting `if *constructed` is `zend.c:243` exactly,
and Verus refuses it. ▶ **F97/F98's *a rung that reproduces the defect cannot be
verified and a rung that verifies does not reproduce it* RECURS, on a second row.**

⚠⚠ **AND THE REPRODUCTION IS STRONGER HERE THAN ON ph53.**
`controls/r4_nowitness.rs` — the witness-free R4, `:243` with no test — prints
**`272040826665440682`** on `adversarial-dblfree.bin`, which is **R1's answer and
not R1h's**, because the `MaybeUninit<Pr>` retains the previous op's value exactly
as the stack slot does. **ph53's witness-free control answered *correctly* where its
R1 faulted; this one reproduces the C's defect bit for bit.**

### §11b ⚠ A §H defect in this row's own suite, found and reported

The first draft of `VERUS_MUTANTS` used the string `"error"` as two arms' expected
diagnostic. Both **passed on a `#[path]` resolution failure** — `negatives.py` writes its
mutants into a scratch directory **one level deeper** than the row, so the row's own
`#[path = "../../common/driver.rs"]` did not resolve and Verus aborted before looking
at the mutation at all. ▶ **Two must-fire arms firing for a reason that had
nothing to do with the mutation.** That is §H's own target — *a gate run exercises a
validator on the rows that pass; it does not attack it* — inside a suite written to
satisfy §H. Repaired with a specific diagnostic per arm and the re-basing made explicit in a
comment **inside `controls/negatives.py`**, where a reader of the validator meets
it; recorded here rather than quietly fixed.

### §11c ⭐⭐ The witness, and §2.9(2) — the O(slots) question, REFUTED AS STATED

| | ph53 | ph52 |
|---|---|---|
| runtime witness | `[bool; MAXD]` — **n bytes**, re-read on every consumer iteration | **two `bool`s** for the whole kernel, tested twice per op, **never indexed** |
| spec-level slot | `Seq<Option<u32>>` + an `abst()` over it | `Sl { c: bool, req: usize }` × 2 |
| trusted items | **four**, 3 twinned | **four**, 1 twinned — and §11f is what it took to get to 1 |
| `mu_unwrapped.rs` | a `Vec`, a push loop, a `forall`, `Vec`'s `IndexMut` spec | a single local, no loop, no quantifier |
| F98's price | **`+21.775 %`** in W1, on `small.bin`, at `O3/isolated`, against `controls/r4_nowitness.rs` (a **Rust** control, not the C), of which only **~44 %** is the witness — so **~`+9.6 %`** witness-only | **`+0.622 %`** in W1, same input, same level, same kind of base (§8g); there is no array, so **the whole of it IS the witness** |
| slots | up to 16, **6** on 15/16 measured windows | **2** |
| witness READS per op | `n_ops × n_decl`, through a computed address | **2**, register-resident |

▶ **VERDICT ON §2.9(2): the prediction's DIRECTION is UPHELD and its word is not.**
*"Predicted: the witness is ~FREE here"* — **`+12.41 Ir/call`, `+0.632 %` in B1, is
not free.** It is a real, reproducible figure an order of magnitude under ph53's.

⭐⭐ **AND BOTH ROWS HAVE AN ABSOLUTE `Ir/call` FIGURE, SO THE COMPARISON DOES NOT
HAVE TO GO THROUGH A PERCENTAGE AT ALL — WHICH IS THE RIGHT WAY TO DO IT:**

| | ph53 | ph52 | ratio |
|---|---:|---:|---:|
| witness cost, **Ir per kernel call** | **+101.59** (F98's own attribution, `+101.59` of `+228.87`) | **+12.41** | **8.19×** |
| slots | **6** (typical; `n_decl` 0..16) | **2** | 3× |
| **Ir per slot per call** | **16.93** | **6.21** | **2.73×** |

⛔⛔ **SO THE HOPED-FOR LAW IS REFUTED AS STATED AND REPLACED BY A DECOMPOSITION.**
*"The cost of a safety witness is O(the number of slots)"* predicts 3× the slots → 3×
the cost. Measured: **3× the slots → 8.19× the cost**, because the **per-slot** cost
is itself **2.73× higher** on ph53. ⭐ **The cost decomposes as (slots) × (per-slot
cost), and the per-slot term is what moves** — ph53's `wrote[i]` is an **indexed array
read**, re-read on every consumer iteration (`n_ops × n_decl` reads per call), where
ph52's is a **register-resident `bool`** tested twice per op (`2 × n_ops` reads).

⚠⚠ **AND THE DATA CANNOT SEPARATE THE TWO CANDIDATE MECHANISMS AT n = 2.** Normalising
by reads instead of slots gives ph53 ~`1.59` Ir/read against ph52's ~`0.39` — a 4×
gap — so *read count* and *indexed vs register* both point the same way and neither is
isolated. ▶ **What the row publishes is the decomposition and the two candidates, not
a law.** A third `T3` row would separate them; `quota.py` says three candidates remain
(`ph49`, `ph50`, `ph51`).

⭐ **Why ph52's SLOT accessor is half of ph53's, and it is a consequence of the C
rather than a choice:** ph52's slots are **two named locals**, so there is no
unchecked *slot* indexing to fold in — `slot_read_unchecked`'s `requires` carries ONE
conjunct (`is_init()`) where ph53's carries two (`is_init()` **and** `i < v@.len()`),
and there is no `slot_set_unchecked`/`pool_get_unchecked` pair at all. ⚠ Both rows
carry a `win_get_unchecked` for the window, and that one is twinned on both.

### §11d ⛔⛔ F97's collision recurs, and it is narrower

`check.py::_scan_unsafe_sites` requires every `unsafe` token in a pinned Verus
source to sit inside an `external_body` body, with no justification hatch, and
5c-twin requires every trusted item to have a **verified twin** — which for a
`MaybeUninit` read would itself need `unsafe`, because there is no safe exec route
from `MaybeUninit<T>` to `T`. **Two sound rules, jointly unsatisfiable for this
operation, a second time.** `controls/mu_unwrapped.rs` verifies the unwrapped shape
at **6/0 with no trusted item**, and `negatives.py --verus` arm N2 **runs** it, so
the fact about Verus is committed and re-checked rather than cited.

### §11e ⚠ The proof-budget overrides, disclosed with their reasons

`#[verifier::rlimit(120)]` on `kernel`, `#[verifier::rlimit(60)]` on
`lemma_run_step`, and `#[verifier::opaque]` on `s_print` and `s_concat`. **The
opacity is not taste:** left transparent, the solver unfolds both under `s_run`'s
own recursion and `lemma_run_step` blows the rlimit — measured, on the first
complete draft of the file. They are revealed exactly where they are proved and
nowhere else.

⚠⚠ **One thing measured the hard way and worth the next agent's time:** `s_run`
recurses on the **front** of its range while the loop invariant needs the op at the
**back**, so the fold's own step law is **not** free. `lemma_run_step` is one
induction on `o - a` and it is the only lemma this rung has; the first version fixed
the start index at `0` and could not be stated inductively at all.

### §11f ⛔⛔ A GATE PROPERTY THIS ROW FOUND, AND IT IS THE SAME OBJECTION `TASK_007` ACCEPTED ONE ITEM DOWN

**The row's first gate run FAILED on stage 5c-twin**, with the whole of the
failure text:

> `[twin] every trusted item in this pattern (['verus.rs:slot_read_unchecked'])
> is excused by verus.twin_justifications, so stage 5c-twin checked the strength
> of NOTHING. A hatch that can be applied to the whole of its own stage is an off
> switch …`

That is `check.py::check_trusted_twins`'s `n_twins == 0` rule, and **it has no hatch**. ⭐
**And it was RIGHT about this row**: with `slot_read_unchecked` as the only
contract-bearing trusted item, and that item genuinely untwinnable (§11d), *nothing
whatever checked the strength of the row's one trusted precondition.*

⚠⚠ **But the rule also reproduces, at n = 1, exactly the defect `TASK_007` deleted
`MAX_TWIN_JUSTIFICATIONS` for.** `check.py's deleted `MAX_TWIN_JUSTIFICATIONS` comment` records that cap's removal and
its third reason verbatim:

> *"It was the only knob in the twin regime that could hard-fail an **honest**
> pattern with no route out. A pattern with two genuinely untwinnable trusted items
> had no legal configuration."*

▶ **A pattern with ONE genuinely untwinnable trusted item and no other has no legal
configuration either**, and `n_twins == 0` is what does it. ⭐ **ph52 is the first
row in either programme to reach that**, because it is the first whose trusted
surface is *small enough* — ph53 passes the stage precisely because its trusted base
is **larger** (four items, three of them twinnable `get_unchecked` accessors on a
`Vec`). ⚠⚠ **So the rule puts pressure on a row to ENLARGE its trusted base**, which
is `.memory/02-bench-rules.md`'s *a rung is never cost-selected* one axis over.
**Reported, not worked around:** the fix would be a `harness/` edit and a 33-pattern
re-gate, and the pressure is latent rather than live because §11g is a legitimate way
out on this row.

### §11g ⭐ How the row answered it WITHOUT inventing work for the stage

`win_get_unchecked` was added — and it is a **fidelity repair the row owed anyway**,
not a TCB inflation to satisfy a gate:

* **every window read in the C is an unchecked array access.** `win[p]`,
  `win[p + 1]`, `win[p + 2]`, `win[p + 3]` and `ph52_rd32`'s four bytes: C has no
  bounds check, and nothing in `concat_function` or `zend_make_printable_zval`
  verifies that the op record is inside the window. The kernel's structural
  precondition (`8 <= len`, `off + len <= buf_len`) is what makes it sound, and it is
  discharged **at the call site** in `main`.
* ▶ **So a safe-indexed R4 pays a bounds check the C does not** — which is exactly
  the R2/R3-vs-R4/R5 distinction this ladder exists to price, and the shipped R4 was
  getting it wrong in the direction that flatters safe Rust.
* ⭐ **And it IS twinnable**, because `v[i]` is the checked stand-in for
  `*v.get_unchecked(i)`. `ph53`'s `win_get_unchecked` is the precedent, character for
  character.

⚠ **What it cost, stated rather than buried:** the R4/R5 numbers moved, the contract
sha moved, and the trusted-item count went 3 → 4 (of which 1 is twinned). §8 carries
the re-measured figures. ⛔ **The route NOT taken, and why:** making `rd32` trusted
*without* a twin, or adding a second unchecked accessor the kernel does not need,
would both have satisfied the stage by enlarging the axiom surface. This one shrinks
the gap between R4 and the C instead.

### §11h ⛔⛔ AND THE `idiom` BACKTICK LAW FIRED ON THIS ROW, BECAUSE I DID NOT RUN THE AUDIT ON THE DRAFT

`.memory-php/02-ladder.md`, landed 2026-09-13: ⭐ *a backtick in an `idiom.required`
/ `forbidden` entry **IS** a pin, including around a filename, a type name or a field
name — so **any draft of that prose goes through `idiom_audit` before it lands.***

**I did not, and the second gate run charged me ten `forbidden_hits`:**

| entry | span | refused |
|---|---|---|
| `forbidden[0].rust` | the Option type name | `safe_naive.rs`, `safe_tuned.rs` |
| `forbidden[1]` | the Vec type name, and `Vec<u8>` in the repair | `verus.rs` |
| `forbidden[2]` | Option, Some, bool — named in order to say the Rust rungs **legitimately carry them** | all four |

⛔ **Every one refused a rung for carrying its own correct code**, which is the exact
consequence `forbidden[0]`'s own last sentence warns against. ⭐ And the
second-order instance is the one worth recording: **the sentence I added to explain
the repair re-backticked `Option` and fired again.** That is
`.memory-php/02-ladder.md`'s own example verbatim — *the engineer applying it caught
one of its own the same way: a meta-sentence saying "ONLY `x` AND `y` ARE BACKTICKED
HERE" re-backticked and duplicated both.* **Neither was found by reasoning; both were
found by running the audit and reading the output.**

### §11i ⚠ A SECOND, WORSE DEFECT THE SAME AUDIT FOUND — IN `required`, WHERE THE GATE CANNOT SEE IT

`required` is presence-only and **cannot fail the gate** (`idiom_audit` measures the
naive reading at 41 misses of 158 obligations on the 33 PAT rows, all non-defects,
17 of them ANTI-signal). ▶ **So this one would have shipped.**

⛔⛔ **Four entries — `required[4]`, `[5]`, `[6]`, `[7]` — each ended with *"NO
BACKTICKED SPELLING IN THIS ENTRY"* and each contained a dozen.** `required[6]`, the
R1h entry, carried **~30**, including bare `` `1` `` and `` `0` `` matching every rung.
⚠⚠ **That is `ph53`'s own repair-in-progress defect — an entry whose appositive and
whose summary disagree about what is pinned — reproduced on the next row, and `ph53`'s
is costing a whole re-gate.** Repaired by stripping every backtick from those four,
which is what their English always claimed.

**The residual, measured and reported rather than enumerated away:**

| | |
|---|---|
| `forbidden` hits that would fail the gate | **0** |
| `required` spans matching **every** rung (ANTI-signal) | **7**, all of them entries whose English says *"Present in BOTH C rungs"* or *"present in all four Rust rungs"* — i.e. intentional |
| `required` spans matching **no** rung (pins nothing) | **25**, all file names, line citations and upstream spellings — `p42`'s `required[1]` names that class as a known convention |

⭐ **The discriminating pins, which is what the declaration is for:**
`required[0].rust` `` `*constructed = true;` `` → `unsafe.rs` + `verus.rs` only;
`required[1].rust` `` `slot_read_unchecked` `` → the same two;
`required[1].c` `` `ph52_zval_dtor(expr_copy);` `` → **`c/kernel.c` only**, which is
the upstream fix as a one-line presence test.

---

SLB-TRUSTED-ARGUMENT verus.rs win_get_unchecked

**(a) Is the twin's body the right checked stand-in?** Yes, and it is the canonical
one: the trusted body is `unsafe { *v.get_unchecked(i) }` and
`slb_twin_win_get_unchecked`'s body is **`v[i]`** — the same access with the bounds
check Rust would have inserted. The twin's signature and contract are lifted and
diffed against the trusted item's by `check.py` step 5c-twin, so a `requires` that
had drifted to something a safe implementation cannot meet (`i <= v@.len()`, say)
would fail the twin and not the shipped rung. ⭐ **That is the one stage in this gate
that judges STRENGTH rather than triviality, and on this row it judges the item that
can be judged** — §11f is what happened when it had nothing.

**(b) Is the `ensures` complete with respect to every unchecked operation the body
performs?** The body is one expression and performs **exactly one** unchecked
operation, `*v.get_unchecked(i)`, and the `requires` has exactly one conjunct for it,
`i < v@.len()`. The `ensures`, `r == v@[i as int]`, names the value of that one
element and nothing else, which is complete *as the body stands*. ⚠⚠ **And (b) is
what `TASK_009_REVIEW`'s x4 is about**: a body that also read `v[i + 1]` would pass
the contract pin, the twin and the `--cfg slb_twin` run unchanged, because the
`ensures` never mentions it. Nothing mechanical catches that. What backs it here:
`identity` is **`norel` at `-O3`** — R4 and R5 are the same machine code — so a
`verus.rs`-only extra read would move `md5_raw_norel` and stage 3c would see it; and
§7d's Miri arms run the shipped R4 on every input and are silent. ⚠ At `-O0` the two
rungs `differ`, so that backstop is an `-O3` backstop only, and I am saying so rather
than implying it covers both levels.

**(c) Does each clause mean the same thing in both configurations?** Yes. Both
clauses are over `v@` and `i`, which are the function's own arguments; a `&[u8]`'s
view is the same in every build, and `v@.len()` is `spec_slice_len` in every build.
The token `slb_twin` appears in this file **only** on the twin's own `#[cfg]`
attribute, which `check.py::_check_twin_cfg_hygiene` is what confirms — so there is no
`cfg`-dependent expression anywhere in either clause.

---

SLB-TRUSTED-ARGUMENT verus.rs slot_read_unchecked

**(a) Is the twin's body the right checked stand-in?** ⛔⛔ **THERE IS NO TWIN, AND
THERE CANNOT BE ONE — §11d, which is the row's finding rather than a concession.**
A twin has to be a VERIFIED exec function meeting this contract, whose `ensures` is
`r == m.mem_contents().value()`, so its body must get a `Pr` **out of** a
`MaybeUninit<Pr>`. The pinned vstd offers exactly three routes — `assume_init`,
`assume_init_ref`, `assume_init_mut` — and **all three are `unsafe fn`**; there is
no safe exec expression from `MaybeUninit<T>` to `T`, which is what the type means.
Any twin's body would therefore contain an `unsafe` token outside a trusted item's
body, and `check.py::_scan_unsafe_sites` refuses exactly that, with no hatch. ⚠
**So what is NOT checked here is precisely what a twin checks: that this `requires`
is STRONG ENOUGH to license a checked implementation.** What replaces it: (i)
`controls/mu_unwrapped.rs` verifies the UNWRAPPED shape at **6 verified / 0
errors** and `controls/negatives.py --verus` arm N2 runs it — vstd's own
`assume_init_ref` specification carrying the same obligation in ordinary exec code
with **no trusted item**, so the contract asserted here is demonstrably the one
vstd asserts; (ii) arm **V1** deletes the caller's `if *constructed` and Verus
refuses with `precondition not satisfied` at `std_specs/maybe_uninit.rs`; (iii)
arm **V2** deletes the `requires` conjunct that supplies the initialisedness and
Verus refuses independently; (iv) arm **V3** deletes the witness-agreement conjunct
and the postcondition fails; (v) §7d's Miri arms are silent on the shipped rung and
**loud** on the witness-free control, on a blob `inputs/` cannot carry.

**(b) Is the `ensures` complete with respect to every unchecked operation the body
performs?** The body is `unsafe { *m.assume_init_ref() }` — **ONE** unchecked
operation, and the `requires` has exactly one conjunct for it,
`m.mem_contents().is_init()`, which is literally what the pinned vstd's own
`assume_specification` demands (`std_specs/maybe_uninit.rs:45-49`). The `ensures`
names the value of that one slot and nothing else, which is complete *as the body
stands*. ⭐ **And the surface is smaller than ph53's by construction, not by
care:** ph53's equivalent item folds a `get_unchecked` in and needs
`i < v@.len()` as well, because its slots are an array; ph52's are two named
locals, so there is no index, no range obligation, and no second unchecked
operation for an `ensures` to miss. ⚠⚠ **Nothing mechanical enforces (b) and the
`identity` pin is `differ` on this row, so stage 3c would not catch a
`verus.rs`-only extra read either. On this item (b) rests on Miri and on review,
and I am saying so rather than implying a backstop the row does not have.**

**(c) Does each clause mean the same thing in both configurations?** Yes, and the
question is thinner than usual here because **there is no twin configuration to
differ from**: both clauses are over `m`, the function's own argument;
`MaybeUninit<Pr>`'s view is the opaque `external_type_specification` type in every
build and `mem_contents()` is `uninterp` in every build, so nothing about the
clauses' meaning can depend on a `cfg`. The token `slb_twin` appears nowhere in
this file at all, there being no twin to gate — which `check.py::_check_twin_cfg_hygiene`
is what confirms.

---

## §12 ⛔⛔ FOUR CITATION DEFECTS IN COMMITTED FILES, AND WHY THE REPAIR WAS TO WRITE THE FILES

**Four paths were cited by committed files and did not exist.** Found by a script that
asks *does every cited path resolve*, not by reading:

| cited path | cited by | digest |
|---|---|---|
| `controls/digest.py` | `c/kernel.c`, `c/kernel.h`, `c/kernel_hardened.c`, all four `.rs` rungs | **MEASUREMENT** |
| `controls/tu_boundary.sh` | `c/kernel.c`, `c/kernel_hardened.c` | **MEASUREMENT** |
| `controls/dblfree.py` | `inputs/gen.py` | **MEASUREMENT** |
| `controls/firstcall.py` | `inputs/gen.py` | **MEASUREMENT** |

⚠⚠ **ALL FOUR ARE IN THE MEASUREMENT DIGEST, WHICH IS `.memory-php/04-process.md`
LAW 14 EXACTLY**: *a C kernel's comments are hashed at MEASUREMENT price, so provenance
prose inside one is effectively frozen.* ▶ **Correcting the POINTERS would have cost a
32-cell re-measure. Writing the named files cost ONE re-gate**, because `controls/*` is
gate-only. ⭐ **So the cheap repair and the honest repair were the same one**, and the
row took it.

⚠ **Two of the four are thin**, and they say so in their own headers:
`controls/tu_boundary.sh` is four lines that `exec`s `d0_stack.py`, and
`controls/firstcall.py` calls `negatives.py::arm_firstcall`. ⛔ **Neither is a second
implementation and neither may become one** — two copies of a measurement is how they
disagree, which is `harness/asm.py`'s own founding lesson.

⭐⭐ **The other two are real controls the row wanted anyway**, and one of them found a
defect in my own reasoning: `controls/digest.py`'s arm **N3c** asserted that folding the
handle's digits most-significant-first differs from least-significant-first on every
handle ≥ 10. **It does not — a PALINDROME folds the same either way, and the agreeing
set is exactly the 35 palindromic handles in a byte** (10 one-digit, 9 two-digit, 16
three-digit). ▶ **So a corpus whose object handles happened to be palindromic would be
blind to the digit order, on 35 of 256 values** — `ph03`'s monoculture with a different
shape — and `inputs/gen.py` does **not** assert non-palindromic handles. ⚠ Recorded
rather than claimed as covered; §13.7 carries it.

---

## §13 What I am unsure of

⚠ **`UNTESTED` and *"I could not tell"* are valued answers.** The full list is
`.tasks-php/TASK_PHP_045_REPORT.md` §12; the ones a reader of this row needs are:

1. ⛔⛔ **THIS ROW SHIPS NO RESPELLING SEARCH.** There is no `controls/spellings.py`,
   so the row publishes its headlines with **no in-contract spread beside them** —
   measured against `ph45`'s 128-case and `ph53`'s 161-case suites. ▶ **Open item
   81's prediction that a new suite would find a FIFTH shared defect in the
   machinery is therefore UNTESTED by this row**, and so is the question of how much
   of §8b's `−0.342 %` and §8g's `+0.622 %` survives a search over the variants the
   declaration leaves free. **That is the largest single gap in the row.**
2. ⚠ **§11c's two-row law rests on n = 2.** *The cost of a safety witness tracks the
   number of witness READS and whether they are indexed, not the number of slots* is
   a hypothesis with two points on it. `quota.py` says three `T3` candidates remain
   (`ph49`, `ph50`, `ph51`); a third row is what would settle it.
3. ⚠ **§8e's cross-language ratio is not a safety figure and I cannot make it one.**
   The C rung runs the real allocator (16.2 M Ir in libc, 11.1 % of the cell) where
   the Rust rungs simulate counters. §B1a.3's label is applied; the underlying
   comparison is not repairable at this row's allocation order.
4. ⚠ **`identity` is `norel` at `-O3` and `differ` at `-O0`, so stage 3c backs
   §11's trusted-argument (b) at one level only.** I do not know why `-O0` differs by
   exactly 3 instructions and I did not chase it; the pin states what was measured.
5. ⚠ **The kernel-overlap heuristic reads 19 % against a `narrowed` expectation of
   25 %** (§2). I think it is right about the text and wrong about the row, and I say
   why in §2 — but it is a judgement and a reviewer may disagree.
7. ⚠⚠ **`inputs/gen.py` DOES NOT ASSERT NON-PALINDROMIC OBJECT HANDLES**, and §12's
   `digest.py` N3c is why that matters: the handle's digits are folded
   least-significant-first, and on the **35 palindromic handles in a byte** that is
   indistinguishable from most-significant-first. ▶ **A corpus whose handles were all
   palindromic would be blind to the digit order.** The shipped corpus is not (it spans
   all three digit counts and `_check_history` asserts that), but the *non-palindromic*
   property is **not asserted** and I found the gap from a failing assertion of my own
   rather than from reading. ⛔ It is `ph03`'s monoculture with a different shape.
6. ⚠ **`controls/negatives.py --firstcall` measured R1 == R1h on the op-0-faulting
   blob, i.e. the 95.3 % outcome.** That is **recorded and not required**: it is the
   C runtime's startup residue and a different libc, a different kernel or a
   different link order could make it one of the 12 freeing tags. The corpus does not
   rest on it (`inputs/gen.py` rule R1 is what makes that true) but the control's
   output will change without notice.
