#!/usr/bin/env python3
"""Generate ph03's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph03-uudecode-bound/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel uudecodes one window
    byte 8..   u8[] blob       uuencoded text; n_blob = payload_len - 8

A *window* is a complete uuencoded document: `K` full lines followed by the
terminator line. One line is

    PHP_UU_ENC(45)  +  60 encoded characters  +  '\\n'          = 62 bytes

and the terminator is `PHP_UU_ENC(0) + '\\n'` = 2 bytes, so a K-line document is
`62*K + 2` bytes and decodes to `45*K`. Nothing is a compile-time constant:
`n_iters`, `stride`, `n_blob` and every length byte come from the file, and the
length byte is the datum the whole pattern is about (`ee` at `uuencode.c:141` is
computed from it).

Three things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 498 and 4032 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all; and the
    safe-vs-unsafe delta varies with the residue of the measured length
    (`.memory/01-ladder.md`). `_check_residues()` asserts both, so an edit that
    quietly puts the pair in one class fails loudly. ⚠ A line is 62 bytes, so
    `62*K + 2` is `2 (mod 4)` for even K and `0 (mod 4)` for odd K -- K = 8 and
    K = 65 is the cheapest pair that separates them.
  * **the strides are not powers of two** (498 = 2*3*83, 4032 = 2^6*63), so
    consecutive windows do not share a cache-set alignment, and no window
    boundary is 8-byte aligned in a way a rung could exploit.
  * **documents tile each window exactly**, so every call decodes the same
    number of lines and `work_per_call = stride` is a slight over-estimate of
    the bytes actually touched (the '\\n' of each line is skipped, and the
    terminator's is never read). An over-estimate raises the derived `Ir` floor,
    which is the direction a floor should err.

⚠⚠ **THE FOUR ADVERSARIAL FILES ARE THE ROW.** Read the comments on each: two
of them differ *only* in 60 bytes of slack after the window, and that difference
decides whether the oracle sees the over-READ or the over-WRITE. NOTES.md §4.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common-php"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

LINE_LEN = 45                      # bytes of plaintext per uuencoded line
ENC_LINE = 1 + 60 + 1              # length byte + 60 characters + '\n' == 62
TERM = 2                           # PHP_UU_ENC(0) + '\n'

SMALL_LINES, LARGE_LINES = 8, 65
SMALL_STRIDE = ENC_LINE * SMALL_LINES + TERM      # 498
LARGE_STRIDE = ENC_LINE * LARGE_LINES + TERM      # 4032
SMALL_WINS, LARGE_WINS = 32, 2050
RESIDUE_MODULI = (4, 8, 16)


def uu_enc(v):
    """`PHP_UU_ENC` -- ext/standard/uuencode.c:62, verbatim."""
    return ((v & 0o77) + 0x20) if (v & 0xFF) else 0x60


def enc_line(data):
    """One uuencoded line: the length byte, 4 characters per 3 plaintext bytes,
    then '\\n'. This is `php_uuencode`'s inner block (uuencode.c:79-101) with
    the padding case dropped -- every line here is exactly 45 bytes, which is
    the only length `php_uuencode` ever emits for a full line."""
    out = bytearray()
    out.append(uu_enc(len(data)))
    for i in range(0, len(data), 3):
        a, b, c = data[i], data[i + 1], data[i + 2]
        out.append(uu_enc(a >> 2))
        out.append(uu_enc(((a << 4) & 0o60) | ((b >> 4) & 0o17)))
        out.append(uu_enc(((b << 2) & 0o74) | ((c >> 6) & 0o3)))
        out.append(uu_enc(c & 0o77))
    out.append(0x0A)
    return bytes(out)


def document(rng, nlines):
    """`nlines` full lines plus the terminator line."""
    out = bytearray()
    for _ in range(nlines):
        out += enc_line(rng.randbytes(LINE_LEN))
    out.append(uu_enc(0))
    out.append(0x0A)
    return bytes(out)


def tiled(rng, nwin, nlines):
    return b"".join(document(rng, nlines) for _ in range(nwin))


def _check_residues():
    """The two measured strides must differ modulo every modulus that has bitten
    this project. p01's first draft used 500 and 4096, both == 0 (mod 4), the
    single worst residue for R2, and overstated the delta 2.4x."""
    bad = []
    for m in RESIDUE_MODULI:
        if SMALL_STRIDE % m == LARGE_STRIDE % m:
            bad.append(f"small and large strides ({SMALL_STRIDE}, "
                       f"{LARGE_STRIDE}) are both == {SMALL_STRIDE % m} "
                       f"(mod {m}); pick line counts of different parity or "
                       f"the delta published is one residue wearing the label "
                       f"of a constant")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def main():
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    rng = random.Random(SEED)

    print("ph03 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 498 B = 15.6 KiB, inside this box's 32 KiB L1.
    write("small.bin", 25_000, SMALL_STRIDE, tiled(rng, SMALL_WINS, SMALL_LINES))
    # large: 2050 windows x 4032 B = 7.9 MiB, 8x this box's 1 MiB L2, so the
    # window the driver picks is a cold walk every call.
    write("large.bin", 20_000, LARGE_STRIDE, tiled(rng, LARGE_WINS, LARGE_LINES))

    # ---- adversarial: the length byte is the attack -----------------------
    # n_iters is small: R1 is executing undefined behaviour on three of these,
    # and there is nothing to learn from doing it 25 000 times.
    #
    # The shape all three share: one well-formed line, then a SECOND length byte
    # claiming 45 with only 8 characters behind it. `uuencode.c:141` sets
    # `ee = s + 60` from that byte while the true end `e = src + src_len` sits
    # unused at `:133`, so the inner loop at `:143-148` walks 52 bytes past the
    # window.
    short = bytearray()
    short += enc_line(rng.randbytes(LINE_LEN))          # 62 well-formed bytes
    short.append(uu_enc(LINE_LEN))                      # 'M' -- claims 45
    short += bytes(uu_enc(b) for b in rng.randbytes(8))  # only 8 characters
    short = bytes(short)
    assert len(short) == 71, len(short)

    # (1) THE OVER-READ. Exactly one window and NO slack: `stride == n_blob`, so
    #     `nwin == 1`, `k` is always 0, and the window is also the last thing in
    #     the allocation. R1's first read past `e` is therefore also its first
    #     read past the 71-byte heap block -> ASan reports a READ.
    #     This is the corpus's own `cwe` (CWE-125).
    write("adversarial-read.bin", 8, len(short), short)

    # (2) THE OVER-WRITE, and the ONLY difference from (1) is 60 bytes of slack.
    #     `n_blob = 131`, `stride = 71`, so `nwin = 131/71 = 1` -- still exactly
    #     one window, still `k == 0` -- but now the 52 bytes R1 reads past the
    #     window land INSIDE the blob, so the read is silent and the first thing
    #     ASan sees is `*p++` at `:144` leaving `emalloc(ceil(71*0.75)+1) = 55`.
    #     That is the corpus's own `root_cause_id` ("writes past emalloc").
    #     ⚠ BOTH LIMBS ARE REAL AND THIS PAIR IS WHAT SHOWS THAT THE ORACLE'S
    #     ANSWER IS DECIDED BY THE SOURCE BUFFER'S SLACK, NOT BY THE DEFECT.
    #     PHP always has slack -- a zval string is NUL-terminated and emalloc
    #     rounds to 8 -- which is why the corpus recorded the write.
    write("adversarial-write.bin", 8, len(short), short + rng.randbytes(60))

    # (3) The FIRST of the 2004 fix's two checks, `len > src_len`. A 20-byte
    #     window whose only length byte claims 45: R1 reads to offset 60, 41
    #     past a 20-byte block; R1h refuses at `:139` rather than at `:145`.
    #     Same harm, different guard -- so a fix that shipped only the `ee > e`
    #     half would still be green on (1) and (2) and fail here.
    tiny = bytes([uu_enc(LINE_LEN)]) + bytes(uu_enc(b) for b in rng.randbytes(19))
    assert len(tiny) == 20, len(tiny)
    write("adversarial-shortsrc.bin", 8, len(tiny), tiny)

    # (4) The degenerate shape: `stride > n_blob`, so the driver's guard skips
    #     the loop entirely rather than entering and breaking out of it (which
    #     would put a branch in the measured loop). Every rung prints 0 after
    #     zero kernel calls. This is the control for (1)-(3): the same driver,
    #     the same blob shape, no kernel call at all, declared clean.
    one = document(rng, 1)
    write("adversarial-nowin.bin", 8, len(one) + 1, one)
    return 0


if __name__ == "__main__":
    sys.exit(main())
