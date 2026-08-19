#!/usr/bin/env python3
"""Generate p07's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and since TASK_021 `harness/check.py` hashes it into `source_sha256`, so every
law measured on these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p07-binary-search/inputs/gen.py            # the 7 matrix inputs
    python3 patterns/p07-binary-search/inputs/gen.py --sweep    # + the log2 n sweep

Payload layout (../spec.md), p16's/p17's/p05's verbatim:

    word 0     u64  stride     bytes per window; the kernel folds one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    n     u32 LE      declared element count   ATTACKER DATA
    byte 4..8    nq    u32 LE      declared query count     ATTACKER DATA
    byte 8..     elements  u32 LE x n      SORTED ASCENDING
    byte 8+4n..  queries   u32 LE x nq
    avail = len - 8 bytes actually present

and the kernel binary-searches each query over the declared array. The check
that R1 omits, and the only line it omits, is

    if (4 * n + 4 * nq > avail) return 0;   /* computed in 64 bits */

--------------------------------------------------------------------------
SORTEDNESS IS A PROPERTY OF THE FILE
--------------------------------------------------------------------------
No rung sorts anything and no rung checks sortedness -- and neither does
../verus.rs's specification, which defines what the *search* returns rather
than "the position of the key". That is why `adversarial-unsorted.bin` is a
correctness row and not a safety row: every rung stays in bounds on it, every
rung agrees with `../model.py` on it, and the answer is simply not the answer a
sorted array would have given. A `requires` about sortedness would be a
precondition no honest loader could discharge
(`.memory/02-bench-rules.md`).

--------------------------------------------------------------------------
THE HIT/MISS RATIO IS EXACTLY 1/2, AND IT IS THE SAME ON EVERY INPUT
--------------------------------------------------------------------------
`nq` is even everywhere, and each window's query list is `nq/2` values drawn
uniformly from the array (guaranteed HITS) plus `nq/2` guaranteed MISSES, then
shuffled with the seeded RNG. Of the misses, exactly one is BELOW every element
and one is ABOVE every element, and the rest
are of the form `element + 1` (a guaranteed miss because consecutive elements
differ by at least 2). The below-minimum key is load-bearing and its absence was
a measured defect in the first draft of this file -- see `query_list`.

Both halves are load-bearing and TASK_026 asks for the ratio to be stated:

  * a **pure-miss** workload walks the full `ceil(log2(n+1))` probes on every
    query and never takes the `v == key` branch, so it would flatter whichever
    rung handles the early exit worst and would make the trip count constant;
  * a **pure-hit** workload exits early at a data-dependent depth, so the mean
    probe count would drop by about one and the `==` branch would stop being
    predictable-not-taken;
  * and **shuffling** matters because an alternating hit/miss pattern is itself
    a pattern a branch predictor can learn. The point of this kernel is the
    unpredictable branch (`.memory/01-ladder.md` findings 5 and 6), so the
    workload must not accidentally be predictable.

Keeping the ratio identical across `small`, `large` and every sweep band is what
makes a rung-to-rung difference a difference between *rungs*.

--------------------------------------------------------------------------
RESIDUES: p05's BATTERY DOES NOT TRANSFER, AND HERE IS WHAT REPLACES IT
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues, and
records p01's modulus 4, p02's 16, p16's 4, p17's 4 and p05's 8-and-16. **Every
one of those is a vector width or an unroll factor**, i.e. a property of a loop
whose trip count the compiler knows. p07 has no such loop: the search loop's
trip count is data and its next address depends on the previous comparison, so
nothing unrolls and nothing vectorises. Assuming p05's moduli here would be
assuming the answer.

What governs p07 instead is `ceil(log2(n+1))` -- the trip count -- and where `n`
sits *inside* its octave, because the last probe of a search over
`n = 2^k - 1` is not the last probe of a search over `n = 2^k + 1`. So
`_check_residues()` asserts:

  * `ceil(log2(n+1))` differs                        (9 vs 18);
  * `n`'s distance below the next power of two differs, and differs mod 4 and 8
                                                     (200 vs 9);
  * `n` and `nq` differ mod 4, 8, 16 and 32;
  * `nq * ceil(log2(n+1))` -- the probe count, i.e. `work_per_call` -- differs
    mod 4, 8, 16 and 32;
  * the stride differs mod 8, 16 and 32. It **cannot** differ mod 4: the stride
    is `8 + 4*(n + nq)`, so it is 0 mod 4 by construction on every input this
    format can express. Stated rather than silently dropped.

and the **sweep** is what establishes the real period, rather than this file
asserting it. `--sweep` band A walks `2^k - 1`, `2^k`, `2^k + 1` for
k = 3 .. 14 -- twelve octaves, so twelve full cycles of the only modulus in
play -- and band B walks 64 consecutive `n` straddling 255/256, which is where
the trip count steps.

--------------------------------------------------------------------------
SIZES
--------------------------------------------------------------------------
  * `small`: 12 windows x 1488 B = 17.4 KiB, inside this box's 32 KiB L1, so
    every probe hits L1 and the wall clock is set by the branch and not by the
    memory system. 312 elements = 1248 B of array per window.
  * `large`: 12 windows x 1 048 916 B = 12.0 MiB. **One window's array alone is
    1 048 540 B**, i.e. the array is L2-sized (this box: 1 MiB/core) and the
    whole blob is 12x L2. The top ~8 levels of each search tree stay in L1 and
    the bottom ~10 miss, which is the pointer-chasing-like regime p07 exists to
    put beside `small`.
  * every adversarial input is exactly one window (`n_blob == stride`), for p16's
    and p17's reason: `k = (acc * nwin) >> 64` is pseudo-random over
    `[0, nwin)`, so with several windows the malformed one is hit only
    probabilistically, and an overrun from a *middle* window stays inside the
    allocation -- a silent wrong answer, no ASan, and a gate that passes by
    luck. With `nwin == 1`, `k` is always 0 and `off` is always 0.
  * **window 0 must serve something** on every input where anything is meant to
    be visited (p17, `.memory/01-ladder.md`): a window returning 0 pins `acc` at
    0, and `k = (acc * nwin) >> 64` is then 0 for ever -- the driver's Lemire
    index has an absorbing state at `acc == 0`. On `small`/`large` every window
    runs a full query batch, so this is satisfied by construction. On the
    adversarial inputs there is only one window, so `k == 0` regardless.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run and discards whatever is declared here, so the Miri cost of a row
is dominated by the payload `to_vec` (a bulk copy -- `head1_u64_bytes`, which is
why p16/p17/p05 are all Miri-clean where p01's element-by-element decoder is
not) plus `4 x (bytes probed per call)`. p07 probes only `4 * work_per_call`
bytes: **2088 on `small` and 6624 on `large`**, against p05's 1976 and 15 860.
So p07 is the cheapest pattern in the project to Miri *per call*, and the only
thing that costs anything is the 12 MB `to_vec`. ../NOTES.md 8 reports the
measured wall time.
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

HDR = 8                                   # n:u32 + nq:u32

# The two measured shapes. Chosen by `.temp/p07/pick_sizes.py` against
# `_check_residues()` below; `nq` is even on both so the hit fraction is exactly
# 1/2 on both.
SMALL_N, SMALL_NQ, SMALL_WINS = 312, 58, 12
LARGE_N, LARGE_NQ, LARGE_WINS = 262135, 92, 12

SMALL_ITERS, LARGE_ITERS = 8000, 1200
ADV_ITERS = 8                             # R1 executes UB on two of them; there
                                          # is nothing to learn from doing it
                                          # 8000 times.

RESIDUE_MODULI = (4, 8, 16, 32)

# Consecutive elements differ by at least MIN_GAP, so `element + 1` is
# guaranteed NOT to be an element and is therefore a guaranteed miss.
MIN_GAP, MAX_GAP = 2, 18


def ceil_log2_plus1(n):
    """Max probes of a half-open binary search over `n` elements: the same
    `ceil(log2(n+1))` `../model.py` computes, duplicated here on purpose --
    `gen.py` must be able to state the shape of the file it is writing without
    importing the model the gate checks against."""
    k, span = 0, 1
    while span < n + 1:
        span *= 2
        k += 1
    return k


def stride_of(n, nq):
    return HDR + 4 * n + 4 * nq


def _check_residues():
    """Every measured pair must differ on the axes that govern THIS kernel.
    Returns a list of problems (empty when healthy). The reasoning is in the
    module docstring; the short version is that p05's vector-width moduli
    describe a loop p07 does not have, and the axis here is `log2 n`."""
    bad = []
    sl2, ll2 = ceil_log2_plus1(SMALL_N), ceil_log2_plus1(LARGE_N)
    if sl2 == ll2:
        bad.append(f"small and large ceil(log2(n+1)) are both {sl2}; the trip "
                   f"count IS the axis of this pattern and quoting one value "
                   f"of it as if it were a constant is the whole trap")
    sd = (1 << sl2) - SMALL_N
    ld = (1 << ll2) - LARGE_N
    pairs = [("n", SMALL_N, LARGE_N, RESIDUE_MODULI),
             ("nq", SMALL_NQ, LARGE_NQ, RESIDUE_MODULI),
             ("probes per call (work_per_call)",
              SMALL_NQ * sl2, LARGE_NQ * ll2, RESIDUE_MODULI),
             # the stride is 8 + 4*(n+nq), hence 0 mod 4 on EVERY input this
             # format can express -- so mod 4 is not checked, deliberately.
             ("stride", stride_of(SMALL_N, SMALL_NQ),
              stride_of(LARGE_N, LARGE_NQ), (8, 16, 32)),
             ("distance below the next power of two", sd, ld, (4, 8))]
    for label, a, b, moduli in pairs:
        for m in moduli:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    if SMALL_NQ % 2 or LARGE_NQ % 2:
        bad.append("nq must be even on every measured input, or the hit "
                   "fraction is not exactly 1/2 and a rung-to-rung difference "
                   "is partly a workload difference")
    return bad


# ---------------------------------------------------------------- content ----

def sorted_elements(rng, n):
    """`n` strictly increasing u32s with gaps in [MIN_GAP, MAX_GAP).

    The gap floor of 2 is what makes `element + 1` a guaranteed miss, which is
    how the 50/50 workload below is built without a membership test."""
    out = []
    v = rng.randrange(1, 8)
    for _ in range(n):
        out.append(v)
        v += rng.randrange(MIN_GAP, MAX_GAP)
    return out


def query_list(rng, elems, nq):
    """`nq/2` guaranteed hits and `nq/2` guaranteed misses, shuffled.

    **The misses are not all interior, and that was a measured mistake once.**
    The obvious construction -- every miss is `element + 1` -- draws every key
    from `[elems[0] + 1, elems[n-1] + 1]`, so **no key is ever below
    `elems[0]`**. Built that way, the textbook inclusive spelling
    (`hi = n - 1`, `while lo <= hi`, `hi = mid - 1`) never reaches `mid == 0`
    with `v > key`, never underflows, and runs to completion on `small.bin`
    printing the correct answer -- measured, and it is why this function has the
    two extra lines below. A workload that cannot reach the underflow cannot be
    used to say the underflow does not happen.

    So every window with `nq >= 4` carries exactly **one key below the minimum**
    and **one above the maximum**, and the remaining misses are interior. On the
    same window the inclusive spelling SIGSEGVs (../NOTES.md 6). `elems[0] >= 1`
    is guaranteed by `sorted_elements`, so `elems[0] - 1` is a representable
    u32."""
    n = len(elems)
    nmiss = nq - nq // 2
    qs = [elems[rng.randrange(n)] for _ in range(nq // 2)]
    if nmiss >= 2:
        qs += [elems[0] - 1, elems[n - 1] + 1]
        nmiss -= 2
    qs += [elems[rng.randrange(n)] + 1 for _ in range(nmiss)]
    rng.shuffle(qs)
    return qs


def window(n_decl, nq_decl, elems, keys):
    """One window: the two declared counts, then the elements, then the queries.

    `n_decl`/`nq_decl` are written verbatim rather than derived from the lists,
    so that `adversarial-count` and `adversarial-width` can declare an array the
    window cannot hold -- which is the whole pattern."""
    return (struct.pack("<II", n_decl, nq_decl)
            + struct.pack("<%dI" % len(elems), *elems)
            + struct.pack("<%dI" % len(keys), *keys))


def tiled(rng, nwin, n, nq, shuffle_elems=False):
    """`nwin` windows, identical in *shape* and different in *content*.

    The shape is fixed so `work_per_call` is one scalar; the elements and
    queries differ per window so the checksum depends on which window the driver
    picked, which is what keeps the anti-collapse barrier honest."""
    out = bytearray()
    for _ in range(nwin):
        elems = sorted_elements(rng, n)
        keys = query_list(rng, elems, nq)
        if shuffle_elems:
            rng.shuffle(elems)
        out += window(n, nq, elems, keys)
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<9d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-count: the declared array does not fit ---------------------
#
#   len = 88, avail = 80, n = 4096, nq = 4  ->  4*n + 4*nq = 16400 > 80
#
# R1 omits `4*n + 4*nq > avail` and therefore reads query 0 at window byte
# 8 + 4*4096 = 16 392 and probes element 2048 at window byte 8200, out of an
# 88-byte blob. One window, so `off == 0` and the overrun is deterministic
# rather than a coin flip on `k`.
#
# **4096 rather than 2^31: the point is a *detectable* overrun, not a long one.**
# 16 KiB past an 88-byte allocation is still inside the process heap, so a plain
# build reads memory it does not own and prints a wrong number -- p02's result,
# and the one worth reproducing -- while ASan's redzones make it a clean
# `heap-buffer-overflow`. `adversarial-width` is the far one.
#
# The window carries 16 real elements and 4 real queries, so a *hardened* rung
# has something well-formed to reject rather than something malformed.
COUNT_ELEMS, COUNT_QUERIES, COUNT_N, COUNT_NQ = 16, 4, 4096, 4

# ---- adversarial-width: the length check written in the wrong width ---------
#
#   n = 2^30, nq = 1  ->  4*n + 4*nq = 4 294 967 300
#
# In `size_t`/`u64` that is 4.29e9 and greater than any `avail` this benchmark
# can present, so **every shipped rung rejects the window and returns 0** except
# R1, which has no check of any width and reads 4 GiB past the blob (SIGSEGV in
# every plain build; ASan reports it too). What this input is *for* is the
# hardened-wrong cell: the same check written in 32 bits.
#
# **And the width that breaks here is `unsigned`, not just `int` -- p07 and p05
# sit on opposite sides of that boundary.** `n` and `nq` are u32 fields, so
# `4*n + 4*nq` reaches 34 359 738 360 and needs 36 bits; at n = 2^30 the 32-bit
# product is exactly 2^32 = 0 (mod 2^32) and the test `4 > 80` is false. p05's
# `nrow*ncol` comes from u16 fields, tops out at 4 294 836 225, and therefore
# still FITS `uint32_t` -- only p05's *signed* spelling breaks. ../NOTES.md 6
# builds both narrow variants and measures them.
WIDTH_ELEMS, WIDTH_QUERIES, WIDTH_N, WIDTH_NQ = 16, 4, 1 << 30, 1

# ---- adversarial-zero: a zero element count --------------------------------
#
#   n = 0, nq = 8  ->  4*0 + 4*8 = 32 <= avail, so the LENGTH check passes
#
# and the `n == 0 || nq == 0` guard is what the kernel meets next. **In the
# shipped half-open spelling that guard changes no answer and prevents no
# access**: with `n == 0` the search bounds are `lo = 0, hi = 0`, the loop does
# not run, every query folds `NOT_FOUND + 1 == 0`, and `n*nq == 0`, so the fold
# returns 0 either way. It is not a correctness check, not a memory-safety check
# and not even a work check (`nq` is bounded by `avail/4`, so there is no DoS).
#
# It is kept, and this input exists, because that deadness **is p07's result**:
# in the textbook *inclusive* spelling -- `hi = n - 1`, `while lo <= hi`,
# `hi = mid - 1` -- the same guard is the only thing standing between `n == 0`
# and `hi = SIZE_MAX`, i.e. a probe at index 2^63. ../NOTES.md 6 derives that
# variant from `c/kernel.c` by exact-string substitution and runs it on this
# file. See ../spec.md, "The zero guard is dead here, and that is the result".
ZERO_N, ZERO_NQ = 0, 8

# ---- adversarial-unsorted: the file breaks the algorithm's assumption -------
#
# Same shape as `small`'s window, with the element array shuffled after the
# queries were drawn. Every rung stays in bounds (the search only ever forms
# indices `< n`), every rung agrees with `../model.py`, and the answer is simply
# not the answer a sorted array would give. This is the row that shows the
# difference between a *correctness* violation and a *safety* violation, and it
# is why neither the spec nor any `requires` mentions sortedness.
UNSORTED_N, UNSORTED_NQ = SMALL_N, SMALL_NQ

# `--sweep`: three bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# **Band A -- the log2 n axis, and it is twelve full cycles.** `.memory` says
# sweep two full cycles of whatever modulus the codegen chose and never sample
# two points. The only modulus in a data-dependent search loop is the octave, so
# band A walks `2^k - 1`, `2^k`, `2^k + 1` for k = 3..14: the powers of two and
# the values on either side, which is exactly where `ceil(log2(n+1))` steps.
# k = 8 is deliberately absent: band B below walks 224..287 at the same `nq`,
# so 255/256/257 are already in the sweep and emitting them twice would write
# the same file name twice with different content.
SWEEP_A_K = (3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14)
SWEEP_A_NQ = 58
SWEEP_A_WINS = 8

# **Band B -- 64 consecutive `n` straddling 255/256**, so that the step in the
# trip count is located rather than assumed, and so that a law of the form
# `a + b*ceil(log2(n+1))` has 64 points to be wrong at instead of 3.
SWEEP_B_FIRST, SWEEP_B_COUNT = 224, 64
SWEEP_B_NQ = 58
SWEEP_B_WINS = 8

# **Band C -- the `nq` axis, `n` held at 312.** Bands A and B move `n` and hold
# `nq`, so every per-call constant they yield is confounded with `nq`. Band C
# moves `nq` over 16 values at fixed `n`, which is what separates the per-CALL
# term from the per-QUERY term -- and `.memory/01-ladder.md` records that
# separating those is exactly where p16's `nrec + 3` and p05's `+11.00 flat`
# both died.
SWEEP_C_N = 312
SWEEP_C_NQS = tuple(range(4, 36, 2))
SWEEP_C_WINS = 8
SWEEP_ITERS = 2000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p07 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sl2, ll2 = ceil_log2_plus1(SMALL_N), ceil_log2_plus1(LARGE_N)
    print(f"  residues ok: n {SMALL_N}/{LARGE_N}, nq {SMALL_NQ}/{LARGE_NQ}, "
          f"strides {stride_of(SMALL_N, SMALL_NQ)}/"
          f"{stride_of(LARGE_N, LARGE_NQ)}, probes/call "
          f"{SMALL_NQ * sl2}/{LARGE_NQ * ll2}, ceil(log2(n+1)) {sl2}/{ll2}, "
          f"distance below 2^k {(1 << sl2) - SMALL_N}/{(1 << ll2) - LARGE_N}; "
          f"hit fraction 1/2 on both")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_N, SMALL_NQ),
          tiled(rng, SMALL_WINS, SMALL_N, SMALL_NQ))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_N, LARGE_NQ),
          tiled(rng, LARGE_WINS, LARGE_N, LARGE_NQ))

    # ---- adversarial ------------------------------------------------------
    # (1) THE pattern. The header declares an array that does not fit.
    ce = sorted_elements(rng, COUNT_ELEMS)
    write("adversarial-count.bin", ADV_ITERS,
          stride_of(COUNT_ELEMS, COUNT_QUERIES),
          window(COUNT_N, COUNT_NQ, ce, query_list(rng, ce, COUNT_QUERIES)))

    # (2) the width the check is written in. Every 64-bit check rejects; the
    #     32-bit variants in ../NOTES.md 6 do not.
    we = sorted_elements(rng, WIDTH_ELEMS)
    write("adversarial-width.bin", ADV_ITERS,
          stride_of(WIDTH_ELEMS, WIDTH_QUERIES),
          window(WIDTH_N, WIDTH_NQ, we, query_list(rng, we, WIDTH_QUERIES)))

    # (3) a zero element count. Every shipped rung returns 0 on every call; the
    #     inclusive-`hi` variant in ../NOTES.md 6 probes index 2^63.
    write("adversarial-zero.bin", ADV_ITERS, stride_of(ZERO_N, ZERO_NQ),
          window(ZERO_N, ZERO_NQ, [],
                 [rng.randrange(1 << 32) for _ in range(ZERO_NQ)]))

    # (4) the file is not sorted. Correctness, not safety: every rung stays in
    #     bounds and every rung agrees with ../model.py.
    write("adversarial-unsorted.bin", ADV_ITERS,
          stride_of(UNSORTED_N, UNSORTED_NQ),
          tiled(rng, 1, UNSORTED_N, UNSORTED_NQ, shuffle_elems=True))

    # (5) stride 7: a window too small to hold the 8-byte header. The driver
    #     guard `stride_w >= 8` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after ZERO kernel calls. Distinct from (3), where
    #     the calls happen and the kernel is what rejects.
    write("adversarial-stride7.bin", ADV_ITERS, 7, bytes(rng.randbytes(56)))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for k in SWEEP_A_K:
            for n in ((1 << k) - 1, 1 << k, (1 << k) + 1):
                write(f"sweep-n{n}q{SWEEP_A_NQ}.bin", SWEEP_ITERS,
                      stride_of(n, SWEEP_A_NQ),
                      tiled(rng, SWEEP_A_WINS, n, SWEEP_A_NQ))
        for n in range(SWEEP_B_FIRST, SWEEP_B_FIRST + SWEEP_B_COUNT):
            write(f"sweep-n{n}q{SWEEP_B_NQ}.bin", SWEEP_ITERS,
                  stride_of(n, SWEEP_B_NQ),
                  tiled(rng, SWEEP_B_WINS, n, SWEEP_B_NQ))
        for nq in SWEEP_C_NQS:
            write(f"sweep-n{SWEEP_C_N}q{nq}.bin", SWEEP_ITERS,
                  stride_of(SWEEP_C_N, nq),
                  tiled(rng, SWEEP_C_WINS, SWEEP_C_N, nq))
    return 0


if __name__ == "__main__":
    sys.exit(main())
