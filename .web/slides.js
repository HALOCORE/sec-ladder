// slides.js — a very small deck engine for this site, in JSONML.
//
// WHY THIS EXISTS, AND WHY IT IS NOT A GENERIC SLIDE LIBRARY.
//
// The talk it renders has one rule, inherited from the paper it accompanies:
// **every slide exists because somebody in the room just asked a question.**  A
// slide that cannot name its question is a slide full of things the speaker
// found interesting, which is the failure mode the paper spent five framings
// escaping.
//
// So the rule is enforced in the constructor rather than in a style guide:
// `ask()` takes the question, and EVERY OTHER SLIDE KIND REQUIRES `q` — the
// question it is answering — and `build()` throws without one.  The question is
// then rendered on the slide, in the audience's voice, above the answer.  You
// cannot quietly add an interesting-but-unmotivated slide to this deck; the
// build fails.
//
// Everything here emits JSONML for Incremental DOM.  There is no innerHTML on
// this page and there is none here either (`.web/CLAUDE.md`).
//
//   const deck = SLIDES.build(D => [ S.title(...), S.ask(...), S.answer(...) ])
//   SLIDES.view(deck, { i, full, on })   ->  JSONML
//
// `D` is the live-data helper handed to the deck body at BUILD time, which is
// render time: `D.n("totals.passing.patterns")` resolves against
// data/index.json exactly like the paper's `\num{}`, so a count in the talk
// cannot go stale either.  ⚠ See `paper_vers/README.md`: that keeps a NUMBER
// live, it does not keep a SENTENCE true — a denominator's meaning can still
// move underneath you, which is why the totals used here are `totals.passing`.

(function (g) {
  "use strict";

  // ------------------------------------------------------------ live data ---

  function makeHelper(data) {
    const at = (path) => {
      let o = data;
      for (const k of String(path).split(".")) {
        if (o == null) return undefined;
        o = o[k];
      }
      return o;
    };
    const fmt = (v) => (typeof v === "number" ? v.toLocaleString("en-US") : String(v));
    return {
      // a total, thousands-separated — the deck's `\num{}`
      n(path) {
        const v = at("totals." + path);
        return v === undefined ? "?" + path : fmt(v);
      },
      // a total, unformatted (for small counts where a comma reads as a typo)
      raw(path) {
        const v = at("totals." + path);
        return v === undefined ? "?" + path : String(v);
      },
      // kernel-exclusive Ir/call for one pattern/band/cell, straight off the
      // same table the paper quotes, so the two cannot drift apart
      ir(pid, band, cell) {
        const p = (data.patterns || []).find(x => x.id.startsWith(pid));
        const row = p && p.kern && p.kern["isolated/" + band + ".bin"];
        const c = row && row.cells && row.cells[cell];
        return c ? fmt(Math.round(c.ir)) : "?" + pid + "/" + cell;
      },
      // the same, as a signed difference against the unsafe rung
      delta(pid, band, cell) {
        const p = (data.patterns || []).find(x => x.id.startsWith(pid));
        const row = p && p.kern && p.kern["isolated/" + band + ".bin"];
        const c = row && row.cells && row.cells[cell];
        if (!c) return "?" + pid + "/" + cell;
        const d = Math.round(c.delta);
        return (d > 0 ? "+" : "") + fmt(d);
      },
    };
  }

  // -------------------------------------------------------------- slides ----
  //
  // Each constructor returns a plain object.  `q` is the audience question the
  // slide answers and is MANDATORY on every kind except `title` and `end`.

  const WHY = {
    q: "every slide must name the question from the floor that it answers",
    head: "an answer slide needs its answer in one sentence; if you cannot write that line, the slide is not an answer yet",
  };
  const need = (o, k, kind) => {
    if (!o || o[k] === undefined || o[k] === null || o[k] === "")
      throw new Error(`slides: ${kind} slide is missing "${k}" — ` +
        (WHY[k] || `${kind} slides require it`));
    return o[k];
  };

  const S = {
    // The opening slide.  No question, because none has been asked yet.
    title: (o) => ({ kind: "title", title: need(o, "title", "title"), sub: o.sub || "", foot: o.foot || "" }),

    // A full-bleed objection, in the audience's own voice.  This is the only
    // slide kind that asks rather than answers, and it opens every section.
    ask: (q, o) => ({ kind: "ask", q: String(q), n: (o || {}).n || "", cue: (o || {}).cue || "" }),

    // Headline answer plus supporting lines.  `head` is the answer in one
    // sentence; if you cannot write it, the slide is not an answer.
    answer: (o) => ({ kind: "answer", q: need(o, "q", "answer"), head: need(o, "head", "answer"),
                      body: o.body || [], aside: o.aside || "", tone: o.tone || "" }),

    // A table.  `cols[0]` is the row label column.
    table: (o) => ({ kind: "table", q: need(o, "q", "table"), head: o.head || "",
                     cols: need(o, "cols", "table"), rows: need(o, "rows", "table"),
                     note: o.note || "", hi: o.hi || [] }),

    // Source, rendered through syntax.js like every other code view here.
    code: (o) => ({ kind: "code", q: need(o, "q", "code"), head: o.head || "",
                    lang: o.lang || "rust", src: need(o, "src", "code"), note: o.note || "" }),

    // A line worth reading out loud, and where it came from.
    quote: (o) => ({ kind: "quote", q: need(o, "q", "quote"), text: need(o, "text", "quote"),
                     src: o.src || "" }),

    // Two columns — for a contrast the audience should hold side by side.
    two: (o) => ({ kind: "two", q: need(o, "q", "two"), head: o.head || "",
                   left: need(o, "left", "two"), right: need(o, "right", "two"), note: o.note || "" }),

    // The closing slide.
    end: (o) => ({ kind: "end", head: need(o, "head", "end"), body: o.body || [] }),
  };

  // --------------------------------------------------------------- build ----

  function build(body, data) {
    const D = makeHelper(data || { totals: {}, patterns: [] });
    const raw = body(D, S) || [];
    const slides = [];
    let section = "";
    for (const s of raw) {
      if (!s || !s.kind) continue;
      if (s.kind === "ask") section = s.q;
      slides.push(Object.assign({ section }, s));
    }
    return { slides, D };
  }

  // ---------------------------------------------------------------- view ----

  // ⚠⚠ EVERY TEXT-BEARING FIELD GOES THROUGH THIS.  Four slides shipped literal
  // backticks and asterisks to the screen because the question banner, a quote's
  // source and the two-column headings were pushed as raw strings — the same
  // defect class as the paper outline (LESSONS.md 14c).  `md()` is not optional
  // on prose, and every one of these fields is prose.  If you add a field that
  // renders text, wrap it in MD() or it WILL ship its own markup.
  const MD = (s) => (g.md ? g.md(String(s == null ? "" : s)) : [String(s == null ? "" : s)]);

  const lines = (arr, key) => (arr || []).map((t, i) =>
    ["li.sl-li", { key: key + i }, ...MD(t)]);

  function slideBody(s) {
    switch (s.kind) {
      case "title":
        return ["div.sl-mid", { key: "b" },
          ["div.sl-title", ...MD(s.title)],
          s.sub ? ["div.sl-sub", { key: "s" }, ...MD(s.sub)] : ["span", { key: "s" }, ""],
          s.foot ? ["div.sl-foot", { key: "f" }, ...MD(s.foot)] : ["span", { key: "f" }, ""]];

      case "ask":
        return ["div.sl-mid", { key: "b" },
          ["div.sl-askmark", "“"],
          ["div.sl-ask", ...MD(s.q)],
          s.cue ? ["div.sl-cue", { key: "c" }, ...MD(s.cue)] : ["span", { key: "c" }, ""]];

      case "answer":
        return ["div.sl-body", { key: "b" },
          ["div.sl-head" + (s.tone ? ".t-" + s.tone : ""), ...MD(s.head)],
          s.body.length ? ["ul.sl-ul", { key: "u" }, ...lines(s.body, "l")] : ["span", { key: "u" }, ""],
          s.aside ? ["div.sl-aside", { key: "a" }, ...MD(s.aside)] : ["span", { key: "a" }, ""]];

      case "table":
        return ["div.sl-body", { key: "b" },
          s.head ? ["div.sl-head", { key: "h" }, ...MD(s.head)] : ["span", { key: "h" }, ""],
          ["div.sl-tw", { key: "t" },
            ["table.sl-tbl",
              ["thead", ["tr", ...s.cols.map((c, i) => ["th" + (i ? ".num" : ""), { key: "c" + i }, ...MD(c)])]],
              ["tbody", ...s.rows.map((r, ri) => ["tr" + (s.hi.indexOf(ri) >= 0 ? ".hi" : ""), { key: "r" + ri },
                ...r.map((cell, ci) => ["td" + (ci ? ".num" : ""), { key: "d" + ci },
                  ...MD(cell)])])]]],
          s.note ? ["div.sl-aside", { key: "n" }, ...MD(s.note)] : ["span", { key: "n" }, ""]];

      case "code": {
        // Through syntax.js, like every other code view here — tokens, never an
        // HTML string.  Same `tk-` classes, so the deck inherits the site's
        // one code theme instead of inventing a second one.
        const toks = g.SYNTAX ? g.SYNTAX.tokenize(s.src, s.lang) : null;
        return ["div.sl-body", { key: "b" },
          s.head ? ["div.sl-head", { key: "h" }, ...MD(s.head)] : ["span", { key: "h" }, ""],
          ["pre.sl-code", { key: "p" }, ["code", ...(toks
            ? toks.map((t, i) => (t.t ? ["span.tk-" + t.t, { key: "t" + i }, t.s] : t.s))
            : [s.src])]],
          s.note ? ["div.sl-aside", { key: "n" }, ...MD(s.note)] : ["span", { key: "n" }, ""]];
      }

      case "quote":
        return ["div.sl-mid", { key: "b" },
          ["div.sl-quote", ...MD(s.text)],
          s.src ? ["div.sl-qsrc", { key: "s" }, ...MD(s.src)] : ["span", { key: "s" }, ""]];

      case "two":
        return ["div.sl-body", { key: "b" },
          s.head ? ["div.sl-head", { key: "h" }, ...MD(s.head)] : ["span", { key: "h" }, ""],
          ["div.sl-two", { key: "t" },
            ["div.sl-col", ["div.sl-coth", ...MD(s.left.h || "")], ["ul.sl-ul", ...lines(s.left.body, "L")]],
            ["div.sl-col", ["div.sl-coth", ...MD(s.right.h || "")], ["ul.sl-ul", ...lines(s.right.body, "R")]]],
          s.note ? ["div.sl-aside", { key: "n" }, ...MD(s.note)] : ["span", { key: "n" }, ""]];

      case "end":
        return ["div.sl-mid", { key: "b" },
          ["div.sl-title.sm", ...MD(s.head)],
          s.body.length ? ["ul.sl-ul.wide", { key: "u" }, ...lines(s.body, "e")] : ["span", { key: "u" }, ""]];

      default:
        return ["div.sl-body", { key: "b" }, ""];
    }
  }

  // The question banner.  It is on EVERY answering slide, always, because it is
  // the reason the slide is allowed to exist.
  function qbar(s) {
    if (s.kind === "title" || s.kind === "ask" || s.kind === "end")
      return ["div.sl-qbar.empty", { key: "q" }, ""];
    return ["div.sl-qbar", { key: "q" },
      ["span.sl-qlab", "they asked"],
      ["span.sl-qtext", ...MD("“" + s.q + "”")]];
  }

  function view(deck, st) {
    const n = deck.slides.length;
    const i = Math.max(0, Math.min(n - 1, st.i | 0));
    const s = deck.slides[i] || { kind: "title", title: "" };
    const on = st.on || {};
    const pct = n > 1 ? (i / (n - 1)) * 100 : 0;

    return ["div.deck" + (st.full ? ".is-full" : ""), { key: "deck" },
      ["div.deck-stage", { key: "stage" },
        ["div.slide.k-" + s.kind, { key: "slide" },
          qbar(s),
          slideBody(s),
          ["div.sl-num", { key: "n" }, (i + 1) + " / " + n],
        ],
      ],
      ["div.deck-bar", { key: "bar" },
        ["button.deck-b", { key: "p", onclick: on.prev, disabled: i === 0 ? "disabled" : undefined,
                            title: "previous slide" }, "‹"],
        ["button.deck-b", { key: "x", onclick: on.next, disabled: i === n - 1 ? "disabled" : undefined,
                            title: "next slide" }, "›"],
        ["div.deck-prog", { key: "pr" }, ["div.deck-progfill", { style: "width:" + pct.toFixed(1) + "%" }, ""]],
        ["div.deck-sec", { key: "sc" }, s.section ? "“" + s.section + "”" : (s.kind === "title" ? "opening" : "")],
        ["button.deck-b.wide", { key: "f", onclick: on.toggleFull,
                                 title: st.full ? "leave full screen (Esc)" : "expand to full screen" },
          st.full ? "✕  close" : "⤢  expand"],
      ],
    ];
  }

  g.SLIDES = { build, view, S, makeHelper };
})(typeof globalThis !== "undefined" ? globalThis : this);
