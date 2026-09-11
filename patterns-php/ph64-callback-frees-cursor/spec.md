# ph64 — `zend_llist_apply`: a cursor the callback is allowed to free

**PHP 5.0.0, `Zend/zend_llist.c:186-193`, corpus row CRASH-086, tier
`narrowed`.** A tick function that calls `unregister_tick_function()` on itself
frees the very element `zend_llist_apply`'s `for` header is about to read.
`:190` advances the cursor **after** `func` has returned, and `func` here runs
userland PHP.

⭐ **The same file has the defence fifteen lines above.**
`zend_llist_apply_with_del` (`:171-183`) takes the same caller-supplied `func`
and caches `next = element->next` at `:177` *before* calling it. Three of
`zend_llist.c`'s six callback walks cache the successor and three advance in the
`for` header — and the three that do not are the three this defect can reach.
That asymmetry is the row; see `NOTES.md` §5.

⚠ **R1h is `562f886ecb14` (Antony Dovgal, 2007-04-10) whole and unmodified, and
it is in a THIRD function** — `user_tick_function_compare`, which is neither the
walk that faults nor the statement the corpus cites. It makes the free
unreachable rather than making either dereference safe. `NOTES.md` §4.

⚠⚠ **The corpus's proposed oracle — a fold of the ids the walk invoked —
measures nothing on this row**, because a freed 39-byte element goes into
`AG(cache)[5]` with its payload untouched. `controls/oracle.py` measures that
(213 of 213 windows, fold bit-identical) and `NOTES.md` §6 explains why the u64
carries `l->count`, the dtor count, the refusal count and the allocator tally as
well.

The machine-readable contract follows.
`harness-php/gate.py ph64-callback-frees-cursor` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "24 <= len",
    "len <= 268435456"
  ],
  "ensures": [
    "result == llist_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (llist_fold). ⚠⚠ `model.py`'s `llist_fold` IS NOT `verus.rs`'s, AND THAT IS THE POINT: verus.rs defines it as a step-by-step recursion over the SAME arena the exec code mutates (`s_reg`/`s_del`/`s_visit`/`s_apply`/`s_destroy`, fuel-bounded), while model.py defines it as a CLOSED FORM -- the visited set, the deletion schedule and all four allocator counters derived arithmetically, with no list, no nodes, no cursor and no event replay. model.py's OTHER implementation, `_simulate`, is a structural doubly-linked-list simulation driven at BOTH rungs. Three spellings, and `selfcheck()` drives the first two against each other on the shipped inputs AND on synthetic windows spanning every (list length x trigger x mode x post x reuse) combination up to eight entries. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. `controls/differential.py` closes the third edge -- the SHIPPED C against both -- over 2 592 windows.",
  "idiom": {
    "required": [
      {
        "c": "`for (element=l->head; element; element=element->next)` at zend_llist.c:190 -- the cursor is advanced in the for header, which runs AFTER func returns. ⚠ THE RUST KEY PINS THE CURSOR'S NAME AND NOT THE EXPRESSION, and that is deliberate: the four Rust rungs read the successor three different ways (R2 self.arena[e as usize].next, R3 self.arena[e].next, R4/R5 nnext(&self.arena, e)) because that difference IS the R2/R3/R4 ladder, and no single expression is common to all four. What IS common is that the variable is called `element`, as in the C, and that it is assigned AFTER the callback returns -- and the ORDER lives in this English, which is what the named-spelling standard says about polarity and scope.",
        "rust": "`element`"
      },
      {
        "c": "`tick_fe->calling = 0`",
        "rust": "`calling`"
      },
      {
        "c": "`pefree((current), (l)->persistent)`",
        "rust": "`self.al.free(REQ_ELEM)`"
      },
      "R1h is 562f886ecb14 WHOLE AND UNMODIFIED -- one hunk, 7 added / 2 deleted lines, in user_tick_function_compare -- and R2-R5 implement the same function, because on the tick list that fix is COMPLETE: zend_llist_apply advances only after func returns and user_tick_function_call holds the calling flag set for exactly the duration of that call, so every element a live cursor points at is in the set the guard refuses to free, and every element the guard does not protect has both neighbours' links repaired by DEL_LLIST_ELEMENT. ⚠ THE ONE PROJECTION THAT CHANGES SOMETHING, stated here rather than in a footnote: the hunk's refusal path calls php_error_docref with E_WARNING, which reaches zend_error's user-handler arm -- arbitrary userland -- from inside zend_llist_del_element's own walk, which holds current and next. This row PROJECTS that to a refusal counter, so the row cannot see it. TASK_PHP_031_REPORT section 4.3 states it as a STATIC READING and NOT MEASURED, master later upgraded the call to zend_throw_error (which cannot run userland), and NOTES.md section 4d carries it as an OPEN ITEM rather than a finding. ⚠ WHAT WAS CHOSEN AGAINST: the next-caching idiom zend_llist_apply_with_del already uses fifteen lines above. It is NOT R1h and PROTOCOL_PHP.md section C is why -- R1h is the real fix_commit, full stop -- and controls/next_cache.py measures it as a control: it removes every wild walk on the SELF shape (189 of 189), LEAVES the write at basic_functions.c:2135 landing in the recycled block (189 of 189), does not restore the answer (189 of 189), and ADDS a use-after-free of the cursor's SUCCESSOR on the AHEAD shape (196 of 196) that the plain walk does not have. The two hardenings are NOT ordered by strength; upstream picked the one that dominates. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it.",
      "the WINDOW LAYOUT is structure and not data: four u32 head words (nent, trig, mode, post) then one 4-byte slot per registered tick function, and entry i's NAME is the little-endian id followed by slot i. NO BACKTICKED SPELLING: the C assembles the eight bytes into an 8-byte emalloc block (which is what PHP's safe_emalloc of one zval pointer is), R2 carries them as a byte array and R3/R4/R5 as the 64-bit value the comparison is -- three legitimate spellings of one fact. ⚠ The id half is what makes names UNIQUE BY CONSTRUCTION, so \"unregister my own name\" cannot silently mean somebody else's; that is exactly how TASK_PHP_031's own first oracle probe was wrong (its report section 8.8) and it is closed here by construction rather than by an assertion."
    ],
    "forbidden": [
      {
        "c": "`next = element->next;` -- zend_llist_apply_with_del:177's idiom, transplanted into the walk at zend_llist.c:190. It is a REAL upstream hardening from the SAME FILE, it is not this row's fix_commit, and it computes a DIFFERENT FUNCTION: controls/next_cache.py measures it removing 189 wild walks and ADDING 196 visits of a freed successor. A rung that acquired it would delete the row's primary span.",
        "rust": "`let nxt_cached = self.arena[e].next;` -- zend_llist_apply_with_del:177's idiom, transplanted. It is a REAL upstream hardening from the SAME FILE, it is not this row's fix_commit, and it computes a DIFFERENT FUNCTION: controls/next_cache.py measures it removing 189 wild walks and ADDING 196 visits of a freed successor. A rung that acquired it would delete the row's primary span."
      },
      "`tick_fe2->calling` -- reading the SEARCH KEY's flag instead of the LIST ELEMENT's. PHP_FUNCTION(unregister_tick_function) never sets it (basic_functions.c:2843-2861), so the guard would be DEAD and R1h would return R1's u64 on every trigger window; controls/predicate.py measures exactly that, 189 of 189. It is pinned absent because 562f886ecb14 is one word away from being a no-op and the word is which argument it reads.",
      {
        "c": "`for (i = 0; i < l->count; i++)` -- walking the list by INDEX instead of by link. It computes the same u64 on this row, because zend_llist_add_element appends at the tail and DEL_LLIST_ELEMENT only ever short-circuits prev to next, so position order and link order agree. It is forbidden because it is a DIFFERENT ALGORITHM: the row's whole subject is a cursor that reads a link the callback was allowed to free, and an index scan has no link to read. ⚠ The same reason forbids deriving l->count from the surviving links rather than from DEL_LLIST_ELEMENT's own decrement -- that decrement is a STORE, it is half the row's oracle precisely because it records a free that happened, and a rung that recomputed it would agree with R1h by construction and measure nothing. There is no single token for that second half, so it lives in this English.",
        "rust": "`for i in 0..n` -- walking the arena by INDEX instead of by link. It computes the same u64 on this row, because register appends at the tail and the unlink only ever short-circuits prev to next, so index order and link order agree -- and safe_tuned.rs's header records it as the cheapest R3 candidate there is. It is forbidden because it is a DIFFERENT ALGORITHM: the row's whole subject is a cursor that reads a link the callback was allowed to free, and an index scan has no link to read. NOTES.md section 8 prices what the row is giving up by refusing it."
      }
    ],
    "why": "ph64 is PHP 5.0.0's tick-function dispatch, corpus row CRASH-086, tier `narrowed`. THE IDIOM IS A LIST WALK WHOSE CURSOR ADVANCES AFTER A CALLBACK THAT CAN FREE THE ELEMENT IT POINTS AT. `Zend/zend_llist.c:190` is `for (element=l->head; element; element=element->next)` and `:191` is `func(element->data)`; here `func` is `user_tick_function_call`, which runs USERLAND PHP, and userland PHP can call `unregister_tick_function()` on itself. That reaches `zend_llist_del_element` -> `DEL_LLIST_ELEMENT` -> `pefree(current)`, which frees the element the `for` header is about to read. ⚠ THERE ARE TWO DEREFERENCES AND THE CORPUS CITES THE OTHER ONE: control returns first to `basic_functions.c:2135`, `tick_fe->calling = 0`, which WRITES into the freed block (SITE C, `index.csv`'s `c_file_line`, and on plain malloc/free the FIRST fault ASan reports), and only then to the `for` header, which READS `element->next` out of it and FOLLOWS it (SITE L, this row's `c_lines`). ⭐⭐ AND THE SAME FILE HAS THE DEFENCE FIFTEEN LINES ABOVE: `zend_llist_apply_with_del` (:171-183) takes the same caller-supplied `func` and caches `next = element->next` at :177 BEFORE calling it. Three of `zend_llist.c`'s six callback walks cache the successor and three advance in the `for` header, and the three that do not are the three this defect can reach. That asymmetry is the row, it is argued C-side and needs no Rust, and `controls/next_cache.py` prices the counterfactual. ⚠⚠ R1h IS IN A THIRD FUNCTION AND FIXES BOTH SITES BY MAKING THE FREE UNREACHABLE. `562f886ecb14` (Antony Dovgal, 2007-04-10, \"MFH: fix #41037 (unregister_tick_function() inside the tick function crash PHP)\") patches `user_tick_function_compare` so that `unregister_tick_function` REFUSES to free an element whose `calling` flag is set. It touches neither `zend_llist.c:190` nor `basic_functions.c:2135`; both survive verbatim into master, 21 years on, and `zend_llist_apply`'s body is byte-identical at twelve tags with only the `TSRMLS_DC` deletion after that. ⚠⚠⚠ AND THE ORACLE IS NOT THE VISIT FOLD. `REAL_SIZE(sizeof(zend_llist_element) + sizeof(user_tick_function_entry) - 1)` is 40 and `40 >> 3 = 5 < MAX_CACHED_MEMORY`, so a freed element goes into `AG(cache)[5]` and is NOT returned to `malloc`: its payload is untouched, `element->next` still reads the true successor, and the walk completes normally. On the corpus's own trigger the VISIT FOLD IS BIT-IDENTICAL between R1 and R1h (`controls/oracle.py` E2a, 213 of 213), which is what `crashes_pristine_5_0_0 = False` is. The row's u64 therefore also carries `l->count`, the dtor count, the refusal count and `php_shim_tally()`'s four allocator fields, and THOSE move: R1 really did free an element R1h refuses to free. ⭐ The sharper half lands on `inputs/adversarial-reuse-*`: one same-size-class `emalloc` inside the same callback -- what any PHP tick function does with any small allocation -- LIFO-pops the freed element straight back out, so `element->next` becomes bytes the WINDOW chose and R1 SIGSEGVs at all four `DEL_LLIST_ELEMENT` arms while R1h is clean. ⚠⚠ WHAT SAFE RUST BUYS HERE IS A REPRESENTATION CHANGE, NOT A CHECK, AND THE ROW REPORTS THAT RATHER THAN HIDING IT: `zend_llist_element *next` is a raw pointer, and safe Rust cannot express that list without `Rc`, `RefCell` or raw pointers, so the faithful safe port is an INDEX ARENA -- and a dangling index is an ordinary in-bounds read of a slot that is still there, which is to the byte what 5.0.0's size-class cache does with the real block. So safe Rust does not turn this defect into a panic; it turns it into a WRONG ANSWER, and what removes it is `562f886ecb14`'s LOGICAL invariant. `verus.rs` proves `wf` -- every link is NIL or an in-range index, `next` ascends, `prev` descends -- which is what licenses all eight unchecked accessors AND every `decreases`; and `wf` holds with the guard DELETED. Memory safety and the upstream fix are orthogonal on this row, and only the value postcondition can see the difference. NOTES.md §9. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "llist_fold": "llist_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 39
    },
    "twin_obligations": {
      "verus.rs": 47
    },
    "obligations_note": "39 verified / 0 errors, and 47 under `--cfg slb_twin` -- EIGHT trusted accessors, therefore seven twins. ⚠⚠ WHAT IS PROVED HERE IS NOT A BOUNDS FACT, AND THE ROW SAYS SO RATHER THAN LETTING IT BE ASSUMED. R1's defect is that `element` OUTLIVES the callback that freed it, and a lifetime is not an index -- so what the four Rust rungs do is change the REPRESENTATION (`next` becomes a `u32` into an arena the kernel owns) and what survives that change is `wf`: every link is NIL or an index below the arena's length, `next` strictly ASCENDS and `prev` strictly DESCENDS. `register` establishes it by appending at the tail and `del_element` preserves it because it only short-circuits `prev -> next` and `prev < c < next`. ⭐ From `wf` alone come BOTH halves of what R1 loses: all eight unchecked accessors are in bounds, and every walk TERMINATES (`decreases arena.len() - element` IS the ascending fact). ⚠⚠ AND `562f886ecb14`'s GUARD DISCHARGES NONE OF IT -- `wf` holds with the guard deleted. The guard buys the VALUE, and only the value postcondition can see it. That is this row's ladder result and NOTES.md §9 states it. The value postcondition is discharged by a LOCKSTEP GHOST MIRROR: `G` is a pure-value copy of the exec state, every exec method carries `ensures final(self).g() == s_<method>(old(self).g(), ..)`, and the four loops carry the remaining-computation invariant `s_X(g_entry, cur_entry, fuel_entry) == s_X(self.g(), cur, fuel)`. The spec walks are FUEL-bounded because a `Seq<Node>` carries no ordering fact by itself; the exec loops keep `fuel >= arena.len() - cur`, which `wf` makes true, so the fuel never runs out on a reachable state.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 39 shipped + 8 for `slb_twin_{nnext,nprev,nname,ncalling,set_next,set_prev,set_calling,subwin}`. ⚠⚠⚠ THERE IS NO `#[verifier::rlimit]` IN THIS FILE AND THAT IS A MEASUREMENT RATHER THAN AN OMISSION. `kernel` would NOT verify at `rlimit(600)` while it was one function; it verifies at the DEFAULT 10, with the whole file at **39 / 0 in ~5 s**, once three STRUCTURAL things were done. ⭐ THE ORDER IS THE POINT AND IT IS RECORDED BECAUSE THE WRONG ORDER IS THE TEMPTING ONE -- raising the budget was tried first and did nothing: (1) the registration loop split out into `register_all`; (2) the decode split from the run, `kernel` / `run`; (3) ⭐ **`run_spec` marked `#[verifier::opaque]` and revealed once inside `run`** -- without which `kernel`'s ONE-LINE body blows any budget, because Z3 unfolds `llist_fold` into the whole composition, unfolds four recursive spec functions inside it once each by default fuel, and then matches that term tree against the same tree with differently-spelled arguments. Opaque, the match is six arguments. Bisected at 10 / 20 / 30 / 60 after the fact: all four give 39 / 0. NOTES.md §10.",
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
        "rd32_s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "name_of_s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mix": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "node_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "wf": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_name_id": {
          "external": null,
          "requires": [],
          "ensures": [
            "(((id as u64) | ((hi as u64) << 32)) as u32) == id"
          ]
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
        "s_alloc": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_free": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_unlink": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_del": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_unreg": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_userland": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_visit": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_apply": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_destroy": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_reg": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_regloop": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tally_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "g_init": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run_spec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "llist_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nnext": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].next"
          ]
        },
        "slb_twin_nnext": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].next"
          ]
        },
        "nprev": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].prev"
          ]
        },
        "slb_twin_nprev": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].prev"
          ]
        },
        "nname": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].name"
          ]
        },
        "slb_twin_nname": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].name"
          ]
        },
        "ncalling": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].calling"
          ]
        },
        "slb_twin_ncalling": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int].calling"
          ]
        },
        "set_next": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { next: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_next": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { next: x, ..old(v)@[i as int] })"
          ]
        },
        "set_prev": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { prev: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_prev": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { prev: x, ..old(v)@[i as int] })"
          ]
        },
        "set_calling": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { calling: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_calling": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { calling: x, ..old(v)@[i as int] })"
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
        "a": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "alloc": {
          "external": null,
          "requires": [
            "size == SZ_NAME || size == REQ_ELEM",
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
            "size == SZ_NAME || size == REQ_ELEM",
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
        "g": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rd32": {
          "external": null,
          "requires": [
            "i + 4 <= win@.len()"
          ],
          "ensures": [
            "r == rd32_s(win@, i as int)"
          ]
        },
        "name_of": {
          "external": null,
          "requires": [
            "1 <= id <= 0x1000_0000",
            "HEAD + (id as int - 1) * SLOT + 4 <= win@.len()"
          ],
          "ensures": [
            "r == name_of_s(win@, id)"
          ]
        },
        "register": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "1 <= id <= old(self).n",
            "HEAD + (id as int - 1) * SLOT + 4 <= win@.len()",
            "old(self).arena@.len() < 0x3FFF_FFFF"
          ],
          "ensures": [
            "final(self).g() == s_reg(old(self).g(), win@, id)",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse",
            "wf(final(self).g())",
            "final(self).arena@.len() == old(self).arena@.len() + 1"
          ]
        },
        "register_all": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "old(self).arena@.len() == 0",
            "old(self).n == n",
            "1 <= n <= 0x1000_0000",
            "HEAD + (n as int) * SLOT <= win@.len()"
          ],
          "ensures": [
            "final(self).g() == s_regloop(old(self).g(), win@, 1, n, n as nat)",
            "wf(final(self).g())",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse"
          ]
        },
        "del_element": {
          "external": null,
          "requires": [
            "wf(old(self).g())"
          ],
          "ensures": [
            "final(self).g() == s_del(old(self).g(), key, old(self).head, old(self).arena@.len())",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse",
            "wf(final(self).g())",
            "final(self).arena@.len() == old(self).arena@.len()"
          ]
        },
        "unregister": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "1 <= id <= old(self).n",
            "HEAD + (id as int - 1) * SLOT + 4 <= win@.len()"
          ],
          "ensures": [
            "final(self).g() == s_unreg(old(self).g(), win@, id)",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse",
            "wf(final(self).g())",
            "final(self).arena@.len() == old(self).arena@.len()"
          ]
        },
        "userland": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "HEAD + (old(self).n as int) * SLOT <= win@.len()",
            "1 <= (nm as u32) <= old(self).n"
          ],
          "ensures": [
            "final(self).g() == s_userland(old(self).g(), win@, nm)",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse",
            "wf(final(self).g())",
            "final(self).arena@.len() == old(self).arena@.len()"
          ]
        },
        "apply": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "HEAD + (old(self).n as int) * SLOT <= win@.len()",
            "old(self).n >= 1"
          ],
          "ensures": [
            "final(self).g() == s_apply(old(self).g(), win@, old(self).head, old(self).arena@.len())",
            "final(self).n == old(self).n",
            "final(self).trigger == old(self).trigger",
            "final(self).mode == old(self).mode",
            "final(self).reuse == old(self).reuse",
            "wf(final(self).g())",
            "final(self).arena@.len() == old(self).arena@.len()"
          ]
        },
        "destroy": {
          "external": null,
          "requires": [
            "wf(old(self).g())"
          ],
          "ensures": [
            "final(self).g() == s_destroy(old(self).g(), old(self).head, old(self).arena@.len())"
          ]
        },
        "run": {
          "external": null,
          "requires": [
            "1 <= n <= 0x1000_0000",
            "trigger <= n",
            "post <= n",
            "HEAD + (n as int) * SLOT <= win@.len()"
          ],
          "ensures": [
            "r == run_spec(win@, n, trigger, mode, reuse, post)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "24 <= len",
            "len <= 268435456"
          ],
          "ensures": [
            "r == llist_fold(buf@, off as int, len as int)"
          ]
        },
        "subwin": {
          "external": "verifier::external_body",
          "requires": [
            "i <= j <= v@.len()"
          ],
          "ensures": [
            "r@ == v@.subrange(i as int, j as int)"
          ]
        },
        "slb_twin_subwin": {
          "external": null,
          "requires": [
            "i <= j <= v@.len()"
          ],
          "ensures": [
            "r@ == v@.subrange(i as int, j as int)"
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
        "set_next": "`x: u32` is a PURE VALUE and needs no precondition. The unchecked operation is `v.get_unchecked_mut(i).next = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<Node>`, and on NOTHING about the index being written -- every one of the 2^32 values of `x` is a legal `u32` store into a field that is already initialised (`Vec::push` initialised the whole node before any link points at it). ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: `DEL_LLIST_ELEMENT` is a pair of NEIGHBOUR writes, so an `ensures` naming only `v@[i].next == x` would license a body that also moved `v[i+1]`'s link. The shipped `ensures` is the whole post-state, `old(v)@.update(i, Node { next: x, ..old(v)@[i] })`, so a body that touched any other slot or any other FIELD could not satisfy it. Miri is the backstop for the class regardless (../spec.md `miri`).",
        "set_prev": "`x: u32` is a PURE VALUE; see `set_next`. The two wrappers are the two halves of `DEL_LLIST_ELEMENT`'s unlink -- `(current)->prev->next = (current)->next` and `(current)->next->prev = (current)->prev` -- and each writes a NEIGHBOUR, never the node the index names in the caller's own cursor. The `ensures` names the whole post-state for the same reason.",
        "set_calling": "`x: bool` is a PURE VALUE and has two inhabitants, both legal. This is `basic_functions.c:2109` and `:2135` -- and `:2135` IS SITE C, the write R1 makes into a freed block. ⭐ The difference between the rungs is exactly the precondition: here `i < old(v)@.len()` must be DISCHARGED, and `wf` is what discharges it after the callback has run; in C nothing is asked."
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
      "if stride_w >= 24 && stride_w <= 268435456 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph64's two probe shapes have different work per call (552 and 4074 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW, and the quantity the cost really scales with is `n`, the number of tick functions registered -- which is read OUT OF THE DATA and would collapse on a one-entry window. The window BOUNDS `n` (`n <= (stride - 16) / 4`) and inputs/gen.py draws `n` as a fixed FRACTION of that bound, so the work really does scale with the denominator. Each call also does `2n + 2` shim allocations and the same number of frees on the C side and the same count of modelled ones on the Rust side, so the marginal is NOT a pure walk rate; NOTES.md §8 decomposes it."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "differ",
      "why": "⚠⚠ R4 AND R5 DIFFER AT BOTH LEVELS, AND THIS ENTRY WAS WRITTEN AS `norel` AT O3 AND CORRECTED BY THE MEASUREMENT -- the correction and its `contract_sha256` move are disclosed in NOTES.md §0. What the measurement says (results-php/ph64-callback-frees-cursor.json, O3/isolated): **385 instructions / 1747 bytes for `unsafe` against 384 / 1740 for `verus`**, so `md5_fn` and `md5_fn_norel` both differ and no `norel` claim is available. ⭐ THE DIFFERENCE IS SCHEDULING AND NOT SEMANTICS, and it is one instruction wide: R4 emits `incq <mem>` where R5 emits `inc %rbx ; mov %rbx,<mem>`, and one padding NOP differs (`data16 cs nopw` vs `nopl`). Nothing else moves -- the normalised diff is those two hunks. ⭐ AND THE RUN-TIME COST OF THE PROOF IS NEGATIVE: `kernel_exclusive_ir` on small.bin is 11 330 956 for R4 and 11 330 192 for R5, i.e. R5 is **764 Ir cheaper over 1 500 calls, -0.007 %**. ⚠ That is a codegen coin flip and NOT a result about verification; it is quoted here so nobody reads `differ` as `the proof costs something`. NOTES.md §11. ⚠ At O0 the two differ for the ordinary reason: nothing is inlined, so R5's seven trusted accessors and its `run` helper survive as real calls where R4 open-codes them -- 441 / 2406 against 485 / 2786."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph64 has EIGHT such items and THREE of them WRITE (`set_next`, `set_prev`, `set_calling`). ⚠⚠ It matters more here than on a row whose unchecked writes are to its own scratch buffer: `DEL_LLIST_ELEMENT` is exactly a pair of NEIGHBOUR writes -- `prev->next` and `next->prev` -- so a write wrapper whose `ensures` named only its own slot would let a body that also moved a neighbour's link through every Verus stage. The shipped `ensures` is the whole post-state, `old(v)@.update(i, Node { field: x, ..old(v)@[i] })`, and Miri is the backstop for the class regardless.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph64's cost is 4 x (one window's tick list built, walked and destroyed), i.e. at worst 4 x 1014 entries -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_llist.c",
    "c_lines": [
      186,
      193
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '186,193p'",
    "extract_sha256": "fce26e38389ba9fb7909f94c7fcfaed8a48f7960ba92c6d132812a958c40e917",
    "extra_spans": [
      {
        "c_file": "Zend/zend_llist.h",
        "c_lines": [
          25,
          29
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.h | sed -n '25,29p'",
        "extract_sha256": "c171e9616068985524cbc37f9d9523ba9f36208db3c0e7a5d685e8a94582a03b",
        "why": "`zend_llist_element`. ⚠⚠ `next` IS AT OFFSET 0, so SITE L's read-after-free is the freed block's FIRST WORD -- and `char data[1]` last is what makes `sizeof(element) + l->size - 1` the request. Both facts are load-bearing for the oracle and both are asserted at compile time by c/kernel.c's `ph64_layout_assert`."
      },
      {
        "c_file": "Zend/zend_llist.h",
        "c_lines": [
          37,
          45
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.h | sed -n '37,45p'",
        "extract_sha256": "c0e8e19b6f9a810a104b3d606abd104367b32f7bf3a3ad2c3a38b7224d3e2ef1",
        "why": "`zend_llist` -- `head`/`tail`/`count`/`size`/`dtor`/`persistent`. `count` is folded into the row's u64 and is half the R1-vs-R1h oracle; `persistent` is 0 (register_tick_function:2823), which is what makes `pemalloc`/`pefree` exactly `emalloc`/`efree`."
      },
      {
        "c_file": "Zend/zend_llist.c",
        "c_lines": [
          26,
          34
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '26,34p'",
        "extract_sha256": "fbbb2fb69b643cd4b4eee95861f1f72119c24f4090a7bc92715e35c33b9ae31c",
        "why": "`zend_llist_init`. Lifted verbatim; it is where `persistent = 0` and the dtor pointer are set."
      },
      {
        "c_file": "Zend/zend_llist.c",
        "c_lines": [
          37,
          52
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '37,52p'",
        "extract_sha256": "6b80ae8a75f7586252791e888218a4547ffb8514c52203d2a2322b987813c461",
        "why": "`zend_llist_add_element` -- the `pemalloc(sizeof(zend_llist_element) + l->size - 1)` that decides the size class (39 -> REAL_SIZE 40 -> cache index 5 < MAX_CACHED_MEMORY 11), and the APPEND-AT-TAIL that the four Rust rungs' ascending arena indices mirror."
      },
      {
        "c_file": "Zend/zend_llist.c",
        "c_lines": [
          73,
          104
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '73,104p'",
        "extract_sha256": "b714ec3184afe1e0a68d30997c480c5d5b5810a3d454aacfbcb915e268146493",
        "why": "⚠⚠ THE FREE SITE. `DEL_LLIST_ELEMENT` (:73-88) and `zend_llist_del_element` (:91-104) as one span, because the macro has no other caller here. Its last two statements are `l->dtor(current->data)` -- which `efree`s the entry's `arguments` -- and `pefree(current)`. ⚠ It is also the walk that CACHES `next` at :97, fifteen lines from the walk that does not; and it is the walk `TASK_PHP_031_REPORT` §4.3's open item lives in."
      },
      {
        "c_file": "Zend/zend_llist.c",
        "c_lines": [
          107,
          121
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_llist.c | sed -n '107,121p'",
        "extract_sha256": "5e38ed5040949606f9cde22cc718c43a9106d2158797d4422a3a5fdadc21dd01",
        "why": "`zend_llist_destroy` -- what the kernel calls at the end of every call so that call N does not depend on call N-1. It caches `next` too."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          154,
          158
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '154,158p'",
        "extract_sha256": "b5f23b9dc0b83a10b09fa6266b9fd980528afe5a6a06108d1afb1634496f8941",
        "why": "`user_tick_function_entry` -- declares **`calling`**, which is SITE C's target AND `562f886ecb14`'s predicate. `sizeof` is 16, which with the element's 24 gives the 39-byte request."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2074,
          2082
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2074,2082p'",
        "extract_sha256": "a84dcb7e67109c37532329ac3b3598dda80c4fbaa0b08c1208e1f43e55c9e81f",
        "why": "`user_tick_function_dtor` -- what the free destroys BESIDES the element: `efree(tick_function_entry->arguments)`, i.e. the chain's third dangling reference, the one the comparator would read on any later walk."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2102,
          2137
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2102,2137p'",
        "extract_sha256": "bacb13c0332f3ec4b51e2446c5ff586c3c44e7fb0fcf43c8e2dd6f35bca5a247",
        "why": "⚠⚠⚠ SITE C. `user_tick_function_call`. The write-after-free is `:2135`, `tick_fe->calling = 0`, and it is the line `index.csv` cites for CRASH-086 -- on plain malloc/free under ASan it is the FIRST faulting access, a `WRITE of size 4`. `:2109` sets the flag and `:2135` clears it, and those two lines are what make R1h's predicate true."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2139,
          2144
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2139,2144p'",
        "extract_sha256": "d64eae1b992514d19098b45efbe692573dc02b165d059609090abc19811e73db",
        "why": "`run_user_tick_functions`, the bridge. The `zend_llist_apply` call is at **`:2143`**, not `:2139`; `:2139` is the signature."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2146,
          2161
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2146,2161p'",
        "extract_sha256": "a429912167dab97bb93e08c6864a3666afb1d90b0513917bb38ca72fc49622f7",
        "why": "⭐⭐ WHERE R1h LANDS. `user_tick_function_compare`, and it is NEITHER the cited line NOR the defect. `TASK_PHP_022`'s open item 25 is that a row which does not cite the frame the fix goes in certifies a span containing neither the fix nor its frame; this row cites it up front."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2799,
          2835
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2799,2835p'",
        "extract_sha256": "a002a982f92b9262ee0ea8f1cb11d2e6a13715dbce96a5ab847a497b9204a3c0",
        "why": "`PHP_FUNCTION(register_tick_function)` -- `calling = 0` at `:2804`, the `safe_emalloc(sizeof(zval *), arg_count, 0)` at `:2811`, the `zend_llist_init(..., 0)` at `:2822-2825` and the `add_element` at `:2832`. `narrowed`: the zval unpack comes off."
      },
      {
        "c_file": "ext/standard/basic_functions.c",
        "c_lines": [
          2840,
          2862
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/basic_functions.c | sed -n '2840,2862p'",
        "extract_sha256": "ef14ca8cae07f307be5c95bdaffcaa2dafed36b61cb15f48da59a8c1f07f5b8d",
        "why": "`PHP_FUNCTION(unregister_tick_function)` -- THE TRIGGER'S ENTRY POINT. ⚠ `:2843-2861` set only `arguments` and `arg_count`, so the search key's `calling` is an INDETERMINATE stack `int` in PHP. That is why `562f886ecb14` reads `tick_fe1->calling` -- the LIST element's -- and `controls/predicate.py` measures what reading the other one would cost."
      }
    ],
    "extra_spans_note": "⚠⚠⚠ THIRTEEN SPANS ACROSS THREE FILES, AND THE PRIMARY IS THE DEFECT RATHER THAN THE CITED LINE. `.memory-php/01-extraction.md` F1: `provenance.c_file`/`c_lines` name the DEFECT site and the other frames go in the notes -- so the primary is `Zend/zend_llist.c:186-193`, the walk, and `index.csv`'s own `c_file_line` (`basic_functions.c:2135`) is `extra_spans[8]`. ⚠ HERE F1 IS SUBTLER THAN USUAL AND THE ROW SAYS SO RATHER THAN REPEATING THE SLOGAN: `:2135` is NOT a mis-citation. It is the FIRST faulting access in the chain -- ASan on plain malloc/free reports it as the initial `heap-use-after-free`, a `WRITE of size 4` -- and the corpus's own history record says exactly that. So on this row the cited line is the faulting frame AND the first fault, and the defect is still one call up. ⭐ `extra_spans[10]` is the frame R1h OCCUPIES: open item 25's whole lesson is that a row which does not cite it certifies a span containing neither the fix nor its frame, and this row cites it from the first commit rather than two tasks late. Each entry is checked exactly as the primary is (in the manifest, in range, canonical extract_cmd, extract_sha256 over the bytes `sed` prints), and the kernel overlap is computed over the UNION.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC / TSRMLS_FETCH()",
        "kind": "deletion",
        "where": "zend_llist.c:186, :188 (x2 in the apply frame); basic_functions.c:2102, :2116, :2141, :2149",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "pemalloc/pefree -> php_shim_emalloc/php_shim_efree",
        "kind": "substitution",
        "where": "zend_llist.c:39, :87, :116",
        "why": "`register_tick_function:2823` passes `persistent = 0`, and `Zend/zend_alloc.h`'s `pemalloc(size, persistent)` macro is `emalloc(size)` for `persistent == 0` and `pefree(p, 0)` is `efree(p)`. common-php/emalloc_shim.h IS PHP 5.0.0's own `_emalloc`/`_efree`, line-cited to the same tarball (PLAN_PHP.md 4.3), so this is a redirection to the same code and not a substitution of a different allocator. No semantics."
      },
      {
        "what": "zval **arguments -> an opaque 8-byte block holding the function name inline",
        "kind": "narrowing",
        "where": "basic_functions.c:155 (the field), :2811 and :2857 (the two allocations)",
        "why": "PHP allocates `safe_emalloc(sizeof(zval *), arg_count, 0)` = 8 bytes for `arg_count == 1` and points it at a separately-allocated `zval` string; this kernel allocates the same 8 bytes and puts the name in them. The allocation the dtor frees, its SIZE CLASS and therefore the whole cache behaviour are unchanged, which is the only thing the row's oracle reads. What comes off is the zval wrapper, which is what `narrowed` means. No semantics."
      },
      {
        "what": "call_user_function(EG(function_table), NULL, function, &retval, arg_count - 1, arguments + 1) -> a direct call",
        "kind": "projection",
        "where": "basic_functions.c:2111-2116",
        "why": "that is the executor. The row's whole point is what USERLAND does to the list while the walk holds a cursor, and the projection supplies the userland the window describes -- self-unregistration, unregistration of a neighbour, and one same-size-class allocation. It removes the executor and preserves the one effect the defect needs. No semantics on the extracted domain."
      },
      {
        "what": "the three php_error_docref(E_WARNING) arms of the call_user_function == FAILURE branch",
        "kind": "projection",
        "where": "basic_functions.c:2118-2132",
        "why": "the projected userland always succeeds, so the arms are DEAD on this kernel's domain. No semantics on the extracted domain."
      },
      {
        "what": "php_error_docref(E_WARNING, \"Unable to delete tick function executed at the moment\") on R1h's refusal path -> a refusal counter",
        "kind": "projection",
        "where": "the 562f886ecb14 hunk, c/kernel_hardened.c only",
        "why": "⚠⚠⚠ THIS `why` CANNOT END IN \"no semantics\" AND IT DOES NOT. `php_error_docref` is `php_error_docref0` (main/php.h:324) -> `php_verror` (main/main.c:431) -> `php_error` -> `zend_error` (Zend/zend.c:866), whose `default:` arm calls `call_user_function_ex(..., orig_user_error_handler, ...)` when `set_error_handler` is installed -- i.e. ARBITRARY USERLAND, reached from inside `zend_llist_del_element`'s own `while` loop, which holds `current` and `next`. The projection REMOVES a re-entry point that the fix itself introduces. ⚠ It is a STATIC READING verified at source at 5.0.0 and at php-5.2.2 (TASK_PHP_031_REPORT §4.3) and it is NOT MEASURED: no PHP was built and no reproducer was run. NOTES.md §4d carries it as an OPEN ITEM. ⭐ Upstream itself is a partial answer -- master replaced the warning with `zend_throw_error`, which cannot run userland."
      },
      {
        "what": "zend_binary_zval_strcmp(func1, func2) -> an 8-byte binary compare, and the Z_TYPE_P == IS_ARRAY arm removed",
        "kind": "projection",
        "where": "basic_functions.c:2152-2159",
        "why": "every name on this kernel's domain is a string, so the `IS_STRING` arm is the one reached and `zend_binary_zval_strcmp` on two equal-length 8-byte strings IS the 8-byte binary compare. No semantics on the extracted domain."
      },
      {
        "what": "the search key's `calling` field is zeroed",
        "kind": "substitution",
        "where": "basic_functions.c:2843-2861",
        "why": "PHP leaves it INDETERMINATE -- `PHP_FUNCTION(unregister_tick_function)` sets only `arguments` and `arg_count`. `562f886ecb14` reads `tick_fe1->calling`, and `zend_llist_del_element:98` calls `compare(current->data, element)`, so `tick_fe1` is the LIST ELEMENT and the key's flag is never read on either rung. Zeroing it removes an indeterminate value without removing a behaviour, and controls/predicate.py measures what reading it instead would cost (the guard becomes a no-op on 189 of 189 trigger windows). No semantics."
      },
      {
        "what": "the three callbacks take `void *` and cast inside",
        "kind": "substitution",
        "where": "basic_functions.c:2143, :2824, :2860 (the three function-pointer casts)",
        "why": "PHP casts the FUNCTION POINTER at the call site -- `(llist_apply_func_t) user_tick_function_call`, `(llist_dtor_func_t) user_tick_function_dtor`, `(int (*)(void *, void *)) user_tick_function_compare` -- which is an indirect call through an incompatible type. This kernel casts the ARGUMENT instead, which is the same call on every ABI this project builds on and is not undefined. It removes a UB the row does not model rather than adding one. No semantics."
      },
      {
        "what": "the four Rust rungs represent `zend_llist_element *next` as a u32 ARENA INDEX",
        "kind": "substitution",
        "where": "zend_llist.h:26-27",
        "why": "⚠⚠ THE ONE DIVERGENCE THE ROW IS ABOUT, AND IT IS DECLARED RATHER THAN LEFT TO BE NOTICED. Safe Rust cannot express an intrusive doubly-linked list of raw pointers without `Rc`, `RefCell` or `unsafe`, so the faithful safe port owns an arena and links by index. `zend_llist_add_element` appends at the TAIL, so indices ASCEND along the list and stay ascending under `DEL_LLIST_ELEMENT` (which only short-circuits `prev -> next`, and `prev < c < next`); the C's element ADDRESSES have no such order, because the size-class cache hands blocks back LIFO. The visit sequence, the fold and the allocator tally are identical either way -- controls/differential.py checks that against the SHIPPED C on 2 592 windows -- and what the arena buys is the `decreases` clause R5 needs. ⚠ It also means a dangling link is an IN-BOUNDS READ rather than a use-after-free, which is why the Rust rungs reproduce this defect as a wrong answer and not as a fault. No semantics on the extracted domain; a large finding about the ladder, and NOTES.md §9 is where it is stated."
      },
      {
        "what": "the four Rust rungs reproduce php_shim_tally() arithmetically instead of linking the shim",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:346-435, :642-648",
        "why": "harness/build.py compiles exactly three C translation units and no Rust rung links C. Each Rust rung carries the same per-size-class LIFO cache model driven by the SAME request sequence, so `n_alloc`, `n_free`, `n_cache_hit` and `bytes_mallocked` are equal by construction and controls/differential.py checks it against the C. ⚠ What the Rust rungs do NOT need is the block's IDENTITY: which block comes back out is observable only through a dangling pointer, and R1h has none. This pins the ALLOCATION SEQUENCE across rungs and is NOT evidence that any Rust rung ran PHP's allocator. No semantics."
      },
      {
        "what": "the driver guard carries a third conjunct, `stride_w <= 268435456`",
        "kind": "narrowing",
        "where": "c/main.c and all four .rs drivers",
        "why": "a `u32` arena index is sound while the arena holds fewer than 2^32 entries, and `n <= (stride - 16) / 4`, so a 256 MiB ceiling on the WINDOW gives `n <= 2^26` with 64x to spare. It is a structural precondition of the REPRESENTATION, it is verus.rs's third `requires`, and all six rungs carry it so no rung is measured over a domain another refuses. The largest window this row ships is 4 074 bytes. No semantics on the measured domain."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection / narrowing and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠⚠ ONE of these twelve entries has a `why` that does NOT end in \"no semantics\", and it is deliberate: the `php_error_docref` projection on R1h's refusal path removes a userland re-entry the fix itself introduces. PROTOCOL_PHP.md A2 says a divergence that changes behaviour is a `modelled` tier; the argument that this row is still `narrowed` is that the removed behaviour is on the HARDENED rung's refusal path only, is absent from R1 entirely, and is unreachable on the measured corpus (no window makes the guard fire). It is stated here rather than smoothed over.",
    "root_cause_ids": [
      "unregister_tick_function-inside-tick-callback-frees-the-element-zend_llist_apply-holds-use-after-free"
    ],
    "cwe": "CWE-416",
    "cwe_note": "index.csv records `heap-use-after-free` for CRASH-086 and this row reproduces the CLASS and NOT the sanitizer STRING, which is a finding and not a failure (PROTOCOL_PHP.md A4). ⚠⚠ On the FAITHFUL 5.0.0 allocator `heap-use-after-free` is NOT REPRODUCIBLE AND CANNOT BE: for ASan to say use-after-free the block must have reached `free()`, and a 39-byte `zend_llist_element` never does -- `REAL_SIZE(39) >> 3 = 5 < MAX_CACHED_MEMORY`, on 32- and 64-bit builds alike. It is handed straight back out instead. So this row fires ASan on the windows where the freed block is handed back out INSIDE the same callback, and what ASan reports there is `SEGV on unknown address`. The `latent` windows -- the corpus's own trigger -- are SILENT under every detector and still return a different u64, which is why the oracle is in the checksum. NOTES.md §6 carries the fidelity table and the plain-malloc build that DOES produce `heap-use-after-free`, which is the artefact that the recorded category is real.",
    "fix_commit": "562f886ecb14",
    "fix_commit_note": "⭐ ONE COMMIT, THREE ARTEFACTS INSIDE IT, AND A BACKPORT THAT COSTS NOTHING. `562f886ecb14` -- Antony Dovgal <tony2001@php.net>, 2007-04-10 09:37:09 +0000, \"MFH: fix #41037 (unregister_tick_function() inside the tick function crash PHP)\". ONE hunk, 7 added / 2 deleted lines, in ONE function: `user_tick_function_compare`. Three artefacts are INSIDE the commit -- the bug number #41037 in the subject, a NEWS entry it adds, and a 23-line regression test `ext/standard/tests/general_functions/bug41037.phpt` it adds. Patch bytes at controls/562f886ecb14.patch (86 lines, sha256 2719dc3f143456d56f42f998172833be7dfee4ffa19182de656b9fcd2107d92b); the test at controls/bug41037.phpt, and controls/bug41037.py replays its three `hello`s and three warnings against both rungs. ⚠ THE WINDOW ADMITS ONE CANDIDATE, AND THAT IS A DERIVATION RATHER THAN A SELECTION: the guard is ABSENT at php-5.2.1 and PRESENT at php-5.2.2 (body sha256 418a53cb63037006 -> 4ae3d1c82072e782), the commit's date sits inside that window, and the php-5.2.1 -> php-5.2.2 diff of the function IS this commit's hunk line for line. ⭐ It applies to the PRISTINE 5.0.0 tarball with `patch -p1`, rc = 0, and the result is byte-identical to php-5.2.2's function -- 5.0.0's `user_tick_function_compare` is byte-identical to php-5.2.1's, so the pre-image IS 5.0.0 and the backport cost is zero. ⚠⚠⚠ IT PATCHES NEITHER SITE. Not `Zend/zend_llist.c:190` (this row's primary span, and never repaired at ANY tag: the body's sha256 is identical at twelve tags from php-5.0.0 to php-5.6.0 and differs at php-7.0.0 and master only by the TSRMLS deletion) and not `basic_functions.c:2135` (`index.csv`'s cited line, untouched at php-5.2.2 and still there in master; `grep -ac 'calling = 0'` over the 86-line patch is 0). It makes the FREE UNREACHABLE from a THIRD function instead, and both dereferences survive verbatim. ⚠ That is also why the pre-image screen (`.tasks-php/preimage_screen.py`) labels this commit NOT-THE-REPAIR with `decisive=False`: no line-level pre-image screen can find a fix of this shape, and TASK_PHP_031_REPORT §7.1 measured the class at 17 of the screen's 43 exclusions. ⭐ AND UPSTREAM STRENGTHENED IT RATHER THAN REVERTING IT: the guard survives into master, 18 years on, with `php_error_docref(E_WARNING)` upgraded to `zend_throw_error(NULL, \"Registered tick function cannot be unregistered while it is being executed\")` -- which is an independent upstream artefact that this is the accepted repair, and a partial answer to the open item in `divergences[5]`. ⚠ WHY THE ONE EXPOSURE WAS CLOSED INSTEAD OF THE CONTAINER: of `zend_llist_apply`'s eight 5.0.0 call sites, SEVEN cannot re-enter userland (`php_ini.c:549,:550`, the two SAPI `php_register_command_line_global_vars`, `zend_execute_API.c:158,:208`, `zend_extensions.c:166`) and the eighth is `user_tick_function_call`. Fixing the one caller closes the one exposure -- which is the clean negative against reading the missing `next`-cache as an unexploited hole elsewhere.",
    "invariant": "I1",
    "obligation": "O1",
    "echoes": [
      "p28",
      "p34"
    ],
    "echoes_note": "p28-intrusive-lists is the closest PAT analogue -- a list whose nodes are unlinked while a walk holds one -- and p34-refcount-stack is the closest on the lifetime axis. PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and never a filter. ⚠ The mechanisms differ where it matters: p28's unlink is done BY the walk, so the walk knows; here it is done by a CALLBACK the walk hands control to, and the walk has no way to know.",
    "uses_allocator": true,
    "uses_allocator_why": "c/kernel.c makes `2n + 2` `php_shim_emalloc` calls and the same number of `php_shim_efree` calls per kernel call, for `zend_llist_add_element`'s `pemalloc(sizeof(zend_llist_element) + l->size - 1)` (zend_llist.c:39) and `register_tick_function`/`unregister_tick_function`'s `arguments` blocks (basic_functions.c:2811, :2857). ⚠⚠ AND THE ALLOCATOR IS NOT BACKGROUND HERE, IT IS THE MECHANISM: the size-class cache is what makes the freed element survive with its payload intact (`crashes_pristine_5_0_0 = False`) and it is also what hands that element straight back to the next same-class request, which is how the defect becomes a fault. The truncations T1/T2/T3 do NOT fire -- every request is 8 or 39 bytes -- so this row exercises the CACHE half of emalloc_shim.h and none of the overflow half. The tally is folded into the checksum and the Rust rungs reproduce it arithmetically, which pins the ALLOCATION SEQUENCE across rungs and is NOT evidence that any Rust rung ran PHP's allocator."
  }
}
```
