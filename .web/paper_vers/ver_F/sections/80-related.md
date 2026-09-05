%% Related work, compact, six paragraphs, each ending in what this study adds.
%% ⚠ CLAIMS.md 3.10: no quotation from a published paper is made here; every
%% sentence is a characterisation, so nothing needs a page-ranged read.
\section{Related Work}
\label{sec:related}

**Why memory safety.** The figure that about seventy percent of serious vulnerabilities are memory-safety bugs comes from Microsoft's and Chromium's own bug data \cite{msrc19}\cite{chromium}, and Android has reported the share falling as new code moved to memory-safe languages \cite{android22}. Those studies count bugs; this one prices the mechanisms that would have stopped them.

**Making C safe.** Checked C \cite{checkedc18} adds bounds-carrying pointer types to C; CHERI \cite{cheri15} moves bounds into hardware capabilities; SoftBound and CETS \cite{softbound09}\cite{cets10} add spatial and temporal checks by compiler instrumentation, at the overheads that motivated language-level approaches; AddressSanitizer \cite{asan12} is the detector we run. Our hardened C is the cheapest member of this family — one hand-written check — and Finding 4 is its price.

**Rust and unsafe Rust.** Studies of Rust in the wild \cite{astrauskas20}\cite{evans20}\cite{qin20} find unsafe code common and memory bugs concentrated in it. RustBelt \cite{rustbelt18} proves the safe language sound given correct unsafe libraries, and Stacked Borrows \cite{stackedborrows20} is the aliasing discipline Miri checks on our unsafe versions. Finding 8 is the run-time complement: what the safe language's guarantee does and does not attach to, measured on programs with a C twin.

**Translating C to Rust.** c2rust \cite{c2rust} produces unsafe Rust; Laertes \cite{laertes21} and later work lift raw pointers toward safe references; a user study of human translators \cite{userstudy25} found their safe Rust mostly within 20% of the C and sometimes faster, which is consistent with our tuned versions and not with our ports. None of these hold the program fixed across safety mechanisms, which is what this study adds.

**Verifying Rust.** Verus \cite{verus23} is the prover we use; Prusti \cite{prusti19}, Creusot \cite{creusot22} and Kani \cite{kani22} verify Rust by other means. Constant-time verification \cite{ctverif16}\cite{jasmin17}\cite{fact19} addresses exactly the trace property Finding 10 shows a value logic missing, and a constant-time-preserving compiler \cite{compcertct} addresses the half of the problem that begins after the prover has finished.

**Measurement.** Mytkowicz et al. \cite{mytkowicz09} showed that environment size and link order alone can invert a performance conclusion, and Stabilizer \cite{stabilizer13} randomises layout to make such effects statistical. Finding 5's layout control is the same effect, measured on byte-identical code with the instruction count held fixed.
