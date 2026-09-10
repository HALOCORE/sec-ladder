#!/usr/bin/env python3
"""Generate ph16's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph16-fdset-index/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel runs one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is one `stream_select($r, $w, $e, $sec)` call, laid out the way the
three stream arrays reach `stream_array_to_fd_set`:

    byte 0..1    u16 LE  ctl        <- which arrays are NULL / not arrays
    byte 2..3    u16 LE  split_r    <- n_r = split_r % (m + 1)
    byte 4..5    u16 LE  split_w    <- n_w = split_w % (m - n_r + 1)
    byte 6..     u16 LE  e[m]       <- m = (stride - 6) / 2 entries

and one entry `e` is

    bits 15..14  tag    0 -> php_stream_from_zval_no_verify() yields NULL
                        1 -> php_stream_cast() returns FAILURE
                        2 -> php_stream_cast() returns SUCCESS
                        3 -> ditto; a SECOND success encoding, so that a rung
                             testing `tag == 2` rather than `tag >= 2` is wrong
    bits 13..0   idx    what php_stream_cast writes through its out-parameter,
                        i.e. `this_fd` at streamsfuncs.c:541

⚠⚠⚠ **THE INDEX IS THE WHOLE ROW AND IT IS 14 BITS ON PURPOSE.** `FD_SETSIZE`
is 1024 and `sizeof(fd_set)` is 128 bytes = 16 words, so an index of 2048
writes at byte offset 256 -- 128 bytes past the object, in the middle of the
NEXT `fd_set` in `PHP_FUNCTION(stream_select)`'s frame. 14 bits reaches 16 383,
i.e. 2 040 bytes past, which is far enough to leave the frame entirely. The
benign corpus stays strictly below 1024 and `_check_span()` refuses to write one
that does not.

⚠ **NEGATIVE `this_fd` IS OUT OF THIS ROW'S CONTRACT** and the tag/index split
is why: `FD_SET(-1, &fds)` is `1UL << -1`, a shift by a negative count, which is
undefined behaviour in the SHIFT rather than the out-of-bounds WRITE this row
models. `99e290f882c9`'s guard (a), `&& this_fd >= 0`, is therefore DEAD here;
../spec.md says so and `controls/fix_scope.py` measures it rather than asserting
it.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_span()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1). The defect lives on
`if (SUCCESS == php_stream_cast(...))` and on the *absence* of a test on
`this_fd`, so the arms are:

  * all three entry tags -- `stream == NULL`, cast FAILURE, cast SUCCESS -- and
    BOTH success encodings (2 and 3);
  * both directions of `if (this_fd > *max_fd)`, i.e. some window whose indices
    do not increase monotonically. A monotone corpus takes the true arm every
    time and would hide a rung that dropped the test;
  * each of the three arrays NULL in some window (`stream_select`'s
    `if (r_array != NULL)`), and each of them non-NULL-but-not-an-array in some
    window (`stream_array_to_fd_set`'s `Z_TYPE_P(...) != IS_ARRAY -> return 0`);
  * at least one window with `sets == 0`, i.e. the `RETURN_FALSE` arm at
    `:675-677`, and at least one with `sets == 3`;
  * at least one window in which some array is EMPTY (`n_r`, `n_w` or `n_e`
    zero) and at least one in which all three are non-empty;
  * index 0 and index 1023 -- the two ends of the benign domain, 1023 being the
    largest `this_fd` `PHP_SAFE_FD_SET` admits (its test is `<`, not `<=`);
  * ⚠ and, NEGATIVELY, **NO window on which any of `99e290f882c9`'s three
    guards fires.** That is the ADVERSARIAL case, and keeping it out of the
    measured corpus is what "benign" means here: R1h is byte-identical to R1 on
    every measured input, which is what `check.py` stage 7h requires and what
    makes the R1-vs-R1h cost comparison a comparison between two runs of one
    program.

⚠ **THIS IS A SUPERSET CONDITION AND `model.py` CARRIES THE SHARPER ONE.**
`_check_span` asserts over EVERY window in the file; the driver picks windows
from a checksum-derived index and need not visit them all, so
`model.py::selfcheck` check 2 re-asserts the same arm table over **the calls the
driver actually makes**. Both are needed: this one can be run without a model,
that one is the one that is true of the measurement.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 550 and 4076 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all.
  * **the strides are not powers of two** (550 = 2*5^2*11, 4076 = 2^2*1019), so
    consecutive windows do not share a cache-set alignment.
  * ⚠ **the number of entries scales with the stride**: `m = (stride - 6) / 2`,
    so the per-call work really does scale with `work_per_call` rather than
    being a constant with a label. The three `FD_ZERO`s and the 48-word fold
    are a FIXED per-call term that does not scale, and ../NOTES.md §8
    decomposes the marginal rather than pretending it is a pure walk rate.
  * **`split_r` and `split_w` are written with a random multiple of `m + 1`
    added**, so the `%` in the kernel is exercised rather than being the
    identity on every window.

⚠⚠ **THE FOUR ADVERSARIAL FILES ARE THE ROW.** Three of them have exactly ONE
window, so the driver makes `n_iters` identical calls and the first
out-of-range `FD_SET` is the only interesting event; the fourth (`-nowin`)
makes no kernel call at all and is their control.
⚠ Read `adversarial-redzone` and `adversarial-silent` together: **they differ in
ONE index and in nothing else**, and that difference is whether ASan can see the
defect. Measured on this box (`.tasks-php/TASK_PHP_025_REPORT.md` §3):

    index 1024 .. 1279   byte offset 128 .. 152   ASan REPORTS stack-buffer-overflow
    index 1280 .. 3071   byte offset 160 .. 376   ASan SILENT; the write lands in
                                                  a LIVE neighbouring fd_set and
                                                  the returned u64 moves
    index >= 4096        byte offset >= 512       ASan SILENT and nothing in the
                                                  frame sees it

so the redzone on this object is exactly 32 bytes wide, and the row ships one
input on each side of that cliff.
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

FD_SETSIZE = 1024          # <sys/select.h>; c/kernel.c asserts it at compile time
NW = 16                    # sizeof(fd_set) / sizeof(long)

SMALL_STRIDE, SMALL_WINS = 550, 32
LARGE_STRIDE, LARGE_WINS = 4076, 2050

# The two adversarial indices, one on each side of ASan's 32-byte redzone.
IDX_REDZONE = 1024         # byte offset 128 -- the first word past the object
IDX_SILENT = 2048          # byte offset 256 -- inside the second neighbour


def ent(tag, idx):
    """One stream-array entry."""
    assert 0 <= tag <= 3 and 0 <= idx < 0x4000
    return ((tag << 14) | idx) & 0xFFFF


def u16(v):
    return bytes((v & 0xFF, (v >> 8) & 0xFF))


def entries_of(win):
    """(ctl, split_r, split_w, [e...]) -- the inverse of `window()`."""
    ctl = win[0] | (win[1] << 8)
    sr = win[2] | (win[3] << 8)
    sw = win[4] | (win[5] << 8)
    m = (len(win) - 6) // 2
    e = [win[6 + 2 * i] | (win[7 + 2 * i] << 8) for i in range(m)]
    return ctl, sr, sw, e


def split_of(stride, sr, sw):
    """(n_r, n_w, n_e) exactly as every rung derives it."""
    m = (stride - 6) // 2
    n_r = sr % (m + 1)
    rem = m - n_r
    n_w = sw % (rem + 1)
    return n_r, n_w, rem - n_w


def window(rng, stride, ctl, want_split=None, forced=()):
    """One benign window.

    `forced` is a list of (position, entry) pairs written after the random
    fill, so a caller can plant the exact index or tag an arm needs.
    """
    m = (stride - 6) // 2
    if want_split is None:
        n_r = rng.randrange(0, m + 1)
        n_w = rng.randrange(0, m - n_r + 1)
    else:
        n_r, n_w = want_split
    assert 0 <= n_r and 0 <= n_w and n_r + n_w <= m
    # exercise the `%` rather than leaving it the identity
    sr = n_r + rng.randrange(0, 3) * (m + 1)
    rem = m - n_r
    sw = n_w + rng.randrange(0, 3) * (rem + 1)
    assert sr <= 0xFFFF and sw <= 0xFFFF
    assert split_of(stride, sr, sw) == (n_r, n_w, m - n_r - n_w)

    es = []
    for _ in range(m):
        t = rng.choices((0, 1, 2, 3), weights=(1, 1, 5, 5))[0]
        # ⚠ strictly below FD_SETSIZE: the benign corpus never fires a guard.
        es.append(ent(t, rng.randrange(0, FD_SETSIZE)))
    for pos, e in forced:
        es[pos % m] = e
    return u16(ctl) + u16(sr) + u16(sw) + b"".join(u16(e) for e in es)


def rng_for(tag):
    return random.Random(SEED ^ (hash(tag) & 0xFFFFFFFF) if False
                         else SEED + sum(tag.encode()))


def tiled(rng, nwin, stride):
    """The measured corpus: `nwin` windows, arms distributed across them."""
    m = (stride - 6) // 2
    out = []
    for k in range(nwin):
        ctl = 0
        forced = []
        want = None
        if k % 8 == 1:
            ctl |= 1                       # r_array is NULL
        if k % 8 == 2:
            ctl |= 2                       # w_array is NULL
        if k % 8 == 3:
            ctl |= 4                       # e_array is NULL
        if k % 8 == 4:
            ctl |= 8                       # r_array is not an IS_ARRAY zval
        if k % 8 == 5:
            ctl |= 16
        if k % 8 == 6:
            ctl |= 32
        if k % 16 == 7:
            ctl |= 1 | 2 | 4               # sets == 0 -> RETURN_FALSE
        if k % 5 == 0:
            want = (m, 0)                  # w and e EMPTY, r takes everything
        if k % 5 == 1:
            want = (0, 0)                  # r and w EMPTY
        # the two ends of the benign index domain, and a descending pair so
        # `if (this_fd > *max_fd)` takes its FALSE arm
        forced.append((0, ent(2, 1023)))
        forced.append((1, ent(3, 0)))
        forced.append((2, ent(2, 900)))
        forced.append((3, ent(3, 5)))
        forced.append((4, ent(0, 777)))    # stream == NULL
        forced.append((5, ent(1, 888)))    # php_stream_cast FAILURE
        out.append(window(rng, stride, ctl, want, forced))
    return b"".join(out)


def one_window(stride, idx, tag=2):
    """A single-window adversarial payload: one out-of-range index, everything
    else ordinary. The three arrays each get a share so that whichever `fd_set`
    the platform puts lowest in the frame is written past."""
    m = (stride - 6) // 2
    rng = random.Random(SEED + idx)
    n_r = m // 3
    n_w = m // 3
    es = [ent(2, rng.randrange(0, FD_SETSIZE)) for _ in range(m)]
    es[0] = ent(tag, idx)                       # into r
    es[n_r] = ent(tag, idx)                     # into w
    es[n_r + n_w] = ent(tag, idx)               # into e
    sr, sw = n_r, n_w
    assert split_of(stride, sr, sw) == (n_r, n_w, m - n_r - n_w)
    return u16(0) + u16(sr) + u16(sw) + b"".join(u16(e) for e in es)


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
    tags = set()
    seen_idx = set()
    ctl_null = set()
    ctl_notarr = set()
    sets_seen = set()
    empty_run = False
    full_run = False
    max_fd_false = False
    guard_fires = 0
    n_ent = 0
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        ctl, sr, sw, es = entries_of(win)
        n_r, n_w, n_e = split_of(stride, sr, sw)
        if n_r + n_w + n_e != (stride - 6) // 2:
            bad.append(f"{name}: window {k} split does not partition the entries")
            break
        for b in range(3):
            if ctl & (1 << b):
                ctl_null.add(b)
            if ctl & (8 << b):
                ctl_notarr.add(b)
        if min(n_r, n_w, n_e) == 0:
            empty_run = True
        if min(n_r, n_w, n_e) > 0:
            full_run = True
        sets = sum(0 if (ctl & (1 << b)) else (0 if (ctl & (8 << b)) else 1)
                   for b in range(3))
        sets_seen.add(sets)
        # walk the three runs exactly as a rung does, and watch every arm
        pos = 0
        for b, n in enumerate((n_r, n_w, n_e)):
            run = es[pos:pos + n]
            pos += n
            if (ctl & (1 << b)) or (ctl & (8 << b)):
                continue
            mx = 0
            for e in run:
                n_ent += 1
                tags.add(e >> 14)
                if (e >> 14) >= 2:
                    fd = e & 0x3FFF
                    seen_idx.add(fd)
                    if fd >= FD_SETSIZE:
                        guard_fires += 1
                    if not fd > mx:
                        max_fd_false = True
                    mx = max(mx, fd)
            if mx >= FD_SETSIZE:
                guard_fires += 1
    if tags != {0, 1, 2, 3}:
        bad.append(f"{name}: entry tags reached {sorted(tags)}, want all of "
                   f"[0, 1, 2, 3] -- a corpus missing tag 0 or 1 never takes "
                   f"the `stream == NULL` / `php_stream_cast FAILURE` arms, and "
                   f"one missing tag 3 cannot tell `tag >= 2` from `tag == 2`")
    if 0 not in seen_idx or (FD_SETSIZE - 1) not in seen_idx:
        bad.append(f"{name}: the benign index domain's ends are not both "
                   f"present (0: {0 in seen_idx}, {FD_SETSIZE - 1}: "
                   f"{(FD_SETSIZE - 1) in seen_idx}). 1023 is the largest "
                   f"`this_fd` PHP_SAFE_FD_SET admits -- its test is `<`, not "
                   f"`<=` -- so a corpus that never reaches it never exercises "
                   f"the guard's own boundary")
    if ctl_null != {0, 1, 2}:
        bad.append(f"{name}: `stream_select`'s `if (X_array != NULL)` takes its "
                   f"false arm only for {sorted(ctl_null)}, want all three")
    if ctl_notarr != {0, 1, 2}:
        bad.append(f"{name}: `Z_TYPE_P(...) != IS_ARRAY -> return 0` is reached "
                   f"only for {sorted(ctl_notarr)}, want all three")
    if 0 not in sets_seen:
        bad.append(f"{name}: no window has `sets == 0`, so the RETURN_FALSE arm "
                   f"at streamsfuncs.c:675-677 is never taken")
    if 3 not in sets_seen:
        bad.append(f"{name}: no window has `sets == 3`, so no window fills all "
                   f"three fd_sets -- which is the shape the row is about")
    if not empty_run:
        bad.append(f"{name}: no window leaves one of the three arrays empty")
    if not full_run:
        bad.append(f"{name}: every window leaves an array empty")
    if not max_fd_false:
        bad.append(f"{name}: `if (this_fd > *max_fd)` never takes its FALSE arm "
                   f"-- the indices are monotone, so a rung that dropped the "
                   f"test entirely would agree on every window")
    if guard_fires:
        bad.append(f"{name}: {guard_fires} of {n_ent} entries would make one of "
                   f"99e290f882c9's guards FIRE. ../spec.md pins all three dead "
                   f"on the measured corpus, because check.py stage 7h requires "
                   f"R1h == R1 on every non-adversarial input and a window R1h "
                   f"refuses is one R1 writes out of bounds on")
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
    print(f"  arm coverage ok on both measured inputs")

    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 12_000, LARGE_STRIDE, large)

    # ---- the adversarial four -------------------------------------------
    # n_iters is small: R1 writes out of bounds on every one of these calls and
    # there is nothing to be learned from doing it 25 000 times.
    #
    # (1) the index ASan CAN see. Byte offset 128 -- the first word past the
    #     object -- which under -fsanitize=address is inside the 32-byte
    #     redzone ASan puts between stack objects.
    write("adversarial-redzone.bin", 64, SMALL_STRIDE,
          one_window(SMALL_STRIDE, IDX_REDZONE))
    # (2) the index ASan CANNOT see, and it differs from (1) in that number
    #     alone. Byte offset 256, which is a LIVE neighbouring fd_set -- a real
    #     object, so there is no redzone and nothing for a sanitizer to report,
    #     and the value `stream_select` returns moves anyway.
    write("adversarial-silent.bin", 64, SMALL_STRIDE,
          one_window(SMALL_STRIDE, IDX_SILENT))
    # (3) the control for both: a stride larger than the blob, so the driver
    #     skips the loop and makes NO kernel call at all. If this one ever
    #     showed a diagnostic, the diagnostic would not be coming from the
    #     kernel.
    write("adversarial-nowin.bin", 64, SMALL_STRIDE + 64,
          one_window(SMALL_STRIDE, IDX_SILENT))
    # (4) a file whose declared payload length exceeds the bytes present. The
    #     driver must notice and exit 5 rather than read past the end; nothing
    #     about ph16 is involved and that is the point.
    body = one_window(SMALL_STRIDE, IDX_SILENT)
    write("adversarial-trunc.bin", 64, SMALL_STRIDE, body,
          declared_len=8 + len(body) + 4096)
    return 0


if __name__ == "__main__":
    sys.exit(main())
