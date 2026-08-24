# TASK_079 — p31, the unbuilt sixth axis: §0 tests the DEMOTION before anything is built

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.tasks/TASK_074.md` in full** — it is the closest analogue to this task
and it ended in a **refusal that was accepted** — then `.memory/06-catalogue.md`'s
**`p31` row** (Family F) and the section *"The waves order by FAMILY…"* including
its **feasibility triage** and the **p48 refusal block**, then
`.memory/04-verus.md`, `.memory/03-measurement.md` (**the two `Ir` conventions,
the INLINE-MODE rule, the DOMAIN rule, the RESIDUE-CLASS rule, the
OUTWARD-DISPATCHED-WORK rule, and the `rep stosb` mis-pricing left behind by
p48**) and `.memory/01-ladder.md` **findings 7 (p08), 19 (p27) and 23 (p36)**.
Templates: `patterns/p27-handle-table/` (**the donor — it is the only pattern in
the tree that ships `vstd::raw_ptr` code**) and `patterns/p36-vtable-dispatch/`
(newest, and the one whose conventions this file forwards).

⚠⚠ **RULE 3 IS FLAGGED AGAINST THE DECISION YOU ARE BEING ASKED TO MAKE.**
`p31` is **demoted** by the catalogue in the manager's own words — *"the expected
shipped-compiler behaviour is **nothing observable**, which makes it **p08's
shape** — a tooling-and-expressiveness result the tree already has one of"* —
and **nobody has tested that sentence.** It is the same test that refused `p48`,
and at TASK_074 the manager explicitly declined to schedule `p31` on an
unmeasured recommendation for exactly this reason. **So §0's first deliverable is
not a measurement. It is an argument, and BOTH outcomes are successful tasks:**

- **"the demotion is right — do not build p31"**, with the measurements that
  show it; or
- **"the demotion is wrong — here is what p31 has that the tree does not"**,
  and then you build it.

**The manager is not to be deferred to on this.** The demotion is the manager's
lineage's own judgement and it has never been attacked.

⚠ **State novelty claims as questions to be measured.** *"The first termination
proof in the project"* was the manager's sentence in `TASK_070.md`; it was
**false**, the engineer had no reason to doubt it, and it shipped into **eight
places, two inside `contract_sha256`**. Everything below is written as a
question. **Treat any sentence in this file that is not a question as a bug in
this file.**

## What p31 would be

Catalogue row: **bump / arena allocator**, bug classes *"alignment, exhaustion,
provenance"*, difficulty `hard`. A bump allocator carves one large buffer into
smaller objects by advancing a cursor: `p = cur; cur += align_up(n); return p`.

⚠ **That row names THREE bug classes and the axis table names only the third.**
The axis table's entry is **provenance** — *"the property Miri checks and nothing
else does; untested here"*. **Which of the three p31 would actually ship is
undecided, and §0 decides it**, the way p38's §0 had to pick its shape and
p10's had to settle its bug class. **Four catalogue bug-class guesses have been
overturned and one row was refused outright; this row has had none of that
scrutiny.**

## §0 — the argument first, then the measurements

### §0a — SHOULD p31 BE BUILT? Five objections, none of them answered.

**1. ⚠ THE p48 MIRROR, AND IT IS ALREADY HALF-CONFIRMED — MANAGER-VERIFIED.**
`p48` died in part because its sole distinguishing Verus claim (*"no pattern in
the tree exercises `is_init`"*) was **false** — p27 exercises it in four places.
**The same check has now been run against p31's vocabulary and it comes back the
same way.** `patterns/p27-handle-table/verus.rs` already carries
**`PointsToRaw`**, **`provenance()`**, **`Dealloc`** and
**`DeallocData.provenance`**, and its core invariant conjoins
`dal[j].provenance() == tab[j]@.provenance`. **So *"p31 brings the provenance
vocabulary"* is FALSE as stated**, exactly as p48's claim was. ✅ Manager-checked
directly, both files.

> ✅ **WHAT SURVIVES THE CHECK, AND IT IS THE ONE THING THAT MIGHT CARRY THE
> PATTERN.** `PointsToRaw::split` and `::join` are **axioms in the pinned vstd**
> (`~/tools/verus/vstd/raw_ptr.rs`) and are used **nowhere in this tree**:
> `grep -rn '\.split(\|\.join(' patterns/*/verus.rs` returns **nothing**.
> p27 allocates and frees **whole objects**; a bump allocator must **carve one
> permission into many and hand the pieces out**, which is what `split` is for.
>
> ⚠ **QUESTION, NOT A CLAIM: is that a new KIND of obligation or a new CLAUSE?**
> That is p48's objection 2 verbatim, and p48 failed it. **Read
> `~/tools/verus/vstd/raw_ptr.rs`'s `split`/`join` and p27's `verus.rs`, and
> say.** A defensible "new kind" answer needs to name what a proof must do that
> no existing pattern's proof does — **not** merely that a different function is
> called.

**2. THE DEMOTION ITSELF. Is *"nothing observable"* true?** The catalogue asserts
the shipped compilers do nothing with a provenance violation, which would make
p31 **p08's shape**: safe Rust cannot express it, the compilers do not exploit
it, and the deliverable is a tooling claim. ⚠ **The tree already has one p08 and
that was the third finding that killed p48.** But it is an *assertion about two
compilers*, and this project's record on those is poor — **p38's row predicted a
null result for strict aliasing and 12 of 12 cells flipped.** §0b measures it.

**3. ⚠ ALL THREE BUG CLASSES MAY BE DUPLICATES, AND THEY ARE DUPLICATES OF THREE
DIFFERENT PATTERNS.** The manager's prior, offered to be refuted:

| p31 sub-case | the manager's guess at its shape | already in the tree as |
|---|---|---|
| **exhaustion** | the cursor outruns the arena, or `cur + n` **overflows** and passes its own check | the tree's **thirteenth** `index >= len`? p36 was the twelfth **and said so** |
| **alignment** | a misaligned load — on **x86-64 a plain scalar load does not fault**, so the UB is masked by hardware and the program limps on | **p18's shape** (*"UB that is not memory-unsafety"*, four catchers, all outside the matrix) |
| **provenance** | Miri-only, compilers indifferent | **p08's shape** — which is objection 2 |

⚠ **If all three are duplicates, p31 is a TRIPLE duplicate — and that still does
not settle it.** **p36 was built with a duplicate bug class and was worth it**,
because its *mechanism*, *catcher* and *prover* stories were each new (finding
23). **Find p31's version of that, on all three, or say there isn't one.**

**4. WHAT IS THE COST AXIS, AND IS IT ACTUALLY A GOOD ONE?** Every pattern here
has one. The manager's candidate, **offered as a question**: *what does a bump
allocator buy over `malloc`, and what does making it safe cost?*

> ⚠ **The hook that makes this more than a guess: p27 measured the allocator's
> contribution to its own safety tax as `0.00`** — its closed decomposition is
> `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`. **p31 would make
> the allocator itself the kernel**, i.e. it measures the term p27 found empty.
> **No pattern in the tree has allocation in the kernel.**
>
> ⚠ **And the safe rung here is not obvious, which is the interesting part.** The
> real safe-Rust arena idiom is **not** a raw bump pointer — it is `Vec<T>` plus
> **`u32` indices** (the "arena pattern"), which trades pointer provenance for an
> index and a bounds check. **Is the R3-vs-R4 comparison then "a pointer against
> an index", and is that a *safety* cost or another spelling?** Finding 14 says
> assume spelling until measured. **Count the levers on each side.**

**5. ⚠ CAN THE HARM BE PRICED AT ALL, AND WHO IS THE HARM'S VICTIM?** p48 died
partly on *"`Ir` cannot measure this harm"*. p31's exhaustion harm is a **write
into the arena's own later region** — in bounds of the *arena's* allocation,
live, owned. **That is p17's shape** (ASan clean, exit 0, plausible answer) and
p09's. **Is there any input on which p31's harm is visible to the gate's stage-7
sanitizers at all?** If not, say so early — p12's review showed the adversarial
row can be *designed* to make a write bug visible, and p48's V1 sentinel design
is committed and reusable (`.memory/06-catalogue.md`, *"What SURVIVES"*).

**Write the decision in `NOTES.md` §0a with the argument. If it is "do not
build", stop there and report — that is a successful task**, and the named
alternatives are at the bottom of this file.

### §0b — IS *"NOTHING OBSERVABLE"* TRUE? This is the demotion's own claim.

**Probe it, do not reason about it.** The question is whether gcc 13.3.0 and
clang 22.1.6 **exploit** a provenance violation the way they exploit strict
aliasing (p38: 12 of 12 cells flipped) or ignore it the way they ignore p38's
*benign* char-buffer direction (8 of 8 cells gave the defined answer).

- The canonical C shape is **pointer comparison / round-trip**: two objects that
  happen to be adjacent, a pointer derived from one used to reach the other,
  `intptr_t` round-trips, `p == q` with `p` and `q` of different provenance.
- ⚠ **`-fno-strict-aliasing` is p38's flag; provenance has a different one, or
  none.** Find out which. If the behaviour cannot be flipped by a flag, **the
  control that shows it is real is missing** and that is itself the finding.
- ⚠ **p38's lesson applies directly and it is the trap here: the catalogue's own
  spelling was the BENIGN direction.** Do not probe the shape this file names —
  probe the shape a compiler would actually exploit, and say which you probed.

### §0c — WHAT CATCHES IT, AND CAN IT BE A RUNG?

- **Miri** is already **gate stage 8** and runs on **`unsafe.rs`, a Rust rung, on
  a nightly toolchain** (`check.py::check_miri`). ⚠ **QUESTION: does that mean
  the C rung's provenance bug has NO catcher in this project at all?** If the
  answer is yes, that asymmetry is worth stating plainly — and it is also the
  strongest form of objection 2, because *"Miri catches it"* would then be a
  claim about the rung that **reintroduces** the bug, not the one that **has** it.
- ⚠ **Stage 7 builds `gcc -O1 -fsanitize=address,undefined`, and gcc's
  `undefined` set is NOT clang's.** **QUESTION to settle with a compile probe,
  not from memory: does gcc have `-fsanitize=pointer-overflow`?** If it does not
  and clang does, then p31's exhaustion sub-case has a catcher **the gate cannot
  reach**, which is `p36`'s `cfi-icall` situation and `p48`'s MSan situation —
  **a control, not a rung**. Two patterns in a row have landed there; a third
  would be a pattern about the gate, not about C.
- Also probe **valgrind** (present at `~/tools/valgrind/bin/valgrind`) and
  **Miri's `-Zmiri-tree-borrows`** against `-Zmiri-stacked-borrows`; they
  disagree about exactly this class, and *which* Miri model catches it is a
  sharper statement than *"Miri catches it"*.
- ⚠ **`build.py` is a full re-measure (RECAP settled answer 4). Do not reach for
  a new build flag.** If a catcher needs one, it is a **control**. Report it.

### §0d — WHERE DOES THE WORK LIVE?

⚠ **p36 was broken by the absence of this rule.** `kernel_exclusive_ir` counts
the kernel symbol and **not what it calls**, and the rule is **not** *"check the
`@plt` calls match"* — it is **any outward-dispatched work**, including
project-local callees. **A bump allocator's whole point is that it does NOT call
`malloc`, while the rung it is compared against DOES** — so the two sides
dispatch wildly different work outward **by construction**. **List the
outward-dispatched work per cell and check the lists are equal before quoting the
kernel column for any cross-rung difference.** If they are unequal, the
comparison needs the whole-program marginal convention and must say so.

⚠ **And p48 left a live trap in this exact area**: `Ir` **mis-prices** a
zero-fill across glibc's `__x86_rep_stosb_threshold` (2048 bytes), because
callgrind counts a `rep` instruction **once per repetition** — so `Ir` reports
the cost **rising 6.5× at exactly the size the real cost falls**. **An arena
pattern will cross that threshold.** Name it or avoid it.

⚠ **gcc defaults to `-fcf-protection=full`**, so every gcc cell carries `endbr64`
landing pads the other compilers do not (`1.00000·nrw + 1` `Ir` per call on
p36). **Name it before attributing any gcc-vs-clang gap to codegen.**

## What p31 must have, if §0 says build it

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**
  (definition-of-done 6), and ⚠ **say that the `git show HEAD:` diff is
  UNAVAILABLE on a new pattern and why** — it compares working tree to HEAD, not
  first-written to shipped, so on a clean tree it always looks like it passed.
  **The recorded first hash is the only evidence.** p22's disclosure still has no
  artefact behind it because it ran that command and got silence.
- **If `spec.md` is generated, fix the GENERATOR and re-run it** — three tasks in
  a row shipped an edit the generator would have silently reverted, and one of
  them was the task fixing that defect. ⚠ **p22's `spec.md` is generated too, and
  the TASK_078 review found that out the hard way.** Read the shared
  named-spelling paragraph from a donor `spec.md`; never embed a copy.
- ⚠ **`WHY_HEAD` NAMES the finding, never a bare number** — *"every rung is a
  spelling"*, not *"finding 14"*, which is a **live collision** (ladder 14 is
  p13). **Follow p36, not p22/p27/p38.**
- ⚠ **SEARCH BOTH SIDES AND COUNT THE LEVERS ON EACH.** *A difference is only as
  honest as its WEAKER-searched endpoint.* **p36 searched R4 first and correctly
  — and then published against an R3 side with ONE lever, which moved R3 the
  wrong way; `+15.00` was `+7`.** Publish the **fixed-R4 bound**, the **span**,
  the words **"cheapest found"**, the **input named**, and **the lever count per
  side**. **No pair interval** unless you built an admissible R4 that moves.
- **NAME THE INLINE MODE at every figure.** Cross-pattern `Ir` is
  `isolated`-only.
- ⚠ **A fitted law owes its DOMAIN, and check the RESIDUE CLASS of any parameter
  your bands hold constant** — p38's additivity failure was 100% attributable to
  three missing columns, two of its bands sitting at `nw ≡ 0 (mod 8)`.
  **An arena pattern has an alignment parameter; residue classes are not a
  hypothetical here.**
- **No `ns` claim without a layout population**; port `controls/clayout.py` and
  ⚠ **point `OUT` and its scratch default at `.temp/p31pat/`** — see the
  constraints block, this is not the default you would guess.
- **Adversarial rows per rung**, **TCB as one number plus the U-license / V-gap /
  infra classification**, and **two proof mutants that FAIL** — ⚠ **run the
  battery with `--multiple-errors`**; p22 skipped it and the review found a
  mutant failing on a different obligation than claimed.
- ⚠ **`forbidden_hits` HARD-FAILS**, and **backtick every entry you want
  enforced** — an unbackticked entry is audited **zero** times. Recompute the
  denominator rather than quoting one:
  ```
  python3 -c "import glob,json;print(sum(json.load(open(f))['idiom_audit']['forbidden_spellings'] for f in glob.glob('results/gate/p*.json')))"
  ```

## Done when

§0a's decision is written with its argument — **and if it is "do not build",
that plus §0b–d's measurements IS the deliverable.** Otherwise: the checklist
above; complete `harness/check.py p31` (**say up front which verdict you expect
and why**); checksums against an independent `model.py`; two failing proof
mutants with `--multiple-errors` output; `measure.py --check-stale` clean.
**Paste actual output.** ⚠ Doc edits make a gate record STALE — re-run after.

⚠ **Expect `PASS`.** A blocked Miri row is **no longer** a by-design outcome:
`check_miri` now reads stage 4's **measured** per-rung `hung` column, so a
declared hang blocks nothing by itself. **If a row blocks, that is a finding, not
a shrug.**

## Constraints

⚠⚠ **SCRATCH IS `.temp/p31pat/`, NOT `.temp/p31/`. THE MANAGER CHECKED THIS
BEFORE WRITING THE FILE AND IT IS A LIVE COLLISION.** `.temp/p31/` **already
exists and is TASK_031's evidence** — the layout finding, i.e. `.memory/`
finding 16, one of the most-cited results in the project (`analyze_p02.log`,
`order.py`, `derive.py`, `NOTES.md` dated 2026-08-19). **Writing p31's scratch
there would destroy it.** This is the **second** time the `.temp/pNN/`
PATTERN-vs-TASK collision has been caught; the first was `.temp/p48/`, caught by
the engineer **after** the manager prescribed it. **`ls` any scratch path before
you name it** — `.memory/00-environment.md` constraint 1.

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`,
`.memory/`, `harness/`, `common/`, or any existing pattern. **If p31 seems to
need a `harness/` change, STOP and report it** — PROTOCOL rule 5's default
applies again unweakened: the `harness/` batch closed at TASK_078 and the queue
of *measured* gate defects is **empty**, so a new gate check now needs the
*"could this happen by accident?"* test first. Verus only via `./verus_run.py`;
`~/tools/verus/vstd/` for vstd source — **never** `../LearnVeri/_VERUS_DOC_/vstd/`,
an older snapshot that caused one false *"no spec exists"* that stood for 44
tasks **and which has no `copy_from_slice` and no `copy_within` at all**. clang
`~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — **none but gcc on
PATH**. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**;
⚠ **no self-matching `pgrep` wait-loops** — one was orphaned and fired a spurious
completion. Measurements in the **FOREGROUND**. **You are the only agent
running.**

Notes to `.temp/p31pat/NOTES.md` as you go, so a transient API death loses
nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 203** — and the entry that matters most for *this* task is that
**TASK_074's engineer refused the pattern the manager proposed, and the refusal
was accepted without a review task.** The count is the evidence that this
instruction is not a courtesy.

**What I am least sure of, by name: objection 1's survivor —
`PointsToRaw::split`/`join`.** It is the only thing in p31's stated vocabulary
that this tree does not already use, so **the entire prover half of the pattern
rests on it**, and I do not know whether carving one permission into many is a
new **kind** of proof obligation or just an unused function with the same
`requires` shape p27 already discharges. **That is p48's objection 2 verbatim and
p48 failed it.** Read the vstd axioms and p27's `verus.rs` and tell me which one
this is **before** agreeing that p31 has a prover story.

**Second-least sure: objection 3's exhaustion row.** I have called it *"the
thirteenth `index >= len`"* from the armchair. It may not be — the bound is the
arena's **own cursor, which the program computes**, where every previous bounds
pattern read its bound from an input or a constant. **If that is a real
distinction, say so; if it is a distinction without a mechanism, say that.**

**If you refuse p31, the named alternatives, in the manager's order:**
**(a) a DIFFERENT catalogue row you argue for** — this is the one the manager
most wants to hear, RECAP has invited it since TASK_066, and `p48`'s refusal is
the only taker so far. Unbuilt rows the manager would find plausible, offered
without endorsement: **p35** (tagged union / tag-payload mismatch, `moderate`),
**p39** (bitfield pack/unpack into wire format), **p41** (flexible array member,
size-computation overflow), **p43** (CRC over an untrusted length, `easy`),
**p45** (saturating/wrapping helpers, signed-overflow UB, `easy–moderate`).
⚠ **Several of these are named in the catalogue's own "more of the same" list —
p43 is called p16's shape. Argue past that, do not ignore it.**
**(b) RECAP "Owed" 4** — p17 ships **no sweep inputs**, which is how its
*"+32 Ir/call flat"* was published from two bands that both had `nsuf = 3`; a
`sweep-*` band appended last costs **one gate re-run, not a re-measure**.
**(c) RECAP "Owed" 3** — p01 and p08 owe an in-contract R3-side span.
⚠ **Do not propose gate hardening.** Rule 5's default is back and the measured-
defect queue is empty.

---

## Outcome (recorded by the manager at the task boundary)

*(to be written)*
