%% ver_A -- the practitioner's section, and the only one about the READER's code
%% rather than about this corpus.  It ASSEMBLES; it introduces no evidence.
%% Every item \refs the section that establishes it, and any figure here must
%% already be published there in the same units.
%%
%% Item 4's ratios are a `wc -l` over all unsafe.rs/verus.rs pairs under
%% patterns/, counted for sec:proof.  Spelled out rather than \ref'd because the
%% item tells the reader to repeat the count on their own tree.

\section{What to do}
\label{sec:whattodo}

Suppose the decision is already yours. There is a C parser in production,
somebody has proposed rewriting it, and the argument in the room is about a
percentage. Nothing here settles that argument, because the percentage is not a
constant. What the measurements do supply is an order in which to ask the
questions — six of them, all established elsewhere in this paper, and none of
them requiring you to believe a number of ours about a kernel of yours.

1. **Ask where the bound comes from, before you count bounds checks.** If the
   fact that discharges the check is already in front of the optimiser — a clamp,
   a modulus, a slice reborrowed once outside the loop, a length the caller
   already tested — the check leaves the loop and costs a flat per-call constant,
   frequently exactly zero. That is a property of the code and not of the
   language: hand the same fact to a C compiler and it deletes the same check.
   The question to ask of a candidate rewrite is not *"how many bounds checks
   does it have"* but *"where does the bound come from, and does the compiler get
   to see it there?"* \ref{sec:cost}
2. **If the bound is true but not derivable, expect a real per-element tax that
   amortises along nothing.** The worst case measured here is about half of a
   kernel — and that fraction has a denominator worth reading, because the kernel
   in question does nothing but probe an array: no parsing, no allocation, no
   logging to dilute it, so the same absolute per-element cost is a much smaller
   share of any function that does real work around the loop. Measure your own
   kernel and take your own fraction. Do not carry this one into it.
   \ref{sec:cost}
3. **If you are not going to rewrite it, harden it.** Every rung above plain C in
   this corpus — the hardened C rung included — matched the reference model on
   every adversarial input, and writing the check costs about the same number of
   instructions in C as in Rust. The whole measured difference is that the C
   check protects you only where you remembered to write it, which the
   deleted-check control makes concrete: the same one-line omission that gives C
   a silent one-byte heap write gives safe Rust an immediate, named abort.
   \ref{sec:hostile}
4. **Budget a proof at zero instructions and about four times the source.** The
   compiled kernel is byte-identical to the unproved one, and what you are really
   buying is a text count you can repeat on your own tree: `wc -l` over all
   \num{totals.patterns} `unsafe.rs`/`verus.rs` pairs here gives
   \num{totals.proof_text.unsafe_lines} lines against
   \num{totals.proof_text.verus_lines} — an aggregate of 4.04×, a per-pattern
   median of 4.24×, from 2.60× on the state machine to 6.29× on the buffer copy.
   Buy it for memory safety and for nothing else: it says nothing about how long
   the kernel takes, whether it computes the right answer, whether it terminates,
   or what was left in a slot you recycled. \ref{sec:proof}
5. **Before attributing a measured gap to safety, find the instructions and read
   them.** Several of the largest safe-versus-unsafe differences in this corpus
   turned out to be an unroll decision, out-of-line drop glue, and an iterator
   adaptor's two exhaustion tests per item — no bounds check in any of them, and
   one running in safe Rust's favour. A difference between two binaries is
   evidence about two binaries and nothing more. \ref{sec:cost}
6. **None of this is about concurrency.** Every kernel here is single-threaded,
   no pattern models a data race, and the guarantee much of Rust's audience means
   first is therefore not on the instrument at all. If that is the guarantee you
   are buying, nothing in this paper is evidence for it or against it.
   \ref{sec:limits}

Every step is something you do to your own code. Not one of them is a number you
can quote.
