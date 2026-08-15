#!/usr/bin/env python3
"""results/pNN-<slug>.json -> markdown tables in results/tables/.

Everything here is regenerable; the JSON is the record. Three rules from
`.memory/` are baked into the formatting rather than left to the writer:

  * a static instruction count never appears without its padding-excluded twin
    and, where measured, a paired `Ir` -- a static count alone is not a cost
    model (gcc's 32-instruction pilot kernel executed 43% more than LLVM's 37)
  * identity is reported from `md5_raw`, with `md5_raw_norel` shown alongside so
    a link-layout-only difference is visible as such
  * `O0` rows are printed but flagged: no perf claim may rest on one

  harness/report.py p01
  harness/report.py p01 --stdout
"""

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")
TABLES = os.path.join(RESULTS, "tables")


def load(pid):
    hits = [f for f in os.listdir(RESULTS)
            if f.startswith(pid + "-") and f.endswith(".json")]
    if len(hits) != 1:
        raise SystemExit(f"report.py: {pid} matches {hits} in results/")
    return json.load(open(os.path.join(RESULTS, hits[0]))), hits[0]


def fmt(n):
    return "-" if n is None else f"{n:,}"


def cell_rows(doc, opt, mode):
    return [c for c in doc["cells"]
            if c.get("opt") == opt and c.get("mode") == mode]


def main_table(doc, opt, mode, out):
    rows = cell_rows(doc, opt, mode)
    if not rows:
        return
    sym = "kernel" if mode == "isolated" else "main (kernel inlined)"
    out.append(f"\n### {opt} / {mode} — symbol: `{sym}`\n")
    if opt == "O0":
        out.append("> `O0` rows exist to read the lowering. **No performance claim "
                   "may rest on one** (`.memory/02-bench-rules.md`). Rust here is "
                   "`opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to "
                   "C `-O0`; the `O0d` axis (overflow checks on) is a separate build.\n")
    out.append("| rung | static raw | static pad-excl | sym bytes | "
               "Ir small | Ir large | md5_raw | md5_norel | loop | vec |")
    out.append("|---|---:|---:|---:|---:|---:|---|---|---|---|")
    for c in rows:
        s = c.get("static") or {}
        ir = c.get("ir") or {}
        def irv(k):
            v = ir.get(k) or {}
            if not v or "error" in v:
                return "-"
            # `kernel` when the symbol survived (isolated, and whole at O0 where
            # nothing inlines); `main` when it did not (whole at O3). Never both
            # added together, and never one silently standing in for the other.
            if v.get("kernel_exclusive_ir") is not None:
                return fmt(v["kernel_exclusive_ir"])
            if v.get("main_exclusive_ir") is not None:
                return fmt(v["main_exclusive_ir"]) + " *"
            return "-"
        out.append(
            f"| {c['cell']} | {fmt(s.get('n_raw'))} | {fmt(s.get('n_nopad'))} | "
            f"{fmt(s.get('n_bytes'))} | {irv('small.bin')} | {irv('large.bin')} | "
            f"`{(s.get('md5_raw') or '')[:8]}` | `{(s.get('md5_raw_norel') or '')[:8]}` | "
            f"{'yes' if s.get('has_loop') else 'NO'} | "
            f"{','.join(s.get('vector_regs') or []) or '-'} |")


def wall_table(doc, out):
    rows = [c for c in doc["cells"] if c.get("wall")]
    if not rows:
        return
    out.append("\n## Wall clock (secondary)\n")
    p = doc.get("protocol", {}).get("wall", "")
    out.append(f"> {p}. Frequency scaling is on and cannot be disabled without "
               f"root; the box is shared and containerised. Wall clock is a sanity "
               f"check on `Ir`, never the headline. Times include process start-up "
               f"and reading the input file.\n")
    inputs = sorted({k for c in rows for k in c["wall"]})
    out.append("| rung | mode | " + " | ".join(f"{i} min (ms) | {i} median (ms)"
                                               for i in inputs) + " |")
    out.append("|---|---|" + "---:|---:|" * len(inputs))
    for c in rows:
        cells = []
        for i in inputs:
            w = c["wall"].get(i)
            cells.append(f"{w['min_s'] * 1e3:.2f}" if w else "-")
            cells.append(f"{w['median_s'] * 1e3:.2f}" if w else "-")
        out.append(f"| {c['cell']} | {c['mode']} | " + " | ".join(cells) + " |")


def identity_table(doc, out):
    out.append("\n## Structural identity — does a proof cost anything?\n")
    out.append("Compared in `isolated` builds, where the kernel is its own symbol. "
               "`md5_raw` is bit-exact machine code; `md5_norel` is the same bytes "
               "with pc-relative displacement fields zeroed, which is the honest "
               "oracle when two binaries link the kernel's callees at different "
               "addresses (that happens at `O0`, where the Rust kernel still calls "
               "`Iterator::next`).\n")
    out.append("| pair | opt | md5_raw equal | md5_norel equal | raw counts |")
    out.append("|---|---|---|---|---|")
    by = {(c.get("cell"), c.get("opt"), c.get("mode")): c for c in doc["cells"]}
    for a, b in (("unsafe", "verus"), ("safe_naive", "safe_naive_verus")):
        for opt in ("O0", "O3"):
            ca, cb = by.get((a, opt, "isolated")), by.get((b, opt, "isolated"))
            if not (ca and cb and ca.get("static") and cb.get("static")):
                continue
            sa, sb = ca["static"], cb["static"]
            out.append(
                f"| {a} vs {b} | {opt} | "
                f"{'**yes**' if sa['md5_raw'] == sb['md5_raw'] else 'no'} | "
                f"{'**yes**' if sa['md5_raw_norel'] == sb['md5_raw_norel'] else 'no'} | "
                f"{sa['n_raw']}/{sa['n_nopad']} vs {sb['n_raw']}/{sb['n_nopad']} |")


def build(doc, name):
    out = [f"# {doc['pattern']} — results", ""]
    out.append(f"Generated {doc['generated_utc']} from `results/{name}` "
               f"(git `{doc['git']['commit'][:12]}`"
               f"{', working tree dirty' if doc['git']['dirty'] else ''}).")
    out.append("")
    out.append("## Toolchain\n")
    for k, v in doc["toolchain"].items():
        first = str(v).splitlines()[0] if v else "?"
        out.append(f"- **{k}**: {first}")
    out.append(f"- **host**: {doc['host']['cpu_model']}, governor "
               f"`{doc['host']['governor']}`")
    out.append("")
    out.append("## Inputs\n")
    out.append("| file | n_iters | declared payload | present | win_len | v_len | truncated |")
    out.append("|---|---:|---:|---:|---:|---:|---|")
    for k, v in doc["inputs"].items():
        out.append(f"| {k} | {fmt(v['n_iters'])} | {fmt(v['declared_len'])} | "
                   f"{fmt(v['present'])} | {fmt(v['win_len'])} | {fmt(v['v_len'])} | "
                   f"{v['truncated']} |")

    out.append("\n## Static + executed instructions\n")
    out.append("`Ir` is **callgrind per-function exclusive** for the kernel symbol. "
               "The whole-program total is deliberately absent: it moves with the "
               "size of the environment block and does not reproduce across shells "
               "(`.memory/03-measurement.md`). Static counts are given raw and "
               "padding-excluded; quote the padding-excluded one, and never quote "
               "either without the `Ir` beside it.")
    out.append("\nAn `Ir` marked `*` is `main`-exclusive, not kernel-exclusive: the "
               "kernel was inlined and has no symbol left. **Read those rows with "
               "care.** `main`-exclusive counts whatever else was inlined into "
               "`main`, and that is not the same set in every language: the Rust "
               "rungs inline the whole payload decoder, while the C rungs leave it "
               "in `common/driver.c`'s own symbols. On `large` that is ~12.4 M "
               "instructions the Rust `main` rows carry and the C ones do not "
               "(visible as the `isolated` `main`-exclusive figures in the JSON: "
               "~12.36 M vs ~0.38 M). So a starred row is comparable **between "
               "Rust rungs only** — never Rust-vs-C, and never to an `isolated` "
               "row. Subtract the same cell's `isolated` `main` figure first if "
               "you need the inlined kernel's cost.")
    for mode in ("isolated", "whole"):
        for opt in ("O3", "O0"):
            main_table(doc, opt, mode, out)
    identity_table(doc, out)
    wall_table(doc, out)

    missing = [c for c in doc["cells"] if c.get("status", "ok") != "ok"]
    out.append("\n## Cells and metrics not measured\n")
    if missing:
        for c in missing:
            out.append(f"- `{c.get('cell')} {c.get('opt')} {c.get('mode')}`: "
                       f"{c['status']}")
    else:
        out.append("Every cell in the matrix built, ran and produced static counts, "
                   "digests and a checksum.")
    # Callgrind is a ~50x slowdown and its coverage is a plan, not exhaustive.
    # Say which (opt, mode, input) combinations have an Ir and which do not,
    # rather than leaving a bare `-` in the table.
    have, want = set(), set()
    for c in doc["cells"]:
        if c.get("status", "ok") != "ok":
            continue
        for inp in doc["inputs"]:
            if doc["inputs"][inp]["truncated"] or inp.startswith("adversarial"):
                continue
            want.add((c["opt"], c["mode"], inp))
            v = (c.get("ir") or {}).get(inp)
            if v and "error" not in v:
                have.add((c["opt"], c["mode"], inp))
    gaps = sorted(want - have)
    out.append("")
    if gaps:
        out.append(f"No `Ir` was collected for {len(gaps)} (opt, mode, input) "
                   f"combination(s) — callgrind runs to a fixed plan "
                   f"(`harness/measure.py: CG_PLAN`), not exhaustively:")
        for o, m, i in gaps:
            out.append(f"- `{o} / {m}` on `{i}`")
    else:
        out.append("Every (opt, mode, input) combination has a paired `Ir`.")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    pid = a.pattern.split("-")[0]
    doc, name = load(pid)
    md = build(doc, name)
    if a.stdout:
        print(md)
        return 0
    os.makedirs(TABLES, exist_ok=True)
    out = os.path.join(TABLES, name.replace(".json", ".md"))
    open(out, "w").write(md)
    print(f"wrote {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
