#!/usr/bin/env python3
"""The driver loop, normalised to a language-neutral token sequence.

`.memory/02-bench-rules.md`: "Driver logic must be identical across R2-R5 and
behaviourally identical to the C driver." Before TASK_003 that was enforced two
different weak ways, and TASK_002_REVIEW walked through both:

  * the Rust copies were diffed **against each other**, so a mutation applied to
    every rung -- deleting the anti-collapse barrier, say -- passed green;
  * the C copy was checked by **seven required substrings**, so inserting a
    `__builtin_prefetch` and an `__asm__ __volatile__` memory barrier passed
    green while putting exactly the cross-language asymmetry the bench rules
    forbid into the measured loop (M9).

So the reference is no longer another rung: it is the canonical token sequence
pinned in the pattern's `spec.md`, and every rung -- C included -- is normalised
and diffed against it. Adding a statement changes the token sequence and the
statement count; deleting one does too; changing `acc % nwin` to `0` does too.

What normalisation removes, and nothing else:

  * comments, and Verus-only clause blocks (`invariant`, `decreases`) --
    `harness/check.py` already exempted those
  * ghost statements (`assert(...)`, `proof { }`, `ghost`/`tracked` bindings).
    Ghost code erases, so an R5 driver that *consumes* its kernel's `ensures`
    (the method change TASK_002_REVIEW asked for) stays byte-identical to R4's
    and must stay diff-identical here too
  * type annotations, declaration types and casts, in both languages
  * `x.wrapping_mul(y)` / `wrapping_add` / `wrapping_sub` -> the C operator
  * parentheses that are not a call's -- `(acc % nwin) as usize` and
    `(size_t)(acc % nwin)` have to land on the same tokens

**Known blind spot:** stripping non-call parentheses means a pure regrouping
(`a * 31 + r` vs `a * (31 + r)`) normalises the same. That is deliberate -- the
alternative is a real expression parser for two languages -- and it is covered
by the checksum stage, which a regrouping would break instantly.

Names that genuinely differ between the languages (C computed `n_body` where
Rust calls `vals.len()`) are reconciled by an explicit, reviewable alias table
in `spec.md`, not by loosening the comparison.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vparse  # noqa: E402

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[0-9]+|&&|\|\||<<|>>|[<>=!+\-*/%]=|->|::|\S")

RUST_TYPES = {
    "usize", "isize", "bool", "char", "str", "f32", "f64",
    *(f"{s}{w}" for s in "ui" for w in (8, 16, 32, 64, 128)),
    "Vec", "Option", "Box",
}
C_TYPES = {
    "const", "volatile", "restrict", "static", "register", "signed", "unsigned",
    "void", "char", "short", "int", "long", "float", "double", "_Bool",
    "size_t", "ssize_t", "ptrdiff_t", "intptr_t", "uintptr_t",
    *(f"{s}int{w}_t" for s in ("u", "") for w in (8, 16, 32, 64)),
}
# Identifier-shaped tokens that are not function names, so a `(` after them is
# grouping and gets stripped.
_NOT_CALLS = {"if", "while", "for", "return", "match", "switch", "sizeof",
              "else", "do", "and", "or", "not"}
# Statements that erase at compile time and must not count as driver logic.
_GHOST_RE = re.compile(r"^(assert|assert_by|assume|proof|ghost|tracked|reveal|"
                       r"reveal_with_fuel|broadcast)\b")

WRAPPING = {"wrapping_mul": "*", "wrapping_add": "+", "wrapping_sub": "-",
            "wrapping_div": "/", "wrapping_rem": "%"}


def region(src_path):
    """The raw text between SLB-DRIVER-BEGIN and SLB-DRIVER-END, or None."""
    txt = open(src_path).read()
    m = re.search(r"SLB-DRIVER-BEGIN\s*(?:\*/)?\n(.*?)\n[^\n]*?SLB-DRIVER-END",
                  txt, re.S)
    return m.group(1) if m else None


def _strip_verus_clauses(body):
    """Drop `invariant ...` / `decreases ...` blocks and ghost statements.

    A clause block runs from the keyword to the line that opens the loop body."""
    out = []
    in_clause = False   # inside `invariant ...` / `decreases ...`, ends at the `{`
    ghost_depth = None  # inside a ghost statement, ends when brackets rebalance
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if ghost_depth is not None:
            ghost_depth += sum(s.count(c) for c in "([{") - \
                sum(s.count(c) for c in ")]}")
            if ghost_depth <= 0:
                ghost_depth = None
            continue
        if in_clause:
            if s.endswith("{"):
                in_clause = False
                out.append("{")
            continue
        if re.match(r"^(invariant|decreases|opens_invariants|no_unwind)\b", s):
            in_clause = not s.endswith("{")
            if s.endswith("{"):
                out.append("{")
            continue
        if _GHOST_RE.match(s):
            # a ghost statement may span lines: `assert(..) by { .. }`,
            # `proof { .. }`. Track bracket depth rather than guessing.
            d = sum(s.count(c) for c in "([{") - sum(s.count(c) for c in ")]}")
            if d > 0:
                ghost_depth = d
            continue
        out.append(s)
    return "\n".join(out)


def _tokens(text):
    return _TOKEN_RE.findall(text)


def _apply_wrapping(toks):
    """`X . wrapping_mul ( Y )` -> `X * ( Y )`."""
    out, i = [], 0
    while i < len(toks):
        if (toks[i] == "." and i + 2 < len(toks) and toks[i + 1] in WRAPPING
                and toks[i + 2] == "("):
            out.append(WRAPPING[toks[i + 1]])
            out.append("(")
            i += 3
            continue
        out.append(toks[i])
        i += 1
    return out


def _strip_rust_types(toks):
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t in ("let", "mut"):
            i += 1
            continue
        if t == ":":
            # `let x: T = ...`  -- consume the type up to `=`, `;` or `,`
            i += 1
            while i < len(toks) and toks[i] not in ("=", ";", ","):
                i += 1
            continue
        if t == "as" and i + 1 < len(toks) and toks[i + 1] in RUST_TYPES:
            i += 2
            continue
        out.append(t)
        i += 1
    return out


def _strip_c_types(toks):
    out, i = [], 0
    stmt_start = True
    while i < len(toks):
        t = toks[i]
        if stmt_start:
            j = i
            while j < len(toks) and (toks[j] in C_TYPES or toks[j] == "*"):
                j += 1
            # only a declaration if a name follows; `*p = x;` must survive
            if j > i and j < len(toks) and re.match(r"^[A-Za-z_]", toks[j]) \
                    and toks[j] not in C_TYPES:
                i = j
                stmt_start = False
                continue
        # cast: `( T ... )` with nothing but type tokens inside
        if t == "(":
            j, depth = i, 0
            while j < len(toks):
                if toks[j] == "(":
                    depth += 1
                elif toks[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = toks[i + 1:j]
            if inner and all(x in C_TYPES or x == "*" for x in inner):
                i = j + 1
                continue
        out.append(t)
        stmt_start = t in (";", "{", "}")
        i += 1
    return out


def _strip_group_parens(toks):
    """Remove every `(`/`)` that is not a call's."""
    keep = [True] * len(toks)
    stack = []
    for i, t in enumerate(toks):
        if t == "(":
            prev = toks[i - 1] if i else ""
            is_call = bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", prev)) and \
                prev not in _NOT_CALLS
            stack.append((i, is_call))
        elif t == ")":
            if stack:
                j, is_call = stack.pop()
                if not is_call:
                    keep[i] = keep[j] = False
    return [t for t, k in zip(toks, keep) if k]


def _apply_aliases(toks, aliases):
    """Single left-to-right pass, longest match first, no re-triggering."""
    if not aliases:
        return toks
    table = sorted(((_tokens(k), _tokens(v)) for k, v in aliases.items()),
                   key=lambda kv: -len(kv[0]))
    out, i = [], 0
    while i < len(toks):
        for src, dst in table:
            if toks[i:i + len(src)] == src:
                out.extend(dst)
                i += len(src)
                break
        else:
            out.append(toks[i])
            i += 1
    return out


def normalise(text, lang, aliases=None):
    """Raw driver region -> canonical token string, one statement per line."""
    text = vparse.blank_noncode(text)
    text = _strip_verus_clauses(text)
    toks = _tokens(text)
    toks = _apply_wrapping(toks)
    toks = _strip_rust_types(toks) if lang == "rust" else _strip_c_types(toks)
    toks = _strip_group_parens(toks)
    toks = _apply_aliases(toks, aliases)
    # one statement per line, so a diff points at a statement
    lines, cur = [], []
    for t in toks:
        if t in ("{", "}"):
            if cur:
                lines.append(" ".join(cur))
                cur = []
            lines.append(t)
            continue
        cur.append(t)
        if t == ";":
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)


def statement_count(canon):
    """Statements, not lines: `;` terminators plus block openers."""
    return sum(1 for l in canon.splitlines() if l.endswith(";") or l == "{")


def normalise_file(path, lang, aliases=None):
    r = region(path)
    return None if r is None else normalise(r, lang, aliases)


if __name__ == "__main__":
    lang = "c" if sys.argv[1].endswith((".c", ".h")) else "rust"
    al = None
    if len(sys.argv) > 2:
        import json
        al = json.loads(sys.argv[2])
    out = normalise_file(sys.argv[1], lang, al)
    print(out)
    print(f"--- {statement_count(out)} statements", file=sys.stderr)
