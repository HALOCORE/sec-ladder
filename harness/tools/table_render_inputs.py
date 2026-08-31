#!/usr/bin/env python3
"""What does `results/tables/*.md` actually depend on? Measure it; don't read it.

    python3 harness/tools/table_render_inputs.py --reads     # the MEASURED read set
    python3 harness/tools/table_render_inputs.py --selfref   # MUST-BE-ZERO check
    python3 harness/tools/table_render_inputs.py --selftest  # the MUST-FIRE arm
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
it is ever non-zero again.

⚠⚠ **AND UNTIL TASK_151 IT DID THAT WITH A HAND-WRITTEN DENY-LIST, WHICH IS THE
ONE SHAPE THIS PARTICULAR CHECK MUST NOT HAVE.** `TASK_132` (`RECAP` finding
46 (iii), `.memory/03-measurement.md` entry 11) measured the hole: the tuple
named **9** keys, the gate record has **34**, so **25 were unclassified** -- and
a `report.py` rendering `table_render`, which is **stage 9c's own verdict about
this very table**, measured `26/26 READ` while `--selfref` printed `0` and
exited `PASS`. **This project's most-named failure, inside the detector built to
prevent it.**

> ⚠⚠⚠ **A DETECTOR FOR A SELF-REFERENCE THAT IS ITSELF ENUMERATED BY HAND CAN
> ONLY FIND THE SELF-REFERENCES YOU ALREADY THOUGHT OF.**

✅ **So `--selfref` is now a CENSUS OVER AN ALLOW-LIST.** It mutates **every key
the record actually has** -- not a list written here -- and any key that moves
the rendered bytes and is **not** in `READ_OK` is a violation. Adding a key to
the gate record can therefore no longer widen the blind spot, because an
undeclared key defaults to *forbidden* rather than to *unclassified*. The four
allow-listed keys are the read set `TASK_127` established **by mutation**, and
they are re-measured on every run rather than assumed: `--selfref` prints which
of them were actually read.

⚠ **`READ_OK` is small on purpose and widening it is a design decision, not
bookkeeping** -- see its own comment for the test a candidate must pass.

## `--selftest` is the must-fire arm, and it exists because of the above

**A forward-only fix is one somebody later "confirms" by finding nothing.**
`--selftest` plants the exact reproduction `TASK_132` used -- a `report.py`
whose render includes the gate record's `table_render` -- and drives **four
cells, two per detector**:

    PLANTED    census  -> MUST FAIL   <- the repair
    PLANTED    legacy  -> MUST PASS   <- the defect, reproduced
    UNPLANTED  census  -> MUST PASS   <- must-not-fire control
    UNPLANTED  legacy  -> MUST PASS

⚠ **A cell that RAISES is reported as a failed cell with its exception text, not
allowed to crash the arm**: a crash and a firing are different failure modes and
only one of them says what happened (`.memory/03-measurement.md` entry 19).

## Placement

`harness/tools/` is **outside** the gate digest -- `check.py`'s `srcs` globs
`harness/*.py` non-recursively (TASK_125) -- so this file costs no gate sweep to
maintain. ⚠ **It must never be imported by `check.py`, `measure.py` or
`build.py`**, or the digest would silently stop covering a file that decides a
verdict. Stage 9c therefore re-implements nothing from here; it calls
`report.build` directly, which is the same function this tool calls.
"""

import argparse
import contextlib
import copy
import json
import os
import shutil
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
import report  # noqa: E402

GATE = os.path.join(REPO, "results", "gate")
SCRATCH = os.path.join(REPO, ".temp", "table_render_inputs")

#: ⚠⚠ **THE ALLOW-LIST, AND IT IS THE WHOLE VERDICT (TASK_151).** A gate-record
#: key `report.py` may read. Every other key -- including one added to the
#: record tomorrow -- is a violation if mutating it moves the rendered bytes.
#:
#: The test a candidate must pass before it is added here, and it is
#: `.memory/03-measurement.md` entry 11's rule rather than a preference:
#: **the key must be a deterministic function of the COMMITTED SOURCES, not of
#: the run.** These four are:
#:
#:   contract_sha256  sha256 of the `slb-contract` block in spec.md
#:   controls_json    stage 9b's re-hash of each committed `controls/*.json`
#:   idiom_audit      stage 0b's spelling audit over the rungs and the contract
#:   loud             the `rep.shout` list -- shouts are about the SOURCES
#:
#: ⚠ `loud` is the one to think hardest about, and it is in because a shout is
#: raised by a property of the tree; it is NOT in because "shouts do not fail".
#: `verdict`, `blocked`, `failures`, `table_render`, `sanitizer`, `miri` and
#: `notes` are all functions of the RUN and none may ever be added.
READ_OK = ("contract_sha256", "controls_json", "idiom_audit", "loud")

#: ⚠ **HISTORICAL, AND IT DECIDES NOTHING.** The hand-written deny-list this
#: tool used from TASK_127 to TASK_151. It is kept for exactly one purpose --
#: `--selftest` shows it PASSING on the plant the census FAILS, which is the
#: reproduction of `RECAP` finding 46 (iii). Nothing else may read it.
_LEGACY_RUN_SCOPED = ("verdict", "blocked", "failures", "invocation",
                      "complete_run", "notes", "sanitizer", "miri",
                      "adversarial")

#: A value no record uses, so substituting it always counts as a mutation.
SENTINEL = "__slb_probe_sentinel__"


def patterns():
    return sorted(f[:-5] for f in os.listdir(GATE) if f.endswith(".json"))


def _resolve(pat):
    """`p03` -> `p03-bounded-stack`; a full name passes through."""
    hits = [p for p in patterns() if p == pat or p.startswith(pat + "-")]
    if len(hits) != 1:
        raise SystemExit(f"table_render_inputs.py: {pat!r} matches "
                         f"{hits or 'nothing'} in results/gate/")
    return hits[0]


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


def measure_reads(pats, keys=None):
    """`(reads, raised, ncells)` -- **the census**.

    `reads[key]` is the list of patterns on which mutating `key` moves the
    rendered bytes. ⚠ **The key set is taken from each RECORD, not from a list
    in this file**, which is the whole of TASK_151's repair: a key added to the
    gate record joins the measurement automatically instead of joining a blind
    spot. `keys` restricts it, and the only caller that passes one is
    `--selftest`'s reproduction of the old deny-list."""
    reads, raised, ncells = {}, {}, 0
    for p in pats:
        base = render(p)
        rec = json.load(open(os.path.join(GATE, p + ".json")))
        for k in (rec if keys is None else [k for k in keys if k in rec]):
            m = copy.deepcopy(rec)
            m[k] = mutate(rec[k])
            md, boom = render_or_raised(p, m)
            ncells += 1
            if boom:
                raised.setdefault(k, []).append(p)
                reads.setdefault(k, []).append(p)
            elif md != base:
                reads.setdefault(k, []).append(p)
    return reads, raised, ncells


def violations(reads):
    """The read keys the allow-list does not permit. `{key: [pattern, ...]}`."""
    return {k: v for k, v in reads.items() if k not in READ_OK}


def cmd_reads(args):
    """Which gate-record keys does `report.py` actually read? Mutate each and
    see whether the bytes move -- a measurement, not a reading of the source."""
    pats = patterns()
    reads, raised, _ = measure_reads(pats)
    print(f"MEASURED read set over {len(pats)} pattern(s) "
          f"(a key is 'read' when mutating it moves the rendered bytes):\n")
    for k in sorted(reads, key=lambda k: (-len(reads[k]), k)):
        flag = "" if k in READ_OK else "  <-- ⚠ NOT ALLOW-LISTED"
        if k in raised:
            flag += f"  [raised on {len(raised[k])}]"
        print(f"  {k:24s} {len(reads[k]):2d}/{len(pats)} pattern(s){flag}")
    unread = sorted(set(json.load(open(os.path.join(GATE, pats[0] + ".json"))))
                    - set(reads))
    print(f"\nnot read on {pats[0]}: {', '.join(unread)}")
    return 0


def cmd_selfref(args):
    """MUST BE ZERO. Does any key `READ_OK` does not permit reach the render?

    ⚠ **A CENSUS, NOT A DENY-LIST** -- see the module docstring and `READ_OK`.
    Every key each record actually carries is mutated, so a key nobody has
    classified counts as forbidden rather than as invisible."""
    pats = patterns()
    reads, _, ncells = measure_reads(pats)
    bad = violations(reads)
    total = sum(len(v) for v in bad.values())
    for k, ps in sorted(bad.items()):
        print(f"  ⚠ `{k}` reaches the render on {len(ps)} pattern(s): "
              f"{', '.join(ps[:6])}{' …' if len(ps) > 6 else ''}")
    print(f"\nallow-listed keys measured READ: "
          + ", ".join(f"{k} {len(reads.get(k, []))}/{len(pats)}"
                      for k in READ_OK))
    print(f"forbidden keys reaching the rendered table: {total} "
          f"(census of {ncells} (pattern, key) cell(s) over {len(pats)} "
          f"pattern(s); allow-list {list(READ_OK)})")
    if total:
        print("SELFREF: FAIL -- `results/tables/*.md` is an input to its own\n"
              "checker (check.py stage 9c). See this file's docstring for the\n"
              "period-2 oscillation this causes, and fix `report.py`, not 9c.")
        return 1
    print("SELFREF: PASS -- the render is a function of committed sources only")
    return 0


# --- the must-fire arm -----------------------------------------------------

@contextlib.contextmanager
def _rendering_key(key):
    """Temporarily give `report.build` the defect: it appends the gate record's
    `key` to the markdown it returns.

    This is `TASK_132`'s reproduction, not an approximation of it -- the record
    is read through `report.gate_record`, the same function the real renderer
    uses, out of the same scratch tree `render()` substitutes into."""
    orig = report.build

    def planted(doc, name, gate=None):
        out = orig(doc, name, gate)
        rec = report.gate_record(doc["pattern"], gate) or {}
        return out + f"\n<!-- {key}: {rec.get(key)!r} -->\n"

    report.build = planted
    try:
        yield
    finally:
        report.build = orig


def _cell(label, want, fn):
    """Run one arm cell. ⚠ **An exception becomes a REPORTED failure**, never a
    crash: `.memory/03-measurement.md` entry 19's correction to `p32`'s own
    `detector_selftest`, where three of four planted mutations failed by
    crashing and the diagnostic was lost."""
    try:
        got = fn()
        note = ""
    except Exception:                                    # noqa: BLE001
        got = "RAISED"
        note = "    " + traceback.format_exc().strip().splitlines()[-1]
    ok = (got == want)
    print(f"  {'ok  ' if ok else 'FAIL'} {label:52s} want {want:4s} got {got}")
    if note:
        print(note)
    return ok


def cmd_selftest(args):
    """The MUST-FIRE arm for `--selfref`. Four cells, two per detector."""
    pats = args.selftest or patterns()[:3]
    pats = [_resolve(p) for p in pats]
    print(f"must-fire arm for `--selfref`, over {len(pats)} pattern(s): "
          f"{', '.join(pats)}\n")
    print("PLANT: a `report.py` whose render appends the gate record's "
          "`table_render`\n       -- stage 9c's OWN VERDICT about this very "
          "table (RECAP finding 46 (iii)).\n")

    def census():
        return "FAIL" if violations(measure_reads(pats)[0]) else "PASS"

    def legacy():
        reads, _, _ = measure_reads(pats, keys=_LEGACY_RUN_SCOPED)
        return "FAIL" if reads else "PASS"

    ok = []
    with _rendering_key("table_render"):
        ok.append(_cell("PLANTED   census  (the TASK_151 repair)", "FAIL",
                        census))
        ok.append(_cell("PLANTED   legacy deny-list (the DEFECT)", "PASS",
                        legacy))
    ok.append(_cell("UNPLANTED census  (must-not-fire control)", "PASS",
                    census))
    ok.append(_cell("UNPLANTED legacy deny-list", "PASS", legacy))

    print(f"\n{sum(ok)}/{len(ok)} cell(s) as designed")
    if all(ok):
        print("SELFTEST: PASS -- the census fires on a plant the hand-written\n"
              "deny-list passes, and neither fires on the shipped report.py.")
        return 0
    print("SELFTEST: FAIL -- `--selfref` is not known to be able to fire. Do "
          "not\ntrust a `SELFREF: PASS` until this is green again.")
    return 1


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
    g.add_argument("--selftest", nargs="*", metavar="PATTERN",
                   help="the must-fire arm; default: the first 3 patterns")
    g.add_argument("--against", metavar="DIR")
    a = ap.parse_args()
    try:
        if a.reads:
            return cmd_reads(a)
        if a.selfref:
            return cmd_selfref(a)
        if a.selftest is not None:
            return cmd_selftest(a)
        return cmd_against(a)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
