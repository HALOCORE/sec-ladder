#!/usr/bin/env python3
"""p25 CONTROLS: **the MUST-FIRE arm for Miri, and the arm the `identity` pin
excludes.**

    python3 patterns/p25-realloc-growth/controls/rust_bug.py

`../spec.md`'s `miri.reason` says Miri finds NOTHING on the shipped
`../unsafe.rs`. ⚠ **Silence from a detector is worth nothing without an arm that
makes the same detector speak** (`.memory/03-measurement.md`; RECAP trap 5), so
this control runs the pair:

  * `../unsafe.rs`         -- the SHIPPED R4, which saves an INDEX.  Miri: CLEAN.
  * `arm_unsafe_ptr.rs`    -- the same file with the index replaced by a raw
                              INTERIOR POINTER taken from `toks.as_ptr()`, i.e.
                              `c/kernel.c`'s bug written in Rust.
                              Miri: **Undefined Behavior**.

⚠⚠ **AND IT SETTLES WHAT `../spec.md` IS ALLOWED TO CLAIM.** Unsafe Rust can
express p25's bug perfectly well -- this file proves it -- so the shipped R4's
index is **not** "Rust cannot say it". It is the `identity` pin: R4 must be the
same machine code as R5, R5 must verify, and Verus cannot license `*cur` because
the permission is unobtainable for a `Vec`'s buffer and because address equality
does not imply provenance equality. That is a claim about the PROOF rung, and
stating it as a claim about the language would be false.

⚠ Both arms are run under the SAME clamped input the gate's Miri stage uses:
`n_iters` rewritten to 4 (`harness/check.py::MIRI_PROBE_ITERS`), payload
untouched. Miri is an interpreter and 200000 iterations do not finish.
"""

import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
INDIR = os.path.join(PDIR, "inputs")
TMP = os.path.join(REPO, ".temp", "p25ctl")

NIGHTLY = "nightly-x86_64-unknown-linux-gnu"
MIRI_BIN = os.path.expanduser(f"~/.rustup/toolchains/{NIGHTLY}/bin/miri")
CARGO = os.path.expanduser("~/.cargo/bin/cargo")
PROBE_ITERS = 4
TIMEOUT = 900

ARMS = [("unsafe.rs", PDIR, False, "the SHIPPED R4: saves an INDEX"),
        ("arm_unsafe_ptr.rs", HERE, True,
         "the same file with a raw INTERIOR POINTER")]

INPUTS = ["adversarial-move.bin", "adversarial-lateread.bin",
          "adversarial-many.bin", "adversarial-nogrow.bin", "small.bin"]


def sysroot():
    r = subprocess.run([CARGO, f"+{NIGHTLY}", "miri", "setup",
                        "--print-sysroot"], capture_output=True, text=True,
                       timeout=TIMEOUT)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def probe_input(name):
    blob = open(os.path.join(INDIR, name), "rb").read()
    _n, decl = struct.unpack("<QQ", blob[:16])
    dst = os.path.join(TMP, f"miri_{name}")
    with open(dst, "wb") as f:
        f.write(struct.pack("<QQ", PROBE_ITERS, decl))
        f.write(blob[16:])
    return dst


def run_miri(src, cwd, blob, sr):
    env = dict(os.environ)
    env.pop("MIRIFLAGS", None)          # `check.py`'s configuration exactly
    env.pop("LD_PRELOAD", None)
    r = subprocess.run([MIRI_BIN, "--sysroot", sr, "--edition", "2021",
                        "-Zmiri-disable-isolation", src, "--", blob],
                       capture_output=True, text=True, timeout=TIMEOUT,
                       cwd=cwd, env=env)
    ub = ("Undefined Behavior" in r.stderr) or ("error: unsupported" in r.stderr)
    kind = None
    m = re.search(r"Undefined Behavior:\s*(.*)", r.stderr)
    if m:
        kind = " ".join(m.group(1).split())[:200]
    return {"exit": r.returncode, "ub": ub, "kind": kind,
            "stdout": r.stdout.strip(),
            "stderr_head": " ".join(r.stderr.split())[:400]}


def derived_from():
    out = {}
    for rel in ("patterns/p25-realloc-growth/unsafe.rs",
                "patterns/p25-realloc-growth/inputs/gen.py",
                "patterns/p25-realloc-growth/controls/arm_unsafe_ptr.rs",
                "patterns/p25-realloc-growth/controls/rust_bug.py",
                "common/driver.rs"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    problems, rows = [], []
    sr = sysroot() if os.path.exists(MIRI_BIN) else None
    if sr is None:
        print(f"rust_bug.py: miri not found at {MIRI_BIN} -- BLOCKED, not "
              f"failed (TOOLCHAIN.md).", file=sys.stderr)
        doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/"
                                     "controls/rust_bug.py"},
               "derived_from_sha256": derived_from(),
               "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                             time.gmtime()),
               "blocked": "miri not installed", "arms": [], "problems": []}
        json.dump(doc, open(os.path.join(HERE, "rust_bug.json"), "w"), indent=2)
        return 0

    for name in INPUTS:
        blob = probe_input(name)
        want_ub_input = name.startswith("adversarial-") and name != \
            "adversarial-nogrow.bin"
        for src, cwd, is_bug, what in ARMS:
            res = run_miri(os.path.join(cwd, src), cwd, blob, sr)
            rows.append(dict(source=src, input=name, **res))
            print(f"  {src:20s} {name:26s} ub={res['ub']!s:6s} "
                  f"exit={res['exit']!s:4s} out={res['stdout']!r} "
                  f"{res['kind'] or ''}")
            if not is_bug and res["ub"]:
                problems.append(
                    f"{src} on {name}: Miri reported UB on the SHIPPED unsafe "
                    f"rung. ../spec.md's miri.reason says it finds nothing. "
                    f"{res['stderr_head'][:200]}")
            if is_bug and want_ub_input and not res["ub"]:
                problems.append(
                    f"{src} on {name}: THE MUST-FIRE ARM DID NOT FIRE. Miri is "
                    f"then silent on both arms, and the shipped rung's silence "
                    f"means nothing -- do not quote ../spec.md's miri.reason "
                    f"until this fires again. exit={res['exit']}")
            if is_bug and not want_ub_input and res["ub"]:
                problems.append(
                    f"{src} on {name}: the interior-pointer arm reported UB on "
                    f"an input with no growth after the SAVE. That would make "
                    f"the arm fire on everything, which is the other way for a "
                    f"must-fire arm to be worthless")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "rust_bug.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "miri_probe_iters": PROBE_ITERS,
           "arms": rows,
           "problems": problems,
           "invariant": "Miri is SILENT on the shipped ../unsafe.rs on every "
                        "probed input, and reports Undefined Behavior on "
                        "arm_unsafe_ptr.rs -- the same file with the saved "
                        "index replaced by a raw interior pointer -- on exactly "
                        "the inputs whose windows grow the token vector after "
                        "the SAVE, and NOT on adversarial-nogrow or small. So "
                        "unsafe Rust CAN express p25's bug; what excludes it "
                        "from the shipped rung is the identity pin and Verus's "
                        "provenance, not the language."}
    out = os.path.join(HERE, "rust_bug.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
