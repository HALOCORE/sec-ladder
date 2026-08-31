# p34 -- manual reference counting over a stack of heap objects

**CWE-911 (improper reference count update) reaching CWE-416 (use after free).**
Every object carries its own count in its own first word. `NEW` allocates one
with `rc = 1` and pushes it; `DUP` publishes a **second reference** to the object
on the top of the stack; `POP` releases one reference and frees at zero; the
epilogue releases whatever the window left behind. **`c/kernel.c` omits the
`rc++` that `DUP` owes**, so the object is freed while a live stack entry still
names it. `c/kernel.h` carries the kernel contract in pseudocode; this file
carries the reasoning and the machine-readable pins; `README.md` says the same
thing for a reader who has read neither.

## Why this row exists, because it is not what a reader will guess

⚠⚠⚠ **THIS ROW WAS REFUSED TWICE AND BOTH REFUSALS WERE LADDER-SIDE.**
*"There is no working leak detector for the C rungs on this box"* -- dead, and it
was never the binding constraint anyway. *"The safe rung leaks only in the
`Rc`-both-ways spelling and `Weak` is equally idiomatic"* -- about a DIFFERENT
bug class (the `Rc` CYCLE LEAK, `.memory/01-ladder.md` outcome 4, scoped to the
statically-asymmetric doubly-linked-list case). **`p34` as built is the
PREMATURE-FREE class only, and it was admitted at `TASK_143` on the C-side bar
(`CLAUDE.md` rule 6): the C program is correct on benign inputs, exhibits a
use-after-free on an adversarial one, and its C mechanism is distinct from every
built row's.** Nothing the Rust or Verus rungs do can shrink or retire it.

## The C-mechanism distinction, stated first because a reviewer will attack it first

```
p27  individually malloc'd records; the free discipline is correct and the READ
     does not ask whether the record is still live.          Fix the READ.
p29  a real free() of a whole record and a stale ADDRESS held across it; the
     READ does not revalidate the occupant.                  Fix the READ.
p32  nothing is allocated at all; a handle is not revalidated against the
     block's incarnation.                                    Fix the READ.
p34  THE READ IS CORRECT AND ASKS NOTHING WRONG.  A refcounted pointer is valid
     BY CONSTRUCTION; it is the ACQUIRE that broke the invariant, and the harm
     lands an unbounded distance away from the omission.     Fix the ACQUIRE.
```

**No check on p34's read path could repair this program without becoming a
liveness table**, because nothing on the read path is wrong. The free happens
EARLY rather than the read happening LATE -- a different C program with a
different repair site. `p32` is the furthest thing from it in the tree: `p32`
allocates nothing at all.

## ⚠⚠ The benign cost gradient is `0.00` BY CONSTRUCTION, and it is proved

`t->rc = t->rc + 1` is the **only increment in the kernel**, so in R1 every
object's `rc` is permanently `1`. Any executed `DUP` therefore leaves **two stack
entries naming a one-reference object**, and the two releases that must follow --
each entry is released exactly once, by `POP` or by the epilogue -- go `1 -> 0`
(*`free`*) and then `0 -> underflow`, **reading `o->rc` out of a freed block**.
**There is no input on which the safety line executes and R1 stays memory-safe.**

The corollary is a hard constraint on the inputs -- **no matrix input may contain
a `DUP` op** -- and it is enforced in three independent places rather than
assumed: `inputs/gen.py` cannot emit one and refuses to write a blob containing
one, `model.py::no_dup_problems` re-derives the property from the SHIPPED blob on
every gate invocation, and `controls/no_dup.py` censuses the whole directory.

⚠ **`0.00` is still MEASURED.** R1h is a different compiled function and a
never-executed statement can still move layout, register allocation and inlining.
`NOTES.md` 4 states the prediction, then reports the measured R1 - R1h delta at
both optimisation levels on both compilers.

## Two bug classes, separated by which instrument sees them

| input | what R1 touches | checksum vs R1h | ASan | UBSan |
|---|---|---|---|---|
| `adversarial-blind` | `o->rc` of a freed block, on the release path | **identical** | fires | silent |
| `adversarial-blindread` | `o->data[0]` of a freed block | **identical** | fires | silent |
| `adversarial-recycle` | `o->data[0]` of a **recycled** block | **diverges** | fires | silent |
| `adversarial-many` | all three, 36 times | diverges | fires | silent |

⚠ **The first two rows are the row's most interesting evidence and they are
exactly what a checksum-only gate misses.** The refcount header comes first and
`data` starts at offset 16, clear of glibc's tcache `next`/`key` words at user
offsets 0 and 8, so the stale read returns the *right* byte -- and the release
path folds a constant that does not depend on `rc` or on whether `free` ran.
**Layout disclosed**, the way `p28` discloses its own.

⚠ **UBSan's silence is derived, not observed-and-hoped**: R1's undefined
behaviour is entirely TEMPORAL, because every index the kernel forms is inside
`stk[]` in both rungs. A positive control licenses only the detector it fires in
(RECAP trap 5), so `controls/detectors.py` ships one control per detector.

## What each rung spells

| rung | the reference | the safety line |
|---|---|---|
| **R1** `c/kernel.c` | `struct p34_obj *` with `size_t rc` in the object | **absent** |
| **R1h** `c/kernel_hardened.c` | the same | present: `t->rc = t->rc + 1;` |
| **R2** `safe_naive.rs` | `Option<Rc<Obj>>` | **it has no site** -- `Rc::clone` publishes and counts in one operation |
| **R3** `safe_tuned.rs` | the same | the same: none |
| **R4** `unsafe.rs` | `*mut Obj` with `rc: usize` in the object | **back, and written by hand**: `obj_retain(t);` |
| **R5** `verus.rs` | the same | the same, and it is what the invariant `wf` needs |

## The R5, and the obligation that is new to this tree

A `PointsTo` is **linear** and p34's subject is **aliasing** -- two stack entries
naming one object is the normal, correct state of this kernel -- so the
permission cannot be held per stack entry the way `p27` holds one per slot. It is
keyed by OBJECT, and the proof carries the bridge:

> **`perms[k].value().rc == cnt(ids, k)`** -- the count stored in the object's
> own first word equals the NUMBER OF STACK ENTRIES naming it.

`cnt` is an occurrence count over a `Seq<int>` with five supporting lemmas, and
it is the first multiset-flavoured obligation in this project. **Leak-freedom
falls out as a corollary**: `obj_ok` requires `cnt(ids, k) > 0` for every key and
the epilogue empties the stack, so the permission map is empty when the kernel
returns. `NOTES.md` 6 states what that does and does not buy.

⚠ **The pinned vstd has no `Rc` specification and that is a RESULT.**
`~/tools/verus/vstd/std_specs/smart_ptrs.rs` is 78 lines with no `strong_count`,
no `Rc::clone`, no `into_raw`/`from_raw` and no `increment_strong_count`, so an
R5 must model the counter itself in a raw-pointer rung -- which is what the C
rung does anyway.

## The pins, and the arithmetic behind three of them

| pin | why |
|---|---|
| `verus.obligations` = 24 | **3 consts + 1 `derive` term + 20 function terms.** Every function term was measured with `--verify-function <name> --verify-root`; `.temp/t154/verus/obligations.log` is the census. The `derive` term is measured too, not inferred -- a second derived struct moves the count to 25 and a bare one does not. |
| `verus.twin_obligations` = 29 | the count under `--cfg slb_twin`. **24 shipped + 5**, one per trusted item in the twin regime. ⚠ **Every trusted item here HAS a twin and none is blocked** -- p32's and p27's position, not p35's. |
| `identity` `O0: norel`, `O3: norel` | ⚠ **weaker than p27's, p32's and p35's `exact`, and the mechanism is measured**: the two crates place `kernel` 0x20 apart and the four-way opcode dispatch loads a jump table with a rip-relative `lea`, so one displacement field differs while `md5_raw_norel`, `md5_fn_norel`, `md5_norm`, the instruction count and the byte count are all identical. See the pin's `why`. |
| `verus.items` `rec_alloc` | **FOUR of vstd's five `ensures`**, not five, and the deletion is the GATE's finding rather than the author's judgement — see the note under this table. |
| `miri.required: true` | derived from the seven trusted items. ⚠ **Unlike p32, Miri has something to see here** -- p34 allocates -- and what it finds on the SHIPPED rung is NOTHING on every input, while `controls/arm_unsafe_bug.rs` (the same file with `obj_retain` deleted) is the must-fire arm. |

⚠⚠ **ONE PIN MOVED AFTER THE FIRST FULL GATE RUN, AND IT IS DISCLOSED RATHER
THAN QUIETLY LANDED.** The contract block as FIRST WRITTEN carried **all five**
of vstd's `allocate` `ensures` on `rec_alloc`. The first full gate run's stage
5c reported `ensures[1]` — `pt.0.addr() + size <= usize::MAX + 1` — **NOT
LOAD-BEARING**: deleting it still gave `24 verified, 0 errors`. A trusted item's
`ensures` is an axiom, and one nothing depends on is an unchecked claim about
real Rust semantics carried for free, so it was deleted. **That is a strict
WEAKENING of a trusted item, which is the direction the gate asks for**, and it
moved `contract_sha256` from
`1fa98c8af297710166a2c93731f12b45be7c2c9b4dc39331fcd06203fae8f3dd` (as first
written) to the value the current gate record carries. `NOTES.md` 0 and 6d
record the move; nothing else in the block changed.

## Reproducing

```sh
python3 patterns/p34-refcount-stack/inputs/gen.py     # the .bin files are gitignored
harness/build.py p34
harness/measure.py p34        # BEFORE report.py: report.py loads results/p34-*.json first
harness/report.py p34
harness/check.py p34
harness/report.py p34 && harness/check.py p34   # stage 9c's one-run lag, on a NEW pattern only
python3 patterns/p34-refcount-stack/controls/safety_line.py
python3 patterns/p34-refcount-stack/controls/no_dup.py
python3 patterns/p34-refcount-stack/controls/detectors.py
python3 patterns/p34-refcount-stack/controls/safe_arms.py
python3 patterns/p34-refcount-stack/controls/rust_bug.py
python3 patterns/p34-refcount-stack/controls/proof_mutants.py
```

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == rc_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (rc_fold). p34's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27, p29, p32 and p35 use and NOT p02's before/after set: p34's stack is a LOCAL of the kernel and every object it allocates is released before the call returns, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by ONE STATEMENT on the ACQUIRE path** -- `t->rc = t->rc + 1` on DUP -- and at R5 it is discharged as a LINEAR-RESOURCE obligation and not as a functional one. \u26a0\u26a0 That is the opposite of p32's and it is the row's R5 result: the abstract machine `run` this `ensures` names has NO REFERENCE COUNT IN IT AT ALL, because under the checked semantics an object is alive exactly while some stack entry names it and its payload never changes, so the ANSWER is a function of the id stack alone. Deleting the retain therefore does not break the postcondition -- it breaks `wf`, whose third conjunct says `perms[k].value().rc == cnt(ids, k)`, and with the count out of step `obj_dec`'s `requires rc > 0` is unprovable at the second release and `obj_free`'s permission has already been consumed. controls/proof_mutants.py demonstrates it with an ATTACK arm (delete `obj_retain`), a VACUITY arm (a constant body), an X1 arm that strikes the central conjunct out of `wf` itself, and a SPEC-WEAKEN arm. **The `ensures` is the FUNCTIONAL one**: `run` is an abstract machine carrying a stack of OBJECT IDS and a payload sequence indexed by ID, and it says the accumulator is what that machine computes -- so a kernel that folded a recycled block's payload, or that folded a different number of created objects, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest or that the op stream is well formed.** `run` specifies what the PROGRAM does -- stop when the window runs out, fold SENT for a NEW past the capacity, for a DUP of an empty or full stack and for a POP or READ of an empty stack -- so degenerate.bin and all five adversarial op-stream files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that the op stream never duplicated a reference would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: ONE statement on the DUP path, `t->rc = t->rc + 1;` in c/kernel_hardened.c. c/kernel.c is otherwise character-identical, and ../controls/safety_line.py preprocesses both shipped files and measures the difference at `+1 / -0` lines -- the smallest safety line in this tree.",
        "rust": "THE SAFETY LINE, in R4 and R5 only, spelled as the call the C rung omits: `obj_retain(t);` immediately after `let t = arr_get_unchecked(&stk, ntop - 1);`. \u26a0\u26a0 R2 AND R3 HAVE NO SITE FOR THIS LINE AND THAT IS THE ROW'S SAFE-RUST RESULT, NOT AN OMISSION -- see the next entry and the why key."
      },
      {
        "c": "THE OBJECT CARRIES ITS OWN COUNT, in both C rungs and in c/kernel.h: `size_t rc;` as the FIRST member of `struct p34_obj`. The position is load-bearing and disclosed -- it is what puts glibc's tcache words on `rc` and `len` and leaves `data` intact.",
        "rust": "the same in R4 and R5: `pub rc: usize,` as the first field of `#[repr(C)] pub struct Obj`. \u26a0 In R2 and R3 the count is `Rc`'s own and this field does not exist -- `Rc::clone(` is where it is incremented and the `Drop` is where it is decremented. That is the one place the rungs are not isomorphic and the why key argues it."
      },
      {
        "c": "THE RELEASE IS A DECREMENT AND A FREE AT ZERO, CORRECT IN BOTH C RUNGS: `o->rc = o->rc - 1;` followed by `if (o->rc == 0)` and `free(o);`. R1's bug is NOT that it releases wrongly -- it does not -- it is that publishing a reference does not count it.",
        "rust": "the same in R4 and R5, through the accessor both rungs share: `let n = obj_dec(q);` followed by `if n == 0 {` and `obj_free(q);`."
      },
      {
        "c": "THE STACK IS A FIXED-EXTENT LOCAL AND EVERY ENTRY IS RELEASED EXACTLY ONCE, in both C rungs: `struct p34_obj *stk[P34_CAP];` plus the epilogue `while (ntop > 0) {`. The epilogue is what makes `0 -> underflow` reachable from every DUP and is why the bug has no benign input.",
        "rust": "the same array in R4 and R5, `[*mut Obj; CAP]`, with the same epilogue `while ntop > 0 {`. \u26a0\u26a0 R2 AND R3 HAVE NO EPILOGUE: dropping `[Option<Rc<Obj>>; CAP]` IS that loop, written by the language. NOTES.md 5 prices the difference."
      },
      {
        "c": "THE STORAGE IS ONE `malloc` PER OBJECT AND A REAL `free`, in both C rungs: `malloc(sizeof *o)` and `free(o);`. A pool or a free list would leave the stale use inside a live allocation and the row would be p32's; see the why key, which measures both.",
        "rust": "the same in R4 and R5, through vstd's own allocation API copied for codegen: `std::alloc::alloc(layout)` and `std::alloc::dealloc(p, layout);`. In R2 and R3 it is `Rc::new(`, which is the same allocator and one allocation per object."
      },
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first: `if len - p < 2 {` in R2, R4 and R5. \u26a0 R3 does not write it -- `chunks_exact(2).take(nops)` carries the same bound inside the iterator, and the walk is the R3 lever the why key leaves deliberately unpinned."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, `c % 4`, in all four Rust rungs -- spelled `c % 4 == 0` in R2, R4 and R5 and `match c % 4 {` in R3, which is the R3 lever."
      },
      {
        "c": "the payload byte is a function of the operand that created the object, in both C rungs: `(uint8_t)(a * 7u + 1u)`. So a READ that returns a recycled block's payload returns a value no honest read of this reference's own object could produce.",
        "rust": "the same payload, in all four Rust rungs, spelled with the wrapping operators the language forces: `a.wrapping_mul(7).wrapping_add(1)`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`."
      },
      {
        "c": "the NEW count is folded last, so a rung that created a different number of objects cannot produce the same checksum: `return acc * 31 + (uint64_t)nnew;` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nnew as u64)`."
      }
    ],
    "forbidden": [
      "`transmute`",
      "`Weak<`",
      "`Arc<`",
      "`RefCell`",
      "`Rc::get_mut`",
      "`Rc::strong_count`",
      "`Rc::try_unwrap`",
      "`Box::into_raw`",
      "`Box::leak`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Vec::with_capacity`",
      "`calloc(`",
      "`realloc(`",
      "`memmove(`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE, AND THE HARM LANDS AN UNBOUNDED DISTANCE AWAY FROM IT. `DUP` publishes a SECOND reference to the object on the top of the stack and R1 does not retain it, so every later release over-decrements: the object is freed while a live stack entry still names it, and the next use of that entry -- a release that reads `o->rc`, or a READ that reads `o->data[0]` -- touches a freed block. THE READ PATH IS CORRECT IN c/kernel.c AND ASKS NOTHING WRONG, AND THAT IS THE C-MECHANISM DISTINCTION THIS ROW RESTS ON. p27's, p29's and p32's stale use is a READ that failed to revalidate, and each is repaired by growing a conjunct on the read path; a refcounted pointer is valid BY CONSTRUCTION, so no test the READ could grow would repair p34 without becoming a liveness table. The free happens EARLY rather than the read happening LATE. p32 is the furthest thing from this row in the tree: it allocates nothing at all. THE SAFETY LINE IS `+1 / -0` PREPROCESSED LINES, THE SMALLEST IN THIS TREE, and controls/safety_line.py measures it on the two SHIPPED files with `cc -E -P` rather than asserting it. \u26a0\u26a0 THERE IS NO BENIGN INPUT THAT EXECUTES THE SAFETY LINE, AND THAT IS PROVED RATHER THAN SEARCHED. `t->rc = t->rc + 1` is the ONLY increment in the kernel, so in R1 every object's `rc` is permanently 1; any executed DUP therefore leaves TWO stack entries naming a ONE-reference object, and the two releases that must follow -- each entry is released exactly once, by POP or by the epilogue -- go `1 -> 0` (*free*) and then `0 -> underflow`, reading `o->rc` out of a freed block. **So the R1-vs-R1h benign cost gradient is `0.00` BY CONSTRUCTION**, a statement about the pattern rather than a measurement outcome, and inputs/gen.py, model.py::no_dup_problems and controls/no_dup.py enforce the corollary mechanically: NO MATRIX INPUT MAY CONTAIN A DUP OP. \u26a0 `0.00` IS STILL MEASURED AND NOT ASSUMED -- R1h is a different compiled function and a never-executed statement can still move layout, register allocation and inlining. NOTES.md 4 reports the measured R1-R1h delta at BOTH optimisation levels on BOTH compilers beside the prediction. TWO BUG CLASSES SEPARATED BY WHICH INSTRUMENT SEES THEM, AND THE PAIR IS THE ROW'S MOST INTERESTING EVIDENCE. On `DUP POP POP` and `DUP POP READ` the two rungs' checksums are BIT-IDENTICAL and ASan is the ONLY discriminator: the refcount header comes first and `data` starts at offset 16, clear of glibc's tcache `next`/`key` words at user offsets 0 and 8, so the stale read returns the RIGHT byte and the release path folds a constant that does not depend on `rc` or on whether `free` ran. On `DUP POP NEW READ` the next NEW RECYCLES the freed block and the checksum DIVERGES. Both are shipped, adversarial-blind / adversarial-blindread and adversarial-recycle, each `sanitizer_expect: fires`. THE LAYOUT IS DISCLOSED HERE THE WAY p28 DISCLOSES ITS OWN, and it is the idiomatic layout for a refcounted buffer rather than a layout chosen to hide the harm; `size_t rc; size_t len; uint8_t data[8];` is what SDS, PyBytesObject and GBytes all look like. UBSAN IS SILENT ON EVERY INPUT AT EVERY OPTIMISATION LEVEL ON BOTH COMPILERS, and that is derived rather than observed: R1's undefined behaviour is entirely TEMPORAL. Every index the kernel forms is inside `stk[]` in both rungs -- DUP reads `ntop - 1` under `ntop > 0`, POP reads `ntop` after decrementing it under `ntop > 0`, and READ's index is `a % ntop` under `ntop > 0` -- so there is no spatial violation for UBSan to see. A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN (RECAP trap 5), so controls/detectors.py ships one control per detector and the UBSan one is not an ASan one. THE STORAGE IS `malloc`/`free` PER OBJECT AND THAT IS THE PATTERN RATHER THAN A CHOICE: a reference count exists to decide WHEN TO FREE, and a slot that is never freed has nothing to decide. `.memory/01-ladder.md`'s law -- safe Rust's temporal guarantee is a guarantee about the ALLOCATOR, and a structure that recycles its own storage gets no guarantee at all -- is what makes the storage choice load-bearing, and controls/safe_arms.py measures BOTH branches of it in ONE ROW: the `Rc` port CANNOT REPRODUCE the bug (p28's shape) and an index-arena port REPRODUCES IT BIT FOR BIT (p32's shape), on the same inputs, in the same file. SAFE RUST HAS NO SITE FOR THE SAFETY LINE, AND THAT IS A FINDING AND NOT AN OMISSION. `Rc::clone` publishes the second reference and increments the count in ONE operation; there is no way to obtain a second `Rc<Obj>` without it, and a borrow cannot be stored in the stack array because the borrow checker ties it to the array it came from. c/kernel.c's bug is exactly the separation of *publish a reference* from *count it*, and safe Rust does not offer the separation. That is why `Rc<` is REQUIRED in R2 and R3 here and FORBIDDEN in p29 and p32: on those rows it would move the liveness decision into a library and delete the comparison, and on this row the library IS the comparison. WHAT THE R5 PROVES AND WHAT IT COSTS. A `PointsTo` is LINEAR and p34's subject is ALIASING -- two stack entries naming one object is the normal, correct state of this kernel -- so the permission cannot be held per stack entry the way p27 holds one per slot. It is keyed by OBJECT, and the proof carries the bridge: `perms[k].value().rc == cnt(ids, k)`, the count stored in the object's own first word equals the NUMBER OF STACK ENTRIES naming it. `cnt` is an occurrence count over a `Seq<int>` and it is the first multiset-flavoured obligation in this tree. \u26a0\u26a0 LEAK-FREEDOM FALLS OUT AS A COROLLARY rather than as a second obligation: `obj_ok` requires `cnt(ids, k) > 0` for every key, and the epilogue runs until the stack is empty, so the permission map is EMPTY when the kernel returns -- `assert(perms.dom() =~= Set::empty())` is that statement. \u26a0 What it does NOT say is that any rung's map must be empty: Verus does not force a tracked resource to be consumed, so a rung that dropped the map would verify. THE PINNED vstd HAS NO `Rc` SPECIFICATION AND THAT IS A RESULT, NOT A REASON TO SHRINK THE ROW: `~/tools/verus/vstd/std_specs/smart_ptrs.rs` is 78 lines with no `strong_count`, no `Rc::clone`, no `into_raw`/`from_raw` and no `increment_strong_count`, so an R5 must model the counter itself in a raw-pointer rung -- which is what the C rung does anyway. NOTES.md 6. THE LAYOUT FACT IS A `global layout` DIRECTIVE AND NOT AN AXIOM. `vstd::layout::size_of` is UNINTERPRETED for a user struct at the pinned vstd, so neither `rec_alloc`'s `size != 0` nor `PointsToRaw::into_typed`'s alignment precondition can be discharged without telling Verus the layout. `global layout Obj is size == 24, align == 8;` does that, and RUSTC CHECKS IT AT CODEGEN -- with a wrong number the file still verifies and then fails to compile with `evaluation panicked: does not have the expected size`, measured. It is the one layout fact in this tree the COMPILER rather than a reviewer is responsible for, and it is why this rung costs no extra trusted item. NOTES.md 6a. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor, and `match c % 4` against R2's `if` chain -- exactly as p32 leaves its handle-register spelling unpinned and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 5 reports what it moves. \u26a0 The consequence for the cursor-guard entry below is stated there rather than left implicit: R2, R4 and R5 write `if len - p < 2 {` and R3 does not write it at all, because the iterator carries the same bound. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 24
    },
    "twin_obligations": {
      "verus.rs": 29
    },
    "obligations_note": "24 = THREE consts (CAP, DLEN, SENT) 1 each + ONE `#[derive(Clone, Copy)]` term on `Obj` + 20 function terms. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, not predicted; the loop is `.temp/t154/verus/obligations.sh` and the log is `.temp/t154/verus/obligations.log`. The 20: `cnt` 1 (RECURSIVE -- one termination query), the five `lemma_cnt_*` proof fns 1 each, `run` 1 (recursive), the five `obj_*` verified wrappers 1 each, `kernel` 3 (body + TWO loop bodies, the op walk and the epilogue) and `main` 5, quoted AS MEASURED. The zero terms are checkable the same way: `u32_at`, `nops_at`, `val_of`, `rc_fold`, `obj_ok` and `wf` are NON-RECURSIVE spec fns and report 0, and the five `external_body` items report 0. \u26a0 THE DERIVE TERM IS MEASURED AND NOT INFERRED: adding a second `#[derive(Clone, Copy)] pub struct` moves the count to 25 and adding a BARE `pub struct` leaves it at 24 (`.temp/t154/verus/ob_derive.rs`, `ob_bare.rs`). That reproduces p29's derive term and p32's bare-struct zero on a third pattern. \u26a0 The `global layout Obj is size == 24, align == 8;` directive carries NO obligation and is not an item -- rustc checks it at codegen instead, which is measured in NOTES.md 6a.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **24 shipped + 5**, one per trusted item inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked, slb_twin_arr_set_unchecked, slb_twin_rec_alloc and slb_twin_rec_free. \u26a0 p34 owes FIVE twins where p32 owes three, and the two extra are `vstd::raw_ptr::allocate` and `deallocate` -- p27's and p29's pair, because p34 allocates and p32 does not. **EVERY trusted item here has a twin and none is blocked**, which is p32's and p27's position and not p35's. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth, p32 the seventh, p35 the eighth and p34 the ninth."
      }
    },
    "items": {
      "verus.rs": {
        "u32_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nops_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "val_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cnt": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_cnt_push": {
          "external": null,
          "requires": [],
          "ensures": [
            "cnt(s.push(x), k) == cnt(s, k) + (if x == k { 1int } else { 0int })"
          ]
        },
        "lemma_cnt_drop": {
          "external": null,
          "requires": [
            "s.len() > 0"
          ],
          "ensures": [
            "cnt(s, k) == cnt(s.drop_last(), k) + (if s.last() == k { 1int } else { 0int })"
          ]
        },
        "lemma_cnt_zero": {
          "external": null,
          "requires": [
            "cnt(s, k) == 0"
          ],
          "ensures": [
            "forall|i: int| 0 <= i < s.len() ==> s[i] != k"
          ]
        },
        "lemma_cnt_absent": {
          "external": null,
          "requires": [
            "forall|i: int| 0 <= i < s.len() ==> s[i] != k"
          ],
          "ensures": [
            "cnt(s, k) == 0"
          ]
        },
        "lemma_cnt_le": {
          "external": null,
          "requires": [],
          "ensures": [
            "cnt(s, k) <= s.len()"
          ]
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rc_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "obj_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "buf_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_buf_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "load_input": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "emit": {
          "external": "verifier::external_body",
          "requires": [],
          "ensures": []
        },
        "arr_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_arr_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "arr_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_arr_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "rec_alloc": {
          "external": "verifier::external_body",
          "requires": [
            "valid_layout(size, align)",
            "size != 0"
          ],
          "ensures": [
            "pt.1@.is_range(pt.0.addr() as int, size as int)",
            "pt.2@@ == (DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
            "pt.0.addr() as int % align as int == 0",
            "pt.0@.provenance == pt.1@.provenance()"
          ]
        },
        "slb_twin_rec_alloc": {
          "external": null,
          "requires": [
            "valid_layout(size, align)",
            "size != 0"
          ],
          "ensures": [
            "pt.1@.is_range(pt.0.addr() as int, size as int)",
            "pt.2@@ == (DeallocData { addr: pt.0.addr(), size: size as nat, align: align as nat, provenance: pt.1@.provenance(), })",
            "pt.0.addr() as int % align as int == 0",
            "pt.0@.provenance == pt.1@.provenance()"
          ]
        },
        "rec_free": {
          "external": "verifier::external_body",
          "requires": [
            "dealloc@.addr() == p.addr()",
            "dealloc@.size() == size",
            "dealloc@.align() == align",
            "dealloc@.provenance() == pt@.provenance()",
            "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
            "p@.provenance == dealloc@.provenance()"
          ],
          "ensures": []
        },
        "slb_twin_rec_free": {
          "external": null,
          "requires": [
            "dealloc@.addr() == p.addr()",
            "dealloc@.size() == size",
            "dealloc@.align() == align",
            "dealloc@.provenance() == pt@.provenance()",
            "pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int)",
            "p@.provenance == dealloc@.provenance()"
          ],
          "ensures": []
        },
        "obj_new": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.1@.ptr() == r.0",
            "r.1@.is_init()",
            "r.1@.value().rc == 1",
            "r.1@.value().data@[0] == val",
            "r.2@.addr() == r.0.addr()",
            "r.2@.size() == size_of::<Obj>()",
            "r.2@.align() == align_of::<Obj>()",
            "r.2@.provenance() == r.0@.provenance"
          ]
        },
        "obj_retain": {
          "external": null,
          "requires": [
            "old(pt).ptr() == p",
            "old(pt).is_init()",
            "old(pt).value().rc < usize::MAX"
          ],
          "ensures": [
            "final(pt).ptr() == p",
            "final(pt).is_init()",
            "final(pt).value().rc == old(pt).value().rc + 1",
            "final(pt).value().data == old(pt).value().data"
          ]
        },
        "obj_dec": {
          "external": null,
          "requires": [
            "old(pt).ptr() == p",
            "old(pt).is_init()",
            "old(pt).value().rc > 0"
          ],
          "ensures": [
            "final(pt).ptr() == p",
            "final(pt).is_init()",
            "final(pt).value().rc == old(pt).value().rc - 1",
            "final(pt).value().data == old(pt).value().data",
            "n == old(pt).value().rc - 1"
          ]
        },
        "obj_read": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "pt.is_init()"
          ],
          "ensures": [
            "r == pt.value().data@[0]"
          ]
        },
        "obj_free": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "dl.addr() == p.addr()",
            "dl.size() == size_of::<Obj>()",
            "dl.align() == align_of::<Obj>()",
            "dl.provenance() == p@.provenance"
          ],
          "ensures": []
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == rc_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    }
  },
  "driver": {
    "statements": 12,
    "c_source": "c/main.c",
    "regions": [
      "safe_naive.rs",
      "safe_tuned.rs",
      "unsafe.rs",
      "verus.rs",
      "c/main.c"
    ],
    "aliases": {
      "c": {
        "n_body": "bytes.len()",
        "bytes": "bytes.as_slice()",
        "inp.n_iters": "n_iters"
      }
    },
    "call_args": {
      "c": {
        "kernel": [
          0,
          2,
          3
        ]
      }
    },
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 4 && stride_w <= n_blob",
      "{",
      "stride = stride_w ;",
      "nwin = n_blob / stride ;",
      "it = 0 ;",
      "while it < n_iters",
      "{",
      "k = acc * nwin >> 64 ;",
      "r = kernel ( buf , k * stride , stride ) ;",
      "acc = acc * 31 + r ;",
      "it = it + 1 ;",
      "}",
      "}"
    ]
  },
  "collapse": {
    "probe_inputs": [
      "small.bin",
      "large.bin"
    ],
    "probe_iters": [
      100,
      200
    ],
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p32's, p35's, p16's, p05's, p11's, p12's, p06's and p14's denominator. marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary, so the one-shot loader terms cancel. \u26a0 The estimate is STRICT and by the widest margin in the temporal family: it over-counts the 4 window-header bytes, which are decoded as a u32 and are not operations, and under-counts every 2-byte operation -- each does a modulo, a compare chain and a multiply-add, while a NEW also calls `malloc`, zeroes DLEN bytes and writes two words, and a POP reads, decrements and stores a word and may call `free`. No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per byte applies and what it catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "norel",
      "why": "R4 == R5 up to pc-relative displacement fields at BOTH optimisation levels, and NOT by raw bytes at either. \u26a0\u26a0 THAT IS WEAKER THAN p27's, p32's and p35's `O3: exact`, AND THE MECHANISM IS KNOWN RATHER THAN GUESSED (PROTOCOL rule 12). `harness/asm.py stat` reports `md5_raw_norel`, `md5_fn_norel` and `md5_norm` IDENTICAL, the same 190 raw / 179 non-pad instructions, the same 688 bytes and the same 33 masked relocation fields on both binaries; the raw digests differ because the two crates place `kernel` at addresses 0x20 apart, and the kernel's four-way opcode dispatch loads a JUMP TABLE out of `.rodata` with a rip-relative `lea` -- `lea -0xde08(%rip),%rcx` against `lea -0xdde8(%rip),%rcx`, both resolving to the SAME absolute address 0x78f0. p27's and p32's kernels have no such rodata reference, which is why they reach `exact` and this one cannot: it is a fact about LINK LAYOUT, not about the proof. The proof still licenses the unsafe code at zero instruction cost, which is this project's standing R4/R5 result, and the instruction-level evidence for it here is the identical normalised digest and the identical count rather than the raw md5. The five twins are `#[cfg(slb_twin)]` and no measured build compiles them, so they cost zero instructions structurally."
    }
  ],
  "miri": {
    "pair": [
      "unsafe",
      "verus"
    ],
    "sources": [
      "unsafe.rs"
    ],
    "required": true,
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. p34 has seven. \u26a0\u26a0 **And unlike p32, Miri has something to see here**: p34 allocates and frees, so a use-after-free is exactly the class Miri reports. What it finds on the SHIPPED unsafe.rs is NOTHING, on every input including all five adversarial ones -- the shipped rung retains correctly, so that is the right answer and it is what stage 8 measures. What it finds on `controls/arm_unsafe_bug.rs`, which is this rung with `obj_retain` deleted and nothing else, is a `heap-use-after-free`-class Undefined Behaviour report; `controls/rust_bug.py` is the must-fire arm and NOTES.md 7 has both rows. Cost: check.py rewrites n_iters to 4.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
