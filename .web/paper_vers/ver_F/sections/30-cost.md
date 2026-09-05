%% RQ1 -- cost.  Five findings.  Each is one box, one concrete program, one
%% "so what", and its limits in the same subsection rather than a later one.
%%
%% PRIMARY SOURCES for every per-program literal in this file:
%%   record walker (p16) table   results/synthesis.md §1 rows p16-tlv-walk
%%   +2,085 / +17,123, +27 / +77 derived from that table; 69% = 2085/3010,
%%                               72% = 17123/23798, 0.9% = 27/3010, 0.3% = 77/23798
%%   tuned = reslice once + iterator fold   patterns/p16-tlv-walk/safe_tuned.rs:3-7 (C4)
%%   4.25 = 2.00 check + 2.25 foreclosed unroll   p16/NOTES.md:56-60 (C5)
%%   -199 / -2,545 cheapest safe patterns/p16-tlv-walk/NOTES.md:213-218
%%   +72% Ir is +0.27% time,     patterns/p16-tlv-walk/NOTES.md:62-65
%%     spread 0.96-2.31%
%%   searched arm 7 / 3 / 10     synthesis/census.py arm C (run this session);
%%     p22 +2 -> +125/+1,021,    results/SYNTHESIS.md §2 table "against the cheapest
%%     p13 and p12 sign flips    admissible R4 found"
%%   negative gaps investigated  SYNTHESIS §2: p46 unroll, p13 bound, p10 60% was the
%%                               unsafe spelling (C10)
%%   attribution table           results/SYNTHESIS.md §2 "Where the number is large"
%%   partition cause OPEN        patterns/p23-partition/NOTES.md:938, :992
%%   ct-compare rung-pair        patterns/p47-ct-compare/NOTES.md:567
%%   p14 "check forecloses it"   results/SYNTHESIS.md §2 "The check's second half"
%%   bounded stack 359/626 =     patterns/p03-bounded-stack/NOTES.md:316-322 (3.00·xpop + 5,
%%     3·pops + 5 exactly;       exact; one surviving check) (C17); clamp :362-410;
%%     clamp, +502, +5 unsearched  +5 never searched SYNTHESIS §7 item (1)
%%   bitset +13,756/+48,885,     patterns/p09-bitset/NOTES.md:1119-1135 (five spellings);
%%     five spellings, 65x       unsafe 6,678 / 24,505 from synthesis.md §1
%%   bitset clock                patterns/p09-bitset/NOTES.md:436-452
%%   never re-ship a cheaper one results/SYNTHESIS.md §2
%%   binary search 3,015/10,025  results/synthesis.md §2; unsafe 6,562 / 21,353 §1;
%%     one lea per probe :375;   patterns/p07-binary-search/NOTES.md:450-465, :508-520
%%     42-47%, +13%/+1.6%
%%   hardened p16 +24/+54 clang  derived from the p16 table
%%   p01 R3-R4 4/5; p02 11/11;   results/synthesis.md §1-§2 (C33); hardened only on p02:
%%     p02 hardened +5/+12       207-202 gcc, 205-193 clang
%%   p06 hardened: fewer Ir,     results/SYNTHESIS.md §6 trap 7(b): 45-108 fewer
%%     10-20% slower             instructions, 10-20% slower, clang
%%   p19 -5,071/+3,569, 2,510    results/synthesis.md §1 p19 rows (2831-7902, 45071-41502);
%%     MECHANISM (C37)           p19/NOTES.md:375-380: the RUST versions run the 2,048-byte
%%                               validation pass (the proof rests on it), plain C SKIPS it
%%                               (its bug) and saves 5,647 fixed; gcc does not unroll the
%%                               fold so C pays 11.00 vs 8.75 Ir/byte; clang flat -5,642
%%   p19 hardened 10,242         13073-2831 off synthesis.md §1
%%   gcc-clang 1,069             4062-2993
%%   p01 7,187 == 7,187          results/synthesis.md §1 p01 large (c-clang, unsafe)
%%   endbr64 / -fcf-protection   results/synthesis.md limit 4; SYNTHESIS.md §1
%%   layout 31 builds, 6 flips   data/index.json layout (common/layout/data/layout_p01.json)
%%   up to 27%, 32-byte window   .memory/03-measurement.md:1150-1160
%%
%% ⚠ The distribution is ONE SENTENCE that partitions exactly: flat + expensive
%% + between = licensed; `negative` is reported inside it, never added in (it
%% overlaps flat).  All counts live (totals.buckets.*).  The searched-arm
%% sentence after it is the half of the same record that does NOT flatter safe
%% Rust (gaps review); its four moves are frozen literals from SYNTHESIS §2.
%% ⚠ The record walker's own cheapest safe spelling (-199 / -2,545) is stated
%% under its table: the counter-instance to "our errors run in safe Rust's
%% favour" that a reader can check against the numbers in front of them.
%% ⚠ CLAIMS.md 1.5: never "hardened C costs +5/+12 flat" as a law.
%% ⚠ CLAIMS.md 1.4: never claim rustc's LLVM is bit-for-bit clang's.
%% ⚠ PITFALLS 1.7: every ratio closes from numbers on the page.
\section{What Memory Safety Costs}
\label{sec:cost}

The question a benchmark usually answers is "how much slower is safe Rust than C". The question we can answer is sharper: for one program held fixed, what does each version cost, and what is the difference paying for? Throughout, a version's **overhead** means its instructions per call beyond the unsafe version's.

\subsection{Who wrote it matters more than whether it is safe}

\begin{finding}{Two safe versions differ more than safe and unsafe do}
Where tuned safe Rust has any overhead over unsafe Rust, the line-for-line port's overhead is a median \num{totals.r2_over_r3.median}× the tuned version's. Nobody removed a check to get from one to the other.
\end{finding}

Take a record walker: read a three-byte header, take a length off the wire, fold that many bytes into a checksum, repeat. Here is every version, in instructions per call at `-O3`, with the two C versions built by both compilers. The verified version gets no row because it is byte-identical to the unsafe one.

| version | small input | large input |
|---|---:|---:|
| unsafe Rust | 3,010 | 23,798 |
| safe Rust, port | 5,095 | 40,921 |
| safe Rust, tuned | 3,037 | 23,875 |
| plain C, clang | 2,993 | 23,761 |
| plain C, gcc | 4,062 | 32,694 |
| hardened C, clang | 3,017 | 23,815 |
| hardened C, gcc | 4,079 | 32,735 |

The port's overhead is +2,085 and +17,123 instructions per call, that is +69% and +72%. The tuned version's is +27 and +77, under one percent. Both are safe Rust; both check every access; neither contains the word `unsafe`. The difference between them is about ten lines: the tuned version re-slices the payload once and folds it with an iterator, so its one bounds check — the re-slice — sits outside the fold loop, where the port's sits inside it and is paid on every byte folded, 4.25 instructions a byte (two of them the check, the rest an unroll the check forecloses). Nor is the tuned version the cheapest safe one: a further safe rewrite of the fold comes out 199 and 2,545 instructions per call *below* the unsafe version, so +27 and +77 are a bound with the safe side held where we first wrote it.

Across the corpus the same shape holds. Of the \num{totals.buckets.licensed} programs whose versions are comparable, \num{totals.r2_over_r3.rows} have tuned safe Rust dearer than unsafe on the large input. Over those, the ratio of the port's overhead to the tuned version's runs from below one — on \num{totals.r2_over_r3.not_overstated} programs the port is the cheaper safe version — to over three thousand; the middle half of the programs lies between \num{totals.r2_over_r3.q1}× and \num{totals.r2_over_r3.q3}×, and the median is \num{totals.r2_over_r3.median}×. The median does not move when the four programs for which a cheaper unsafe version was later found are recomputed against it.

> When a benchmark reports that safe Rust is slow, the first question is not *how slow*. It is *which safe Rust, and did anyone tune it*.

The tuned version's own overhead splits the \num{totals.buckets.licensed} comparable programs three ways: on \num{totals.buckets.flat} it is flat, within 32 instructions per call of unsafe on both inputs; on \num{totals.buckets.expensive} it exceeds 100 instructions per call on at least one input; and the other \num{totals.buckets.between} sit between — \num{totals.buckets.negative_not_flat} where safe Rust is the cheaper version on both inputs, and the record walker at +27 and +77. Those counts are for the versions we measured; against the cheapest unsafe version later found for each program — measured, verifying, within the allowed idioms — the split is 7, 3 and 10, four programs moving, every one of them against safe Rust and two changing sign. Where a negative gap has been investigated, none of the margin is safety: an unroll decision, a bound the compiler could see, an unsafe version nobody had tuned. Every program's figures are in the table below.

\figure{programs}{Every program, at `-O3` with the measured function out of line, in instructions per call. A dash marks a difference the two versions are not comparable enough to take. The hardened-C column is the same check written into the C, under clang.}

\subsection{The bill is usually not the check}

\begin{finding}{Most large overheads are attributed to something other than the bounds check}
Of the ten programs whose overhead has a written attribution, three attribute it to the bounds check. Of the other seven, two are disputed by the program's own notes, so between five and seven of the ten are paying for something else.
\end{finding}

An attribution is a written account of where the instructions went, obtained by reading the two compiled functions side by side and, where possible, building one-line variants that isolate one mechanism. Ten programs carry one: nine of the \num{totals.buckets.expensive} expensive ones — the newest, a free-list pool, has none — plus a hash probe that is flat as measured (+2) and expensive only against the cheaper unsafe version found later (+125 and +1,021).

| program | what the attribution names |
|---|---|
| index flattener | a hoisted per-row trip count and a scalar epilogue |
| rotate | the tests an iterator chain runs to ask whether it has run out; none of it a bounds check |
| field splitter | an unroll the unsafe version could do and the checked loop could not — an optimisation the check forecloses rather than the check itself |
| protocol state machine | a single `and $0x7` mask, not a check |
| hash probe | a missing re-slice in the unsafe version; none of it a bounds check |
| partition | the shape of the data: which way a pivot splits it — cause marked open |
| constant-time compare | the constant-time discipline; the port is cheaper because it leaks — attributed to a different pair of versions |

The remaining three — a bounded stack, a binary search and a bitset — are attributed to the check, and they are the next finding.

\subsection{When the check is real}

\begin{finding}{Where the optimiser cannot see the bound the cost is real, and instructions are not time}
A binary search pays 3,015 and 10,025 instructions per call for its bounds checks, over an unsafe version costing 6,562 and 21,353, and that share does not shrink as the array grows. In wall clock the same cost is +13% on the small input and +1.6% on the large.
\end{finding}

Three programs carry an overhead that is the check. They end differently.

**The bounded stack: the cost vanishes when the optimiser is told what the proof knows.** Tuned safe Rust pays 359 and 626 instructions per call over unsafe — exactly one surviving check per executed pop, at three instructions, plus a five-instruction constant. Add one line at the top of the loop that can never fire — a clamp restating the invariant the proof already proves — and the compiler deletes the surviving check on the safe and the unsafe side alike, leaving a per-pop difference of exactly zero across nineteen inputs; clang and gcc both do the same to the hand-written C check. It is not free: the clamp costs two instructions per rejected push, so on the large input the clamped safe version is still +502, and the five-instruction constant survives unsearched.

**The bitset: the cost is mostly a choice.** The tuned safe version pays +13,756 and +48,885 instructions per call over an unsafe version costing 6,678 and 24,505 — on the large input, twice the unsafe version's entire cost. It is also the second dearest of five allowed safe spellings, which on the small input run from +263 to +16,992, a sixty-five-fold span that the line-for-line port sits inside, cheaper than the tuned version. We never swap a measured version for a cheaper one found later — a benchmark that re-ships whatever wins is measuring its own search — so the span is reported beside it; the unsafe side was searched and has nothing cheaper the prover accepts, so the whole span sits on the safe side. On this program a stopwatch agrees with the instruction count: on the small input +205.6% of instructions is +205% to +220% of time in the measured function, no discount at all.

**The binary search: the cost is real and survives everything.** It probes the array by a rule the optimiser cannot follow, so there is nothing to hoist a check out of and nothing to fold it into. Four safe spellings were tried and the cheapest differs from the measured one by one instruction per probe. Both unsafe candidates were tried; the only cheaper one dereferences a raw pointer in a way the prover cannot accept. Swept across array sizes the tuned safe version costs 42% to 47% more instructions than unsafe, rising with the array in all six query distributions. Then the stopwatch: +13% of time on the small input and +1.6% on the large, which is where the function actually spends its time. Both survive re-running, and we could not establish where the rest goes; neither number should be quoted without the other.

The record walker is the same warning from the other side. Its port's +72% of instructions is +0.27% of wall clock, inside the 1% to 2% that separates two runs of the same binary, because the fold waits on a chain of dependent arithmetic and the extra instructions fit in the gaps. An instruction count is not a time, and it is not reliably an overstatement either.

\subsection{The same check in C}

\begin{finding}{Writing the missing check into the C costs the same order as tuned safe Rust's overhead}
Across the \num{totals.hardened.patterns} programs with a hardened version, the check costs a median of \num{totals.hardened.gcc.median_int} instructions per call under gcc and \num{totals.hardened.clang.median_int} under clang, over both inputs; tuned safe Rust's overhead over the comparable programs has a median of \num{totals.buckets.median_small} on the small input and \num{totals.buckets.median_large} on the large. The same order, not the same number — and in C the check is optional.
\end{finding}

On the record walker, hardened C is +24 and +54 instructions per call over plain C under clang, which lands it between the two Rust versions in the table above: unsafe Rust is a few instructions in front of it, tuned safe Rust 20 and 60 behind. On the two simplest programs — an array sum and a bounded copy — tuned safe Rust's check is four to eleven instructions per call, flat in the data; on the copy, the only one of the two that ships a hardened C, writing the check into the C costs five under gcc and twelve under clang.

The median hides a wide range. Under gcc the check runs from \num{totals.hardened.gcc.min} instructions per call — cheaper with the check than without, on \num{totals.hardened.gcc.negative_patterns} programs — to +\num{totals.hardened.gcc.max}. The dearest is not a check at all but a whole validation pass over a 2,048-entry table in a protocol state machine, and on one program, a rotate, the hardened C executes fewer instructions than the plain C and runs 10% to 20% slower. "Hardening is cheap" is true where the check is all you are adding, and false as a law.

\subsection{Which two programs, which compiler, which input}

\begin{finding}{A cost figure can flip sign with the input, and the compiler moves it more than safety does}
On a protocol state machine plain C is 5,071 instructions per call cheaper than unsafe Rust on the small input and 3,569 dearer on the large. On the record walker the same C source costs 1,069 more instructions under gcc than under clang, forty times the tuned version's +27.
\end{finding}

The state machine's two numbers have one cause, and it is not safety. The unsafe Rust — and the verified version, whose proof rests on it — validates the whole 2,048-entry transition table once per call; the plain C skips that pass, which is its bug, and saves a fixed 5,647 instructions. But gcc does not unroll the C's per-byte fold, so the C pays 2.25 instructions more per message byte, and the two cross at a message of about 2,510 bytes, between the inputs the program ships with. Under clang the same comparison is flat at −5,642 on both inputs and never crosses. Any percentage quoted at either input is wrong in sign at the other.

The compiler gap is inside every C-versus-Rust figure in this paper, which is why each names its compiler. Part of it is a flag: gcc on this machine defaults to `-fcf-protection=full`, so every gcc-compiled function opens with an `endbr64` landing pad that clang and rustc do not emit. Through one back end the languages can coincide exactly — on the array sum, clang's C and unsafe Rust both execute 7,187 instructions per call on the large input, the same LLVM version behind both — and the Rust-versus-Rust figures go through one compiler and carry none of the gap.

Wall clock adds a third axis. One program's three Rust versions were built thirty-one times from identical source, changing only where the linker placed the code, and all six version-to-version timing comparisons changed sign across the builds; elsewhere in the corpus the same effect — a loop body straddling one more 32-byte instruction-fetch window — reaches 27% of wall clock at an unchanged instruction stream. A single timing comparison between two builds has no sign until the layout noise has been measured.

\figure{spread}{One program's Rust versions built thirty-one ways from identical source. Each row is one comparison of two versions; the band is its range over the layouts and the centre line is zero. Every row crosses it.}
