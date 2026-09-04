// paper.js — the renderer for `paper_vers/`.
//
// The format is markdown plus a small set of LaTeX-shaped markers; the spec is
// `paper_vers/README.md` and it is the durable document, not this file.
//
// TWO THINGS THIS FILE MUST KEEP DOING:
//
//   1. It emits JSONML, never an HTML string.  This page has no `innerHTML`
//      anywhere and that is a policy, not an accident — `syntax.js` exists in
//      the shape it does for the same reason.
//   2. It renders NUMBERS from data and PROSE from source, and never lets one
//      become the other.  `\num{totals.patterns}` is resolved at build time
//      against `data/index.json`; the build fails on a path that does not
//      resolve.  A count in this paper cannot go stale in silence, which is the
//      failure mode this whole project keeps having.
//
// Parsing is two passes.  Pass one walks the flattened source line by line and
// produces a flat list of blocks — heading, para, list, quote, code, figure,
// environment open/close.  Pass two numbers the sections, principles, examples
// and figures, resolves `\label`/`\ref`, and emits the tree.  Two passes because
// a `\ref` may point forwards.

(function (g) {
  "use strict";

  // ------------------------------------------------------------- inline ----
  // Inline markers are resolved into a plain string first, then handed to the
  // site's own md() so bold/italic/code behave exactly as they do everywhere
  // else.  Only `\ref` and `\src` need to become elements rather than text, so
  // the string is split around those and md() runs on the pieces between.

  const RE_INLINE = /\\(num|ref|cite|src|pat|todo)\{([^}]*)\}/g;

  function fmtNum(v, mode) {
    if (typeof v !== "number") return String(v);
    if (mode === "raw" || mode === "plain") return String(v);
    return v.toLocaleString("en-US");
  }

  // ctx: { nums, refs, labels, patterns, todos }
  //
  // ⚠⚠ ORDER MATTERS AND IT IS NOT THE OBVIOUS ONE.  The first version split on
  // markers and ran md() on the text between them — so `**a \num{x} b**` had its
  // opening `**` in one piece and its closing `**` in another, md() saw neither
  // pair, and SIX literal asterisks reached the page.  A marker inside emphasis
  // is completely natural prose ("**\num{totals.plain_c.silent_first} are
  // silent**") and it must work.
  //
  // So: run md() over the WHOLE string first, then walk its output and expand
  // markers inside the text nodes it produced. Emphasis pairs before markers
  // exist, and a marker inside a `**strong**` lands inside that element.
  function inline(text, ctx, keyBase) {
    const out = [];
    let k = 0;
    const expand = (s, into) => {
      let pos = 0, m;
      RE_INLINE.lastIndex = 0;
      while ((m = RE_INLINE.exec(s))) {
        if (m.index > pos) into.push(s.slice(pos, m.index));
        pos = m.index + m[0].length;
        into.push(marker(m[1], m[2], keyBase + "-" + (k++), ctx));
      }
      if (pos < s.length) into.push(s.slice(pos));
    };
    for (const node of g.md(text)) {
      if (typeof node === "string") expand(node, out);
      else if (Array.isArray(node)) {
        // ["strong", {key}, "text"] — expand markers inside the element
        const kids = [];
        for (let i = 2; i < node.length; i++) {
          if (typeof node[i] === "string") expand(node[i], kids);
          else kids.push(node[i]);
        }
        out.push([node[0], node[1], ...kids]);
      } else out.push(node);
    }
    return out;
  }

  // One inline marker -> one node.
  function marker(kind, arg, key, ctx) {
    if (kind === "num") {
      const [path, mode] = arg.split("|").map(s => s.trim());
      const v = ctx.nums[path];
      return v === undefined
        ? ["span.pp-bad", { key }, "?" + path]
        : ["span.pp-num", { key, "data-tip": "live from data/index.json \u00b7 " + path },
           fmtNum(v, mode)];
    }
    if (kind === "ref") {
      const t = ctx.labels[arg];
      return ["a.pp-ref", { key, href: "#paper/" + arg }, t ? t.num : "??"];
    }
    if (kind === "cite") {
      const r = ctx.refs[arg];
      return ["a.pp-cite", { key, href: r && r.url ? r.url : "#paper/bib",
                             "data-tip": r ? (r.title || arg) : arg },
              "[" + (r && r.short ? r.short : arg) + "]"];
    }
    if (kind === "src") return ["code.pp-src", { key, "data-tip": "evidence: " + arg }, arg];
    if (kind === "pat") {
      const p = (ctx.patterns || []).find(x => x.id.startsWith(arg));
      return ["span.pp-pat", { key }, p ? p.id : arg];
    }
    return ["span.pp-todo", { key }, "TODO: " + arg];
  }

  // -------------------------------------------------------------- blocks ---

  const ENVS = ["abstract", "principle", "example", "takeaway", "caveat",
                "retraction", "quote"];

  function parseBlocks(src) {
    const lines = src.split("\n");
    const blocks = [];
    let file = "paper.md";
    let i = 0;

    const isBlank = (s) => !s.trim();

    while (i < lines.length) {
      const line = lines[i];

      // provenance marker written by the build's \input splicer
      const fm = /^%%FILE (.+)$/.exec(line);
      if (fm) { file = fm[1]; i++; continue; }
      // `%%` is a source comment — it is for whoever edits the .md, not for the
      // reader, and it must never reach the page as prose
      if (/^\s*%%/.test(line)) { i++; continue; }

      if (isBlank(line)) { i++; continue; }

      // ⚠⚠ A BLOCK MARKER MAY WRAP, AND A WRAPPED ONE USED TO VANISH.
      // These were matched line by line with `$`-anchored regexes, so
      // `\figure{outcomes}{a caption long enough to wrap}` split across two
      // lines matched nothing, fell through to the paragraph scanner, and was
      // DROPPED — taking its figure with it and leaving its `\label` to attach
      // to the preceding subsection, so `\ref{fig:outcomes}` rendered a section
      // number. Two figures shipped that way and nothing threw. So: if a line
      // opens a block marker whose braces do not balance by end of line, keep
      // joining lines until they do.
      if (/^\s*\\(section|subsection|label|figure|begin|end)\s*\{/.test(line)) {
        let joined = line, j = i;
        const balanced = (s) => {
          let d = 0;
          for (const ch of s) { if (ch === "{") d++; else if (ch === "}") d--; }
          return d === 0;
        };
        while (!balanced(joined) && j + 1 < lines.length) { j++; joined += " " + lines[j].trim(); }
        // `continue` so the loop re-reads the spliced line — `line` was bound
        // before the splice and would otherwise still hold the unjoined half.
        if (j !== i) { lines.splice(i, j - i + 1, joined); continue; }
      }

      let m;
      if ((m = /^\\(section|subsection)\{(.*)\}\s*$/.exec(line))) {
        blocks.push({ t: m[1], text: m[2], file }); i++; continue;
      }
      if ((m = /^\\label\{(.+)\}\s*$/.exec(line))) {
        blocks.push({ t: "label", id: m[1], file }); i++; continue;
      }
      if ((m = /^\\figure\{([^}]+)\}\{(.*)\}\s*$/.exec(line))) {
        blocks.push({ t: "figure", fig: m[1], cap: m[2], file }); i++; continue;
      }
      if ((m = /^\\begin\{([a-z]+)\}(?:\{(.*)\})?\s*$/.exec(line))) {
        if (ENVS.includes(m[1])) { blocks.push({ t: "env-open", env: m[1], arg: m[2] || "", file }); i++; continue; }
      }
      if ((m = /^\\end\{([a-z]+)\}\s*$/.exec(line))) {
        blocks.push({ t: "env-close", env: m[1], file }); i++; continue;
      }

      // fenced code
      if (/^```/.exec(line)) {
        const lang = line.slice(3).trim();
        const body = [];
        i++;
        while (i < lines.length && !/^```/.test(lines[i])) body.push(lines[i++]);
        i++;                                              // the closing fence
        blocks.push({ t: "code", lang, text: body.join("\n"), file });
        continue;
      }

      // list — one level, `- ` or `1. `
      if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
        const items = [];
        const ordered = /^\s*\d+\./.test(line);
        while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
          let txt = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, "");
          i++;
          // a continuation line is indented and not itself a bullet
          while (i < lines.length && /^\s+\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
            txt += " " + lines[i].trim(); i++;
          }
          items.push(txt);
        }
        // ⚠ Merge with an immediately preceding list of the same kind. A writer
        // separating numbered items by blank lines — which is normal markdown
        // and normal prose hygiene — otherwise produced N separate lists, every
        // one of them numbered "1". A reviser hit this and had to delete the
        // blank lines to work around it. `sawBlank` is not consulted on purpose:
        // two adjacent lists of the same kind are one list either way.
        const prev = blocks[blocks.length - 1];
        if (prev && prev.t === "list" && prev.ordered === ordered) {
          prev.items = prev.items.concat(items);
        } else {
          blocks.push({ t: "list", ordered, items, file });
        }
        continue;
      }

      // blockquote
      if (/^>\s?/.test(line)) {
        const body = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) { body.push(lines[i].replace(/^>\s?/, "")); i++; }
        blocks.push({ t: "quote", text: body.join(" ").trim(), file });
        continue;
      }

      // markdown table — a header row followed by a delimiter row
      if (/^\|/.test(line) && i + 1 < lines.length && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1])) {
        const cells = (s) => s.replace(/^\||\|$/g, "").split("|").map(c => c.trim());
        const head = cells(line);
        i += 2;
        const rows = [];
        while (i < lines.length && /^\|/.test(lines[i])) { rows.push(cells(lines[i])); i++; }
        blocks.push({ t: "table", head, rows, file });
        continue;
      }

      // Paragraph — runs to the next blank line or BLOCK-level marker.
      // ⚠ It must NOT break on any backslash: `\num{...}` and `\ref{...}` are
      // INLINE and legitimately start a line after a wrap. Breaking on `\`
      // dropped those lines silently — the paragraph ended, the next iteration
      // matched no block rule, and the line was skipped to avoid spinning.
      const BLOCK = /^\s*\\(section|subsection|label|figure|begin|end|input)\{/;
      const para = [];
      while (i < lines.length && !isBlank(lines[i])
             && !BLOCK.test(lines[i])
             && !/^(>|```|\s*([-*]|\d+\.)\s|%%|\|)/.test(lines[i])) {
        para.push(lines[i]); i++;
      }
      if (para.length) blocks.push({ t: "para", text: para.join(" "), file });
      else i++;                                            // never spin
    }
    return blocks;
  }

  // ------------------------------------------------------------ numbering --
  // Sections and subsections number as 1, 1.1; principles and examples number
  // independently and continuously, because they are the paper's spine and a
  // reader refers to "principle 3", not "the principle in section 4.2".

  function number(blocks) {
    const labels = {};
    const outline = [];
    let sec = 0, sub = 0, prin = 0, exa = 0, fig = 0;
    let pendingKind = null, pendingNum = null, pendingText = null;

    for (const b of blocks) {
      if (b.t === "section") {
        sec++; sub = 0; b.num = String(sec);
        outline.push({ num: b.num, text: b.text, level: 1 });
        pendingKind = "section"; pendingNum = b.num; pendingText = b.text;
      } else if (b.t === "subsection") {
        sub++; b.num = sec + "." + sub;
        outline.push({ num: b.num, text: b.text, level: 2 });
        pendingKind = "subsection"; pendingNum = b.num; pendingText = b.text;
      } else if (b.t === "figure") {
        fig++; b.num = String(fig);
        pendingKind = "figure"; pendingNum = "Figure " + fig; pendingText = b.cap;
      } else if (b.t === "env-open" && b.env === "principle") {
        prin++; b.num = String(prin);
        pendingKind = "principle"; pendingNum = "Principle " + prin; pendingText = b.arg;
      } else if (b.t === "env-open" && b.env === "example") {
        exa++; b.num = String(exa);
        pendingKind = "example"; pendingNum = "Example " + exa; pendingText = b.arg;
      } else if (b.t === "label") {
        if (pendingKind) labels[b.id] = { num: pendingNum, text: pendingText, kind: pendingKind };
      }
    }
    return { labels, outline, counts: { sec, prin, exa, fig } };
  }

  // --------------------------------------------------------------- render --

  function renderBlocks(blocks, ctx) {
    const out = [];
    // an environment collects its children until \end
    const stack = [];
    const push = (node) => (stack.length ? stack[stack.length - 1].kids : out).push(node);
    let k = 0;

    for (const b of blocks) {
      const key = "b" + (k++);
      if (b.t === "section") {
        push(["h2.pp-h2", { key, id: "pp-" + b.num },
          ["span.pp-secnum", b.num], " ", ...inline(b.text, ctx, key)]);
      } else if (b.t === "subsection") {
        push(["h3.pp-h3", { key, id: "pp-" + b.num },
          ["span.pp-secnum", b.num], " ", ...inline(b.text, ctx, key)]);
      } else if (b.t === "para") {
        push(["p.pp-p", { key }, ...inline(b.text, ctx, key)]);
      } else if (b.t === "list") {
        push([(b.ordered ? "ol" : "ul") + ".pp-list", { key },
          ...b.items.map((it, j) => ["li", { key: "i" + j }, ...inline(it, ctx, key + "i" + j)])]);
      } else if (b.t === "quote") {
        push(["blockquote.pp-quote", { key }, ...inline(b.text, ctx, key)]);
      } else if (b.t === "code") {
        push(["pre.pp-code", { key }, ["code", b.text]]);
      } else if (b.t === "table") {
        push(["div.table-wrap", { key },
          ["table.tbl",
            ["thead", ["tr", ...b.head.map((h, j) => ["th", { key: "h" + j }, ...inline(h, ctx, key + "h" + j)])]],
            ["tbody", ...b.rows.map((r, ri) => ["tr", { key: "r" + ri },
              ...r.map((c, ci) => ["td.wrap", { key: "c" + ci }, ...inline(c, ctx, key + ri + "c" + ci)])])]],
        ]);
      } else if (b.t === "figure") {
        push(["figure.pp-fig", { key, id: "pp-Figure " + b.num },
          ["div.pp-figbody", ctx.figure(b.fig)],
          ["figcaption.pp-cap",
            ["span.pp-figlab", "Figure " + b.num], " ", ...inline(b.cap, ctx, key + "c")],
        ]);
      } else if (b.t === "env-open") {
        stack.push({ env: b.env, arg: b.arg, num: b.num, key, kids: [] });
      } else if (b.t === "env-close") {
        const e = stack.pop();
        if (!e) continue;
        push(renderEnv(e, ctx));
      }
      // `label` renders nothing — it names the thing before it
    }
    // an unclosed environment still renders; losing the text would be worse
    while (stack.length) push(renderEnv(stack.pop(), ctx));
    return out;
  }

  // ⚠ An environment's ARGUMENT is prose too. It was passed through as a raw
  // string, so `\num`, `\ref` and `\pat` inside a `\begin{caveat}{…}` heading
  // rendered literally — a writer hit this and had to move two markers into the
  // body to work around it. Headings get the same inline pass as everything else.
  function renderEnv(e, ctx) {
    const argNodes = e.arg ? inline(e.arg, ctx, e.key + "a") : [];
    const head = {
      abstract: ["Abstract"],
      principle: ["Principle " + e.num],
      example: ["Example " + e.num],
      takeaway: ["In short"],
      caveat: e.arg ? argNodes : ["Caveat"],
      retraction: ["Retracted — ", ...argNodes],
      quote: null,
    }[e.env];
    const id = e.env === "principle" ? "pp-Principle " + e.num
             : e.env === "example" ? "pp-Example " + e.num : undefined;
    const named = (e.env === "principle" || e.env === "example") && e.arg;
    // ⚠ `quote` is the one environment whose argument is an ATTRIBUTION rather
    // than a heading, so it renders BELOW the quotation instead of above it —
    // and it renders at all, which it did not. `head` is null for `quote`, so
    // the argument was computed and then dropped on the floor: every
    // `\begin{quote}{results/SYNTHESIS.md}` in the corpus published an
    // unsourced quotation. In a report whose whole claim is that every sentence
    // can be traced, that is the worst possible thing to lose silently.
    return ["div.pp-env.pp-" + e.env, { key: e.key, id },
      head ? ["div.pp-envh", { key: "h" },
        ["span.pp-envl", ...head],
        named ? ["span.pp-envt", " — ", ...argNodes] : ["span", { key: "n" }, ""]]
        : ["span", { key: "h" }, ""],
      ["div.pp-envb", { key: "b" }, ...e.kids],
      (e.env === "quote" && e.arg)
        ? ["div.pp-envcite", { key: "c" }, "— ", ...argNodes]
        : ["span", { key: "c" }, ""],
    ];
  }

  // ----------------------------------------------------------------- api ---

  function render(doc, opts) {
    const o = opts || {};
    const blocks = parseBlocks(doc.body || "");
    const { labels, outline, counts } = number(blocks);
    const ctx = {
      nums: doc.nums || {},
      refs: doc.refs || {},
      labels,
      patterns: o.patterns || [],
      figure: o.figure || (() => ["div.pp-figmiss", "figure unavailable"]),
    };
    return { body: renderBlocks(blocks, ctx), outline, labels, counts, ctx };
  }

  g.PAPER = { render, parseBlocks, number, inline };
})(typeof globalThis !== "undefined" ? globalThis : this);
