#!/usr/bin/env python3
"""ph97 — what does `Option<&[u8; 21]>` COST? P1's falsifier, decomposed.

    python3 patterns-php/ph97-optarg-unwritten/controls/optional_cost.py

=============================================================================
THE QUESTION, AND WHY THE RECORD ALONE CANNOT ANSWER IT
=============================================================================
The row's headline is that **the null-as-absent idiom is the cheapest thing C
does that Rust deletes outright**: `Option<&T>` is the null-pointer-optimised
layout, so the safety is a REPRESENTATION rather than a TEST. Every Rust rung
carries the size assertion, so the *bytes* half is checked at compile time.

⚠⚠ **THE RUNTIME HALF IS NOT VISIBLE IN THE MEASUREMENT RECORD**, and quoting
the R3→R4 step for it would be wrong. R4 removes **seven** checks, of which the
optional's discriminant is **one**; the other six are array and slice bounds
that have nothing to do with this row. A reader handed the R3→R4 step and told
it is *the optional's cost* has been handed six other things as well — which is
`RECAP_PHP.md` F83's shape, *attributing a whole difference to one named cause*.

▶ **So this control isolates it.** Two builds of `unsafe.rs`, differing in
exactly one function body:

    v00   `opt_get` is `unsafe { t.unwrap_unchecked() }`   — as shipped
    v01   `opt_get` is `t.unwrap()`                        — CHECKED, and
                                                             nothing else moves

Everything else — the six other unchecked accessors, the fold, the parser — is
identical text. **The A1 difference between them IS the discriminant test, and
nothing else is in it.**

⚠ The two build directories are fixed-width `vNN` and asserted equal in length
(`RECAP_PHP.md` F101 / item 109: the kernel fingerprint is path-sensitive and
has fired live in both directions on this project).

⚠ `inside_share` is reported for both, because a difference that lands outside
the measured symbol is a difference family A1 cannot see (F119).
"""

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php97", "optcost")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")

UNCHECKED = """fn opt_get(t: Option<&[u8; NTYP]>) -> &[u8; NTYP] {
    unsafe { t.unwrap_unchecked() }
}"""
CHECKED = """fn opt_get(t: Option<&[u8; NTYP]>) -> &[u8; NTYP] {
    t.unwrap()
}"""

#: calls the driver makes on each input -- from the payload header, not guessed.
CALLS = {"small.bin": 20000, "large.bin": 3000}

_CG_ROW = re.compile(r"^\s*([\d,]+)\s+(.*)$")


def _cg(exe, inp, tag):
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", exe, inp],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        return {"error": f"callgrind exit {r.returncode}"}
    total = None
    for line in open(out):
        if line.startswith("summary:") or line.startswith("totals:"):
            total = int(line.split(":", 1)[1].strip().split()[0])
    ann = subprocess.run([CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True).stdout
    kern = 0
    for line in ann.splitlines():
        m = _CG_ROW.match(line)
        if not m or ":" not in m.group(2):
            continue
        func = m.group(2).split(":", 1)[1].split(" [")[0].strip()
        if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", func):
            kern += int(m.group(1).replace(",", ""))
    return {"kernel_exclusive_ir": kern or None, "whole_program_ir": total,
            "inside_share_pct": (100.0 * kern / total) if (kern and total) else None}


def build(vdir, checked):
    src = open(os.path.join(PDIR, "unsafe.rs")).read()
    assert src.count(UNCHECKED) == 1, "unsafe.rs no longer spells opt_get as expected"
    if checked:
        src = src.replace(UNCHECKED, CHECKED, 1)
    d = os.path.join(SCRATCH, vdir)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    p = os.path.join(d, "k.rs")
    open(p, "w").write(src)
    exe = os.path.join(d, "k")
    subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                    "-C", "opt-level=3", "-C", "debug-assertions=off",
                    "--cfg", "slb_isolated", p, "-o", exe], check=True,
                   capture_output=True)
    return exe


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    cdir = os.path.join(os.path.dirname(SCRATCH), "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))

    rec = {"cell": "unsafe.rs, O3/isolated", "problems": [],
           "statistic": "A1 = callgrind exclusive Ir of the `kernel` symbol, "
                        "divided by the calls the driver makes",
           "variants": {}}
    exes = {}
    for vdir, tag, checked in (("v00", "unwrap_unchecked (shipped)", False),
                               ("v01", "unwrap (checked)", True)):
        exes[tag] = (build(vdir, checked), vdir)
    assert len({len(os.path.dirname(e)) for e, _ in exes.values()}) == 1, (
        "the two build directories must have EQUAL PATH LENGTHS (F101)")

    print(f"{'variant':28s}{'input':12s}{'A1 total':>14s}{'A1/call':>11s}"
          f"{'inside_share':>14s}")
    for tag, (exe, vdir) in exes.items():
        rec["variants"][tag] = {"dir": vdir, "by_input": {}}
        for inp, n in CALLS.items():
            ip = os.path.join(PDIR, "inputs", inp)
            got = subprocess.run([exe, ip], capture_output=True, text=True)
            c = _cg(exe, ip, f"{vdir}-{inp}")
            c["checksum"] = got.stdout.strip()
            c["ir_per_call"] = (c["kernel_exclusive_ir"] / n
                                if c.get("kernel_exclusive_ir") else None)
            rec["variants"][tag]["by_input"][inp] = c
            print(f"{tag:28s}{inp:12s}{c['kernel_exclusive_ir']:>14d}"
                  f"{c['ir_per_call']:>11.3f}{c['inside_share_pct']:>13.2f}%")

    a = rec["variants"]["unwrap_unchecked (shipped)"]["by_input"]
    b = rec["variants"]["unwrap (checked)"]["by_input"]
    rec["discriminant_cost_ir_per_call"] = {}
    print()
    for inp in CALLS:
        d = b[inp]["ir_per_call"] - a[inp]["ir_per_call"]
        rec["discriminant_cost_ir_per_call"][inp] = d
        print(f"  ⭐ {inp:12s} the OPTIONAL'S DISCRIMINANT TEST costs "
              f"{d:+.4f} Ir/call (A1, O3/isolated, checked minus unchecked)")
        if a[inp]["checksum"] != b[inp]["checksum"]:
            rec["problems"].append(
                f"{inp}: the two variants return different checksums, so they "
                f"are not the same program and the difference is not the "
                f"discriminant")

    print("\n  ⚠ This is the ONLY difference between the two binaries: one "
          "function body, one operation. The R3->R4 step in the measurement "
          "record removes SEVEN checks and must not be quoted for this.")

    rec.update(_pin.pin(["unsafe.rs", "inputs/small.bin", "inputs/large.bin"],
                        "python3 controls/optional_cost.py",
                        "two rustc builds and four callgrind runs; minutes"))
    with open(os.path.join(HERE, "optional_cost.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/optional_cost.json -- "
          f"{len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
