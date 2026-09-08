#!/usr/bin/env python3
"""Generate ph03's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph03-uudecode-bound/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel uudecodes one window
    byte 8..   u8[] blob       uuencoded text; n_blob = payload_len - 8

A *window* is a complete uuencoded document, exactly as `php_uuencode`
(`uuencode.c:68-124`) emits one: `K` full lines, then a SHORT FINAL LINE, then
the terminator.

    full line      PHP_UU_ENC(45)  + 60 characters + '\\n'     = 62 bytes
    short line     PHP_UU_ENC(T)   + 4*ceil(T/3) chars + '\\n'
    terminator     PHP_UU_ENC(0)   + '\\n'                     = 2 bytes

⚠⚠⚠ **THE SHORT FINAL LINE IS NOT DECORATION AND ITS ABSENCE WAS A DEFECT.**
`uuencode.c:141` is

    ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));

— **two arms**, and the whole pattern is about the second one. Until
TASK_PHP_015 this file emitted length 45 exclusively and called the padding case
*"dropped"*, so **not one byte of the benign corpus ever took the `floor()`
arm**, and `45 % 3 == 0` is precisely the case in which the number of bytes a
line EMITS equals the `total_len` it DECLARES. That monoculture hid
`TASK_PHP_014` M1 — `model.py::uu_fold` folding every emitted byte where
`verus.rs` folds the first `total_len` — for a whole task, and it was also
*unfaithful*, because real uuencoded data always has a short final line.

**THE RULE, and it generalises past this row (`PROTOCOL_PHP.md` §A5): the
generator must take EVERY ARM of the branch the defect lives on, and must
ASSERT that it does.** `_check_span()` below is that assertion — it re-decodes
the generated blob with its own transcription of the decoder and refuses to
write a corpus that does not reach the `floor()` arm, the strict case
`declared < emitted` and the equality case `declared == emitted`. An unasserted
intention is what the old comment was.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 556 and 4090 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all; and the
    safe-vs-unsafe delta varies with the residue of the measured length
    (`.memory/01-ladder.md`). `_check_residues()` asserts both, so an edit that
    quietly puts the pair in one class fails loudly. ⚠ A full line is 62 bytes,
    so `62*K + 60` is `0 (mod 4)` for even K and `2 (mod 4)` for odd K -- K = 8
    and K = 65 is the cheapest pair that separates them.
  * **the strides are not powers of two** (556 = 2^2*139, 4090 = 2*5*409), so
    consecutive windows do not share a cache-set alignment, and no window
    boundary is 8-byte aligned in a way a rung could exploit.
  * **documents tile each window exactly**, so every call decodes the same
    number of lines and `work_per_call = stride` is a slight over-estimate of
    the bytes actually touched (the '\\n' of each line is skipped, and the
    terminator is never reached at all -- the decoder stops at the short line,
    `uuencode.c:156`). An over-estimate raises the derived `Ir` floor, which is
    the direction a floor should err.
  * ⚠ **the three tail lengths all encode to 14 groups** -- `ceil(T/3) == 14`
    and `ceil(line_len(T)/4) == 14` for T in {40, 41, 42} -- so the short line
    costs the same DECODE WORK whichever tail a window carries, and the
    `large - small` difference stays exactly 57 full lines. That is what keeps
    NOTES.md §8b's per-line arithmetic a clean subtraction while the corpus
    still spans both the strict and the equality case.

⚠⚠ **THE FIVE ADVERSARIAL FILES ARE THE ROW.** Read the comments on each: two
of them differ *only* in 60 bytes of slack after the window, and that difference
decides whether the oracle sees the over-READ or the over-WRITE. NOTES.md §4.
The fifth, `adversarial-floor`, is the `floor()` arm's adversarial cell and was
added by TASK_PHP_015 for the same reason as the short final line.
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

LINE_LEN = 45                      # bytes of plaintext per FULL uuencoded line
ENC_LINE = 1 + 60 + 1              # length byte + 60 characters + '\n' == 62
TERM = 2                           # PHP_UU_ENC(0) + '\n'

# The short final line's plaintext lengths, cycled by document index.
#   40, 41  ->  declared < emitted   (3*ceil(line_len(T)/4) = 42 > T)
#   42      ->  declared == emitted
# Both cases matter: the strict one is what `model.py::uu_fold` got wrong, and
# the equality one is the case that used to be the ONLY one in the corpus.
TAILS = (40, 41, 42)
TAIL_GROUPS = 14                   # ceil(T/3) for every T in TAILS
ENC_TAIL = 1 + 4 * TAIL_GROUPS + 1  # 58

SMALL_LINES, LARGE_LINES = 8, 65
SMALL_STRIDE = ENC_LINE * SMALL_LINES + ENC_TAIL + TERM      # 556
LARGE_STRIDE = ENC_LINE * LARGE_LINES + ENC_TAIL + TERM      # 4090
SMALL_WINS, LARGE_WINS = 32, 2050
RESIDUE_MODULI = (4, 8, 16)


def rng_for(name):
    """One INDEPENDENT stream per output file.

    ⚠ It used to be a single stream shared by all six files, which means every
    edit to `small`'s shape silently rewrote all four adversarial blobs as the
    draws shifted -- so a fixture change could never be reviewed as a local one.
    Seeding per name costs nothing and makes it local. (`random.seed` on a `str`
    hashes it with sha512, so this is stable across interpreter versions.)"""
    return random.Random(f"{SEED:x}:{name}")


def uu_enc(v):
    """`PHP_UU_ENC` -- ext/standard/uuencode.c:62, verbatim."""
    return ((v & 0o77) + 0x20) if (v & 0xFF) else 0x60


def enc_line(data):
    """One uuencoded line: the length byte, 4 characters per 3 plaintext bytes,
    then '\\n'. This is `php_uuencode`'s inner block (uuencode.c:79-101) **with
    the padding case INCLUDED** -- a final partial group is zero-padded to
    three bytes, which is what `uuencode.c:110-115` produces for a tail whose
    length is not a multiple of 3 (its `PHP_UU_ENC('\\0')` operands are exactly
    the zeros this pads with)."""
    out = bytearray()
    out.append(uu_enc(len(data)))
    d = bytes(data) + b"\0" * (-len(data) % 3)
    for i in range(0, len(d), 3):
        a, b, c = d[i], d[i + 1], d[i + 2]
        out.append(uu_enc(a >> 2))
        out.append(uu_enc(((a << 4) & 0o60) | ((b >> 4) & 0o17)))
        out.append(uu_enc(((b << 2) & 0o74) | ((c >> 6) & 0o3)))
        out.append(uu_enc(c & 0o77))
    out.append(0x0A)
    return bytes(out)


def document(rng, nlines, tail):
    """`nlines` full lines, a short final line of `tail` plaintext bytes, then
    the terminator line -- exactly `php_uuencode`'s output shape."""
    out = bytearray()
    for _ in range(nlines):
        out += enc_line(rng.randbytes(LINE_LEN))
    out += enc_line(rng.randbytes(tail))
    out.append(uu_enc(0))
    out.append(0x0A)
    return bytes(out)


def tiled(rng, nwin, nlines):
    return b"".join(document(rng, nlines, TAILS[i % len(TAILS)])
                    for i in range(nwin))


def _decode_stats(win):
    """(declared, emitted, non45_lines) for one window.

    A deliberately SEPARATE transcription of `php_uudecode`'s walk -- gen.py
    must be able to assert what it generated without importing the model it is
    generating for (and `../model.py` binds a different `slb` than this file
    does, so importing it would be wrong twice over). Kept to the arithmetic
    the assertion needs: it does not decode, it counts."""
    s, e = 0, len(win)
    declared = emitted = non45 = 0
    while s < e:
        ln = (win[s] - 0x20) & 0o77                   # PHP_UU_DEC
        s += 1
        if ln == 0:
            break
        fl = 60 if ln == 45 else (ln * 133) // 100    # uuencode.c:141
        if ln > len(win) or fl > e - s:               # f95c1df58349
            break
        if ln != 45:
            non45 += 1
        steps = (fl + 3) // 4                         # the inner loop's count
        emitted += 3 * steps
        declared += ln
        s += 4 * steps
        if ln < 45 or s >= e:                         # uuencode.c:156, :150
            break
        s += 1                                        # skip '\n'
    return declared, emitted, non45


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


def _check_span(name, blob, stride):
    """⚠⚠⚠ THE MUST-FIRE ASSERTION, AND IT IS THE PART THAT GENERALISES.

    A benign corpus must exercise every arm of the branch the defect lives on,
    and must SAY SO mechanically. Here that branch is `uuencode.c:141`'s
    `len == 45 ? 60 : (int) floor(len * 1.33)`, and the derived quantity the
    oracle turns on is whether a line's declared `ln` is less than the
    `3*ceil(fl/4)` bytes it emits.

    Refuses to write a corpus that misses any of three:
      * a line taking the `floor()` arm at all;
      * a window with `declared <  emitted`  (the strict case -- 42 of the 63
        length bytes, and the case TASK_PHP_014 M1 lived in);
      * a window with `declared == emitted`  (the equality case -- multiples of
        3, which is ALL the corpus had before TASK_PHP_015).
    """
    strict = equal = non45 = 0
    for k in range(len(blob) // stride):
        d, em, n45 = _decode_stats(blob[k * stride:(k + 1) * stride])
        non45 += n45
        strict += (d < em)
        equal += (d == em)
    bad = []
    if not non45:
        bad.append(f"{name}: not one line takes uuencode.c:141's floor() arm "
                   f"-- every length byte is 45, which is the arm the defect "
                   f"is NOT about")
    if not strict:
        bad.append(f"{name}: no window has declared < emitted, so the corpus "
                   f"cannot tell `fold(out[:total_len])` from `fold(out)` "
                   f"(TASK_PHP_014 M1)")
    if not equal:
        bad.append(f"{name}: no window has declared == emitted; the equality "
                   f"case is a real one and must not be lost while fixing the "
                   f"strict one")
    print(f"  span ok: {name:24s} windows={len(blob)//stride:<6d} "
          f"floor()-arm lines={non45:<6d} declared<emitted={strict:<6d} "
          f"declared==emitted={equal}")
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

    print("ph03 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 556 B = 17.4 KiB, inside this box's 32 KiB L1.
    small = tiled(rng_for("small"), SMALL_WINS, SMALL_LINES)
    # large: 2050 windows x 4090 B = 8.0 MiB, 8x this box's 1 MiB L2, so the
    # window the driver picks is a cold walk every call.
    large = tiled(rng_for("large"), LARGE_WINS, LARGE_LINES)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    for p in problems:
        print("gen.py: " + p, file=sys.stderr)
    if problems:
        return 1
    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 20_000, LARGE_STRIDE, large)

    # ---- adversarial: the length byte is the attack -----------------------
    # n_iters is small: R1 is executing undefined behaviour on four of these,
    # and there is nothing to learn from doing it 25 000 times.
    #
    # The shape (1)-(3) share: one well-formed line, then a SECOND length byte
    # claiming 45 with only 8 characters behind it. `uuencode.c:141` sets
    # `ee = s + 60` from that byte while the true end `e = src + src_len` sits
    # unused at `:133`, so the inner loop at `:143-148` walks 52 bytes past the
    # window.
    rng = rng_for("adversarial")
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
    #     ⚠ TASK_PHP_014 M5 measured this guard REDUNDANT (hunk 2 refuses every
    #     document hunk 1 does). The input stays because it pins WHICH guard
    #     R1h reaches first, which is what a reader of `kernel_hardened.c` asks.
    tiny = bytes([uu_enc(LINE_LEN)]) + bytes(uu_enc(b) for b in rng.randbytes(19))
    assert len(tiny) == 20, len(tiny)
    write("adversarial-shortsrc.bin", 8, len(tiny), tiny)

    # (4) The degenerate shape: `stride > n_blob`, so the driver's guard skips
    #     the loop entirely rather than entering and breaking out of it (which
    #     would put a branch in the measured loop). Every rung prints 0 after
    #     zero kernel calls. This is the control for (1)-(3): the same driver,
    #     the same blob shape, no kernel call at all, declared clean.
    one = document(rng, 1, TAILS[0])
    write("adversarial-nowin.bin", 8, len(one) + 1, one)

    # (5) ⚠ THE `floor()` ARM, ADVERSARIALLY -- TASK_PHP_015.
    #     (1)-(3) all claim 45, so before this file every adversarial byte took
    #     `uuencode.c:141`'s `== 45` arm too, and the arm the row is named for
    #     had no adversarial cell at all. Here the single length byte declares
    #     40: `fl = (int) floor(40 * 1.33) = 53`, `ee = s + 53` against a true
    #     end 44 characters away, so hunk 1 (`len > src_len`, 40 <= 45) does
    #     NOT fire and hunk 2 (`ee > e`) does -- the one guard of the 2004 fix
    #     that decides anything (TASK_PHP_014 M5). R1 runs `ceil(53/4) = 14`
    #     groups from offset 1, i.e. reads to offset 57 of a 45-byte window and
    #     writes 42 bytes into an `emalloc(ceil(45*0.75)+1) = 35`.
    floor_win = bytes([uu_enc(40)]) + bytes(
        uu_enc(b) for b in rng_for("floor").randbytes(44))
    assert len(floor_win) == 45, len(floor_win)
    write("adversarial-floor.bin", 8, len(floor_win), floor_win)
    return 0


if __name__ == "__main__":
    sys.exit(main())
