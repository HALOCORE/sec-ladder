# ph97 — the optional argument the parser never writes

**PHP 5.0.0, `ext/mbstring/mbstring.c:3209-3252`, corpus row CRASH-126, tier
`narrowed`.** `PHP_FUNCTION(mb_get_info)` initialises `char *typ = NULL` at
`:3211`, parses its arguments against the spec `"|s"` at `:3215`, tests the
result for FAILURE — and then hands `typ` straight to `strcasecmp` at `:3219`.
The `|` is the spec's FIRST character, so `zend_API.c:486` sets `min_num_args`
from a `max_num_args` that is still **zero**; the count test at `:511` admits a
call with no arguments; the write loop at `:537` runs **zero times**; and
`:548` returns **SUCCESS** having written nothing.

⭐⭐ **THE GUARD IS PRESENT AND IT PASSES, AND IT ANSWERS A DIFFERENT QUESTION
FROM THE ONE THE CODE NEEDS ANSWERED.** `:3215` tests *were the supplied
arguments well-typed?*; `:3219` needs *was the optional argument supplied?*.
The real test is `ZEND_NUM_ARGS()` or `typ != NULL`, and upstream wrote the
second of those four months later.

⭐⭐⭐ **AND CRITERION 2 IS MEASURED ON THIS ROW.** A PHP 5.0.0 CLI on this box,
under the committed `LD_PRELOAD` shim `.tasks-php/probes/segaddr.c`:

```
mb_get_info()                    -> SIG11 si_code=1 si_addr=(nil)   exit 139
mb_get_info("internal_encoding") -> string(10) "ISO-8859-1"         exit 0
```

Same binary, same run. ⚠ Two cautions travel with that and `NOTES.md` §1
repeats them: the binary is php-in-safe-rust's **oracle build**, not a
museum-default one, and a clean run would not have been evidence of absence.
`c/kernel.c` reproduces the same `si_addr=(nil)` from the same shim, and ASan
independently reports `SEGV on unknown address 0x000000000000` in
`ph97_strcasecmp`.

⚠ **The null VALUE and the absent ARGUMENT are different states.** `"|s"`
carries no `!`, so `zend_API.c:302-308`'s `IS_NULL` arm falls through to
`convert_to_string_ex` and a supplied `null` becomes the **empty string**:
`mb_get_info(null)` answers `bool(false)` on the same CLI. Only the *absent*
argument faults. `NOTES.md` §1.

**R1h is `f7326d627962`** (Antony Dovgal, 2005-01-28, *"MFB: fix #31732"*) —
one file, one hunk, **one line**, and `git apply` places it at offset −13.
⭐ It **widens** the benign domain: with the argument absent the patched build
answers with the four-element array where the unpatched one faults, so the only
input whose answer moves is one that previously crashed. `NOTES.md` §5.

The machine-readable contract follows.
`harness-php/gate.py ph97-optarg-unwritten` enforces it; `README.md` is the
reader's entry point and `NOTES.md` carries the measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len"
  ],
  "ensures": [
    "result == ph97_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (ph97_fold). `ph97_fold` is model.py's SECOND, independent implementation -- a RECURSIVE walk with no cursor variable and no window table, mirroring verus.rs's `s_run` / `s_step` / `s_cmp` / `s_fold_str` one unfolding at a time -- and not the imperative `_window` simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic records model.py builds itself, spanning the whole (argument-count x type-tag) cross product, every selector in five casings, every one-character mutation of the first selector, the whole length domain, an embedded NUL at every position, and seven degenerate strides. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. A THIRD spelling, `_dumb`, decides the selector by DICT LOOKUP on the decoded, case-folded, NUL-truncated argument instead of walking the five-arm compare chain -- the one spelling that cannot share a chain-order mistake with the other two, and chain order is load-bearing here because upstream tries the four-element arm first.",
  "idiom": {
    "required": [
      {
        "c": "`b[0] % 3u` and `b[1] % 4u` -- the record's argument COUNT and its argument TYPE, decoded from TWO SEPARATE BYTES. The first is ZEND_NUM_ARGS() at mbstring.c:3215 and the second is Z_TYPE_PP(arg) at zend_API.c:301, and they answer two different questions: *was an argument supplied?* and *is it well-typed?*. The guard at :3215 answers the second; the dereference at :3219 needs the first. A kernel that derived either from the other -- a type tag meaningful only when the count is non-zero, say -- would have deleted the mechanism before a single rung was measured, and the row would be modelling an ordinary missing NULL check. inputs/gen.py asserts the corpus reaches every combination and model.py's synthetic sweep drives the whole three-by-four cross product.",
        "rust": "`sget(b, 0) % 3` and `sget(b, 1) % 4` -- the record's argument COUNT and its argument TYPE, decoded from TWO SEPARATE BYTES. The first is ZEND_NUM_ARGS() at mbstring.c:3215 and the second is Z_TYPE_PP(arg) at zend_API.c:301, and they answer two different questions: *was an argument supplied?* and *is it well-typed?*. A rung that derived either from the other would have deleted the mechanism and would be modelling an ordinary missing NULL check."
      },
      "`min_num_args = max_num_args` -- zend_API.c:486, and this ONE ASSIGNMENT IS THE DEFECT. It runs when the scanner meets the optional marker, and in mb_get_info's spec the marker is the FIRST character, so the running maximum is still ZERO when it runs and the minimum becomes zero. Everything else follows mechanically: the count test at :511 admits a call with no arguments, the write loop at :537 runs zero times, and :548 returns SUCCESS with nothing written. ONE BACKTICKED SPELLING, and it covers BOTH LANGUAGES -- every rung writes those three tokens identically, which is itself part of the point: the mechanism is not a language artefact. verus.rs states the same fact a second time as a LOOP INVARIANT, in the form that after one character of the spec the minimum is zero while the maximum still is, which is what Z3 checks and a reader can read in three lines.",
      {
        "c": "`num_args < min_num_args || num_args > max_num_args` -- zend_API.c:511, THE GUARD, and it is PRESENT AND IT PASSES. With a minimum of zero and a maximum of one it refuses two arguments and admits none, so the RETURN_FALSE at mbstring.c:3216 is a reachable benign outcome and the faulting call is not. A kernel whose guard could never fail would have no guard at all and the row's claim -- *the test is there and it answers a different question* -- would be untestable. The adversarial input named in NOTES.md section 9 is the one that makes this arm fire, and inputs/gen.py refuses a measured corpus that never reaches it.",
        "rust": "`(num_args as i32) < min_num_args || (num_args as i32) > max_num_args` -- zend_API.c:511, THE GUARD, present and passing. With a minimum of zero and a maximum of one it refuses two arguments and admits none. The casts are upstream's types: the caller's count and the two bounds are C ints and the comparison is signed. A rung whose guard could never fail would have no guard at all."
      },
      {
        "c": "`ph97_strcasecmp(ph97_sels[0], typ)` -- mbstring.c:3219, THE DEREFERENCE, and there is nothing between it and the guard above: no NULL test, no second look at the argument count, no question put to the parser about which out-parameters it wrote. The pointer is the caller's own :3211 initialiser whenever the optional argument was absent. Testing it here IS the 2005 fix and is what the hardened C rung does; adding it to the vulnerable one would delete the row. The spelling is shared by BOTH C rungs on purpose, because the hardened rung differs from this one by a disjunct in FRONT of this call and not by this call.",
        "rust": "`strcasecmp(sel_get(0), opt_get(typ))` -- mbstring.c:3219, THE DEREFERENCE. In Rust the parser's output cannot be read without being opened, so the call goes through an accessor; WHICH accessor is the R3-to-R4 lever and is deliberately not pinned here. What IS pinned is that the compare's second operand is the parser's output, unmediated by any test of its own."
      },
      {
        "c": "`PH97_LOWER((uint8_t) *b)` -- the second operand's FIRST BYTE, read with nothing in front of it, and the exact expression a PHP 5.0.0 CLI faults on. The faulting address is zero rather than an offset because there is no struct field to add: the compare reads byte zero. The compare is implemented HERE rather than called out to libc, and that is a MEASUREMENT decision as much as a fidelity one -- family A1 is symbol-scoped and structurally excludes callee work, so a kernel whose whole computation sat inside libc would read approximately zero in the statistic this programme publishes. spec.md's divergence ledger itemises the substitution and controls/libc_compare.py prices it with a must-fire control.",
        "rust": "the compare's per-byte read, and it is PER RUNG because the R3-to-R4 lever IS this expression: safe_naive.rs and safe_tuned.rs read the two operands with checked operations and unsafe.rs and verus.rs read them through the row's trusted frame accessor. Both are the same operation on the same array; one checks and one does not, and the loop's own upper bound is what licenses the one that does not. NO BACKTICKED SPELLING ON THIS SIDE AT ALL, deliberately: a pin here would name a spelling half the Rust rungs cannot carry, which is the shape that put twenty obligations out of contract at TASK_018."
      },
      {
        "c": "`typ = (const char *) 0` -- mbstring.c:3211, the function's own initialiser, and the reason the faulting pointer is the CALLER's and not a callee's. It is what makes this a *the guard answers the wrong question* row rather than a *the callee returned NULL and nobody looked* row: nothing fails, nothing returns NULL, and the pointer that reaches the compare was written by this function's first line. A kernel that initialised it to a sentinel string would have deleted the harm and left a row measuring a guard with no consequence.",
        "rust": "`Option<&[u8; NTYP]>` -- mbstring.c:3211's null initialiser, with the absence in the TYPE. THAT IS THE ROW'S RESULT AND IT IS FREE: the const assertion at the top of every Rust rung measures this type at the same eight bytes as the reference it wraps, because the discriminant lives in the reference's own null niche -- so the null-as-absent idiom costs exactly the bytes C spends, and cannot be read without being opened. A rung that carried a raw pointer plus a separate wrote flag would be paying for the safety C gets free, and controls/nullable.py measures that alternative rather than arguing about it."
      },
      "R1h IS f7326d6279629ccd80cc77fa389584f36434a2fd (Antony Dovgal, 2005-01-28, 'MFB: fix #31732') AND IT IS ONE LINE IN ONE HUNK IN ONE FILE: the strcasecmp test at mbstring.c:3219 gains a disjunct in front of it that tests the pointer first. R2 through R5 implement the same function, because the fix is COMPLETE for this defect -- it removes the only dereference of the unwritten out-parameter and changes no benign answer. Nothing is invented and there is no second hunk to adjudicate. It APPLIES to 5.0.0 with git apply at offset -13 lines, and controls/r1h_backport.py RUNS the apply on every invocation and takes the verdict FROM THE BYTES rather than from the exit status, because git apply --check has lied on this project before when the scratch path was gitignored. THE FIX WIDENS THE BENIGN DOMAIN RATHER THAN NARROWING IT: with the argument supplied the two builds behave identically, and with it absent the patched build answers with the four-element array where the unpatched one faults -- so the only input whose answer moves is one that previously CRASHED, the two C rungs agree on every call the measured corpus makes, and check.py stage 7h has nothing to refuse. controls/widened_domain.py measures that rather than asserting it. NO BACKTICKED SPELLING ANYWHERE IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements, the six rungs spell it in three languages, and no single token decides it."
    ],
    "forbidden": [
      "`memcpy` and `copy_from_slice` -- MOVING THE FRAME COPY OUT OF THE MEASURED SYMBOL. The 21-byte NUL-terminated frame the argument converter materialises is built by an explicit byte loop in every rung, and it is built there rather than by a library call because family A1 is symbol-scoped and STRUCTURALLY EXCLUDES callee work: on ph53, 100 per cent of a seven-instruction swing lived inside a libc call A1 could not see. A rung that called out for the copy would be measuring a different program with the same answer, and the difference would be invisible in the column this row publishes. Note the absence of backticks in the rest of this entry, and it is not style: in a forbidden entry EVERY backticked span becomes a banned token, so an entry that quotes what it is PROTECTING bans that too (item 100, three instances in three consecutive tasks).",
      "`strncasecmp` and `eq_ignore_ascii_case` -- A LENGTH-BOUNDED OR LIBRARY COMPARE instead of the NUL-terminated walk. Upstream compares with strcasecmp, which stops at the first NUL of EITHER operand and consults no length, and the row's corpus carries an argument with an embedded NUL inside its recorded length precisely so that a length-bounded compare would answer differently on that record. A library one would additionally move the work out of the measured symbol, which is the entry above's reason. The locale is not in question here: the kernel's own fold is A to Z lowered and nothing else, which is what the C library does under LC_ALL=C and what controls/libc_compare.py checks against the platform, with a must-fire control.",
      "`unwrap_or` -- SUBSTITUTING A DEFAULT ARGUMENT for an absent one. It is the most plausible Rust repair and it is the wrong one: the zero-argument call would stop faulting, but it would answer with the UNMATCHED arm rather than with the four-element array, which is neither the 5.0.0 behaviour nor the patched behaviour. Upstream's own answer is the opposite direction -- the 2005 fix makes the absent argument take the all branch, which is what the documentation already described -- so a default here would silence the detector and change the answer at the same time. It is also what the catalogue's own risk note warns about one row over: a kernel that papers over the missing output has rebuilt a different row."
    ],
    "why": "ph97 is PHP 5.0.0's `PHP_FUNCTION(mb_get_info)` out of `ext/mbstring/mbstring.c:3209-3252`, corpus row CRASH-126, tier `narrowed`. THE IDIOM IS AN OPTIONAL PARAMETER WHOSE PARSER REPORTS SUCCESS WITHOUT WRITING IT, AND A GUARD THAT IS PRESENT, PASSES, AND ANSWERS A DIFFERENT QUESTION FROM THE ONE THE CODE NEEDS ANSWERED. ⭐⭐⭐ THE WHOLE MECHANISM IS FIVE LINES AND THEY ARE ALL IN THE TARBALL. `:3211` writes `char *typ = NULL;`. `:3215` calls `zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, \"|s\", &typ, &typ_len)` and tests it for FAILURE. In `zend_parse_va_args` the spec scanner meets the optional marker FIRST, so `case '|': min_num_args = max_num_args;` at `zend_API.c:486` runs while `max_num_args` is still ZERO; the count test at `:511` therefore admits a call with no arguments; the write loop at `:537`, `while (num_args-- > 0)`, runs ZERO TIMES; and `:548` returns SUCCESS. `:3219` then hands `typ` -- still the caller's own NULL -- to `strcasecmp`. ⭐⭐ THE GUARD IS NOT MISSING. It is present, it is correct, and it passes: `:3215` tests *were the supplied arguments well-typed?* and `:3219` needs *was the optional argument supplied?*. Those are different propositions and they come apart at exactly one point, `ZEND_NUM_ARGS() == 0`. The real test is the argument count or `typ != NULL`, and the second is what upstream wrote four months later. ⚠ That is why this row is NOT `ph60`'s *a fallible call's failure not tested*: nothing fails here. The catalogue's own risk note on `ph60` says so in terms, and it is why CRASH-126 was split out of it. ⭐⭐⭐ CRITERION 2 IS MEASURED ON THIS ROW AND IT IS THE FIRST ROW IN THIS PROGRAMME OF WHICH THAT IS TRUE. `PROTOCOL_PHP.md` §A3a landed with this build. A PHP 5.0.0 CLI on this box, under the committed `LD_PRELOAD` shim `.tasks-php/probes/segaddr.c`, answers `mb_get_info()` with `SIG11 si_code=1 si_addr=(nil)` and exit 139, and answers `mb_get_info(\"internal_encoding\")` with `string(10) \"ISO-8859-1\"` and exit 0 in the same run on the same binary. ⚠⚠ TWO CAUTIONS TRAVEL WITH THAT AND THEY ARE REPEATED HERE BECAUSE A ROW THAT OMITS THEM HAS OVER-CLAIMED: the binary is php-in-safe-rust's ORACLE build (`-O3 -march=native -flto`, mysql + webext) and NOT a museum-default one, and a CLEAN run would not have been evidence of absence (`RECAP_PHP.md` F3). The converse is the new half: a run that faults, executed, is evidence of PRESENCE. `NOTES.md` §1 has both runs. ⭐⭐ AND THE C RUNG REPRODUCES IT AT THE ADDRESS. `c/kernel.c` on `inputs/adversarial-absent.bin` prints the SAME string from the SAME shim -- `SIG11 si_code=1 si_addr=(nil)` -- and ASan independently reports `SEGV on unknown address 0x000000000000`, a READ, in `ph97_strcasecmp`. The address is ZERO and not an offset because the dereference is of the second operand's FIRST byte: there is no struct field to add. `NOTES.md` §2. ⚠⚠ THE NULL VALUE AND THE ABSENT ARGUMENT ARE DIFFERENT STATES, AND ONLY ONE OF THEM FAULTS. `zend_API.c:302-308`'s `case IS_NULL:` writes `*p = NULL` only `if (return_null)`, which the `!` modifier sets and `\"|s\"` does not carry -- upstream's own comment on the missing break is *break omitted intentionally* -- so a supplied null becomes the EMPTY STRING. Measured on the same CLI: `mb_get_info(null)` answers `bool(false)`. `inputs/adversarial-nullvalue.bin` is that input and it is declared `clean`; the pair is what makes *the guard answers the wrong question* a behavioural claim rather than a reading of the source. ⛔⛔ THE GUARD MUST BE ABLE TO FAIL, AND ON THIS ROW IT FAILS BY TWO INDEPENDENT ROUTES, BOTH IN THE MEASURED CORPUS. `mb_get_info(array())` reaches `zend_API.c:330`, warns, and returns `bool(false)`; `mb_get_info(\"all\", \"x\")` reaches the count test at `:511` and returns `bool(false)`. Both are measured on the 5.0.0 CLI and both are records `inputs/gen.py` refuses to omit. A kernel whose `:3215` could never fail would have no guard at all, and the row's entire claim is about a guard that is there. ⚠ The three FAILURE routes are INDISTINGUISHABLE in the answer -- upstream returns `bool(false)` from `:3216` and from `:3250` and the CLI cannot tell them apart either -- so the kernel folds one tag for both, which is a fidelity decision and not an omission. ⭐⭐ THE ROW'S PERFORMANCE RESULT IS ABOUT A TYPE AND NOT ABOUT A TEST. C spells *absent* as a NULL `char *` and has no way to make the reader check; Rust spells it `Option<&[u8; 21]>`, which every Rust rung asserts at compile time occupies the SAME EIGHT BYTES as the reference it wraps, because the discriminant lives in the reference's own null niche. So the safety here is not a bounds check that costs instructions -- it is a representation that costs nothing and a `match` the compiler will not let you skip. `NOTES.md` §7 and §8 carry the numbers and the decomposition. ⚠⚠ AND THE CONSEQUENCE IS THAT NO RUST RUNG REPRODUCES THE DEFECT, WHICH IS A FINDING AND NEVER A PROBLEM (`CLAUDE.md` rule 6). In C the bug is an OMISSION -- a test that is not written -- and in Rust reproducing it takes a COMMISSION: an `unwrap` or an `unwrap_unchecked` on an unguarded optional, i.e. an extra operation a reviewer would ask about. `controls/rust_bug.py` builds BOTH of those on purpose and records what each does, so the ladder's *does the defect survive?* column is measured rather than argued. ⭐ THE R5 OBLIGATION IS `I12/O3` STATED DIRECTLY AND IT COSTS NOTHING TO RUN. `opt_get`'s `requires` is `t.is_some()` -- *a possibly-NULL pointer must not be passed to a callee that dereferences it without testing it*, with the possibility in the type -- discharged at all five compare sites from the ONE disjunct `f7326d627962` adds. ⛔ IT IS NOT DISCHARGED FROM THE PARSER'S POSTCONDITION, AND THAT IS THE POINT: `parse_va_args` returns SUCCESS with nothing written whenever the count is zero, and its `ensures` says so, so the parser's contract PROVES the pointer may be absent. No strengthening of the parser could discharge the obligation, because the parser is behaving correctly. Delete the 2005 disjunct from `verus.rs` and the file stops verifying, on that precondition, at that site -- `controls/negatives.py --emit r1`. ⚠ THE COMPARE IS IMPLEMENTED IN THE KERNEL AND THAT IS A MEASUREMENT DECISION AS MUCH AS A FIDELITY ONE. `kernel_exclusive_ir` (family A1) is symbol-scoped and structurally excludes callee work, so a kernel whose whole computation sat inside libc `strcasecmp` would read approximately zero in the statistic this programme publishes -- which is `RECAP_PHP.md` F119's lesson on `ph53`, where all of a seven-instruction swing lived inside a libc call A1 could not see. `controls/libc_compare.py` builds the libc-calling variant beside the shipped one and reports `inside_share` for both, which prices that exclusion directly rather than arguing about it, and it checks the in-kernel compare against the platform's own with a must-fire control. ▶ The consequence for the obligation is narrow and is stated in `provenance.invariant_note`: `I12/O3`'s *including libc* clause becomes *a callee that does not test its argument*, which is the operative half. ⚠ THE FOUR `!= NULL` TESTS INSIDE `mb_get_info` ARE DEAD, AND THEY ARE DEAD UPSTREAM AND NOT ONLY HERE. `mbfl_no_encoding2name` returns `\"\"` for an encoding number `mbfl_no2encoding` does not know (`mbfl_encoding.c:260-261`), so it cannot return NULL and `:3221`, `:3224`, `:3227` and `:3230` are unreachable in any 5.0.0 build. The kernel keeps both the tests and the reason, and the measured CLI's `http_input => string(0) \"\"` is that line firing. ⚠ `int typ_len;` at `:3212` is UNINITIALISED and is written only by the loop that never runs, so the faulting call leaves TWO outputs unwritten. It is NOT a second defect here, because nothing on any path reads it -- it is write-only in this function -- and no rung reads it either. It is recorded as an observation with that qualifier because it is `ph96`'s mechanism one variable over, and `ph96` is the row that closes this family. ⚠ THE ROW ALLOCATES NOTHING, which makes `PROTOCOL_PHP.md` §B1a's precondition hold at ZERO allocations per call rather than at O(1), so this row's cross-language column carries no allocator caveat at all. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "s_fold": "ph97_fold",
      "REC": "24",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 47
    },
    "twin_obligations": {
      "verus.rs": 54
    },
    "obligations_note": "47 verified / 0 errors, and 54 under `--cfg slb_twin` -- seven trusted accessors, therefore seven twins; `load_input` and `emit` are I/O and have none. WHAT THE PROOF RESTS ON IS ONE CONJUNCT, AND IT IS `I12/O3` VERBATIM: `opt_get`'s `requires t.is_some()`, discharged at ALL FIVE compare sites from ONE fact -- the `typ.is_none() ||` disjunct that IS `f7326d627962`. At the first site it comes from the short-circuit; at the other four it comes from the first site's condition having been FALSE. ⛔⛔ AND IT IS **NOT** DISCHARGED FROM THE PARSER'S POSTCONDITION, WHICH IS THE POINT OF THE ROW. `parse_va_args` returns SUCCESS with nothing written whenever the argument count is zero, and its `ensures` says exactly that: `r ==> *final(wrote) == (num_args == 1)`. The parser's contract is strong enough to prove the pointer MAY be absent -- so the guard at :3215 cannot discharge the obligation at :3219, and no amount of strengthening the parser would let it, because the parser is behaving correctly. ⭐ `controls/negatives.py --emit r1` deletes the 2005 disjunct from this file and that mutant must FAIL to verify; it fails on `opt_get`'s precondition at the FIRST site, which is the one the patch guards. The other six unchecked classes rest on facts that have nothing to do with PHP: a frame-width index bound, two slice bounds, and two constant-table bounds indexed by literals. NOTES.md section 10 keeps them apart, because an editor who deleted the 2005 line would be removing the precondition of exactly ONE of them.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 47 shipped + 7 for slb_twin_opt_get, _aget, _fset, _sget, _wsub, _sel_get and _name_get. ⭐ THE TWO TABLE ACCESSORS HAVE VERIFYING TWINS ONLY BECAUSE `s_sel` AND `s_name` ARE DEFINED AS THE CONSTANTS' OWN VIEWS rather than as a second transcription of their bytes: Verus does not evaluate the literals and does not need to, so the safe twin satisfies the same `ensures` the trusted body does. A row that had written the 105 bytes out again in spec-land would have had two unverifiable twins and would have needed the justification hatch for them. ⭐⭐⭐ THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A MEASUREMENT, NOT AN OMISSION. Verus's default is 10. Bisected on this box (controls/rlimit_bisect.sh; NOTES.md section 11 has the table): **1** suffices, plain and twin, and every value from 1 to 30 gives 47/0 and 54/0. ⚠⚠ BEFORE THE THREE `#[verifier::opaque]` ATTRIBUTES IT DID NOT, AND THE SYMPTOM IS WORTH RECOGNISING: the requirement was large and NON-MONOTONE -- rlimit 10 passed, 30 FAILED and 60 passed on the plain side -- which is a proof that passes on one side of a coin flip rather than a proof that is too big. The cause was `kernel`'s loop unfolding the whole chain down to the per-byte compare on every iteration; making three spec functions opaque and revealing them in the one function that needs them took the requirement from *unstable above 30* to *one*.",
    "items": {
      "verus.rs": {
        "s_sel": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_name": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "zeros21": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_pad": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_lower": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_cmp": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold_str": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_argc": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ty": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_len": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_lval": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_type_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_body_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_body": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_frame": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_ok": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_wrote": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_match": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_all": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_step": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_false": {
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
        "s_nfalse": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "s_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "opt_get": {
          "external": "verifier::external_body",
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "r@ == t.unwrap()@"
          ]
        },
        "slb_twin_opt_get": {
          "external": null,
          "requires": [
            "t.is_some()"
          ],
          "ensures": [
            "r@ == t.unwrap()@"
          ]
        },
        "aget": {
          "external": "verifier::external_body",
          "requires": [
            "i < NTYP"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "slb_twin_aget": {
          "external": null,
          "requires": [
            "i < NTYP"
          ],
          "ensures": [
            "r == v@[i as int]"
          ]
        },
        "fset": {
          "external": "verifier::external_body",
          "requires": [
            "i < NTYP"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
        },
        "slb_twin_fset": {
          "external": null,
          "requires": [
            "i < NTYP"
          ],
          "ensures": [
            "final(v)@ == old(v)@.update(i as int, x)"
          ]
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
        "sel_get": {
          "external": "verifier::external_body",
          "requires": [
            "k < NSEL"
          ],
          "ensures": [
            "r@ == s_sel(k as int)"
          ]
        },
        "slb_twin_sel_get": {
          "external": null,
          "requires": [
            "k < NSEL"
          ],
          "ensures": [
            "r@ == s_sel(k as int)"
          ]
        },
        "name_get": {
          "external": "verifier::external_body",
          "requires": [
            "k < NENC"
          ],
          "ensures": [
            "r@ == s_name(k as int)"
          ]
        },
        "slb_twin_name_get": {
          "external": null,
          "requires": [
            "k < NENC"
          ],
          "ensures": [
            "r@ == s_name(k as int)"
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
        "lower": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_lower(c)"
          ]
        },
        "strcasecmp": {
          "external": null,
          "requires": [],
          "ensures": [
            "r as int == s_cmp(a@, b@, 0)"
          ]
        },
        "fold_str": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == s_fold_str(acc, s@, 0)"
          ]
        },
        "parse_arg": {
          "external": null,
          "requires": [
            "old(frame)@ == zeros21()",
            "arg.val@.len() == STRMAX",
            "arg.len <= STRMAX"
          ],
          "ensures": [
            "r == s_type_ok(arg.ty)",
            "r ==> *final(n_out) <= STRMAX",
            "r ==> final(frame)@ == s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@))"
          ]
        },
        "parse_va_args": {
          "external": null,
          "requires": [
            "old(frame)@ == zeros21()",
            "*old(wrote) == false",
            "type_spec@ == seq![124u8, 115u8]",
            "arg.val@.len() == STRMAX",
            "arg.len <= STRMAX",
            "num_args <= 2"
          ],
          "ensures": [
            "r == (num_args <= 1 && (num_args == 0 || s_type_ok(arg.ty)))",
            "r ==> *final(wrote) == (num_args == 1)",
            "r && *final(wrote) ==> final(frame)@ == s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@))"
          ]
        },
        "get_info": {
          "external": null,
          "requires": [
            "b@.len() == REC"
          ],
          "ensures": [
            "r == s_step(b@, acc)",
            "s_false(b@) ==> *final(falses) == (*old(falses)).wrapping_add(1)",
            "!s_false(b@) ==> *final(falses) == *old(falses)"
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
        "opt_get": "⭐⭐ THE ROW'S OWN TRUSTED ITEM, AND ITS PARAMETER IS THE WHOLE STORY. `t: Option<&[u8; NTYP]>` is a value with exactly two shapes and the `requires` names the one the body assumes: `t.is_some()`. There is no second parameter to leave unconstrained -- the shape this stage exists to catch cannot arise here, because the ONLY thing that can make `t.unwrap_unchecked()` undefined is `t` itself. ⚠ What makes the entry worth reading is WHERE the precondition comes from: not from arithmetic, not from the caller's convenience, and NOT from the parser -- whose postcondition proves the opposite, that the pointer may be absent -- but from `f7326d627962`, the one line PHP added in 2005. `controls/negatives.py --emit r1` deletes it and that mutant must FAIL to verify.",
        "aget": "`v: &[u8; NTYP]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its length is in its TYPE, so there is nothing about it left for a `requires` to say: the length holds for every value this signature admits. The only quantity that can make the unchecked read undefined is `i`, and `i` IS constrained, by `i < NTYP`. ⚠ IT IS NOT THE SAME ARGUMENT AS `sget`'s: that one takes a SLICE, whose length is a run-time fact, so its `requires` has to name it.",
        "fset": "`x: u8` is a PURE VALUE and needs no precondition. The unchecked operation's definedness depends on `i` being in bounds and on `v` being a live fixed-size array, and on NOTHING about the byte being written -- every inhabitant of `u8` is a legal store into a slot that is already initialised. Contrast the shape this stage exists to catch, an unconstrained parameter that the body then indexes with: here the INDEXING parameter is the constrained one, and the `ensures` names the WHOLE post-state, so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition.",
        "sget": "`v: &[u8]` is a SLICE and its length is a run-time fact, so the `requires` has to name it -- `i < v@.len()` -- and that is the whole of what makes the unchecked read sound. There is no second parameter. ⚠ The two call sites bound `i` differently: inside the record decode it is a literal under 24 and the caller's `b@.len() == REC` supplies the rest; inside the frame copy it is the loop's own cursor under `STRMAX`, and `arg.val@.len() == STRMAX` is carried as a precondition of the enclosing function rather than re-derived.",
        "wsub": "`v: &[u8]` again, and the constrained quantities are BOTH endpoints at once: `o + n <= v@.len()` is one conjunct and it bounds the pair, which is what a sub-slice needs and what an index bound would not give. ⚠ The `ensures` names the whole result -- the subrange, not merely its length -- because a body that returned a correctly-sized slice of the WRONG bytes would satisfy a length-only contract and change every answer downstream.",
        "sel_get": "`k: usize` is the only parameter and it IS constrained, by `k < NSEL`. ⭐ What is worth reading here is the `ensures`: `r@ == s_sel(k as int)`, where `s_sel` is DEFINED AS THE CONSTANT TABLE'S OWN VIEW. So the contract does not assert anything about the table's 105 bytes -- it says the accessor returns row `k` of it, whatever it is -- and that is why the verified twin can meet the same contract with a bounds-checked index. A row that had transcribed the bytes into spec-land instead would have put them in the TCB. The bytes themselves are checked by `controls/tables.py`, which diffs all three transcriptions (C, Rust, model.py) and carries must-fire negatives.",
        "name_get": "same argument as `sel_get` on the encoding-name table: `k < NENC` is the only constraint there is, and the `ensures` names the table's own view rather than its bytes. ⚠ The entry exists separately because the BOUND is different -- three entries rather than five -- and a reviewer checking that the bound matches the array has two different pairs to keep apart in this file."
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
      "if stride_w >= 24 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph97's two probe shapes have different work per call (122 and 1036 window bytes, i.e. 5 and 43 CALL records) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. ⚠ `work_per_call` is the WINDOW IN BYTES and the record count is `stride / 24` truncated, so the work really does scale with the denominator rather than merely being labelled by it. ⚠⚠ THE PER-RECORD WORK IS NOT CONSTANT AND THE ROW SAYS SO RATHER THAN HIDING IT: a record whose argument matches the first arm does ONE compare and EIGHT folds, one that matches nothing does FIVE compares and no fold, and one the guard refuses does neither. NOTES.md section 8 decomposes the marginal instead of presenting it as a per-byte rate. ⚠ There is also a fixed per-call term -- the 21-byte frame is zeroed on every call whatever the argument is -- and it does not scale with the stride."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "norel",
      "O3": "norel",
      "why": "⭐⭐⭐ R4 AND R5 ARE THE SAME MACHINE CODE AT BOTH OPTIMISATION LEVELS, AND AT O3 THEY ARE THE SAME RAW BYTES. Measured, O3 isolated: both `kernel` symbols are 558 instructions, `md5_fn` and `md5_fn_norel` and `md5_norm` all IDENTICAL, and `asm.py::identity_level` returns `exact` with `md5_raw_equal` true. At O0 isolated both are 1224 instructions with `md5_fn_norel` and `md5_norm` identical and the raw bytes differing, i.e. `norel`. ⚠ THE PIN IS `norel` AT BOTH LEVELS AND NOT `exact` AT O3, DELIBERATELY: `exact` compares raw bytes including relocations, `kernel_fingerprint` is PATH-SENSITIVE and has fired live in both directions on this project (F101, item 109), and a pin that a re-measure under a longer build root could break is a pin that reports an environment change as a defect. The `exact` reading is a MEASUREMENT recorded in NOTES.md section 11, not a contract. ⚠⚠ AND IT TOOK A REPAIR TO GET THERE, WHICH IS ITSELF THE FINDING: as first written the two rungs differed by 144 instructions at O0 and were `exact` at O3, so the O3 reading alone would have certified an equivalence that was FALSE one optimisation level down. The cause was three exec-text divergences the optimiser erased -- two accessors R4 called through the checked path, a bitmask where R5 wrote a modulus, and seven trusted wrappers that carried `#[inline(always)]` in R4 and not in R5. ▶ A `whole`-mode pin is NOT claimed: the gate compares the `isolated` cells, and in `whole` mode the kernel is inlined into `main` and there is no common symbol to compare. ⭐⭐ AND MIRI IS STILL REQUIRED: `norel` counts as the same machine code, so `.memory/02-bench-rules.md`'s non-waivable clause does not fire on this pin -- but the row has SEVEN trusted accessors, one of which WRITES and one of which is `Option::unwrap_unchecked`, and that is the clause that does. `miri.required: true` is a declaration about the trusted surface, not about this entry. ⚠ The figures here are from results-php/gate/ph97-optarg-unwritten.json and results-php/ph97-optarg-unwritten.json; PROTOCOL.md rule 6's addendum says to re-read this entry against THOSE records rather than trusting the hash."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph97 has SEVEN and one of them WRITES (`fset`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only the byte at `i` would let a body that also clobbered `i + 1` through every Verus stage. The shipped `ensures` is the whole post-state. ⭐ AND ONE OF THE SEVEN IS NOT AN INDEX AT ALL: `opt_get` is `Option::unwrap_unchecked`, whose misuse is not an out-of-bounds access but a read through a reference the niche says is absent, and Miri is the only detector in this tree that sees that class -- which on THIS row is the defect itself rather than a neighbouring hazard.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph97's cost is 4 x (one window of 5 or 43 call records, each parsed and run through at most five 21-byte compares), i.e. four orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "ext/mbstring/mbstring.c",
    "c_lines": [
      3209,
      3252
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '3209,3252p'",
    "extract_sha256": "e33b0520cd20f81b8395d9979fd056b5aa7069cc5d974aaf571c33ab4c68a8ff",
    "extra_spans": [
      {
        "c_file": "Zend/zend_API.c",
        "c_lines": [
          463,
          549
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_API.c | sed -n '463,549p'",
        "extract_sha256": "d0799daecbcc4ad7e58869a28f6a6488475e7f8c0c4a1b23366e8246907e5587",
        "why": "⭐⭐⭐ THE MECHANISM, AND THE ROW IS UNREADABLE WITHOUT IT. `zend_parse_va_args` is where `\"|s\"` becomes `min_num_args == 0`: `:485-487`'s `case '|': min_num_args = max_num_args;` runs while `max_num_args` is still ZERO because the `|` is the FIRST character; `:511`'s count test then admits `num_args == 0`; `:537`'s `while (num_args-- > 0)` write loop runs ZERO times; and `:548` returns SUCCESS. The guard at mbstring.c:3215 is PRESENT and it PASSES, which is the whole claim. ⚠ `:527-534`'s `EG(argument_stack)` consistency check is inside this span and is DELETED in the kernel -- itemised in `divergences`."
      },
      {
        "c_file": "Zend/zend_API.c",
        "c_lines": [
          290,
          333
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/Zend/zend_API.c | sed -n '290,333p'",
        "extract_sha256": "5c0981b4dbf53b850c8fb9c317ab129243dfadaff14a6e24a86bca6f0e32c118",
        "why": "⭐⭐ THE `'s'` ARM OF THE ARGUMENT CONVERTER, AND IT IS WHAT SEPARATES THE NULL VALUE FROM THE ABSENT ARGUMENT. `:302-308`'s `case IS_NULL:` writes `*p = NULL; *pl = 0;` ONLY `if (return_null)`, which the `!` modifier sets and `\"|s\"` does not carry -- upstream's own comment on the missing break is *break omitted intentionally* -- so a null ARGUMENT falls through to `convert_to_string_ex` and becomes the EMPTY STRING. `:327-330` is the IS_ARRAY/IS_RESOURCE arm that returns the expected type name and makes the `:3215` guard FAIL, which is the row's `F` tick: the guard is reachable and it can fail. Measured on a 5.0.0 CLI: `mb_get_info(null)` answers `bool(false)`, `mb_get_info(array())` warns and answers `bool(false)`, and only `mb_get_info()` faults."
      },
      {
        "c_file": "ext/mbstring/libmbfl/mbfl/mbfl_encoding.c",
        "c_lines": [
          253,
          265
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfl_encoding.c | sed -n '253,265p'",
        "extract_sha256": "7eb4e9d208616fec108156a6a1d8552a90425f0e24f6c21c6e0ab35fe8c420f0",
        "why": "⚠ WHY `mb_get_info`'s FOUR `!= NULL` TESTS ARE DEAD -- UPSTREAM, not only in this kernel. `mbfl_no_encoding2name` returns `\"\"` for an encoding number `mbfl_no2encoding` does not know (`:260-261`), so it CANNOT return NULL and `:3221`, `:3224`, `:3227` and `:3230` are unreachable arms in any 5.0.0 build. The kernel keeps both the tests and the reason. It is also why the measured CLI answers `http_input` with a zero-length string rather than omitting the key."
      },
      {
        "c_file": "ext/mbstring/mbstring.c",
        "c_lines": [
          720,
          735
        ],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '720,735p'",
        "extract_sha256": "0e3de141d376945eacd2db7a90dc947be6f17bc64136448327c2050478031fb2",
        "why": "⭐ THE GLOBALS THE CHAIN READS, SO THE FOUR SETTINGS ARE PINNED AND NOT INVENTED. `:726` sets `MBSTRG(http_input_identify) = mbfl_no_encoding_invalid`, which is the encoding number the span above turns into `\"\"`. The kernel's four-entry table is this configuration, and the measured 5.0.0 CLI reports exactly it: internal_encoding `ISO-8859-1`, http_input `\"\"`, http_output `pass`, func_overload `pass`."
      }
    ],
    "extra_spans_note": "THE ROW LIFTS FIVE SPANS AND ALL FIVE ARE PINNED. `provenance.c_lines` names the defect site (`PHP_FUNCTION(mb_get_info)`, mbstring.c:3209-3252); the four extras are the parser that makes it reachable (zend_API.c:463-549), the argument converter whose IS_NULL fall-through separates the null VALUE from the absent ARGUMENT (zend_API.c:290-333), the callee whose contract makes four of the defect site's own tests dead (mbfl_encoding.c:253-265), and the globals the chain reads (mbstring.c:720-735). ⚠ TWO OF THE FIVE ARE THE MECHANISM RATHER THAN CONTEXT: a row that pinned only the defect site would certify a span containing a dereference of a pointer that is NULL for a reason NOT IN THAT SPAN, and a reader would have to take `\"|s\" means optional\" on trust. ⚠ What is NOT pinned is `Zend/zend_execute_API.c`'s argument-stack machinery: `zend_API.c:527-534` reads it, the kernel deletes that check, and the deletion is itemised in `divergences` rather than hidden behind a span.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "TSRMLS_DC / TSRMLS_CC",
        "kind": "deletion",
        "where": "mbstring.c:3215; zend_API.c:463, :542",
        "why": "thread plumbing, no semantics"
      },
      {
        "what": "`zval` becomes a four-field record and `zval **` becomes a pointer to one",
        "kind": "substitution",
        "where": "zend_API.c:297-333",
        "why": "the `'s'` arm reads exactly three things out of a zval -- `Z_TYPE_PP`, `Z_STRVAL_PP` and `Z_STRLEN_PP` -- plus `Z_LVAL_PP` on the IS_BOOL path, and this record carries those four and nothing else. The refcount, the `is_ref` bit and the union's other members carry no part of this mechanism. Demonstrated behaviour-preserving on the extracted domain by model.py's three independent implementations agreeing on every window of every input AND on 200+ synthetic records spanning the whole (num_args x type) cross product, and by the gate's stage-3 cross-rung checksum on every input. No semantics."
      },
      {
        "what": "the `va_list` becomes three explicit out-parameters (`frame`, `wrote`, `typ_len`)",
        "kind": "substitution",
        "where": "zend_API.c:299-300, :315-316, :542",
        "why": "`zend_parse_arg` pops `char **p` and `int *pl` off a `va_list` and writes through them; `\"|s\"` has exactly one type letter, so there is exactly one pair. ⚠ `wrote` is the bit that C spells as *`typ` still holds its `:3211` initialiser*: Rust cannot let a callee store a reference to a frame the same callee is still writing, so the callee reports whether it wrote and the caller forms `Option<&[u8; 21]>` from that -- which is `char *typ = NULL` with the absence in the TYPE. The one bit is the same bit. No semantics."
      },
      {
        "what": "`zend_parse_va_args`'s `EG(argument_stack)` consistency check",
        "kind": "deletion",
        "where": "zend_API.c:527-534",
        "why": "`p = EG(argument_stack).top_element-2; arg_count = (ulong) *p; if (num_args > arg_count) return FAILURE;` re-derives the argument count from the VM's own stack and refuses a caller that lied. `num_args` here IS `ZEND_NUM_ARGS()`, which is read from the same stack one word away, so the two cannot disagree in a well-formed call and the arm is unreachable. ⭐ It is also the one thing that would have forced the executor into this row, and it does not: `TASK_PHP_054` agent C named exactly this as what would demote the row, and the measurement is that the check is dead. No semantics."
      },
      {
        "what": "IS_LONG and IS_DOUBLE fold into the IS_STRING arm; IS_OBJECT and IS_RESOURCE fold into the IS_ARRAY arm",
        "kind": "deletion",
        "where": "zend_API.c:310-313, :318-329",
        "why": "the 's' arm sorts every zval type into exactly two outcomes -- CONVERTED (IS_NULL, IS_STRING, IS_LONG, IS_DOUBLE, IS_BOOL, and IS_OBJECT with a cast handler) or REFUSED (IS_ARRAY, IS_RESOURCE, IS_OBJECT without one) -- and the row keeps one representative of each side plus the two whose conversion differs observably (IS_NULL -> \"\", IS_BOOL -> \"\" or \"1\"). Modelling `convert_to_string_ex` on a LONG would add decimal formatting, which is a different function's worth of code and carries no part of this mechanism. No semantics on the extracted domain."
      },
      {
        "what": "`array_init` + four `add_assoc_string` become a fixed-size fold",
        "kind": "substitution",
        "where": "mbstring.c:3220-3232",
        "why": "the `all` arm builds a four-element hash whose keys are four of the row's own five selector strings and whose values are the four MBSTRG settings; the kernel folds the same eight strings into the `u64` in the same order. The hash table is the CONTAINER and not the defect (.memory-php/01-extraction.md prices extraction at the DEFECT site), and keeping it would make this the only allocating row in a family whose precondition (PROTOCOL_PHP.md B1a) it otherwise satisfies at ZERO allocations per call. No semantics on the extracted domain."
      },
      {
        "what": "`RETVAL_STRING` / `RETURN_FALSE` become fold tags",
        "kind": "substitution",
        "where": "mbstring.c:3216, :3235, :3239, :3243, :3247, :3250",
        "why": "the function's three observable answers are an ARRAY, a STRING and `bool(false)`, and the kernel folds a distinct tag for each plus the string's bytes. ⚠ BOTH `RETURN_FALSE` sites fold the SAME tag, deliberately: upstream returns `bool(false)` from both and the measured 5.0.0 CLI cannot tell them apart either -- `mb_get_info(array())` and `mb_get_info(\"nonesuch\")` both print `bool(false)`. A kernel that distinguished them would answer a question PHP does not. No semantics."
      },
      {
        "what": "libc `strcasecmp` becomes `ph97_strcasecmp`, in the kernel",
        "kind": "substitution",
        "where": "mbstring.c:3219, :3233, :3237, :3241, :3245",
        "why": "⛔ A MEASUREMENT DECISION AS MUCH AS A FIDELITY ONE. `kernel_exclusive_ir` (family A1) is symbol-scoped and structurally EXCLUDES callee work, so a kernel whose whole computation sat inside libc would read approximately zero in the statistic this programme publishes -- which is F119's lesson on `ph53`, where 100 % of a +/-7 Ir swing lived inside a libc `memset` A1 could not see. The body is `strcasecmp(3)` in the C locale, byte for byte: fold A-Z, compare, stop at the first NUL, return the difference of the folded bytes. Demonstrated behaviour-preserving by `controls/libc_compare.py`, which drives it against the platform's own `strcasecmp` over a domain including every selector, every casing, embedded NULs and every one-character mutation, WITH a must-fire control. No semantics."
      },
      {
        "what": "`int typ_len;` is initialised",
        "kind": "substitution",
        "where": "mbstring.c:3212",
        "why": "upstream leaves it UNINITIALISED and writes it only in the same loop that never runs -- so the faulting call leaves TWO outputs unwritten. It is not a second defect, because nothing on any path reads it: it is write-only in `mb_get_info`. The C rung keeps it uninitialised; the four Rust rungs set it to 0 because Rust has no uninitialised `i32` without `MaybeUninit`, which this row deliberately does not use. Neither rung READS it, so no rung's answer can depend on it. ../NOTES.md §3 records the observation with its own *not load-bearing* qualifier; it is `ph96`'s mechanism, one row over. No semantics."
      },
      {
        "what": "the encoding-name tables are NUL-padded to the frame width",
        "kind": "substitution",
        "where": "mbstring.c:3219-3247, mbfl_encoding.c:263",
        "why": "upstream's operands are NUL-terminated `char *` of whatever length; both operands here are `[u8; 21]` so that the compare is symmetric and total. Every walk in every rung stops at the first NUL, so the padding is invisible to the answer -- and it is what lets the kernel bound the compare without inventing a length test upstream does not have. Demonstrated behaviour-preserving by `controls/tables.py`, which checks that no table entry is longer than 20 bytes and that all three transcriptions (C, Rust, model.py) carry the same bytes. No semantics."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. ⭐ THERE ARE NO PROJECTIONS ON THIS ROW: every observable behaviour of the extracted span is reproduced rather than narrowed, which is unusual and is a property of the span (44 lines of C with no allocation, no re-entry and no container) rather than of the extraction. PROTOCOL_PHP.md A1 requires a substitution in a non-`modelled` tier to be (a) itemised with a line citation, (b) given a `why` ending in 'no semantics' and (c) DEMONSTRATED behaviour-preserving rather than asserted; all seven substitutions here carry (c) by measurement -- the libc compare by `controls/libc_compare.py` with a must-fire control, the tables by `controls/tables.py`, and the rest by model.py's three independent implementations plus the gate's own stage-3 cross-rung checksum on every input.",
    "root_cause_ids": [
      "optional-argument-left-null-by-zend_parse_parameters-then-dereferenced-by-strcasecmp"
    ],
    "cwe": "CWE-476",
    "cwe_note": "index.csv records CWE-476 (NULL pointer dereference) for CRASH-126 and this row reproduces exactly that, MEASURED ON BOTH SIDES AND AT THE SAME ADDRESS. A PHP 5.0.0 CLI on this box under `.tasks-php/probes/segaddr.c` answers `mb_get_info()` with `SIG11 si_code=1 si_addr=(nil)` and exit 139, while `mb_get_info(\"internal_encoding\")` returns `ISO-8859-1` and exit 0 in the same run; `c/kernel.c` on `inputs/adversarial-absent.bin` gives the same `si_addr=(nil)` under the same shim, and ASan independently reports `SEGV on unknown address 0x000000000000 ... READ memory access` in `ph97_strcasecmp`. ⭐ `si_addr` is ZERO and not an offset, because the dereference is of the second operand's FIRST byte -- there is no struct field to add. ../NOTES.md §1 and §2 have both runs and the build each was taken on.",
    "fix_commit": "f7326d6279629ccd80cc77fa389584f36434a2fd",
    "fix_commit_note": "⚠ THE SHA IS THE CORPUS INDEX'S OWN `fix_commit` VALUE AND THE ROW USES ITS SHORT FORM EVERYWHERE. `f7326d627962` -- Antony Dovgal, 2005-01-28, 'MFB: fix #31732' -- is ONE FILE, ONE HUNK, ONE LINE: `if (!strcasecmp(\"all\", typ))` becomes `if (!typ || !strcasecmp(\"all\", typ))`. The patch bytes are at controls/f7326d627962.patch. ⭐⭐ IT IS THE SMALLEST R1h IN EITHER PROGRAMME. `git apply` PLACES it on the pristine 5.0.0 file -- *Hunk #1 succeeded at 3216 (offset -13 lines)* -- and the post-image line at `:3219` is byte for byte the patch's `+` line; `controls/r1h_backport.py` RUNS the apply on every invocation and reads the VERDICT OUT OF THE BYTES rather than out of the exit status, because `git apply --check` has lied on this project before when the scratch path was gitignored (ph55 NOTES §5). ⭐⭐ AND IT WIDENS THE BENIGN DOMAIN RATHER THAN NARROWING IT: with the argument supplied the two builds are byte-identical in behaviour, and with the argument ABSENT the patched build answers with the `all` array where the unpatched one faults. So the only input whose answer moves is one that previously CRASHED, the two C rungs agree on every call in `small.bin` and `large.bin`, and `check.py` stage 7h has nothing to refuse. `controls/widened_domain.py` measures that rather than asserting it. ⚠ The patch BINDS: its `From` line is `f7326d6279629ccd80cc77fa389584f36434a2fd` and its filename is the same prefix, so it is not one of F115's three mis-bound cached patches. ⚠ `preimage_screen.py --row ph97` returns CANDIDATE with 1 record and 1 id -> 1 commit, and CANDIDATE is the screen's POSITIVE label. ⭐ There is NO census: one hunk, one site, and `strcasecmp` is called at 12 places in `mbstring.c` of which 5 are this chain -- a clean negative, and `controls/census.py` re-derives the count rather than asserting it. ⚠ UNVERIFIED IN THIS ROW: whether `f7326d627962` is the FIRST commit to close this site and whether any 5.0.x branch backport preceded it. PROTOCOL_PHP.md F5(iii) asks for confirmation against the tags and this row confirms the SITE and the DIRECTION from the patch bytes rather than the exact commit.",
    "invariant": "I12",
    "obligation": "O3",
    "invariant_note": "The catalogue row says `I12/O3` and this block names it unchanged. **I12** is *a fallible call's outcome must be tested before its result is used* and its **O3** is 'a possibly-NULL pointer must not be passed to a callee -- including libc -- that dereferences it without testing it'. ⭐⭐ THE ROW NARROWS THE PHRASE *including libc* AND SAYS SO: with the compare implemented INSIDE the kernel (see `divergences`), the operative half of O3 is *a callee that does not test its argument*, which `ph97_strcasecmp` does not -- the clause is about the callee's contract, not about which library it lives in. ⚠ What the row does NOT claim is `I12/O1`: the call at `:3215` IS tested and it does NOT fail. That is the distinction the catalogue's own `⚠ risk` note on `ph60` draws, and it is why this is a separate row. Blind-labelled by the corpus (`paper/invariants-list.md`) and carried across unmodified.",
    "echoes": [],
    "echoes_note": "The catalogue's `echoes` column for ph97 is EMPTY and this block carries that verbatim rather than inventing a neighbour. ⚠ A negative is a result (F10): no `patterns/` row models an optional-argument parser that returns SUCCESS without writing its out-parameter, and the nearest PAT analogues are about a pointer that is null for a DIFFERENT reason. ⚠ The nearest neighbour anywhere is `ph96`, one row over in the same family: SAME obligation (I12), same *the guard is present and it passes* shape, and a DIFFERENT reason the output is missing -- there the callee writes NULL into the out-parameter on purpose and returns SUCCESS anyway. PLAN_PHP.md §3 makes C-side duplication the only kill and these are not duplicates: the unchecked predicate differs (*was it supplied?* against *was it written?*), and so does the upstream repair.",
    "uses_allocator": false,
    "uses_allocator_why": "the kernel allocates NOTHING. The argument frame is a 21-byte frame object, the two constant tables are `static const`, and no rung calls `emalloc`, `efree`, `malloc` or `free` -- so allocations per kernel call are ZERO, not merely O(1), and PROTOCOL_PHP.md B1a's precondition holds with room to spare. ⭐ That is why this row's cross-language column carries NO allocator caveat: unlike `ph64` there is no allocator term in it at all, and the same is true of the LIBC term -- `controls/libc_compare.py` reports `inside_share` for the in-kernel compare and for the libc-calling variant side by side. ⚠ DECLARED, NEVER DETECTED (TASK_PHP_008 §0.4) -- nothing reads this field and no verdict depends on it. The row still carries `c/emalloc_shim.h` as a symlink, because that rule is UNCONDITIONAL."
  }
}
```
