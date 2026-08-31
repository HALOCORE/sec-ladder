# p25 -- a dynamic array grown with `realloc`, and an interior pointer held across the growth

**CWE-416 (use after free) reached through CWE-825 (expired pointer
dereference).** The kernel parses an op stream into two growable byte vectors. It
saves an INTERIOR POINTER into the token vector, `cur = &toks[curi]`, keeps
parsing, and a later push grows the token vector with `realloc`. When the block
relocates, the old one is retired -- **the program never calls `free` on it,
`realloc` does** -- and the next `READ` dereferences a pointer into storage the
allocator has taken back. `c/kernel.c` omits the conjunct `curbase == toks` that
would ask. `c/kernel.h` carries the kernel contract in pseudocode; this file
carries the reasoning and the machine-readable pins; `README.md` says the same
thing for a reader who has read neither.

## Why this row exists, because it is not what a reader will guess

⚠⚠⚠ **THIS ROW WAS REFUSED AT `TASK_134` AND EVERY LIMB OF THAT REFUSAL WAS
DRIVER-ARTEFACT OR LADDER-SIDE.** *"In `p25`'s shipped heap topology `realloc`
never moves"* -- a fact about **that driver**, and `probe_move` puts it at
`24/48` once a second live allocation sits behind the first. *"There is no safety
conjunct to omit; the safety line here is an ADDRESSING MODE"* -- refuted by
`c/kernel_hardened.c`, whose diff against `c/kernel.c` is literally the conjunct
`curbase == toks`. *"Safe Rust makes the bug a compile error"* -- a **finding**,
and a weak one, because the error code is not distinguishing
(`controls/safe_arms.py` ships the negative control). **p25 as built was admitted
at `TASK_143` on the C-side bar (`CLAUDE.md` rule 6): the C program is correct on
benign inputs, exhibits a use-after-free on an adversarial one, and its C
mechanism is distinct from every built row's.** Nothing the Rust or Verus rungs
do can shrink or retire it -- and what they *do* do is this row's most
interesting result, not its weakness.

## The C-mechanism distinction, stated first because a reviewer will attack it first

```
p27  individually malloc'd records; an explicit free(); the READ does not ask
     whether the record is still live.                        Fix the READ.
p29  an explicit free() of a whole record and a stale ADDRESS held across it;
     the READ does not revalidate the occupant.               Fix the READ.
p32  nothing is allocated at all; a handle is not revalidated against the
     block's incarnation.                                     Fix the READ.
p34  an explicit free() driven by a refcount the ACQUIRE failed to raise; the
     read path is correct.                                    Fix the ACQUIRE.
p25  NO free() ANYWHERE EXCEPT THE EPILOGUE. `realloc` retires the block as a
     SIDE EFFECT OF GROWTH, and what is stale is an INTERIOR pointer into the
     middle of a container.                                   Fix the READ.
```

⚠ **`p34` is the sharpest attack on that and it is worth saying where it lands.**
Both rows read a retired block. `p34`'s block is retired by an explicit `free(o)`
that a reference count reaching zero selected, and its repair site is the
ACQUIRE; `p25` calls `free` on nothing but the two vectors at the end, the
retirement is `realloc`'s and is **not a decision the program makes at all**, and
its repair site is the READ. ✅ **Measured rather than asserted**
(`controls/no_reloc.py`, re-derived every run, with comments and string literals
blanked first): `realloc` is called by **exactly one** pattern's `c/` and it is
this one -- **1 of 32** -- and only **5 of 32** call `malloc` at all (p27, p28,
p29, p34, p42). ⚠ `.temp/mgr155/NOTES.md` §6 published *"p10 p27 p28 p29 p32
p42, 6 of 30"* from a raw grep: p10's and p32's hits are PROSE (p32's own
`kernel.h` says *"neither `malloc`'d nor `free`d per use"*) and p34, which
really does allocate, is missing. The load-bearing half is unaffected. **No
other built row has an allocation that MOVES while logically live, and none has
a stale INTERIOR pointer.** ⚠ `free` is called by 32 of 32 -- every `c/main.c`
frees the driver payload -- so *"calls `free`"* is not a distinguishing token and
the distinction has to be stated about the KERNEL, which it is.

## ⚠⚠ THE HARDENED CELL RE-DERIVES, AND THAT IS FORCED

The obvious hardened cell -- `if (curbase == toks) v = *cur; else v = SENT;` --
**cannot be shipped**, and the reason is not style:

> **It makes the kernel's ANSWER a function of the ALLOCATOR.** Whether `realloc`
> relocates is a heap-topology fact, so `model.py` could not derive the checksum
> without simulating glibc; and the four Rust rungs, whose `Vec` grows on a
> different schedule, could not agree with the C ones on the adversarial input.
> `harness/check.py` stage 2's *"every checked rung agrees with the model"* would
> be unsatisfiable in principle.

Re-deriving `toks[curi]` in the `else` branch makes the answer
**allocator-independent**, because `realloc` COPIES: `toks[curi]` after the move
is the byte `*cur` named before it. ⚠ **So the conjunct buys MEMORY SAFETY and
buys nothing else** -- both branches compute the same value in every terminating
execution -- which makes the R1-vs-R1h gradient a clean price for memory safety
alone. `NOTES.md` 3a has the safety-line measurement, 3c the price of both
repairs, and 2c the collision arithmetic the sentinel form would have owed.

⚠⚠ **AND THE CONJUNCT IS NOT THE STANDARD-CLEAN REPAIR, WHICH IS THIS ROW'S
SHARPEST C-SIDE FINDING.** C11 7.22.3.5p4 with DR 400 makes `cur` indeterminate
the moment `realloc` returns, **whether or not the block moved**, so the
surviving `*cur` in the true branch is a use of an indeterminate value under the
abstract machine even though no relocating allocator can observe it. The
standard-clean rung is the UNCONDITIONAL re-derive -- i.e. **the addressing-mode
change the old refusal named** -- and `controls/rederive.py` builds it and prices
it. **Both halves are findings: the conjunct exists (the old kill's first half is
refuted) and it is insufficient (the old kill's second half is vindicated for a
reason nobody had stated).**

## ⚠⚠ No benign input may go stale, and that is enforced in three places

**ASan's allocator moves on EVERY `realloc`.** A benign window that grew `toks`
after a SAVE and then read through `cur` would make R1 report
`heap-use-after-free` on a row whose `sanitizer_expect` is `clean`. So no
non-adversarial window may read through an interior pointer whose token vector
has been reallocated since the SAVE -- `inputs/gen.py` cannot emit one,
`model.py::stale_free_problems` re-derives the property from the SHIPPED blob on
every gate invocation, and `controls/no_stale.py` censuses the whole directory.

⚠ **Unlike p34, p25's safety line DOES execute on every benign input.** Every
`READ` evaluates `curbase == toks`; what no benign input does is take the `else`
branch. So p25 has a real, non-zero benign cost gradient where p34's is `0.00`,
and `NOTES.md` 4 reports it at both optimisation levels on both compilers.

## The harm window is ONE GROWTH wide

glibc's minimum chunk gives a 4-byte `malloc` 24 usable bytes, so `4 -> 8` and
`8 -> 16` are satisfied in place; it is `16 -> 32` that has to move, and only
because the string vector was allocated after the token vector and is still
live. **The adversarial windows are TUNED to that growth**, and saying
*"`realloc` moves"* without the qualification would mislead.
`controls/reloc_probe.py` measures which growth relocates under the shipped
driver rather than under a hand-rolled one, which is the mistake `TASK_134` made.

⚠ **ASan is therefore a BIASED instrument for this row and the result does not
rest on it.** The unbiased evidence is the plain-build divergence between R1 and
R1h; the ASan column is the conservative one. Both are reported separately in
`NOTES.md` 2.

## What each rung spells

| rung | the saved reference | the safety line |
|---|---|---|
| **R1** `c/kernel.c` | `const uint8_t *cur` + `curbase` + `curi`, and it consults neither of the last two | **absent** |
| **R1h** `c/kernel_hardened.c` | the same three | present: `} else if (curbase == toks) {` with a re-derive in the `else` |
| **R2** `safe_naive.rs` | `curi: usize` -- **an index, because safe Rust offers nothing else** | **it has no site**: `realloc` copies, so `toks[curi]` is correct by construction |
| **R3** `safe_tuned.rs` | the same | the same: none |
| **R4** `unsafe.rs` | the same index; the unchecked read is `vec_get_unchecked(&toks, curi)` | none |
| **R5** `verus.rs` | the same, with `have ==> curi < toks@.len()` in the loop invariant | none |

## The R5, and what is NOT there is the result

⚠⚠ **THE TEMPORAL OBLIGATION HAS NO ANALOGUE AT R5, BECAUSE NO RUNG ABOVE R1 CAN
HOLD THE STALE INTERIOR POINTER.** Writing `cur` in Rust needs a raw `*const u8`
dereferenced under `curbase == toks.as_ptr()`, and Verus cannot license it: the
read needs a `PointsTo` permission that no vstd API yields for a `Vec`'s buffer,
and the guard is an **address** comparison while Verus's pointers carry
PROVENANCE -- so the guard is exactly the fact the proof would need and exactly
the fact address equality does not give. What is left to prove is
`have ==> curi < toks@.len()`, a spatial obligation that is easy because a vector
only grows.

**So `p25` is the first row in this tree where the LADDER DELETES THE BUG above
R1 rather than making it provable, and the honest statement of the R5 result is
that its obligation is SMALLER than p27's, p29's, p32's or p34's.**
`controls/rust_bug.py` builds the R4 that *does* hold the pointer, so the claim
is measured; `controls/proof_mutants.py` is the four-cell battery that says the
remaining proof is not vacuous.

⚠ **`p25`'s R5 is also the first in this tree to call `Vec::push` in exec code**
-- measured, not assumed: no other `verus.rs` under `patterns/` contains an exec
`.push(` on a `Vec`. vstd's `assume_specification[Vec::push]` carries
`final(vec)@ == old(vec)@.push(value)` and **no `requires` at all**, so the
growth costs no trusted item; `group_vec_axioms` is what ties `vec.len()` to
`vec@.len()`, and no other pattern in the tree needs that group.

## The pins, and the arithmetic behind three of them

| pin | why |
|---|---|
| `verus.obligations` = 10 | **2 consts + 8 function terms.** Every function term was measured with `--verify-function <name> --verify-root`; `.temp/t157/verus/obligations.log` is the census. The 8: `run` 1 (RECURSIVE -- one termination query), `kernel` 2 (body + the op-walk loop body) and `main` 5. The zero terms are checkable the same way: `u32_at`, `nops_at` and `parse_fold` are non-recursive spec fns and report 0, and the four `external_body` items report 0. |
| `verus.twin_obligations` = 12 | the count under `--cfg slb_twin`. **10 shipped + 2**, one per trusted item inside the twin regime. ⚠ **Every trusted item here HAS a twin and none is blocked** -- p27's, p32's and p34's position, not p35's. `load_input` and `emit` are outside the regime (`external_body` with no `ensures` and no `unsafe` body) and have no twins. |
| `identity` `O0: norel`, `O3: norel` | ⚠ **weaker than p27's, p32's and p35's `exact`, and the mechanism is measured**: the two crates place `kernel` 0x20 apart, so every intra-function branch displacement and the rip-relative `lea` into the landing-pad table differ by exactly that -- `lea -0xde51(%rip),%rcx` against `lea -0xde31(%rip),%rcx`, **both resolving to the same absolute address `0x7910`** -- while `md5_fn_norel`, `md5_norm`, the instruction count (189 non-pad at `-O3`, 313 at `-O0`) and the byte count are all identical. p34's mechanism exactly, on a different rodata reference. |
| `miri.required: true` | derived from the four trusted items. ⚠ **Miri has something to see here** -- p25 allocates, grows and frees -- and what it finds on the SHIPPED rung is NOTHING on every input, while `controls/arm_unsafe_ptr.rs` (the R4 that holds the interior pointer across the growth) is the must-fire arm. |

## Reproducing

```sh
python3 patterns/p25-realloc-growth/inputs/gen.py     # the .bin files are gitignored
harness/build.py p25
harness/measure.py p25        # BEFORE report.py: report.py loads results/p25-*.json first
harness/report.py p25
harness/check.py p25
harness/report.py p25 && harness/check.py p25   # stage 9c's one-run lag, on a NEW pattern only
python3 patterns/p25-realloc-growth/controls/safety_line.py
python3 patterns/p25-realloc-growth/controls/no_stale.py
python3 patterns/p25-realloc-growth/controls/no_reloc.py
python3 patterns/p25-realloc-growth/controls/reloc_probe.py
python3 patterns/p25-realloc-growth/controls/detectors.py
python3 patterns/p25-realloc-growth/controls/safe_arms.py
python3 patterns/p25-realloc-growth/controls/rederive.py
python3 patterns/p25-realloc-growth/controls/rust_bug.py
python3 patterns/p25-realloc-growth/controls/proof_mutants.py
```

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == parse_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (parse_fold). p25's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27, p29, p32, p34 and p35 use and NOT p02's before/after set: p25's two growable vectors are LOCALS of the kernel and both are freed before the call returns, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by ONE CONJUNCT on the READ path** -- `curbase == toks` in c/kernel_hardened.c -- and ⚠⚠ AT R5 IT HAS NO ANALOGUE AT ALL, WHICH IS THIS ROW'S PROOF-SIDE RESULT RATHER THAN AN OMISSION. The abstract machine `run` this `ensures` names has NO HEAP, NO BLOCK, NO CAPACITY AND NO ALLOCATOR in it: two byte sequences and one saved INTEGER index. That is not a simplification, it is the specification-side statement of why the conjunct is needed only in C -- `realloc` COPIES, so under the checked semantics the element the saved index names is the same element before and after a growth, and where the bytes live cannot be observed. c/kernel.c's bug is precisely that a THIRD representation, the ADDRESS the interior pointer holds, can fall out of step with the two `run` and model.py agree about. What survives at R4 and R5 is the spatial residue, `have ==> curi < toks@.len()`, which is what licenses `vec_get_unchecked`; controls/proof_mutants.py demonstrates it with an ATTACK arm (delete that conjunct from the loop invariant), a VACUITY arm (a constant kernel body), an X1 arm (strike the SAVE statement that re-establishes it) and a SPEC-WEAKEN arm. **The `ensures` is the FUNCTIONAL one**: `run` says the accumulator is what an abstract parser computes -- so a kernel that folded a retired block's byte, or that accepted a different number of pushes, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest or that the op stream is well formed.** `run` specifies what the PROGRAM does -- stop when the window runs out, fold SENT for a push past MAXCAP, for a SAVE with an empty token vector and for a READ before any SAVE -- so degenerate.bin and all five adversarial op-stream files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that the op stream never grew the token vector after a SAVE would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete the row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: ONE conjunct on the READ path, `} else if (curbase == toks) {` in c/kernel_hardened.c, with a re-derive `v = (uint64_t)toks[curi];` in the `else` it guards. c/kernel.c is otherwise character-identical, and ../controls/safety_line.py preprocesses both shipped files and measures the difference rather than asserting it.",
        "rust": "THE SAFETY LINE HAS NO SITE IN ANY RUST RUNG, AND THAT IS THE ROW'S RESULT AND NOT AN OMISSION. ⚠⚠ R2 and R3 cannot hold `&toks[curi]` across `toks.push(a)` at all, and R4 and R5 could hold a raw `*const u8` but must not: `identity` pins R4 to R5, and Verus cannot license `*cur` because the permission is not obtainable for a `Vec`'s buffer and because address equality does not imply provenance equality. ../controls/rust_bug.py builds the excluded arm and measures it under Miri."
      },
      {
        "c": "THE SAVED REFERENCE IS AN INTERIOR POINTER, in both C rungs: `cur = &toks[curi];` beside `curbase = toks;`. The base and the index are MAINTAINED IN BOTH RUNGS and consulted only by the hardened one, which is what makes the two files differ by the conjunct and nothing else.",
        "rust": "THE SAVED REFERENCE IS AN INDEX, in all four Rust rungs: `curi = (a as usize) % toks.len();`. ⚠ There is no `curbase` in any Rust rung because there is nothing for it to guard -- that is the one place the rungs are not isomorphic and the why key argues it."
      },
      {
        "c": "THE GROWTH IS A REAL `realloc` OF THE TOKEN VECTOR, in both C rungs: `nt = (uint8_t *)realloc(toks, nc);` with `nc = tcap ? tcap * 2 : P25_SEED;`. A fixed-extent array or an arena would leave the stale use inside a live allocation and the row would be p32's.",
        "rust": "the growth, in all four Rust rungs, spelled as the language spells it: `toks.push(a);`. ⚠ `Vec::push` is a `realloc` through the same system allocator, with the same doubling policy and a different starting capacity; the why key prices the difference and NOTES.md 5 measures it."
      },
      {
        "c": "THE SECOND LIVE GROWABLE ALLOCATION, in both C rungs, and it is what stops the first extending in place: `ns = (uint8_t *)realloc(strs, nc);`. Without it the token vector is the newest allocation, glibc extends it and the undefined behaviour is unobservable -- which is exactly the topology TASK_134 measured and mistook for a fact about C.",
        "rust": "the same second vector, in all four Rust rungs: `strs.push(a);`."
      },
      {
        "c": "THE CAPACITY GUARD, in both C rungs: `ntok < P25_MAXCAP` and `nstr < P25_MAXCAP`, so a push past the bound folds SENT in EVERY rung including R1 and the bug is not a write out of bounds.",
        "rust": "the same guard, in all four Rust rungs, with no capacity variable at all: `toks.len() < MAXCAP` and `strs.len() < MAXCAP`. ⚠ The equivalence is exact and load-bearing: MAXCAP is SEED * 2**k, so growth at `n == cap` from `cap = SEED` makes the acceptance guard fire at exactly `n == MAXCAP`."
      },
      {
        "c": "THE READ IS GUARDED AGAINST HAVING NO SAVED REFERENCE, in both C rungs: `if (cur == NULL)`, folding SENT. So R1's bug is not 'dereference an uninitialised pointer'.",
        "rust": "the same guard, in all four Rust rungs, over the flag the index needs: `if have {`."
      },
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first: `if len - p < 2 {` in R2, R4 and R5. ⚠ R3 does not write it -- `chunks_exact(2).take(nops)` carries the same bound inside the iterator, and the walk is the R3 lever the why key leaves deliberately unpinned."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, `c % 4`, in all four Rust rungs -- spelled `c % 4 == 0` in R2, R4 and R5 and `match c % 4 {` in R3, which is the R3 lever."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 + v;` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add(`."
      },
      {
        "c": "the two vector lengths are folded last, so a rung that accepted a different number of pushes cannot produce the same checksum: `return acc * 31 + (uint64_t)(ntok + nstr);` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)`."
      }
    ],
    "forbidden": [
      "`transmute`",
      "`with_capacity`",
      "`reserve_exact`",
      "`as_ptr()`",
      "`as_mut_ptr()`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Box::leak`",
      "`Rc<`",
      "`calloc(`",
      "`memmove(`",
      "`alloca(`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED CONJUNCT ON THE READ PATH, AND THE HARM IS A READ OF STORAGE `realloc` TOOK BACK. The kernel saves `cur = &toks[curi]`, a later push grows the token vector, and `realloc` retires the old block as a SIDE EFFECT OF GROWTH -- the program never calls `free` on it. THAT IS THE C-MECHANISM DISTINCTION THIS ROW RESTS ON: p27's, p29's and p32's stale use follows an explicit free() of a whole object or a handle the read failed to revalidate, and p34's follows an explicit free() a refcount selected; p25 calls free() on nothing but the two vectors at the end, and what is stale is an INTERIOR pointer into the middle of a container. Measured rather than asserted (controls/no_reloc.py, re-derived every run, with comments and string literals blanked first): `realloc` is called by EXACTLY ONE pattern's c/ and it is this one, 1 of 32, and only 5 of 32 call `malloc` at all (p27, p28, p29, p34, p42). ⚠ .temp/mgr155/NOTES.md §6 published *p10 p27 p28 p29 p32 p42, 6 of 30* from a RAW grep, and both halves of that are wrong: p10's and p32's hits are PROSE -- p32's own kernel.h says *neither malloc'd nor free'd per use* -- and p34, which really does allocate, is missing. ⚠ And `free` is called by 32 of 32, because every c/main.c frees the driver payload, so *calls free* is not a distinguishing token and this row's distinction is stated about the KERNEL. ⚠⚠ THE HARDENED CELL RE-DERIVES IN ITS `else` BRANCH AND THAT IS FORCED, NOT CHOSEN. A rung that folded SENT on relocation would make the kernel's ANSWER a function of the ALLOCATOR -- model.py could not derive the checksum without simulating glibc, and the four Rust rungs, whose `Vec` grows on a different schedule, could not agree with the C ones on the adversarial input, so check.py stage 2 would be unsatisfiable in principle. Re-deriving is allocator-independent because `realloc` COPIES: `toks[curi]` after the move is the byte `*cur` named before it. ⚠ SO THE CONJUNCT BUYS MEMORY SAFETY AND BUYS NOTHING ELSE -- both branches compute the same value in every terminating execution -- which is why the R1-vs-R1h gradient is a clean price for memory safety alone. ⚠⚠ AND THE CONJUNCT IS NOT THE STANDARD-CLEAN REPAIR. C11 7.22.3.5p4 with DR 400 makes `cur` indeterminate the moment `realloc` returns, WHETHER OR NOT THE BLOCK MOVED, so the surviving `*cur` in the true branch is a use of an indeterminate value under the abstract machine even though no relocating allocator can observe it -- ASan moves on every realloc, so under ASan the true branch is taken only when no realloc happened at all. The standard-clean rung is the UNCONDITIONAL RE-DERIVE, i.e. the addressing-mode change TASK_134's kill named; controls/rederive.py builds it and prices it. BOTH HALVES OF THAT OLD KILL ARE ANSWERED AND THEY GO OPPOSITE WAYS: the conjunct EXISTS (the first half is refuted, and the shipped diff is it) and it is INSUFFICIENT (the second half is vindicated, for a reason nobody had stated). THE HARM WINDOW IS ONE GROWTH WIDE AND SAYING OTHERWISE MISLEADS. glibc's minimum chunk gives a 4-byte malloc 24 usable bytes, so 4->8 and 8->16 are satisfied in place and it is 16->32 that has to move, and only because the string vector was allocated after the token vector and is still live. The adversarial windows are TUNED to that growth; controls/reloc_probe.py measures which growth relocates under the SHIPPED driver rather than under a hand-rolled one, which is the mistake TASK_134 made. ⚠ ASan IS A BIASED INSTRUMENT FOR THIS ROW AND THE RESULT DOES NOT REST ON IT: its allocator moves on EVERY realloc, so its column would fire even under a topology where glibc never relocated. The unbiased evidence is the plain-build divergence between R1 and R1h, and NOTES.md 2 reports the two separately. It is also why model.py's derived `sanitizer_expect` models ASan and not glibc -- the gate compares against an ASan build, so modelling ASan is what makes the column checkable, and it is the CONSERVATIVE direction because every read it calls stale is a read C already calls undefined. ⚠⚠ NO BENIGN INPUT MAY GO STALE, AND IT IS ENFORCED IN THREE PLACES RATHER THAN ASSUMED: inputs/gen.py cannot emit a non-adversarial window that grows the token vector while a saved pointer is live, model.py::stale_free_problems re-derives the property from the SHIPPED blob every gate run, and controls/no_stale.py censuses the directory. ⚠ UNLIKE p34, p25's SAFETY LINE DOES EXECUTE ON EVERY BENIGN INPUT -- every READ evaluates the conjunct; what no benign input does is take the `else` branch -- so p25 has a real, non-zero benign cost gradient where p34's is 0.00, and NOTES.md 4 reports it at BOTH optimisation levels on BOTH compilers. SAFE RUST HAS NO SITE FOR THE SAFETY LINE, AND THE EVIDENCE FOR THAT IS NOT THE ERROR CODE. `&toks[curi]` cannot be held across `toks.push(a)`, so the safe port saves an INDEX -- and then `realloc` copies and the read is correct by construction, so the safe port IS the hardened rung. ⚠⚠ E0502 IS NOT DISTINGUISHING AND MUST NOT BE QUOTED AS IF IT WERE: controls/safe_arms.py compiles the &T-across-push spelling and gets E0502, AND compiles a NEGATIVE CONTROL that cannot have p25's bug -- no container, no growth, no saved reference -- and gets the same code and the same message. FOURTH TIME THIS PROJECT HAS READ A rustc CODE AS DISTINGUISHING WHEN IT WAS NOT (p25's own E0502 in the catalogue, p28's E0382/E0499, p34's E0507). ⚠ AND THE INDEX PORT HAS NO BUG AT ALL, WHICH IS A FINDING AND NOT A FAILURE: it is recorded here so nobody rediscovers it as new. WHAT THE R5 PROVES AND WHAT IT DOES NOT. ⚠⚠ THE TEMPORAL OBLIGATION HAS NO ANALOGUE AT R5 BECAUSE NO RUNG ABOVE R1 CAN HOLD THE STALE INTERIOR POINTER. Reading `*cur` needs a PointsTo permission, and no vstd API at the pin yields one for a `Vec`'s buffer; and the guard `curbase == toks.as_ptr()` is an ADDRESS comparison while Verus's pointers carry PROVENANCE, so address equality does not entail that the permission you hold names that byte -- the guard is exactly the fact the proof would need and exactly the fact address equality does not give. What is left is the spatial residue `have ==> curi < toks@.len()`, easy because a vector only grows. SO p25 IS THE FIRST ROW IN THIS TREE WHERE THE LADDER DELETES THE BUG ABOVE R1 RATHER THAN MAKING IT PROVABLE, AND THE HONEST STATEMENT IS THAT ITS R5 OBLIGATION IS SMALLER THAN p27's, p29's, p32's OR p34's. controls/rust_bug.py builds the R4 that DOES hold the pointer and measures it under Miri, so the claim is a measurement; controls/proof_mutants.py is the four-cell battery that says what is left is not vacuous. ⚠ p25's R5 IS ALSO THE FIRST IN THIS TREE TO CALL `Vec::push` IN EXEC CODE -- measured, not assumed -- and vstd's assume_specification for it carries `final(vec)@ == old(vec)@.push(value)` with NO `requires` at all, so the growth costs no trusted item; group_vec_axioms is what ties `vec.len()` to `vec@.len()` and no other pattern in the tree needs it. TCB IS FOUR ITEMS, THREE FEWER THAN p27's AND p34's SEVEN, and the reason is the same fact: this rung allocates through `Vec`, whose allocation and deallocation are vstd's problem rather than this file's, so there is no rec_alloc/rec_free pair to trust. WHAT IS DELIBERATELY NOT PINNED is how R3 walks the op stream -- `chunks_exact(2).take(nops)` against R2's cursor, and `match c % 4` against R2's `if` chain -- exactly as p32 leaves its handle-register spelling unpinned, p34 leaves its op walk and p14 leaves its fold loop. That is the R3 lever, it costs zero TCB, and NOTES.md 5 reports what it moves. ⚠ The consequence for the cursor-guard entry above is stated there rather than left implicit: R2, R4 and R5 write `if len - p < 2 {` and R3 does not write it at all, because the iterator carries the same bound. ⚠ THE `forbidden` LIST PINS THE GROWTH ITSELF: `with_capacity` and `reserve_exact` are excluded so that no Rust rung can pre-allocate the relocation away, and `as_ptr()`/`as_mut_ptr()` are excluded so that no Rust rung can reconstruct the interior pointer the identity pin forbids. `Rc<` is forbidden here and REQUIRED in p34 for the mirror-image reason: on p34 the library IS the comparison, and on this row it would move the storage decision into a library that has nothing to do with growth. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 10
    },
    "twin_obligations": {
      "verus.rs": 12
    },
    "obligations_note": "10 = TWO consts (MAXCAP, SENT) 1 each + 8 function terms. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`, not predicted; the loop is `.temp/t157/verus/obligations.sh` and the log is `.temp/t157/verus/obligations.log`. The 8: `run` 1 (RECURSIVE -- one termination query), `kernel` 2 (body + the op-walk loop body) and `main` 5, quoted AS MEASURED. The zero terms are checkable the same way: `u32_at`, `nops_at` and `parse_fold` are NON-recursive spec fns and report 0, and the four `external_body` items report 0. ⚠ p25 declares no struct, so there is no `derive` term and no bare-struct term to account for -- p29's derive term and p32's bare-struct zero have no analogue on this row.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. **10 shipped + 2**, one per trusted item inside the twin regime: slb_twin_buf_get_unchecked and slb_twin_vec_get_unchecked. ⚠ p25 owes TWO twins where p32 owes three and p34 owes five, and the missing ones are the allocation API: p34 trusts `vstd::raw_ptr::allocate`/`deallocate` copies for codegen, while p25 allocates through `Vec` and trusts nothing for it. **EVERY trusted item here has a twin and none is blocked**, which is p27's, p32's and p34's position and not p35's. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {},
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
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "parse_fold": {
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
        "vec_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_vec_get_unchecked": {
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
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == parse_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p32's, p34's, p35's, p16's, p05's, p11's, p12's, p06's and p14's denominator. marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary, so the one-shot loader terms cancel. ⚠ The estimate is STRICT: it over-counts the 4 window-header bytes, which are decoded as a u32 and are not operations, and under-counts every 2-byte operation -- each does a modulo, a compare chain and a multiply-add, while a push that crosses a capacity boundary also calls `realloc` and copies the vector. ⚠ p25's under-count is BOUNDED where p34's is not: the number of allocator calls per window is at most `2 * log2(MAXCAP/SEED) + 2`, i.e. at most 10 whatever the input, so no op stream can make the estimate arbitrarily loose. No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per byte applies and what it catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "norel",
      "why": "R4 == R5 up to pc-relative displacement fields at BOTH optimisation levels, and NOT by raw bytes at either. ⚠⚠ THAT IS WEAKER THAN p27's, p32's and p35's `O3: exact`, AND THE MECHANISM IS KNOWN RATHER THAN GUESSED (PROTOCOL rule 12). `harness/asm.py stat` reports `md5_raw_norel`, `md5_fn_norel` and `md5_norm` IDENTICAL, the same 189 non-pad instructions and 751 bytes at `-O3` (313 and 1791 at `-O0`) and the same masked relocation count on both binaries; the raw digests differ because the two crates place `kernel` at addresses 0x20 apart, so every intra-function branch displacement carries that offset and so does the rip-relative `lea` into the landing-pad table -- `lea -0xde51(%rip),%rcx` against `lea -0xde31(%rip),%rcx`, **both resolving to the SAME absolute address 0x7910**. p27's and p32's kernels have no such rodata reference, which is why they reach `exact` and this one cannot: it is a fact about LINK LAYOUT, not about the proof. The proof still licenses the unsafe code at zero instruction cost, which is this project's standing R4/R5 result, and the instruction-level evidence for it here is the identical normalised digest and the identical count rather than the raw md5. The two twins are `#[cfg(slb_twin)]` and no measured build compiles them, so they cost zero instructions structurally."
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
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. p25 has four. ⚠⚠ **And Miri has something to see here**: p25 allocates, GROWS and frees, and a read through an interior pointer taken before a growth is exactly the class Miri reports. What it finds on the SHIPPED unsafe.rs is NOTHING, on every input including all five adversarial ones -- the shipped rung saves an INDEX, so that is the right answer and it is what stage 8 measures. What it finds on `controls/arm_unsafe_ptr.rs`, which is this rung with the index replaced by a raw interior pointer taken from `toks.as_ptr()` and nothing else, is an Undefined Behaviour report; `controls/rust_bug.py` is the must-fire arm and NOTES.md 7 has both rows. Cost: check.py rewrites n_iters to 4.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
