%% RQ3 -- the proof.  Three findings.
%%
%% PRIMARY SOURCES:
%%   identity 28 exact / 5 norel     results/gate/*.json `identity` (re-derived this
%%                                   session); live as totals.passing.identity_exact
%%   p36 26-byte stub, 40 vs 32      SYNTHESIS §4 "One scope clause"; CLAIMS 1.19
%%   497 verified / 0 errors         live totals
%%   17,526 = 35% of the NUL scan    p11/NOTES.md:942-953, :1019-1020; unsafe large
%%                                   50,160 off synthesis.md §1; "four `is not
%%                                   supported` errors" SYNTHESIS §1
%%   p11 proof-enabling guard 8.5%   p11/NOTES.md:432, :456 (via ver_E comments);
%%                                   CLAIMS 2.3; 1 Ir per scanned byte, 4,265 on large
%%   3.00000 Ir per dispatch         p36/NOTES.md:37-38, :122; SYNTHESIS §4
%%   ct-compare u_win 24 cheaper     SYNTHESIS §4 ("A second, smaller instance sits on p47")
%%   kernel spec (requires/ensures)  patterns/p09-bitset/verus.rs:443-447, verbatim
%%   _msonly strips the ensures      patterns/p09-bitset/controls/gen_controls.py:66-70
%%   bitset mutant table             RECAP.md finding 19; SYNTHESIS §3; scopes: bounds
%%                                   check on the SAFE mutants, ASan on the HARDENED C
%%                                   at gcc -O1, Miri on the UNSAFE copy; CLAIMS 1.21:
%%                                   mutants from a committed generator, not gate-certified
%%   honest proof three ghost lines  p09/NOTES.md:488-495
%%   hint line on both proof rows    ver_E fact-check (p09 _msonly built FROM the hinted one)
%%   range parser 9/1, 10/0          p17/NOTES.md:26-34; SYNTHESIS §3
%%   ct-compare +7,088, contract     p47/NOTES.md:656, :1015; CLAIMS.md 1.8 (KERNEL count)
%%   proof text 386%, comments 38%   live totals.passing.proof_text_ratio_pct; the
%%                                   stripped ratio rises -- ver_E fact-check
%%   two first-try proofs; ~2 s / ~8 min  ver_E fact-check against pattern notes
%%   TCB 152 items / 333 lines       live
%%   obligations r = 0.92 with size  SYNTHESIS §5 (0.920 at 33; dead-code arm 5 vs 4)
%%   assume_specification vacuity    .memory/04-verus.md:1423-1446; synthesis.md §3
%%   trusted body unchecked (p08)    SYNTHESIS §4 (copy_nonoverlapping inside move_right
%%                                   verifies 11/0; Miri and identity catch it)
%%   gate blind to ensures prose     SYNTHESIS §4 ("nothing in this project's gate checks
%%                                   that an ensures means what its prose says")
%%
%% ⚠ THE SPECIFICATION IS SHOWN, verbatim from verus.rs.
%% ⚠ p42 (affine token / ghost ledger) is CUT: it needs linear types to follow
%% and SYNTHESIS §4 calls it "the least safe to paraphrase".
%% ⚠ CLAIMS.md 1.7: never "the CVE port verifies clean".
%% ⚠ CLAIMS.md 1.16: proof totals are over the measured versions.
%% ⚠ CLAIMS.md 3.7: say once that Verus counts ITEMS, not verification conditions.
\section{What a Proof Costs and What It Proves}
\label{sec:proof}

Verus \cite{verus23} is a verifier for Rust. Separately from the code, in logic rather than in Rust, the author writes what the function must do and where it is allowed to read; the prover reconciles the two with an SMT solver \cite{z3}, and if it cannot, the code does not compile. Across the measured versions Verus reports \num{totals.passing.verus_verified} verified items — functions, loop bodies and sub-proofs, not individual conditions — and \num{totals.passing.verus_errors} errors.

\subsection{Zero instructions, by rule}

\begin{finding}{A proof costs zero instructions because we required it to; the price is what the prover lets you write}
On \num{totals.passing.identity_exact} of \num{totals.passing.patterns} programs the verified and unsafe versions are byte-identical at `-O3`; on the rest the instruction stream is identical and only link addresses differ, except one program where the proof leaves a 26-byte function nothing calls. The cost moved into expressiveness: on a NUL scan a faster unsafe version, 17,526 instructions per call cheaper, was refused because the prover rejects it.
\end{finding}

The zero is not a discovery. Section \ref{sec:method} made it a rule, and the rule has a price paid on one side of every comparison in this paper: the unsafe version may only use what the prover's pinned standard library can specify, while the safe version is bounded by nothing. On the NUL scan somebody wrote the unsafe version around the standard library's own byte scan — the routine the safe version already uses at no cost — and measured it 17,526 instructions per call cheaper on the large input, about a third of the measured unsafe version's 50,160; the prover rejects it with four unsupported-feature errors, so it was refused. Two smaller instances: on a dispatch table the prover cannot type a plain function pointer, so every Rust version uses trait objects instead, at exactly 3 instructions per dispatch more than C's mechanism; and on a constant-time compare a version 24 instructions per call cheaper was excluded because its machine code differed from its verified twin. The proof can also add code: on the NUL scan a guard that exists only to make the proof go through costs one instruction per scanned byte, 8.5% of that function, and was described as free until somebody deleted the line and measured.

So the honest form of "what a proof costs" is two numbers: zero instructions for the proof itself, and whatever the prover's expressiveness costs in the code you are then allowed to write. The second is a floor, priced only on those three programs where somebody built the excluded version and measured it.

\figure{identity}{Byte-identity between the unsafe and verified versions at `-O3`, and the proof totals over the measured versions.}

\subsection{A proof of what you wrote down}

\begin{finding}{A memory-safety proof certifies a wrong answer that stays in bounds}
Change `q >> 6` to `q >> 7` in the bitset and the index is still legal: the bounds check, the sanitizer, Miri and a memory-safety-only proof all pass, and the program prints the wrong answer. Only a specification that also says what the answer must be refuses to build.
\end{finding}

Here is the whole specification of the bitset's measured function, verbatim. The `requires` line is the memory rule: the window the caller names must lie inside the buffer. The `ensures` line is the answer: the result must equal a mathematical definition of the fold, written separately in the prover's logic.

```rust
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == bitset_fold(buf@, off as int, len as int),
```

The function finds bit `q` in word `q >> 6`. Type a `7` for the `6` and the word index is smaller, so it cannot overshoot where the right one did not; this is the first row of Finding 8's table. We put that one character into each version's own copy — one-line variants generated by a script, not measured programs — and pointed everything in the project at it, including the proof twice: once with the `ensures` line and the loop invariants that carry it removed, so that only the memory rule remains, and once complete.

| instrument | verdict |
|---|---|
| the bounds check safe Rust compiles in | never fires; exit 0, wrong answer |
| AddressSanitizer and UBSan, on the hardened C | silent on every input; exit 0 |
| Miri, on the unsafe copy | exit 0, reported nothing, wrong answer |
| the proof, with the `ensures` removed | verifies the buggy version |
| the proof, complete | refuses to build: `invariant not satisfied` |

Every instrument but the last watches the same boundary, the edges of an allocation, so four of them agreeing is not four confirmations. Both proof rows carry one extra line that exists only to help the prover along and that the measured program never needed, so what the table shows is the difference between those two rows. Moving the specification to match the typo does make the prover verify the bug, but the edit is the specification's own arithmetic plus two assertions over four lines of proof — more than the three lines the honest proof of that step needed.

The same shape shipped as a real vulnerability. The HTTP range parser is a port of a suffix-range parser missing one test. Guard the index against the whole buffer the function was handed — the slice, which is exactly what a bounds check checks — and every memory-safety obligation discharges. The one obligation that fails is the one about the answer: `9 verified, 1 error`. Remove it and the verdict is `10 verified, 0 errors`: memory-safe, and reading a neighbouring window's bytes. And in the constant-time compare, adding an early exit to the verified version leaves the specification unchanged, the measured function's verified-item count unchanged, every checksum identical, and leaks +7,088 instructions per call between two inputs: a property of the trace is invisible to a logic about values.

> A proof is a proof of what you wrote down, and the count of verified items does not tell you what that was.

\subsection{The proof burden and the trusted base}

\begin{finding}{Proof text runs to about four times the code, resting on \num{totals.passing.tcb_items} items the prover takes on trust}
Over the measured versions, proof files are \num{totals.passing.proof_text_ratio_pct}% the length of the unsafe files they prove. Underneath sit \num{totals.passing.tcb_items} trusted items — hand-written declarations the prover accepts without checking — totalling \num{totals.passing.tcb_lines} lines, plus a pinned standard library whose own trusted surface is larger and is not counted here.
\end{finding}

The obvious discount — that most proof text is comments — runs the wrong way: strip comments and blank lines from both sides and the ratio rises. Nor is the burden uniform: on four programs the proof went through first try, and on three of them the notes record the session budgeted for it going unused.

Four things a reader should know before using those counts. The verified-item count is a size proxy: across the corpus it correlates 0.92 with the size of the proof text, and between two variants of one program — one adding code that never executes, one adding a real check — it is higher for the dead code, so it says nothing about what a proof covers. Nothing checks a trusted item's body: substitute a non-overlapping copy for the overlapping one inside the overlapping-copy program's single trusted function and the proof verifies unchanged while the program commits its own bug — only Miri and the byte-identity rule caught it. The verifier's own escape hatch is vacuous: when Verus meets a function it has no specification for, it prints one for you to paste, carrying no preconditions and no postconditions, and pasted for a raw-pointer read it verifies a one-megabyte out-of-bounds read at `4 verified, 0 errors`. And no measurement here records the time a proof took to write. One program records the prover's wall time, about two seconds; none records authoring effort, and nobody ran the experiment a maintainer would ask for: change one line of a verified function and count the lines of proof that break. Every price in this section is a floor.
