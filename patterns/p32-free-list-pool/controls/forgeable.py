#!/usr/bin/env python3
"""p32 CONTROLS: **the design decision, measured rather than argued.**

    python3 patterns/p32-free-list-pool/controls/forgeable.py

`TASK_143`'s admitted demonstration packed the handle into the OPERAND BYTE, so
the file named a `(slot, generation)` pair directly. The shipped rungs do not:
ALLOC issues the handle into a handle REGISTER and the file names the register.
That is a deviation from the promoted demonstration and it needs evidence, so
here it is -- `arm_forgeable.c` is the file-supplied-handle variant **with the
hardened guard present**, and on a five-operation input it

  * accepts a FREE of a block that is already on the free list, because the
    attacker can spell the CURRENT generation of a free block;
  * writes `nx[h] = freehead` with `freehead == h`, SELF-LOOPING the list;
  * hands the next two ALLOCs the SAME slot -- two live handles aliasing one
    block, in R1h.

`arm_forgeable.c` walks the resulting free list with a visited set and **exits
non-zero if the list is still simple**, so this control cannot silently stop
demonstrating its point.

⚠ It is the same failure `.memory/02-bench-rules.md`'s admission question 1
forbids -- *the C kernel is CORRECT on normal inputs* -- so the variant is not a
harder version of this row, it is a broken R1h. `../c/kernel.h`, `../spec.md`
and `../NOTES.md` 1b all cite this file.
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


def derived_from():
    out = {}
    for rel in ("patterns/p32-free-list-pool/controls/arm_forgeable.c",
                "patterns/p32-free-list-pool/controls/forgeable.py",
                "patterns/p32-free-list-pool/c/kernel_hardened.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(BIN, exist_ok=True)
    exe = os.path.join(BIN, "forgeable")
    b = subprocess.run([GCC, "-std=c99", "-Wall", "-Wextra", "-O1", "-o", exe,
                        os.path.join(HERE, "arm_forgeable.c")],
                       capture_output=True, text=True, timeout=300)
    if b.returncode != 0:
        raise SystemExit("forgeable.py: build failed:\n" + b.stdout + b.stderr)
    r = subprocess.run([exe], capture_output=True, text=True, timeout=300)
    log = r.stdout + r.stderr
    print(log.rstrip())
    broke = "SELF-LOOP" in log and "ALIAS ONE BLOCK" in log
    doc = {"pin": {"regenerate":
                   "python3 patterns/p32-free-list-pool/controls/forgeable.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "exit_code": r.returncode,
           "hardened_kernel_broke": broke,
           "transcript": log.splitlines(),
           "invariant":
               "With a FILE-SUPPLIED (slot, generation) handle the HARDENED "
               "kernel self-loops its own free list on a five-operation input "
               "and hands two ALLOCs the same slot. That is why the shipped "
               "rungs make ALLOC issue the handle into a REGISTER and let the "
               "file name the register instead."}
    out = os.path.join(HERE, "forgeable.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    if not broke:
        print("*** the forgeable variant did NOT break -- NOTES.md 1b is no "
              "longer supported by this control ***", file=sys.stderr)
    return 0 if broke and r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
