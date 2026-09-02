#!/usr/bin/env python3
"""Generate p13's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p13-strncpy-trunc/inputs/gen.py            # the 9 matrix inputs
    python3 patterns/p13-strncpy-trunc/inputs/gen.py --sweep     # + the three sweep bands

Payload layout (../spec.md), p11's/p12's/p16's/p17's/p05's/p07's/p03's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nstr  u32 LE      declared string count   ATTACKER DATA
    byte 4..      packed, NUL-terminated strings

and the kernel copies each string into a fixed `dst[DST_CAP]` with exact
`strncpy(dst, src, sizeof dst)` semantics, then reads `dst` back as a C string.
The line R1 omits, and the only thing it omits, is the TERMINATION:

    R1   /* nothing */                 d = 0; while (dst[d] != 0) d++;
    R1h  dst[DST_CAP - 1] = 0;         d = 0; while (dst[d] != 0) d++;

--------------------------------------------------------------------------
WHY small AND large ARE 100% NON-TRUNCATING, AND WHY THAT IS NOT A CHOICE
--------------------------------------------------------------------------
`harness/check.py::check_checksums` requires **every cell, R1 included, to print
`model.py`'s checksum on every non-adversarial input** -- the non-adversarial
set is `check.py::inputs_of`'s `good`. The source scan stops at
the first zero byte, so every one of the `n = min(slen, DST_CAP)` copied bytes
is non-zero, and the zero-fill `for i in n .. DST_CAP` is empty exactly when
`slen >= DST_CAP`. So

    a window holds a string of DST_CAP bytes or more
      <=> `dst` contains no zero byte at all
      <=> R1's consumer scan leaves the array.

R1's answer on such a window is then built from whatever the stack held past
`dst[31]` -- and on some builds **it is not even stable across runs of the same
binary**: measured over 60 runs each, 3 of `c-clang`'s 4 builds give two
different answers and all 4 of `c-gcc`'s are stable (../NOTES.md 0b and 7).
Which way round that falls is a property of the individual binary's frame
layout and cannot be predicted. A p13 row on which the bug fires therefore
cannot also be a checksum-agreeing perf row.

⚠ **This is where TASK_043's input table is wrong and the correction is
measured.** The task file asks `large` for "a **different truncation ratio**"
from `small`. Any non-zero truncation ratio puts R1 out of agreement -- and on
some builds out of agreement with *itself* run to run. So `small` and `large` are
both 0% truncating and what differs between them is the LENGTH DISTRIBUTION
BELOW `DST_CAP` and the working-set size; the truncation-ratio axis lives in
`sweep-t*`, where R1 is excluded for L >= 32 exactly as R1 is excluded from
p12's `sweep-a*`.

--------------------------------------------------------------------------
THE MEAN STRING LENGTH IS THE AXIS, AND small/large SIT ON OPPOSITE SIDES OF 16
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues.
p13's per-string cost is `O(DST_CAP)` whatever the source length is -- the
zero-fill sees to that -- so the mean length is the axis that decides how much
of the work is *source* work and how much is *destination* work:

  * `small`: 13 strings, mean 7.00, 91 source bytes, stride 108;
  * `large`: 24 strings, mean 22.04, 529 source bytes, stride 557.

`_check_residues()` asserts that `nstr`, the source bytes and the stride differ
mod 4, 8, 16 and 32 between the two, that the mean lengths straddle 16, that
**no string in either reaches `DST_CAP`**, and that **`large` dominates `small`
componentwise**. The constants were picked by `.temp/p13/pick_sizes2.py` against
exactly that predicate.

⚠ The domination clause is a MEASURED repair and not tidiness. The first pick
put the two at opposite ends of the count/length trade (20 strings of mean 6.35
against 10 of mean 23.60) and `check.py::check_marginal_ir` then failed 16 of
32 cells whichever way the work was denominated, because **the Ir ordering
between the two inputs is cell-dependent**: 16 cells have Ir(small) > Ir(large)
and 16 the reverse (`.temp/p13/gate1.log`, `.temp/p13/gate2.log`). No scalar
`work_per_call` can satisfy `d(Ir)/d(work) >= 0.25` against an ordering that
flips. p13 is the first pattern here where that could happen at all, and the
cause is the pattern's own headline: `strncpy` costs `DST_CAP` per string
regardless of the source, so "more short strings" and "fewer long strings" are
nearly the same amount of work and the compilers rank them differently.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS SEPARATE THE TWO HARMS -- BY RUNG, BECAUSE NO INPUT CAN
--------------------------------------------------------------------------
⚠ **TASK_043 asks for an `adversarial-truncate` row on which "truncation changes
the answer while every rung stays memory-safe". That input does not exist**, and
the reason is the equivalence three paragraphs up: content is lost iff
`slen >= DST_CAP` iff `dst` holds no NUL iff R1 reads out of bounds. The two
harms fire on **exactly the same inputs**. What separates them is the RUNG:

  * TRUNCATION  -- a memory-safe wrong answer, present in **every** rung
                   including R5. Demonstrated by the `exact` / `truncate` /
                   `truncate-alt` triple below, which are three different
                   windows with the **same checksum**.
  * MISSING NUL -- an out-of-bounds READ, present in **R1 only**. The checked
                   rungs cannot express it.

So the rows are built as a controlled triple plus two routes to the overread:

  * `adversarial-exact`         four strings of exactly `DST_CAP - 1` = 31
                                bytes. The boundary from the SAFE side: the
                                zero-fill writes `dst[31] = 0`, nothing is lost,
                                every rung including R1 agrees and the sanitizer
                                is clean.
  * `adversarial-truncate`      the SAME 31 bytes per string plus ONE more byte,
                                so `slen == DST_CAP`. Nothing about the *copy*
                                changes -- all 32 bytes are copied -- but the
                                termination store overwrites `dst[31]`, so one
                                content byte is silently dropped and R1 has no
                                NUL to stop at.
  * `adversarial-truncate-alt`  the same 31 bytes plus NINE more, `slen == 40`.
                                Nine content bytes dropped instead of one.

  **All three print the identical checksum in every checked rung.** That is the
  memory-safe harm, isolated: three inputs that differ in 0, 1 and 9 dropped
  bytes are indistinguishable to a correct, proven, memory-safe program.

  * `adversarial-nonul-dst`     four 96-byte strings: the overread at full
                                stretch, and the row the per-compiler overrun
                                distance is measured on.
  * `adversarial-nonul-src`     the last string has no terminator, so its
                                measured length is `len - p` = 40 -- p11's
                                malformed record reaching p13's bug through the
                                SOURCE scan's window cap rather than through a
                                declared length.
  * `adversarial-empty`         `nstr = 8` and eight zero bytes. Every string is
                                empty, `n = 0`, the zero-fill writes all 32
                                bytes, `d = 0` and every folded byte is 0: the
                                row where the per-string constant is measured
                                with the source terms set to zero. Returns
                                exactly `nstr == 8`.
  * `adversarial-stride3`       a 3-byte window cannot hold the 4-byte header.
                                The driver guard `stride_w >= 4` skips the loop,
                                so every rung prints 0 after ZERO kernel calls.

`exact`, `truncate` and `truncate-alt` share ONE draw of their four strings'
first 31 bytes, so the three blobs differ only in the tails (p11's TASK_034
lesson: a controlled triple must actually be controlled).
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
DST_CAP = 32                              # must equal every rung's DST_CAP

# 0x00 -> 0x5a. Applied to every string body, so the ONLY zero byte in a window
# is a terminator this file wrote deliberately.
NONZERO = bytes([0x5a] + list(range(1, 256)))

# The two measured shapes, picked by `.temp/p13/pick_sizes2.py`.
# `(base, spread, step)` generates the per-window length multiset
# deterministically; see `length_list`.
SMALL_NSTR, SMALL_LEN = 13, (1, 13, 2)       # lens 1..13,  total 91,  mean 7.00
SMALL_WINS = 140                             # 140 x 108 B = 14.8 KiB, inside L1
LARGE_NSTR, LARGE_LEN = 24, (16, 13, 5)      # lens 16..28, total 529, mean 22.04
LARGE_WINS = 13000                           # 13000 x 557 B = 6.90 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 60000, 20000
ADV_ITERS = 8                             # R1 executes UB on four of them;
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

    The shuffle is safe here in a way it would not be for a p12 window: p13's
    destination is rebuilt from scratch on every string, so `work_per_call` is
    order-independent by construction rather than by argument."""
    base, spread, step = spec
    return [base + (i * step) % spread for i in range(k)]


def stride_of(k, spec):
    """4 header bytes + one terminator per string + the string bytes."""
    return HDR + k + sum(length_list(k, spec))


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and neither may truncate. Returns a list of problems."""
    bad = []
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    for label, lens in (("small", sl), ("large", ll)):
        if max(lens) >= DST_CAP:
            bad.append(f"{label} has a string of {max(lens)} >= DST_CAP="
                       f"{DST_CAP} bytes, so `dst` holds no NUL, R1's consumer "
                       f"reads out of bounds and R1 cannot agree with the model "
                       f"-- see this file's header")
    smean, lmean = sum(sl) / len(sl), sum(ll) / len(ll)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean string length ({smean:.2f}, "
                   f"{lmean:.2f}) are on the same side of 16; the two inputs "
                   f"would measure the same balance of source work against "
                   f"destination work")
    # DOMINATION. `check.py::check_marginal_ir` asserts d(Ir)/d(work) >= 0.25
    # per cell over these two inputs, and the first pick of these constants had
    # `small` and `large` at OPPOSITE ends of the count/length trade -- at which
    # point the measured Ir ordering is CELL-DEPENDENT (16 cells each way;
    # `.temp/p13/gate1.log`, `.temp/p13/gate2.log`) and no scalar work measure
    # can make that assertion pass. `strncpy` writes DST_CAP bytes per string
    # whatever the source length is, so "more short strings" and "fewer long
    # strings" cost nearly the same and -O0/-O3 and gcc/clang order them
    # differently. The repair is to make `large` dominate `small` in EVERY work
    # component at once, so Ir(large) > Ir(small) holds by construction.
    if LARGE_NSTR <= SMALL_NSTR:
        bad.append(f"large must walk MORE strings than small "
                   f"({LARGE_NSTR} <= {SMALL_NSTR}) -- see the domination note")
    if min(ll) < max(sl):
        bad.append(f"large's shortest string ({min(ll)}) is shorter than "
                   f"small's longest ({max(sl)}), so `large` does not dominate "
                   f"`small` componentwise and the Ir ordering between the two "
                   f"collapse probe inputs is not guaranteed -- see the "
                   f"domination note")
    pairs = [("nstr", SMALL_NSTR, LARGE_NSTR),
             ("source bytes per call", sum(sl), sum(ll)),
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
    that shares the oracle's code cannot check the oracle.

    The fold here is ../spec.md's, i.e. FULL-EXTENT since TASK_046: `d` and then
    every one of the `DST_CAP` destination bytes."""
    ln = len(win)
    if ln < HDR:
        return 0
    nstr = int.from_bytes(win[:4], "little")
    if nstr == 0:
        return 0
    mask = (1 << 64) - 1
    dst, acc, p, s = bytearray(DST_CAP), 0, HDR, 0
    while s < nstr:
        q = p
        while q < ln and win[q] != 0:
            q += 1
        slen = q - p
        n = min(slen, DST_CAP)
        dst[0:n] = win[p:p + n]
        dst[n:DST_CAP] = bytes(DST_CAP - n)
        dst[DST_CAP - 1] = 0
        d = dst.index(0)
        acc = (acc * 31 + d) & mask
        for fi in range(DST_CAP):                 # THE FULL-EXTENT FOLD
            acc = (acc * 31 + dst[fi]) & mask
        if q >= ln:
            break
        p = q + 1
        if p >= ln:
            break
        s += 1
    return (acc * 31 + nstr) & mask


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12 and p13 check it,
    which is strictly stronger and costs one pass over the blob at generation
    time."""
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


def tiled_lens(rng, nwin, lens):
    """`nwin` windows from an explicit length multiset (the sweep bands)."""
    out = bytearray()
    for _ in range(nwin):
        shuffled = list(lens)
        rng.shuffle(shuffled)
        out += window(len(lens), strings(rng, shuffled))
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None, check_zero=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:32s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- the controlled truncation triple ---------------------------------------
#
# Four strings. `exact` gives each 31 bytes, `truncate` the same 31 plus 1,
# `truncate-alt` the same 31 plus 9. The first 31 bytes of every string are one
# shared draw, so the three blobs differ only in the tails.
TRUNC_NSTR = 4
TRUNC_HEAD = DST_CAP - 1        # 31
TRUNC_TAILS = (0, 1, 9)         # exact, truncate, truncate-alt

# ---- adversarial-nonul-dst: the overread at full stretch --------------------
NONUL_DST_NSTR = 4
NONUL_DST_LEN = 96

# ---- adversarial-nonul-src: p11's malformed record --------------------------
#
# Two terminated 20-byte strings, then 40 bytes with no terminator. The source
# scan is bounded by the window in every rung, so the third string's measured
# length is `len - p` = 40 >= DST_CAP: the same destination overread, reached
# through the window cap instead of through a terminator.
NONUL_SRC_LENS = [20, 20]
NONUL_SRC_TAIL = 40

# ---- adversarial-empty ------------------------------------------------------
EMPTY_NSTR = 8

# ---- adversarial-stride3 ----------------------------------------------------
STRIDE3_BLOB = 30

# `--sweep`: three bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# The regressors are (1, K, S, C, T) where K is strings walked, S source bytes
# scanned including terminators, C bytes copied and T strings truncated. The
# zero-filled bytes F are NOT an independent regressor: `C + F == DST_CAP * K`
# exactly, by construction of `strncpy`. `../controls/sweep_fit.py` prints the
# pooled design's RANK before it fits anything -- TASK_043 asks for that check
# and p04's precedent is that no pair of its four bands identified its four
# regressors.
#
# **Band N -- the string-count axis, nothing truncating.** All strings are 8
# bytes, so `T == 0`, `C == 8K` and `S == 9K`: rank 2 on its own.
SWEEP_N_LEN = 8
SWEEP_N_KS = tuple(range(1, 25))
SWEEP_N_WINS = 8

# **Band L -- the source-length axis, CROSSING DST_CAP.** `K == 8`, `L = 1..48`.
# `S = 8(L+1)` rises linearly while `C = 8*min(L, 32)` SATURATES at 256 and
# `T` switches from 0 to 8 at L = 32. That saturation is the only thing in the
# design that separates a per-scanned-byte term from a per-copied-byte term, and
# it is why the band has to cross `DST_CAP` rather than stop below it.
# **R1 is not measurable on this band for L >= 32**: its consumer would read
# past `dst[31]`. That exclusion is the price of the bug being an overread and
# it is stated in ../NOTES.md rather than worked around.
SWEEP_L_NSTR = 8
SWEEP_L_LENS = tuple(range(1, 49))
SWEEP_L_WINS = 8

# **Band T -- the truncation-RATIO axis, count held at 16.** `t` of the 16
# strings are 40 bytes and `16 - t` are 8, `t = 0 .. 16`. Every regressor is
# linear in `t`, so the band is rank 2 on its own -- it is here as the
# OUT-OF-SAMPLE test `.memory/03-measurement.md` demands: at `0 < t < 16` it is
# the only blob in the pattern that turns on truncating and non-truncating
# strings **simultaneously**, which is the combination p04's 99 in-sample blobs
# did not have.
SWEEP_T_NSTR = 16
SWEEP_T_SHORT = 8
SWEEP_T_LONG = 40
SWEEP_T_TS = tuple(range(0, 17))
SWEEP_T_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p13 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sl, ll = length_list(SMALL_NSTR, SMALL_LEN), length_list(LARGE_NSTR, LARGE_LEN)
    print(f"  residues ok: nstr {SMALL_NSTR}/{LARGE_NSTR}, source bytes "
          f"{sum(sl)}/{sum(ll)}, strides "
          f"{stride_of(SMALL_NSTR, SMALL_LEN)}/{stride_of(LARGE_NSTR, LARGE_LEN)}, "
          f"mean string length {sum(sl)/len(sl):.2f}/{sum(ll)/len(ll):.2f}, "
          f"lengths {min(sl)}..{max(sl)}/{min(ll)}..{max(ll)}, "
          f"DST_CAP={DST_CAP}, truncating strings 0/0")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NSTR, SMALL_LEN),
          tiled(rng, SMALL_WINS, SMALL_NSTR, SMALL_LEN))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NSTR, LARGE_LEN),
          tiled(rng, LARGE_WINS, LARGE_NSTR, LARGE_LEN))

    # ---- adversarial ------------------------------------------------------
    # (1)-(3) are a CONTROLLED TRIPLE: one draw of four 31-byte heads, then
    #         0 / 1 / 9 extra bytes per string. Every checked rung prints the
    #         SAME checksum on all three; R1 reads out of bounds on the second
    #         and third and not on the first.
    heads = [rng.randbytes(TRUNC_HEAD).translate(NONZERO)
             for _ in range(TRUNC_NSTR)]
    for tail, name in zip(TRUNC_TAILS, ("adversarial-exact.bin",
                                        "adversarial-truncate.bin",
                                        "adversarial-truncate-alt.bin")):
        body = bytearray()
        for h in heads:
            body += h + rng.randbytes(tail).translate(NONZERO) + b"\x00"
        write(name, ADV_ITERS, HDR + len(body), window(TRUNC_NSTR, bytes(body)))

    # (4) the overread at full stretch: four 96-byte strings.
    body = strings(rng, [NONUL_DST_LEN] * NONUL_DST_NSTR)
    write("adversarial-nonul-dst.bin", ADV_ITERS, HDR + len(body),
          window(NONUL_DST_NSTR, body))

    # (5) the last string has no terminator: p11's malformed record reaching
    #     p13's bug through the SOURCE scan's window cap.
    body = (strings(rng, NONUL_SRC_LENS)
            + rng.randbytes(NONUL_SRC_TAIL).translate(NONZERO))
    write("adversarial-nonul-src.bin", ADV_ITERS, HDR + len(body),
          window(len(NONUL_SRC_LENS) + 1, body))

    # (6) the degenerate copy: every string is empty, so `n` is 0, the zero-fill
    #     writes all DST_CAP bytes, `d` is 0 and every folded byte is 0.
    write("adversarial-empty.bin", ADV_ITERS, HDR + EMPTY_NSTR,
          window(EMPTY_NSTR, bytes(EMPTY_NSTR)))

    # (7) stride 3: a window too small to hold the 4-byte header. The driver
    #     guard skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3,
          rng.randbytes(STRIDE3_BLOB).translate(NONZERO), check_zero=False)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for k in SWEEP_N_KS:
            lens = [SWEEP_N_LEN] * k
            write(f"sweep-n{k:02d}L{SWEEP_N_LEN:02d}.bin", SWEEP_ITERS,
                  HDR + k + sum(lens), tiled_lens(rng, SWEEP_N_WINS, lens))
        for n in SWEEP_L_LENS:
            lens = [n] * SWEEP_L_NSTR
            write(f"sweep-l{SWEEP_L_NSTR:02d}L{n:02d}.bin", SWEEP_ITERS,
                  HDR + SWEEP_L_NSTR + sum(lens),
                  tiled_lens(rng, SWEEP_L_WINS, lens))
        for t in SWEEP_T_TS:
            lens = [SWEEP_T_LONG] * t + [SWEEP_T_SHORT] * (SWEEP_T_NSTR - t)
            write(f"sweep-t{SWEEP_T_NSTR:02d}T{t:02d}.bin", SWEEP_ITERS,
                  HDR + SWEEP_T_NSTR + sum(lens),
                  tiled_lens(rng, SWEEP_T_WINS, lens))
    return 0


if __name__ == "__main__":
    sys.exit(main())
