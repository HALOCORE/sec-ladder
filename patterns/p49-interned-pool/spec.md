# p49 -- an interned, deduplicated string pool, and a write through a buffer the record does not own

**CWE-471 (modification of assumed-immutable data), reached through the
deduplication that makes the pool worth having.** The kernel parses an op stream
into a pool of strings. Content narrower than an `INLINE_THRESHOLD` is
**INTERNED**: the pool looks the string up in a dedup table and, on a hit, the
new record BORROWS the buffer an earlier record already holds. Two records then
legitimately name ONE buffer -- correctly, intentionally, and with no undefined
behaviour anywhere. The cycle-breaker then **writes through it**. `c/kernel.c`
omits the copy-on-write block `if (rshd[t]) { ... }` that would ask *is this
buffer mine to write?*. `c/kernel.h` carries the kernel contract in pseudocode;
this file carries the reasoning and the machine-readable pins; `README.md` says
the same thing for a reader who has read neither.

The C mechanism is `CVE-2022-40304`'s, **admitted at `TASK_143` and
re-adjudicated and UPHELD at `TASK_160` by running it** against the 32-row tree:
120 cells x 20 runs, `n_distinct = 1` in all 120, every hardened arm silent in
12/12, positive controls firing on both compilers.

## ⚠⚠ NOTHING IS FREED, EVERY INDEX IS IN BOUNDS, AND EVERY DETECTOR IS SILENT

This row's rung R1 executes **no undefined behaviour of any kind**. Nothing is
allocated, nothing is freed, no pointer dangles, and `c/kernel.h` proves in four
lines that every index it forms is inside `mem[0 .. MEM)`. So ASan, UBSan, Miri
and the glibc allocator are silent on **every** input including the adversarial
ones, at both optimisation levels on both compilers.

> **The checksum is the only instrument this row has**, which is why `model.py`
> carries the whole result and ships a must-fire detector arm, and why
> `controls/detectors.py`'s positive controls are load-bearing here in a way they
> are not elsewhere: on a row where every column is silent, a control that FIRES
> is the only thing separating *silent* from *not linked in*.

✅ **That is the exact INVERSE of `p34`'s detector-only cell**, where the two
rungs' checksums are bit-identical and ASan is the only discriminator. **The two
rows bracket *which instrument sees the harm* from opposite ends, and neither
could have been written without the other.**

## The C-mechanism distinction, stated first because a reviewer will attack it first

```
p08  ONE memcpy whose source and destination ranges OVERLAP. The overlap lasts
     one library call, it is UNDEFINED BEHAVIOUR (C11 7.24.2.1p2), it is created
     by an arithmetic accident (2*dr < m), there is no second referent and no
     ownership structure, and the repair is A DIFFERENT FUNCTION (memmove).
p32  nothing is allocated; a stale handle is double-pushed, the free list
     SELF-LOOPS, and two handles come to name one block. The aliasing is
     CREATED BY THE BUG, the block has been RECYCLED, and the safety line asks a
     LIFETIME question: gen[h] != g.
p34  a missing retain on publish frees an object a live reference still names.
     A real free(); the read path is correct; fix the ACQUIRE.
p49  the sharing is CREATED BY DESIGN, by a dedup table, is CORRECT, and is not
     undefined behaviour at all. It persists across many operations. The bug is
     the WRITE THROUGH IT, and the safety line asks an OWNERSHIP question:
     is this buffer mine to write?                              Fix the MUTATION.
```

⚠⚠ **`p08` IS THE SHARPEST ATTACK AND IT IS WORTH ANSWERING WITH A
MEASUREMENT.** `harness/tools/composition.py` declares `p08`'s class as *"two
live references to overlapping storage, one of them mutable"*, which describes
`p49` word for word. Four separations, and the last is measured:

1. **`p08`'s overlap is UB; `p49`'s sharing is not.** C says nothing whatever
   against two pointers into one object. There is no rule `c/kernel.c` breaks.
2. **`p08`'s alias is an accident; `p49`'s is the contract.** Delete the aliasing
   from `p08` and it is the same program, correct. Delete it from `p49` and the
   pool stops deduplicating -- which is the upstream patch, and `TASK_160`
   measured that it changes a benign observable.
3. **`p08` repairs by changing the FUNCTION; `p49` repairs by adding an
   OWNERSHIP TEST BEFORE THE WRITE.** `memcpy` -> `memmove` is a one-token
   substitution with no state; `c/kernel_hardened.c` un-shares, which costs
   storage and can REFUSE.
4. ⚠ **`p49`'s kernel contains no overlapping copy at all, and that is
   re-derived rather than argued.** `controls/no_overlap.py` walks every shipped
   window and checks that (a) every copy's source and destination ranges are
   DISJOINT and (b) two records' content ranges either COINCIDE EXACTLY or are
   disjoint -- **never partial, which is the only kind `p08` has**. `p08`'s own
   kernel is re-run in the same control as the negative: its ranges overlap
   partially on its adversarial input, and the census separates the two rows on
   a number.

⚠ **`p32` is the closest built row and it INVERTS**, which is the sentence
`RECAP.md` finding 61 and the catalogue both carry: `p32`'s alias is created BY
the bug and its line asks a LIFETIME question; here the alias IS the contract and
the line asks an OWNERSHIP one. ✅ **And a fourth repair-site position:**
`p27`/`p29`/`p32` fix the READ, `p28` the DESTROY, `p34` the ACQUIRE, `p49` the
**MUTATION**.

## ⚠⚠⚠ THE DEFECT THE REDUCTION CARRIED, AND WHAT FIXING IT COST

`.temp/t160/red/k40304.c` -- the demonstration this row was admitted on -- fixes
the content width at `K_CLEN 3` against `K_THRESH 5`, so
`if (K_CLEN < K_THRESH)` is **`if (3 < 5)`, a compile-time constant**. The
non-interned branch is DEAD and **no record is ever born owned**, so the
`INLINE_THRESHOLD` -- which is the CVE's own precondition -- is not a test at
all. That is `.memory/03-measurement.md` entry 19's shape: *a check that is a
tautology of the representation it is written over*.

⚠⚠⚠ **BUT THE STRONGER FORM OF THAT CLAIM IS FALSE, AND MEASURING IT IS HOW
THIS ROW EARNED ITS FIRST REFUTATION.** `TASK_161.md` and `.temp/mgr161/NOTES.md`
both assert, verbatim, *"`r_shared[nrec]` is therefore ALWAYS `1`, so
`SLB_HARDEN == 1`'s guard `if (r_shared[i])` CAN NEVER BE FALSE"*. **It can.**
The reduction's own copy-on-write arm writes `r_shared[i] = 0;` when it
un-shares, so a *second* `BREAK` on a record the first one copied takes the false
branch. Measured in the reduction's own C, with two counters spliced into a copy
of it (`.temp/t161/red_probe/probe.py`, 20 000 random op streams at
`SLB_HARDEN=1`):

```
records BORN shared            215579
records BORN owned                  0     <-- the DEAD branch, and the real defect
guard `if (r_shared[i])` TRUE   67195
guard `if (r_shared[i])` FALSE  30263     <-- 31.1% of 97 458 evaluations
```

⚠ What *is* true of the reduction **as shipped**: its two blobs evaluate the
guard **once between them** (benign 0, adversarial 1) and it is TRUE that once,
so the demonstration never exercised the false branch even though the program
can. ✅ **The precise defect is *no record is ever born owned*, not *the guard
cannot fire*** — and the two would need different repairs. `NOTES.md` 8a.

✅ **The fix is that the content width is DERIVED FROM THE INPUT**:
`w = 1 + a % MAXW` with `MAXW = 6` against `THRESH = 4`, so `w` ranges over
`1 .. 6` and three of the six intern. `controls/threshold.py` measures both
configurations on the same 20 000 random op streams:

```
                              shipped (w = 1 + a % 6)   reduction (w == 3)
intern branch taken                    90476                180834
own branch taken                       89409                     0    DEAD
records BORN shared                    90222                177555
records BORN owned                     87760                     0    DEAD
guard TRUE                             33373  (34.2%)        65973  (67.7%)
guard FALSE                            64127  (65.8%)        31527  (32.3%)
  ...of which on a record BORN owned   48033                     0    IMPOSSIBLE
  ...of which after a copy-on-write    16094                 31527
```

⚠⚠ **AND THE FIX IS NOT SMALL, WHICH THE TASK FILE ASSERTED AND `NOTES.md` 8
REFUTES WITH A COUNT.** A variable width makes three of the kernel's five
operations loops over `w` instead of straight-line code, and at R5 each of those
loops needs a recursive spec function, a loop invariant and -- for the copy -- an
INDUCTION LEMMA. `NOTES.md` 8 has the line counts, the obligation counts and the
one Verus failure the change produced.

## The safety line is `cow`, and it is NOT the upstream patch

| arm | site | shape |
|---|---|---|
| **`cow`, shipped as R1h** | `c/kernel_hardened.c`, the BREAK path | un-share before writing. **Benign-invisible.** |
| `provenance`, a `controls/` arm | the DEFINE path | never borrow, always own. Upstream commit `644a89e`. **Changes a benign observable.** |

`TASK_160` measured on the port that upstream's spelling turns `10 passed,
0 failed` into `9 passed, 1 failed` and flips `"interned":true` to `false`, while
copy-on-write is byte-identical to the bug on benign input. **The same thing is
true here and it is measured rather than inherited** (`controls/spellings.py`),
because this kernel's epilogue folds `rshd[t]` beside each record's content --
which is the reduction of the port's `"interned"` API field.
⚠ **An upstream patch is not automatically a safety line; check it against the
benign observable.**

## ⚠ The repair can REFUSE, and that is the honest price of copy-on-write

Un-sharing needs storage the bug does not need. With the private region
exhausted, R1h folds SENT and does not write at all -- still memory-safe, still
value-safe, and **one behaviour the buggy rung does not have**.
`adversarial-cowfull.bin` is the cell that fires it and `NOTES.md` 3c prices it.
**A repair that consumes a resource can run out of it**, and nothing else in this
tree says so.

## No benign input may BREAK a shared record, and that is enforced in three places

`harness/check.py` stage 2 requires every non-adversarial cell to agree with
`model.py` **and with every other cell**, and a BREAK on a shared record is
exactly where R1 and R1h part company. ⚠ **The divergence is not only the
corrupted byte**: R1h's copy-on-write also spends private storage and clears the
record's ownership flag, and the epilogue folds that flag. Both halves are
excluded by one property, which is why the property is stated about the FLAG:

> **no non-adversarial window may execute a BREAK on a record whose `rshd` is 1.**

`inputs/gen.py` cannot emit one, `model.py::no_share_break_problems` re-derives
it from the SHIPPED blob on every gate invocation, and
`controls/no_share_break.py` censuses the whole directory.

⚠ **The safety line's guard is still EVALUATED on every benign BREAK that names
a record** -- 1437 times on `large.bin`, 34 on `small.bin`, 2 on
`degenerate.bin`, and FALSE every time. (A BREAK with `nrec == 0` folds SENT
before reaching the guard; `degenerate.bin` executes 3 BREAKs and evaluates the
guard twice, which is what the parenthesis is for.) So p49 has a real, non-zero benign cost gradient where `p34`'s is `0.00`,
and `NOTES.md` 4 reports it at both optimisation levels on both compilers.

## What each rung spells

| rung | the shared buffer | the safety line |
|---|---|---|
| **R1** `c/kernel.c` | `roff[t]`, a byte offset into `mem[]`; `rshd[t]` is maintained and folded but never consulted before a write | **absent** |
| **R1h** `c/kernel_hardened.c` | the same | present: `if (rshd[t])`, with a byte-loop copy and a SENT refusal |
| **R2** `safe_naive.rs` | the same offset, in `[u8; MEM]` -- ⚠ **the alias is an INTEGER, so the borrow checker has nothing to say** | present: `if rshd[t] == 1 {` |
| **R3** `safe_tuned.rs` | the same | the same, with `copy_within` for the copy |
| **R4** `unsafe.rs` | the same, every access unchecked | present: `if arr_get_unchecked(&rshd, t) == 1 {` |
| **R5** `verus.rs` | the same, with `wf_prov` in the loop invariant | the same, plus a DISJOINTNESS `requires` on `copy_bytes` |

## ⚠⚠ Safe Rust offers BOTH the bug and the repair, and that is the row's safe-Rust result

`CLAUDE.md` rule 6 names *"safe Rust reproduces the bug bit-identically"* as a
FINDING. Here it is the finding, and `controls/safe_arms.py` builds three ports:

1. **the index arena** (shipped as R2/R3). The alias is a `usize`; the borrow
   checker is silent; **safe Rust expresses the bug and the repair equally
   easily**, and `controls/rust_bug.py` builds the buggy one with no `unsafe`
   anywhere.
2. **`Rc<RefCell<Buf>>`** -- an idiomatic shared mutable buffer.
   **Reproduces `c/kernel.c` bit for bit on all nine inputs**, safely: `RefCell`
   is exactly the "shared and mutable" the pattern is about, and the runtime
   borrow check passes because there is only ever one borrow at a time.
3. **`Rc<Buf>` with `Rc::make_mut`.** ⚠⚠ **THE SAFETY LINE IS THE STANDARD
   LIBRARY'S**: `make_mut` *is* copy-on-write, and this arm reproduces
   `c/kernel_hardened.c` bit for bit. **That is the only one of the three in
   which safe Rust rules the bug out, and it does it with an API choice rather
   than with the type system.** ⚠ **The two `Rc` arms differ in ONE type**:
   `Buf` carries the width as a field in both.

⚠ **That is the opposite of `p34`**, where safe Rust cannot express the bug at
all because `Rc::clone` is the only way to publish a second reference.

## The R5, and the obligation that is genuinely new

⚠⚠ **`copy_bytes` carries `requires src + w <= dst` -- a DISJOINTNESS /
PROVENANCE precondition, and `TASK_160` §8 predicted that nothing in this tree
states one.** It is discharged out of `wf_prov`, the loop invariant that says a
SHARED buffer lives wholly inside the interning arena while the private bump is
at or above it: `roff[t] + rlen[t] <= ARENA <= pbump`.

⚠ **What the `ensures` deliberately does NOT say is "no record's content aliases
another's" -- because that is FALSE BY DESIGN.** Deduplication is the contract.
The abstract machine `run` shares buffers exactly where the kernel does; the
disjointness that IS stated is narrower and is about the COPY. Saying it the
other way round would be the easy mistake and it would specify a different
program.

⚠⚠ **And the safety line itself is discharged as an ORDINARY FUNCTIONAL
POSTCONDITION**, which is `p32`'s finding in a different currency. Both arms of
`if rshd[t] == 1` type-check without the test, every index is in range either
way, and no permission is consumed anywhere in the kernel. What fails without it
is that the loop stops computing `run`. **Linearity has nothing to say about this
bug, because the bug does not touch an allocation.**
`controls/proof_mutants.py` is the battery that says so rather than asserting it.

## The pins, and the arithmetic behind four of them

| pin | why |
|---|---|
| `verus.obligations` = 34 | one Verus query per function plus one per loop body. **Measured, not predicted**: `./verus_run.py patterns/p49-interned-pool/verus.rs` reports `34 verified, 0 errors`. p49 has 17 spec fns, 3 proof fns, 5 trusted items, 5 verified helpers, `kernel` and `main` -- more than any built row, because a variable-width string pool needs four helper loops where `p32` needs none. |
| `verus.twin_obligations` = 37 | the count under `--cfg slb_twin`: **34 shipped + 3**, one per trusted item inside the twin regime -- `slb_twin_buf_get_unchecked`, `slb_twin_arr_get_unchecked` and `slb_twin_arr_set_unchecked`. Measured, not predicted: `./verus_run.py patterns/p49-interned-pool/verus.rs --cfg slb_twin` reports `37 verified, 0 errors`. **Every trusted item here HAS a twin and none is blocked** -- p27's, p32's and p34's position, not p35's. `load_input` and `emit` are outside the regime (`external_body` with no `ensures` and no `unsafe` body) and have no twins. |
| `identity` `O0: norel`, `O3: exact` | **R4 == R5 by raw machine-code bytes at `-O3`** (`md5_raw 563ecf2f9431db3c9ec8963b5ccd5c62` on both), and identical up to pc-relative displacement fields at `-O0` (`md5_raw_norel bdab100e3517b0c56fc510117d7bac7a`, `md5_norm 06e8fe436c25b756ace6c640a5fad7ac`, 665 non-pad instructions on both). p32's pin exactly, and for p32's reason: p49 has no pointer write, no allocation and no vstd call in the kernel at all, so there is nothing for the two rungs to spell differently. The `-O0` residue is link layout -- the crate names differ in length, so the displacements do. |
| `miri.required: true` | derived from the five trusted items. ⚠ **And note what Miri finds, because it is this row's headline and not a gap in the run: NOTHING, on any input, including all five adversarial ones.** The pool is a local array alive for the whole call; the buggy rung's every index is in range; nothing is allocated, so nothing can be used after being freed. **Miri is an instrument about ALLOCATIONS and p49 has none.** What Miri still buys is what it buys on `p08` and `p32`: a trusted body that read one element past an array would satisfy every `ensures` in `verus.rs` and be invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req. Cost: `check.py` rewrites `n_iters` to 4. |

## Reproducing

```sh
python3 patterns/p49-interned-pool/inputs/gen.py     # the .bin files are gitignored
harness/build.py p49
harness/measure.py p49        # BEFORE report.py: report.py loads results/p49-*.json first
harness/report.py p49
harness/check.py p49
harness/report.py p49 && harness/check.py p49   # stage 9c's one-run lag, on a NEW pattern only
python3 patterns/p49-interned-pool/controls/safety_line.py
python3 patterns/p49-interned-pool/controls/threshold.py
python3 patterns/p49-interned-pool/controls/no_share_break.py
python3 patterns/p49-interned-pool/controls/no_overlap.py
python3 patterns/p49-interned-pool/controls/detectors.py
python3 patterns/p49-interned-pool/controls/spellings.py
python3 patterns/p49-interned-pool/controls/safe_arms.py
python3 patterns/p49-interned-pool/controls/rust_bug.py
python3 patterns/p49-interned-pool/controls/proof_mutants.py
```

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == intern_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (intern_fold). p49's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27, p29, p32, p34, p35 and p25 use and NOT p02's before/after set: the pool is a LOCAL of the kernel and nothing crosses the signature, so there is nothing for an `after` binding to name. **The security property is carried by ONE BLOCK ON THE MUTATION PATH** -- `if (rshd[t])` in c/kernel_hardened.c -- and ⚠⚠ AT R5 IT IS DISCHARGED AS AN ORDINARY FUNCTIONAL POSTCONDITION, WHICH IS THIS ROW'S PROOF-SIDE RESULT RATHER THAN AN OMISSION. The abstract machine `run` this `ensures` names HAS NO ALLOCATOR, NO POINTER AND NO LIFETIME in it: one byte sequence, three parallel dedup-table sequences, three parallel record sequences and two bumps. That is not a simplification, it is the specification-side statement of why this bug is not a memory-safety bug -- every index the buggy rung forms is in range, so the only thing an omission can cost is a WRONG ANSWER, and a wrong answer is exactly what a functional postcondition catches. ⚠⚠ What IS a memory-safety obligation here is `copy_bytes`'s `requires src + w <= dst`, a DISJOINTNESS precondition discharged out of wf_prov, and TASK_160 §8 predicted that nothing in this tree states one. ⚠ The `ensures` deliberately does NOT say that no record's content aliases another's: that is FALSE BY DESIGN, because deduplication is the contract. **The `ensures` is the FUNCTIONAL one**: `run` says the accumulator is what an abstract pool computes, so a rung that wrote through a borrowed buffer, or that deduplicated differently, or that accepted a different number of records, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest or that the op stream is well formed.** `run` specifies what the PROGRAM does -- stop when the window runs out, fold SENT for a DEFINE past the record table, past the dedup table, past the arena or past the private region, fold SENT for a BREAK or a READ with no records, and fold SENT for a BREAK that cannot un-share -- so degenerate.bin and all six adversarial op-stream files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that no BREAK ever names a shared record would be a precondition about the contents of a file that no honest loader can discharge (.memory/02-bench-rules.md), and it would delete the row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: the copy-on-write block at the ONE site where the cycle-breaker writes, opening `if (rshd[t]) {` in c/kernel_hardened.c. c/kernel.c goes straight to `mem[roff[t]] = 0;` and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct. ../controls/safety_line.py preprocesses both shipped files and measures the difference rather than asserting it.",
        "rust": "THE SAFETY LINE, in all four Rust rungs, and every one of them has it because every Rust rung computes the CHECKED answer: `if rshd[t] == 1 {` in safe_naive.rs and safe_tuned.rs, `if arr_get_unchecked(&rshd, t) == 1 {` in unsafe.rs and verus.rs -- the operand is the same, the accessor is what each rung forces. ⚠⚠ **Not one of the four gets any part of it from the language**: the alias is an INTEGER offset, so the borrow checker has nothing to say, and ../controls/rust_bug.py builds the rung WITHOUT it in SAFE Rust with no unsafe anywhere. See the why key for the two container choices that DO decide it."
      },
      {
        "c": "THE INLINE THRESHOLD, in both C rungs: `if (w < P49_THRESH)`, with the width DERIVED FROM THE INPUT one line above -- `w = (uint8_t)(1u + a % P49_MAXW);`. Both branches are live and the rshd flag genuinely varies; the reduction this row was admitted on had a constant width and a dead branch, and the why key measures the difference.",
        "rust": "the same threshold and the same derivation, in all four Rust rungs: `let w: u8 = 1 + a % MAXW;` and `w < THRESH`."
      },
      {
        "c": "THE DEDUP TABLE IS CONSULTED BEFORE A BUFFER IS CREATED, in both C rungs: `f = p49_find(ekey, elen, nent, key, w);` followed by `if (f == nent)`. A HIT is what creates the alias, and it is CORRECT -- `roff[nrec] = eoff[f];` with `rshd[nrec] = 1;`.",
        "rust": "the same lookup in all four Rust rungs, spelled the way each forces: an indexed `while k < nent` with a `break` in safe_naive.rs, unsafe.rs and verus.rs, and `.position(|(&x, &y)| x == key && y == w)` in safe_tuned.rs -- the R3 lever, which the why key leaves deliberately unpinned."
      },
      {
        "c": "THE WRITE THROUGH THE BUFFER, in both C rungs, and it is one store: `mem[roff[t]] = 0;`. It is in bounds in every run of both rungs; what differs is whether `roff[t]` still names a buffer somebody else holds.",
        "rust": "the same store in all four Rust rungs: `mem[roff[t] as usize] = 0;` in safe_naive.rs and safe_tuned.rs, `arr_set_unchecked(&mut mem, ro as usize, 0)` in unsafe.rs and verus.rs."
      },
      {
        "c": "THE ARENA AND THE PRIVATE REGION ARE ONE ARRAY WITH TWO BUMPS, in both C rungs: `abump = 0;` and `pbump = P49_ARENA;`, each grown only under an explicit capacity test (`abump + w > P49_ARENA` and `pbump + w > P49_MEM`). One array is what makes the sharing expressible as an OFFSET, which is what lets all seven rungs share a representation.",
        "rust": "the same two bumps over the same one array in all four Rust rungs: `let mut abump: usize = 0;` and `let mut pbump: usize = ARENA;`."
      },
      {
        "c": "THE EPILOGUE FOLDS EVERY RECORD'S CONTENT AND ITS OWNERSHIP FLAG, in both C rungs: `acc = acc * 31 + (uint64_t)rshd[t];` beside the content fold. The flag is this kernel's reduction of the port's interned:true/false API field; it is what makes the PROVENANCE repair benign-observable while copy-on-write is not, and it is what keeps the rshd array LIVE in R1 so the gradient prices the check rather than the bookkeeping.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(rshd[t] as u64)` in safe_naive.rs and safe_tuned.rs, and `acc.wrapping_mul(31).wrapping_add(arr_get_unchecked(&rshd, t) as u64)` in unsafe.rs and verus.rs."
      },
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first: `if len - p < 2 {` in safe_naive.rs, unsafe.rs and verus.rs. ⚠ safe_tuned.rs does not write it -- `chunks_exact(2).take(nops)` carries the same bound inside the iterator, and the walk is the R3 lever the why key leaves deliberately unpinned."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, `c % 4`, in all four Rust rungs -- spelled `c % 4 == 0` in safe_naive.rs, unsafe.rs and verus.rs and `match c % 4 {` in safe_tuned.rs, which is the R3 lever."
      },
      {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `v = P49_SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: `SENT`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(v);`."
      },
      {
        "c": "the RECORD COUNT is folded last, so a rung that accepted a different number of records cannot produce the same checksum: `return acc * 31 + (uint64_t)nrec;` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nrec as u64)`."
      }
    ],
    "forbidden": [
      "`malloc(`",
      "`calloc(`",
      "`realloc(`",
      "`free(`",
      "`std::alloc::`",
      "`vstd::raw_ptr::`",
      "`Box::new`",
      "`Box::leak`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Rc<`",
      "`RefCell`",
      "`memcpy(`",
      "`memmove(`",
      "`memset(`",
      "`transmute`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED BLOCK AT THE MUTATION SITE, AND THE HARM IS A WRONG VALUE CROSSING AN OWNERSHIP BOUNDARY WITH NO UNDEFINED BEHAVIOUR ANYWHERE. Content narrower than THRESH is INTERNED and DEDUPLICATED, so two records legitimately BORROW one buffer -- correctly, intentionally, and with no rule of C broken -- and the cycle-breaker then WRITES THROUGH IT. c/kernel.c omits `if (rshd[t])`, the copy-on-write test that asks whether the buffer is the record's to write. THAT IS THE C-MECHANISM DISTINCTION THIS ROW RESTS ON, AND THE ROW A READER WILL REACH FOR FIRST IS p08. p08 is ONE memcpy whose source and destination ranges overlap: the overlap lasts one library call, it is UNDEFINED BEHAVIOUR (C11 7.24.2.1p2), it is created by an arithmetic accident (`2*dr < m`), there is no second referent and no ownership structure anywhere in the program, and the repair is A DIFFERENT FUNCTION. Here the sharing is created BY DESIGN by a dedup table, is CORRECT, is not undefined behaviour at all, persists across many operations, and the repair is an OWNERSHIP TEST BEFORE A WRITE that costs storage and can REFUSE. ⚠ And this kernel contains NO overlapping copy at all, which is re-derived rather than argued: controls/no_overlap.py walks every shipped window and checks that every copy's source and destination ranges are DISJOINT and that two records' content ranges either COINCIDE EXACTLY or are disjoint -- never PARTIAL, which is the only kind p08 has -- and it runs p08's own kernel in the same census as the negative. ⚠ p32 IS THE CLOSEST BUILT ROW AND IT INVERTS: p32's alias is created BY the bug, its block has been RECYCLED, and its safety line asks a LIFETIME question (`gen[h] != g`); here the alias IS THE CONTRACT, nothing is stale or recycled, and the line asks an OWNERSHIP question. By harness/tools/composition.py's own stated test -- what does the safety line ASK? -- they ask different questions. And this is a FOURTH REPAIR-SITE POSITION: p27/p29/p32 fix the READ, p28 the DESTROY, p34 the ACQUIRE, p49 the MUTATION. ⚠⚠⚠ THE REDUCTION THIS ROW WAS ADMITTED ON CARRIED A DEFECT AND THE BUILD FIXES IT. .temp/t160/red/k40304.c sets `K_CLEN 3` against `K_THRESH 5`, so `if (K_CLEN < K_THRESH)` is `if (3 < 5)` -- a compile-time constant -- the non-interned branch is DEAD and NO RECORD IS EVER BORN OWNED, so the INLINE_THRESHOLD, which is the CVE's own precondition, is not a test at all. That is .memory/03-measurement.md entry 19's shape. ⚠⚠⚠ THE STRONGER FORM OF THAT CLAIM IS FALSE AND MEASURING IT IS THIS ROW'S FIRST REFUTATION: TASK_161.md and .temp/mgr161/NOTES.md both assert verbatim that `if (r_shared[i])` CAN NEVER BE FALSE, and IT CAN -- the reduction's own copy-on-write arm writes `r_shared[i] = 0;` when it un-shares, so a SECOND BREAK on a record the first one copied takes the false branch. Measured in the reduction's own C with two counters spliced into a COPY of it (.temp/t161/red_probe/probe.py, 20 000 random op streams at SLB_HARDEN=1): records born shared 215579, records born owned 0, guard TRUE 67195, guard FALSE 30263 -- 31.1% of 97 458 evaluations. ⚠ What IS true of the reduction AS SHIPPED is that its two blobs evaluate the guard ONCE between them and it is TRUE that once, so the demonstration never exercised the false branch even though the program can. THE PRECISE DEFECT IS *no record is ever born owned*, NOT *the guard cannot fire*, and the two would need different repairs. THE FIX IS THAT THE CONTENT WIDTH IS DERIVED FROM THE INPUT: `w = 1 + a % MAXW` with MAXW = 6 against THRESH = 4, so three of six widths intern and three do not. controls/threshold.py measures both configurations on the SAME 20 000 random op streams: shipped 90476 intern / 89409 own / 87760 records born owned / guard 33373 TRUE and 64127 FALSE of which 48033 on a record BORN owned; reduction 180834 intern / 0 own / 0 born owned / guard 65973 TRUE and 31527 FALSE of which 0 on a record born owned. ⚠⚠ AND THE FIX WAS NOT SMALL, WHICH THE TASK FILE ASSERTED: a variable width turns three of the kernel's operations into loops over `w`, and at R5 each needs a recursive spec function, a loop invariant and -- for the copy -- an INDUCTION LEMMA. NOTES.md 8 has the counts. THE SAFETY LINE IS `cow` AND IT IS NOT THE UPSTREAM PATCH. Upstream's fix (commit 644a89e) changes the PROVENANCE -- never borrow, always own -- which deletes the deduplication, and TASK_160 measured that it CHANGES A BENIGN OBSERVABLE on the port (`10 passed, 0 failed` becomes `9 passed, 1 failed`; `\"interned\":true` becomes `false`) while copy-on-write is byte-identical to the bug on benign input. The same is true here and it is MEASURED rather than inherited (controls/spellings.py), because this kernel's epilogue folds `rshd[t]` beside each record's content -- which is the reduction of the port's `\"interned\"` API field, and which is also what keeps `rshd[]` LIVE in R1 so that the R1-vs-R1h gradient prices the check rather than the bookkeeping. ⚠ AN UPSTREAM PATCH IS NOT AUTOMATICALLY A SAFETY LINE; CHECK IT AGAINST THE BENIGN OBSERVABLE. ⚠ THE REPAIR CAN REFUSE, AND THAT IS THE HONEST PRICE OF COPY-ON-WRITE. Un-sharing needs storage the bug does not need; with the private region exhausted R1h folds SENT and does not write at all. Still memory-safe, still value-safe, and one behaviour the buggy rung does not have. adversarial-cowfull.bin fires it and NOTES.md 3c prices it. A REPAIR THAT CONSUMES A RESOURCE CAN RUN OUT OF IT, and nothing else in this tree says so. ⚠⚠ NOTHING IS FREED, EVERY INDEX IS IN BOUNDS, AND EVERY DETECTOR IS SILENT ON EVERY INPUT INCLUDING THE ADVERSARIAL ONES. c/kernel.h proves the index claim in four lines. So model.py's `sanitizer_expect` is DECLARED `clean` rather than derived -- .memory/03-measurement.md entry 19: DECLARING IS HONEST, a derivation that cannot fire is not -- and THE CHECKSUM IS THE ONLY INSTRUMENT THIS ROW HAS. That makes controls/detectors.py's positive controls load-bearing here in a way they are not elsewhere: on a row where every column is silent, a control that FIRES is the only thing separating `silent` from `not linked in`. ✅ It is the exact INVERSE of p34's detector-only cell, where the checksums are bit-identical and ASan is the only discriminator; the two rows bracket which instrument sees the harm from opposite ends. What model.py DOES derive is a different question -- what did the write REACH -- answered by Detector over two integer lists, and detector_selftest() exhibits three probes on which it answers three different ways, including an INTERNED record that no other record names. NO BENIGN INPUT MAY BREAK A SHARED RECORD, AND IT IS ENFORCED IN THREE PLACES RATHER THAN ASSUMED: inputs/gen.py cannot emit one, model.py::no_share_break_problems re-derives it from the SHIPPED blob every gate run, and controls/no_share_break.py censuses the directory. ⚠ The divergence is not only the corrupted byte -- R1h's copy-on-write also spends private storage and clears the ownership flag, and the epilogue folds that flag -- so the property is stated about the FLAG and not about the corruption. ⚠ UNLIKE p34, p49's SAFETY LINE DOES EXECUTE ON EVERY BENIGN BREAK THAT NAMES A RECORD: the guard is evaluated 1437 times on large.bin, 34 on small.bin and 2 on degenerate.bin, and is FALSE every time. (A BREAK with `nrec == 0` folds SENT before reaching the guard, which is why degenerate.bin executes 3 BREAKs and evaluates the guard twice.) So p49 has a real, non-zero benign cost gradient where p34's is 0.00, and NOTES.md 4 reports it at BOTH optimisation levels on BOTH compilers. SAFE RUST OFFERS BOTH THE BUG AND THE REPAIR, AND WHICH ONE YOU GET IS A CHOICE OF CONTAINER. CLAUDE.md rule 6 names *safe Rust reproduces the bug bit-identically* as a FINDING, and here it is the finding. controls/safe_arms.py builds three ports: the INDEX ARENA shipped as R2/R3, where the alias is a `usize` and the borrow checker has nothing to say -- controls/rust_bug.py writes the buggy rung in SAFE Rust with no `unsafe` anywhere -- MEASURED at ZERO unsafe tokens; `Rc<RefCell<Buf>>`, an idiomatic shared mutable buffer that reproduces c/kernel.c bit for bit on all nine inputs, safely, because there is only ever one borrow at a time; and `Rc<Buf>` with `Rc::make_mut`, which reproduces c/kernel_hardened.c bit for bit on all nine and where THE SAFETY LINE IS THE STANDARD LIBRARY'S because make_mut IS copy-on-write. ⚠ THE TWO Rc ARMS DIFFER IN ONE TYPE: `Buf` carries the width as a field in both. Only the third rules the bug out, and it does it with an API choice rather than with the type system. ⚠ That is the OPPOSITE of p34, where safe Rust cannot express the bug at all. The index arena is shipped because it is the one representation all seven rungs can share, so the ladder compares like with like and the Rc arms are priced beside it. WHAT THE R5 PROVES AND WHAT IT DOES NOT. ⚠⚠ copy_bytes CARRIES `requires src + w <= dst`, A DISJOINTNESS / PROVENANCE PRECONDITION, AND TASK_160 §8 PREDICTED THAT NOTHING IN THIS TREE STATES ONE. It is discharged out of wf_prov, the loop invariant that a SHARED buffer lives wholly inside the interning arena while the private bump is at or above it. ⚠ The `ensures` deliberately does NOT say *no record's content aliases another's*, because that is FALSE BY DESIGN: deduplication is the contract, and the abstract machine `run` shares buffers exactly where the kernel does. Saying it the other way round would be the easy mistake and it would specify a different program. ⚠⚠ AND THE SAFETY LINE ITSELF IS DISCHARGED AS AN ORDINARY FUNCTIONAL POSTCONDITION, WHICH IS p32's FINDING IN A DIFFERENT CURRENCY: both arms of `if rshd[t] == 1` type-check without the test, every index is in range either way, and no permission is consumed anywhere in the kernel -- what fails without it is that the loop stops computing `run`. LINEARITY HAS NOTHING TO SAY ABOUT THIS BUG, BECAUSE THE BUG DOES NOT TOUCH AN ALLOCATION. controls/proof_mutants.py is the battery -- an ATTACK arm that deletes the safety line from the exec code, a VACUITY arm, an X1 arm that strikes wf_prov's shared-buffer clause, and a SPEC-WEAKEN arm -- that says so rather than asserting it. TCB IS FIVE ITEMS, TWO FEWER THAN p27's AND p29's SEVEN, and the reason is the same fact: p49 allocates nothing, so there is no vstd::raw_ptr::allocate/deallocate pair to trust. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream (`chunks_exact(2).take(nops)` against R2's cursor), how it spells the opcode (`match c % 4` against an `if` chain), how it spells the dedup lookup (`iter().zip().position()` against an indexed `while`) and how it spells the three byte loops (slice iterators and `copy_within` against explicit `while`s) -- exactly as p32 leaves its handle-register spelling unpinned, p34 its op walk and p14 its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 5 reports what it moves. ⚠ `copy_within` IS memmove, and on this row of all rows that is worth saying out loud: it is CORRECT under overlap, which is exactly the difference from p08, where the choice between memcpy and memmove is a CORRECTNESS decision and not a tuning one. Here it is a tuning decision because the ranges cannot overlap. ⚠ THE `forbidden` LIST PINS THE ABSENCE OF AN ALLOCATOR: malloc/calloc/realloc/free, std::alloc, vstd::raw_ptr, Box and friends are all excluded, because *nothing is ever allocated or freed* is what makes every detector silent and is therefore the row's headline rather than an incidental fact. `Rc<` and `RefCell` are forbidden in the SHIPPED rungs for the mirror-image reason p34 REQUIRES them: on p34 the library IS the comparison, and here it would move the storage decision into a library and stop the seven rungs sharing one representation -- the Rc ports live in controls/safe_arms.py, where they are the measurement. memcpy/memmove/memset are forbidden so that no C rung can acquire a bulk copy the p08 distinction turns on. ⚠ THAT PIN IS ABOUT SOURCE SPELLINGS AND NOT ABOUT THE OBJECT, AND SAYING SO MATTERS ON THIS ROW: safe_tuned.rs's copy_within LOWERS TO memmove@GLIBC_2.2.5, which the gate's own stage-3a bulk-call column prints for the safe_tuned cells -- so the forbidden list says no rung WRITES a bulk copy, not that no rung CALLS one, and what decides the p08 question is the RANGES, which controls/no_overlap.py measures. The arrays are zero-initialised with `= { 0 }` rather than memset for the same reason p08 memsets its scratch -- so that the initialisation is a uniform per-call constant in all seven rungs and cancels in every rung-to-rung comparison. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 34
    },
    "twin_obligations": {
      "verus.rs": 37
    },
    "obligations_note": "34 = one Verus query per function plus one per loop body. MEASURED, not predicted: `./verus_run.py patterns/p49-interned-pool/verus.rs` reports `34 verified, 0 errors`. ⚠ It is the largest count in the tree (p32 15, p28 23, p25 10) and the reason is the CONTENT WIDTH: a variable-width string pool needs four verified helper loops -- find, fill, copy_bytes, fold_bytes -- where p32's every operation is O(1) straight-line code, plus three recursive spec functions and two induction lemmas to give those loops postconditions. NOTES.md 8 counts what that cost against the constant-width reduction, which is the version this row was admitted on.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **34 shipped + 3**, one per trusted item inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked and slb_twin_arr_set_unchecked. **EVERY trusted item here has a twin and none is blocked**, which is p27's, p32's and p34's position and not p35's. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth, p32 the seventh and p49 the eighth."
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
        "width_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "key_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cbyte_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "filled": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "copied": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "folded": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "find_from": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_sizes": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_prov": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_recs": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "st0": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "intern_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_find": {
          "external": null,
          "requires": [
            "0 <= k <= n"
          ],
          "ensures": [
            "k <= find_from(ek, el, k, n, key, w) <= n",
            "find_from(ek, el, k, n, key, w) < n ==> ek[find_from(ek, el, k, n, key, w)] == key",
            "find_from(ek, el, k, n, key, w) < n ==> el[find_from(ek, el, k, n, key, w)] == w"
          ]
        },
        "lemma_rec_in_pool": {
          "external": null,
          "requires": [
            "wf(st)",
            "0 <= t < st.nrec"
          ],
          "ensures": [
            "1 <= st.rlen[t] as int <= MAXW as int",
            "(st.roff[t] as int) + (st.rlen[t] as int) <= MEM as int",
            "st.rshd[t] == 1u8 ==> (st.roff[t] as int) + (st.rlen[t] as int) <= ARENA as int"
          ]
        },
        "lemma_copied_below": {
          "external": null,
          "requires": [
            "0 <= w",
            "0 <= i < dst"
          ],
          "ensures": [
            "copied(m, dst, src, w)[i] == m[i]",
            "copied(m, dst, src, w).len() == m.len()"
          ]
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
        "cbyte": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == cbyte_of(key, j)"
          ]
        },
        "find": {
          "external": null,
          "requires": [
            "nent <= NENT"
          ],
          "ensures": [
            "r as int == find_from(ekey@, elen@, 0, nent as int, key, w)",
            "r <= nent"
          ]
        },
        "fill": {
          "external": null,
          "requires": [
            "base + w <= MEM"
          ],
          "ensures": [
            "final(mem)@ == filled(old(mem)@, base as int, key, w as int)"
          ]
        },
        "copy_bytes": {
          "external": null,
          "requires": [
            "src + w <= dst",
            "dst + w <= MEM"
          ],
          "ensures": [
            "final(mem)@ == copied(old(mem)@, dst as int, src as int, w as int)"
          ]
        },
        "fold_bytes": {
          "external": null,
          "requires": [
            "base + w <= MEM"
          ],
          "ensures": [
            "r == folded(mem@, base as int, w as int, acc)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == intern_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p32's, p34's, p25's, p16's, p05's, p11's, p12's, p06's and p14's denominator. WHICH WAY THE ESTIMATE ERRS: STRICT. It OVER-counts by the 4 window-header bytes, which are decoded as a u32 and are not operations. It UNDER-counts by everything else: each 2 window bytes is one OPERATION, and every operation does two moduli, a compare chain and a multiply-add, while an interning DEFINE also SCANS the dedup table (up to NENT two-field comparisons) and materialises up to MAXW bytes, a READ folds up to MAXW bytes, and the epilogue folds every one of up to NREC records. ⚠ p49's under-count is BOUNDED where p34's is not: no operation can do more than NENT comparisons plus MAXW byte moves, and the epilogue is at most NREC * MAXW bytes whatever the input, so no op stream can make the estimate arbitrarily loose. model.py declares NO min_ir_per_work, so the harness default of 0.25 Ir per byte applies unchanged and what it catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing. The two probe inputs differ in work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5 by RAW MACHINE-CODE BYTES at `-O3` (`md5_raw 563ecf2f9431db3c9ec8963b5ccd5c62` on both binaries, 439 non-pad instructions, 1822 bytes) and identical up to pc-relative displacement fields at `-O0` (`md5_raw_norel bdab100e3517b0c56fc510117d7bac7a`, `md5_norm 06e8fe436c25b756ace6c640a5fad7ac`, 665 non-pad instructions and 3739 bytes on both). ⚠⚠ That is p32's pin exactly and STRONGER than p25's and p29's, and the reason is the pattern rather than the effort: p49 has no pointer write, no allocation and no vstd call in the kernel at all -- the trusted items are three `get_unchecked` wrappers, all `#[inline(always)]` and all identical between the two files -- so there is nothing for the two rungs to spell differently. ⚠ The four verified helpers `find`, `fill`, `copy_bytes` and `fold_bytes` are `#[inline(always)]` in BOTH files and carry contracts in only one; the contracts erase, which is why adding them costs zero instructions. The `-O0` residue is link layout: the crate names differ in length, so the pc-relative displacements do. The proof licenses the unsafe code at zero instruction cost, which is this project's standing R4/R5 result."
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
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. p49 has five, so Miri runs. ⚠⚠ **And note what Miri finds, because it is this row's headline and not a gap in the run: NOTHING, ON ANY INPUT, INCLUDING ALL FIVE ADVERSARIAL ONES.** The pool is a local array alive for the whole call; the buggy rung's every index is in range; nothing is allocated, so nothing can be used after being freed. **Miri is an instrument about ALLOCATIONS and p49 has none.** What Miri still buys here is what it buys on p08 and p32: a trusted body that read one element past an array would satisfy every `ensures` in verus.rs and be invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req. Cost: check.py rewrites n_iters to 4, and this kernel makes no allocator call at all, so the rows are cheap.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
