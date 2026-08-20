#!/usr/bin/env python3
"""Generate p12's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p12-strcat-fixed/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p12-strcat-fixed/inputs/gen.py --sweep     # + the two sweep bands

Payload layout (../spec.md), p11's/p16's/p17's/p05's/p07's/p03's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nstr  u32 LE      declared string count   ATTACKER DATA
    byte 4..      packed, NUL-terminated strings

and the kernel concatenates each string into a fixed `dst[DST_CAP]`, folds the
lengths, then folds the destination. The line R1 omits, and the only thing it
omits, is the CAPACITY CHECK on the write:

    R1   /* nothing */                        for (i = p; i < q; i++) dst[dlen++] = ...
    R1h  if (dlen + slen <= DST_CAP) {        for (i = p; i < q; i++) dst[dlen++] = ...

--------------------------------------------------------------------------
WHY small AND large ARE 100% ACCEPT, AND WHY THAT IS NOT A CHOICE
--------------------------------------------------------------------------
`harness/check.py:1249-1278` requires **every cell, R1 included, to print
`model.py`'s checksum on every non-adversarial input**. R1 omits the capacity
check, so on any window where the check would fire R1 copies bytes the checked
rungs skip *and* ends with a larger `dlen` -- and both are folded. R1's checksum
therefore differs *necessarily*, for every `DST_CAP` and for a truncating policy
as much as for a skipping one.

So a p12 row on which the bug fires cannot also be a checksum-agreeing row.
This is structural for a WRITE bug and it has no analogue in the READ patterns:
p11 has `adversarial-zerotail`, a header lie on which every rung including R1
agrees. p12 cannot have one. The consequence is stated rather than hidden:
`small` and `large` exercise the check on the ACCEPT path only, so they cannot
separate "per string" from "per accepted string" -- `sweep-a*` is what does
that, and R1 is absent from it for the same reason.

--------------------------------------------------------------------------
THE MEAN STRING LENGTH IS THE AXIS, AND small/large SIT ON OPPOSITE SIDES OF 16
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues.
Because every window must fit inside `DST_CAP = 128` bytes of destination, the
count and the mean length trade off against each other exactly, so the two
inputs are built at opposite ends of that trade:

  * `small`: 6 long strings, mean 20.5, 123 of 128 bytes of `dst` used;
  * `large`: 31 short strings, mean 4.0, 124 of 128 used.

`_check_residues()` asserts that `nstr`, the copied bytes and the stride differ
mod 4, 8, 16 and 32 between the two, and that the mean lengths straddle 16. The
constants were picked by `.temp/p12/pick_sizes.py` against exactly that
predicate.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A LADDER IN OVERFLOW MAGNITUDE, BECAUSE THE FAILURE
MODE IS A FUNCTION OF IT
--------------------------------------------------------------------------
Measured on this box at the gate's own flags (`.temp/p12/probe_sp3.c`; gcc
defaults to `-fstack-protector-strong`, the upstream clang tarball to no stack
protector, and `harness/build.py` passes neither way):

    overflow  +1 .. +8      SILENT in gcc AND clang -- wrong answer, exit 0
    overflow +16 .. +48     gcc `*** stack smashing detected ***` (134);
                            clang SILENT, and it corrupts the CALLER's locals
    overflow +64 and up     gcc 134; clang SIGSEGV (139)

so the adversarial rows are designed one per regime rather than all at one
magnitude:

  * `adversarial-exact`    total exactly DST_CAP. Nothing overflows, every rung
                           agrees, the sanitizer is clean. The boundary from
                           the safe side.
  * `adversarial-off1`     the SAME four strings plus one 1-byte string, so the
                           total is DST_CAP + 1. R1 writes exactly ONE byte
                           past `dst` and exits 0 with a wrong answer under both
                           compilers; only ASan sees it. The off-by-one.
  * `adversarial-nonul`    the last string has no terminator, so its measured
                           length is `len - p` -- p11's bug arriving as a
                           SECOND route to the overflow, through the copy
                           instead of through the scan. Sized to land in the
                           silent regime (+6).
  * `adversarial-overflow` four 64-byte strings against a 128-byte destination:
                           +128, i.e. the regime where the frame is destroyed.
                           gcc aborts on the canary, clang segfaults.

`exact` and `off1` share one draw of their first four strings, so the pair
differs in the presence of one 1-byte string and in nothing else (p11's
TASK_034 lesson: a controlled pair must actually be controlled).
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

HDR = 4                                   # nstr:u32
DST_CAP = 128                             # must equal every rung's DST_CAP

# 0x00 -> 0x5a. Applied to every string body, so the ONLY zero byte in a window
# is a terminator this file wrote deliberately.
NONZERO = bytes([0x5a] + list(range(1, 256)))

# The two measured shapes, picked by `.temp/p12/pick_sizes.py`.
# `(base, spread, step)` generates the per-window length multiset
# deterministically; see `length_list`.
SMALL_NSTR, SMALL_LEN = 6, (2, 36, 17)       # lens 2..36, total 123, mean 20.50
SMALL_WINS = 100                             # 100 x 133 B = 13.0 KiB, inside L1
LARGE_NSTR, LARGE_LEN = 31, (1, 7, 3)        # lens 1..7,  total 124, mean 4.00
LARGE_WINS = 50000                           # 50000 x 159 B = 7.58 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 120000, 40000
ADV_ITERS = 8                             # R1 executes UB on three of them;
                                          # there is nothing to learn from doing
                                          # it 100 000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


def length_list(k, spec):
    """`k` string lengths, deterministic, spanning `[base, base+spread)`.

    `base + (i*step) % spread` with `gcd(step, spread) == 1` walks the whole
    residue class before repeating, so the multiset is fixed and its mean is
    exact. It is the *multiset* that is fixed, not the order: `tiled()` shuffles
    it per window with the seeded RNG, so every window does the same amount of
    work while its bytes -- and therefore its checksum -- differ, which is what
    keeps the driver's anti-collapse barrier honest.

    Note the shuffle is safe here in a way it would not be for a rejecting
    window: with `sum(lens) <= DST_CAP` every string is accepted whatever the
    order, so `dlen` is order-independent and `work_per_call` is one scalar."""
    base, spread, step = spec
    return [base + (i * step) % spread for i in range(k)]


def stride_of(k, spec):
    """4 header bytes + one terminator per string + the string bytes."""
    return HDR + k + sum(length_list(k, spec))


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and both must be 100% accept. Returns a list of problems."""
    bad = []
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    for label, lens in (("small", sl), ("large", ll)):
        if sum(lens) > DST_CAP:
            bad.append(f"{label} copies {sum(lens)} bytes into a {DST_CAP}-byte "
                       f"destination, so the capacity check FIRES on it and R1 "
                       f"cannot agree with the model -- see this file's header")
    smean, lmean = sum(sl) / len(sl), sum(ll) / len(ll)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean string length ({smean:.2f}, "
                   f"{lmean:.2f}) are on the same side of 16; the two inputs "
                   f"would measure the same shape of scan and copy")
    pairs = [("nstr", SMALL_NSTR, LARGE_NSTR),
             ("copied bytes per call", sum(sl), sum(ll)),
             ("stride", stride_of(SMALL_NSTR, SMALL_LEN),
              stride_of(LARGE_NSTR, LARGE_LEN))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


# ---------------------------------------------------------------- content ----

def strings(rng, lens):
    """One window's string area: each length, non-zero bytes, one terminator."""
    out = bytearray()
    for n in lens:
        out += rng.randbytes(n).translate(NONZERO)
        out += b"\x00"
    return bytes(out)


def window(nstr_decl, body):
    """A window: the declared count, then the string area.

    `nstr_decl` is written verbatim rather than derived from `body` so that a
    row can declare a count the window does not hold."""
    return nstr_decl.to_bytes(4, "little") + body


def kernel_result(win):
    """The checked kernel, on one window, in twenty lines.

    Used only by `_no_zero_window()` below. It is deliberately NOT imported
    from `../model.py`: `gen.py` must be runnable on its own, and a generator
    that shares the oracle's code cannot check the oracle."""
    ln = len(win)
    if ln < HDR:
        return 0
    nstr = int.from_bytes(win[:4], "little")
    if nstr == 0:
        return 0
    mask = (1 << 64) - 1
    dst, dlen, acc, p, s = bytearray(DST_CAP), 0, 0, HDR, 0
    while s < nstr:
        q = p
        while q < ln and win[q] != 0:
            q += 1
        slen = q - p
        if dlen + slen <= DST_CAP:
            dst[dlen:dlen + slen] = win[p:q]
            dlen += slen
        acc = (acc * 31 + slen) & mask
        if q >= ln:
            break
        p = q + 1
        if p >= ln:
            break
        s += 1
    for i in range(dlen):
        acc = (acc * 31 + dst[i]) & mask
    return ((acc * 31 + dlen) * 31 + nstr) & mask


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12 checks it, which is
    strictly stronger and costs one pass over the blob at generation time."""
    for w in range(len(body) // stride):
        if kernel_result(body[w * stride:(w + 1) * stride]) == 0:
            return [f"window {w} returns 0; the driver's Lemire index has an "
                    f"absorbing state there"]
    return []


def tiled(rng, nwin, k, spec):
    """`nwin` windows, identical in *shape* and different in *content*."""
    lens = length_list(k, spec)
    out = bytearray()
    for _ in range(nwin):
        shuffled = list(lens)
        rng.shuffle(shuffled)
        out += window(k, strings(rng, shuffled))
    return bytes(out)


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


# ---- adversarial-exact / adversarial-off1: the off-by-one, controlled -------
#
# Four 32-byte strings total exactly DST_CAP, so every rung accepts all four and
# `exact` is a row on which R1 and the checked rungs agree BY A SINGLE BYTE of
# margin. `off1` is the same four strings plus one string of length 1: the
# checked rungs reject it (128 + 1 > 128) and R1 writes `dst[128]`, one byte
# past the array. Measured: silent under gcc AND clang, exit 0, wrong answer;
# only ASan sees it.
EXACT_LENS = [32, 32, 32, 32]
OFF1_EXTRA = 1

# ---- adversarial-nonul: p11's bug arriving through the COPY -----------------
#
# nstr = 3, two terminated 40-byte strings, then 54 bytes with no terminator.
# The scan is bounded by the window in every rung, so the third string's
# measured length is `len - p` = 54; the checked rungs reject it (80 + 54 > 128)
# and R1 copies it, ending 6 bytes past `dst`. So the same malformed input that
# makes p11's R1 read off the end makes p12's R1 write off the end, through a
# different mechanism: nothing about the SCAN is wrong here.
NONUL_LENS = [40, 40]
NONUL_TAIL = 54

# ---- adversarial-overflow: the frame is destroyed --------------------------
#
# Four 64-byte strings against a 128-byte destination. The checked rungs accept
# two and reject two; R1 writes 256 bytes, i.e. 128 past the array, which is the
# regime where gcc's canary fires and clang's return address is gone.
OVERFLOW_LENS = [64, 64, 64, 64]

# ---- adversarial-empty: every string is empty ------------------------------
#
# nstr = 8 and the window is the 4-byte header plus 8 NULs. Every string has
# length 0 and every one of them is ACCEPTED (0 + 0 <= 128), so `dlen` is 0 and
# the destination fold never runs: the row where the per-string constant is
# measured with both byte terms set to zero. Returns exactly `nstr == 8`.
EMPTY_NSTR = 8

# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nstr`. The
# guard skips the loop entirely, so every rung prints 0 after ZERO kernel calls.
STRIDE3_BLOB = 30

# `--sweep`: two bands, both skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# **Band N -- the string-count axis, every string ACCEPTED.** All strings are 4
# bytes, so `4*K <= 128` for every K in the band and R1 can be measured on it:
# this is the band that carries the R1-vs-R1h law. Its regressors are
# `(1, K, 5K, 4K)`, i.e. it is RANK 2 on its own -- scanned bytes and copied
# bytes are both proportional to K when nothing is rejected, which is the same
# rank deficiency `small`/`large` have and the reason band A exists.
SWEEP_N_LEN = 4
SWEEP_N_KS = tuple(range(1, 25))
SWEEP_N_WINS = 8

# **Band A -- the ACCEPTANCE-RATIO axis, count held at 24.** All strings are L
# bytes, L = 1..24, so the number accepted is `min(24, floor(128/L))`: 24 for
# L <= 5 and as few as 5 at L = 24. Scanned bytes `24*(L+1)` rise linearly while
# copied bytes `L*min(24, floor(128/L))` saturate at ~128, which is what
# separates the per-SCANNED-byte term from the per-COPIED-byte term.
# **R1 is not measurable on this band** for L >= 6: it would copy `24*L` bytes
# into a 128-byte destination. That exclusion is the price of the bug being a
# write, and it is stated in ../NOTES.md rather than worked around.
SWEEP_A_NSTR = 24
SWEEP_A_LENS = tuple(range(1, 25))
SWEEP_A_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p12 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    print(f"  residues ok: nstr {SMALL_NSTR}/{LARGE_NSTR}, copied bytes "
          f"{sum(sl)}/{sum(ll)} of {DST_CAP}, strides "
          f"{stride_of(SMALL_NSTR, SMALL_LEN)}/{stride_of(LARGE_NSTR, LARGE_LEN)}, "
          f"mean string length {sum(sl)/len(sl):.2f}/{sum(ll)/len(ll):.2f}, "
          f"lengths {min(sl)}..{max(sl)}/{min(ll)}..{max(ll)}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NSTR, SMALL_LEN),
          tiled(rng, SMALL_WINS, SMALL_NSTR, SMALL_LEN))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NSTR, LARGE_LEN),
          tiled(rng, LARGE_WINS, LARGE_NSTR, LARGE_LEN))

    # ---- adversarial ------------------------------------------------------
    # (1) and (2) are a CONTROLLED PAIR and share one draw of the four strings,
    #     so the blobs differ in the two extra bytes of the fifth string and in
    #     nothing else (p11's TASK_034 lesson).
    shared = strings(rng, EXACT_LENS)

    # (1) exactly DST_CAP: every rung accepts everything and agrees.
    write("adversarial-exact.bin", ADV_ITERS, HDR + len(shared),
          window(len(EXACT_LENS), shared))

    # (2) DST_CAP + 1: the checked rungs reject one 1-byte string, R1 writes
    #     `dst[128]`. Silent under both compilers; ASan is the only witness.
    body = shared + strings(rng, [OFF1_EXTRA])
    write("adversarial-off1.bin", ADV_ITERS, HDR + len(body),
          window(len(EXACT_LENS) + 1, body))

    # (3) the last string has no terminator: p11's malformed record reaching
    #     p12's bug through the copy rather than through the scan.
    body = strings(rng, NONUL_LENS) + rng.randbytes(NONUL_TAIL).translate(NONZERO)
    write("adversarial-nonul.bin", ADV_ITERS, HDR + len(body),
          window(len(NONUL_LENS) + 1, body))

    # (4) 256 bytes into 128: the regime where the frame is destroyed.
    body = strings(rng, OVERFLOW_LENS)
    write("adversarial-overflow.bin", ADV_ITERS, HDR + len(body),
          window(len(OVERFLOW_LENS), body))

    # (5) the degenerate copy: every string is empty, so `dlen` stays 0.
    write("adversarial-empty.bin", ADV_ITERS, HDR + EMPTY_NSTR,
          window(EMPTY_NSTR, bytes(EMPTY_NSTR)))

    # (6) stride 3: a window too small to hold the 4-byte header. The driver
    #     guard skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3,
          rng.randbytes(STRIDE3_BLOB).translate(NONZERO), check_zero=False)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for k in SWEEP_N_KS:
            write(f"sweep-n{k:02d}L{SWEEP_N_LEN:02d}.bin", SWEEP_ITERS,
                  stride_of(k, (SWEEP_N_LEN, 1, 1)),
                  tiled(rng, SWEEP_N_WINS, k, (SWEEP_N_LEN, 1, 1)))
        for n in SWEEP_A_LENS:
            write(f"sweep-a{SWEEP_A_NSTR:02d}L{n:02d}.bin", SWEEP_ITERS,
                  stride_of(SWEEP_A_NSTR, (n, 1, 1)),
                  tiled(rng, SWEEP_A_WINS, SWEEP_A_NSTR, (n, 1, 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
