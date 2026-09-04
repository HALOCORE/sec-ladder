\section{Will your existing tools tell you?}
\label{sec:tools}

%% Opening sentence is ver_A 40-hostile.md verbatim -- the best line in the old
%% paper, and it puts the reader in their own incident channel.
%%
%% ORDER (OUTLINE §0.4): headline -> example -> principle -> blind spots ->
%% positive control -> figure -> caveat. ⚠ THE CAVEAT AND ITS PLACEMENT AFTER
%% THE HEADLINE AND EXAMPLE ARE PROTECTED (REVISE part E).
%%
%% R6 -- these scope clauses are mandatory; a reviewer treats a missing one as a
%% blocker, so each is welded into the sentence carrying its number:
%%   * 51/143 is ONE build config -- gcc -O1 -fsanitize=address,undefined,
%%     isolated, kernel.c only. No clang, no hardened rung, no Rust.
%%   * _FORTIFY_SOURCE is Ubuntu gcc's DEFAULT at -O2/-O3, not a flag
%%     harness/build.py passes, and the discriminator is the `_chk` symbol rather
%%     than the compiler. The one-byte overflow's 8th build likewise aborts
%%     because of the DISTRIBUTION.
%%   * the shift blind spot is ASan's ALONE. "not ASan, not Miri, not a proof"
%%     was refuted in-tree, and there is no ASan-only build here, so the claim is
%%     argued from the defect's shape and is labelled that way.
%%     ⚠ REVISE F7: EIGHT patterns are UBSan-only, so the superlative that stood
%%     here ("the one pattern whose sanitizer row is UBSan's") is FALSE. What is
%%     defensible is the defect's shape: it never leaves the object.
%%   * "nothing catches an infinite loop" holds of the static instruments only;
%%     a `decreases` clause and a plain `timeout` both catch it. What is true is
%%     that no rung's language EMITS the capacity test.
%%
%% R4 -- the deleted-check control holds on 4 of the 8 patterns that have one,
%% is conditional on 2 and false on 2, and that clause goes BEFORE the artefact.
%% REVISE part C4 requires ONE FALSE CASE WITH ITS NUMBERS: without it the beat
%% is a full table where safe Rust wins beside a clause where it does not, which
%% is the gap direction §6 warns about. ⚠ The TLV table's C row is the SHIPPED
%% rung and gate-certified; its three Rust rows are `.temp/` scratch with no
%% committed generator (REVISE F8) -- say both.
%%
%% ⚠ \figure{}{} MUST BE ON ONE LINE -- paper.js matches it with a single-line
%% regex and silently drops a wrapped one, taking its \label with it.

The interesting question about a memory-safety bug is not whether it is
dangerous. It is what you would have seen in your logs. You already have an
answer: ASan and UBSan in CI, a nightly fuzzer, everything green, no crash in
months. The question is what that is evidence *of*.

Take the plain, unchecked C rungs and ask, per row, what the worst thing they
did was. Of \num{totals.plain_c.rows} rows —
one pattern on one adversarial input across both C compilers and four builds —
plain C matched the model everywhere on \num{totals.plain_c.clean}. **Of the
\num{totals.plain_c.deviating} that deviated,
\num{totals.plain_c.silent_first} were silent**: exit 0, a plausible wrong
answer, no diagnostic. \num{totals.plain_c.crash_silent_first} crashed;
\num{totals.plain_c.hung} never returned.

That depends on an aggregation rule. Those figures score a row silent if any
build was silent; let a crash outrank silence instead and the same rows read
\num{totals.plain_c.loud_first_silent} silent and
\num{totals.plain_c.crash_loud_first} crashed, the two rules differing on
exactly \num{totals.plain_c.build_split} rows where one source on one input is
silent in some builds and crashes in others. Silence dominates either way.

\begin{example}{A one-byte overflow that returns success}
A length-prefixed record is copied into a fixed 64-byte destination, and one
adversarial input overruns it by exactly one byte. Plain, unchecked C prints
`198979479034752` and exits 0 in **seven of the eight** plain C builds: the
overflow lands inside glibc's chunk rounding, so nothing is corrupted and
nothing detected. The eighth aborts, and that is the distribution's doing —
Ubuntu gcc's default `_FORTIFY_SOURCE=3` at `-O3`, one of eight builds of one of
three attacks. Scope: one pattern, one input, one libc, and the *one-byte* case,
because the same pattern's 65,535-byte overflow aborts loudly, destroying the
next chunk header. **The realistic overflow is the invisible one**; the
spectacular one your monitoring already catches.
\end{example}

\begin{principle}{A silent detector and an absent detector are one observation}
A detector that reports nothing and a detector that never ran produce the same
log line. No silence is evidence until that tool, in that build, on that box,
has been seen reporting something.
\end{principle}

**Hardening blinded the sanitizer**, and not by a bug in ASan. A genuinely
overlapping `memcpy` draws no report: fortification rewrites the call to
`__memcpy_chk`, and ASan's overlap check lives in its `memcpy` interceptor, no
longer on the path. Isolated to that flag on identical source — gcc at the box
default silent, gcc with `-D_FORTIFY_SOURCE=0` reporting
`memcpy-param-overlap`, clang with fortification forced on silent too — the
discriminator is the `_chk` symbol, not the compiler. That flag is Ubuntu gcc's
default at `-O2` and `-O3`, not one this project passes.

**A defect that never touches memory.** A LEB128 decoder shifts past the width
of its type. Nothing goes out of bounds, so ASan is silent on every input and
every rung — the one defect here that never leaves the object at all. The blind
spot is ASan's alone: UBSan fires, Miri fires as a panic, the prover fires. It
is argued from the defect's shape, not isolated by an ASan-only build.

**Non-termination.** A hash probe on a full table spins forever: ASan and UBSan
on the C rung print nothing, and Miri on a safe-Rust control with the guard
removed had not terminated in 90 seconds. Not *nothing catches it* — a
`decreases` clause catches it at compile time, a `timeout` at run time. What no
rung's language does is **emit** the capacity test; the five that terminate
write it by hand.

So add a positive control, and make it Monday's first job: put a known-bad input
into the sanitizer run and fail the build when it is **not** reported. Here every
input declares whether the sanitizer must be clean or must fire, and in the one
configuration that runs them — gcc `-O1 -fsanitize=address,undefined`, isolated,
`kernel.c` only, no clang, no hardened rung, no Rust — it fired on all
\num{totals.sanitizer.declared_fires} inputs declared to require it and was
clean on the other \num{totals.sanitizer.clean}.

\figure{outcomes}{The worst behaviour each rung produced on any adversarial input. Every rung above plain, unchecked C — hardened C included — matches the model everywhere. Read it with its limit attached: the Rust rungs are the fixed program and the plain C rung is the one carrying the bug, so this chart counts a design choice at least as much as a language difference, and not one bounds check fires anywhere in it.}
\label{fig:outcomes}

The scoreboard judges exit code and standard output, so a memory leak and a
timing leak both score as *matched*: absence of deviation is not absence of a
bug.

\begin{caveat}{What the outcome matrix does not measure}
\ref{fig:outcomes} reads as "C corrupts memory, Rust catches it", and it does
not. The Rust rungs are the **fixed** program and the C rung the **buggy** one.
**Not one bounds check fires anywhere in the shipped matrix**:
\num{totals.loud|plain} of \num{totals.adversarial_runs} adversarial runs end
with a rung refusing to continue where the model says exit 0, and every non-zero
exit under attack is a driver-level rejection the C rungs produce identically
\src{results/gate/*.json}. The matrix largely measures a design choice — the bug
was written in C, not Rust.
\end{caveat}

Where safety is genuinely attributed, a **deleted-check control** does it:
remove the mechanism, change nothing else, rerun the input. Eight patterns carry
one and they disagree. On four, deleting the safe rung's bound test turns silent
corruption into a panic; on two, the stripped rung prints C's answer bit-for-bit
and exits 0 in the in-bounds regime. **And on two it is false: strip the shift
bound from the varint decoder and safe Rust prints the same 64-bit integer as
plain C on every adversarial input** — the same integer, not a similar one, at
both optimisation levels this benchmark measures, exit 0, no panic. It panics
only under `-C debug-assertions=on`, which the matrix does not build and which
costs that safe rung 23 instructions per byte
\src{patterns/p18-varint-shift/NOTES.md}. The other is a hash probe that hangs.

The clearest is a TLV walker \pat{p16}. Delete one line —
`if vlen > end - (p + 3) { break; }` — from each rung and run a window whose
last record declares a length that does not fit:

| the same omission | on the overrun input |
|---|---|
| plain C — the **shipped** rung | exit −11, SIGSEGV, silent |
| unsafe Rust, line deleted | exit −11, SIGSEGV, **identical to C** |
| safe Rust, line deleted | **exit 101**, `index out of bounds: the len is 3072 but the index is 3072` |
| the proved rung, line deleted | **will not build**: `invariant not satisfied before loop: p + 3 + vlen <= end` |

**And every rung that builds still prints the correct checksum on both well-formed
blobs and on the truncated adversarial input**: the bug is invisible on the happy
path in every one of those languages, and on a malformed input that happens not to
trip it. Read the rows with their provenance — the C row is the shipped rung and is
gate-certified; the three Rust rows are line deletions from the shipped sources,
rebuilt and re-run by a committed generator \src{.web/insights/p16_control.py},
and certified by no gate.

Monday's second job: **delete one check in a branch and run your test suite.**
If nothing goes red, that check is untested.

\begin{takeaway}
Hardened C is correct on these inputs too — every rung above plain C matches the
model on every adversarial input — so this corpus **cannot** distinguish
hardened C from Rust on outcomes. If you are not rewriting it, harden it;
\ref{sec:cost} prices that check. What the rewrite buys is narrower: the omission
that gives C a silent heap write gives safe Rust a named, non-exploitable abort,
and the proved rung a compile error.
\end{takeaway}
