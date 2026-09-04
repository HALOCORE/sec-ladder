# .web — the sec-ladder report

A static, read-only web report over this repository's measurements: the ladder
explained, the cost side, the security side, the proof burden, every pattern's
own numbers and sources, the cross-cutting findings, and the method with its
caveats.

**Nothing in this directory writes outside it.** `build_data.py` routes every
write through one `_out()` helper that refuses any path outside `.web/`;
`index.stdio.py` reads repository files and never writes one. Running anything
here leaves the parent repository's `git status` unchanged — which matters,
because that tree is under active research by other agents. `.web/` is ignored
by the parent and keeps its own git history.

**Three docs, three audiences:** this file is how to run and read it,
[`CLAUDE.md`](./CLAUDE.md) is the rules for an agent editing it, and
[`RECAP.md`](./RECAP.md) is the state, the design decisions, the traps and what
is owed.

## What is in it

| tab | what it answers |
|---|---|
| Overview | the thesis, the hero figure, the KPI row, the ladder, three headline results |
| The ladder | what each of the six rungs buys, costs and leaves trusted · one profile per pattern |
| Cost of safety | safe-vs-unsafe per call, the spelling gap, what the same check costs inside C, the full table |
| Hostile input | the outcome matrix, per-run detail, ASan/UBSan and Miri, and where "memory-safe" is the wrong question |
| Proof & trusted base | obligations, trusted items and lines, verified twins, the vacuity probes, byte-identity |
| Patterns | per pattern: narrative, contract, profile, inputs, adversarial behaviour, wall clock, each rung's source, gate record, and its own README / spec / NOTES |
| Findings | the cross-cutting results, marked `standing` or `corrected`, plus the full retraction list |
| Method | what a cell is, the two `Ir` columns, wall clock, what the gate checks, and what this benchmark cannot tell you |

## Look at it

The repo is already wired into the local ccneo server's `apps_routes`, so:

```
http://127.0.0.1:8000/pw11apt/apps/pub-to38u0zfu2/
```

Any static file server works too — the page needs no backend:

```bash
python3 -m http.server 8099            # from inside .web/, then open http://localhost:8099/
```

(An agent working here should not need this: the ccneo route above already
serves the folder, and static snapshots are what to screenshot. See `CLAUDE.md`.)

Views are hash-routed, so a link can point at one: `#cost`, `#findings`,
`#patterns/p17-http-range`, `#proof/p03-bounded-stack`.

### Choosing what to compare

The legend under every profile chart is also the control: click a key to drop
that rung from **all** of them (the ladder wall, each pattern's profile, and the
cost table's columns), and the charts rescale to what is left. The selection is
one piece of state shared by those views and remembered across reloads, so a
comparison holds while you move around. Presets:

| preset | rungs | what it isolates |
|---|---|---|
| All rungs | everything | the full ladder |
| **Same backend** | C clang · C clang hardened · R3 safe tuned · R5 proven unsafe | the only C-vs-Rust comparison with no backend difference in it — clang is bit-for-bit the LLVM rustc ships |
| Rust only | R2 · R3 · R4 · R5 (+R2v) | the spelling gap beside the safety gap |
| C only | gcc · gcc hardened · clang · clang hardened | what the check costs inside one language |
| Checked vs unchecked | C clang · C clang hardened · R4 · R3 | the two unchecked rungs against the two that carry the check |

Colour is bound to the rung, never to the row, so hiding one never repaints the
others; the hidden state is carried by a struck-through label and a hollow key
as well as by fading, and the table view under each chart follows the same
selection.

## Rebuild the data after new measurements land

```bash
python3 build_data.py                 # ~1 s, reads ../results/ and ../patterns/
```

or press **check / rebuild** in the page footer, which reports whether `data/`
is older than the evidence before it does anything.

It writes only these, all derived and all safe to delete:

| path | what |
|---|---|
| `data/index.json` | site-wide summary, one row per pattern |
| `data/index.boot.js` | the same object as a `<script>`, so the page opens with data already in scope |
| `data/patterns/<id>.json` | cells, marginal Ir, Verus record, adversarial matrix, sanitizer, Miri, identity |
| `data/code/<id>.json` | each rung's kernel source (driver boilerplate sliced off) |
| `data/docs/<id>.json` | that pattern's `README.md`, `spec.md`, `NOTES.md`, verbatim |

New patterns are picked up automatically: anything with both `results/<id>.json`
and `results/gate/<id>.json` appears. A pattern with no hand-written write-up in
`content.js` still gets every chart, table and source view — its page just says
so and points at its own files. The catalogue size in the header is counted from
`.memory/06-catalogue.md` rather than hard-coded.

**When the evidence format moves, the build says so.** `build_data.py` knows the
set of gate-record keys and the set of ladder rungs; anything new lands in a
`warnings` list that is printed at the end of the build *and* rendered as a
callout at the top of the Method tab. That is not hypothetical — the gate's
adversarial record changed from one entry per (input, rung) to a **list of
behaviour groups**, each naming the builds that produced it, and grew `hung` /
`diverges` / `expected_hang` / `run_timeout_s`. Those are now first-class here:
a fourth outcome ("never returned"), and a corner notch on any matrix cell whose
builds disagree.

## The files

| file | what it is |
|---|---|
| `index.html` | page shell |
| `index.js` | all views (JSONML + Incremental DOM, per `LESSONS.md`) |
| `index.css` | this report's styling; light + dark, both selected rather than flipped |
| `content.js` | **the prose layer** — hand-written from `RECAP.md`, `.memory/` and each pattern's `NOTES.md` |
| `build_data.py` | evidence → `data/` |
| `index.stdio.py` | optional JSON-RPC backend: `status`, `rebuild`, `doc` |
| `syntax.js` | the tokenizer behind every code view — C, Rust and Verus |
| `diff.js` | line diff between two rungs; comments dropped by default |
| `insights/insight_*.py` | **script-guarded notes** — prose whose claims are attached to assertions |
| `insights/asm_extract.py`, `asmcache/` | the compiled kernels, extracted once and digest-checked on every build |
| `common.js` / `common.css` / `vendor/` | the app framework, copied verbatim from `template_apps` |
| `check.mjs` | the gate: every view rendered against real data in a stubbed DOM |
| `tools/validate_palette.js` | the dataviz colour validator, vendored so `index.css`'s report can be re-run |
| `LESSONS.md` | the framework's pitfall list, copied verbatim |

### Reading the code

Every rung's source is syntax-highlighted, and the **Verus rung is highlighted
semantically** rather than decoratively. Four classes, chosen to match what this
project actually asks of a proof:

| class | what it marks |
|---|---|
| specification | `requires` `ensures` `invariant` `decreases` — what is promised |
| proof | `proof` `assert` `by` `forall` `lemma_*` — the work discharging it |
| ghost | `spec fn` `ghost` `tracked` `Seq` `int` — no run-time representation |
| **trusted** | `external_body` `assume` `#[verifier::…]` — **not verified**; the TCB |

That last class is the point: those bodies are taken on faith, and the report
counts them per pattern. Highlighting them puts the trusted base in the source
instead of only in a table.

Beside the eight rung tabs are four **diffs**, which are the ladder's own
transitions — C → hardened C, R2 → R3, R3 → R4, R4 → R5. There is no
gcc-vs-clang diff because both C cells compile the *same file*; that pair
differs by compiler, not by source. Comments are hidden by default: each rung
lives in its own file with its own banner comment, and on p03 a raw C diff is 66
changed comment lines around 8 changed code lines.

Two of the tabs are not source diffs at all. **hardened C → R4** compares the
languages with clang on the C side, because clang *is* the LLVM rustc ships and
gcc there would confound backend with language; its sources sit side by side
undiffed. **gcc vs clang** compiles one identical file with two backends, so the
source is shown once and only the machine code differs — that is the control the
language comparison depends on.

In the cross-language tab, clicking a line also lights the other side's lines
whose instructions are *identical* in both kernels. That correspondence is
inferred from the compiled code and is sparse — on p03 only 3 line pairs exist —
so a line without one names the lines that have one.

The R4 → R5 diff is the one to look at. Those two kernels are byte-identical
machine code, so everything the diff shows compiles to nothing at all.

Both views come in **split** (side by side, the default) and **unified**, with
a toggle; below ~940px split is not offered, because two code columns in a
phone-width window are two unreadable columns. Both panes cap their height and
scroll on their own — some diffs run to 800 lines.

Each diff also has an **assembly** view: what the source change did to the
compiled kernel. On R3 → R4 the removed instructions are the bounds check
itself; on R4 → R5 nothing changes at all. Two caveats travel with it, both on
the page. The text is *normalised* — immediates read `$` and branch targets
`TGT` — because two kernels computing different answers can normalise the same,
so identity is decided by the `md5(fn)` printed under each block. And the diff
is **not a bill for the check**: removing a check also changes what the
optimiser does next, which is why the same transition removes 11 instructions on
one pattern and 270 on another.

### The split that matters

Every **number** on the site is generated from `results/` and `results/gate/`.
Every **claim about what a number means** is in `content.js`, written by hand and
attributed. That is deliberate: this project's own history is full of numbers
that were right and sentences about them that were wrong, so the two are kept in
separate files and a rebuild can never quietly change a claim.

### Colour means the rung

One palette carries identity across every chart. There are **four base hues, one
per sub-family**, and each rung pair is that one base at two strengths:

| channel | meaning |
|---|---|
| hue family | **C is cool** (gcc cyan, clang blue) · **Rust is warm** (safe amber, unsafe red) |
| hue within family | gcc vs clang · safe vs unsafe |
| strength | **washed** — the base under white glass, `mix(base, white)` keeping 62% — is the plain rung; **solid** is the hardened, tuned or proven twin |

So R5 is solid red beside R4's washed red because it *is* R4 plus a proof, and
R1h is solid cyan beside R1's washed cyan because it is R1 plus the check. In the
diverging cost chart the bar takes the colour of whichever rung the excess
belongs to, so red never has to mean two things.

Profile charts are **horizontal**: one row per rung, the rung's name on the row
and its value at the right. That is why the palette can afford a washed member —
colour reinforces identity here, it does not carry it.

Values are validated with the dataviz skill's validator on this report's two
surfaces (light `#fdfdfc`, dark `#16181c`), in bar order. Cross-family
separation — the part that carries identity — passes in both modes; the three
checks that fail do so by construction (whitening lowers chroma, a pair is meant
to read as one hue, and washed light-mode members sit under 3:1). The full
report is in the comment block at the top of `index.css`.
The status palette (good / silent / crashed / refused) stays reserved for the
outcome matrix, where the subject is a behaviour rather than a rung. Every chart
has a table-view twin, and every mark also carries a label and a tooltip, so
colour is never the only channel.

## Checking a change

`check.mjs` runs every view against the real data in a stubbed DOM and validates the JSONML: no `null` children, no bad
tag strings, no throws, in every tab, for every pattern, at every filter setting.

```bash
node check.mjs                       # every view, every pattern, every rung and diff
node check.mjs --snap                # also freeze .temp/snap-*.html for screenshots
node tools/check_syntax.mjs          # tokens must reconstruct their source exactly
node tools/responsive_audit.mjs      # no grid overflows at any viewport
python3 insights/insight_codediff.py --print   # what each guarded note claims, and why
python3 insights/asm_extract.py --verify       # cached assembly still matches results/
```

It exercises every tab, every pattern, every rung's source view, every cost
filter combination and every rung-filter preset. **It does not see CSS** — take a
screenshot after a style change.

The `--snap` HTML files are fully-populated static renders, which is what to
screenshot — a live screenshot races the lazy fetches and catches "Loading…".
