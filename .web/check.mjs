// render_check.mjs — run every view function of index.js against the real data
// in a stubbed DOM, and validate the JSONML trees they return.
//
// Catches: syntax errors, bad data-shape assumptions, `null` children (LESSONS #1),
// missing tag strings, attrs objects in the wrong slot, and any throw inside a view.
//
//   node check.mjs           # renders every view; must print OK
//   node check.mjs --snap    # also freeze .temp/snap-*.html, which is what to screenshot
//
// It writes nothing except the optional --snap files under .temp/.
//
// WHAT IT DOES NOT DO: it does not load index.css.  A stylesheet regression --
// a deleted rule, a swatch class removed with the block around it -- passes this
// check silently.  Screenshot after any CSS change.

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const WEB = path.dirname(fileURLToPath(import.meta.url));

const listeners = [];
const mkEl = () => ({
  classList: { add() {}, remove() {}, contains: () => false },
  style: {}, dataset: {}, textContent: "",
  setAttribute() {}, getAttribute: () => null, removeAttribute() {},
  addEventListener() {}, appendChild() {}, closest: () => null,
});

const documentStub = {
  readyState: "complete",
  documentElement: mkEl(),
  getElementById: () => mkEl(),
  querySelector: () => mkEl(),
  querySelectorAll: () => [],
  addEventListener: (t, f) => listeners.push([t, f]),
  createElement: () => mkEl(),
  body: mkEl(),
};

let renderCount = 0;
const sandbox = {
  console: { log() {}, warn: console.warn, error: console.error },
  document: documentStub,
  window: { scrollTo() {}, innerWidth: 1440, innerHeight: 900, addEventListener() {} },
  localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  setTimeout, clearTimeout, Math, Date, JSON, Object, Array, String, Number, Boolean,
  location: { hash: "" },
  decodeURIComponent, encodeURIComponent,
  fetch: async (url) => {
    const rel = String(url).replace(/^\.\//, "");
    const file = path.join(WEB, rel);
    if (!fs.existsSync(file)) return { ok: false, status: 404, json: async () => ({}) };
    return { ok: true, status: 200, json: async () => JSON.parse(fs.readFileSync(file, "utf8")) };
  },
  UI: {
    $id: () => mkEl(),
    debounce: (f) => f,
    render_patch: (el, fn) => { renderCount++; LAST = typeof fn === "function" ? fn() : fn; },
    createSmartConfirm: () => ({ show: async () => ({ confirmed: false }) }),
  },
};
let LAST = null;
sandbox.window.UI = sandbox.UI;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

for (const f of ["syntax.js", "diff.js", "paper.js", "slides.js", "slides_deck.js", "content.js", "index.js"]) {
  const src = fs.readFileSync(path.join(WEB, f), "utf8");
  try {
    vm.runInContext(src, sandbox, { filename: f });
  } catch (e) {
    console.error(`FAIL: ${f} threw at load: ${e.stack.split("\n").slice(0, 3).join("\n")}`);
    process.exit(1);
  }
}

// ---------------------------------------------------------------- validation --

const problems = [];
let nodes = 0;

function walk(node, where) {
  nodes++;
  if (node === null) { problems.push(`${where}: null child (LESSONS #1)`); return; }
  if (node === undefined) return;                       // ignored by jsonml2idom
  if (typeof node === "string" || typeof node === "number" || typeof node === "boolean") return;
  if (!Array.isArray(node)) { problems.push(`${where}: child is ${typeof node} (${JSON.stringify(node).slice(0, 60)})`); return; }
  if (typeof node[0] !== "string") { problems.push(`${where}: element[0] is not a tag string (${JSON.stringify(node[0]).slice(0, 60)})`); return; }
  if (/className/.test(JSON.stringify(node[1] || {}))) problems.push(`${where}: className in attrs (LESSONS #11)`);
  const tag = node[0];
  for (let i = 1; i < node.length; i++) {
    const c = node[i];
    if (i === 1 && c && typeof c === "object" && !Array.isArray(c)) continue;  // attrs
    if (c && typeof c === "object" && !Array.isArray(c)) {
      problems.push(`${where}/${tag}: plain object in child slot ${i}`);
      continue;
    }
    walk(c, `${where}/${tag}[${i}]`);
  }
}

// ------------------------------------------------------------ JSONML -> HTML --

const VOID = new Set(["br", "hr", "img", "input", "meta", "link"]);
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function toHTML(node) {
  if (node === undefined || node === null) return "";
  if (typeof node !== "object") return esc(node);
  if (!Array.isArray(node)) return "";
  const spec = node[0];
  const m = /^([a-zA-Z0-9]+)((?:[.#][^.#]+)*)$/.exec(spec) || [null, "div", ""];
  const tag = m[1] || "div";
  const classes = (m[2].match(/\.[^.#]+/g) || []).map(c => c.slice(1));
  const ids = (m[2].match(/#[^.#]+/g) || []).map(c => c.slice(1));
  let attrs = "", start = 1;
  if (node[1] && typeof node[1] === "object" && !Array.isArray(node[1])) {
    start = 2;
    for (const [k, v] of Object.entries(node[1])) {
      if (k === "key" || k === "skip" || typeof v === "function" || v === undefined) continue;
      attrs += ` ${k}="${esc(v)}"`;
    }
  }
  const open = `<${tag}${ids.length ? ` id="${ids[0]}"` : ""}${classes.length ? ` class="${classes.join(" ")}"` : ""}${attrs}>`;
  if (VOID.has(tag)) return open;
  let inner = "";
  for (let i = start; i < node.length; i++) inner += toHTML(node[i]);
  return open + inner + `</${tag}>`;
}

// ------------------------------------------------------------ contact sheet --
//
// Every check in this repo is structural: they prove the tree is well-formed,
// that no grid overflows and that no token stream is mangled.  None of them can
// see whether the page is LEGIBLE, and headless capture does not work on this
// box — a trivial 80-byte page hangs the same way the real one does, so it is
// the browser build and not the content.
//
// So the visual pass belongs to a human, and this makes it one file to open
// instead of twenty-odd.  It frames every snapshot in an iframe at a chosen
// width, in either theme, at the four breakpoints the stylesheet actually has.
// The narrow widths matter most: they are the ones no one has ever looked at.
function contactSheet(names) {
  const WIDTHS = [1440, 900, 720, 560, 400];
  const opt = (v, sel) => `<option value="${v}"${v === sel ? " selected" : ""}>${v}px</option>`;
  const rows = names.map(n => `<section><h2>${esc(n)}</h2>`
    + `<iframe data-snap="${esc(n)}" src="snap-${esc(n)}.html" loading="lazy"></iframe></section>`).join("\n");
  return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>sec-ladder — visual review sheet</title>
<style>
  body { margin:0; font:14px/1.5 system-ui, sans-serif; background:#1b1d22; color:#e6e8ee; }
  header { position:sticky; top:0; z-index:9; display:flex; gap:16px; align-items:center;
           flex-wrap:wrap; padding:10px 16px; background:#111318; border-bottom:1px solid #333; }
  header b { font-size:15px; } label { display:flex; gap:6px; align-items:center; }
  select, button { font:inherit; padding:3px 8px; }
  .hint { opacity:.65; font-size:12px; }
  section { padding:18px 16px 4px; border-bottom:1px solid #2a2d34; }
  h2 { margin:0 0 8px; font:600 13px/1 ui-monospace, monospace; letter-spacing:.04em;
       text-transform:uppercase; opacity:.8; }
  iframe { width:1440px; height:900px; border:1px solid #3a3d45; background:#fff;
           display:block; resize:vertical; }
</style></head><body>
<header>
  <b>visual review sheet</b>
  <label>width <select id="w">${WIDTHS.map(w => opt(w, 1440)).join("")}</select></label>
  <label>theme <select id="t"><option value="">light</option><option value="dark">dark</option></select></label>
  <label>height <select id="h"><option>900</option><option>1400</option><option>2400</option></select></label>
  <button id="r">reload all</button>
  <span class="hint">${names.length} views · each frame scrolls and can be dragged taller · open over file://</span>
</header>
${rows}
<script>
  var W = document.getElementById("w"), T = document.getElementById("t"),
      H = document.getElementById("h"), R = document.getElementById("r");
  function apply() {
    var frames = document.querySelectorAll("iframe");
    for (var i = 0; i < frames.length; i++) {
      var f = frames[i];
      f.style.width = W.value + "px";
      f.style.height = H.value + "px";
      var want = "snap-" + f.getAttribute("data-snap") + ".html" + (T.value ? "?dark" : "");
      if (f.getAttribute("src") !== want) f.setAttribute("src", want);
    }
  }
  W.onchange = T.onchange = H.onchange = apply;
  R.onclick = function () {
    var frames = document.querySelectorAll("iframe");
    for (var i = 0; i < frames.length; i++) frames[i].contentWindow.location.reload();
  };
  apply();
</script>
</body></html>`;
}

// -------------------------------------------------------------------- drive --

// ⚠⚠ DERIVED FROM index.js, NEVER RETYPED. This was a hard-coded list of eight
// and it went stale the moment a ninth tab was added: the Paper tab existed,
// rendered, and was swept by NOTHING — not the render walk, not the markdown
// sweep — while this file printed OK. A whole view was unchecked and the check
// said everything was fine, which is the exact failure mode this repo keeps
// having with hard-coded counts (CLAUDE.md rule 2).
const TABS = vm.runInContext("TABS", sandbox).map(t => t.id);
// Tabs that render no source or assembly. On these, every asterisk on the page
// came from this repo's prose, so a literal one is a lost emphasis marker.
// `patterns` is excluded: it shows C, where `*` is a pointer and `/* */` a
// comment, and judging those is not this check's business.
const NO_CODE_TABS = new Set(["overview", "ladder", "cost", "security", "proof", "findings", "method"]);

// `const` bindings are script-scoped in a vm context, so reach them by evaluation.
const APP = vm.runInContext("APP", sandbox);
const call = (expr) => vm.runInContext(expr, sandbox);
sandbox.APP = APP;

async function run() {
  await sandbox.loadIndex();
  const D = APP.data;
  if (!D || !D.patterns) { console.error("FAIL: index.json did not load"); process.exit(1); }

  // preload every pattern detail + code + docs so no view is exercised half-empty
  for (const p of D.patterns) {
    await sandbox.loadPattern(p.id);
    await sandbox.loadCode(p.id);
    await sandbox.loadDocs(p.id);
    await sandbox.loadAsm(p.id);
  }
  // …and every paper version, or the Paper tab is only ever rendered in its
  // loading state and the whole renderer goes unexercised
  for (const v of Object.keys(D.paper || {})) await sandbox.loadPaper(v);

  for (const tab of TABS) {
    APP.tab = tab;
    try { sandbox.renderAll(); } catch (e) {
      problems.push(`tab ${tab} THREW: ${e.stack.split("\n").slice(0, 4).join(" | ")}`);
      continue;
    }
    const before = nodes;
    walk(LAST, tab);
    if (nodes - before < 20) problems.push(`tab ${tab}: suspiciously small tree (${nodes - before} nodes)`);
  }

  // every pattern page, every rung's code view
  APP.tab = "patterns";
  for (const p of D.patterns) {
    APP.patId = p.id;
    APP.patDiff = null;
    for (const rung of ["c-gcc", "safe_naive", "safe_tuned", "unsafe", "verus"]) {
      APP.patRung = rung;
      try { sandbox.renderAll(); walk(LAST, `pattern ${p.id}/${rung}`); }
      catch (e) { problems.push(`pattern ${p.id}/${rung} THREW: ${e.message}`); }
    }
  }

  // every diff, on every pattern, with comments both hidden and shown.  This is
  // 4 x 23 x 2 renders and it is worth it: a diff is the one view that reads two
  // rungs at once, so it breaks on patterns where one of them is missing (p01
  // has no hardened C) or where both are the same text (p08's Rust rungs).
  const PAIRS = vm.runInContext("DIFF_PAIRS", sandbox);
  for (const p of D.patterns) {
    APP.patId = p.id;
    for (const pair of PAIRS) {
      APP.patDiff = pair.id;
      APP.diffAsm = false;
      for (const layout of ["split", "unified"]) {
        APP.diffLayout = layout;
        for (const showComments of [false, true]) {
          APP.diffComments = showComments;
          try { sandbox.renderAll(); walk(LAST, `diff ${p.id}/${pair.id}/${layout}`); }
          catch (e) { problems.push(`diff ${p.id}/${pair.id}/${layout} (comments=${showComments}) THREW: ${e.message}`); }
        }
      }
      // and the compiled view, at both optimisation levels and both layouts,
      // with the notes fold both shut and open — the confidence legend only
      // exists in the open state and would otherwise never be rendered
      APP.diffAsm = true;
      for (const layout of ["split", "unified"]) {
        APP.diffLayout = layout;
        for (const opt of ["O3", "O0"]) {
          APP.diffOpt = opt;
          for (const notes of [false, true]) {
            APP.diffNotes = notes;
            try { sandbox.renderAll(); walk(LAST, `asm ${p.id}/${pair.id}/${opt}/${layout}/notes=${notes}`); }
            catch (e) { problems.push(`asm ${p.id}/${pair.id}/${opt}/${layout}/notes=${notes} THREW: ${e.message}`); }
          }
        }
      }
      APP.diffAsm = false; APP.diffLayout = "split"; APP.diffNotes = false;
    }
  }
  APP.patDiff = null; APP.diffComments = false; APP.diffAsm = false; APP.diffOpt = "O3";

  // The linked source<->assembly view, WITH A SELECTION ACTIVE.  Selection
  // changes what every row renders (classes, the #asm-sel anchor, tooltips), so
  // rendering only the unselected state would leave that path untested.  Both
  // sides, a line that exists, and a line that does not.
  for (const p of D.patterns) {
    const asmRec = vm.runInContext("CACHE", sandbox).asm[p.id];
    if (!asmRec || !asmRec.pairs) continue;
    APP.patId = p.id; APP.diffAsm = true; APP.diffOpt = "O3";
    for (const pair of PAIRS) {
      APP.patDiff = pair.id;
      const aid = (pair.asm || [])[0];
      const d = aid && asmRec.pairs[aid] && asmRec.pairs[aid].O3;
      const lines = d && d.map
        ? [d.map.al.find(x => x > 0), d.map.bl.find(x => x > 0), 999999]
        : [1, 999999];
      for (const side of ["a", "b"]) {
        for (const line of lines) {
          APP.linkSel = line ? { side, line } : null;
          for (const layout of ["split", "unified"]) {
            APP.diffLayout = layout;
            try { sandbox.renderAll(); walk(LAST, `linked ${p.id}/${pair.id}/${side}:${line}/${layout}`); }
            catch (e) { problems.push(`linked ${p.id}/${pair.id}/${side}:${line}/${layout} THREW: ${e.message}`); }
          }
        }
      }
    }
  }
  APP.linkSel = null; APP.patDiff = null; APP.diffAsm = false; APP.diffLayout = "split";

  // The split layout falls back to unified below SPLIT_MIN_PX, and that fallback
  // is computed at render time from window.innerWidth — so it has to be
  // exercised at a narrow width, or a phone-width viewer is rendering a code
  // path nothing here has ever run.
  {
    const realW = sandbox.window.innerWidth;
    for (const w of [1440, 900, 420]) {
      sandbox.window.innerWidth = w;
      APP.patId = D.patterns[0].id;
      for (const pair of PAIRS.slice(0, 2)) {
        APP.patDiff = pair.id;
        for (const asmMode of [false, true]) {
          APP.diffAsm = asmMode;
          try { sandbox.renderAll(); walk(LAST, `width ${w} ${pair.id}${asmMode ? "/asm" : ""}`); }
          catch (e) { problems.push(`width ${w} ${pair.id} THREW: ${e.message}`); }
        }
      }
    }
    sandbox.window.innerWidth = realW;
    APP.patDiff = null; APP.diffAsm = false;
  }

  // every cost filter combination
  APP.tab = "cost";
  for (const metric of ["marginal", "kernel"]) {
    for (const mode of ["isolated", "whole"]) {
      for (const input of ["small.bin", "large.bin"]) {
        Object.assign(APP.cost, { metric, mode, input });
        try { sandbox.renderAll(); walk(LAST, `cost ${metric}/${mode}/${input}`); }
        catch (e) { problems.push(`cost ${metric}/${mode}/${input} THREW: ${e.message}`); }
      }
    }
  }

  // security + proof detail for every pattern
  for (const tab of ["security", "proof"]) {
    APP.tab = tab;
    for (const p of D.patterns) {
      APP.secPattern = p.id; APP.proofPattern = p.id;
      try { sandbox.renderAll(); walk(LAST, `${tab} ${p.id}`); }
      catch (e) { problems.push(`${tab} ${p.id} THREW: ${e.message}`); }
    }
  }

  // A pattern's `title` and `SHORT` name are used in headings, tooltips, table
  // cells and the sidebar — none of which run md(). Markdown in one renders as
  // literal punctuation, and three titles shipped with backticks doing exactly
  // that. They are LABELS, not prose; keep them plain.
  {
    const C = vm.runInContext("({P: PATTERNS, S: SHORT})", sandbox);
    for (const [id, e] of Object.entries(C.P)) {
      for (const field of ["title", "family", "bug", "role"]) {
        if (e[field] && /[`*_]/.test(e[field]))
          problems.push(`content.js PATTERNS["${id}"].${field} contains markdown — it is a label, rendered raw`);
      }
    }
    for (const [id, v] of Object.entries(C.S)) {
      if (/[`*_]/.test(v))
        problems.push(`content.js SHORT["${id}"] contains markdown — it is a label, rendered raw`);
    }
  }

  // A `**` that never closes renders as two literal asterisks. Nothing throws,
  // the tree is well-formed, and the page just quietly has punctuation in it —
  // which is exactly what happened the first time a sentence was split between
  // content.js and index.js, with the opening marker on one side of the seam
  // and the closing marker on the other. `md()` leaves the stray behind, so
  // finding one in the OUTPUT is the test.
  {
    // every tab, and every pattern's own write-up — the prose is per pattern,
    // so sweeping only the one that happens to be selected checks one of 25
    const targets = TABS.map(t => [t, null])
      .concat(D.patterns.map(p => ["patterns", p.id]));
    for (const [tab, pid] of targets) {
      APP.tab = tab;
      if (pid) APP.patId = pid;
      try {
        sandbox.renderAll();
        // <pre> holds upstream files verbatim and source code; their markdown
        // and their asterisks are content, not markup, so they are not ours to
        // judge. Everything outside <pre> is prose this repo wrote.
        const raw = toHTML(LAST);
        const text = raw
          .replace(/<pre[\s\S]*?<\/pre>/g, " ")
          .replace(/<[^>]+>/g, " ");
        // code spans legitimately contain `*`; unmatched `**` does not occur in
        // any source file here, so any survivor is a marker that lost its pair
        const stray = text.match(/\*\*/g);
        const where = pid ? `${tab}/${pid}` : tab;
        if (stray) problems.push(`${where}: ${stray.length} unclosed \`**\` reached the page — a bold marker lost its pair`);
        // On the tabs with no code pane, prose is ALL there is, and a single
        // literal `*` can only be an emphasis marker that lost its partner.
        // Measured: these tabs render zero asterisks when the markup is right.
        // A literal BACKTICK on the page means a code span that md() never saw
        // — a label, a heading or a table cell rendered raw. Measured across
        // every tab: the right answer is zero, everywhere, including the
        // patterns tab, because a real code span becomes a <code> element and
        // is stripped below before counting.
        const prose = raw
          .replace(/<pre[\s\S]*?<\/pre>/g, " ")
          .replace(/<code[^>]*>[\s\S]*?<\/code>/g, " ")     // `a * b` is content
          .replace(/<[^>]+>/g, " ");
        const ticks = prose.match(/`/g);
        if (ticks) problems.push(`${where}: ${ticks.length} literal backtick(s) — a code span reached the page through something that does not run md()`);
        if (!pid && NO_CODE_TABS.has(tab)) {
          const lone = prose.match(/\*/g);
          if (lone) problems.push(`${where}: ${lone.length} literal \`*\` in prose — an italic marker lost its pair`);
        }
      } catch (e) { problems.push(`markdown sweep ${pid ? `${tab}/${pid}` : tab} THREW: ${e.message}`); }
    }
  }

  // The Security and Proof panes each show ONE pattern, chosen by a <select>
  // and mirrored by a marked row. A select whose `selected` attribute stops
  // tracking the state looks fine and lies about what you are reading — and
  // `selected: false` would silently render as selected (LESSONS #10). So:
  // drive the state, and assert BOTH indicators agree with it.
  {
    const pick = D.patterns[Math.min(3, D.patterns.length - 1)].id;
    for (const [tab, key] of [["security", "secPattern"], ["proof", "proofPattern"]]) {
      APP.tab = tab; APP[key] = pick;
      try {
        sandbox.renderAll();
        const html = toHTML(LAST);
        const opts = [...html.matchAll(/<option value="([^"]+)"[^>]*selected/g)].map(m => m[1]);
        if (opts.length !== 1) problems.push(`${tab}: ${opts.length} options marked selected, expected exactly 1`);
        else if (opts[0] !== pick) problems.push(`${tab}: picker shows ${opts[0]} while the pane shows ${pick}`);
        const marked = (html.match(/<tr class="on"/g) || []).length;
        if (marked !== 1) problems.push(`${tab}: ${marked} rows marked as current, expected exactly 1`);
        if (!html.includes(pick.replace(/^p(\d+).*/, "p$1"))) problems.push(`${tab}: pane heading does not name ${pick}`);
      } catch (e) { problems.push(`picker ${tab} THREW: ${e.message}`); }
    }
    APP.secPattern = null; APP.proofPattern = null;
  }

  // The spread chart positions every mark by percentage, and a percentage out
  // of range is invisible in a render check and invisible in a stylesheet —
  // the mark simply leaves the track. The dumbbell's negative-width bar at
  // 360px was this same class of bug. So: arithmetic, not eyes.
  {
    APP.tab = "cost";
    sandbox.renderAll();
    const html = toHTML(LAST);
    let bands = 0, ticks = 0;
    for (const m of html.matchAll(/class="spread-band (?:neg|pos)[^"]*" style="left:([-\d.]+)%;width:([-\d.]+)%"/g)) {
      bands++;
      const l = +m[1], w = +m[2];
      if (l < -0.01 || w < -0.01 || l + w > 100.01)
        problems.push(`spread band leaves its track: left=${l}% width=${w}%`);
    }
    for (const m of html.matchAll(/class="spread-tick"[^>]*style="left:([-\d.]+)%"/g)) {
      ticks++;
      const l = +m[1];
      if (l < -0.01 || l > 100.01) problems.push(`spread tick leaves its track: left=${l}%`);
    }
    const L = vm.runInContext("APP", sandbox).data.layout || {};
    const want = (L.pairs || []).length;
    if (want && bands !== want * 2) problems.push(`spread chart: ${want} comparisons but ${bands} bands (expected ${want * 2})`);
    const wantTicks = (L.pairs || []).reduce((n, p) => n + (p.values || []).length, 0);
    if (wantTicks && ticks !== wantTicks) problems.push(`spread chart: ${wantTicks} builds but ${ticks} ticks`);
    console.log(`spread chart: ${bands} bands, ${ticks} ticks, all within track`);
  }

  // Two branches that exist for evidence the corpus does not currently
  // contain, so nothing here has ever executed them — and the day they fire is
  // the day they must not throw.  Both were dead within hours of being written:
  // `verus_exit_anomalies` is empty on every pattern, and p23 arrived with a
  // FAILing gate and was fixed upstream the same afternoon.  So: inject the
  // evidence, assert the page SAYS SO, then put the real record back.
  {
    const CACHE_ = vm.runInContext("CACHE", sandbox);
    const pid = D.patterns[0].id;
    const det = CACHE_.pattern[pid];
    const probe = (what, mutate, restore, marker, tab) => {
      mutate();
      APP.tab = tab; APP.proofPattern = pid; APP.patId = pid;
      let text = "";
      try {
        sandbox.renderAll();
        walk(LAST, `${what} ${pid}`);
        text = toHTML(LAST);
      } catch (e) { problems.push(`${what} ${pid} THREW: ${e.message}`); }
      if (!marker.test(text)) problems.push(`${what} injected but never rendered — the branch is dead markup`);
      restore();
      sandbox.renderAll();
      if (marker.test(toHTML(LAST))) problems.push(`${what} persisted after the record was restored`);
    };

    if (det && det.verus) {
      const real = det.verus.exit_anomalies;
      probe("exit-anomaly",
        () => { det.verus.exit_anomalies = ["verus.rs: 9 verified, 0 errors, rc=101"]; },
        () => { det.verus.exit_anomalies = real; },
        /rc=101/, "proof");
    }
    // ⚠ THE ONE THAT MATTERS MOST: a MISSING licence check must never render as
    // a PASSED one. Blank the licence map and the cost view must say the check
    // is unavailable and mark every row — not quietly drop the qualification.
    {
      const real = D.licence;
      D.licence = {};
      APP.tab = "cost";
      let html = "";
      try { sandbox.renderAll(); walk(LAST, "cost/no-licence"); html = toHTML(LAST); }
      catch (e) { problems.push(`cost with no licence data THREW: ${e.message}`); }
      if (!/could not read the licence/i.test(html))
        problems.push("licence data removed and the cost view did NOT say so — a missing check is rendering as a passed one");
      const marks = (html.match(/‡/g) || []).length;
      if (!marks) problems.push("licence data removed and no row was marked unverified");
      D.licence = real;
      sandbox.renderAll();
      if (/could not read the licence/i.test(toHTML(LAST)))
        problems.push("the missing-licence notice persisted after the data was restored");
    }

    if (det && det.verus && det.verus.proof_domain) {
      const pd = det.verus.proof_domain;
      const first = Object.keys(pd)[0];
      const real = pd[first].requires_ok;
      probe("requires-violated",
        () => { pd[first].requires_ok = false; },
        () => { pd[first].requires_ok = real; },
        /did NOT hold/, "proof");
    }
    if (det) {
      const row = D.patterns[0];
      const rv = row.verdict, rf = row.failures, dv = det.verdict, df = det.failures;
      probe("gate-failure",
        () => {
          row.verdict = det.verdict = "FAIL"; row.failures = 1;
          det.failures = [{ section: "twin", message: "SLB-PROBE-9182 injected failure" }];
        },
        () => { row.verdict = rv; row.failures = rf; det.verdict = dv; det.failures = df; },
        /SLB-PROBE-9182/, "patterns");
    }
  }

  // every rung-filter preset, plus a single-rung selection, on every view that
  // honours it — a hidden rung must never empty or throw a chart
  const PRESETS = vm.runInContext("RUNG_PRESETS", sandbox);
  const setRungs = (cells) => { APP.rungs = new Set(cells); };
  for (const preset of [...PRESETS.map(p => p.cells), ["verus"], ["c-gcc"]]) {
    setRungs(preset);
    for (const tab of ["ladder", "patterns", "cost"]) {
      APP.tab = tab;
      try { sandbox.renderAll(); walk(LAST, `rungs[${preset.join("|")}] ${tab}`); }
      catch (e) { problems.push(`rungs[${preset.join("|")}] ${tab} THREW: ${e.message}`); }
    }
  }
  setRungs(vm.runInContext("RUNG_ORDER", sandbox));

  // ---- the line map and the source pane must be in the SAME COORDINATES ----
  // This was a silent bug for several commits: Rust rungs are sliced (the
  // driver banner onwards is dropped) so the pane numbered lines from 1, while
  // every line in the assembly map is a FILE line from addr2line.  p03's
  // unsafe.rs starts at file line 54, so clicking any Rust line sent a number
  // that could never match and nothing happened.  Nothing threw, so no render
  // check could have seen it — only this comparison can.
  {
    const CACHE_ = vm.runInContext("CACHE", sandbox);
    let checked = 0, bad = 0;
    for (const p of D.patterns) {
      const code = CACHE_.code[p.id], asmRec = CACHE_.asm[p.id];
      if (!code || !asmRec || !asmRec.pairs) continue;
      for (const [pairId, byOpt] of Object.entries(asmRec.pairs)) {
        for (const [opt, d] of Object.entries(byOpt)) {
          if (!d.map) continue;
          for (const [side, arr] of [["a", d.map.al], ["b", d.map.bl]]) {
            const cell = code[d[side].cell];
            if (!cell) continue;
            if (cell.first_line === undefined) {
              problems.push(`${p.id}/${d[side].cell}: code cell has no first_line — the pane cannot be in file coordinates`);
              bad++; continue;
            }
            const lo = cell.first_line, hi = lo + cell.text.split("\n").length;
            const lines = arr.filter(v => v > 0);
            const inside = lines.filter(v => v >= lo && v < hi).length;
            checked++;
            // some instructions legitimately map outside the displayed slice
            // (a helper below the driver banner); a WHOLESALE miss is the bug
            if (lines.length >= 5 && inside === 0) {
              problems.push(`${p.id}/${pairId}/${opt}/${side} (${d[side].cell}): NONE of ${lines.length} mapped lines fall inside the displayed pane (${lo}..${hi - 1}) — pane and map are in different coordinates`);
              bad++;
            }
          }
        }
      }
    }
    if (!checked) problems.push("line-map coordinate check ran over nothing");
    console.log(`line-map coordinates: ${checked} cell-views checked, ${bad} mismatched`);
  }

  // ------------------------------------------------------------- the deck --
  //
  // The paper view renders ONE slide, so walking the page validates slide 1 and
  // nothing else — 51 of 52 slides could be malformed and this check would
  // still print OK.  So drive every slide through the same renderer and walk
  // each tree.  This also exercises `SLIDES.build`, whose whole job is to THROW
  // when a slide cannot name the question it answers.
  {
    const SL = call("typeof SLIDES !== 'undefined' ? SLIDES : null");
    const DECK = call("typeof SLIDES_DECK === 'function' ? SLIDES_DECK : null");
    if (!SL || typeof DECK !== "function") {
      problems.push("the talk did not load — slides.js / slides_deck.js are not on the sandbox global");
    } else {
      let deck = null;
      try {
        deck = SL.build(DECK, APP.data);
      } catch (e) {
        problems.push(`the talk did not build: ${e.message}`);
      }
      if (deck) {
        const kinds = new Set();
        let noQ = 0;
        for (let i = 0; i < deck.slides.length; i++) {
          const s = deck.slides[i];
          kinds.add(s.kind);
          if (s.kind !== "title" && s.kind !== "ask" && s.kind !== "end" && !s.q) noQ++;
          const tree = SL.view(deck, { i, full: false, on: {} });
          walk(tree, `deck[${i}:${s.kind}]`);
          walk(SL.view(deck, { i, full: true, on: {} }), `deck-full[${i}:${s.kind}]`);
          // ⚠ THE TREE BEING WELL-FORMED SAYS NOTHING ABOUT THE TEXT ON IT.
          // Four slides once shipped literal backticks and asterisks because a
          // question banner, a quote's source and a column heading were pushed
          // as raw strings — md() never ran on them.  The page-wide markdown
          // sweep could not see it, because the paper tab renders slide 1 and
          // no more.  So run the same sweep here, per slide.
          const prose = toHTML(tree)
            .replace(/<pre[\s\S]*?<\/pre>/g, " ")
            .replace(/<code[^>]*>[\s\S]*?<\/code>/g, " ")
            .replace(/<[^>]+>/g, " ");
          const tick = (prose.match(/`/g) || []).length;
          const star = (prose.match(/\*/g) || []).length;
          if (tick) problems.push(`deck[${i}:${s.kind}]: ${tick} literal backtick(s) on the slide — a field reached the page without md()`);
          if (star) problems.push(`deck[${i}:${s.kind}]: ${star} literal asterisk(s) on the slide — an emphasis marker lost its pair, or a field skipped md()`);
        }
        if (noQ) problems.push(`the talk has ${noQ} answering slide(s) with no question — every slide must be motivated`);
        if (deck.slides.length < 20) problems.push(`the talk is ${deck.slides.length} slides; a 45-minute deck should not be that short`);
        // a live-data miss surfaces as "?path" rather than throwing
        const flat = JSON.stringify(deck.slides);
        const misses = [...new Set(flat.match(/\?(?:totals|passing|p\d\d)[\w./-]*/g) || [])];
        if (misses.length) problems.push(`the talk has unresolved live values: ${misses.join(", ")}`);
        console.log(`the talk: ${deck.slides.length} slides, ${kinds.size} kinds, every slide rendered in both states`);
      }
    }
  }

  // --snap: freeze fully-populated views to static HTML for visual QA, so a
  // screenshot never races the lazy fetches.
  if (process.argv.includes("--snap")) {
    APP.rungs = new Set(vm.runInContext("RUNG_ORDER", sandbox));
    const snaps = [
      ["overview", () => { APP.tab = "overview"; }],
      ["findings", () => { APP.tab = "findings"; APP.findTag = "all"; }],
      ["patterns", () => { APP.tab = "patterns"; APP.patId = "p02-buffer-copy"; APP.patRung = "safe_tuned"; APP.patDiff = null; }],
      ["verus", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patRung = "verus"; APP.patDiff = null; }],
      ["diff", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "r4-r5"; APP.diffAsm = false; }],
      ["asm", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "r3-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = null; }],
      ["asm-linked", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "r3-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = { side: "a", line: 49 }; }],
      ["asm-unified", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "r3-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "unified"; }],
      ["diff-split", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "c-check"; APP.diffAsm = false; APP.diffLayout = "split"; }],
      // p06 has the longest lines that land in a diff — the case that broke the
      // first split layout, so it gets a snapshot of its own
      ["diff-split-long", () => { APP.tab = "patterns"; APP.patId = "p06-rotate"; APP.patDiff = "r2-r3"; APP.diffAsm = false; APP.diffLayout = "split"; }],
      // the cross-language pair: two sources side by side, assembly diffed
      ["xlang", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "ch-r4"; APP.diffAsm = false; APP.diffLayout = "split"; APP.linkSel = null; }],
      ["xlang-asm", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "ch-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = null; }],
      // the alignment: a C line selected, Rust lines lit through the assembly
      ["xlang-aligned", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "ch-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = { side: "a", line: 52 }; }],   // a line that DOES align
      // clicking the RUST side — the case that silently did nothing until the
      // sliced-source line offset was carried through
      ["xlang-rust-click", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "ch-r4"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = { side: "b", line: 65 }; }],
      // the worst partial-twin case in the corpus — the only place the
      // approximate tier is visible, so it gets a snapshot of its own
      ["conf-tiers", () => { APP.tab = "patterns"; APP.patId = "p09-bitset"; APP.patDiff = "ch-r4"; APP.diffAsm = true; APP.diffOpt = "O0"; APP.diffLayout = "unified"; APP.linkSel = null; APP.diffNotes = true; }],
      // one source, two backends
      ["backend", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "c-backend"; APP.diffAsm = true; APP.diffOpt = "O3"; APP.diffLayout = "split"; APP.linkSel = null; }],
      ["asm-c", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "c-check"; APP.diffAsm = true; APP.diffOpt = "O3"; }],
      ["diff-c", () => { APP.tab = "patterns"; APP.patId = "p03-bounded-stack"; APP.patDiff = "c-check"; }],
      ["security", () => { APP.tab = "security"; APP.secPattern = "p02-buffer-copy"; }],
      // the sanitizer rows that used to read as a plain "silent": a run that
      // exits 0 with the wrong answer, and the one run in the corpus that hung
      ["san-silent", () => { APP.tab = "security"; APP.secPattern = "p04-ring-buffer"; }],
      ["san-hung", () => { APP.tab = "security"; APP.secPattern = "p22-hash-probe"; }],
      ["proof",    () => { APP.tab = "proof"; APP.proofPattern = "p03-bounded-stack"; }],
      ["method",   () => { APP.tab = "method"; }],
      ["paper",    () => { APP.tab = "paper"; }],
      ["ladder",   () => { APP.tab = "ladder"; }],
      ["cost",     () => { APP.tab = "cost"; }],
    ];
    for (const [name, set] of snaps) {
      set();
      sandbox.renderAll();
      // `?dark` switches the theme in-document, so the contact sheet below can
      // frame the same file both ways without writing two copies of each view.
      const html = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../common.css"><link rel="stylesheet" href="../index.css">
<script>if(location.search.indexOf("dark")>=0)document.documentElement.dataset.theme="dark";</script>
<title>snap ${name}</title></head><body><div class="app"><div class="wrap">${toHTML(LAST)}</div></div></body></html>`;
      fs.mkdirSync(path.join(WEB, ".temp"), { recursive: true });
      fs.writeFileSync(path.join(WEB, ".temp", `snap-${name}.html`), html);
    }
    fs.writeFileSync(path.join(WEB, ".temp", "snap-index.html"),
                     contactSheet(snaps.map(s => s[0])));
    console.log(`wrote .temp/snap-*.html + snap-index.html (${snaps.length} views)`);
  }

  console.log(`rendered ${renderCount} trees, walked ${nodes} nodes`);
  if (problems.length) {
    console.error(`\n${problems.length} PROBLEM(S):`);
    for (const p of problems.slice(0, 40)) console.error("  · " + p);
    process.exit(1);
  }
  console.log("OK — no null children, no bad tags, no throws");
}

run().catch(e => { console.error("harness error:", e); process.exit(1); });
