// syntax.js — the tokenizer behind every code view on this site.
//
// Hand-rolled rather than vendored, for three reasons.  This codebase never
// uses innerHTML (see index.js `md()`), so a highlighter that emits HTML
// strings cannot be used at all — the output here is a token list that index.js
// turns into JSONML spans.  The corpus is 19k lines of this project's own C and
// Rust and contains none of the constructs that break hand-rolled lexers: zero
// raw strings, zero byte strings, zero nested block comments, zero
// line-continuations inside strings.  And the part that carries the real value,
// the Verus classification below, is custom work under any option.
//
// CORRECTNESS CONTRACT: the concatenation of every emitted token's text is
// byte-for-byte the input.  Nothing is dropped, nothing is duplicated, no
// character is silently reclassified out of existence.  `tools/check_syntax.mjs`
// asserts exactly that over all 184 cells and fails loudly if it ever stops
// holding — which is what makes a hand-rolled lexer safe to rely on here.
//
// Token classes are a READING AID, not a data encoding.  Unlike every chart on
// this site, colour here identifies nothing and groups nothing; it only helps a
// reader parse the code.  So these values are free to be chosen for legibility
// and need not stay clear of the rung palette.
//
// The exception is the Verus layer, which IS semantic.  Its four classes are
// chosen to match what this project actually asks of a proof:
//
//   spec    requires / ensures / invariant / decreases   — what is promised
//   proof   proof / assert / by / forall / lemma_*       — the work discharging it
//   ghost   spec fn / ghost / tracked / Seq / int / nat  — erased before codegen
//   trust   external_body / assume / #[verifier::...]    — NOT verified: the TCB
//
// The last one is the point.  `external_body` bodies and `assume` are the places
// the guarantee rests on an unchecked claim, and this project counts them in a
// column; highlighting them makes the trusted base visible in the source itself.

(function (g) {
  "use strict";

  const C_KW = set(`auto break case const continue default do else enum extern for goto if
    inline register restrict return sizeof static struct switch typedef union volatile while
    _Bool _Static_assert _Alignof asm`);
  const C_TY = set(`char double float int long short signed unsigned void bool
    size_t ssize_t ptrdiff_t intptr_t uintptr_t FILE
    int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t`);

  const RS_KW = set(`as async await break const continue crate dyn else enum extern false fn
    for if impl in let loop match mod move mut pub ref return self Self static struct super
    trait true type union unsafe use where while yield box`);
  const RS_TY = set(`bool char str f32 f64 i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize
    String Vec Option Result Box Some None Ok Err Copy Clone Default Iterator`);

  // ---- Verus, classified by what each construct does to the guarantee -------
  const V_SPEC = set(`requires ensures invariant decreases recommends
    invariant_except_break opens_invariants no_unwind returns`);
  const V_PROOF = set(`proof assert assert_by assert_forall_by by calc forall exists old
    reveal reveal_with_fuel hide choose implies lemma broadcast use_type_invariant`);
  const V_GHOST = set(`spec ghost tracked open closed exec verus int nat
    Seq Set Map Ghost Tracked Multiset FnSpec`);
  // Trusted, not verified.  Every one of these is a hole a reader must inspect.
  const V_TRUST = set(`external_body external_fn_specification external_type_specification
    assume assume_specification external external_trait_specification verifier`);

  function set(s) { return new Set(s.split(/\s+/).filter(Boolean)); }

  const isIdStart = (c) => (c >= "a" && c <= "z") || (c >= "A" && c <= "Z") || c === "_";
  const isId = (c) => isIdStart(c) || (c >= "0" && c <= "9");
  const isDigit = (c) => c >= "0" && c <= "9";

  // Classify one identifier for the given language.
  function classifyIdent(word, lang, nextCh, prevSig) {
    if (lang === "verus") {
      if (V_TRUST.has(word)) return "vtrust";
      if (V_SPEC.has(word)) return "vspec";
      if (V_PROOF.has(word) || /^lemma(_|$)/.test(word)) return "vproof";
      if (V_GHOST.has(word)) return "vghost";
    }
    if (lang === "c") {
      if (C_TY.has(word)) return "typ";
      if (C_KW.has(word)) return "kw";
    } else {
      if (RS_TY.has(word)) return "typ";
      if (RS_KW.has(word)) return "kw";
    }
    if (nextCh === "!") return "mac";
    if (nextCh === "(") return "fn";
    // Foo::bar and `struct Foo` style type names
    if (/^[A-Z]/.test(word)) return "typ";
    if (prevSig === "fn") return "fn";
    return null;                       // plain text: emitted without a span
  }

  // Tokenize `src`.  Returns [{t, s}] where `t` is null for unclassified text.
  function tokenize(src, lang) {
    src = String(src == null ? "" : src);
    lang = lang === "c" ? "c" : lang === "verus" ? "verus" : "rust";
    const out = [];
    const push = (t, s) => { if (s) out.push({ t: t, s: s }); };
    const n = src.length;
    let i = 0, plain = "";
    let prevSig = null;                // last significant word, for `fn name`

    const flush = () => { if (plain) { out.push({ t: null, s: plain }); plain = ""; } };

    while (i < n) {
      const c = src[i], c2 = src[i + 1];

      // ---- comments ----
      if (c === "/" && c2 === "/") {
        flush();
        let j = src.indexOf("\n", i); if (j < 0) j = n;
        push("com", src.slice(i, j)); i = j; continue;
      }
      if (c === "/" && c2 === "*") {
        flush();
        let j = src.indexOf("*/", i + 2);
        j = j < 0 ? n : j + 2;
        push("com", src.slice(i, j)); i = j; continue;
      }

      // ---- C preprocessor: whole directive, with <header> kept as a string ----
      if (lang === "c" && c === "#" && atLineStart(src, i)) {
        flush();
        let j = src.indexOf("\n", i); if (j < 0) j = n;
        const line = src.slice(i, j);
        const inc = /^(#\s*include\s*)(<[^>\n]*>)(.*)$/.exec(line);
        if (inc) { push("pre", inc[1]); push("str", inc[2]); push("pre", inc[3]); }
        else push("pre", line);
        i = j; continue;
      }

      // ---- Rust attribute: #[...] / #![...] , brackets balanced ----
      if (lang !== "c" && c === "#" && (c2 === "[" || (c2 === "!" && src[i + 2] === "["))) {
        flush();
        let j = src.indexOf("[", i), d = 0;
        while (j < n) { if (src[j] === "[") d++; else if (src[j] === "]") { d--; if (!d) { j++; break; } } j++; }
        const attr = src.slice(i, j);
        // an attribute naming a trusted construct IS the trusted marker
        push(/external_body|external_fn_specification|external_type_specification|\bexternal\b|verifier/.test(attr)
          && lang === "verus" ? "vtrust" : "mac", attr);
        i = j; continue;
      }

      // ---- strings ----
      if (c === '"') {
        flush();
        let j = i + 1;
        while (j < n) { if (src[j] === "\\") j += 2; else if (src[j] === '"') { j++; break; } else j++; }
        push("str", src.slice(i, Math.min(j, n))); i = Math.min(j, n); continue;
      }

      // ---- char literal vs Rust lifetime ----
      // 'a  is a lifetime;  'x'  and  '\n'  are chars.  The corpus has 3 of the
      // former and 4 of the latter, and this is the only real ambiguity in it.
      if (c === "'") {
        flush();
        if (lang !== "c" && isIdStart(c2 || "") && src[i + 2] !== "'") {
          let j = i + 1; while (j < n && isId(src[j])) j++;
          push("typ", src.slice(i, j)); i = j; continue;   // lifetime
        }
        let j = i + 1;
        while (j < n) { if (src[j] === "\\") j += 2; else if (src[j] === "'") { j++; break; } else j++; }
        push("str", src.slice(i, Math.min(j, n))); i = Math.min(j, n); continue;
      }

      // ---- numbers ----
      if (isDigit(c)) {
        flush();
        let j = i;
        while (j < n && /[0-9a-fA-FxXbBoO_.]/.test(src[j])) j++;
        while (j < n && isId(src[j])) j++;               // suffix: 12u64, 3usize
        push("num", src.slice(i, j)); i = j; continue;
      }

      // ---- identifiers ----
      if (isIdStart(c)) {
        let j = i; while (j < n && isId(src[j])) j++;
        const word = src.slice(i, j);
        let k = j; while (k < n && (src[k] === " " || src[k] === "\t")) k++;
        const cls = classifyIdent(word, lang, src[k], prevSig);
        if (cls) { flush(); push(cls, word); } else plain += word;
        prevSig = word;
        i = j; continue;
      }

      plain += c;
      i++;
    }
    flush();
    return out;
  }

  function atLineStart(src, i) {
    for (let j = i - 1; j >= 0; j--) {
      const c = src[j];
      if (c === "\n") return true;
      if (c !== " " && c !== "\t") return false;
    }
    return true;
  }

  // Split a token stream into lines, preserving each token's class across a
  // newline — which is why tokenizing happens over the whole text first and not
  // line by line: block comments and strings span lines.
  function toLines(tokens) {
    const lines = [[]];
    for (const tk of tokens) {
      const parts = tk.s.split("\n");
      for (let i = 0; i < parts.length; i++) {
        if (i) lines.push([]);
        if (parts[i]) lines[lines.length - 1].push({ t: tk.t, s: parts[i] });
      }
    }
    return lines;
  }

  function tokenizeLines(src, lang) { return toLines(tokenize(src, lang)); }

  // ---- x86 AT&T assembly, for the kernel-diff view ------------------------
  // A separate, much smaller pass: the input is one normalised instruction per
  // line, produced by harness/asm.py, so there are no strings, no comments and
  // no multi-line anything.  Immediates and branch targets have already been
  // erased by normalisation — `sub $,%rsp`, `jb TGT` — which is why `$` and
  // `TGT` are marked as the redactions they are rather than as values.
  const ASM_JUMP = /^(j\w+|call|ret|leave|ud2|hlt|syscall)$/;
  const ASM_MEM = /^(mov|movz|movs|lea|push|pop|xchg|cmov\w+)/;

  function tokenizeAsm(line) {
    const out = [];
    // leading mnemonic, plus any prefix (`lock`, `rep`, `cs`, ...)
    const m = /^(\s*)([a-z0-9.]+)(\s*)(.*)$/.exec(line);
    if (!m) return [{ t: null, s: line }];
    if (m[1]) out.push({ t: null, s: m[1] });
    const mn = m[2];
    out.push({
      t: ASM_JUMP.test(mn) ? "asm-jmp" : ASM_MEM.test(mn) ? "asm-mov" : "asm-op",
      s: mn,
    });
    if (m[3]) out.push({ t: null, s: m[3] });

    // operands: registers, the erased-immediate marker, the erased target
    const rest = m[4];
    const re = /(%[a-z0-9]+)|(\$[-\w]*)|(\bTGT\b)|(0x[0-9a-f]+)|([^%$\w]+)|(\w+)/gi;
    let mm;
    while ((mm = re.exec(rest))) {
      if (mm[1]) out.push({ t: "asm-reg", s: mm[1] });
      else if (mm[2]) out.push({ t: "asm-imm", s: mm[2] });
      else if (mm[3]) out.push({ t: "asm-tgt", s: mm[3] });
      else if (mm[4]) out.push({ t: "asm-imm", s: mm[4] });
      else out.push({ t: null, s: mm[0] });
    }
    return out;
  }

  // The language to tokenize a cell as.  Everything is `lang` from build_data.py
  // except the Verus rung, which is Rust plus the proof layer.
  function langFor(cell, declared) {
    if (cell === "verus" || cell === "safe_naive_verus") return "verus";
    return declared === "c" ? "c" : "rust";
  }

  g.SYNTAX = {
    tokenize: tokenize, tokenizeLines: tokenizeLines, toLines: toLines,
    langFor: langFor, tokenizeAsm: tokenizeAsm,
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
