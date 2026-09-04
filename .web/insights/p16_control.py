#!/usr/bin/env python3
"""p16_control.py — rebuild p16's four-rung "deleted check" table from committed source.

    python3 insights/p16_control.py            # rebuild everything, write insights/p16control.json
    python3 insights/p16_control.py --print    # print the committed table; runs nothing
    python3 insights/p16_control.py --check    # re-run and diff against the committed JSON
    python3 insights/p16_control.py --no-verus # skip the two Verus runs (they are the slow half)
    python3 insights/p16_control.py --keep     # leave the built binaries in .temp/p16ctl/

WHY THIS EXISTS.

The report's most quotable artefact is a four-rung table for `p16-tlv-walk`: the
same missing bounds test, deleted at four rungs of the ladder, producing four
different failures.  Only the first row was evidenced by anything committed.
`c/kernel.c` IS the pattern's designed bug — it ships without the check and the
gate certifies it — so that row is reproducible by definition.  The other three
rows were produced from mutant sources that lived in the parent's gitignored
`.temp/`, with no generator and no surviving run log: one `rm -rf` from being
unevidenced.

So this script derives the mutants, builds them, runs them, and commits the
outcome.  It is the p16 twin of `asm_extract.py`: extract from scratch that gets
deleted, commit the result, and record alongside it the digest that lets a later
run notice the input moved.

WHAT IT REFUSES TO DO.

It does not carry a copy of a mutant.  A checked-in mutant source is a claim
about a shipped file that nothing re-checks, and the failure mode is silent: the
shipped kernel is edited, the mutant is not, and the table goes on describing a
program that no longer stands in any relation to the rung it is named after.
The deletion is therefore performed here, by pattern match, against the file the
pattern ships — and if the shipped source has changed shape so that the match is
not exactly one hit, this refuses to produce anything at all.  A generator that
silently emits a wrong mutant is worse than no generator.

It does not retype a compiler flag.  `harness/build.py` is imported and asked for
the argv it would have used; the only edit made to that argv is the output path
and, for a mutant, the source path.  Flags typed here would be a second build
pipeline, which is the thing `asm_extract.py`'s header records going wrong.

It does not run `verus_run.py`, for one narrow reason: that script puts its
scratch dir under the PARENT repo's `.temp/`, and this directory may not write
outside `.web/`.  Its two load-bearing behaviours — locating the Verus binary,
and putting the Verus dir plus `~/.cargo/bin` on PATH so Verus can find its
pinned rustc — are replicated below and marked, with the cwd moved into
`.web/.temp/p16ctl/`.

WHAT THE TABLE IS ALLOWED TO SAY.

Nothing here interprets.  The JSON records exit status, stdout, stderr and the
Verus verdict, plus every input digest that produced them.  The reading — that
these are four failure MODES and not four bugs — is prose, and prose lives in
`content.js`.
"""

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)
PID = "p16-tlv-walk"
PDIR = os.path.join(REPO, "patterns", PID)
INPUTS = os.path.join(PDIR, "inputs")
WORK = os.path.join(WEB, ".temp", "p16ctl")
OUT = os.path.join(HERE, "p16control.json")

# Importing a module from the parent tree would drop a `.pyc` into
# `../harness/__pycache__/`, which is a write outside `.web/` — gitignored, but
# still a write, and `.web/CLAUDE.md` rule 1 does not carve out gitignored
# files.  Bytecode writing is off for the duration of the import and restored
# after it.
sys.path.insert(0, os.path.join(REPO, "harness"))
_dwb = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    import build as harness_build  # noqa: E402  — the repo's only build pipeline
finally:
    sys.dont_write_bytecode = _dwb

# The band the report quotes.  O3/isolated is the cell every published p16
# number is taken at, so the mutants are built there and nowhere else: a mutant
# at a band the report does not show would be a number with no twin.
OPT, MODE, PANIC = "O3", "isolated", "unwind"

# The five committed inputs that are not the `sweep-k*` band.  Named rather than
# globbed: the sweep band is 90 near-identical blobs for a marginal-cost fit and
# has nothing to say about a deleted check, and a glob would silently grow this
# table the next time somebody adds one.
INPUT_NAMES = [
    "small.bin",
    "large.bin",
    "adversarial-trunc.bin",
    "adversarial-stride2.bin",
    "adversarial-overrun.bin",
]

# Shipped sources this reads.  Every one is digested into the JSON.
SHIPPED = {
    "c-gcc": "c/kernel.c",
    "c-clang": "c/kernel.c",
    "c-gcc-h": "c/kernel_hardened.c",
    "c-clang-h": "c/kernel_hardened.c",
    "safe_naive": "safe_naive.rs",
    "safe_tuned": "safe_tuned.rs",
    "unsafe": "unsafe.rs",
    "verus": "verus.rs",
}

# The Rust rungs a mutant is derived from.  `c/kernel.c` is NOT here: that rung
# already ships without the check.
MUTATED = ["safe_naive", "safe_tuned", "unsafe", "verus"]

# The four rows of the published table, in ladder order.  `c-gcc` is the shipped
# R1 rung and carries no mutation; the other three are mutants.
TABLE = ["c-gcc", "nocheck-safe_naive", "nocheck-unsafe", "nocheck-verus"]
# Every rung, in ladder order, for the full matrix `--print` shows underneath.
ROW_ORDER = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
             "safe_naive", "safe_tuned", "unsafe", "verus",
             "nocheck-safe_naive", "nocheck-safe_tuned", "nocheck-unsafe",
             "nocheck-verus"]

RUN_TIMEOUT = 300
VERUS_TIMEOUT = 1800
STREAM_LIMIT = 4000
# Lines that must survive truncation whatever else does: the panic line IS the
# row.  `index out of bounds: the len is N but the index is N` is the entire
# difference between the R2 row and the R4 row.
KEY_LINE = re.compile(
    r"panicked at|out of bounds|overflow|assertion|Aborted|Segmentation|"
    r"error(\[|:)|verification results|not satisfied|not supported"
)

# The one deletion.  Anchored to the start of a line and to the whole three-line
# form, so a partial match cannot pass: `if vlen > end - (p + 3)` alone appears
# in prose in more than one of these files, and matching it would produce a
# mutant with a dangling `break`.
CHECK_RE = re.compile(
    r"^([ \t]*)if vlen > end - \(p \+ 3\) \{\n"
    r"[ \t]*break;\n"
    r"[ \t]*\}\n",
    re.MULTILINE,
)
# `mod driver;` is pulled in by a path relative to the SOURCE FILE, and a mutant
# does not live where the shipped file lives.  Re-anchored to an absolute path,
# once, explicitly, and recorded in the JSON — a mutant that silently failed to
# find the driver would fail to build, but one that found a DIFFERENT driver
# would not, and that is the failure worth naming.
PATH_RE = re.compile(r'^#\[path = "\.\./\.\./common/(driver\.rs)"\]$', re.MULTILINE)


# ------------------------------------------------------------------ helpers ---

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# Run-to-run noise that is not a result.  Kept to a named list, because a
# blanket "normalise the numbers" would erase `the len is 3072 but the index is
# 3072`, which IS the R2 row.  Rust's panic header carries the OS thread id
# since 1.87 (`thread 'main' (2434212) panicked at ...`), so a --check would
# otherwise report drift on every single run.
NOISE = [
    (re.compile(r"(thread '[^']*') \(\d+\) panicked"), r"\1 (<tid>) panicked"),
]


def scrub(s):
    """Absolute paths and run-to-run noise out, so the JSON is diffable."""
    if not s:
        return s
    for real, tag in ((WORK, "<work>"), (WEB, "<web>"), (REPO, "<repo>"),
                      (os.path.expanduser("~"), "<home>")):
        s = s.replace(real, tag)
    for pat, rep in NOISE:
        s = pat.sub(rep, s)
    return s


def clip(s):
    """Truncate a stream, but never lose a line that carries the verdict."""
    s = scrub(s or "")
    if len(s) <= STREAM_LIMIT:
        return s, False, []
    keep = [ln for ln in s.splitlines() if KEY_LINE.search(ln)]
    head = s[: STREAM_LIMIT // 2]
    tail = s[-(STREAM_LIMIT // 4):]
    return (f"{head}\n...[{len(s) - STREAM_LIMIT} chars elided]...\n{tail}",
            True, keep)


def stream(s):
    text, truncated, keep = clip(s)
    d = {"text": text}
    if truncated:
        d["truncated"] = True
        d["key_lines"] = keep
    return d


def sig_name(rc):
    if rc is None or rc >= 0:
        return None
    try:
        return signal.Signals(-rc).name
    except ValueError:
        return f"SIG{-rc}"


def capture_argv(fn, *args):
    """Ask harness/build.py for the argv it would run, without running it.

    `build.run` is the single choke point every builder in that module goes
    through, so replacing it for the duration yields the exact command line the
    harness would have used — flags, include paths, source order and all.  This
    is the whole reason no flag is typed in this file.
    """
    box = {}
    orig = harness_build.run

    def spy(cmd, dry):
        box["cmd"] = list(cmd)
        return 0, "", ""

    harness_build.run = spy
    try:
        fn(*args)
    finally:
        harness_build.run = orig
    if "cmd" not in box:
        raise SystemExit("p16_control: harness/build.py did not reach run(); "
                         "its internals have changed and this must be re-read")
    return box["cmd"]


# ------------------------------------------------------------------ mutants ---

def derive_mutant(rung):
    """Delete the bounds test from a shipped rung. Fails loudly, never quietly."""
    src = os.path.join(PDIR, SHIPPED[rung])
    text = open(src, encoding="utf-8").read()

    hits = list(CHECK_RE.finditer(text))
    if len(hits) != 1:
        raise SystemExit(
            f"p16_control: {SHIPPED[rung]} contains {len(hits)} occurrences of the "
            f"bounds test, expected exactly 1.\n"
            f"  The shipped source has changed shape and this deletion no longer "
            f"applies.  Re-read the kernel and update CHECK_RE — do NOT relax it.")
    m = hits[0]
    deleted = m.group(0)
    line = text[: m.start()].count("\n") + 1
    mutant = text[: m.start()] + text[m.end():]

    paths = list(PATH_RE.finditer(mutant))
    if len(paths) != 1:
        raise SystemExit(
            f"p16_control: {SHIPPED[rung]} has {len(paths)} relative `#[path]` "
            f"driver anchors, expected exactly 1.  A mutant built outside "
            f"patterns/ would resolve it to the wrong file.")
    abs_driver = os.path.join(REPO, "common", "driver.rs")
    mutant = PATH_RE.sub(lambda _m: f'#[path = "{abs_driver}"]', mutant)

    return mutant, {
        "from": SHIPPED[rung],
        "from_sha256": sha256_file(src),
        "deleted_at_line": line,
        "deleted_lines": deleted.count("\n"),
        "deleted_text": deleted,
        "reanchored": {
            "why": "the mutant is built outside patterns/, so the driver "
                   "module's source-relative #[path] would resolve elsewhere",
            "from": '#[path = "../../common/driver.rs"]',
            "to": f'#[path = "{scrub(abs_driver)}"]',
            "count": 1,
        },
        "sha256": sha256_text(mutant),
    }


# ------------------------------------------------------------------- builds ---

def bin_path(rung):
    return os.path.join(WORK, "bin", f"{rung}-{OPT}-{MODE}")


def build_argv(rung, mutant_src=None):
    """The harness's own argv, re-pointed at our output (and our source)."""
    out = bin_path(rung)
    base = rung[len("nocheck-"):] if rung.startswith("nocheck-") else rung
    if base.startswith("c-"):
        cc = harness_build.GCC if base.startswith("c-gcc") else harness_build.CLANG
        ksrc = "kernel_hardened.c" if base.endswith("-h") else "kernel.c"
        argv = capture_argv(harness_build.build_c, PDIR, cc, OPT, MODE, PANIC,
                            out, False, ksrc)
    elif base == "verus":
        argv = capture_argv(harness_build.build_verus, PDIR, base, OPT, MODE,
                            PANIC, out, False)
    else:
        argv = capture_argv(harness_build.build_rust, PDIR, base, OPT, MODE,
                            PANIC, out, False)
    if mutant_src is not None:
        shipped = os.path.join(PDIR, harness_build.RUST_SRC[base])
        if shipped not in argv:
            raise SystemExit(f"p16_control: {shipped} not in the harness argv for "
                             f"{rung}; cannot substitute the mutant")
        argv = [mutant_src if a == shipped else a for a in argv]
    return argv, out


def verus_env_and_bin():
    """verus_run.py's two load-bearing behaviours, replicated.

    Not imported and not shelled out to, because `verus_run.py` puts its scratch
    dir under the PARENT repo's `.temp/` and this directory may not write there.
    Everything else about the invocation is that script's.
    """
    cands = [os.environ.get("VERUS_BIN"),
             os.path.join(os.environ.get("VERUS_HOME", ""), "verus")
             if os.environ.get("VERUS_HOME") else None,
             os.path.expanduser("~/tools/verus/verus")]
    verus = next((c for c in cands if c and os.path.isfile(c)
                  and os.access(c, os.X_OK)), None) or shutil.which("verus")
    if not verus:
        return None, None
    verus = os.path.abspath(verus)
    env = dict(os.environ)
    cargo_bin = os.path.expanduser("~/.cargo/bin")
    parts = [os.path.dirname(verus)] + ([cargo_bin] if os.path.isdir(cargo_bin) else [])
    env["PATH"] = os.pathsep.join(parts + [env.get("PATH", "")])
    return verus, env


def run_verus(rung, mutant_src=None):
    """Verify (and compile) one Verus rung. Returns a result dict."""
    verus, env = verus_env_and_bin()
    if not verus:
        return {"skipped": True,
                "why": "no Verus install found (tried $VERUS_BIN, $VERUS_HOME/verus, "
                       "~/tools/verus/verus, PATH) — see TOOLCHAIN.md"}
    argv, out = build_argv(rung, mutant_src)
    # build_verus wraps the call in `verus_run.py`; drop the wrapper and keep
    # every flag it would have forwarded.
    if argv[:2] != [sys.executable, harness_build.VERUS_RUN]:
        raise SystemExit("p16_control: harness build_verus no longer shells out to "
                         "verus_run.py; re-read it before trusting this")
    argv = [verus] + argv[2:]

    scratch = os.path.join(WORK, "verus-scratch", rung)
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch, exist_ok=True)
    try:
        r = subprocess.run(argv, cwd=scratch, env=env, capture_output=True,
                           text=True, timeout=VERUS_TIMEOUT)
        rc, so, se = r.returncode, r.stdout, r.stderr
        timed_out = False
    except subprocess.TimeoutExpired as e:
        rc, timed_out = None, True
        so = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    blob = (so or "") + (se or "")
    m = re.search(r"(\d+) verified, (\d+) error", blob)
    return {
        "argv": [scrub(a) for a in argv],
        "rc": rc,
        "timed_out": timed_out,
        "verified": int(m.group(1)) if m else None,
        "errors": int(m.group(2)) if m else None,
        "diagnostics": sorted({scrub(ln.strip()) for ln in blob.splitlines()
                               if KEY_LINE.search(ln)}),
        "stdout": stream(so),
        "stderr": stream(se),
        "binary_built": os.path.exists(out),
    }


def build_one(rung, mutant_src=None):
    argv, out = build_argv(rung, mutant_src)
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(argv, cwd=WORK, capture_output=True, text=True, timeout=900)
    ok = r.returncode == 0 and os.path.exists(out)
    return {
        "argv": [scrub(a) for a in argv],
        "rc": r.returncode,
        "ok": ok,
        "log": scrub(((r.stdout or "") + (r.stderr or "")).strip())[:STREAM_LIMIT],
    }, out


# --------------------------------------------------------------------- runs ---

def run_inputs(rung, exe):
    rows = {}
    for name in INPUT_NAMES:
        path = os.path.join(INPUTS, name)
        try:
            r = subprocess.run([exe, path], capture_output=True, text=True,
                               timeout=RUN_TIMEOUT)
            rc, so, se, to = r.returncode, r.stdout, r.stderr, False
        except subprocess.TimeoutExpired:
            rc, so, se, to = None, "", "", True
        rows[name] = {
            "rc": rc,
            "signal": sig_name(rc),
            "timed_out": to,
            "stdout": stream(so),
            "stderr": stream(se),
        }
    return rows


# -------------------------------------------------------------------- build ---

def generate(do_verus=True):
    os.makedirs(os.path.join(WORK, "src"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "bin"), exist_ok=True)

    sources, seen = {}, set()
    for rel in SHIPPED.values():
        if rel in seen:
            continue
        seen.add(rel)
        p = os.path.join(PDIR, rel)
        sources[rel] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    sources["common/driver.rs"] = {
        "sha256": sha256_file(os.path.join(REPO, "common", "driver.rs")),
        "bytes": os.path.getsize(os.path.join(REPO, "common", "driver.rs"))}
    sources["common/driver.c"] = {
        "sha256": sha256_file(os.path.join(REPO, "common", "driver.c")),
        "bytes": os.path.getsize(os.path.join(REPO, "common", "driver.c"))}
    sources["harness/build.py"] = {
        "sha256": sha256_file(os.path.join(REPO, "harness", "build.py")),
        "bytes": os.path.getsize(os.path.join(REPO, "harness", "build.py"))}

    inputs = {n: {"sha256": sha256_file(os.path.join(INPUTS, n)),
                  "bytes": os.path.getsize(os.path.join(INPUTS, n))}
              for n in INPUT_NAMES}

    # --- mutants -----------------------------------------------------------
    mutants, mutant_src = {}, {}
    for rung in MUTATED:
        text, meta = derive_mutant(rung)
        dest = os.path.join(WORK, "src", f"nocheck-{harness_build.RUST_SRC[rung]}")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(text)
        meta["path"] = scrub(dest)
        mutants["nocheck-" + rung] = meta
        mutant_src["nocheck-" + rung] = dest

    # --- builds and runs ---------------------------------------------------
    builds, runs = {}, {}
    exec_rungs = ([r for r in SHIPPED if r != "verus"] +
                  [f"nocheck-{r}" for r in MUTATED if r != "verus"])
    for rung in exec_rungs:
        print(f"  build {rung} ...", end="", flush=True)
        rec, exe = build_one(rung, mutant_src.get(rung))
        builds[rung] = rec
        print(" ok" if rec["ok"] else f" FAILED rc={rec['rc']}")
        if rec["ok"]:
            print(f"  run   {rung} ...", end="", flush=True)
            runs[rung] = run_inputs(rung, exe)
            print(" done")

    # --- verus -------------------------------------------------------------
    verus = {}
    if do_verus:
        for rung, src in (("verus", None), ("nocheck-verus", mutant_src["nocheck-verus"])):
            print(f"  verus {rung} ... (slow)", end="", flush=True)
            verus[rung] = run_verus(rung, src)
            v, e = verus[rung].get("verified"), verus[rung].get("errors")
            print(f" rc={verus[rung].get('rc')} {v} verified, {e} errors")
            exe = bin_path(rung)
            if verus[rung].get("binary_built") and os.path.exists(exe):
                builds[rung] = {"argv": verus[rung]["argv"], "rc": verus[rung]["rc"],
                                "ok": True, "log": ""}
                print(f"  run   {rung} ...", end="", flush=True)
                runs[rung] = run_inputs(rung, exe)
                print(" done")
    else:
        verus = {"skipped": True, "why": "--no-verus"}

    # --- flags, quoted from the harness rather than typed -------------------
    flags = {
        "source": "harness/build.py c_flags()/rust_flags() at "
                  f"opt={OPT} mode={MODE} panic={PANIC}",
        "c": harness_build.c_flags(OPT, MODE, PANIC),
        "rust": harness_build.rust_flags(OPT, MODE, PANIC),
        "cc_gcc": scrub(harness_build.GCC),
        "cc_clang": scrub(harness_build.CLANG),
        "rustc": scrub(harness_build.RUSTC),
    }

    return {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pattern": PID,
        "opt": OPT, "mode": MODE, "panic": PANIC,
        "table": TABLE,
        "flags": flags,
        "sources": sources,
        "inputs": inputs,
        "mutants": mutants,
        "builds": builds,
        "runs": runs,
        "verus": verus,
        "caveat": "the plain-C and unsafe-Rust rows are UNDEFINED BEHAVIOUR by "
                  "construction; their exit status and output are what this box "
                  "produced, not what the language guarantees. A --check drift on "
                  "those two rows is a report about the machine, not a broken "
                  "generator. The other rows are defined behaviour and a drift "
                  "there is real.",
    }


# ------------------------------------------------------------------- report ---

def volatile_free(obj):
    """Everything a re-run may legitimately change, removed."""
    if isinstance(obj, dict):
        return {k: volatile_free(v) for k, v in obj.items()
                if k not in ("generated_utc",)}
    if isinstance(obj, list):
        return [volatile_free(v) for v in obj]
    return obj


def diff(a, b, path=""):
    out = []
    if type(a) is not type(b):
        return [f"{path}: type {type(a).__name__} -> {type(b).__name__}"]
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}/{k}: ADDED")
            elif k not in b:
                out.append(f"{path}/{k}: REMOVED")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} -> {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += diff(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: {a!r} -> {b!r}")
    return out


def first_line(s):
    return (s or "").strip().splitlines()[0] if (s or "").strip() else ""


def print_table(data):
    print(f"p16 deleted-check table — {data['pattern']} {data['opt']}/{data['mode']}")
    print(f"generated {data['generated_utc']}")
    print()
    key = "adversarial-overrun.bin"
    print(f"  the attack input: {key}  "
          f"sha256 {data['inputs'][key]['sha256'][:12]}")
    print()
    hdr = f"  {'rung':22} {'outcome':34} {'stdout':22} stderr"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for rung in data["table"]:
        if rung.startswith("nocheck-verus"):
            v = data.get("verus", {}).get(rung, {})
            if v.get("skipped"):
                outcome, so, se = "SKIPPED: " + v.get("why", "")[:24], "", ""
            else:
                outcome = f"does not build: {v.get('verified')} verified, {v.get('errors')} errors"
                so, se = "(no binary)", first_line(
                    "\n".join(d for d in v.get("diagnostics", []) if "not satisfied" in d))
        else:
            r = (data.get("runs", {}).get(rung) or {}).get(key)
            if not r:
                outcome, so, se = "NOT BUILT", "", ""
            else:
                rc = r["rc"]
                outcome = (f"signal {r['signal']} (rc {rc})" if r.get("signal")
                           else f"exit {rc}")
                so = first_line(r["stdout"]["text"]) or "(empty)"
                se = first_line(r["stderr"]["text"]) or "(empty)"
        print(f"  {rung:22} {outcome:34} {so:22} {se}")

    print()
    print("  every rung that built, on every input.  The rows WITHOUT `nocheck-`")
    print("  are shipped source; `c-gcc`/`c-clang` are shipped AND already have no")
    print("  check, which is p16's designed bug.")
    names = [r for r in ROW_ORDER if r in data.get("runs", {})]
    w = max(len(n) for n in INPUT_NAMES) + 2
    print(f"    {'rung':22}" + "".join(f"{n[:-4]:>{w}}" for n in INPUT_NAMES))
    for rung in names:
        cells = []
        for n in INPUT_NAMES:
            r = (data.get("runs", {}).get(rung) or {}).get(n)
            if not r:
                cells.append("-")
            elif r.get("signal"):
                cells.append(r["signal"].replace("SIG", ""))
            elif r["rc"] != 0:
                cells.append(f"exit{r['rc']}")
            else:
                cells.append(first_line(r["stdout"]["text"]) or "(empty)")
        print(f"    {rung:22}" + "".join(f"{c:>{w}}" for c in cells))

    v = data.get("verus", {})
    if isinstance(v, dict) and not v.get("skipped"):
        print()
        print("  verus")
        for rung in ("verus", "nocheck-verus"):
            d = v.get(rung) or {}
            if d.get("skipped"):
                print(f"    {rung:22} SKIPPED: {d.get('why')}")
                continue
            print(f"    {rung:22} rc={d.get('rc')}  "
                  f"{d.get('verified')} verified, {d.get('errors')} errors")
            for ln in d.get("diagnostics", []):
                print(f"      | {ln}")

    print()
    print("  mutants (derived here, never checked in)")
    for rung, m in (data.get("mutants") or {}).items():
        print(f"    {rung:22} {m['from']:16} -{m['deleted_lines']} lines at "
              f"line {m['deleted_at_line']}, from sha {m['from_sha256'][:12]}")


def cleanup(keep):
    if keep:
        print(f"p16_control: binaries kept in {scrub(os.path.join(WORK, 'bin'))}")
        return
    n = 0
    bins = os.path.join(WORK, "bin")
    for root, _dirs, files in os.walk(bins):
        for f in files:
            os.remove(os.path.join(root, f))
            n += 1
    shutil.rmtree(os.path.join(WORK, "verus-scratch"), ignore_errors=True)
    print(f"p16_control: removed {n} built binar{'y' if n == 1 else 'ies'} "
          f"(re-derivable: run this script)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="re-run and diff against the committed JSON; write nothing")
    ap.add_argument("--print", dest="show", action="store_true",
                    help="print the committed table; run nothing")
    ap.add_argument("--no-verus", action="store_true")
    ap.add_argument("--keep", action="store_true",
                    help="leave the built binaries in .temp/p16ctl/bin")
    a = ap.parse_args()

    if a.show:
        if not os.path.exists(OUT):
            raise SystemExit(f"p16_control: {scrub(OUT)} does not exist — "
                             f"run `python3 insights/p16_control.py` first")
        print_table(json.load(open(OUT, encoding="utf-8")))
        return 0

    data = generate(do_verus=not a.no_verus)

    if a.check:
        if not os.path.exists(OUT):
            raise SystemExit(f"p16_control: nothing to check against: {scrub(OUT)}")
        old = json.load(open(OUT, encoding="utf-8"))
        d = diff(volatile_free(old), volatile_free(data))
        if a.no_verus:
            d = [x for x in d if not x.startswith("/verus")]
        if d:
            print(f"p16_control: {len(d)} DRIFT(s) against {scrub(OUT)}")
            for line in d[:60]:
                print(f"  {line}")
            if len(d) > 60:
                print(f"  ... and {len(d) - 60} more")
            cleanup(a.keep)
            return 1
        print(f"p16_control: OK — re-run matches {scrub(OUT)} exactly")
        cleanup(a.keep)
        return 0

    if a.no_verus and os.path.exists(OUT):
        # Never let a fast run silently drop the Verus rows that are already
        # evidenced: carry them across and say so.
        old = json.load(open(OUT, encoding="utf-8"))
        if isinstance(old.get("verus"), dict) and not old["verus"].get("skipped"):
            data["verus"] = old["verus"]
            data["verus_carried_from"] = old["generated_utc"]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"p16_control: wrote {scrub(OUT)}")
    print_table(data)
    cleanup(a.keep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
