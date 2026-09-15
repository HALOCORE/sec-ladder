#!/usr/bin/env python3
"""`inside_share` for EVERY cell of THIS row, as a matrix, before the statistic
is chosen.

    python3 controls/inside_share.py             # run it from the row directory
    python3 controls/inside_share.py --selftest  # the must-fire arms, no build

⚠ **THIS FILE IS BYTE-IDENTICAL IN EVERY ROW THAT SHIPS IT, AND THAT IS THE
POINT.** It names no row, no build path and no call count: the row is its own
location, the build root is derived the way `harness/build.py::pattern_id`
derives it, and the call count is read out of the input file's header. ⭐ A
reader can `sha256sum` the copies and see one hash; a copy that drifts is
visible without reading either one.

=============================================================================
WHY A MATRIX AND NOT A NUMBER
=============================================================================
⭐⭐⭐ **`inside_share` IS PER-CELL, NOT PER-ROW** (`.memory-php/03-numbers.md`,
from `TASK_PHP_045`): `ph52` measures **22.24 %** on its C rungs and **≈98.6 %**
on its Rust ones, and publishes its R1-vs-R1h column in W1 while a respelling
search of its Rust rungs lands where A1 resolves. A row that quoted one number
would have been wrong about half its own cells.

**It is what decides which family can resolve a difference**, and it has to be
computed BEFORE the statistic is chosen rather than after the search disagrees.

⛔ **AND A HIGH SHARE IS NOT A CERTIFICATE** (F109): `ph55`'s C cells sit at
74-83 % and A1 still read `0.000 %` on that row's own defect site, because the
defect lived in an uninlinable callee. What matters is whether **the
DIFFERENCE** lands inside the symbol, not the level. ⚠ **This file prints the
LEVEL.** Nothing in it licenses a claim that A1 is safe on this row.

=============================================================================
⚠⚠⚠ TWO QUANTITIES WEAR THIS NAME IN THIS PROGRAMME. THIS IS THE `W` ONE.
=============================================================================
    inside_share = 100 x (callgrind exclusive Ir of the `kernel` symbol)
                       / (callgrind `summary:` total Ir for the SAME run)

-- defined here rather than inherited, because a percentage owes its denominator
a name (`.memory-php/03-numbers.md`, F88). The denominator is **one whole run**:
it includes process start-up, the dynamic loader, the file read and every
allocator call, because those are work the program really does.

⛔⛔ **THE OTHER ONE IS `F74`'s AND IT IS A DIFFERENT NUMBER:**

    F74 share = (kernel_exclusive_ir / n_iters) / marginal_ir_per_call

-- A1 per call over the **whole-program MARGINAL** per call, both read out of
the committed records. Its denominator excludes every fixed cost by
construction, and it is measured at `collapse.probe_iters` rather than at
`n_iters`. **Every `inside_share` figure in `RECAP_PHP.md`, in
`.memory-php/03-numbers.md` and in `ph29`'s `controls/spellings.py` docstring is
that one.** On `ph29`'s `c-gcc`/`small.bin` cell, **LABELLED**:

    F74's share      0.8045   (A1/call over the whole-program marginal/call)
    THIS file's `W`  0.8933   (kernel Ir over the callgrind whole-run total)

⛔⛔ **AND THAT LABELLING IS A REPAIR, NOT A FLOURISH.** This sentence shipped
as *"the two read 80.45 % and 89.33 %"* -- **two bare numbers in the one
sentence whose whole purpose is to stop two quantities being confused**, and in
the order a reader would most likely map them they are BACKWARDS, because the
paragraph introduces `W` first and `F74` second. ⭐ **The defect the file exists
to fix, inside the file that fixes it** -- `RECAP_PHP.md` F122/F127's class.
Caught by the manager re-deriving both numbers from the committed records
instead of reading them.

▶ **Say which you mean; they are not interchangeable**
(`TASK_PHP_058`, `.tasks-php/php58_record_share.py` computes the F74 one for
every built row without running anything).

⚠ It measures the binaries `harness-php/gate.py --tool build` already produced,
in the shim's build root, and builds nothing itself -- so the numbers are about
the cells the measurement record describes and not about a scratch copy. A
missing binary is a loud failure naming the build command, never a skip.

⚠ `whole` cells are NOT in the matrix: at `O3` the kernel is inlined into `main`
and there is no `kernel` symbol to be exclusive of, so the ratio is undefined
rather than 100 %.

=============================================================================
THE MUST-FIRE ARMS ARE IN HERE, AND THE GATE READS THEIR SCORE
=============================================================================
`PROTOCOL_PHP.md` §H: *a change to a validator lands with its must-fire
negatives, or it does not land*, and *a gate run EXERCISES a validator on the
rows that pass; it does not ATTACK it.* So the four decisions this control makes
-- is a binary missing, is there a `kernel` row in the listing, is the pin
aimed at this row, did the pin hash everything it was asked to -- are pure
functions with synthetic cases driven on **every** run, not only under
`--selftest`. The count lands in `summary` as `{"n": .., "as_expected": ..}`,
which `harness/check.py::control_json_verdict` FAILS when the two differ.
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
ROW = os.path.basename(PDIR)
#: ⚠ DERIVED the way `harness/build.py::pattern_id` derives it, so the build
#: root this reads cannot drift from the one the builder writes.
ROWTAG = ROW.split("-")[0]
sys.path.insert(0, HERE)
import _pin  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "common-php"))
import slb  # noqa: E402

BUILD = os.path.join(REPO, ".temp", "php-scratch", "build", ROWTAG)
SCRATCH = os.path.join(REPO, ".temp", "php58", "ishare", ROWTAG)
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")

CELLS = ["c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
INPUTS = ["small.bin", "large.bin"]
#: everything a cell's Ir derives from, row-relative. ⚠ `c/kernel.h` and
#: `c/main.c` are in it because they are compiled into every C cell; the
#: template this was ported from pinned neither.
PINNED = ["c/kernel.c", "c/kernel.h", "c/kernel_hardened.c", "c/main.c",
          "safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs",
          "inputs/small.bin", "inputs/large.bin"]

_CG_ROW = re.compile(r"^\s*([\d,]+)\s+(.*)$")
#: ⚠ `kernel_hardened` must NOT match: `_` is a word character, so the trailing
#: class excludes it. Arm 3 is that case and it is a must-NOT-fire.
_KERNEL = re.compile(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])")


# --------------------------------------------------------------------------
# the four decisions, as pure functions -- see the docstring's last section
# --------------------------------------------------------------------------
def kernel_ir(ann):
    """Exclusive Ir summed over every `kernel` row of a `callgrind_annotate`
    listing, or **None** when the listing has no such row. PURE."""
    kern = None
    for line in ann.splitlines():
        m = _CG_ROW.match(line)
        if not m or ":" not in m.group(2):
            continue
        func = m.group(2).split(":", 1)[1].split(" [")[0].strip()
        if _KERNEL.search(func):
            kern = (kern or 0) + int(m.group(1).replace(",", ""))
    return kern


def missing_binaries(build, cells):
    """The cells with no `-O3-isolated` binary under `build`."""
    return [c for c in cells
            if not os.path.exists(os.path.join(build, f"{c}-O3-isolated"))]


def pin_problems(block, pdir, wanted):
    """What is wrong with a `derived_from_sha256` block, as a list of strings.

    ⚠⚠ **`check.py` stage 9b SHOUTS rather than FAILS on a pin whose paths are
    absent, so a pin aimed at the wrong tree is the quietest possible way to
    have no pin at all** (`_pin.py`'s own docstring). This asks stage 9b's
    question HERE, where it is a FAILURE, against the row the file is sitting
    in -- no shim root needed.

    ⚠ And it asks a second one the stage cannot: `_pin.derived_from` OMITS a
    path that does not exist rather than hashing it, deliberately, so a typo in
    `PINNED` silently shrinks the pin instead of breaking it."""
    want = "patterns/" + os.path.basename(pdir) + "/"
    bad = []
    for k in sorted(block):
        if not k.startswith(want):
            bad.append(f"pin key `{k}` is not under `{want}` -- a pin is "
                       f"written in the SHIM's view of this row, or it hashes "
                       f"nothing and stage 9b only SHOUTS")
        elif not os.path.exists(os.path.join(pdir, k[len(want):])):
            bad.append(f"pin key `{k}` names no file under this row")
    if len(block) != len(wanted):
        bad.append(f"the pin hashed {len(block)} of {len(wanted)} requested "
                   f"path(s): {sorted(set(want + w for w in wanted) - set(block))}"
                   f" -- `_pin.derived_from` omits what does not exist")
    return bad


def n_iters(inp):
    """The driver's call count for one input, **READ FROM THE FILE'S HEADER**.

    ⭐ The template this was ported from carried
    `CALLS = {"small.bin": 20000, "large.bin": 3000}` with a comment saying the
    numbers came *"from the payload header, not guessed"*. Both were right, and
    both were still literals: three rows ported to have three different pairs,
    and a count in prose or in a tool has rotted nine times in this programme
    (open item 73). **A derived number cannot go stale when the input is
    regenerated; a copied one silently can.** `common-php/slb.py` is the reader
    `inputs/gen.py` and `harness/check.py` already share."""
    return slb.read(os.path.join(PDIR, "inputs", inp)).n_iters


# --------------------------------------------------------------------------
# the arms
# --------------------------------------------------------------------------
_ANN_OK = """--------------------------------------------------------------
Ir                   file:function
--------------------------------------------------------------
39,273,585 (89.33%)  ???:kernel [/some/where/c-gcc-O3-isolated]
   350,053 ( 0.80%)  ???:main [/some/where/c-gcc-O3-isolated]
43,965,591 (100.0%)  PROGRAM TOTALS
"""
_ANN_RUST = _ANN_OK.replace("???:kernel ", "???:safe_naive::kernel ")
_ANN_NEAR = _ANN_OK.replace("???:kernel ", "???:kernel_hardened ")
_ANN_NONE = _ANN_OK.replace("???:kernel ", "???:memcpy ")


def arms():
    """`[(name, expectation, ok)]` -- every arm, must-fire and must-NOT-fire.

    ⚠ Four of the seven are MUST-FIRE: a listing with no `kernel` row, a
    listing whose only near-match is `kernel_hardened`, an empty build root,
    and a pin aimed at another row. **A control that cannot fail is not a
    control.**"""
    out = []

    def arm(name, expect, got):
        out.append((name, expect, got == expect, got))

    arm("1 must-NOT-fire: a C `kernel` row is counted", 39273585,
        kernel_ir(_ANN_OK))
    arm("2 must-NOT-fire: a Rust `crate::kernel` row is counted", 39273585,
        kernel_ir(_ANN_RUST))
    arm("3 MUST-FIRE: `kernel_hardened` is NOT a `kernel` row", None,
        kernel_ir(_ANN_NEAR))
    arm("4 MUST-FIRE: a listing with no `kernel` row reads None", None,
        kernel_ir(_ANN_NONE))
    arm("5 MUST-FIRE: an empty build root reports every cell missing",
        list(CELLS), missing_binaries(os.path.join(SCRATCH, "no-such-build"),
                                      CELLS))
    arm("6 must-NOT-fire: this row's own pin is clean", [],
        pin_problems(_pin.derived_from(PINNED), PDIR, PINNED))
    arm("7 MUST-FIRE: a pin written in the non-shim view is caught", 2,
        len(pin_problems({"patterns-php/" + ROW + "/c/kernel.c": "x"},
                         PDIR, PINNED)))
    return out


def run_arms(rec):
    a = arms()
    rec["summary"] = {"n": len(a), "as_expected": sum(1 for x in a if x[2])}
    for name, expect, ok, got in a:
        if not ok:
            rec["problems"].append(
                f"SELFTEST ARM `{name}` did not behave as expected: wanted "
                f"{expect!r}, got {got!r}. This control's own decisions are "
                f"not trustworthy until it does.")
    return a


# --------------------------------------------------------------------------
def cg(exe, inp, tag):
    os.makedirs(SCRATCH, exist_ok=True)
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
    kern = kernel_ir(ann)
    return {"kernel_exclusive_ir": kern, "whole_program_ir": total,
            "inside_share_pct": (100.0 * kern / total) if (kern and total)
                                else None}


def main(argv):
    rec = {"row": ROW, "cell_spec": "O3 / isolated",
           "definition": "100 * callgrind exclusive Ir of the `kernel` symbol / "
                         "callgrind `summary:` total Ir for the same run",
           "not_this_definition": "(kernel_exclusive_ir / n_iters) / "
                                  "marginal_ir_per_call -- F74's share, which "
                                  "every published `inside_share` figure in "
                                  "this programme uses and which is a "
                                  "DIFFERENT number",
           "n_iters": {}, "matrix": {}, "problems": []}
    a = run_arms(rec)
    if "--selftest" in argv:
        for name, expect, ok, got in a:
            print(f"  {'ok  ' if ok else 'BAD '}{name}: got {got!r}")
        print(f"\n{rec['summary']['as_expected']} of {rec['summary']['n']} arms "
              f"as expected")
        return 0 if not rec["problems"] else 1

    for inp in INPUTS:
        rec["n_iters"][inp] = n_iters(inp)

    missing = missing_binaries(BUILD, CELLS)
    if missing:
        rec["problems"].append(
            f"binaries missing for {missing} -- run "
            f"`harness-php/gate.py --tool build {ROW} --all`")
        # ⚠ the pin goes on the FAILURE path too: an unpinned sidecar is one
        # stage 9b can only call UNPINNED, and a blocked run still overwrites
        # the numbers a reader may be about to quote.
        rec.update(_pin.pin(PINNED, "python3 controls/inside_share.py",
                            "blocked: the row was not built"))
        with open(os.path.join(HERE, "inside_share.json"), "w") as f:
            json.dump(rec, f, indent=1)
            f.write("\n")
        print(f"BLOCKED {rec['problems'][-1]}")
        return 1

    print(f"{ROW}  O3/isolated   n_iters " + " ".join(
        f"{i}={rec['n_iters'][i]}" for i in INPUTS))
    print(f"{'cell':12s}" + "".join(f"{i:>26s}" for i in INPUTS))
    print(f"{'':12s}" + "".join(f"{'A1/call   share':>26s}" for _ in INPUTS))
    for c in CELLS:
        rec["matrix"][c] = {}
        line = f"{c:12s}"
        for inp in INPUTS:
            r = cg(os.path.join(BUILD, f"{c}-O3-isolated"),
                   os.path.join(PDIR, "inputs", inp), f"{c}-{inp}")
            r["n_iters"] = rec["n_iters"][inp]
            r["ir_per_call"] = (r["kernel_exclusive_ir"] / r["n_iters"]
                                if r.get("kernel_exclusive_ir") else None)
            rec["matrix"][c][inp] = r
            if r.get("inside_share_pct") is None:
                rec["problems"].append(
                    f"{c}/{inp}: no `kernel` symbol or no callgrind total, so "
                    f"`inside_share` is undefined and the statistic for this "
                    f"cell cannot be chosen from it")
                line += f"{'--':>17s}{'--':>9s}"
            else:
                line += f"{r['ir_per_call']:>17.2f}{r['inside_share_pct']:>8.2f}%"
        print(line)

    # BOTH C COLUMNS ARE PRESENT BY CONSTRUCTION -- F108. A matrix that named
    # only one would be the exact defect this task was written about.
    for want in ("c-gcc", "c-clang"):
        if want not in rec["matrix"]:
            rec["problems"].append(
                f"{want} is absent from the matrix; a cross-language reading "
                f"needs BOTH C columns (F108)")

    print("\n  A HIGH SHARE IS NOT A CERTIFICATE (F109). What matters is "
          "whether the DIFFERENCE lands inside the symbol, not the level.")
    print("  `whole` cells are deliberately absent: at O3 the kernel is "
          "inlined into `main` and the ratio is undefined, not 100 %.")
    print("  This is the callgrind-total share, NOT F74's "
          "A1/marginal share. They differ; say which you mean.")

    block = _pin.derived_from(PINNED)
    rec["problems"].extend(pin_problems(block, PDIR, PINNED))
    rec.update(_pin.pin(PINNED, "python3 controls/inside_share.py",
                        f"{len(CELLS) * len(INPUTS)} callgrind runs over the "
                        f"already-built O3/isolated cells; minutes"))
    with open(os.path.join(HERE, "inside_share.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/inside_share.json -- "
          f"{rec['summary']['as_expected']}/{rec['summary']['n']} arms, "
          f"{len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  PROBLEM " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
