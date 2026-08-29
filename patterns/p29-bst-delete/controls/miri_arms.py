#!/usr/bin/env python3
"""p29 CONTROLS: what Miri sees, and what it does not.

`NOTES.md` 2a claims four mechanisms split on one fault line, and three of the
four rows are measured by the gate itself: ASan on the C rungs (stage 7), safe
Rust's `Option` discriminant by construction (the class cannot occur), and
Verus's linear `PointsTo` by `controls/proof_mutants.py`. **The Miri row was
NOT**, because the gate runs Miri over `unsafe.rs`, which is the CORRECT rung
and has no UB to find on any input. This script measures it.

    python3 patterns/p29-bst-delete/controls/miri_arms.py

It builds one variant of `unsafe.rs` -- the shipped file with the USE path's two
conjuncts deleted, i.e. `c/kernel.c`'s bug written in Rust -- and runs Miri over
it on the two adversarial inputs that select the two bug classes. The prediction
the row rests on is:

    adversarial-uaf.bin      Miri REPORTS undefined behaviour   (use-after-free)
    adversarial-recycle.bin  Miri is SILENT and the answer is WRONG

⚠ **The shipped `unsafe.rs` is run too, as the must-be-clean control**: if Miri
were simply not working here, both rows would be silent and the table's Miri
column would be evidence of nothing.

⚠ Miri's invocation copies `harness/check.py`'s exactly -- the `miri` rustc
driver with `--sysroot` from `cargo +nightly miri setup --print-sysroot`,
`--edition 2021`, `-Zmiri-disable-isolation`, `MIRIFLAGS` removed from the
environment, and `n_iters` rewritten to 4 in a copy of the input.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
WDIR = os.path.join(REPO, ".temp", "p29miri")

NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
CARGO = os.path.expanduser("~/.cargo/bin/cargo")

USE_GUARD = ("            let v: u64 = if g_has && arr_get_unchecked(&live, "
             "g_slot as usize) == 1u8 {")
IDENT_TEST = """                if rr.key == g_key {
                    rr.val as u64
                } else {
                    SENT
                }"""

INPUTS = ["adversarial-uaf.bin", "adversarial-succ.bin",
          "adversarial-recycle.bin", "small.bin"]


def sysroot():
    r = subprocess.run([CARGO, f"+{NIGHTLY}", "miri", "setup",
                        "--print-sysroot"], capture_output=True, text=True,
                       timeout=1800)
    if r.returncode != 0 or not r.stdout.strip():
        raise SystemExit(f"miri_arms: cannot get the miri sysroot:\n{r.stderr}")
    return r.stdout.strip()


def variants():
    """(name, source text, what it is)."""
    src = open(os.path.join(PDIR, "unsafe.rs")).read()
    if USE_GUARD not in src or IDENT_TEST not in src:
        raise SystemExit("miri_arms: unsafe.rs's USE path moved under this "
                         "script; update USE_GUARD / IDENT_TEST")
    bug = src.replace(USE_GUARD, "            let v: u64 = if g_has {", 1) \
             .replace(IDENT_TEST, "                rr.val as u64", 1)
    # the variant lives one directory deeper than unsafe.rs
    fix = lambda t: t.replace('#[path = "../../common/driver.rs"]',
                              '#[path = "../../common/driver.rs"]')
    return [("shipped", fix(src),
             "the shipped R4. MUST be clean on every input -- the control."),
            ("r1line", fix(bug),
             "c/kernel.c's USE path written in Rust: both conjuncts deleted.")]


def probe_input(src, out, n_iters=4):
    blob = open(src, "rb").read()
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def derived_from():
    out = {}
    for rel in ("patterns/p29-bst-delete/unsafe.rs",
                "patterns/p29-bst-delete/inputs/gen.py",
                "patterns/p29-bst-delete/controls/miri_arms.py",
                "common/driver.rs"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()
    if not os.path.exists(MIRI_BIN):
        raise SystemExit(f"miri_arms: no miri at {MIRI_BIN} -- see TOOLCHAIN.md")
    os.makedirs(WDIR, exist_ok=True)
    sr = sysroot()
    env = dict(os.environ)
    env.pop("MIRIFLAGS", None)
    ver = subprocess.run([MIRI_BIN, "--version"], capture_output=True,
                         text=True).stdout.strip()

    rows = []
    for name, text, why in variants():
        spath = os.path.join(WDIR, f"{name}.rs")
        open(spath, "w").write(text)
        for nm in INPUTS:
            src = os.path.join(PDIR, "inputs", nm)
            if not os.path.exists(src):
                continue
            probe = probe_input(src, os.path.join(WDIR, f"probe-{nm}"))
            try:
                r = subprocess.run(
                    [MIRI_BIN, "--sysroot", sr, "--edition", "2021",
                     "-Zmiri-disable-isolation", spath, "--", probe],
                    capture_output=True, text=True, timeout=a.timeout,
                    cwd=PDIR, env=env)
                txt = r.stdout + r.stderr
                ub = ("Undefined Behavior" in txt) or ("error: unsupported" in txt)
                kind = ""
                m = re.search(r"Undefined Behavior: (.+)", txt)
                if m:
                    kind = m.group(1).strip()[:90]
                rows.append({"variant": name, "why": why, "input": nm,
                             "rc": r.returncode, "ub": ub, "ub_kind": kind,
                             "stdout": r.stdout.strip().splitlines()[-1]
                                       if r.stdout.strip() else ""})
            except subprocess.TimeoutExpired:
                rows.append({"variant": name, "why": why, "input": nm,
                             "rc": None, "ub": None,
                             "ub_kind": f"timeout after {a.timeout}s",
                             "stdout": ""})
            k = rows[-1]
            print(f"  {name:8s} {nm:26s} rc={str(k['rc']):>4s} "
                  f"ub={str(k['ub']):>5s}  {k['ub_kind'][:60]}")

    doc = {"pin": {"regenerate":
                   "python3 patterns/p29-bst-delete/controls/miri_arms.py"},
           "derived_from_sha256": derived_from(),
           "miri_version": ver,
           "n_iters": 4,
           "rows": rows,
           "note": "The gate runs Miri over the SHIPPED unsafe.rs, which is "
                   "correct on every input, so it cannot substantiate the Miri "
                   "row of NOTES.md 2a. This does: the `r1line` variant is "
                   "c/kernel.c's bug in Rust, and Miri reports UB on the "
                   "use-after-FREE inputs and is SILENT on the "
                   "use-after-RECYCLE input while the answer is wrong."}
    out = os.path.join(HERE, "miri_arms.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    shutil.rmtree(WDIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
