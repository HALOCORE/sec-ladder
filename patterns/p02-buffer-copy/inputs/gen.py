#!/usr/bin/env python3
"""Generate p02's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p02-buffer-copy/inputs/gen.py            # the 9 matrix inputs
    python3 patterns/p02-buffer-copy/inputs/gen.py --sweep    # + record-length sweep

Payload layout (../spec.md):

    word 0     u64  cap        destination buffer capacity, in bytes
    word 1     u64  stride     bytes per record
    byte 16..  u8[] src        the record blob; n_src = payload_len - 16

Every record is `stride` bytes: a little-endian u16 length prefix followed by
that many data bytes (plus whatever padding `stride` leaves). Nothing is a
compile-time constant: `n_iters`, `cap`, `stride` and `n_src` all come from the
file, and so does every length prefix the kernel reads.

Two things about the sizes are deliberate and must survive any edit:

  * `small` and `large` copy **61** and **4092** bytes, which are different
    residues mod 4 (1 and 0) *and* mod 8 (5 and 4). `.memory/01-ladder.md`: the
    safe-vs-unsafe delta varies with the residue, and quoting one residue as if
    it were the number has now been the mistake three times. The tail of a
    vectorised copy is exactly where that shows up.
  * the strides (63 and 4094) are not powers of two, so consecutive records do
    not share a cache-set alignment and the record offsets the driver picks are
    not all 8-byte aligned. A length-prefixed record on the wire is not aligned;
    pretending otherwise would flatter every rung equally but measure something
    else.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.


def blob(rng, nrec, stride, rec_len, tail_len=None):
    """`nrec` records of `stride` bytes, each prefixed with its length.

    `rec_len` is the length written into every prefix; `tail_len` overrides it
    for the last record, which is how the "record runs off the end of the
    source" case is built without touching any other record."""
    out = bytearray()
    for i in range(nrec):
        ln = rec_len if (tail_len is None or i != nrec - 1) else tail_len
        rec = bytearray(stride)
        # A stride < 2 cannot hold a prefix at all -- that is the whole point of
        # the `adversarial-stride1` shape, so write as much of it as fits.
        if stride >= 1:
            rec[0] = ln & 0xFF
        if stride >= 2:
            rec[1] = (ln >> 8) & 0xFF
            rec[2:] = rng.randbytes(stride - 2)
        out += rec
    return bytes(out)


def write(name, n_iters, cap, stride, body, declared_len=None):
    payload = slb.pack_head2_bytes(cap, stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:32s} n_iters={n_iters:<7d} cap={cap:<12d} stride={stride:<6d} "
          f"n_src={len(body):<9d} payload={len(payload)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-l*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p02 inputs ->", os.path.relpath(HERE, os.getcwd()))

    # ---- the two measured inputs -----------------------------------------
    # small: 200 records x 63 B = 12 600 B of source + a 64 B destination, so
    # the whole working set is ~12.4 KiB and lives in L1 (32 KiB on this box).
    write("small.bin", 200_000, 64, 63, blob(rng, 200, 63, 61))
    # large: 2048 records x 4094 B = 8.0 MiB of source, 8x this box's 1 MiB L2
    # and comfortably beyond it; the record the driver picks is uniform over the
    # whole blob, so every call is a cold 4 KiB read.
    write("large.bin", 20_000, 4096, 4094, blob(rng, 2048, 4094, 4092))

    # ---- adversarial: the length prefix is the attack ---------------------
    # The four below are the point of the pattern. Every one of them REACHES
    # the kernel (p01's adversarial inputs all made zero kernel calls, which is
    # what hid blocker B3), and each isolates one term of the rejection test.
    #
    # n_iters is small: R1 is expected to be executing undefined behaviour on
    # these, and there is nothing to learn from doing it 200 000 times.

    # (1) the maximum a u16 prefix can express: 65 535 bytes into a 64 B buffer.
    write("adversarial.bin", 8, 64, 63, blob(rng, 200, 63, 0xFFFF))
    # (2) len == cap exactly. LEGAL -- the boundary from the safe side, and the
    #     input that catches an off-by-one *in the check*: a rung that wrote
    #     `len >= cap` would reject a well-formed record and diverge here.
    write("adversarial-cap.bin", 8, 64, 66, blob(rng, 190, 66, 64))
    # (3) len == cap + 1. The record's bytes are all present in `src`, so the
    #     destination bound is the ONLY thing violated, by exactly one byte.
    write("adversarial-cap1.bin", 8, 64, 67, blob(rng, 188, 67, 65))
    # (4) len fits the destination but runs off the end of the source: one
    #     record of 40 bytes claiming 61. Isolates the second term of the test
    #     (an out-of-bounds READ, where (1) and (3) are writes).
    write("adversarial-srcend.bin", 8, 64, 40, blob(rng, 1, 40, 61))

    # ---- adversarial: degenerate shapes the driver must survive -----------
    # (5) stride < 2: a "record" that cannot even hold its own length prefix.
    #     The guard skips the loop entirely rather than entering and breaking
    #     out of it, which would put a branch in the measured loop.
    write("adversarial-stride1.bin", 8, 64, 1, blob(rng, 64, 1, 0))
    # (6) a declared capacity of 1 TiB. Rejected before the allocation, by both
    #     drivers, with the same exit code -- otherwise C's calloc returns NULL
    #     where Rust's allocator aborts, and a driver difference reads as a rung
    #     difference (common/driver.h, SLB_MAX_CAP).
    write("adversarial-capbig.bin", 8, 1 << 40, 63, blob(rng, 8, 63, 61))
    # (7) payload_len declares more bytes than the file carries.
    body = blob(rng, 8, 63, 61)
    write("adversarial-shortlen.bin", 8, 64, 63, body,
          declared_len=16 + len(body) + 4096)

    if a.sweep:
        # Diagnostic only: one record length is a coincidence, not a number.
        # `harness/check.py` and `harness/measure.py` both skip `sweep-`.
        print("  -- sweep (diagnostic, not part of the matrix)")
        for ln in range(56, 72):
            write(f"sweep-l{ln}.bin", 200_000, 72, 74, blob(rng, 175, 74, ln))
    return 0


if __name__ == "__main__":
    sys.exit(main())
