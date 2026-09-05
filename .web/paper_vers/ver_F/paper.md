%% ver_F -- the manifest.  \input in reading order and nothing else.
%%
%% A CONVENTIONAL EMPIRICAL-STUDY PAPER.  The shape is the one a reader of
%% TaxDC (ASPLOS 16) or the C-to-Rust user study (NDSS 25) already knows, and
%% that familiarity is most of the readability: abstract, introduction ending in
%% a bulleted summary of findings, methodology with its limits stated early,
%% results organised by research question with one numbered Finding box per
%% result, lessons, threats to validity, related work, conclusion.
%%
%% THE RULES THAT GOVERN EVERY SECTION, all paid for by earlier versions
%% (PITFALLS.md 1.1-1.11):
%%   * a Finding box is one or two sentences a reader could quote; the
%%     paragraphs under it are only its evidence, and each finding is
%%     demonstrated ONCE;
%%   * claim, one concrete picture, so what -- never claim, scope, denominator,
%%     counterexample, qualification;
%%   * any two numbers on the page will be subtracted or divided by the reader,
%%     so every ratio stated must close from what is printed;
%%   * corpus totals are \num{} and never literals; per-program measurements are
%%     literals and each carries a %% comment naming its primary source;
%%   * no apparatus vocabulary without a definition: version not rung, program
%%     not pattern, the measured function not the kernel, the checker not the
%%     gate, build not cell;
%%   * no reference to earlier versions of this document, anywhere.

\input{sections/00-abstract.md}
\input{sections/10-intro.md}
\input{sections/20-method.md}
\input{sections/30-cost.md}
\input{sections/40-reach.md}
\input{sections/50-proof.md}
\input{sections/60-lessons.md}
\input{sections/70-threats.md}
\input{sections/80-related.md}
\input{sections/90-conclusion.md}
