#!/usr/bin/env python3
"""Generate p06's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p06-rotate/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p06-rotate/inputs/gen.py --sweep     # + the five sweep bands

Payload layout (../spec.md), p11's/p16's/p17's/p05's/p07's/p03's/p12's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nrec  u32 LE     declared record count   ATTACKER DATA
    byte 4..     records, each:  u32 LE nelem ; u32 LE r ; nelem bytes

and the kernel copies `m = min(nelem, SCR)` bytes into a fixed `scr[SCR]`,
rotates `scr[0..m]` left by `r` as three in-place reverses, and folds it. The
line R1 omits, and the only thing it omits, is the REDUCTION of the rotate
amount:

    R1   /* nothing */                          reverse(0,r); reverse(r,m); reverse(0,m)
    R1h  if (m != 0) r %= m; else r = 0;        reverse(0,r); reverse(r,m); reverse(0,m)

--------------------------------------------------------------------------
TWO REGIMES, SEPARATED BY SCR, AND ONLY ONE OF THEM IS A MEMORY-SAFETY EVENT
--------------------------------------------------------------------------
`m <= r < SCR`  -- REGIME 1. `reverse(scr, 0, r)` touches `scr[0 .. r)`, which
                  is INSIDE the array. Nothing overruns, no sanitizer fires,
                  nothing panics, and the answer is wrong. `adversarial-inarray`.
`SCR <= r`      -- REGIME 2. The first reverse walks off the end of the fixed
                  local. `adversarial-past1` / `-past48` / `-pastfar` are one
                  row per observability regime, the ladder p12 established
                  (silent / canary / SIGSEGV, and the boundaries differ by
                  compiler). Re-scanned for p06 by `controls/regime_probe.py`.

**p06 does NOT inherit `.memory/02-bench-rules.md`'s WRITE rule**, and the
threshold test in that section is what decides it: the guard's threshold here is
`m = min(nelem, SCR)`, which is at most and usually strictly *inside* the
destination's extent `SCR`. So "the guard fired" and "the unguarded rung
committed UB" are INDEPENDENT events, and regime 1 is exactly the set where they
separate. p12/p23/p25 inherit because their threshold IS the extent; p06 sits
with p24.

--------------------------------------------------------------------------
WHY small AND large HAVE EVERY r < m
--------------------------------------------------------------------------
`harness/check.py` requires every cell, R1 included, to print `model.py`'s
checksum on every non-adversarial MATRIX input. With `r < m` the reduction is
semantically a no-op, so R1 and R1h compute the same rotation and agree -- which
is what makes the perf rows a measurement of the safety line's PRICE rather than
of two different kernels. (`degenerate` is also an agreeing row, deliberately:
`r == m` reduces to 0 and the unreduced triple composes to the identity too.)

--------------------------------------------------------------------------
small AND large: DIFFERENT RESIDUES, AND small IS LENGTH-HETEROGENEOUS
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues, and
`.memory/03-measurement.md`'s queue item 11 says no pattern ships a
length-heterogeneous band. p06's records carry their own `nelem`, so the natural
place is here:

  * `small`: 5 records, `nelem` 13/47/29/61/7 -- five DIFFERENT lengths in one
    window, mean 31.4, stride 201;
  * `large`: 12 records, `nelem` 1..8, mean 4.33, stride 152.

`_check_residues()` asserts that `nrec`, the copied bytes and the stride differ
mod 4, 8, 16 and 32 between the two, that the mean `m` straddles 16, that every
`r < m`, and that `small` really is heterogeneous.

The parity of `r` is a regressor here and not an afterthought: a reverse of a
half-open range of length `L` runs `ceil(L/2)` iterations, so the three reverses
cost `m + [m even AND r odd]` swaps. Both perf inputs therefore carry a MIX of
`r` parities, and `_check_residues()` asserts that the two inputs' odd-`r`
counts differ.
"""

import argparse
import os
import random
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

HDR = 4                                   # nrec:u32
REC_HDR = 8                               # nelem:u32 ; r:u32
SCR = 64                                  # must equal every rung's SCR

# The two measured shapes. `(nelem, r)` per record, fixed across the windows of
# a blob so that `work_per_call` is one scalar; only the DATA BYTES differ per
# window, which is what keeps the driver's anti-collapse barrier honest.
SMALL_RECS = ((13, 5), (47, 20), (29, 13), (61, 34), (7, 2))
SMALL_WINS = 64                              # 64 x 201 B = 12.6 KiB, inside L1
LARGE_RECS = ((3, 1), (5, 3), (1, 0), (7, 5), (2, 1), (6, 4),
              (4, 2), (8, 6), (3, 2), (5, 1), (1, 0), (7, 3))
LARGE_WINS = 50000                           # 50000 x 152 B = 7.25 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 60000, 20000
ADV_ITERS = 8                             # R1 executes UB on three of them;
                                          # there is nothing to learn from doing
                                          # it 100 000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


def stride_of(recs):
    """4 header bytes + 8 per record + the record data bytes."""
    return HDR + sum(REC_HDR + nelem for nelem, _ in recs)


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and both must have every `r < m`. Returns a list of problems."""
    bad = []
    for label, recs in (("small", SMALL_RECS), ("large", LARGE_RECS)):
        for nelem, r in recs:
            m = min(nelem, SCR)
            if not (m == 0 or r < m):
                bad.append(f"{label} has a record with r={r} >= m={m}; the "
                           f"reduction would not be a no-op there and R1 could "
                           f"not agree with the model -- see this file's header")
    sm = [min(n, SCR) for n, _ in SMALL_RECS]
    lm = [min(n, SCR) for n, _ in LARGE_RECS]
    if len(set(sm)) < len(sm):
        bad.append("small is not length-heterogeneous; its whole point is that "
                   "every record has a different nelem (queue item 11)")
    smean, lmean = sum(sm) / len(sm), sum(lm) / len(lm)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean m ({smean:.2f}, {lmean:.2f}) are on "
                   f"the same side of 16; the two inputs would measure the same "
                   f"shape of copy, rotate and fold")
    sodd = sum(1 for n, r in SMALL_RECS if r % 2 and min(n, SCR) % 2 == 0)
    lodd = sum(1 for n, r in LARGE_RECS if r % 2 and min(n, SCR) % 2 == 0)
    if sodd == lodd:
        bad.append(f"small and large carry the same number of odd-r records at "
                   f"even m ({sodd}); that count is the [m even AND r odd] term "
                   f"of the swap law and must differ between the two inputs")
    pairs = [("nrec", len(SMALL_RECS), len(LARGE_RECS)),
             ("copied bytes per call", sum(sm), sum(lm)),
             ("stride", stride_of(SMALL_RECS), stride_of(LARGE_RECS))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


# ---------------------------------------------------------------- content ----

def record(rng, nelem_decl, r, ndata=None):
    """One record: the declared element count, the rotate amount, the bytes.

    `nelem_decl` is written verbatim and `ndata` defaults to it, so a row can
    declare a count the window does not hold."""
    n = nelem_decl if ndata is None else ndata
    return struct.pack("<II", nelem_decl, r) + rng.randbytes(n)


def window(nrec_decl, recs):
    """A window: the declared record count, then the records.

    `nrec_decl` is written verbatim rather than derived from `recs` so that a
    row can declare a count the window does not hold."""
    return struct.pack("<I", nrec_decl) + b"".join(recs)


def tiled(rng, nwin, recs):
    """`nwin` windows, identical in *shape* and different in *content*."""
    out = bytearray()
    for _ in range(nwin):
        out += window(len(recs), [record(rng, n, r) for n, r in recs])
    return bytes(out)


# ---------------------------------------------------------------- oracle -----

MASK = (1 << 64) - 1


def kernel_result(win):
    """The CHECKED kernel, on one window, in twenty lines.

    Used only by `_no_zero_window()` below. It is deliberately NOT imported from
    `../model.py`: `gen.py` must be runnable on its own, and a generator that
    shares the oracle's code cannot check the oracle."""
    ln = len(win)
    if ln < HDR:
        return 0
    nrec = int.from_bytes(win[:4], "little")
    if nrec == 0:
        return 0
    scr, acc, p = bytearray(SCR), 0, HDR
    for _ in range(nrec):
        if ln - p < REC_HDR:
            break
        nelem = int.from_bytes(win[p:p + 4], "little")
        r = int.from_bytes(win[p + 4:p + 8], "little")
        p += REC_HDR
        m = min(nelem, SCR)
        if ln - p < nelem:
            break
        scr[:m] = win[p:p + m]
        p += nelem
        r = r % m if m else 0
        scr[:r] = scr[:r][::-1]
        scr[r:m] = scr[r:m][::-1]
        scr[:m] = scr[:m][::-1]
        for i in range(m):
            acc = (acc * 31 + scr[i]) & MASK
        acc = (acc * 31 + m) & MASK
    return (acc * 31 + nrec) & MASK


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12 and p06 check it,
    which is strictly stronger and costs one pass over the blob at generation
    time."""
    for w in range(len(body) // stride):
        if kernel_result(body[w * stride:(w + 1) * stride]) == 0:
            return [f"window {w} returns 0; the driver's Lemire index has an "
                    f"absorbing state there"]
    return []


def write(name, n_iters, stride, body, declared_len=None, check_zero=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-inarray: REGIME 1, the bug nothing sees --------------------
#
# Two records, both with `m <= r < SCR`: the unreduced first reverse touches
# `scr[0 .. r)` with `r <= 63`, which is INSIDE the 64-byte scratch. R1 and R1h
# therefore compute different rotations with no diagnostic anywhere -- no
# out-of-bounds access, no sanitizer report, no panic in the safe rungs, and no
# panic in the delete-the-check CONTROLS either, which is the finding
# (`controls/gen_controls.py`, ../NOTES.md 7).
#
# The third record is the BOUNDARY FROM THE SAFE SIDE and it is one past where
# TASK_047 put it: `reverse(scr, 0, r)` swaps `scr[i]` with `scr[r-1-i]`, so the
# highest index it touches is `r - 1`. At `r == SCR == 64` that is 63 and the
# rung is still inside the array. **The regime boundary is `r > SCR`, not
# `r >= SCR`.** ../NOTES.md 0.
INARRAY_RECS = ((16, 40), (32, 50), (8, 64))

# ---- adversarial-past*: REGIME 2, the ladder in overflow magnitude ----------
#
# `r >= SCR`, so `reverse(scr, 0, r)` swaps `scr[i]` with `scr[r-1-i]` and the
# high half of that walks off the fixed local. The number of bytes written past
# the array is `r - SCR` (rounded to the swap that reaches them), so `r` names
# the magnitude directly. Boundaries measured by `controls/regime_probe.py`.
PAST1_RECS = ((16, 65),)         # +1  byte past
PAST48_RECS = ((16, 112),)       # +48 bytes past
PASTFAR_RECS = ((16, 100000),)   # +99936 bytes past: the frame is gone

# ---- degenerate: m == 0, r == 0, r == m, nelem > SCR ------------------------
#
# Every record here is one every rung agrees on, R1 included, which is why the
# file is NOT named `adversarial-*` and the gate holds all eight cells to the
# model's checksum on it:
#
#   (0,  0)   m == 0. The hardened rungs would DIVIDE BY ZERO here, and the
#             contract pins the answer: `if m != 0 { r %= m } else { r = 0 }`.
#             R1 has no division at all, so this record is where R1h's guard
#             does work R1 never needed.
#   (20, 0)   r == 0: the first reverse is skipped entirely (its loop preamble
#             is 3 Ir/record on clang), so this is the third case of the
#             `sweep-r*` law and not a member of "r even".
#   (12, 12)  r == m. Reduced it is 0; UNREDUCED the triple is
#             reverse(0,12) ; reverse(12,12)=no-op ; reverse(0,12) = identity,
#             so R1 agrees here by composition rather than by luck.
#   (100, 7)  nelem > SCR: `m = min(nelem, SCR)` clamps the COPY in every rung
#             including R1, so the 36 undeclared bytes are skipped by the cursor
#             and never read. The clamp is not the safety line.
DEGENERATE_RECS = ((0, 0), (20, 0), (12, 12), (100, 7))

# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nrec`. The
# guard skips the loop entirely, so every rung prints 0 after ZERO kernel calls.
STRIDE3_BLOB = 30

# `--sweep`: five bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure). Appended LAST so the eight matrix blobs
# stay byte-identical when a band is added.
#
# Band M -- the ROTATED EXTENT axis. `nrec` held at 8, `r` held at 2, `m` swept
#           1..48. Isolates the per-copied/rotated/folded-byte terms.
SWEEP_M_NREC, SWEEP_M_R, SWEEP_M_MS = 8, 2, tuple(range(1, 49))
# Band N -- the RECORD-COUNT axis. `m` held at 16, `r` at 2, `nrec` swept 1..24.
SWEEP_N_M, SWEEP_N_R, SWEEP_N_KS = 16, 2, tuple(range(1, 25))
# Band R -- ITEM 3's FALSIFIER. `m` held, `r` swept over the whole legal range.
#           Two sub-bands, because the swap law's `r` term is a PARITY term that
#           exists only at even `m`:
#             e32  m = 32 (even), r = 0 .. 31
#             o31  m = 31 (odd),  r = 0 .. 30
SWEEP_R_NREC = 8
SWEEP_R_EVEN_M, SWEEP_R_ODD_M = 32, 31
# Band X -- p04's band X: every regressor non-zero at once, so the pooled design
#           has full rank, plus a WITHIN-BAND NEGATIVE CONTROL (`x08b`) whose
#           regressors are identical to `x08a`'s and whose bytes differ, for
#           which the predicted delta is exactly 0.
SWEEP_X_SHAPES = {
    "x04": ((5, 1), (12, 7), (33, 0), (64, 63)),
    "x06": ((1, 0), (7, 3), (18, 17), (40, 8), (57, 2), (64, 1)),
    "x08a": ((2, 1), (9, 4), (16, 15), (23, 0), (31, 30), (44, 9), (52, 3), (61, 60)),
    "x08b": ((2, 1), (9, 4), (16, 15), (23, 0), (31, 30), (44, 9), (52, 3), (61, 60)),
    "x11": ((3, 2), (6, 1), (10, 9), (14, 0), (19, 18), (25, 6), (30, 29),
            (37, 4), (43, 42), (50, 11), (64, 33)),
}
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p06 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sm = [min(n, SCR) for n, _ in SMALL_RECS]
    lm = [min(n, SCR) for n, _ in LARGE_RECS]
    print(f"  residues ok: nrec {len(SMALL_RECS)}/{len(LARGE_RECS)}, copied "
          f"bytes {sum(sm)}/{sum(lm)}, strides "
          f"{stride_of(SMALL_RECS)}/{stride_of(LARGE_RECS)}, mean m "
          f"{sum(sm)/len(sm):.2f}/{sum(lm)/len(lm):.2f}, m "
          f"{min(sm)}..{max(sm)}/{min(lm)}..{max(lm)}, distinct m "
          f"{len(set(sm))}/{len(set(lm))}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_RECS),
          tiled(rng, SMALL_WINS, SMALL_RECS))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_RECS),
          tiled(rng, LARGE_WINS, LARGE_RECS))

    # ---- adversarial ------------------------------------------------------
    for name, recs in (("adversarial-inarray", INARRAY_RECS),
                       ("adversarial-past1", PAST1_RECS),
                       ("adversarial-past48", PAST48_RECS),
                       ("adversarial-pastfar", PASTFAR_RECS),
                       ("degenerate", DEGENERATE_RECS)):
        write(f"{name}.bin", ADV_ITERS, stride_of(recs),
              window(len(recs), [record(rng, n, r) for n, r in recs]))

    # stride 3: a window too small to hold the 4-byte header. The driver guard
    # skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3, rng.randbytes(STRIDE3_BLOB),
          check_zero=False)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for m in SWEEP_M_MS:
            recs = tuple((m, SWEEP_M_R % m if m else 0)
                         for _ in range(SWEEP_M_NREC))
            write(f"sweep-m{m:02d}n{SWEEP_M_NREC:02d}.bin", SWEEP_ITERS,
                  stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for k in SWEEP_N_KS:
            recs = tuple((SWEEP_N_M, SWEEP_N_R) for _ in range(k))
            write(f"sweep-n{k:02d}m{SWEEP_N_M:02d}.bin", SWEEP_ITERS,
                  stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for tag, m in (("e", SWEEP_R_EVEN_M), ("o", SWEEP_R_ODD_M)):
            for r in range(m):
                recs = tuple((m, r) for _ in range(SWEEP_R_NREC))
                write(f"sweep-r{tag}{m:02d}v{r:02d}.bin", SWEEP_ITERS,
                      stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for tag, recs in SWEEP_X_SHAPES.items():
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(recs),
                  tiled(rng, SWEEP_WINS, recs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
