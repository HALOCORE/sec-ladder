#!/usr/bin/env python3
"""Generate p23's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p23-partition/inputs/gen.py            # the 9 matrix inputs
    python3 patterns/p23-partition/inputs/gen.py --sweep     # + the four sweep bands

Payload layout (../spec.md), p06's/p11's/p16's/p17's/p05's/p07's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nrec  u32 LE     declared record count   ATTACKER DATA
    byte 4..     records, each:  u32 LE nelem ; u8 pivot ; u8 pad[3] ; nelem bytes

and the kernel copies `m = min(nelem, SCR)` bytes into a fixed `scr[SCR]`,
partitions `scr[0..m)` around `pivot` with Hoare's nested-scan, and folds the
partitioned prefix and the partition point. The lines R1 omits, and the only
things it omits, are the two `i < j` conjuncts:

    R1   while (        scr[i] <= pv) i++;   while (        scr[j-1] >= pv) j--;
    R1h  while (i < j && scr[i] <= pv) i++;   while (i < j && scr[j-1] >= pv) j--;

--------------------------------------------------------------------------
THREE REGIMES UPWARD, TWO DOWNWARD, AND ONLY THE LAST OF EACH IS A MEMORY EVENT
--------------------------------------------------------------------------
Write `hi` for "some byte of `scr[0..m)` is strictly ABOVE `pv`" and `lo` for
"some byte of `scr[0..m)` is strictly BELOW `pv`". Both are properties of the
DATA, which is what makes this bug class different from every earlier one here:
the missing guard's replacement is not a length, it is a sentinel the input is
assumed to contain.

  UPWARD (`scr[i] <= pv`)
    `hi` holds                     -- R1 stops where R1h stops. AGREEMENT.
    `hi` fails, but some byte of
    the STALE TAIL `scr[m..SCR)` is
    above `pv`                     -- R1 stops INSIDE the array, at an index
                                      past `j`. Wrong answer, exit 0, ASan and
                                      UBSan clean, no panic in any Rust rung.
                                      `adversarial-inarray`.
    no byte of `scr[0..SCR)` is
    above `pv`                     -- R1 reads `scr[SCR]`. `adversarial-allbelow`
                                      (and the `pv == 255` half of
                                      `adversarial-both`).

  DOWNWARD (`scr[j-1] >= pv`)
    `lo` holds                     -- AGREEMENT. (Even when the only such byte
                                      is BELOW the upward cursor: R1 then stops
                                      at a smaller `j` than R1h, both exit the
                                      outer loop, and the folded value is `i`,
                                      which neither scan changed. Checked by
                                      `_agree()` rather than argued.)
    `lo` fails                     -- R1 reaches `j == 0`, evaluates
                                      `scr[j - 1]` with `j - 1` WRAPPED, and
                                      walks away from the frame; the exchange
                                      that follows writes there.
                                      `adversarial-allabove`.

There is no in-bounds middle regime downward, because the scan's own start
`j == m` is already at the top of the live prefix -- it never enters the stale
tail. That asymmetry is the reason this file ships one `inarray` row and not two.

--------------------------------------------------------------------------
WHY EVERY BENIGN RECORD HAS BOTH SENTINELS, AND WHY m >= 2 IS FORCED
--------------------------------------------------------------------------
`harness/check.py` requires every cell, R1 included, to print `model.py`'s
checksum on every non-adversarial MATRIX input. `_agree()` below checks it by
simulation rather than by argument, but the construction makes it true up
front: every benign record is built with at least one byte strictly below the
pivot AND at least one strictly above it.

**A one-element record cannot satisfy that**, so `m == 1` is STRUCTURALLY
adversarial and ships as `adversarial-single` rather than inside `degenerate`.
It is the sharpest row in the file: nothing about it is malformed -- one
element, a pivot, a partition that is trivially already done -- and R1 still
leaves the array, upward if the element is at or below the pivot and downward if
it is above. `m == 0` is fine, because the outer `while (i < j)` never runs.

**The sentinels only have to exist in the FIRST outer iteration.** After the
first exchange, `scr[j] > pv` and `scr[i-1] < pv` for the new cursors, and those
are the sentinels for every later iteration. So "one byte on each side" is the
whole benign condition, and it is a condition on the record, not on the walk.

--------------------------------------------------------------------------
small AND large: DIFFERENT RESIDUES, DIFFERENT PIVOT RANKS
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues, and
p23 has a regressor no earlier pattern has: **the PIVOT'S RANK.** A partition's
work depends on how the data splits, not only on how much of it there is, and
the probe for this row measured the safe-over-unsafe gap moving by a factor of
3.3 across the rank axis at fixed `n`. So `_check_residues()` asserts the two
inputs' mean rank straddles 0.35 as well as the usual moduli, and `--sweep`
ships a whole band (`sweep-k*`) that holds `m` and sweeps the rank.

  * `small`: 5 records, `nelem` 13/47/29/61/7 -- five DIFFERENT lengths in one
    window, 157 copied bytes, stride 201, mean pivot rank 0.44, and 11 bytes
    exactly EQUAL to their pivot (which is what the `<=`/`>=` spelling is about);
  * `large`: 12 records, `nelem` 2..8, 54 copied bytes, stride 154, mean pivot
    rank 0.28, and no byte equal to its pivot.
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
REC_HDR = 8                               # nelem:u32 ; pivot:u8 ; pad:u8[3]
SCR = 64                                  # must equal every rung's SCR

# The two measured shapes: `(nelem, pv, nlow, neq)` per record, where `nlow` is
# how many of the record's bytes are strictly BELOW the pivot and `neq` how many
# are exactly equal to it; the rest are strictly above. Fixed across the windows
# of a blob so that `work_per_call` is one scalar; only the DATA BYTES differ
# per window, which is what keeps the driver's anti-collapse barrier honest.
SMALL_RECS = ((13, 96, 5, 2), (47, 140, 20, 3), (29, 64, 22, 0),
              (61, 200, 12, 5), (7, 33, 3, 1))
SMALL_WINS = 64                              # 64 x 201 B = 12.6 KiB, inside L1
LARGE_RECS = ((3, 60, 1, 0), (5, 90, 1, 0), (2, 120, 1, 0), (7, 150, 1, 0),
              (2, 30, 1, 0), (6, 200, 1, 0), (4, 77, 1, 0), (8, 180, 1, 0),
              (3, 44, 1, 0), (5, 111, 1, 0), (2, 222, 1, 0), (7, 66, 1, 0))
LARGE_WINS = 50000                           # 50000 x 154 B = 7.34 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 60000, 20000
ADV_ITERS = 8                             # R1 executes UB on four of them;
                                          # there is nothing to learn from doing
                                          # it 100 000 times.

RESIDUE_MODULI = (4, 8, 16, 32)
MASK = (1 << 64) - 1


def stride_of(recs):
    """4 header bytes + 8 per record + the record data bytes."""
    return HDR + sum(REC_HDR + r[0] for r in recs)


def _rank(nelem, nlow):
    return nlow / min(nelem, SCR)


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and every benign record must carry both sentinels. Returns a list
    of problems."""
    bad = []
    for label, recs in (("small", SMALL_RECS), ("large", LARGE_RECS)):
        for nelem, pv, nlow, neq in recs:
            m = min(nelem, SCR)
            nhigh = m - nlow - neq
            if nlow < 1 or nhigh < 1:
                bad.append(f"{label} has a record with nlow={nlow} nhigh={nhigh} "
                           f"at m={m}; a benign record needs a byte strictly "
                           f"below AND one strictly above the pivot or R1 leaves "
                           f"the scratch -- see this file's header")
            if not 1 <= pv <= 254:
                bad.append(f"{label} pivot {pv} leaves no room for a byte on "
                           f"one side of it")
    sm = [min(n, SCR) for n, _, _, _ in SMALL_RECS]
    lm = [min(n, SCR) for n, _, _, _ in LARGE_RECS]
    if len(set(sm)) < len(sm):
        bad.append("small is not length-heterogeneous; its whole point is that "
                   "every record has a different nelem (queue item 11)")
    smean, lmean = sum(sm) / len(sm), sum(lm) / len(lm)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean m ({smean:.2f}, {lmean:.2f}) are on "
                   f"the same side of 16; the two inputs would measure the same "
                   f"shape of copy, partition and fold")
    srank = sum(_rank(n, lo) for n, _, lo, _ in SMALL_RECS) / len(SMALL_RECS)
    lrank = sum(_rank(n, lo) for n, _, lo, _ in LARGE_RECS) / len(LARGE_RECS)
    if (srank < 0.35) == (lrank < 0.35):
        bad.append(f"small and large mean PIVOT RANK ({srank:.2f}, {lrank:.2f}) "
                   f"are on the same side of 0.35; the rank is p23's own "
                   f"regressor and the two measured inputs must not hold it "
                   f"fixed -- see this file's header")
    seq = sum(e for _, _, _, e in SMALL_RECS)
    leq = sum(e for _, _, _, e in LARGE_RECS)
    if (seq == 0) == (leq == 0):
        bad.append(f"small and large both {'do' if seq else 'do not'} carry "
                   f"bytes equal to their pivot ({seq}, {leq}); the `<=`/`>=` "
                   f"spelling is exactly what those bytes exercise")
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

def _bytes_for(rng, m, pv, nlow, neq):
    """`m` bytes with exactly `nlow` strictly below `pv`, `neq` equal to it and
    the rest strictly above, shuffled. Raises if the split is impossible."""
    nhigh = m - nlow - neq
    if nlow < 0 or neq < 0 or nhigh < 0:
        raise ValueError(f"impossible split m={m} nlow={nlow} neq={neq}")
    out = ([rng.randrange(0, pv) for _ in range(nlow)]
           + [pv] * neq
           + [rng.randrange(pv + 1, 256) for _ in range(nhigh)])
    rng.shuffle(out)
    return bytes(out)


def record(rng, nelem_decl, pv, nlow, neq=0, ndata=None, raw=None):
    """One record: the declared element count, the pivot byte, three pad bytes,
    then the data bytes.

    `nelem_decl` is written verbatim and `ndata` defaults to it, so a row can
    declare a count the window does not hold. `raw` overrides the generated
    bytes entirely, for the adversarial rows."""
    n = nelem_decl if ndata is None else ndata
    if raw is not None:
        data = raw
    else:
        m = min(n, SCR)
        data = _bytes_for(rng, m, pv, nlow, neq) + rng.randbytes(max(0, n - m))
    return struct.pack("<IBBBB", nelem_decl, pv, 0, 0, 0) + data


def window(nrec_decl, recs):
    """A window: the declared record count, then the records.

    `nrec_decl` is written verbatim rather than derived from `recs` so that a
    row can declare a count the window does not hold."""
    return struct.pack("<I", nrec_decl) + b"".join(recs)


def tiled(rng, nwin, recs):
    """`nwin` windows, identical in *shape* and different in *content*."""
    out = bytearray()
    for _ in range(nwin):
        out += window(len(recs), [record(rng, n, pv, lo, eq)
                                  for n, pv, lo, eq in recs])
    return bytes(out)


# ---------------------------------------------------------------- oracle -----
#
# Deliberately NOT imported from `../model.py`: `gen.py` must be runnable on its
# own, and a generator that shares the oracle's code cannot check the oracle.

def kernel_result(win):
    """The CHECKED kernel (R1h and R2-R5), on one window."""
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
        pv = win[p + 4]
        p += REC_HDR
        m = min(nelem, SCR)
        if ln - p < nelem:
            break
        scr[:m] = win[p:p + m]
        p += nelem
        i, j = 0, m
        while i < j:
            while i < j and scr[i] <= pv:
                i += 1
            while i < j and scr[j - 1] >= pv:
                j -= 1
            if i < j:
                scr[i], scr[j - 1] = scr[j - 1], scr[i]
                i += 1
                j -= 1
        for q in range(m):
            acc = (acc * 31 + scr[q]) & MASK
        acc = (acc * 31 + i) & MASK
    return (acc * 31 + nrec) & MASK


def r1_result(win):
    """R1 (the buggy rung), on one window: `(checksum_or_None, direction)`.

    `direction` is `""` when R1 stayed inside the scratch, `"up"` when its
    upward scan needed `scr[SCR]` and `"down"` when its downward scan needed
    `scr[-1]`; the checksum is `None` in both of those cases, because what R1
    does after leaving the array is not a function of the input."""
    ln = len(win)
    if ln < HDR:
        return 0, ""
    nrec = int.from_bytes(win[:4], "little")
    if nrec == 0:
        return 0, ""
    scr, acc, p = bytearray(SCR), 0, HDR
    for _ in range(nrec):
        if ln - p < REC_HDR:
            break
        nelem = int.from_bytes(win[p:p + 4], "little")
        pv = win[p + 4]
        p += REC_HDR
        m = min(nelem, SCR)
        if ln - p < nelem:
            break
        scr[:m] = win[p:p + m]
        p += nelem
        i, j = 0, m
        while i < j:
            while i < SCR and scr[i] <= pv:      # R1: no `i < j` conjunct
                i += 1
            if i == SCR:
                return None, "up"
            while j > 0 and scr[j - 1] >= pv:    # R1: no `i < j` conjunct
                j -= 1
            if j == 0:
                return None, "down"
            if i < j:
                scr[i], scr[j - 1] = scr[j - 1], scr[i]
                i += 1
                j -= 1
        for q in range(m):
            acc = (acc * 31 + scr[q]) & MASK
        acc = (acc * 31 + i) & MASK
    return (acc * 31 + nrec) & MASK, ""


def _agree(body, stride):
    """R1 must agree with the checked kernel on every window of a benign blob.

    Checked by SIMULATION and not by argument, because the sentinel condition is
    a property of the data and the header's derivation of it is exactly the sort
    of thing that is right until it is not."""
    bad = []
    for w in range(len(body) // stride):
        win = body[w * stride:(w + 1) * stride]
        want = kernel_result(win)
        got, direction = r1_result(win)
        if direction:
            bad.append(f"window {w}: R1 leaves the scratch ({direction}); a "
                       f"benign input must not")
            break
        if got != want:
            bad.append(f"window {w}: R1 {got} != checked {want}; every cell "
                       f"including R1 must print model.py's checksum on a "
                       f"non-adversarial input")
            break
    return bad


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`."""
    for w in range(len(body) // stride):
        if kernel_result(body[w * stride:(w + 1) * stride]) == 0:
            return [f"window {w} returns 0; the driver's Lemire index has an "
                    f"absorbing state there"]
    return []


def write(name, n_iters, stride, body, declared_len=None, check_zero=True,
          check_agree=False):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    if check_agree and stride and len(body) >= stride:
        for p in _agree(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- degenerate: m == 0, nelem > SCR, the two-element minimum ---------------
#
# Every record here is one every rung agrees on, R1 included, which is why the
# file is NOT named `adversarial-*` and the gate holds all eight cells to the
# model's checksum on it:
#
#   (0, ...)    m == 0. The outer `while (i < j)` never runs, so neither scan
#               executes and R1 has nothing to get wrong. This is the ONE
#               degenerate extent that is safe in R1, and it is safe for a
#               structural reason rather than a data one.
#   (100, ...)  nelem > SCR: `m = min(nelem, SCR)` clamps the COPY in every rung
#               including R1, so the 36 undeclared bytes are skipped by the
#               cursor and never read. The clamp is not the safety line.
#   (2, ...)    the SMALLEST record that can carry both sentinels, and therefore
#               the boundary of the benign class from the safe side.
#   (20, ...)   an ordinary record, so the file is not all boundary.
DEGENERATE_RECS = ((0, 128, 0, 0), (100, 128, 30, 4), (2, 128, 1, 0),
                   (20, 90, 7, 2))

# ---- adversarial-single: m == 1, the row that CANNOT be made benign ---------
#
# One element. Nothing malformed, nothing oversized, and both sentinels are
# unavailable by arithmetic: a single byte cannot be both strictly above and
# strictly below the pivot. The element is BELOW the pivot here, so the UPWARD
# scan is the one that leaves; the mirror case is `adversarial-allabove`.
SINGLE_RECS = ((1, 200, 1, 0),)

# ---- adversarial-allbelow / -allabove / -both ------------------------------
#
# `pv = 255`: no `uint8_t` is above it, so no upward sentinel exists ANYWHERE in
# the scratch, stale tail included -- R1 reads `scr[SCR]`.
# `pv = 0`: no `uint8_t` is below it, so R1 reaches `j == 0`, wraps `j - 1` and
# walks away from the frame.
# Both are reachable at a SINGLE HEADER BYTE and are the two extreme pivots.
ALLBELOW_RECS = ((32, 255, 32, 0),)
ALLABOVE_RECS = ((32, 0, 0, 0),)

# ---- adversarial-inarray: the UPWARD scan's in-bounds middle regime ---------
#
# Record 1 fills 48 bytes of scratch and leaves a byte above 200 in
# `scr[16..48)`. Record 2 declares 16 bytes, all at or below its own pivot 200,
# and one below it so the DOWNWARD scan still has its sentinel. R1's upward scan
# for record 2 therefore consumes `scr[0..16)`, walks into the STALE TAIL and
# stops there -- INSIDE the array. Wrong answer, exit 0, no sanitizer report and
# no panic in any Rust rung. That is p23's analogue of p06's regime 1, and the
# gate records the divergence rather than requiring it to vanish.
INARRAY_PV = 200
INARRAY_R1 = (48, 100, 20, 0)     # fills scratch, leaves highs above index 16
INARRAY_R2_M = 16

# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nrec`. The
# guard skips the loop entirely, so every rung prints 0 after ZERO kernel calls.
STRIDE3_BLOB = 30

# `--sweep`: four bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure). Appended LAST so the nine matrix blobs
# stay byte-identical when a band is added.
#
# Band M -- the LIVE EXTENT axis. `nrec` held at 8, rank held at 1/2, `m` swept
#           2..48. Isolates the per-copied/scanned/folded-byte terms. It starts
#           at 2 and not 1 because `m == 1` cannot carry both sentinels.
SWEEP_M_NREC, SWEEP_M_MS = 8, tuple(range(2, 49))
# Band N -- the RECORD-COUNT axis. `m` held at 16, rank at 1/2, `nrec` 1..24.
SWEEP_N_M, SWEEP_N_KS = 16, tuple(range(1, 25))
# Band K -- **THE PIVOT-RANK AXIS**, and p23's own regressor. `m` held at 32 and
#           `nrec` at 8 while `nlow` -- the number of bytes below the pivot --
#           is swept over its whole legal range 1..31. This is the band that
#           answers "does the published law hold at a pivot that is not the
#           median", and the probe says the answer matters: the safe-over-unsafe
#           gap moved 3.3x across this axis at fixed `m`.
SWEEP_K_NREC, SWEEP_K_M = 8, 32
# Band X -- p04's band X: every regressor non-zero at once, so the pooled design
#           has full rank, plus a WITHIN-BAND NEGATIVE CONTROL (`x08b`) whose
#           regressors are identical to `x08a`'s and whose bytes differ, for
#           which the predicted delta is exactly 0.
SWEEP_X_SHAPES = {
    "x04": ((5, 128, 1, 0), (12, 64, 6, 2), (33, 200, 30, 0), (64, 32, 2, 1)),
    "x06": ((2, 128, 1, 0), (7, 90, 3, 1), (18, 17, 9, 0), (40, 240, 30, 5),
            (57, 8, 4, 0), (64, 128, 63, 0)),
    "x08a": ((2, 128, 1, 0), (9, 50, 4, 0), (16, 128, 15, 0), (23, 199, 1, 3),
             (31, 20, 15, 0), (44, 128, 9, 8), (52, 77, 3, 0), (61, 180, 60, 0)),
    "x08b": ((2, 128, 1, 0), (9, 50, 4, 0), (16, 128, 15, 0), (23, 199, 1, 3),
             (31, 20, 15, 0), (44, 128, 9, 8), (52, 77, 3, 0), (61, 180, 60, 0)),
    "x11": ((3, 128, 1, 0), (6, 64, 1, 1), (10, 200, 9, 0), (14, 30, 1, 0),
            (19, 128, 18, 0), (25, 90, 6, 2), (30, 240, 29, 0), (37, 12, 4, 0),
            (43, 128, 42, 0), (50, 160, 11, 5), (64, 100, 33, 0)),
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

    print("p23 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sm = [min(n, SCR) for n, _, _, _ in SMALL_RECS]
    lm = [min(n, SCR) for n, _, _, _ in LARGE_RECS]
    srank = sum(_rank(n, lo) for n, _, lo, _ in SMALL_RECS) / len(SMALL_RECS)
    lrank = sum(_rank(n, lo) for n, _, lo, _ in LARGE_RECS) / len(LARGE_RECS)
    print(f"  residues ok: nrec {len(SMALL_RECS)}/{len(LARGE_RECS)}, copied "
          f"bytes {sum(sm)}/{sum(lm)}, strides "
          f"{stride_of(SMALL_RECS)}/{stride_of(LARGE_RECS)}, mean m "
          f"{sum(sm)/len(sm):.2f}/{sum(lm)/len(lm):.2f}, mean pivot rank "
          f"{srank:.2f}/{lrank:.2f}, m "
          f"{min(sm)}..{max(sm)}/{min(lm)}..{max(lm)}, distinct m "
          f"{len(set(sm))}/{len(set(lm))}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_RECS),
          tiled(rng, SMALL_WINS, SMALL_RECS), check_agree=True)
    write("large.bin", LARGE_ITERS, stride_of(LARGE_RECS),
          tiled(rng, LARGE_WINS, LARGE_RECS), check_agree=True)

    # ---- degenerate: R1 agrees on every record, so it is held to the model --
    write("degenerate.bin", ADV_ITERS, stride_of(DEGENERATE_RECS),
          window(len(DEGENERATE_RECS),
                 [record(rng, n, pv, lo, eq) for n, pv, lo, eq in DEGENERATE_RECS]),
          check_agree=True)

    # ---- adversarial ------------------------------------------------------
    for name, recs in (("adversarial-single", SINGLE_RECS),
                       ("adversarial-allbelow", ALLBELOW_RECS),
                       ("adversarial-allabove", ALLABOVE_RECS)):
        write(f"{name}.bin", ADV_ITERS, stride_of(recs),
              window(len(recs), [record(rng, n, pv, lo, eq)
                                 for n, pv, lo, eq in recs]))

    # both directions in one window: the pv==255 record first, then pv==0.
    both = (ALLBELOW_RECS[0], ALLABOVE_RECS[0])
    write("adversarial-both.bin", ADV_ITERS, stride_of(both),
          window(len(both), [record(rng, n, pv, lo, eq)
                             for n, pv, lo, eq in both]))

    # the in-bounds middle regime: record 2's upward scan stops in record 1's
    # leftovers. Built explicitly rather than by shape, and ASSERTED to be in
    # that regime -- an `inarray` row that quietly overran would be the same
    # mistake p06's task file made about its own boundary.
    n1, pv1, lo1, eq1 = INARRAY_R1
    r1 = record(rng, n1, pv1, lo1, eq1)
    r2data = bytes([INARRAY_PV - 1] + [INARRAY_PV] * (INARRAY_R2_M - 1))
    r2 = record(rng, INARRAY_R2_M, INARRAY_PV, 0, 0, raw=r2data)
    inarray = window(2, [r1, r2])
    got, direction = r1_result(inarray)
    want = kernel_result(inarray)
    if direction or got == want:
        print(f"gen.py: adversarial-inarray is not in the in-bounds middle "
              f"regime (direction={direction!r} r1={got} checked={want}); the "
              f"whole point of the row is a WRONG ANSWER with no memory event",
              file=sys.stderr)
        return 1
    write("adversarial-inarray.bin", ADV_ITERS, len(inarray), inarray)

    # stride 3: a window too small to hold the 4-byte header. The driver guard
    # skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3, rng.randbytes(STRIDE3_BLOB),
          check_zero=False)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for m in SWEEP_M_MS:
            recs = tuple((m, 128, m // 2, 0) for _ in range(SWEEP_M_NREC))
            write(f"sweep-m{m:02d}n{SWEEP_M_NREC:02d}.bin", SWEEP_ITERS,
                  stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for k in SWEEP_N_KS:
            recs = tuple((SWEEP_N_M, 128, SWEEP_N_M // 2, 0) for _ in range(k))
            write(f"sweep-n{k:02d}m{SWEEP_N_M:02d}.bin", SWEEP_ITERS,
                  stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for lo in range(1, SWEEP_K_M):
            recs = tuple((SWEEP_K_M, 128, lo, 0) for _ in range(SWEEP_K_NREC))
            write(f"sweep-k{lo:02d}m{SWEEP_K_M:02d}.bin", SWEEP_ITERS,
                  stride_of(recs), tiled(rng, SWEEP_WINS, recs))
        for tag, recs in SWEEP_X_SHAPES.items():
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(recs),
                  tiled(rng, SWEEP_WINS, recs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
