// diff.js — line diff between two rungs of the same pattern.
//
// The four diffs this site shows are the ladder's own transitions, and each
// isolates one thing:
//
//   C      -> hardened C   the check, written out by hand
//   R2     -> R3           spelling, at an identical guarantee
//   R3     -> R4           what removing the check looks like
//   R4     -> R5           the proof — and R4/R5 are byte-identical machine
//                          code, so this diff is a picture of exactly the text
//                          that compiles to nothing
//
// COMMENTS ARE DROPPED BY DEFAULT, and that is not cosmetic.  Each rung lives in
// its own file with its own banner comment, so a raw diff of C against hardened
// C on p03 is 66 changed comment lines around 8 changed code lines — the signal
// is 11% of the output.  `ignoreComments` filters comment-only and blank lines
// from both sides before comparing, using the tokenizer rather than a regex so
// that a line inside a multi-line block comment is recognised as one.
//
// Long runs of unchanged code are collapsed to a few lines of context, because
// R4 -> R5 adds a median of 281 lines and the unchanged remainder would bury it.

(function (g) {
  "use strict";

  // A line is "comment" if it has no content outside comment tokens.
  function isCommentLine(tokens) {
    let sawCode = false;
    for (const t of tokens) {
      if (t.t === "com") continue;
      if (t.s.trim() === "") continue;
      sawCode = true; break;
    }
    return !sawCode;
  }

  // Build the comparable view of a file: keeps the original line number so the
  // gutter still reports where a line really is in the source.
  // `base` is the FILE line number of the first displayed line.  Rust rungs are
  // sliced (the driver banner onwards is dropped), so a pane numbered from 1
  // disagrees with every line number the assembly map holds — those come from
  // addr2line, which reads the whole file.  Numbering in file coordinates keeps
  // the two in the same units and is more useful to a reader anyway.
  function prepare(text, lang, ignoreComments, base) {
    const lines = g.SYNTAX.tokenizeLines(text, lang);
    const first = base || 1;
    const out = [];
    for (let i = 0; i < lines.length; i++) {
      const toks = lines[i];
      if (ignoreComments && isCommentLine(toks)) continue;
      out.push({ no: first + i, toks: toks, key: toks.map(t => t.s).join("").trim() });
    }
    return out;
  }

  // Longest common subsequence over line keys.  Common prefix and suffix are
  // trimmed first, which on these files collapses the matrix to almost nothing.
  function lcsOps(A, B) {
    const ops = [];
    let s = 0, ea = A.length, eb = B.length;
    while (s < ea && s < eb && A[s].key === B[s].key) { ops.push({ k: " ", a: A[s], b: B[s] }); s++; }
    const tail = [];
    while (ea > s && eb > s && A[ea - 1].key === B[eb - 1].key) { ea--; eb--; tail.unshift({ k: " ", a: A[ea], b: B[eb] }); }

    const a = A.slice(s, ea), b = B.slice(s, eb);
    const n = a.length, m = b.length;
    if (!n && !m) return ops.concat(tail);
    if (!n) { for (const x of b) ops.push({ k: "+", a: null, b: x }); return ops.concat(tail); }
    if (!m) { for (const x of a) ops.push({ k: "-", a: x, b: null }); return ops.concat(tail); }

    // DP table of LCS lengths.  n,m <= ~900 here, so this is a few ms.
    const w = m + 1;
    const dp = new Int32Array((n + 1) * w);
    for (let i = n - 1; i >= 0; i--) {
      for (let j = m - 1; j >= 0; j--) {
        dp[i * w + j] = a[i].key === b[j].key
          ? dp[(i + 1) * w + (j + 1)] + 1
          : Math.max(dp[(i + 1) * w + j], dp[i * w + (j + 1)]);
      }
    }
    let i = 0, j = 0;
    while (i < n && j < m) {
      if (a[i].key === b[j].key) { ops.push({ k: " ", a: a[i], b: b[j] }); i++; j++; }
      else if (dp[(i + 1) * w + j] >= dp[i * w + (j + 1)]) { ops.push({ k: "-", a: a[i], b: null }); i++; }
      else { ops.push({ k: "+", a: null, b: b[j] }); j++; }
    }
    while (i < n) { ops.push({ k: "-", a: a[i], b: null }); i++; }
    while (j < m) { ops.push({ k: "+", a: null, b: b[j] }); j++; }
    return ops.concat(tail);
  }

  // Replace long unchanged runs with a {k:"@", n} marker.
  function collapse(ops, context) {
    const keep = new Array(ops.length).fill(false);
    for (let i = 0; i < ops.length; i++) {
      if (ops[i].k === " ") continue;
      for (let j = Math.max(0, i - context); j <= Math.min(ops.length - 1, i + context); j++) keep[j] = true;
    }
    const out = [];
    let run = 0;
    for (let i = 0; i < ops.length; i++) {
      if (keep[i]) {
        if (run) { out.push({ k: "@", n: run }); run = 0; }
        out.push(ops[i]);
      } else run++;
    }
    if (run) out.push({ k: "@", n: run });
    return out;
  }

  // opts: {ignoreComments (default true), context (default 3)}
  function diffRungs(aText, aLang, bText, bLang, opts) {
    const o = opts || {};
    const ic = o.ignoreComments !== false;
    const A = prepare(aText, aLang, ic, o.aFirst);
    const B = prepare(bText, bLang, ic, o.bFirst);
    const ops = lcsOps(A, B);
    const added = ops.filter(x => x.k === "+").length;
    const removed = ops.filter(x => x.k === "-").length;
    return {
      ops: collapse(ops, o.context === undefined ? 3 : o.context),
      added: added, removed: removed,
      identical: added === 0 && removed === 0,
      comparedLines: { a: A.length, b: B.length },
      ignoredComments: ic,
    };
  }

  // Pair a flat op stream into side-by-side rows.
  //
  // A unified diff is a sequence; a split diff is a table, and turning one into
  // the other means deciding which deletion sits opposite which insertion.  The
  // usual rule, and the one here: consecutive runs of - and + are zipped
  // positionally, and whichever run is longer gets blank cells opposite its
  // tail.  Context and skip markers span both columns.
  //
  // `kindOf` lets this serve both op shapes — source ops are objects, assembly
  // ops are strings whose first character is the kind.
  function splitRows(ops, kindOf) {
    const rows = [];
    let dels = [], ins = [];

    const flush = () => {
      const n = Math.max(dels.length, ins.length);
      for (let i = 0; i < n; i++) {
        rows.push({ kind: "change", l: dels[i] === undefined ? null : dels[i],
                    r: ins[i] === undefined ? null : ins[i] });
      }
      dels = []; ins = [];
    };

    for (const op of ops) {
      const k = kindOf(op);
      if (k === "-") { dels.push(op); continue; }
      if (k === "+") { ins.push(op); continue; }
      flush();
      rows.push(k === "@" ? { kind: "skip", op: op } : { kind: "ctx", l: op, r: op });
    }
    flush();
    return rows;
  }

  g.DIFF = { diffRungs: diffRungs, isCommentLine: isCommentLine, splitRows: splitRows };
})(typeof globalThis !== "undefined" ? globalThis : this);
