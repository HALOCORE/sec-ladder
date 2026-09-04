#!/usr/bin/env python3
"""build_data.py — turn the sec-ladder evidence files into the JSON this site reads.

READ-ONLY OUTSIDE `.web/`.  Every write goes through `_out()`, which refuses any
path that is not inside this directory.  Nothing in the research tree is touched,
created or deleted; `git status` must be unchanged by running this.

Inputs (all read-only):
    results/<pattern>.json          per-cell static counts, Ir, wall clock
    results/gate/<pattern>.json     the gate record: marginal Ir, Verus, adversarial,
                                    sanitizer, Miri, identity, contract, idiom
    patterns/<pattern>/{c/kernel*.c,*.rs,spec.md,README.md}

Outputs (all under `.web/data/`):
    data/index.json                 site-wide summary; one row per pattern
    data/patterns/<id>.json         everything the pattern view needs
    data/code/<id>.json             the kernel source of each rung

Usage:
    python3 .web/build_data.py            # rebuild everything
    python3 .web/build_data.py --quiet
"""
from __future__ import annotations

import datetime as _dt
import glob
import json
import os
import re
import subprocess
import sys

WEB = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(WEB)
DATA = os.path.join(WEB, "data")

# ---------------------------------------------------------------- guard rails --

def _out(*parts: str) -> str:
    """Resolve a path under `.web/` or die.  The only writer in this file."""
    p = os.path.abspath(os.path.join(WEB, *parts))
    if os.path.commonpath([p, WEB]) != WEB:
        raise SystemExit(f"refusing to write outside .web/: {p}")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _read(rel: str) -> str:
    with open(os.path.join(REPO, rel), "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _jload(rel: str):
    return json.loads(_read(rel))


def _write_json(rel: str, obj) -> int:
    path = _out(rel)
    blob = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(blob)
    return len(blob)


# ------------------------------------------------------------------- the ladder --
# Rung ids as they appear in the evidence files, mapped onto the ladder positions
# the project defines in `.memory/01-ladder.md`.

RUNGS = [
    # cell id,             rung,  label,                 compiler/notes
    ("c-gcc",              "R1",  "C (gcc)",             "c"),
    ("c-clang",            "R1",  "C (clang)",           "c"),
    ("c-gcc-h",            "R1h", "hardened C (gcc)",    "c"),
    ("c-clang-h",          "R1h", "hardened C (clang)",  "c"),
    ("safe_naive",         "R2",  "safe Rust, naive",    "rust"),
    ("safe_tuned",         "R3",  "safe Rust, tuned",    "rust"),
    ("unsafe",             "R4",  "unsafe Rust",         "rust"),
    ("verus",              "R5",  "unsafe Rust + Verus", "rust"),
    ("safe_naive_verus",   "R2v", "safe Rust + Verus",   "rust"),
]
RUNG_OF = {cell: rung for cell, rung, _l, _k in RUNGS}
LABEL_OF = {cell: lab for cell, _r, lab, _k in RUNGS}
ORDER = {cell: i for i, (cell, *_r) in enumerate(RUNGS)}

BASELINE = "unsafe"           # R4 — the "C performance, C safety" reference point

# Anything the evidence files grow that this script does not know about lands
# here, is printed, and is carried into index.json so the site can say so.  The
# gate's schema has moved under us twice; silence would have been worse.
WARNINGS: list = []

# {frozenset of unrecognised gate keys: [pattern ids]} — see the flush below.
UNKNOWN_KEYS: dict = {}

def warn(msg: str) -> None:
    if msg not in WARNINGS:
        WARNINGS.append(msg)


def asm_for(pid: str, rec: dict) -> int:
    """Publish the cached kernel assembly diffs — but only the ones that still
    match the evidence.

    `asmcache/<pid>.json` is committed, because the assembly text is not in
    `results/` and the binaries it came from are 1.7 GB of deletable scratch.
    That makes staleness the obvious hazard: a cached disassembly outlives the
    build it came from, and would otherwise sit on the page looking authoritative
    beside Ir figures it no longer corresponds to.

    So every cached side carries the `md5_fn` of the kernel symbol it was taken
    from, and `results/<pid>.json` publishes that same digest for the same cell.
    Matching digests mean the cached assembly IS the measured machine code.  A
    mismatch drops that diff and raises a warning naming what to re-run.
    """
    src = os.path.join(WEB, "asmcache", pid + ".json")
    if not os.path.exists(src):
        return 0

    with open(src, encoding="utf-8") as fh:
        cached = json.load(fh)

    published = {}
    for c in rec.get("cells", []):
        if c.get("mode") == "isolated":
            published[(c.get("cell"), c.get("opt"))] = (c.get("static") or {}).get("md5_fn")

    kept, dropped = {}, []
    for pair_id, by_opt in (cached.get("pairs") or {}).items():
        for opt, d in by_opt.items():
            ok = True
            for side in ("a", "b"):
                want = published.get((d[side]["cell"], opt))
                if want != d[side]["md5_fn"]:
                    ok = False
                    dropped.append(f"{pair_id}/{opt}/{d[side]['cell']}")
            if ok:
                kept.setdefault(pair_id, {})[opt] = d

    if dropped:
        warn(f"{pid}: {len(dropped)} cached assembly diff(s) no longer match the "
             f"kernel digests in results/ and are NOT shown ({', '.join(sorted(set(dropped))[:4])}"
             f"{'…' if len(dropped) > 4 else ''}) — rebuild with harness/build.py, "
             f"then python3 insights/asm_extract.py")

    if not kept:
        return 0
    out = dict(cached)
    out["pairs"] = kept
    return _write_json(f"data/asm/{pid}.json", out)


def run_insights() -> dict:
    """Run every insights/insight_*.py and collect what they emit.

    These carry SCRIPT-GUARDED NOTES: prose whose claims are attached to
    assertions about the evidence, emitted only while those assertions hold.  A
    script that exits non-zero is reporting that one of its notes has gone stale
    against the research tree — which is a finding, not a build failure, so it
    lands in WARNINGS and gets rendered on the Method tab rather than stopping
    the build.  Silence here would put us back to hard-coded prose that stays
    confidently wrong.
    """
    out: dict = {}
    idir = os.path.join(WEB, "insights")
    if not os.path.isdir(idir):
        return out

    for fn in sorted(f for f in os.listdir(idir) if f.startswith("insight_") and f.endswith(".py")):
        name = fn[len("insight_"):-len(".py")]
        try:
            proc = subprocess.run([sys.executable, os.path.join(idir, fn)],
                                  capture_output=True, text=True, timeout=120, cwd=WEB)
        except Exception as exc:                       # noqa: BLE001 — report, never raise
            warn(f"insights/{fn} could not be run: {exc}")
            continue
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip().replace("\n", " · ")[:400]
            warn(f"insights/{fn} reports STALE notes — a guarded claim no longer "
                 f"matches the evidence and needs rewriting: {detail}")
        path = os.path.join(WEB, "data", "insights", name + ".json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    out[name] = json.load(fh)
            except Exception as exc:                   # noqa: BLE001
                warn(f"insights/{fn} wrote unreadable JSON: {exc}")
    return out


KNOWN_GATE_KEYS = {
    "pattern", "skipped_inputs", "inputs_checked", "contract_sha256", "idiom",
    "idiom_audit", "source_sha256", "derived_contract", "identity",
    "marginal_ir_per_call", "verus", "verified_call_site", "clause_deletion",
    "requires_strength", "verified_twins", "proof_domain", "driver_loops",
    "adversarial", "sanitizer", "miri", "failures", "notes", "loud", "blocked",
    "verdict", "complete_run", "invocation", "expected_hang", "run_timeout_s",
    # The environment block the marginal `Ir` column was measured under, and
    # any glibc tunables in it.  Upstream established that an `-O3 isolated`
    # marginal is NOT invariant to it: the same binary on the same input moves
    # by a few instructions with the block's LENGTH, and by far more with its
    # CONTENT (a `GLIBC_TUNABLES` entry moved one cell by ~486 Ir/call at an
    # identical block length).  So this is what makes that column reproducible:
    # same length and same tunables => the marginal must match exactly.
    "marginal_ir_env",
    # whether the pattern's published results table is still fresh against the
    # contract hash it cites
    "published_table",
    # per-pattern control scripts' recorded output
    "controls_json",
    # TASK_097.  A run where Verus reported `0 errors` and the process still
    # exited non-zero -- i.e. the PROOF was satisfied and `rustc` was not.
    # `harness/check.py` says of it: "Empty on every healthy run -- the key
    # exists so that a run in which Verus was satisfied and rustc was not says
    # so in the record, not only in the transcript."  Rendered as a count, and
    # the count being zero is the evidence; see `proofPane` in index.js.
    "verus_exit_anomalies",
    # The same sanitizer sweep run against the HARDENED C rung — the direct
    # evidence that the safety line silences the detector the buggy rung trips.
    # Rendered beside the buggy rung's table.
    "sanitizer_hardened",
    # Gate-health keys: they say the gate's own apparatus was sound on this run
    # (build cfgs resolved, doc citations resolved, the published table
    # re-renders to its committed digest). Not evidence ABOUT the ladder, so
    # they are summarised on Method rather than given a view.
    "codegen_cfgs", "doc_citations", "table_render",
}


# --------------------------------------------------------------- classification --

def classify(g: dict) -> str:
    """One adversarial behaviour group -> what a security reviewer would call it.

    Since 2026-08 the gate records a LIST of behaviour groups per (input, rung),
    each naming the (opt, mode) cells that produced it, plus `hung` and
    `diverges`.  A rung whose groups disagree behaved differently at different
    optimisation levels — which is a finding, not noise.

    `model_*` is the independent reference implementation (`model.py`), so
    "matches the model" is the only definition of correct available here."""
    if g.get("hung"):
        return "hung"                       # never returned — the timeout fired
    if g.get("signal"):
        return "crash"                      # SIGSEGV / SIGABRT — loud, at least
    ex, mex = g.get("exit"), g.get("model_exit")
    so, mso = g.get("stdout", ""), g.get("model_stdout", "")
    diverges = g.get("diverges", (ex != mex or so != mso))
    if not diverges and ex == mex:
        return "match"                      # behaved exactly as specified
    if ex == 0 and mex == 0:
        return "silent"                     # exit 0, wrong answer, no diagnostic
    if ex not in (0, None) and mex == 0:
        return "loud"                       # refused to continue (panic / abort)
    return "other"


# worst first: an undetected wrong answer beats a hang beats a crash beats a refusal
CLASS_ORDER = ["silent", "hung", "crash", "loud", "other", "match"]


# ---------------------------------------------------------------- source slicing --

_BANNER = re.compile(r"^//\s*-+\s*(\w+)\s*-+$", re.M)


def slice_rust(text: str, keep=("spec", "TCB", "kernel", "proof", "lemma")):
    """Rust rung sources carry `// ------- kernel ----` banners.  Keep everything
    from the first kept banner up to the `driver` banner; the driver is shared
    boilerplate (`common/driver.rs`) and is identical across rungs."""
    hits = [(m.start(), m.group(1)) for m in _BANNER.finditer(text)]
    if not hits:
        return text, 1
    start = None
    for pos, name in hits:
        if name in keep:
            start = pos
            break
    if start is None:
        return text, 1
    end = len(text)
    for pos, name in hits:
        if pos > start and name == "driver":
            end = pos
            break
    # `first_line` is not decoration: the assembly line map is in FILE
    # coordinates (addr2line reads the whole file), so a pane numbered from 1
    # can never match it.  Every Rust rung is sliced — p03's unsafe.rs starts at
    # file line 54 — and clicking a Rust line silently did nothing until this
    # offset was carried through.
    return text[start:end].rstrip() + "\n", text[:start].count("\n") + 1


def rung_sources(pdir: str) -> dict:
    """The kernel source of every rung, keyed by cell id."""
    out = {}
    c_main = os.path.join(pdir, "c", "kernel.c")
    c_hard = os.path.join(pdir, "c", "kernel_hardened.c")
    if os.path.exists(c_main):
        txt = open(c_main, encoding="utf-8").read()
        for cell in ("c-gcc", "c-clang"):
            out[cell] = {"file": os.path.relpath(c_main, REPO), "lang": "c",
                         "text": txt, "first_line": 1}
    if os.path.exists(c_hard):
        txt = open(c_hard, encoding="utf-8").read()
        for cell in ("c-gcc-h", "c-clang-h"):
            out[cell] = {"file": os.path.relpath(c_hard, REPO), "lang": "c",
                         "text": txt, "first_line": 1}
    for cell, fname in (("safe_naive", "safe_naive.rs"),
                        ("safe_tuned", "safe_tuned.rs"),
                        ("unsafe", "unsafe.rs"),
                        ("verus", "verus.rs"),
                        ("safe_naive_verus", "safe_naive_verus.rs")):
        p = os.path.join(pdir, fname)
        if os.path.exists(p):
            sliced, first = slice_rust(open(p, encoding="utf-8").read())
            out[cell] = {"file": os.path.relpath(p, REPO), "lang": "rust",
                         "text": sliced, "first_line": first}
    return out


# ------------------------------------------------------------------ the builder --

def catalogue_total() -> int:
    """How many patterns the plan catalogues — one table row per `| pNN |`.
    Read rather than hard-coded, because the catalogue grows (47 -> 48 when the
    initialisation axis was added)."""
    try:
        return len(re.findall(r"(?m)^\|\s*p\d\d\s*\|", _read(".memory/06-catalogue.md")))
    except Exception:
        return 0


def layout_effect() -> dict:
    """`../common/layout/data/layout_p01.json` -> the code-layout control.

    31 builds per rung from IDENTICAL SOURCE, differing only in where the linker
    put the kernel.  Every build in a rung has the same `n_fn` and the same
    `md5_fn_norel`: same instruction stream, same executed instruction count,
    different address.  So every difference in wall clock below is layout and
    nothing else, and the sign of a rung-to-rung comparison is a property of the
    build rather than of the source.

    That claim is checked here, not assumed: `identical` is False the moment a
    rung's builds stop agreeing on their normalised machine code, and the site
    refuses to draw the chart when it is.  Returns {} if the control is absent,
    which is a warning and not a crash — it is a separate directory upstream and
    is not part of the gate."""
    path = os.path.join(REPO, "common", "layout", "data", "layout_p01.json")
    if not os.path.exists(path):
        warn("common/layout/data/layout_p01.json is missing — the layout-effect "
             "chart is omitted (finding 9 stays prose-only)")
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        warn(f"layout control unreadable: {exc}")
        return {}

    # key is "<rung>|<knob>|<i>"; a knob is what was varied to move the kernel
    builds: dict = {}
    knobs: dict = {}
    for key, rec in raw.items():
        try:
            rung, knob, i = key.split("|")
        except ValueError:
            continue
        builds.setdefault(rung, {})[(knob, int(i))] = rec
        knobs[knob] = knobs.get(knob, 0) + 1

    rungs, identical = {}, True
    for rung, recs in sorted(builds.items()):
        md5s = {r.get("md5_fn_norel") for r in recs.values()}
        nfns = {r.get("n_fn") for r in recs.values()}
        same = len(md5s) == 1 and len(nfns) == 1
        identical = identical and same
        rungs[rung] = {"builds": len(recs), "n_fn": sorted(nfns)[0] if len(nfns) == 1 else None,
                       "md5_fn_norel": sorted(md5s)[0] if len(md5s) == 1 else None,
                       "identical": same,
                       "addresses": len({r.get("addr") for r in recs.values()})}

    # the inputs the control timed; `#p1c3` is the same input on a pinned core
    inputs = sorted({k for r in builds.values() for rec in r.values() for k in rec
                     if k in ("small", "large")})

    spread, pairs = [], []
    for inp in inputs:
        for rung, recs in sorted(builds.items()):
            ts = [r[inp] for r in recs.values() if isinstance(r.get(inp), (int, float))]
            if len(ts) > 1:
                spread.append({"input": inp, "rung": rung, "n": len(ts),
                               "min": min(ts), "max": max(ts),
                               "pct": 100.0 * (max(ts) - min(ts)) / min(ts)})
        # every rung-to-rung comparison, once per layout, against unsafe Rust —
        # the same baseline the cost view uses
        for a, b in (("safe_naive", "unsafe"), ("safe_tuned", "unsafe"),
                     ("safe_naive", "safe_tuned")):
            if a not in builds or b not in builds:
                continue
            ds = []
            for k in builds[a]:
                ra, rb = builds[a].get(k), builds[b].get(k)
                if not ra or not rb:
                    continue
                if isinstance(ra.get(inp), (int, float)) and rb.get(inp):
                    ds.append(100.0 * (ra[inp] - rb[inp]) / rb[inp])
            if len(ds) > 1:
                pairs.append({"input": inp, "a": a, "b": b, "n": len(ds),
                              "min": min(ds), "max": max(ds),
                              "neg": sum(1 for x in ds if x < 0),
                              "pos": sum(1 for x in ds if x > 0),
                              "values": [round(x, 4) for x in sorted(ds)]})

    return {"pattern": "p01-array-sum", "identical": identical, "rungs": rungs,
            "knobs": knobs, "inputs": inputs, "spread": spread, "pairs": pairs,
            "flips": sum(1 for p in pairs if p["neg"] and p["pos"]),
            "source": "common/layout/data/layout_p01.json"}


# ------------------------------------------------------------------- paper --
# `paper_vers/ver_X/` -> `data/paper/ver_X.json`.  The build resolves the
# `\input` tree, then VALIDATES: every `\num` path must resolve to a scalar in
# the index we just built, every `\ref` must have a `\label`, every `\cite` a
# bibliography entry, every `\figure` an id the renderer knows.  A paper that
# quotes a number the data no longer has is exactly the failure this whole
# project keeps having, so it is a build error and not a warning.

FIGURE_IDS = {"ladder", "spread", "outcomes", "tcb", "rungcost", "identity"}
_RE_INPUT = re.compile(r"^\s*\\input\{([^}]+)\}\s*$", re.M)
_RE_NUM = re.compile(r"\\num\{([^}]+)\}")
_RE_LABEL = re.compile(r"\\label\{([^}]+)\}")
_RE_REF = re.compile(r"\\ref\{([^}]+)\}")
_RE_CITE = re.compile(r"\\cite\{([^}]+)\}")
_RE_FIG = re.compile(r"\\figure\{([^}]+)\}")
_RE_TODO = re.compile(r"\\todo\{")
_RE_PRINCIPLE = re.compile(r"\\begin\{principle\}")
_RE_EXAMPLE = re.compile(r"\\begin\{example\}")


def _paper_resolve(root: str, rel: str, seen: list, errs: list) -> str:
    """Splice the `\\input` tree into one string, depth-first, in reading order."""
    if rel in seen:
        errs.append(f"\\input cycle: {' -> '.join(seen + [rel])}")
        return ""
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        errs.append(f"\\input{{{rel}}} does not exist")
        return ""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    out, pos = [], 0
    for m in _RE_INPUT.finditer(text):
        out.append(text[pos:m.start()])
        # a marker comment so the renderer and any error can name the real file
        out.append(f"\n%%FILE {m.group(1)}\n")
        out.append(_paper_resolve(root, m.group(1), seen + [rel], errs))
        out.append(f"\n%%FILE {rel}\n")
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


def _dotted(obj, path: str):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
                continue
            except (ValueError, IndexError):
                return None, f"index `{part}` is not valid here"
        if not isinstance(cur, dict) or part not in cur:
            return None, f"no key `{part}`"
        cur = cur[part]
    return cur, None


def build_paper(index: dict, quiet: bool) -> dict:
    root_dir = os.path.join(WEB, "paper_vers")
    if not os.path.isdir(root_dir):
        return {}
    vers = sorted(d for d in os.listdir(root_dir)
                  if d.startswith("ver_") and os.path.isdir(os.path.join(root_dir, d)))
    out = {}
    for v in vers:
        vdir = os.path.join(root_dir, v)
        errs: list = []
        try:
            with open(os.path.join(vdir, "meta.json"), encoding="utf-8") as fh:
                meta = json.load(fh)
        except Exception as exc:                                # noqa: BLE001
            warn(f"paper {v}: meta.json unreadable ({exc}) — version skipped")
            continue
        body = _paper_resolve(vdir, "paper.md", [], errs)

        refs = {}
        rpath = os.path.join(vdir, "refs.json")
        if os.path.exists(rpath):
            try:
                with open(rpath, encoding="utf-8") as fh:
                    refs = json.load(fh)
            except Exception as exc:                            # noqa: BLE001
                errs.append(f"refs.json unreadable: {exc}")

        # ⚠ VALIDATE THE RENDERED TEXT, NOT THE SOURCE.  `paper.js` drops every
        # `%%` line before it parses anything, so a marker inside a comment never
        # reaches a reader — and validating it means the build can fail on prose
        # that does not exist.  That is not hypothetical: a writer explaining in a
        # comment why a `\figure{}` was removed hit exactly this, and only the id
        # pattern's own greediness saved the build.  Strip comments first, and
        # collect `\label` from the same stripped text so a label that is only
        # commented out cannot satisfy a live `\ref`.
        #
        # `%%literal-ok` is read from the RAW body below, on purpose: it is a
        # directive addressed to this checker rather than content, so it has to
        # survive the strip that hides everything else in a comment.
        visible = re.sub(r"(?m)^\s*%%.*$", "", body)

        # every \num must resolve to a scalar in the index built this run
        nums = {}
        for raw in set(_RE_NUM.findall(visible)):
            path = raw.split("|")[0].strip()
            val, why = _dotted(index, path)
            if why:
                errs.append(f"\\num{{{path}}}: {why} in data/index.json")
            elif isinstance(val, (dict, list)):
                errs.append(f"\\num{{{path}}} resolves to a {type(val).__name__}, not a number")
            else:
                nums[path] = val

        labels = set(_RE_LABEL.findall(visible))
        for r in set(_RE_REF.findall(visible)):
            if r not in labels:
                errs.append(f"\\ref{{{r}}} has no \\label")
        for c in set(_RE_CITE.findall(visible)):
            if c not in refs:
                errs.append(f"\\cite{{{c}}} is not in refs.json")
        for f in set(_RE_FIG.findall(visible)):
            if f not in FIGURE_IDS:
                errs.append(f"\\figure{{{f}}} is not a figure the renderer knows "
                            f"(known: {', '.join(sorted(FIGURE_IDS))})")

        # ⚠ The build already fails on a `\num{}` path that does not resolve.
        # That catches a number written WRONG; it does not catch a number
        # written as a LITERAL, which is the failure this project actually keeps
        # having — "13 patterns", "47 catalogued", each true when typed and
        # false within days. So: if a corpus total appears in the prose as a
        # bare figure, say so. A warning and not an error, because a literal is
        # sometimes right (a historical figure, a quoted retraction, a number
        # that is a coincidence), and only a human can tell which.
        prose = re.sub(r"\\num\{[^}]*\}", " ", body)         # what \num already owns
        prose = re.sub(r"(?m)^\s*%%.*$", " ", prose)         # source comments
        # Check against EVERY scalar total, not only the paths this paper
        # already uses — otherwise a figure that is a literal everywhere and a
        # `\num{}` nowhere is invisible to the check, which is the worst case.
        every = {}

        def _flatten(obj, prefix):
            for k, val in (obj or {}).items():
                p = f"{prefix}.{k}" if prefix else k
                if isinstance(val, dict):
                    _flatten(val, p)
                elif isinstance(val, (int, float)) and not isinstance(val, bool):
                    every[p] = val
        _flatten(index.get("totals"), "totals")

        # A coincidence is acknowledged in the source, where it is reviewable:
        #   %%literal-ok 230  p27's whole-program difference, not the TCB line count
        # A warning that fires forever on a known false positive is a warning
        # that gets ignored, and then the real one is ignored with it.
        ok_literals = set(re.findall(r"(?m)^\s*%%literal-ok\s+([\d,]+)", body))
        ok_literals = {s.replace(",", "") for s in ok_literals}

        literals = []
        for path, val in sorted(every.items()):
            if not isinstance(val, int) or val < 100 or str(val) in ok_literals:
                continue                                     # 0/1/26 are everywhere and mean everything
            for form in {f"{val:,}", str(val)}:
                if re.search(r"(?<![\d,.])" + re.escape(form) + r"(?![\d,.])", prose):
                    literals.append(f"{form} (= {path})")
                    break
        if literals:
            warn(f"paper {v}: corpus figure(s) written as a literal where "
                 f"\\num{{}} would keep them live: {', '.join(sorted(set(literals))[:6])}"
                 + ("…" if len(set(literals)) > 6 else "")
                 + " — check each; a literal is right only if the number is meant to be frozen")

        # ⚠⚠ AND SAY WHAT IS BEING SUPPRESSED, because the escape hatch turned
        # into a silencer.  A draft printed "126 required-but-absent spellings"
        # with `%%literal-ok 126` beside it.  The real value had moved to 175,
        # and the literal-ok was suppressing THE ONE WARNING THAT WOULD HAVE
        # CAUGHT IT — a number frozen on purpose and a number frozen by mistake
        # look identical from here, so the only defence is to keep the list
        # visible and short enough to re-read.
        if ok_literals:
            warn(f"paper {v}: {len(ok_literals)} figure(s) are frozen by %%literal-ok "
                 f"({', '.join(sorted(ok_literals, key=lambda s: int(s)))}) — each is a "
                 f"number that will NEVER update. Re-read them when the corpus moves; "
                 f"a literal-ok also hides the staleness warning for that value")

        # PROSE words: the ones a reader reads.  Source comments are excluded
        # because they are not rendered, and this file's own comments are heavy —
        # ver_C's sections carry more comment than prose, and counting them made
        # the Paper tab report a 7,600-word paper as 17,700.  A report whose
        # thesis is that numbers get credited to the wrong thing should not
        # publish a word count that means something other than it says.
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*",
                               re.sub(r"\\[a-z]+\{[^}]*\}", " ", visible)))
        stats = {"words": words, "todos": len(_RE_TODO.findall(body)),
                 "principles": len(_RE_PRINCIPLE.findall(body)),
                 "examples": len(_RE_EXAMPLE.findall(body)),
                 "sections": len(re.findall(r"\\section\{", body))}
        rec = {"id": v, "meta": meta, "body": body, "refs": refs,
               "nums": nums, "stats": stats, "errors": errs}
        n = _write_json(f"data/paper/{v}.json", rec)
        out[v] = {"id": v, "meta": meta, "stats": stats, "errors": len(errs), "bytes": n}
        if errs:
            warn(f"paper {v}: {len(errs)} source error(s) — " + "; ".join(errs[:3])
                 + ("…" if len(errs) > 3 else ""))
        if not quiet:
            print(f"  paper {v:14s} {stats['words']:6d} words · {stats['sections']} sections · "
                  f"{stats['principles']} principles · {stats['examples']} examples · "
                  f"{stats['todos']} todo · {len(errs)} error(s)")
    return out


def licence_table() -> dict:
    """`results/synthesis.md` §2 -> may this rung-to-rung difference be taken?

    THIS IS THE MOST IMPORTANT HONESTY FEATURE ON THE COST VIEW, and the site
    drew those differences for a long time without it.

    The published `Ir` column is KERNEL-EXCLUSIVE: it counts instructions inside
    the kernel symbol and nothing the kernel calls out to.  Two cells may only
    be subtracted when they dispatch the SAME work outside that symbol —
    otherwise the difference is a difference of two different programs, and the
    research says so in a `licence` column with five tags:

        LICENSED   the two cells' live outward call multisets are equal
        NOT-LIC    they are not, and the difference is KNOWN TO BE WRONG
        UNDEC      both sides dispatch through an unresolvable pointer
        NO-KSYM    a cell has no kernel symbol (inlined away)
        NOT-BUILT  the binary is absent — a tooling state

    ⚠ These verdicts are PARSED, not recomputed.  `synthesis/licence.py` derives
    them from disassembly pinned to each gate record's `source_sha256`, and
    re-implementing that rule here would risk publishing a verdict the research
    does not hold.  If the table's shape changes, this returns {} and warns
    rather than guessing — a missing licence must never read as a granted one.
    """
    try:
        txt = _read("results/synthesis.md")
    except OSError:
        warn("results/synthesis.md is missing — cost differences render with no "
             "licence column, so the page cannot say which of them the research "
             "permits. Treat every difference as unverified until it is back.")
        return {}

    out: dict = {}
    # each `### \`PAIR\`` section runs to the next heading of any level
    for m in re.finditer(r"(?m)^### `([A-Za-z0-9_-]+)`.*?$", txt):
        pair = m.group(1)
        nxt = re.search(r"(?m)^#{2,3} ", txt[m.end():])
        body = txt[m.end(): m.end() + (nxt.start() if nxt else len(txt))]
        hm = re.search(r"(?m)^\|\s*pattern\s*\|.*$", body)
        if not hm:
            continue
        cols = [c.strip().lower() for c in hm.group(0).strip().strip("|").split("|")]
        if "licence" not in cols:
            continue
        li = cols.index("licence")
        rows = {}
        for rm in re.finditer(r"(?m)^\|\s*(p\d\d-[a-z0-9-]+)\s*\|(.*)$", body):
            cells = [c.strip() for c in (rm.group(1) + "|" + rm.group(2)).strip().strip("|").split("|")]
            if len(cells) > li and cells[li]:
                rows[rm.group(1)] = cells[li]
        if rows:
            out[pair] = rows
        # The same table's LAST column is the R3/R4 spelling search state — how
        # hard each side of this comparison was searched for a cheaper spelling.
        # It is the qualification that decides whether a bar means anything, and
        # the page used to carry it as a hand-typed "on four patterns".
        if "r3/r4 search state" in cols:
            si = cols.index("r3/r4 search state")
            srows = {}
            for rm in re.finditer(r"(?m)^\|\s*(p\d\d-[a-z0-9-]+)\s*\|(.*)$", body):
                cells = [c.strip() for c in (rm.group(1) + "|" + rm.group(2)).strip().strip("|").split("|")]
                if len(cells) > si and cells[si]:
                    srows[rm.group(1)] = cells[si]
            if srows:
                out.setdefault("_search", {}).update(srows)

    if not out:
        warn("could not read the licence column out of results/synthesis.md — the "
             "cost view cannot mark which differences the research permits. The "
             "table's shape has changed; fix licence_table() before trusting the "
             "cost tab, and do not read a missing licence as a granted one.")
    return out


# `synthesis/licence.py`'s own two filters, copied verbatim so the verdict this
# file computes is the verdict that file would compute.
_NORETURN = re.compile(
    r"panic|slice_index_fail|slice_end_index|slice_start_index|len_mismatch"
    r"|unwrap_failed|expect_failed|assert_failed|handle_alloc_error"
    r"|rust_begin_unwind|__stack_chk_fail|(?<![A-Za-z_])abort(?![A-Za-z0-9_])"
    r"|_Unwind_Resume|core.*9panicking")
_KERNEL_SIBLING = re.compile(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])")


def licence_c_hardening() -> dict:
    """C -> hardened C: may THAT difference be taken?  Computed here, and the
    reason is disclosed on the page.

    ⚠ The research publishes licence verdicts for four rung pairs and `R1->R1h`
    is NOT one of them — so unlike `licence_table()`, this one is DERIVED here
    by applying `synthesis/licence.py`'s own rule to `synthesis/licence.json`:
    two cells may be differenced when their LIVE outward call multisets are
    equal, where diverging callees (panic pads, `__stack_chk_fail`) and kernel
    siblings are excluded because neither is work the kernel column misses.

    This matters because the hardened-C chart is the site's cleanest comparison
    — same source, same compiler, one check added — and it was the only one with
    no licence check on it.  Measured: p47's C rung calls `memcmp` and its
    hardened rung inlines the comparison, so the largest bar on that chart is a
    libc call leaving the kernel symbol rather than the price of a check.
    """
    path = os.path.join(REPO, "synthesis", "licence.json")
    if not os.path.exists(path):
        warn("synthesis/licence.json is missing — the C-vs-hardened-C chart "
             "cannot be licence-checked, and its rows render as unverified")
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        warn(f"synthesis/licence.json unreadable: {exc}")
        return {}

    def live(cell):
        out = [s for s in (cell.get("outward") or [])
               if not _KERNEL_SIBLING.search(s.split("  [")[0])]
        return sorted(s for s in out if not _NORETURN.search(s))

    out: dict = {}
    for pat, rec in raw.items():
        cells = rec.get("cells") or {}
        for plain, hard in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            a, b = cells.get(plain), cells.get(hard)
            if not a or not b:
                continue
            if a.get("error") or b.get("error"):
                out.setdefault(pat, {})[hard] = {"tag": "NO-KSYM", "why": "a cell has no kernel symbol"}
                continue
            ia, ib = a.get("unresolved_indirect") or [], b.get("unresolved_indirect") or []
            if len(ia) != len(ib):
                out.setdefault(pat, {})[hard] = {"tag": "NOT-LIC", "why": "asymmetric indirect dispatch"}
                continue
            if ia:
                out.setdefault(pat, {})[hard] = {"tag": "UNDEC", "why": "both sides dispatch through an unresolvable pointer"}
                continue
            la, lb = live(a), live(b)
            if la == lb:
                out.setdefault(pat, {})[hard] = {"tag": "LICENSED", "why": ""}
            else:
                only_a = sorted(set(x for x in la if la.count(x) > lb.count(x)))
                only_b = sorted(set(x for x in lb if lb.count(x) > la.count(x)))
                bits = []
                if only_a:
                    bits.append("only the unfixed rung calls " + ", ".join(s.split("@")[0] for s in only_a))
                if only_b:
                    bits.append("only the fixed rung calls " + ", ".join(s.split("@")[0] for s in only_b))
                out.setdefault(pat, {})[hard] = {"tag": "NOT-LIC", "why": "; ".join(bits)}
    return out


def git_head() -> dict:
    try:
        out = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H%x00%h%x00%cI%x00%s"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            full, short, when, subject = out.stdout.strip().split("\0")
            return {"commit": full, "short": short, "date": when, "subject": subject}
    except Exception:
        pass
    return {}


def build_pattern(pid: str, quiet: bool) -> dict:
    res = _jload(f"results/{pid}.json")
    gate = _jload(f"results/gate/{pid}.json")

    new_keys = set(gate) - KNOWN_GATE_KEYS
    if new_keys:
        # Aggregated rather than one per pattern: a schema change upstream lands
        # in every gate record at once, and 24 identical lines bury the warning
        # they are trying to raise.  UNKNOWN_KEYS is flushed to one warning per
        # distinct key set at the end of the build.
        UNKNOWN_KEYS.setdefault(tuple(sorted(new_keys)), []).append(pid)
    unknown_cells = {c["cell"] for c in res.get("cells", [])} - set(RUNG_OF)
    if unknown_cells:
        warn(f"{pid}: rung(s) not on the ladder and therefore NOT DRAWN: "
             f"{sorted(unknown_cells)} — add them to RUNGS in build_data.py")
    pdir = os.path.join(REPO, "patterns", pid)

    # calls per input — from the proof-domain stage, which counts real kernel
    # invocations.  Needed to turn a total Ir into an Ir-per-call.
    calls = {k: v.get("calls", 0) for k, v in gate.get("proof_domain", {}).items()}

    cells = {}
    for c in res["cells"]:
        key = f"{c['cell']}/{c['opt']}/{c['mode']}"
        st = c.get("static") or {}
        ir = {}
        for inp, rec in (c.get("ir") or {}).items():
            k = rec.get("kernel_exclusive_ir")
            n = calls.get(inp) or 0
            ir[inp] = {
                "kernel": k,
                "kernel_per_call": (k / n) if (k and n) else None,
                "main": rec.get("main_exclusive_ir"),
            }
        wall = {}
        for inp, rec in (c.get("wall") or {}).items():
            wall[inp] = {"min_ms": rec["min_s"] * 1e3, "median_ms": rec["median_s"] * 1e3,
                         "spread_pct": rec.get("spread_pct"), "reps": rec.get("reps")}
        cells[key] = {
            "cell": c["cell"], "rung": RUNG_OF.get(c["cell"], "?"), "opt": c["opt"],
            "mode": c["mode"], "status": c.get("status"),
            "n_fn": st.get("n_fn"), "n_fn_nopad": st.get("n_fn_nopad"),
            "fn_bytes": st.get("fn_bytes"), "md5_fn": (st.get("md5_fn") or "")[:8],
            "md5_fn_full": st.get("md5_fn"),
            "pad_insns": st.get("pad_insns"),
            "has_loop": st.get("has_loop"), "vector_regs": st.get("vector_regs") or [],
            "bulk_calls": st.get("bulk_calls") or [],
            "text_bytes": c.get("binary_text_bytes"),
            "checksum": c.get("checksum") or {},
            "ir": ir, "wall": wall,
        }

    # adversarial matrix: input -> cell -> {worst outcome, one entry per behaviour}
    adv = {}
    for k, rec in gate.get("adversarial", {}).items():
        inp, cell = k.rsplit("/", 1)
        groups = rec if isinstance(rec, list) else [rec]     # pre-2026-08 shape
        out = []
        for g in groups:
            out.append({
                "class": classify(g),
                "cells": g.get("cells") or [],
                "exit": g.get("exit"), "signal": g.get("signal"),
                "hung": bool(g.get("hung")), "diverges": bool(g.get("diverges")),
                "stdout": (g.get("stdout") or "")[:120],
                "model_stdout": (g.get("model_stdout") or "")[:120],
                "model_exit": g.get("model_exit"),
                "stderr": (g.get("stderr") or "")[:200],
            })
        classes = [o["class"] for o in out]
        worst = min(classes, key=lambda c: CLASS_ORDER.index(c))
        adv.setdefault(inp, {})[cell] = {
            "class": worst,
            "build_dependent": len(set(classes)) > 1,
            "runs": sum(len(o["cells"]) or 1 for o in out),
            "groups": out,
        }

    verus = gate.get("verus", {})
    tcb = []
    for src, rec in verus.items():
        for it in rec.get("tcb_items", []):
            tcb.append({"source": src, **it})
    twins = []
    for src, rec in (gate.get("verified_twins") or {}).items():
        for t in rec.get("twins", []):
            vp = t.get("vacuity_probe") or {}
            twins.append({"source": src, "trusted": t.get("trusted"), "twin": t.get("twin"),
                          "requires": t.get("requires", []), "ensures": t.get("ensures", []),
                          "body_lines": t.get("body_lines"),
                          "load_bearing": vp.get("load_bearing"), "conjuncts": vp.get("conjuncts")})

    inputs = {}
    for name, rec in (res.get("inputs") or {}).items():
        inputs[name] = {**rec, "calls": calls.get(name)}

    detail = {
        "id": pid,
        "generated_utc": res.get("generated_utc"),
        "git": res.get("git", {}),
        "toolchain": res.get("toolchain", {}),
        "host": res.get("host", {}),
        "protocol": res.get("protocol", {}),
        "timing_cpu": res.get("timing_cpu"),
        "verdict": gate.get("verdict"),
        "complete_run": gate.get("complete_run"),
        "blocked": gate.get("blocked", []),
        "gate_notes": gate.get("notes", []),
        "expected_hang": gate.get("expected_hang", []),
        "run_timeout_s": gate.get("run_timeout_s", {}),
        "loud": gate.get("loud", []),
        "failures": gate.get("failures", []),
        "contract_sha256": gate.get("contract_sha256"),
        "derived_contract": gate.get("derived_contract", {}),
        "idiom": gate.get("idiom", {}),
        "idiom_audit": gate.get("idiom_audit", {}),
        "inputs": inputs,
        "cells": cells,
        "marginal": gate.get("marginal_ir_per_call", {}),
        "identity": gate.get("identity", []),
        "verus": {
            "sources": {s: {"verified": r.get("verified"), "errors": r.get("errors"),
                            "pinned": r.get("pinned"),
                            "axiom_decls": r.get("axiom_decls") or []} for s, r in verus.items()},
            "tcb": tcb, "twins": twins,
            "call_site": gate.get("verified_call_site", {}),
            "clause_deletion": gate.get("clause_deletion", {}),
            "requires_strength": gate.get("requires_strength", {}),
            "proof_domain": gate.get("proof_domain", {}),
            # a list, empty on a healthy run — see KNOWN_GATE_KEYS
            "exit_anomalies": gate.get("verus_exit_anomalies") or [],
        },
        "adversarial": adv,
        "sanitizer": gate.get("sanitizer", {}),
        # the same sweep on the HARDENED rung: does the fix silence it?
        "sanitizer_hardened": gate.get("sanitizer_hardened", {}),
        "miri": gate.get("miri", {}),
        "driver_loops": gate.get("driver_loops", {}),
        "source_sha256": gate.get("source_sha256", {}),
        "marginal_ir_env": gate.get("marginal_ir_env", {}),
        "published_table": gate.get("published_table", {}),
    }

    n = _write_json(f"data/patterns/{pid}.json", detail)
    src = rung_sources(pdir)
    ns = _write_json(f"data/code/{pid}.json", src)

    # the pattern's own prose, copied verbatim so the site can show the evidence
    # a claim rests on without anybody having to open the repo
    docs = {}
    for key, fname in (("readme", "README.md"), ("spec", "spec.md"), ("notes", "NOTES.md")):
        p = os.path.join(pdir, fname)
        if os.path.exists(p):
            docs[key] = {"file": os.path.relpath(p, REPO),
                         "text": open(p, encoding="utf-8", errors="replace").read()}
    _write_json(f"data/docs/{pid}.json", docs)
    na = asm_for(pid, res)
    if not quiet:
        print(f"  {pid:20s} detail {n/1024:6.1f} KB   code {ns/1024:5.1f} KB   "
              f"{'asm ' + format(na / 1024, '5.1f') + ' KB' if na else 'asm      —'}   "
              f"{gate.get('verdict')}")

    # ---- the summary row the index carries -----------------------------------
    def marg(cell, opt, mode, inp):
        return detail["marginal"].get(f"{cell}/{opt}/{mode}/{inp}")

    tax = {}
    for mode in ("isolated", "whole"):
        for inp in ("small.bin", "large.bin"):
            base = marg(BASELINE, "O3", mode, inp)
            if base is None:
                continue
            row = {}
            for cell, *_ in RUNGS:
                v = marg(cell, "O3", mode, inp)
                if v is not None:
                    row[cell] = {"ir": v, "delta": v - base, "ratio": v / base if base else None}
            tax[f"{mode}/{inp}"] = {"base": base, "cells": row}

    # the other Ir column: instructions inside the kernel symbol, per call.
    # Only meaningful in `isolated` builds — at `whole` the kernel is inlined
    # away and has no symbol of its own.
    kern = {}
    for inp in ("small.bin", "large.bin"):
        base_cell = cells.get(f"{BASELINE}/O3/isolated")
        base = ((base_cell or {}).get("ir", {}).get(inp) or {}).get("kernel_per_call")
        if base is None:
            continue
        row = {}
        for cell, *_ in RUNGS:
            c = cells.get(f"{cell}/O3/isolated")
            v = ((c or {}).get("ir", {}).get(inp) or {}).get("kernel_per_call")
            if v is not None:
                row[cell] = {"ir": v, "delta": v - base, "ratio": v / base if base else None}
        kern[f"isolated/{inp}"] = {"base": base, "cells": row}

    adv_counts, adv_pairs, adv_runs, build_dep = {}, 0, 0, 0
    for inp, per in adv.items():
        for cell, rec in per.items():
            adv_pairs += 1
            adv_runs += rec["runs"]
            build_dep += 1 if rec["build_dependent"] else 0
            for g in rec["groups"]:                       # weight by builds run
                n = len(g["cells"]) or 1
                adv_counts[g["class"]] = adv_counts.get(g["class"], 0) + n
    worst_by_cell, split_cells = {}, {}
    for inp, per in adv.items():
        for cell, rec in per.items():
            cur = worst_by_cell.get(cell)
            if cur is None or CLASS_ORDER.index(rec["class"]) < CLASS_ORDER.index(cur):
                worst_by_cell[cell] = rec["class"]
            if rec["build_dependent"]:
                split_cells[cell] = True

    # ------------------------------------------- what the PLAIN C rungs did --
    # A ROW is one (pattern, adversarial input) pair judged on the two rungs
    # that carry the bug.  ⚠ The silent/crash split depends on an AGGREGATION
    # RULE, because a row spans two compilers and four builds and some rows are
    # silent in one build and crash in another.  Both rules are counted here and
    # both are published: quoting one without naming the rule is quoting a
    # number you do not understand.  They differ by exactly `build_split`.
    PLAIN_C = ("c-gcc", "c-clang")
    pc = {"rows": 0, "clean": 0, "silent_first": 0, "loud_first_silent": 0,
          "crash_silent_first": 0, "crash_loud_first": 0, "hung": 0, "build_split": 0}
    for inp, per in adv.items():
        # ⚠ Read the per-BUILD groups, not the rung's summary class. The summary
        # is already a worst-of, so it hides exactly the rows this is trying to
        # count: the ones that are silent in one build and crash in another.
        seen = {g["class"] for c, rec in per.items() if c in PLAIN_C
                for g in rec["groups"]}
        if not seen:
            continue
        pc["rows"] += 1
        if seen <= {"match"}:
            pc["clean"] += 1
            continue
        if "silent" in seen and ({"crash", "hung"} & seen):
            pc["build_split"] += 1
        if "hung" in seen:                                 # a hang outranks both
            pc["hung"] += 1
        elif "silent" in seen:                             # rule A: silent wins
            pc["silent_first"] += 1
        else:
            pc["crash_silent_first"] += 1
        if "hung" in seen:
            pass                                           # already counted
        elif "crash" in seen:                              # rule B: loud wins
            pc["crash_loud_first"] += 1
        else:
            pc["loud_first_silent"] += 1

    ident_o3 = next((i for i in detail["identity"] if i.get("opt") == "O3"), None)
    san_fired = sum(1 for v in detail["sanitizer"].values() if v.get("fired"))
    miri = detail["miri"]

    return {
        "id": pid,
        "verdict": detail["verdict"],
        "complete_run": detail["complete_run"],
        "failures": len(detail["failures"]),
        "blocked": len(detail["blocked"]),
        "generated_utc": detail["generated_utc"],
        "git": detail["git"].get("commit", "")[:12],
        "inputs": sorted(inputs.keys()),
        "n_adversarial_inputs": len(adv),
        "cells_built": len(cells),
        "tax": tax,
        "kern": kern,
        "plain_c": pc,
        "adversarial": {"counts": adv_counts, "worst_by_cell": worst_by_cell,
                        "split_cells": split_cells,
                        "pairs": adv_pairs, "runs": adv_runs, "build_dependent": build_dep,
                        "expected_hang": len(detail["expected_hang"])},
        "sanitizer_fired": san_fired,
        "sanitizer_hardened": {
            "cells": len(detail["sanitizer_hardened"]),
            "fired": sum(1 for v in detail["sanitizer_hardened"].values() if v.get("fired")),
        },
        "sanitizer_rows": len(detail["sanitizer"]),
        "miri": {"ran": miri.get("ran"), "required": miri.get("required"),
                 "runs": len(miri.get("runs", [])),
                 "ub": sum(1 for r in miri.get("runs", []) if r.get("ub"))},
        "verus": {
            # ⚠ THE SHIPPED RUNG IS `verus.rs`.  p01 also carries a SECOND
            # verified file, `safe_naive_verus.rs` — the R2v control, which
            # exists to demonstrate a NEGATIVE result (proving the safe rung
            # panic-free changes nothing in the binary).  Summing over every
            # verified source folds that control into the corpus's proof burden
            # and puts these totals 7 obligations / 2 trusted items / 5 trusted
            # lines above the figures the project itself publishes.  So the
            # headline counts the shipped rungs and the control is reported
            # separately, by name.
            "verified": sum(r.get("verified") or 0 for s, r in verus.items() if s == "verus.rs"),
            "errors": sum(r.get("errors") or 0 for r in verus.values()),
            "tcb_items": len([i for i in tcb if i.get("source") == "verus.rs"]),
            "tcb_lines": sum(i.get("body_lines") or 0 for i in tcb if i.get("source") == "verus.rs"),
            "control_sources": sorted(s for s in verus if s != "verus.rs"),
            "control_verified": sum(r.get("verified") or 0 for s, r in verus.items() if s != "verus.rs"),
            "control_tcb_items": len([i for i in tcb if i.get("source") != "verus.rs"]),
            "twins": len(twins),
            "axiom_decls": sum(len(r.get("axiom_decls") or []) for r in verus.values()),
            "exit_anomalies": len(detail["verus"]["exit_anomalies"]),
        },
        "identity_o3": {
            "level": ident_o3.get("level") if ident_o3 else None,
            "equal": (ident_o3.get("md5_fn_a") == ident_o3.get("md5_fn_b")) if ident_o3 else None,
            "n_fn": (ident_o3.get("counts_a") or [None])[0] if ident_o3 else None,
        },
        "idiom_audit": {k: detail["idiom_audit"].get(k) for k in
                        ("spellings", "pairs", "present", "forbidden_spellings",
                         "forbidden_hits", "required_absent",
                         # the two buckets that say what the audit did NOT check:
                         # an entry written as prose with no backticked spelling
                         # is not mechanically checked at all, and one that pins
                         # nothing is a defect in the ruler rather than the code
                         "forbidden_unaudited_entries", "required_pins_nothing")},
    }


def main() -> int:
    quiet = "--quiet" in sys.argv
    gates = sorted(f for f in glob.glob(os.path.join(REPO, "results", "gate", "*.json"))
                   if ".partial." not in f)
    pids = [os.path.basename(f)[:-5] for f in gates]
    have = [p for p in pids if os.path.exists(os.path.join(REPO, "results", f"{p}.json"))]
    for p in set(pids) - set(have):
        warn(f"{p}: has a gate record but no results/{p}.json — not shown yet")
    pids = have
    if not quiet:
        print(f"sec-ladder → .web/data   ({len(pids)} patterns)")

    rows = [build_pattern(pid, quiet) for pid in pids]
    ref = _jload(f"results/{pids[0]}.json")

    totals = {
        "patterns": len(rows),
        "catalogue": catalogue_total(),
        "adversarial_pairs": sum(r["adversarial"]["pairs"] for r in rows),
        "build_dependent": sum(r["adversarial"]["build_dependent"] for r in rows),
        "axiom_decls": sum(r["verus"]["axiom_decls"] for r in rows),
        "cells": sum(r["cells_built"] for r in rows),
        "verus_verified": sum(r["verus"]["verified"] for r in rows),
        # the R2v control's obligations, counted apart from the shipped rungs
        "verus_verified_controls": sum(r["verus"].get("control_verified", 0) for r in rows),
        "tcb_items_controls": sum(r["verus"].get("control_tcb_items", 0) for r in rows),
        "verus_errors": sum(r["verus"]["errors"] for r in rows),
        "verus_exit_anomalies": sum(r["verus"]["exit_anomalies"] for r in rows),
        "tcb_items": sum(r["verus"]["tcb_items"] for r in rows),
        "tcb_lines": sum(r["verus"]["tcb_lines"] for r in rows),
        "identity_exact": sum(1 for r in rows if r["identity_o3"]["equal"]),
        "adversarial_runs": sum(r["adversarial"]["runs"] for r in rows),
        "silent": sum(r["adversarial"]["counts"].get("silent", 0) for r in rows),
        "crash": sum(r["adversarial"]["counts"].get("crash", 0) for r in rows),
        "loud": sum(r["adversarial"]["counts"].get("loud", 0) for r in rows),
        "hung": sum(r["adversarial"]["counts"].get("hung", 0) for r in rows),
        "match": sum(r["adversarial"]["counts"].get("match", 0) for r in rows),
        "miri_ub": sum(r["miri"]["ub"] for r in rows),
        "miri_runs": sum(r["miri"]["runs"] for r in rows),
        # the idiom contract, corpus-wide: what was pinned, what was checked and
        # — the part worth publishing — what was NOT checked
        "idiom": {k: sum(r["idiom_audit"].get(k) or 0 for r in rows) for k in
                  ("spellings", "pairs", "present", "forbidden_spellings",
                   "forbidden_hits", "required_absent",
                   "forbidden_unaudited_entries", "required_pins_nothing")},
    }
    # Figures the paper had frozen as prose because nothing derived them.  Each
    # is a one-second computation over evidence already in hand, and each is the
    # kind of number this project has watched go stale.
    san_expect_fires = san_fired = san_expect_clean = san_clean = 0
    pd_inputs = pd_calls = pd_ok = 0
    for r in rows:
        det_p = json.loads(open(_out(f"data/patterns/{r['id']}.json"), encoding="utf-8").read())
        for rec in (det_p.get("sanitizer") or {}).values():
            if rec.get("expect") == "fires":
                san_expect_fires += 1
                san_fired += 1 if rec.get("fired") else 0
            elif rec.get("expect") == "clean":
                san_expect_clean += 1
                san_clean += 0 if rec.get("fired") else 1
        for rec in ((det_p.get("verus") or {}).get("proof_domain") or {}).values():
            pd_inputs += 1
            pd_calls += rec.get("calls") or 0
            pd_ok += 1 if rec.get("requires_ok") is True else 0
    totals["sanitizer_hardened"] = {
        "cells": sum(r["sanitizer_hardened"]["cells"] for r in rows),
        "fired": sum(r["sanitizer_hardened"]["fired"] for r in rows),
    }
    totals["sanitizer"] = {"declared_fires": san_expect_fires, "fired": san_fired,
                           "declared_clean": san_expect_clean, "clean": san_clean}
    totals["proof_domain"] = {"inputs": pd_inputs, "calls": pd_calls, "requires_ok": pd_ok}

    # How much text a proof costs, in the unit a reader can budget in.  Counted
    # here rather than quoted, because it is the figure a verification decision
    # actually turns on and nothing upstream publishes it.
    u_lines = v_lines = 0
    ratios = []
    for r in rows:
        pdir = os.path.join(REPO, "patterns", r["id"])
        try:
            nu = sum(1 for _ in open(os.path.join(pdir, "unsafe.rs"), encoding="utf-8"))
            nv = sum(1 for _ in open(os.path.join(pdir, "verus.rs"), encoding="utf-8"))
        except OSError:
            continue
        u_lines += nu
        v_lines += nv
        if nu:
            ratios.append(nv / nu)
    if ratios:
        ratios.sort()
        mid = len(ratios) // 2
        totals["proof_text"] = {
            "unsafe_lines": u_lines, "verus_lines": v_lines,
            "ratio_pct": round(100.0 * v_lines / u_lines) if u_lines else 0,
            "median_pct": round(100.0 * (ratios[mid] if len(ratios) % 2
                                         else (ratios[mid - 1] + ratios[mid]) / 2)),
            "min_pct": round(100.0 * ratios[0]), "max_pct": round(100.0 * ratios[-1]),
        }

    # The paper's headline security figure, aggregated from the per-pattern
    # counts above so it cannot become a frozen string in prose.
    PC_KEYS = ("rows", "clean", "silent_first", "loud_first_silent",
               "crash_silent_first", "crash_loud_first", "hung", "build_split")
    totals["plain_c"] = {k: sum(r["plain_c"][k] for r in rows) for k in PC_KEYS}
    totals["plain_c"]["deviating"] = totals["plain_c"]["rows"] - totals["plain_c"]["clean"]

    # A pattern whose gate did not pass is still SHOWN — hiding it would be the
    # wrong correction — but its numbers are pooled into every total on this
    # site, so the fact has to travel with them.  `PASS-WITH-BLOCKED-ROWS` is a
    # pass: p01 has one real 180 s Miri timeout and is otherwise complete.
    notpass = [{"id": r["id"], "verdict": r["verdict"], "failures": r["failures"]}
               for r in rows if not str(r.get("verdict", "")).startswith("PASS")]
    totals["patterns_passing"] = len(rows) - len(notpass)
    totals["patterns_not_passing"] = notpass
    if notpass:
        warn("gate did not pass on " + ", ".join(f"{n['id']} ({n['verdict']}, "
             f"{n['failures']} failure(s))" for n in notpass)
             # ⚠ no `*` in this string: it is rendered as prose on the Method tab,
             # which does not run md(), so a bare asterisk fails check.mjs as an
             # italic marker that lost its pair. Write the namespace without it.
             + " — shown, but its numbers are inside every corpus total on this"
               " site. A PAPER MUST RESOLVE AGAINST the totals.passing namespace"
               " INSTEAD, and any literal it froze from the project's own analysis"
               " (licensed rows, bucket counts, bug-class splits) was derived"
               " BEFORE this pattern and is now stale against the unscoped"
               " totals — re-derive them together or not at all")

    # ── the paper's evidence base, which is NOT the same set as the site's ──
    #
    # Every total above pools a non-passing pattern in with the rest, on purpose
    # (see the note above): hiding it would be the wrong correction for a status
    # page.  But a REPORT may not draw a conclusion from a program whose gate
    # says FAIL, and this is not hypothetical — a 27th pattern landed mid-session
    # with verdict FAIL and no entry in the research synthesis, and it silently
    # moved `totals.patterns` 26 -> 27 underneath sentences reading "25 of the
    # 26".  `\num{}` kept every figure live and still made the prose wrong,
    # because what changed was the DENOMINATOR'S MEANING, not the number.
    #
    # So the paper resolves against `totals.passing.*`, which is the same
    # arithmetic over gate-passing patterns only.  If nothing is failing, these
    # equal their unscoped twins.
    # ── how many kernels the RESEARCH's own analysis covers ──
    #
    # The corpus and the analysis are not the same set and they move apart.
    # `results/SYNTHESIS.md` states its own denominator in prose — "drawn from N
    # kernels" — and everything a paper freezes from that analysis (the licensed
    # rows, the buckets, the 7.26x median, the bug-class split) is against THAT
    # N, not against however many patterns exist today.
    #
    # This is not hypothetical.  A 27th pattern arrived failing, then passed a
    # session later, taking `passing.patterns` 26 -> 27 while the analysis it is
    # quoted beside still covered 26.  The earlier guard only fired while the
    # pattern was FAILING, so the day it passed the warning went silent and the
    # prose went wrong quietly.  Parse the denominator instead of trusting one.
    n_analysed = None
    try:
        with open(os.path.join(REPO, "results", "SYNTHESIS.md"), encoding="utf-8") as fh:
            m = re.search(r"drawn from \*{0,2}(\d+)\*{0,2}\s+kernels", fh.read())
            if m:
                n_analysed = int(m.group(1))
    except OSError:
        pass

    pas = [r for r in rows if str(r.get("verdict", "")).startswith("PASS")]
    p_ratios, p_u, p_v = [], 0, 0
    for r in pas:
        pdir = os.path.join(REPO, "patterns", r["id"])
        try:
            nu = sum(1 for _ in open(os.path.join(pdir, "unsafe.rs"), encoding="utf-8"))
            nv = sum(1 for _ in open(os.path.join(pdir, "verus.rs"), encoding="utf-8"))
        except OSError:
            continue
        p_u += nu
        p_v += nv
        if nu:
            p_ratios.append(nv / nu)
    p_ratios.sort()
    pmid = len(p_ratios) // 2
    totals["passing"] = {
        "patterns": len(pas),
        "cells": sum(r["cells_built"] for r in pas),
        "adversarial_runs": sum(r["adversarial"]["runs"] for r in pas),
        "identity_exact": sum(1 for r in pas if r["identity_o3"]["equal"]),
        "verus_verified": sum(r["verus"]["verified"] for r in pas),
        "verus_errors": sum(r["verus"]["errors"] for r in pas),
        "tcb_items": sum(r["verus"]["tcb_items"] for r in pas),
        "tcb_lines": sum(r["verus"]["tcb_lines"] for r in pas),
        "miri_runs": sum(r["miri"]["runs"] for r in pas),
        "loud": sum(r["adversarial"]["counts"].get("loud", 0) for r in pas),
        # crash/hung were missing here, and their absence forced a paper to
        # freeze "109 end in a signal and eight hang" as literals — an unscoped
        # total cannot sit inside a sentence whose subject is a passing-only
        # count, because the two diverge the moment a gate goes red.
        "crash": sum(r["adversarial"]["counts"].get("crash", 0) for r in pas),
        "hung": sum(r["adversarial"]["counts"].get("hung", 0) for r in pas),
        "proof_text_ratio_pct": round(100.0 * p_v / p_u) if p_u else 0,
        "proof_text_median_pct": round(100.0 * (p_ratios[pmid] if len(p_ratios) % 2
                                                else (p_ratios[pmid - 1] + p_ratios[pmid]) / 2))
                                 if p_ratios else 0,
        # the denominator a paper must use for anything it quotes OUT of the
        # research synthesis, as opposed to counts it derives itself
        "analysed": n_analysed if n_analysed else len(pas),
    }
    if n_analysed and n_analysed != len(pas):
        warn(f"the synthesis DERIVED its results from {n_analysed} kernels and the corpus "
             f"now has {len(pas)}; the synthesis re-derived every result against all "
             f"{len(pas)} and reports the out-of-sample verdicts itself. So this is a "
             f"PROVENANCE fact, not a staleness one — but any figure quoted out of that "
             f"analysis (licensed rows, buckets, medians, bug-class splits) still carries "
             f"the {n_analysed} denominator. Use totals.passing.analysed for those, and "
             f"never let a derived count stand next to a quoted one without saying which "
             f"is which. Rendered on the page by `provenanceNote()`.")

    # how many rungs never deviated from the model on any adversarial input
    clean_cells, dirty_cells = set(), set()
    for r in rows:
        for cell, cls in r["adversarial"]["worst_by_cell"].items():
            (clean_cells if cls == "match" else dirty_cells).add((r["id"], cell))
    totals["cells_clean_on_adversarial"] = len(clean_cells)
    totals["cells_deviating"] = len(dirty_cells)

    # one line per distinct schema change, not one per pattern
    for keys, pids in sorted(UNKNOWN_KEYS.items()):
        where = (f"all {len(pids)} patterns" if len(pids) == len(rows)
                 else f"{len(pids)} pattern(s): {', '.join(pids[:4])}"
                       + ("…" if len(pids) > 4 else ""))
        warn(f"gate records grew key(s) this site does not render: {list(keys)} "
             f"— on {where}. The evidence format has moved; decide whether it belongs on the page.")

    insights = run_insights()
    lic = licence_table()
    lic_ch = licence_c_hardening()
    # Count what the page will have to disclose, and say it at build time too.
    if lic:
        bad = {p: sum(1 for v in rws.values() if v != "LICENSED")
               for p, rws in lic.items()}
        tot = sum(bad.values())
        if tot:
            warn("cost differences NOT licensed for subtraction: "
                 + ", ".join(f"{p} {n}/{len(lic[p])}" for p, n in sorted(bad.items()) if n)
                 + " — the two cells dispatch different work outside the kernel symbol, "
                   "so the difference is between two different programs. Rendered per row "
                   "on the Cost tab; do not quote an unlicensed row as a safety tax.")

    index = {
        "built_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head": git_head(),
        "toolchain": ref.get("toolchain", {}),
        "host": ref.get("host", {}),
        "protocol": ref.get("protocol", {}),
        "rungs": [{"cell": c, "rung": r, "label": l, "lang": k} for c, r, l, k in RUNGS],
        "warnings": WARNINGS,
        "insights": insights,
        "licence": lic,
        "licence_c": lic_ch,
        "layout": layout_effect(),
        "patterns": rows,
        "totals": totals,
    }
    # the paper is built AFTER the index, because every `\num` in it is checked
    # against the index this run produced
    index["paper"] = build_paper(index, quiet)
    n = _write_json("data/index.json", index)
    # …and the same object as a plain script, so the page has its summary data at
    # parse time: no loading flash, and a screenshot of any tab is deterministic.
    with open(_out("data/index.boot.js"), "w", encoding="utf-8") as fh:
        fh.write("window.SLB_INDEX = " + json.dumps(index, separators=(",", ":"), ensure_ascii=False) + ";\n")
    if not quiet:
        print(f"  {'index.json':20s}        {n/1024:6.1f} KB")
        for w in WARNINGS:
            print(f"  ! {w}")
        print(f"  totals: {totals['cells']} cells · {totals['adversarial_runs']} adversarial runs · "
              f"{totals['silent']} silent · {totals['verus_verified']} obligations verified, "
              f"{totals['verus_errors']} errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
