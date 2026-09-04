// render_deck.mjs — print the talk as plain text, one slide at a time.
//
// The deck lives as data in `slides_deck.js` and is only ever seen through a
// 16:9 box in a browser.  That is the wrong medium for the two things you
// actually need to do with a talk: read it end to end to check the argument
// holds, and hold a script while presenting it.  So this renders the same deck
// the page renders — same `SLIDES.build`, same live data — as text.
//
//   node tools/render_deck.mjs            # the whole talk
//   node tools/render_deck.mjs --questions  # ONLY the questions, in order
//
// ⚠ `--questions` is the deck's own version of the paper's breadth-first cut:
// the questions alone must read as a coherent interrogation, because if they do
// not, the running order is wrong and no amount of good slides will fix it.

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const WEB = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const onlyQ = process.argv.includes("--questions");

const sandbox = { console: { log() {}, warn() {}, error() {} } };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
for (const f of ["syntax.js", "slides.js", "slides_deck.js"]) {
  vm.runInContext(fs.readFileSync(path.join(WEB, f), "utf8"), sandbox, { filename: f });
}

const data = JSON.parse(fs.readFileSync(path.join(WEB, "data", "index.json"), "utf8"));
const deck = sandbox.SLIDES.build(sandbox.SLIDES_DECK, data);

const strip = (s) => String(s).replace(/\*\*(.+?)\*\*/g, "$1").replace(/`(.+?)`/g, "$1").replace(/\*(.+?)\*/g, "$1");
const wrap = (s, w, pad) => {
  const out = []; let line = "";
  for (const word of strip(s).split(/\s+/)) {
    if ((line + " " + word).trim().length > w) { out.push(line.trim()); line = word; }
    else line += " " + word;
  }
  if (line.trim()) out.push(line.trim());
  return out.map(l => pad + l).join("\n");
};

if (onlyQ) {
  console.log("THE QUESTIONS, IN ORDER — the talk's argument with the slides removed\n" + "=".repeat(72));
  let last = null;
  deck.slides.forEach((s, i) => {
    if (s.kind === "ask") { console.log(`\n── “${s.q}”${s.cue ? "   [" + s.cue + "]" : ""}`); last = s.q; }
    else if (s.q && s.q !== last) console.log(`     ${String(i + 1).padStart(2)}. ${s.q}`);
  });
  console.log(`\n${deck.slides.length} slides.`);
} else {
  deck.slides.forEach((s, i) => {
    console.log("\n" + "─".repeat(72));
    console.log(`[${i + 1}/${deck.slides.length}]  ${s.kind.toUpperCase()}`);
    if (s.kind !== "title" && s.kind !== "ask" && s.kind !== "end") console.log(`  THEY ASKED: “${s.q}”`);
    if (s.cue) console.log(`  CUE: ${s.cue}`);
    console.log("");
    if (s.title) console.log(wrap(s.title, 66, "  "));
    if (s.kind === "ask") console.log(wrap("“" + s.q + "”", 66, "  "));
    if (s.head) console.log(wrap(s.head, 66, "  "));
    if (s.sub) console.log("\n" + wrap(s.sub, 66, "  "));
    if (s.text) console.log(wrap("“" + s.text + "”", 66, "  "));
    if (s.src && s.kind === "quote") console.log(wrap("— " + s.src, 66, "     "));
    for (const b of s.body || []) console.log("\n" + wrap("• " + b, 64, "    "));
    if (s.left) { console.log("\n  " + strip(s.left.h)); for (const b of s.left.body) console.log(wrap("• " + b, 60, "    ")); }
    if (s.right) { console.log("\n  " + strip(s.right.h)); for (const b of s.right.body) console.log(wrap("• " + b, 60, "    ")); }
    if (s.cols) {
      console.log("");
      console.log("    " + s.cols.join("  |  "));
      for (const r of s.rows) console.log("    " + r.map(strip).join("  |  "));
    }
    if (s.src && s.kind === "code") console.log("\n" + s.src.split("\n").map(l => "    " + l).join("\n"));
    if (s.note) console.log("\n" + wrap("NOTE: " + s.note, 64, "  "));
    if (s.aside) console.log("\n" + wrap("ASIDE: " + s.aside, 64, "  "));
  });
  console.log("");
}
