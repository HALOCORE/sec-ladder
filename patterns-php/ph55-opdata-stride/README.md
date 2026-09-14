# ph55 — an early exit strides 1 over a two-word instruction

**PHP 5.0.0 · `Zend/zend_execute.c:1724-1796` · corpus row CRASH-023 · CWE-476**

> `zend_binary_assign_op_helper` computes its own instruction's **width** at run
> time and then leaves by one of two exits. The normal exit consults the width.
> The error exit, 23 lines earlier, does not.

---

## The mechanism, in nine facts

Every one is a line in the pinned 5.0.0 tarball, and `spec.md` pins all six spans.

```
1  a compound assignment to an array dimension is TWO WORDS
       zend_op *op_data = opline+1;                              :1742
2  the handler records that in a LOCAL FLAG, at run time
       zend_bool increment_opline = 0;   :1728   ... = 1;        :1749
3  the ERROR exit does not consult it
       if (*var_ptr == EG(error_zval_ptr)) { ...; NEXT_OPCODE(); }
                                                            :1765-1770
4  the NORMAL exit does
       if (increment_opline) { INC_OPCODE(); } NEXT_OPCODE();
                                                            :1792-1795
5  NEXT_OPCODE() = EX(opline)++; return 0;   -- stride 1 AND a return
   INC_OPCODE()  = if (!EG(exception)) { EX(opline)++; }  -- no return
                                                   :1317-1320, :1326-1330
6  ZEND_API opcode_handler_t zend_opcode_handlers[512];          :1338
7  zend_opcode_handlers[ZEND_OP_DATA] = NULL;                    :4427
       the ONLY `= NULL` among the 130 assignments in
       zend_init_opcodes_handlers() (:4276-4443, 168 lines)
8  pass_two copies the table into EVERY instruction
       opline->handler = zend_opcode_handlers[opline->opcode];
                                                  zend_opcode.c:363
9  the executor dispatches through that field with NO NULL CHECK
       while (1) { ... if (EX(opline)->handler(...)) { return; } }
                                                            :1383-1394
```

▶ **error arm → PC strides 1 → the PC lands on the trailing `ZEND_OP_DATA` word
→ that word's `handler` is NULL → unconditional indirect call through NULL.**

The trigger is two lines of PHP:

```php
$x = 1;
$x[0] += 1;     // $x is not an array, so the dimension fetch yields error_zval
```

### The sentence worth remembering

`INC_OPCODE()` has **four** call sites in 5.0.0. **Three are unconditional**,
because those handlers are *statically* two-word — and two of the three carry a
shouting comment in the original:

```c
/* assign_obj has two opcodes! */     :2192
/* assign_dim has two opcodes! */     :2223
```

`zend_binary_assign_op_helper` is the **only** one whose width is
**data-dependent**. That is why it needs a flag, and it is the one with the bug.

> **The codebase shouts the invariant at the two sites that get it right, and is
> silent at the site where the invariant became conditional.**

Both siblings were read and both are clean. The kernel **lifts one of them**
(`PH55_ASSIGN_DIM`), so the contrast is in the measured program.

---

## The fix is three lines

`4f68f3774c34` (Stanislav Malyshev, 2004-08-30, *"fix crash #29893"*) — one
file, **three insertions, zero deletions**, and they are **the normal exit's own
three lines copied onto the error exit**. Nothing is invented.

⚠ It is a **hand backport**: the commit is against 2004-08-30 HEAD and `git
apply` refuses it on 5.0.0. `controls/r1h_backport.py` runs the refusal, ships
`controls/4f68f3774c34-backport-5.0.0.patch` as the positive control, and
re-derives the three legs that identify *which* exit the hunk belongs to.

---

## What the row prices, and it is sharper than *"safe Rust catches it"*

The defect is a **control-flow** error — a wrong PC. The NULL call is only how
it **manifests**. So there are two adversarial inputs, **one byte apart**:

| | `adversarial-nullcall.bin` | `adversarial-opdatalive.bin` |
|---|---|---|
| what the wrong PC lands on | a word with **no handler** | a word that **has** one |
| C (`c/kernel.c`) | ⛔ **SIGSEGV** | a **wrong answer**, exit 0 |
| safe Rust + the same bug | ⛔ **panic** | **the same wrong answer, bit for bit** |
| unsafe Rust + the same bug | a **third** wrong answer — UB, no crash | the same wrong answer |
| every shipped rung (R1h, R2–R5) | correct | correct |

> ⭐ **The `Option` catches the NULL. It does not catch the wrong PC.** And no
> sanitizer, and not Miri, sees the second column at all.

`controls/stride_bug.py` produces that table and refuses to print a claim its
own measurement stopped supporting. `NOTES.md` §6.

---

## The Rust side has a finding that is not about this defect

**Verus does not support function pointer types** — which is this row's own
dispatch mechanism. So all four Rust rungs carry an `Option<u8>` handler ID and
a `match` instead of `Option<fn>` and an indirect call.
`controls/fnptr.rs` is the probe (it **must fail**),
`controls/fnptr_dispatch.rs` is the substitution undone, and
`controls/fnptr_cost.py` prices it. `NOTES.md` §7, §12.

---

## ⚠ Two things the row's own search then measured about its own rungs

* **`safe_tuned.rs`'s headline lever is a pessimisation.** Reverting lever 1 —
  the `let o: Op = ops[pc];` bind the file calls *"the lever that is about the
  row"* — is **1.8–2.8 % CHEAPER**. LLVM already proves `pc < MAX_OPS`, so the
  re-index costs no check, while binding a 16-byte `Op` by value costs a copy.
  *"Fewer bounds checks"* and *"cheaper"* came apart. Of the three levers, only
  **lever 3** does any work; **lever 2 does nothing at all**.
* **Halving the trusted surface costs 0.35–0.84 %.** `r4_safe_slots` takes the
  eight trusted accessors to four and still verifies (57/0). And making *only*
  the handler `unwrap` checked — this row's own `unsafe` — costs **2.2–3.7 %**.

⛔ Neither rung is re-shipped: the shipped rungs are fixed by fiat, chosen by
idiom before measurement, and that fiat is what makes `R3 − R4` a bound.
`NOTES.md` §11.

---

## The proof

```
requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_OPS
ensures   r == ph55_fold(buf@, off as int, len as int)
```

and the obligation the row is about is **`ok_from`** — *starting at `p` and
striding by each instruction's own width, every word the PC lands on is an
instruction word and never a data word.* ⭐ That is a statement about **the PC**,
not about the table, and it is exactly the invariant the error exit breaks.

⭐⭐ The whole proof — an interpreter, ten handlers, a value postcondition over
the entire machine state and **eight verified twins** — needs
`#[verifier::rlimit]` **2**, against Verus's default of 10, so the row ships no
attribute at all. `NOTES.md` §10.

---

## Layout

```
c/kernel.c            R1   PHP 5.0.0, narrowed control flow. THE BUG.
c/kernel_hardened.c   R1h  the same file + 4f68f3774c34's three lines
c/main.c                   the driver; the three stride_w guards are structural
safe_naive.rs         R2   the mechanical port
safe_tuned.rs         R3   three levers ⚠ and NOTES.md §11a measures one of
                           them a PESSIMISATION -- see below
unsafe.rs             R4   get_unchecked + unwrap_unchecked, 8 trusted items
verus.rs              R5   the same exec code + ok_from + the value postcondition
model.py                   three independent implementations + a synthetic sweep
inputs/gen.py              the corpus, with its arm-coverage assertions
spec.md                    the machine-readable contract the gate enforces
NOTES.md                   the measurements, the adjudications, and §13: what I
                           am unsure of
controls/                  SEVEN controls, each with its must-fire negatives
                           INSIDE it feeding `problems` (63 selftest arms in
                           total), plus `_pin.py` (the staleness pin they all
                           carry), `rlimit_bisect.sh`, the Verus probe
                           `fnptr.rs`, the `Option<fn>` variant
                           `fnptr_dispatch.rs` and the two patches
```

Run `python3 harness-php/gate.py ph55-opdata-stride` before believing anything.
