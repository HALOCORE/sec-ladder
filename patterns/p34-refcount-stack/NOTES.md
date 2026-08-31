# p34 — manual reference counting: the measurements

`README.md` is the summary; `spec.md` carries the reasoning and the pins; this
file carries the numbers and the arguments they support. Every figure below was
produced by a script in `controls/` or by `harness/measure.py`, and each section
names the one that produced it.

⚠ **PROTOCOL definition-of-done rule 6 disclosure is section 0.** Read it before
quoting anything here.

---

## 0. The contract hash, and an honest note about WHEN it was written

**`contract_sha256` as first written, before any measurement:**
`1fa98c8af297710166a2c93731f12b45be7c2c9b4dc39331fcd06203fae8f3dd`

Recorded at the moment the `slb-contract` block was first written and **before
`harness/build.py`, `harness/check.py` or `harness/measure.py` had ever been run
on `p34`** — at that point `results/gate/p34-refcount-stack.json` and
`results/p34-refcount-stack.json` did not exist.

⚠ **A SPAN ERROR IN THE FIRST RECORDING, DISCLOSED RATHER THAN OVERWRITTEN.**
`.temp/t154/NOTES.md` first wrote that hash as
`7216cbf11a642b3d8fe46150dc6ca3c7f7c5d98c2f05c0e2db4c50d3e4a1faa3`, which is the
same block hashed over a span **one newline shorter** than the one
`harness/check.py::read_contract` uses (`r"```slb-contract\s*\n(.*?)```"` keeps
the trailing newline; the scratch note's regex did not). Same bytes, different
span; the figure above is the one the gate computes and the one to compare
against. The scratch note is kept as it was written.

⚠⚠ **AND ONE PIN MOVED AFTER THE FIRST FULL GATE RUN.** The block as first
written carried **all five** of vstd's `allocate` `ensures` on `rec_alloc`. The
first full run's **stage 5c reported `ensures[1]` — `pt.0.addr() + size <=
usize::MAX + 1` — NOT LOAD-BEARING**: deleting it still gave `24 verified,
0 errors`. A trusted item's `ensures` is an axiom, and one nothing depends on is
an unchecked claim about real Rust semantics carried for free, so it was deleted.
**That is a strict WEAKENING of a trusted item, which is the direction the gate
asks for, and it is the gate's finding rather than the author's judgement.**

| | value |
|---|---|
| as first written (all five `ensures`) | `1fa98c8af297710166a2c93731f12b45be7c2c9b4dc39331fcd06203fae8f3dd` |
| **as shipped** (four `ensures`) | `f1537d7f601175122e67f9991a107449ad7ca52520b0484f5f014685369d2762` |

**Nothing else in the block changed**, and the delta is checkable with
`python3 harness/tools/contract_diff.py p34` once the pattern is committed. The
edit also moved `verus.rs` and `unsafe.rs` doc comments (§6d), which are
MEASUREMENT-hashed, so `harness/measure.py p34` was re-run: **every `Ir`, every
static count and every md5 in `results/p34-refcount-stack.json` is unchanged** —
an `ensures` is ghost and erases before codegen.

⚠ **Disclosed precisely rather than tidily**, because `p46` shipped a rule-6
disclosure that reconstructed *perfectly* over a `why` that measurement had
already falsified. **Three pins in that first block came from PRE-GATE probes
rather than from imagination**, and they are named here so a reviewer can see
which numbers were not invented:

| pin | value | where it came from |
|---|---|---|
| `verus.obligations` | 24 | `.temp/t154/verus/obligations.{sh,log}` — a `--verify-function` census, one Verus run per item |
| `verus.twin_obligations` | 29 | `./verus_run.py verus.rs --cfg slb_twin` |
| `identity` `O0`/`O3` | `norel`/`norel` | `harness/asm.py diff` on hand-built `--cfg slb_isolated` pairs |

⚠ **`git show HEAD:patterns/p34-refcount-stack/spec.md | diff - …` is VACUOUS on
a new pattern** and is deliberately not cited: it compares the working tree to
HEAD, and `p34` lands in one commit, so on a clean tree it always prints nothing
and always looks like it passed. The recorded hash above is the only evidence.

⚠ **Rule 6's added step, applied**: every number in the hashed `why` and in every
rung source's doc comment was re-read against the measurements below before this
file was finished. The `why` asserts `+1 / −0` (§4 measures it), `0.00` (§4
measures it), *checksums bit-identical on two shapes* (§2), *UBSan silent* (§2),
*78 lines and no `Rc` spec* (§6), and *`global layout` checked by rustc* (§6a).
None was falsified.

---

## 1. What the row is

A stack of at most `CAP = 16` references to heap objects. Every object carries
its own count in its own first word:

```c
struct p34_obj { size_t rc; size_t len; uint8_t data[8]; };
```

`NEW` allocates one with `rc = 1` and pushes it. **`DUP` publishes a SECOND
reference to the object on top of the stack.** `POP` releases one reference and
frees at zero. `READ` folds `data[0]` through the `a % ntop`-th reference. The
epilogue releases every reference the window left behind.

`c/kernel.c` omits the `rc++` that `DUP` owes. **The read path is correct in both
rungs and asks nothing wrong**: a refcounted pointer is valid by construction, so
no test the read could grow would repair this program without becoming a liveness
table. **The free happens EARLY rather than the read happening LATE** — which is
what makes it a different C program from `p27`, `p29` and `p32`, all three of
which are repaired by a conjunct on the READ path.

**Layout note, disclosed the way `p28` discloses its own.** The count comes
first, so glibc's tcache `next` and `key` words — user offsets 0 and 8 — land on
`rc` and `len` and never on `data`. That is the idiomatic layout for a refcounted
buffer (SDS, `PyBytesObject`, `GBytes` all look like it), and it is why §2's
first two rows are checksum-blind.

---

## 2. The two bug classes, and which instrument sees them

`controls/detectors.py`, **twelve build lines** — plain / ASan / UBSan × gcc /
clang × `-O0` / `-O3` — on all seven non-sweep inputs, both C rungs.
⚠ Twelve rather than `p35`'s five because `.temp/mgr149/NOTES.md`'s table, which
this row's headline came from, was **gcc `-O1` only**, and `TASK_154` required
it re-derived before publication. **Every figure in it reproduces, and nothing
in it depends on the compiler or the optimisation level.**

| input | R1 checksum | R1h checksum | | ASan on R1 | UBSan on R1 |
|---|---|---|---|---|---|
| `adversarial-blind` | 5576862673510090752 | 5576862673510090752 | **IDENTICAL** | fires | silent |
| `adversarial-blindread` | 12442434272084377600 | 12442434272084377600 | **IDENTICAL** | fires | silent |
| `adversarial-recycle` | 16102462438644451328 | 7544618244297525248 | diverges | fires | silent |
| `adversarial-many` | 5628475829885786112 | 2893199866468423680 | diverges | fires | silent |
| `degenerate` / `small` / `large` / `adversarial-stride3` | — | — | identical | clean | silent |

The same four rows hold on all four **plain** build lines (gcc/clang × `-O0`/`-O3`)
and ASan fires on all four **ASan** build lines. R1h is clean on every input on
every one of the twelve.

**Why the first two are blind.** The release path folds the constant `2`
regardless of what `rc` reads, and `data` is clear of the tcache words, so a
stale read returns the right byte. **Only ASan distinguishes the rungs there** —
which is exactly the shape a checksum-only gate misses.

**Why the third diverges.** glibc's tcache is LIFO, so the `NEW` after the `POP`
gets the freed block back and writes its own payload into it; the stale entry
then reads *another object's* byte.

⚠ **UBSan's silence is DERIVED, not merely observed.** R1's undefined behaviour
is entirely temporal: `stk[ntop-1]` runs only under `ntop > 0`, `stk[ntop]` only
under `ntop < CAP`, and READ's index is `a % ntop` under `ntop > 0`, so every
index is inside `stk[]` in both rungs and there is no spatial violation to see.
**And it is LICENSED**: `controls/ctl_ubsan.c` fires `runtime error: signed
integer overflow` on all four UBSan build lines and is silent on all four plain
ones, while `controls/ctl_asan.c` fires `heap-use-after-free` on all four ASan
lines and is **silent on every UBSan line** — which is the measured evidence for
*a positive control licenses only the detector it fires in* rather than an appeal
to it.

**Reproducibility.** `n = 1` distinct value in **20 runs** on every row at
`iters = 1` (gcc and clang × `-O0`/`-O1`/`-O3`) and at `iters = 4` and
`iters = 200 000` (gcc and clang × `-O0`/`-O3`); single runs at `iters = 10` and
`1000` agree with them across all six builds
(`.temp/t154/repro_t154.log`, `.temp/t154/repro_hi_t154.log`).
⚠ **That last column is a cell `.temp/mgr149` did not have and it mattered**:
R1's release path *writes* `o->rc - 1` into a freed block, which lands on glibc's
tcache `next` word, and the pattern harness calls the kernel up to 200 000 times
per run. It does not compound: no crash, no abort, and the checksum is identical
on all six builds at every iteration count. ⚠ p27's `adversarial-noreuse`
hazard — a stale read whose value is ASLR-dependent and therefore not
reproducible — does not reach p34's shipped inputs, for the layout reason in §1.

**No matrix input executes a DUP.** `controls/no_dup.py`, censusing the shipped
blobs by walking the cursor the rungs walk:

```
input                             stride  nwin     NEW     DUP     POP    READ
adversarial-blind.bin                 36     1       4       4       8       0
adversarial-blindread.bin             44     1       4       4       8       4
adversarial-many.bin                 388     1      48      36      84      24
adversarial-recycle.bin               60     1       8       4      12       4
adversarial-stride3.bin                3     0       0       0       0       0
degenerate.bin                        72     1      21       0       5       8
large.bin                            244    64    3441       0    2309    1930
small.bin                             52     8      80       0      59      53
  executed DUP ops on MATRIX inputs      : 0
  executed DUP ops on ADVERSARIAL inputs : 48
```

---

## 2a. ⚠⚠⚠ The novelty claim this row was launched with is FALSE on both halves

`TASK_154` carried it as a belief to be attacked rather than a fact to inherit:

> *"no built temporal row has a cell that is reproducible AND checksum-divergent
> AND detector-firing at once, and nothing in the tree has the detector-only
> pair"*

`.temp/t154/novelty.py` derives both halves from **every** `results/gate/p*.json`.
Definitions, all read out of the RECORD and never from a log: *detector-firing* =
`sanitizer[<input>].fired`; *checksum-divergent* = `diverges` on the C R1 rows of
`adversarial[<input>/c-gcc|c-clang]`; *reproducible* = those rows carry exactly
ONE behaviour across opt × mode and both compilers agree.

| half | claim | verdict | counterexamples |
|---|---|---|---|
| 1 | no built temporal row has the TRIPLE | **FALSE** | `p27/adversarial-uaf.bin` and **all four** of `p28`'s (`-many`, `-uaf-head`, `-uaf-read`, `-uaf-write`). 31 such cells tree-wide. |
| 2 | nothing in the tree has the PAIR | **FALSE** | `p18/adversarial-sat.bin`, `p42/adversarial-mixed.bin`, `-notag.bin`, `-win1.bin`. |

**What survives, and it is narrower than the sentence it replaces:**

* `p18` is the `ub-not-mem` axis (a saturating shift; the detector is UBSan) and
  `p42` is `resource` (a leak; the detector is LSan). **`p34` is the first
  TEMPORAL row with a detector-only cell**, and it has two.
* ⚠ **"Both shapes in one row" is NOT new either** — `p18` already carries three
  triples and one pair. What `p34` adds is both shapes **where the detector is
  ASan and the harm is a use-after-free**: the silent cell is a read of freed
  heap that returns the right byte because of the disclosed layout.

⚠ **This is the third time an axis claim written into a task file as fact has
turned out false** (`RECAP` item 4 records the first two), and both halves were
settled by one derivation over records that were already on disk. **Do not quote
the retracted sentence.**

---

## 3. Correctness across the rungs

All seven rungs agree with `model.py` on all seven inputs, and R1 agrees on the
three non-DUP ones. `harness/check.py` stage 2 covers the 32 measured cells;
`controls/detectors.py` re-covers the two C rungs across twelve build lines.

`model.py` derives `sanitizer_expect` rather than declaring it, which
`TASK_154`'s deliverable 2 predicted would be impossible — *"Python has no
dangling pointers, so p34's harm is very likely UNREPRESENTABLE in the model by
construction. DECIDE THAT FIRST."* **The decision is that it IS representable**,
and the reason is worth stating: what ASan reports here is not a dangling
*pointer*, it is *a touch of an object whose storage has been returned to the
allocator*, and that is a property of the OBJECT, which Python models exactly.
`Pool.release` sets `Obj.freed` when the count reaches zero, every field access
the buggy simulation performs goes through `Pool.touch`, and `_Escape` makes the
detector **report** rather than crash.

⚠ **And it can fire.** `model.py::detector_selftest()` is a six-cell must-fire
arm that `selfcheck()` runs on every gate invocation: the same three probe
windows under both semantics — `NEW NEW POP POP` (silent both ways),
`NEW DUP POP POP` (silent hardened, **fires** buggy, `o->rc (release)`) and
`NEW DUP POP READ` (silent hardened, **fires** buggy, `o->data[0] (read)`).
The no-DUP pair is the control that stops a detector which fires on everything
from passing.

The two implementations inside `model.py` disagree about what a reference *is*:
the simulation is object-based with an explicit per-object count and a `freed`
flag, and the helper `rc_fold` — the one the derived `ensures` is evaluated
against, and the mirror of `verus.rs`'s `run` — **has no reference count in it at
all**, because under the checked semantics an object is alive exactly while some
stack entry names it. That is a real independence: R1's bug is precisely that a
third representation, the count in the object's own first word, falls out of step
with the stack the other two agree about.

---

## 4. THE SAFETY LINE: `+1 / −0`, and `0.00`

### 4a. `+1 / −0`, the smallest safety line in this tree

`controls/safety_line.py`, on the SHIPPED files with `cc -E -P`:

```
A. the two SHIPPED files, preprocessed
     kernel.c          332 line(s)
     kernel_hardened.c 333 line(s)
     diff  +1 / -0
       + t->rc = t->rc + 1;
B. the include-twice construction reproduces both shipped files
     SLB_HARDEN 0 vs c/kernel.c                 IDENTICAL (332 vs 332 line(s))
     SLB_HARDEN 1 vs c/kernel_hardened.c        IDENTICAL (333 vs 333 line(s))
```

⚠ **B is p34's addition to `p32`'s control and it is the half that matters.**
A diff of two hand-written files proves the difference is SMALL; it cannot prove
it is the INTENDED one. `controls/arm_body.inc` is `TASK_143`'s include-twice
body, and requiring it to preprocess to each shipped file *exactly* is what says
the two rungs really are one body plus one `#if`. Neither construction can make
that claim alone: the include-twice form cannot fail, and the diff cannot speak
about intent.

### 4b. `0.00` — predicted from the proof, then measured

**The prediction, written before the measurement** (`spec.md`'s `why`, hashed at
the sha256 in §0): the R1-vs-R1h benign gradient is `0.00` **by construction**,
because the safety line is the only increment in the kernel, so any executed
`DUP` in R1 ends in a use-after-free, so no input on which the rungs agree can
contain one.

**The measurement** (`.temp/t154/marginal.py`, the same difference-of-two-runs
method `harness/check.py::check_marginal_ir` uses: Ir at 200 iterations minus Ir
at 100, over 100):

| | small `-O0` | small `-O3` | large `-O0` | large `-O3` |
|---|---:|---:|---:|---:|
| **R1h − R1, gcc** | **+0.00** | **+0.00** | **+0.00** | **+0.00** |
| **R1h − R1, clang** | **+0.00** | **+0.00** | **+0.00** | **+0.00** |

**All sixteen cells** (2 inputs × 2 opt levels × 2 inline modes × 2 compilers) are
exactly `+0.00`, and the kernel-exclusive `Ir` in `results/p34-refcount-stack.json`
is bit-identical between the arms as well (`c-gcc` and `c-gcc-h` both
171,353,731 on small at `O3/isolated`; both 325,624,819 at `O0/isolated`).
Wall clock agrees within the noise floor: 40.70 ms vs 40.51 ms on small, 31.02 ms
vs 30.98 ms on large, against a 1.3–2.9 % spread.

⚠⚠ **AND THE STATIC COUNT IS NOT ZERO, WHICH IS THE PART WORTH KNOWING.** The
never-executed statement still costs instructions in the binary:

| | R1 | R1h | Δ |
|---|---:|---:|---:|
| gcc `-O3`, `kernel` symbol, pad-excluded | 286 | 287 | **+1** |
| clang `-O3` | 135 | 136 | **+1** |
| gcc `-O0` | 218 | 223 | **+5** |
| clang `-O0` | 203 | 208 | **+5** |

So *"the safety line is free"* is true of **executed** instructions and false of
**emitted** ones, and this row is the cleanest instance of that distinction in the
tree: `0.00` dynamic against `+1` static at `-O3`. A pattern that quoted only the
static column would report a cost that never runs.

---

## 5. The cost axis, with a TWO-SIDED spelling search

⚠⚠⚠ **READ THIS FIRST.** Six patterns in this project have published a
rung-to-rung headline **wrong in the flattering direction** — `p10`, `p27`,
`p38`, `p22`, `p36` and `p35` — every time because one endpoint was searched over
its in-contract spellings and the other was left at whatever the author wrote.
`controls/spellings.py` searches BOTH sides here, and **it caught one on p34**.

### 5a. The shipped cells, marginal Ir per kernel call

`isolated`, the two probe inputs, both levels (`.temp/t154/marginal.json`):

| rung | small `-O0` | small `-O3` | large `-O0` | large `-O3` |
|---|---:|---:|---:|---:|
| `c-gcc` | 3,143.94 | 2,207.05 | 15,579.69 | 11,106.93 |
| `c-gcc-h` | 3,143.94 | 2,207.05 | 15,579.69 | 11,106.93 |
| `c-clang` | 3,130.64 | 2,226.78 | 15,627.76 | 11,293.47 |
| `c-clang-h` | 3,130.64 | 2,226.78 | 15,627.76 | 11,293.47 |
| `safe_naive` (R2) | 6,265.40 | 2,785.16 | 29,015.21 | 13,782.86 |
| `safe_tuned` (R3) | 8,243.33 | 2,558.38 | 38,129.31 | 12,623.43 |
| `unsafe` (R4) | 5,631.32 | 2,364.59 | 27,058.04 | 11,906.72 |
| `verus` (R5) | 5,631.32 | 2,364.59 | 27,057.94 | 11,906.62 |

R5 equals R4 **exactly** on both `small` cells and differs by **0.10 Ir/call** on
both `large` ones — one part in 119 000, well inside the coin-flip band
`results/synthesis.md` publishes. The `identity` pin's assembly evidence (§6b and
`spec.md`'s pin) is what carries the R4 ≡ R5 claim; this column is not.

### 5b. ⚠⚠ THE COMPARISON REVERSES BETWEEN OPTIMISATION LEVELS — TWICE

`p35`'s lesson, and p34 has two independent instances of it:

* **R2 vs R3.** At `-O3` the tuned rung is **8.14 % cheaper** than the naive one
  on small (2,558.38 vs 2,785.16) and 8.41 % cheaper on large. **At `-O0` it is
  31.58 % DEARER** (8,243.33 vs 6,265.40) and 31.41 % dearer on large. The lever
  is `chunks_exact(2).take(nops)`: the iterator machinery is not inlined at
  `-O0`, so R3's "tuning" is a large loss there and a modest win at `-O3`.
* **R4's stack accessor.** `arr_get_unchecked` against plain indexing:
  **at `-O3` the unchecked spelling is 2.24 % cheaper** on small (2,364.59 vs
  2,417.61) and 2.25 % on large, **and at `-O0` it is 7.17 % DEARER**
  (5,631.32 vs 5,227.32) and 7.43 % dearer on large. The mechanism is the same
  one in mirror: `slice::get_unchecked` is a generic std call chain that `-O0`
  does not flatten, while `stk[i]` is a direct index with a compare.

⚠ **So p27's `41.62 Ir/call` figure for its own checked spelling does not
transfer** and this row does not inherit it. Measured here, on this stack, the
unchecked accessor is worth **+53.02 / +267.42** Ir/call at `-O3` and
**−404.00 / −2,009.60** at `-O0`.

### 5c. The two-sided search, and what it corrected

`controls/spellings.py` builds each variant by TEXT SUBSTITUTION from the shipped
rung so it cannot drift, checks every variant against `model.py` on all seven
inputs, measures its marginal at both levels on both probe inputs, and — for the
R4 candidates — **applies the same substitution to `verus.rs` and records whether
it still verifies**, because `spec.md` pins `identity: unsafe ≡ verus` and an
unverified R4 is a control, not a rung.

| variant | side | small `-O0` | small `-O3` | large `-O0` | large `-O3` | Verus |
|---|---|---:|---:|---:|---:|---|
| `safe_tuned` (shipped R3) | R3 | 8,243.33 | 2,558.38 | 38,129.31 | 12,623.43 | — |
| `r3_cursor` (R3's `match`, R2's cursor walk) | R3 | **6,133.33** | 2,775.04 | **28,339.31** | 13,716.39 | — |
| `unsafe` (shipped R4) | R4 | 5,631.32 | **2,364.59** | 27,058.04 | **11,906.72** | `24/0` |
| `r4_checked` (plain stack indexing) | R4 | **5,227.32** | 2,417.61 | **25,048.44** | 12,174.14 | **`24/0`** |
| `r4_readdirect` (`r.data[0]`) | R4 | 5,515.19 | **2,364.59** | 26,446.94 | **11,906.72** | **`24/0`** |

**Two corrections fall out of that table and both are against the author.**

1. ⚠⚠ **The shipped-pair R3−R4 figure at `-O0` OVERSTATES the gap by about
   3×.** Shipped R3 minus shipped R4 is `8,243.33 − 5,631.32 = 2,612.01` on
   small and `11,071.27` on large. **Cheapest-found in contract on each side** is
   `6,133.33 − 5,227.32 = 906.01` and `28,339.31 − 25,048.44 = 3,290.87`. So the
   naive shipped-pair figure is **2.88×** and **3.36×** too large, in the
   direction that flatters `unsafe`. **The `-O0` shipped-pair number is therefore
   not published as a result**; what is published is the span.
   ⚠ At `-O3` the shipped pair IS the cheapest-found pair on both sides
   (`2,558.38 − 2,364.59 = 193.79` on small, `716.71` on large) and the figure
   stands as written.
2. ⚠ **The shipped R4 is NOT the cheapest admissible R4 found at `-O0`.**
   `r4_readdirect` ties it exactly at `-O3` (2,364.59 / 11,906.72 — the same
   number, not a rounding) and beats it by **116.13 / 611.10** at `-O0`, **and it
   verifies at the pinned obligation count**, so it is admissible. It also uses
   one fewer unchecked operation. The shipped rung keeps the accessor spelling
   for uniformity with p27/p29/p32/p35; that choice now has a price tag on it
   instead of an assumption.

**Which endpoint is the weaker-searched one: THE R4 SIDE, and the reason is
structural.** `spec.md` pins `identity: unsafe ≡ verus`, so an R4 candidate is
not merely a program that MAY use `unsafe` — it must have a machine-code-identical
R5 that Verus verifies. Two candidates were put through Verus here and both
passed, which is more than `p05` and `p16` managed (their R4 candidates were
`is not supported` at the pinned vstd), **so p34 is the first pattern in this
project with more than one R4 spelling SHOWN admissible and a measured R4-side
width**: `53.02` / `267.42` Ir/call at `-O3`, `404.00` / `2,009.60` at `-O0`.
The R4 endpoint is no longer degenerate. ⚠ It is still a **found** minimum and
not a minimum (`.memory/01-ladder.md` finding 14).

### 5d. What the cross-language column says

At `-O3`, cheapest-found in contract, `isolated`, per kernel call:

| | small | large |
|---|---:|---:|
| C (gcc) | 2,207.05 | 11,106.93 |
| R4 unsafe | 2,364.59 | 11,906.72 |
| R3 safe tuned | 2,558.38 | 12,623.43 |
| R2 safe naive | 2,785.16 | 13,782.86 |

`unsafe` is **7.14 % / 7.20 %** dearer than C, `safe_tuned` **8.20 % / 6.02 %**
dearer than `unsafe`, and `safe_naive` **8.87 % / 9.19 %** dearer than
`safe_tuned`. ⚠ **Every one of those three gaps is between spellings whose
in-contract width is now measured** (§5c), and the C side has had **no** spelling
search at all, so the C endpoint is the weakest-searched of the four. The
`Ir(main)` column is not comparable Rust-to-C (`results/tables/` says why) and is
not used here.

---

## 6. The R5: what it proves, what it costs, what it does not buy

**`24 verified, 0 errors`**; twin configuration **`29 verified, 0 errors`**.
**TCB: seven `external_body` items** — `buf_get_unchecked`,
`arr_get_unchecked`, `arr_set_unchecked`, `rec_alloc`, `rec_free`, `load_input`,
`emit` — which is `p27`'s seven exactly. **The reference-counting obligation
costs none of them.**

⚠ **TWO DENOMINATORS, AND `TASK_145_REPORT` §8 CAUGHT `p32` MIXING THEM, so they
are separated here.** SEVEN is the ITEM count. **FIVE** is the number inside the
twin regime, which `harness/check.py::_is_trusted` defines as `external_body`
plus either a non-empty `ensures` or `unsafe` in the body: `load_input` and
`emit` have neither, so they cannot axiomatise a falsehood and owe no twin.
**All five that do owe one HAVE one, and the gate record's `blocked` is `[]`** —
which is `p27`'s and `p32`'s position and not `p35`'s, where three union readers
are blocked because Rust has no safe spelling of a union read. §10 has the
per-item arguments and the cross-pattern table.

### 6a. The obligation census, measured rather than predicted

`.temp/t154/verus/obligations.{sh,log}`, one `--verify-function <name>
--verify-root` run per item:

```
cnt 1   lemma_cnt_push 1   lemma_cnt_drop 1   lemma_cnt_zero 1
lemma_cnt_absent 1   lemma_cnt_le 1   run 1
obj_new 1   obj_retain 1   obj_dec 1   obj_read 1   obj_free 1
kernel 3   main 5
u32_at 0  nops_at 0  val_of 0  rc_fold 0  obj_ok 0  wf 0
buf_get_unchecked 0  arr_get_unchecked 0  arr_set_unchecked 0
rec_alloc 0  rec_free 0  load_input 0  emit 0
```

`20` function terms `+ 3` consts (`CAP`, `DLEN`, `SENT`) `+ 1` **`derive` term**
`= 24`. ⚠ **The derive term is measured and not inferred**: adding a second
`#[derive(Clone, Copy)] pub struct` moves the count to **25** and adding a BARE
`pub struct` leaves it at **24** (`.temp/t154/verus/ob_derive.rs`, `ob_bare.rs`).
That reproduces `p29`'s derive term and `p32`'s bare-struct zero on a third
pattern.

**The layout fact is a `global layout` directive and NOT an axiom, and that is
worth knowing.** `vstd::layout::size_of` is **uninterpreted** for a user struct
at the pinned vstd — there is no axiom anywhere in it saying a struct with a
`usize` field is bigger than zero bytes — so neither `rec_alloc`'s `size != 0`
nor `PointsToRaw::into_typed`'s alignment precondition can be discharged without
telling Verus the layout. `global layout Obj is size == 24, align == 8;` does
that, **and rustc CHECKS it at codegen**: measured, with `size == 32` the file
still reports `9 verified, 0 errors` and then fails to compile with
`error[E0080]: evaluation panicked: does not have the expected size`
(`.temp/t154/verus/probe3.rs` vs `probe3_bad.rs`). It carries **zero
obligations**, is not an item, and costs **no trusted item** — it is the one
layout fact in this tree that the COMPILER rather than a reviewer is responsible
for. ⚠ **Adjacent, and reported rather than fixed:**
`harness/vparse.py::axiom_decls` does not recognise `global layout` as a
body-less trusted declaration, so `verus.axioms` neither sees it nor could
declare it. On p34 that is defensible because rustc checks it; on a future
pattern it is a fifth form the gate is blind to.

### 6b. The obligation itself, and why it is not `p27`'s

`p27`'s R5 proves *at the moment of the read, the record still exists*, and one
`PointsTo<u8>` per slot carries it. **p34 cannot do that.** A `PointsTo` is
LINEAR and p34's whole subject is ALIASING — two stack entries naming one object
is the normal, correct state of this kernel — so there is only one permission to
go round. The permission is keyed by OBJECT instead, and the proof carries the
bridge between the two representations:

```
perms[k].value().rc == cnt(ids, k)
```

`cnt` is an occurrence count over a `Seq<int>`, defined recursively with five
supporting lemmas (`push`, `drop_last`, `zero ⇒ absent`, `absent ⇒ zero`,
`cnt ≤ len`). To the best of this project's knowledge it is **the first
multiset-flavoured obligation in the tree**: every other R5 here proves a spatial
fact about one index, or (p27, p29) a liveness fact about one slot.

**Leak-freedom is a COROLLARY rather than a second obligation.** `obj_ok`
requires `cnt(ids, k) > 0` for every key in the permission map, and the epilogue
runs until the stack is empty, so `perms.dom()` is empty when the kernel returns
— which is what the `assert(perms.dom() =~= Set::<int>::empty())` at the end of
the kernel says. ⚠ **What it does NOT say**: Verus does not force a tracked
resource to be consumed, so a rung that simply dropped the map would verify. What
is proved is that THIS rung's map is empty, not that any rung's must be.
`controls/proof_mutants.py`'s `M3` deletes the epilogue and that assertion is
what fails.

### 6c. The mutation battery, and the one arm that separates p34 from p32

`controls/proof_mutants.py`, six arms, `--rlimit 200`, all as expected:

| arm | kind | expect | got | diagnostic |
|---|---|---|---|---|
| `M0-control` | control | verify | `24 / 0` | — |
| `M1-delete-retain` | **attack** | fail | `23 / 1` | `assertion failed` |
| `M2-constant-body` | vacuity | fail | `21 / 1` | `postcondition not satisfied` |
| `X1-delete-rc-conjunct` | attack | fail | `22 / 2` | **`precondition not satisfied`** |
| `X2-exec-and-spec` | spec-weaken | fail | `22 / 2` | **`precondition not satisfied`** |
| `M3-delete-epilogue` | deletion | fail | `23 / 1` | `assertion failed` |

⚠⚠ **`X1` and `X2` are the two to read, and both come from other rows' results.**

* **`X1` is `p35`'s arm.** Strike the central obligation out of the invariant and
  see whether anything but a hand-written pin notices. **On `p35` the equivalent
  deletion VERIFIED** at the pinned obligation count, and only the `verus.items`
  pin caught it — which is the sharper half of that row's headline. **On `p34` it
  FAILS, on a `precondition not satisfied`.** The bridge is what discharges
  `obj_dec`'s `requires rc > 0` and what licenses `obj_free` at zero, so it is a
  memory-safety precondition rather than a refinement clause.
* **`X2` is `p32`'s arm.** Weaken the exec code AND the invariant so the two
  agree with each other again. **On `p32` that VERIFIES**, and p32 publishes it
  as the honest statement of what its R5 buys: its safety line is load-bearing
  against the SPECIFICATION alone, because nothing there is allocated and there
  is no linear resource to consume. **On `p34` it FAILS**, again on a
  precondition. **That is the sharpest difference between the two rows' R5
  results, and it is exactly the difference the storage makes.**

### 6d. What the pinned vstd does not have

`~/tools/verus/vstd/std_specs/smart_ptrs.rs` is **78 lines** and has **no
`strong_count`, no `Rc::clone`, no `into_raw`/`from_raw` and no
`increment_strong_count`**, so there is no route to a proof *about* `Rc`'s counter
at this pin. **That is a RESULT and it is reported as one, not a reason to shrink
the row**: the R5 models the counter itself in a raw-pointer rung, which is what
the C rung does anyway, and the `Rc` port's finding (§8) is measured on the
compiler rather than on the prover.

⚠ `rec_alloc` here ships **FOUR** of vstd's five `ensures` where `p27` ships
three, and the difference from p27 is the ALIGNMENT conjunct: p27 allocates a
`u8` at `align == 1`, so `pt.0.addr() % align == 0` is trivial there and its gate
found it not load-bearing, while p34's object is `align == 8` and
`into_typed::<Obj>` needs it. **The gate's stage 5c re-derives that every run —
and on the first full run it also found the one BOTH patterns now drop.**

⚠⚠ **THE FIFTH CONJUNCT WAS DELETED BECAUSE THE GATE SAID SO, AND THAT IS THE
CORRECTION WORTH READING.** The pattern as first written shipped all five, on the
author's reasoning that a copy of vstd's item should be a faithful copy. Stage 5c
disagreed, out loud:

```
[clause-mut] verus.rs rec_alloc ensures[1] is NOT load-bearing: deleting
`pt.0.addr() + size <= usize::MAX + 1` still gives 24 verified, 0 errors.
A trusted item's `ensures` is an axiom; one that nothing depends on is an
unchecked claim about real Rust semantics carried for free, and the TCB tally
counts it as an obligation the reviewer must judge.
```

It was deleted. `§0` records the `contract_sha256` move, `harness/measure.py` was
re-run because the doc comments live in measurement-hashed files, and **every
number in `results/p34-refcount-stack.json` is unchanged** — an `ensures` erases
before codegen. **A faithful copy of a trusted item is not automatically the
right one: the gate's question is what the shipped proof DEPENDS on, and it is a
better judge of that than the author.**

---

## 7. Miri

`spec.md`'s `miri.reason` publishes a claim about SILENCE: **what Miri finds on
the shipped `unsafe.rs` is NOTHING, on every input including all five adversarial
ones.** A silence claim owes a control that can break it
(`.memory/03-measurement.md` entry 14; RECAP trap 5), and `controls/rust_bug.py`
is it.

`controls/arm_unsafe_bug.rs` is **`unsafe.rs` with `obj_retain(t);` deleted and
nothing else**, and `rust_bug.py` **re-derives that at every run** — it reads both
files, deletes the retain from the rung, normalises the one legitimate difference
(a control sits one directory deeper, so the `#[path]` gains a `../`) and requires
the result to equal the arm exactly. So the two cannot drift.

| | `adversarial-blind` | `-blindread` | `-many` | `-recycle` | `-stride3` | `degenerate` | `small` | `large` |
|---|---|---|---|---|---|---|---|---|
| **bug arm** | **UB** | **UB** | **UB** | **UB** | no UB | no UB | no UB | no UB |
| **shipped `unsafe.rs`** | no UB | no UB | no UB | no UB | no UB | no UB | no UB | no UB |

Miri fires on **exactly** the four inputs `model.py` derives as
`sanitizer_expect: fires` and on none of the others, so the firing is caused by
the missing retain and not by the arm being a control. The diagnostic is
`constructing invalid value of type &Obj` / `&mut Obj` — a dangling reference,
which is where Miri catches a use-after-free in Rust rather than at the load.

**And the bug arm reproduces `c/kernel.c` bit for bit on all eight inputs**,
including the recycle-divergent one (16102462438644451328). So the Rust port is
faithful on the buggy path too, and the divergence is the allocator's LIFO
recycling rather than anything about C.

---

## 8. The safe-Rust experiment: BOTH branches of the law, in ONE row

`.memory/01-ladder.md`'s law is *safe Rust's temporal guarantee is a guarantee
about the ALLOCATOR; a structure that recycles its own storage gets no guarantee
at all.* Outcome 3 had three demonstrations and they disagreed: `p32`'s safe Rust
reproduces the buggy C bit for bit, `p28`'s cannot reproduce it at all, and `p35`
shows both shapes on a non-temporal axis. **`p34` has both TEMPORAL branches, and
the selector is the PORT rather than the pattern.** `controls/safe_arms.py`:

### Branch A — the `Rc` port: the bug is NOT EXPRESSIBLE

```
  safe_naive.rs            COMPILES   -        (the sanity arm)
  arm_safe_rc_move.rs      REJECTED   E0507    cannot move out of `*t` which is behind a shared reference
  arm_safe_rc_borrow.rs    REJECTED   E0502    cannot borrow `objs` as mutable because it is also borrowed as immutable
```

The two arms cover the two ways a program could hold a second reference at all —
**own it** or **borrow it** — and safe Rust closes both, for two different
reasons. `Rc::clone` publishes the second reference and increments in ONE
operation and there is no way to obtain a second `Rc<Obj>` without it; a borrow
cannot be stored in the stack array because the borrow checker ties it to the
array it came from. **`c/kernel.c`'s bug is exactly the separation of *publish a
reference* from *count it*, and safe Rust does not offer the separation.**
⚠ The sanity arm matters: two files that fail to compile prove nothing unless a
third one on the same command line succeeds.

### Branch B — the index-arena port: it reproduces `c/kernel.c` BIT FOR BIT

`controls/arm_safe_arena.rs`, `#![forbid(unsafe_code)]`, one `#[cfg]` as the
safety line:

| input | arena, retain absent | `c/kernel.c` | arena, retain present | `model.py` |
|---|---|---|---|---|
| `adversarial-blind` | 5576862673510090752 | **same** | 5576862673510090752 | same |
| `adversarial-blindread` | 12442434272084377600 | **same** | 12442434272084377600 | same |
| `adversarial-many` | 5628475829885786112 | **same** | 2893199866468423680 | same |
| `adversarial-recycle` | 16102462438644451328 | **same** | 7544618244297525248 | same |
| `degenerate` / `small` / `large` / `-stride3` | — | **same** | — | same |

**8 of 8 inputs, bit for bit, including the recycle-divergent one** — safe Rust
under `forbid(unsafe_code)` reproducing the exact output of a use-after-free. The
free list is LIFO precisely because glibc's tcache is; a FIFO list would not
reproduce it and would be measuring a different allocator.

⚠ **And Miri is silent on the arena arm on every input.** Nothing is allocated in
that kernel — the arena is a local — so there is no deallocation for Miri to see.
That is the `p32` half of the detector-coverage result, and it is what makes the
storage choice load-bearing rather than incidental.

### What this settles, and what it does not

**The manager's prediction in `TASK_154` was that an owned/`Rc` safe port should
land in `p28`'s shape and an index-arena port in `p32`'s, putting both branches
of the law in one row selected by the port choice. It is CONFIRMED, and the
arena arm is stronger than predicted**: it does not merely reproduce the bug, it
reproduces the **recycle divergence** — the one cell whose value depends on the
allocator handing the same block back.

⚠ What it does **not** settle: this says nothing about which port an author would
choose. Both are idiomatic; the `Rc` one is what `safe_naive.rs` and
`safe_tuned.rs` ship, and the arena one is what a Rust programmer writes the
moment the object graph stops being a tree. **`Rc::clone` incrementing
unconditionally is a finding about what safe Rust removes — the SITE of the bug —
and not a claim that safe Rust removes the bug CLASS.**

---

## 9. What is not here

* **No leak axis.** `.memory/01-ladder.md`'s outcome 4 — *the safe rung is worse
  than C* — is the `Rc` CYCLE leak and is scoped to the statically-asymmetric
  doubly-linked-list case. `p34` is the PREMATURE-FREE class only. Adjacent and
  cheap if anyone wants it: neither C rung leaks on any shipped input (ASan's
  LSan is on in `controls/detectors.py`'s ASan lines and reports nothing), and
  R1 cannot leak — it frees too EARLY, not too late.
* **No `-O1` column.** The tree measures `-O0` and `-O3`;
  `.temp/t154/repro_t154.log` carries `-O1` for the demonstration only, where it
  agrees with both.
* **No C-side spelling search.** §5d names the C endpoint as the
  weakest-searched of the four and does not publish a C-to-Rust ratio as a
  bound.
* **No `Weak`/`Arc` arm.** Both are `forbidden` in `spec.md`: a weak reference is
  not a reference for the purpose of this count, and an atomic count would be a
  different cost axis in a single-threaded kernel.

---

## 10. SLB-TRUSTED-ARGUMENT sections

The gate requires one section per trusted item **as
`harness/check.py::_is_trusted` defines one** — `#[verifier::external_body]`
**with a non-empty `ensures`, or `unsafe` in the body** — and prints it in full on
every run. **It required FIVE for p34**, and there are five below.

⚠ **FIVE is not the same denominator as §6's TCB tally, and the two are easy to
mix** (`TASK_145_REPORT` §8 caught p32 doing exactly that):

| | `#[verifier::external_body]` items | sections the gate required |
|---|---|---|
| **`p34`** | **7** | **5** |
| `p27` | 7 | 5 |
| `p29` | 7 | 7 |
| `p32` | 5 | 3 |

The two p34 items the gate does **not** govern are `load_input` and `emit`: they
carry no `ensures` and no `unsafe`, so they cannot axiomatise a falsehood, which
is the property `_is_trusted` is keyed on. **§6's sentence — *"TCB: seven
`external_body` items"* — is the ITEM count and is correct, and §6 now separates
the two denominators explicitly rather than leaving it to this table.**

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's is `v[i]` on the same
`&[u8]`, with the same parameters and character-identical clause text. `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < v.len()` that `get_unchecked` requires of the caller — so a `requires` too
weak to license the unchecked read is too weak to license the indexed one, and
`--cfg slb_twin` rejects it. The gate re-derives that every run: deleting
`i < v@.len()` alone makes the twin fail at `28 verified, 1 errors`. This is the
same item every unsafe rung in this project ships and it is unchanged here.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly ONE unchecked operation — a read of
one element — and returns it. `r == v@[i as int]` names that element and its
value, and `v: &[u8]` is immutable so nothing can be modified. The completeness
question is `TASK_009_REVIEW`'s x4: a body that ALSO read `i + 1` would satisfy
this contract, this twin and the `--cfg slb_twin` run unchanged, and nothing in
the gate would notice. **What stands behind (b) here is that the body is one
expression, printed in full in every verdict, and Miri interprets the shipped
`unsafe.rs` on all eight inputs (§7).**

**(c) Does each clause mean the same in both configurations?** `v@` is
`vstd::slice`'s view and `v@.len()` is `spec_slice_len(v)` in both; neither is
`#[cfg]`-dependent, and the token `slb_twin` occurs nowhere but on the twin's own
attribute — which the gate checks and prints.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a)** Trusted body `unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; twin body
`v[i]` on the same type, same generic parameters, character-identical clauses.
Array indexing is the checked form of the same operation and rustc emits
`i < N`. Deleting `i < v@.len()` alone makes the twin fail (`28 / 1`).
⚠ **On p34 this item is used at TWO different instantiations** — `[*mut Obj; CAP]`
for the reference stack and `[u8; DLEN]` for the object payload — which is why it
is generic: one axiom instead of two. Both instantiations are the same operation.

**(b)** One unchecked read, one returned value, `v` immutable. The x4 gap is the
same as `buf_get_unchecked`'s and is closed by the same two things: a one-line
body printed in every verdict, and Miri. ⚠ **`controls/spellings.py` measures the
alternative**: replacing this item's uses on the stack with plain indexing still
verifies at `24 / 0` and is 2.24 % DEARER at `-O3` and 7.17 % CHEAPER at `-O0`
(§5), so the trust this item buys has a price tag on it in both directions rather
than an assumption.

**(c)** `v@` for an array is `vstd::array`'s view and `v@.len() == N` in both
configurations; nothing here is `#[cfg]`-dependent.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a)** Trusted body `unsafe { *v.get_unchecked_mut(i) = x; }`; twin body
`v[i] = x;`. The checked store is the same operation with rustc's bounds test in
front of it, and deleting `i < old(v)@.len()` alone makes the twin fail
(`28 / 1`).

**(b)** The body performs ONE unchecked operation, a store, and the `ensures` is
a WHOLE-SEQUENCE equality — `final(v)@ == old(v)@.update(i as int, x)` — not a
statement about slot `i` alone. That is what closes the x4 gap here in a way it
is not closed for the two readers: a body that also wrote `i + 1` would violate
`update`, because `update` says every other index is unchanged. ⚠ **This is the
strongest of the five (b) arguments and it is worth saying why: a `set`'s
postcondition can quantify over what did NOT change, and a `get`'s cannot.**

**(c)** Same as `arr_get_unchecked`. ⚠ `x` is a pure VALUE parameter and carries
no precondition; `spec.md`'s `verus.unsafe_justifications` says so and the gate
shouts it every run. Every `T` is a legal thing to store in a `T` slot, and the
two parameters that DO decide whether the store is defined, `v` and `i`, are both
constrained.

## SLB-TRUSTED-ARGUMENT verus.rs rec_alloc

**(a) The twin is not a checked re-implementation — it is `vstd::raw_ptr::allocate`
ITSELF**, and that is a stronger arrangement than the three accessors above. This
item exists for a CODEGEN reason and not a trust one: vstd carries no `#[inline]`
on `allocate`, so an R5 that called it directly would emit a GOT-indirect
cross-crate `call` that `unsafe.rs` cannot produce and the `identity` pin would
drop (p27's TASK_055 measurement). Because the twin's body is
`allocate(size, align)`, the gate proves every run that **this item's contract is
no stronger than the one vstd already discharges** — a copy that had
STRENGTHENED a clause would not verify. Deleting either `valid_layout(size,
align)` or `size != 0` alone makes the twin fail (`28 / 1` each).

**(b)** The body is vstd's, with `alloc::alloc::` respelled `std::alloc::`, and
its unchecked operations are `Layout::from_size_align_unchecked` (licensed by
`valid_layout`) and `alloc` (licensed by `size != 0`, with the null return
handled by `abort`). The `ensures` ships **four of vstd's five**, which is a
strict WEAKENING; the fifth was deleted because **stage 5c found it not
load-bearing** (§6d), and a weakening cannot make an axiom say more than vstd's
does. ⚠ The remaining four are all load-bearing on this pattern and stage 5c
re-derives that: in particular `pt.0.addr() as int % align as int == 0` is what
`PointsToRaw::into_typed::<Obj>` needs at `align == 8`, and p27 could drop it
only because its records are `u8` at `align == 1`.

**(c)** `valid_layout`, `PointsToRaw`, `Dealloc` and `DeallocData` are vstd's own
and are not `#[cfg]`-dependent. ⚠ **One thing that IS p34-specific and belongs
here**: the caller passes `core::mem::size_of::<Obj>()` and
`core::mem::align_of::<Obj>()`, and what makes those usable at all is the
`global layout Obj is size == 24, align == 8;` directive — **which rustc checks
at codegen** (§6a), so it is the one fact in this item's neighbourhood that a
reviewer does NOT have to take on trust.

## SLB-TRUSTED-ARGUMENT verus.rs rec_free

**(a) The twin is `vstd::raw_ptr::deallocate` ITSELF**, for the same codegen
reason as `rec_alloc`, so the gate proves every run that this contract is no
stronger than vstd's. All **six** of vstd's `requires` are shipped verbatim in
meaning, with one respelling: vstd destructures its tracked parameters and writes
`dealloc.addr()` where this item takes plain `dealloc` and writes
`dealloc@.addr()`. Deleting any ONE of the six alone makes the twin fail
(`28 / 1` for each of the six, printed in the verdict).

**(b)** The body performs two unchecked operations,
`Layout::from_size_align_unchecked` and `dealloc`, and the six `requires` are
exactly the conditions the standard library documents for the second: the pointer
came from this allocator, with this layout, and the caller is giving up the
permission. The item has **no `ensures` at all**, which is the right shape — it
CONSUMES two tracked resources and promises nothing — and that is also what makes
the temporal argument work: after this call the caller has no permission to
present, so a later touch of the same object is unprovable rather than merely
wrong. **`controls/proof_mutants.py`'s `M1` and `X2` are what demonstrate that,
and both fail.**

**(c)** Same vstd types in both configurations; nothing `#[cfg]`-dependent.
⚠ **The one thing (c) cannot settle, said plainly**: `rec_free` is a REAL `free`
and this pattern's whole result depends on it being one. A free-list push into a
slab would consume nothing, the stale use would be in bounds of a live
allocation, and `p34` would be `p32`'s row instead. `spec.md`'s `forbidden` list
and `controls/safe_arms.py`'s branch B are where that is pinned and measured, not
here.
