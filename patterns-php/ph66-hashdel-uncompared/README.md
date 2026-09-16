# ph66 — a numeric bucket's key is never compared

**PHP 5.0.0, `Zend/zend_hash.c:464-465`, corpus row LOGIC-001.**
`zend_hash_del_key_or_index` settles a bucket's key **kind** with a disjunct:

```c
464  if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
465      ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength))))) {
```

A numeric bucket carries `nKeyLength == 0` (upstream says so at `:387`), so for
a numeric bucket the left arm fires and `memcmp` is never reached. Hash equality
alone stands in for key identity, and on a real PHP 5.0.0 CLI:

```php
$a = array();
$a['abc']     = 'ABC';
$a[6385036779] = 'NUM';     // == zend_inline_hash_func("abc", 4)
unset($a['abc']);
// count=1, and the survivor is 'abc'.
```

**The key you named survives. The key you never named dies. PHP exits 0.**

---

## ⭐⭐⭐ Why this row is here

Every other row in this programme exhibits its defect as a **signal** — a
segfault, an ASan report, an address. **This one exhibits it as a wrong answer.**
`rc=0` on every cell, on every input; the observable is the surviving-key list.

That single difference propagates all the way up the ladder, and the table is
the row's result:

| instrument | what it sees | measured by |
|---|---|---|
| a CLI reproducer | ✅ **the wrong VALUE** | `.tasks-php/probes/ph66_key_identity.sh` |
| ASan + UBSan | ⛔ nothing | gate stages 7 and 7h |
| Miri | ⛔ nothing | gate stage 6 |
| safe Rust (R2, R3) | ⛔ nothing — **it reproduces the defect exactly** | `controls/ladder.py` |
| `unsafe` Rust (R4) | ⛔ nothing — same | `controls/ladder.py` |
| Verus (R5), shipped | ⛔ nothing — **49 verified, 0 errors, with the defect in place** | `verus.rs` |
| ⭐ Verus, asked the RIGHT question | ✅ **refuses it** | `controls/key_identity.py` |

**R1 = R2 = R3 = R4 = R5 on all eight inputs, adversarial included. Only
`c/kernel_hardened.c` moves.** `CLAUDE.md` Don't 6 is what makes that
publishable: *"safe Rust reproduces the bug bit-identically"* is a **finding**,
never a kill — and it is the first defect in this corpus that the whole safety
stack is blind to.

⚠ The last row of the table is the sharp one. Verus is not *the rung that
catches the bug*; it is **the rung that can be asked**. Which obligation gets
written is a human act, and `NOTES.md` §6 quotes the corpus's own labeller
deciding that the filed invariant (`I7`, refcounts) is the wrong one.

---

## The trigger needs no preimage

`CATALOGUE.md` said *"the DJBX33A preimage the fixture needs was never computed;
compute it before building."* ⛔ **That names the wrong direction, and the one it
names is infeasible.** DJBX33A accumulates in a `ulong` — 64-bit on LP64 — and
every `33^k` is odd, hence a unit mod 2^64, so no byte position owns a bit range
and there is nothing to lift.

⭐ **No preimage is needed.** `_zend_hash_index_update_or_next_insert` stores
`p->h = h` with `h` the **raw user-chosen index**, so running the hash
**forwards** on any string key gives the integer index that key will destroy.
One line, no search. `.tasks-php/probes/ph66_djbx33a_collide.py`.

---

## The files

| | |
|---|---|
| `spec.md` | the hashed contract — tier, provenance, divergence ledger, the pinned idiom, the Verus item table |
| `NOTES.md` | **the measurements, and the arguments that are not in the contract** |
| `c/kernel.c` | R1 — `Zend/zend_hash.c` lifted `verbatim`. THE BUG |
| `c/kernel_hardened.c` | R1h — the same file with `b73349dbe4e9` applied `-p1`, rc 0, no backport |
| `safe_naive.rs` / `safe_tuned.rs` / `unsafe.rs` / `verus.rs` | R2 / R3 / R4 / R5 — **all four implement R1's function**, and `safe_naive.rs`'s header says why |
| `model.py` | three independent reference implementations, driven against each other over a domain `inputs/` does not span |
| `inputs/gen.py` | the corpus generator, which **refuses** a measured corpus that reaches the defect |
| `controls/ladder.py` | ⭐ the six-cell × eight-input table above, measured |
| `controls/key_identity.py` | ⭐ the key-identity obligation in Verus, three arms |
| `controls/r1h_apply.py` | the R1h binding re-derived from the tarball bytes |
| `controls/differential.py` | the shipped C against all three model spellings, 94 off-corpus windows, five must-fire mutations |
| `controls/inside_share.py` | `inside_share` per cell, both C columns, **both optimisation levels** |
| `controls/spellings.py` | does every backticked span in `spec.md` actually pin? |

Run the gate with `python3 harness-php/gate.py ph66-hashdel-uncompared`.
Rebuild the inputs with `python3 patterns-php/ph66-hashdel-uncompared/inputs/gen.py`.

---

## ⚠ What this row cannot show

On this kernel's domain **`memcmp` never decides anything**: every site that
compares key bytes has already required equal hash *and* equal length, and the
64 keys have pairwise distinct 64-bit hashes. Making the byte comparison
discriminate would need a DJBX33A collision — the same object the catalogue
asked for and which is not constructible. **The same fact that makes this row
cheap to trigger makes that one arm of it unreachable.** `NOTES.md` §8.
