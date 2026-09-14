# ph56 — an opcode chosen by arithmetic, and the guard replicated onto some arms

**PHP 5.0.0, `Zend/zend_compile.c:736-780`, corpus row CRASH-041, tier
`modelled`.** `zend_do_end_variable_parse` selects a fetch opcode's ACCESS MODE
by adding a multiple of three to the opcode the parser built, over the layout
`zend_compile.h:636-638` documents with its own exclamation mark — *the
following 18 opcodes are 6 groups of 3 opcodes each, and must remain in that
order!*. Three of the six combinations are illegal, because an append dim
(`$a[]`) has no dimension to read. **Two of the three carry the test. `case
BP_VAR_IS:` at `:763-765` is `opline->opcode += 6;` and nothing else.**

⭐ **And the harm is not where reading `:763` alone suggests.** Four lines later
`zend_do_isset_or_isempty` rewrites the last opline a SECOND time (`:3229`), so
`ZEND_FETCH_DIM_IS` exists for four lines and is overwritten;
`zend_fetch_dim_is_handler` never runs on this row's trigger. What reaches the
executor is `ZEND_ISSET_ISEMPTY_DIM_OBJ` carrying an `IS_UNUSED` op2, and its
handler reads that operand through `get_zval_ptr` — whose `case IS_UNUSED:` is
an explicit `return NULL;` (`:118-121`) — and dereferences the result at
`switch (offset->type)` (`:3973`) **with nothing in between**. Measured on a
pristine-sourced 5.0.0 CLI: `SEGV on unknown address 0x000000000014`, and
`0x14` is `offsetof(zval, type)`.

⚠⚠ **The defect is a MIS-COMPILE and the NULL read is only how it manifests.**
`inputs/adversarial-nullderef.bin` and `inputs/adversarial-chain.bin` differ in
**one statement record**, mis-compile by exactly as much, and the first SEGVs
while the second **silently grows the array** and returns a wrong answer with
exit 0. `NOTES.md` §6 prices the pair.

⭐ **Verus needs no substitution here, and `ph55` did.** That row's dispatch is a
call through a function pointer and Verus refuses the TYPE; this row dispatches
with a `switch`, because every opcode this compiler emits **has** a handler —
what is missing is the OPERAND. `NOTES.md` §7.

**R1h is `1e708a5aeb30`** (Marcus Boerger, 2004-08-29, *"Bugfix #29882 isset
crashes on arrays"*) — three lines, the `BP_VAR_R` arm's own guard copied
across, and **`git apply` places it** at offset −2. `NOTES.md` §5 has the run,
and the `--check` that lied.

The machine-readable contract follows.
`harness-php/gate.py ph56-fetchmode-arith` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == ph56_run(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (ph56_run). `ph56_run` is model.py's SECOND, independent implementation -- a PURE FOLD over an immutable state tuple, mirroring verus.rs's `c_stmt`/`parsed`/`e_step`/`e_run` one unfolding at a time -- and not the imperative `_Machine` simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic windows model.py builds itself, spanning the whole (mode x base x op2-type x chain) cross product, operand encodings past every modulus, and both configurations of the compiler. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. A THIRD spelling, `_dumb`, derives the EMITTED OPCODE SEQUENCE by TABLE LOOKUP -- the six deltas read off zend_compile.c:756-774 into a dict and applied by index -- checks it against what the branch-per-arm compiler actually emitted, and only then replays. That is the one spelling that cannot share a transposed-delta mistake with `compile_window`, and a transposed delta is exactly what this row is about.",
  "idiom": {
    "required": [
      {
        "c": "`opline->opcode += 6` -- zend_compile.c:764, the BP_VAR_IS arm's delta, and the whole defect is that this line has no test above it while :753 and :771 do. The six deltas are arithmetic over zend_compile.h:636-638's six-groups-of-three layout, which upstream documents with its own exclamation mark, so keeping the literal value keeps this row's arithmetic identical to upstream's. A rung that selected the opcode from a table instead would be measuring a different compiler and would make the arm-by-arm asymmetry invisible. ONE BACKTICKED SPELLING IN THIS ENTRY, deliberately: the arm names are C enumerators the Rust rungs spell differently, and a pin on one of them would be pinning a token rather than the arithmetic.",
        "rust": "`o.opcode.wrapping_add(6)` -- zend_compile.c:764, the BP_VAR_IS arm's delta, and the whole defect is that this expression has no test above it while the BP_VAR_R and BP_VAR_UNSET arms do. The six deltas are arithmetic over zend_compile.h:636-638's six-groups-of-three layout. `wrapping_` rather than plain addition, because upstream's compound assignment on a zend_uchar wraps and a panic here would be a different program."
      },
      {
        "c": "`case PH56_IS_UNUSED:` with `return NULL;` -- zend_execute.c:118-121, and it is an EXPLICIT case rather than a fall-through. It is CORRECT: an operand that is not there has no zval. Every caller that can be handed an IS_UNUSED operand is supposed to know it cannot be, and this row is about the one that was handed one anyway. An extraction whose operand fetch returned a sentinel zval instead would delete the harm and leave the row measuring a mis-compile with no consequence.",
        "rust": "`Option<usize>` -- zend_execute.c:118-121's explicit return of NULL, as the return TYPE of the operand fetch. In Rust the absence is in the type, which is the whole reason the four Rust rungs turn a read of address 0x14 into a panic with a message: the Option cannot be dereferenced without being opened. That is a different OUTCOME, not a different program -- the compiler still emits the opline with the absent operand."
      },
      {
        "c": "`switch (offset->type)` with `get_zval_ptr` -- zend_execute.c:3973 and :3961, THE DEREFERENCE and the read it dereferences, with nothing between them: no NULL test, no assertion, no operand-kind check. The pointer is NULL exactly when op2 is IS_UNUSED, and the compiler emitted exactly that. Testing it here would delete the row.",
        "rust": "the operand open, and it is PER RUNG because the lever between R3 and R4 IS this expression: safe_naive.rs and safe_tuned.rs write a CHECKED unwrap and unsafe.rs and verus.rs write the unchecked one through the row's tenth trusted accessor. Both are the same operation on the same Option; one tests and one does not, and verus.rs's compile-pass invariant is what licenses the one that does not. Each spelling is SCOPED-ABSENT from the other pair by design and the gate reports it as such. NO BACKTICKED SPELLING ON THIS SIDE AT ALL, deliberately: a pin here would name a spelling half the Rust rungs cannot carry, which is the shape that put twenty obligations out of contract at TASK_018."
      },
      {
        "c": "`last_op->opcode = PH56_ISSET_ISEMPTY_DIM_OBJ;` -- zend_compile.c:3229, the SECOND rewrite, which runs AFTER the mode switch and rewrites the LAST opline of the fetch list only. Two things hang on that word LAST: the opcode the executor sees is 115 and never 90, so zend_fetch_dim_is_handler is not on this row's path at all; and a chain's LEADING append opline survives as 90, which is the row's second, silent harm. A rung that folded the two rewrites into one would lose both.",
        "rust": "`o.opcode = ISSET_ISEMPTY_DIM_OBJ;` -- zend_compile.c:3229, the SECOND rewrite, which runs AFTER the mode switch and rewrites the LAST opline of the fetch list only. Two things hang on that word LAST: the opcode the executor sees is 115 and never 90; and a chain's LEADING append opline survives as 90, which is the row's second, silent harm and what the chain input measures."
      },
      {
        "c": "`ex->slots[PH56_UNINIT].refcount++` -- zend_execute.c:938, upstream's increment on the uninitialized zval, and it is NOT a defect: it is the implementation of the append operator, it is what the write and read-write appends reach on every legal append, and the FAILURE arm decrements it again at :942. It is pinned because the row answers *is the global's refcount left unbalanced?* with a NUMBER -- every slot's refcount is folded into the returned u64 -- and a rung that dropped the field would answer it with an argument instead.",
        "rust": "`UNINIT as usize` with `wrapping_add(1)` and `wrapping_sub(1)` -- zend_execute.c:938 and :942 on the uninitialized zval, the process-global the append takes a reference to. NOT a defect: it is the implementation of the append operator and the FAILURE arm decrements it again. It is pinned because the row answers *is the global's refcount left unbalanced?* with a NUMBER -- every slot's refcount is folded into the returned u64 -- and a rung that dropped the field would answer it with an argument."
      },
      "R1h IS 1e708a5aeb30711f8b7b2a811377a13f2b23a8c9 (Marcus Boerger, 2004-08-29, 'Bugfix #29882 isset crashes on arrays') AND IT IS THREE LINES -- the BP_VAR_R arm's own append-dim guard, copied onto the BP_VAR_IS arm, same test and same message -- and R2 through R5 implement the same function, because the fix is COMPLETE for this defect: it removes BOTH of the row's harms and changes no benign answer. Nothing is invented and there is no second hunk to adjudicate. It APPLIES to 5.0.0 with git apply, at offset -2 lines, which is where this row parts company with ph55; controls/r1h_backport.py RUNS the apply and records the hunk header rather than asserting it, and it records that git apply --check returned 0 on a run in which nothing moved. WHICH ARM the hunk belongs to is settled by the SCREEN on this row and not by an offline argument, because the cited line is UNIQUE: case BP_VAR_IS: occurs exactly once in Zend/zend_compile.c, counted on the pristine tarball and re-counted on every invocation of the control. NO BACKTICKED SPELLING ANYWHERE IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements, the C rungs and the Rust rungs spell the three lines differently, and no single token decides it."
    ],
    "forbidden": [
      "`offset != NULL` and `offset.is_none()` -- TESTING THE OPERAND BEFORE READING IT. That is the check zend_execute.c:3973 does not have, and adding it deletes the row: the C would stop faulting on the adversarial input and the Rust rungs would stop panicking, and every rung would be measuring a different program. Note the absence of backticks in the rest of this entry, and it is not style: in a forbidden entry EVERY backticked span becomes a banned token, so an entry that quotes what it is PROTECTING bans that too -- item 100, three instances in three consecutive tasks. What the sentence says, in plain text: the Rust rungs do OPEN the Option, which is not the same thing as testing it. unwrap and unwrap_unchecked both ASSUME the operand is there, exactly as C does, and neither takes a different path when it is not.",
      "`unwrap_or` and `case PH56_IS_UNUSED: return &` -- SUBSTITUTING A DEFAULT OPERAND for an absent one. It keeps every index in bounds, silences every detector this row has, and computes a different function: the handler would report a value for an element the program never named. Upstream does not do it -- zend_execute.c:118-121 returns NULL and means it -- and 1e708a5aeb30 corrects the EMITTER rather than padding the reader.",
      "`opline->op2_type != PH56_IS_UNUSED` and `o.op2_type != T_UNUSED` -- MOVING THE GUARD INTO THE EXECUTOR. It is the most plausible repair and it is the wrong one twice over: it leaves the compiler emitting an opline whose operand contract its own handler cannot meet, which is the defect; and it does not touch the row's second harm at all, because the chain case reaches zend_fetch_dimension_address rather than the isset handler. Upstream's own answer is the opposite direction -- 1e708a5aeb30 is a COMPILE-time fix -- and the one arm upstream did move into the VM, BP_VAR_FUNC_ARG, it moved eleven months later and in a different file."
    ],
    "why": "ph56 is PHP 5.0.0's `zend_do_end_variable_parse` out of `Zend/zend_compile.c:736-780`, corpus row CRASH-041, tier `modelled`. ⚠⚠ THE CATALOGUE FILES THIS ROW AS `narrowed` AND THE BUILD REFUTES IT, MEASURED: harness-php/provenance.py reports the kernel overlap at **10% (14/143)** over the union of seven cited spans and **23% (7/30)** over the defect site alone, where `narrowed` leads a reader to expect 25%. The DEFECT SITE is lifted one for one -- six arms in upstream's order, upstream's five deltas, upstream's two guards and the third arm's absent one, the `while (le)` walk over every fetch-list element, the second rewrite four lines later, and a handler that reads op2 with nothing between the read and the dereference -- but the SCENERY is RE-EXPRESSED: the hash table is an array of DIM slots, `zval **` is an index, the fetch list is a two-element window, and the opcode set is thirteen opcodes standing for the 18 the six-groups-of-three layout names. ⚠ A tier is a COST and never a filter (PROTOCOL_PHP.md A1), and a tier read as STRONGER than it is, is the dangerous direction, so the row declares the weaker one and publishes the number. NOTES.md §2 and §12. THE IDIOM IS AN OPCODE CHOSEN BY ARITHMETIC OVER A FIXED-STRIDE LAYOUT, WITH THE LEGALITY TEST REPLICATED ONTO SOME ARMS AND NOT OTHERS. `zend_compile.h:636-638` says, in upstream's own words and exclamation mark, *the following 18 opcodes are 6 groups of 3 opcodes each, and must remain in that order!*, and `zend_do_end_variable_parse` selects an access mode by adding a multiple of three to the opcode the parser built: `-= 3` read (`:756`), nothing for write (`:759`), `+= 3` read-write (`:761`), `+= 6` isset (`:764`), `+= 9` func-arg (`:767`), `+= 12` unset (`:774`). THREE of the six combinations are illegal -- an append dim, `$a[]`, has no dimension to read -- and TWO of the three carry the test: `:752-757` raises *Cannot use [] for reading* and `:770-775` raises *Cannot use [] for unsetting*. ⛔⛔ `case BP_VAR_IS:` at `:763-765` is `opline->opcode += 6;` and nothing else. ⭐⭐ AND THE HARM IS NOT WHERE READING `:763` ALONE SUGGESTS. Four lines later `zend_do_isset_or_isempty` (`:3215-3240`) rewrites the LAST opline of the fetch list a SECOND time -- `case ZEND_FETCH_DIM_IS: last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;` at `:3229` -- so `ZEND_FETCH_DIM_IS` exists for four lines and is then overwritten, `zend_fetch_dim_is_handler` never runs on this row's trigger, and the opcode that reaches the executor is `ZEND_ISSET_ISEMPTY_DIM_OBJ` (115) carrying an IS_UNUSED op2. `zend_isset_isempty_dim_prop_obj_handler` (`:3958`) reads that op2 through `get_zval_ptr` at `:3961`, whose `case IS_UNUSED:` is an explicit `*should_free = 0; return NULL;` (`:118-121`), and dereferences the result at `switch (offset->type)` (`:3973`) with NOTHING in between. ⭐⭐⭐ MEASURED, NOT INFERRED: a pristine-sourced PHP 5.0.0 CLI under ASan answers `isset($a[])` with *SEGV on unknown address 0x000000000014* in `zend_isset_isempty_dim_prop_obj_handler`, and `0x14` is 20, which is `offsetof(zval, type)` on this ABI. `c/kernel.c` keeps upstream's field order and faults at the SAME offset in the same frame; `PH56_LAYOUT_ASSERT` is a C99 negative-array-bound assertion that fails the build if the offset ever moves. That is CWE-476 and it is a MEMORY error, not a logic defect. ⚠⚠ AND THE ROW SHIPS A SECOND HARM THAT NOTHING SEES. `:3223` rewrites the LAST opline only, so in `isset($a[][0])` the leading `[]` opline SURVIVES as `ZEND_FETCH_DIM_IS`, `zend_fetch_dim_is_handler` really does run, and `zend_fetch_dimension_address` takes the append arm at `:935-943`. Measured on the same CLI: `var_dump(isset($a[][0]))` prints `bool(false)`, `count($a)` goes 3 -> 4, and the exit code is 0. `inputs/adversarial-nullderef.bin` and `inputs/adversarial-chain.bin` differ in ONE STATEMENT RECORD, mis-compile by exactly as much, and the first SEGVs while the second returns a wrong answer with exit 0 and no diagnostic from any detector in this tree. `model.py::sanitizer_expect` derives `fires` from the NULL DEREFERENCE and not from the mis-compile, and says so in its own docstring. ⚠⚠⚠ AND THE REFCOUNT ON THE PROCESS GLOBAL IS BALANCED, WHICH IS A FINDING AND NOT A CONCESSION. `new_zval->refcount++` at `:938` is the implementation of `[]`: `$a[] = 1` (BP_VAR_W) and `$a[] += 1` (BP_VAR_RW) reach the same line on every legal append -- measured, NOTES.md §2 -- and the FAILURE arm decrements it again at `:942`. This kernel folds EVERY slot's refcount into the returned u64, so the balance is a number and not an argument. Upstream is careful at `:935-943`; the carelessness is one file away, in the compiler. ⚠⚠ THE SIBLING CENSUS IS NON-EMPTY AND ITS ANSWER IS NOT *AN OVERSIGHT*. Four arms lack the guard and only one was fixed. `BP_VAR_W` is what `[]` is FOR. `BP_VAR_RW` has NEVER been guarded, at compile time or run time, in any PHP from 5.0.0 to master, and `ext/opcache/tests/jit/assign_dim_op_001.phpt` carries it as an expected-to-succeed case. `BP_VAR_FUNC_ARG` is a live defect at 5.0.0 whose reachability is DECLARATION ORDER -- `zend_do_pass_param` (`:1411-1427`) asks for `BP_VAR_R` when the callee is already declared and `BP_VAR_FUNC_ARG` when it is not, so the same expression is a compile error or a silent array mutation depending on whether the function is written above or below the call -- and it was closed 11 and a half months later, AT RUN TIME, IN A DIFFERENT FILE, BY A DIFFERENT AUTHOR (`9183f91b506a`, Dmitry Stogov, 2005-08-10, bug #34064, three lines into `zend_fetch_dim_func_arg_handler`). Corroborated by counting: *Cannot use [] for reading* occurs 0 times in `php-5.0.0` and `php-5.0.4`'s `zend_execute.c` and once, at `:2135`, in `php-5.0.5`'s. Upstream's settled position, reached in 2005 and unchanged into PHP 8: the RW append and the by-reference argument append are FEATURES, only the by-value read is an error, and by-value-ness is not always knowable at compile time so that check belongs in the VM. `zend_delayed_compile_dim` at master `zend_compile.c:3154-3161` guards the SAME THREE ARMS and not the other three. `controls/census.py` re-derives all of this three ways on every invocation -- the parsed tarball switch, the row's own ladder, and a pristine 5.0.0 CLI -- with a 7-case selftest. ⚠ R1h IS `1e708a5aeb30` (Marcus Boerger, 2004-08-29, *Bugfix #29882 isset crashes on arrays*) AND IT IS THREE LINES: `BP_VAR_R`'s own guard copied onto `BP_VAR_IS`, same test, same message. Nothing is invented, and the fix is COMPLETE for this defect -- it removes BOTH harms and changes no benign answer. ⭐ UNLIKE `ph55`, `git apply` PLACES IT, at offset -2 lines; `controls/r1h_backport.py` RUNS it on every invocation and records the hunk header rather than asserting it. ⚠⚠ AND `git apply --check` LIED, LIVE, ON THE FIRST ATTEMPT: it returned 0 on a run in which nothing was applied, because the scratch path was gitignored in the enclosing repository; `gitignore_trap()` reproduces the trap on every run, so a future git that fixes the behaviour surfaces as a changed number rather than a stale paragraph. --check is not the test; the bytes are. ⚠ WHICH ARM the three lines belong to is settled by the SCREEN here and not by an offline argument, and that is the contrast worth keeping: `preimage_screen.py --id CRASH-041` returns `CANDIDATE` with `hits [[763, \"case BP_VAR_IS:\"]]` and `misses []`, and `case BP_VAR_IS:` occurs EXACTLY ONCE in `Zend/zend_compile.c` -- counted on the pristine tarball and re-counted by `controls/r1h_backport.py` on every run. `ph55` got the SAME VERDICT STRING on the strength of one `NEXT_OPCODE();` line that occurs 117 times in its file. ▶ The screen's verdict is not a scalar: its evidential weight is decided entirely by the uniqueness of the cited line, and the tool does not report that. A row quoting `CANDIDATE` owes the occurrence count beside it. ⭐⭐ THE SENTENCE THE CRASH COURSE WANTS, AND IT IS A FAMILY RESULT RATHER THAN A ROW ONE: `ph55` and `ph56` are the same defect shape one file apart -- a guard that ALREADY EXISTS elsewhere in the same function, not copied onto one more arm -- and in both, what the unguarded arm breaks is an invariant the executor relies on WITHOUT TESTING. `ph55`'s is *no instruction start is a data word*; `ph56`'s is *an opcode that reads op2 is only ever emitted with op2 present*. Both fixes are three lines, both are a COPY of a sibling's guard, and the harms are completely different: a NULL indirect CALL against a NULL operand READ, the program counter against the operand contract. ⭐⭐⭐ AND THE R5 HALF IS THE SAME SHAPE TWICE: `ph55`'s `ok_from` and `ph56`'s `operand_present` are both properties the EMITTER establishes and the EXECUTOR consumes untested, both are loop invariants of the emitting pass, and both discharge one `unwrap_unchecked` precondition. Deleting `1e708a5aeb30`'s three lines from `verus.rs` makes `operand_present` unprovable and the file fails -- measured, `controls/negatives.py --emit r1`. ⚠ WHERE THE TWO ROWS DIVERGE IS VERUS'S OWN LIMIT AND NOT THE DEFECT: `ph55` dispatches through a function pointer stored in each instruction and Verus answers *The verifier does not yet support the following Rust feature: function pointer types*, a TYPE-LEVEL refusal no external_body wrapper fixes, which forced `Option<u8>` plus a match on all four of that row's Rust rungs. `ph56` dispatches with a switch on the opcode, because every opcode this compiler emits HAS a handler -- the missing thing is the OPERAND, not the handler -- so no substitution was forced and none was made. That is a finding about the two rows' costs, not a claim that either is better. ⚠ THE ROW MODELS COMPILE-AND-RUN IN ONE LOOP AND SAYS SO: `kernel()` compiles the whole record stream and then executes it on EVERY call, where PHP compiles once per script and executes many times. Any `c-gcc-h` minus `c-gcc` this row measures is therefore a LOOSE UPPER BOUND on PHP's own cost of `1e708a5aeb30` and may not be quoted as PHP's cost of it. NOTES.md §8. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "ph56_fold": "ph56_run",
      "MAX_STMT": "64",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 66
    },
    "twin_obligations": {
      "verus.rs": 76
    },
    "obligations_note": "66 verified / 0 errors, and 76 under `--cfg slb_twin` -- ten trusted accessors, therefore ten twins. ⭐⭐ WHAT THE PROOF RESTS ON IS `operand_present`, AND IT IS A STATEMENT ABOUT THE OPERAND RATHER THAN ABOUT THE DISPATCH TABLE: *for every j < nops, an opline whose opcode is ZEND_ISSET_ISEMPTY_DIM_OBJ carries an op2 that is IS_CONST or IS_VAR, and never IS_UNUSED.* It is the loop invariant of the compile pass, it is what discharges `zunwrap`'s `requires t.is_some()`, and it is exactly the invariant `case BP_VAR_IS:` breaks at 5.0.0. ⭐ It is ESTABLISHED BY THE EMITTER and consumed by the EXECUTOR WITHOUT TESTING, which is `ph55`'s `ok_from` one file over and makes the family n = 2 on the proof shape as well as on the fix shape. ⚠ Note what it is NOT: it is not *every opcode has a handler*. Every opcode this compiler emits HAS one -- that is why the four Rust rungs need no `Option<u8>` handler-ID substitution and why this row never meets Verus's function-pointer-type refusal. The other unchecked classes rest on facts that have nothing to do with PHP: the driver's `off + len <= buf@.len()`, `c/main.c`'s `stride_w <= 512` with `MAX_OPS == 2 * MAX_STMT`, and arithmetic -- `% NVAR`, `% MAX_STMT`, `% NSLOT`. NOTES.md §11 keeps them apart, because an editor who deleted the 2004 patch would be removing the precondition of exactly ONE of them, and `controls/negatives.py --emit r1` measures that it is the tenth.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 66 shipped + 10 for slb_twin_bget, _oget, _oset, _sget, _sset, _tget, _tset, _nget, _nset and _zunwrap. ⭐⭐⭐ THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A MEASUREMENT, NOT AN OMISSION. Verus's default is 10. Bisected on this box (controls/rlimit_bisect.sh; NOTES.md §11 has the table): rlimit 1 gives 65 verified / 1 error plain and 75 / 1 twin; rlimit 2 gives 66/0 and 76/0; and every value from 3 to 200 gives 66/0 and 76/0. So a compile pass, an interpreter, a value postcondition over the whole machine state and TEN verified twins need **2**, and the default is 5x that. ⭐ `ph55` bisected to the same **2** on a proof of the same shape. ⚠⚠ AND THE FIRST DRAFT OF THIS FILE *DID* EXCEED THE DEFAULT, with the cause a WRONG LOOP INVARIANT rather than proof size: two clauses that cannot hold at a `break` were declared `invariant` instead of `invariant_except_break`, and Z3 spent the budget failing. An rlimit error is a symptom, not a size -- which is worth saying because the obvious reading of one is *this proof is too big* and the obvious repair is to raise the number.",
    "items": {
      "verus.rs": {
        "s_mode_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_base_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_o2t_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_var_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_tmp_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_parse_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_parse_op": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_isset_rewrite": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "operand_present": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "parsed": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "c_stmt": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "compiled": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "init_cs": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_gzp_some": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_gzp": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fetch": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_is_dim": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_dim_mode": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_isset_pair": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "e_step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "e_run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "init_zv": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "init_slots": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_slots": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_anext": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ph56_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "bget": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_bget": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "oget": {
          "external": "verifier::external_body",
          "requires": [
            "i < MAX_OPS"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_oget": {
          "external": null,
          "requires": [
            "i < MAX_OPS"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "oset": {
          "external": "verifier::external_body",
          "requires": [
            "i < MAX_OPS"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_oset": {
          "external": null,
          "requires": [
            "i < MAX_OPS"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "sget": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_sget": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "sset": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_sset": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "tget": {
          "external": "verifier::external_body",
          "requires": [
            "i < MAX_STMT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_tget": {
          "external": null,
          "requires": [
            "i < MAX_STMT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "tset": {
          "external": "verifier::external_body",
          "requires": [
            "i < MAX_STMT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_tset": {
          "external": null,
          "requires": [
            "i < MAX_STMT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "nget": {
          "external": "verifier::external_body",
          "requires": [
            "i < NVAR"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_nget": {
          "external": null,
          "requires": [
            "i < NVAR"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "nset": {
          "external": "verifier::external_body",
          "requires": [
            "i < NVAR"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_nset": {
          "external": null,
          "requires": [
            "i < NVAR"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "zunwrap": {
          "external": "verifier::external_body",
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "r == t.unwrap()"
          ]
        },
        "slb_twin_zunwrap": {
          "external": null,
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "r == t.unwrap()"
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
        "var_of": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_var_of(o)",
            "r < NSLOT",
            "VAR_BASE <= r < ARR_BASE"
          ]
        },
        "tmp_of": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_tmp_of(o)",
            "r < MAX_STMT"
          ]
        },
        "get_zval_ptr": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.is_some() == s_gzp_some(op_type)",
            "r.is_some() ==> r.unwrap() == s_gzp(ts@, op_type, op)",
            "r.is_some() ==> r.unwrap() < NSLOT"
          ]
        },
        "do_end_variable_parse": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_parse_ok(*old(o), ty)",
            "r ==> *final(o) == s_parse_op(*old(o), ty)",
            "!r ==> *final(o) == *old(o)"
          ]
        },
        "do_isset_or_isempty": {
          "external": null,
          "requires": [],
          "ensures": [
            "*final(o) == s_isset_rewrite(*old(o))"
          ]
        },
        "fetch_dimension_address": {
          "external": null,
          "requires": [],
          "ensures": [
            "final(slots)@ == s_fetch( old(slots)@, old(anext)@, *old(bailout), op1, op2_type, op2, ty, ).slots",
            "final(anext)@ == s_fetch( old(slots)@, old(anext)@, *old(bailout), op1, op2_type, op2, ty, ).anext",
            "*final(bailout) == s_fetch( old(slots)@, old(anext)@, *old(bailout), op1, op2_type, op2, ty, ).bail",
            "r == s_fetch(old(slots)@, old(anext)@, *old(bailout), op1, op2_type, op2, ty).r",
            "r < NSLOT"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == ph56_fold(buf@, off as int, len as int)"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "oset": "`x: Op` is a PURE VALUE and needs no precondition. The unchecked operation is `*a.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `a` being a live `[Op; 128]`, and on NOTHING about the record being written -- every inhabitant of `Op` is a legal store into a slot that is already initialised (`[ZERO_OP; MAX_OPS]` initialises the whole array before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < MAX_OPS`, and the `ensures` names the WHOLE post-state -- `old(a)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition.",
        "sset": "`x: Zv` is a PURE VALUE and needs no precondition, for exactly oset's reason one type down: definedness depends on `i`, which IS constrained by `i < NSLOT`, and the `ensures` names the whole post-state. ⚠ The entry exists separately because the ARRAY is different -- `[Zv; 42]` rather than `[Op; 128]` -- and a reviewer checking that the bound matches the array is checking two different pairs. ⭐ `Zv` is ONE record rather than the parallel arrays `ph55` used, which halves this row's write surface for the store: two wrappers there, one here.",
        "tset": "`x: u16` is a PURE VALUE; same argument as oset on the temp vector, whose index is constrained by `i < MAX_STMT` and whose `ensures` names the whole post-state. ⚠ The bound is MAX_STMT and not NSLOT and not MAX_OPS: `EX(Ts)` has one slot per STATEMENT, and a reviewer checking that the bound matches the array has three different pairs to keep apart in this file.",
        "nset": "`x: u16` is a PURE VALUE; same argument as oset on the next-free-index vector, constrained by `i < NVAR` -- one entry per CV slot, which is the narrowest of the four bounds and the one established by `% NVAR` on a value the input controls.",
        "oget": "`a: &[Op; MAX_OPS]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its length is in its TYPE, so there is nothing about it left for a `requires` to say: `a@.len() == MAX_OPS` holds for every `a` this signature admits. The only quantity that can make `*a.get_unchecked(i)` undefined is `i`, and `i` IS constrained, by `i < MAX_OPS`. ⚠ IT IS NOT THE SAME ARGUMENT AS `bget`'s: `bget` takes a SLICE, whose length is a run-time fact, so its `requires` has to name it (`i < v@.len()`) and the stage is satisfied without a declaration.",
        "sget": "same argument as oget on `&[Zv; 42]`: the length is in the type, the index is constrained by `i < NSLOT`, and there is nothing else a `requires` could honestly say.",
        "tget": "same argument as oget on `&[u16; 64]`: the length is in the type, the index is constrained by `i < MAX_STMT`, and there is nothing else a `requires` could honestly say.",
        "nget": "same argument as oget on `&[u16; 8]`: the length is in the type, the index is constrained by `i < NVAR`, and there is nothing else a `requires` could honestly say.",
        "zunwrap": "⭐⭐ THE ROW'S OWN TRUSTED ITEM, AND ITS PARAMETER IS THE WHOLE STORY. `t: Option<usize>` is a value with exactly two shapes and the `requires` names the one the body assumes: `t.is_some()`. There is no second parameter to leave unconstrained -- the shape this stage exists to catch cannot arise here, because the ONLY thing that can make `t.unwrap_unchecked()` undefined is `t` itself. ⚠ What makes the entry worth reading is WHERE the precondition comes from: not from arithmetic and not from the caller's convenience, but from the COMPILER. `operand_present` is the compile pass's loop invariant, it needs the `BP_VAR_IS` guard to hold, and that guard is `1e708a5aeb30`. `controls/negatives.py --emit r1` deletes the three lines and that mutant must FAIL to verify -- measured, and it fails exactly on the assert that re-establishes `operand_present`."
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
    "canonical": [
      "n_blob = bytes . len ( ) ;",
      "buf = bytes . as_slice ( ) ;",
      "acc = 0 ;",
      "if stride_w >= 16 && stride_w <= 512 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph56's two probe shapes have different work per call (128 and 512 window bytes, i.e. 16 and 64 STATEMENT records) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW IN BYTES and the statement count is `stride / 8`, an exact linear function of it, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ THERE IS ALSO A FIXED PER-CALL TERM AND IT IS LARGE: the op_array (128 records), the 42-slot store and the 64-entry temp vector are built on EVERY call whatever the stride, and the final fold walks all 42 slots plus 8 next-free indices. ⚠⚠⚠ AND THE MARGINAL IS NOT A DISPATCH RATE ON THIS ROW AT ALL: `kernel()` COMPILES AND THEN EXECUTES on every call, so each statement is paid for twice -- once through the mode switch and once through the handler. NOTES.md §8 decomposes it rather than presenting it as one, and says why no R1h cost figure from this row may be quoted as PHP's cost of 1e708a5aeb30."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "norel",
      "why": "⭐⭐⭐ R4 AND R5 ARE THE SAME MACHINE CODE MODULO RELOCATION BYTES AT *BOTH* OPTIMISATION LEVELS, AND `ph55` MEASURED THE OPPOSITE ON THE SAME QUESTION. Measured, O3 isolated: both `kernel` symbols are 632 instructions, `md5_fn` DIFFERS, and `md5_fn_norel` and `md5_norm` are IDENTICAL; at O0 isolated both are 929 instructions with the same three verdicts. `ph55` checked exactly this and recorded *`norel` does not rescue it either (87140a47b1370398 vs 9a0ed674d02a9bf0), so it is not relocation bytes* -- 876 instructions against 872, and 22 544 Ir more on small.bin. ⚠⚠ THE DIFFERENCE BETWEEN THE TWO ROWS IS NOT LUCK AND IT IS NOT THE PROOF: IT IS WHETHER R4 AND R5 ARE ONE EXEC TEXT. `ph55` shipped `(x as usize) % NVAR` in unsafe.rs and `(x % (NVAR as u64)) as usize` in verus.rs, because Verus models `usize` as 32 or 64 bits and will not assume the cast is lossless. This row normalised ALL FOUR Rust rungs onto the second spelling -- nine expressions across three files, itemised in provenance.divergences -- so R4 and R5 are character-identical apart from the `verus!` block, the spec and proof items and the ghost clauses, and the compiler produces the same instruction sequence from them. ⭐ THE CONSEQUENCE IS MEASURED AND NOT INFERRED: A1 at O3/isolated is 3396.263 Ir/call for BOTH rungs on small.bin and 9918.610 for BOTH on large.bin -- EQUAL TO THE DIGIT, where `ph55` paid +0.071 %. ⚠ The pin is `norel` and not `exact` because the raw bytes really do differ: the two cells are built by different drivers (`rustc` for R4, the Verus driver for R5) and land at different addresses. ⚠ `whole` is NOT covered by this pin -- the gate compares the `isolated` cells -- and the two whole cells DO differ structurally (1240 against 1239 instructions at O3), because there the kernel is inlined into `main` and there is no common symbol to compare. ⭐⭐ AND MIRI IS STILL REQUIRED: `norel` counts as the same machine code, so `.memory/02-bench-rules.md`'s non-waivable clause does not fire on this pin -- but the row has TEN trusted items, four of which WRITE and one of which is `Option::unwrap_unchecked`, and that is the clause that does. `miri.required: true` is a declaration about the trusted surface, not about this entry. ⚠ The figures here are from results-php/gate/ph56-fetchmode-arith.json and results-php/ph56-fetchmode-arith.json; PROTOCOL.md rule 6's addendum says to re-read this entry against THOSE records rather than trusting the hash."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph56 has TEN such items and four of them WRITE (`oset`, `sset`, `tset`, `nset`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `a@[i] == x` would let a body that also clobbered `a[i + 1]` through every Verus stage. Each shipped `ensures` is the whole post-state, `old(a)@.update(i, x)`, and Miri is the backstop for the class regardless. ⭐ AND ONE OF THE TEN IS NOT AN INDEX AT ALL: `zunwrap` is `Option::unwrap_unchecked`, whose misuse is not an out-of-bounds access but a read of an uninhabited discriminant, and Miri is the only detector in this tree that sees that class -- which on THIS row is the defect itself rather than a neighbouring hazard.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph56's cost is 4 x (one record stream decoded, compiled through the mode switch and executed), i.e. 4 x at most 64 statements and 128 dispatches -- four orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_compile.c",
    "c_lines": [
      736,
      780
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '736,780p'",
    "extract_sha256": "53df75a81666621930f00eefb944dd8a5be7def46ede67c728c7eef0e7efe657",
    "extra_spans": [
      {
        "c_file": "Zend/zend_compile.c",
        "c_lines": [
          3215,
          3240
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '3215,3240p'",
        "extract_sha256": "977998d164ec4cdb82b898b5ce3216963a01170c5cc7024ecbf657abb4c58bf7",
        "why": "⭐⭐ THE SECOND REWRITE, AND WITHOUT IT THIS ROW NAMES THE WRONG HARM. `zend_do_isset_or_isempty` calls `zend_do_end_variable_parse(BP_VAR_IS, 0)` at `:3219` and then, four lines later, rewrites the LAST opline AGAIN: `case ZEND_FETCH_DIM_IS: last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;` at `:3229`. So `ZEND_FETCH_DIM_IS` exists for four lines and is overwritten, `zend_fetch_dim_is_handler` never runs on `isset($a[])`, and the word LAST is what leaves a chain's leading append opline alive as the row's second harm."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          88,
          125
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '88,125p'",
        "extract_sha256": "3a895390317938015c9475c4f2b7de21541a3149cb59532464e3541923eca6a3",
        "why": "⛔ `_get_zval_ptr`, AND ITS `case IS_UNUSED:` IS AN EXPLICIT `*should_free = 0; return NULL;` AT `:118-121` -- a decision, not a fall-through. It is CORRECT on its own terms: an operand that is not there has no zval. The whole row is one caller that was handed one anyway."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          3958,
          4000
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '3958,4000p'",
        "extract_sha256": "33d08e0f038f4185372ec3ae50916cce1fe26c62e8e1e234f22bb13818501d0c",
        "why": "⛔⛔ THE FAULTING FRAME. `zend_isset_isempty_dim_prop_obj_handler` reads op2 through `get_zval_ptr` at `:3961` and dereferences the result at `switch (offset->type)` at `:3973` with NOTHING in between: no NULL test, no operand-kind check, no assertion. A pristine 5.0.0 CLI faults here at `0x14` = `offsetof(zval, type)`, and `c/kernel.c` faults at the same offset in the same frame."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          896,
          975
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '896,975p'",
        "extract_sha256": "4ac45e000a6f994bb0a5d4db99baaa0df1d8aef90469a3960366a0a64491d26c",
        "why": "⭐ THE APPEND ARM, AND IT IS NOT THE DEFECT. `:935-943` is what `$a[] = 1` and `$a[] += 1` reach on every legal append; `new_zval->refcount++` at `:938` is the implementation of `[]` and the FAILURE arm decrements it again at `:942`. ⭐ The span also carries the container type that IS guarded -- `:963-964` refuses `[]` on a string with `E_ERROR` -- so the contrast between a guarded container and an unguarded fetch mode is inside the MEASURED program and not only in a comment. And it is where the row's SECOND harm lands, through `inputs/adversarial-chain.bin`."
      },
      {
        "c_file": "Zend/zend_compile.h",
        "c_lines": [
          636,
          656
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.h | sed -n '636,656p'",
        "extract_sha256": "1ac60fb0c2f7946870e667ceff849fe6b03b3408d7ad480bf99644e7deddf906",
        "why": "⭐ THE LAYOUT THE ARITHMETIC WALKS, IN UPSTREAM'S OWN WORDS AND WITH UPSTREAM'S OWN EXCLAMATION MARK: *the following 18 opcodes are 6 groups of 3 opcodes each, and must remain in that order!*. The span is pinned because every delta in `zend_do_end_variable_parse` is a multiple of three over exactly this layout, so the kernel keeps the LITERAL opcode numbers. A row that renumbered them would be measuring its own arithmetic."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          1383,
          1396
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '1383,1396p'",
        "extract_sha256": "a18c98a900b0f3ca097b5a0b9a7dec02445d40b597a59265653abcda701bb351",
        "why": "`execute()`'s dispatch loop. It is pinned because this row's executor IS this loop, and because of what it does NOT contain: the loop calls through `opline->handler` with no test, and on `ph56` that is HARMLESS -- every opcode this compiler emits has a handler. The same fourteen lines are `ph55`'s mechanism and this row's scenery, which is the sharpest statement of how the two differ."
      }
    ],
    "extra_spans_note": "THE ROW LIFTS SEVEN SPANS AND ALL SEVEN ARE PINNED. `provenance.c_lines` names the defect site (zend_compile.c:736-780, `zend_do_end_variable_parse`); the six extras are the second rewrite (zend_compile.c:3215-3240), the operand fetch whose IS_UNUSED arm returns NULL (zend_execute.c:88-125), the faulting handler (zend_execute.c:3958-4000), the append arm and the STRING container's guard (zend_execute.c:896-975), the six-groups-of-three opcode layout the arithmetic walks (zend_compile.h:636-656) and `execute()`'s dispatch loop (zend_execute.c:1383-1396). ⚠ FOUR OF THE SEVEN ARE THE *HARM*, NOT CONTEXT: a row that pinned only the defect site would certify a span containing a missing test and nothing that makes a missing test fatal -- and would in particular not carry :3229, without which a reader concludes the harm is in `zend_fetch_dim_is_handler`, which is what the task file that commissioned this row concluded and what measurement refuted. ⚠ What is NOT pinned as a span is `zend_compile.c:1411-1427`, `zend_do_pass_param`, which the sibling census (NOTES.md §2) measures and cites but whose CODE this kernel does not lift: the argument-passing path is outside the row.",
    "tier": "modelled",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "zend_compile.c:736, :3215; zend_execute.c:88, :896, :3958",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "zvals become a flat store of fixed records and `zval **` becomes an INDEX into it",
        "kind": "substitution",
        "where": "zend_execute.c:88-125, :896-975, :3958-4000",
        "why": "`EG(uninitialized_zval)` and `EG(error_zval)` are two RESERVED INDICES, so the handler's tests are index comparisons and the branch structure is one for one. ⭐ THE RECORD'S FIELD ORDER IS UPSTREAM'S AND THAT IS LOAD-BEARING: `lval`/`value_hi` (16 bytes) then `refcount` (4) then `type`, so `offsetof(ph56_zval, type)` is 20 and the C rung faults at the same `0x14` a pristine 5.0.0 CLI faults at -- measured, both. `PH56_LAYOUT_ASSERT` is a C99 negative-array-bound assertion that fails the build if it moves. Demonstrated behaviour-preserving on the extracted domain by model.py's three independent implementations agreeing on 156 synthetic windows and by the C-to-model differential, 156 windows x 2 configurations, 0 mismatches. No semantics."
      },
      {
        "what": "the hash table becomes an array of PH56_DIM slots per variable, with a next-free index",
        "kind": "substitution",
        "where": "zend_execute.c:930-944",
        "why": "the ONE property this row needs is kept: the append arm at :935-943 takes a reference to the process-global, inserts, and DECREMENTS again when the insert reports FAILURE -- so the `n >= PH56_DIM` arm is upstream's `zend_hash_next_index_insert(...) == FAILURE` arm and both are reached by the corpus, asserted by inputs/gen.py. The lookup a real hash table performs on a present dimension is the CONTAINER and not the defect (.memory-php/01-extraction.md prices extraction at the DEFECT site). No semantics on the extracted domain."
      },
      {
        "what": "the fetch list becomes a one-or-two element window and `zend_llist` is gone",
        "kind": "substitution",
        "where": "zend_compile.c:748-779, :3223",
        "why": "the `while (le)` walk runs the mode switch over EVERY element and `zend_do_isset_or_isempty` rewrites the LAST one only, and that distinction is the row's second harm, so both are kept exactly. A statement record's chain bit selects one element or two, which spans the reachable shapes of `$a[d]` and `$a[][d]`; longer chains add elements the switch treats identically. inputs/gen.py asserts both shapes are reached. No semantics on the extracted domain."
      },
      {
        "what": "`zend_bailout()` becomes a flag tested at the top of the executor",
        "kind": "substitution",
        "where": "zend_compile.c:754, :772; zend_execute.c:963-964",
        "why": "`zend_error(E_COMPILE_ERROR, ...)` is a `longjmp` out of the whole compile, so nothing runs at all; the kernel sets a flag, stops the compile pass and skips the executor, which is the same observable. The flag is FOLDED INTO THE ANSWER, so a rung that bailed at the wrong point returns a different u64 rather than merely looking different. No semantics."
      },
      {
        "what": "`zend_opcode_handlers[]` becomes a `switch` on the opcode",
        "kind": "substitution",
        "where": "zend_execute.c:1383-1396, Zend/zend_opcode.c:363",
        "why": "⭐ ADMISSIBLE HERE AND NOT ON `ph55`, AND THE REASON IS THE ROW: every opcode this compiler can emit HAS a handler, so no dispatch target is NULL and no behaviour depends on the table's representation. `ph55`'s table has one deliberate NULL entry and IS the mechanism, which is why that row pays a representation substitution and this one does not. ⚠ It is also why `ph56` never meets Verus's function-pointer-type refusal. Demonstrated behaviour-preserving by the gate's own stage-3 cross-rung checksum comparison on every input: six rungs, one switch each, one answer. No semantics."
      },
      {
        "what": "the op_array is a `[PH56_MAX_OPS]` frame array and the driver refuses a larger window",
        "kind": "substitution",
        "where": "Zend/zend_opcode.c:349 (`get_next_op`), c/main.c",
        "why": "PHP's op_array is heap-grown at COMPILE time and has no capacity bound; the kernel uses a frame array of 128 records, so the bound lives in the DRIVER as `stride_w <= 512`, outside every measured loop and outside both the compiler and the executor. ⚠ IT IS NOT A CHECK IN EITHER PASS and must not become one: the compile pass still applies its delta without testing, which is the row. No semantics."
      },
      {
        "what": "the opcode set is thirteen constants rather than the full 150",
        "kind": "deletion",
        "where": "zend_compile.h:636-713",
        "why": "the six-groups-of-three layout is what the arithmetic walks, so all eighteen of the FETCH group's relevant members and the three ISSET_ISEMPTY members keep their LITERAL upstream values -- 81, 83, 84, 85, 87, 89, 90, 91, 93, 96, 114, 115, 148 -- and the deltas are upstream's. Opcodes the row's statement records cannot produce carry no part of the mechanism. No semantics on the extracted domain."
      },
      {
        "what": "`array_init` on a NULL container keeps only the type transition",
        "kind": "substitution",
        "where": "zend_execute.c:914-927",
        "why": "upstream allocates a HashTable and installs it; the kernel sets the record's type to array and zeroes the next-free index, which is the same observable in a store with no allocator. The arm is kept at all because it is what makes `$a[] = 1` on an unset variable reach the append, and the corpus reaches it -- asserted by inputs/gen.py. No semantics on the extracted domain."
      },
      {
        "what": "the per-dispatch opcode fold",
        "kind": "projection",
        "where": "zend_execute.c:1390 (`zend_clean_garbage`)",
        "why": "upstream sweeps refcounts once per dispatch and returns void; this kernel folds the dispatched opcode into the checksum there instead, so the EXECUTED TRACE lands in the answer rather than only in a sanitizer. That is what makes `inputs/adversarial-chain.bin`'s silent mis-compile a DIFFERENT NUMBER rather than an invisible one. Nothing observable in the returned u64 depends on the sweep itself."
      },
      {
        "what": "`BP_VAR_FUNC_ARG` hands the executor `BP_VAR_R` rather than a mode of its own",
        "kind": "projection",
        "where": "zend_execute.c:2084 (`ARG_SHOULD_BE_SENT_BY_REF`)",
        "why": "upstream chooses W or R at run time from the callee's signature, which is a whole function-table machinery for one bit; by-value is the common case and is what `f($a[])` takes. ⭐ The arm is kept rather than deleted because it is the row's UNCAUGHT SIBLING: `inputs/adversarial-funcarg.bin` produces the same u64 at R1 and at R1h, to the digit, because 1e708a5aeb30 does not touch that arm -- the census, inside the ladder. No semantics on the extracted domain."
      },
      {
        "what": "the modulo spelling `(x % (NVAR as u64)) as usize` in all four Rust rungs",
        "kind": "substitution",
        "where": "zend_execute.c:930, :3967, :3977",
        "why": "Verus models `usize` as 32 or 64 bits and will not assume a `u64` cast to `usize` is lossless, so R5 must take the modulus BEFORE the cast. ⚠⚠ ALL FOUR RUST RUNGS WRITE IT THAT WAY, not just R5, so the R2->R3 and R3->R4 gradients are not polluted by a representation change -- which is the mistake `ph55` made here, shipping one spelling in unsafe.rs and another in verus.rs. The two expressions denote the same value on any 64-bit target and compile to the same mask. C writes the cast-first form because C has nothing to prove. Demonstrated behaviour-preserving by the gate's stage-3 cross-rung checksum on every input. No semantics."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠ EIGHT of these twelve entries are SUBSTITUTIONS and TWO are PROJECTIONS, which is a lot, and the reason is structural rather than sloppy: this defect spans the COMPILER and the EXECUTOR, and everything between a `znode` and a `zval **` is machinery in another file. PROTOCOL_PHP.md A1 requires a substitution in a non-`modelled` tier to be (a) itemised with a line citation, (b) given a `why` ending in 'no semantics' and (c) DEMONSTRATED behaviour-preserving rather than asserted -- and this row declares `modelled`, so (c) is owed by nothing but honesty. It is discharged anyway: by model.py's three independent implementations agreeing on 156 synthetic windows spanning the whole (mode x base x op2-type x chain) cross product, by the C-to-model differential at 156 windows x 2 configurations with 0 mismatches, by inputs/gen.py's per-arm reachability assertions, and by the gate's own stage-3 cross-rung checksum comparison on every input. ⭐ The ONE divergence whose (c) is a MEASUREMENT of what it costs rather than of whether it changes an answer is the dispatch `switch`, and the measurement is `ph55`: that row pays `controls/fnptr_cost.py` for the same substitution because its table's one NULL entry IS the mechanism, and this row pays nothing because every opcode it emits has a handler.",
    "root_cause_ids": [
      "fetch-mode-arith-bp-var-is-arm-unguarded"
    ],
    "cwe": "CWE-476",
    "cwe_note": "index.csv records CWE-476 (NULL pointer dereference) and this row reproduces exactly that, MEASURED ON BOTH SIDES: a pristine-sourced PHP 5.0.0 CLI running `isset($a[])` under ASan reports *SEGV on unknown address 0x000000000014* in `zend_isset_isempty_dim_prop_obj_handler`, and `c/kernel.c` under ASan reports the same address in `ph56_isset_isempty_dim_obj_handler`. `0x14` is 20, which is `offsetof(zval, type)` on this ABI -- the fault is `offset->type` through a NULL `zval *`, and the kernel carries a compile-time assertion that fails the build if the offset moves. ⚠⚠ AND THE ROW SAYS, IN ITS OWN INPUTS, THAT CWE-476 IS THE MANIFESTATION AND NOT THE DEFECT. The defect is a MIS-COMPILE -- an opline emitted with an operand its handler's contract requires and its compiler did not check -- and `inputs/adversarial-chain.bin` mis-compiles by exactly as much, differs from `inputs/adversarial-nullderef.bin` in ONE STATEMENT RECORD, silently GROWS THE ARRAY, returns a plausible answer with exit 0, and is declared `sanitizer_expect: clean` because there is nothing for a sanitizer to say. ⭐ That is why `model.py::sanitizer_expect` derives from the NULL DEREFERENCE and not from the mis-compile, and says so in its own docstring. NOTES.md §6 prices the pair.",
    "fix_commit": "1e708a5aeb30711f8b7b2a811377a13f2b23a8c9",
    "fix_commit_note": "⚠ THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE AND THE ROW USES ITS SHORT FORM EVERYWHERE. `1e708a5aeb30` -- Marcus Boerger, 2004-08-29, 'Bugfix #29882 isset crashes on arrays' -- is ONE FILE, THREE INSERTIONS, ZERO DELETIONS; the patch bytes are at controls/1e708a5aeb30.patch, sha256 `9e86b04f294c4516...`. ⭐⭐ IT IS THE CLEANEST R1h IN EITHER PROGRAMME AND IT IS CLEANER THAN `ph55`'s: the three lines are the `BP_VAR_R` arm's own guard, copied onto the `BP_VAR_IS` arm, and `git apply` PLACES IT on 5.0.0 -- *Hunk #1 succeeded at 761 (offset -2 lines)* -- where `ph55` needed a hand backport. ⚠⚠ THE REASON THAT WAS PREDICTED FOR IT IS REFUTED: the prediction was that it applies because the hunk header says `@@ -763,6 +763,9 @@` and 5.0.0's arm is also at :763. Those are TWO DIFFERENT LINES THAT HAPPEN TO SHARE A NUMBER -- the hunk's first context line is `opline->opcode += 3;`, which 2004-08-30 HEAD puts at 763 and 5.0.0 puts at 761 -- so it applies DESPITE a two-line offset, not because of an exact match. controls/r1h_backport.py measures both numbers and FAILS if they ever converge. ⚠⚠ AND `git apply --check` LIED, LIVE, ON THE FIRST ATTEMPT: `--check` returned 0 and the real apply returned 0 with *Skipped patch 'Zend/zend_compile.c'.* and moved no bytes, because the scratch path was gitignored in the enclosing repository. `gitignore_trap()` reproduces the trap on every invocation and records `{path_is_gitignored, check_rc, bytes_moved}`, so a future git that fixes the behaviour surfaces as a CHANGED NUMBER rather than as a stale paragraph. --check is not the test; the bytes are. ⭐ A DETAIL WORTH KEEPING: the control's first spelling computed the applied hunk's added lines as a SET difference and got the empty list, because all three inserted lines ALREADY OCCUR in the file, in the `BP_VAR_R` arm. That is the fix in one sentence -- it adds nothing new, it adds one more COPY -- and the control now uses a multiset difference and says why in situ. ⚠ WHICH ARM the three lines belong to is settled by `preimage_screen.py --id CRASH-041` ON THIS ROW, because the cited line is unique: `case BP_VAR_IS:` occurs EXACTLY ONCE in Zend/zend_compile.c. ⚠ UNVERIFIED IN THIS ROW: whether `1e708a5aeb30` is the FIRST commit to close this site, and whether any 5.0.x branch backport preceded it. PROTOCOL_PHP.md F5(iii) asks for confirmation against the tags and this row confirms the SITE and the DIRECTION -- over 18 release tags, first and last of every 5.x minor line -- rather than the exact commit. The tag matrix is a SAMPLE and not a bisect: a guard added and removed entirely inside one minor line would be invisible to it.",
    "invariant": "I18",
    "obligation": "O2",
    "invariant_note": "⚠ THE CATALOGUE ROW SAYS `I18 + I12` AND BOTH ARE RIGHT, AT TWO DIFFERENT POINTS OF ONE CHAIN, and this block can name only one so it names the first. **I18** is *opcode and IR well-formedness* -- 'every instruction handed to the interpreter must actually carry the operands its handler is going to read' -- and its **O2** is 'an opcode or fetch-mode rewrite ... must preserve operand presence and handler expectations rather than silently reinterpret them'. That is the MIS-COMPILE, and it is this row's defect exactly: the fetch-mode rewrite at :764 does not preserve operand presence. **I12/O1** is 'a NULL return, sentinel, status code, or NULL-able out-parameter must be tested before the result is read through', and that is the DEREFERENCE: `get_zval_ptr` is a NULL-able return read through without a test at :3973. ⭐ The two halves are exactly the two adversarial inputs. `adversarial-chain.bin` breaks I18/O2 and NOT I12/O1 -- the handler it reaches has its operand -- and it is the input no detector sees. ⭐⭐ AND IT IS THE SAME PAIR `ph55` CARRIES, WITH THE HALVES SWAPPED BETWEEN THE LAYERS: there I18 is broken by the EXECUTOR and I12 manifests in the dispatch; here I18 is broken by the COMPILER and I12 manifests in the operand. Blind-labelled by the corpus (`paper/invariants-list.md`) and carried across unmodified.",
    "echoes": [
      "p19"
    ],
    "echoes_note": "p19 is the closest PAT analogue by the catalogue's own `echoes` column, and it is the same column `ph55` carries. ⚠ PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and NEVER a filter, and patterns-php/ is fresh: 'that's p19's mechanism' may not refuse a candidate. ⚠⚠ AND THE NEARER NEIGHBOUR IS `ph55`, NOT p19 -- same family T5, same corpus `echoes`, same three-line fix shape, same proof shape, one file apart -- which is a reason to read the two rows together and NOT a reason to have built only one: the harms are a NULL indirect CALL and a NULL operand READ, and the C mechanisms are a mis-stride and a mis-emit. PLAN_PHP.md §3 makes C-side duplication the only kill and these are not duplicates.",
    "uses_allocator": false,
    "uses_allocator_why": "the kernel allocates nothing. PHP's op_array is heap-grown by `get_next_op` at COMPILE time and `EX(Ts)` is a `safe_emalloc` in `execute()` whose size is `op_array->T`, a COMPILE-TIME constant of the op_array; this kernel keeps both as frame arrays instead, so both are O(1) per call in the input. No emalloc, no efree, no php_shim_reset, no php_shim_tally. ⭐ That is why PROTOCOL_PHP.md B1a's caveat does NOT apply to this row's cross-language column: unlike ph64 there is no allocator term in it at all. ⚠ DECLARED, NEVER DETECTED (TASK_PHP_008 §0.4) -- nothing reads this field and no verdict depends on it. The row still carries c/emalloc_shim.h as a symlink, because that rule is UNCONDITIONAL."
  }
}
```
