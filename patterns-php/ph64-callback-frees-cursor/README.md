# ph64 — `zend_llist_apply`: a cursor the callback is allowed to free

**PHP 5.0.0 · `Zend/zend_llist.c:186-193` · corpus row CRASH-086 · CWE-416 ·
tier `narrowed`**

```
for (element=l->head; element; element=element->next)   /* :190  SITE L */
	func(element->data);                                /* :191 */
```

`func` here is `user_tick_function_call`, which runs **userland PHP** — and
userland PHP can call `unregister_tick_function()` on itself. That reaches
`zend_llist_del_element` → `DEL_LLIST_ELEMENT` → `pefree(current)`, which frees
the element the `for` header is about to read.

**Two dereferences, and the corpus cites the other one.** Control returns first
to `basic_functions.c:2135` — `tick_fe->calling = 0` — which *writes* into the
freed block (SITE C, `index.csv`'s `c_file_line`, and the first fault ASan
reports on plain `malloc`/`free`); only then to the `for` header, which *reads*
`element->next` out of it and follows it (SITE L, this row's `c_lines`).

## What to read, in this order

| | |
|---|---|
| `spec.md` | the contract the gate enforces, and the thirteen cited spans |
| `NOTES.md` | the measurements, the fidelity table, the ladder and the open item |
| `c/kernel.c` | R1 — PHP 5.0.0, narrowed. THE BUG |
| `c/kernel_hardened.c` | R1h — `562f886ecb14` and nothing else |
| `controls/` | six controls, every one with declared must-fire **and** must-NOT-fire cases |

## The three things a reader should not have to dig for

⭐ **The same file has the defence fifteen lines above.**
`zend_llist_apply_with_del` (`:171-183`) takes the same caller-supplied `func`
and caches `next = element->next` at `:177` *before* calling it. Three of
`zend_llist.c`'s six callback walks cache the successor and three advance in the
`for` header — and the three that do not are exactly the three this defect can
reach. `controls/next_cache.py` prices that counterfactual against the fix
upstream actually shipped, and finds they are **not ordered by strength**.

⚠⚠ **The obvious oracle measures nothing.** A freed
`sizeof(zend_llist_element) + sizeof(user_tick_function_entry) - 1` = 39-byte
block has `REAL_SIZE` 40 and cache index 5, so it is **not returned to
`malloc`** — its payload survives, `element->next` still reads the true
successor, and *the visit fold is bit-identical between R1 and R1h*
(`controls/oracle.py`, 213 of 213 windows). That is what
`crashes_pristine_5_0_0 = False` is. The row's `u64` therefore also carries
`l->count`, the dtor count, the refusal count and the allocator tally.

⚠⚠ **Safe Rust does not turn this into a panic.** `next` is a raw pointer, and
the faithful safe port is an index arena — where a dangling link is an ordinary
in-bounds read of a slot that is still there, which is to the byte what PHP's
size-class cache does with the real block. So R2 reproduces the defect as a
**wrong answer**, and what removes it is `562f886ecb14`'s *logical* invariant.
`verus.rs` proves that invariant's memory-safety half — and it holds with the
guard deleted. `NOTES.md` §9.

## Regenerating

```sh
python3 patterns-php/ph64-callback-frees-cursor/inputs/gen.py     # the .bin files
python3 harness-php/gate.py ph64-callback-frees-cursor            # the gate
python3 patterns-php/ph64-callback-frees-cursor/controls/oracle.py
python3 patterns-php/ph64-callback-frees-cursor/controls/differential.py
python3 patterns-php/ph64-callback-frees-cursor/controls/next_cache.py
python3 patterns-php/ph64-callback-frees-cursor/controls/predicate.py
python3 patterns-php/ph64-callback-frees-cursor/controls/bug41037.py
```
