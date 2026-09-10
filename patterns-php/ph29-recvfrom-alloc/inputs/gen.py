#!/usr/bin/env python3
"""Generate ph29's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph29-recvfrom-alloc/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is one `stream_socket_recvfrom($s, $to_read [, $flags, &$remote])`
call, laid out the way the arguments and the datagram reach the function:

    byte 0..7    i64 LE  to_read    <- zend_parse_parameters "l", :304/:309
    byte 8..9    u16 LE  ctl        <- bit 0: `zremote` was passed (:315)
                                       bit 1: the transport fails, recvd = -1
    byte 10..11  u16 LE  want       <- navail = want % (n_pay + 1)
    byte 12..    u8[]    payload    <- the datagram; n_pay = stride - 12

⚠⚠⚠ **`to_read` IS THE WHOLE ROW AND IT IS A FULL 64-BIT SIGNED VALUE ON
PURPOSE.** `emalloc(to_read + 1)` at `streamsfuncs.c:321` hands a `size_t` to
`_emalloc`, which stores `REAL_SIZE(size)` into `Zend/zend_alloc.c:129`'s
`unsigned int real_size` -- truncation T1. The block that comes back is
`real_size` bytes; the receive at `:323` is given `to_read`. Any `to_read` whose
`to_read + 1` is `0 mod 2^32`, and every negative `to_read`, makes the two
disagree.

⚠⚠ **THE BENIGN CORPUS MUST NOT CONTAIN ONE, AND `_check_span()` REFUSES TO
WRITE ONE THAT DOES.** Two independent reasons:

  * a truncating window is an OUT-OF-BOUNDS WRITE, so it is adversarial by
    definition and must not be in a file the gate calls benign;
  * `445daac3ab1a`'s guard is `if (to_read <= 0)`, so any window with
    `to_read <= 0` makes R1h answer differently from R1 -- and `check.py`
    stage 7h requires the two arms to agree on every non-adversarial input.
    ⚠ `to_read == 0` is NOT a defect (`emalloc(1)` is honoured and
    `read_buf[0] = '\0'` is in bounds); the guard refuses it anyway, which is
    measured in `../controls/fix_scope.py` and is a finding about the fix
    rather than about the corpus.

⚠ **AND NO WINDOW MAY CARRY `to_read == LONG_MAX`**: `to_read + 1` is then
signed-overflow UB, which a compiler may fold differently at `-O0` and `-O3`
for a reason that is not the defect. That is `RECAP_PHP.md` F46's UB-free
trigger, applied to the whole corpus rather than to one input.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_span()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1). The defect lives on the
size the allocator computes, so the arms are:

  * **both sides of the size-class cache** -- `real_size <= 87` makes `_efree`
    push the block onto a per-class LIFO and return WITHOUT calling `free`
    (`zend_alloc.c:270-279`), and `real_size > 87` returns it to `malloc`.
    ⚠ That is the branch `PROTOCOL_PHP.md` §B1.1 is about, and a corpus on one
    side of it exercises half the allocator;
  * **both arms of `if (recvd >= 0)`** (`:328`) -- a successful receive and a
    failed one. The failed one is the arm where 5.0.0 **leaks** `read_buf`;
  * **both arms of `if (zremote)`** (`:315`) and both arms of
    `if (zremote && Z_STRLEN_P(zremote))` (`:329`);
  * **both directions of the transport's clamp** -- `to_read < navail`, where
    `php_stream_read` returns fewer bytes than the datagram had, and
    `to_read >= navail`, where it returns all of them;
  * `navail == 0` (an empty datagram) and `navail == n_pay` (a full one);
  * ⚠ and, NEGATIVELY, **no window on which `445daac3ab1a`'s guard fires and no
    window on which the allocation truncates.**

⚠ **THIS IS A SUPERSET CONDITION AND `model.py` CARRIES THE SHARPER ONE.**
`_check_span` asserts over EVERY window in the file; the driver picks windows
from a checksum-derived index and need not visit them all, so
`model.py::selfcheck` check 2 re-asserts the same arm table over **the calls the
driver actually makes**.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 550 and 4076 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all.
  * **the strides are not powers of two** (550 = 2*5^2*11, 4076 = 2^2*1019), so
    consecutive windows do not share a cache-set alignment.
  * ⚠ **`navail` and `to_read` both scale with the stride**: `navail` is taken
    mod `n_pay + 1` and `to_read` is drawn relative to `n_pay`, so the per-call
    copy, the per-call fold AND the per-call allocation all grow with
    `work_per_call` rather than being constants with a label.
  * **`want` is written with a random multiple of `n_pay + 1` added**, so the
    `%` in the kernel is exercised rather than being the identity.

⚠⚠ **THE FOUR ADVERSARIAL FILES ARE THE ROW.**
⚠ Read `adversarial-trunc` and `adversarial-neg` together: **they differ in
`to_read` and in nothing else**, and that difference is whether the row needs
`common-php/emalloc_shim.h` at all. Measured on this box
(`../controls/allocator.py`, `.temp/php27/reach.c`):

    to_read = -4294967297   size = 18446744069414584320  real_size = 0
                            shim  -> a 24-byte block, and the receive OVERFLOWS
                            plain -> malloc FAILS; PHP exit(1)s at
                                     zend_alloc.c:189. THE DEFECT DOES NOT EXIST
    to_read = -1            size = 0                     real_size = 0
                            shim  -> a 24-byte block, and the receive OVERFLOWS
                            plain -> malloc(0) SUCCEEDS and the receive
                                     overflows it too. THE SHIM IS NOT NEEDED

so `adversarial-trunc` is the input that cannot pass without the shim and
`adversarial-neg` is its control. Both are refused by `445daac3ab1a`.

⚠⚠ **`navail` is 4 on both, and WHAT R1 DOES WITH IT IS AN ABORT.**
Measured on the shipped binaries, all four R1 cells:

    c-gcc/c-clang x O0/O3, isolated   rc=134  `malloc(): invalid size (unsorted)`
    c-gcc-h (R1h)                     rc=0    the refusal sentinel
    safe_naive / unsafe               rc=0    the clamped fold

⚠ **THE FIRST DRAFT OF THIS PARAGRAPH SAID THE OPPOSITE** -- that a 5-byte
overflow of a 24-byte `malloc` region lands inside the 8 bytes glibc leaves as
the next chunk's unused `mchunk_prev_size`, so the process survives to print its
`u64`. That is true in a program whose heap has a chunk after this one, and
FALSE in the driver, where the block is adjacent to the top chunk and the
overflow smashes its size field. `../controls/oracle.py`'s `navail` sweep is
where the boundary is measured: silent at `navail <= 1`, `malloc(): corrupted
top size` from 4 upward. **The claim was a plausible reading of glibc's layout
that nobody had run** -- `F52`'s shape, caught by running it.

⭐ An aborting adversarial cell is the ESTABLISHED shape in this corpus, not a
concession: `ph03` records `malloc(): invalid size (unsorted)` and `ph16`
records `munmap_chunk(): invalid pointer` in their own gate records, and
`check.py` stage 4 records per-rung behaviour rather than requiring agreement.
⚠ It does mean R1's `u64` is NOT observable on these two inputs, so the
"tally collapse lands in the checksum" evidence (`PROTOCOL_PHP.md` §B1.2) comes
from `../controls/allocator.py`, which runs the same kernel at a `navail` the
heap survives and prints `bytes_mallocked = 0` beside `bytes_requested =
18446744069414584320`.
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

HEAD = 12                     # bytes before the datagram
LONG_MAX = (1 << 63) - 1

#: zend_alloc.h:63-64 -- MAX_CACHED_MEMORY 11, and `cache_index = real_size >> 3`
#: (zend_alloc.c:136), so a block with `real_size <= 87` is CACHED on free and
#: never returned to `malloc`. The benign corpus must straddle this.
CACHE_MAX_REAL = 87

#: A benign window may not ask for more than this. It bounds the driver loop's
#: RSS and, more importantly, keeps `php_shim_emalloc`'s NULL arm -- the
#: projection of `zend_alloc.c:189`'s `exit(1)` -- unreachable in the measured
#: corpus, so no measured cell can take a path the Rust rungs do not model.
MAX_BENIGN_REAL = 1 << 16

SMALL_STRIDE, SMALL_WINS = 550, 32
LARGE_STRIDE, LARGE_WINS = 4076, 2050

#: The two adversarial `to_read` values, one on each side of "does this need the
#: allocator shim?".
TR_TRUNC = -4294967297        # size = 2^64 - 2^32; plain malloc REFUSES it
TR_NEG = -1                   # size = 0;           plain malloc(0) succeeds
ADV_WANT = 4                  # navail; see the module docstring


def real_size_of(to_read):
    """`zend_alloc.c:129`/`:135` -- T1, and the store is the truncation."""
    size = (to_read + 1) & ((1 << 64) - 1)
    return ((size + 7) & ~7) & 0xFFFFFFFF


def recorded_size_of(to_read):
    """`zend_alloc.h:53` -- T2, `unsigned int size:31`."""
    size = (to_read + 1) & ((1 << 64) - 1)
    return (size & 0xFFFFFFFF) & 0x7FFFFFFF


def i64(v):
    return (v & ((1 << 64) - 1)).to_bytes(8, "little")


def u16(v):
    return bytes((v & 0xFF, (v >> 8) & 0xFF))


def unpack(win):
    """(to_read, ctl, want, navail, n_pay) -- the inverse of `window()`."""
    tr = int.from_bytes(win[0:8], "little")
    if tr >= 1 << 63:
        tr -= 1 << 64
    ctl = win[8] | (win[9] << 8)
    want = win[10] | (win[11] << 8)
    n_pay = len(win) - HEAD
    return tr, ctl, want, want % (n_pay + 1), n_pay


def window(rng, stride, to_read, ctl, navail):
    """One window with an exact `navail`, the `%` exercised."""
    n_pay = stride - HEAD
    assert 0 <= navail <= n_pay
    want = navail + rng.randrange(0, 3) * (n_pay + 1)
    assert want <= 0xFFFF, (navail, n_pay, want)
    assert want % (n_pay + 1) == navail
    pay = bytes(rng.randrange(0, 256) for _ in range(n_pay))
    return i64(to_read) + u16(ctl) + u16(want) + pay


def rng_for(tag):
    return random.Random(SEED + sum(tag.encode()))


def tiled(rng, nwin, stride):
    """The measured corpus: `nwin` windows, arms distributed across them."""
    n_pay = stride - HEAD
    out = []
    for k in range(nwin):
        ctl = 0
        if k % 4 == 1:
            ctl |= 1                       # zremote was passed
        if k % 4 == 2:
            ctl |= 1                       # ... and again, with a different n
        if k % 11 == 5:
            ctl |= 2                       # the transport fails -> recvd = -1
        if k % 7 == 3:
            ctl |= 3                       # both

        # navail spans [0, n_pay], including both ends
        if k % 13 == 0:
            navail = 0                     # an empty datagram
        elif k % 13 == 1:
            navail = n_pay                 # a full one
        elif k % 13 == 2:
            navail = 32                    # remote_len = 32 % 32 = 0
        else:
            navail = rng.randrange(0, n_pay + 1)

        # to_read spans both sides of the size-class cache and both directions
        # of the transport's clamp
        if k % 9 == 0:
            to_read = rng.randrange(1, CACHE_MAX_REAL - 8)   # cached class
        elif k % 9 == 1:
            to_read = max(1, navail // 2)                    # to_read < navail
        elif k % 9 == 2:
            to_read = max(1, navail)                         # to_read == navail
        else:
            to_read = navail + 1 + rng.randrange(0, n_pay + 1)
        out.append(window(rng, stride, to_read, ctl, navail))
    return b"".join(out)


def one_window(stride, to_read, want=ADV_WANT, ctl=0):
    """A single-window adversarial payload: one hostile `to_read`, everything
    else ordinary."""
    rng = random.Random(SEED ^ (to_read & 0xFFFFFFFF))
    n_pay = stride - HEAD
    pay = bytes(rng.randrange(0, 256) for _ in range(n_pay))
    return i64(to_read) + u16(ctl) + u16(want) + pay


# --------------------------------------------------------------------------
# the assertion half of A2a rule 1 -- an intention in a comment is what ph03
# had, and it was wrong for a task
# --------------------------------------------------------------------------

def _check_span(name, blob, stride):
    """Refuse to write a corpus that misses an arm. Returns a list of problems."""
    bad = []
    nwin = len(blob) // stride
    if nwin == 0:
        return [f"{name}: no complete window at stride {stride}"]
    cached = uncached = False
    recv_ok = recv_fail = False
    zrem = no_zrem = False
    is_str = not_str = False
    clamp_hit = clamp_miss = False
    navail_zero = navail_full = False
    guard_fires = 0
    truncates = 0
    ub = 0
    too_big = 0
    n_win_seen = 0
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        to_read, ctl, want, navail, n_pay = unpack(win)
        n_win_seen += 1
        if to_read <= 0:
            guard_fires += 1
        if to_read == LONG_MAX:
            ub += 1
        rs = real_size_of(to_read)
        if to_read > 0 and rs != ((to_read + 1 + 7) & ~7):
            truncates += 1
        if rs > MAX_BENIGN_REAL:
            too_big += 1
        if rs <= CACHE_MAX_REAL:
            cached = True
        else:
            uncached = True
        if ctl & 1:
            zrem = True
        else:
            no_zrem = True
        if ctl & 2:
            recv_fail = True
        else:
            recv_ok = True
            n = min(navail, to_read if to_read >= 0 else navail)
            if to_read >= 0 and to_read < navail:
                clamp_hit = True
            else:
                clamp_miss = True
            if navail == 0:
                navail_zero = True
            if navail == n_pay:
                navail_full = True
            if ctl & 1:
                if (n % 32) != 0:
                    is_str = True
                else:
                    not_str = True
        # the write the kernel performs, and the block it has
        if (ctl & 2) == 0:
            n = min(navail, (to_read if to_read >= 0 else (1 << 64) + to_read))
            if n + 1 > rs:
                bad.append(f"{name}: window {k} writes {n + 1} bytes into a "
                           f"{rs}-byte block (to_read={to_read}, navail="
                           f"{navail}) -- that is an OUT-OF-BOUNDS WRITE and it "
                           f"must not be in a file the gate calls benign")
                break
    if guard_fires:
        bad.append(f"{name}: {guard_fires} of {n_win_seen} windows have "
                   f"to_read <= 0, so 445daac3ab1a's guard FIRES. ../spec.md "
                   f"pins it dead on the measured corpus, because check.py "
                   f"stage 7h requires R1h == R1 on every non-adversarial input")
    if ub:
        bad.append(f"{name}: {ub} window(s) carry to_read == LONG_MAX, whose "
                   f"`to_read + 1` is signed-overflow UB (RECAP_PHP.md F46)")
    if truncates:
        bad.append(f"{name}: {truncates} window(s) truncate at zend_alloc.c:135")
    if too_big:
        bad.append(f"{name}: {too_big} window(s) ask for more than "
                   f"{MAX_BENIGN_REAL} bytes; the measured corpus must keep "
                   f"php_shim_emalloc's NULL arm unreachable")
    if not (cached and uncached):
        bad.append(f"{name}: the corpus does not straddle the size-class cache "
                   f"(real_size <= {CACHE_MAX_REAL}: {cached}, above: "
                   f"{uncached}) -- one side of zend_alloc.c:270-279 is never "
                   f"taken, and that branch is what PROTOCOL_PHP.md B1.1 is about")
    if not (recv_ok and recv_fail):
        bad.append(f"{name}: `if (recvd >= 0)` at :328 takes only one arm "
                   f"(ok: {recv_ok}, fail: {recv_fail}) -- the failing arm is "
                   f"where 5.0.0 LEAKS read_buf")
    if not (zrem and no_zrem):
        bad.append(f"{name}: `if (zremote)` at :315 takes only one arm "
                   f"(passed: {zrem}, absent: {no_zrem})")
    if not (is_str and not_str):
        bad.append(f"{name}: `if (zremote && Z_STRLEN_P(zremote))` at :329 "
                   f"takes only one arm (non-zero: {is_str}, zero: {not_str})")
    if not (clamp_hit and clamp_miss):
        bad.append(f"{name}: the transport's clamp takes only one arm "
                   f"(to_read < navail: {clamp_hit}, to_read >= navail: "
                   f"{clamp_miss}) -- transports.c:406-407")
    if not (navail_zero and navail_full):
        bad.append(f"{name}: navail does not reach both ends (0: {navail_zero}, "
                   f"n_pay: {navail_full})")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    path = os.path.join(HERE, name)
    payload = slb.pack_head1_bytes(stride, body)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"blob={len(body):<9d} windows={len(body) // stride if stride else 0:<6d} "
          f"file={os.path.getsize(path)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()

    for mod in (4, 8, 16):
        if SMALL_STRIDE % mod == LARGE_STRIDE % mod:
            print(f"REFUSING TO WRITE: strides {SMALL_STRIDE}/{LARGE_STRIDE} "
                  f"are both == {SMALL_STRIDE % mod} mod {mod}")
            return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          f"4, 8 and 16")

    small = tiled(rng_for("small"), SMALL_WINS, SMALL_STRIDE)
    large = tiled(rng_for("large"), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    if problems:
        print("REFUSING TO WRITE -- the corpus misses an arm "
              "(PROTOCOL_PHP.md A2a rule 1):")
        for p in problems:
            print(f"    {p}")
        return 1
    print("  arm coverage ok on both measured inputs")

    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 12_000, LARGE_STRIDE, large)

    # ---- the adversarial four -------------------------------------------
    # n_iters is small: R1 writes out of bounds on every one of these calls and
    # there is nothing to be learned from doing it 25 000 times.
    #
    # (1) THE ROW. `to_read + 1` is 2^64 - 2^32, `REAL_SIZE` truncates it to 0,
    #     and the receive overflows a header-sized block. Under plain `malloc`
    #     the request FAILS and there is no defect at all.
    write("adversarial-trunc.bin", 64, SMALL_STRIDE,
          one_window(SMALL_STRIDE, TR_TRUNC))
    # (2) its control, and it differs in `to_read` alone: `emalloc(0)` also
    #     truncates to a header-sized block, but `malloc(0)` succeeds, so this
    #     one overflows under EITHER allocator. It is the value
    #     445daac3ab1a's own subject describes ("a negative value").
    write("adversarial-neg.bin", 64, SMALL_STRIDE,
          one_window(SMALL_STRIDE, TR_NEG))
    # (3) the control for both: a stride larger than the blob, so the driver
    #     skips the loop and makes NO kernel call at all. If this one ever
    #     showed a diagnostic, the diagnostic would not be coming from the
    #     kernel.
    write("adversarial-nowin.bin", 64, SMALL_STRIDE + 64,
          one_window(SMALL_STRIDE, TR_TRUNC))
    # (4) a file whose declared payload length exceeds the bytes present. The
    #     driver must notice and exit 5 rather than read past the end; nothing
    #     about ph29 is involved and that is the point.
    body = one_window(SMALL_STRIDE, TR_TRUNC)
    write("adversarial-short.bin", 64, SMALL_STRIDE, body,
          declared_len=8 + len(body) + 4096)
    return 0


if __name__ == "__main__":
    sys.exit(main())
