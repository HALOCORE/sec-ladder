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

def blank_noncode(text):
    """Return `text` with comments, string and char literals replaced by spaces
    of the same length, so offsets are preserved and every search below sees
    only code. Newlines are kept so line numbers still work."""
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
            blank(i, j)
            i = j
        elif c == "'":
            # char literal or lifetime; only blank a real char literal
            m = re.match(r"'(\\.|[^\\'])'", text[i:])
            if m:
                blank(i, i + m.end())
                i += m.end()
            else:
                i += 1
        else:
            i += 1
    return "".join(out)


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
    """One `fn` / `spec fn` / `proof fn`, with everything the gate asks about."""

    __slots__ = ("name", "kind", "start", "sig", "body", "attrs", "external",
                 "clauses", "in_verus", "line")

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
                f"in_verus={self.in_verus}, clauses={ {k: v for k, v in self.clauses.items() if v} })")


def _clause_split(text):
    """Split a clause list on top-level commas."""
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


def parse(text):
    """Every `fn`-like item in `text`, in source order."""
    code = blank_noncode(text)
    vs = verus_span(text, code)
    attrs = attribute_spans(code)
    attr_end = {e: (s, e) for s, e in attrs}
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
        my_attrs, p = [], pos
        while True:
            q = len(code[:p].rstrip())
            if q == 0:
                break
            if code[q - 1] != "]":
                break                      # `}`, `;`, `{` -> previous item
            span = attr_end.get(q)
            if span is None:
                break
            my_attrs.insert(0, text[span[0]:span[1]])
            p = span[0]
        item_start = p

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
        items.append(Item(
            name=name, kind=kind, start=item_start, sig=sig_text, body=body,
            attrs=my_attrs, external=ext,
            clauses=_parse_clauses(sig_code, sig_text),
            in_verus=bool(vs) and vs[0] <= m.start() < vs[1],
            line=text.count("\n", 0, item_start) + 1,
        ))
    return items


def by_name(text):
    return {i.name: i for i in parse(text)}


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
    print("vparse selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    for i in parse(open(sys.argv[1]).read()):
        print(i)
