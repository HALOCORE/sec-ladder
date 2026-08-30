# p28 — intrusive doubly linked lists, two link sets, incomplete destroy

Measured notes. `spec.md` carries the reasoning and the pins; `c/kernel.h`
carries the kernel contract; this file carries what was **run**, including the
three places a prediction written into this tree turned out to be wrong.

⚠ **Every claim below is re-derivable.** `controls/*.py` regenerate their own
JSON sidecars, `inputs/gen.py` regenerates the blobs, `harness/build.py` the
binaries, and the scratch under `.temp/t146/` carries the Verus obligation
census and the C demonstrations.

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

## 2. The two harm shapes and the two SITES, measured

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

### 2b. UBSan sees nothing, and that is not a gap

`model.py`'s `sanitizer_expect` derives the TEMPORAL half only. UBSan is silent
here for `p27`'s and `p29`'s reason: no signed overflow, no misaligned access, no
out-of-range index. **R1's every index is in range; what is out of range is the
object's LIFETIME.**

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

**Deleting p28's safety line from safe Rust changes no answer on any input this
pattern ships.** Its only trace is a `None` where `.unwrap()` expects `Some`.

⚠ **And there is a reason, which is worth more than the table.** The eviction
list is insertion-ordered and every chain is newest-first, so **the globally
oldest object in a bucket is that bucket's chain TAIL** — TRIM always evicts a
chain tail, and the entries the buggy rung leaves behind form a SUFFIX. A walk
that stops at the first `None` slot loses only objects that are already gone, so
the safe rung's walk sees exactly the live prefix, which is exactly the correct
chain. GET and DEL are right for a structural reason rather than by luck. (⚠ That
is an argument plus a measurement over the shipped inputs, not a proof. A cache
whose eviction order and chain order disagreed would not have it.) The one path
that notices is PUT, which writes the old chain head's `hp` *without walking to
it* — and when every object in the bucket has been evicted, that head is a `None`
slot.

**So safe Rust's answer to p28's omission is: NOTHING, or a PANIC, decided by the
input and by which of two idiomatic safe spellings the port uses. Never undefined
behaviour, and — on these inputs — never a silently wrong answer.** Miri agrees:
silent on `arm_safe_bug` in both spellings on all eight inputs, while it reports
`Undefined Behavior: in-bounds pointer arithmetic failed` on
`controls/arm_rawptr.rs`'s bug arm on all four adversarial inputs and on nothing
else.

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
  every input at both optimisation levels, and its BUG arm equals `c/kernel.c` on
  the benign ones;
* the DETECTOR moves. Miri sees the raw-pointer bug arm and cannot see the
  slot-table one, because in the slot table the stale link is a `u8` and reading a
  `u8` is never UB. **The shipped `unsafe.rs` is correct, so Miri reports nothing
  on it on any input** — that is what `spec.md`'s `miri.reason` says and it is not
  a gap in the run.

**What it costs in EXEC TEXT**, counted in `unsafe.rs` and `verus.rs`: one
`live[cur] == 1u8` conjunct in the walk plus **ten `alive_link` sites** (PUT ×2,
DEL ×4, TRIM ×4). Not one can fire. ⚠⚠ **`p29` could put its liveness conjuncts
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
{safety line kept, safety line deleted} — and `selfcheck()` runs it on every gate
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
and the measurement says the other way. ⚠⚠ **The MECHANISM was not
investigated**, and that is an open item rather than a result: R3 reads `hn` on
every walk step where R2 reads it only when it advances, and R3 hoists the walk
out of the opcode dispatch, but which of those (or neither) accounts for the gap
has not been measured. **A rung-to-rung figure this pattern does not publish is
still a figure a reader can compute from the record, so the honest thing is to
name the direction and the gap in the evidence rather than leave both in a JSON
file.**

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
* ⚠ **The mechanism behind §8a — R3 measuring dearer than R2 — was not
  investigated.** The direction is measured in two conventions; the cause is not.
  It is the one place this pattern leaves a number in the record without an
  account of it.
* **`controls/harm_sites.py` runs ASan at `-O1` only**, inherited from the
  demonstration it grew out of.

---

## 10. SLB-TRUSTED-ARGUMENT sections

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
