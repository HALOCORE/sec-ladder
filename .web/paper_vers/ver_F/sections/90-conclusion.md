%% Four sentences.  No new numbers, no restatement of every finding.
\section{Conclusion}
\label{sec:conclusion}

We held \num{totals.passing.patterns} small programs fixed and varied only what enforces their memory safety, from nothing to a machine-checked proof. The cost of memory safety turned out to be a property of a pair of programs rather than of a language, and the pair matters more than the safety. Under attack, plain C was the only version that ever misbehaved, and what the safe language buys over the same C with its check written in is not a different outcome but a check that cannot be left out unnoticed. A proof adds nothing to the cost and proves exactly what its author specified — which, for a memory-safety specification, excludes every wrong answer that stays in bounds.
