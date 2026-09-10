# TASK_PHP_027 — engineer report: `ph29-recvfrom-alloc`, row 4

**Role:** research engineer, alone. **Written to the file first** (rule 10).

---

## §0 The staleness bracket

**FIRST**, before anything was touched:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
8 record(s) examined, 0 STALE
```

**LAST**, after everything:

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph29-recvfrom-alloc.json      38 source(s)
FRESH       results/ph29-recvfrom-alloc.json           19 source(s) + 6 input(s)
10 record(s) examined, 0 STALE
```

⚠ **The php figure is 10/0, not the 8/0 the task file brackets and not the 9/0
I predicted while drafting this report.** A row adds **two** records, a
measurement one and a gate one, and I wrote 9 without counting. The PAT figure
is **66/0** at both ends, which is the half that proves nothing frozen was
touched.

---

## §1 What was built

`patterns-php/ph29-recvfrom-alloc/`, five rungs + R1h, six inputs, five
controls, all six gate commands run.

| path | |
|---|---|
| `c/kernel.c` | R1 — `PHP_FUNCTION(stream_socket_recvfrom)`, `streamsfuncs.c:300-345`, narrowed |
| `c/kernel_hardened.c` | R1h — + the whole of `445daac3ab1a`, sha-pinned |
| `c/main.c`, `c/kernel.h` | driver TU, shared declaration |
| `c/emalloc_shim.h` | the mandatory unconditional symlink |
| `safe_naive.rs` `safe_tuned.rs` `unsafe.rs` `verus.rs` | R2–R5 |
| `model.py` | three independent implementations + a 176-window synthetic sweep |
| `inputs/gen.py` | 2 benign + 4 adversarial, with `_check_span` refusing a corpus that misses an arm |
| `spec.md` `NOTES.md` `README.md` | contract, measurements, entry point |
| `controls/allocator.{c,py}` | **the row's reason to exist** — shim vs plain `malloc`, both directions |
| `controls/fix_scope.py` | what each stage of the upstream fix removes |
| `controls/fortify.py` | `_FORTIFY_SOURCE`, four arms incl. a must-fire |
| `controls/oracle.{c,py}` | the substitution differential + the detector sweep |
| `controls/negatives.py` | 8 Verus mutants |
| `controls/445daac3ab1a.patch`, `controls/6ac8ffdfea10.patch` | both upstream commits, fetched and pinned |

**Nothing under `harness/`, `common/`, `patterns/`, `results/` or `pilot/` was
touched. No `git add`, no `git commit`. Nothing written to `RECAP_PHP.md`,
`.memory-php/` or `.web/`. Scratch is `.temp/php27/` only.**

---

## §2 The three findings

### F-a ⭐⭐⭐ THE SHIM IS LOAD-BEARING, AND THE ROW PROVES IT BOTH WAYS

`TASK_PHP_027` §6.1's stopping condition — *"if this row can only be made to
fault by a shim behaviour the real `zend_alloc.c` does not have, STOP"* — **is
not met.** The behaviour is one store, transcribed verbatim
(`zend_alloc.c:129` `unsigned int real_size` ← `:135` `REAL_SIZE(size)`), and
`controls/allocator.py --audit` re-derives those three lines **from the tarball
text rather than from the shim** before it runs anything.

`controls/allocator.py`, 18 (case × allocator) cells, **PASS**:

| `to_read` | shim | plain `malloc` | shim + `445daac3ab1a` |
|---|---|---|---|
| `4294967295` (the row's trigger) | **OVERFLOW** | **CLEAN** | **OVERFLOW** |
| `-4294967297` (shipped) | **OVERFLOW** | **ALLOC-REFUSED** | CLEAN |
| `-1` (shipped) | OVERFLOW | OVERFLOW | CLEAN |
| `63`, `4095`, `0` (benign) | CLEAN | CLEAN | CLEAN |

⭐ **The task file's §3 named ONE way the row disappears under plain `malloc`
and there are TWO.** *"`malloc(2^63)` simply fails and PHP exits"* is right for
the negative values. At the row's own UB-free trigger the request is 4 GiB,
plain `malloc` **succeeds**, and the write is in bounds — the defect vanishes
because the request is HONOURED. Opposite mechanisms, same absence.

⚠ **A first draft of that control was wrong in F52's shape** and is recorded as
such in `NOTES.md` §3a: it asked *"did the sanitizer print?"*, and ASan's own
*`requested allocation size … exceeds maximum supported size`* — its allocator
limit, not an out-of-bounds access — scored as the defect firing. The control
now reports three outcomes.

### F-b ⚠⚠ THE UPSTREAM FIX DOES NOT REMOVE THE DEFECT, AND IT IS WRONG IN BOTH DIRECTIONS

Both commits verified **at the commit**, not at the column
(`PROTOCOL_PHP.md` §F5(iii)); both patch files ship under `controls/`.

* **Stage 1 = `445daac3ab1a`** (Ilia Alshanetsky, 2004-07-28, 1 file, +5),
  `if (to_read <= 0) RETURN_FALSE;`. ✅ The corpus column is **right** here,
  unlike `ph12`/`ph21`: right file, right function, right release window. The
  fetched bytes are **byte-identical to the manager's independently cached
  copy** (sha256 `48ac72d1…`, 807 B).
* **Stage 2 = `6ac8ffdfea10`** (Antony Dovgal, 2006-12-25, 1 file, +1/−1),
  `emalloc(to_read + 1)` → `safe_emalloc(1, to_read, 1)`. Found by fetching
  **every** commit touching `ext/standard/streamsfuncs.c` from 2004-07 to
  2009-07 (82) and grepping the patches: exactly two hits, this is the earlier.

`controls/fix_scope.py`, exact arithmetic over a structured 8 227-value domain,
checked against the compiled C on six values, **PASS**:

```
R1 faults on             30
stage 1 alone refuses    10 of those 30
stage 2 alone refuses    12 of those 30
stage 1 + stage 2 refuse 12 of those 30
SURVIVE BOTH             18

Q3b  what does STAGE 2 buy OVER stage 1? 2 value(s): [LONG_MAX-1, LONG_MAX]
```

**→ ANSWER TO §2's QUESTION: stage 1 and stage 2 are NOT the same rung.**
Stage 2's entire marginal contribution is refusing the two values whose
`to_read + 1` is signed-overflow UB in stage 1's spelling. **It removes ZERO
truncation faults in `[1, LONG_MAX − 2]`**, because `_safe_emalloc` checks in
64-bit `long` and then calls the truncating `_emalloc` (`zend_alloc.c:238`).
**R1h ships stage 1 alone**; shipping both would price a checked multiply that
buys nothing this row can observe. Its cost: **+0.124 % / +0.024 %** on gcc and
**−0.221 % / −0.034 %** on clang.

⭐ **And the guard is over-broad and under-broad at once**: it also refuses
`to_read == 0`, which was never a fault (`emalloc(1)` is honoured,
`read_buf[0] = '\0'` is in bounds). 5.0.0 returned `""`; 5.1.0 returns `false`
with `E_WARNING`. `.memory-php/02-ladder.md` records *"half dead and half
incomplete"* and *"half wrong"*; this is a third shape.

⚠ **Consequence for the shipped corpus, stated plainly**: `check.py` stage 7h
requires R1h clean on **every** input, so the arm the fix does NOT close cannot
be an `inputs/` file. It is in `controls/`, which is where
`.memory-php/02-ladder.md` F31 says it belongs. **A green gate on this row does
not mean the fix is complete.**

### F-c ⭐⭐ PHP 5.0.0's SIZE-CLASS CACHE DEFEATS `-D_FORTIFY_SOURCE=3`

§4 asked for this to be checked and not inherited. `controls/fortify.py`, **PASS**:

```
A  gcc -O3 -> FORTIFY_IS_DEFINED;  gcc -O0 / clang -O0,-O3 -> NOT DEFINED
B  ph29's kernel object: 0 fortify _chk across all 8 (compiler x opt x mode)
C  MUST-FIRE: gcc -O3, a heap dest gcc CAN bound, runtime length -> __memcpy_chk
D  V=1 php_shim_emalloc's shape (cache arm + malloc arm) -> NONE
   V=0 the same function with the CACHE ARM DELETED        -> __memcpy_chk
```

**The mechanism is PHP's, not gcc's.** `php_shim_emalloc` has two return paths,
so the pointer reaching `memcpy` is a PHI of two allocations and
`__builtin_dynamic_object_size` of that is unknown. **The same feature that
makes `crashes_pristine_5_0_0 = False` unreliable (`§B1.1`) also disables a
2024 compiler mitigation.** Unlike `ph16`, no rung needs `#undef
_FORTIFY_SOURCE`, and `spec.md` **forbids** one so the finding stays
falsifiable.

⚠ The detector's first draft counted `__stack_chk_fail`, which is the stack
protector, is present at `-O0` where fortify is off, and would have reported
the opposite of the truth. Arm C exists because arm B's silence is otherwise
indistinguishable from a broken detector.

---

## §3 The ladder

`results-php/ph29-recvfrom-alloc.json`, `Ir(kernel)`, **O3 / isolated**,
within-row only:

| cell | `small.bin` | vs `unsafe` | `large.bin` | vs `unsafe` |
|---|---:|---:|---:|---:|
| `c-gcc` (R1) | 39 273 585 | +57.4 % | 120 800 132 | +41.6 % |
| `c-gcc-h` (R1h) | 39 322 352 | +57.6 % | 120 828 536 | +41.7 % |
| `c-clang` (R1) | 28 335 859 | +13.6 % | 86 864 573 | +1.9 % |
| `c-clang-h` (R1h) | 28 273 143 | +13.3 % | 86 835 243 | +1.8 % |
| `safe_naive` (R2) | 28 068 358 | **+12.5 %** | 90 821 295 | **+6.5 %** |
| `safe_tuned` (R3) | 23 441 029 | **−6.1 %** | 79 788 966 | **−6.4 %** |
| `unsafe` (R4) | 24 951 895 | 0 | 85 283 038 | 0 |
| `verus` (R5) | 24 951 895 | **byte-identical** | 85 283 038 | **byte-identical** |

⚠⚠⚠ **`R3ship − R4ship` IS NEGATIVE, so NO figure in this row is a
`fixed-R4 bound`** — the same position `ph16` is in. **Three of four built rows
now owe `controls/spellings.py`**, and `TASK_PHP_028` covers only two of them.

⚠⚠ **Two things in that table are NOT safety effects.** `c-clang` beats
`c-gcc` by **27.9 % / 28.1 %**, larger than any other movement; and **C is
slower than every Rust rung**, because the C rungs run PHP's request boundary
(`php_shim_reset` + `_emalloc` + `_efree` + `php_shim_shutdown`) per call and a
memory-safe translation has nothing for a size-class cache to be. `NOTES.md` §8.

**Verus**: `10 verified, 0 errors` plain, `15 verified, 0 errors` twin, and
⭐ **no `#[verifier::rlimit]` at all** — bisected at 30/10/4/2/1/none, all green
(`ph16` needs 30, `ph07` needs 9). `controls/negatives.py`: 8 mutants, 7
must-FAIL and 1 must-VERIFY, **all PASS**.

---

## §4 The three answers §6 asked for

1. **Does the shim's fidelity survive being tested?** ✅ **Yes** — §2 F-a. The
   store is transcribed, the excerpt is sha-pinned in
   `provenance.extra_spans[1]`, and `--audit` re-derives it from the tarball.
   **The stopping condition was not reached.**
2. **Are stage 1 and stage 2 the same rung?** ❌ **No, and the answer is a
   count of two.** §2 F-b.
3. **Is `narrowed` right when the wrapper coming off is
   `zend_parse_parameters` itself?** ✅ **Yes**, and `NOTES.md` §2 argues it in
   four steps rather than asserting it. The decisive one is that `ph94` needed
   a `projection` because its blob could supply a value the real parse could
   not; **here every `long` the eight bytes can hold is a value
   `stream_socket_recvfrom($s, $n)` can pass**, negatives included.
   ⚠ `UPSTREAM_001.md` §6 had already checked ph29's tier against the M4 frame
   test and agreed; **the two tests agree here where they disagreed on `ph16`**,
   exactly as §1 said.

---

## §5 What I got wrong, and how it was caught

⚠⚠ **NINE declarations were wrong and are corrected. THE GATE FOUND FOUR OF
THEM.** `NOTES.md` §12 is the itemised pass; `PROTOCOL.md` rule 6's addendum is
the rule — a frozen declaration is evidence about *when* it was written, not
about whether it is still true. The four the gate found are the interesting
ones, because I had already re-read the block by hand and missed them.

**Found by the gate:**

-3. ⚠⚠⚠ **`idiom.forbidden[0]` OPENED BY BACKTICKING `to_read + 1` — THE
   EXPRESSION IT EXISTS TO PROTECT — while its own last sentence warned against
   exactly that.** Every backticked span in a `forbidden` entry is a banned
   token, so the gate refused the row twice, once per C rung. **I wrote the
   warning into the entry and then made the mistake in the entry's first four
   characters.** `ph16` lost fourteen obligations to the same shape. **A
   warning placed where the mistake is made does not prevent the mistake.**
-2. ⚠ **After that fix `forbidden` had NO backticked token at all**, so the
   list pinned nothing mechanically — the same defect, quieter. Two
   genuinely-absent tokens added, each verified absent first.
-1. ⚠⚠ **`vcopy_unchecked` shipped a THIRD `ensures` clause with a comment
   arguing it was the important one** (*"the suffix is untouched … without it
   the NUL store could be discharged by a body that had already scribbled over
   the tail"*). `check.py` stage 5b deleted it and the file still verified:
   **an axiom nothing depended on.** Gone, and `NOTES.md` §11d states the
   larger residual that leaves.
0. ⚠⚠ **Two `idiom.required` entries carried a `why` key.** The schema admits
   only `c` and `rust`, so **that text pinned nothing in either language**
   while reading exactly like a pin.

**Found by me, re-reading against the record:**

1. **`verus.rs` shipped `#[verifier::rlimit(30)]`, copied from `ph16` by
   analogy, with a `spec.md` note defending 30.** Nothing had been bisected. It
   verifies with the attribute deleted. **An unearned budget override is a
   claim about proof cost**, and this row's real claim is the opposite one.
2. **`identity[0]` declared `O3: "norel"`** by reasoning about a PLT entry. The
   record says `md5_fn` is `a7adc5d4e32f` in BOTH cells — `exact`.
3. **`identity[0]` declared `O0: "differ"`** by analogy with three other rows.
   The record says the O0 cells differ only in relocations — `norel`. **The
   analogy was to three rows and was still wrong.**
4. ⚠⚠ **`inputs/gen.py` claimed a 5-byte overflow keeps the process alive**, a
   plausible reading of glibc's chunk layout that nobody had run. **All four R1
   cells abort** with `malloc(): invalid size (unsorted)`. Corrected in three
   files; the boundary is now measured by `controls/oracle.py`'s sweep.
5. ⚠⚠ **`NOTES.md` §1 pasted `.temp/php20/ph29_probe.log` — `TASK_PHP_020`'s
   STORED output — under a `$ gcc … && ./ph29_probe` prompt, as though it were
   a fresh run.** I had only `cat`-ed the log. Re-run for real; the numbers are
   byte-identical but the provenance of the paste was not, and §5's rule is
   *"paste output you actually saw"*. The real run also shows a
   `-Woverflow` warning the log does not, from the probe's own
   `LONG_MAX + 1L`.
6. ⚠ **`NOTES.md` §11 first described the overlap's matched lines as *"exactly
   the four the defect is made of"*.** Enumerating them showed two were
   declarations and that **the defect's own line was a MISS** — because the
   kernel spelled it `(char *)php_shim_emalloc((size_t)(to_read + 1))`. Fixing
   the cause was a fidelity gain: a `#define` redirect (`ph03`'s sanctioned
   spelling) makes `read_buf = emalloc(to_read + 1);` and `long to_read = 0;`
   **verbatim**, overlap 9 % → 14 %, **both benign checksums byte-identical
   across the change**, and the ledger gained a twelfth entry.

---

## §6 The kernel-overlap number (§F9 asks for a judgement, here it is)

```
per-span overlap: span0 20% (6/30), span1 0% (0/9), span2 0% (0/4)
kernel overlap 14% (6/43)   tier=narrowed is expected to clear 25%
1 unevaluable conditional: ['#ifndef PH29_KERNEL_H']
```

**14 % against 25 %. The number is right, the tier is right, the expectation
does not fit this shape of row.** `NOTES.md` §11 enumerates all thirty lines
rather than describing them. Two things worth carrying:

* ⚠⚠ **CITING MORE SPANS MAKES THE STATISTIC WORSE.** The denominator is the
  union. `span2` is `zend_alloc.c:128-137` — the truncation itself, the single
  most important citation in the row — and it scores 0 because it lives in
  `c/emalloc_shim.h`, which the heuristic does not read. **A row citing only
  its defect site would score 20 %.** The 25 % expectation is not comparable
  between a one-span row and a three-span row.
* The unmatched 24 are the zval wrapper, the `magic_quotes_runtime` arm and the
  substituted transport call — **which is what `narrowed` means.**

---

## §7 Problems

1. ⚠ **`inputs/adversarial-trunc.bin` and `adversarial-neg.bin` produce
   IDENTICAL output in every rung.** They differ only in the request size
   (`2^64 − 2^32` vs `0`) and both truncate to `real_size = 0`, so the gate
   cannot tell them apart. Their difference is entirely in what a **substituted**
   allocator does, which is `controls/allocator.py`'s business. **The pair is
   shipped deliberately and `NOTES.md` §13 says so**, but a reviewer should know
   the gate gets no extra information from the second one.
2. ⚠ **`model.py` is slow** — the synthetic sweep plus `_dumb` over
   `large.bin`'s 2 050 windows. ⚠ Its first version allocated `[0] * real_size`
   in `_dumb` and took the process to **25 GB RSS** before I killed the exact
   PID; the fix is in the docstring.
3. ⚠ **`controls/oracle.py`'s differential compares the shipped C against a
   READING of `transports.c`, not against PHP.** It catches a transcription
   error, not a misreading. Said in the file's own text; the misreading risk is
   bounded by `extra_spans[0]`'s sha256 instead.
4. **Three re-measures** were paid: one for the `verus.rs` rlimit removal, one
   for the `c/kernel.c` verbatim change, one initial. Each cost ~9 min.

---

## §8 Unsure / not done

* ⚠⚠ **`controls/spellings.py` is NOT built.** `TASK_PHP_027` §5 ruled it out
  and told me to declare the debt: **declared, in `NOTES.md` §8/§14, `README.md`
  and here.** ⚠ **`TASK_PHP_028` covers `ph03` + `ph16`; ph29 makes it three
  rows, and ph29's `R3 − R4` is negative like `ph16`'s**, so the manager may
  want to widen that task.
* ⚠ **Whether `safe_tuned < unsafe` is a real non-monotone ladder or a spelling
  artefact is UNKNOWN** — the same open question `ph16` left.
* **`echoes: ["p25"]` is my judgement, not the catalogue's** (`CATALOGUE.md`'s
  cell for ph29 is empty). `spec.md` offers it as a pointer and says the
  mechanisms differ in the thing that matters.
* **I did not re-adjudicate the catalogue's `ph29` block**; F46 settled it and
  the task said not to re-derive it. I re-ran the probe once and pasted it.
* **I did not run Miri by hand**; `spec.md` declares it required and the gate
  runs it. Its verdict is in the gate record.
* ⚠ **The 4 GiB `malloc` on this box succeeded because of overcommit.** On a
  box with `vm.overcommit_memory=2` the `4294967295` arm of
  `controls/allocator.py` would be `ALLOC-REFUSED` rather than `CLEAN`. The
  control would then still PASS its shim arm and FAIL its plain-malloc
  expectation — **it would report, not silently pass**, which is the right
  failure mode, but the expectation is environment-dependent and I have not
  parameterised it.

---

## §9 Memory updates

**None written.** `.memory-php/` and `RECAP_PHP.md` are manager-only
(`PROTOCOL.md` rule 9: findings go into the row's `NOTES.md` and wait for a
review). Every measured claim is in
`patterns-php/ph29-recvfrom-alloc/NOTES.md`.

**Candidates a reviewer may want promoted**, in order of how much they change
what the next agent does:

1. **PHP 5.0.0's size-class cache defeats `-D_FORTIFY_SOURCE=3`** (F-c). It is
   a property of the *shim*, so it applies to **every future allocating row**,
   and it means F56's `#undef` is a per-row question with a mechanism.
2. **`_safe_emalloc` protects against none of the three truncations** — §B
   already says this; ph29 is the first row to **measure** it, and the number is
   *two values of `to_read`*.
3. **The overlap statistic penalises citing more spans.** A metric property, not
   a row property.
4. **An upstream fix can be over-broad and under-broad in one line.**

---

## §10 The gate

```
$ python3 harness-php/gate.py --tool build   ph29-recvfrom-alloc --all   # 1
$ python3 harness-php/gate.py --tool measure ph29-recvfrom-alloc         # 2
$ python3 harness-php/gate.py --tool report  ph29-recvfrom-alloc         # 3
$ python3 harness-php/gate.py                ph29-recvfrom-alloc         # 4  FAIL (9)
$ python3 harness-php/gate.py --tool report  ph29-recvfrom-alloc         # 5
$ python3 harness-php/gate.py                ph29-recvfrom-alloc         # 6  ...
...
$ python3 harness-php/gate.py                ph29-recvfrom-alloc
check.py: PASS
```

⚠ **It took MORE than the documented six commands** — **five gate runs, four
report renders, four builds and four measures** — because the gate found four
declaration defects (§5, items −3 … 0) and each fix moved `contract_sha256`,
which restarts the `gate → report → gate` chain. ⚠ The fifth run is the one
worth knowing about: **`NOTES.md` is in the gate digest, so correcting §1's
stored-log paste staled the gate record** (`STALE … patterns/ph29/NOTES.md`)
and cost a gate run — no re-measure, no `contract_sha256` move, because
`NOTES.md` is prose outside the fence. Logs: the seventeen numbered files
`.temp/php27/01-build.log` … `17-gate5.log`.

**The five gate runs, in order:** 9 failures → 4 → 2 → PASS → **PASS**.

Final record: `results-php/gate/ph29-recvfrom-alloc.json`, contract
`28a92facffb3`, `failures: 0`, `complete_run: true`.

Selected green lines from the final run (`.temp/php27/16-gate4.log`):

```
== 3c. structural identity R4-vs-R5
    ok   unsafe vs verus O0: norel (md5_fn 2a8f2758f4db; md5_raw equal=False, padding 14/14 B)
    ok   unsafe vs verus O3: exact (md5_fn a7adc5d4e32f; md5_raw equal=True,  padding 1/1 B)

== 3b. marginal Ir per kernel call vs a derived floor
    ok   64 cell/probe pairs: marginal Ir per call 1406...121911, all above the
         derived floor (tightest margin 7.3x over a declared 0.25 Ir/byte)

== 7h. R1h under ASan + UBSan -- clean on EVERY input
    ok   R1h clean under ASan+UBSan on all 6 input(s), adversarial included

== 7.  sanitizers
    ok   adversarial-neg.bin    sanitizer fired as declared (exit=1): heap-buffer-overflow
    ok   adversarial-trunc.bin  sanitizer fired as declared (exit=1): heap-buffer-overflow

== 8.  Miri  (REQUIRED: 4 trusted items)
    ok   miri unsafe.rs on all 6 inputs: no UB, exit and stdout match the model
```

**All five controls re-run against the final tree, after the last source
change:**

```
controls/allocator.py    RESULT: PASS (0 problem(s))     18 (case x allocator) cells
controls/fix_scope.py    RESULT: PASS (0 problem(s))     8227-value domain + a C differential
controls/fortify.py      RESULT: PASS (0 problem(s))     VERDICT: 0 fortify checks -- no #undef needed
controls/oracle.py       RESULT: PASS (0 problem(s))     1920 of 1920 cells agree
controls/negatives.py    RESULT: PASS (0 problem(s))     8 mutants, 7 must-FAIL + 1 must-VERIFY
```

⚠ **`spec.md`'s hashed `why` was written LAST**, after the measurement record
existed, and every numeral in it was re-derived from the shipped record rather
than from the draft that preceded it — `TASK_PHP_027` §5 asked me to say so and
this is that sentence. `NOTES.md` §0 discloses all four `contract_sha256`
moves with what moved in each, and §12 itemises the eight declarations a
measurement refuted.

---

## §11 Tree state, and a CONCURRENCY EVENT AFTER I FINISHED

⚠⚠ **Between my last gate run and this line, someone else ran
`harness-php/gate.py ph29` — the SHORT name — and then staged the row.** It is
not mine: all five of my runs used the full row name, which the logs show
(`grep -ao "check.py ph29[a-z-]*" .temp/php27/1[4-7]-gate*.log` →
`check.py ph29-recvfrom-alloc`, three times). The other run started
`Thu Sep 10 06:38:54 2026` and I waited it out rather than touching anything
while it held the row (`PROTOCOL.md` rule 11's shape, from the other side).

✅ **It reproduces my verdict exactly**, which is the useful part — an
independent invocation, by another actor, on the same tree:

```
results-php/gate/ph29-recvfrom-alloc.json
  contract    28a92facffb3      (= spec.md's, = the published table's)
  failures    0
  complete    True
  invocation  ph29              <- was `ph29-recvfrom-alloc` in my run
```

✅ **Bracket re-taken after it, unchanged: `66/0` and `10/0`, everything FRESH.**
✅ `python3 harness-php/gate.py --audit` → `preflight coverage: complete`, rc 0.

⚠⚠ **BUT IT LEFT A SECOND WRONGLY-KEYED PREFLIGHT, AND THIS IS `RECAP_PHP.md`
F55 FIRING FOR THE THIRD TIME.** The preflight record is keyed by the name
typed, not the row it resolved to:

```
results-php/preflight/ph29-recvfrom-alloc.preflight.json   row key ph29-recvfrom-alloc   7 runs   STAGED
results-php/preflight/ph29.preflight.json                  row key ph29                  1 run    NOT staged
results-php/preflight/ph07.preflight.json                  (also not mine)                        NOT staged
```

⚠ **So the gate record that is staged was WRITTEN by the `ph29` invocation,
whose preflight is in the file that is NOT staged.** The audit still passes,
because my own 7-run `ph29-recvfrom-alloc.preflight.json` certifies the same
tree and IS staged — but the pairing a reader would infer is not the pairing
that happened. **Manager: decide whether `ph29.preflight.json` and
`ph07.preflight.json` should be committed, deleted, or merged, before the
commit. I did not touch either.**

`git status --porcelain` at the time of writing — **the staging is the
manager's, not mine; I ran no `git add`**:

```
A  patterns-php/ph29-recvfrom-alloc/…            (23 files)
A  results-php/gate/ph29-recvfrom-alloc.json
A  results-php/ph29-recvfrom-alloc.json
A  results-php/preflight/ph29-recvfrom-alloc.preflight.json
A  results-php/tables/ph29-recvfrom-alloc.md
M  results-php/preflight/_norow.preflight.json
?? results-php/preflight/ph07.preflight.json      <- not mine, not staged
?? results-php/preflight/ph29.preflight.json      <- not mine, not staged
```

`inputs/*.bin` and `__pycache__/` are gitignored, verified with
`git check-ignore -v`.

⚠ `_norow.preflight.json` is MODIFIED and that is the documented
`PROTOCOL_PHP.md` §E behaviour — *"a FAILING run grows a COMMITTED file"*, and a
`--check-stale` that reports STALE counts as one. It grew during the mid-task
staleness checks.

---

## §12 Scratch

`.temp/php27/`, 1.7 MB after cleanup. Every binary, `.o` and downloaded patch
bundle deleted; `.temp/php27/REFETCH.sh` rebuilds the 82-commit `patches/`
directory from the two `sf_commits*.json` sha lists that stay, and names the
one-line command for every other blob. Kept: `reach.c` (the reachability
probe), `mkspec.py` and `kernel_verbatim.py` (the two one-shot builders, both
of which refuse to re-run over the artefact), the 16 numbered run logs, the
five `final-*.log` control runs, the three `span*.txt` excerpts and the five
`sf-php-*.c` tag fetches.
