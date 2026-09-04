// index.js — sec-ladder report.
//
// Architecture (JSONML + Incremental DOM, per ../LESSONS.md):
//   - One JSONML root (#app); every state change goes through renderAll().
//   - All tab panels are always in the DOM; only the active one has `.visible`
//     (LESSONS #8), so scroll position and <details> state survive tab switches.
//   - Never a `null` child (LESSONS #1); conditional content is rendered empty
//     rather than omitted, and containers holding it carry a stable `key`.
//   - Classes are dot-notation in the tag string, never `className` (LESSONS #11).
//
// Data:  data/index.json is loaded once; data/patterns/<id>.json and
//        data/code/<id>.json are fetched on first use and cached.  Every number
//        rendered here comes from those files, i.e. from results/ and
//        results/gate/ — the prose comes from content.js.

console.log("===== sec-ladder report =====");

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "ladder",   label: "The ladder" },
  { id: "cost",     label: "Cost of safety" },
  { id: "security", label: "Hostile input" },
  { id: "proof",    label: "Proof & trusted base" },
  { id: "patterns", label: "Patterns" },
  { id: "findings", label: "Findings" },
  { id: "method",   label: "Method" },
  { id: "paper",    label: "Paper" },
];

const APP = {
  tab: "overview",
  data: null,
  err: null,
  cost: { metric: "marginal", mode: "isolated", input: "small.bin" },
  ladderInput: "small.bin",
  secPattern: null,
  proofPattern: null,
  paperVer: null,
  slide: 0,              // which slide of the talk the banner is showing
  deckFull: false,       // deck owns the whole viewport
  patId: null,
  patRung: "safe_tuned",
  patDiff: null,          // null = show one rung; else a DIFF_PAIRS id
  diffAsm: false,         // show the compiled kernels rather than the source
  diffOpt: "O3",          // which optimisation level's assembly
  diffLayout: "split",    // "split" | "unified"; narrow viewports force unified
  linkSel: null,          // {side:"a"|"b", line:N} — the source line linked to
  diffNotes: false,       // prose folded away in the linked view; both panes need the height
  diffComments: false,    // comments are noise in these diffs; hidden by default
  findTag: "all",
  rungs: null,          // Set of visible cells; null until initRungs()
};


const CACHE = { pattern: {}, code: {}, docs: {}, asm: {}, paper: {} };
let ELEMS = {};
let _sc = null;                     // UI.createSmartConfirm instance, wired in main_init

// ============================================================ small helpers ==

const RUNG_ORDER = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
                    "safe_naive", "safe_tuned", "unsafe", "verus", "safe_naive_verus"];
const RUNG_SHORT = {
  "c-gcc": "R1 gcc", "c-clang": "R1 clang", "c-gcc-h": "R1h gcc", "c-clang-h": "R1h clang",
  "safe_naive": "R2", "safe_tuned": "R3", "unsafe": "R4", "verus": "R5", "safe_naive_verus": "R2v",
};
const RUNG_NAME = {
  "c-gcc": "C (gcc)", "c-clang": "C (clang)", "c-gcc-h": "hardened C (gcc)",
  "c-clang-h": "hardened C (clang)", "safe_naive": "safe Rust, naive",
  "safe_tuned": "safe Rust, tuned", "unsafe": "unsafe Rust", "verus": "unsafe Rust + Verus",
  "safe_naive_verus": "safe Rust + Verus",
};
const CLASS_LABEL = {
  match: "as specified", silent: "silent + wrong", hung: "never returned",
  crash: "crashed", loud: "refused", other: "other", none: "not built",
};
const CLASS_ICON = { match: "✓", silent: "✕", hung: "∞", crash: "!", loud: "▲", other: "?", none: "·" };
// status colour per outcome — reserved tokens, each shipped with an icon and a label
const CLASS_TONE = {
  match: "good", silent: "critical", hung: "warning", crash: "serious",
  loud: "other", other: "other", none: "none",
};

// Which rungs the profile charts draw.  One selection, shared by the ladder wall,
// the pattern profiles and the cost table, so a comparison set holds while you
// move around.  Colour is bound to the rung, not to the row, so hiding one never
// repaints the others.
const RUNG_PRESETS = [
  { id: "all", label: "All rungs", cells: RUNG_ORDER },
  { id: "backend", label: "Same backend", cells: ["c-clang", "c-clang-h", "safe_tuned", "verus"],
    tip: "clang is bit-for-bit the LLVM rustc ships, so this is the only C-vs-Rust comparison with no backend difference in it: C, C+check, idiomatic safe Rust, and proven unsafe Rust." },
  { id: "rust", label: "Rust only", cells: ["safe_naive", "safe_tuned", "unsafe", "verus", "safe_naive_verus"],
    tip: "The four Rust rungs — the spelling gap and the safety gap side by side." },
  { id: "c", label: "C only", cells: ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h"],
    tip: "What the check costs inside one language, on both compilers." },
  { id: "checked", label: "Checked vs unchecked", cells: ["c-clang", "c-clang-h", "unsafe", "safe_tuned"],
    tip: "The two unchecked rungs against the two that carry the check." },
];

function initRungs() {
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem("slb-rungs") || "null"); } catch (e) {}
  const valid = Array.isArray(saved) && saved.length && saved.every(c => RUNG_ORDER.includes(c));
  APP.rungs = new Set(valid ? saved : RUNG_ORDER);
}
function rungOn(cell) { return !APP.rungs || APP.rungs.has(cell); }
function saveRungs() {
  try { localStorage.setItem("slb-rungs", JSON.stringify([...APP.rungs])); } catch (e) {}
}
function toggleRung(cell) {
  if (APP.rungs.has(cell)) {
    if (APP.rungs.size === 1) return;          // never leave a chart with nothing in it
    APP.rungs.delete(cell);
  } else {
    APP.rungs.add(cell);
  }
  saveRungs(); renderAll();
}
function setRungs(cells) { APP.rungs = new Set(cells); saveRungs(); renderAll(); }
function activePreset() {
  const cur = [...APP.rungs].sort().join(",");
  const hit = RUNG_PRESETS.find(p => p.cells.slice().sort().join(",") === cur);
  return hit ? hit.id : null;
}
// the rungs a given pattern actually has, in ladder order, honouring the filter
function visibleRungs(cellsPresent) {
  return RUNG_ORDER.filter(c => cellsPresent[c] && rungOn(c));
}

const pid = (id) => id.split("-")[0];

// A pattern that landed in the repo after this page's prose was written still
// gets a usable name and an honest "no narrative yet" note, rather than a blank.
function fallbackTitle(id) {
  const rest = id.split("-").slice(1).join(" ");
  return rest ? rest.charAt(0).toUpperCase() + rest.slice(1) : id;
}
const pname = (id) => (CONTENT_PATTERNS()[id] || {}).title || fallbackTitle(id);
const pshort = (id) => (typeof SHORT !== "undefined" && SHORT[id]) || fallbackTitle(id).toLowerCase();
const prow = (id) => pid(id) + " " + pshort(id);

function CONTENT_PATTERNS() { return typeof PATTERNS !== "undefined" ? PATTERNS : {}; }

function fmt(n, d) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const v = d ? Number(n).toFixed(d) : Math.round(n);
  return String(v).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
function sfmt(n, d) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const s = n > 0 ? "+" : n < 0 ? "−" : "";
  return s + fmt(Math.abs(n), d);
}
// 48,714 -> 48.7k.  Small multiples only; the tooltip and the table keep the
// exact value, so nothing is rounded away.
function compact(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const a = Math.abs(n);
  if (a >= 1e6) return (n / 1e6).toFixed(a >= 1e7 ? 0 : 1) + "M";
  if (a >= 1e4) return (n / 1e3).toFixed(0) + "k";
  if (a >= 1e3) return (n / 1e3).toFixed(1) + "k";
  return String(Math.round(n));
}

function pctf(x, d) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  const s = x > 0 ? "+" : x < 0 ? "−" : "";
  return s + Math.abs(x).toFixed(d === undefined ? 1 : d) + "%";
}
function cls(v) { return v > 0 ? ".pos" : v < 0 ? ".neg" : ".zero"; }

// **bold** and `code` -> JSONML children.  Text only; never innerHTML.
// Bold, code and italic — the three this project's prose actually uses.
//
// Italic was missing and 106 emphasised spans across content.js and index.js
// were rendering as literal asterisks, in sentences whose whole point was the
// emphasis ("the *verdict*, not the position"; "*what* is computed, not *how
// long* it takes"). The italic alternative comes LAST so `**bold**` and code
// spans still win, and it is deliberately narrow: the opener may not follow a
// word character and the closer may not precede one, so arithmetic like
// `2*n*m` is left alone. Verified against every string in both files.
// ⚠ CODE SPANS NEST INSIDE EMPHASIS; EMPHASIS DOES NOT NEST INSIDE EMPHASIS.
//
// The bold alternative is `\*\*[^*]+\*\*` — no asterisk between the markers, so
// bold-in-bold cannot match and never will. But it says nothing about backticks,
// so `**no `requires` and no `ensures`**` matched as bold and pushed its inner
// text as a RAW STRING, printing four literal backticks on the page. That is
// ordinary prose in a paper about code, it happened twelve times across the
// draft, and nothing threw.
//
// So emphasis recurses ONCE, into a pass that knows only code spans. That is
// the whole of the nesting anyone here needs, and keeping the inner pass
// emphasis-blind is what stops it looping.
function md(s) { return mdSpans(String(s), true); }

function mdSpans(s, emph) {
  const re = emph
    ? /(\*\*[^*]+\*\*|`[^`]+`|(?<![\w*])\*(?![\s*])[^*]*[^\s*]\*(?![\w*]))/g
    : /(`[^`]+`)/g;
  const out = [];
  s.split(re).forEach((part, i) => {
    if (!part) return;
    if (emph && part.startsWith("**") && part.endsWith("**"))
      out.push(["strong", { key: "b" + i }, ...mdSpans(part.slice(2, -2), false)]);
    else if (part.startsWith("`") && part.endsWith("`"))
      out.push(["code", { key: "c" + i }, part.slice(1, -1)]);
    else if (emph && part.startsWith("*") && part.endsWith("*"))
      out.push(["em", { key: "i" + i }, ...mdSpans(part.slice(1, -1), false)]);
    else out.push(part);
  });
  return out;
}
const mdP = (s, k) => ["p", { key: k || "p" }, ...md(s)];

function tip(text) { return { "data-tip": text }; }

// Rung identity is a colour: C is cool (gcc cyan, clang blue), Rust is warm
// (safe yellow, unsafe red), and the darker member of each pair is the hardened
// / tuned / proven one.  One class per cell, defined once in index.css.
const sw = (cell) => ".sw-" + cell;

// A legend is the identity channel for these charts, so it is always present —
// and here it is also the control: click a key to drop that rung from every
// profile chart.  The off state is carried by more than colour (struck-through
// label, hollow key), per the accessibility rule.
function rungLegend(cells, opts) {
  const o = opts || {};
  return ["div.rung-toggles", { key: o.key || "lg" },
    ...cells.map(c => ["button.rtog" + (rungOn(c) ? "" : ".off"),
      Object.assign({ key: "lg" + c, onclick: () => toggleRung(c) },
        tip(`${RUNG_SHORT[c]} · ${RUNG_NAME[c]}\n${rungOn(c) ? "shown — click to hide" : "hidden — click to show"}`)),
      ["span.k" + sw(c)],
      ["span.lbl", o.short ? RUNG_SHORT[c] : RUNG_SHORT[c] + " " + RUNG_NAME[c]],
    ]),
  ];
}

// Preset comparison sets, above the toggles.
function rungPresets(key) {
  const act = activePreset();
  return ["div.field", { key: key || "pre", style: "flex:1;min-width:300px" },
    ["span.field-label", "compare"],
    ["div.seg",
      ...RUNG_PRESETS.map(p => ["button" + (act === p.id ? ".on" : ""),
        Object.assign({ key: "pr" + p.id, onclick: () => setRungs(p.cells) },
          p.tip ? tip(p.tip) : {}),
        p.label]),
    ],
  ];
}

// ================================================================== charts ==

// Diverging bars: one row per category, zero in the middle, warm = dearer.
function chartDiverging(opts) {
  const rows = opts.rows.filter(r => r.value !== null && r.value !== undefined && !Number.isNaN(r.value));
  const max = Math.max(1e-9, ...rows.map(r => Math.abs(r.value)));
  const zero = 50;
  return ["div.chart", { key: opts.key || "dv" },
    ["div.chart-head",
      ["div",
        ["div.chart-title", opts.title],
        ["div.chart-sub", ...md(opts.sub || "")],
      ],
      ["div.legend",
        ["span.legend-item", ["span.legend-key" + (opts.posSw || ".sw-safe_tuned")], opts.posLabel || "dearer"],
        ["span.legend-item", ["span.legend-key" + (opts.negSw || ".sw-unsafe")], opts.negLabel || "cheaper"],
      ],
    ],
    ["div.dbar-rows",
      ...rows.map((r, i) => {
        const w = (Math.abs(r.value) / max) * 48;
        const style = r.value >= 0
          ? `left:${zero}%;width:${w}%`
          : `right:${100 - zero}%;width:${w}%`;
        return ["div.dbar-row", { key: "r" + i, onclick: r.onclick },
          ["div.dbar-name", r.name],
          ["div.dbar-track", { style: `--zero:${zero}%` },
            ["div.dbar-fill" + (r.value >= 0 ? ".pos" + (opts.posSw || ".sw-safe_tuned")
                                             : ".neg" + (opts.negSw || ".sw-unsafe")),
              Object.assign({ style }, tip(r.tip || `${r.name}\n${opts.valueFmt(r.value)}`))],
          ],
          ["div.dbar-val" + cls(r.value), opts.valueFmt(r.value)],
        ];
      }),
    ],
    ["div.chart-foot", ...md(opts.foot || "")],
    tableFold(opts.tableHead || ["", "value"], rows.map(r => [r.name, opts.valueFmt(r.value)]), "tv" + (opts.key || "")),
  ];
}

// Spread: one row per comparison, showing the RANGE a single number covers
// across many builds of identical machine code, with zero marked.
//
// Every other chart here plots one value per rung, which is the right shape
// when the value is determined by the source.  Wall clock is not: the layout
// control builds the same kernel 31 ways and the rung-to-rung difference lands
// anywhere in a band.  A dot plot would say "here is the number"; this says
// "here is the interval, and it contains zero", which is the actual finding.
//
// Colour follows the diverging chart's rule exactly — the band takes the colour
// of whichever rung is the dearer one on that side of zero — so red and blue
// keep meaning the same rungs they mean everywhere else.  The individual builds
// are drawn as neutral ticks: they are samples, not rungs.
function chartSpread(opts) {
  const rows = (opts.rows || []).filter(r => Number.isFinite(r.min) && Number.isFinite(r.max));
  const M = Math.max(1e-9, ...rows.map(r => Math.max(Math.abs(r.min), Math.abs(r.max))));
  const px = (v) => 50 + (v / M) * 48;
  const seg = (from, to) => `left:${px(from)}%;width:${Math.max(0, px(to) - px(from))}%`;
  return ["div.chart", { key: opts.key || "sp" },
    ["div.chart-head",
      ["div",
        ["div.chart-title", opts.title],
        ["div.chart-sub", ...md(opts.sub || "")],
      ],
      ["div.legend", ...(opts.legend || []).map((l, i) =>
        ["span.legend-item", { key: "lg" + i }, ["span.legend-key" + l.sw], l.label])],
    ],
    ["div.dbar-rows",
      ...rows.map((r, i) => ["div.dbar-row", { key: "r" + i },
        ["div.dbar-name", r.name],
        ["div.dbar-track", { style: "--zero:50%" },
          // both halves always render (LESSONS rule 9); an empty one is 0 wide
          ["div.spread-band.neg" + (r.negSw || ""), { key: "n", style: seg(Math.min(r.min, 0), Math.min(r.max, 0)) }],
          ["div.spread-band.pos" + (r.posSw || ""), { key: "p", style: seg(Math.max(r.min, 0), Math.max(r.max, 0)) }],
          ...(r.values || []).map((v, j) => ["div.spread-tick", Object.assign(
            { key: "t" + j, style: `left:${px(v)}%` }, tip(`${r.name}\n${opts.valueFmt(v)}`))]),
        ],
        ["div.dbar-val", opts.valueFmt(r.min) + " … " + opts.valueFmt(r.max)],
      ]),
    ],
    ["div.chart-foot", ...md(opts.foot || "")],
    tableFold(opts.tableHead || ["", "lowest", "highest", "builds below zero", "builds above zero", "builds"],
      rows.map(r => [r.name, opts.valueFmt(r.min), opts.valueFmt(r.max),
                     String(r.neg), String(r.pos), String(r.n)]), "tv" + (opts.key || "")),
  ];
}

// Dumbbell: two points per row, one hue in two shades.
function chartDumbbell(opts) {
  const rows = opts.rows.filter(r => r.a !== null && r.b !== null && r.a !== undefined && r.b !== undefined);
  const lo = Math.min(0, ...rows.map(r => Math.min(r.a, r.b)));
  const hi = Math.max(...rows.map(r => Math.max(r.a, r.b)));
  const span = (hi - lo) || 1;
  const px = (v) => ((v - lo) / span) * 100;
  return ["div.chart", { key: opts.key || "db" },
    ["div.chart-head",
      ["div",
        ["div.chart-title", opts.title],
        ["div.chart-sub", ...md(opts.sub || "")],
      ],
      ["div.legend",
        ["span.legend-item", ["span.legend-key" + (opts.aSw || "") + (opts.aSw ? "" : ".seqa"),
          { style: "border-radius:50%" + (opts.aSw ? "" : ";background:var(--seq-250)") }], opts.aLabel],
        ["span.legend-item", ["span.legend-key" + (opts.bSw || "") + (opts.bSw ? "" : ".seqb"),
          { style: "border-radius:50%" + (opts.bSw ? "" : ";background:var(--seq-550)") }], opts.bLabel],
      ],
    ],
    ["div.dumb-rows",
      ...rows.map((r, i) => {
        const a = px(r.a), b = px(r.b);
        const l = Math.min(a, b), w = Math.abs(a - b);
        return ["div.dumb-row", { key: "r" + i },
          ["div.dbar-name", r.name],
          ["div.dumb-track",
            ["div.dumb-axis"],
            ["div.dumb-conn" + (opts.aSw ? ".pairline" : ""), { style: `left:${l}%;width:${w}%` }],
            ["div.dumb-dot.a" + (opts.aSw || ""), Object.assign({ style: `left:${a}%` },
              tip(`${r.name}\n${opts.aLabel}: ${opts.valueFmt(r.a)}`))],
            ["div.dumb-dot.b" + (opts.bSw || ""), Object.assign({ style: `left:${b}%` },
              tip(`${r.name}\n${opts.bLabel}: ${opts.valueFmt(r.b)}`))],
          ],
          ["div.dumb-val", `${opts.valueFmt(r.a)}  →  ${opts.valueFmt(r.b)}`],
        ];
      }),
    ],
    ["div.chart-foot", ...md(opts.foot || "")],
    tableFold([" ", opts.aLabel, opts.bLabel],
      rows.map(r => [r.name, opts.valueFmt(r.a), opts.valueFmt(r.b)]), "tv" + (opts.key || "")),
  ];
}

// Horizontal bars — one row per rung, one series, magnitude.  The rung's name
// sits on the row and its value at the tip, so colour reinforces identity here
// rather than carrying it.
function barsChart(items, opts) {
  const o = opts || {};
  const max = Math.max(1e-9, ...items.map(i => i.value || 0));
  return ["div.bars" + (o.small ? ".small" : ""), { key: o.key || "bars" },
    ...items.map((it, i) => ["div.bar-row", { key: "b" + i },
      ["div.bar-lab", it.label],
      ["div.bar-track",
        ["div.bar-fill" + (it.cell ? sw(it.cell) : ""),
          Object.assign({ style: `width:${Math.max(0.6, (it.value / max) * 100)}%` },
            tip(it.tip || `${it.label}: ${fmt(it.value)}`))],
      ],
      ["div.bar-val", o.small ? compact(it.value) : fmt(it.value)],
    ]),
  ];
}

// The table twin every chart carries (WCAG-clean equivalent, LESSONS-safe).
function tableFold(head, rows, key) {
  return ["details.fold", { key: key || "tf" },
    ["summary", "Table view"],
    ["div.fold-body",
      ["div.table-wrap",
        ["table.tbl",
          ["thead", ["tr", ...head.map((h, i) => ["th" + (i ? ".num" : ""), { key: "h" + i }, h])]],
          ["tbody", ...rows.map((r, i) => ["tr", { key: "r" + i },
            ...r.map((c, j) => ["td" + (j ? ".num" : ""), { key: "c" + j }, String(c)])])],
        ],
      ],
    ],
  ];
}

// The Security and Proof tabs each end in a detail pane for ONE pattern, and
// the only way to change it used to be clicking a row in the table above it —
// an affordance with no label, no control and no mark on the selected row. On a
// phone, where the table scrolls sideways, the connection is invisible. So the
// pane header carries a real picker, and the table marks its current row.
function patternPicker(tab, sel, key) {
  const d = APP.data;
  return ["div.pane-pick", { key: key || "pp" },
    ["label.pane-pick-l", { for: "pick-" + tab }, "pattern"],
    ["select.sel", {
      id: "pick-" + tab,
      onchange: (e) => go(tab, e.target.value),
    },
      ...d.patterns.map(p => ["option", {
        key: "o" + p.id, value: p.id,
        // LESSONS #10 — a boolean attribute is removed with undefined, not false
        selected: p.id === sel ? "selected" : undefined,
      }, pid(p.id) + " — " + pname(p.id)]),
    ],
  ];
}

function dataTable(head, rows, key, opts) {
  const o = opts || {};
  return ["div.table-wrap", { key: key || "dt" },
    ["table.tbl",
      ["thead", ["tr", ...head.map((h, i) => ["th" + ((o.num || []).includes(i) ? ".num" : ""), { key: "h" + i }, h])]],
      ["tbody", ...rows.map((r, i) => ["tr" + (o.selRow === i ? ".on" : ""), { key: "r" + i, onclick: o.onRow ? () => o.onRow(i) : undefined },
        ...r.map((c, j) => {
          const isNum = (o.num || []).includes(j);
          const wrap = (o.wrap || []).includes(j);
          if (c && typeof c === "object" && c.jsonml) return ["td" + (isNum ? ".num" : "") + (wrap ? ".wrap" : ""), { key: "c" + j }, c.jsonml];
          return ["td" + (isNum ? ".num" : "") + (wrap ? ".wrap" : "") + (c && c.cls ? c.cls : ""),
            { key: "c" + j }, String(c && c.text !== undefined ? c.text : c)];
        })])],
    ],
  ];
}

// The rung strip's top rule: one rung's own colour, or a two-stop gradient when
// the rung covers two compilers (R1 = gcc + clang, R1h likewise).
function rungStripe(r) {
  const v = (c) => `var(--rung-${c === "safe_naive" ? "r2" : c === "safe_tuned" ? "r3"
    : c === "unsafe" ? "r4" : c === "verus" ? "r5"
    : c === "safe_naive_verus" ? "r2v" : c})`;
  if (r.cells.length === 1) return v(r.cells[0]);
  return `linear-gradient(90deg, ${v(r.cells[0])} 0 50%, ${v(r.cells[1])} 50% 100%)`;
}

// The sub-label went through md() and the label did not, so a KPI naming a flag
// or a type printed its own backticks. Both are prose; both get the same pass.
function kpi(label, value, sub, tone) {
  return ["div.kpi", { key: "k-" + label },
    ["div.kpi-label", ...md(label)],
    ["div.kpi-value" + (tone ? "." + tone : ""), value],
    ["div.kpi-sub", ...md(sub || "")],
  ];
}

function callout(kind, head, body) {
  return ["div.callout." + kind, { key: "co-" + head },
    ["div.callout-h", head],
    ...(Array.isArray(body) ? body : [body]).map((b, i) => ["p", { key: "b" + i }, ...md(b)]),
  ];
}

// ============================================================= data access ==

async function loadIndex() {
  try {
    // data/index.boot.js (written by build_data.py) puts the summary in scope at
    // parse time; the fetch is the fallback for a hand-copied data/ directory.
    if (typeof window !== "undefined" && window.SLB_INDEX) {
      APP.data = window.SLB_INDEX;
    } else {
      const res = await fetch("./data/index.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      APP.data = await res.json();
    }
    APP.patId = APP.data.patterns[0].id;
    APP.secPattern = APP.data.patterns[1] ? APP.data.patterns[1].id : APP.patId;
    APP.proofPattern = APP.patId;
    readHash();                       // now that pattern ids are known
    // warm the three details the first interaction will want, so the panels do
    // not open on a "Loading…" line
    [APP.patId, APP.secPattern, APP.proofPattern].forEach(id => { if (id) loadPattern(id); });
  } catch (e) {
    APP.err = `Could not load data/index.json (${e.message}). Run: python3 .web/build_data.py`;
  }
  renderAll();
}

async function loadPattern(id) {
  if (CACHE.pattern[id]) return CACHE.pattern[id];
  CACHE.pattern[id] = "loading";
  try {
    const res = await fetch(`./data/patterns/${id}.json`, { cache: "no-store" });
    CACHE.pattern[id] = await res.json();
  } catch (e) {
    CACHE.pattern[id] = { error: String(e) };
  }
  renderAll();
  return CACHE.pattern[id];
}

async function loadDocs(id) {
  if (CACHE.docs[id]) return CACHE.docs[id];
  CACHE.docs[id] = "loading";
  try {
    const res = await fetch(`./data/docs/${id}.json`, { cache: "no-store" });
    CACHE.docs[id] = await res.json();
  } catch (e) {
    CACHE.docs[id] = { error: String(e) };
  }
  renderAll();
  return CACHE.docs[id];
}

// The kernel assembly diffs.  Extracted once by insights/asm_extract.py and
// validated against results/ at build time — see build_data.py::asm_for.
async function loadAsm(id) {
  if (CACHE.asm[id]) return CACHE.asm[id];
  CACHE.asm[id] = "loading";
  try {
    const res = await fetch(`./data/asm/${id}.json`, { cache: "no-store" });
    CACHE.asm[id] = res.ok ? await res.json() : { absent: true };
  } catch (e) {
    CACHE.asm[id] = { absent: true };
  }
  renderAll();
  return CACHE.asm[id];
}

async function loadCode(id) {
  if (CACHE.code[id]) return CACHE.code[id];
  CACHE.code[id] = "loading";
  try {
    const res = await fetch(`./data/code/${id}.json`, { cache: "no-store" });
    CACHE.code[id] = await res.json();
  } catch (e) {
    CACHE.code[id] = { error: String(e) };
  }
  renderAll();
  return CACHE.code[id];
}

const pat = (id) => (APP.data ? APP.data.patterns.find(p => p.id === id) : null);

// The cost model the whole "cost" view is computed from.
function costSel(p) {
  const c = APP.cost;
  if (c.metric === "kernel") return (p.kern || {})[`isolated/${c.input}`];
  return (p.tax || {})[`${c.mode}/${c.input}`];
}
function costDelta(p, cell) {
  const sel = costSel(p);
  if (!sel || !sel.cells[cell]) return null;
  return sel.cells[cell].delta;
}
function costRatioPct(p, cell) {
  const sel = costSel(p);
  if (!sel || !sel.cells[cell] || !sel.base) return null;
  return (sel.cells[cell].delta / sel.base) * 100;
}

// ================================================================== render ==

function renderAll() { UI.render_patch(ELEMS.app, jml_app); }
const renderSoon = UI.debounce(renderAll, 16);

// The split/unified fallback is computed at render time from the viewport, so a
// resize has to re-render or the page keeps a two-column diff in a phone-width
// window.  Debounced through the same path as everything else.
if (typeof window !== "undefined" && window.addEventListener) {
  let lastW = window.innerWidth;
  window.addEventListener("resize", () => {
    const w = window.innerWidth;
    // only when the answer could have changed, not on every pixel
    if ((lastW < SPLIT_MIN_PX) !== (w < SPLIT_MIN_PX)) renderSoon();
    lastW = w;
  });
}

function jml_app() {
  return ["div.app",
    jml_topbar(),
    ["div.panel-area",
      jml_panel("overview", viewOverview),
      jml_panel("ladder", viewLadder),
      jml_panel("cost", viewCost),
      jml_panel("security", viewSecurity),
      jml_panel("proof", viewProof),
      jml_panel("patterns", viewPatterns),
      jml_panel("findings", viewFindings),
      jml_panel("method", viewMethod),
      jml_panel("paper", viewPaper),
    ],
  ];
}

function jml_panel(id, fn) {
  return ["div.panel" + (APP.tab === id ? ".visible" : ""), { key: "panel-" + id },
    ["div.wrap", { key: "w-" + id }, APP.tab === id ? fn() : ["div", { key: "idle" }, ""]],
  ];
}

function jml_topbar() {
  return ["div.topbar",
    ["div.topbar-in",
      ["div.brand",
        ["span.brand-name", "sec-ladder"],
        ["span.brand-sub", "performance ↔ memory-safety, measured"],
      ],
      ["div.tabs",
        ...TABS.map(t => ["button.tab" + (APP.tab === t.id ? ".active" : ""),
          { key: "t-" + t.id, onclick: () => go(t.id) },
          t.label]),
      ],
      ["button.icon-btn", { key: "theme", onclick: toggleTheme }, themeLabel()],
    ],
  ];
}

// ------------------------------------------------------ hash routing (links) --
// `#cost`, `#patterns/p02-buffer-copy` — so a paragraph in an email can point at
// one chart, and so a screenshot of a given view is reproducible.

function go(tab, id) {
  const moved = APP.tab !== tab;
  APP.tab = tab;
  if (id) {
    if (tab === "patterns") APP.patId = id;
    if (tab === "security") APP.secPattern = id;
    if (tab === "proof") APP.proofPattern = id;
  }
  writeHash();
  renderAll();
  if (moved) window.scrollTo(0, 0);
}

function writeHash() {
  const t = APP.tab;
  const sub = t === "patterns" ? APP.patId : t === "security" ? APP.secPattern
    : t === "proof" ? APP.proofPattern : null;
  const h = "#" + t + (sub ? "/" + sub : "");
  if (location.hash !== h) {
    _hashSelf = true;
    location.hash = h;
  }
}
let _hashSelf = false;

function readHash() {
  const raw = decodeURIComponent((location.hash || "").replace(/^#/, ""));
  if (!raw) return;
  const [tab, sub] = raw.split("/");
  if (!TABS.some(t => t.id === tab)) return;
  APP.tab = tab;
  if (sub && APP.data && APP.data.patterns.some(p => p.id === sub)) {
    if (tab === "patterns") APP.patId = sub;
    if (tab === "security") APP.secPattern = sub;
    if (tab === "proof") APP.proofPattern = sub;
  }
}

function themeLabel() {
  const t = document.documentElement.getAttribute("data-theme");
  return t === "dark" ? "☾ dark" : t === "light" ? "☀ light" : "◐ auto";
}
function toggleTheme() {
  const el = document.documentElement;
  const cur = el.getAttribute("data-theme");
  const next = cur === "light" ? "dark" : cur === "dark" ? null : "light";
  if (next) el.setAttribute("data-theme", next); else el.removeAttribute("data-theme");
  try { next ? localStorage.setItem("slb-theme", next) : localStorage.removeItem("slb-theme"); } catch (e) {}
  renderAll();
}

// ---------------------------------------------------------------- overview --

// The one result on the front page, and every number in it is derived.
//
// The Overview leads with the argument by design — but it carried no finding at
// all, and a cold reader left with the method and none of the point. This is
// the most repeatable thing the corpus says to a C programmer, and it is a
// statement about WHICH RUNG FAILED, not a benchmark figure.
function headlineResult() {
  const d = APP.data, t = d.totals;
  const dev = new Set();
  d.patterns.forEach(p => Object.keys(p.adversarial.worst_by_cell || {}).forEach(c => {
    if (p.adversarial.worst_by_cell[c] !== "match") dev.add(c);
  }));
  const onlyC = dev.size && [...dev].every(c => c === "c-gcc" || c === "c-clang");
  if (!onlyC) {
    // a Rust rung has deviated: the sentence below is no longer true, so say
    // what IS true rather than printing a claim the data has overtaken
    return ["p.intro-p", { key: "hr" }, ...md(
      `Across **${fmt(t.adversarial_runs)}** runs on deliberately malformed input, the rungs that deviated from the reference implementation were: **`
      + [...dev].map(c => RUNG_NAME[c]).join(", ") + `** — ${fmt(t.silent)} of those runs silently wrong, ${fmt(t.crash)} loud.`)];
  }
  return ["p.intro-p.callout-lite", { key: "hr" }, ...md(
    `And one result is worth having before any of the numbers. Across **${fmt(t.adversarial_runs)}** runs on deliberately malformed input, `
    + `**every single deviation from the reference implementation is in a plain-C build** — no rung above it, at any level of safety, ever returned a wrong answer. `
    + `**${fmt(t.silent)} of those failures are silent**: exit code 0, a plausible number, no diagnostic. Only ${fmt(t.crash)} crash. `
    + `⚠ The reason that reads so cleanly is itself a finding, and it is on the **Hostile input** tab: the safe rungs are not merely surviving these attacks, they are structurally incapable of failing them.`)];
}

function viewOverview() {
  if (APP.err) return ["div.callout.retract", ["div.callout-h", "No data"], ["p", APP.err]];
  if (!APP.data) return ["div.loading", "Loading…"];

  return ["div", { key: "ov" },
    ["div.eyebrow", "a micro-benchmark for the security ↔ performance trade"],
    ["h1", "Memory safety is not a yes-or-no choice, and its price can be measured rung by rung."],
    ["p.lede", ...md(INTRO.lede)],

    ["div.section", { key: "problem" },
      ...INTRO.problem.map((s, i) => ["p.intro-p", { key: "ip" + i }, ...md(s)]),
      // ⚠ The front page deliberately leads with the argument rather than with
      // statistics — but it had NO result on it at all, and the single most
      // repeatable thing this project found was four tabs away. One sentence,
      // and every number in it is DERIVED, so a pattern whose Rust rung
      // misbehaves rewrites this line by itself.
      headlineResult(),
    ],

    // The ladder is the argument, so it comes before anything measured.
    ["div.section", { key: "ladder" },
      ["h2", "Two ladders, climbing toward each other"],
      ["p.section-note", ...md("The two languages start at opposite ends of the same trade. **C begins fast and unchecked**, and safety is something you add to it by hand. **Rust begins checked by the language**, and speed is something you win back — first by spelling the program better, and finally by removing the check and *proving* it was unnecessary. Every pattern is built at all six rungs — except p01, which models no bug and so has no hardened-C rung — and that is what lets the two climbs be priced against each other.")],
      ladderViz(),
      ["p.small.muted.mt16", ...md("A seventh cell, **R2v** (safe Rust + Verus), is built once on p01 as a control: proving the safe rung panic-free changes nothing in the binary, because rustc never learns what the solver knew.")],
    ],

    ["div.section", { key: "three" },
      ["h2", "What this measures that a single benchmark number cannot"],
      ["div.grid.g3.mt16",
        ...INTRO.points.map((p, i) => ["div.card", { key: "pt" + i },
          ["h3", p[0]],
          ["p.small.muted", { key: "b" }, ...md(p[1])],
        ]),
      ],
    ],

    ["div.section", { key: "next" },
      ["h2", "Where the numbers are"],
      ["p.section-note", ...md("Every figure on this site is read out of the committed evidence in the repository above this one. Nothing is re-measured in the browser, and nothing is rounded on the way in.")],
      ["div.next-grid.mt16",
        ...INTRO.next.map(([tab, label, blurb]) => ["button.next-card", {
          key: "nx-" + tab, onclick: () => go(tab),
        },
          ["div.next-label", label],
          ["div.next-blurb", ...md(blurb)],
        ]),
      ],
    ],

    ["div.section", { key: "prov" },
      ["h2", "Provenance"],
      ["p.section-note", "Every number on this site is read out of the committed evidence files; nothing is re-measured in the browser."],
      provenanceTable(),
    ],
    footer(),
  ];
}

// The ladder, as the overview's centrepiece.  Two tracks, because the languages
// approach the trade from opposite ends: C starts fast and adds the check, Rust
// starts checked and takes the cost back out.  Within a track, one row per rung,
// the rung's own colour as a rail, and the two columns that actually vary — who
// enforces the check, and what is left trusted.
//
// R4 carries `aside` and renders de-emphasised.  It is measured on every pattern
// and it is not a destination: the guarantee is surrendered there and only R5's
// proof returns it.  A ladder that let the climb end at "unsafe" would be
// telling the reader the opposite of what this project found.
//
// Qualitative on purpose — every number belongs to a later tab.
function ladderViz() {
  const cols = ["", "rung", "what it is", "where the check lives", "what you still trust"];
  return ["div.lv-tracks", { key: "lvt" },
    ...TRACKS.map(tr => {
      const rungs = LADDER.filter(r => r.track === tr.id && r.rung !== "R2v");
      return ["div.lv-track", { key: "trk-" + tr.id },
        ["div.lv-track-h", { key: "th" },
          ["div.lv-track-name", { key: "n" }, tr.name],
          ["div.lv-track-start", { key: "s" }, tr.start],
          ["div.lv-track-dir", { key: "d" }, tr.dir],
        ],
        ["p.lv-track-arc", { key: "arc" }, ...md(tr.arc)],
        ["div.ladder-viz", { key: "viz" },
          ["div.lv-head", { key: "lvh" },
            ...cols.map((c, i) => ["div", { key: "h" + i }, c]),
          ],
          ...rungs.map(r =>
            ["div.lv-row" + (r.aside ? ".aside" : ""), {
              key: "lv-" + r.rung, style: `--step:${rungStripe(r)}`,
            },
              ["div.lv-rail", { key: "rail" }, ""],
              ["div.lv-id", { key: "id" }, r.rung],
              ["div.lv-what", { key: "what" },
                ["div.lv-title", { key: "t" }, r.title],
                ["div.lv-line", { key: "l" }, ...md(r.line)],
                ...(r.aside ? [["div.lv-aside", { key: "a" }, r.aside]] : []),
              ],
              ["div.lv-check", { key: "chk" }, ...md(r.check)],
              ["div.lv-tcb", { key: "tcb" }, ...md(r.tcb)],
            ]),
        ],
      ];
    }),
  ];
}

// ------------------------------------------------------------ code views ----
// Tokens become JSONML spans, never an HTML string — this page has no innerHTML
// anywhere and syntax.js is built to emit a token list for exactly that reason.
// Unclassified text is emitted as a bare string rather than a wrapped span, so
// a 900-line kernel costs a few hundred nodes instead of a few thousand.

function tokenSpans(toks, keyBase) {
  const out = [];
  for (let i = 0; i < toks.length; i++) {
    const t = toks[i];
    if (t.t) out.push(["span.tk-" + t.t, { key: keyBase + i }, t.s]);
    else out.push(t.s);
  }
  return out;
}

function codeBlock(text, lang, key) {
  const lines = SYNTAX.tokenizeLines(text, lang);
  const kids = [];
  for (let i = 0; i < lines.length; i++) {
    kids.push(...tokenSpans(lines[i], "k" + i + "_"));
    if (i < lines.length - 1) kids.push("\n");
  }
  return ["pre.code", { key: key }, ...kids];
}

// A one-line Verus expression (a `requires`/`ensures` clause from the contract).
function clauseLine(text, key) {
  return ["pre.code.clause", { key: key },
    ...tokenSpans(SYNTAX.tokenize(text, "verus"), "c" + key + "_")];
}

function verusLegend() {
  return ["div.vlegend", { key: "vleg" },
    ["div.eyebrow", "the proof layer, by what it does to the guarantee"],
    ...VERUS_LEGEND.map(([cls, name, blurb]) => ["div.vleg-row", { key: "vl" + cls },
      ["span.vleg-key.tk-" + cls, { key: "k" }, "abc"],
      ["span.vleg-name", { key: "n" }, name],
      ["span.vleg-blurb", { key: "b" }, ...md(blurb)],
    ]),
  ];
}

// ---- diff layout -----------------------------------------------------------
// Split reads correspondence better; unified reads *change* better, which is
// why a 3-line edit in a 200-line function is easier to find unified.  Both are
// offered.  Below the breakpoint split is not offered at all — two code columns
// in 500px are two unreadable columns — so the layout is computed rather than
// taken straight from APP.
const SPLIT_MIN_PX = 940;

// ---- source <-> assembly linking -------------------------------------------
// Click a source line, the instructions it compiled to light up and the
// assembly pane scrolls to them; click an instruction, its source line lights
// up.  The link is PER SIDE — a diff has two sources and two kernels, and A's
// line 49 has nothing to do with B's line 49 — so a selection carries the side
// it was made on.  asmcache's `map.al` / `map.bl` hold each instruction's line
// on each side, which is why a context instruction can answer to both.

function selectLine(side, line) {
  if (!line || line < 0) return;                       // 0 = unmapped, -1 = inlined
  const s = APP.linkSel;
  APP.linkSel = (s && s.side === side && s.line === line) ? null : { side: side, line: line };
  renderAll();
  // the first matching instruction is tagged #asm-sel by the renderer
  if (typeof document !== "undefined" && document.getElementById) {
    const el = document.getElementById("asm-sel");
    if (el && el.scrollIntoView) el.scrollIntoView({ block: "center", behavior: "smooth" });
  }
}

function selMatches(side, line) {
  const s = APP.linkSel;
  return !!(s && line > 0 && s.side === side && s.line === line);
}

// ---- alignment through the assembly ----------------------------------------
// Two sources in different languages have no line-to-line correspondence of
// their own — but their COMPILED kernels do, and that can be read backwards.
//
// If an instruction carries a line on both sides, those two lines produced the
// same instruction and are related.  Two things supply such pairs: a context
// instruction, which is literally identical in both kernels, and a change row
// in the split pairing, where a deletion sits opposite an insertion.  The first
// is strong evidence, the second is positional and weaker, so they are counted
// separately and the caller can say which it is showing.
//
// ⚠ This is INFERRED, not measured. It is a useful way to find the other side's
// neighbourhood, not a claim that one line "became" the other, and the page
// labels it that way.
function relatedLines(d, side, line) {
  if (!d || !d.map || !(line > 0)) return { strong: [], weak: [] };
  const from = side === "a" ? d.map.al : d.map.bl;
  const to = side === "a" ? d.map.bl : d.map.al;
  const fc = side === "a" ? d.map.ac : d.map.bc;
  const tc = side === "a" ? d.map.bc : d.map.ac;
  const strong = new Set();
  for (let i = 0; i < d.ops.length; i++) {
    if (d.ops[i][0] !== " " || from[i] !== line) continue;
    // an approximate line on either end is not evidence of correspondence — it
    // is a positional guess, and two of those do not make a fact
    if (fc && fc[i] === CONF_APPROX) continue;
    if (tc && tc[i] === CONF_APPROX) continue;
    if (to[i] > 0) strong.add(to[i]);
  }
  return { strong: [...strong].sort((x, y) => x - y) };
}

// Every line pair this diff supports, so a line with no correspondence can say
// where the correspondences ARE instead of being a dead end.  Cross-language
// alignment is sparse by nature: on p03's C-against-Rust only 5 of 112
// instructions are shared, giving 3 line pairs.
function allRelated(pair, pid) {
  const rec = CACHE.asm[pid];
  const pairs = [];
  if (!rec || !rec.pairs) return pairs;
  const seen = new Set();
  for (const aid of (pair.asm || [])) {
    const bo = rec.pairs[aid]; const d = bo && (bo[APP.diffOpt] || bo.O3);
    if (!d || !d.map) continue;
    for (let i = 0; i < d.ops.length; i++) {
      if (d.ops[i][0] !== " ") continue;
      const a = d.map.al[i], b = d.map.bl[i];
      if (d.map.ac && (d.map.ac[i] === CONF_APPROX || d.map.bc[i] === CONF_APPROX)) continue;
      if (a > 0 && b > 0 && !seen.has(a + ":" + b)) { seen.add(a + ":" + b); pairs.push([a, b]); }
    }
  }
  return pairs.sort((x, y) => x[0] - y[0]);
}

// The union across every assembly block in this view — a C pair has two.
function relatedFor(pair, pid, side, line) {
  const rec = CACHE.asm[pid];
  const out = { strong: new Set() };
  if (!rec || !rec.pairs) return out;
  for (const aid of (pair.asm || [])) {
    const bo = rec.pairs[aid]; const d = bo && (bo[APP.diffOpt] || bo.O3);
    if (!d) continue;
    relatedLines(d, side, line).strong.forEach(x => out.strong.add(x));
  }
  return out;
}

// Is `line` on `side` related to the current selection, via the assembly?
function relMatches(pair, side, line) {
  const s = APP.linkSel;
  if (!s || !(line > 0) || s.side === side) return "";
  const r = relatedFor(pair, APP.patId, s.side, s.line);
  return r.strong.has(line) ? ".rel" : "";
}

// ---- how much a mapped line is worth -----------------------------------------
// Set by insights/asm_map.py, which aligns the measured kernel against its debug
// twin instruction by instruction.  See that file's align() for why `-g` cannot
// simply be assumed codegen-neutral.
const CONF_CERTAIN = 2, CONF_LIKELY = 1, CONF_APPROX = 0;
const CONF_NAME = {
  2: "certain", 1: "likely", 0: "approximate",
};
const CONF_WHY = {
  2: "the debug twin compiled to the same instructions as the measured binary, so this line is exact",
  1: "the twin differs elsewhere, but this instruction sits in a matching run — same instruction, same position",
  0: "inside a run where the twin and the measured binary differ; the line is anchored by position only",
};

// The class an instruction wears for its mapping confidence.  Only the two
// weaker tiers are marked: `certain` is the default and marking it would put a
// badge on almost every row and say nothing.
function confCls(d, i) {
  if (!d.map || !d.map.ac) return "";
  const a = d.map.al[i], b = d.map.bl[i];
  if (!(a > 0) && !(b > 0)) return "";
  const c = a > 0 ? d.map.ac[i] : d.map.bc[i];
  return c === CONF_LIKELY ? ".c-likely" : c === CONF_APPROX ? ".c-approx" : "";
}

function confOf(d, i, side) {
  if (!d.map) return null;
  const arr = side === "a" ? d.map.ac : d.map.bc;
  return arr ? arr[i] : null;
}

// Does instruction `i` of this diff belong to the current selection?
function asmSelMatches(d, i) {
  const s = APP.linkSel;
  if (!s || !d.map) return false;
  const arr = s.side === "a" ? d.map.al : d.map.bl;
  return arr && arr[i] === s.line && s.line > 0;
}

function effectiveLayout() {
  const w = (typeof window !== "undefined" && window.innerWidth) || 1440;
  return w < SPLIT_MIN_PX ? "unified" : APP.diffLayout;
}

function sourceUnifiedRows(r) {
  const rows = [];
  let i = 0;
  for (const op of r.ops) {
    i++;
    if (op.k === "@") {
      rows.push(["div.dl.skip", { key: "s" + i }, `⋯ ${op.n} unchanged line${op.n === 1 ? "" : "s"}`]);
      continue;
    }
    const src = op.k === "-" ? op.a : op.b;
    // a unified row belongs to whichever side it came from; a context row is
    // claimed by the side the reader is currently linked to, defaulting to A
    const side = op.k === "+" ? "b" : op.k === "-" ? "a"
      : (APP.linkSel && APP.linkSel.side === "b" ? "b" : "a");
    const line = side === "a" ? (op.a && op.a.no) : (op.b && op.b.no);
    rows.push(["div.dl.d" + (op.k === "+" ? "add" : op.k === "-" ? "del" : "ctx")
      + (selMatches(side, line) ? ".sel" : ""), {
        key: "d" + i, onclick: () => selectLine(side, line),
      },
      ["span.dl-no", { key: "na" }, op.a ? String(op.a.no) : ""],
      ["span.dl-no", { key: "nb" }, op.b ? String(op.b.no) : ""],
      ["span.dl-sign", { key: "sg" }, op.k],
      ["span.dl-src", { key: "sc" }, ...tokenSpans(src.toks, "t" + i + "_")],
    ]);
  }
  return rows;
}

// Two sources that are not the same language, put side by side rather than
// diffed.  Nothing is marked added or removed, because nothing was: these are
// two independent programs, and pretending line 12 of one "became" line 12 of
// the other would be an invented correspondence.  Clicking still works — the
// link is by side and line number, which does not need a diff.
// Both rungs compile the same file, so it is shown once.  Clicking a line
// lights that line's instructions in EVERY assembly block below, which is the
// whole point of a same-source pair: one line, two backends.
function sourceSingleRows(A, pair) {
  const lines = SYNTAX.tokenizeLines(A.text, SYNTAX.langFor(pair.a, A.lang));
  const base = A.first_line || 1;
  return lines.map((toks, i) => ["div.dl.dctx" + (selMatches("a", base + i) || selMatches("b", base + i) ? ".sel" : ""),
    { key: "s" + i, onclick: () => selectLine("a", base + i) },
    ["span.dl-no", { key: "n" }, String(base + i)],
    ["span.dl-sign", { key: "g" }, " "],
    ["span.dl-src", { key: "c" }, ...tokenSpans(toks, "s" + i + "_")],
  ]);
}

// Longest subsequence of anchors that is strictly increasing on BOTH sides.
// Anchors come from the assembly and nothing stops two of them crossing — line
// 60 of C sharing an instruction with line 70 of Rust while line 62 shares with
// line 65.  Laying those out in order is impossible, so the crossing ones are
// dropped rather than allowed to scramble the pairing.
function risingAnchors(pairs) {
  const n = pairs.length;
  if (n < 2) return pairs.slice();
  const len = new Array(n).fill(1), prev = new Array(n).fill(-1);
  let best = 0;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < i; j++) {
      if (pairs[j][0] < pairs[i][0] && pairs[j][1] < pairs[i][1] && len[j] + 1 > len[i]) {
        len[i] = len[j] + 1; prev[i] = j;
      }
    }
    if (len[i] > len[best]) best = i;
  }
  const out = [];
  for (let k = best; k >= 0; k = prev[k]) out.unshift(pairs[k]);
  return out;
}

// Two sources laid out so the lines that produced the SAME INSTRUCTION sit on
// the same row.  Between anchors each side runs at its own pace and the shorter
// one gets blank cells, so the panes stay in step without pretending the gaps
// correspond.  This is the alignment the assembly buys: the sources have no
// line correspondence of their own, and this one is derived, not assumed.
function sourceAlignedRows(A, B, pair) {
  const la = SYNTAX.tokenizeLines(A.text, SYNTAX.langFor(pair.a, A.lang));
  const lb = SYNTAX.tokenizeLines(B.text, SYNTAX.langFor(pair.b, B.lang));
  const fa = A.first_line || 1, fb = B.first_line || 1;

  const anchors = risingAnchors(allRelated(pair, APP.patId))
    .map(([x, y]) => [x - fa, y - fb])
    .filter(([i, j]) => i >= 0 && i < la.length && j >= 0 && j < lb.length);
  if (!anchors.length) return sourcePairRows(A, B, pair);

  const rows = [];
  let i = 0, j = 0, k = 0;
  const emit = (ai, bj, isAnchor) => {
    const an = ai === null ? null : fa + ai, bn = bj === null ? null : fb + bj;
    const cell = (toks, side, no) => toks
      ? [["span.sl-no", { key: side + "n" }, String(no)],
         ["span.sl-src", { key: side + "s" }, ...tokenSpans(toks, side + k + "_")]]
      : [["span.sl-no", { key: side + "n" }, ""],
         ["span.sl-src.blank", { key: side + "s" }, ""]];
    rows.push(["div.sl" + (isAnchor ? ".anchor" : ""), { key: "a" + (k++) },
      ["div.sl-side" + (ai === null ? ".none" : "")
        + (selMatches("a", an) ? ".sel" : relMatches(pair, "a", an)),
        { key: "L", onclick: () => ai !== null && selectLine("a", an) },
        ...cell(ai === null ? null : la[ai], "l", an)],
      ["div.sl-side" + (bj === null ? ".none" : "")
        + (selMatches("b", bn) ? ".sel" : relMatches(pair, "b", bn)),
        { key: "R", onclick: () => bj !== null && selectLine("b", bn) },
        ...cell(bj === null ? null : lb[bj], "r", bn)],
    ]);
  };

  for (const [ai, bj] of anchors) {
    while (i < ai || j < bj) emit(i < ai ? i++ : null, j < bj ? j++ : null, false);
    emit(i++, j++, true);
  }
  while (i < la.length || j < lb.length) {
    emit(i < la.length ? i++ : null, j < lb.length ? j++ : null, false);
  }
  return rows;
}

function sourcePairRows(A, B, pair) {
  const la = SYNTAX.tokenizeLines(A.text, SYNTAX.langFor(pair.a, A.lang));
  const lb = SYNTAX.tokenizeLines(B.text, SYNTAX.langFor(pair.b, B.lang));
  const fa = A.first_line || 1, fb = B.first_line || 1;
  const n = Math.max(la.length, lb.length);
  const out = [];
  for (let i = 0; i < n; i++) {
    const cell = (toks, side, no) => toks
      ? [["span.sl-no", { key: side + "n" }, String(no)],
         ["span.sl-src", { key: side + "s" }, ...tokenSpans(toks, side + i + "_")]]
      : [["span.sl-no", { key: side + "n" }, ""],
         ["span.sl-src.blank", { key: side + "s" }, ""]];
    const an = fa + i, bn = fb + i;
    out.push(["div.sl", { key: "p" + i },
      ["div.sl-side" + (la[i] ? "" : ".none")
        + (selMatches("a", an) ? ".sel" : relMatches(pair, "a", an)),
        { key: "L", onclick: () => la[i] && selectLine("a", an) }, ...cell(la[i], "l", an)],
      ["div.sl-side" + (lb[i] ? "" : ".none")
        + (selMatches("b", bn) ? ".sel" : relMatches(pair, "b", bn)),
        { key: "R", onclick: () => lb[i] && selectLine("b", bn) }, ...cell(lb[i], "r", bn)],
    ]);
  }
  return out;
}

// Same content stacked, for narrow viewports where two columns will not fit.
function sourcePairUnified(A, B, pair) {
  const out = [];
  for (const [cell, src, side] of [[pair.a, A, "a"], [pair.b, B, "b"]]) {
    out.push(["div.dl.skip", { key: "h" + side }, `${RUNG_NAME[cell]} — ${src.file}`]);
    const base = src.first_line || 1;
    SYNTAX.tokenizeLines(src.text, SYNTAX.langFor(cell, src.lang)).forEach((toks, i) => {
      const no = base + i;
      out.push(["div.dl.dctx" + (selMatches(side, no) ? ".sel" : ""),
        { key: side + i, onclick: () => selectLine(side, no) },
        ["span.dl-no", { key: "n" }, String(no)],
        ["span.dl-sign", { key: "g" }, " "],
        ["span.dl-src", { key: "s" }, ...tokenSpans(toks, side + i + "_")],
      ]);
    });
  }
  return out;
}

let PAIR_IN_VIEW = null;   // set by diffBlock; relMatches() needs the pair

function sourceSplitRows(r) {
  const out = [];
  let i = 0;
  for (const row of DIFF.splitRows(r.ops, o => o.k)) {
    i++;
    if (row.kind === "skip") {
      out.push(["div.sl.skip", { key: "s" + i },
        `⋯ ${row.op.n} unchanged line${row.op.n === 1 ? "" : "s"}`]);
      continue;
    }
    const ctx = row.kind === "ctx";
    // In a context row both sides are the same op; in a change row either side
    // may be absent, and an absent side is a blank cell rather than a missing
    // one, so the two columns stay in step.
    const cell = (op, side) => {
      if (!op) return [["span.sl-no", { key: side + "n" }, ""],
                       ["span.sl-src.blank", { key: side + "s" }, ""]];
      const line = side === "l" ? op.a : op.b;
      const toks = side === "l" ? (op.a || op.b).toks : (op.b || op.a).toks;
      return [["span.sl-no", { key: side + "n" }, line ? String(line.no) : ""],
              ["span.sl-src", { key: side + "s" }, ...tokenSpans(toks, side + i + "_")]];
    };
    const lno = row.l && row.l.a && row.l.a.no;
    const rno = row.r && row.r.b && row.r.b.no;
    const lcls = (ctx ? "" : (row.l ? ".del" : ".none"))
      + (selMatches("a", lno) ? ".sel" : relMatches(PAIR_IN_VIEW, "a", lno));
    const rcls = (ctx ? "" : (row.r ? ".add" : ".none"))
      + (selMatches("b", rno) ? ".sel" : relMatches(PAIR_IN_VIEW, "b", rno));
    out.push(["div.sl", { key: "r" + i },
      ["div.sl-side" + lcls, { key: "L", onclick: () => selectLine("a", lno) }, ...cell(row.l, "l")],
      ["div.sl-side" + rcls, { key: "R", onclick: () => selectLine("b", rno) }, ...cell(row.r, "r")],
    ]);
  }
  return out;
}

// Comments are dropped by default — see diff.js for why that is not cosmetic
// (the C diff is 11% signal without it).
function diffBlock(pair, code, key) {
  const A = code[pair.a], B = code[pair.b];
  if (!A || !B) {
    return ["div.loading", { key: key },
      `This pattern has no ${!A ? RUNG_NAME[pair.a] : RUNG_NAME[pair.b]} rung, so this diff does not exist.`];
  }
  PAIR_IN_VIEW = pair;
  const mode = pair.sourceMode || "diff";
  const noDiff = mode !== "diff";
  const r = noDiff ? null : DIFF.diffRungs(A.text, SYNTAX.langFor(pair.a, A.lang),
    B.text, SYNTAX.langFor(pair.b, B.lang),
    { ignoreComments: !APP.diffComments, aFirst: A.first_line, bFirst: B.first_line });

  const split = effectiveLayout() === "split";
  const rows = mode === "single" ? sourceSingleRows(A, pair)
    : mode === "pair" ? (split ? sourceAlignedRows(A, B, pair) : sourcePairUnified(A, B, pair))
    : (split ? sourceSplitRows(r) : sourceUnifiedRows(r));

  return ["div", { key: key },
    ["div.diff-head", { key: "dh" },
      ["div.diff-stat", { key: "st" },
        ...(noDiff ? [] : [
          ["span.dstat.add", { key: "a" }, "+" + r.added],
          ["span.dstat.del", { key: "d" }, "−" + r.removed],
        ]),
        ["span.dstat.muted", { key: "m" },
          noDiff
            ? (mode === "single"
                ? `${RUNG_SHORT[pair.a]} vs ${RUNG_SHORT[pair.b]} · one source, two backends`
                : `${RUNG_SHORT[pair.a]} vs ${RUNG_SHORT[pair.b]} · two languages, shown side by side`)
            : `${RUNG_SHORT[pair.a]} → ${RUNG_SHORT[pair.b]} · comparing ${r.comparedLines.a} and ${r.comparedLines.b} lines`],
      ],
      ["div.diff-ctl", { key: "ctl" },
        ["div.seg", { key: "sw" },
          ["button" + (!APP.diffAsm ? ".on" : ""), {
            key: "s1", onclick: () => { APP.diffAsm = false; renderAll(); },
          }, "source"],
          ["button" + (APP.diffAsm ? ".on" : ""), {
            key: "s2", onclick: () => { APP.diffAsm = true; loadAsm(APP.patId); renderAll(); },
          }, "assembly"],
        ],
        ["div.seg", { key: "lay" },
          ...["split", "unified"].map(l => ["button" + (APP.diffLayout === l ? ".on" : ""), {
            key: "l" + l, onclick: () => { APP.diffLayout = l; renderAll(); },
          }, l]),
        ],
        APP.diffAsm
          ? ["div.seg", { key: "op" },
              ...["O3", "O0"].map(o => ["button" + (APP.diffOpt === o ? ".on" : ""), {
                key: "o" + o, onclick: () => { APP.diffOpt = o; renderAll(); },
              }, "-" + o]),
            ]
          : (noDiff
              ? ["span", { key: "tc" }, ""]     // nothing is being diffed to hide comments from
              : ["button.seg-btn" + (APP.diffComments ? ".on" : ""), {
                  key: "tc", onclick: () => { APP.diffComments = !APP.diffComments; renderAll(); },
                }, APP.diffComments ? "comments shown" : "comments hidden"]),
      ],
    ],
    // In the linked view the two panes are the point, so every paragraph between
    // them is height stolen from the thing the reader came for.  All of the
    // prose — what the pair isolates, the guarded notes, the mapping caveats —
    // folds behind one toggle, and what stays is a single line of counts.
    APP.diffAsm
      ? ["div", { key: "linked" },
          ["div.pane-head", { key: "ph0" },
            ["button.mini-btn" + (APP.diffNotes ? ".on" : ""), {
              key: "nb", onclick: () => { APP.diffNotes = !APP.diffNotes; renderAll(); },
            }, APP.diffNotes ? "▾ notes" : "▸ notes"],
            ["span.pane-lab", { key: "sl" }, mode === "single" ? "source (shared)" : "source"],
            alignLegend(pair),
          ],
          APP.diffNotes
            ? ["div.pane-notes", { key: "pn" },
                ["p.section-note", { key: "iso" }, ...md(pair.isolates)],
                diffNote(pair, "asmdiff"),
                ...asmProse(pair, APP.patId),
              ]
            : ["span", { key: "pn" }, ""],
          (!noDiff && r.identical)
            ? ["p.small.muted", { key: "same" },
                ...md(`Identical source at these two rungs${r.ignoredComments ? " once comments are set aside" : ""}.`)]
            : ["div.difflines.pane." + effectiveLayout(), { key: "sp" }, ...rows],
          asmDiffBlock(pair, APP.patId, "asm"),
        ]
      : ["div", { key: "srcv" },
          ["p.section-note", { key: "iso" }, ...md(pair.isolates)],
          diffNote(pair, "codediff"),
          (!noDiff && r.identical)
        ? ["div.callout.note", { key: "same" },
            ["div.callout-h", "These two rungs are the same source on this pattern."],
            ["p", ...md(`Nothing changes between ${RUNG_NAME[pair.a]} and ${RUNG_NAME[pair.b]} here${r.ignoredComments ? " once comments are set aside" : ""}. That is a result about this pattern, not a gap in the report — see the note above and the pattern's own write-up.`)],
          ]
            : ["div.difflines." + effectiveLayout(), { key: "dl" }, ...rows],
          ["div.code-meta", { key: "mf" }, `${A.file}   →   ${B.file}`],
        ],
  ];
}

// ---- the compiled kernels ---------------------------------------------------
// What the source diff above did to the machine code.  The text is NORMALISED
// (harness/asm.py): immediates and branch targets are erased, which is why an
// operand reads `$` and a jump reads `TGT`.  That makes it readable and makes it
// unusable as evidence — two kernels computing different answers have normalised
// identically before now — so the identity claim beside it cites `md5_fn`, which
// is what the gate decides on.

const IDENTITY_WORDS = {
  exact: ["identical machine code", "The kernel symbols are byte-for-byte the same."],
  norel: ["identical apart from link addresses",
    "The bytes differ only in pc-relative fields — a call to a callee that sits at a different address. Every instruction and register is the same. At `-O0` the Rust kernels still call `Iterator::next`, so this is a linking artefact and **not** a cost."],
  counts: ["same instruction count, different code", "Equal length, differing bytes."],
  differ: ["different machine code", ""],
};

function asmUnifiedRows(d, seen) {
  const rows = [];
  for (let i = 0; i < d.ops.length; i++) {
    const op = d.ops[i], k = op[0], text = op.slice(1);
    if (k === "@") {
      const n = +text;
      rows.push(["div.dl.skip", { key: "as" + i }, `⋯ ${n} unchanged instruction${n === 1 ? "" : "s"}`]);
      continue;
    }
    const on = asmSelMatches(d, i);
    const first = on && !seen.hit; if (on) seen.hit = true;
    rows.push(["div.dl.d" + (k === "+" ? "add" : k === "-" ? "del" : "ctx")
      + (on ? ".sel" : "") + confCls(d, i),
      Object.assign({ key: "ad" + i, onclick: () => asmClick(d, i) },
        first ? { id: "asm-sel" } : {}, asmTip(d, i)),
      ["span.dl-sign", { key: "s" }, k],
      ["span.dl-src", { key: "c" }, ...tokenSpans(SYNTAX.tokenizeAsm(text), "a" + i + "_")],
    ]);
  }
  return rows;
}

// Clicking an instruction selects the source line it came from — on whichever
// side that instruction exists.
function asmClick(d, i) {
  if (!d.map) return;
  const a = d.map.al[i], b = d.map.bl[i];
  if (a > 0) selectLine("a", a);
  else if (b > 0) selectLine("b", b);
}

// Instructions with no line, or a line in an inlined stdlib file, say so rather
// than silently doing nothing when clicked.
function asmTip(d, i) {
  if (!d.map) return {};
  const f = (d.map.fx || {})[String(i)];
  if (f) return tip("inlined from " + f);
  const a = d.map.al[i], b = d.map.bl[i];
  if (a > 0 || b > 0) {
    const parts = [];
    if (a > 0) parts.push("left: line " + a);
    if (b > 0) parts.push("right: line " + b);
    const c = a > 0 ? confOf(d, i, "a") : confOf(d, i, "b");
    if (c !== null) parts.push(CONF_NAME[c] + " — " + CONF_WHY[c]);
    return tip(parts.join("\n"));
  }
  return tip("no source line for this instruction");
}

function asmSplitRows(d, seen) {
  // splitRows() pairs the ops, but the map is indexed by op position, so the
  // original index travels with each op rather than being recomputed.
  const idx = new Map();
  d.ops.forEach((op, i) => { if (!idx.has(op)) idx.set(op, []); idx.get(op).push(i); });
  const take = (op) => (idx.get(op) || []).shift();
  const out = [];
  let i = 0;
  for (const row of DIFF.splitRows(d.ops, o => o[0])) {
    i++;
    if (row.kind === "skip") {
      const n = +row.op.slice(1);
      out.push(["div.sl.skip", { key: "as" + i },
        `⋯ ${n} unchanged instruction${n === 1 ? "" : "s"}`]);
      continue;
    }
    const ctx = row.kind === "ctx";
    const li = row.l === null ? -1 : take(row.l);
    const ri = ctx ? li : (row.r === null ? -1 : take(row.r));
    const cell = (op, side) => op
      ? [["span.sl-src", { key: side + "s" }, ...tokenSpans(SYNTAX.tokenizeAsm(op.slice(1)), side + i + "_")]]
      : [["span.sl-src.blank", { key: side + "s" }, ""]];
    const lon = li >= 0 && asmSelMatches(d, li);
    const ron = ri >= 0 && asmSelMatches(d, ri);
    const firstL = lon && !seen.hit; if (lon) seen.hit = true;
    const firstR = !firstL && ron && !seen.hit; if (ron) seen.hit = true;
    const lcls = (ctx ? "" : (row.l ? ".del" : ".none")) + (lon ? ".sel" : "")
      + (li >= 0 ? confCls(d, li) : "");
    const rcls = (ctx ? "" : (row.r ? ".add" : ".none")) + (ron ? ".sel" : "")
      + (ri >= 0 ? confCls(d, ri) : "");
    out.push(["div.sl.noline", { key: "r" + i },
      ["div.sl-side" + lcls,
        Object.assign({ key: "L", onclick: () => li >= 0 && asmClick(d, li) },
          firstL ? { id: "asm-sel" } : {}, li >= 0 ? asmTip(d, li) : {}),
        ...cell(row.l, "l")],
      ["div.sl-side" + rcls,
        Object.assign({ key: "R", onclick: () => ri >= 0 && asmClick(d, ri) },
          firstR ? { id: "asm-sel" } : {}, ri >= 0 ? asmTip(d, ri) : {}),
        ...cell(row.r, "r")],
    ]);
  }
  return out;
}

function asmDiffBlock(pair, pid, key) {
  const rec = CACHE.asm[pid];
  if (rec === "loading" || rec === undefined) { loadAsm(pid); return ["div.loading", { key: key }, "Loading assembly…"]; }
  if (rec.absent || !rec.pairs) {
    return ["div.callout.warn", { key: key },
      ["div.callout-h", "No cached assembly for this pattern."],
      ["p", ...md("The disassembly is extracted from the built binaries, which are scratch and are not committed. Run `harness/build.py` for this pattern, then `python3 insights/asm_extract.py`.")]];
  }

  const blocks = [];
  const seen = { hit: false };     // only the first matching row gets #asm-sel
  for (const aid of (pair.asm || [])) {
    const byOpt = rec.pairs[aid];
    if (!byOpt) continue;
    const d = byOpt[APP.diffOpt] || byOpt.O3;
    if (!d) continue;
    const [word, gloss] = IDENTITY_WORDS[d.identity_level] || IDENTITY_WORDS.differ;

    // ops are compact: first char is the kind, the rest is the text (or, for
    // "@", the count of instructions skipped)
    const rows = effectiveLayout() === "split" ? asmSplitRows(d, seen) : asmUnifiedRows(d, seen);

    blocks.push(["div.asmpair", { key: "ap" + aid },
      ["div.asm-head", { key: "ah" },
        // The rung name leads, because the C symbols are both literally
        // `kernel` and the gcc block would otherwise be indistinguishable from
        // the clang one.
        ["div.asm-sym", { key: "sy" },
          ["b", { key: "l" }, `${RUNG_NAME[d.a.cell]} → ${RUNG_NAME[d.b.cell]}`],
          ["span.asm-symnames", { key: "s" },
            ["code", { key: "a" }, d.a.symbol], " → ", ["code", { key: "b" }, d.b.symbol]]],
        ["div.asm-stat", { key: "st" },
          ["span.dstat.muted", { key: "n" }, `${d.a.n_fn} → ${d.b.n_fn} instructions`],
          ["span.chip." + (d.identity_level === "exact" ? "good" : "neutral"), { key: "lv" }, word],
        ],
      ],
      gloss ? ["p.small.muted.mt0", { key: "gl" }, ...md(gloss)] : ["span", { key: "gl" }, ""],
      d.ops.length && (d.added || d.removed)
        ? ["div.difflines.asm." + effectiveLayout(), { key: "dl" }, ...rows]
        : ["p.small.muted", { key: "nd" }, ...md("**No instruction differs.** " +
            (d.identity_level === "exact"
              ? "Everything the source diff added compiles to nothing at all."
              : "The normalised instruction streams are the same; see the note above."))],
      ["div.code-meta", { key: "md" }, `md5(fn) ${d.a.md5_fn.slice(0, 12)} → ${d.b.md5_fn.slice(0, 12)}`],
    ]);
  }

  if (!blocks.length) {
    return ["div.callout.warn", { key: key },
      ["div.callout-h", "This diff has no cached assembly."],
      ["p", ...md("Either the rung is missing on this pattern, or its digests no longer match `results/` and the build withheld it — the Method tab will say which.")]];
  }

  // Coverage is reported rather than implied: at -O3 a good fraction of the
  // instructions come from inlined library code and have no line in the source
  // shown above, and a reader clicking one deserves to know why nothing happens.
  let own = 0, foreign = 0, none = 0, mapped = false;
  const tiers = [0, 0, 0];
  let anyPartial = false;
  for (const aid of (pair.asm || [])) {
    const bo = rec.pairs[aid]; const dd = bo && (bo[APP.diffOpt] || bo.O3);
    if (!dd || !dd.map) continue;
    mapped = true;
    if (dd.map_level === "partial") anyPartial = true;
    for (let i = 0; i < dd.ops.length; i++) {
      if (dd.ops[i][0] === "@") continue;
      const a = dd.map.al[i], b = dd.map.bl[i];
      if (a > 0 || b > 0) {
        own++;
        const c = a > 0 ? dd.map.ac[i] : dd.map.bc[i];
        tiers[c === undefined ? CONF_CERTAIN : c]++;
      } else if (a === -1 || b === -1) foreign++;
      else none++;
    }
  }
  const total = own + foreign + none;

  // One line, always visible: the label, and the counts a reader needs in order
  // to know whether clicking will do anything.  Everything else is prose and
  // lives in the fold above — see asmProse().
  return ["div", { key: key },
    ["div.pane-head", { key: "ph" },
      ["span.pane-lab", { key: "l" }, "compiled kernel"],
      mapped
        ? ["span.pane-stats", { key: "s" },
            ["span.pstat.on", { key: "m" }, `${own}/${total} mapped`],
            // the tiers, and only the ones that exist — a badge reading "0
            // approximate" is noise
            ...(tiers[CONF_CERTAIN] ? [["span.pstat.tc", { key: "c" },
              `${tiers[CONF_CERTAIN]} certain`]] : []),
            ...(tiers[CONF_LIKELY] ? [["span.pstat.tl", { key: "l" },
              `${tiers[CONF_LIKELY]} likely`]] : []),
            ...(tiers[CONF_APPROX] ? [["span.pstat.ta", { key: "a" },
              `${tiers[CONF_APPROX]} approx`]] : []),
            ...(foreign ? [["span.pstat", { key: "f" }, `${foreign} inlined`]] : []),
            ...(none ? [["span.pstat", { key: "n" }, `${none} no line`]] : []),
          ]
        : ["span.pane-stats", { key: "s" },
            ["span.pstat.off", { key: "m" }, "no source mapping here"]],
      ["span.pane-hint", { key: "h" },
        mapped ? "click a line, or an instruction" : "see notes"],
    ],
    ...blocks,
  ];
}

// When a line is selected, say what the green on the other side means — it is
// inferred from the compiled code, not read off the source, and a reader has no
// way to know that from the colour alone.
function alignLegend(pair) {
  const s = APP.linkSel;
  if (!s || (pair.sourceMode || "diff") === "single") return ["span", { key: "al" }, ""];
  const r = relatedFor(pair, APP.patId, s.side, s.line);
  const n = r.strong.size;
  if (!n) {
    const all = allRelated(pair, APP.patId);
    const col = s.side === "a" ? 0 : 1;
    const others = [...new Set(all.map(p => p[col]))];
    return ["span.align-leg.none", { key: "al" },
      others.length
        ? `line ${s.line} shares no instruction with the other side — ${others.length} line(s) here do: ${others.slice(0, 8).join(", ")}${others.length > 8 ? "…" : ""}`
        : `no line in this pair shares an instruction with the other side`];
  }
  return ["span.align-leg", { key: "al" },
    ["span.rel-key", { key: "k" }, ""],
    `line ${s.line} → ${[...r.strong].join(", ")} · lines whose instructions are identical in both kernels`,
  ];
}

// The prose that used to sit between the two panes.  It is all still true and
// still worth reading once; it is just not worth 6 lines of viewport every time
// somebody wants to see a source line next to its instructions.
function asmProse(pair, pid) {
  const rec = CACHE.asm[pid];
  const has = rec && rec.pairs && (pair.asm || []).some(aid => {
    const bo = rec.pairs[aid]; const dd = bo && (bo[APP.diffOpt] || bo.O3);
    return dd && dd.map;
  });
  return [
    has
      ? ["div", { key: "lh" },
          ["p.small.muted", { key: "a" }, ...md("**Click a line in the source pane** to light up the instructions it compiled to, or click an instruction to find its line. Optimised code is scheduled, so one line's instructions are scattered rather than contiguous, and some come from inlined library code — hover an instruction for its origin.")],
          ["p.small.muted", { key: "b" }, ...md("**Where the line numbers come from, and what each is worth.** The measured binaries carry no line information for this project's code at all, so the line table is taken from a throwaway debug twin — the *assembly shown is still the measured binary's*, only the line numbers are the twin's. `-g` is meant not to change codegen and for C it does not, but for Rust it can, so the twin is aligned against the measured kernel instruction by instruction and every line is graded:")],
          ["div.conf-legend", { key: "c" },
            ["div.conf-row", { key: "r2" }, ["span.conf-key.k-certain", { key: "k" }, ""],
              ["b", { key: "n" }, "certain"], ["span", { key: "w" }, " — " + CONF_WHY[2]]],
            ["div.conf-row", { key: "r1" }, ["span.conf-key.k-likely", { key: "k" }, ""],
              ["b", { key: "n" }, "likely"], ["span", { key: "w" }, " — " + CONF_WHY[1]]],
            ["div.conf-row", { key: "r0" }, ["span.conf-key.k-approx", { key: "k" }, ""],
              ["b", { key: "n" }, "approximate"], ["span", { key: "w" }, " — " + CONF_WHY[0]]],
          ],
          ["p.small.muted", { key: "d" }, ...md("A twin sharing less than half the measured instruction stream is refused outright: that is a different program, not a variant. **The source-to-source alignment counts only certain and likely instructions** — two positional guesses do not make a correspondence.")],
        ]
      : ["p.small.muted", { key: "lh" }, ...md("**No source mapping for this pair.** The line table comes from a debug twin, and a twin is only believed once it compiles to the *same instructions* as the measured binary — same count, same normalised text, matching `md5_fn_norel`. Where it does not, usually at `-O0` but sometimes at `-O3` where register allocation shifts, no mapping is offered rather than a wrong one.")],
    ["p.small.muted", { key: "cav" }, ...md("Kernel symbol only, `isolated` builds — at `whole` the kernel is inlined into the driver and has no symbol to disassemble. **The text is normalised for reading**: immediates show as `$` and branch targets as `TGT`, because two kernels that compute different answers can normalise the same. Identity is decided by `md5(fn)`, printed under each block.")],
  ];
}

// The script-guarded note for whichever view is showing — insight_codediff.py
// for the source diff, insight_asmdiff.py for the compiled one.  Absent means
// either that no note was written or that its guards stopped holding and the
// build withheld it; both are correct outcomes and neither is an error here.
function diffNote(pair, which) {
  const ins = (APP.data || {}).insights || {};
  const notes = ((ins[which] || {})[APP.patId] || {})[pair.id];
  if (!notes || !notes.length) return ["span", { key: "nn" }, ""];
  return ["div.stack", { key: "notes" },
    ...notes.map((note, n) => ["div.callout.note", { key: "note" + n },
      ["div.callout-h", note.title],
      ...(note.body || []).map((b, i) => ["p", { key: "b" + i }, ...md(b)]),
    ]),
  ];
}

function provenanceTable() {
  const d = APP.data;
  const tc = d.toolchain || {}, h = d.host || {};
  const t = d.totals || {};
  const np = t.patterns_not_passing || [];
  // patterns that passed WITH blocked rows — a disclosed gap, worth naming
  const blocked = (d.patterns || []).filter(p => p.blocked)
    .map(p => ({ id: p.id, what: p.blocked + " blocked row" + (p.blocked === 1 ? "" : "s") }));
  const rows = [
    // Every count on this site pools all patterns, so which of them the gate
    // actually passed is provenance, not a detail.
    // "33 of 33 passed" pooled three PASS-WITH-BLOCKED-ROWS rows in silence.
    // Blocked rows are disclosed gaps, not clerical ones — p35's are three
    // trusted items with no verified twin — so the split belongs here.
    ["gate", (np.length
      ? `${t.patterns_passing} of ${t.patterns} passed · ${np.map(n => `${n.id} (${n.verdict}, ${n.failures} failure(s))`).join(", ")} — pooled into every total here`
      : `${t.patterns_passing || t.patterns} of ${t.patterns} passed`)
      + (blocked.length
          ? ` · ${t.patterns - blocked.length} clean, ${blocked.length} with disclosed blocked rows (${blocked.map(b => pid(b.id) + ": " + b.what).join("; ")})`
          : "")],
    ["gcc", tc.gcc || "—"],
    ["clang", (tc.clang || "").split(" (")[0] || "—"],
    ["rustc", `${tc.rustc || "—"} · ${tc.rustc_llvm || ""}`],
    // ⚠ The first line of this block is a local filesystem path, not a version.
    // Every pin-specific claim on the Proof tab is a claim about THIS build, so
    // the version is the thing a reader needs — and the author's home directory
    // is not something to publish.
    ["Verus", (/Version:\s*(\S+)/.exec(tc.verus || "") || [])[1] || "—"],
    ["valgrind / objdump", `${tc.valgrind || "—"} · ${tc.objdump || "—"}`],
    ["host", `${h.cpu_model || "—"} · governor ${h.governor || "?"}`],
    ["git HEAD when built", `${(d.head || {}).short || "—"} — ${(d.head || {}).subject || ""}`],
    ["site data built", d.built_utc],
  ];
  return dataTable(["", ""], rows, "prov", { wrap: [1] });
}

// ------------------------------------------------- rebuilding data in place --
// index.stdio.py re-runs build_data.py, which writes only under .web/.  If the
// page is served statically with no backend, this degrades to a toast.

const STDIO = "./index.stdio.py";

async function rpcCall(method, params) {
  const res = await fetch(STDIO, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ kind: "JSON_LIST", data: [{ jsonrpc: "2.0", id: method, method, params: params || {} }] }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const env = await res.json();
  if (!env || !Array.isArray(env.data) || !env.data[0]) throw new Error("bad envelope");
  if (env.data[0].error) throw new Error(env.data[0].error.message);
  return env.data[0].result;
}

async function checkAndRebuild() {
  let st;
  try {
    st = await rpcCall("status");
  } catch (e) {
    UI.toast_error("No backend here — rebuild with: python3 .web/build_data.py");
    return;
  }
  const msg = st.fresh
    ? `data/ is up to date with the evidence files.\n\nbuilt   ${st.built_utc}\nnewest  ${st.newest_evidence.file}\n\nRebuild anyway?`
    : `data/ is STALE.\n\nbuilt   ${st.built_utc}\nnewer   ${st.newest_evidence.file}\n\nRe-run build_data.py now? It writes only under .web/.`;
  const r = await _sc.show({
    title: st.fresh ? "Data is current" : "Data is stale",
    message: msg,
    confirmLabel: "Rebuild",
    confirmCls: st.fresh ? ".sc-teal" : ".sc-green",
  });
  if (!r.confirmed) return;
  UI.toast_info("Rebuilding…");
  try {
    const out = await rpcCall("rebuild");
    if (!out.ok) { UI.toast_error("build_data.py failed — see stderr in the console"); console.error(out.stderr); return; }
    UI.toast_success(`Rebuilt in ${out.seconds}s — reloading`);
    setTimeout(() => location.reload(), 700);
  } catch (e) {
    UI.toast_error(String(e.message || e));
  }
}

function footer() {
  const d = APP.data || {};
  return ["div.footer", { key: "footer" },
    ["p", { key: "built" },
      ...md(`Data built **${d.built_utc || "—"}** from git \`${(d.head || {}).short || "—"}\`. `),
      ["button.icon-btn", { key: "rb", onclick: checkAndRebuild }, "check / rebuild"],
    ],
    ["p", ...md(`Built from \`results/\` and \`results/gate/\` by \`.web/build_data.py\`. ` +
      `Rebuild with \`python3 .web/build_data.py\`. This directory is gitignored and nothing under it writes outside \`.web/\`.`)],
    ["p", ...md(`Interpretive text is hand-written in \`.web/content.js\` from \`RECAP.md\`, \`.memory/\` and each pattern's \`NOTES.md\`; every number is generated.`)],
  ];
}

// ------------------------------------------------------------------ ladder --

function viewLadder() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const d = APP.data;
  const inp = APP.ladderInput;

  return ["div", { key: "ld" },
    ["div.eyebrow", "the six rungs"],
    ["h1", "Between “C” and “proved safe” there are four other places to stand"],
    ["p.lede", ...md("The binary reading of security — safe or unsafe — hides the fact that each of these rungs buys a *different* thing, at a different price, with a different amount of trust left over. This is what the ladder is for.")],

    ["div.section", { key: "cards" },
      ["div.grid.g2",
        ...LADDER.map(r => ["div.card.rung-card", { key: "L" + r.rung, style: `--step:${rungStripe(r)}` },
          ["div.row-between",
            ["div",
              ["div.rung-id", r.rung + " · " + r.lang],
              ["h3", { key: "h" }, r.title],
            ],
            ["span.inline-list", { key: "cells" },
              ...r.cells.map(c => ["span.chip.tag", { key: "c" + c },
                ["span.legend-key" + sw(c), { style: "width:9px;height:9px;border-radius:2px" }], c]),
            ],
          ],
          ["p.small", { key: "line" }, ...md(r.line)],
          ["p.small.muted", { key: "body" }, ...md(r.body)],
          ["div.rung-meta",
            ["b", "guarantee: "], r.guarantee, ["br"],
            ["b", "trusted base: "], r.tcb,
          ],
        ]),
      ],
    ],

    ["div.section", { key: "wall" },
      ["h2", "One profile per pattern"],
      ["p.section-note", ...md("Executed instructions per kernel call at `-O3`, isolated build — the marginal (whole-program slope) column. **Each bar wears its rung's colour: C cool, Rust warm — and within a pair the washed-out bar is the plain rung, the solid one the hardened, tuned or proven twin.** Pick a preset or click any key below to drop a rung from every profile; each chart rescales to the rungs left in it, and a hidden rung never repaints the others. Click a pattern to open it.")],
      ["div.filters", { key: "f" },
        ["div.field",
          ["span.field-label", "Input"],
          ["div.seg",
            ...["small.bin", "large.bin"].map(i => ["button" + (inp === i ? ".on" : ""),
              { key: "i" + i, onclick: () => { APP.ladderInput = i; renderAll(); } }, i.replace(".bin", "")]),
          ],
        ],
        rungPresets("wall-pre"),
        ["div.field", { key: "tog", style: "flex-basis:100%" },
          ["span.field-label", `rungs, top → bottom — click a key to hide it (${APP.rungs.size} of ${RUNG_ORDER.length} shown)`],
          rungLegend(RUNG_ORDER, { short: false, key: "wall-lg" }),
        ],
      ],
      ["div.sm-grid",
        ...d.patterns.map(p => {
          const sel = (p.tax || {})[`isolated/${inp}`];
          if (!sel) return ["div", { key: "sm" + p.id }, ""];
          const items = visibleRungs(sel.cells).map(c => ({
            label: RUNG_SHORT[c],
            cell: c,
            value: sel.cells[c].ir,
            tip: `${pid(p.id)} · ${RUNG_NAME[c]}\n${fmt(sel.cells[c].ir)} Ir/call\n${sfmt(sel.cells[c].delta)} vs unsafe Rust`,
          }));
          return ["div.sm", { key: "sm" + p.id, onclick: () => go("patterns", p.id) },
            ["div.sm-h",
              ["span.sm-t", pid(p.id)],
              ["span.sm-s", pshort(p.id)],
            ],
            items.length
              ? barsChart(items, { small: true, key: "c" + p.id })
              : ["div.loading", { key: "none" }, "no selected rung on this pattern"],
          ];
        }),
      ],
      ["p.small.muted.mt16", ...md("**Colour is the rung, everywhere on this site.** C is cool — gcc cyan, clang blue; Rust is warm — safe amber, unsafe red. Each pair is *one* hue at two strengths: the washed bar is the plain rung and the solid bar is the same rung with the check, the tuning or the proof added. So a washed amber bar is R2 — the rung most reports publish as “what safe Rust costs”, which on p16 is ~75× the honest figure — and the solid amber beneath it is the same program written to let the optimiser hoist. p01 models no bug, so it has no hardened-C rung and its last bar is the R2v control.")],
    ],
    footer(),
  ];
}

// -------------------------------------------------------------------- cost --

// May this rung-to-rung difference be taken at all?
//
// The published Ir column counts instructions INSIDE the kernel symbol. Two
// cells may only be subtracted when they dispatch the same work outside it —
// otherwise the difference is between two different programs. `synthesis/`
// decides that from disassembly and publishes a verdict per row; build_data.py
// parses those verdicts rather than recomputing them.
//
// ⚠ A MISSING VERDICT IS NOT A GRANTED ONE. When the table cannot be read, the
// licence map is empty and `licOk` returns false, so every row is marked and
// the reader is told the check is unavailable — never silently waved through.
const LIC_WHY = {
  "NOT-LIC": "NOT LICENSED — the two rungs call different things outside the kernel symbol, so this difference is between two different programs and is known to be wrong.",
  "UNDEC": "UNDECIDABLE — both rungs dispatch through a pointer the disassembler cannot resolve, so the check could not be run.",
  "NO-KSYM": "NO KERNEL SYMBOL — a rung was inlined away, so there is no column to compare.",
  "NOT-BUILT": "NOT BUILT — the binary is absent. A tooling state, not a property of the pattern.",
};
const licMap = () => ((APP.data || {}).licence || {});
const licTag = (pair, id) => (licMap()[pair] || {})[id];
const licOk = (pair, id) => licTag(pair, id) === "LICENSED";
const licWhy = (pair, id) => {
  const t = licTag(pair, id);
  if (!t) return "The licence check could not be read for this row — treat the difference as unverified.";
  return LIC_WHY[t] || t;
};
// every pattern in `pair` whose difference the research does not license
const licBad = (pair) => Object.keys(licMap()[pair] || {})
  .filter(id => licMap()[pair][id] !== "LICENSED").sort();

// How hard each side of a comparison was searched for a cheaper spelling. The
// research publishes this per row and it is the qualification that decides
// whether a bar is a safety cost or an artefact of which code was chosen.
const searchState = (id) => ((licMap()._search || {})[id] || "")
  .replace(/[*`⚠]/g, "").replace(/\s+/g, " ").trim();

// C -> hardened C. The research does not tabulate this pair, so build_data.py
// applies the same rule to the same disassembly and says so on the page.
const licCRec = (id, cell) => (((APP.data || {}).licence_c || {})[id.slice(0, 3)] || {})[cell];
const licCOk = (id, cell) => (licCRec(id, cell) || {}).tag === "LICENSED";
const licCWhy = (id, cell) => {
  const r = licCRec(id, cell);
  if (!r) return "the licence check could not be read for this row";
  return r.why || LIC_WHY[r.tag] || r.tag;
};

// The disclosure that belongs next to every difference on this page: how many
// of them the research does NOT permit, which ones, and why. Folded, because it
// is a qualification rather than a headline — but the marker on each affected
// row is not folded, so a reader cannot miss that a row is marked.
function licenceNote() {
  const L = licMap();
  const pairs = Object.keys(L);
  if (!pairs.length) {
    return ["div.section", { key: "lic" },
      callout("warn", "The licence check could not be read",
        [LICENCE.missing])];
  }
  const LABEL = {
    "R2-R4": "safe Rust naive − unsafe Rust",
    "R3-R4": "safe Rust tuned − unsafe Rust",
    "R5-R4": "proved − unsafe Rust",
    "gcc-clang": "C on gcc − C on clang",
  };
  const rows = pairs.map(pair => {
    const bad = licBad(pair);
    const n = Object.keys(L[pair]).length;
    return [pair, LABEL[pair] || pair, `${n - bad.length} / ${n}`,
      { jsonml: ["span.small.muted", bad.length ? bad.map(pid).join(", ") : "—"] }];
  });
  // the C -> hardened C rows, which the research does not tabulate
  const C = (APP.data || {}).licence_c || {};
  const cRows = [];
  Object.keys(C).sort().forEach(short => Object.keys(C[short]).sort().forEach(cell => {
    const r = C[short][cell];
    if (r.tag === "LICENSED") return;
    const full = (APP.data.patterns.find(p => p.id.startsWith(short)) || {}).id || short;
    cRows.push([pid(full), cell.replace("-h", " hardened"), r.tag,
      { jsonml: ["span.small.muted", r.why || LIC_WHY[r.tag] || ""] }]);
  }));
  const cAll = Object.keys(C).reduce((a, k) => a + Object.keys(C[k]).length, 0);
  const total = pairs.reduce((a, p) => a + licBad(p).length, 0) + cRows.length;
  const all = pairs.reduce((a, p) => a + Object.keys(L[p]).length, 0) + cAll;
  return ["div.section", { key: "lic" },
    ["details.fold", { key: "licfold" },
      ["summary", `⚠ ${total} of ${all} rung-to-rung differences on this page are NOT licensed for subtraction — what that means`],
      ["div.fold-body",
        ["div.prose", ...LICENCE.body.map((b, i) => mdP(b, "l" + i))],
        dataTable(["pair", "what it compares", "licensed", "rows that are not"],
          rows, "lictbl", { wrap: [3] }),
        cRows.length ? ["div", { key: "chard" },
          ["h3.mt28", "C against hardened C"],
          ["p.small.muted", ...md(LICENCE.cnote)],
          dataTable(["pattern", "build", "verdict", "why"], cRows, "liccbl", { wrap: [3] }),
        ] : ["div", { key: "nochard" }, ""],
        ["p.small.muted.mt8", ...md(LICENCE.foot)],
      ],
    ],
    searchFold(),
  ];
}

// Every row's spelling-search state, verbatim from the research. This is the
// qualification that decides whether a safe-vs-unsafe bar is a safety cost or
// an artefact of which two programs were chosen, and it belongs on the page
// rather than compressed into a hand-typed clause.
function searchFold() {
  const S = (licMap() || {})._search || {};
  const ids = Object.keys(S).sort();
  if (!ids.length) return ["div", { key: "nosearch" }, ""];
  return ["details.fold.mt16", { key: "searchfold" },
    ["summary", `How hard was each side searched for a cheaper spelling? — all ${ids.length} patterns`],
    ["div.fold-body",
      ["div.prose", ...SEARCH.body.map((b, i) => mdP(b, "s" + i))],
      dataTable(["pattern", "search state, as published"],
        ids.map(id => [pid(id), { jsonml: ["span.small", searchState(id)] }]),
        "searchtbl", { wrap: [1] }),
    ],
  ];
}

function viewCost() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const d = APP.data, c = APP.cost;
  const pats = d.patterns;
  const inpShort = c.input.replace(".bin", "");

  const metricNote = c.metric === "marginal"
    ? "Marginal Ir per call — a whole-program slope, so it is independent of which symbol the work landed in."
    : "Kernel-exclusive Ir per call — instructions inside the kernel symbol only, isolated builds. Right only where every rung does its own work inside its own symbol.";

  const rows3 = pats.map(p => ({
    name: prow(p.id) + (licOk("R3-R4", p.id) ? "" : " ‡"),
    value: costRatioPct(p, "safe_tuned"),
    tip: `${pid(p.id)} — ${pname(p.id)}\nR3 safe tuned: ${fmt((costSel(p) || { cells: {} }).cells.safe_tuned && costSel(p).cells.safe_tuned.ir)} Ir/call\nR4 unsafe:     ${fmt((costSel(p) || {}).base)} Ir/call\ndelta ${sfmt(costDelta(p, "safe_tuned"))} = ${pctf(costRatioPct(p, "safe_tuned"))}`
      + (licOk("R3-R4", p.id) ? "" : `\n\n‡ ${licWhy("R3-R4", p.id)}`)
      // How hard each side was searched for a cheaper spelling decides whether
      // this bar means anything at all. The research publishes it per row; the
      // page used to compress all 33 of these into a hand-typed "on four
      // patterns", which was both unattributed and un-derived.
      + (searchState(p.id) ? `\n\nsearch state: ${searchState(p.id)}` : ""),
    onclick: () => go("patterns", p.id),
  }));

  // ⚠ This chart plots BOTH R2−R4 and R3−R4, so it needs both licences. It
  // shipped unmarked while the chart directly above it marked the same rows —
  // the page said "its difference is known to be wrong" and then printed the
  // same row clean two inches lower.
  const rowsDumb = pats.map(p => {
    const ok2 = licOk("R2-R4", p.id), ok3 = licOk("R3-R4", p.id);
    return {
      name: prow(p.id) + (ok2 && ok3 ? "" : " ‡"),
      a: costRatioPct(p, "safe_tuned"),
      b: costRatioPct(p, "safe_naive"),
      tip: `${pid(p.id)} — ${pname(p.id)}`
        + (ok3 ? "" : `\n\n‡ R3 − R4: ${licWhy("R3-R4", p.id)}`)
        + (ok2 ? "" : `\n\n‡ R2 − R4: ${licWhy("R2-R4", p.id)}`),
    };
  });
  const badDumb = pats.filter(p => !(licOk("R2-R4", p.id) && licOk("R3-R4", p.id)));

  const rowsC = pats.filter(p => costDelta(p, "c-clang-h") !== null).map(p => {
    const sel = costSel(p);
    const r1 = sel.cells["c-clang"], r1h = sel.cells["c-clang-h"];
    const g1 = sel.cells["c-gcc"], g1h = sel.cells["c-gcc-h"];
    // ⚠ This chart had NO licence check on it, and it is the site's cleanest
    // comparison — so it was the easiest place to be quietly wrong. p47's C
    // rung calls `memcmp` where its hardened rung inlines the comparison, so
    // the largest bar here was a libc call leaving the kernel symbol, not the
    // price of a check.
    const okC = licCOk(p.id, "c-clang-h"), okG = licCOk(p.id, "c-gcc-h");
    return {
      name: prow(p.id) + (okC && okG ? "" : " ‡"),
      a: r1 && r1h ? ((r1h.ir - r1.ir) / r1.ir) * 100 : null,
      b: g1 && g1h ? ((g1h.ir - g1.ir) / g1.ir) * 100 : null,
      tip: `${pid(p.id)} — ${pname(p.id)}`
        + (okC ? "" : `\n\n‡ clang: ${licCWhy(p.id, "c-clang-h")}`)
        + (okG ? "" : `\n\n‡ gcc: ${licCWhy(p.id, "c-gcc-h")}`),
    };
  });
  const badC = pats.filter(p => !(licCOk(p.id, "c-clang-h") && licCOk(p.id, "c-gcc-h")));

  // where the two build modes disagree about the sign of R3 − R4
  const flips = c.metric === "marginal" ? pats.filter(p => {
    const a = (p.tax || {})["isolated/" + c.input], b = (p.tax || {})["whole/" + c.input];
    if (!a || !b || !a.cells.safe_tuned || !b.cells.safe_tuned) return false;
    return Math.sign(a.cells.safe_tuned.delta) !== Math.sign(b.cells.safe_tuned.delta);
  }) : [];

  const costCols = RUNG_ORDER.slice(0, 8).filter(rungOn);
  // ⚠ Same rule as the charts: a cell whose difference is not licensed must
  // not print as a bare number here either. The pair each rung belongs to:
  const LIC_PAIR = { safe_naive: "R2-R4", safe_tuned: "R3-R4", verus: "R5-R4" };
  const full = pats.map(p => {
    const sel = costSel(p) || { base: null, cells: {} };
    const anyBad = costCols.some(c => LIC_PAIR[c] && !licOk(LIC_PAIR[c], p.id));
    return [pid(p.id) + (anyBad ? " ‡" : "")].concat(costCols.map(cell => {
      const v = sel.cells[cell];
      const pair = LIC_PAIR[cell];
      const bad = pair && !licOk(pair, p.id);
      return v ? { text: sfmt(v.delta) + (bad ? " ‡" : ""), cls: cls(v.delta) } : "—";
    })).concat([fmt(sel.base)]);
  });

  return ["div", { key: "cost" },
    ["div.eyebrow", "the price side of the trade"],
    ["h1", "What safety costs, per kernel call"],
    ["p.lede", ...md("Everything below is a **difference against unsafe Rust (R4)** — the rung with C's machine code and C's obligations. Positive means the safer rung executes more instructions. The unit is **`Ir`: one executed machine instruction**, counted exactly rather than timed, so the same input gives the same number every run. Executed-instruction counts are deterministic on this box; wall clock is a sanity check and is reported per pattern — the one exception on this page is the layout control at the foot, which is wall clock and exists to show why.")],

    ["div.filters.mt16", { key: "filters" },
      ["div.field",
        ["span.field-label", "Metric"],
        ["div.seg",
          ...[["marginal", "marginal Ir/call"], ["kernel", "kernel Ir/call"]].map(([k, l]) =>
            ["button" + (c.metric === k ? ".on" : ""), { key: "m" + k, onclick: () => { c.metric = k; renderAll(); } }, l]),
        ],
      ],
      ["div.field",
        ["span.field-label", "Build"],
        ["div.seg",
          ...[["isolated", "isolated"], ["whole", "whole-program"]].map(([k, l]) =>
            ["button" + (c.mode === k ? ".on" : "") + (c.metric === "kernel" && k === "whole" ? ".off" : ""),
              { key: "b" + k, disabled: (c.metric === "kernel" && k === "whole") ? true : undefined,
                onclick: () => { c.mode = k; renderAll(); } }, l]),
        ],
      ],
      ["div.field",
        ["span.field-label", "Input"],
        ["div.seg",
          ...["small.bin", "large.bin"].map(i => ["button" + (c.input === i ? ".on" : ""),
            { key: "i" + i, onclick: () => { c.input = i; renderAll(); } }, i.replace(".bin", "")]),
        ],
      ],
      ["div.field", { key: "note" },
        ["span.field-label", "what this column is"],
        ["span.small.muted", { style: "max-width:46ch;display:block" }, metricNote],
      ],
      rungPresets("cost-pre"),
      ["div.field", { key: "tog", style: "flex-basis:100%" },
        ["span.field-label", "rungs in the table below — click a key to hide it"],
        rungLegend(RUNG_ORDER.slice(0, 8), { key: "cost-lg" }),
      ],
    ],

    ["div.stack", { key: "charts" },
      chartDiverging({
        key: "r3",
        title: "Idiomatic safe Rust (R3) against unsafe Rust (R4)",
        sub: `Per kernel call, ${c.metric === "kernel" ? "kernel-exclusive" : "marginal"} Ir, \`-O3\`, ${c.metric === "kernel" ? "isolated" : c.mode} build, \`${c.input}\`. **Both rungs are the same program; only the spelling and the checks differ.**`,
        rows: rows3,
        valueFmt: (v) => pctf(v),
        posSw: sw("safe_tuned"), negSw: sw("unsafe"),
        posLabel: "R3 safe tuned is dearer",
        negLabel: "R4 unsafe is dearer",
        foot: "A negative bar is not “safe Rust is faster”. It is one *declared spelling* of the safe rung beating one declared spelling of the unsafe rung. ⚠ **The unsafe rung is held fixed on every pattern, not minimised** — the project forbids re-shipping a rung because a cheaper spelling was found, so every bar here is measured against an unsafe side that may be above its floor. On four rows a cheaper admissible unsafe spelling has actually been measured, and three of those four leave their bucket. **How hard each side was searched is published per pattern** — hover any bar to read that row's search state, or open the fold below for all of them. Click a bar for the pattern's own account.",
        tableHead: ["pattern", "R3 − R4"],
      }),

      chartDumbbell({
        key: "spell",
        title: "The spelling gap dwarfs the safety gap",
        sub: "Same language, same guarantee, same input: **R3 is safe Rust written to let the optimiser hoist; R2 is safe Rust written the obvious way.** Publishing R2 alone as “the cost of safe Rust” is the single most common way this benchmark could have been wrong."
          + (badDumb.length ? ` ⚠ **${badDumb.length} rows are marked ‡** — one or both of their differences is not licensed for subtraction.` : ""),
        rows: rowsDumb,
        aLabel: "R3 safe tuned", bLabel: "R2 safe naive",
        aSw: sw("safe_tuned"), bSw: sw("safe_naive"),
        valueFmt: (v) => pctf(v, 1),
        foot: "Both dots are memory-safe. Neither contains `unsafe`. The distance between them is a *codegen* fact — a lost bulk-copy idiom, a foreclosed unroll, a load-merge that did not happen — and it is not a safety property at all.",
      }),

      chartDumbbell({
        key: "hard",
        title: "What the same check costs inside C",
        sub: "R1 → R1h: the identical C kernel with that pattern's own missing safety line added, per compiler — a bounds check on many rows, but elsewhere a validation pass, a splice, a statement reordering or a reference-count increment. **No cross-language noise at all** — the only difference is the check."
          + (badC.length ? ` ⚠ **${badC.length} rows are marked ‡ and are not the price of a check** — see below the chart.` : ""),
        rows: rowsC,
        aLabel: "clang", bLabel: "gcc",
        aSw: sw("c-clang"), bSw: sw("c-gcc"),
        valueFmt: (v) => pctf(v, 1),
        foot: "Without this rung, “C is faster” and “C is unsafe” are the same sentence — C is faster precisely in that it skipped the check. On p08 the two are identical to 0.00 Ir/call, because glibc 2.39's `memcpy` *is* `memmove`; that is a property of this libc, not a result about the check.",
      }),
    ],

    licenceNote(),

    flips.length ? ["div.section", { key: "flip" },
      callout("warn", "The build mode flips the sign here",
        ["On " + flips.map(p => pid(p.id)).join(", ") + ", `R3 − R4` has a different sign in the isolated build than in the whole-program build at `" + c.input + "`. Real programs inline; the assembly you can read is the isolated one. **Both are published because neither is “the” answer**, and a benchmark that reported only one would look decisive and be arbitrary."]),
    ] : ["div", { key: "flip" }, ""],

    ["div.section", { key: "tbl" },
      ["h2", "Every rung, every pattern"],
      ["p.section-note", ...md(`Difference against unsafe Rust in ${c.metric === "kernel" ? "kernel-exclusive" : "marginal"} Ir per call, \`-O3\`, ${c.metric === "kernel" ? "isolated" : c.mode}, \`${c.input}\`. The last column is the unsafe rung's own absolute cost, so a delta can be read as a fraction.`)],
      dataTable(["pattern", ...costCols.map(r => RUNG_SHORT[r]), "R4 Ir/call"],
        full, "fulltbl", { num: [1, 2, 3, 4, 5, 6, 7, 8, 9] }),
      costCols.length < 8
        ? ["p.small.mt8", { key: "trim" },
            ...md(`**${8 - costCols.length} rung column(s) hidden** by the rung filter above. `),
            ["button.icon-btn", { key: "all", onclick: () => setRungs(RUNG_ORDER) }, "show every rung"]]
        : ["div", { key: "trim" }, ""],
      ["p.small.muted.mt8", ...md("**R5's column is not a proof cost.** The R4 and R5 *kernels* are the same machine code, so any non-zero entry there is the environment term the marginal column carries — a stack or heap alignment that moves a C-library routine's path length by up to ±7 instructions per rung on p03 and p04. ⚠ **That bound is for those two patterns, not for the column**: other rows carry a much larger environment term — p25's is +269.52 — and each pattern's own R5 − R4 entry is the null its other differences must be read against. Switch the metric to *kernel Ir/call* and these entries go to exactly 0.")],
    ],

    ["div.section", { key: "caveats" },
      ["h2", "Before quoting any of this"],
      ["div.stack",
        callout("retract", "There is no “cost of safe Rust” here, and seven patterns have published a headline in the flattering direction and had it refuted.",
          ["Every rung is a *spelling*. An audit found all three shipped safe rungs beaten by another safe spelling — each beater also cheaper than its own unsafe rung — and the control that answered it put unsafe back on top, until one more round on the unsafe side flipped the conclusion again on the first thing a reader would try. What ships is a **named-spelling contract** per pattern, hashed into the gate record, and one quantity: `R3ship − R4ship`, which bounds `inf(in-contract R3) − R4ship` **only because R4 is held fixed by fiat**."]),
        callout("warn", "The two Ir columns are not interchangeable, and each pattern says which one it is in.",
          ["The kernel-exclusive column is wrong wherever a rung calls out of its own symbol — it reverses real comparisons on p11 and p08, and p13's rungs call *different* libc routines. The marginal column does not cancel the environment on p03, p04 and p08, where a stack- or heap-alignment term moves it by up to ±7 Ir. Neither is universally right; the pattern pages carry the convention each pattern's own notes declare."]),
        callout("note", "Instruction count is not time.",
          ["On p02, gcc executes 10% fewer instructions and runs 23% slower. On p07, one LLVM pass disabled on unchanged source gives +10.07% instructions and −18.13% wall clock. And **code layout alone moves wall clock by up to 27% at an unchanged instruction stream** — mechanism identified (the 32-byte fetch grid and Intel's SKX102 JCC erratum), predicted out of sample on 20 pre-registered layouts."]),
      ],
    ],
    layoutSection(),
    footer(),
  ];
}

// ------------------------------------------------------------ layout effect --
//
// The control that says why this whole site leads with instruction counts.
// `common/layout/` builds one pattern's rungs 31 ways from identical source —
// same n_fn, same md5_fn_norel, only the address moves — and times each.  The
// derivation lives in build_data.py; the interpretation is in content.js.  This
// only lays out what is in data/index.json.
function layoutSection() {
  const L = (APP.data || {}).layout || {};
  const pairs = L.pairs || [];
  if (!pairs.length) return ["div", { key: "nolay" }, ""];

  // If the builds ever stop being byte-identical the chart's premise is gone,
  // and drawing it anyway would be the exact mistake it exists to warn about.
  if (!L.identical) {
    return ["div.section", { key: "layout" },
      ["h2", "The code-layout control"],
      callout("warn", "Withheld — the control's builds are no longer identical",
        [LAYOUT.withheld + " (`" + (L.source || "the control") + "`)"])];
  }

  const nameOf = (p) => `${RUNG_SHORT[p.a]} − ${RUNG_SHORT[p.b]} · ${p.input}`;
  const rows = pairs.map(p => ({
    name: nameOf(p),
    min: p.min, max: p.max, neg: p.neg, pos: p.pos, n: p.n, values: p.values,
    // positive = the first rung is the dearer one, so the band right of zero is
    // its colour and the band left of zero is the other's — the same rule the
    // diverging chart uses, so no hue means anything new here
    posSw: sw(p.a), negSw: sw(p.b),
  }));
  const flips = pairs.filter(p => p.neg && p.pos);
  const rungs = Object.keys(L.rungs || {});
  const builds = rungs.reduce((n, r) => n + (L.rungs[r].builds || 0), 0);
  const widest = pairs.reduce((w, p) => Math.max(w, p.max - p.min), 0);

  return ["div.section", { key: "layout" },
    ["h2", "The code-layout control"],
    ["p.section-note", ...md(
      "One pattern (`" + (L.pattern || "?") + "`), **" + builds + " builds** " + LAYOUT.lede + " " +
      rungs.map(r => `${RUNG_SHORT[r]}: ${L.rungs[r].builds} layouts at ${L.rungs[r].addresses} addresses, ${L.rungs[r].n_fn} instructions, \`md5_fn_norel ${(L.rungs[r].md5_fn_norel || "").slice(0, 8)}\``).join(" · "))],
    chartSpread({
      key: "layoutspread",
      title: LAYOUT.chartTitle,
      sub: LAYOUT.chartSub,
      rows,
      valueFmt: (v) => (v >= 0 ? "+" : "") + v.toFixed(2) + "%",
      legend: rungs.map(r => ({ sw: sw(r), label: RUNG_SHORT[r] + " dearer" })),
      foot: "Source: `" + (L.source || "") + "`. " + LAYOUT.foot,
      tableHead: ["comparison", "lowest", "highest", "builds where the first rung won", "builds where it lost", "builds"],
    }),
    flips.length
      ? callout("warn",
          `All ${flips.length} of these comparisons change sign depending on the layout`,
          ["The widest band spans **" + widest.toFixed(1) + " percentage points** across builds whose machine code is byte-for-byte the same. " + LAYOUT.flip])
      : ["div", { key: "noflip" }, ""],
  ];
}

// ---------------------------------------------------------------- security --

function viewSecurity() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const d = APP.data, t = d.totals;
  const sel = APP.secPattern || d.patterns[0].id;
  const det = CACHE.pattern[sel];
  if (!det) loadPattern(sel);

  const cols = RUNG_ORDER.slice(0, 8);
  const dev = new Set();
  d.patterns.forEach(p => Object.keys(p.adversarial.worst_by_cell || {}).forEach(c => {
    if (p.adversarial.worst_by_cell[c] !== "match") dev.add(c);
  }));
  const deviatingCells = RUNG_ORDER.filter(c => dev.has(c));

  return ["div", { key: "sec" },
    ["div.eyebrow", "the benefit side of the trade"],
    ["h1", "What each rung does when the input is hostile"],
    ["p.lede", ...md("Every pattern ships adversarial inputs — the ones that trigger the C bug. Every cell is run on every one of them and compared against an **independent Python model** of the kernel. “Correct” here means *agrees with the model*; nothing else counts.")],

    ["div.grid.g4.mt16", { key: "kpi" },
      kpi("Adversarial runs", fmt(t.adversarial_runs),
        `every rung × adversarial input × build — ${fmt(t.adversarial_pairs)} rung/input pairs`),
      // ⚠ NOT a percentage: the denominator pools rungs where failing is
      // impossible with rungs where it is the point, so "87% of runs" is a
      // statement about the mix of rungs, not about safety.
      kpi("Behaved as specified", fmt(t.match),
        `of ${fmt(t.adversarial_runs)} runs. **Deliberately not shown as a rate** — the denominator mixes rungs that cannot fail with the one that does, so a percentage here would measure the ladder's shape, not its safety`, "good"),
      kpi("Silent and wrong", fmt(t.silent), "exit 0, plausible output, **no diagnostic at all**", "crit"),
      kpi("Crashed", fmt(t.crash), "SIGSEGV or abort — loud, and therefore the good outcome"),
      kpi("Never returned", fmt(t.hung || 0),
        "the timeout fired — a memory-safe denial of service (p22)", (t.hung ? "crit" : "")),
      kpi("Build-dependent", fmt(t.build_dependent || 0),
        "rung/input pairs where the **optimisation level decides** what the bug does"),
      // The plainest result on this tab: add the check, and the detector that
      // was firing goes quiet. Every cell, every pattern.
      kpi("Sanitizer hits after the fix", fmt((t.sanitizer_hardened || {}).fired),
        `across **${fmt((t.sanitizer_hardened || {}).cells)}** hardened-C runs — the same sweep that fires **${fmt((t.sanitizer || {}).fired)}** times on the unfixed rung`,
        (t.sanitizer_hardened || {}).fired ? "crit" : "good"),
    ],

    ["div.section", { key: "matrix" },
      ["h2", "The outcome matrix"],
      // The "all deviations are in C" sentence is DERIVED, not asserted — a new
      // pattern whose Rust rung misbehaves must change this line by itself.
      ["p.section-note", ...md(`Worst outcome each rung reached on any adversarial input of that pattern. **${
        deviatingCells.length && deviatingCells.every(c => c === "c-gcc" || c === "c-clang")
          ? "Every deviation in the entire study is in an R1 (plain C) cell"
          : "Cells that deviated from the model: " + deviatingCells.map(c => RUNG_NAME[c]).join(", ")
      }** — ${t.silent} of them silent, ${t.crash} loud. Click a row to inspect the runs.`)],
      ["div.legend.mt8", { key: "leg" },
        ...[["match", "as specified"], ["silent", "silent + wrong"], ["hung", "never returned"],
            ["crash", "crashed"]].map(([k, l]) =>
          ["span.legend-item", { key: "l" + k },
            ["span.legend-key", { style: `background:var(--${CLASS_TONE[k]})` }],
            `${CLASS_ICON[k]} ${l}`]),
        ["span.legend-item", { key: "lsplit" },
          ["span.legend-key.split-key"], "◪ builds disagree"],
      ],
      ["div.matrix.mt16", { key: "m" },
        ["table",
          ["thead", ["tr", ["th.row", "pattern"], ...cols.map(c => ["th", { key: "h" + c }, RUNG_SHORT[c]])]],
          // the row whose detail is shown below is marked, so the matrix and
          // the pane visibly agree about which pattern you are looking at
          ["tbody", ...d.patterns.map(p => ["tr" + (p.id === sel ? ".on" : ""), { key: "r" + p.id },
            ["th.row", { onclick: () => go("security", p.id) },
              ["span", { style: "cursor:pointer" }, prow(p.id)]],
            ...cols.map(c => {
              const k = (p.adversarial.worst_by_cell || {})[c] || "none";
              const sp = (p.adversarial.split_cells || {})[c];
              return ["td", { key: "c" + c },
                ["div.cell." + k + (sp ? ".split" : ""),
                  Object.assign({ onclick: () => go("security", p.id) },
                    tip(`${pid(p.id)} · ${RUNG_NAME[c]}\n${CLASS_LABEL[k]}` +
                        (sp ? "\nand it does not do this in every build" : ""))),
                  CLASS_ICON[k]]];
            }),
          ])],
        ],
      ],
      callout("warn", "Read the green honestly — and the reason is stronger than “we need better inputs”",
        [MATRIX.green, MATRIX.zerocall]),
    ],

    ["div.section", { key: "detail" },
      ["div.pane-head", { key: "ph" },
        ["h2", "Run detail — " + pid(sel) + " " + pname(sel)],
        patternPicker("security", sel, "pk"),
      ],
      ["p.section-note", ...md("Each row is one adversarial input; each column one cell. `✓` means the process exit code *and* the printed checksum matched the model.")],
      det && det !== "loading" ? advDetail(det) : ["div.loading", { key: "l" }, "Loading run detail…"],
    ],

    ["div.section", { key: "tools" },
      ["h2", "What the tools saw — " + pid(sel) + " " + pname(sel)],
      det && det !== "loading" ? toolsDetail(det) : ["div.loading", { key: "l2" }, "…"],
    ],

    ["div.section", { key: "limits" },
      ["h2", "Where “memory-safe” is the wrong question"],
      ["div.grid.g2.mt16",
        ...[
          ["p17-http-range", "Proved memory-safe, still leaking",
            "Guard the slice-relative index — exactly what a bounds check buys, no more — and Verus discharges every access obligation. The program then reads a neighbouring window's bytes and its output tracks the victim's secret. No panic, no `unsafe`, no sanitizer finding."],
          ["p09-bitset", "One character, invisible to everything",
            "`words[q >> 7]` under the guard `q < nbits` is always a legal word index, so it verifies clean, costs zero instructions, differs from the shipped kernel in **one byte of 368**, and returns a wrong answer on every input. `q >> 5` — the same edit in the other direction — is caught by the bounds check alone."],
          ["p04-ring-buffer", "A bug entirely in bounds",
            "Drop the fullness check and a push overwrites the oldest live element. Every index formed stays inside the array, so with the functional spec stripped the proof still verifies 9/0 — and it is blind to *every* functional change, including reading the wrong cursor."],
          ["p08-overlap-move", "A bug safe Rust cannot express — and the proof does not close",
            "The borrow checker rejects the overlapping move at compile time: no runtime check, nothing to measure. But substituting `copy_nonoverlapping` into the *trusted* body verifies clean under Verus and under the twin. Only Miri and the byte-identity pin catch it. **A proof that a `requires` holds is not a proof that the trusted body honours it.**"],
          ["p22-hash-probe", "Safe Rust does not help at all",
            "A full table makes the probe loop **never return**. Every index stays in the table forever, so Miri is silent, ASan is silent, and the bounds checks buy nothing — the missing guard is a fill count, not a bound. Both C rungs hit the timeout; the harm is a denial of service, and the obligation that sees it is **termination**."],
          ["p47-ct-compare", "Safe Rust leaks where hardened C does not",
            "The kernel folds only the *verdict*, so the functional contract cannot see the leak. C's `memcmp` and safe Rust's `a == b` both leak in executed instructions; hardened C, tuned safe Rust and both unsafe rungs do not. R5 verifies the same contract as R4 and **the obligation count does not move** — a specification of *what* is computed cannot constrain *how long* it takes."],
        ].map(([id, h, body]) => ["div.card", { key: "lim" + id },
          ["div.rung-id", pid(id)],
          ["h3", { key: "h" }, h],
          ["p.small.muted", { key: "b" }, ...md(body)],
          ["button.icon-btn", { key: "go", onclick: () => go("patterns", id) }, "open pattern →"],
        ]),
      ],
    ],
    footer(),
  ];
}

function advDetail(det) {
  const inputs = Object.keys(det.adversarial).sort();
  const cols = RUNG_ORDER.filter(c => inputs.some(i => det.adversarial[i][c]));
  const shortCell = (c) => c.replace("isolated", "iso").replace("whole", "wp").replace("/", " ");
  const rows = inputs.map(inp => {
    const per = det.adversarial[inp];
    return [inp.replace(".bin", "")].concat(cols.map(c => {
      const r = per[c];
      if (!r) return "—";
      // One entry per distinct behaviour.  A rung with two entries behaved
      // differently at different optimisation levels — that is the finding.
      const chips = (r.groups || []).map((g, i) => {
        const detail = `${inp} · ${RUNG_NAME[c]}` +
          (g.cells.length ? `\nbuilds   ${g.cells.join(", ")}` : "") +
          `\nexit ${g.hung ? "— (timed out)" : g.exit}${g.signal ? " (signal " + g.signal + ")" : ""}` +
          `, model exit ${g.model_exit}` +
          `\nprinted  ${g.stdout || "(nothing)"}` +
          `\nmodel    ${g.model_stdout || "(nothing)"}` +
          (g.stderr ? `\nstderr   ${g.stderr.slice(0, 90)}` : "");
        return ["span.chip." + (CLASS_TONE[g.class] || "warning"),
          Object.assign({ key: "g" + i }, tip(detail)),
          ["span.dot"],
          CLASS_LABEL[g.class] + (r.groups.length > 1 && g.cells.length
            ? " · " + g.cells.map(shortCell).join(", ") : "")];
      });
      return { jsonml: ["span.chip-stack", { key: "cs" }, ...chips] };
    }));
  });
  return dataTable(["input"].concat(cols.map(c => RUNG_SHORT[c])), rows, "adv-" + det.id, {});
}

// What a sanitizer run actually did, in the outcome matrix's own vocabulary.
//
// "fired / silent" was the whole answer here, and it hides the two cases that
// matter most: a run that NEVER RETURNED reads as silent, and so does a run
// that exited 0 with the wrong number.  Both are in the record — `hung`, and
// `stdout` against the model's — and both are the site's own thesis, which is
// that a clean sanitizer report is not a statement about correctness.
function sanClass(s) {
  if (s.hung) return "hung";
  if (s.fired) return "loud";
  if (s.stdout !== undefined && s.model_stdout !== undefined
      && s.stdout !== "" && s.stdout !== s.model_stdout) return "silent";
  return "match";
}

// The idiom audit's own rows, which were only ever summed into three numbers.
// Folded, because on a healthy pattern the interesting count is zero and the
// rest is a list a reader consults rather than reads.
function idiomDetail(det) {
  const ia = det.idiom_audit || {};
  const buckets = [
    ["hits", "forbidden spelling FOUND in a rung", ia.hits],
    ["forbidden_unaudited", "declared as prose — no spelling to search for, so nothing was checked", ia.forbidden_unaudited],
    ["pins_nothing", "required in a language, present in none of its rungs", ia.pins_nothing],
    ["absent", "required and scoped — present in some rungs of that language, not others", ia.absent],
    ["no_rung", "declared for a language this pattern ships no rung for", ia.no_rung],
  ].filter(b => (b[2] || []).length);
  if (!buckets.length) return ["div", { key: "noia" }, ""];
  const rows = [];
  buckets.forEach(([name, meaning, list]) => (list || []).forEach(e => rows.push([
    name, e.entry || "—", e.lang || "—",
    { jsonml: ["code.small", (e.spelling || (e.spellings || []).join(", ") || e.text || "—").slice(0, 90)] },
    { jsonml: ["span.small.muted", e.rung || (e.of_rungs !== undefined ? `${e.of_rungs} rung(s)` : meaning.slice(0, 40))] },
  ])));
  return ["details.fold.mt16", { key: "iafold" },
    ["summary", `idiom audit — ${rows.length} entr${rows.length === 1 ? "y" : "ies"} worth reading`],
    ["div.fold-body",
      ["p.small.muted", ...md(IDIOM.detail)],
      dataTable(["bucket", "entry", "lang", "spelling", "where"], rows, "ia-" + det.id, { wrap: [3] }),
    ],
  ];
}

function toolsDetail(det) {
  const san = det.sanitizer || {};
  const keys = Object.keys(san).sort();
  const rows = keys.map(k => {
    const s = san[k], cl = sanClass(s);
    return [k.replace(".bin", ""),
      s.expect,
      { jsonml: ["span.chip." + (CLASS_TONE[cl] || "other"), ["span.dot"],
          CLASS_ICON[cl] + " " + (cl === "loud" ? "fired" : CLASS_LABEL[cl])] },
      s.hung ? (s.declared_hang ? "declared" : "UNDECLARED") : String(s.exit),
      { jsonml: ["span.small.muted", (s.diagnostic || "").slice(0, 150)
          || (cl === "silent" ? `printed ${s.stdout} · model says ${s.model_stdout}` : "—")] }];
  });
  const quiet = keys.filter(k => sanClass(san[k]) === "silent");
  const stuck = keys.filter(k => san[k].hung);
  const m = det.miri || {};
  const ti = m.trusted_items || {};
  const tiList = Object.keys(ti).map(s => `\`${s}\`: ` + (ti[s] || []).map(i => "`" + i + "`").join(", ")).join(" · ");
  return ["div", { key: "tools" },
    ["h3", "ASan + UBSan, on the adversarial inputs"],
    quiet.length
      ? callout("warn", `${quiet.length} of these ${keys.length} runs exit 0, report nothing, and print the wrong answer`,
          ["The sanitizers are working: there is no memory error on these inputs to find. The kernel is simply wrong, and **a clean sanitizer report says nothing about that** — which is why the column below compares what each run printed against the independent model rather than trusting its exit code. Inputs: " + quiet.map(k => "`" + k.replace(".bin", "") + "`").join(", ") + "."])
      : ["div", { key: "nq" }, ""],
    stuck.length
      ? callout("note", `${stuck.length} run never returned`,
          ["A timeout is not a silent pass, and it used to render as one. " +
           (san[stuck[0]].declared_hang
             ? "This input is **declared** non-terminating in the pattern's own spec, so the timeout is the expected result and not a gate failure."
             : "⚠ This input is **not** declared non-terminating — an undeclared hang is a finding.")])
      : ["div", { key: "ns" }, ""],
    dataTable(["input", "expected", "result", "exit", "diagnostic"], rows, "san-" + det.id, { wrap: [4] }),
    ["h3.mt28", "Miri"],
    ["p.small.muted", ...md(m.required
      ? `Required here because this pattern has ${m.trusted_items ? Object.values(ti).reduce((n, v) => n + v.length, 0) : 0} trusted \`external_body\` item(s) — ${tiList} — whose \`ensures\` need not be *complete* with respect to the unchecked operations their bodies perform. **${(m.runs || []).length} runs, ${(m.runs || []).filter(r => r.ub).length} reporting UB.**`
      : "Not required for this pattern.")],
    (m.runs || []).length ? dataTable(["source", "input", "exit", "UB", "printed", "model"],
      m.runs.map(r => [r.source, (r.input || "").replace(".bin", ""), r.exit,
        { text: r.ub ? "YES" : "no", cls: r.ub ? ".pos" : "" }, r.stdout || "—", r.model_stdout || "—"]),
      "miri-" + det.id, { num: [2] }) : ["div", { key: "nomiri" }, ""],
  ];
}

// ------------------------------------------------------------------- proof --

function viewProof() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const d = APP.data, t = d.totals;
  const sel = APP.proofPattern || d.patterns[0].id;
  const det = CACHE.pattern[sel];
  if (!det) loadPattern(sel);

  const tcbRows = d.patterns.map(p => [
    pid(p.id), pname(p.id),
    p.verus.verified, { text: p.verus.errors, cls: p.verus.errors ? ".pos" : ".zero" },
    p.verus.tcb_items, p.verus.tcb_lines, p.verus.twins,
    { jsonml: ["span.chip." + (p.identity_o3.equal ? "good" : "critical"), ["span.dot"],
      p.identity_o3.equal ? "byte-identical" : "differs"] },
    p.identity_o3.n_fn,
  ]);

  return ["div", { key: "proof" },
    ["div.eyebrow", "the third axis nobody publishes"],
    ["h1", "The proof is free. The trusted base is the price."],
    ["p.lede", ...md(`A Verus proof erases at run time: **zero executed instructions**, and on ${t.identity_exact} of ${t.patterns} patterns the proved kernel is byte-identical to the unproved one. What it actually costs is a small set of \`external_body\` wrappers whose bodies are **trusted, not verified** — and every one of them is a place the guarantee can be silently wrong. So this project counts them, in lines, per pattern.`)],
    // ⚠ The one place this site read as over-claiming. The zero is enforced,
    // not discovered, and the enforcement has a price of its own that is
    // measured elsewhere on the site. Say both, right under the headline.
    callout("warn", PROOFCOST.head, PROOFCOST.body),

    ["div.grid.g4.mt16", { key: "kpi" },
      // ⚠ The page's biggest number, with its unit never defined and its own
      // known weakness unstated: the research measures this as a SIZE PROXY
      // (0.92 correlation with syntactic size), not as a coverage measure.
      kpi("Proof goals discharged", fmt(t.verus_verified),
        `small checks — “this index is in range”, “this loop ends” — one at a time, across ${t.patterns} proved kernels, **all passing**`
        + (t.verus_verified_controls
            ? ` · a further **${t.verus_verified_controls}** belong to the R2v control and are counted apart`
            : "")
        + " · ⚠ **a count, not a coverage measure** — see below",
        "good"),
      kpi("Verification errors", fmt(t.verus_errors), "every shipped rung verifies", t.verus_errors === 0 ? "good" : "crit"),
      kpi("Trusted items", fmt(t.tcb_items), `**${t.tcb_lines} lines** of trusted body in total`),
      kpi("R4 ≡ R5 at `-O3`", `${t.identity_exact}/${t.patterns}`,
        t.identity_exact === t.patterns
          ? "byte-identical kernel machine code"
          : `byte-identical kernel machine code · on the other ${t.patterns - t.identity_exact} the two kernels have the **same instructions in the same order** and differ only in pc-relative displacements`,
        "good"),
      // ⚠ This 0 counts FIVE body-less forms and reads as "no hand-written
      // assumptions anywhere", which is false: ten patterns carry a `global`
      // directive, and every proof rests on the prover library's own axioms.
      kpi("Body-less trusted forms", fmt(t.axiom_decls || 0),
        "`assume` and uninterpreted declarations found by the gate. ⚠ **Not the same as “rests on no assumptions”** — every proof here stands on the prover library's axioms, and ten patterns declare a compile-time fact of their own",
        (t.axiom_decls ? "crit" : "good")),
      kpi("Verus-satisfied, `rustc` not", fmt(t.verus_exit_anomalies || 0),
        "runs where the proof reported no errors and the process still exited non-zero — `0 errors` alone is not a green light",
        (t.verus_exit_anomalies ? "crit" : "good")),
    ],

    ["div.section", { key: "expl" },
      callout("warn", GOALS.head, GOALS.body),
      ["h2", "How a trusted item is kept honest"],
      ["div.grid.g3.mt16",
        ["div.card", { key: "e1" }, ["h3", "1 · It is counted"],
          ["p.small.muted", ...md("Every `external_body` item is listed with its body length. A rung-5 cell with a 200-line trusted base is not a win and must not be presented as one.")]],
        ["div.card", { key: "e2" }, ["h3", ...md("2 · Its `requires` must bite")],
          ["p.small.muted", ...md("Each precondition is re-verified as a *tautology* — if it is one, it constrains no caller and the item is trusted for nothing. Each `ensures` is deleted in turn; if the proof still passes, that clause was never load-bearing.")]],
        ["div.card", { key: "e3" }, ["h3", "3 · It gets a verified twin"],
          ["p.small.muted", ...md("A second implementation of the same signature, written in *safe* Rust and **verified**, must discharge the same contract. It catches a trusted `requires` that is too weak — which Miri cannot, because Miri never opens the proof. ⚠ **It is a rule with recorded exceptions**: on p35 three trusted items have no twin at all, because Rust has no safe way to read a union, and the gate reports those as blocked rows rather than passing them.")]],
      ],
      callout("note", "Why the trusted base cannot simply be verified away",
        ["The obvious repair — verify the wrappers instead of trusting them — was measured across the whole corpus as it stood at the time (14 patterns, 58 trusted items) and **it does not scale**: exactly **2** of those could be discharged by leaning on vstd's own specifications instead. `get_unchecked`, `get_unchecked_mut`, `copy_nonoverlapping`, `as_ptr`, `<*const T>::add` and `count_ones` are each `is not supported` at the pinned vstd. And where it *does* work the axiom does not vanish — it **relocates** into vstd's own trusted items, which is a different trusted base, not a smaller one."]),
      callout("warn", "And the limit of all three, measured on p08",
        ["Substituting `copy_nonoverlapping` for `core::ptr::copy` inside p08's trusted `move_right` — a wrapper whose entire safety contract *is* the non-overlap — verifies 11/0, and 15/0 under the twin. The `requires` still holds; the *body* stops honouring it. Only Miri and the byte-identity pin caught it. **A proof is exactly as good as its trusted base and its specification, and both are human artefacts.**"]),
    ],

    ["div.section", { key: "table" },
      ["h2", "Proof burden per pattern"],
      dataTable(["", "pattern", "verified", "errors", "trusted items", "trusted lines", "twins", "R4 ≡ R5 (O3)", "kernel instrs"],
        tcbRows, "tcb", { num: [2, 3, 4, 5, 6, 8], onRow: (i) => go("proof", d.patterns[i].id),
                          selRow: d.patterns.findIndex(p => p.id === sel) }),
      ["p.small.muted.mt8", ...md("Click any row to inspect that pattern's trusted base below. “Kernel instrs” is the declared symbol extent of the R4/R5 kernel at `-O3`, which is the object the byte-identity claim is about.")],
    ],

    ["div.section", { key: "detail" },
      ["div.pane-head", { key: "ph" },
        ["h2", "Trusted base — " + pid(sel) + " " + pname(sel)],
        patternPicker("proof", sel, "pk"),
      ],
      det && det !== "loading" ? proofDetail(det) : ["div.loading", { key: "l" }, "Loading…"],
    ],
    footer(),
  ];
}

// Was the precondition true on the runs that matter, or is it an assumption
// that quietly excuses the kernel from the attacks?  The gate answers it by
// EVALUATING the clause on every call rather than reasoning about it, and
// records `requires_ok` per input alongside how many `ensures` it checked
// against the independent model.
function domainNote(det) {
  const pd = (det.verus || {}).proof_domain || {};
  const names = Object.keys(pd);
  if (!names.length) return ["div", { key: "nodom" }, ""];
  const hostile = names.filter(n => !/^(small|large)\.bin$/.test(n));
  const calls = names.reduce((n, k) => n + (pd[k].calls || 0), 0);
  const bad = names.filter(n => pd[n].requires_ok !== true);
  const ens = names.reduce((n, k) => n + (pd[k].ensures_checked || 0), 0);
  return bad.length
    ? callout("warn", `The precondition did NOT hold on ${bad.length} input(s)`,
        ["Any run outside the precondition is outside what the proof says anything about: " +
         bad.map(n => "`" + n.replace(".bin", "") + "`").join(", ") + "."])
    : callout("note", "This precondition held on every run, including every attack",
        [`Evaluated on **${fmt(calls)} kernel calls** across **${names.length} inputs**, `
         + `**${hostile.length}** of them adversarial or degenerate — it held on all of them, `
         + `and **${fmt(ens)}** postcondition checks were made against the independent model.`,
         CONTRACT.domain]);
}

function proofDetail(det) {
  const v = det.verus || {};
  const tcb = v.tcb || [];
  const twins = v.twins || [];
  const cd = v.clause_deletion || {};
  const rs = v.requires_strength || {};
  const dc = det.derived_contract || {};

  const cdRows = [];
  Object.keys(cd).forEach(src => (cd[src].mutants || []).forEach(m => {
    const control = /assert/.test(m.kind || "");
    const live = m.errors > 0;
    cdRows.push([m.item, m.kind, { jsonml: ["code.small", (m.clause || "—").slice(0, 90)] },
      `${m.verified} / ${m.errors}`,
      control
        ? { text: live ? "probe is live" : "PROBE IS BLIND", cls: live ? "" : ".pos" }
        : { text: live ? "load-bearing" : "NOT load-bearing", cls: live ? "" : ".pos" }]);
  }));

  const rsRows = [];
  Object.keys(rs).forEach(src => (rs[src].mutants || []).forEach(m => {
    rsRows.push([m.item, m.kind, { jsonml: ["code.small", (m.clause || "—").slice(0, 80)] }, m.test,
      m.verdict || `${m.verified} / ${m.errors}`]);
  }));

  // Empty on every healthy run, so this renders nothing at all until it does
  // not: a cell where Verus reported `0 errors` and the process still failed.
  const anom = v.exit_anomalies || [];

  return ["div", { key: "pd" },
    anom.length
      ? callout("warn", `Verus was satisfied and \`rustc\` was not — ${anom.length} run(s)`,
          [`The proof reported no errors and the process still exited non-zero, so "0 errors" is not by itself a green light on this pattern.`,
           ...anom.map(a => "`" + (typeof a === "string" ? a : JSON.stringify(a)) + "`")])
      : ["span", { key: "noanom" }, ""],
    ["div.grid.g2", { key: "contract" },
      ["div.card", { key: "req" },
        ["div.eyebrow", "what the caller must guarantee"],
        ...(dc.requires || []).map((r, i) => clauseLine(r, "rq" + i)),
        (dc.requires || []).length ? ["span", { key: "x" }, ""] : ["p.small.muted", { key: "none" }, "total — no precondition"],
        ["p.small.muted.mt8", { key: "why" }, ...md(CONTRACT.requires)],
      ],
      ["div.card", { key: "ens" },
        ["div.eyebrow", "what it promises"],
        ...(dc.ensures || []).map((r, i) => clauseLine(r, "en" + i)),
        ["p.small.muted.mt8", { key: "why" }, ...md(CONTRACT.ensures)],
      ],
    ],
    // A precondition is only worth as much as the set of runs it holds on. The
    // gate evaluates it on every call of every input and records the result, so
    // this is the answer to "is that assumption doing the work the proof should
    // be doing?" — and it was sitting in data/ unrendered.
    domainNote(det),
    ["h3.mt28", ...md("Trusted items (`external_body` — bodies are trusted, not verified)")],
    dataTable(["item", "attribute", "body lines", "source", "line"],
      tcb.map(i => [i.name, i.attr, i.body_lines, i.source, i.line]), "tcb-" + det.id, { num: [2, 4] }),

    twins.length ? ["div", { key: "tw" },
      ["h3.mt28", "Verified twins"],
      ["p.small.muted", ...md("Each twin re-implements a trusted item's signature in safe, **verified** Rust. `load-bearing` counts the `requires` conjuncts whose individual deletion breaks the twin's proof — a conjunct that is not load-bearing is trusted for nothing.")],
      dataTable(["trusted item", "twin", "requires", "body lines", "load-bearing conjuncts"],
        twins.map(t => [t.trusted, t.twin, { jsonml: ["code.small", (t.requires || []).join("  ∧  ") || "—"] },
          t.body_lines, `${t.load_bearing} / ${t.conjuncts}`]), "twins-" + det.id, { num: [3] }),
    ] : ["div", { key: "tw" }, ""],

    cdRows.length ? ["div", { key: "cd" },
      ["h3.mt28", "Is each promise load-bearing? (clause-deletion probe)"],
      ["p.small.muted", ...md("Every `ensures` is deleted in turn and the proof re-run. If it still passes, that clause was decoration. The first row is an `assert(false)` control: if *that* verifies, the whole probe is blind.")],
      dataTable(["item", "kind", "clause deleted", "verified / errors", "verdict"], cdRows, "cd-" + det.id, {}),
    ] : ["div", { key: "cd" }, ""],

    rsRows.length ? ["div", { key: "rs" },
      ["h3.mt28", "Is each precondition non-trivial? (tautology probe)"],
      dataTable(["item", "kind", "clause", "test", "verdict"], rsRows, "rs-" + det.id, {}),
    ] : ["div", { key: "rs" }, ""],

    ["h3.mt28", "Byte-identity of the R4 and R5 kernels"],
    dataTable(["opt", "expected", "md5(fn) a", "md5(fn) b", "equal", "instrs a / b"],
      (det.identity || []).map(i => [i.opt, i.expected, (i.md5_fn_a || "").slice(0, 12), (i.md5_fn_b || "").slice(0, 12),
        { text: i.md5_fn_a === i.md5_fn_b ? "yes" : "no (relocation-masked at O0)", cls: i.md5_fn_a === i.md5_fn_b ? "" : ".zero" },
        `${(i.counts_a || [])[0]} / ${(i.counts_b || [])[0]}`]),
      "id-" + det.id, {}),
    ["p.small.muted.mt8", ...md("At `-O0` the Rust kernel still calls out (`Iterator::next`), so the two binaries link callees at different addresses; the honest oracle there is the same bytes with pc-relative displacement fields zeroed. At `-O3` the claim is exact, on raw bytes.")],
  ];
}

// ---------------------------------------------------------------- patterns --

function viewPatterns() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const d = APP.data;
  const id = APP.patId || d.patterns[0].id;
  const p = pat(id);
  const det = CACHE.pattern[id];
  if (!det) loadPattern(id);

  return ["div.pat-layout", { key: "pl" },
    ["div.pat-list", { key: "list" },
      ["div.eyebrow", `${d.patterns.length} of ${(d.totals || {}).catalogue || "?"}`],
      ...d.patterns.map(x => ["button.pat-item" + (x.id === id ? ".on" : ""),
        { key: "pi" + x.id, onclick: () => go("patterns", x.id) },
        ["span.pid", pid(x.id)],
        ["span.pnm", pname(x.id)],
      ]),
    ],
    ["div", { key: "detail" }, det && det !== "loading" ? patternView(p, det) : ["div.loading", "Loading pattern…"]],
  ];
}

function patternView(p, det) {
  const c = CONTENT_PATTERNS()[p.id] || {};
  const hasProse = !!CONTENT_PATTERNS()[p.id];
  const code = CACHE.code[p.id];
  if (!code) loadCode(p.id);
  const docs = CACHE.docs[p.id];
  if (!docs) loadDocs(p.id);
  const rung = APP.patRung;

  const sel = (p.tax || {})["isolated/small.bin"] || { cells: {} };
  const items = visibleRungs(sel.cells).map(x => ({
    label: RUNG_SHORT[x], cell: x, value: sel.cells[x].ir,
    tip: `${RUNG_NAME[x]}\n${fmt(sel.cells[x].ir)} Ir/call\n${sfmt(sel.cells[x].delta)} vs unsafe Rust`,
  }));

  const inputRows = Object.keys(det.inputs || {}).sort().map(k => {
    const i = det.inputs[k];
    return [k.replace(".bin", ""), fmt(i.n_iters), fmt(i.calls), { jsonml: ["span.small.muted", i.model || ""] }];
  });

  return ["div", { key: "pv" },
    ["div.eyebrow", (c.family || "") + " · " + (c.bug || "")],
    ["h1", pid(p.id) + " — " + (c.title || p.id)],
    ["p.lede", ...md(c.role || "")],

    ["div.inline-list.mt16", { key: "chips" },
      ["span.chip." + (p.verdict === "PASS" ? "good" : "warning"), ["span.dot"], p.verdict],
      ["span.chip", `${p.verus.verified} verified · ${p.verus.errors} errors`],
      ["span.chip", `TCB ${p.verus.tcb_items} items / ${p.verus.tcb_lines} lines`],
      ["span.chip." + (p.identity_o3.equal ? "good" : "critical"), ["span.dot"], "R4 ≡ R5 exact at O3"],
      ["span.chip" + (p.adversarial.counts.silent ? ".critical" : ""),
        p.adversarial.counts.silent ? ["span.dot"] : ["span", ""],
        `${p.adversarial.counts.silent || 0} silent-wrong runs`],
      ["span.chip.tag", `measured ${(det.generated_utc || "").slice(0, 10)}`],
    ],

    // A gate that did not pass is the first thing a reader needs, not a chip
    // two thirds of the way down. Every number below still renders — refusing
    // to show it would be worse — but it is provisional and says so here.
    String(p.verdict || "").startsWith("PASS") ? ["div", { key: "nfail" }, ""]
      // ⚠ NO BACKTICKS IN A CALLOUT HEADING. `callout` runs `md()` over its
      // BODY and renders its HEAD as a raw string, so a code span here reaches
      // the page as a literal backtick — which `check.mjs` fails on, correctly.
      // This only fired the first time a pattern upstream actually went FAIL,
      // months after the line was written, because until then the branch was
      // dead. Keep the verdict unformatted, or move it into the body.
      : callout("warn", `This pattern's gate did not pass — verdict ${p.verdict}, ${p.failures || 0} failure(s)`,
          ["Everything below is generated from its record exactly as for every other pattern, and is **provisional**: the gate is the thing that decides whether a pattern's numbers may be believed, and on this one it has not. The failures are listed under **Gate record**. This normally means the pattern is still being built upstream."]),

    ["div.section", { key: "story" },
      hasProse ? ["div", { key: "np" }, ""] : callout("note", "No write-up on this page yet",
        ["This pattern landed in the repository after the report's prose was written, so the account below is its own — the numbers, tables and charts are generated from its gate record exactly as for every other pattern, and its `README.md`, `spec.md` and `NOTES.md` are at the bottom of this page."]),
      ["div.prose", ...(c.story || []).map((s, i) => mdP(s, "s" + i))],
      c.caveat ? callout("warn", "The correction", [c.caveat]) : ["div", { key: "nc" }, ""],
      c.convention ? ["p.small.muted", { key: "conv" }, ...md("**Which `Ir` column this pattern's numbers are in:** " + c.convention)] : ["div", { key: "nv" }, ""],
    ],

    ["div.section", { key: "profile" },
      ["h2", "The ladder on this kernel"],
      ["p.section-note", ...md("Marginal Ir per kernel call, `-O3`, isolated build, `small.bin`. Cool bars are C, warm bars are Rust; within each pair the washed bar is the plain rung and the solid one is its hardened, tuned or proven twin.")],
      ["div.filters", { key: "pf-filters" },
        rungPresets("pp-pre"),
        ["div.field", { key: "tog", style: "flex-basis:100%" },
          ["span.field-label", "rungs — click a key to hide it"],
          rungLegend(RUNG_ORDER.filter(x => sel.cells[x]), { key: "lg" + p.id }),
        ],
      ],
      ["div.chart", { key: "ch" },
        items.length
          ? barsChart(items, { key: "cc" + p.id })
          : ["div.loading", { key: "none" }, "every rung is hidden — turn one back on above"],
        ["div.chart-foot", ...md("R5 sits on R4 by construction — the identity pin requires it, and it is checked on raw machine-code bytes.")],
      ],
      tableFold(["rung", "Ir/call", "vs R4"],
        visibleRungs(sel.cells).map(x => [RUNG_NAME[x], fmt(sel.cells[x].ir), sfmt(sel.cells[x].delta)]), "pf" + p.id),
    ],

    ["div.section", { key: "contract" },
      ["h2", "The contract the gate enforces"],
      ["div.grid.g2",
        ["div.card", { key: "rq" },
          ["div.eyebrow", "requires — what the kernel demands of its caller"],
          ...((det.derived_contract || {}).requires || ["(none — total)"]).map((r, i) => clauseLine(r, "r" + i)),
        ],
        ["div.card", { key: "en" },
          ["div.eyebrow", "ensures — what it promises in return"],
          ...((det.derived_contract || {}).ensures || ["—"]).map((r, i) => clauseLine(r, "e" + i)),
        ],
      ],
      idiomFold(det),
    ],

    ["div.section", { key: "inputs" },
      ["h2", "Inputs"],
      ["p.section-note", ...md("All data and every loop bound come from the file, so no cell can be partially evaluated to its answer. `calls` is the number of real kernel invocations the proof-domain stage counted.")],
      dataTable(["input", "driver iterations", "kernel calls", "model"], inputRows, "in" + p.id, { num: [1, 2], wrap: [3] }),
    ],

    ["div.section", { key: "adv" },
      ["h2", "Behaviour on the adversarial inputs"],
      advDetail(det),
    ],

    ["div.section", { key: "wall" },
      ["h2", "Wall clock"],
      ["p.section-note", ...md((det.protocol || {}).wall || "")],
      wallTable(det),
      callout("warn", "Read these as levels, not as differences",
        ["Each time includes process start-up and reading the input file — on one pattern that constant is 73% of the number — so a **ratio of two of these is not a ratio of two kernels**. And code layout alone moves wall clock at an unchanged instruction stream, which can flip a rung comparison: the control for that is charted under **Cost of safety**, where every comparison it produces changes sign across builds of identical machine code. Only the patterns whose notes carry a 30-layout population have a bracketed answer. The instruction columns above are the headline; this table is the sanity check on them."]),
    ],

    ["div.section", { key: "code" },
      ["h2", "The kernel, rung by rung"],
      ["p.section-note", ...md("Kernel source only — the driver is shared boilerplate (`common/driver.rs`, `common/driver.c`) and is byte-identical across rungs by construction, which the gate checks.")],
      ["div.codebar-group", { key: "cbg" },
        ["div.codebar-lab", { key: "l1" }, "one rung"],
        ["div.codebar", { key: "cb1" },
          ...RUNG_ORDER.filter(x => code && code !== "loading" && code[x]).map(x =>
            ["button.tab" + (!APP.patDiff && rung === x ? ".active" : ""),
              { key: "cb" + x, onclick: () => { APP.patRung = x; APP.patDiff = null; renderAll(); } },
              RUNG_SHORT[x] + " · " + RUNG_NAME[x]]),
        ],
      ],
      ["div.codebar-group", { key: "cbg2" },
        ["div.codebar-lab", { key: "l2" }, "what changes between rungs"],
        ["div.codebar", { key: "cb2" },
          ...DIFF_PAIRS.filter(p => code && code !== "loading" && code[p.a] && code[p.b]).map(p =>
            ["button.tab.diff" + (APP.patDiff === p.id ? ".active" : ""),
              { key: "db" + p.id, onclick: () => { APP.patDiff = p.id; renderAll(); } }, p.label]),
        ],
      ],
      (!code || code === "loading")
        ? ["div.loading", { key: "cl" }, "Loading source…"]
        : APP.patDiff
          ? diffBlock(DIFF_PAIRS.find(p => p.id === APP.patDiff) || DIFF_PAIRS[0], code, "dv")
          : code[rung]
            ? ["div", { key: "cw" },
                SYNTAX.langFor(rung, (code[rung] || {}).lang) === "verus"
                  ? verusLegend() : ["span", { key: "nl" }, ""],
                codeBlock(code[rung].text, SYNTAX.langFor(rung, code[rung].lang), "src"),
                ["div.code-meta", { key: "cm" }, code[rung].file],
              ]
            : ["div.loading", { key: "cl" }, "This pattern has no such rung."],
    ],

    ["div.section", { key: "gate" },
      ["h2", "Gate record"],
      dataTable(["", ""], [
        ["verdict", det.verdict],
        ["complete run", String(det.complete_run)],
        ["failures", String((det.failures || []).length)],
        // Quoted verbatim from the gate record — machine text, not our prose, so
        // it renders as code and its own punctuation is left alone.
        ["blocked rows", (det.blocked || []).length
          ? { jsonml: ["code.small", (det.blocked || [])
              .map(b => typeof b === "string" ? b : JSON.stringify(b)).join("; ")] }
          : "none"],
        ["contract sha256", (det.contract_sha256 || "").slice(0, 24)],
        ["idiom audit", `${(det.idiom_audit || {}).spellings || 0} pinned spellings over ${(det.idiom_audit || {}).pairs || 0} spelling × rung pairs · ${(det.idiom_audit || {}).forbidden_hits || 0} forbidden hits · ${(det.idiom_audit || {}).required_absent || 0} scoped-absent · ${(det.idiom_audit || {}).required_pins_nothing || 0} pinning nothing · ${(det.idiom_audit || {}).forbidden_unaudited_entries || 0} unchecked`],
        ["files hashed", String(Object.keys(det.source_sha256 || {}).length)],
        ["declared non-terminating inputs",
          (det.expected_hang || []).length
            ? (det.expected_hang || []).join(", ") + "  (timeout " +
              Object.values(det.run_timeout_s || {}).map(v => v + "s").join(", ") + ")"
            : "none"],
        ["timing", (det.protocol || {}).wall || "—"],
        // The marginal Ir column is not invariant to the environment it was
        // measured in — so what makes it reproducible is recording the draw,
        // not pretending there was not one.
        ["environment the marginal was measured under",
          (det.marginal_ir_env || {}).bytes
            ? `${fmt(det.marginal_ir_env.bytes)} bytes`
              + (Object.keys(det.marginal_ir_env.tuning_vars || {}).length
                  ? " · tunables: " + Object.keys(det.marginal_ir_env.tuning_vars).join(", ")
                  : " · no glibc tunables")
            : "not recorded"],
        ["published table", (det.published_table || {}).verdict
          ? `${det.published_table.verdict} — ${det.published_table.table || ""}`
          : "—"],
      ], "gate" + p.id, { wrap: [1] }),
      idiomDetail(det),
      // The count alone said "3 failures" and nothing about what failed, so a
      // pattern still being built upstream read as a finished one with a bad
      // chip.  The gate writes a section and a message per failure; show them.
      (det.failures || []).length ? ["div.mt16", { key: "fails" },
        ...det.failures.map((f, i) =>
          callout("warn", "gate failure — " + (f.section || "?"), [f.message || ""]))] : ["div", { key: "nf" }, ""],
      // ⚠ `md()`, not a bare string.  The gate writes its notes in markdown —
      // they name files and patterns in backticks — and this was the one of the
      // three failure/note renderers that did not run them through it, so a
      // code span reached the page as a literal backtick.  It only showed when
      // a pattern upstream went FAIL and its note quoted a filename, which is
      // exactly when someone is reading this panel.
      (det.gate_notes || []).length ? ["div.mt16", { key: "notes" },
        ...det.gate_notes.map((n, i) => ["p.small.muted", { key: "n" + i }, "· ", ...md(n)])] : ["div", { key: "nn" }, ""],
      (det.loud || []).length ? ["div.mt16", { key: "loud" },
        ...det.loud.map((l, i) => callout("note", "gate note — " + l.section, [l.message]))] : ["div", { key: "nl" }, ""],
    ],

    ["div.section", { key: "docs" },
      ["h2", "The pattern's own files"],
      ["p.section-note", ...md("Copied verbatim at build time. `NOTES.md` is written by the engineer who took the measurements and is where every number on this page is argued; `spec.md` is the contract the gate enforces.")],
      ...(docs && docs !== "loading"
        ? ["readme", "spec", "notes"].filter(k => docs[k]).map(k => ["details.fold", { key: "doc" + k },
            ["summary", `${docs[k].file}  ·  ${fmt(Math.round(docs[k].text.length / 1024))} KB`],
            ["div.fold-body", ["pre.code", { style: "max-height:600px" }, docs[k].text]],
          ])
        : [["div.loading", { key: "dl" }, "Loading…"]]),
    ],
    footer(),
  ];
}

function wallTable(det) {
  const rows = [];
  RUNG_ORDER.forEach(cell => {
    ["isolated", "whole"].forEach(mode => {
      const c = det.cells[`${cell}/O3/${mode}`];
      if (!c || !c.wall) return;
      const s = c.wall["small.bin"] || {}, l = c.wall["large.bin"] || {};
      rows.push([RUNG_SHORT[cell] + " · " + RUNG_NAME[cell], mode,
        s.min_ms ? s.min_ms.toFixed(2) : "—", s.median_ms ? s.median_ms.toFixed(2) : "—",
        s.spread_pct ? s.spread_pct.toFixed(1) + "%" : "—",
        l.min_ms ? l.min_ms.toFixed(2) : "—", l.median_ms ? l.median_ms.toFixed(2) : "—",
        l.spread_pct ? l.spread_pct.toFixed(1) + "%" : "—"]);
    });
  });
  return dataTable(["rung", "build", "small min ms", "small median", "spread",
    "large min ms", "large median", "spread"], rows, "wall-" + det.id, { num: [2, 3, 4, 5, 6, 7] });
}

function idiomFold(det) {
  const id = det.idiom || {};
  const req = id.required || [], forb = id.forbidden || [];
  const line = (e) => typeof e === "string" ? e : Object.keys(e).map(k => `${k}: ${e[k]}`).join("  |  ");
  return ["details.fold", { key: "idiom" },
    ["summary", `The declared idiom — ${req.length} required spellings, ${forb.length} forbidden`],
    ["div.fold-body",
      ["p", ...md("Each rung is a *spelling*. Without a pinned idiom the difference between two rungs is unattributable, so every pattern declares the tokens each rung must write literally, hashed into the gate record. **The gate checks the declaration is present and audits the spellings; it does not check that the declaration is the right one.**")],
      ["h3", "required"],
      ...req.map((e, i) => ["pre", { key: "rq" + i }, "· " + line(e)]),
      ["h3.mt16", "forbidden"],
      ...forb.map((e, i) => ["pre", { key: "fb" + i }, "· " + line(e)]),
      ["details.fold", { key: "why" },
        ["summary", "why (verbatim from spec.md — this is a research artefact in its own right)"],
        ["div.fold-body", ["pre", id.why || "—"]],
      ],
    ],
  ];
}

// ---------------------------------------------------------------- findings --

function viewFindings() {
  const tags = ["all", "cost", "security", "proof", "method"];
  const list = FINDINGS.filter(f => APP.findTag === "all" || f.tags.includes(APP.findTag));
  return ["div", { key: "fi" },
    ["div.eyebrow", "cross-cutting results"],
    ["h1", "Findings"],
    // ⚠ This line used to read "Twelve results ... Four of them are marked
    // corrected" as a constant, while FINDINGS held fifteen and five. Both
    // counts are derived now; the sentence around them is in content.js.
    ["p.lede", ...md(`${FINDINGS.length} ${FINDINGS_LEDE.a} ${FINDINGS.filter(f => f.status === "corrected").length} ${FINDINGS_LEDE.b}`)],
    ["div.filters.mt16", { key: "f" },
      ["div.field",
        ["span.field-label", "Topic"],
        ["div.seg", ...tags.map(t => ["button" + (APP.findTag === t ? ".on" : ""),
          { key: "t" + t, onclick: () => { APP.findTag = t; renderAll(); } }, t])],
      ],
    ],
    ["div.stack", { key: "list" },
      ...list.map(f => ["div.card", { key: "f" + f.id },
        ["div.row-between",
          ["h3", { key: "h" }, `${f.id}. ${f.title}`],
          ["span.chip" + (f.status === "corrected" ? ".warning" : f.status === "retracted" ? ".critical" : ".good"),
            ["span.dot"], f.status],
        ],
        ["div.prose.mt8", ...f.body.map((b, i) => mdP(b, "b" + i))],
        // a finding may carry a caveat about its own standing; it was being
        // dropped silently, which is the one thing a caveat must never be
        f.caveat ? callout("warn", "Standing of this finding", [f.caveat])
                 : ["div", { key: "nfc" }, ""],
        ["div.inline-list.mt8", ...f.tags.map(t => ["span.chip.tag", { key: "t" + t }, t])],
      ]),
    ],
    ["div.section", { key: "retr" },
      ["h2", "Retracted — do not reinstate"],
      ["p.section-note", ...md("Kept in full, because a retracted claim that vanishes silently is how it gets re-derived. Each of these was published somewhere in the project before it was refuted — several by the person who wrote the rule it broke.")],
      ["div.stack",
        ...RETRACTED.map((r, i) => ["div.callout.retract", { key: "r" + i },
          ["div.callout-h", "✕ " + r[0]],
          ["p", ...md(r[1])],
        ]),
      ],
    ],
    footer(),
  ];
}

// ------------------------------------------------------------------ method --

// The idiom contract, corpus-wide.  Every pattern pins the tokens each rung
// must and must not use, hashed into its gate record — it is what stops a
// comparison being a comparison of two people's spelling habits.  The audit
// counts were in `data/` from the start and shown only as three numbers on a
// pattern page; the number worth publishing is the one that says what the
// audit did NOT check.
function idiomSection() {
  const I = ((APP.data || {}).totals || {}).idiom;
  if (!I || !I.pairs) return ["div", { key: "noidiom" }, ""];
  const n = (APP.data.totals || {}).patterns;
  return ["div.section", { key: "idiom" },
    ["h2", "The idiom contract, and what it does not check"],
    ["p.section-note", ...md(IDIOM.lede)],
    ["div.grid.g4.mt16", { key: "ik" },
      kpi("Spellings pinned", fmt(I.spellings), `across ${n} patterns · **${fmt(I.pairs)}** spelling × rung pairs checked`),
      kpi("Forbidden spellings found", fmt(I.forbidden_hits), `of **${fmt(I.forbidden_spellings)}** declared forbidden — nothing a pattern rules out appears in any rung`,
        I.forbidden_hits ? "crit" : "good"),
      kpi("Declared but never checked", fmt(I.forbidden_unaudited_entries),
        "entries written as prose with no quoted spelling, so **no** mechanical check ran on them",
        I.forbidden_unaudited_entries ? "warn" : "good"),
      kpi("Pins nothing", fmt(I.required_pins_nothing),
        `required entries present in no rung of a language they name · **${fmt(I.required_absent)}** more are scoped to some rungs and not others`),
    ],
    callout("note", IDIOM.readHead, IDIOM.read),
  ];
}

// ------------------------------------------------------------------ paper --
// The report tab renders `paper_vers/ver_X/` through paper.js. A version is a
// FRAMING, not a draft — see paper_vers/README.md — so the switcher here picks
// between arguments over the same evidence, and git carries the revisions.

async function loadPaper(v) {
  if (CACHE.paper[v]) return CACHE.paper[v];
  CACHE.paper[v] = "loading";
  try {
    const res = await fetch(`./data/paper/${v}.json`, { cache: "no-store" });
    CACHE.paper[v] = await res.json();
  } catch (e) {
    CACHE.paper[v] = { error: String(e) };
  }
  renderAll();
  return CACHE.paper[v];
}

// The figures a paper may embed. Each draws from the same data the rest of the
// site does, so a figure and the tab it came from cannot disagree — and a
// figure id the build does not know is a build error, not a blank box.
function paperFigure(id) {
  const d = APP.data;
  if (id === "ladder") return ladderViz();

  // the layout control, as a figure rather than the whole Cost-tab section
  if (id === "spread") {
    const L = d.layout || {};
    const pairs = (L.pairs || []);
    if (!pairs.length || !L.identical) return ["div.pp-figmiss", { key: "f" }, "layout control unavailable"];
    return chartSpread({
      key: "f-spread",
      title: "Rung-to-rung wall clock across builds of identical machine code",
      sub: "Each row is one comparison; the band is its range over every layout, each tick one build, the centre line zero.",
      rows: pairs.map(p => ({
        name: `${RUNG_SHORT[p.a]} − ${RUNG_SHORT[p.b]} · ${p.input}`,
        min: p.min, max: p.max, neg: p.neg, pos: p.pos, n: p.n, values: p.values,
        posSw: sw(p.a), negSw: sw(p.b),
      })),
      valueFmt: (v) => (v >= 0 ? "+" : "") + v.toFixed(2) + "%",
      legend: Object.keys(L.rungs || {}).map(r => ({ sw: sw(r), label: RUNG_SHORT[r] + " dearer" })),
      foot: "Source: `" + (L.source || "") + "`.",
    });
  }

  // what each rung does under hostile input, as counts rather than the matrix
  if (id === "outcomes") {
    const cells = RUNG_ORDER.filter(c => d.patterns.some(p => (p.adversarial.worst_by_cell || {})[c]));
    const rows = cells.map(c => {
      const tally = {};
      d.patterns.forEach(p => {
        const k = (p.adversarial.worst_by_cell || {})[c];
        if (k) tally[k] = (tally[k] || 0) + 1;
      });
      const n = Object.values(tally).reduce((a, b) => a + b, 0);
      return [RUNG_SHORT[c] + " " + RUNG_NAME[c],
        { jsonml: ["span.inline-list", ...Object.keys(tally).sort().map(k =>
          ["span.chip." + (CLASS_TONE[k] || "other"), { key: "t" + k }, ["span.dot"],
           `${CLASS_ICON[k]} ${CLASS_LABEL[k]} — ${tally[k]}`])] },
        String(n)];
    });
    return dataTable(["rung", "worst behaviour observed, over patterns", "patterns"],
      rows, "f-out", { num: [2], wrap: [1] });
  }

  if (id === "identity") {
    const eq = d.patterns.filter(p => p.identity_o3.equal).length;
    // `dataTable` renders a plain string cell raw, so a label with markdown in
    // it prints its own punctuation — wrap anything with markup as jsonml.
    return dataTable(["", "patterns"], [
      [{ jsonml: ["span", ...md("R4 and R5 kernels byte-identical at `-O3`")] }, String(eq)],
      ["identical only with pc-relative displacements masked", String(d.totals.patterns - eq)],
      ["proof obligations discharged for the shipped rungs", fmt(d.totals.verus_verified)],
      ["verification errors", String(d.totals.verus_errors)],
    ], "f-id", { num: [1] });
  }

  if (id === "tcb") {
    return dataTable(["", "pattern", "obligations", "trusted items", "trusted lines", "twins"],
      d.patterns.map(p => [pid(p.id), pname(p.id), p.verus.verified,
                           p.verus.tcb_items, p.verus.tcb_lines, p.verus.twins]),
      "f-tcb", { num: [2, 3, 4, 5] });
  }

  // the safety tax, per pattern, at the default view: R3 against R4
  if (id === "rungcost") {
    const KEY = "isolated/small.bin";
    const rows = d.patterns.map(p => {
      const t = (p.tax || {})[KEY];
      const c = t && t.cells && t.cells.safe_tuned;
      return c ? { name: pid(p.id), value: c.delta } : null;
    }).filter(Boolean).sort((a, b) => a.value - b.value);
    if (!rows.length) return ["div.pp-figmiss", { key: "f" }, "no tax data"];
    return chartDiverging({
      key: "f-rc", rows,
      title: "Tuned safe Rust against unsafe Rust, per pattern",
      sub: "Executed instructions per call, `-O3`, isolated inlining, `small.bin`. Positive means the safe rung executes more.",
      valueFmt: (v) => (v >= 0 ? "+" : "") + v.toFixed(0),
      posSw: ".sw-safe_tuned", negSw: ".sw-unsafe",
      posLabel: "R3 dearer", negLabel: "R4 dearer",
      foot: "One input and one inlining mode — the pattern pages carry the rest, and each pattern declares which `Ir` convention it is in.",
    });
  }
  return ["div.pp-figmiss", { key: "f-none" }, "no figure `" + id + "`"];
}

// ─────────────────────────────────────────────────────────── the talk ──
//
// A 45-minute deck, rendered as a 16:9 banner at the top of the paper and
// expandable to the whole viewport.  It is BUILT ON EVERY RENDER on purpose:
// `SLIDES.build` hands the deck body a live-data helper, so every count in the
// talk resolves against data/index.json the same way the paper's `\num{}` does
// and the two cannot drift apart.  Forty-two slides is cheap to rebuild.
//
// ⚠ The deck resolves `totals.passing.*`, not `totals.*` — see
// `paper_vers/README.md`.  A talk that quietly counts a half-built failing
// pattern is the same defect as a paper that does.
function deckBanner() {
  if (!APP.data || typeof SLIDES === "undefined" || typeof SLIDES_DECK !== "function")
    return ["div", { key: "deckoff" }, ""];
  let deck;
  try {
    deck = SLIDES.build(SLIDES_DECK, APP.data);
  } catch (e) {
    // A slide missing its question throws by design.  Say so on the page
    // rather than rendering a deck with an unmotivated slide in it.
    return callout("warn", "The talk did not build", [String(e && e.message || e)]);
  }
  const last = deck.slides.length - 1;
  const go = (n) => { APP.slide = Math.max(0, Math.min(last, n)); renderAll(); };
  return ["div.deck-wrap" + (APP.deckFull ? ".is-full" : ""), { key: "deckwrap" },
    ["div.deck-cap", { key: "cap" },
      ["span.deck-caplab", "the talk"],
      ["span.deck-captext", "the same argument in 45 minutes — every slide is a question from the floor"]],
    SLIDES.view(deck, {
      i: APP.slide, full: APP.deckFull,
      on: {
        prev: () => go(APP.slide - 1),
        next: () => go(APP.slide + 1),
        toggleFull: () => { APP.deckFull = !APP.deckFull; renderAll(); },
      },
    }),
  ];
}

// Arrow keys and Escape, but only while the deck owns the viewport — otherwise
// they would fight the page's own scrolling.
if (typeof document !== "undefined" && document.addEventListener) {
  document.addEventListener("keydown", (e) => {
    if (!APP.deckFull) return;
    const k = e.key;
    if (k === "Escape") { APP.deckFull = false; renderAll(); }
    else if (k === "ArrowRight" || k === " " || k === "PageDown") { APP.slide++; renderAll(); }
    else if (k === "ArrowLeft" || k === "PageUp") { APP.slide = Math.max(0, APP.slide - 1); renderAll(); }
    else return;
    if (e.preventDefault) e.preventDefault();
  });
}

function viewPaper() {
  if (!APP.data) return ["div.loading", "Loading…"];
  const vers = APP.data.paper || {};
  const ids = Object.keys(vers).sort();
  if (!ids.length) {
    return ["div", { key: "pp" },
      ["div.eyebrow", "the write-up"],
      ["h1", "Paper"],
      callout("note", "No version yet",
        ["Nothing under `paper_vers/`. A version is a directory `ver_X` holding `meta.json`, `paper.md` and its sections — the format is in `paper_vers/README.md`."])];
  }
  // A version is a framing, and framings do not supersede each other — but one
  // of them is the one the project currently argues, and a reader landing here
  // should get that one rather than whichever sorts first. `"current": true` in
  // meta.json says which; with none set, the alphabetically last wins, so the
  // newest directory is the default by default.
  const marked = ids.filter(v => ((vers[v].meta || {}).current));
  const dflt = marked.length ? marked[marked.length - 1] : ids[ids.length - 1];
  const cur = ids.includes(APP.paperVer) ? APP.paperVer : dflt;
  const doc = CACHE.paper[cur];
  if (!doc) { loadPaper(cur); }
  const meta = (vers[cur] || {}).meta || {};
  const stats = (vers[cur] || {}).stats || {};

  const rendered = (doc && doc !== "loading" && !doc.error)
    ? PAPER.render(doc, { patterns: APP.data.patterns, figure: paperFigure })
    : null;

  return ["div.pp", { key: "pp" },
    deckBanner(),
    ["div.eyebrow", "the write-up · " + (meta.status || "draft")],
    ["h1.pp-title", meta.title || cur],
    meta.subtitle ? ["p.pp-sub", { key: "sub" }, ...md(meta.subtitle)] : ["div", { key: "ns" }, ""],

    ["div.pp-bar", { key: "bar" },
      ids.length > 1
        ? ["div.field", ["span.field-label", "framing"],
            ["div.seg", ...ids.map(v => ["button" + (v === cur ? ".on" : ""),
              { key: "v" + v, onclick: () => { APP.paperVer = v; renderAll(); } },
              ((vers[v].meta || {}).short || v)])]]
        : ["span.chip.tag", { key: "only" }, cur],
      ["span.chip.tag", { key: "w" }, fmt(stats.words || 0) + " words"],
      ["span.chip.tag", { key: "s" }, (stats.sections || 0) + " sections"],
      ["span.chip.tag", { key: "p" }, (stats.principles || 0) + " principles · " + (stats.examples || 0) + " examples"],
      stats.todos ? ["span.chip.warning", { key: "t" }, ["span.dot"], stats.todos + " todo"] : ["span", { key: "nt" }, ""],
    ],

    // Source errors are build errors and the build already warned; showing them
    // here too is deliberate, because this is the page where they are actionable.
    (doc && doc.errors && doc.errors.length)
      ? callout("warn", `${doc.errors.length} source error(s) in this version`,
          ["The build could not resolve these, so the paper below renders around them:"]
            .concat(doc.errors.map(e => "· " + e)))
      : ["div", { key: "ne" }, ""],

    // The framing statement used to render HERE, as an open callout above the
    // title's own first sentence — so the first thing a reader met was several
    // hundred words of editorial about which version this is and how it differs
    // from the ones before it.  It now sits collapsed at the BOTTOM, below the
    // references, because THE PAPER HAS TO BE SELF-CONTAINED: a reader of the
    // report is owed the report, not its revision history.  Do not move it back
    // up, and do not open it by default.
    !doc || doc === "loading" ? ["div.loading", { key: "l" }, "Loading the paper…"]
      : doc.error ? callout("warn", "Could not load this version", [String(doc.error)])
      : ["div.pp-layout", { key: "lay" },
          ["nav.pp-outline", { key: "out" },
            ["div.eyebrow", "contents"],
            // ⚠ md() IS NOT OPTIONAL HERE.  A section title is rendered TWICE —
            // once as the h2/h3, which goes through paper.js's inline(), and
            // once here.  This path used to push the raw `o.text`, so a code
            // span in any heading reached the page as literal backticks and
            // check.mjs failed — with the count DOUBLED, because both copies of
            // the title leak.  Headings are prose; prose runs through md().
            ...rendered.outline.map((o, i) => ["a.pp-ol" + (o.level === 2 ? ".sub" : ""),
              { key: "o" + i, href: "#paper/" + o.num },
              ["span.pp-olnum", o.num], " ", ...md(o.text)]),
          ],
          ["article.pp-body", { key: "body" }, ...rendered.body],
        ],

    doc && doc !== "loading" && doc.refs && Object.keys(doc.refs).length
      ? ["div.section", { key: "bib" },
          ["h2", "References"],
          ["div.pp-bib", { id: "pp-bib" },
            ...Object.keys(doc.refs).sort().map(k => ["div.pp-bibitem", { key: "b" + k },
              ["span.pp-bibkey", "[" + (doc.refs[k].short || k) + "]"],
              ["span", " " + (doc.refs[k].text || doc.refs[k].title || "")],
            ])],
        ]
      : ["div", { key: "nb" }, ""],

    // Editorial, collapsed, and last. See the note above the body.
    meta.framing
      ? ["details.fold.mt16", { key: "framing" },
          ["summary", "Editorial note — how this version is built, and why"],
          ["div.pp-framing", ...md(meta.framing)]]
      : ["div", { key: "nf" }, ""],

    footer(),
  ];
}

// Where the cross-cutting results came from, and how far they have been tested.
//
// The research derived its four results from a smaller corpus than the one that
// exists now, then re-derived every one of them against the whole thing and
// published the out-of-sample verdicts. That is a good outcome and an unusual
// one — and it is exactly the kind of fact a report is tempted to leave out,
// because "derived on 26, holds on 33" reads worse at a glance than "33".
// Folded, with the count derived so it cannot go stale.
// Which patterns exist, and who decided. The advisor's first question, and the
// site had no answer on any tab — while the research tree has a frank one.
function selectionNote() {
  const t = (APP.data || {}).totals || {};
  if (!t.catalogue || !t.patterns) return ["div", { key: "nosel" }, ""];
  return ["div.section", { key: "sel" },
    ["h2", "Which patterns exist, and how they were chosen"],
    ["p.section-note", ...md(
      `**${t.patterns} of ${t.catalogue}** catalogued candidates were built. `
      + SELECTION.lede)],
    ["details.fold", { key: "selfold" },
      ["summary", "How the rest were decided — including the rule that was withdrawn"],
      ["div.fold-body",
        ["div.prose", ...SELECTION.body.map((b, i) => mdP(b, "sl" + i))],
      ],
    ],
  ];
}

function provenanceNote() {
  const t = (APP.data || {}).totals || {};
  const p = t.passing || {};
  const derived = p.analysed;
  const now = t.patterns_passing || t.patterns;
  if (!derived || !now || derived === now) return ["div", { key: "noprov" }, ""];
  return ["div.section", { key: "prov-note" },
    ["h2", "Where the cross-cutting results came from"],
    ["details.fold", { key: "provfold" },
      ["summary", `The four results were derived from ${derived} of these ${now} patterns, then re-tested against all ${now} — what happened`],
      ["div.fold-body",
        ["div.prose", ...PROVENANCE.body.map((b, i) => mdP(b, "pv" + i))],
        dataTable(["result", "verdict out of sample"], PROVENANCE.verdicts, "provtbl", { wrap: [1] }),
        callout("warn", PROVENANCE.warnHead, PROVENANCE.warn),
      ],
    ],
  ];
}

// Split the build's own warnings into the ones a READER needs and the ones the
// site's maintainer needs. Nothing is dropped — the maintainer's are folded,
// verbatim — because a warning that disappears is the failure this whole
// mechanism exists to prevent.
function buildNotes(warnings) {
  const readerish = /licensed|licence|synthesis|gate did not pass|missing/i;
  const reader = warnings.filter(w => readerish.test(w));
  const maint = warnings.filter(w => !readerish.test(w));
  return ["div", { key: "warnbox" },
    reader.length
      ? callout("note", "Two things the build wants you to know about scope",
          ["These are printed by the build itself, from the evidence:"].concat(reader.map(w => "· " + w)))
      : ["div", { key: "nr" }, ""],
    maint.length
      ? ["details.fold.mt16", { key: "mw" },
          ["summary", `${maint.length} further build note(s) — for whoever maintains this page`],
          ["div.fold-body",
            ["p.small.muted", ...md("Housekeeping the build emits about its own inputs: figures frozen by hand in a draft, and evidence keys that exist but are not drawn. Kept visible rather than silenced, because a warning nobody sees is how a page goes quietly stale.")],
            ...maint.map((w, i) => ["p.small.muted", { key: "mwx" + i }, ...md("· " + w)])],
        ]
      : ["div", { key: "nm" }, ""],
  ];
}

function viewMethod() {
  if (!APP.data) return ["div.loading", "Loading…"];
  return ["div", { key: "me" },
    ["div.eyebrow", "how the numbers were made, and what they are not"],
    ["h1", "Method & caveats"],
    ["p.lede", ...md("A benchmark that reports one number per language is measuring its author's spelling habits. This section is the part of the study that makes the numbers arguable — which is the only thing that makes them useful.")],

    ["div.section", { key: "m" },
      ...METHOD.map((s, i) => ["div", { key: "m" + i },
        ["h2" + (i ? ".mt28" : ""), s.h],
        ["div.prose", ...s.p.map((p, j) => mdP(p, "p" + j))],
      ]),
    ],

    selectionNote(),
    provenanceNote(),
    idiomSection(),

    ["div.section", { key: "traps" },
      ["h2", "The recurring traps"],
      ["p.section-note", ...md("Written down because every one of them cost a published number. They are as transferable as any result here.")],
      ["div.grid.g2.mt16",
        ...TRAPS.map((t, i) => ["div.card", { key: "tr" + i },
          ["h3", t[0]],
          ["p.small.muted", { key: "b" }, ...md(t[1])],
        ]),
      ],
    ],

    ["div.section", { key: "warn" },
      (APP.data.warnings || []).length
        // ⚠ These are the BUILD's warnings, and most of them are addressed to
        // whoever maintains this site, not to a reader — a `%%literal-ok` note
        // about a frozen figure in a draft reads as disrepair on a public page
        // while meaning nothing. Reader-facing ones stay visible; the rest go
        // behind a fold, still complete, still unedited.
        ? buildNotes(APP.data.warnings)
        : ["div", { key: "ok" }, ""],
    ],

    ["div.section", { key: "prov" },
      ["h2", "Provenance"],
      provenanceTable(),
      ["p.small.muted.mt16", ...md("The measurement protocol recorded with the data: " +
        `\`${(APP.data.protocol || {}).static || ""}\`; \`${(APP.data.protocol || {}).ir || ""}\`; \`${(APP.data.protocol || {}).wall || ""}\`.`)],
    ],
    footer(),
  ];
}

// ================================================================= tooltip ==

function wireTooltip() {
  const tipEl = document.getElementById("tip");
  let cur = null;
  document.addEventListener("pointermove", (e) => {
    const t = e.target.closest ? e.target.closest("[data-tip]") : null;
    if (!t) {
      if (cur) { tipEl.classList.remove("on"); cur = null; }
      return;
    }
    if (t !== cur) {
      cur = t;
      tipEl.textContent = t.getAttribute("data-tip");   // untrusted text — never innerHTML
      tipEl.classList.add("on");
    }
    const pad = 12;
    tipEl.style.left = Math.min(window.innerWidth - 20, Math.max(20, e.clientX)) + "px";
    tipEl.style.top = Math.max(40, e.clientY - pad) + "px";
  }, { passive: true });
  document.addEventListener("pointerleave", () => { tipEl.classList.remove("on"); cur = null; });
}

// ============================================================ initialization ==

function main_init() {
  ELEMS.app = UI.$id("app");
  _sc = UI.createSmartConfirm(UI.$id("sc-backdrop"), UI.$id("sc-dialog"));
  try {
    const saved = localStorage.getItem("slb-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) {}
  initRungs();
  wireTooltip();
  readHash();
  window.addEventListener("hashchange", () => {
    if (_hashSelf) { _hashSelf = false; return; }
    readHash();
    renderAll();
  });
  renderAll();
  loadIndex();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", main_init);
} else {
  main_init();
}
