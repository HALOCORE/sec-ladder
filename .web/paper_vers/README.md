# `paper_vers/` — the paper, in versioned source form

A tech report over the sec-ladder measurements, written as markdown with a small
set of LaTeX-shaped markers, rendered by `paper.js` into the **Paper** tab.

**One directory per FRAMING, not per draft.** `ver_A`, `ver_B`, … are different
*stories* over the same evidence. Editing a paragraph is a commit; deciding the
paper argues something else is a new `ver_`. Git carries the drafts; these
directories carry the arguments, so two framings can be read side by side and
the losing one does not have to be reconstructed from history.

```
paper_vers/
  README.md                 this file — the format, which is the durable part
  CLAIMS.md                 ⚠ what every version may and may not say — READ FIRST
  ver_A/
    meta.json               title, subtitle, status, and THE FRAMING STATEMENT
    paper.md                the manifest: \input in reading order, nothing else
    sections/*.md           the prose
    refs.json               bibliography, keyed
```

## Why not LaTeX, and why not plain markdown

Plain markdown cannot state a number without freezing it. This project's history
is mostly a record of correct numbers under sentences that outlived them —
"13 patterns", "47 catalogued", "byte-identical on every pattern" were each true
when written and false within days. So the format keeps `CLAUDE.md` rule 3: **a
number is generated, a claim is hand-written, and they live in different
places.** `\num{totals.patterns}` resolves against `data/index.json` at build
time and the build FAILS on a key that does not resolve. A count in this paper
cannot go stale without the gate saying so.

Everything else is markdown, because the prose is the part a human argues about.

### ⚠ `\num{}` keeps a NUMBER live. It does not keep a SENTENCE true.

This is the format's one real gap and it was found the hard way, in the middle of
writing ver_E. A 27th pattern landed upstream with gate verdict `FAIL`, and
`totals.patterns` went 26 → 27. Every `\num{}` in the paper updated correctly.
The prose went wrong anyway:

- *"On `\num{totals.identity_exact}` of the `\num{totals.patterns}` programs the
  proved and unproved builds are byte-identical"* rendered as **25 of the 27**,
  which silently asserts **two** exceptions where the paper then describes one.
- *"the twenty-sixth loosens that pin"* became an orphan.
- Every literal drawn from the project's own analysis — "22 of them are fair to
  subtract", "fifteen of the 26 are spatial" — was now stated against a corpus
  the analysis had never seen.

**What changed was not the number. It was the denominator's meaning.** A count
that pools a failing, half-built pattern in with 26 finished ones is the right
number for a status page and the wrong one for a report.

✅ **So a paper resolves against `totals.passing.*`** — the same arithmetic over
gate-passing patterns only, built in `build_data.py` beside the unscoped totals.
If nothing is failing they are identical, and the day something is, the paper's
evidence base does not silently acquire it.

✅ **And the rule that generalises:** `\num{}` protects a number against going
stale. **Nothing protects a sentence whose meaning depends on what a total
counts** — so when a figure carries a denominator, say what is in it. The paper
now discloses the excluded program in its own opening, which costs two sentences
and is cheaper than being caught at it.

## `CLAIMS.md` — read it before writing

`\num{}` stops a *count* going stale. It does nothing about a *claim* that was
always wrong. `CLAIMS.md` is the second half: a committed list of the things a
draft of this paper asserted and had to withdraw, with the correct form beside
each. It spans every version, because a false claim is false in every framing,
and it is committed precisely because the verification behind it lived in
`.temp/` and got cleared.

## Markers

### Structure

| marker | what it does |
|---|---|
| `\input{sections/x.md}` | include, recursively; cycles are a build error |
| `\section{Title}` | numbered section |
| `\subsection{Title}` | numbered subsection |
| `\label{sec:x}` | name the preceding section, figure or environment |
| `\ref{sec:x}` | render its number, hyperlinked; a dangling ref is a build error |

### Live values — the whole point of the format

| marker | what it does |
|---|---|
| `\num{totals.patterns}` | dot-path into `data/index.json`, thousands-separated |
| `\num{totals.cells\|raw}` | same, unformatted |
| `\num{totals.verus_verified\|plain}` | same, no thousands separators |

An unresolvable path fails the build. A path that resolves to an object or an
array fails too — `\num` is for scalars.

### Environments

```
\begin{abstract}
...
\end{abstract}
```

`abstract`, `principle{Short name}`, `example{Caption}`, `takeaway`,
`caveat{Heading}`, `retraction{What was claimed}`, `quote{Attribution}`.

`principle` and `example` are the paper's spine: **a principle is a rule a
reader could follow, an example is the smallest concrete thing that makes it
land.** The renderer numbers principles and lists them in the outline, so a
principle that never gets an example is visible at a glance.

### Inline

| marker | what it does |
|---|---|
| `\src{patterns/p03-bounded-stack/NOTES.md}` | a provenance chip — where a claim comes from |
| `\cite{key}` | bibliography reference, keyed into `refs.json` |
| `\pat{p03}` | a pattern's id and short name, pulled live from `data/index.json` |
| `\todo{...}` | visible in the rendered draft, and counted on the Paper tab |

Markdown inline formatting (`**bold**`, `*italic*`, `` `code` ``) is handled by
the site's own `md()`. ⚠ It does **not** nest — see `LESSONS.md` #13.

### Figures

`\figure{id}{Caption text}` renders a live figure from the report's own data,
so the paper and the rest of the site cannot disagree. `id` must be one the
renderer knows; an unknown id is a build error. The known ids are listed in
`paper.js` next to the function that draws each one.

## The loop

```bash
python3 build_data.py     # resolves \input, validates every \num, \ref, \cite, \figure
node check.mjs            # renders the paper in a stubbed DOM like every other view
```

The build prints the paper's word count, its `\todo` count, and the number of
principles that have no example. None of those are failures; they are the
draft's own dashboard.
