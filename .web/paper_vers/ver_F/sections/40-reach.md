%% RQ2 -- what each version does under attack, then what memory safety does not
%% reach.  Three findings.
%%
%% PRIMARY SOURCES:
%%   crash/hung/loud, all plain C   re-derived this session over results/gate/*.json
%%                                   (.temp/verF/verify.py): 133 crash (67 gcc, 66 clang),
%%                                   8 hung (4+4), 0 exit 101; hardened C 1,280 cells
%%                                   0 diverging; 166 pairs, 85 divergent, 0 Rust splits
%%   sanitizer 67 fired on plain C   same script; ONE configuration (CLAIMS 1.17)
%%   contracts bound length only     results/SYNTHESIS.md §7
%%   p02 one-byte overflow           patterns/p02-buffer-copy/NOTES.md:140-150 (7 of 8
%%                                   builds exit 0 with 198979479034752; gcc -O3 whole
%%                                   aborts), :183-196 (_FORTIFY_SOURCE 3 is the
%%                                   distribution's default); SYNTHESIS §3 "the measured one"
%%   record-walker control table     insights/p16control.json (regenerated, committed);
%%                                   error strings verbatim from its `runs` and `verus`
%%   required_absent                 totals.idiom.required_absent (live)
%%   eight-program control tally     paper_vers/CLAIMS.md §1.6 (binding); p16 and p02
%%                                   verified (SYNTHESIS §3), p18 NOTES.md:1036-1040
%%                                   (stripped safe rung bit-identical to C), p22
%%                                   NOTES.md:74-93 (hang, ASan and Miri silent),
%%                                   p22 NOTES.md:944-949 (proof: 3 errors)
%%   bitset q>>7                     RECAP.md finding 19; SYNTHESIS §3
%%   ring buffer fullness check      SYNTHESIS §3 ("no out-of-bounds access at all, 9/0")
%%   range parser CVE-2017-7529      SYNTHESIS §3; p17/NOTES.md:26-34, :250-262
%%   varint shift; UBSan/Miri/Verus  p18/NOTES.md:1036-1040; SYNTHESIS §3; CLAIMS 1.14
%%     do catch it
%%   hash probe hang                 p22/NOTES.md:74-93
%%   free-list pool bit-for-bit      SYNTHESIS §3 temporal table (10 of 10 cells)
%%   interned pool CVE-2022-40304    SYNTHESIS §3; p49/NOTES.md:182 (216 cells, 0 diagnostics)
%%   ct-compare +7,088 Ir, no ns     p47/NOTES.md:656, :1015; CLAIMS 1.9 (no timing
%%                                   measurement of the leak exists)
%%   temporal rule, six rows         .memory/01-ladder.md:2611-2700; SYNTHESIS §3 table
%%   p27 allocator 0.00, one op      SYNTHESIS §2 "The lifetime guarantee costs zero"
%%   "not a score"                   SYNTHESIS §3 ("That ratio is a property of which
%%                                   patterns were built ... so it is not a score")
%%   overlapping memcpy              p08/c/kernel_hardened.c:1-20 (one address);
%%                                   p08/NOTES.md:28-36 (+26/+26 = +0.36%/+0.09%);
%%                                   :626-656 (rustc suggests split_at_mut; copy_within; Miri)
%%   strict aliasing -6, +12/+32     SYNTHESIS §3 (p38 neighbours: c_halves is a C spelling)
%%
%% ⚠ CLAIMS.md 2.2 / 2.4: never "Rust catches it" and never "safer than hardened
%% C on outcomes".
%% ⚠ CLAIMS.md 1.11: "Miri reported nothing", never "Miri-clean" as a verdict.
%% ⚠ CLAIMS.md 1.15: never "nothing catches an infinite loop".
%% ⚠ CLAIMS.md 1.21: the C rows of the control are the measured programs and pass
%% the checking script; the Rust rows are deletions re-run from a script.
%% ⚠ p35 (tagged union) is NOT in the eight: its safe versions cannot express
%% the bug (SYNTHESIS §3 table), so it is a win, not a gap.
%% ⚠ The ledger is 8 misses / 1 measured win (p02) / 2 unpriceable wins, as
%% SYNTHESIS §3 has it; the first draft dropped p02 — the exact omission the
%% research's own first synthesis made — and the gaps review put it back.
\section{What Each Version Does Under Attack}
\label{sec:reach}

Every version of every program was run on inputs written to trigger that program's bug and compared with the reference. This section asks what happened, then which bugs memory safety did not reach.

\subsection{Every misbehaviour was in plain C}

\begin{finding}{Under attack, plain C crashed \num{totals.passing.crash} times and hung \num{totals.passing.hung} times; no other version ever deviated from the reference}
Across \num{totals.passing.adversarial_runs} hostile runs, hardened C and all four Rust versions returned the reference answer on every input. The four Rust versions never once disagreed with each other. Not one bounds check fired.
\end{finding}

Of the \num{totals.plain_c.rows} hostile program-and-input pairs, \num{totals.plain_c.deviating} have some build deviating from the reference — a crash, a hang, or a plausible wrong answer with exit 0 — and in every one of them the deviating builds are plain C, while the port, the tuned version, the unsafe version and the verified version print the same thing as each other and as the hardened C. Under the sanitizers, in the one configuration we ran them, the plain C fires on \num{totals.sanitizer.fired} of its inputs and the hardened C never fires.

The sharpest single case is a one-byte overflow. A bounded copy is handed a record one byte longer than its 64-byte destination. Plain C prints a plausible-looking number and exits 0 in seven of eight builds, because the allocator rounds a 64-byte request up to 72 usable bytes and the extra byte lands in the padding; the eighth build aborts only because the distribution's glibc fortification happens to see this one of the program's three attacks. Hardened C and every Rust version return the reference answer. Delete the bound test from the safe port and it stops itself on that input with `index out of bounds: the len is 64 but the index is 64`, while printing the C's answer bit for bit on every well-formed one.

\figure{outcomes}{The worst behaviour each version produced on any hostile input, counted over programs. Every version above plain C matched the reference everywhere.}

Two things bound that result. It cannot separate hardened C from Rust: on what these programs do under attack the two are indistinguishable. And the all-green Rust columns are a property of the experiment, not a score. Every Rust version was written to accept any byte content inside the window it is handed, and every contract we have audited — 26 of the \num{totals.passing.patterns}; the seven newest have not been re-checked — bounds the input by its length and never by its contents, so no hostile input can take a Rust version anywhere its checks would object. That is why no bounds check ever fired — \num{totals.passing.loud} of \num{totals.passing.adversarial_runs} runs ended with a Rust program stopping itself — and it is why the safety net in this study has never been photographed catching anybody.

\subsection{Delete the check and see who notices}

\begin{finding}{Remove the check and Rust tells you; C does not}
On the record walker, deleting the check from the safe versions turns a silent wrong answer into a stop with a message, and deleting it from the verified version turns it into a build failure. The plain C ships without it, and our checking script records the absence and passes the build.
\end{finding}

Since no measured check ever fires, the evidence that a check does anything has to be made: delete it, rebuild, and attack. On the record walker the check is three lines, `if vlen > end - (p + 3) { break; }`, deleted from each Rust version, and the hostile input is one 3,072-byte window whose last record claims 4,096 bytes.

| version | on the hostile input, with the check removed |
|---|---|
| plain C — ships without it | crashes: SIGSEGV, nothing on either stream |
| hardened C — the check written in C | prints the right answer, exit 0 |
| unsafe Rust, check deleted | crashes: SIGSEGV, exactly like the C |
| safe Rust, port, check deleted | stops itself: `index out of bounds: the len is 3072 but the index is 3072` |
| safe Rust, tuned, check deleted | stops itself: `range end index 7107 out of range for slice of length 3072` |
| verified Rust, check deleted | will not build: `invariant not satisfied before loop` |

Nothing in that table is a difference between languages: hardened C with the same check is fine. What differs is whether you can leave the check out and not find out. Each program's contract names the check its C is supposed to contain; our checking script reads every source, finds it missing, records the absence — \num{totals.idiom.required_absent} such (check, version) pairs across the corpus — and passes the build anyway, because the only spelling rule that fails a build is a construct we have explicitly forbidden. The two C rows are the measured programs and pass every check; the four Rust rows are deletions re-run from a script and certified by nothing.

The control does not always work. On eight programs where the check was deleted from the safe versions, four stopped where the C is silently wrong; two depend on the input, printing the C's answer and exiting 0 inside the in-bounds regime; and two produced no stop at all. On one, a varint decoder, the check was the entire difference: with it deleted the safe version compiles to the same machine code as the plain C, because the bug touches no memory and nothing else in the language objects. On the other, a hash probe, the stripped version hangs instead, with the sanitizer and Miri silent and only the proof objecting: without the capacity guard the invariant that an empty slot still exists cannot be re-established, and the loop's termination argument rests on it.

\subsection{Eight bugs memory safety does not reach}

\begin{finding}{Memory safety is a narrow property}
At least eight of the \num{totals.passing.patterns} programs carry a bug that the guarantees of safe Rust do not reach: the safe version either reproduces the C's wrong answer, or is correct only because its author wrote the same check the C author forgot.
\end{finding}

| program | the bug | why memory safety does not see it |
|---|---|---|
| bitset | `q >> 7` typed for `q >> 6` | a smaller word index cannot leave the array; the wrong word is a legal word |
| ring buffer | the fullness check dropped | a push overwrites the oldest element in place, with no out-of-bounds access |
| HTTP range parser (CVE-2017-7529) | a suffix range missing `start >= 0` | every read is inside the window it was handed; it reads the wrong part of it |
| varint decoder | a shift bound removed | touches no memory; with the bound deleted the safe version is bit-identical to the C, and only UBSan, Miri and the proof — none of them a memory-safety check — object |
| hash probe | no capacity check on a full table | every access is reduced modulo the table size; the loop simply never ends |
| free-list pool | a stale handle into recycled storage | nothing is ever freed, so there is nothing for the lifetime guarantee to attach to |
| interned pool (CVE-2022-40304) | a write through a deliberately shared buffer | the sharing is the contract; every index is in bounds and nothing is allocated or freed |
| constant-time compare | an early exit whose instruction count depends on the secret | a property of the execution trace, invisible to any check on values |

Eight misses against the three wins below is a property of what we chose to build, not a score. The catalogue was written around bugs a check can price, a bug safe Rust removes outright leaves nothing to measure, and the admission rule that shaped this list was changed once, mid-project, in a direction that added rows to it (Section \ref{sec:method}). Read the rows, not the tally.

The temporal row deserves a sentence, because it is where intuition is strongest. Safe Rust's protection against use-after-free is a guarantee about the allocator: it attaches to a `free`. Where a structure does free per node — a handle table over per-record allocations — the guarantee cost zero instructions in the allocator, because the free and the invalidation are one operation in safe Rust and two in C. A structure that recycles its own storage never frees, and its use-after-recycle is writable in safe Rust with zero `unsafe`, silently wrong, with Miri reporting nothing. The six temporal programs here do not agree: the free-list pool's safe version reproduces the C bug bit for bit, an intrusive-list program cannot reproduce it at all because the representation Rust forces removes the mechanism along with the pointers, and a reference-counting program shows both outcomes, selected by which representation the porter chose.

Three results run the other way. One is measured: the one-byte overflow above, where every safe version returns the reference answer and the plain C is silently wrong in seven of eight builds. Two are not visible in any instruction count. An overlapping `memcpy` cannot be written in safe Rust: the borrow checker refuses two live names into one buffer, the compiler's message suggests splitting the buffer into non-overlapping halves, and the only safe spelling of an overlapping move is `copy_within`, which has `memmove` semantics and costs 0.4% and 0.1% more than the unsafe version. On this machine's C library the hardened-C fix, `memcpy` to `memmove`, costs nothing, since both names resolve to one address; the trouble is that the wrong one runs, returns a plausible answer, and nothing objects. And a strict-aliasing miscompile does not occur in unsafe Rust either, because Rust has no type-based aliasing rule to violate. It is not a speed win in C: under gcc the undefined spelling costs 6 instructions per call more than five well-defined C spellings of the same read, one of which is a compiler flag, and under clang four of them compile to the same bytes as it. The one well-defined C spelling that costs more is a two-half read, the shape Rust is forced into, at +12 instructions per call under gcc and +32 under clang.
