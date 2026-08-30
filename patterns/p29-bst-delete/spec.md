# p29 -- binary search tree delete, with a cached lookup result

**The SECOND temporal row in this project, and it is `p27`'s row with one term
added to the safety line.** `c/kernel.h` carries the kernel contract in
pseudocode; this file carries the reasoning and the machine-readable pins.

## The bug, in one paragraph

A `FIND` saves the address of the record it found. A later `USE` reads through
that address and asks only whether a `FIND` ever succeeded. Deleting a key from
a binary search tree does one of two things to the record that held it, and
**which one is chosen by the DEGREE of the victim**:

| victim | what the splice does | what R1's cached read is |
|---|---|---|
| 0 or 1 child | unlinks it and **frees** it | a genuine `heap-use-after-free`; ASan aborts; the value read is **not reproducible** |
| 2 children | copies the in-order successor's key and val **into it** and frees the **successor** | an in-bounds read of a **live** allocation whose occupant changed; ASan is silent; the wrong answer is **stable** |

One omitted line, two bug classes, selected by the input.

## What the safety line has to notice, and why no detector notices it

```
p27   if (h < ntab && live[h] == 1)                     is the ALLOCATION there?
p29   if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)
                             ^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^
                             is the ALLOCATION     is the OCCUPANT still the
                             still there?          one FIND returned?
                             (p27's whole line)    (p27 has no analogue)
```

The occupant-identity test exists because **`p29`'s second bug class never
touches the allocation.** A liveness bit cannot see it, and neither can ASan,
safe Rust's `Option` discriminant, Miri, or a linear `PointsTo` -- all four are
mechanisms about the ALLOCATION. `../NOTES.md` 2 measures all of them.

⚠⚠⚠ **AND THIS SECTION USED TO BE HEADED *"why the safety line needs TWO
conjuncts, and `p27`'s needs one"*, WHICH IS FALSE.** `TASK_140` built **two**
single-conjunct spellings out of the shipped `c/kernel.c` by substitution and
both score `0 wrong / 0 ASan lines` with the positive control firing; one of
them adds **no state at all**, widening `live[]` from a bit to the occupant tag
-- which `p27`'s own kernel calls a generation counter with slot reuse removed.
**ONE CONJUNCT IS ENOUGH.** What ships here is a two-conjunct spelling because
it buys a free `wf` at R5 (`../NOTES.md` 6c); that is a CHOICE. ⚠ **The row is
still not a duplicate of `p27`** -- one source line carrying two bug classes
selected by the input is what makes it a row, and the ⚠ **half every detector
sees is the half that cannot be gated**, R1's checksum being irreproducible on
the use-after-free windows and stable on the recycle one. **The conjunct count
was never evidence for any of that.**

**Neither conjunct subsumes the other, and they fail in different currencies.**
Measured on one 500-window corpus (`../NOTES.md` 2b, `controls/arms.json`): drop
the liveness conjunct and the harm is memory-unsafety and usually *not* a wrong
answer — the freed bytes still hold the old record often enough that the
checksum survives; drop the identity conjunct and the harm is a wrong answer,
**every** recycle window, and *never* a memory error. ⚠ The counts are in
`NOTES.md` and in the control's JSON, not here: a number only a rebuild can
produce must not sit inside a fence the rebuild re-hashes.

**Given this spelling, the order is load-bearing.** `tab[g_slot]` is never
reset, so `tab[g_slot][0]` is the same load from the same address as
`g_saved[0]`. `&&` short-circuits, so the identity test is not evaluated on the
inputs where the record has been freed. At R5 the ordering is not even a
choice: the record read needs `perms.tracked_borrow(g_slot)` and only the
liveness test discharges its precondition. ⚠ **That is a fact about the
two-conjunct spelling, not about the pattern** -- a one-conjunct spelling has
no ordering to force.

## What every rung carries that a textbook BST would not

Every walk is `while (cur != NIL && live[cur] == 1 && steps < TABCAP)`, and the
two-child test asks liveness of both children: **six liveness conjuncts and five
step bounds, eleven terms, and not one of them can fire** — in every rung
including R1. They are the price of *not* proving the link
structure is a tree: with them, the licence for a record read is `p27`'s own
per-slot `live[i] == 1 <==> perms.dom().contains(i)`; without them it is unique
parents and acyclicity. They are in **every** rung so that no rung-to-rung
comparison is confounded by them, and the safe rungs would need the liveness
half anyway (`unwrap` on a `None` slot is a panic). `../NOTES.md` 4 counts them.

## Why `tab[h]` is not nulled on the free

`p27`'s `c/kernel.c` argues it by name: nulling the table slot turns a stale
read into a NULL dereference, *a crash, not a use-after-free, and a different
bug class*. p29 keeps the convention and now has a measurement for it -- with
`tab[cur] = NULL` added, the one-conjunct control stops reporting
`heap-use-after-free` and starts reporting `SEGV` (`../NOTES.md` 2c). It also
keeps `tab[]` **write-once per slot**, which is what lets R5 know `g_saved` is
slot `g_slot`'s record through an invariant no operation has to re-establish.

## Why every benign window must USE only a record that is still itself

`inputs/gen.py` checks it, by running a copy of the checked kernel over every
window of every blob it emits, and `harness/check.py` stage 2 requires every
non-adversarial cell to agree with `model.py` and with every other cell. Both
bug classes therefore live on the `adversarial-*` rows alone, whose behaviour
the gate **records** per cell instead of requiring agreement.

## The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop
calls `kernel(buf, k * stride, stride)`. `driver.call_args` declares which
argument *positions* of a named call are the canonical ones. **This is p14's pin
unchanged**, inherited through p27; p29 adds no new declaration surface.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts and
the price of the identity pin.

| pin | why |
|---|---|
| `verus.obligations` = 25 | **4 consts + 1 derive + 4 recursive spec fns + 4 record ops + walk 2 + kernel 5 + main 5.** Every function term was measured with `--verify-function <name> --verify-root`. ⚠ The 25th term is the `#[derive(Clone, Copy)]` on `Rec`, **not** the `struct`: a bare `struct` carries ZERO (TASK_140, measured eleven ways; the number 25 never moved, only its stated cause) -- see `obligations_note`. |
| `verus.twin_obligations` = 30 | the count under `--cfg slb_twin`. **25 shipped + 5**, one per trusted item inside the twin regime. Two of the five are `vstd::raw_ptr::allocate` and `deallocate` themselves. |
| `identity` `O3: norel`, `O0: differ` | ⚠ **the first `differ` row in the tree**, and it is measured rather than conceded: p27's one-line `-O0` fix does not transfer once the record is a struct. See the pin's `why`. |
| `miri.required: true` | on p29 Miri is the only instrument that checks the temporal property on the unsafe rung **and** the only one that sees R4's `-O0` shape at all, because R4 and R5 are not byte-identical there. ⚠ And it is **silent on the recycle half**, which is the row's point. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == bst_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (bst_fold). p29's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07 and p27 use and NOT p02's before/after set: p29's records are allocated AND FREED inside the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. **The security property is carried by TWO conjuncts on the USE path** -- `live[g_slot] == 1 && tab[g_slot][0] == g_key` in C and in the unsafe rungs, `tab[g_slot].is_some() && rec.key == g_key` in the safe rungs -- and at R5 the FIRST becomes `perms.dom().contains(g_slot)`, the precondition `tracked_borrow` cannot be called without, while the SECOND is an ordinary value equality that linearity has nothing to say about. ⚠ That SPLIT is real and it is not the row, and this entry said it was: p27 spells only the first conjunct, but p29's line can also be spelled with one (TASK_140, measured), so the row rests on its two BUG CLASSES and not on a conjunct count. **The `ensures` is the FUNCTIONAL one**: `run` is an abstract machine carrying five parallel slot sequences (`ky`, `vl`, `lt`, `rt`, `lv`), a root link and the cached lookup result, and it says the accumulator is what that machine computes -- so a kernel that folded a freed record's value, or a re-occupied record's, or that truncated at a different TABCAP, is rejected. **What the `ensures` deliberately does NOT say is that `nops` is honest, that the op stream is well formed, or that a cached record is still itself.** `run` specifies what the PROGRAM does -- stop when the window runs out, reject an INSERT past TABCAP, reject a FIND or REMOVE of an absent key, fold SENT for a USE whose cached record is gone or re-occupied -- so degenerate.bin and all four adversarial op-stream files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that the op stream never staled a cached record would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: TWO conjuncts on the USE path, `if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key) {` in c/kernel_hardened.c. c/kernel.c writes `if (g_saved != NULL) {` there and is otherwise character-identical, so the scoped-absent audit pair this entry reports is on that rung and is correct.",
        "rust": "THE SAFETY LINE. In the unsafe rungs it is `if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {` followed by `if rr.key == g_key {`, and the NESTING is forced rather than chosen: at R5 the record read needs `perms.tracked_borrow(g_slot)`, whose precondition only the liveness test discharges. In the safe rungs the first conjunct is the `Option` discriminant -- `tab[g_slot].is_some()` in safe_naive.rs and the `Some(rec)` arm in safe_tuned.rs -- because safe Rust has no separate liveness array to test, **and the second conjunct has to be written out in full there too**: `rec.key == g_key`. That asymmetry is the pattern's whole subject; see the why key."
      },
      {
        "c": "THE LINE THE C RUNG MUST NOT FORGET, present in BOTH C rungs: `live[cur] = 0;` immediately after the `free`. R1's bug is NOT that it skips this -- it does not -- it is that its USE path never asks. Splitting the free from the invalidation is what makes forgetting possible at all.",
        "rust": "the same line in the unsafe rungs, `arr_set_unchecked(&mut live, cur as usize, 0u8);` -- and at R5 the proof FORCES it: without it the loop invariant cannot be re-established, because `rec_free` has consumed slot `cur`'s permission while the liveness array would still claim it exists. In the safe rungs there is no such line, because `tab[cur] = None` frees the record and invalidates the slot in ONE operation."
      },
      {
        "c": "THE SUBSTITUTION, in both C rungs, and it is the SECOND bug class's whole mechanism: `tab[cur][0] = tab[s][0];` copies the in-order successor's key INTO the victim's record. The victim's ALLOCATION is not freed, so nothing temporal happens and no allocation-shaped detector fires.",
        "rust": "the substitution in the unsafe rungs, `Rec { key: srec.key, val: srec.val, l: co.l, r: co.r }` written back through `rec_write`; in the safe rungs the same two fields are assigned to the live `Box`'s contents. Nothing is dropped in any rung."
      },
      {
        "c": "THE REAL `free`, in both C rungs: `free(tab[cur]);`. Not a freelist push into a slab -- see the why key.",
        "rust": "THE REAL free, in all four Rust rungs: `std::alloc::dealloc(p, layout);` inside rec_free in unsafe.rs and verus.rs (`vstd::raw_ptr::deallocate`'s six preconditions and its body, respelled but not weakened, whose verified twin in verus.rs is vstd's own `deallocate`), and the drop of `Option<Box<Rec>>` in safe_naive.rs and safe_tuned.rs."
      },
      {
        "c": "ONE ALLOCATION PER RECORD, in both C rungs: `malloc(RECSZ)`.",
        "rust": "ONE ALLOCATION PER RECORD, in all four Rust rungs: `std::alloc::alloc(layout)` inside rec_alloc in unsafe.rs and verus.rs, and `Box::new(Rec {` in safe_naive.rs and safe_tuned.rs. Rust's default global allocator calls `malloc` for `align <= 8`, so all seven rungs hit the same glibc, in the same size class, once per record."
      },
      {
        "c": "THE WALK'S LIVENESS CONJUNCT AND ITS STEP BOUND, in every rung including R1: `while (cur != NIL && live[cur] == 1 && steps < TABCAP)`. Neither ever fires; both are what R5 needs. See the why key.",
        "rust": "the same walk guard in the unsafe rungs, `while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP`, and in the safe rungs the `Option` discriminant plays the liveness role -- `tab[cur].is_some()` in safe_naive.rs and a `match tab[cur].as_ref()` whose `None` arm breaks in safe_tuned.rs."
      },
      {
        "c": "the table's extent is a COMPILE-TIME CONSTANT and the capacity guard is in every rung including R1: `if (ntab < TABCAP)` in both C rungs.",
        "rust": "the capacity guard, in all four Rust rungs: `if ntab < TABCAP {`."
      },
      {
        "c": "the cursor guard is SUBTRACTION-FIRST, so it cannot wrap and the additive form's overflow never arises: `if (len - p < 2)` in both C rungs.",
        "rust": "the cursor guard, subtraction-first, in all four Rust rungs: `if len - p < 2 {`."
      },
      {
        "c": "the opcode is `c % 4`, so EVERY byte value is a legal opcode and no input is rejected for being malformed: `c % 4 == 0` in both C rungs.",
        "rust": "the opcode, in all four Rust rungs: `c % 4 == 0`."
      },
      {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `acc = acc * 31 + SENT;` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: `.wrapping_add(SENT)`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier: `acc = acc * 31 +` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `.wrapping_mul(31)`."
      },
      "the slot count is folded last so that a rung which allocated a different number of records cannot produce the same checksum: `ntab` appears in the return expression of all seven rungs."
    ],
    "forbidden": [
      "`realloc(`",
      "`calloc(`",
      "`Vec::with_capacity`",
      "`Rc<`",
      "`RefCell`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Box::leak`",
      "`Box::into_raw`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens above must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED SOURCE LINE CARRIES TWO BUG CLASSES SELECTED BY THE INPUT, AND THAT IS THE ROW. A victim with 0 or 1 child is unlinked and FREED, so R1's cached read is a genuine use-after-FREE; a victim with 2 children has the in-order successor's key and val copied INTO its record and the SUCCESSOR freed, so the record stays live at the same address holding somebody else's data and R1's read is an IN-BOUNDS use-after-RECYCLE. AND THE HALF EVERY DETECTOR SEES IS THE HALF THAT CANNOT BE GATED: ASan, Miri, safe Rust's `Option` discriminant and a linear `PointsTo` are all mechanisms about the ALLOCATION and see the FREE half only -- whose checksum is not reproducible run to run -- while the RECYCLE half is silent, stable and wrong (../controls/repro.json publishes the invariant and no pinned count). WHAT THIS FENCE CLAIMED HERE UNTIL TASK_141 AND IT IS FALSE, MEASURED AND RETRACTED AT TASK_140: ~~p29's safety line NEEDS two conjuncts where p27's needs one~~. ONE CONJUNCT IS ENOUGH -- two single-conjunct spellings built from c/kernel.c by substitution score 0 wrong and 0 ASan lines with the positive control firing, and one of them adds NO STATE, widening `live[]` from a bit to the occupant tag (which p27's own kernel calls a generation counter with slot reuse removed). The two-conjunct spelling is a CHOICE -- it buys a free `wf` at R5, ../NOTES.md 6c -- and the row is not a duplicate of p27 for the TWO-BUG-CLASS reason above, which is a reason the conjunct count was never evidence for. GIVEN THIS SPELLING THE ORDER IS FORCED, WHICH IS WHY THESE TWO ARE NOT INTERCHANGEABLE: `tab[g_slot]` is never reset, so `tab[g_slot][0]` is the same load from the same address as `g_saved[0]`; C's `&&` short-circuits, so with the liveness conjunct in front the identity test is not evaluated on exactly the inputs where the record has been freed, and without it the identity test is ITSELF a heap-use-after-free (measured: zero ASan lines against a hit on every use-after-free window; the counts live in ../NOTES.md 2b and ../controls/arms.json and are deliberately NOT transcribed into this hashed fence). At R5 the ordering is not even a choice: `perms.tracked_borrow(g_slot)` has `dom().contains(g_slot)` as a precondition and `live[g_slot] == 1` is the only thing that discharges it, so the identity test cannot be written first -- a fact about the TWO-CONJUNCT spelling and not about the pattern, since a single-conjunct spelling has no ordering to force. WHY `tab[h]` IS NOT NULLED ON THE FREE, and it is p27's reason with a measurement behind it: nulling the table slot would turn a stale read into a NULL dereference -- a crash, not a use-after-free, and a different bug class. Measured on this kernel: with `tab[cur] = NULL` added, the one-conjunct control stops reporting `heap-use-after-free` and starts reporting `SEGV` (../NOTES.md 2c). It also keeps `tab[]` WRITE-ONCE PER SLOT, which is what lets R5 know `g_saved` is slot `g_slot`'s record through an invariant that no operation has to re-establish. WHY EVERY WALK CARRIES `live[cur] == 1` AND A `steps` BOUND, IN EVERY RUNG INCLUDING R1: they never fire -- a correct tree never links to a retired slot and no path is longer than TABCAP -- and they are pinned because R5 needs them. The liveness conjunct licenses the record read through `live[i] == 1 <==> perms.dom().contains(i)`, a PER-SLOT fact; the alternative is proving the link structure IS A TREE (unique parents, acyclicity), which no per-slot invariant gives you. The step bound is the `decreases` measure. They are in EVERY rung so that no rung-to-rung comparison is confounded by them, and the safe rungs would need the liveness half anyway -- `Option::unwrap` on a `None` slot is a panic. THE FREE MUST BE A REAL `free`: if the records were one slab and the release were a freelist push, the stale read would be IN BOUNDS OF A LIVE ALLOCATION -- Miri would not flag it, `PointsTo` would license it, and the bug would be LOGICAL, which is p17's class and the tree already has one. That is what `Box::into_raw`, `ManuallyDrop`, `mem::forget` and `Box::leak` are forbidden for. `realloc`/`calloc`/`Vec::with_capacity` are forbidden because they change the allocator traffic and the fairness argument is that every rung makes exactly one allocation and one free per record; `Rc`/`RefCell` because they would move the liveness decision to run time inside the library and delete the comparison. SLOTS ARE NEVER RECYCLED, AND THAT IS NOT A PRESENTATIONAL CHOICE. It is p27's convention (`ntab` only grows, which is what reduces the generation counter to one bit) and it is what keeps the safe rung's answer a function of the operations rather than of the allocator. `TASK_137` measured the third spelling -- an arena in which the release does NOT destroy the record -- and it is wrong on BOTH bug classes and BIT-IDENTICAL to buggy C, which is verbatim p32/p33's result. (TASK_143/144: p32/p33 was RE-ADMITTED under the C-side bar and is BUILT as p32-free-list-pool; the sentence here formerly called that result `already-refused', which was true when written and is now false. It does not change this pin: choosing that spelling here would make p29 a second copy of p32's row rather than presenting p29 differently.) WHAT IS DELIBERATELY NOT PINNED is how the liveness half is SPELLED in the safe rungs -- `is_some()` + `unwrap()` in R2, a `match` arm in R3 -- exactly as p14 leaves its fold loop unpinned: those are the R3-side levers, they cost zero TCB, and the pattern reports the cheapest one FOUND on a named input rather than a minimum. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 25
    },
    "twin_obligations": {
      "verus.rs": 30
    },
    "obligations_note": "25 = TABCAP 1 + RECSZ 1 + NIL 1 + SENT 1 + **the `#[derive(Clone, Copy)]` on struct Rec 1** + descend 1 + succ_walk 1 + del_walk 1 + run 1 + rec_open 1 + rec_close 1 + rec_read 1 + rec_write 1 + walk 2 + kernel 5 + main 5. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root` (controls/../.temp is not needed: the loop is in `.temp/t139/verus/obligations.sh` in TASK_139's scratch and the log is `.temp/t139/logs/obligations.log`). The zero terms are checkable the same way: u32_at, nops_at, val_of, alive, ins_new, step, st0, bst_fold, rec_ok, dal_ok, base and wf are NON-RECURSIVE spec fns and report 0, while descend, succ_walk, del_walk and run are RECURSIVE and carry one termination query each; buf_get_unchecked, arr_get_unchecked, arr_set_unchecked, rec_alloc, rec_free, load_input and emit are external_body and report 0. FOUR `const`s carry one query each (`.memory/04-verus.md`: a const inside verus! is its own obligation). ⚠⚠ **THE 25th TERM IS THE `#[derive(Clone, Copy)]` ON `Rec`, NOT THE `struct`, AND THIS NOTE SAID OTHERWISE UNTIL TASK_141**: a BARE `struct` carries ZERO -- adding one to a copy of this file gives 25 and adding three still gives 25 -- while `#[derive(Clone)]` carries one, the derived `clone` body being its own query; `#[derive(Debug)]` and `#[derive(PartialEq)]` carry zero. TASK_139's probe (`.temp/t139/verus/probe_ob.rs`) added its `Rec2` WITH `#[derive(Clone, Copy)]` while describing it as *bare*, so it measured the derive and attributed the result to the struct; TASK_140 re-measured it eleven ways in minimal files and four ways on this file, and p36's bare `pub struct OpTag<const K: u8>` counts ZERO while its own census sums exactly to its pinned 12. **The NUMBER 25 is unchanged and was never in doubt; only the stated CAUSE was wrong.** The `global layout Rec` directive also carries ZERO. kernel's 5 = body + FOUR loop bodies (the op walk, the deletion guard loop, the successor descent and the epilogue); walk's 2 = body + its one loop. main's 5 is quoted AS MEASURED.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, which is where step 5c-twin checks the twins. 25 shipped + 5, one per trusted item that is inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked, slb_twin_arr_set_unchecked, slb_twin_rec_alloc and slb_twin_rec_free. **The last two are the point of the pattern's TCB section**: their checked implementations are `vstd::raw_ptr::allocate` and `vstd::raw_ptr::deallocate` themselves, so what the twin stage proves is that this crate's copies are no stronger than vstd's originals -- a relocation of trust for a codegen reason, not new trust. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth and p29 the sixth.",
        "rec_alloc": "`size` and `align` are constrained by `valid_layout(size, align)` and `size != 0`, which is vstd's own precondition for the identical body, and the returned pointer is constrained by THREE `ensures` clauses copied from vstd verbatim -- vstd states five, and the other two (`pt.0.addr() + size <= usize::MAX + 1` and `pt.0.addr() as int % align as int == 0`) are dropped here as p27 drops them, at `align == 1` where neither is used. Dropping them makes the item strictly WEAKER, and the twin -- vstd's own `allocate` -- still verifies, which is what a weakening has to do. There is no unconstrained parameter. The reason this item exists at all is CODEGEN and not trust: vstd carries no `#[inline]` on `allocate`, so an R5 that called it directly emits a GOT-indirect cross-crate `call` that unsafe.rs cannot produce.",
        "rec_free": "Every parameter is constrained: `p`, `size` and `align` by the four `dealloc.*` equalities, and the two tracked permissions by `pt.is_range(..)` and the provenance equalities -- vstd's own six preconditions for the identical body, all six shipped, RESPELLED through `dealloc@.` / `pt@.` because vstd destructures its tracked parameters and this item takes plain ones; the destructured form made the gate's tautology probe unsynthesisable and left all six conjuncts unjudged. Its verified twin is vstd's `deallocate`. Same codegen reason as `rec_alloc`."
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
        "alive": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "descend": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "succ_walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "del_walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ins_new": {
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
        "bst_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rec_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "dal_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "base": {
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
        "rec_open": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.1@.ptr() == r.0",
            "r.1@.is_init()",
            "r.1@.value() == v",
            "r.2@.addr() == r.0.addr()",
            "r.2@.size() == RECSZ",
            "r.2@.align() == 1",
            "r.2@.provenance() == r.0@.provenance"
          ]
        },
        "rec_close": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "dl.addr() == p.addr()",
            "dl.size() == RECSZ",
            "dl.align() == 1",
            "dl.provenance() == p@.provenance"
          ],
          "ensures": []
        },
        "rec_read": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "pt.is_init()"
          ],
          "ensures": [
            "r == pt.value()"
          ]
        },
        "rec_write": {
          "external": null,
          "requires": [
            "old(pt).ptr() == p"
          ],
          "ensures": [
            "final(pt).ptr() == p",
            "final(pt).is_init()",
            "final(pt).value() == v"
          ]
        },
        "walk": {
          "external": null,
          "requires": [
            "base(tab@, live@, st, ntab, *perms)",
            "root == st.root"
          ],
          "ensures": [
            "r == descend(st, st.root, NIL, false, k, TABCAP as nat)",
            "r.0 == NIL || (r.0 as int) < ntab",
            "r.1 == NIL || alive(st, r.1)",
            "r.3 ==> alive(st, r.0)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == bst_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p16's, p05's, p11's, p12's, p06's and p14's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT, and by more than an order of magnitude. It OVER-counts by the 4 window-header bytes, which are decoded as a u32 and are not operations. It UNDER-counts by everything else: each 2 window bytes is one OPERATION, and an operation here is a TREE WALK -- up to TABCAP steps, each a table index, a liveness test and a record load -- plus, for two of the four opcodes, a `malloc` or a `free`. model.py declares NO min_ir_per_work, so the harness default applies unchanged; it is not a tight floor here and is not meant to be, because a kernel that walks a tree and calls the allocator cannot be denominated like a fold. What it still catches is the failure it exists to catch -- a kernel the optimiser collapsed to nothing. The two probe inputs differ in work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "norel",
      "why": "R4 == R5 at `-O3` up to pc-relative displacement fields, and NOT at `-O0`. ⚠⚠ **THIS IS THE FIRST `identity: differ` ROW IN THE TREE AND IT IS A MEASURED RESULT, NOT A CONCESSION** -- `.memory/02-bench-rules.md` records that `differ` is a legal pin value that no pattern had yet exercised, so p29 is the run that was owed. **What differs and why.** p27 bought `O0: norel` with one line: writing `*base = v` rather than `core::ptr::write(base, v)`, because vstd's `ptr_mut_write` is `#[inline(always)]` over a precompiled vstd and inlines to a bare store while `core::ptr::write` is only `#[inline]` and survives as a call. **That trick does not transfer once the record is a four-byte struct rather than a byte**: at `-O0` R4's `*p = v` emits 870 kernel instructions and R5's `ptr_mut_write` emits 900, thirty more, in six-instruction groups at five write sites; `core::ptr::write` in R4 measures 886, closer and still not equal. All three were built and counted (../NOTES.md 5). At `-O3` the normalised text is IDENTICAL and only pc-relative fields differ -- the crate names differ in length, so the GOT displacements for `__rust_alloc`/`__rust_dealloc` differ -- which is link layout and not codegen, hence `norel`, p36's level. **The consequence the gate draws is the right one**: `check_miri` treats R4 != R5 as a reason Miri is REQUIRED rather than as an error, and Miri is required here anyway."
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
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. **On p29 Miri is doing what it does on p27 and one thing more**: it is the only tool in the matrix that checks the TEMPORAL property on the unsafe rung, and because R4 and R5 are NOT byte-identical at `-O0` it is also the only tool that checks R4's own `-O0` shape at all. ASan checks the temporal half on the C rungs; the proof covers R5. ⚠ **And note what Miri CANNOT see here, which is the pattern's headline**: the two-child splice frees nothing, so Miri is silent on `adversarial-recycle.bin` in every rung -- the use-after-RECYCLE bug class is invisible to every allocation-shaped instrument. Cost: check.py rewrites n_iters to 4, so each row performs at most 4 x nops allocator operations.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
