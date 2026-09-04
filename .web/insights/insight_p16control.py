#!/usr/bin/env python3
"""insight_p16control.py — the drift guard for the deleted-check control.

    python3 insights/insight_p16control.py          # write data/insights/p16control.json
    python3 insights/insight_p16control.py --print  # show every guard's verdict
    python3 insights/insight_p16control.py --check  # verify only; write nothing

WHY THIS EXISTS, AND WHY IT IS NOT `p16_control.py --check`.

`insights/p16_control.py` rebuilds the whole five-rung experiment from the
parent's shipped sources and re-runs it, Verus included, in about seven seconds.
That is the right thing to run when you want to know whether the RESULT still
holds, and `--check` diffs it against the committed JSON.

It is the wrong thing to run on every `build_data.py` invocation: it invokes
rustc, two C compilers and a prover, and `build_data.py` is a one-second command
people run constantly.  So this file is the cheap half.  It re-hashes the shipped
sources the control was derived from and asserts they have not moved.  If one
has, the note is withheld, this script exits non-zero, and `build_data.py` turns
that into a warning the Method tab renders — pointing at the expensive script.

The division is the same one `asm_extract.py` and `asm_for()` already use in this
repository: extract from scratch, commit the result, record the digest that lets
a later build notice the evidence moved underneath it.  A digest check cannot
tell you the outcome changed; it tells you the outcome is no longer known to
describe the code that is there, which is the only claim a cheap guard can make
honestly.

⚠ WHAT THIS GUARD DOES **NOT** ASSERT.  It does not re-run anything, so it cannot
catch a change of behaviour with no change of source — a toolchain bump, a libc
change, a different box.  The committed JSON carries its own caveat about that:
the plain-C and unsafe-Rust rows are undefined behaviour by construction and
their determinism is a property of this machine.  For those, only
`p16_control.py --check` is evidence, and a drift there is a report about the
machine rather than about the claim.
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
REPO = os.path.dirname(WEB)

CACHE = os.path.join(HERE, "p16control.json")

# Where each recorded source lives.  `p16_control.py` records pattern-relative
# paths for the pattern's own files and repo-relative ones for the shared driver
# and the harness, so resolution has to try both roots rather than guess.
ROOTS = (os.path.join(REPO, "patterns", "p16-tlv-walk"), REPO)


def _resolve(rel: str):
    for root in ROOTS:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            return p
    return None


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def guards(cache: dict):
    """Yield (name, ok, why).  `why` is reported either way, so `--print`
    doubles as a description of what is currently believed and why."""
    srcs = cache.get("sources") or {}
    if not srcs:
        yield ("sources recorded", False, "p16control.json records no source digests")
        return

    moved, missing, checked = [], [], 0
    for rel, rec in sorted(srcs.items()):
        want = (rec or {}).get("sha256")
        path = _resolve(rel)
        if path is None:
            missing.append(rel)
            continue
        checked += 1
        if _sha256(path) != want:
            moved.append(rel)

    yield ("every recorded source still present", not missing,
           f"{checked} resolved"
           + (f"; MISSING {', '.join(missing)}" if missing else ""))
    yield ("every recorded source unchanged", not moved,
           f"{checked} digests match"
           if not moved else
           f"MOVED: {', '.join(moved)} — re-run `python3 insights/p16_control.py`")

    # The control is only interesting because the two Verus runs disagree.  If a
    # future edit made them agree, the row that carries the section's whole point
    # would be silently gone.
    v = cache.get("verus") or {}
    ctl, mut = v.get("verus") or {}, v.get("nocheck-verus") or {}
    ok = (ctl.get("errors") == 0 and mut.get("errors", 0) > 0)
    yield ("the proved rung still rejects the deletion", ok,
           f"shipped {ctl.get('verified')} verified / {ctl.get('errors')} errors; "
           f"mutant {mut.get('verified')} verified / {mut.get('errors')} errors")


def main() -> int:
    argv = sys.argv[1:]
    verbose = "--print" in argv or "--check" in argv

    if not os.path.exists(CACHE):
        print("p16control: no insights/p16control.json — run "
              "`python3 insights/p16_control.py` first", file=sys.stderr)
        return 1

    with open(CACHE, encoding="utf-8") as fh:
        cache = json.load(fh)

    results, failed = [], []
    for name, ok, why in guards(cache):
        results.append({"guard": name, "ok": ok, "why": why})
        if not ok:
            failed.append(f"{name} — {why}")
        if verbose:
            print(f"  [{'ok ' if ok else 'FAIL'}] {name}: {why}")

    note = None
    if not failed:
        # The note is emitted only while every guard holds.  It states what the
        # committed JSON licenses and nothing beyond it — in particular it does
        # NOT say the control is gate-certified, because the parent repo's gate
        # does not run it.
        note = ("The deleted-check control is reproducible from a committed "
                "generator: `insights/p16_control.py` rebuilds all five rungs "
                "from the pattern's shipped sources, deletes the one bounds "
                "test, and re-runs them. It is certified by no gate.")

    out = {"note": note, "guards": results,
           "generated_utc": cache.get("generated_utc"),
           "pattern": cache.get("pattern")}

    if "--check" not in argv and "--print" not in argv:
        d = os.path.join(WEB, "data", "insights")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "p16control.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)

    if failed:
        print("p16control: note WITHHELD — " + "; ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
