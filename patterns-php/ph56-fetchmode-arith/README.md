# ph56 — opcode selected by arithmetic, guard replicated on some arms only

**PHP 5.0.0, `Zend/zend_compile.c:736-780`, corpus row CRASH-041, CWE-476.**
Mechanism family **T5** — *the emitted program is not the one the executor
implements* — and this row is T5's **second** member, beside `ph55`.

> ## ⛔⛔⛔ THIS ROW IS **INCOMPLETE**. READ `NOTES.md` §10 BEFORE TOUCHING IT.
> **Five of six rungs are built, validated and cross-agreeing. `verus.rs` (R5)
> does not exist, `spec.md` does not exist, and the row HAS NOT BEEN GATED.**
> `NOTES.md` §10 is the exact stopping point and the exact next steps.
> Everything that IS here has been differentially tested and is described below.

---

## The mechanism, in six lines

PHP lays its eighteen fetch opcodes out as **six groups of three at stride 3**
and says so in a comment (`zend_compile.h:636-638`, exclamation mark upstream's):

> *the following 18 opcodes are 6 groups of 3 opcodes each, and must remain in
> that order!*

`zend_do_end_variable_parse` therefore picks a variable's **access mode** by
arithmetic on the opcode value — and **replicates the append-dim guard onto the
arms by hand**:

| arm | delta | guard at 5.0.0 | the PHP | what 5.0.0 does |
|---|---:|---|---|---|
| `BP_VAR_R` | `-= 3` | ✅ `:753-755` | `$x = $a[];` | `Fatal error: Cannot use [] for reading` |
| `BP_VAR_W` | `0` | — | `$a[] = 1;` | ✅ **legal — this is what `[]` is FOR** |
| `BP_VAR_RW` | `+= 3` | — | `$a[] += 1;` | ✅ works, exit 0, appends `int(1)` |
| `BP_VAR_IS` | `+= 6` | ⛔ **none** | `isset($a[]);` | ⛔ **SEGV** |
| `BP_VAR_FUNC_ARG` | `+= 9` | ⚠ **none** | `f($a[]);` | ⚠ runs, exit 0, **silently appends** |
| `BP_VAR_UNSET` | `+= 12` | ✅ `:771-773` | `unset($a[]);` | `Fatal error: Cannot use [] for unsetting` |

Every cell of that table is **measured**, on a pristine-sourced PHP 5.0.0 CLI,
by `controls/census.py`, which re-runs it on every invocation.

---

## Why it crashes, and it is not where `:763` alone would put it

`isset($a[])` does **not** reach the executor as `ZEND_FETCH_DIM_IS`.
`zend_do_isset_or_isempty` calls `zend_do_end_variable_parse(BP_VAR_IS, 0)` and
then, four lines later, **rewrites the last opline again** — `case
ZEND_FETCH_DIM_IS: last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;`
(`zend_compile.c:3229`).

So the emitted opcode is `ZEND_ISSET_ISEMPTY_DIM_OBJ` (115) carrying an
`IS_UNUSED` op2, and **that** handler reads op2 with no test:

```c
zval *offset = get_zval_ptr(&opline->op2, ...);   /* :3961 -- returns NULL */
...
switch (offset->type) {                           /* :3973 -- DEREFERENCES IT */
```

`get_zval_ptr`'s `case IS_UNUSED:` is an explicit `return NULL;` (`:118-121`).
`offsetof(zval, type)` is **20**, and pristine PHP 5.0.0 faults at exactly
`SEGV on unknown address 0x000000000014`. ⭐ **So does `c/kernel.c`** — the
kernel keeps upstream's field order on purpose, and a C99 compile-time assertion
(`PH56_LAYOUT_ASSERT`) fails the build if that offset ever moves.

**The second harm needs one more bracket pair.** `:3223` rewrites only the
**last** opline, so in `isset($a[][0])` the `[]` opline survives as
`ZEND_FETCH_DIM_IS`, reaches `zend_fetch_dimension_address`'s append arm
(`:935-943`) and **grows the array**. Exit 0, a plausible answer, no diagnostic
from anything. `count($a)` goes 3 → 4 on the real interpreter.

---

## What is here

```
c/kernel.c              R1   PHP 5.0.0 narrowed. THE BUG.
c/kernel_hardened.c     R1h  + 1e708a5aeb30's three lines (2004-08-29)
c/kernel.h  c/main.c         the shared declaration and the driver
safe_naive.rs           R2   `[..]` indexing, `.unwrap()` on the operand
safe_tuned.rs           R3   three bounds checks removed, still zero `unsafe`
unsafe.rs               R4   ten trusted accessors; the tenth is `zunwrap`
                             — `Option::unwrap_unchecked` on the OPERAND, which
                             is the check whose absence is CRASH-041
verus.rs                R5   ⛔ NOT WRITTEN — see NOTES.md §10
model.py                     THREE independent implementations + a 156-window
                             synthetic sweep
inputs/gen.py                the corpus, with its reachability ASSERTIONS
controls/r1h_backport.py     re-runs `git apply`; reproduces the gitignore trap
controls/census.py           the six-arm census, re-derived three ways
```

## Reproducing

```sh
python3 patterns-php/ph56-fetchmode-arith/inputs/gen.py
python3 patterns-php/ph56-fetchmode-arith/controls/census.py
python3 patterns-php/ph56-fetchmode-arith/controls/census.py --selftest
python3 patterns-php/ph56-fetchmode-arith/controls/r1h_backport.py
python3 patterns-php/ph56-fetchmode-arith/controls/r1h_backport.py --selftest
```

⛔ **Do NOT run `harness-php/gate.py` on this row yet** — it has no `spec.md`,
so the gate cannot read a contract and `provenance.py` has nothing to validate.
The preflight is green with the row present (measured); the gate is not.

`NOTES.md` is the measurement record and the argument. `../CATALOGUE.md` has the
row's catalogue entry — ⚠ **whose `⚠ risk` note is WRONG in both halves**, and
`NOTES.md` §1 is the correction.
