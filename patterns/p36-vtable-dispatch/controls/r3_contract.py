#!/usr/bin/env python3
"""Is an R3-side control IN CONTRACT? Checked with the GATE'S OWN oracle.

Built at TASK_073 for TASK_072_REVIEW B1. p36 published `R3 - R4 = +15.00 flat`
having pulled exactly one R3-side lever, and that lever moved R3 the DEARER way.
The review found a cheaper in-contract R3 (`gen_controls.py::c_r3_window`), so
what p36 owes beside its headline is an R3-side span whose members are shown to
be inside the declaration -- not asserted to be.

⚠ **The point of this file is that it does not re-implement the matching rule.**
It imports `harness/check.py::spelling_matches`, the definition the gate is
selftested on at stage 0 and which is hashed into `source_sha256`, and it pulls
the spellings out of `../spec.md`'s `slb-contract` block rather than out of a
list here. A control that passes this file passes the same test the shipped
rungs pass. What the gate itself does NOT do -- and neither does this -- is
decide an entry's POLARITY or the SET OF RUNGS it scopes to; those live in the
entry's English (`check.py::spelling_matches`'s own docstring). So this file
reports each control **against the shipped R3**: what is meaningful is
DIVERGENCE, i.e. a spelling the shipped rung matches and the control does not,
or a `forbidden` span the control hits.

    python3 patterns/p36-vtable-dispatch/controls/r3_contract.py
    python3 patterns/p36-vtable-dispatch/controls/r3_contract.py r3_window
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)
import check as checkmod       # noqa: E402
import gen_controls as gc      # noqa: E402

#: The R3-side controls this file audits: every control derived from the shipped
#: R3, i.e. the members of the R3-side span.
R3_CONTROLS = ["r3_window", "r3_hdr4", "r3_iter", "r3_idx"]


def contract():
    text = open(os.path.join(PDIR, "spec.md")).read()
    block = text.split("```slb-contract", 1)[1].split("```", 1)[0]
    return json.loads(block)


def rust_spellings(entries):
    """[(index, spelling)] for every backticked span of every entry that scopes
    to Rust -- a plain string, or the `rust` key of a per-language object."""
    out = []
    for i, e in enumerate(entries):
        text = e if isinstance(e, str) else e.get("rust", "")
        for tok in checkmod._TICK.findall(text):
            out.append((i, tok))
    return out


def main():
    c = contract()
    idiom = c.get("idiom", {})
    req = rust_spellings(idiom.get("required", []))
    forb = rust_spellings(idiom.get("forbidden", []))
    shipped = open(os.path.join(PDIR, "safe_tuned.rs")).read()
    names = sys.argv[1:] or R3_CONTROLS
    rc = 0
    for name in names:
        src = gc.CONTROLS[name][1]()
        print(f"=== {name}  ({len(req)} required rust spelling(s), "
              f"{len(forb)} forbidden)")
        div = 0
        for i, tok in req:
            a = checkmod.spelling_matches(tok, src, "rust")
            b = checkmod.spelling_matches(tok, shipped, "rust")
            flag = "" if a == b else "   <-- DIVERGES FROM THE SHIPPED R3"
            if a != b:
                div += 1
            print(f"  required[{i}] {tok!r:45s} control={a!s:5s} shipped={b!s:5s}{flag}")
        hits = 0
        for i, tok in forb:
            a = checkmod.spelling_matches(tok, src, "rust")
            if a:
                hits += 1
            print(f"  forbidden[{i}] {tok!r:44s} hit={a}")
        # `unsafe` is not a `forbidden` entry -- it is what makes a rung an R4 --
        # so an R3 control is checked for it separately, on exec code only.
        uns = re.search(r"\bunsafe\b", checkmod.exec_code(src, "rust")) is not None
        print(f"  divergences from the shipped R3: {div}   forbidden hits: {hits}"
              f"   `unsafe` in exec code: {uns}")
        if div or hits or uns:
            rc = 1
    print("\nOUT OF CONTRACT" if rc else "\nevery control above is in contract "
          "by the gate's own matcher")
    return rc


if __name__ == "__main__":
    sys.exit(main())
