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
    check all by itself (`check.py::check_call_site`).
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


def _match_bracket_back(code, i):
    """Index of the bracket that `code[i]` closes. `code` must already be
    comment/string-blanked.

    The mirror of `_match_bracket`, added at TASK_088 for `trait_spans`'
    walk-back over a restricted visibility group (`pub(crate) trait ...`,
    `TASK_084_REVIEW` minor 4): the scan there runs right to left, so it needs
    to step from the `)` to its `(` rather than the other way round."""
    pairs = {")": "(", "]": "[", "}": "{"}
    if code[i] not in pairs:
        raise ValueError(f"vparse: {code[i]!r} at offset {i} is not a closer")
    depth, j = 0, i
    while j >= 0:
        if code[j] in pairs:
            depth += 1
        elif code[j] in "([{":
            depth -= 1
            if depth == 0:
                return j
        j -= 1
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
    'outside' the block. That end-finder lived in `check.py` before this module
    existed; it has no line to cite today, and the convention is the function
    name and no line number (`.memory/02-bench-rules.md`)."""
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


def trait_spans(text, code=None):
    """[(name, [attr, ...], body_start, body_end)] for every `trait NAME { ... }`.

    Exists for one reason: **`#[verifier::external_trait_specification]` sits on
    the `trait`, and every method it introduces is body-less**, so neither
    `parse()` (which drops body-less items, on purpose --
    `.memory/05-layout.md`) nor `parse()`'s own attribute walk (which only ever
    looks at `fn` items) can see that those declarations are trusted. The
    discriminator `axiom_decls` needs is the ENCLOSING item's attribute, and
    this is what computes it.

    ⚠ It must distinguish an external-trait declaration from an **ordinary**
    trait method declaration, which is body-less too and is *not* trusted -- it
    is proved by its impl, and `patterns/p36-vtable-dispatch/verus.rs` ships two
    of them (`fn apply`, `spec fn spec_apply`). p36 is the live negative control
    for that, and `_selftest` pins both directions.

    A `trait ... ;` (no body) and a trait whose generics this cannot read are
    simply not reported; `axiom_decls` has a fallback that still counts an
    unattached attribute, so an unreadable trait cannot make one invisible."""
    code = code if code is not None else blank_noncode(text)
    attr_end = {e: (s, e) for s, e in attribute_spans(code)}
    out = []
    for m in re.finditer(r"\btrait\s+(" + _IDENT + r")", code):
        pre = code[:m.start()].rstrip()
        # `impl Trait for X`, `dyn Trait`, `T: Trait` -- only an item-position
        # `trait` opens a declaration. Step back over `pub`/`unsafe`/... first.
        start = m.start()
        while True:
            p = code[:start].rstrip()
            # ⚠ A RESTRICTED VISIBILITY GROUP FIRST -- `pub(crate)`,
            # `pub(super)`, `pub(in path)` (TASK_084_REVIEW minor 4). Without
            # this the walk-back sees `)` where an identifier has to be, stops,
            # and the item-position guard below rejects a perfectly legal
            # `#[verifier::external_trait_specification] pub(crate) trait X`.
            # `axiom_decls`' fallback then reported it as ONE `ExW::?` instead
            # of one axiom per body-less method: visible, but the count wrong.
            if p.endswith(")"):
                try:
                    o = _match_bracket_back(code, len(p) - 1)
                except ValueError:
                    break
                q = code[:o].rstrip()
                wv = re.search(r"(" + _IDENT + r")$", q)
                if wv and wv.group(1) == "pub":
                    start = wv.start()
                    continue
                break
            w = re.search(r"(" + _IDENT + r")$", p)
            if not w or w.group(1) not in _MODIFIERS:
                break
            start = w.start()
        pre = code[:start].rstrip()
        # ⚠ `]` MUST be in this set. `impl_spans`' identical guard omits it and
        # that is its documented LIMIT 2 (an attributed `impl` is not reported);
        # here the whole point is an **attributed** trait -- the external-trait
        # form is `#[verifier::external_trait_specification] pub trait X` -- so
        # a guard that stops at the attribute's `]` reports nothing at all. It
        # costs nothing to allow: `trait` is a reserved keyword and cannot
        # appear anywhere but item position (`impl Trait`/`dyn Trait` capitalise
        # the *name*, not the keyword).
        if pre and pre[-1] not in "{};]":
            continue
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
                    break                  # a trait alias / forward decl
                j += 1
        except ValueError:
            continue
        if body is None:
            continue
        try:
            end = _match_bracket(code, body)
        except ValueError:
            continue
        attrs, _ = _attrs_before(code, text, start, attr_end)
        out.append((m.group(1), attrs, body + 1, end - 1))
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
            # ⚠ `\bverifier::external\b` DOES NOT MATCH `verifier::external_fn_
            # specification` -- the next character is `_`, a word character, so
            # there is no word boundary (TASK_083_REVIEW blocker 2). The item
            # therefore came back `external=None` and in `spec.md`'s
            # `verus.items` pin was **indistinguishable from an ordinary
            # verified function**, while its `ensures` is a hand-written claim
            # about real Rust semantics that Verus never checks:
            # `.temp/t84/probe/p_extfn.rs` verifies `r == 0` at `2 verified, 0
            # errors` and the compiled program prints `3`.
            #
            # This form is NOT body-less -- measured, not assumed: strip the
            # body and the pinned Verus refuses it twice over, `error[E0308]:
            # ... implicitly returns () as its body has no tail` and
            # `error: assume_specification encoding error: body should end in
            # call expression`. So `parse()` does see the item and the only
            # defect was the classification; `axiom_decls` handles the
            # body-less forms and the two matchers stay disjoint.
            m_es = re.search(r"\bverifier::(external_(?:fn|trait|type)"
                             r"_specification)\b", a)
            if m_es:
                ext = "verifier::" + m_es.group(1)
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
# body-less TRUSTED declarations -- what `parse()` structurally cannot report
# --------------------------------------------------------------------------

#: The body-less forms Verus offers for asserting something about code it
#: does not verify. `axiom fn` covers `broadcast axiom fn` and `pub axiom fn`;
#: `uninterp spec fn` covers the `open`/`closed` spellings.
_AXIOM_RE = (
    ("axiom fn", re.compile(r"\baxiom\s+fn\s+(" + _IDENT + r")")),
    ("uninterp spec fn",
     re.compile(r"\buninterp\s+(?:open\s+|closed\s+)?spec\s+fn\s+("
                + _IDENT + r")")),
)
_ASSUME_SPEC_RE = re.compile(r"\bassume_specification\b")
#: `#[verifier::external_trait_specification]` sits on a `trait` and
#: `#[verifier::external_type_specification]` on a `struct`/`enum`/`union`, so
#: neither is reachable from `parse()`'s `fn`-keyed attribute walk.
_EXT_TRAIT_ATTR_RE = re.compile(r"\bexternal_trait_specification\b")
_EXT_TYPE_ATTR_RE = re.compile(r"\bexternal_type_specification\b")
_TYPE_ITEM_RE = re.compile(r"\b(?:struct|enum|union)\s+(" + _IDENT + r")")
_FN_NAME_RE = re.compile(r"\bfn\s+(" + _IDENT + r")")

#: TASK_164 item B. The `global` DIRECTIVE is a SIXTH body-less trusted form and
#: nothing in `harness/` mentioned it. `GLOBAL_KINDS` is exported because
#: `check.py` partitions on it: a `global` is trusted and body-less like the five
#: above, but it is NOT an unchecked axiom -- rustc const-evaluates it (measured;
#: see the docstring) -- so it does not belong in the `verus.axioms` declared
#: count or in the Miri-mandating set. Anything that wants "all trusted body-less
#: declarations" takes the whole list; anything that wants "axioms nothing
#: checks" subtracts these.
GLOBAL_KINDS = ("global layout", "global size_of", "global")
_GLOBAL_RE = re.compile(r"\bglobal\b")
_GLOBAL_LAYOUT_RE = re.compile(r"\Alayout\b\s*(" + _IDENT + r")?")
_GLOBAL_SIZEOF_RE = re.compile(r"\Asize_of\b([^=;{}]*)")


def axiom_decls(text, code=None):
    """[{kind, name, line, in_verus}] for every body-less TRUSTED declaration.

    **`assume_specification`, `axiom fn` and `uninterp spec fn` are axioms about
    real Rust semantics, written by hand and checked by nothing** -- Verus does
    not prove them and this project's gate did not, until TASK_082, even *see*
    them (TASK_081_REVIEW blocker 1, RECAP "Owed" 0). They are the strongest
    kind of trusted item there is, and `.memory/04-verus.md`'s final section has
    the measurement: the declaration Verus's own error message prints for you to
    paste carries **no `requires` and no `ensures`**, so pasting it verifies a
    1 MiB out-of-bounds read and a null dereference at `4 verified, 0 errors`.

    ⚠ **THIS IS A SEPARATE MATCHER AND `parse()` MUST NOT BE MADE TO REPORT
    THESE. Measured at TASK_082, not argued.** The obvious repair -- delete
    `parse()`'s `if body_open is None: continue` so body-less items become
    `Item`s -- makes `by_name` raise on a file that is green today, because a
    **trait method declaration** is body-less too:

        patterns/p36-vtable-dispatch/verus.rs:141  fn apply       (trait decl)
        patterns/p36-vtable-dispatch/verus.rs:166  fn apply       (impl)
        -> vparse: duplicate item name(s): apply at lines [166, 141],
                                           spec_apply at lines [186, 146]

    and `by_name` has six consumers that each turn that `ValueError` into a gate
    failure (see its docstring), so p36 would go from PASS to six FAILs. p36's
    three other rung sources declare `apply` the same way. A trait method
    declaration is *not* trusted -- the implementing item is verified -- so
    widening `parse()` would both break a green pattern and count the wrong
    thing. Keyword-keyed detection does neither.

    `assume_specification` has no `fn` token at all, so `parse()`'s
    `\\bfn\\s+NAME` matcher never had any chance of seeing it in the first
    place.

    Comments and string literals are blanked first, so
    `patterns/p08-overlap-move/verus.rs:322` -- which *discusses*
    `assume_specification` in a comment -- is correctly not a hit.

    ---- TASK_084, from TASK_083_REVIEW blocker 1 -------------------------

    **`#[verifier::external_trait_specification]` is a fourth body-less form,
    it is in the pinned vstd 54 times, and until now no file in `harness/`
    mentioned it.** The attribute sits on the **`trait`**, not on a `fn`, so
    `parse()`'s attribute walk -- which only ever looks at `fn` items -- could
    not reach it, and the method declarations it introduces are body-less and
    dropped. Re-measured at TASK_084 on `.temp/t84/probe/p_ets.rs`: Verus
    reports `2 verified, 0 errors` proving `r == 0`, and the compiled program
    prints **7**.

    ⚠ **The discriminator is the ENCLOSING trait's attribute, and it has to be,
    because the shape is identical to p36's.** An ordinary trait's method
    declarations are body-less too and are *not* trusted -- they are proved by
    the impl. `trait_spans()` computes the enclosing attribute; the selftest
    pins both directions, and `p36-vtable-dispatch` is the live negative
    control (its four rung sources declare `fn apply` / `spec fn spec_apply` in
    a trait with no `external_*` attribute anywhere).

    **`#[verifier::external_type_specification]` is counted too**, one per
    declared item. On its own it cannot lie -- it carries no `ensures` -- but it
    is the *enabling* declaration for the trait form, and it is the exact line
    **Verus prints for you to paste** when it refuses an external type
    (*"The following declaration may resolve this error:"*), which is the same
    accident vector as `assume_specification`'s. Over-counting is the safe
    direction for a mechanism whose job is visibility.

    **`#[verifier::external_fn_specification]` is deliberately NOT here.** It
    is not body-less -- Verus rejects it without one, twice over
    (`error[E0308] ... implicitly returns ()` and `error: assume_specification
    encoding error: body should end in call expression`, measured at TASK_084)
    -- so `parse()` does see it, and it is classified there instead, by the
    attribute matcher this task also fixed. The rule that keeps the two
    matchers disjoint is exactly **body-less here, bodied there**.

    An attribute this cannot attach to a readable item is still counted, with
    `name='?'`, so an unparseable trait cannot make a trusted declaration
    invisible.

    ---- TASK_164, item B: the `global` DIRECTIVE is a SIXTH form -------------

    **`global layout T is size == n, align == m;` and `global size_of T == n;`
    are body-less, hand-written and trusted, and nothing in `harness/`
    mentioned either.** They are matched here, keyword-keyed, for the same
    reason the other five are and NOT by widening `parse()` -- see the warning
    above, which is still the measurement that governs.

    **The census, re-derived at TASK_164 with comments BLANKED**
    (`.temp/t164/census_global.py`), because the published *"live on four
    patterns (p28 p29 p32 p34)"* was a `grep -l` and was wrong in BOTH
    directions:

        global layout   p28 p29 p34                          3 patterns
        global size_of  p10 p19 p22 p36 p38 p46 p47          7 patterns
        union                                               10 of 33
        axiom_decls saw, before this:                         0 of 10

    ⚠ **`p32` HAS NONE.** `patterns/p32-free-list-pool/verus.rs:17` and
    `patterns/p49-interned-pool/verus.rs:29` are COMMENTS SAYING THE PATTERN HAS
    NO `global layout`, and a raw `grep -l` counted the negation as an instance.
    Those two files are the live negative controls for the comment-blanking arm
    in `_selftest`.

    **The `kind` distinguishes `layout` from `size_of` on purpose**, so a later
    reader can count either without re-deriving the census. They are the same
    CONSTRUCT and -- measured, not argued -- the same EXPOSURE:

        .temp/t164/globalprobe/, verus 0.2026.08.09.92f466f, single-file mode
          a FALSE `global layout S is size == 24` on a 6-byte struct
            -> `2 verified, 0 errors`  THEN  rustc `error[E0080]: evaluation
               panicked: does not have the expected size`, exit 1
          a FALSE `global size_of usize == 4`
            -> `2 verified, 0 errors`  THEN the SAME `E0080`, exit 1
          the same lie on a NEVER-CONSTRUCTED type, and with `--crate-type=lib`
            -> `1 verified, 0 errors` THEN the same `E0080`, exit 1
          the TRUE controls (`size == 6`, `usize == 8`) -> `2 verified, 0 errors`,
            exit 0

    So a `global` directive **CAN make Verus prove something false about the
    program's behaviour** -- the probes' `ensures r == 24usize` is a claim about
    the value `core::mem::size_of::<S>()` returns at run time, and Verus
    discharges it -- and the program **cannot be built**. ⚠ The Verus guide says
    the static check *"only happens when codegen is run"*
    (`_VERUS_DOC_/guide/src/reference-global.md`); on the pinned Verus that is
    too weak -- `E0080` is a const-eval error and it fires in a plain
    verify-only `./verus_run.py <file>` run, with no `--compile`, and in
    `--crate-type=lib`.

    ⚠⚠ **AND THE GATE ALREADY CATCHES IT, which refutes `TASK_156` minor 2's
    *"no verify-only stage is protected"*.** `check.py::_verus` treats
    `summary parsed and errors == 0 and returncode != 0` as an anomaly and
    stage `5e` (`check_verus_exit_codes`) fails on it. Driven in-process over
    these probes (`.temp/t164/globalprobe/drive_verus.py`): all three false ones
    return `(None, None, ...)` with `SUMMARY SUPPRESSED`, both true ones return
    `(2, 0)`, and stage 5e raises **3** failures. **This is visibility, not a
    hole being closed** -- which is exactly what `axiom_decls` is for."""
    code = code if code is not None else blank_noncode(text)
    vs = verus_span(text, code)
    out = []

    def add(kind, name, at):
        out.append(dict(kind=kind, name=name,
                        line=text.count("\n", 0, at) + 1,
                        in_verus=bool(vs) and vs[0] <= at < vs[1]))

    for kind, rx in _AXIOM_RE:
        for m in rx.finditer(code):
            add(kind, m.group(1), m.start())

    # --- TASK_164: the `global` directive ---------------------------------
    # Keyword-keyed like the two above. `code` has comments and string literals
    # blanked already, which is the whole difference between this and the
    # `grep -l` that counted p32's and p49's "this pattern has NO global layout"
    # comments as instances.
    for m in _GLOBAL_RE.finditer(code):
        j = m.end()
        while j < len(code) and code[j] in " \t\r\n":
            j += 1
        rest = code[j:]
        lm = _GLOBAL_LAYOUT_RE.match(rest)
        if lm:
            add("global layout", lm.group(1) or "?", m.start())
            continue
        sm = _GLOBAL_SIZEOF_RE.match(rest)
        if sm:
            # `global size_of usize == 8;` -- the type runs to the `==`. A
            # truncated line has nothing there and is counted as `?` rather
            # than dropped, the convention every other form here uses.
            nm = re.sub(r"\s+", " ", sm.group(1)).strip()
            add("global size_of", nm or "?", m.start())
            continue
        # A `global` this cannot classify. Line-anchored, because `global` is an
        # ITEM keyword in Verus and an unanchored fallback would count a local
        # named `global` (measured at TASK_164: ZERO code-level `global` tokens
        # outside the two forms across all 161 tracked `.rs`, so this fallback
        # is prospective). Never invisible -- same rule as the `?` above.
        bol = code.rfind("\n", 0, m.start()) + 1
        if not code[bol:m.start()].strip():
            add("global", "?", m.start())

    # `assume_specification` names its target in brackets rather than after
    # `fn`: `pub assume_specification<T>[ <[T]>::starts_with ](s: &[T]) -> ...`.
    for m in _ASSUME_SPEC_RE.finditer(code):
        j, name = m.end(), "?"
        try:
            while j < len(code) and code[j] in " \t\r\n":
                j += 1
            if j < len(code) and code[j] == "<":
                j = _match_angle(code, j)
            while j < len(code) and code[j] in " \t\r\n":
                j += 1
            if j < len(code) and code[j] == "[":
                end = _match_bracket(code, j)
                name = re.sub(r"\s+", " ", text[j + 1:end - 1]).strip()
        except ValueError:
            name = "?"          # unreadable target: still an axiom, still counted
        add("assume_specification", name, m.start())

    # --- `#[verifier::external_trait_specification]` -----------------------
    # One axiom per body-less method declaration inside the trait: each carries
    # a hand-written `ensures` about a trait method Verus never checks. The
    # attribute is matched on the ENCLOSING trait, which is the only thing that
    # separates this from an ordinary (verified-by-its-impl) trait method decl.
    traits = trait_spans(text, code)
    ext_traits = {}
    for tname, tattrs, bs, be in traits:
        if not any(_EXT_TRAIT_ATTR_RE.search(a) for a in tattrs):
            continue
        ext_traits.setdefault(tname, []).append(bs)
        n_here, j = 0, bs
        while True:
            m = _FN_NAME_RE.search(code, j, be)
            if not m:
                break
            k, depth, bodied = m.end(), 0, None
            while k < be:
                c = code[k]
                if c in "([":
                    depth += 1
                elif c in ")]":
                    depth -= 1
                elif c == "{" and depth == 0:
                    bodied = k
                    break
                elif c == ";" and depth == 0:
                    break
                k += 1
            if bodied is None:                      # body-less -> an axiom
                add("external_trait_specification",
                    f"{tname}::{m.group(1)}", m.start())
                n_here += 1
                j = k + 1
            else:                                   # a default body: skip it
                try:
                    j = _match_bracket(code, bodied)
                except ValueError:
                    j = bodied + 1
        if not n_here:
            # An external-trait declaration with no method declarations still
            # tells Verus to trust a trait it never checks. Never let the
            # construct be invisible.
            add("external_trait_specification", tname, bs)

    # ...and the fallback: an attribute whose `trait` this could not read at
    # all. Located by looking FORWARD for the `trait NAME` the attribute must
    # precede, then asking whether `trait_spans` reported a body for it.
    for s, e in attribute_spans(code):
        if not _EXT_TRAIT_ATTR_RE.search(text[s:e]):
            continue
        m = re.compile(r"\btrait\s+(" + _IDENT + r")").search(
            code, e, min(len(code), e + 400))
        if m is None:
            add("external_trait_specification", "?", s)
        elif not any(bs > e for bs in ext_traits.get(m.group(1), [])):
            add("external_trait_specification", m.group(1) + "::?", s)

    # --- `#[verifier::external_type_specification]` ------------------------
    for s, e in attribute_spans(code):
        if not _EXT_TYPE_ATTR_RE.search(text[s:e]):
            continue
        m = _TYPE_ITEM_RE.search(code, e, min(len(code), e + 400))
        add("external_type_specification", m.group(1) if m else "?", s)

    out.sort(key=lambda d: (d["line"], d["kind"], d["name"]))
    return out


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


_IMPL_HEAD_GENERICS_RE = re.compile(r"^impl\s*")


def impl_self_type(head):
    """`impl<const K: u8> Op for OpTag<K>` -> `OpTag`; `impl Buf` -> `Buf`.

    The Self type as a **path segment**, which is how Verus prints an item in
    `--verify-function`'s "matched results are:" list (`OpTag::apply`) and
    therefore what a caller must hand back to disambiguate one. Returns None
    for a head this does not model, so a caller can fall back rather than
    invent a name.

    Deliberately textual: `impl_spans` already hands over the head verbatim and
    a second Rust type parser is exactly the drift `parse()`'s docstring warns
    about. It has to survive three shapes the tree can hold -- inherent
    (`impl Buf`), trait (`impl Op for A`) and generic-with-const
    (`impl<const K: u8> Op for OpTag<K>`) -- and nothing more.

    ⚠ **TWO MEASURED LIMITS, both found by TASK_077_REVIEW / TASK_078 and
    neither of them fixed here.** Both are invisible on today's tree and both
    bite the first pattern that writes the eight-impl spelling "Owed" 20 is
    about, so they are written down rather than left to be re-discovered:

      1. **Generic arguments are collapsed** (TASK_077_REVIEW m6). `impl Op for
         OpTag<0>` ... `impl Op for OpTag<7>` are eight monomorphisations of one
         generic type and all eight return `"OpTag"`, so `unique_names` raises
         *"`OpTag::apply` is defined more than once even after qualification"* --
         which is FALSE, Verus distinguishes them. Keeping `<0>`..`<7>` would
         need the Self type printed the way Verus prints it in
         `--verify-function`'s "matched results are:" list, and that is not
         verified to be the source spelling.
      2. **An `impl` preceded by an ATTRIBUTE is not seen at all**, so its
         methods get `impl_head=None` and qualify to the bare name.
         `impl_spans` only recognises `impl` at item position, testing
         `pre[-1] not in "{};"`; `#[cfg(slb_twin)]` ends in `]`. Measured
         (`.temp/p78/f1_probe.py`): a `#[cfg(slb_twin)] impl Op0 { fn
         slb_twin_apply ... }` and its `Op1` sibling BOTH qualify to
         `slb_twin_apply`, so `unique_names` raises on the very file the fix
         exists for -- an eight-impl `verus.rs` whose trusted methods carry the
         verified twins `check.py::check_trusted_twins` requires. The same two
         impls with the attribute deleted qualify correctly to
         `Op0::slb_twin_apply` / `Op1::slb_twin_apply`.

    No pattern in the tree has an attribute-preceded `impl` today (every
    `slb_twin_*` is a free function), so 2 changes nothing that is measured;
    widening `impl_spans` would also widen the `requires`-tautology probe's
    synthesis site, which is a gate-semantics change and wants PROTOCOL rule
    5's accident test first."""
    if not head:
        return None
    s = _IMPL_HEAD_GENERICS_RE.sub("", head.strip(), count=1)
    # drop the impl's own generic parameter list, balanced
    if s.startswith("<"):
        depth, k = 0, 0
        for k, c in enumerate(s):
            depth += (c == "<") - (c == ">")
            if depth == 0:
                break
        s = s[k + 1:]
    s = re.split(r"\bwhere\b", s)[0].strip()
    # `Trait for Type` -> `Type`; a bare `Type` is an inherent impl
    m = re.search(r"\bfor\b", s)
    if m:
        s = s[m.end():].strip()
    # `&'a mut dyn Wrap<T>` -> `Wrap<T>`: reference, lifetime, `mut`, `dyn`
    s = s.lstrip("&").strip()
    s = re.sub(r"^'[A-Za-z_][A-Za-z0-9_]*\s*", "", s)
    s = re.sub(r"^\bmut\b\s*", "", s)
    s = re.sub(r"^\bdyn\b\s*", "", s)
    s = s.split("<")[0].strip()          # `OpTag<K>` -> `OpTag`
    s = s.split("::")[-1].strip()        # `crate::Buf` -> `Buf`
    return s or None


def scope_label(item):
    """The item's enclosing scope as Verus would path-qualify it, or `""`.

    `mod_path` and the enclosing `impl` are BOTH scopes and both are already
    computed by `parse()`; this is only the two of them joined."""
    parts = [p for p in [(item.mod_path or ""),
                         (impl_self_type(item.impl_head) or "")] if p]
    return "::".join(parts)


def qualified_name(item):
    """`Type::name` / `mod::name` / `mod::Type::name`, or the bare name."""
    sc = scope_label(item)
    return f"{sc}::{item.name}" if sc else item.name


def duplicate_names(items, qualified=False):
    """{name: [Item, ...]} for every name defined more than once.

    Two items with one name is not a style problem: whichever the gate keeps
    supplies the pinned contract for whichever the compiler keeps, and there is
    no reason those are the same one.

    ⚠ **`qualified=True` keys by (mod path, impl Self type, name) instead**,
    which is the fix for RECAP "Owed" 20 (TASK_077). Keying by BARE name made a
    pinned `verus.rs` unable to define one item name twice, so p36's first
    spelling -- eight `impl Op for OpN` blocks, which is the shape a reader of
    its `c/kernel.c` would write -- **verified `19/0` and the gate refused it**
    (`patterns/p36-vtable-dispatch/NOTES.md` 9b). Rust has no ambiguity between
    `<OpN as Op>::apply` and `<OpM as Op>::apply`; only the gate's name->item
    map did.

    **The default is still bare, and that is not timidity.** The callers want
    different things and it took a measurement to see it:

      * `check.py::check_verus_contract` and `check.py::_verus_verified_files`
        key items so `spec.md`'s per-item contract lands on the right item.
        Qualified is right there, and `unique_names` keeps every existing pin
        working unchanged.
      * `by_name` returns `{name: Item}`, so a qualified duplicate would
        silently drop one and re-open TASK_003_REVIEW's decoy. Bare is right
        there and must stay.

    ⚠ **SO THE EIGHT-IMPL SPELLING IS STILL REFUSED, AND "Owed" 20 IS NARROWED
    RATHER THAN CLOSED** (TASK_077_REVIEW B1; TASK_078 measured the route and
    declined it). `by_name` has **six** consumers, all of which turn its
    `ValueError` into a failure: `check.py::check_call_site`,
    `check_clause_deletion`, `check_requires_strength`, `check_trusted_twins`,
    `derive_contract`, and `harness/limbs.py::main`. TASK_077 switched the
    *contract* stage and the *driver-identity* stage only. Threading
    `qualified=True` through the rest is **not** mechanical, measured
    (`.temp/p78/f1_probe.py`, TASK_078):

      * `check_trusted_twins` and `limbs.py` build the twin's key by string
        concatenation, `TWIN_PREFIX + t.name`, from the item's BARE name. In a
        qualified map that key MISSES on every trusted method inside an `impl`
        (`slb_twin_apply` looked up in a map holding `Op0::slb_twin_apply`), so
        every trusted item reports `NO TWIN` -- a failure that says the
        opposite of the truth. Scope-aware key construction is a semantic
        change to the twin rule, not a keying change.
      * `harness/limbs.py` is not a gate stage but six patterns' published
        `NOTES.md` sentences rest on what it reports, so it has to move too.
      * the clause-deletion and precondition-strength stages label every
        recorded row with `it.name`, so an eight-impl file emits eight rows all
        labelled `apply` into `results/gate/*.json`. That is a record-schema
        change on top of the keying.
      * and see `impl_self_type`'s limit 2: with the twins in place,
        `unique_names` RAISES on the eight-impl file anyway.

    **What IS closed**: the per-item contract map and the `--verify-function`
    label are scope-keyed, and `check_driver_identity`'s duplicate refusal is
    now scoped to duplicates qualification cannot separate.
    """
    seen = {}
    for i in items:
        seen.setdefault(qualified_name(i) if qualified else i.name, []).append(i)
    return {k: v for k, v in seen.items() if len(v) > 1}


def unique_names(items):
    """{label: Item} where `label` is the BARE name when that is unambiguous in
    this file and the qualified name when it is not.

    The degradation is the point: every `verus.rs` in the tree today has unique
    bare names, so this returns exactly `{i.name: i}` for all of them and no
    `spec.md` item pin has to move. A file that really does define one name in
    two scopes gets `OpTag0::apply`-shaped keys, and its `spec.md` must name
    them that way -- which is the honest cost of the eight-impl spelling and is
    why "Owed" 20 was never a one-liner.

    **Raises** if two items share even the qualified name, because then there
    is no key that distinguishes them and the caller must not pick one.
    ⚠ **Two shapes reach that raise for a reason that is `impl_self_type`'s
    limitation and NOT the file's** -- eight `OpTag<0..7>` monomorphisations,
    and any `impl` preceded by an attribute. Both are written out in
    `impl_self_type`'s docstring; read it before believing the message.

    ⚠ **A label this returns is NOT guaranteed to be a name Verus can be given.**
    Verus matches `--verify-function` by SUBSTRING over the qualified path and
    errors on more than one match, so a BARE label is ambiguous whenever another
    item's name contains it -- measured on a file with **no** duplicate item name
    at all, one `impl A` defining `apply` and `spec_apply`
    (`.temp/p78/vprobe/subambig.log`, TASK_078 M5). `check.py::_verify_function`
    reports that as its own third answer; it is not something this function can
    see, because it is a property of the whole name set and of Verus's matcher."""
    bare = {}
    for i in items:
        bare.setdefault(i.name, []).append(i)
    out = {}
    for i in items:
        key = i.name if len(bare[i.name]) == 1 else qualified_name(i)
        if key in out:
            raise ValueError(
                f"vparse: `{key}` is defined more than once even after "
                f"qualification (lines {[out[key].line, i.line]}); no key "
                f"distinguishes them")
        out[key] = i
    return out


def by_name(text):
    """Name -> Item. **Raises** on a duplicate; use `parse()` if you want to
    handle it yourself.

    Bare-name keyed **on purpose** -- see `duplicate_names`: the return type is
    `{name: Item}`, so admitting a qualified duplicate here would drop one of
    the two silently, which is TASK_003_REVIEW's decoy.

    ⚠ **THIS RAISE IS WHAT STILL REFUSES THE EIGHT-IMPL SPELLING, and it costs
    SIX failures, not one** (TASK_077_REVIEW B1). Every consumer turns it into a
    `rep.fail` / a fired limb: `check.py::check_call_site` (`FAIL [proof-rule2]`),
    `check_clause_deletion` (`FAIL [clause-mut]`), `check_requires_strength`
    (`FAIL [req-mut]`), `check_trusted_twins` (`FAIL [twin]`),
    `derive_contract` (`FAIL [contract-source]`), and `harness/limbs.py::main`.
    Their message is *"duplicate item name(s): apply"*, which is the same text
    `duplicate_names`' qualified path calls fine -- so read `duplicate_names`'
    docstring before concluding the gate has changed its mind."""
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

    # --- RECAP "Owed" 20 / TASK_077: one name in two IMPLS is not a decoy ---
    eight = '''use vstd::prelude::*;
verus! {
struct Op0;
struct Op1;
trait Op { fn apply(&self, x: u64) -> u64; }
impl Op for Op0 { fn apply(&self, x: u64) -> u64 { x } }
impl Op for Op1 { fn apply(&self, x: u64) -> u64 { x + 1 } }
impl<const K: u8> Op for OpTag<K> { fn apply(&self, x: u64) -> u64 { x + 2 } }
} // verus!
'''
    eitems = parse(eight)
    want("impl_self_type: trait impl", impl_self_type("impl Op for Op0"), "Op0")
    want("impl_self_type: inherent impl", impl_self_type("impl Buf"), "Buf")
    want("impl_self_type: generic const impl",
         impl_self_type("impl<const K: u8> Op for OpTag<K>"), "OpTag")
    want("impl_self_type: where-clause and reference",
         impl_self_type("impl<'a, T> Op for &'a Wrap<T> where T: Copy"), "Wrap")
    want("impl_self_type on a free fn's None head", impl_self_type(None), None)
    want("bare keying still calls three `apply`s a duplicate",
         sorted(duplicate_names(eitems)), ["apply"])
    want("qualified keying does NOT -- three distinct impls",
         sorted(duplicate_names(eitems, qualified=True)), [])
    want("qualified_name spells the Self type",
         sorted(qualified_name(i) for i in eitems),
         ["Op0::apply", "Op1::apply", "OpTag::apply"])
    want("unique_names falls back to qualified only where it must",
         sorted(unique_names(eitems)),
         ["Op0::apply", "Op1::apply", "OpTag::apply"])
    # ...and the decoy is STILL caught, by both keyings, because a mod path is
    # part of the scope: `decoy::kernel` vs `kernel` are two labels, so the
    # pinned item SET no longer matches and `by_name` still raises.
    want("the mod decoy is still two distinct labels",
         sorted(unique_names(ditems)),
         ["decoy::kernel", "gated_leaf", "kernel", "outside_verus"])
    same_scope = '''verus! {
fn kernel(v: &[u64]) -> u64 { 0 }
fn kernel(v: &[u64]) -> u64 { 1 }
}
'''
    want("two items in the SAME scope are a duplicate under both keyings",
         (sorted(duplicate_names(parse(same_scope))),
          sorted(duplicate_names(parse(same_scope), qualified=True))),
         (["kernel"], ["kernel"]))
    raises("unique_names refuses what no key distinguishes",
           lambda: unique_names(parse(same_scope)), ValueError)
    want("unique_names is the identity on a file with unique bare names",
         sorted(unique_names(parse(src))), sorted(i.name for i in parse(src)))

    # --- TASK_078: the two LIMITS of the qualification, pinned as tests so a
    # later fix has something that changes. Both are documented in
    # `impl_self_type`'s docstring and both are why "Owed" 20 is narrowed and
    # not closed. NEITHER is exercised by any pattern in the tree today.
    gen8 = "verus! {\n" + "".join(
        f"impl Op for OpTag<{k}> {{ fn apply(&self) -> u64 {{ {k} }} }}\n"
        for k in range(8)) + "}\n"
    want("LIMIT 1 (m6): eight OpTag<K> monomorphisations collapse to one scope",
         sorted({qualified_name(i) for i in parse(gen8)}), ["OpTag::apply"])
    raises("LIMIT 1: ...so unique_names refuses a file Verus accepts",
           lambda: unique_names(parse(gen8)), ValueError)
    attr_impl = '''verus! {
#[cfg(slb_twin)]
impl Op0 { fn slb_twin_apply(&self) -> u64 { 0 } }
#[cfg(slb_twin)]
impl Op1 { fn slb_twin_apply(&self) -> u64 { 1 } }
}
'''
    want("LIMIT 2: an impl preceded by an ATTRIBUTE is invisible to impl_spans",
         [i.impl_head for i in parse(attr_impl)], [None, None])
    want("LIMIT 2: ...so its methods qualify to the bare name",
         sorted(qualified_name(i) for i in parse(attr_impl)),
         ["slb_twin_apply", "slb_twin_apply"])
    want("LIMIT 2 control: delete the attribute and both qualify correctly",
         sorted(qualified_name(i)
                for i in parse(attr_impl.replace("#[cfg(slb_twin)]\n", ""))),
         ["Op0::slb_twin_apply", "Op1::slb_twin_apply"])

    # --- TASK_082: body-less TRUSTED declarations (RECAP "Owed" 0) ----------
    # The gate could not see any of these at all. The last two cases are the
    # ones that make this a separate matcher rather than a widened `parse()`:
    # a trait method declaration is body-less and is NOT trusted, and p36 ships
    # two of them beside impl definitions of the same names.
    ax = '''use vstd::prelude::*;
verus! {
// assume_specification for `<[T]>::copy_from_slice` -- a COMMENT, not an axiom
pub uninterp spec fn view_of(s: &[u8]) -> Seq<u8>;
pub open spec fn defined(x: int) -> bool { x > 0 }
broadcast axiom fn axiom_view(s: &[u8]) ensures view_of(s).len() == s@.len();
pub axiom fn tracked_empty() -> (tracked out_v: u8);
pub assume_specification[ u32::rotate_left ](x: u32, n: u32) -> (r: u32)
    ensures r == x, opens_invariants none no_unwind ;
pub assume_specification<T: PartialEq>[ <[T]>::starts_with ](s: &[T], p: &[T]) -> (b: bool)
    ensures b == (p@.len() <= s@.len()) ;
trait Op { fn apply(&self) -> u64; }
impl Op for u8 { fn apply(&self) -> u64 { 0 } }
fn hide() { let s = "assume_specification"; let _ = s; }
}
'''
    want("axiom_decls: every body-less trusted form, in source order",
         [(d["kind"], d["name"]) for d in axiom_decls(ax)],
         [("uninterp spec fn", "view_of"),
          ("axiom fn", "axiom_view"),
          ("axiom fn", "tracked_empty"),
          ("assume_specification", "u32::rotate_left"),
          ("assume_specification", "<[T]>::starts_with")])
    want("axiom_decls: a comment/string mention is not a declaration",
         [d for d in axiom_decls(ax) if d["name"] in ("?", "copy_from_slice")],
         [])
    want("axiom_decls: a defined `open spec fn` is not an axiom",
         [d for d in axiom_decls(ax) if d["name"] == "defined"], [])
    want("axiom_decls: a TRAIT METHOD DECLARATION is not an axiom",
         [d for d in axiom_decls(ax) if d["name"] == "apply"], [])
    want("axiom_decls: all inside verus!",
         sorted({d["in_verus"] for d in axiom_decls(ax)}), [True])
    want("axiom_decls: none of these are `parse()` items",
         sorted(set(i.name for i in parse(ax))
                & {d["name"] for d in axiom_decls(ax)}), [])
    # ...and the reason `parse()` was NOT widened: p36's shape, reduced.
    trait_dup = '''verus! {
trait Op { spec fn spec_apply(&self) -> u64; fn apply(&self) -> u64; }
impl Op for u8 { spec fn spec_apply(&self) -> u64 { 0 }
                 fn apply(&self) -> u64 { 0 } }
}
'''
    want("body-less trait decls stay out of parse(), so by_name still works",
         sorted(by_name(trait_dup)), ["apply", "spec_apply"])
    want("...and they are not counted as axioms either",
         axiom_decls(trait_dup), [])

    # --- TASK_084: the two `*_specification` attributes -------------------
    # TASK_083_REVIEW blockers 1 and 2. Both are trusted declarations about
    # code Verus never checks; neither was visible to anything in `harness/`,
    # and `external_trait_specification` is in the pinned vstd 54 times.
    #
    # ⚠ The pair of pins that matters most is the NEGATIVE one directly above
    # (`trait_dup`) against the positive one here: the two shapes differ ONLY
    # by the attribute on the enclosing trait, and p36 ships the negative in
    # four rung sources.
    extspec = '''use vstd::prelude::*;
pub trait Widget { fn width(&self) -> usize; }
pub struct W;
impl Widget for W { fn width(&self) -> usize { 7 } }
verus! {
#[verifier::external_type_specification]
pub struct ExW(crate::W);

#[verifier::external_trait_specification]
pub trait ExWidget {
    type ExternalTraitSpecificationFor: Widget;
    fn width(&self) -> (r: usize) ensures r == 0, ;
    fn height(&self) -> (r: usize) ensures r == 0, ;
    fn area(&self) -> (r: usize) { 0 }          // a DEFAULT body: not body-less
}

#[verifier::external_fn_specification]
pub fn ex_count_ones(x: u64) -> (r: u32) ensures r == 0, { x.count_ones() }
}
'''
    want("external_trait_specification: one axiom per BODY-LESS method decl",
         [(d["kind"], d["name"]) for d in axiom_decls(extspec)],
         [("external_type_specification", "ExW"),
          ("external_trait_specification", "ExWidget::width"),
          ("external_trait_specification", "ExWidget::height")])
    want("...a DEFAULT body inside an external trait is not counted",
         [d for d in axiom_decls(extspec) if d["name"].endswith("::area")], [])
    want("...and the trait's methods are still not `parse()` items",
         sorted(set(i.name for i in parse(extspec))
                & {"width", "height"}), ["width"])   # only the plain-Rust impl
    want("trait_spans reports the enclosing attribute (the discriminator)",
         [(n, a) for n, a, _, _ in trait_spans(extspec)],
         [("Widget", []),
          ("ExWidget", ["#[verifier::external_trait_specification]"])])
    want("external_fn_specification is BODIED, so it is classified in parse()",
         [(i.name, i.external) for i in parse(extspec) if i.external],
         [("ex_count_ones", "verifier::external_fn_specification")])
    want("...and is therefore NOT double-counted as an axiom",
         [d for d in axiom_decls(extspec) if d["name"] == "ex_count_ones"], [])
    want("a bare `#[verifier::external]` still classifies as before",
         [(i.name, i.external) for i in
          parse("verus!{ #[verifier::external] fn z() {} }")],
         [("z", "verifier::external")])
    # An attribute whose trait this cannot read must still be VISIBLE.
    unreadable = ('verus! {\n'
                  '#[verifier::external_trait_specification]\n'
                  'pub trait Broken<F: Fn(u8) -> u8 {\n'
                  '    fn go(&self) -> (r: u8) ensures r == 0, ;\n'
                  '}\n'
                  '}\n')
    want("an unparseable external trait is still counted, as `?`",
         [(d["kind"], d["name"]) for d in axiom_decls(unreadable)],
         [("external_trait_specification", "Broken::?")])

    # TASK_084_REVIEW minor 4, fixed at TASK_088. A RESTRICTED VISIBILITY GROUP
    # between the attribute and `trait` used to stop `trait_spans`' walk-back
    # dead: `code[:start].rstrip()` ends `)`, no identifier matches, and the
    # item-position guard then rejects the item. Measured before the fix:
    # `trait_spans` -> `[]` and `axiom_decls` -> ONE `ExVis::?` for a trait with
    # TWO body-less methods. Visible, but the count wrong for a legal spelling.
    vis = ('verus! {\n'
           '#[verifier::external_trait_specification]\n'
           'pub(crate) trait ExVis {\n'
           '    type ExternalTraitSpecificationFor: Vis;\n'
           '    fn a(&self) -> usize;\n'
           '    fn b(&self) -> usize;\n'
           '}\n'
           '#[verifier::external_trait_specification]\n'
           'pub(in crate::deep) trait ExVis2 {\n'
           '    type ExternalTraitSpecificationFor: Vis2;\n'
           '    fn c(&self) -> usize;\n'
           '}\n'
           'pub(crate) trait PlainVis { fn d(&self) -> usize; }\n'
           '}\n')
    want("pub(crate) / pub(in path) trait: the walk-back steps over the group",
         [n for n, _, _, _ in trait_spans(vis)],
         ["ExVis", "ExVis2", "PlainVis"])
    want("...so it is ONE AXIOM PER BODY-LESS METHOD, not one `?`",
         [(d["kind"], d["name"]) for d in axiom_decls(vis)],
         [("external_trait_specification", "ExVis::a"),
          ("external_trait_specification", "ExVis::b"),
          ("external_trait_specification", "ExVis2::c")])
    want("...and a pub(crate) ORDINARY trait is still not an axiom",
         [d for d in axiom_decls(vis) if d["name"].startswith("PlainVis")], [])

    # --- TASK_164 item B: the `global` DIRECTIVE, and BOTH DIRECTIONS -------
    # ⚠⚠ Case 3 is the arm that would have caught the published *"four
    # patterns (p28 p29 p32 p34)"* error: it was a `grep -l` and `p32`'s and
    # `p49`'s hits are COMMENTS SAYING THE PATTERN HAS NONE. A negation counted
    # as an instance. Those two files are the live negative controls; the cell
    # below is the synthetic one that runs on every invocation.
    glob = '''use vstd::prelude::*;
verus! {
// This pattern has NO `global layout` -- a COMMENT, and the p32/p49 shape.
global layout Obj is size == 24, align == 8;
global size_of usize == 8;
fn hide() { let s = "global layout Fake is size == 1;"; let _ = s; }
}
'''
    want("axiom_decls: a `global` directive is counted, with its own kind",
         [(d["kind"], d["name"]) for d in axiom_decls(glob)],
         [("global layout", "Obj"), ("global size_of", "usize")])
    want("axiom_decls: `global layout` in a COMMENT is NOT counted "
         "(the p32/p49 error)",
         [d for d in axiom_decls(glob) if d["name"] in ("Fake", "NO")], [])
    want("axiom_decls: `global` in a STRING LITERAL is not counted",
         [d for d in axiom_decls(glob) if d["line"] == 6], [])
    want("axiom_decls: a `global` directive is inside verus!",
         sorted({d["in_verus"] for d in axiom_decls(glob)}), [True])
    want("axiom_decls: `global` is not a `parse()` item either",
         sorted(set(i.name for i in parse(glob))
                & {d["name"] for d in axiom_decls(glob)}), [])
    # A truncated / unreadable directive is COUNTED as `?`, never invisible --
    # the convention `assume_specification` and `external_trait_specification`
    # already use above.
    want("axiom_decls: a truncated `global layout` is counted as `?`",
         [(d["kind"], d["name"]) for d in axiom_decls("verus!{\nglobal layout\n}")],
         [("global layout", "?")])
    want("axiom_decls: a truncated `global size_of` is counted as `?`",
         [(d["kind"], d["name"]) for d in axiom_decls("verus!{\nglobal size_of\n}")],
         [("global size_of", "?")])
    want("axiom_decls: an UNKNOWN `global` form at item position is counted",
         [(d["kind"], d["name"]) for d in axiom_decls("verus!{\nglobal align_of u8 == 1;\n}")],
         [("global", "?")])
    # ...and the false-positive direction: `global` as an ordinary identifier.
    want("axiom_decls: a LOCAL named `global` is not a directive",
         axiom_decls("verus!{ fn f() { let global = 1u8; let _ = global; } }"),
         [])
    want("GLOBAL_KINDS covers every kind this can emit for a `global`",
         sorted({d["kind"] for d in
                 axiom_decls("verus!{\nglobal layout A is size == 1;\n"
                             "global size_of usize == 8;\nglobal x;\n}")}
                - set(GLOBAL_KINDS)), [])

    print("vparse selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    for i in parse(open(sys.argv[1]).read()):
        print(i)
