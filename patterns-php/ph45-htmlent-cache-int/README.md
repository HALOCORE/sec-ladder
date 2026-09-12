# ph45 — `int cache`: a heap pointer in a field too narrow to hold it

**PHP 5.0.0 · `ext/mbstring/libmbfl/mbfl/mbfl_convert.h:49` with
`ext/mbstring/libmbfl/filters/mbfilter_htmlent.c:161 :169 :178 :183 :249` ·
corpus row CRASH-123 / V5C-123 · bug #30573 · CWE-787 · tier `narrowed`**

```c
int cache;                                              /* mbfl_convert.h:49 */

filter->cache = (int)mbfl_malloc(html_enc_buffer_size+1);   /* :161  STORE  */
char *buffer  = (char*)filter->cache;                       /* :178  BACK   */
buffer[0] = '&';                                            /* :183  WRITE  */
buffer = (char*)filter->cache;                              /* :249  BACK   */
mbfl_free((void*)filter->cache);                            /* :169  FREE   */
```

A 64-bit heap pointer goes into a 32-bit field, comes back out through
`(char*)` — which **sign-extends** — and is then dereferenced ten times and
freed. It is the **only one of the corpus's 166 cases with its own invariant**,
`pointer-value-integrity`, and its three obligations map one-to-one onto three
of those lines.

## What to read, in this order

| | |
|---|---|
| **`c/arena.h`** | ⚠ **read this first.** Why the row places its work buffer, and why that is needed to make the **benign** case work |
| `spec.md` | the contract the gate enforces, the twelve cited spans and the fifteen itemised divergences |
| `NOTES.md` | the measurements, the ladder, the vacuity mutants and the two adjacent defects found and not pursued |
| `c/kernel.c` | R1 — PHP 5.0.0, narrowed. THE BUG |
| `c/kernel_hardened.c` | R1h — `e8901dc17087` and nothing else; `diff` the two |
| `controls/` | six controls, every one with declared must-fire **and** must-NOT-fire cases |

## The five things a reader should not have to dig for

⚠⚠ **The defect is not input-conditioned, and that inverts the usual design.**
`:167`'s `if (filter->cache)` rejects only the value zero, so `:169`'s free runs
on **every** filter destruction whatever the input — 60 SIGSEGVs in 60 runs on
`"hello, world"`, which contains no `&` at all (`controls/native.py`, and
`TASK_PHP_034_REPORT` §5.4 before it). **So the placed arena exists to make the
BENIGN case work, not the adversarial one.** Without it there is no benign
corpus and the row cannot be measured at all.

⚠⚠ **On the measured placement R1 and R1h are bit-identical.** `LO` is
`MAP_32BIT`, so `(char*)(int)p == p` exactly — which is 2004's non-PIE `brk`
heap, and is precisely why this shipped and was filed as *a compiler warning*.
The published `u64` therefore carries **no evidence that the defect exists**;
that is `check.py` stage 7h being satisfied, and it is `ph64`'s lesson arriving
on a second row. The evidence is in `inputs/adversarial-*.bin` and
`controls/oracle.py`.

⭐⭐ **The oracle is a silent wrong answer, not a crash.** Two filters whose work
buffers are exactly 2³² apart are **one buffer** under truncation: filter A
decodes `&amp;` to **65** — the character `A` — where the fix gives **38**,
because filter B's `&#65;` overwrote A's buffer index 1 with `#` and `:190`'s
`buffer[1]=='#'` then chose the *numeric* arm of a *named* entity. No crash, no
sanitizer diagnostic, no allocator damage. `controls/oracle.py` runs it beside
the must-**not**-fire control that carries the same bytes at the same
placement-0.

⚠⚠ **`kernel_exclusive_ir` sees one tenth of this row.** The filter body is a
separate symbol in every rung — the C reaches it through a function pointer —
and 44 % of the C's instructions are in glibc's `strcmp`, which lands in no
column of the published table at all. The row's headline `fixed-R4 bound`
therefore **disagrees on sign** between the two families: `+0.37 %` in A1 and
`−3.06 %` whole-program. Both are published, labelled, and `NOTES.md` §8 carries
the mechanism.

⭐⭐ **The ladder result contradicts the brief this row was built from.**
`TASK_PHP_034_REPORT` §6.8 says *"safe Rust cannot store a pointer in an `i32`
at all"*. **Measured false**: `(&x[0] as *const u8) as i32` is ordinary safe
Rust, it truncates, and it compiles with **zero diagnostics even under
`-D warnings`** — where the same C emits **four**. What safe Rust refuses is the
*dereference*. So all four Rust rungs carry **R1's own idiom**, not R1h's, and
are safe anyway — because the value they store is an index into an arena the
program owns. And Verus is a third answer again: it **refuses** the round trip
without `idx < 2³¹`, naming both cast sites. **gcc warns, rustc is silent, Verus
refuses.** `NOTES.md` §10.

## Regenerating

```sh
python3 patterns-php/ph45-htmlent-cache-int/inputs/gen.py          # the .bin files
python3 harness-php/gate.py ph45-htmlent-cache-int                 # the gate
python3 patterns-php/ph45-htmlent-cache-int/controls/oracle.py
python3 patterns-php/ph45-htmlent-cache-int/controls/warnings.py
python3 patterns-php/ph45-htmlent-cache-int/controls/native.py
python3 patterns-php/ph45-htmlent-cache-int/controls/vacuity.py
python3 patterns-php/ph45-htmlent-cache-int/controls/entity_table.py --selftest
python3 ./verus_run.py patterns-php/ph45-htmlent-cache-int/controls/o1_roundtrip.rs
python3 ./verus_run.py patterns-php/ph45-htmlent-cache-int/controls/o1_roundtrip_nopre.rs
```
