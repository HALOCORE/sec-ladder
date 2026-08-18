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
  * the pattern's **declared idiom** is printed above the numbers, because this
    file is the artefact a writeup reads from and it carried no trace of what a
    pattern forbids until TASK_017. It is worth having on its own merits; it is
    **not** the fix for the observed failure, and TASK_017 said it was. See
    `idiom_section` for what actually happened.

  harness/report.py p01
  harness/report.py p01 --stdout
"""

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")
TABLES = os.path.join(RESULTS, "tables")


def load(pid):
    """The measure.py record for `pid`.

    `results/` also holds side records -- p02 ships `p02-residue-sweep.json`
    beside `p02-buffer-copy.json` -- and matching on the `pNN-` prefix alone
    made `report.py p02` a hard error from the day the sweep was committed,
    which is why `results/tables/p02-buffer-copy.md` was never regenerated
    (found at TASK_008). A measure.py record is the one with a `cells` list, so
    that is the discriminator; the exact stem still works if it is ever
    ambiguous even so."""
    hits = sorted(f for f in os.listdir(RESULTS)
                  if (f == pid + ".json" or f.startswith(pid + "-"))
                  and f.endswith(".json"))
    if len(hits) > 1:
        keep = []
        for f in hits:
            try:
                if isinstance(json.load(open(os.path.join(RESULTS, f)))
                              .get("cells"), list):
                    keep.append(f)
            except (ValueError, OSError):
                continue
        if len(keep) == 1:
            hits = keep
        else:
            raise SystemExit(
                f"report.py: {pid} matches {hits} in results/, of which "
                f"{keep} carry a `cells` list. Name the stem exactly.")
    if len(hits) != 1:
        raise SystemExit(f"report.py: {pid} matches {hits} in results/")
    return json.load(open(os.path.join(RESULTS, hits[0]))), hits[0]


def fmt(n):
    return "-" if n is None else f"{n:,}"


def cell_rows(doc, opt, mode):
    return [c for c in doc["cells"]
            if c.get("opt") == opt and c.get("mode") == mode]


def read_idiom(pattern):
    """The pattern's declared idiom, out of `patterns/<pattern>/spec.md`.

    Read from `spec.md`, not from `results/gate/<pattern>.json`, although the
    gate record carries a copy: the copy is as old as the last gate run, and a
    table generated today must show what the pattern declares today. Same block
    and same regex as `check.py: read_contract()`, which hashes it into
    `contract_sha256`.

    Returns None (and the section then says so loudly) if the file, the block or
    its JSON is missing -- `report.py` regenerates a description of a
    measurement and must not become a second gate."""
    path = os.path.join(REPO, "patterns", pattern, "spec.md")
    try:
        txt = open(path).read()
    except OSError:
        return None
    m = re.search(r"```slb-contract\s*\n(.*?)```", txt, re.S)
    if not m:
        return None
    try:
        idi = json.loads(m.group(1)).get("idiom")
    except ValueError:
        return None
    return idi if isinstance(idi, dict) else None


def idiom_section(doc, out):
    """What the numbers below are numbers *of*.

    TASK_017 Part 2, from TASK_016_REVIEW B1.

    **What this does not do, corrected at TASK_018 (TASK_017_REVIEW M2.)**
    TASK_017 wrote here that the observed failure "is a reader who quotes
    `results/tables/p05-index-flatten.md` without ever opening
    `patterns/p05-index-flatten/spec.md`, which happened in two consecutive
    tasks and cost a published headline". That is false as a description of what
    happened: `.temp/review014/NOTES.md` and `.temp/p05r3/NOTES.md` have **zero**
    occurrences of `results/tables` between them -- neither task read a generated
    table. What they read is in `.memory/01-ladder.md:15-22`: both quoted
    **`.memory/01-ladder.md`'s own permissive R3 rung list**, which names
    `chunks_exact` as an R3 technique, as licence for a spelling p05's `spec.md`
    forbids.

    So the failure this section addresses is a *possible* one, not the observed
    one, and the mechanism that would have caught the observed one is a
    declaration on `.memory/01-ladder.md`'s rung table -- which this file cannot
    print. Keep the section: a declaration above every table is worth having,
    and it is the only copy of the idiom a reader of `results/` will ever see.
    Do not budget against it as the repair for the two-task failure."""
    out.append("\n## Declared idiom — what these numbers are numbers *of*\n")
    idi = read_idiom(doc["pattern"])
    if not idi:
        out.append(f"**No `idiom` object could be read from "
                   f"`patterns/{doc['pattern']}/spec.md`.** Every pattern is "
                   f"required to declare one (gate stage `0b`), so this table "
                   f"is describing a pattern that would not pass the gate — "
                   f"treat every number below as unattributed.\n")
        return
    out.append("Every delta below is a difference between rungs that are meant to be "
               "spellings of one kernel. The pattern's hashed `slb-contract` block "
               "declares which spellings that means; **a rung that deviates is a "
               "different benchmark and its numbers are not comparable to these.**\n")
    for s in idi.get("required") or []:
        out.append(f"- **required** — {s}")
    for s in idi.get("forbidden") or []:
        out.append(f"- **FORBIDDEN** — {s}")
    if not (idi.get("forbidden") or []):
        out.append("- **FORBIDDEN** — *nothing is excluded by name.* The rungs are "
                   "matched only by the `required` list above, so these numbers are "
                   "a spelling's numbers unless the rationale below argues otherwise.")
    out.append(f"\n> **Why**: {idi.get('why') or '(none given)'}\n")
    out.append("> The gate checks that this declaration is **present** and hashes it "
               "into `contract_sha256`. It never checks that a rung honours it — that "
               "check would have to be textual and would fail open, and the threat "
               "model is honest mistake, not malicious author. TASK_016_REVIEW forked "
               "p05 with a **forbidden** R3 and got a complete green run with an "
               "unchanged `contract_sha256`. So this section is a claim about intent "
               "that a reader must check against the rung sources, not a verified "
               "property of the numbers below.\n")


def main_table(doc, opt, mode, out):
    rows = cell_rows(doc, opt, mode)
    if not rows:
        return
    # The static counts in this table are for *one* symbol, named by
    # `asm_symbol_needle`. `Ir` gets its own columns per symbol and is never
    # merged into one: pairing a `main` static count with a `kernel` `Ir` (which
    # is what the O0/whole section used to do) is not a row, it is two halves of
    # two different measurements (TASK_002_REVIEW, M12).
    sym = rows[0].get("asm_symbol_needle") or ("kernel" if mode == "isolated"
                                               else "main")
    kernel_alive = any((c.get("ir") or {}).get(i, {}).get("kernel_exclusive_ir")
                       is not None for c in rows for i in ("small.bin", "large.bin"))
    label = f"static counts are for the `{sym}` symbol"
    if mode == "whole":
        label += ("; the kernel symbol **survived** at this opt level, so nothing "
                  "was inlined and the `Ir(kernel)` column is the real kernel cost"
                  if kernel_alive else
                  "; the kernel was inlined away, so it has no symbol and no "
                  "static count of its own here")
    out.append(f"\n### {opt} / {mode} — {label}\n")
    if opt == "O0":
        out.append("> `O0` rows exist to read the lowering. **No performance claim "
                   "may rest on one** (`.memory/02-bench-rules.md`). Rust here is "
                   "`opt-level=0 -C debug-assertions=off`, i.e. semantics-matched to "
                   "C `-O0`; the `O0d` axis (overflow checks on) is a separate build.\n")
    out.append(f"| rung | `{sym}` instrs (nm extent) | pad-excl | trailing pad "
               "(insns) | sym bytes | Ir(kernel) small | Ir(kernel) large | "
               "Ir(main) small | Ir(main) large | md5_fn | md5_raw | loop | vec |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|")
    for c in rows:
        s = c.get("static") or {}
        ir = c.get("ir") or {}

        def irv(inp, which):
            v = ir.get(inp) or {}
            if not v or "error" in v:
                return "-"
            n = v.get(which + "_exclusive_ir")
            return "-" if n is None else fmt(n)
        # md5_fn is the `nm --print-size` extent (the function); md5_raw is
        # objdump's grouping, which also swallows the alignment padding that
        # `pad` counts. Older JSONs have only md5_raw.
        out.append(
            f"| {c['cell']} | {fmt(s.get('n_fn', s.get('n_raw')))} | "
            f"{fmt(s.get('n_fn_nopad', s.get('n_nopad')))} | "
            f"{fmt(s.get('pad_insns'))} | {fmt(s.get('fn_bytes', s.get('n_bytes')))} | "
            f"{irv('small.bin', 'kernel')} | {irv('large.bin', 'kernel')} | "
            f"{irv('small.bin', 'main')} | {irv('large.bin', 'main')} | "
            f"`{(s.get('md5_fn') or '-')[:8]}` | `{(s.get('md5_raw') or '')[:8]}` | "
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
    # `.memory/03-measurement.md` step 4: "Discard a run whose min-to-median
    # spread exceeds 10% and say so." measure.py records the warning per cell;
    # this table used to drop it silently (TASK_002_REVIEW, M10), so a table of
    # mostly-discarded numbers read as a table of numbers.
    discarded = []
    out.append("| rung | mode | " + " | ".join(
        f"{i} min (ms) | {i} median (ms) | {i} spread" for i in inputs) + " |")
    out.append("|---|---|" + "---:|---:|---:|" * len(inputs))
    for c in rows:
        cells = []
        for i in inputs:
            w = c["wall"].get(i)
            if not w:
                cells += ["-", "-", "-"]
                continue
            sp = w.get("spread_pct")
            bad = "warning" in w or (sp is not None and sp > 10)
            if bad:
                discarded.append((c["cell"], c["mode"], i, sp))
            cells.append(f"{w['min_s'] * 1e3:.2f}")
            cells.append(f"{w['median_s'] * 1e3:.2f}")
            cells.append(("**" + f"{sp:.1f}%" + " ✗**") if bad
                         else (f"{sp:.1f}%" if sp is not None else "-"))
        out.append(f"| {c['cell']} | {c['mode']} | " + " | ".join(cells) + " |")
    total = sum(1 for c in rows for i in inputs if c["wall"].get(i))
    out.append("")
    if discarded:
        out.append(f"**{len(discarded)} of {total} wall-clock cells exceed the 10% "
                   f"min-to-median spread threshold and are DISCARDED** per "
                   f"`.memory/03-measurement.md` step 4. They are printed above "
                   f"marked ✗ rather than deleted, because a missing cell that "
                   f"looks like an omission is worse than a documented failure "
                   f"(`.memory/02-bench-rules.md`). **No claim in this report "
                   f"rests on a marked row.**\n")
        for cell, mode, inp, sp in discarded:
            out.append(f"- `{cell} / {mode}` on `{inp}`: spread {sp:.1f}%")
        out.append("")
    else:
        out.append("Every wall-clock cell is within the 10% min-to-median spread "
                   "threshold.\n")


def identity_table(doc, out):
    out.append("\n## Structural identity — does a proof cost anything?\n")
    out.append("Compared in `isolated` builds, where the kernel is its own symbol, "
               "and on the **declared symbol extent** (`nm --print-size`), which is "
               "the function proper. `md5_raw` is objdump's grouping and also "
               "covers the alignment padding that follows the function, so two "
               "genuinely identical kernels at different alignments disagree on it "
               "and agree on `md5_fn` — the padding is reported separately rather "
               "than folded in. `md5_fn_norel` is the same bytes with pc-relative "
               "displacement fields zeroed, which is the honest (weaker) oracle "
               "when two binaries link the kernel's callees at different addresses "
               "— that happens at `O0`, where the Rust kernel still calls "
               "`Iterator::next`.\n")
    out.append("| pair | opt | md5_fn equal | md5_fn_norel equal | md5_raw equal | "
               "counts (fn / pad-excl) | padding |")
    out.append("|---|---|---|---|---|---|---|")
    by = {(c.get("cell"), c.get("opt"), c.get("mode")): c for c in doc["cells"]}
    for a, b in (("unsafe", "verus"), ("safe_naive", "safe_naive_verus")):
        for opt in ("O0", "O3"):
            ca, cb = by.get((a, opt, "isolated")), by.get((b, opt, "isolated"))
            if not (ca and cb and ca.get("static") and cb.get("static")):
                continue
            sa, sb = ca["static"], cb["static"]

            def eq(k):
                if k not in sa or k not in sb:
                    return "—"
                return "**yes**" if sa[k] == sb[k] else "no"
            cnt = (f"{sa.get('n_fn', sa['n_raw'])}/{sa.get('n_fn_nopad', sa['n_nopad'])}"
                   f" vs {sb.get('n_fn', sb['n_raw'])}/"
                   f"{sb.get('n_fn_nopad', sb['n_nopad'])}")
            pad = (f"{sa.get('pad_bytes', '—')} B vs {sb.get('pad_bytes', '—')} B")
            out.append(f"| {a} vs {b} | {opt} | {eq('md5_fn')} | "
                       f"{eq('md5_fn_norel')} | {eq('md5_raw')} | {cnt} | {pad} |")


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
    # The last column is the pattern's own `model.py` describing the input.
    # It used to be `win_len`/`v_len`, i.e. p01's payload layout hard-coded into
    # the report of every pattern.
    out.append("| file | n_iters | declared payload | present | truncated | model |")
    out.append("|---|---:|---:|---:|---|---|")
    for k, v in doc["inputs"].items():
        out.append(f"| {k} | {fmt(v['n_iters'])} | {fmt(v['declared_len'])} | "
                   f"{fmt(v['present'])} | {v['truncated']} | "
                   f"{v.get('model', '')} |")

    idiom_section(doc, out)

    out.append("\n## Static + executed instructions\n")
    out.append("`Ir` is **callgrind per-function exclusive** for the kernel symbol. "
               "The whole-program total is deliberately absent: it moves with the "
               "size of the environment block and does not reproduce across shells "
               "(`.memory/03-measurement.md`). Static counts are given raw and "
               "padding-excluded; quote the padding-excluded one, and never quote "
               "either without the `Ir` beside it.")
    out.append("\n`Ir(kernel)` and `Ir(main)` are separate columns and are never "
               "merged: a `main`-exclusive count is not a kernel measurement "
               "wearing a different hat, and pairing one with a static count "
               "taken from the *other* symbol is two halves of two different "
               "measurements. **`Ir(main)` counts whatever else was inlined into "
               "`main`, and that is not the same set in every language**: the Rust "
               "rungs inline the whole payload decoder, while the C rungs leave it "
               "in `common/driver.c`'s own symbols. On `large` that is ~12.4 M "
               "instructions the Rust `main` rows carry and the C ones do not "
               "(~12.36 M vs ~0.38 M in the `isolated` rows). So `Ir(main)` is "
               "comparable **between Rust rungs only** — never Rust-vs-C, and "
               "never to an `isolated` row.")
    out.append("\n**Do not try to rescue it by subtraction.** A difference of two "
               "large numbers, each containing language-specific inlining, is not "
               "a measurement — `.memory/03-measurement.md` records the arithmetic "
               "that went wrong when TASK_002 tried. Use the `isolated` "
               "kernel-exclusive figure, which needs no correction.")
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
