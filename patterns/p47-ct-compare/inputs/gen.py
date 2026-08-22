#!/usr/bin/env python3
"""p47-ct-compare input generator. Deterministic: no `random` module anywhere,
every byte comes from a fixed LCG seeded per window, so regenerating twice
gives byte-identical files. `harness/check.py` hashes THIS FILE and never the
blobs (`.memory/05-layout.md`), so that determinism is the entire basis of
every swept law p47 publishes -- verify it with

    python3 patterns/p47-ct-compare/inputs/gen.py --sweep
    sha256sum patterns/p47-ct-compare/inputs/*.bin > .temp/p47/a
    python3 patterns/p47-ct-compare/inputs/gen.py --sweep
    sha256sum -c .temp/p47/a

Usage:

    python3 patterns/p47-ct-compare/inputs/gen.py            # the matrix inputs
    python3 patterns/p47-ct-compare/inputs/gen.py --sweep    # + the sweep bands

File format: `.memory/02-bench-rules.md`. Payload is `u64 stride` then the
window blob, decoded by `slb.head1_u64_bytes`.

Window layout (../spec.md):

    byte 0..4     ntag  u32 LE   DECLARED comparison count
    byte 4..8     tlen  u32 LE   DECLARED tag length
    byte 8..      ntag records of 2*tlen bytes: secret[tlen] then cand[tlen]

**THE FILE, AND NOT THE KERNEL, DECIDES `k`.** The first-mismatch position of
comparison `t` is a property of the bytes this generator writes, exactly as
sortedness is a property of p07's file. No rung computes `k` and no rung is
told it.

**THE CHECKSUM CANNOT SEE `k`.** ../spec.md's fold folds the VERDICT
(`MATCH`/`MISS`) and never a tag byte, so two blobs with the same verdict
sequence and the same `(ntag, tlen, stride, n_iters)` print the *same
checksum on every cell* while differing in `k`. That is what makes the
adversarial pair below a timing row rather than a correctness row, and it is
the whole design: `adversarial-k000` and `adversarial-klast` are the same
program state and a different instruction count.

**Sweep bands.** `sweep-*` blobs are diagnostic: `check.py` and `measure.py`
both drop them, so appending a band costs a gate re-run and NOT a re-measure.
Bands are appended LAST for that reason.

    k<NNN>     the FIRST-MISMATCH axis. tlen fixed, nmatch = 0, k = 0..248
    m<NN>      the VERDICT-MIX axis.    tlen fixed, k = 0, nmatch = 0..ntag
    t<NNN>     the TAG-LENGTH axis.     k = 0, nmatch = 0
    g<NN>      the COMPARISON-COUNT axis. tlen fixed, k = 0, nmatch = 0
    x<..>      ADDITIVITY EXTRAPOLATION: k > 0 **and** nmatch > 0 together,
               which no band above contains -- so an `x` row is outside the
               row space of the fit set by construction and a linear
               combination of fitted rows cannot reach it
               (`.memory/03-measurement.md`).
    h<N>       LENGTH-HETEROGENEOUS: windows of DIFFERENT (ntag, tlen, k) in
               one blob, padded to a common stride, so no band is a scalar
               multiple of another.
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
HDR = 8
MATCH = 7
MISS = 251


# ------------------------------------------------------------------- bytes --
def lcg(seed):
    """A fixed 31-bit LCG. Deliberately NOT `random`: `.memory/05-layout.md`
    records that `random.shuffle`'s rejection sampling makes stream
    consumption data-dependent, so two blobs can re-converge and an edit to
    one band can silently move another. One generator per window, seeded from
    that window's own parameters, so no blob's bytes depend on any other."""
    x = seed & 0x7FFFFFFF
    while True:
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        yield (x >> 16) & 0xFF


def window(ntag, tlen, seed, k=0, nmatch=0, short=0):
    """One window.

    `nmatch` of the `ntag` comparisons are made EQUAL (the candidate is a copy
    of the secret, so the compare scans all `tlen` bytes and the verdict is
    MATCH). The remaining `ntag - nmatch` differ first at byte `k`: bytes
    `0..k` are copied and byte `k` is flipped, so the FIRST MISMATCH IS AT
    EXACTLY `k` and nothing before it differs. Bytes after `k` are drawn
    independently, so a rung that kept scanning past the first difference
    cannot get the same answer by luck.

    The equal comparisons come FIRST, so `nmatch` and `k` are independent:
    changing one does not move where the other's bytes sit.

    `short` removes trailing bytes, which is how the window-too-short row is
    built."""
    g = lcg(seed)
    b = bytearray(struct.pack("<II", ntag, tlen))
    for t in range(ntag):
        sec = bytes(next(g) for _ in range(tlen))
        if t < nmatch:
            cand = sec
        else:
            kk = k if k < tlen else tlen - 1
            cand = bytearray(sec)
            cand[kk] ^= 0x5A          # a multi-bit flip: 4 bits differ
            for i in range(kk + 1, tlen):
                cand[i] = next(g)
            cand = bytes(cand)
        b += sec
        b += cand
    if short:
        del b[len(b) - short:]
    return bytes(b)


def tiled(ntag, tlen, nwin, seed0, k=0, nmatch=0):
    """`nwin` windows of the SAME shape, so every window has the same
    `work_per_call`, the same `k` and the same verdict sequence -- which is
    what makes a swept law exact: whichever window the driver's Lemire index
    picks, the kernel does the same work. Each window gets its own LCG seed,
    so the blob is not a repeated pattern the optimiser could exploit."""
    return b"".join(window(ntag, tlen, seed0 + 7919 * w, k, nmatch)
                    for w in range(nwin))


def emit(path, n_iters, blob, stride, trailing=b""):
    slb.write(path, n_iters, slb.pack_head1_bytes(stride, blob + trailing))
    return stride


# ------------------------------------------------ the checked kernel, again --
# A third implementation of the kernel (model.py has two), used ONLY to check
# the generated files before they are written: p17's trap is that a window
# returning 0 pins `acc` at 0 and the driver's Lemire index k = (acc*nwin)>>64
# then has an absorbing state at 0, so window 0 must serve something.
def kern(blob, off, ln):
    if ln < HDR:
        return 0
    ntag = int.from_bytes(blob[off:off + 4], "little")
    tlen = int.from_bytes(blob[off + 4:off + 8], "little")
    if ntag == 0 or tlen == 0:
        return 0
    acc, p, o = 0, HDR, 0
    while o < ntag and ln - p >= 2 * tlen:
        a = blob[off + p:off + p + tlen]
        b = blob[off + p + tlen:off + p + 2 * tlen]
        acc = (acc * 31 + (MATCH if a == b else MISS)) & MASK
        p += 2 * tlen
        o += 1
    return (acc * 31 + o) & MASK


def first_mismatch(blob, off, ln):
    """The `k` of every comparison in this window, for the audit -- and it is
    the quantity the whole pattern is about, so the generator computes it and
    prints it rather than asserting it."""
    ntag = int.from_bytes(blob[off:off + 4], "little")
    tlen = int.from_bytes(blob[off + 4:off + 8], "little")
    ks, p, o = [], HDR, 0
    while o < ntag and ln - p >= 2 * tlen:
        a = blob[off + p:off + p + tlen]
        b = blob[off + p + tlen:off + p + 2 * tlen]
        ks.append(next((i for i in range(tlen) if a[i] != b[i]), None))
        p += 2 * tlen
        o += 1
    return ks


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

    # small: L1-resident. 96 windows of (ntag=4, tlen=24), every comparison
    # mismatching at k = 5.  stride = 8 + 4*48 = 200, blob 19 200 B.
    blob = tiled(4, 24, 96, 40001, k=5, nmatch=0)
    rows.append(("small.bin", blob, 200, 20000, b""))

    # large: past L2. 8192 windows of (ntag=8, tlen=64), mismatching at k=37,
    # two of the eight EQUAL so the row exercises both verdicts.
    # stride = 8 + 8*128 = 1032, blob 8 454 144 B.
    blob = tiled(8, 64, 8192, 50021, k=37, nmatch=2)
    rows.append(("large.bin", blob, 1032, 1500, b""))

    # degenerate: three well-formed shapes the contract has to decide, padded
    # to a common stride. Every rung agrees on it, which is why it is not
    # `adversarial-*`.
    #   tlen = 1        a one-byte tag: the compare loop runs once
    #   ntag = 1        one comparison, and it is EQUAL (full scan)
    #   ntag declared 6 but the window holds 2: the guard breaks the walk
    ws = [window(3, 1, 60011, k=0, nmatch=1),
          window(1, 40, 60013, k=0, nmatch=1),
          window(6, 12, 60017, k=3, nmatch=0)[:8 + 2 * 24]]
    stride = max(len(w) for w in ws)
    blob = b"".join(w + bytes(stride - len(w)) for w in ws)
    rows.append(("degenerate.bin", blob, stride, 4000, b""))

    # ---- adversarial ----------------------------------------------------
    # ONE window each: `k` is pseudo-random, so with several windows a
    # particular window would be hit only probabilistically.
    #
    # THE PAIR. Same seed, same (ntag, tlen, nmatch, stride, n_iters), same
    # verdict sequence -- so the two files print the SAME CHECKSUM on all
    # eight cells -- and different first-mismatch positions. What separates
    # them is instruction count and nothing else. This is p47's harm row and
    # `.temp/p47/NOTES.md` (c) argues why an adversarial row has to look like
    # this for a timing pattern.
    NT, TL = 8, 128
    w0 = window(NT, TL, 70001, k=0, nmatch=0)
    wl = window(NT, TL, 70001, k=TL - 1, nmatch=0)
    assert len(w0) == len(wl)
    rows.append(("adversarial-k000.bin", w0, len(w0), 3000, b""))
    rows.append(("adversarial-klast.bin", wl, len(wl), 3000, b""))

    # The third member of the family: every comparison EQUAL, so every rung
    # scans the whole tag and the leaking rungs pay their maximum. Different
    # verdicts, so this one's checksum differs -- it is the "no mismatch at
    # all" end of the `k` axis and it is why the sweep needs a k = "none"
    # point that is not a value of k.
    rows.append(("adversarial-equal.bin",
                 window(NT, TL, 70001, k=0, nmatch=NT), 8 + NT * 2 * TL,
                 3000, b""))

    # stride7: below the 8-byte header, so the driver's `stride_w >= 8` guard
    # skips the loop entirely and every rung prints 0 after ZERO kernel calls.
    rows.append(("adversarial-stride7.bin", window(2, 8, 70005), 7, 2000, b""))

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
    NT0, TL0, NW = 4, 256, 4

    # band k: THE FIRST-MISMATCH AXIS, and the whole pattern. tlen 256, every
    # comparison mismatching, k stepped over the full tag INCLUDING 0 and
    # including both sides of every 16/32/64-byte block boundary a vector
    # `bcmp` might use.
    for k in (0, 1, 2, 3, 7, 8, 15, 16, 17, 24, 31, 32, 33, 47, 48, 63, 64,
              65, 79, 80, 95, 96, 111, 112, 127, 128, 129, 159, 160, 191,
              192, 223, 224, 248, 255):
        rows.append((f"sweep-k{k:03d}.bin",
                     tiled(NT0, TL0, NW, 11000 + k, k=k, nmatch=0),
                     HDR + NT0 * 2 * TL0))
    # band m: THE VERDICT-MIX AXIS. k = 0, nmatch 0..8 of ntag = 8.
    for nm in range(0, 9):
        rows.append((f"sweep-m{nm:02d}.bin",
                     tiled(8, TL0, NW, 21000 + nm, k=0, nmatch=nm),
                     HDR + 8 * 2 * TL0))
    # band t: THE TAG-LENGTH AXIS. k = 0, nmatch = 0.
    for tl in (1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384):
        rows.append((f"sweep-t{tl:03d}.bin",
                     tiled(NT0, tl, NW, 31000 + tl, k=0, nmatch=0),
                     HDR + NT0 * 2 * tl))
    # band g: THE COMPARISON-COUNT AXIS. tlen fixed, ntag stepped.
    for ng in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32):
        rows.append((f"sweep-g{ng:02d}.bin",
                     tiled(ng, 64, NW, 41000 + ng, k=0, nmatch=0),
                     HDR + ng * 2 * 64))
    # band x: ADDITIVITY EXTRAPOLATION. `k > 0` AND `nmatch > 0` together,
    # which NO band above contains: k varies only at nmatch = 0 and nmatch
    # varies only at k = 0. A linear combination of fitted rows cannot reach
    # these, so this band CAN fail -- which is the point.
    for (k, nm) in ((64, 3), (128, 5), (32, 6), (192, 2), (17, 7)):
        rows.append((f"sweep-x{k:03d}m{nm:d}.bin",
                     tiled(8, TL0, 2, 51000 + k + nm, k=k, nmatch=nm),
                     HDR + 8 * 2 * TL0))
    # band h: LENGTH-HETEROGENEOUS WITHIN a blob -- windows of different
    # (ntag, tlen, k, nmatch) padded to a common stride, so a blob's regressor
    # row is not a scalar multiple of any band above.
    for tag, shapes in (
            ("h1", [(2, 32, 5, 0), (4, 16, 0, 2), (3, 48, 20, 1)]),
            ("h2", [(6, 24, 11, 3), (2, 96, 40, 0)]),
            ("h3", [(8, 8, 2, 4), (1, 200, 100, 0), (5, 40, 0, 5)])):
        ws = [window(ng, tl, 61000 + 13 * i + hash7(tag), k=k, nmatch=nm)
              for i, (ng, tl, k, nm) in enumerate(shapes)]
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
    """A tiny fixed string hash -- `hash()` is randomised per process and
    would make this generator non-deterministic across runs."""
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFF
    return h


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
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
        z = name.startswith("adversarial")
        p = audit(name, blob + trail, stride, expect_zero_ok=z)
        if p:
            bad.append(p)
        full = blob + trail
        nwin = len(full) // stride if stride else 0
        ks = first_mismatch(full, 0, stride) if nwin else []
        print(f"{name:32s} stride={stride:6d} nwin={nwin:6d} "
              f"n_iters={iters:6d} bytes={len(full):9d} k(win0)={ks}")
    for p in bad:
        print("AUDIT:", p, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
