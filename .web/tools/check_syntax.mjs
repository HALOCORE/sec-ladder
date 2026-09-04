// check_syntax.mjs — the tokenizer's correctness contract.
//
//   node tools/check_syntax.mjs
//
// syntax.js is hand-rolled, which is only defensible if there is a mechanical
// guarantee it never mangles the source.  There is exactly one that matters:
//
//   THE CONCATENATION OF EVERY EMITTED TOKEN IS BYTE-FOR-BYTE THE INPUT.
//
// A lexer that drops a character, duplicates one, or falls into an infinite
// classification loop cannot satisfy that.  It is checked here over every cell
// of every pattern — all 184 — plus a battery of hand-written adversarial
// snippets covering the constructs the corpus happens not to contain today but
// might tomorrow.
//
// It also asserts the line-splitting round-trips, because the diff view consumes
// tokenizeLines() rather than tokenize(), and a bug that only shows up at a line
// boundary would otherwise be invisible.
//
// WHAT THIS DOES NOT PROVE: that any token is classified *correctly*.  A lexer
// that returned one plain token per file would pass every assertion here.  The
// classification counts printed at the end are the guard against that — if
// `vtrust` ever reads 0, the Verus layer has silently stopped working.

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const WEB = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const sandbox = { console };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(WEB, "syntax.js"), "utf8"), sandbox, { filename: "syntax.js" });
const SYNTAX = sandbox.SYNTAX;

let failures = 0;
const counts = {};

function roundTrip(label, src, lang) {
  let toks;
  try {
    toks = SYNTAX.tokenize(src, lang);
  } catch (e) {
    console.error(`FAIL ${label}: threw — ${e.message}`);
    failures++; return;
  }
  const back = toks.map(t => t.s).join("");
  if (back !== src) {
    failures++;
    // locate the first divergence so the failure is actionable
    let i = 0; while (i < Math.min(back.length, src.length) && back[i] === src[i]) i++;
    console.error(`FAIL ${label}: round-trip differs at offset ${i}`);
    console.error(`  expected: ${JSON.stringify(src.slice(i, i + 60))}`);
    console.error(`  got:      ${JSON.stringify(back.slice(i, i + 60))}`);
    return;
  }
  // line split must round-trip too — the diff view depends on it
  const lines = SYNTAX.toLines(toks);
  const rejoined = lines.map(l => l.map(t => t.s).join("")).join("\n");
  if (rejoined !== src) {
    failures++;
    console.error(`FAIL ${label}: toLines() does not round-trip`);
    return;
  }
  for (const t of toks) counts[t.t || "plain"] = (counts[t.t || "plain"] || 0) + 1;
}

// ---------------------------------------------------------- the real corpus --
const codeDir = path.join(WEB, "data", "code");
if (!fs.existsSync(codeDir)) {
  console.error("no data/code — run `python3 build_data.py` first");
  process.exit(1);
}
let cells = 0;
for (const f of fs.readdirSync(codeDir).filter(x => x.endsWith(".json"))) {
  const d = JSON.parse(fs.readFileSync(path.join(codeDir, f), "utf8"));
  for (const [cell, v] of Object.entries(d)) {
    cells++;
    roundTrip(`${f}:${cell}`, v.text, SYNTAX.langFor(cell, v.lang));
  }
}

// ------------------------------------------------- adversarial hand-written --
// Constructs the corpus does not contain today.  They are here so that the day
// one of them lands upstream, this check fails instead of the page rendering
// mangled source.
const EVIL = [
  ["unterminated block comment", "rust", "let x = 1; /* never closed"],
  ["unterminated string", "rust", 'let s = "open'],
  ["unterminated char", "rust", "let c = 'a"],
  ["raw string", "rust", 'let s = r#"he said "hi""#;'],
  ["byte string", "rust", 'let b = b"\\x00\\xff";'],
  ["nested block comment", "rust", "/* outer /* inner */ still outer */ let x = 1;"],
  ["lifetime vs char", "rust", "fn f<'a>(x: &'a str) -> char { 'q' }"],
  ["lifetime at eof", "rust", "&'a"],
  ["escaped quote in char", "rust", "let c = '\\'';"],
  ["backslash at eof", "rust", 'let s = "abc\\'],
  ["attribute unbalanced", "verus", "#[verifier::external_body"],
  ["nested attribute", "verus", "#[verifier::external_body] fn f() {}"],
  ["hash not attribute", "rust", "let x = a # b;"],
  ["C include", "c", '#include <stdint.h>\n#include "local.h"'],
  ["C directive indented", "c", "  # define FOO 1"],
  ["C hash mid-line", "c", "int a = b # c;"],
  ["number suffixes", "rust", "let a = 0xff_u8 + 1_000usize + 3.5f64 + 0b1010;"],
  ["number then ident", "rust", "let x = 12abc;"],
  ["empty", "rust", ""],
  ["only newlines", "rust", "\n\n\n"],
  ["crlf", "rust", "let a = 1;\r\nlet b = 2;\r\n"],
  ["tabs and trailing space", "c", "\tint x = 1;   \n"],
  ["unicode identifiers", "rust", "let café = 1; // ☕ comment"],
  ["unicode in string", "rust", 'let s = "→ ∀x ∈ S";'],
  ["lone hash at eof", "rust", "#"],
  ["slash at eof", "rust", "let x = 1 /"],
  ["verus block", "verus",
    "verus!{ spec fn f(s: Seq<int>) -> nat { s.len() }\n" +
    "  proof fn lemma_x() ensures true decreases 0int { assert(true) by { } }\n" +
    "  #[verifier::external_body] fn g() { assume(false); } }"],
];
for (const [label, lang, src] of EVIL) roundTrip(`evil/${label}`, src, lang);

// ------------------------------------------------------------------ report --
console.log(`round-tripped ${cells} cells + ${EVIL.length} adversarial snippets`);
const order = ["plain", "com", "str", "num", "kw", "typ", "fn", "mac", "pre",
  "vspec", "vproof", "vghost", "vtrust"];
console.log("token classes: " + order.map(k => `${k}=${counts[k] || 0}`).join("  "));

// A lexer that classified nothing would pass every round-trip above.  These
// floors are what stops that from being green.  Each is ~65% of the count
// measured on the 23-pattern corpus, so a class collapsing to zero or halving
// fails while ordinary growth upstream does not.
//   com 3296  str 45  num 6202  kw 6905  typ 5689  fn 3194  mac 263  pre 193
//   vspec 474  vproof 335  vghost 1994  vtrust 99
// vtrust looks small beside the 139 raw occurrences of `external_body` because
// `#[verifier::external_body]` is one token here, not one per word.
const FLOORS = { com: 2000, str: 25, num: 4000, kw: 4500, typ: 3500, fn: 2000,
  mac: 150, pre: 120, vspec: 300, vproof: 200, vghost: 1200, vtrust: 60 };
for (const [k, min] of Object.entries(FLOORS)) {
  if ((counts[k] || 0) < min) {
    console.error(`FAIL: token class "${k}" produced ${counts[k] || 0}, expected >= ${min} — classification has regressed`);
    failures++;
  }
}

if (failures) { console.error(`\n${failures} failure(s).`); process.exit(1); }
console.log("OK — every token stream reconstructs its source exactly.");
