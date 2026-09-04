\section{How this measurement lied to itself}
\label{sec:lied}

%% Opens on what HELD, ~60 words. This section is not a confession of chaos and
%% must not read as one -- the retractions are worth reading only because the
%% process that produced them also produced results that survived it.
%%
%% ⚠ ver_A wrote "nineteen claims were retracted" with no denominator and the
%% reader's advocate flagged it as trust-destroying ("nineteen of how many?").
%% The count is not led with here and no ordinal replaces it.
%%
%% Sources read directly at writing time, not taken from the summary:
%%   retraction 1  .memory/03-measurement.md, "THE CONTROLS THAT COULD NOT HAVE
%%                 FIRED" entry 1; the rank case from results/SYNTHESIS.md §3
%%   retraction 2  RECAP.md, the TASK_031/TASK_032 layout block
%%   retraction 3  results/SYNTHESIS.md, "A gap in this document rather than in
%%                 the project"
%%
%% ⚠ The \figure line must stay on ONE line -- a wrapped one used to vanish
%% silently and take its \label with it.
%%
%% If a trim agent needs words, cut in this order: the two named statistics in
%% retraction 2, then the cause sentence in retraction 3. Every "The rule."
%% paragraph is the reason its retraction is here at all -- do not cut one.
%%
%% ⚠ TENSE (REVISE F16). "the new field's name appears zero times in that
%% generator" was true when written and is FALSE NOW -- `synthesis/synthesize.py`
%% reads the field today. Past tense, and say when.
%% ⚠ PLACEMENT (REVISE F17). The exact-fit hold-out is NOT an entry on
%% `.memory/03-measurement.md`'s "controls that could not have fired" list; it is
%% elsewhere in the same file. "Beside it in the same file", never "its
%% neighbour on the list".
%% ⚠ RETRACTION 3 IS PROTECTED (REVISE part E) -- compress the anecdote if you
%% must, never the rule.

**Start with what held.** Every pattern here was built by one agent and then
attacked by a different one whose job was to break it. All
\num{totals.patterns} pass the gate with zero failures;
\num{totals.verus_verified} items verify across the shipped rungs at
\num{totals.verus_errors|plain} errors; \num{totals.adversarial_runs} adversarial
runs stand behind \ref{sec:tools}. What follows is three traps in the apparatus,
each of which would recur in any benchmark of this shape.

\begin{retraction}{The control came back byte-identical, so nothing moved}
A field was added to 22 gate records, the tables were regenerated, the output
came back byte-identical, and that was quoted as evidence nothing had moved.
**It was byte-identical because the generator read a different key.** The new
field's name appeared nowhere in that generator at the time, so the control
could not have fired whatever the change had been. Beside it in the same file is
the same trap from the other end: a hold-out that re-derives the same exact
solution after any drop, so a residual of exactly zero was guaranteed in
advance.

**The rule.** Before believing a check, ask what would make it fail — then make
that happen. Pick the check in your pipeline that has never gone red and break
the thing it watches. **A residual of exactly zero is not a strong pass; it is
the signature of a test that could not fail.**
\end{retraction}

\begin{retraction}{The shipped binary is the slowest of 31 layouts}
This is why this paper quotes no wall clock, and the failure is in the protocol,
not the physics. The probe gave each cell a contiguous block of repetitions
instead of alternating, and the effect then **reproduced at zero layout
variation, on byte-identical copies**. That pattern's real noise floor is 5–45 %
on identical binaries, wider than any gap read off it. Two wall-clock rows were
withdrawn, and two statistics with them — both extrema, the second introduced as
the fix for the first. The hazard is old \cite{mytkowicz09} \cite{stabilizer13}.

\figure{spread}{Rung-to-rung wall clock over builds of identical machine code; each band is one comparison's range across layouts, each tick one build.}
\label{fig:spread}

**The rule.** Interleave by cell, never by block. Measure your own noise floor on
byte-identical copies before believing any timing effect; if the floor is wider
than the effect, you have not measured the effect. Never publish an extremum, and
never repair one extremum with another.
\end{retraction}

\begin{retraction}{The summary is faithful: every figure reproduces}
That was true, and it was not the question. When this project compressed
\num{totals.patterns} patterns into four results, its own review found the
omissions ran **systematically one way**: five reviewed, quotable results went
missing, and every one flattered safe Rust.

**The rule, and it is the hardest here. Coverage bias has no arithmetic
signature.** Every figure in the biased version reproduced correctly on the pass
that found the bias; there was nothing to recompute, because nothing was wrong.
Checking a document's numbers cannot detect it. The only check is a different
question, asked of a finished document: **which way do its gaps point?** Ask it
of your own migration report before you send it.
\end{retraction}

Ask it of this paper too. **Read every figure here as a bound with one endpoint
held fixed by decree**, and **quote the mechanism, not the magnitude** — why a
check survives or is elided reproduces on code this project never built, while
the magnitudes belong to one box, one pin and one pair of spellings.
