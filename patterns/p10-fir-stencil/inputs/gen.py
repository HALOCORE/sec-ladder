#!/usr/bin/env python3
"""p10-fir-stencil input generator. Deterministic: no `random` module anywhere,
every byte comes from a fixed LCG seeded per blob, so regenerating twice gives
byte-identical files. `harness/check.py` hashes THIS FILE and never the blobs
(`.memory/05-layout.md`), so that determinism is the entire basis of every
swept law p10 publishes -- verify it with

    python3 patterns/p10-fir-stencil/inputs/gen.py --sweep
    sha256sum patterns/p10-fir-stencil/inputs/*.bin > /tmp/a   # (use .temp/)
    python3 patterns/p10-fir-stencil/inputs/gen.py --sweep
    sha256sum -c ...

Usage:

    python3 patterns/p10-fir-stencil/inputs/gen.py            # the matrix inputs
    python3 patterns/p10-fir-stencil/inputs/gen.py --sweep     # + the sweep bands

File format: `.memory/02-bench-rules.md`. Payload is
`u64 stride` then the window blob, decoded by `slb.head1_u64_bytes`.

Window layout (../spec.md):

    byte 0..4     n     u32 LE   DECLARED sample count
    byte 4..8     r     u32 LE   DECLARED radius            RUNTIME radius
    byte 8..      w[]  u8 x (2r+1)   the FIR coefficients
    byte 8+2r+1.. s[]  u8 x n        the samples

**Every BENIGN window is packed exactly full**: `stride == 8 + taps + n`, so
`last == 8 + taps + n - 1 == stride - 1` and the check `last >= len` is false in
every rung, R1's `last > len` included. That is what makes R1 and R1h
behaviourally identical on every non-adversarial input, which
`harness/check.py` stage 2 requires -- and it is why p10's bug had to be
conditional on attacker data rather than a plain fencepost in the output loop.

**Sweep bands.** `sweep-*` blobs are diagnostic: `check.py` and `measure.py`
both drop them, so appending a band costs a gate re-run and NOT a re-measure.
Bands are appended LAST for that reason.

    r<NN>      nout fixed, r = 1..16          the TAP-COUNT axis
    o<NNN>     r fixed,    nout = 8..192      the OUTPUT-COUNT axis
    e<..>      BOTH moved, outside the convex hull of r and o
               -- the ADDITIVITY EXTRAPOLATION rows (`.memory/03-measurement.md`)
    h<NN>      LENGTH-HETEROGENEOUS: several windows of DIFFERENT (n, r) in one
               blob, so no band is a scalar multiple of another and the design
               does not collapse to rank 2 when a band is dropped

The `e` band is the one that can fail: `r` and `nout` are never large together
in `r`/`o`/`h`, so an `e` row is outside the row space of the fit set by
construction and a linear combination of fitted rows cannot reach it.
"""
import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
M32 = (1 << 32) - 1
HDR = 8


# ------------------------------------------------------------------- bytes --
def lcg(seed):
    """A fixed 31-bit LCG. Deliberately NOT `random`: `.memory/05-layout.md`
    records that `random.shuffle`'s rejection sampling makes stream consumption
    data-dependent, so two blobs can re-converge and an edit to one band can
    silently move another. One generator per window, seeded from that window's
    own parameters, so no blob's bytes depend on any other blob."""
    x = seed & 0x7FFFFFFF
    while True:
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        yield (x >> 16) & 0xFF


def window(n, r, seed, short=0):
    """One window, packed exactly full unless `short` says otherwise.

    `short=1` removes the LAST sample byte while leaving `n` declared, which is
    exactly the input R1's fencepost accepts and every other rung rejects."""
    taps = 2 * r + 1
    g = lcg(seed)
    b = bytearray(struct.pack("<II", n, r))
    # Coefficients are small (1..7). Not for overflow -- every rung wraps -- but
    # so that `truncating`-style saturation cannot hide a wrong tap: a zero
    # coefficient would make one tap invisible to the fold, and p06's lesson is
    # that a fold which cannot observe the change is not an oracle.
    b += bytes(1 + (next(g) % 7) for _ in range(taps))
    b += bytes(next(g) for _ in range(n))
    if short:
        del b[len(b) - short:]
    return bytes(b)


def tiled(n, r, nwin, seed0):
    """`nwin` windows of the same shape, so every window has the same
    `work_per_call` and `model.py`'s minimum is exact. Each window gets its own
    LCG seed, so the blob is not a repeated pattern the optimiser could exploit
    and `k` selects genuinely different data."""
    return b"".join(window(n, r, seed0 + 7919 * k) for k in range(nwin))


def emit(path, n_iters, blob, stride, trailing=b""):
    slb.write(path, n_iters, slb.pack_head1_bytes(stride, blob + trailing))
    return stride


# ------------------------------------------------- the checked kernel, again --
# A third implementation of the kernel (model.py has two), used ONLY to check
# the generated files before they are written: p17's trap is that a window
# returning 0 pins `acc` at 0 and the driver's Lemire index `k = (acc*nwin)>>64`
# then has an absorbing state at 0, so window 0 must serve something.
def kern(blob, off, ln):
    if ln < HDR:
        return 0
    n = int.from_bytes(blob[off:off + 4], "little")
    r = int.from_bytes(blob[off + 4:off + 8], "little")
    taps = 2 * r + 1
    if n < taps:
        return 0
    if 8 + taps + n - 1 >= ln:
        return 0
    coef = blob[off + 8:off + 8 + taps]
    samp = blob[off + 8 + taps:off + 8 + taps + n]
    acc = 0
    for i in range(n - 2 * r):
        s = sum(a * c for a, c in zip(samp[i:i + taps], coef)) & M32
        acc = (acc * 31 + s) & MASK
    return (acc * 31 + (n - 2 * r)) & MASK


def audit(name, blob, stride, expect_zero_ok=False):
    nwin = len(blob) // stride if stride else 0
    vals = [kern(blob, k * stride, stride) for k in range(nwin)]
    if not vals:
        return f"{name}: no whole window"
    if vals[0] == 0 and not expect_zero_ok:
        return (f"{name}: window 0 returns 0 -- the driver's Lemire index has "
                f"an absorbing state at acc == 0")
    return None


# ------------------------------------------------------------------ inputs --
def matrix(out):
    """The measured matrix. `small` and `large` are the two
    `collapse.probe_inputs` and must have DIFFERENT `work_per_call`."""
    rows = []

    # small: L1-resident. 96 windows of (n=72, r=4) -> taps 9, nout 64,
    # work/call = 576 taps, stride 89, blob 8544 B.
    blob = tiled(72, 4, 96, 40001)
    rows.append(("small.bin", blob, 89, 20000, b""))

    # large: past L2. 32768 windows of (n=136, r=8) -> taps 17, nout 120,
    # work/call = 2040 taps, stride 161, blob 5 275 648 B.
    # A DIFFERENT shape from `small` in both parameters, which is what
    # check.py's d(Ir)/d(work) assertion needs.
    blob = tiled(136, 8, 32768, 50021)
    rows.append(("large.bin", blob, 161, 2000, b""))

    # degenerate: three well-formed shapes the contract has to decide. Every
    # rung including R1 agrees on it, which is why it is not `adversarial-*`.
    #   r = 0     taps 1, a one-tap FIR: `windows(1)`
    #   n == taps exactly one output; the window does not slide
    #   n <  taps the window guard fires and the call returns 0
    # Padded to a common stride; the padding sits AFTER the samples, so
    # `last < len` strictly and both C rungs still agree.
    ws = [window(20, 0, 60011),          # taps 1, nout 20, len 8+1+20  = 29
          window(9, 4, 60013),           # taps 9, nout 1,  len 8+9+9   = 26
          window(4, 4, 60017)]           # taps 9, n < taps -> 0
    stride = max(len(w) for w in ws)
    blob = b"".join(w + bytes(stride - len(w)) for w in ws)
    rows.append(("degenerate.bin", blob, stride, 4000, b""))

    # ---- adversarial ----------------------------------------------------
    # ONE window each: `k` is pseudo-random, so with several windows the
    # malformed one would be hit only probabilistically.

    # fencepost: the window is ONE BYTE SHORT of the samples it declares, so
    # `last == len`. R1's `last > len` accepts; every other rung rejects. The
    # window is the whole blob, so the stolen byte is one past the C driver's
    # `bytes` malloc: ASan fires.
    w = window(40, 3, 70001, short=1)
    rows.append(("adversarial-fencepost.bin", w, len(w), 2000, b""))

    # fenceslack: the SAME window, plus three trailing payload bytes that do
    # not form a further window (`nwin` is still 1, `k` is still 0). The
    # identical off-by-one now reads a byte that is merely the wrong one:
    # ASan clean, UBSan clean, exit 0, wrong answer.
    rows.append(("adversarial-fenceslack.bin", w, len(w), 2000, b"\xa5\xa5\xa5"))

    # farover: `n` declared far beyond what the window holds. R1's `last > len`
    # rejects it just as loudly as R1h's `last >= len` -- an off-by-one buys
    # exactly one byte and nothing more -- so the two rungs AGREE here. The row
    # exists to say that, and it is a clean negative rather than a harm.
    w = bytearray(window(40, 3, 70003))
    w[0:4] = struct.pack("<I", 4000)
    rows.append(("adversarial-farover.bin", bytes(w), len(w), 2000, b""))

    # stride7: below the 8-byte header, so the driver's `stride_w >= 8` guard
    # skips the loop entirely and every rung prints 0 after ZERO kernel calls.
    w = window(40, 3, 70005)
    rows.append(("adversarial-stride7.bin", w, 7, 2000, b""))

    made = []
    for name, blob, stride, iters, trail in rows:
        p = os.path.join(out, name)
        emit(p, iters, blob, stride, trail)
        made.append((name, blob, stride, iters, trail))
    return made


def sweep(out):
    """The `sweep-*` bands. Appended LAST, and never renumbered: a `sweep-*`
    blob is dropped by both `check.py` and `measure.py`, so adding one costs a
    gate re-run and not a re-measure -- but only if the existing blobs stay
    byte-identical."""
    rows = []
    NOUT0, R0, NW = 32, 4, 4

    # band r: the TAP-COUNT axis. nout fixed, r 1..16.
    for r in range(1, 17):
        n = NOUT0 + 2 * r
        rows.append((f"sweep-r{r:02d}.bin", tiled(n, r, NW, 10000 + r),
                     8 + (2 * r + 1) + n))
    # band o: the OUTPUT-COUNT axis. r fixed, nout 8..192.
    for nout in (8, 16, 24, 32, 48, 64, 96, 128, 160, 192):
        n = nout + 2 * R0
        rows.append((f"sweep-o{nout:03d}.bin", tiled(n, R0, NW, 20000 + nout),
                     8 + (2 * R0 + 1) + n))
    # band e: EXTRAPOLATION. Both parameters outside the hull of r/o/h.
    for (nout, r) in ((160, 20), (192, 24), (256, 12), (224, 18)):
        n = nout + 2 * r
        rows.append((f"sweep-e{nout:03d}r{r:02d}.bin",
                     tiled(n, r, 2, 30000 + nout + r), 8 + (2 * r + 1) + n))
    # band h: LENGTH-HETEROGENEOUS WITHIN a blob. Windows of different (n, r)
    # padded to a common stride, so the blob's rows are not a scalar multiple
    # of any band above and dropping a band cannot leave the design full rank
    # by accident (`.memory/03-measurement.md`: the rank after the drop is the
    # test, not the column count).
    for tag, shapes in (
            ("h1", [(24, 2), (40, 6), (56, 3)]),
            ("h2", [(72, 8), (36, 1), (48, 5), (60, 7)]),
            ("h3", [(90, 10), (30, 4)])):
        ws = [window(n, r, 40000 + 13 * i + hash7(tag))
              for i, (n, r) in enumerate(shapes)]
        stride = max(len(w) for w in ws)
        blob = b"".join(w + bytes(stride - len(w)) for w in ws)
        rows.append((f"sweep-{tag}.bin", blob, stride))

    made = []
    for name, blob, stride in rows:
        p = os.path.join(out, name)
        emit(p, 2000, blob, stride)
        made.append((name, blob, stride, 2000, b""))
    return made


def hash7(s):
    """A tiny fixed string hash -- `hash()` is randomised per process and would
    make this generator non-deterministic across runs."""
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFF
    return h


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    made = matrix(a.out)
    if a.sweep:
        made += sweep(a.out)
    bad = []
    for name, blob, stride, iters, trail in made:
        # `adversarial-*` rows are allowed to have a window-0 result of 0 --
        # that is what a rejecting guard does, and it is the point of the row.
        z = name.startswith("adversarial")
        p = audit(name, blob + trail, stride, expect_zero_ok=z)
        if p:
            bad.append(p)
        nwin = len(blob + trail) // stride if stride else 0
        print(f"{name:32s} stride={stride:6d} nwin={nwin:6d} "
              f"n_iters={iters:6d} bytes={len(blob) + len(trail):9d}")
    for p in bad:
        print("AUDIT:", p, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
