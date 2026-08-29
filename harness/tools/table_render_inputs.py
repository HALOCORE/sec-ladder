#!/usr/bin/env python3
"""What does `results/tables/*.md` actually depend on? Measure it; don't read it.

    python3 harness/tools/table_render_inputs.py --reads     # the MEASURED read set
    python3 harness/tools/table_render_inputs.py --selfref   # MUST-BE-ZERO check
    python3 harness/tools/table_render_inputs.py --against DIR   # two-draw stability

`check.py` stage `9c` (`check_table_render`, TASK_127) certifies that every
published table is byte-identical to what `harness/report.py` renders from this
tree. That is only sound while the render is a **deterministic function of
committed sources**. This tool is the probe that keeps it so, and it exists
because the premise it protects was nearly wrong when the stage was written.

## Why this is a tool and not a comment

`report.py` reads three things: `results/pNN-<slug>.json`, the pattern's
`spec.md`, and `results/gate/<pattern>.json`. The first two are stable -- they
change only when someone runs `measure.py` or edits the file. ⚠ **The third is
not:** a gate record is not byte-reproducible (`.memory/03-measurement.md`), and
comparing the committed records against a second sweep of the same tree,
**21 of 26 differ**. Everything that moves is run-scoped -- sanitizer
`diagnostic` strings, `miri.runs[].seconds`, `adversarial` group order, and the
`N distinct behaviours` `notes` line -- and **none of it is in the set
`report.py` reads**, which is the whole reason stage 9c can work where a
whole-file hash of the gate record cannot.

⚠⚠ **THAT IS A CLAIM ABOUT `report.py`'s CODE, AND CODE CHANGES.** `--reads`
measures the read set by mutation instead of by reading the source, so it stays
true across edits.

## `--selfref` is the one that must never regress

Until TASK_127 `report.py` rendered the gate record's `verdict` into the table.
`verdict` is an **output** of the gate run stage 9c runs in, so the stage wrote
its own input and oscillated with period 2 -- starting the first time it fired:

    run N    9c fires -> rep.fail -> verdict FAIL -> the record says FAIL
    report.py         -> the table prints ``verdict `FAIL```
    run N+1  render(FAIL record) == table -> FRESH -> verdict PASS
    run N+2  render(PASS record) != table -> FIRES AGAIN -> ...

Measured before the fix: **19 of 26 tables changed bytes when the record's
`verdict` changed.** `--selfref` re-runs exactly that measurement and exits 1 if
it is ever non-zero again. ⚠ `blocked` is checked too, and `failures`, and
`invocation`, and `complete_run`: all four are functions of the RUN rather than
of the sources, so any of them reaching the render recreates the defect.

## Placement

`harness/tools/` is **outside** the gate digest -- `check.py`'s `srcs` globs
`harness/*.py` non-recursively (TASK_125) -- so this file costs no gate sweep to
maintain. ⚠ **It must never be imported by `check.py`, `measure.py` or
`build.py`**, or the digest would silently stop covering a file that decides a
verdict. Stage 9c therefore re-implements nothing from here; it calls
`report.build` directly, which is the same function this tool calls.
"""

import argparse
import copy
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
import report  # noqa: E402

GATE = os.path.join(REPO, "results", "gate")
SCRATCH = os.path.join(REPO, ".temp", "table_render_inputs")

#: Gate-record keys that are a function of the RUN rather than of the committed
#: sources. Any of these reaching the render recreates TASK_127's oscillation.
RUN_SCOPED = ("verdict", "blocked", "failures", "invocation", "complete_run",
              "notes", "sanitizer", "miri", "adversarial")

#: A value no record uses, so substituting it always counts as a mutation.
SENTINEL = "__slb_probe_sentinel__"


def patterns():
    return sorted(f[:-5] for f in os.listdir(GATE) if f.endswith(".json"))


def render(pattern, record=None):
    """`report.build`'s markdown for `pattern`, optionally with `record`
    substituted for `results/gate/<pattern>.json`."""
    gs = os.path.join(SCRATCH, "gate")
    os.makedirs(gs, exist_ok=True)
    for f in os.listdir(os.path.join(REPO, "results")):
        if f.endswith(".json"):
            d = os.path.join(SCRATCH, f)
            if not os.path.islink(d):
                os.symlink(os.path.join(REPO, "results", f), d)
    dst = os.path.join(gs, pattern + ".json")
    if os.path.lexists(dst):
        os.remove(dst)
    if record is None:
        os.symlink(os.path.join(GATE, pattern + ".json"), dst)
    else:
        json.dump(record, open(dst, "w"), default=str)
    old = report.RESULTS
    report.RESULTS = SCRATCH
    try:
        doc, name = report.load(pattern.split("-")[0])
        return report.build(doc, name)
    finally:
        report.RESULTS = old


def mutate(value):
    """A value of the same JSON type that is guaranteed different.

    ⚠ A list gets an element SHAPED LIKE THE ONES ALREADY IN IT. Appending a
    bare string to `loud` -- which holds `{"section", "message"}` dicts --
    makes `report.py` raise `AttributeError`, and a probe that crashes the
    thing it is measuring reports nothing at all. Found by running it.

    ⚠⚠ A dict is mutated RECURSIVELY, at every leaf, and the weaker version
    (add one unused key) was WRONG: it reported `idiom_audit` as NOT READ on
    26 of 26 patterns, when `report.py::audit_section` renders eight of its
    fields. **A mutation the renderer does not look at proves nothing**, which
    is this repo's own "a control that could not have fired"."""
    if isinstance(value, dict):
        return ({k: mutate(v) for k, v in value.items()} if value
                else {SENTINEL: SENTINEL})
    if isinstance(value, list):
        proto = value[0] if value else {}
        if isinstance(proto, dict):
            return list(value) + [{k: SENTINEL for k in proto} or
                                  {SENTINEL: SENTINEL}]
        return list(value) + [SENTINEL]
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    if isinstance(value, str):
        return value + SENTINEL
    return SENTINEL


def render_or_raised(pattern, record):
    """`(markdown, raised)`. A mutation that makes `report.py` RAISE counts as
    read: the key reached the renderer either way."""
    try:
        return render(pattern, record), False
    except Exception:                                    # noqa: BLE001
        return None, True


def cmd_reads(args):
    """Which gate-record keys does `report.py` actually read? Mutate each and
    see whether the bytes move -- a measurement, not a reading of the source."""
    reads = {}
    raised = {}
    pats = patterns()
    for p in pats:
        base = render(p)
        rec = json.load(open(os.path.join(GATE, p + ".json")))
        for k in rec:
            m = copy.deepcopy(rec)
            m[k] = mutate(rec[k])
            md, boom = render_or_raised(p, m)
            if boom:
                raised.setdefault(k, []).append(p)
                reads.setdefault(k, []).append(p)
            elif md != base:
                reads.setdefault(k, []).append(p)
    print(f"MEASURED read set over {len(pats)} pattern(s) "
          f"(a key is 'read' when mutating it moves the rendered bytes):\n")
    for k in sorted(reads, key=lambda k: (-len(reads[k]), k)):
        flag = "  <-- ⚠ RUN-SCOPED" if k in RUN_SCOPED else ""
        if k in raised:
            flag += f"  [raised on {len(raised[k])}]"
        print(f"  {k:24s} {len(reads[k]):2d}/{len(pats)} pattern(s){flag}")
    unread = sorted(set(json.load(open(os.path.join(GATE, pats[0] + ".json"))))
                    - set(reads))
    print(f"\nnot read on {pats[0]}: {', '.join(unread)}")
    return 0


def cmd_selfref(args):
    """MUST BE ZERO. Does any run-scoped key reach the render?"""
    pats = patterns()
    bad = {}
    for p in pats:
        base = render(p)
        rec = json.load(open(os.path.join(GATE, p + ".json")))
        for k in RUN_SCOPED:
            if k not in rec:
                continue
            m = copy.deepcopy(rec)
            m[k] = mutate(rec[k])
            if render(p, m) != base:
                bad.setdefault(k, []).append(p)
    total = sum(len(v) for v in bad.values())
    for k, ps in sorted(bad.items()):
        print(f"  ⚠ `{k}` reaches the render on {len(ps)} pattern(s): "
              f"{', '.join(ps[:6])}{' …' if len(ps) > 6 else ''}")
    print(f"\nrun-scoped keys reaching the rendered table: {total} "
          f"(over {len(pats)} patterns x {len(RUN_SCOPED)} keys)")
    if total:
        print("SELFREF: FAIL -- `results/tables/*.md` is an input to its own\n"
              "checker (check.py stage 9c). See this file's docstring for the\n"
              "period-2 oscillation this causes, and fix `report.py`, not 9c.")
        return 1
    print("SELFREF: PASS -- the render is a function of committed sources only")
    return 0


def cmd_against(args):
    """Two draws of the same tree: does the RENDER move even though the gate
    records do? `DIR` holds a second sweep's `results/gate/*.json`."""
    other = os.path.abspath(args.against)
    same_file = same_render = n = 0
    for p in patterns():
        q = os.path.join(other, p + ".json")
        if not os.path.exists(q):
            continue
        n += 1
        a = open(os.path.join(GATE, p + ".json"), "rb").read()
        b = open(q, "rb").read()
        same_file += a == b
        same_render += render(p) == render(p, json.load(open(q)))
    print(f"{n} pattern(s) present in both draws")
    print(f"  gate record byte-identical : {same_file}/{n}")
    print(f"  RENDERED TABLE identical   : {same_render}/{n}")
    print("\nA whole-file pin on the gate record fires on its own gate run "
          f"for {n - same_file} of {n};\nre-rendering fires for {n - same_render}.")
    return 0 if same_render == n else 1


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--reads", action="store_true")
    g.add_argument("--selfref", action="store_true")
    g.add_argument("--against", metavar="DIR")
    a = ap.parse_args()
    try:
        if a.reads:
            return cmd_reads(a)
        if a.selfref:
            return cmd_selfref(a)
        return cmd_against(a)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
