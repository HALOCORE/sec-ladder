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
    residues mod 4 (1 and 0), mod 8 (5 and 4) **and mod 16 (13 and 12)**.
    `.memory/01-ladder.md`: the safe-vs-unsafe delta varies with the residue,
    and quoting one residue as if it were the number has now been the mistake
    three times. **Mod 16 is the modulus that actually mattered here**: R2's
    epilogue on this codegen swings ~170 Ir across a mod-16 cycle -- measured,
    `-O3 isolated`, copying *one more byte* (2048 -> 2049) made R2 166.7
    instructions *cheaper* per call. `_check_residues()` below asserts the two
    measured lengths differ mod 4, 8 and 16, so an edit that quietly puts them
    in the same class fails loudly instead of producing a flattering number.
  * the strides (63 and 4094) are not powers of two, so consecutive records do
    not share a cache-set alignment and the record offsets the driver picks are
    not all 8-byte aligned. A length-prefixed record on the wire is not aligned;
    pretending otherwise would flatter every rung equally but measure something
    else.

And one about the sweep: two points and a line is not a curve. `--sweep` emits
**two complete mod-16 cycles** of record lengths, one at L1 scale and one at
~2 KiB, because the residue effect is a property of the copy epilogue and its
amplitude is not the same at both scales. `harness/check.py` and
`harness/measure.py` both skip the `sweep-` prefix, so these are diagnostic
inputs and never enter the matrix.
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


# The two measured record lengths, and the moduli they must not share. The
# lengths are here rather than inline so `_check_residues` can see them.
SMALL_LEN, LARGE_LEN = 61, 4092
RESIDUE_MODULI = (4, 8, 16)

# `--sweep`: (first_len, n_lens, cap, stride, nrec, n_iters). Each band is
# **two** full cycles of `RESIDUE_MODULI[-1]` consecutive lengths plus the
# endpoints, so the curve shows the whole sawtooth *and* establishes its period
# instead of assuming it. One cycle is not enough: the first draft of this sweep
# used 16 lengths per band and both bands happened to straddle a multiple of 64,
# which cannot tell a period of 16 from a period of 64.
#
# So each band is **34 consecutive lengths** -- 56..89 and 2040..2073, 68 inputs
# in total. (This comment said "measured over 72 consecutive lengths" until
# TASK_008; 72 is not a number in the data. The two bands are 34 each and they
# are not adjacent.) What 34 buys is the lag-16 comparison repeated 18 times per
# band: R3 - R4 agrees with itself at lag 8 and lag 16 in 26/26 and 18/18 pairs
# in both bands, which excludes a period of 32 or 64 outright, while R2 - R4
# agrees at lag 16 only after the 0.21 Ir/byte linear term is subtracted (the
# raw lag-16 difference is a constant ~5.0 Ir = 16 x 0.21). It cannot exclude a
# period longer than 34; the second band, 32x larger, is what makes one
# implausible. The shape: a ~167 Ir drop at `len == 1 (mod 16)` and a ~7 Ir drop
# at `len == 0 (mod 8)`, on top of ~17 Ir per extra byte within a cycle.
# NOTES.md 3b has the table and the check.
SWEEP_CYCLES = 2
SWEEP_BANDS = ((56, RESIDUE_MODULI[-1] * SWEEP_CYCLES + 2, 96, 98, 130, 200_000),
               (2040, RESIDUE_MODULI[-1] * SWEEP_CYCLES + 2, 2080, 2082, 64, 20_000))


def _check_residues():
    """The two measured lengths must differ modulo every modulus that has ever
    bitten this project. Returns a list of problems (empty when healthy).

    p01's first draft used 500 and 4096, both == 0 (mod 4), which is the single
    worst residue for R2 and overstated it 2.4x. p02's first draft used 61 and
    4092, which differ mod 4 and mod 8 -- and *that* was still not enough,
    because the modulus that governs this kernel's copy epilogue is 16."""
    bad = []
    for m in RESIDUE_MODULI:
        if SMALL_LEN % m == LARGE_LEN % m:
            bad.append(f"small={SMALL_LEN} and large={LARGE_LEN} are both "
                       f"== {SMALL_LEN % m} (mod {m}); pick lengths in "
                       f"different residue classes or the delta you publish is "
                       f"one residue wearing the label of a constant")
    return bad


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
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: {SMALL_LEN} and {LARGE_LEN} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 200 records x 63 B = 12 600 B of source + a 64 B destination, so
    # the whole working set is ~12.4 KiB and lives in L1 (32 KiB on this box).
    write("small.bin", 200_000, 64, 63, blob(rng, 200, 63, SMALL_LEN))
    # large: 2048 records x 4094 B = 8.0 MiB of source, 8x this box's 1 MiB L2
    # and comfortably beyond it; the record the driver picks is uniform over the
    # whole blob, so every call is a cold 4 KiB read.
    write("large.bin", 20_000, 4096, 4094, blob(rng, 2048, 4094, LARGE_LEN))

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
        #
        # Two full mod-16 cycles. The first band is L1-resident and answers
        # "what does the residue cost at the scale of `small`"; the second sits
        # at ~2 KiB, which is where the swing was first noticed (2048 -> 2049
        # made R2 cheaper). Sweeping only one band would have reproduced exactly
        # the mistake this sweep exists to correct.
        print("  -- sweep (diagnostic, not part of the matrix)")
        for first, n, cap, stride, nrec, iters in SWEEP_BANDS:
            for ln in range(first, first + n):
                write(f"sweep-l{ln}.bin", iters, cap, stride,
                      blob(rng, nrec, stride, ln))
    return 0


if __name__ == "__main__":
    sys.exit(main())
