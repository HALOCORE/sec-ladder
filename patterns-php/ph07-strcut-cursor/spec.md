# ph07 — `mbfl_strcut`: a cursor loop with no end test

**PHP 5.0.0, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`, corpus row
CRASH-124, tier `narrowed`.** `mb_strcut($s, strlen($s) + 1, 1)` walks a cursor
past the end of a PHP string and reads there. The walk's only exit is
`if (n > from)`; `string->len` is read at the top of the arm and used only by
the clamps that run *after* the walk.

⭐ **The same function's second walk is bounded** (`if (k >= (int)string->len)`),
so `mbfl_strcut` guards its end search and not its start search, in adjacent
lines. That asymmetry is the row — see `NOTES.md` §5.

⚠ **R1h is the guard configuration upstream converged on — `php-5.2.12 …
php-5.2.17`, `PHP_FUNCTION(mb_strcut)` body sha256 `26e2099e33433c74` — and it
is in the CALLER**, `ext/mbstring/mbstring.c`, not in `mbfl_strcut`. That is
`cb3cca21b345` (2005-12-15) hunk (a), after `c2471b495009` (2009-09-23) removed
hunk (b) as **bug #49354, with a regression test**.

⚠⚠ **The row shipped both hunks until `TASK_PHP_018`, and its own gate had
already said why it should not.** `check.py` stage 7h refuses an R1h that
changes benign output; hunk (b) changes it on **13.5 %** of benign calls while
removing **none** of the 15 333 over-reads. The row read the refusal as a
harness limitation and restricted the measured corpus instead. Upstream reached
the same verdict from a bug report, four years later. `NOTES.md` §4 has the
history, the tag sweep, what each guard buys, and the fidelity question that
comes with an R1h that is a *subset* of a labelled security fix.

The machine-readable contract follows. `harness-php/gate.py ph07-strcut-cursor`
enforces it; `README.md` is the reader's entry point and `NOTES.md` carries the
measurements.

```slb-contract
{
  "kernel": "kernel(buf: &[u8], off: usize, len: usize) -> u64",
  "model": "model.py",
  "requires": [
    "off + len <= buf_len",
    "9 <= len"
  ],
  "ensures": [
    "result == strcut_fold(buf, off, len)"
  ],
  "note": "requires/ensures above are DERIVED by check.py from verus.rs's own clause text through verus.translate, and the copy here must equal the derivation exactly. They are evaluated in Python against the bindings model.py yields per call (buf/off/len/buf_len/result) plus the helper it supplies (strcut_fold). `strcut_fold` is model.py's SECOND, independent implementation -- two pure transition functions driven to a fixpoint, mirroring verus.rs's tail-recursive `walk_start`/`walk_end` one application at a time -- and not the simulation that produced `result`; `selfcheck()` runs the two against each other on the calls each input makes AND on synthetic windows model.py builds itself, spanning every lead-byte class, `from` past the end, and both signs of both parameters. THE SECOND HALF IS NOT OPTIONAL (PROTOCOL_PHP.md A2a rule 2): ph03 shipped for a whole task with its two implementations computing different functions, because its corpus took one arm of a two-armed branch and `inputs/` is not a domain. A THIRD spelling -- `_dumb`, which builds the cursor list and selects from it -- checks every shipped window as well.",
  "idiom": {
    "required": [
      {
        "c": "the start walk's only exit is the accumulated count, `if (n > from)` at mbfilter.c:1206, and `p` is never compared against `string->val + string->len`. The Rust spelling is the ROTATED form -- read once, then `while n <= frm` -- which performs the same reads in the same order (provenance.divergences)",
        "rust": "`while n <= frm`"
      },
      {
        "c": "`m = mbtab[*p]`",
        "rust": "`MBTAB`"
      },
      {
        "c": "`if (k >= (int)string->len)`",
        "rust": "`if k >= slen`"
      },
      {
        "c": "`slen = (unsigned int)(len - 9)`",
        "rust": "`s.len() - 1`"
      },
      "R1h is the guard CONFIGURATION UPSTREAM CONVERGED ON -- php-5.2.12 .. php-5.2.17, PHP_FUNCTION(mb_strcut) body sha256 26e2099e33433c74, which is cb3cca21b345 hunk (a) and NOTHING ELSE -- and R2-R5 implement the same function, because that configuration is COMPLETE: unlike ph03's fix it leaves no residue (controls/fix_scope.py Q1: 15 333 over-reads become 0). \u26a0\u26a0 WHAT WAS CHOSEN AND WHAT WAS CHOSEN AGAINST, because a row publishes both. THE ALTERNATIVE, and it is what this row shipped until TASK_PHP_018: cite the 2005 commit cb3cca21b345 entire -- BOTH hunks -- and disclose that hunk (b) changes benign output. It was rejected on THREE measurements, none of them about Rust or Verus. (i) hunk (b) removes NONE of the 15 333 out-of-bounds reads and hunk (a) removes ALL of them, so (b) is not part of the memory-safety fix (controls/fix_scope.py Q1). (ii) hunk (b) CHANGES the answer on 15 870 of 117 612 benign calls (13.5 %), so honouring the whole commit forced inputs/gen.py to exclude the region it fires in -- a corpus of 86.5 % of the benign domain, presented as the domain (Q2). (iii) UPSTREAM REMOVED IT: c2471b495009 (Moriyoshi Koizumi, 2009-09-23) deletes hunk (b) as bug #49354, 'mb_strcut() cuts wrong length when offset is within a multibyte character', and ships ext/mbstring/tests/bug49354.phpt with it. controls/bug49354.py replays those six expectations against all three configurations: hunk (a) alone agrees on all six, hunk (a)+(b) is WRONG on one, and R1 over-reads on one. \u26a0 THE COST OF THE CHOICE, stated rather than smoothed over: a tag range is not a commit, and PROTOCOL_PHP.md C says R1h is the real upstream fix_commit. The argument is that what upstream SHIPPED AND KEPT is a stronger citation than what it once merged -- five tags carry this configuration byte-for-byte, and php-5.3.2 .. php-5.3.29 carry it respelled (body sha256 49ad3ab2796d63e4) -- and that a subset of a commit pinned by (tag range, function, body sha256) is more checkable than a commit id, not less. It is still a SUBSET of a labelled security fix and the row says so here rather than in a footnote. Both commits are cited in provenance.fix_commit and both patches are under controls/. NO BACKTICKED SPELLING IN THIS ENTRY, deliberately: it is a statement about WHICH ALGORITHM each rung implements and no single token decides it. The mechanical checks are controls/negatives.py --emit noguard, which must NOT verify, and forbidden[3], which pins hunk (b)'s own two spellings ABSENT from every rung.",
      "the mblen_table is STATIC DATA in every rung -- a 256-byte constant lifted verbatim from mbfilter_utf8.c:39-56, not part of the blob. NO BACKTICKED SPELLING: the C writes a file-scope `static const unsigned char`, the Rust rungs a `static [u8; 256]` and verus.rs a `pub const [u8; 256]`, which are three legitimate spellings of one fact. An attacker who could choose the table could put a zero in it and hang the start walk, which is a defect PHP does not have."
    ],
    "forbidden": [
      "`if (n >= from)` -- relaxing the strict exit test. It moves the cut by one character and it would mask the terminator read the upstream clamp depends on. The strictness is the program.",
      "`p - string->val < (int)string->len` -- the in-loop bound a reader adds on sight. Adding it to the start walk deletes the row: the whole point is that the bound is computed and then not consulted until `:1227`.",
      "`frm = slen` -- the 2010 in-library CLAMP (d9dda48f8a7e's prologue) written into a Rust rung. It is a real upstream guard but it is NOT this row's fix_commit and it is a DIFFERENT function: cb3cca21b345 returns FALSE where the clamp returns a cut. controls/fix_scope.py measures both.",
      {
        "c": "`((unsigned)from + (unsigned)length) > str_len` -- cb3cca21b345 HUNK (b), in the C rungs' own spelling. TASK_PHP_018 pins it ABSENT because upstream removed it (c2471b495009, bug #49354) and R1h is now hunk (a) alone: a rung that re-acquired it would compute a function upstream withdrew, and would silently re-impose the corpus restriction inputs/gen.py has just been rewritten to forbid. \u26a0 PER-LANGUAGE because the C and Rust spellings share no token. \u26a0 It pins the SPELLING and not the property: a rung could still clamp the length argument by some third expression, which is what a forbidden entry can and cannot do, and is why controls/negatives.py, controls/bug49354.py and controls/spellings.py sit beside it. Measured clean on all six rungs with harness/check.py::spelling_matches itself (.temp/php18/spellcheck.log).",
        "rust": "`frm.saturating_add(length) > slen` -- cb3cca21b345 HUNK (b), in the four Rust rungs' own spelling. TASK_PHP_018 pins it ABSENT because upstream removed it (c2471b495009, bug #49354) and R1h is now hunk (a) alone: a rung that re-acquired it would compute a function upstream withdrew, and would silently re-impose the corpus restriction inputs/gen.py has just been rewritten to forbid. \u26a0 PER-LANGUAGE because the C and Rust spellings share no token. \u26a0 It pins the SPELLING and not the property: a rung could still clamp the length argument by some third expression, which is what a forbidden entry can and cannot do, and is why controls/negatives.py, controls/bug49354.py and controls/spellings.py sit beside it. Measured clean on all six rungs with harness/check.py::spelling_matches itself (.temp/php18/spellcheck.log)."
      }
    ],
    "why": "ph07 is `mbfl_strcut`'s mblen_table arm out of PHP 5.0.0, `ext/mbstring/libmbfl/mbfl/mbfilter.c:1179-1259`, corpus row CRASH-124, tier `narrowed`. THE IDIOM IS A CURSOR ADVANCED BY THE DATA WITH NO END TEST. `:1179` reads the true length into `len` and `:1202-1210` never looks at it: `for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }` -- the only exit is the accumulated count passing the caller's `from`, and `p` is never compared against `string->val + string->len`. The clamps at `:1227-1241` do use `len`, but they run AFTER the walk, which is after the over-read. \u2b50 AND THE SAME FUNCTION'S SECOND WALK IS BOUNDED: `:1213`'s `if (k >= (int)string->len)` means `:1217-1222` only ever runs while `n <= k < string->len`, so every byte IT reads is in range. One function, adjacent lines, one guarded search and one unguarded one -- that asymmetry is the row. \u26a0 THERE IS EXACTLY ONE LIMB AND IT IS A READ: after the clamps `0 <= start <= end <= len`, so the copy at `:1248-1252` is always in bounds however wild the walk was, and the returned value is UNAFFECTED by the out-of-bounds bytes (controls/fix_scope.py Q3: 0 of 15 333 over-reading calls move under seven different fillers, with a must-fire control at 13 293). That is why it shipped byte-identical in six releases. \u26a0 THE ZVAL TERMINATOR IS PART OF THE PROGRAM. `string->val` is a PHP string, `emalloc(len + 1)` with `val[len] == 0`, so a walk that reaches index `len` finds `mblen_table_utf8[0] == 1` and steps past `from`. Both upstream guards admit `from == string->len` for that reason, and `inputs/gen.py` writes the NUL into every window. \u26a0 R1h IS A TAGGED CONFIGURATION AND IT IS IN THE CALLER, IN ANOTHER FILE -- `php-5.2.12 .. php-5.2.17`, `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c`, body sha256 26e2099e33433c74, which is `cb3cca21b345` (2005-12-15) hunk (a) after `c2471b495009` (2009-09-23, bug #49354) removed hunk (b). That the fix is one file up is why `mbfl_strcut`'s body is byte-identical at NINE tags from php-5.0.0 to php-5.3.2. This row's `kernel()` wrapper IS that caller -- it already carries mbstring.c:1787-1805's two negative clamps, and the whole frame is pinned as `provenance.extra_spans[1]` -- so the guard lands in upstream's own position, immediately before the call at `:1807`. \u2b50 THE ROW SHIPPED BOTH HUNKS UNTIL TASK_PHP_018 AND ITS OWN GATE HAD SAID WHY NOT: `check.py` stage 7h refuses an R1h that changes benign output, hunk (b) changes it on 13.5 % of benign calls while removing none of the 15 333 over-reads, and the row read the refusal as a harness limitation and restricted the corpus instead. Upstream reached the same verdict from a bug report four years later. `idiom.required[4]` states the choice and the alternative; `forbidden[3]` pins hunk (b)'s two spellings absent; controls/bug49354.py replays upstream's own six expectations; c/kernel_hardened.c and NOTES.md \u00a74 state the residual fidelity question -- a subset of a labelled security fix, presented as an upstream configuration -- rather than smoothing it over. NAMED-SPELLING STANDARD -- POLICY ADOPTED AT TASK_018, AFTER the alternate spellings had been measured, and REPAIRED AT TASK_019 because TASK_018_REVIEW B1 measured that the version it replaced did not describe the shipped tree. It is NOT a disambiguation of what these entries always meant, and presenting it as one would be the self-certification this mechanism exists to prevent (TASK_017_REVIEW). The rule, and this paragraph is byte-identical in all six patterns' `why` -- diff them: where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract even when it is semantically identical and even when it compiles to the same bytes; a `forbidden` entry excludes the spelling it quotes, the same way. HOW A SPELLING IS MATCHED -- written down because `literal` never was, and twenty shipped obligations turned on the gap: a rung matches a quoted spelling when the spelling occurs in that rung's EXEC source after comments and string literals are blanked, after Verus ghost clauses are blanked, and after every whitespace character is deleted from both sides. That is `harness/check.py::spelling_matches`, selftested at gate stage 0 and therefore hashed into `source_sha256`, so the convention cannot drift while remaining an adjective. Each of its three parts was forced by a shipped cell, not chosen. (a) Whitespace is not a spelling: p17 declares `2 + 2*nsuf > len` and all six p17 rungs write `2 + 2 * nsuf > len`, which put six cells out of their own contract on two space characters. (b) A comment is not code: `patterns/p02-buffer-copy/c/kernel_hardened.c` and `patterns/p16-tlv-walk/c/kernel_hardened.c` each quote their own pattern's `forbidden` spelling inside the comment that explains why they do not use it, and `patterns/p17-http-range/c/kernel.c` would otherwise satisfy `2 + 2*nsuf > len` on the strength of a comment while its code writes the spaced form -- a match for the wrong reason is as bad as a miss. (c) Ghost is not exec: a Verus `requires`/`ensures`/`invariant`/`decreases` is erased before codegen and its arithmetic is over unbounded `int`, so it cannot carry the overflow an additive spelling is forbidden for; `patterns/p16-tlv-walk/verus.rs`'s loop invariant `p + 3 + vlen <= end` is the shipped instance, and without this part p16's own R5 violates p16's `forbidden[0]` on a grep. PER-LANGUAGE ENTRIES: an entry of `required` or `forbidden` may be an object keyed by language, with keys `c` and `rust`, instead of a string; each rung is then matched only against its own language's spelling. A plain string still applies to every rung and stays the right shape whenever one spelling covers all six -- which it does for p16's comparisons, so per-language is a tool and not a habit. THE CLAUSE THIS REPLACED IS RETRACTED, and so is the count that justified it. Until TASK_019 this paragraph read `where a rung's LANGUAGE cannot express the quoted spelling, that rung spells the same operands the way its language forces and nothing else varies`, justified by EIGHT SHIPPED CELLS. Both are wrong (TASK_018_REVIEW B1). The count was never eight: p08's `dr = d + r` carries no backticks and so was never pinned, and six p17 cells nobody had counted were out on spacing. TASK_018_REVIEW put the corrected figure at 10, or 4 once whitespace is normalised; measured against the WHOLE declaration rather than the two entries that review looked at, the pre-repair figure is 20 obligations failing on raw text, 15 once comments and ghost are blanked and 9 once whitespace is deleted. The five it adds are p17's `required[1]`, which quoted an ELLIPSIS -- `if start < end && start >= 0 { ... }` -- that no rung can contain, and which nobody had counted either. And the clause's antecedent is FALSE exactly where it was needed -- Rust CAN spell `len > src_len - (src_off + 2)`, and a p02 R3 variant that does is byte-identical to the shipped cell (`md5_fn e207ec6c8697...`, identical marginal on both bands), so the clause never fired for the four cells it existed to rescue. Per-language entries do that job, and they do it by NARROWING and not by widening: with p02's `required[0]` and `forbidden[0]` carrying Rust spellings, the shipped R3 matches and BOTH variants that are not it fail to match -- the forbidden additive guard, 3.00 Ir/call cheaper than shipped R3, and the byte-identical `src_len`-spelled guard -- where before the edit the pin matched none of the three and decided nothing at all. THE COUNT, MEASURED AFTER THE REPAIR RATHER THAN ASSERTED (TASK_019, `.temp/p19/pins.py`, a hand-transcribed table of every backticked spelling against every rung it scopes to): the repaired declaration makes 82 (spelling x rung) obligations across the six patterns, of which 11 fail on raw text, 6 once comments and ghost are blanked, and 0 under the rule above -- so NO shipped cell is out of its own declaration, and that is a count and not an adjective. The pre-repair declaration made 78 obligations and failed 20 / 15 / 9. The total ROSE because per-language entries pin MORE and not less: the Rust three-term guard `len > dst.len() || len > src.len() - (src_off + 2)` is now pinned where before only a sub-expression of it was. WHY IT WAS ADOPTED: TASK_017 applied this reading to p16 and refused it for p17 in the same commit, writing into p17's NOTES.md that a spelling with no `end` binding anywhere in its code satisfied entries naming `start < end` (TASK_017_REVIEW B1). One rule across all six is the repair, and it still holds `.temp/p05r3/v17/tuned_suffix.rs` out: every p17 rung binds `end`, so p17's entries name spellings its rungs really write and no per-language key rescues a variant that binds no `end` at all. TOKENS rather than SEMANTICS, for a reason that is checkable rather than rhetorical: only the token reading partitions cleanly. `.temp/p05r3/v16/tuned_split.rs` satisfies p16's `every comparison is subtraction-first` VACUOUSLY -- it contains no comparison at all -- and `tuned_splitat.rs`'s `rest.len() >= 3` is neither subtraction-first nor additive, so the semantic reading does not decide either of them (TASK_017_REVIEW m5). A contract a grep can settle beats a contract only an argument can settle -- WHERE a grep settles it, which is narrower than TASK_018 wrote. WHAT NO GREP SETTLES, recorded so nobody re-derives it: `required` in p01 and p05 contains no backticks at all, so those two patterns pin no token and their rungs are matched by prose only; and the POLARITY of a quoted span (p02's `|`, p08's `&` and p17's `continue` are quoted in order to be ABSENT) and the SET OF RUNGS it scopes to (p02's first entry, p16's fourth, p17's third) live in the entry's English. `spelling_matches` decides one spelling against one rung; which spelling and which rung is a reading, and no gate stage reproduces it. WHAT THE STANDARD DOES NOT BUY, measured and put here rather than in a footnote: a pinned idiom makes the admissible class DECIDABLE, not SINGULAR. Respelling only what the declaration leaves free moves p16's R3 by `4*nrec - 8` Ir/call, p17's by 51 flat and p02's by 3 to 4. THE UNSAFE SIDE DOES NOT MOVE, AND THE SENTENCE THAT SAID IT DID IS WITHDRAWN (TASK_028, on TASK_027_REVIEW's seven Verus twins). Until TASK_028 this paragraph read `and it moves the UNSAFE rung too, by the same lever: p16's R4 by 4*nrec (TASK_023) and p05's by 7 flat (TASK_022)`, and that names ONE lever -- respelling the header read -- which is NOT ADMISSIBLE ON EITHER PATTERN. All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies. At the pinned vstd every route to that respelling is `is not supported` -- `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`, `TryFromSliceError` and `from_le_bytes` -- so p16's `r4_hdr` and p05's `c4_hu16_nz` are controls and not rungs, and shipping either costs a NEW TRUSTED ITEM, which is exactly what disqualified `r4_hdr` on p16. `4*nrec` and `7 flat` are therefore both withdrawn, NEITHER PATTERN'S R4 SIDE HAS MOVED BY A SINGLE ADMISSIBLE INSTRUCTION, and the reason is this block's own `identity` pin rather than anything about those two patterns -- it binds all six, and p01's R2 as well, which is pinned the same way. Read the ERROR TEXT and not the exit code: `is not supported` disqualifies, because it is what forces a new TRUSTED item, while `postcondition not satisfied` disqualifies nothing -- the same p05 exec code went from `11 verified, 1 errors` to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB. THIS PROJECT PUBLISHES NO PAIR INTERVAL, and the two it did publish fall with that sentence: p05's `2*nrow - 2` ... `6*nrow + 20` (36...134 / 128...410, whose bottom endpoint was quoted as `exactly 0.00`) took its endpoints from `r4_dataslice` and `c4_hu16_nz`, and p16's from `r4_hdr`; none of the three is a rung. What ships is TWO quantities and not three. THE ONE REAL BOUND needs R4 held fixed BY FIAT rather than minimised: then, and only then, `R3ship - R4ship` bounds `inf(in-contract R3) - R4ship`. Beside it goes the R3-SIDE SPAN, cheapest-found to dearest-found in contract. A pair interval over the ADMISSIBLE class is not unavailable, it is DEGENERATE, which is the more informative thing to say and is why `unavailable` is not written here: the only p05 R4 SHOWN admissible is the shipped cell -- six more measure exactly R4ship and were never put through Verus, and the two that MOVE were put through it and failed -- so the R4 endpoint has ZERO measured width and the interval collapses onto the R3-side span, `5*nrow + 6` ... `6*nrow + 13` = 101...127 / 331...403, width `nrow + 7` = 26 / 72. That is p05's R3-side span exactly, i.e. a third NAME for a second NUMBER, so do not quote it as a pair result; it becomes one the day somebody builds an admissible R4 that MOVES, and on two patterns now -- p05's unbuilt zero-guard deletion and p16's unbuilt hand-unrolled 32x fold -- that is the open question and nobody has built it. And `min(R3 found) - min(R4 found)` is NOT the repair -- two upper bounds differenced bound nothing in either direction; on p05 one edit moved it -2 on R4 and +1 on R3, so the constant does not cancel (the R4 half of that illustration is an inference from the inadmissible `c4_hu16_nz` family and has never been compiled; the arithmetic point does not rest on it), and its third published minimum EXCEEDS its published figure at `nrow <= 3`. Every pattern owes an in-contract spread beside its headline; on the R3 side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from TASK_021 (their NOTES.md 10a / 14; 14 also measured that this audit CANNOT settle p05 -- its declaration backticks nothing, so `spellings` is 0 and admission is decided by prose plus one grep), on the R4 side ONLY p05 and p16, and p01 and p08 neither"
  },
  "verus": {
    "call_site": "main",
    "kernel_item": "kernel",
    "translate": {
      "buf@.len()": "buf_len",
      "buf@": "buf",
      " as int": "",
      "strcut_fold": "strcut_fold",
      "r": "result"
    },
    "obligations": {
      "verus.rs": 21
    },
    "twin_obligations": {
      "verus.rs": 24
    },
    "obligations_note": "21 verified / 0 errors, and 24 under `--cfg slb_twin` -- three trusted accessors, therefore three twins. The proof rests on two facts from two different places: `lemma_mbtab_pos` (every mblen_table entry is >= 1, so `n` strictly increases and the start walk has a `decreases` at all -- proved out of the LITERAL 256-byte table by `lemma_mbtab_matches`, `by (compute_only)` plus one induction, with NO assume and NO sixth trusted item), and `cb3cca21b345` hunk (a) (`from <= string->len`, which is what discharges every `get_unchecked`). `lemma_fold_shift` is the third lemma and says that folding the copy from the front is folding the source from `start`. \u2b50 The END walk needs neither: mbfilter.c:1213 bounds it in the 5.0.0 source already, so the proof obligation exists on one walk and not the other -- which is this row's finding, visible as an asymmetry in the proof.",
    "twin_obligations_note": "`verus.rs --cfg slb_twin`, where step 5c-twin checks the twins. 21 shipped + 3 for slb_twin_get_unchecked, slb_twin_vget_unchecked and slb_twin_vset_unchecked. \u26a0\u26a0 `#[verifier::rlimit(30)]` IS STILL ON THE KERNEL AND ITS JUSTIFICATION CHANGED AT TASK_PHP_018. It USED to be load-bearing: with cb3cca21b345 hunk (b) in the spec and the exec code the kernel needed ~10-12 plain and 15 under --cfg slb_twin, so at the default 10 it verified plain and FAILED twin. Removing hunk (b) made the proof CHEAPER on both sides -- one fewer branch on `length` in `strcut_fold` and one fewer in the kernel -- and the requirement is now 9 on BOTH: bisected at TASK_PHP_018, `20 verified, 1 errors` at rlimit 8 and `21 verified, 0 errors` at 9 plain, `23 verified, 1 errors` at 8 and `24 verified, 0 errors` at 9 twin (.temp/php18/rlimit-sweep.log). \u26a0 So both sides now pass at the DEFAULT -- with a margin of ONE, which is the width of a coin flip and is why the override stays rather than being deleted. 30 is 3.3x the measured requirement. NOTES.md \u00a710 has the numbers and the reduction that came first.",
    "items": {
      "verus.rs": {
        "mbtab_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "mbtab_matches_upto": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_mbtab_elim": {
          "external": null,
          "requires": [
            "mbtab_matches_upto(n)",
            "0 <= k < n"
          ],
          "ensures": [
            "MBTAB@[k] as int == mbtab_of(k as u8)"
          ]
        },
        "lemma_mbtab_matches": {
          "external": null,
          "requires": [],
          "ensures": [
            "MBTAB@[b as int] as int == mbtab_of(b)"
          ]
        },
        "lemma_mbtab_pos": {
          "external": null,
          "requires": [],
          "ensures": [
            "mbtab_of(b) >= 1"
          ]
        },
        "head_u32": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "guard_from": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "guard_len": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk_start": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk_start_dec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk_end": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "walk_end_dec": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "fold_out": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "tally_of": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "strcut_fold": {
          "external": null,
          "requires": [],
          "ensures": []
        },
        "lemma_fold_shift": {
          "external": null,
          "requires": [
            "0 <= ao",
            "0 <= n",
            "ao + n <= a.len()",
            "n <= b.len()",
            "forall|t: int| 0 <= t < n ==> a[ao + t] == b[t]"
          ],
          "ensures": [
            "fold_out(b, 0, n, acc) == fold_out(a, ao, ao + n, acc)"
          ]
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
        "mbtab": {
          "external": null,
          "requires": [],
          "ensures": [
            "r as int == mbtab_of(b)",
            "r >= 1"
          ]
        },
        "tally": {
          "external": null,
          "requires": [],
          "ensures": [
            "r == tally_of(cap as int)"
          ]
        },
        "kernel": {
          "external": null,
          "requires": [
            "off + len <= buf@.len()",
            "9 <= len"
          ],
          "ensures": [
            "r == strcut_fold(buf@, off as int, len as int)"
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
        "vset_unchecked": "`x: u8` is a PURE VALUE and needs no precondition. The unchecked operation is `*v.get_unchecked_mut(i) = x`: its definedness depends on `i` being in bounds and on `v` being a live `Vec<u8>`, and on NOTHING about the byte being written -- every one of the 256 values of `x` is a legal `u8` store into a byte that is already initialised (`vec![0u8; cap]` initialised the whole buffer before the first call site is reached). Contrast the shape this stage exists to catch, `requires n >= 0` on a `usize`: there the unconstrained parameter was the one the body indexed with. Here the indexing parameter `i` IS constrained, by `i < old(v)@.len()`, and the `ensures` names `x` in the post-state -- `final(v)@ == old(v)@.update(i as int, x)` -- so a body that stored anything other than `x`, or stored it anywhere other than `i`, could not satisfy its own postcondition."
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
      "if stride_w >= 9 && stride_w <= n_blob",
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
    "note": "marginal Ir = (Ir at 200 iterations - Ir at 100 iterations) / 100, a difference of two runs of the same binary so the one-shot loader terms cancel. They do NOT cancel exactly -- see p01's copy of this note for the environment-block and build-to-build residuals, measured at ~0.1 and ~0.2 Ir respectively. ph07's two probe shapes have different work per call (553 and 4074 window bytes) so check.py can also assert d(Ir)/d(work) >= ALPHA. THE FLOOR IS NOT DECLARED HERE: check.py derives it as ALPHA_IR_PER_WORK * model.work_per_call. \u26a0 `work_per_call` is the WINDOW and the kernel touches `from` + up to `length` + `end - start` of it, all three read out of the data; inputs/gen.py draws `from` and `length` as fixed FRACTIONS of the window so the work really does scale with the denominator. Each call also does one `mbfl_malloc` + one `mbfl_free` + one `php_shim_reset` on the C side and one `vec![0u8; cap]` on the Rust side, so a fixed per-call term is present in every rung and the marginal is NOT a pure walk rate; NOTES.md \u00a78 decomposes it."
  },
  "identity": [
    {
      "a": "unsafe",
      "b": "verus",
      "O0": "differ",
      "O3": "norel",
      "why": "R4 == R5 at O3 UP TO RELOCATIONS, and `norel` is the honest level rather than `exact`. Measured, `results-php/ph07-strcut-cursor.json`, O3/isolated: 255 instructions and 953 bytes in BOTH cells, `md5_fn_norel` identical at `702235d5f057...`, and `md5_fn` DIFFERENT (`b20b2fd9aa42e532` vs `b3ecc80e00209841`). The proof licenses the two walks' unchecked reads, the unchecked copy and the unchecked fold at ZERO instructions; what differs is the relocation bytes of the `memcpy@GLIBC_2.14` call, because the two crates lay their PLT out differently. ph03 pins `exact` at O3 because its kernel calls out to nothing; ph07's copies with a bulk call and therefore cannot. \u26a0 AT O0 THE TWO GENUINELY DIFFER -- 442 vs 464 instructions, 2530 vs 2683 bytes, and `md5_fn_norel` differs too. At O0 nothing is inlined, so R5's four trusted wrappers and its `mbtab` accessor survive as real calls where R4 open-codes them; that is codegen, not layout. \u26a0 In `whole` mode the two differ at BOTH levels (875 vs 888 instructions at O3) because the whole-program symbol absorbs different amounts of the driver; the pin is about the `isolated` cells, where the kernel is a symbol of its own."
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
    "reason": "`.memory/02-bench-rules.md` makes Miri mandatory for any pattern with a trusted `unsafe` item, and check.py derives that from verus.rs rather than from this flag. ph07 has THREE such items and one of them WRITES (`vset_unchecked`): a trusted `ensures` need not be COMPLETE with respect to what the body does, and a write wrapper whose `ensures` named only `v@[i] == x` would let a body that also clobbered `v[i+1]` through every Verus stage. The shipped `ensures` is the whole post-state, `old(v)@.update(i, x)`, and Miri is the backstop for the class regardless. \u26a0 It matters more here than on a row whose unchecked reads are index-bounded by a literal: ph07's are bounded by `from <= string->len`, a fact that comes from a 2005 upstream patch, so an editor who removed that patch would be removing the precondition of three `get_unchecked` sites at once.",
    "blocked_reason": "miri is installed on the nightly toolchain beside the pinned one (TOOLCHAIN.md). check.py rewrites n_iters to 4 for every Miri run, so ph07's cost is 4 x (one window walked and copied), i.e. 4 x 4074 bytes at worst -- three orders of magnitude inside the 180 s budget. A timeout is recorded as a BLOCKED row for that input, never as a pattern failure."
  },
  "provenance": {
    "php_version": "5.0.0",
    "tarball_sha256": "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919",
    "c_file": "ext/mbstring/libmbfl/mbfl/mbfilter.c",
    "c_lines": [
      1179,
      1259
    ],
    "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/mbfl/mbfilter.c | sed -n '1179,1259p'",
    "extract_sha256": "5edc6c04b7ff5f64255ae6b01d17f0a4e3afe9ec54525f97cbd703a91c451f55",
    "extra_spans": [
      {
        "c_file": "ext/mbstring/libmbfl/filters/mbfilter_utf8.c",
        "c_lines": [39, 56],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/libmbfl/filters/mbfilter_utf8.c | sed -n '39,56p'",
        "extract_sha256": "716ba3fb219d4fb457ce115accd72be9cc2334d62cd82ab34ead4d078084e7c1",
        "why": "`mblen_table_utf8`, the 256-byte step table both C rungs and all four Rust rungs carry verbatim. It is STATIC DATA in PHP -- a field of a `const mbfl_encoding` (mbfilter_utf8.c:58-65) -- not input, and an attacker cannot choose it. Disclosed as divergences[6] since the row was built; PINNED here since TASK_PHP_018, which is what divergences[6] said was owed."
      },
      {
        "c_file": "ext/mbstring/mbstring.c",
        "c_lines": [1774, 1812],
        "extract_cmd": "tar -xzOf <tarball> php-5.0.0/ext/mbstring/mbstring.c | sed -n '1774,1812p'",
        "extract_sha256": "4ef738b3546c31c1adfd41e4b214c0082c16d72138917a336848cacfa85c41fb",
        "why": "\u26a0\u26a0 THE CALLER FRAME, AND IT WAS LIFTED AND DISCLOSED NOWHERE AS A SPAN UNTIL TASK_PHP_018 (TASK_PHP_017 M1, RECAP_PHP.md open item 25). `PHP_FUNCTION(mb_strcut)`'s body from the zval unpack to RETVAL_FALSE: c/kernel.c's `kernel()` wrapper IS this code -- the `int` truncation of the two `long`s, the two negative clamps at :1787-1805, the call at :1807 and the two return arms at :1809-1812. \u2b50 AND IT IS THE FRAME R1h OCCUPIES: cb3cca21b345 patches THIS function, not `mbfl_strcut`, so with only the mbfilter.c span pinned the overlap report certified a span containing neither the fix nor the frame the fix goes in. The end of the span is :1812 and not :1813 because :1813 is the closing brace of `PHP_FUNCTION`, which the wrapper does not lift."
      }
    ],
    "extra_spans_note": "\u26a0\u26a0\u26a0 THE ROW LIFTS THREE SPANS AND PINNED ONE UNTIL TASK_PHP_018. `provenance.c_lines` names the walk (mbfilter.c:1179-1259); the row also lifts the step table and the caller frame, and the caller frame is where R1h lives. The 75 % (39/52) overlap this row published was therefore computed against a third of what it cites. `extra_spans` is a harness-php/provenance.py schema addition and costs NO PAT re-gate; it is deliberately ADDITIVE, so the primary four fields do not move and ph03 and ph00-smoke are byte-identical -- making `c_lines` a list of lists would have moved every row and still not expressed this shape, which is three spans in THREE DIFFERENT FILES. Each entry is checked exactly as the primary is (in the manifest, in range, canonical extract_cmd, extract_sha256 over the bytes `sed` prints), and the kernel overlap is now computed over the UNION.",
    "tier": "narrowed",
    "divergences": [
      {
        "what": "the mbfl_no2encoding() lookup and its NULL test",
        "kind": "deletion",
        "where": "mbfilter.c:1169-1172",
        "why": "the kernel is compiled for ONE encoding, UTF-8, whose `mbfl_encoding` record is a compile-time constant (mbfilter_utf8.c:58-65): mblen_table_utf8, flag MBFL_ENCTYPE_MBCS. Resolving a constant at build time instead of run time is exactly the wrapper removal `narrowed` names. No semantics."
      },
      {
        "what": "the MBFL_ENCTYPE_WCS2* and MBFL_ENCTYPE_WCS4* arms",
        "kind": "deletion",
        "where": "mbfilter.c:1182-1193",
        "why": "`else if`s on `encoding->flag`, and UTF-8's flag is MBFL_ENCTYPE_MBCS (mbfilter_utf8.c:63), so on this kernel's domain they are DEAD and the surviving `else if (encoding->mblen_table != NULL)` is the arm reached. Verified at source in the tarball. No semantics on the extracted domain."
      },
      {
        "what": "the wchar filter-chain else arm",
        "kind": "deletion",
        "where": "mbfilter.c:1260-1361",
        "why": "the `mblen_table == NULL` path -- libmbfl's filter-chain object model, which is what the corpus's kill sentence was about. This kernel always has a table, so the arm is unreachable. No semantics on the extracted domain."
      },
      {
        "what": "mbfl_string narrowed to {val, len}",
        "kind": "deletion",
        "where": "ext/mbstring/libmbfl/mbfl/mbfl_string.h:41-46",
        "why": "`no_language` and `no_encoding` are inputs to the encoding lookup removed above and are read nowhere in :1179-1259. No semantics."
      },
      {
        "what": "mbfl_string_init(result) inlined as its two stores",
        "kind": "deletion",
        "where": "mbfilter.c:1173",
        "why": "the function is in mbfl_string.c, outside the cited span; it clears the four fields and this struct has two. No semantics."
      },
      {
        "what": "mbfl_malloc -> php_shim_emalloc, mbfl_free -> php_shim_efree",
        "kind": "substitution",
        "where": "mbfilter.c:1245 (mbfl_malloc); the mbfl_free is in the wrapper",
        "why": "these are NOT plain malloc: mbfl_allocators.h:48 defines mbfl_malloc as `(__mbfl_allocators->malloc)` and mbstring.c:764 points __mbfl_allocators at _php_mb_allocators, whose malloc is `emalloc` (mbstring.c:240-243) and whose free is `efree` (:255-258). common-php/emalloc_shim.h is PHP 5.0.0's own _emalloc/_efree, line-cited to the same tarball (PLAN_PHP.md 4.3). No semantics."
      },
      {
        "what": "mblen_table_utf8 lifted as a file-scope static const",
        "kind": "substitution",
        "where": "ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56",
        "why": "in PHP it is reached as `encoding->mblen_table`, a field of a `const mbfl_encoding`; here it is the array itself, byte-identical (diffed against the tarball). \u2b50 It is a SECOND span, and TASK_PHP_018 PINNED IT: `provenance.extra_spans[0]`, hashed and checked like the primary. Until then it was disclosed here and cited nowhere the validator could reach -- the gap TASK_PHP_015 2.5 deferred as a schema decision. model.py::selfcheck check 5 parses the 256 numbers out of c/kernel.c and compares, and verus.rs's lemma_mbtab_matches proves the closed-form spec equals all 256 mechanically. No semantics."
      },
      {
        "what": "the emalloc NULL arm",
        "kind": "projection",
        "where": "common-php/emalloc_shim.h, _emalloc's :189-198 projection",
        "why": "PHP prints to stderr and exit(1)s; the shim returns NULL and the caller decides, because a kernel that exits turns a measurement into a build failure. DECLARED per emalloc_shim.h's own instruction. ph07 cannot reach it: `n = end - start` is clamped to `string->len` before `mbfl_malloc((n + 8))`, so the request is at most the window plus eight."
      },
      {
        "what": "the Rust rungs spell the caller's clamps in usize with saturating_sub/saturating_add",
        "kind": "substitution",
        "where": "ext/mbstring/mbstring.c:1787-1805 and cb3cca21b345",
        "why": "the C rungs write mbstring.c's `int` arithmetic verbatim; the Rust rungs cannot, because Verus has no `slice.len() <= isize::MAX` fact and a signed round-trip is not total. DEMONSTRATED behaviour-preserving by controls/guard_equiv.py: 0 disagreements over 5 122 (slen, from, length) triples against a build of the C itself, with three must-fire mutants at 2 376 / 269 / 509. \u26a0 TASK_PHP_018: `saturating_add` no longer appears in this clamp at all -- it spelled cb3cca21b345 hunk (b), which upstream withdrew and this row no longer ships -- so what remains here is `saturating_sub` in the two negative clamps, plus the `start.saturating_add(length)` at mbfilter.c:1212 that is a different statement. The control still compares BOTH configurations and adds an eighth case, `hb`, which scores the withdrawn two-hunk spelling against the shipped column and MUST FIRE: 1 134 of 5 122. No semantics on this kernel's domain."
      },
      {
        "what": "the Rust rungs rotate the start walk",
        "kind": "substitution",
        "where": "mbfilter.c:1202-1210",
        "why": "the C keeps `for (;;)` verbatim in both C rungs; the Rust rungs read once and then `while n <= from`, which performs the same reads in the same order and assigns the same `start`. It is the shape LLVM produces from either spelling and the one Verus can carry an invariant across. No semantics."
      }
    ],
    "divergences_note": "`kind` is one of deletion / substitution / projection and is DECLARED, NEVER DETECTED -- provenance.py does not read this block at all (PROTOCOL_PHP.md D). Nothing may come to depend on it. \u26a0 Three of these ten entries are DOMAIN RESTRICTIONS written as deletions (the WCS arms, the else arm, the encoding lookup), and PROTOCOL_PHP.md A2 says a deletion that changes behaviour is a `modelled` tier -- so the argument is written out in each `why` and rests on one checkable fact: UTF-8's mbfl_encoding record has a non-NULL mblen_table and flag MBFL_ENCTYPE_MBCS, verified in the tarball at mbfilter_utf8.c:58-65.",
    "root_cause_ids": [
      "mb_strcut-from-offset-exceeds-strlen-wchar-branch-walks-past-buffer-oob-read"
    ],
    "cwe": "CWE-125",
    "cwe_note": "index.csv records CWE-125 and this row reproduces exactly that and nothing else: `heap-buffer-overflow READ of size 1` at c/kernel.c:171 = mbfilter.c:1203, `0 bytes after` the blob. \u2b50 Unlike ph03 there is no second limb to adjudicate -- the clamps at :1227-1241 force `0 <= start <= end <= len`, so the copy cannot leave the buffer however wild the walk was. \u26a0 The corpus's own root_cause_id says `wchar-branch`, and that is wrong about which arm: the defect is in the mblen_table arm (:1194-1225); the wchar branch is the `else` at :1260+ and has no such walk. The `c_file_line` field is right (`mbfilter.c:1203 (OOB read site); missing guard at ext/mbstring/mbstring.c:1807`) and is what this row cites.",
    "fix_commit": "cb3cca21b34518caf45852ed90597052e99294c3",
    "fix_commit_removal": "c2471b4950091c71da5e3f686d6d455e8e3092ea",
    "r1h_configuration": {
      "tags": "php-5.2.12 .. php-5.2.17",
      "function": "PHP_FUNCTION(mb_strcut), ext/mbstring/mbstring.c",
      "body_sha256_16": "26e2099e33433c74",
      "body_bytes": 1823,
      "respelled_as": "php-5.3.2 .. php-5.3.29, body sha256 49ad3ab2796d63e4, `(unsigned int)from > string.len`"
    },
    "fix_commit_note": "\u26a0\u26a0\u26a0 TWO COMMITS AND ONE CONFIGURATION, AND R1h IS THE CONFIGURATION. `cb3cca21b345` -- Ilia Alshanetsky, 2005-12-15, 'Fixed possible memory corruption inside mb_strcut().', ext/mbstring/mbstring.c, +7 lines, ONE hunk, TWO guards. First shipped in php-5.1.2 (2006-01-12); php-5.0.x never received it. Patch bytes at controls/cb3cca21b345.patch, 829 bytes, sha256 14dbafc9a3b970d048e0a24347c503b436c51d15e5fb382427be2bece5353b64. The corpus's index.csv names this commit in its `fix_commit` column. `c2471b495009` -- Moriyoshi Koizumi, 2009-09-23, 'Fixed bug #49354 (mb_strcut() cuts wrong length when offset is within a multibyte character).', -3 lines: it REMOVES hunk (b) and adds ext/mbstring/tests/bug49354.phpt, a regression test whose --EXPECT-- block pins six answers. Patch bytes at controls/c2471b495009.patch. \u2b50 It was committed THREE times in the same second -- c2471b495009, 0c974164e248 and ce3c028803aa, one per live branch -- so the removal is not one branch's local decision. \u26a0 Its message blames 'the commit by r202895'; TASK_PHP_018 could NOT resolve that SVN revision to a git sha (php-src's converted history carries no git-svn-id trailer and svn.php.net no longer resolves), so the attribution is UNVERIFIED and is not relied on. What IS measured is the code: the three lines removed in 2009 are byte-identical to three of the seven added in 2005, and the function carries them continuously at every tag from php-5.1.2 to php-5.2.11. \u26a0 Guard (a) is the memory-safety half and guard (b) is not: (a) alone removes all 15 333 out-of-bounds reads over 133 932 interpreted calls, and (b) CHANGES BENIGN OUTPUT on 15 870 of 117 612 calls that never crashed (controls/fix_scope.py). controls/bug49354.py replays upstream's six expectations: (a) alone agrees on all six, (a)+(b) is wrong on one, R1 over-reads on one. \u26a0\u26a0 IT IS IN THE CALLER, IN ANOTHER FILE: PHP_FUNCTION(mb_strcut), not mbfl_strcut -- which is why mbfl_strcut's body is byte-identical (sha256 613648930a3d2551...) at php-5.0.0, 5.0.5, 5.1.0, 5.1.1, 5.1.2, 5.2.17, 5.3.0, 5.3.1 and 5.3.2. NINE tags, not six: the row said six and TASK_PHP_017 m3 measured nine. That caller frame is pinned as extra_spans[1] since TASK_PHP_018. \u2b50 AND THE BOUND CAME BACK A SECOND TIME, INSIDE AN UNLABELLED REWRITE: d9dda48f8a7e (2010-03-12, '- Update the bundled libmbfl to the latest on upstream', 64 files, +3435 -4164, no security label, no bug number) gave mbfl_strcut a prologue clamp of its own, first shipped in php-5.3.3. So the LIBRARY function was unsafe for any other caller for four years and three months after mb_strcut was fixed. That patch's mbfilter.c half is at controls/d9dda48f8a7e-mbfilter.patch (full patch sha256 d8a52e5cf0375d6cc6dea95ce8f56234a9f8835799435abd4a8409190a06bb0d).",
    "invariant": "I1",
    "obligation": "O1",
    "echoes": [
      "p16"
    ],
    "echoes_note": "p16-tlv-walk is the closest PAT analogue -- a length read out of the data driving a cursor -- and PLAN_PHP.md 3.1 makes the overlap a CROSS-REFERENCE and never a filter. \u26a0 The mechanisms differ where it matters: p16's walk has a bound in its signature and does not look at it; ph07's bound is inside the object and is consulted AFTER the walk instead of during it, and the same function's second walk consults it correctly.",
    "uses_allocator": true,
    "uses_allocator_why": "c/kernel.c calls php_shim_emalloc once and php_shim_efree once per call, for `mbfl_malloc((n + 8) * sizeof(unsigned char))` at mbfilter.c:1245 -- and that IS PHP's allocator on this path (mbstring.c:764 points libmbfl's allocator vtable at emalloc/efree). \u26a0 The truncations are NOT the defect here: `n = end - start` is clamped to `string->len` first, so `cap` is at most the window plus eight and T1/T2/T3 all sit ~2^40 below their moduli. The tally is folded into the checksum so a rung that sized the result differently cannot agree by accident, and the Rust rungs reproduce it ARITHMETICALLY -- which pins the SIZE across rungs and is NOT evidence that any Rust rung ran PHP's allocator."
  }
}
```
