# p28 -- intrusive doubly linked lists, two link sets, incomplete destroy

A bounded object cache whose objects carry **TWO INTRUSIVE LINK SETS** -- a
doubly linked eviction list (`lp`/`ln`) and a doubly linked hash chain
(`hn`/`hp`) -- and a DESTROY path that leaves only one of them. `c/kernel.h`
carries the kernel contract in pseudocode; this file carries the reasoning and
the machine-readable pins. `README.md` says the same thing for a reader who has
not read either.

⚠⚠⚠ **WHY THIS ROW EXISTS, BECAUSE IT IS NOT WHAT A READER WILL GUESS.** It
exists because the ADMISSION BAR WAS CORRECTED (`CLAUDE.md` rule 6,
`.memory/02-bench-rules.md` *THE ADMISSION BAR IS C-SIDE ONLY*, RECAP findings 53
and 54). `TASK_093` refused it on the sentence *"safe Rust's answer is an arena
that never frees, or `p27`'s mechanism"*, which is a RUST-SIDE reason the bar now
forbids -- and which is **also false of the spelling this row ships**:
`safe_naive.rs` holds `Option<Box<Obj>>` and frees per object, exactly as the C
rungs do. Nothing the Rust or the Verus rungs do can shrink or retire this row;
what they do is a RESULT, and this pattern's are in `NOTES.md` 4, 4b, 5 and 6.

## The bug, in one paragraph

An object is one `malloc` and both link sets live INSIDE it, so **the object is
aliased by two lists at once and MEMBERSHIP IS NOT OWNERSHIP**. `bucket[b]` heads
chain `b`; `head`/`tail` are the eviction list's ends and the eviction list is the
OWNERSHIP list. **TRIM reaches its victim through the EVICTION list** -- that is
what "the oldest object" means -- so it holds no chain cursor and has to go and
get one. `c/kernel.c` does not. The freed victim's chain predecessor keeps
`hn == victim`, or `bucket[b]` does, and the next walk of that bucket reads
through it.

| what the input does after a TRIM | what R1 does |
|---|---|
| GET or PUT on the victim's bucket | walks the chain into the freed object and reads `n->key`, then `n->val`. ASan: `heap-use-after-free READ`. **The value is STABLE** (`controls/repro.py`) |
| PUT that HITS the freed object | stores `n->val` **inside** the freed chunk. ASan: `heap-use-after-free WRITE`, size 1, measured on `adversarial-many.bin` |
| DEL on the victim's bucket | the same walk, then a SPLICE that WRITES through `n->lp` -- the word glibc's tcache has overwritten -- so a plain build **SIGSEGVs**, and the write lands at an allocator-chosen address |
| ⚠ **the same DEL, two statements later** | **`free(n)` on an object TRIM already freed — CWE-415 DOUBLE FREE.** Reachable on `adversarial-uaf-write.bin` and invisible to every detector on this box except an allocator interposer, because the SEGV above arrives first. `NOTES.md` 2d |

**One omitted block, THREE harm shapes, selected by the input** — ⚠ this line said
*two* until `TASK_150`, and the third was in the source all along. And **the READ
path is CORRECT while the DESTROY path is INCOMPLETE**, which is the INVERSION of
`p27`, `p29` and `p32`: all three keep a correct free discipline and put the
missing check on the READ. There is no test to add on this rung's read path.

## ⚠⚠ The C-mechanism distinction, stated first because a reviewer will attack it first

```
p27   individually malloc'd records reached by a SLOT NUMBER the input supplies;
      the stale reference is a HANDLE in a STACK TABLE, and `h < ntab &&
      live[h] == 1` is a question the program can ask because there IS an `h`.
p29   a real free() of a whole record and a stale ADDRESS held in a STACK LOCAL
      across it. The read path is what forgets to check.
p32   NOTHING IS ALLOCATED AND NOTHING IS FREED; the harm is ALIASING inside a
      program-owned pool.
p28   the stale reference is a POINTER INSIDE ANOTHER HEAP OBJECT (`hn`) or in
      `bucket[]`. THE INPUT NAMES AN OBJECT ONLY BY KEY and the program finds it
      by WALKING: there is no slot number, no liveness bit and no generation
      anywhere in either C rung, so p27's guard has NO ANALOGUE BECAUSE THERE IS
      NO `h`. And the omission is on the DESTROY path.
```

**`controls/harm_sites.py` makes the site claim checkable rather than adjectival.**
It ships one adversarial window for each of the two sites, decides which site each
lands on by counting -- in the HARDENED arm, before any free -- which branch TRIM's
splice takes, and then runs ASan over the BUGGY arm on both. Positive control on
both compilers; hardened arm silent on both windows.

## What the safety line has to notice, and what notices it

```
p27   if (h < ntab && live[h] == 1)         is the ALLOCATION there?
p29   if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)
p32   if (h == NIL) ... else if (gen[h] != g)
p28   the victim is on TWO lists. LEAVE THE OTHER ONE.
          if (victim->hp != NULL) victim->hp->hn = victim->hn;
          else                    bucket[vb]     = victim->hn;
          if (victim->hn != NULL) victim->hn->hp = victim->hp;
```

The first three are TESTS on a read path and the last is a WRITE on a destroy
path, which is why no detector-shaped question ("is this reference still valid?")
has an analogue here. What ASan sees is the CONSEQUENCE, one operation later and
in a different arm.

## ⚠⚠ The one thing every Rust rung had to give up, disclosed and measured

Safe Rust cannot write an object onto two intrusive lists -- an object with two
list memberships is an object with two owners. **So every Rust rung, including
the unsafe one and the proof, replaces the four POINTERS with four SLOT NUMBERS
into a table.** `unsafe.rs` follows the safe rungs so that R4 and R5 stay
byte-comparable and so that the proof can rest on a per-slot invariant rather
than on the full doubly-linked-list well-formedness an address-keyed permission
map would need (`TASK_091`).

That is a real divergence from the mechanism the row is admitted on, so it is
**measured rather than argued**: `controls/arm_rawptr.rs` is the faithful
raw-pointer port of BOTH C arms, from one macro expansion, and
`controls/rust_arms.py` shows it agrees with the shipped rungs on every input
while **Miri reports undefined behaviour on its BUG arm on all four adversarial
inputs and on nothing else**. `NOTES.md` 5 prices the divergence; `NOTES.md` 4b
reports what the safe rungs do with the same omission, and it is not what anyone
predicted.

## Why every benign window must leave the poisoned buckets alone

⚠ **The benign invariant is SHARPER here than on `p27` or `p29`.** Their rule is
a condition on ONE later operation; here **a TRIM poisons its victim's bucket
permanently** -- the freed object stays in that chain for the rest of the window,
so *any* later PUT, GET or DEL whose operand lands in it touches freed storage.
`inputs/gen.py` tracks the poisoned set, never emits an operand that lands in
one, and then CHECKS the property by running `model.py`'s own `_sim_buggy` over
every window of every blob it writes.

⚠ **What is NOT a reason here, and it is `p27`'s and `p29`'s first reason:**
p28's R1 checksum is REPRODUCIBLE -- 1 distinct value in 20 runs, on every
adversarial input, in all four (compiler x opt) cells, **although R1 reads freed
heap**. The layout is why: the links come first, so glibc's tcache clobbers `lp`
and `ln` and leaves the `key`/`val`/`hn`/`hp` the stale walk reads. p28's
adversarial rows are excluded from the agreement set because they DISAGREE, not
because they are unstable.

## ⚠⚠ And what that reproducibility does NOT buy -- settled with a run at `TASK_146`

`TASK_143_REPORT` §2.2 and `.memory/06-catalogue.md` said it makes p28
*"GATABLE against `model.py` on its adversarial inputs where `p27` and `p29` are
NOT"*. **That is false.** `harness/check.py`'s `inputs_of` splits the matrix on
the `adversarial` prefix, stage 2 is handed `good_models` only, and stage 4
RECORDS behaviour -- its docstring says so and its only `rep.fail` concerns a
declared `expected_hang`. Across the three built temporal rows' committed gate
records, **54 adversarial rows carry `diverges: true` inside a `PASS` verdict
with 0 failures**. ✅ What it DOES buy is a PINNABLE FIGURE, which `p29`
explicitly cannot have, and `controls/repro.json` carries it.

⚠ The one thing that IS required on an adversarial input is `sanitizer_expect`:
`check_sanitizers` is handed `all_models`, so an input declaring `"fires"` fails
the gate if the sanitiser stays silent.

## The C/Rust arity gap, and `driver.call_args`

The C loop calls `kernel(buf, n_blob, k * stride, stride)` and the Rust loop calls
`kernel(buf, k * stride, stride)`. `driver.call_args` declares which argument
*positions* of a named call are the canonical ones. **This is p14's pin
unchanged**, inherited through p27, p29 and p32; p28 adds no new declaration
surface.

## The machine-readable contract

Everything in the block below is a **pin**: `harness/check.py` fails the pattern
when the tree stops matching it. p01's `spec.md` explains what each pin closes;
what is worth saying here is the arithmetic behind the two obligation counts and
what the identity pin is measuring.

| pin | why |
|---|---|
| `verus.obligations` = 23 | **5 consts + 1 `derive` + 2 recursive spec fns + 4 object ops + `alive_link` 1 + `walk` 2 + `kernel` 3 + `main` 5.** Every function term was measured with `--verify-function <name> --verify-root` (`.temp/t146/obligations.log`), and ⚠ **the non-function terms were measured too** rather than assumed -- `.temp/t146/obl_probe.log` adds a bare `const` (+1), a BARE struct (+0) and a `#[derive(Clone, Copy)]` struct (+1) in turn, which reproduces `TASK_140` on this file. `global layout` carries ZERO. |
| `verus.twin_obligations` = 28 | 23 shipped + **5**, one per trusted item inside the twin regime. ⚠ **p32 owes THREE and p28 owes FIVE**, and the two it adds back are `vstd::raw_ptr::allocate` and `deallocate` -- because p28 really does allocate and free. |
| `identity` `O0: differ`, `O3: norel` | **p29's pin exactly, for p29's reason.** ⚠⚠ And it earned its keep: with `nmade = nmade + 1` sitting in a different place in `unsafe.rs` and `verus.rs`, the pair measured `differ` at BOTH levels. The identity pin is what found the drift; `NOTES.md` 6c. |
| `miri.required: true` | derived from the seven trusted items. ⚠⚠ **What Miri finds on the shipped rung is NOTHING** -- the shipped rung is correct, and in its representation the bug would not be UB even if it were there. The arm that can see it is `controls/arm_rawptr.rs`, and it fires. |

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == cache_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (cache_fold). p28's bindings are the READ-ONLY set p03, p06, p11, p12, p14, p16, p17, p05, p07, p27, p29 and p32 use and NOT p02's before/after set: p28's objects are allocated AND FREED inside the kernel, so no buffer crosses the signature and there is nothing for an `after` binding to name. THE SECURITY PROPERTY IS CARRIED BY ONE BLOCK ON ONE PATH -- the hash-chain splice in TRIM -- and at R5 it is discharged as an ORDINARY FUNCTIONAL POSTCONDITION. THAT IS THIS ROW'S R5 RESULT AND IT IS THE OPPOSITE OF WHAT ITS C SIDE SUGGESTS. `rec_close` consumes the victim's `PointsTo` and its `Dealloc`, so nothing in R5 can READ a freed object -- a real temporal guarantee, and `controls/proof_mutants.py`'s A6 shows the linear resources also force the epilogue. But what `c/kernel.c` forgets is not a read, IT IS A LINK, and leaving a slot number behind consumes nothing: A4-spec-weaken deletes the splice from the exec code AND from the abstract machine `trim` and it VERIFIES. \u26a0\u26a0 THAT IS p32's SHAPE AND IT IS SHARPER HERE: p32 had no linear resource at all, so of course none forced its conjunct; p28 HAS them, consumed by a real `free`, and they still do not reach the destroy path's omission, because the linear argument only ever bites at a READ. The three-cell form is what makes it a result rather than an assertion -- A1 exec-only FAIL, A3 spec-only FAIL, A4 both VERIFY -- and A5 is the contrast arm that fails for a PERMISSION reason so the battery can tell the two failure modes apart. THE `ensures` IS THE FUNCTIONAL ONE: `run` is an abstract machine carrying the objects, the bucket array, both link sets, the liveness sequence and the two list ends, and it says the accumulator is what that machine computes -- so a kernel that left a freed object in a chain, or that spliced the wrong list, or that truncated at a different SLOTS, is rejected. WHAT THE `ensures` DELIBERATELY DOES NOT SAY is that `nops` is honest, that the op stream is well formed, or that either list is acyclic. `run` specifies what the PROGRAM does -- stop when the window runs out, fold SENT for a PUT past the budget, fold SENT for an absent key, fold SENT for a TRIM of an empty cache -- so degenerate.bin and all five adversarial files are INSIDE the verified domain and every checked rung agrees with model.py on all of them. A `requires` that the op stream never trimmed a bucket it later touches would be a precondition about the contents of a file that no honest loader can discharge (`.memory/02-bench-rules.md`), and it would delete every row the pattern exists for. \u26a0 ONE PLACE THE SPECIFICATION IS NOT LITERALLY THE C PROGRAM, stated rather than hidden: every splice arm of `put_new`, `del_at` and `trim` tests `alive(st, x)` where C tests `x != NULL`. In the checked kernel the two are the same test and neither can fire; they are spelled `alive` because the exec code spells them `alive_link(&live, x)`, and it spells them that way because the alternative is the doubly-linked-list invariant that would let `x != NIL` discharge `alive(st, x)`. NOTES.md 5 counts the ten sites.",
  "idiom": {
    "required": [
      {
        "c": "THE SAFETY LINE, and the only thing c/kernel.c omits: the hash-chain splice in TRIM, `if (victim->hp != NULL)` followed by `victim->hp->hn = victim->hn;` and `bucket[vb] = victim->hn;` and `victim->hn->hp = victim->hp;` in c/kernel_hardened.c. c/kernel.c goes straight from `tail = victim->lp;` to `free(victim);` and is otherwise character-identical; controls/safety_line.py preprocesses both and measures a pure +9 / -0 addition.",
        "rust": "THE SAFETY LINE, in all four Rust rungs, spliced through SLOT NUMBERS because that is what the representation forces: three spellings, one per representation, each scoped-absent on the rungs that are not its own: `bucket[vb] = tab[v].as_ref().unwrap().hn;` in safe_naive.rs, `bucket[vb] = hnv;` in safe_tuned.rs, and `arr_set_unchecked(&mut bucket, vb, vo.hn);` in unsafe.rs and verus.rs. \u26a0 Not one of the four gets any part of it from the language -- see the why key, and controls/arm_safe_bug.rs for what deleting it does in safe Rust."
      },
      {
        "c": "TRIM'S VICTIM IS THE EVICTION LIST'S OLDEST END AND IT IS REACHED WITHOUT A CHAIN CURSOR, in both C rungs: `victim = tail;`. That is why TRIM is the path that forgets and DEL is not.",
        "rust": "the same victim, in all four Rust rungs: `tail` is read into `v` and nothing on the path holds a bucket cursor."
      },
      {
        "c": "DEL SPLICES BOTH LISTS AND THEN FREES, in both C rungs -- it arrives ALONG the chain, so it is already holding the cursor TRIM lacks: `if (n->hp != NULL)`.",
        "rust": "the same splice in all four Rust rungs, on the victim's four links read out of the object."
      },
      {
        "c": "THE ALLOCATION BUDGET IS ALSO THE WALK'S FUEL, in both C rungs: `nmade < P28_SLOTS` and `steps < P28_SLOTS`. See the why key for why a C reader would not write the first.",
        "rust": "the same two, in all four Rust rungs: `nmade < SLOTS` and `steps < SLOTS`."
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
        "c": "the bucket is the operand modulo the table width, so every operand lands somewhere: `a % P28_NB` in both C rungs.",
        "rust": "the bucket, in all four Rust rungs: `a % NB as u8`."
      },
      {
        "c": "a rejected operation folds the SENTINEL rather than being skipped, so the fold's length is a function of the op count alone: `SENT` in both C rungs.",
        "rust": "the sentinel fold, in all four Rust rungs: `SENT`."
      },
      {
        "c": "the fold is a serial Horner chain over `acc`, spelled with the literal multiplier, ONCE per operation: `acc = acc * 31 +` in both C rungs.",
        "rust": "the fold, in all four Rust rungs, spelled with the literal multiplier: `acc.wrapping_mul(31).wrapping_add`."
      },
      {
        "c": "the OBJECT COUNT is folded last, so a rung that made a different number of objects cannot produce the same checksum: `return acc * 31 + (uint64_t)nmade;` in both C rungs.",
        "rust": "the same, in all four Rust rungs: `acc.wrapping_mul(31).wrapping_add(nmade as u64)`."
      },
      {
        "c": "THE LINKS COME FIRST IN THE STRUCT, in both C rungs: `struct p28_obj *lp, *ln;`. It is what makes R1's stale read reproducible rather than ASLR-dependent -- c/kernel.h's LAYOUT NOTE, and controls/repro.py measures both sides of it.",
        "rust": "not applicable: the Rust rungs' links are slot numbers, so there is no layout question. The why key states the divergence and controls/arm_rawptr.rs measures it."
      },
      "THE EPILOGUE FREES EVERY OBJECT STILL ALIVE, in all seven rungs, so NEITHER C rung LEAKS, and NEITHER DOUBLE-FREES IN THE EPILOGUE -- TRIM unlinks its victim from the eviction list before freeing it, so the epilogue's walk cannot reach it. It is spelled three ways because the representation forces three: the C rungs walk the eviction list, unsafe.rs and verus.rs scan the slot table, and safe_naive.rs and safe_tuned.rs have no epilogue at all because dropping the table IS the loop. ⚠⚠ THIS ENTRY READ 'so NEITHER C rung leaks and neither double-frees', UNSCOPED, UNTIL TASK_150, AND THE SECOND HALF OF THAT WAS FALSE. R1's DEL double-frees: its walk can reach an object TRIM already released and then run the splice to completion, free(n) included. Measured on adversarial-uaf-write.bin with a --wrap=malloc,--wrap=free interposer under LEAKING semantics -- the semantics model.py and all four Rust rungs implement, since slots are never recycled -- R1 gives mallocs=4 frees=5 doublefree=1 where R1h gives 4/4/0, on the same input through the same driver, with the safety line as the only difference; every other shipped input is balanced in both arms. The real allocator masks it, because glibc's tcache overwrites the freed chunk's user offsets 0 and 8, which are exactly lp and ln, so the splice faults two statements before free(n). THE LEAK HALF OF THE OLD SENTENCE IS TRUE AND STAYS. This is PROTOCOL rule 6's second half -- the hash matched and the measurement refuted the claim -- and it is p46's shape on a second pattern. NOTES.md 2d and 10 carry the numbers and the sha256 disclosure."
    ],
    "forbidden": [
      "`realloc(`",
      "`calloc(`",
      "`Vec::with_capacity`",
      "`VecDeque`",
      "`HashMap`",
      "`Rc<`",
      "`Weak<`",
      "`RefCell`",
      "`ManuallyDrop`",
      "`mem::forget`",
      "`Box::leak`",
      "`Box::into_raw`"
    ],
    "why": "POLICY ADOPTED AFTER MEASURING (`.memory/01-ladder.md` finding 14): a published spread cannot carry a safety number, so what ships is a named-spelling standard -- the tokens below must appear literally, uniform across all seven rungs, with ONE measured clause: a rung spells the same operands the way its language forces. ONE OMITTED BLOCK, ON THE DESTROY PATH, AND THAT IS THE ROW. An object here carries TWO INTRUSIVE LINK SETS -- a doubly linked eviction list (`lp`/`ln`) and a doubly linked hash chain (`hn`/`hp`) -- so IT IS ALIASED BY TWO LISTS AT ONCE AND MEMBERSHIP IS NOT OWNERSHIP. TRIM reaches its victim through the EVICTION list, so it holds no chain cursor and has to go and get one; DEL reaches its victim by WALKING THE CHAIN, so it is already holding one. THE PATH THAT ARRIVES FROM THE OTHER LIST IS THE ONE THAT FORGETS, and that is the shape of this bug in real code rather than an arbitrary choice of arm. THE READ PATH IS CORRECT AND THE DESTROY PATH IS INCOMPLETE, which is the INVERSION of p27, p29 and p32 -- all three keep a correct free discipline and put the missing check on the READ. There is no test to add on this rung's read path. THE DANGLING POINTER ENDS UP INSIDE ANOTHER HEAP OBJECT'S `hn` FIELD, or in `bucket[]` when the victim was the chain head -- NOT in a stack table (p27's `tab[]`), NOT in a stack local (p29's `g_saved`), NOT in a program-owned pool (p32, which frees nothing). `controls/harm_sites.py` measures both sites separately, in the HARDENED arm and before any free, and ASan reports a heap-use-after-free on the buggy arm at each. AND THERE IS NOTHING THE INPUT CAN INDEX: the input names an object only by KEY and the program finds it by walking, so p27's `h < ntab && live[h] == 1` has NO ANALOGUE BECAUSE THERE IS NO `h`. Neither C rung contains a slot number, a liveness bit or a generation. THE ALLOCATION BUDGET `nmade < P28_SLOTS` IS THE CACHE'S ONLY SIZE LIMIT AND IT IS ALSO THE WALK'S FUEL. It is a budget per WINDOW rather than a live capacity, and it is spelled that way because R2-R5 hold their objects in a FIXED-SIZE TABLE with slots never recycled -- safe Rust cannot hold an intrusive pointer list, so every Rust rung indexes a slot table instead -- and all seven rungs must agree on every window. p29's C rungs carry `ntab < TABCAP` for exactly the same reason and say so. TRIM IS A SHRINKER: something outside the cache asks it to give storage back, which is why there is no capacity test and why TRIM is an opcode rather than a consequence of PUT. THE RUST RUNGS DIVERGE FROM THE C MECHANISM IN ONE DISCLOSED WAY AND IT IS MEASURED RATHER THAN ARGUED: the C rungs store the four links as POINTERS, and every Rust rung stores them as SLOT NUMBERS into a table. Safe Rust has no choice -- an object on two intrusive lists is an object with two owners -- and unsafe.rs and verus.rs follow it so that R4 and R5 stay byte-comparable and so that the proof can be carried by a per-slot invariant instead of the full doubly-linked-list well-formedness (`hn[hp[j]] == j` and its three siblings) that an address-keyed permission map would need. `controls/arm_rawptr.rs` is the FAITHFUL raw-pointer port of both C arms, from one macro expansion; it agrees with the shipped rungs on every input, and Miri reports undefined behaviour on its BUG arm on all four adversarial inputs and on nothing else. That is the measurement the divergence owes, and NOTES.md 5 prices it. THE ONE EXEC CONJUNCT THE C RUNGS CANNOT SPELL is the liveness half of a link test: the walk's `live[cur] == 1u8` and `alive_link`'s second half, ten sites in unsafe.rs and verus.rs. Not one of them can fire -- a correct chain holds only live objects -- and they are there because the alternative is the list invariant. p29 could put its liveness conjuncts in its C rungs too; p28 CANNOT, and the reason is this row's own headline: p28's C links are POINTERS and there is no `live[]` bit anywhere in either C rung. THE PROPERTY THAT MAKES THE ROW DISTINCT AT C LEVEL IS THE PROPERTY THAT MAKES THAT CONJUNCT UNSPELLABLE THERE. THIS PATTERN PUBLISHES NO RUNG-TO-RUNG COST AT ALL (NOTES.md 8), and the absence is stated rather than left to read as a zero. It is not shyness: `TASK_093_REVIEW` measured that a p28 with a safe index arena against a raw-pointer unsafe rung would have published `safe Rust is 6.02x CHEAPER than unsafe` with 108.4% of the gap IN THE ALLOCATOR and the bounds check at 3.0% of the magnitude AND THE OPPOSITE SIGN, and `TASK_091` measured that 4.0 of a 12.5 R3->R4 gap is INDEX SCALING rather than checking. The rungs here differ in ALLOCATION SIZE (40 bytes of pointers in C against 6 bytes of slot numbers in Rust), in EPILOGUE SHAPE (C walks the eviction list, R4/R5 scan the slot table, R2/R3 drop the table) and in the ten non-firing liveness conjuncts above. Any of the three would confound a spread, so none is published. p29 ships the same way. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
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
      "verus.rs": 23
    },
    "twin_obligations": {
      "verus.rs": 28
    },
    "obligations_note": "23 = FIVE consts (NB, SLOTS, OBJSZ, NIL, SENT) 1 each + the `#[derive(Clone, Copy)]` on `Obj` 1 + descend 1 + run 1 + rec_open/rec_close/rec_read/rec_write 1 each + alive_link 1 + walk 2 + kernel 3 + main 5. Every FUNCTION term was measured with `./verus_run.py verus.rs --verify-function <name> --verify-root`; the loop is `.temp/t146/obligations.sh` and the log is `.temp/t146/obligations.log`. THE NON-FUNCTION TERMS WERE MEASURED TOO rather than assumed (`.memory/03-measurement.md` 17 is the rule): `.temp/t146/obl_probe.sh` adds one bare `const`, one BARE `#[repr(C)]` struct and one `#[derive(Clone, Copy)]` struct in turn -- the const moves the count by 1, the BARE struct moves it by 0, and the derive moves it by 1, which is TASK_140's measured rule reproduced on this file. \u26a0 `global layout Obj is size == 6, align == 1;` carries ZERO: the arithmetic sums to 23 exactly without it. The zero terms are checkable the same way: u32_at, nops_at, val_of, alive, bkt, put_new, del_at, trim, step, st0, cache_fold, rec_ok, dal_ok, links_ok, base and wf are NON-RECURSIVE spec fns and report 0, while `descend` and `run` are RECURSIVE and carry one termination query each; buf_get_unchecked, arr_get_unchecked, arr_set_unchecked, rec_alloc, rec_free, load_input and emit are external_body and report 0.",
    "twin_obligations_note": "The obligation count in the OTHER configuration -- `verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 23 shipped + 5, one per trusted item inside the twin regime: slb_twin_buf_get_unchecked, slb_twin_arr_get_unchecked, slb_twin_arr_set_unchecked, slb_twin_rec_alloc and slb_twin_rec_free. That is p27's and p29's FIVE exactly, and it is five rather than p32's three because p28 DOES allocate and free: `vstd::raw_ptr::allocate` and `deallocate` are borrowed, so their twins are owed. `load_input` and `emit` are outside the regime (external_body with no `ensures` and no `unsafe` body) and have no twins.",
    "unsafe_justifications": {
      "verus.rs": {
        "arr_set_unchecked": "`x` is a pure VALUE parameter: it is stored into the array and is never used as an address, an index or a length, so there is no precondition a caller could usefully be asked for -- every `T` is a legal thing to store in a `T` slot. The two parameters that DO decide whether the unchecked store is defined, `v` and `i`, are both constrained by `i < old(v)@.len()`, which for a `&mut [T; N]` reads `i < N`. This is the parameter-coverage false positive `.memory/04-verus.md` names; p03 was the first pattern to exercise it, p12 the second, p06 the third, p14 the fourth, p27 the fifth, p29 the sixth, p32 the seventh and p28 the eighth."
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
        "bkt": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "put_new": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "del_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "trim": {
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
        "cache_fold": {
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
        "links_ok": {
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
            "r.2@.size() == OBJSZ",
            "r.2@.align() == 1",
            "r.2@.provenance() == r.0@.provenance"
          ]
        },
        "rec_close": {
          "external": null,
          "requires": [
            "pt.ptr() == p",
            "dl.addr() == p.addr()",
            "dl.size() == OBJSZ",
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
        "alive_link": {
          "external": null,
          "requires": [
            "live@.len() == SLOTS",
            "x == NIL || (x as int) < SLOTS as int"
          ],
          "ensures": [
            "r == (x != NIL && live@[x as int] == 1u8)"
          ]
        },
        "walk": {
          "external": null,
          "requires": [
            "base(tab@, live@, bucket, st, nmade, *perms)",
            "start == NIL || (start as int) < nmade"
          ],
          "ensures": [
            "r == descend(st, start, k, SLOTS as nat)",
            "r.0 == NIL || (r.0 as int) < nmade",
            "r.1 ==> alive(st, r.0)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == cache_fold(buf@, off as int, len as int)"
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
    "note": "work_per_call is **bytes of the window** -- `stride`, 52 on small and 244 on large -- which is p27's, p29's, p32's, p16's, p05's, p11's, p12's, p06's and p14's denomination. WHICH WAY THE ESTIMATE ERRS: STRICT. It OVER-counts by the 4 window-header bytes, which are decoded as a u32 and are not operations. It UNDER-counts by everything else, and that dominates: each 2 window bytes is one OPERATION, three of the four opcodes begin with a CHAIN WALK of up to SLOTS steps, and PUT, DEL and TRIM each splice up to four links while two of them call the allocator, which is tens of instructions in glibc. model.py declares NO min_ir_per_work, so the harness default applies unchanged. The two probe inputs differ in work_per_call (52 vs 244) precisely so check.py's d(Ir)/d(work) assertion has two shapes and can run at all."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "norel",
      "why": "R4 == R5 up to pc-relative displacement fields at `-O3`, and DIFFER at `-O0` -- p29's pin exactly, for p29's reason. The `-O3` residue is link layout: the crate names differ in length, so the pc-relative displacements do. The `-O0` difference is `rec_open`: unsafe.rs writes `*q = v` and verus.rs calls vstd's `ptr_mut_write`, which at `-O0` expands to a sequence of 16- and 32-bit moves where the bare store is one instruction. \u26a0 It is NOT p32's `exact`, and the reason is that p32 has no pointer write at all. \u26a0\u26a0 AND ONE ALIGNMENT WAS MEASURED RATHER THAN ASSUMED: with `nmade = nmade + 1` in a different place in the two files the pair was `differ` at BOTH levels, on register allocation and one extra instruction. The two exec bodies are statement-for-statement identical now, and NOTES.md 6c records that the identity pin is what found the drift."
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
    "reason": "Since TASK_010 `.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted item, which check.py DERIVES from verus.rs rather than reading from this flag. p28 has seven, so Miri runs. \u26a0\u26a0 AND NOTE WHAT MIRI FINDS ON THE SHIPPED RUNG: NOTHING, on any input including all five adversarial ones -- not because the bug is invisible to Miri but because THE SHIPPED unsafe.rs IS CORRECT and, in the slot-table representation it uses, the bug would not be UB even if it were there. `controls/rust_arms.py` supplies the arm that can see it: `controls/arm_rawptr.rs` is the faithful raw-pointer port of both C arms, and Miri reports `Undefined Behavior: in-bounds pointer arithmetic failed` on its BUG arm on all four adversarial inputs and on nothing else. What Miri buys on the shipped rung is what it buys on p08: a trusted body that read one element past an array would satisfy every `ensures` in verus.rs and be invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req. Cost: check.py rewrites n_iters to 4.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). If it is missing, this row is blocked rather than failed."
  }
}
```
