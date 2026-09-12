#!/usr/bin/env python3
"""ph53 control: **WHAT `d09cdd9f71f3` ACTUALLY BUYS, PER CONSUMER.**

    python3 patterns-php/ph53-iface-tail-uninit/controls/r1h_consumers.py
    python3 .../r1h_consumers.py --selftest      # the same, plus the negatives

⚠⚠⚠ **THIS CONTROL EXISTS BECAUSE THE GATE STRUCTURALLY CANNOT CARRY ITS
EVIDENCE, AND THAT IS ITSELF THE ROW'S RESULT.**
`harness/check.py` stage 7h requires the hardened C rung to be **clean under
ASan+UBSan on EVERY input in `inputs/`**, and says so in terms: *"a per-input
declaration here would let a pattern declare its way out of the only thing this
stage asks."* But `d09cdd9f71f3` zeroes the interface array and adds **no
consumer guard**, so every blob on which R1 dereferences a slot nobody wrote is
a blob on which **R1h dereferences NULL**. ▶ So the row whose headline is *the
upstream fix does not remove the fault* cannot ship the input that shows it.
That is `.memory-php/02-ladder.md` F31's standing limitation — *"a green php
gate does NOT mean the upstream fix is complete, and cannot … that evidence
lives in the row's `controls/`"* — binding on a real row for the first time,
and this file is the place F31 itself prescribes.

**WHAT IT MEASURES.** Four blobs, generated here (not shipped: `.temp/` is
gitignored and a committed file must not rest a claim on a `.temp/` path, so the
numbers go in `../NOTES.md` §5 and in the task report), against both C kernels
built with **exactly `check.py::_san_build`'s line** — `gcc -std=c99 -Wall
-Wextra -O1 -g -fsanitize=address,undefined -fstrict-aliasing -static-libasan
-static-libubsan -DSLB_ISOLATED` — and again with no sanitizer at `-O2`:

    deref        n_decl 2, FILL(slot 0), QUERY_DEREF        slot 1 is read and
                                                            DEREFERENCED
    deref-nofill n_decl 2, no FILL at all, QUERY_DEREF      both slots ditto
    cmp          n_decl 2, FILL(slot 0), QUERY_CMP          slot 1 is READ and
                                                            NOT dereferenced
    covered      n_decl 2, FILL(0), FILL(1), QUERY_DEREF    must-NOT-fire

**THE RESULT, AND IT IS WHY THE KERNEL SHIPS TWO CONSUMERS.** One hunk, two
severities: on the dereferencing consumer the fix turns a wild-pointer
dereference into a *deterministic NULL* dereference and the process still dies;
on the comparing consumer it turns an indeterminate comparison into a *defined
and correct* answer, and both arms print the same `u64`. `PROTOCOL_PHP.md` §C's
*"an upstream fix is not automatically correct — report it, do not repair it"*
case, measured rather than read off the source.

⚠ **ASan DOES NOT SEE THE UNINITIALISED READ, and the control says so rather
than letting the reader assume otherwise.** The read is of an in-bounds slot of
a live allocation — CWE-824, not CWE-125 — which is MSan's class and not
ASan's. What the ASan/UBSan build reports is the *dereference of the value that
came out*, and it is deterministic only because ASan fills fresh allocations
with `0xbe`: `0xbebebebebebebebe` is not a canonical address. Under plain
`malloc` the same blob may or may not fault, which is exactly what an
indeterminate value means and is why `controls/wild_choice.c` exists — it
CHOOSES the value instead of observing it.

§H: the negatives are part of the control. `--selftest` adds:

    N1 MUST-FIRE     R1 on `deref` must produce a diagnostic naming a
                     NON-NULL address, so the control cannot pass by reporting
                     R1h's fault twice
    N2 MUST-FIRE     R1h on `deref` must produce a diagnostic naming NULL
    N3 MUST-NOT-FIRE both arms on `cmp` must be silent and must AGREE on the
                     u64 -- without this, "R1h fixes the comparing consumer"
                     could be a claim about a crash that never happened
    N4 MUST-NOT-FIRE both arms on `covered` must be silent, so the three rows
                     above are attributable to the COVERAGE and not to the
                     kernel being broken outright
    N5 MUST-FIRE     the four blobs must be DISTINCT and must decode to the
                     coverage this docstring claims, re-derived from the bytes
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, os.path.join(REPO, "common-php"))
sys.path.insert(0, ROW)
import slb  # noqa: E402
from model import Model, OP_FILL, OP_QD, OP_QC, unpack  # noqa: E402

OUT = os.path.join(REPO, ".temp", "php41", "controls")
STRIDE = 221
POOL_IDS = tuple(0x0C1A55_000000_01 + j for j in range(8))

#: `harness/check.py::_san_build`'s line, character for character, so this
#: control cannot drift from the stage whose gap it fills. ⚠ `-static-libasan`
#: and `-static-libubsan` are gcc spellings and clang rejects them; this
#: control is gcc-only, as stage 7 and stage 7h are.
SAN_FLAGS = ["-std=c99", "-Wall", "-Wextra", "-O1", "-g",
             "-fsanitize=address,undefined", "-fstrict-aliasing",
             "-static-libasan", "-static-libubsan", "-DSLB_ISOLATED"]
PLAIN_FLAGS = ["-std=c99", "-Wall", "-Wextra", "-O2", "-DSLB_ISOLATED"]

BLOBS = {
    # name          n_decl  ops
    "deref":        (2, [(OP_FILL, 0, 0), (OP_QD, 1, 0)]),
    "deref-nofill": (2, [(OP_QD, 1, 0)]),
    "cmp":          (2, [(OP_FILL, 0, 0), (OP_QC, 1, 0)]),
    "covered":      (2, [(OP_FILL, 0, 0), (OP_FILL, 1, 1), (OP_QD, 1, 0)]),
}


def build(tag, kernel, flags):
    out = os.path.join(OUT, f"{tag}-{kernel}")
    cmd = (["gcc"] + flags
           + ["-I", os.path.join(REPO, "common"),
              "-I", os.path.join(ROW, "c"),
              "-I", os.path.join(REPO, "common-php"),
              os.path.join(REPO, "common", "driver.c"),
              os.path.join(ROW, "c", f"{kernel}.c"),
              os.path.join(ROW, "c", "main.c"),
              "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"BUILD FAILED ({tag}/{kernel}):\n{r.stdout}{r.stderr}")
    return out


def write_blob(name, n_decl, ops, n_iters=8):
    win = Model._mkwin(STRIDE, n_decl, 7, len(ops), POOL_IDS, ops)
    path = os.path.join(OUT, f"{name}.bin")
    slb.write(path, n_iters, slb.pack_head1_bytes(STRIDE, win))
    return path


def run(binary, blob):
    r = subprocess.run([binary, blob], capture_output=True, text=True,
                       timeout=180)
    err = re.sub(r"\s+", " ", r.stderr.strip())
    return r.returncode, r.stdout.strip(), err


def fault_address(diag):
    """The address UBSan/ASan names, or None. ⚠ Anchored on the two message
    shapes this row produces and NOT a bare hex scan: a `pc 0x...` or a
    `BuildId` would otherwise read as the faulting address."""
    m = re.search(r"member access within (null pointer|misaligned address "
                  r"(0x[0-9a-f]+))", diag)
    if m:
        return "NULL" if m.group(1) == "null pointer" else m.group(2)
    m = re.search(r"SEGV on unknown address (0x[0-9a-f]+)", diag)
    if m:
        return "NULL" if int(m.group(1), 16) == 0 else m.group(1)
    if "SEGV on unknown address" in diag:
        return "unknown"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true",
                    help="also run the five negatives (PROTOCOL_PHP.md H)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    blobs = {n: write_blob(n, nd, ops) for n, (nd, ops) in BLOBS.items()}
    bins = {}
    for kernel in ("kernel", "kernel_hardened"):
        bins[("san", kernel)] = build("san", kernel, SAN_FLAGS)
        bins[("plain", kernel)] = build("plain", kernel, PLAIN_FLAGS)

    print("ph53 controls/r1h_consumers.py -- what d09cdd9f71f3 buys, per consumer")
    print(f"  san flags:   {' '.join(SAN_FLAGS)}")
    print(f"  plain flags: {' '.join(PLAIN_FLAGS)}")
    print()
    rows = {}
    for name, blob in blobs.items():
        for arm in ("san", "plain"):
            for kernel, label in (("kernel", "R1 "), ("kernel_hardened", "R1h")):
                rc, out, err = run(bins[(arm, kernel)], blob)
                addr = fault_address(err)
                rows[(name, arm, kernel)] = (rc, out, err, addr)
                sig = f" signal={-rc}" if rc < 0 else ""
                print(f"  {name:13s} {arm:5s} {label}  rc={rc:<4d}{sig:11s} "
                      f"u64={out or '-':<22s} fault={addr or '-'}")
                if err:
                    print(f"      {err[:190]}")
        print()

    if not a.selftest:
        return 0

    print("-- negatives (PROTOCOL_PHP.md H) " + "-" * 46)
    bad = []

    # N1: R1's fault on `deref` must name a NON-NULL address.
    for name in ("deref", "deref-nofill"):
        addr = rows[(name, "san", "kernel")][3]
        if addr is None:
            bad.append(f"N1 {name}: R1 produced NO diagnostic under "
                       f"ASan+UBSan. The whole control rests on R1 faulting "
                       f"here; silence means the corpus's recorded "
                       f"wild-pointer-deref is not being reproduced")
        elif addr == "NULL":
            bad.append(f"N1 {name}: R1's fault address is NULL, which is "
                       f"R1h's. If both arms fault at NULL the control is "
                       f"measuring one program twice and the 'two severities' "
                       f"claim has no evidence")
        else:
            print(f"  ok   N1 {name}: R1 faults at {addr} (not NULL)")

    # N2: R1h's fault on `deref` must name NULL.
    for name in ("deref", "deref-nofill"):
        addr = rows[(name, "san", "kernel_hardened")][3]
        if addr != "NULL":
            bad.append(f"N2 {name}: R1h's fault address is {addr!r}, want "
                       f"NULL. The claim is that the memset makes the fault "
                       f"DETERMINISTIC, and that is a claim about the address")
        else:
            print(f"  ok   N2 {name}: R1h faults at NULL, deterministically")

    # N3: on `cmp` both arms are silent and AGREE.
    r1 = rows[("cmp", "san", "kernel")]
    r1h = rows[("cmp", "san", "kernel_hardened")]
    if r1[3] is not None or r1h[3] is not None:
        bad.append(f"N3 cmp: a diagnostic fired on the COMPARE-ONLY consumer "
                   f"(R1 {r1[3]!r}, R1h {r1h[3]!r}). That consumer reads the "
                   f"slot and does not dereference it, so neither arm should "
                   f"fault -- and the 'two severities' result depends on it")
    elif r1[0] != 0 or r1h[0] != 0:
        bad.append(f"N3 cmp: exit {r1[0]}/{r1h[0]}, want 0/0")
    elif r1[1] != r1h[1]:
        bad.append(f"N3 cmp: the two arms print DIFFERENT u64s "
                   f"({r1[1]} vs {r1h[1]}). That is a result and not a "
                   f"failure, but it contradicts the docstring, so the "
                   f"docstring is what must move")
    else:
        print(f"  ok   N3 cmp: both arms silent, exit 0, same u64 {r1[1]}")

    # N4: `covered` must be silent everywhere -- the must-NOT-fire control.
    for arm in ("san", "plain"):
        for kernel in ("kernel", "kernel_hardened"):
            rc, out, err, addr = rows[("covered", arm, kernel)]
            if addr is not None or rc != 0:
                bad.append(f"N4 covered/{arm}/{kernel}: rc={rc} fault={addr!r} "
                           f"-- the fully-covered blob must be clean on every "
                           f"arm, or the three rows above are not attributable "
                           f"to the COVERAGE")
    if not any(b.startswith("N4") for b in bad):
        print("  ok   N4 covered: clean on all four (arm x kernel) cells")

    # N5: the blobs are distinct and decode to the coverage claimed here.
    seen = {}
    for name, blob in blobs.items():
        body = open(blob, "rb").read()
        if body in seen:
            bad.append(f"N5 {name}: byte-identical to {seen[body]}")
        seen[body] = name
        m = Model(blob)
        win = m.buf[:STRIDE]
        n_decl, n_pool, n_ops, pool, ops = unpack(win)
        written = [None] * n_decl
        reached_unwritten = derefed = 0
        for (op, x, y) in ops:
            if op == OP_FILL:
                written[x % n_decl] = y % n_pool
            else:
                for i in range(n_decl):
                    if written[i] is None:
                        reached_unwritten += 1
                        derefed += (op == OP_QD)
                    if op == OP_QD and written[i] is not None \
                            and pool[written[i]] == pool[x % n_pool]:
                        break
                    if op == OP_QC and written[i] == (x % n_pool):
                        break
        want_read = name != "covered"
        want_deref = name in ("deref", "deref-nofill")
        if (reached_unwritten > 0) != want_read:
            bad.append(f"N5 {name}: re-derived unwritten-slot reads "
                       f"{reached_unwritten}, docstring says "
                       f"{'some' if want_read else 'none'}")
        if (derefed > 0) != want_deref:
            bad.append(f"N5 {name}: re-derived unwritten-slot DEREFERENCES "
                       f"{derefed}, docstring says "
                       f"{'some' if want_deref else 'none'}")
    if not any(b.startswith("N5") for b in bad):
        print(f"  ok   N5: the {len(blobs)} blobs are distinct and each decodes "
              f"to the coverage this docstring claims")

    print()
    if bad:
        print("SELFTEST FAIL")
        for b in bad:
            print(f"    {b}")
        return 1
    print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
