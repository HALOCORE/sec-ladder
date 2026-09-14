# ph55 — an early exit strides 1 over a two-word instruction

**PHP 5.0.0, `Zend/zend_execute.c:1724-1796`, corpus row CRASH-023, tier
`narrowed`.** `zend_binary_assign_op_helper` computes its own instruction's
WIDTH at run time — `increment_opline = 1` on the `ZEND_ASSIGN_DIM` arm
(`:1749`) and nowhere else — and then leaves by one of two exits. The normal
exit consults the flag (`:1792-1795`). The error exit, 23 lines earlier, does
not (`:1765-1770`).

⭐ **The word the PC then lands on is the trailing `ZEND_OP_DATA`, and
`zend_opcode_handlers[ZEND_OP_DATA] = NULL;` (`:4427`) is an explicit
assignment — the ONLY `= NULL` among the **130** `zend_opcode_handlers[...]`
assignments in `zend_init_opcodes_handlers()` (`:4276-4443`, 168 lines),
counted on the pristine tarball.**** `pass_two`
copies the table into every instruction (`zend_opcode.c:363`) and the executor
calls through that field with no test (`:1391`). The whole mechanism is nine
facts and the fix is three lines.

⚠⚠ **The defect is a CONTROL-FLOW error and the NULL call is only how it
manifests.** `inputs/adversarial-nullcall.bin` and
`inputs/adversarial-opdatalive.bin` differ in **one byte** — the opcode field of
the trailing data word — mis-stride by exactly as much, and the first SEGVs
while the second returns a **wrong answer with exit 0** and no diagnostic from
any detector. `NOTES.md` §6 prices the pair.

⚠⚠⚠ **Verus does not support function pointer types**, which is the row's own
dispatch mechanism, so all four Rust rungs carry an `Option<u8>` handler ID and
a `match` instead. Measured, not assumed: `controls/fnptr.rs` is the probe and
`controls/fnptr_cost.py` prices the substitution. `NOTES.md` §7.

**R1h is `4f68f3774c34`** (Stanislav Malyshev, 2004-08-30, *"fix crash
#29893"*) — three lines, **hand backported**, because the commit is against
2004-08-30 HEAD and `git apply` cannot place it. `NOTES.md` §5 has the failure
and the three legs that identify which exit.

The machine-readable contract follows. `harness-php/gate.py ph55-opdata-stride`
enforces it; `README.md` is the reader's entry point and `NOTES.md` carries the
measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "16 <= len",
    "len <= 8 * 64"
  ],
  "ensures": [
    "result == ph55_run(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (ph55_run). `ph55_run` is model.py's SECOND, independent implementation -- a PURE TRANSITION over an immutable machine tuple, driven to a fixpoint, mirroring verus.rs's `step` and `run` one unfolding at a time -- and not the imperative `_Machine` simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic windows model.py builds itself, spanning every opcode in a body slot, every `extended_value` byte in 0..255, both sides of the error test on BOTH instruction forms, operand encodings past every modulus, and five degenerate op_arrays. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. ⭐ IT HAS ALREADY EARNED ITS KEEP ON THIS ROW: the sweep caught an evaluation-order disagreement in `ADD` -- C and the imperative model wrote `kind[d]` before reading `op1`, which is a different function whenever `result` names the same slot as `op1` -- on a window no input file contains. A THIRD spelling, `_dumb`, materialises the list of PCs the program visits FIRST and then replays it, which is the spelling that catches a stride error, and every shipped window goes through it.",
  "idiom": {
    "required": [
      {
        "c": "`var_ptr == PH55_ERR` -- the error test at zend_execute.c:1765, *var_ptr == EG(error_zval_ptr), as an index comparison against the reserved slot. The zval layer is narrowed away (provenance.divergences) but the BRANCH is one for one, and this is the branch whose true arm forgets the width.",
        "rust": "`var_ptr == ERR` -- the error test at zend_execute.c:1765, *var_ptr == EG(error_zval_ptr), as an index comparison against the reserved slot. The zval layer is narrowed away (provenance.divergences) but the BRANCH is one for one, and this is the branch whose true arm forgets the width."
      },
      {
        "c": "`[PH55_OP_DATA] = NULL` -- zend_execute.c:4427, and it is an EXPLICIT assignment in the middle of `zend_init_opcodes_handlers()` (`:4276-4443`, 168 lines), and the ONLY `= NULL` among that function's 130 `zend_opcode_handlers[...]` assignments -- COUNTED on the pristine tarball, not estimated -- so it is a decision and not an omission. A table whose data-word entry has a handler would delete the harm and leave the row measuring a stride error with no consequence.",
        "rust": "`OP_DATA { None }` -- pass_two's own arm (zend_opcode.c:363 over zend_execute.c:4427). The data word is the ONE opcode with no handler, and in Rust that is an an Option whose None case a caller cannot skip. A table of total functions would delete the harm and leave the row measuring a stride error with no consequence."
      },
      {
        "c": "`ex->opline->handler(ex, ex->opline)` -- zend_execute.c:1391, the INDIRECT CALL, with nothing between the field and the call: no PC bound, no NULL test, no assertion. Dispatching on the opcode with a switch would delete facts 6-9 of the mechanism and the row with them.",
        "rust": "the dispatch, and it is PER RUNG because the lever between R3 and R4 IS this line: safe_naive.rs and safe_tuned.rs write `.handler.unwrap()` and unsafe.rs and verus.rs write `hunwrap(o.handler)`. Both are the same operation on the same Option; one of them tests and one of them does not, and verus.rs's ok_from is what licenses the one that does not. Each spelling is SCOPED-ABSENT from the other pair by design and the gate reports it as such."
      },
      {
        "c": "`ex->opline++` -- NEXT_OPCODE() and INC_OPCODE() keep upstream's bodies (zend_execute.c:1317-1330), INCLUDING NEXT_OPCODE()'s trailing return-0 and INC_OPCODE()'s lack of one. The fact that one of the two macros returns and the other does not is why the error exit reads like a complete exit and is not one; a rung that open-coded them as a bare increment would lose exactly that.",
        "rust": "`pc = pc + 1` and `pc = pc + 2` -- NEXT_OPCODE() and INC_OPCODE(), open-coded, because Rust has no analogue of a macro whose body ends in a return and forcing one would be modelling the C's syntax rather than its behaviour. The row states this rather than hiding it: provenance.divergences itemises the macro expansion, and the two-word arms are the ones that write `pc = pc + 2`."
      },
      {
        "c": "`ph55_emit_fixup` -- THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S. zend_compile emits ZEND_OP_DATA only as the trailing word of a two-word instruction, so no instruction START is a data word, and that is the invariant the dispatch loop relies on when it dispatches without testing. The compiler is outside this row (the blob IS the op_array, PLAN_PHP.md 3), so this walk stands in for it -- it visits exactly the words a CORRECT executor visits and refuses a data word at any of them, and TOUCHES NOTHING ELSE. The last clause is load bearing: a pass that normalised every data word would make inputs/adversarial-opdatalive.bin unrepresentable and delete half the row's result. Every rung has it.",
        "rust": "`emit_from` -- THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S, and in Rust it is TAIL RECURSION rather than a loop. That is a Verus decision showing through into every Rust rung: the property it establishes (ok_from in verus.rs) is defined by recursion on the instruction chain, so written this way the postcondition is the definition's own unfolding and needs no lemma, while a loop needs an invariant quantified over instruction starts plus a glue lemma. c/kernel.c writes the loop, because C has nothing to prove. provenance.divergences itemises it."
      },
      {
        "c": "R1h IS 4f68f3774c34 (Stanislav Malyshev, 2004-08-30, 'fix crash #29893') AND IT IS THREE LINES -- the normal exit's own `if (increment_opline) { INC_OPCODE(); }` copied onto the error exit -- and R2-R5 implement the same function, because the fix is COMPLETE for this defect: it removes every mis-stride and changes no benign answer (controls/fix_scope.py). ⚠ IT IS A HAND BACKPORT AND git apply FAILS; controls/r1h_backport.py runs it and records the failure rather than asserting it. WHICH EXIT the hunk belongs to is settled by THREE INDEPENDENT LEGS and NOT by preimage_screen.py, whose verdict is CANDIDATE on the strength of one NEXT_OPCODE(); line that occurs 117 times in that file: (1) the hunk's own function-context line names zend_binary_assign_op_helper; (2) increment_opline occurs exactly three times in zend_execute.c and all three are inside that function; (3) the other exit ALREADY has the identical guard at 5.0.0, so a patch adding it there would be adding a duplicate. NO BACKTICKED SPELLING BEYOND THE SHA AND THE MACRO NAMES, deliberately: this entry is a statement about WHICH ALGORITHM each rung implements and no single token decides it.",
        "rust": "R1h IS 4f68f3774c34 (Stanislav Malyshev, 2004-08-30, 'fix crash #29893') AND IT IS THREE LINES -- the normal exit's own increment-opline guard copied onto the error exit -- and R2-R5 implement the same function, because the fix is COMPLETE for this defect: it removes every mis-stride and changes no benign answer (controls/fix_scope.py). ⚠ IT IS A HAND BACKPORT AND git apply FAILS; controls/r1h_backport.py runs it and records the failure rather than asserting it. WHICH EXIT the hunk belongs to is settled by THREE INDEPENDENT LEGS and NOT by preimage_screen.py, whose verdict is CANDIDATE on the strength of one NEXT_OPCODE(); line that occurs 117 times in that file: (1) the hunk's own function-context line names zend_binary_assign_op_helper; (2) increment_opline occurs exactly three times in zend_execute.c and all three are inside that function; (3) the other exit ALREADY has the identical guard at 5.0.0, so a patch adding it there would be adding a duplicate. ⚠ NO BACKTICKED SPELLING ON THIS SIDE AT ALL, deliberately: the fix is three lines of C macro calls and the Rust rungs open-code both macros, which required[3] declares, so a pin here would name a spelling no Rust rung can carry."
      }
    ],
    "forbidden": [
      "`if (ex->opline->handler)` and `handler.is_none()` -- TESTING THE DISPATCH TARGET. That is the check zend_execute.c:1391 does not have and adding it deletes the row: the C would stop crashing on the adversarial input and the Rust rungs would stop panicking, and both would be measuring a different program. ⚠⚠ NOTE THE ABSENCE OF BACKTICKS IN THE REST OF THIS ENTRY, AND IT IS NOT STYLE: in a forbidden entry EVERY backticked span becomes a banned token, so an entry that quotes what it is PROTECTING bans that too. The first draft of this block quoted unwrap, unwrap_unchecked and Option in its own explanatory prose, and all three are present in all four Rust rungs -- three hard gate failures, in the class check.py calls an entry that backticks its replacement (PROTOCOL_PHP.md H1, item 100, three instances in three consecutive tasks). It was caught by running the audit on the draft BEFORE it landed. What the sentence says, in plain text: the Rust rungs do open the Option, which is not the same thing as testing it -- unwrap and unwrap_unchecked both ASSUME the handler is there, exactly as C does, and neither takes a different path when it is not.",
      "`% PH55_MAX_OPS` and `% MAX_OPS` -- CLAMPING the PC into range instead of establishing that it is in range. It keeps every index in bounds and puts the PC on THE WRONG WORD anyway, so it is a repair that silences every detector this row has while changing the answer, and it is the first thing a reader reaches for. Upstream did not do it: 4f68f3774c34 corrects the STRIDE.",
      "`[PH55_OP_DATA] = ph55_` -- giving the data word a handler. It makes the executor total and leaves the mis-stride executing an operand record as an instruction, silently, which is precisely the case inputs/adversarial-opdatalive.bin exists to measure AS A SEPARATE INPUT rather than as the shipped behaviour. zend_execute.c:4427 writes NULL and the row measures what that buys."
    ],
    "why": "ph55 is PHP 5.0.0's executor out of `Zend/zend_execute.c:1724-1796`, corpus row CRASH-023, tier `modelled`. ⚠⚠ THE CATALOGUE FILES THIS ROW AS `narrowed` AND THE BUILD REFUTES IT, MEASURED: harness-php/provenance.py reports the kernel overlap at **14% (13/93)** over the union of six cited spans and **16% (7/45)** over the defect site alone, where `narrowed` leads a reader to expect 25%. The CONTROL FLOW is lifted one for one -- the flag, the arm that sets it, the `op_data = opline+1` read, both exits in upstream's order, both stride macros with upstream's bodies, pass_two's handler copy and a dispatch loop with nothing between the field and the call -- but the SCENERY is RE-EXPRESSED: zvals become (kind, val) pairs in a flat store, `zval **` becomes an index, the hash container is gone and the opcode set is ten opcodes standing for the 130 `zend_opcode_handlers[...]` entries `zend_init_opcodes_handlers()` fills -- counted, :4276-4443. ⚠ A tier is a COST and never a filter (PROTOCOL_PHP.md A1), and a tier read as STRONGER than it is, is the dangerous direction, so the row declares the weaker one and publishes the number. NOTES.md §2. THE IDIOM IS A PROGRAM COUNTER ADVANCED BY A WIDTH THE HANDLER COMPUTES AT RUN TIME, WITH ONE EXIT THAT FORGETS TO ASK. `zend_binary_assign_op_helper` declares `zend_bool increment_opline = 0;` at `:1728` and sets it to 1 at `:1749` on exactly one arm of its `switch (opline->extended_value)` -- the `ZEND_ASSIGN_DIM` arm, whose instruction is TWO WORDS (`zend_op *op_data = opline+1;`, `:1742`). The NORMAL exit consults the flag: `if (increment_opline) { INC_OPCODE(); } NEXT_OPCODE();` at `:1792-1795`. The ERROR exit, 23 lines earlier, does not: `if (*var_ptr == EG(error_zval_ptr)) { ...; NEXT_OPCODE(); }` at `:1765-1770`, and `NEXT_OPCODE()` is `EX(opline)++; return 0;` (`:1317-1320`) -- stride 1, unconditionally. So on the two-word form the error exit leaves the PC on the trailing data word. ⭐⭐ AND THAT WORD HAS NO HANDLER, DELIBERATELY: `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` (`:4427`) is an explicit assignment in the middle of `zend_init_opcodes_handlers()` (`:4276-4443`, 168 lines) and the ONLY `= NULL` among its 130 `zend_opcode_handlers[...]` assignments -- counted, not estimated; `pass_two` copies the table into EVERY instruction (`opline->handler = zend_opcode_handlers[opline->opcode];`, `Zend/zend_opcode.c:363`); and the executor calls through that field with no test at all (`if (EX(opline)->handler(...)) { return; }`, `:1391`). The result is an indirect call through NULL, which is what CRASH-023 records and what CWE-476 names. ⚠⚠ THE DEFECT IS A CONTROL-FLOW ERROR AND THE NULL CALL IS ONLY HOW IT MANIFESTS, and this row is built to price that distinction rather than assert it: `inputs/adversarial-nullcall.bin` and `inputs/adversarial-opdatalive.bin` differ in ONE BYTE -- the opcode field of the trailing data word -- mis-stride by exactly as much, and the first SEGVs while the second returns a wrong answer with exit 0 and no diagnostic from any detector. `model.py::sanitizer_expect` derives `fires` from the NULL DISPATCH and not from the mis-stride, and says so. ⭐⭐⭐ THE SENTENCE THE CRASH COURSE WANTS: `INC_OPCODE()` has FOUR call sites in 5.0.0 -- `:1719`, `:1793`, `:2193`, `:2224` -- and THREE of them are unconditional, because those handlers are STATICALLY two-word. Two of the three carry a shouting comment in the original, exclamation marks and all: assign_obj has two opcodes! at `:2192` and assign_dim has two opcodes! at `:2223`. `zend_binary_assign_op_helper` is the ONLY one of the four whose instruction width is DATA-DEPENDENT, which is why it needs a flag, and it is the one with the bug. THE CODEBASE SHOUTS THE INVARIANT AT THE TWO SITES THAT GET IT RIGHT AND IS SILENT AT THE SITE WHERE THE INVARIANT BECAME CONDITIONAL. Both siblings were read and are CLEAN -- `zend_assign_obj_handler` (`:2186-2195`) and `zend_assign_dim_handler` (`:2198-2226`) have exactly one exit each -- and the second of them is LIFTED INTO THIS KERNEL as `PH55_ASSIGN_DIM`, so the contrast is inside the measured program and not only in a comment. No sibling site is owed. ⚠ R1h IS 4f68f3774c34 (Stanislav Malyshev, 2004-08-30, 'fix crash #29893') AND IT IS THREE LINES: the normal exit's own `if (increment_opline) { INC_OPCODE(); }` copied onto the error exit. Nothing is invented. IT IS A HAND BACKPORT: the commit is against 2004-08-30 HEAD, 5.0.0 shipped 2004-07-13, and by fix time the function had gained an inner block and a `FREE_OP_VAR_PTR(free_op1);` that `:1765-1770` does not have, so `git apply` cannot place it -- `controls/r1h_backport.py` runs it and records the failure. WHICH EXIT the hunk belongs to is settled OFFLINE by three independent legs and NOT by `preimage_screen.py`, whose verdict is `CANDIDATE` on the strength of one `NEXT_OPCODE();` line that occurs 117 times in that file (⚠ TASK_PHP_048 §2.3 says 115 and it is off by two; controls/r1h_backport.py COUNTS it): (1) the hunk's own function-context line names `zend_binary_assign_op_helper`; (2) `increment_opline` occurs exactly three times in `zend_execute.c` and all three are inside that function; (3) the other exit ALREADY has the identical guard at 5.0.0, so a patch adding it there would be adding a duplicate. ⚠⚠ ITEM 95 IS CLOSED AND THE ANSWER IS `DELIBERATE HAND-OFF, NOT A SECOND DEFECT`: `INC_OPCODE()`'s own `if (!EG(exception))` guard is a CORRECTION, not an omission. `zend_throw_exception_internal` parks the PC at `&EG(active_op_array)->opcodes[EG(active_op_array)->last-1-1]` (`Zend/zend_exceptions.c:58`), and `last-1-1` is `last-2` while `ZEND_HANDLE_EXCEPTION` is the LAST opcode -- `zend_do_end_function_declaration` emits `zend_do_return` then `zend_do_handle_exception` (`Zend/zend_compile.c:1091-1092`). So the throw parks the PC one slot SHORT of the handler in anticipation of the `EX(opline)++` the handler's own trailing `NEXT_OPCODE()` performs, and `:53` reads the same invariant back. The guard exists to stop the stride being spent TWICE. The exception path is therefore deliberately OUT of this kernel and `PH55_EXCEPTION` is pinned to 0, and NOTES.md §3 carries the trace. ⭐ AND IT STRENGTHENS THE ROW: the same function guards its stride correctly against TWO hazards on one exit and against NEITHER on the other, 23 lines apart. ⚠⚠⚠ THE ROW ALSO CARRIES A VERUS RESULT THAT IS NOT ABOUT THIS DEFECT AT ALL AND IS DECLARED HERE BECAUSE IT DECIDES WHAT EVERY RUST RUNG LOOKS LIKE: **Verus does not support function pointer types.** `c/kernel.c` dispatches through a function pointer stored in each instruction, which is the mechanism; the verifier answers `The verifier does not yet support the following Rust feature: function pointer types`, measured, and `controls/fnptr.rs` is the probe that `controls/negatives.py --verus` runs on every invocation. So all four Rust rungs store an `Option<u8>` handler ID and dispatch with a `match`, `identity` pins R4 == R5 so the representation R5 cannot express is one R4 may not use either, and `controls/fnptr_dispatch.rs` + `controls/fnptr_cost.py` price the substitution instead of waving at it. IT CHANGES NO ANSWER -- `Option<fn>` and `Option<u8>` are `None` for exactly the same opcode -- so what moves is instructions and not behaviour. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "ph55_fold": "ph55_run",
      "MAX_OPS": "64",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 53
    },
    "twin_obligations": {
      "verus.rs": 61
    },
    "obligations_note": "53 verified / 0 errors, and 61 under `--cfg slb_twin` -- eight trusted accessors, therefore eight twins. ⭐⭐ WHAT THE PROOF RESTS ON IS `ok_from`, AND IT IS A STATEMENT ABOUT THE PC RATHER THAN ABOUT THE TABLE: *starting at p and striding by each instruction's own width, every word the PC lands on is an INSTRUCTION word and never a ZEND_OP_DATA word, and every stride stays inside the op_array.* It is the dispatch loop's invariant, it is what discharges `hunwrap`'s `requires t.is_some()`, and it is exactly the invariant zend_binary_assign_op_helper's error exit breaks. ⭐ It is ESTABLISHED BY THE EMITTER and not by the executor -- `emit_from`, written as tail recursion so its postcondition is `ok_from`'s own unfolding -- which is why the interesting half of this proof is two `reveal_with_fuel` asserts and no lemma. The other three unchecked classes rest on facts that have nothing to do with PHP: the driver's `off + len <= buf@.len()`, `c/main.c`'s `stride_w <= 512`, and `all_slots(ts@)` -- every value ever written into a temp slot is a slot index. NOTES.md §10 keeps them apart, because an editor who deleted the 2004 patch would be removing the precondition of ONE of them.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 53 shipped + 8 for slb_twin_bget, _oget, _oset, _kget, _kset, _vget, _vset and _hunwrap. ⭐⭐⭐ THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A MEASUREMENT, NOT AN OMISSION. Verus's default is 10. Bisected on this box (controls/rlimit_bisect.sh; NOTES.md §10 has the table): rlimit 1 gives 53/0 plain and 60 verified / 1 ERROR twin; rlimit 2 gives 53/0 and 61/0; rlimit 30 gives 53/0 and 61/0. So an interpreter with ten handlers, a value postcondition over the whole machine state and EIGHT verified twins needs **2**, and the default is 5x that. ⚠ Compare ph16, whose obligation is a single index bound with no loop in it and which had to ship `#[verifier::rlimit(30)]` because its twin build FAILED at 8. The reason is structural and it is this row's Verus finding: every obligation here is ONE unfolding of a recursive definition whose shape the exec code mirrors, so Z3 never searches.",
    "items": {
      "verus.rs": {
        "two_word_s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "width_s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ok_from": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "handlers_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "all_slots": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_is_tmp": {
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
        "s_gzpp": {
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
        "step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "dec_word": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "with_opcode": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "decoded": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "emitted": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "with_handler": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "passed": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "init_kind": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "init_st": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_slots": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_ts": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "ph55_fold": {
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
        "kget": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_kget": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "kset": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_kset": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "vget": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_vget": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "vset": {
          "external": "verifier::external_body",
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_vset": {
          "external": null,
          "requires": [
            "i < NSLOT"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "hunwrap": {
          "external": "verifier::external_body",
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "r == t.unwrap()"
          ]
        },
        "slb_twin_hunwrap": {
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
        "two_word": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == two_word_s(o)"
          ]
        },
        "is_tmp": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_is_tmp(o)"
          ]
        },
        "var_of": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_var_of(o)",
            "r < NSLOT"
          ]
        },
        "tmp_of": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_tmp_of(o)",
            "r < NT"
          ]
        },
        "emit_from": {
          "external": null,
          "requires": [
            "old(ops)@.len() == MAX_OPS",
            "n <= MAX_OPS",
            "n >= 2",
            "p <= n",
            "old(ops)@[n as int - 2].opcode == RETURN",
            "old(ops)@[n as int - 1].opcode == RETURN"
          ],
          "ensures": [
            "final(ops)@.len() == MAX_OPS",
            "ok_from(final(ops)@, n as int, p as int)",
            "forall|j: int| 0 <= j < p && j < MAX_OPS ==> final(ops)@[j] == old(ops)@[j]",
            "forall|j: int| n <= j < MAX_OPS ==> final(ops)@[j] == old(ops)@[j]",
            "final(ops)@[n as int - 2] == old(ops)@[n as int - 2]",
            "final(ops)@[n as int - 1] == old(ops)@[n as int - 1]",
            "final(ops)@ == emitted(old(ops)@, n as int, p as int)"
          ]
        },
        "gzpp": {
          "external": null,
          "requires": [
            "all_slots(ts@)",
            "ts@.len() == NT",
            "kind@.len() == NSLOT",
            "val@.len() == NSLOT"
          ],
          "ensures": [
            "r < NSLOT",
            "r as int == s_gzpp( St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false }, op, )"
          ]
        },
        "gzp": {
          "external": null,
          "requires": [
            "all_slots(ts@)",
            "ts@.len() == NT",
            "kind@.len() == NSLOT",
            "val@.len() == NSLOT"
          ],
          "ensures": [
            "r == s_gzp(St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false }, op)"
          ]
        },
        "fetch_dim": {
          "external": null,
          "requires": [
            "kind@.len() == NSLOT",
            "val@.len() == NSLOT",
            "ts@.len() == NT"
          ],
          "ensures": [
            "r < NSLOT",
            "r as int == s_fetch( St { kind: kind@, val: val@, ts: ts@, acc: 0, pc: 0, done: false }, base, dim, )"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "16 <= len",
            "len <= 8 * MAX_OPS"
          ],
          "ensures": [
            "r == ph55_fold(buf@, off as int, len as int)"
          ]
        },
        "lemma_ok_from_opcodes": {
          "external": null,
          "requires": [
            "a.len() == b.len()",
            "n <= a.len()",
            "0 <= p",
            "forall|j: int| 0 <= j < a.len() ==> #[trigger] b[j].opcode == a[j].opcode",
            "forall|j: int| 0 <= j < a.len() ==> #[trigger] b[j].ext == a[j].ext",
            "ok_from(a, n, p)"
          ],
          "ensures": [
            "ok_from(b, n, p)"
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
        "oset": "`x: Op` is a PURE VALUE and needs no precondition. The unchecked operation is `*a.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `a` being a live `[Op; 64]`, and on NOTHING about the record being written -- every inhabitant of `Op` is a legal store into a slot that is already initialised (`[ZERO_OP; MAX_OPS]` initialises the whole array before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < MAX_OPS`, and the `ensures` names the WHOLE post-state -- `old(a)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition.",
        "kset": "`x: u8` is a PURE VALUE and needs no precondition, for exactly oset's reason one type down: definedness depends on `i`, which IS constrained by `i < NSLOT`, and the `ensures` names the whole post-state. ⚠ The entry exists separately because the ARRAY is different -- `[u8; 42]` rather than `[Op; 64]` -- and a reviewer checking that the bound matches the array is checking two different pairs.",
        "vset": "`x: u64` is a PURE VALUE and needs no precondition; same argument as kset, on the value half of the same zval store. ⚠ `kset` and `vset` are two wrappers and not one because this kernel keeps `zval.type` and `zval.value.lval` in PARALLEL ARRAYS; a `[Zv; 42]` of a two-field record would have halved this row's trusted surface and was NOT taken. NOTES.md §10 records the trade rather than hiding it.",
        "oget": "`a: &[Op; MAX_OPS]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its length is in its TYPE, so there is nothing about it left for a `requires` to say: `a@.len() == MAX_OPS` holds for every `a` this signature admits. The only quantity that can make `*a.get_unchecked(i)` undefined is `i`, and `i` IS constrained, by `i < MAX_OPS`. ⚠ IT IS NOT THE SAME ARGUMENT AS `bget`'s: `bget` takes a SLICE, whose length is a run-time fact, so its `requires` has to name it (`i < v@.len()`) and the stage is satisfied without a declaration.",
        "kget": "same argument as oget on `&[u8; 42]`: the length is in the type, the index is constrained by `i < NSLOT`, and there is nothing else a `requires` could honestly say.",
        "vget": "same argument as oget on `&[u64; 42]`: the length is in the type, the index is constrained by `i < NSLOT`, and there is nothing else a `requires` could honestly say.",
        "hunwrap": "⭐⭐ THE ROW'S OWN TRUSTED ITEM, AND ITS PARAMETER IS THE WHOLE STORY. `t: Option<u8>` is a value with exactly two shapes and the `requires` names the one the body assumes: `t.is_some()`. There is no second parameter to leave unconstrained -- the shape this stage exists to catch cannot arise here, because the ONLY thing that can make `t.unwrap_unchecked()` undefined is `t` itself. ⚠ What makes the entry worth reading is WHERE the precondition comes from: not from arithmetic and not from the caller's convenience, but from `ok_from` -- the dispatch loop's invariant, established by the emitter pass, and the exact invariant `4f68f3774c34` restores. `controls/negatives.py --emit nofixup` deletes the pass and that mutant must FAIL to verify."
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph55's two probe shapes have different work per call (128 and 512 window bytes, i.e. 16 and 64 instruction words) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW IN BYTES and the number of instruction words is `stride / 8`, an exact linear function of it, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ THERE IS ALSO A FIXED PER-CALL TERM AND IT IS LARGE: the op_array (64 x 16 bytes) and the zval store (42 slots) are zeroed on EVERY call whatever the stride, and the final fold walks all 42 slots plus 4 temps. So the marginal is NOT a pure dispatch rate and NOTES.md §8 decomposes it rather than presenting it as one."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "differ",
      "why": "⚠⚠ R4 AND R5 DIFFER AT BOTH LEVELS, AND THE `exact` THIS ENTRY FIRST DECLARED WAS REFUTED BY THE FIRST GATE RUN. Measured against the SHIPPED record (results-php/ph55-opdata-stride.json, O3/isolated): 876 instructions and md5_fn 37f8a672831f6774 in `unsafe` against 872 and 30602b986da0f05b in `verus` -- and `norel` does not rescue it either (87140a47b1370398 vs 9a0ed674d02a9bf0), so it is not relocation bytes. The exec code is character-identical apart from the `verus!` block, the spec/proof items and the clauses; what differs is REGISTER ALLOCATION AND SCHEDULING, and R5 is the SHORTER of the two by four instructions while costing 22 544 Ir MORE on small.bin (A1 1577.830 vs 1576.703 per call, +0.071 %). ⚠ THE CAUSE IS NOT IDENTIFIED and this entry says so rather than inventing one: the two cells are built by different drivers (`rustc` for R4, the Verus driver for R5) and NOTES.md §10 records the three hypotheses that were NOT distinguished. ⚠ At O0 the two differ far more -- 1199 vs 1048 instructions -- because at O0 nothing is inlined, so R5's eight trusted wrappers survive as real calls where R4's `#[inline(always)]` helpers do not; that is codegen, not layout. ⭐⭐ CONSEQUENCE, AND IT IS NOT A FORMALITY: `.memory/02-bench-rules.md` makes Miri NON-WAIVABLE when R4 and R5 are not the same machine code, so this row's `miri.required: true` is load-bearing twice over -- once for the eight trusted items and once for this pin. ⚠ The figures here are from the shipped measurement record; PROTOCOL.md rule 6's addendum says to re-read this entry against THAT record rather than trusting the hash."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph55 has EIGHT such items and three of them WRITE (`oset`, `kset`, `vset`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `a@[i] == x` would let a body that also clobbered `a[i + 1]` through every Verus stage. Each shipped `ensures` is the whole post-state, `old(a)@.update(i, x)`, and Miri is the backstop for the class regardless. ⭐ AND ONE OF THE EIGHT IS NOT AN INDEX AT ALL: `hunwrap` is `Option::unwrap_unchecked`, whose misuse is not an out-of-bounds access but a read of an uninhabited discriminant, and Miri is the only detector in this tree that sees that class.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph55's cost is 4 x (one op_array decoded, fixed up, pass_two'd and executed), i.e. 4 x at most 64 dispatches -- four orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_execute.c",
    "c_lines": [
      1724,
      1796
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '1724,1796p'",
    "extract_sha256": "9bce864972fdf5d7086b5ded5f59aa46a20580c1f02a22784cd4c7ae2a818fe6",
    "extra_spans": [
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          1313,
          1338
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '1313,1338p'",
        "extract_sha256": "db683b0f6b210280a9a6387bd5d7e1d2a9447f3d4e61a042ddab01366df29eed",
        "why": "THE TWO MACROS AND THE TABLE. `NEXT_OPCODE()` is `CHECK_SYMBOL_TABLES() EX(opline)++; return 0;` (:1317-1320) -- stride 1 AND a return -- and `INC_OPCODE()` is `if (!EG(exception)) { CHECK_SYMBOL_TABLES() EX(opline)++; }` (:1326-1330) -- conditional, and no return. The whole defect is which of the two a given exit calls. The span also carries `ZEND_API opcode_handler_t zend_opcode_handlers[512];` at :1338 and the `#else`-empty `CHECK_SYMBOL_TABLES()` at :1313-1315 that a non-ZEND_DEBUG build compiles."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          1383,
          1396
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '1383,1396p'",
        "extract_sha256": "a18c98a900b0f3ca097b5a0b9a7dec02445d40b597a59265653abcda701bb351",
        "why": "⛔ THE DISPATCH LOOP, AND IT IS THE HALF WITHOUT WHICH THE STRIDE ERROR WOULD BE HARMLESS. `while (1) { zend_clean_garbage(TSRMLS_C); if (EX(opline)->handler(&execute_data, EX(opline), op_array)) { return; } }` -- fourteen lines with NOTHING between the `handler` field and the call: no PC bound, no NULL test, no assertion. c/kernel.c's `ph55_execute` IS this loop."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          2198,
          2226
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '2198,2226p'",
        "extract_sha256": "5200ef0a9cb8b3ce6d50498e2c20b2308c453db80f11eaa97cd3e411a9b5e10b",
        "why": "⭐ THE CLEAN SIBLING, LIFTED ON PURPOSE. `zend_assign_dim_handler` is STATICALLY two-word, so it needs no flag, has exactly ONE exit, and ends `INC_OPCODE(); NEXT_OPCODE();` under upstream's own `/* assign_dim has two opcodes! */` at :2223 -- exclamation mark in the original. It is `PH55_ASSIGN_DIM` in the kernel, so the contrast between a static width and a data-dependent one is inside the MEASURED program and not only in a comment. The manager read both siblings (this one and `zend_assign_obj_handler`, :2186-2195) and both are clean; no sibling site is owed."
      },
      {
        "c_file": "Zend/zend_execute.c",
        "c_lines": [
          4426,
          4427
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '4426,4427p'",
        "extract_sha256": "23b3b6e1e4c39621b20dcfcfb862821e25de79deaf40faa5f31424edd1e3f2ff",
        "why": "⭐ TWO LINES, AND THE SECOND IS THE HARM. `zend_opcode_handlers[ZEND_ASSIGN_OBJ] = zend_assign_obj_handler;` then `zend_opcode_handlers[ZEND_OP_DATA] = NULL;`. The span is two lines rather than one deliberately: the NULL sits BETWEEN real assignments, and it is the ONLY `= NULL` among the 130 `zend_opcode_handlers[...]` assignments in `zend_init_opcodes_handlers()` (`:4276-4443`, 168 lines) -- counted on the pristine tarball rather than estimated. It is an explicit decision, not an omission, and citing it alone would lose that."
      },
      {
        "c_file": "Zend/zend_opcode.c",
        "c_lines": [
          341,
          366
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_opcode.c | sed -n '341,366p'",
        "extract_sha256": "2e82e7e63352f083f0b55c0a21333f2f87fc3625de051afeb769ff722bb4ec92",
        "why": "`pass_two`'s walk, and the line that makes the NULL REACHABLE FROM A PC: `opline->handler = zend_opcode_handlers[opline->opcode];` at :363. Without it the data word would have no handler field to be NULL. The rest of the span is jump-address fixup and constant refcounting, which this kernel has no analogue for and which provenance.divergences itemises as deleted."
      }
    ],
    "extra_spans_note": "THE ROW LIFTS SIX SPANS AND ALL SIX ARE PINNED. `provenance.c_lines` names the defect site (zend_execute.c:1724-1796, `zend_binary_assign_op_helper`); the five extras are the two stride macros plus the opcode table (:1313-1338), the dispatch loop (:1383-1396), the clean sibling the kernel also lifts (:2198-2226), the NULL table entry (:4426-4427) and `pass_two`'s handler copy (zend_opcode.c:341-366). ⚠ FIVE OF THE SIX ARE THE *HARM*, NOT CONTEXT: facts 5 through 9 of the mechanism live in them, and a row that pinned only the defect site would certify a span containing the wrong stride and nothing that makes a wrong stride fatal. ⚠ What is NOT pinned as a span is `Zend/zend_compile.c:1078-1092` -- `zend_do_handle_exception` and `zend_do_end_function_declaration` -- which is cited in `c/kernel.c` and in NOTES.md §3/§4 for the two-terminator tail and for item 95's closure, but whose CODE this kernel does not lift: the compiler is outside the row.",
    "tier": "modelled",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "zend_execute.c:1724, :1340-1345, :1390-1391",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "zvals become (kind, val) pairs in one flat store and `zval **` becomes an INDEX into it",
        "kind": "substitution",
        "where": "zend_execute.c:1726-1727, :1765-1768, :1786",
        "why": "`EG(error_zval_ptr)` and `EG(uninitialized_zval_ptr)` are two RESERVED INDICES, so *var_ptr == EG(error_zval_ptr) at :1765 is an index comparison and the branch structure is one for one. Refcounting, `SEPARATE_ZVAL_IF_NOT_REF` (:1772), `SELECTIVE_PZVAL_LOCK` and `AI_USE_PTR` are gone; none of them touches the PC, which is what this row measures. Demonstrated behaviour-preserving on the extracted domain by model.py's three independent implementations plus inputs/gen.py::_check_span, which asserts every arm of the substituted test is reached. No semantics."
      },
      {
        "what": "`zend_fetch_dimension_address(..., BP_VAR_RW)` becomes `ph55_fetch_dimension_address`",
        "kind": "substitution",
        "where": "zend_execute.c:1744, :2218",
        "why": "the ONE property this row needs is kept: on a non-array base it yields `EG(error_zval_ptr)`, because `zend_fetch_dimension_address_inner` raises 'Cannot use a scalar value as an array' and sets the error zval. That is `$x = 1; $x[0] += 1;` -- the corpus's own trigger for CRASH-023 -- and it is what makes the error arm reachable at all. The hash-table lookup it performs on an array base is the CONTAINER and not the defect (.memory-php/01-extraction.md: extraction cost is priced at the DEFECT site). No semantics on the extracted domain."
      },
      {
        "what": "the `case ZEND_ASSIGN_OBJ:` arm of the switch",
        "kind": "deletion",
        "where": "zend_execute.c:1731-1733",
        "why": "it is a `return zend_binary_assign_op_obj_helper(...)` into ONE OF THE THREE unconditional `INC_OPCODE(); NEXT_OPCODE();` sites (:1719), so it strides 2 on every path and carries no part of the defect; keeping it would require the object machinery for no mechanism. ⭐ Its clean sibling `zend_assign_dim_handler` (:2198-2226) IS lifted as PH55_ASSIGN_DIM, so the static-vs-data-dependent contrast survives the deletion. The switch is left with TWO arms and inputs/gen.py asserts the corpus reaches both. No semantics on the extracted domain."
      },
      {
        "what": "the exception path, and `EG(exception)` pinned to 0",
        "kind": "projection",
        "where": "zend_execute.c:1327, Zend/zend_exceptions.c:36-59",
        "why": "⭐ ITEM 95, CLOSED. `INC_OPCODE()`'s own `if (!EG(exception))` guard is NOT a second instance of the defect: `zend_throw_exception_internal` parks the PC at `opcodes[last-1-1]` (zend_exceptions.c:58), one slot SHORT of the ZEND_HANDLE_EXCEPTION word that `zend_do_end_function_declaration` emits last (zend_compile.c:1091-1092), in anticipation of the `EX(opline)++` the handler's own trailing NEXT_OPCODE() performs -- and :53 reads the same invariant back. The guard stops the stride being spent TWICE; it is a CORRECTION. Modelling it would add a whole exception machinery for no mechanism, so the kernel keeps INC_OPCODE()'s body verbatim with the token pinned to 0. The row builds ONE faulting exit, not two. NOTES.md §3."
      },
      {
        "what": "`zend_init_opcodes_handlers`'s 200 assignments become a C99 designated initialiser",
        "kind": "substitution",
        "where": "zend_execute.c:4230-4440",
        "why": "upstream fills the table once at startup in a function; the kernel fills it once at LINK time in a static initialiser, because a per-call `ph55_init_opcodes_handlers()` would put 200 stores inside the measured loop and measure the wrong thing. The ONE entry this row turns on -- `[PH55_OP_DATA] = NULL` -- is written out explicitly because upstream writes it out explicitly. No semantics."
      },
      {
        "what": "`zend_clean_garbage(TSRMLS_C)` becomes the per-dispatch opcode fold",
        "kind": "projection",
        "where": "zend_execute.c:1390",
        "why": "upstream sweeps refcounts once per dispatch and returns void; this kernel has no refcounts, so the slot is occupied by the one observation the benchmark needs -- `acc = acc * 31 + opline->opcode`, which is what makes the EXECUTED TRACE land in the checksum rather than only in a sanitizer. It is the row's analogue of ph16's fold standing in for `php_select`. Nothing observable in the returned u64 depends on the sweep itself."
      },
      {
        "what": "`safe_emalloc(sizeof(temp_variable), op_array->T, 0)` becomes a frame array",
        "kind": "substitution",
        "where": "zend_execute.c:1352",
        "why": "`EX(Ts)` is heap-allocated with a size that is a COMPILE-TIME constant of the op_array (`op_array->T`), so it is O(1) per call in the input and PROTOCOL_PHP.md B1a's precondition holds. The kernel keeps it as a fixed frame array of PH55_NT slots instead, which is what lets `provenance.uses_allocator` be false and what keeps this row's cross-language column free of the allocator caveat B1a puts on ph64. No semantics."
      },
      {
        "what": "the op_array is a `[PH55_MAX_OPS]` frame array and the driver refuses a larger window",
        "kind": "substitution",
        "where": "zend_opcode.c:349 (`erealloc(op_array->opcodes, ...)`), c/main.c",
        "why": "PHP's op_array is heap-grown by `get_next_op` and has no capacity bound; the kernel uses a frame array of 64 records, so the bound lives in the DRIVER as `stride_w <= 512`, outside every measured loop and outside the executor. ⚠ IT IS NOT A CHECK IN THE EXECUTOR and must not become one: the dispatch loop still has no PC bound, which is the row. The C array is written `= {{0, 0, 0, 0, 0, NULL}}` for PARITY with safe Rust, which cannot declare `[Op; 64]` without initialising it; a fixed per-call term present in one language and absent in the other would read as a C-versus-Rust result. No semantics."
      },
      {
        "what": "the emitter's guarantee becomes an explicit chain walk (`ph55_emit_fixup` / `emit_from`)",
        "kind": "projection",
        "where": "Zend/zend_compile.c, `zend_do_assign_op` and every `get_next_op` caller",
        "why": "⭐ zend_compile emits ZEND_OP_DATA ONLY as the trailing word of a two-word instruction, so no instruction START is a data word -- and THAT is the invariant `execute()` relies on when it dispatches without testing. The compiler is outside this row (the blob IS the op_array, PLAN_PHP.md 3 criterion 3), so something must stand in for it. This walk visits exactly the words a CORRECT executor visits and refuses a data word at any of them, and TOUCHES NOTHING ELSE -- a pass that normalised every data word would make inputs/adversarial-opdatalive.bin unrepresentable. Every rung has it, identically, so no rung is advantaged. It is a PROJECTION rather than a substitution because it models a compile-time property with a run-time pass."
      },
      {
        "what": "the emitter walk is TAIL RECURSION in the Rust rungs and a `while` loop in C",
        "kind": "substitution",
        "where": "c/kernel.c `ph55_emit_fixup`, *.rs `emit_from`",
        "why": "the property it establishes (ok_from in verus.rs) is defined by recursion on the instruction chain, so as tail recursion the postcondition is the definition's own unfolding and needs no lemma; as a loop it needs an invariant quantified over instruction starts plus a glue lemma. C has nothing to prove and writes the loop. ⚠ ALL FOUR RUST RUNGS WRITE THE RECURSION, including R2 and R3 which have no proof, so the R3->R4 gradient is not polluted by it. LLVM tail-calls it at -O3. Demonstrated behaviour-preserving by the gate's own stage-3 checksum comparison across all six rungs on every input. No semantics."
      },
      {
        "what": "`opline->handler` becomes `Option<u8>` + a `match` in every Rust rung",
        "kind": "substitution",
        "where": "zend_execute.c:1391, zend_opcode.c:363",
        "why": "⚠⚠ FORCED, AND IT IS THE ROW'S VERUS FINDING. Verus answers `The verifier does not yet support the following Rust feature: function pointer types` on a `[Option<fn(..)>; N]` parameter -- measured, controls/fnptr.rs is the probe and controls/negatives.py --verus runs it -- and `identity` pins R4 == R5, so a representation R5 cannot express is one R4 may not use either. ⭐ IT CHANGES NO ANSWER: `Option<fn>` and `Option<u8>` are `None` for exactly the same opcode, so both spellings turn C's NULL CALL into the same `unwrap()` panic. controls/fnptr_dispatch.rs is safe_naive.rs with the function-pointer table and controls/fnptr_cost.py measures the difference, so what this substitution costs is a number and not a shrug. No semantics."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠ SIX of these twelve entries are SUBSTITUTIONS and THREE are PROJECTIONS, which is a lot, and the reason is structural rather than sloppy: this defect's frame is the whole Zend executor, and everything between a `zval **` and a program counter is machinery in another file. PROTOCOL_PHP.md A1 requires a substitution in a non-`modelled` tier to be (a) itemised with a line citation, (b) given a `why` ending in 'no semantics' and (c) DEMONSTRATED behaviour-preserving rather than asserted. (c) is discharged by model.py's three independent implementations plus inputs/gen.py::_check_span for the zval and operand encodings, by the gate's own stage-3 cross-rung checksum comparison for the recursion/loop and the frame-array substitutions, and by controls/fnptr_cost.py for the dispatch representation -- which is the one whose (c) is a MEASUREMENT of what it costs rather than only of whether it changes an answer.",
    "root_cause_ids": [
      "assign-op-dim-error-zval-skips-op_data-increment"
    ],
    "cwe": "CWE-476",
    "cwe_note": "index.csv records CWE-476 (NULL pointer dereference) and this row reproduces exactly that: `c/kernel.c`'s `ph55_execute` calls through a `handler` field that `pass_two` filled from `zend_opcode_handlers[ZEND_OP_DATA]`, which is NULL. ⚠⚠ AND THE ROW SAYS, IN ITS OWN INPUTS, THAT CWE-476 IS THE MANIFESTATION AND NOT THE DEFECT. The defect is a CONTROL-FLOW error -- a wrong PC -- and `inputs/adversarial-opdatalive.bin` mis-strides by exactly as much as `inputs/adversarial-nullcall.bin`, differs from it in ONE BYTE, produces a WRONG ANSWER with exit 0, and is declared `sanitizer_expect: clean` because there is nothing for a sanitizer to say. ⭐ That is why `model.py::sanitizer_expect` derives from the NULL DISPATCH and not from the mis-stride, and says so in its own docstring. NOTES.md §6 prices the pair.",
    "fix_commit": "4f68f3774c34948ac651344d73c9d9e0a08801e6",
    "fix_commit_note": "⚠ THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE AND THE ROW USES ITS SHORT FORM EVERYWHERE. `4f68f3774c34` -- Stanislav Malyshev, 2004-08-30, 'fix crash #29893' -- is ONE FILE, THREE INSERTIONS, ZERO DELETIONS; the patch bytes are at controls/4f68f3774c34.patch. ⭐⭐ IT IS THE CLEANEST R1h IN EITHER PROGRAMME: the three lines are the normal exit's own `if (increment_opline) { INC_OPCODE(); }`, copied onto the error exit. Nothing is invented and there is no second hunk to adjudicate. ⚠⚠ BUT IT IS A HAND BACKPORT AND `git apply` FAILS: the commit is against 2004-08-30 HEAD (the hunk header says `@@ -1942,6 +1942,9 @@`), 5.0.0 shipped 2004-07-13 with the function at :1724-1796, and by fix time the error exit had gained an inner block and a `FREE_OP_VAR_PTR(free_op1);` that :1765-1770 does not have. controls/r1h_backport.py RUNS `git apply` against the pristine span on every invocation and records the refusal -- `error: while searching for: ... FREE_OP_VAR_PTR(free_op1);` -- rather than asserting it, AND ships controls/4f68f3774c34-backport-5.0.0.patch as the POSITIVE CONTROL that makes that verdict worth anything: the SAME three inserted lines, character for character, with 5.0.0's own context, which applies cleanly and moves the bytes at :1765-1770. THAT CONTROL EXISTS BECAUSE THE FIRST VERSION OF THE CHECK GOT THE ANSWER BACKWARDS: `git apply --check` SILENTLY SKIPS a patch whose target path is GITIGNORED in the enclosing repository and returns exit 0, and .temp/ is gitignored here, so the check said 0 and nothing had been applied. --check is not the test; the bytes are, and gitignore_trap() reproduces the trap on every run. ⚠⚠ WHICH EXIT the three lines belong to is settled OFFLINE BY THREE LEGS AND NOT BY THE SCREEN: `preimage_screen.py --id CRASH-023` returns CANDIDATE with `hits [[1769, \"\\t\\tNEXT_OPCODE();\"]]`, `misses []`, `n_matchable 1`, and `NEXT_OPCODE();` occurs 117 times in that file, so '1/1 cited 5.0.0 lines are present in the pre-image' is true and nearly information-free. The screen has done its job -- it is an EXCLUSION tool (F68 / item D11) and it correctly declines to exclude -- and the row does not quote it as confirmation. The three legs are in `idiom.required[5]`. ⚠ UNVERIFIED IN THIS ROW: whether `4f68f3774c34` is the FIRST commit to close this site, and whether any 5.0.x branch backport preceded it. It is what index.csv names, its patch really does add the guard at the error exit, and 5.0.0 is unguarded; what was not done is a tag-by-tag bisect. PROTOCOL_PHP.md F5(iii) asks for confirmation against the tags and this row confirms the SITE and the DIRECTION rather than the exact commit.",
    "invariant": "I18",
    "obligation": "O2",
    "invariant_note": "⚠ THE CATALOGUE ROW SAYS `I18 + I12` AND BOTH ARE RIGHT, AT TWO DIFFERENT POINTS OF ONE CHAIN, and this block can name only one so it names the first. **I18** is *opcode and IR well-formedness* -- 'every instruction handed to the interpreter must actually carry the operands its handler is going to read' -- and its **O2** is 'an opcode or fetch-mode rewrite ... must preserve operand presence and handler expectations rather than silently reinterpret them'. That is the WRONG PC: the executor hands itself an operand record and reads it as an instruction. **I12/O1** is 'a NULL return, sentinel, status code, or NULL-able out-parameter must be tested before the result is read through', and that is the DISPATCH: `opline->handler` is a NULL-able pointer read through without a test at :1391. ⭐ The two halves are exactly the two adversarial inputs. `adversarial-opdatalive.bin` breaks I18/O2 and NOT I12/O1 -- the word it lands on has a handler -- and it is the input no detector sees. Blind-labelled by the corpus (`paper/invariants-list.md`) and carried across unmodified.",
    "echoes": [
      "p19"
    ],
    "echoes_note": "p19 is the closest PAT analogue by the catalogue's own `echoes` column. ⚠ PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and NEVER a filter, and patterns-php/ is fresh: 'that's p19's mechanism' may not refuse a candidate. The mechanisms differ where it matters anyway -- this row's blob IS the instruction stream, which the catalogue calls out as the one candidate whose ORIGINAL C SHAPE is the pinned kernel shape, so nothing about the dispatch had to be translated on the C side.",
    "uses_allocator": false,
    "uses_allocator_why": "the kernel allocates nothing. PHP's op_array is heap-grown by `get_next_op` at COMPILE time and the compiler is outside this row; `EX(Ts)` is a `safe_emalloc` in `execute()` (zend_execute.c:1352) whose size is `op_array->T`, a COMPILE-TIME constant, so it is O(1) per call in the input and this kernel keeps it as a fixed frame array instead. No emalloc, no efree, no php_shim_reset, no php_shim_tally. ⭐ That is why PROTOCOL_PHP.md B1a's caveat does NOT apply to this row's cross-language column: unlike ph64 there is no allocator term in it at all. ⚠ DECLARED, NEVER DETECTED (TASK_PHP_008 §0.4) -- nothing reads this field and no verdict depends on it. The row still carries c/emalloc_shim.h as a symlink, because that rule is UNCONDITIONAL."
  }
}
```
