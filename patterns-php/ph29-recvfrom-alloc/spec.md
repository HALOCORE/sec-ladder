# ph29 — `emalloc(to_read + 1)` where the allocator truncates the size

**PHP 5.0.0, `ext/standard/streamsfuncs.c:300-345`, corpus row CRASH-097, tier
`narrowed`.** `stream_socket_recvfrom` asks the allocator for `to_read + 1`
bytes, gets a block of `real_size` bytes, and then hands the transport
`to_read` — the number it asked for. `Zend/zend_alloc.c:129` is
`unsigned int real_size` and `:135` assigns a 64-bit `size_t` into it, so the
two disagree for every `to_read` with `to_read + 1 ≡ 0 (mod 2^32)` and for
every negative one. Nothing in PHP compares them.

⚠⚠⚠ **This is the row that cannot pass without `common-php/emalloc_shim.h`,
and it is the only one.** Under plain `malloc` the defect disappears twice
over, in two different ways: `malloc(2^64 − 2^32)` **fails** (PHP prints and
`exit(1)`s at `zend_alloc.c:189`) and `malloc(2^32)` **succeeds** with a real
4 GiB block, so the write is in bounds. `controls/allocator.py` runs both
directions with must-fire and must-not-fire cases. `PLAN_PHP.md` §4.3 has
warned since Phase 0 that a substituted allocator is not neutral; this row is
where that warning is finally tested by something that fails without it.

⚠⚠ **R1h is the real upstream fix and it does not remove the defect.**
`445daac3ab1a` (Ilia Alshanetsky, 2004-07-28) adds
`if (to_read <= 0) RETURN_FALSE;` — which is exactly what its subject claims,
*"when length parameter has a negative value"* — and
`stream_socket_recvfrom($s, 4294967295)` is positive. The 2006 follow-up
`6ac8ffdfea10` swaps `emalloc` for `safe_emalloc` and does not remove it
either, because `_safe_emalloc` checks in 64-bit `long` and then calls the
truncating `_emalloc`. `NOTES.md` §4 prices each stage; `controls/fix_scope.py`
measures them.

⭐ **The compiler does not remove it either, and the reason is PHP's own
allocator.** gcc injects `-D_FORTIFY_SOURCE=3` at `-O3` on this box and level 3
uses `__builtin_dynamic_object_size`, which tracks allocation sizes — the exact
check this row is about. It emits **no** `__memcpy_chk` in any of the eight
measured configurations, because `php_shim_emalloc`'s size-class cache gives
the returned pointer two provenances. `controls/fortify.py` isolates that with
a must-fire control. Unlike `ph16`, no rung here needs `#undef
_FORTIFY_SOURCE`.

The machine-readable contract follows. `harness-php/gate.py ph29-recvfrom-alloc`
enforces it; `README.md` is the reader's entry point and `NOTES.md` carries the
measurements.

```slb-contract
{
 "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
 "model": "model.py",
 "requires": [
  "off + len <= buf_len",
  "16 <= len"
 ],
 "ensures": [
  "result == recv_fold(buf, off, len)"
 ],
 "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (recv_fold). `recv_fold` is model.py's SECOND, independent implementation -- pure transitions driven to a fixpoint, mirroring verus.rs's `foldb` and `recv_win` one application at a time -- and not the simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic windows model.py builds itself, spanning every truncation boundary of `to_read` (0, +-1, 2^31, 2^32 - 1, 2^32, 2^33 - 1, LONG_MAX, LONG_MIN and the two values whose `real_size` is exactly 0 or 8), every `ctl` in 0..3, both sides of the size-class cache and five strides. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions because its corpus took one arm of a two-armed branch -- and here `inputs/` STRUCTURALLY CANNOT span the parameter, because a benign corpus may not contain a truncating window at all. A THIRD spelling -- `_dumb`, which materialises the destination buffer as a list and performs the copy and the NUL store into it -- checks every shipped window as well.",
 "idiom": {
  "required": [
   {
    "c": "`emalloc(to_read + 1)` -- THE REQUEST ITSELF, AND IT IS THIS ROW'S DEFINING IDIOM: a size is asked for, silently truncated by the allocator, and then used again as if it had been honoured. THIS ENTRY BINDS ALL SIX RUNGS -- the C span here on c/kernel.c:226 and c/kernel_hardened.c:160, one line each, and the Rust span beside it on all four Rust rungs -- because a rung that did not compute the request would be modelling a different bug and would not be this ladder. The C spelling is character-for-character streamsfuncs.c:321's, which is what the emalloc redirect itemised in provenance.divergences buys and what that entry's own why records. ⚠ THIS ENTRY CARRIED NO ENGLISH AT ALL UNTIL TASK_PHP_033 -- a bare span per language and nothing else. An entry with no English declares a spelling and says neither what it binds nor what it is required FOR, which is precisely the half required reserves to prose because no gate stage can decide it.",
    "rust": "`.wrapping_add(1)` -- THE SAME REQUEST, AND IT BINDS ALL FOUR RUST RUNGS. ⚠ RESPELLED AT TASK_PHP_033, AND THE SPAN IS SHORT FOR A REASON. All four Rust rungs compute the allocation request, so the entry must bind all four; but they do not spell the receiver alike -- safe_naive.rs:100 and safe_tuned.rs:64 write (to_read as u64).wrapping_add(1) while unsafe.rs:88 and verus.rs:450 write tr.wrapping_add(1). ⚠⚠ THOSE SPANS ARE WRITTEN HERE WITHOUT BACKTICKS ON PURPOSE: an entry that quotes what it is EXPLAINING acquires a second pin -- forbidden[0]'s own trap, arriving in the key where the polarity is the opposite -- and pinning the longer form would put the two safe rungs out of their own contract ON A VARIABLE NAME, which is p17's whitespace disaster in a new costume, where six cells fell out of contract on two space characters. The span above pins all four at exactly one line each (100 / 64 / 88 / 450) and nothing else; the closing paren is what keeps it off the fold constant .wrapping_add(1000039) two entries down. That was checked at LINE level and not merely at rung level, because idiom_audit's own docstring names substring matching as a real false-positive shape. ⚠ ONE IDIOM, TWO LANGUAGES, AND THE SPLIT IS COSMETIC HERE: unlike required[1] below, nothing about this entry is scoped -- every rung computes the request and every rung is pinned. The per-language keys exist because the two spellings share no token, which is the same reason required[2] and required[3] are per-language, and not because the fact differs across the languages."
   },
   {
    "c": "`read_buf[recvd] =` -- THE STORE THAT IS THIS ROW'S OWN FAULT LINE, pinned at c/kernel.c:247 and c/kernel_hardened.c:175, one line each: the fault line and its hardened twin, exactly. ⚠⚠ RESPELLED AT TASK_PHP_033, AND THE RULE IT YIELDS IS A WRITING RULE -- NEVER BACKTICK A CHARACTER LITERAL. This entry opened read_buf[recvd] = '\\0' -- written here WITHOUT BACKTICKS, for the reason the entry above gives -- and that spelling pins NOTHING. It is a MATCHER ARTEFACT and not a kernel defect: both C rungs really do spell that line, but check.py::exec_code layer 1 blanks comments and string/char literals before matching, so the matcher sees the statement with its literal erased. THE RULE: a declared spelling containing a character literal can never match. In required it merely reports pins nothing; in forbidden it is A BAN THAT CANNOT FIRE, and since TASK_068 forbidden_hits is the half that FAILS the gate -- a check that silently cannot fail, which is PROTOCOL_PHP.md H's exact target. ⚠ THIS IS NOT A BUG REPORT AGAINST harness/. The blanking is deliberate and documented in exec_code's own docstring, exec_code is hashed into all 33 PAT gate records, and no harness edit is proposed, wanted or permitted. ⚠⚠ AND THE BLIND SPOT IS LATENT, WHICH IS WHAT DECIDED THE RESPELLING RATHER THAN A REPORT: .temp/mgr169/charlit_reach.py measures 0 affected spellings across 33 PAT and 6 PHP rows, so backticking the literal form would have created the first one in either programme, on this row's own fault line.",
    "rust": "`vset_unchecked(&mut read_buf, recvd, 0)` -- ⚠⚠ SCOPED TO THE UNSAFE SIDE: R4 AND R5 ONLY, AND THE SCOPE IS THE WHOLE POINT OF THE ENTRY. This is the one line in this declaration where the rungs differ SEMANTICALLY and not cosmetically. The unsafe rungs store the terminating NUL through an UNCHECKED write (unsafe.rs:129, verus.rs:500); the two safe rungs perform the same store CHECKED, spelling it read_buf[recvd as usize] = 0 at safe_naive.rs:142 and safe_tuned.rs:97 -- WRITTEN WITHOUT BACKTICKS ON PURPOSE, so that this explanation does not become a second pin. There is no span the four Rust rungs share, and per-language keys cannot express the split because both spellings are Rust; so the entry names the unchecked spelling and says in English which rungs it binds, which is where required scope lives and the only place it can live. ⚠ SO EXPECT EXACTLY TWO SCOPED ABSENCES AGAINST THIS ENTRY -- safe_naive.rs and safe_tuned.rs, by construction. That is required_absent working rather than failing, and it is this row's entire required_absent count. ⭐ AND IT IS THE LADDER'S DIFFERENCE AT THIS LINE: the bounds check on that store is what R2 and R3 pay for and what R4 and R5 do not, which is why the idiom is stated as a required unchecked spelling on one side rather than as a forbidden checked one on the other. ⚠⚠ THIS ENTRY ALSO CARRIED NO ENGLISH AT ALL UNTIL TASK_PHP_033, and that mattered more here than on required[0]: a bare span that binds two of six rungs and says so nowhere leaves a reader two absences he cannot adjudicate, and required is given NO VERDICT by design precisely because that adjudication is prose. The absences were invisible before the backticks went on -- with zero pins the audit reported present 0 and required_absent 0, which reads like a clean row and was a row nothing was being checked against."
   },
   {
    "c": "`php_shim_tally()` -- THE ALLOCATOR'S BEHAVIOUR IS IN THE CHECKSUM, NOT ONLY IN A SANITIZER (PROTOCOL_PHP.md B1.2). The C rungs fold php_shim_tally(), whose fourth field is bytes_mallocked -- the sum of the TRUNCATED real_size, i.e. what reached malloc, and NOT bytes_requested. The four Rust rungs fold the same u64 computed arithmetically, and 1000039 is the mixing constant that multiplies bytes_mallocked, so a rung that folded the un-truncated request instead would not carry this token. On adversarial-trunc.bin that field is 0 while bytes_requested is 18446744069414584320, and the two are exactly the two sides of truncation T1. PER-LANGUAGE because the two spellings share no token and not because the fact differs.",
    "rust": "`1000039` -- THE ALLOCATOR'S BEHAVIOUR IS IN THE CHECKSUM, NOT ONLY IN A SANITIZER (PROTOCOL_PHP.md B1.2). The C rungs fold php_shim_tally(), whose fourth field is bytes_mallocked -- the sum of the TRUNCATED real_size, i.e. what reached malloc, and NOT bytes_requested. The four Rust rungs fold the same u64 computed arithmetically, and 1000039 is the mixing constant that multiplies bytes_mallocked, so a rung that folded the un-truncated request instead would not carry this token. On adversarial-trunc.bin that field is 0 while bytes_requested is 18446744069414584320, and the two are exactly the two sides of truncation T1. PER-LANGUAGE because the two spellings share no token and not because the fact differs."
   },
   {
    "c": "`php_shim_reset` -- PROTOCOL_PHP.md B1.3: one request per kernel call, so call N does not inherit call N-1's size-class cache and the marginal-Ir subtraction every number rests on survives. The C rungs call it at the top of the kernel; the Rust rungs have no cache to reset and instead name real_size, the quantity that reset makes a pure function of to_read. PER-LANGUAGE for the same reason as the entry above.",
    "rust": "`real_size` -- PROTOCOL_PHP.md B1.3: one request per kernel call, so call N does not inherit call N-1's size-class cache and the marginal-Ir subtraction every number rests on survives. The C rungs call it at the top of the kernel; the Rust rungs have no cache to reset and instead name real_size, the quantity that reset makes a pure function of to_read. PER-LANGUAGE for the same reason as the entry above."
   },
   "R1h IS THE WHOLE OF 445daac3ab1a (Ilia Alshanetsky, 2004-07-28, 'Fixed possible crash in stream_socket_recvfrom() when length parameter has a negative value'), ONE FILE AND FIVE LINES, and it is the corpus index's own fix_commit for CRASH-097. Verified AT THE COMMIT and not at the column (PROTOCOL_PHP.md F5(iii)): the patch bytes are under controls/445daac3ab1a.patch, 807 B, sha256 48ac72d125ac39d200271013d1743fd3a87113db444c0697113483cbf8c1c1c2, byte-identical to the copy the manager cached independently. IT IS NOT COMPLETE AND THE ROW SAYS SO IN ITS OWN HASHED BLOCK. Measured over the whole to_read domain, controls/fix_scope.py: the guard removes every fault with to_read < 0; it ALSO refuses to_read == 0, which was never a fault, so it is over-broad on the safe side; and it removes NOTHING in [1, LONG_MAX - 2], where 2147483647 distinct values still make to_read + 1 a multiple of 2^32 and truncate. THE SECOND UPSTREAM CHANGE IS CITED HERE TOO AND IS NOT SHIPPED: 6ac8ffdfea108696fe32b4738b779a00d2d4328c (Antony Dovgal, 2006-12-25, one line, emalloc(to_read + 1) -> safe_emalloc(1, to_read, 1), in the 5.2.0 -> 5.3.0 window; patch under controls/). Measured marginal effect over stage 1: it removes the signed-overflow UB in to_read + 1 and refuses exactly TWO further values, LONG_MAX - 1 and LONG_MAX; it removes ZERO truncation faults. So the two stages are NOT the same rung, and shipping both would price a checked multiply that buys nothing this row can observe. NOTES.md section 4 is the argument and controls/fix_scope.py is the measurement. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each C rung implements and no single token decides it. The mechanical checks are controls/negatives.py --emit noclamp, which must NOT verify, and controls/fix_scope.py.",
   "THE FOUR RUST RUNGS COMPUTE PHP'S OWN ALLOCATOR ARITHMETIC AND BOUND THE COPY BY IT, AND THAT IS WHAT MAKES R1..R5 DIFFER IN EXACTLY ONE THING. real_size is what _emalloc returns (zend_alloc.c:182), so a memory-safe translation binds the destination's length to it and clamps the receive; R1 hands the transport to_read instead, and the gap between the two IS the defect. THE ALTERNATIVE READING IS STATED SO A READER CAN DISAGREE: one could argue the safe port of emalloc(to_read + 1) is a Vec of to_read + 1 bytes, since Rust's allocator has no 32-bit truncation, and then safe Rust simply does not have the bug -- true, and unmeasurable, because it allocates 4 GiB per kernel call on the row's own trigger. NOTES.md section 6. A rung that allocated the UNTRUNCATED size would not be this ladder."
  ],
  "forbidden": [
   "the addition computed in anything wider than a long, or reordered. ⚠⚠ THIS ENTRY OPENED WITH THE EXPRESSION IN BACKTICKS AND THE GATE REFUSED THE ROW FOR IT -- twice, once per C rung -- WHICH IS THE EXACT TRAP ITS OWN LAST SENTENCE WARNS ABOUT. In a forbidden entry EVERY backticked span becomes a banned token, so an entry that quotes what it is PROTECTING bans that too, and c/kernel.c spells the protected thing because that is the point of protecting it. ph16's first draft lost fourteen (spelling x rung) obligations to the same shape; writing the warning into the entry did not stop me repeating it, which is worth more than the warning. The protected expression is streamsfuncs.c:321's, it is signed-overflow UB at LONG_MAX, that UB is PHP's and it is kept, and inputs/gen.py REFUSES to emit LONG_MAX so the measured corpus never evaluates it -- F46's UB-free-trigger strengthening applied to the whole corpus rather than to one input. NOTE THE ABSENCE OF BACKTICKS IN THIS ENTRY AND IN THE ONE BELOW IT -- and NOT in the two after that, which carry one banned token each and ARE audited. ⚠ THIS SENTENCE CLAIMED THIS ENTRY AND THE THREE BELOW UNTIL TASK_PHP_033 AND WAS FALSE ABOUT ITS OWN SCOPE: forbidden_unaudited_entries is 2 and not 4, and it has been 2 in every gate record this row has ever written, so the sentence contradicted an artefact printed three lines from it. Corrected in the same edit that backticked the required side, since the block was being rehashed for that anyway and the correction was therefore free.",
   "a capacity passed alongside the request. emalloc receives to_read + 1 and nothing that says how big the block it returns actually is; handing this kernel both numbers would be modelling a different bug and would delete the row.",
   "plain malloc, calloc or realloc in place of the shim. Under plain malloc this row's adversarial input is CLEAN -- measured both ways in controls/allocator.py -- so a substituted allocator does not weaken the row, it deletes it. This is the one row in the corpus where PLAN_PHP.md 4.3's warning is load-bearing rather than prudential. ⚠ THE ONE BACKTICKED TOKEN IN THIS ENTRY IS `calloc`, and it is safe to backtick BECAUSE NO RUNG SPELLS IT: it is the substitution, not the thing protected. The protected name is written without backticks two sentences up, for the reason forbidden[0] now records at length.",
   "an undef of the fortify level. ph16 needs one and this row does not: gcc emits no memcpy check here in any of the eight measured configurations, and controls/fortify.py measures that with a must-fire control rather than inheriting ph16's answer. A rung that added one would be suppressing a mitigation that is not there, and would make this row's own fortify finding unfalsifiable. ⚠ The banned token here is `#undef _FORTIFY_SOURCE`, spelled in backticks because it is what must NOT appear -- ph16's two C rungs both carry it and ph29's must not."
  ],
  "why": "ph29 is `PHP_FUNCTION(stream_socket_recvfrom)` out of PHP 5.0.0, `ext/standard/streamsfuncs.c:300-345`, corpus row CRASH-097, tier `narrowed`. THE IDIOM IS A SIZE THAT IS ASKED FOR, SILENTLY TRUNCATED BY THE ALLOCATOR, AND THEN USED AGAIN AS IF IT HAD BEEN HONOURED. `:321` is `read_buf = emalloc(to_read + 1);` where `to_read` is a `long` that `zend_parse_parameters` took from USERLAND at `:309`; `Zend/zend_alloc.c:129` declares `unsigned int real_size` and `:135` assigns `REAL_SIZE(size)` into it, so `:182` allocates `header + real_size` and hands back a block of `real_size` bytes. `:323` then calls `php_stream_xport_recvfrom(stream, read_buf, to_read, ...)` -- with `to_read`, the number it ASKED for -- and `:332` writes `read_buf[recvd]`. NOTHING IN PHP EVER COMPARES THE TWO. ⭐ THE ROW EXISTS TO TEST `common-php/emalloc_shim.h` AND IT CANNOT PASS WITHOUT IT: under plain `malloc` the defect disappears in two different ways and both are measured in `controls/allocator.py` -- `malloc(2^64 - 2^32)` FAILS, so PHP prints and `exit(1)`s at `zend_alloc.c:189`, while `malloc(2^32)` SUCCEEDS with a real 4 GiB block and the write is in bounds. `PLAN_PHP.md` §4.3 records that a substituted allocator once made a real defect look unreachable; this is the row where that warning is tested by something that fails without it. ⚠⚠ R1h IS `445daac3ab1a` AND IT DOES NOT REMOVE THE DEFECT. The guard it adds is `if (to_read <= 0) RETURN_FALSE;` -- exactly what its own subject says, *\"when length parameter has a negative value\"* -- and `stream_socket_recvfrom($s, 4294967295)` is positive. The second upstream change, `6ac8ffdfea10`, does not remove it either, because `_safe_emalloc` checks in 64-bit `long` and then calls the truncating `_emalloc` at `zend_alloc.c:238`. `controls/fix_scope.py` prices both, separately and together, over the whole `to_read` domain. ⚠ SO THE SHIPPED ADVERSARIAL INPUTS ARE THE ARM THE FIX DOES CLOSE (`to_read < 0`), because `check.py` stage 7h requires R1h to be clean on every input; the arm it does not close is in `controls/`, which is where `.memory-php/02-ladder.md` F31 says that evidence belongs. ⭐ AND THE COMPILER DOES NOT CLOSE IT EITHER. Ubuntu's gcc injects `-D_FORTIFY_SOURCE=3` at `-O3` and level 3 uses `__builtin_dynamic_object_size`, which tracks allocation sizes -- exactly the check this row is about. It emits NO `__memcpy_chk` here, in any of the eight (compiler × opt × mode) configurations. `controls/fortify.py` isolates why, with must-fire controls: `php_shim_emalloc`'s SIZE-CLASS CACHE gives the returned pointer TWO PROVENANCES and `__bdos` of that PHI is unknown, so PHP 5.0.0's own allocator feature defeats a 2024 compiler mitigation. ⚠ Unlike `ph16`, no rung here needs `#undef _FORTIFY_SOURCE`, and that is MEASURED rather than inherited (F56 says explicitly not to inherit it). NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
 },
 "verus": {
  "call_site": "main",
  "kernel_item": "kernel",
  "translate": {
   "buf@.len()": "buf_len",
   "buf@": "buf",
   " as int": "",
   "recv_fold": "recv_fold",
   "r": "result"
  },
  "obligations": {
   "verus.rs": 10
  },
  "twin_obligations": {
   "verus.rs": 15
  },
  "obligations_note": "10 verified / 0 errors, and 15 under `--cfg slb_twin` -- four trusted accessors, therefore four twins, and `slb_twin_vcopy_unchecked` carries a loop of its own so the twin build gains five obligations rather than four. ⭐ WHAT THE PROOF RESTS ON IS A BOUND BETWEEN TWO DERIVED QUANTITIES, NOT AN INDEX AGAINST A CONSTANT, and that is this row's difference from ph16: `cap` is `rs_of(tr + 1)`, a 32-bit truncation of the number the program asked for, and every unchecked destination access is licensed by `n <= cap`. `lemma_foldb_ext` is the file's only lemma and it exists because the fold reads the DESTINATION while the spec folds the WINDOW; the copy's `ensures` is what makes the two agree over exactly the range folded.",
  "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 10 shipped + 5 for slb_twin_get_unchecked, slb_twin_vget_unchecked, slb_twin_vset_unchecked and slb_twin_vcopy_unchecked (whose loop is an obligation of its own, which is why the twin build gains five and not four). ⚠⚠ THERE IS NO `#[verifier::rlimit]` ON THIS ROW, AND THAT IS A MEASUREMENT RATHER THAN AN OVERSIGHT: ph16 needs 30 and ph07 needs 9, and this file verifies with the attribute DELETED and at rlimit(1), in BOTH builds. Bisected at 30 / 10 / 4 / 2 / 1 / none -- every one `10 verified, 0 errors` plain and `15 verified, 0 errors` twin (NOTES.md section 10b). ⭐ The row shipped WITH `rlimit(30)` in its first draft, by analogy with ph16, and the analogy was wrong; an unearned budget override is a claim about proof cost and this row's actual claim is the opposite one.",
  "items": {
   "verus.rs": {
    "tr_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "ctl_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "want_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "rs_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "rec_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "tally_of": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "foldb": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "lemma_foldb_ext": {
     "external": null,
     "requires": [
      "0 <= i <= n",
      "forall|j: int| #![trigger a[ba + j]] i <= j < n ==> a[ba + j] == b[bb + j]"
     ],
     "ensures": [
      "foldb(a, ba, i, n, acc) == foldb(b, bb, i, n, acc)"
     ]
    },
    "min3": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "recv_win": {
     "external": null,
     "requires": [],
     "ensures": []
    },
    "recv_fold": {
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
    "vget_unchecked": {
     "external": "verifier::external_body",
     "requires": [
      "i < v@.len()"
     ],
     "ensures": [
      "r == v@[i as int]"
     ]
    },
    "slb_twin_vget_unchecked": {
     "external": null,
     "requires": [
      "i < v@.len()"
     ],
     "ensures": [
      "r == v@[i as int]"
     ]
    },
    "vset_unchecked": {
     "external": "verifier::external_body",
     "requires": [
      "i < old(v)@.len()"
     ],
     "ensures": [
      "final(v)@ == old(v)@.update(i as int, x)"
     ]
    },
    "slb_twin_vset_unchecked": {
     "external": null,
     "requires": [
      "i < old(v)@.len()"
     ],
     "ensures": [
      "final(v)@ == old(v)@.update(i as int, x)"
     ]
    },
    "vcopy_unchecked": {
     "external": "verifier::external_body",
     "requires": [
      "n <= old(v)@.len()",
      "from + n <= s@.len()"
     ],
     "ensures": [
      "final(v)@.len() == old(v)@.len()",
      "forall|j: int| 0 <= j < n ==> final(v)@[j] == s@[from + j]"
     ]
    },
    "slb_twin_vcopy_unchecked": {
     "external": null,
     "requires": [
      "n <= old(v)@.len()",
      "from + n <= s@.len()"
     ],
     "ensures": [
      "final(v)@.len() == old(v)@.len()",
      "forall|j: int| 0 <= j < n ==> final(v)@[j] == s@[from + j]"
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
    "kernel": {
     "external": null,
     "requires": [
      "off + len <= buf@.len()",
      "16 <= len"
     ],
     "ensures": [
      "r == recv_fold(buf@, off as int, len as int)"
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
    "vcopy_unchecked": "THE RECEIVE, and the one place this row's obligation is actually discharged. `core::ptr::copy_nonoverlapping(s.as_ptr().add(from), v.as_mut_ptr(), n)` is defined iff `from + n <= s.len()` and `n <= v.len()`, and iff the two regions do not overlap -- which holds because `v` is a freshly allocated Vec and `s` is a subslice of the input blob. Both length conditions are the `requires`. `n <= v@.len()` is EXACTLY the comparison PHP 5.0.0 does not make: `streamsfuncs.c:323` passes `to_read` where the block is `real_size` bytes. ⚠⚠ THE `ensures` HAD A THIRD CLAUSE AND THE GATE DELETED IT. It said `forall|j| n <= j < old(v)@.len() ==> final(v)@[j] == old(v)@[j]` -- the suffix is untouched -- with a comment claiming it was what kept the NUL store honest. `check.py` stage 5b's clause deletion showed the file still gives `10 verified, 0 errors` without it, because nothing in this kernel reads past `recvd`. A trusted item's `ensures` is an AXIOM; one nothing depends on is an unchecked claim about real Rust semantics carried for free. It is gone. ⚠ What the two surviving clauses do NOT exclude is a body that also scribbles past `n` -- that would be UB without moving anything the proof reads, and `identity: exact` plus Miri are what cover it. NOTES.md's SLB-TRUSTED-ARGUMENT section for this item says so in the form the gate requires.",
    "vset_unchecked": "`streamsfuncs.c:332`'s `read_buf[recvd] = '\\0'`. `x: u8` is a PURE VALUE and needs no precondition; the unchecked operation's definedness depends on `i` being in bounds and on nothing about the byte written. The `ensures` names the WHOLE new state, `old(v)@.update(i, x)`, not just `v@[i] == x`: an `ensures` naming only the written element would let a body that also clobbered `v[i + 1]` through, which `.memory/04-verus.md` records as the most dangerous vacuity mode.",
    "vget_unchecked": "the read-back at `:340`, `RETURN_STRINGL(read_buf, recvd, 0)`. `v: &Vec<u8>` is a shared reference, so the only thing that can be wrong is the index; `i < v@.len()` is the whole precondition and `r == v@[i as int]` the whole postcondition. ⚠ THIS IS THE SECOND LIMB OF THE DEFECT AND NOT A CONVENIENCE: in R1 the same read runs off the end of the block, because the zval takes a string of length `recvd` over a buffer that is not that long.",
    "get_unchecked": "the window reads -- the eight bytes of `to_read`, the two control words and the datagram. Licensed by a fact that is not in PHP at all: the driver's `off + len <= buf@.len()` and `16 <= len`, plus `navail = want % (n_pay + 1)`, which bounds the payload index by construction rather than by a check. Keeping this class apart from the destination class is the point -- they rest on independent facts, one from the harness and one from `Zend/zend_alloc.c`."
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
  "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph29's two probe shapes have different work per call (550 and 4076 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW, and what the kernel actually touches is `navail = want % (n_pay + 1)` bytes copied plus `recvd` folded plus a `real_size` allocation -- inputs/gen.py draws BOTH `navail` and `to_read` relative to `n_pay = stride - 12`, so all three scale with the denominator rather than merely being labelled by it. ⚠⚠ THERE IS ALSO A FIXED PER-CALL TERM AND IT IS AN ALLOCATOR TERM: one php_shim_reset (which walks 11 cache classes), one _emalloc, one _efree and one php_shim_shutdown (which walks them again plus the live list) happen on every call whatever the stride. So the marginal is NOT a pure copy rate and NOTES.md §8 decomposes it rather than presenting it as one."
 },
 "identity": [
  {
   "a": "unsafe",
   "b": "verus",
   "O0": "norel",
   "O3": "exact",
   "why": "R4 == R5 at O3 EXACTLY -- `md5_fn` a7adc5d4e32f in BOTH cells, 182 instructions and 671 bytes each, measured against the SHIPPED record (results-php/ph29-recvfrom-alloc.json, O3/isolated). The proof licenses all four unchecked classes at ZERO instructions. ⚠⚠ THIS ENTRY FIRST SAID `norel` AT O3, on the reasoning that `vec![0u8; cap]` reaches the global allocator through a PLT entry so the two cells must differ in relocation bytes. THE MEASUREMENT SAYS `exact`: the relocations are identical too, because both rungs emit the same call to the same symbol at the same offset. `PROTOCOL.md` rule 6's addendum is exactly this -- a frozen declaration is evidence about WHEN it was written, not about whether it is still true -- and NOTES.md §12 is the pass that caught it. ⚠ AT O0 THE TWO DIFFER ONLY IN RELOCATIONS, which is why this row says `norel` and not `differ`: 406 instructions and 2354 bytes in BOTH, `md5_fn_norel` 1d07d74ab74e in BOTH, and `md5_fn` 2a8f2758f4db vs 21f7fa2d2dd6. ⭐ THAT IS A DIFFERENT ANSWER FROM ph03, ph07 AND ph16, all of which record `differ` at O0 because R5's trusted wrappers survive as real calls where R4's `#[inline(always)]` helpers do not. Here they survive in BOTH, because this kernel's helpers are called from inside a loop rather than inlined at one site, so the instruction streams match and only the symbol names behind the relocations move."
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
  "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph29 has FOUR such items and TWO of them WRITE (`vset_unchecked` and `vcopy_unchecked`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a bulk-copy wrapper whose `ensures` named only the copied prefix would let a body that also scribbled over the tail through every Verus stage. The shipped `ensures` names the whole post-state in three clauses -- length preserved, prefix copied, suffix untouched -- and Miri is the backstop for the class regardless. ⭐ IT MATTERS MORE HERE THAN ON `ph16`, because `vcopy_unchecked` is a raw `copy_nonoverlapping` through two `as_ptr` calls: it is the one place in this row where a provenance or aliasing error would be invisible to both the type system and the proof.",
  "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph29's cost is 4 x (one allocation, one copy of at most 4 064 bytes and one fold of the same) -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
 },
 "provenance": {
  "php_version": "5.0.0",
  "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
  "c_file": "ext/standard/streamsfuncs.c",
  "c_lines": [
   300,
   345
  ],
  "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/standard/streamsfuncs.c | sed -n '300,345p'",
  "extract_sha256": "b1d9da603abb3423003f15b00f274fd806566570c6cc56e0cd2e9172e536cb6f",
  "extra_spans": [
   {
    "c_file": "main/streams/transports.c",
    "c_lines": [
     381,
     392
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/main/streams/transports.c | sed -n '381,392p'",
    "extract_sha256": "24d45e6a3409c2d73ecf471b9b380c55ff447cfb6a7d711c28164de4163015c1",
    "why": "⚠⚠ WHAT `:323` ACTUALLY CALLS, AND IT DECIDES HOW MANY BYTES ARE WRITTEN. `php_stream_xport_recvfrom`'s `buflen` is a `size_t`, so `to_read` widens into it unchanged; and with `flags == 0 && addr == NULL` -- which is the arm `stream_socket_recvfrom($s, $n)` takes, because `:323` passes `NULL, NULL` for addr/addrlen -- the whole function is `return php_stream_read(stream, buf, buflen);` at `:391`. So the transport writes min(available, to_read) bytes into a block of `real_size`, which is what `ph29_stream_read` in `c/kernel.c` is. Without this span the row would be citing a call whose length parameter's TYPE is the thing that carries the defect across the frame boundary, and not showing it."
   },
   {
    "c_file": "Zend/zend_alloc.c",
    "c_lines": [
     128,
     137
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_alloc.c | sed -n '128,137p'",
    "extract_sha256": "c33f1b65573dd18dadf1108390da4f793296dd62a664be12280e274bf4bdd621",
    "why": "⚠⚠⚠ TRUNCATION T1 ITSELF, AND IT IS NOT IN `c/kernel.c` -- IT IS IN `c/emalloc_shim.h`, which every row symlinks and which this row is the first to depend on. `DECLARE_CACHE_VARS()` at `:128-130` declares `unsigned int real_size`; `:132` is `#define REAL_SIZE(size) ((size+7) & ~0x7)`, done in `size_t`; `CALCULATE_REAL_SIZE_AND_CACHE_INDEX` at `:134-136` assigns the one into the other. THE STORE IS THE TRUNCATION, not the macro -- the manager hypothesised it was at `emalloc`'s signature and was wrong (F36, retracted by F46). Cited here because the row's `why`, its `idiom` and its whole admission rest on these ten lines, and `extract_sha256` is what makes 'those lines of that tarball hash to this' a one-command check rather than a claim. ⚠ The kernel-overlap statistic reads only `c/kernel*.{c,h}`, so this span contributes nothing to it and is not meant to."
   }
  ],
  "extra_spans_note": "THE ROW LIFTS ONE SPAN AND CITES TWO MORE, AND ALL THREE ARE PINNED. `provenance.c_lines` names the defect site (streamsfuncs.c:300-345, PHP_FUNCTION(stream_socket_recvfrom)); extra_spans[0] names the callee that decides how much is written (transports.c:381-392); extra_spans[1] names the truncation itself, which lives in the allocator and reaches the row through the c/emalloc_shim.h symlink rather than through c/kernel.c. ⚠ `.memory-php/01-extraction.md` says the DEFECT site, the GUARD site and the FAULTING site can be three different places; on this row they are streamsfuncs.c:321, streamsfuncs.c (nowhere in 5.0.0 -- the guard arrives in 5.1.0) and streamsfuncs.c:323/:332, and there is a FOURTH -- zend_alloc.c:135 -- which is where the quantity actually goes wrong.",
  "tier": "narrowed",
  "divergences": [
   {
    "what": "TSRMLS_CC",
    "kind": "deletion",
    "where": "streamsfuncs.c:309, :326",
    "why": "thread plumbing, no semantics"
   },
   {
    "what": "emalloc / efree -> php_shim_emalloc / php_shim_efree",
    "kind": "substitution",
    "where": "streamsfuncs.c:321, and the zval destructor's efree",
    "why": "a `#define` REDIRECT in c/kernel.c and c/kernel_hardened.c, which is ph03's own sanctioned spelling for this (PROTOCOL_PHP.md A1: a substitution is admissible when it is itemised, given a `why` that ends in 'no semantics', and DEMONSTRATED behaviour-preserving rather than asserted). common-php/emalloc_shim.h transcribes _emalloc (zend_alloc.c:142-217) and _efree (:248-289) line for line against the pristine tarball, so this is a RENAME. ⚠⚠ IT IS ALSO WHAT MAKES `read_buf = emalloc(to_read + 1);` -- the row's own defect line -- CHARACTER-FOR-CHARACTER upstream's, and `long to_read = 0;` likewise. Before the redirect the kernel spelled the allocation `(char *)php_shim_emalloc((size_t)(to_read + 1))` and provenance.py's overlap heuristic scored THE DEFECT LINE ITSELF as a miss: 9% (4/43), rising to 14% (6/43) after, with the two shipped benign checksums BYTE-IDENTICAL across the change (5917653902369662825 and 3996271157387841948). The differential is controls/oracle.py (1920 of 1920 cells agree, with a must-fire control) and controls/allocator.py (18 of 18, both directions). No semantics."
   },
   {
    "what": "zend_parse_parameters(..., \"rl|lz\", &zstream, &to_read, &flags, &zremote)",
    "kind": "deletion",
    "where": "streamsfuncs.c:309",
    "why": "argument parsing -- the wrapper PROTOCOL_PHP.md A1 names as the whole content of tier `narrowed`. The eight bytes of the window's head are what it yields; on a 64-bit build \"l\" produces a full `long` (Zend/zend_API.c's `case 'l': convert_to_long_ex(arg)`). The parse is HOW the value arrives, not WHAT is wrong with it, and it is itself correct. No semantics."
   },
   {
    "what": "php_stream_from_zval(stream, &zstream)",
    "kind": "deletion",
    "where": "streamsfuncs.c:313",
    "why": "zval unpacking; the stream is the window's payload bytes. No semantics."
   },
   {
    "what": "zval_dtor / ZVAL_NULL / Z_STRLEN_P(zremote) = 0",
    "kind": "substitution",
    "where": "streamsfuncs.c:316-318",
    "why": "the zval triple becomes a `ctl` bit and a scalar. Both arms of `if (zremote)` are KEPT and inputs/gen.py asserts the corpus reaches both. No semantics."
   },
   {
    "what": "Z_TYPE_P(zremote) = IS_STRING",
    "kind": "substitution",
    "where": "streamsfuncs.c:330",
    "why": "becomes a folded flag, so the `:329` arm stays observable in the u64. No semantics."
   },
   {
    "what": "php_stream_xport_recvfrom -> ph29_stream_read",
    "kind": "substitution",
    "where": "streamsfuncs.c:323",
    "why": "the transport's flags==0 && addr==NULL arm is `return php_stream_read(stream, buf, buflen);` (transports.c:390-392) and the socket is a blob, so the stand-in copies min(navail, buflen) bytes and returns the count as an `int`. `buflen` stays the `size_t` widening of `to_read`, which is the only thing about this call the defect uses. extra_spans[0] pins the original. No semantics."
   },
   {
    "what": "if (PG(magic_quotes_runtime)) { ... }",
    "kind": "deletion",
    "where": "streamsfuncs.c:334-338",
    "why": "a php.ini setting, not attacker data, whose shipped 5.0.0 default is 0, so the measured arm is the `else` at :339-341. ⚠ Keeping it would ADD a second defect this row is not about -- that arm addslashes Z_STRVAL_P(return_value), which nothing has set. No semantics for this row's defect."
   },
   {
    "what": "RETURN_STRINGL(read_buf, recvd, 0)",
    "kind": "substitution",
    "where": "streamsfuncs.c:340",
    "why": "becomes the fold over read_buf[0 .. recvd). The `0` is duplicate=0, i.e. the engine takes ownership and its zval destructor efrees the block later; that is the php_shim_efree in the kernel. The READ of `recvd` bytes is kept because it is the second limb of the defect. No semantics."
   },
   {
    "what": "the request boundary -- php_shim_shutdown() per kernel call",
    "kind": "projection",
    "where": "zend_alloc.c:469-569",
    "why": "PHP runs shutdown_memory_manager once per REQUEST; the kernel runs it once per CALL, because the driver loop's 25 000 iterations are one request each. It is what reclaims the block the `RETURN_FALSE` arm at :344 LEAKS (5.0.0 does not efree it there), so without it the loop would be bounded by RSS rather than by instruction count -- the hazard emalloc_shim.h names for a leaking row. The leak arm itself is reproduced, not repaired."
   },
   {
    "what": "the emalloc NULL arm",
    "kind": "projection",
    "where": "zend_alloc.c:189-198",
    "why": "PHP prints to stderr and exit(1)s; a kernel must not exit or the driver reports a build failure instead of a measurement, so php_shim_emalloc returns NULL and the kernel returns the sentinel PH29_EALLOC. ⚠ It is UNREACHABLE on the measured corpus -- inputs/gen.py refuses any window whose real_size exceeds 65536 -- and that is asserted rather than assumed. This is the same projection ph03 declares."
   },
   {
    "what": "php_shim_recorded_size(read_buf) folded into the u64",
    "kind": "projection",
    "where": "zend_alloc.h:53",
    "why": "not part of PHP's control flow: it is the block's own 31-bit recorded size, truncation T2, which _efree recomputes its cache class from at zend_alloc.c:263. It is folded so that the SECOND truncation is observable in the checksum and not only in a debugger, and because it moves when T1 does but with a different modulus."
   }
  ],
  "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⚠ TWELVE entries, of which four are deletions, five substitutions and three projections -- so the block's old name `deletions` would have described a third of it, which is why TASK_PHP_015 renamed it. ⚠⚠ PROTOCOL_PHP.md A1's clause (c) demands a DIFFERENTIAL for any substitution claimed to be behaviour-preserving. There are TWO substantive ones -- the transport stand-in and the emalloc/efree redirect -- and controls/oracle.py is the differential for both: it drives the shipped kernel and a from-source re-derivation over a to_read x navail grid the corpus does not span.",
  "root_cause_ids": [
   "stream_socket_recvfrom-emalloc-to_read-plus-1-truncated-by-REAL_SIZE-heap-overflow"
  ],
  "cwe": "CWE-787",
  "cwe_note": "index.csv records CWE-787 (out-of-bounds write) and the write is the primary limb: the receive at :323 and the NUL at :332 both land past a block of `real_size` bytes. ⚠ THERE IS A SECOND, READ limb and the row does not hide it: RETURN_STRINGL at :340 hands the engine a string of length `recvd` over the same block, so R1 reads what it just wrote out of bounds. That is ph03's shape rather than ph16's, and NOTES.md §5 keeps the two apart because R1h closes NEITHER of them at the row's own trigger.",
  "fix_commit": "445daac3ab1aa26ad95f9c75177f1ae604f75d1d",
  "fix_commit_note": "⚠ THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE for CRASH-097 and the row uses its short form everywhere. `445daac3ab1a` -- Ilia Alshanetsky, 2004-07-28, 'Fixed possible crash in stream_socket_recvfrom() when length parameter has a negative value' -- 1 file, +5 lines, and the patch is under controls/. ⭐ UNLIKE ph12 AND ph21 THE COLUMN IS RIGHT HERE: the commit lands in the 5.0.0 -> 5.1.0 window the tag bisect predicted (UPSTREAM_001.md §4), it is in the row's own file and function, and it is the only commit in the reachable history of ext/standard/streamsfuncs.c that introduces the guard. ⚠⚠ RIGHT IS NOT THE SAME AS COMPLETE: it does not remove this row's defect at to_read = 4294967295, and neither does the second change 6ac8ffdfea108696fe32b4738b779a00d2d4328c. Both patches are under controls/ and controls/fix_scope.py prices them separately and together.",
  "invariant": "I11",
  "obligation": "O2",
  "echoes": [
   "p25"
  ],
  "echoes_note": "p25-realloc-growth is the closest PAT analogue -- a size computation whose result is used as if it had been honoured -- and PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and never a filter. ⚠ The mechanisms differ in the thing that matters: p25's growth arithmetic is IN the kernel, where ph29's truncation is inside the allocator and invisible to the caller by construction. CATALOGUE.md's own `echoes` cell for ph29 is empty; this entry is the row's, and it is offered as a pointer rather than as a claim of equivalence.",
  "uses_allocator": true,
  "uses_allocator_why": "⚠⚠⚠ TRUE, AND THIS IS THE ROW WHERE IT IS LOAD-BEARING RATHER THAN INCIDENTAL. The C rungs call php_shim_emalloc / php_shim_efree / php_shim_reset / php_shim_shutdown / php_shim_recorded_size / php_shim_tally from c/emalloc_shim.h, and under plain malloc the adversarial input is CLEAN -- measured both ways in controls/allocator.py. The four Rust rungs do NOT call the shim: they compute the same allocator arithmetic explicitly (rs_of / rec_of / tally_of) and allocate a Vec of real_size bytes, which is exactly what _emalloc returns. ⚠ uses_allocator is a DECLARED answer to a question no detector asks any more (PROTOCOL_PHP.md B2); nothing depends on it being right, and the c/emalloc_shim.h symlink is unconditional whatever it says."
 }
}
```
