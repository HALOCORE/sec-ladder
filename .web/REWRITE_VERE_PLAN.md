# REWRITE_VERE_PLAN — build `paper_vers/ver_E`

**Written to be executed cold, after the conversation that produced it is gone.**
Resume with: *"resume from REWRITE_VERE_PLAN.md and write ver_E."*

Read order on resume: **this file → `paper_vers/CLAIMS.md` (binding, all
versions) → `paper_vers/ver_D/sections/` (the prose voice to keep) →
`paper_vers/ver_B/sections/10-question.md` (the opening move that works).**

---

## 0. THE BRIEF, IN ONE PARAGRAPH

**ver_E is a dialogue with a principled sceptic.** The reader is a C expert who
has not written Rust, who has real objections, and whose objections arrive in a
predictable order because they are *principled* — each one follows from the
answer to the last. The paper is that ladder. Every section is an objection in
the reader's voice, answered with evidence; every subsection is a sub-objection
to that answer. Nothing appears because we measured it. Everything appears
because the reader just asked for it.

---

## 1. WHAT I GOT WRONG IN ver_A THROUGH ver_D — AND IT IS ONE ERROR, FOUR TIMES

The owner has rejected four framings. This section exists so the fifth does not
repeat them. **Read it before writing a word.**

### 1.1 The root error: organised by FINDING, not by OBJECTION

Every version so far was structured around *what we measured*: a taxonomy
(ver_A), three questions we chose (ver_B), an attribution thesis (ver_C), four
stories (ver_D). Sections were named after results.

**A finding carries no motivation. An objection carries its own.** When a
section opens "here is what we measured about attribution", the reader has to be
*told* why they should care, which is exactly the abstract throat-clearing the
owner has rejected four times. When a section opens with the sentence the reader
was about to say out loud, the motivation is already in the room.

> ✅ **THE FIX, AND IT IS THE WHOLE PLAN: each section is an objection. The
> answer is the evidence. The next section is what the reader says after hearing
> it.**

### 1.2 The second error: I optimised proxies and never stated the science

Across four framings I tuned readability scores, word ceilings, cold-read
ratings and fact-check compliance — and **never once wrote down what the
research actually says**. The owner had to ask for it directly. A paper whose
author cannot state its message in five sentences will not acquire one through
revision. **Write §4 of this plan's evidence tree into prose; do not go looking
for a thesis in the data again.**

### 1.3 The third error: ver_D led with the weakest finding

ver_D's headline was *non-optionality* — "you can't leave the check out and not
find out". It is true, it is the best artefact in the corpus, and it is the
**weakest of the six findings**: bounded by "4 of 8 patterns", and a C expert
already suspects it. Meanwhile the strongest and most surprising result — **safe
Rust is not C plus dynamic checks, and the naive port's +69% versus the tuned
version's +0.9% proves it on one program** — was a supporting detail in section
2. **ver_E promotes it to the load-bearing node (Q3).**

### 1.4 What to KEEP from ver_D — it is not all wrong

ver_D scored **8/10** with a cold undergraduate reader against ver_C's 5, and
these are why:

- **Second person, contractions, 2–4 sentence paragraphs, no jargon unglossed.**
  Keep the register exactly.
- **Gloss as a trailing appositive inside a sentence doing other work**, never a
  glossary block.
- **One concrete subject at a time**, and it must be a thing that *did*
  something.
- **Demonstrate each finding exactly once.** All four cold readers of ver_C quit
  on repetition, not difficulty; one counted eight demonstrations of a single
  finding and said *"I would have closed the tab."*
- **The admissions.** Asked which sentences bought the most trust, a reader
  named six and **not one was a provenance claim** — they were all admissions of
  ignorance (*"and we cannot explain it"*, *"nobody knows"*).
- **The retraction material** scored 7–9 in every version. It has a home in
  ver_E as **Q7**, not as a confession appended to the end.

---

## 2. THE LADDER — this is the paper

Eight nodes. Each is an objection in the reader's voice. **Section titles are
the objection, or the answer to it, in the reader's words — never a topic.**

```
Q0  Should I rewrite this C in Rust?
     └─ the setup: why this corpus can answer that when benchmarks can't

Q1  "It'll be slower."
     └─ parity: unsafe ≈ C, proved ≡ unsafe, tuned safe ≈ unsafe
     └─ Q1.1 "But I measured a big number."  → you measured the wrong pair

Q2  "Fine, but that's unsafe Rust. Safe Rust is C plus dynamic checks."
     ⚠ THE PAPER'S CENTRE. Longest node.
     └─ same language, same contract, same guarantee: +69% vs +0.9%
     └─ Q2.1 why?  the check leaves the hot path; per-byte difference is zero
     └─ Q2.2 then what were those big numbers?  7 of 10 aren't the check

Q3  "The compiler can't always see it."
     └─ correct, and here is exactly where: binary search, bitset
     └─ hence `unsafe`, scoped to a region you can point at

Q4  "Then you've given up the safety. It's as bad as C."
     └─ no: `unsafe` isn't unchecked, it's TO-BE-VERIFIED
     └─ Q4.1 is the zero real?      → it is ENFORCED, not discovered
     └─ Q4.2 what does it prove?    → memory safety, not correctness
     └─ Q4.3 what does it cost?     → not instructions: text, TCB, hours

Q5  "Why not just harden my C instead?"
     └─ on outcomes we CANNOT tell them apart — say so plainly
     └─ the difference is that the check is not optional

Q6  "Why should I believe your numbers?"
     └─ two of our own checks could not have failed, and here they are

Q7  "What breaks this in two years, and what doesn't?"
     └─ which limits are toolchain maturity, which are structural
     └─ what to do on Monday
```

⚠ **The order is the argument and it is not rearrangeable.** Q3 exists because
Q2's answer was incomplete. Q4 exists because Q3's answer introduced `unsafe`.
Q5 is only devastating *after* Q4, because the reader has now seen the whole
Rust story and the honest tie on outcomes lands as a concession rather than a
retreat. **If a node can be moved, it is not motivated.**

---

## 3. THE BFS RULE, AND HOW TO ACTUALLY GET IT

The owner's requirement: *"Any BFS of the paper's top-down argument chain is
fully self-consistent and self-complete. No unjustified badly-organized detail
that falls off the top-down structure."*

That is not a style note. It is a **construction method**:

> ✅ **WRITE LEVEL 1 FIRST, COMPLETE, AND READ IT AS A FINISHED PAPER.** Eight
> objections, eight answers, ~1,200 words total. If that document does not stand
> on its own and make the argument, **the structure is wrong and no amount of
> level-2 detail will fix it.**
>
> ✅ **THEN ADD LEVEL 2** — the sub-objections. Re-read. It must still be
> coherent, and every new paragraph must be traceable to the sentence above it
> that provoked it.
>
> ✅ **THEN LEVEL 3** — the evidence, the caveats, the provenance.
>
> **Commit each level separately** so a reviewer can read the tree at any depth.

**The test for any paragraph: which sentence above it made the reader ask for
this?** If you cannot point at one, the paragraph is a finding that wandered in
from the data, and it goes — however good the number is. That test is the whole
mechanism; apply it to every paragraph before it ships.

**Budget:** ~5,000–6,000 prose words. Do not set a global ceiling and shave;
**allocate per node** and let Q2 and Q4 be large because they carry the
argument. Q1, Q3, Q5 are short. If a node needs more than its evidence supports,
that is a signal the objection is weak, not that the budget is.

---

## 4. THE EVIDENCE, MAPPED TO ITS NODE

**Every number below was verified against the tree in the session that produced
this plan.** ⚠ `paper_vers/CLAIMS.md` is binding and lists 23 things a draft
actually claimed and had to withdraw. ⚠ Re-run `python3 build_data.py` before
believing any count; the corpus moves.

### Q0 — the setup

`\num{totals.patterns}` patterns, small C kernels each with one named defect,
built at six rungs over two C compilers, two optimisation levels, two inlining
modes: `\num{totals.cells}` measured builds, each driven against **the model** (a
Python reference sharing no code with any kernel), then attacked
`\num{totals.adversarial_runs}` times.

**Why this design answers what benchmarks can't:** the closest prior work
\cite{userstudy25} has 33 participants producing 31 safe-Rust translations of 8 C
programs — real translations, but each pair differs in many ways at once. **Here
the contract is pinned and independently checked at every rung**, so safety is a
graded dial with the computation held fixed.

### Q1 — parity

- Plain clang C **beats** unsafe Rust by 17 (small) and 37 (large) `Ir`/call on
  the record walker. Noise, in C's favour.
- Proved − unsafe = **0**, byte-identical machine code, on
  `\num{totals.identity_exact}` of `\num{totals.patterns}` patterns.
- Tuned safe − unsafe = **+27 (+0.897%)** and **+77 (+0.324%)**.
- **Q1.1 — the four answers.** On one program, per call, large input:
  **−2,545, 0, +77, +17,123**, depending only on which two versions you subtract.
- ⚠ **Context that must ship with Q1:** gcc against clang **on identical C
  source** is **1,069** and **8,933** `Ir`/call — **40× and 116× the entire
  tuned-safe cost**. Part is `-fcf-protection=full`, a control-flow-integrity
  mitigation. *Your compiler flags cost more than the argument you're having.*
  ⚠ `results/synthesis.md:58` forbids attributing a gcc-vs-clang gap to codegen
  without naming that flag.

### Q2 — THE CENTRE: safe Rust is not C + checks

- **The proof of it, on one program:** line-for-line port **+69% / +72%**; tuned
  safe **+0.9% / +0.3%**. Same language, same pinned contract, same guarantee.
- **Q2.1 — the mechanism.** Both versions take their slice **outside** the fold
  loop — safe one checked, unsafe not — so the check is **per record, not per
  access**. The per-byte difference is **exactly zero**, over six ways of writing
  the fold. ⚠ Write "exactly zero", not `0.00000`; a reader said the decimals
  *"made me trust the number less."*
- A **safe** version can beat the unsafe one: **−2,545** on the large input,
  from rewriting the tuned version's inner loop to take sixty-four bytes at a
  time. ⚠ It is **about ten lines**, not "one string changed" — three readers
  across three versions failed on that phrasing. ⚠ Name the input: on the
  smaller blob a narrower fold is cheaper. "Cheapest found", never "minimum".
- A bounded stack: add a **clamp** — one provably-dead line at the top of the
  loop — and the optimiser deletes the real check. Per-pop cost goes to
  **exactly zero**, over 13 popping rates and six operation counts.
  ⚠⚠ **THREE CORRECTIONS ver_C GOT WRONG AND ver_D INHERITED:** the clamp is a
  line **ADDED**, not a check deleted (`p03/NOTES.md:366-371`, and `:405` —
  *"the dead test is gone"*); it is **not free**, costing 2 instructions per
  *dropped* push, which leaves it **+502** against unsafe on the large input;
  and the surviving **+5** **is** explained — it is the *window-reslice check*
  (`:1259-1260`), a different check. ⚠⚠ `p03/NOTES.md:1263-1266` says in bold
  **"Do not publish that as p03's safety tax."**
- **Q2.2 — what the big numbers actually were.** Of the ten programs whose gap
  is large enough to explain, `results/SYNTHESIS.md:284-295` names something
  other than a bounds check on **seven**: a hoisted trip count and scalar
  epilogue, iterator adaptor exhaustion tests, a foreclosed unroll, one
  `and $0x7,%edi` mask, a missing reslice, the data's shape, constant-time
  discipline. **Three are the check: a bounded stack, a binary search, a bitset.**
  ⚠ **Seven, not six** — an earlier fact pack said six and forbade seven.
  ⚠ Attribute it (*"this project's own summary names…"*): ver_C reclassified two
  of those rows off the patterns' notes, which is a live disagreement.

### Q3 — where the compiler genuinely can't see it

- A **binary search**: the check runs **42.5%** of the kernel at 7 elements to
  **46.6%** at 16,385, rising with array size over six query distributions, with
  **no axis along which it amortises**.
- A **bitset**: **+13,756 / +48,885**, which is **+205.6%** of the unsafe kernel
  on the small input — *"the one row where that is established rather than
  assumed"*. Write the safe rung the cheapest way found and it drops to +263;
  the unsafe side has no answering spelling.
- The rule: **when the fact that justifies the check is not available to the
  optimiser, you pay per operation.** That is what `unsafe` is for.

### Q4 — to-be-verified Rust

- `\num{totals.verus_verified}` obligations verify across the **shipped**
  versions at `\num{totals.verus_errors|plain}` errors. ⚠ CLAIMS §1.16: the
  words "shipped versions" are load-bearing (with controls it is 357/110/235).
- Byte-identical to the unproved version on 25 of 26 → **zero executed
  instructions**. The one exception: a ghost function occupying a vtable slot,
  40 bytes against 32 — still zero executed.
- **Enforcement, shown:** delete the bounds test from the proved version and it
  does not panic, it **will not build** (`invariant not satisfied before loop`).
  ⚠ Quote **no verifier counts anywhere in the paper**; "it will not build" plus
  the error text carries more and a reader cannot interpret `9 verified, 1
  errors`. CLAIMS §3.7: those count *items*, not conditions.

**Q4.1 — is the zero real? It is enforced, not discovered.** The gate *requires*
the proved and unproved versions to compile at `-O3` to one digest. So
proved−unsafe = 0 is a **tautology** (CLAIMS §2.3). ⚠ **State it as a design
decision and say what it buys before what it costs:** without the rule we'd be
pricing the proof's effect on the compiler rather than the cost of the code, and
a proof that moved the code could hide the difference being measured. **And it
costs us:** it rules out an unsafe NUL-scan spelling **17,526 `Ir`/call
cheaper** on the large input (~35% of that function's work), because that
candidate's proved twin does not verify — Verus has no `CStr` support at all. So
**our unsafe baseline is slower than it needed to be, and every safe-versus-unsafe
figure in the paper reads more kindly to safe Rust than the program warrants.**
⚠ Two qualifications, each its own short sentence: a *saving refused, not a cost
added*; and large input only — on the small one the pinned version is cheaper by
3,448. ⚠ Never phrase this as *"ours is held too high"* — three of four readers
took that as a **boast**. Lead with *"slower than it needed to be."*

**Q4.2 — what does it prove? Memory safety, not correctness.**
- The CVE port is `9 verified, 1 error` with the functional specification
  present, **and the failing obligation is the functional one, never an access
  obligation** (CLAIMS §1.7). Write *every memory-safety obligation discharges*.
- **The bitset, and this is the sharpest thing in the corpus.** Bits packed 64 to
  a word, so bit `q` lives in word `q >> 6`. Type `q >> 7`. Dividing by 128 can
  never overshoot where dividing by 64 didn't, so **the index is still inside the
  array — the wrong word, not an illegal one.** Rust's bounds check never fires.
  ASan+UBSan silent on every input. Miri exits 0 and **reports nothing** (⚠ CLAIMS
  §1.11: never *"certifies it clean"*). Wrong answer on four of the five shipped
  inputs; on the fifth every version returns 0, that input never reaching the
  query loop.
  **The proof catches it — and only because someone wrote down what the answer
  must BE, not just where the code may read.** Strip the functional
  postcondition and the prover certifies the bug. **Move the specification to
  match the typo and it verifies the bug**, and that edit is not one character
  either: the spec's arithmetic, plus the bridging lemma, plus two proof lines.
  ⚠⚠ **Both proof rows carry one added hint line the shipped program never
  needed**; the pure one-character mutant fails for a proof-engineering reason.
  Say so — attaching the caveat to only one row flatters the prover, and a
  previous version dropped exactly the half that damned it.
  → **A proof is a proof of what you wrote down.**
- ⚠ Structural point worth one sentence: every runtime instrument here watches
  **the same boundary** — the edges of an allocation. Four agreeing is **not**
  four independent confirmations.

**Q4.3 — what does it cost? Not instructions.**
- Proof text is `\num{totals.proof_text.ratio_pct}`% of the unsafe source lines
  (median `\num{totals.proof_text.median_pct}`%), **and counts mostly comments**.
- Trusted base: `\num{totals.tcb_items}` hand-written items over
  `\num{totals.tcb_lines}` lines the prover takes on trust and never checks,
  sitting on a standard library whose own trusted surface is larger and is not
  counted.
- **No compile-time and no authoring-hours data exists anywhere, so every price
  here is a floor.** The other way: on two kernels the proof went through first
  try, leaving the budgeted engineer session unused.
- ⚠ CLAIMS §2.3: a proof-enabling change cost **8.5%** of one kernel and shipped
  described as free.

### Q5 — "why not just harden my C?"

- **Those three lines cost +17 / +41 under gcc and +24 / +54 under clang** on the
  record walker, same compiler both sides. `c/kernel_hardened.c`'s own header
  licenses exactly this subtraction: *"what the check costs within one language,
  with the signature, the calling convention, the header test, the fold and the
  return all held fixed."* ⚠ Do not place it beside +27/+77 and imply a ratio.
- Across the 25 patterns shipping a hardened rung the delta is **median 24**,
  range **−125…+10,242 (gcc)**, **−108…+5,637 (clang)**, negative on three. The
  biggest numbers are not checks — the largest is a whole extra validation pass
  over a 2,048-entry table. ⚠ p01 ships **no** hardened rung; it is 25 of 26.
- **The concession, and it must be stated plainly:** `\num{totals.loud|plain}` of
  `\num{totals.adversarial_runs}` hostile runs end with any version refusing to
  continue. Exit code 101 appears **zero** times. **Not one bounds check fires
  anywhere in the shipped matrix**, and hardened C matched the model everywhere.
  **On outcomes this corpus cannot distinguish hardened C from Rust** (CLAIMS
  §2.4). Say it, do not bury it.
- **So the difference is not outcomes, it is who has to remember.** The plain C
  here *ships* with a comment standing where the check would go — nobody deleted
  it. And our own gate **reads** every rung's source, matches the pinned spelling
  `vlen > end - (p + 3)`, records `absent: c/kernel.c` — **and passes anyway.**
  ⚠⚠ ver_C and ver_D both said *"no stage of our gate reads source"*. **That is
  FALSE** (`harness/check.py:1216`; `results/gate/p16-tlv-walk.json`
  `required_absent: 1`; corpus-wide `totals.idiom.required_absent = 126`). Only a
  `forbidden` hit fails a run. **The true version is the better sentence.**
- **And the enforcement is partial — this may not be smoothed.** Eight patterns
  carry the deleted-check control. On four, deletion turns silent corruption into
  a stop. On two it depends on the input. **On two it does nothing**: one
  stripped safe rung is bit-identical to C at both optimisation levels, and
  another **hangs** — the sanitizer and the interpreter silent, though the proof
  does catch that one. ⚠ CLAIMS §1.15 bans *"nothing catches an infinite loop"*.

### Q6 — why believe the numbers

Keep close to ver_C's `70-caughtitself.md`, which scored 7–9 every read.
- **The control that could not have failed.** A field was added to 22 gate
  records, tables regenerated, output came back byte-identical — quoted as
  evidence nothing had moved. It was byte-identical because the generator read a
  different key. ⚠ Past tense, and say when: it reads the field today.
  → *A residual of exactly zero is not a strong pass. It is the signature of a
  test that could not fail.*
- **The faithful summary that was still biased.** Compressing twenty-six programs
  into four results, its own review found five reviewed, quotable results missing
  — **every one flattering safe Rust**. Every figure in it reproduced correctly.
  → *Coverage bias has no arithmetic signature. The only check is a different
  question, asked by someone who did not write it: which way do its gaps point?*
- **And an earlier version of this report failed that check**, asserting no tool
  was caught missing a bug it was looking for — true only after six of twelve
  rows had been dropped. Quote the withdrawn sentence and the circle: *drop every
  row where a detector looked and did not see, and no row is left where one did.*
  ⚠ 67% → 50% as a pair; do not compute a "drop" across different denominators.

### Q7 — what expires, what doesn't, what to do Monday

- **Expires (toolchain maturity):** Verus cannot express `CStr` at all (four `is
  not supported` errors), cannot dereference raw pointers, and a `chunks_exact`
  fold costs five trusted items. These are the reason Q4.1's baseline is
  inflated. ⚠ Do not generalise into a claim about provers.
- **Does not expire (structural):** the trusted base; the authoring cost, which
  is unmeasured here; that a proof only proves what you specified.
- ⚠⚠ **NOT MEASURED AT ALL, and a rewrite's most-cited motive: concurrency.**
  Zero of `\num{totals.patterns}` patterns creates a thread. **On data races this
  report is evidence neither way.** Non-negotiable, and it goes near the reader,
  not in a footnote.
- **Scale:** these kernels do nothing but the loop, so **per-call constants
  transfer to your code and percentages do not** — a percentage measured here can
  only shrink on a function that does other work.
- **Monday:** run your known-bad input against the configuration you actually
  ship and fail the build on silence; delete a check in a branch and run your
  tests; publish the pair (which two versions, and which of the two anyone tried
  to make fast). ⚠ **No "budget the proof honestly"** — all four cold readers
  skipped the proof-buying material.

---

## 5. THE THREE PLACES THE EVIDENCE FIGHTS THE STORY

A hostile reader with the tree open will go here first. **Each must be stated by
us, first, in our own voice.**

1. **Q4's zero is ours.** It is enforced by our rule, it is a tautology, and the
   rule costs us 17,526 instructions of unsafe baseline. Present it as a design
   decision with its price attached, never as a measurement.
2. **Q4 will be read as "verified means correct."** It does not. Memory-safety
   obligations discharge; the functional one is where the work and the risk are.
   The bitset is the proof of this and belongs to Q4.2, not to a side note.
3. **Q5's outcome tie is real.** Hardened C matched the model everywhere and no
   Rust check ever fired. The paper's argument is non-optionality, **not**
   outcomes, and the enforcement it rests on is partial (4 of 8).

---

## 6. BANNED — carried forward, all of it evidence-backed

- ❌ **Any section named after a topic or a result.** Sections are objections.
- ❌ **Any paragraph you cannot trace to the sentence that provoked it.**
- ❌ Numbered findings (F1…), cross-references used as a substitute for
  structure, `principle`/`example`/`takeaway`/`caveat`/`retraction` environments.
- ❌ Verifier counts, anywhere.
- ❌ Percentages as cost figures where a per-call constant exists.
- ❌ Enumerated distributions ("three… five… one… one"). A corpus claim survives
  as one count of one thing.
- ❌ "Here are N qualifications" as a form — weld each to the sentence it
  modifies.
- ❌ The twelve-row coverage matrix; the ten-row attribution table.
- ❌ The provenance formula more than twice in the whole paper. A reader stopped
  reading it after the third appearance.
- ❌ Pattern ids as nouns. "A bitset", "a record walker".
- ❌ Any sentence whose subject is the paper.

**Words that must be glossed at first use, in a sentence doing other work:**
`kernel` (a reader took it to mean *operating system*), `unsafe`, the two safe
versions, `hardened`, `specification` (**the load-bearing gloss — Q4.2 rests on
it**), `sanitizer`, `prover`, `gate`, `slice`, `panic`, `control`, `invariant`,
`undefined behaviour`.

---

## 7. FORMAT

`paper_vers/ver_E/` with `meta.json` (`"current": true`, and flip ver_D's to
`false`), `paper.md`, `sections/*.md`, `refs.json`. Spec: `paper_vers/README.md`.

⚠ Renderer traps, each of which has cost a session:
- Every block marker (`\section`, `\label`, `\figure`, `\begin`, `\end`) on
  **one line**; a wrapped one vanishes silently with its `\label`.
- **Emphasis does not nest**; `check.mjs` fails on a surviving `**`.
- `\num{path}` for every live corpus count — the build **fails** on a bad path.
  Everything else is a literal, but these integers collide with a corpus total
  and warn: `108 109 126 129 143 164 194 230 255 260 329 350 404 424 629 817 828
  1026 1486 2478 3612 3658 4104 14604`. Use `%%literal-ok <n>  <reason>`.
- ⚠ A number describing a **past event** must be frozen as prose ("twenty-six"),
  not `\num{}` — otherwise it goes false when the corpus grows.
- Quotations: markdown `> ` blockquote, source in the surrounding sentence.
- `\cite` needs an entry in `refs.json`; copy only what you cite from ver_C's.

**The loop:** `python3 build_data.py` (0 errors) → `node check.mjs` (OK) →
`node tools/responsive_audit.mjs` (exit 0). ⚠ **Never write outside `.web/`**;
`git -C .. status` must be unchanged.

---

## 8. PROCESS

1. **Write level 1 alone** — eight objections, eight answers, ~1,200 words — and
   read it end to end. **If it isn't already a good paper, stop and fix the
   ladder.** Do not proceed to level 2 to rescue it.
2. **Level 2**, then **level 3**. Commit each.
3. **One fact-check**, pointed at the draft **and at this plan's §4** — the last
   fact-check found three errors that came *from* the fact pack, including one
   that stated a tally as six and forbade the correct seven. **A fact pack is not
   a source.**
4. **One cold read by a C developer persona who has not written Rust** — not an
   undergraduate this time; the audience changed. Ask: which objection did you
   still have at the end, and where did an answer arrive before you'd asked the
   question?
5. **Stop at 8.**

⚠ **If a cold read scores under 7, change the ladder, not the sentences.** That
was ver_C's four-pass mistake and it cost a whole framing.
