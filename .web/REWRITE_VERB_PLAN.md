# REWRITE_VERB_PLAN — build `paper_vers/ver_B`

**This file is written to be executed cold, after the conversation that produced
it is gone.** Everything needed is here or named by path.

---

## 0. THE ONE RULE

> **Every concept enters through a problem the reader already has, and only
> after the obvious answer to that problem has been shown to fail.**

No concept is introduced because it is elegant, symmetric or complete. If a
paragraph defines something before the reader has been hurt by not having it,
the paragraph is in the wrong place or should not exist.

**Test to apply to every abstraction in the draft, mechanically:**

1. Name the concrete question a working developer arrived with.
2. Name the answer they would obviously try.
3. Show that answer failing — **with a measurement, not an argument.**
4. *Only now* introduce the distinction that survives.
5. Give it back to them as something they can do on Monday.

If any of 1–3 is missing, the concept is unmotivated. Cut it or fix it.

---

## 1. WHY ver_A FAILED — do not repeat this

ver_A is at `paper_vers/ver_A/` and **stays**. It is not deleted, not edited.
It is a different framing and the directory structure exists for exactly that.

Its defect, in the user's words: *"abstraction just for self-fun, NO CLEAR
MOTIVATION."* Concretely:

- **It introduces its central abstraction (the "guarantee quadruple") as a
  framework in §8 and then finds instances for it.** The reader is asked to
  accept four coordinates before any of them has been needed.
- **A third of its word count is about how the paper might be wrong** — method,
  limits, retractions — before the reader has been given anything to be wrong
  *about*.
- **17,400 words.** The practitioner review's verdict was *"the research is
  better than the paper"* and *"would you forward this to your director? No."*
- Its one developer-facing section (`15-whattodo.md`) is good and is **buried at
  §2 of 13**, after which the paper returns to abstraction for 15,000 words.

⚠ **The abstraction itself is not the problem and must not be thrown away.** The
property/bearer/quantifier/residual distinction is real and it is what explains
three programs in this corpus that verify and are broken anyway. **It is
correctly motivated in ver_B by arriving fourth, after three concrete failures
have made it necessary.**

---

## 2. WHO ver_B IS FOR

**A working developer or tech lead who has a C or C++ codebase and is being
asked whether to rewrite part of it in Rust, or has already started and wants to
know what it costs and what it buys.** Undergraduate-readable. No prior
knowledge of Verus, formal methods, or this project.

They arrive with three questions, in this order, and the paper is those three
questions:

1. **What will it cost me?**
2. **Will my existing tools tell me if I'm wrong?**
3. **If it's memory-safe — or even proved — am I done?**

Question 3 is where the abstraction is *earned*, because the honest answer is
"no", and saying why requires vocabulary the reader does not yet have.

---

## 3. THE SPINE — problem → failure → concept

This is the plan's core. Build the paper on exactly these four movements.

### Movement 1 — "What will it cost me?"

| | |
|---|---|
| **Problem** | We're rewriting a parser in Rust. How much slower will it be? |
| **Obvious answer** | Benchmark it. Read a published number. |
| **How it fails, measured** | The number is not a property of the languages. On one pattern the published safe-vs-unsafe difference moves **510×** when the *unsafe* side is written a second way, and it **changes sign** on three others. And most published benchmarks measure the mechanical port, which is a **median 7.3×** dearer than the same code written properly. |
| **Concept earned** | **A safety cost is a difference between two specific programs, not between two languages.** Always ask: which two spellings, and which side did anyone try to make fast? |
| **What they do Monday** | **Ask where the bound comes from.** If the fact that makes the access safe is already in front of the optimiser — a clamp, a `% capacity`, a slice taken once outside the loop, a length the caller already checked — the check leaves the loop and costs a flat per-call constant, often exactly zero. If it isn't, expect a real per-element tax that never amortises. |

Worked pair, both needed:
- **The zero case**: hand the optimiser the invariant the proof states — one dead
  `if sp > CAP { return 0; }` — and the safe-vs-unsafe gap goes to **exactly
  zero**, on rustc *and* on both C compilers. The check was never the cost; the
  compiler not knowing the bound was.
- **The honest worst case**: binary search. `Θ(log n)` probes, nothing to hoist,
  **~6 instructions per probe, 42.5%→46.6% of the kernel, rising**. ⚠ Must carry
  its own caveat: that fraction is of a kernel that does nothing else, and p07's
  search state is `undeclared` — neither side was searched.
- **Hardened C costs the same**: **+5 instructions/call (gcc), +12 (clang)**,
  flat. **Rust's difference is not price. It is that you cannot forget.**

### Movement 2 — "Will my tools catch it?"

| | |
|---|---|
| **Problem** | We run ASan/UBSan/fuzzing in CI and it's clean. Are we fine? |
| **Obvious answer** | Clean run ⇒ no bug. |
| **How it fails, measured** | **C mostly does not crash. It exits 0 with a plausible wrong answer.** Of 58 (pattern, malformed-input) rows where unchecked C misbehaved: **45 silent, 12 crashed, 1 hung.** A one-byte heap overflow printed a normal-looking number and returned success in **7 of 8 builds**. And the detectors have named blind spots: `_FORTIFY_SOURCE` (on by default) rewrites `memcpy` to `__memcpy_chk` and **blinds ASan** to overlap bugs; an out-of-range shift is UB that touches no memory and ASan never sees it; nothing at all catches an infinite loop. |
| **Concept earned** | **A detector that is silent and a detector that did not run are the same observation.** Every "clean" needs a positive control in the same configuration — an input you know it must flag. |
| **What they do Monday** | Add a known-bad input to the sanitizer job and fail the build if it *isn't* reported. Stop treating exit code 0 as evidence. |

⚠ **Honesty this movement must carry, or a reviewer destroys the paper:** the
Rust rungs here are the *fixed* program and the C rung is the *buggy* one, so
the outcome table largely measures a design choice. Where safety is genuinely
attributed, it is by a **deleted-check control**: remove the bound test from the
safe rung and silent corruption becomes a panic. Also state plainly that
**hardened C is correct on these inputs too** — this corpus cannot distinguish
hardened C from Rust on outcomes.

### Movement 3 — "It's memory-safe / it's proved. Am I done?"

| | |
|---|---|
| **Problem** | We moved to Rust. Or: we paid for a proof. Is the bug class gone? |
| **Obvious answer** | Memory-safe means safe. A proof means correct. |
| **How it fails, measured** | **Three programs in this corpus verify with zero errors and are broken anyway.** (a) A port of a real CVE verifies clean and serves an attacker a neighbouring window's bytes — no panic, no crash. (b) A constant-time tag comparison verifies with its obligation count *unchanged* and leaks the secret through timing. (c) A recursive kernel's termination proof goes through and the binary dies of stack overflow. And a one-character change to a shift (`>> 6` → `>> 7`) is caught by **nothing** — not the bounds check, not ASan, not Miri, not the proof — because the wrong index is still legal. |
| **Concept earned — AND THIS IS WHERE THE ABSTRACTION IS FINALLY NECESSARY** | Those proofs were not weak. The leaking one discharges the *identical contract* the honest one does. So "is it safe?" is the wrong question, and the reader now needs four words to ask the right one: **which property, whose obligation, over what resource, and what is left over.** |
| **What they do Monday** | Before trusting any safety mechanism — a type system, a check, a sanitizer, a proof — write down the **resource** its guarantee ranges over. Values? The execution trace? Allocations from *this* allocator? Stack frames? Wall-clock? **Whatever it does not range over is still your problem**, and you can name it before running anything. |

**Introduce property/bearer/quantifier/residual HERE, in one page, as the
minimum vocabulary needed to explain (a), (b) and (c) — and say so in that
sentence.** Not as a framework. As the shortest thing that explains three
programs the reader has just watched break.

The one honest predictive instance, and it must be labelled as the only one: a
handle table's proof quantifies over *allocations released through this
allocator*, so a structure that recycles its own slots inherits nothing — and
use-after-recycle is then writable under `#![forbid(unsafe_code)]`, silently
wrong, and **Miri-clean**.

### Movement 4 — "So which do I fix first?"

**The paper cannot answer this and must say so in one short section, not eight.**
No exploitability model, no bug-frequency weighting, no concurrency at all
(**zero of 26 patterns model a thread or a data race** — state early, it is what
much of the audience means by "Rust is safe"), no compile time, no proof-authoring
hours, and every number is from a build configuration that suppresses inlining.

---

## 4. STRUCTURE AND BUDGET

**Target: 5,000–6,000 words.** ver_A is 17,400. If a section cannot justify its
length against "what does the reader do differently", cut it.

| file | § | words | job |
|---|---|---:|---|
| `00-summary.md` | — | 350 | **The eight things, as a list, on page one.** A reader who stops here has the value. No abstraction, no hedging, numbers with their scope. |
| `10-question.md` | 1 | 500 | The three questions, why one number cannot answer the first, and how the corpus was built — **method in ~150 words, not a section.** |
| `20-cost.md` | 2 | 1300 | Movement 1. Decision rule → zero case → worst case → hardened C → the pair-of-spellings problem. One table of all 26 patterns. |
| `30-tools.md` | 3 | 1000 | Movement 2. Silent-failure headline → detector blind spots → positive controls → the honest caveat about what the matrix measures. |
| `40-notdone.md` | 4 | 1200 | Movement 3. The three broken-but-verified programs, then the vocabulary, then the lookup table of which mechanism reaches which class. |
| `50-cantsay.md` | 5 | 600 | Movement 4. Concurrency first. Short. |
| `60-lied.md` | 6 | 600 | **Three** retractions, each with a rule a reader can use. Not nineteen. Open with what held. |
| `99-close.md` | 7 | 250 | What to do, restated. No flourish. |

**Reuse from ver_A rather than rewriting** (mine these files for verified prose;
they are already fact-checked): `15-whattodo.md` (the six actions — this is the
seed of `00-summary.md`), `40-hostile.md` (silent-failure headline and detector
blind spots), `50-cost.md` (decision rule, dead-clamp example, binary-search
counterexample, the 26-row table), `60-proof.md` (the CVE example), `90-limits.md`
(concurrency caveat — verbatim, it is the most credible passage in ver_A).

**Burn, do not port:** ver_A's §8 framework framing, its §9 principles card, its
§4 method section as a section, and its retraction ledger beyond three entries.

---

## 5. VERIFIED FACTS — every number here was re-derived and fact-checked

Use `\num{}` for anything in this list marked LIVE; the build **fails** on a bad
path and **warns** when a corpus figure is typed as a literal.

| fact | value | LIVE path / source |
|---|---|---|
| patterns · cells · catalogue rows | 26 · 828 · 48 | `totals.patterns` `totals.cells` `totals.catalogue` |
| adversarial rows · clean · deviating | 129 · 71 · 58 | `totals.plain_c.rows` `.clean` `.deviating` |
| silent / crash / hung | **45 / 12 / 1** | `totals.plain_c.silent_first` `.crash_silent_first` `.hung` |
| ⚠ the other honest split | 39 / 18 / 1 | `.loud_first_silent` `.crash_loud_first` — differs only in a tie-break on `.build_split` = 6 rows |
| proof obligations · trusted items · lines | 350 · 108 · 230 | `totals.verus_verified` `totals.tcb_items` `totals.tcb_lines` — **shipped rungs only**; p01's R2v control is `totals.verus_verified_controls` |
| proof text vs code | 4.04× aggregate, 4.24× median, 2.60×–6.29× | `totals.proof_text.*` (as percentages) |
| sanitizer rows declared/fired | 51/51 fire, 143/143 clean | `totals.sanitizer.*` |
| precondition held | on all 194 inputs, 2,512,736 calls | `totals.proof_domain.*` |
| hardened C check | +5 (gcc) / +12 (clang) per call, flat | `results/synthesis.md` §1, p02 |
| naive vs tuned safe Rust | median **7.26×**, range −1.37× to 3536× | `results/SYNTHESIS.md` §2 |
| search asymmetry | p22 `+2` → `+125/+1021` = **510×**; sign flips on p12, p13, p42 | `results/SYNTHESIS.md` §6 |
| binary search tax | ~6 Ir/probe, 42.53%→46.63% | `patterns/p07-binary-search/NOTES.md`. ⚠ search state `undeclared` |
| max per-call working set | **6,144 bytes** (p19) | ⚠ `results/tables/p19-state-machine.md` — p19 writes `work/call=6144` with **no `B` suffix**; a grep for `work/call=(\d+)B` misses it and gives 4,328 |
| C kernels that allocate | **two** (p27, p42) | grep `patterns/*/c/kernel.c` |
| concurrency patterns | **zero** | grep for thread/atomic across `patterns/` |
| LLVM identity | same **version** (22.1.6), separately built — **not** bit-for-bit | `TOOLCHAIN.md` |

**Authority order for anything not listed:** `.memory/` 00–06 (supersedes any
task report it contradicts) → `RECAP.md` → `results/SYNTHESIS.md` →
`results/gate/*.json` → pattern `NOTES.md`/`spec.md`/`verus.rs` headers.

⚠ **Upstream moves during a session.** Re-run `python3 build_data.py` before
believing any count. During ver_A's writing the pattern count went 24→26 and
`totals.verus_verified` moved 357→350.

---

## 6. WRITING RULES

1. **Lead every section with the reader's situation, not the corpus's.** Model:
   *"The interesting question about a memory-safety bug is not whether it is
   dangerous. It is what you would have seen in your logs."*
2. **End every rule on something the reader does to their own code.** Model:
   *"the question to ask of a candidate rewrite is not 'how many bounds checks
   does it have' but 'where does the bound come from, and does the compiler get
   to see it there?'"*
3. **Bold the claim; the next sentence is *why*, not *more*.**
4. **Every number ships with its scope in the same sentence** — one pattern, one
   input, one libc. A scope clause a screenshot separates from its number is not
   a scope clause.
5. **No pattern IDs as nouns in prose.** Write "a binary search", "a bitset
   probe", not "p07 shows". Use `\pat{p07}` only where the reader might go look.
6. **Say "plain, unchecked C", never "idiomatic C".** A copy with the capacity in
   scope and no check is a defect, not an idiom, and calling it idiomatic is the
   cheapest attack on the paper.
7. **Verus's `N verified` counts items, not verification conditions.** Do not
   call it "proof obligations" without saying so.
8. **Round.** Keep full digits only where exactness is the evidence (a slope of
   exactly zero, a residual of exactly 0.0000).
9. **Do not editorialise about C or Rust without a measurement.**

---

## 7. THE FORMAT

Spec: `paper_vers/README.md`. Create `paper_vers/ver_B/` with `meta.json`,
`paper.md` (an `\input` manifest), `sections/*.md`, `refs.json`.

Markers: `\section{}` `\subsection{}` `\label{}` `\ref{}` `\num{path}`
`\figure{id}{caption}` `\src{path}` `\pat{p03}` `\cite{key}` `\todo{}`;
environments `abstract|principle|example|takeaway|caveat|retraction|quote`;
markdown tables; `%%` line comments; `%%literal-ok <n>` to acknowledge a
coincidental literal.

Figure ids: `ladder` `outcomes` `rungcost` `tcb` `identity` `spread`.

**Build fails on**: an unresolvable `\num{}`, a `\ref` with no `\label`, a
`\cite` with no `refs.json` entry, an unknown `\figure` id, an `\input` cycle.
**Build warns on**: a corpus figure written as a literal.

⚠ **Renderer traps, each of which has already cost time:**
- Emphasis does **not** nest in emphasis. Code spans inside emphasis **do** work.
- Keep a block marker on one line where you can (wrapping is supported now, but
  it silently ate two figures before it was).
- A label (`PATTERNS[].title`, `SHORT[]`) is **not** prose — it is rendered raw
  in tooltips and table cells and `check.mjs` fails if it contains markdown.

---

## 8. PROCESS

The role split that produced ver_A worked; see `.memory/paper-writing-process.md`.
For ver_B, with its lessons applied:

1. **One outline agent** turns §3's four movements into a section-by-section
   outline with, for each concept, the problem/obvious-answer/failure triple
   filled in. **Reject any concept whose triple cannot be filled.**
2. **Writers, one per movement**, each owning whole files. ⚠ **Give word budgets
   that already include the mandated additions** — three ver_A revisers
   independently reported their targets unreachable because fixes cost more
   words than cuts licensed.
3. **One practitioner reviewer** whose only question is *"what does the reader do
   differently after this section?"* — if the answer is nothing, the section is
   cut, not shortened.
4. **One fact-checker** that **re-derives from `results/gate/*.json`** rather than
   grepping prose. ⚠ On ver_A my own re-derivation agreed with the paper and was
   wrong, because I pattern-matched a field suffix one pattern does not write.
5. **One trim agent owning every file**, so cross-file moves are possible.

**Tell every agent to verify the brief against the tree, not just execute it.**
On ver_A two agents caught retracted premises I had passed them, and two agents
contradicted each other on the same evidence — the supervisor settles that
against `.memory/`, not by preferring the more confident report.

---

## 9. DONE MEANS

```bash
python3 build_data.py            # 0 errors, 0 todo, no literal-figure warning
node check.mjs                   # OK
node tools/responsive_audit.mjs  # exit 0
git -C .. status --porcelain | grep '\.web'   # empty
```

And the test that actually matters, which no gate can run:

> **Hand `00-summary.md` to a developer who has never heard of this project.
> Can they name three things they would do differently on Monday?**

If not, ver_B has failed in the same way ver_A did.
