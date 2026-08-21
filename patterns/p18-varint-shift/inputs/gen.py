#!/usr/bin/env python3
"""Generate p18's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p18-varint-shift/inputs/gen.py            # the matrix inputs
    python3 patterns/p18-varint-shift/inputs/gen.py --sweep     # + the five bands

Payload layout (../spec.md), p06's/p11's/p14's/p16's/p17's/p05's/p07's/p03's/
p12's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nv  u32 LE     declared varint count   ATTACKER DATA
    byte 4..     the varint bytes                       ATTACKER DATA

and the kernel decodes `nv` LEB128 varints out of it, seven payload bits per
byte, continuing while bit 7 is set. The line R1 omits, and the only thing it
omits, is the SHIFT BOUND:

    R1   /* nothing */          val |= (uint64_t)(c & 0x7f) << shift;
    R1h  if (shift < VBITS)     val |= (uint64_t)(c & 0x7f) << shift;

--------------------------------------------------------------------------
THE OVERFLOWING QUANTITY IS A SHIFT COUNT, AND NO LENGTH BOUNDS IT
--------------------------------------------------------------------------
`shift` is `7 * nb`, where `nb` is the number of bytes consumed so far in the
current varint -- and `nb` is decided by the attacker's continue bits, not by
any declared length. The canonical encoding of a `uint64_t` is at most **ten**
bytes and its last shift is exactly **63**, in range. The **eleventh** byte is
the first one that is not, and nothing in the wire format forbids one.

So `small`, `large`, `truncating`, `degenerate` and every sweep blob hold
varints of **at most ten bytes**, which is what makes R1 and R1h agree on them
and the perf rows a measurement of the safety line's PRICE. Each
`adversarial-shift*` blob holds at least one varint of eleven bytes or more.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE AN OBSERVABILITY EXPERIMENT, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
`|=` is idempotent, so a wrapped-round payload OR'd into a bit that is ALREADY
SET changes nothing. The rows are chosen so that this is the experiment:

  `adversarial-shift11`  ONE varint of 11 bytes; the first ten carry payload 0
                         and the eleventh carries 1 at shift 70. Guarded: 0.
                         Unguarded: `1 << (70 mod 64)` = 64. The MINIMAL
                         divergence -- one byte, one bit.
  `adversarial-shift20`  ONE varint of 20 bytes; ten oversized bytes whose
                         masked shifts 6/13/20/27/34/41/48/55/62/5 are all
                         distinct, so ten separate payloads land in the low
                         word. The divergence is large and structured.
  `adversarial-many`     SIX oversized varints in one window: the undefined
                         shift repeats, so a rung that survives one has to
                         survive six.
  `adversarial-sat`      **THE ONE THE CHECKSUM CANNOT SEE.** ONE varint of 20
                         bytes, every payload `0x7f`. The first ten bytes
                         already set all 64 bits, so every wrapped-round OR is
                         a no-op and R1 and R1h return the SAME value. UB
                         executes on ten bytes, UBSan fires, and the checksum
                         column is identical. This row is why a fold is not an
                         oracle for this bug class, and it is stated in
                         ../spec.md as a property of the BUG rather than of the
                         fold.
  `adversarial-stride3`  a 3-byte window: too small for the header, so the
                         driver guard `stride_w >= 4` skips the loop and every
                         rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
TWO FULL-AGREEMENT ROWS THAT ARE NOT NAMED `adversarial-*`
--------------------------------------------------------------------------
`truncating.bin` is **the second bug, the one nothing catches at all.** Its
varints are ten bytes long, so the last shift is 63 and the guard never fires --
but the last byte carries payload `0x7f`, i.e. seven bits of which only the
lowest survives a `u64`. Six bits of the encoded integer are silently discarded
by the shift itself. Every rung agrees, ASan and UBSan are clean,
`debug-assertions=on` is clean, Miri is clean, and R5's proof discharges -- and
the decoded number is not the number that was written. It is p17's limit
arriving on arithmetic instead of on a range, and it is the catalogue's
"truncation" half.

`degenerate.bin` carries the shapes the contract has to decide, all agreeing:

  * a 1-byte varint with payload 0 -- `val == 0`, `nb == 1`;
  * a 10-byte varint whose last shift is exactly 63 -- **the boundary from the
    safe side**, on which R1 and R1h agree exactly and one more byte would not;
  * a varint whose continue bit is set on the LAST byte of the window, so the
    scan exits on `p < len` rather than on the terminator -- the truncated-tail
    case. **This is `cut = 1`.**
  * a declared `nv` LARGER than the window holds, so the outer `p == len` guard
    fires. **This is `brk = 1`.**
  * a padded-zero varint (`80 80 00`), legal LEB128 that decodes to 0.

⚠ **The last two make `degenerate.bin` the ONLY committed input outside the
domain of every per-call `Ir` law p18 publishes**, and until TASK_052 no law
said it had a domain: bands b/v/x/y all have `cut = brk = 0`, and the
two-column law misses `degenerate.bin` by up to +8.00 Ir/call and reverses the
sign of `R3 - R4` on it (TASK_051_REVIEW blocker 1). **Sweep band `t` below is
the band that establishes the domain**, and ../NOTES.md 4a0 is the caveat a
reader should meet before the laws.

--------------------------------------------------------------------------
small AND large: DIFFERENT RESIDUES, AND BOTH ARE LENGTH-HETEROGENEOUS
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues, and
`.memory/03-measurement.md`'s hold-out rule says a fit set must be
length-heterogeneous. p18's varints carry their length in their own continue
bits, so the natural place is here:

  * `small`: 24 varints, byte-lengths 1..10, every length in 1..10 present,
    112 varint bytes, stride 116;
  * `large`: 10 varints, byte-lengths 1..9, 41 varint bytes, stride 45.

`_check_residues()` asserts that `nv`, the varint bytes, the stride and the mean
varint length differ mod 4, 8, 16 and 32 between the two, that every varint of
both is at most ten bytes, and that `small` really is heterogeneous.
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

HDR = 4                                   # nv:u32
VBITS = 64                                # must equal every rung's VBITS
SAFE_MAX_BYTES = 10                       # 7*(10-1) == 63 < VBITS: the last
                                          # in-range varint length

# The two measured shapes: the byte-length of each varint in a window, fixed
# across the windows of a blob so that `work_per_call` is one scalar; only the
# PAYLOAD BYTES differ per window, which is what keeps the driver's
# anti-collapse barrier honest.
SMALL_LENS = (1, 4, 2, 7, 3, 10, 1, 5, 8, 2, 6, 9, 3, 1, 4, 7, 2, 10, 5, 3,
              6, 1, 8, 4)
SMALL_WINS = 112                          # 112 x 116 B = 12.7 KiB, inside L1
LARGE_LENS = (2, 5, 1, 3, 9, 2, 6, 1, 4, 8)
LARGE_WINS = 116000                       # 116000 x 45 B = 5.0 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 60000, 40000
ADV_ITERS = 8                             # R1 executes UB on four of them;
                                          # there is nothing to learn from doing
                                          # it 100 000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


def stride_of(lens):
    """4 header bytes + the varint bytes."""
    return HDR + sum(lens)


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and every varint of both must stay inside the shift bound.
    Returns a list of problems."""
    bad = []
    for label, lens in (("small", SMALL_LENS), ("large", LARGE_LENS)):
        for L in lens:
            if L > SAFE_MAX_BYTES:
                bad.append(f"{label} has a {L}-byte varint; its last shift is "
                           f"{7 * (L - 1)} >= {VBITS}, so R1 would execute an "
                           f"undefined shift and could not agree with the "
                           f"model -- see this file's header")
            if L < 1:
                bad.append(f"{label} has a {L}-byte varint")
    if len(set(SMALL_LENS)) < SAFE_MAX_BYTES:
        bad.append("small is not length-heterogeneous; its whole point is that "
                   "every varint byte-length 1..10 occurs in one window "
                   "(`.memory/03-measurement.md`'s hold-out rule)")
    pairs = [("nv", len(SMALL_LENS), len(LARGE_LENS)),
             ("varint bytes per call", sum(SMALL_LENS), sum(LARGE_LENS)),
             ("stride", stride_of(SMALL_LENS), stride_of(LARGE_LENS))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    smean = sum(SMALL_LENS) / len(SMALL_LENS)
    lmean = sum(LARGE_LENS) / len(LARGE_LENS)
    if abs(smean - lmean) < 0.5:
        bad.append(f"small and large mean varint length ({smean:.2f}, "
                   f"{lmean:.2f}) are within half a byte; the two inputs would "
                   f"measure the same shape of scan")
    return bad


# ---------------------------------------------------------------- content ----

def cut_run(rng, u):
    """`u` bytes that ALL carry the continue bit, i.e. a varint that never
    terminates. Placed last in a window it makes the inner scan exit on
    `p < len` rather than on a terminator, which is the `term < nv` shape band
    T is built to price. `u <= SAFE_MAX_BYTES` keeps its last shift at
    `7*(u-1) <= 63`, so `over == 0` and R1 still agrees with the model."""
    assert 1 <= u <= SAFE_MAX_BYTES
    return bytes(0x80 | rng.randrange(1, 0x80) for _ in range(u))


def varint(rng, nbytes, last_payload=None):
    """A varint of exactly `nbytes` bytes.

    Bytes 0 .. nbytes-2 carry the continue bit; the last does not. Payloads are
    random in 1..0x7f (so no byte is a padded zero unless asked), except the
    last, whose payload is `last_payload` if given.

    **A varint of `nbytes` bytes reaches shift `7*(nbytes-1)`**, so `nbytes <=
    10` is in range and `nbytes >= 11` is the bug."""
    assert nbytes >= 1
    out = bytearray()
    for _ in range(nbytes - 1):
        out.append(0x80 | rng.randrange(1, 0x80))
    if last_payload is None:
        # For a 10-byte varint the last shift is 63, so only bit 0 of the
        # payload survives a u64. Keep the encoding canonical-looking and the
        # arithmetic honest by using 1 there; `truncating.bin` is the blob that
        # deliberately does not.
        last_payload = 1 if nbytes == SAFE_MAX_BYTES else rng.randrange(1, 0x80)
    out.append(last_payload & 0x7f)
    return bytes(out)


def window(nv_decl, chunks):
    """A window: the declared varint count, then the bytes.

    `nv_decl` is written verbatim rather than derived from `chunks` so that a
    row can declare a count the window does not hold."""
    return struct.pack("<I", nv_decl) + b"".join(chunks)


def tiled(rng, nwin, lens):
    """`nwin` windows, identical in *shape* and different in *content*."""
    out = bytearray()
    for _ in range(nwin):
        out += window(len(lens), [varint(rng, L) for L in lens])
    return bytes(out)


def tiled_t(rng, nwin, lens, u, decl):
    """Band T's tile: `lens` terminated varints, then `u` unterminated bytes if
    `u`, with `nv` declared as `decl`.

    The two structural parameters band T exists to vary, neither of which any
    other band moves off zero:

      cut = 1   `u > 0`: the last varint ends on WINDOW EXHAUSTION, so the inner
                `while p < len` test is evaluated one extra time and fails.
      brk = 1   `decl > walked`: the outer loop reaches an iteration whose
                `p == len` guard fires, instead of exiting on `v == nv`.

    `tiled()` produces `cut = 0, brk = 0` always, because it declares
    `len(lens)` and fills the window exactly."""
    walked = len(lens) + (1 if u else 0)
    assert decl >= walked
    out = bytearray()
    for _ in range(nwin):
        chunks = [varint(rng, L) for L in lens]
        if u:
            chunks.append(cut_run(rng, u))
        out += window(decl, chunks)
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
    nv = int.from_bytes(win[:4], "little")
    if nv == 0:
        return 0
    acc, p = 0, HDR
    for _ in range(nv):
        if p == ln:
            break
        val, shift, nb = 0, 0, 0
        while p < ln:
            c = win[p]
            p += 1
            nb += 1
            if shift < VBITS:
                val |= (c & 0x7f) << shift
            shift = (shift + 7) & 0xFFFFFFFF
            if not (c & 0x80):
                break
        acc = (acc * 31 + (val & MASK)) & MASK
        acc = (acc * 31 + nb) & MASK
    return (acc * 31 + nv) & MASK


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12, p06, p14 and p18
    check it, which is strictly stronger and costs one pass over the blob at
    generation time."""
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


# ---- the adversarial varints, written out byte by byte ----------------------
#
# These are not drawn from the RNG: every byte of them is part of the
# experiment and is stated here so that a reader can check the arithmetic
# without running anything.

def over_min():
    """11 bytes: ten continuation bytes with payload 0, then payload 1.

    shift reaches 70 on the last byte.
      guarded   -> 0                    (the contribution is dropped)
      unguarded -> 1 << (70 mod 64) = 64
    The smallest divergence the wire format can express."""
    return bytes([0x80] * 10 + [0x01])


def over_wide():
    """20 bytes: ten payload-0 continuation bytes, then ten bytes whose
    masked shifts 70,77,84,91,98,105,112,119,126,133 mod 64 =
    6,13,20,27,34,41,48,55,62,5 are all DISTINCT, so ten separate payloads
    land in the low word.
      guarded   -> 0
      unguarded -> a large structured constant"""
    return bytes([0x80] * 10
                 + [0x83, 0x85, 0x89, 0x91, 0xa1, 0xc1, 0x83, 0x85, 0x89, 0x11])


def over_sat():
    """20 bytes, every payload 0x7f.

    The first ten bytes (shifts 0..63) already set all 64 bits, so every
    wrapped-round OR is a no-op:
      guarded   -> 0xFFFF_FFFF_FFFF_FFFF
      unguarded -> 0xFFFF_FFFF_FFFF_FFFF   IDENTICAL
    UB executes on ten bytes and the checksum column cannot see it."""
    return bytes([0xff] * 19 + [0x7f])


def trunc10():
    """10 bytes, last payload 0x7f: the last shift is 63, so the guard never
    fires and every rung agrees -- and six bits of the encoded integer are
    discarded by the shift itself. THE SECOND BUG, and nothing catches it."""
    return bytes([0xff] * 9 + [0x7f])


# ---- degenerate ------------------------------------------------------------
# All agreeing, so the file is NOT named `adversarial-*` and the gate holds all
# eight cells to the model's checksum on it.
def degenerate_window():
    chunks = [
        bytes([0x00]),                      # 1 byte, payload 0
        bytes([0x80, 0x80, 0x00]),          # padded zero, legal LEB128
        bytes([0xff] * 9 + [0x01]),         # 10 bytes: last shift EXACTLY 63,
                                            # the boundary from the safe side
        bytes([0xb9, 0x60]),                # an ordinary 2-byte varint
        bytes([0xff, 0xff]),                # continue bit still set on the LAST
                                            # byte of the window: the scan exits
                                            # on `p < len`, not on a terminator
    ]
    # `nv` is declared 9 while the window holds 5 varints, so the outer
    # `p == len` guard fires after the fifth.
    return window(9, chunks)


# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nv`. The
# guard skips the loop entirely, so every rung prints 0 after ZERO kernel calls.
STRIDE3_BLOB = 30

# `--sweep`: five bands (b, v, x, then y and t appended later -- see below), all
# skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure). Appended LAST so the matrix blobs stay
# byte-identical when a band is added.
#
# The pooled design is [bytes, varints, 1]. Band B holds `nv` fixed and moves
# the byte count; band V holds the varint length fixed and moves both together;
# band X turns every regressor on at once with a length-HETEROGENEOUS window.
# Dropping band B or band V takes the design from rank 3 to rank 2, which is
# what makes the leave-one-band-out test able to fail (`.memory/03-measurement.md`).
SWEEP_B_NV = 8
SWEEP_B_LENS = tuple(range(1, SAFE_MAX_BYTES + 1))     # 1..10
SWEEP_V_LEN = 4
SWEEP_V_NVS = tuple(range(1, 17))                      # 1..16
SWEEP_X_SHAPES = {
    "x04": (1, 4, 7, 10),
    "x06": (2, 3, 5, 6, 9, 10),
    "x08a": (1, 2, 3, 5, 6, 8, 9, 10),
    "x08b": (1, 2, 3, 5, 6, 8, 9, 10),   # same regressors as x08a, other bytes:
                                         # the predicted delta is exactly 0
    "x11": (1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
}
# Band Y -- THE EXTRAPOLATION BAND, appended after b/v/x were already fitted.
#
# `.memory/03-measurement.md`: a leave-one-band-out on a design that stays FULL
# RANK after the drop is arithmetically incapable of failing, and p18's pooled
# design is three columns wide -- so ANY three independent rows determine it and
# NO hold-out over b/v/x can fail. That was measured before this band existed
# (../NOTES.md 8) and it is why the band is here: these shapes are outside the
# CONVEX HULL of b/v/x in both regressors, so predicting them is a real
# extrapolation rather than an interpolation dressed up as a hold-out.
#
#   b/v/x cover  bytes 4..80,  nv 1..16
#   band Y is    bytes 160..320, nv 16..64
#
# The predictions were written down and SHA-256'd BEFORE these blobs were
# measured (controls/predict.py, ../NOTES.md 8).
SWEEP_Y_SHAPES = {
    "y16": tuple(10 for _ in range(16)),                    # bytes 160, nv 16
    "y40": tuple((1 + (i % 10)) for i in range(40)),        # bytes 220, nv 40
    "y64": tuple(5 for _ in range(64)),                     # bytes 320, nv 64
}
# Band T -- THE DOMAIN BAND, appended after b/v/x/y at TASK_052.
#
# TASK_051_REVIEW's blocker: **every blob of bands b/v/x/y has `term == nv`**,
# because `tiled()` declares exactly as many varints as it writes and fills the
# window exactly. So the published laws were fitted inside one regime of a
# structural parameter nobody had named, and `degenerate.bin` -- a COMMITTED
# MATRIX INPUT -- sits outside it and misses by +2.00 (six cells), +5.00 (the
# two clang cells) and +8.00 (`safe_tuned`) against a quoted max residual of
# 0.029, taking `R3 - R4` the wrong way round. Same CLASS of defect as p14's
# law-fitted-inside-one-regime (`.memory/02-bench-rules.md`, `.memory/01-ladder.md`
# finding 16), on a different axis.
#
# The two parameters, varied INDEPENDENTLY so the miss decomposes:
#
#   cut  the last varint ends on window exhaustion (`term = nv - 1`)
#   brk  the outer loop exits on `p == len` rather than on `v == nv`
#
# `degenerate.bin` has BOTH, which is why it needed two rows to explain. t01-t04
# are cut+brk; t05/t06 are cut only; t07/t08 are brk only; t08 is t07's
# WITHIN-BAND NEGATIVE CONTROL -- identical regressors, 40 extra declared
# varints that are never walked, predicted delta exactly 0.
#
# Every `u` is <= SAFE_MAX_BYTES so `over == 0` on every row, exactly as on
# b/v/x/y (`.memory/02-bench-rules.md`: never compare cost on an input where R1
# commits UB).
SWEEP_T_SHAPES = {
    #        lens                       u   decl-above-walked
    "t01": ((2, 2, 2),                  1,  1),
    "t02": ((1,) * 5,                   3,  1),
    "t03": ((4,) * 8,                   5,  1),
    "t04": ((6,) * 12,                 10,  1),
    "t05": ((2, 2, 2),                  1,  0),
    "t06": ((4,) * 8,                   5,  0),
    "t07": ((3,) * 6,                   0,  1),
    "t08": ((3,) * 6,                   0, 40),
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

    print("p18 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: nv {len(SMALL_LENS)}/{len(LARGE_LENS)}, varint "
          f"bytes {sum(SMALL_LENS)}/{sum(LARGE_LENS)}, strides "
          f"{stride_of(SMALL_LENS)}/{stride_of(LARGE_LENS)}, mean varint len "
          f"{sum(SMALL_LENS)/len(SMALL_LENS):.2f}/"
          f"{sum(LARGE_LENS)/len(LARGE_LENS):.2f}, lens "
          f"{min(SMALL_LENS)}..{max(SMALL_LENS)}/"
          f"{min(LARGE_LENS)}..{max(LARGE_LENS)}, distinct lens "
          f"{len(set(SMALL_LENS))}/{len(set(LARGE_LENS))}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_LENS),
          tiled(rng, SMALL_WINS, SMALL_LENS))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_LENS),
          tiled(rng, LARGE_WINS, LARGE_LENS))

    # ---- adversarial ------------------------------------------------------
    write("adversarial-shift11.bin", ADV_ITERS, HDR + 11, window(1, [over_min()]))
    write("adversarial-shift20.bin", ADV_ITERS, HDR + 20, window(1, [over_wide()]))
    six = [over_min() for _ in range(6)]
    write("adversarial-many.bin", ADV_ITERS, HDR + 6 * 11, window(6, six))
    write("adversarial-sat.bin", ADV_ITERS, HDR + 20, window(1, [over_sat()]))
    # stride 3: a window too small to hold the 4-byte header. The driver guard
    # skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3, rng.randbytes(STRIDE3_BLOB),
          check_zero=False)

    # ---- full-agreement rows ---------------------------------------------
    trunc = [trunc10(), trunc10(), trunc10()]
    write("truncating.bin", ADV_ITERS, HDR + 30, window(3, trunc))
    dg = degenerate_window()
    write("degenerate.bin", ADV_ITERS, len(dg), dg)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for L in SWEEP_B_LENS:
            lens = tuple(L for _ in range(SWEEP_B_NV))
            write(f"sweep-b{L:02d}v{SWEEP_B_NV:02d}.bin", SWEEP_ITERS,
                  stride_of(lens), tiled(rng, SWEEP_WINS, lens))
        for V in SWEEP_V_NVS:
            lens = tuple(SWEEP_V_LEN for _ in range(V))
            write(f"sweep-v{V:02d}b{SWEEP_V_LEN:02d}.bin", SWEEP_ITERS,
                  stride_of(lens), tiled(rng, SWEEP_WINS, lens))
        for tag, lens in SWEEP_X_SHAPES.items():
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(lens),
                  tiled(rng, SWEEP_WINS, lens))
        for tag, lens in SWEEP_Y_SHAPES.items():
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(lens),
                  tiled(rng, SWEEP_WINS, lens))
        for tag, (lens, u, extra) in SWEEP_T_SHAPES.items():
            decl = len(lens) + (1 if u else 0) + extra
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(lens) + u,
                  tiled_t(rng, SWEEP_WINS, lens, u, decl))
    return 0


if __name__ == "__main__":
    sys.exit(main())
