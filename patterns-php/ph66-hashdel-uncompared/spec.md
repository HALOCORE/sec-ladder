# ph66 — `zend_hash_del_key_or_index`: a numeric bucket's key is never compared

**PHP 5.0.0, `Zend/zend_hash.c:450-503` (the defect at `:464-465`), corpus row
LOGIC-001, tier `verbatim`.** The delete settles a bucket's key *kind* with a
disjunct, so for a numeric bucket the left arm fires and `memcmp` is never
reached: hash equality alone stands in for key identity, and
`unset($a["abc"])` destroys `$a[6385036779]`.

⭐⭐⭐ **THIS ROW'S TARGET ERROR IS A VALUE, NOT A SIGNAL, AND THAT IS WHY IT
EXISTS.** Every cell exits 0 on every input. There is no segfault, no ASan
report, no `si_addr`; the observable is the surviving-key list. **R1, R2, R3, R4
and R5 all return the same `u64` on every input, adversarial included** — a
wrong boolean is expressible in safe Rust, in `unsafe` Rust and in Verus, and
none of them has any reason to refuse it. Only `c/kernel_hardened.c` moves.
`controls/ladder.py` measures that table and `NOTES.md` §7 publishes it.

⭐ **The trigger needs no preimage**, and the catalogue's instruction to compute
one names the wrong direction: `_zend_hash_index_update_or_next_insert` stores
`p->h = h` with `h` the raw user-chosen index, so running DJBX33A *forwards* on
any string key gives the integer index that key will destroy.

⚠ **R1h is `b73349dbe4e9` whole and unmodified** — one hunk, 4 added / 2 deleted
lines, one file, `patch -p1` against the pristine tarball with no fuzz and no
backport. It hoists `p->nKeyLength == nKeyLength` into a required conjunct.

The machine-readable contract follows.
`harness-php/gate.py ph66-hashdel-uncompared` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "4 <= len",
    "len <= 268435456"
  ],
  "ensures": [
    "result == hash_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (hash_fold). ⚠⚠ `model.py`'s `hash_fold` IS NOT `verus.rs`'s, AND THAT IS THE POINT: verus.rs builds it out of fuel-bounded recursions over the SAME state the exec code mutates (`s_run`/`s_step`/`s_ins_str`/`s_ins_idx`/`s_del`/`s_find_*`/`s_fold`), while model.py's `hash_fold` is an immutable-tuple recursion with no `while` and no mutation, written one unfolding at a time. model.py's OTHER two implementations are `simulate`, an imperative arena simulation with real chain and global links, and `_dumb`, which has NO LINKS AT ALL and resolves every lookup by `max(insertion sequence)` over the live buckets of a slot -- sound because CONNECT_TO_BUCKET_DLLIST prepends at the head and the delete only short-circuits pLast->pNext, so chain order IS descending insertion order. `selfcheck()` drives all three against each other on the shipped inputs AND on synthetic windows this file builds. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. `controls/differential.py` closes the fourth edge -- the SHIPPED C against all three -- over 94 off-corpus windows, with five must-fire mutations.",
  "idiom": {
    "required": [
      {
        "c": "`(p->nKeyLength == 0) ||` at zend_hash.c:464 -- the DISJUNCT that settles the key KIND, and the whole of this row. ⚠ IT IS PINNED IN BOTH C RUNGS ON PURPOSE AND THAT IS NOT AN OVERSIGHT: the R1h KEEPS the == 0 disjunct and merely HOISTS the length test in front of it, so the spelling survives the repair and what changes is its POSITION. A forbidden entry on the hoisted conjunct is therefore impossible -- both C rungs contain it, the string-key insert at :215 included -- and the positional half lives in this English and in the census arm of .tasks-php/probes/ph66_djbx33a_collide.py, which classifies the two texts dual and guarded and whose own N8 arm fails if it cannot tell them apart.",
        "rust": "`nkl == 0 ||` -- the same disjunct, in all four Rust rungs. ⚠ THE RUST KEY PINS THE DISJUNCTION AND NOT THE WHOLE PREDICATE, deliberately: R2 reads the node through a full arena index expression, R3 and R4 bind a reference first, and R5 spells it twice -- once in exec and once in the spec function the exec is proved against -- so no single longer expression is common to all four. What IS common is that the key-kind test is a DISJUNCT and that the key comparison sits to the right of it, and the ORDER lives in this English, which is what the named-spelling standard says about polarity and scope."
      },
      {
        "c": "`p->nKeyLength = 0;` at zend_hash.c:387 -- the NUMERIC MARKING, with upstream's own comment beside it. It is the fact the defect rests on: a bucket whose key is an integer carries length zero, and length zero is what the disjunct tests.",
        "rust": "`nkl: 0`"
      },
      {
        "c": "`p->h = h;` at zend_hash.c:388 -- the RAW USER INDEX, stored verbatim. ⭐ THIS IS WHY THE ROW NEEDS NO PREIMAGE: the numeric bucket's hash field is whatever integer the caller named, so a colliding pair is built by running the hash FORWARDS on a string key and publishing the result as the index.",
        "rust": "NO BACKTICKED SPELLING, deliberately: R2 and R3 build the node with field shorthand and R4/R5 write the field name twice, which is one fact in two spellings and not a pin. The Rust side of this entry is that the coll bit of a record turns the index into the hash of the record's own key, which is the same integer the numeric insert stores; inputs/gen.py asserts the 64 keys' hashes are pairwise distinct and all above the plain-index range, so that bit is the ONLY collision in the kernel's domain."
      },
      "R2, R3, R4 AND R5 IMPLEMENT THE DEFECTIVE C KERNEL'S FUNCTION -- THE DEFECT INCLUDED -- AND NOT THE HARDENED ONE'S. That is the opposite of ph64 and ph96 and it is a DECISION, not an omission: the ladder memory says the Rust rungs carry whatever is actually memory-safe, and on this row the DEFECTIVE kernel ALREADY IS memory-safe. Its defect is a wrong boolean; every free it makes is a correct free of a bucket it has just unlinked from both lists and from the table's internal pointer. So there is nothing for safe Rust, for unsafe Rust or for Verus to refuse, all five rungs return the same u64 on every input including every adversarial one, and only the hardened C rung moves. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it.",
      "THE RECORD LAYOUT is structure and not data: four bytes per record -- a control byte, a selector, a payload low byte and a payload high byte -- and the control byte carries THREE INDEPENDENT BITS, op (insert/delete), kind (string key/numeric index) and coll. NO BACKTICKED SPELLING: the C decodes them into int locals, R2 and R3 into unsigned locals and R5 into locals it also has spec functions for -- three legitimate spellings of one fact. ⭐ The three bits are INDEPENDENT because which operation, which key kind and is this the colliding index are three propositions, and the row's whole subject is what happens when the second and third disagree with what the delete names. inputs/gen.py partitions the 64 selectors so that a MEASURED window can never reach that state and an ADVERSARIAL one always does, and asserts both."
    ],
    "forbidden": [
      "`HANDLE_NUMERIC` -- zend_hash.h:283-317, the macro the symtable delete and its siblings apply BEFORE hashing, which converts a numeric-looking STRING key into an integer index. It is the OTHER place PHP 5.0.0 decides what kind a key is, and a rung that acquired it would resolve some string-key deletes to the index path before the defective predicate ever ran -- i.e. it would delete part of the row by making the two kinds agree upstream of the predicate. The kernel lifts the symtable-free entry point instead, and NOTES.md section 5 records that the choice is upstream's own: the two are different entry points in the same header.",
      "`zend_hash_do_resize` -- zend_hash.c:410-430. The kernel sizes its table from the record count at init, which is a real PHP spelling wherever the size is known, and that makes the table-full condition unreachable, so the resize path is outside the extracted span and is declared in the divergence ledger. It is FORBIDDEN rather than merely absent because a rehash REORDERS EVERY BUCKET CHAIN, and chain order is what decides WHICH element this defect destroys -- a rung that acquired it would still compute a wrong answer, but a DIFFERENT wrong answer from the C's, and the row's cross-rung checksum would blame the rung. ⚠ c/kernel.c's own header comment names this spelling, which is why controls/spellings.py's N1 arm exists: a comment-only occurrence must MISS, and if it ever HITS then every verdict in that audit is about prose rather than code.",
      {
        "rust": "`KEYTAB` -- a 64-entry memo of the per-selector key, which is the largest single optimisation available to R3 on this row and is refused. The delete receives the key BYTES from its caller and hashes them itself; a rung that looked a key up by its selector would have stopped comparing keys, which is the one thing this row measures. NOTES.md section 9 prices what the row is giving up by refusing it.",
        "c": "`ph66_keytab` -- the same memo on the C side, refused for the same reason. The key pointer is a parameter of both the delete and the string-key insert, and a kernel that resolved a key without reading its bytes would not be lifting either."
      }
    ],
    "why": "ph66 is PHP 5.0.0's `Zend/zend_hash.c` container, corpus row LOGIC-001, tier `verbatim`. THE IDIOM IS A HASH-TABLE DELETE THAT SETTLES A BUCKET'S KEY *KIND* WITH A DISJUNCT. `zend_hash_del_key_or_index`'s chain walk is `if ((p->h == h) && ((p->nKeyLength == 0) || ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength)))))` at `:464-465`, and a NUMERIC bucket is marked by `nKeyLength == 0` -- upstream says so itself at `:387`, `Numeric indices are marked by making the nKeyLength == 0`. So for a numeric bucket the LEFT DISJUNCT FIRES AND THE KEY IS NEVER COMPARED AT ALL: hash equality alone stands in for key identity, and `unset($a[\"abc\"])` destroys `$a[6385036779]`. ⭐ THE TRIGGER NEEDS NO PREIMAGE AND THE CATALOGUE'S INSTRUCTION TO COMPUTE ONE NAMES THE WRONG DIRECTION. `_zend_hash_index_update_or_next_insert` stores `p->h = h` with `h` the RAW user-chosen index, so running DJBX33A FORWARDS on any string key gives the integer index that key will destroy -- one line, no search. A PREIMAGE, by contrast, is a 64-bit target with no digit structure to lift (every `33^k` is odd, hence a unit mod 2^64), and `.tasks-php/probes/ph66_djbx33a_collide.py` is the generator for both halves of that. ⚠⚠⚠ THE TARGET ERROR IS A VALUE AND NOT A SIGNAL, AND EVERY COLUMN OF THIS ROW FOLLOWS FROM THAT. Measured on a real PHP 5.0.0 CLI, all five oracle cells exit 0 with a clean stderr and the observable is the SURVIVING-KEY LIST (`.tasks-php/probes/ph66_key_identity.sh`; NOTES.md section 2). There is no use-after-free variant and there must not be one: `pDestructor` is `zval_ptr_dtor`, which frees only at refcount 0, so the last holder's free is a CORRECT free of a value nobody else names; and the bucket's one external alias is repaired four lines above the free by `if (ht->pInternalPointer == p) ht->pInternalPointer = p->pListNext;`. NOTES.md section 3 states how this row checks that its own kernel introduces no UB the C does not have. ⭐⭐⭐ AND THE CONSEQUENCE IS THE ROW'S REASON FOR EXISTING: R1, R2, R3, R4 AND R5 ALL RETURN THE SAME u64 ON EVERY INPUT, ADVERSARIAL INCLUDED. A wrong boolean is expressible in safe Rust, in `unsafe` Rust and in Verus, and none of them has any reason to refuse it, so the whole safety stack is blind to this defect and only `c/kernel_hardened.c` moves. `controls/ladder.py` measures the six-cell table rather than asserting it and NOTES.md section 7 publishes it. `CLAUDE.md` Don't 6: *safe Rust reproduces the bug* is a FINDING, never a kill. ⚠⚠ WHAT R5 DOES AND DOES NOT BUY, STATED HERE RATHER THAN LEFT TO BE ASSUMED. `verus.rs` proves `kernel` returns `hash_fold(...)` and discharges every one of its ten trusted accessors' index bounds from `wf` -- every link is NIL or an in-range arena index, the bucket chain's `pNext` strictly DESCENDS and the global list's `pListNext` strictly ASCENDS, which is what gives both walks a `decreases` clause where `zend_hash.c` has none. ⛔ `wf` HOLDS WITH THE DEFECT IN PLACE, and the shipped `ensures` is a value postcondition against a spec function that CARRIES the defect, so R5 verifies with `:464`'s disjunct exactly as R2-R4 do. The property that excludes it is the corpus labeller's own `NEW:container-key-identity` -- *a hash-table operation acts on the bucket whose key equals the requested key in both key kind and key bytes, and on no other bucket* -- and `controls/key_identity.py` builds it in Verus three times: it VERIFIES against `b73349dbe4e9`'s predicate, FAILS on the POSTCONDITION against 5.0.0's, and a vacuous obligation verifies against both so the difference is attributable to the predicate and not to the file. NOTES.md sections 6 and 7. ⚠⚠ R1h IS `b73349dbe4e9` WHOLE AND UNMODIFIED, APPLIED TO THE PRISTINE TARBALL WITH `patch -p1`, rc 0, NO FUZZ AND NO BACKPORT -- one hunk, 4 added / 2 deleted lines, one file. Zeev Suraski, 2006-02-01, *Fix possibility of a wrong element being deleted by zend_hash_del()  Thanks Stefan!*. It HOISTS `p->nKeyLength == nKeyLength` into a required conjunct, so a numeric bucket can match only an index lookup and the surviving `== 0` disjunct is nothing but a short-circuit past the `memcmp` -- which is what its own new comment says. `controls/r1h_apply.py` re-derives the whole claim from the tarball on every run. ⭐ THE REPAIR IS NARROW: it leaves the benign answer byte-identical, which is what makes the R1-vs-R1h cost comparison a comparison of two programs that agree, and `inputs/gen.py` refuses a measured corpus in which any delete would take the defective arm. ⚠⚠ WHAT THE FIXTURE CANNOT DO, DECLARED RATHER THAN DISCOVERED: on this kernel's domain `memcmp` NEVER DECIDES ANYTHING. Every site that compares key bytes has already required `p->h == h` AND `p->nKeyLength == nKeyLength`, and the 64 keys have pairwise distinct 64-bit DJBX33A hashes, so the byte comparison runs on every match and always returns 0. Making it decide would need two distinct keys with an equal 64-bit hash, which is the same object the catalogue's `compute the preimage` instruction asked for and which is not constructible. `controls/differential.py`'s first draft mutated the `memcmp` and DID NOT FIRE ON A SINGLE WINDOW; that is recorded as a measurement rather than repaired away, and the test that discriminates -- the LENGTH one -- is mutated instead. NOTES.md section 8. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "hash_fold": "hash_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 49
    },
    "twin_obligations": {
      "verus.rs": 59
    },
    "obligations_note": "49 verified / 0 errors, and 59 under `--cfg slb_twin` -- TEN trusted accessors, therefore ten twins. ⚠⚠ WHAT IS PROVED IS NOT WHAT THE ROW'S DEFECT VIOLATES, AND THE ROW SAYS SO RATHER THAN LETTING IT BE ASSUMED. `kernel` returns `hash_fold(buf@, off, len)`, and `hash_fold` is a spec function that CARRIES `:464`'s disjunct -- so R5 verifies WITH THE DEFECT IN PLACE, exactly as R2, R3 and R4 reproduce it. What the proof buys is the ten accessors' index bounds, and they come from `wf`: every link is NIL or an in-range arena index, the bucket chain's `nxt` strictly DESCENDS and the global list's `lnxt` strictly ASCENDS. ⭐ Those two orderings are a consequence of `CONNECT_TO_BUCKET_DLLIST` prepending and `CONNECT_TO_GLOBAL_DLLIST` appending, they survive the delete because it only short-circuits `lst -> nxt` and `llst -> lnxt`, and they are what give both walks a `decreases` clause where `zend_hash.c` has none. ⛔ `wf` HOLDS WITH THE GUARD DELETED, which is this row's ladder result: memory safety and the upstream fix are ORTHOGONAL here, and only a KEY-IDENTITY obligation can see the difference. `controls/key_identity.py` builds that obligation in Verus three times -- hardened predicate + obligation VERIFIES, shipped predicate + obligation FAILS ON THE POSTCONDITION, shipped predicate + vacuous obligation VERIFIES -- so the difference is attributable to the PREDICATE and not to the file. NOTES.md sections 6 and 7. ⭐ THERE IS EXACTLY ONE `#[verifier::rlimit(120)]` IN THIS FILE, ON `del`, AND IT IS MEASURED. A first draft carried six; deleting all six from a copy of the shipped file gives `48 verified, 1 errors` with the single error `function body check: Resource limit (rlimit) exceeded` on `del`, and keeping only `del`'s gives `49 verified, 0 errors`. ▶ The other five were decoration and were removed. `del` is the expensive one because its lockstep postcondition rewrites four links, two list heads, the bucket table, the destructor counters and the allocator and proves the whole post-state equal to `s_del`'s output in one query. NOTES.md section 11a records both measurements.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 49 shipped + 10 for `slb_twin_{nref,set_nxt,set_lst,set_lnxt,set_llst,set_data,aget,aset,wsub,wb}`. ⚠ `slb_twin_wsub` needs one extra line the trusted item does not -- `assert(v@.len() == vstd::slice::spec_slice_len(v))` -- because `o + n <= v@.len()` alone does not stop `o + n` overflowing a `usize`; the broadcast group is what says a slice's length IS a `usize`, and the twin has to re-derive that where the `external_body` item simply asserts its way past it. That is the twin mechanism working: it found a precondition the trusted item was getting for free.",
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
        "s_kbyte": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_hash": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_kl": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_keyw": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_key": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_nkl": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ts_from": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ts": {
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
        "s_dtor": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_connect": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_find_str": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_find_idx": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_find_del": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ins_str": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ins_idx": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_del": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_foldk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_tail": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_run": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "g_init": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "hash_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_mask_le": {
          "external": null,
          "requires": [],
          "ensures": [
            "(h & m) <= m"
          ]
        },
        "nref": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < v@.len()"
          ],
          "ensures": [
            "*r == v@[i as int]"
          ]
        },
        "slb_twin_nref": {
          "external": null,
          "requires": [
            "(i as int) < v@.len()"
          ],
          "ensures": [
            "*r == v@[i as int]"
          ]
        },
        "set_nxt": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { nxt: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_nxt": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { nxt: x, ..old(v)@[i as int] })"
          ]
        },
        "set_lst": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { lst: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_lst": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { lst: x, ..old(v)@[i as int] })"
          ]
        },
        "set_lnxt": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { lnxt: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_lnxt": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { lnxt: x, ..old(v)@[i as int] })"
          ]
        },
        "set_llst": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { llst: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_llst": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { llst: x, ..old(v)@[i as int] })"
          ]
        },
        "set_data": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { data: x, ..old(v)@[i as int] })"
          ]
        },
        "slb_twin_set_data": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, Node { data: x, ..old(v)@[i as int] })"
          ]
        },
        "aget": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_aget": {
          "external": null,
          "requires": [
            "(i as int) < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "aset": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_aset": {
          "external": null,
          "requires": [
            "(i as int) < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
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
        "wb": {
          "external": "verifier::external_body",
          "requires": [
            "(i as int) < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_wb": {
          "external": null,
          "requires": [
            "(i as int) < v@.len()"
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
        "g": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "table_size": {
          "external": null,
          "requires": [
            "nrec <= 0x400_0000"
          ],
          "ensures": [
            "r as nat == s_ts(nrec as nat)",
            "8 <= r <= 0x800_0000",
            "nrec <= r"
          ]
        },
        "key_of": {
          "external": null,
          "requires": [
            "sel < NKEY"
          ],
          "ensures": [
            "r.0 == s_key(sel)",
            "r.1 == s_nkl(sel)",
            "r.1 >= 2",
            "r.1 <= 8"
          ]
        },
        "kbyte": {
          "external": null,
          "requires": [
            "i < 8"
          ],
          "ensures": [
            "r == s_kbyte(k, i as nat)"
          ]
        },
        "hash_of": {
          "external": null,
          "requires": [
            "nkl <= 8"
          ],
          "ensures": [
            "r == s_hash(k, nkl as nat)"
          ]
        },
        "alloc": {
          "external": null,
          "requires": [
            "old(self).cnt@.len() == MCM as int",
            "size <= 0x4000_0000"
          ],
          "ensures": [
            "final(self).g() == s_alloc(old(self).g(), size)",
            "final(self).cnt@.len() == MCM as int"
          ]
        },
        "free": {
          "external": null,
          "requires": [
            "old(self).cnt@.len() == MCM as int",
            "size <= 0x4000_0000"
          ],
          "ensures": [
            "final(self).g() == s_free(old(self).g(), size)",
            "final(self).cnt@.len() == MCM as int"
          ]
        },
        "dtor": {
          "external": null,
          "requires": [],
          "ensures": [
            "final(self).g() == s_dtor(old(self).g(), v)"
          ]
        },
        "connect": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "(i as int) == old(self).a@.len() - 1",
            "(n_index as int) < old(self).ar@.len()",
            "old(self).lhead == NIL || (old(self).lhead as int) < i as int",
            "old(self).ltail == NIL || (old(self).ltail as int) < i as int",
            "old(self).iptr == NIL || (old(self).iptr as int) < i as int",
            "forall|j: int| 0 <= j < old(self).ar@.len() ==> (#[trigger] old(self).ar@[j]) == NIL || ( old(self).ar@[j] as int) < i as int"
          ],
          "ensures": [
            "final(self).g() == s_connect(old(self).g(), i, n_index as int)",
            "wf(final(self).g())",
            "final(self).a@.len() == old(self).a@.len()",
            "final(self).cnt@.len() == MCM as int"
          ]
        },
        "find_str": {
          "external": null,
          "requires": [
            "wf(self.g())",
            "(n_index as int) < self.ar@.len()"
          ],
          "ensures": [
            "r == s_find_str(self.a@, self.ar@[n_index as int], h, nkl, key, self.a@.len())",
            "r == NIL || (r as int) < self.a@.len()"
          ]
        },
        "find_idx": {
          "external": null,
          "requires": [
            "wf(self.g())",
            "(n_index as int) < self.ar@.len()"
          ],
          "ensures": [
            "r == s_find_idx(self.a@, self.ar@[n_index as int], h, self.a@.len())",
            "r == NIL || (r as int) < self.a@.len()"
          ]
        },
        "find_del": {
          "external": null,
          "requires": [
            "wf(self.g())",
            "(n_index as int) < self.ar@.len()"
          ],
          "ensures": [
            "r == s_find_del(self.a@, self.ar@[n_index as int], h, nkl, key, self.a@.len())",
            "r == NIL || (r as int) < self.a@.len()"
          ]
        },
        "ins_str": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "nkl <= 8",
            "old(self).a@.len() < 0x3FFF_FFFF"
          ],
          "ensures": [
            "final(self).g() == s_ins_str(old(self).g(), key, nkl, data)",
            "wf(final(self).g())",
            "final(self).a@.len() <= old(self).a@.len() + 1"
          ]
        },
        "ins_idx": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "old(self).a@.len() < 0x3FFF_FFFF"
          ],
          "ensures": [
            "final(self).g() == s_ins_idx(old(self).g(), h, data)",
            "wf(final(self).g())",
            "final(self).a@.len() <= old(self).a@.len() + 1"
          ]
        },
        "del": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "nkl <= 8"
          ],
          "ensures": [
            "final(self).g() == s_del(old(self).g(), key, nkl, h0, del_key)",
            "wf(final(self).g())",
            "final(self).a@.len() == old(self).a@.len()"
          ]
        },
        "fold": {
          "external": null,
          "requires": [
            "wf(self.g())"
          ],
          "ensures": [
            "r == s_tail(self.g())"
          ]
        },
        "step": {
          "external": null,
          "requires": [
            "wf(old(self).g())",
            "old(self).a@.len() < 0x3FFF_FFFF"
          ],
          "ensures": [
            "final(self).g() == s_step(old(self).g(), ctl, b1, val)",
            "wf(final(self).g())",
            "final(self).a@.len() <= old(self).a@.len() + 1"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "4 <= len",
            "len <= 268435456"
          ],
          "ensures": [
            "r == hash_fold(buf@, off as int, len as int)"
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
        "nref": "The ONLY read accessor, and it returns a `&Node` rather than a scalar so that ten field reads cost one bound. `i < v@.len()` is the whole precondition and `wf` is what discharges it: every link this kernel follows is NIL or an in-range arena index, and the three chain walks (`find_str`, `find_idx`, `find_del`) and the global-list walk in `fold` each carry that as a loop invariant. ⚠ It ASSUMES NOTHING ABOUT THE NODE, only that the index is in range -- `ensures *r == v@[i as int]` is the whole post-state, so a body that returned a different slot or a modified copy could not satisfy it.",
        "set_nxt": "`x: u32` is a PURE VALUE and needs no precondition: every one of the 2^32 values is a legal `u32` store into a field `Vec::push` initialised before any link pointed at it. The unchecked operation is `v.get_unchecked_mut(i as usize).nxt = x`, whose definedness depends on `i` being in bounds and on nothing about what is written. ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: the delete is a pair of NEIGHBOUR writes in each of two lists -- `p->pLast->pNext = p->pNext` / `p->pNext->pLast = p->pLast` at zend_hash.c:470-475 and `p->pListLast->pListNext` / `p->pListNext->pListLast` at :477-484 -- so an `ensures` naming only `v@[i].nxt == x` would license a body that also moved a neighbour's link, which is exactly the class the C makes easy. The shipped `ensures` is the WHOLE post-state, `old(v)@.update(i, Node { nxt: x, ..old(v)@[i] })`, so a body that touched any other slot or any other FIELD could not satisfy it. Miri is the backstop for the class regardless (../spec.md `miri`).",
        "set_lst": "`x: u32` is a PURE VALUE and needs no precondition: every one of the 2^32 values is a legal `u32` store into a field `Vec::push` initialised before any link pointed at it. The unchecked operation is `v.get_unchecked_mut(i as usize).lst = x`, whose definedness depends on `i` being in bounds and on nothing about what is written. ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: the delete is a pair of NEIGHBOUR writes in each of two lists -- `p->pLast->pNext = p->pNext` / `p->pNext->pLast = p->pLast` at zend_hash.c:470-475 and `p->pListLast->pListNext` / `p->pListNext->pListLast` at :477-484 -- so an `ensures` naming only `v@[i].lst == x` would license a body that also moved a neighbour's link, which is exactly the class the C makes easy. The shipped `ensures` is the WHOLE post-state, `old(v)@.update(i, Node { lst: x, ..old(v)@[i] })`, so a body that touched any other slot or any other FIELD could not satisfy it. Miri is the backstop for the class regardless (../spec.md `miri`).",
        "set_lnxt": "`x: u32` is a PURE VALUE and needs no precondition: every one of the 2^32 values is a legal `u32` store into a field `Vec::push` initialised before any link pointed at it. The unchecked operation is `v.get_unchecked_mut(i as usize).lnxt = x`, whose definedness depends on `i` being in bounds and on nothing about what is written. ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: the delete is a pair of NEIGHBOUR writes in each of two lists -- `p->pLast->pNext = p->pNext` / `p->pNext->pLast = p->pLast` at zend_hash.c:470-475 and `p->pListLast->pListNext` / `p->pListNext->pListLast` at :477-484 -- so an `ensures` naming only `v@[i].lnxt == x` would license a body that also moved a neighbour's link, which is exactly the class the C makes easy. The shipped `ensures` is the WHOLE post-state, `old(v)@.update(i, Node { lnxt: x, ..old(v)@[i] })`, so a body that touched any other slot or any other FIELD could not satisfy it. Miri is the backstop for the class regardless (../spec.md `miri`).",
        "set_llst": "`x: u32` is a PURE VALUE and needs no precondition: every one of the 2^32 values is a legal `u32` store into a field `Vec::push` initialised before any link pointed at it. The unchecked operation is `v.get_unchecked_mut(i as usize).llst = x`, whose definedness depends on `i` being in bounds and on nothing about what is written. ⚠⚠ WHAT THE CONTRACT MUST NOT LEAVE OUT, AND THIS IS THE ROW WHERE IT BITES: the delete is a pair of NEIGHBOUR writes in each of two lists -- `p->pLast->pNext = p->pNext` / `p->pNext->pLast = p->pLast` at zend_hash.c:470-475 and `p->pListLast->pListNext` / `p->pListNext->pListLast` at :477-484 -- so an `ensures` naming only `v@[i].llst == x` would license a body that also moved a neighbour's link, which is exactly the class the C makes easy. The shipped `ensures` is the WHOLE post-state, `old(v)@.update(i, Node { llst: x, ..old(v)@[i] })`, so a body that touched any other slot or any other FIELD could not satisfy it. Miri is the backstop for the class regardless (../spec.md `miri`).",
        "set_data": "`x: u64` is a PURE VALUE -- it is the projected `zval *` the bucket stores, and `_zend_hash_add_or_update`'s and `_zend_hash_index_update_or_next_insert`'s UPDATE arms are its two call sites (zend_hash.c:232, :364, through `UPDATE_DATA`). It is the only write this kernel makes that is NOT a link, and its `ensures` is the whole post-state for the same reason the four link setters' are: `UPDATE_DATA` is a macro that writes TWO fields in C (`pDataPtr` and `pData`), and the second is a self-pointer this row projects away, so a partial `ensures` here would be the one place a reader could not tell the projection from an omission.",
        "aget": "`ht->arBuckets[nIndex]` and the size-class cache counter, which are the same Rust type and therefore the same accessor. ⭐ THE BOUND IS DISCHARGED WITHOUT ANY POWER-OF-TWO FACT, and that is deliberate: `wf` carries `ar.len() == mask + 1`, and `lemma_mask_le` is the one bit-vector fact in the file -- `h & m <= m`, universally true -- so `(h & mask) as usize <= mask < ar.len()`. A proof that needed `ts` to be a power of two would have needed a symbolic shift in the bit-vector solver; this one needs nothing. For the cache, `idx < MCM` is tested in the exec code and `wf` carries `cnt.len() == MCM`.",
        "aset": "The write half of `aget`, with the same bound from the same place, and `ensures final(v)@ == old(v)@.update(i as int, x)` -- the whole post-state, so a body that also moved another slot of `arBuckets` (which `zend_hash_rehash` would) could not satisfy it. That is not hypothetical on this row: `idiom.forbidden[1]` pins `zend_hash_do_resize` absent precisely because a rehash rewrites every entry of this array.",
        "wsub": "`&buf[off..off + len]`, spelled so Verus knows the view. `o + n <= v@.len()` is the kernel's own first `requires` and the driver loop discharges it from the multiply-shift barrier bound. ⚠ ITS TWIN NEEDS A LINE THE TRUSTED ITEM DOES NOT -- `assert(v@.len() == vstd::slice::spec_slice_len(v))` -- because `o + n <= v@.len()` alone does not stop `o + n` overflowing a `usize`. That is the twin mechanism earning its place: it found a precondition the `external_body` item was getting for free.",
        "wb": "One window byte. `i < v@.len()` comes from `nrec * 4 <= win@.len()` and `r < nrec`, which the record loop carries as an invariant. It is the only place attacker data enters the kernel and it asserts nothing about the byte -- `ensures r == v@[i as int]` -- which is the point: every one of the 256 values is a legal record byte and the kernel's job is to be correct on all of them."
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
      "if stride_w >= 4 && stride_w <= 268435456 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph66's two probe shapes have different work per call (66 and 517 window bytes, i.e. 16 and 129 key-stream records) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW IN BYTES and the record count is `stride / 4` truncated, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ AND THE PER-RECORD WORK IS NOT CONSTANT, which this row says rather than presenting the marginal as a per-byte rate: an insert of a NEW key walks its chain, allocates a bucket and links it into two lists; an insert of an EXISTING key walks the chain and writes one word; a failing delete walks the chain and does nothing. ⭐ The BUCKET TABLE is also sized from the same `nrec`, so chain length -- and therefore walk cost -- is itself a function of the denominator. NOTES.md section 9 decomposes it."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "differ",
      "why": "⚠⚠ R4 AND R5 DIFFER AT BOTH LEVELS, AND THE O3 FIGURE IS THE INTERESTING ONE. Measured, `results-php/ph66-hashdel-uncompared.json` and `results-php/gate/ph66-hashdel-uncompared.json`, O3/isolated: **791 instructions / 3231 bytes for `unsafe` against 770 / 3125 for `verus`** -- so `md5_fn` and `md5_fn_norel` both differ and no `norel` claim is available. ⭐ THE PROOF RUNG IS THE SMALLER ONE, by 21 instructions (18 excluding padding) and 106 bytes. That is a codegen coin flip and NOT a result about verification; it is quoted here so nobody reads `differ` as *the proof costs something*, and NOTES.md section 11 gives the run-time figure beside it. ⚠ At O0 the two differ for the ordinary reason: nothing is inlined, so R5's ten trusted accessors and its `Ht` construction survive as real calls and extra scaffolding where R4 open-codes them -- 106 / 509 against 170 / 977. ⭐⭐ AND THE SHAPE OF THE TWO `kernel` FUNCTIONS WAS MADE THE SAME BEFORE THIS ENTRY WAS WRITTEN, WHICH IS THE PART WORTH CARRYING. As first built, `verus.rs` split the record loop into a `run` helper (Verus wants the window bound stated once) and `unsafe.rs` did not, so at O0 the measured symbol was a 14-instruction wrapper on one side and the whole loop on the other: `identity_level` said `differ` about a difference that was entirely the split. Both rungs now carry the loop in `kernel`, which is also what gate stage 3a wants -- a `kernel` window with no backward branch is a collapsed cell. ⚠ THE PIN IS `differ` AND NOT `norel`, and `kernel_fingerprint` is PATH-SENSITIVE and has fired live in both directions on this project (F101, item 109), so the row directory name is a fixed-width 23-character slug in the same length class as `ph96-outparam-unwritten`. ▶ A `whole`-mode pin is NOT claimed: the gate compares the `isolated` cells, and in `whole` mode the kernel is inlined into `main` and there is no common symbol to compare. ⚠ The figures here are an EVENT: they were read from those two records at the commit this row landed at, and PROTOCOL.md rule 6's addendum says to re-read this entry against the records rather than trusting the prose."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph66 has TEN, and FIVE of them WRITE (`set_nxt`, `set_lst`, `set_lnxt`, `set_llst`, `set_data`). ⚠⚠ IT MATTERS MORE HERE THAN ON A ROW WHOSE UNCHECKED WRITES ARE TO ITS OWN SCRATCH BUFFER: the delete is a pair of NEIGHBOUR writes in each of two lists -- `pLast->pNext` and `pNext->pLast`, `pListLast->pListNext` and `pListNext->pListLast` -- so a write wrapper whose `ensures` named only its own slot would license a body that also moved a neighbour's link. Every shipped `ensures` is the whole post-state, `old(v)@.update(i, Node { field: x, ..old(v)@[i] })`. ⭐ AND WHAT MIRI IS EXPECTED TO REPORT IS NOTHING, on every input including every adversarial one: this row's defect is a wrong boolean and there is no UB to detect. That is prediction P2 and NOTES.md section 7 scores it.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph66's cost is 4 x (one window of 16 or 129 key-stream records built into a bucket table and folded), i.e. three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_hash.c",
    "c_lines": [
      450,
      503
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '450,503p'",
    "extract_sha256": "d232e484baf894775ceb088691ee5406d1688151a9a739dfc646b745f72963e5",
    "extra_spans": [
      {
        "c_file": "Zend/zend_hash.h",
        "c_lines": [
          48,
          58
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.h | sed -n '48,58p'",
        "extract_sha256": "1cdb042eaf291eb1b85686049145f95b81c18342a8f810340b14ef6ea58e4dfa",
        "why": "`Bucket`. ⚠⚠ `nKeyLength` IS A FIELD OF THE BUCKET AND `arKey[1]` IS LAST, and both facts are load-bearing: the first is what the defect tests instead of the key, the second is what makes `sizeof(Bucket)-1+nKeyLength` the allocation request and therefore what decides the size class. `c/kernel.c::ph66_layout_assert` holds this file's own Bucket to `sizeof(Bucket)-1 == 71` at COMPILE time, so a padding change on another ABI is a build failure and never a silent disagreement with model.py's `BUCKET_BASE`."
      },
      {
        "c_file": "Zend/zend_hash.h",
        "c_lines": [
          60,
          76
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.h | sed -n '60,76p'",
        "extract_sha256": "c204885bdb034d8f4931973bea4e9e89eb4dca6841c94d58398214c1fbb935b1",
        "why": "`HashTable` -- `nTableSize`/`nTableMask`/`nNumOfElements`/`nNextFreeElement`, the two list heads, `arBuckets` and `pInternalPointer`. ⭐ `pInternalPointer` is why this defect has no use-after-free variant: the delete repairs it four lines above the free, so the bucket's one external alias is gone before the block is."
      },
      {
        "c_file": "Zend/zend_hash.h",
        "c_lines": [
          243,
          270
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.h | sed -n '243,270p'",
        "extract_sha256": "52b4484bdc47f136449c4d57f474be24e8b1ed36c888d75dfb7561ec6daac0d3",
        "why": "`zend_inline_hash_func` -- DJBX33A accumulating in a `ulong`, i.e. 64-bit on LP64, unrolled eight times with a `switch` tail. ⚠ The 64-bit accumulator is what makes a PREIMAGE infeasible and the FORWARD direction free, which is the whole of why this row needs no search. `nKeyLength` spans 2..8 here, so both arms run."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          24,
          42
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '24,42p'",
        "extract_sha256": "d661d1f961a9c9736cb18faceb7d3bf449ac93083e325b8fd0caddb9d86814de",
        "why": "`CONNECT_TO_BUCKET_DLLIST` and `CONNECT_TO_GLOBAL_DLLIST`. ⭐⭐ ONE PREPENDS AND THE OTHER APPENDS, and that asymmetry is the whole of `verus.rs`'s `wf`: bucket chains descend in insertion order and the global list ascends, which is what gives both walks a `decreases` clause and what `model.py::_dumb` turns into a link-free `max(seq)` lookup."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          103,
          133
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '103,133p'",
        "extract_sha256": "1dbd022d060172b9a33be25bad4f9de7adfd94217db68c7d28a3285c5f2015dc",
        "why": "`UPDATE_DATA` and `INIT_DATA`. ⚠ `INIT_DATA`'s definition carries a STRAY SEMICOLON after its parameter list -- `#define INIT_DATA(ht, p, pData, nDataSize);` -- so every expansion begins with an empty statement. Reproduced verbatim rather than tidied. The `nDataSize == sizeof(void*)` arm is the one a PHP array takes, because an array stores a `zval *`."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          137,
          176
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '137,176p'",
        "extract_sha256": "87674f645087da0ece0c08b61513f104097af223a8ccd6994edd528a4573edcd",
        "why": "`_zend_hash_init` -- `while ((1U << i) < nSize) i++;` from `i = 3`, so the smallest table is 8. The kernel passes the record count as `nSize`, which is the `zend_hash_init(ht, n, ...)` spelling PHP uses wherever the size is known and is what makes the resize path unreachable."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          195,
          263
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '195,263p'",
        "extract_sha256": "e498e461ea1465b77e9efa7aa6bc19dcf34f0be15770688bf56b760b00698f34",
        "why": "`_zend_hash_add_or_update`. ⭐⭐ ITS PREDICATE AT `:215` IS ALREADY THE REPAIR'S OWN FORM -- `(p->h == h) && (p->nKeyLength == nKeyLength)`, two required conjuncts -- which is the census's point and this file's own answer to *nobody knew*. Nine of the file's ten `p->h == h` predicates spell it that way; `:464` is the tenth."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          342,
          407
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '342,407p'",
        "extract_sha256": "19440d54d98cceb057dbd631af93c26d68798e6ef69f3266c4c50164531df133",
        "why": "`_zend_hash_index_update_or_next_insert`. Two load-bearing lines: `:387` marks a numeric bucket with `p->nKeyLength = 0` IN UPSTREAM'S OWN COMMENT, and `:388` stores `p->h = h` with `h` the RAW user index -- which is what makes the collision constructible by running the hash forwards. ⚠ Its own predicate at `:356` is `(p->nKeyLength == 0) && (p->h == h)`: a required conjunct, the correct form, in the function that CREATES the bucket the delete then mis-selects."
      },
      {
        "c_file": "Zend/zend_hash.c",
        "c_lines": [
          506,
          529
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_hash.c | sed -n '506,529p'",
        "extract_sha256": "4b313586fa46e4f567b3e4e62ff4ddfefe1856a5a037524ee42a5717967d00a2",
        "why": "`zend_hash_destroy` -- what the kernel calls at the end of every call so that call N does not depend on call N-1. Its `if (!q->pDataPtr && q->pData)` is the same test the delete makes, one function over, and it is why the kernel's payload is never zero."
      }
    ],
    "extra_spans_note": "TEN SPANS, ALL IN ONE CONSTRUCT, AND THE PRIMARY IS THE CITED LINE. ⭐ THAT IS UNUSUAL FOR THIS PROGRAMME AND IT IS WHY THE ROW IS CHEAP: `.memory-php/01-extraction.md`'s F1 says `c_file_line` usually names the FAULTING FRAME, one call up from the defect, so a row's primary span and the corpus's citation normally differ. Here they do not -- `index.csv` cites `Zend/zend_hash.c:464-465` and that IS the defect -- because a non-crash class has no faulting frame to name instead. Every other span is a sibling in the same file or its header, and `.tasks-php/probes/ph66_djbx33a_collide.py` enumerates the whole population the row is claiming about (ten `p->h == h` predicates, nine of them already correct). Each entry is checked exactly as the primary is (in the manifest, in range, canonical extract_cmd, extract_sha256 over the bytes `sed` prints), and the kernel overlap is computed over the UNION.",
    "tier": "verbatim",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC and ZEND_FILE_LINE_DC / ZEND_FILE_LINE_CC / ZEND_FILE_LINE_ORIG_DC",
        "kind": "deletion",
        "where": "zend_hash.c:137, :195, :342 (the three lifted signatures)",
        "why": "thread plumbing and debug-allocator call-site plumbing, no semantics"
      },
      {
        "what": "the ZEND_DEBUG arms -- IS_CONSISTENT, SET_INCONSISTENT, the two ZEND_PUTS blocks and EMPTY_SWITCH_DEFAULT_CASE",
        "kind": "deletion",
        "where": "zend_hash.c:44-72 (the `#else` arm is what the shipped build takes), :218-224, :361-367; zend_hash.h:267",
        "why": "the shipped 5.0.0 build is not a debug build, so these expand to nothing; keeping them would ADD checks PHP does not do. No semantics."
      },
      {
        "what": "HANDLE_BLOCK_INTERRUPTIONS() / HANDLE_UNBLOCK_INTERRUPTIONS() -> nothing",
        "kind": "projection",
        "where": "zend.h:514-515, expanded at zend_hash.c:226, :237, :254, :258, :370, :373, :396, :399, :466, :487",
        "why": "both are `if (zend_block_interruptions) { zend_block_interruptions(); }` through a function pointer the SAPI installs; the CLI installs neither, so both are `if (NULL) {}` on every path this kernel takes. No semantics on the extracted domain."
      },
      {
        "what": "pemalloc/pemalloc_rel/pefree/pefree_rel/ecalloc_rel -> php_shim_emalloc/php_shim_efree/php_shim_ecalloc",
        "kind": "substitution",
        "where": "zend_hash.c:160, :239, :383, :492, :494, :522, :524, :526",
        "why": "`array()` is `ZEND_INIT_SYMTABLE_EX(ht, 2, 0)` (zend_hash.h:287-288), i.e. `persistent == 0`, and `Zend/zend_alloc.h`'s `pemalloc(size, 0)` IS `emalloc(size)` and `pefree(p, 0)` IS `efree(p)`. common-php/emalloc_shim.h IS PHP 5.0.0's own `_emalloc`/`_efree`/`_ecalloc`, line-cited to the same tarball, so this is a redirection to the same code and not a substitution of a different allocator. No semantics."
      },
      {
        "what": "the `persistent` arm of _zend_hash_init's table allocation (the `calloc` branch)",
        "kind": "projection",
        "where": "zend_hash.c:161-167",
        "why": "`persistent` is 0 on every call this kernel makes, so the `calloc` branch is unreachable. No semantics on the extracted domain."
      },
      {
        "what": "the `nDataSize != sizeof(void*)` arms of UPDATE_DATA and INIT_DATA",
        "kind": "projection",
        "where": "zend_hash.c:110-119, :126-132",
        "why": "every call site passes `sizeof(void *)`, which is what a PHP array does (it stores a `zval *`), so the other arm is unreachable and its `perealloc` is never made. No semantics on the extracted domain."
      },
      {
        "what": "ZEND_HASH_IF_FULL_DO_RESIZE and zend_hash_do_resize / zend_hash_rehash",
        "kind": "narrowing",
        "where": "zend_hash.c:88-92, :261, :405, :410-448",
        "why": "the kernel calls `_zend_hash_init(&ht, nrec, ...)` -- a real PHP spelling wherever the size is known -- so `nTableSize >= nrec >= nNumOfElements` and `nNumOfElements > nTableSize` is unreachable. ⚠ IT IS A NARROWING OF THE DOMAIN AND NOT OF THE CODE, and it is declared because a rehash REORDERS EVERY CHAIN and chain order is what decides which element this defect destroys. `spec.md`'s `idiom.forbidden[1]` pins it absent on every rung so no rung can acquire it unilaterally. No semantics on the extracted domain."
      },
      {
        "what": "ht->pDestructor = ZVAL_PTR_DTOR -> a counter and a fold of the destroyed value",
        "kind": "projection",
        "where": "zend_hash.h:288 (the installation); zend_execute_API.c:388-408 (_zval_ptr_dtor)",
        "why": "`_zval_ptr_dtor` decrements a refcount and frees only at zero. Every payload in this kernel is held exactly once, so the destructor's reachable behaviour is *the value is destroyed now*; the projection records THAT as a count and a fold, which is what makes WHICH element died visible in the u64 and not only in the surviving-key list. ⭐ It is also the half that explains why the row has no use-after-free variant, and NOTES.md section 3 states it. No semantics on the extracted domain."
      },
      {
        "what": "pData is a non-zero tagged integer rather than a zval pointer",
        "kind": "projection",
        "where": "zend_hash.c:492-494 (`if (!p->pDataPtr) pefree(p->pData, ...)`), :521-523",
        "why": "PHP stores a `zval *`, which is never NULL, so `if (!p->pDataPtr)` is never taken and `pefree(&p->pDataPtr)` -- a free of an INTERIOR pointer -- is unreachable. This kernel stores `0x10000 | val`, which is likewise never zero, so it takes the same arm PHP takes. ⛔ THE DIRECTION MATTERS AND IS THE REASON THIS ENTRY EXISTS: a payload that could be zero would make the kernel free an interior pointer, i.e. introduce UB THE C ORIGINAL DOES NOT HAVE, and this row's whole value is that every free in it is a correct free. No semantics on the extracted domain."
      },
      {
        "what": "the four Rust rungs carry `char arKey[]` PACKED into one u64, zero-filled past nKeyLength",
        "kind": "substitution",
        "where": "zend_hash.h:57 (the field), zend_hash.c:238 (the memcpy), :215 and :465 (the two memcmp sites)",
        "why": "the kernel's keys are at most 8 bytes including the NUL, so the whole key is one word. Packed equality agrees with `memcmp(p->arKey, arKey, nKeyLength)` because EVERY site that compares key bytes has already required `p->nKeyLength == nKeyLength`, and two zero-filled words of equal length agree on all eight bytes exactly when they agree on the first `nKeyLength`. ⚠ DEMONSTRATED AND NOT ASSERTED, as PROTOCOL_PHP.md A1 clause (c) requires: `controls/differential.py` drives the SHIPPED C against three independent model implementations over 94 off-corpus windows with five must-fire mutations, one of which (N2a) is exactly the claim that every byte of the packed word is observable. No semantics on the reachable domain."
      },
      {
        "what": "the four Rust rungs write zend_inline_hash_func's loop ROLLED",
        "kind": "substitution",
        "where": "zend_hash.h:247-268",
        "why": "`hash * 33` IS `(hash << 5) + hash` and an eightfold unrolling with a `switch` tail computes the same function as the rolled loop for every length. `controls/differential.py`'s N3 mutation shortens the hash and is CAUGHT, so the two are checked against each other over a domain that reaches `nKeyLength == 8`. No semantics."
      },
      {
        "what": "the four Rust rungs represent `Bucket *pNext` / `pLast` / `pListNext` / `pListLast` as u32 ARENA INDICES",
        "kind": "substitution",
        "where": "zend_hash.h:53-56",
        "why": "safe Rust cannot express two intrusive doubly-linked lists over one heap without `Rc`, `RefCell` or raw pointers, so the faithful safe port owns an arena and links by index; `pefree` becomes *unlink and stop being reachable*. ⭐ UNLIKE ph64, THE SUBSTITUTION IS INVISIBLE HERE, and the reason is the row: ph64's cursor READ A LINK OUT OF A FREED BLOCK, so the arena changed what the read returned. This kernel never reads a freed bucket at all -- the delete unlinks from both lists and from pInternalPointer before freeing -- so the arena changes nothing observable and `controls/differential.py` measures the two computing the same function. What the arena buys is the `decreases` clause R5 needs. No semantics on the extracted domain."
      },
      {
        "what": "the four Rust rungs reproduce php_shim_tally() arithmetically instead of linking the shim",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:346-435, :642-648",
        "why": "harness/build.py compiles exactly three C translation units and no Rust rung links C. Each Rust rung carries the same per-size-class LIFO cache model driven by the SAME request sequence, so `n_alloc`, `n_free`, `n_cache_hit` and `bytes_mallocked` are equal by construction; `controls/differential.py`'s N4 mutation deletes the cache and is CAUGHT. This pins the ALLOCATION SEQUENCE across rungs and is NOT evidence that any Rust rung ran PHP's allocator. No semantics."
      },
      {
        "what": "the driver guard carries a third conjunct, `stride_w <= 268435456`",
        "kind": "narrowing",
        "where": "c/main.c and all four .rs drivers",
        "why": "a `u32` arena index is sound while the arena holds fewer than 2^32 buckets, and a bucket costs a 4-byte record, so a 256 MiB ceiling on the WINDOW gives at most 2^26 buckets with 64x to spare. It is a structural precondition of the REPRESENTATION, it is verus.rs's third `requires`, and all six rungs carry it so no rung is measured over a domain another refuses. The largest window this row ships is 517 bytes. No semantics on the measured domain."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection / narrowing and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⭐⭐ EVERY ONE OF THESE FOURTEEN `why` STRINGS ENDS IN *no semantics*, WHICH IS WHAT `verbatim` MEANS AND IS ALSO THE ROW'S MOST FRAGILE CLAIM -- so two of them are MEASURED rather than argued. The u64 key packing and the rolled hash are both differentials with must-fire controls (`controls/differential.py`, PROTOCOL_PHP.md A1 clause (c)), and the allocator-tally reproduction is a third. ⚠ THE TIER IS DECLARED AS `verbatim` AND THE NARROWING THAT COULD COST IT IS NAMED: the resize path is out of the extraction because the kernel sizes its table from the record count. That is a narrowing of the DOMAIN by a real PHP spelling, not an edit to any lifted body -- every function this row lifts is lifted whole -- and NOTES.md section 10 argues it rather than assuming it.",
    "root_cause_ids": [
      "hash-del-key-or-index-numeric-bucket-short-circuits-key-length-check-destroys-unrelated-live-element"
    ],
    "cwe": "CWE-843",
    "cwe_note": "⚠⚠ `index.csv` RECORDS `CWE-416` FOR LOGIC-001 AND THIS ROW DOES NOT REPRODUCE THAT CLASS, WHICH IS A FINDING TO STATE AND NOT A FAILURE TO HIDE (PROTOCOL_PHP.md A4). Measured on a real PHP 5.0.0 CLI, `.tasks-php/probes/ph66_key_identity.sh`, five cells including one where a live reference still holds the victim: ALL FIVE EXIT 0, none faults, and nothing is read after it is freed. The corpus's own row agrees with the measurement where it counts -- its `crashes_pristine_5_0_0` column reads `n/a (non-crash class)` -- so the `CWE-416` label and the `refcount-logic` family it sits in are the index's classification and not an observation. ⭐ WHAT THE DEFECT IS INSTEAD: a container operation acts on a bucket whose key it never compared, because hash equality was allowed to stand in for key identity across a KEY-KIND boundary. The nearest CWE is 843 (type confusion) with the *type* being the key kind, and the corpus's own labeller reached the same place from the other direction -- `paper/_old_story/invariants-166.json` `cases[98]` proposes a NEW invariant, `NEW:container-key-identity`, and files `I7` only because a freeze rule forbids new entries. `CWE-416` is carried here UNCHANGED because the corpus's columns are carried across unmodified by design; NOTES.md section 6 states the disagreement.",
    "fix_commit": "b73349dbe4e9",
    "fix_commit_note": "⭐⭐ ONE COMMIT, ONE FILE, ONE HUNK, AND IT APPLIES TO THE PRISTINE TARBALL VERBATIM. `b73349dbe4e99e837703552ba18c91bbe95f6e99` -- Zeev Suraski <zeev@php.net>, 2006-02-01 01:01:05 +0000, *Fix possibility of a wrong element being deleted by zend_hash_del()  Thanks Stefan!*. 4 added / 2 deleted lines in `Zend/zend_hash.c`, and `patch -p1` against php-5.0.0 returns 0 with no fuzz and no offset. Patch bytes at `controls/b73349dbe4e9.patch` (sha256 92fd3a1e31744dc5289ff1f5912ff1a37b3d766a76466a4a8546fec67990fa31); `controls/r1h_apply.py` re-derives the application from the pinned tarball on every run and diffs the result's predicate against `c/kernel_hardened.c`'s, with must-fire negatives. ⚠ THE BINDING IS VERIFIED AGAINST THE BYTES AND NOT AGAINST THE COLUMN (PROTOCOL_PHP.md §C, F38/F118): the commit's subject names the exact harm, its hunk is at the exact cited lines, and the post-image predicate is the one `.tasks-php/probes/ph66_djbx33a_collide.py` classifies `guarded` where the pre-image is `dual`. `preimage_screen.py --row ph66` returns one record labelled `CANDIDATE`, which is SILENCE and not support (F68/F95) -- the patch BODY is what decides it. ⭐⭐ AND ITS EFFICACY IS MEASURED ON REAL PHP, not argued: `.tasks-php/probes/rebuild_hardened_php.sh --label ph66` builds pristine 5.0.0, runs the trigger, applies this patch, rebuilds and runs it again. NOTES.md section 4 carries the two images side by side.",
    "invariant": "I7",
    "obligation": "O2",
    "echoes": [
      "p22"
    ],
    "echoes_note": "`p22` is the PAT analogue the catalogue names. PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and NEVER a filter. ⚠ The mechanisms differ where it matters: a PAT row's key comparison is invented, so its domain can be chosen to make the byte comparison decide; here the key comparison is `memcmp` against a 64-bit-hashed bucket and it can NEVER decide, because two distinct keys with an equal 64-bit DJBX33A hash are not constructible. That is a property of the extracted construct and it is the row's sharpest limitation -- NOTES.md section 8.",
    "uses_allocator": true,
    "uses_allocator_why": "`c/kernel.c` makes ONE `php_shim_ecalloc` for `ht->arBuckets` plus ONE `php_shim_emalloc` per bucket INSERTED and ONE `php_shim_efree` per bucket DELETED, per kernel call, and a final `zend_hash_destroy` sweep after the tally is read. ⚠⚠ THE PER-CALL ALLOCATION COUNT IS THEREFORE O(nrec) AND NOT O(1), AND PROTOCOL_PHP.md §B1a's PRECONDITION DOES NOT HOLD ON THIS ROW. ⛔ That is a FINDING and never a refusal (§B1a decision 1, CLAUDE.md Don't 6): what it costs is that a CROSS-LANGUAGE figure on this row includes allocator work on the C side against arithmetic on the Rust side, so every such figure is labelled, and the row publishes no bare C-vs-Rust headline without that label. ⭐ The POSITIVE half is unaffected: R2-vs-R3 and R4-vs-R5 allocate identically, so the allocator term CANCELS in a same-language ratio and the fixed-R4 bound is clean. NOTES.md section 9. ⭐⭐ AND THE ALLOCATOR IS NOT BACKGROUND HERE, it is half the oracle: the tally is folded into the u64, so a delete that removed a bucket and a delete that removed nothing differ in `n_free` as well as in the surviving-key list. The truncations T1/T2/T3 do NOT fire -- every request is 71..79 bytes or the 8*nTableSize table -- so this row exercises the CACHE half of emalloc_shim.h and none of the overflow half, and `controls/differential.py`'s N4 mutation is what checks the Rust and Python cache models against the SHIPPED shim rather than against each other.",
    "obligation_note": "⚠⚠ `CATALOGUE.md` CARRIES `I7/O2 + I7/O3` AND THIS ROW DOES NOT EDIT IT -- the axis, the family and the invariant columns are the corpus's and are carried across unmodified. But `I7/O2` and `I7/O3` are REFCOUNT obligations, and a Verus proof about refcounts is not the proof this row needs: the defect never miscounts a holder, it picks the wrong bucket. ⭐ R5's obligation is stated instead as the corpus labeller's own `NEW:container-key-identity` -- *a hash-table operation acts on the bucket whose key equals the requested key in both key kind and key bytes, and on no other bucket* -- and `controls/key_identity.py` builds exactly that in Verus, where it verifies against `b73349dbe4e9`'s predicate and fails on the postcondition against 5.0.0's. NOTES.md section 6 quotes the labeller's note in full as the corpus artefact it is, and records that the labeller's own `T3`-honesty sub-rule fires here and has nowhere to send the case."
  }
}
```
