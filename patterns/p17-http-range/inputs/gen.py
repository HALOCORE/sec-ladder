#!/usr/bin/env python3
"""Generate p17's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p17-http-range/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel parses one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..2        nsuf       u16 LE, the number of suffix requests
    byte 2..2+2nsuf  suffixes   u16 LE each -- ATTACKER DATA
    byte 2+2nsuf..   body       the bytes a suffix range serves

and the kernel serves, for each suffix `s`, the **last `s` bytes of the
window's body**. The identity that makes the whole design work is
`abs = body_start + (content_len - s) = len - s`, so the served range is
`[len - s, len)` and one attacker-controlled `u16` decides which of three
regimes the read lands in:

    s <= content_len          correct
    content_len < s <= len    IN BOUNDS of the allocation, into the window's
                              own metadata -- the leak, invisible to ASan and
                              to safe Rust alike
    s > len                   BEFORE the allocation -- the OOB, which ASan sees
                              and safe Rust panics on

Six inputs, and the two adversarial ones in the middle are the pattern.

Four things about the sizes are deliberate and must survive any edit.

  * **`small` and `large` have different strides** -- 506 and 4093. Two
    independent reasons, both of which have bitten this project:
      - `work_per_call` *is* the stride, and `harness/check.py`'s
        `d(Ir)/d(work)` assertion needs two probe shapes with **different**
        `work_per_call` or it cannot run at all;
      - the safe-vs-unsafe delta varies with the residue of the measured
        length (`.memory/01-ladder.md`), and quoting one residue as if it were
        the number has been the mistake three times. `_check_residues()`
        asserts that the strides differ mod 4, 8 and 16, **and** that each of
        the three suffix values does too, **and** that the totals folded per
        call do -- so an edit that quietly puts any of those pairs in one class
        fails loudly instead of producing a flattering number.
  * **the strides are not powers of two and are odd-shaped** (506 = 2 + 6 + 498
    and 4093 = 2 + 6 + 4085), so the served ranges are not 8-byte aligned. A
    suffix range on the wire is not aligned; pretending otherwise would flatter
    every rung equally but measure something else.
  * **both adversarial reads are exactly one window** (`n_blob == stride`), and
    that is load-bearing rather than tidy. `k = (acc * nwin) >> 64` is
    pseudo-random over `[0, nwin)`, so with several windows the malformed one
    would be hit only probabilistically -- and, far worse for this pattern
    specifically, a **backward** read from a middle window stays inside the
    allocation, which is a silent wrong answer with no ASan and a gate that
    passes by luck. With `nwin == 1`, `k` is always 0 and `off` is always 0, so
    a negative `abs` is a negative *absolute* index, deterministically.
  * **`adversarial-leak` and `adversarial-oob` differ in exactly one `u16`.**
    Same 64-byte window, same first two suffixes, same body bytes; the third
    suffix is 64 in one file and 70 in the other. That is the whole experiment:
    one attacker-controlled number chooses between an in-bounds information
    leak and an out-of-bounds read, and only the second is a memory-safety
    failure that any bounds check -- C's, Rust's, or a proof's -- can see.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run and discards whatever is declared here, so the Miri cost of a row
is `4 x (bytes folded per call)`. Here that is `4 x sum(suffixes)`, i.e. 3484 on
`small` and 28580 on `large`, against a measured budget of ~3 M folded bytes at
~16 900 B/s / 180 s. Four orders of magnitude clear, so every p17 row is
Miri-checkable.

Note the unit: unlike p16, **the bytes folded per call can EXCEED the window**,
because every suffix serves a slice of the same body and `nsuf` of them can each
serve nearly all of it (871 of 506 on `small`, 7145 of 4093 on `large`). See
`../model.py`'s `work_per_call` docstring -- the derived `Ir` floor is therefore
*looser* here than p16's, not stricter, and that is stated rather than hidden.
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
SMALL_SUFFIXES = (498, 251, 122)          # <= content_len: all well-formed
LARGE_SUFFIXES = (4085, 2041, 1019)
SMALL_BODY, LARGE_BODY = 498, 4085        # content_len
SMALL_WINS, LARGE_WINS = 32, 2050
RESIDUE_MODULI = (4, 8, 16)


def head(nsuf_declared, suffixes):
    """The window header: `nsuf` then the suffix table, u16 LE throughout.

    `nsuf_declared` is written verbatim rather than derived from `len(suffixes)`
    so that `adversarial-nsuf.bin` can declare a count the window cannot hold --
    that is the one check every rung keeps."""
    out = bytearray()
    out += nsuf_declared.to_bytes(2, "little")
    for s in suffixes:
        out += s.to_bytes(2, "little")
    return out


def window(rng, nsuf_declared, suffixes, body_len):
    """One window: header, suffix table, random body."""
    w = head(nsuf_declared, suffixes)
    w += rng.randbytes(body_len)
    return bytes(w)


def tiled(rng, nwin, nsuf_declared, suffixes, body_len):
    """`nwin` windows, byte-identical in *shape* and different in *content*.

    The shape is fixed so `work_per_call` is one scalar; the body bytes differ
    per window so the checksum depends on which window the driver picked, which
    is what keeps the anti-collapse barrier honest."""
    out = bytearray()
    for _ in range(nwin):
        out += window(rng, nsuf_declared, suffixes, body_len)
    return bytes(out)


def _check_residues():
    """Every measured pair must differ modulo every modulus that has ever bitten
    this project. Returns a list of problems (empty when healthy).

    p01's first draft used 500 and 4096, both == 0 (mod 4), the single worst
    residue for R2, and overstated it 2.4x. p02's used 61 and 4092, which differ
    mod 4 and mod 8 -- and that was still not enough, because the modulus that
    governed its copy epilogue was 16. p16's turned out to be 4. So p17 checks
    all three moduli on every quantity a loop's trip count is derived from: the
    **stride** (`work_per_call`, and the outer walk's extent), each of the three
    **suffix values** (the inner fold's trip counts, one per served range), and
    the **total folded per call** (what an O(n) claim would be denominated in).
    """
    bad = []
    pairs = [("stride", small_stride(), large_stride()),
             ("total folded per call", sum(SMALL_SUFFIXES), sum(LARGE_SUFFIXES))]
    pairs += [(f"suffix[{i}]", a, b)
              for i, (a, b) in enumerate(zip(SMALL_SUFFIXES, LARGE_SUFFIXES))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    return bad


def small_stride():
    return 2 + 2 * len(SMALL_SUFFIXES) + SMALL_BODY      # 506


def large_stride():
    return 2 + 2 * len(LARGE_SUFFIXES) + LARGE_BODY      # 4093


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# The two adversarial windows. Same 64 bytes of shape, same body, and one
# suffix apart -- see the module docstring.
#
#   len = 64, nsuf = 3, body_start = 8, content_len = 56
#
#   s = 10  -> start =  46, abs = 54  correct: serves buf[54..64)
#   s = 56  -> start =   0, abs =  8  correct: serves the whole body
#   s = 64  -> start =  -8, abs =  0  LEAK: serves buf[0..64) -- the suffix
#                                     table and `nsuf` itself, IN BOUNDS
#   s = 70  -> start = -14, abs = -6  OOB: serves buf[-6..64) -- six bytes
#                                     BEFORE the allocation
#
# The first two suffixes are shared, so **every rung that keeps the check prints
# the same checksum on both files** and only R1 tells them apart -- once
# silently and once with a sanitizer report.
ADV_LEN = 64
ADV_NSUF = 3
ADV_BODY = ADV_LEN - (2 + 2 * ADV_NSUF)      # 56 == content_len
ADV_LEAK_SUFFIXES = (10, 56, 64)
ADV_OOB_SUFFIXES = (10, 56, 70)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    rng = random.Random(SEED)

    print("p17 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {small_stride()}/{large_stride()}, suffixes "
          f"{SMALL_SUFFIXES}/{LARGE_SUFFIXES} and totals "
          f"{sum(SMALL_SUFFIXES)}/{sum(LARGE_SUFFIXES)} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 506 B = 15.8 KiB, so the whole working set fits this
    # box's 32 KiB L1 and the row is latency-free. 871 bytes folded per call.
    write("small.bin", 25_000, small_stride(),
          tiled(rng, SMALL_WINS, len(SMALL_SUFFIXES), SMALL_SUFFIXES, SMALL_BODY))
    # large: 2050 windows x 4093 B = 8.0 MiB, 8x this box's 1 MiB L2. The window
    # the driver picks is pseudo-uniform over the whole blob, so every call is a
    # cold walk. 7145 bytes folded per call.
    write("large.bin", 12_000, large_stride(),
          tiled(rng, LARGE_WINS, len(LARGE_SUFFIXES), LARGE_SUFFIXES, LARGE_BODY))

    # ---- adversarial: one u16 decides which harm ---------------------------
    # n_iters is small: R1 is executing undefined behaviour on `oob`, and there
    # is nothing to learn from doing it 25 000 times.
    #
    # The bodies are drawn from the same rng state for both files so that the
    # ONLY difference between them is the third suffix. Drawing them separately
    # would leave two variables and the comparison would be worth less.
    adv_body = rng.randbytes(ADV_BODY)

    # (1) THE LEAK. `content_len < s <= len`: the read starts inside the
    #     window's own metadata. In bounds of the allocation, so **no
    #     sanitizer may fire** and safe Rust cannot see it either. If ASan
    #     fires here the input is mis-targeted, not the pattern.
    leak = bytes(head(ADV_NSUF, ADV_LEAK_SUFFIXES)) + adv_body
    assert len(leak) == ADV_LEN, len(leak)
    write("adversarial-leak.bin", 8, ADV_LEN, leak)

    # (2) THE OOB. `s > len`: `abs` is negative, and because this file is a
    #     single window `off` is 0, so the absolute index is negative too.
    #     ASan must fire, and it must say *before* the region -- p16's said
    #     *after*, and the difference is the sign of the arithmetic.
    oob = bytes(head(ADV_NSUF, ADV_OOB_SUFFIXES)) + adv_body
    assert len(oob) == ADV_LEN, len(oob)
    assert leak[:6] == oob[:6] and leak[8:] == oob[8:], "the two must differ in one u16"
    write("adversarial-oob.bin", 8, ADV_LEN, oob)

    # (3) `2 + 2*nsuf > len`: the suffix table does not fit in the window. This
    #     is the check EVERY rung keeps, R1 included, so all eight cells must
    #     return 0 on every call and print 0. It is the control for (1) and (2):
    #     the same "the header lied" shape with the suffix *values* innocent.
    write("adversarial-nsuf.bin", 8, 34, tiled(rng, 16, 100, (7, 9), 28))

    # (4) stride 1: a window that cannot even hold `nsuf`. The driver guard
    #     `stride_w >= 2` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after ZERO kernel calls. Distinct from (3), where
    #     the calls happen and the kernel is what rejects.
    write("adversarial-stride1.bin", 8, 1,
          tiled(rng, 8, 2, (3, 4), 8))
    return 0


if __name__ == "__main__":
    sys.exit(main())
