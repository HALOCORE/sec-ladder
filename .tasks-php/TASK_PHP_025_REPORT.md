# TASK_PHP_025 — `ph16-fdset-index`, row 3 — engineer's report

**Role:** research engineer. **Row:** `patterns-php/ph16-fdset-index/`.
**Scratch:** `.temp/php25/` (`REFETCH.sh` regenerates every artefact).

---

## 0. Bracket

**First**, before anything was touched:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE
$ python3 harness-php/gate.py --tool measure --check-stale
6 record(s) examined, 0 STALE
```

**Last**, after the row landed and gated green:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE                 <- UNCHANGED: nothing under
                                                  harness/ common/ patterns/
                                                  results/ pilot/ was touched
$ python3 harness-php/gate.py --tool measure --check-stale
FRESH  results/gate/ph16-fdset-index.json   37 source(s)
FRESH  results/ph16-fdset-index.json        19 source(s) + 6 input(s)
8 record(s) examined, 0 STALE
```

⚠ **The php side is 8 and not 6 because this row added two records** — one gate,
one measurement. The task file's bracket figure was taken before the row
existed.

---

## 1. ⚠ THE MANAGER'S `:657` IS WRONG AND `TASK_PHP_020_REPORT.md:131`'s `:658` IS RIGHT

`TASK_PHP_025` §1 and `.temp/mgr166/NOTES.md` both place
`fd_set rfds, wfds, efds;` at `streamsfuncs.c:657` and say `_020`'s `:658` is
"off by one and harmless". **The correction is inverted.** Measured against the
pinned tarball (`5783e0c0…d6919`, verified before reading):

```
$ grep -a -n 'fd_set.*rfds' streamsfuncs-5.0.0.c
658:	fd_set			rfds, wfds, efds;
$ sed -n '653,660p' streamsfuncs-5.0.0.c | cat -A | sed -n '5p'
^Istruct timeval *tv_p = NULL;$          <- this is :657
```

`:541` (`FD_SET(this_fd, fds)`) is exact, as claimed.

## 2. ⚠⚠⚠ THE UPSTREAM FIX HAS **THREE** POSIX GUARDS, NOT TWO

`TASK_PHP_025` §2 names `PHP_SAFE_FD_SET` and `&& this_fd >= 0`. Read from the
patch (`.temp/mgr166/99e290f882c9.patch:386-450, 700-724`), the commit also adds
a third macro **and applies it in the caller — the frame this row lifts**:

```c
# define PHP_SAFE_MAX_FD(m, n)  do { if (m >= FD_SETSIZE) { _php_emit_fd_setsize_warning(m); m = FD_SETSIZE - 1; }} while(0)
```

called as `PHP_SAFE_MAX_FD(max_fd, max_set_count);` in
`PHP_FUNCTION(stream_select)` immediately after the `if (!sets)` test.

⭐ **It is not about the write.** `*max_fd = this_fd` sits *inside* the arm
`PHP_SAFE_FD_SET` protects but is **not bounded by it**, so guard (b) alone
still hands `select(2)` an `nfds` past `FD_SETSIZE`. Since this row folds
`max_fd`, the third guard is observable in the checksum, and
`controls/fix_scope.py` prices it apart from (b) — which matters for §4's F52
argument. `max_set_count` is Win32-only (the POSIX arm ignores its second
argument) and is declared a `deletion`.

## 3. ⚠⚠⚠ ONE OF THE FOUR MEASURED C CELLS ALREADY CARRIED THE ROW'S OWN BOUND

**Nothing in the task file anticipated this, and it would have silently
invalidated the row.**

```
$ ./fp_gcc-O0    oob 2048   ->  _FORTIFY_SOURCE undefined   SURVIVED
$ ./fp_gcc-O3    oob 2048   ->  _FORTIFY_SOURCE = 3         *** bit out of range
                                 0 - FD_SETSIZE on fd_set ***: terminated  (rc 134)
$ ./fp_gcc-O3-nofortify      ->  _FORTIFY_SOURCE = 0         SURVIVED
$ ./fp_clang-O0 / -O3        ->  undefined                   SURVIVED
```

Ubuntu 24.04's gcc spec adds `-D_FORTIFY_SOURCE=3` whenever it optimises;
glibc's fortified `FD_SET` is `__FD_ELT` → `__fdelt_chk`, testing
`d < FD_SETSIZE`. **That is exactly the bound `streamsfuncs.c:541` is missing.**

`controls/fortify.py` (three controls, all green) measures the cost on
**benign, in-range** indices, with the denominator counted from `model.py`'s own
decode rather than estimated:

```
gcc   -O3 with #undef      92 605 764 Ir
gcc   -O3 without         148 709 085 Ir     +56 103 321 = +60.6 %
clang -O3 with #undef      90 887 777 Ir
clang -O3 without          90 887 763 Ir     -14 Ir TOTAL -- clang never fortifies
benign FD_SET calls on small.bin = 3 773 157   =>  14.87 Ir per FD_SET (gcc)
```

Both C kernels therefore `#undef _FORTIFY_SOURCE` before the first system
header, itemised as a `substitution` in `provenance.divergences`. Without it
`c-gcc-O3` is a hardened rung wearing R1's label, carrying a 60 % tax a reader
would read as C-versus-Rust while `c-clang-O3` carried none.

⚠ **I first quoted 7.01 Ir/`FD_SET` from a standalone probe and it was wrong for
this row** — different code shape. Corrected in four places; disclosed in
`NOTES.md` §0 and §12 as a `contract_sha256` move.

⭐ **The reusable lesson:** `PROTOCOL_PHP.md` §A1's substitution rule is written
for what the EXTRACTION changes. This is a thing the extraction did *not* change
and the TOOLCHAIN did. **A row that only diffs its C against the tarball cannot
see it; only running the binary can.**

## 4. THE TIER — `narrowed`, and the test I applied

**Two tests, and they disagree.** I applied the **definition**
(`PLAN_PHP.md` §4.1 / `PROTOCOL_PHP.md` §A1) and not `TASK_PHP_012` M4's
enclosing-frame heuristic:

| test | verdict |
|---|---|
| M4's — *is the defect site inside a `PHP_FUNCTION`/argument-parsing frame?* `stream_array_to_fd_set` is a `static` helper | `verbatim` |
| the definition — *did a wrapper come off (zval unpacking, argument parsing), body unchanged?* | **`narrowed`** |

What comes off is `Z_TYPE_P(...) != IS_ARRAY`, the `zend_hash` cursor triple,
`php_stream_from_zval_no_verify` and `php_stream_cast` — **zval unpacking, every
one** — and what is left, `FD_SET(this_fd, fds); if (this_fd > *max_fd) …`, is
unchanged. **The M4 test asks about the enclosing frame and the definition asks
about what came off; this row is the case that separates them.** A `static`
helper can still be all wrapper.

⚠ `modelled` was considered and refused: the mechanism is **not** re-expressed —
`FD_SET` is lifted with the platform macro intact, which is precisely what lets
§3 measure what the toolchain does to it.

⚠⚠ **`patterns-php/CATALOGUE.md` still says `verbatim` for `ph16`**, and this
task was forbidden to edit it. **The manager owns that correction.**

**The overlap number and what I think of it** (`PROTOCOL_PHP.md` §F9 — this is
the first real row it has been read on):

```
per-span overlap: span0 31% (5/16), span1 15% (6/39)
kernel overlap 20% (11/55)   tier=narrowed is expected to clear 25%
unevaluable_conditionals: 1  (#ifndef PH16_KERNEL_H)
```

Below expectation, and I am **not** repairing it by moving the tier. `NOTES.md`
§1b accounts for it line by line: span1 is the *caller frame*, pinned because it
contains the **object** and a third of R1h, and the row deliberately drops
`zend_parse_parameters`, the timeout, `php_select` and the three
`stream_array_from_fd_set` calls; span0's 11 missing lines are exactly the
wrapper. ⚠ **Dropping `extra_spans[0]` would have raised the union to 31 % and
made the row worse** — that is `ph07`'s `TASK_PHP_017` M1 lesson. **A span
pinned for its DECLARATIONS rather than its statements is a shape the heuristic
does not model.**

## 5. ⭐⭐ THE ORACLE — and it needed no canary

`TASK_PHP_025` §6.1 asked whether the `volatile` canary survives contact with a
real kernel, and whether honouring the tier costs the oracle. **Neither: the
canary was not needed at all.** `PHP_FUNCTION(stream_select)` already has two
live neighbouring `fd_set`s and reads all three back at `:706`, so the witness
is PHP's own data. `idiom.forbidden[2]` now **bans** a canary, for the reason
§6.1 half-anticipated: it would put an object the compiler may not move in the
middle of the layout the completeness range is stated against.

**The frame, measured** (`.temp/php25/layout_probe.c`):

```
gcc   -O0/-O3   rfds +0  wfds +128  efds +256   span 384 B   LOWEST = rfds
clang -O0/-O3   rfds +0  wfds -128  efds -256   span 384 B   LOWEST = efds
```

Contiguous under both — **in opposite order**.

**⚠⚠ F52 IS THE HAZARD HERE AND THIS IS THE CHECK THAT IT DID NOT BITE.** R1
differs from R1h for **two** reasons: the write, and `max_fd` going unclamped
(guard (c) — §2). A control that said *"R1 ≠ R1h"* would have been satisfied by
the second alone, on a row whose whole claim is the first. So
`controls/oracle.py` **never differences the rungs.** It predicts R1's exact
checksum from the measured layout:

| cell / input | predicted | measured |
|---|---|---|
| `c-gcc-O3` / `adversarial-redzone.bin` | 16790048728120879104 | **16790048728120879104** |
| `c-gcc-O3` / `adversarial-silent.bin` | 13722268663371347968 | **13722268663371347968** |
| `c-clang-O3` (desc layout) / `-redzone` | 18151814905338390528 | **18151814905338390528** |
| `c-clang-O3` (desc layout) / `-silent` | 15084034840588859392 | **15084034840588859392** |

**Bit for bit, both compilers, from the layout alone — nothing left over.** Its
three negatives: predicting with the write suppressed does **not** match;
predicting against gcc with clang's layout does **not** match (and vice versa);
and on `small.bin`/`large.bin` prediction, R1, R1h and `model.py` all agree with
`escaped == 0`.

**⭐ Where ASan stops, measured on the real frame** (`asan_sweep.c`, one
`FD_SET` per process, gcc `-O1 -fsanitize=address,undefined
-fstrict-aliasing`):

| index | offset past `rfds` | ASan | the row's own fold |
|---|---|---|---|
| ≤ 1023 | in bounds | silent | unchanged |
| **1024 … 1279** | 128 … 152 | ✅ REPORTED `stack-buffer-overflow` | — |
| **1280 … 3071** | 160 … 376 | ⚠ **SILENT** | ⭐ **value moved** |
| ≥ 4096 | ≥ 512 | silent | unchanged |

Flip located at exactly 1279 → 1280: **the redzone on this object is 32 bytes**,
which reproduces `.temp/mgr166/asan_reach.c` **on a frame the manager did not
control**. The row ships one adversarial input on each side of that cliff,
differing in one number.

⚠ **The oracle's completeness range is `1024 ≤ idx < 3072`** and the row states
it rather than assuming one. `escaped` counts what leaves the block: 64 and 128
on the two adversarial inputs.

## 6. ⭐ THE HEADLINE ASYMMETRY — MEASURED

`controls/miri_vs_asan.py`, four controls, all green:

```
ASan+UBSan on c/kernel.c (R1), gcc -O1        -- the gate's own arm
   adversarial-redzone   exit=1  fired=True   stack-buffer-overflow
   adversarial-silent    exit=0  fired=False
   small (benign)        exit=0  fired=False

Miri on unsafe.rs, n_iters -> 4 as check.py does
   MUTANT (guard b deleted)  adversarial-silent   exit=1  fired=True
   MUTANT (guard b deleted)  adversarial-redzone  exit=1  fired=True
   MUTANT (guard b deleted)  small (benign)       exit=0  fired=False
   SHIPPED unsafe.rs         all three            exit=0  fired=False
```

**The same defect, at the same index, is invisible to the C detector and visible
to the Rust one.**

⚠ **The mechanism, read off the diagnostic rather than guessed:**

```
error: Undefined Behavior: `assume` called with `false`
  --> unsafe_noguard.rs:48:15
48 |     unsafe { *a.get_unchecked(i) }
   |               ^^^^^^^^^^^^^^^^^^
```

Miri catches it inside `core::slice::get_unchecked`'s own
`assert_unsafe_precondition!`, **before any address is formed**. ASan has
nothing analogous to catch: C's `FD_SET` carries no precondition and the address
it forms is a legitimate live object. **So the asymmetry is about WHERE THE
BOUND IS WRITTEN DOWN — Rust in a contract, C nowhere — and not about one
checker watching memory harder.** I had first written the provenance story; the
diagnostic says otherwise and the control now says what the diagnostic says.

⚠ It is a **control, not a rung**: the shipped R4 carries guard (b), so Miri has
nothing to find there. And there is **no safe-Rust program that can carry this
defect at all** — `[u64; 16]` out of bounds panics — which is itself part of the
result.

## 7. What each guard buys — `controls/fix_scope.py`

```
Q1  the SHIPPED BENIGN corpus     small.bin  (a) 0  (b) 0  (c) 0
                                  large.bin  (a) 0  (b) 0  (c) 0
Q2  1536 synthetic windows
      R1 (no guards)        out-of-bounds writes 2880   max_fd out of range on 880
      R1 + (a)                                   2880   -- (a) fired 0
      R1 + (b)                                      0   -- (b) fired 2880
      R1h (a+b+c)                                   0
      b_too_wide (fd<2048)                       1440   <- must-fire INCOMPLETE control
Q3  guard (a) fired 0 times over the WHOLE domain
Q4  (b) alone still differs from (a+b+c) on 880 of 1536 windows
```

⭐ **The fix is COMPLETE** — which licenses R2–R5 implementing R1h's function.
⚠ **That makes `ph16` the counter-example to `.memory-php/02-ladder.md`'s
*"of two shipped security fixes, NEITHER WAS MINIMAL NOR SUFFICIENT AS
SHIPPED"*.** `ph03`'s was half dead and half incomplete, `ph07`'s was half a bug
upstream deleted; **`ph16`'s is neither.** n is now 3, and the sentence needs its
n said.

⚠ **Guard (a) is DEAD on this kernel's domain and the row measures it rather
than banking it** (`this_fd` is a 14-bit field). Negative `this_fd` is out of
contract for a measured reason: `FD_SET(-1, …)` is `1UL << -1`, UB **in the
shift** rather than the out-of-bounds **write** this row models. It is a
`PLAN_PHP.md` §3.1 variation and its own row.

## 8. The ladder, and a mechanism for the number

`results-php/ph16-fdset-index.json`, O3/isolated, `kernel_exclusive_ir`.
⚠ **Within-row ratios only** (`.memory-php/03-numbers.md`).

| rung | `large.bin` | vs `c-gcc` | `small.bin` | vs `c-gcc` |
|---|---:|---:|---:|---:|
| `c-gcc` (R1) | 317 708 014 | — | 92 081 388 | — |
| `c-clang` (R1) | 320 046 417 | +0.74 % | 90 365 805 | −1.86 % |
| `safe_naive` (R2) | 416 298 533 | **+31.03 %** | 118 269 785 | +28.44 % |
| `safe_tuned` (R3) | 305 508 386 | **−3.84 %** | 88 874 724 | −3.48 % |
| `unsafe` (R4) | 311 246 696 | −2.03 % | 89 974 452 | −2.29 % |
| `verus` (R5) | 311 246 696 | −2.03 % | 89 974 452 | −2.29 % |
| `c-gcc-h` (R1h) | 352 560 086 | **+10.97 %** | 101 993 201 | +10.76 % |
| `c-clang-h` (R1h) | 341 130 813 | +7.37 % | 95 936 934 | +4.19 % |

⭐ **`verus` is byte-identical to `unsafe`** — `md5_fn 659d7b4b4168`, 425
instructions, 1775 bytes, gate pin `identity: exact`. **The proof costs nothing
at run time.**

**⭐⭐ The mechanism for +10.97 %, off `objdump`:** the hot per-entry loop is 19
instructions in R1 and 21 in R1h — **+2 on 19 = +10.5 %** against a measured
+10.76 / +10.97. And the two instructions are not the ones you would write: gcc
turned `this_fd < FD_SETSIZE` into **`test $0x3c,%ch`** — a bit test on bits
10..13 of the *raw entry word*, before `this_fd` is ever materialised. **The
compiler proved the guard without computing the quantity it guards.** Guard (a)
vanishes entirely (§7's deadness, confirmed in codegen); guard (c) is branchless
and once per call (`mov $0x3ff,%ecx; cmp; cmovle`). `NOTES.md` §8a has both
listings.

**⚠ `safe_naive` at +31 % is NOT "the bounds-check tax".** It is *one redundant
bounds check per entry*: R2 writes the C's own `this_fd < FD_SETSIZE` and then
indexes with `this_fd / 64`, which rustc must check again; R3 writes
`let w = this_fd / 64; if w < NW`, the same predicate, and there is nothing left
to check. `controls/guard_equiv.py` proves the equivalence over all 16 384
reachable values against a build of the C, with four negatives (including an
off-by-one mutant **located** at exactly 1024, which is the value
`adversarial-redzone.bin` is built on). ⚠ **It is a check MOVED, not deleted.**

**⚠⚠ AND ONE COLUMN IN THE PUBLISHED TABLE IS NOT A SAFETY EFFECT.** `vec`,
O3/isolated: **both gcc cells vectorise nothing and every other cell uses
`xmm`**. The vectorisable work is the three `FD_ZERO`s — 384 bytes of zeroing
per call — and rustc and clang emit SIMD stores where gcc does not. So
`safe_tuned` at −3.84 % against `c-gcc` is **not purely** §8b's respelling: part
of it is codegen on a term that has nothing to do with safety. It cancels in
every Rust-vs-Rust delta and does not cancel in the C-vs-Rust one.
`.memory-php/02-ladder.md` records the same trap on `ph03`.
⭐ **What survives it is the +10.97 % R1-vs-R1h figure**, because that compares
two gcc cells differing only in the guard, with the mechanism read off their
disassembly. **That is this row's headline cost number; the Rust-vs-C ones are
not.** `NOTES.md` §8b-bis.

**⚠⚠ `R3ship − R4ship` is NEGATIVE here** — `safe_tuned` is 1.84 % *cheaper*
than `unsafe` on `large.bin`. **Do not publish it as a bound**: neither side has
been searched (§9).

## 9. ⚠⚠ WHAT I DID NOT DO — `controls/spellings.py`, AND THE ANSWER TO §6.2

**`controls/spellings.py` was NOT built. This turned into two tasks and I am
stopping at a green row with the debt declared**, which is what `TASK_PHP_025`
§6.2 asked for explicitly.

What it cost instead: **two full re-measures** (one for the R1h restructure in
§11, one for a corrected comment in a measured source), **seven gate rounds**,
and six controls each with its negatives. The debt is now **three rows old**
(`ph03` owes both sides, `ph16` owes both, `ph07` has discharged it).

⭐ **The row is a better candidate for that search than either predecessor**,
and the reason is in the numbers: `R3ship − R4ship` is **negative** here, so the
"minimum can only fall" arithmetic `.memory-php/02-ladder.md` describes points
the other way for once. `NOTES.md` §8c states that no figure in this row is a
`fixed-R4 bound`.

Also not done:

* **no tag-by-tag bisect of the `fix_commit`.** `provenance.fix_commit` is
  `index.csv`'s value; its patch adds the guard at `:541`; the code is unguarded
  at 5.0.0 and guarded at 5.1.0. `PROTOCOL_PHP.md` §F5(iii) asks for the tags —
  this row confirms the **window**, not the exact commit, and
  `fix_commit_note` says so.
* **no adjudication of the three uncatalogued sibling sites** (§12).
* **`adversarial-far.bin`** designed and dropped — `reach.c` showed a sweep past
  3072 hits the stack protector, so it would record "the layout beyond the
  frame", which the row does not model.

## 10. Gate

**The row gates GREEN.** Key stage results, from the transcript:

```
2.   checksum agreement across every cell   -- all 16 O0+O3 x isolated+whole cells
                                               against model.py, both benign inputs
3b.  marginal Ir per call 3331...213226, all above the derived floor
     (tightest margin 24.2x over 0.25 Ir/byte); d(Ir)/d(work) 6.57...52.76
3c.  unsafe vs verus O0: differ (527 vs 488)
     unsafe vs verus O3: EXACT  (md5_fn 659d7b4b4168, 425 insns, 1775 B)
7.   adversarial-redzone.bin  sanitizer fired as declared (exit=1)
                              ERROR: AddressSanitizer: stack-buffer-overflow
     adversarial-silent.bin   clean, exit=0  <- DECLARED clean; this is the row
     small/large              clean, match the model
7h.  R1h clean under ASan+UBSan on all 6 input(s), adversarial included
8.   miri unsafe.rs: no UB on all 6 inputs, every stdout matches the model
0b.  idiom: 0 pin nothing, 9 scoped-absent, forbidden 0 hits over 10 spellings
```

⚠ **`adversarial-silent.bin` is declared `sanitizer_expect: "clean"` and the
gate agrees.** That is not a hole in the row — it is the row. `model.py` derives
the expectation from ASan's *redzone*, not from the defect, and says so in terms
(§5, `NOTES.md` §3d).

## 11. ⚠ A defect I introduced and then measured out

R1h's first version computed `PH16_IDX(e)` **before** the tag test, to spell
upstream's `&&` literally. That made `c/kernel_hardened.c` differ from
`c/kernel.c` by an assignment as well as by the safety lines, which
`PLAN_PHP.md` §3 criterion 4 forbids. Restructured to a nested `if` (same
predicate, same short-circuit, minimal diff) and re-measured:

```
c-clang-h vs c-gcc, large.bin   before +24.73 %   after +7.37 %
c-gcc-h   vs c-gcc, large.bin   before +10.97 %   after +10.97 %
```

**17 points of the clang R1h figure were my extra work and none of gcc's was.**
Had it shipped, the row would have published a guard cost that was 3.4× the real
one on one of its two C compilers.

## 12. Out of scope, and one paragraph on it (as the task asked)

`99e290f882c9` patches **four** unchecked fd-set sites and the catalogue has
**one**. Reading the patch confirms the manager's census — `:541` (write, this
row), `:577` (`FD_ISSET`, read, no row), `ext/sockets/sockets.c:536` and `:563`
(no rows; `sockets.c` has none at all). **I do not adjudicate them.** What my
reading adds is one fact that bears on all four: **the fix is three macros, not
two**, and the third (`PHP_SAFE_MAX_FD`) is *per-`select`-call* rather than
per-site — so whatever `TASK_PHP_026` decides about the other three sites, they
share a caller-frame guard with this one and the `_019`/`§G` "same fault
primitive" question should be asked about **`PHP_SAFE_FD_SET` vs
`PHP_SAFE_FD_ISSET`** (write vs read) rather than about the commit.

## 12a. ⚠ FIVE `contract_sha256` MOVES, ALL DISCLOSED

`NOTES.md` §0 is the table. In summary, and the shape matters more than the
count: **two moves were the gate refusing me, two were me repeating my own
mistake inside the text that fixed it, and one was a numeral no check looks
at.**

| # | what | found by |
|---|---|---|
| 1 | `forbidden` prose backticked `sizeof(fd_set)` / `wfds` / `efds` → 14 refusals; `aget_unchecked` needed a justification | **the gate** |
| 2 | `7.01 Ir/FD_SET` (×4 places) and `426` / `533` / `501` instruction counts | **measurements**, `controls/fortify.py` and the record |
| 3 | `required[2]`/`[3]`/`[5]` pinned 18 spellings no rung has | **the gate's audit** |
| 4 | the note fixing move 3 backticked `pins_nothing` and re-pinned the guard pair on the C side | **the gate's audit, again** — and leaving it would have made move 3's own disclosure FALSE |
| 5 | `divergences_note` said "SEVEN of these thirteen" against **EIGHT of TWELVE** | **`NOTES.md` §12's numeral sweep** — nothing mechanical looks at a note's count of its own list |

⚠ **AND EACH MOVE COSTS `gate → report → gate`, NOT `report → gate`.** I paid
that twice by getting it the wrong way round: the published table's *"cites
contract"* line is read from `results/gate/<row>.json` — **the LAST GATE's
record** — not from `spec.md`, so a render taken straight after a contract edit
cites the *previous* hash and the next gate's stage 9c refuses it. The
`PROTOCOL.md` chain is written down and I still had to be shown it by the gate.

⭐ **Move 5 is the one worth carrying out of this task.** `PROTOCOL.md` rule 6's
addendum says a frozen declaration is evidence about *when* it was written, not
about whether it is still true — and the case it was written for is a
*measurement* going stale. This is the other case: **a sentence that COUNTS the
block it lives in**, which goes stale when the block is edited and whose hash
still matches because nobody edited the sentence. `.temp/php25/fix_divcount.py`
recomputes both numbers from the block instead of hard-coding them.

## 13. CLEAN NEGATIVES — attacks that did NOT land

Worth as much as the findings, and they stop the next agent re-running them.

1. **"The corrupted checksum is really `max_fd`, not the write."** Tried, and it
   is not: `controls/oracle.py --only max-fd-alone` predicts
   `3831935670616942592` / `7552720107290115072` against measured
   `16790048728120879104` / `13722268663371347968`. The write contributes and is
   separable.
2. **"The layout prediction would match anything."** Tried: predicting with the
   *other* compiler's measured layout fails on both adversarial inputs, both
   directions. The prediction is sensitive to the ordering.
3. **"An impossible layout is the sharp control."** Tried and **withdrawn**: with
   the three sets 64 words apart every out-of-range write escapes the folded
   words, so that prediction collapses onto `max-fd-alone` and the two negatives
   become one negative twice. Replaced by the other-compiler layout.
4. **"`fd < 512` is the incomplete-fix control."** Tried and **wrong-headed**: a
   *stricter* bound cannot leave a residue, and `fix_scope.py` reported FAIL and
   was right to. The incomplete variant of a bound is a **wider** one
   (`fd < 2048`, residue 1440).
5. **"A tautological `ensures` verifies, as `.memory/04-verus.md` says."** Tried:
   on this row it **fails**, in `main`'s `while` loop, because the driver's
   `assert(r == fdset_fold(...))` consumes the postcondition. The vacuity
   baseline needed a *second* mutant with that assert deleted (`tautology-un`,
   15/0). **The consuming assert is load-bearing here, with a number.**
6. **"The `mask` mutant disagrees in the WORD column."** Predicted in a
   docstring, **measured false**: it disagrees 15 360 times in the *verdict*
   column, because masking makes the spelling write for every index. Docstring
   corrected; the word column is an unexercised half of that comparison on this
   row and is kept for the failure it exists for.
7. **`_FORTIFY_SOURCE` as a "third configuration control"** — the task file
   offered it that way. It is not a control here; **it is on by default in one
   of the four measured C cells** and had to be turned off in the row itself.
8. **The `volatile` canary** — the task file's constructive answer. Not needed,
   and now **forbidden**: PHP's own frame supplies two live witnesses.
9. **A heap `fd_set`** — not attempted. `TASK_PHP_025` §3 says it changes the
   storage class the row is about and `ph17` is catalogued as that variation.
10. **`grep` vs `ugrep`** — `-a` used throughout. `streamsfuncs.c` decodes as
    UTF-8, so the trap did not fire on this row; the discipline was kept anyway.

## 13b. ⚠ ONE COMMITTED FILE MOVED THAT IS NOT MINE TO MOVE

`git status` after the closing bracket:

```
M  results-php/preflight/_norow.preflight.json     <- the bracket's own run
?? patterns-php/ph16-fdset-index/                  <- the row
?? results-php/{gate/,}ph16-fdset-index.json
?? results-php/preflight/ph16-fdset-index.preflight.json
?? results-php/tables/ph16-fdset-index.md
?? .tasks-php/TASK_PHP_025_REPORT.md
?? results-php/preflight/ph07.preflight.json       <- NOT MINE, see below
```

`_norow.preflight.json` is a **committed** file and
`harness-php/gate.py --tool measure --check-stale` appends to it — the closing
bracket did that, and so did the opening one. `PROTOCOL_PHP.md` §E documents it
(*"not read-only: a FAILING run grows a COMMITTED file"*); here it grew on a
run that PASSED, which the section's wording does not quite cover.

⚠ **`results-php/preflight/ph07.preflight.json` is UNTRACKED and is NOT mine.**
Its mtime is **14:25**, before this task started (~15:40) and I never passed
`ph07` to the gate. It is the short-name record from the manager's own `ph07`
re-gate earlier today. **Flagged so it is not attributed to this row.**

**Nothing under `harness/`, `common/`, `patterns/`, `results/`, `pilot/` or
`.web/` was created, edited or deleted, and neither was `RECAP_PHP.md`,
`.memory-php/`, `patterns-php/CATALOGUE.md` or
`patterns-php/ph07-strcut-cursor/`.** No `git add`, no `git commit`.

## 14. ⚠ Harness observations — reported, NOT acted on

**Nothing under `harness/`, `common/`, `patterns/`, `results/` or `pilot/` was
touched.** Two things a reviewer may want:

1. **`vparse` truncates a `requires`/`ensures` clause at the first `{`.** An
   `ensures` written with an `if … { … } else { … }` block expression derives as
   a **prefix** — mine came out as `"r == if not_an_array"`. Verus is unaffected
   (it reads the source), but the `spec.md` item pin would have under-described
   the contract *and the gate would have compared it and passed*. Worked around
   by routing the conditional through two spec helpers (`arm_sets`,
   `arm_state`); no clause in the shipped `verus.rs` contains a brace. **Minor,
   and it is a false-PASS shape rather than a false-fail.**
2. **`idiom.forbidden` bans every backticked span in the entry, including the
   prose.** Known and documented in `check.py`; this row is the first to *fire*
   on it — 14 refusals because my entries quoted `sizeof(fd_set)`, `wfds` and
   `efds` while explaining what they protect. Fixed in the row, and
   `forbidden[1]` now says so in its own text so the next author reads it.

---

## 15. ⚠⚠ A DEFECT IN MY OWN REPORTING, CAUGHT BY RE-RUNNING

**`reach.c`'s first version aborted before it printed the two verdicts I had
already written down.** The Q4 sweep ran to index 8192, walked past the three
`fd_set`s into the stack protector, and died with
`*** stack smashing detected ***` **after** Q4's flip lines and **before** Q4's
summary and the whole of Q5. I had put `Q4 oracle fires over [1024, 3064]` and
`Q5 PASS …` into the row's `NOTES.md` §5 **from what the probe was designed to
print**, not from what it printed.

Caught late, by re-running the probe to confirm the transcript rather than
trusting my own paste. The sweep now stops at 3071 — out-of-frame behaviour is
`oracle_sweep.c`'s and `controls/fortify.py`'s job — and the real output is:

```
Q1 PASS  R1 == R1h on benign input, nothing corrupted
Q2 PASS  R1 corrupts a set no legitimate FD_SET could reach; R1h does not.
         THE VERDICT MOVES WITH THE GUARD (F52).
Q3 PASS  the corruption is visible in the RETURNED u64
Q4       oracle fires over index [1024 .. 3064] (step 8, sweep 0..3071)
Q4 PASS  complete exactly over [1024, 3072)
Q5       benign sweep idx 0..1023: R1 corrupt on 0, R1 != R1h on 0
Q5 PASS  the upstream guard is DEAD on the whole benign domain
RESULT: PASS
```

**Both verdicts turned out to be TRUE, which is exactly what makes the mistake
worth reporting**: the numbers were right and the process that produced them was
not, and nothing in the gate, the controls or the review checklist would have
caught it. `NOTES.md` §5 carries the disclosure. ⚠ **A transcript written from a
probe's intent rather than its output is the same defect as a stale figure, one
step earlier** — and it is the shape `.memory-php/04-process.md`'s standing
warning describes: *the citation and the story about it are two different
claims.*

⚠ **Related, and it is why the polls in this task took so long:** foreground
`sleep` is BLOCKED in this environment, so `until … sleep 30 …` loops return
instantly and a shell "wait" measures nothing while reading exactly like a
completed wait. Backgrounded `Bash` tasks (one completion notification) are the
working spelling. Recorded in `.temp/php25/NOTES.md` §11.

---

## 16. What the manager asked to be judged rather than assumed

| § | question | answer |
|---|---|---|
| §1 | **the TIER** — decide it from `PLAN_PHP.md` §4's definitions and say which test you applied | **`narrowed`**, from the DEFINITION. The M4 enclosing-frame test says `verbatim` and is the wrong test here — this row is the case that separates them. `CATALOGUE.md` still says `verbatim` and I could not edit it. Report §4, `NOTES.md` §1a. |
| §3 | **the ORACLE is measured, not guessed** — and *"if honouring the tier costs you the oracle, say which you dropped"* | **Neither was dropped.** The canary was not needed at all: `stream_select`'s own `wfds`/`efds` are the witnesses, and `idiom.forbidden[2]` now BANS a canary. The oracle **predicts R1's corrupted checksum bit for bit under both compilers** from the measured layout, with three negatives. Report §5. |
| §3 | **if R4-under-Miri catches what R1-under-ASan cannot, that is the headline** | **It does, measured.** ASan silent at index 2048 on R1; Miri fires on an R4 mutant at the same index. ⚠ The mechanism is `core::slice::get_unchecked`'s own precondition assert, not provenance — read off the diagnostic. Report §6. |
| §4.1 | **`controls/spellings.py` from the start, both sides** — *"if carrying it turns this into two tasks, say so and stop at a green row with the debt declared"* | **It turned this into two tasks and I stopped.** Not built; declared in `NOTES.md` §8c/§11, `README.md` and report §9. **No figure in this row is a `fixed-R4 bound`**, and `R3ship − R4ship` is NEGATIVE here, which makes the search more interesting than on either predecessor. |

## 17. For `.memory-php/` — durable facts this row measured

Manager-only to write; offered here as candidates.

1. ⚠⚠⚠ **A ROW CAN INHERIT ITS OWN SAFETY CHECK FROM THE TOOLCHAIN.** Ubuntu's
   gcc adds `-D_FORTIFY_SOURCE=3` at `-O2+`; glibc's fortified `FD_SET` is
   `__fdelt_chk`. Measured on `ph16`: `c-gcc-O3` aborts on the adversarial input
   and charges **14.87 Ir per BENIGN `FD_SET`, +60.6 % whole-program**.
   **`PROTOCOL_PHP.md` §A1's substitution rule is written for what the
   EXTRACTION changes; this is a thing the extraction did not change and the
   toolchain did, and only running the binary can see it.**
2. ⭐⭐ **`.memory-php/02-ladder.md`'s *"of two shipped security fixes, NEITHER
   WAS MINIMAL NOR SUFFICIENT AS SHIPPED"* now has its n = 3, and the third is
   the counter-example.** `99e290f882c9` is COMPLETE and minimal for the
   memory-safety defect: 2880 of 2880 illegal writes removed, no guard firing on
   any benign window. **It is also THREE guards on POSIX, one of them in the
   caller's frame and not about the write at all.**
3. ⭐ **A CALLER'S OTHER LOCALS CAN BE THE ORACLE, AND THEY BEAT A CANARY.**
   `stream_select`'s three `fd_set`s make a strided over-write observable in the
   function's own return value, with no scaffolding — and the row's control
   PREDICTS the corrupted checksum from the frame layout rather than
   differencing two rungs, which is what keeps `max_fd` from being mistaken for
   the memory error (F52).
4. ⚠⚠ **ASan's REDZONE, not the defect, is what decides `sanitizer_expect` when
   the over-write is STRIDED.** 32 bytes on this frame, measured: index
   1024…1279 reported, 1280…3071 silent. A contiguous run cannot miss a redzone;
   a strided single word can. That is also why `echoes: p02` is a
   cross-reference and not a duplicate.
5. ⚠ **`vparse` truncates a `requires`/`ensures` clause at the first `{`**, so a
   clause containing a block expression pins only a prefix — and the gate
   compares the prefix and passes. A false-PASS shape. Worked around in the row;
   `harness/` untouched.
6. ⚠ **A `forbidden` entry bans every backticked span in its own PROSE.**
   Documented in `check.py`; `ph16` is the first row to fire on it (14
   refusals), and the same mistake recurred inside the text that fixed it.
   **Write forbidden prose without backticks.**
7. ⚠ **Foreground `sleep` is blocked in this environment**, so `until … sleep`
   poll loops return instantly and read exactly like a completed wait.

---

## Gate transcript

`.temp/php25/` carries every log: `01-build`, `02-measure`, `03-build2`,
`04-measure2`, `05-gate1`, `06-build3`, `07-measure3`, `08-gate2`, `09-report`,
`10-gate3`, `11-report2`, `12-gate4`, `13-report3`, `14-gate5`, `15-report4`,
`16-gate6`, `17-report5`, `18-gate7`.
