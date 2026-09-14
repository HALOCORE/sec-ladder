# ph55 — NOTES

Measurements, adjudications and the things no gate stage can judge.
`spec.md` is the contract; `README.md` is the reader's entry point.

⚠ Every percentage below names **the statistic, the input, the opt/mode level,
the base — and, where the base is a C cell, WHICH COMPILER, with both columns.**
`.memory-php/03-numbers.md` F108: two published claims in the authoritative
layer changed **sign** under `c-gcc` → `c-clang`. **No `O0` figure is quoted as
a performance result** anywhere in this file.

---

## 1. What the row is, in nine facts

All nine were read on the pristine tarball (`sha256 5783e0c0…`) and every one is
pinned as a `provenance` span in `spec.md`.

| # | fact | site |
|---|---|---|
| 1 | a compound assignment to an array dimension is a **two-word** instruction: `zend_op *op_data = opline+1;` | `Zend/zend_execute.c:1742` |
| 2 | the handler records that at run time in a **local flag**: `zend_bool increment_opline = 0;`, set to 1 **only** on the `ZEND_ASSIGN_DIM` arm | `:1728`, `:1749` |
| 3 | ⛔ the **error exit does not consult the flag** — `if (*var_ptr == EG(error_zval_ptr)) { …; NEXT_OPCODE(); }` | `:1765-1770`, the `NEXT_OPCODE()` at `:1769` |
| 4 | ✅ the **normal exit does** — `if (increment_opline) { INC_OPCODE(); } NEXT_OPCODE();` | `:1792-1795` |
| 5 | `NEXT_OPCODE()` = `EX(opline)++; return 0;` — stride 1 **and** a return. `INC_OPCODE()` = `if (!EG(exception)) { EX(opline)++; }` — conditional, no return | `:1317-1320`, `:1326-1330` |
| 6 | `ZEND_API opcode_handler_t zend_opcode_handlers[512];` | `:1338` |
| 7 | ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` — explicit, and the **only `= NULL` among the 130 `zend_opcode_handlers[...]` assignments** in `zend_init_opcodes_handlers()` (`:4276-4443`, 168 lines). Measured, not estimated | `:4427` |
| 8 | `pass_two` copies the table into **every** instruction: `opline->handler = zend_opcode_handlers[opline->opcode];` | `Zend/zend_opcode.c:363` |
| 9 | ⛔ the executor dispatches through that field with **no NULL check** | `:1383-1394`, the call at `:1391` |

▶ error arm → PC strides 1 → the PC lands on the trailing `ZEND_OP_DATA` word →
that word's `handler` field is `NULL` → unconditional indirect call through NULL.

### ⭐ The sentence the crash course wants

`INC_OPCODE()` has **four** call sites in 5.0.0 — `:1719`, `:1793`, `:2193`,
`:2224` — and **three are unconditional**, because those handlers are
**statically** two-word. Two of the three carry a shouting comment in the
original, exclamation marks and all:

```
/* assign_obj has two opcodes! */        :2192
/* assign_dim has two opcodes! */        :2223
```

`zend_binary_assign_op_helper` is the **only** one of the four whose instruction
width is **data-dependent** — it dispatches on `opline->extended_value` and is
one-word for `default`, two-word for `ZEND_ASSIGN_DIM`. That is why it needs a
flag, and it is the one with the bug.

▶ **The codebase shouts the invariant at the two sites that get it right, and is
silent at the site where the invariant became conditional.**

✅ Both siblings were read and both are **clean** — `zend_assign_obj_handler`
(`:2186-2195`) and `zend_assign_dim_handler` (`:2198-2226`) have exactly one
exit each. **No sibling site is owed.** The second of them is **lifted into this
kernel** as `PH55_ASSIGN_DIM`, so the contrast between a static width and a
data-dependent one is inside the measured program and not only in a comment.

---

## 2. ⚠⚠ THE TIER: the catalogue says `narrowed` and this build declares `modelled`

`PROTOCOL_PHP.md` §F9 asks the builder to read the kernel-overlap number and say
what they think of it, because the demotion from a floor to a report moved the
judgement from the tool to a person. Here it is.

`harness-php/provenance.py ph55-opdata-stride` reports:

```
per-span overlap: span0 16% (7/45)   the defect site, zend_execute.c:1724-1796
                  span1 30% (3/10)   the two stride macros + the 512-entry table
                  span2 14% (1/7)    the dispatch loop
                  span3 12% (2/17)   zend_assign_dim_handler, the clean sibling
                  span4  0% (0/2)    zend_opcode_handlers[ZEND_OP_DATA] = NULL
                  span5 15% (3/20)   pass_two's handler copy
kernel overlap 14% (13/93 excerpt lines)
```

`narrowed` leads a reader to expect **25 %**, and the defect site alone measures
**16 %**. ▶ **The catalogue's `narrowed` is a mining-wave label and this build
refutes it. The row declares `modelled`.**

**What IS lifted one for one — the control flow, which is what the row
measures:** the flag and its single assignment; the `op_data = opline + 1` read;
both exits, in upstream's order, 23 lines apart; both stride macros with
upstream's bodies including `NEXT_OPCODE()`'s trailing `return 0;`; `pass_two`'s
handler copy; the `= NULL` table entry; and a dispatch loop with nothing between
the `handler` field and the call.

**What is RE-EXPRESSED, which is what `modelled` names:** zvals become
`(kind, val)` pairs in a flat store and `zval **` becomes an index; the hash
container is gone; the opcode set is ten opcodes standing for the **130** `zend_opcode_handlers[...]` entries `zend_init_opcodes_handlers()` fills (counted, `:4276-4443`); and
the compiler's emitter guarantee is supplied by a run-time pass (§4).

⚠ **A tier is a COST and never a filter** (`PROTOCOL_PHP.md` §A1), and a tier
read as **stronger** than it is, is the dangerous direction. ⚠ `span4` scoring
**0 %** is not a defect either: it is a two-line span whose text is
`zend_opcode_handlers[ZEND_ASSIGN_OBJ] = …` / `= NULL`, and the kernel writes
the same fact as a C99 designated initialiser. The heuristic measures TEXT.

ⓘ `unevaluable_conditionals` = **1** (`#ifndef PH55_KERNEL_H`), so the residual
the heuristic could not evaluate is one include guard. That is as small as it
gets and it does not qualify the number.

---

## 3. ⭐ ITEM 95 IS CLOSED — deliberate hand-off, not a second defect

`INC_OPCODE()`'s own `if (!EG(exception))` guard means that **with an exception
pending the normal exit also advances by only one word**. Item 95 asked whether
that is a *second* instance of the defect. **It is not**, and the trace is:

`Zend/zend_exceptions.c:36-59`, `zend_throw_exception_internal`:

```c
53   if ((EG(current_execute_data)->opline+1)->opcode == ZEND_HANDLE_EXCEPTION) {
54       /* no need to rethrow the exception */
55       return;
56   }
57   EG(opline_before_exception) = EG(current_execute_data)->opline;
58   EG(current_execute_data)->opline = &EG(active_op_array)->opcodes[EG(active_op_array)->last-1-1];
```

`last-1-1` is `last-2`, and `ZEND_HANDLE_EXCEPTION` is the **last** opcode —
`zend_do_end_function_declaration` emits `zend_do_return(…)` then
`zend_do_handle_exception(…)` (`Zend/zend_compile.c:1091-1092`, and
`zend_do_handle_exception`'s own body at `:1078-1085`). ▶ **So the throw parks
the PC one slot SHORT of the handler, in anticipation of the `EX(opline)++`
that the handler's own trailing `NEXT_OPCODE()` will perform.** ✅ Line 53 reads
the same invariant back: *"`opline+1` is `ZEND_HANDLE_EXCEPTION`"* is exactly
the state `:58` creates.

▶ **`INC_OPCODE()`'s guard exists to stop the stride being spent TWICE.** It is
a **correction**, not an omission.

**Consequence, and it is why this row has ONE faulting exit and not two:** the
exception path is correct, and modelling it would add a whole exception
machinery for no mechanism. `PH55_EXCEPTION` is pinned to `0` and
`INC_OPCODE()`'s body is otherwise upstream's, token for token.
`provenance.divergences` itemises it as a **projection**. ⚠ **It was considered
and it is out; this section is the record.**

⭐ **And it strengthens the row:** the same function guards its stride correctly
against **two** hazards on one exit — the `increment_opline` flag *and*
`EG(exception)` — and against **neither** on the other exit, 23 lines earlier.

---

## 4. ⭐ THE EMITTER'S GUARANTEE, and why the PC provably stays inside the op_array

Two structural facts do all the work, and neither is a check in the executor.

**(a) The two-terminator tail.** `zend_do_end_function_declaration` emits
`ZEND_RETURN` then `ZEND_HANDLE_EXCEPTION`, so every op_array ends with two
one-word instructions that stop execution. `c/kernel.c`'s decoder writes both
(`PH55_RETURN` twice; the second is the exception word's projection, §3). With a
maximum stride of **2**:

> the PC can only leave the array by striding from `p` to `≥ nops`, which needs
> `nops − p ≤ 2`, i.e. `p ≥ nops − 2` — and at `nops − 2` and `nops − 1` the
> opcode is `ZEND_RETURN`, which **halts**. ∎

That argument is why the dispatch loop needs no PC bound, which is the row. It
is also what makes `opline + 1` safe for every two-word instruction: a two-word
instruction can only sit at `p ≤ nops − 3`.

**(b) No instruction START is a data word.** `zend_compile` emits
`ZEND_OP_DATA` **only** as the trailing word of a two-word instruction, so the
executor may dispatch through `opline->handler` without testing it. **The
compiler is outside this row** — the blob *is* the op_array — so something here
must stand in for it, and that is `ph55_emit_fixup` / `emit_from`: a walk that
visits exactly the words a **correct** executor visits and refuses a data word
at any of them.

⚠⚠ **It touches nothing else, and that clause is load-bearing.** A pass that
normalised *every* data word would make `inputs/adversarial-opdatalive.bin`
unrepresentable and delete half this row's result (§6).

⭐ In `verus.rs` fact (b) is the spec function `ok_from`, and `emit_from` is
**tail recursion** so that its postcondition is `ok_from`'s own unfolding — two
`reveal_with_fuel` asserts and no lemma. Written as a `while` loop it needs an
invariant quantified over instruction starts plus a glue lemma. **The shape of
the property decided the shape of the code, in every Rust rung.** `c/kernel.c`
writes the loop, because C has nothing to prove. §10 prices it.

---

## 5. R1h IS A HAND BACKPORT — `git apply` fails, and three legs identify the exit

`4f68f3774c34` (Stanislav Malyshev, 2004-08-30, *"fix crash #29893"*) is **one
file, three insertions, zero deletions**; the bytes are at
`controls/4f68f3774c34.patch`:

```
@@ -1942,6 +1942,9 @@ static inline int zend_binary_assign_op_helper(…)
 			AI_USE_PTR(EX_T(opline->result.u.var).var);
 		}
 		FREE_OP_VAR_PTR(free_op1);
+		if (increment_opline) {
+			INC_OPCODE();
+		}
 		NEXT_OPCODE();
 	}
```

⭐⭐ **The fix is the normal exit's own three lines, copied onto the error
exit.** Nothing is invented. It is the cleanest R1h in either programme.

⚠⚠ **AND IT DOES NOT APPLY TO 5.0.0.** The commit is against 2004-08-30 HEAD
(hunk header `@@ -1942,6 +1942,9 @@`); 5.0.0 shipped 2004-07-13 with the
function at `:1724-1796`; and by fix time the error exit had gained an inner
block and a `FREE_OP_VAR_PTR(free_op1);` that `:1765-1770` does not have.
`controls/r1h_backport.py` **runs** `git apply` against the pristine span and
records the failure rather than asserting it:

```
error: while searching for:
			AI_USE_PTR(EX_T(opline->result.u.var).var);
		}
		FREE_OP_VAR_PTR(free_op1);
		NEXT_OPCODE();
error: patch failed: Zend/zend_execute.c:1942
```

⭐ **And it ships the POSITIVE control that makes that verdict worth anything:**
`controls/4f68f3774c34-backport-5.0.0.patch` is the **same three `+` lines,
character for character**, with 5.0.0's own context. It applies cleanly and
moves the bytes, at `:1765-1770`, which is the hand backport `c/kernel_hardened.c`
carries.

⛔⛔ **AND THE FIRST VERSION OF THAT CONTROL GOT THE ANSWER BACKWARDS, WHICH IS
A HAZARD WORTH MORE THAN THE ROW.** It used `git apply --check` in a scratch dir
under `.temp/`. **`git apply` SILENTLY SKIPS a patch whose target path is
gitignored in the enclosing repository and returns exit 0** — so `--check` said
`0`, the control printed **APPLIED**, and nothing had been applied. Measured, and
reproduced on every run by `gitignore_trap()`: `path_is_gitignored=True`,
`git apply --check` **rc 0**, `bytes_moved=False`; the same patch in a standalone
`git init` repo gives `error: patch does not apply`. ▶ **`--check` is not the
test. The bytes are.** ⚠ Any control in this programme that scratches under
`.temp/` and trusts `git apply --check` is unsound for the same reason.

### ⛔ Which exit — and it is NOT settled by the screen

`preimage_screen.py --id CRASH-023` returns **`CANDIDATE`** with
`hits [[1769, "\t\tNEXT_OPCODE();"]]`, `misses []`, `n_matchable 1`,
`n_dropped 0`. ⚠⚠ **`NEXT_OPCODE();` occurs 117 times in that file** — ⓘ `TASK_PHP_048` §2.3
says **115** and it is off by two; `controls/r1h_backport.py` counts it on every
run rather than quoting it — so *"1/1
cited 5.0.0 lines are present in the pre-image"* is true and nearly
information-free. ▶ **The screen has done its job — it is an EXCLUSION tool
(F68 / item D11) and it correctly declines to exclude — and this row does not
quote it as confirmation.** ⓘ `preimage_screen.py --selftest` PASSES.

**The three legs that do settle it, all offline and all re-derived here:**

1. **The hunk's own function-context line names the function**:
   `@@ … @@ static inline int zend_binary_assign_op_helper(…)`.
2. **`increment_opline` is a local of that function and of no other.** Measured:
   it occurs exactly **three** times in the whole of `zend_execute.c` —
   `:1728`, `:1749`, `:1792` — and all three are inside `:1724-1796`.
3. **The other exit already carries the identical guard at 5.0.0** (`:1792-1794`),
   so a patch adding it *there* would be adding a duplicate. ∎

### ⚠ What is NOT verified

Whether `4f68f3774c34` is the **first** commit to close this site, and whether
any 5.0.x branch backport preceded it. It is what `index.csv` names, its patch
really does add the guard at the error exit, and 5.0.0 is unguarded. What was
**not** done is a tag-by-tag bisect. `PROTOCOL_PHP.md` §F5(iii) asks for
confirmation against the tags; this row confirms the **site** and the
**direction**, not the exact commit. It is in §13.

---

## 6. ⭐⭐⭐ THE TWO ADVERSARIAL CASES, PRICED SEPARATELY — one byte apart

`controls/stride_bug.py` produces this table on every run and refuses to print a
claim its own measurement stopped supporting. `inputs/gen.py` **asserts** that
the two blobs differ in exactly one byte (offset 16 — the opcode field of the
trailing data word: `7 = OP_DATA` against `3 = ADD`).

⚠ The Rust rows are **mutants, not rungs**: every shipped Rust rung implements
R1h and never mis-strides, so a table built from the shipped binaries would be
all-green and say nothing. Each mutant is the shipped `.rs` with
`4f68f3774c34`'s three lines deleted by exact-string substitution, **hit count
asserted**.

| rung | `adversarial-nullcall.bin` | `adversarial-opdatalive.bin` |
|---|---|---|
| **R1h and every shipped rung** | `15498615717350492160` | `15498615717350492160` |
| `c/kernel.c` (C, the bug) | ⛔ **SIGNAL 11** | `17484701542569762048` (**wrong**, exit 0) |
| `safe_naive.rs` + the bug | ⛔ **PANIC** | `17484701542569762048` — **== C, bit for bit** |
| `safe_tuned.rs` + the bug | ⛔ **PANIC** | `17484701542569762048` — **== C** |
| `controls/fnptr_dispatch.rs` + the bug (`Option<fn>`) | ⛔ **PANIC** | `17484701542569762048` — **== C** |
| `unsafe.rs` + the bug (`unwrap_unchecked`) | **`11370550710093900800`** | `17484701542569762048` — **== C** |

### What safe Rust does, in each case

* **`adversarial-nullcall.bin`** — C dies of a signal; a **safe** Rust port
  carrying the same bug **panics** on the `Option`. ⭐ A real difference, and it
  is a **finding, not the row's purpose**.
* **`adversarial-opdatalive.bin`** — C answers `17484701542569762048` and a
  **safe** Rust port carrying the same bug answers **the same value**. ⛔ **The
  `Option` caught the NULL. It did not catch the wrong PC.** Nothing in either
  language notices: `model.py::sanitizer_expect` declares this input **`clean`**,
  and it is, because there is no memory error to report — only a wrong answer.

⭐⭐ **AND THE ROW FOUND A THIRD BEHAVIOUR NOBODY PREDICTED.** `unsafe.rs` with
the bug does **not** crash on the NULL case: `unwrap_unchecked` on a `None` is
undefined behaviour, LLVM took it, and the program ran to completion printing
`11370550710093900800` — a **third** value, agreeing with neither C nor R1h.
▶ **On this input, unsafe Rust carrying the bug is strictly worse than C: C at
least segfaults.** That is the `unwrap_unchecked` lever's real price and it is
why `miri.required` is `true`.

### ⚠ Item: this is why `sanitizer_expect` derives from the NULL dispatch

`model.py` runs each window **twice** — once with the fix and once without — and
declares `fires` iff the unfixed run **NULL-dispatches**, not iff it
mis-strides. The two adversarial inputs mis-stride identically. That asymmetry
is the row's headline and not a concession.

---

## 7. ⛔⛔ VERUS DOES NOT SUPPORT FUNCTION POINTER TYPES — and that is this row's mechanism

```
error: The verifier does not yet support the following Rust feature:
       function pointer types
  --> controls/fnptr.rs:69:13
   |
69 | fn dispatch(t: &[Option<H>; 4], i: usize, x: u64) -> (r: u64)
   |             ^^^^^^^^^^^^^^^^^^
```

Measured 2026-09-14 against Verus `0.2026.08.09.92f466f`. `controls/fnptr.rs`
is a **must-fire negative** and `controls/negatives.py --verus` runs it on every
invocation, because the day Verus grows function pointers is the day four of
this row's files should be rewritten.

⚠ **It is a TYPE-LEVEL refusal, not a proof failure**, which is what decides the
row. `.memory/04-verus.md`'s rule is to read the ERROR TEXT: `is not supported`
forces a **new trusted item** — except that here there is nothing to make
trusted, because the refusal is on the **parameter's type**. A
`#[verifier::external_body]` wrapper does not help: any Verus-visible signature
mentioning `[Option<fn(..)>; N]` is refused, so the op_array itself would have
to be opaque, and an opaque op_array cannot carry `ok_from` or the value
postcondition.

▶ **So all four Rust rungs store an `Option<u8>` handler ID and dispatch with a
`match`.** It is not a choice R4 could have made differently: `spec.md`'s
`identity` pins R4 and R5 to the same machine code, so **a representation R5
cannot express is one R4 may not use either.**

⭐ **It changes NO answer.** `Option<fn>` and `Option<u8>` are `None` for exactly
the same opcode, so both spellings turn C's NULL call into the same `unwrap()`
panic — measured, in §6's table, where `fnptr_dispatch` behaves identically to
`safe_naive`. **What moves is instructions**, and §8f prices it.

---

## 8. The numbers

**Environment**: `.memory/00-environment.md`. gcc 13.3.0, clang 22.1.6, rustc
1.97.1 (LLVM 22.1.6 — same backend, exactly), Verus `0.2026.08.09.92f466f`,
valgrind 3.27.1. All figures `O3/isolated` unless stated. `n_iters = 20 000` on
both measured inputs; `small.bin` is a 128-byte window (16 instruction words)
and `large.bin` a 512-byte window (64 words, `PH55_MAX_OPS`).

### 8a. ⭐⭐⭐ `inside_share` FIRST, AND IT DECIDES THE COLUMN

`.memory-php/03-numbers.md`: *family A resolves a code difference exactly to the
extent the difference lands INSIDE the kernel symbol*, and `inside_share` is
**per CELL, not per ROW**. Measured here (`A1 / W1`, `O3/isolated`):

| cell | `small.bin` | `large.bin` |
|---|---|---|
| `c-gcc` | **81.75 %** | **73.97 %** |
| `c-gcc-h` | **82.61 %** | **74.94 %** |
| `c-clang` | **76.20 %** | **74.37 %** |
| `c-clang-h` | **76.20 %** | **74.37 %** |
| `safe_naive` | 96.66 % | 98.91 % |
| `safe_tuned` | 96.16 % | 98.71 % |
| `unsafe` | 95.88 % | 98.58 % |
| `verus` | 95.89 % | 98.58 % |

⛔ **THE MANAGER'S GUESS IS REFUTED FOR THE C CELLS.** `TASK_PHP_048` §2.7
offered, as a guess, that *"the whole mechanism is inside the dispatch loop, so
`inside_share` should be high on every cell and A1 should resolve this row
well"*. The Rust cells are 96–99 %; **the C cells are 74–83 %, and
`|Δinside_share|` between the C and Rust columns is up to 25 pp — an order of
magnitude past `STATISTICS_001.md`'s `≤ 0.02` condition.**

⭐⭐ **AND THE CAUSE IS THE ROW'S OWN MECHANISM.** In C the handlers are reached
**through a function pointer**, so they cannot be inlined and each is its own
symbol: 17–26 % of a C cell's instructions are in callees `kernel_exclusive_ir`
never sees. In Rust the `match` arms are inlined into `kernel`, so 96–99 % is
inside. **The dispatch representation §7 is about is exactly what moves
`inside_share`.**

▶ **So this row publishes its CROSS-LANGUAGE column in W1**, and its
**same-language** Rust ratios in A1 (`|Δinside_share|` across the four Rust
cells is 0.78 pp on `small.bin` and 0.33 pp on `large.bin`). Both statistics are
published below, labelled.

### 8b. ⛔⛔ A1 IS BLIND TO THIS ROW'S OWN R1-vs-R1h COLUMN — and `inside_share` does not warn you

`c/kernel.c` and `c/kernel_hardened.c` compile to a **byte-identical `kernel`
symbol** under both compilers: `md5_fn 11d21e546a4f5cfd` (gcc, 460 insns,
2 194 B) and `55caf689768d03e5` (clang, 168 insns, 718 B), `asm.py` level
**`exact`**. And yet **one of the two binaries SEGVs on
`adversarial-nullcall.bin` and the other answers.**

▶ **The defect is not in `kernel`. It is in `ph55_binary_assign_op_helper`**,
which is reached through the function-pointer table and therefore cannot be
inlined into `kernel`. A1 — `kernel_exclusive_ir` — is **structurally blind to
the defect site of its own row**, and reports the fix at **`0.000 %`** on every
cell and every input.

⭐⭐⭐ **THE LESSON, AND IT IS ABOUT THE RULE AND NOT ABOUT THIS ROW:** an
`inside_share` of **74–83 %** is *high*, and A1 is **still** blind here, because
what matters is not how much of the cell A sees but whether **the DIFFERENCE**
lands inside it. `STATISTICS_001.md` §4 says so in terms — *"the exact flip
condition is geometric… deciding whether A is safe to publish requires computing
the statistic the rule would let you skip"* — and this row is a clean worked
instance of it. **Do not read a high `inside_share` as a certificate.**

### 8b-2. ⛔⛔⛔ AND W1 ON THIS ROW MOVES WITH THE LENGTH OF `argv[1]` — a `−0.398 %` was one paste away from being published

⚠⚠ **This section exists because the row nearly published an artefact.** §8c's
R1-vs-R1h table was first computed with a **relative** input path and gave
`c-clang → c-clang-h = −0.0007 Ir/call` — free. Recomputed with an **absolute**
path, the same two binaries gave **`−7.004 Ir/call` = `−0.398 %`**. Nothing was
rebuilt; `md5sum` on both binaries is identical across the two runs.

`controls/argv_align.py` sweeps eight `argv[1]` lengths over the **same
binaries** and the **same input bytes**. Measured (`small.bin`, whole-program
`Ir`, eight path lengths from 61 to 75 bytes):

| pair | median Δ | sweep range | magnitude | sign |
|---|---|---|---|---|
| `c-gcc → c-gcc-h` | **−395 640** | 104 | **RESOLVABLE** | stable |
| `c-clang → c-clang-h` | +10 | **140 058** | ⛔ **NOT RESOLVABLE** | unstable |
| `safe_naive → safe_tuned` | −5 092 796 | **0** | RESOLVABLE | stable |
| `safe_tuned → unsafe` | −2 372 242 | 32 | RESOLVABLE | stable |
| `unsafe → verus` | +22 574 | 74 | RESOLVABLE | stable |
| `c-gcc-h → safe_tuned` | −2 347 363 | 110 | RESOLVABLE | stable |
| `c-gcc-h → unsafe` | −4 719 610 | 112 | RESOLVABLE | stable |
| `c-clang-h → unsafe` | −2 296 019 | 140 123 | RESOLVABLE | stable |
| `c-clang-h → safe_tuned` | +76 223 | **140 123** | ⛔ **NOT RESOLVABLE** | **stable** |

**The mechanism.** A longer `argv[1]` shifts the initial stack pointer and with
it the alignment of every frame below. This kernel zeroes a 1 024-byte
`[Op; 64]` and a 42-slot zval store on **every call**, so an alignment change
moves `memset`'s entry path: 7 Ir per call over 20 000 calls is 140 000 Ir, i.e.
0.4 % of the whole program. ⚠ **The mechanism is INFERRED from the size and
shape of the step, not proven** — what is *measured* is that a cell's total
takes exactly two values and which one depends on the path length. §13.

⭐⭐ **AND THE CONTROL FORCED A DISTINCTION THE ROW NEEDED.** Its first version
had only a magnitude test and it refused `c-clang-h → safe_tuned` — whose delta
is `+216 k` or `+76 k` depending on which side of the step `c-clang-h` lands.
**Both are positive.** So the *magnitude* is not quotable and the *sign* is, and
§8d's F108 headline needs only the sign. **A single verdict would have thrown
away a real result in order to avoid quoting an unreal one.**

▶ **THE RULE THIS ROW OBEYS: a LEVEL is never quotable; a DIFFERENCE is quotable
as a number only when it survives the sweep, and as a SIGN only when every delta
in the sweep agrees.** `.memory-php/03-numbers.md`'s *"never difference two
records taken in two shells and call the result its cost"* is the same rule from
the other end, and this is it firing.

### 8c. §2.8 PREDICTION 2: SCORED, AND **REFUTED**

> *"The upstream fix costs a measurable, non-zero amount — it adds a branch on
> `increment_opline` to a hot dispatch loop."*

**It does not.**

| statistic | input | `c-gcc` → `c-gcc-h` | `c-clang` → `c-clang-h` |
|---|---|---|---|
| **A1** Ir/call | `small.bin` | 1553.348 → 1553.348 = **`0.000 %`** | 1340.587 → 1340.587 = **`0.000 %`** |
| **A1** Ir/call | `large.bin` | 3774.095 → 3774.095 = **`0.000 %`** | 3678.382 → 3678.382 = **`0.000 %`** |
| **W1** Ir/call | `small.bin` | 1900.157 → 1880.374 = **`−1.041 %`** ✅ resolvable | **`0.000 %` ± 7.00 Ir/call** ⛔ not resolvable |
| **W1** Ir/call | `large.bin` | 5102.041 → 5036.190 = **`−1.290 %`** ✅ resolvable | **`0.000 %` ± 7.00 Ir/call** ⛔ not resolvable |

*(W1, `O3/isolated`, medians over `controls/argv_align.py`'s eight-length sweep;
A1 from the shipped measurement record.)*

▶ **Under gcc the fix is PROFITABLE by 1.0–1.3 % (W1, whole program). Under
clang it is FREE, and its size is below the 7.00 Ir/call alignment step, so no
percentage may be quoted for it at all.** In A1 it is `0.000 %` everywhere, for
the structural reason in §8b.

⚠ **The prediction's MECHANISM was also wrong**, and that is the more useful
half: the branch is not "in a hot dispatch loop" — it is in the **error exit of
one handler**, which the benign corpus reaches only through the ONE-WORD form,
where `increment_opline` is 0 and the added test is one predictable compare.

ⓘ **`ph52` refuted the analogous prediction the same way** (item 76: the fix was
*profitable*, `−0.342 %`). ▶ **`n = 2` toward a real law, and the two rows'
mechanisms are different**, which is what makes the pair worth something.
⚠ It is `n = 2`, not a law. Two rows.

### 8c-2. ⭐⭐⭐ FAMILY B — the GATE'S OWN statistic — settles the clang column

`marginal_ir_per_call`, from `results-php/gate/ph55-opdata-stride.json`, is
family **B**: `(Ir at 200 iterations − Ir at 100 iterations) / 100`, a **slope**,
so the one-shot loader term cancels by construction. It is a **third,
independent statistic**, taken by the gate itself, in the gate's own
environment, by a different tool from either column above.

| pair | `O3/isolated` `small.bin` | `O3/isolated` `large.bin` | `O3/whole` `small.bin` | `O3/whole` `large.bin` |
|---|---|---|---|---|
| `c-gcc → c-gcc-h` | **`−20.07`** = `−1.061 %` | **`−66.14`** = `−1.300 %` | `−20.07` = `−1.061 %` | `−66.14` = `−1.299 %` |
| `c-clang → c-clang-h` | `+7.00` **or** `+0.00` | `+7.00` **or** `+0.00` | **`+0.00`** | **`+0.00`** |

⭐ **The gcc figure is corroborated to three significant figures** — `−1.061 %` /
`−1.300 %` here against W1's `−1.041 %` / `−1.290 %`, measured in a different
environment by a different tool. ▶ **The upstream fix really is profitable under
gcc, and §8c's refutation of §2.8 prediction 2 does not rest on one statistic.**

⛔⛔ **AND THE CLANG FIGURE IS THE ARTEFACT, SHOWN THREE WAYS AT ONCE:**

1. **`+7.00` Ir/call is EXACTLY the alignment step** `controls/argv_align.py`
   measures — 140 058 Ir over 20 000 calls is `7.0029`.
2. **It is IDENTICAL on two inputs whose work differs by 4×.** A real per-call
   cost scales with the work; a fixed per-call term does not. `+7.00` on both
   `small.bin` (16 instruction words) and `large.bin` (64) is the signature of
   the second, not the first.
3. **The same two binaries, the same statistic, and `whole` instead of
   `isolated` gives `+0.00` on both inputs.** Nothing about the *fix* changed
   between those two build modes; what changed is where the frames landed.
4. ⭐⭐⭐ **AND THE CELL MOVED UNDER A RE-RUN, WHICH IS THE DIRECT FORM OF 1–3.**
   An earlier draft of this table printed `+7.00` = `+0.402 %` / `+0.142 %` flat,
   from one gate record. A later gate run over **byte-identical binaries**
   (`md5_fn` unchanged, every `kernel_exclusive_ir` unchanged) recorded
   **`+0.00` on both inputs at `O3/isolated`.** ▶ So the cell takes BOTH values
   this section predicts it can, with nothing whatever changed between the two
   readings but the run — and the column is published above as the observed
   SET, not as a number. ⚠ **A point value here was never measurable**, and this
   is the row finding that out about its own table rather than being told.

▶ **Family B on this row is reporting where two binaries' frames landed, not
what the fix costs.** ⚠⚠ **And that is the sharpest form of
`.memory-php/03-numbers.md`'s own warning** — *"measure a mechanism; never
difference two records taken in two shells and call the result its cost"* —
because here the two records were taken by the SAME tool in the SAME run, and
the difference is still an artefact. **A slope cancels a FIXED term; it does not
cancel a PER-CALL one.**

### 8d. THE CROSS-LANGUAGE COLUMN — W1, and **both C columns**

`O3/isolated`, W1 Ir/call, against **R1h** (the arm that carries the fix, which
is what R2–R5 implement). Positive = the Rust rung is **dearer**.
⚠ **`c-clang-h`'s own level is bimodal** (1752.194 or 1759.194 Ir/call,
depending on stack alignment — §8b-2), so every figure against it is a **range**
and its sign is what the row relies on.

| `small.bin` | vs `c-gcc-h` = 1880.374 | vs `c-clang-h` = 1752.194 … 1759.194 |
|---|---|---|
| `safe_naive` 2017.645 | **`+7.30 %`** | **`+14.69 … +15.15 %`** |
| `safe_tuned` 1763.005 | **`−6.24 %`** | **`+0.22 … +0.62 %`** |
| `unsafe` 1644.393 | **`−12.55 %`** | **`−6.53 … −6.15 %`** |
| `verus` 1645.520 | **`−12.49 %`** | **`−6.46 … −6.09 %`** |

| `large.bin` | vs `c-gcc-h` = 5036.190 | vs `c-clang-h` = 4938.823 … 4945.824 |
|---|---|---|
| `safe_naive` 6222.592 | **`+23.56 %`** | **`+25.82 … +25.99 %`** |
| `safe_tuned` 5309.602 | **`+5.43 %`** | **`+7.36 … +7.51 %`** |
| `unsafe` 4802.012 | **`−4.65 %`** | **`−2.91 … −2.77 %`** |
| `verus` 4806.536 | **`−4.56 %`** | **`−2.82 … −2.68 %`** |

*(Medians over `controls/argv_align.py`'s sweep — eight path lengths on
`small.bin`, six on `large.bin`. ⚠ The medians move by ≤ 0.002 Ir/call between
sweeps of different lengths, which is the alignment wobble of §8b-2 and not
noise in the measurement; a LEVEL is never quotable on this row and a difference
is quotable only when `controls/argv_align.py` says it survives.)*

⛔⛔ **ONE CELL CHANGES SIGN BETWEEN THE TWO C COLUMNS, AND IT IS THE SAFE ONE.**
`safe_tuned` on `small.bin` is **6.24 % FASTER than `c-gcc-h`** and **slower
than `c-clang-h` on every one of the eight sweep points** (`+0.22 … +0.62 %`).
That is F108's class, live on this row: *"one C column is not a number with
error bars — it is a different sign."* ⭐ **A row that had published only the gcc
column would have published *"safe Rust beats C"*.** ✅ The flip is
**SIGN-STABLE** across the whole alignment sweep — `controls/argv_align.py`
checks exactly that, and would fail if it stopped being true.

⚠ **And the A1 column disagrees in sign with W1 on the unsafe rungs.** A1,
`small.bin`, against `c-gcc-h` = 1553.348: `unsafe` 1576.703 is **`+1.50 %`**
where W1 says **`−12.55 %`**. Against `c-clang-h` = 1340.587 it is
**`+17.61 %`**. ▶ **That is §8b's blindness showing up in the cross-language
column too, and it is why this row publishes W1 there.** Both are printed by
`controls/statistic.py`; neither is hidden.

ⓘ **No allocator caveat applies to this row's cross-language column.**
`PROTOCOL_PHP.md` §B1a puts one on `ph64` because it allocates `2n+2` blocks per
call. ph55 allocates **nothing**: `EX(Ts)` is a `safe_emalloc` whose size is a
compile-time constant (`op_array->T`, `zend_execute.c:1352`) and this kernel
keeps it as a frame array. `provenance.uses_allocator` is `false`.

### 8e. THE SAME-LANGUAGE LADDER — A1, where `inside_share` is 96–99 %

| step | `small.bin` | `large.bin` |
|---|---|---|
| R2 → R3 (`safe_naive` → `safe_tuned`) | 1950.172 → 1695.310 = **`−13.07 %`** | 6154.522 → 5241.310 = **`−14.84 %`** |
| **`fixed-R4 bound`** R3 − R4 | 1695.310 → 1576.703 = **`+7.52 %`** | 5241.310 → 4733.725 = **`+10.72 %`** |
| R4 → R5 (the proof) | 1576.703 → 1577.830 = **`+0.071 %`** | 4733.725 → 4738.248 = **`+0.096 %`** |

⚠ **`fixed-R4 bound` is `R3ship − R4ship` with BOTH endpoints held by fiat**
(`.memory/02-bench-rules.md`): the shipped rungs were chosen by IDIOM, before
measurement, and that is what makes the difference a **bound** rather than an
interval. **Two labelled quantities, never three; no pair interval.** §11 is the
R3-side span from the respelling search.

⭐ **THE PROOF IS NOT FREE ON THIS ROW, AND THAT IS UNUSUAL.** `+0.071 %` /
`+0.096 %` is small but it is **not zero**, because R4 and R5 are **not the same
machine code** (§10). Every PAT row that pins `exact` reports the proof at zero
instructions; this one cannot.

### 8f. WHAT THE VERUS LIMITATION COSTS — the `Option<fn>` substitution, priced

`controls/fnptr_cost.py`, A1 and W1, `O3/isolated`, against `safe_naive.rs`
(same algorithm, **byte-identical answers on all seven inputs — asserted before
any number is quoted**). ⚠ **The control's own build, not `build.py`'s**, so the
LEVELS are not comparable with the tables above; only its two columns are
comparable with each other.

| `fn_pointer` against `tag_match` | A1 | W1 |
|---|---|---|
| `small.bin` | **`−13.50 %`** | **`+14.40 %`** |
| `large.bin` | **`−16.01 %`** | **`+12.41 %`** |

⭐⭐ **The two families disagree in SIGN**, for §8b's reason arising a second
time: a function pointer is exactly what stops a handler being inlined, so the
work leaves the `kernel` symbol without leaving the program. **§12 is the
reading**, and `controls/fnptr_cost.json` carries the levels.

### 8g. WHERE THE TIME GOES — the decomposition, not a single rate

`work_per_call` is the **window in bytes**, and the instruction count is
`stride / 8`. But a ph55 call does **five** things and only one of them scales
with the window in the way the name suggests:

1. zero a `[Op; 64]` op_array (1 024 B) and a 42-slot zval store — **fixed**,
   whatever the stride, and it is why `small.bin`'s A1 (1553) is not a quarter
   of `large.bin`'s (3774);
2. decode `nops` words — linear;
3. the emitter chain walk — linear in the number of **instructions**, not words;
4. the dispatch loop — linear in instructions **executed**, which is fewer than
   `nops` whenever a two-word instruction is present;
5. fold 42 slots + 4 temps — **fixed**.

▶ **So the marginal is not a dispatch rate.** Measured: `(3774.095 − 1553.348) /
(64 − 16) = 46.27` A1 Ir per additional instruction word on `c-gcc`, against a
fixed term of `1553.348 − 16 × 46.27 = 812.9` Ir/call. The fixed term is **52 %
of `small.bin`'s whole cost** and 22 % of `large.bin`'s. ⚠ Any figure quoted on
`small.bin` alone is half scenery; both inputs are published for that reason.

### 8h. THE gcc↔clang GAP ON IDENTICAL EXTRACTED C

| input | `c-gcc` | `c-clang` | clang vs gcc |
|---|---|---|---|
| `small.bin` | 1900.154 … 1900.158 | **1752.192 … 1759.195** | **`−7.79 … −7.42 %`** |
| `large.bin` | 5102.040 … 5102.043 | **4938.822 … 4945.826** | **`−3.20 … −3.06 %`** |

*(W1, `O3/isolated`, the full spread over `controls/argv_align.py`'s sweep.)*
⚠⚠ **A RANGE AND NOT A NUMBER, AND §8b-2 IS WHY.** Over the whole sweep
`c-gcc`'s total moves by **65 Ir** — `0.0033` Ir/call — while `c-clang`'s moves
by **140 065 Ir**, i.e. **`7.00` Ir/call, BIMODAL**, on both inputs. ⭐ An
earlier draft of this table quoted `−7.42 %` / `−3.06 %` flat, from one run, and
a re-measurement of the SAME byte-identical binaries gave `−7.79 %` / `−3.20 %`
— **this row's own finding biting its own prose, caught by its own control.**
The sign and the magnitude band survive; the third digit does not exist.
Inside `.memory-php/03-numbers.md`'s measured band of
`−1.86 %` to `−29.96 %` over eight rows. ⭐ The static counts show why: gcc emits
**460** instructions for `kernel` where clang emits **168** (2 194 B against
718 B) — gcc unrolls the decoder and the fold, clang does not.

---

## 9. What the sanitizers and Miri say

* Stage 7 (`c/kernel.c` under ASan+UBSan, per-input expectation): `fires` on
  `adversarial-nullcall.bin` and `clean` everywhere else, as `model.py` derives.
* Stage 7h (`c/kernel_hardened.c`, expected clean on **every** input,
  adversarial included): clean. That is what R1h *means* and it is not
  declarable away.
* Miri: **required and non-waivable twice over** — eight trusted items, and R4
  and R5 are not the same machine code (§10).

⚠ **The one thing no detector on this row sees is
`adversarial-opdatalive.bin`.** There is no memory error in it: the PC is on the
wrong word, the word has a handler, the handler runs, and the answer is wrong.
ASan, UBSan and Miri all have nothing to say. §6.

---

## 10. The proof, the trusted surface, and the twins

### 10a. What is proved

```
requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_OPS
ensures   r == ph55_fold(buf@, off as int, len as int)
```

`ph55_fold` composes six recursive spec functions — `decoded`, `emitted`,
`passed`, `step`, `run`, `fold_*` — so the postcondition is the **value**, over
the whole machine state, and not a memory-safety-only retreat. `model.py`'s
`ph55_run` re-derives it from a different decomposition (a pure transition on an
immutable tuple), and `model.py::selfcheck` drives the two against each other on
synthetic windows the corpus does not contain.

### 10b. ⭐⭐⭐ The obligation is about the PC, not about the table

```
ok_from(ops, n, p)  ≡  starting at p and striding by each instruction's own
                       width, every word the PC lands on is an INSTRUCTION word
                       -- never a ZEND_OP_DATA word -- and every stride stays
                       inside the op_array
```

It is the dispatch loop's invariant; it is what discharges `hunwrap`'s
`requires t.is_some()`; and **it is exactly the invariant
`zend_binary_assign_op_helper`'s error exit breaks.** ▶ **That is a better
statement than `handler != NULL`**, and §6 is the measurement that shows why:
`adversarial-opdatalive.bin` breaks `ok_from` and does **not** produce a NULL.

⭐ It is established by the **emitter**, not by the executor — `emit_from`, tail
recursion, postcondition = the definition's own unfolding.

### 10c. ⭐⭐ THE PROOF BUDGET — no `#[verifier::rlimit]`, and that is a measurement

`controls/rlimit_bisect.sh`, on this box:

| rlimit | plain | `--cfg slb_twin` |
|---|---|---|
| **1** | 53 verified / 0 errors | **60 verified / 1 ERROR** |
| **2** | 53 / 0 | **61 / 0** |
| 3, 4, 5, 10, 30 | 53 / 0 | 61 / 0 |

▶ **The whole proof — an interpreter, ten handlers, a value postcondition over
the entire machine state and eight verified twins — needs `2`, against Verus's
default of `10`.** The row ships **no attribute at all**; the default is 5× the
measured requirement.

⚠ **Compare `ph16`**, whose obligation is a single index bound with no loop in
it and which had to ship `#[verifier::rlimit(30)]` because its **twin build
FAILED at 8**. ⭐ **The reason is structural and it is this row's Verus finding:
every obligation here is ONE unfolding of a recursive definition whose shape the
exec code mirrors, so Z3 never searches.** A proof about a bigger program is not
a more expensive proof; a proof whose spec does not mirror its code is.

### 10d. ⚠⚠ R4 AND R5 ARE NOT THE SAME MACHINE CODE — the `exact` pin was refuted

Measured, `O3/isolated`, from the shipped record:

```
unsafe   876 insns   md5_fn 37f8a672831f6774   md5_fn_norel 87140a47b1370398
verus    872 insns   md5_fn 30602b986da0f05b   md5_fn_norel 9a0ed674d02a9bf0
```

`norel` does not rescue it, so it is not relocation bytes. The exec code is
character-identical apart from the `verus!` block, the spec/proof items and the
clauses; what differs is **register allocation and scheduling** — the same
instruction kinds in a different order, with an extra `lea (%rdi,%rdi,4)` on the
Verus side. R5 is **four instructions shorter** and costs **22 544 Ir more** on
`small.bin`.

⛔ **THE CAUSE IS NOT IDENTIFIED, AND THIS SECTION SAYS SO RATHER THAN INVENTING
ONE.** Three hypotheses were **not** distinguished: (i) the Verus driver passes
codegen flags `rustc` does not; (ii) linking `vstd` changes LLVM's inlining
thresholds for the crate; (iii) the extra (erased) items perturb LLVM's pass
ordering. Distinguishing them needs a flag-by-flag comparison of the two driver
invocations, which was not done. **It is in §13.**

⭐ **Consequence, and it is not a formality:** `.memory/02-bench-rules.md` makes
Miri **non-waivable** when R4 and R5 are not the same machine code.

### 10d-2. The trusted surface, and the trade that was NOT taken

**Eight** `#[verifier::external_body]` items with contracts, plus `load_input`
and `emit` — ten TCB items, and that is more than any row in either programme.
⚠ **Six of the eight are index accessors on FOUR different arrays**, and the
reason is a layout choice: this kernel keeps `zval.type` and `zval.value.lval`
in **parallel arrays** (`[u8; 42]` and `[u64; 42]`). A single `[Zv; 42]` of a
two-field record would have collapsed `kget`/`kset`/`vget`/`vset` into two
items and taken the trusted surface from eight to six. **It was not taken**, and
the reason is honest rather than principled: the parallel-array rungs were
already built, measured and verified when the count was noticed, and a relayout
would have re-opened the proof for a TCB reduction of two accessors whose
contracts are the least interesting in the file. ⚠ It is a real cost and it is
recorded here rather than defended. §13.

⚠ **`ts` is deliberately NOT unchecked.** `tmp_of` is `(op & 0x7FFF) % NT` with
`NT` a constant, so LLVM proves the bound itself and emits nothing; an `unsafe`
there would add a ninth trusted item and buy zero instructions.

### 10e. The four independent facts the unchecked classes rest on

An editor who deleted the 2004 patch would be removing the precondition of
**one** of these and not the others, which is why they are kept apart:

| class | rests on | comes from |
|---|---|---|
| `hunwrap(o.handler)` | `ok_from` | **the 2004 patch's own invariant** |
| `bget(win, ..)` | `off + len <= buf@.len()` | the driver's contract |
| `oget/oset(ops, ..)` | `nops <= MAX_OPS` | `c/main.c`'s `stride_w <= 512` |
| `kget/kset/vget/vset` | `all_slots(ts@)` | an invariant of the interpreter |

### 10f. ⭐ THE §2.6 PREDICTION: REGISTERED AND **UPHELD**

> *"`slb_twin_*` for an `Option<fn>` accessor is `t.unwrap()` — safe, same
> signature — so `n_twins ≥ 1`, NO hatch, NO blocked row, and a CLEAN stage
> 5c-twin."*

**Upheld, and by a wider margin than predicted.** `n_twins = 8`, every twin is a
safe body with the trusted item's signature character for character, the twin
configuration verifies at **61 / 0**, `twin_justifications` is **empty** and no
hatch is taken. ▶ **F97's narrowing survives this row**: the joint
unsatisfiability is a property of the ITEM (`MaybeUninit`), not of php rows, and
ph55 is the control that shows it.

⚠ The one trusted item that is **not** an index accessor —
`hunwrap: Option<u8> -> u8` — twins to `t.unwrap()` in one line, exactly as
predicted.

### 10g. SLB-TRUSTED-ARGUMENT — the per-item arguments the gate requires

For each item: **(a)** is the twin's body the right checked stand-in; **(b)** is
the `ensures` COMPLETE with respect to every unchecked operation the body
performs; **(c)** does each clause mean the same thing in the shipped
configuration as in the twin's.

#### SLB-TRUSTED-ARGUMENT verus.rs bget

**(a)** The unchecked operation is `*v.get_unchecked(i)` on a `&[u8]`; the twin
is `v[i]`, which is the same read with the bounds check Rust would have emitted.
There is no third thing `get_unchecked` does. **(b)** The body performs exactly
one memory operation and it is a read at `i`; the `ensures` `r == v@[i as int]`
names the value of that read and there is no post-state to constrain, because
`v` is a shared reference and the function returns by value. A body that also
read `i + 1` would still satisfy this contract — which is `TASK_009_REVIEW`'s
x4 — and the defence is Miri, which this row requires, plus the fact that the
body is three tokens long and is quoted verbatim beside the twin. **(c)**
`i < v@.len()` and `r == v@[i as int]` mention only the parameter, the slice
view and the return value; `slb_twin` is on the twin's own `#[cfg]` and nowhere
else, so no constant, type or spec function in either clause can differ between
the two configurations.

#### SLB-TRUSTED-ARGUMENT verus.rs oget

**(a)** `*a.get_unchecked(i)` on a `&[Op; MAX_OPS]` against the twin's `a[i]`:
the same read, checked. `Op` is `Copy`, so both return by value and neither can
alias. **(b)** One read, at `i`, returned; `r == a@[i as int]` is the whole of
it, and there is no post-state — `a` is shared. **(c)** The clauses name `i`,
`MAX_OPS` and `a@`; `MAX_OPS` is a `pub const usize` outside any `#[cfg]`, so it
is the same 64 in both configurations. ⚠ **The `requires` is `i < MAX_OPS` and
NOT `i < a@.len()`**, deliberately: the length is in the TYPE, so
`a@.len() == MAX_OPS` holds of every `a` this signature admits and a
length-shaped `requires` would be saying nothing. That is the difference from
`bget`, whose slice length is a run-time fact.

#### SLB-TRUSTED-ARGUMENT verus.rs oset

**(a)** `*a.get_unchecked_mut(i) = x` against the twin's `a[i] = x`: the same
store, checked. **(b)** ⭐ This is the completeness case that matters. The body
performs exactly one store, and the `ensures` names the **whole post-state** —
`final(a)@ == old(a)@.update(i as int, x)` — so a body that also clobbered
`a[i + 1]`, or stored something other than `x`, or stored at some other index,
could not satisfy its own postcondition. A weaker `ensures` naming only
`final(a)@[i] == x` would have admitted all three, and this row does not write
one. **(c)** `i`, `MAX_OPS`, `x`, `old(a)@`, `final(a)@` — none of them is
`#[cfg]`-dependent. ⚠ `x: Op` is a **pure value** and correctly has no
precondition: every inhabitant of `Op` is a legal store into a slot that
`[ZERO_OP; MAX_OPS]` already initialised, and the only parameter that can make
the operation undefined is `i`, which **is** constrained.

#### SLB-TRUSTED-ARGUMENT verus.rs kget

**(a)** `*a.get_unchecked(i)` on `&[u8; NSLOT]` against `a[i]`. **(b)** One
read, returned; `r == a@[i as int]` is complete for a shared reference.
**(c)** `i` and `NSLOT`, a `pub const usize = 42` outside any `#[cfg]`.
⚠ The bound is `i < NSLOT` rather than `i < a@.len()` for `oget`'s reason: the
length is in the type. ⚠⚠ **This item exists separately from `oget` because the
ARRAY is different**, and a reviewer checking that the bound matches the array is
checking two different pairs; folding them would be folding two claims into one.

#### SLB-TRUSTED-ARGUMENT verus.rs kset

**(a)** `*a.get_unchecked_mut(i) = x` on `&mut [u8; NSLOT]` against `a[i] = x`.
**(b)** One store; `final(a)@ == old(a)@.update(i as int, x)` names the whole
post-state, so a clobber of a neighbour or a store of the wrong value cannot
satisfy it. **(c)** `i`, `NSLOT`, `x`, and the two array views; nothing
`#[cfg]`-dependent. ⚠ `x: u8` is a pure value and needs no precondition, for
`oset`'s reason one type down.

#### SLB-TRUSTED-ARGUMENT verus.rs vget

**(a)** `*a.get_unchecked(i)` on `&[u64; NSLOT]` against `a[i]`. **(b)** One
read, returned; complete for a shared reference. **(c)** `i` and `NSLOT`, both
configuration-independent. ⚠ It is a separate item from `kget` because the
element type is different and the two bounds are checked against two different
arrays; §10d-2 records that a single `[Zv; NSLOT]` layout would have merged
them, and that the merge was not taken.

#### SLB-TRUSTED-ARGUMENT verus.rs vset

**(a)** `*a.get_unchecked_mut(i) = x` on `&mut [u64; NSLOT]` against
`a[i] = x`. **(b)** One store; the `ensures` is the whole post-state.
**(c)** `i`, `NSLOT`, `x`, the two views — none `#[cfg]`-dependent. ⚠ `x: u64`
is a pure value: every one of the 2^64 values is a legal store into a word
`[0u64; NSLOT]` already initialised, and the indexing parameter is the
constrained one.

#### SLB-TRUSTED-ARGUMENT verus.rs hunwrap

⭐⭐ **The row's own trusted item, and the only one of the eight whose
precondition is not arithmetic.**

**(a)** The unchecked operation is `t.unwrap_unchecked()`; the twin is
`t.unwrap()`, which is the same projection with the `None` test Rust would have
emitted — and the panic that test produces is **exactly** what §6 measures safe
Rust doing on `adversarial-nullcall.bin`. There is no better checked stand-in:
`unwrap` *is* the checked form of `unwrap_unchecked`, by definition in `core`.
**(b)** The body performs one operation on a by-value `Option<u8>`: it projects
the payload. There is no memory to touch, no post-state, and no second parameter
— so `r == t.unwrap()` is complete in the strongest sense available, because the
function's entire observable effect is its return value and the `ensures` names
it exactly. ⚠ The shape this stage exists to catch — an unconstrained parameter
that the body indexes with — **cannot arise here**: the only thing that can make
`unwrap_unchecked` undefined is `t` itself, and `t` is what the `requires`
constrains. **(c)** `t.is_some()` and `r == t.unwrap()` mention one parameter
and the return value; `Option<u8>` is a `core` type, `slb_twin` appears only on
the twin's `#[cfg]`, and there is nothing in either clause a configuration could
change.

⚠⚠ **What makes this entry worth reading is WHERE the precondition comes from.**
Not from arithmetic, and not from the caller's convenience: from `ok_from`, the
dispatch loop's invariant, established by the emitter pass, and **the exact
invariant `4f68f3774c34` restores**. `controls/negatives.py --emit nofixup`
deletes the emitter pass and that mutant must FAIL to verify — which is the only
mechanical evidence that this `requires` is load-bearing rather than decorative.

---

## 11. ⭐⭐⭐ THE IN-CONTRACT RESPELLING SEARCH — §2.8 PREDICTION 1, **REFUTED IN BOTH HALVES**

`controls/spellings.py --verus`. ⭐ **Search first, predict second**: `ph45` and
`ph52` both reversed their ordering under search, and so does this row. **`n = 3`.**

> **The prediction** (`TASK_PHP_048` §2.8): *"The R3 endpoint is DEGENERATE and
> the R4 endpoint MOVES — the opposite of `ph52`. Reason: there is no
> bounds-check term to respell away (the PC walk is the whole kernel), while
> `unwrap()` → `unwrap_unchecked()` is a single named lever."*

**Both halves are wrong, and the signs are exactly swapped.**

A1, against each side's shipped rung, `O3/isolated`. ⚠ **This is the control's
own build** (`rustc -C opt-level=3 --cfg slb_isolated`), so the LEVELS are not
comparable with §8; the columns are comparable with each other. A difference
below 0.5 % is reported as a **TIE**, not a win.

| variant | what it changes | `small.bin` | `large.bin` | admissible? |
|---|---|---|---|---|
| **R3 shipped** | — | `0.00 %` | `0.00 %` | — |
| ⭐ `r3_nobind` | **lever 1 REVERTED** — re-index `ops[pc]` per field | **`−1.82 %`** | **`−2.76 %`** | in contract |
| `r3_noodbind` | lever 2 reverted — re-index `ops[pc+1]` | `0.00 %` **TIE** | `0.00 %` **TIE** | in contract |
| `r3_noslice` | lever 3 reverted — eight index expressions in the decoder | `+15.96 %` | `+18.39 %` | in contract |
| **R4 shipped** | 8 trusted accessors | `0.00 %` | `0.00 %` | — |
| ⭐ `r4_safe_slots` | the four zval-store accessors checked; **surface 8 → 4** | `+0.35 %` **TIE** | `+0.84 %` | ✅ 57 verified / 0 errors |
| ⭐⭐ `r4_safe_hunwrap` | **only** the handler `unwrap` checked; surface 8 → 7 | `+2.20 %` | `+3.67 %` | ✅ 54 / 0 |
| `r4_safe_ops` | the op_array accessors checked; surface 8 → 6 | `+3.02 %` | `+4.48 %` | ✅ 55 / 0 |
| `r4_safe_all` | **zero** unchecked operations — R3 with a proof | `+22.67 %` | `+28.07 %` | ⛔ not a rung: an R4 with no `unsafe` is an R3 |

### 11a. ⛔ THE R3 ENDPOINT IS NOT DEGENERATE — and the lever that moves it is a PESSIMISATION

`r3_nobind` is **cheaper than the shipped R3** by `−1.82 %` / `−2.76 %` (**A1**),
and it is **in contract on every backticked spelling**. ⚠ **The W1 column of
`controls/spellings.py` is NOT quoted here**: its binaries are not swept, and
§8b-2 measured that an unswept W1 level on this row carries a 7.00 Ir/call
alignment term — which is the same order as some of the differences in that
table. **A1 is stable across rebuilds on every variant** (checked: every A1
figure in the table above is byte-identical across two independent
regenerations), so A1 is what the search publishes. So the shipped R3 is **not** the cheapest in-contract R3 found.

⚠⚠ **AND WHAT IT REVERTS IS `safe_tuned.rs`'s OWN HEADLINE LEVER.** That file
calls lever 1 — `let o: Op = ops[pc];` once per dispatch — *"⭐ the lever that is
about the row"*, on the reasoning that a dispatch loop reads its current
instruction four or five times so a re-index per field is a per-field bounds
check in the hottest loop. **The reasoning about the bounds checks is right and
the conclusion is wrong**: LLVM already proves `pc < MAX_OPS` from the loop
invariant, so the re-index costs no check — and binding a **16-byte `Op` by
value** costs a copy the per-field reads do not. ▶ *"Fewer bounds checks"* and
*"cheaper"* came apart, measured.

⛔ **The rung is NOT re-shipped.** `.memory/02-bench-rules.md` holds the shipped
rungs fixed by fiat — chosen by IDIOM, before measurement — and that fiat is what
makes `R3ship − R4ship` a **bound**. §13 carries the debt: `safe_tuned.rs`'s
comment is a framing this measurement has undercut, and repairing it costs a
full re-measure for a paragraph. **Declared, not repaired** (F98's shape,
recognised instead of repeated).

⭐ **And the decomposition is the useful half**: of `safe_tuned.rs`'s three
levers, **lever 3 does all the work** (`+15.96 %` / `+18.39 %` to revert),
**lever 2 does nothing at all** (a TIE on both inputs, in both families), and
**lever 1 costs 1.8–2.8 %**. Reporting `R2 → R3` as one number (§8e's
`−13.07 %` / `−14.84 %`) would have hidden all three facts.

### 11b. ⛔ THE R4 ENDPOINT DOES NOT MOVE EITHER — every reduction costs

**No cheaper admissible R4 was found.** All four variants are dearer, from
`+0.35 %` to `+28.07 %`. ▶ **On this row, reducing the trusted surface is never
free**, which is the opposite of `ph53`'s `r4_bitmask_min` (cheaper *and*
smaller).

⭐ **The two numbers worth carrying out of that:**

* **`r4_safe_slots` HALVES the trusted surface — eight accessors to four — for
  `+0.35 %` (a TIE on `small.bin`) / `+0.84 %`**, and its Verus analogue
  verifies at 57 / 0. That is the cheapest safety-for-TCB trade in the row and
  it is a real option a reader can take.
* ⭐⭐ **`r4_safe_hunwrap` PRICES THIS ROW'S OWN `unsafe`**: making **only** the
  handler `unwrap` checked, and leaving every index unchecked, costs
  **`+2.20 %` / `+3.67 %`**. ▶ So *"what does `unwrap_unchecked` on the dispatch
  target buy?"* has an answer on this row, and it is **2.2–3.7 % of the kernel**
  — against a panic on exactly one input in the whole corpus (§6).

ⓘ **An internal cross-check that fell out of the search**: `r4_safe_all` and
`r3_noslice` measure **identically** — `1794.310` and `5916.310` A1, to the
digit. They are reached by different substitution paths from different base
files, and they coincide because `unsafe.rs` never had lever 3: with every
accessor made safe it *is* `safe_tuned.rs` without the slice bind. Two paths,
one program, same number.

### 11c. What ships

**Two labelled quantities, never three, and NO PAIR INTERVAL** —
`min(R3 found) − min(R4 found)` differences two upper bounds and bounds nothing.

```
fixed-R4 bound   R3ship - R4ship   +7.52 % (small) / +10.72 % (large), A1,
                                   both endpoints held by fiat (§8e)
R3-side span     cheapest-found to dearest-found, in contract:
                 r3_nobind  -1.82 %  ...  r3_noslice +15.96 %   (small)
                 r3_nobind  -2.76 %  ...  r3_noslice +18.39 %   (large)
R4-side span     among RUNG CANDIDATES only:
                 R4ship  0.00 %  ...  r4_safe_ops +3.02 % / +4.48 %
```

⚠ **R4 searched is not R4 exhausted.** Seven variants are what was tried, and
the search is a *decomposition* of the two shipped rungs rather than a hunt for
a cheaper one. Every number here is about `rustc 1.97.1` / `LLVM 22.1.6` on this
box.

## 12. ⭐⭐ WHAT THE VERUS LIMITATION COSTS — and the two families disagree in SIGN

`controls/fnptr_dispatch.rs` restores C's representation — `Option<fn(&mut Ex)
-> bool>`, one handler function each, a real indirect call — into
`safe_naive.rs`'s algorithm. `controls/fnptr_cost.py` asserts it produces
**byte-identical checksums on all seven shipped inputs** before quoting any
number: a variant that has drifted is not measuring the substitution, and the
assertion includes the two adversarial inputs, because the claim the whole
comparison rests on is that `Option<fn>` and `Option<u8>` are `None` for exactly
the same opcode.

| `fn_pointer` against `tag_match` | A1 Ir/call | W1 Ir/call |
|---|---|---|
| `small.bin` | 1766.172 → 1527.692 = **`−13.50 %`** | 1890.860 → 2163.053 = **`+14.40 %`** |
| `large.bin` | 5778.522 → 4853.264 = **`−16.01 %`** | 5903.809 → 6636.285 = **`+12.41 %`** |

⚠⚠ **THESE ARE THE CONTROL'S OWN BUILD** (`rustc -C opt-level=3 --cfg
slb_isolated`), **not `harness/build.py`'s**, so the LEVELS are not comparable
with §8's table. Only the two columns here are comparable with each other, and
they are built with identical flags.

✅ **AND UNLIKE §8h's, THIS PAIR IS STABLE**, which was checked rather than
assumed after §8b-2 made it a live question: two independent regenerations of
this control, on either side of a full rebuild, give A1 identical to the
milli-instruction and W1 to `±0.004` Ir/call — `+14.40 %` / `+12.41 %` both
times. Neither of these two binaries straddles the alignment boundary that makes
`c-clang`'s level bimodal.

⭐⭐⭐ **AND THE TWO FAMILIES DISAGREE IN SIGN, FOR THE ROW'S OWN REASON.** A1
makes the function-pointer table look **13–16 % cheaper** and W1 makes it
**12–14 % dearer** — because **a function pointer is exactly what stops a
handler being inlined**: the work leaves the `kernel` symbol without leaving the
program. ▶ That is §8b's blindness arising a **second** time, independently, and
from the very construct this row is about. Two demonstrations, one mechanism.

⚠ **It is a pair difference of TWO things and not one**, and the control says so
in its own output: a function pointer has ONE signature, so every handler must
take the same argument, which forces the machine state into a `struct Ex` where
the rungs keep plain locals. **Representation + frame**, never a clean
one-variable cost.

▶ **So the honest statement of what the Verus limitation costs is: the
substitution Verus forces is worth `+12.4 … +14.4 %` whole-program on this row's
own two probe shapes, in the direction that FAVOURS the shipped rungs** — the
tag dispatch the rungs are obliged to use is the cheaper of the two — **and it
changes no answer at all.**

## 13. ⭐ WHAT I AM UNSURE OF

`TASK_PHP_041` reported 15 uncertainties and found its own citation defect; that
is the standard. `UNTESTED` and *"I could not tell"* are valued answers.

1. **Why R4 and R5 differ at O3 (§10d).** Three hypotheses, none eliminated. The
   difference is real (876 vs 872 instructions, `norel` also differs) and the
   *cause* is UNTESTED.
2. **Whether `4f68f3774c34` is the FIRST commit to close this site.** No
   tag-by-tag bisect was done. The row confirms the site and the direction.
3. **Whether `ph55_emit_fixup` is the *cheapest* stand-in for the compiler's
   guarantee.** It is O(instructions) per call in every rung. A one-shot pass
   outside the measured loop is impossible with the pinned kernel signature; a
   *cheaper* in-kernel formulation was not searched for.
4. **The trusted surface is EIGHT and could have been six** (§10d-2). The
   `[Zv; NSLOT]` relayout was not built, so the claim that it would cost nothing
   is UNTESTED.
5. **`inside_share` was measured at `O3/isolated` only.** Whether the C cells'
   74–83 % holds at `whole` was not measured; `whole` cells have no `kernel`
   symbol at all in four of the eight, so A1 is undefined there.
6. **The A1-blindness of §8b is demonstrated, not bounded.** How much of *other*
   rows' A1 figures sit in the same trap is not something this row can say.
7. **`unsafe.rs` + the bug prints `11370550710093900800` on the NULL case**
   (§6). That is UB and the value is a fact about this build of LLVM, not about
   Rust. It was not re-checked under a different opt-level or compiler.
8. **Whether `-Wstringop-overflow` would have fired on any OTHER expression**
   without the `nops >= 2` guard. Two warnings were measured and removed; no
   sweep was done for others.
9. **The opcode set is ten.** Whether a larger set would change the
   `inside_share` picture (more handlers = more uninlinable symbols in C) is a
   plausible and unmeasured confound in §8a.
10. **`work_per_call` is the window in bytes** and the executor visits FEWER
    instructions than `nops` whenever a two-word form is present. The
    over-estimate raises the derived floor, which is the safe direction, but the
    exact executed-instruction count per call was not tabulated per input.
11. **W1 was measured with three repeats per cell and `spread = 0.000`.**
    That is within-build stability; **across-build** stability was not measured
    and item 99's ±14–28 Ir band may still apply to a regenerated sidecar.
12. **The `ZEND_ASSIGN_OBJ` arm is deleted** (`provenance.divergences`). The
    claim that it "carries no part of the defect" rests on reading `:1719`; it
    was not built and measured.
13. **`preimage_screen.py`'s `CANDIDATE` is reported, not used.** Whether the
    screen *could* be made to decide this row (a longer citation, more matchable
    lines) was not explored.
14. **The C `whole` cells have no `kernel` symbol for clang and for every Rust
    rung**, so four of the eight `O3/whole` cells report `kernel_exclusive_ir:
    None`. Every figure in §8 is therefore `isolated`. Whether the `whole`
    ordering differs was read off `main_exclusive_ir` only, and that column
    includes the driver loop.
15. **Whether a reader of `README.md` can reconstruct the mechanism without
    `NOTES.md`.** Untested; there is no reader but me.
16. ⚠⚠ **A DECLARED DEBT: `safe_tuned.rs`'s header calls lever 1 *"the lever
    that is about the row"* and §11a measures it a PESSIMISATION** (`−1.82 %` /
    `−2.76 %` to revert). The comment claims a mechanism, not a number, and the
    mechanism is true — but the framing is one this row's own search has
    undercut. Repairing it costs a **full re-measure** for a paragraph, so it is
    declared here instead. `PROTOCOL_PHP.md` §F6a's shape, recognised rather
    than repeated.
17. **Why binding a 16-byte `Op` by value is dearer than four field reads is
    INFERRED, not measured.** §11a attributes it to the copy; no disassembly
    diff of the two variants was taken.
18. **The `r4_safe_*` variants' Verus analogues verify, but their MIRI status
    is untested.** They are controls, not rungs, so no Miri run was made; a
    reader promoting one to a rung owes that.
19. **`controls/statistic.py` and `controls/spellings.py` build with different
    flags from `harness/build.py`**, so three sets of LEVELS appear in this
    file (§8, §11, §12) and only within-set comparisons are meaningful. Each
    table says so; whether a reader will carry the caveat is untested.
20. ⭐ **The `git apply --check` / gitignore trap (§5) may affect OTHER rows.**
    It was found here; no sweep of the programme's other controls was done.
21. ⚠ **A number that was ESTIMATED and is now COUNTED, and the repair is
    partial.** The row's prose said the `= NULL` sits *"in the middle of a
    200-line block of real assignments"*. Counted on the pristine tarball
    afterwards: `zend_init_opcodes_handlers()` is `:4276-4443` — **168 lines,
    130 `zend_opcode_handlers[...]` assignments, exactly ONE `= NULL`.** The
    load-bearing half (*the only one*) was always true. ✅ `spec.md` (four
    places, inside the **hashed** contract), `NOTES.md` and `README.md` now
    carry the counted figures, because a loose number frozen into
    `contract_sha256` is the class `PROTOCOL_PHP.md` §F6a treats as
    unrepairable. ⛔ **`c/kernel.c`'s and `c/kernel_hardened.c`'s copies still
    say "200-line block"**, and they stay: they are in the MEASUREMENT digest,
    so repairing an adjective costs a 32-cell re-measure. Declared, not
    repaired, and the C comment is an approximation rather than a falsehood.
