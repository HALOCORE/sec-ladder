#!/usr/bin/env python3
"""Structural parsing of a Verus/Rust source file: items, attributes, clauses.

This module exists because the previous version of the check was a regex over
`prefix.split("\\n\\n")[-1]`, and a single blank line between
`#[verifier::external_body]` and `fn main` hid the attribute completely
(TASK_002_REVIEW, B1). That is the pilot's fatal defect -- an `external_body`
`main` discharges no precondition, so the proof constrains nothing -- and the
gate reported 28/28 PASS with it in the tree.

Three things the naive regex got wrong and this does not:

  * **Attributes are found by walking backwards over the real token stream**,
    not by splitting on a blank line. Whitespace and comments between an
    attribute and its item are skipped; a `}` or `;` terminates the walk, so an
    attribute can never be stolen from the previous item.
  * **Comments and string literals are blanked before anything is searched.**
    `// calls kernel(...)` used to satisfy the "there is a verified call site"
    check all by itself (`check.py:411`).
  * **`external_body` is matched wherever it appears in an attribute**, so
    `#[cfg_attr(all(), verifier::external_body)]` counts. The previous regex
    only matched a bare `#[verifier::external_body]`.

It also extracts `requires`/`ensures`/`decreases` clause *text* per item, which
is what lets `spec.md` pin a contract and the gate diff against it. The pin is
the only mechanical defence against the project's worst known vacuity mode:
deleting a `requires` from an `#[verifier::external_body]` wrapper verifies
cleanly and moves no obligation count (`.memory/04-verus.md`).

Not a Rust parser. It is a bracket-matcher that knows about comments, strings,
raw strings and char literals, which is enough for the shape our rung files
have and fails *loudly* (raises) rather than quietly when it is not.
"""

import re
import sys

# Clause keywords that may follow a Verus signature, in any order.
CLAUSE_KEYWORDS = ("requires", "ensures", "recommends", "decreases",
                   "opens_invariants", "no_unwind", "returns", "when")

# Item modifiers that may sit between the attributes and `fn`.
_MODIFIERS = {"pub", "exec", "open", "closed", "uninterp", "unsafe", "const",
              "async", "extern", "default", "broadcast", "axiom"}

_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"


# --------------------------------------------------------------------------

def blank_noncode(text, keep_strings=False):
    """Return `text` with comments, string and char literals replaced by spaces
    of the same length, so offsets are preserved and every search below sees
    only code. Newlines are kept so line numbers still work.

    `keep_strings=True` blanks **comments only** and leaves string and char
    literals verbatim -- still skipping over them, so a `//` or `/*` inside a
    string is not mistaken for a comment. That is what `blank_comments` below
    wants: it needs the clause's real text back, and blanking a string literal
    inside a clause would change what `spec.md` pins."""
    out = list(text)
    i, n = 0, len(text)

    def blank(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            depth, j = 1, i + 2          # Rust block comments nest
            while j < n and depth:
                if text.startswith("/*", j):
                    depth += 1
                    j += 2
                elif text.startswith("*/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            blank(i, j)
            i = j
        elif c == "r" and re.match(r'r#*"', text[i:i + 8] or ""):
            m = re.match(r'r(#*)"', text[i:])
            close = '"' + m.group(1)
            j = text.find(close, i + m.end())
            j = n if j < 0 else j + len(close)
            if not keep_strings:
                blank(i, j)
            i = j
        elif c == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            if not keep_strings:
                blank(i, j)
            i = j
        elif c == "'":
            # char literal or lifetime; only blank a real char literal
            m = re.match(r"'(\\.|[^\\'])'", text[i:])
            if m:
                if not keep_strings:
                    blank(i, i + m.end())
                i += m.end()
            else:
                i += 1
        else:
            i += 1
    return "".join(out)


def blank_comments(text):
    """`text` with **comments only** blanked to spaces of the same length.

    A COMMENT IS NOT CLAUSE TEXT. `_clause_split` used to run over the raw
    signature text, so `vparse` handed a comment inside a `requires` list back
    as clause text -- as its own clause when it trailed, glued onto the front of
    the next clause when it preceded (the newline having been collapsed by
    `norm_clause`). Two things went wrong with that, and TASK_053 F4 measured
    both:

      * `check.py`'s parameter-coverage rule (`_check_trusted_unsafe`) is a bag
        of identifiers taken from the joined `requires` text, so a parameter
        named only in a COMMENT counted as constrained. An `external_body` item
        whose body reads `*v.get_unchecked(i + n)` with nothing constraining `n`
        passed the rule on the strength of the trailing comment
        "// n is bounded by the caller". That is the rule TASK_006_REVIEW added
        precisely because no verify/fail oracle can catch a weak trusted
        precondition.
      * `item.clauses[kw]` and `clause_spans(item)[kw]["spans"]` are documented
        as parallel lists, and they were not: `clause_spans` works on the
        blanked copy and therefore already drops a comment-only clause and
        already trims a leading comment, so a comment made the two lists
        different lengths and `requires[idx]` labels slid by one.

    Blanking comments in `_clause_split` fixes both at once and makes the two
    lists agree by construction. Strings are left alone deliberately -- they are
    code, and blanking one would move a `spec.md` pin."""
    return blank_noncode(text, keep_strings=True)


def _match_bracket(code, i):
    """Index just past the bracket opened at `code[i]`. `code` must already be
    comment/string-blanked."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    close = pairs[code[i]]
    depth, j = 0, i
    while j < len(code):
        if code[j] in pairs:
            depth += 1
        elif code[j] in ")]}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError(f"vparse: unbalanced {code[i]!r} at offset {i}")


def _match_angle(code, i):
    """Index just past the `<` opened at `code[i]`.

    Angle brackets are not brackets -- `->`, `=>` and comparison operators all
    contain one of the characters -- so this skips the two arrows explicitly and
    recurses through any real bracket it meets (`<F: Fn(u8) -> u8>`). Raises
    rather than guessing: a generic list this cannot read must fail the caller
    loudly, because the caller is synthesising code from it."""
    if code[i] != "<":
        raise ValueError(f"vparse: no '<' at offset {i}")
    depth, j = 0, i
    while j < len(code):
        if code.startswith("->", j) or code.startswith("=>", j):
            j += 2
            continue
        c = code[j]
        if c in "([{":
            j = _match_bracket(code, j)
            continue
        if c in ")]}":
            raise ValueError(f"vparse: unbalanced '<' at offset {i}")
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError(f"vparse: unbalanced '<' at offset {i}")


def attribute_spans(code):
    """[(start, end)] of every `#[...]` / `#![...]` in the blanked code."""
    spans = []
    for m in re.finditer(r"#!?\[", code):
        try:
            spans.append((m.start(), _match_bracket(code, m.end() - 1)))
        except ValueError:
            continue
    return spans


def verus_span(text, code=None):
    """(start, end) of the body of the outermost `verus! { ... }`, by brace
    matching. The previous version located the end with a literal
    `^}\\s*//\\s*verus!` comment, so deleting the comment moved every item
    'outside' the block (`check.py:511`)."""
    code = code if code is not None else blank_noncode(text)
    m = re.search(r"\bverus!\s*[{(\[]", code)
    if not m:
        return None
    open_at = m.end() - 1
    return open_at + 1, _match_bracket(code, open_at) - 1


# --------------------------------------------------------------------------

class Item:
    """One `fn` / `spec fn` / `proof fn`, with everything the gate asks about.

    `sig_start` / `body_start` are absolute offsets into the *original* text, so
    a caller can perform surgery on one clause without re-finding it. That is
    what `clause_spans` and `delete_clause` are for: the clause-deletion gate
    stage has to produce a mutant per clause, and a regex that re-locates the
    clause would be a second, drifting parser."""

    __slots__ = ("name", "kind", "start", "sig", "sig_code", "sig_start",
                 "body", "body_start", "body_end", "attrs", "external",
                 "clauses", "in_verus", "line", "cfg_gated", "mod_path",
                 "impl_span", "impl_head")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    @property
    def body_lines(self):
        return len([l for l in (self.body or "").splitlines() if l.strip()])

    def calls(self, name):
        """Does the body contain a real call to `name(`? Comments do not count
        -- `self.body` is the comment-blanked text."""
        return re.search(r"\b" + re.escape(name) + r"\s*\(", self.body or "") is not None

    def __repr__(self):
        return (f"Item({self.name!r}, kind={self.kind!r}, external={self.external!r}, "
                f"in_verus={self.in_verus}, cfg_gated={self.cfg_gated!r}, "
                f"mod_path={self.mod_path!r}, "
                f"clauses={ {k: v for k, v in self.clauses.items() if v} })")


def _clause_split(text):
    """Split a clause list on top-level commas.

    Comments are blanked first (`blank_comments`), so a comment-only clause is
    dropped and a comment beside a clause does not become part of that clause's
    text -- which is what `clause_spans` has always done, and what makes the two
    parallel. It also means a `,`, `(` or `)` inside a comment can no longer
    move the split. TASK_053 F4."""
    text = blank_comments(text)
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            if cur.strip():
                out.append(norm_clause(cur))
            cur = ""
            continue
        cur += ch
    if cur.strip():
        out.append(norm_clause(cur))
    return out


def norm_clause(s):
    """Whitespace-canonical form of one clause, for diffing against `spec.md`.

    Whitespace only: the pin is meant to be sensitive to `r == r` vs
    `r == sum_wrap(...)`, so nothing semantic is normalised away."""
    return re.sub(r"\s+", " ", s).strip()


def _parse_clauses(sig_code, sig_text):
    """{keyword: [clause, ...]} from a signature's clause region."""
    hits = []
    for kw in CLAUSE_KEYWORDS:
        for m in re.finditer(r"\b" + kw + r"\b", sig_code):
            # only at bracket depth 0
            pre = sig_code[:m.start()]
            if sum(pre.count(c) for c in "([{") == sum(pre.count(c) for c in ")]}"):
                hits.append((m.start(), m.end(), kw))
    hits.sort()
    out = {kw: [] for kw in CLAUSE_KEYWORDS}
    for idx, (s, e, kw) in enumerate(hits):
        end = hits[idx + 1][0] if idx + 1 < len(hits) else len(sig_code)
        out[kw] = _clause_split(sig_text[e:end])
    return out


_CFG_RE = re.compile(r"#!?\[\s*cfg\s*\(")


def _attrs_before(code, text, pos, attr_end):
    """Every `#[...]` immediately preceding the item that starts at `pos`.

    Walks backwards over the real token stream: whitespace and comments are
    skipped (they are already blanked), and anything that is not the `]` of an
    attribute -- a `}`, `;`, `{` -- stops the walk, so an attribute can never be
    stolen from the previous item."""
    out, p = [], pos
    while True:
        q = len(code[:p].rstrip())
        if q == 0 or code[q - 1] != "]":
            break
        span = attr_end.get(q)
        if span is None:
            break
        out.insert(0, text[span[0]:span[1]])
        p = span[0]
    return out, p


def module_spans(text, code=None):
    """[(name, body_start, body_end, cfg_gated)] for every `mod NAME { ... }`.

    An item inside a `#[cfg(...)] mod` may not exist in the build at all, so it
    must never be allowed to supply a pinned contract for the item that does
    (TASK_003_REVIEW: a decoy `fn kernel` in a `#[cfg(any())] mod` fed the pin
    while the real, weakened kernel was the one measured)."""
    code = code if code is not None else blank_noncode(text)
    attr_end = {e: (s, e) for s, e in attribute_spans(code)}
    out = []
    for m in re.finditer(r"\bmod\s+(" + _IDENT + r")\s*\{", code):
        start = m.start()
        # `pub mod`, `pub(crate) mod`, ... -- step back over modifiers
        pre = code[:start].rstrip()
        w = re.search(r"(" + _IDENT + r")$", pre)
        if w and w.group(1) in _MODIFIERS:
            start = w.start()
        mattrs, _ = _attrs_before(code, text, start, attr_end)
        open_at = m.end() - 1
        end = _match_bracket(code, open_at)
        out.append((m.group(1), open_at + 1, end - 1,
                    any(_CFG_RE.match(a.replace(" ", "")) or
                        re.match(r"#!?\[\s*cfg\s*\(", a) for a in mattrs)))
    return out


def impl_spans(text, code=None):
    """[(head, body_start, body_end)] for every `impl ... { ... }` block.

    Needed by the `requires`-tautology probe: a trusted accessor with a `&self`
    receiver cannot be copied into a free function -- *"`self` parameter is only
    allowed in associated functions"* -- so the probe is synthesised **inside
    the same `impl`**, where `self`, the impl's generics and its `Self` type are
    all in scope. Without this a pattern whose trusted item is method-shaped
    hard-fails the gate and cannot be greened at all (TASK_008_REVIEW, major C).

    `impl` is only recognised at item position (preceded by nothing, `{`, `}` or
    `;`), so a `-> impl Iterator<...>` return type is not mistaken for a block.
    An `impl` this cannot read is simply not reported, and the probe then
    refuses with a named reason rather than emitting code that will not
    compile."""
    code = code if code is not None else blank_noncode(text)
    out = []
    for m in re.finditer(r"\bimpl\b", code):
        pre = code[:m.start()].rstrip()
        if pre and pre[-1] not in "{};":
            continue                       # `-> impl Trait`, `dyn impl`, ...
        j, body = m.end(), None
        try:
            while j < len(code):
                if code.startswith("->", j) or code.startswith("=>", j):
                    j += 2
                    continue
                c = code[j]
                if c == "<":
                    j = _match_angle(code, j)
                    continue
                if c in "([":
                    j = _match_bracket(code, j)
                    continue
                if c == "{":
                    body = j
                    break
                if c == ";":
                    break                  # `impl` used in a way we don't model
                j += 1
        except ValueError:
            continue
        if body is None:
            continue
        try:
            end = _match_bracket(code, body)
        except ValueError:
            continue
        out.append((text[m.start():body].strip(), body + 1, end - 1))
    return out


def parse(text):
    """Every `fn`-like item in `text`, in source order.

    A **list**, not a dict. `check.py` used to key these by name and the last
    one won, so a decoy item could supply the pinned contract for the real one
    (TASK_003_REVIEW). Callers that want a mapping must decide what a duplicate
    means; `duplicate_names()` is here for that."""
    code = blank_noncode(text)
    vs = verus_span(text, code)
    attrs = attribute_spans(code)
    attr_end = {e: (s, e) for s, e in attrs}
    mods = module_spans(text, code)
    impls = impl_spans(text, code)
    items = []

    for m in re.finditer(r"\bfn\s+(" + _IDENT + r")", code):
        name = m.group(1)
        # --- kind: walk back over modifiers to find the item's real start ----
        pos, kind_words = m.start(), []
        while True:
            pre = code[:pos].rstrip()
            w = re.search(r"(" + _IDENT + r")$", pre)
            if not w or w.group(1) not in _MODIFIERS | {"spec", "proof"}:
                break
            kind_words.insert(0, w.group(1))
            pos = w.start() + (len(code[:pos]) - len(pre))
            pos = w.start()
        kind = "fn"
        if "spec" in kind_words:
            kind = "spec fn"
        elif "proof" in kind_words:
            kind = "proof fn"

        # --- attributes: skip whitespace backwards, absorb every `#[...]` ----
        my_attrs, item_start = _attrs_before(code, text, pos, attr_end)

        # --- signature / body ------------------------------------------------
        j, depth = m.end(), 0
        body_open = None
        while j < len(code):
            c = code[j]
            if c in "([":
                depth += 1
            elif c in ")]":
                depth -= 1
            elif c == "{" and depth == 0:
                body_open = j
                break
            elif c == ";" and depth == 0:
                break                       # a trait method declaration
            j += 1
        if body_open is None:
            continue
        sig_text = text[m.end():body_open]
        sig_code = code[m.end():body_open]
        body_end = _match_bracket(code, body_open)
        body = code[body_open + 1:body_end - 1]

        ext = None
        for a in my_attrs:
            if re.search(r"\bexternal_body\b", a):
                ext = "verifier::external_body"
                break
            if re.search(r"\bverifier::external\b", a):
                ext = "verifier::external"
                break
        enclosing = [mm for mm in mods if mm[1] <= m.start() < mm[2]]
        in_impl = [ii for ii in impls if ii[1] <= m.start() < ii[2]]
        inner_impl = max(in_impl, key=lambda ii: ii[1]) if in_impl else None
        gated = None
        if any(re.match(r"#!?\[\s*cfg\s*\(", a) for a in my_attrs):
            gated = "own #[cfg(...)]"
        else:
            for mn, _, _, mcfg in enclosing:
                if mcfg:
                    gated = f"#[cfg(...)] mod {mn}"
                    break
        items.append(Item(
            name=name, kind=kind, start=item_start, sig=sig_text, body=body,
            sig_code=sig_code, sig_start=m.end(), body_start=body_open + 1,
            body_end=body_end - 1, attrs=my_attrs, external=ext,
            clauses=_parse_clauses(sig_code, sig_text),
            in_verus=bool(vs) and vs[0] <= m.start() < vs[1],
            line=text.count("\n", 0, item_start) + 1,
            cfg_gated=gated,
            mod_path="::".join(mm[0] for mm in enclosing),
            impl_span=None if inner_impl is None else (inner_impl[1], inner_impl[2]),
            impl_head=None if inner_impl is None else inner_impl[0],
        ))
    return items


# --------------------------------------------------------------------------
# clause surgery -- what the clause-deletion gate stage is built on
# --------------------------------------------------------------------------

def clause_spans(item):
    """{kw: {'kw_span': (a, b), 'spans': [(a, b), ...]}} in absolute offsets.

    `kw_span` covers the keyword itself; each entry of `spans` covers one clause
    *without* its separating comma. Offsets index the original text the item was
    parsed from, so `text[a:b]` is the clause verbatim."""
    sig_code, base = item.sig_code or "", item.sig_start or 0
    hits = []
    for kw in CLAUSE_KEYWORDS:
        for m in re.finditer(r"\b" + kw + r"\b", sig_code):
            pre = sig_code[:m.start()]
            if sum(pre.count(c) for c in "([{") == sum(pre.count(c) for c in ")]}"):
                hits.append((m.start(), m.end(), kw))
    hits.sort()
    out = {}
    for idx, (s, e, kw) in enumerate(hits):
        end = hits[idx + 1][0] if idx + 1 < len(hits) else len(sig_code)
        spans, depth, cur = [], 0, e
        for i in range(e, end):
            ch = sig_code[i]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 0:
                if sig_code[cur:i].strip():
                    spans.append((cur, i))
                cur = i + 1
        if sig_code[cur:end].strip():
            spans.append((cur, end))
        trimmed = []
        for a, b in spans:
            while a < b and sig_code[a] in " \t\r\n":
                a += 1
            while b > a and sig_code[b - 1] in " \t\r\n":
                b -= 1
            trimmed.append((base + a, base + b))
        out[kw] = {"kw_span": (base + s, base + e), "spans": trimmed}
    return out


def delete_clause(text, item, kw, idx):
    """`text` with clause `idx` of `item`'s `kw` list removed.

    Removing the clause's separating comma too, and removing the keyword as well
    when the clause was the only one -- a dangling `ensures` before `{` is a
    parse error, and a parse error is not the same experiment as a missing
    postcondition."""
    info = clause_spans(item).get(kw)
    if not info or idx >= len(info["spans"]):
        raise ValueError(f"vparse: {item.name} has no {kw} clause {idx}")
    spans = info["spans"]
    a, b = spans[idx]
    if len(spans) == 1:
        a = info["kw_span"][0]
    # Swallow one separator: the comma after, else the comma before. Scanned on
    # the comment-blanked copy, because `clause_spans` trims through comments
    # too -- see `delete_conjunct` for the failure this caused.
    code = blank_noncode(text)
    j = b
    while j < len(code) and code[j] in " \t\r\n":
        j += 1
    if j < len(code) and code[j] == ",":
        b = j + 1
    else:
        i = a
        while i > 0 and code[i - 1] in " \t\r\n":
            i -= 1
        if i > 0 and code[i - 1] == ",":
            a = i - 1
    return text[:a] + text[b:]


def _first_clause_offset(sig_code):
    """Offset of the first Verus clause keyword at bracket depth 0, or the end."""
    best = len(sig_code)
    for kw in CLAUSE_KEYWORDS:
        for m in re.finditer(r"\b" + kw + r"\b", sig_code):
            pre = sig_code[:m.start()]
            if sum(pre.count(c) for c in "([{") == sum(pre.count(c) for c in ")]}"):
                best = min(best, m.start())
                break
    return best


def _param_span(item):
    """(open, close) offsets of the parameter list inside `item.sig_code`."""
    sc = item.sig_code or ""
    i = 0
    while i < len(sc) and sc[i].isspace():
        i += 1
    if i < len(sc) and sc[i] == "<":
        i = _match_angle(sc, i)
    while i < len(sc) and sc[i].isspace():
        i += 1
    if i >= len(sc) or sc[i] != "(":
        raise ValueError(f"vparse: {item.name} has no parameter list")
    return i, _match_bracket(sc, i)


def sig_prefix(item):
    """(generics, params, where_clause) of the item, as verbatim source text.

    Everything the tautology probe must reproduce so that the parameter list it
    copies actually type-checks. `params_text` used to be the whole of it, and
    TASK_008_REVIEW measured the four shapes that then hard-fail the probe --
    `<T: Copy>` and a `where` clause give *E0425 cannot find type `T`*, `<'a>`
    gives *E0261 undeclared lifetime*, and a `&self` receiver gives *`self`
    parameter is only allowed in associated functions*. Fail-closed, and
    therefore correct, but the consequence was that a pattern with a generic or
    method-shaped trusted accessor could not be greened at all.

    Any piece that is empty comes back as `""`."""
    sc, st = item.sig_code or "", item.sig or ""
    i, j = _param_span(item)
    k = 0
    while k < len(sc) and sc[k].isspace():
        k += 1
    gen = st[k:_match_angle(sc, k)] if k < len(sc) and sc[k] == "<" else ""
    end = _first_clause_offset(sc)
    if end < j:                      # a clause keyword inside the parameters?
        end = len(sc)
    m = re.search(r"\bwhere\b", sc[j:end])
    where = st[j:end][m.start():].strip() if m else ""
    return gen, st[i:j], where


def params_text(item):
    """The item's parameter list, brackets included, verbatim.

    What the `requires`-tautology probe needs: a synthesised
    `proof fn <name><params> ensures <clause>, { }` has to bind exactly the
    names the clause mentions, and copying the source's own text is the only
    way to be sure it does. See `sig_prefix` for the generics and `where` that
    have to travel with it."""
    return sig_prefix(item)[1]


def params(item):
    """[(name, type_text)] of the item's parameters, in order.

    A `self` receiver comes back as `("self", "<the receiver text>")`. Raises on
    anything that is not `[mut ]name: type` -- a caller that reasons about
    *which* parameters a contract constrains must not be allowed to silently
    skip one it could not parse."""
    sc, st = item.sig_code or "", item.sig or ""
    i, j = _param_span(item)
    inner_code, inner_text = sc[i + 1:j - 1], st[i + 1:j - 1]
    out, depth, start = [], 0, 0
    pieces = []
    for k, ch in enumerate(inner_code):
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth -= 1
        elif ch == "," and depth == 0:
            pieces.append((start, k))
            start = k + 1
    pieces.append((start, len(inner_code)))
    for a, b in pieces:
        code, text = inner_code[a:b], inner_text[a:b]
        if not code.strip():
            continue
        if re.fullmatch(r"\s*&?\s*('[A-Za-z_][A-Za-z0-9_]*\s+)?(mut\s+)?self\s*",
                        code):
            out.append(("self", text.strip()))
            continue
        depth, cut = 0, None
        for k, ch in enumerate(code):
            if ch in "([{<":
                depth += 1
            elif ch in ")]}>":
                depth -= 1
            elif ch == ":" and depth == 0:
                cut = k
                break
        if cut is None:
            raise ValueError(f"vparse: {item.name}: parameter {text.strip()!r} "
                             f"has no `: type`")
        nm = text[:cut].strip()
        nm = re.sub(r"^(mut|ref)\s+", "", nm).strip()
        if not re.fullmatch(_IDENT, nm):
            raise ValueError(f"vparse: {item.name}: parameter pattern "
                             f"{nm!r} is not a plain identifier")
        out.append((nm, text[cut + 1:].strip()))
    return out


def param_names(item):
    """[name] of the item's parameters, in order; `self` for a receiver."""
    return [n for n, _ in params(item)]


# --- conjuncts: one deletable unit is not always one clause ----------------
#
# TASK_006_REVIEW, major C. `_clause_split` splits on top-level commas, so
# `ensures a, b` is two deletable clauses and `ensures a && b` is one. Re-joining
# a redundant conjunct with `&&` therefore makes the clause-deletion stage delete
# **both** halves at once; the file fails to verify, and the stage reports the
# clause load-bearing and prints a green line. Cost to an author: one character.
# Demonstrated on p02: ` && final(dst)@.len() == old(dst)@.len()` re-joined onto
# `copy_bytes`'s surviving `ensures` gives `ensures[0] load-bearing (8 verified,
# 1 errors)` and a green gate, while deleting only that conjunct reproduces the
# shipped file at 9 verified, 0 errors.
#
# So the deletion stage works on *conjuncts*, not clauses. Splitting is only
# sound where `&&` is the top-level connective: `a ==> b && c` parses as
# `a ==> (b && c)`, and a conjunct lifted out of an implication's antecedent or
# consequent is not a deletable unit. Any other top-level logical operator
# therefore **refuses** the split and says so, rather than guessing.
#
# `item.clauses` is untouched and stays comma-split: it is what `spec.md` pins,
# and the pin is a verbatim text diff that must not move under this.
#
# **And "atomic" is a claim, not a default** (TASK_008_REVIEW, blocker A).
# `top_level_ops` reports operators at bracket depth 0 only, and "no operators
# found" used to mean *atomic, `refused=None`* -- so `( A && B )` was neither
# split nor refused. No shout, no failure, full green gate, and the redundant
# trusted axiom is back for two characters. The `==>` path was loud all along;
# the parenthesised case escaped both branches. Two changes close it:
#
#   * redundant outer brackets are stripped before the top-level scan, so
#     `( A && B )` splits exactly as `A && B` does;
#   * a clause with no top-level operator but *some* logical operator inside
#     brackets, or a top-level quantifier binder whose body runs to the end of
#     the clause, is **refused** (and therefore shouted) rather than being
#     called atomic. Only a clause containing no logical operator anywhere is
#     atomic without an argument.
#
# The quantifier case is a soundness fix in its own right: `forall|j| A && B`
# parses as `forall|j| (A && B)`, so splitting at that `&&` produced a fragment
# with `j` unbound -- a mutant that fails to compile, which the stage would read
# as "load-bearing" if the probe did not hard-fail first.
_LOGIC_OPS = ("<==>", "<==", "==>", "&&&", "|||", "||", "&&")

# `forall|j: int| ...` / `exists|...| ...` / `choose|...| ...`: the binder's
# body extends to the end of the clause, so nothing inside it is a deletable
# conjunct of the clause.
_QUANT_RE = re.compile(r"\b(forall|exists|choose)\s*\|")


def top_level_ops(text, depth0=True):
    """[(offset, op)] for each logical operator of `_LOGIC_OPS` in `text`.

    `depth0` (the default) reports only operators at bracket depth 0; with
    `depth0=False` every occurrence is reported, which is how a caller asks
    "is there a connective hiding inside brackets?". Longest match wins at each
    position, so `&&&` is never read as `&&` and `<==>` is never read as
    `<==`."""
    out, depth, i = [], 0, 0
    while i < len(text):
        ch = text[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if depth == 0 or not depth0:
            for op in _LOGIC_OPS:
                if text.startswith(op, i):
                    out.append((i, op))
                    i += len(op)
                    break
            else:
                i += 1
            continue
        i += 1
    return out


def strip_outer_brackets(text):
    """(start, end) of `text` with every redundant enclosing `( ... )` removed.

    Redundant means: the whole of `text` is one bracketed group. `"( a && b )"`
    -> the span of `" a && b "`. Returns `(0, len(text))` when there is nothing
    to strip. `text` must be comment/string-blanked."""
    a, b = 0, len(text)
    while True:
        while a < b and text[a] in " \t\r\n":
            a += 1
        while b > a and text[b - 1] in " \t\r\n":
            b -= 1
        if b - a < 2 or text[a] != "(":
            return a, b
        try:
            if _match_bracket(text[a:b], 0) != b - a:
                return a, b
        except ValueError:
            return a, b
        a, b = a + 1, b - 1


def conjunct_spans(item, kw):
    """Per comma-clause of `item`'s `kw` list: the deletable conjuncts inside it.

    Returns a list parallel to `item.clauses[kw]`, each entry
    `{"spans": [(a, b), ...], "op": "&&"|"&&&"|None, "refused": None|str}` in
    absolute offsets into the text the item was parsed from. `refused` says why
    the clause could not be split into conjuncts; the caller must surface it
    rather than silently treating the clause as atomic. **`refused is None` is a
    positive claim** -- "this clause contains no logical connective at all, so
    it has exactly one conjunct" -- not a fallback."""
    info = clause_spans(item).get(kw)
    if not info:
        return []
    out = []
    base = item.sig_start or 0
    for a, b in info["spans"]:
        # the comment/string-blanked copy: a `&&` inside a comment is not a
        # connective, and the two copies are the same length so offsets agree
        whole = (item.sig_code or "")[a - base:b - base]
        # `( A && B )` must split exactly as `A && B` does (TASK_008_REVIEW A)
        sa, sb = strip_outer_brackets(whole)
        body = whole[sa:sb]
        a_in = a + sa
        ops = top_level_ops(body)
        kinds = {op for _, op in ops}
        quant = _QUANT_RE.search(body)
        if quant and (not ops or quant.start() < min(o for o, _ in ops)):
            # `forall|j| A && B` is `forall|j| (A && B)`: nothing after the
            # binder is a conjunct of the clause.
            out.append({"spans": [(a, b)], "op": None,
                        "refused": f"a top-level `{quant.group(1)}` binder, "
                                   f"whose body runs to the end of the clause"})
            continue
        if kinds == {"&&"} or kinds == {"&&&"}:
            op = kinds.pop()
            cuts, prev, spans = [o for o, _ in ops], 0, []
            for c in cuts:
                spans.append((prev, c))
                prev = c + len(op)
            spans.append((prev, len(body)))
            trimmed = []
            for s, e in spans:
                while s < e and body[s] in " \t\r\n":
                    s += 1
                while e > s and body[e - 1] in " \t\r\n":
                    e -= 1
                if e > s:
                    trimmed.append((a_in + s, a_in + e))
            out.append({"spans": trimmed, "op": op, "refused": None})
            continue
        if kinds:
            out.append({"spans": [(a, b)], "op": None,
                        "refused": "top-level " + ", ".join(sorted(kinds))})
            continue
        buried = {op for _, op in top_level_ops(body, depth0=False)}
        if buried:
            out.append({"spans": [(a, b)], "op": None,
                        "refused": "no top-level connective but "
                                   + ", ".join(sorted(buried))
                                   + " inside brackets"})
            continue
        out.append({"spans": [(a, b)], "op": None, "refused": None})
    return out


def delete_conjunct(text, item, kw, ci, ji):
    """`text` with conjunct `ji` of clause `ci` of `item`'s `kw` list removed.

    Removes the adjacent connective with it. A clause with a single conjunct
    falls back to `delete_clause`, which also drops the keyword when the clause
    was the only one -- a dangling `ensures` before `{` is a parse error, and a
    parse error is not the same experiment as a missing postcondition.

    **The scan for the connective runs on the comment-blanked copy**
    (TASK_008_REVIEW, minor 1). `conjunct_spans` trims a span's trailing
    whitespace on the blanked text, so it trims *through* a comment;
    `ensures a == b /* && c */ && d == e` therefore ends conjunct 0 at `b`,
    and a raw-text scan for the operator then stops at the `/`, leaves the
    `&&` in place, and produces `ensures /* && c */ && d == e`. That is a parse
    error, which the gate reports as *"Verus produced no result for the
    mutant"* -- blaming Verus for a splitter bug."""
    cj = conjunct_spans(item, kw)
    if ci >= len(cj):
        raise ValueError(f"vparse: {item.name} has no {kw} clause {ci}")
    spans, op = cj[ci]["spans"], cj[ci]["op"]
    if ji >= len(spans):
        raise ValueError(f"vparse: {item.name} {kw}[{ci}] has no conjunct {ji}")
    if len(spans) == 1:
        return delete_clause(text, item, kw, ci)
    code = blank_noncode(text)
    a, b = spans[ji]
    if ji + 1 < len(spans):                       # swallow the operator after
        j = b
        while j < len(code) and code[j] in " \t\r\n":
            j += 1
        if code.startswith(op, j):
            b = j + len(op)
    else:                                         # ...else the one before
        i = a
        while i > 0 and code[i - 1] in " \t\r\n":
            i -= 1
        if code[max(0, i - len(op)):i] == op:
            a = i - len(op)
    return text[:a] + text[b:]


def duplicate_names(items):
    """{name: [Item, ...]} for every name defined more than once.

    Two items with one name is not a style problem: whichever the gate keeps
    supplies the pinned contract for whichever the compiler keeps, and there is
    no reason those are the same one."""
    seen = {}
    for i in items:
        seen.setdefault(i.name, []).append(i)
    return {k: v for k, v in seen.items() if len(v) > 1}


def by_name(text):
    """Name -> Item. **Raises** on a duplicate; use `parse()` if you want to
    handle it yourself."""
    items = parse(text)
    dup = duplicate_names(items)
    if dup:
        raise ValueError("vparse: duplicate item name(s): " + ", ".join(
            f"{k} at lines {[i.line for i in v]}" for k, v in sorted(dup.items())))
    return {i.name: i for i in items}


# --------------------------------------------------------------------------

def _selftest():
    """Cases that the pre-TASK_003 parser got wrong. Each one is a bypass the
    gate reported green on."""
    src = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn a() -> (r: u64) requires true, ensures r == 1, { 1 }

// B1: a single blank line used to hide the attribute completely
#[verifier::external_body]

fn b() { }

// B1 variant: a comment paragraph between attribute and item
#[verifier::external_body]
// a comment
fn c() { }

// B1 variant: cfg_attr, which the old `#[(verifier::[a-z_]+)]` regex
// could not see at all
#[cfg_attr(all(), verifier::external_body)]
fn d() { }

#[cfg_attr(slb_isolated, inline(never))]
fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= v@.len(),
    ensures
        r == sum_wrap(v@, off as int, len as int),
{ 0 }

fn e() {
    // kernel( in a comment used to satisfy the call-site check
    let s = "kernel(";
    let _ = s;
}

fn f() { let r = kernel(v, 0, 1); }
} // verus!
'''
    it = by_name(src)
    bad = 0

    def want(label, got, exp):
        nonlocal bad
        ok = got == exp
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label:52s} {got!r}"
              + ("" if ok else f"  (want {exp!r})"))

    def raises(label, fn, exc=Exception):
        nonlocal bad
        try:
            fn()
        except exc as e:
            print(f"  ok   {label:52s} raised {type(e).__name__}")
            return
        bad += 1
        print(f"  FAIL {label:52s} did not raise {exc.__name__}")

    for n in "abcd":
        want(f"{n}: external_body seen", it[n].external, "verifier::external_body")
    want("kernel: not external", it["kernel"].external, None)
    want("kernel: inside verus!", it["kernel"].in_verus, True)
    want("kernel: requires pinned", it["kernel"].clauses["requires"],
         ["off + len <= v@.len()"])
    want("kernel: ensures pinned", it["kernel"].clauses["ensures"],
         ["r == sum_wrap(v@, off as int, len as int)"])
    want("a: requires", it["a"].clauses["requires"], ["true"])
    want("e: comment/string `kernel(` is not a call", it["e"].calls("kernel"), False)
    want("f: real call site found", it["f"].calls("kernel"), True)
    want("verus! end found by brace match, not a comment",
         verus_span(src.replace(" // verus!", "")) is not None, True)

    # --- a comment inside a clause list is NOT clause text (TASK_053 F4) ----
    # Before this, `check.py`'s parameter-coverage rule (the one built at
    # TASK_006_REVIEW because no verify/fail oracle can catch a weak trusted
    # precondition) read parameter names out of the comment, so
    # `requires i < v@.len(), // n is bounded by the caller` on an item whose
    # body reads `i + n` passed the rule -- and the same item with the comment
    # deleted failed it. Three shapes, plus the two-lists-parallel invariant.
    cmt = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn g1(v: &[u8], i: usize, n: usize) -> (r: u8)
    requires
        i < v@.len(),   // `n` is bounded by the caller
{ unsafe { *v.get_unchecked(i + n) } }

#[verifier::external_body]
fn g2(v: &[u8], i: usize, n: usize) -> (r: u8)
    requires
        // `n` is bounded by the caller
        i < v@.len(),
{ unsafe { *v.get_unchecked(i + n) } }

#[verifier::external_body]
fn g3(v: &[u8], i: usize, n: usize) -> (r: u8)
    requires
        i < v@.len(), /* `n` is bounded by the caller, len(v) */
{ unsafe { *v.get_unchecked(i + n) } }
} // verus!
'''
    ci = by_name(cmt)
    for n in ("g1", "g2", "g3"):
        want(f"{n}: comment is not a clause", ci[n].clauses["requires"],
             ["i < v@.len()"])
        want(f"{n}: clauses parallel to clause_spans",
             len(clause_spans(ci[n])["requires"]["spans"]),
             len(ci[n].clauses["requires"]))
    want("a comment's own comma does not split a clause list",
         len(ci["g3"].clauses["requires"]), 1)
    want("blank_comments keeps string literals, blanks the comment",
         (blank_comments('x == "a // b" /* c */').rstrip(),
          len(blank_comments('x == "a // b" /* c */'))),
         ('x == "a // b"', len('x == "a // b" /* c */')))

    # --- clause surgery, for the clause-deletion gate stage ----------------
    two = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn copy_bytes(src: &[u8], from: usize, dst: &mut [u8], n: usize)
    requires
        from + n <= src@.len(),
        n <= old(dst)@.len(),
    ensures
        final(dst)@.len() == old(dst)@.len(),
        final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange(
            n as int,
            old(dst)@.len() as int,
        ),
{ }
} // verus!
'''
    cb = by_name(two)["copy_bytes"]
    sp = clause_spans(cb)
    want("clause_spans: both ensures clauses located",
         [two[a:b] for a, b in sp["ensures"]["spans"]],
         ["final(dst)@.len() == old(dst)@.len()",
          "final(dst)@ =~= src@.subrange(from as int, from + n as int) + "
          "old(dst)@.subrange(\n            n as int,\n            "
          "old(dst)@.len() as int,\n        )"])
    want("clause_spans: text agrees with the parsed clause list",
         [norm_clause(two[a:b]) for a, b in sp["requires"]["spans"]],
         cb.clauses["requires"])
    d0 = delete_clause(two, cb, "ensures", 0)
    want("delete_clause(0): the other clause survives, alone",
         by_name(d0)["copy_bytes"].clauses["ensures"], [cb.clauses["ensures"][1]])
    want("delete_clause(0): `requires` untouched",
         by_name(d0)["copy_bytes"].clauses["requires"], cb.clauses["requires"])
    d1 = delete_clause(two, cb, "ensures", 1)
    want("delete_clause(1): the other clause survives, alone",
         by_name(d1)["copy_bytes"].clauses["ensures"], [cb.clauses["ensures"][0]])
    one = by_name(d0)["copy_bytes"]
    d01 = delete_clause(d0, one, "ensures", 0)
    want("deleting the only clause removes the `ensures` keyword too",
         "ensures" in d01, False)
    want("...and the item still parses", by_name(d01)["copy_bytes"].clauses["ensures"], [])
    want("...and its `requires` is intact",
         by_name(d01)["copy_bytes"].clauses["requires"], cb.clauses["requires"])
    raises("deleting a clause that does not exist raises",
           lambda: delete_clause(two, cb, "ensures", 2), ValueError)

    # --- TASK_006_REVIEW C: `&&` must not hide a conjunct from deletion -----
    merged = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn f(dst: &mut [u8], n: usize) -> (r: u64)
    requires
        n <= old(dst)@.len() && n >= 0,
    ensures
        final(dst)@.len() == old(dst)@.len(),
        r == 1 ==> n > 0 && n < 9,
        &&& r == 2
        &&& n == 3,
{ 0 }
} // verus!
'''
    mf = by_name(merged)["f"]
    want("a merged `a && b` is still ONE clause for the pin",
         mf.clauses["requires"], ["n <= old(dst)@.len() && n >= 0"])
    cj = conjunct_spans(mf, "requires")
    want("...but TWO conjuncts for the deletion stage",
         [merged[a:b] for a, b in cj[0]["spans"]],
         ["n <= old(dst)@.len()", "n >= 0"])
    want("deleting conjunct 1 leaves the other, still a clause",
         by_name(delete_conjunct(merged, mf, "requires", 0, 1))["f"]
         .clauses["requires"], ["n <= old(dst)@.len()"])
    want("deleting conjunct 0 leaves the other",
         by_name(delete_conjunct(merged, mf, "requires", 0, 0))["f"]
         .clauses["requires"], ["n >= 0"])
    ej = conjunct_spans(mf, "ensures")
    want("a clause with no top-level connective is one conjunct",
         [merged[a:b] for a, b in ej[0]["spans"]],
         ["final(dst)@.len() == old(dst)@.len()"])
    want("`==>` refuses the split rather than guessing at precedence",
         ej[1]["refused"], "top-level &&, ==>")
    want("...and the refused clause stays a single deletable unit",
         [merged[a:b] for a, b in ej[1]["spans"]], ["r == 1 ==> n > 0 && n < 9"])
    want("`&&&` (n-ary, lowest precedence) splits too",
         [merged[a:b] for a, b in ej[2]["spans"]], ["r == 2", "n == 3"])
    want("deleting the only conjunct falls back to deleting the clause",
         "final" in delete_conjunct(merged, mf, "ensures", 0, 0), False)
    raises("a conjunct index past the end raises",
           lambda: delete_conjunct(merged, mf, "requires", 0, 2), ValueError)
    want("top_level_ops does not read `&&&` as `&&`",
         top_level_ops("a &&& b"), [(2, "&&&")])
    want("top_level_ops ignores operators inside brackets",
         top_level_ops("f(a && b) && c"), [(10, "&&")])

    # --- TASK_008_REVIEW A: one pair of brackets must not buy silence --------
    paren = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn g(dst: &mut [u8], n: usize, v: &[u8], j: usize) -> (r: u64)
    requires
        ( n <= old(dst)@.len() && n >= 0 ),
    ensures
        (( r == 1 && n == 2 )),
        (r == 1 ==> n > 0),
        f(n && j),
        forall|q: int| 0 <= q < n && v@[q] == 0u8,
        r == 1,
{ 0 }
} // verus!
'''
    pg = by_name(paren)["g"]
    want("strip_outer_brackets removes one redundant pair",
         strip_outer_brackets("( a && b )"), (2, 8))
    want("...and does not remove a non-enclosing one",
         strip_outer_brackets("(a) && (b)"), (0, 10))
    cjp = conjunct_spans(pg, "requires")
    want("a fully-parenthesised `( A && B )` SPLITS (was: silently atomic)",
         [paren[a:b] for a, b in cjp[0]["spans"]],
         ["n <= old(dst)@.len()", "n >= 0"])
    want("...and is not refused", cjp[0]["refused"], None)
    want("deleting conjunct 1 of it leaves the brackets balanced",
         by_name(delete_conjunct(paren, pg, "requires", 0, 1))["g"]
         .clauses["requires"], ["( n <= old(dst)@.len() )"])
    ejp = conjunct_spans(pg, "ensures")
    want("`(( A && B ))` -- two pairs -- splits too",
         [paren[a:b] for a, b in ejp[0]["spans"]], ["r == 1", "n == 2"])
    want("`(A ==> B)` is refused, not called atomic",
         ejp[1]["refused"], "top-level ==>")
    want("a connective buried in a call argument is refused",
         ejp[2]["refused"], "no top-level connective but && inside brackets")
    want("a top-level quantifier binder is refused (its body is not a conjunct)",
         ejp[3]["refused"],
         "a top-level `forall` binder, whose body runs to the end of the clause")
    want("...and a clause with no connective anywhere is atomic, positively",
         (ejp[4]["refused"], [paren[a:b] for a, b in ejp[4]["spans"]]),
         (None, ["r == 1"]))

    # --- TASK_008_REVIEW minor 1: a comment between two conjuncts -----------
    cmt = '''use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn h(n: usize) -> (r: u64)
    ensures
        r == 1 /* && r == 9 */ && n == 2,
{ 0 }
} // verus!
'''
    ch = by_name(cmt)["h"]
    want("a `&&` inside a comment is not a connective",
         [cmt[a:b] for a, b in conjunct_spans(ch, "ensures")[0]["spans"]],
         ["r == 1", "n == 2"])
    d = delete_conjunct(cmt, ch, "ensures", 0, 0)
    want("deleting conjunct 0 swallows the operator ACROSS the comment",
         by_name(d)["h"].clauses["ensures"], ["n == 2"])
    want("...and deleting conjunct 1 leaves a parseable clause (comment kept)",
         [c.replace("/* && r == 9 */", "").strip()
          for c in by_name(delete_conjunct(cmt, ch, "ensures", 0, 1))["h"]
          .clauses["ensures"]], ["r == 1"])

    # --- TASK_008_REVIEW C: what the tautology probe has to copy ------------
    shapes = '''use vstd::prelude::*;
verus! {
pub struct Buf { pub b: Vec<u8> }

impl Buf {
    #[verifier::external_body]
    pub fn at(&self, i: usize) -> (r: u8)
        requires i < self.b@.len(),
    { 0 }
}

#[verifier::external_body]
fn gen<T: Copy>(v: &[T], i: usize) -> (r: T) requires i < v@.len(), { v[i] }

#[verifier::external_body]
fn wh<T>(v: &[T], i: usize) -> (r: T) where T: Copy
    requires i < v@.len(),
{ v[i] }

#[verifier::external_body]
fn lt<'a>(v: &'a [u8], i: usize) -> (r: u8) requires i < v@.len(), { 0 }
} // verus!
'''
    si = by_name(shapes)
    want("sig_prefix carries the generic list",
         sig_prefix(si["gen"])[0], "<T: Copy>")
    want("sig_prefix carries the `where` clause",
         sig_prefix(si["wh"])[2], "where T: Copy")
    want("...and its generics, and stops the params at the right bracket",
         (sig_prefix(si["wh"])[0], sig_prefix(si["wh"])[1]),
         ("<T>", "(v: &[T], i: usize)"))
    want("sig_prefix carries a lifetime parameter",
         sig_prefix(si["lt"])[0], "<'a>")
    want("a `self` receiver is reported with its text",
         params(si["at"]), [("self", "&self"), ("i", "usize")])
    want("...and the item knows which `impl` encloses it",
         si["at"].impl_head, "impl Buf")
    want("a free fn has no impl", si["gen"].impl_head, None)
    want("param types come back beside the names",
         params(si["gen"]), [("v", "&[T]"), ("i", "usize")])
    want("_match_angle survives a nested generic",
         _match_angle("<Vec<u8>, T>x", 0), 12)

    # --- parameter names, for the trusted-`unsafe` coverage rule ------------
    want("param_names on a &mut signature",
         param_names(cb), ["src", "from", "dst", "n"])
    want("params_text copies the source verbatim",
         params_text(cb),
         "(src: &[u8], from: usize, dst: &mut [u8], n: usize)")
    want("param_names strips `mut` and keeps generics whole",
         param_names(by_name("verus! {\nfn g(mut a: Vec<u64>, b: &[u8]) { }\n}")["g"]),
         ["a", "b"])
    raises("a parameter with no type raises rather than being skipped",
           lambda: param_names(by_name("verus! {\nfn h(a) { }\n}")["h"]),
           ValueError)

    # --- TASK_003_REVIEW: items keyed by name, last wins -------------------
    decoy = '''use vstd::prelude::*;
verus! {
#[cfg(any())]
mod decoy {
    // never compiled; supplied the pinned contract while the real kernel
    // below was the one measured
    pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
        requires off + len <= v@.len(),
        ensures r == sum_wrap(v@, off as int, len as int),
    { 0 }
}

pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires true,
{ 0 }

#[cfg(feature = "x")]
fn gated_leaf() { }
} // verus!

fn outside_verus() { }
'''
    ditems = parse(decoy)
    want("parse() returns a list, both kernels present",
         [i.name for i in ditems],
         ["kernel", "kernel", "gated_leaf", "outside_verus"])
    want("duplicate_names finds the decoy",
         sorted(duplicate_names(ditems)), ["kernel"])
    raises("by_name() refuses a duplicate", lambda: by_name(decoy), ValueError)
    want("decoy kernel is cfg-gated by its enclosing mod",
         ditems[0].cfg_gated, "#[cfg(...)] mod decoy")
    want("decoy kernel records its mod path", ditems[0].mod_path, "decoy")
    want("real kernel is not cfg-gated", ditems[1].cfg_gated, None)
    want("an item's own #[cfg] is seen too",
         ditems[2].cfg_gated, "own #[cfg(...)]")
    want("item outside verus! is flagged", ditems[3].in_verus, False)

    print("vparse selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    for i in parse(open(sys.argv[1]).read()):
        print(i)
