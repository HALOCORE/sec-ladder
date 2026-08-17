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
  * ghost statements (`assert(...)`, `proof { }`, `ghost`/`tracked` bindings),
    **inside `verus! { ... }` and nowhere else**. Ghost code erases *in Verus*,
    so an R5 driver that consumes its kernel's `ensures` (the method change
    TASK_002_REVIEW asked for) stays byte-identical to R4's and must stay
    diff-identical here too. Outside `verus!` every one of those tokens is live
    code, and gating this on `lang == "rust"` -- which is what TASK_003 did --
    reopened M9 in the other language (TASK_004_REVIEW; see `region_in_verus`)
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

**Arities that genuinely differ** get a second, equally constrained table.
`&[u8]` is a pointer *and* a length, so a C kernel that takes the same
information takes more arguments: p02's is
`kernel(src, src_len, src_off, dst, dst_cap)` against Rust's
`kernel(src, src_off, dst)`. An alias cannot express that -- both sides of an
alias are a dotted identifier path, so it can rename and nothing else -- and no
amount of renaming turns five arguments into three. `driver.call_args` declares,
per language, which argument positions of a named call are the canonical ones
(`{"c": {"kernel": [0, 2, 3]}}`). Three things keep it from being a hole:

  * it only ever drops arguments of a call to a **named** function, so it cannot
    delete or restructure a statement the way an unconstrained alias could;
  * every dropped argument must be a **single token** -- a bare identifier. A
    dropped `foo(bar)` or `x + 1` is refused, so nothing can hide in the gap;
  * dropping the *wrong* positions does not silently pass: the surviving
    arguments still have to match the pinned sequence token for token, and the
    declared positions are right there in `spec.md` for a reviewer to read
    against the C source.

The alternative was to give the C kernel a `{ptr, len}` struct so the arities
matched, which is a real C idiom (`struct iovec`) but is also exactly the
"Rust-in-C-syntax written to lose" the reviewer checklist warns about. The
asymmetry is a fact about the two languages; the pin makes it visible instead of
making it go away.

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
    defines `NDEBUG` -- was deleted from the C driver before the diff. The fix
    made it Rust-only, which was **still wrong** and TASK_004_REVIEW showed why:
    plain Rust is not Verus, `-C debug-assertions=off` does not remove
    `assert!`, and `let ghost = <anything>;` is an ordinary binding whose
    initialiser may be an `unsafe` block. Ghost stripping is now gated on
    `vparse.verus_span` -- the region must literally be inside `verus! { }`.
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
# `let ghost x = ...;` / `let tracked x = ...;` are ghost *bindings*: Verus
# erases them exactly as it erases `assert`, and a rung that snapshots state
# before a call in order to consume the callee's `ensures` needs one. Without
# this the snapshot showed up in the token stream as a real statement and the
# driver pin rejected it, so the only way to consume a postcondition about
# `&mut` state was not to. Rust-only, like every other rule in
# `_strip_verus_clauses`: `let` is not C, and outside `verus!` it is not Rust
# either.
_GHOST_RE = re.compile(r"^(let\s+(ghost|tracked)\b|assert|assert_by|assume|"
                       r"proof|ghost|tracked|reveal|reveal_with_fuel|"
                       r"broadcast)\b")

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


class GhostHarbourError(Exception):
    """The region's syntax claims to sit inside `verus! { }`, but the caller
    could not certify that **Verus compiled this file**.

    TASK_006_REVIEW put the M9 prefetch payload back into `safe_naive.rs`'s
    measured loop with

        macro_rules! verus { ($($t:tt)*) => { $($t)* } }
        verus!( fn main() { ... SLB-DRIVER-BEGIN ... } );

    -- three lines and a round bracket. `verus_span` accepted it (it matches
    `verus!\\s*[{(\\[]`), so `region_in_verus` said True, ghost stripping ran,
    `let ghost = unsafe { _mm_prefetch(..) };` vanished before the diff, and the
    gate passed with a `contract sha256` identical to the shipped pattern at
    +5.0 Ir/call.

    The bypass is **not** a regex bug and must not be fixed with a fourth
    regex: the brace form was already guarded by one and the paren form walked
    round it. The question is semantic -- *did Verus compile this file?* -- and
    the gate already has the answer, because it runs Verus on every file in
    `spec.md`'s `verus.obligations` and gets an obligation count back. So
    `normalise_file` demands that answer from its caller (`verus_verified=`) and
    **fails closed**: a region that claims the harbour without it is this
    exception, not a quiet downgrade to non-ghost normalisation."""


def region_span(txt, where="<text>"):
    """`(start, end)` offsets of the region body in `txt`, or None.

    Same validation as `region_text`, which is written in terms of this: the
    offsets are what decides whether the region is inside `verus! { ... }`, and
    that decides whether ghost stripping applies (see `normalise`)."""
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
    return m.start(1), m.end(1)


def region_text(txt, where="<text>"):
    """The raw text between the markers, or None if the file has no region.

    Raises `RegionError` if the file carries more than one BEGIN or more than
    one END. The old leftmost non-greedy match silently picked the *first*
    pair, so a decoy region in a block comment above the real loop was what got
    diffed while the real loop was free to say anything."""
    sp = region_span(txt, where)
    return None if sp is None else txt[sp[0]:sp[1]]


def region_in_verus(txt, where="<text>"):
    """Does the driver region's **syntax** claim to be inside `verus! { ... }`?

    This is a *claim*, not a licence. Read `GhostHarbourError`: any file can
    write `macro_rules! verus` and this function will say True, because it is
    looking at the token stream and the token stream is the attacker's. What
    licenses ghost stripping is this claim **plus** Verus's own verdict on the
    file, which only `normalise_file`'s caller can supply.

    Ghost statements erase *in Verus*; in plain Rust every one of the tokens
    `_GHOST_RE` matches is live code. TASK_004_REVIEW put three payloads into
    `safe_naive.rs`'s measured loop through the language-level gate -- each
    normalised to the canonical sequence, kept `statements = 13`, printed the
    right checksum, and cost 2.0 / 4.0 / 10.0 marginal Ir per call:

        assert!(k < nrec as usize);                      # live in release Rust:
                                                         # -C debug-assertions=off
                                                         # removes debug_assert!
                                                         # and nothing else
        let ghost = black_box(src[k * stride]);          # `ghost` is just a name
        let ghost = unsafe { _mm_prefetch(...) };        # M9's payload, in Rust

    The `assert` exclusion was argued in TASK_003_REVIEW for C only and then
    applied to both languages; `let ghost` is worse, because it admits an
    arbitrary initialiser expression including an `unsafe` block."""
    sp = region_span(txt, where)
    if sp is None:
        return False
    vs = vparse.verus_span(txt)
    if not vs or not (vs[0] <= sp[0] and sp[1] <= vs[1]):
        return False
    # ...and the enclosing item must not be `external`/`external_body`. Verus
    # compiles such an item as plain Rust, so `let ghost = <expr>;` inside one is
    # a live binding again -- the same payload, one attribute further in.
    inner = [i for i in vparse.parse(txt)
             if i.body_start is not None and i.body_end is not None
             and i.body_start <= sp[0] and sp[1] <= i.body_end]
    if not inner:
        return False
    return max(inner, key=lambda i: i.body_start).external is None


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


# --- the call-shape table -------------------------------------------------

def validate_call_args(spec, where="spec.md"):
    """[] when the table is legal, else a list of problems."""
    problems = []
    for fn, keep in (spec or {}).items():
        if not isinstance(fn, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", fn):
            problems.append(f"{where}: call_args key {fn!r} is not a function name")
            continue
        if (not isinstance(keep, list) or not keep
                or not all(isinstance(i, int) for i in keep)):
            problems.append(f"{where}: call_args[{fn!r}] = {keep!r} must be a "
                            f"non-empty list of argument positions")
            continue
        if keep != sorted(set(keep)) or keep[0] < 0:
            problems.append(f"{where}: call_args[{fn!r}] = {keep!r} must be "
                            f"strictly increasing and non-negative -- it "
                            f"selects positions, it does not reorder them")
    return problems


def _split_args(toks, i):
    """`toks[i]` is a `(`. Returns (args, index_of_matching_paren)."""
    depth, args, cur, j = 0, [], [], i
    while j < len(toks):
        t = toks[j]
        if t == "(":
            depth += 1
            if depth == 1:
                j += 1
                continue
        elif t == ")":
            depth -= 1
            if depth == 0:
                args.append(cur)
                return args, j
        elif t == "," and depth == 1:
            args.append(cur)
            cur = []
            j += 1
            continue
        cur.append(t)
        j += 1
    raise ValueError("unbalanced parentheses in the driver region")


def _apply_call_args(toks, spec):
    """Keep only the declared argument positions of a call to a named function.

    Raises ValueError when the declaration does not fit what is actually
    written -- a pin that has drifted from the source must fail loudly, not
    normalise to something that happens to match."""
    if not spec:
        return toks
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t in spec and i + 1 < len(toks) and toks[i + 1] == "(":
            args, close = _split_args(toks, i + 1)
            keep = spec[t]
            if keep[-1] >= len(args):
                raise ValueError(
                    f"call_args[{t!r}] keeps position {keep[-1]} but the call "
                    f"has {len(args)} argument(s)")
            for pos, a in enumerate(args):
                if pos in keep:
                    continue
                if len(a) != 1 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", a[0]):
                    raise ValueError(
                        f"call_args[{t!r}] drops argument {pos} = "
                        f"{' '.join(a)!r}, which is not a single identifier. "
                        f"Only a bare name may be dropped, so that nothing can "
                        f"hide in the arguments the diff stops looking at.")
            out.append(t)
            out.append("(")
            for n, pos in enumerate(keep):
                if n:
                    out.append(",")
                out.extend(args[pos])
            out.append(")")
            i = close + 1
            continue
        out.append(t)
        i += 1
    return out


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


def normalise(text, lang, aliases=None, call_args=None, in_verus=False):
    """Raw driver region -> canonical token string, one statement per line.

    `in_verus` says the region sits inside a `verus! { ... }` block, and it is
    the **only** thing that licenses ghost stripping. It defaults to False, so a
    caller that does not know gets the strict reading and a `let ghost` shows up
    as the statement it is; `normalise_file` derives it from the file. See
    `region_in_verus` for the three payloads the old `lang == "rust"` gate let
    through."""
    if lang not in ("rust", "c"):
        raise ValueError(f"dloop: unknown language {lang!r}")
    if in_verus and lang != "rust":
        raise ValueError(f"dloop: in_verus=True with lang={lang!r}; `verus!` is "
                         f"Rust syntax and there is no Verus C")
    bad = validate_aliases(aliases) + validate_call_args(call_args)
    if bad:
        raise ValueError("; ".join(bad))
    text = vparse.blank_noncode(text)
    # Ghost/clause stripping applies **inside `verus! {}` only**, not to Rust
    # generally. `assert(...)` is a ghost statement in Verus and erases; in C it
    # is live code -- `build.py` never defines `NDEBUG` -- and in *plain Rust* it
    # is live code too, because `-C debug-assertions=off` removes `debug_assert!`
    # and nothing else. TASK_003_REVIEW's argument for excluding it was made
    # about C and then applied to both languages; TASK_004_REVIEW walked an
    # `assert!`, a `black_box` load and an `_mm_prefetch` into `safe_naive.rs`'s
    # measured loop through the gap.
    if in_verus:
        text = _strip_verus_clauses(text)
    toks = _tokens(text)
    toks = _apply_wrapping(toks)
    toks = _strip_rust_types(toks) if lang == "rust" else _strip_c_types(toks)
    toks = _strip_group_parens(toks)
    toks = _apply_aliases(toks, aliases)
    toks = _apply_call_args(toks, call_args)
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


def normalise_file(path, lang, aliases=None, call_args=None,
                   verus_verified=False):
    """Normalise the driver region of `path`.

    `verus_verified` is the caller's certificate that **Verus itself compiled
    and verified this file** -- in `check.py` it comes from stage 5a, which runs
    `verus_run.py` on every file in `spec.md`'s `verus.obligations` and reads
    the obligation count back, plus a `--verify-function --verify-root` query on
    the item that encloses the region. It is the only thing that licenses ghost
    stripping.

    Fails closed. A file whose region *claims* the `verus!` harbour without that
    certificate raises `GhostHarbourError` rather than being renormalised
    without ghost stripping: a rung that is not compiled by Verus has no
    business spelling `verus!` around its measured loop at all, and downgrading
    silently would leave the payload's author a second guess to make."""
    txt = open(path).read()
    where = os.path.basename(path)
    sp = region_span(txt, where)
    if sp is None:
        return None
    claims = (lang == "rust" and region_in_verus(txt, where))
    if claims and not verus_verified:
        raise GhostHarbourError(
            f"{where}: the driver region sits inside something spelled "
            f"`verus!`, but Verus never verified this file -- it is not in "
            f"spec.md's `verus.obligations`, or the item enclosing the region "
            f"has no verified body. Ghost stripping is licensed by Verus's own "
            f"verdict, not by the token `verus!`: `macro_rules! verus "
            f"{{ ($($t:tt)*) => {{ $($t)* }} }}` plus `verus!( ... )` is three "
            f"lines, and it is how TASK_006_REVIEW put `let ghost = unsafe "
            f"{{ _mm_prefetch(..) }};` back into a measured loop at +5.0 "
            f"Ir/call with a fully green gate.")
    return normalise(txt[sp[0]:sp[1]], lang, aliases, call_args,
                     in_verus=claims)


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

    # --- ghost stripping happens inside `verus! {}` and nowhere else --------
    c_body = "assert(off < nwin);\nacc = acc * 31 + r;"
    rust_body = "assert(off < nwin);\nacc = acc.wrapping_mul(31).wrapping_add(r);"
    want("C `assert(...)` survives (it is live code there)",
         normalise(c_body, "c"), "assert ( off < nwin ) ;\nacc = acc * 31 + r ;")
    want("Verus `assert(...)` is ghost and erases",
         normalise(rust_body, "rust", in_verus=True), "acc = acc * 31 + r ;")
    want("Verus `let ghost x = ...;` is a ghost binding and erases",
         normalise("let ghost d0: Seq<u8> = dst@;\nacc = acc + r;", "rust",
                   in_verus=True),
         "acc = acc + r ;")
    want("C keeps a variable that merely starts with `let`-ish text",
         normalise("lettuce = 1;", "c"), "lettuce = 1 ;")
    want("a plain `let` binding is NOT ghost",
         normalise("let r: u64 = kernel(v, off);", "rust", in_verus=True),
         "r = kernel ( v , off ) ;")
    want("Verus `invariant` block erases",
         normalise("while it < n\n    invariant\n        a <= b,\n{\nit = it + 1;\n}",
                   "rust", in_verus=True),
         "while it < n\n{\nit = it + 1 ;\n}")
    raises("in_verus=True is refused for C",
           lambda: normalise(c_body, "c", in_verus=True), ValueError)

    # --- TASK_004_REVIEW: the three payloads the `lang == "rust"` gate passed
    # Each one normalised to the canonical sequence, kept statements = 13 and
    # printed the right checksum, while costing 2.0 / 4.0 / 10.0 marginal Ir per
    # call in `safe_naive.rs`'s measured loop. `_GHOST_RE` is now gated on the
    # region actually being inside `verus! { }`, so in a plain-Rust rung each is
    # a statement the pin does not have.
    for label, payload in (
            ("assert! (live in release Rust: -C debug-assertions=off "
             "removes debug_assert! only)", "assert!(k < nrec as usize);"),
            ("let ghost = black_box(load)",
             "let ghost = core::hint::black_box(src[k * stride]);"),
            ("let ghost = unsafe { _mm_prefetch(..) }  (M9, in Rust)",
             "let ghost = unsafe { core::arch::x86_64::_mm_prefetch("
             "src.as_ptr().add(k) as *const i8, 3) };")):
        loop = payload + "\nlet r: u64 = kernel(src, k * stride, dst);"
        pin = normalise("let r: u64 = kernel(src, k * stride, dst);", "rust")
        want(f"plain Rust keeps: {label[:38]}", normalise(loop, "rust") == pin,
             False)
        want(f"...and it still erases inside verus!: {label[:22]}",
             normalise(loop, "rust", in_verus=True) == pin, True)

    # --- region_in_verus decides it, and it is decided per file -------------
    plain = (f"fn main() {{\n// {B}\nlet ghost = f(x);\n// {E}\n}}\n")
    inside = ("verus! {\n" + plain + "}\n")
    outside = (plain + "verus! {\nfn k() { }\n}\n")
    ext = ("verus! {\n#[verifier::external_body]\n" + plain + "}\n")
    want("region in a file with no verus! -> not verus",
         region_in_verus(plain), False)
    want("region inside verus! -> verus", region_in_verus(inside), True)
    want("region *before* a verus! block -> not verus",
         region_in_verus(outside), False)
    want("region inside an `external_body` item -> not verus (it is plain Rust)",
         region_in_verus(ext), False)
    want("region_span agrees with region_text",
         (lambda s: plain[s[0]:s[1]])(region_span(plain)), region_text(plain))

    # --- TASK_006_REVIEW: `verus!` is a token, not a certificate -------------
    # A rung can define its own `verus!` and enter the ghost-strip harbour in
    # any of the three bracket forms `vparse.verus_span` accepts. The brace form
    # already had a guard in `check.py` and the paren form walked round it, so
    # the fix is not a fourth regex: `normalise_file` refuses to strip anything
    # unless the caller certifies that **Verus verified this file**.
    fake = "macro_rules! verus { ($($t:tt)*) => { $($t)* } }\n"
    scratch = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".temp", "dloop-selftest")
    os.makedirs(scratch, exist_ok=True)
    for label, o, c, tail in (("brace", "{", "}", ""),
                              ("paren", "(", ")", ";"),
                              ("bracket", "[", "]", ";")):
        src = (fake + f"verus!{o}\n" + plain + f"{c}{tail}\n")
        want(f"fake `verus!{o}...{c}` still *claims* the harbour",
             region_in_verus(src), True)
        p = os.path.join(scratch, f"fake_{label}.rs")
        open(p, "w").write(src)
        raises(f"...but normalise_file fails closed on it ({label})",
               lambda p=p: normalise_file(p, "rust"), GhostHarbourError)
        want(f"...and with the Verus certificate it strips ({label})",
             normalise_file(p, "rust", verus_verified=True), "")
    real = os.path.join(scratch, "no_verus.rs")
    open(real, "w").write(plain)
    want("a plain-Rust region needs no certificate and keeps its statement",
         normalise_file(real, "rust"), "ghost = f ( x ) ;")

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

    # --- the call-shape table (p02: C spells slice lengths as arguments) ----
    c_call = "uint64_t r = kernel(src, n_src, k * stride, dst, dst_cap);"
    rs_call = "let r: u64 = kernel(src, k * stride, dst);"
    want("C's extra length arguments drop out at the declared positions",
         normalise(c_call, "c", None, {"kernel": [0, 2, 3]}),
         normalise(rs_call, "rust"))
    want("a call the table says nothing about is untouched",
         normalise(c_call, "c", None, {"other": [0]}), normalise(c_call, "c"))
    want("legal call_args table accepts",
         validate_call_args({"kernel": [0, 2, 3]}), [])
    want("out-of-order positions rejected (it selects, it does not reorder)",
         len(validate_call_args({"kernel": [2, 0]})), 1)
    want("empty position list rejected", len(validate_call_args({"kernel": []})), 1)
    raises("dropping a non-identifier argument raises",
           lambda: normalise("r = kernel(src, prefetch(src), off);", "c", None,
                             {"kernel": [0, 2]}), ValueError)
    raises("dropping an *expression* argument raises",
           lambda: normalise("r = kernel(src, n + 1, off);", "c", None,
                             {"kernel": [0, 2]}), ValueError)
    raises("a position past the end of the call raises",
           lambda: normalise("r = kernel(src, off);", "c", None,
                             {"kernel": [0, 2, 3]}), ValueError)
    # Keeping the wrong positions cannot silently match: either the dropped
    # argument is not a bare name (raises), or the survivors differ from the
    # pin. Both are shown, because "it happens to line up" is the only way a
    # positional table could be a hole.
    raises("keeping the wrong positions raises when a real argument is dropped",
           lambda: normalise(c_call, "c", None, {"kernel": [0, 1, 3]}), ValueError)
    want("keeping the wrong bare names does not match the pin",
         normalise("r = kernel(a, b, c);", "c", None, {"kernel": [0, 1]})
         == normalise("r = kernel(a, c);", "rust"), False)

    print("dloop selftest:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    lang = "c" if sys.argv[1].endswith((".c", ".h")) else "rust"
    al, ca = None, None
    if len(sys.argv) > 2:
        import json
        al = json.loads(sys.argv[2])
    if len(sys.argv) > 3:
        import json
        ca = json.loads(sys.argv[3])
    out = normalise_file(sys.argv[1], lang, al, ca)
    print(out)
    print(f"--- {statement_count(out)} statements", file=sys.stderr)
