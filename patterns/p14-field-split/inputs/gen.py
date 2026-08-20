#!/usr/bin/env python3
"""Generate p14's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p14-field-split/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p14-field-split/inputs/gen.py --sweep     # + the four sweep bands

Payload layout (../spec.md), p06's/p11's/p16's/p17's/p05's/p07's/p03's/p12's
verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nline  u32 LE     declared line count   ATTACKER DATA
    byte 4..     lines, each:  u32 LE llen ; llen bytes

and the kernel copies `m = min(llen, SCR)` bytes into a fixed `scr[SCR]`, splits
`scr[0..m)` on `DELIM` into fields, records one length per field in a fixed
`tl[MAXTOK]`, and folds count/lengths/content. The line R1 omits, and the only
thing it omits, is the FIELD-COUNT BOUND:

    R1   /* nothing */          tl[nt] = i - s; nt++; s = i + 1;
    R1h  if (nt == MAXTOK)      tl[nt] = i - s; nt++; s = i + 1;
             break;

--------------------------------------------------------------------------
THE BOUND IS A COUNT OF A BYTE VALUE, NOT A LENGTH
--------------------------------------------------------------------------
`nt` is one more than the number of `DELIM` bytes in `scr[0 .. m)`, so a 64-byte
line holds anywhere between 1 and 65 fields against a 16-entry table. Nothing in
the wire format declares that count and no length bounds it. Every read and
every write of `scr` is in bounds in R1; the out-of-bounds store is into the
METADATA table, and its magnitude is set by delimiter DENSITY -- up to 49
`size_t` stores, 392 bytes, past the end.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A LIBRARY-CONTRACT EXPERIMENT, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
`strtok(3)` COLLAPSES a run of delimiters into a single separator; this kernel's
partition (and Rust's `split`, and `strsep(3)`, and every CSV reader) does not.
The three overflow rows are chosen so that the difference is the experiment:

  `adversarial-run17`   one line, 16 ADJACENT delimiters. 17 fields here, and
                        **2** under `strtok`. The same bytes are a
                        stack-buffer-overflow WRITE under one library contract
                        and a correct parse under the other.
  `adversarial-alt33`   one line, 32 ALTERNATING delimiters (`a,a,a,...`). 33
                        fields under BOTH contracts -- there are no runs to
                        collapse. **Collapse changes WHICH inputs are dangerous;
                        it does not remove the need for the guard**, and this
                        row is what stops that overclaim.
  `adversarial-full65`  one line, 64 delimiters: 65 fields, 49 descriptors and
                        392 bytes past the table -- the largest overflow the
                        wire format can express, because `m <= SCR`.
  `adversarial-many`    eight lines, 20 delimiters each: the store repeats, so a
                        rung that survives one line has to survive eight.

--------------------------------------------------------------------------
p14 DOES NOT INHERIT `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
That section's threshold test decides it. p14's guard threshold is `MAXTOK`,
which IS the destination table's extent -- so "the guard fired" and "the
unguarded rung committed UB" would be the same event, p12's shape... **except
that the fired-guard case is not a checksum-agreeing row for a different reason
and the test is therefore not the binding constraint.** The two events do
coincide here: every input on which R1h truncates is an input on which R1 stores
past `tl`. So p14 sits with p12/p23/p25 and NOT with p06/p24, and the
consequence is the one that section states: **p14 cannot have an adversarial row
where the guard fires and the sanitizer is silent.** It is stated here rather
than left to be inferred, because p06's file states the opposite conclusion from
the same test and the two must not be confused.

--------------------------------------------------------------------------
WHY small AND large HAVE EVERY LINE UNDER MAXTOK FIELDS
--------------------------------------------------------------------------
`harness/check.py` requires every cell, R1 included, to print `model.py`'s
checksum on every non-adversarial MATRIX input. With at most `MAXTOK - 1`
delimiters per line the bound is never reached, so R1 and R1h compute the same
table and agree -- which is what makes the perf rows a measurement of the safety
line's PRICE rather than of two different kernels. (`degenerate` is also an
agreeing row, deliberately, and its fifth line sits at exactly `MAXTOK` fields:
the boundary from the safe side, p12's `adversarial-exact` analogue.)

--------------------------------------------------------------------------
small AND large: DIFFERENT RESIDUES, AND small IS LENGTH-HETEROGENEOUS
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues, and
`.memory/03-measurement.md`'s queue item 11 says a fit set must be
length-heterogeneous. p14's lines carry their own `llen`, so the natural place
is here:

  * `small`: 6 lines, `llen` 13/47/29/61/7/22 with 2/7/4/11/1/0 delimiters --
    six DIFFERENT lengths and six different field counts in one window, stride
    207;
  * `large`: 12 lines, `llen` 1..8, 0..2 delimiters, stride 104.

`_check_residues()` asserts that `nline`, the copied bytes, the stride and the
TOTAL FIELD COUNT differ mod 4, 8, 16 and 32 between the two, that the mean
`llen` straddles 16, that every line is under `MAXTOK` fields, and that `small`
really is heterogeneous.
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

HDR = 4                                   # nline:u32
LINE_HDR = 4                              # llen:u32
SCR = 64                                  # must equal every rung's SCR
MAXTOK = 16                               # must equal every rung's MAXTOK
DELIM = 0x2C                              # ','  -- every rung's DELIM

# The two measured shapes. `(llen, ndelim)` per line, fixed across the windows
# of a blob so that `work_per_call` is one scalar; only the DATA BYTES differ
# per window, which is what keeps the driver's anti-collapse barrier honest.
SMALL_LINES = ((13, 2), (47, 7), (29, 4), (61, 11), (7, 1), (22, 0))
SMALL_WINS = 64                              # 64 x 207 B = 13.0 KiB, inside L1
LARGE_LINES = ((3, 0), (5, 1), (1, 0), (7, 2), (2, 0), (6, 1),
               (4, 1), (8, 2), (3, 1), (5, 0), (1, 0), (7, 1))
LARGE_WINS = 50000                           # 50000 x 104 B = 5.0 MiB, past L2

SMALL_ITERS, LARGE_ITERS = 60000, 20000
ADV_ITERS = 8                             # R1 executes UB on four of them;
                                          # there is nothing to learn from doing
                                          # it 100 000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


def stride_of(lines):
    """4 header bytes + 4 per line + the line data bytes."""
    return HDR + sum(LINE_HDR + llen for llen, _ in lines)


def ntok_of(llen, ndel):
    """Fields the CHECKED kernel records for a line: `ndel + 1`, capped."""
    return min(ndel + 1, MAXTOK)


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    artefact, and every line of both must stay under `MAXTOK` fields. Returns a
    list of problems."""
    bad = []
    for label, lines in (("small", SMALL_LINES), ("large", LARGE_LINES)):
        for llen, ndel in lines:
            if ndel >= MAXTOK:
                bad.append(f"{label} has a line with {ndel} delimiters; R1 "
                           f"would store past tl[MAXTOK] and could not agree "
                           f"with the model -- see this file's header")
            if ndel > llen:
                bad.append(f"{label} line ({llen},{ndel}) cannot hold that many "
                           f"delimiters")
    sl = [llen for llen, _ in SMALL_LINES]
    ll = [llen for llen, _ in LARGE_LINES]
    if len(set(sl)) < len(sl):
        bad.append("small is not length-heterogeneous; its whole point is that "
                   "every line has a different llen (queue item 11)")
    sd = [ndel for _, ndel in SMALL_LINES]
    if len(set(sd)) < len(sd):
        bad.append("small's lines do not have distinct delimiter counts; the "
                   "per-FIELD term and the per-BYTE term would be collinear "
                   "inside one window")
    smean, lmean = sum(sl) / len(sl), sum(ll) / len(ll)
    if (smean < 16) == (lmean < 16):
        bad.append(f"small and large mean llen ({smean:.2f}, {lmean:.2f}) are "
                   f"on the same side of 16; the two inputs would measure the "
                   f"same shape of copy, scan and fold")
    pairs = [("nline", len(SMALL_LINES), len(LARGE_LINES)),
             ("copied bytes per call", sum(sl), sum(ll)),
             ("fields per call", sum(ntok_of(a, b) for a, b in SMALL_LINES),
              sum(ntok_of(a, b) for a, b in LARGE_LINES)),
             ("stride", stride_of(SMALL_LINES), stride_of(LARGE_LINES))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


# ---------------------------------------------------------------- content ----

def linebytes(rng, llen, ndel, spread="even"):
    """`llen` bytes holding exactly `ndel` delimiters and no NUL.

    `spread` picks where the delimiters go, which is the whole experiment on the
    adversarial rows:
      "even"  -- fields as equal as the arithmetic allows (the perf shape)
      "run"   -- all `ndel` delimiters ADJACENT, one field either side; this is
                 the shape `strtok` collapses to two fields and this kernel
                 splits into `ndel + 1`
      "alt"   -- delimiters alternating with single data bytes; NO runs, so
                 `strtok` and this kernel agree on the field count
      "all"   -- every byte a delimiter: `llen + 1` empty fields, the maximum
    """
    assert 0 <= ndel <= llen
    if spread == "all":
        assert ndel == llen
        return bytes([DELIM]) * llen
    if spread == "run":
        head = (llen - ndel + 1) // 2
        tail = llen - ndel - head
        return (bytes(rng.randrange(0x61, 0x7B) for _ in range(head))
                + bytes([DELIM]) * ndel
                + bytes(rng.randrange(0x61, 0x7B) for _ in range(tail)))
    if spread == "alt":
        out = bytearray()
        for i in range(llen):
            out.append(DELIM if (i % 2 == 1 and out.count(DELIM) < ndel)
                       else rng.randrange(0x61, 0x7B))
        assert out.count(DELIM) == ndel, (out.count(DELIM), ndel)
        return bytes(out)
    body = llen - ndel
    base, extra = divmod(body, ndel + 1)
    lens = [base + (1 if i < extra else 0) for i in range(ndel + 1)]
    out = bytearray()
    for i, L in enumerate(lens):
        if i:
            out.append(DELIM)
        out += bytes(rng.randrange(0x61, 0x7B) for _ in range(L))
    assert len(out) == llen and out.count(DELIM) == ndel
    return bytes(out)


def line(rng, llen_decl, ndel, ndata=None, spread="even"):
    """One line: the declared length, then the bytes.

    `llen_decl` is written verbatim and `ndata` defaults to it, so a row can
    declare a length the window does not hold."""
    n = llen_decl if ndata is None else ndata
    return struct.pack("<I", llen_decl) + linebytes(rng, n, ndel, spread)


def window(nline_decl, lines):
    """A window: the declared line count, then the lines.

    `nline_decl` is written verbatim rather than derived from `lines` so that a
    row can declare a count the window does not hold."""
    return struct.pack("<I", nline_decl) + b"".join(lines)


def tiled(rng, nwin, lines, spread="even"):
    """`nwin` windows, identical in *shape* and different in *content*."""
    out = bytearray()
    for _ in range(nwin):
        out += window(len(lines),
                      [line(rng, a, b, spread=spread) for a, b in lines])
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
    nline = int.from_bytes(win[:4], "little")
    if nline == 0:
        return 0
    acc, p = 0, HDR
    for _ in range(nline):
        if ln - p < LINE_HDR:
            break
        llen = int.from_bytes(win[p:p + 4], "little")
        p += LINE_HDR
        m = min(llen, SCR)
        if ln - p < llen:
            break
        scr = bytes(win[p:p + m])
        p += llen
        for fld in scr.split(bytes([DELIM]))[:MAXTOK]:
            acc = (acc * 31 + len(fld)) & MASK
            for b in fld:
                acc = (acc * 31 + b) & MASK
        acc = (acc * 31 + min(scr.count(DELIM) + 1, MAXTOK)) & MASK
    return (acc * 31 + nline) & MASK


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12, p06 and p14 check
    it, which is strictly stronger and costs one pass over the blob at
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


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
# Every line here is one every rung agrees on, R1 included, which is why the
# file is NOT named `adversarial-*` and the gate holds all eight cells to the
# model's checksum on it:
#
#   (0,  0)   llen == 0: `m == 0`, and the scan's `i == m` disjunct fires at
#             `i == 0`, so the line yields ONE field of length zero. A kernel
#             that yielded zero fields here would disagree with `bytes.split`,
#             with Rust's `split` and with `strsep`.
#   (1,  0)   one byte, no delimiter: one field, and the tail-append path with
#             nothing before it.
#   (5,  1)   with `spread="lead"`: a LEADING delimiter, so field 0 is empty and
#             `cur` steps over a delimiter at offset 0.
#   (5,  1)   with `spread="trail"`: a TRAILING delimiter, so the LAST field is
#             empty -- the case a `while i < m` scan silently drops.
#   (17, 15)  exactly `MAXTOK` fields: **the boundary from the safe side.** R1
#             fills the table exactly and stores nothing past it, so the two C
#             cells agree here and diverge at 16 delimiters.
#   (100, 3)  `llen > SCR`: `m = min(llen, SCR)` clamps the COPY in every rung
#             including R1, so the 36 undeclared bytes are skipped by the cursor
#             and never read. The clamp is not the safety line.
DEGENERATE_LINES = ((0, 0, "even"), (1, 0, "even"), (5, 1, "lead"),
                    (5, 1, "trail"), (17, 15, "run"), (100, 3, "even"))

# ---- adversarial-stride3: a window too small for the header -----------------
#
# The driver guard is `stride_w >= 4`; a 3-byte window cannot hold `nline`. The
# guard skips the loop entirely, so every rung prints 0 after ZERO kernel calls.
STRIDE3_BLOB = 30

# `--sweep`: four bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure). Appended LAST so the eight matrix blobs
# stay byte-identical when a band is added.
#
# Band M -- the BYTE axis. `nline` 8, fields 4 per line, `llen` swept 4..60.
SWEEP_M_NLINE, SWEEP_M_NDEL = 8, 3
SWEEP_M_LLENS = tuple(range(4, 61, 2))
# Band T -- the FIELD axis, and the one that is new here: `llen` held at 60 and
#           the delimiter count swept 0..15, so the TOTAL BYTES FOLDED IS FIXED
#           and only the number of fields moves. That is the amortisation
#           denominator swept on its own -- see ../NOTES.md 9.
SWEEP_T_NLINE, SWEEP_T_LLEN = 8, 60
SWEEP_T_NDELS = tuple(range(0, 16))
# Band L -- the LINE axis. `llen` 32, 3 delimiters, `nline` swept 1..16.
SWEEP_L_LLEN, SWEEP_L_NDEL = 32, 3
SWEEP_L_NLINES = tuple(range(1, 17))
# Band X -- p04's band X: every regressor non-zero at once and length- AND
#           field-heterogeneous WITHIN a window, so the pooled design has full
#           rank, plus a WITHIN-BAND NEGATIVE CONTROL (`x08b`) whose regressors
#           are identical to `x08a`'s and whose bytes differ, for which the
#           predicted delta is exactly 0.
SWEEP_X_SHAPES = {
    "x04": ((5, 1), (12, 7), (33, 0), (64, 15)),
    "x06": ((1, 0), (7, 3), (18, 12), (40, 8), (57, 2), (64, 1)),
    "x08a": ((2, 1), (9, 4), (16, 15), (23, 0), (31, 9), (44, 6), (52, 3),
             (61, 12)),
    "x08b": ((2, 1), (9, 4), (16, 15), (23, 0), (31, 9), (44, 6), (52, 3),
             (61, 12)),
    "x11": ((3, 2), (6, 1), (10, 9), (14, 0), (19, 13), (25, 6), (30, 4),
            (37, 11), (43, 3), (50, 8), (64, 15)),
}
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def degenerate_window(rng):
    """`degenerate.bin`'s single window: six lines, all agreeing."""
    out = []
    for llen, ndel, spread in DEGENERATE_LINES:
        if spread == "lead":
            body = bytes([DELIM]) + bytes(rng.randrange(0x61, 0x7B)
                                          for _ in range(llen - 1))
            out.append(struct.pack("<I", llen) + body)
        elif spread == "trail":
            body = bytes(rng.randrange(0x61, 0x7B)
                         for _ in range(llen - 1)) + bytes([DELIM])
            out.append(struct.pack("<I", llen) + body)
        else:
            out.append(line(rng, llen, ndel, spread=spread))
    return window(len(DEGENERATE_LINES), out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p14 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    sl = [llen for llen, _ in SMALL_LINES]
    ll = [llen for llen, _ in LARGE_LINES]
    print(f"  residues ok: nline {len(SMALL_LINES)}/{len(LARGE_LINES)}, copied "
          f"bytes {sum(sl)}/{sum(ll)}, fields "
          f"{sum(ntok_of(x, y) for x, y in SMALL_LINES)}/"
          f"{sum(ntok_of(x, y) for x, y in LARGE_LINES)}, strides "
          f"{stride_of(SMALL_LINES)}/{stride_of(LARGE_LINES)}, mean llen "
          f"{sum(sl)/len(sl):.2f}/{sum(ll)/len(ll):.2f}, llen "
          f"{min(sl)}..{max(sl)}/{min(ll)}..{max(ll)}, distinct llen "
          f"{len(set(sl))}/{len(set(ll))}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_LINES),
          tiled(rng, SMALL_WINS, SMALL_LINES))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_LINES),
          tiled(rng, LARGE_WINS, LARGE_LINES))

    # ---- adversarial ------------------------------------------------------
    # run17: ONE line, 16 ADJACENT delimiters -> 17 fields here, 2 under strtok.
    run17 = [line(rng, 18, 16, spread="run")]
    write("adversarial-run17.bin", ADV_ITERS, HDR + LINE_HDR + 18,
          window(1, run17))
    # alt33: ONE line, 32 ALTERNATING delimiters -> 33 fields under BOTH
    # contracts. `llen` 65 also exercises the clamp: `m = 64`.
    alt33 = [line(rng, 65, 32, spread="alt")]
    write("adversarial-alt33.bin", ADV_ITERS, HDR + LINE_HDR + 65,
          window(1, alt33))
    # full65: ONE line, every byte a delimiter -> 65 fields, 49 past the table.
    full65 = [line(rng, 64, 64, spread="all")]
    write("adversarial-full65.bin", ADV_ITERS, HDR + LINE_HDR + 64,
          window(1, full65))
    # many: EIGHT lines, 20 delimiters each -> the store repeats eight times.
    many = [line(rng, 22, 20, spread="run") for _ in range(8)]
    write("adversarial-many.bin", ADV_ITERS, HDR + 8 * (LINE_HDR + 22),
          window(8, many))

    write("degenerate.bin", ADV_ITERS,
          stride_of([(a, b) for a, b, _ in DEGENERATE_LINES]),
          degenerate_window(rng))

    # stride 3: a window too small to hold the 4-byte header. The driver guard
    # skips the loop, so every rung prints 0 after ZERO kernel calls.
    write("adversarial-stride3.bin", ADV_ITERS, 3, rng.randbytes(STRIDE3_BLOB),
          check_zero=False)

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for llen in SWEEP_M_LLENS:
            nd = min(SWEEP_M_NDEL, llen)
            lines = tuple((llen, nd) for _ in range(SWEEP_M_NLINE))
            write(f"sweep-m{llen:02d}t{nd + 1:02d}.bin", SWEEP_ITERS,
                  stride_of(lines), tiled(rng, SWEEP_WINS, lines))
        for nd in SWEEP_T_NDELS:
            lines = tuple((SWEEP_T_LLEN, nd) for _ in range(SWEEP_T_NLINE))
            write(f"sweep-t{nd + 1:02d}m{SWEEP_T_LLEN:02d}.bin", SWEEP_ITERS,
                  stride_of(lines), tiled(rng, SWEEP_WINS, lines))
        for k in SWEEP_L_NLINES:
            lines = tuple((SWEEP_L_LLEN, SWEEP_L_NDEL) for _ in range(k))
            write(f"sweep-l{k:02d}m{SWEEP_L_LLEN:02d}.bin", SWEEP_ITERS,
                  stride_of(lines), tiled(rng, SWEEP_WINS, lines))
        for tag, lines in SWEEP_X_SHAPES.items():
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(lines),
                  tiled(rng, SWEEP_WINS, lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
