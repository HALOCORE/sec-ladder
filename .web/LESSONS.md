# LESSONS.md — JSONML + Incremental DOM Pitfalls

Lessons that apply to any standalone web app built on the JSONML +
Incremental DOM framework in this template. Every rule below was learned
from a real silent bug — none throw errors, they just produce wrong UI.

> **Building an app that lives inside a ccneo shell (iframe-loaded)?**
> Read the full lesson list at `../../special_ui/server_ccneo/static/LESSONS.md`.
> It adds rules around iframe management, Monaco editor integration, the
> `scrollIntoView` cross-iframe leak, and Monaco-overlay mobile toolbars —
> none of which matter for a standalone app, but all bite if your app is
> embedded.


## 1. Never use `null` in JSONML arrays

**Problem:** JSONML throws `TypeError: Cannot read properties of null` when `null` appears as a child element.

**Bad:**
```javascript
["div",
  someCondition ? ["span", "Yes"] : null  // THROWS ERROR
]
```

**Good:**
```javascript
["div",
  someCondition ? ["span", "Yes"] : undefined  // undefined is ignored
]
```

**Why:** jsonml2idom checks `item.constructor` on each child. `null` has no constructor. `undefined` is filtered out.


## 2. Don't render wrapper-inside-wrapper

**Problem:** When doing partial re-renders, rendering a component with its wrapper INTO an existing wrapper element causes nesting.

```javascript
function jml_counter() {
  return ["div.demo-section",  // wrapper
    ["h2", "Counter"], ...
  ];
}

function updateCounter() {
  let section = document.querySelector('.demo-section');
  render_patch(section, jml_counter);  // BAD: puts .demo-section inside .demo-section
}
```

**Solutions:**

1. **Full re-render (simplest):** Re-render the whole tree. Incremental DOM diffs efficiently.
   ```javascript
   RENDER.counter = UI.debounce(renderAll, 16);
   ```

2. **Content-only functions:** Split wrapper from content.
   ```javascript
   function jml_counter_content() { return [["h2", "Counter"], ...]; }
   function jml_counter()         { return ["div.demo-section#counter", ...jml_counter_content()]; }
   render_patch(UI.$id("counter"), () => ["div", ...jml_counter_content()]);
   ```


## 3. Use IDs for partial render targets, not CSS selectors

Positional selectors like `.demo-section:nth-child(1)` are fragile and pick the wrong element when structure changes. Give partial-render targets an `id` and use `getElementById`.


## 4. Prefer full re-render over complex partial updates

```javascript
function renderAll() { UI.render_patch(ELEMS.app, jml_app); }

// All updates just re-render everything
RENDER.counter = UI.debounce(renderAll, 16);
RENDER.input   = UI.debounce(renderAll, 16);
RENDER.table   = UI.debounce(renderAll, 16);
```

`debounce(..., 16)` coalesces rapid updates into one frame. Incremental DOM only touches DOM nodes that actually changed.


## 5. JSONML requires a single root element

You cannot pass an array of siblings to `render_patch`. Wrap them in a container:

```javascript
function jml_content() {
  return ["div",                  // single root, required
    ["h1", "Title"],
    ["p", "Text"]
  ];
}
```


## 6. Use `key` for list items with stateful elements

Without keys, Incremental DOM matches by position. Deleting item 2 from a 3-item list:
1. Item 1 stays at position 0.
2. Item 3's *data* is written into position 1's existing DOM node.
3. Last element is removed.

For lists containing `<input>`, `<textarea>`, or any element with user state — typed value persists at the wrong row.

```javascript
function jml_row(item) {
  return ["tr",
    { key: "row-" + item.id },                                 // key by identity
    ["td", item.name],
    ["td", ["input", { key: "input-" + item.id, type: "text" }]]
  ];
}
```

**Corollary — imperatively-attached listeners survive too.** With stable keys, IDOM keeps the same DOM node across renders, so `addEventListener` calls made imperatively after first mount also survive. Wire once on mount; don't re-attach in a render loop.


## 7. `<textarea>` vs `<input>` — preserving user-typed content across re-renders

**`<textarea>`:** Text content lives as child text nodes. Without `skip: true`, IDOM reconciles children and wipes typed text.

```javascript
// BAD: typed text lost on re-render
["textarea", { placeholder: "..." }]
// GOOD: skip preserves children
["textarea", { placeholder: "...", skip: true }]
```

**`<input>`:** Typed value lives in the DOM `.value` property, NOT as a child or attribute. IDOM only patches attributes you specify. So as long as you **don't include `value`** in attrs, typed text is preserved without `skip`.

```javascript
// GOOD: no "value" attr → preserved
["input", { placeholder: "..." }]
// BAD: setting value would overwrite user input every render
["input", { placeholder: "...", value: "" }]
```

**`<select>`:** `.value` property is NOT reliably set by IDOM. Set it imperatively after render:
```javascript
function renderAll() {
  UI.render_patch(ELEMS.app, jml_app);
  let sel = document.querySelector("select");
  if (sel) sel.value = APP.selectedValue;
}
```


## 8. Per-instance persistent UI via show/hide pattern

When the same component exists for multiple entities (tabs, items, panels), switching between them recreates DOM and loses state. Solution: render ALL instances, each with a stable `key`, toggle visibility via CSS class. Only the selected one gets `.visible`.

```javascript
for (let name of allItems) {
  bars.push(
    ["div.my-bar" + (name === selected ? ".visible" : ""),
      { key: "bar-" + name },
      ["textarea", { id: "input-" + name, skip: true }],
      ["button", { onclick: () => onSend(name) }, "Send"]
    ]
  );
}
```

```css
.my-bar         { display: none; }
.my-bar.visible { display: flex; }
```

Event handlers capture `name` via closure — self-contained, no global selection lookup needed.


## 9. Never use conditional (`undefined`) children — always render, hide instead

**Problem:** IDOM without keys matches elements by position. If a conditional child is sometimes `undefined`, all subsequent siblings shift position. Siblings with `skip: true` get reconciled against the wrong element and are **destroyed** — losing all manually-managed content.

**Bad:**
```javascript
function jml_app() {
  return ["div.container",
    jml_header(),
    jml_status_bar(),
    APP.error ? ["div.error-box", "Error: " + APP.error] : undefined,  // SHIFTS POSITIONS
    jml_panels_area(),   // skip:true panels DESTROYED when positions shift
  ];
}
```

**Good:**
```javascript
function jml_app() {
  return ["div.container",
    jml_header(),
    jml_status_bar(),
    ["div.error-box", { key: "error", style: APP.error ? "" : "display:none" },
      APP.error ? "Error: " + APP.error : ""],
    jml_panels_area(),
  ];
}
```

**Rules:**
1. **Never skip siblings with `undefined`** — always render every element (hide with `display:none` or empty content).
2. **Add explicit `key` to containers that hold stateful/skip content** — keys ensure matching by identity, not position.


## 10. Boolean HTML attributes: use `undefined` to remove, not `false`

Boolean attrs like `disabled` are active when **present**, regardless of value. `disabled="false"` still disables.

```javascript
["button", { disabled: !isEnabled }, "Click"]                       // BAD
["button", { disabled: isEnabled ? undefined : true }, "Click"]     // GOOD
```

IDOM removes attributes set to `undefined`; any other value (including `false`, `0`, `""`) keeps the attribute.


## 11. Use dot-notation for CSS classes, NEVER `className` in attrs

jsonml2idom's `applyAttrsObj()` calls `IncrementalDOM.attr(k, v)` for each attr. `className` as an attr is set as a literal HTML attribute called `className` — browsers IGNORE it. No CSS classes apply. No console error.

```javascript
["div", { className: "shell-tab active" }, "Tab"]      // BAD — no styling
["div.shell-tab.active", { key: "tab-1" }, "Tab"]      // GOOD — dot-notation
```

**Dynamic classes** — concatenate into the tag string:
```javascript
["div.panel" + (isSelected ? ".visible" : ""), { key: "p-" + name }]
["button.tab" + (isActive ? ".active" : ""), { key: "t-" + id }]
```

**Don't mix dot-notation classes with `class` in attrs** — the attrs `class` overwrites dot-notation since `applyAttrsObj` runs after `openTag`.


## 12. Guard `setInterval` polling with an in-flight flag

When polling an async endpoint on a fixed interval, a slow response causes overlapping requests. Both may try to apply the same delta — silently duplicating content.

```javascript
let _polling = false;
setInterval(async () => {
  if (_polling) return;
  _polling = true;
  try {
    let resp = await fetchDelta(offset);
    content += resp.delta;
    offset = resp.newOffset;
  } finally {
    _polling = false;
  }
}, 500);
```

The `finally` block ensures the flag clears even if `fetchDelta` throws, so polling doesn't permanently stall.

## 13. `md()` does not nest — bold inside italic, or italic inside bold, breaks both

`md()` in `index.js` handles exactly three spans, and it finds them with one
flat `String.split` over an alternation. There is no recursion, so a marker of
one kind **inside** a span of another kind does not nest — it terminates the
outer span early and leaves literal asterisks on the page.

```javascript
// WRONG — the inner *shape* ends the outer ** span, and `.**` reaches the page
"**the tax is a function of the data's *shape*, not its *size*.**"

// WRONG — same failure, one marker further in
"**a row earns its place by bringing a new *mechanism***"

// RIGHT — pick one level of emphasis per span
"**the tax is a function of the data's shape, not its size.**"
"**a row earns its place by bringing a new mechanism**"
```

The bold alternative is literally `\*\*[^*]+\*\*`: *no asterisk may appear
between the markers*. The same applies to a `` ` `` code span inside emphasis —
the code span is matched first and its backticks stay literal.

Nothing throws. The tree is well-formed, the render check passes, and the page
just quietly has punctuation in it. `node check.mjs` now sweeps every tab and
every pattern write-up for a surviving `**`, and every tab that renders no code
for a surviving `*`; both were added after this bug shipped twice in one
session. `<pre>` and `<code>` are excluded, because upstream markdown and C
pointers are content rather than markup.

## 14. `grid-row: 1 / -1` needs explicit rows — or the span collapses and the rest auto-flows

This one shipped, on the ladder strip, and it was only visible on a phone.

```css
/* WRONG — what shipped */
.lv-row  { display: grid; grid-template-columns: 4px 1fr; }
.lv-rail { grid-row: 1 / -1; }        /* five children, two columns */
```

Two spec details combine:

1. **`-1` resolves against the *explicit* grid.** With no `grid-template-rows`,
   there is no explicit row track list, so `-1` is the *first* line and the span
   collapses to a single row instead of the full card height.
2. **Whatever the collapsed item stops covering is now free**, and the remaining
   children auto-flow into it, row-major.

So the rail took one cell, and `.lv-what` and `.lv-tcb` landed in the **4px rail
column**, where a sentence wraps one word per line and overlaps the cell beside
it. The rung title and its blurb were unreadable.

```css
/* RIGHT — explicit rows for the span, explicit column for every text child */
.lv-row  { grid-template-columns: 4px 1fr; grid-template-rows: repeat(4, auto); }
.lv-rail { grid-column: 1; grid-row: 1 / -1; }
.lv-id, .lv-what, .lv-check, .lv-tcb { grid-column: 2; min-width: 0; }
```

**The invariant, and it is what `tools/responsive_audit.mjs` now enforces: if a
grid has more children than columns, no auto-flowed child may land in a fixed
track of 24px or less.** Auto-placement is fine — stacking into a wide label
column is what a narrow layout is *supposed* to look like. Landing in a track
sized for a coloured bar is not. `.vleg-row` shows the other correct spelling:
its third child declares `grid-column: 1 / -1`, which works because that grid's
*columns* are explicit.

Nothing here was catchable by the render check (the tree was perfect), the
syntax check, or the overflow arithmetic (nothing overflowed — the row fit, it
was just illegible).

## 14b. `md()` nests code inside emphasis — and nothing else nests

`LESSONS #13` says emphasis does not nest, and that is still true: the bold
alternative is `\*\*[^*]+\*\*`, so bold-in-bold and italic-in-bold cannot match
and never will.

But that regex says nothing about **backticks**, and this is a project about
code:

```javascript
// Rendered four literal backticks on the page, for months
"**no `requires` and no `ensures`**"
```

`md()` matched the bold and pushed its inner text as a raw string. Twelve of
these shipped. So emphasis now recurses **once**, into a pass that knows only
code spans — `mdSpans(s, emph)`. Keeping the inner pass emphasis-blind is what
stops it looping, and it is all the nesting anyone here needs.

**The wider rule, which is what actually cost the time: every string a reader
sees is either prose or a label, and prose must go through `md()`.** These all
rendered their own punctuation because they did not:

| what | why it was missed |
|---|---|
| a KPI's **label** | its `sub` went through `md()` and its label did not |
| an `h3` heading | written as a bare string beside headings that had no markup |
| a `dataTable` cell | cells are rendered raw; wrap with `{jsonml: [...]}` |
| a pattern's `title` / `SHORT` name | used in headings, tooltips and the sidebar, none of which run `md()` |
| an environment's `{argument}` in `paper.js` | passed through as a raw string |

**A label is not prose.** `PATTERNS[].title`, `bug`, `family`, `role` and every
`SHORT` value are labels — they appear in tooltips and table cells, they can
never be `md()`'d, and `check.mjs` now fails if one contains markdown.

Everything else is prose, and `check.mjs` now fails on a literal backtick
reaching any tab. Measured: the right answer is **zero on every tab**. Two
exclusions, both principled — `<pre>` and `<code>` hold content rather than
markup, and upstream evidence quoted verbatim (a gate record's blocked-row
reason) is rendered as `code` for exactly that reason.

## 14c. LaTeX quote syntax in a `\section` title renders as literal backticks — and the count doubles

`paper_vers/*/sections/*.md` is markdown wearing LaTeX-shaped *markers*. It is
not LaTeX, and the difference bites in exactly one place a writer reaches for by
reflex:

```
\section{``It'll be slower.''}      // two literal backticks reach the page
\section{“It'll be slower.”}        // right
```

`md()` sees `` ``It'll ``, finds no closing backtick before the apostrophe run,
and passes the whole thing through as text. Nothing is malformed, nothing
throws, and the heading looks *almost* right — which is why this survived a
read-through of eight titles.

**The count is the tell, and it is why the arithmetic is worth knowing.** A
section title is rendered **twice** — once as the `h2`, once in the outline nav
— so seven titles with two backticks each reported **28**, not 14. If a
backtick count is an exact multiple of the section count times four, look at the
titles before you go hunting in the renderer.

⚠⚠ **AND THE PIPELINE WAS WRONG TOO — this entry originally blamed only the
prose, and that was half the bug.** A section title is rendered **twice**: as the
`h2`/`h3`, which goes through `paper.js`'s `inline()` and therefore `md()`, and
again in the outline nav, which pushed the **raw** `b.text`. So a *legitimate*
code span in a heading — `` \subsection{"So I write `unsafe` and I'm back on C's
rules."} `` — also reached the page as literal backticks, and a writer who
followed this entry's advice would have deleted correct markup to appease a
renderer defect. The outline now runs `md()` (`index.js`, `rendered.outline.map`).

**The doubling is the diagnostic and it points at the second render, not the
first.** If a backtick count is exactly twice what the source suggests, look for
a second, rawer path to the page before you touch the prose.
