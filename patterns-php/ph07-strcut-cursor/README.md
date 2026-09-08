# ph07-strcut-cursor — `mbfl_strcut`, the cursor loop with no end test

**PHP 5.0.0 · `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259` · corpus row
CRASH-124 · CWE-125 · tier `narrowed` · echoes `p16`**

`mb_strcut($s, strlen($s) + 1, 1)` reads past the end of a PHP string.

```c
/* mbfilter.c:1202-1210 -- the start walk */
for (;;) {
    m = mbtab[*p];        /* per-byte length, from a 256-entry static table */
    n += m;
    p += m;
    if (n > from) {       /* the ONLY exit */
        break;
    }
    start = n;
}
```

`from` is the caller's untrusted offset and `p` is never compared against
`string->val + string->len`. `:1179` *does* read `len = string->len` — but only
for the clamps at `:1227-1241`, which run **after** the walk.

⭐ **And `:1213` guards the second walk**: `if (k >= (int)string->len)` means
`:1217-1222` only ever runs while `n <= k < string->len`. One function, adjacent
lines, one bounded search and one unbounded one. **That asymmetry is the row.**

---

## The ladder

| rung | what it is |
|---|---|
| **R1** `c/kernel.c` | `mbfilter.c:1179-1259` narrowed to the `mblen_table` arm. **The bug.** Shipped byte-identical in php-5.0.0, 5.1.0, 5.2.17, 5.3.0, 5.3.1 and 5.3.2. |
| **R1h** `c/kernel_hardened.c` | ⚠ **`cb3cca21b345` (2005-12-15), and it is in the CALLER** — `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, not in `mbfl_strcut`. |
| **R2–R5** | the same function as R1h, in Rust. The 2005 fix is COMPLETE, so unlike `ph03` no rung has to carry a second one. |

## Where to look

| | |
|---|---|
| the contract, hashed | `spec.md` |
| the findings and every number | `NOTES.md` |
| the two implementations + the sweep | `model.py` |
| the fixture and its must-fire assertions | `inputs/gen.py` |
| what each upstream guard actually buys | `controls/fix_scope.py` |
| the Rust clamps against the C's | `controls/guard_equiv.py` |
| the Verus mutants | `controls/negatives.py` |
| the fix, and the 2010 second restoration | `controls/*.patch` |

## Running it

```sh
python3 harness-php/gate.py --tool build   ph07-strcut-cursor --all
python3 harness-php/gate.py --tool measure ph07-strcut-cursor
python3 harness-php/gate.py --tool report  ph07-strcut-cursor
python3 harness-php/gate.py                ph07-strcut-cursor      # FAILS on tables
python3 harness-php/gate.py --tool report  ph07-strcut-cursor
python3 harness-php/gate.py                ph07-strcut-cursor      # green
```

⚠ **Never run `harness/check.py` on a php row directly** — everything goes
through `harness-php/gate.py`, which builds the shim, verifies the digest
bridge and checks provenance first (`PROTOCOL_PHP.md` §E).

`inputs/*.bin` is gitignored; `python3 inputs/gen.py` regenerates it
byte-for-byte from the committed seed.
