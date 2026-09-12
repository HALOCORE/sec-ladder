# ph53 — storage grown to the COUNT, and the tail is never written

**PHP 5.0.0, `Zend/zend_compile.c:2569-2572` with `:2591`, `:1951`,
`Zend/zend_operators.c:1534-1535` and `:3747-3748`, corpus row CRASH-158, tier
`narrowed`.** `ce->num_interfaces` is advanced once per `implements` clause at
compile time and **no slot is written**; `:2570-2571` then grows the storage to
that count and leaves it indeterminate. A consumer that runs before every
`ZEND_ADD_INTERFACE` has executed reads a slot nobody wrote.

⚠⚠⚠ **The read is IN BOUNDS.** The slot is inside the reallocated block and
nothing has been freed: **CWE-824**, not CWE-125. No built row in either
programme prices that. `ph32` is the cross-reference and not the duplicate —
same C shape, sized to the *literal*, so its excess is past the end.

⚠⚠ **And the 2005 upstream fix does not remove the fault — it makes it
deterministic, at two different severities.** `d09cdd9f71f3` zeroes the array
and adds no consumer guard, so `zend_operators.c:1535` becomes a **NULL
dereference** and `zend_compile.c:1951` becomes a **correct answer**. One hunk,
two severities, and that is why this kernel ships both consumers. `NOTES.md` §5
has the measurement.

⚠⚠ **The corpus column's `fix_commit` is the wrong one and both shas are cited
below** — `be8daf1f47fa` (2008) is excluded twice independently, and the commit
that removes the 5.0.0 defect is `d09cdd9f71f3` (2005). `provenance.fix_commit_note`.

⭐⭐ **The ladder is four answers to one question — *was this slot written?*** —
and one of them is that the question cannot be answered at all: a faithful
witness-free R4 **cannot be verified**, because coverage is a property of
attacker data and the pinned driver loop offers no call site at which to
establish it. `NOTES.md` §11 and `controls/r4_nowitness.rs`.

The machine-readable contract follows.
`harness-php/gate.py ph53-iface-tail-uninit` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "76 <= len"
  ],
  "ensures": [
    "result == iface_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (iface_fold). ⚠⚠ model.py's `iface_fold` IS ITS SECOND, INDEPENDENT IMPLEMENTATION and not the simulation that produced `result`: `_window` is an imperative transcription of c/kernel_hardened.c with the cursors named as the C names them and a mutable slot list, while `iface_fold` mirrors verus.rs's `scan_d` / `scan_c` / `run_ops` as pure transitions driven to a fixpoint. A THIRD spelling, `_dumb`, snapshots the slot array before every op and answers each query against that snapshot from scratch, sharing no code with either; it checks every shipped window. ⭐ AND model.py CANNOT EXPRESS THE DEFECT: there is no Python spelling of \"read a slot nobody wrote\", so its unwritten slot is `None` and is SKIPPED. That makes it a genuinely independent second opinion -- it agrees with both C rungs on every measured window and on three of the five adversarial ones, and where the defect is REACHED the C's answer is recorded by check.py stage 4 rather than required to agree. It is also a small statement of this row's own ladder result. selfcheck() drives the two implementations against each other on the calls each input makes AND on 90 SYNTHETIC windows model.py builds itself, spanning n_decl_w 0..32 (past one wrap of the `% 17`), n_pool_w 0..15, seven op orderings x four counts -- including queries-before-fills, out-of-order fills, repeated fills and no fills at all, i.e. every uninitialised-slot shape the measured corpus is FORBIDDEN to contain -- the four scan arms, duplicate pool ids and an empty op stream. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. ⭐⭐ AND THE SWEEP CARRIES ITS OWN CONTROLS, because a sweep that cannot fail is not a check (PROTOCOL_PHP.md H): three MUST-FIRE mutants of `iface_fold` are driven over the same 90 windows and each must be caught -- M1 `scan_c` returns the count on a match, M2 `scan_d` never stops early, and ⭐ M3 an unwritten slot reads as pool index 0, which is the one the measured corpus CANNOT see -- plus one MUST-NOT-FIRE equivalent rewrite of `scan_c`, so the sweep is keyed on the function and not on the spelling.",
  "idiom": {
    "required": [
      {
        "c": "`sizeof(ph53_iface *)*ce->num_interfaces` -- THE STORAGE IS SIZED TO THE COUNT, zend_compile.c:2571. Present in BOTH C rungs, and deliberately so: d09cdd9f71f3 changes WHICH allocator is called and not what it is asked for, so the hardened rung sizes the same block and then zeroes it. The only tokens that differ from the tarball's own line are the narrowed type name and the shim's allocator prefix. The Rust key pins a DIFFERENT expression on purpose, because no single expression is common to all six: the C sizes a byte count for an allocator and the Rust rungs give a Vec a capacity. What IS common is that the number comes from ce->num_interfaces and from nothing the writes ever touched.",
        "rust": "`Vec::with_capacity(num_interfaces)` -- present in safe_tuned.rs, unsafe.rs and verus.rs. safe_naive.rs writes a vector of None instead and does NOT match this entry, which is the R2/R3 distinction this row exists to price: R2 materialises n slots as VALUES, R3 reserves n and materialises none. The set of rungs lives in this English, which is what the named-spelling standard says about scope."
      },
      {
        "c": "`idx[k] = ce->num_interfaces++;` -- THE COUNT ADVANCE WITH NO SLOT WRITTEN, zend_compile.c:2591, which upstream spells opline->extended_value = CG(active_class_entry)->num_interfaces++. Present in both C rungs. It is the defect's first half and it is a whole statement away from the second, which is why the kernel keeps it as its own loop instead of folding the count to n_decl.",
        "rust": "`idx[d0] = num_interfaces;` -- present in safe_naive.rs, unsafe.rs and verus.rs. It is ABSENT FROM safe_tuned.rs AND THAT ABSENCE IS PART OF THE REPAIR: php-5.2.0 deleted the compile-time index coupling and left the bare increment alone, which is also, later and independently, exactly what the corpus's own excluded be8daf1f47fa did in 2008. So R3's phase 1 is O(1) where every other rung's is O(n_decl), it is declared in the divergence ledger, and NOTES.md 8 prices it."
      },
      {
        "c": "`ce->interfaces[i]->id` -- THE DEREFERENCE, zend_operators.c:1535, the FAULTING consumer. Present in both C rungs, and it is the line that still faults after d09cdd9f71f3: on R1 the slot may hold whatever the allocator left there and on R1h it holds NULL, and this line follows it either way.",
        "rust": "`assume_init()` -- present in unsafe.rs and verus.rs, absent from safe_naive.rs and safe_tuned.rs, which have no unwritten slot to read. It is the one operation on this row that vstd ALREADY SPECIFIES, in std_specs/maybe_uninit.rs -- so in ordinary exec code it costs no trusted item, while the unchecked slice access on the same line costs one. ⛔ This file cannot use that: check.py requires every `unsafe` token in a Verus source to sit inside an external_body body, and 5c-twin then demands a twin that cannot exist for a MaybeUninit read, so the two operations are folded into one trusted item. See verus.twin_justifications and NOTES.md 11."
      },
      {
        "c": "`ce->interfaces[i] == entry` -- zend_compile.c:1951, the COMPARE-ONLY consumer. IT READS THE SLOT AND DOES NOT DEREFERENCE IT, which is the whole reason this kernel carries two consumers: the same one hunk makes this line DEFINED AND CORRECT and the line above a NULL dereference. Present in both C rungs. NO RUST KEY, deliberately -- the four Rust rungs represent the empty slot three different ways (an Option discriminant, a shorter array, a witness byte) and no single expression is common to them; what they share is that none of them reaches the pool on this path, and a reviewer settles that with one grep."
      },
      {
        "rust": "`wrote[i]` -- THE ONE-BYTE-PER-SLOT WITNESS, present in unsafe.rs and verus.rs and in no other rung. IT IS NOT IN THE C AND IT IS NOT UPSTREAM: it is what makes R4's unsafe read dischargeable, and the row's Verus-side result is that a faithful witness-free R4 CANNOT BE VERIFIED at all -- coverage is a property of the op stream, i.e. of attacker data, and the pinned driver loop offers no call site at which to establish it. controls/r4_nowitness.rs is that program, measured, run under Miri and put through Verus with its error text. It is indexed SAFELY on purpose: reaching a rung's own safety witness with an unchecked access would make the witness rest on the thing it exists to establish."
      },
      "R1h IS d09cdd9f71f34deab4b99f4e63523fb94164a724 WHOLE AND UNMODIFIED -- erealloc becomes emalloc plus a memset of the same size, one hunk, two insertions and one deletion -- and diffing the two C kernels gives that commit and only that commit, modulo the header and the comments that name it. BOTH SHAS ARE CITED HERE AND THE CORPUS COLUMN'S IS THE WRONG ONE (PROTOCOL_PHP.md F5(iii)). index.csv and FIXSURVEY_001.md give be8daf1f47fa (Dmitry Stogov, 2008-03-12, \"Optimized ZEND_FETCH_CLASS + ZEND_ADD_INTERFACE into single ZEND_ADD_INTERFACE opcode\"); it is EXCLUDED, twice independently -- preimage_screen.py labels it NOT-THE-REPAIR because neither cited 5.0.0 line is in the pre-image of its zend_compile.c hunk, AND the tag walk shows the cited erealloc line surviving php-5.0.1 through php-5.0.4 and gone at php-5.0.5, two years and nine months before that commit (TASK_PHP_040_REPORT 2.2). Both patches are under controls/ so the citation survives without network, and a later reader who finds the column does not have to re-refute it. The 2005 commit applies to the pristine 5.0.0 text at ZERO FUZZ -- patch -p1 --dry-run reports the hunk succeeding at 2568 with an offset of -14 lines, exit 0 -- and memset is already used three times in 5.0.0's zend_compile.c, so the backport needs no new include. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about which COMMIT the hardened rung is and no single token decides it.",
      "R2-R5 IMPLEMENT NEITHER C RUNG'S ALGORITHM, and that is forced rather than chosen. .memory-php/02-ladder.md: where the real upstream fix is INCOMPLETE, a safe-Rust rung built to it panics on the surviving inputs, and a rung that panics is not a translation of the C. d09cdd9f71f3 leaves both consumers unguarded, so a Rust rung built to R1h would have to panic at zend_operators.c:1535; the four Rust rungs therefore carry what is actually memory-safe and only R1 and R1h diverge. On the MEASURED corpus all six agree bit for bit, which is what check.py stage 2 checks; on inputs/adversarial-cmp.bin safe_tuned.rs alone diverges, because its array is only as long as the fills it saw, and stage 4 records that. NO BACKTICKED SPELLING: it is a statement about algorithms.",
      "THE WINDOW LAYOUT is three u32 head words, then the eight-entry interface pool as u64 ids, then 9-byte op records of one op byte and two u32s -- and the op count is bounded by the window LENGTH, as (len - 76) / 9, and never trusted out of the blob. THE BLOB IS THE OPCODE STREAM AND THE ROW DOES NOT REACH FOR THE EXECUTOR: ph49's warning applies verbatim -- an extraction that reaches for the executor has built a different row. n_decl is what zend_do_implements_interface counted at compile time and the FILL ops are the ZEND_ADD_INTERFACE opcodes that were supposed to write the slots, so the defect is the gap between the two and the corpus's job is to control that gap. inputs/gen.py re-derives its coverage from the bytes it just wrote and refuses a corpus that misses an arm: both arms of zend_compile.c:2570 (n_decl 0 and 6), all three op codes with the modulo taken past one wrap, both consumers, all four arms of the scan loop, all three head words' modulo exercised, and NEGATIVELY no measured window on which a QUERY runs with a slot unwritten. NO BACKTICKED SPELLING: the C reads the window with one helper and the Rust rungs with another, which is one fact in two spellings.",
      "THE ALLOCATION ORDER IS O(1) PER KERNEL CALL AND IT IS DECLARED HERE RATHER THAN LEFT TO BE RE-DERIVED FROM THE KERNEL (PROTOCOL_PHP.md B1a.2). Exactly ONE erealloc per call when n_decl is positive and NONE AT ALL when it is zero, plus one efree in the teardown; FILL and QUERY allocate nothing, and the interface pool is not allocated because upstream's interfaces are existing class entries. So ph53 IS the exception B1a says is worth remarking on -- ph64 allocates 2n+2 per call and 60 per cent of its C rung's instructions are in libc malloc and free -- and this row's cross-language column needs NO allocator caveat. The four Rust rungs reproduce the shim's tally ARITHMETICALLY (B forbids them the shim) and the reproduction is exact BECAUSE the count is O(1): one alloc, one free, no cache hit, and 8 times n_decl bytes reaching malloc. AND THAT MAKES BOTH ARMS OF THE DEFECT'S OWN BRANCH VISIBLE IN THE u64 FOR FREE: the dead arm allocates nothing, so the tally is zero. NO BACKTICKED SPELLING: it is a statement about a COUNT."
    ],
    "forbidden": [
      {
        "c": "`php_shim_ecalloc` -- zeroing at allocation time. It removes the defect without being d09cdd9f71f3 and without being php-5.2.0's restructuring either, so it answers a question nobody asked; and it is the first thing a reader reaches for. Upstream did not do it: the 2005 fix kept the allocation unzeroed and added a separate memset, which is a DIFFERENT number of instructions on the measured path and is what this row prices. ONLY THE ONE TOKEN IS BACKTICKED and every other name in this entry is deliberately plain, because a forbidden entry's backticks are matched against EVERY rung of the language and an incidental one refuses a rung for carrying its own correct code -- measured on this row before the first gate run, where six such incidental spellings would have failed it.",
        "rust": "`vec![0u32;` -- zero-filling the slot array. It would make an unwritten slot INDISTINGUISHABLE from a written one holding pool index 0, so it changes the answer while silencing every detector this row has -- the same shape as masking an index instead of testing it. The Option-valued fill safe_naive.rs writes is the opposite move and is NOT forbidden: it makes the empty slot representable rather than forging a value for it."
      },
      "`set_len` and `spare_capacity_mut` -- R4's MOST NATURAL SHAPE, and it is forbidden for a reason outside the row: the pinned vstd specifies NEITHER (std_specs/vec.rs has neither name, and assume_init_read is unspecified too -- it is named here rather than backticked because it is a third spelling of the same gap). Reserving a capacity, setting the length past it and writing through the spare capacity is therefore unverifiable at R5, and this contract's identity pin requires R4 and R5 to be the same program -- so R4 materialises uninitialised elements one at a time and initialises by assigning a fresh MaybeUninit. Both tokens are absent from all eight sources, checked by grep before they were written here rather than after the gate said so.",
      "A NULL TEST, AN EMPTINESS TEST OR ANY OTHER GUARD INSIDE EITHER CONSUMER'S SCAN LOOP IN EITHER C KERNEL. Upstream added none -- that is the row's headline -- and a C rung that added one would be measuring php-5.2.0's restructuring while claiming to be 5.0.0 or 5.0.5. NO BACKTICKED SPELLING IN THIS ENTRY, AND IT IS FORCED RATHER THAN CHOSEN: harness/check.py's spelling matcher decides one spelling against EVERY rung of a language, and the four Rust rungs legitimately DO carry such a guard -- an Option match, a push-bounded length, a witness byte -- so any token that named the C's absence would refuse all four. The SCOPE lives in this English and a reviewer settles it with one grep, which is what the named-spelling standard says about the things no grep settles."
    ],
    "why": "ph53 is PHP 5.0.0's class-declaration interface array, corpus row CRASH-158, tier `narrowed`. THE IDIOM IS STORAGE GROWN TO A COUNT THAT WAS ADVANCED SEPARATELY FROM THE WRITES, SO THE TAIL OF THE ALLOCATION IS NEVER WRITTEN AND IS READ ANYWAY. `Zend/zend_compile.c:2591` is `opline->extended_value = CG(active_class_entry)->num_interfaces++;` -- the count moves once per `implements` clause, at COMPILE time, and no slot is written -- and `:2570-2571` then grows the storage to that count and leaves it indeterminate: `if (ce->num_interfaces > 0) { ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces); }`. `:3747-3748` set `num_interfaces = 0` and `interfaces = NULL`, so the `erealloc` is a plain `malloc` and the WHOLE array is indeterminate. ⚠⚠⚠ THE READ IS IN BOUNDS. The slot a consumer reads is inside the reallocated block and nothing has been freed: CWE-824 (uninitialised pointer), NOT CWE-125 (over-read). No built row in either programme prices that. `ph32` is the cross-reference and not the duplicate -- same C shape, sized to the LITERAL instead of the count, so its excess is PAST the end. ⚠⚠ THE TIER IS `narrowed` AND `CATALOGUE.md` SAYS `verbatim`; the catalogue is wrong and TASK_PHP_040_REPORT §5.1 itemises why. The DEFECT SPAN lifts byte-identically -- which is exactly why d09cdd9f71f3 patches onto it at zero fuzz -- but the MECHANISM needs three frames in two files and two of them do not lift: the count advance drags `zend_op` / `get_next_op` / `CG()` / `opline->extended_value` (a projection) and the faulting consumer drags `instanceof_function`'s class-tree walk and `TSRMLS` (a narrowing). A tier is a COST STATEMENT AND NEVER A FILTER (CATALOGUE.md 0.2), so declaring `narrowed` refuses nothing and costs only honesty. ⓘ Two of two catalogue tiers examined by hand are optimistic in the same direction (RECAP_PHP.md open item 75); that is an observation from two rows and this row does not survey it. ⚠⚠⚠ AND THE UPSTREAM FIX DOES NOT REMOVE THE FAULT -- IT MAKES IT DETERMINISTIC, AT TWO DIFFERENT SEVERITIES ON THE ROW'S TWO CONSUMERS, WHICH IS WHY THIS KERNEL SHIPS BOTH OF THEM. `d09cdd9f71f34deab4b99f4e63523fb94164a724` (Dmitry Stogov, 2005-06-08, \"Fixed valgrind errors\", first shipped php-5.0.5) replaces the `erealloc` with an `emalloc` plus `memset(ce->interfaces, 0, ...)` and adds NO consumer guard. At php-5.0.5 `Zend/zend_operators.c:1535` still reads `instanceof_function(instance_ce->interfaces[i], ce)` and `Zend/zend_compile.c:1951` still compares `ce->interfaces[i] == entry`. MEASURED, on this box, under gcc -O1 -fsanitize=address,undefined, on a blob whose QUERY reaches an unwritten slot (controls/r1h_consumers.py): R1 reports `member access within misaligned address 0xbebebebebebebebe for type 'struct ph53_iface'` then `SEGV on unknown address`, and R1h reports `member access within null pointer of type 'struct ph53_iface'` then `SEGV on unknown address 0x000000000000` -- while the COMPARE-ONLY consumer exits 0 on both arms with the same u64. ⭐ ONE HUNK, TWO SEVERITIES: a wild-pointer dereference becomes a deterministic NULL dereference at the dereferencing sink and a correct answer at the comparing sink. That is PROTOCOL_PHP.md C's \"an upstream fix is not automatically correct -- report it, do not repair it\" case and NO built row carries it. ⚠⚠ THE CONSEQUENCE FOR `inputs/`, STATED RATHER THAN LEFT TO BE NOTICED: there is no `adversarial-deref.bin` and there CANNOT be one. check.py stage 7h requires R1h clean on EVERY input in `inputs/`, in terms, and every blob on which R1 dereferences an unwritten slot is a blob on which R1h NULL-dereferences -- so the row whose result is that the fix is incomplete is structurally unable to ship the input that shows it. That is `.memory-php/02-ladder.md` F31's standing limitation binding on a real row for the first time, and the resolution F31 itself prescribes is the one taken: the evidence lives in `controls/`. What `inputs/` carries is the half that is safe under every detector -- `adversarial-cmp` reads an unwritten slot through the compare-only consumer, which does not dereference it, with `adversarial-shadowed` (the unwritten slot exists and a QUERY_DEREF runs, but an earlier slot matches and the loop breaks first) and `adversarial-covered` (the same op stream with the coverage completed) as its two must-NOT-fire controls. ⭐ ON THE MEASURED CORPUS R1 AND R1h ARE BIT-IDENTICAL, and that is check.py stage 7h's requirement being SATISFIED: the benign corpus writes every slot before any query, so the published u64 carries no evidence whatever that the defect exists. That is ph64's and ph45's lesson arriving on a THIRD row. What R1h does cost on the measured path is an O(n_decl) `memset` on every class declaration -- a real, attributable number, which is what NOTES.md 8 reports. ⭐⭐ THE LADDER, AND IT IS FOUR ANSWERS TO ONE QUESTION -- \"was this slot written?\". R1h answers it by zeroing the storage and still faults. R2 answers it with `Option<u32>`, which is EIGHT BYTES PER SLOT on this platform because a u32 has no niche, plus a discriminant load and a branch on every read -- and what it reinvents is not php-5.0.5's `memset` but that `memset` PLUS the consumer guard upstream never added, because `if let Some(p)` is the only expression that reaches the value at all. R3 does not answer it: it is php-5.2.0's own repair, `ce->interfaces[ce->num_interfaces++] = iface`, so `Vec::len()` already carries it and there is no unwritten slot to represent -- and it deletes the compile-time index array with it, which is what 5.2.0 (and, independently in 2008, the corpus's own excluded be8daf1f47fa) actually did. R4/R5 answer it with ONE BYTE PER SLOT in a stack array and a test/jz. ⚠⚠⚠ AND THE R4/R5 WITNESS IS A RESULT AND NOT A DESIGN CHOICE. The faithful unsafe port has no witness -- it scans `0..num_interfaces` and `assume_init()`s every slot, which is `zend_operators.c:1535` exactly -- and THAT PROGRAM CANNOT BE VERIFIED, for a reason that is not about Verus being weak: `MaybeUninit::assume_init`'s precondition is `m.mem_contents().is_init()`, whether slot i was written is a property of the OP STREAM, i.e. of attacker data, and this contract's driver loop is pinned canonical and calls `kernel(buf, k * stride, stride)` with no test -- so there is no call site at which coverage could be established and no `requires` that could carry it. A rung that reproduces the defect is unverifiable and a rung that verifies does not reproduce it. The faithful witness-free version is therefore a CONTROL -- `controls/r4_nowitness.rs`, measured, run under Miri and put through Verus with its error text -- and not a rung. ⭐⭐ AND ONE MORE THING THE PINNED vstd DECIDES: `MaybeUninit::{new, uninit, assume_init, assume_init_ref, assume_init_mut}` are `assume_specification`'d in `~/tools/verus/vstd/std_specs/maybe_uninit.rs`, so `assume_init` -- the operation the row is about -- costs NO trusted item, while `get_unchecked` on the same line costs one, because 0 files under `~/tools/verus/vstd/` mention it. Two unsafe operations, one line, and only one of them enlarges the trusted base. `set_len` and `spare_capacity_mut` are unspecified too, which is why R4's most natural shape is forbidden here. NOTES.md 10 and 11. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "iface_fold": "iface_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 27
    },
    "twin_obligations": {
      "verus.rs": 30
    },
    "obligations_note": "27 verified / 0 errors, and 30 under `--cfg slb_twin` -- FOUR trusted accessors and THREE twins, because the fourth cannot have one (see twin_justifications). ⭐⭐ WHAT IS PROVED IS THE OBLIGATION THE ROW IS ABOUT, IN THE SPELLING THE PINNED vstd ALREADY HAS: the query loops' invariant is `forall|j| 0 <= j < n_decl ==> (wrote@[j] ==> slots@[j].mem_contents().is_init() && slots@[j].mem_contents().value() < n_pool)`, and its first conjunct is literally `MaybeUninit::assume_init`'s own `requires` (std_specs/maybe_uninit.rs). ⛔⛔ AND THE ROW CANNOT USE THAT FOR FREE, WHICH IS ITS SHARPEST INFRASTRUCTURE FINDING: `harness/check.py::_scan_unsafe_sites` requires EVERY `unsafe` token in a pinned Verus source to sit inside an `external_body` body, with no justification hatch, and 5c-twin requires every trusted item to have a VERIFIED twin -- which for a MaybeUninit read would itself need `unsafe`, because there is NO safe exec route from MaybeUninit<T> to T. Two sound rules, jointly unsatisfiable for this operation. So `slot_read_unchecked` folds `get_unchecked` and `assume_init` into ONE trusted item whose `requires` RE-ASSERTS BY HAND the precondition vstd already provides, and its twin is justified away. The TCB count is unchanged by the fold (one item either way) and what is lost is that the `is_init` precondition is now the row author's rather than vstd's. `controls/mu_unwrapped.rs` verifies the unwrapped shape at 7/0 with NO trusted item at all -- vstd's own assume_specification carrying the obligation -- and `controls/negatives.py --verus` RUNS it as must-NOT-fire arm N2, so the fact about Verus stands, is committed rather than cited, and is re-checked on every invocation; the wrapper is the GATE's requirement and not Verus's. NOTES.md 11. ⚠ THE SECOND CONJUNCT IS THE PRICE OF THE REPRESENTATION AND NOT PART OF THE C's OBLIGATION: the C stores a `zend_class_entry *` and needs only that the pointer designate a class, while safe Rust cannot store an address in memory it owns, so all four Rust rungs store an INDEX (ph45's precedent) and an index needs a RANGE as well as an initialisedness. So where the C has one fact the proof has a conjunction, and that is a finding about the representation rather than about the prover. ⚠⚠ AND THE PREDICTION IT PARTLY REFUTES IS TASK_PHP_040_REPORT 5.6's \"R5 needs NO hand-rolled ghost state\": right about MEMORY SAFETY -- `mem_contents()` is the ghost state and no `Seq<bool>` is needed for it -- and WRONG about the VALUE postcondition, because a spec function cannot construct a `MaybeUninit` (`mem_contents` is `uninterp`), so the spec-level slot array is a `Seq<Option<u32>>` and `abst()` is the abstraction function onto it. ONE ghost Seq, and not the one that was predicted absent. ⚠ THE PROOF-BUDGET OVERRIDE IS DISCLOSED WITH ITS REASON: `#[verifier::rlimit(60)]` on `kernel`. The file verifies in ~40 s wall at that setting; the kernel carries two nested loops, a three-way op dispatch and four recursive spec functions, and a proof that passes on one side of a coin flip is not a proof. ⚠⚠ ONE THING MEASURED THE HARD WAY AND WORTH THE NEXT AGENT'S TIME: a Verus `while` body sees the loop INVARIANTS and the loop condition and NOTHING from before the loop, so a `let ghost target = ...` binding is out of scope inside the body. Both query helpers return from INSIDE their loop on a match, and with the binding alone both exits fail their postcondition while every assert inside them passes -- which is a confusing way to be told a binding is out of scope. The repair is one invariant clause per helper, pinning `target` to the postcondition's own expression, and the comment in `instanceof_ex` says so.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 27 shipped + 3 for `slb_twin_win_get_unchecked`, `slb_twin_slot_set_unchecked` and `slb_twin_pool_get_unchecked`, whose bodies are `v[i]`, `v[i] = x` and `a[i]` with the IDENTICAL contract -- so three of the four unchecked accessors' `requires` and `ensures` are CHECKED against a safe implementation rather than asserted. ⛔⛔ THE FOURTH, `slot_read_unchecked`, HAS NO TWIN AND CANNOT HAVE ONE, and the reason is a COLLISION BETWEEN TWO SOUND GATE RULES rather than a concession: `_scan_unsafe_sites` requires every `unsafe` token in this file to sit inside an `external_body` body, and there is NO safe exec route from MaybeUninit<T> to T -- `assume_init`, `assume_init_ref` and `assume_init_mut` are the only ones and all three are unsafe -- so any twin's body would contain an `unsafe` token outside a trusted body and would be REFUSED by the first rule. The two rules are jointly unsatisfiable for a MaybeUninit read. `load_input` and `emit` have no twin either and cannot: one reads a file and the other prints, and neither is a function of its arguments. ⚠ THREE OF SIX TRUSTED ITEMS ARE TWINNED, WHICH IS WHAT THE STAGE MEASURES, and the `ok` line does not fire when anything is justified away -- that is check.py's own design and this row's record shows it. NOTES.md 11.",
    "items": {
      "verus.rs": {
        "rd32s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "rd64s": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "cap_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "nd_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "np_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "no_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "pool_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tally_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "abst": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "scan_d": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "scan_c": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "run_ops": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "iface_win": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "iface_fold": {
          "external": null,
          "requires": [],
          "ensures": []
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
        "slot_read_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()",
            "v@[i as int].mem_contents().is_init()"
          ],
          "ensures": [
            "r == v@[i as int].mem_contents().value()"
          ]
        },
        "slot_set_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_slot_set_unchecked": {
          "external": null,
          "requires": [
            "i < old(v)@.len()"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "pool_get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < MAXP"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_pool_get_unchecked": {
          "external": null,
          "requires": [
            "i < MAXP"
          ],
          "ensures": [
            "r == a@[i as int]"
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
        "tally": {
          "external": null,
          "requires": [
            "n_decl <= MAXD"
          ],
          "ensures": [
            "r == tally_of(n_decl as int)"
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
        "rd64": {
          "external": null,
          "requires": [
            "o + 8 <= w@.len()"
          ],
          "ensures": [
            "r == rd64s(w@, o as int)"
          ]
        },
        "instanceof_ex": {
          "external": null,
          "requires": [
            "slots@.len() <= MAXD",
            "forall|j: int| 0 <= j < slots@.len() ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init() && slots@[j].mem_contents().value() < MAXP)"
          ],
          "ensures": [
            "r == scan_d( abst(slots@, wrote@, slots@.len() as int), pool@, 0, slots@.len() as int, target_id, )"
          ]
        },
        "inherit_scan": {
          "external": null,
          "requires": [
            "slots@.len() <= MAXD",
            "forall|j: int| 0 <= j < slots@.len() ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init() && slots@[j].mem_contents().value() < MAXP)"
          ],
          "ensures": [
            "r == scan_c(abst(slots@, wrote@, slots@.len() as int), 0, slots@.len() as int, target)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "76 <= len"
          ],
          "ensures": [
            "r == iface_fold(buf@, off as int, len as int)"
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
        "slot_read_unchecked": "⛔⛔ NO TWIN, AND IT IS NOT POSSIBLE RATHER THAN NOT CONVENIENT. A twin has to be a VERIFIED exec function meeting the same contract, and this contract's `ensures` is `r == v@[i as int].mem_contents().value()` -- so the body must get a `u32` OUT of a `MaybeUninit<u32>`. The pinned vstd offers exactly three routes -- `assume_init`, `assume_init_ref` and `assume_init_mut` -- and ALL THREE ARE `unsafe fn`. There is no safe exec expression from `MaybeUninit<T>` to `T`; that is what the type MEANS. So any twin's body would contain an `unsafe` token outside a trusted item's body, which `harness/check.py::_scan_unsafe_sites` refuses with no justification hatch. ▶ TWO SOUND RULES, JOINTLY UNSATISFIABLE FOR THIS ONE OPERATION, and the row reports the collision (NOTES.md 11) rather than working around it quietly. ⚠ WHAT IS THEREFORE UNCHECKED, STATED PLAINLY: that this item's `requires` is STRONG ENOUGH to license a checked implementation. What IS checked is that it is not VACUOUS (5a: both parameters its body uses are constrained), that deleting either conjunct breaks a caller (`controls/negatives.py` M1 deletes the guard that supplies the second and Verus refuses at std_specs/maybe_uninit.rs:40:13, and M2 the range conjunct), and that Miri is silent on the shipped rung and LOUD on the witness-free control. ⭐ AND ONE MORE THING IS CHECKED THAT NO TWIN COULD CHECK: `controls/mu_unwrapped.rs` verifies the UNWRAPPED shape -- vstd's own `assume_init` spec carrying the same obligation in ordinary exec code, with NO trusted item at all, 7 verified / 0 errors -- so the contract asserted here is demonstrably the one vstd asserts, which is a stronger statement than a hand-written twin would have made. ⚠ IT IS A COMMITTED FILE AND NOT A `.temp/` PROBE, deliberately: RECAP_PHP.md open item 65 is about a claim in a committed layer resting on a gitignored path, and this citation is inside the HASHED block. `controls/negatives.py --verus` runs it as a must-NOT-fire arm on every invocation, so if the hand-asserted contract ever drifts from what vstd says, one command reports it.",
        "load_input": "NO TWIN AND THERE CANNOT BE ONE. It opens a file, reads it and allocates; it is not a function of its arguments, it has no `ensures` to check, and a safe implementation would be the same code. Every pattern in both programmes carries this item and none has a twin.",
        "emit": "NO TWIN AND THERE CANNOT BE ONE. `println!` is not verifiable and the item has no `ensures`, so there is nothing for a twin to be checked against."
      }
    },
    "unsafe_justifications": {
      "verus.rs": {
        "win_get_unchecked": "`*v.get_unchecked(i)` is defined only while `i < v.len()`, and the pinned vstd ships NO spec for it -- grepped `~/tools/verus/vstd/` entire, 0 files mention `get_unchecked` at all, while `assume_init` appears in four. So the wrapper is the trusted boundary and `i < v@.len()` is the whole of what makes it sound. The `ensures` is the value, which is what makes it useful; both are trusted and the twin `slb_twin_win_get_unchecked` checks the pair against `v[i]`.",
        "slot_read_unchecked": "`(*v.get_unchecked(i)).assume_init()` -- TWO unchecked operations in one expression, and the `requires` has one conjunct for each: `i < v@.len()` for the slice access, which the pinned vstd does not specify at all, and `v@[i as int].mem_contents().is_init()` for the `assume_init`, which it DOES specify (`std_specs/maybe_uninit.rs`). ⛔⛔ THE SECOND CONJUNCT IS RE-ASSERTED BY HAND HERE AND THAT IS A LOSS THE ROW REPORTS RATHER THAN HIDES: in ordinary exec code `unsafe { m.assume_init() }` needs NO trusted item, because vstd's `assume_specification` carries the obligation -- verified at 7/0 in the COMMITTED control `controls/mu_unwrapped.rs`. But `check.py::_scan_unsafe_sites` requires every `unsafe` token in this file to sit inside an `external_body` body and 5c-twin then demands a twin that cannot exist, so the two operations are folded and the obligation vstd owns becomes one this contract asserts. ⭐ THE TCB COUNT IS UNCHANGED BY THE FOLD -- one item either way -- and that control is what keeps the asserted contract checkable against vstd's. NOTES.md 11.",
        "slot_set_unchecked": "`*v.get_unchecked_mut(i) = x` -- sound iff `i < v.len()`, and `x: MaybeUninit<u32>` is a PURE VALUE that needs no precondition, because every inhabitant is a legal store into a slot of that type, initialised or not. The `ensures` names the WHOLE post-state, `old(v)@.update(i, x)`, so a body that also clobbered `v[i + 1]` could not satisfy it -- that completeness is the thing a write wrapper's contract can get wrong and it is why Miri is required on this row.",
        "pool_get_unchecked": "`*a.get_unchecked(i)` on a `&[u64; MAXP]`. The array's length is in its TYPE, so `a@.len() == MAXP` holds for every `a` this signature admits (vstd's `array_len_matches_n`) and there is nothing left for a `requires` to say beyond the index. ⚠ `i < MAXP` is the PRICE OF THE REPRESENTATION and not part of the C's obligation: the C's slot holds a `zend_class_entry *` and needs only that the pointer designate a class, while safe Rust cannot store an address in memory it owns, so all four Rust rungs store an index -- and an index needs a range as well as an initialisedness. The row reports that as a finding about the representation rather than hiding it in a precondition.",
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
      "if stride_w >= 76 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph53's two probe shapes have different work per call (221 and 439 window bytes, i.e. 16 and 40 op slots) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW and the op count is `(stride - 76) / 9`, an affine function of it, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ THERE IS ALSO A FIXED PER-CALL TERM: the 12-byte header, the eight-entry pool read (64 bytes, read in full on every rung so that the term is a CONSTANT), the phase-1 index loop and R1h's `memset` happen on every call whatever the stride. So the marginal is NOT a pure op rate and NOTES.md 8 decomposes it. ⚠⚠⚠ AND THE PER-WINDOW WORK IS NOT UNIFORM, WHICH IS DECLARED RATHER THAN ELIDED: one window in sixteen has `n_decl == 0`, because BOTH arms of the defect's own branch at zend_compile.c:2570 have to be in the MEASURED corpus (PROTOCOL_PHP.md A2a rule 1) and the two arms cannot cost the same. That matters for family B -- RECAP_PHP.md F88: `probe_iters [100, 200]` is ONE DRAW of a sampling distribution and a row with heterogeneous per-window work is exactly where the draw bites -- so every B1 figure this row publishes is labelled as one draw and marked PROVISIONAL pending open item 62 (family C)."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "differ",
      "why": "⚠⚠ R4 AND R5 DIFFER AT BOTH LEVELS, AND THE PIN IS `differ` BECAUSE THAT IS WHAT WAS MEASURED, BEFORE THE GATE WAS FIRST RUN. Kernel instruction counts with padding removed, `isolated`, same rustc flags as build.py's: O3 762 (R4) against 755 (R5), O0 899 against 803. ⭐ SO THE PROVED RUNG IS CHEAPER THAN THE UNSAFE ONE AT BOTH LEVELS, WITH NO SEARCH AT ALL -- which is F82's observation on ph45 and ph64 arriving on a THIRD row, and this is the largest margin of the three. ⚠ It is a register-allocation and block-ordering difference and not a semantic one: R5's exec code is R4's, the extra text is `verus!`, the spec/proof items and the `requires`/`ensures`, and every `let ghost`, `assert` and `proof {}` erases before codegen. What differs is that rustc sees a different (and larger) module and allocates registers differently -- `mov %rdx,%r15` where R4 keeps the value in `%rcx`, from the very first block. ⚠⚠ DO NOT READ THE 7 AND 96 INSTRUCTIONS AS A COST OF PROOF IN EITHER DIRECTION: nothing about the proof is in the binary, and the row states the difference rather than attributing it. NOTES.md 10."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph53 has FOUR such items and one of them WRITES (`slot_set_unchecked`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `v@[i] == x` would let a body that also clobbered `v[i + 1]` through every Verus stage. ⭐⭐ AND IT MATTERS MORE HERE THAN THE RULE ANTICIPATES, FOR A REASON THAT IS THIS ROW'S SUBJECT: the defect is an UNINITIALISED READ OF AN IN-BOUNDS SLOT, and ASan cannot see that class at all -- it is MSan's, and what ASan reports on the C rung is the SEGV that FOLLOWS, because ASan fills fresh allocations with 0xbe and 0xbebebebebebebebe is not a canonical address. Miri is the only detector in this tree that sees the uninitialised read ITSELF. `controls/r4_nowitness.rs` is the witness-free R4 and `controls/negatives.py --miri` runs it: Miri must report it and must be silent on the shipped rung.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph53's cost is 4 x (one window decoded, 16 or 40 ops run over at most 6 slots), i.e. a few hundred slot reads -- orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "Zend/zend_compile.c",
    "c_lines": [
      2569,
      2572
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '2569,2572p'",
    "extract_sha256": "617c5c8532f0d9e4ac34ab66fd5ffe8f287a921be7aa6a40c4b088044f7a27a0",
    "extra_spans": [
      {
        "c_file": "Zend/zend_compile.c",
        "c_lines": [
          2584,
          2592
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '2584,2592p'",
        "extract_sha256": "5dfed24c579ddf68a98845cf66b4f6a989266dfad944a84b64250a5886bf7b3f",
        "why": "`zend_do_implements_interface` -- THE COUNT ADVANCE. `:2591` is `opline->extended_value = CG(active_class_entry)->num_interfaces++;`, the defect's first half: the count moves once per `implements` clause and no slot is written. ⚠ PROJECTION, not a lift: `zend_op`, `get_next_op`, `CG(active_op_array)`, `CG(implementing_class)` and `opline->extended_value` do not come across -- the opcode array's only role at these lines is to carry the compile-time index from phase 1 to phase 2 and the blob's op stream carries it instead. This is one of the two frames that make the tier `narrowed` rather than the catalogue's `verbatim`."
      },
      {
        "c_file": "Zend/zend_operators.c",
        "c_lines": [
          1530,
          1538
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_operators.c | sed -n '1530,1538p'",
        "extract_sha256": "070ebda5e99f5ebd5cb878f6177de0ca54c8ad07e37af09272439a312a76b266",
        "why": "`instanceof_function_ex`'s interface loop -- THE FAULTING CONSUMER, and the corpus's `c_file_line`. `:1534` loops to `instance_ce->num_interfaces` and `:1535` DEREFERENCES `instance_ce->interfaces[i]`. ⚠ NARROWED: `instanceof_function` (`:1552-1555`) and its parent-chain walk (`:1539-1546`) become an identity test through the slot pointer, because the row prices the SLOT READ and not the class-tree walk -- but the DEREFERENCE, which is the fault, is kept, one per examined slot. The second frame that makes the tier `narrowed`."
      },
      {
        "c_file": "Zend/zend_compile.c",
        "c_lines": [
          1947,
          1957
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '1947,1957p'",
        "extract_sha256": "ffb081bc8831900663841f699dbc8c45ec25d977289ee2d793ea7565ab790834",
        "why": "`zend_do_inherit_interfaces`'s dedup scan -- THE COMPARE-ONLY CONSUMER, and the corpus's second cited line (`:1951`). ⚠⚠ IT READS THE SLOT AND DOES NOT DEREFERENCE IT, which is why the row ships two consumers: `d09cdd9f71f3` makes this line defined and correct and `zend_operators.c:1535` a NULL dereference. The compare loop lifts; what is left behind is the surrounding `while (if_num--)` merge, which belongs to a different operation."
      },
      {
        "c_file": "Zend/zend_compile.c",
        "c_lines": [
          3740,
          3748
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '3740,3748p'",
        "extract_sha256": "f3b1ed5a257ad2a8a158900e4717cec57357ff13df9b1327f38fa9af57e41f0e",
        "why": "`zend_initialize_class_data`'s tail -- `:3747 ce->num_interfaces = 0;` and `:3748 ce->interfaces = NULL;`. ⭐ THIS SPAN IS WHY THE WHOLE ARRAY IS INDETERMINATE AND NOT JUST ITS TAIL: with `interfaces` NULL the `erealloc` at `:2571` is a plain `malloc`, so there is no old content to preserve and every slot of the new block is fresh heap. TASK_PHP_040_REPORT 3 notes that the task file inferred `:3748` and did not quote it; it is quoted here."
      },
      {
        "c_file": "Zend/zend_opcode.c",
        "c_lines": [
          152,
          168
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_opcode.c | sed -n '152,168p'",
        "extract_sha256": "f6df30b4ccddd544892f839187311a7a9f36e2e807b901d67cc9d07701638ca4",
        "why": "`destroy_zend_class`'s `ZEND_USER_CLASS` arm -- `:161-162 if (ce->num_interfaces > 0 && ce->interfaces) { efree(ce->interfaces); }`, the teardown the kernel carries so that the array is released once per call rather than orphaned by the next `php_shim_reset()`. ⚠ Note the guard is on the COUNT and the POINTER, not on what any slot holds, so it is unaffected by the defect. The rest of the function -- five `zend_hash_destroy`s and the `ZEND_INTERNAL_CLASS` arm, which uses plain `free` -- is outside the row."
      },
      {
        "c_file": "Zend/zend.h",
        "c_lines": [
          304,
          344
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend.h | sed -n '304,344p'",
        "extract_sha256": "9018d8b3e29578aee0b918b2760da8746b17285a5c2f538215a21f3442a90e5b",
        "why": "`struct _zend_class_entry`, for `:334 zend_class_entry **interfaces;` and `:335 zend_uint num_interfaces;` -- the two members the row is about, in upstream's order and with upstream's types (`zend_uint` is `unsigned int`). The other 22 members are not lifted: nothing in the extracted spans reads them, and a kernel that carried the whole struct would be pricing `zend_hash`'s layout."
      }
    ],
    "extra_spans_note": "SEVEN SPANS ACROSS FOUR FILES, AND THE PRIMARY IS FOUR LINES. `.memory-php/01-extraction.md` F1: `provenance.c_file`/`c_lines` name the DEFECT site and the other frames go in the notes -- and on this row the defect site is the shortest of the seven, because `zend_compile.c:2569-2572` is the whole of what `d09cdd9f71f3` touches. ⚠ The corpus's own `c_file_line` names `zend_operators.c:1534-1535`, the FAULTING frame, which is `extra_spans[1]`; F1's lesson exactly. ⚠⚠ TWO OF THE SEVEN DO NOT LIFT AND THAT IS THE TIER: `extra_spans[0]` is a projection (the opcode array) and `extra_spans[1]` a narrowing (the class-tree walk), which is why this row declares `narrowed` against the catalogue's `verbatim`.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "zend_compile.c:2542, :2584, :2575; zend_operators.c:1530, :1535, :1552",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "zend_op / get_next_op(CG(active_op_array)) / CG(implementing_class) / opline->extended_value -> the blob's op stream",
        "kind": "projection",
        "where": "zend_compile.c:2586-2590",
        "why": "the opcode array's only role at these lines is to carry the compile-time index from phase 1 to phase 2, and the blob's 9-byte op records carry it instead. The count advance itself (`num_interfaces++`) lifts verbatim. ⚠ THE ROW DOES NOT REACH FOR THE EXECUTOR -- `ph49`'s warning applies verbatim and THE BLOB IS THE OPCODE STREAM. No semantics."
      },
      {
        "what": "instanceof_function's parent-chain walk and its recursive call",
        "kind": "narrowed",
        "where": "zend_operators.c:1535, :1539-1546, :1552-1555",
        "why": "the row prices the SLOT READ, not the class-tree walk, so `instanceof_function(instance_ce->interfaces[i], ce)` becomes an identity test through the slot pointer -- `ce->interfaces[i]->id == target->id`. The DEREFERENCE is kept, one per examined slot, because it is the fault. ⚠ REACHABLE-DOMAIN ARGUMENT OWED AND GIVEN: the narrowing changes which interfaces are reported as implemented (no transitivity) and therefore the answer, so it is a `narrowed` tier and not a `substitution`; what it does NOT change is the number of slot dereferences, which is the quantity the row measures."
      },
      {
        "what": "the `||` disjunct `ce->interfaces[i] == target` in the faulting consumer",
        "kind": "deletion",
        "where": "zend_operators.c:1535 (as narrowed)",
        "why": "REDUNDANT: `p == q` implies `p->id == q->id`, so its only effect would be to SKIP the dereference on the matching slot -- and a matching slot is written by construction, so no behaviour moves on any input. What dropping it buys is that no rung's control flow ever depends on an ADDRESS, which `TASK_PHP_041.md` 2.3 requires of everything that reaches the cross-rung checksum. No semantics."
      },
      {
        "what": "zend_verify_abstract_class / do_verify_abstract_class, and the ctor / dtor / clone fn_flags block",
        "kind": "deletion",
        "where": "zend_compile.c:2546-2567, :2573-2579",
        "why": "same function, either side of the defect span, and neither touches `ce->interfaces`. `.memory-php/01-extraction.md` F8: extraction cost is priced at the DEFECT site, and four rows have been killed by pricing an adjacent frame's machinery. No semantics."
      },
      {
        "what": "zend_do_inherit_interfaces' `while (if_num--)` merge and its own erealloc",
        "kind": "deletion",
        "where": "zend_compile.c:1941-1945, :1948-1949, :1955-1957",
        "why": "the row lifts the dedup SCAN (`:1950-1953`) and not the merge around it: the merge is a second, differently-sized allocation belonging to inheritance rather than to declaration, and `:1942`/`:1944` are a DIFFERENT `erealloc` whose size comes from `ce_num + if_num`. Carrying it would put two defects in one kernel. No semantics for the scan."
      },
      {
        "what": "the 22 other members of struct _zend_class_entry",
        "kind": "deletion",
        "where": "zend.h:304-344",
        "why": "nothing in the extracted spans reads them. `ph53_ce` keeps `interfaces` and `num_interfaces` in upstream's order and with upstream's types; a kernel that carried the whole struct would be pricing `zend_hash`'s layout. No semantics."
      },
      {
        "what": "zend_class_entry * -> a one-u64 `ph53_iface`, and the interface POOL",
        "kind": "projection",
        "where": "zend.h:304-344; zend_compile.c:2571",
        "why": "the slot's pointee only ever has its identity compared, so the kernel gives it one `uint64_t id` and puts eight of them in a stack array read from the window. ⚠ NOT ALLOCATED, and that is faithful: at `:2571` every interface an `implements` clause names is an EXISTING `zend_class_entry`, so the pool costs no allocation and the per-call allocation count stays O(1) (see `idiom.required`'s allocation-order entry). All eight entries are read on every call, `n_pool` or not, so the pool term is a CONSTANT and no rung reads an uninitialised pool slot -- a second uninitialised read would be a different row. No semantics for the slot mechanism."
      },
      {
        "what": "erealloc / efree -> php_shim_erealloc / php_shim_efree",
        "kind": "substitution",
        "where": "zend_compile.c:2571; zend_opcode.c:162",
        "why": "NOT a divergence in substance: `common-php/emalloc_shim.h` IS PHP 5.0.0's own `_erealloc`/`_efree`, cited line by line, and PROTOCOL_PHP.md B REQUIRES it. It is listed so a reader can see that the allocator was not substituted for a plain `malloc` -- which an earlier effort did, and as a direct result reported a real defect as unreachable. ⭐ `php_shim_erealloc(NULL, n)` takes `_erealloc`'s `:316-318` arm straight to `_emalloc`, which is what makes the block fresh uninitialised heap rather than preserved content. No semantics."
      },
      {
        "what": "the four Rust rungs reproduce php_shim_tally() arithmetically instead of linking the shim",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:642-648, :346-435",
        "why": "`harness/build.py` compiles exactly three C translation units and no Rust rung links C, and §B forbids it anyway. Each Rust rung computes the same u64 the C folds -- n_alloc 1, n_free 1, n_cache_hit 0, bytes_mallocked 8*n_decl, or all zeros when `n_decl == 0`. ⭐ The reproduction is EXACT because the allocation count is O(1) in the input, which is §B1a's precondition and the reason this row's cross-language column carries no allocator caveat. Verified against the C: all six rungs agree bit for bit on both measured inputs. No semantics."
      },
      {
        "what": "PHP_SHIM_REAL_SIZE's rounding is written as `8 * n_decl` in the four Rust rungs",
        "kind": "substitution",
        "where": "common-php/emalloc_shim.h:217",
        "why": "`REAL_SIZE(size)` is `(size + 7) & ~7` and `8 * n_decl` is already 8-aligned, so the rounding is the IDENTITY on every value this row can produce (n_decl 0 to 16). The rungs write the simplified form because a bitwise `&` on a spec-mode `int` has no type in Verus and R4 and R5 must be the same program. `model.py::_real_size` keeps the rounding and applies it, so the two spellings are checked against each other on every call. No semantics."
      },
      {
        "what": "the four Rust rungs store a pool INDEX where the C stores a zend_class_entry *",
        "kind": "projection",
        "where": "zend.h:334; zend_compile.c:2571, :1951; zend_operators.c:1535",
        "why": "⚠⚠ THE ONE DIVERGENCE THE ROW'S LADDER TURNS ON, DECLARED RATHER THAN LEFT TO BE NOTICED, and it is ph45's precedent: safe Rust has no expression that turns an integer into a place and no way to store an address in memory it owns, so a faithful safe port must OWN its pool and the value in the slot becomes an index. The consequence for the proof is stated in `verus.unsafe_justifications.pool_get_unchecked`: where the C's obligation is one fact (the pointer designates a class) the Rust rungs' is a conjunction (the slot is initialised AND its value is in range). The fault class is unchanged -- an uninitialised u32 used as an unchecked index into an 8-entry array reaches up to 32 GiB away, exactly as an indeterminate pointer does."
      },
      {
        "what": "safe_tuned.rs reserves the count once instead of erealloc'ing per interface",
        "kind": "projection",
        "where": "php-5.2.0's zend_do_implement_interface",
        "why": "php-5.2.0 grows the array one slot at a time -- `erealloc(..., ++current_iface_num)` -- i.e. O(n) allocations per declaration. R3 reserves `n_decl` once and pushes into it, i.e. ONE allocation, the same count as every other rung. That is what keeps §B1a's precondition true of the whole row rather than of five sixths of it, which is what lets the cross-language column go out without an allocator caveat. ⚠ It also means R3's `push` never reallocates, so `Vec`'s growth schedule is not in any published number; the guard `if slots.len() < num_interfaces` is what makes that true of every input and not only of the benign ones."
      },
      {
        "what": "safe_tuned.rs carries no `idx[]` index array",
        "kind": "deletion",
        "where": "zend_compile.c:2591",
        "why": "php-5.2.0's `zend_do_implements_interface` is `num_interfaces++` and nothing else -- the compile-time index is gone, which is the structural half of the repair and, later and independently, what the corpus's own excluded `be8daf1f47fa` did in 2008. R3 is that program, so its phase 1 is O(1) where every other rung's is O(n_decl). ⚠ DECLARED BECAUSE IT IS A REAL COST DIFFERENCE and not plumbing: NOTES.md 8 prices it rather than letting it sit inside \"R3 is cheapest\"."
      },
      {
        "what": "R4 and R5 carry a one-byte-per-slot `wrote[]` witness that no C rung has",
        "kind": "projection",
        "where": "c/kernel.c's ph53_instanceof_ex; verus.rs",
        "why": "⚠⚠⚠ THE LARGEST DIVERGENCE ON THE ROW AND IT IS A RESULT RATHER THAN A CHOICE. A faithful unsafe port scans `0..num_interfaces` and `assume_init()`s every slot, and that program CANNOT BE VERIFIED: `assume_init`'s precondition is `m.mem_contents().is_init()`, coverage is a property of the op stream (i.e. of attacker data), and the pinned driver loop calls the kernel with no test, so there is no call site at which to establish it and no `requires` that could carry it. R4/R5 therefore carry the cheapest witness that discharges it. ⚠ The consequence is that R4 does NOT reproduce the defect -- on `inputs/adversarial-cmp.bin` it answers correctly where R1 reads a slot nobody wrote -- and `controls/r4_nowitness.rs` is the program that does, measured, Miri'd and refused by Verus with its error text. NOTES.md 11."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠ FOUR of these fifteen entries are about the RUST rungs rather than about the extraction, and that is deliberate: §A2 asks for every way the row's C differs from the tarball, and `.memory-php/02-ladder.md` adds that R2-R5 are not ports of R1h -- so the places where the Rust rungs are a different program from both C rungs are exactly what a reader needs and exactly what no line citation can carry. ⚠⚠ ONE ENTRY'S `why` DOES NOT END IN \"no semantics\" AND CANNOT: the `wrote[]` witness changes the answer on an input where the defect is reached, because it is what makes R4 memory-safe. §A2 says a divergence that changes behaviour is a `modelled` tier -- and that is a statement about the row's C, which does not have the witness. The tier is `narrowed` on the C and the Rust-side divergence is reported as the row's finding.",
    "root_cause_ids": [
      "storage-grown-to-num_interfaces-with-the-tail-never-written-then-read"
    ],
    "cwe": "CWE-824",
    "cwe_note": "index.csv records `crashes_pristine_5_0_0 = True`, `build = asan`, `wild-pointer-deref` and CWE-824 for CRASH-158, and this row reproduces exactly that: on a blob whose QUERY_DEREF reaches an unwritten slot, gcc -O1 -fsanitize=address,undefined reports `member access within misaligned address 0xbebebebebebebebe for type 'struct ph53_iface'` followed by `SEGV on unknown address`, caused by a READ (controls/r1h_consumers.py). ⚠⚠ THE READ THAT CAUSES IT IS IN BOUNDS, WHICH IS WHY THE CWE IS 824 AND NOT 125: the slot is inside the reallocated block and nothing has been freed, so there is nothing for ASan to say about the read ITSELF -- an uninitialised read of live memory is MSan's class, not ASan's -- and what ASan sees is the dereference of the value that came out. ⭐ Miri is the only detector in this tree that sees the read itself, which is why `miri.required` is true and why the reason field says so. `ph32` is the cross-reference: same C shape, sized to the literal, excess PAST the end, CWE-125.",
    "fix_commit": "d09cdd9f71f34deab4b99f4e63523fb94164a724",
    "fix_commit_note": "⚠⚠⚠ NOT THE SHA THE CORPUS COLUMN GIVES, AND BOTH ARE CITED WITH WHICH IS WHICH (PROTOCOL_PHP.md F5(iii)). `index.csv` and `.tasks-php/FIXSURVEY_001.md` give `be8daf1f47fa` (2008-03-12); it is EXCLUDED TWICE INDEPENDENTLY. (i) `.tasks-php/preimage_screen.py` labels it NOT-THE-REPAIR: neither cited 5.0.0 line is in the pre-image of its `Zend/zend_compile.c` hunk. (ii) The release-tag walk is decisive on its own: the cited `erealloc` line is present at php-5.0.0 through php-5.0.4 and GONE at php-5.0.5, TWO YEARS AND NINE MONTHS before that commit (TASK_PHP_040_REPORT 2.2, which tracks the enclosing function across seven refs). ⭐ The commit that removes the 5.0.0 defect is `d09cdd9f71f3` -- Dmitry Stogov, 2005-06-08, \"Fixed valgrind errors\", 1 file, 1 hunk, 2 insertions, 1 deletion, first shipped in php-5.0.5 -- found by bisecting the one-release bracket the tag walk produced. The removed line is BYTE-IDENTICAL to 5.0.0's `:2571`, and `patch -p1 --dry-run` on the pristine tarball gives `Hunk #1 succeeded at 2568 (offset -14 lines)`, zero fuzz, exit 0. Both patches are in `controls/`: `d09cdd9f71f3.patch` (sha256 4f97b625fc9772d6..., 1026 B) and `be8daf1f47fa.patch` (sha256 42190b44ad8068c3..., 7397 B), the second so a reader who finds the column does not have to re-fetch it to re-refute it. ⚠⚠ AND THE FIX IS INCOMPLETE: it does not remove the fault, it makes it deterministic, at two different severities on the row's two consumers. See `idiom.why` and NOTES.md 5.",
    "invariant": "I19",
    "obligation": "O2",
    "invariant_note": "`CATALOGUE.md`'s T3 row for ph53 declares I19/O2 and this row carries the declaration forward unchanged; the labels live in `paper/invariants-166.json` and are ATTRIBUTED rather than re-derived here. ⚠ `invariant` and `obligation` are UNVALIDATED DECLARATIONS (PROTOCOL_PHP.md D) and nothing in the gate reads them. What the proof actually discharges is written out in `verus.obligations_note`, in the spelling the pinned vstd has: `wrote@[j] ==> slots@[j].mem_contents().is_init() && slots@[j].mem_contents().value() < n_pool`.",
    "echoes": [
      "p27"
    ],
    "echoes_note": "`CATALOGUE.md` names p27 as the closest PAT analogue and this row keeps the cross-reference. PLAN_PHP.md 3.1 makes an overlap a CROSS-REFERENCE and NEVER a filter -- `patterns-php/` is fresh and stands on its own. ⚠ AND THE MORE USEFUL CROSS-REFERENCE IS INSIDE THIS PROGRAMME: `ph32` is the same C shape sized from the OTHER number -- to the literal, so its excess is PAST the end (CWE-125) -- and `CATALOGUE.md`'s own T3 note says cross-reference, do not merge. This row is CWE-824 because the excess is INSIDE the block, which no built row in either programme prices.",
    "uses_allocator": true,
    "uses_allocator_why": "c/kernel.c and c/kernel_hardened.c make exactly ONE `php_shim_erealloc`/`php_shim_emalloc` call per kernel call when `n_decl > 0` and NONE when `n_decl == 0`, plus one `php_shim_efree` in the teardown, and `php_shim_reset()` at the top of every call (§B1.3). `php_shim_tally()` is folded into the returned u64 (§B1.2) and the four Rust rungs reproduce it arithmetically. ⚠ DECLARED, NEVER DETECTED (TASK_PHP_008 0.4) -- nothing reads this field, and the `c/emalloc_shim.h` symlink is unconditional whatever it says. ⭐ The allocation ORDER is declared in `idiom.required`'s last entry, per §B1a.2."
  }
}
```
