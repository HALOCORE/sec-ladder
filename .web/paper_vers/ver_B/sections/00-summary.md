%% ver_B -- the briefing.  No \section, no number: it precedes section 1.
%%
%% THE DONE-TEST FOR THE WHOLE PAPER lives here.  Hand this file, alone and on
%% paper, to a developer who has never heard of this project: they must be able
%% to name three things they would do differently on Monday.  Everything about
%% the file's shape follows from that.
%%   - no \ref and no \pat: it has to work detached from the paper;
%%   - no `abstract` environment: an abstract is read as a summary of a paper,
%%     and this is a briefing about the reader's codebase;
%%   - none of the paper's vocabulary -- the three words section 4 earns are not
%%     earned here, so they are not used here;
%%   - every item is three things and nothing else: a bolded claim, one number
%%     carrying its own scope, and the action it implies.  Where the claim is
%%     already an imperative, the action sentence is deleted rather than
%%     restated -- that is where most of the word budget came from.
%%
%% Item 5 is scoped to ONE pattern deliberately (.temp/verify/RULINGS.md R3):
%% across the 25 patterns with a hardened build the hardened-minus-plain delta
%% runs from -125 to +10242 under gcc, so "hardening is cheap" is false as a
%% corpus claim.  What survives is: writing the check is cheap where the check
%% is all you are adding.  The corpus median goes in the same sentence.
%%
%% Item 2 quotes BOTH safe spellings (RULINGS R2).  The spelling that shipped is
%% the dearest of four found in contract; quoting only it would be the same
%% one-endpoint move section 2 tells the reader to refuse.
%%
%% Item 7 carries the bitset index, the range parser and the constant-time
%% compare.  It does NOT carry the recursive kernel that verifies and then
%% overflows the stack: RULINGS R1 went to the primary artefacts and there is no
%% such pattern -- it is a refused catalogue candidate whose sources do not
%% survive a clone.  The three that remain ladder by what the failing guarantee
%% covers: the value computed, the data you were handed, the execution trace.
%%
%% Item 7's PROVENANCE CLAUSE is not optional (REVISE A5).  All three are
%% one-edit mutants of proved kernels, and `controls_json` is `{}` on 25 of the
%% 26 gate records, so no gate certifies any of them.  The file has to work
%% detached, so it cannot borrow section 4's provenance sentence.  And the range
%% parser is worded per RULINGS R7-CORRECTED: the disclosure is the CROSSWIN
%% pair, not `adversarial-leak`, whose excess bytes are the attacker's own
%% request table.
%%
%% Item 8 is not a hedge and is not written as one.  It is what stops the seven
%% items above it being misquoted, and it ships the DIRECTION of each limit.

You have a C or C++ codebase and somebody has proposed rewriting part of it in
Rust. Here is what \num{totals.patterns} common C patterns, rebuilt at five
levels of safety across \num{totals.cells} measured builds, say about that.

1. **Ask where the bound comes from before you count bounds checks.** A bounded
   stack's safe-versus-unsafe gap runs 3 instructions per executed pop, +626 per
   call on its large input; one provably dead line hands the optimiser the
   invariant and the per-pop gap becomes exactly zero, across 19 input sizes.
2. **A bound the compiler cannot derive is a real per-element tax.** A binary
   search pays 6 instructions per probe as shipped, 5 in the cheapest safe
   spelling found; the shipped one is 42.5–46.6 % of a kernel that does nothing
   else. Take the fraction of your own.
3. **Never quote a Rust-versus-C number without asking which safe Rust.** A
   mechanical port pays a median 7.26× the safety tax a tuned rewrite of the
   same kernel pays, across 17 comparable rows — and the port is what most
   benchmarks measure.
4. **A quiet sanitizer is not evidence.** Of \num{totals.plain_c.deviating} rows
   where plain, unchecked C misbehaved on hostile input,
   \num{totals.plain_c.silent_first} were silent in at least one build, and
   \num{totals.plain_c.loud_first_silent} even when a crash in any build is
   allowed to outrank silence: exit 0, plausible wrong answer, no diagnostic.
   Put a known-bad input in the sanitizer job and fail the build on silence.
5. **If you are not rewriting it, harden it — on outcomes these measurements
   cannot tell hardened C from Rust.** Every rung above plain, unchecked C
   matched the reference model on every hostile input. On a buffer copy, where
   the check is all that differs, it costs +5 instructions per call under gcc
   and +12 under clang; across 25 hardened patterns the median is 24 and the
   range is wide.
6. **A proof costs nothing at runtime and about four times the source.** Proved
   and unproved kernels execute identically, byte-identical on
   \num{totals.identity_exact} of \num{totals.patterns} patterns; the proof text
   is \num{totals.proof_text.ratio_pct} % of the unsafe source, raw lines.
7. **Verified is not done.** Changing `>> 6` to `>> 7` in a bitset index leaves
   a legal index, so the bounds check, ASan, Miri and the proof all report
   nothing; a range parser handed a whole response buffer folds a neighbouring
   client's bytes into its answer, and the memory-safe and the proved versions
   of it do it too; a constant-time compare leaks through instruction count.
   Each is a one-edit mutant of a proved kernel, rebuilt from that pattern's
   committed sources and certified by no gate. Name what each mechanism covers.
8. **Read this before quoting anything above.** Zero of \num{totals.patterns}
   patterns creates a thread, so nothing here is evidence for or against
   fearless concurrency. Every figure is executed instructions per call, not
   seconds. Per-call constants transfer to your code; fractions of our kernels
   do not.
