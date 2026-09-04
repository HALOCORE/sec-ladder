%% ver_C -- the manifest. \input in reading order and nothing else.
%% Every line of prose lives in sections/, so this file is the paper's table of
%% contents in source form. See ../README.md for the format.
%%
%% THE ORDER IS AN ARGUMENT and it was stress-tested against three alternatives
%% (.temp/brief/OUTLINE.md part 0.1). The reader arrives holding a cost number.
%% §1 destroys one, on one kernel, with numbers in sentence one. §2 shows the
%% destruction generalises. §3 shows BOTH endpoints of every such number move,
%% including ours, and ends by naming the operation the two halves share. §4 runs
%% that operation where it FAILS and needs a different move. §5 is the bound on
%% the whole method, and it is the strongest fact in the paper, so it must arrive
%% AFTER the method is on the table or it is merely a curiosity about Rust
%% panics -- which is the framing this version exists to correct. §6 spends the
%% credit. §7 tests the method on the paper. §8 restates, narrower.
%%
%% Half-B-first was rejected on three grounds, the third fatal: `remove the
%% mechanism and re-measure` is established in Half A and FAILS in Half B, so
%% running B first shows the reader the failure before the method, inverts the
%% hinge, and makes `resource` look like a coinage rather than a consequence.
%%
%% ⚠ There is no limitations section, on purpose. Every caveat is filed beside
%% the claim it bounds (CONVENTIONS.md 2.6), which is what moves the proportions
%% from ver_B's 67/17/4 to 47/6/19. `70-caughtitself.md` is NOT that section: a
%% limitation says our evidence does not reach X, a retraction says we asserted
%% X and it was false. Only the first was abolished.

\input{sections/00-summary.md}
\input{sections/10-onekernel.md}
\input{sections/20-notthecheck.md}
\input{sections/30-bothends.md}
\input{sections/40-allocation.md}
\input{sections/50-nonoptional.md}
\input{sections/60-measureinstead.md}
\input{sections/70-caughtitself.md}
\input{sections/99-close.md}
