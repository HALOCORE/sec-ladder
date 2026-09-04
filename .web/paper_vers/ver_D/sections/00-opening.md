%% Story 1.  The hook is DECIDED (brief 5, beat 1) and is not to be reinvented:
%% open on something the reader has personally done, second person, no term that
%% needs a gloss.  An abstraction in sentence one killed two earlier framings.
%%
%% THE CLAIM lands in sentences three to five and carries no numbers.  This post
%% has no summary section, so if the claim is not here it is nowhere.  Three
%% framings have failed the question "what is it claiming, in your own words?".
%%
%% GLOSSES PAID FOR HERE, each as a trailing appositive in a sentence doing other
%% work: kernel (a reader once took it for an operating system and held that for
%% a whole document), unsafe, the difference between the two safe versions,
%% hardened, gate, sanitizer, slice-free.  No glossary block.
%%
%% THE HARDENED-C ROW IS MANDATORY.  Without it the table reads "C crashes, Rust
%% stops", which CLAIMS.md 2.4 bans outright, and it would sit one row from the
%% best artefact in the report.  With it the table SHOWS the thesis: write the
%% same three lines in C and the C is fine.
%%
%% Do NOT print 101 in the table -- it collides with the zero-panics paragraph
%% below and a cold reader lost the distinction.  "Stops itself" in the table,
%% the exit code in the paragraph, where shipped-versus-mutant is the point.
%%
%% CLAIMS.md 3.1: "plain, unchecked C", never "idiomatic C".
%% CLAIMS.md 1 / C1: never "we deleted a line from each version" -- the C SHIPS
%% without the check; only the Rust versions had a line deleted.
%% CLAIMS.md 1.6: the deleted-check control does not always work, and the
%% paragraph saying so is not optional, only short (45 words).
%%
%% THIS FILE CARRIES THE POST'S ONE FULL PROVENANCE STATEMENT.  Story 3 gets a
%% clause; nowhere else gets one.  A cold reader on the previous framing: "I
%% stopped reading them after the third.  It reads as a ritual."
%%
%% Sources: FACTS.md A1, A2, B, B1, B2, B3, C, C1.  Every table cell re-read out
%% of insights/p16control.json this session.
\section{You can forget a check, and nothing will tell you}
\label{sec:opening}

You have deleted a check before — the line that makes sure an index is still inside the array — just to see whether anything broke. Nothing broke, the tests stayed green, you put it back, and you were never completely sure it had been earning its keep. That uncertainty is what I want to talk about, so let me put the claim up front: the useful thing you get from a memory-safe language is not that the check is fast, or well written, or even that it is there. It's that you can't leave it out and not find out. Take it away and something tells you. Leave it out of the C and nothing does — and everything's fine, right up until the day it isn't.

%% ⚠⚠ FACT-CHECK, MUST-FIX 7.  "on two of them nothing happened either" was
%% false for one of the two.  The two cases are DIFFERENT and only one is
%% "nothing": p18's stripped safe rung is BIT-IDENTICAL to C on every adversarial
%% input at both opt levels (p18/NOTES.md:1036-1040 -- genuinely nothing), while
%% p22's HANGS (p22/NOTES.md:74-93, six safe-Rust cells `rc None, <timeout after
%% 8s>`).  A hang is a change, not a nothing.  The hook now claims only the case
%% that is actually nothing, and the payoff paragraph splits the two.
We did that on purpose to eight small programs and wrote down what happened each time; on one of them nothing happened at all, and I'll come back to it.

So: one small C program with a real bug in it, written six ways, and all six measured.

The program walks length-prefixed records: read a three-byte header, take the length off the wire, fold that many bytes into a running checksum, move on, repeat. It's the kernel — which here means the one small function being measured, nothing to do with an operating system — and this is all of it:

```c
    while (end - p >= 3) {
        size_t vlen, j;
        acc = acc * 31 + buf[p];
        vlen = (size_t)buf[p + 1] + 256 * (size_t)buf[p + 2];
        /* R1h has, and this rung does not:
         *     if (vlen > end - (p + 3))
         *         break;
         */
        for (j = 0; j < vlen; j++)
            acc = acc * 31 + buf[p + 3 + j];
        p = p + 3 + vlen;
        nrec = nrec + 1;
    }
```

%% ⚠ ~65 WORDS TRIMMED HERE AND IN THE OPENING CLAIM, to hold the post under its
%% own ceiling after this round added three glosses and a factual correction.
%% NOTHING CLAIMED WAS DROPPED — what went was duplication:
%%  * the claim paragraph used to preview "a comment sitting where a line should
%%    be", which SPOILED the code block's own best moment four paragraphs later
%%    ("Read the comment").  Demonstrate once, which is this post's second rule.
%%  * "Believe a length that came off the wire and you read past the window" was
%%    a third statement of the bug, after the section title and the comment.
%%  * "because the table is unreadable otherwise" — a sentence about the post.
%%  * the input paragraph's arithmetic is now one sentence; the 47/48th-record
%%    detail is kept because it is what makes the attack concrete, and 3,072
%%    reappears in two table cells.
Read the comment. Nobody deleted that check from this file; this plain, unchecked C is what ships, and the missing test is the deliberate bug. The function is even handed the buffer's real size, and casts it to `(void)` without ever looking.

The Rust versions all have the check, spelled the same way — `if vlen > end - (p + 3) { break; }` — and for the experiment we deleted those three lines from each, rebuilt, and fed them all the same hostile input: one window of 3,072 bytes, in which forty-seven well-formed records fill almost everything and the forty-eighth has sixty-one bytes of room left but declares its value is 4,096 bytes long.

Thirty seconds on the six. Two are C: the plain one you just read, and a hardened one — the same file with those three lines written in C, nothing else changed. Two are safe Rust, where the compiler puts a bounds test in front of every array access whether you asked or not: one a line-for-line port of the C, one tuned, meaning somebody made it fast — which, as you'll see, changed what it says on the way down. One is unsafe Rust — the language lets you write `unsafe` and opt out of those tests, and people do, for speed, on the promise that they checked by hand. And one is that unsafe version with a machine-checked proof attached.

| the same three lines | what happens on the hostile input |
|---|---|
| plain C — ships without them | crashes. SIGSEGV, no message, nothing on either stream |
| hardened C — the same three lines, in C | prints the right answer and exits 0 |
| unsafe Rust, deleted | crashes. SIGSEGV, exactly like the C |
| safe Rust, the port, deleted | stops itself: `index out of bounds: the len is 3072 but the index is 3072` |
| safe Rust, tuned, deleted | stops itself: `range end index 7107 out of range for slice of length 3072` |
| the proved version, deleted | will not build: `invariant not satisfied before loop` |

%% ⚠ TWO GLOSSES ADDED, both named by the first cold read.  `slice` was never
%% explained anywhere in the post and sits in a table cell the reader is asked to
%% read carefully ("I guessed array-ish and moved on"); `invariant` was in this
%% table and not glossed until section 3 ("three sections is a long time to sit
%% on a word that's in a table I'm being asked to read carefully").  Both are
%% glossed HERE, against the error text that uses them, in eleven words total.
%% ⚠ §3 still glosses `invariant` where the argument turns on it — that is a
%% second use in a different job, not a duplicate: here it says what the word
%% means, there it says which loop's invariant failed and why that matters.
Two of those messages use a word each: a *slice* is a stretch of the buffer named by where it starts and how long it is, and an *invariant* is something a loop is supposed to keep true every time round.

Every version still holding those three lines returns the same right answer on that hostile input — hardened C and all four shipped Rust versions, one value, exit 0 — and on well-formed input every version that builds prints an answer identical to every other. The last row is the exception, and it's worth being plain about it: that version never builds, so it never runs, and "prints the right answer" is vacuous for it.

So nothing in that table is a difference between languages. It's three lines. What differs between the rows is only whether you can leave them out and not find out.

%% ⚠⚠⚠ FACT-CHECK, MUST-FIX 1, AND IT WAS THE WORST THING IN THE DRAFT.
%% The sentence used to end "...the source text, which no stage of our checking
%% reads."  THAT IS FALSE, and falsest here of all places.  harness/check.py:1216
%% `spelling_matches` says so in its own docstring: "since TASK_068 it is also a
%% gate check: `idiom_audit` calls it against every rung source".  And the gate
%% record behind THIS VERY TABLE publishes the result for THIS VERY CHECK --
%% results/gate/p16-tlv-walk.json `idiom_audit`:
%%     "required_absent": 1,
%%     "absent": [{"entry":"required[0]","lang":"c",
%%                 "spelling":"vlen > end - (p + 3)","rung":"c/kernel.c"}]
%% I opened both.  Corpus-wide the field is totals.idiom.required_absent = 126.
%% So the gate reads the source, matches the pinned spelling against every rung,
%% and writes down which rung lacks it.  What it does NOT do is FAIL: only a
%% `forbidden` hit fails a run, and p16's verdict is PASS carrying that absence.
%% ⚠ THE POINT SURVIVES AND IS SHARPER FOR BEING TRUE -- a check that records a
%% missing bounds test and passes anyway is a better example of this post's own
%% thesis than a check that never looked.  ⚠ ver_C ships the false version of
%% this sentence too (50-nonoptional.md, "no stage of our gate reads source");
%% that is a real defect in a shipped version and is recorded in RECAP.md.
%% ⚠ The three clauses that used to follow were verified TRUE and are dropped
%% only for length: nothing looks in the machine code for a compare or a branch,
%% nothing scans a safe version for `unsafe`, and no identity pin ties a safe
%% version to an unsafe one.
Here's the part that should stop you believing too much of that table. Across all \num{totals.patterns} programs in this project and \num{totals.adversarial_runs} hostile runs against them, exit code 101 — what a Rust program exits with when it stops itself — appears zero times. Not one bounds check fires anywhere in the shipped set. We have never watched a check save anything.

%% ⚠ THE `gate` GLOSS MOVES TO FIRST USE, which also saves ~35 words.  It used to
%% sit in the provenance paragraph four paragraphs down — after three uses — and
%% the first cold reader skimmed that paragraph and lost the definition.
So the only evidence a check is there is the source text. Our gate — the script that rebuilds everything and refuses to publish a number when a pinned one has moved — does read it: it matches the check's pinned spelling against every version and writes down which one is missing it. For this program it writes down that the C is missing it, and passes anyway. That's why we broke the others on purpose: the deleted-line control is the committed, re-runnable witness that the check does something.

One more instrument, because it matters later. Run the plain C under a sanitizer — a tool that watches every memory access as the program runs and shouts when one leaves its allocation — and it catches this immediately: `heap-buffer-overflow`, a one-byte read zero bytes past a 3,072-byte region. That's one build configuration here: gcc at `-O1`, the plain C only, no Rust.

%% ⚠ CALLBACK, NOT A REPEAT.  The hook already spends "on two of them nothing
%% happened either", so this paragraph must ADD rather than restate — otherwise
%% it is a second demonstration of a finding the reader already has, which is
%% the failure mode that made four cold readers quit the previous version.  What
%% is new here is the hang and the silence, and that clause is also the bridge
%% into the next section.
%% ⚠⚠ FACT-CHECK, MUST-FIX 7, second half.  "with every tool silent" was FALSE
%% and CLAIMS.md §1.15 bans it in as many words -- "Nothing catches an infinite
%% loop" is true of the STATIC instruments only; a `decreases` clause catches it
%% at compile time and a plain `timeout` at run time.  p22/NOTES.md:944-949
%% records the same deletion in the PROVED version producing THREE Verus errors.
%% ASan+UBSan and Miri really are silent (p22/NOTES.md:87-88), so the honest
%% form names which instruments were silent and which was not -- and it is a
%% better sentence, because a proof catching what two runtime tools miss is the
%% same shape as the section that follows.
Eight programs carry that control, and it doesn't always tell you anything. On the one I promised to come back to, deleting the check changed nothing whatever: the safe version compiled to code that behaves exactly like the C, on every hostile input, at both optimisation levels. On another it stops answering altogether and hangs, with the sanitizer and the interpreter both silent — though there the proof does catch it.

%% ⚠ THE OPENING CLAUSE IS REWRITTEN.  It used to read "Where all of that comes
%% from, once, and then I'll stop saying it" — which announced itself as
%% bookkeeping, so the first cold reader skimmed the paragraph.  That cost them
%% the definition of `the gate`, which three later sentences depend on.  Same two
%% facts, same order, but the paragraph now opens on the asymmetry (which is
%% interesting) instead of on its own housekeeping (which is not).
%% ⚠ BOTH CLAUSES ARE MANDATORY, CLAIMS.md §1.21: a committed generator, AND no
%% gate.  ver_B's old disclaimer — "no committed generator, does not survive a
%% clone" — is now FALSE and must not come back.
Those rows are not all equally well attested, and the difference matters. The C ones are the shipped program and pass that gate in every build configuration. The Rust ones are deletions I made from those sources, re-run from a committed script, and certified by no gate at all. \src{insights/p16_control.py}
