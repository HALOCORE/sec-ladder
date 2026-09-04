# .web — the sec-ladder report

A static web report over the measurements in the repository one level up: the
safety ladder explained, what each rung costs, what each rung does under hostile
input, the proof burden and its trusted base, every pattern's own numbers and
sources, the cross-cutting findings, and the method with its caveats. It is a
**reporting layer over someone else's live research** — the parent repo is being
extended by other agents while you work here.

Read `RECAP.md` next: it carries the state, the design decisions and the traps.
Its **START HERE** box and the **"What is built, and what is next"** section
immediately under it are written for a cold resume — read those two first and
you can continue without the conversation that produced them.

## Where things are

- `README.md` — how to serve it, rebuild it, and what each file is. Outward-facing.
- `RECAP.md` — **state of this app, why it is shaped this way, what is owed.** Start there.
- `PITFALLS.md` — **what did not work, and cost real sessions.** ⚠ **Read it
  before writing prose or touching the renderer.** Its first four entries are one
  mistake in four disguises and they are why five framings of the report were
  rejected; §3 is one renderer bug class found four separate times. Most of it
  was found by a *reader*, not by a check — the gates were green throughout.
- `build_data.py` — the only writer. Evidence (`../results/`, `../patterns/`) → `data/`.
- `index.js` — every view (JSONML + Incremental DOM). `content.js` — **all prose**.
- `index.css` — styling, and the rung-colour system with its validation report at the top.
- `index.stdio.py` — optional JSON-RPC backend: `status`, `rebuild`, `doc`. The page works without it.
- `LESSONS.md` — the JSONML/Incremental-DOM pitfall list. Every rule in it was a real silent bug.
- `check.mjs` — the gate. Renders every view against real data in a stubbed DOM.
- `syntax.js` — the hand-rolled tokenizer for every code view. Emits **tokens, not HTML** (this page has no innerHTML anywhere). Its contract is that tokens reconcatenate to the source byte-for-byte; `tools/check_syntax.mjs` enforces it.
- `diff.js` — line diff between two rungs. Comments are dropped by default and that is not cosmetic; see the file header.
- `paper_vers/` — **the tech report, in versioned source form**, rendered by
  `paper.js` into the **Paper** tab. One directory per **framing** (`ver_A`,
  `ver_B`, …), not per draft: editing a paragraph is a commit, deciding the
  paper argues something else is a new `ver_`. The format is markdown plus
  LaTeX-shaped markers, and it exists so that **a number in the paper cannot go
  stale** — `\num{totals.patterns}` resolves against `data/index.json` at build
  time and an unresolvable path **fails the build**, as do a `\ref` with no
  `\label`, a `\cite` with no bibliography entry, an unknown `\figure` id and an
  `\input` cycle. Spec: `paper_vers/README.md`. ⚠ `md()` does not nest emphasis
  (`LESSONS.md` #13) and `check.mjs` fails on a surviving `**`.
- `insights/insight_*.py` — **script-guarded notes**, see below.
- `insights/asm_extract.py` + `asmcache/` — the kernel assembly diffs. The text is NOT in `results/`; it is extracted from `../.temp/build` binaries (1.7 GB of deletable scratch) and committed. Every side records the `md5_fn` that `results/` publishes for the same cell, and `build_data.py` drops any diff whose digests no longer match. **Never run objdump here** — `harness/asm.py` is the repo's only objdump pipeline; import it.
- `insights/asm_map.py` — the source↔assembly link. The measured binaries carry **no line info for this project's code**, so it builds a throwaway `-g` twin and takes the line table from that. The twin is aligned against the measured kernel instruction by instruction and every line is graded **certain / likely / approximate** — `-g` is codegen-neutral for C but not for Rust, so a twin cannot simply be assumed identical. Only a twin sharing under half the instruction stream is refused. **The alignment between two sources counts certain and likely only.** Flags come from `harness/build.py`'s own `c_flags`/`rust_flags`; do not retype them.
- `tools/validate_palette.js` — the dataviz colour validator, vendored so the checks documented in `index.css` stay runnable.
- `.memory/` — **this agent's memory, in the repo.** Preferences and standing decisions, one fact per file. See rule 9 and `.memory/README.md`.
- `data/` — derived, gitignored, rebuilt in about a second. Never hand-edit.

## Script-guarded notes

Prose that makes a claim about the research tree does not get to be a bare
string. It lives in `insights/insight_*.py` **attached to assertions**, and is
emitted only while every assertion still holds. A failed guard withholds the
note, exits non-zero, and `build_data.py` turns that into a warning the Method
tab renders — so a stale claim announces itself instead of sitting there being
wrong. `python3 insights/insight_codediff.py --print` shows every note's
verdict and the evidence behind it.

Write the guard against `results/`, `results/gate/` or the pattern's own source.
Reading a number out of `.web/data/` and calling it evidence is circular —
`build_data.py` derived it from the same place the note did.

Two things this already caught, which is the argument for it: the R4≡R5
"compiles to nothing" note **declines to apply to p36**, whose kernels are not
byte-identical, without anyone having to know that; and a probe note asserting
p01's safe and unsafe kernels were identical was withheld rather than published.

## The loop

```bash
python3 build_data.py              # after anything lands upstream; heed its warnings
node check.mjs                     # must print OK before you believe a change
node check.mjs --snap              # static renders in .temp/, which is what to screenshot
node tools/responsive_audit.mjs    # after ANY layout change; exits 1 on overflow
node tools/check_syntax.mjs        # after ANY syntax.js change; exits 1 on a mangled token stream
python3 insights/asm_extract.py    # ONLY when ../.temp/build binaries are fresh; refreshes asmcache/
python3 insights/asm_map.py        # then this: source lines per instruction, via verified debug twins
python3 insights/insight_codediff.py --print   # what each guarded note currently claims, and why
```

The page is already served at `http://127.0.0.1:8000/pw11apt/apps/pub-to38u0zfu2/`
by the ccneo server the user runs. Views are hash-routed (`#cost`,
`#patterns/p17-http-range`).

## Don't

0. **Do not write prose without reading `PITFALLS.md` first.** The gates cannot
   see the defect that has cost this project the most: a document that is
   correct, fully qualified, and unreadable. ⚠ **If a figure needs a qualifier it
   cannot carry, cut the figure, not the qualifier** — and *"the reader was
   confused by X"* never means *"explain X better"*.
1. **Never write outside `.web/`.** The parent is an active research tree; a
   `git status` there must be unchanged by anything you run. `build_data.py`
   routes every write through `_out()`, which refuses any path outside this
   directory — keep it that way, and keep `index.stdio.py` read-only upstream.
   This directory is **its own git repo** — commit here when the user asks for it,
   and never run a history-mutating git command in the parent.
2. **Never hard-code a count, a pattern name, or a claim that the data can
   settle.** "13 patterns", "47 catalogued" and "byte-identical on every
   pattern" were all true when written and all false within days. Derive from
   `data/index.json`; if a sentence cannot be derived, write it in `content.js`
   where it is visibly a claim and not a fact.
3. **Never let `index.js` state a number that `content.js` also states.**
   Numbers are generated; interpretation is hand-written and attributed. That
   split is the whole reason a rebuild cannot quietly change a claim.
4. **No new server.** One is running and it already serves this folder. Do not
   start `http.server` "just to check" — screenshot the `--snap` files over
   `file://` instead (dot-directories are not served).
5. **Scratch goes in `.temp/`, and the artefact does not survive the task.**
   Keep the generators (`check.mjs`, `tools/`), delete what they produce — PNGs,
   browser profiles, snapshot HTML. Same rule as the parent repo's `.temp/`.
6. **Do not trust a green render check for a CSS change.** It validates the
   JSONML tree, not the stylesheet. Deleting a CSS block by line range once
   removed the rung swatches and made every bar transparent while the check
   stayed green. **Screenshot after any CSS edit**, and run
   `node tools/responsive_audit.mjs`, which catches the narrow-viewport half
   arithmetically: a grid whose fixed tracks exceed the container, and a chart
   row whose label and value columns leave the bar no width. It does not judge
   whether the result looks right — only eyes do that.
7. **Do not repaint by rank.** Colour identifies the rung, everywhere. A filter
   that hides a rung must leave the others' colours untouched, and any palette
   change must be re-run through the validator documented at the top of
   `index.css`.
8. **Do not remove a table view, a direct label or a tooltip to make a chart
   cleaner.** Three light-mode rung colours sit under 3:1 on purpose; the labels
   and the table twin are what make that legal.
9. **Memory goes in `.memory/` HERE, never in `~/.claude/…/memory/`.** Anything
   worth remembering across sessions — the user's preferences, standing
   decisions, corrections — is a file in `.web/.memory/`, versioned with the code
   it describes and reviewable in a diff. A note in the harness's own memory
   directory is invisible to everyone but the agent that wrote it, cannot be
   reviewed, and drifts from the code silently.
   ⚠ **`.web/.memory/` is not `../.memory/`.** The parent's `.memory/` 00–06 is
   the research project's authoritative findings layer, written by the
   researcher agents under `PROTOCOL.md` rule 9 — writing there would break
   rule 1 as well as pollute their layer.
   ⚠ **What goes where:** the user and how they want the work done → `.memory/`.
   The state of the app, what is built and what is owed → `RECAP.md`. The rules
   for editing → this file. See `.memory/README.md`.
