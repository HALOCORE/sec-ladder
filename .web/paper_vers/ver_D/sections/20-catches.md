%% Story 3.  The longest section, and the one all four cold readers asked for and
%% never got: "I'd trade every gloss of blob for one sentence each on the four
%% detectors."  Spend the words here.
%%
%% ⚠⚠ THE PLAN THIS DESCENDS FROM STATED THIS STORY WRONG.  It said "and the
%% proof is happy too".  FALSE.  The proof CATCHES it -- until the specification
%% inherits the bug, which is the better story and the one written here.
%% Everything below is FACTS.md G, re-verified at source.
%%
%% THE TRANSITION IS THE RISKIEST MOMENT IN THE POST.  Do NOT open with "here is
%% a different program"; a cold reader on exactly that move said "I could not see
%% why I needed to know they were two programs and not one."  Bridge on the
%% SANITIZER instead: same tool, caught the record walker, blind to this.  That
%% turns two anecdotes into a controlled pair, and the reader is not being asked
%% to drop a program -- they are being asked what the tool was watching.
%%
%% START FROM THE VERSION THAT HAS THE GUARD.  The shipped plain-C kernel of this
%% pattern is missing `if (q < nbits)` -- that is a DIFFERENT designed bug.  All
%% the mutants are generated off the guarded versions.  Never "the shipped C
%% kernel plus one character".
%%
%% THE LOAD-BEARING GLOSS OF THE WHOLE POST is what a specification is and how it
%% differs from the code.  The punchline rests entirely on it.
%%
%% ⚠ ZERO VERIFIER COUNTS, here or anywhere.  "It will not build" plus the real
%% error text carries strictly more meaning than "9 verified, 1 errors", which a
%% reader cannot interpret and which counts items rather than conditions.  There
%% is no saved transcript for this pattern's counts anyway.
%%
%% ⚠ The two things that may not be smoothed (FACTS.md G4) are here, but NOT as
%% "two qualifications": the proof-hint clause is welded INSIDE the sentence that
%% says the prover refuses, and "moving the spec is not one character either" is
%% promoted to the punchline, where it is the point rather than a retraction.
%% Written as a list they run 110 words and produce three consecutive reversals
%% where attention is thinnest.
%%
%% ⚠ Do not add "the type system" to the instrument table; there is no evidence
%% in the tree for it as a separately measured instrument.  Do not say "wrong on
%% every input" -- it is four of the five shipped ones.
\section{One character, still inside the array, and almost nothing sees it}
\label{sec:catches}

Go back to that sanitizer, because the interesting question is what it was watching. It caught the record walker instantly, and it caught it because the program read a byte outside its allocation — leaving an allocation is precisely the event a sanitizer exists to notice. So here's a bug that never does that.

%% ⚠ Tightened, ~25 words, no content lost.  `q & 63` picking the bit within the
%% word is never used again and the story is entirely about the WORD index; the
%% two sentences about what the program reads collapse into the sentence that
%% introduces the code.
A bitset stores a huge pile of yes/no answers cheaply: one bit per member, packed sixty-four to a machine word. Is this identifier on the blocklist, is this page already fetched — you look up one bit and something acts on the answer. To find bit `q` you go to word number `q >> 6`, which is `q` divided by sixty-four.

The program reads a bit count and a list of queries out of a file. Here's the real line that answers one, from the tuned safe version, with the guard above it that keeps `q` inside the set:

```rust
        if q < nbits {
            let w: u64 = load_u64(win, ws + (8 * (q >> 6)) as usize);
```

Now type a `7` where the `6` is. One character. Dividing by a hundred and twenty-eight instead of sixty-four gives a smaller word number, and a smaller number cannot overshoot where the right one did not, so the index is still inside the array. It's the wrong word, not an illegal one. The program reads it, answers the query, and exits 0.

%% ⚠ COMPRESSED, ~12 words.  The SCOPE IS THE POINT AND SURVIVES INTACT: four of
%% five, not five of five.  The gate record's own `why` prose says "a different
%% answer on `small` and on every other blob", which is wrong — NOTES.md:842 and
%% :786 both record `adversarial-count` matching, because that input declares a
%% shape the window cannot hold so every build returns 0 before the query loop.
%% Do not let a later pass "simplify" this back to "wrong on every input".
On four of the five inputs shipped with that program the answer is wrong. On the fifth every version returns 0, correct ones included — that input never reaches the query loop at all.

%% ⚠⚠ FACT-CHECK 10 AND 12, TWO SCOPES, BOTH BINDING UNDER CLAIMS.md §1.17-18.
%% "We pointed everything at it" collapsed FOUR DIFFERENT BINARIES into one: the
%% bounds-check verdict is on the safe-Rust mutants, the sanitizer verdict is on
%% the HARDENED C one at gcc `-O1` (p09/NOTES.md:831-843; gen_controls.py:429,
%% 452-456), and Miri ran the UNSAFE Rust one (p09/NOTES.md:855-857).  CLAIMS.md
%% §1.17 -- the sanitizer numbers are one build configuration, C only, no Rust.
%% §1.18 -- Miri only ever runs the unsafe rung.  "the same character, in each
%% version's own copy" discharges both in seven words.
%% ⚠ MIRI'S SCOPE AND ITS VERB.  It ran on THREE inputs, not every one
%% (p09/NOTES.md:855-857), where the sanitizer row beside it does say every one.
%% And CLAIMS.md §1.11 requires "Miri reported nothing", NEVER a clean verdict in
%% our own voice: the draft's "reports nothing, because there's none to find"
%% asserted the absence rather than the silence.  Both fixed.
We put the same character into each version's own copy and pointed everything this project has at the result. Rust's own bounds check never fires, because the index is legal. The sanitizer — run here on the C copy — is silent on every input, for the same reason: nothing left the allocation. And Miri, an interpreter that runs Rust hunting for undefined behaviour, the class of mistake where the language stops promising anything about what happens next, exits 0 on the three inputs it was given and reports nothing.

| what we pointed at it | what it did |
|---|---|
| the bounds check safe Rust compiles in | never fires; exit 0, wrong answer |
| the sanitizer, on the flags the gate itself uses | silent on every input; exit 0 |
| Miri | exit 0, reported nothing, wrong answer |
| the proof, with only the memory rules written down | verifies the buggy version |
| the proof, with the answer written down too | refuses to build: `invariant not satisfied` |

The last two rows are the story, and they need one term. A proof here means somebody also wrote a specification: a separate statement, in logic rather than in Rust, of what the function must do, which the prover — the program that checks the argument — has to reconcile with the code. Part of it is about memory — this index stays inside that buffer. Part of it is about the answer — what the function returns is bit `q` of the set the file described. Different sentences, and you can have one without the other.

With only the memory part present, the prover cheerfully certifies the typo, because the typo breaks no memory rule. %% ⚠ SPLIT IN TWO.  This was ~45 words carrying two glosses and a mandated
%% qualification at once, at the point the section is densest — the writer flagged
%% it as the likeliest place a cold reader slows down.  NOTHING IS DROPPED: the
%% `invariant` gloss and the extra-hint qualification both survive, and the
%% qualification is still welded to the claim it modifies rather than filed after
%% it as a retraction (which is the rhythm that kills attention here).
%% ⚠⚠ FACT-CHECK 11.  THE HINT QUALIFICATION GOVERNED THE WRONG ROW, and moving
%% it is the difference between a true sentence and a flattering one.  It used to
%% sit only on "it refuses" -- but gen_controls.py:356-362 builds the
%% memory-rules-only variant FROM the hinted one, so BOTH proof rows carry the
%% same added `assert((q >> 7) <= (q >> 6)) by (bit_vector)`.  The pure
%% one-character mutant, `m_shift7_bare`, is 17 verified / 1 error and fails on a
%% PRECONDITION (p09/NOTES.md:691, 748-751) -- so without the hint the
%% memory-only proof does NOT cheerfully certify the typo either.  Attached to
%% one row it made the prover look better than the evidence does; attached to
%% both, the contrast between the rows is what survives, which is all the story
%% ever needed.  NOTES.md:752: "Quote the `fixshift` and `m_shift7` rows, never
%% the bare ones."
Both of those rows carry one extra line of hint that the shipped program never needed. Take it away and the prover balks either way, for a reason about the proof rather than about the bug — so what is worth reading here is the difference between the two rows, not either row by itself.

With the answer written down as well, it refuses — on an *invariant*, meaning something the loop is supposed to keep true every time round. It sees the bug because somebody wrote down what the answer must be, not merely where the code was allowed to read.

%% ⚠ Tightened ~30 words.  The two-step detail (spec arithmetic, then the bridge
%% lemma, then two proof lines; and that moving the spec alone leaves the lemma
%% false) is kept because it is what makes "not one character either" a fact
%% rather than a hedge — but "Which makes the honest headline better than the
%% neat one" was the post talking about itself, and the punchline reads harder
%% without the run-up.
So move the specification to match the typo. Now the prover verifies the bug and reports nothing wrong. That edit isn't one character either — it's the specification's arithmetic, plus the small lemma bridging it to the code, plus two more lines of proof, and moving the specification alone just leaves the lemma's promise false. So the honest version of this isn't *one more character*. It's the author's misunderstanding reaching the specification. A proof is a proof of what you wrote down.

There's a version of this that runs the other way, in the same character position. Type a `5` instead — dividing by thirty-two, which can overshoot — and the bounds check panics, Rust's word for stopping yourself on purpose, and the sanitizer reports a heap buffer overflow at exit 1, exactly as advertised. But only on an input nobody would think to write: a thin probe built specially for it, not one of the five shipped with the program and not in the gate. On the five real ones both stay quiet, while the proof catches it on every input, because what it must show is quantified over all of them.

%% ⚠ "at least nine one-character edits" IS CUT, ~15 words.  It is true and
%% sourced (NOTES.md:891-892), but the first cold reader flagged it as the one
%% place the section felt like it was selling: "attributed to notes I can't see,
%% at the emotional peak of the section.  I believed the demonstrated one; the
%% nine felt like it was there to make the one feel bigger."  Nothing rests on
%% it — the demonstrated edit carries the argument by itself — so it goes.
%% ⚠ `mutant` was the last unglossed term in the post (first and only use, at the
%% very end of the section); it is now named as what it is.
For the `7`, no such input exists. Nothing you could feed the program would make any of those mechanisms fire, because the index never leaves the bitset. Every one of them watches the edges of a block of memory, and this bug never goes near an edge.

They're the right tools for the class of bug people mean when they say most serious security bugs are memory-safety bugs \cite{msrc19}\cite{chromium}. This one isn't in that class. Both broken copies here — the `7` and the `5` — rebuild from a committed script whose hash the gate does record, and are certified by no gate. \src{patterns/p09-bitset/controls/gen_controls.py}
