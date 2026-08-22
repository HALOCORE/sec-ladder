#!/usr/bin/env python3
"""p38-alias-pun input generator. Deterministic; the gate hashes THIS FILE and
never the blobs, so the determinism is the whole basis of the claim that the
committed `.bin` files are reproducible. Regenerate twice and diff.

File format (`.memory/02-bench-rules.md`): `u64 n_iters`, `u64 payload_len`,
payload. p38's payload is p47's, p10's and eight others':

    word 0     u64  stride      # bytes per window
    byte 8..   u8[] blob        # the windows

Window layout (../spec.md):

    byte 0..4   nrec  u32 LE    DECLARED record count      ATTACKER DATA
    byte 4..    the record stream, as 16-bit little-endian words

    record at word index i:
      words i, i+1   rlen, a u32 stored as two 16-bit halves, low half first.
                     **rlen counts 32-bit units**, so the payload is 2*rlen
                     words and every record header stays 4-byte aligned.
      words i+2 ..   2*rlen payload words

**A well-formed record has `rlen <= room`, so the clamp never fires and every
cell agrees.** The `adversarial-*` blobs are the ones that declare more, and
they are the only inputs on which any rung can diverge -- p02's and p14's shape.

`--sweep` appends the `sweep-*` band. The prefix is the whole mechanism
(`check.py:459-460`, `measure.py:60`): `sweep-*` blobs are diagnostic, are not
part of the measured matrix, and a band named otherwise would enter it.

**Two structural parameters vary INDEPENDENTLY in the sweep** -- `nrec`
(records per window) and `rlen` (32-bit units per record) -- which is what
makes additivity extrapolation available, the only out-of-sample test this
project has that can fail (`.memory/03-measurement.md`).
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HDR = 4                # nrec:u32
SCRATCH_W = 256        # must equal SLB_P38_SCRATCH_W and every rung's const
MASK = (1 << 64) - 1


# ------------------------------------------------------------------ build ----
def payload_words(rlen, seed):
    """2*rlen payload words, none of them zero, deterministic in `seed`."""
    return [(0x1000 + ((seed * 37 + 11 * t) & 0x7FFF)) | 1 for t in range(2 * rlen)]


def record(rlen, seed, declared=None):
    """One record. `declared` overrides the length field written to the wire --
    that is the ONLY thing an adversarial blob changes."""
    d = rlen if declared is None else declared
    b = struct.pack("<HH", d & 0xFFFF, (d >> 16) & 0xFFFF)
    for w in payload_words(rlen, seed):
        b += struct.pack("<H", w & 0xFFFF)
    return b


def window(nrec, recs, stride):
    """`stride` bytes: the header, the records, zero padding."""
    b = struct.pack("<I", nrec)
    for r in recs:
        b += r
    if len(b) > stride:
        raise SystemExit(f"gen.py: window of {len(b)} bytes exceeds stride {stride}")
    return b + b"\x00" * (stride - len(b))


def uniform(nrec, rlen, stride, seed0=0):
    """A window-homogeneous window: `nrec` records, each declaring `rlen`."""
    return window(nrec, [record(rlen, seed0 + t) for t in range(nrec)], stride)


def stride_for(nrec, rlen):
    """The smallest stride that holds `nrec` records of `rlen` 32-bit units."""
    return HDR + nrec * (4 + 4 * rlen)


def emit(path, n_iters, blob, stride):
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload)))
        f.write(payload)


# ------------------------------------------------------------------ audit ----
def sim(blob, off, stride):
    """The kernel's DEFINED semantics, re-implemented here so the generator can
    assert what it is shipping. Independent of model.py on purpose: a generator
    that imported the model could not catch a model bug."""
    if stride < HDR:
        return 0, 0
    nrec = int.from_bytes(blob[off:off + 4], "little")
    if nrec == 0:
        return 0, 0
    nw = min((stride - HDR) // 2, SCRATCH_W)
    sc = [blob[off + HDR + 2 * j] | (blob[off + HDR + 2 * j + 1] << 8)
          for j in range(nw)]
    acc, i, o, nclamp = 0, 0, 0, 0
    while o < nrec and i + 2 <= nw:
        room = (nw - i - 2) // 2
        if sc[i] | (sc[i + 1] << 16) > room:
            sc[i], sc[i + 1] = room & 0xFFFF, (room >> 16) & 0xFFFF
            nclamp += 1
        n = sc[i] | (sc[i + 1] << 16)
        for k in range(2 * n):
            acc = (acc * 31 + sc[i + 2 + k]) & MASK
        i = i + 2 + 2 * n
        o = o + 1
    return (acc * 31 + o) & MASK, nclamp


def audit(name, blob, stride, expect_zero_ok=False):
    """What must hold of every shipped blob."""
    if stride < 8:
        return None if name.startswith("adversarial") else \
            f"{name}: stride {stride} < 8 and it is not an adversarial row"
    nwin = len(blob) // stride
    if nwin == 0:
        return f"{name}: no whole window"
    if len(blob) % stride:
        return f"{name}: blob {len(blob)} is not a multiple of stride {stride}"
    r0, _ = sim(blob, 0, stride)
    # `.memory/01-ladder.md`: window 0 returning 0 is an ABSORBING STATE --
    # `acc` stays 0, the Lemire index stays 0, and every later call re-runs
    # window 0. A blob whose first window folds to 0 measures one window.
    if r0 == 0 and not expect_zero_ok:
        return f"{name}: window 0 folds to 0 (absorbing state)"
    return None


def clamps(blob, stride):
    n = 0
    for w in range(len(blob) // stride):
        n += sim(blob, w * stride, stride)[1]
    return n


# ----------------------------------------------------------------- matrix ----
def matrix(out):
    rows = []

    # ---- small: stride 200 -> nw = 98 words; 4 records of 11 u32-units
    #      (footprint 24 words each, 96 of 98 used).
    S_STRIDE, S_NREC, S_RLEN = 200, 4, 11
    small = b"".join(uniform(S_NREC, S_RLEN, S_STRIDE, seed0=7 * w)
                     for w in range(40))
    rows.append(("small.bin", small, S_STRIDE, 20000))

    # ---- large: stride 516 -> nw = 256 words, EXACTLY the scratch, so the
    #      truncation branch is on the boundary rather than untested. 8 records
    #      of 15 u32-units: footprint 32 words each, 256 of 256 used.
    L_STRIDE, L_NREC, L_RLEN = 516, 8, 15
    large = b"".join(uniform(L_NREC, L_RLEN, L_STRIDE, seed0=13 * w)
                     for w in range(40))
    rows.append(("large.bin", large, L_STRIDE, 20000))

    # ---- degenerate: windows that exercise every early exit, plus one that
    #      does real work first so the blob is not absorbing.
    d = [uniform(2, 5, 200, seed0=3)]                 # window 0: real work
    d.append(window(0, [], 200))                      # nrec == 0
    d.append(window(3, [record(0, 1)], 200))          # a zero-length record
    d.append(window(9, [record(4, 2)], 200))          # nrec > records present
    degen = b"".join(d)
    rows.append(("degenerate.bin", degen, 200, 4000))

    # ---- adversarial-stale: the declared length overruns the record stream
    #      but stays INSIDE the 256-word scratch. Under gcc -O3 the fold then
    #      reads scratch words the decode loop never wrote -- a disclosure of
    #      whatever the previous call left there, ASan- and UBSan-clean.
    #      room here is (98-2)/2 = 48; 60 u32-units is 120 words from word 2.
    stale = window(1, [record(3, 5, declared=60)], 200)
    rows.append(("adversarial-stale.bin", stale, 200, 1))

    # ---- adversarial-oob: the declared length leaves the scratch ARRAY.
    #      2*rlen must exceed SCRATCH_W - 2 = 254, so rlen >= 128; 200 puts the
    #      last read 146 words past the end. ASan: stack-buffer-overflow READ.
    oob = window(1, [record(3, 6, declared=200)], 200)
    rows.append(("adversarial-oob.bin", oob, 200, 1))

    # ---- adversarial-huge: the largest length the field can carry. The read
    #      walks off the stack entirely.
    huge = window(1, [record(3, 8, declared=0xFFFFFFF)], 200)
    rows.append(("adversarial-huge.bin", huge, 200, 1))

    # ---- adversarial-nrec: nrec saturated, so only the `i + 2 <= nw` guard
    #      stops the walk. Every record is well formed.
    nr = window(0xFFFFFFFF, [record(11, 9 + t) for t in range(4)], 200)
    rows.append(("adversarial-nrec.bin", nr, 200, 200))

    # ---- adversarial-stride7: below the driver's `stride_w >= 8`; every rung
    #      skips the loop and prints 0.
    rows.append(("adversarial-stride7.bin", b"\x01\x00\x00\x00\x00\x00\x00", 7, 100))

    made = []
    for name, blob, stride, iters in rows:
        emit(os.path.join(out, name), iters, blob, stride)
        made.append((name, blob, stride, iters))
    return made


# ------------------------------------------------------------------ sweep ----
def sweep(out):
    """Two bands, each varying ONE structural parameter with the other held
    fixed, plus a heterogeneous band. `sweep-*` blobs never enter the matrix."""
    rows = []
    # band r: records per window, rlen fixed at 4 (footprint 10 words each).
    for nrec in (1, 2, 3, 4, 6, 8, 12, 16, 20, 24):
        st = stride_for(24, 4)
        rows.append((f"sweep-r{nrec:02d}.bin", b"".join(
            uniform(nrec, 4, st, seed0=5 * w) for w in range(6)), st))
    # band w: 32-bit units per record, nrec fixed at 2.
    for rlen in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 60):
        st = stride_for(2, 60)
        rows.append((f"sweep-w{rlen:02d}.bin", b"".join(
            uniform(2, rlen, st, seed0=9 * w) for w in range(6)), st))
    # band x: the additivity test set -- pairs neither band contains.
    for nrec, rlen in ((3, 7), (5, 9), (7, 5), (9, 3), (11, 10), (14, 6)):
        st = stride_for(14, 10)
        rows.append((f"sweep-x{nrec:02d}u{rlen:02d}.bin", b"".join(
            uniform(nrec, rlen, st, seed0=17 * w) for w in range(6)), st))
    # band h: length-HETEROGENEOUS within a blob, so a row is not a scalar
    # multiple of any band above.
    for tag, shapes in (("h1", [(2, 8), (4, 3), (1, 20)]),
                        ("h2", [(6, 2), (2, 14)]),
                        ("h3", [(3, 11), (8, 1), (5, 5)])):
        st = max(stride_for(n, r) for n, r in shapes)
        rows.append((f"sweep-{tag}.bin",
                     b"".join(uniform(n, r, st, seed0=23 * t)
                              for t, (n, r) in enumerate(shapes)), st))

    made = []
    for name, blob, stride in rows:
        emit(os.path.join(out, name), 2000, blob, stride)
        made.append((name, blob, stride, 2000))
    return made


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
    for name, blob, stride, iters in made:
        z = name.startswith("adversarial")
        p = audit(name, blob, stride, expect_zero_ok=z)
        if p:
            bad.append(p)
        nwin = len(blob) // stride if stride else 0
        nc = clamps(blob, stride) if stride >= 8 and nwin else 0
        r0 = sim(blob, 0, stride)[0] if stride >= 8 and nwin else 0
        print(f"{name:30s} stride={stride:5d} nwin={nwin:4d} n_iters={iters:6d} "
              f"bytes={len(blob):8d} clamped={nc:3d} win0={r0}")
    for p in bad:
        print("AUDIT:", p, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
