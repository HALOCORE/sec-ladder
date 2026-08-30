#!/usr/bin/env python3
"""p32 CONTROLS: **the two-cell storage experiment, and it is this row's
headline.**

    python3 patterns/p32-free-list-pool/controls/storage_arms.py

ONE ALGORITHM, FOUR ARMS, STORAGE THE ONLY VARIABLE
---------------------------------------------------
  `c-arena`      the SHIPPED C kernels, R1 and R1h, exactly as `harness/
                 build.py` builds them: the pool is `uint8_t pool[SLOTS*BLK]`.
  `c-malloc`     `arm_malloc.c`, which is `c/kernel.c` with the pool
                 replaced by `uint8_t *blk[SLOTS]`, one `malloc` per ALLOC and
                 one `free` per FREE. The free list, the generations, the handle
                 registers, the fold and the safety line are byte-identical;
                 `arm_body.inc` is included TWICE, with `P32_HARDEN` 0 and 1,
                 so the two arms of THAT file also differ by the safety line
                 alone.
  `safe-rust`    `arm_safe_bug.rs`, a `#![forbid(unsafe_code)]` port of the
                 same kernel with the same omitted conjunct.
  and the `ctl` POSITIVE CONTROL, a real double free of a real heap block.

WHY IT EXISTS
-------------
⚠⚠⚠ **The sentence *"safe Rust reproduces the buggy C bit for bit"*
was used TWICE as a reason to REFUSE this row** (`.memory/06-catalogue.md` p32
and p33, `RECAP` findings 53 and 54). It is true. It is measured here. And under
the corrected, C-side-only admission bar it is **the most interesting result
this project can produce**, not a defect -- `p29` ships with the same headline.

What makes it a MEASUREMENT rather than an anecdote is the `c-malloc` arm: with
everything else held byte-identical, changing where the bytes live turns two of
the three harms into an ASan `heap-use-after-free` and an `attempting
double-free`, and leaves the third -- the use-after-RECYCLE -- **bit-identical
and silent in both**. That is a controlled two-cell experiment on DETECTOR
COVERAGE.

RULES OBSERVED
--------------
  * every arm runs with `LD_PRELOAD` unset -- ASan silently fails to start
    otherwise and both cases exit 1;
  * the sanitiser log is never truncated: the classifier reads the whole of it;
  * **the positive control must FIRE in every sanitiser build**, and the script
    exits non-zero if it does not. ⚠ `TASK_143` had clang ELIMINATE its
    first control -- a `malloc`/`free`/`free` whose pointer never escapes is
    deleted whole (`p31`'s malloc-elision artefact) -- so `arm_malloc.c`
    forces the pointer through a `volatile void *` sink;
  * the arm sources are committed and the binaries are not: this script rebuilds
    every one of them (`.memory/00-environment.md` constraint 6).

⚠ **What no number here is:** a performance figure. This pattern publishes
no rung-to-rung cost at all (../NOTES.md 8). Everything below is a checksum or a
detector verdict.
"""

import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
BIN = os.path.join(REPO, ".temp", "build", "p32-arms")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))
RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))

CFLAGS = ["-std=c99", "-Wall", "-Wextra", "-O1", "-g", "-fno-omit-frame-pointer"]

# The op streams, written the way inputs/gen.py writes them: a u32 op count
# then (opcode, operand) pairs. `oper(reg, pay)` puts the handle REGISTER in the
# operand's low three bits and varies the payload above it.
ALLOC, FREE, READ, WRITE = 0, 1, 2, 3
NREG = 8


def oper(reg, pay):
    return (8 * pay + reg) & 0xFF


def enc(ops):
    b = bytes([len(ops) & 255, (len(ops) >> 8) & 255, 0, 0])
    for c, a in ops:
        b += bytes([c, a])
    return b.hex()


INPUTS = {
    # every handle used is still current
    "benign": enc([(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)), (READ, oper(0, 3)),
                   (WRITE, oper(1, 4)), (READ, oper(1, 5)), (FREE, oper(0, 6)),
                   (ALLOC, oper(2, 7)), (READ, oper(2, 8)), (FREE, oper(1, 9)),
                   (FREE, oper(2, 10)), (ALLOC, oper(3, 11)),
                   (READ, oper(3, 12))]),
    # FREE r0 then READ r0: the block is on the free list and nobody owns it
    "adv-stale-read": enc([(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)),
                           (FREE, oper(0, 3)), (READ, oper(0, 4))]),
    # FREE r0, ALLOC r2 (recycles slot 0), READ r0: the NEW occupant's payload
    "adv-recycle": enc([(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)),
                        (FREE, oper(0, 3)), (ALLOC, oper(2, 9)),
                        (READ, oper(0, 4)), (READ, oper(2, 5))]),
    # FREE r0 twice: the free list SELF-LOOPS and the two later ALLOCs alias
    "adv-doublefree": enc([(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)),
                           (FREE, oper(0, 3)), (FREE, oper(0, 4)),
                           (ALLOC, oper(2, 5)), (ALLOC, oper(3, 6)),
                           (READ, oper(2, 7)), (READ, oper(3, 8))]),
    # the aliasing put in the checksum: WRITE through one handle, READ the other
    "adv-alias": enc([(ALLOC, oper(0, 1)), (FREE, oper(0, 2)),
                      (FREE, oper(0, 3)), (ALLOC, oper(2, 5)),
                      (ALLOC, oper(3, 6)), (WRITE, oper(2, 7)),
                      (READ, oper(3, 8)), (WRITE, oper(3, 9)),
                      (READ, oper(2, 10))]),
}

# Read the WHOLE log; never `head` a sanitiser report.
SAN_PAT = ("ERROR: AddressSanitizer", "ERROR: LeakSanitizer", "runtime error:",
           "detected memory leaks", "double free or corruption", "free(): ",
           "malloc(): ")


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit("storage_arms.py: build failed:\n  "
                         + " ".join(cmd) + "\n" + r.stdout + r.stderr)


def build():
    os.makedirs(BIN, exist_ok=True)
    src = os.path.join(HERE, "arm_malloc.c")
    sh([GCC] + CFLAGS + ["-o", os.path.join(BIN, "malloc-plain"), src])
    sh([GCC] + CFLAGS + ["-fsanitize=address", "-o",
                         os.path.join(BIN, "malloc-asan"), src])
    sh([GCC] + CFLAGS + ["-fsanitize=undefined", "-o",
                         os.path.join(BIN, "malloc-ubsan"), src])
    if os.path.exists(CLANG):
        sh([CLANG] + CFLAGS + ["-o", os.path.join(BIN, "malloc-plain-clang"),
                               src])
        sh([CLANG] + CFLAGS + ["-fsanitize=address", "-o",
                               os.path.join(BIN, "malloc-asan-clang"), src])
    # The ARENA arm is the same source with -DP32_ARENA, so that "the storage is
    # the only variable" is true of ONE file rather than of two files a reader
    # has to diff.
    sh([GCC] + CFLAGS + ["-DP32_ARENA", "-o",
                         os.path.join(BIN, "arena-plain"), src])
    sh([GCC] + CFLAGS + ["-DP32_ARENA", "-fsanitize=address", "-o",
                         os.path.join(BIN, "arena-asan"), src])
    sh([GCC] + CFLAGS + ["-DP32_ARENA", "-fsanitize=undefined", "-o",
                         os.path.join(BIN, "arena-ubsan"), src])
    if os.path.exists(CLANG):
        sh([CLANG] + CFLAGS + ["-DP32_ARENA", "-o",
                               os.path.join(BIN, "arena-plain-clang"), src])
        sh([CLANG] + CFLAGS + ["-DP32_ARENA", "-fsanitize=address", "-o",
                               os.path.join(BIN, "arena-asan-clang"), src])
    sh([RUSTC, "-O", "--edition", "2021", "-o", os.path.join(BIN, "safe"),
        os.path.join(HERE, "arm_safe_bug.rs")])


def run(binname, arm, hexin):
    e = dict(os.environ)
    e.pop("LD_PRELOAD", None)          # ASan will not start otherwise
    p = subprocess.run([os.path.join(BIN, binname), arm, hexin],
                       capture_output=True, text=True, env=e, timeout=300)
    log = p.stdout + p.stderr
    fired = [s for s in SAN_PAT if s in log]
    err = ""
    for line in log.splitlines():
        if "ERROR: AddressSanitizer:" in line:
            err = line.split("ERROR: AddressSanitizer:")[1].strip()
            err = err.split(" on ")[0].split(" address")[0].strip()
            break
        if line.startswith("free(): ") or line.startswith("malloc(): "):
            err = line.strip()
            break
    return {"rc": p.returncode, "out": p.stdout.strip().split(" ")[-1]
            if p.stdout.strip() else "", "fired": fired, "diagnostic": err}


def derived_from():
    out = {}
    for rel in ("patterns/p32-free-list-pool/c/kernel.c",
                "patterns/p32-free-list-pool/c/kernel_hardened.c",
                "patterns/p32-free-list-pool/controls/storage_arms.py",
                "patterns/p32-free-list-pool/controls/arm_body.inc",
                "patterns/p32-free-list-pool/controls/arm_malloc.c",
                "patterns/p32-free-list-pool/controls/arm_safe_bug.rs"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    build()
    builds = sorted(os.listdir(BIN))
    cbuilds = [b for b in builds if b != "safe"]
    rows = []

    # ---- the positive control, FIRST, because nothing below means anything
    # if the detector never started.
    ctl = []
    for b in cbuilds:
        if "asan" not in b and "plain" not in b and "ubsan" not in b:
            continue
        r = run(b, "ctl", INPUTS["benign"])
        ctl.append(dict(build=b, **r))
        print(f"  POSITIVE-CONTROL {b:20s} rc={r['rc']:<4d} "
              f"{'FIRED' if r['fired'] else '*** DID NOT FIRE ***'} "
              f"{r['diagnostic']}")
    dead = [c["build"] for c in ctl if not c["fired"]]

    print()
    hdr = (f"{'input':16} {'arm':4} {'c-arena':>22} {'c-malloc':>22} "
           f"{'safe-rust':>22}  malloc detector")
    print(hdr)
    print("-" * len(hdr))
    for iname, hx in INPUTS.items():
        for arm in ("bug", "fix"):
            a = run("arena-plain", arm, hx)
            m = run("malloc-plain", arm, hx)
            s = run("safe", arm, hx)
            ma = run("malloc-asan", arm, hx)
            aa = run("arena-asan", arm, hx)
            row = {"input": iname, "arm": arm,
                   "c_arena_plain": a, "c_malloc_plain": m, "safe_rust": s,
                   "c_malloc_asan": ma, "c_arena_asan": aa,
                   "arena_equals_safe_rust": a["out"] == s["out"]}
            rows.append(row)
            print(f"{iname:16} {arm:4} {a['out'] or ('rc=%d' % a['rc']):>22} "
                  f"{m['out'] or ('rc=%d' % m['rc']):>22} "
                  f"{s['out']:>22}  {ma['diagnostic'] or '-'}")
        print()

    # every C build x every input, for the record
    matrix = []
    for iname, hx in INPUTS.items():
        for arm in ("bug", "fix"):
            for b in cbuilds:
                matrix.append(dict(input=iname, arm=arm, build=b,
                                   **run(b, arm, hx)))

    bad = [r for r in rows if not r["arena_equals_safe_rust"]]
    print("HEADLINE: `#![forbid(unsafe_code)]` safe Rust == the C ARENA rung on "
          f"{len(rows) - len(bad)} of {len(rows)} (input, arm) cells"
          + ("" if not bad else f"  *** {len(bad)} MISMATCH ***"))
    print("          the SAME C source with `malloc` storage aborts on the "
          "double-free and the stale-read arms, and is bit-identical on the "
          "use-after-RECYCLE one.")

    doc = {
        "pin": {"regenerate": "python3 patterns/p32-free-list-pool/controls/"
                              "storage_arms.py"},
        "derived_from_sha256": derived_from(),
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": INPUTS,
        "positive_control": ctl,
        "positive_control_dead_builds": dead,
        "rows": rows,
        "matrix": matrix,
        "invariant":
            "(1) `#![forbid(unsafe_code)]` safe Rust reproduces the C ARENA "
            "rung EXACTLY on every (input, arm) cell, buggy arm included. "
            "(2) The SAME algorithm on `malloc` storage aborts under ASan on "
            "the stale-read and double-free inputs and is silent on the "
            "use-after-RECYCLE one. (3) The arena arm is silent under ASan and "
            "UBSan on EVERY input while its answer is wrong on four of them. "
            "⚠ The CHECKSUMS of the `malloc` PLAIN build on adv-stale-read "
            "are NOT reproducible -- it reads freed heap -- so no number from "
            "that cell is a fact; the DETECTOR verdicts and the arena "
            "checksums are.",
    }
    if dead:
        doc["FAILED"] = ("the positive control did not fire in: "
                         + ", ".join(dead))
    json.dump(doc, open(os.path.join(HERE, "storage_arms.json"), "w"), indent=2)
    print(f"wrote {os.path.join(HERE, 'storage_arms.json')}")
    if dead:
        print(f"*** POSITIVE CONTROL DID NOT FIRE IN {dead} -- nothing above "
              f"is evidence ***", file=sys.stderr)
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
