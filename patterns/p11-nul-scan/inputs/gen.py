#!/usr/bin/env python3
"""Generate p11's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and since TASK_021 `harness/check.py` hashes it into `source_sha256`, so every
law measured on these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p11-nul-scan/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p11-nul-scan/inputs/gen.py --sweep    # + the two sweep bands

Payload layout (../spec.md), p16's/p17's/p05's/p07's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nstr  u32 LE      declared string count   ATTACKER DATA
    byte 4..      packed, NUL-terminated strings
    data_start = 4 ; avail = len - 4 bytes actually present

and the kernel measures each string with a scan, folds its bytes, and steps the
cursor past the terminator. The bound that R1 omits, and the only thing it
omits, is the bound on the SCAN:

    R1   q = p + strlen(buf + off + p);                 /* the sentinel */
    R1h  z = memchr(buf + off + p, 0, len - p); ...     /* the window   */

--------------------------------------------------------------------------
THE COUNT IS NOT A BOUND, AND adversarial-zerotail IS THE PROOF
--------------------------------------------------------------------------
`nstr` is attacker data and it bounds *nothing*: what stops the walk is the
terminator (inner loop) and `p >= len` (outer loop). Three adversarial inputs
separate the two quantities, and the third is the one that says which matters:

  * `adversarial-nonul`   -- nstr HONEST, the last declared string has no
                             terminator. R1 overruns.
  * `adversarial-count`   -- nstr = 4096, a lie, and the tail is NON-ZERO
                             filler. R1 overruns -- but on a string that was
                             never written, reached only because the count lied.
  * `adversarial-zerotail`-- nstr = 4096, the SAME lie, and the tail is NUL.
                             **Every rung including R1 stays in bounds and every
                             rung agrees.** The count is off by 4073 strings and
                             nothing happens.

So the three rows are not three spellings of one thing. `count` and `zerotail`
have the identical header lie and differ only in the tail bytes, which is what
makes "the sentinel, not the count, is the bound" a measurement rather than a
remark. ../NOTES.md 7.

--------------------------------------------------------------------------
THE MEAN STRING LENGTH IS THE AXIS, AND small/large SIT ON OPPOSITE SIDES OF 16
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues and
records p01's modulus 4, p02's 16, p16's 4, p17's 4, p05's 8-and-16 and p07's
octave. p11's moduli are the *scan implementations'* strides, and they are not
the fold's:

  * the fold is a byte-at-a-time Horner chain LLVM unrolls **4x**;
  * `core::slice::memchr` -- what R3's `CStr::from_bytes_until_nul` lowers to --
    reads **16** bytes per iteration and takes a scalar byte loop below 16;
  * glibc's AVX2 `strlen` -- what R1/R1h reach -- reads **32** bytes per
    `vpcmpeqb` and 128 per unrolled iteration.

So the axis is the **string length**, and `small`'s mean of 6.92 is below
`memchr`'s 16-byte threshold while `large`'s 100.0 is above it: R3's scan is a
scalar loop on one input and word-at-a-time on the other, from the same source.
`_check_residues()` additionally asserts that `nstr`, the total folded bytes and
the stride differ mod 4, 8, 16 and 32 between the two; the constants were picked
by `.temp/p11/pick_sizes.py` against exactly that predicate.

The **sweep** is what establishes the law rather than this file asserting it.
Band A holds the string count and walks the length 1..64 -- four full cycles of
16, sixteen of 4, two of 32 -- and band B holds the length at 24 and walks the
count, which is what separates the per-CALL term from the per-STRING term
(`.memory/01-ladder.md`: separating those is where p16's `nrec + 3` and p05's
"+11.00 flat" both died).

--------------------------------------------------------------------------
SIZES
--------------------------------------------------------------------------
  * `small`: 12 windows x 1192 B = 14.0 KiB, inside this box's 32 KiB L1.
    150 strings per window, mean length 6.92.
  * `large`: 2000 windows x 4145 B = 7.9 MiB, ~8x this box's 1 MiB/core L2, so
    the window the driver jumps to is cold. 41 strings per window, mean
    length 100.0.
  * every adversarial input is exactly one window (`n_blob == stride`), for
    p16's, p17's and p07's reason: `k = (acc * nwin) >> 64` is pseudo-random
    over `[0, nwin)`, so with several windows the malformed one is hit only
    probabilistically, and an overrun from a *middle* window stays inside the
    allocation -- a silent wrong answer, no ASan, and a gate that passes by
    luck. With `nwin == 1`, `k` is always 0 and `off` is always 0.
  * **window 0 must serve something** (p17, `.memory/01-ladder.md`): a window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`. Every
    window here returns `... * 31 + nstr` with `nstr != 0`, so no window can
    return 0 by construction; `adversarial-empty` returns exactly `nstr == 8`.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run, so the cost of a row is the payload `to_vec` (a bulk copy --
`head1_u64_bytes`) plus `4 x stride` bytes scanned *and* folded. That is 9536
byte-visits on `small` and 33 160 on `large`, against `.memory`'s measured
budget of ~3.05 M folded bytes in 180 s, so both rows are ~100x inside it. The
only cost is the 8 MB `to_vec`; p07's 12 MB one passes.
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

# 0x00 -> 0x5a. Applied to every string body, so the ONLY zero byte in a window
# is a terminator this file wrote deliberately. Done with `bytes.translate`
# rather than a Python loop because `large` is 8 MB of body.
NONZERO = bytes([0x5a] + list(range(1, 256)))

# The two measured shapes, picked by `.temp/p11/pick_sizes.py` against
# `_check_residues()` below. `(base, spread, step)` generates the per-window
# length multiset deterministically; see `length_list`.
SMALL_NSTR, SMALL_LEN = 150, (1, 13, 7)      # mean 6.92, below memchr's 16
SMALL_WINS = 12
LARGE_NSTR, LARGE_LEN = 41, (40, 121, 3)     # mean 100.0, above it
LARGE_WINS = 2000

SMALL_ITERS, LARGE_ITERS = 6000, 1500
ADV_ITERS = 8                             # R1 executes UB on two of them; there
                                          # is nothing to learn from doing it
                                          # 6000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


def length_list(k, spec):
    """`k` string lengths, deterministic, spanning `[base, base+spread)`.

    `base + (i*step) % spread` with `gcd(step, spread) == 1` walks the whole
    residue class before repeating, so the multiset is fixed and its mean is
    exact. It is the *multiset* that is fixed, not the order: `window()` shuffles
    it per window with the seeded RNG, so every window does the same amount of
    work (one scalar `work_per_call`) while its bytes -- and therefore its
    checksum -- differ, which is what keeps the driver's anti-collapse barrier
    honest."""
    base, spread, step = spec
    return [base + (i * step) % spread for i in range(k)]


def stride_of(k, spec):
    """4 header bytes + one terminator per string + the string bytes."""
    return HDR + k + sum(length_list(k, spec))


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact. Returns a list of problems (empty when healthy)."""
    bad = []
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    smean, lmean = sum(sl) / len(sl), sum(ll) / len(ll)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean string length ({smean:.2f}, "
                   f"{lmean:.2f}) are on the same side of 16; that threshold is "
                   f"where core::slice::memchr switches between its scalar and "
                   f"its word-at-a-time path, so both inputs would measure the "
                   f"same half of R3")
    pairs = [("nstr", SMALL_NSTR, LARGE_NSTR),
             ("folded bytes per call", sum(sl), sum(ll)),
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

    `nstr_decl` is written verbatim rather than derived from `body`, so that
    `adversarial-count` and `adversarial-zerotail` can declare 4096 strings a
    40-byte window cannot hold -- which is half the pattern."""
    return nstr_decl.to_bytes(4, "little") + body


def tiled(rng, nwin, k, spec):
    """`nwin` windows, identical in *shape* and different in *content*."""
    lens = length_list(k, spec)
    out = bytearray()
    for _ in range(nwin):
        shuffled = list(lens)
        rng.shuffle(shuffled)
        out += window(k, strings(rng, shuffled))
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<9d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-nonul: the declared string has no terminator ---------------
#
# nstr = 6 and six strings are written -- the count is HONEST. The sixth has no
# terminator and runs to the last byte of the window, which is also the last byte
# of the blob (one window). R1's `strlen` therefore reads buf[n_blob] and beyond;
# the checked rungs stop at `q == len` and treat the window end as the end of the
# string. This is THE input for this pattern: nothing is computed wrongly, the
# loop simply does not stop.
NONUL_LENS = [7, 11, 5, 13, 9]
NONUL_TAIL = 12

# ---- adversarial-count: the count lies AND the tail is unterminated ---------
#
# nstr = 4096 against 3 strings actually written, then 20 non-zero bytes with no
# terminator. The checked rungs walk 4 strings (three real, one running to the
# window end) and stop on `p >= len`; R1 walks into the filler and off the end.
# Note that the overrun is caused by the count lie *plus* the unterminated tail:
# `adversarial-zerotail` is the same lie with a terminated tail and is harmless.
COUNT_LENS = [4, 6, 3]
COUNT_NSTR = 4096
COUNT_TAIL = 20

# ---- adversarial-zerotail: the same lie, a NUL tail -------------------------
#
# Identical header (nstr = 4096) and identical first three strings -- the same
# bytes, not merely the same lengths, because `main()` draws them ONCE and
# reuses them (TASK_034; before that the two blobs differed in 33 bytes and
# this comment was wrong). The 20-byte
# tail is NUL rather than filler. Every rung including R1 stays inside the
# window: each tail byte is an empty string, the cursor advances one byte at a
# time, and the walk ends on `p >= len` after 23 strings -- 4073 short of the
# declared count, with no error anywhere. The control that shows `nstr` bounds
# nothing.
ZEROTAIL_LENS = COUNT_LENS
ZEROTAIL_NSTR = COUNT_NSTR
ZEROTAIL_TAIL = COUNT_TAIL

# ---- adversarial-empty: every string is empty -------------------------------
#
# nstr = 8 and the window is the 4-byte header plus 8 NULs. Every rung folds
# eight zero-length strings (`h = 0`, `slen = 0`, so `h ^ slen == 0`) and returns
# `0*31 + 8 == 8`. The degenerate scan: the inner loop never iterates, so this is
# the row where the per-string constant is measured with the per-byte term set to
# zero. It is also non-zero on purpose -- see "window 0 must serve something".
EMPTY_NSTR = 8

# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nstr`. The
# guard skips the loop entirely rather than entering it and breaking out, which
# would put a branch in the measured loop, so every rung prints 0 after ZERO
# kernel calls. Distinct from every row above, where the calls happen.
STRIDE3_BLOB = 30

# `--sweep`: two bands, both skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# **Band A -- the string-length axis, 64 consecutive lengths.** All strings in a
# band-A window have the SAME length, so the scan's trip count is a constant of
# the file and a per-byte rate can be read off a lag pair rather than fitted.
# 1..64 is four full cycles of `core::slice::memchr`'s 16-byte stride, sixteen of
# the fold's 4x unroll and two of `strlen`'s 32-byte `vpcmpeqb`.
SWEEP_A_LENS = tuple(range(1, 65))
SWEEP_A_NSTR = 24
SWEEP_A_WINS = 8

# **Band B -- the string-count axis, length held at 24.** Band A moves the length
# and holds the count, so every per-call constant it yields is confounded with
# the count. Band B moves the count over 16 values at fixed length, which is what
# separates the per-CALL term from the per-STRING term. `k = 24` is deliberately
# absent: band A's `len24` window already has 24 strings of length 24, so
# emitting it here would write the same file name twice with different content --
# p07's band-A/band-B collision, avoided the same way.
SWEEP_B_LEN = 24
SWEEP_B_NSTRS = tuple(k for k in range(4, 38, 2) if k != SWEEP_A_NSTR)
SWEEP_B_WINS = 8
SWEEP_ITERS = 2000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p11 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    print(f"  residues ok: nstr {SMALL_NSTR}/{LARGE_NSTR}, folded bytes "
          f"{sum(sl)}/{sum(ll)}, strides "
          f"{stride_of(SMALL_NSTR, SMALL_LEN)}/{stride_of(LARGE_NSTR, LARGE_LEN)}, "
          f"mean string length {sum(sl)/len(sl):.2f}/{sum(ll)/len(ll):.2f} "
          f"(memchr's threshold is 16), lengths "
          f"{min(sl)}..{max(sl)}/{min(ll)}..{max(ll)}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NSTR, SMALL_LEN),
          tiled(rng, SMALL_WINS, SMALL_NSTR, SMALL_LEN))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NSTR, LARGE_LEN),
          tiled(rng, LARGE_WINS, LARGE_NSTR, LARGE_LEN))

    # ---- adversarial ------------------------------------------------------
    # (1) THE pattern: a declared string with no terminator.
    body = strings(rng, NONUL_LENS) + rng.randbytes(NONUL_TAIL).translate(NONZERO)
    write("adversarial-nonul.bin", ADV_ITERS, HDR + len(body),
          window(len(NONUL_LENS) + 1, body))

    # (2) and (3) are a CONTROLLED PAIR and share one draw of the strings.
    #
    # Until TASK_034 each called `strings(rng, ...)` on the same sequentially
    # advancing RNG, so the two blobs got three strings of the same LENGTHS and
    # different BYTES: `cmp` reported 33 differing bytes where this file and
    # ../NOTES.md 7 both said "20 tail bytes and nothing else"
    # (TASK_033_REVIEW major 2). The conclusion survived -- string content
    # cannot change whether `strlen` runs off the end -- but the sentence that
    # upgrades the row from a remark to a controlled comparison was false about
    # the shipped tree. One draw, reused, makes it true: the two windows are
    # byte-identical up to the tail, and the tail is the only thing that moves.
    shared = strings(rng, COUNT_LENS)

    # (2) the count lies and the tail is unterminated: R1 walks into filler
    #     that was never a string and off the end of the blob.
    body = shared + rng.randbytes(COUNT_TAIL).translate(NONZERO)
    write("adversarial-count.bin", ADV_ITERS, HDR + len(body),
          window(COUNT_NSTR, body))

    # (3) the SAME count lie with a NUL tail: harmless in every rung. The
    #     control that shows the declared count is not a bound.
    assert ZEROTAIL_LENS == COUNT_LENS, "the pair must share its strings"
    body = shared + bytes(ZEROTAIL_TAIL)
    write("adversarial-zerotail.bin", ADV_ITERS, HDR + len(body),
          window(ZEROTAIL_NSTR, body))

    # (4) the degenerate scan: every string is empty.
    write("adversarial-empty.bin", ADV_ITERS, HDR + EMPTY_NSTR,
          window(EMPTY_NSTR, bytes(EMPTY_NSTR)))

    # (5) stride 3: a window too small to hold the 4-byte header. The driver
    #     guard skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3,
          rng.randbytes(STRIDE3_BLOB).translate(NONZERO))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for n in SWEEP_A_LENS:
            write(f"sweep-len{n:02d}k{SWEEP_A_NSTR:02d}.bin", SWEEP_ITERS,
                  stride_of(SWEEP_A_NSTR, (n, 1, 1)),
                  tiled(rng, SWEEP_A_WINS, SWEEP_A_NSTR, (n, 1, 1)))
        for k in SWEEP_B_NSTRS:
            write(f"sweep-len{SWEEP_B_LEN:02d}k{k:02d}.bin", SWEEP_ITERS,
                  stride_of(k, (SWEEP_B_LEN, 1, 1)),
                  tiled(rng, SWEEP_B_WINS, k, (SWEEP_B_LEN, 1, 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
