#!/usr/bin/env python3
"""asm_extract.py — cache the kernel assembly diffs the report shows.

    python3 insights/asm_extract.py              # refresh asmcache/ for every pattern
    python3 insights/asm_extract.py p03 p17      # just these
    python3 insights/asm_extract.py --verify     # check the cache against results/, write nothing

WHY THERE IS A CACHE AT ALL.

The assembly is not in the committed evidence — `results/*.json` publishes
digests and counts (`md5_fn`, `n_fn`, `pad_insns`), never text.  The text lives
only in the built binaries under `../.temp/build/`, which are 1.7 GB of scratch
that this project's own rules say get deleted once the gates are green.  So the
extraction is done once, here, and the result is committed.

WHY IT IS SAFE TO SHOW A CACHED DISASSEMBLY.

Because it is tied to the published evidence by digest.  Every side of every
diff records the `md5_fn` of the kernel symbol it was taken from, and
`results/<pid>.json` publishes that same digest for the same cell.  When they
match, the cached assembly IS the measured machine code — verifiably, not by
assumption.  When they do not, `build_data.py` withholds the diff and warns.

That is why this does not build its own binaries even though it easily could.
Binaries built here would carry no such tie: the assembly on screen might not be
the assembly that produced the Ir figures beside it, and nothing would say so.
`harness/build.py` is hashed into the measurement records precisely because a
second build pipeline is a way to publish numbers nobody can trace.

WHY IT DOES NOT RUN objdump ITSELF.

`harness/asm.py` is the only place in the repo that runs objdump, and its header
records what happened the last time there were two pipelines: they disagreed,
one could not have produced the published numbers, and three defects hid in the
gap.  This imports that module and calls it.

⚠ THE TEXT IS NORMALISED, WHICH MEANS IT IS FOR READING AND NOT FOR DECIDING.
`asm.normalise_text` erases every immediate, displacement and branch target — a
review once built two kernels that compute DIFFERENT ANSWERS and normalise
identically.  So `sub $,%rsp` below has lost its operand on purpose.  Identity
is decided by `md5_fn`, which is carried alongside and is what the page cites.
"""

import datetime as _dt
import difflib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)
CACHE = os.path.join(WEB, "asmcache")
BUILD = os.path.join(REPO, ".temp", "build")

sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402  — the one sanctioned objdump pipeline

# Both C compilers, because gcc and clang disagree often enough here that a
# single-compiler claim about "C" has been wrong twice in this project.
PAIRS = [
    ("c-gcc-check", "c-gcc", "c-gcc-h"),
    ("c-clang-check", "c-clang", "c-clang-h"),
    ("r2-r3", "safe_naive", "safe_tuned"),
    ("r3-r4", "safe_tuned", "unsafe"),
    ("r4-r5", "unsafe", "verus"),
    # Cross-language, and assembly-only: C and Rust source cannot be
    # line-diffed, but their kernels can be put side by side.  clang first
    # because it is the honest one — clang 22.1.6 IS the LLVM rustc 1.97.1
    # ships, so that pair has no backend difference in it at all.  gcc is here
    # as the what-a-distro-ships baseline and its differences confound backend
    # with language.
    # C vs Rust is CLANG ONLY.  gcc against rustc would confound the backend
    # with the language and this project has been wrong that way before.
    ("ch-r4-clang", "c-clang-h", "unsafe"),
    # gcc against clang on the SAME hardened C file: one source, two backends,
    # which is the control that says how much of any C-vs-Rust gap is compiler.
    ("ch-gcc-clang", "c-gcc-h", "c-clang-h"),
]
# `isolated` only, and not as a default: at `whole` the kernel is inlined into
# the driver and has no symbol of its own, so there is nothing to disassemble.
MODE = "isolated"
OPTS = ("O3", "O0")
CONTEXT = 4


def binary(pid_short, cell, opt):
    return os.path.join(BUILD, pid_short, f"{cell}-{opt}-{MODE}")


def readable_symbol(sym, cell):
    """A heading a person can read.

    Rust v0 mangling gives `_RNvCs86OlWC8CPt8_10safe_tuned6kernel`.  Nothing here
    needs general demangling — the symbol is always the kernel — so this pulls
    the crate and function out and leaves anything unrecognised alone.
    """
    if not sym.startswith("_R"):
        return sym
    parts, i, n = [], 2, len(sym)
    while i < n:
        c = sym[i]
        if c.isdigit():
            length = 0
            while i < n and sym[i].isdigit():
                length = length * 10 + int(sym[i]); i += 1
            if not length or i + length > n:
                break
            parts.append(sym[i:i + length]); i += length
        elif c == "s":
            # `s<base62>_` disambiguator.  Skipping it is the whole trick: its
            # base62 payload contains digits, and reading those as a length
            # prefix is what made the first version of this a silent no-op.
            j = sym.find("_", i)
            if j < 0:
                break
            i = j + 1
        else:
            i += 1
    return "::".join(parts) if parts else sym


def collapse(ops, context):
    """Long unchanged runs become a single "@<count>" marker.

    Ops are encoded as one string each — first character is the kind
    (space / - / + / @), the rest is the instruction text (or, for @, the count
    of instructions skipped).  An object per line tripled the cache for nothing:
    the same content was 2.0 MB as {"k":..,"s":..} and is well under half that
    as strings.
    """
    keep = [False] * len(ops)
    for i, o in enumerate(ops):
        if o[0] == " ":
            continue
        for j in range(max(0, i - context), min(len(ops), i + context + 1)):
            keep[j] = True
    out, run = [], 0
    for i, o in enumerate(ops):
        if keep[i]:
            if run:
                out.append("@" + str(run)); run = 0
            out.append(o)
        else:
            run += 1
    if run:
        out.append("@" + str(run))
    return out


def extract_pair(pid_short, a_cell, b_cell, opt):
    pa, pb = binary(pid_short, a_cell, opt), binary(pid_short, b_cell, opt)
    if not (os.path.exists(pa) and os.path.exists(pb)):
        return None, f"binary missing ({os.path.basename(pa)} / {os.path.basename(pb)})"
    ka, kb = asm.try_kernel(pa), asm.try_kernel(pb)
    if ka is None or kb is None:
        return None, "no kernel symbol"

    la = [asm.normalise_text(i.text) for i in ka.insns_fn]
    lb = [asm.normalise_text(i.text) for i in kb.insns_fn]
    sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
    ops, added, removed = [], 0, 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            ops += [" " + t for t in la[i1:i2]]
        else:
            ops += ["-" + t for t in la[i1:i2]]
            ops += ["+" + t for t in lb[j1:j2]]
            removed += i2 - i1
            added += j2 - j1

    # asm.py's own classification, weakest to strongest: differ / counts /
    # norel / exact.  A bare md5_fn comparison is not enough to describe what a
    # reader is looking at: at -O0 the Rust kernels still call Iterator::next,
    # so md5_fn differs for LINK reasons while the normalised text is identical
    # — which shows up as "not identical" beside a diff of zero lines.  `norel`
    # is the level that says exactly that, and the page reports it.
    level = asm.identity_level(ka, kb)
    if isinstance(level, tuple):
        level = level[0]

    return {
        "a": {"cell": a_cell, "md5_fn": ka.md5_fn, "md5_fn_norel": ka.md5_fn_norel,
              "n_fn": ka.n_fn, "symbol": readable_symbol(ka.symbol, a_cell)},
        "b": {"cell": b_cell, "md5_fn": kb.md5_fn, "md5_fn_norel": kb.md5_fn_norel,
              "n_fn": kb.n_fn, "symbol": readable_symbol(kb.symbol, b_cell)},
        "identical": ka.md5_fn == kb.md5_fn,
        "identity_level": level,
        "added": added, "removed": removed,
        "ops": collapse(ops, CONTEXT),
    }, None


def published_md5(pid, cell, opt):
    """What results/<pid>.json says this cell's kernel digest is."""
    p = os.path.join(REPO, "results", pid + ".json")
    if not os.path.exists(p):
        return None
    rec = json.load(open(p, encoding="utf-8"))
    for c in rec.get("cells", []):
        if c.get("cell") == cell and c.get("opt") == opt and c.get("mode") == MODE:
            return (c.get("static") or {}).get("md5_fn")
    return None


def verify(pid, data):
    """Every cached digest must equal the one results/ publishes."""
    bad = []
    for pair_id, by_opt in (data.get("pairs") or {}).items():
        for opt, d in by_opt.items():
            for side in ("a", "b"):
                want = published_md5(pid, d[side]["cell"], opt)
                if want is None:
                    bad.append(f"{pair_id}/{opt}/{side}: results/ has no {d[side]['cell']} {opt} {MODE} cell")
                elif want != d[side]["md5_fn"]:
                    bad.append(f"{pair_id}/{opt}/{side}: cached {d[side]['md5_fn'][:8]} "
                               f"but results/ publishes {want[:8]} — cache is STALE")
    return bad


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    verify_only = "--verify" in sys.argv

    pids = sorted(f[:-5] for f in os.listdir(os.path.join(WEB, "data", "code"))
                  if f.endswith(".json")) if os.path.isdir(os.path.join(WEB, "data", "code")) else []
    if argv:
        pids = [p for p in pids if any(p.startswith(a) or p == a for a in argv)]

    os.makedirs(CACHE, exist_ok=True)
    total_bad, wrote, skipped = 0, 0, []

    for pid in pids:
        short = pid.split("-")[0]
        dest = os.path.join(CACHE, pid + ".json")

        if verify_only:
            if not os.path.exists(dest):
                print(f"  {pid}: no cache"); continue
            bad = verify(pid, json.load(open(dest, encoding="utf-8")))
            total_bad += len(bad)
            print(f"  {pid}: {'OK' if not bad else str(len(bad)) + ' STALE'}")
            for b in bad:
                print(f"      {b}", file=sys.stderr)
            continue

        pairs, notes = {}, []
        for pair_id, a_cell, b_cell in PAIRS:
            by_opt = {}
            for opt in OPTS:
                d, why = extract_pair(short, a_cell, b_cell, opt)
                if d:
                    by_opt[opt] = d
                elif opt == "O3":
                    notes.append(f"{pair_id}: {why}")
            if by_opt:
                pairs[pair_id] = by_opt
        if not pairs:
            skipped.append(pid); continue

        data = {
            "pattern": pid,
            "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": MODE,
            "normalised": True,
            "pairs": pairs,
        }
        bad = verify(pid, data)
        total_bad += len(bad)
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(data, fh, separators=(",", ":"), sort_keys=True)
        wrote += 1
        flag = "" if not bad else f"  ** {len(bad)} digest mismatch"
        print(f"  {pid:22} {len(pairs)} pair(s){flag}")
        for b in bad:
            print(f"      {b}", file=sys.stderr)

    if skipped:
        print(f"  no binaries for: {', '.join(skipped)} — run harness/build.py", file=sys.stderr)
    print(f"asm_extract: {'verified' if verify_only else 'wrote'} {wrote or len(pids)} pattern(s), "
          f"{total_bad} digest mismatch(es)")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
