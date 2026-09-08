# ph07-strcut-cursor — notes

`spec.md` is the contract, `README.md` is the entry point, this file is the
evidence. Everything here was run; the logs are named per claim.

---

## §0 `PROTOCOL.md` rule 6 — the `contract_sha256` disclosure

```
13bb0b70d031be7354077ee852e80f3dced307729fee71eb5b418e43816176a0   AS FIRST WRITTEN
```

Recorded **before any cell was built through `harness/build.py`**, which is the
only evidence rule 6 can have on a row that lands in one commit. ⚠ Rule 6's
`git show HEAD:` command is **vacuous on a new pattern** — it compares the
working tree to HEAD and prints nothing on a clean tree — and this line says so
rather than citing a check that cannot fire.

⚠ **Two things happened before that hash and neither is hidden.** (1) An
earlier draft of the contract hashed to `09b46bfecaab118d0ade88f876f8f2c1…`; it
pinned `` `n > frm` `` as the Rust spelling of the start walk's exit test, which
**appears in no Rust rung** because the rungs use the rotated `while n <= frm`
form. Caught by grepping the pins against the sources before the first gate
run, corrected to `` `while n <= frm` ``, and the row was never built or gated
at the old hash. (2) The cells under `.temp/php16/tb/` were built by hand with
`gcc`/`rustc` during development, outside `harness/build.py`; they measure
nothing and are deleted.

**The hash MOVED ONCE, after the measurement and before the first gate run:**

```
be5f5818ffa625c72af87eea036735219de01b8d61e05ce3b8271805d241359c   AS SHIPPED
```

⚠ **One edit inside the fence, and it is the `identity` entry.** `spec.md`
cannot pin `identity.O3` before the measurement exists — the honest level is
`norel`, not `exact`, and I could not know that until the record showed
`md5_fn` differing while `md5_fn_norel` and both instruction counts matched.
The `why` is written from the record, and `spec.md` is **not** in
`measure.py::measurement_sources`, so no re-measure was owed and none was
taken.

⚠ **Any later move is disclosed here with its reason**, per rule 6.

Also per rule 6's addendum: the hashed `idiom.why` and every rung-source doc
comment were re-read against the measured numbers in §8 before this row was
finished, not only against what they said when written.

---

## §1 The row

**`mbfl_strcut`'s `mblen_table` arm, `mbfilter.c:1179-1259`, narrowed.** The
extraction is line-for-line identical to the tarball except for what
`spec.md`'s `provenance.divergences` itemises: the encoding lookup, the two
WCS arms, the filter-chain `else` arm, two struct fields, the allocator
substitution, and the Rust rungs' `usize` spelling of the caller's clamps.

`harness-php/provenance.py ph07-strcut-cursor`:

```
OK  ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259  1489 bytes
    sha256 5edc6c04b7ff5f64  tier=narrowed
kernel overlap 75% (39/52 excerpt lines in kernel.c, kernel.h, kernel_hardened.c)
    tier=narrowed is expected to clear 25% -- REPORTED, NOT ENFORCED
1 preprocessor condition this heuristic cannot evaluate: ['#ifndef PH07_KERNEL_H']
1 row(s) checked, 0 FAILED
```

### §1a ⚠ `PROTOCOL_PHP.md` §F item 9 asks what I think of that number

**75 % is higher than I expected for a `narrowed` row and the 13 missing lines
are exactly the declared ones**: the `mbfl_no2encoding` call and its NULL test,
the twelve lines of the two WCS arms, and the `} else if (encoding->mblen_table
!= NULL) {` line itself. Nothing is missing that I did not itemise.

⚠ **And the number is not evidence that the cited lines are compiled.**
`provenance.py` reads `c/kernel*.{c,h}` and never `main.c`, the driver loop or
the build; it says so itself on every run. **What ties the cited lines to the
benchmark on this row is the ASan backtrace** (§4b): `ph07_strcut` appears at
`kernel.c:171` with `kernel` above it and `main.c:59` above that. That is the
evidence a reviewer should want; the overlap is a spelling check.

⚠ **The first `narrowed` row is where `TASK_PHP_008` §2's demotion stops being
free**, exactly as `PROTOCOL_PHP.md` §F item 9 predicted for the first
`verbatim` one. My reading: for a `narrowed` row the number is *less*
informative than for a `verbatim` one, because narrowing is defined as removing
lines — so a low score is expected and a high one only says the removals were
small. **The load-bearing artefact is the divergence ledger, and nothing checks
it.**

---

## §2 Reachability — `PROTOCOL_PHP.md` §A3, settled before any rung existed

`.temp/php16/02-reach.log`, an **offset** interpreter of the extracted walk (it
never holds a pointer, so it records an access it does not perform), over
133 932 `(string, from, length)` calls spanning six lead-byte families ×
`slen ∈ {0,1,2,3,5,8,13,21,34,48}` × every `from`/`length` in
`[-slen-2, slen+8]`:

```
calls interpreted                          : 133932
  of which the wrapper left `from` >= slen : 18444

  R1   reads past val[slen] :  15333   first: ('ascii/0', from=1, length=0)
  R1h  reads past val[slen] :      0
```

**The smallest instance is the EMPTY string with `from = 1`** — a one-byte
allocation holding only the terminator. It ships as
`inputs/adversarial-empty.bin`.

⚠ **"Past `val[slen]`", not "past `val[slen-1]`", and the distinction is the
model of a PHP string.** `string->val` is `emalloc(len + 1)` with
`val[len] == '\0'`; index `len` is the terminator and is **inside** the
allocation. Both upstream guards admit `from == string->len` for exactly that
reason (§4). A kernel handed a source without a terminator would make the fix
look wrong by one byte, so `inputs/gen.py` writes it into every window and
`c/kernel.h` says why.

---

## §3 ⭐ The `mblen_table` lifts as static data — `TASK_PHP_016` §5.2 answered

The manager's second doubt was *"that the `mblen_table` can be lifted as static
data without becoming a `modelled` row — if reproducing it faithfully means
dragging in the encoding registry, the tier is wrong."*

**It does not, and the tier is right.** The evidence, in four parts:

1. **It is 256 bytes of `static const` in PHP too.** `mbfilter_utf8.c:39-56`,
   `static const unsigned char mblen_table_utf8[]`, reached as
   `encoding->mblen_table` — a field of a `const mbfl_encoding`
   (`mbfilter_utf8.c:58-65`). *Nothing* about it is dynamic. `c/kernel.c`'s copy
   is **byte-identical to the tarball's 16 lines**, diffed
   (`.temp/php16` table diff, `TABLE IDENTICAL (16 lines)`).
2. **The registry is what `narrowed` removes, and removing it is sound because
   the flag is a compile-time constant.** UTF-8's record is
   `{mbfl_no_encoding_utf8, "UTF-8", "UTF-8", aliases, mblen_table_utf8,
   MBFL_ENCTYPE_MBCS}`. `MBFL_ENCTYPE_MBCS` is neither `SBCS` nor any `WCS`
   bit, so the two WCS arms at `:1182-1193` are dead and the `else` arm at
   `:1260+` is unreachable. That is one checkable fact, it is in the tarball,
   and it is written into all three ledger entries rather than assumed.
3. ⭐ **It costs the PROOF one lemma, not a tier.** `verus.rs::lemma_mbtab_matches`
   proves `MBTAB@[b] == mbtab_of(b)` for **all 256 `b`** mechanically —
   `by (compute_only)` over a recursive conjunction plus one induction, ph03's
   `emit_ok_upto` recipe applied to static data — with **no `assume`, no
   `external_body`, and no sixth trusted item**. `controls/negatives.py --emit
   notable` changes ONE table entry and the proof fails.
4. **It must NOT be in the blob.** An attacker who could choose the table could
   put a zero in it, and the start walk would then spin for ever — a defect PHP
   does not have. `model.py::selfcheck` check 4 asserts every entry is ≥ 1 and
   check 5 re-parses the 256 numbers out of `c/kernel.c` and compares.

⚠ **The one place it cost something is `provenance.c_lines`, which pins a
single span.** The table is a second span in a second file, and `extract_sha256`
does not cover it. That is `TASK_PHP_015` §2.5's deferred schema decision
arriving on a second row, and this row does not fix it either — it declares the
span in the ledger and pins the bytes three other ways (the diff, check 5, and
the Verus lemma).

---

## §4 ⚠⚠ The fix commit — and it is in the CALLER, in another file

### 4a. What was found, and how

`TASK_PHP_016` §2 sent me to look for the commit that introduced 5.4.0's
prologue clamp `if (from >= string->len) { from = string->len; }`. **I found
it, and it is not the fix.** The manager then found the actual `fix_commit` in
a place neither of us had looked — **the corpus's own `index.csv` has a
`fix_commit` column** (`PLAN_PHP.md:109`), and `CRASH-124`'s cell reads
`cb3cca21b345`. Verified here:

```
CRASH-124  fix_commit  'cb3cca21b345'
CRASH-124  c_file_line 'ext/mbstring/libmbfl/mbfl/mbfilter.c:1203 (OOB read site);
                        missing guard at ext/mbstring/mbstring.c:1807'
CRASH-115  fix_commit  'f95c1df58349'      <- the column is trustworthy: this is
                                              exactly what ph03 established
                                              independently
```

⚠ **The `c_file_line` field said `missing guard at mbstring.c:1807` all along,
and I read the catalogue's paraphrase of it instead of the CSV.** That is
`.memory-php/00-corpus.md`'s standing rule — *the label is a hint; the line is
the claim* — with the roles swapped: the field was right and the derived prose
was where I stopped.

### 4b. The commit

```
cb3cca21b34518caf45852ed90597052e99294c3
Ilia Alshanetsky, 2005-12-15
"Fixed possible memory corruption inside mb_strcut()."
ext/mbstring/mbstring.c, +7 lines, ONE hunk, TWO guards
controls/cb3cca21b345.patch, 829 B, sha256 14dbafc9a3b970d0…
```

```c
+	if (from > Z_STRLEN_PP(arg1)) {          /* hunk (a) */
+		RETURN_FALSE;
+	}
+	if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) {   /* hunk (b) */
+		len = Z_STRLEN_PP(arg1) - from;
+	}
+
 	ret = mbfl_strcut(&string, &result, from, len);
```

### 4c. ⭐ The history, and it is the row's second finding

`mbfl_strcut`'s **body** is byte-identical — sha256 `613648930a3d2551…`,
4 693 B — at six release tags (5.0.0, 5.1.0, 5.2.17, 5.3.0, 5.3.1, 5.3.2).
`.temp/php16/07-history.log`, `.temp/php16/01-fixcommit.log`,
`controls/fix_scope.py` Q4.

| tag | `mb_strcut`'s own guards before the call | `mbfilter.c` prologue |
|---|---|---|
| php-5.0.0 **← THIS ROW** | — | — |
| php-5.0.5 / 5.1.0 / 5.1.1 | — | — |
| **php-5.1.2** ← `cb3cca21b345` | **`from >` + the sum clamp** | — |
| php-5.2.17 | `from >` only (**sum clamp GONE**) | — |
| php-5.3.0 / 5.3.1 | `from >` + the sum clamp **(back)** | — |
| php-5.3.2 | `from >` only (**gone again**) | — |
| **php-5.3.3** ← `d9dda48f8a7e` | `from >` only | **YES** |
| php-5.3.29 / 5.4.0 | `from >` only | YES |

⭐ **So the bound was restored TWICE, four years and three months apart, in two
different files.** The 2005 fix repaired the userland entry point;
`mbfl_strcut` itself — a library function any other caller could reach — stayed
unbounded until `d9dda48f8a7e` (2010-03-12), *"— Update the bundled libmbfl to
the latest on upstream"*, **64 files, +3435 −4164, no CVE, no bug number, no
security label**. Its `mbfilter.c` half is at
`controls/d9dda48f8a7e-mbfilter.patch`.

⚠ **And hunk (b) went out, came back and went again** — dropped at 5.2, present
at 5.3.0/5.3.1, gone from 5.3.2 on. §4e measures what it does; a guard that
changes benign output and cannot settle down for three minor releases is a guard
nobody was sure about.

### 4c-bis ⚠⚠ TWO GREPS, TWO OPPOSITE ERRORS, AND THE TABLE ABOVE IS THE REPAIR

**The first version of this table was wrong and the mistake is worth more than
the table.** I built it twice with two `grep`s over `mbstring.c`:

* `if (from > Z_STRLEN_PP(arg1))` — the 5.1.2 spelling. It scored **php-5.3.0
  through 5.4.0 as UNGUARDED**, because by 5.3 the same guard is spelled
  `if ((unsigned int)from > string.len)`. **A spelling-dependent grep reporting
  ABSENCE.**
* `from > Z_STRLEN_PP(arg1)` unanchored — it scored **php-5.0.5 and 5.1.1 as
  GUARDED**, because the hit is inside `PHP_FUNCTION(mb_strimwidth)`. **A
  function-blind grep reporting PRESENCE.**

⚠ **Neither error is visible from its own output; both are visible from the
other's.** What caught it was running the broader pattern *and then chasing the
discrepancy instead of taking the newer answer.**The repair is to stop matching
text and ask a question about a function**: `07-history.log` now parses
`PHP_FUNCTION(mb_strcut)` out of the file and looks only between its opening
brace and its `mbfl_strcut(` call. That is `.memory-php/`'s own recurring
lesson — *a guard that is a string search is a guard with a spelling* — arriving
in a **history table** rather than in a gate.

### 4c-ter ⭐⭐ AND THE SIBLING ENTRY POINT ALREADY HAD THE GUARD, IN 2004

Chasing that discrepancy turned up the finding this row should be remembered
for. In the **pinned 5.0.0 tarball**, `ext/mbstring/mbstring.c:1900`:

```c
/* PHP_FUNCTION(mb_strimwidth) */
if (from < 0 || from > Z_STRLEN_PP(arg1)) {
    RETURN_FALSE;
}
```

**It is the only occurrence of that text in the whole file.** `mb_strimwidth`
clamps `from` from above; `mb_strcut`, one screen away in the same file, written
in the same style against the same zval accessor, clamps it only from below —
and `cb3cca21b345` is, five and a half years later, that same line copied down.

⭐ **So this row's asymmetry is not one asymmetry, it is three, at three scales:**

| scale | guarded | unguarded |
|---|---|---|
| **within one function** | `mbfl_strcut`'s END walk, `:1213` | its START walk, `:1202` |
| **within one file** | `mb_strimwidth`, `mbstring.c:1900` | `mb_strcut`, `:1807` |
| **across time** | the caller, 2005 · the library, 2010 | 5.0.0 – 5.1.1 |

⚠ **That is the shape of the finding, and it is a stronger one than "the author
forgot a bound":** at every scale the correct code is *adjacent* to the
incorrect code. The bound was never unknown — it was never in the one place it
was needed.

### 4d. ⚠ The fidelity question, stated rather than smoothed over

**`kernel_hardened.c`'s citation is a different function from the extracted
one.** The manager asked for this to be said plainly, and here it is.

**Why I think it is nevertheless faithful.** This row's kernel is *two frames*.
`ph07_strcut` is `mbfl_strcut`'s arm; the `kernel()` wrapper **is**
`PHP_FUNCTION(mb_strcut)` — it already carries that function's two negative
clamps (`mbstring.c:1787-1805`), because they decide the kernel's domain and
without them a negative `from` would reach the walk, which `mb_strcut` cannot
produce. The fix's seven lines therefore land in the wrapper in **upstream's own
position**: after those two clamps, immediately before `mbstring.c:1807`'s call.
The diff between `c/kernel.c` and `c/kernel_hardened.c` is upstream's diff, in
upstream's place, against upstream's neighbouring lines.

**What a reviewer should attack.** R1 and R1h differ in the *wrapper*, not in
the *extracted function*. So this row cannot answer *"what does the fix cost
inside `mbfl_strcut`?"* — nothing was added there. It answers *"what does the
fix cost `mb_strcut`?"*, which is the question PHP's users had. ⚠ **If the
project wants the first question, the row it needs is R1h built from
`d9dda48f8a7e`'s prologue instead**, and `controls/fix_scope.py` already
measures that variant (`R1_2010`) so the swap is a decision, not a rebuild.

### 4e. What each guard buys — `controls/fix_scope.py`, `.temp/php16/08-fixscope.log`

```
calls interpreted                     : 133932
cb3cca21b345 hunk (a) would fire      : 16320
cb3cca21b345 hunk (b) would fire      : 32238   (with (a) not firing)

variant    reads past val[slen]  answer != R1
R1                        15333             0
R1h_a                         0         16320      <- (a) ALONE closes it
R1h                           0         32190
R1_2010                       0          5717      <- the 2010 clamp also closes it
R1_walk                   13293             0      <- the 2010 WALK REWRITE does NOT
```

⭐⭐ **`R1_walk` is the result to carry.** `d9dda48f8a7e` rewrote the start walk
to test before it reads (`for (m=0, p=val, q=p+from; p<q; p += (m=mbtab[*p]))`),
and **that rewrite alone still over-reads on 13 293 of the same calls.** The
loop shape is not the fix; the bound on `from` is. This is the variant a reader
guesses at, and it is wrong — which is why it is in the file.

⚠⚠ **Hunk (b) CHANGES BENIGN OUTPUT.** Q2, over the 117 612 calls that neither
over-read nor hit hunk (a):

```
of those, hunk (b) CHANGES the answer : 15870   (13.5 %)
e.g. 2byte/1 from=1 length=1
     (a) alone -> start=0 end=1 len=1
     (a)+(b)   -> start=0 end=0 len=0
```

It shortens `length`, which moves `k = start + length` out of the
`k >= string->len` shortcut and into the bounded end walk, and the cut comes
back shorter — on an input that never crashed. ⭐ **Upstream itself withdrew
it: php-5.2.17 carries (a) alone.** `check.py` stage 7h requires R1h to be
byte-identical to R1 on every non-adversarial input, so `inputs/gen.py`
`_check_span` refuses to write a measured window with
`from + length > string->len` and asserts `cb3cca21b345-fires=0`. **The change
is measured where it belongs and the measured corpus is not contaminated by
it.**

### 4f. ⭐ The `(unsigned)` casts are adequate, and the reason is the order

`controls/guard_equiv.py`, `.temp/php16/12-guardequiv.log`. Hunk (b)'s
`((unsigned) from + (unsigned) len)` is a 32-bit sum on two `long`s and looks
like an overflow waiting to happen. It is not:

```
SHIPPED    must NOT fire  disagreements=0
VARIANT c32 must NOT fire disagreements=0     <- the C's own 32-bit sum, in place
VARIANT ord must NOT fire disagreements=0     <- the two guards swapped
VARIANT m1 must FIRE      disagreements=2276
VARIANT m2 must FIRE      disagreements=269
VARIANT m3 must FIRE      disagreements=509
triples compared: 5122
```

`c32` is a **result**: hunk (a) runs first and has already bounded
`from <= string->len <= INT_MAX`, so the sum cannot reach 2³². ⚠ **`ord` is a
refuted prediction and it is left visible**: I expected swapping the guards to
fire, and it does not, because hunk (a)'s `RETURN_FALSE` *discards* whatever
hunk (b) computed. A control written to fire and then quietly reclassified is
how a probe stops measuring anything, so the prediction and its refutation both
stay in the file.

`SHIPPED must NOT fire, 0 disagreements` is the demonstration
`PROTOCOL_PHP.md` §A1(c) asks for on the Rust rungs' `usize` spelling of the
clamps, against a build of the C itself, with three firing mutants.

---

## §5 ⭐⭐ THE ROW'S FINDING: one function, one guarded walk and one unguarded one

`mbfl_strcut` does two cursor walks over the same buffer with the same table.

```c
/* :1202-1210 -- the START search.  UNBOUNDED. */
for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }

/* :1212-1223 -- the END search.  BOUNDED. */
k = start + length;
if (k >= (int)string->len) { end = string->len; }
else { end = start; while (n <= k) { end = n; m = mbtab[*p]; n += m; p += m; } }
```

The second one's `else` branch is entered only when `k < string->len`, and it
steps while `n <= k`, so **every byte it reads is in range for a reason that is
in the 5.0.0 source already.** The first one has the same author, the same
table, the same cursor, three lines earlier, and no bound at all.

⭐ **The proof makes the asymmetry visible as an obligation.** In `verus.rs`,
`walk_start`'s reads are discharged from `frm <= slen` — a fact that does not
exist in 5.0.0 and arrives only with `cb3cca21b345` — while `walk_end`'s are
discharged from `k < slen`, which `mbfilter.c:1213` establishes. Delete the
2005 guard and only one of the two loops stops verifying:
`controls/negatives.py --emit noguard` fails on `invariant not satisfied before
loop: frm <= slen`, the start walk's bound, and the end walk is untouched.

⚠ **It is not "the author forgot".** The end search *needs* a bound because `k`
is `start + length` and `length` is unbounded; the start search's cursor is
compared against `from`, which *looks* like a bound and is not one, because
nothing relates `from` to `string->len`. **The defect is that a comparison
against an attacker-controlled scalar reads as a bounds check.**

---

## §6 ⭐ The over-read does not change the answer, and that is why it survived

`controls/fix_scope.py` Q3, `.temp/php16/08-fixscope.log`:

```
over-reading calls re-run under 7 different fillers : 15333
calls whose answer MOVED                            : 0
MUST-FIRE CONTROL (mbfilter.c:1227's `start > len` clamp DELETED): 13293 of 15333 moved
```

**Mechanism.** `start` is assigned the cursor of the iteration *before* the
break, so the first read at index `i > slen` happens with `start == i > slen`
already set; `start` only grows; `mbfilter.c:1227`'s `if (start > len) start =
len;` then forces `start = end = slen` and an empty cut. **R1's return value is
a deterministic function of the in-bounds input on every call, over-reading or
not.**

⭐⭐ **So the clamp that arrives too late to PREVENT the over-read is exactly
the clamp that HIDES it.** That is what the must-fire control demonstrates: the
same probe, with `:1227` deleted, moves on 13 293 of the same calls.

⚠ **My first must-fire control did not fire and I am leaving that visible.** It
moved `start = n` past the break test — so `start` took the cursor that had read
out of bounds — and the answer *still* did not move, for the same reason. **A
control that does not fire is not a passed control; it is a probe measuring
nothing**, and chasing why it did not fire is what produced this section.

**Consequence for the ladder.** `inputs/adversarial-silent.bin` and
`adversarial-offbyone.bin` differ only in the shape of the LAST CHARACTER
(all-ASCII vs a truncated four-byte sequence) and in nothing else. R1 reads one
byte past the heap block on both. The pair is here so the reader can see that
the *trajectory* differs while the *effect* does not.

---

## §7 The allocator

`uses_allocator: true`, and it is real: `mbfl_malloc` is
`(__mbfl_allocators->malloc)` (`mbfl_allocators.h:48`) and `mbstring.c:764`
points that vtable at `_php_mb_allocators`, whose `malloc` is `emalloc`
(`:240-243`) and whose `free` is `efree` (`:255-258`). So `mbfl_malloc((n + 8))`
at `:1245` **is** PHP's allocator and the row links
`common-php/emalloc_shim.h`.

⚠ **The truncations are not the defect here.** `n = end - start` is clamped to
`string->len` *before* the allocation, so `cap` is at most the window plus
eight and T1/T2/T3 sit ~2⁴⁰ below their moduli. The tally is folded into the
checksum so a rung that sized the result differently cannot agree by accident.

⚠ **The Rust rungs reproduce `php_shim_tally()` ARITHMETICALLY** and do not
link the shim. That pins the allocation SIZE across rungs; it is **not**
evidence that any Rust rung ran PHP's allocator. `ph03` says the same thing and
`TASK_PHP_013` §11 warns the technique does not carry to a row where the tally
*is* the defect. It carries here for the reason above.

---

## §8 The measurement, and the mechanism for every delta

`-O3 isolated`, kernel-exclusive `Ir`, from `results-php/ph07-strcut-cursor.json`
(`.temp/php16/22-irtable.log`). `small` = 25 000 calls over a 553-byte window;
`large` = 12 000 over 4 074. The two strides differ mod 4, 8 and 16.

| cell | `Ir`/call small | `Ir`/call large | **`Ir` / window byte** | fixed `Ir`/call |
|---|--:|--:|--:|--:|
| `c-gcc` (R1) | 2 376.5 | 15 982.7 | **3.8643** | 239.5 |
| `c-gcc-h` (R1h) | 2 383.8 | 15 989.9 | **3.8643** | 246.8 |
| `c-clang` (R1) | 2 026.6 | 13 228.2 | **3.1814** | 267.3 |
| `c-clang-h` (R1h) | 2 035.8 | 13 237.3 | **3.1813** | 276.5 |
| `safe_naive` (R2) | 2 818.3 | 19 669.9 | **4.7860** | 171.6 |
| `safe_tuned` (R3) | 2 029.4 | 14 159.6 | **3.4451** | 124.3 |
| `unsafe` (R4) | 1 796.2 | 12 483.8 | **3.0354** | 117.7 |
| `verus` (R5) | 1 796.2 | 12 483.8 | **3.0354** | 117.7 |

⚠ **`RECAP_PHP.md` open item 9 / F14 respected: no number here is put beside a
`pNN` number, in a table or in prose.**

### 8a ⭐ THE UPSTREAM FIX COSTS A CONSTANT, NOT A RATE

`c-gcc` and `c-gcc-h` have the **same marginal to four decimal places**
(3.8643 both); on clang they differ by 0.0001, which is the last digit.
`cb3cca21b345` is **two branches per call, outside both loops**, and it shows
up entirely in the fixed term: **+7.3 `Ir`/call on gcc, +9.2 on clang**.

⚠ **Contrast ph03**, where the 2004 fix moved the marginal by ∓3.0 `Ir`/line
and the sign was compiler-dependent — because *that* fix is a test inside the
outer loop and hands the optimiser a trip-count fact. **The same question,
"what does the upstream fix cost?", has a different SHAPE on the two rows, and
the shape is decided by where in the loop nest the guard sits.**

### 8b The mechanism, per loop, read off `objdump`

`.temp/php16/23-loops.log` — the tight loops, classified and counted:

| loop | body | R2 | R3 | R4 / R5 |
|---|---|--:|--:|--:|
| **start walk** | per character | **9 insns**, 1 bounds branch | **9**, 1 | **7**, 0 |
| **end walk** | per character | **8**, 1 | **8**, 1 | **6**, 0 |
| **copy** | per byte | **13**, 1 | *`memcpy@GLIBC_2.14`* | *`memcpy@GLIBC_2.14`* |
| **fold** | per byte | **10**, 0 | **8**, 0 | **8**, 0 |

R2's start walk, in full:

```
cmp    %rcx,%rax          <- the bounds check on s[n]
jae    <panic>
movzbl (%rbx,%rax,1),%r10d    <- s[n]
movzbl (%r10,%r8,1),%r10d     <- MBTAB[s[n]]   (no check: u8 index, [u8;256])
add    %rax,%r10
mov    %rax,%rbp
mov    %r10,%rax
cmp    %rsi,%r10
jbe    <top>
```

R4's is the same seven instructions with the `cmp`/`jae` pair deleted.

⭐⭐ **R3's two walks are BYTE-FOR-BYTE R2's — 9 and 8 instructions, one bounds
branch each.** That is `safe_tuned.rs`'s header claim, measured: **a
variable-stride cursor is not an iterator**, `n` advances by a value read out of
the byte it is standing on, and no reslice lets LLVM discharge `n < s.len()`.
**R3's entire gain over R2 is the copy and the fold**; **R4's entire gain over
R3 is the two walks.** The row's cost sits exactly where safe Rust cannot reach
it.

**Arithmetic check on the R3 → R4 delta.** The measured difference is
**0.4097 `Ir`/window byte**. Predicted from the mechanism with no fitting: the
start walk runs `from` bytes and the end walk up to `length`, and
`inputs/gen.py` draws them as fractions with means 0.441 and 0.291 of the
window; `make_body` emits characters of mean width ≈ 3.5 bytes, so
`(0.441 + 0.291)/3.5 = 0.209` walk steps per window byte × 2 deleted
instructions = **0.418**. ✅ **Within 2 % of the measurement, from the
disassembly and the generator alone.**

### 8c ⚠⚠ THE CAVEAT THAT MATTERS: `memcpy` IS OUTSIDE `kernel_exclusive_ir`

`.memory/03-measurement.md` rule 7 — *kernel-exclusive `Ir` misses whatever the
rung calls out to* — **bites on this row**, and the record shows it: R3, R4 and
R5 carry `bulk_calls: ['memcpy@GLIBC_2.14']` and R2 and the C rungs do not.
So the table above charges R2 for a byte-at-a-time copy it performs inline and
does **not** charge R3/R4/R5 for the copy they delegate.

**Measured, hand-run, with the pinned valgrind** (`.temp/php16/25-totalir.log`,
`--tool=callgrind`, TOTAL process `Ir`, which includes the `memcpy`):

| rung | total `Ir`/window byte | kernel-exclusive | difference |
|---|--:|--:|--:|
| `safe_naive` | 4.8237 | 4.7860 | +0.0377 |
| `safe_tuned` | 3.5147 | 3.4451 | +0.0696 |
| `unsafe` | 3.1050 | 3.0354 | +0.0696 |

**R2 vs R4 is +55.4 % on total `Ir` against +57.7 % kernel-exclusive; R3 vs R4
is +13.2 % against +13.5 %.** ✅ **The ordering and the magnitudes survive**, and
the hidden term is ~2 % of the total. The caveat is real, it is bounded, and it
is bounded by a measurement rather than by an argument.

### 8d ⚠ The wall clock says NOTHING here, and I am not going to pretend it does

`.temp/php16/24-wall.log`, `-O3 isolated`, 30 reps, `taskset -c 3`:

```
cell         ns/window-byte   vs unsafe   worst spread
safe_naive       1.1542        +5.04%       12.2 %
safe_tuned       1.1725        +6.71%       13.7 %
unsafe           1.0987         0.00%        8.0 %
verus            1.0391        -5.43%        3.0 %
```

⚠ **R4 and R5 are the same machine code** (§`identity`, `md5_fn_norel`
identical, 255 instructions both) **and their wall medians differ by 5.4 %.**
That is the noise floor of this box on this workload, and it is larger than
every difference the table contains. **The wall numbers are reported and are
not evidence for anything on this row** — `.memory/03-measurement.md` rule 6's
spirit, one step further: report ns, and then say when ns cannot decide.

### 8e What these numbers are NOT

- ⚠ **Not a searched comparison.** This row owes a `controls/spellings.py`
  (`PLAN_PHP.md` §5.3, the trap that has fired seven times). Each figure is the
  cost of *these* spellings of these rungs.
- ⚠ **Not a bounds-check tax in aggregate.** A ph07 call walks, walks again,
  allocates, copies and folds; only the two walks and (in R2) the copy carry a
  check R4 removes. §8b separates them.
- ⚠ **The C-vs-Rust column is confounded by a choice this row made and ph03
  made too**: `vec![0u8; cap]` ZEROES the destination and `mbfl_malloc` does
  not, so every Rust rung pays `cap` bytes of zeroing the C never pays. It
  cancels in every safe-vs-unsafe delta and does **not** cancel in
  C-vs-Rust — which is one reason `c-clang` (3.1814) lands so close to
  `unsafe` (3.0354) while `c-gcc` (3.8643) does not.
- ⚠ **`c-clang` beats `c-gcc` by 17.7 %** on the marginal, which is larger than
  the R3→R4 safety effect and is **not a safety effect at all**. The C rungs
  vectorise their copy (`vector_regs: ['xmm']`, 22–25 backward branches); the
  Rust rungs either call `memcpy` or emit a scalar loop. `.memory/03-measurement.md`
  rule 2 is why both C columns are here.

---

## §9 ⚠ Scope: what this row deliberately does NOT model

`mbfilter.c:1212` is `k = start + length` on two `int`s and **overflows** for a
`length` near `INT_MAX`. That is a **second, distinct defect**, fixed upstream
in 2016 by `f8dd10508bd6` / `64f42c73efc5` (bug #71906) — the only php-src
commit whose subject names an `mbfl_strcut` memory-safety bug, and it fixes the
*rewritten* function, not this one. R1h does not guard it either, so an input
that reached it would trip UBSan on the **hardened** rung and `check.py` stage
7h would hard-fail.

`inputs/gen.py::_check_span` therefore asserts `max(start + length) < 2^31` and
refuses a corpus that leaves `int`. **Stated as a boundary, not hidden**: a row
that models two defects at once cannot attribute a number to either.

---

## §10 R5 — Verus

**21 verified, 0 errors; 24 under `--cfg slb_twin`.** Three runs of each,
identical (`.temp/php16/10-rlimit.log`).

```
requires  off + len <= buf@.len(),  9 <= len
ensures   r == strcut_fold(buf@, off as int, len as int)
```

A full functional postcondition, not a memory-safety-only retreat.
`model.py::strcut_fold` re-derives the same `u64` from a different
decomposition, and `model.py::_dumb` from a third.

### 10a. The two facts the proof rests on, and they come from two places

1. **`mbtab_of(b) >= 1`** — every table entry is at least one, so `n` strictly
   increases and the start walk has a `decreases` at all. A fact about STATIC
   DATA, proved out of the literal 256-byte table by `lemma_mbtab_matches`
   (`by (compute_only)` over a recursive conjunction, plus one induction).
   **No `assume`, no `external_body`, no sixth trusted item** — §3.
2. **`from <= string->len`** — which is `cb3cca21b345` hunk (a), and is what
   discharges every `get_unchecked`. **Delete that one line and the proof
   fails.**

⭐ And the end walk needs neither: `mbfilter.c:1213` bounds it in the 5.0.0
source already (§5).

### 10b. ⚠⚠ The proof-budget finding, and the reduction came first

`.temp/php16/09-profile.log`, `.temp/php16/10-rlimit.log`.

The kernel first **did not verify at `--rlimit 100`** — ten times the default —
and `--profile` said why: **4 127 instantiations of vstd's
`Seq::new(len, f)[i] == f(i)`, 88 % of the total cost.** The cause is that
`MBTAB@` is `array_view`, which vstd defines as `Seq::new(256, …)`, so **every
mention of the table inside a spec function drags a 256-element sequence axiom
into the SMT context** — and `walk_start`/`walk_end` mentioned it on every
recursive step.

✅ **The repair was to take the table OUT of the spec path**: `mbtab_of` became
a closed form over the byte's range, `lemma_mbtab_matches` ties it to the
literal table once, and the `broadcast use vstd::array::group_array_axioms` was
scoped to the three items that need it instead of being module-level. **Same
kernel, same postcondition: from "does not verify at rlimit 100" to "verifies
at the default in five seconds."**

⚠ **`#[verifier::rlimit(30)]` is still on the kernel, and here is the honest
reason.** Measured after the reduction: the kernel needs ~10–12 plain and
**15 under `--cfg slb_twin`**, where the three verified twins add to the
module's context. At the default 10 it verified plain and **failed twin**; with
two `assert`s removed it verified twin and **failed plain**. A proof that passes
on one side of a coin flip is not a proof, so the budget is 30 — twice the worst
measured requirement — and `harness/check.py::_verus` passes no `--rlimit`, so
it has to be an attribute. **It is 30 and not 300 because the cost was attacked
first.**

⚠ **The reusable lesson, and it is not about this row**: *a module-level
`broadcast use` is a cost every function in the file pays.* Scoping the groups
to the items that need them is free and, on a row that lifts a lookup table,
decides whether the file verifies at all.

### 10c. TCB — four trusted items

| item | why it is trusted | twin |
|---|---|---|
| `get_unchecked(v: &[u8], i)` | vstd ships no spec for `<[T]>::get_unchecked`; the `requires` is std's documented contract | ✅ `slb_twin_get_unchecked` |
| `vget_unchecked(v: &Vec<u8>, i)` | same, for the destination read | ✅ |
| `vset_unchecked(v: &mut Vec<u8>, i, x)` | the destination WRITE; `ensures` is the whole post-state `old(v)@.update(i, x)` | ✅ |
| `load_input`, `emit` | file I/O and `println!`; **no `ensures` at all**, deliberately — an `ensures` here would axiomatise the contents of a file | n/a (no `unsafe`) |

⚠ **That is five `external_body` items and four trusted *contracts*** — `emit`
and `load_input` state nothing, so nothing can be wrong about them except that
they run; they are counted anyway, because `.memory/04-verus.md` records a pilot
published as *"one 3-line wrapper"* whose true tally was three.

### 10c-bis. Trusted items — the arguments no oracle can make

`harness/check.py` stage `5c-twin` requires one written argument per trusted
item, for the three things no stage of the gate can judge. It prints them and
fails without them; **only a human can judge them.**

SLB-TRUSTED-ARGUMENT verus.rs get_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked(i)`; the twin's body is `v[i]`. The standard
library documents `get_unchecked(i)` as `index(i)` with the bounds check
removed, so it is the same operation on the same slice at the same index, and
Verus checks the bound `v[i]` needs against the same `requires`. A defensive
twin — `if i < v.len() { v[i] } else { 0 }` — cannot satisfy the `ensures` and
fails the stage rather than passing it.

(b) **Is the `ensures` complete with respect to every unchecked operation the
body performs?** Yes *as the body stands*: one expression, one unchecked read,
at index `i` of slice `v`, and `ensures r == v@[i as int]` names that index and
that slice. ⚠ **Nothing mechanical enforces it.** A second unchecked read the
`ensures` never mentions — `let _peek = *v.get_unchecked(i + 1);` — is invisible
to 5a, 5c, 5c-req and 5c-twin alike.

⚠⚠ **AND THIS ROW'S BACKSTOPS ARE WEAKER THAN ph03's, WHICH IS WORTH SAYING
RATHER THAN COPYING ph03's PARAGRAPH.** ph03 can lean on its `exact` O3
identity pin: an extra read added to `verus.rs` alone moves `md5_fn` and stage
3c fails. **ph07's O3 pin is `norel`, not `exact`** (§`identity`), because the
kernel calls `memcpy@GLIBC` and the two crates lay their PLT out differently —
so identity here compares `md5_fn_norel`, which is a weaker instrument. It
would still catch an added `movzbl` (the instruction count 255 and the byte
count 953 are both pinned and both would move), but it is a normalised
comparison rather than a byte one. **Miri is the other backstop and it needs an
input that reaches the boundary**: on ph07 that is
`adversarial-offbyone.bin`/`-empty.bin`/`-wild.bin`, whose whole point is that
`from` sits past the end — except that R4/R5 REFUSE those calls at
`cb3cca21b345` hunk (a) and never reach the walk at all. ⚠ **So on the
adversarial inputs Miri exercises the refusal, not the boundary; the boundary
read `s[slen]` (the zval terminator) is reached on the benign windows whose
`from == string->len`, which `inputs/gen.py` guarantees exist (`from==len=4` on
`small.bin`, 256 on `large.bin`) and `_check_span` asserts.** That is the input
class a reviewer should check the body against. **Read the body, every time.**

(c) **Does the clause mean the same in both configurations?** Yes. `i < v@.len()`
mentions only `i`, `v` and vstd's `@`/`len()`, and `v: &[u8]` / `i: usize` are
concrete types with no generic or associated item that a `#[cfg]` could
redefine. The gate additionally forbids the token `slb_twin` anywhere in the
file except each twin's own `#[cfg(slb_twin)]`.

SLB-TRUSTED-ARGUMENT verus.rs vget_unchecked

(a) Yes, and it is `get_unchecked`'s argument with `&Vec<u8>` in place of
`&[u8]`: the unchecked operation is `*v.get_unchecked(i)` reached through
`Vec`'s `Deref<Target = [T]>`, and the twin is `v[i]`, which is `Vec`'s `Index`
— documented as the slice index. ⚠ **It is a separate item rather than a reuse
of item 1 for a real reason**: `out` is a `Vec` the kernel owns and `s` is a
borrowed slice, and passing `out.as_slice()` to item 1 would put a `Deref` call
between the proof and the fold loop that R4 does not have, which would move the
`norel` identity pin.

(b) Yes as the body stands — one expression, one unchecked read at `i`, and the
`ensures` names it. Same residual and the same two backstops as item 1, with
the same weakening noted there. ⚠ **Its boundary input is different and easier**:
this wrapper reads `out[j]` for `j < cnt`, and `cnt == 0` on every adversarial
input (the refusal path) while `cnt` is hundreds of bytes on `small`/`large`,
so the boundary `j == cnt - 1` is reached on every benign call.

(c) Yes, and identically to item 1: `i < v@.len()` over `&Vec<u8>` / `usize`.

SLB-TRUSTED-ARGUMENT verus.rs vset_unchecked

(a) **Is the twin's body the right checked stand-in?** Yes. The unchecked
operation is `*v.get_unchecked_mut(i) = x`; the twin is `v.set(i, x)`, vstd's
verified `Vec` store, whose own `ensures` is `v@ == old(v)@.update(i, x)` —
character for character this item's postcondition. ⚠ It is **not** `v[i] = x`,
because `IndexMut` on `Vec` has no vstd specification; `set` is the checked
spelling Verus can reason about, and the twin rules forbid `unsafe` in a twin
so there is no third option.

(b) **Is the `ensures` complete?** Yes, and **this is the item where the answer
is load-bearing rather than routine.** The postcondition is the WHOLE
post-state, `final(v)@ == old(v)@.update(i as int, x)`, not `v@[i] == x`. A body
that also clobbered `v[i + 1]` would satisfy `v@[i] == x` and violate
`update(i, x)`, so **for a body whose only writes are through this contract the
`ensures` is complete by construction** — which is exactly why it is spelled
this way and not the shorter way. ⚠ The residual is a body that performs an
extra unchecked **READ**, which no `ensures` about the post-state can see; that
is item 1's residual and has item 1's backstops.

(c) **Does the clause mean the same in both configurations?** Yes.
`i < old(v)@.len()` and `final(v)@ == old(v)@.update(i as int, x)` mention only
`i`, `v`, `x` and vstd's `@` / `len()` / `update()`. `v: &mut Vec<u8>`,
`i: usize` and `x: u8` are concrete, and `#[cfg(slb_twin)]` is the only `cfg` in
the file (the gate checks that).

SLB-TRUSTED-ARGUMENT verus.rs load_input

(a) There is **no twin and there must not be**: this item contains no `unsafe`,
so the twin regime does not apply to it, and a checked stand-in for argument
parsing and file I/O does not exist. It is trusted because it is I/O.

(b) The `ensures` is **empty, deliberately**. An `ensures` here would be an
axiom about the contents of a file, which nothing can justify. Every fact the
proof needs — `buf@.len() == n_blob`, `stride >= 9`, `stride <= n_blob` — is
re-derived at run time inside verified code from `bytes.len()` and the driver's
own guard.

(c) N/A — no clause, and no `cfg`.

SLB-TRUSTED-ARGUMENT verus.rs emit

(a) No twin, no `unsafe`: `println!` through `common/driver.rs`. Trusted
because printing is not verifiable.

(b) No `ensures`, so nothing to be complete about. What it prints is checked
elsewhere and much more strongly: stage 2 compares this rung's stdout against
`model.py`'s expectation on every input, across all 32 cells.

(c) N/A.

### 10d. The mutants — `controls/negatives.py`, `.temp/php16/13-negatives.log`

```
noguard    expect FAIL got FAIL   20 verified, 1 errors   ok
nopos      expect FAIL got FAIL   (mbtab_matches_upto(256) fails)   ok
notable    expect FAIL got FAIL   (one table entry changed)   ok
noconsume  expect PASS got PASS   21 verified, 0 errors   ok
verus.rs sha256 unchanged: 28811d6d6f45c3b2
```

⚠ `noguard` deletes **both** `cb3cca21b345` hunks and not just (a), because
hunk (b)'s `slen - frm` needs `frm <= slen` too — a hunk-(a)-only mutant fails
on an arithmetic underflow one line later and never reaches the walk. Measured:
`.temp/php16/13-noguard.log`.

⚠ `noconsume` is a **must-PASS** control and is therefore weaker than the other
three: it shows the postcondition is unconsumed decoration unless `main` reads
it, and it cannot show the file is still being mutated. `noguard` shares the
emit path and is must-FAIL, so a `negatives.py` that had stopped editing
anything would be caught there.

---

## §11 What I did NOT do, and what I am unsure about

1. ⚠ **No `controls/spellings.py`.** `PLAN_PHP.md` §5.3 asks for a re-derivable
   search of both endpoints before a rung difference is published. This row
   ships one spelling per rung by construction. **No ratio in §8 is *the* cost
   of safety on this kernel** — each is the cost of *these* spellings. ph03 owes
   the same thing and the debt is now on two rows.
2. ⚠ **No `sweep-*` band.** `work_per_call` moves between `small` and `large`
   (553 vs 4074, different residues mod 4/8/16), which is what
   `check_marginal_ir` needs, but two points and a line is not a curve.
3. ⚠ **`provenance.c_lines` pins one span and this row lifts two** (the walk,
   and `mblen_table_utf8` at `mbfilter_utf8.c:39-56`). `TASK_PHP_015` §2.5
   deferred the multi-span schema change with a design attached; this row is the
   second to want it and also does not take it. §3 lists the three other ways
   the table's bytes are pinned.
4. ⚠ **R1h is cited to a different function from the extracted one** — §4d. I
   argue it is faithful and I have written down what to attack.
5. ⚠ **`#[verifier::rlimit(30)]`** — §10b. A reviewer should ask whether the
   budget hides a proof that is one edit from not closing.
6. **Unsure: whether `adversarial-silent.bin` earns its measurement slot.** It
   costs eight iterations over a 105-byte window and it is the only cell that
   shows the over-read's *effect* is invisible while its *trajectory* is not.
   A reviewer may reasonably say §6's numbers already say that and the file is
   redundant.
7. **Unsure: the `FRACTIONS` table.** `from` and `length` are drawn as fixed
   fractions of the window so the work scales with `work_per_call`. That is a
   design choice with a consequence: **every window's `from` is at the same
   relative position**, so the corpus spans lead-byte classes and the two arms
   of `:1213` but *not* the distribution of `from` a real workload has.
   `model.py::selfcheck`'s synthetic sweep covers the domain; the *measurement*
   does not.
8. **Unsure: `work_per_call = stride` over-estimates by more than ph03's does.**
   A ph07 call walks `from` bytes, then up to `length` more, then copies
   `end - start` — none of which is the window. The over-estimate raises the
   derived `Ir` floor, which is the safe direction, but the denominator is
   further from the work than on a row that touches every byte once.
