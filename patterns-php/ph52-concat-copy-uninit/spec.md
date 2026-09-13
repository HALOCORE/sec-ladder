# ph52 — an unconstructed caller slot destructed on an early exit

**PHP 5.0.0, `Zend/zend.c:242-247` with `:263`, `Zend/zend_operators.c:1148`,
`:1187-1192` and `Zend/zend_variables.c:36-80`, corpus row LOGIC-007, tier
`narrowed`.** `concat_function` declares **`zval op1_copy, op2_copy;`** — bare
stack locals, no `= {0}`, no `INIT_ZVAL`, no `memset` — and hands their addresses
to `zend_make_printable_zval`, which writes `expr_copy->value.str.*` on every arm
and `expr_copy->type` **once, at `:263`, after the switch**. The `EG(exception)`
early exit at `:243` tears the slot down first.

⚠⚠⚠ **The harm is a TAG-DISPATCHED FREE, not a read.** `_zval_dtor` switches on
`zvalue->type & ~IS_CONSTANT_INDEX` and releases a pointer read out of the *same*
uninitialised slot: **CWE-457 with CWE-824 as the consequence**. And on the common
path (`:190-193`) `expr_copy` is never written at all, so the function's own
convention is *constructed only if `*use_copy`* — and this arm destructs it anyway.

⚠⚠ **The uninitialised memory is on the STACK, and that made DETERMINISM the
row's first deliverable rather than a rung.** Every mechanism this tree has for
uninitialised memory is an allocator shim. `controls/d0_stack.py` is the
measurement, committed rather than left in `.temp/`: over 16 cells the stack
offset is reused **exactly**, so the trigger is a **call history** — and without a
`noinline` on the lifted callees **2 of the 16 answer differently**, because at
`-O3` a compiler that can see the unwritten tag may treat it as `undef` and fold
the teardown away. `NOTES.md` §4.

⭐⭐ **And the corpus's `uninit-read-silent` is explained, not excused.**
`controls/tag_sweep.py` drives the whole tag byte through `_zval_dtor` and measures
**12 of 256 values (4.688 %) tearing anything down, 8 of 256 (3.125 %) reaching
`efree`** — so **95.3 % of byte values make `:243` a no-op**, and `IS_NULL` is `0`.
That figure is the answer to *why do uninitialised-read bugs survive for years in
shipped code*. ⚠ `RECAP_PHP.md` F102's untested *"five named cases"* is wrong in
three ways and `NOTES.md` §6 itemises them.

⭐⭐⭐ **What this row publishes that `ph53` structurally could not: the defect is
in the published u64.** `php_shim_tally()` is folded into the kernel's return, and
`:243`'s teardown is observable only through the allocator — so on
`inputs/adversarial-dblfree.bin` **R1 prints `272040826665440682` and R1h prints
`272040826666539789`** in all four C cells, while `inputs/adversarial-safe.bin` —
the same op shape with one byte changed so `:243` runs on a *safe* slot — gives
`254123829775225275` on all six rungs.

⭐⭐ **And the upstream fix is COMPLETE, which is the opposite of `ph53`'s result.**
`7412202c43e7` (2006) deletes one line, and because `:263` writes the tag after the
switch there is nothing left for the deletion to miss. ⚠ It is a **hand
reconstruction** and not a `patch -p1` — the 2006 context names two tokens that do
not exist in 5.0.0 — and `controls/r1h_onelinedel.py` is that argument as a check.
⭐ The consequences are that R2–R5 *are* ports of R1h and that the adversarial
input *can* ship; `ph53` could do neither.

The machine-readable contract follows.
`harness-php/gate.py ph52-concat-copy-uninit` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "8 <= len"
  ],
  "ensures": [
    "result == concat_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (concat_fold). ⚠⚠ model.py's `concat_fold` IS ITS SECOND, INDEPENDENT IMPLEMENTATION and not the simulation that produced `result`: `_window` is an imperative transcription of c/kernel_hardened.c with two mutable slot variables named as the C names them and one mutable Alloc, while `concat_fold` mirrors verus.rs's `s_print` / `s_dtor` / `s_op` / `s_run` as pure transitions over a returned tuple. A THIRD spelling, `_dumb`, collects the allocator REQUEST SEQUENCE as a flat list with no cache at all and replays it through a cache built from scratch, and spells the object arm's digest from the LITERALS rather than from the PH52_DIG_* constants, so it checks those too; it shares no code with either of the other two. ⭐ AND model.py CANNOT EXPRESS THE DEFECT: there is no Python spelling of \"read a stack byte nobody wrote\", so its unconstructed slot is `None` and `zval_dtor` on it is SKIPPED. That makes it a genuinely independent second opinion -- it agrees with both C rungs on every measured window and on adversarial-safe.bin, and on adversarial-dblfree.bin, where the C double-frees, R1's answer is recorded by check.py stage 4 rather than required to agree. It is also a small statement of this row's own ladder result. selfcheck() drives the three implementations against each other on the calls each input makes AND on 69 SYNTHETIC WINDOWS model.py builds itself, spanning every (arm, aux-parity) pair on BOTH sides independently, the faulting arm at op 0 with the slot unconstructed, the faulting arm after each of the three DANGLING arms and each of the three SAFE ones, the pass-through arm carrying a state across a six-op run, an empty op stream, a full one, the object handle's 1-, 2- and 3-digit cases and every arm against every arm -- i.e. every slot shape the measured corpus is FORBIDDEN to contain. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. ⭐⭐ AND THE SWEEP CARRIES ITS OWN CONTROLS, because a sweep that cannot fail is not a check (PROTOCOL_PHP.md H): FOUR must-fire mutants of `run_ops` are driven over the same 69 windows and each must be caught -- M1 the tag written EARLY, which is the catalogue's own tidying trap; M2 STR_FREE losing its `!= empty_string` test, which turns the three SAFE arms dangerous; M3 the pass-through arm CLEARING the slot instead of leaving it alone, which makes the call history unobservable; and M4 the allocator's cache ignored, which is the one mutant a row with O(1) allocations per call could not detect -- plus one MUST-NOT-FIRE equivalent rewrite that threads the slot pair through a dict, so the sweep is keyed on the function and not on the spelling. It also asserts that the sweep REACHES what it claims to: all five arms, `:243` on an unconstructed slot, `:243` on a DANGLING slot, and `:243` on a SAFE slot.",
  "idiom": {
    "required": [
      {
        "c": "`expr_copy->type = PH52_IS_STRING;` -- THE TAG, WRITTEN LAST, AFTER THE SWITCH. `zend.c:263`. Present in BOTH C rungs and in that position in both. ⚠⚠ THIS IS AN ORDERING PIN AND THE CATALOGUE DOES NOT ASK FOR IT: the defect lives in the fact that the tag is written last, so a kernel that writes it EARLY -- the tidy ordering a careful author reaches for -- deletes the defect while keeping every line that looks load-bearing. value first, type last. The span is the one STATEMENT that decides it and it is in both rungs deliberately: `7412202c43e7` moves nothing here. `model.py::_mutants` M1 and `controls/negatives.py --verus` V4 are the two places this is driven rather than asserted.",
        "rust": "`*constructed = true;` -- THE WITNESS, WRITTEN LAST, AFTER THE SLOT. Present in unsafe.rs and verus.rs and in no other rung, because no other rung HAS a witness: safe_naive.rs's ordering pin is the `Option`'s own discriminant and safe_tuned.rs has no slot at all. The set of rungs lives in this English, which is what the named-spelling standard says about scope. ⚠ In verus.rs the ordering is not merely a convention: make_printable_zval's `ensures` carries `s.1.c ==> final(expr_copy).mem_contents().is_init()`, so setting the witness on a path that did not write the slot FAILS THE PROOF -- which is what V4 measures."
      },
      {
        "c": "`ph52_zval_dtor(expr_copy);` -- THE DEFECT, `zend.c:243`, a tag-dispatched teardown of a slot no path reaching it has constructed. ⛔ PRESENT IN c/kernel.c AND ABSENT FROM c/kernel_hardened.c, AND THAT ABSENCE IS THE WHOLE OF THE UPSTREAM FIX: `7412202c43e7` is 1 file, 1 hunk, 0 insertions, 1 deletion. ⭐ `controls/r1h_onelinedel.py` makes that a CHECK rather than a claim -- it regenerates the hardened kernel from the plain one and reports `code lines only in R1: 1`, `code lines only in R1h: 0`, with an 11-case must-fire / must-NOT-fire suite. It is the same spelling the commit deletes, up to one tab of indentation.",
        "rust": "`slot_read_unchecked` -- the READ the C performs with nothing between. Present in unsafe.rs and verus.rs, absent from safe_naive.rs and safe_tuned.rs, which have no unconstructed slot to read. ⚠ It is the ONE trusted item on this row, against ph53's four, because ph52's slots are two NAMED LOCALS and not an array -- so there is no unchecked indexing to fold in. `MaybeUninit::assume_init_ref` is the one operation here that the pinned vstd ALREADY SPECIFIES, in std_specs/maybe_uninit.rs:45-49, so in ordinary exec code it costs NO trusted item -- `controls/mu_unwrapped.rs` verifies exactly that at 6/0. ⛔ This file cannot use it: check.py requires every `unsafe` token in a Verus source to sit inside an external_body body, and 5c-twin then demands a twin that cannot exist for a MaybeUninit read. See verus.twin_justifications and NOTES.md 11."
      },
      {
        "c": "`zvalue->type & ~PH52_IS_CONSTANT_INDEX` -- THE DISPATCH, `zend_variables.c:41`, and the reason this row's harm is a FREE and not a branch: the arm it selects releases a pointer read out of the SAME uninitialised slot. Present in both C rungs, unchanged: the upstream fix removes the CALL and not the callee. ⚠⚠ THE MASK IS PART OF THE PIN AND NOT DECORATION -- it is what doubles the freeing tag values from six to twelve, and `controls/tag_sweep.py` N8 is a must-fire mutant on a dispatch that omits it. A kernel whose teardown merely BRANCHED on the tag would have built a weaker row.",
        "rust": "NO RUST KEY, deliberately. The four Rust rungs represent the teardown's dispatch three different ways -- an `Option` discriminant, a `Some`/`None` return value, a `bool` witness -- and no single expression is common to them. What they share is that NONE of them dispatches on a byte it did not write, and a reviewer settles that with one grep. That is what the named-spelling standard says about the things no grep settles."
      },
      {
        "c": "`php_shim_efree(zvalue->value.str.val)` -- THE FREE, `zend_variables.c:45`'s `STR_FREE_REL`, guarded by `zvalue->value.str.val != ph52_empty_string`. Present in both C rungs. ⚠⚠ THE GUARD IS PINNED WITH IT AND IT IS WHY THE ROW HAS A BENIGN CORPUS AT ALL: `zend.h:469 STR_FREE(ptr)` is `if (ptr && ptr != empty_string) { efree(ptr); }`, so the three arms that write `empty_string` leave the slot PERMANENTLY SAFE to tear down -- which makes the faulting arm self-defusing on repetition and is what lets `inputs/gen.py` build a corpus in which `:243` runs and frees nothing. Deleting the test makes every repetition a double free, and that is `model.py::_mutants` M2.",
        "rust": "`al.free(p.req)` with `if p.req != 0` -- the same guard, with `req == 0` standing for `empty_string`. Present in all four Rust rungs, because all four have to reproduce the C's allocator SEQUENCE arithmetically (§B forbids them the shim) and the skipped `efree` is part of it."
      },
      "THE WINDOW LAYOUT is two u32 head words -- n_ops_w and fold_w -- then 4-byte op records of {u8 t1; u8 a1; u8 t2; u8 a2}, and the op count is bounded by the window LENGTH as (len - 8) / 4 and never trusted out of the blob. ONE OP IS ONE $x . $y: t % 5 selects the arm of zend_make_printable_zval's switch for that operand and a carries its payload -- the boolean for :200, the object handle for :250, and EG(exception) for :242. ⚠⚠ WHAT \"BENIGN\" MEANS ON THIS ROW IS A PROPERTY OF THE CALL HISTORY AND NOT OF ANY FIELD, and inputs/gen.py re-derives all of it from the bytes it just wrote and refuses to write otherwise (PROTOCOL_PHP.md A2a rule 1): R1 no window's op 0 carries the faulting arm on either side, because op 0's predecessor is another window's last op or -- on the program's first kernel call -- the C runtime's own startup residue; R2 no op presents the faulting arm while that side's slot is DANGLING, which is the double free and is inputs/adversarial-dblfree.bin's job; R3 every window's last op leaves BOTH sides SAFE, so the corpus is order-independent under the driver's k = (acc * nwin) >> 64. It also asserts the coverage: both arms of zend.c:242, all five arms on BOTH sides, both parities of a for arms 2 and 4, the handle's 1-, 2- and 3-digit cases, :243 reached, and :243 reached on a SAFE slot. ⭐ AND EVERY MEASURED WINDOW CARRIES EXACTLY cap OPS, so work_per_call is affine in the stride with NO per-window heterogeneity -- which is what ph53 had to declare for family B's sake and this row does not. ⚠ THIS ENTRY CONTAINS NO BACKTICK AT ALL, AND THAT IS CHECKED RATHER THAN ASSERTED: the first draft said \"no backticked spelling\" and carried a dozen, which is .memory-php/02-ladder.md's *a backtick IS a pin, including around a filename, a type name or a field name* and is the defect ph53's repair is paying for. NO BACKTICKED SPELLING: the C reads the window with one helper and the Rust rungs with another, which is one fact in two spellings.",
      "THE ALLOCATION ORDER IS O(n_ops) PER KERNEL CALL AND §B1a's PRECONDITION THEREFORE DOES NOT HOLD (PROTOCOL_PHP.md B1a.2). Per op: 0, 1 or 2 emallocs in the two zend_make_printable_zval calls (2 bytes for :202's estrndup(\"1\",1), 6 for :214's estrndup(\"Array\",5), 31 for :249's sizeof(\"Object id #\")-1 + MAX_LENGTH_OF_LONG), one emalloc(total+1) at :1181, then 0, 1 or 2 efrees at :1188/:1191 and one efree(total+1) when the executor releases the temporary -- so up to five allocations and three frees per op, and n_ops is (stride - 8) / 4. ▶ §B1a.3 BINDS: every CROSS-LANGUAGE figure this row publishes is labelled as including allocator work, and the row publishes no bare C-vs-Rust headline without that label. ⭐ THE SAME-LANGUAGE RATIOS ARE UNAFFECTED (§B1a.4): R2-vs-R3 and R4-vs-R5 allocate IDENTICALLY -- :243 never frees anything on the measured corpus, because the slot is empty_string or unconstructed and STR_FREE skips empty_string -- so the allocator term cancels exactly and R2-vs-R3 is the cleanest column the row has. ⚠ The four Rust rungs reproduce php_shim_tally() ARITHMETICALLY and the reproduction is NOT closed-form here: because the count is O(n_ops) the size-class cache (zend_alloc.c:150-168, :270-279) is EVOLVING, so each rung carries a counters-only simulation of it -- ph64's safe_naive.rs::Alloc is the precedent and this is the second row to need one. ⚠ THIS ENTRY CONTAINS NO BACKTICK AT ALL, AND THAT IS CHECKED RATHER THAN ASSERTED: the first draft said \"no backticked spelling\" and carried a dozen, which is .memory-php/02-ladder.md's *a backtick IS a pin, including around a filename, a type name or a field name* and is the defect ph53's repair is paying for. NO BACKTICKED SPELLING: it is a statement about a COUNT.",
      "R1h IS 7412202c43e7 AND IT IS A HAND RECONSTRUCTION, NOT A patch -p1 (PROTOCOL_PHP.md C, which requires the argument in writing). The commit -- Antony Dovgal, 2006-05-11, \"no need to destroy the zval here\", Zend/zend.c, 1 file, 1 hunk, 0 insertions, 1 deletion -- is committed at controls/7412202c43e7.patch, sha256 32e8526ebfe684d9..., 746 B. ⛔ IT CANNOT APPLY TO PRISTINE 5.0.0 AND HERE IS EVERY TOKEN THAT DIFFERS. The DELETED LINE is byte-identical: the patch removes \\t\\t\\t\\tzval_dtor(expr_copy);\\n (four tabs) and 5.0.0's :243 is \\t\\t\\t\\t\\tzval_dtor(expr_copy);\\n (five tabs), so the ONLY difference in the statement itself is one tab of indentation, because by 2006 the arm had lost a level of nesting. What does not match is the CONTEXT: the 2006 hunk's lines name STR_EMPTY_ALLOC() and E_RECOVERABLE_ERROR, and BOTH TOKENS ARE ABSENT FROM THE WHOLE 5.0.0 TARBALL -- measured, 0 occurrences across Zend/zend.h, zend_variables.h, zend_API.h, zend_operators.h and zend_errors.h -- while 5.0.0's own arm is if (EG(exception)) { ... expr_copy->value.str.val = empty_string; break; }. So patch has nothing to match and the reconstruction is the deletion of that one statement. ⭐ AND THE DELETION IS COMPLETE, WHICH IS WHAT MAKES THIS ROW DIFFERENT FROM ph53: zend.c:243 is the ONLY line in zend_make_printable_zval that reads expr_copy with no write to it earlier on the same path -- every other read (:210, :214, :250, :254, :259, :260) reads a field written one or two lines above, :253/:258 are whole-struct writes, :222 is inside the #if 0 at :220-228, and :263 sits AFTER the switch so every path that leaves the function has written the tag. ⚠ FIXSURVEY_001.md and the corpus column agree on this sha, so unlike ph53 there is no wrong commit to exclude; what there is instead is a fix dated 2006, i.e. IN NO 5.0.x RELEASE AT ALL, which is consistent with the patch not applying. ⭐⭐ controls/r1h_onelinedel.py IS THIS ARGUMENT AS A CHECK: it derives c/kernel_hardened.c from c/kernel.c, reports the code-line diff as 1 / 0, and carries an 11-case suite including a must-fire on a hardened kernel that added a GUARD instead of deleting the call -- which stage 7h would not have noticed. ⚠ THIS ENTRY CONTAINS NO BACKTICK AT ALL, AND THAT IS CHECKED RATHER THAN ASSERTED: the first draft said \"no backticked spelling\" and carried a dozen, which is .memory-php/02-ladder.md's *a backtick IS a pin, including around a filename, a type name or a field name* and is the defect ph53's repair is paying for. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about which COMMIT the hardened rung is and no single token decides it.",
      "R2-R5 IMPLEMENT R1h's ALGORITHM AND NOT R1's, and on this row that is POSSIBLE rather than forced -- which is itself the result. .memory-php/02-ladder.md: where the real upstream fix is INCOMPLETE, a safe-Rust rung built to it panics on the surviving inputs and a rung that panics is not a translation of the C. ph53's d09cdd9f71f3 is that case. ph52's 7412202c43e7 is NOT: it deletes the only unconstructed read in the function, so R1h is memory-safe and the four Rust rungs ARE ports of it. ⭐ R3 goes further and makes the deletion STRUCTURAL -- make_printable_zval returns the printable, so the deleted line cannot be written. On the MEASURED corpus all six rungs agree bit for bit, which is what check.py stage 2 checks; on inputs/adversarial-dblfree.bin R1 alone diverges and stage 4 records it. ⚠ THIS ENTRY CONTAINS NO BACKTICK AT ALL, AND THAT IS CHECKED RATHER THAN ASSERTED: the first draft said \"no backticked spelling\" and carried a dozen, which is .memory-php/02-ladder.md's *a backtick IS a pin, including around a filename, a type name or a field name* and is the defect ph53's repair is paying for. NO BACKTICKED SPELLING: it is a statement about algorithms."
    ],
    "forbidden": [
      {
        "c": "`= {0}` -- zero-initialising the slot at its declaration. It removes the defect without being `7412202c43e7` and it is the first thing a reader reaches for; `CATALOGUE.md`'s own trap for this row is *an extraction that zero-initialises the slot for tidiness deletes it*. ⚠⚠ AND THE TRAP APPLIES TO THE COMPILER AND NOT ONLY TO THE AUTHOR, WHICH THE CATALOGUE DOES NOT SAY: `-ftrivial-auto-var-init=zero` and `=pattern` delete it in all 16 cells `controls/d0_stack.py` measures, and they CHANGE THE ANSWER. Neither flag is in `harness/build.py::c_flags`, checked by that control's N5 rather than assumed. ONLY THE ONE TOKEN IS BACKTICKED and every other name in this entry is deliberately plain, because a forbidden entry's backticks are matched against EVERY rung of the language and an incidental one refuses a rung for carrying its own correct code.",
        "rust": "`MaybeUninit::zeroed` -- forging a value for the state the C actually has. It would make an unconstructed slot INDISTINGUISHABLE from one holding `empty_string`, so it changes the answer while silencing every detector this row has, and it would make the witness unnecessary for the wrong reason. The Option-valued slot safe_naive.rs writes is the opposite move and is NOT forbidden: it makes the unconstructed slot representable rather than forging a value for it. Absent from all five Rust sources, checked by grep before this entry was written. ⚠⚠ ONLY `MaybeUninit::zeroed` IS BACKTICKED HERE AND EVERY OTHER NAME IN THIS ENTRY IS DELIBERATELY PLAIN -- the Option type name was backticked in the first draft and `forbidden_hits` FAILED the gate on safe_naive.rs and safe_tuned.rs, which is `.memory-php/02-ladder.md`'s *a backtick in a forbidden entry IS a pin, including around a type name* firing on a row that had not run `idiom_audit` on the draft. NOTES.md 11h."
      },
      "`set_len` and `spare_capacity_mut` -- the shape a reader reaches for when a row says MaybeUninit, and forbidden for a reason outside the row: the pinned vstd specifies NEITHER (std_specs/vec.rs has neither name). ⚠ This row does not need them, because its slots are two named locals rather than a Vec -- so unlike ph53 the ban is VACUOUS here and it is written down anyway, because a reader who has seen ph53 will look for it. Both tokens are absent from all five Rust sources, checked by grep. ⚠ ONLY THE TWO FORBIDDEN TOKENS ARE BACKTICKED; the container's type name is deliberately plain, because backticking it refuses verus.rs for carrying its own correct Vec<u8> argument -- measured, on this row's second gate run.",
      "A TEST OF THE SLOT'S TAG, A NULL TEST OR ANY OTHER GUARD INSIDE EITHER C KERNEL'S `:243` ARM. Upstream added none -- it deleted the call -- and a C rung that added one would be measuring a hardening nobody shipped while claiming to be 5.0.0 or the 2006 fix. `controls/r1h_onelinedel.py` N3 is the must-fire on exactly that. NO BACKTICKED SPELLING IN THIS ENTRY, AND IT IS FORCED RATHER THAN CHOSEN: check.py's spelling matcher decides one spelling against EVERY rung of a language, and the four Rust rungs legitimately DO carry such a guard -- an Option match, a Some binding, a one-bit witness -- so any token that named the C's absence would refuse all four. The SCOPE lives in this English and a reviewer settles it with one grep. ⚠⚠ AND THE THREE RUST SPELLINGS THIS ENTRY NAMES ARE DELIBERATELY PLAIN FOR EXACTLY THE REASON THE ENTRY GIVES: backticked, they refused four rungs for carrying their own correct code -- measured, six `forbidden_hits` on this row's second gate run, which is what `.memory-php/02-ladder.md` means by *run `idiom_audit` on any draft*. NOTES.md 11h."
    ],
    "why": "ph52 is PHP 5.0.0's string-concatenation operator, corpus row LOGIC-007, tier `narrowed`. THE IDIOM IS A CALLER-OWNED STACK SLOT THAT A CALLEE DESTRUCTS ON AN EARLY EXIT BEFORE ANY PATH HAS CONSTRUCTED IT. `Zend/zend_operators.c:1148` is `zval op1_copy, op2_copy;` -- bare locals, no `= {0}`, no `INIT_ZVAL`, no `memset` -- and `:1152`/`:1153` pass their addresses to `zend_make_printable_zval`, which writes `expr_copy->value.str.*` on every arm and `expr_copy->type` EXACTLY ONCE, at `zend.c:263`, AFTER the switch. The arm at `:242-247` is `if (EG(exception)) { zval_dtor(expr_copy); expr_copy->value.str.len = 0; expr_copy->value.str.val = empty_string; break; }` -- a TAG-DISPATCHED TEARDOWN OVER A TAG BYTE NOBODY HAS WRITTEN. `Zend/zend_variables.c:36-80` `_zval_dtor` switches on `zvalue->type & ~IS_CONSTANT_INDEX` and RELEASES A POINTER READ OUT OF THE SAME UNINITIALISED SLOT, so the harm is a FREE and not a branch. ⚠ ON THE COMMON PATH (`:190-193`, `expr` already a string) `expr_copy` IS NEVER WRITTEN AT ALL, so the function's own convention is *constructed only if `*use_copy`* -- and this arm destructs it regardless. ⭐⭐⭐ AND THE UNINITIALISED MEMORY IS ON THE **STACK**, WHICH IS WHY DELIVERABLE #0 OF THIS ROW WAS A DETERMINISM QUESTION AND NOT A RUNG. Every mechanism this tree has for uninitialised memory is an ALLOCATOR shim, so before any rung existed the row had to settle whether `:243` reads anything reproducible. `controls/d0_stack.py` is that measurement, COMMITTED rather than left in `.temp/`, over 16 cells -- {gcc, clang} x {-O0, -O3} x {isolated, whole} x {callee noinline, callee inlinable}. THREE RESULTS, and two of them changed the row: (i) THE STACK OFFSET IS REUSED EXACTLY in all 16, at both opt levels, in both modes, on both compilers -- so op k+1's `op1_copy` sits where op k's did and the trigger is a CALL HISTORY; (ii) WITHOUT a `noinline` on the lifted callees, 2 OF THE 16 CELLS ANSWER DIFFERENTLY -- `gcc -O3 isolated` and `clang -O3 whole` -- because a compiler that can see the unwritten tag may treat it as `undef` and fold the teardown away, and `gcc`'s choice is exactly the answer a ZERO-INITIALISED slot would give; (iii) the harness's own `isolated`/`whole` axis MOVES NOTHING, because `harness/build.py` compiles three TUs for the whole row where upstream has `zend_operators.c`, `zend.c` and `zend_variables.c` as three SEPARATE ones and links without LTO. ▶ So `c/kernel.h` defines `PH52_NOINLINE` and it is a declared `substitution` with a 16-cell differential behind it, not a style choice. ⭐⭐ THE TRIGGER, STATED AS THE THREE SLOT STATES THE C HAS: UNCONSTRUCTED (the stack byte), `IS_STRING` + `empty_string` (from `:195-197`, `:204-205` or `:244-245` -- and `zend.h:469 STR_FREE` SKIPS `empty_string`, so a teardown here is DEFINED and costs no allocator call, which makes the faulting arm SELF-DEFUSING on repetition), and `IS_STRING` + a pointer `:1188` HAS ALREADY FREED (from `:202`, `:214` or `:249`). ⛔ The third state is the defect and `:243` on it is a DOUBLE FREE. ⚠⚠ THE MANAGER'S REGISTERED FALLBACK (a) -- *iteration 2 frees the previous iteration's already-freed pointer* -- IS REFUTED AS STATED and upheld once corrected: a REPEATED faulting arm does not fire, because `:244-245` writes `empty_string` into the slot it just tore down. The adversarial history needs TWO DIFFERENT ARMS, a converting one then the faulting one, which is what `inputs/adversarial-dblfree.bin` carries and what two different `.` operations in a PHP script do. ⚠⚠⚠ AND THE CORPUS'S `uninit-read-silent` IS EXPLAINED AND NOT EXCUSED. `controls/tag_sweep.py` drives the whole byte through `_zval_dtor` and measures 12 OF 256 VALUES (4.688 %) TEARING ANYTHING DOWN AT ALL and only 8 OF 256 (3.125 %) REACHING `efree`, i.e. 95.3 % OF BYTE VALUES MAKE `:243` A NO-OP. ⚠ `RECAP_PHP.md` F102's UNTESTED *\"five named cases out of a byte\"* is wrong in three ways and the control's `--selftest` fires on each: it is SIX named cases (`IS_RESOURCE`, `zend_variables.c:64-71`, is missing from the list), TWELVE byte values once the mask is applied, and `_zval_dtor` DOES have `case IS_NULL` at `:75` -- the conclusion that a zero tag no-ops holds, the reason F102 gives for it does not. ⛔⛔⛔ AND THE SANITIZER FIRES ON THE **BENIGN** INPUTS AND IS SILENT ON THE ADVERSARIAL ONE, WHICH IS THE ROW'S MOST SURPRISING MEASUREMENT AND IS AN ARTEFACT OF THE DETECTOR. `model.py::sanitizer_expect` declares `fires` on small.bin and large.bin and `clean` on all four adversarial blobs, measured under check.py's own `gcc -O1 -fsanitize=address,undefined -static-libasan` line: R1 gives `heap-use-after-free` on both measured inputs and R1h is clean on all six. THE MECHANISM, TRACED: the two slots are STACK locals and the row's benignness is a property of the stack being REUSED AT THE SAME OFFSET, which inputs/gen.py's three call-history rules exploit -- and ASan's fake stack (`detect_stack_use_after_return`, default 1 here) breaks that in BOTH directions. It usually hands out a freshly ZEROED frame, so `:243` reads `type = 0 = IS_NULL` and no-ops -- 282 of the 283 `:243`-reaching calls on small.bin -- and 1 in 283 it hands back a RECYCLED frame carrying an older call's bytes, naming a block `php_shim_reset()` has since freed. ▶ ASan CREATES the fault on an input the real stack keeps clean, and on the REAL stack every one of the 25,000 iterations' `:243` calls reads `IS_STRING + empty_string` and frees nothing -- which is what the published u64 rests on. ⛔ DO NOT READ `fires` AS \"the benign corpus exercises the defect\": it does not, on the binaries every number here was taken with. ⭐⭐ AND THE ADVERSARIAL BLOB IS SILENT FOR TWO FURTHER INDEPENDENT REASONS: `n_iters = 1` and two ops is too few for the fake stack to recycle, so the defect does not happen under ASan at all; and even when it does, `php_shim_efree` of a block under 88 bytes never reaches `free()` (`zend_alloc.c:270-279`), so there is no double free to intercept -- PROTOCOL_PHP.md §B1.1's measured fact on a third row. ⚠ THE MANAGER'S §2.6 -- *expect ASan to fire on the double free where the corpus says silent* -- IS THEREFORE REFUTED THREE WAYS: ASan never reports the double free on any input, what it reports is a use-after-free IT CAUSED ITSELF on the benign inputs, and the third mechanism (frame recycling) has nothing to do with the allocator. ⭐ This is F102's `0xbe` correction -- a detector-dependent observation must not be recorded as a row property -- with the SIGN REVERSED: the detector does not reveal the defect, it manufactures one. NOTES.md §7. ⭐⭐⭐ WHAT THE ROW PUBLISHES THAT `ph53` STRUCTURALLY COULD NOT: THE DEFECT IS IN THE u64. `php_shim_tally()` is folded into the kernel's return (§B1.2), and `:243`'s teardown is observable ONLY through the allocator -- so on `inputs/adversarial-dblfree.bin` R1 prints 272040826665440682 and R1h prints 272040826666539789, in all four C cells, and `inputs/adversarial-safe.bin` -- the SAME op shape with one op byte changed so `:243` runs on a SAFE slot -- gives 254123829775225275 on all six rungs. One byte apart, and one of the pair moves. ph53's `idiom.why` records that *\"the published u64 carries no evidence whatever that the defect exists\"*; this row's does. ⚠ `n_iters` IS 1 ON BOTH ADVERSARIAL BLOBS AND IT IS LOAD-BEARING: the second `efree` pushes the SAME header into `cache[1]` twice, so nothing reaches `free()` during the call and the NEXT call's `php_shim_reset()` (`emalloc_shim.h:267-269`) frees that header twice -- glibc aborts with `double free detected in tcache 2`, exit 134. At `n_iters = 1` there is no next call and the defect lands in the number instead of in a signal. The escalation is measured in `controls/d0_stack.py` at `n_iters = 64` -- see NOTES.md §5b. ⚠⚠ THE TIER IS `narrowed` AND `CATALOGUE.md:146` ALSO SAYS `narrowed`, so this row AGREES with the catalogue where `ph53` did not -- which is the third data point on `RECAP_PHP.md` open item 75 and it goes the OTHER WAY from the first two. The defect span lifts nearly verbatim; what forces `narrowed` is that three of the switch's eight arms are not lifted (`:207-212` needs `zend_list`, `:253-256` needs `zend_locale_sprintf_double`, `:258-261` needs `convert_to_string`'s `smart_str`), the `cast_object`/`get` handler dispatch at `:229-241` is a projection onto one attacker byte, and `:1182-1184`'s stores are replaced by a content digest. A tier is a COST STATEMENT AND NEVER A FILTER. ⭐⭐ THE LADDER, AND IT IS FOUR ANSWERS TO ONE QUESTION -- *has this slot been constructed?* R1h answers it by DELETING THE QUESTION: `7412202c43e7` removes the one line that asks, and because `zend.c:263` writes the tag after the switch the deletion is COMPLETE -- unlike `ph53`, whose upstream fix left the fault standing. R2 answers it with `Option<Pr>` and `slot.take()`, which makes the FOURTH state -- a slot naming memory `:1188` has freed -- UNREPRESENTABLE: the C has four slot states and safe Rust has three. ⚠ That is NOT `Option` reinventing the upstream fix: `7412202c43e7` deletes the teardown and keeps the states, `Option` keeps the teardown and deletes the state. R3 IS A PORT OF R1h, which is unusual and is the point -- `make_printable_zval` RETURNS the printable instead of writing through a `&mut`, so on the early-exit path there is no slot in scope and the deleted line is not merely absent but UNWRITEABLE. R4/R5 answer it with ONE BIT PER SLOT, `constructed: bool`, two of them for the whole kernel. ⭐⭐⭐ AND THAT ONE BIT IS WHAT MAKES `ph53`'s F98 FALSIFIABLE RATHER THAN SAFE. ph53's witness is `[bool; MAXD]` -- one byte per slot, re-read on every consumer iteration -- and F98 priced the shipped R4/R5's extra work at `+21.775 %` in W1 on `small.bin` at `O3/isolated` AGAINST `controls/r4_nowitness.rs`, a RUST control and not the C, with only ~44 % of that attributable to the witness. ph52's is two `bool`s, tested twice per op and NEVER INDEXED, and `NOTES.md` §11 reports what it costs. ⚠⚠ AND THE R4 SIDE CARRIES A SECOND RESULT ph53 DOES NOT HAVE: `controls/r4_nowitness.rs` -- the faithful port, `:243` with no test -- REPRODUCES THE DEFECT BIT FOR BIT. It prints 272040826665440682 on `adversarial-dblfree.bin`, which is R1's answer and not R1h's, because the `MaybeUninit<Pr>` retains the previous op's value exactly as the stack slot does. ph53's witness-free control answered CORRECTLY where its R1 faulted; this one does not. And Verus REFUSES it -- `controls/negatives.py --verus` mutant V1 deletes the `if *constructed` and gets `precondition not satisfied` at `std_specs/maybe_uninit.rs` -- so F97/F98's *a rung that reproduces the defect cannot be verified and a rung that verifies does not reproduce it* RECURS, on a second row, with the reproduction now bit-exact. ⚠⚠⚠ AND §B1a's PRECONDITION FAILS HERE: the kernel makes up to five `emalloc`s and three `efree`s PER OP, i.e. O(n_ops) per kernel call, so the size-class cache is EVOLVING and every rung carries a counters-only simulation of it (`ph64`'s precedent). ▶ §B1a.3 binds: the allocation order is declared in `idiom.required`'s last entry and EVERY CROSS-LANGUAGE FIGURE THIS ROW PUBLISHES IS LABELLED AS INCLUDING ALLOCATOR WORK. ⭐ The SAME-LANGUAGE ratios are unaffected (§B1a.4): R2-vs-R3 and R4-vs-R5 allocate identically and the term cancels exactly, so `ph53` is the O(1) exception and this row is not it. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "concat_fold": "concat_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 33
    },
    "twin_obligations": {
      "verus.rs": 34
    },
    "obligations_note": "33 verified / 0 errors, and 34 under `--cfg slb_twin` -- FOUR trusted items and ONE twin, because exactly one of the two items with a contract can have one. ⚠⚠ AND THE ROW LEARNED THAT FROM ITS OWN FIRST GATE RUN: with `slot_read_unchecked` as the only contract-bearing trusted item, stage 5c-twin FAILED with *every trusted item in this pattern is excused ... so stage 5c-twin checked the strength of NOTHING*, which is `check.py`'s `n_twins == 0` rule and has no hatch. ⭐ The repair was NOT to invent something for the stage to check: `win_get_unchecked` is a FIDELITY REPAIR the row owed anyway, because every window read in the C is an unchecked array access and a safe-indexed R4 pays a bounds check the C does not. NOTES.md 11f is the finding. ⭐⭐ WHAT IS PROVED IS THE OBLIGATION THE ROW IS ABOUT, IN THE SPELLING THE PINNED vstd ALREADY HAS: `zval_dtor`'s `requires` is `*old(constructed) ==> slot.mem_contents().is_init() && slot.mem_contents().value().req == sl.req`, and its first conjunct is literally `MaybeUninit::assume_init_ref`'s own `requires` (std_specs/maybe_uninit.rs:45-49). ⛔⛔ AND THE ROW CANNOT USE THAT FOR FREE, WHICH IS F97 RECURRING ON A SECOND ROW: check.py::_scan_unsafe_sites requires EVERY `unsafe` token in a pinned Verus source to sit inside an `external_body` body, with no justification hatch, and 5c-twin requires every trusted item to have a VERIFIED twin -- which for a MaybeUninit read would itself need `unsafe`, because there is NO safe exec route from MaybeUninit<T> to T. Two sound rules, jointly unsatisfiable for this operation, a second time. ⭐ WHAT IS NARROWER HERE THAN ON ph53: ONE trusted item against four, because ph52's slots are two named locals and not an array -- there is no unchecked INDEXING to fold in, so the wrapper carries ONE conjunct where ph53's carries two. `controls/mu_unwrapped.rs` verifies the unwrapped shape at 6/0 with NO trusted item at all -- vstd's own assume_specification carrying the obligation -- and `controls/negatives.py --verus` RUNS it as must-NOT-fire arm N2, so the fact about Verus stands, is committed rather than cited, and is re-checked on every invocation. ⚠⚠ THE SPEC-LEVEL SLOT IS NOT A MaybeUninit AND CANNOT BE: `mem_contents` is `uninterp`, so a spec function cannot construct one. `Sl { c: bool, req: usize }` is the abstraction -- ONE bool and ONE usize per slot, two slots -- where ph53 needed a whole `Seq<Option<u32>>` and an `abst()` over it. That is the same O(slots) story the runtime witness tells, one level up. ⚠ THE PROOF-BUDGET OVERRIDES ARE DISCLOSED WITH THEIR REASONS: `#[verifier::rlimit(120)]` on `kernel` and `#[verifier::rlimit(60)]` on `lemma_run_step`, and `#[verifier::opaque]` on `s_print` and `s_concat`. The opacity is not taste: left transparent, the solver unfolds both under `s_run`'s own recursion and `lemma_run_step` blows the rlimit -- measured, on the first complete draft of the file -- and they are revealed exactly where they are proved and nowhere else. ⚠⚠ ONE THING MEASURED THE HARD WAY AND WORTH THE NEXT AGENT'S TIME: `s_run` recurses on the FRONT of its range while the loop invariant needs the op at the BACK, so the fold's own step law is NOT free. `lemma_run_step` is one induction on `o - a` and it is the only lemma this rung has; the first version fixed the start index at 0 and could not be stated inductively at all.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 33 shipped and 34 under the flag: ONE twin, `slb_twin_win_get_unchecked`, whose body is `v[i]` with the IDENTICAL contract -- so the window accessor's `requires` and `ensures` are CHECKED against a safe implementation rather than asserted. ⛔⛔ `slot_read_unchecked` HAS NO TWIN AND CANNOT HAVE ONE, and the reason is a COLLISION BETWEEN TWO SOUND GATE RULES rather than a concession: `_scan_unsafe_sites` requires every `unsafe` token in this file to sit inside an `external_body` body, and there is NO safe exec route from MaybeUninit<T> to T -- `assume_init`, `assume_init_ref` and `assume_init_mut` are the only ones and all three are unsafe -- so any twin's body would carry an `unsafe` token outside a trusted body and would be REFUSED by the first rule. `load_input` and `emit` have no twin either and cannot: one reads a file and the other prints, and neither is a function of its arguments. ⚠ ONE OF FOUR TRUSTED ITEMS IS TWINNED, which is what the stage measures, and the `ok` line does not fire when anything is justified away -- that is check.py's own design. ⭐⭐ AND THE ROW FOUND A GATE PROPERTY WORTH REPORTING ON THE WAY HERE: `check.py`'s `n_twins == 0` rule (`:7420-7431`) hard-fails a pattern whose ONLY contract-bearing trusted item is genuinely untwinnable -- which is the same objection TASK_007 accepted when it DELETED `MAX_TWIN_JUSTIFICATIONS` (*\"the only knob in the twin regime that could hard-fail an HONEST pattern with no route out\"*), one item down. ph52 is the first row in either programme to reach it. NOTES.md 11f.",
    "items": {
      "verus.rs": {
        "real_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "idx_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rd32s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mix": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mix131": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_alloc_a": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_free_a": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tally_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_dtor": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "obj_dig": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "obj_nd": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_print": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_concat": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_op": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "arm_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "aux_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "arm2_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "aux2_at": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "st_init": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cap_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "n_ops_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "concat_win": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "concat_fold": {
          "external": null,
          "requires": [],
          "ensures": []
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
        "a": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "new": {
          "external": null,
          "requires": [],
          "ensures": [
            "r.a() == st_init(Seq::empty()).al",
            "r.cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "alloc": {
          "external": null,
          "requires": [
            "size <= 64",
            "old(self).cnt@.len() == MAX_CACHED_MEMORY as int"
          ],
          "ensures": [
            "final(self).a() == s_alloc_a(old(self).a(), size)",
            "final(self).cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "free": {
          "external": null,
          "requires": [
            "size <= 64",
            "old(self).cnt@.len() == MAX_CACHED_MEMORY as int"
          ],
          "ensures": [
            "final(self).a() == s_free_a(old(self).a(), size)",
            "final(self).cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "tally": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == tally_of(self.a())"
          ]
        },
        "win_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_win_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "rd32": {
          "external": null,
          "requires": [
            "o + 4 <= w@.len()"
          ],
          "ensures": [
            "r == rd32s(w@, o as int)"
          ]
        },
        "slot_read_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "m.mem_contents().is_init()"
          ],
          "ensures": [
            "r == m.mem_contents().value()"
          ]
        },
        "zval_dtor": {
          "external": null,
          "requires": [
            "sl.c == *old(constructed)",
            "*old(constructed) ==> slot.mem_contents().is_init() && slot.mem_contents().value().req == sl.req",
            "sl.req <= 64",
            "old(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ],
          "ensures": [
            "final(al).a() == s_dtor(old(al).a(), sl).0",
            "*final(constructed) == s_dtor(old(al).a(), sl).1.c",
            "final(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "make_printable_zval": {
          "external": null,
          "requires": [
            "arm < NARM",
            "aux <= 255",
            "sl.c == *old(constructed)",
            "*old(constructed) ==> old(expr_copy).mem_contents().is_init() && old(expr_copy).mem_contents().value().req == sl.req",
            "sl.req <= 64",
            "old(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ],
          "ensures": [
            "({ let s = s_print(old(al).a(), sl, arm, aux); &&& final(al).a() == s.0 &&& *final(constructed) == s.1.c &&& (s.1.c ==> final(expr_copy).mem_contents().is_init() && final(expr_copy).mem_contents().value().req == s.1.req) &&& r.0 == s.2 &&& r.1 == s.3 &&& r.2 == s.4 &&& s.1.req <= 64 &&& s.3 <= 14 })",
            "final(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "concat_function": {
          "external": null,
          "requires": [
            "a1 < NARM",
            "a2 < NARM",
            "x1 <= 255",
            "x2 <= 255",
            "st.al == old(al).a()",
            "st.s1.c == *old(c1)",
            "st.s2.c == *old(c2)",
            "*old(c1) ==> old(op1_copy).mem_contents().is_init() && old(op1_copy).mem_contents().value().req == st.s1.req",
            "*old(c2) ==> old(op2_copy).mem_contents().is_init() && old(op2_copy).mem_contents().value().req == st.s2.req",
            "st.s1.req <= 64",
            "st.s2.req <= 64",
            "old(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ],
          "ensures": [
            "({ let c = s_concat(st, a1, x1, a2, x2); let n = c.0; &&& final(al).a() == n.al &&& *final(c1) == n.s1.c &&& *final(c2) == n.s2.c &&& (n.s1.c ==> final(op1_copy).mem_contents().is_init() && final(op1_copy).mem_contents().value().req == n.s1.req) &&& (n.s2.c ==> final(op2_copy).mem_contents().is_init() && final(op2_copy).mem_contents().value().req == n.s2.req) &&& n.s1.req <= 64 &&& n.s2.req <= 64 &&& n.acc == mix(mix(mix(st.acc, r.0 as u64), r.1), r.2) &&& r.0 == c.1 &&& r.0 <= 28 })",
            "final(al).cnt@.len() == MAX_CACHED_MEMORY as int"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "8 <= len"
          ],
          "ensures": [
            "r == concat_fold(buf@, off as int, len as int)"
          ]
        },
        "lemma_run_step": {
          "external": null,
          "requires": [
            "a <= o"
          ],
          "ensures": [
            "s_run(st, win, a, o + 1) == s_op( s_run(st, win, a, o), arm_at(win, o), aux_at(win, o), arm2_at(win, o), aux2_at(win, o), )"
          ]
        },
        "main": {
          "external": null,
          "requires": [],
          "ensures": []
        }
      }
    },
    "twin_justifications": {
      "verus.rs": {
        "slot_read_unchecked": "⛔⛔ NO TWIN, AND IT IS NOT POSSIBLE RATHER THAN NOT CONVENIENT. A twin has to be a VERIFIED exec function meeting the same contract, and this contract's `ensures` is `r == m.mem_contents().value()` -- so the body must get a `Pr` OUT of a `MaybeUninit<Pr>`. The pinned vstd offers exactly three routes -- `assume_init`, `assume_init_ref` and `assume_init_mut` -- and ALL THREE ARE `unsafe fn`. There is no safe exec expression from MaybeUninit<T> to T; that is what the type MEANS. So any twin's body would contain an `unsafe` token outside a trusted item's body, which `harness/check.py::_scan_unsafe_sites` refuses with no justification hatch. ▶ TWO SOUND RULES, JOINTLY UNSATISFIABLE FOR THIS ONE OPERATION, and the row reports the collision (NOTES.md 11) rather than working around it quietly -- ph53 found it first (F97) and this is its second instance, on a row with ONE trusted item instead of four. ⚠ WHAT IS THEREFORE UNCHECKED, STATED PLAINLY: that this item's `requires` is STRONG ENOUGH to license a checked implementation. What IS checked is that it is not VACUOUS (both its parameter's ghost state and the caller's witness are constrained), that deleting the caller's guard breaks the proof (`controls/negatives.py --verus` V1 deletes `if *constructed` and Verus refuses at std_specs/maybe_uninit.rs with `precondition not satisfied`; V2 deletes the conjunct that supplies it; V3 deletes the witness-agreement conjunct), and that Miri is silent on the shipped rung and LOUD on the witness-free control. ⭐ AND ONE MORE THING IS CHECKED THAT NO TWIN COULD CHECK: `controls/mu_unwrapped.rs` verifies the UNWRAPPED shape -- vstd's own `assume_init_ref` spec carrying the same obligation in ordinary exec code, with NO trusted item at all, 6 verified / 0 errors -- so the contract asserted here is demonstrably the one vstd asserts, which is a stronger statement than a hand-written twin would have made. ⚠ IT IS A COMMITTED FILE AND NOT A `.temp/` PROBE, deliberately: PROTOCOL_PHP.md F6 and .memory-php/04-process.md law 13, and this citation is inside the HASHED block.",
        "load_input": "NO TWIN AND THERE CANNOT BE ONE. It opens a file, reads it and allocates; it is not a function of its arguments, it has no `ensures` to check, and a safe implementation would be the same code. Every pattern in both programmes carries this item and none has a twin.",
        "emit": "NO TWIN AND THERE CANNOT BE ONE. `println!` is not verifiable and the item has no `ensures`, so there is nothing for a twin to be checked against."
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "win_get_unchecked": "`*v.get_unchecked(i)` is defined only while `i < v.len()`, and the pinned vstd ships NO spec for it -- grepped `~/tools/verus/vstd/` entire, 0 files mention `get_unchecked` at all, while `assume_init_ref` appears in `std_specs/maybe_uninit.rs`. So the wrapper is the trusted boundary and `i < v@.len()` is the whole of what makes it sound. The `ensures` is the value, which is what makes it useful; both are trusted, and the twin `slb_twin_win_get_unchecked` checks the pair against `v[i]`. ⚠⚠ WHY R4/R5 HAVE THIS AND R2/R3 DO NOT, AND IT IS A FIDELITY REPAIR RATHER THAN AN OPTIMISATION: every window read in the C -- `win[p]` and `ph52_rd32`'s four bytes -- is an UNCHECKED array access, because C has no bounds check and nothing in `concat_function` or `zend_make_printable_zval` verifies that the op record is inside the window. The kernel's structural precondition is what makes it sound and it is discharged AT THE CALL SITE in `main`. ▶ A safe-indexed R4 would pay a bounds check the C does not, which is exactly the R2/R3-vs-R4/R5 distinction this ladder exists to price. `ph53`'s `win_get_unchecked` is the precedent, character for character.",
        "slot_read_unchecked": "`*m.assume_init_ref()` -- ONE unchecked operation, and the `requires` has one conjunct for it: `m.mem_contents().is_init()`, which is EXACTLY what the pinned vstd's own `assume_specification` demands (std_specs/maybe_uninit.rs:45-49). ⛔⛔ IT IS RE-ASSERTED BY HAND HERE AND THAT IS A LOSS THE ROW REPORTS RATHER THAN HIDES: in ordinary exec code `unsafe { m.assume_init_ref() }` needs NO trusted item, because vstd's assume_specification carries the obligation -- verified at 6/0 in the COMMITTED control `controls/mu_unwrapped.rs`. But `check.py::_scan_unsafe_sites` requires every `unsafe` token in this file to sit inside an `external_body` body and 5c-twin then demands a twin that cannot exist, so the obligation vstd owns becomes one this contract asserts. ⭐ THE TCB COUNT IS UNCHANGED BY THE WRAPPING -- one item either way -- and that control is what keeps the asserted contract checkable against vstd's. ⭐⭐ AND THERE IS NO SECOND CONJUNCT, WHICH IS THE DIFFERENCE FROM ph53: ph53's equivalent item folds `get_unchecked` in and needs `i < v@.len()` as well, because its slots are an array. ph52's are two NAMED LOCALS, so there is no index and no range obligation -- the `Pr` returned is a pure value every inhabitant of which is legal. NOTES.md 11.",
        "load_input": "⚠ NO `requires`, and the gate asks for this line because a trusted item without one is an axiom that its operation is always defined. Here the operation is `open`/`read`/`parse` on a path from `argv`: it is not a function of its arguments in any sense a `requires` could constrain, and every failure mode it has (missing file, short payload) is handled inside `common/driver.rs` with an `exit`. What it returns is unconstrained, which is why the kernel's own `requires` is discharged in `main` from the driver loop's arithmetic and not from this item.",
        "emit": "⚠ NO `requires` and NO `ensures`. `println!` is not verifiable and the item exists so that the kernel's result is CONSUMED -- `.memory/02-bench-rules.md`'s \"is the result actually consumed and printed?\". Nothing downstream of it is proved and nothing needs to be."
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
      "if stride_w >= 8 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph52's two probe shapes have different work per call (74 and 181 window bytes, i.e. 16 and 43 op slots) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⭐ AND THE PER-WINDOW WORK IS UNIFORM ON THIS ROW, WHICH IS A PROPERTY OF THE CORPUS AND NOT OF THE STATISTIC: `inputs/gen.py` fills EVERY measured window to exactly `cap = (stride - 8) / 4` ops and `_check_history` refuses to write otherwise, so `n_ops` is an exact affine function of the stride and the work really does scale with the denominator rather than merely being labelled by it. ph53 had one window in sixteen with `n_decl == 0` and had to declare the heterogeneity for family B's sake (RECAP_PHP.md F88); this row has none. ⚠⚠ THERE IS STILL A PER-CALL FIXED TERM -- the two head words, `php_shim_reset()`'s sweep over eleven cache classes, and the tally fold -- so the marginal is NOT a pure op rate and NOTES.md 8 decomposes it. ⚠ AND THE PER-OP WORK IS NOT UNIFORM ACROSS OPS, which is declared rather than elided: the five arms cost different amounts (the pass-through arm allocates nothing, `:249` allocates 31 bytes and runs the digit case analysis) and BOTH arms of the defect's own branch at `zend.c:242` have to be in the measured corpus (PROTOCOL_PHP.md A2a rule 1). Every B1 figure this row publishes is labelled as one draw and marked PROVISIONAL pending open item 62 (family C)."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "norel",
      "why": "⭐⭐ R4 AND R5 ARE THE SAME MACHINE CODE AT `-O3` AND NO OTHER php ROW REPORTS THAT. Measured, `isolated`, same rustc flags as build.py's, with padding removed: at `-O3` both kernels are **433 instructions / 425 non-pad / 1685 bytes** and `asm.identity_level` returns **`norel`**, which `check.py::check_miri` is explicit counts as byte-identical -- the only bytes that differ are pc-relative displacement FIELDS, i.e. call targets that moved because the crate is named `verus` instead of `unsafe`. ⚠ At `-O0` they DIFFER: 773 instructions against 770. ⭐ THE THREE-INSTRUCTION GAP IS THE INTERESTING HALF and it is the same direction ph45, ph64 and ph53 all reported (F82) -- THE PROVED RUNG IS THE SHORTER ONE -- and at `-O0` rustc does not constant-fold, so the difference is that R5's module is larger and its register allocation lands differently, not that the proof is in the binary. Every `let ghost`, `assert`, `proof {}`, `requires` and `ensures` erases before codegen; `verus!`, the 26 spec items and the one lemma contribute NOTHING to the text. ⚠⚠ DO NOT READ THE 3 INSTRUCTIONS AS A COST OF PROOF IN EITHER DIRECTION -- the row states the difference rather than attributing it. ⭐ AND WHY ph53 DIFFERS AT BOTH LEVELS WHERE THIS ROW DOES NOT, stated because two rows is where a pattern starts: ph53's verus.rs carries 14 spec functions over `Seq`s, four trusted items and three twins, so rustc sees a much larger module; ph52's proof is one lemma and two opaque transitions over scalar state. THE PIN IS WHAT WAS MEASURED and the explanation is a reading. ⚠ The figures moved once, when `win_get_unchecked` landed (NOTES.md 11g): before it, `-O3` was 467/467/1952 and `norel` too, so the LEVEL did not move and the counts did. NOTES.md 10a and 11c."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph52 has ONE such item and it READS a `MaybeUninit` whose initialisedness is the defect. ⭐⭐ AND IT MATTERS MORE HERE THAN THE RULE ANTICIPATES, FOR TWO MEASURED REASONS THAT ARE THIS ROW'S SUBJECT. First, ASAN IS NOT MEASURING WHAT IT LOOKS LIKE IT IS MEASURING ON THIS ROW: `model.py::sanitizer_expect` is `fires` on the two BENIGN inputs and `clean` on all four adversarial ones, because ASan's fake stack (`detect_stack_use_after_return` defaults to 1) hands out a freshly zeroed frame on 282 of 283 `:243`-reaching calls and a RECYCLED one on the 283rd -- so it MANUFACTURES a `heap-use-after-free` on an input the real stack keeps clean, and it never reports the double free the adversarial blob exists to cause, because `php_shim_efree` of a block under 88 bytes never reaches `free()` (PROTOCOL_PHP.md B1.1). Second, an uninitialised read of a LIVE stack slot is MSan's class and not ASan's. ▶ MIRI IS THE ONLY DETECTOR IN THIS TREE THAT SEES THIS READ AT ALL. `controls/r4_nowitness.rs` is the witness-free R4 and `controls/negatives.py --miri` runs it: Miri must report it on a blob whose op 0 is the faulting arm -- which `inputs/` is structurally unable to carry, because that blob's u64 is not a function of the blob -- and must be silent on the shipped rung and on every shipped input.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph52's cost is 4 x (one window decoded, 16 or 43 concat ops over two slots), i.e. a few hundred arm dispatches and allocator counter updates -- orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend.c",
    "c_lines": [
      242,
      247
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.c | sed -n '242,247p'",
    "extract_sha256": "e3dc2e7da55c2df2f475cc191f890a1c96aab45fdbc1720f40b8fb1c75850e27",
    "extra_spans": [
      {
        "c_file": "Zend/zend_operators.c",
        "c_lines": [
          1146,
          1153
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_operators.c | sed -n '1146,1153p'",
        "extract_sha256": "ccb12491a26d42578217809443b48dad9ec38fecdf541fd8200f929f3990ae7c",
        "why": "`concat_function`'s head -- **THE DECLARATION THE ROW EXISTS TO EXTRACT**. `:1148` is `zval op1_copy, op2_copy;`: bare locals, no `= {0}`, no `INIT_ZVAL`, no `memset`, and `:1152`/`:1153` pass their ADDRESSES to `zend_make_printable_zval`. ⚠ The defect site (`provenance.c_file`) is the CALLEE's early exit and this is the caller's frame, which is `.memory-php/01-extraction.md` F1's shape with the frames the other way round: the corpus names one and the declaration that makes it a defect is in the other. ⚠ NARROWED: `TSRMLS_DC` comes off, and `result == op1`'s in-place arm at `:1155-1178` is not lifted."
      },
      {
        "c_file": "Zend/zend.c",
        "c_lines": [
          188,
          216
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.c | sed -n '188,216p'",
        "extract_sha256": "76180c0f3708c6f2bdb1052b933660b748f6e9d3b7e188aa37243ad8c0dd1eb1",
        "why": "`zend_make_printable_zval`'s head and its first four arms. ⚠⚠ `:190-193` IS THE COMMON PATH AND IT NEVER WRITES `expr_copy` AT ALL -- `if (expr->type==IS_STRING) { *use_copy = 0; return; }` -- which is what makes the function's convention *constructed only if `*use_copy`* and what makes the `:243` teardown wrong. `:195-197` (IS_NULL) and `:204-205` (IS_BOOL false) write `empty_string`, which is why those arms leave the slot PERMANENTLY SAFE. `:202` and `:214` allocate, which is why theirs do not. ⚠ `:207-212` (IS_RESOURCE) is NOT lifted: it needs `zend_list`."
      },
      {
        "c_file": "Zend/zend.c",
        "c_lines": [
          248,
          265
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.c | sed -n '248,265p'",
        "extract_sha256": "5dc049cf738019e8d09df5e95ce91103c17829330d520db37bd84e320a3d942c",
        "why": "The tail -- `:249-250`'s `emalloc` + `sprintf(\"Object id #%ld\")` and, at **`:263`, `expr_copy->type = IS_STRING;`**. ⭐ THIS SPAN IS WHY THE UPSTREAM FIX IS COMPLETE AND WHY THE WRITE ORDER IS PINNED: the tag is written ONCE, AFTER the switch, so every path that leaves the function has written it and `:243` is the only line that reads it before anything has. ⚠ `:253-256` (IS_DOUBLE, `zend_locale_sprintf_double`) and `:258-261` (the IS_LONG default, `convert_to_string`'s `smart_str`) are NOT lifted, and `:250`'s `sprintf` is narrowed to a content digest plus the digit count."
      },
      {
        "c_file": "Zend/zend_variables.c",
        "c_lines": [
          36,
          80
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_variables.c | sed -n '36,80p'",
        "extract_sha256": "bb9d89f1495de6c4bb6096b2081b76caaf89deac118c498681f741df8574b3d0",
        "why": "`_zval_dtor` -- **THE TAG-DISPATCHED TEARDOWN, AND THE REASON THE HARM IS A FREE AND NOT A BRANCH.** `:38` returns early on `IS_LONG`; `:41` switches on `zvalue->type & ~IS_CONSTANT_INDEX`; `:45` is `STR_FREE_REL(zvalue->value.str.val)`, i.e. an `efree` OF A POINTER READ OUT OF THE SAME UNINITIALISED SLOT. ⚠ Two of the six teardown arms are NOT lifted -- `:61`'s `Z_OBJ_HT_P(zvalue)->del_ref` needs `zend_objects_store` and `:69`'s `zend_list_delete` needs `zend_list` -- and `controls/tag_sweep.c` carries ALL SIX over the whole byte so the published 12-of-256 figure is about upstream rather than about the kernel. ⚠ `:44`'s `CHECK_ZVAL_STRING_REL` is EMPTY in a non-`ZEND_DEBUG` build (`zend_API.h:338-346`), which the shipped 5.0.0 is."
      },
      {
        "c_file": "Zend/zend_operators.c",
        "c_lines": [
          1179,
          1194
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_operators.c | sed -n '1179,1194p'",
        "extract_sha256": "94f5871e6adf7cf14571f943eebf163c61068eeb3a461ee86318a68432e02dba",
        "why": "`concat_function`'s `result != op1` arm and **its own teardown at `:1187-1192`**. ⭐ THIS IS WHAT PUTS THE DANGLING POINTER IN THE SLOT: `if (use_copy1) { zval_dtor(op1); }` frees the block `:202`, `:214` or `:249` allocated, and the slot goes on naming it -- so the NEXT call's `:243` frees it again. Without this span the row's trigger would be unexplainable. ⚠ `:1182-1184`'s two `memcpy`s and the NUL store are NOT lifted; see the divergence ledger."
      },
      {
        "c_file": "Zend/zend_variables.c",
        "c_lines": [
          29,
          33
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_variables.c | sed -n '29,33p'",
        "extract_sha256": "9950ff838542d2ad54fe6d6b0e66e271dd6efedf0aceba4931d4510405713f73",
        "why": "`ZEND_API char *empty_string` and upstream's own comment that `STR_FREE()` will not `efree()` it. ⚠ IT IS THE ADDRESS THAT IS COMPARED, so the kernel's `ph52_empty_string` must be ONE object with static storage -- and this span is why three of the five lifted arms leave the slot safe to tear down for ever."
      },
      {
        "c_file": "Zend/zend.h",
        "c_lines": [
          467,
          470
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.h | sed -n '467,470p'",
        "extract_sha256": "06000ffe91b9aba99701fa0cd283cc1c0fd66fafe5454c945f647380bcf6733b",
        "why": "`STR_FREE` / `STR_FREE_REL` -- `if (ptr && ptr!=empty_string) { efree(ptr); }`. The guard the row's benign corpus rests on, pinned in `idiom.required[3]` and mutated in `model.py::_mutants` M2."
      },
      {
        "c_file": "Zend/zend.h",
        "c_lines": [
          275,
          293
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.h | sed -n '275,293p'",
        "extract_sha256": "8c18cd66941a8bfece4c2b958e09fedc4f87c2365124970588cdf830eb74cae9",
        "why": "`union _zvalue_value` and `struct _zval_struct`. ⚠⚠ THE FIELD ORDER IS NOT COSMETIC: `zend_uchar type` sits AFTER `value` and `refcount`, at offset 20 of a 24-byte object, so an extraction that reordered the struct would move which of the caller's leftovers the defect reads. The union's `obj` member is not lifted (it needs `zend_object_value` and `zend_object_handlers`); `ht` IS, because the `IS_ARRAY` teardown arm reads the same eight bytes as a different type."
      },
      {
        "c_file": "Zend/zend.h",
        "c_lines": [
          386,
          399
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.h | sed -n '386,399p'",
        "extract_sha256": "51efeeddb82da4d222f0a1e5f9d3c5e0115731f6e7fc1d72cccedb7b19f1c309",
        "why": "The IS_* codes and `IS_CONSTANT_INDEX 0x80`. ⭐ THIS SPAN IS THE ROW'S PUBLISHED NUMBER: `IS_NULL` is **0**, so a clean stack slot is `IS_NULL` and `_zval_dtor` no-ops on it -- which is why the corpus records `uninit-read-silent`. `controls/tag_sweep.py` drives the whole byte through `:41`'s switch and measures 12 of 256 (4.688 %) tearing anything down. ⚠ `RECAP_PHP.md` F102's untested *\"five named cases\"* and its *\"no `case IS_NULL`\"* are both wrong against this span; `zend_variables.c:75` IS `case IS_NULL:`."
      }
    ],
    "extra_spans_note": "TEN SPANS ACROSS FOUR FILES, AND THE PRIMARY IS SIX LINES. `.memory-php/01-extraction.md` F1: `provenance.c_file`/`c_lines` name the DEFECT site and the other frames go in the notes. ⚠⚠ ON THIS ROW F1's SHAPE IS INVERTED AND IT IS WORTH THE SENTENCE: F1's usual case is that the corpus names the FAULTING frame while the defect is one call DOWN. Here the corpus's own `c_file_line` (`Zend/zend.c:242-247`) IS the defect site and the frame that makes it a defect is one call UP -- `zend_operators.c:1148`'s bare declaration, which is `extra_spans[0]`. A reader who applies F1 mechanically would look in the wrong direction. ⚠ TWO SPANS DO NOT LIFT AND THAT IS THE TIER: `extra_spans[1]`/`[2]` drop three of the switch's eight arms and project the `cast_object`/`get` handler dispatch at `:229-241` onto one attacker byte, which is why this row declares `narrowed`.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC / TSRMLS_FETCH()",
        "kind": "deletion",
        "where": "zend_operators.c:1146; zend.c:219; zend_variables.c:49",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "EG(exception) and the cast_object / get handler dispatch -> one attacker byte",
        "kind": "projection",
        "where": "zend.c:219-241",
        "why": "on the faulting path those handlers' ONLY role is to have SET the exception, and what this row prices is the teardown at `:243`. The `#if 0` block at `:220-228` is dead in the shipped build. ⚠ `.memory-php/01-extraction.md` F8: extraction cost is priced at the DEFECT site, and four rows have been killed by pricing an adjacent frame's machinery. No semantics for the teardown."
      },
      {
        "what": "the IS_RESOURCE, IS_DOUBLE and IS_LONG-default arms of zend_make_printable_zval",
        "kind": "deletion",
        "where": "zend.c:207-212, :253-256, :258-261",
        "why": "`:207-212` needs `zend_list`, `:253-256` needs `zend_locale_sprintf_double` and `:258-261` needs `convert_to_string`'s `smart_str`. The five arms that ARE lifted span every shape the defect needs -- one that writes nothing, one that writes `empty_string`, one that allocates, one that allocates conditionally, and the faulting arm itself -- and `inputs/gen.py` asserts that the corpus reaches all five on BOTH sides. No semantics for the defect."
      },
      {
        "what": "the IS_OBJECT and IS_RESOURCE arms of _zval_dtor",
        "kind": "deletion",
        "where": "zend_variables.c:57-63, :64-71",
        "why": "`:61`'s `Z_OBJ_HT_P(zvalue)->del_ref` needs `zend_objects_store` and `:69`'s `zend_list_delete` needs `zend_list`. ⭐ THE NUMBER THEY AFFECT IS PUBLISHED ANYWAY: `controls/tag_sweep.c` carries all SIX arms over the whole byte, so the row's 12-of-256 figure is about upstream and the kernel's own live count -- 8 of 256 -- is reported beside it. No semantics for the two arms the kernel does reach."
      },
      {
        "what": "CHECK_ZVAL_STRING_REL",
        "kind": "deletion",
        "where": "zend_variables.c:44; zend_API.h:338-346",
        "why": "`zend_API.h:343-346` defines it EMPTY when `ZEND_DEBUG` is 0, and the shipped 5.0.0 build is not a debug build. Keeping the debug arm would ADD a `zend_error` PHP does not do. No semantics."
      },
      {
        "what": "concat_function's result == op1 in-place arm",
        "kind": "deletion",
        "where": "zend_operators.c:1155-1178",
        "why": "the kernel always passes a `result` distinct from both operands, so `result == op1` is false on every call it makes and the `else` at `:1179-1186` is the arm that runs. ⚠ BOTH ARMS ARE DOWNSTREAM OF THE DEFECT -- `:1152`/`:1153` have already run -- so nothing the row measures depends on which. No semantics over the reachable domain."
      },
      {
        "what": "zend.c:250's sprintf and zend_operators.c:1182-1184's two memcpys and NUL store -> a 131-content digest",
        "kind": "narrowed",
        "where": "zend.c:250; zend_operators.c:1182-1184",
        "why": "⚠⚠ THE LARGEST C-SIDE DIVERGENCE ON THE ROW AND A REACHABLE-DOMAIN ARGUMENT IS OWED AND GIVEN. The bytes those lines move are a PURE FUNCTION of the two operand descriptors, so the kernel allocates exactly the blocks upstream allocates -- `:249`'s `sizeof(\"Object id #\")-1 + MAX_LENGTH_OF_LONG` and `:1181`'s `total + 1` -- and folds the same content as a digest (`PH52_DIG_*` plus the handle's decimal digits) instead of materialising it. It CHANGES THE u64, so it is `narrowed` and not a `substitution`: every rung computes the same digest and all six agree, but the number is not what a kernel carrying the stores would print. ⭐ THE REASON IS `ph64`'s LESSON ONE LEVEL OVER: keeping the stores would put a `Seq<u8>` concatenation in `verus.rs`'s postcondition and would make the cross-language column a comparison of `rep movsb` against a Rust `while` loop -- a memcpy comparison, not a safety comparison, on a row whose cross-language column already carries an allocator caveat. ⚠ What it does NOT change is the allocator request sequence, the slot state machine, the teardown dispatch or the number of `:243` calls, which are the quantities the row measures. `model.py::selfcheck` checks each digest constant against the literal it stands for and `_dumb` spells the object arm from the literals rather than from the constants."
      },
      {
        "what": "zend.c:250's sprintf(\"%ld\") -> an exhaustive three-way case on the digit count",
        "kind": "narrowed",
        "where": "zend.c:250",
        "why": "the kernel projects `zend_object_handle` (`zend.h:265`, an `unsigned int`) onto ONE window byte, so the handle has at most three decimal digits and `sprintf`'s own `do { } while (d)` becomes an exhaustive three-way case -- in all six rungs, so the asymmetry is not between languages. ⚠ DECLARED BECAUSE IT BOUNDS THE ATTACKER: a handle of 2^32 would run ten iterations and the row does not price that. No semantics over the reachable domain."
      },
      {
        "what": "__attribute__((noinline)) on the lifted zend.c and zend_variables.c functions",
        "kind": "substitution",
        "where": "zend.c:188; zend_variables.c:36; zend_operators.c:1146",
        "why": "⚠⚠⚠ NOT COSMETIC AND MEASURED, NOT ASSERTED. Upstream `concat_function`, `zend_make_printable_zval` and `_zval_dtor` live in THREE SEPARATE TRANSLATION UNITS and PHP 5.0.0 links without LTO; `harness/build.py` compiles exactly three TUs for the whole row and is frozen, so the boundary is spelled with `PH52_NOINLINE` instead. `controls/d0_stack.py` is the differential: over 16 cells -- {gcc, clang} x {-O0, -O3} x {isolated, whole} x {callee noinline, callee inlinable} -- the eight `noinline` cells agree on ONE u64 and the eight `inlinable` ones split THREE ways, because at `-O3` a compiler that can see the unwritten tag may treat it as `undef` and fold the teardown away. ⚠ The harness's own `isolated`/`whole` axis moves NOTHING. No semantics relative to upstream's build configuration, which is what the substitution restores."
      },
      {
        "what": "emalloc / erealloc / efree / estrndup -> php_shim_*",
        "kind": "substitution",
        "where": "zend.c:202, :214, :249; zend_operators.c:1181; zend_variables.c:45",
        "why": "NOT a divergence in substance: `common-php/emalloc_shim.h` IS PHP 5.0.0's own `_emalloc`/`_efree`/`_estrndup`, cited line by line, and `PROTOCOL_PHP.md` §B REQUIRES it. It is listed so a reader can see that the allocator was not substituted for a plain `malloc` -- which an earlier effort did, and as a direct result reported a real defect as unreachable. ⭐ AND ON THIS ROW THE SHIM IS LOAD-BEARING FOR THE RESULT, not merely for fidelity: the size-class cache at `zend_alloc.c:270-279` means the second `efree` of the same block never reaches `free()`, so the double free is SILENT under ASan and lands in `php_shim_tally()` instead. No semantics."
      },
      {
        "what": "the four Rust rungs reproduce php_shim_tally() arithmetically instead of linking the shim",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:642-648, :346-435",
        "why": "`harness/build.py` compiles exactly three C translation units, no Rust rung links C, and §B forbids it anyway. ⚠⚠ AND THE REPRODUCTION IS NOT CLOSED-FORM HERE, WHICH IS §B1a's PRECONDITION FAILING: the kernel allocates O(n_ops) times per call, so the size-class cache is EVOLVING and each rung carries a counters-only simulation of it -- `cnt[11]`, `n_alloc`, `n_free`, `n_hit`, `bytes` -- transcribed from `_emalloc`'s `:150-168` and `_efree`'s `:270-279`. `ph64`'s `safe_naive.rs::Alloc` is the precedent and this is the second row to need one. ▶ §B1a.3 binds and every cross-language figure is labelled. No semantics: verified against the C, all six rungs agree bit for bit on both measured inputs."
      },
      {
        "what": "the zval's `obj` union member and the 22 fields of struct _zend_class_entry",
        "kind": "deletion",
        "where": "zend.h:270-284",
        "why": "`zend_object_value` needs `zend_object_handlers`, and nothing in the extracted spans reads it -- the `IS_OBJECT` teardown arm that would is itself not lifted. `lval`, `dval`, `str` and `ht` are kept, in upstream's order. No semantics."
      },
      {
        "what": "R4 and R5 carry a one-bit-per-slot `constructed` witness that no C rung has",
        "kind": "projection",
        "where": "c/kernel.c's ph52_zval_dtor; verus.rs",
        "why": "⚠⚠⚠ THE LARGEST RUST-SIDE DIVERGENCE AND IT IS A RESULT RATHER THAN A CHOICE. A faithful unsafe port reads the `MaybeUninit` with no test, which is `zend.c:243` exactly, and THAT PROGRAM CANNOT BE VERIFIED: `assume_init_ref`'s precondition is `m.mem_contents().is_init()`, whether the slot was constructed is a property of the OP STREAM (i.e. of attacker data), and the pinned driver loop calls the kernel with no test -- so there is no call site at which to establish it and no `requires` that could carry it. `controls/negatives.py --verus` mutant V1 is that program and Verus refuses it with `precondition not satisfied`. R4/R5 therefore carry the cheapest witness that discharges it: TWO BOOLS for the whole kernel, against ph53's `[bool; MAXD]`. ⭐⭐ AND THE CONSEQUENCE IS DIFFERENT FROM ph53's: `controls/r4_nowitness.rs` REPRODUCES THE DEFECT BIT FOR BIT -- it prints R1's answer on `inputs/adversarial-dblfree.bin`, not R1h's, because the `MaybeUninit` retains the previous op's value exactly as the stack slot does -- where ph53's witness-free control answered CORRECTLY where its R1 faulted. NOTES.md 11."
      },
      {
        "what": "safe_naive.rs's slot is Option<Pr>, so the C's fourth slot state is unrepresentable",
        "kind": "projection",
        "where": "zend_operators.c:1148; zend_variables.c:45",
        "why": "⚠⚠ THE ROW'S LADDER RESULT, DECLARED RATHER THAN LEFT TO BE NOTICED. The C's slot has FOUR states -- unconstructed, `IS_STRING` + `empty_string`, `IS_STRING` + a live block, `IS_STRING` + a block `:1188` has freed -- and safe Rust has THREE, because `slot.take()` leaves `None` the moment the block is released. The fourth state is the defect and there is no safe expression that produces it. ⚠ It is NOT `Option` reinventing the upstream fix: `7412202c43e7` deletes the teardown and keeps the states, `Option` keeps the teardown and deletes the state. ⚠⚠ THIS ENTRY'S `why` CANNOT END IN \"no semantics\" AND §A2 IS SATISFIED ANYWAY: §A2 asks for every way the row's C differs from the tarball, and this is a statement about the RUST rungs, which are not ports of R1. The tier is `narrowed` ON THE C and this is reported as the row's finding."
      },
      {
        "what": "safe_tuned.rs returns the printable instead of writing through a &mut",
        "kind": "projection",
        "where": "zend.c:188-265 as repaired by 7412202c43e7",
        "why": "⭐ R3 IS A PORT OF R1h AND THE STRUCTURAL FORM OF IT: with no `expr_copy` out-parameter there is no slot in scope on the early-exit path, so the line `7412202c43e7` deletes cannot even be written. ⚠ It is available only BECAUSE the fix is complete; ph53's R3 could not be a port of its R1h for exactly the opposite reason. DECLARED BECAUSE IT IS A REAL COST DIFFERENCE and not plumbing: NOTES.md 8 prices it rather than letting it sit inside \"R3 is cheapest\"."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection / narrowed and is DECLARED, NEVER DETECTED -- `provenance.py` does not read this block at all (`PROTOCOL_PHP.md` §D). Nothing may come to depend on it. ⚠ THREE of these fifteen entries are about the RUST rungs rather than about the extraction, and that is deliberate: §A2 asks for every way the row's C differs from the tarball, and `.memory-php/02-ladder.md` adds that R2-R5 need not be ports of R1h -- so the places where the Rust rungs are a different program from the C are exactly what a reader needs and exactly what no line citation can carry. ⚠⚠ TWO ENTRIES ARE `narrowed` RATHER THAN `substitution` BECAUSE THEY CHANGE THE u64, and §A2 says a divergence that changes behaviour is a `modelled` tier: both are changes to what the kernel COMPUTES and neither touches the mechanism the row prices, which is the distinction ph53's `instanceof_function` narrowing already drew. The tier is `narrowed` and the reachable-domain argument is in each entry.",
    "root_cause_ids": [
      "caller-slot-declared-uninitialised-then-destructed-by-the-callee-on-an-early-exit"
    ],
    "cwe": "CWE-457",
    "cwe_note": "CWE-457 (use of uninitialised variable) with CWE-824 (access of uninitialised pointer) as the consequence, and `CATALOGUE.md`'s T3 family is *initialised before read*. ⚠⚠ THE CORPUS RECORDS NO CRASH FOR LOGIC-007 AND THE ROW EXPLAINS THAT RATHER THAN EXCUSING IT (§A4). `vuln_class = uninit-read-silent` is verified directly in `.tasks-php/TASK_PHP_001_MINE/type/NOTES.md:398`; the *`n/a (non-crash class)`* phrasing that has circulated is `TASK_PHP_040_REPORT.md:221` quoting `index.csv`, which is NOT in this repository, and this row rests nothing on it. ▶ THREE INDEPENDENT MEASURED REASONS THE WILD RUN IS SILENT, and the first is the publishable one: (1) `controls/tag_sweep.py` measures 12 OF 256 TAG BYTES (4.688 %) TEARING ANYTHING DOWN and 8 of 256 (3.125 %) reaching `efree`, so 95.3 % of the time `:243` is a no-op -- and `IS_NULL` is 0, so a clean slot is the likeliest case of all; (2) PHP's own size-class cache means the second `efree` of a block under 88 bytes never reaches `free()` (`zend_alloc.c:270-279`), so even when it DOES fire no allocator raises anything -- `PROTOCOL_PHP.md` §B1.1; (3) ASan's fake stack relocates the frame per call, so the sanitizer that would be asked to look does not see the slot at all -- ⛔⛔ AND THAT THIRD MECHANISM CUTS BOTH WAYS AND IS THE ROW'S MOST SURPRISING MEASUREMENT: 1 in 283 `:243`-reaching calls gets a RECYCLED fake frame instead of a zeroed one, so under check.py's own ASan line R1 reports `heap-use-after-free` ON THE TWO BENIGN INPUTS and is CLEAN on the adversarial one, while R1h is clean on all six. `model.py::sanitizer_expect` declares that, and its docstring and NOTES.md §7 carry the trace. ⚠ On the REAL stack -- the binaries every number here was taken with -- all 25,000 iterations' `:243` calls read `empty_string` and free nothing. ⚠ The manager's prediction that ASan would fire ON THE DOUBLE FREE where the corpus says silent is therefore REFUTED three ways: it never reports the double free on any input, what it reports is a use-after-free it CAUSED itself on the BENIGN inputs, and the mechanism is frame recycling rather than the allocator. ⭐ WHAT THE ROW REPRODUCES INSTEAD IS A DOUBLE FREE VISIBLE IN THE PUBLISHED u64: on `inputs/adversarial-dblfree.bin` R1 prints 272040826665440682 and R1h prints 272040826666539789, in all four C cells, and at `n_iters = 64` the deferred free in `php_shim_reset()` makes glibc abort with `double free detected in tcache 2`, exit 134. NOTES.md 5 and 7. ⚠ AND MIRI IS THE ONLY DETECTOR IN THIS TREE THAT SEES THE READ ITSELF: `controls/negatives.py --miri` M3 reports `Undefined Behavior: reading memory at alloc...[0x0..0x8], but memory is uninitialized` on the witness-free control, and M4 is silent on the shipped rung with the one-bit witness.",
    "fix_commit": "7412202c43e74d24c55669dedc36542e43b4f2bb",
    "fix_commit_note": "✅ THE CORPUS COLUMN AND `FIXSURVEY_001.md:242` AGREE ON THIS SHA, so unlike ph53 there is no wrong commit to exclude (`PROTOCOL_PHP.md` §F5(iii) is satisfied without a tag walk). Antony Dovgal, 2006-05-11, \"no need to destroy the zval here\", `Zend/zend.c`, 1 file, 1 hunk, 0 insertions, 1 deletion; the patch is committed at `controls/7412202c43e7.patch`, sha256 32e8526ebfe684d9ae80e32df0f453c018f954dd0694f1cd5cbc7d30891adfbf, 746 B, so the citation survives without network. ⛔⛔ IT IS A HAND RECONSTRUCTION AND NOT A `patch -p1`, WHICH §C SAYS OWES AN ARGUMENT, AND HERE IS EVERY TOKEN THAT DIFFERS. The DELETED LINE matches byte for byte except for one tab: the commit removes `\\t\\t\\t\\tzval_dtor(expr_copy);\\n` (four tabs) and 5.0.0's `:243` is `\\t\\t\\t\\t\\tzval_dtor(expr_copy);\\n` (five), because by 2006 the arm had lost a level of nesting. The CONTEXT does not match at all: the 2006 hunk's lines name `STR_EMPTY_ALLOC()` and `E_RECOVERABLE_ERROR`, and BOTH ARE ABSENT FROM THE WHOLE 5.0.0 TARBALL -- measured, 0 occurrences across `Zend/zend.h`, `zend_variables.h`, `zend_API.h`, `zend_operators.h` and `zend_errors.h` -- while 5.0.0's arm writes `empty_string` and ends in `break;`. ⭐ AND THE DATE IS THE POINT OF THE ROW AS MUCH AS THE DIFF IS: 2006 is AFTER EVERY 5.0.x RELEASE, so the defect shipped in all of them and the fix is in none. ⭐⭐ `controls/r1h_onelinedel.py` IS THIS ARGUMENT AS A CHECK RATHER THAN AS PROSE: it derives `c/kernel_hardened.c` from `c/kernel.c` by that one deletion, reports `code lines only in R1: 1` / `only in R1h: 0`, and carries an 11-case suite whose must-fire arms include a hardened kernel that added a GUARD instead of deleting the call, one that deleted `:1188` as well, and a comment-only edit that must still fail the derivation. ⚠⚠ AND THE FIX IS COMPLETE, WHICH IS THE OPPOSITE OF ph53's RESULT: `zend.c:243` is the only line in the function that reads `expr_copy` before any path has written it, and `:263` sits after the switch -- so there is nothing left for the deletion to miss. ▶ The consequence is that R2-R5 ARE ports of R1h, and `inputs/adversarial-dblfree.bin` CAN ship, because R1h is clean on it. ph53 could do neither.",
    "invariant": "I3",
    "obligation": "O1",
    "invariant_note": "`CATALOGUE.md:146`'s T3 row for ph52 declares I3/O1 and this row carries the declaration forward unchanged; the labels live in `paper/invariants-166.json` and are ATTRIBUTED rather than re-derived here. ⚠ `invariant` and `obligation` are UNVALIDATED DECLARATIONS (`PROTOCOL_PHP.md` §D) and nothing in the gate reads them. What the proof actually discharges is written out in `verus.obligations_note`, in the spelling the pinned vstd has: `*old(constructed) ==> slot.mem_contents().is_init()`.",
    "echoes": [
      "p42"
    ],
    "echoes_note": "`CATALOGUE.md` names `p42-goto-cleanup` as the closest PAT analogue and this row keeps the cross-reference: p42 is a cleanup path that runs over state a failed setup never built. `PLAN_PHP.md` §3.1 makes an overlap a CROSS-REFERENCE and NEVER a filter -- `patterns-php/` is fresh and stands on its own. ⭐ AND THE MORE USEFUL CROSS-REFERENCE IS INSIDE THIS PROGRAMME: `ph53` is the same FAMILY (T3) and differs on four counts -- heap vs STACK, a pointer value vs a DISCRIMINANT, a fold vs a DISPATCH, a wild deref vs a WRONG-ARM TEARDOWN -- and the two rows together are the first two-row statement this programme has on the T3 axis: see NOTES.md 11 for the witness-cost comparison, which is what makes ph53's F98 falsifiable.",
    "uses_allocator": true,
    "uses_allocator_why": "`c/kernel.c` and `c/kernel_hardened.c` make up to FIVE `php_shim_emalloc`/`php_shim_estrndup` calls and THREE `php_shim_efree` calls PER CONCAT OP, i.e. O(n_ops) per kernel call, plus `php_shim_reset()` at the top of every call (§B1.3). `php_shim_tally()` is folded into the returned u64 (§B1.2) and the four Rust rungs reproduce it with a counters-only simulation of the size-class cache, because the count is not O(1). ⚠ DECLARED, NEVER DETECTED (`TASK_PHP_008` §0.4) -- nothing reads this field, and the `c/emalloc_shim.h` symlink is unconditional whatever it says. ⭐ The allocation ORDER is declared in `idiom.required`'s allocation entry, per §B1a.2, and §B1a.3's labelling obligation is carried in every rung's module header."
  }
}
```
