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
| **R1** `c/kernel.c` | `mbfilter.c:1179-1259` narrowed to the `mblen_table` arm. **The bug.** Shipped byte-identical at **nine** release tags, php-5.0.0 → php-5.3.2. |
| **R1h** `c/kernel_hardened.c` | ⚠ **the guard configuration upstream CONVERGED on** — `php-5.2.12 … php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body sha256 `26e2099e33433c74` — **and it is in the CALLER**, `ext/mbstring/mbstring.c`, not in `mbfl_strcut`. That is `cb3cca21b345` (2005-12-15) hunk **(a)**, after `c2471b495009` (2009-09-23) removed hunk (b) as **bug #49354**. |
| **R2–R5** | the same function as R1h, in Rust. That configuration is COMPLETE, so unlike `ph03` no rung has to carry a second one. |

⚠⚠ **The row shipped BOTH hunks until `TASK_PHP_018`, and the gate had already
said why it should not.** Hunk (b) removes **none** of the 15 333 out-of-bounds
reads and changes the answer on **13.5 %** of benign calls; `check.py` stage 7h
refused it, and the row worked around the refusal by restricting the corpus.
**Upstream reached the same verdict from a bug report, four years later.**
`NOTES.md` §00 is the whole story; `controls/bug49354.py` is upstream's own test.

## The ladder, in numbers — ⚠ read `NOTES.md` §12 before quoting one

```
fixed-R4 bound              R3ship - R4ship          +11.98 %
cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %   (`r3_reslice`)
R4 side, searched                                     DEGENERATE -- no cheaper
                                                      admissible R4 was found
```

**Neither number is "the cost of safe Rust".** `controls/spellings.py` — the
first in `patterns-php/` — searches both endpoints and publishes both, labelled.

## Where to look

| | |
|---|---|
| the contract, hashed | `spec.md` |
| **why R1h is a tag range and not a commit** | `spec.md` `idiom.required[4]`, `NOTES.md` §00 |
| the findings and every number | `NOTES.md` |
| the three implementations + the sweep | `model.py` |
| the fixture and its must-fire assertions | `inputs/gen.py` |
| what each upstream guard actually buys | `controls/fix_scope.py` |
| ⭐ **upstream's own regression test, all three configurations** | `controls/bug49354.py` |
| ⭐ **the in-contract spelling span, both sides** | `controls/spellings.py` |
| the Rust clamps against the C's, both configurations | `controls/guard_equiv.py` |
| the Verus mutants | `controls/negatives.py` |
| the 2005 fix, its 2009 half-removal, the 2010 restoration | `controls/*.patch` |

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
