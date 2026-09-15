# ph96 — SUCCESS does not mean the out-parameter was written

**PHP 5.0.0, `Zend/zend_object_handlers.c:506-517`, corpus row CRASH-061, tier
`modelled`** — ⚠ the catalogue says `narrowed` and this row **refutes its own
mining-wave label**; `NOTES.md` §11 has the measurement and the argument. `zend_std_unset_dimension` declares `zval *retval;` at `:509`,
hands its address to `zend_call_method_with_1_params` at `:512`, and calls
`zval_ptr_dtor(&retval)` at `:513` — **no test of any kind.** Testing the status
would not have helped and is not what is missing: `zend_call_function` writes
`*fci->retval_ptr_ptr = NULL` at `zend_execute_API.c:595` under its own comment
*"we may return SUCCESS, and yet retval may be uninitialized, if there was an
exception"*, and returns `SUCCESS` unconditionally at `:873` with the exception
still pending. `_zval_ptr_dtor`'s first statement is `(*zval_ptr)->refcount--`.

⭐⭐ **THE STATUS IS TESTED AND THE OUT-PARAMETER IS NOT.**
`zend_interfaces.c:81-87` tests `result == FAILURE` and raises `E_CORE_ERROR`,
which does not return. `I12/O1` lists four things that must be tested — *a NULL
return, sentinel, status code, **or NULL-able out-parameter*** — and it is the
last of the four that nothing here looks at.

⭐⭐⭐ **AND CRITERION 2 IS MEASURED FOUR TIMES OVER ON THIS ROW.** A PHP 5.0.0
CLI on this box, under the committed `LD_PRELOAD` shim
`.tasks-php/probes/segaddr.c` and driven by the committed
`.tasks-php/probes/ph96_arrayaccess_matrix.sh`:

```
offsetUnset  throws  :512  output, UNGUARDED   -> SIG11 si_code=1 si_addr=0x10  rc 139
offsetExists throws  :427  output, UNGUARDED   -> SIG11 si_code=1 si_addr=0x14  rc 139
offsetGet    throws  :384  output + GUARD :385 -> Fatal error: Uncaught ...     rc 255
offsetSet    throws  :413  NO-OUTPUT (NULL)    -> Fatal error: Uncaught ...     rc 255
nothing      throws  --                        -> benign ok                     rc 0
```

**Same binary, same run, five runs each of the two faulting scripts with the
same signal and the same address every time.** ⚠ Two cautions travel with that
and `NOTES.md` §2 repeats them: the binary is php-in-safe-rust's **oracle
build**, not a museum-default one, and a clean run would not have been evidence
of absence. `c/kernel.c` reproduces `si_addr=0x10` from the same shim, and the
address is `offsetof(zval, refcount)` — a **struct offset**, which `c/kernel.c`
asserts at build time.

⭐⭐⭐ **BOTH CORRECT SPELLINGS AND BOTH WRONG SPELLINGS ARE IN ONE FILE, BY ONE
AUTHOR, BEFORE THE BUG WAS REPORTED.** `:385` is `if (!retval)` — the output
contract, guarded, **two lines after** an identical call. `:413` passes `NULL` —
the no-output contract, **99 lines before** `:512`. The row therefore models the
**contract**, not the site: one kernel, one helper, four consumer shapes.

**R1h is a BACKPORT of `cf020f133487`** (Marcus Boerger, 2005-03-19, *"- Fix
#31185"*) — three lines at the `offsetunset` site. ⛔ `git apply --check`
**refuses** the cached patch on pristine 5.0.0 at every context width, because
its pre-image carries two lines 5.0.0 does not have. The hand backport
reproduces upstream's own diffstat exactly — `1 insertion(+), 3 deletions(-)` —
so the semantic change is upstream's and only the context is not. `NOTES.md` §4.

⛔⛔⛔ **AND THE UPSTREAM REPAIR IS INCOMPLETE.** `:427-429` has the same defect,
`cf020f133487` does not touch it, and **both C rungs fault on it at
`si_addr=0x14`.** `controls/second_limb.py` measures it through all six rungs.
`NOTES.md` §5 states the scope of that claim, which is narrow.

The machine-readable contract follows.
`harness-php/gate.py ph96-outparam-unwritten` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == ph96_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (ph96_fold). `ph96_fold` is model.py's SECOND, independent implementation -- a RECURSIVE walk with no cursor variable and no window table, mirroring verus.rs's `s_run` / `s_step` / `s_fold_zval` / `s_fold_bytes` one unfolding at a time -- and not the imperative `_window` simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic records model.py builds itself, spanning the WHOLE (shape x failed x wrote) cross product INCLUDING the four sentinel cells no measured input may carry, every Z_TYPE tag against every truth value, the whole Z_STRLEN domain, a payload whose first byte is the digit zero at every length, and eight degenerate strides. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. A THIRD spelling, `_dumb`, decides each record's outcome by DICT LOOKUP on the decoded (shape, failed, wrote) triple instead of walking the helper and the four handlers -- the one spelling that cannot share a CONTROL-FLOW mistake with the other two, and control flow is exactly where this row's defect lives.",
  "idiom": {
    "required": [
      {
        "c": "`b[1] % 5u` and `b[2] % 3u` -- the call's STATUS and its WROTE-OUTPUT bit, decoded from TWO SEPARATE BYTES. The first is what zend_call_function returns at zend_execute_API.c:667, :674 and :679; the second is whether the user method replaced the sentinel zend_execute_API.c:595 wrote. They answer two different questions: *did the call fail?* and *is the output there?*. zend_interfaces.c:81 answers the first and zend_object_handlers.c:513 needs the second. A kernel that derived either from the other -- an output bit meaningful only when the call succeeded, say -- would have deleted the mechanism before a single rung was measured, and the row would be ph60 rebuilt. That is the catalogue's own risk note on this row, verbatim. inputs/gen.py asserts the corpus reaches every combination the benign domain admits and model.py's synthetic sweep drives the whole four-by-two-by-two cross product.",
        "rust": "`sget(b, 1) % 5` and `sget(b, 2) % 3` -- the call's STATUS and its WROTE-OUTPUT bit, decoded from TWO SEPARATE BYTES. The first is what zend_call_function returns; the second is whether the user method replaced the sentinel zend_execute_API.c:595 wrote. A rung that derived either from the other would have deleted the mechanism and would be modelling an ordinary missing NULL check."
      },
      {
        "c": "`*retval_ptr_ptr = (ph96_zval *) 0` -- zend_execute_API.c:595, THE SENTINEL, and it is written UNCONDITIONALLY and BEFORE every FAILURE return in that function. The author's comment two lines above it names the hazard it exists to make detectable: SUCCESS may be returned with retval uninitialized if there was an exception. A kernel that wrote the sentinel only on the failure path, or not at all, would have turned a documented NULL into an uninitialised pointer and would be modelling a different bug class.",
        "rust": "`let mut wrote: bool = false` -- zend_execute_API.c:595, THE SENTINEL. In Rust a callee cannot store a reference to a frame it is still writing, so the callee reports whether it wrote and the caller forms the Option from that. The one bit is the same bit: upstream spells it as a pointer that is still NULL and this spells it as an Option that is still None. NO SECOND BACKTICKED SPELLING IN THIS ENTRY, deliberately -- the C declaration is a C spelling and a pin on it inside a rust-keyed entry would pin NOTHING, which is item 100 exactly, and the first draft of this very sentence was caught by controls/spellings.py doing it."
      },
      {
        "c": "`result == PH96_FAILURE` -- zend_interfaces.c:81, THE STATUS TEST, AND IT IS PRESENT AND IT IS CORRECT. Upstream raises E_CORE_ERROR here, which does not return, so I12/O1's *status code* clause is DISCHARGED at this site. The row's claim is about the clause beside it -- *or NULL-able out-parameter* -- and a kernel whose status could never fail would have no status guard at all, which would make the claim untestable. inputs/adversarial-corefail.bin is the input that makes this arm fire and inputs/gen.py refuses a measured corpus that never reaches it.",
        "rust": "the status test, which is present and correct and which the row does not claim is missing. It is spelled as the early return reported by call_method, and the record byte it reads is already pinned by the first entry above. NO BACKTICKED SPELLING ON THIS SIDE, deliberately: the three safe rungs and the Verus rung write the early return four different ways and a pin here would name a spelling only some of them carry."
      },
      {
        "c": "`ph96_zval_ptr_dtor(&retval, n_rel)` -- zend_object_handlers.c:513 and :429, THE RELEASE, and there is nothing between it and the call: no NULL test, no second look at the status, no question put to the helper about what it wrote. The pointer is the sentinel whenever the user method threw. Testing it here is one of the two attested repairs and controls/repair_price.py prices it; removing the output instead is cf020f133487 and is what c/kernel_hardened.c does. The spelling is shared by BOTH C rungs on purpose, because the hardened rung differs from this one at the unset site and NOT at the exists site.",
        "rust": "`zval_ptr_dtor(rv, n_rel)` -- zend_object_handlers.c:429, THE RELEASE. In Rust the out-parameter cannot be released without being opened, so the call goes through an accessor; WHICH accessor is the R3-to-R4 lever and is deliberately not pinned here. What IS pinned is that the released value is the helper's output, unmediated by any test of the status."
      },
      {
        "c": "`(*zval_ptr)->refcount--` -- zend_execute_API.c:389, THE DEREFERENCE, and the exact expression a PHP 5.0.0 CLI faults on. It is the FIRST statement of _zval_ptr_dtor. The faulting address is 0x10 rather than zero because refcount is not the first field: Zend/zend.h:287-293 puts the 16-byte zvalue_value union in front of it on LP64, and c/kernel.c holds its own zval to that layout with negative-array-size assertions that fail the BUILD if it ever stops matching. A struct offset is a harder target to hit by accident than offset zero, and controls/fault_addr.py measures both C rungs against both offsets with a must-fire control.",
        "rust": "`z.refcount = z.refcount - 1` -- zend_execute_API.c:389, the refcount decrement. It is reached through an already-opened reference in every Rust rung, which is why no Rust rung can reproduce the fault: the dereference the C performs is the OPEN, and in Rust the open is where the test has to be. NO BACKTICKED SPELLING OF THE ACCESSOR ON THIS SIDE, deliberately: it is the R3-to-R4 lever."
      },
      {
        "c": "`if (!retval) {` -- zend_object_handlers.c:385, THE GUARDED CELL OF THE 2x2, written TWO LINES AFTER an identical call and by the same author. It is one of the two correct spellings in the vulnerable file, and the other is the NO-OUTPUT contract at :413. Both C rungs carry it, because the defect is that the same test is absent 128 lines further down and not that the author did not know it.",
        "rust": "`retval.is_none()` -- zend_object_handlers.c:385, THE GUARDED CELL OF THE 2x2, and in Rust it is also the guard at :427 that upstream does not have. ../NOTES.md section 5 says why: an Option cannot be opened without a None arm, so the type forces a decision C never had to make. That is a finding about the ladder and not a liberty taken with the extraction."
      },
      "R1h IS A BACKPORT OF cf020f133487d36a8b1d9cfd16ec456f7f07952e (Marcus Boerger, 2005-03-19, '- Fix #31185') AND IT IS THREE LINES AT ONE SITE: the local zval pointer goes, the helper is handed NULL instead of its address, and the dtor goes. It does not TEST the output -- it REMOVES it, switching the call site from zend_interfaces.c:94's contract to :88-93's, which is the contract :413 had been using since before the bug was reported. git apply REFUSES the cached patch on pristine 5.0.0 at every context width, because the pre-image carries two lines 5.0.0 does not have; the hand backport reproduces upstream's own diffstat exactly, 1 insertion and 3 deletions, so the semantic change is upstream's and only the context is not. controls/r1h_backport.py RUNS both halves on every invocation and takes the verdict FROM THE BYTES rather than from an exit status. R2 through R5 implement this same function PLUS the :385 guard at :427, because an Option cannot be released without being opened; the two coincide on the whole benign domain and controls/second_limb.py measures the one state where they part. NO BACKTICKED SPELLING ANYWHERE IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements, the six rungs spell it in three languages, and no single token decides it."
    ],
    "forbidden": [
      "`unwrap_or` -- SUBSTITUTING A DEFAULT OUTPUT for an absent one. It is the most plausible Rust repair and it is the wrong one: the release would stop faulting, but it would release a value the callee never produced, which is I16/O2 -- the outputs of an aborted call must not be destroyed -- broken the other way round. Upstream's own answer at the unset site is the opposite direction: remove the output, so there is nothing to default. Note the absence of backticks in the rest of this entry, and it is not style: in a forbidden entry EVERY backticked span becomes a banned token, so an entry that quotes what it is PROTECTING bans that too (item 100, three instances in three consecutive tasks).",
      "`memcpy` and `copy_from_slice` -- MOVING THE VALUE FOLD OUT OF THE MEASURED SYMBOL. The ten bytes of Z_STRVAL a read_dimension call folds are walked by an explicit byte loop in every rung, and they are walked there rather than by a library call because family A1 is symbol-scoped and STRUCTURALLY EXCLUDES callee work: on ph53, 100 per cent of a seven-instruction swing lived inside a libc call A1 could not see, and on ph97 the same substitution moved inside_share by 34 percentage points and flipped the sign of the measured difference. A rung that called out for the fold would be measuring a different program with the same answer.",
      "`to_vec` and `Vec::` -- ALLOCATING PER RECORD. The row declares that it allocates nothing, so PROTOCOL_PHP.md B1a's precondition holds at ZERO allocations per call rather than at O(1) and the cross-language column carries no allocator caveat at all. ph64 allocates 2n+2 blocks per call and 60 per cent of its C rung's instructions are in malloc and free, which makes that row's cross-language column largely a comparison of an allocator against arithmetic. A rung that allocated a buffer per record would put this row in the same position for no fidelity gain: the zval a user method returns is a fixed-size record and the row models no allocator."
    ],
    "why": "ph96 is PHP 5.0.0's `zend_call_method` helper and the FOUR `ArrayAccess` handlers in `Zend/zend_object_handlers.c` that call it, corpus row CRASH-061. THE IDIOM IS A CALL THAT REPORTS SUCCESS AND LEAVES ITS OUT-PARAMETER AT A SENTINEL THE CALLEE WROTE ON PURPOSE, AND A CALLER THAT RELEASES THAT OUT-PARAMETER WITH NO TEST OF ANY KIND. \u2b50\u2b50\u2b50 THE WHOLE MECHANISM IS THREE LINES AND THEY ARE ALL IN THE TARBALL. `zend_execute_API.c:595` writes `*fci->retval_ptr_ptr = NULL` under its own comment at `:592-594` -- *we may return SUCCESS, and yet retval may be uninitialized, if there was an exception* -- and `:870-873` re-throws the pending exception and returns SUCCESS anyway. `zend_object_handlers.c:509` declares `zval *retval;`, `:512` hands its address to the helper, and `:513` calls `zval_ptr_dtor(&retval)`, whose first statement is `(*zval_ptr)->refcount--` at `zend_execute_API.c:389`. \u26a0\u26a0 THE STATUS IS TESTED AND IT IS THE OUT-PARAMETER THAT IS NOT, AND THAT IS WHAT SEPARATES THIS ROW FROM `ph60`. `zend_interfaces.c:81-87` tests `result == FAILURE` and raises `E_CORE_ERROR`, which does not return. `I12/O1` names the case verbatim -- *a NULL return, sentinel, status code, or NULL-able out-parameter must be tested* -- and it is the LAST of those four that nothing here tests. `I16/O2` is *the outputs of an aborted call must not be ... destroyed*, which is the `zval_ptr_dtor` half, and the kernel's release tally is the quantity that obligation is about. \u2b50\u2b50\u2b50 CRITERION 2 IS MEASURED ON THIS ROW AND IT IS MEASURED FOUR TIMES OVER. A PHP 5.0.0 CLI on this box, under the committed `LD_PRELOAD` shim `.tasks-php/probes/segaddr.c` and driven by the committed `.tasks-php/probes/ph96_arrayaccess_matrix.sh`, answers a throwing `offsetUnset` with `SIG11 si_code=1 si_addr=0x10` and exit 139, a throwing `offsetExists` with `si_addr=0x14` and exit 139, a throwing `offsetGet` and a throwing `offsetSet` with PHP's own `Fatal error: Uncaught exception` and exit 255, and a script in which nothing throws with exit 0. Five runs each of the two faulting scripts gave the same signal and the same address every time: a STABLE SIGNAL WITH A STABLE ADDRESS, which is the strongest of the three categories `PROTOCOL_PHP.md` A3a step 4 distinguishes. \u26a0\u26a0 TWO CAUTIONS TRAVEL WITH THAT AND THEY ARE REPEATED HERE BECAUSE A ROW THAT OMITS THEM HAS OVER-CLAIMED: the binary is php-in-safe-rust's ORACLE build (mysql + webext) and NOT a museum-default one, and a CLEAN run would not have been evidence of absence (`RECAP_PHP.md` F3). The converse is the half this programme long lacked: a run that faults, executed, is evidence of PRESENCE. `../NOTES.md` section 2 has every run. \u2b50\u2b50 AND THE C RUNG REPRODUCES IT AT THE ADDRESS, WHICH IS A STRONGER MATCH THAN AN ADDRESS OF ZERO WOULD BE. `c/kernel.c` on `inputs/adversarial-unset.bin` prints the SAME string from the SAME shim -- `SIG11 si_code=1 si_addr=0x10` -- and 0x10 is `offsetof(zval, refcount)`, which `Zend/zend.h:287-293` fixes on LP64 because the `zvalue_value` union is 16 bytes. `c/kernel.c` carries three negative-array-size assertions holding its own zval to that layout, so the match is a BUILD-TIME property of the extraction rather than a coincidence of one run. A struct offset is a harder target to hit by accident than offset zero. `../NOTES.md` section 3. \u26d4\u26d4 THE 2x2 IS INSIDE THE MEASURED ARTEFACT AND IT IS WHY THE ROW MODELS THE CONTRACT RATHER THAN THE SITE. `zend_object_handlers.c` calls ONE helper from FOUR handlers: `:384` takes the output contract and GUARDS it at `:385` with `if (!retval)`; `:413` takes the NO-OUTPUT contract by passing NULL; `:427` and `:512` take the output contract and guard nothing. Both correct spellings and both wrong spellings are in one file by one author, and the no-output contract was already supported in 5.0.0 with the very test `:513` omits -- `zend_interfaces.c:48` selects it and `:88-93` disposes of the value behind its own `if (retval)`. A census of the 23 real `zend_call_method` call sites in 5.0.0 finds SEVEN already on the no-output contract and SIXTEEN on the output one; `controls/census.py` re-derives that rather than asserting it. So the 2005 repair did not invent a strategy, it copied the sibling 99 lines up. \u26d4\u26d4 THE BLOB CARRIES `(status, wrote_out)` INDEPENDENTLY AND THE INDEPENDENCE IS THE ROW. `b[1]` decides whether `zend_call_function` returns FAILURE and `b[2]` decides whether the user method left an output, and neither is computed from the other: a kernel that derived the second from the first would have deleted the mechanism and rebuilt `ph60`, which is the catalogue's own risk note on this row. `inputs/gen.py` asserts that the measured corpus reaches the three combinations the benign domain admits and refuses to write one that carries the fourth, `model.py::selfcheck` re-asserts it over the calls the driver actually makes, and `idiom.required[0]` pins the two spellings. \u2b50\u2b50 R1h IS A BACKPORT AND THE WORD IS LOAD-BEARING. cf020f133487 -- Marcus Boerger, 2005-03-19, *- Fix #31185* -- is one file, one hunk, three lines: the local goes, `&retval` becomes NULL, the dtor goes. `git apply --check` REFUSES it on pristine 5.0.0 at every context width, because the patch's pre-image carries `SEPARATE_ARG_IF_REF(offset);` and `zval_ptr_dtor(&offset);`, two lines an unrelated later change added. The hand backport reproduces upstream's own diffstat EXACTLY -- 1 insertion, 3 deletions -- so the SEMANTIC change is upstream's and only the context is not. `controls/r1h_backport.py` re-runs both halves on every invocation and takes its verdict from the BYTES rather than from an exit status. It also removes the fault from a REAL PHP 5.0.0: `controls/rebuild_hardened_php.sh` rebuilds the interpreter with the backport applied and re-runs the trigger, which is `PROTOCOL_PHP.md` A3a obligation 5. \u26d4\u26d4\u26d4 AND THE UPSTREAM REPAIR IS INCOMPLETE WITH RESPECT TO THE OBLIGATION, WHICH IS THIS ROW'S SHARPEST RESULT AND IS MEASURED RATHER THAN ARGUED. `zend_std_has_dimension` at `:427-429` has the same defect and cf020f133487 does not touch it. Both C rungs fault on it at `si_addr=0x14`, and `controls/second_limb.py` drives that state through all six rungs and records what each does. `PROTOCOL_PHP.md` C says in terms that an upstream fix is not automatically correct and that measuring one that leaves a reachable fault in the arm it does not guard is a result to report. The SCOPE of the claim is in `../NOTES.md` section 5 and it is narrow: no repair for that limb exists in the 163-patch screened corpus cache on this box, which is a fact about the cache and NOT a claim about php-src's history. \u26a0\u26a0 THE FOUR RUST RUNGS THEREFORE IMPLEMENT `c/kernel_hardened.c` PLUS ONE GUARD UPSTREAM NEVER WROTE, AND THE DIFFERENCE IS A FINDING RATHER THAN A LIBERTY. `Option<&mut Zval>` cannot be released without being opened, so the `None` arm at `:427` has to go somewhere; upstream's C can, and does, simply not have an arm there. The sentence *safe Rust cannot express the `:427` limb* is the ladder result, and `CLAUDE.md` rule 6 makes it a finding and never a problem. On the whole benign domain R1, R1h and R2-R5 coincide exactly, because the extra guard is reachable only from the sentinel state and `inputs/gen.py` refuses a measured corpus that carries one -- so the gate measures one function across six cells and `controls/second_limb.py` measures the one state where they part. \u26a0\u26a0 AND NO RUST RUNG REPRODUCES THE DEFECT, WHICH IS ALSO A FINDING AND NEVER A PROBLEM. In C the bug is an OMISSION -- a test that is not written -- and in Rust reproducing it takes a COMMISSION: an `unwrap` or an `unwrap_unchecked` on an unguarded out-parameter, i.e. an extra operation a reviewer would ask about. `controls/rust_bug.py` builds both of those on purpose and records what each does, so the ladder's *does the defect survive?* column is measured rather than argued. \u2b50 THE R5 OBLIGATION IS `I12/O1` STATED DIRECTLY AND IT COSTS NOTHING TO RUN. `opt_get`'s `requires` is `t.is_some()`, discharged at both compare sites from a NULL test, and `verus.rs`'s `call_method` carries the defect as a CONTRACT: `*final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@))` relates the out-parameter to the SHAPE and to what the method did, and to the status only through a conjunct that says the status alone decides nothing. A caller holding SUCCESS knows nothing about whether the output is there. `controls/negatives.py --emit r1` deletes the `:385` test and that mutant must FAIL to verify. \u26d4\u26d4 THE TIER IS `modelled` AND THE CATALOGUE SAYS `narrowed`; THIS ROW REFUTES ITS OWN MINING-WAVE LABEL, WHICH IS THE SECOND TIME AFTER ph55. MEASURED, `harness-php/provenance.py`: the kernel-overlap heuristic reads **14.63 %** (18 of 123 excerpt lines) against the 25 % a `narrowed` tier leads a reader to expect. Restricted to the FIVE spans the kernel actually lifts and normalised for this row's `ph96_` prefix convention it reads **24.73 %** -- one line short, which is exactly where ph97 sat -- so the heuristic is not simply wrong about the row. But the decisive fact is not the heuristic: `zend_call_function` is a three-hundred-line VM entry of which THREE lines survive (`:595`, `:870-872`, `:873`), and what a call DOES arrives in the record as attacker data rather than being computed. That is a mechanism re-expressed, not a wrapper removed. Two behaviours are also PROJECTED, both non-returns. \u2b50 A tier is a COST and NEVER a FILTER (`PROTOCOL_PHP.md` A1), so the honest lower tier costs this row nothing, and `ph56` is the precedent: it declared `modelled` for re-expressing a compiler. \u26a0 The DEFECT SITE and all four consumer handlers and `zend_call_method` and `_zval_ptr_dtor` and `i_zend_is_true` are upstream's bodies unchanged -- a reviewer who prefers `narrowed` on that ground has a real argument and `../NOTES.md` section 11 gives it the numbers to weigh. \u26a0 THE ROW ALLOCATES NOTHING, which makes `PROTOCOL_PHP.md` B1a's precondition hold at ZERO allocations per call rather than at O(1), so this row's cross-language column carries no allocator caveat at all. The zval a user method returns is `ALLOC_ZVAL`'d in PHP and is a frame object here; that projection, and the projection of `E_CORE_ERROR`'s non-return, are itemised in `provenance.divergences`. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "s_fold": "ph96_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 36
    },
    "twin_obligations": {
      "verus.rs": 40
    },
    "obligations_note": "36 verified / 0 errors, and 40 under `--cfg slb_twin` -- four trusted accessors, therefore four twins; `load_input` and `emit` are I/O and have none. WHAT THE PROOF RESTS ON IS ONE CONJUNCT, AND IT IS `I12/O1` VERBATIM: `opt_get`'s `requires t.is_some()`, discharged at BOTH compare sites from a NULL test -- `zend_object_handlers.c:385` at the read shape, which upstream wrote, and the same spelling at `:427`, which upstream did not. \u26d4\u26d4 AND IT IS **NOT** DISCHARGED FROM THE CALL'S STATUS, WHICH IS THE POINT OF THE ROW. `call_method` returns SUCCESS with `*wrote_out == false` whenever the user method threw, and its `ensures` says exactly that: `*final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@))`. The status's contract is strong enough to prove the out-parameter MAY be absent -- so the test at `zend_interfaces.c:81` cannot discharge the obligation at `:513`, and no amount of strengthening it would, because it is behaving correctly. \u2b50 `controls/negatives.py --emit r1` deletes the `:385` test from this file and that mutant must FAIL to verify; it fails on `opt_get`'s precondition at the read shape. The other five unchecked classes rest on facts that have nothing to do with PHP: a slice index bound, a sub-slice bound, a four-entry table indexed by a residue, and two I/O wrappers. NOTES.md section 8 keeps them apart, because an editor who deleted a NULL test would be removing the precondition of exactly ONE of them.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 36 shipped + 4 for slb_twin_sget, _wsub, _ty_get and _opt_get. \u2b50 THE TABLE ACCESSOR HAS A VERIFYING TWIN ONLY BECAUSE `s_tytab` IS DEFINED AS THE CONSTANT TABLE'S OWN VIEW rather than as a second transcription of its four bytes: Verus does not evaluate the literal and does not need to, so the safe twin satisfies the same `ensures` the trusted body does. A row that had written the four values out again in spec-land would have put them in the TCB. The bytes themselves are checked by `controls/tables.py`, which diffs all three transcriptions (C, Rust, model.py) and carries must-fire negatives. \u2b50\u2b50\u2b50 THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A MEASUREMENT, NOT AN OMISSION -- `controls/rlimit_bisect.sh` has the bisect and NOTES.md section 7 has the table.",
    "items": {
      "verus.rs": {
        "s_tytab": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_shape": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_core": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_wrote": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ty": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_lval": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_slen": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_true": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold_bytes": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold_zval": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_relc": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_rel1": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_rec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_nrel": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ncore": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "sget": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_sget": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "wsub": {
          "external": "verifier::external_body",
          "requires": [
            "o + n <= v@.len()"
          ],
          "ensures": [
            "r@ == v@.subrange(o as int, (o + n) as int)"
          ]
        },
        "slb_twin_wsub": {
          "external": null,
          "requires": [
            "o + n <= v@.len()"
          ],
          "ensures": [
            "r@ == v@.subrange(o as int, (o + n) as int)"
          ]
        },
        "ty_get": {
          "external": "verifier::external_body",
          "requires": [
            "k < 4"
          ],
          "ensures": [
            "r == s_tytab(k as int)"
          ]
        },
        "slb_twin_ty_get": {
          "external": null,
          "requires": [
            "k < 4"
          ],
          "ensures": [
            "r == s_tytab(k as int)"
          ]
        },
        "opt_get": {
          "external": "verifier::external_body",
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "*r == *t.unwrap()"
          ]
        },
        "slb_twin_opt_get": {
          "external": null,
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "*r == *t.unwrap()"
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
        "zval_ptr_dtor": {
          "external": null,
          "requires": [
            "old(z).refcount >= 1"
          ],
          "ensures": [
            "old(z).refcount == 1 ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "old(z).refcount != 1 ==> *final(n_rel) == *old(n_rel)"
          ]
        },
        "is_true": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "z.ty == s_ty(b@)",
            "z.lval == s_lval(b@)",
            "z.slen == s_slen(b@)"
          ],
          "ensures": [
            "r == s_true(b@)"
          ]
        },
        "fold_bytes": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "n <= STRMAX"
          ],
          "ensures": [
            "r == s_fold_bytes(acc, b@, 0, n as int)"
          ]
        },
        "fold_zval": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "z.ty == s_ty(b@)",
            "z.lval == s_lval(b@)",
            "z.slen == s_slen(b@)",
            "z.slen <= STRMAX"
          ],
          "ensures": [
            "r == s_fold_zval(acc, b@)"
          ]
        },
        "call_method": {
          "external": null,
          "requires": [
            "b@.len() == REC"
          ],
          "ensures": [
            "r == s_core(b@)",
            "*final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@))",
            "s_relc(b@, want_output) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "!s_relc(b@, want_output) ==> *final(n_rel) == *old(n_rel)",
            "*final(wrote_out) ==> final(slot).ty == s_ty(b@)",
            "*final(wrote_out) ==> final(slot).lval == s_lval(b@)",
            "*final(wrote_out) ==> final(slot).slen == s_slen(b@)",
            "*final(wrote_out) ==> final(slot).slen <= STRMAX",
            "*final(wrote_out) ==> final(slot).refcount == 1"
          ]
        },
        "read_dimension": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "s_shape(b@) == 0"
          ],
          "ensures": [
            "r == s_step(b@, acc)",
            "s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "!s_rel1(b@) ==> *final(n_rel) == *old(n_rel)",
            "s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1)",
            "!s_core(b@) ==> *final(n_core) == *old(n_core)"
          ]
        },
        "write_dimension": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "s_shape(b@) == 1"
          ],
          "ensures": [
            "r == s_step(b@, acc)",
            "s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "!s_rel1(b@) ==> *final(n_rel) == *old(n_rel)",
            "s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1)",
            "!s_core(b@) ==> *final(n_core) == *old(n_core)"
          ]
        },
        "has_dimension": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "s_shape(b@) == 2"
          ],
          "ensures": [
            "r == s_step(b@, acc)",
            "s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "!s_rel1(b@) ==> *final(n_rel) == *old(n_rel)",
            "s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1)",
            "!s_core(b@) ==> *final(n_core) == *old(n_core)"
          ]
        },
        "unset_dimension": {
          "external": null,
          "requires": [
            "b@.len() == REC",
            "s_shape(b@) == 3"
          ],
          "ensures": [
            "r == s_step(b@, acc)",
            "s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1)",
            "!s_rel1(b@) ==> *final(n_rel) == *old(n_rel)",
            "s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1)",
            "!s_core(b@) ==> *final(n_core) == *old(n_core)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()"
          ],
          "ensures": [
            "r == s_fold(buf@, off as int, len as int)"
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
        "sget": "`v: &[u8]` is a SLICE and its length is a run-time fact, so the `requires` has to name it -- `i < v@.len()` -- and that is the whole of what makes the unchecked read sound. There is no second parameter. \u26a0 The call sites bound `i` differently: inside the record decode it is a literal under 16 and the caller's `b@.len() == REC` supplies the rest; inside the value fold it is the loop's own cursor plus `SOFF`, bounded by `n <= STRMAX` and by `REC == SOFF + STRMAX`.",
        "wsub": "`v: &[u8]` again, and the constrained quantities are BOTH endpoints at once: `o + n <= v@.len()` is one conjunct and it bounds the pair, which is what a sub-slice needs and what an index bound would not give. \u26a0 The `ensures` names the whole result -- the subrange, not merely its length -- because a body that returned a correctly-sized slice of the WRONG bytes would satisfy a length-only contract and change every answer downstream.",
        "ty_get": "`k: usize` is the only parameter and it IS constrained, by `k < 4`. \u2b50 What is worth reading here is the `ensures`: `r == s_tytab(k as int)`, where `s_tytab` is DEFINED AS THE CONSTANT TABLE'S OWN VIEW. So the contract does not assert anything about the table's four bytes -- it says the accessor returns entry `k` of it, whatever it is -- and that is why the verified twin can meet the same contract with a bounds-checked index. A row that had transcribed the values into spec-land instead would have put them in the TCB.",
        "opt_get": "\u2b50\u2b50 THE ROW'S OWN TRUSTED ITEM, AND ITS PARAMETER IS THE WHOLE STORY. `t: Option<&mut Zval>` is a value with exactly two shapes and the `requires` names the one the body assumes: `t.is_some()`. There is no second parameter to leave unconstrained -- the shape this stage exists to catch cannot arise here, because the ONLY thing that can make `t.unwrap_unchecked()` undefined is `t` itself. \u26a0 What makes the entry worth reading is WHERE the precondition comes from: not from arithmetic, not from the caller's convenience, and NOT from the call's status -- whose contract proves the opposite, that the output may be absent -- but from a NULL test at each of the two sites. `controls/negatives.py --emit r1` deletes one and that mutant must FAIL to verify."
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
      "if stride_w >= 16 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph96's two probe shapes have different work per call (118 and 1004 window bytes, i.e. 7 and 62 CALL records) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. \u26a0 `work_per_call` is the WINDOW IN BYTES and the record count is `stride / 16` truncated, so the work really does scale with the denominator rather than merely being labelled by it. \u26a0\u26a0 THE PER-RECORD WORK IS NOT CONSTANT AND THE ROW SAYS SO RATHER THAN HIDING IT: a record whose call fails takes one branch, one whose read_dimension returns a ten-byte string folds ten bytes, and one whose unset_dimension succeeds does a refcount decrement and nothing else. NOTES.md section 9 decomposes the marginal instead of presenting it as a per-byte rate."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "norel",
      "why": "R4 AND R5 ARE THE SAME MACHINE CODE AT BOTH OPTIMISATION LEVELS. Measured, O3 isolated: both `kernel` symbols are 271 instructions (269 excluding padding, 978 bytes), `md5_fn_norel` and `md5_norm` identical, `asm.py::identity_level` returns `norel`. At O0 isolated both are 644 instructions and 3377 bytes with the same verdict. \u26a0 THE PIN IS `norel` AT BOTH LEVELS AND NOT `exact`, DELIBERATELY: `exact` compares raw bytes including relocations, `kernel_fingerprint` is PATH-SENSITIVE and has fired live in both directions on this project (F101, item 109), and a pin that a re-measure under a longer build root could break is a pin that reports an environment change as a defect. \u26a0\u26a0 AND ph97's OWN LESSON IS APPLIED HERE RATHER THAN RE-LEARNED: that row was `exact` at O3 and `differ` at O0 as first written, so the O3 reading alone would have certified an equivalence that was false one optimisation level down. This row was checked at BOTH levels before the pin was written and agreed at both. \u25b6 A `whole`-mode pin is NOT claimed: the gate compares the `isolated` cells, and in `whole` mode the kernel is inlined into `main` and there is no common symbol to compare. \u2b50\u2b50 AND MIRI IS STILL REQUIRED: `norel` counts as the same machine code, so `.memory/02-bench-rules.md`'s non-waivable clause does not fire on this pin -- but the row has FOUR trusted accessors, one of which is `Option::unwrap_unchecked` on the row's own out-parameter, and that is the clause that does. `miri.required: true` is a declaration about the trusted surface, not about this entry. \u26a0 The figures here are from results-php/gate/ph96-outparam-unwritten.json and results-php/ph96-outparam-unwritten.json; PROTOCOL.md rule 6's addendum says to re-read this entry against THOSE records rather than trusting the hash."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph96 has FOUR. \u2b50 AND ONE OF THE FOUR IS NOT AN INDEX AT ALL: `opt_get` is `Option::unwrap_unchecked` on the row's own out-parameter, whose misuse is not an out-of-bounds access but a read through a reference the niche says is absent -- which on THIS row is the defect itself rather than a neighbouring hazard. Miri is the only detector in this tree that sees that class.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph96's cost is 4 x (one window of 7 or 62 call records, each decoded and run through at most a ten-byte fold), i.e. four orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_object_handlers.c",
    "c_lines": [
      506,
      517
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_object_handlers.c | sed -n '506,517p'",
    "extract_sha256": "31d61d0348c91b049670c1089dbb4e822f85513845f34979c1d88b48fe5774f2",
    "extra_spans": [
      {
        "c_file": "Zend/zend_object_handlers.c",
        "c_lines": [
          378,
          434
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_object_handlers.c | sed -n '378,434p'",
        "extract_sha256": "55ed48b24e609d4ea3f41d13a18e6a474946495976bd1a6d65011783c35cdb1b",
        "why": "\u2b50\u2b50\u2b50 THE 2x2, AND IT IS THE REASON THE ROW MODELS THE CONTRACT RATHER THAN THE SITE. Three more handlers call the SAME helper: `:384` `zend_std_read_dimension` takes the output contract and GUARDS it at `:385` with `if (!retval)`, two lines after the call; `:413` `zend_std_write_dimension` takes the NO-OUTPUT contract by passing NULL; `:427` `zend_std_has_dimension` takes the output contract and guards nothing, dereferencing the sentinel TWICE -- `:428 i_zend_is_true(retval)` at offset 0x14 and `:429 zval_ptr_dtor(&retval)` at 0x10. Both correct spellings and both wrong spellings are in one file by one author. \u26a0 `:393 retval->refcount--` is inside this span and is upstream's `Undo PZVAL_LOCK`; it is why the read shape does NOT count as a release."
      },
      {
        "c_file": "Zend/zend_interfaces.c",
        "c_lines": [
          30,
          96
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_interfaces.c | sed -n '30,96p'",
        "extract_sha256": "2546d7165bfd2a87eee4c9cf73403afb93ddf1807abe9570f81da21fa9a0b9ae",
        "why": "\u2b50\u2b50 THE HELPER, AND IT OFFERS TWO CONTRACTS, ONE OF WHICH CANNOT BE MISUSED. `:48 fci.retval_ptr_ptr = retval_ptr_ptr ? retval_ptr_ptr : &retval;` selects between them; `:81-87` TESTS THE STATUS and raises E_CORE_ERROR, which does not return, so `I12/O1`'s *status code* clause is discharged HERE; and `:88-93` disposes of the value on the no-output path behind its own `if (retval)` NULL test at `:89` -- **the very test `:513` omits, written by the same hand, in the function being called.** cf020f133487 moves the unset site from `:94`'s contract to `:88`'s."
      },
      {
        "c_file": "Zend/zend_execute_API.c",
        "c_lines": [
          584,
          600
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute_API.c | sed -n '584,600p'",
        "extract_sha256": "ba828e0307f7b0118a92f61b8062f1c00a7469c28129d8007e0044b6ac4cbec5",
        "why": "\u2b50\u2b50\u2b50 THE SENTINEL AND THE COMMENT THAT NAMES THE HAZARD. `:592-594` is the author's own *we may return SUCCESS, and yet retval may be uninitialized, if there was an exception*, and `:595 *fci->retval_ptr_ptr = NULL;` is the defensive store that makes the hazard DETECTABLE. \u26a0 IT IS QUOTED AS EVIDENCE OF INTENT AND NEVER AS PROOF OF RUNTIME BEHAVIOUR: what makes the sentinel guaranteed is that `:595` precedes every FAILURE return in the function, which is a fact about the line numbers, and `../NOTES.md` section 2 has the behaviour measured instead."
      },
      {
        "c_file": "Zend/zend_execute_API.c",
        "c_lines": [
          862,
          874
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute_API.c | sed -n '862,874p'",
        "extract_sha256": "17e12488325babc41b31db80446c96d37742f4cc9dbc1225149501ec28e1a1c4",
        "why": "\u26d4 AND IT RETURNS SUCCESS ANYWAY. `:870-872` re-throws the pending exception through `zend_throw_exception_internal` and `:873` is an unconditional `return SUCCESS`. So the status the caller tests says nothing about whether the method completed, which is what makes the out-parameter the only thing that could have said so."
      },
      {
        "c_file": "Zend/zend_execute_API.c",
        "c_lines": [
          384,
          396
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute_API.c | sed -n '384,396p'",
        "extract_sha256": "52ff5853dba6612bc943f028c902053fb3bee0d616a3c3427f34c75071eca903",
        "why": "\u26d4\u26d4 THE DEREFERENCE, AND IT IS THE FIRST STATEMENT. `_zval_ptr_dtor` opens with `(*zval_ptr)->refcount--` at `:389` -- no NULL test, no assert, nothing. `:390-395` is the release itself, which the row PROJECTS onto a tally because it models no allocator."
      },
      {
        "c_file": "Zend/zend_execute.h",
        "c_lines": [
          68,
          112
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.h | sed -n '68,112p'",
        "extract_sha256": "fe77a2d8661f1776da408a6b91fd70757c4fade682da7af09cdfcbfa7877b80d",
        "why": "\u26a0 THE SECOND LIMB'S DEREFERENCE. `i_zend_is_true`'s first statement is `switch (op->type)` at `:72`, which reads offset 0x14 -- the address the 5.0.0 CLI faults at when `offsetExists` throws. The span is lifted because the kernel's `ph96_is_true` is this switch narrowed to four tags, and because `:85-90`'s TWO conjuncts (`len == 0` OR `len == 1 && val[0] == '0'`) are what `inputs/gen.py` asserts the corpus reaches all three arms of."
      },
      {
        "c_file": "Zend/zend.h",
        "c_lines": [
          270,
          293
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.h | sed -n '270,293p'",
        "extract_sha256": "f22ab43a740a583cfc2d2f34294fc87b905a8ddcf2be482b3802b5f1b622b28a",
        "why": "\u2b50\u2b50 THE LAYOUT THAT FIXES BOTH FAULT ADDRESSES, AND IT IS WHY THIS ROW'S `si_addr` IS A STRUCT OFFSET RATHER THAN ZERO. `:275-284`'s `zvalue_value` union is 16 bytes on LP64 because `:270-273`'s `zend_object_value` is `{zend_object_handle handle; zend_object_handlers *handlers;}`, so `:290 zend_uint refcount` lands at 16 = 0x10 and `:291 zend_uchar type` at 20 = 0x14. `c/kernel.c` holds its own zval to exactly those offsets with negative-array-size assertions, so a change in the extraction fails the BUILD rather than moving a measured address."
      }
    ],
    "extra_spans_note": "THE ROW LIFTS EIGHT SPANS AND ALL EIGHT ARE PINNED. `provenance.c_lines` names the defect site (`zend_std_unset_dimension`, zend_object_handlers.c:506-517, which is the catalogue's own citation); the seven extras are the three sibling handlers that make the 2x2 (:378-434), the helper that offers both contracts and tests the status (zend_interfaces.c:30-96), the two zend_execute_API.c spans that write the sentinel and return SUCCESS anyway (:584-600 and :862-874), the releaser whose first statement is the dereference (:384-396), i_zend_is_true, whose first statement is the OTHER dereference (zend_execute.h:68-112), and the zval layout that fixes both fault addresses (zend.h:270-293). \u26a0 FIVE OF THE EIGHT ARE THE MECHANISM RATHER THAN CONTEXT: a row that pinned only the defect site would certify twelve lines in which nothing is visibly wrong -- the sentinel, the SUCCESS, the status test and the dereference are all somewhere else -- and a reader would have to take *the helper leaves a NULL* on trust. \u26a0 What is NOT pinned is the executor itself: `zend_call_function`'s VM entry, the `zend_fcall_info` struct and the class-entry lookup are DELETED, and the deletions are itemised in `divergences` rather than hidden behind a span.",
    "tier": "modelled",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "zend_object_handlers.c:506, :420, :403, :378; zend_interfaces.c:32",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "`zval` becomes a five-field record and `zval **` becomes a pointer to one",
        "kind": "substitution",
        "where": "zend.h:287-293",
        "why": "the row reads exactly four things out of a zval -- `Z_TYPE_P`, `Z_LVAL_P`, `Z_STRVAL_P`, `Z_STRLEN_P` -- plus `refcount` and `is_ref`, which are the fields `_zval_ptr_dtor` writes, and this record carries those six and nothing else. \u2b50 THE FIELD OFFSETS ARE PRESERVED AND ASSERTED: `c/kernel.c` carries negative-array-size assertions holding `sizeof(zvalue_value) == 16`, `offsetof(refcount) == 0x10` and `offsetof(type) == 0x14`, which is what upstream's union gives on LP64, so the kernel faults at the same addresses the 5.0.0 CLI does. The union's `ht` member is folded into `obj` because both are pointers of the same width and neither is read. Demonstrated behaviour-preserving by `controls/fault_addr.py` with a must-fire control. No semantics."
      },
      {
        "what": "the `zend_fcall_info` struct and the VM entry become three arguments",
        "kind": "deletion",
        "where": "zend_execute_API.c:537-591, :596-861",
        "why": "`zend_call_function` sets up an `execute_data`, looks the method up in the class's function table, pushes an argument stack and runs the VM. NONE of that is the mechanism: the mechanism is `:595`, `:870-873` and the relationship between them, and the row keeps all three. What a call DOES is attacker data in this row and arrives in the record rather than being computed, which is the same narrowing every php row makes at the executor boundary (.memory-php/01-extraction.md prices extraction at the DEFECT site). No semantics."
      },
      {
        "what": "`E_CORE_ERROR` at zend_interfaces.c:86 becomes a fold tag",
        "kind": "projection",
        "where": "zend_interfaces.c:81-87",
        "why": "`zend_error(E_CORE_ERROR, ...)` terminates the request and does not return, and a `u64` kernel driven thousands of times has no way to terminate that the driver loop would survive. The row PROJECTS it onto *this call contributes a CORE tag and the consumer does not run*, which is the behaviour the status test buys and is strictly NARROWER than the real one: every behaviour it stands for is one in which the process stops. Same shape as `common-php/emalloc_shim.h`'s NULL arm for PHP's `exit(1)`. No semantics on the extracted domain."
      },
      {
        "what": "the `E_ERROR` arm at zend_object_handlers.c:387 becomes a fold tag",
        "kind": "projection",
        "where": "zend_object_handlers.c:386-389",
        "why": "`if (!EG(exception)) { zend_error(E_ERROR, \"Undefined offset...\"); }` then `return 0`. In the state this row is about the exception IS set -- it is what put the sentinel there -- so the E_ERROR is NOT raised and the handler returns 0 quietly; the kernel folds a distinct tag for that. The other arm, where no exception is pending, is a non-return and is projected the same way as the entry above. No semantics on the extracted domain."
      },
      {
        "what": "`ALLOC_ZVAL` / `zval_dtor` / `safe_free_zval_ptr` become a release tally",
        "kind": "projection",
        "where": "zend_execute_API.c:390-392",
        "why": "the zval a user method returns is heap-allocated in PHP and freed when the refcount reaches zero. The row models no allocator: the zval is a frame object and the free becomes an increment of the release count that the kernel's `u64` carries. That is what keeps allocations per kernel call at ZERO and PROTOCOL_PHP.md B1a's precondition satisfied with room to spare, and it is what makes the release count -- which is the quantity I16/O2 is about -- visible in the checksum the gate compares across six rungs rather than only in a sanitizer. No semantics on the extracted domain."
      },
      {
        "what": "IS_DOUBLE, IS_ARRAY, IS_OBJECT and IS_RESOURCE fold away",
        "kind": "deletion",
        "where": "zend_execute.h:81-106",
        "why": "`i_zend_is_true` sorts eight type tags into five outcomes, and the row keeps one representative of each that does not need a container or a handler table: IS_NULL (always false), IS_LONG and IS_BOOL (the shared `op->value.lval ? 1 : 0` arm) and IS_STRING (the two-conjunct arm). IS_DOUBLE is the same shape as the LONG arm one type over, and IS_ARRAY / IS_OBJECT / IS_RESOURCE need a HashTable or an object handler table, which is a container and not the defect. Upstream's own numbering is kept for the four that remain, so the switch really is upstream's switch. No semantics on the extracted domain."
      },
      {
        "what": "the returned zval becomes a fold of its bytes rather than a value",
        "kind": "substitution",
        "where": "zend_object_handlers.c:395",
        "why": "`zend_std_read_dimension` RETURNS the zval to the VM, which goes on to read it. A kernel whose signature is `-> u64` cannot return a zval, so the row folds what the VM would read: the type tag, and for a string its whole `Z_STRLEN` bytes. The fold is implemented IN THE KERNEL rather than by a library call, which is a MEASUREMENT decision as much as a fidelity one -- family A1 is symbol-scoped and structurally excludes callee work, and on ph97 the same substitution moved `inside_share` by 34 percentage points and flipped the sign of the measured difference. Demonstrated behaviour-preserving by model.py's three independent implementations agreeing on every window of every input AND on synthetic records spanning the whole cross product, and by the gate's stage-3 cross-rung checksum. No semantics."
      },
      {
        "what": "the `:385` guard is ADDED at `:427` in the four Rust rungs",
        "kind": "substitution",
        "where": "zend_object_handlers.c:427-428",
        "why": "\u26d4\u26d4 THIS IS THE ONE DIVERGENCE THAT IS NOT PRESENT IN EITHER C RUNG, AND IT IS DECLARED RATHER THAN HIDDEN. Upstream goes straight from `:427` to `:428 i_zend_is_true(retval)`, and cf020f133487 does not change that; both C rungs therefore fault on the sentinel at that site. In Rust the out-parameter is an `Option<&mut Zval>` and cannot be released without being opened, so the `None` arm has to go somewhere -- the four Rust rungs take `:385`'s own spelling, which is upstream's, at a site upstream did not use it. On the whole BENIGN domain the six rungs coincide exactly, because the arm is reachable only from the sentinel state and `inputs/gen.py` refuses a measured corpus that carries one; `controls/second_limb.py` drives that one state through all six and records what each does. No semantics on the extracted domain, and a FINDING off it."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. \u2b50 THERE ARE TWO PROJECTIONS ON THIS ROW AND BOTH ARE NON-RETURNS: `E_CORE_ERROR` at zend_interfaces.c:86 and the `E_ERROR` arm at zend_object_handlers.c:387 terminate the request in PHP, and a `u64` kernel has no way to terminate that the driver loop would survive -- so each becomes a distinct fold tag and the consumer does not run. That is the same shape `common-php/emalloc_shim.h` uses for PHP's `exit(1)`, and it NARROWS rather than widens: every behaviour it stands for is one in which the process stops. PROTOCOL_PHP.md A1 requires a substitution in a non-`modelled` tier to be (a) itemised with a line citation, (b) given a `why` ending in 'no semantics' and (c) DEMONSTRATED behaviour-preserving rather than asserted; the substitutions here carry (c) by measurement -- the type table by `controls/tables.py`, the zval layout by `controls/fault_addr.py` and by the build-time offset assertions in `c/kernel.c`, and the rest by model.py's three independent implementations plus the gate's own stage-3 cross-rung checksum on every input.",
    "root_cause_ids": [
      "out-parameter-left-at-the-callees-own-NULL-sentinel-by-a-call-that-returns-SUCCESS-then-released-untested"
    ],
    "cwe": "CWE-476",
    "cwe_note": "index.csv records CWE-476 (NULL pointer dereference) for CRASH-061 and this row reproduces exactly that, MEASURED ON BOTH SIDES AND AT THE SAME ADDRESS. A PHP 5.0.0 CLI on this box under `.tasks-php/probes/segaddr.c`, driven by `.tasks-php/probes/ph96_arrayaccess_matrix.sh`, answers a throwing `offsetUnset` with `SIG11 si_code=1 si_addr=0x10` and exit 139 while a script in which nothing throws exits 0; `c/kernel.c` on `inputs/adversarial-unset.bin` gives the same `si_addr=0x10` under the same shim. \u2b50 `si_addr` is `offsetof(zval, refcount)` rather than zero, because `refcount` is not the first field of a zval: Zend/zend.h:287-293 puts the 16-byte `zvalue_value` union in front of it on LP64. `c/kernel.c` asserts that offset at BUILD time. ../NOTES.md sections 2 and 3 have every run and the build each was taken on.",
    "fix_commit": "cf020f133487d36a8b1d9cfd16ec456f7f07952e",
    "fix_commit_note": "\u26a0 THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE AND THE ROW USES ITS SHORT FORM EVERYWHERE. `cf020f133487` -- Marcus Boerger, 2005-03-19, '- Fix #31185' -- is ONE FILE, ONE HUNK, THREE LINES. The patch bytes are at controls/cf020f133487.patch. \u26d4\u26d4 IT BINDS BUT IT DOES NOT APPLY, AND `c/kernel_hardened.c` IS THEREFORE DECLARED A BACKPORT RATHER THAN AN APPLICATION. `git apply --check` returns rc=1 on the pristine 5.0.0 file at the default context width and at -C1, -C0 and -3, because the patch's pre-image carries `SEPARATE_ARG_IF_REF(offset);` and `zval_ptr_dtor(&offset);` -- two context lines an unrelated later change added. \u2705 The three-line hand backport reproduces upstream's own diffstat EXACTLY: `Zend/zend_object_handlers.c | 4 +---`, `1 file changed, 1 insertion(+), 3 deletions(-)`, which is the evidence that the semantic change is upstream's and only the context is not. `controls/r1h_backport.py` RUNS the refusal and the backport on every invocation and reads the VERDICT OUT OF THE BYTES rather than out of the exit status, because `git apply --check` has lied on this project before when the scratch path was gitignored (ph55 NOTES section 5). \u26a0 The patch BINDS: its `From` line is `cf020f133487d36a8b1d9cfd16ec456f7f07952e` and its filename is the same prefix, so it is not one of F115's three mis-bound cached patches. \u26a0 `preimage_screen.py --row ph96` returns CANDIDATE with 1 record and 0 NOT-THE-REPAIR exclusions, and CANDIDATE is the screen's POSITIVE label, which under PROTOCOL_PHP.md C says nothing either way. \u2b50\u2b50 THE FIX WIDENS THE BENIGN DOMAIN RATHER THAN NARROWING IT: on every input the measured corpus makes, the two C rungs agree bit for bit, and they diverge on exactly one input -- the one R1 faults on -- so check.py stage 7h has nothing to refuse. `controls/widened_domain.py` measures that rather than asserting it. \u26d4\u26d4\u26d4 AND IT IS INCOMPLETE WITH RESPECT TO THE OBLIGATION: `zend_std_has_dimension` at :427-429 has the same defect and this commit does not touch it, so both C rungs fault on that limb at si_addr=0x14. controls/second_limb.py measures it. NO repair for that limb exists in the 163-patch screened corpus cache on this box, which is a result about THE CACHE and not a claim about php-src's history. \u26a0 UNVERIFIED IN THIS ROW: whether cf020f133487 is the FIRST commit to close the unset site and whether any 5.0.x branch backport preceded it. PROTOCOL_PHP.md F5(iii) asks for confirmation against the tags and this row confirms the SITE and the DIRECTION from the patch bytes rather than the exact commit.",
    "invariant": "I12",
    "obligation": "O1",
    "invariant_note": "The catalogue row says `I12/O1 + I16/O2` and this block names `I12/O1`, which is the one the R5 proof states. **I12** is *a fallible call's outcome must be tested before its result is used* and its **O1** is 'a NULL return, sentinel, status code, **or NULL-able out-parameter** must be tested'. \u2b50\u2b50 THE ROW IS ABOUT THE LAST OF THOSE FOUR AND NOT ABOUT THE THIRD, AND THE DISTINCTION IS THE WHOLE ROW: the STATUS CODE **is** tested, at zend_interfaces.c:81, and raising E_CORE_ERROR there is correct. What is never tested is the NULL-able out-parameter, which the callee set to NULL on purpose at zend_execute_API.c:595 and documented at :592-594. \u26a0 **I16/O2** -- *the outputs of an aborted call must not be ... destroyed* -- is the `zval_ptr_dtor` half and the kernel's release tally is the quantity it is about; it is carried in the fold rather than in this field, because `obligation` is a single value and the proof states O1. \u26a0 What the row does NOT claim is ph60's *a fallible call's failure not tested*: the call SUCCEEDS here. That is the distinction the catalogue's own risk note on ph60 draws, and it is why CRASH-061 was split out of it. Blind-labelled by the corpus (`paper/invariants-list.md`) and carried across unmodified.",
    "echoes": [
      "p42"
    ],
    "echoes_note": "The catalogue's `echoes` column for ph96 reads `p42` with a dagger, and this block carries it. \u26a0 It is a cross-reference and NEVER a filter (PLAN_PHP.md 3.1, DP-03): `patterns-php/` is fresh and *that is p42's mechanism* may not refuse a candidate. \u26a0 The nearest neighbour anywhere is `ph97`, one row over in the same family: SAME obligation (I12), same *the guard is present and it passes* shape, and a DIFFERENT reason the output is missing -- there the parser never writes the optional argument and the guard answers a question about TYPES, here the callee writes a NULL into the out-parameter on purpose and the guard answers a question about STATUS. The unchecked predicate differs (*was it supplied?* against *was it written?*) and so does the upstream repair: ph97's TESTS the pointer, ph96's REMOVES the output.",
    "uses_allocator": false,
    "uses_allocator_why": "the kernel allocates NOTHING. The zval a user method returns is a frame object, the four-entry type table is `static const`, and no rung calls `emalloc`, `efree`, `malloc` or `free` -- so allocations per kernel call are ZERO, not merely O(1), and PROTOCOL_PHP.md B1a's precondition holds with room to spare. \u2b50 That is why this row's cross-language column carries NO allocator caveat: unlike ph64 there is no allocator term in it at all. \u26a0 PHP's own `ALLOC_ZVAL` / `FREE_ZVAL` around the returned value are PROJECTED onto the release tally and the projection is itemised in `divergences`; modelling them would make this the only allocating row in a family whose precondition it otherwise satisfies at zero. \u26a0 DECLARED, NEVER DETECTED (TASK_PHP_008 0.4) -- nothing reads this field and no verdict depends on it. The row still carries `c/emalloc_shim.h` as a symlink, because that rule is UNCONDITIONAL."
  }
}
```
