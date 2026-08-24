#!/usr/bin/env python3
"""Generate p17's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns/p17-http-range/inputs/gen.py
    python3 patterns/p17-http-range/inputs/gen.py --sweep   # + the `nsuf` sweep

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

Eight inputs; the adversarial ones in the middle are the pattern. `leak`/`oob`
are the one-`u16` pair that chooses between the two harms, and
`crosswin-lo`/`crosswin-hi` are the two-window pair that shows what the in-bounds
harm reads when there *is* a neighbour to read.

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
    `adversarial-crosswin-{lo,hi}` is the **deliberate exception** and the
    paragraph above is exactly why it is built as a *pair*: see
    `crosswin()` below and `../spec.md`, "Why `adversarial-crosswin` is two
    windows and a pair".
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

# ---- adversarial-crosswin: the read that reaches into ANOTHER window --------
#
# Two 64-byte windows in one blob. Everything above about `nwin == 1` still
# holds for `leak`/`oob`; this input breaks that rule ON PURPOSE, and the way it
# stays a *demonstration* rather than a coin flip is that it is generated as a
# PAIR that differs in nothing but the victim's secret bytes. The claim is
# differential -- "change the victim's bytes and the output changes, with no
# panic and no sanitizer report" -- and that claim is independent of which
# window `k` happens to select on any given iteration.
#
#   window 0, off = 0    THE VICTIM
#       nsuf = 1, suffix (32) -> body_start = 4, content_len = 60
#       serves buf[32..64) and nothing else, so bytes buf[4..32) -- the SECRET
#       -- are read by NO rung that keeps `start >= 0`, and by no rung at all
#       that guards the WINDOW-relative index either.
#
#       It has to serve *something*. A window that serves nothing returns 0,
#       `acc` never leaves 0, and `k = (acc * nwin) >> 64` is then pinned at 0
#       for ever: the driver's multiply-shift has an absorbing state at
#       `acc == 0` and window 1 would never be visited. 32 bytes is enough for
#       window 0's result to be a full-width pseudo-random u64 on the first
#       call.
#
#   window 1, off = 64   THE ATTACKER
#       nsuf = 3, suffixes (10, 56, 122) -> body_start = 8, content_len = 56
#       s = 122 gives start = 56 - 122 = -66 and an ABSOLUTE index of
#       off + len - s = 128 - 122 = 6, i.e. six bytes into the *victim's*
#       window. The read is [6, 128): in bounds of the blob, so ASan is silent
#       and safe Rust does not panic, and it covers 26 of the 28 secret bytes.
#
# What each guard does with that third request:
#
#   none        (R1, c/kernel.c)                   serves it   -> DISCLOSES
#   start >= -(body_start)        (window-relative, NOTES 7 M4)  rejects (-66 < -8)
#   start >= -((off + body_start))(slice-relative)  serves it   -> DISCLOSES
#   start >= 0                    (R1h, R2..R5)     rejects
#
# and the middle two are the point: same Verus verdict, opposite outcome.
CW_LEN = 64
CW_PUB = 32                                   # window 0's public tail
CW_VICTIM_SUFFIXES = (32,)
CW_ATTACK_SUFFIXES = (10, 56, 122)
CW_SECRETS = (("lo", 0x00), ("hi", 0xFF))     # the only difference in the pair


# ---- `--sweep`: the `nsuf` axis, appended LAST (TASK_082, RECAP "Owed" 4) ----
#
# **This is the axis p17's headline is denominated in and the one it never
# swept.** `small` and `large` differ 8x in body size and NOT AT ALL in `nsuf`
# -- both serve 3 requests -- so the published "+32 Ir/call" is two points at one
# `nsuf`, which is the residue-class failure that broke p16's `nrec + 3` and
# p38's additivity, sitting inside a published law. NOTES.md 10 already carries
# TASK_015_REVIEW M2's finding that the difference is `~= 7*nsuf + 9`, i.e. **per
# REQUEST and not per call**, measured on inputs that were never committed
# (`.temp/review015/gen17.py`). The tree could state the law and not reproduce
# it; this band is what makes it re-derivable from a hashed file.
#
# Three decisions, each forced rather than chosen:
#
#   * **the same shape TASK_015_REVIEW used** -- body 498, 32 windows, and the
#     same `BODY - 1 - (i*37) % (BODY - 8)` suffix spread -- so the shipped band
#     is directly comparable with NOTES.md 10's published table rather than being
#     a second, differently-shaped experiment that cannot be checked against it.
#     `nsuf = 3` here is `small`'s `nsuf` at `small`'s body length, so the band
#     lands on a point the matrix already measures.
#   * **`nsuf` 1..8 CONSECUTIVE, not two full mod-16 cycles.** The file's own
#     rule elsewhere is two cycles of the largest modulus that has bitten this
#     project, and it does not apply here: `nsuf` is a REQUEST COUNT, the outer
#     loop's trip count, not a byte length -- no unrolled epilogue is keyed on
#     it, so it has no residue class to hide a sawtooth in. Eight consecutive
#     points test an affine law directly, and NOTES.md 10 reports exactly zero
#     residual for `17*nsuf` over these eight.
#   * **appended LAST, drawn from the shared sequential rng**, so every one of
#     the eight pre-existing blobs stays BYTE-IDENTICAL -- verified by sha256
#     before and after at TASK_082, 8 of 8 unchanged. That is what makes this
#     cost a gate re-run and not a re-measure: `check.inputs_of` and
#     `measure.SKIP_INPUT_PREFIX` both drop the `sweep-` prefix, so no matrix
#     input, no `inputs_checked` entry and no number in
#     `results/p17-http-range.json` depends on any of it. ⚠ The prefix IS the
#     mechanism (`.memory/05-layout.md`): a band named anything else enters the
#     measurement matrix and costs 43 minutes.
#
# ⚠ **What this band deliberately does NOT hold fixed: the folded bytes.** The
# suffix values are large, so `sum(suffixes)` -- p17's `work_per_call` -- rises
# with `nsuf`. That is TASK_015_REVIEW's shape and it is sound for the quantity
# NOTES.md 10 publishes, because that quantity is a *difference between rungs*
# and §3b measured the per-byte rate of `R3ship - R4` at exactly 0, so the byte
# term cancels. It is NOT sound for an absolute per-call law of any single rung;
# for that, sweep the body length, which is what §3b's 34-point band already
# does at fixed `nsuf`. The two bands are orthogonal on purpose.
SWEEP_NSUFS = tuple(range(1, 9))
SWEEP_BODY = 498                  # == SMALL_BODY: the band crosses `small`
SWEEP_WINS = 32                   # == SMALL_WINS
SWEEP_ITERS = 5_000


def sweep_suffixes(nsuf, body=SWEEP_BODY):
    """`nsuf` well-formed suffix values, spread over the body.

    Byte-identical to `.temp/review015/gen17.py`'s formula, which is what
    NOTES.md 10's published `17*nsuf` / `7*nsuf + 9` table was measured on. All
    values are `<= content_len`, so every request is in the *correct* regime and
    no rung enters an adversarial band: all rungs must print the same checksum
    on every blob of this sweep."""
    return [body - 1 - (i * 37) % (body - 8) for i in range(nsuf)]


def crosswin(secret_byte):
    """The two-window blob, parameterised by the victim's secret fill byte.

    Deterministic and rng-free: the pair must differ in the secret bytes and in
    NOTHING else, and drawing either window from the shared rng would make the
    two files differ in whatever the rng happened to be doing."""
    v = bytearray()
    v += head(len(CW_VICTIM_SUFFIXES), CW_VICTIM_SUFFIXES)          # 4 bytes
    v += bytes([secret_byte]) * (CW_LEN - 4 - CW_PUB)               # SECRET
    v += bytes((0x11 * (i % 15)) % 251 for i in range(CW_PUB))      # public
    assert len(v) == CW_LEN, len(v)
    v += head(len(CW_ATTACK_SUFFIXES), CW_ATTACK_SUFFIXES)          # 8 bytes
    v += bytes(0x40 + (i % 64) for i in range(CW_LEN - 8))
    assert len(v) == 2 * CW_LEN, len(v)
    return bytes(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-nsuf-NN.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    # `args`, not `a`: the crosswin assertion below binds `a, b = ...` and p16's
    # `a = ap.parse_args()` spelling would be silently shadowed by it.
    args = ap.parse_args()
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

    # (3b) THE CROSS-WINDOW READ. Two windows, generated as a pair whose only
    #      difference is window 0's secret fill byte. Every rung that keeps
    #      `start >= 0` -- and every rung that guards the WINDOW-relative index
    #      -- prints the same checksum on both files; a rung that guards the
    #      SLICE-relative index, which is all a bounds check or a
    #      `get_unchecked` precondition actually demands, prints two different
    #      ones. Both files are in bounds throughout, so ASan must stay silent
    #      on both, exactly as on `adversarial-leak`.
    for tag, byte in CW_SECRETS:
        blob = crosswin(byte)
        assert len(blob) == 2 * CW_LEN
        write(f"adversarial-crosswin-{tag}.bin", 8, CW_LEN, blob)
    a, b = (crosswin(x) for _, x in CW_SECRETS)
    assert a[:4] == b[:4] and a[CW_LEN - CW_PUB:] == b[CW_LEN - CW_PUB:], \
        "the crosswin pair must differ ONLY in window 0's secret bytes"

    # (4) stride 1: a window that cannot even hold `nsuf`. The driver guard
    #     `stride_w >= 2` skips the loop entirely rather than entering and
    #     breaking out of it, which would put a branch in the measured loop, so
    #     every rung prints 0 after ZERO kernel calls. Distinct from (3), where
    #     the calls happen and the kernel is what rejects.
    write("adversarial-stride1.bin", 8, 1,
          tiled(rng, 8, 2, (3, 4), 8))

    # ---- the `nsuf` sweep, appended LAST ----------------------------------
    # Everything above is emitted from the same rng in the same order as before
    # TASK_082, so all eight blobs above are byte-identical to the committed
    # ones. See SWEEP_NSUFS above for why this band exists.
    if args.sweep:
        print(f"  -- sweep over nsuf (NOTES.md 10's axis, "
              f"{len(SWEEP_NSUFS)} consecutive request counts at body "
              f"{SWEEP_BODY})")
        for nsuf in SWEEP_NSUFS:
            sufs = sweep_suffixes(nsuf)
            write(f"sweep-nsuf-{nsuf:02d}.bin", SWEEP_ITERS,
                  2 + 2 * nsuf + SWEEP_BODY,
                  tiled(rng, SWEEP_WINS, nsuf, sufs, SWEEP_BODY))
    return 0


if __name__ == "__main__":
    sys.exit(main())
