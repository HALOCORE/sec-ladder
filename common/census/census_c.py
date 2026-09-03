#!/usr/bin/env python3
"""TASK_129 — bound-site census over C corpora. PROMOTED AT TASK_170 (item C).

⚠⚠ **THIS FILE IS A VERBATIM PROMOTION of `.temp/t129/census.py`** — the
instrument behind `results/SYNTHESIS.md` §7's *"`0 of 255`"*, now `0 of 464`.
The only edit is this header. It lived only in gitignored `.temp/` from
TASK_129 to TASK_170, so a `.temp/` clean — which `CLAUDE.md` constraint 1
asks for — would have deleted the instrument behind a published number, which
is the exact defect that created `common/census/` in the first place
(TASK_132). `common/census/README.md` §3 recorded the numbers at TASK_166 and
said plainly that the instrument was still not committed; this closes that.

**Drive it through `common/census/bound_sites.py`**, which carries the CONTROL:
the 26-kernel population must still reproduce the published `255 / 0 / 30 / 26`
before the 33-kernel figure is believed.

⚠ **Nothing here may be imported by `harness/check.py`, `harness/measure.py` or
`harness/build.py`** — `common/census/` is outside both digests only for as
long as that holds (`README.md`, *Digest note*).


A SITE is a memory access whose safety depends on a bound.
Each site is labelled with three fields (the limbs of the reviewed admission bar):

  operator      index | ptr_offset | mem_call | str_call | cast_deref
  bound_source  none | const | strlen | call | field | induction | cursor |
                param | local | global
  check         at_site | earlier | none      <-- NOT limb 3.  Limb 3 is ELISION,
                                                  a compiler property, invisible
                                                  in source.  This field is a
                                                  different, weaker thing.

For induction sites a second field `resolved` re-applies the bound_source
classifier to the enclosing loop's own bound expression.

Usage:
  census.py selftest
  census.py run   <files-list> <out.json>   [--label NAME]
  census.py sample <out.json> --n 60 --seed 129 --out sample.txt
"""
import sys, os, re, json, random, bisect, hashlib, collections

# ----------------------------------------------------------------- tokenizer
COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
TOKEN_RE = re.compile(r"""
   (?P<ws>[ \t\r\n\\]+)
 | (?P<str>"(?:\\.|[^"\\\n])*")
 | (?P<chr>'(?:\\.|[^'\\\n])*')
 | (?P<num>\.?[0-9](?:[eEpP][-+]|[0-9a-zA-Z_.])*)
 | (?P<id>[A-Za-z_][A-Za-z0-9_]*)
 | (?P<punct>->|\+\+|--|<<=|>>=|<=|>=|==|!=|&&|\|\||\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<|>>|\.\.\.|.)
""", re.X | re.S)

def _blank(m):
    """replace a comment with the same number of newlines (keeps line numbers)"""
    return "\n" * m.group(0).count("\n")

PP_DEFINE_RE = re.compile(r"^\s*#\s*define\s+([A-Za-z_]\w*)\s*(?:\(([^)]*)\))?\s*(.*)$", re.S)
CONST_BODY_RE = re.compile(r"^[\s0-9xXa-fA-F\(\)\+\-\*/<>|&~ULul]*$")

class Tok:
    __slots__ = ("k", "t", "p")
    def __init__(self, k, t, p): self.k, self.t, self.p = k, t, p
    def __repr__(self): return f"{self.k}:{self.t}"

def preprocess(src):
    """Strip comments, pull out preprocessor directives, and RESOLVE conditional
    compilation to ONE configuration (first live branch; `#if 0` takes its
    `#else`).  Returns (code, pp_lines, dropped_lines).

    ⚠ Resolving is not optional: leaving both branches of an `#ifdef` in place
    desynchronises brace depth, and a desynced depth makes `find_functions`
    silently return NOTHING for the rest of the file.  Measured on php-4.0.2:
    without this, token coverage inside a recognised function body is 70.9%.
    """
    src = COMMENT_RE.sub(_blank, src)
    lines = src.split("\n")
    n = len(lines)
    isdir = [False] * n          # line belongs to a directive
    heads = {}                   # first line of a directive -> its text
    i = 0
    while i < n:
        if lines[i].lstrip().startswith("#"):
            a = i
            buf = [lines[i]]
            while buf[-1].rstrip().endswith("\\") and i + 1 < n:
                i += 1
                buf.append(lines[i])
            for k in range(a, i + 1):
                isdir[k] = True
            heads[a] = "\n".join(buf)
        i += 1
    pp = []
    stack = []                   # [cur_alive, parent_alive, taken_any]
    dropped = 0
    for i in range(n):
        if i in heads:
            txt = heads[i]
            w = txt.lstrip()[1:].lstrip()
            m = re.match(r"\w+", w)
            kw = m.group(0) if m else ""
            rest = w[len(kw):].strip()
            if kw in ("if", "ifdef", "ifndef"):
                par = all(st[0] for st in stack) if stack else True
                first = not (kw == "if" and re.match(r"^0\s*$", rest))
                stack.append([first and par, par, first])
            elif kw in ("elif", "else"):
                if stack:
                    st = stack[-1]
                    if st[2]:
                        st[0] = False
                    else:
                        st[0] = st[1]; st[2] = True
            elif kw == "endif":
                if stack: stack.pop()
            if all(st[0] for st in stack) if stack else True:
                pp.append(txt)
        alive = all(st[0] for st in stack) if stack else True
        if isdir[i] or not alive:
            if not isdir[i] and lines[i].strip(): dropped += 1
            lines[i] = ""
    return "\n".join(lines), pp, dropped

def const_macros(pp_lines):
    out = set()
    for d in pp_lines:
        m = PP_DEFINE_RE.match(d)
        if not m: continue
        name, args, body = m.group(1), m.group(2), (m.group(3) or "").strip()
        if args is not None:      # function-like macro: not a constant
            continue
        body = body.replace("\\\n", " ")
        if body and CONST_BODY_RE.match(body) and re.search(r"\d", body):
            out.add(name)
        elif re.match(r"^sizeof\b", body):
            out.add(name)
    return out

def lex(code):
    toks = []
    for m in TOKEN_RE.finditer(code):
        k = m.lastgroup
        if k == "ws": continue
        toks.append(Tok(k, m.group(0), m.start()))
    return toks

def linemap(code):
    return [m.start() for m in re.finditer("\n", code)]

def lineof(nl, pos):
    return bisect.bisect_right(nl, pos) + 1

# ----------------------------------------------------------------- vocabulary
TYPE_KW = {"char","short","int","long","unsigned","signed","float","double","void",
           "struct","union","enum","const","static","extern","register","volatile",
           "auto","inline","__inline","__inline__","_Bool","__extension__","restrict",
           "__restrict","__restrict__","typedef"}
CTRL_KW = {"return","if","else","while","for","do","switch","case","default","break",
           "continue","goto","sizeof"}
MEM_FN = {"memcpy","memmove","memset","memcmp","memchr","memrchr","mempcpy","memccpy",
          "bcopy","bzero","bcmp","wmemcpy","wmemmove","wmemset","wmemcmp"}
STR_FN = {"strcpy","strncpy","strcat","strncat","strcmp","strncmp","strcasecmp",
          "strncasecmp","strlen","strnlen","strchr","strrchr","strstr","strdup",
          "strndup","strtok","strtok_r","strspn","strcspn","strpbrk","strcoll",
          "sprintf","snprintf","vsprintf","vsnprintf","gets","stpcpy","stpncpy",
          "strlcpy","strlcat","strsep","wcscpy","wcsncpy","wcscat","wcslen"}
LEN_FN = {"strlen","strnlen","wcslen"}
# argument index (0-based) that carries the size bound; None => unbounded operator
SIZE_ARG = {
 "memcpy":2,"memmove":2,"memset":2,"memcmp":2,"memchr":2,"memrchr":2,"mempcpy":2,
 "memccpy":3,"bcopy":2,"bzero":1,"bcmp":2,"wmemcpy":2,"wmemmove":2,"wmemset":2,
 "wmemcmp":2,
 "strncpy":2,"strncat":2,"strncmp":2,"strncasecmp":2,"strnlen":1,"strndup":1,
 "snprintf":1,"vsnprintf":1,"stpncpy":2,"strlcpy":2,"strlcat":2,"wcsncpy":2,
}
UNBOUNDED = {"strcpy","strcat","sprintf","vsprintf","gets","strdup","stpcpy","strlen",
             "strcmp","strcasecmp","strchr","strrchr","strstr","strtok","strtok_r",
             "strspn","strcspn","strpbrk","strcoll","strsep","wcscpy","wcscat","wcslen"}

# ----------------------------------------------------------------- structure
def match_fwd(toks, i, open_t, close_t):
    d = 0
    while i < len(toks):
        t = toks[i].t
        if t == open_t: d += 1
        elif t == close_t:
            d -= 1
            if d == 0: return i
        i += 1
    return -1

class Func:
    __slots__ = ("name","a","b","params","param_ptrs","locals","ptrs","loops","cmps","conds","_toks","knr")

def _func_header(toks, i):
    """If toks[i] == '{' opens a function body, return (open_paren_idx, cp, knr).

    ⚠ Deliberately does NOT use a global brace-depth counter.  Conditional
    compilation leaves the depth skewed in real trees (`nstrftime.c` ends at
    depth -2, `fopen-wrappers.c` at +3), and a depth test then silently drops
    EVERY function after the skew.  Nesting is handled by span suppression in
    find_functions instead.
    """
    if i == 0 or toks[i].t != "{": return None
    cp = i - 1
    knr = False
    if toks[i-1].t == ";":
        j = i - 1
        while j >= 0 and toks[j].t != ")":
            if toks[j].t in ("{", "}"): return None
            if toks[j].k not in ("id", "num") and toks[j].t not in \
               (";", ",", "*", "[", "]", "(", ")"):
                return None
            j -= 1
        if j < 0: return None
        cp = j; knr = True
    elif toks[i-1].t != ")":
        return None
    d = 0; op = None; j = cp
    while j >= 0:
        if toks[j].t == ")": d += 1
        elif toks[j].t == "(":
            d -= 1
            if d == 0: op = j; break
        elif toks[j].t in ("{", "}", ";"):
            return None
        j -= 1
    if op is None or op == 0: return None
    nm = toks[op-1]
    if nm.k != "id" or nm.t in CTRL_KW: return None
    return (op, cp, knr)

def find_functions(toks):
    """[Func]; body span [a,b] are the indices of '{' and its matching '}'."""
    out = []
    end_of_last = -1
    n = len(toks)
    for i in range(n):
        if toks[i].t != "{" or i <= end_of_last:
            continue
        h = _func_header(toks, i)
        if h is None: continue
        op, cp, knr = h
        close = match_fwd(toks, i, "{", "}")
        if close < 0: continue
        f = Func()
        f.name = toks[op-1].t
        f.a, f.b = i, close
        f.params, f.param_ptrs = param_names(toks, op, cp)
        if knr:
            for kk in range(cp + 1, i):
                if toks[kk].k == "id" and toks[kk].t not in TYPE_KW \
                   and toks[kk].t not in DECL_START:
                    nx = toks[kk+1].t if kk + 1 < i else ""
                    if nx in (";", ",", "[", ")"):
                        f.params.add(toks[kk].t)
                        if toks[kk-1].t in ("*", "[") or nx == "[":
                            f.param_ptrs.add(toks[kk].t)
        f.knr = knr
        out.append(f)
        end_of_last = close
    return out

def param_names(toks, op, cp):
    """(all parameter names, those declared as pointers/arrays)"""
    names, ptrs = set(), set()
    part = []
    d = 0
    for k in range(op + 1, cp):
        t = toks[k]
        if t.t == "(" : d += 1
        if t.t == ")" : d -= 1
        if t.t == "," and d == 0:
            n, q = _param_one(part); names |= n; ptrs |= q; part = []
        else:
            part.append(t)
    n, q = _param_one(part); names |= n; ptrs |= q
    return names, ptrs

def _param_one(part):
    ids = [t.t for t in part if t.k == "id" and t.t not in TYPE_KW]
    if not ids: return set(), set()
    isptr = any(t.t in ("*", "[") for t in part)
    # function-pointer parameter:  int (*cb)(void)  -> name is right after '(*'
    for k in range(len(part) - 2):
        if part[k].t == "(" and part[k+1].t == "*" and part[k+2].k == "id":
            return {part[k+2].t}, set()
    nm = {ids[-1]}
    return nm, (nm if isptr else set())

DECL_START = TYPE_KW | {"size_t","ssize_t","uint8_t","uint16_t","uint32_t","uint64_t",
                        "int8_t","int16_t","int32_t","int64_t","zval","zend_bool",
                        "off_t","time_t","FILE","va_list","ptrdiff_t","intptr_t",
                        "uintptr_t","wchar_t"}

def scan_locals(toks, f):
    """crude local-declaration scan: names declared at statement start after a type"""
    loc, ptr = set(), set()
    i = f.a + 1
    stmt_start = True
    depth = 0
    while i < f.b:
        t = toks[i]
        if t.t in "{": depth += 1
        if t.t == "}": depth -= 1
        if stmt_start and t.k == "id" and (t.t in DECL_START or
                (i + 1 < f.b and toks[i+1].k == "id") or
                (i + 1 < f.b and toks[i+1].t == "*")):
            # walk the declaration to its ';'
            j = i
            star = 0
            while j < f.b and toks[j].t not in (";", "{"):
                if toks[j].t == "*": star += 1
                if toks[j].t == "," : star = 0
                if toks[j].k == "id" and toks[j].t not in TYPE_KW and toks[j].t not in DECL_START:
                    nxt = toks[j+1].t if j + 1 < f.b else ""
                    prv = toks[j-1].t if j > i else ""
                    if nxt in (";", ",", "=", "[", ")") or prv == "*":
                        loc.add(toks[j].t)
                        if star or nxt == "[":
                            ptr.add(toks[j].t)
                j += 1
            i = j
            stmt_start = True
            i += 1
            continue
        stmt_start = t.t in (";", "{", "}")
        i += 1
    return loc, ptr

REL = {"<", "<=", ">", ">="}

def analyse_function(toks, f):
    f._toks = toks
    f.locals, f.ptrs = scan_locals(toks, f)
    f.ptrs |= f.param_ptrs
    f.loops = []      # (body_a, body_b, {var: bound_tok_list}, header_a, header_b)
    f.cmps = []       # (tok_index, frozenset(root ids))
    f.conds = []      # (cond_a, cond_b, body_a, body_b, frozenset(ids in cond cmps))
    i = f.a + 1
    while i < f.b:
        t = toks[i]
        if t.k == "punct" and t.t in REL:
            f.cmps.append((i, frozenset(_ids_around(toks, i, f))))
        if t.k == "id" and t.t in ("for", "while", "if", "switch") and i + 1 < f.b and toks[i+1].t == "(":
            cp = match_fwd(toks, i + 1, "(", ")")
            if cp < 0: i += 1; continue
            ba, bb = _body_span(toks, cp + 1, f)
            cids = set()
            for j in range(i + 2, cp):
                if toks[j].k == "punct" and toks[j].t in REL:
                    cids |= _ids_around(toks, j, f)
            f.conds.append((i + 1, cp, ba, bb, frozenset(cids)))
            if t.t in ("for", "while"):
                f.loops.append((ba, bb, _loop_vars(toks, i, cp, t.t), i + 1, cp))
        i += 1
    f.loops.sort(key=lambda L: L[0])
    f.cmps.sort()

def _body_span(toks, i, f):
    if i < f.b and toks[i].t == "{":
        c = match_fwd(toks, i, "{", "}")
        return (i, c if c > 0 else f.b)
    j = i; d = 0
    while j < f.b:
        if toks[j].t in "([{": d += 1
        elif toks[j].t in ")]}": d -= 1
        elif toks[j].t == ";" and d == 0: return (i, j)
        j += 1
    return (i, f.b)

def _ids_around(toks, i, f):
    """root identifiers of the two operands of the comparison at index i"""
    out = set()
    j = i - 1; d = 0; n = 0
    while j > f.a and n < 8:
        t = toks[j]
        if t.t in ")]": d += 1
        elif t.t in "([":
            d -= 1
            if d < 0: break
        elif d == 0 and t.t in (";", "&&", "||", ",", "{", "}", "?", ":"): break
        if t.k == "id" and t.t not in CTRL_KW and t.t not in TYPE_KW: out.add(t.t)
        j -= 1; n += 1
    j = i + 1; d = 0; n = 0
    while j < f.b and n < 8:
        t = toks[j]
        if t.t in "([": d += 1
        elif t.t in ")]":
            d -= 1
            if d < 0: break
        elif d == 0 and t.t in (";", "&&", "||", ",", "{", "}", "?", ":"): break
        if t.k == "id" and t.t not in CTRL_KW and t.t not in TYPE_KW: out.add(t.t)
        j += 1; n += 1
    return out

def _loop_vars(toks, i, cp, kind):
    """{induction var -> bound expression tokens} for a for/while header"""
    out = {}
    op = i + 1
    secs = []
    if kind == "for":
        cur = []; d = 0
        for j in range(op + 1, cp):
            t = toks[j]
            if t.t in "([": d += 1
            elif t.t in ")]": d -= 1
            if t.t == ";" and d == 0:
                secs.append(cur); cur = []
            else:
                cur.append((j, t))
        secs.append(cur)
    else:
        secs = [[], [(j, toks[j]) for j in range(op + 1, cp)], []]
    cond = secs[1] if len(secs) > 1 else []
    for k in range(len(cond)):
        if cond[k][1].k == "punct" and cond[k][1].t in REL:
            lhs = [x for x in cond[:k] if x[1].k == "id"]
            rhs = [x for _, x in [(j, t) for j, t in cond[k+1:]]]
            # stop rhs at && / || / ,
            r = []
            for x in rhs:
                if x.t in ("&&", "||", ","): break
                r.append(x)
            if lhs:
                out[lhs[-1][1].t] = r
    return out

# ----------------------------------------------------------------- site finder
class Site:
    __slots__ = ("file","line","op","fn","expr","src","bound_source","check","resolved","callee")

def expr_tokens(toks, a, b):
    return [t for t in toks[a:b]]

def arg_spans(toks, op, cp):
    """top-level comma-separated argument spans of a call ( op='(' index )"""
    out = []
    d = 0; start = op + 1
    for j in range(op + 1, cp):
        t = toks[j].t
        if t in "([{": d += 1
        elif t in ")]}": d -= 1
        elif t == "," and d == 0:
            out.append((start, j)); start = j + 1
    out.append((start, cp))
    return out

def find_sites(toks, f):
    sites = []
    i = f.a + 1
    while i < f.b:
        t = toks[i]
        # --- subscript
        if t.t == "[" and i > f.a:
            p = toks[i-1]
            if (p.k == "id" and p.t not in TYPE_KW and p.t not in CTRL_KW) or p.t in (")", "]"):
                if not _is_declarator(toks, i, f):
                    cb = match_fwd(toks, i, "[", "]")
                    if cb > 0 and cb > i + 1:
                        s = Site(); s.op = "index"; s.fn = f.name
                        s.expr = expr_tokens(toks, i + 1, cb); s.callee = ""
                        s.line = i
                        sites.append(s)
                        i = i + 1
                        continue
        # --- unary * applied to a parenthesised expression
        if t.t == "*" and _is_unary_star(toks, i, f) and i + 1 < f.b and toks[i+1].t == "(":
            cp = match_fwd(toks, i + 1, "(", ")")
            if cp > 0:
                inner = toks[i+2:cp]
                if _is_cast(inner):
                    s = Site(); s.op = "cast_deref"; s.fn = f.name; s.callee = ""
                    s.expr = _additive_tail(toks, cp + 1, f)
                    s.line = i
                    sites.append(s); i += 1; continue
                add = _top_additive(toks, i + 2, cp)
                if add is not None:
                    s = Site(); s.op = "ptr_offset"; s.fn = f.name; s.callee = ""
                    s.expr = expr_tokens(toks, add + 1, cp); s.line = i
                    sites.append(s); i += 1; continue
        # --- ((T*)p)[i] style cast is caught by the subscript branch already
        # --- *p++ / *++p  cursor deref
        if t.t == "*" and _is_unary_star(toks, i, f) and i + 2 < f.b:
            if toks[i+1].k == "id" and toks[i+2].t in ("++", "--"):
                s = Site(); s.op = "ptr_offset"; s.fn = f.name; s.callee = ""
                s.expr = [toks[i+1]]; s.line = i
                sites.append(s); i += 1; continue
            if toks[i+1].t in ("++", "--") and toks[i+2].k == "id":
                s = Site(); s.op = "ptr_offset"; s.fn = f.name; s.callee = ""
                s.expr = [toks[i+2]]; s.line = i
                sites.append(s); i += 1; continue
        # --- library calls
        if t.k == "id" and (t.t in MEM_FN or t.t in STR_FN) and i + 1 < f.b and toks[i+1].t == "(":
            cp = match_fwd(toks, i + 1, "(", ")")
            if cp > 0:
                s = Site()
                s.op = "mem_call" if t.t in MEM_FN else "str_call"
                s.fn = f.name; s.callee = t.t; s.line = i
                ai = SIZE_ARG.get(t.t)
                if ai is None:
                    s.expr = []
                else:
                    sp = arg_spans(toks, i + 1, cp)
                    s.expr = expr_tokens(toks, *sp[ai]) if ai < len(sp) else []
                sites.append(s); i += 1; continue
        i += 1
    return sites

def _is_unary_star(toks, i, f):
    if i == f.a: return False
    p = toks[i-1]
    if p.k in ("id",) and p.t not in TYPE_KW and p.t not in CTRL_KW: return False
    if p.k == "num": return False
    if p.t in (")", "]"): return False
    return True

def _is_cast(inner):
    if not inner: return False
    if inner[0].k == "id" and (inner[0].t in TYPE_KW or inner[0].t in DECL_START):
        return any(x.t == "*" for x in inner)
    # (foo_t *) with an unknown typedef name
    if len(inner) >= 2 and inner[0].k == "id" and all(x.t == "*" for x in inner[1:]):
        return True
    return False

def _additive_tail(toks, j, f):
    if j < f.b and toks[j].t == "(":
        cp = match_fwd(toks, j, "(", ")")
        if cp > 0:
            add = _top_additive(toks, j + 1, cp)
            if add is not None:
                return toks[add + 1:cp]
        return []
    if j < f.b and toks[j].t in ("+", "-"):
        k = j + 1; d = 0; out = []
        while k < f.b:
            t = toks[k]
            if t.t in "([{": d += 1
            elif t.t in ")]}":
                d -= 1
                if d < 0: break
            elif d == 0 and t.t in (";", ",", ")"): break
            out.append(t); k += 1
        return out
    return []

def _top_additive(toks, a, b):
    """index of a top-level binary '+'/'-' inside toks[a:b], else None"""
    d = 0
    for j in range(a, b):
        t = toks[j].t
        if t in "([{":
            d += 1
        elif t in ")]}":
            d -= 1
        elif d == 0 and t in ("+", "-") and j > a:
            prev = toks[j-1]
            if prev.k in ("id", "num") or prev.t in (")", "]"):
                return j
    return None

def _is_declarator(toks, i, f):
    """is the '[' at index i an array DECLARATOR rather than a subscript?"""
    if toks[i-1].k != "id": return False
    if i - 2 < f.a: return False
    p2 = toks[i-2]
    if p2.k == "id" and p2.t not in CTRL_KW:
        return True                       # `char buf[` / `foo_t v[`
    if p2.t == "*":
        # `char *argv[` -> declarator;  `*p[`  -> ambiguous, treat as declarator only
        # if there is a type identifier two back
        if i - 3 >= f.a and toks[i-3].k == "id" and toks[i-3].t not in CTRL_KW:
            return True
    return False

# ----------------------------------------------------------------- classify
def root_ids(expr):
    out = set()
    for k, t in enumerate(expr):
        if t.k == "id" and t.t not in CTRL_KW and t.t not in TYPE_KW:
            nxt = expr[k+1].t if k + 1 < len(expr) else ""
            if nxt != "(":
                out.add(t.t)
    return out

def call_names(expr):
    out = []
    for k, t in enumerate(expr):
        if t.k == "id" and k + 1 < len(expr) and expr[k+1].t == "(":
            out.append(t.t)
    return out

def classify_bound(expr, f, cmac, enclosing_loops):
    if not expr: return "none"
    txt = [t.t for t in expr]
    if "sizeof" in txt: return "const"
    if all(t.k in ("num",) or t.k == "punct" for t in expr): return "const"
    cn = call_names(expr)
    if any(c in LEN_FN for c in cn): return "strlen"
    ids = root_ids(expr)
    if any(x in cmac for x in ids): return "const"
    if any(x.isupper() and len(x) > 1 and x not in f.locals and x not in f.params for x in ids):
        return "const"
    if cn: return "call"
    if any(t.t in ("->", ".") for t in expr): return "field"
    for (_, _, lv, _, _) in enclosing_loops:
        if ids & set(lv): return "induction"
    if any(x in f.ptrs for x in ids): return "cursor"
    if ids & f.params: return "param"
    if ids & f.locals: return "local"
    return "global"

def classify_check(site_i, expr, f):
    ids = root_ids(expr)
    if not ids: return "none"
    # innermost enclosing conditional whose condition compares one of `ids`
    enc = [(a, b, ba, bb, cids) for (a, b, ba, bb, cids) in f.conds if ba <= site_i <= bb or a <= site_i <= b]
    enc.sort(key=lambda c: (c[3] - c[2]))
    if enc and (ids & enc[0][4]): return "at_site"
    # same statement
    sa = _stmt_start(f, site_i)
    for (j, cids) in f.cmps:
        if sa <= j <= site_i and (ids & cids): return "at_site"
    for (a, b, ba, bb, cids) in enc:
        if ids & cids: return "earlier"
    for (j, cids) in f.cmps:
        if j < site_i and (ids & cids): return "earlier"
    return "none"

def _stmt_start(f, i):
    """index just after the nearest preceding ';', '{', '}' or ')' of a control
    header — i.e. the first token of the statement containing site index i."""
    toks = f._toks
    j = i - 1
    while j > f.a:
        if toks[j].t in (";", "{", "}"):
            return j + 1
        j -= 1
    return f.a + 1

# ----------------------------------------------------------------- driver
GEN_MARKERS = (b"generated by flex", b"A Bison parser", b"A lexical scanner generated",
               b"GNU Bison", b"created by flex", b"DO NOT EDIT", b"Generated automatically",
               b"machine generated", b"This file was generated")

def is_generated(raw):
    head = raw[:4096]
    return any(m in head for m in GEN_MARKERS)

def process_file(path, cmac_global):
    raw = open(path, "rb").read()
    gen = is_generated(raw)
    src = raw.decode("latin-1")
    code, pp, dropped = preprocess(src)
    cmac = set(cmac_global) | const_macros(pp)
    toks = lex(code)
    nl = linemap(code)
    funcs = find_functions(toks)
    rows = []
    pp_subscripts = sum(d.count("[") for d in pp)
    for f in funcs:
        analyse_function(toks, f)
        for s in find_sites(toks, f):
            i = s.line
            loops = [L for L in f.loops if L[0] <= i <= L[1]]
            s.bound_source = classify_bound(s.expr, f, cmac, loops)
            s.resolved = ""
            if s.bound_source == "induction":
                ids = root_ids(s.expr)
                for L in reversed(loops):
                    hit = [v for v in L[2] if v in ids]
                    if hit:
                        s.resolved = classify_bound(L[2][hit[0]], f, cmac,
                                                    [x for x in loops if x is not L])
                        break
                if not s.resolved: s.resolved = "none"
            s.check = classify_check(i, s.expr, f)
            rows.append({
                "file": path, "line": lineof(nl, toks[i].p), "fn": f.name,
                "op": s.op, "callee": s.callee,
                "expr": " ".join(t.t for t in s.expr)[:120],
                "bound_source": s.bound_source, "resolved": s.resolved,
                "check": s.check, "gen": gen,
            })
    return rows, len(funcs), pp_subscripts, len(toks), dropped

def collect_macros(paths):
    out = set()
    for p in paths:
        try:
            src = open(p, "rb").read().decode("latin-1")
        except OSError:
            continue
        _, pp, _d = preprocess(src)
        out |= const_macros(pp)
    return out

def cmd_run(argv):
    listfile, outfile = argv[0], argv[1]
    label = argv[argv.index("--label") + 1] if "--label" in argv else "corpus"
    hdr = argv[argv.index("--headers") + 1] if "--headers" in argv else None
    files = []
    for line in open(listfile, errors="surrogateescape"):
        line = line.rstrip("\n")
        if not line: continue
        files.append(line.split("\t")[-1])
    cmac = set()
    if hdr:
        hp = [l.rstrip("\n").split("\t")[-1] for l in open(hdr, errors="surrogateescape") if l.strip()]
        cmac = collect_macros(hp)
    allrows = []
    nfunc = 0; npp = 0; ntok = 0; nfail = 0; ndrop = 0
    for p in files:
        try:
            r, nf, pps, nt, dr = process_file(p, cmac)
        except Exception as e:
            nfail += 1
            sys.stderr.write(f"FAIL {p}: {e}\n")
            continue
        allrows += r; nfunc += nf; npp += pps; ntok += nt; ndrop += dr
    meta = {"label": label, "files": len(files), "failed": nfail,
            "functions": nfunc, "tokens": ntok,
            "pp_subscripts_skipped": npp, "sites": len(allrows),
            "lines_dropped_by_ifdef_resolution": ndrop,
            "const_macros_from_headers": len(cmac)}
    json.dump({"meta": meta, "rows": allrows}, open(outfile, "w"))
    print(json.dumps(meta, indent=1))

def cmd_sample(argv):
    src = argv[0]
    n = int(argv[argv.index("--n") + 1])
    seed = int(argv[argv.index("--seed") + 1])
    out = argv[argv.index("--out") + 1]
    d = json.load(open(src))
    rows = d["rows"]
    rnd = random.Random(seed)
    idx = sorted(rnd.sample(range(len(rows)), n))
    with open(out, "w") as fh:
        fh.write(f"# sample of {n} SITES from {src} (population {len(rows)}), "
                 f"random.Random({seed}).sample(range(N), {n}), sorted\n")
        for k, j in enumerate(idx):
            r = rows[j]
            fh.write("\n" + "=" * 78 + f"\n[{k+1}] rowidx={j}\n")
            fh.write(f"file: {r['file']}\nline: {r['line']}  fn: {r['fn']}\n")
            fh.write(f"AUTO op={r['op']} callee={r['callee']} bound_source={r['bound_source']}"
                     f" resolved={r['resolved']} check={r['check']}\n")
            fh.write(f"expr: {r['expr']}\n---- context ----\n")
            try:
                lines = open(r["file"], "rb").read().decode("latin-1").split("\n")
            except OSError:
                lines = []
            a = max(0, r["line"] - 16); b = min(len(lines), r["line"] + 6)
            for ln in range(a, b):
                mark = ">>" if ln + 1 == r["line"] else "  "
                fh.write(f"{mark}{ln+1:6d}| {lines[ln]}\n")
    print(f"wrote {out} ({n} sites)")

# ----------------------------------------------------------------- self test
SELFTEST = r"""
#define CAP 64
#define NOTCONST foo(x)
#define MACRO_SITE(a,i) ((a)[(i)] = 0)      /* pp line: NOT scanned */
static char gbuf[CAP];

struct rec { unsigned char *data; int len; };

int t1(char *dst, const char *src, int n, struct rec *r, char *end)
{
    char local[CAP];            /* DECLARATOR, not a site */
    int i, k;
    unsigned char *p = (unsigned char *)src;

    memcpy(dst, src, CAP);          /* S1  mem_call  const      */
    memcpy(dst, src, n);            /* S2  mem_call  param      */
    memcpy(dst, src, r->len);       /* S3  mem_call  field      */
    memcpy(dst, src, strlen(src));  /* S4  mem_call  strlen  (+S5 str_call none) */
    strcpy(dst, src);               /* S6  str_call  none       */
    strcat(dst, src);               /* S7  str_call  none       */
    strncpy(dst, src, sizeof local);/* S8  str_call  const      */
    memcpy(dst, src, count_it(r));  /* S9  mem_call  call       */

    for (i = 0; i < n; i++)
        dst[i] = src[i];            /* S10,S11 index induction, resolved param */

    for (k = 0; k < CAP; k++)
        local[k] = 0;               /* S12 index induction, resolved const */

    if (n < CAP)
        gbuf[n] = 1;                /* S13 index param, check at_site */

    if (n < CAP) { }
    gbuf[n] = 2;                    /* S14 index param, check earlier */

    gbuf[k] = 3;                    /* S15 index local, check earlier (loop cond) */

    while (p < (unsigned char *)end)
        i += *p++;                  /* S16 ptr_offset induction, resolved cursor */

    i += *(src + n);                /* S17 ptr_offset param */
    i += *(int *)(src + 4);         /* S18 cast_deref const */
    return i + local[0] + r->data[3];  /* S19 index const, S20 index const */
}

/* ---- adversarial arms: NONE of these may produce a site ---- */
int t2(void)
{
    /* a comment containing buf[i] and memcpy(a,b,c) and strcpy(x,y) */
    const char *s1 = "buf[i] memcpy(a,b,c) strcpy(x,y)";
    char c = '[';
    int table[8] = { [3] = 1 };   /* designated initialiser, and a declarator */
    static const int t2a[] = { 1, 2, 3 };
    return (int)(s1[0]) + c + table[0] + t2a[0];  /* A1 A2 A3 : three real sites */
}

/* ---- K&R definition, 2-D subscript, ternary ---- */
int t3(a, n)
    char **a;
    int n;
{
    return a[0][1] + (n > 2 ? a[1][0] : 0);   /* B1..B4 four subscripts */
}
"""

SELFTEST_EXPECT = {
    "t1": [("mem_call","const","","none"), ("mem_call","param","","none"),
           ("mem_call","field","","none"), ("mem_call","strlen","","none"),
           ("str_call","none","","none"), ("str_call","none","","none"),
           ("str_call","none","","none"), ("str_call","const","","none"),
           ("mem_call","call","","none"),
           ("index","induction","param","at_site"), ("index","induction","param","at_site"),
           ("index","induction","const","at_site"),
           ("index","param","","at_site"), ("index","param","","earlier"),
           ("index","local","","earlier"),
           ("ptr_offset","induction","cursor","at_site"),
           ("ptr_offset","param","","earlier"),
           ("cast_deref","const","","none"),
           ("index","const","","none"), ("index","const","","none")],
    "t2": [("index","const","","none")] * 3,
    "t3": [("index","const","","none")] * 4,
}

def cmd_selftest(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = os.path.join(here, "selftest.c")
    open(tmp, "w").write(SELFTEST)
    rows, nf, npp, nt, _dr = process_file(tmp, set())
    got = {}
    for r in rows:
        got.setdefault(r["fn"], []).append(
            (r["op"], r["bound_source"], r["resolved"], r["check"]))
    bad = 0
    for fn, exp in SELFTEST_EXPECT.items():
        g = got.get(fn, [])
        if g != exp:
            bad += 1
            print(f"MISMATCH in {fn}: expected {len(exp)} sites, got {len(g)}")
            for k in range(max(len(exp), len(g))):
                e = exp[k] if k < len(exp) else None
                a = g[k] if k < len(g) else None
                if e != a: print(f"   [{k}] expect={e}  got={a}")
        else:
            print(f"OK   {fn}: {len(g)}/{len(exp)} sites, all four fields match")
    extra = set(got) - set(SELFTEST_EXPECT)
    if extra:
        bad += 1; print("UNEXPECTED FUNCTIONS:", extra)
    # NEGATIVE control: a file with no memory access at all must give 0 sites
    neg = os.path.join(here, "selftest_neg.c")
    open(neg, "w").write("int f(int a, int b) { int c = a * b + 3; return c; }\n")
    nrows, _, _, _, _ = process_file(neg, set())
    print(f"NEGATIVE control: {len(nrows)} sites (must be 0)")
    if nrows: bad += 1
    # MUST-FIRE control: break the tokenizer's comment stripping and the arm must fail
    global COMMENT_RE
    save = COMMENT_RE
    COMMENT_RE = re.compile(r"(?!x)x")     # matches nothing => comments NOT stripped
    brows, _, _, _, _ = process_file(tmp, set())
    COMMENT_RE = save
    fired = len(brows) != len(rows)
    print(f"MUST-FIRE arm (disable comment stripping): sites {len(rows)} -> {len(brows)} "
          f"=> {'FIRED' if fired else 'DID NOT FIRE (instrument is blind)'}")
    if not fired: bad += 1
    print("SELFTEST", "PASS" if bad == 0 else f"FAIL ({bad} problems)")
    for r in rows:
        print(f"  {r['fn']} L{r['line']:<3} {r['op']:<11} {r['bound_source']:<10} "
              f"res={r['resolved']:<9} check={r['check']:<9} expr={r['expr']!r}")
    return 0 if bad == 0 else 1

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "selftest": sys.exit(cmd_selftest(sys.argv[2:]))
    elif c == "run": cmd_run(sys.argv[2:])
    elif c == "sample": cmd_sample(sys.argv[2:])
    else: print(__doc__); sys.exit(2)
