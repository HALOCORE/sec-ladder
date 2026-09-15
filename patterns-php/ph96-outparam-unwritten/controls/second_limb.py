#!/usr/bin/env python3
"""ph96 -- THE SECOND LIMB: what does `cf020f133487` NOT repair?

    python3 patterns-php/ph96-outparam-unwritten/controls/second_limb.py

=============================================================================
THE QUESTION, AND WHY IT IS A CONTROL AND NOT A GATE INPUT
=============================================================================
`zend_std_has_dimension` at `zend_object_handlers.c:427-429` calls the SAME
helper with the SAME output contract as `:512` and guards nothing, dereferencing
the `zend_execute_API.c:595` sentinel TWICE -- `:428 i_zend_is_true(retval)`
reads `op->type` at 0x14 and `:429 zval_ptr_dtor(&retval)` writes `refcount` at
0x10. **`cf020f133487` does not touch it.**

⛔⛔ **SO AN INPUT CARRYING THAT STATE FAULTS IN R1h AS WELL AS IN R1**, and
`harness/check.py` stage 7h FAILS a row whose R1h fires a sanitizer on ANY input,
adversarial included -- *"R1h is the arm that carries the check, so it is
expected clean on EVERY input"*. ▶ **That is why `inputs/` carries no
`adversarial-exists.bin` and this file exists instead.** The state is built here,
driven through all six rungs, and recorded.

⚠⚠ **THE SCOPE OF THE CLAIM, AND IT IS NARROW.** *No repair for this limb exists
in the 163-patch screened corpus cache on this box* is a result about THE CACHE
(`RECAP_PHP.md` F10: a negative is a result). *Upstream never fixed it* is a
claim this box cannot support: there is no network here and the cache is not
php-src's history. This file re-derives the cache half and says nothing about the
other.

▶ **WHAT THE ROW CONCLUDES FROM IT** is in `../NOTES.md` section 5, not here:
`PROTOCOL_PHP.md` C says an upstream fix is not automatically correct and that
measuring one which leaves a reachable fault in the arm it does not guard is a
result to report and not to repair.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "common-php"))
import _pin  # noqa: E402
import slb  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php96", "limb")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VERUS = os.path.join(REPO, "verus_run.py")
PATCHES = os.path.join(REPO, ".temp", "mgr", "batch", "patches")

STRIDE = 118
SHAPES = {"read": 0, "write": 1, "exists": 2, "unset": 3}


def _rec(rng, shape, failed, wrote, ty=0, lval=0, slen=0):
    """One 16-byte record, residues written directly. Mirrors inputs/gen.py."""
    b0 = shape + 4 * rng.randrange(0, 63)
    b1 = (0 if failed else rng.randrange(1, 5)) + 5 * rng.randrange(0, 51)
    b2 = (0 if not wrote else rng.randrange(1, 3)) + 3 * rng.randrange(0, 84)
    b3 = ty + 4 * rng.randrange(0, 63)
    b5 = slen + 11 * rng.randrange(0, 23)
    pad = bytes(rng.randrange(1, 256) for _ in range(10 - slen))
    return bytes((b0, b1, b2, b3, lval & 0xFF, b5)) + b"z" * slen + pad


def make_input(path, shape):
    """One window, one sentinel record at `shape`, benign filler after it."""
    rng = random.Random(0x5EC1ADDE + 7)
    nrec, tail = STRIDE // 16, STRIDE % 16
    body = _rec(rng, SHAPES[shape], False, False)
    body += b"".join(_rec(rng, i % 4, False, True, 3, 1, 2)
                     for i in range(nrec - 1))
    body += bytes(rng.randrange(1, 256) for _ in range(tail))
    slb.write(path, 64, slb.pack_head1_bytes(STRIDE, body), None)


def build_all():
    """The six rungs, O3 isolated, in EQUAL-LENGTH build directories (F101)."""
    os.makedirs(SCRATCH, exist_ok=True)
    cdir = os.path.join(SCRATCH, "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))
    exes = {}
    for i, (cell, src) in enumerate((("c-gcc", "kernel.c"),
                                     ("c-gcc-h", "kernel_hardened.c"))):
        d = os.path.join(SCRATCH, f"v{i:02d}")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        out = os.path.join(d, "k")
        subprocess.run(["gcc", "-std=c99", "-O1", "-g", "-Wall", "-Wextra",
                        "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
                        "-I", os.path.join(PDIR, "c"),
                        os.path.join(REPO, "common", "driver.c"),
                        os.path.join(PDIR, "c", src),
                        os.path.join(PDIR, "c", "main.c"), "-o", out],
                       check=True, capture_output=True)
        exes[cell] = out
    for i, rung in enumerate(("safe_naive", "safe_tuned", "unsafe"), start=2):
        d = os.path.join(SCRATCH, f"v{i:02d}")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        out = os.path.join(d, "k")
        subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", "opt-level=3", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated",
                        os.path.join(PDIR, rung + ".rs"), "-o", out],
                       check=True, capture_output=True)
        exes[rung] = out
    d = os.path.join(SCRATCH, "v05")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    out = os.path.join(d, "k")
    subprocess.run([sys.executable, VERUS, "--compile",
                    os.path.join(PDIR, "verus.rs"), "--cfg", "slb_isolated",
                    "-C", "opt-level=3", "-C", "codegen-units=1",
                    "-C", "debug-assertions=off", "-o", out],
                   check=True, capture_output=True, cwd=REPO)
    exes["verus"] = out
    assert len({len(os.path.dirname(p)) for p in exes.values()}) == 1, (
        "the six build directories must have EQUAL PATH LENGTHS (F101)")
    return exes


def run(exe, inp, shim):
    env = dict(os.environ, LD_PRELOAD=shim)
    r = subprocess.run([exe, inp], capture_output=True, text=True, env=env,
                       timeout=300)
    addr = re.search(r"si_addr=(\S+)", r.stderr or "")
    return {"exit": r.returncode, "stdout": r.stdout.strip(),
            "si_addr": addr.group(1) if addr else None}


def cache_search():
    """Which cached patches touch either limb, BY DIFF BODY.

    ⚠⚠ **NOT BY THE `@@ ... @@` HUNK-HEADER LABEL**, which names the function
    the hunk STARTS AFTER and not the function it touches -- that misreading made
    `235e6c0afe1d` look like an `unset_dimension` repair when it is a
    `call_user_call` one. ⚠ And never a COMPOUND grep: a hit on `A|B` attributed
    to `A` is how the manager's own first pass went wrong. Each token is searched
    separately."""
    out = {"offsetunset": [], "offsetexists": []}
    if not os.path.isdir(PATCHES):
        return {"error": f"no patch cache at {PATCHES}", **out}
    files = sorted(f for f in os.listdir(PATCHES) if f.endswith(".patch"))
    out["patches_scanned"] = len(files)
    for f in files:
        txt = open(os.path.join(PATCHES, f), encoding="latin-1").read()
        # diff BODY only: the +/- lines, never the hunk header or the subject.
        body = "\n".join(l for l in txt.splitlines()
                         if (l.startswith(("+", "-"))
                             and not l.startswith(("+++", "---"))))
        for tok in ("offsetunset", "offsetexists"):
            if tok in body:
                out[tok].append(f)
    return out


def main():
    problems = []
    os.makedirs(SCRATCH, exist_ok=True)
    shim = os.path.join(SCRATCH, "segaddr.so")
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", shim,
                    os.path.join(REPO, ".tasks-php", "probes", "segaddr.c")],
                   check=True, capture_output=True)
    inputs = {}
    for shape in ("exists", "unset", "read", "write"):
        p = os.path.join(SCRATCH, f"sent-{shape}.bin")
        make_input(p, shape)
        inputs[shape] = p

    exes = build_all()
    rec = {"problems": problems, "build": "O1 -g for C, O3 isolated for Rust",
           "note": ("every cell is driven on the SAME four one-window inputs, "
                    "each carrying one SUCCESS-with-nothing-written record at "
                    "the named shape"),
           "cells": {}}
    order = ["c-gcc", "c-gcc-h", "safe_naive", "safe_tuned", "unsafe", "verus"]
    print(f"{'cell':12s} " + " ".join(f"{s:>22s}" for s in inputs))
    for cell in order:
        rec["cells"][cell] = {}
        row = []
        for shape, p in inputs.items():
            r = run(exes[cell], p, shim)
            rec["cells"][cell][shape] = r
            row.append(f"rc={r['exit']} {r['si_addr'] or 'ok':>10s}")
        print(f"{cell:12s} " + " ".join(f"{c:>22s}" for c in row))

    # ---- the verdicts ----------------------------------------------------
    def faulted(cell, shape):
        return rec["cells"][cell][shape]["exit"] not in (0,)

    rec["verdict"] = {
     "unset_limb_repaired_by_cf020f133487":
        faulted("c-gcc", "unset") and not faulted("c-gcc-h", "unset"),
     "exists_limb_repaired_by_cf020f133487":
        faulted("c-gcc", "exists") and not faulted("c-gcc-h", "exists"),
     "exists_limb_faults_in_both_c_rungs":
        faulted("c-gcc", "exists") and faulted("c-gcc-h", "exists"),
     "no_rust_rung_faults_on_either_limb":
        not any(faulted(c, s) for c in order[2:] for s in ("unset", "exists")),
    }
    print()
    for k, v in rec["verdict"].items():
        print(f"  {k:44s} {v}")
    if not rec["verdict"]["unset_limb_repaired_by_cf020f133487"]:
        problems.append("R1 does not fault at the unset limb, or R1h does -- "
                        "the row's own R1h claim is not reproduced")
    if not rec["verdict"]["exists_limb_faults_in_both_c_rungs"]:
        problems.append("the exists limb does NOT fault in both C rungs, so "
                        "spec.md's incompleteness claim is wrong and NOTES.md "
                        "section 5 must be rewritten")
    a = rec["cells"]["c-gcc"]["unset"]["si_addr"]
    b = rec["cells"]["c-gcc"]["exists"]["si_addr"]
    rec["fault_addresses"] = {"unset": a, "exists": b}
    if a != "0x10" or b != "0x14":
        problems.append(f"the two limbs fault at {a} and {b}, not at "
                        f"offsetof(zval, refcount)=0x10 and "
                        f"offsetof(zval, type)=0x14 -- an address that is "
                        f"NEITHER is a DIFFERENT bug and must not be filed here")

    # ---- the cache half, with its scope ---------------------------------
    rec["cache"] = cache_search()
    print(f"\n163-patch cache, searched by diff BODY (never by the @@ label, "
          f"never compound):")
    print(f"  patches scanned            : {rec['cache'].get('patches_scanned')}")
    print(f"  bodies mentioning offsetunset : {rec['cache']['offsetunset']}")
    print(f"  bodies mentioning offsetexists: {rec['cache']['offsetexists']}")
    print("  ⚠ SCOPE: this is THE SCREENED CORPUS CACHE ON THIS BOX, not "
          "php-src's history.")
    print("    `no repair in the cache` is a result; `upstream never fixed it` "
          "is not supported here.")
    if rec["cache"].get("offsetunset") != ["cf020f133487.patch"]:
        problems.append(f"the cache's offsetunset repair is "
                        f"{rec['cache'].get('offsetunset')}, not uniquely "
                        f"cf020f133487 -- spec.md names that commit as R1h")
    if rec["cache"].get("offsetexists"):
        problems.append(f"the cache DOES carry a patch touching offsetexists "
                        f"({rec['cache']['offsetexists']}); NOTES.md section 5 "
                        f"says it does not and must be corrected")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "safe_naive.rs",
                         "safe_tuned.rs", "unsafe.rs", "verus.rs"],
                        "python3 controls/second_limb.py",
                        "six builds (one through Verus) and 24 runs; minutes"))
    with open(os.path.join(HERE, "second_limb.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/second_limb.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
