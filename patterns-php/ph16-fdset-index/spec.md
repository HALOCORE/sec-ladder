# ph16 — `FD_SET` past an on-stack `fd_set`

**PHP 5.0.0, `ext/standard/streamsfuncs.c:518-548`, corpus row CRASH-098, tier
`narrowed`.** `stream_array_to_fd_set` takes an `int` out of `php_stream_cast`
and uses it as a bit position in an `fd_set` the *caller* declared, with nothing
between the two: `FD_SETSIZE` does not appear in the function.

⭐ **The object it overflows is `PHP_FUNCTION(stream_select)`'s `fd_set rfds,
wfds, efds;` (`:658`), and the function reads all three back** through
`php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)` at `:706`. So an over-index
lands in a **live neighbouring object** whose value the result depends on. That
is this row's oracle, and it is why the row needs no `volatile` canary.

⚠⚠ **Stock ASan sees it for 32 bytes and then stops.** Measured on this frame:
index 1024…1279 (byte offset 128…152) is reported `stack-buffer-overflow`;
index 1280…3071 (offset 160…376) is **silent**, because past the redzone the
write lands in `wfds`. `adversarial-redzone.bin` and `adversarial-silent.bin`
differ in that one number and in nothing else. `NOTES.md` §3.

⚠⚠⚠ **One of the four measured C cells already carried this row's own bound,
and the toolchain put it there.** Ubuntu's gcc adds `-D_FORTIFY_SOURCE=3`
whenever it optimises; glibc's fortified `FD_SET` is `__fdelt_chk`, and
`c-gcc-O3` aborted with `*** bit out of range 0 - FD_SETSIZE on fd_set ***`
while charging **14.87 Ir per benign `FD_SET`** (+60.6 % whole-program
on `small.bin`). Both C rungs therefore
`#undef _FORTIFY_SOURCE`; `controls/fortify.py` measures both configurations.
`NOTES.md` §2.

**R1h is the POSIX branch of `99e290f882c9`** (Wez Furlong, 2004-09-17,
*"Bug #24189: possibly unsafe select(2) usage"*) — and it is **three** guards,
one of them in the caller's frame. `NOTES.md` §4 has each one priced separately.

The machine-readable contract follows. `harness-php/gate.py ph16-fdset-index`
enforces it; `README.md` is the reader's entry point and `NOTES.md` carries the
measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "8 <= len"
  ],
  "ensures": [
    "result == fdset_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (fdset_fold). `fdset_fold` is model.py's SECOND, independent implementation -- pure transitions driven to a fixpoint, mirroring verus.rs's `walk` and `fold16` one application at a time -- and not the simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic windows model.py builds itself, spanning every `ctl` value in 0..63, every entry tag, both sides of the guard's boundary and every split of five strides. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. A THIRD spelling -- `_dumb`, which collects the set of indices each array legitimately sets and then materialises the sixteen words from it -- checks every shipped window as well.",
  "idiom": {
    "required": [
      {
        "c": "FD_SET(this_fd, fds)",
        "rust": "1u64 << (this_fd % 64)"
      },
      {
        "c": "if (this_fd > *max_fd)",
        "rust": "this_fd > *max_fd"
      },
      {
        "c": "`fd_set rfds, wfds, efds;` -- THE THREE fd_sets ARE THREE SEPARATE LOCALS OF ONE FRAME, in upstream's declaration order -- streamsfuncs.c:658. Packing them into an array or a struct, or shipping ONE set instead of three, changes what an over-index lands in and DELETES THE ROW: it is the SEPARATENESS that makes the write land in a live object rather than in padding, and it is what gives this row an oracle a sanitizer cannot supply. controls/oracle.py is the mechanical check -- it predicts the corrupted checksum from the measured frame layout and reproduces the binary bit for bit under both compilers. ⚠ PER-LANGUAGE because the two spellings share no token, and NOT because the fact differs: this entry was a PLAIN STRING until the first gate run, which reported both of its spellings as pinning nothing in the other language.",
        "rust": "`[u64; NW]`, three of them -- THE THREE fd_sets ARE THREE SEPARATE LOCALS OF ONE FRAME, in upstream's declaration order -- streamsfuncs.c:658. Packing them into an array or a struct, or shipping ONE set instead of three, changes what an over-index lands in and DELETES THE ROW: it is the SEPARATENESS that makes the write land in a live object rather than in padding, and it is what gives this row an oracle a sanitizer cannot supply. controls/oracle.py is the mechanical check -- it predicts the corrupted checksum from the measured frame layout and reproduces the binary bit for bit under both compilers. ⚠ PER-LANGUAGE because the two spellings share no token, and NOT because the fact differs: this entry was a PLAIN STRING until the first gate run, which reported both of its spellings as pinning nothing in the other language."
      },
      {
        "c": "R1h IS THE POSIX BRANCH OF 99e290f882c9 (Wez Furlong, 2004-09-17, 'Bug #24189: possibly unsafe select(2) usage'), WHICH IS THREE GUARDS AND NOT ONE, and R2-R5 implement the same function, because that configuration is COMPLETE: it removes every out-of-range FD_SET and changes no benign answer (controls/fix_scope.py Q1/Q2). The three, all from main/php_network.h's macros as the commit adds them: (a) && this_fd >= 0 appended to the php_stream_cast test at :540; (b) FD_SET -> PHP_SAFE_FD_SET at :541, i.e. `do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)`; (c) PHP_SAFE_MAX_FD(max_fd, max_set_count) inserted in PHP_FUNCTION(stream_select), i.e. do { if (m >= FD_SETSIZE) { _php_emit_fd_setsize_warning(m); m = FD_SETSIZE - 1; }} while(0). ⚠ (c) IS NOT ABOUT THE WRITE and the row does not let that pass unsaid: `*max_fd = this_fd` sits INSIDE the arm (b) protects and is NOT bounded by it, so without (c) php_select is still handed an nfds past FD_SETSIZE. This row folds max_fd, so (c) is observable in the checksum and controls/fix_scope.py prices it apart from (b). ⚠ (a) IS DEAD ON THIS KERNEL'S DOMAIN: `this_fd` is PH16_IDX(e), a 14-bit field, so it is in 0..=16383 and never negative. It is carried anyway, because it is the shipped POSIX configuration, and its deadness is MEASURED (fix_scope.py Q3) rather than argued. A kernel admitting negative indices would model FD_SET(-1, ...) = 1UL << -1, undefined behaviour in the SHIFT rather than the out-of-bounds WRITE this row is about; PLAN_PHP.md 3.1 admits that as a variation and its own row, and NOTES.md §9 says so. ⭐ WHICH BRANCH IS COMPILED IS PART OF THE CLAIM: on PHP_WIN32 all three macros are unguarded or warning-only, and the comment saying so is CORRECT, because Win32's fd_set is a counted array of SOCKETs. We build POSIX. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it. The mechanical checks are controls/negatives.py --emit noguard, which must NOT verify, and controls/fix_scope.py, which prices each guard separately. ⚠⚠ THE ONLY BACKTICKED SPELLING IN THIS ENTRY IS PHP_SAFE_FD_SET's POSIX BODY, ON THE C SIDE, and it is scoped-absent from c/kernel.c by design -- that absence IS the row. Everything else here is quoted as PLAIN TEXT on purpose: the first version backticked the other four and the gate's audit reported all four as pinning nothing in either language, which is check.py's pins_nothing class -- the one it calls the class that carries real defects.",
        "rust": "R1h IS THE POSIX BRANCH OF 99e290f882c9 (Wez Furlong, 2004-09-17, 'Bug #24189: possibly unsafe select(2) usage'), WHICH IS THREE GUARDS AND NOT ONE, and R2-R5 implement the same function, because that configuration is COMPLETE: it removes every out-of-range FD_SET and changes no benign answer (controls/fix_scope.py Q1/Q2). The three, all from main/php_network.h's macros as the commit adds them: (a) && this_fd >= 0 appended to the php_stream_cast test at :540; (b) FD_SET -> PHP_SAFE_FD_SET at :541, i.e. do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0); (c) PHP_SAFE_MAX_FD(max_fd, max_set_count) inserted in PHP_FUNCTION(stream_select), i.e. do { if (m >= FD_SETSIZE) { _php_emit_fd_setsize_warning(m); m = FD_SETSIZE - 1; }} while(0). ⚠ (c) IS NOT ABOUT THE WRITE and the row does not let that pass unsaid: `*max_fd = this_fd` sits INSIDE the arm (b) protects and is NOT bounded by it, so without (c) php_select is still handed an nfds past FD_SETSIZE. This row folds max_fd, so (c) is observable in the checksum and controls/fix_scope.py prices it apart from (b). ⚠ (a) IS DEAD ON THIS KERNEL'S DOMAIN: `this_fd` is PH16_IDX(e), a 14-bit field, so it is in 0..=16383 and never negative. It is carried anyway, because it is the shipped POSIX configuration, and its deadness is MEASURED (fix_scope.py Q3) rather than argued. A kernel admitting negative indices would model FD_SET(-1, ...) = 1UL << -1, undefined behaviour in the SHIFT rather than the out-of-bounds WRITE this row is about; PLAN_PHP.md 3.1 admits that as a variation and its own row, and NOTES.md §9 says so. ⭐ WHICH BRANCH IS COMPILED IS PART OF THE CLAIM: on PHP_WIN32 all three macros are unguarded or warning-only, and the comment saying so is CORRECT, because Win32's fd_set is a counted array of SOCKETs. We build POSIX. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it. The mechanical checks are controls/negatives.py --emit noguard, which must NOT verify, and controls/fix_scope.py, which prices each guard separately. ⚠⚠ THE ONLY BACKTICKED SPELLING IN THIS ENTRY IS PHP_SAFE_FD_SET's POSIX BODY, ON THE C SIDE, and it is scoped-absent from c/kernel.c by design -- that absence IS the row. Everything else here is quoted as PLAIN TEXT on purpose: the first version backticked the other four and the gate's audit reported all four as pinning nothing in either language, which is check.py's pins_nothing class -- the one it calls the class that carries real defects."
      },
      {
        "c": "#define _FORTIFY_SOURCE 0"
      },
      {
        "c": "the guard is spelled this_fd < FD_SETSIZE in c/kernel_hardened.c and safe_naive.rs and w < NW in safe_tuned.rs, unsafe.rs and verus.rs, where `w` is this_fd / 64. NO BACKTICKED SPELLING because the entry is about a PAIR of spellings and a backtick would pin one of them on rungs that legitimately carry the other. They are ONE PREDICATE on a u32 -- f < 1024 iff f / 64 < 16 -- and controls/guard_equiv.py demonstrates that exhaustively over all 16 384 reachable values with must-fire mutants, rather than asserting it. The word-index spelling is what makes the array index provably in range, which is R3's whole tuning and what R4's get_unchecked_mut rests on; the FD_SETSIZE spelling is upstream's own and is what the C rungs write. ⚠ PER-LANGUAGE, and the RUST side keeps both backticks on purpose: this_fd < FD_SETSIZE is present in safe_naive.rs and absent from the other three, and w < NW is the other way round, so the audit reports each as SCOPED-ABSENT -- which is exactly what this entry says. The C side backticks nothing, because c/kernel_hardened.c reaches the guard through PHP_SAFE_FD_SET's parameter name and neither literal occurs; the first version was a plain string and the audit reported five spellings pinning nothing on the C rungs.",
        "rust": "the guard is spelled `this_fd < FD_SETSIZE` in c/kernel_hardened.c and safe_naive.rs and `w < NW` in safe_tuned.rs, unsafe.rs and verus.rs, where `w` is this_fd / 64. NO BACKTICKED SPELLING because the entry is about a PAIR of spellings and a backtick would pin one of them on rungs that legitimately carry the other. They are ONE PREDICATE on a u32 -- f < 1024 iff f / 64 < 16 -- and controls/guard_equiv.py demonstrates that exhaustively over all 16 384 reachable values with must-fire mutants, rather than asserting it. The word-index spelling is what makes the array index provably in range, which is R3's whole tuning and what R4's get_unchecked_mut rests on; the FD_SETSIZE spelling is upstream's own and is what the C rungs write. ⚠ PER-LANGUAGE, and the RUST side keeps both backticks on purpose: `this_fd < FD_SETSIZE` is present in safe_naive.rs and absent from the other three, and `w < NW` is the other way round, so the audit reports each as SCOPED-ABSENT -- which is exactly what this entry says. The C side backticks nothing, because c/kernel_hardened.c reaches the guard through PHP_SAFE_FD_SET's parameter name and neither literal occurs; the first version was a plain string and the audit reported five spellings pinning nothing on the C rungs."
      }
    ],
    "forbidden": [
      "`& 1023` and `% FD_SETSIZE` -- MASKING the index instead of testing it. It keeps the write in bounds and sets THE WRONG BIT, so it is a repair that silences every detector this row has while changing the answer, and it is the first thing a reader reaches for. Upstream did not do it: 99e290f882c9 SKIPS the descriptor.",
      "`[0u64; 32]` -- oversizing the fd_set so that the write is in bounds. The object's size is fixed by <sys/select.h> and by FD_SETSIZE; a rung that gave itself more room would be measuring a different object and would delete the row. The C rungs carry a C99 compile-time assertion that the platform's fd_set really is 16 words. ⚠ NOTE THE ABSENCE OF BACKTICKS in this sentence and in the next entry: in a `forbidden` entry EVERY backticked span becomes a banned token, so an entry that quotes what it is protecting bans that too. The first draft of this block quoted sizeof(fd_set), wfds and efds in its own prose and the gate refused fourteen (spelling x rung) obligations for it -- which is check.py's documented false-positive shape 'an entry that backticks its REPLACEMENT', firing on a row for the first time.",
      "`volatile` -- a scaffolding local added to the frame purely to witness the write. .temp/mgr166/asan_reach.c needed one because it controlled its own frame; this row does not, because PHP's own second and third fd_sets are the witnesses. A rung that added one would be measuring a frame PHP does not have, and would put an object the compiler may not move in the middle of the layout the oracle's completeness range is stated against."
    ],
    "why": "ph16 is `stream_array_to_fd_set` out of PHP 5.0.0, `ext/standard/streamsfuncs.c:518-548`, corpus row CRASH-098, tier `narrowed`. THE IDIOM IS AN INDEX TAKEN FROM THE OUTSIDE AND USED AS A BIT POSITION IN A FIXED-SIZE OBJECT, WITH NOTHING BETWEEN THEM. `:540` tests whether the cast SUCCEEDED and `:541` writes with what it produced: `FD_SET(this_fd, fds);`, and `FD_SETSIZE` appears nowhere in the function. `FD_SET` is a pure bit-set macro -- `fds->__fds_bits[d / 64] |= 1UL << (d % 64)` -- and consults no file-descriptor table, so index 2048 writes at byte offset 256 of a 128-byte object. ⭐ AND `fds` IS THE CALLER'S: `PHP_FUNCTION(stream_select)` declares `fd_set rfds, wfds, efds;` at `:658` and reads all three back at `:706` through `php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)`. So the bytes an over-index reaches are a LIVE NEIGHBOURING OBJECT the function's own result depends on -- which is this row's oracle, and it needs no scaffolding. ⚠⚠ THAT IS ALSO WHY STOCK ASan CANNOT SEE IT. Measured on this frame (NOTES.md §3): under `-fsanitize=address` each stack object gets a 32-byte redzone, so index 1024..1279 (offset 128..152) is REPORTED `stack-buffer-overflow` and index 1280..3071 (offset 160..376) is SILENT, because past the redzone the write lands in `wfds` -- a real object, with nothing for a sanitizer to say. `adversarial-redzone.bin` and `adversarial-silent.bin` differ in that one number and in nothing else. ⚠⚠⚠ AND ONE OF THE FOUR MEASURED C CELLS ALREADY CARRIED THE ROW'S OWN BOUND, PUT THERE BY THE TOOLCHAIN: Ubuntu's gcc adds `-D_FORTIFY_SOURCE=3` whenever it optimises, glibc's fortified `FD_SET` is `__fdelt_chk`, and `c-gcc-O3` aborted with `*** bit out of range 0 - FD_SETSIZE on fd_set ***` while paying 14.87 Ir per BENIGN `FD_SET` -- +60.6 % whole-program on `small.bin`, 92 605 764 -> 148 709 085 Ir over 3 773 157 `FD_SET`s, counted rather than estimated. Both C rungs therefore `#undef _FORTIFY_SOURCE` before the first system header, itemised in `provenance.divergences` and measured in `controls/fortify.py` -- without it R1 is not R1 in half the gcc cells and the tax reads as C-versus-Rust. ⚠ R1h IS THE POSIX BRANCH OF `99e290f882c9` AND IT IS THREE GUARDS, NOT ONE: `&& this_fd >= 0` at the call site, `PHP_SAFE_FD_SET`'s `if (fd < FD_SETSIZE)`, and `PHP_SAFE_MAX_FD`'s clamp of `max_fd` IN THE CALLER'S FRAME -- which is not about the write at all, because `*max_fd = this_fd` sits inside the arm the second guard protects but is not bounded by it. Guard (a) is DEAD here (`this_fd` is a 14-bit field) and the row says so and measures it rather than banking it. ⭐ A MACRO NAMED `PHP_SAFE_...` WHOSE SAFETY IS `#ifdef`-CONDITIONAL, and the Win32 comment is correct: there `fd_set` is a counted array of `SOCKET`s, so the bound lives in the platform's data structure instead of in the code. `c/kernel_hardened.c` states which branch it compiles. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "fdset_fold": "fdset_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 15
    },
    "twin_obligations": {
      "verus.rs": 18
    },
    "obligations_note": "15 verified / 0 errors, and 18 under `--cfg slb_twin` -- three trusted accessors, therefore three twins. ⭐ WHAT THE PROOF RESTS ON IS ONE INDEX BOUND AND NOT A TERMINATION ARGUMENT, and that is this row's finding on the Verus side: `walk`'s `decreases` is the trivial `n - i` of a counted loop, so unlike ph03 and ph07 -- whose obligations are about a cursor advanced by the data -- everything interesting is the single `w < NW` that licenses `aset_unchecked`. That test IS 99e290f882c9 guard (b). The window reads rest on a SECOND and unrelated fact, `off + len <= buf@.len()` plus `m = (len - 6) / 2`, which comes from the harness's contract and not from PHP; NOTES.md §10 keeps the two apart, because an editor who deleted the 2004 patch would be removing the precondition of one class and not the other.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 15 shipped + 3 for slb_twin_get_unchecked, slb_twin_aget_unchecked and slb_twin_aset_unchecked. ⚠⚠ `#[verifier::rlimit(30)]` IS ON THE KERNEL AND THE EXPENSIVE SIDE IS THE TWIN, WHICH IS THE INVERSE OF ph07. Bisected on this box: as first written the kernel needed 16 plain (FAILED at 14) and 1 twin; adding nine `let ghost` bindings that name every quantity `fdset_win` names took it to 6 plain (FAILED at 4); hiding the three arms' `if` behind `arm_state`/`arm_sets` took it to 2 plain and pushed the TWIN to 10, FAILING at 8. ⭐ The cost was ATTACKED FIRST and the attack worked on the side it could reach: 16 -> 2 plain. What it could not reach is the twin build, where three more verified functions add to the module's SMT context and the kernel needs the whole default of 10. A proof that passes on one side of a coin flip is not a proof, so the budget is 30 -- 3x the worst measured requirement. NOTES.md §10 has the table.",
    "items": {
      "verus.rs": {
        "ent_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tag_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fd_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "word_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mask_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold16": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zero16": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "arm_state": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "arm_sets": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fdset_win": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fdset_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "get_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_get_unchecked": {
          "external": null,
          "requires": [
            "i < v@.len()"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "aget_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < NW"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "slb_twin_aget_unchecked": {
          "external": null,
          "requires": [
            "i < NW"
          ],
          "ensures": [
            "r == a@[i as int]"
          ]
        },
        "aset_unchecked": {
          "external": "verifier::external_body",
          "requires": [
            "i < NW"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
          ]
        },
        "slb_twin_aset_unchecked": {
          "external": null,
          "requires": [
            "i < NW"
          ],
          "ensures": [
            "final(a)@ == old(a)@.update(i as int, x)"
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
        "to_fd_set": {
          "external": null,
          "requires": [
            "6 + 2 * (base + n) <= win@.len()"
          ],
          "ensures": [
            "r == arm_sets(not_an_array)",
            "(final(fds)@, *final(max_fd)) == arm_state(win@, base as int, n as int, not_an_array, old(fds)@, *old(max_fd))"
          ]
        },
        "fold_set": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == fold16(s@, NW as int, 0u64)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "8 <= len"
          ],
          "ensures": [
            "r == fdset_fold(buf@, off as int, len as int)"
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
        "aset_unchecked": "`x: u64` is a PURE VALUE and needs no precondition. The unchecked operation is `*a.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `a` being a live `[u64; 16]`, and on NOTHING about the word being written -- every one of the 2^64 values of `x` is a legal `u64` store into a word that is already initialised (`[0u64; NW]` initialises the whole array before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < NW`, and the `ensures` names `x` in the post-state -- `final(a)@ == old(a)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition. ⚠ THAT COMPLETENESS IS EXACTLY WHAT THIS ROW IS ABOUT ONE LEVEL DOWN: `FD_SET`'s C definition has no such contract, and the whole defect is a write whose destination nothing constrains.",
        "aget_unchecked": "`a: &[u64; NW]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its length is in its TYPE, so there is nothing about it left for a `requires` to say: `a@.len() == NW` holds for every `a` this signature admits, by `vstd::array::array_len_matches_n`. The only quantity that can make `*a.get_unchecked(i)` undefined is `i`, and `i` IS constrained, by `i < NW`. Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. ⚠ IT IS NOT THE SAME ARGUMENT AS `get_unchecked`'s, and that is why this entry exists and that one does not: `get_unchecked` takes a SLICE, whose length is a run-time fact, so its `requires` has to name it (`i < v@.len()`) and the stage is satisfied without a declaration. Here the length is a constant of the type and the honest `requires` mentions only `i`. ⭐ THAT DIFFERENCE IS THE ROW ONE LEVEL UP: `fd_set`'s size is a compile-time constant of the platform too, and `streamsfuncs.c:541` still manages not to consult it."
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph16's two probe shapes have different work per call (550 and 4076 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW and the number of entries the kernel walks is `(stride - 6) / 2`, an affine function of it, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ THERE IS ALSO A FIXED PER-CALL TERM AND IT IS LARGE: three FD_ZEROs (3 x 128 bytes) and a 48-word fold happen on every call whatever the stride, plus two `%` for the split. So the marginal is NOT a pure walk rate and NOTES.md §8 decomposes it rather than presenting it as one."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "exact",
      "why": "R4 == R5 at O3 EXACTLY, and `exact` rather than `norel` because this kernel calls out to nothing -- no memcpy, no allocator, no PLT entry -- so there are no relocation bytes to differ. Measured against the SHIPPED record (`results-php/ph16-fdset-index.json`), O3/isolated: 425 instructions and 1775 bytes in BOTH cells, `md5_fn` identical at `659d7b4b4168`. ⚠ THIS ENTRY FIRST SAID 426, from a hand build with different flags taken before the gate ran; PROTOCOL.md rule 6's addendum is that a frozen declaration is evidence about WHEN it was written and not about whether it is still true, and NOTES.md §12 is the pass that caught it. The disassembly is byte-for-byte identical except for the crate name inside jump-target annotations, with every target address identical. The proof licenses the three unchecked classes at ZERO instructions. ⚠ AT O0 THE TWO GENUINELY DIFFER -- 527 vs 488 instructions in the record (533 vs 501 in that same hand build) -- because at O0 nothing is inlined, so R5's three trusted wrappers survive as real calls where R4's `#[inline(always)]` helpers do not; that is codegen, not layout. ⚠ The figures in this entry are pre-measurement disassembly counts taken on the shipped sources; NOTES.md §8 carries the numbers from the measurement record and PROTOCOL.md rule 6's addendum says to re-read this entry against THOSE rather than trusting the hash."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph16 has THREE such items and one of them WRITES (`aset_unchecked`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `a@[i] == x` would let a body that also clobbered `a[i + 1]` through every Verus stage. The shipped `ensures` is the whole post-state, `old(a)@.update(i, x)`, and Miri is the backstop for the class regardless. ⭐ IT MATTERS MORE HERE THAN ON ANY ROW SO FAR, AND THE REASON IS THE ROW'S OWN FINDING: the defect this pattern models is a write past a stack object that STOCK ASan CANNOT SEE past 32 bytes, so if a Rust rung ever re-acquired it, the detector every other row relies on would be silent. controls/miri_vs_asan.py measures exactly that asymmetry on a mutant of unsafe.rs with the guard removed.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph16's cost is 4 x (one window walked and three fd_sets folded), i.e. 4 x 272 entries at worst -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "ext/standard/streamsfuncs.c",
    "c_lines": [
      518,
      548
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/streamsfuncs.c | sed -n '518,548p'",
    "extract_sha256": "e3fbdff6d5e63f8e68f34884375d9256c84167858759563ca06a7aabe68f9ff1",
    "extra_spans": [
      {
        "c_file": "ext/standard/streamsfuncs.c",
        "c_lines": [
          653,
          718
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/streamsfuncs.c | sed -n '653,718p'",
        "extract_sha256": "bad87d1ad43233f1f6dd8b643e30b5c418e69206f2b6062496fa44d5e00b1cf8",
        "why": "⚠⚠ THE CALLER FRAME, AND ON THIS ROW IT IS NOT CONTEXT -- IT IS THE OBJECT THE DEFECT OVERFLOWS. `PHP_FUNCTION(stream_select)` declares `fd_set rfds, wfds, efds;` at :658, calls stream_array_to_fd_set three times on them at :670-672, and reads all three back at :706 through php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p). c/kernel.c's `kernel()` wrapper IS this code -- the three sets, the three FD_ZEROs, the shared `int max_fd`, the `sets` accumulation and the `if (!sets) RETURN_FALSE` arm at :674-677. ⭐ AND IT IS THE FRAME ONE THIRD OF R1h OCCUPIES: 99e290f882c9 inserts PHP_SAFE_MAX_FD HERE, not in stream_array_to_fd_set, so with only the :518-548 span pinned the overlap report would certify a span containing neither the object nor a third of the fix. The end of the span is :718 and not :719 because :719 is the closing brace of PHP_FUNCTION, which the wrapper does not lift."
      }
    ],
    "extra_spans_note": "THE ROW LIFTS TWO SPANS AND BOTH ARE PINNED. `provenance.c_lines` names the defect site (streamsfuncs.c:518-548, `stream_array_to_fd_set`); `extra_spans[0]` names the caller frame (:653-718, `PHP_FUNCTION(stream_select)`), which is where the three `fd_set`s live and where guard (c) goes. They are in the SAME file, unlike ph07's three, and the kernel overlap is computed over the union. ⚠ What is NOT pinned as a span is main/php_network.h's macro block, and deliberately: it does not exist in 5.0.0 -- 99e290f882c9 ADDS it -- so there is no pristine-tarball span to cite. It is quoted in c/kernel_hardened.c's header and its bytes are at controls/99e290f882c9.patch.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "streamsfuncs.c:518, :670-672",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "the zend_hash cursor triple becomes an index walk over a flat entry run",
        "kind": "substitution",
        "where": "streamsfuncs.c:527-529",
        "why": "`zend_hash_internal_pointer_reset` / `zend_hash_get_current_data` / `zend_hash_move_forward` iterate a container whose own count is what bounds the loop; the kernel walks `n` entries of the window instead, with `n` derived so the split is TOTAL by construction. The loop body, the branch structure and the number of iterations are unchanged. `.memory-php/01-extraction.md`: extraction cost is priced at the DEFECT site, and four rows have already been killed by pricing an adjacent frame's machinery. No semantics on the extracted domain."
      },
      {
        "what": "php_stream_from_zval_no_verify + `stream == NULL` becomes entry tag 0",
        "kind": "substitution",
        "where": "streamsfuncs.c:531-534",
        "why": "the arm is kept, one for one -- an entry with tag 0 takes the `continue`. What is removed is the zval-to-`php_stream *` unpacking, which is the wrapper `narrowed` names. No semantics."
      },
      {
        "what": "php_stream_cast(...) == SUCCESS becomes entry tags 1 (FAILURE) and 2/3 (SUCCESS)",
        "kind": "substitution",
        "where": "streamsfuncs.c:540",
        "why": "`php_stream_cast` is in main/streams/streams.c and dispatches on the stream's ops; what reaches :541 is an `int` written through its out-parameter and a SUCCESS/FAILURE verdict, and both are what the entry carries. TWO success encodings (2 and 3) are used so that a rung testing `tag == 2` rather than `tag != 1` is wrong on the corpus; `inputs/gen.py::_check_span` asserts both are present. No semantics."
      },
      {
        "what": "Z_TYPE_P(stream_array) != IS_ARRAY becomes a `ctl` bit",
        "kind": "substitution",
        "where": "streamsfuncs.c:524-526",
        "why": "the arm is kept and returns 0 exactly as upstream does; only the zval type test itself is gone, which is argument checking. `inputs/gen.py` asserts the corpus reaches it for all three arrays. No semantics."
      },
      {
        "what": "`if (r_array != NULL)` becomes a `ctl` bit",
        "kind": "substitution",
        "where": "streamsfuncs.c:670-672",
        "why": "same shape as above, one frame up: the arm is kept and the zval NULL test is gone. No semantics."
      },
      {
        "what": "zend_parse_parameters, the timeout construction, stream_array_emulate_read_fd_set, php_select and the three stream_array_from_fd_set calls",
        "kind": "deletion",
        "where": "streamsfuncs.c:663, :678-693, :695-703, :706, :714-716",
        "why": "argument parsing and everything DOWNSTREAM of the write. The fold of the three fd_sets and of `max_fd` stands in for :706's consumption of them, which is the only property of that line this row needs -- that all three objects are live across the calls. ⚠ One of the deleted lines, :577's FD_ISSET inside stream_array_from_fd_set, is a DIFFERENT uncatalogued defect site of the same commit; NOTES.md §9 says so and does not adjudicate it. No semantics on the extracted domain."
      },
      {
        "what": "_php_emit_fd_setsize_warning(m) inside PHP_SAFE_MAX_FD",
        "kind": "projection",
        "where": "main/php_network.h, 99e290f882c9's POSIX arm",
        "why": "PHP raises a diagnostic on its error handler and returns void; this kernel has no error handler, so only the CLAMP the warning precedes is carried. Nothing observable in the returned u64 depends on it. R1h-only."
      },
      {
        "what": "set_count / max_set_count in PHP_FUNCTION(stream_select)",
        "kind": "deletion",
        "where": "99e290f882c9's streamsfuncs.c hunk at :670-696",
        "why": "the POSIX arm of PHP_SAFE_MAX_FD ignores its second argument entirely -- it is the Win32 arm that reads it -- so the bookkeeping the patch adds is dead on this platform. Carrying it would be dead code `-Wall -Wextra` warns about. R1h-only. No semantics on POSIX."
      },
      {
        "what": "_FORTIFY_SOURCE is #undef'd and set to 0 in both C kernels",
        "kind": "substitution",
        "where": "c/kernel.c:1-4, c/kernel_hardened.c:1-2",
        "why": "⚠⚠ THE TOOLCHAIN, NOT THE SOURCE, AND IT IS THE ROW'S OWN BOUND. Ubuntu 24.04's gcc spec adds -D_FORTIFY_SOURCE=3 whenever it is optimising, and glibc's fortified FD_SET is __FD_ELT -> __fdelt_chk, which tests exactly `d < FD_SETSIZE`. Measured (controls/fortify.py): gcc -O0 undefined and the write survives; gcc -O3 = 3 and the write ABORTS with `*** bit out of range 0 - FD_SETSIZE on fd_set ***`; gcc -O3 with this #undef survives; clang never fortifies at either level. On BENIGN, in-range indices the check costs 14.87 Ir per FD_SET ON THIS ROW: callgrind on small.bin, 92 605 764 -> 148 709 085 Ir (+60.6 % whole-program) over 3 773 157 FD_SETs, and the denominator is COUNTED from model.py's own decode rather than estimated. ⚠ A standalone probe of a tight FD_SET loop and nothing else gives 7.01, and the first draft of this entry quoted that; it is a different code shape and is not this row's number. Without the #undef `c-gcc-O3` would be a HARDENED rung wearing R1's label and its Ir would carry a bounds-check tax a reader would attribute to C-versus-Rust, while c-clang-O3 carried none. PHP 5.0.0 (2004) was built with no such thing. The substitution is DEMONSTRATED behaviour-preserving on the benign domain by controls/fortify.py, which also reports what it costs and what it catches. No semantics on the benign domain."
      },
      {
        "what": "the Rust rungs spell the guard in the word index",
        "kind": "substitution",
        "where": "main/php_network.h, PHP_SAFE_FD_SET's POSIX arm",
        "why": "c/kernel_hardened.c and safe_naive.rs write `this_fd < FD_SETSIZE`; safe_tuned.rs, unsafe.rs and verus.rs write `w < NW` where `w = this_fd / 64`. They are one predicate on a u32 and controls/guard_equiv.py demonstrates it EXHAUSTIVELY over all 16 384 reachable values against a build of the C itself, with must-fire mutants. The word-index spelling is what makes the array index provably in range, which is what R3's tuning buys and what R4's unchecked store rests on. No semantics."
      },
      {
        "what": "the three fd_sets are `[u64; 16]` in the Rust rungs",
        "kind": "substitution",
        "where": "<sys/select.h>, `fd_set`",
        "why": "glibc's fd_set is `long int __fds_bits[FD_SETSIZE / NFDBITS]`, i.e. sixteen 64-bit words on this platform, and both C rungs carry a C99 compile-time assertion that it is. The Rust rungs declare the same object; FD_SET's `__FDELT`/`__FDMASK` become `f / 64` and `1u64 << (f % 64)`, which is the macro's own definition. ⚠ A Rust rung CANNOT reproduce the defect through this spelling, which is the point of the rung and not a divergence in what is measured: every rung computes the same u64 on every benign input. No semantics on the benign domain."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠ EIGHT of these twelve entries are SUBSTITUTIONS, which is more than any row so far, and the reason is structural rather than sloppy: this defect's frame is a zval array of stream resources, and every step from `zval **` to `int this_fd` is machinery in another file. PROTOCOL_PHP.md A1 requires a substitution in a non-`modelled` tier to be (a) itemised with a line citation, (b) given a `why` ending in 'no semantics' and (c) DEMONSTRATED behaviour-preserving rather than asserted. (c) is discharged by controls/guard_equiv.py for the guard spelling, by controls/fortify.py for the _FORTIFY_SOURCE substitution, and by model.py's three independent implementations plus inputs/gen.py::_check_span for the tag/ctl encodings -- every arm of every substituted test is reached by the measured corpus and asserted to be. ⚠ THIS SENTENCE'S OWN COUNT WAS WRONG WHEN FIRST WRITTEN -- it said SEVEN of THIRTEEN -- and NOTES.md §12's re-read against the shipped tree is what caught it. It is PROTOCOL.md rule 6's addendum in miniature: a frozen sentence about a list that then grew and shrank underneath it, with the hash still matching because nobody had edited the sentence. `.temp/php25/fix_divcount.py` recomputes both numbers from the block rather than hard-coding the repair, so it cannot go stale the same way twice.",
    "root_cause_ids": [
      "stream_array_to_fd_set-fd-not-checked-against-FD_SETSIZE-fd_set-overflow"
    ],
    "cwe": "CWE-787",
    "cwe_note": "index.csv records CWE-787 (out-of-bounds write) and this row reproduces exactly that and nothing else: a `stack-buffer-overflow WRITE of size 8` at c/kernel.c's FD_SET = streamsfuncs.c:541. ⭐ UNLIKE ph03 AND ph07 THERE IS EXACTLY ONE LIMB AND IT IS A WRITE: nothing in this kernel reads out of bounds, because the fold walks the three fd_sets at their declared size. ⚠⚠ AND THE DETECTOR ONLY SEES IT OVER PART OF THE RANGE -- 32 bytes, measured -- which is why this row's model derives `sanitizer_expect` from ASan's redzone rather than from the defect. NOTES.md §3.",
    "fix_commit": "99e290f882c9a1e2b2e9fbe8a1b0dcbcbb7d1b0e",
    "fix_commit_note": "⚠ THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE AND THE ROW USES ITS SHORT FORM EVERYWHERE. `99e290f882c9` -- Wez Furlong, 2004-09-17, 'Bug #24189: possibly unsafe select(2) usage. Where possible we avoid it by using poll(2).' -- first shipped in php-5.1.0; php-5.0.x never received it. TEN files, 27 368 B; the patch bytes are at controls/99e290f882c9.patch. ⚠⚠ CITE THE HUNK, NOT THE COMMIT (PROTOCOL_PHP.md F): the commit also introduces php_poll2, an IPv6 configure probe and an OpenSSL socket rework, none of which is this row. What R1h carries is the POSIX branch of the three main/php_network.h macros applied at the two sites in stream_array_to_fd_set's frame; idiom.required[3] states all three and c/kernel_hardened.c's header quotes them. ⭐⭐ AND THE COMMIT IS A CENSUS OF ITS OWN DEFECT'S SIBLINGS: it patches FOUR unchecked fd-set sites, of which the catalogue has ONE. streamsfuncs.c:577 (FD_ISSET, a READ) and ext/sockets/sockets.c:536 / :563 are uncatalogued, and ext/sockets/sockets.c has no rows at all. NOTES.md §9 records that and DOES NOT adjudicate it -- TASK_PHP_026 owns the question. ⚠ UNVERIFIED IN THIS ROW: whether the sha above is the FIRST commit to close this site. It is what index.csv names, its patch really does add the guard at :541, and the code is guarded at php-5.1.0 and unguarded at php-5.0.0 (UPSTREAM_001.md §4). What was not done is a tag-by-tag bisect of 5.0.x branch backports; PROTOCOL_PHP.md F5(iii) asks for confirmation against the tags and this row confirms the WINDOW (5.0.0 -> 5.1.0) rather than the exact commit.",
    "invariant": "I1",
    "obligation": "O2",
    "echoes": [
      "p02"
    ],
    "echoes_note": "p02-buffer-copy is the closest PAT analogue -- an attacker-controlled quantity used as a destination offset with no bound -- and PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and never a filter. ⚠ The mechanisms differ where it matters: p02 copies a RUN of bytes whose length is attacker-controlled, so its overflow is contiguous and starts at the object's edge; ph16 writes EIGHT BYTES at an attacker-chosen STRIDE of 8 from the object's base, so it can skip arbitrarily far past the object and land in a chosen neighbour without touching anything in between. That is precisely why ASan sees p02 and does not see this: a contiguous run cannot miss a redzone and a strided single word can.",
    "uses_allocator": false,
    "uses_allocator_why": "the kernel allocates nothing. `stream_array_to_fd_set` fills an `fd_set` the CALLER declared as a stack local (streamsfuncs.c:658), and this row's wrapper does the same; no emalloc, no efree, no php_shim_reset, no php_shim_tally. ⚠ DECLARED, NEVER DETECTED (TASK_PHP_008 §0.4) -- nothing reads this field and no verdict depends on it. The row still carries c/emalloc_shim.h as a symlink, because that rule is UNCONDITIONAL: two detectors of exactly this question were built and bypassed (TASK_PHP_005 F-1, TASK_PHP_007 B1/B2), so the audit stopped asking it. ⭐ It is also why this row has NO analogue of PROTOCOL_PHP.md B1.2's tally fold: there is no allocator activity to land in the checksum, and the three fd_sets themselves are what the checksum carries instead."
  }
}
```
