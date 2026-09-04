// responsive_audit.mjs — does any grid demand more width than the viewport has?
//
//   node tools/responsive_audit.mjs
//
// check.mjs validates the JSONML tree and never sees a stylesheet, and headless
// Firefox does not complete a capture on this box, so neither of the two gates
// can catch the one CSS failure that matters at narrow widths: a grid whose
// fixed tracks add up to more than the container, which pushes the page into a
// horizontal scroll and cuts content off at the right edge.
//
// That failure is arithmetic, so it can be checked without rendering anything.
// For each target viewport this resolves the cascade over `grid-template-columns`
// (later rule wins; `@media (max-width: N)` applies when N >= viewport), sums
// the tracks that cannot shrink, adds the column gaps, and compares the total to
// the width actually available at that nesting depth.
//
// WHAT THIS PROVES: no grid overflows its container at the listed widths.
// WHAT IT DOES NOT PROVE: that the result looks good, that type is legible, or
// that anything is where a reader would want it.  Only eyes do that.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const WEB = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
// optional path argument, so the audit can be pointed at an older revision of
// the stylesheet to confirm it still reports the faults that were there
const css = fs.readFileSync(process.argv[2] || path.join(WEB, "index.css"), "utf8");

// ---------------------------------------------------------------- parse ----
// Flatten to {media, selector, decls} in source order.  Only max-width queries
// matter here; colour-scheme queries are irrelevant to layout.
function parse(src) {
  // Strip comments FIRST.  Without this a `/* ... */` sitting above a rule is
  // captured as part of the selector text, so `.dbar-row` in that rule silently
  // stops matching `.dbar-row` — which is exactly the false negative that made
  // this audit report a stacked row as un-stacked.
  src = src.replace(/\/\*[\s\S]*?\*\//g, "");
  const out = [];
  const re = /(?:@media([^{]+)\{)|([^{}@]+)\{([^{}]*)\}|(\})/g;
  let media = null, depth = 0, m;
  while ((m = re.exec(src))) {
    if (m[1] !== undefined) { media = m[1].trim(); depth++; }
    else if (m[4] !== undefined) { if (depth > 0) { depth--; if (!depth) media = null; } }
    else if (m[2] !== undefined) {
      const decls = {};
      for (const d of m[3].split(";")) {
        const i = d.indexOf(":");
        if (i > 0) decls[d.slice(0, i).trim()] = d.slice(i + 1).trim();
      }
      for (const sel of m[2].split(",")) out.push({ media, sel: sel.trim(), decls });
    }
  }
  return out;
}

const RULES = parse(css);

// a rule applies at `vw` if it has no media query, or a max-width that covers it
function applies(media, vw) {
  if (!media) return true;
  if (/prefers-color-scheme/.test(media)) return false;
  const mw = /max-width:\s*(\d+)px/.exec(media);
  return mw ? vw <= +mw[1] : false;
}

// last declaration wins, exactly as the cascade would for equal specificity
function resolve(selector, prop, vw) {
  let v = null;
  for (const r of RULES) {
    if (r.sel !== selector || !applies(r.media, vw)) continue;
    if (r.decls[prop] !== undefined) v = r.decls[prop];
  }
  return v;
}

// ------------------------------------------------------ track arithmetic ----
// The width a track cannot go below.  `min(Xpx, 100%)` and every flexible unit
// yield entirely; a bare px value and a bare minmax() floor do not.
function trackMin(tok) {
  tok = tok.trim();
  if (!tok) return null;
  if (/^min\s*\(/.test(tok)) return 0;                    // min(Npx, 100%) — yields
  if (/^minmax\s*\(/.test(tok)) {
    const inner = tok.slice(tok.indexOf("(") + 1, tok.lastIndexOf(")"));
    return trackMin(splitTop(inner)[0]);                  // the floor is the minimum
  }
  if (/^repeat\s*\(/.test(tok)) {
    const inner = tok.slice(tok.indexOf("(") + 1, tok.lastIndexOf(")"));
    const parts = splitTop(inner);
    // auto-fit/auto-fill can always drop to a single track
    return trackMin(parts.slice(1).join(","));
  }
  const px = /^(\d+(?:\.\d+)?)px$/.exec(tok);
  if (px) return +px[1];
  return 0;                                               // fr, auto, %, min-content
}

// split on commas / spaces that are not inside parentheses
function splitTop(s, sep = ",") {
  const out = []; let d = 0, cur = "";
  for (const ch of s) {
    if (ch === "(") d++;
    if (ch === ")") d--;
    if (ch === sep && !d) { out.push(cur); cur = ""; continue; }
    cur += ch;
  }
  if (cur.trim()) out.push(cur);
  return out;
}

function tracks(tpl) {
  // top-level space-separated tokens, parens respected
  const out = []; let d = 0, cur = "";
  for (const ch of tpl) {
    if (ch === "(") d++;
    if (ch === ")") d--;
    if (/\s/.test(ch) && !d) { if (cur.trim()) out.push(cur.trim()); cur = ""; continue; }
    cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

function colGap(sel, vw) {
  const g = resolve(sel, "gap", vw) || resolve(sel, "grid-gap", vw);
  if (!g) return 0;
  const parts = g.trim().split(/\s+/);
  const pick = parts.length > 1 ? parts[1] : parts[0];   // gap: <row> <column>
  const px = /^(\d+(?:\.\d+)?)px$/.exec(pick);
  return px ? +px[1] : 0;
}

// ------------------------------------------------------------- the check ----
// Every selector that ever sets grid-template-columns, with how deeply it nests
// inside padded containers (the padding is spent before the grid sees the width).
const GRIDS = [...new Set(RULES.filter(r => r.decls["grid-template-columns"]).map(r => r.sel))];

// horizontal padding spent before a grid at that nesting depth
const CHART_SELECTORS = /^\.(dbar-row|dumb-row|bar-row|bars)/;
const CARD_SELECTORS = /^\.(lv-head|lv-row)/;

const VIEWPORTS = [1280, 900, 768, 560, 430, 360, 320];

let fail = 0;
console.log("viewport   grid                       needs   has   ");
console.log("--------   ------------------------   -----   -----");

for (const vw of VIEWPORTS) {
  const wrapPad = 2 * (vw <= 400 ? 10 : vw <= 560 ? 13 : vw <= 720 ? 16 : 24);
  for (const sel of GRIDS) {
    // a box that is not rendered cannot overflow — .lv-head is hidden once the
    // ladder rows stack, and its desktop template is left in place on purpose
    if (resolve(sel, "display", vw) === "none") continue;
    const tpl = resolve(sel, "grid-template-columns", vw);
    if (!tpl) continue;
    const ts = tracks(tpl);
    const mins = ts.map(trackMin);
    const n = ts.length;
    const need = mins.reduce((a, b) => a + b, 0) + colGap(sel, vw) * Math.max(0, n - 1);

    // chart rows sit inside .chart's padding; ladder rows inside .ladder-viz
    const inner = CHART_SELECTORS.test(sel) ? 2 * (vw <= 400 ? 13 : vw <= 720 ? 16 : 20)
      : CARD_SELECTORS.test(sel) ? 16 : 0;
    const have = Math.min(vw, 1280) - wrapPad - inner;

    if (need > have) {
      fail++;
      console.log(
        String(vw).padEnd(10), sel.padEnd(26),
        String(Math.round(need)).padStart(5), String(Math.round(have)).padStart(5),
        "  *** OVERFLOWS by " + Math.round(need - have) + "px");
    }
  }
}

if (!fail) console.log("(none)");
else console.log(`${fail} overflow(s).`);

// -------------------------------------------------- how much bar is left ----
// Overflow is the loud failure; this is the quiet one, and it is what actually
// makes a chart unreadable on a phone.  A bar row spends fixed px on its label
// and its value and gives the rest to the mark.  When "the rest" is a sliver,
// the row is still technically laid out and still useless.
const BARS = [".dbar-row", ".dumb-row", ".bar-row"];
console.log("\nshare of each chart row left for the bar itself:\n");
console.log("viewport   " + BARS.map(s => s.padEnd(14)).join(""));
console.log("--------   " + BARS.map(() => "-------------,".slice(0, 14)).join(""));

let thin = 0;
for (const vw of VIEWPORTS) {
  const wrapPad = 2 * (vw <= 400 ? 10 : vw <= 560 ? 13 : vw <= 720 ? 16 : 24);
  const inner = 2 * (vw <= 400 ? 13 : vw <= 720 ? 16 : 20);
  const have = Math.min(vw, 1280) - wrapPad - inner;
  const cells = BARS.map(sel => {
    const tpl = resolve(sel, "grid-template-columns", vw);
    if (!tpl) return "—".padEnd(14);
    const ts = tracks(tpl);
    // a stacked row gives the bar its own line: full width
    const stacked = (resolve(sel, "grid-template-areas", vw) || "").includes("track track");
    const fixed = ts.map(trackMin).reduce((a, b) => a + b, 0)
      + colGap(sel, vw) * Math.max(0, ts.length - 1);
    const bar = stacked ? have : have - fixed;
    const pct = Math.round((bar / have) * 100);
    if (pct < 45) thin++;
    return `${Math.round(bar)}px (${pct}%)`.padEnd(14);
  });
  console.log(String(vw).padEnd(10) + cells.join(""));
}
console.log(thin ? `\n${thin} row/viewport pair(s) leave the bar under 45% of the row.`
  : "\nevery chart row keeps at least 45% of its width for the bar.");

// ------------------------------------------------------- the header shape ---
// The third failure mode, and the one that looked worst on a phone.  `.tabs` is
// `flex: 1` — flex-basis 0 — so when it shares a row with the brand and the
// theme button it is left with whatever they did not take, and eight tabs wrap
// ONE PER LINE into a tall vertical column.  Giving `.tabs` its own row
// (`flex-basis: 100%`) is what fixes it, so that is what this checks.
const TAB_LABELS = ["Overview", "The ladder", "Cost of safety", "Hostile input",
  "Proof & trusted base", "Patterns", "Findings", "Method"];

function padX(sel, vw) {
  const p = resolve(sel, "padding", vw);
  if (!p) return 0;
  const parts = p.trim().split(/\s+/);
  const h = parts.length === 1 ? parts[0] : parts[1];
  const px = /^(\d+(?:\.\d+)?)px$/.exec(h);
  return px ? +px[1] : 0;
}

console.log("\nheader: how the eight tabs lay out\n");
console.log("viewport   tabs row      per row   rows   verdict");
console.log("--------   -----------   -------   ----   -------");

let headerBad = 0;
for (const vw of VIEWPORTS) {
  const pad = 2 * padX(".topbar-in", vw);
  const flex = resolve(".tabs", "flex", vw) || "1";
  const ownRow = /100%/.test(flex);
  const fs = parseFloat((resolve(".tab", "font-size", vw) || "13.5px"));
  const tp = 2 * (parseFloat((resolve(".tab", "padding", vw) || "7px 11px").split(/\s+/)[1]) || 11);
  const gap = 3;
  // the brand (and its subtitle, when shown) plus the theme button
  const subShown = resolve(".brand-sub", "display", vw) !== "none";
  const brand = (subShown ? 230 : 96) + 70 + 24;

  const avail = Math.max(40, vw - pad - (ownRow ? 0 : brand));
  const widths = TAB_LABELS.map(l => l.length * fs * 0.53 + tp);
  let rows = 1, cur = 0, perRow = [];
  let n = 0;
  for (const w of widths) {
    if (cur && cur + gap + w > avail) { rows++; perRow.push(n); cur = 0; n = 0; }
    cur += (cur ? gap : 0) + w; n++;
  }
  perRow.push(n);
  const minPer = Math.min(...perRow);

  // one tab per line is the scramble; more than 4 rows is a header that eats
  // the screen before any content appears
  const bad = minPer < 2 || rows > 4;
  if (bad) headerBad++;
  console.log(
    String(vw).padEnd(10),
    (ownRow ? "own row" : "shared").padEnd(13),
    String(minPer).padStart(4).padEnd(9),
    String(rows).padStart(3).padEnd(6),
    bad ? "*** SCRAMBLED" : "ok");
}
console.log(headerBad
  ? `\n${headerBad} viewport(s) lay the header out badly.`
  : "\nthe header keeps at least two tabs per line at every viewport.");

// -------------------------------------------------------- sticky panes -----
// A `position: sticky` column taller than the viewport cannot be scrolled on
// its own, so reaching its last item means scrolling the whole page — which is
// the one thing sticky was there to avoid.  Any sticky pane holding a list must
// cap its height and carry its own overflow.
const STICKY = [".pat-list"];
console.log("\nsticky panes:");
let stickyBad = 0;
for (const sel of STICKY) {
  for (const vw of VIEWPORTS) {
    if (resolve(sel, "position", vw) !== "sticky") continue;
    const mh = resolve(sel, "max-height", vw);
    const ov = resolve(sel, "overflow-y", vw);
    if (!mh || mh === "none" || !ov || ov === "visible") {
      stickyBad++;
      console.log(`  *** ${sel} at ${vw}px is sticky with max-height:${mh || "unset"} overflow-y:${ov || "unset"}`);
    }
  }
}
console.log(stickyBad ? `  ${stickyBad} unscrollable sticky pane(s).`
  : "  every sticky pane caps its height and scrolls itself.");

// ------------------------------------------------- split-diff alignment ----
// A split diff only lines up if both columns are tracks of the SAME grid.  The
// first version gave every row its own `1fr 1fr` grid with `min-width:
// max-content`, so each row sized to its own content and the column boundary
// landed somewhere different on every line — a long line shoved its right
// column off screen while a short line two rows down started halfway across.
//
// The invariant that prevents it: the container owns the tracks and the rows
// are `display: contents`.  Neither half is checkable by the overflow
// arithmetic above, because nothing overflows — it just misaligns.
console.log("\nsplit diff:");
let splitBad = 0;
{
  const containerTracks = resolve(".difflines.split", "grid-template-columns", 1280);
  const rowDisplay = resolve(".sl", "display", 1280);
  const rowTracks = resolve(".sl", "grid-template-columns", 1280);

  if (!containerTracks) {
    splitBad++; console.log("  *** .difflines.split defines no grid-template-columns — the container must own the tracks");
  } else if (!/minmax\(\s*0/.test(containerTracks)) {
    splitBad++; console.log(`  *** .difflines.split tracks are "${containerTracks}" — need minmax(0, …) or a long line re-widens the column`);
  }
  if (rowDisplay !== "contents") {
    splitBad++; console.log(`  *** .sl display is "${rowDisplay || "unset"}", not contents — rows must join the container's grid`);
  }
  if (rowTracks) {
    splitBad++; console.log(`  *** .sl defines its own grid-template-columns ("${rowTracks}") — that is the per-row-grid bug`);
  }
}
console.log(splitBad ? `  ${splitBad} problem(s).` : "  columns are tracks of one grid; rows join it.");

// ------------------------------------------- auto-placement into a rail -----
// The failure this catches SHIPPED, on the ladder strip at phone width, and no
// check here could see it: nothing overflowed, no track was too narrow, the
// tree was well-formed and every token round-tripped. The row simply had FIVE
// children and TWO columns.
//
// Two separate spec details conspire:
//
//   1. `grid-row: 1 / -1` resolves `-1` against the EXPLICIT grid. With no
//      `grid-template-rows`, `-1` is the first line, so the span collapses to a
//      single row instead of the full card height.
//   2. Whatever the collapsed item no longer covers is free, and the remaining
//      children AUTO-FLOW into it — including a 4px decorative rail column,
//      where text wraps one word per line and overlaps the cell beside it.
//
// The invariant: if a grid has more children than columns, either the template
// has enough columns or EVERY child is explicitly placed. Auto-placement is
// fine; auto-placement into a track sized for a coloured bar is not.
// A child counts as placed if it declares `grid-column` OR `grid-area` — the
// chart rows use named areas, which is the same guarantee by another spelling.
const NARROW = [560, 430, 360, 320];
const PLACED = [
  { parent: ".lv-row", rail: ".lv-rail", decorative: [".lv-rail"],
    children: [".lv-id", ".lv-what", ".lv-check", ".lv-tcb"], narrowAt: NARROW },
  // these three are CORRECT and are here as regression guards: every child is
  // pinned to a named area, so nothing auto-flows
  { parent: ".dbar-row", children: [".dbar-name", ".dbar-track", ".dbar-val"], narrowAt: NARROW },
  { parent: ".dumb-row", children: [".dbar-name", ".dumb-track", ".dumb-val"], narrowAt: NARROW },
  { parent: ".bar-row", children: [".bar-lab", ".bar-track", ".bar-val"], narrowAt: NARROW },
  // and this one places its third child across both columns explicitly, which
  // is the idiom .lv-row should have used from the start
  { parent: ".vleg-row", children: [".vleg-key", ".vleg-name", ".vleg-blurb"], narrowAt: NARROW },
];
console.log("\nauto-placement:");
let placeBad = 0;
for (const g of PLACED) {
  for (const vw of g.narrowAt) {
    if (resolve(g.parent, "display", vw) === "none") continue;
    const tpl = resolve(g.parent, "grid-template-columns", vw);
    if (!tpl) continue;
    const ts = tracks(tpl);
    const mins = ts.map(trackMin);
    const ncols = ts.length;

    // `grid-template-areas` places children by name; that is placement too
    const areas = resolve(g.parent, "grid-template-areas", vw);
    const rows = resolve(g.parent, "grid-template-rows", vw) || areas;
    const span = g.rail ? (resolve(g.rail, "grid-row", vw) || "") : "";
    if (/-1\s*$/.test(span) && !rows) {
      placeBad++;
      console.log(`  *** ${vw}px ${g.parent}: ${g.rail} spans "${span}" but ${g.parent} declares no grid-template-rows`
        + " — `-1` resolves to the first line and the span collapses");
    }

    // Auto-flow the unplaced children row-major and see where each LANDS.
    // Auto-placement is not the defect — landing in a decorative track is.
    // A 4px rail column cannot hold a sentence; a 104px label column is just
    // the next row, which is what stacking is supposed to look like.
    // ⚠ Decorative means a FIXED small track. `1fr` has a minimum of 0 and is
    // the widest thing in the row — judging by trackMin() alone calls every
    // flexible column decorative and flags the whole page.
    const DECORATIVE_PX = 24;
    const isDecorative = (tok) => /^\d+(\.\d+)?px$/.test(tok.trim()) && parseFloat(tok) <= DECORATIVE_PX;
    const order = (g.rail ? [g.rail] : []).concat(g.children);
    let slot = 0;
    for (const c of order) {
      if (resolve(c, "grid-column", vw) || resolve(c, "grid-area", vw)) continue;
      const col = slot % ncols;
      slot++;
      if (isDecorative(ts[col]) && !(g.decorative || []).includes(c)) {
        placeBad++;
        console.log(`  *** ${vw}px ${g.parent}: ${c} auto-flows into column ${col + 1}, `
          + `a fixed ${ts[col].trim()} track — text there wraps one word per line`);
      }
    }
  }
}
console.log(placeBad ? `  ${placeBad} problem(s).`
  : "  every child of a short-column grid is placed explicitly.");

process.exit(fail || headerBad || stickyBad || splitBad || placeBad ? 1 : 0);
