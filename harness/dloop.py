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

**Known blind spots**, both deliberate, both covered elsewhere:

  * stripping non-call parentheses means a pure regrouping (`a * 31 + r` vs
    `a * (31 + r)`) normalises the same. The alternative is a real expression
    parser for two languages. The checksum stage breaks instantly on a
    regrouping, so nothing rides on this;
  * **casts are erased, so a width change is invisible here.** `acc as u32` and
    `acc as u64` produce the same token sequence, and so do `(size_t)x` and
    `(uint32_t)x`. This is *load-bearing* for the C/Rust reconciliation --
    `(size_t)(acc % nwin)` and `(acc % nwin) as usize` have to land on the same
    tokens or there is no cross-language diff at all -- so it cannot simply be
    removed. What catches a width change instead: the checksum stage (a
    truncating cast changes the fold), and, for the driver specifically, that
    every rung is diffed against one pinned sequence rather than against each
    other, so a width change applied to only one language shows up as a
    *checksum* divergence rather than a token one. A width change applied to
    **all** rungs at once would pass both; that is an open gap, recorded in
    `.memory/02-bench-rules.md`.

Names that genuinely differ between the languages (C computed `n_body` where
Rust calls `vals.len()`) are reconciled by an explicit, reviewable alias table
in `spec.md`, not by loosening the comparison.

TASK_003_REVIEW found three ways through this file, all fixed here and all
covered by `_selftest()` (which nothing in the repo had before -- every bypass
demonstrated against the gate so far has lived in this module):

  * **A decoy region.** `region()` used a leftmost non-greedy match, so the
    *first* `SLB-DRIVER-BEGIN ... SLB-DRIVER-END` pair won and a decoy in a
    block comment above the real loop was what got diffed (demonstrated with a
    2x-unrolled real loop and a full green gate). `region()` now raises on a
    second BEGIN or END, and `check.py` pins the *set* of files that must carry
    a region so deleting the markers no longer makes a rung vanish silently.
  * **Ghost-stripping applied to C.** `_GHOST_RE` was applied without branching
    on language, so `assert(...)` -- live code in C, since `build.py` never
    defines `NDEBUG` -- was deleted from the C driver before the diff.
    Normalisation of Verus clauses and ghost statements is now Rust-only.
  * **The alias table was an unconstrained rewriting program.** Destinations
    were unconstrained and an *empty* destination deleted statements outright,
    which revives the M9 prefetch/barrier payload with two lines of `spec.md`.
    Both sides must now be a dotted identifier path with an optional nullary
    call (`validate_aliases`), so an alias can rename but can never add,
    delete or restructure a statement.
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
    # gcc/clang 128-bit extension: `(unsigned __int128)x` must normalise to the
    # same tokens as Rust's `x as u128`.
    "__int128", "__int128_t", "__uint128_t",
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


BEGIN_MARK = "SLB-DRIVER" "-BEGIN"
END_MARK = "SLB-DRIVER" "-END"
_REGION_RE = re.compile(BEGIN_MARK + r"\s*(?:\*/)?\n(.*?)\n[^\n]*?" + END_MARK,
                        re.S)


class RegionError(Exception):
    """More than one driver region, or an unbalanced pair. Never returned as
    `None`: a file that *looks* like it has a region but has two is an attack,
    not an absence."""


def region_text(txt, where="<text>"):
    """The raw text between the markers, or None if the file has no region.

    Raises `RegionError` if the file carries more than one BEGIN or more than
    one END. The old leftmost non-greedy match silently picked the *first*
    pair, so a decoy region in a block comment above the real loop was what got
    diffed while the real loop was free to say anything."""
    nb, ne = txt.count(BEGIN_MARK), txt.count(END_MARK)
    if nb == 0 and ne == 0:
        return None
    if nb != 1 or ne != 1:
        raise RegionError(
            f"{where}: {nb} {BEGIN_MARK} marker(s) and {ne} {END_MARK} "
            f"marker(s); exactly one of each is required. A second pair -- in a "
            f"comment, a dead `#[cfg]` block, or anywhere else -- lets a decoy "
            f"region be diffed while the real driver loop goes unchecked.")
    m = _REGION_RE.search(txt)
    if not m:
        raise RegionError(f"{where}: {END_MARK} does not follow {BEGIN_MARK}")
    return m.group(1)


def region(src_path):
    """The raw text between SLB-DRIVER-BEGIN and SLB-DRIVER-END, or None."""
    return region_text(open(src_path).read(), os.path.basename(src_path))


# --- the alias table ------------------------------------------------------
# A dotted identifier path with an optional nullary call: `vals`, `inp.n_iters`,
# `vals.len()`, `vals.as_slice()`. Nothing else. In particular no operators, no
# literals, no arguments, no `;`, no braces -- so an alias can rename a name
# across the C/Rust boundary and can do *nothing else*. Before this, the table
# was an arbitrary token-sequence rewriter whose destinations were
# unconstrained: an empty destination deleted the statement it matched, which
# is enough to re-introduce the `__builtin_prefetch` / `__asm__ __volatile__`
# payload that M9 was about with two lines of `spec.md`.
_ALIAS_TERM_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*"
                            r"(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
                            r"(?:\(\))?$")


def validate_aliases(aliases, where="spec.md"):
    """[] when the table is legal, else a list of problems."""
    problems = []
    for k, v in (aliases or {}).items():
        for side, s in (("source", k), ("destination", v)):
            if not isinstance(s, str) or not s.strip():
                problems.append(f"{where}: alias {k!r} -> {v!r}: empty {side}; "
                                f"an empty destination deletes tokens")
            elif not _ALIAS_TERM_RE.match(s.strip()):
                problems.append(
                    f"{where}: alias {k!r} -> {v!r}: {side} {s!r} is not a "
                    f"dotted identifier path with an optional `()` -- aliases "
                    f"rename, they do not rewrite")
    return problems


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
    if lang not in ("rust", "c"):
        raise ValueError(f"dloop: unknown language {lang!r}")
    bad = validate_aliases(aliases)
    if bad:
        raise ValueError("; ".join(bad))
    text = vparse.blank_noncode(text)
    # Ghost/clause stripping is **Rust-only**. `assert(...)` is a ghost
    # statement in Verus and erases; in C it is live code -- `build.py` never
    # defines `NDEBUG` -- so stripping it there deletes a real branch from the
    # measured loop and the diff still passes.
    if lang == "rust":
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


# --------------------------------------------------------------------------

def _selftest():
    """Every bypass TASK_002_REVIEW and TASK_003_REVIEW demonstrated against
    this module, as an executable case. There was no selftest here before, and
    all three of the third review's driver-level bypasses lived in this file."""
    bad = 0

    def want(label, got, exp):
        nonlocal bad
        ok = got == exp
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label:56s} {got!r}"
              + ("" if ok else f"  (want {exp!r})"))

    def raises(label, fn, exc=Exception):
        nonlocal bad
        try:
            fn()
        except exc as e:
            print(f"  ok   {label:56s} raised {type(e).__name__}")
            return
        except Exception as e:                              # wrong type
            bad += 1
            print(f"  FAIL {label:56s} raised {type(e).__name__}, want {exc.__name__}")
            return
        bad += 1
        print(f"  FAIL {label:56s} did not raise")

    B, E = BEGIN_MARK, END_MARK

    # --- the decoy region (TASK_003_REVIEW bypass #7) ----------------------
    real = f"/* {B}\n" "acc = 1;\n" f"{E} */\n" \
           f"// {B}\n" "acc = 2;\n" f"// {E}\n"
    raises("two BEGIN/END pairs -> RegionError", lambda: region_text(real),
           RegionError)
    raises("BEGIN without END -> RegionError",
           lambda: region_text(f"// {B}\nacc = 1;\n"), RegionError)
    raises("END without BEGIN -> RegionError",
           lambda: region_text(f"acc = 1;\n// {E}\n"), RegionError)
    want("no markers at all -> None", region_text("int main(void){}"), None)
    want("exactly one pair -> the body",
         region_text(f"// {B}\nacc = 1;\n// {E}\n"), "acc = 1;")

    # --- ghost stripping is Rust-only --------------------------------------
    c_body = "assert(off < nwin);\nacc = acc * 31 + r;"
    rust_body = "assert(off < nwin);\nacc = acc.wrapping_mul(31).wrapping_add(r);"
    want("C `assert(...)` survives (it is live code there)",
         normalise(c_body, "c"), "assert ( off < nwin ) ;\nacc = acc * 31 + r ;")
    want("Rust `assert(...)` is ghost and erases",
         normalise(rust_body, "rust"), "acc = acc * 31 + r ;")
    want("Verus `invariant` block erases",
         normalise("while it < n\n    invariant\n        a <= b,\n{\nit = it + 1;\n}",
                   "rust"),
         "while it < n\n{\nit = it + 1 ;\n}")

    # --- the alias table is a renamer, not a rewriter ----------------------
    want("legal alias table accepts",
         validate_aliases({"n_body": "vals.len()", "inp.n_iters": "n_iters",
                           "vals": "vals.as_slice()"}), [])
    want("empty destination rejected (it deletes statements)",
         len(validate_aliases({"__builtin_prefetch ( vs , 0 , 1 ) ;": ""})), 2)
    want("operator in destination rejected",
         len(validate_aliases({"nwin": "nwin + 1"})), 1)
    want("literal destination rejected", len(validate_aliases({"nwin": "0"})), 1)
    want("statement source rejected",
         len(validate_aliases({"acc = acc * 31 ;": "acc"})), 1)
    raises("normalise() refuses an illegal alias table",
           lambda: normalise("acc = 1;", "c", {"acc": ""}), ValueError)
    raises("normalise() refuses an unknown language",
           lambda: normalise("acc = 1;", "verilog"), ValueError)

    # --- what normalisation is *supposed* to do ----------------------------
    want("C cast and Rust `as` land on the same tokens",
         normalise("size_t off = (size_t)(acc % nwin);", "c")
         == normalise("let off: usize = (acc % nwin) as usize;", "rust"), True)
    want("wrapping_* maps to the C operator",
         normalise("acc = acc.wrapping_mul(31).wrapping_add(r);", "rust"),
         "acc = acc * 31 + r ;")
    want("statement_count counts `;` and block openers",
         statement_count(normalise("while a < b {\nc = 1;\nd = 2;\n}", "c")), 3)

    print("dloop selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    lang = "c" if sys.argv[1].endswith((".c", ".h")) else "rust"
    al = None
    if len(sys.argv) > 2:
        import json
        al = json.loads(sys.argv[2])
    out = normalise_file(sys.argv[1], lang, al)
    print(out)
    print(f"--- {statement_count(out)} statements", file=sys.stderr)
