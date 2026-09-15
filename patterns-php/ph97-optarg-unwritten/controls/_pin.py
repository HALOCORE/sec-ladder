#!/usr/bin/env python3
"""ph97 controls -- the staleness pin every `controls/*.json` in this row carries.

`harness/check.py::check_control_json_pins` (stage 9b) asks two questions of a
published sidecar: *were these numbers taken against THIS tree?* and *what did
the control CONCLUDE?* The second is `problems`; this file answers the first.

**`derived_from_sha256` is the key to prefer**, and the stage says why:
`gate_source_sha256` covers `patterns/*/*.md`, so pinning against it reports
`STALE` on a prose fix -- and a pin whose `STALE` does not mean *"the numbers are
wrong"* is a pin that gets switched off.

⚠⚠ **NO CONTROL IN THIS ROW PINS `NOTES.md`, DELIBERATELY.** Not one of them
derives a number from it: every figure `NOTES.md` quotes comes FROM a control,
not the other way round. Pinning it would make an editorial fix to a paragraph
turn the sidecars red, which is the failure mode the stage's own docstring names.

⚠ **PATHS ARE WRITTEN IN THE SHIM'S VIEW** -- `patterns/ph97-optarg-unwritten/...`,
not `patterns-php/...` -- because `check.py` re-hashes them relative to the REPO
it is running under, and `harness-php/gate.py` runs it under `.temp/php-root`
where `patterns-php/` is `patterns/`. A pin written the other way hashes nothing
and the stage reports every path ABSENT, which it SHOUTS rather than fails: a pin
that cannot be evaluated is the quietest way to have no pin at all.
"""

import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))
ROW = "patterns/ph97-optarg-unwritten"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def derived_from(rels):
    """`{shim-relative path: sha256}` for the row-relative paths in `rels`.

    ⚠ A path that does not exist is OMITTED rather than hashed as empty: the
    stage SHOUTS on an absent hashed path, which is the signal wanted, whereas
    `sha256(b"")` is a number that looks like evidence."""
    out = {}
    for rel in rels:
        p = os.path.join(PDIR, rel)
        if os.path.exists(p):
            out[f"{ROW}/{rel}"] = _sha(p)
    return out


def pin(rels, regenerate, note):
    """The two keys a sidecar in this row publishes, together."""
    return {"derived_from_sha256": derived_from(rels),
            "pin": {"regenerate": regenerate, "note": note}}
