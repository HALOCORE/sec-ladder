# p28 — intrusive doubly linked lists, two link sets, incomplete destroy

Measured notes. `spec.md` carries the reasoning and the pins; `c/kernel.h`
carries the kernel contract; this file carries what was **run**, including the
three places a prediction written into this tree turned out to be wrong.

⚠ **Every claim below is re-derivable.** `controls/*.py` regenerate their own
JSON sidecars, `inputs/gen.py` regenerates the blobs, `harness/build.py` the
binaries, and the scratch under `.temp/t146/`, `.temp/t149/` and `.temp/t150/`
carries the Verus obligation census, the C demonstrations and the review's own
probes.

⚠⚠ **AND "REGENERATE THEIR OWN JSON SIDECARS" MEANS THEY REWRITE COMMITTED
FILES.** Running any of the five `controls/*.py` overwrites its `.json` in
`patterns/p28-intrusive-lists/controls/`, so a bare re-run leaves the working
tree dirty even when nothing moved — `measured_utc` alone changes. That is by
design: the sidecar is a measurement and `derived_from_sha256` pins it to the
sources it was taken against, so it **must** be regenerated whenever any of them
moves, and the gate FAILS a stale one (`check.py::check_control_json_pins`,
`rep.fail("tables", ...)`). **Run `git status` afterwards, and `git diff` before
you keep it.** ⚠ Since `TASK_150` all five use `argparse` and **exit 2 on an
unrecognised argument**; three of them (`harm_sites.py`, `rust_arms.py`,
`safety_line.py`) previously accepted anything silently and then ran the whole
battery, which cost the `TASK_149` reviewer a restore in two patterns' trees.

---

## 1. What the row is, and why the omission is on TRIM and not on DEL

An object is one `malloc`, and **both link sets live inside it**: `lp`/`ln` for
the eviction list, `hn`/`hp` for the hash chain. So the object is a member of two
containers at once and **membership is not ownership** — which is the whole
reason intrusive lists exist (one allocation, O(1) removal from either list given
the object) and the whole reason they go wrong.

**DEL reaches its victim BY WALKING THE CHAIN**, so when it frees it is already
holding a chain cursor and unlinking is one more line of the code it is in.
**TRIM reaches its victim through the EVICTION LIST** — that is what "the oldest
object" means — so it holds no chain cursor and has to go and get one.
`c/kernel.c` does not. **The path that arrives from the other list is the one
that forgets**, and that is the shape of this bug in real code rather than an
arbitrary choice of arm.

### 1a. The safety line, measured

`controls/safety_line.py` preprocesses both shipped C rungs with `cc -E -P` and
diffs them:

```
preprocessed kernel.c           392 line(s)
preprocessed kernel_hardened.c  401 line(s)
diff  +9 / -0
    + {
    + size_t vb = (size_t)(victim->key % 8);
    + if (victim->hp != ((void *)0))
    + victim->hp->hn = victim->hn;
    + else
    + bucket[vb] = victim->hn;
    + if (victim->hn != ((void *)0))
    + victim->hn->hp = victim->hp;
    + }
```

A pure addition, every added line inside the splice, `victim->hp` mentioned
exactly three times and `victim->hn` exactly four. The control exits non-zero if
any of that stops holding. ⚠ Its first draft asserted TWO and THREE and was
WRONG — `victim->hn->hp = victim->hp;` mentions each once more — which the
control caught on its first run. The counts are transcribed from the diff it
prints, not from a reading of the source.

### 1b. ⚠⚠ THE SPELLING THIS ROW SHIPS, AND THE PREMISE IT CORRECTS

`TASK_143` called the singly linked chain's fifteen-line safety line *"the one
honest weakness"* of this row and predicted it *"shortens to 4 if the hash chain
is doubly linked too"*. The manager built that (`.temp/mgr146/p28d/`) and
reported **`+9 / −0` at a SHARED COST OF ZERO** — both R1 bodies preprocessing to
127 lines — and `TASK_146` was told to take it.

⚠⚠ **`.temp/mgr146/p28d/body.inc` NEVER INITIALISES `hp`.** Six `hp` sites, all
reads (DEL ×3, TRIM ×3), and not one write on the PUT path. The chain's back
pointer is whatever `malloc` returned. Measured (`.temp/t146/cdemo/repro28d.sh`,
ASan, `env -u LD_PRELOAD`):

```
p28d bug  benign-noTrim   rc=1  asan=4  SEGV on unknown   <- a BENIGN input
p28d fix  benign-noTrim   rc=1  asan=4  SEGV on unknown   <- BENIGN, HARDENED arm
p28d fix  benign-trim     rc=1  asan=4  SEGV on unknown
p28d fix  adv-uaf-read    rc=1  asan=4  SEGV at body.inc:164
```

`victim->hp->hn = victim->hn` through an uninitialised pointer. The plain build
survives only because a fresh `brk` page reads as zero, so `hp` happens to be
`NULL` and the `else` branch runs; ASan's poison pattern is non-zero and it dies.
**As delivered, `p28d` fails admission question 1 — *correct on benign inputs* —
in BOTH arms.** The manager's re-verification could not see it: its `repro.sh`
runs ASan on `ctl` and `bug` and never on `fix`.

Corrected (`.temp/t146/cdemo/p28dfix/`, three preprocessed lines added to PUT:
`n->hp = NULL;` and the two that give the old chain head its `hp`):

| | `p28` singly linked | `p28d` as delivered | **corrected** |
|---|---|---|---|
| safety line, preprocessed | **+15 / −0** | +9 / −0 | **+9 / −0** |
| R1 body, preprocessed | **127** | 127 | **130** |
| correct on benign input | yes | **NO** | yes |
| four inputs × both arms | — | — | **bit-identical to `p28`'s** |
| ASan `ctl` / `bug`-read / `bug`-write / `fix` | fires/fires/fires/silent | fires/fires/fires/**SEGV** | fires/fires/fires/silent |

**So *"a 40% shorter safety line, FREE"* is `9 against 15 at +3 shared lines`, not
at zero.** The conclusion survives and the arithmetic does not; this row ships the
doubly linked spelling.

---

## 2. The harm shapes and the two SITES, measured

⚠⚠ **THIS SECTION SAID "TWO HARM SHAPES" UNTIL `TASK_150`. THERE ARE THREE**, on
the same omitted block: a use-after-free READ, a use-after-free WRITE, and a
**CWE-415 DOUBLE FREE** (§2d). The third was immediate from `c/kernel.c`'s source
— DEL's splice ends in `free(n)` and DEL's walk can reach an object TRIM already
freed — and **no text in the pattern named it**, including the sentence inside
`spec.md`'s hashed contract block that denied it. `c/kernel.h` now tabulates all
three and names the instrument that sees each.

`controls/harm_sites.py`, one binary, both arms from one `#include`
(`controls/arm_body.inc`), ASan under `env -u LD_PRELOAD`:

```
ctl  asan_gcc     exit=1 asan_lines=2 ['heap-use-after-free']   <- POSITIVE CONTROL
ctl  asan_clang   exit=1 asan_lines=2 ['heap-use-after-free']
site head         fix 5700746 head=1 interior=0   -> head      (want head)
site tail         fix 5015554 head=0 interior=1   -> interior  (want interior)
bug  head   asan_gcc     exit=1 asan_lines=2 ['heap-use-after-free']
bug  head   asan_clang   exit=1 asan_lines=2 ['heap-use-after-free']
fix  head   asan_gcc     exit=0 asan_lines=0 []
fix  head   asan_clang   exit=0 asan_lines=0 []
bug  tail   asan_gcc     exit=1 asan_lines=2 ['heap-use-after-free']
bug  tail   asan_clang   exit=1 asan_lines=2 ['heap-use-after-free']
fix  tail   asan_gcc     exit=0 asan_lines=0 []
fix  tail   asan_clang   exit=0 asan_lines=0 []
```

**The two sites p28 claims are separately reachable**: with one key in the bucket
the victim IS `bucket[5]`, and with two the victim is the chain TAIL, so the
dangling pointer sits in the survivor's `hn` — inside another heap object. ⚠ The
site is decided in the HARDENED arm and BEFORE any free, by counting which branch
the splice takes; asking the buggy arm would mean committing the use-after-free in
order to observe it, and a control that has to execute the bug to see it proves
nothing about where the bug is.

⚠ **The positive control is laundered through a `volatile` sink**, because
`TASK_143` had clang delete a control of exactly this shape by malloc elision and
`p31` hit the same artefact.

### 2a. What the gate's own matrix records

`c-gcc` (R1) against `c-gcc-h` (R1h), `O0/isolated`, all eight shipped inputs:

```
small.bin, large.bin, degenerate.bin, adversarial-stride3.bin  R1 == R1h
adversarial-uaf-read.bin    R1h 14476180526798907392  R1  9891317877474112512
adversarial-uaf-head.bin    R1h 11740759076003072000  R1  7155896426678277120
adversarial-uaf-write.bin   R1h 14476180526798907392  R1  SIGSEGV (rc 139)
adversarial-many.bin        R1h  8660776832395219968  R1  6439359753103586304
```

### 2b. ⚠⚠ UBSan SEES ONE THING, AND ON ONE INPUT IT IS THE ONLY WITNESS OF THE WRITE

**RETRACTED.** This subsection read *"UBSan sees nothing, and that is not a
gap … no signed overflow, **no misaligned access**, no out-of-range index"*, and
`model.py`'s `sanitizer_expect` docstring said the same. `TASK_149` measured both
false and `TASK_150` reproduced it independently.

A **UBSan-only** build of `c/kernel.c` (gcc and clang, `-O1 -g`,
`-fsanitize=undefined -fstrict-aliasing`, `env -u LD_PRELOAD`, diagnostics read
with `grep` and never truncated) reports, on `adversarial-uaf-write.bin` and on
**no other shipped input**:

```
gcc    c/kernel.c:215:31  runtime error: member access within misaligned address
                          0x... for type 'struct p28_obj', which requires 8 byte
                          alignment
clang  c/kernel.c:215:28  the same, AND
       c/kernel.c:215:28  runtime error: store to misaligned address 0x... for
                          type 'struct p28_obj *', which requires 8 byte alignment
```

`c/kernel.c:215` is `n->lp->ln = n->ln;` — the DEL splice writing through the
`lp` that glibc's tcache has overwritten.

⚠⚠ **IT IS NOT A 10/10 DIAGNOSTIC, AND `TASK_149`'s FIGURE WAS A SMALL-SAMPLE
ARTEFACT.** Three independent samples of ten gave `(gcc, clang)` = `(10, 9)`,
`(9, 10)` and `(9, 8)`, so `TASK_150` measured the rate properly at
**50 runs per compiler** (`.temp/t150/ubsan_rate.sh`):

```
ubsan-only gcc,   uaf-write                 44/50   (88%)
ubsan-only clang, uaf-write                 45/50   (90%)
ubsan-only, the other 7 inputs, both cc      0/112
ubsan-only, HARDENED arm, 8 inputs x 2 cc    0/16
```

**The miss is the run in which the SEGV wins the race**: whether UBSan's
alignment check reports before the store faults depends on the address the
allocator hands back. So the right sentence is *"UBSan reports it on about nine
runs in ten, on both compilers"* — **not** *"10/10 gcc and 9/10 clang"*, which is
what `TASK_149` wrote from a single sample of ten.

⚠ **THE COLUMN IS LICENSED, not assumed** (`.memory/03-measurement.md`'s rule
that a probe owes a positive control in the detector whose column it licenses).
Four cells, both compilers, one binary with two arms and a `volatile` sink:

```
ubsan/gcc    signed overflow   fires: runtime error: signed integer overflow
ubsan/gcc    heap UAF          SILENT      <- UBSan cannot see a heap UAF
ubsan/clang  signed overflow   fires
ubsan/clang  heap UAF          SILENT
asan/gcc     signed overflow   SILENT      <- ASan cannot see a signed overflow
asan/gcc     heap UAF          fires: heap-use-after-free, exit 1
asan/clang   signed overflow   SILENT
asan/clang   heap UAF          fires
```

Each column fires where it should **and is silent where it should be**, which is
the half that makes the finding a measurement rather than a coincidence.

#### ⚠⚠ What ASan does and does not see — and the narrower claim that survives

`c/kernel.h` calls the DEL shape a *"heap-use-after-free WRITE"*, and the gate's
ASan column never shows one. With `-fsanitize-recover=address` and
`ASAN_OPTIONS=halt_on_error=0`, over **all eight** shipped inputs and **both**
compilers (`gcc` and `clang` agree cell for cell):

```
input                    errors  READ  WRITE  SEGV
adversarial-many              5     3      2     0
adversarial-uaf-write         7     6      0     1
adversarial-uaf-read          2     2      0     0
adversarial-uaf-head          2     2      0     0
the other four                0     0      0     0
HARDENED arm, all eight       0     0      0     0     <- negative control
```

**ASan DOES report the WRITE, twice, on `adversarial-many.bin`:**

```
WRITE of size 1  c/kernel.c:143   n->val = (uint8_t)(a * 7u + 1u);   PUT's hit arm
WRITE of size 8  c/kernel.c:213   n->hn->hp = n->hp;                 DEL's splice
```

The second is exactly the harm shape `c/kernel.h` tabulates.

> ⚠⚠⚠ **SO THE CLAIM *"UBSan IS THE ONLY WITNESS OF THIS ROW'S WRITE ANYWHERE IN
> THE TREE"* IS TOO STRONG AND IS NOT MADE HERE.** `TASK_149` ran three of the
> four adversarial blobs under `-fsanitize-recover` and did not run
> `adversarial-many.bin`; `TASK_150` ran all eight on both compilers and found
> the two WRITEs above. **What survives is narrower and still worth having:**
> on **`adversarial-uaf-write.bin`** — the one input the header names for the
> WRITE shape — ASan gives 6 READs and a SEGV and **no** WRITE, because
> `n->lp` is tcache-garbage and the splice faults before it completes. **There,
> and only there, UBSan is the sole witness**, and clang's `store to misaligned
> address … for type 'struct p28_obj *'` is the report that witnesses it.

⚠ **And the structural half of the argument is right about ORDER but not about
VISIBILITY.** DEL must read `n->key` before it can splice, so a READ always
arrives first — confirmed: in a **halting** build the first error is a READ on
all four adversarial inputs. That is why **the gate's stage 7 can never show a
WRITE**: it builds `-fsanitize=address,undefined` combined and halts on ASan's
first report. ⚠⚠ **A combined halting build cannot license a per-sanitiser claim
in EITHER direction** — it is what made *"UBSan is silent"* look measured.

⚠ **Finally, what UBSan is actually detecting is ALIGNMENT, not lifetime.** The
freed chunk's `lp` happens to be a tcache word that is not 8-byte aligned. A
different allocator, or a different tcache layout, and UBSan would be silent
while the use-after-free was exactly as present. Read it as *UBSan sees an
ARTEFACT of this row's harm*, not as *UBSan detects this row's harm*.

### 2c. ⚠ R1 READS FREED HEAP AND IS STILL REPRODUCIBLE — and what that buys

`controls/repro.py`, 20 runs per cell, every (compiler × opt) cell:

```
adversarial-uaf-read.bin     c-gcc/O0=1 c-gcc/O3=1 c-clang/O0=1 c-clang/O3=1  ONE behaviour across all four cells
adversarial-uaf-head.bin     1 1 1 1                                          ONE behaviour across all four cells
adversarial-uaf-write.bin    1 1 1 1                       ONE behaviour (a stable CRASH, not a value)
adversarial-many.bin         1 1 1 1                                          ONE behaviour across all four cells
degenerate.bin, small.bin    1 1 1 1

NEGATIVE CONTROL  arm_aslr.c  20/20 distinct  randomize_va_space=2  FIRED
```

**The layout is why** (`c/kernel.h`'s LAYOUT NOTE): the four links come first, so
glibc's tcache overwrites `lp` and `ln` with its `next` and `key` words and
leaves `key`, `val`, `hn` and `hp` — the only fields the stale walk reads —
intact. `controls/arm_aslr.c` reads the word that does **not** survive and gives
20 distinct values through the same counter, so the same run both certifies the
instrument and exhibits the contrast.

⚠⚠ **AND HERE IS WHAT IT DOES NOT BUY.** `TASK_143_REPORT` §2.2 and
`.memory/06-catalogue.md` say the reproducibility makes p28 *"GATABLE against
`model.py` on its adversarial inputs where `p27` and `p29` are NOT"*.
**Measured false** (`TASK_146` deliverable 0). `harness/check.py`'s `inputs_of`
splits on the `adversarial` prefix; stage 2 (`check_checksums`) is handed
`good_models` only; stage 4 (`check_adversarial`) *records* — its docstring says
so and its only `rep.fail` concerns a declared `expected_hang`. Over the three
built temporal rows' committed gate records:

```
p29-bst-delete      PASS  0 failures   58 adversarial rows   26 with diverges:true
p32-free-list-pool  PASS  0 failures   48 adversarial rows   10 with diverges:true
p27-handle-table    PASS  0 failures   44 adversarial rows   18 with diverges:true
```

✅ **What it DOES buy is a PINNABLE FIGURE.** `p29` cannot have one — its own
`controls/repro.json` publishes an invariant and no count, and its gate record
shows `adversarial-many.bin/c-clang` at `13261590098807716864` (O3) and
`13757854543850195968` (O0). p28 is the first temporal row whose adversarial
evidence carries a number. ⚠ And the one adversarial obligation the gate *does*
enforce is `sanitizer_expect`: `check_sanitizers` is handed `all_models`.

### 2d. ⚠⚠⚠ THE THIRD HARM SHAPE: R1 DOUBLE-FREES, AND THE DENIAL WAS INSIDE THE HASH

**This is `PROTOCOL` rule 6's second half exactly — the hash matched and the
measurement refuted the claim.** `p46` was the first pattern to demonstrate that
hole; `p28` is the second, and here the refuted sentence was `spec.md`'s
`idiom.required`, **inside the `slb-contract` block**.

**The bug is immediate from the source.** `c/kernel.c`'s DEL ends its splice with
`free(n)`, and DEL's walk can reach an object TRIM already freed — *that is the
row's bug*. So the only question was reachability, and it is reachable.

**Why nothing in the tree had seen it.** The real allocator gets there first:
glibc's tcache overwrites the freed chunk's user offsets 0 and 8, which are
exactly `lp` and `ln`, so `n->lp->ln = n->ln;` faults **two statements before**
`free(n)`. Measured: a plain `-O1` build of R1 on `adversarial-uaf-write.bin`
exits **139 (SIGSEGV)**, every run, and never reaches the second `free`.

**So the PROGRAM property was measured instead of the ALLOCATOR's**, with
`-Wl,--wrap=malloc,--wrap=free` — a link-time interposer, **no `LD_PRELOAD`, so
the container's ASan blindness is not in play** — under a **LEAKING** mode that
never calls the real `free`. ⚠ That is not a hack: **it is exactly the semantics
`model.py` and all four Rust rungs implement**, because slots are never recycled.
All eight shipped inputs, both C arms, `n_iters` forced to 1:

```
arm              input                        mallocs  frees  doublefree
kernel           adversarial-uaf-write.bin          4      5           1   <<<
kernel_hardened  adversarial-uaf-write.bin          4      4           0
kernel           adversarial-many                   8      8           0
kernel           adversarial-uaf-read               4      4           0
kernel           adversarial-uaf-head               3      3           0
kernel           adversarial-stride3                2      2           0
kernel           small / large / degenerate    11 / 37 / 50   balanced  0
kernel_hardened  every input                              balanced     0
```

**Same input, same driver, same binary recipe; the only difference is the safety
line.** `livemallocs` is 0 in every cell of both arms.

> ✅ **THE LEAK HALF OF THE OLD CLAIM IS TRUE AND STAYS. THE DOUBLE-FREE HALF WAS
> FALSE AND IS STRUCK.** The two SCOPED spellings — `c/kernel.c`'s and
> `c/kernel_hardened.c`'s epilogue comments, *"neither leaks and neither
> double-frees **here**"* — are **correct** and were left alone: TRIM unlinks its
> victim from the eviction list before freeing, so the epilogue's walk cannot
> reach it. Only the two UNSCOPED spellings were wrong.

**Which instrument sees it, and the answer is uncomfortable:**

| instrument | verdict |
|---|---|
| the `--wrap` interposer | ✅ **the only thing on this box that reports it** |
| ASan, even with `-fsanitize-recover=address` | ✗ never reaches it — the SEGV is not a recoverable error, so the run ends at `n->lp->ln`. `grep -l 'double-free\|attempting free'` over every recovering log: **no match** |
| UBSan | ✗ does not look for it |
| Miri | ✗ drives the Rust rungs, which never recycle a slot and cannot double-free |
| valgrind `memcheck` | ⚠ **cannot start on this box** — `Fatal error at startup: a function redirection … memcmp … ld-linux-x86-64.so.2`, i.e. the missing `libc6-dbg` (`.memory/00-environment.md`). **UNTESTED, not silent** |

⚠ **That is the general lesson and it is bigger than `p28`: a harm shape can be
STRUCTURALLY invisible to every detector the tree runs, because an EARLIER harm
on the same path crashes the process first.** Nothing in the gate would ever have
raised it; it took reading the source and then building an instrument that
changes the allocator's semantics rather than watching them.

---

## 3. Where the shipped guards fire

| guard | fires on | never fires on |
|---|---|---|
| `nmade < P28_SLOTS` (the allocation budget) | `degenerate.bin`, on purpose — it reaches `48/48` and then rejects **13** further PUTs | `small` (peak `12/48`), `large` (peak **`42/48`** — ⚠ a narrow margin; a `gen.py` change could tip it), the adversarial files |
| `steps < P28_SLOTS` (the walk fuel) | nothing shipped, in any CHECKED rung — a chain holds only live objects | — ⚠ in R1 it *can* fire, which is R1's behaviour and is recorded, not required |
| `live[cur] == 1u8` and the ten `alive_link` sites (R4/R5 only) | nothing, ever | see §5 |

---

## 4. ⚠ THE SAFE RUNGS ARE NOT AN ARENA, AND THE CATALOGUE SENTENCE IS FALSE OF THEM

`.memory/06-catalogue.md` carries `TASK_093`'s reusable reason: *"p28's two safe
spellings that free per node both catch the bug by `p27`'s runtime mechanism —
`Rc`/`Weak` reproduces p27's published sentence, while the index arena NEVER
FREES."* **The spelling this row ships is a third one and it frees.**
`safe_naive.rs` and `safe_tuned.rs` hold `[Option<Box<Obj>>; SLOTS]`: `tab[i] =
None` is the `free`, one `Box::new` per object and one drop per DEL and per TRIM,
so the allocator traffic is the C rungs'. What the slot table costs is not
freeing, it is that **slots are never recycled** — `p27`'s and `p29`'s convention,
and the reason every rung including C carries the allocation budget.

### 4b. ⚠⚠⚠ AND WHAT SAFE RUST DOES WITH THE OMISSION IS NOT WHAT THIS TREE PREDICTED

`controls/arm_safe_bug.rs` is `safe_tuned.rs` minus the safety line, in both
idiomatic safe spellings, under `#![forbid(unsafe_code)]`. The first drafts of
`safe_naive.rs`'s header, of that file's own header and of `controls/rust_arms.py`
all predicted **"a WRONG ANSWER"**. Measured (`controls/rust_arms.json`):

| input | checked kernel | `strict` (`.unwrap()`) | `lenient` (`if let`) |
|---|---|---|---|
| `adversarial-uaf-read` | 14476180526798907392 | **same** | **same** |
| `adversarial-uaf-head` | 11740759076003072000 | **same** | **same** |
| `adversarial-uaf-write` | 14476180526798907392 | **same** | **same** |
| `adversarial-many` | 8660776832395219968 | **PANIC, exit 101** | **same** |

**Deleting p28's safety line from safe Rust changes no VALUE on any input this
pattern ships — never undefined behaviour, never silently wrong — while the
`.unwrap()` spelling PANICS instead.**

⚠ **THE PANIC IS THE TYPICAL CASE, NOT AN EXOTIC ONE**, and this file said *"its
only trace is a `None` where `.unwrap()` expects `Some`"* until `TASK_150`. The
strict spelling panics on **15,929 of 20,000** randomly generated windows (80%)
and on **304,578 of 3,257,436** exhaustively enumerated ones (9.4%, and 100% of
the length-6 cases that evict a whole bucket). One shipped input reaches it; most
random ones do. And a panic at exit 101 **is** a changed answer — the program
prints no checksum.

### 4c. ⚠⚠⚠ THE HEADLINE SURVIVED A REAL ATTACK, AND THE HEDGE IS NOW A PROOF

`TASK_149` attacked *"changes no answer"* directly rather than re-reading it, and
**the attack is a clean negative — do not re-run it.** Three simulators
transliterated line by line from `safe_tuned.rs` and `controls/arm_safe_bug.rs`,
plus a `suffix_witness()` that is independent of the answers because it rebuilds
each bucket chain **through freed slots**, which the safe rung cannot do:

```
mode            cases   VALDIFF    panic    trunc  SUFFIX!
uniform          4000         0     3151     3445        0
trim-heavy       4000         0     3403     3538        0
one-bucket       4000         0     2702     3712        0
reinsert         4000         0     3576     3652        0
del-mid          4000         0     3097     3340        0
TOTAL           20000         0    15929    17687        0

EXHAUSTIVE  |alpha|=12  L<=6  keys=[0, 8, 1]   (two colliding in bucket 0, one not)
  seqs=3257436   VALDIFF=0   SUFFIX=0   strictpanic=304578
```

**17,687 of 20,000 random cases DO truncate the walk at a freed slot**, so the
mechanism the headline is about is exercised throughout — it just never changes
an answer. **Zero counterexamples, and none could be manufactured.**

⚠⚠ **AND THE HEDGE CAN GO.** This file, `arm_safe_bug.rs`'s header and
`TASK_146`'s report all said *"an argument plus a measurement over the shipped
inputs, not a proof"*. **It is provable, in three steps, from two facts the rung
already pins:**

1. **Every chain is strictly decreasing in slot number.** Slots are handed out as
   `s = nmade`, monotonically; PUT prepends the largest so far, DEL splices, and
   the buggy TRIM does not touch chains. So the order is an invariant.
2. **The eviction list is in that same order, so its TAIL is the MINIMUM live
   slot.** Same three writers.
3. **Therefore live-before-dead.** Suppose slot `i` is dead and `j < i` is live,
   both in bucket `b`'s chain, so `j` sits behind `i`. `i` cannot have died by
   DEL, which splices it out. So TRIM freed `i` — but TRIM takes the minimum live
   slot and `j < i` was live. Contradiction. Slots are never recycled, so a dead
   slot never returns.

Hence stale entries are exactly a SUFFIX, the truncated walk visits exactly the
live entries in exactly the right order, and every answer is unchanged. The
`SUFFIX!` column above is the mechanised check of step 3 and it is **0** in
3,277,436 sequences.

> ⚠⚠ **THE TWO HYPOTHESES ARE THE USEFUL OUTPUT, because they name what a real
> cache would break:** (a) **eviction order equals chain order**, and (b) **slots
> are never recycled**. An LRU that promoted on a hit breaks (a); a recycling
> arena breaks (b); **drop either and the result is gone.** That is worth more
> than the old hedge, which said the same thing without saying which two facts
> were doing the work.

The one path that notices is PUT, which writes the old chain head's `hp` *without
walking to it* — and when every object in the bucket has been evicted, that head
is a `None` slot.

⚠ **The simulators are not taken on trust.** `TASK_149` closed the loop against
real binaries: decoding each adversarial blob's single window and running the
simulators against what `c/kernel.c` and `c/kernel_hardened.c` actually printed
at `n_iters = 1`, `sim_checked` MATCHES R1h on all four, the safe-buggy arm
returns the CHECKED answer on every input while the C buggy arm returns a
different number on every input, and the strict spelling panics on
`adversarial-many` and on nothing else — which is what `controls/rust_arms.json`
records.

**So safe Rust's answer to p28's omission is: NOTHING, or a PANIC, decided by the
input and by which of two idiomatic safe spellings the port uses. Never undefined
behaviour, and — on these inputs *and on 3,277,436 more* — never a silently wrong
answer.** Miri agrees: silent on `arm_safe_bug` in both spellings on all eight
inputs, while it reports `Undefined Behavior: in-bounds pointer arithmetic
failed` on `controls/arm_rawptr.rs`'s bug arm on all four adversarial inputs and
on nothing else. ⚠ **Miri runs at `miri_iters = 4`** (`controls/rust_arms.json`
records the field), so the silence is over the first four windows the driver
visits, not the shipped 200 000 iterations. On the adversarial inputs `nwin == 1`
so all four hit the same window and the scoping is harmless; on `large.bin` it is
not, and the sentence means *"silent on the first four windows"* there. Nothing
in this row depends on it.

⚠⚠ **That is a STRONGER outcome than `p32`'s and it points the other way.**
`p32`'s headline is that safe Rust reproduces its buggy C **bit for bit** on 10 of
10 cells — the type system is SILENT. p28's is that safe Rust **cannot reproduce
its buggy C at all**: the representation safe Rust forces on you removes the
harm's mechanism along with the pointers. Both are outcome-3 results in
`.memory/01-ladder.md`'s sense — *the guarantee you get is not the one you wanted*
— and they are the two opposite ways that happens.

---

## 5. ⚠⚠ THE ONE DISCLOSED DIVERGENCE FROM THE C MECHANISM, AND WHAT IT COSTS

The C rungs store the four links as `struct p28_obj *`. **Every Rust rung stores
them as `u8` slot numbers into a table**, `unsafe.rs` and `verus.rs` included.
Safe Rust has no choice; `unsafe.rs` follows it for two reasons, both stated
rather than assumed:

1. R4 and R5 must be byte-comparable, so they must be the same program;
2. an address-keyed permission map needs the FULL doubly-linked-list
   well-formedness — `hn[hp[j]] == j`, `hp[hn[j]] == j` and the same pair for the
   eviction list — before a walk can be licensed. `TASK_091` proved `wf` for ONE
   list at `4/0` (preserved) and `8/0` (establishable) with zero TCB; **p28 has
   two link sets and the bug is in their interaction**, and this row did not buy
   that proof. ⚠ **That gap is a RESULT, not a reason to shrink the row**, and it
   is the honest answer to `TASK_091`'s own open question.

**What the divergence costs, measured** (`controls/rust_arms.json`):

* nothing to the ANSWER — `arm_rawptr`'s FIX arm equals `c/kernel_hardened.c` on
  every input at both optimisation levels, and its BUG arm equals `c/kernel.c`
  ⚠ **on ALL EIGHT, adversarial included, down to reproducing the SIGSEGV.**
  This line said *"on the benign ones"* until `TASK_150` and that UNDERSTATED it
  (`TASK_149` 5). Re-derived from `controls/rust_arms.json` as regenerated by
  this task: **16 cells (8 inputs × `O0`/`O3`), `raw_bug != c_bug` in 0 of
  them**, and the `adversarial-uaf-write.bin` cell is `[-11, '']` on both sides
  — the same signal, not merely the same value;
* the DETECTOR moves. Miri sees the raw-pointer bug arm and cannot see the
  slot-table one, because in the slot table the stale link is a `u8` and reading a
  `u8` is never UB. **The shipped `unsafe.rs` is correct, so Miri reports nothing
  on it on any input** — that is what `spec.md`'s `miri.reason` says and it is not
  a gap in the run.

**What it costs in EXEC TEXT**, counted in `unsafe.rs` and `verus.rs`: one
`live[cur] == 1u8` conjunct in the walk plus **ten `alive_link` sites** (PUT ×2,
DEL ×4, TRIM ×4). Not one can fire.

✅ ***"Not one can fire"* IS NOW A NUMBER, not a reading** (`TASK_149` 5;
`.temp/t149/alive/`). `alive_link` is `x != NIL && live[x] == 1u8` — a real
runtime branch at ten sites — so an instrumented copy of `unsafe.rs` counted, per
call, whether the `live[]` half ever DISAGREES with the `!= NIL` half:

```
input                        alive_link calls  nonNIL_but_dead    walk calls  dead
adversarial-many                        7,600                0         4,200     0
adversarial-uaf-{head,read,write}   1,200/1,600/1,600        0     200/400/400   0
degenerate                             58,400                0        11,200     0
large                                  24,064                0        45,536     0
small                                   5,116                0         2,052     0
adversarial-stride3                         0                0             0     0
TOTAL                                  99,580            **0**        63,988   **0**
```

**163,568 evaluations of a conjunct that never once decides a branch.** (200
driver iterations per input; the counters are `static mut`, so the instrumented
copy is a probe and was never measured as a rung.) That is exactly why §8's
refusal to publish a rung-to-rung cost is the right call — R4/R5 pay measurable
exec text for a test whose `live[]` half is dead on every shipped input.

⚠⚠ **`p29` could put its liveness conjuncts
in its C rungs too, and p28 CANNOT — because p28's C links are pointers and
neither C rung contains a slot number or a `live[]` bit. The property that makes
the row distinct at C level is the property that makes that conjunct unspellable
there.** No cost claim rests on it, because this pattern publishes none (§8).

⚠ **The epilogues differ too, three ways**: the C rungs walk the eviction list,
`unsafe.rs`/`verus.rs` scan the slot table, and `safe_naive.rs`/`safe_tuned.rs`
have none because dropping the table is the loop. All three free each live object
exactly once.

---

## 6. ⚠⚠⚠ WHAT THE R5 PROOF ACTUALLY FORCES — AND IT IS NOT WHAT THE C SIDE SUGGESTS

`controls/proof_mutants.py`, seven arms, each with a declared verdict, all
re-derived on every run at `--rlimit 400`:

```
A0-control             control     expect=verify got=verify OK  23/0
A1-exec-safety-line    attack      expect=fail   got=fail   OK  22/1  assertion failed
A2-constant-body       vacuity     expect=fail   got=fail   OK  20/1  postcondition not satisfied
A3-spec-only-weaken    attack      expect=fail   got=fail   OK  22/1  assertion failed
A4-spec-weaken         must-verify expect=verify got=verify OK  23/0
A5-walk-liveness       attack      expect=fail   got=fail   OK  22/1  assertion failed
A6-epilogue-dead       must-verify expect=verify got=verify OK  23/0
```

**The three-cell experiment** — A1 exec-only FAIL, A3 spec-only FAIL, A4 both
VERIFY — says the safety line is load-bearing **against the SPECIFICATION and
against nothing else**. And the two failing diagnostics are different
obligations, which is what stops that from being a reading of one error message:

```
A1  assert(st == step(st_in, c, a).0)   <- the REFINEMENT assertion
A5  assert(alive(st, cur))              <- the MEMORY-SAFETY licence, inside walk
```

⚠⚠ **That is `p32`'s shape and it is SHARPER here.** `p32` has no linear resource
at all — nothing is ever allocated — so of course nothing linear forced its
conjunct. **p28 HAS them**: `rec_close` consumes the victim's `PointsTo` and its
`Dealloc`, and that is a real temporal guarantee. It still does not reach this
omission, **because the linear argument only ever bites at a READ and what
`c/kernel.c` forgets is a LINK.** Leaving a slot number in a chain consumes
nothing.

### 6a. ⚠ A6 WAS PREDICTED TO FAIL AND VERIFIES — retracted here, not dropped

`A6-epilogue-dead` makes the epilogue's `live[j] == 1` test unreachable, so every
surviving object leaks. It verifies, `23/0`. The reason is already in
`.memory/04-verus.md`: **`Tracked<Dealloc>` is AFFINE, not linear** — dropping a
token is legal, so a proof built on it shows deallocation is LEGAL (no double
free, no use after free) and never that it HAPPENS. `TASK_104` measured that on
`p42` with a committed must-fail control; this is the same result on a fourth
pattern, and the first on a kernel whose C rungs really do free everything. **The
sentence *the linear resources force the epilogue*, which this file and
`verus.rs`'s SAFETY (6) both asserted before the arm was run, is retracted.**

### 6a-bis. ⚠⚠⚠ AND IT IS STRICTLY STRONGER THAN `A6`: NOT ONE OF THE THREE FREES IS FORCED

`TASK_149` ran seven arms the shipped battery does not have
(`.temp/t149/proof_arms2.py`, `--rlimit 400`, ⚠ **with the FILE NAME held at
`verus.rs` and only the directory varied**, because §6b measured that the margin
moves with the crate name and `controls/proof_mutants.py` does not do this):

```
  B0-control                   control  expect=verify got=verify OK  23/0 35.2s
  B1-assume-false              vacuity  expect=verify got=verify OK  23/0 35.7s
  B2-requires-false            vacuity  expect=fail   got=fail   OK  22/1 36.0s
  B3-const-body-weak-ensures   vacuity  expect=verify got=FAIL   XX  20/1  2.0s
  B4-trim-leaks-the-victim     affine   expect=verify got=verify OK  23/0 61.7s
  B5-del-leaks-the-victim      affine   expect=verify got=verify OK  23/0 40.9s
  B6-epilogue-free-deleted     affine   expect=verify got=verify OK  23/0 40.3s
```

`B0` reproducing the shipped `23 verified, 0 errors` at 35.2 s against 36.8 s
says the crate-name worry is not biting today.

**`verus.rs` calls `rec_close` at exactly three sites — TRIM, DEL and the
epilogue. DELETE ANY ONE OF THEM** — so that object's `PointsTo` and `Dealloc`
are removed from the tracked maps and then simply **dropped**, and the storage is
never returned — **and the file verifies at `23/0` every time, a count
indistinguishable from the control.**

| arm | what it deletes | result |
|---|---|---|
| `A6` (shipped battery) | the epilogue's `live[j] == 1` **branch** | verify `23/0` |
| **`B4`** | **TRIM's `rec_close`** — the row's own destroy path | **verify `23/0`** |
| **`B5`** | **DEL's `rec_close`** | **verify `23/0`** |
| **`B6`** | **the epilogue's `rec_close`**, leaving the loop and its asserts | **verify `23/0`** |

`A6` shows the *epilogue's branch* is not forced; `B6` separates *"the branch is
dead"* from *"the free is not forced"* and gets the same answer; `B4`/`B5` show
**the free is not forced on either destroy path, including the very path the row
is about**. So the honest statement of this R5's scope is:

> **Nothing in this proof forces `c/kernel.c`'s omitted line, and nothing in it
> forces any of the three `free`s either — a rung that leaks every object it ever
> allocates verifies at the same `23/0`. What it forces is the FUNCTIONAL
> postcondition (`A1`/`A3`/`A4`); the memory-safety obligations it carries are
> LICENCES TO READ, NOT OBLIGATIONS TO RELEASE.**

⚠ **This is the fourth instance of the affine-token family** after `p42`'s ghost
ledger, `p32`'s `M4` and `A6` — and it is the sharpest, because it shows the
result at **every** free site rather than at one, on the first pattern whose C
rungs really do free everything.

#### ✅ `B3` surprised the reviewer, and the surprise is in `p28`'s favour

`ensures true` + `return 0;` was predicted to VERIFY. It **fails**, `20/1` —
**and the failing obligation is in `main`, not in `kernel`**:

```
error: assertion failed
    --> .../verus.rs:1701:20
```

which is `assert(r == cache_fold(buf@, (k * stride) as int, stride as int));`
under the comment *"Ghost only: this is what CONSUMES the kernel's `ensures`."*
**So the driver is not a passive verified call site: weakening the kernel's
postcondition breaks the driver's own proof.** That is stronger than what
`check.py` stage 5b documents and no shipped arm exhibits it. ⚠ It belongs in the
battery as a must-fail arm; it is **not** there, because adding it moves
`controls/proof_mutants.py` and costs the ~40-minute regeneration of
`proof_mutants.json` (`TASK_150` did not spend it — §9).

#### `B1` — the `assume(false)` hole, confirmed on this rung

`assume(false);` at the top of `kernel` verifies **`23/0`, the same counts as the
control**, and `check.py` only `rep.shout`s. `RECAP`'s owed gate item applies to
`p28` exactly as written. ✅ **Exposure today is zero**: `grep -c 'assume(' verus.rs`
is 0. Recorded so nobody re-runs it. `B2` (a `requires` nothing can discharge)
fails at the CALL SITE with `precondition not satisfied`, which is what makes
stage 5b's *"verified call site"* mean something.

### 6b. What the proof cost — three levers, and TWO OF THEM WENT THE OTHER WAY

The kernel's loop body carries four opcode arms, ten `alive_link` sites and a
dozen invariant re-establishments in ONE SMT query, and `Resource limit (rlimit)
exceeded` on that query is what forced every decision below. ⚠⚠ **The binding
constraint turned out not to be the shipped configuration at all — it was
`--cfg slb_twin`**, which `harness/check.py`'s twin stage runs and which adds
five more verified functions (and, through `slb_twin_rec_alloc`/`_rec_free`,
vstd's `PointsToRaw`/`Dealloc` axioms) to the shared context.

| lever | shipped config | `--cfg slb_twin` |
|---|---|---|
| baseline (`St` with six parallel `Seq<u8>`, ghost-guarded quantifiers) | rlimit exceeded | — |
| **ONE `Seq<Obj>` + exec-guarded quantifiers** | floor between **100** and **120** | ⚠ **rlimit exceeded at 400 AND at 2000** (the 2000 run was killed at **9 m 43 s**, well past `check.py`'s 900 s per-run timeout) |
| ⚠ **`#[verifier::spinoff_prover]` on `kernel`** | ⚠ **WORSE** — `22 verified, 1 errors` at rlimit 400, where the same file without it verifies | not reached |
| ✅ **`put_new`/`del_at`/`trim`/`step` `#[verifier::opaque]`, revealed in the ONE proof block that needs them** | floor between **70** (fails) and **80** (verifies); **23/0 in 36.8 s** at 400 | ✅ floor between **60** (fails) and **70** (verifies); **28/0 in 33.1 s** at 400 |

**The shipped file is the last row**, and the shipped budget of 400 is a **5x
margin** over a floor measured in BOTH configurations rather than one:

```
rlimit    shipped            --cfg slb_twin
   60     22 verified, 1 err   27 verified, 1 err
   70     22 verified, 1 err   28 verified, 0 err
   80     23 verified, 0 err   28 verified, 0 err
  100     23 verified, 0 err   28 verified, 0 err
  150     23 verified, 0 err   28 verified, 0 err
  400     23 verified, 0 err   28 verified, 0 err     <- shipped, 36.8 s / 33.1 s
```

The four spec functions are needed by exactly one obligation —
`assert(st == step(st_in, c, a).0)` — and carrying their bodies through the other
~200 statements of the loop is what the budget was being spent on.

The two structural decisions that came first, and are still load-bearing:

* **`St` carries ONE `Seq<Obj>`, not six parallel `Seq<u8>`.** With parallel
  sequences, every splice AND every `bk`/`head`/`tail` write produces a fresh
  `St` term that the record invariant has to be re-proved against. With one `ob`
  sequence, `rec_ok` and `links_ok` are stated over `st.ob` alone and a write to
  `bk`, `head` or `tail` leaves their terms unchanged.
* **`base`'s two big quantifiers are guarded by the EXEC array `live[j] == 1u8`,
  not by the ghost `st.lv[j]`.** Same reason: `live@` does not move during a
  splice, so the guard term is stable. This also removed seven `dal_ok`
  re-establishment blocks outright — `dal_ok` mentions no ghost state at all, so
  a splice cannot disturb it.

⚠ **And one lever went the OPPOSITE way to `p09`'s measured result.** `p09`'s
NOTES.md 5c scopes `lemma_u128_shr_is_div` and `lemma_mul_inequality` into the
driver's loop body because at file scope they push the kernel's query past the
rlimit. On p28, scoping them **makes the kernel's query WORSE**: at file scope the
pre-opaque floor was between 100 and 120, and with them scoped 120 failed too.
They stay at file scope and `verus.rs`'s `broadcast use` block says so.

**`#[verifier::rlimit(400)]` on `kernel`** is a solver budget, not a soundness
knob — every obligation is still discharged, and `controls/proof_mutants.py`'s
seven arms are the check on that. It is a SOURCE-LEVEL attribute, so the gate's
flagless invocation honours it.

⚠ **A fragility worth knowing, measured on the PRE-OPAQUE file**: the margin
moves with the CRATE NAME. A copy under a different FILE name (`ob_base.rs`)
failed at `rlimit 200` where `verus.rs` passed, because the crate name changes
every symbol in the SMT encoding. `harness/check.py`'s mutant machinery keeps the
file name and changes only the directory, and a copy under the mirrored path
verifies (checked explicitly). With the opaque change the margin is wide enough
that this stopped mattering, but it is the reason the shipped budget is 400
rather than the measured floor.

### 6c. ⚠ The identity pin found a real drift

`identity` is `O0: differ`, `O3: norel` — `p29`'s pin, for `p29`'s reason (the
`-O3` residue is link layout; the `-O0` difference is `rec_open`, where
`unsafe.rs` writes `*q = v` and `verus.rs` calls vstd's `ptr_mut_write`, which at
`-O0` expands to a sequence of 16- and 32-bit moves).

⚠⚠ **It earned its keep before it was ever pinned.** With `nmade = nmade + 1`
sitting at the END of the PUT-alloc block in `unsafe.rs` and in the MIDDLE of it
in `verus.rs`, the pair measured `differ` at BOTH levels — 355 vs 356
instructions, a different register allocation and one extra `movq`. Moving the
one statement made `-O3` `norel` immediately. **The identity pin is the only
thing in this tree that would have found that.**

---

## 7. ⚠ The `model.py` question that had to be answered before the gate, not at it

`TASK_146` deliverable 2 asks whether this model can represent the stale link at
all, *"decided early and written down rather than discovered at gate time"*. The
answer is in `model.py`'s module docstring and it is **yes, with one named
limit**:

* the **simulation** (`_sim_checked`), which produces the model's answer, is a
  `dict` from key to object plus an insertion-ordered `list`. **It has no links of
  any kind, in either direction, in either list, and no buckets and no walk.**
  That is the independence axis, and it is the row's own axis: every rung records
  membership in fields inside the objects, and the model records it in two
  containers outside them;
* the **helper** `cache_fold` mirrors the Verus spec function `run`, carrying the
  object sequence, the liveness sequence, the bucket array and both list ends
  exactly as the proof does — links, walk and fuel included;
* the **detector** is a THIRD function, `_sim_buggy`, which is neither and is
  never consulted for an answer. It carries per-bucket **membership lists** and a
  `released` flag; the buggy TRIM frees the victim and leaves it in the list.

**What it represents faithfully**: that after a TRIM the victim is still reachable
by a walk of its bucket, in the same position and after the same number of steps;
that reading it is a use-after-free; that a DEL of a neighbour writes into it.
⚠ **What it collapses, said so nobody reads the derivation as more than it is**:
the membership list cannot tell *the dangling pointer is in `bucket[b]`* from
*the dangling pointer is in a live predecessor's `hn`*. **That distinction is the
row's own claim, so it is measured OUTSIDE the model**, at C level, by
`controls/harm_sites.py` (§2).

### 7a. The must-fire arm, and why it reports rather than crashes

`sanitizer_expect` is DERIVED, and the derivation **fires on shipped inputs** —
`clean` on `small`, `large` and `degenerate` (all of which TRIM, repeatedly) and
`fires` on all four adversarial files. That alone is stronger evidence than `p32`
had. `detector_selftest()` closes the other half with four cells — two probes ×
{safety line kept, safety line deleted} — **plus, since `TASK_150`, three more
that assert the PUBLISHED `sanitizer_expect` itself over the same probes in both
directions (§7c)** — and `selfcheck()` runs the whole thing on every gate
invocation, so the gate re-derives it once per input on every run.

⚠ **Every cell runs inside `try`, and an exception becomes the designed problem
string with the exception text attached.** `.memory/03-measurement.md` 19's
closing paragraph is the reason: three of the four mutations the manager planted
into `p32`'s repaired arm failed by CRASHING rather than by reporting, which is
loud and loses the diagnostic.

### 7b. ⚠⚠ THE MUST-FIRE ARM OWES THE SAME TEST, AND THE FIRST DRAFT FAILED IT

`.memory/03-measurement.md` 19 asks for exactly that, so
`.temp/t146/mustfire_probe.py` plants five mutations into a COPY of `model.py`
(the tree is never touched) and records TWO columns per row: was the mutation
CAUGHT, and was it caught by a RETURNED message or by an exception escaping.

```
M0-control               problems=False returned          OK
M1-touch-neutered        problems=True  returned          OK   MUST-FIRE ARM DEAD
M2-touch-always-fires    problems=True  returned          OK   FIRED with the line PRESENT
M3-safety-line-inert     problems=True  returned          OK   FIRED with the line PRESENT
M4-detector-raises-wrong problems=True  returned          OK   MUST-FIRE ARM BROKEN ... KeyError
```

⚠ **M4 originally read `RAISED KeyError  XX`.** A detector that raises the wrong
exception type escaped `Model.__init__` — through `_run` → `_window` →
`_sim_buggy`, before `selfcheck()` was ever reached — so the gate would have seen
a crash instead of a sentence, which is `p32`'s exact failure mode one file over.
**The repair is `Model.detector_error`**: `_window` catches ANY exception out of
`_sim_buggy`, not just `_Escape`, records it, and `selfcheck()` turns it into a
named problem. The window's answer comes from `_sim_checked` and does not depend
on the detector, so the model keeps working and says what broke.

⚠⚠ **READ 7c BEFORE QUOTING THE PARAGRAPH ABOVE.** *"catches ANY exception"* was
**false as written** — the spelling was `except Exception`, which a
`BaseException` walks straight past — and `TASK_149` measured one escaping. It is
`except BaseException` now, at all three sites, and the counterfactual is in 7c.

### 7c. ⚠⚠ THE ARM HAD TWO HOLES OF ITS OWN, AND BOTH ARE CLOSED HERE

`TASK_149` planted seven mutations `TASK_146`'s battery does not have, aimed at
the stretch `detector_selftest()` did **not** cover
(`_sim_buggy → _window → any_uaf → sanitizer_expect`), and found two.

**HOLE 1 — `BaseException` walked straight past it.** `TASK_146`'s `M4` raised a
`KeyError`, which **is** an `Exception`; `SystemExit` and `KeyboardInterrupt` are
not, and **all three** catch sites in `model.py` spelled `except Exception`. So
the failure mode entry 19 exists to prevent — loud crash, lost diagnostic — was
still reachable, and `model.py`'s own comment claimed *"`_window` catches ANY
exception"*. ⚠ Not hypothetical spelling: `.temp/t146/mustfire_probe.py:86`
itself bails out with `SystemExit`. **All three sites now spell `except
BaseException`**, and the counterfactual is measured rather than argued:

```
the SAME planted SystemExit, against HEAD's model.py:  *** ESCAPED, diagnostic lost
                              against the file today:  returned  MUST-FIRE ARM BROKEN
                                                                 (READ, safety line KEPT)
```

⚠⚠ **THIS IS TREE-WIDE, NOT `p28`'s DEFECT.** Every pattern with a must-fire arm
spells it the same way; `p28` is only where it was measured.

**HOLE 2 — the arm licensed `_sim_buggy`, not the PUBLISHED VALUE.**
`TASK_149`'s `N2` replaced `sanitizer_expect`'s body with a per-filename table
and **every cell of the four-cell arm still passed**, because the arm stops three
steps short of the string the pattern publishes.
⚠ **`.memory/03-measurement.md` 19's rule is about whatever is DERIVED, and what
this file derives is the STRING**, so the string owes an arm.
**`detector_selftest()` now has one**: it builds a real `Model` over each planted
probe — from BYTES, no file opened and nothing under `inputs/` read — and asserts
`sanitizer_expect` itself, **in both directions**, because an arm that only ever
expects `fires` is satisfied by `return "fires"`. A third probe, `_PROBE_QUIET`,
supplies the `clean` half: the same TRIM, then an operation on a different
bucket.

**And the new arm owes the same test as the thing it repairs**
(`.temp/t150/mustfire_probe3.py`, mutations planted into a COPY; the tree is
never touched):

```
mutation                             selfcheck   how        verdict
N0-control                           no problem  returned   OK
N2-per-filename-table                problem     returned   OK   <- INVISIBLE before
N3-expect-inverted                   problem     returned   OK
X1-always-fires                      problem     returned   OK   <- the QUIET probe catches it
X2-always-clean                      problem     returned   OK
N1-anyuaf-never-set                  problem     returned   OK
N4-detector-raises-BaseException     problem     returned   OK   <- ESCAPED before

mutations that ESCAPED the arm or crashed it: 0
```

Every one is caught by a **RETURNED** diagnostic rather than by a crash, which is
entry 19's closing requirement. ⚠ **The last-hop gap is a hole in the must-fire
MECHANISM, not in `p28`** — `N1` and `N3` show `p28`'s own wire was live all
along — and it applies to every pattern that derives a `sanitizer_expect`.

---

## 8. ⚠⚠ THIS PATTERN PUBLISHES NO RUNG-TO-RUNG COST, AND THE ABSENCE IS STATED

`p29` ships the same way, and the absence must not be read as a zero. Three
independent confounds, any one of which would be enough:

1. **allocation size.** A C object is four pointers plus two bytes — 40 bytes; a
   Rust object is six bytes. Same number of allocator calls, different sizes.
2. **epilogue shape**, three different loops (§5).
3. **the ten non-firing `alive_link` sites and the walk's liveness conjunct**,
   present in R4/R5 and unspellable in C.

And two measured warnings from this row's own history, which is why the absence is
deliberate rather than lazy:

* `TASK_093_REVIEW`: a p28 with a safe index arena against a raw-pointer unsafe
  rung would have published *"safe Rust is 6.02× CHEAPER than unsafe"* with
  **108.4% of the gap IN THE ALLOCATOR**, the bounds check at **3.0% of the
  magnitude and the OPPOSITE SIGN**;
* `TASK_091`: **4.0 of a 12.5 R3→R4 gap is INDEX SCALING**, not checking.

What this row publishes instead is in §2, §4b, §5 and §6 — behaviour, detector
coverage and proof burden, all of them measured.

### 8a. ⚠ AND THE RECORD CONTAINS ONE NUMBER THE RUNG NAMES WOULD MISLEAD ABOUT

`results/p28-intrusive-lists.json` and `results/tables/p28-intrusive-lists.md`
carry an `Ir` column whether or not this file draws a conclusion from it, so the
one direction a reader would otherwise misread is stated here:

```
O3 / isolated        kernel-exclusive Ir          whole-program marginal Ir/call
                     small        large           small     large
safe_naive (R2)      386,910,519  211,267,507     3406.22   16764.91
safe_tuned (R3)      436,272,774  236,511,509     3652.26   18024.41
```

**R3 — the rung named "tuned" — is DEARER than R2, in both conventions and on
both inputs** (+12.8%/+12.0% kernel-exclusive, +7.2%/+7.5% marginal). The two
conventions agree on the DIRECTION and differ on the magnitude, which is exactly
what the published table's own caveat says to expect and check.

⚠ **Nothing rests on it** — this pattern publishes no rung-to-rung cost (§8) and
`safe_tuned.rs`'s header says in terms that its three levers are *"not priced"*
and claim nothing. But *"tuned"* is a name, a reader will read it as a direction,
and the measurement says the other way. **A rung-to-rung figure this pattern does
not publish is still a figure a reader can compute from the record, so the honest
thing is to name the direction and the gap in the evidence rather than leave both
in a JSON file.**

#### ⚠⚠ THE MECHANISM, MEASURED — 72% OF IT IS THE WALK HOIST

This paragraph read *"the MECHANISM was not investigated, and that is an open
item rather than a result"* until `TASK_150`. **It is resolved**
(`TASK_149` deliverable 4, `.temp/t149/lever/`, callgrind, kernel-exclusive `Ir`,
`n_iters = 2000`). Three variants, **identical checksum on every probe**, so no
rung changed the algorithm and the port is fair — only the rung's NAME is
aspirational:

| probe | walk steps/op | A = `safe_tuned` | B = `safe_naive` | D = `safe_tuned`, walk UN-hoisted | A − B |
|---|---|---|---|---|---|
| all-TRIM (no walk) | 0 | 4,554,000 | 4,794,000 | 4,554,000 | ✅ **−240,000 (R3 CHEAPER)** |
| all GET, empty cache (walk never enters) | 0 | 6,458,000 | 4,666,000 | 5,438,000 | ⚠ **+1,792,000 (+38%)** |
| 30-deep chain, GET misses | 30 | 41,874,000 | 41,112,000 | 41,042,000 | +762,000 (+1.9%) |
| `small.bin` (the shipped mix) | mixed | 4,365,534 | 3,871,949 | 4,010,155 | **+493,585 (+12.7%)** |

`+12.7%` against the record's `+12.8%`, at a different scale. Static instruction
counts are 541 / 538 / 560, so **this is not code size — it is instructions
EXECUTED.**

> ⚠⚠ **The mechanism is the WALK HOIST, and it is a FOURTH change that
> `safe_tuned.rs`'s own header does not list among its levers.** Un-hoisting it
> recovers **72%** of the gap on `small.bin` and **57%** on the GET-miss probe.
> The cost is paid **per OPERATION, not per walk step**: with a 30-deep walk the
> gap is `+1.9%`, with no walk at all it is `+38%` — the hoisted walk's setup runs
> on every opcode including the ones that never use it.

`safe_tuned.rs:3-7` says *"Three levers, and all three are on the same thing — R2
re-indexes `tab` once per FIELD and this rung indexes it once per OBJECT"*. Those
three are neutral-to-favourable: **on the TRIM path, which uses none of the
hoisted walk, R3 is genuinely 5% cheaper**, which is lever 3 doing what it says.
The dominant term is a control-flow change on a different axis and it goes the
other way. The two candidates this file named are both accounted for: **the hoist
is the one, at 72%, and the `hn`-per-step one is inside the 1.9%.**

---

## 9. What was NOT done

* **No address-keyed R4/R5.** The faithful raw-pointer port exists as a control
  and is not a rung; the doubly-linked-list well-formedness `TASK_091` names was
  not attempted. §5.
* **No cost measurement of any kind between rungs.** §8.
* **No sweep bands were measured.** `inputs/gen.py --sweep` emits three
  (operations, key space, TRIM fraction) and nothing has been run over them.
* **`arm_safe_bug`'s two spellings are the two this file names**, not an
  enumeration of safe ports. An `Rc`/`Weak` port and a `HashMap`-plus-arena port
  are both plausible and neither was built; `TASK_093` measured the first at
  `bwd=32127` and that number is inherited, not re-derived.
* **The `-O0d` (debug-assertions on) column was not examined.**
* ✅ ~~The mechanism behind §8a was not investigated.~~ **RESOLVED at `TASK_150`**
  — it is the walk hoist, at 72%, paid per operation. §8a.
* **`controls/harm_sites.py` runs ASan at `-O1` only**, inherited from the
  demonstration it grew out of.
* ⚠ **`B3` is not in the shipped battery**, although §6a-bis measures it and it
  is the only arm that shows the DRIVER consuming the kernel's postcondition.
  Adding it moves `controls/proof_mutants.py`, which costs a ~40-minute
  regeneration of `controls/proof_mutants.json` (`A3` alone is ~25 minutes of
  it). `TASK_150` did not spend it and the battery is unchanged; the same is
  true of holding the mutant FILE NAME at `verus.rs` (§6b's crate-name
  fragility), which `proof_mutants.py` still does not do.
* ⚠ **`controls/proof_mutants.json`'s pinned `invariant` still carries the
  RETRACTED prediction** that `A6` fails, while the same file's `MUTANTS` table
  declares `A6` `expect="verify"` and §6a retracts it in bold. The `invariant` is
  the string a reader quotes. Same 40-minute regeneration; not spent.
* ⚠⚠ **The gate NEVER runs a detector on the HARDENED arm, for ANY pattern** —
  `check_sanitizers` builds `c/kernel.c`, gcc, `-O1` only. `p28`'s own missed cell
  is **CLEAN** (`TASK_149` 6: **0 defects over 88 hardened-arm cells**, 11
  compiler × detector columns × 8 inputs, each column positively controlled;
  `TASK_150` re-confirmed it for the ASan-recover and UBSan-only columns, §2b).
  **So this is a GATE gap and not a `p28` defect**, it is in the gate digest, and
  it is left for the manager together with the other owed gate repairs.

---

## 10. ⚠⚠ THE `slb-contract` HASH, AND WHY THIS ROW HAS NO PRE-BUILD SNAPSHOT

**`PROTOCOL` rule 6 asks for the block's sha256 to be recorded in `NOTES.md`
*before any cell is built*. `p28` DID NOT DO IT** — `TASK_146` shipped the row
without a disclosure, and `TASK_149`'s review did not raise it. ⚠ **That evidence
cannot be recovered**: a pattern lands in one commit, so `git show HEAD:` compares
the working tree to the *shipped* text and says nothing about the *first-written*
text. **The recorded first hash was the only possible artefact and it does not
exist.** Recorded here so nobody later reads the table below as one.

**What CAN be verified, and is** (`python3 harness/tools/contract_diff.py p28`,
which derives it from `git` alone):

```
block sha256  HEAD (TASK_146 + TASK_149):  5c92154096baea5de8f8fd4c24a16c6d285000687bd6006782837db00d724455
block sha256  tree (TASK_150):             f0bd1f608df27895eed33e180bc1ba75b7c87f2a83b13829acbbc8ac778a081c

collapse IDENTICAL · driver IDENTICAL · ensures IDENTICAL · identity IDENTICAL
idiom.forbidden IDENTICAL · idiom.why IDENTICAL · kernel IDENTICAL
miri IDENTICAL · model IDENTICAL · note IDENTICAL · requires IDENTICAL
verus IDENTICAL
idiom.required  ⚠ MOVED       2 path(s) moved: ['idiom', 'idiom.required']
```

**Exactly one entry moved, and it is the last one — the epilogue entry whose
unscoped *"and neither double-frees"* the measurement in §2d refuted.** The edit
is a RETRACTION of a falsified claim, made after measuring and disclosed as such;
`.memory/01-ladder.md`'s direction test is what governs it. ✅ **It pins no new
spelling**: `required` carried **32** backticked spellings before the edit and
**32** after, over the same 12 entries, so no rung gained or lost an obligation.

⚠ **This is `PROTOCOL` rule 6's second half — *the hash matched and the
measurement refuted the claim* — on its second pattern after `p46`.** Rule 6
protects against a declaration edited AFTER measuring and does nothing about one
that measurement has since FALSIFIED, and `p28`'s disclosure would have verified
perfectly the whole time.

---

## 11. SLB-TRUSTED-ARGUMENT sections

`harness/check.py` stage 5c-twin requires one per trusted item, for the three
things no stage of the gate can judge. **p28's seven trusted items are the seven
`p27` and `p29` ship**, so where the argument is theirs it says so — and ⚠ **where
it is not, the difference is called out**, because p28's `identity` pin sits at
`p29`'s level rather than `p27`'s and one of `p27`'s backstops is therefore
weaker here too.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's body is `v[i]` on the
same `&[u8]`, with the same parameters and the same clause text. `v[i]` is the
*checked* form of the identical operation — `<[u8] as Index<usize>>::index`
performs the bounds test `i < v.len()` that `get_unchecked` requires the caller
to have performed — so a `requires` too weak to license the unchecked read is too
weak to license the indexed one, and Verus sees the second. There is no other
safe expression whose value is `v@[i as int]`.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly one operation, a read of one element,
and returns it. `r == v@[i as int]` names that element and its value. There is no
second read, no write, no aliasing and no interior mutability: `v` is `&[u8]`, so
the item cannot modify anything, and `u8` has no padding or niche that could make
*"the value read"* ambiguous. `TASK_009_REVIEW`'s completeness question — a body
that *also* reads `i + 1` — would be invisible to this contract, and that is why
Miri is mandatory here and runs over `unsafe.rs`, which contains the same
expression inline.

**(c) Does each clause mean the same in both configurations?** One `requires` and
one `ensures`, both in terms of `v@`, `i` and `r` only; neither mentions a
`p28`-defined item that `--cfg slb_twin` could redefine. The two items sit in the
same module with the same imports, and their signatures are character-identical
after normalisation, which the gate checks structurally.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a)** Identical in shape to `buf_get_unchecked` one type over: trusted body
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`, twin body `v[i]`, same
parameters, same clause text. The checked form performs exactly the bounds test
the unchecked one delegates to the caller.
⚠ **p28 instantiates this item at THREE element types** — `*mut Obj` for `tab`,
`u8` for `live` and `u8` for `bucket` — where `p27` and `p29` use two. The
argument does not depend on `T`: the item is generic, `T: Copy`, and the twin is
generic in the same way, so the twin covers every instantiation at once rather
than the ones this kernel happens to use.

**(b)** One read of one element, returned. `r == v@[i as int]` names it. No
write, no second read, no interior mutability — `v` is `&[T; N]`. ⚠ **For
`T = *mut Obj` the value read is a raw pointer, and reading a raw pointer is not
a dereference**: the clause says what the pointer VALUE is and says nothing about
what it points at, which is exactly right, because whether the pointee is live is
`base`'s `rec_ok` and not this item's business.

**(c)** `requires i < v@.len()` and `ensures r == v@[i as int]`, both in terms of
`v@`, `i`, `r`. `v@` for a `[T; N]` is vstd's array view, which `slb_twin` cannot
redefine.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a)** Trusted body `unsafe { *v.get_unchecked_mut(i) = x; }`, twin body
`v[i] = x;`, same parameters and clause text. `IndexMut` performs the bounds test
the unchecked store delegates.

**(b)** One store of one element. `final(v)@ == old(v)@.update(i as int, x)` is a
statement about the WHOLE array after the call, not just about slot `i`, so a
body that also wrote `i + 1` would violate it — which is a strictly better
position than the read items are in, and worth saying because it is the one place
`TASK_009_REVIEW`'s x4 does not bite. ⚠ **`x` is unconstrained by the `requires`
and the gate SHOUTS `[tcb-unsafe]` about it**; `spec.md`'s
`unsafe_justifications` carries the argument and this is the eighth pattern to
exercise that documented false positive. `x` is a pure value, stored and never
used as an address, an index or a length.

**(c)** Two clauses, in terms of `v`, `i` and `x` only, using vstd's `Seq::update`
and the array view. Nothing `slb_twin` can redefine.

## SLB-TRUSTED-ARGUMENT verus.rs rec_alloc

**(a) The twin's body is `allocate(size, align)` — `vstd::raw_ptr::allocate`
itself**, which is the strongest stand-in available anywhere in this project: the
checked implementation of the trusted item is the very API the item is a copy of,
so what stage 5c-twin proves is that this crate's contract is **no stronger than
the one vstd already discharges**. If any `requires` here were weaker than
vstd's, or any `ensures` stronger, the twin would not verify. `p27`'s NOTES 10
records the four-way clean negative against the obvious circularity attack, and
that argument is about the mechanism rather than about `p27`, so it transfers
unchanged.

⚠⚠ **ONE OF `p27`'s TWO BACKSTOPS IS WEAKER HERE, exactly as it is on `p29`, and
the difference must not be glossed.** `p27` closes the body-drift gap — the twin
cannot see the item's BODY, which is a copy of vstd's rather than a call to it —
with (i) `md5_raw` of `unsafe::kernel` and `verus::kernel` equal at
`-O3 isolated`, and (ii) Miri over `unsafe.rs`. **On p28 leg (i) is
`md5_raw_norel`, not `md5_raw`** (§6c): the normalised instruction text is
identical and only pc-relative displacement fields differ, which is link layout
rather than codegen — so *"R5's inlined body IS R4's"* still holds at the
instruction level but is certified one notch weaker. **At `-O0` the pair is
`differ` outright**, so leg (i) says nothing there at all. ✅ **Leg (ii) is
unchanged and is the independent one**: Miri runs over `unsafe.rs`, which
contains this body.

The item exists for **codegen and not for trust**: vstd carries no `#[inline]` on
`allocate`, so calling it emits a GOT-indirect cross-crate call that `unsafe.rs`
cannot produce.

**(b)** The body performs one operation — `std::alloc::alloc(layout)` after
`Layout::from_size_align_unchecked(size, align)`, aborting on null — and returns
the pointer plus two tracked permissions. The three clauses state exactly what a
caller may conclude: the `PointsToRaw` covers `[addr, addr+size)`, the `Dealloc`
records the address, size, align and provenance the eventual `rec_free` must
match, and the returned pointer's provenance is the `PointsToRaw`'s. **Three
clauses, and `spec.md`'s `verus.items` dump lists three.** Two further clauses
exist in vstd and are deliberately NOT shipped — `addr + size <= usize::MAX + 1`
and `addr % align == 0` — because this kernel allocates at `align == 1`, where
the second is a tautology and the first is never used; dropping them makes the
item strictly WEAKER, which is the direction the gate asks for. The `requires` is
vstd's own, and `size != 0` is not a tautology (`OBJSZ` is 6, but the item is
generic in `size`).

**(c)** Every clause is in terms of `size`, `align` and the return binding `pt`
only, and all of `PointsToRaw::is_range`, `Dealloc::view` and `DeallocData` are
vstd items that `slb_twin` cannot redefine. Shipped item and twin sit in the same
module with the same imports and the same `opens_invariants none`, and their
signatures are character-identical after normalisation — ⚠ **which the gate
checks, and which it CAUGHT here**: the first draft wrapped the twin's return
type across four lines and stage 5c-twin refused it as *"not the trusted item's
signature"*, because a twin with its own contract is a second declaration rather
than a check.

## SLB-TRUSTED-ARGUMENT verus.rs rec_free

**(a) The twin's body is `deallocate(p, size, align, pt, dealloc)` —
`vstd::raw_ptr::deallocate` itself**, for the same reason and with the same force
as `rec_alloc`: the gate proves this crate's copy is no stronger than vstd's
original. Same codegen-not-trust motivation, and the same weakened leg (i)
caveat.

**(b)** The body performs one operation, `std::alloc::dealloc(p, layout)`. It has
**six `requires` and NO `ensures`**, and that is complete rather than empty: the
operation returns nothing, and everything a caller may conclude from it is
negative — the `PointsToRaw` and the `Dealloc` are CONSUMED, so no later read of
that address is provable. ⚠⚠ **And that is the whole of what it buys, which §6
of this file measures rather than asserts**: a consumed token forbids a READ; it
does not force the deallocation to HAPPEN (`Tracked<Dealloc>` is affine —
`A6-epilogue-dead` verifies while leaking, §6a) and it does not reach a LINK left
behind in a chain (`A4-spec-weaken` verifies, §6). The six `requires` are vstd's
six verbatim.

**(c)** Every clause is in terms of `p`, `size`, `align`, `pt` and `dealloc`, all
through vstd's `Dealloc` and `PointsToRaw` accessors, which `slb_twin` cannot
redefine.

## SLB-TRUSTED-ARGUMENT verus.rs load_input

**(a)** There is no twin and there can be none: the body is file I/O through
`common/driver.rs`, which sits outside `verus!` and is external-by-default. It is
`external_body` because Verus cannot see through it, not because anything
unchecked happens inside — the body contains **no `unsafe` at all**.

**(b)** It states **no `ensures`**, so it grants the caller nothing. Every fact
`main` uses about the input comes from the loop invariant it proves for itself,
not from this item. An `external_body` with no postcondition is the weakest
possible trusted item: it can only lose information.

**(c)** No clauses, so nothing can mean two things.

## SLB-TRUSTED-ARGUMENT verus.rs emit

**(a), (b), (c)** Identical to `load_input`: plain Rust output through
`common/driver.rs`, no `unsafe`, no `requires`, no `ensures`, no twin possible
and nothing granted. It is in the TCB tally because it is `external_body`, and
`.memory/04-verus.md`'s rule is that the tally counts items rather than judging
them — the judgement is here, and it is that this one carries no weight.
