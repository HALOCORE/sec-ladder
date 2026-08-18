#!/usr/bin/env python3
"""Generate p08's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p08-overlap-move/inputs/gen.py

Payload layout (../spec.md), p05's and p17's verbatim:

    word 0     u64  stride     bytes per window; the kernel folds one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..2   d       u16 LE     the shift distance      ATTACKER DATA
    byte 2..4   nrep_w  u16 LE     the layer count         ATTACKER DATA
    byte 4..    data    u8[]       avail = len - 4 bytes actually present

and the kernel copies `m = min(avail, 4096)` of them into a fixed 4096-byte
scratch and shifts that scratch right `nrep = 1 + nrep_w % 4` times, by
`dr = d + r` on round `r`. The move is `scr[dr..m] <- scr[0..m-dr]`; R1 spells
it `memcpy` and every other rung `memmove`.

**The design decision that governs every size below: the ranges overlap exactly
when `2*dr < m`.** So:

  * on `small` and `large`, `d >= ceil(m/2)` -- **no round overlaps**, `memcpy`
    and `memmove` agree, every rung produces the same checksum, and the perf
    rows compare like with like. `d = ceil(m/2)` exactly (bumped to the next
    residue class where needed), because that maximises the move length
    `n = m - d` subject to non-overlap and therefore the move's share of the
    call;
  * `adversarial-overlap` sets `d = 3` against `m = 4089`, so all four rounds
    overlap by more than 4 KiB and R1 executes the undefined behaviour.

That is not dodging the bug. The overlap is *attacker-controlled* because `d`
comes from the file, and separating the perf rows from the harm row is what
lets both be measured.

It also protects the measurement. `k = (acc * nwin) >> 64` is derived from the
previous result, so a rung whose checksum diverged would visit *different
windows* and stop being comparable. Adversarial inputs are exactly one window
(`n_blob == stride`, so `nwin == 1` and `k == 0` always), which is p16's and
p17's rule doing a second job here: divergence on an adversarial input cannot
change which window anything looks at.

Five further things are deliberate and must survive any edit.

  * **`small` and `large` differ in stride, in `m`, in `d` and in the first
    round's move length `n0 = m - d`, modulo 4, 8, 16 and 32.** `work_per_call`
    *is* the stride, and `harness/check.py`'s `d(Ir)/d(work)` assertion needs
    two probe shapes with different `work_per_call` or it cannot run at all;
    and quoting one residue as if it were a constant has been this project's
    most repeated mistake (`.memory/01-ladder.md` finding 3: p01's residues
    were both 0 mod 4, p02's modulus turned out to be 16, p05's 8).
    `_check_residues()` asserts all four moduli on all four quantities.
    **The one quantity that is NOT checked is the total moved per call**, and
    that is not an oversight: with `nrep = 4` the total is
    `sum(m - d - r for r in 0..4) = 4*(m-d) - 6`, which is `== 2 (mod 4)` for
    every choice of `m` and `d`, so it cannot be put in two residue classes at
    all. `n0` is checked in its place.
  * **`nrep = 4` on both measured inputs** (the mask `1 + nrep_w % 4` is
    saturated), so the move is four calls per kernel call rather than one and
    the thing p08 is named after is as large a share of the call as the design
    permits. NOTES.md 2 reports the share it actually reached.
  * **every adversarial input is exactly one window**, for the reason above.
  * **window 0 must serve something** on the measured inputs (p17,
    `.memory/01-ladder.md` finding 5): a window returning 0 pins `acc` at 0 and
    `k = (acc * nwin) >> 64` is then 0 for ever -- the driver's Lemire index has
    an absorbing state at `acc == 0`. Every window of `small`/`large` holds a
    well-formed shift, so this is satisfied by construction.
  * **`m = avail` on every input here**, i.e. `avail < 4096`, so the measured
    length is genuinely file-derived and `m` is never the compile-time constant
    `SCR`. A window with `avail >= 4096` would clamp `m` to 4096 and hand the
    optimiser a constant trip count; the kernel handles it (`m = min(avail,
    SCR)`) and no shipped input exercises it. NOTES.md 8 records that as a
    deliberately unmeasured branch.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run, so the per-call cost is `4096` (the memset) + `m` (the copy in)
+ `4*(m-d) - 6` (the moves) + `m` (the fold) bytes, i.e. ~20.4 KB on `large`,
times 4 iterations = ~82 KB against a measured budget of ~3 M bytes at
~16 900 B/s over 180 s. Two orders of magnitude clear. The payload decoder is
`head1_u64_bytes`, a single bulk `to_vec` -- `.memory/02-bench-rules.md` records
that p01's `large.bin` blocks under Miri because `head_u64_body` decodes element
by element, and p02's larger file does not because its decoder is a `to_vec`.
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

HDR = 4            # d:u16 + nrep_w:u16
SCR = 4096         # the kernel's scratch capacity; mirrored from ../spec.md

# The two measured shapes. `d >= ceil(m/2)` on both, so no round overlaps.
#   small:  m = 498,  d = 251  (2*251 = 502 >= 498)
#   large:  m = 4089, d = 2045 (2*2045 = 4090 >= 4089)
SMALL_M, SMALL_D, SMALL_WINS = 498, 251, 32
LARGE_M, LARGE_D, LARGE_WINS = 4089, 2045, 8192

# Any u16 with the low two bits set gives nrep = 4. Two different values so
# that nothing can be reading a constant.
SMALL_NREPW, LARGE_NREPW = 0x0103, 0x0207

RESIDUE_MODULI = (4, 8, 16, 32)


def _check_residues():
    """Every measured pair must differ modulo every modulus that has bitten this
    project. Returns a list of problems (empty when healthy).

    p01's first draft used 500 and 4096, both == 0 (mod 4), the single worst
    residue for R2, and overstated it 2.4x. p02's modulus turned out to be 16.
    p05's were 8 (LLVM's vector width) and 16 (gcc's).

    **p08's are not known in advance and that is why all four are checked.**
    The move is a `memmove` call whose cost is governed by glibc's internal size
    classes (32 / 64 / 128 / 256 / 512 B and the ERMS threshold), the fold is a
    serial Horner chain LLVM unrolls 4x, and the naive rung's reverse byte loop
    is rolled. Three different periods on one kernel."""
    bad = []
    pairs = [("stride", SMALL_M + HDR, LARGE_M + HDR),
             ("m", SMALL_M, LARGE_M),
             ("d", SMALL_D, LARGE_D),
             ("first-round move length n0 = m - d",
              SMALL_M - SMALL_D, LARGE_M - LARGE_D)]
    for label, a, b in pairs:
        for mod in RESIDUE_MODULI:
            if a % mod == b % mod:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % mod} (mod {mod}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    for label, m, d, nrepw in (("small", SMALL_M, SMALL_D, SMALL_NREPW),
                               ("large", LARGE_M, LARGE_D, LARGE_NREPW)):
        nrep = 1 + (nrepw & 3)
        if 2 * (d + nrep - 1) < m:
            bad.append(f"{label}: round {nrep - 1} overlaps (2*{d + nrep - 1} "
                       f"< {m}); the perf rows must NOT overlap or memcpy and "
                       f"memmove stop agreeing")
        if d + nrep > m or d == 0 or m < 2:
            bad.append(f"{label}: the kernel's own guard rejects this window")
        if m >= SCR:
            bad.append(f"{label}: m = {m} >= SCR = {SCR}, so `m` would be the "
                       f"compile-time constant SCR rather than file data")
    return bad


def window(rng, d, nrep_w, data_len):
    """One window: the shift distance, the layer count, then random bytes.

    `d` is written verbatim rather than derived from `data_len`, so that
    `adversarial-overlap` can declare a distance that makes the ranges overlap
    and `adversarial-dbig` one the guard rejects -- which is the whole
    pattern."""
    w = bytearray()
    w += d.to_bytes(2, "little")
    w += nrep_w.to_bytes(2, "little")
    w += rng.randbytes(data_len)
    return bytes(w)


def tiled(rng, nwin, d, nrep_w, data_len):
    """`nwin` windows, identical in *shape* and different in *content*.

    The shape is fixed so `work_per_call` is one scalar; the data bytes differ
    per window so the checksum depends on which window the driver picked, which
    is what keeps the anti-collapse barrier honest."""
    out = bytearray()
    for _ in range(nwin):
        out += window(rng, d, nrep_w, data_len)
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-overlap: THE pattern -------------------------------------
#
#   stride 4093 -> m = 4089, d = 3, nrep = 4, so dr in {3,4,5,6} and every
#   round copies ~4086 bytes from [0, m-dr) to [dr, m). 2*dr < m by three
#   orders of magnitude: the deepest overlap this format can express.
#
# Note what this input is NOT: it is not out of bounds. The guard
# `d + nrep > m` passes (7 <= 4089), every index is inside the 4096-byte
# scratch, and no rung reads or writes outside an allocation. ASan's
# `heap-buffer-overflow` cannot fire here; what fires is
# `memcpy-param-overlap`, which is a different interceptor entirely.
OVL_M, OVL_D, OVL_NREPW = 4089, 3, 0x0003

# ---- adversarial-dzero: d == 0 --------------------------------------------
#
# A zero shift is a no-op move, and `memcpy(scr, scr, m)` with dst == src is
# *also* undefined behaviour in C (the ranges are identical, hence overlapping)
# even though it cannot corrupt anything. The kernel rejects it rather than
# relying on that: every rung returns 0. Rejecting it is also what makes
# `0 < dr` available as a precondition of the trusted item in verus.rs.
DZERO_M, DZERO_D, DZERO_NREPW = 64, 0, 0x0003

# ---- adversarial-dbig: d + nrep > m ---------------------------------------
#
# A ONE-OFF near miss, not a wild value: d = 61, nrep = 4, m = 64, so
# d + nrep = 65 > 64 by one and the guard rejects. A rung that wrote the guard
# as `d >= m` or `d + nrep >= m` would disagree with the model here.
DBIG_M, DBIG_D, DBIG_NREPW = 64, 61, 0x0003


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    rng = random.Random(SEED)

    print("p08 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_M + HDR}/{LARGE_M + HDR}, m "
          f"{SMALL_M}/{LARGE_M}, d {SMALL_D}/{LARGE_D} and first-round move "
          f"{SMALL_M - SMALL_D}/{LARGE_M - LARGE_D} differ mod "
          + ", ".join(str(x) for x in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 502 B = 15.7 KiB, inside this box's 32 KiB per-core
    # L1d, so the copy in and the fold are latency-free and what is left is the
    # move.
    write("small.bin", 25_000, SMALL_M + HDR,
          tiled(rng, SMALL_WINS, SMALL_D, SMALL_NREPW, SMALL_M))
    # large: 8192 windows x 4093 B = 32.0 MiB, past this box's 27.5 MiB shared
    # L3 (and 32x its 1 MiB per-core L2). The window the driver picks is
    # pseudo-uniform over the whole blob, so every call's copy in is cold --
    # which is the ONLY cache axis p08 has, because the scratch itself is 4 KiB
    # in every cell of the matrix. See ../spec.md, "p08 has no cache axis in the
    # scratch".
    write("large.bin", 8_000, LARGE_M + HDR,
          tiled(rng, LARGE_WINS, LARGE_D, LARGE_NREPW, LARGE_M))

    # ---- adversarial ------------------------------------------------------
    # n_iters is small: R1 is executing undefined behaviour on `overlap`, and
    # there is nothing to learn from doing it 25 000 times.

    # (1) THE pattern. Deep overlap; only R1 is undefined.
    write("adversarial-overlap.bin", 8, OVL_M + HDR,
          window(rng, OVL_D, OVL_NREPW, OVL_M))

    # (2) d == 0: the degenerate distance. Every rung returns 0.
    write("adversarial-dzero.bin", 8, DZERO_M + HDR,
          window(rng, DZERO_D, DZERO_NREPW, DZERO_M))

    # (3) d + nrep > m by exactly one. Every rung returns 0.
    write("adversarial-dbig.bin", 8, DBIG_M + HDR,
          window(rng, DBIG_D, DBIG_NREPW, DBIG_M))

    # (4) stride 3: a window too small to hold the 4-byte header. The driver
    #     guard `stride_w >= 4` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after ZERO kernel calls. Distinct from (2) and
    #     (3), where the calls happen and the kernel is what rejects.
    write("adversarial-stride3.bin", 8, 3, rng.randbytes(24))
    return 0


if __name__ == "__main__":
    sys.exit(main())
