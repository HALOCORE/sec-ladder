#!/usr/bin/env python3
"""THE PRE-IMAGE SCREEN -- mechanically exclude `fix_commit`s that cannot be the
5.0.0 repair.

    TASK_PHP_030.  Origin: TASK_PHP_029 §3, which refuted `ph21`'s fix_commit
    FROM THE COMMIT'S OWN BYTES rather than from a tag comparison.

THE RULE
--------
    If a fix_commit's patch TOUCHES the defect's file but its PRE-IMAGE for
    that file does NOT contain the 5.0.0 text at the cited site, that commit is
    NOT the repair of that site.

A unified diff only applies to a tree whose text matches the hunk's context and
`-` lines.  So the pre-image IS a partial snapshot of the tree the commit was
written against.  If the 5.0.0 line the corpus cites is nowhere in that
snapshot, the commit was diffed against a tree that no longer has it -- i.e.
something else removed it first.  That is a PROOF OF EXCLUSION, not a ranking.

THREE OUTCOMES, NOT TWO
-----------------------
    INAPPLICABLE    the patch has no pre-image hunk for the defect's file at
                    all (the `ph07` shape: the fix is in the caller, in another
                    file).  The screen says NOTHING about such a commit.
    NOT-THE-REPAIR  the patch DOES touch the defect's file, and none of the
                    cited 5.0.0 lines appear in its pre-image for that file.
    CANDIDATE       at least one cited 5.0.0 line appears.  ⚠ CANDIDATE IS NOT
                    A VERDICT OF CORRECTNESS.  It means the screen could not
                    exclude the commit.  The tag comparison still owes an
                    answer (PROTOCOL_PHP.md §F5(iii)).

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
  * It never looks at a LINE NUMBER in the patch.  Between 5.0.0 and a 2016
    commit the same function has moved thousands of lines; `@@ -4949` in
    c591f022f8ab is not ph21's `:4120`.  Matching is TEXT-ONLY.
  * It does not `git apply` anything and needs no repository and no network.
  * It does not decide WHICH commit is the repair.  It only removes some.

NORMALISATION (stated, because §3.3 requires it)
------------------------------------------------
  norm_ws(s)    -- strip trailing '\\r', collapse every run of whitespace
                   (tabs included) to one space, strip the ends.
  norm_code(s)  -- norm_ws, then delete /*...*/ and //... comment text, then
                   collapse again.  Comments are dropped because PHP's tree
                   re-flows them; code is NOT touched otherwise.
  Both are applied to BOTH sides.  Nothing is lowercased, no punctuation is
  removed, no identifier is renamed -- so two lines that differ by a single
  operator still compare different (asserted in --selftest, case N3).

MATCHABILITY
------------
  A cited 5.0.0 line is `matchable` if, after norm_code, it is non-empty, is
  not a purely structural line (`}`, `{`, `};`, `break;`, `return;`, `#endif`
  ...) and contains at least one identifier of length >= 3.  A structural line
  carries NO information about WHERE a pre-image sits -- every hunk in every
  patch has braces -- so counting it as a hit would make every record a
  CANDIDATE and destroy the screen.  The count of dropped lines is REPORTED per
  record, never hidden.

  ⚠ The screen is deliberately CONSERVATIVE: ONE matchable hit is enough for
  CANDIDATE.  False CANDIDATEs cost coverage; a false NOT-THE-REPAIR would be a
  wrong exclusion, and exclusion is the whole product.

USAGE
-----
    python3 .temp/php30/preimage_screen.py --selftest     # §H, no network
    python3 .temp/php30/preimage_screen.py --all          # every resolved record
    python3 .temp/php30/preimage_screen.py --row ph21     # one row
    python3 .temp/php30/preimage_screen.py --all --json OUT.json
    python3 .temp/php30/preimage_screen.py --all --no-file-restrict   # control
"""
import argparse, hashlib, importlib.util, json, os, re, sys, tarfile

ROOT = "/home/apt/repos_common/sec-ladder"
PATCHES = os.path.join(ROOT, ".temp/mgr/batch/patches")
# ⚠ the shared cache first; a task's own scratch cache second.  A sha the
# 169-record sweep never needed (ph95's two extra candidates, §5) lives here.
PATCH_DIRS = [PATCHES, os.path.join(ROOT, ".temp/php30/patches")]
FIXSURVEY_JSON = os.path.join(ROOT, ".temp/mgr/batch/fixsurvey.json")
FIXSURVEY_PY = os.path.join(ROOT, ".tasks-php/fixsurvey.py")

TARBALL_SHA256 = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
TARBALL_DEFAULT = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/"
                   "oracle/build-5.0.0/php-5.0.0.tar.gz")

# ---------------------------------------------------------------- 5.0.0 source

_TAR = None
_SRC_CACHE = {}


def tarball_path():
    return os.environ.get("PHP500_TARBALL", TARBALL_DEFAULT)


def _open_tarball():
    """SOURCES.md §1: refuse any tarball whose sha256 is not the pinned one."""
    global _TAR
    if _TAR is None:
        p = tarball_path()
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h != TARBALL_SHA256:
            sys.exit(f"REFUSED: {p} sha256 {h} != pinned {TARBALL_SHA256}")
        _TAR = tarfile.open(p, "r:gz")
    return _TAR


def src_lines(path):
    """1-based line list for php-5.0.0/<path>.  Byte-for-byte the same split as
    SOURCES.md §2's `tar -xzOf <tarball> php-5.0.0/<path> | sed -n 'a,bp'`
    (verified: identical sha256 on Zend/zend_object_handlers.c 520,545)."""
    if path not in _SRC_CACHE:
        try:
            f = _open_tarball().extractfile("php-5.0.0/" + path)
            if f is None:
                _SRC_CACHE[path] = None
            else:
                _SRC_CACHE[path] = f.read().decode("utf-8", "replace").split("\n")
        except KeyError:
            _SRC_CACHE[path] = None
    return _SRC_CACHE[path]


# ---------------------------------------------------------------- citations

# `ext/standard/string.c:4144`, `Zend/zend_execute.c:1146-1149`, and bare
# `:542` / `:587-588` continuations which inherit the previous path.
_CITE = re.compile(r"(?:(?P<path>[A-Za-z0-9_./+-]*[A-Za-z0-9_-]\.(?:c|h|y|re|phpt))\s*)?"
                   r":(?P<lo>\d+)(?:\s*-\s*(?P<hi>\d+))?")


def parse_citation(cell):
    """`c_file_line` -> ([(path, lo, hi), ...], residual_note).

    The cell is prose: 58 of 166 are a bare `path:N`, the rest carry secondary
    sites, faulting frames and commentary.  Every `path:N[-M]` is taken, and a
    bare `:N[-M]` inherits the path most recently named -- which is exactly how
    the corpus writes `Zend/zend_object_handlers.c:524 (+ :542, :587-588)`.

    ⚠ Line numbers appearing with NO colon (`(also 3903-3905, 3914)`) are NOT
    parsed; they are reported in `residual` so nothing is silently dropped."""
    cites, last, seen = [], None, []
    for m in _CITE.finditer(cell):
        p = m.group("path") or last
        if not p:
            continue
        last = p
        lo = int(m.group("lo"))
        hi = int(m.group("hi") or lo)
        if hi < lo:
            lo, hi = hi, lo
        cites.append((p, lo, hi))
        seen.append(m.span())
    # residual: any run of digits not consumed by a citation
    resid = []
    for m in re.finditer(r"\d+", cell):
        if not any(a <= m.start() < b for a, b in seen):
            resid.append(m.group(0))
    return cites, resid


# ---------------------------------------------------------------- patches

_PATCH_CACHE = {}


def patch_sections(sha):
    """sha -> {a_side_path: [section_text, ...]} for every `diff --git` block.

    Keyed on the **a-side** name because the pre-image is what we are asking
    about; a rename shows up as a != b and the a-side is the old tree."""
    if sha in _PATCH_CACHE:
        return _PATCH_CACHE[sha]
    p = None
    for d in PATCH_DIRS:
        c = os.path.join(d, f"{sha}.patch")
        if os.path.exists(c) and os.path.getsize(c) > 0:
            p = c
            break
    if p is None:
        _PATCH_CACHE[sha] = None
        return None
    txt = open(p, encoding="utf-8", errors="replace").read()
    parts = re.split(r"^diff --git a/(\S+) b/(\S+)$", txt, flags=re.M)
    out = {}
    for i in range(1, len(parts), 3):
        out.setdefault(parts[i], []).append(parts[i + 2])
    _PATCH_CACHE[sha] = out
    return out


def preimage_lines(section_texts):
    """§3.2: the pre-image is CONTEXT (' ') plus REMOVED ('-') lines, and
    nothing else.  `+` lines are the post-image and are excluded -- including
    them is the permissive error that makes every record look like a match.

    Returns raw (un-normalised) source lines."""
    out = []
    for sec in section_texts:
        in_hunk = False
        for ln in sec.split("\n"):
            if ln.startswith("@@"):
                in_hunk = True
                continue
            if not in_hunk:
                continue
            if ln.startswith("diff ") or ln.startswith("index ") \
               or ln.startswith("--- ") or ln.startswith("+++ "):
                in_hunk = False
                continue
            if ln.startswith("\\"):          # "\ No newline at end of file"
                continue
            if ln.rstrip() == "--":          # git format-patch signature trailer
                in_hunk = False
                continue
            if ln.startswith("-") or ln.startswith(" "):
                out.append(ln[1:])
            elif ln.startswith("+"):
                continue
            else:
                # a blank line inside a hunk is a context line with its single
                # leading space stripped by some mailers; treat as context.
                if ln == "":
                    out.append("")
                else:
                    in_hunk = False
    return out


# ---------------------------------------------------------------- normalising

_WS = re.compile(r"\s+")
_BLOCK_C = re.compile(r"/\*.*?\*/", re.S)
_LINE_C = re.compile(r"//.*$")

STRUCTURAL = {
    "", "{", "}", "};", "});", "}", ")", ");", "(", ",", ";",
    "break;", "continue;", "return;", "} else {", "} else", "else {", "else",
    "#endif", "#else", "*/", "/*", "do {", "} while (0)", "} while (0);",
    "return NULL;", "return;", "default:", "break", "#if 0",
}
_IDENT3 = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


def norm_ws(s):
    return _WS.sub(" ", s.replace("\r", "")).strip()


def norm_code(s):
    """⚠ Deliberately SHALLOW.  It removes only what PHP's tree re-flows:
    complete `/*...*/` on one line, `//...` to end of line, and an unterminated
    `/*...` tail.  It does NOT try to delete the *body* of a multi-line comment
    (a ` * foo` continuation line normalises to `* foo` and is compared as
    text) -- deleting it would need comment state the screen does not have, and
    an over-eager normaliser is the failure §3.3 warns about."""
    s = _BLOCK_C.sub(" ", s.replace("\r", ""))
    s = _LINE_C.sub(" ", s)
    s = re.sub(r"/\*.*$", " ", s)          # unterminated /* tail
    return _WS.sub(" ", s).strip()


def matchable(norm):
    if norm in STRUCTURAL:
        return False
    if not _IDENT3.search(norm):
        return False
    return True


# ---------------------------------------------------------------- the screen

def screen_record(rec, corpus_row, file_restrict=True, span_override=None):
    """One (row, corpus-id, sha) record -> a verdict dict."""
    row, cid, sha = rec["row"], rec["id"], rec.get("sha", "")
    out = {"row": row, "id": cid, "sha": sha,
           "defect_file": rec.get("defect_file", ""),
           "verdict": "?", "why": "",
           "span": [], "span_lines": [], "hits": [], "misses": [],
           "n_matchable": 0, "n_dropped": 0, "elsewhere": {},
           "patch_files": [], "residual_numbers": [], "residual_lines": [],
           "residual_hits": [], "bracketed": None, "bracket_evidence": {},
           "same_function": None, "same_function_evidence": {},
           "decisive": None}

    if not re.fullmatch(r"[0-9a-f]{11,40}", sha or ""):
        out["verdict"] = "NO-SHA"
        out["why"] = "the corpus cell carries no sha (ph36: bison regeneration)"
        return out

    sections = patch_sections(sha)
    if sections is None:
        out["verdict"] = "NO-PATCH"
        out["why"] = f"{sha}.patch is not in the cache; run fixsurvey.py online"
        return out
    out["patch_files"] = sorted(sections)

    cell = (corpus_row.get("c_file_line") or "").strip()
    cites, resid = parse_citation(cell)
    out["residual_numbers"] = resid
    if not cites:
        out["verdict"] = "NO-SPAN"
        out["why"] = f"c_file_line does not parse into any path:line -- {cell[:80]!r}"
        return out

    dfile = cites[0][0]
    out["defect_file"] = dfile
    if span_override is not None:
        spans = [(dfile, a, b) for a, b in span_override]
        resid = []
    else:
        spans = [c for c in cites if c[0] == dfile]
    out["span"] = [[a, b] for _, a, b in spans]

    src = src_lines(dfile)
    if src is None:
        out["verdict"] = "NO-SPAN"
        out["why"] = f"{dfile} is not in the 5.0.0 tarball"
        return out

    # ---- the 5.0.0 text at the cited site
    nums = []
    for _, a, b in spans:
        nums.extend(range(a, b + 1))
    nums = sorted(set(n for n in nums if 1 <= n <= len(src)))
    # ⚠⚠ RESIDUAL LINES.  `ext/standard/streamsfuncs.c:728 (and 735, 742)` and
    # `ext/standard/array.c:3938 (also 3903-3905, 3914)` cite further sites with
    # NO colon and NO path, so the `path:N` parse cannot see them.  Reading
    # `:728` alone made ph73/CRASH-100 come out NOT-THE-REPAIR when 735 and 742
    # are BOTH in the pre-image -- a FALSE EXCLUSION, which is the one direction
    # this screen may not fail in.  So every bare number in the cell that is a
    # valid line of the defect file is added to the search set and FLAGGED.
    # ⚠ Some of these are certainly not line numbers (`2014` in "the 2014 fix
    # commit's line numbers", `5`/`0`/`0` from "php-5.0.0").  That is the SAFE
    # direction: a spurious extra line can only turn an exclusion into a
    # CANDIDATE -- it costs coverage, never soundness.  Hits that come ONLY
    # from a residual line are reported separately as `residual_hits`.
    resid_nums = sorted({int(x) for x in resid if x.isdigit()
                         and 1 <= int(x) <= len(src)} - set(nums))
    out["residual_lines"] = resid_nums
    nums = sorted(set(nums) | set(resid_nums))
    if not nums:
        out["verdict"] = "NO-SPAN"
        out["why"] = (f"cited lines {out['span']} are out of range for {dfile} "
                      f"({len(src)} lines)")
        return out

    cited = [(n, src[n - 1]) for n in nums]
    out["span_lines"] = [[n, t] for n, t in cited]
    keep = [(n, t, norm_code(t)) for n, t in cited]
    good = [(n, t, k) for n, t, k in keep if matchable(k)]
    out["n_matchable"] = len(good)
    out["n_dropped"] = len(keep) - len(good)
    if not good:
        out["verdict"] = "NO-SPAN"
        out["why"] = ("every cited 5.0.0 line is blank/structural, so there is "
                      "nothing distinctive to look for")
        return out

    # ---- the pre-image
    if file_restrict:
        targets = [dfile] if dfile in sections else []
    else:
        targets = sorted(sections)
    if not targets:
        out["verdict"] = "INAPPLICABLE"
        out["why"] = (f"the patch does not touch {dfile} at all "
                      f"(it touches {', '.join(sorted(sections))})")
        # even so, say whether the 5.0.0 text turns up in some OTHER file the
        # patch does touch -- that is the "the file moved" signal (F34).
        out["elsewhere"] = _elsewhere(sections, good, skip=dfile)
        return out

    pre = preimage_lines([s for t in targets for s in sections[t]])
    preset = set()
    for ln in pre:
        preset.add(norm_code(ln))
    hits, misses = [], []
    for n, t, k in good:
        (hits if k in preset else misses).append([n, t])
    out["nearest"] = {str(n): nearest_preimage(norm_code(t), preset)
                      for n, t in misses}
    out["hits"], out["misses"] = hits, misses
    out["residual_hits"] = [h for h in hits if h[0] in resid_nums]
    out["elsewhere"] = _elsewhere(sections, good, skip=dfile)

    if not hits and file_restrict:
        cnums = [n for n, _ in misses]
        br, ev = bracketed(src, sections[dfile], cnums)
        out["bracketed"], out["bracket_evidence"] = br, ev
        sf, ev2 = same_function(src, sections[dfile], cnums)
        out["same_function"], out["same_function_evidence"] = sf, ev2
        out["decisive"] = bool(br or sf)

    if hits:
        out["verdict"] = "CANDIDATE"
        only_resid = all(h[0] in resid_nums for h in hits)
        out["why"] = (f"{len(hits)}/{len(good)} cited 5.0.0 lines are present in "
                      f"the pre-image of {dfile}"
                      + (" — ⚠ ALL of them from RESIDUAL (bare-number) citations"
                         if only_resid and resid_nums else ""))
    else:
        out["verdict"] = "NOT-THE-REPAIR"
        out["why"] = (f"the patch touches {dfile} but NONE of its {len(good)} "
                      f"cited 5.0.0 lines appear in that file's pre-image"
                      + ("; and the commit's window PROVABLY REACHES the site "
                         "(DECISIVE)" if out.get("decisive") else
                         "; ⚠ but nothing shows the commit's window reaches the "
                         "site, so the absence may be the window's and not the "
                         "tree's (NOT DECISIVE)"))
    return out


def split_hunks(section_texts):
    """One entry per hunk, so a hunk can be located independently."""
    out = []
    for sec in section_texts:
        cur = None
        for ln in sec.split("\n"):
            if ln.startswith("@@"):
                if cur is not None:
                    out.append(cur)
                cur = [ln]          # the header is KEPT so a TEST can read it;
                continue            # the screen itself never parses its numbers
            if cur is not None:
                cur.append(ln)
        if cur is not None:
            out.append(cur)
    return ["\n".join(h) for h in out]


def bracketed(src, section_texts, cited_nums, window=60):
    """⚠⚠ THE SOUNDNESS TEST, AND IT IS WHAT SEPARATES A PROOF FROM A SHRUG.

    `the cited text is absent from the pre-image` has TWO readings:

      (i)  the tree the commit was diffed against NO LONGER HAS that text --
           a genuine exclusion, `TASK_PHP_029` §3's `ph21`; or
      (ii) the tree still has it and the hunk's ~3-line context window simply
           does not REACH it -- in which case the absence proves nothing.

    The median pre-image behind an exclusion is 14 lines, so (ii) is not a
    corner case.  This distinguishes them WITHOUT reading a patch line number:

      locate each hunk in the 5.0.0 file BY TEXT.  A 5.0.0 line is an ANCHOR
      for a hunk if its normalised text (a) appears in that hunk's pre-image,
      (b) is matchable, and (c) occurs EXACTLY ONCE in the whole 5.0.0 file --
      so it pins a position.  If some hunk has an anchor BEFORE the cited line
      and an anchor AFTER it, within `window` 5.0.0 lines, then that hunk's
      pre-image spans the cited site and the cited line is missing FROM INSIDE
      the window.  Reading (i).  Otherwise reading (ii).

    Returns (bracketed_bool, evidence)."""
    counts = {}
    for t in src:
        k = norm_code(t)
        counts[k] = counts.get(k, 0) + 1
    uniq = {}
    for i, t in enumerate(src, 1):
        k = norm_code(t)
        if k and counts[k] == 1 and matchable(k):
            uniq[k] = i

    for h in split_hunks(section_texts):
        pre = {norm_code(x) for x in preimage_lines([h])}
        anchors = sorted(uniq[k] for k in pre if k in uniq)
        if not anchors:
            continue
        for c in cited_nums:
            lo = [a for a in anchors if a < c]
            hi = [a for a in anchors if a > c]
            if lo and hi and (min(hi) - max(lo)) <= window:
                return True, {"cited": c, "before": max(lo), "after": min(hi),
                              "n_anchors": len(anchors)}
    return False, {}


_FUNCHEAD = re.compile(r"^[A-Za-z_$]")


def enclosing_header(src, n):
    """The line git's default C `xfuncname` heuristic would print in a hunk
    header for a hunk at 5.0.0 line `n`: the nearest preceding line that starts
    at column 0 with a letter, `_` or `$`.  ⚠ This reads a 5.0.0 line number,
    which is fine -- what §3.1 forbids is reading the PATCH's line numbers."""
    for i in range(n - 1, 0, -1):
        if _FUNCHEAD.match(src[i - 1]):
            return i, src[i - 1]
    return None, None


def same_function(src, section_texts, cited_nums):
    """⚠⚠ THE OTHER HALF OF THE SOUNDNESS TEST, AND THE ONE THAT FIRES ON
    `ph21`.

    A hunk header is `@@ -a,b +c,d @@ <enclosing function>`, and that trailing
    text is git's own answer to `which function is this hunk in?`.  It is TEXT,
    not a line number.  If it equals the enclosing header of the CITED 5.0.0
    line, then the commit edited THE SAME FUNCTION the corpus cites -- so its
    window does reach the site, and the cited line's absence from the
    pre-image means the tree differs there.  That is `TASK_PHP_029` §3 exactly:
    `@@ -4949,6 +4949,10 @@ PHP_FUNCTION(str_repeat)` against 5.0.0's
    `PHP_FUNCTION(str_repeat)` at :4115, cited line :4144."""
    want = set()
    for c in cited_nums:
        _, h = enclosing_header(src, c)
        if h:
            want.add(norm_code(h))
    if not want:
        return False, {}
    for h in split_hunks(section_texts):
        head = h.split("\n", 1)[0]
        m = re.match(r"^@@ -\S+ \+\S+ @@ ?(.*)$", head)
        ctx = norm_code(m.group(1)) if m else ""
        if not ctx:
            continue
        for w in want:
            if w == ctx or w.startswith(ctx) or ctx.startswith(w):
                return True, {"hunk_context": ctx, "5.0.0_enclosing": w}
    return False, {}


def nearest_preimage(target_norm, preimage_norms, n=1):
    """The pre-image line the commit's tree has WHERE 5.0.0 has `target`.

    Purely for the side-by-side report -- it never touches a verdict.  Uses
    difflib similarity over the normalised pre-image, so it is a `looks like'
    and nothing more; the report labels it that way."""
    import difflib
    best = difflib.get_close_matches(target_norm, list(preimage_norms), n=n,
                                     cutoff=0.35)
    return best


def _elsewhere(sections, good, skip):
    """Which OTHER files of the same patch carry the cited 5.0.0 text in their
    pre-image.  A hit here on a NOT-THE-REPAIR / INAPPLICABLE record means the
    code MOVED FILE between 5.0.0 and the commit -- F34's third cause."""
    res = {}
    for f, secs in sections.items():
        if f == skip:
            continue
        preset = {norm_code(x) for x in preimage_lines(secs)}
        h = [n for n, t, k in good if k in preset]
        if h:
            res[f] = h
    return res


# ---------------------------------------------------------------- driver

def load_records():
    if not os.path.exists(FIXSURVEY_JSON):
        sys.exit(f"missing {FIXSURVEY_JSON}; run `python3 .tasks-php/fixsurvey.py --offline`")
    d = json.load(open(FIXSURVEY_JSON))
    out = []
    for row in sorted(d["rows"], key=lambda s: int(s[2:])):
        out.extend(d["rows"][row])
    return out


def load_corpus_index():
    spec = importlib.util.spec_from_file_location("fixsurvey", FIXSURVEY_PY)
    mod = importlib.util.module_from_spec(spec)
    saved, sys.argv = sys.argv, ["fixsurvey.py", "--offline"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod.load_corpus()


def run(records, idx, file_restrict=True):
    res = []
    for rec in records:
        cr = idx.get(rec["id"])
        if cr is None:
            r = dict(rec)
            r["verdict"] = "UNRESOLVED"
            r["why"] = "corpus index cannot find this id"
            res.append(r)
            continue
        res.append(screen_record(rec, cr, file_restrict=file_restrict))
    return res


# ---------------------------------------------------------------- §H selftest

GROUND_TRUTH = [
    # (row, corpus id, sha, expected verdict, who established it)
    ("ph21", "CRASH-107", "c591f022f8ab", "NOT-THE-REPAIR",
     "TASK_PHP_029 §3; the pre-image is already the post-5.2.0 form"),
    ("ph73", "CRASH-052", "3d7b0bab28e7", "CANDIDATE",
     "TASK_PHP_029 §2; exact fix, regression test in-commit"),
    ("ph73", "CRASH-051", "235e6c0afe1d", "CANDIDATE",
     "TASK_PHP_029 §2; bug #30562, 5.0.3->5.0.4"),
    ("ph07", "CRASH-124", "cb3cca21b345", "INAPPLICABLE",
     "the fix is in the caller, ext/mbstring/mbstring.c"),
]


def selftest():
    idx = load_corpus_index()
    ok = True

    print("=" * 78)
    print("§4 GROUND TRUTH -- all four must reproduce, in BOTH directions")
    print("=" * 78)
    for row, cid, sha, want, who in GROUND_TRUTH:
        r = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid])
        got = r["verdict"]
        mark = "✅" if got == want else "❌"
        if got != want:
            ok = False
        print(f"{mark} {row:5} {cid:10} {sha}  expect {want:15} got {got:15}")
        print(f"     {r['why']}")
        print(f"     ({who})")
        if r["hits"]:
            print(f"     hits  : {[t.strip() for _, t in r['hits']]}")
        if r["misses"]:
            print(f"     misses: {[t.strip() for _, t in r['misses']]}")
        if r["elsewhere"]:
            print(f"     ⚠ same text in ANOTHER file of the same patch: "
                  f"{ {k: v for k, v in r['elsewhere'].items()} }")
        print()

    print("=" * 78)
    print("N0  MUST-FIRE (regression): ph73 · CRASH-100 · 5d804d163ae9")
    print("=" * 78)
    print("    NOT one of §4's four -- it is TASK_PHP_029 §2's fifth per-id block,")
    print("    which states of this commit: \"its pre-image is byte-identical to")
    print("    5.0.0\".  The FIRST version of this screen called it NOT-THE-REPAIR,")
    print("    a FALSE EXCLUSION, because the corpus cites the site as")
    print("    `ext/standard/streamsfuncs.c:728 (and 735, 742)` and the bare 735 /")
    print("    742 have no colon for the `path:N` parse to find.  735 and 742 are")
    print("    both in the pre-image.  This case guards the residual-line repair.")
    r = screen_record({"row": "ph73", "id": "CRASH-100", "sha": "5d804d163ae9"},
                      idx["CRASH-100"])
    print(f"    verdict {r['verdict']}   span {r['span']}   residual {r['residual_lines']}")
    print(f"    hits   : {[(n, t.strip()) for n, t in r['hits']]}")
    print(f"    misses : {[(n, t.strip()) for n, t in r['misses']]}")
    if r["verdict"] == "CANDIDATE" and r["residual_hits"]:
        print("    ✅ fires -- CANDIDATE, and it is the residual lines that carry it")
    else:
        print("    ❌ DID NOT FIRE -- the false exclusion is back")
        ok = False
    print()

    print("=" * 78)
    print("N1  MUST-NOT-FIRE: no constant answer passes §4")
    print("=" * 78)
    wants = [w for _, _, _, w, _ in GROUND_TRUTH]
    for const in ("CANDIDATE", "NOT-THE-REPAIR", "INAPPLICABLE"):
        n = sum(1 for w in wants if w == const)
        print(f"    a screen that always says {const:15} scores {n}/4")
    if len(set(wants)) != 3:
        print("    ❌ the ground truth does not span all three outcomes")
        ok = False
    else:
        print("    ✅ the four cases span all three outcomes, so a no-op "
              "implementation cannot pass")
    print()

    print("=" * 78)
    print("N2  MUST-FIRE: the answer is keyed on the CITED TEXT, not on a constant")
    print("=" * 78)
    # ph73/CRASH-051 is a CANDIDATE.  Re-run it against a DIFFERENT span of the
    # SAME file (the function 200 lines earlier).  If the screen still says
    # CANDIDATE, it is not reading the span at all.
    r0 = screen_record({"row": "ph73", "id": "CRASH-051", "sha": "235e6c0afe1d"},
                       idx["CRASH-051"])
    r1 = screen_record({"row": "ph73", "id": "CRASH-051", "sha": "235e6c0afe1d"},
                       idx["CRASH-051"], span_override=[(300, 340)])
    print(f"    cited span {r0['span']} -> {r0['verdict']}")
    print(f"    bogus span [[300, 340]] -> {r1['verdict']}")
    if r0["verdict"] == "CANDIDATE" and r1["verdict"] == "NOT-THE-REPAIR":
        print("    ✅ fires -- moving the span flips the verdict, so the screen "
              "reads the cited 5.0.0 text")
    else:
        print("    ❌ DID NOT FIRE -- the verdict does not depend on the span")
        ok = False
    print()

    print("=" * 78)
    print("N3  MUST-NOT-FIRE: the normaliser does not make different code equal")
    print("=" * 78)
    pairs = [("a = b + c;", "a = b - c;"),
             ("\tzval tmp;", "\tzval *tmp;"),
             ("if (x < y) {", "if (x <= y) {"),
             ("foo(a, b);", "foo(b, a);")]
    bad = [(x, y) for x, y in pairs if norm_code(x) == norm_code(y)]
    for x, y in pairs:
        print(f"    {x!r:22} vs {y!r:22} -> "
              f"{'SAME ❌' if norm_code(x) == norm_code(y) else 'different ✅'}")
    if bad:
        ok = False
        print("    ❌ FIRED: the normalisation is too aggressive")
    else:
        print("    ✅ silent")
    # and one case the normalisation DOES change, per §3.3
    a, b = "\t\tzval  tmp;\r", "    zval tmp;"
    print(f"    §3.3 example the normalisation changes: {a!r} vs {b!r}")
    print(f"        raw equal?        {a == b}")
    print(f"        norm_code equal?  {norm_code(a) == norm_code(b)}")
    if a == b or norm_code(a) != norm_code(b):
        print("    ❌ the whitespace normalisation is not load-bearing")
        ok = False
    else:
        print("    ✅ load-bearing -- tabs/CR/indent differ, code is the same")
    print()

    print("=" * 78)
    print("N4  MUST-FIRE: the pre-image really excludes `+` lines")
    print("=" * 78)
    sec = {"f.c": ["\n@@ -1,3 +1,4 @@\n ctx_alpha();\n-removed_beta();\n"
                   "+added_gamma();\n ctx_delta();\n"]}
    pre = [norm_code(x) for x in preimage_lines(sec["f.c"])]
    print(f"    pre-image = {pre}")
    if "added_gamma();" in pre:
        print("    ❌ FIRED: a `+` line leaked into the pre-image")
        ok = False
    elif "removed_beta();" in pre and "ctx_alpha();" in pre and "ctx_delta();" in pre:
        print("    ✅ silent -- context and `-` kept, `+` dropped")
    else:
        print("    ❌ FIRED: a context or `-` line was lost")
        ok = False
    print()

    print("=" * 78)
    print("N5  MUST-FIRE: the file restriction is load-bearing")
    print("=" * 78)
    moved = 0
    for row, cid, sha, want, _ in GROUND_TRUTH:
        a = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid])
        b = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid],
                          file_restrict=False)
        flag = "moves" if a["verdict"] != b["verdict"] else "same"
        moved += a["verdict"] != b["verdict"]
        print(f"    {row:5} {cid:10} restricted={a['verdict']:15} "
              f"unrestricted={b['verdict']:15} {flag}")
    if moved:
        print(f"    ✅ fires -- {moved} of 4 verdicts change when the "
              "defect-file restriction is dropped")
    else:
        print("    ❌ DID NOT FIRE: the restriction changes nothing on these 4")
        ok = False
    print()

    print("=" * 78)
    print("N6  MUST-NOT-FIRE: the verdict does not depend on the patch's LINE NUMBERS")
    print("=" * 78)
    print("    §3.1 is the trap that would produce a confident, uniformly wrong")
    print("    answer.  Behavioural test: rewrite EVERY `@@ -a,b +c,d @@` header")
    print("    in all four ground-truth patches to `@@ -1,1 +1,1 @@` and re-run.")
    moved6 = []
    for row, cid, sha, want, _ in GROUND_TRUTH:
        before = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid])
        real = _PATCH_CACHE[sha]
        try:
            _PATCH_CACHE[sha] = {
                f: [re.sub(r"@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", "@@ -1,1 +1,1 @@", s)
                    for s in secs] for f, secs in real.items()}
            after = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid])
        finally:
            _PATCH_CACHE[sha] = real
        same = before["verdict"] == after["verdict"] and before["hits"] == after["hits"]
        print(f"    {row:5} {cid:10} {before['verdict']:15} -> {after['verdict']:15}"
              f" {'unchanged' if same else 'CHANGED'}")
        if not same:
            moved6.append(cid)
    if moved6:
        print(f"    ❌ FIRED: {moved6} -- a line number is load-bearing somewhere")
        ok = False
    else:
        print("    ✅ silent -- `@@` headers are used only to ENTER a hunk")
    print()

    print("=" * 78)
    print("N7  MUST-NOT-FIRE: the pre-image parser against HUNK ARITHMETIC")
    print("=" * 78)
    print("    `@@ -a,b` DECLARES that the hunk's pre-image is exactly b lines.")
    print("    preimage_lines never reads b, so counting its output against b is")
    print("    an external check that no line is dropped or invented.")
    print("    (Full sweep over all 476 cached file sections / 1892 hunks:")
    print("     `python3 .temp/php30/audit_parser.py`.)")
    nbad = nh = 0
    for sha in ("c591f022f8ab", "3d7b0bab28e7", "235e6c0afe1d", "cb3cca21b345"):
        for path, texts in patch_sections(sha).items():
            for h in split_hunks(texts):
                m = re.match(r"^@@ -\d+(?:,(\d+))? \+", h)
                body = h.split("\n")[1:]
                while body and body[-1] == "":
                    body.pop()
                got = len(preimage_lines(["@@\n" + "\n".join(body)]))
                want = int((m.group(1) if m else None) or 1)
                nh += 1
                if got != want:
                    nbad += 1
                    print(f"    ❌ {sha} {path} declared {want} parsed {got}")
    print(f"    hunks checked {nh}, mismatches {nbad}")
    if nbad:
        ok = False
    else:
        print("    ✅ silent")
    print()

    print("=" * 78)
    print("N8  the DECISIVENESS test -- `absent from the pre-image` has TWO")
    print("    readings and only one of them is an exclusion")
    print("=" * 78)
    print("    (i)  the commit's tree no longer HAS the cited line  -> exclusion")
    print("    (ii) the hunk's ~3-line window simply never REACHES it -> nothing")
    print("    The median pre-image behind an exclusion is 14 lines, so (ii) is")
    print("    not a corner case.  `same_function` and `bracketed` separate them,")
    print("    both from TEXT: git's own `@@ ... @@ <function>` context, and")
    print("    5.0.0-unique anchor lines either side of the cited line.")
    r21 = screen_record({"row": "ph21", "id": "CRASH-107", "sha": "c591f022f8ab"},
                        idx["CRASH-107"])
    print(f"    ph21 CRASH-107 decisive={r21['decisive']} "
          f"same_function={r21['same_function']} {r21['same_function_evidence']} "
          f"bracketed={r21['bracketed']}")
    if r21["decisive"] and r21["same_function"]:
        print("    ✅ fires -- TASK_PHP_029 §3's case is the DECISIVE kind, and")
        print("       it is `same_function` that shows it, not `bracketed`")
    else:
        print("    ❌ DID NOT FIRE -- the one case known to be decisive is not")
        ok = False
    # must-NOT-fire: a synthetic hunk in a DIFFERENT function of the same file
    sstr = src_lines("ext/standard/string.c")
    fake = ["@@ -1,3 +1,3 @@ PHP_FUNCTION(nl2br)\n " + sstr[9].lstrip("\t")
            + "\n-x();\n+y();\n"]
    br, _ = bracketed(sstr, fake, [4144])
    sf, _ = same_function(sstr, fake, [4144])
    print(f"    synthetic hunk in PHP_FUNCTION(nl2br), cited line 4144 (which is")
    print(f"    in str_repeat) -> same_function={sf} bracketed={br}")
    if sf or br:
        print("    ❌ FIRED: a hunk in another function counts as reaching the site")
        ok = False
    else:
        print("    ✅ silent")
    print()

    print("=" * 78)
    print("N9  CORROBORATION -- five verdicts this programme established BY HAND,")
    print("    none of which was used to build the screen")
    print("=" * 78)
    print("    ⚠ These are NOT §4's four.  They are recorded because a screen")
    print("    validated only against the cases it was written for is validated")
    print("    against nothing.  THREE ARE MUST-NOT-EXCLUDE, which is the")
    print("    direction a NOT-THE-REPAIR screen is dangerous in.")
    corro = [
        ("ph03", "CRASH-115", "f95c1df58349", "CANDIDATE",
         "MUST-NOT-EXCLUDE. F38 half 1: TASK_PHP_013 APPLIED this patch and "
         "measured its effect over 12,600 documents. The only fix_commit in "
         "the corpus confirmed correct behaviourally."),
        ("ph29", "CRASH-097", "445daac3ab1a", "CANDIDATE",
         "MUST-NOT-EXCLUDE. F38 half 2: 'exact and minimal'."),
        ("ph16", "CRASH-098", "99e290f882c9", "CANDIDATE",
         "MUST-NOT-EXCLUDE. F38 half 2: 'the right fix, inside a 10-file "
         "27 KB change' -- also a size control."),
        ("ph12", "CRASH-108", "896a5216d73d", "NOT-THE-REPAIR",
         "F38 half 2 proved this is a LATER fix, by hand, from its pre-image."),
        ("ph22", "CRASH-014", "865739e5b196", "NOT-THE-REPAIR",
         "FIXSURVEY_001 'ph22 was the standout': settled across EIGHT TAGS; "
         "R1h is INC_OUTPUTPOS's 5.1.0 arrival, not this 2025 commit."),
    ]
    for row, cid, sha, want, why in corro:
        r = screen_record({"row": row, "id": cid, "sha": sha}, idx[cid])
        got = r["verdict"]
        mark = "✅" if got == want else "❌"
        if got != want:
            ok = False
        print(f"    {mark} {row:5} {cid:10} expect {want:15} got {got:15}"
              f" decisive={r['decisive']}")
        print(f"       {why}")
    print()

    print(f"selftest: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--row")
    ap.add_argument("--id")
    ap.add_argument("--json")
    ap.add_argument("--cell", help="MANUAL MODE: screen one sha against a "
                    "hand-supplied c_file_line-shaped citation. Use with "
                    "--sha. The citation is NOT from the corpus, so say so "
                    "wherever the answer is quoted.")
    ap.add_argument("--sha")
    ap.add_argument("--label", default="manual")
    ap.add_argument("--no-file-restrict", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    if a.cell:
        if not a.sha:
            sys.exit("--cell needs --sha")
        r = screen_record({"row": a.label, "id": "(manual)", "sha": a.sha},
                          {"c_file_line": a.cell})
        print(f"⚠ MANUAL citation, not the corpus's: {a.cell!r}")
        print(json.dumps(r, indent=1))
        return 0

    recs = load_records()
    if a.row:
        recs = [r for r in recs if r["row"] == a.row]
    if a.id:
        recs = [r for r in recs if r["id"] == a.id]
    if not recs:
        sys.exit("no records selected")
    idx = load_corpus_index()
    res = run(recs, idx, file_restrict=not a.no_file_restrict)

    from collections import Counter
    c = Counter(r["verdict"] for r in res)
    print(f"records screened: {len(res)}")
    for k in ("NOT-THE-REPAIR", "CANDIDATE", "INAPPLICABLE", "NO-SPAN",
              "NO-SHA", "NO-PATCH", "UNRESOLVED"):
        if c[k]:
            print(f"   {k:16} {c[k]}")
    print()

    print("## NOT-THE-REPAIR -- the exclusions (this is the deliverable)\n")
    for r in res:
        if r["verdict"] != "NOT-THE-REPAIR":
            continue
        print(f"### {r['row']} · {r['id']} · `{r['sha']}` · `{r['defect_file']}` "
              f"{r['span']}"
              + (f" (+residual {r['residual_lines']})" if r["residual_lines"] else ""))
        for n, t in r["misses"]:
            print(f"    5.0.0     :{n}  {t.strip()}")
            near = (r.get("nearest") or {}).get(str(n)) or []
            if near:
                print(f"    pre-image      ~  {near[0]}")
            else:
                print(f"    pre-image      ~  (nothing within 0.35 similarity)")
        if r["elsewhere"]:
            print(f"    ⚠ the same text IS in another file of this patch: "
                  f"{r['elsewhere']}")
        print(f"    dropped as structural/blank: {r['n_dropped']}")
        print(f"    DECISIVE: {r['decisive']}  "
              f"[same_function={r['same_function']} {r['same_function_evidence']}] "
              f"[bracketed={r['bracketed']} {r['bracket_evidence']}]")
        print()

    if a.verbose:
        print("## every record\n")
        for r in res:
            print(f"{r['row']:6} {r['id']:10} {r['sha'][:12]:12} "
                  f"{r['verdict']:15} {r['defect_file']}")

    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
