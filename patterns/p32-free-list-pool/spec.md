# p32 -- free-list allocator / object pool with recycling

**`p32` and `p33` of `.memory/06-catalogue.md` are ONE ROW with TWO ARMS**, and
this is it. One C mechanism, one omitted conjunct, and the input picks the harm:
`p32`'s double-free-into-aliasing arm and `p33`'s use-after-recycle arm.
`c/kernel.h` carries the kernel contract in pseudocode; this file carries the
reasoning and the machine-readable pins. `README.md` says the same thing for a
reader who has not read either.

⚠⚠⚠ **WHY THIS ROW EXISTS, BECAUSE IT IS NOT WHAT A READER WILL
GUESS.** It exists because the ADMISSION BAR WAS CORRECTED (`CLAUDE.md` rule 6,
`.memory/02-bench-rules.md` *THE ADMISSION BAR IS C-SIDE ONLY*, RECAP findings
53 and 54). It was refused twice on the sentence *"safe Rust reproduces the
buggy C bit for bit"*, and that sentence is TRUE, is REPRODUCED here, and is
**the row's headline rather than a defect**. `controls/storage_arms.py` measures
it on four inputs. Nothing the Rust or the Verus rungs do can shrink or retire
this row.

## The bug, in one paragraph

A pool of fixed-size blocks with a LIFO free list. A block is neither `malloc`'d
nor `free`d per use -- it is POPPED and PUSHED -- so **the storage belongs to the
program from the first instruction to the last**. A handle is a
`(slot, generation)` pair that ALLOC issues into a handle register; `gen[h]` is
slot `h`'s incarnation and every FREE bumps it. FREE, READ and WRITE all consume
the handle in the register the file names, and they share one guard. R1 asks only
whether the register holds a handle at all:

| what the input does with a stale handle | what R1 does |
|---|---|
| FREE it again | pushes the block a SECOND time. `nx[h] = freehead` with `freehead == h` **self-loops the list**, so every later ALLOC returns the SAME slot: **two live handles alias one block** and the rest of the list is lost |
| READ it | returns the **new occupant's** payload -- an in-bounds read of a live array whose tenant changed |

One omitted line, two bug classes, selected by the input. That is `p29`'s shipped
shape on a mechanism `p29` does not have.

## ⚠⚠ The C-mechanism distinction, stated first because a reviewer will attack it first

```
p27   individually malloc'd records; `live[h]` consulted on the FREE path, so it
      CANNOT double-free; no free list, no recycling, no generation. Its stale
      read dereferences a DANGLING POINTER.
p29   a real `free()` of a whole record and a stale ADDRESS held across it. Its
      recycle half re-occupies a LIVE allocation, which is the closest either
      built row comes.
p32   NOTHING IS ALLOCATED AND NOTHING IS FREED. The harm is ALIASING -- two
      live handles naming one block, produced by a self-looping intrusive free
      list -- and neither built row can produce it.
```

**The aliasing harm has no analogue in `p27` or `p29`.** `p27` keeps a liveness
bit and checks it before freeing, so a second FREE of the same handle is a no-op;
`p29` never recycles a slot at all (`ntab` only grows), so no handle can ever
name a different tenant of the same slot. `p32` recycles by construction, and
recycling is what a free-list allocator is for.

## What the safety line has to notice, and why no detector notices it

```
p27   if (h < ntab && live[h] == 1)              is the ALLOCATION there?
p29   if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)
                             ^ allocation there?   ^ same occupant?
p32   if (h == NIL) ... else if (gen[h] != g)
           ^ does the register    ^ is this block still the SAME INCARNATION?
             hold a handle?         THERE IS NO ALLOCATION TO ASK ABOUT.
```

`p27`'s and `p29`'s first conjunct is a question about an allocation, and safe
Rust answers it for them: `tab[i] = None` frees the record and invalidates the
slot in one operation, so the `Option` discriminant IS the liveness bit. **p32
has no allocation anywhere**, so:

* **ASan, UBSan and Miri are silent on every input**, adversarial ones included,
  and `model.py` DERIVES the spatial half of that rather than declaring it -- its
  simulation carries a handle through the index path as the RUNGS carry it, a
  slot or the `NIL` sentinel 255, and touches every index R1 forms from one:
  `gen[h]`, `nx[h]`, `pool[h*BLK]`, `pool[h*BLK+1]`, on ALLOC's `freehead` side
  as well. None escapes. ⚠ **And that check is one that CAN fire**:
  `model.py::detector_selftest()` deletes each `NIL` guard in turn and the
  detector reports `fires`, and `selfcheck()` runs it on every gate invocation.
  ⚠⚠ **Until `TASK_147` it could NOT fire** -- the guard tested `0 <= s < SLOTS`
  of a number drawn from `range(SLOTS)`, and the one case that would have set it
  crashed the model first (`TASK_145_REPORT` §4b, `NOTES.md` 11). The verdict did
  not move; the evidence for it did.
* **safe Rust gives you nothing.** `Option<(u8, u32)>` in `safe_tuned.rs` writes
  the `h == NIL` half; the generation half is written out by hand in all four
  Rust rungs, in the most idiomatic spelling available.
* **the R5 has no linear resource to consume.** See `NOTES.md` 6b.

⚠ `controls/storage_arms.py` is the other cell of the experiment: the same
algorithm with per-block `malloc`/`free` storage, everything else held
byte-identical. Two of the three harms become an ASan `heap-use-after-free` and
an `attempting double-free`; the use-after-RECYCLE one stays bit-identical and
silent in both. **That is a controlled two-cell measurement of detector coverage,
not an anecdote.**

## Why the hardened rung is CORRECT, and why the file names a REGISTER

Admission question 1 asks the C kernel to be correct on benign inputs, so R1h has
to be genuinely correct and not merely better. It is, and the invariant is:

> for every handle register `r` with `regs[r] = h != NIL` and `regg[r] == gen[h]`,
> **slot `h` is not on the free list**

preserved because ALLOC removes `s` from the list before issuing `(s, gen[s])`
-- and no register could already hold that pair, since `s` was on the list -- and
because FREE pushes only a slot the invariant says is off the list and then bumps
`gen[h]` to a value that has never been issued. **So R1h can neither double-push
nor alias.**

⚠⚠ **This is why the file names a handle REGISTER and never a slot or a
generation.** `NOTES.md` 1b measures the alternative: with a file-supplied
`(slot, generation)` byte the attacker can always spell the CURRENT incarnation
of a block that is already free, and **the hardened kernel self-loops its own
free list on an input of five operations**. That variant is not a harder version
of this row, it is a broken R1h. `p29`'s corrected sentence is the rule --
*a file cannot name a pointer, but it CAN name an operation that saves one* --
and ALLOC is that operation.

⚠⚠⚠ **THE R5 DOES NOT PROVE THE INVARIANT ABOVE AND DOES NOT NEED
TO.** It is not required for memory safety (every index is in range without it)
and it is not required for the functional `ensures` (the abstract machine models
a self-looping list perfectly happily). `NOTES.md` 6b states what that means and
`controls/proof_mutants.py` demonstrates it with three arms rather than asserting
it.

## Why the generation is `u32` and wraps

`gen[h]` is bumped once per FREE of slot `h`, and a window holds `(len - 4) / 2`
operations; the largest window this pattern ships is 244 bytes. A wrap needs 2^32
frees of ONE slot inside ONE window. Both C rungs, all four Rust rungs, `model.py`
and the Verus spec all wrap, so they agree by construction rather than by the size
of the inputs -- which is the only reason the wrap is worth mentioning.

## Why every benign window must use only a handle that is still current

`inputs/gen.py` checks it, by running a copy of the checked kernel over every
window of every blob it emits, and `harness/check.py` stage 2 requires every
non-adversarial cell to agree with `model.py` and with every other cell. Both bug
classes therefore live on the `adversarial-*` rows alone, whose behaviour the gate
**records** per cell instead of requiring agreement.

⚠ **What is NOT a reason here, and it is `p27`'s and `p29`'s first reason:**
p32's R1 checksum is REPRODUCIBLE. The pool is a local array with no heap address
anywhere in the answer, so R1 prints one distinct value in twenty runs on every
adversarial input (`NOTES.md` 2d). p32's adversarial rows are excluded from the
agreement set because they DISAGREE, not because they are unstable.

## The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop calls
`kernel(buf, k * stride, stride)`. `driver.call_args` declares which argument
*positions* of a named call are the canonical ones. **This is p14's pin
unchanged**, inherited through p27 and p29; p32 adds no new declaration surface.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts and
what the identity pin is measuring.

| pin | why |
|---|---|
| `verus.obligations` = 15 | **6 consts + 1 recursive spec fn (`run`) + kernel 3 + main 5.** Every function term was measured with `--verify-function <name> --verify-root`; `.temp/t144/verus/obligations.log` is the census. ⚠ There is no `struct`/`derive` term: p32's only datatype is the ghost `St`, and a bare `struct` carries ZERO. |
| `verus.twin_obligations` = 18 | the count under `--cfg slb_twin`. **15 shipped + 3**, one per trusted item inside the twin regime. ⚠⚠ **p27 and p29 owe FIVE twins and p32 owes THREE**, and the two it does not owe are `vstd::raw_ptr::allocate` and `deallocate` -- because it does not allocate. |
| `identity` `O3: exact`, `O0: norel` | **stronger than p29's `norel`/`differ`, and the reason is the pattern.** There is no pointer write in this kernel and no vstd call, so R4 and R5 have nothing to spell differently. See the pin's `why`. |
| `miri.required: true` | derived from the trusted items, and ⚠⚠ **what Miri finds is NOTHING, on every input including all six adversarial ones** -- which is the row's detector-coverage result rather than a gap in the run. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == pool_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (pool_fold). p32's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27 and p29 use and NOT p02's before/after set: p32's pool is a LOCAL of the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by ONE conjunct at the ONE site where a handle is consumed** -- `gen[h] != g` in C and in all four Rust rungs, since FREE, READ and WRITE share the handle decode -- and at R5 it is discharged as an ORDINARY FUNCTIONAL POSTCONDITION. ⚠⚠ **That is the row's R5 result and it is the opposite of p27's and p29's**: there is no `PointsTo` to consume, no `Dealloc` token and no precondition that forces the conjunct's presence, because nothing in this pattern is ever allocated or freed. The proof fails without the conjunct only because the postcondition stops holding -- the same way it would fail if the fold multiplied by 32. NOTES.md 6b measures what that means and controls/proof_mutants.py demonstrates it: the ATTACK arm (delete the conjunct) fails, the VACUITY arm (a constant body) fails, and the SPEC-WEAKEN arm (delete the conjunct from `step` as well) VERIFIES, which is the honest statement of what this R5 buys. **The `ensures` is the FUNCTIONAL one**: `run` is an abstract machine carrying the pool bytes, the intrusive free list, the per-slot generations and both handle-register sequences, and it says the accumulator is what that machine computes -- so a kernel that folded a recycled block's payload, or that pushed a block twice, or that truncated at a different SLOTS, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest, that the op stream is well formed, or that the free list is a set of distinct slots.** `run` specifies what the PROGRAM does -- stop when the window runs out, fold SENT for an ALLOC from an exhausted pool, fold SENT for an empty register, fold SENT for a stale handle -- so degenerate.bin and all six adversarial op-stream files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that the op stream never staled a handle would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: ONE conjunct at the ONE site where a handle is consumed, `} else if (gen[h] != g) {` in c/kernel_hardened.c. c/kernel.c goes straight from `if (h == NIL) {` to the opcode arms and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct. FREE, READ and WRITE share the decode, which is why one omitted line carries both bug classes.",
        "rust": "THE SAFETY LINE, in all four Rust rungs. `gen[h as usize] != g` in safe_naive.rs, `gen[h] != g` in safe_tuned.rs, and `arr_get_unchecked(&gen, h as usize) != g` in unsafe.rs and verus.rs -- the operand is the same, the accessor is what each rung forces. ⚠ **Not one of the four gets any part of it from the language.** safe_tuned.rs's `Option<(u8, u32)>` writes the `h == NIL` half for you, which is p29's `is_some()`; the generation half is written out by hand in every rung, because nothing in the type system knows that a live range of bytes has changed occupant. See the why key."
      },
      {
        "c": "THE HANDLE IS ISSUED BY ALLOC AND NAMED BY REGISTER, in both C rungs: `r = (size_t)(a % NREG);`. The file names the register; ALLOC writes `regs[r]` and `regg[r]`. This is what makes the generation unforgeable -- see the why key, which measures the alternative.",
        "rust": "the same, in all four Rust rungs: `let r: usize = (a % NREG as u8) as usize;`."
      },
      {
        "c": "THE GENERATION IS BUMPED BY EVERY FREE, IN BOTH C RUNGS: `gen[h] = gen[h] + 1;`. R1's bug is NOT that it skips this -- it does not -- it is that its handle-consuming path never asks. Splitting the bump from the check is what makes forgetting possible at all.",
        "rust": "the same bump in all four Rust rungs, spelled `wrapping_add(1)` because `-C debug-assertions=on` would otherwise panic and C wraps by definition."
      },
      {
        "c": "THE FREE LIST IS INTRUSIVE AND LIFO, in both C rungs: `nx[h] = freehead;` followed by `freehead = h;`. It is the intrusive spelling that makes the double push a SELF-LOOP rather than a duplicate entry, and the self-loop is what produces the aliasing.",
        "rust": "the same push in all four Rust rungs: `nx[h as usize] = freehead;` in safe_naive.rs, `nx[h] = freehead;` in safe_tuned.rs, `arr_set_unchecked(&mut nx, h as usize, freehead)` in unsafe.rs and verus.rs."
      },
      "THE HANDLE REGISTER IS NOT CLEARED ON THE FREE, in all seven rungs. Nothing writes `regs[]`/`regg[]`/`reg[]` except ALLOC. See the why key for why clearing it would be a different bug class.",
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, in all four Rust rungs: `c % 4 == 0`."
      },
      {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `v = SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: `SENT`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc = acc.wrapping_mul(31).wrapping_add(v);`."
      },
      {
        "c": "the ALLOC count is folded last, so a rung that served a different number of allocations cannot produce the same checksum -- which is what puts the SELF-LOOPED free list in the answer: `return acc * 31 + (uint64_t)nalloc;` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nalloc as u64)`."
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
      "`Box::into_raw`",
      "`Box::leak`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Rc<`",
      "`RefCell`",
      "`Vec::with_capacity`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens below must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. A FREE through a handle whose block has been recycled pushes that block onto the free list a SECOND time; `nx[h] = freehead` with `freehead == h` SELF-LOOPS the list, every later ALLOC returns the same slot, TWO LIVE HANDLES ALIAS ONE BLOCK and the rest of the list is lost. A READ through such a handle returns the NEW OCCUPANT's payload. Which harm the input gets is chosen by whether it frees again or reads again, and the omitted conjunct is the same one. THE ALIASING HARM HAS NO ANALOGUE IN p27 OR p29 AND THAT IS WHY THIS IS A ROW: p27 consults `live[h]` on its FREE path so it cannot double-free at all, has no free list, no recycling and no generation; p29 frees a record with a real `free()` and holds a stale ADDRESS. Neither can produce two live handles naming one block. NOTHING IS ALLOCATED AND NOTHING IS FREED, IN ANY RUNG, AND THAT IS THE POINT RATHER THAN A SIMPLIFICATION. The pool is a local array alive for the whole call, which is what a free-list allocator IS. Its consequence is that R1 executes NO undefined behaviour -- `regs[r]` is NIL or a real slot, `freehead` is NIL or a real slot, `nx[]` holds only values drawn from those two -- so ASan, UBSan and Miri are silent on every input this pattern ships, while the answer is WRONG on four of them and two handles alias on two of them. `model.py` DERIVES the spatial half of that silence rather than declaring it, AND THE CHECK IS ONE THAT CAN FIRE: its simulation carries a handle through the index path AS THE RUNGS CARRY IT -- a slot number or the NIL sentinel 255 -- and touches every index R1 forms from one, `gen[h]`, `nx[h]`, `pool[h*BLK]` and `pool[h*BLK+1]`, on ALLOC's `freehead` side as well as on FREE/READ/WRITE's; `model.py::detector_selftest()` deletes each of the two NIL guards in turn and the detector reports `fires`, and `selfcheck()` runs that arm on every gate invocation. CORRECTED AT TASK_147, AND THE OLD SENTENCE IS RETRACTED RATHER THAN QUIETLY REPLACED: until then this read `its simulation computes every index the buggy rung would compute and reports whether one escapes`, and TASK_145_REPORT 4b measured that false four ways -- the guard `0 <= s < SLOTS` was a TAUTOLOGY of the simulation's own representation with 0 firings in 20 000 fuzzed buggy windows, the one case that would have set it crashed the model with IndexError before the flag was read, `gen[h]`/`nx[h]`/`regs[r]` were not indexes that simulation computed at all, and M3-nil-test's failure mode was unrepresentable because an empty register was None rather than slot 255. THE CONCLUSION WAS AND IS TRUE; WHAT WAS FALSE WAS THAT model.py ESTABLISHED IT. The same 20 000-window sweep now fires 19 622 times with the `h == NIL` test deleted and 0 times with both guards present (NOTES.md 11). `controls/storage_arms.py` is the other cell of the experiment -- the same algorithm with per-block `malloc`/`free` storage -- and it is what makes this a controlled two-cell measurement of DETECTOR COVERAGE rather than an anecdote. That is why `malloc(`, `free(`, `std::alloc::` and `vstd::raw_ptr::` are forbidden here: a rung that allocated would be measuring a different pattern, and `Box::new`, `Rc<`, `RefCell` and `Vec::with_capacity` are forbidden for p29's reason as well -- they would move the liveness decision into a library and delete the comparison. THE FILE NAMES A HANDLE REGISTER, NEVER A SLOT AND NEVER A GENERATION, AND THAT IS LOAD-BEARING RATHER THAN PRESENTATIONAL. It is p29's corrected sentence -- a file cannot name a pointer, but it CAN name an operation that saves one -- and here it is what makes the generation UNFORGEABLE. Measured (NOTES.md 1b): with a file-supplied `(slot, generation)` byte the attacker can always spell the CURRENT incarnation of a block that is already on the free list, so the HARDENED kernel self-loops its own free list on an input of five operations -- FIVE, corrected at TASK_147 from `four`, which contradicted NOTES.md 1b, README.md, c/kernel.h and the control's own `op0..op4` transcript (TASK_145_REPORT 8). That variant is not a harder version of this row, it is a broken R1h, and admission question 1 asks the C kernel to be correct. `regs[r]` IS DELIBERATELY NOT CLEARED ON THE FREE, and it is p27's and p29's reason: clearing it would turn every stale use into the `h == NIL` case, which folds SENT in BOTH rungs -- a defined operation and a different bug class. Splitting the release from the invalidation is what makes forgetting possible at all. THE GENERATION IS `u32` AND IT WRAPS. `gen[h]` is bumped once per FREE of slot `h` and a window holds `(len - 4) / 2` operations, so a wrap needs 2^32 frees of one slot inside one window; the largest window this pattern ships is 244 bytes. Both C rungs, all four Rust rungs, `model.py` and the Verus spec all wrap, so they agree by construction and not by the size of the inputs. WHAT IS DELIBERATELY NOT PINNED is how the handle register is SPELLED in the safe rungs -- a NIL-sentinel pair of parallel arrays in R2, `Option<(u8, u32)>` in R3 -- exactly as p14 leaves its fold loop unpinned and p29 leaves its liveness half. Those are the R3-side levers, they cost zero TCB, and THIS PATTERN PUBLISHES NO RUNG-TO-RUNG COST AT ALL (NOTES.md 8), so no spread is being reported as a number and the absence is stated rather than left to read as a zero. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 15
    },
    "twin_obligations": {
      "verus.rs": 18
    },
    "obligations_note": "15 = SIX consts (SLOTS, BLK, POOLSZ, NREG, NIL, SENT) 1 each + run 1 + kernel 3 + main 5. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`; the loop is `.temp/t144/verus/obligations.sh` and the log is `.temp/t144/verus/obligations.log`. The zero terms are checkable the same way: u32_at, nops_at, val_of, written, wf_ranges, step, st0 and pool_fold are NON-RECURSIVE spec fns and report 0, while `run` is RECURSIVE and carries one termination query; buf_get_unchecked, arr_get_unchecked, arr_set_unchecked, load_input and emit are external_body and report 0. FOUR of the six consts are the ones p29 also has; POOLSZ and BLK are p32's (`.memory/04-verus.md`: a const inside verus! is its own obligation). kernel's 3 = body + TWO loop bodies (the free-list initialisation and the op walk); main's 5 is quoted AS MEASURED. ⚠ **There is no `struct` and no `derive` term here.** p29's 25th obligation is the `#[derive(Clone, Copy)]` on its record; p32's only datatype is the GHOST `St`, which carries none -- a bare `struct` counts ZERO (TASK_140, measured eleven ways).",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **15 shipped + 3**, one per trusted item that is inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked and slb_twin_arr_set_unchecked. ⚠⚠ **p27 and p29 have FIVE twins and p32 has THREE, and the two missing ones are the whole difference between the rows**: `rec_alloc` and `rec_free`, i.e. `vstd::raw_ptr::allocate` and `deallocate`. p32 does not allocate, so it does not borrow those two items and does not owe those two twins -- and it also does not get the temporal argument they carry. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth and p32 the seventh."
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
        "written": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf_ranges": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "step": {
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
        "pool_fold": {
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
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == pool_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p16's, p05's, p11's, p12's, p06's and p14's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, and by about an order of magnitude rather than p27's two. It OVER-counts by the 4 window-header bytes, which are decoded as a u32 and are not operations. It UNDER-counts by everything else: each 2 window bytes is one OPERATION, and every operation does a modulo, two array reads, a compare, a branch and a multiply-add, while ALLOC and FREE also read-modify-write the free list. ⚠ **p32's under-count is SMALLER than p27's and p29's on purpose**: an operation here is O(1) with no allocator call and no inner loop, so the floor is tighter than on either built temporal row even though it is still strict. model.py declares NO min_ir_per_work, so the harness default applies unchanged. The two probe inputs differ in work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "exact",
      "why": "R4 == R5 by raw machine-code bytes at `-O3`, and identical up to pc-relative displacement fields at `-O0`. ⚠⚠ **This is a STRONGER pin than p29's `norel`/`differ`, and the reason is the pattern rather than the effort**: p29's pair diverges at `-O0` because its record write goes through vstd's `ptr_mut_write` on one side and a bare `*p = v` on the other, six instructions apart at five sites. p32 has no pointer write, no allocation and no vstd call in the kernel at all -- the only trusted items are three `get_unchecked` wrappers, all `#[inline(always)]` and all identical between the two files -- so there is nothing for the two rungs to spell differently. The `-O0` residue is link layout: the crate names differ in length, so the pc-relative displacements do."
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
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. p32 has three, so Miri runs. ⚠⚠ **And note what Miri finds, because it is this row's headline and not a gap in the run: NOTHING, ON ANY INPUT, INCLUDING ALL SIX ADVERSARIAL ONES.** The pool is a local array alive for the whole call; the buggy rung's every index is in range; nothing is allocated, so nothing can be used after being freed. Miri is an instrument about ALLOCATIONS and p32 has none. What Miri still buys here is what it buys on p08: a trusted body that read one element past an array would satisfy every `ensures` in verus.rs and be invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req. Cost: check.py rewrites n_iters to 4, and this kernel makes no allocator call at all, so the rows are cheap.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
