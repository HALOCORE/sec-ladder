#!/usr/bin/env python3
"""Generate p05's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p05-index-flatten/inputs/gen.py            # the 6 matrix inputs
    python3 patterns/p05-index-flatten/inputs/gen.py --sweep    # + the ncol sweep

Payload layout (../spec.md), p17's verbatim:

    word 0     u64  stride     bytes per window; the kernel folds one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..2   nrow   u16 LE      declared row count      ATTACKER DATA
    byte 2..4   ncol   u16 LE      declared column count   ATTACKER DATA
    byte 4..    data   u8[]        avail = len - 4 bytes actually present

and the kernel folds `nrow * ncol` elements at `data[i*ncol + j]`. The check
that R1 omits, and the only line it omits, is

    if (nrow * ncol > avail) return 0;      /* computed in 64 bits */

Five things about the sizes are deliberate and must survive any edit.

  * **`small` and `large` have different strides AND different `ncol`** --
    (498, 26) and (3969, 61). Three independent reasons:
      - `work_per_call` *is* the stride, and `harness/check.py`'s
        `d(Ir)/d(work)` assertion needs two probe shapes with **different**
        `work_per_call` or it cannot run at all;
      - the safe-vs-unsafe delta varies with the residue of the measured
        length (`.memory/01-ladder.md`), and quoting one residue as if it were
        the number has been the mistake three times;
      - **and on p05 the modulus that matters is a vector width, not an unroll
        factor.** p05's inner loop is the first in this project that actually
        vectorises (NOTES.md 1), so `ncol mod 8` (LLVM: VW 4 x IC 2) and
        `ncol mod 16` (gcc: one 16-byte `movdqu` per iteration) are what govern
        the scalar epilogue. `_check_residues()` therefore asserts the pairs
        differ mod 4, 8, 16 **and 32**, on the stride, on `ncol`, on `nrow` and
        on the element count -- one modulus more than p16/p17 checked.
  * **`nrow * ncol == avail` exactly on both measured inputs** (19 x 26 = 494 =
    498 - 4; 65 x 61 = 3965 = 3969 - 4). So `work_per_call = stride` is a
    *strict over-estimate* of the bytes folded, by exactly the 4 header bytes,
    and the derived `Ir` floor errs strict -- p16's direction, not p17's. See
    `../model.py`'s `work_per_call` docstring.
  * **the strides are not powers of two and `ncol` is odd-shaped**, so rows are
    not 8- or 16-byte aligned and consecutive rows start at different alignments
    (`ncol = 26` and `61` are both != 0 mod 16). A matrix row on the wire is not
    aligned; pretending otherwise would flatter every rung equally but measure
    something else.
  * **every adversarial input is exactly one window** (`n_blob == stride`), for
    p16's and p17's reason: `k = (acc * nwin) >> 64` is pseudo-random over
    `[0, nwin)`, so with several windows the malformed one is hit only
    probabilistically, and an overrun from a *middle* window stays inside the
    allocation -- a silent wrong answer, no ASan, and a gate that passes by luck.
    With `nwin == 1`, `k` is always 0 and `off` is always 0.
  * **window 0 must serve something** on every input where anything is meant to
    be visited (p17, `.memory/01-ladder.md` finding 5): a window returning 0 pins
    `acc` at 0, and `k = (acc * nwin) >> 64` is then 0 for ever -- the driver's
    Lemire index has an absorbing state at `acc == 0`. On `small`/`large` every
    window folds a full matrix, so this is satisfied by construction. On the
    adversarial inputs there is only one window, so `k == 0` regardless and the
    absorbing state is harmless -- but it is why `adversarial-zero` is one
    window and not several.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run and discards whatever is declared here, so the Miri cost of a row
is `4 x (bytes folded per call)` = `4 x nrow * ncol`, i.e. 1976 on `small` and
15 860 on `large`, against a measured budget of ~3 M folded bytes at ~16 900 B/s
over 180 s. Two orders of magnitude clear, so every p05 row is Miri-checkable.
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

HDR = 4                                   # nrow:u16 + ncol:u16

# The two measured shapes. `nrow * ncol` tiles the window exactly.
SMALL_NROW, SMALL_NCOL, SMALL_WINS = 19, 26, 32
LARGE_NROW, LARGE_NCOL, LARGE_WINS = 65, 61, 2115

# One modulus more than p16 and p17 checked: p05's inner loop vectorises, so 8
# (LLVM's VW 4 x IC 2) and 16 (gcc's `movdqu`) are live, and 32 is what an AVX2
# build would use if this project ever passes `-march`.
RESIDUE_MODULI = (4, 8, 16, 32)


def small_stride():
    return HDR + SMALL_NROW * SMALL_NCOL          # 498


def large_stride():
    return HDR + LARGE_NROW * LARGE_NCOL          # 3969


def _check_residues():
    """Every measured pair must differ modulo every modulus that has ever bitten
    this project, plus 32. Returns a list of problems (empty when healthy).

    p01's first draft used 500 and 4096, both == 0 (mod 4), the single worst
    residue for R2, and overstated it 2.4x. p02's used 61 and 4092, which differ
    mod 4 and mod 8 -- and that was still not enough, because the modulus that
    governed its copy epilogue was 16. p16's turned out to be 4, p17's 4.

    **p05's is a vector width and there is more than one of them**, because
    different back ends pick different widths on the same source: measured at
    TASK_013, LLVM takes 8 elements per iteration (VW 4, interleave 2) and gcc
    takes 16 (one `movdqu`). Both epilogues are therefore live at once, so the
    pairs are checked against 4, 8, 16 and 32 on **four** quantities: the
    stride (`work_per_call`), `ncol` (the *inner*, vectorised loop's trip
    count), `nrow` (the outer loop's), and `nrow * ncol` (what an O(n) claim
    would be denominated in)."""
    bad = []
    pairs = [("stride", small_stride(), large_stride()),
             ("ncol", SMALL_NCOL, LARGE_NCOL),
             ("nrow", SMALL_NROW, LARGE_NROW),
             ("elements folded per call",
              SMALL_NROW * SMALL_NCOL, LARGE_NROW * LARGE_NCOL)]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


def window(rng, nrow, ncol, data_len):
    """One window: the two declared dimensions, then `data_len` random bytes.

    `nrow`/`ncol` are written verbatim rather than derived from `data_len`, so
    that `adversarial-dims` can declare a matrix the window cannot hold -- which
    is the whole pattern."""
    w = bytearray()
    w += nrow.to_bytes(2, "little")
    w += ncol.to_bytes(2, "little")
    w += rng.randbytes(data_len)
    return bytes(w)


def tiled(rng, nwin, nrow, ncol, data_len):
    """`nwin` windows, identical in *shape* and different in *content*.

    The shape is fixed so `work_per_call` is one scalar; the data bytes differ
    per window so the checksum depends on which window the driver picked, which
    is what keeps the anti-collapse barrier honest."""
    out = bytearray()
    for _ in range(nwin):
        out += window(rng, nrow, ncol, data_len)
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-dims: the declared matrix does not fit ---------------------
#
#   len = 68, avail = 64, nrow = 8, ncol = 64  ->  nrow*ncol = 512 > 64
#
# R1 omits `nrow*ncol > avail` and therefore folds 512 bytes out of a 68-byte
# blob: 448 bytes past the end of the allocation. One window, so `off == 0` and
# the overrun is deterministic rather than a coin flip on `k`.
#
# 512 rather than 2^31: the point is a *detectable* overrun, not a long one.
# ASan reports the first byte past the region and stops; a plain build reads
# heap it does not own and prints a wrong number.
DIMS_LEN, DIMS_NROW, DIMS_NCOL = 68, 8, 64

# ---- adversarial-ovf: the check written in the wrong width ------------------
#
#   nrow = ncol = 65535  ->  nrow*ncol = 4 294 836 225
#
# In `size_t`/`u64` that is 4.29e9 and is greater than any `avail` this
# benchmark can present, so **every shipped rung rejects the window and returns
# 0**, R1 included -- R1 omits the check, but with ncol = 65535 > avail its
# very first row already leaves the window, so this input is not what R1's bug
# is demonstrated on (`adversarial-dims` is). What this input is for is the
# *hardened-wrong* cell: the same check written in a narrower type.
#
# **And the width that actually breaks is `int`, not `unsigned`.** With u16
# dimension fields the product is at most 65535 * 65535 = 4 294 836 225 =
# 2^32 - 131 071, which **fits in `uint32_t`** -- an unsigned 32-bit check is
# therefore NOT fooled by any input this format can express. It exceeds INT_MAX
# by 2 147 352 577, so a *signed* `int` product overflows (UB; in practice it
# wraps to -131 071), the test `-131071 > 64` is false, and the wrong check
# waves the window through. NOTES.md 6 builds that variant and measures it.
OVF_LEN, OVF_NROW, OVF_NCOL = 72, 65535, 65535

# ---- adversarial-zero: a dimension of zero ----------------------------------
#
#   nrow = 65535, ncol = 0  ->  nrow*ncol = 0 <= avail, so the SIZE check passes
#
# and the `nrow == 0 || ncol == 0` guard is what stops the kernel walking 65535
# empty rows per call. Note what that guard is and is not: it changes **no
# answer** -- an empty fold returns 0 either way -- so it is not a correctness
# check and not a memory-safety check. It is a *work* check, and this input is
# what makes it load-bearing. See ../spec.md, "The zero guard is a DoS guard".
ZERO_LEN, ZERO_NROW, ZERO_NCOL = 68, 65535, 0

# `--sweep`: (nrow, first_ncol, n_ncols, nwin, n_iters). Diagnostic only;
# `harness/check.py` and `harness/measure.py` both skip the `sweep-` prefix.
#
# **64 consecutive `ncol` per band, not 34.** p16 and p17 swept two full cycles
# of 16 because 16 was the widest modulus in play. Here the widest is 32, and
# more importantly the *period is what the sweep has to establish* -- LLVM and
# gcc pick different vector widths on the same source, so a sweep that assumed
# one of them would be assuming the answer. 64 points is two full cycles of 32,
# four of 16 and eight of 8, which distinguishes all three.
#
# **Band C is a third `nrow`, and it exists because two are not a fit.** Bands A
# and B give two values of `nrow`, and any cost of the form `a + b*nrow` can be
# solved exactly from two points -- a zero-degrees-of-freedom interpolation,
# which `.memory/01-ladder.md` is explicit is not a prediction. Band C holds
# `ncol` to one cycle and moves `nrow` to a value neither of the others used, so
# the `a + b*nrow` model has somewhere to be wrong. It is short on purpose: the
# question it answers is out-of-sample accuracy, not shape.
SWEEP_CYCLES = 2
SWEEP_BANDS = ((19, 24, RESIDUE_MODULI[-1] * SWEEP_CYCLES, 32, 25_000),
               (65, 56, RESIDUE_MODULI[-1] * SWEEP_CYCLES, 512, 8_000),
               (41, 24, RESIDUE_MODULI[-2], 32, 20_000))

# ---- band D: the `nrow` AXIS, added at TASK_021 -----------------------------
#
# **Bands A-C sweep `ncol` and sample `nrow`.** Between them they give `nrow` in
# {19, 41, 65} and nothing else, so every law of the form `a + b*nrow` that this
# pattern publishes -- `R3ship - R4ship = 6*nrow + 9` is the headline one -- rests
# on **three points**. That is one degree of freedom against a two-parameter
# model, and it is exactly the shape that has already cost this project two
# retractions: p16's `nrec + 3` and p05's own `+11.00 flat` were both fits over
# three or fewer values of the axis they were quoted in, and both flipped on the
# next point measured (`.memory/01-ladder.md` finding 6; NOTES.md 12c). Band C's
# own comment says two points cannot be wrong -- three can only be wrong in one
# direction.
#
# Band D moves `nrow` over **nine consecutive values plus two distant ones** at
# **three `ncol` residue classes**, which is p16's TASK_020 band shape. `ncol` is
# held to {30, 32, 33} = {6, 0, 1} mod 8, so the class LLVM peels a full extra
# vector iteration for (`ncol = 0 mod 8`, NOTES.md 2a) is in the band rather than
# assumed away; `nrow` is small on purpose, because the quantity under test is
# the *slope* and small `nrow` keeps the sweep cheap enough to run every
# variant on every blob.
#
# It is appended **after** bands A-C and the RNG is drawn sequentially, so every
# one of the 150 files that existed before this band is byte-identical after it
# (verified by md5 over all 150, TASK_021). The blobs are gitignored; this
# generator is what is committed -- and since TASK_021 `harness/check.py` hashes
# it into `source_sha256`, so a law measured on these blobs is no longer
# re-derivable from a file the gate record cannot see.
SWEEP_NROWS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16)
SWEEP_NROW_NCOLS = (30, 32, 33)
SWEEP_NROW_BAND = (32, 20_000)          # nwin, n_iters


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-c*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p05 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {small_stride()}/{large_stride()}, ncol "
          f"{SMALL_NCOL}/{LARGE_NCOL}, nrow {SMALL_NROW}/{LARGE_NROW} and "
          f"elements {SMALL_NROW * SMALL_NCOL}/{LARGE_NROW * LARGE_NCOL} "
          "differ mod " + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 498 B = 15.6 KiB, so the whole working set fits this
    # box's 32 KiB L1 and the row is latency-free. 494 bytes folded per call,
    # as a 19 x 26 matrix: 3 full LLVM vector iterations per row plus a 2-element
    # scalar epilogue.
    write("small.bin", 25_000, small_stride(),
          tiled(rng, SMALL_WINS, SMALL_NROW, SMALL_NCOL,
                small_stride() - HDR))
    # large: 2115 windows x 3969 B = 8.0 MiB, 8x this box's 1 MiB L2. The window
    # the driver picks is pseudo-uniform over the whole blob, so every call is a
    # cold 4 KiB fold. 3965 bytes per call, as a 65 x 61 matrix: 7 full vector
    # iterations per row plus a 5-element epilogue.
    write("large.bin", 12_000, large_stride(),
          tiled(rng, LARGE_WINS, LARGE_NROW, LARGE_NCOL,
                large_stride() - HDR))

    # ---- adversarial ------------------------------------------------------
    # n_iters is small: R1 is executing undefined behaviour on `dims`, and there
    # is nothing to learn from doing it 25 000 times.

    # (1) THE pattern. The header declares a matrix that does not fit.
    write("adversarial-dims.bin", 8, DIMS_LEN,
          window(rng, DIMS_NROW, DIMS_NCOL, DIMS_LEN - HDR))

    # (2) the width the check is written in. Every shipped rung rejects; the
    #     `int`-typed variant in NOTES.md 6 does not.
    write("adversarial-ovf.bin", 8, OVF_LEN,
          window(rng, OVF_NROW, OVF_NCOL, OVF_LEN - HDR))

    # (3) a zero dimension. Every rung returns 0 on every call and prints 0.
    write("adversarial-zero.bin", 8, ZERO_LEN,
          window(rng, ZERO_NROW, ZERO_NCOL, ZERO_LEN - HDR))

    # (4) stride 3: a window too small to hold the 4-byte header. The driver
    #     guard `stride_w >= 4` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after ZERO kernel calls. Distinct from (3), where
    #     the calls happen and the kernel is what rejects.
    write("adversarial-stride3.bin", 8, 3,
          tiled(rng, 8, 1, 1, 5))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        # The two bands overlap in `ncol` (24..87 and 56..119) on purpose -- the
        # question is whether the period depends on the *inner* trip count
        # alone -- so the file name has to carry `nrow` as well or band B
        # silently overwrites half of band A.
        for nrow, first, n, nwin, iters in SWEEP_BANDS:
            for nc in range(first, first + n):
                write(f"sweep-r{nrow}c{nc}.bin", iters, HDR + nrow * nc,
                      tiled(rng, nwin, nrow, nc, nrow * nc))
        # Band D, LAST so bands A-C stay byte-identical (see SWEEP_NROWS).
        # Same name shape, so one parser reads every sweep blob; no `nrow` here
        # collides with 19, 41 or 65.
        nwin, iters = SWEEP_NROW_BAND
        for nr in SWEEP_NROWS:
            for nc in SWEEP_NROW_NCOLS:
                write(f"sweep-r{nr}c{nc}.bin", iters, HDR + nr * nc,
                      tiled(rng, nwin, nr, nc, nr * nc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
