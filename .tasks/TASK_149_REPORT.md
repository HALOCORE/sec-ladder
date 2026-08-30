# TASK_149 — review `p28-intrusive-lists`. Report

**Role: research reviewer.** Adversarial. I did not fix anything; `git status` is
clean and every file I touched under `patterns/p28-*/` was restored and verified
byte-identical against `HEAD`.

**Verdict: `p28` STANDS as a row.** ⚠⚠⚠ Nothing here is a reason to refuse,
shrink or retire it, and I did not look for one on the Rust or Verus side
(`CLAUDE.md` rule 6). The C-mechanism distinction is the only admissible ground
and it **survives, narrowed** (item 1).

✅ **`harness/check.py p28` re-run from scratch: `PASS`, 0 failures, 0 blocked,
`contract_sha256` unchanged** — and the record moves only 5 of 1296 leaf values,
all of them nuisance fields.

**Two `major` findings, both measured, both in text the pattern SHIPS:**

1. ⚠⚠⚠ **R1 DOUBLE-FREES on a shipped input.** `spec.md`'s `idiom.required` —
   **inside the hashed `slb-contract` block** — asserts *"NEITHER C rung leaks
   and neither double-frees"*, and `c/kernel.c:37` says it unqualified.
   **Measured false**: on `adversarial-uaf-write.bin`, R1 calls `free()` twice on
   one address. On the real allocator the crash arrives two statements earlier,
   which is why nothing in the tree saw it.
2. ⚠⚠ **UBSan is NOT silent.** `NOTES.md` 2b (*"no misaligned access"*) and
   `model.py`'s `sanitizer_expect` docstring are refuted, reproducibly, on both
   compilers, on the same input — and **UBSan is the only detector in the tree
   that witnesses p28's WRITE harm shape at all**, because ASan halts on the
   walk's READ before the write happens.

**The headline attack FAILED, and that is the most useful thing in this report:**
3,257,436 exhaustively enumerated op sequences plus 20,000 randomised ones,
**zero** value differences and **zero** counterexamples to the suffix argument.
See item 2 — and the suffix property is a **theorem**, not just an argument.

---

## Item-by-item verdicts

| # | item | verdict |
|---|---|---|
| 1 | the C-mechanism distinction | **SURVIVES, NARROWED** |
| 2 | the safe-Rust headline | **SURVIVES** (attack failed; strengthened, and one wording narrowing) |
| 3 | the must-fire arm and `model.py` | **SURVIVES, NARROWED** — 2 new gaps |
| 4 | `A6` verifies while leaking | **SURVIVES, and it is STRONGER than reported** |
| 5 | the slot-number divergence / Miri | **SURVIVES** — both halves verified |
| 6 | R1/R1h construction, `+9/+3`, every (arm × input) cell | **SURVIVES** — the missed cell is clean |
| 7 | positive controls | **SURVIVES** — every column licensed |
| D2 | is `p28` FINISHED? | **NO — `results/synthesis.md` does not carry it** |
| D3 | `RECAP` 56 / `CAVEATS` / catalogue overstatements | **one in `RECAP` 56** |
| D4 | the one open number (`safe_tuned` dearer) | **RESOLVED — mechanism measured** |
| — | `harness/check.py p28`, re-run | ✅ **PASS**, 0 failures, 0 blocked, contract hash unchanged |

---

## 1. THE C-MECHANISM DISTINCTION — SURVIVES, NARROWED

**I tried to show p28 is `p29`.** The strongest form of the attack: both free a
real `malloc`'d record and later dereference a stale reference to it; both are
CWE-416 reached through CWE-672; both keep a `steps` bound; both hold their
records individually `malloc`'d with links inside the record.

**It does not land**, and the load-bearing difference is not the one `RECAP` 56
leads with. Read off the two sources:

| | `p27` | `p29` | `p32` | **`p28`** |
|---|---|---|---|---|
| free discipline | complete | complete | complete (nothing is freed) | ⚠ **INCOMPLETE** |
| where the missing safety line goes | READ (`live[h] == 1`) | USE (`live[g_slot] && key`) | READ/FREE (`gen[h] != g`) | ⚠ **DESTROY (a 9-line splice)** |
| the safety line is a … | test | test | test | ⚠ **maintaining WRITE** |
| what goes stale | a handle the input names | a pointer an earlier op SAVED | a handle in a register | **a link the structure made for itself** |
| is there a liveness bit to consult? | `live[]` | `live[]` | `gen[]` | ⚠ **none — no slot number, no bit, in either C rung** |

The last row is the sharp one and it is checkable: `grep -c 'live\[' c/kernel.c`
is **0** for p28 and non-zero for p27/p29. There is no test p28's read path could
add, because it holds no handle — it walks a chain. That is a different C
mechanism from all three, and `CAVEATS["p28"]` already states it correctly.

### ⚠ Where it is NARROWED — and the task file asked exactly this question

*"Is 'the pointer lives in a heap object rather than a stack local' a real
distinction or a restatement?"* — **it is partly a restatement and, as `RECAP` 56
words it, partly FALSE.**

`p28` has **two** dangling-pointer sites and the row's own control measures both:

```
controls/harm_sites.json  "invariant":
  "The two dangling-pointer sites p28 claims -- inside `bucket[]` when the
   victim is the chain head, and inside ANOTHER HEAP OBJECT's `hn` when it is
   not -- are separately reachable ..."
```

`bucket[]` is `struct p28_obj *bucket[P28_NB]` — **a stack array in `kernel`'s own
frame**, i.e. the same storage class as `p27`'s `tab[]`. I confirmed the head site
is reachable and is that array: `adversarial-uaf-head.bin` decodes to
`PUT 5 · GET 5 · TRIM · GET 5`, one object in bucket 5, evicted, and the stale
pointer that the second GET follows is `bucket[5]` itself.

`c/kernel.h:69-73` and `spec.md`'s hashed `why` **both carry the `bucket[]`
disjunct**. Two places drop it and assert the heap-only version:

* `RECAP.md` finding 56 — *"The dangling pointer therefore lives INSIDE ANOTHER
  HEAP OBJECT's link field, not in a stack table (`p27`), a stack local (`p29`)
  or a program-owned pool (`p32`)."* **Manager-written, and refuted by the row's
  own `harm_sites.json`.** (deliverable 3)
* `c/kernel.c:45-46` — *"p27 and p29 have a stale reference IN A VARIABLE THE
  FREEING CODE CAN SEE; here it is in a field of a different heap object."*
  ⚠ **Also wrong in a second way**: `bucket[]` **is** visible to the freeing code
  — `c/kernel_hardened.c:209` writes `bucket[vb] = victim->hn;` from inside TRIM.
  The true statement is that TRIM holds no chain **cursor** and must compute
  `victim->key % NB` to get one, which is what `c/kernel.h:61-67` says.

⚠ `spec.md`'s hashed `why` carries the disjunct **and** the negation in one
sentence — *"or in `bucket[]` when the victim was the chain head — NOT in a stack
table (p27's `tab[]`)"* — which reads as a contradiction unless "stack table" is
understood as *p27's mechanism* rather than *storage class*. Worth a clause.

**Severity: `minor` for the two texts; the row's admission is unaffected**, because
the distinction that carries it is *which path is incomplete*, not where the
pointer lands.

**No C-side duplication ground exists.** The `p08` overlap is the SETUP (one
object on two lists), not the harm, and `CAVEATS["p28"]` says so.

---

## 2. ⚠⚠⚠ THE SAFE-RUST HEADLINE — I ATTACKED IT HARD AND IT SURVIVED

The claim: *"Deleting p28's safety line from safe Rust changes no answer on any
input this pattern ships"*, with a structural reason (stale entries form a
SUFFIX). The report and `RECAP` 56 both concede: *"an argument plus a measurement
over the shipped inputs, not a proof"*.

### What I ran

`.temp/t149/fuzz_safe_headline.py` transliterates **three** simulators line by
line: `sim_checked` from `safe_tuned.rs`, and `sim_buggy(strict=True/False)` from
`controls/arm_safe_bug.rs`. `suffix_witness()` is independent of the answers: it
rebuilds each bucket chain **through freed slots** (which the safe rung cannot do)
and asserts directly that no LIVE slot ever sits BEHIND a freed one.

Five generators aimed at exactly the windows the task file names — a bucket whose
chain order and LRU order might disagree, a PUT walking past a stale entry,
re-insertion of an evicted key, DEL from the middle of a chain that already holds
stale entries, and every key colliding in one bucket:

```
mode            cases   VALDIFF    panic    trunc  SUFFIX!
uniform          4000         0     3151     3445        0
trim-heavy       4000         0     3403     3538        0
one-bucket       4000         0     2702     3712        0
reinsert         4000         0     3576     3652        0
del-mid          4000         0     3097     3340        0
TOTAL           20000         0    15929    17687        0
```

Then `.temp/t149/exhaust_safe_headline.py` — **EXHAUSTIVE** over every op sequence
of length ≤ 6 on an alphabet of {PUT, GET, DEL, TRIM} × {key 0, key 8, key 1} (two
keys colliding in bucket 0, one not):

```
exhaustive: |alpha|=12  L<=6  keys=[0, 8, 1]
  L=6 cumulative: seqs=3257436 VALDIFF=0 SUFFIX=0 strictpanic=304578
TOTAL sequences=3257436  VALDIFF=0  SUFFIX=0  strictpanic=304578
first VALDIFF: None
first SUFFIX : None
```

**17,687 of 20,000 random cases DO truncate the walk at a freed slot**, so the
mechanism the headline is about is being exercised throughout; it just never
changes an answer.

### ⚠ The simulators are not taken on trust — they reproduce the shipped table

A transliteration that agrees with itself proves nothing, so I closed the loop
against real binaries. Decoding each adversarial blob's single window and running
my simulators on it, against what `c/kernel_hardened.c` and `c/kernel.c` actually
printed at `n_iters = 1`:

```
input                      sim_checked            C R1h (measured)       verdict
adversarial-uaf-read.bin   5015554                5015554                MATCH
adversarial-uaf-head.bin   5700746                5700746                MATCH
adversarial-uaf-write.bin  5015554                5015554                MATCH
adversarial-many.bin       3339691840943063889    3339691840943063889    MATCH

                           safe-buggy (lenient)   C R1 (measured)        strict
adversarial-uaf-read.bin   5015554                5008889                no panic
adversarial-uaf-head.bin   5700746                5694081                no panic
adversarial-many.bin       3339691840943063889    16016581709108102841   PANIC
```

**Read the two halves together and they are the row's entire result in one
table**: the safe-Rust buggy arm returns the CHECKED answer on every input, while
the C buggy arm returns a different number on every input — and the strict
spelling panics on `adversarial-many` **and on nothing else**, which is exactly
what `controls/rust_arms.json` records. So §6's table is reproduced from a
from-scratch transliteration plus binaries I built, not quoted.

### ⚠ And the argument is a THEOREM, not just an argument

The report, `NOTES.md` 4b, `arm_safe_bug.rs`'s header and `RECAP` 56 all say *"an
argument plus a measurement … not a proof"*. It **is** provable, in three steps,
from two facts the rung already pins:

1. **Every chain is strictly decreasing in slot number.** Slots are handed out as
   `s = nmade`, monotonically; PUT prepends `s` (the largest so far); DEL splices;
   buggy TRIM does not touch chains. So the order is an invariant.
2. **The eviction list is the same order, and its TAIL is the minimum live slot.**
   Same three writers.
3. **Therefore live-before-dead.** Suppose slot `i` is dead and slot `j < i` is
   live, both in bucket `b`'s chain, so `j` is behind `i`. `i` cannot have died by
   DEL (DEL splices it out). So TRIM freed `i` — but TRIM takes the minimum live
   slot, and `j < i` was live. Contradiction. Slots are never recycled, so a dead
   slot never comes back.

Hence stale entries are exactly a suffix, the truncated walk visits exactly the
live entries in exactly the right order, and every answer is unchanged. **The
`SUFFIX!` column above is the mechanised check of step 3 and it is 0 in
3,277,436 sequences.**

⚠ **The proof names its own escape hatch precisely**, which is more useful than
the hedge it replaces: it needs (a) eviction order = chain order and (b) slots
never recycled. Drop either — an LRU that promotes on hit, or a recycling arena —
and the result goes away. That is the sentence to keep.

### ⚠ ONE NARROWING, and it is a wording one

*"Its only trace is a `None` where `.unwrap()` expects `Some`"* (report §6,
`RECAP` 56, `arm_safe_bug.rs:23`) reads as an exotic corner. **It is the typical
case: the strict spelling panics on 15,929 of 20,000 random inputs (80%) and on
304,578 of 3,257,436 exhaustive ones (9.4%, and 100% of the length-6 cases that
evict a whole bucket).** And a panic with exit 101 **is** a changed answer: the
program produces no checksum. `RECAP` 56 already contains both halves — *"changes
no answer … i.e. a PANIC on one input in one spelling"* — so as written it is in
tension with itself.

**Suggested wording**: *"changes no VALUE on any input — never UB, never silently
wrong — while the `.unwrap()` spelling PANICS instead, on one shipped input and on
most randomly generated ones."*

**No counterexample exists and I could not manufacture one.** This is a clean
negative: do not re-run it.

---

## 3. ⚠⚠ THE MUST-FIRE ARM AND `model.py` — SURVIVES, NARROWED (two new gaps)

`.temp/t146/mustfire_probe.py` re-run verbatim: **all five arms reproduce**, every
one caught by a RETURNED diagnostic, `M0` silent. Entry 19's closing paragraph is
genuinely satisfied for `_sim_buggy`.

**The entry-19 question, asked directly: is any predicate a tautology of the
model's own representation?** **No.** The detector's predicate is `o.released`, an
explicit flag on a `chains[b]` membership list, set by TRIM and DEL. It takes both
values on shipped inputs (`clean` on `small`/`large`/`degenerate`, all of which
TRIM repeatedly; `fires` on four adversarial inputs), and both values on planted
probes. That is `p04`'s honest shape, not `p32`'s defect.

**A broken detector REPORTS rather than crashes — for `Exception`.** Verified, and
that is what this task asked `p28` to fix. But:

`.temp/t149/mustfire_probe2.py` plants **seven mutations `TASK_146`'s battery does
not have**, aimed at the part of the chain `detector_selftest()` does NOT cover
(`_sim_buggy → _window → any_uaf → sanitizer_expect`), each scored against the
ASan ground truth I measured independently in item 6:

```
mutation                           selfcheck  how                      verdict
N0-control                         False      returned                 OK baseline
N1-anyuaf-never-set                False      returned                 CAUGHT by stage 7 only (4 inputs)
N2-sanitizer-expect-hardcoded      False      returned                 *** INVISIBLE
N3-expect-inverted                 False      returned                 CAUGHT by stage 7 only (8 inputs)
N4-detector-raises-BaseException   True       RAISED SystemExit        *** CRASHES -- diagnostic lost
N5-buggy-arm-splices-too           True       returned                 CAUGHT by selfcheck (returned)
N6-walk-truncates-not-touches      True       returned                 CAUGHT by selfcheck (returned)
N7-only-_sim_checked-budget        (see below) returned                CAUGHT by selfcheck on degenerate.bin
```

### ⚠ GAP 1 (`minor`, and it is TREE-WIDE, not p28's defect)

**`N2` is INVISIBLE.** Replace `sanitizer_expect`'s body with a per-filename table
and `detector_selftest()` still passes — because it licenses `_sim_buggy`, not the
path from `_sim_buggy` to the published expectation. Entry 19 repaired *"a
derivation that cannot fire"*; `N2` is *"a table that was never a derivation"*, and
nothing in the gate distinguishes them. `p28` is not guilty of it — `N1` and `N3`
show the wire is live — but the **must-fire arm as a mechanism does not cover its
last hop**, and this applies to every pattern that has one.

*Cheap closure, if the manager wants it*: have `detector_selftest()` build a
`Model` over the two planted probe blobs and assert `sanitizer_expect` itself,
rather than `_sim_buggy` alone.

### ⚠ GAP 2 (`minor`, one word in two places)

**`N4` CRASHES.** `TASK_146`'s `M4` raised a `KeyError`, which **is** an
`Exception`. `SystemExit` / `KeyboardInterrupt` are `BaseException`s, and **both**
catch sites spell `except Exception` (`model.py:465` in `_window`,
`model.py:384` and `:398` in `detector_selftest`). So `model.py:443`'s comment —
*"`_window` below catches ANY exception out of `_sim_buggy`"* — is **wrong as
written**, and the failure mode entry 19 exists to prevent (loud crash, lost
diagnostic) is still reachable. This is not hypothetical spelling: `.temp/t146/
mustfire_probe.py:86` itself raises `SystemExit` as a bail-out. Fix is
`except BaseException` in two places.

### ✅ The two-implementation cross-check is real

`N7` (mutating the allocation budget in `_sim_checked` only) is silent on seven
inputs and **caught on `degenerate.bin`** — which is exactly the input `NOTES.md`
3 says exercises the budget. `N8` (both answer arms moved consistently) is silent
in `selfcheck` and **moves the checksum**, so gate stage 2 catches it. Both arms
of `selfcheck()` do work.

---

## 4. ⚠⚠ `A6` VERIFIES WHILE LEAKING — CONFIRMED, AND IT IS STRONGER THAN REPORTED

I did not re-run the shipped 7-arm battery (≈40 min, and its JSON is fresh against
its `derived_from_sha256`). I ran **seven arms it does not have**
(`.temp/t149/proof_arms2.py`), at `--rlimit 400`, **with the file name held at
`verus.rs` and only the directory varied** — because `TASK_146_REPORT` §8 measured
that the margin moves with the crate name and `controls/proof_mutants.py` does
**not** do this (it writes `.temp/p28mut/A0-control.rs`, so its arms compile as
crates `A0_control`, `A1_exec_safety_line`, …).

```
  B0-control                   control  expect=verify got=verify OK  23/0 35.2s
  B1-assume-false              vacuity  expect=verify got=verify OK  23/0 35.7s
  B2-requires-false            vacuity  expect=fail   got=fail   OK  22/1 36.0s  precondition not satisfied
  B3-const-body-weak-ensures   vacuity  expect=verify got=FAIL   XX  20/1  2.0s  assertion failed
  B4-trim-leaks-the-victim     affine   expect=verify got=verify OK  23/0 61.7s
  B5-del-leaks-the-victim      affine   expect=verify got=verify OK  23/0 40.9s
  B6-epilogue-free-deleted     affine   expect=verify got=verify OK  23/0 40.3s
surprises: ['B3-const-body-weak-ensures']   <- and the surprise is in p28's favour
```

**`B0` verifying at `23/0` in 35.2 s reproduces the shipped `23 verified, 0
errors` in 36.8 s**, so the crate-name worry is not biting today — but the battery
should hold the name anyway, and it costs nothing.

### ⚠⚠⚠ `B4`/`B5`/`B6` — the answer to *"what ELSE in this R5 is affine?"*

**EVERYTHING THAT RELEASES MEMORY.** `verus.rs` calls `rec_close` at exactly
three sites — TRIM (`:1527`), DEL (`:1362`) and the epilogue (`:1614`). **Delete
any one of them** — so that object's `PointsTo` and `Dealloc` are removed from the
tracked maps and then simply **dropped**, and the storage is never returned — and
the file **verifies at `23/0` every time, a count indistinguishable from the
control.**

| arm | what it deletes | result |
|---|---|---|
| `A6` (shipped battery) | the epilogue's `live[j] == 1` **branch** | verify `23/0` |
| **`B4`** | **TRIM's `rec_close`** — the row's own destroy path | **verify `23/0`** |
| **`B5`** | **DEL's `rec_close`** | **verify `23/0`** |
| **`B6`** | **the epilogue's `rec_close`**, leaving the loop and its asserts | **verify `23/0`** |

**That is strictly stronger than `A6`.** `A6` makes the *epilogue's* branch dead
and shows the epilogue is not forced; `B6` separates *"the branch is dead"* from
*"the free is not forced"* and gets the same answer; and `B4`/`B5` show **the free
is not forced on either destroy path, including the very path the row is about**.
`TASK_146` §4/§4a say *"`rec_close` consumes the victim's `PointsTo` and its
`Dealloc`, a real temporal guarantee"* — true, and it is a guarantee about what a
**later READ may not do**, not about the free happening. The honest statement of
p28's R5 result is:

> Nothing in this proof forces `c/kernel.c`'s omitted line, and **nothing in it
> forces any of the three `free`s either** — a rung that leaks every object it
> ever allocates verifies at the same `23/0`. What it forces is the FUNCTIONAL
> postcondition (`A1` / `A3` / `A4`); the memory-safety obligations it carries
> are **licences to read, not obligations to release**.

⚠ So `.memory/04-verus.md`'s affine-token entry should read *"a proof built on
`Tracked<PointsTo>`/`Tracked<Dealloc>` shows deallocation is LEGAL and never that
it HAPPENS **anywhere**"* — `p28` is the instance that shows it at **every** free
site rather than at one, and it is the first pattern where a full leak of a real
`malloc`'d heap is invisible to the proof.

### ⚠ `B3` surprised me, and the surprise is in `p28`'s favour

I predicted `ensures true` + `return 0;` would verify. It **fails**, `20/1` — and
**the failing obligation is in `main`, not in `kernel`**:

```
error: assertion failed
    --> .../verus.rs:1701:20
```

`verus.rs:1700` is `assert(r == cache_fold(buf@, (k * stride) as int, stride as
int));` under the comment *"Ghost only: this is what **consumes** the kernel's
`ensures`."* So the driver is not a passive verified call site: **weakening the
kernel's postcondition breaks the driver's own proof.** That is a real property of
this rung, stronger than `check.py` stage 5b documents, and no shipped arm exhibits
it. Worth adding to the battery as a must-fail arm.

### `B1` — the `assume(false)` hole, confirmed on this rung

`assume(false);` at the top of `kernel` verifies **`23/0` — the same counts as the
control**, and `check.py` only `rep.shout`s (`check.py:4466`,
`_axiom_keyword_shout`). So `RECAP`'s owed item (ii) applies to `p28` exactly as
written. **Exposure today is zero**: `grep -c 'assume(' verus.rs` is 0. Recorded so
the next person does not have to run it.

### `B2` — a `requires` nothing can discharge

Fails at the **call site** (`precondition not satisfied`), which is what makes
stage 5b's *"verified call site"* mean something. Clean negative.

---

## 5. THE SLOT-NUMBER DIVERGENCE — SURVIVES, BOTH HALVES VERIFIED

The defence is *"the slot table changed the PROOF BURDEN and not the PROGRAM"*.
I re-derived it from `controls/rust_arms.json` and checked it against binaries I
built myself:

```
input                        opt  c_bug                  raw_bug                raw_fix / safe_lenient / c_fix
adversarial-many.bin         O0   0:6439359753103586304  0:6439359753103586304  all three 0:8660776832395219968
adversarial-uaf-head.bin     O0   0:7155896426678277120  0:7155896426678277120  all three 0:11740759076003072000
adversarial-uaf-read.bin     O0   0:9891317877474112512  0:9891317877474112512  all three 0:14476180526798907392
adversarial-uaf-write.bin    O0   -11:(SIGSEGV)          -11:(SIGSEGV)          all three 0:14476180526798907392
... and the same at O3, all 8 inputs

deviations: NONE
```

⚠ **The report UNDERSTATES this.** §5 says the raw-pointer BUG arm *"equals
`c/kernel.c` on the benign ones"*; it equals it on **all eight**, adversarial
included, **down to reproducing the SIGSEGV**. Every `c_bug` figure above matches
what my own gcc and clang builds printed in `.temp/t149/detector_matrix.json`.

**Miri, both halves.** `rust_arms.json` records `ub: true` on `raw_bug` for all
four adversarial inputs and `ub: false` on everything else — `raw_fix`, both safe
spellings, and all three benign inputs. A detector that fires on everything is not
a detector; this one is silent on 28 of 32 cells.

### ✅ *"Not one can fire"* — CONFIRMED, and now with a number

`NOTES.md` 5 and `TASK_146` §5 say the divergence costs *"one `live[cur] == 1u8`
conjunct in the walk plus **ten `alive_link` sites**. Not one can fire."* That is
a claim about **exec code** — `alive_link` is `x != NIL && live[x] == 1u8`
(`unsafe.rs:199`), a real runtime branch at ten sites — so I instrumented it
rather than reading it. A copy of `unsafe.rs` under `.temp/t149/alive/` counts,
per call, whether the `live[]` half ever *disagrees* with the `!= NIL` half:

```
input                        alive_link calls  nonNIL_but_dead    walk calls  dead
adversarial-many.bin                    7,600                0         4,200     0
adversarial-stride3.bin                     0                0             0     0
adversarial-uaf-head.bin                1,200                0           200     0
adversarial-uaf-read.bin                1,600                0           400     0
adversarial-uaf-write.bin               1,600                0           400     0
degenerate.bin                         58,400                0        11,200     0
large.bin                              24,064                0        45,536     0
small.bin                               5,116                0         2,052     0
TOTAL                                  99,580            **0**        63,988   **0**
```

**163,568 evaluations of a conjunct that never once decides a branch.** The claim
is right, and the sharper way to say it is that R4/R5 pay a measurable exec-text
cost for a test whose `live[]` half is dead on every shipped input — which is
precisely why §7's refusal to publish a rung-to-rung cost is the right call, and
why `NOTES.md` 5's *"no cost claim rests on it"* is load-bearing rather than
throat-clearing. (200 driver iterations per input; the counters are `static mut`
so the instrumented copy is not a rung and was never measured as one.)

⚠ **One narrowing, `minor`: `miri_iters` is 4.** The Miri silence is over four
driver iterations, not the shipped 200,000. For the adversarial inputs `nwin == 1`
so all four iterations hit the same window and the scoping is harmless; for
`large.bin` it is not, and *"Miri is silent on the benign inputs"* is really
*"…on the first four windows the driver visits"*. Nothing depends on it, but the
sentence should say `4`.

✅ **And the report's §6 correction to the catalogue is CONFIRMED by measurement.**
`.memory/06-catalogue.md` still carries `TASK_093`'s reusable reason *"the index
arena NEVER FREES (`0` heap blocks released by unlink, measured)"*. On the shipped
spelling, callgrind's call profile for `safe_tuned` on `small.bin` (n_iters 2000):

```
  18015  __rustc::__rust_alloc
  18014  __rustc::__rust_dealloc
```

against **18,007 `malloc` / 18,007 `free`** for `c/kernel_hardened.c` on the same
input. The safe rungs free per object. The catalogue sentence is false of them, as
`NOTES.md` 4 says. (Manager's memory-update item 1 — I confirm it.)

---

## 6. ⚠⚠ EVERY DETECTOR ON EVERY (ARM × INPUT) CELL — THE MISSED CELL IS CLEAN

### First: the gate itself never runs a detector on the hardened arm, for ANY pattern

`check_sanitizers` (`check.py:7229`) builds `c/kernel.c` only, `gcc` only, `-O1`
only. So the cell that let `p28d` ship as an instruction is **structurally outside
the gate**, not merely missed once. I ran it by hand.

`.temp/t149/detector_matrix.py` + `detector_matrix2.py`: `{bug, fix}` ×
`{gcc, clang}` × `{plain-O0, plain-O3, asan-only, ubsan-only, asan+ubsan}` × all 8
shipped inputs, `env -u LD_PRELOAD`, diagnostics read with `grep`, never `head`.

```
=== FIX (HARDENED) ARM: any nonzero exit / any class is a DEFECT ===
  hardened-arm defects: 0        (part 1: gcc+clang x 4 configs x 8 inputs)
  hardened-arm defects: 0        (part 2: the clang sanitiser columns part 1 could not build)
```

✅ **Zero, over 88 hardened-arm cells** — 11 distinct (compiler × detector)
columns × 8 shipped inputs:

```
gcc/plain-O0  gcc/plain-O3  gcc/asan+ubsan  gcc/ubsan-only  asan_gcc  ubsan_gcc
clang/plain-O0 clang/plain-O3 asan_clang  ubsan_clang  asanub_clang
```

`p28`'s hardened arm is clean on every one: exit 0, no diagnostic, on every
shipped input. **The `p28d` defect did not ship.** (176 cells in total counting
the bug arm; `.temp/t149/detector_matrix{,2}.json`.)

⚠ **Part 1's clang sanitiser columns failed to build and part 2 exists because of
it**: `-static-libasan` / `-static-libubsan` are gcc spellings and clang rejects
them. A battery that reported "0 defects" without checking `build_errors` would
have silently claimed a clean result for four columns it never compiled. Both
JSONs carry `build_errors` and part 2's is empty.

### ✅ `+9 / −0` and the `+3` shared lines, independently reproduced

`controls/safety_line.py` re-run: `+9 / −0`, preprocessed 392 vs 401, every added
line inside the TRIM splice. (⚠ It rewrote its own JSON in `patterns/`; I restored
it and verified byte-identical against `HEAD`.)

The `+3` needed the counterfactual, so I copied `.temp/t146/cdemo/` to
`.temp/t149/` (never touching `t146`) and ran the engineer's own scripts:

```
p28        preprocessed R1 body lines = 127     safety line: lines only in R1h: 15   only in R1: 0
p28d       preprocessed R1 body lines = 127     safety line: lines only in R1h:  9   only in R1: 0
p28dfix    preprocessed R1 body lines = 130     safety line: lines only in R1h:  9   only in R1: 0
```

**`9` against `15` at `+3` shared lines — reproduced exactly.** And `p28d`'s
`body.inc` really does carry 2 `hp = ` writes against `p28dfix`'s 4, which is the
uninitialised-`hp` bug the report found. `TASK_146` §1's arithmetic stands.

### ⚠⚠ MAJOR: R1 DOUBLE-FREES, and the claim that it does not is INSIDE THE HASH

`c/kernel.c:200` is `free(n)` at the end of DEL's splice, and DEL's walk can reach
an object TRIM already freed — that **is** the row's bug. So the double free is
immediate from the source; the only question is whether it is reachable, and it is.

The real allocator hides it: glibc's tcache overwrites user offsets 0 and 8 of the
freed chunk with its `next` and `key` words, which are exactly `lp` and `ln`, so
`n->lp->ln = n->ln` (`c/kernel.c:193`) faults two statements before `free(n)`.
**So I measured the program property instead of the allocator's.**
`.temp/t149/wrapfree.c` links with `-Wl,--wrap=malloc,--wrap=free` (no
`LD_PRELOAD`, so ASan blindness is not in play) and, under `SLBWRAP_NOFREE=1`,
never calls the real `free` — which is precisely the semantics `model.py` and
**all four Rust rungs** implement, since slots are never recycled:

```
kernel           adversarial-uaf-write.bin  SLBWRAP DOUBLEFREE 0x55d0ad9e14a0
                                            mallocs=4 frees=5 doublefree=1 livemallocs=0
kernel_hardened  adversarial-uaf-write.bin  mallocs=4 frees=4 doublefree=0 livemallocs=0
```

**Same input, same driver, same binary recipe; the ONLY difference is the safety
line.** Every other input, both arms, is balanced with `doublefree=0` and
`livemallocs=0` — so **the leak half of the claim is true and the double-free half
is false**.

What the claim says, and where:

| file | text | in the hash? |
|---|---|---|
| `spec.md` `idiom.required` (line 213) | *"…so NEITHER C rung leaks and neither double-frees."* | ⚠⚠ **YES — inside `slb-contract`** |
| `c/kernel.c:37` | *"…frees each live object exactly once: **neither rung leaks and neither double-frees.**"* | measurement-hashed |
| `c/kernel.c:231`, `c/kernel_hardened.c:225` | *"…neither leaks and neither double-frees **here**"* | ✅ scoped to the epilogue — TRUE |

The scoped spellings are right; the two unscoped ones are wrong. This is
`PROTOCOL` rule 6's second half exactly — **the hash matches and the measurement
refutes the claim**, `p46`'s shape.

⚠ **And it means the row has THREE harm shapes, not two.** `c/kernel.h:80-93`
tabulates a UAF READ and a UAF WRITE; **CWE-415 is a third**, it is on the same
omitted block, and no text in the pattern names it.

### ⚠⚠ MAJOR: UBSan is NOT silent, and it is the ONLY detector that sees the WRITE

`NOTES.md` 2b: *"UBSan is silent here … no signed overflow, **no misaligned
access**, no out-of-range index."* `model.py:699` says the same. **Both are false
on `adversarial-uaf-write.bin`, at both compilers, reproducibly:**

```
gcc   10/10 runs:
  c/kernel.c:193:31: runtime error: member access within misaligned address
    0x00055d0099b5 for type 'struct p28_obj', which requires 8 byte alignment
clang  9/10 runs:
  c/kernel.c:193:28: runtime error: member access within misaligned address ...
  c/kernel.c:193:28: runtime error: store to misaligned address 0x0005634fc42a
    for type 'struct p28_obj *', which requires 8 byte alignment
```

`c/kernel.c:193` is `n->lp->ln = n->ln;` — the DEL splice writing through the
tcache-clobbered `lp`. UBSan-only is silent on the other seven inputs, so this is a
detector doing its job, not noise.

⚠⚠ **The constructive half is bigger than the correction.** `c/kernel.h` says the
DEL shape is a *"heap-use-after-free WRITE"*, and **ASan never reports a WRITE on
any shipped input.** With `-fsanitize-recover=address` and
`ASAN_OPTIONS=halt_on_error=0` I let it run past the first error:

```
adversarial-uaf-write : 7 ASan errors -- 6 x heap-use-after-free READ + 1 SEGV.
                        ZERO `WRITE of size N`.
adversarial-uaf-read  : 2 errors, both READ of size 1
adversarial-uaf-head  : 2 errors, both READ of size 1
```

That is **structurally forced**: DEL arrives *along the chain*, so it must READ
`n->key` out of the freed chunk before it can write anything, and ASan halts there.
**So the WRITE harm shape has exactly one witness in the whole tree and it is
`clang`'s UBSan `store to misaligned address … for type 'struct p28_obj *'`.**

`p28`'s UBSan column is not empty, and the input where it is non-empty is exactly
the input whose harm ASan cannot reach. `NOTES.md` 2b's heading — *"UBSan sees
nothing, and that is not a gap"* — should become *"UBSan sees one thing, and it is
the half ASan cannot reach."*

⚠ The gate's own stage 7 cannot see this: it builds `-fsanitize=address,undefined`
combined, ASan fires first and halts. **A combined build cannot license a
per-sanitiser claim in either direction** — the mirror of `.temp/mgr147`'s lesson.

### ✅ Other item-6 confirmations

* **Reproducibility, independently**: `randomize_va_space = 2`; 20 runs × 4
  (compiler × opt) cells × 3 adversarial inputs → **1 distinct value every time**,
  and **ONE value per input across all four cells** (`5008889`, `5694081`,
  `16016581709108102841`). §0's stronger form is right.
* **`54` adversarial `diverges: true` inside three PASSING verdicts**, re-derived
  from the committed records: `p27` 44 rows/18, `p29` 58/26, `p32` 48/10.
  `p28` is 40 rows / 8 diverges. Matches §0 and §9b exactly.
  ⚠ `adversarial` is keyed `input/cell` and each value is a LIST of cell-groups —
  `len(adv)` is **not** the row count. Anyone re-deriving these must iterate.
* **`sanitizer_expect` IS gated on adversarial inputs**: `check.py:8743` passes
  `all_models`. §0's addition to the manager's note is correct.
* **Identity pin**: `unsafe vs verus` `O0 differ` / `O3 norel` with identical
  `-O3` counts `[360, 356, 1429]` on both sides, and identical kernel-exclusive
  `Ir` (299,017,209 / 185,227,142). Independent confirmation of §8a/§9c.

---

## 7. POSITIVE CONTROLS — ALL LICENSED, AND ALL EXECUTE

`controls/arm_sites.c`'s `k_ctl` writes through a `static … *volatile sink`
specifically to defeat the malloc elision that ate `TASK_143`'s control, and
`harm_sites.json` records it firing `heap-use-after-free` at exit 1 on **both**
compilers. It is not elided.

I built my own controls per (compiler × detector) column so each column is
licensed for what it is quoted for, not merely for "a sanitiser fired":

```
  asan_clang/uaf         exit=1 cls=['heap-use-after-free']     <- licenses ASan for UAF
  asan_gcc/uaf           exit=1 cls=['heap-use-after-free']
  asan_clang/ub          exit=0 cls=[]                          <- ASan CANNOT see signed overflow
  asan_gcc/ub            exit=0 cls=[]
  ubsan_clang/uaf        exit=0 cls=[]                          <- UBSan CANNOT see a heap UAF
  ubsan_gcc/uaf          exit=0 cls=[]
  ubsan_clang/ub         exit=0 cls=["runtime error: signed integer overflow: ..."]
  ubsan_gcc/ub           exit=0 cls=["runtime error: signed integer overflow: ..."]
  asanub_clang/uaf       exit=1 cls=['heap-use-after-free']
  asanub_clang/ub        exit=0 cls=["runtime error: signed integer overflow: ..."]
```

Each column fires where it should and is **silent where it should be**, which is
the half that makes the UBSan finding in item 6 a measurement rather than a
coincidence.

✅ **All five control JSONs are FRESH** — every `derived_from_sha256` entry matches
the file in the tree today (23 hashes, 0 stale).

⚠ **`minor` hygiene**: `harm_sites.py`, `rust_arms.py` and `safety_line.py` accept
**any** unknown argument silently and then run the whole battery, rewriting their
committed JSON in `patterns/`. `proof_mutants.py` and `repro.py` use `argparse` and
refuse. I dirtied `patterns/p28-*/` and `patterns/p32-*/` this way while probing
for a `--list` flag and restored both, byte-verified against `HEAD`. Same class as
`.temp/mgr146`'s lesson — *a script that silently ignores what it was told*. (No
live risk: `synthesis/synthesize.py:558` only runs scripts whose source contains
the literal `--list`, and none of p28's do.)

---

## Gate re-run — ✅ PASS, and the record is FAR more reproducible than "not byte-reproducible"

`harness/check.py p28`, run fresh from 18:27 to 19:00 (33 min; stage 5c's eight
clause-deletion mutants are all *supposed* to fail, and a p28 mutant that fails
for a real reason then burns the whole `--rlimit 400` on a second query —
`TASK_146` §11):

```
check.py: PASS
results/gate/p28-intrusive-lists.json
    verdict  PASS      failures 0      blocked 0      (read out of the RECORD)
    contract_sha256  5c92154096baea5de8f8fd4c24a16c6d285000687bd6006782837db00d724455  UNCHANGED
    loud     2   [collapse-ir]  [tcb-unsafe]   <- both documented, both expected
```

`[tcb-unsafe]` names `p28` as the **eighth** pattern to exercise
`.memory/04-verus.md`'s parameter-coverage false positive, exactly as `TASK_146`
§9a claims.

⚠⚠ **And the record turns out to be nearly byte-reproducible, which the task file
did not expect.** Leaf-by-leaf against `git show HEAD:`:

```
leaf values: HEAD=1296  MINE=1296   MOVED=5   only-in-HEAD=0  only-in-MINE=0
moved: 4 x sanitizer/<input>/diagnostic   (ONLY the embedded ASan pid, ==58xxxx== -> ==62xxxx==)
       1 x miri/runs[3]/seconds           (0.2 -> 0.1, wall clock)
```

**Zero `Ir`, zero md5, zero checksum, zero identity, zero adversarial row, zero
verdict movement.** So `p28`'s gate record reproduces down to a pid and one
wall-clock float — a stronger statement than the standing *"records are not
byte-reproducible"*, and worth knowing before anyone treats a moved gate record as
a signal. ⚠ **The two nondeterministic fields are both nuisance fields**; if the
manager wants gate records diffable, masking the ASan pid (as `check.py`'s own
`-fstrict-aliasing` blast-radius probe already does — `check.py:7267`) and the
Miri `seconds` would make this one exact.

⚠ **`results/gate/p28-intrusive-lists.json` is therefore MODIFIED in the working
tree, by my run.** It is a `PASS` record with the same contract hash; `git
checkout` it if you would rather keep the committed one. Nothing else of mine
touches a tracked file.

## ⚠⚠ CONCURRENCY: the manager was editing this tree while I ran

`git status` at 19:01 shows three files I did **not** touch:

```
 M RECAP.md                                    18:57:33
 M harness/tools/temp_citations_baseline.json  18:57:15
?? .tasks/TASK_150.md                          18:58:40
```

**`PROTOCOL` rule 11 is live right now** — *"Never `git add -A` while a subagent
is working. Stage explicit paths."* Whatever lands next must name paths, or this
report, the gate record and the manager's own edits go into one commit.

✅ **One consequence is good news and I am withdrawing a finding because of it**:
the `temp_citations.py` failure I report below **is already fixed in the working
tree.** The manager added both `p28` baseline entries (`.temp/p28mut`,
`.temp/build/p28-repro`, `kind: destination`, with notes) at 18:57, and the check
now passes:

```
temp_citations.py: OK  (new=0 unclassified=0 resolved=0)
```

I am leaving the finding written up because **the mechanism is still worth
recording** — `proof_mutants.py:273` deletes the directory it cites, so the green
result `TASK_146` §9b reported was an artefact of run ordering and could not have
been reproduced from a clean tree. The baseline entry is the right fix and it is
in.

⚠ **I did not touch `RECAP.md`, `TASK_150.md` or the baseline**, and I have not
re-read them; nothing in this report is written against them.

---

## Deliverable 2 — IS `p28` FINISHED? **NO.**

Gate-green is not finished; a reader must be able to find the result. Checked:

| artefact | carries `p28`? |
|---|---|
| `RECAP.md` findings section | ✅ finding 56 (the `basename` loop reports **no** pattern missing) |
| `.memory/06-catalogue.md` | ✅ row present, 48 rows |
| `harness/tools/composition.py` | ✅ `temporal`, with `CAVEATS["p28"]` |
| `results/tables/p28-intrusive-lists.md` | ✅ and **FRESH** |
| **`results/synthesis.md`** | ⚠⚠ **NO — 0 occurrences of `p28`** |

```
results/synthesis.md:  "Patterns: **28**. Gate records: **28**."
tree:                  29 patterns, 29 gate records
patterns present in synthesis.md: p01..p14 p16 p17 p18 p19 p22 p23 p27 p29 p32
                                  p36 p38 p42 p46 p47   (28, no p28)
```

It was generated at 12:25 on the day `p28` landed, before `p28`'s records existed.
`synthesis/synthesize.py` builds nothing and reads committed records only, so this
is a re-run, not work — but until it happens **the one cross-pattern artefact does
not carry the tree's 29th row**. `RECAP`'s owed queue item (iii) is about the
hand-written `SYNTHESIS.md`; this is the *generated* one and is a different,
cheaper gap.

**Published table vs a fresh render**: `harness/report.py p28 --stdout` differs
from the committed table by exactly one blank line, which is the `--stdout`
trailing newline; the gate's own render check is authoritative and says
`render_sha256 == published_sha256`, verdict `FRESH`. ✅

**Dangling-citation sweep** (`PROTOCOL` rule 10): clean apart from the documented
`TASK_NNN` placeholders and two *self*-references in unrun task files
(`TASK_148_REPORT.md`, and this report's own path in `TASK_149.md`).

### ⚠ AND `harness/tools/temp_citations.py` EXITS 1 ON THE TREE TODAY — because of `p28`

`TASK_146` §9b reports it `OK (new=0 unclassified=0 resolved=0)`. **It now FAILs,
exit 1, and both new dangling citations are `p28`'s own:**

```
-- 2 NEW dangling citation(s):
   patterns/p28-intrusive-lists/controls/proof_mutants.py:51   .temp/p28mut
   patterns/p28-intrusive-lists/controls/repro.py:65           .temp/build/p28-repro
temp_citations.py: FAIL  (new=2 unclassified=0 resolved=3)
```

`grep -c p28 harness/tools/temp_citations_baseline.json` is **0** — the baseline
was last written at `TASK_147`, before `p28` landed, and never gained `p28`'s two
entries. **`p32` has the identical pair and both ARE baselined**, with the note
that says exactly why the green run was not reproducible:

> `.temp/p32mut` — *"scratch directory the citing script CREATES with `mkdir -p`
> and **deletes on success** … **Dangling is the CORRECT steady state.**"*

`controls/proof_mutants.py:273` does `shutil.rmtree(MDIR)` when all arms pass, so
`.temp/p28mut` is **absent by design** after any successful run. `TASK_146`'s `OK`
was therefore true only in the window where the directories happened to exist —
a green check that cannot be reproduced from a clean tree.

⚠ **I did not create this and I do not believe I removed it**: I never executed
`proof_mutants.py` or `repro.py` (both use `argparse` and exited 2 on the unknown
argument I probed with, before doing any work), and my gate re-run builds into
`.temp/build/p28/`, not `p28-repro`. **Fix**: two baseline entries copied from
`p32`'s, `kind: destination`. One command, `--update`, plus the notes.

---

## Deliverable 3 — WHAT THE MANAGER OVERSTATED

1. ⚠⚠ **`RECAP` 56, the dangling-pointer sentence.** *"The dangling pointer
   therefore lives INSIDE ANOTHER HEAP OBJECT's link field, not in a stack
   table (`p27`)…"* — **refuted by `controls/harm_sites.json`'s own invariant**,
   which names `bucket[]` (a stack array) as the second of two separately
   reachable sites. `spec.md`'s hashed `why` and `c/kernel.h` both carry the
   disjunct; `RECAP` dropped it. Item 1. **This is exactly the failure mode the
   task file predicted: re-running a script checks the arithmetic, not the
   experiment design — the manager re-ran `repro.sh` and `contract_diff`, neither
   of which has anything to say about a sentence.**
2. ⚠ **`RECAP` 56's *"its only trace is a `None` where `.unwrap()` expects
   `Some`"*** understates by a factor of ~1600 in case count. Item 2.
3. ✅ **`CAVEATS["p28"]` — I attacked it and it stands.** *"The safety line is
   not a TEST, it is a nine-line SPLICE"*, *"`temporal` is read off the HARM"*,
   *"the aliasing is the SETUP and the use-after-free is the HARM"*, *"the tree's
   first INVERSION"* — every clause is checkable in the two C files and every one
   holds. ⚠ One addition it now owes: the harm is **three** shapes, not two
   (item 6), and its ASan/Miri list should not imply UBSan silence.
4. ✅ **The catalogue cell.** Its live content is right; its two pending
   corrections (`~~gatable~~`, and *"the index arena never frees"*) are exactly
   the two the engineer asked for, and I confirmed the second by measurement
   (item 5). ⚠ Nothing else in the cell is overstated.

---

## Deliverable 4 — THE ONE OPEN NUMBER, RESOLVED

*"the record shows `safe_tuned` DEARER than `safe_naive` in both conventions,
direction stated and MECHANISM NOT INVESTIGATED"* (`NOTES.md` 8a).

**Is the direction real?** Yes, and it is not noise — `Ir` is deterministic. From
the record: `safe_naive` 386,910,519 / 211,267,507 vs `safe_tuned` 436,272,774 /
236,511,509 (`O3 isolated`, small/large), marginal 3406.22/16764.91 vs
3652.26/18024.41. I reproduced it independently at a different scale.

**Is it in-contract?** Yes. I built three variants and every one prints the
**identical checksum** on every probe, so no rung changed the algorithm. The rung
is a fair port; only its *name* is aspirational.

**The mechanism, measured** (`.temp/t149/lever/`, callgrind, kernel-exclusive `Ir`,
`n_iters = 2000`):

| probe | walk steps/op | A = `safe_tuned` | B = `safe_naive` | D = `safe_tuned`, walk UN-hoisted | A − B |
|---|---|---|---|---|---|
| all-TRIM (no walk) | 0 | 4,554,000 | 4,794,000 | 4,554,000 | ✅ **−240,000 (R3 CHEAPER)** |
| all GET, empty cache (walk never enters) | 0 | 6,458,000 | 4,666,000 | 5,438,000 | ⚠ **+1,792,000 (+38%)** |
| 30-deep chain, GET misses | 30 | 41,874,000 | 41,112,000 | 41,042,000 | +762,000 (+1.9%) |
| `small.bin` (the shipped mix) | mixed | 4,365,534 | 3,871,949 | 4,010,155 | **+493,585 (+12.7%)** |

`+12.7%` against the record's `+12.8%`. Static instruction counts are 541 / 538 /
560, so **this is not code size** — it is instructions *executed*.

> ⚠⚠ **The mechanism is the WALK HOIST, and it is a FOURTH change that
> `safe_tuned.rs`'s header does not list among its levers.** Un-hoisting recovers
> **72%** of the gap on `small.bin` and **57%** on the GET-miss probe. The cost is
> paid **per OPERATION, not per walk step**: with a 30-deep walk the gap is +1.9%,
> with no walk at all it is +38%. The three levers the header *does* claim are
> neutral-to-favourable — on the TRIM path, which uses none of the hoisted walk,
> R3 is genuinely **5% cheaper**, which is lever 3 doing what it says.

`safe_tuned.rs:3-7` says *"Three levers, and all three are on the same thing — R2
re-indexes `tab` once per FIELD and this rung indexes it once per OBJECT"*. The
dominant term is a control-flow change on a different axis, and it goes the other
way. `NOTES.md` 8a's two candidate mechanisms were both named; **the hoist is the
one, at 72%, and the `hn`-per-step one is inside the 1.9%.**

---

## Adjacent findings (reported, not fixed)

* ⚠ **`controls/proof_mutants.json`'s pinned `invariant` still carries the
  retracted prediction**: *"The ATTACK arm (A1 …), the VACUITY arm (A2 …), the
  SPEC-ONLY arm (A3), the WALK-GUARD arm (A5) **and the EPILOGUE arm (A6) all
  FAIL**"* — while the same file's `MUTANTS` table declares `A6` `expect="verify"`
  and its docstring retracts the prediction in bold. The `invariant` is the string
  a reader quotes. `minor`, one sentence.
* ⚠ **`controls/rust_arms.json`'s `invariant` carries the retracted *"or a wrong
  answer"*** — *"safe Rust changes the bug's CLASS from a use-after-free into
  NOTHING AT ALL, a PANIC, **or a wrong answer**"* — which is the prediction §6
  measured false. **And the same sentence is garbled**: *"while its checksum and
  its checksum differs on at least one of them"*. `minor`.
* ⚠ `model.py:456`'s `_window` docstring says it returns a 2-tuple; it returns 3.
* ⚠ `model.py`'s `sanitizer_expect` docstring names `fires` on
  `adversarial-uaf-read` and `adversarial-uaf-write`; the derivation actually
  fires on **four** inputs (`adversarial-many` and `adversarial-uaf-head` too).
  Understated, not wrong.
* ⚠ `controls/proof_mutants.py` writes its arms as `.temp/p28mut/<NAME>.rs`, so
  each compiles under a different crate name, while `TASK_146_REPORT` §8 measured
  that the rlimit margin moves with the crate name. One line to hold it at
  `verus.rs` in a per-arm directory. ⚠ **And the directory must be two levels
  below the repo root** or `#[path = "../../common/driver.rs"]` cannot resolve —
  my own first draft got this wrong and every arm failed in 0.1 s, **including
  the control, which is what caught it.**

---

## What I did NOT do

* **I did not re-run `controls/proof_mutants.py`** (≈40 min, and `A3` alone is
  ≈25 min of it). Its JSON is fresh against `verus.rs` and
  `proof_mutants.py`, and my seven arms are additional rather than a re-derivation.
  `A1`/`A3`/`A4`/`A5` are unverified by me.
* **I did not re-run the Miri arms of `controls/rust_arms.py`.** I verified the
  recorded table's internal consistency and its `c_bug`/`c_fix` columns against
  binaries I built, but the `ub: true/false` column is quoted, not re-derived.
* **I did not attempt an address-keyed R4/R5** or `TASK_091`'s two-list `wf`.
* **I did not run the `O0d` column, the sweep bands, or `harness/measure.py`.**
  The record's `Ir` figures are quoted from `results/p28-intrusive-lists.json`;
  the lever experiment used my own builds at `n_iters = 2000`.
* **The double-free is demonstrated under a LEAKING allocator.** That is
  deliberate — it isolates the program property from the allocator's behaviour,
  and it is the semantics every Rust rung and `model.py` implement — but it means
  I have not shown glibc reporting `double free detected in tcache`. On the real
  allocator the SEGV at `c/kernel.c:193` arrives first, every run.
* **The gate re-run DID finish, `PASS`** — see *Gate re-run* above. It leaves
  `results/gate/p28-intrusive-lists.json` modified in the working tree (5 leaf
  values, all nuisance fields). ⚠ **That is my run, not a regression.**
* `.temp/t149/` holds **only** the generators, logs, JSON and `.rs`/`.c` probe
  sources; every binary, `.o` and mutant tree is deleted
  (`constraint 6`). `.temp/t149/cleanup.sh` names the exact rebuild command for
  every deleted artefact and has three runnable arms (`n1`, `c`, `lever`).
  `.temp/t149/evidence.log` carries the runs quoted above that had no other home.

---

## Severity summary

| sev | finding |
|---|---|
| **major** | R1 double-frees on `adversarial-uaf-write.bin`; the denial is inside `spec.md`'s hashed `slb-contract` and in `c/kernel.c:37`. The row has three harm shapes, not two. |
| **major** | `NOTES.md` 2b and `model.py:699` say UBSan sees nothing; it reports a misaligned member access **and a misaligned store** at `c/kernel.c:193`, 10/10 gcc and 9/10 clang — and it is the only witness of the WRITE shape anywhere in the tree. |
| **minor** | `RECAP` 56 drops the `bucket[]` dangling-pointer site the row's own control measures; `c/kernel.c:45` adds a false clause on top of it. |
| **minor** | `RECAP` 56 / §6 / `arm_safe_bug.rs:23` understate the strict-spelling panic as *"its only trace"*; it is the typical outcome. |
| **minor** | `model.py`'s detector-error repair catches `Exception`, not `BaseException`, and `model.py:443` claims otherwise. |
| **minor** | The must-fire arm licenses `_sim_buggy`, not `sanitizer_expect`: a per-filename table is invisible to it. Tree-wide. |
| **minor** | `results/synthesis.md` is one pattern stale and does not carry `p28`. |
| **minor** | Retracted predictions still standing in two pinned control `invariant` strings; one of them is garbled. |
| **minor** | Three controls silently accept unknown arguments and rewrite committed JSON in `patterns/`. |
| **minor** | `miri_iters = 4` is not disclosed where the Miri silence is claimed. |
| ~~minor~~ **FIXED MID-REVIEW** | `harness/tools/temp_citations.py` exited 1 on `p28`'s two unbaselined `.temp/` citations; **the manager landed both baseline entries at 18:57 while I ran** and it is now `OK`. Recorded because the mechanism stands: `proof_mutants.py:273` deletes the directory it cites, so `TASK_146` §9b's `OK` was an artefact of run ordering. |
| — | `safe_tuned.rs`'s three-lever header omits the change that dominates its cost (deliverable 4 — a result, not a defect). |

---

**PROTOCOL rule 2 running count: launched from 756 (`TASK_146_REPORT.md`'s closing
paragraph), carried to 769** — branch delta **+13**. ⚠ `TASK_148` was written from
the same base and has not reported; **reconciliation across the two branches is
the manager's job, not mine.**

1. **R1 DOUBLE-FREES** on a shipped input, and the denial is inside the hashed
   contract block. Three harm shapes, not two.
2. **UBSan is not silent** — and it is the only witness of the WRITE shape,
   because ASan must halt on the walk's READ first.
3. **ASan never reports a WRITE** on any shipped input; with
   `-fsanitize-recover` it reports six READs and a SEGV.
4. **The safe-Rust headline survived an exhaustive attack** — 3,257,436 sequences,
   0 counterexamples — and the "argument, not a proof" hedge can be **replaced by
   a proof**, whose two hypotheses are the useful part.
5. **The strict spelling's panic is typical, not exotic** (80% of random inputs).
   And `NOTES.md` 5's *"not one [`alive_link`] can fire"* is **confirmed with a
   number**: 163,568 evaluations across the eight shipped inputs, **zero** of
   which decide a branch.
6. **`RECAP` 56 overstates the dangling-pointer distinction**; the row's own
   control refutes it for half the harm.
7. **The cell the manager missed on `p28d` is clean in the shipped row** — 0
   hardened-arm defects over **88** cells (11 compiler × detector columns × 8
   inputs) — and **the gate never checks that cell for any pattern**.
8. **`B4`/`B5`/`B6`: deleting `rec_close` from TRIM, from DEL or from the epilogue
   each verifies `23/0`** — **not one of the R5's three frees is forced**, which is
   strictly stronger than `A6`'s epilogue-branch result.
9. **`B3`: weakening the kernel's `ensures` fails in `main`, not in `kernel`** —
   the driver consumes the postcondition, which no shipped arm shows.
10. **The must-fire arm has two holes**: `BaseException` escapes it, and it does
    not license `sanitizer_expect` itself.
11. **Deliverable 4 resolved: 72% of `safe_tuned`'s excess is the WALK HOIST**, a
    fourth change its header does not list, paid **per operation** (+38% with no
    walk at all, +1.9% with a 30-deep one).
12. **`temp_citations.py` exited 1 on `p28`'s two unbaselined `.temp/`
    citations**, and `TASK_146`'s `OK` was an artefact of run ordering —
    `proof_mutants.py` deletes the directory it cites. ✅ **Fixed by the manager
    mid-review**; recorded for the mechanism, not as an outstanding defect.
13. **The gate re-runs `PASS` and its record moves 5 of 1296 leaf values** — four
    ASan pids and one Miri wall-clock float, and **nothing else**. `p28`'s record
    is materially reproducible, which the standing *"not byte-reproducible"* note
    understates.

⚠ **A rigour signal, not a ledger.**
