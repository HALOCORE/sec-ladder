%% Threats to validity.  Each limit ships its DIRECTION (CLAIMS.md 3.5).
%%
%% PRIMARY SOURCES:
%%   15 of 33 spatial; composition   harness/tools/composition.py (run this session)
%%   ptr_offset census               results/SYNTHESIS.md §7: 49,898 sites over 991,147
%%                                   lines in 22 programs; median share 6.9%; 0 of 464
%%                                   sites in 40 functions at 33 (kernels plus helpers)
%%   type axis two rows; temporal 6  composition.py; SYNTHESIS §3, §7
%%   Ir vs time, 3 mechanisms        results/synthesis.md limit 3 (rep-string, div, latency chain)
%%   Ir not invariant: ±7, +486      SYNTHESIS §6 trap 7(a)
%%   port +10% once inlined          p16/NOTES.md:441-448 (via ver_E fact-check)
%%   both sides searched 10 of 33    SYNTHESIS §7 retirement subsection
%%   counter-instances toward safe   SYNTHESIS §2 (p17 -19, p06 c_idx), §7 (p16 sign
%%     Rust                          flip, p14 88.9%, p09 65x span, p36 mirror image)
%%   nineteen retractions            SYNTHESIS §0, §6 (no denominator exists — CLAIMS 1.20:
%%                                   not led with; stated with that absence)
%%   nine results missing, five graded  SYNTHESIS §7 "A gap in this document"
%%   gate blind to ensures prose     SYNTHESIS §4
%%   "no spec exists" twice          CLAUDE.md (copy_from_slice, index_mut)
%%
%% ⚠ CLAIMS.md 2.1: never "memory safety costs about X%".
%% ⚠ "Our errors run in safe Rust's favour" now carries the counter-instances
%% the record carries (gaps review E): the direction is the record's, the
%% absence of every counter-instance was not.
\section{Threats to Validity}
\label{sec:threats}

**The corpus is small, hand-built, and mostly bounds checks.** Fifteen of \num{totals.passing.patterns} programs are spatial. A census over 991,147 lines of real C in 22 programs — PHP, GNU coreutils and other GNU packages — classified every place a memory access is bounded, and found the pointer cursor, walking memory by advancing a pointer rather than indexing, in every one of them, ranking second or third in fifteen, with a median share of 6.9% of those sites. It appears in none of ours: 0 of 464 sites across the 40 functions of our 33 C programs. Every measured function here indexes; none walks. Everything we say about the type system's compile-time guarantees rests on two programs, and the temporal results on six that disagree with each other.

**Instruction counts are not time, and are not quite invariant.** Three programs here show instructions and time disagreeing in direction, and there is no cross-program wall-clock column because the timing floor on this machine is a property of the session. The instruction count itself moves by a few per call with the length of the process environment, and by hundreds with the content of one allocator-tuning variable, so a difference of a handful of instructions between two runs is inside the noise. Per-call constants transfer to other code; fractions of these functions do not, because a real function does other work, so every percentage here can only shrink in a program that is not the loop.

**Every function is out of line, single-threaded, and alone.** Compile these programs the way they ship and the measured function inlines into its caller and stops existing as a symbol; on the record walker the port costs about ten percent *more* once inlined. Nothing here starts a thread, so the study is silent on data races. Nothing here is a whole system or a mixed C-and-Rust binary, so it prices a rewritten loop and not a rewritten daemon, and the gap between those two is where a real decision lives.

**Our errors run mostly in safe Rust's favour.** Two props hold the unsafe side high: the rule tying each verified version to an identical unsafe one refused a 17,526-instruction saving on one program (Finding 9), and only ten of the \num{totals.passing.patterns} programs have had both sides of their safe-versus-unsafe comparison searched, the unsearched side usually being the unsafe one. Not always: on the record walker, the bitset and a field splitter the safe side is the one held high — by 2,545 instructions, fifty-fold and 89% respectively — and on a dispatch table a review moved the safe figure down rather than the unsafe one. Where a figure here is wrong, the way to bet is still that safe Rust comes out of it better than it should.

**The project has retracted a great deal.** Over its life it withdrew nineteen of its own published claims — there is no clean count of how many it made — and the rules in Section \ref{sec:method} are what most of them taught. When it first compressed its programs into headline results, nine reviewed results went missing, every one whose direction could be graded flattering safe Rust: a long habit of retracting "safety is cheap" had deleted the evidence for it, while every figure reproduced correctly. Two of the nine were missing again from the first draft of this paper. The only check that finds such a gap is to ask, of a finished document, which way its gaps point; one reviewer did, and the reader is invited to.

**The checker certifies the proof, not the specification.** Nothing in our checking script tests that a specification means what its author says it means; it checks that the proof discharges, that the verified and unsafe versions compile alike, and that the source contains the idioms it declared. Finding 10 is the consequence, and it applies to this paper's proof figures as much as to anyone's.

**One machine, one pin.** One host, one libc, one gcc, one clang, one rustc, one Verus with one pinned standard library. Where a claim is about the verifier it is about that version and no other: this project twice reported that no specification existed for a function whose specification was one directory away.
