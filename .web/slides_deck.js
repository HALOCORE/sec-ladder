// slides_deck.js — the 45-minute talk, as data.
//
// THE ONE RULE, AND `slides.js` ENFORCES IT: every slide carries `q`, the
// question from the floor that it exists to answer, and the engine prints that
// question on the slide.  A slide you cannot attribute to a question is a slide
// about something the speaker found interesting, and it will not build.
//
// The audience is one person: a senior C developer, twenty years of systems
// work, who has never written Rust, whose objections are principled — each is
// what they say after a satisfying answer to the last — and who is tired of the
// pitch.  The running order is the paper's ladder, because the ladder IS the
// argument: Q3 exists because Q2's answer was incomplete, Q4 because Q3
// introduced `unsafe`, and Q5 is only sharp after all of it.
//
// ⚠⚠⚠ RULE ZERO — THE SIZE CAP, AND IT IS THE RULE THIS FILE KEPT BREAKING.
// The owner's verdict on the previous cut, twice, in capitals: "WHAT
// OVERCOMPLICATED MESS WITHOUT MOTIVATION" and "I CANNOT EVEN UNDERSTAND
// SLIDE 2".  The measured state at that moment: 24 of the 35 answering slides
// were over 150 words or carried five or more bullets; the worst were 286, 254,
// 247, 239, 238 and 206 words.  That is a page of prose projected on a wall.
//
//   For EVERY `answer` and `two` slide:
//     · headline — one sentence, and it is the answer itself
//     · AT MOST THREE bullets, each ≤ 30 words
//     · AT MOST ONE aside, ≤ 35 words
//     · ~120 words per slide, head + bullets + aside + note.  It is a CAP,
//       not a target: a slide of one plain sentence is fine.
//   `table`, `code` and `quote` keep their table/code/quote; the prose around
//   them obeys the same cap.
//
// ⚠⚠ HOW THIS FILE GOT FAT, SO YOU DO NOT DO IT AGAIN.  Every previous round
// answered "a reader was confused by X" by EXPLAINING X BETTER, so every pass
// added clauses; and four separate fixes each said "move it earlier" without
// re-reading the destination, which is how one setup slide ended up carrying
// seven topics.  Therefore:
//   1. DO NOT COMPRESS BY MAKING SENTENCES DENSER.  Four tight clauses are
//      worse than one plain sentence.  Cut whole bullets.
//   2. For each bullet ask: DOES THE AUDIENCE NEED THIS TO ACCEPT THE HEADLINE?
//      A second example, a scope on a scope, a qualification of a qualification
//      — cut it.  Apparatus (build counts, machine names, how our checking
//      script works, which set a number was computed over) — cut it outright;
//      it is in the paper.
//   3. A CONCESSION THAT WILL NOT FIT GETS ITS OWN SLIDE.  Slides are free,
//      attention is not.  A claim slide followed by a concession slide beats
//      one slide carrying both.  Five slides in this deck exist for exactly
//      that reason (the stopwatch, the bounded stack's arithmetic, the bitset's
//      spread, the range hiding behind hardened C's average, and the two
//      programs where deleting the check changed nothing).
//   4. AFTER EVERY MOVE, RE-READ THE DESTINATION SLIDE, then run the audit:
//
//      node -e 'const fs=require("fs"),vm=require("vm");
//      const sb={console:{log(){},warn(){},error(){}}};sb.globalThis=sb;vm.createContext(sb);
//      for(const f of ["syntax.js","slides.js","slides_deck.js"])vm.runInContext(fs.readFileSync(f,"utf8"),sb,{filename:f});
//      const d=sb.SLIDES.build(sb.SLIDES_DECK,JSON.parse(fs.readFileSync("data/index.json","utf8")));
//      d.slides.forEach((s,i)=>{ if(s.kind==="ask"||s.kind==="title")return;
//       const b=(s.body||[]).length+(s.left?s.left.body.length+s.right.body.length:0);
//       const w=JSON.stringify([s.head,s.body,s.aside,s.note,s.left,s.right]).split(/\s+/).length;
//       console.log(String(i+1).padStart(3)+" "+s.kind.padEnd(6)+String(b).padStart(3)+" "+String(w).padStart(4)+((b>3||w>150)?"  <<<":""));});'
//
//      NO `answer` OR `two` SLIDE MAY PRINT `<<<`.
//
// ⚠ AND NOTHING IS EVER SILENTLY DROPPED.  Cutting means moving it to another
// slide, or accepting that it lives only in the paper — never losing a
// concession.  The blunt ones are load-bearing and stay blunt: "we have never
// once watched a bounds check fire and save anything"; "that zero is a rule we
// imposed, not a result we went out and found"; "a mistake inside an `unsafe`
// block is the same class of memory corruption you get in C"; "we searched the
// safe side harder than the unsafe side, so every number here leans Rust's way".
//
// ⚠⚠ THE SECOND RULE — WHOSE WORLD IS THE ANSWER ABOUT?
// **The subject of every answer is the listener's code, not our experiment.**
// The first version of this deck answered in the apparatus's own voice — "this
// corpus cannot tell the two apart", "22 of the rows are licensed for
// differencing" — and the owner's verdict was that the questions made sense and
// the answers did not.  Three tests, and a line that fails one gets rewritten:
//   1. WHOSE WORLD IS THE SUBJECT?  Their situation, their code, their
//      decision.  Our method appears only where it CHANGES the answer, and then
//      in one clause, in plain words: "on the big input", "under gcc".
//   2. CAN THEY SIZE EVERY NUMBER, IN THE SAME BREATH?  "+24 instructions per
//      call" is noise until somebody says whether that is a lot.
//   3. COULD THEY REPEAT IT IN A MEETING TOMORROW, with no repository open?
// ⚠ Words that must be glossed or replaced: corpus, rung, spelling, row,
// licensed for differencing, in contract, the shipped set, the gate, cell,
// kernel-exclusive, band, the model, pattern.
//
// ⚠⚠ THE THIRD RULE — THE QUESTIONS ARE FROM A ROOM, NOT FROM A REVIEWER.
//   ⇒ COULD SOMEBODY SAY THIS OUT LOUD, HAVING HEARD ONLY THE SLIDES BEFORE IT?
// If a question needs our methodology to make sense, it is us defending a paper.
// ⚠ NO QUESTION MAY CONTAIN: corpus, rung, spelling, row, version-pair, "your
// numbers", "how hard did you look", or any word that exists only in our method.
// ⚠ AND NO ANSWER MAY DEPEND ON THE LISTENER OWNING OUR SIX VERSIONS.  They
// have their C, a compiler, and something they read.
//
// ⚠⚠ RULE FOUR.  AN AUDIENCE SHOWN TWO NUMBERS WILL SUBTRACT OR DIVIDE THEM.
// Any ratio, multiple or "it vanishes" must be DERIVABLE FROM WHAT IS ON THE
// SCREEN, or the numbers must not be on the screen.  "I sat there doing
// arithmetic that doesn't close while the speaker moved on.  That is the moment
// I stopped following."  Every ratio here closes against figures its own slide
// carries: 16,992 / 263 IS sixty-five; 626 − 828 + 704 IS 502; 4,062 / 2,993 IS
// the 36% your compiler costs you.
// ⚠ AND WHERE A MECHANISM WILL DO, GIVE THE MECHANISM AND NOT THE MAGNITUDE.
// The slide that reader believed instantly was the binary search — "it jumps
// around the array by a rule the optimiser cannot follow".  No arithmetic.
//
// ⚠⚠ RULE FIVE.  NOTHING MAY BE USED AS EVIDENCE BEFORE IT IS DEFINED, and the
// fix is to MOVE THE DEFINITION, not to explain the gap.  But ⚠ FRONT-LOADING
// IS NOT MOTIVATING: a fact belongs where the audience needs it AND has a
// reason to want it.  So `unsafe` is glossed on the array-sum slide, which is
// its first use, and Verus is defined in the proof section, where it earns its
// place.  Neither is in the setup.  Never say "Rust with the checks turned off":
// a cold reader carried that for six slides as a BUILD FLAG.
//
// ⚠ PROSE HERE IS HAND-WRITTEN AND IS A CLAIM.  NUMBERS ARE NOT: they come
// through `D` off data/index.json, from `totals.passing` and from the same
// kernel table the paper quotes, so the talk and the report cannot drift apart.
// `.web/CLAUDE.md` rules 2 and 3.
//
// ⚠⚠ TWO DENOMINATORS, AND THEY ARE NOT THE SAME ONE.  `passing.patterns` is
// the corpus as it stands today and it oscillates 26 ↔ 27 as one program's gate
// goes red and green.  `passing.analysed` is what the project's own synthesis
// analysed, and every breakdown quoted here — the 22 comparable programs, the
// nine/four/nine buckets, the seven-times median — was computed over 26.  The
// talk therefore says twenty-six everywhere and NEVER shows the live count next
// to a frozen analysis figure.  ⚠ A slide used to open "one bookkeeping thing
// first, because the next number would otherwise look like a typo": that is our
// problem, not theirs, and it is gone rather than explained.  For the same
// reason the proof-identity slide now says "almost every program" instead of
// "25 of the 27", which clashed with the twenty-six on every other slide and
// invited exactly the subtraction rule four warns about.
//
// ⚠ MARKUP: `md()` runs on every text-bearing field, `q` and quote sources and
// column headings included — but emphasis does not nest, so `**bold with
// *italic* inside**` ships literal asterisks.  Questions are spoken aloud; keep
// them plain prose with no markup at all.
//
// ⚠ Timing: 50 slides in 45 minutes.  Eight are `ask` slides and cost a beat
// apiece; the rest are now a page shorter each, so most run 45 seconds and the
// five concession slides run 20.  The cues on the `ask` slides are wall-clock
// checkpoints, not slide-number arithmetic: if you have not started the
// hardened-C section by thirty-two minutes you are running long, and the cut is
// Q4's three programs, which reduce to the bounded stack and the binary search
// without losing the argument.  `check.mjs` reports the live count.

(function (g) {
  "use strict";

  g.SLIDES_DECK = (D, S) => [

    // ───────────────────────────────────────────────────────── opening ──
    // Four things somebody needs before they can hear the first objection.
    // Nothing else.  The definitions live at first use, the apparatus is out.
    S.title({
      title: "Should you rewrite this C in Rust?",
      sub: "Your objections, in the order you actually raise them — with measurements attached to every answer",
      foot: D.n("passing.analysed") + " small C programs · six versions of each · every one attacked",
    }),

    // ⚠⚠ THIS WAS THE DENSEST SLIDE IN THE DECK AND IT IS THE ONE THE OWNER
    // SAID THEY COULD NOT UNDERSTAND.  It listed the six versions in a single
    // 54-word bullet.  Six things in a sentence is a wall; six things in a
    // table is three seconds.  ⚠ Do not turn this back into prose — the whole
    // talk is comparisons between these rows, so the audience has to be able to
    // SEE them, not reconstruct them from a list they heard once.
    S.table({
      q: "What did you measure?",
      head: "Twenty-six small C programs, each with one real bug in it, each written six ways.",
      cols: ["the version", "what it is"],
      rows: [
        ["your C", "with the bug still in it"],
        ["hardened C", "the same file, with the missing check written in"],
        ["safe Rust, ported", "translated line for line from the C"],
        ["safe Rust, tuned", "the same program, written the way the language wants"],
        ["unsafe Rust", "you take the checks back off the compiler"],
        ["proved", "that last one, with a machine-checked proof attached"],
      ],
      note: "Every version is run against a reference written independently of all six, so nothing here marks its own homework — then attacked with inputs built to trigger that program's bug. **What I count is instructions executed inside the measured function**: counted, not timed, so there are no error bars in this talk.",
    }),

    S.answer({
      q: "And what can't it tell me?",
      head: "Three things, before you start trusting any of it.",
      tone: "warn",
      body: [
        "**It is narrower than “memory safety” sounds.** Almost all of it is one bug: running off the end of a buffer. Against exactly one use-after-free and one type confusion. If your bug is a use-after-free, I have one program for you and no distribution at all.",
        "**It is not a system.** Every program here is one function. No binary with C and Rust in it, no calls across a language boundary, nobody migrated anything.",
        "**Not one of them starts a thread.** If what you want out of Rust is the data-race guarantee — and for most people proposing a rewrite, it is — this talk is evidence neither way.",
      ],
      aside: "Nothing here asks you to rewrite anything.",
    }),

    // ─────────────────────────────────────────────────── Q1 · slower ──
    S.ask("It'll be slower.", { cue: "≈ 4 min in" }),

    // ⚠ `unsafe` IS GLOSSED HERE, on its first use, and it gets its own bullet
    // rather than a subordinate clause inside the numbers bullet.  It came out
    // of the setup, where it was one of seven topics on a slide nobody could
    // hold.
    S.answer({
      q: "It'll be slower.",
      head: "No. On the simplest program here — a sum over an array — the C and the Rust run the same number of instructions per call.",
      body: [
        "Built with clang, the C runs **" + D.ir("p01", "large", "c-clang") + "** instructions each time it is called. The Rust runs **" + D.ir("p01", "large", "unsafe") + "**. Four digits, two languages.",
        "That Rust is written with `unsafe` — a way of writing the source that opts you out of the automatic bounds checks, on your promise that you did the checking.",
        "On a smaller input they are one instruction apart: " + D.ir("p01", "small", "c-clang") + " against " + D.ir("p01", "small", "unsafe") + ". Most of the rest land within a few dozen per call of each other.",
      ],
      aside: "The friendliest program in the set — and not two compilers agreeing: the C went through clang and the Rust through the same LLVM.",
    }),

    S.answer({
      q: "Does that hold for more than one program?",
      head: "Take the twenty-two programs here where the comparison is fair, and most of the time safe Rust costs you almost nothing.",
      body: [
        "**Nine** land within thirty-two instructions per call of the unsafe version, on both inputs. You could not measure that on your own code.",
        "**On four the safe version is actually cheaper** — on both inputs. We looked into three of them, and none of the margin was safety.",
        "**On a handful it is over a hundred instructions per call.** Those are the rest of this talk.",
      ],
      aside: "Do not add those up — one program is in two of those groups and one is in none. The other four of the " + D.n("passing.analysed") + " are not comparable at all.",
    }),

    // ────────────────────────────────────── Q2 · the benchmark ──
    S.ask("I've seen benchmarks where Rust is slower.", { cue: "≈ 7 min" }),

    S.answer({
      q: "I've seen benchmarks where Rust is slower.",
      head: "You have, and I believe the numbers. Almost every one of them puts somebody's first port up against C that people have been sharpening for a decade.",
      body: [
        "There are two ways to write the same program in safe Rust: **port the C line for line**, or **write it the way the language wants**.",
        "Both check every access. Neither contains the word `unsafe`. Both are honestly called safe Rust.",
        "Wherever safe Rust costs anything at all here, the line-for-line port costs about **seven times** what the hand-written version does. That is the median. **Seven times. Not seven percent.**",
      ],
      aside: "That does not make the benchmark you read wrong. It makes it a measurement of how the Rust was written — so ask who wrote it, and whether anybody tuned it.",
    }),

    // ⚠ A SLIDE WAS CUT HERE and it should stay cut.  It was a pull-quote of
    // OUR OWN summary restating the slide above it.  "An entire slide quoting
    // YOURSELVES restating the last one."  It is a sentence, not a slide, and
    // the sentence is already the aside above.

    // ──────────────────────────────────────── Q3 · the centre ──
    S.ask("Fine, but that's unsafe Rust. Safe Rust is C plus a check on every access.", { cue: "≈ 10 min · the centre of the talk" }),

    // ⚠ THE CLAIM AND ITS CONCESSION ARE TWO SLIDES.  This one used to carry
    // both, at 239 words and five bullets, and the concession — that the
    // stopwatch barely moves — was the fifth bullet nobody reached.  It is the
    // second most important thing on the slide, so it gets its own.
    S.answer({
      q: "Safe Rust is C plus a check on every access.",
      head: "It isn't — and one program settles it. **Two** safe versions of it, both checking every access: on the short message one costs **69%** more than the unsafe version, the other **0.9%**.",
      body: [
        "The program is a record walker: read a header, take a length off the wire, add up that many bytes, repeat. That is the shape of every parser you own.",
        "One is the C ported line for line. The other is the same program written the way Rust wants it. Same contract, same answers on every input.",
        "**Nobody removed a check to get from the first to the second.** 69% down to 0.9%, and not one access went unchecked on the way.",
      ],
      aside: "So the gap between those two is not the price of safety. It is the price of how the code was written — and that is this whole talk in one sentence.",
    }),

    S.answer({
      q: "Instructions aren't time. What does a stopwatch say?",
      head: "On the long message the port runs **72% more instructions** and **0.27% more wall-clock time** — less than the noise between two runs of the same binary.",
      tone: "warn",
      body: [
        "So on this program the count overstates what you would feel. I am telling you because it is my own headline it undercuts.",
        "And the gap does not depend on which input you pick: **72%** and **0.3%** on the long message, **69%** and **0.9%** on the short.",
        "Later today a stopwatch agrees with the count exactly — on the bitset, three times the instructions and three times the time.",
      ],
    }),

    S.table({
      q: "Show me the actual numbers, not the percentages.",
      head: "One record walker. Instructions per call, best optimisation, both C compilers.",
      cols: ["version", "short message", "long message"],
      rows: [
        ["unsafe Rust", D.ir("p16", "small", "unsafe"), D.ir("p16", "large", "unsafe")],
        ["safe Rust — ported line for line", D.ir("p16", "small", "safe_naive"), D.ir("p16", "large", "safe_naive")],
        ["safe Rust — rewritten by hand", D.ir("p16", "small", "safe_tuned"), D.ir("p16", "large", "safe_tuned")],
        ["plain, unchecked C — clang", D.ir("p16", "small", "c-clang"), D.ir("p16", "large", "c-clang")],
        ["plain, unchecked C — gcc", D.ir("p16", "small", "c-gcc"), D.ir("p16", "large", "c-gcc")],
        ["C with the check written in — clang", D.ir("p16", "small", "c-clang-h"), D.ir("p16", "large", "c-clang-h")],
        ["C with the check written in — gcc", D.ir("p16", "small", "c-gcc-h"), D.ir("p16", "large", "c-gcc-h")],
      ],
      hi: [1, 2],
      note: "⚠ **Before my rows, read your own two.** Same C, same flags, and gcc's row is **36% above clang's** — divide them. That is the compiler you happened to pick, not the language. · The proved version gets no row because it is the same machine code as the unsafe one.",
    }),

    S.answer({
      q: "Where does the check actually go, then?",
      head: "Out of the loop. It gets paid once per record, and the bytes ride free.",
      body: [
        "In the hand-written version the check and the unsafe version's unchecked access **both sit outside the loop that adds up the bytes**, so the loop body is instruction-for-instruction identical.",
        "The cost per byte added up is **exactly zero** — not small, zero.",
        "The port leaves its check inside the loop and pays for every single byte. That is the whole distance between 0.9% and 69%.",
      ],
      aside: "That zero holds only because the two versions were matched line for line. Compare two nobody matched and you can invent a safety tax that is really a choice of idiom.",
    }),

    S.table({
      q: "So when it does cost something, is it the checks?",
      head: "Mostly not bounds checks. **Ten** of these gaps have a written-down explanation, and on **seven** of them it is not a check.",
      cols: ["program", "what it is actually paying for"],
      rows: [
        ["an index flattener", "a row-length calculation the compiler hoisted, plus a leftover tail loop"],
        ["a rotate", "**not a bounds check at all** — a chain of Rust's list-walking helpers, each one repeatedly asking whether it has run out"],
        ["a field splitter", "the *unsafe* version losing an unroll"],
        ["a protocol state machine", "one `and $0x7,%edi` — that is a mask, not a check"],
        ["a hash probe", "something the *unsafe* version is missing, not something the safe one added"],
        ["a partition", "the shape of the data"],
        ["a constant-time compare", "the constant-time discipline — the port is cheaper *because it leaks*"],
      ],
      // ⚠ NO COUNT OF "EXPENSIVE PROGRAMS" ON THIS SLIDE OR THE ONE BEFORE IT.
      // It is nine as shipped and ten once a cheaper unsafe version is applied,
      // and a cold reader spent real attention trying to reconcile the two
      // across three slides.  PITFALLS 1.7: if the arithmetic cannot close on
      // screen, the number does not go on screen.  The seven-of-ten split below
      // is self-contained and needs no corpus count to stand.
      note: "Two of these are disputed inside the project and you should know which. On the partition our own notes mark the cause **open**, and the constant-time explanation belongs to a different pair of versions than the one this table subtracts.",
    }),

    S.answer({
      q: "Somebody had to go and tune it. Who pays for that?",
      head: "You do. Per function, forever. That is the objection I cannot close.",
      tone: "warn",
      body: [
        "The hand-written version differs from the ported one by **about ten lines** — the inner loop rewritten to take the bytes in chunks. Not a compiler flag, not a library swap.",
        "**And I cannot tell you what that costs.** Not one measurement in this project has an hours column. Two of our own planning documents promised that metric and nobody collected it.",
        "**The two sides are not equally easy to improve, either.** Tuning the safe version costs somebody an afternoon; tuning the unsafe one has to come back out through a machine-checked proof.",
      ],
      aside: "I will come back to what that asymmetry did to our own numbers, with the receipts.",
    }),

    // ──────────────────────────────── Q4 · where it costs ──
    S.ask("The compiler can't always see what I can.", { cue: "≈ 17 min" }),

    S.answer({
      q: "The compiler can't always see what I can.",
      head: "You are right, and I can show you exactly where — then take most of it back.",
      body: [
        "Of the expensive ones, **three** really are paying for the check.",
        "So we went and searched both sides of all three for a cheaper way of writing it. **One of the three survives that.**",
      ],
      aside: "They are a bounded stack, a bitset and a binary search. I will take them worst-first, so the one that holds up comes last.",
    }),

    // ⚠⚠ THE BOUNDED STACK IS TWO SLIDES AND THE ARITHMETIC IS THE SECOND ONE.
    // It was 286 words and five bullets — the worst slide in the deck — because
    // the claim and the sum that proves it were fighting for the same screen.
    // The sum CLOSES on its own slide: 4 × 118 = 472 off it, 359 − 472 = −113;
    // 828 off, 704 on, 626 − 828 + 704 = 502.  Keep it closing.
    S.answer({
      q: "So where does it actually cost me?",
      head: "**A bounded stack, first.** Here the cost really is the check — and it is charged once for every pop.",
      body: [
        "**" + D.delta("p03", "small", "safe_tuned") + "** instructions per call on the short input and **" + D.delta("p03", "large", "safe_tuned") + "** on the long — about a tenth on top of the unsafe version.",
        "The compiler cannot work out on its own that the stack pointer stays inside the array, so it tests every pop.",
        "**So hand it the fact.** One line at the top of the loop — a test that can never be true — and it deletes the real one.",
      ],
      aside: "Note the direction: that is a line **added**, not a check deleted. And the fact you hand it is the fact the proof writes down as its invariant.",
    }),

    S.answer({
      q: "How much does that one line actually buy?",
      head: "**4 instructions off every pop, and 2 back on to every push a full stack has to throw away.** Nothing else moves.",
      body: [
        "**Short input — 118 pops a call, and it never fills the stack.** 4 × 118 = 472 off, nothing on: " + D.delta("p03", "small", "safe_tuned") + " becomes **−113**, and the safe version ends up cheaper.",
        "**Long input — 207 pops a call, 352 pushes thrown away.** 828 off, 704 on: " + D.delta("p03", "large", "safe_tuned") + " becomes **+502**. Not a vanishing act; a bill moved somewhere cheaper.",
        "Give either C compiler that identical dead test and both delete a hand-written bounds check too. This is a fact about optimisers, not about Rust.",
      ],
      aside: "Both directions are on this slide because both are real.",
    }),

    S.answer({
      q: "And the big one?",
      head: "**The bitset.** Three times the work — and this is the one place a stopwatch agrees with the count exactly.",
      body: [
        "The safe version we ship runs **" + D.ir("p09", "small", "safe_tuned") + "** instructions per call against the unsafe version's **" + D.ir("p09", "small", "unsafe") + "** on the short input, and the same three times on the long.",
        "Three times the instructions, three times the time. No discount at all. This bill is not an artefact of counting.",
        "**And it is not a check we could delete.** We went looking for a cheaper way to write the unsafe side and came back empty — there is no check in it.",
      ],
    }),

    S.answer({
      q: "Three times — is that the check, or is that how you wrote it?",
      head: "Mostly how we wrote it. **We then wrote the safe side four more ways, and the five of them spread sixty-five-fold.**",
      tone: "warn",
      body: [
        "All five check every access, all five meet the same contract, all five give the same answers on every input.",
        "Cheapest **+263** over the unsafe version, dearest **+16,992** — sixty-five times the cheapest. The one we shipped sits at **" + D.delta("p09", "small", "safe_tuned") + "**: second dearest of the five.",
        "**The line-for-line port is one of the five, and it is cheaper than the one we shipped as the tuned version.** So much for tuned.",
      ],
      aside: "One catch on the cheapest: it reads four bytes at a time through a library call our prover has no description of. A permission we granted, not a win it earned.",
    }),

    S.answer({
      q: "Is there one I can't write my way out of?",
      head: "**The binary search.** Yes — and it barely moves however you write either side.",
      body: [
        "" + D.delta("p07", "small", "safe_tuned") + " instructions per call on the small array and " + D.delta("p07", "large", "safe_tuned") + " on the large — and unlike the last two, that number survives everything we tried.",
        "It jumps around the array by a rule the optimiser cannot follow, so there is nothing to hoist the test out of and nothing to fold it into.",
        "**Four** ways of writing the safe version, tried, and both unsafe ones. From the cheapest we found to the one we shipped is **one instruction per probe**.",
      ],
      aside: "And it does not amortise away. It climbs with the size of the array, on every query shape we tried. No input makes it go quiet.",
    }),

    S.quote({
      q: "So how do I tell which one I've got?",
      text: "A check's bill can be dissolved by one added line, or be mostly a choice of how somebody wrote it, or be genuine and hold up against a stopwatch — and you cannot tell which from the number alone.",
      src: "which is why Rust has an escape hatch at all — and why the next objection is the right one",
    }),

    // ⚠ THE BLUNTEST SENTENCE IN THE DECK IS THE FIRST BULLET HERE, AND A COLD
    // READER CALLED IT THE SINGLE MOST IMPORTANT ONE FOR A C DEVELOPER.  Do not
    // soften it and do not move it below the fold: `unsafe` is being defended on
    // this slide, so the concession belongs on this slide.
    S.answer({
      q: "So I write unsafe and I'm back on C's rules.",
      head: "No — stricter rules. But get them wrong and the failure is exactly C's.",
      tone: "warn",
      body: [
        "**A mistake inside an `unsafe` block is the same class of memory corruption you get in C.** What differs is how much of your code can contain one.",
        "The rules are stricter than C's, and they are not in a standard: what unsafe Rust demands about aliasing arrived as a research paper, and is still being written down.",
        "Every unsafe version here was run under Miri — an interpreter that runs your Rust looking for undefined behaviour. **" + D.n("passing.miri_runs") + " runs, nothing reported.**",
      ],
      aside: "Two of those runs never finished, and **Miri only ever runs the unsafe version** — no safe version in this project has ever been under it.",
    }),

    // ──────────────────────────── Q5 · to-be-verified ──
    S.ask("Then you've given up the safety. That's just C with extra steps.", { cue: "≈ 23 min" }),

    S.answer({
      q: "That's just C with extra steps.",
      head: "It would be, if `unsafe` were the last step. It isn't.",
      body: [
        "**Verus reads your code and a separate written-down statement of what it must do, works out every fact needed for the two to agree, and demands a proof of each.**",
        "Across these programs it got a proof of every single one. The proved build and the unproved build are the same machine code, so **the proof executes zero instructions**.",
        "**Take the bounds test out of the proved record walker and it does not crash — it does not build:** `invariant not satisfied before loop`.",
      ],
      aside: "So the `unsafe` block is not unchecked. It is to-be-verified — and in C that same check is a line somebody has to not forget.",
    }),

    S.answer({
      q: "Zero? Nothing is free.",
      head: "You are right to push on it. That zero is a rule we imposed, not a result we went out and found.",
      tone: "warn",
      body: [
        "On almost every program here our own checking script **requires** the proved build and the unproved build to come out as the same bytes. So proved-minus-unproved is zero by construction.",
        "**Why the rule is there:** without it we would be pricing what a proof does to the compiler, and code the proof moved could hide the very difference we are measuring.",
        "**What it costs us:** one program has an unsafe version **17,526 instructions cheaper per call** — a third of its whole cost. We refused it: its proved twin does not verify.",
      ],
      aside: "So our unsafe baseline is slower than it needed to be, and every safe-against-unsafe figure in this talk reads more kindly to Rust than the program deserves.",
    }),

    S.answer({
      q: "What does the proof actually prove?",
      head: "That it cannot corrupt memory. **Not** that the answer is right.",
      body: [
        "And you already know why that distinction is the whole game: **a wrong specification inside a proved program is silent memory corruption with a certificate attached** — worse than C, because in C nobody trusted it.",
        "So: how would you ever catch a wrong specification?",
      ],
      aside: "The next two slides are the sharpest thing in this work, and they cost one character.",
    }),

    S.code({
      q: "Show me a bug that gets past everything.",
      head: "A bitset packs one bit per member, sixty-four to a word — so bit `q` lives in word `q >> 6`, which is `q` divided by sixty-four.",
      lang: "rust",
      src: "        if q < nbits {\n            let w: u64 = load_u64(win, ws + (8 * (q >> 6)) as usize);",
      note: "Now type a **7** where the 6 is. Dividing by 128 instead of 64 gives you a *smaller* word number — and a smaller number cannot run off the end where the right one did not. **The index is still inside the array.** It is the wrong word, not an illegal one. The program answers the query and exits 0.",
    }),

    S.table({
      q: "Surely one of your tools catches that?",
      head: "We put that one character into every version's own copy and pointed everything we own at it.",
      cols: ["what we pointed at it", "what it did"],
      rows: [
        ["the bounds check safe Rust compiles in", "never fires. exit 0, wrong answer"],
        ["a sanitizer, on the flags we use everywhere", "silent on every input. exit 0"],
        ["Miri", "exit 0, reported nothing, wrong answer"],
        ["the proof, with only the memory rules written down", "**verifies the buggy version**"],
        ["the proof, with the right answer written down too", "**refuses to build**: `invariant not satisfied`"],
      ],
      hi: [3, 4],
      note: "⚠ Both proof rows carry one extra hint line the shipped program never needed, so what they are worth is **the difference between the two rows**, not either row on its own. And every runtime tool above watches the same thing — the edge of an allocation — so four of them agreeing is not four confirmations.",
    }),

    S.answer({
      q: "So just move the specification to match?",
      head: "Then the prover verifies the bug, and reports nothing wrong.",
      body: [
        "That edit is not one character either. It is the specification's own arithmetic, plus two more assertions over four lines of proof.",
        "So the honest version of this is not *one more character*. **It is the author's misunderstanding reaching the specification** — which is exactly the way it would reach yours.",
      ],
      aside: "**A proof is a proof of what you wrote down.**",
    }),

    S.answer({
      q: "Is that just a toy typo?",
      head: "No. The same shape shipped as a real vulnerability, and that program is in here.",
      body: [
        "An HTTP range parser, ported from a real CVE — a suffix-range parser missing one test.",
        "Guard the index against the buffer it was handed — all a bounds check buys you — and **every proof about memory safety goes through.**",
        "What comes out is **memory-safe and functionally wrong**: no crash, no sanitizer report, and the only proof that fails is the one that says what the answer has to be.",
      ],
      aside: "On one buffer it hands back the caller's own bytes. Give it a second buffer belonging to somebody else and it hands back **theirs** — provably memory-safe.",
    }),

    S.answer({
      q: "What does the proof cost to write, and to keep?",
      head: "Real, and not in instructions — and the number that would actually decide it for you does not exist.",
      tone: "warn",
      body: [
        "Proof text runs to **" + D.n("passing.proof_text_ratio_pct") + "%** of the code it proves: four lines of proof for every line of program. Strip the comments and it gets worse, not better.",
        "Underneath it sits a base the prover takes on trust and never checks: **" + D.n("passing.tcb_items") + " hand-written facts over " + D.n("passing.tcb_lines") + " lines**. That is where the proof stops and somebody's word starts.",
        "And that base is easy to get wrong: the prover prints a specification for you to paste, with no preconditions. Paste one for a raw-pointer read and a megabyte read off the end verifies.",
      ],
      aside: "**What I cannot give you:** no hours column anywhere, and nobody changed one line in a verified program to count how much proof broke. Every price here is a floor.",
    }),

    // ────────────────────────── Q6 · hardened C ──
    S.ask("Then why not just harden the C I already have?", { cue: "≈ 32 min · the strongest objection" }),

    S.answer({
      q: "Why not just harden the C I already have?",
      head: "**Honestly? For these bugs, hardening your C works — and I am not going to pretend otherwise.**",
      tone: "warn",
      body: [
        "Write the missing check into the C and it gives the right answer on **every** attack we threw at it. Every one.",
        "It costs about **24 instructions per call** — the middle one here. On any function that does real work you will not find that in a profile.",
        "And we have never once watched a Rust bounds check fire and save anything. Not in **" + D.n("passing.adversarial_runs") + "** hostile runs. **The safety net I am selling you has never been photographed catching anybody.**",
      ],
      aside: "So it is not a performance argument and it is not an outcomes argument. The difference is that in C the check is optional, and nothing tells you when it is missing.",
    }),

    S.answer({
      q: "So the C I already have is fine.",
      head: "Not the one you have. The hardened one, yes.",
      body: [
        "Of those same hostile runs, **" + D.n("passing.crash") + " end in a signal and " + D.n("passing.hung") + " hang** — every one of them on the plain, unchecked C, on inputs where the right answer was to exit 0.",
        "So this does separate plain C from everything else, loudly. What it **cannot** separate is checked C from Rust.",
        "**Take the simplest program that ships both — a buffer copy.** Safe Rust costs **11** instructions per call; the same check written into the C costs **5 under gcc and 12 under clang**.",
      ],
      aside: "On that one program, safety costs about what it costs in Rust — and your choice of C compiler moved it further than your choice of language did.",
    }),

    // ⚠ THE AVERAGE'S OWN CONCESSION, ON ITS OWN SLIDE.  It used to be a 55-word
    // aside under the buffer copy, where it read as small print under a claim it
    // actually contradicts.  It is fifteen seconds and it protects the 24.
    S.answer({
      q: "So hardening is cheap, then.",
      head: "Not as a law. **24 is a middle, and it hides a range from −125 to +10,242 instructions per call.**",
      tone: "warn",
      body: [
        "Negative on three programs: the hardened C runs **fewer** instructions than the unchecked one.",
        "And the dearest of them is not a check at all — it is a whole extra validation pass over a 2,048-entry table.",
        "**So “hardened C is cheap” is true of most of these and false as a rule.** On your code it is a thing to measure, not a thing to assume.",
      ],
    }),

    S.two({
      q: "Is there anything on your list I can't just write in C?",
      head: "Two things — and `unsafe` does not take either of them back.",
      left: { h: "An overlapping memcpy — no price", body: [
        "Safe Rust **cannot express it.** It will not let you hold two live references to the same memory when one can write, and it decides that at compile time.",
        "So there is nothing to put a price on — and hardening your C does not buy it either.",
      ] },
      right: { h: "A strict-aliasing miscompile — costs 6", body: [
        "The compiler may assume two pointers of different types never address the same memory, and optimises on it. Writing it that way costs **6 instructions per call more** than not.",
      ] },
      note: "⚠ And one that costs *us*: the safe versions cannot express a single wide read — they take the value in two halves, at **12 instructions more under gcc, 32 under clang**.",
    }),

    // ⚠⚠ THE DELETION EXPERIMENT IS TWO SLIDES.  It was 238 words: the claim,
    // two ways it fails, and a two-part admission about the experiment itself.
    // The admission is the part a hostile reader wants and it was the aside
    // nobody read out loud.  Claim first, then the failures with the admission.
    S.answer({
      q: "So the whole argument is that Rust makes you write it. Does it?",
      head: "On four of the eight programs we tried it on, yes. Not on the other four.",
      tone: "warn",
      body: [
        "We went in and **deleted the bounds check on purpose**, in a branch, to find out what was actually holding each program up.",
        "On **four**, a silently wrong answer becomes a stop. That is the claim, and that is its size.",
        "On **two** it depends on the input: while the input stays in bounds, the stripped version prints C's answer bit for bit and exits 0.",
      ],
      aside: "You could not do that by accident — the compiler writes that check and you cannot forget it. This is an experiment, not something that happens to you on a Friday.",
    }),

    S.answer({
      q: "And the two where nothing happened?",
      head: "On **two**, deleting the check changed nothing at all — and they fail differently.",
      body: [
        "One compiles to the same bytes as the C at both optimisation levels, so there was no check in the machine code to delete.",
        "The other **hangs**, with the sanitizer and the interpreter both silent. The proof does catch that one.",
        "**And the two halves of this experiment do not weigh the same.** The C side is the shipped program. The Rust side is deletions re-run from a script, certified by nothing.",
      ],
      aside: "⚠ And one you are entitled to hold against us: our own checking script reads every version's source, writes down that the C is missing its check, and passes it anyway.",
    }),

    S.answer({
      q: "I already run a sanitizer and a fuzzer. Why isn't that enough?",
      head: "They work — the crashes I showed you on the plain, unchecked C are them working. They also all need an input that reaches the bug.",
      body: [
        "Point a sanitizer at the plain C record walker and it fires on the first input that gets there. A fuzzer's job is to find that input.",
        "**Now the bitset typo from two sections ago.** Sanitizer silent on every input, Miri silent, no bounds check — nothing ever leaves the allocation.",
        "**There is no input you could write that would make any of them fire.** A tool that watches for a boundary being crossed is blind to a bug that never goes near one.",
      ],
      aside: "And half your toolbox we never touched: nothing here runs a static analyser at all. On Coverity and CodeQL this work is evidence in neither direction.",
    }),

    S.answer({
      q: "So instead of a wrong answer I get an outage.",
      head: "Sometimes, yes. That is a trade rather than a win — and it is the one thing here we did not measure.",
      tone: "warn",
      body: [
        "A bounds check turns a memory-safety bug into a **reliable abort** — a remote denial of service in a network daemon, a device that does not come back in firmware.",
        "**And we have no data either way.** Not one check fired anywhere in any of those runs, so we have never watched one of these programs stop itself.",
        "**Plenty of people should take that trade. Nobody should take it without noticing they made one.**",
      ],
      aside: "The top of the ladder does answer one part: whatever the specification covers cannot fail at run time. If the prover cannot show it, you get no binary. The failure moved to build time.",
    }),

    // ─────────────────────────── Q7 · trust ──
    S.ask("Why should I believe any of your numbers?", { cue: "≈ 39 min" }),

    S.answer({
      q: "Why should I believe any of your numbers?",
      head: "Not entirely — and here is the specific reason rather than a general disclaimer.",
      body: [
        "**Twice, a check of ours turned out to be one that could not fail.** A script read the wrong field, and we quoted the unchanged table as evidence nothing had moved.",
        "**The second one matters more, because the document it happened to was correct.** A summary of twenty-six programs reproduced every figure it gave — and **nine reviewed results were simply missing.**",
        "And they were missing in a direction. Of the five whose direction we graded, **every one was a result that made safe Rust look good.**",
      ],
      aside: "Nineteen retractions had trained this project to distrust *safety is cheap*, and the reflex went on to delete the evidence for it.",
    }),

    S.answer({
      q: "What else would you rather I didn't ask?",
      head: "This one. **We searched the safe side harder than the unsafe side — so every number in this talk leans Rust's way.**",
      tone: "warn",
      body: [
        "Every figure I have given you is **our** safe version against **our** unsafe version. Both are somebody's choice, and the two choices did not get the same effort.",
        "On four of the twenty-two programs we could compare, there is a cheaper unsafe version. It passes everything we ask of it, and **we simply did not ship it.**",
        "Put all four back in and three programs move into a worse group. **All four move against safe Rust. None of them move the other way.**",
      ],
      aside: "Making the safe version faster costs an afternoon; making the unsafe one faster has to come back out through a proof. The side that goes unsearched will always be the same side.",
    }),

    S.quote({
      q: "How would I even detect that in my own work?",
      text: "A residual of exactly zero is not a strong pass. It is the signature of a test that could not fail.",
      src: "and coverage bias has no arithmetic signature at all — the only check is a different question, asked by someone who did not write the document: which way do its gaps point?",
    }),

    // ─────────────────────── Q8 · signing up ──
    S.ask("So what am I actually signing up for?", { cue: "≈ 42 min" }),

    S.two({
      q: "So what am I actually signing up for?",
      head: "Two bills, and they are different in kind.",
      left: { h: "Expires — this year's tools", body: [
        "The prover refuses C strings four different ways. Teaching it costs four hand-written facts, after which it verifies first try. **The limits you hit will not be these ones.**",
      ] },
      right: { h: "Does not expire — the shape of it", body: [
        "A proof rests on a base of hand-written facts the prover takes on trust and never checks.",
        "Somebody has to write the specification. It is a separate artefact from the code, and it can be wrong. **No amount of tool maturity touches either.**",
      ] },
      note: "⚠ Two things here are not expensive, they are simply **absent**: nothing starts a thread, and no binary has both languages in it. So this prices a rewritten loop, not a rewritten daemon.",
    }),

    S.answer({
      q: "Then what can I actually use on Monday?",
      head: "Three things, and none of them requires believing a word I have said.",
      body: [
        "**Run your known-bad input against the build you actually ship**, not the debug build — and fail when nothing happens. A silent pass is a result.",
        "**Delete a check in a branch and run your tests**, so you find out today whether anything is watching.",
        "**When somebody quotes you a number, ask what they compared it against** — and which of the two anybody had bothered to make fast.",
      ],
      aside: "If you take a figure out of here rather than a habit: take a per-call constant, never a percentage. These programs do nothing but the loop, so every fraction here can only shrink.",
    }),

    S.end({
      head: "Three sentences, if you take nothing else",
      body: [
        "**Safe Rust is not C plus a check on every access.** Same program, same guarantee, and it cost +69% or +0.9% depending only on who wrote it.",
        "**A proof costs zero executed instructions and proves exactly what you wrote down** — which is why the sharpest bug here is one that every runtime tool missed and only a specification caught.",
        "**On outcomes I cannot tell hardened C from Rust.** What differs is that in one of them the check is not optional — and even that holds on four of the eight programs we tried it on.",
      ],
    }),
  ];
})(typeof globalThis !== "undefined" ? globalThis : this);
