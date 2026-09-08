# ph03-uudecode-bound

**A loop bound computed from a length byte inside the data.**
`php_uudecode`, PHP 5.0.0, `ext/standard/uuencode.c:126-171`, lifted verbatim.
Corpus row CRASH-115 (merged with V5C-116). The first real row of the PHP
programme (`TASK_PHP_013`), reviewed at `TASK_PHP_014` and corrected and
re-measured at `TASK_PHP_015`.

```c
131  p = *dest = emalloc(ceil(src_len * 0.75) + 1);
133  e = src + src_len;                                  /* the TRUE end ... */
135  while (s < e) {                                     /* ... read only here */
136      if ((len = PHP_UU_DEC(*s++)) <= 0) break;       /* len is ATTACKER DATA */
141      ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
143      while (s < ee) {
144          *p++ = PHP_UU_DEC(*s) << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
```

A line whose length byte claims 45 with fewer than 60 characters behind it makes
`ee > e`. The inner loop then reads past the source **and** writes past the
allocation.

## Read these, in this order

| | |
|---|---|
| `spec.md` | the kernel contract and the machine-readable pins the gate enforces |
| `NOTES.md` | the measurements, the findings, and what is *not* here |
| `c/kernel.c` | R1 — PHP 5.0.0 verbatim. The bug. |
| `c/kernel_hardened.c` | R1h — the real upstream fix `f95c1df58349` (2004), **and why it is incomplete** |
| `safe_naive.rs` | R2 — and its header explains why R2–R5 are *not* ports of R1h |
| `verus.rs` | R5 — 25 verified / 0 errors; the proof's refusal of the 2004 fix is the row's headline |
| `controls/` | the runs that must FAIL, and the two upstream patches, kept so the citations survive with no network |

## Three things a reader should not get wrong

1. ⚠ **The five rungs do not implement the same fix.** R1 has no checks, R1h has
   the 2004 upstream fix, and R2–R5 have that *plus* PHP's own 2014 fix
   `1e2818b14376` — because the 2004 one is incomplete and a memory-safe rung
   cannot stop there. `NOTES.md` §5.
2. ⚠ **Which limb a sanitizer reports is decided by the source buffer, not by
   the defect.** `inputs/adversarial-read.bin` and `adversarial-write.bin`
   differ by 60 bytes of slack and by nothing else, and give a READ at
   `uuencode.c:144` and a WRITE at `:146` respectively. `NOTES.md` §4.
3. ⚠ **The floating point is the mechanism.** `(int) floor(len * 1.33)` stays
   in R1/R1h; the Rust rungs use the exhaustively-equal integer form because
   Verus has no `f64`. And `harness/build.py` links no `-lm`, which is why the
   C rungs substitute `floor`/`ceil` by macro. `NOTES.md` §9.
4. ⚠⚠ **Of the 2004 fix's two guards, one is DEAD.** Hunk 1 (`len > src_len`)
   fires 1 953 times over 12 600 documents and hunk 2 (`ee > e`) would have
   refused every one of them; deleting hunk 1 from `verus.rs` still gives
   `25 verified, 0 errors`. So the patch that missed the real bug for ten years
   also shipped a check that never decided anything. `NOTES.md` §5e.
5. ⚠⚠ **The benign fixture used to be a monoculture, and it hid a real defect
   in `model.py` for a task.** Every line declared 45, so the corpus never took
   `:141`'s `floor()` arm and `45 ≡ 0 (mod 3)` was the one case in which a line
   emits as many bytes as it declares. `inputs/gen.py` now emits a short final
   line and **asserts** that the corpus reaches both arms, and
   `model.py::selfcheck` drives its two implementations over 896 windows it
   builds itself. `NOTES.md` §13 — **this is the part a builder of the next row
   should read first.**

## Running it

Everything goes through the php driver, never `harness/check.py` directly
(`PROTOCOL_PHP.md` §E):

```sh
python3 patterns-php/ph03-uudecode-bound/inputs/gen.py      # the .bin are gitignored
python3 harness-php/gate.py --tool build   ph03-uudecode-bound --all
python3 harness-php/gate.py --tool measure ph03-uudecode-bound
python3 harness-php/gate.py --tool report  ph03-uudecode-bound
python3 harness-php/gate.py                ph03-uudecode-bound   # FAILS on tables, once
python3 harness-php/gate.py --tool report  ph03-uudecode-bound
python3 harness-php/gate.py                ph03-uudecode-bound   # green
```

The hand-run evidence that the gate cannot hold:

```sh
gcc -std=c99 -Wall -Wextra -O1 -g -fsanitize=address,undefined -fstrict-aliasing \
    -static-libasan -static-libubsan \
    patterns-php/ph03-uudecode-bound/controls/fix_incomplete.c -o .temp/php13/fixctl
env -u LD_PRELOAD .temp/php13/fixctl control     # must fire
env -u LD_PRELOAD .temp/php13/fixctl fixed       # fires -- the 2004 fix is incomplete

python3 patterns-php/ph03-uudecode-bound/controls/negatives.py --list
python3 patterns-php/ph03-uudecode-bound/controls/negatives.py --emit no2014 \
    > patterns-php/ph03-uudecode-bound/verus_no2014_tmp.rs
python3 verus_run.py .temp/php-root/patterns/ph03-uudecode-bound/verus_no2014_tmp.rs
rm patterns-php/ph03-uudecode-bound/verus_no2014_tmp.rs
```

⚠ **`--list` prints each mutant's expectation and one of the three is
`MUST VERIFY`** (`no2004a`, `no2004a_both`): they delete the *dead* half of the
2004 fix, so `25 verified, 0 errors` is the result that proves the point.
`.temp/php15/19-run-negatives.sh` runs all three against their declared
expectations in one pass and cleans up in a `trap`.

⚠ Delete the emitted mutant afterwards: a stray `.rs` in the row directory is a
source no record pins.
