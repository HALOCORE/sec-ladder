#!/usr/bin/env python3
"""Generate p16's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p16-tlv-walk/inputs/gen.py            # the 5 matrix inputs
    python3 patterns/p16-tlv-walk/inputs/gen.py --sweep    # + value-length sweep

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the record chain; n_blob = payload_len - 8

A record is `tag:u8, vlen:u16le, value:u8[vlen]`, so it occupies `3 + vlen`
bytes. Nothing is a compile-time constant: `n_iters`, `stride`, `n_blob` and
every tag and every length prefix come from the file.

Three things about the sizes are deliberate and must survive any edit.

  * **`small` and `large` have different strides** -- 508 and 4090. Two
    independent reasons, and both have bitten this project:
      - `work_per_call` *is* the stride, and `harness/check.py`'s
        `d(Ir)/d(work)` assertion needs two probe shapes with **different**
        `work_per_call` or it cannot run at all. Two inputs that differ only in
        blob size would silently disable it.
      - the safe-vs-unsafe delta varies with the residue of the measured length
        (`.memory/01-ladder.md`), and quoting one residue as if it were the
        number has been the mistake three times. `_check_residues()` asserts
        that the strides differ mod 4, 8 and 16 **and** that the value lengths
        (124 and 406) do too, so an edit that quietly puts either pair in one
        class fails loudly instead of producing a flattering number.
  * **the strides are not powers of two and the records are odd-sized** (127 and
    409 bytes), so consecutive records do not share a cache-set alignment and
    the offsets the walk visits are not all 8-byte aligned. A length-prefixed
    record on the wire is not aligned; pretending otherwise would flatter every
    rung equally but measure something else.
  * **records tile each window exactly** on `small` and `large`: 4 x 127 = 508
    and 10 x 409 = 4090. So every call walks the same number of records and
    folds `stride - 2 * nrec` of the `stride` bytes -- `work_per_call = stride`
    is therefore a slight over-estimate and the derived `Ir` floor errs strict,
    which is the direction a floor should err.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run and discards whatever is declared here, so the Miri cost of a row
is `4 x (bytes folded per call)`, i.e. `4 x stride` -- **not** `4 x n_blob` and
not a function of `n_iters` at all. Measured fold throughput on this box is
~16 900 B/s against a 180 s budget, so the ceiling is a stride of ~760 KiB.
p16's largest stride is 4090 bytes, four orders of magnitude clear, which is why
every p16 row is Miri-checkable where p01's `large.bin` is not.
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

# The two measured shapes, and the moduli they must not share. Named here rather
# than inline so `_check_residues` can see them.
SMALL_VLEN, LARGE_VLEN = 124, 406        # value bytes per record
SMALL_RECS, LARGE_RECS = 4, 10           # records per window
SMALL_STRIDE = SMALL_RECS * (3 + SMALL_VLEN)   # 508
LARGE_STRIDE = LARGE_RECS * (3 + LARGE_VLEN)   # 4090
SMALL_WINS, LARGE_WINS = 32, 2050
RESIDUE_MODULI = (4, 8, 16)


def records(rng, vlens):
    """A chain of records, one per entry of `vlens`.

    Each is `tag, vlen_lo, vlen_hi, value...`. The tag is random rather than
    zero: ../spec.md folds it, so a constant tag would be one byte per record
    the checksum could not distinguish, and a rung that mis-parsed the chain but
    folded the same value bytes could still agree."""
    out = bytearray()
    for ln in vlens:
        out.append(rng.randrange(256))
        out.append(ln & 0xFF)
        out.append((ln >> 8) & 0xFF)
        out += rng.randbytes(ln)
    return out


def tiled(rng, nwin, recs_per_win, vlen, pad=0):
    """`nwin` windows, each exactly `recs_per_win` records of `vlen` value bytes
    followed by `pad` bytes of tail. Every window is byte-identical in *shape*
    and different in *content*, which is what makes the walk's trip count come
    from the data while the driver's `work_per_call` stays constant."""
    out = bytearray()
    for _ in range(nwin):
        out += records(rng, [vlen] * recs_per_win)
        out += rng.randbytes(pad)
    return bytes(out)


def _check_residues():
    """Both measured pairs must differ modulo every modulus that has ever bitten
    this project. Returns a list of problems (empty when healthy).

    p01's first draft used 500 and 4096, both == 0 (mod 4), the single worst
    residue for R2, and overstated it 2.4x. p02's used 61 and 4092, which differ
    mod 4 and mod 8 -- and that was still not enough, because the modulus that
    governed its copy epilogue was 16. So both p16 pairs are checked against all
    three: the **stride**, which is `work_per_call` and the outer walk's total
    length, and the **value length**, which is the inner fold's trip count."""
    bad = []
    for label, a, b in (("stride", SMALL_STRIDE, LARGE_STRIDE),
                        ("value length", SMALL_VLEN, LARGE_VLEN)):
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label}s ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


# `--sweep`: (first_vlen, n_vlens, recs_per_win, nwin, n_iters). Diagnostic only;
# `harness/check.py` and `harness/measure.py` both skip the `sweep-` prefix.
#
# Two full mod-16 cycles per band, plus the endpoints, because two points and a
# line is not a curve and one cycle cannot tell a period of 16 from a period of
# 64 (p02's first sweep design made exactly that mistake). The sweep is over the
# **value length**, i.e. the inner fold's trip count, with the number of records
# per window held fixed -- so the stride moves with it and the two loops are not
# fully separated. That is a limitation of a chain that has to tile a window
# exactly; NOTES.md 3 separates the loops by rewriting them, not by sweeping.
SWEEP_CYCLES = 2
SWEEP_BANDS = ((56, RESIDUE_MODULI[-1] * SWEEP_CYCLES + 2, 4, 32, 25_000),
               (2040, RESIDUE_MODULI[-1] * SWEEP_CYCLES + 2, 2, 16, 5_000))

# The THIRD band, and it sweeps a different axis: `nrec`, the number of records
# per window, with the value length held fixed. Added at TASK_020.
#
# Both bands above sit at `nrec` 4 and 2, so between them the committed
# generator moves the *residue* and holds `nrec` essentially fixed. NOTES.md
# 10a's load-bearing statement is the opposite shape -- four laws linear in
# `nrec` (`2*nrec - 2`, `4*nrec - 8`, `nrec`, and `7 + 5*nrec` / `7 + 7*nrec`),
# promoted from a three-point fit to a swept law at TASK_018_REVIEW over inputs
# that were never committed. So the tree could state the law and not reproduce
# it, which is the shape of defect `nrec + 3` already cost this pattern once.
#
# Two decisions worth defending:
#
#   * **the `nrec` values are not consecutive** -- 1..9, then 12 and 16. Every
#     law here is claimed to be affine in `nrec`, and 1..9 is nine consecutive
#     points, which is what tests that; 12 and 16 are the lever arm that
#     separates an affine law from a low-order polynomial fitted to a short run.
#     The `+3` failure was a three-point fit, and nine consecutive points plus
#     two distant ones is a different object.
#   * **both residue classes ship**, 22 blobs rather than 11, because the fourth
#     law is the only one that is residue-dependent (`7 + 5*nrec` at
#     `vlen == 0 mod 4` against `7 + 7*nrec` otherwise). One class reproduces
#     three of the four laws and silently turns the fourth into a fit. 124 and
#     126 are the two classes NOTES.md 10a used, and 124 is `small`'s own value
#     length, so one column of the band is directly comparable with the matrix.
#
# This band is appended AFTER the two above and the RNG is drawn sequentially,
# so every `sweep-v*.bin` the earlier bands emit is byte-identical to before.
SWEEP_NRECS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16)
SWEEP_NREC_VLENS = (124, 126)      # 0 and 2 mod 4 -- NOTES.md 10a's two classes
SWEEP_NREC_WINS = 16
SWEEP_NREC_ITERS = 5_000

# The FOURTH band, `sweep-k*`, added at TASK_027. It sweeps the same axis as the
# first two -- the value length, `nrec` held at 2 -- and exists for one reason
# the first two cannot serve: NOTES.md 10a.2 measures the value fold respelled as
# `chunks_exact(K)` up to **K = 64**, and a per-byte rate at chunk width `K` is
# only readable from a pair of blobs whose value lengths differ by a MULTIPLE OF
# K, or the two ends of the difference carry different `.remainder()` tails and
# the epilogue does not cancel. Bands A and B span 34 consecutive lengths each,
# so between them the committed tree contains no pair differing by 32 either --
# 10a.2's K = 32 and K = 64 rows were measured on scratch blobs that were never
# committed, which is the same "the tree states a law it cannot re-derive"
# defect the third band was added to close, on its fourth sighting.
#
# Three decisions, and each is forced rather than chosen:
#
#   * **CONSECUTIVE, not a mod-64 triple.** `.temp/p24/gen_k64.py` reached K = 64
#     with three blobs at `vlen` 2040 / 2168 / 2296, all == 56 (mod 64). That is
#     three points at ONE residue offset, and TASK_025_REVIEW measured what that
#     costs: the three "residue-matched bands" 10a.2 published are three pairs
#     all sitting at 24 (mod 32), and a legitimately matched pair at a different
#     offset moves the rate by ±0.01 Ir/byte (the driver's `println` digit-count
#     term, which does not cancel within one binary). A consecutive band gives
#     every offset, so the null is swept rather than sampled -- and the review's
#     own 128-blob consecutive sweep needed no mod-64 triple at all.
#   * **the width follows this file's own rule**, `2 cycles + 2` of the largest
#     modulus measured, which for the fold band is K = 64 rather than 16: two
#     cycles because one cannot tell a period of 64 from a period of 128, and the
#     +2 for the endpoints. 130 lengths.
#   * **appended LAST, after the `nrec` band**, and the RNG is drawn sequentially,
#     so every blob the first three bands emit stays BYTE-IDENTICAL. Measured at
#     TASK_027, not asserted: sha256 of all 95 pre-existing blobs before and
#     after, 0 differences. That is why this costs a gate RE-RUN (the record's
#     `source_sha256` for this file moves) and not a re-measure -- `check.py` and
#     `measure.py` both drop the `sweep-` prefix, so no matrix input, no
#     `inputs_checked` entry and no number in `results/p16-tlv-walk.json` depends
#     on any of it.
SWEEP_FOLD_K = 64                  # the largest chunk width NOTES.md 10a.2 measures
SWEEP_FOLD_FIRST = 120
SWEEP_FOLD_N = SWEEP_FOLD_K * SWEEP_CYCLES + 2
SWEEP_FOLD_RECS = 2
SWEEP_FOLD_WINS = 16
SWEEP_FOLD_ITERS = 5_000


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-v*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p16 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} and value "
          f"lengths {SMALL_VLEN}/{LARGE_VLEN} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 508 B = 15.9 KiB, so the whole working set fits this
    # box's 32 KiB L1 and the row is latency-free.
    write("small.bin", 25_000, SMALL_STRIDE,
          tiled(rng, SMALL_WINS, SMALL_RECS, SMALL_VLEN))
    # large: 2050 windows x 4090 B = 8.0 MiB, 8x this box's 1 MiB L2. The window
    # the driver picks is pseudo-uniform over the whole blob, so every call is a
    # cold 4 KiB walk.
    write("large.bin", 20_000, LARGE_STRIDE,
          tiled(rng, LARGE_WINS, LARGE_RECS, LARGE_VLEN))

    # ---- adversarial: the length field is the attack ----------------------
    # n_iters is small: R1 is executing undefined behaviour on `overrun`, and
    # there is nothing to learn from doing it 25 000 times.

    # (1) THE pattern. A window whose last record declares a value longer than
    #     the bytes that remain. **Exactly one window** (n_blob == stride), and
    #     that is load-bearing rather than tidy: `k` is pseudo-random over
    #     [0, nwin), so with several windows the malformed one would be hit only
    #     probabilistically, and an overrun from a *middle* window stays inside
    #     the allocation -- a silent wrong answer, no ASan, and a gate that
    #     passes by luck. With nwin == 1, k is always 0, the window is also the
    #     last, and R1's read leaves the allocation deterministically.
    #
    #     47 well-formed 64-byte records fill 3008 of the 3072 bytes; the 48th
    #     has 61 bytes of room after its header and claims 4096, so R1 folds
    #     ~4 KiB past a 3 KiB heap block. (And then `p` is past `end`, so
    #     `end - p` underflows and R1's walk does not stop at the buffer end at
    #     all -- see c/kernel.c.)
    over = bytearray(records(rng, [61] * 47))          # 47 * 64 = 3008
    assert len(over) == 3008, len(over)
    over += bytes([rng.randrange(256), 4096 & 0xFF, 4096 >> 8])
    over += rng.randbytes(3072 - len(over))            # the 61 bytes that exist
    assert len(over) == 3072, len(over)
    write("adversarial-overrun.bin", 8, 3072, bytes(over))

    # (2) a window whose tail is too short to hold a header: 3 records of 13
    #     bytes leave 2 of the 41. Exercises `end - p >= 3`, the test R1 KEEPS,
    #     so every rung must stop cleanly and agree on the checksum. This is the
    #     control for (1): it is the same "the chain ran out" shape with the
    #     length field innocent, and it is declared `clean`.
    write("adversarial-trunc.bin", 8, 41, tiled(rng, 40, 3, 10, pad=2))

    # (3) stride 2: a window too small to hold even a header. The driver guard
    #     `stride_w >= 3` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after zero kernel calls.
    write("adversarial-stride2.bin", 8, 2, tiled(rng, 8, 1, 5))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for first, n, recs, nwin, iters in SWEEP_BANDS:
            for vl in range(first, first + n):
                write(f"sweep-v{vl}.bin", iters, recs * (3 + vl),
                      tiled(rng, nwin, recs, vl))
        # The `nrec` axis (TASK_020). Same `write`, same `tiled`, same tiling
        # rule -- records fill each window exactly, so `work_per_call = stride`
        # keeps erring strict here as it does everywhere else in this file.
        print("  -- sweep over nrec (NOTES.md 10a's axis)")
        for vl in SWEEP_NREC_VLENS:
            for nr in SWEEP_NRECS:
                write(f"sweep-n{nr}v{vl}.bin", SWEEP_NREC_ITERS,
                      nr * (3 + vl), tiled(rng, SWEEP_NREC_WINS, nr, vl))
        # The FOLD band (TASK_027). Appended last for the reason above: drawing
        # the RNG sequentially keeps every blob the three bands above emit
        # byte-identical, so adding it costs a gate re-run and nothing more.
        print(f"  -- sweep over vlen for the fold width (NOTES.md 10a.2's axis, "
              f"{SWEEP_FOLD_N} consecutive lengths at nrec {SWEEP_FOLD_RECS})")
        for vl in range(SWEEP_FOLD_FIRST, SWEEP_FOLD_FIRST + SWEEP_FOLD_N):
            write(f"sweep-k{vl}.bin", SWEEP_FOLD_ITERS,
                  SWEEP_FOLD_RECS * (3 + vl),
                  tiled(rng, SWEEP_FOLD_WINS, SWEEP_FOLD_RECS, vl))
    return 0


if __name__ == "__main__":
    sys.exit(main())
