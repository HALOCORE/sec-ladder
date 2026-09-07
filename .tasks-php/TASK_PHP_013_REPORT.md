# TASK_PHP_013_REPORT — `ph03`, the PHP programme's first real row

**Role:** research engineer, one agent alone.
**Row:** `patterns-php/ph03-uudecode-bound/` — `php_uudecode`,
`ext/standard/uuencode.c:126-171`, CRASH-115, tier `verbatim`.
**Status:** ✅ **BUILT, MEASURED, GATE GREEN** — `check.py: PASS`, 0 failures,
contract `0302248bc9868121…`; brackets `66 / 0 STALE` (PAT) and `4 / 0 STALE`
(php) at both ends. All five rungs plus R1h; R5 verifies **25 / 0** (28 with
`--cfg slb_twin`) with a full functional postcondition.

⚠ **Reconciliation of the running count is the manager's job.** This task was
launched from **61** and I do not carry it forward.

---

## §0 The bracket

**Open** (first two commands of the session):

```
$ python3 harness/measure.py --check-stale
...
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
...
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)

2 record(s) examined, 0 STALE
```

**Closed** — see §9.

`git status --porcelain` throughout shows only `patterns-php/ph03-uudecode-bound/`
and `results-php/`. **`.web/` was never touched and `git add -A` was never run.**
No `harness/`, `common/`, `patterns/`, `results/` or `pilot/` file was created,
edited or deleted.

---

## §1 What was built

```
patterns-php/ph03-uudecode-bound/
  spec.md                     contract_sha256 0302248bc9868121... (first written
                              875387e901b85b5e...; it MOVED TWICE -- §9, NOTES.md §0)
  NOTES.md                    the findings, §§0-12
  README.md                   the reader's entry point
  model.py                    two independent implementations + selfcheck
  c/kernel.h  c/kernel.c      R1  -- uuencode.c:126-171 VERBATIM. The bug.
  c/kernel_hardened.c         R1h -- + f95c1df58349 (2004), all three hunks
  c/main.c                    the driver
  c/emalloc_shim.h            -> ../../../common-php/emalloc_shim.h  (symlink)
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs      R2 R3 R4 R5
  inputs/gen.py               + small, large, adversarial-{read,write,shortsrc,nowin}
  controls/f95c1df58349.patch   the 2004 fix, 1433 B, sha256 fc3ef3c50488d004...
  controls/1e2818b14376.patch   the 2014 fix, 2063 B, sha256 97975e658d67aaad...
  controls/fix_incomplete.c     ASan demo that the 2004 fix is incomplete
  controls/negatives.py         the Verus mutant that must NOT verify
```

**Provenance**, validated: `ext/standard/uuencode.c:126-171`, 939 bytes, sha256
`9f68d3cfb639cb62a3ec7b685da1a8e4cec828085791e200c23ffa8eb12778fe`, against the
pinned tarball `5783e0c0ba94f165…`. Kernel overlap **95 % (18/19 excerpt lines)**
against a `verbatim` expectation of 50 %; **1** unevaluable preprocessor
condition, and it is the header guard `#ifndef PH03_KERNEL_H`.

⚠ **`PROTOCOL_PHP.md` §F item 9 asks me to say what I think of that number.**
95 % is right and the missing line is the one I expect: `PHPAPI int
php_uudecode(...)` against my `static int php_uudecode(...)`, which is a declared
`deletions` entry. **But the number would be 95 % whether or not the function is
compiled** — `provenance.py` reads `c/kernel*.{c,h}` and never `main.c` or the
build, and it says so itself. What actually ties the cited lines to the
benchmark on this row is the ASan backtrace: `php_uudecode` appears in the
stack at `kernel.c:143` with `kernel` above it and `main.c:57` above that (§4).
**That is the evidence a reviewer should want; the overlap is a spelling check.**

---

## §2 ⚠⚠⚠ THE PIPELINE DEFECTS THIS ROW FOUND

§0 of the task file said to expect these and to **report them rather than force
the row into the pipeline**. Four, in descending order of how much they matter.

### B1 — `harness/build.py` LINKS NO `-lm`, AND IT IS FROZEN

`uuencode.c:131` is `ceil(src_len * 0.75) + 1` and `:141` is
`(int) floor(len * 1.33)`. Both are libm. **A verbatim kernel fails to link in
6 of the 8 C cells.** Measured, `.temp/php13/01b-floor-runtime.log`, the exact
flag sets `build.py::c_flags` produces:

```
gcc   -O0 -DSLB_ISOLATED   FAILED: undefined reference to `floor'
gcc   -O0 -flto            FAILED: undefined reference to `floor'
gcc   -O3 -DSLB_ISOLATED   built
gcc   -O3 -flto            built
clang -O0 -DSLB_ISOLATED   FAILED: undefined reference to `floor'
clang -O0 -flto            FAILED: ld.lld: undefined symbol: floor
clang -O3 -DSLB_ISOLATED   FAILED: undefined reference to `ceil'
clang -O3 -flto            FAILED: ld.lld: undefined symbol: ceil
```

Only `gcc -O3` folds both away; **clang folds `floor` and not `ceil`**, so even
the optimisation level is not a clean predictor.

⚠ **This is not about uudecode.** Any php kernel touching `math.h` hits it, and
the catalogue has several — `ext/standard/math.c`, `formatted_print.c`, the
`pack`/`unpack` family. **The next builder will hit it and should not have to
re-derive it.**

**What I did**, because `build.py` is frozen (`PLAN_PHP.md` §2.1: editing it
costs a 33-pattern re-measure): the C rungs define `php_uu_floor` /
`php_uu_ceil` and substitute them **by macro**, so the verbatim text
`(int) floor(len * 1.33)` is unchanged and the arithmetic is still binary64 on
the same expressions. Declared as a `provenance.deletions` entry with a
differential and a must-fire control: **0 disagreements** against libm over the
whole reachable domain (`len` 0..63, `n` 0..10⁶), control **38**.

**What the manager may want to decide instead:** adding `-lm` to `build.py`'s
link line is a one-token edit that costs the PAT programme a 33-row re-measure
and buys every future php row a verbatim libm call. I did not take that
decision; it is not mine.

### B2 — ⚠⚠ `check_sanitizers_hardened` FORBIDS A ROW FROM SHIPPING `PROTOCOL_PHP.md` §C's STRONGEST RESULT

`PROTOCOL_PHP.md` §C: *"An upstream fix is not automatically correct … That is a
result, and one of the strongest a row can carry. Report it; do not repair it."*

`harness/check.py::check_sanitizers_hardened` (stage `7h`, `TASK_151`)
**hard-fails the gate on any ASan/UBSan diagnostic from the R1h arm on any
input**, and argues the point explicitly:

> *"R1h is the rung that does NOT have the bug, so the expectation is `clean` on
> EVERY input, adversarial included — that is what R1h means, and a per-input
> declaration here would let a pattern declare its way out of the only thing
> this stage asks. A row that fires here is a real finding."*

That reasoning is correct for a PAT row, whose R1h is **hand-written by us**. It
is wrong for a php row, whose R1h is **whatever upstream shipped** — and
`ph03`'s upstream fix is incomplete (§3). **The two documents are in direct
tension, and the first real row hit it.**

**Consequence, and it is not cosmetic:** a php row cannot carry, as gate
evidence, the class of result the php protocol calls its strongest. `ph03`'s
demonstration lives in `controls/fix_incomplete.c` and is run by hand;
`model.py::selfcheck` asserts that no shipped `inputs/` blob reaches the class
that would fire on R1h, so the constraint is *enforced* rather than remembered.

⚠ **I did not "fix" this and it is not this row's to fix** — the repair is a
`harness/check.py` edit and a 33-pattern re-gate. What I would suggest, for the
manager to weigh: the honest shape is *"R1h is clean on every input unless
`model.py` declares `hardened_sanitizer_expect: fires` **with** a `fix_commit`
and a citation"*, which is a per-input declaration and therefore exactly what
that docstring refuses. **It refuses it for a reason that does not hold here,
and that is the thing to decide, not the spelling.**

### B3 — ⚠ THE OVERLAP NUMBER IS NOT EVIDENCE THAT THE CITED LINES ARE COMPILED, AND THE FIRST `verbatim` ROW IS WHERE THAT STOPS BEING FREE

`PROTOCOL_PHP.md` §F item 9 warned that the demotion of the overlap floor to a
report *"is free today only because no real row has ever been adjudicated by
it — the first `verbatim` row is where that stops being true."* **This is that
row, and the warning is right.** 95 % is a fact about text in
`c/kernel*.{c,h}`. §1 says what I trust instead.

⚠ A concrete way the number could mislead the *next* row: `provenance.py` globs
`c/kernel*.{c,h}`, so `c/kernel_hardened.c` is included in the overlap. A row
whose `kernel.c` was a stub and whose `kernel_hardened.c` was the real
extraction would score the same. Nothing about ph03 does that; it is a shape the
metric cannot distinguish.

### B4 — minor: `PROTOCOL_PHP.md` §E says the named-spelling tail is **11,003** bytes; it is **11,004**

`check.py`'s own `NAMED_SPELLING_LEN` and the tail extracted verbatim from
`ph00-smoke/spec.md` both give **11004**. One byte, in a document that is quoted
when a builder is trying to make a hash reproduce. Worth correcting because it
is exactly the kind of number a reader trusts instead of measuring.

---

## §3 ⚠⚠⚠ THE ROW'S HEADLINE — THE 2004 UPSTREAM FIX IS INCOMPLETE, MEASURED TWO WAYS

`TASK_PHP_012` §7.3 predicted this from the corpus's history layer and asked me
to verify it with a detector and a must-fire control, "and if it does not hold,
say so." **It holds, and it is sharper than predicted.**

`c/kernel_hardened.c` is `f95c1df583490814b0501c56f59671193a57507b` (Ilia
Alshanetsky, 2004-08-24, bug #29821), all three hunks, patch kept under the row.
It adds `if (len > src_len) goto err;` and `if (ee > e) goto err;`.

**`ee` bounds where the inner loop TESTS. The body reads `*(s+3)`.**

### 3a. Counted, over 12 600 documents

`.temp/php13/02-reach.log`, an instrumented interpreter of the verbatim function
(offsets, not pointers, so it records every access without performing one):

```
Q2 verbatim, 200*63 = 12600 single-line documents:
   read  past src end : 3608
   write past emalloc : 3352
   :158 tail entered  : 0

Q3 with f95c1df58349 applied, same 12600 documents:
   goto err taken     : 3464
   read  past src end : 144   <- the fix is INCOMPLETE
   write past emalloc : 0
```

**The write is closed. A read is left.** Smallest surviving case: `src_len = 2`,
`len = 1` → `fl = 1`, so `ee == e`, hunk 2 does not fire, and the body reads to
`s + 3`.

### 3b. Under ASan, with a must-fire control

`controls/fix_incomplete.c`, `.temp/php13/11-fixctl.log`:

```
control    ==1440994==ERROR: AddressSanitizer: heap-buffer-overflow READ of size 1
           #0 in main .../fix_incomplete.c:126            <- the detector IS live
benign     BENIGN src_len=63 -> total_len=45 (expect 45)  <- silent
fixed      ==1441005==ERROR: AddressSanitizer: heap-buffer-overflow READ of size 1
           #0 in php_uudecode .../fix_incomplete.c:88     <- uuencode.c:144
fixed2014  returned -1 -- no detector fired               <- silent
```

⚠ The source is `malloc`ed at **exactly** `src_len`. A stack array or an
over-allocated buffer gives the over-read slack to land in and the control
reports nothing — which is §5's finding one level down.

### 3c. ⭐ And Verus refuses the shipped fix, in one line

`controls/negatives.py --emit no2014` deletes **only** the four lines of the 2014
check from `verus.rs` — leaving exactly the algorithm `c/kernel_hardened.c`
implements. `.temp/php13/10-verus-negctl.log`:

```
error: precondition not satisfied
   --> ...verus_no2014_tmp.rs:673:26
    |
382 |         i < v@.len(),
    |         ------------ failed precondition
...
673 |             let b1: u8 = get_unchecked(buf, s + 1);

verification results:: 24 verified, 1 errors
```

**`i < v@.len()` on `get_unchecked(buf, s + 1)` IS the over-read** — the same
byte ASan reports at `uuencode.c:144` in 3b. A proof obligation refuses, in one
line, the patch PHP shipped in 2004 and did not complete until **2014**
(`1e2818b143760a79a0887861bd6221b158355073`, bug #67252, whose own `.phpt`
reproducer is `"M" + 60 chars + "\n" + "a."` — `PHP_UU_DEC('a') == 1`, the same
`fl == 1, ee == e` shape 3a found independently).

⚠ **This is the crash course's argument in one row**: the thing the ladder buys
is not that the proof is fast, it is that *the obligation is stated at all*, and
a stated obligation caught in 2026 what a careful patch missed for ten years.

**Consequence for the ladder, and it is why R2–R5 are NOT ports of R1h:** with
only the 2004 pair, a safe-Rust rung **panics** on those 144 documents. A rung
that panics is not a translation of the C. So R2–R5 carry both fixes, and the
row's ladder reads:

| rung | checks |
|---|---|
| R1 | none — CRASH-115, both limbs |
| R1h | `f95c1df58349` (2004) — the write closed, a read left |
| R2–R5 | + `1e2818b14376` (2014) — memory-safe |

On every input this row ships a 2004 check fires first, so R1h and R2–R5 agree
on all six and only R1 diverges. `model.py::selfcheck` asserts that.

---

## §4 Reachability and fidelity — `PROTOCOL_PHP.md` §A3/§A4

**Deliverable #1, settled before any rung existed**: §3a's table, plus the fact
that the triggering `len` values span the whole domain **1..63** — this is not a
property of the `len == 45` special case.

**Fidelity**, built exactly as `check.py::_san_build` builds it, `env -u
LD_PRELOAD`, `.temp/php13/06-asan.log`:

| input | R1 (`c/kernel.c`) | R1h |
|---|---|---|
| `small` / `large` | clean | clean, identical checksums |
| `adversarial-read` | **heap-buffer-overflow READ of size 1** at `php_uudecode`, `kernel.c:143` = `uuencode.c:144` | clean |
| `adversarial-write` | **heap-buffer-overflow WRITE of size 1** at `kernel.c:145` = `uuencode.c:146` | clean |
| `adversarial-shortsrc` | **heap-buffer-overflow READ of size 1** at `kernel.c:145` = `uuencode.c:146` | clean |
| `adversarial-nowin` | clean, `0` | clean, `0` |

✅ **The corpus's recorded category (`heap-buffer-overflow`) reproduces, in the
named function, and `uuencode.c:144` is the exact line the corpus's history
layer names.**

---

## §5 ⚠⚠ I REFUTE PART OF THE CATALOGUE'S RISK NOTE AND PART OF `TASK_PHP_012`'s READING

The catalogue says: *"the row's `cwe` is CWE-125 but the **write** fires first
under ASan on most inputs."* `TASK_PHP_012` §7.3 measured a WRITE at
`uuencode.c:144`.

**Both are artefacts of the source buffer, not properties of the code.**

`inputs/adversarial-read.bin` and `inputs/adversarial-write.bin` carry the
**same 71-byte window** and differ in exactly one thing — the second has 60
bytes of slack after the window inside the blob. `nwin = 1` in both:

```
adversarial-read   stride=71  n_blob=71   -> READ  at uuencode.c:144
adversarial-write  stride=71  n_blob=131  -> WRITE at uuencode.c:146
```

**Mechanism.** The inner loop reads 4 source bytes and writes 3 destination
bytes per iteration, and the destination starts with ~25 % more headroom
(`cap = ceil(0.75·src_len) + 1` is three quarters of the source). So **on an
exactly-sized source the read always leaves the allocation first** — §3a's
3608 ⊇ 3352 is the same fact counted. The over-write is *downstream* of the
over-read, not independently reachable.

The corpus recorded the write because **PHP always has slack**: a zval string is
NUL-terminated and `emalloc` rounds to a multiple of 8. `TASK_PHP_012`'s probe
saw it for the same reason — a `char enc[16]` holding 9 live bytes.

**What I adopt from `TASK_PHP_012` m8:** `provenance.cwe` is **`CWE-787`**, with
`cwe_note` recording the corpus's internal disagreement and both runs.
**What I refute:** *"the write fires first"* as a statement about the code. A
reader who took it as one would build the wrong adversarial blob and get a green
gate over a silent over-read.

⚠⚠ **The general lesson, for the next row: an oracle built on "which sanitizer
message appears" is measuring the allocator's rounding as much as the defect.
Where two limbs share one bound, ship both blobs.** This row does.

---

## §6 The rungs

### R1 / R1h — C

Verbatim `:126-171`, including `:158`'s precedence bug
(`if ((len = total_len > (p - *dest)))`, so `len` ∈ {0,1} and `:160`/`:162` are
dead). ⚠ **Measured: the whole block is dead** — 0 of 12 600 documents enter it
(`.temp/php13/02-reach.log` Q2), and `model.py::selfcheck` re-derives it per
window. `TASK_PHP_012` m6 said `:160`/`:162` are provably dead; **the condition
at `:158` is dead too**, so the tail block is unreachable rather than merely
truncated.

### R2 / R3 / R4 — safe-naive / safe-tuned / unsafe

R2 indexes, R3 reslices the 4-byte source group and the 3-byte destination group
once each and folds with an iterator, R4 uses `get_unchecked` /
`get_unchecked_mut` throughout. All three allocate `vec![0u8; cap]` per call,
because `cap` is `php_uudecode`'s own `emalloc` size and dropping it would be a
different program.

### R5 — Verus: **25 verified, 0 errors** (28 under `--cfg slb_twin`)

**A full functional postcondition**, not a memory-safety-only retreat:

```
requires  off + len <= buf@.len()
ensures   r == uu_fold(buf@, off as int, len as int)
```

where `uu_fold` is a pair of mutually recursive spec walks (`uu_walk` over the
line chain, `fold_line` over the 4-character groups) that emit a `Seq<u8>`, plus
the Horner fold over its `total_len`-byte prefix and the allocator tally.
`model.py` re-derives it independently.

**Seven `proof fn`s**; the four that carry weight, and **two of them are about
this kernel specifically**:

- `lemma_store_in_bounds` — the three destination stores, from the invariant
  `4·p ≤ 3·(s − off)`;
- ⭐ `lemma_emit_covers_declared` — `ln ≤ 3·⌈line_len(ln)/4⌉` for every
  `ln ∈ 1..=63`, **the one obligation that is not a loop invariant.** It is
  *tight*: equality holds at all 21 multiples of 3, so no slack argument works.
  Proved by `by (compute_only)` over a recursive conjunction — the domain is
  finite precisely because `PHP_UU_DEC` masks with `077`;
- `lemma_nsteps_exact` — the inner loop lands on `s0 + 4·nsteps(fl)`, which is
  **past `ee`** whenever `fl % 4 ≠ 0`. That overshoot is the very thing the 2004
  fix does not bound (§3);
- `lemma_cap_bound`, `lemma_fold_prefix`, plus `lemma_dec_range` (a
  `by (bit_vector)` one-liner giving `dec_of(b) <= 63`, which is what makes
  `lemma_emit_covers_declared`'s domain finite) and `lemma_emit_upto_elim`
  (the induction that turns the bounded conjunction into the `forall`).

⚠ **A modelling error the spec caught and `selfcheck` could not have.** My first
`uu_walk` resumed the outer walk at `ee + 1` instead of at
`s0 + 4·nsteps(fl) + 1`. That is wrong for every `fl` not divisible by 4 — and
**it agrees with the simulation on every input this row ships**, because every
shipped line declares 45 and `60 % 4 == 0`. It was found by writing the Verus
termination argument, not by any test. Recorded in `model.py::_uu_walk`'s
docstring so the next reader does not re-introduce it.

**`identity`: `unsafe == verus`, `exact` at O3 — and `differ` at O0.** From the
gate record: at `-O3 isolated` both cells' kernel is
**`md5_fn 338505795ee18db952aafcdaec522df4`, 708 bytes, 200 instructions**.
**The proof licenses the unchecked reads *and* the unchecked writes at zero
instructions.** ⚠ **At O0 they genuinely differ — 335 vs 352 instructions, 1906
vs 2042 bytes — and I first pinned `norel` there, copying p01/p16 and a hand
build that had shown only a size change. The gate refuted it** (§9). At O0
nothing is inlined, so R5's five trusted wrappers survive as real calls where
R4's `get_unchecked` sites are open-coded; that is codegen, not relocation, and
`norel` was the wrong level.

**TCB: five `external_body` items**, counted individually in `NOTES.md` §10.
Three carry `unsafe` or a non-empty `ensures` and therefore get verified twins.
⚠ **`vset_unchecked` is the first *writing* trusted accessor in either
programme**, and its `ensures` is the whole post-state
(`final(v)@ == old(v)@.update(i, x)`) rather than a point assertion — a wrapper
naming only the written element would let a body that also clobbered `v[i+1]`
through every Verus stage.

---

## §7 Cross-rung agreement

All six rungs and `model.py`, `-O3 isolated`:

| input | R1 | R1h / R2 / R3 / R4 / R5 / model |
|---|---|---|
| `small` | `4724622162658835783` | identical |
| `large` | `16949792395555472632` | identical |
| `adversarial-read` | **abort (134)** | `9832046297558006400` |
| `adversarial-write` | **abort (134)** | `9832046297558006400` |
| `adversarial-shortsrc` | **abort (134)** | `10969280517312833152` |
| `adversarial-nowin` | `0` | `0` |

R1's abort without a sanitizer is glibc's own
`malloc(): invalid size (unsorted)` — the heap metadata it corrupted is detected
on the next allocation, on **all eight** C cells.

⚠ **`TASK_PHP_013` §7.3 asked whether the `floor()` double is reproducible
across the eight build cells. It is.** Byte-identical checksums on `small` and
`large` from gcc and clang × {O0,O3} × {isolated,whole}
(`.temp/php13/05-crun.log`), the gate's own stage 2 agrees over all 32 cells,
and the `floor` table itself hashes to `a422642e99c46107` on every cell that
links.

⚠ **And the claim is BOUNDED beyond `build.py`'s flag set rather than asserted**
— `.temp/php13/16-flagscope.sh`, output `.temp/php13/16-flagscope.log`:
`-ffast-math`, `-march=native`, `-funsafe-math-optimizations` and `-Ofast`, on
**both** compilers, give the same two hashes and **0** disagreements against
libm. ⚠ **`-mfpmath=387 -m32` was NOT measured** — no 32-bit target on this box,
the probe does not build. None of the five is in `build.py`'s set, so **no flag
scope needs stating**, but the one that could plausibly have moved it is the one
that did not run, and that is said rather than rounded off.

---

## §8 The measurement, and the mechanism for every delta

`-O3 isolated`, kernel-exclusive `Ir`, from
`results-php/ph03-uudecode-bound.json`. `small` = 25 000 calls × a 498-byte
window (120 four-character groups); `large` = 20 000 × 4032 bytes (975 groups).

| cell | `Ir`/call small | `Ir`/call large | **`Ir`/group** | fixed `Ir`/call |
|---|--:|--:|--:|--:|
| `c-gcc` (R1) | 6 626.0 | 52 168.0 | **53.27** | 234.1 |
| `c-gcc-h` (R1h) | 6 601.0 | 51 972.0 | **53.07** | 233.1 |
| `c-clang` (R1) | 5 605.0 | 44 413.0 | **45.39** | 158.3 |
| `c-clang-h` (R1h) | 5 627.0 | 44 606.0 | **45.59** | 156.3 |
| `safe_naive` (R2) | 8 404.0 | 67 675.0 | **69.32** | 85.3 |
| `safe_tuned` (R3) | 6 868.0 | 55 196.0 | **56.52** | 85.1 |
| `unsafe` (R4) | 6 125.0 | 49 206.0 | **50.39** | 78.5 |
| `verus` (R5) | 6 125.0 | 49 206.0 | **50.39** | 78.5 |

⚠ **`RECAP_PHP.md` open item 9 / F14 respected: no number here is put beside a
`pNN` number, in a table or in prose.**

**Mechanism for each delta, read off `objdump -d` — `PROTOCOL_PHP.md` §F item 8:**

| delta | value | mechanism |
|---|--:|---|
| R2 − R4 | **+18.94** `Ir`/group | one `cmp` + not-taken `jae` per checked access; the disassembly shows three back-to-back (`cmp %rsi,%rbx ; jae`, `cmp %rsi,%r14 ; jae`, `cmp %r12,%r10 ; jae`) immediately before the four `movzbl` loads R4 reaches directly. Ten checked accesses per group at ~1.9 `Ir`. |
| R3 − R4 | **+6.14** | the reslice collapses 4 source checks into 1 and 3 destination checks into 1 — **and adds one R2 never had**: `&mut dest[p..p+3]` must prove its endpoint does not wrap, `cmp $0xfffffffffffffffc,%rax ; ja`. ⚠ **R3's residual is not the check R2 was paying; it is a check R2 did not have.** |
| R4 vs R5 | **0** | `md5_fn 338505795ee18db952aafcdaec522df4`, 708 bytes, 200 instructions, both. The proof is free **including the writes**. |
| R4 − `c-gcc` | **−2.88** | unsafe Rust **beats** gcc C on this kernel. |
| R4 − `c-clang` | **+5.00** | …and loses to clang C. rustc 1.97.1 and clang 22.1.6 share LLVM 22.1.6 exactly, so this gap is language/ABI and the gcc one is two compilers. `.memory/03-measurement.md` rule 2 is what decides the sign, and quoting either alone would be quoting a compiler. |
| C − Rust *fixed* term | **~+150** `Ir`/call | `php_shim_reset()` walks 11 size classes per call (`PROTOCOL_PHP.md` §B1.3 requires it) where the Rust rungs only allocate a `Vec`. Cancels in R1-vs-R1h, does not cancel in C-vs-Rust; subtracted out of the per-group column above and named rather than buried. |

### ⭐ §8a — THE 2004 SAFETY CHECK HAS A NEGATIVE COST ON gcc

Per **line** (57 more lines on `large` than on `small`):

```
gcc    (51972 - 6601) - (52168 - 6626) = -171 / 57 lines  =  -3.0 Ir/line
clang  (44606 - 5627) - (44413 - 5605) = +171 / 57 lines  =  +3.0 Ir/line
```

**Mechanism, and it is visible.** Without `if (ee > e)`, gcc cannot prove the
inner loop is entered, so the per-line epilogue *selects* the trip count:

```
lea 0x2(%rbx),%rax ; cmp %rax,%rsi ; setae %dl
test %dl,%dl ; cmove %r12,%rcx      <- s += 4n  or  s unchanged
test %dl,%dl ; cmove %rbp,%rax      <- p += 3n  or  p unchanged
```

With the check, gcc knows the count is `(ee − s + 3)/4` unconditionally and
emits straight-line `sub`/`shr`/`lea` arithmetic — **the `setae` and both
`cmove`s are gone.**

⚠⚠ **The safety check paid for itself by handing the optimiser a fact it
otherwise had to branch around.** clang does not take that route and keeps a
plain compare, hence the `+3.0`. **"What does the upstream fix cost?" has no
single answer on this row: −3.0 `Ir`/line on gcc, +3.0 on clang.**

⚠ **What these numbers are NOT.** Not a bounds-check tax (the kernel allocates,
decodes, folds and frees per call, and only two of the four carry a check R4
removes); **not a searched comparison** — this row owes a
`controls/spellings.py` (`PLAN_PHP.md` §5.3, the trap that has fired seven
times), so **no ratio above is *the* cost of safety on this kernel**; and the
wall-clock numbers (17.0 ms / 94.3 ms medians, 30 reps, 3.5 % / 1.7 % spread)
are secondary.

---

## §9 The bracket, closed, and the gate

```
$ python3 harness/measure.py --check-stale
66 record(s) examined, 0 STALE

$ python3 harness-php/gate.py --tool measure --check-stale
FRESH       results/gate/ph00-smoke.json               29 source(s)
FRESH       results/gate/ph03-uudecode-bound.json      33 source(s)
FRESH       results/ph00-smoke.json                    19 source(s) + 8 input(s)
FRESH       results/ph03-uudecode-bound.json           19 source(s) + 6 input(s)

4 record(s) examined, 0 STALE
```

⚠ **The php side is 4 records, not 2** — ph03's gate and measurement records
join `ph00-smoke`'s pair.

⚠ **`0 STALE` means "every source that was PINNED
still matches"**, not "everything is pinned" (`RECAP_PHP.md` F14), and it does
not even mean every pinned source still exists — a deleted one prints `MISSING`
and does not fail (`PROTOCOL_PHP.md` §E, `TASK_PHP_009` m3). The preflight is
what closes that, and it is green.

**The six-command chain, as run** (`PROTOCOL_PHP.md` §E):

| # | command | result |
|---|---|---|
| 1 | `gate.py --tool build ph03-uudecode-bound --all` | `all builds ok`, 32 builds |
| 2 | `gate.py --tool measure ph03-uudecode-bound` | `wrote results/ph03-uudecode-bound.json` |
| 3 | `gate.py --tool report ph03-uudecode-bound` | `wrote results/tables/ph03-uudecode-bound.md` |
| 4 | `gate.py ph03-uudecode-bound` | **FAIL, 7 failures** — see below |
| 5 | `gate.py --tool report ph03-uudecode-bound` | re-render |
| 6 | `gate.py ph03-uudecode-bound` | FAIL, tables only — plus 3 `idiom-forbidden` SHOUTS |
| 7 | `gate.py --tool report` | re-render |
| 8 | `gate.py` | FAIL, tables only (my sequencing again) |
| 9 | `gate.py --tool report` | re-render |
| 10 | `gate.py ph03-uudecode-bound` | **PASS, 0 failures** |
| — | *then a `NOTES.md` citation fix (see below)* | |
| 11 | `gate.py` | FAIL, tables only — `doc-citation-other` dropped 5 → 4 |
| 12 | `gate.py --tool report` | re-render |
| 13 | `gate.py ph03-uudecode-bound` | **`check.py: PASS`, 0 failures, contract `0302248bc986`, 2 `loud` entries** |

**Run 4's seven failures, and what each was:**

| failure | cause | fix |
|---|---|---|
| `[identity]` ×1 | **I pinned `norel` at O0 and the measured level is `differ`** — 335 vs 352 instructions, 1906 vs 2042 bytes. My hand build had shown only a size difference and I copied p01/p16's level. **The pin was too strong and the gate caught it**, which is the direction it exists for. | `identity.O0 = "differ"`, with the mechanism in `why` |
| `[tcb-unsafe]` ×1 | `vset_unchecked`'s `requires` constrains `i` and not `x` — a **new** obligation, because it is the project's first *writing* trusted accessor and a read wrapper has no value parameter | `verus.unsafe_justifications["verus.rs"]["vset_unchecked"]` |
| `[twin]` ×3 | no `SLB-TRUSTED-ARGUMENT` sections in `NOTES.md` | added, one per trusted item, five in all |
| `[tables]` ×2 | the expected step-4 failure | step 5 |

**Run 6 failed only on `[tables]`** — but it also printed three
`[idiom-forbidden]` **SHOUTS**, which are recorded and rendered and **do not
fail the gate**, and they are worth more than the failure was:

> *"`idiom.forbidden[0]` has NOT ONE backticked spelling, so the enforced audit
> never ranges over it and its share of the 0 hits above is vacuous."*

**All three of my `forbidden` entries carried their spelling in plain prose**, so
the `0 forbidden hits` line above them was vacuous — `p09`'s shape exactly, five
entries and zero audited spellings (`TASK_038_REVIEW`), in the one `idiom` class
that has teeth. ⚠ **I fixed it because it is a real defect, not because the gate
demanded it**: one backticked spelling per entry, the `required` list tidied in
the same pass (two entries became per-language `{c: ...}` objects; two lost
their backticks with a sentence saying they pin an ALGORITHM CHOICE and an
OPERATION that no single token decides). Verified with
`check.py::spelling_matches` **before** re-running, and confirmed by the gate:
5 required backticked spellings, each present in every rung it scopes to; 3
forbidden entries, which the audit reads as **6 (spelling x language)** audits,
**0 hits, 0 entry/entries with NO backticked spelling** — against `3 entries
with none` before the fix.

**The last correction was mine and not the gate's**: NOTES.md §9 cited
`.temp/php13/01-floor-probe.log` for a `-ffast-math` / `-march=native` claim
that log does not contain. ⚠ **The claim was true — I had run those flags — but
the citation did not support it, which is this project's own citation-rot class
one level down.** I re-ran the flags into `.temp/php13/16-flagscope.{sh,log}`
(and found that `-mfpmath=387 -m32` cannot be measured on this box at all, which
the corrected text now says), fixed the citation, and paid the three commands.
A citation that does not support its claim is worse than no citation, because a
reader stops checking.

⚠⚠ **SO THE CHAIN WAS THIRTEEN COMMANDS, NOT SIX.** Of the seven extra,
**three were my own sequencing**, and the rule I did not find stated anywhere is
worth adding beside `PROTOCOL_PHP.md` §E's *"do not batch edits into a running
gate"*:

> ⚠ **After ANY edit to `spec.md` or `NOTES.md` the chain is
> `gate → report → gate`, not `report → gate`.** `report.py` renders from the
> gate record, and the gate record is written by the run *before* it. I edited
> `spec.md` after a render twice and paid a full gate run each time. The §E box
> says the order is load-bearing for a NEW row; it is load-bearing for **every
> correction**, and that is the part a first-time builder gets wrong.

⚠⚠ **`contract_sha256` therefore MOVED TWICE**, and `PROTOCOL.md` rule 6 says to
say so and say why:

```
875387e901b85b5eb969ab5be8b9d86e45f779d87456bbeb0ade3f833ab822dd   AS FIRST WRITTEN
bb2eb51917d2aabcafde52b3693ee9e2659e0442c99be5939bbc08761d3f2746   after gate run 1
0302248bc9868121ae74260e3b4ec4987fde5437e5c0a366ca8bef78d0f140df   AS SHIPPED
```

All three are in `NOTES.md` §0 with the itemised reason. ⚠ **Both moves are gate
findings, not second thoughts, and neither touches a measured number** —
`spec.md` is not in `measure.py::measurement_sources`, so no re-measure was owed
and none was taken. **The first hash was recorded before any cell was built
through `harness/build.py`**, which is the only evidence rule 6 can have on a row
that lands in one commit.

---

## §10 What I refute, and what I confirm

**Reconciliation is the manager's job; this is the list.**

### Refuted

1. ⚠⚠ **The catalogue's `ph03` risk note — *"the write fires first under ASan on
   most inputs"* — is not a property of the code.** It is a property of the
   source buffer's slack (§5). On an exactly-sized source the **read** always
   fires first, because the read runs away from `e` at 4 bytes per iteration
   while the write runs away from `cap` at 3 and starts with 25 % more headroom.
   `TASK_PHP_012`'s WRITE-at-`:144` measurement is correct *for its probe*,
   whose `char enc[16]` held 9 live bytes.
2. ⚠ **`TASK_PHP_012` m6 said `uuencode.c:160`/`:162` are provably dead. The
   condition at `:158` is dead too**, so the whole tail block is unreachable
   rather than merely truncated — 0 of 12 600 documents enter it, re-derived per
   window by `model.py::selfcheck`.
3. ⚠ **`PROTOCOL_PHP.md` §E says the shared named-spelling paragraph is 11,003
   bytes. It is 11,004** (`check.py::NAMED_SPELLING_LEN`, and the tail extracted
   verbatim from `ph00-smoke/spec.md`).

### Confirmed, with the measurement rather than the argument

4. ✅ **`TASK_PHP_012` §7.3's prediction that the 2004 fix leaves a second,
   distinct over-read reachable.** 144 of 12 600 documents, an ASan run with a
   must-fire control, and a Verus refusal (§3).
5. ✅ **`TASK_PHP_012` m8's proposal to re-label the row `CWE-787`** — adopted,
   with `cwe_note` recording the corpus's internal disagreement and both runs.
6. ✅ **The catalogue's `emalloc_dependent: false`.** `cap` peaks at 3025 bytes,
   so T1, T2 and T3 all sit ~2⁴⁰ below their moduli. The shim is linked,
   symlinked, digested and executed **without its semantics being the finding**,
   which is exactly what `TASK_PHP_012` §7.3 said this row was for.
7. ✅ **`ph03` vs `ph07` are not one kernel** (`TASK_PHP_012` §6.1) — nothing in
   building this row disturbs that.
8. ✅ **`TASK_PHP_013` §7.3's worry that the `floor()` double might not be
   reproducible across the eight build cells.** It is; see §7. No flag scope is
   needed.

---

## §11 ⚠ `TASK_PHP_013` §7.2 — WHAT I THINK THE SECOND ROW WILL HIT

The manager asked: *"if you finish and believe the second row will hit a
different class of problem, say what it is so the batch order can be changed."*
**I do, and I would reorder.**

`ph03` is a row where the allocator is *present and not load-bearing*. The next
row in `TASK_PHP_012`'s batch is **`ph29`** (`stream_socket_recvfrom`), where the
T1 truncation **is** the defect. Two things I hit here get *worse* there and one
technique I used does not carry:

1. ⚠⚠ **The tally-in-the-checksum technique does not carry to `ph29`.** ph03's
   Rust rungs reproduce `php_shim_tally()` **arithmetically** because the
   allocation is small and correct, so the tally is a closed form (§7 of
   `NOTES.md`). On `ph29` the tally is the *defect*: the C allocates a truncated
   buffer and the Rust rungs cannot reproduce that without modelling T1
   themselves, which is either a Rust reimplementation of `emalloc` in every
   rung or a checksum that stops comparing across rungs. **That is a design
   decision, not an implementation detail, and it should be made before the row
   is started rather than during it.**
2. ⚠ **`ph29`'s adversarial cell has an UNBOUNDED WRITE, not a large
   allocation** — and I had this backwards until I re-read the catalogue, so it
   is worth stating precisely: `emalloc(to_read + 1)` with `to_read` near
   `LONG_MAX` wraps to `2^63` as `size_t`, `REAL_SIZE(2^63)` truncates to
   `unsigned int` **0**, and a **header-sized** block succeeds. The receive then
   writes into it. So the hazard is not RSS, it is a write that walks the heap
   until it hits an unmapped page. Budget a detector on the adversarial cell and
   a `run_timeout_s`, and expect Miri blocked rather than green. ph03's
   adversarial inputs are 20–131 bytes and fault within tens of instructions;
   nothing here transfers.
3. ✅ **`ph07` (`mbfl_strcut`) is the safer second row** and I would build it
   next: it is the first `narrowed` extraction, so it is the first real test of
   the tiers and of `provenance.py`'s overlap at the 25 % expectation — a
   *pipeline* question, like ph03's, rather than a *semantics* one. It also
   allocates nothing, so §7's asymmetry does not arise at all.

**Concretely: `ph03 → ph07 → ph21 → ph16 → ph12 → ph29`, with `ph29` last in the
batch rather than second**, so the allocator-semantics decision is taken with
five rows of pipeline experience behind it instead of one.

---

## §12 What I did NOT do, and what I am unsure about

1. ⚠ **No `controls/spellings.py`.** `PLAN_PHP.md` §5.3 asks for a re-derivable
   search of both endpoints before a rung difference is published. This row
   ships one spelling per rung by construction and **has not searched either
   endpoint**. **No ratio in §8 is *the* cost of safety on this kernel**, and
   `NOTES.md` §12 says so where a reader will meet it.
2. ⚠ **No `sweep-*` band.** `work_per_call` moves between `small` and `large`
   (498 vs 4032, different residues mod 4/8/16), which is what
   `check_marginal_ir` needs — but there is no length sweep, so §8's per-group
   figures are two-point slopes, not swept laws. Two points and a line is not a
   curve; `p02`'s first sweep design made exactly that mistake.
3. ⚠ **`c/kernel.c:52` cites `harness/build.py` by LINE**, where
   `.memory/02-bench-rules.md` says to name the function and give no line number
   at all. The gate shouts it (`doc-citation-other`, a `loud` entry, **not** a
   failure) and its own advice is *"cite the FUNCTION when one of these files is
   next re-measured anyway"* — because `c/kernel.c` is measurement-hashed and
   re-citing costs a re-measure. **I took that advice and left it.** The
   `NOTES.md` prose, which is only gate-hashed, now names `build.py::build_c`.
   ⚠⚠ **And the shout still counts FIVE, not four, because one of the five is
   `NOTES.md`'s own sentence DESCRIBING the citation** — it quotes the line span
   in order to say the span should not be there, which is the same shape as a
   `kernel_hardened.c` comment quoting the `forbidden` spelling it refuses.
   Rephrasing it would cost another `gate → report → gate` (~40 min) for a
   cosmetic point on an already-green row, **and I chose not to pay it**. Said
   here so the number is not read as four unfixed citations.
3b. ⚠ **`results-php/preflight/_norow.preflight.json` is MODIFIED (+59 lines)**
   and will show in `git status`. That is `PROTOCOL_PHP.md` §E's *"not
   read-only"* row: every `gate.py --tool measure --check-stale` with no row
   named appends an entry to that committed file, and the bracket runs this task
   is required to make are exactly two such invocations. Expected, not a stray
   edit — but it means **the closing bracket itself dirties the tree**, which
   nothing in the bracket instruction says.
4. ⚠ **I did not decide the `-lm` question** (§2 B1). Adding one token to
   `build.py` costs the PAT programme a 33-row re-measure and buys every future
   php row a verbatim libm call. It is a manager decision.
5. ⚠ **I did not repair `check_sanitizers_hardened`** (§2 B2). The repair is a
   `harness/check.py` edit and a 33-pattern re-gate, and the design question —
   whether a php row may declare that its `fix_commit` is incomplete — is not
   mine to settle.
6. **Unsure: whether `required[3]`'s prose entry earns its place.** It carries no
   backticked spelling, so it pins nothing mechanically; it is there because
   *"R1h is the 2004 fix and nothing else, and R2–R5 carry the 2014 one too"* is
   the row's most load-bearing convention and a reader needs it inside the
   hashed block. A reviewer may reasonably say it belongs only in `why`.
7. **Unsure: whether folding `total_len` bytes rather than `p − *dest` bytes is
   the right oracle.** It is what PHP does (`RETURN_STRINGL(dst, dst_len, 0)`),
   and it is what makes the fold's bound a real proof obligation — which is how
   `lemma_emit_covers_declared` came to exist. But it means the C wrapper reads
   `dest[0 .. total_len)` on an adversarial input where `total_len > cap`, i.e.
   **a second out-of-bounds site the wrapper adds**. Under ASan the decoder
   faults first on every shipped input, so it is never reached — but I cannot
   prove it never could be, and a reviewer should attack it.
8. **Unsure: the `Ir` fixed-term decomposition.** §8's "fixed `Ir`/call" column
   is `small − 120 × marginal`, a two-point extrapolation. The *ordering* (C
   ~150 above Rust) is robust and mechanism-backed; the exact values are not.

---

## §13 Memory updates

**None written.** `PROTOCOL.md` rule 9: *"Do not write a finding into `.memory/`
before its review lands."* Every durable fact from this task is in
`patterns-php/ph03-uudecode-bound/NOTES.md` (measured claims, per rule 9's
ordering) and in this report; `.memory-php/` is the manager's to write **after
the review**, from the reviewed text.

⚠ Candidates I would nominate, in the order I would land them:

1. **`build.py` links no `-lm`** — §2 B1. Affects every future php row that
   touches `math.h`.
2. **`check_sanitizers_hardened` vs `PROTOCOL_PHP.md` §C** — §2 B2. A structural
   tension, not a bug in this row.
3. **Which sanitizer limb fires is decided by the source buffer's slack** — §5.
   An oracle-design rule for every row whose two limbs share one bound.
4. **A safety check can have negative instruction cost, and the sign is
   compiler-dependent** — §8a, with the `setae`/`cmove` mechanism.
5. **The tally-in-the-checksum technique does not carry to an
   allocator-dependent row** — §11.
