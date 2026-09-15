# ph97-optarg-unwritten — NOTES

Measurements, runs and the things a reader has to be told. `README.md` is the
entry point; `spec.md` carries the contract the gate enforces.

> **`PROTOCOL.md` rule 6 disclosure.** The `slb-contract` block's sha256 **as
> first written, before any measured cell was built**, is
>
>     c6bcd425a40b1f4c3f04113043bdf2e878b56515986de50edb1ed9e3966d8abf
>
> computed the way `check.py::read_contract` computes it — the capture KEEPS the
> newline before the closing fence, and the obvious spelling gives a different
> number for every pattern in the tree (`PROTOCOL_PHP.md` §E).
>
> ⚠⚠ **AND IT MOVED ONCE, TO**
>
>     2814106af6631df69d455ed51bb6b6cf7c0ce6bbc057785e058ae7d4db94db11
>
> **for two reasons, both of them the GATE's, both after the first measurement
> and before any gate went green.** Disclosing the scope is the point of rule 6,
> so here it is exactly:
>
> 1. ⛔ **`verus.items` was keyed by ITEM NAME and had to be keyed by FILE.**
>    `{"kernel": {...}, ...}` became `{"verus.rs": {"kernel": {...}, ...}}`.
>    Stage 5a reported `[proof-pin] verus.rs: no item pin in spec.md` and stage 6
>    reported the driver region as *inside something spelled `verus!` that Verus
>    never verified* — **two stages, one missing level of nesting.** The item
>    contents did not change: they are DERIVED from `verus.rs` by
>    `harness/vparse.py`, not transcribed.
> 2. ⛔ **`requires` lost `24 <= len`, because the gate PROVED it was
>    decoration.** Stage 5c-req deleted `REC <= len` from `verus.rs`'s `kernel`
>    and got `47 verified, 0 errors` — no call site had to discharge it and the
>    body never used it. ⭐ **That is a result and not a repair**: the kernel has
>    no minimum-length precondition. `nrec = len / REC` is zero for a short
>    window, the loop does not run, and both the spec and the exec return the
>    same `0`. The driver's `stride_w >= 24` is a structural choice about what a
>    window IS, not a precondition of this kernel.
>
> ⚠ **NOT ONE `idiom.required`, `idiom.forbidden`, `identity`, `miri` or
> `provenance` entry moved**, and no `why` text moved. The two edits are a JSON
> nesting level and a deleted clause the gate itself refused.
>
> ⚠ `git show HEAD:patterns-php/ph97-optarg-unwritten/spec.md | diff -` is
> **vacuous on a new row** and is deliberately not cited: a row lands in one
> commit, so on a clean tree that command always prints nothing and always looks
> like it passed. The recorded hash above is the only evidence, which is why
> rule 6 demands it be written before building.
>
> ⚠⚠ **Rule 6 is necessary and not sufficient** (`p46`, TASK_089_REVIEW): a
> matching hash says the declaration did not move *after* the measurement, not
> that the measurement did not refute it. §12 is the re-read of the hashed `why`
> against this row's own numbers.

---

## §1 ⭐⭐⭐ CRITERION 2, **MEASURED** — the first row in this programme of which that is true

`PROTOCOL_PHP.md` §A3a. Recorded as an EVENT: what was run, on which binary, on
which date, and what came back.

**Date:** 2026-09-15.
**Binary:** `/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`
(`-v` → `PHP 5.0.0 (cli) (built: Aug  5 2026 09:26:33)`).
**Instrument:** `.tasks-php/probes/segaddr.c`, the committed `LD_PRELOAD` shim,
built with the command in its own header. ⚠ The `.so` is scratch and is deleted;
the generator is the citation.

```
$ LD_PRELOAD=<segaddr.so> $ORACLE -n trigger.php      # <?php mb_get_info(); ?>

[segaddr] SIG11 si_code=1 si_addr=(nil)
EXIT=139

$ LD_PRELOAD=<segaddr.so> $ORACLE -n benign.php       # mb_get_info("internal_encoding")
string(10) "ISO-8859-1"
EXIT=0
```

`si_code=1` is `SEGV_MAPERR`; `si_addr=(nil)` is a dereference at offset 0 —
`strcasecmp("all", NULL)` reading the second operand's first byte.
`crashes_pristine_5_0_0 = True`, **executed**.

### ⚠⚠ THE TWO CAUTIONS, AND A ROW THAT OMITS THEM HAS OVER-CLAIMED

1. **Say which build.** That binary is **php-in-safe-rust's oracle build**
   (`-O3 -march=native -flto`, mysql + webext) and **not** a museum-default one.
   A fault address is a property of a build.
2. **A clean run is not evidence of absence** (`RECAP_PHP.md` F3). The converse
   is the new half and is the whole point: a run that faults, executed, **is**
   evidence of presence.

### §1.1 The whole benign domain, on the same binary in the same session

This is the behaviour table the kernel reproduces, and it is **measured** rather
than read off the source:

```
all               => array(4){ internal_encoding:"ISO-8859-1", http_input:"",
                               http_output:"pass", func_overload:"pass" }
internal_encoding => string(10) "ISO-8859-1"
http_input        => string(0) ""
http_output       => string(4) "pass"
func_overload     => string(4) "pass"
ALL               => array(4){...}          <- strcasecmp is CASE-INSENSITIVE
nonesuch          => bool(false)            <- the final `else RETURN_FALSE`, :3250
""                => bool(false)
null              => bool(false)            <- §1.2
array(1,2)        => Warning: mb_get_info() expects parameter 1 to be string,
                     array given ... bool(false)     <- the :3215 guard FAILING
"all","x"         => Warning: mb_get_info() expects at most 1 parameter, 2 given
                     ... bool(false)                 <- the :3215 guard FAILING
exit 0 for every line above
```

⭐⭐ **THE LAST TWO LINES ARE THE ROW'S `F` TICK, MEASURED IN REAL PHP.** The
`:3215` guard is reachable and it fails by **two independent routes** — a wrong
**type** (`zend_API.c:330`) and a wrong **count** (`:511`) — so `RETURN_FALSE`
at `:3216` is a live benign outcome. A kernel whose guard could never fail would
have no guard at all, and the row's entire claim is about a guard that is there.
`inputs/adversarial-typefail.bin` and `inputs/adversarial-toomany.bin` are those
two inputs; `inputs/gen.py::_check_span` refuses a measured corpus that reaches
neither.

### §1.2 ⭐ `mb_get_info(null)` does **not** crash — and that is the claim at run time

`zend_API.c:302-308`: the `'s'` arm's `case IS_NULL:` writes `*p = NULL; *pl = 0`
**only `if (return_null)`**, which the `!` modifier sets. `"|s"` carries no `!`,
so `IS_NULL` falls through to `convert_to_string_ex` — upstream's own comment on
the missing break is *break omitted intentionally* — and `typ` becomes the
**empty string**. Measured: `bool(false)`, no fault.

▶ So *the argument is the null value* and *the argument was not supplied* are
**different states with different behaviour**, and only the second faults. That
is *the guard answers a different question* as a **behavioural** claim rather
than a reading of the source. `inputs/adversarial-nullvalue.bin` is that input
and `model.py::selfcheck` check 5 refuses a model that conflates the two.

---

## §2 ⭐⭐ THE C RUNG REPRODUCES THE ORACLE'S FAULT **AT THE ADDRESS**

Same shim, same day, on `inputs/adversarial-absent.bin`:

```
$ LD_PRELOAD=<segaddr.so> <c/kernel.c, gcc -O1 -g -DSLB_ISOLATED> .../adversarial-absent.bin

[segaddr] SIG11 si_code=1 si_addr=(nil)
EXIT=139
```

Byte for byte the string §1 got out of the PHP CLI. Independently, under ASan:

```
==...==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000000
==...==The signal is caused by a READ memory access.
    #0 ... in ph97_strcasecmp   c/kernel.c:153      <- PH97_LOWER((uint8_t) *b)
    #1 ... in ph97_get_info     c/kernel.c:311      <- mbstring.c:3219
    #2 ... in kernel            c/kernel.c:385
```

and `inputs/small.bin` under the same ASan build is clean.

⭐ **The address is ZERO and not an offset.** There is no struct field to add:
the compare reads the second operand's first byte. That is why this row has no
`offsetof` to pin, and it is the one thing that distinguishes its fault
signature from `ph56`'s `0x14`.

⚠ **The two builds are not the same build**, and the match is therefore about
the *mechanism* and not about the toolchain: the oracle is `-O3 -march=native
-flto`; the kernel above is `gcc -O1 -g`. What is identical is the signal, the
`si_code` and the faulting address.

---

## §3 ⚠ `int typ_len;` — the second unwritten output, and why it is **not** a limb

`mbstring.c:3212` declares `int typ_len;` **uninitialised**, and it is written
only by the same loop at `zend_API.c:537` that never runs. **So the faulting
call leaves TWO outputs unwritten and the code dereferences one of them.**

▶ **It is NOT a second defect on this row, and this note carries that
qualifier deliberately.** Nothing on any path reads `typ_len`: it is
**write-only** in `mb_get_info`, upstream and here. `c/kernel.c` keeps it
uninitialised exactly as upstream does; the four Rust rungs set it to `0`
because Rust has no uninitialised `i32` without `MaybeUninit`, which this row
deliberately does not use (and whose absence is why F97's stage-5c-twin
collision does not recur here). **No rung reads it, so no rung's answer can
depend on it.**

⭐ It is recorded because it is **`ph96`'s mechanism one variable over** — *the
call reported SUCCESS and the output is not there* — and `ph96` is the row that
closes family T6. Read the two together.

---

## §4 ⚠ The four `!= NULL` tests inside `mb_get_info` are **dead upstream**, not only here

`:3221`, `:3224`, `:3227` and `:3230` each test
`mbfl_no_encoding2name(...) != NULL`. That callee cannot return NULL:

```
ext/mbstring/libmbfl/mbfl/mbfl_encoding.c
 259  	encoding = mbfl_no2encoding(no_encoding);
 260  	if (encoding == NULL) {
 261  		return "";
```

▶ So the four arms are unreachable in **any** 5.0.0 build. The kernel keeps both
the tests and the reason, and the measured CLI's `http_input => string(0) ""`
(§1.1) is that line firing: `mbstring.c:726` initialises
`MBSTRG(http_input_identify) = mbfl_no_encoding_invalid`, `mbfl_no2encoding`
does not know that number, and the caller gets `""` rather than NULL.

⚠ **This is a fidelity result, not a divergence.** A row that had "simplified"
the dead tests away would have removed four branches upstream really executes
(they are compiled, they are evaluated, they are just never false).

---

## §5 R1h — the apply, the offset, and the bytes

`controls/r1h_backport.py` re-derives all of this on every invocation. Recorded
here as an **event**, 2026-09-15:

- **The patch BINDS.** `controls/f7326d627962.patch`'s `From` line is
  `f7326d6279629ccd80cc77fa389584f36434a2fd` and its filename is the same
  prefix — so it is **not** one of `RECAP_PHP.md` F115's three mis-bound cached
  patches. Checked before trusting it, not re-fetched.
- **`git apply --check` succeeds** in a standalone `git init` repo over the
  pristine file: `Hunk #1 succeeded at 3216 (offset -13 lines)`. The cached
  patch's pre-image is a later tree (`@@ -3229`), so the offset is expected.
- **Applied for real, the post-image line at `:3219` is, byte for byte:**

  ```
  $ sed -n '3219p' ext/mbstring/mbstring.c | cat -A
  ^Iif (!typ || !strcasecmp("all", typ)) {$
  ```

  ⚠ **The verdict is taken from the BYTES and not from the exit status.**
  `git apply --check` returned 0 on this project before on a run in which
  nothing moved, because the scratch path was gitignored in the enclosing
  repository (`ph55` NOTES §5). `controls/r1h_backport.py` reproduces that trap
  on every run and records whether it fired.
- **`preimage_screen.py --row ph97 --verbose` → `CANDIDATE`, 1 record, 1 id → 1
  commit.** ⚠ `CANDIDATE` is the screen's **positive** label; it is neither
  `INAPPLICABLE-SAME-FILE` nor an exclusion, and the run reports **0**
  `NOT-THE-REPAIR` exclusions, which the tool's own banner says to cite as
  *0 exclusions, not 0*.
- ⭐ **No census, and it is a CLEAN NEGATIVE.** One hunk, one site. `strcasecmp`
  is called at **12** places in the pristine `mbstring.c` and **5** of them are
  this chain; the other 7 are `"auto"`, `"none"` and `"long"` tests on
  configuration values that are never optional parameters.
  `controls/census.py` re-derives that count from the tarball rather than
  asserting it.

### ⭐⭐ THE FIX **WIDENS** THE BENIGN DOMAIN, AND STAGE 7h HAS NOTHING TO REFUSE

`check.py` stage 7h refuses an R1h that **changes benign output**. Here the only
input whose answer changes is one that previously **crashed**:

| input | R1 (`c/kernel.c`) | R1h (`c/kernel_hardened.c`) |
|---|---|---|
| `small.bin` | `9594554053753204562` | `9594554053753204562` |
| `large.bin` | `2871891596321943169` | `2871891596321943169` |
| `adversarial-absent.bin` | **SIGSEGV, exit 139** | `1265852909175663616` |
| `adversarial-typefail.bin` | `7284756796784009216` | `7284756796784009216` |
| `adversarial-toomany.bin` | `7284756796784009216` | `7284756796784009216` |
| `adversarial-nullvalue.bin` | `7284756796784009216` | `7284756796784009216` |
| `adversarial-nowin.bin` | `0` | `0` |

▶ **Stage 7h's verdict on this row is in §9**, quoted from the gate record.
`controls/widened_domain.py` measures the table rather than asserting it, and
`inputs/gen.py::_check_span` refuses a *measured* corpus containing a record
with `num_args == 0` — which is what keeps R1 and R1h identical there.

---

## §6 ⛔⛔ THE COMPARE IS IN THE KERNEL, AND THAT IS A MEASUREMENT DECISION

`kernel_exclusive_ir` (family A1) is **symbol-scoped and structurally excludes
callee work**. `RECAP_PHP.md` F119 measured the consequence on `ph53`: **100 %
of a ±7 Ir swing lived inside a libc `memset` that A1 could not see.** A kernel
whose whole computation sat inside libc `strcasecmp` would therefore read
approximately **zero** in the column this programme publishes — the row would
measure nothing.

▶ So `ph97_strcasecmp` is implemented **inside the measured symbol**, and
`controls/libc_compare.py` builds the libc-calling variant beside it and reports
`inside_share` for both. **Either answer is a result**, and it prices F119's
exclusion directly.

▶ **The consequence for the obligation, stated rather than hidden:** `I12/O3`
reads *a possibly-NULL pointer must not be passed to a callee — **including
libc** — that dereferences it without testing it*. With the compare in-kernel
the *including libc* clause is narrowed to **a callee that does not test its
argument**, which is the obligation's operative half and which
`ph97_strcasecmp` satisfies (it does not test `b`). `spec.md`'s
`provenance.invariant_note` says the same thing inside the hashed block.

**Numbers: §8.**

---

## §7 ⚠⚠ NO RUST RUNG REPRODUCES THE DEFECT — a FINDING, never a problem

`CLAUDE.md` rule 6 is absolute and this section is the deliverable, not an
apology.

**In C the bug is an OMISSION** — a test that is not written. **In Rust
reproducing it takes a COMMISSION**: `typ` is an `Option<&[u8; 21]>` and cannot
be read without being opened, so a rung that wanted the defect would have to
*add* an `unwrap` or an `unwrap_unchecked` on an unguarded value. That is an
extra operation a reviewer would ask about, where the C's defect is the absence
of one.

▶ **Which safe behaviour this row built, and its ground.** All four Rust rungs
handle the absent argument — they implement `c/kernel_hardened.c`'s function,
i.e. the 2005 fix — **because the type system makes that the path of least
resistance and because it keeps the four rungs ONE function**, so the ladder
measures cost rather than semantics. The alternative (a naive R2 that mirrors
the C with `.unwrap()` and panics) is legitimate and is a different row of the
*does the defect survive?* column; this row **builds both alternatives as
controls rather than choosing between them in prose**:

- `controls/rust_bug.py --emit unwrap` — safe Rust, `.unwrap()` on an unguarded
  optional;
- `controls/rust_bug.py --emit unchecked` — the same with
  `unwrap_unchecked()`.

Both are run on `inputs/adversarial-absent.bin` and what each does is recorded
in `controls/rust_bug.json`. **§13 has the table.**

---

## §8 THE NUMBERS, AND THE DECOMPOSITION THE HEADLINE OWES

All from `results-php/ph97-optarg-unwritten.json`. **A1** is
`kernel_exclusive_ir`, callgrind per-function exclusive Ir of the `kernel`
symbol. `small.bin` makes 20 000 calls at 122 B/call; `large.bin` makes 3 000 at
1036 B/call.

⛔⛔ **EVERY PERCENTAGE HERE CARRIES FIVE THINGS** (`RECAP_PHP.md` F108):
STATISTIC · INPUT · OPT/MODE · BASE · and where the base is a C cell, **BOTH C
COLUMNS**. Nothing below is quoted from an `O0` row.

| cell | A1 `small` | A1/call | A1 `large` | A1/call |
|---|---:|---:|---:|---:|
| `c-gcc` (R1) | 38 881 170 | 1944.06 | 48 425 302 | 16 141.77 |
| `c-gcc-h` (R1h) | 38 835 018 | 1941.75 | 48 367 634 | 16 122.54 |
| `c-clang` (R1) | 15 400 757 | 770.04 | 18 682 938 | 6 227.65 |
| `c-clang-h` (R1h) | 15 390 761 | 769.54 | 18 668 620 | 6 222.87 |
| `safe_naive` (R2) | 11 347 522 | 567.38 | 13 195 596 | 4 398.53 |
| `safe_tuned` (R3) | 13 955 912 | 697.80 | 16 527 835 | 5 509.28 |
| `unsafe` (R4) | **11 107 522** | **555.38** | **12 931 596** | **4 310.53** |
| `verus` (R5) | **11 107 522** | **555.38** | **12 931 596** | **4 310.53** |

### 8.1 ⭐⭐⭐ R4 == R5 TO THE INSTRUCTION, ON BOTH INPUTS

Identical A1, and `asm.py` reports the two `kernel` symbols at **558
instructions** each. **The proof costs zero run-time instructions.**

### 8.2 ⚠⚠ THE TWO C COLUMNS DISAGREE BY 2.5× ON IDENTICAL C

`c-gcc` **1944.06** against `c-clang` **770.04** Ir/call (A1, `small.bin`,
`O3/isolated`) — gcc is **+152.5 %** over clang on the same source. A gcc-only
baseline would have overstated C's cost by that factor, which is why every
cross-language line here carries both.

### 8.3 ⛔ THE "TUNED" RUNG IS SLOWER THAN THE NAIVE ONE

A1, `O3/isolated`, base `safe_naive`: R3 is **+22.99 %** on `small.bin` and
**+25.25 %** on `large.bin`. The three iterator pipelines — `zip` over the
compare, `zip().take()` over the frame copy, `iter()` over the name fold — cost
**more** than the indexed `while` loops they replace.

⚠⚠ **THIS IS A COST WITH NO MECHANISM AND THE ROW SAYS SO** (`PROTOCOL_PHP.md`
§F8). The hypothesis is that `zip` over two `slice::Iter`s keeps two live
cursors where the index form keeps one, and that the early `return` inside each
loop defeats the bound-hoisting the pipeline exists for — **but I did not read
the disassembly, and until somebody does, this row has a number and a guess.**
It is recorded rather than tuned away: the row's question is what an idiomatic
port costs, not what the best port costs.

### 8.4 R3 → R4 IS **−20.41 %**, AND NONE OF IT IS THE OPTIONAL

A1, `small.bin`, `O3/isolated`, base `safe_tuned`: **555.38 against 697.80**.
⚠ **That step removes SEVEN checks** (§10), of which the optional's discriminant
is one. Quoting it as *the optional's cost* would be `RECAP_PHP.md` F83's shape
— a whole difference attributed to one named cause. §8.5 is the isolation.

### 8.5 ⭐⭐⭐ THE OPTIONAL'S DISCRIMINANT COSTS **`+0.0000 Ir/call`**

`controls/optional_cost.py` builds two binaries from `unsafe.rs` differing in
**one function body** — `opt_get` as `unwrap_unchecked()` and as `unwrap()` —
and in nothing else:

```
variant                     input        A1 total   A1/call  inside_share
unwrap_unchecked (shipped)  small.bin    11107522   555.376        87.32%
unwrap (checked)            small.bin    11107522   555.376        87.32%
unwrap_unchecked (shipped)  large.bin    12931596  4310.532        88.55%
unwrap (checked)            large.bin    12931596  4310.532        88.55%
```

**Identical, on both inputs.** LLVM elides the checked open entirely, because
the `typ.is_none() ||` disjunct in front of it has already decided the question.

▶ **Together with the compile-time assertion every Rust rung carries —
`size_of::<Option<&[u8; 21]>>() == size_of::<&[u8; 21]>() == 8` — both halves
are measured: the representation is free in BYTES and the open is free in
INSTRUCTIONS.** That is this row's headline and it is the reason to read it.

### 8.6 ⭐⭐ `inside_share` PER CELL, AS A MATRIX, BEFORE THE STATISTIC IS CHOSEN

`inside_share = 100 × A1 / W`, where `W` is callgrind's own `summary:` total for
the same run — the denominator is named because a percentage owes one. Every
figure below is `O3/isolated` and is measured by `controls/inside_share.py` over
the cells `--tool build` produced, not inherited from anywhere:

| cell | `small.bin` A1/call | share | `large.bin` A1/call | share |
|---|---:|---:|---:|---:|
| `c-gcc` | 1944.06 | **98.84 %** | 16141.77 | **99.42 %** |
| `c-clang` | 770.04 | **91.48 %** | 6227.65 | **92.60 %** |
| `c-gcc-h` | 1941.75 | **98.84 %** | 16122.54 | **99.42 %** |
| `c-clang-h` | 769.54 | **91.48 %** | 6222.87 | **92.59 %** |
| `safe_naive` | 567.38 | **87.56 %** | 4398.53 | **88.75 %** |
| `safe_tuned` | 697.80 | **89.64 %** | 5509.28 | **90.81 %** |
| `unsafe` | 555.38 | **87.32 %** | 4310.53 | **88.55 %** |
| `verus` | 555.38 | **87.32 %** | 4310.53 | **88.55 %** |

⚠ **THIS TABLE IS EIGHT INDEPENDENT PER-CELL RATIOS AND IS NOT A COMPARISON.**
`inside_share` is *how much of a cell's own work is inside its own kernel
symbol*; a `c-gcc` share above a `verus` share says nothing about which is
faster. **Both C columns are present** so that no reader takes it as one, and
the cross-language figures this row does publish are in §8.2–§8.5 with their
bases named.

⛔ **A HIGH SHARE IS NOT A CERTIFICATE.** `ph55`'s `c-gcc` and `c-clang` cells
sit at 74–83 % and A1 still read `0.000 %` on that row's own defect site
(`RECAP_PHP.md` F109). What matters is whether **the DIFFERENCE** lands inside
the symbol. Here the two differences the row rests on (§8.1, §8.5) are **exactly
zero**, and the non-zero ones (§8.3, §8.4) are same-language A1 ratios at
87–99 %. ▶ **A1 is the resolving statistic for this row.**

⭐ **The row's narrowest band is 87.3 % (`unsafe`/`verus`, `small.bin`) and its
widest is 99.42 % (`c-gcc` and `c-gcc-h`, `large.bin`)**, and the spread is
itself readable: `c-gcc`, `c-clang`, `c-gcc-h` and `c-clang-h` keep more of
their work inside the kernel symbol because the Rust rungs' driver does more
(`Vec`, the file read); and `c-gcc-h` / `c-clang-h` match `c-gcc` / `c-clang` to
two decimal places, which is the one-line fix costing nothing, in a third
statistic.

⚠ **The whole-program column is in the record and is not hidden**:
`main_exclusive_ir` in the `whole` cells on `small.bin` reads `c-gcc`
38 576 026, `c-clang` 14 974 013, `unsafe` 11 334 476, `verus` 11 314 474. It
moves the picture by under 1 pp and is not quoted to more than 2 dp anywhere.

⭐ **And the libc control's pair is the same statistic doing its job**
(§6): moving the compare out of the kernel takes `c-gcc`'s share from
**98.84 %** to **64.50 %** — both C-cell readings, same compiler, one variable.

### 8.7 ⛔ NO FAMILY-B FIGURE IS PUBLISHED BY THIS ROW

`marginal_ir_per_call` differences are exposed to the probe `argv`'s stack
alignment (`PROTOCOL_PHP.md` §B5), and **this row publishes none**, so the sweep
is not owed by anything written here. ▶ **A later task that quotes one from this
record owes `.tasks-php/php50_align_sweep.py` and TWO verdicts — *magnitude
resolvable?* and *sign stable?* — and this row has not paid that.**

---

## §9 THE GATE

`python3 harness-php/gate.py ph97-optarg-unwritten`. The verdict is in
`results-php/gate/ph97-optarg-unwritten.json` and is quoted from there, by name,
in `.tasks-php/TASK_PHP_056_REPORT.md` §16 — deliberately not here, because
stage 9c renders this tree against the record being written and a verdict copied
into a gate-hashed file is an input to its own checker.

**What stage 7h did with the widened benign domain: NOTHING, and that is the
right answer.** 7h refuses an R1h that CHANGES benign output. The only input
whose answer moves is `adversarial-absent.bin` — the one R1 **faults** on — and
`controls/widened_domain.py` measures **0 disagreements** between R1 and R1h on
every input where R1 does not fault, across both compilers. `inputs/gen.py`
is what keeps it that way: it refuses to write a *measured* corpus containing a
record with `num_args == 0`.

**What stage 7 (ASan + UBSan) did:** `adversarial-absent.bin` fired as declared —
`runtime error: load of null pointer` at `c/kernel.c:167`, which is the compare's
second-operand read — and every other input is clean. `model.py::sanitizer_expect`
derives `fires` from *some call the driver makes reaches `:3219` with `typ ==
NULL`*, never from a table.

---

## §10 THE TRUSTED SURFACE — seven items, one argument each

`verus.rs` carries **nine** `external_body` items. Seven are accessors with
verified twins; `load_input` and `emit` are I/O and have none (`println!` is not
verifiable).

| # | item | `requires` | what it rests on |
|---|---|---|---|
| 1 | `opt_get` | `t.is_some()` | ⭐⭐⭐ **the 2005 fix.** Nothing else. |
| 2 | `aget` | `i < NTYP` | the compare loop's own bound |
| 3 | `fset` | `i < NTYP` | the copy loop's own bound and `arg.len <= STRMAX` |
| 4 | `sget` | `i < v@.len()` | `b@.len() == REC`, the caller's precondition |
| 5 | `wsub` | `o + n <= v@.len()` | the same, and the kernel's `nrec * REC <= len` |
| 6 | `sel_get` | `k < NSEL` | a literal at every call site |
| 7 | `name_get` | `k < NENC` | a literal at every call site |

⭐⭐⭐ **ITEM 1 IS THE ROW AND THE OTHER SIX ARE SCENERY, AND THE DIFFERENCE IS
CHECKABLE RATHER THAN RHETORICAL.** `controls/negatives.py --emit r1` deletes
the `typ.is_none() ||` disjunct — `f7326d627962`, the whole of it — from
`verus.rs`, and that mutant must **FAIL** to verify. It fails on **item 1's
precondition, at the first compare site**, which is the site the patch guards.
Deleting any of the other six preconditions fails somewhere else entirely.

⛔⛔ **AND THE OBLIGATION IS NOT DISCHARGED FROM THE PARSER'S POSTCONDITION,
WHICH IS THE POINT OF THE ROW.** `parse_va_args` returns SUCCESS with nothing
written whenever the count is zero, and its `ensures` says exactly that:
`r ==> *final(wrote) == (num_args == 1)`. **The parser's contract is strong
enough to PROVE the pointer may be absent.** No strengthening of the parser
could discharge item 1, because the parser is behaving correctly — which is
precisely what *the guard answers a different question* means, restated as a
proof obligation.

⭐ **The two table accessors have verifying twins only because `s_sel` and
`s_name` are defined as the constants' OWN VIEWS** rather than as a second
transcription of their 168 bytes. Verus does not evaluate the literals and does
not need to. A row that had written the bytes out again in spec-land would have
put them in the TCB and would have needed the justification hatch for two more
items. What checks the bytes instead is `controls/tables.py`, which diffs all
three transcriptions — `c/kernel.c`, `verus.rs`, `model.py` — and carries
must-fire negatives.

### §10.1 SLB-TRUSTED-ARGUMENT — the per-item arguments the gate requires

Seven trusted accessors, seven arguments. Each answers the three things no stage
of the gate can judge: **(a)** is the twin's body the right checked stand-in for
the unchecked operation; **(b)** is the `ensures` COMPLETE with respect to every
unchecked operation the body performs; **(c)** does each clause mean the same
thing in the shipped configuration as in the twin's.

⚠ **(b) is `TASK_009_REVIEW`'s x4 and it is the one a contract pin cannot
catch:** a body that ALSO read `i + 1` satisfies the contract, the twin and the
`--cfg slb_twin` run unchanged. The defence on every item below is the same
two things — a body short enough to quote whole, and **Miri**, which this row
requires.

#### SLB-TRUSTED-ARGUMENT verus.rs opt_get

**(a)** The unchecked operation is `t.unwrap_unchecked()` on an
`Option<&[u8; NTYP]>`; the twin is `t.unwrap()`, the same open with the check
Rust would have emitted. There is no third thing `unwrap_unchecked` does — its
`None` arm is `unreachable_unchecked()` and its `Some` arm is the projection.
**(b)** The body performs **no memory operation at all**: it opens a value with
two shapes and returns the reference inside it. `r@ == t.unwrap()@` names the
whole of what comes out, and there is no post-state to constrain because the
parameter is taken by value and the return is a shared reference. A body that
returned a DIFFERENT reference could not satisfy it. **(c)** `t.is_some()` and
`r@ == t.unwrap()@` mention only the parameter and the return value; `slb_twin`
is on the twin's own `#[cfg]` and nowhere else.
⭐⭐ **AND THIS IS THE ITEM THE ROW IS ABOUT.** Its `requires` is `I12/O3` word
for word, and what discharges it at all five call sites is `f7326d627962` and
nothing else — `controls/negatives.py --emit r1` deletes that line and the file
stops verifying, on THIS precondition, at the first site.
⚠⚠ **A CAUTION THIS ROW MEASURED AND DID NOT EXPECT** (§7): the
`unwrap_unchecked` in this body is UB when its `requires` is violated, and at
`-O1` and above LLVM does **not** lower that to a null read — it exploits it.
So the *consequence* of breaking this contract is unbounded in the ordinary way,
and the fault signature is NOT the C's. That is an argument for the contract,
not against it.

#### SLB-TRUSTED-ARGUMENT verus.rs aget

**(a)** The unchecked operation is `*v.get_unchecked(i)` on a `&[u8; NTYP]`; the
twin is `v[i]`, the same read with the bounds check. There is no third thing.
**(b)** The body performs exactly one memory operation and it is a read at `i`;
`r == v@[i as int]` names the value of that read, and there is no post-state to
constrain because `v` is a shared reference and the function returns by value.
**(c)** `i < NTYP` and `r == v@[i as int]` mention only the parameter, the array
view and the return value. ⚠ Note what the `requires` does NOT have to say: the
LENGTH is in the TYPE, so `v@.len() == NTYP` holds for every value this
signature admits and a `requires` naming it would be a tautology — which is what
distinguishes this item from `sget`.

#### SLB-TRUSTED-ARGUMENT verus.rs fset

**(a)** The unchecked operation is `*v.get_unchecked_mut(i) = x` on a
`&mut [u8; NTYP]`; the twin is `v[i] = x`, the same write with the bounds check.
**(b)** ⭐ **This is the item where (b) has teeth, because it WRITES.** The body
performs exactly one memory operation and it is a store at `i`; the `ensures` is
`final(v)@ == old(v)@.update(i as int, x)` — **the WHOLE post-state**, not
`final(v)@[i] == x`. A body that also clobbered `v[i + 1]` could not satisfy it,
which is the difference between this contract and the one `TASK_009_REVIEW`'s x4
walks through. **(c)** `x: u8` is a pure value and needs no precondition: the
definedness of the store depends on `i` and on `v` being a live fixed-size array
and on nothing about the byte. The indexing parameter is the constrained one.

#### SLB-TRUSTED-ARGUMENT verus.rs sget

**(a)** The unchecked operation is `*v.get_unchecked(i)` on a `&[u8]`; the twin
is `v[i]`. **(b)** One memory operation, a read at `i`; `r == v@[i as int]` names
its value and there is no post-state. **(c)** ⚠ **IT IS NOT `aget`'s ARGUMENT.**
`v` here is a SLICE, whose length is a run-time fact, so the `requires` has to
name it — `i < v@.len()` — where `aget`'s length is in its type. The two call
sites bound `i` differently and both are visible in the caller: inside the record
decode it is a literal under `REC` and `b@.len() == REC` supplies the rest;
inside the frame copy it is the loop cursor under `STRMAX`, and
`arg.val@.len() == STRMAX` is a precondition of the enclosing function.

#### SLB-TRUSTED-ARGUMENT verus.rs wsub

**(a)** The unchecked operation is `v.get_unchecked(o..o + n)` on a `&[u8]`; the
twin is `&v[o..o + n]`, the same sub-slice with the range check. ⚠ The twin's
body carries one ghost line, `assert(v@.len() == vstd::slice::spec_slice_len(v))`,
which fires the vstd axiom that a slice length fits in a `usize` — without it
the twin cannot show `o + n` does not overflow. It is ghost and is not a second
operation. **(b)** The body performs **no read**: it forms a reference. The
`ensures` names the WHOLE result — `r@ == v@.subrange(o as int, (o + n) as int)`
— and not merely its length, because a body that returned a correctly-sized
slice of the WRONG bytes would satisfy a length-only contract and move every
answer downstream. **(c)** ⭐ The `requires` constrains BOTH endpoints at once,
`o + n <= v@.len()`, which is what a sub-slice needs and what an index bound
would not give.

#### SLB-TRUSTED-ARGUMENT verus.rs sel_get

**(a)** The unchecked operation is `SELS.get_unchecked(k)` on a
`[[u8; NTYP]; NSEL]`; the twin is `&SELS[k]`. **(b)** One memory operation, a
reference into a `'static` table; `r@ == s_sel(k as int)` names which row.
**(c)** ⭐⭐ **THE `ensures` ASSERTS NOTHING ABOUT THE TABLE'S 105 BYTES**, and
that is deliberate: `s_sel` is DEFINED as `SELS[k]@`, the constant's own view.
Verus does not evaluate the literals and does not need to, which is exactly why
the safe twin can meet the same contract — a row that had transcribed the bytes
into spec-land would have put them in the TCB and would have had an
unverifiable twin. ⚠ **The bytes are therefore checked OUTSIDE the proof**, by
`controls/tables.py`, which diffs all three transcriptions (`c/kernel.c`,
`verus.rs`, `model.py`) and carries two must-fire negatives.

#### SLB-TRUSTED-ARGUMENT verus.rs name_get

**(a)**, **(b)** and **(c)** are `sel_get`'s, one table over: the unchecked
operation is `NAMES.get_unchecked(k)`, the twin is `&NAMES[k]`, the `ensures` is
the constant's own view, and the bytes are checked by `controls/tables.py`.
⚠ The entry exists separately because the BOUND is different — `k < NENC`, three
entries, where `sel_get`'s is five — and a reviewer checking that the bound
matches the array has two different pairs to keep apart in this file.

---

## §11 THE PROOF BUDGET — and a non-monotone `rlimit` is a SHAPE, not a size

⭐⭐⭐ **THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A
MEASUREMENT.** Verus's default is 10. Bisected on this box with
`controls/rlimit_bisect.sh`:

```
rlimit   plain                    twin (--cfg slb_twin)
1        47 verified, 0 errors    54 verified, 0 errors
2        47 verified, 0 errors    54 verified, 0 errors
3        47 verified, 0 errors    54 verified, 0 errors
5        47 verified, 0 errors    54 verified, 0 errors
10       47 verified, 0 errors    54 verified, 0 errors
30       47 verified, 0 errors    54 verified, 0 errors
```

**1 suffices, in both configurations.**

⚠⚠ **BEFORE THE THREE `#[verifier::opaque]` ATTRIBUTES IT DID NOT, AND THE
SYMPTOM IS WORTH RECOGNISING.** The same file, with `s_all` / `s_step` /
`s_false` transparent, measured:

```
rlimit   plain                    twin
2         46 verified, 1 errors   53 verified, 1 errors
10        47 verified, 0 errors   54 verified, 0 errors
30        46 verified, 1 errors   54 verified, 0 errors
60        47 verified, 0 errors   53 verified, 1 errors
```

⛔ **NON-MONOTONE IN THE BUDGET — 10 passes, 30 fails, 60 passes.** That is not
*this proof is too big*; it is *this proof is a coin flip*, and raising the
number would have hidden it behind a green line. The cause was `kernel`'s loop
unfolding `s_run → s_step → s_all → eight `s_fold_str` recursions → `s_cmp`
recursions` on **every iteration**. Making the three spec functions opaque and
revealing them in the one function that needs their bodies took the requirement
from *unstable above 30* to **1**.

▶ **The lesson, and it is `ph16`'s one level up:** ph16 attacked its budget and
took the plain requirement from 16 to ≤ 2 by *naming quantities*; this row took
an unstable requirement to 1 by *hiding definitions*. Both are attacks on the
SMT context rather than on the number, and in both cases the attack worked.

### ⚠⚠ THE IDENTITY READING IS PATH-DEPENDENT, AND THIS ROW MEASURED IT BOTH WAYS

⛔ **QUOTE THIS AS AN EVENT, NEVER AS A STATE** (`RECAP_PHP.md` F119/M2).
`asm.py::identity_level` on `unsafe` vs `verus`, `isolated`, gave **two
different answers on the same sources**, and the difference is the BUILD ROOT:

| where the two binaries were built | O3 | O0 |
|---|---|---|
| a scratch tree, filenames `unsafe-O3-isolated` / `verus-O3-isolated` | **`exact`**, `md5_raw_equal = True` | `norel` |
| **the gate's own build root**, `harness-php/gate.py --tool build` | **`norel`**, `md5_raw_equal = False` | `norel` |

⭐⭐ **THAT IS `RECAP_PHP.md` F101 / ITEM 109 FIRING LIVE, ON THIS ROW, IN THE
DIRECTION THE PIN'S RATIONALE PREDICTED.** `kernel_fingerprint` is
path-sensitive; the raw bytes carry relocations, and the two build roots put the
same code at different addresses. **The instruction counts agree in both
(558 / 558 at O3, 1224 / 1224 at O0) and `md5_fn_norel` and `md5_norm` agree in
both.** Only the raw-byte comparison moves.

▶ ⭐ **SO `spec.md` PINS `norel` AT BOTH LEVELS, AND THE GATE'S OWN VERDICT IS
`norel` AT BOTH LEVELS.** Had the row pinned `exact` on the strength of the
scratch reading, the gate would have refused it — an environment difference
reported as a defect, which is what the pin's rationale says to avoid. ⚠ **The
`exact` reading above is NOT withdrawn and is NOT a contradiction**: it is a
true statement about two binaries built at two particular paths, and it is
recorded here so that nobody re-derives it and thinks the pin is too weak.

⚠⚠ **AND IT TOOK A REPAIR TO GET THERE, WHICH IS ITSELF A FINDING.** As first
written the two rungs were `exact` at O3 and **differed by 144 instructions at
O0** — so *the O3 reading alone would have certified an equivalence that was
false one optimisation level down*. Three exec-text divergences the optimiser
erased: two accessors R4 reached through the checked path, a bitmask where R5
wrote a modulus, and seven trusted wrappers carrying `#[inline(always)]` in R4
and not in R5. ▶ **Check the identity at O0 as well as at O3; O3 can hide a
real difference and O0 cannot.**

---

## §12 THE KERNEL-OVERLAP NUMBER, AND WHAT I THINK OF IT

`PROTOCOL_PHP.md` §F9: the floor was demoted to a report at `TASK_PHP_008` §2,
which moved the judgement from the tool to a person.

```
per-span overlap: span0 9% (2/22), span1 48% (25/52), span2 10% (2/20),
                  span3 25% (2/8), span4 0% (0/14)
kernel overlap 25% (28/113)   tier=narrowed is expected to clear 25%
⚠⚠ THE OVERLAP IS BELOW WHAT tier=narrowed LEADS A READER TO EXPECT (25% < 25%)
```

**What I think of it, in order.**

1. **The warning is a ROUNDING ARTEFACT and not a verdict.** 28/113 is
   **24.78 %**, which prints as `25%` and compares as `< 25`. The row is one
   excerpt line away from clearing its own tier. I am recording that rather than
   adding a line to clear it.
2. ⭐ **The MECHANISM span is the one that overlaps, and it overlaps at 48 %.**
   `span1` is `zend_parse_va_args` (`zend_API.c:463-549`) — the spec scanner,
   the count test and the write loop — and half its lines are in the kernel
   verbatim. That is the half of the row a reader has to trust, and it is the
   half the number is highest on.
3. ⚠ **`span4` is 0 % and that is correct.** It is the globals constructor
   (`mbstring.c:720-735`), sixteen lines of `MBSTRG(...) = ...` assignments that
   the kernel expresses as a three-entry constant table. It is cited so the four
   settings are **pinned rather than invented**, not because the kernel lifts
   it. A span cited for provenance drags the union down without saying anything
   about fidelity — which is a property of the heuristic, not of the row.
4. ⚠ **`span0` is 9 % and that is the one worth arguing about.** It is
   `mb_get_info` itself, and the kernel's version of it keeps every branch,
   every arm and the order, while spelling `array_init` + four
   `add_assoc_string` as a fold and `RETVAL_STRING` as a tag. Those are the
   divergences the ledger itemises. **Whether that makes the row `narrowed` or
   `modelled` is the honest question**, and my answer is `narrowed`: the wrapper
   (zvals, the `va_list`, the hash table) comes off and the BODIES —
   the spec scanner, the count test, the write loop, the five-arm chain and the
   dead NULL tests — are unchanged. `ph56` faced the same question and answered
   `modelled`; the difference is that this row's control flow is upstream's
   line for line, where `ph56` re-expressed a compiler.
5. ⚠ **The number measures TEXT IN `c/kernel*.{c,h}`, not code in the
   benchmark.** It never reads `c/main.c` or the build, so a high number would
   not have been evidence that the cited lines are compiled (`TASK_PHP_005`
   F-4). What *is* evidence of that is the gate's stage 6 — the driver loop, the
   single call site and callgrind's own caller→callee edges.
6. ⓘ **One unevaluable preprocessor condition**, `#ifndef PH97_KERNEL_H`, the
   include guard. Anything inside a dead one of those counts as live; here the
   one condition is live and the residual is zero. Reported as a number rather
   than enumerated away.

---

## §13 THE RUNS — the six-command sequence, and what it cost

```
1  gate.py --tool build   ph97-optarg-unwritten --all     28 binaries
2  gate.py --tool measure ph97-optarg-unwritten           the matrix
3  gate.py --tool report  ph97-optarg-unwritten           the table exists
4  gate.py                ph97-optarg-unwritten           FAILS on tables
5  gate.py --tool report  ph97-optarg-unwritten           re-render
6  gate.py                ph97-optarg-unwritten           green
```

⚠ **THE ROW PAID THE BUILD+MEASURE PAIR FOUR TIMES, NOT ONCE, AND EVERY EXTRA
ONE WAS A `c/*` OR `*.rs` EDIT MADE *BEFORE* THE FIRST GATE.** They are recorded
because the cost of each is the thing `PROTOCOL_PHP.md` §F6a is about:

1. the first build+measure;
2. ⛔ the `c/*` verdict-comment repair — `contract_audit.py`'s N8 ratchet fired
   on a comment that STATED another artefact's verdict, and the sentence moved
   to §14. **Free here; a 32-cell re-measure after the row gates.**
3. a `-Wcomment` warning `c/kernel.h` was emitting on every C build (the token
   `c/*` inside a C comment). Now **0 warnings** across all 28 builds;
4. the R4/R5 exec-text alignment of §11 and the `requires` deletion the gate
   proved was decoration.

▶ **The lesson, and it is the cheap half of §F6a: run `contract_audit.py` and a
warning-free build BEFORE the first `--tool measure`, not after.**

### The gate's own preflight, every run

Nine stages, eight of which can fail: the shim link, the digest bridge,
`c_digest_audit`, the unconditional `c/emalloc_shim.h` symlink, the overlap
self-test, the manifest, provenance, `why_sizes` (reported, cannot fail) and
preflight coverage. `1 row(s) checked, 0 FAILED` on every invocation.

---

## §14 ⭐⭐ WHY THE TWO BYTES MUST BE INDEPENDENT — the argument, in its right home

`c/kernel.h` and `c/kernel.c` point here and do not state this; `c/*` is in the
**measurement** digest and a verdict frozen there costs a 32-cell re-measure to
repair (`PROTOCOL_PHP.md` §F6a, `RECAP_PHP.md` F98). `NOTES.md` is gate-only and
costs a re-gate.

**The argument.** A record carries `b[0]` for *was an argument supplied?* and
`b[1]` for *is it well-typed?*. Those are two propositions and the whole row is
that `mbstring.c:3215` answers the second while `:3219` needs the first. ▶ **A
kernel that derived one from the other would have deleted the mechanism**: if
the type tag were meaningful only when the count is non-zero — or if the count
were inferred from a sentinel type — then *supplied* and *well-typed* would
coincide, the guard would answer the question the code needs, and the row would
be modelling an ordinary missing NULL check with a longer name.

**Where the argument comes from, and it is not mine.** `patterns-php/
CATALOGUE.md`'s `⚠ risk` note on **`ph96`** states it one row over — *"the two
flags must be independent in the blob — a kernel that derives `wrote_out` from
`status` has deleted the mechanism and rebuilt `ph60`"* — and `TASK_PHP_056`
§2.5 carries it forward to this row as a build instruction.

**What enforces it here, rather than asserting it.**

- `spec.md` `idiom.required[0]` pins `b[0] % 3u` / `b[1] % 4u` (C) and
  `sget(b, 0) % 3` / `sget(b, 1) % 4` (Rust) as separate spellings, so a rung
  that collapsed them would be out of its own contract;
- `inputs/gen.py::_check_span` refuses to write a measured corpus that does not
  reach both benign argument counts **and** all four type tags **and** all three
  parser routes;
- `model.py::_synthetic_windows` family (a) drives the **whole 3 × 4 cross
  product** — twelve combinations, including the six that are unreachable if
  either byte is derived from the other — and `selfcheck()` runs three
  independent implementations over them.

⚠ **This section is the reason `c/kernel.c:323` carries a pointer and not a
sentence.** `contract_audit.py`'s N8 ratchet fired on the first draft of that
comment, which did state the verdict, and it fired **before** the row was
measured — which is when it is free. The residual hit is the classifier's
adjective spelling (`independent` describing two bytes rather than two
artefacts) and is filed as a FALSE-POSITIVE with its reason in that tool's
`ADJUDICATED` table; it is the **third** instance of that spelling class.
