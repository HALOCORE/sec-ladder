# TASK_146 — build `p28`: two intrusive link sets, incomplete destroy. Report

**Role: research engineer.** Built `patterns/p28-intrusive-lists/` — seven rungs,
`spec.md` with the machine-readable pins, `model.py`, `inputs/gen.py`,
`NOTES.md`, `README.md` and five controls. Deliverable 0 is settled with a run
and it goes the manager's way. **Three predictions written into this tree — one
of them the manager's, two of them mine — were measured FALSE and are retracted
in the files that carried them, not quietly dropped.**

✅ **`harness/check.py p28` PASSES** — verdict `PASS`, 0 failures, 0 blocked,
0 shouts — and `measure.py` records all 32 cells `ok`. §9 carries the run.

---

## 0. ⚠⚠ DELIVERABLE 0 — the overstated sentence, SETTLED, and the manager is right

`TASK_143_REPORT` §2.2 and `.memory/06-catalogue.md`'s `p28` cell say the row's
reproducibility makes it *"GATABLE against `model.py` on its adversarial inputs
where `p27` and `p29` are NOT"*. **That is false.**

Source, `harness/check.py`:

```
631 def inputs_of(pdir, skip=()):
639     good = [n for n in names if not n.startswith("adversarial")]
640     adv  = [n for n in names if     n.startswith("adversarial")]
...
8717 good_models = build_models(modmod, indir, good, rep)
8718 adv_models  = build_models(modmod, indir, adv,  rep)
8723 check_checksums(built, rep, good_models, indir)      <- STAGE 2: `good` ONLY
8729 advtable = check_adversarial(built, rep, adv_models, indir, cells, budgets)
```

`check_adversarial`'s docstring says it in terms (*"behaviour recorded, not
required to agree"*), it computes `diverges` into each row, and the **only**
`rep.fail` in the whole function concerns a declared `expected_hang`.

**The run** — over the three built temporal rows' committed gate records, which is
the strongest available form because these are patterns the project has already
certified:

```
p29-bst-delete      verdict=PASS  failures=0   58 adversarial rows   26 diverges:true
p32-free-list-pool  verdict=PASS  failures=0   48 adversarial rows   10 diverges:true
p27-handle-table    verdict=PASS  failures=0   44 adversarial rows   18 diverges:true
```

**54 recorded adversarial rows disagree with `model.py` inside three PASSING
verdicts.** No pattern gates an adversarial cell against `model.py`, and no
amount of reproducibility could change that.

⚠ **One correction to the manager's own note, and it is the useful half.** The
note says stage 4 records and stage 2 excludes, and stops there. **There IS one
adversarial obligation the gate enforces: `sanitizer_expect`.**
`check_sanitizers(pdir, rep, indir, all_models, budgets)` takes `all_models`, so
an adversarial input declaring `"fires"` FAILS the gate if the sanitiser stays
silent. That is the row's one gated adversarial fact, and it is about the
DETECTOR rather than the checksum.

✅ **What reproducibility does buy is the manager's narrower sentence, and p28
turns out to have it in a stronger form than the note claimed.**
`controls/repro.py` runs every (compiler × opt) cell rather than one:

```
adversarial-uaf-read.bin   c-gcc/O0=1 c-gcc/O3=1 c-clang/O0=1 c-clang/O3=1   ONE behaviour across all four
adversarial-uaf-head.bin   1 1 1 1                                            ONE behaviour across all four
adversarial-uaf-write.bin  1 1 1 1                      ONE behaviour (a stable CRASH, not a value)
adversarial-many.bin       1 1 1 1                                            ONE behaviour across all four
NEGATIVE CONTROL  arm_aslr.c  20/20 distinct  randomize_va_space=2  FIRED
```

So the pinnable figure is ONE number per input, not one per cell — `p29`'s own
gate record shows `adversarial-many.bin/c-clang` at `13261590098807716864` (O3)
and `13757854543850195968` (O0). **`p28` is the first temporal row whose
adversarial evidence carries a figure**, and `controls/repro.json` is where it
lives.

**Suggested catalogue wording** (the manager applies): strike the `~~gatable~~`
clause, keep the reproducibility, and replace the consequence with *"so its
recorded adversarial row is a PINNABLE FIGURE — one value per input across all
four (compiler × opt) cells, which `p29` and `p27` cannot have. It is not
gatable; no adversarial cell is, in any pattern (`TASK_146` §0). The one
adversarial fact the gate does enforce is `sanitizer_expect`."*

---

## 1. ⚠⚠⚠ BLOCKER IN `.temp/mgr146/p28d` — THE SPELLING THE TASK FILE ORDERS IS AN INCORRECT PROGRAM

The task file says, in bold: *"BUILD `p28d`, NOT `p28` — measured, not argued"*,
on the strength of `+9 / −0` at **a shared cost of zero** (both R1 bodies
preprocessing to 127 lines) and *"bit-identical checksums, all four inputs ×
both arms"*.

**`.temp/mgr146/p28d/body.inc` never initialises `hp`.** `grep -n hp` gives six
hits, all READS (DEL ×3, TRIM ×3), and not one write on the PUT path. The chain's
back pointer is whatever `malloc` returned.

Measured (`.temp/t146/cdemo/repro28d.sh`, ASan, `env -u LD_PRELOAD`; the manager's
own `build.sh` and `common/`, copied unmodified):

```
p28d bug  benign-noTrim   rc=1  asan=4  SEGV on unknown   <- a BENIGN input
p28d fix  benign-noTrim   rc=1  asan=4  SEGV on unknown   <- BENIGN, HARDENED arm
p28d fix  benign-trim     rc=1  asan=4  SEGV on unknown
p28d fix  adv-uaf-read    rc=1  asan=4  SEGV at p28d/body.inc:164
```

Line 164 is `victim->hp->hn = victim->hn;` **inside the safety line**, through an
uninitialised pointer. The plain build survives only because a fresh `brk` page
reads as zero, so `hp` happens to be `NULL` and the `else` branch runs; ASan's
poison pattern is non-zero and it dies. **As delivered, `p28d` fails admission
question 1 — *correct on benign inputs* — in BOTH arms.**

⚠ **Why the re-verification could not see it**, which is the reusable part:
`.temp/mgr146/repro.sh` runs ASan on the `ctl` and `bug` arms and **never on
`fix`**. The hardened arm is the one admission question 1 is about, and it was
the only arm not put under the detector. The plain build was silently lucky.

**Corrected** (`.temp/t146/cdemo/p28dfix/` = `p28d` + three preprocessed lines in
PUT: `n->hp = NULL;` and the two that give the old chain head its `hp`):

| | `p28` singly | `p28d` as delivered | corrected |
|---|---|---|---|
| safety line, preprocessed | **+15 / −0** | +9 / −0 | **+9 / −0** |
| R1 body, preprocessed (`ppcount.sh`) | **127** | 127 | **130** |
| correct on benign input | yes | **NO** | yes |
| four inputs × both arms | — | — | **bit-identical to `p28`'s** |
| 20-run reproducibility | 1 every row | 1 every row | 1 every row |
| ASan `ctl`/`bug`-read/`bug`-write/`fix` | fires/fires/fires/silent | fires/fires/fires/**SEGV** | fires/fires/fires/silent |

**So *"a 40% shorter safety line, FREE"* is `9 against 15 at +3 SHARED LINES`.**
The conclusion survives — the doubly linked spelling is still the one to build,
and this row ships it — and the arithmetic does not. `NOTES.md` 1b carries the
table.

---

## 2. What was built

```
patterns/p28-intrusive-lists/
  c/kernel.h  c/kernel.c  c/kernel_hardened.c  c/main.c
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  model.py  inputs/gen.py  spec.md  NOTES.md  README.md
  controls/ safety_line.py   arm_body.inc arm_sites.c harm_sites.py
            repro.py arm_aslr.c
            proof_mutants.py
            rust_arms.py arm_rawptr.rs arm_safe_bug.rs
```

Constants `NB=8`, `SLOTS=48`, `NIL=255`, `SENT=251`. ⚠ An earlier draft also
carried `CAP=12` (a live capacity) and `STEPS=16` (a separate walk fuel); **both
were dropped for a PROOF reason, not a design one** — `nlive -= 1` needs a
counting invariant `st.nlive == #{j : lv[j]}` before it can be shown not to
underflow, which is three inductive `Seq` lemmas, and the loop body is what the
solver's rlimit is paid on. TRIM is an explicit opcode, so eviction never needed
a capacity to be reachable. `SLOTS` is now the allocation budget *and* the walk
fuel, and the argument is one line: a chain holds only live objects and at most
`SLOTS` are ever made.

**Rung agreement**, `O0/isolated`, all eight inputs: `c-gcc-h`, `safe_naive`,
`safe_tuned`, `unsafe`, `verus` all equal `model.py`'s `expected`. `c-gcc` (R1)
agrees on `small`, `large`, `degenerate`, `adversarial-stride3` and diverges on
the other four, with `adversarial-uaf-write` SIGSEGVing (rc 139).

**Safety line**: `controls/safety_line.py` measures a pure `+9 / −0` on the
shipped C rungs, every added line inside the splice.

⚠ **The include-twice construction is KEPT, in `controls/arm_body.inc`**, which
is where p32 keeps it and where it can be: a kernel body inside an `.inc` would
be outside `check.py`'s `forbidden` text audit, so the two shipped rungs are
written out in full and `safety_line.py` makes the claim by preprocessing
instead — which is strictly stronger, because the include-twice version cannot
fail.

---

## 3. `model.py` — the two failure modes, answered before the gate

**Transliteration.** The simulation that produces the model's answer,
`_sim_checked`, is a **`dict` from key to object plus an insertion-ordered
`list`**. It has **no links of any kind, in either direction, in either list**,
no buckets and no walk. Every rung records membership in fields inside the
objects; the model records it in two containers outside them. That is the
row's own axis, which is what the task file asked for. The second
implementation, `cache_fold`, mirrors the Verus `run` — object sequence,
liveness sequence, bucket array, both list ends, links, walk and fuel — and
`selfcheck()` runs them against each other. ⚠ The pair carries one fact neither
carries alone: **the walk fuel never truncates**, because the dict simulation
cannot truncate and a truncation would show up as a disagreement.

**⚠⚠ Tautology-of-the-representation — decided EARLY and written down, as asked.**
The answer is in `model.py`'s module docstring under a heading that says so:
**yes, the stale link is representable, with one named limit.** It is not
representable in the dict simulation, so the detector is a THIRD function,
`_sim_buggy`, which is never consulted for an answer: it carries per-bucket
**membership lists** and a `released` flag, and the buggy TRIM frees the victim
and leaves it in the list.

* **Faithful**: that the victim is still reachable by a walk of its bucket, in
  the same position, after the same number of steps; that reading it is a
  use-after-free; that a DEL of a neighbour writes into it.
* **Collapsed, and stated**: the membership list cannot tell *the dangling
  pointer is in `bucket[b]`* from *it is in a live predecessor's `hn`*. **That
  distinction is the row's own claim, so it is measured OUTSIDE the model**, at
  C level, by `controls/harm_sites.py`.

**The derivation fires on SHIPPED inputs** — `clean` on `small`, `large`,
`degenerate` (all of which TRIM, repeatedly) and `fires` on all four adversarial
files — which is evidence `p32`'s repaired arm does not have.
`detector_selftest()` adds four planted cells (two probes × {line kept, line
deleted}) and `selfcheck()` runs it on every gate invocation.

### 3a. ⚠⚠ The must-fire arm owes the same test, and the FIRST DRAFT FAILED IT

`.memory/03-measurement.md` 19's closing paragraph asks for exactly this, so
`.temp/t146/mustfire_probe.py` plants five mutations into a COPY of `model.py`
and records TWO columns: was it CAUGHT, and was it caught by a RETURNED message
or by an exception escaping.

```
M0-control               problems=False returned          OK
M1-touch-neutered        problems=True  returned          OK   MUST-FIRE ARM DEAD
M2-touch-always-fires    problems=True  returned          OK   FIRED with the line PRESENT
M3-safety-line-inert     problems=True  returned          OK   FIRED with the line PRESENT
M4-detector-raises-wrong problems=True  returned          OK   MUST-FIRE ARM BROKEN ... KeyError
```

⚠ **M4 originally read `RAISED KeyError  XX`.** A detector raising an exception
type the caller does not catch escaped `Model.__init__` — through `_run` →
`_window` → `_sim_buggy`, before `selfcheck()` was ever reached — so the gate
would have seen a crash instead of a sentence. **That is `p32`'s exact failure
mode one file over, and the manager's brief predicted it by name.** The repair is
`Model.detector_error`: `_window` catches ANY exception out of `_sim_buggy`, not
just `_Escape`, records it, and `selfcheck()` turns it into a named problem. The
window's answer comes from `_sim_checked` and does not depend on the detector, so
the model keeps working and says what broke.

---

## 4. The R5 attack and vacuity arms — seven, all as declared

`controls/proof_mutants.py`, `--rlimit 400`, every verdict declared in advance:

```
A0-control             control     expect=verify got=verify OK  23/0
A1-exec-safety-line    attack      expect=fail   got=fail   OK  22/1  assertion failed
A2-constant-body       vacuity     expect=fail   got=fail   OK  20/1  postcondition not satisfied
A3-spec-only-weaken    attack      expect=fail   got=fail   OK  22/1  assertion failed
A4-spec-weaken         must-verify expect=verify got=verify OK  23/0
A5-walk-liveness       attack      expect=fail   got=fail   OK  22/1  assertion failed
A6-epilogue-dead       must-verify expect=verify got=verify OK  23/0
7 of 7 behaved as expected
```

**The three-cell experiment** — A1 exec-only FAIL, A3 spec-only FAIL, A4 both
VERIFY — says the safety line is load-bearing **against the SPECIFICATION and
against nothing else**. And the two failing diagnostics name **different
obligations**, which is what stops that from being a reading of one error string:

```
A1  assert(st == step(st_in, c, a).0)   <- the REFINEMENT assertion
A5  assert(alive(st, cur))              <- the MEMORY-SAFETY licence, inside walk
```

⚠⚠ **That is `p32`'s shape and it is SHARPER here.** `p32` has no linear resource
at all — nothing is ever allocated — so of course nothing linear forced its
conjunct. **p28 HAS them**: `rec_close` consumes the victim's `PointsTo` and its
`Dealloc`, a real temporal guarantee. They still do not reach this omission,
**because the linear argument only ever bites at a READ and what `c/kernel.c`
forgets is a LINK.** Leaving a slot number in a chain consumes nothing.

⚠ **The task file offered `TASK_091`'s ready-made attack arm — delete the ADDRESS
INJECTIVITY conjunct and `fake3` passes — and it does not exist in this rung.**
Injectivity is a property of an address-keyed permission map, and this R5 is
slot-keyed (§5). The arms above are the analogue that does exist, and A5 is the
one that plays `fake3`'s role: it is the arm whose deletion makes a memory-safety
licence unprovable rather than a postcondition false.

### 4a. ⚠ A6 was predicted to FAIL and VERIFIES — retracted, not dropped

`A6-epilogue-dead` makes the epilogue's `live[j] == 1` test unreachable, so every
surviving object leaks. It verifies, `23/0`. The reason is already in
`.memory/04-verus.md`: **`Tracked<Dealloc>` is AFFINE, not linear** — dropping a
token is legal, so a proof built on it shows deallocation is LEGAL (no double
free, no use after free) and never that it HAPPENS. `TASK_104` measured that on
`p42` with a committed must-fail control; **this is the fourth pattern to show it
and the first whose C rungs really do free everything.**

The sentence *"this is the half the linear resources DO force"* stood in
`verus.rs`'s `SAFETY (6)` and in this battery's own `why` text before the arm was
run. **Both are struck in the files that carried them.**

---

## 5. ⚠⚠ THE ONE DISCLOSED DIVERGENCE FROM THE C MECHANISM

The C rungs store the four links as `struct p28_obj *`. **Every Rust rung stores
them as `u8` slot numbers into a table**, `unsafe.rs` and `verus.rs` included.
Safe Rust has no choice — an object on two intrusive lists is an object with two
owners — and `unsafe.rs` follows it so R4/R5 stay byte-comparable and so the
proof can rest on a per-slot invariant rather than the full doubly-linked-list
well-formedness (`hn[hp[j]] == j` and its three siblings) an address-keyed map
needs. **`TASK_091` proved `wf` for ONE list; p28 has two and the bug is in their
interaction. That gap is reported as a result, and it is the honest answer to
`TASK_091`'s own open question.**

**Measured rather than argued** (`controls/rust_arms.json`):

* `controls/arm_rawptr.rs` is the FAITHFUL raw-pointer port of both C arms, from
  ONE macro expansion (the Rust spelling of the include-twice construction). Its
  FIX arm equals `c/kernel_hardened.c` on every input at both optimisation
  levels, and its BUG arm equals `c/kernel.c` on the benign ones. **So the
  slot-table representation changed the PROOF BURDEN and not the PROGRAM.**
* **Miri reports `Undefined Behavior: in-bounds pointer arithmetic failed` on the
  raw-pointer BUG arm on all four adversarial inputs and on NOTHING ELSE** — not
  on its fix arm, not on the benign inputs, not on either safe arm. A detector
  that fires on everything is not a detector, so both halves are asserted.

**Cost in exec text**: one `live[cur] == 1u8` conjunct in the walk plus **ten
`alive_link` sites**. Not one can fire. ⚠⚠ **`p29` could put its liveness
conjuncts in its C rungs too, and p28 CANNOT — because p28's C links are pointers
and neither C rung contains a slot number or a `live[]` bit. The property that
makes the row distinct at C level is the property that makes that conjunct
unspellable there.**

---

## 6. ⚠⚠⚠ SAFE RUST'S ANSWER, AND IT IS NOT WHAT ANY DRAFT PREDICTED

`controls/arm_safe_bug.rs` is `safe_tuned.rs` minus the safety line, in both
idiomatic safe spellings, under `#![forbid(unsafe_code)]`. Three separate drafts
in this tree — `safe_naive.rs`'s header, that file's header and
`controls/rust_arms.py`'s docstring — predicted **"a WRONG ANSWER"**.

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
chain tail, and the entries the buggy rung leaves behind form a **SUFFIX**. A walk
that stops at the first `None` slot loses only objects that are already gone. GET
and DEL are right for a structural reason rather than by luck. (⚠ An argument
plus a measurement over the shipped inputs, not a proof; a cache whose eviction
order and chain order disagreed would not have it.) The one path that notices is
PUT, which writes the old chain head's `hp` *without walking to it*.

⚠⚠ **This is a STRONGER outcome than `p32`'s and it points the other way.**
`p32`'s headline is that safe Rust reproduces its buggy C **bit for bit** — the
type system is SILENT. **p28's is that safe Rust cannot reproduce its buggy C at
all**: the representation safe Rust forces on you removes the harm's mechanism
along with the pointers. Both are outcome-3 results in `.memory/01-ladder.md`'s
sense and they are the two opposite ways that happens.

⚠ **And it makes the catalogue's reusable reason false of this spelling.** The
cell carries `TASK_093`'s *"p28's two safe spellings that free per node both catch
the bug by `p27`'s runtime mechanism … the index arena NEVER FREES"*. The shipped
spelling is a third one: `[Option<Box<Obj>>; SLOTS]` **frees per object**, one
`Box::new` per object and one drop per DEL and per TRIM. What the slot table
costs is not freeing, it is that slots are never recycled.

---

## 7. Deliverable 4 — the cost axis, and it is ABSENT ON PURPOSE

**This pattern publishes NO rung-to-rung cost of any kind**, and the absence is
stated in `spec.md`'s `why`, in `NOTES.md` 8 and in every rung header, so it
cannot read as a zero. `p29` ships the same way. Three independent confounds, any
one of which would be enough:

1. **allocation size** — a C object is four pointers plus two bytes (40 B); a
   Rust object is 6 B. Same number of allocator calls, different sizes.
2. **epilogue shape**, three different loops (C walks the eviction list, R4/R5
   scan the slot table, R2/R3 drop the table).
3. **the ten non-firing `alive_link` sites and the walk's liveness conjunct**,
   present in R4/R5 and unspellable in C.

And the two measured warnings from this row's own history, which is why the
absence is deliberate rather than lazy: `TASK_093_REVIEW`'s *"safe Rust is 6.02×
CHEAPER than unsafe"* with **108.4% of the gap IN THE ALLOCATOR** and the bounds
check at **3.0% of the magnitude and the OPPOSITE SIGN**; and `TASK_091`'s **4.0
of a 12.5 R3→R4 gap is INDEX SCALING**, not checking.

**I searched BOTH sides before deciding not to publish**, which is what the
deliverable asks: the R3 side has the two spellings `safe_naive`/`safe_tuned`
differ by (one borrow per object rather than per field, and one splice read
rather than eight), and the R4 side has the whole-struct RMW that `TASK_091`
measured free, the `arr_get_unchecked` question inherited from p27, and the
`alive_link` sites. Neither side is under-searched relative to the other; both
are swamped by confound 1.

---

## 8. Verus: what it cost, and ⚠⚠ THE BINDING CONSTRAINT WAS NOT THE SHIPPED CONFIG

**Shipped: `23 verified, 0 errors` in 36.8 s; twin configuration `--cfg
slb_twin`: `28 verified, 0 errors` in 33.1 s.** Obligation arithmetic in
`spec.md`'s `obligations_note`, measured per function
(`.temp/t146/obligations.log`) and — per `.memory/03-measurement.md` 17 — **per
non-function term too** (`.temp/t146/obl_probe.log`): a bare `const` moves the
count by 1, a **BARE** `#[repr(C)]` struct by 0, a `#[derive(Clone, Copy)]`
struct by 1. `global layout` carries ZERO; the arithmetic sums to 23 exactly
without it.

⚠⚠ **The thing that nearly stopped this rung shipping was `--cfg slb_twin`, not
the shipped file.** `check.py`'s twin stage runs the whole file with five extra
verified functions in scope — and, through `slb_twin_rec_alloc`/`_rec_free`,
vstd's `PointsToRaw`/`Dealloc` axioms — which made the KERNEL's own query
diverge. Three levers, measured:

| lever | shipped | `--cfg slb_twin` |
|---|---|---|
| baseline (six parallel `Seq<u8>` in `St`, ghost-guarded quantifiers) | rlimit exceeded | — |
| ONE `Seq<Obj>` + quantifiers guarded by the EXEC `live[]` array | floor between 100 and 120 | ⚠ **rlimit exceeded at 400 AND at 2000** — the 2000 run was killed at **9 m 43 s**, already past `check.py`'s 900 s per-run timeout, so no budget would have rescued it |
| ⚠ `#[verifier::spinoff_prover]` on `kernel` | ⚠ **WORSE**: `22 verified, 1 errors` at 400 where the same file without it verifies | not reached |
| ✅ `put_new`/`del_at`/`trim`/`step` `#[verifier::opaque]`, revealed in the ONE proof block that needs them | floor 70 fails / 80 verifies | ✅ floor 60 fails / 70 verifies |

```
rlimit    shipped              --cfg slb_twin
   60     22 verified, 1 err   27 verified, 1 err
   70     22 verified, 1 err   28 verified, 0 err
   80     23 verified, 0 err   28 verified, 0 err
  100     23 verified, 0 err   28 verified, 0 err
  150     23 verified, 0 err   28 verified, 0 err
  400     23 verified, 0 err   28 verified, 0 err   <- shipped, 36.8 s / 33.1 s
```

**`#[verifier::rlimit(400)]` on `kernel` is a 5× margin over a floor measured in
BOTH configurations.** It is a solver budget, not a soundness knob — every
obligation is still discharged, and the seven mutant arms are the check on that.
It is a SOURCE-LEVEL attribute, so the gate's flagless invocation honours it.

⚠ **Two of the three levers went the wrong way, and one of them contradicts a
measured result already in the tree.** `p09`'s NOTES.md 5c scopes
`lemma_u128_shr_is_div` and `lemma_mul_inequality` into the driver's loop body
because at file scope they push the kernel's query past the rlimit. **On p28,
scoping them makes the kernel's query WORSE** — the pre-opaque floor went from
"between 100 and 120" to "above 120". They stay at file scope and the
`broadcast use` block says so. And `spinoff_prover`, which is the obvious thing
to reach for, is a regression here.

⚠ **A fragility worth knowing, measured on the PRE-OPAQUE file**: the margin
moves with the CRATE NAME. A copy under a different FILE name (`ob_base.rs`)
failed at `rlimit 200` where `verus.rs` passed. `check.py`'s mutant machinery
keeps the file name and changes only the directory, and a copy under the mirrored
path verifies (checked explicitly).

⚠ **What I did NOT do, and it is the structurally correct fix**: split the loop
body into four per-opcode `#[inline(always)]` functions, or move the repeated
invariant re-establishment into a `proof fn` lemma called at each of the ten
splice sites. Either would give each arm its own query instead of one query for
the whole body. Both were identified, neither was built; the opaque change made
them unnecessary for THIS file and they are what the next person should reach for
if it grows.

### 8a. The identity pin found a real drift before it was ever pinned

`identity` is `O0: differ`, `O3: norel` — `p29`'s pin for `p29`'s reason. ⚠⚠ With
`nmade = nmade + 1` sitting at the END of the PUT-alloc block in `unsafe.rs` and
in the MIDDLE of it in `verus.rs`, the pair measured `differ` at BOTH levels —
355 vs 356 instructions, a different register allocation and one extra `movq`.
Moving that one statement made `-O3` `norel` immediately. **Nothing else in this
tree would have found it.**

---

## 9. Gate and measurement

### 9a. What the gate caught that nothing else would have — THREE things

`harness/check.py p28` was run three times. The first two FAILED, and both
failures are worth reporting because neither is a defect a local check of mine
could have found.

**Run 1 — `FAIL [idiom-named-spelling]`.** `idiom.why` must END with a
tree-wide, **byte-identical 11003-byte** paragraph (`sha256 59748cce2db5…`) that
defines what a backticked pin means. **I had written my own abridged version.**
It reads correct; only a byte comparison against the rest of the tree can see
that it is not the same prose. Fixed by copying it verbatim from `p32`'s
`idiom.why` (checked byte-identical against `p29`'s too). ⚠ **This is exactly the
self-certification the mechanism exists to prevent** — an abridged definition of
what a pin means is a pattern deciding for itself what its own pins mean.

**Run 2 — 7 failures, all mechanical, and one of them structural:**

| | what |
|---|---|
| 1 × `[twin]` | ⚠ **`slb_twin_rec_alloc`'s signature is not the trusted item's.** I had wrapped its return type across four lines; normalised, that is `( *mut u8, …, )` against `(*mut u8, …)`. The gate's own message says why it refuses: *"a twin with its own contract is a second declaration, not a check"*. One-line fix; `--cfg slb_twin` still `28 verified, 0 errors`. |
| 5 × `[twin]` | `NOTES.md` carried no `SLB-TRUSTED-ARGUMENT verus.rs <item>` section for the five twin-regime items. **Written, all seven** (the two I/O items too, which the gate does not demand), in `NOTES.md` 10 — including the three things the gate says only a human can judge, and including the `arr_get_unchecked` case p28 makes new: it is instantiated at **three** element types where p27 and p29 use two, and one of them is `*mut Obj`, where "the value read is a raw pointer and reading a raw pointer is not a dereference" has to be said out loud. |
| 1 × `[tables]` | `results/tables/p28-*.md` does not exist. **Expected on a brand-new pattern** and the gate says the fix in terms: `measure.py` → `report.py` → gate again. |

**Everything else in run 2 was green**, including every stage that carries a
result: stage 2 (checksum agreement, **32 of 32 cells** on every benign input),
3a/3b (anti-collapse), 4 (adversarial behaviour recorded — R1 diverges on all
four adversarial inputs and every other rung matches `model.py`), 5a (the Verus
contract matches the pin), 5b (the call site is a verified call site), 5c
(clause deletion), 5c-req (requires strength), 5d0 (the Python contract is
DERIVED from `verus.rs` and identical to the declared copy), 5d (`requires` holds
on all 200 000 kernel calls of every input, `ensures` re-derived on 128 sampled
calls each), 6 (identity), 7 (sanitisers), 8 (Miri), 9a/9b (sidecar pins).

Two `!!` shouts, both expected and both carrying their justification:
`[collapse-ir]` (the derived floor is 186× below the tightest measured cell — a
smoke test, which `model.py`'s `work_per_call` docstring says) and
`[tcb-unsafe]` on `arr_set_unchecked`'s unconstrained `x`, which is
`.memory/04-verus.md`'s documented parameter-coverage false positive and which
`spec.md`'s `unsafe_justifications` answers — **p28 is the eighth pattern to
exercise it**.

### 9b. ✅ GREEN

```
harness/check.py p28   ->  check.py: PASS
results/gate/p28-intrusive-lists.json
    verdict  PASS      failures 0      blocked 0      shouts 0
    contract_sha256    5c92154096baea5de8f8fd4c24a16c6d285000687bd6006782837db00d724455
    adversarial rows   40, of which 8 diverge (R1 at both compilers, four inputs)

harness/measure.py p28 ->  wrote results/p28-intrusive-lists.json, 32 cells, all `ok`
harness/report.py  p28 ->  wrote results/tables/p28-intrusive-lists.md

harness/measure.py --check-stale        58 record(s) examined, 0 STALE
harness/tools/temp_citations.py         OK (new=0 unclassified=0 resolved=0)
harness/tools/composition.py --check    FAIL: built but unclassified: ['p28']   <- EXPECTED, §10
```

⚠ **A fourth gate run was needed and it is disclosed rather than folded in.**
`NOTES.md` is inside the gate record's `source_sha256`, and after the record was
written the measurement turned up a number that needed recording (§9c), so the
gate was run once more over the edited file. Nothing else changed.

### 9c. ⚠ The measurement contains one number the rung NAMES would mislead about

```
O3 / isolated        kernel-exclusive Ir          whole-program marginal Ir/call
                     small        large           small     large
safe_naive (R2)      386,910,519  211,267,507     3406.22   16764.91
safe_tuned (R3)      436,272,774  236,511,509     3652.26   18024.41
```

**The rung named "tuned" is DEARER than the naive one**, in both conventions and
on both inputs (+12.8%/+12.0% kernel-exclusive, +7.2%/+7.5% marginal — the two
agree on direction and differ on magnitude, which is what the published table's
own caveat says to check for).

**Nothing rests on it** — the pattern publishes no rung-to-rung cost and
`safe_tuned.rs`'s header says its levers are *"not priced"*. But *"tuned"* is a
name a reader reads as a direction, and the record is public, so `NOTES.md` 8a
now states the direction. ⚠⚠ **The MECHANISM was not investigated and that is
listed as an open item, not resolved.** R3 reads `hn` on every walk step where R2
reads it only when it advances, and R3 hoists the walk out of the opcode
dispatch; which of those (or neither) accounts for the gap has not been measured.
**A figure this pattern does not publish is still a figure a reader can compute
from the record**, so naming the direction and the gap beats leaving both in a
JSON file.

⚠ **R4 and R5 have IDENTICAL kernel-exclusive `Ir`** (299,017,209 / 185,227,142),
which is the independent confirmation of the `O3 norel` identity pin.

---

## 10. Deliverable 5 — the bug class for `harness/tools/composition.py`

⚠ **Proposed, not applied — the file is the manager's.** `--check` currently
fails with `built but unclassified: ['p28']`, which is the check working.

**Category: `temporal`**, i.e. `CLASSES["temporal"]` becomes
`["p27", "p28", "p29", "p32"]`.

⚠⚠ **And it owes a CAVEAT, for two reasons, the first of which is about the
table's own stated test rather than about p28.**

1. **The table says it counts SAFETY LINES — *"the one conjunct `c/kernel.c`
   omits"*** — and asks *"what does the safety line ASK?"*. **p28's safety line
   asks nothing.** It is not a conjunct and not a test: it is a nine-line SPLICE,
   a WRITE on the destroy path that maintains an invariant. The classification
   therefore rests on the HARM — a real `free()` followed by a read or a write
   through a link that names the freed object, which ASan reports as
   `heap-use-after-free` on both compilers and Miri reports as UB on the faithful
   raw-pointer port. **p28 is the first row in the table whose safety line is a
   maintaining write rather than a guard, and the taxonomy's test does not reach
   it.**
2. **The harm has an ALIASING limb, and it is the MIRROR of `p32`'s.** `p32`'s
   caveat says the aliasing is the HARM and the stale generation is the BUG. For
   p28 it is the other way round: **the aliasing is the SETUP** — one object is a
   member of two lists at once, which is p08's class — and **the use-after-free is
   the HARM**. Without the aliasing the omission is not possible; without the
   `free` it is not a memory error.

**Suggested `CAVEATS["p28"]`** (wording to take or amend):

> the safety line is not a TEST, it is a nine-line SPLICE — a WRITE on the
> DESTROY path that maintains *membership implies ownership* across two intrusive
> lists. So the table's stated test (*what does the safety line ask?*) does not
> apply, and `temporal` is read off the HARM instead: a real `free()` followed by
> a read or a write through a link naming the freed object, ASan
> `heap-use-after-free` on both compilers, Miri UB on the faithful raw-pointer
> port. ⚠ The harm has an ALIASING limb and it is `p32`'s caveat MIRRORED: here
> the aliasing (one object on two lists) is the SETUP that makes the omission
> possible and the use-after-free is the HARM, where in `p32` the aliasing IS the
> harm. ⚠⚠ And the row is the tree's first inversion: `p27`, `p29` and `p32` all
> keep a correct free discipline and put the missing check on the READ; p28's
> read path is correct and its DESTROY path is incomplete.

---

## 11. Problems, and what I did NOT do

* **No address-keyed R4/R5.** §5. The faithful raw-pointer port exists as a
  control and is not a rung; `TASK_091`'s doubly-linked-list well-formedness for
  two lists was not attempted, and that is the row's largest open item.
* **No cost measurement of any kind between rungs.** §7 says why, in the file.
* **The sweep bands were not run.** `inputs/gen.py --sweep` emits three
  (operations, key space, TRIM fraction) and nothing has been measured over them.
* **`arm_safe_bug`'s two spellings are two, not an enumeration.** An `Rc`/`Weak`
  port and a `HashMap`-plus-arena port are both plausible and neither was built;
  `TASK_093`'s `bwd=32127` is inherited, not re-derived.
* **`controls/harm_sites.py` runs ASan at `-O1` only**, inherited from the
  demonstration it grew out of.
* **The `O0d` (debug-assertions on) column was not examined.**
* ⚠ **`spec.md`'s `contract_sha256` moved TWICE during authoring**, both times
  before any measurement, and all three hashes with what moved are in
  `.temp/t146/NOTES.md` §3:
  `5a9dcb52…` as first written → `8fb2708c…` → `5c921540…` as shipped.
  **Move 1** was two edits inside `required[0]`, both NARROWING — a backticked
  `+9 / -0` that pinned nothing, and a `rust` text that named `safe_tuned.rs`'s
  spelling for `safe_naive.rs`; `required_pins_nothing` went 1 → 0.
  **Move 2 was demanded by the gate**, and it is the more interesting one:
  `FAIL [idiom-named-spelling] idiom.why does NOT carry the shared
  named-spelling paragraph (11003 bytes, sha256 59748cce2db5…)`. **I had written
  my own abridged version of a paragraph that is a TREE-WIDE byte-identical
  invariant** and that defines what a backticked pin means. Replaced verbatim
  from `p32`'s `idiom.why` (checked byte-identical against `p29`'s too); nothing
  p28-specific was removed. ⚠ **That is what a gate is for**: the abridgement
  reads correct, and only a byte comparison against the rest of the tree can see
  that it is not the same prose. `.temp/t146/gate-attempt1.log` is the failing
  run and `.temp/t146/shared_why.txt` the extracted block.
  ⚠ `git show HEAD:…/spec.md | diff -` **cannot fire on a new pattern**
  (PROTOCOL rule 6's own note), so the recorded triple is the only evidence and
  `harness/tools/contract_diff.py` has nothing to compare against until this
  lands in a commit.
* ⚠ **The `A3-spec-only-weaken` mutant arm takes ~25 min on its own** because it
  fails for a real reason (`assertion failed`) AND then exhausts the whole
  `--rlimit 400` on a second query, so `controls/proof_mutants.py` is a ~40 min
  control. `README.md` says so. Not fixed; a per-arm rlimit would fix it and
  would cost the informative diagnostics `.memory/03-measurement.md` 18's
  precedent warns about.
* ⚠ **Scratch under `.temp/t146/` has been cleaned per constraint 6** — every
  binary, `.o` and mutant tree deleted, every `.py`/`.sh`/`.rs`/`.c` probe
  source, `.log` and `.json` kept, and `.temp/t146/cleanup.sh` names the command
  that rebuilds each deleted thing. `temp_citations.py` is `OK` afterwards.
* ⚠ **I did not re-derive `TASK_091`'s probe-2/probe-3 `Ir` figures.** They are
  quoted where they bear on a design decision (the whole-struct RMW being free,
  index scaling being 4.0 of 12.5) and are marked as inherited.

---

## 12. Memory updates owed (the manager applies, after review)

1. ⚠⚠ **`.memory/06-catalogue.md`'s `p28` cell**: strike the `~~gatable~~`
   clause per §0, and strike the reusable reason *"the index arena never frees"*
   as false of the shipped spelling per §6.
2. **`.memory/03-measurement.md`**: the must-fire arm's own must-fire test now
   has a worked example that passes on all five arms **with a RETURNED
   diagnostic**, which is what entry 19's closing paragraph asked for and could
   not point at.
3. **`.memory/04-verus.md`**: three items.
   (a) the affine-token family gains a fourth member (§4a), and it is the first
   on a kernel whose C rungs really do free everything;
   (b) ⚠ **`--cfg slb_twin` can be the BINDING rlimit constraint** — on p28 the
   twin configuration diverged where the shipped one verified, and no budget
   would have rescued it (9 m 43 s at rlimit 2000, past `check.py`'s 900 s
   per-run timeout). **A pattern whose shipped file verifies is not a pattern
   whose gate passes**, and the twin config is where that bites;
   (c) two rlimit levers with measured directions: **`#[verifier::opaque]` on
   spec fns needed by exactly one obligation, revealed there, is the big win**
   (it is what made p28 verifiable at all), while **`#[verifier::spinoff_prover]`
   on the kernel is a REGRESSION here** and **`p09`'s broadcast-scoping lever
   reverses** (§8).
4. **`.memory/01-ladder.md`**: outcome 3 has a second, opposite shape — `p32`
   (safe Rust reproduces the buggy C bit for bit) and `p28` (safe Rust cannot
   reproduce it at all, because the representation removes the mechanism).

---

**PROTOCOL rule 2 running count: launched from 745 (`TASK_147_REPORT.md`'s
closing paragraph), carried to 756** — branch delta **+11**:

1. **The task file's central instruction was wrong**: `p28d` as delivered is an
   incorrect program that SEGVs on a benign input in its HARDENED arm, and the
   *"shared cost of ZERO"* is `+3` (§1).
2. **The re-verification's blind spot is nameable**: `repro.sh` never ran ASan on
   the `fix` arm, which is the arm admission question 1 is about.
3. **Deliverable 0 goes the manager's way, with one addition the note missed**:
   `sanitizer_expect` IS gated on adversarial inputs (§0).
4. **And the pinnable figure is stronger than the note claimed**: ONE value per
   input across all four (compiler × opt) cells, not one per cell.
5. **My own `model.py` must-fire arm failed its own test** (M4 raised instead of
   reporting) and needed `Model.detector_error` (§3a).
6. **`A6` was predicted to fail and verifies** — the affine-token family, fourth
   instance — and the prediction was struck in `verus.rs` and in the battery
   (§4a).
7. **Safe Rust's answer is not "a wrong answer"** — it is nothing, or a panic —
   and three drafts in this tree said otherwise before it was run (§6).
8. **Two rlimit levers went the wrong way and the binding constraint was the
   TWIN configuration, not the shipped one** — `p09`'s broadcast scoping reverses
   and `spinoff_prover` is a regression, while `#[verifier::opaque]` + `reveal`
   is what made the file verifiable at all (§8).
9. **`CAP` and `STEPS` were dropped for a PROOF reason**, and the row is simpler
   for it (§2).
10. **The gate caught two things no local check of mine would have** (§9a): an
    ABRIDGED copy of the tree-wide named-spelling paragraph — which is a pattern
    quietly redefining what its own pins mean — and a twin whose signature was
    not the trusted item's because I had line-wrapped its return type.
11. **The measurement contradicts a rung's NAME** (§9c): `safe_tuned` is dearer
    than `safe_naive` in both conventions. The pattern publishes no cost, so
    nothing rests on it — but the record is public and the name is not neutral,
    so `NOTES.md` 8a states the direction and lists the unmeasured mechanism as
    an open item.

⚠ **A rigour signal, not a ledger — reconciliation across branches is the
manager's job, not mine.**
