#!/usr/bin/env python3
"""Generate ph07's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`).

    python3 patterns-php/ph07-strcut-cursor/inputs/gen.py

Payload layout (../spec.md):

    word 0     u64  stride     bytes per window; the kernel cuts one window
    byte 8..   u8[] blob       windows; n_blob = payload_len - 8

A *window* is one `mb_strcut($s, $from, $length)` call, laid out the way the
arguments reach `mbfl_strcut`:

    byte 0..3    i32 LE  from        <- mbstring.c:1779, attacker-controlled
    byte 4..7    i32 LE  length      <- mbstring.c:1782, attacker-controlled
    byte 8..     u8[]    the string  <- mbstring.c:1775, Z_STRVAL_PP(arg1)
    last byte    0x00                <- THE ZVAL TERMINATOR

so `slen = stride - 9`.

⚠⚠⚠ **THE TRAILING NUL IS PART OF THE MODEL, NOT PADDING.** Every PHP string
is `emalloc(len + 1)` with `val[len] == '\\0'`, and this row's fix turns on it:
`cb3cca21b345` refuses `from > string->len` and so ADMITS `from == string->len`
-- and that is safe only because a walk that reaches `val[len]` finds
`mblen_table_utf8[0] == 1` there and steps past `from`. (The 2010 in-library
restoration `d9dda48f8a7e` clamps to `string->len` rather than to
`string->len - 1` for the same reason.) A fixture that omitted the terminator
would make both upstream guards look wrong by one byte. c/kernel.h says the
same thing from the kernel's side.

⚠⚠ **THE ARMS THIS CORPUS MUST REACH, AND `_check_span()` REFUSES TO WRITE A
CORPUS THAT DOES NOT** (`PROTOCOL_PHP.md` §A2a rule 1). The defect lives on
`m = mbtab[*p]`, whose arms are the LEAD-BYTE CLASSES, and on
`if (k >= (int)string->len)`, which is the *guarded* walk's branch:

  * every one of the six distinct `mblen_table_utf8` step sizes -- 1, 2, 3, 4,
    5 and 6 -- is stepped on by some window's start walk. An all-ASCII corpus
    takes `m == 1` on every byte, and with `m == 1` the cursor can never
    overshoot: it is ph03's monoculture with a different name, and
    `PROTOCOL_PHP.md` §A2a names this row as the case it was checked against;
  * both arms of `k >= (int)string->len` -- the bounded end walk and the
    `end = string->len` shortcut;
  * both `start == from` (the cut lands on a character boundary) and
    `start < from` (the cursor stepped over `from` and the cut moved left),
    which is the semantic difference the start walk exists to compute;
  * at least one window with `from == string->len` exactly -- the largest
    `from` R1h admits (its guard is `from > len`, not `>=`) and the only benign
    value at which the walk reads the zval terminator;
  * NO window on which R1h's guard -- `cb3cca21b345` hunk (a), `from > len ->
    RETURN_FALSE` -- fires. That is the ADVERSARIAL case, and keeping it out of
    the measured corpus is what "benign" means here; it is not a restriction on
    the domain. R1h is byte-identical to R1 on every measured input;
  * ⭐ and, since `TASK_PHP_018`, windows with `from + length > string->len`
    MUST BE PRESENT -- with a second, sharper assertion that some of them are
    windows on which the WITHDRAWN hunk (b) would have changed the answer.
    ⚠⚠ **This requirement is the inverse of the one that stood here until
    `TASK_PHP_018`**, which read *"NO window on which EITHER guard fires"*.
    Upstream removed hunk (b) in `c2471b495009` (2009-09-23) as **bug #49354,
    with a regression test**, and R1h is now the configuration upstream kept --
    hunk (a) alone, `php-5.2.12 .. php-5.2.17`. So the region hunk (b) used to
    clamp is ordinary benign input again, and a fixture that still avoided it
    would be measuring 86.5 % of the domain while claiming the whole of it.
    `controls/bug49354.py` is upstream's own test for this region.

Four things about the sizes are deliberate.

  * **`small` and `large` have different strides** -- 553 and 4074 -- and they
    are in different residue classes mod 4, 8 and 16. `work_per_call` *is* the
    stride, so `harness/check.py`'s `d(Ir)/d(work)` assertion needs two probe
    shapes with different `work_per_call` or it cannot run at all; and the
    safe-vs-unsafe delta varies with the residue of the measured length
    (`.memory/01-ladder.md`). `_check_residues()` asserts both.
  * **the strides are not powers of two** (553 = 7*79, 4074 = 2*3*7*97), so
    consecutive windows do not share a cache-set alignment.
  * ⚠ **`from` and `length` are drawn as FIXED FRACTIONS of `slen`**, not as
    absolute byte counts. The work a call does is `from` steps of the start
    walk plus up to `length` of the end walk plus `end - start` copied bytes,
    so fractions are what make the work scale with the window and
    `work_per_call = stride` a real denominator rather than a label.
  * ⚠ **`start + length` is asserted to stay inside `int`.** `mbfilter.c:1212`
    is `k = start + length` on two `int`s, and a `length` near `INT_MAX`
    overflows it -- a SECOND, DISTINCT defect, fixed upstream in 2016 by
    `f8dd10508bd6` / `64f42c73efc5` (bug #71906) and deliberately out of this
    row's scope. R1h does not guard it either, so an input that reached it
    would trip UBSan on the hardened rung and `check.py` stage 7h would
    hard-fail. NOTES.md §9.

⚠⚠ **THE FIVE ADVERSARIAL FILES ARE THE ROW.** Four of them have exactly ONE
window and NO slack, so the first byte the start walk reads past `val[slen]` is
also the first byte past the blob's heap block, which is what makes a detector
fire; the fifth (`-nowin`) makes no kernel call at all and is their control.
⚠ Read `adversarial-offbyone` and `adversarial-silent` together: they differ in
the shape of the LAST CHARACTER and in nothing else, and that difference is
whether the over-read changes the answer.
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

# ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56, as a run-length. The
# model re-derives the same 256 numbers out of c/kernel.c's literal text.
MBTAB = tuple(([1] * 192) + ([2] * 32) + ([3] * 16)
              + ([4] * 8) + ([5] * 4) + ([6] * 2) + ([1] * 2))

# One lead byte per step size the table has. `LEADS[m]` is a byte `b` with
# `MBTAB[b] == m`; the assertion below is the check, not the comment.
LEADS = {1: 0x41, 2: 0xC3, 3: 0xE3, 4: 0xF0, 5: 0xF8, 6: 0xFC}
assert all(MBTAB[b] == m for m, b in LEADS.items())
CONT = 0x80                        # a continuation byte; never read as a lead

HEAD = 8                           # the two i32 words
SMALL_STRIDE, SMALL_WINS = 553, 32
LARGE_STRIDE, LARGE_WINS = 4074, 2050
RESIDUE_MODULI = (4, 8, 16)

# (from, length) as fractions of `slen`, cycled by window index. Chosen so that
# every one of `_check_span`'s assertions passes -- see the module docstring.
#
# ⚠⚠⚠ **THE SUMS RUN PAST 1, AND THAT IS THE `TASK_PHP_018` CHANGE.** Until
# then this table read *"EVERY PAIR SUMS TO AT MOST 1, AND THAT IS A
# REQUIREMENT, NOT A TASTE"*, because R1h carried `cb3cca21b345` hunk (b) --
# which fires exactly when `from + length > string->len`, SHORTENS `length`,
# and can move `k = start + length` out of the `k >= string->len` shortcut into
# the bounded end walk, returning a shorter cut on an input that never crashed.
# `check.py` stage 7h refused that, correctly.
#
# ⭐⭐ **UPSTREAM REACHED THE SAME VERDICT AND ACTED ON IT.** `c2471b495009`
# (Moriyoshi Koizumi, 2009-09-23) DELETED hunk (b) as **bug #49354** --
# *"mb_strcut() cuts wrong length when offset is within a multibyte
# character"* -- and shipped `ext/mbstring/tests/bug49354.phpt` with it. R1h is
# now the configuration upstream KEPT (hunk (a) alone, `php-5.2.12 ..
# php-5.2.17`), so the region below the old ceiling and the region above it are
# both ordinary benign input, and the ceiling goes. `controls/bug49354.py`
# replays upstream's six expectations against all three configurations.
#
# ⭐ Entry 6 is `from == slen, length == 0`: the largest `from` R1h admits (its
# guard is `from > len`, not `>=`) and the only benign window whose walk reads
# the zval terminator.
# ⭐ Entries 8 and 9 are the two `TASK_PHP_018` added: sums 1.15 and 1.30,
# continuing the spacing of the eight above rather than jumping. Entry 8's
# `length == slen` is upstream's own regression-test shape -- `bug49354.phpt`
# calls `mb_strcut($crap, k, 100)` on a 12-byte string, i.e. `length` far past
# the end. Measured over both shipped corpora, they put **20.0 %** of windows in
# the newly admitted region and **14.5 %** on windows where hunk (b) would have
# changed the answer -- against `controls/fix_scope.py` Q2's independent
# **13.5 %** over a uniform sweep, which is the cross-check that the fixture is
# not over- or under-weighting the region it just re-admitted.
FRACTIONS = (
    (0.00, 0.25),
    (0.10, 0.30),
    (0.25, 0.50),
    (0.50, 0.45),
    (0.33, 0.33),
    (0.75, 0.10),
    (1.00, 0.00),
    (0.60, 0.40),
    (0.15, 1.00),          # sum 1.15  <- TASK_PHP_018
    (0.80, 0.50),          # sum 1.30  <- TASK_PHP_018
)


def rng_for(name):
    """One INDEPENDENT stream per output file, so that an edit to `small`'s
    shape does not silently rewrite every adversarial blob. (`random.seed` on a
    `str` hashes it with sha512, so this is stable across interpreters.)"""
    return random.Random(f"{SEED:x}:{name}")


def make_body(rng, slen):
    """`slen` bytes of well-formed multibyte text, NO terminator.

    Characters are emitted whole -- a lead byte for a class `m` followed by
    `m - 1` continuation bytes -- so both walks always land on character
    boundaries, which is what real text does and what makes `start == from`
    versus `start < from` a property of where the cut falls rather than of a
    malformed string. The tail is padded with single-byte characters when
    fewer than `m` bytes remain, so **`slen` is always a boundary**."""
    out = bytearray()
    classes = list(LEADS)
    while len(out) < slen:
        room = slen - len(out)
        choices = [m for m in classes if m <= room]
        m = rng.choice(choices)
        out.append(LEADS[m] + rng.randrange(2))
        out += bytes(CONT + rng.randrange(0x40) for _ in range(m - 1))
    assert len(out) == slen
    return bytes(out)


def make_string(rng, slen):
    """`make_body` plus the zval terminator at index `slen`."""
    return make_body(rng, slen) + b"\0"


def window(rng, stride, idx):
    slen = stride - HEAD - 1
    ff, lf = FRACTIONS[idx % len(FRACTIONS)]
    frm = int(round(slen * ff))
    # ⚠⚠ **THE `min(..., slen - frm)` THAT USED TO BE HERE IS GONE**
    # (`TASK_PHP_018`). It clamped `length` so that `from + length <= slen` and
    # hunk (b) could never fire. ⚠ Measured before deleting it
    # (`.temp/php18/fractions.log`): over the eight shipped FRACTIONS entries it
    # **never once fired** -- clamped and unclamped give byte-identical corpora
    # -- so the restriction was carried by the FRACTIONS table alone and this
    # line was belt-and-braces. It is deleted anyway, because a dead clamp that
    # would silently re-impose the old domain the moment somebody added a
    # fraction pair is exactly the failure mode this task exists to remove.
    # `frm <= slen` still holds by construction (no `ff` exceeds 1.00), which is
    # what keeps R1h's ONE guard dead on the measured corpus.
    length = int(round(slen * lf))
    assert 0 <= frm <= slen and 0 <= length
    body = make_string(rng, slen)
    win = (frm.to_bytes(4, "little", signed=True)
           + length.to_bytes(4, "little", signed=True) + body)
    assert len(win) == stride, (len(win), stride)
    return win


def tiled(rng, nwin, stride):
    return b"".join(window(rng, stride, i) for i in range(nwin))


def _walk_stats(win):
    """(classes stepped on, start, from, k_ge_len, oob) for one window.

    A deliberately SEPARATE transcription of the two walks -- `gen.py` must be
    able to assert what it generated without importing the model it generates
    for (and `../model.py` binds a different `slb` than this file does, so
    importing it would be wrong twice over). It counts; it does not cut."""
    frm = int.from_bytes(win[0:4], "little", signed=True)
    length = int.from_bytes(win[4:8], "little", signed=True)
    s = win[HEAD:]
    slen = len(s) - 1
    classes, n, start, oob = set(), 0, 0, False
    while True:
        if n > slen:
            oob = True
            break
        m = MBTAB[s[n]]
        classes.add(m)
        n += m
        if n > frm:
            break
        start = n
    return (classes, start, frm, (start + length >= slen), oob,
            start + length, length)


def _cut(win, hunk_b):
    """`(start, end)` for one window under R1h, with `cb3cca21b345` hunk (b)
    applied or not -- or `None` if hunk (a) refuses the window or the walk would
    leave the buffer, which are the two cases where "the cut" is not defined.

    ⭐ `TASK_PHP_018`: this is what turns *"the corpus now contains windows
    with `from + length > string->len`"* -- true but weak, because most such
    windows take the `k >= string->len` shortcut under BOTH configurations and
    answer identically -- into *"the corpus contains windows on which the
    WITHDRAWN hunk (b) would have returned a different cut"*, which is the arm
    upstream's own regression test `bug49354.phpt` exercises.

    Deliberately a fourth transcription of the walks, like `_walk_stats`:
    `gen.py` must be able to assert what it generated without importing
    `../model.py` (which binds a different `slb`)."""
    frm = int.from_bytes(win[0:4], "little", signed=True)
    length = int.from_bytes(win[4:8], "little", signed=True)
    s = win[HEAD:]
    slen = len(s) - 1
    if frm > slen:
        return None                       # cb3cca21b345 hunk (a): RETURN_FALSE
    if hunk_b and frm + length > slen:
        length = slen - frm
    n = start = 0
    while True:
        if n > slen:
            return None                   # R1's over-read; no defined cut
        m = MBTAB[s[n]]
        n += m
        if n > frm:
            break
        start = n
    k = start + length
    if k >= slen:
        end = slen
    else:
        end = start
        while n <= k:
            end = n
            if n > slen:
                return None
            n += MBTAB[s[n]]
    start = min(max(start, 0), slen)
    end = min(max(end, 0), slen)
    return (min(start, end), end)


def _check_residues():
    """The two measured strides must differ modulo every modulus that has
    bitten this project. p01's first draft used 500 and 4096, both == 0 (mod
    4), the single worst residue for R2, and overstated the delta 2.4x."""
    bad = []
    for m in RESIDUE_MODULI:
        if SMALL_STRIDE % m == LARGE_STRIDE % m:
            bad.append(f"small and large strides ({SMALL_STRIDE}, "
                       f"{LARGE_STRIDE}) are both == {SMALL_STRIDE % m} "
                       f"(mod {m}); pick strides of different parity or the "
                       f"delta published is one residue wearing the label of a "
                       f"constant")
    return bad


def _check_span(name, blob, stride):
    """⚠⚠⚠ THE MUST-FIRE ASSERTION -- `PROTOCOL_PHP.md` §A2a rule 1.

    A benign corpus must REACH every arm of the branch the defect lives on and
    must SAY SO mechanically. Refuses to write a corpus that misses any of:

      * a lead-byte class -- all six of `mblen_table_utf8`'s step sizes;
      * either arm of `if (k >= (int)string->len)` (mbfilter.c:1213);
      * either of `start == from` / `start < from`;
      * a window with `from == string->len` exactly;
      * ⭐ (`TASK_PHP_018`) windows with `from + length > string->len`, AND
        windows in that region on which the WITHDRAWN hunk (b) would have
        returned a DIFFERENT cut -- the arm `bug49354.phpt` exercises;

    and refuses one on which R1h's guard (hunk (a), `from > len`) fires -- that
    is the adversarial case, not a measured one -- or one that over-reads (a
    benign input must be clean on R1 too), or whose `start + length` leaves
    `int` (bug #71906's territory, out of scope -- module docstring).
    """
    seen, kge, klt, exact, over, atlen, oob, maxk = set(), 0, 0, 0, 0, 0, 0, 0
    hunk_a_fires = over_sum = hunk_b_moves = 0
    for i in range(len(blob) // stride):
        win = blob[i * stride:(i + 1) * stride]
        cls, start, frm, k_ge, is_oob, k, length = _walk_stats(win)
        if frm > stride - 9:
            hunk_a_fires += 1
        if frm + length > stride - 9:
            over_sum += 1
            a, b = _cut(win, False), _cut(win, True)
            if a is not None and b is not None and a != b:
                hunk_b_moves += 1
        seen |= cls
        kge += k_ge
        klt += not k_ge
        exact += (start == frm)
        over += (start < frm)
        atlen += (frm == stride - 9)
        oob += is_oob
        maxk = max(maxk, k)
    bad = []
    missing = sorted(set(LEADS) - seen)
    if missing:
        bad.append(f"{name}: no window's start walk ever takes a step of size "
                   f"{missing} -- the corpus does not reach every arm of "
                   f"`m = mbtab[*p]`, which is the branch the defect lives on")
    if not kge:
        bad.append(f"{name}: no window takes `k >= (int)string->len` at "
                   f"mbfilter.c:1213")
    if not klt:
        bad.append(f"{name}: no window takes the BOUNDED end walk at "
                   f"mbfilter.c:1216-1222 -- the guard this row contrasts the "
                   f"start walk against is never executed")
    if not exact:
        bad.append(f"{name}: no window has `start == from`; every cut lands "
                   f"mid-character and the boundary case is untested")
    if not over:
        bad.append(f"{name}: no window has `start < from`; the cursor never "
                   f"steps OVER `from`, which is the whole reason the walk is "
                   f"not `start = from`")
    if not atlen:
        bad.append(f"{name}: no window has `from == string->len`, the value "
                   f"d9dda48f8a7e clamps to and the only benign value whose "
                   f"walk reads the zval terminator")
    if oob:
        bad.append(f"{name}: {oob} window(s) make R1 read past val[slen]; a "
                   f"MEASURED input must be benign on every rung")
    if hunk_a_fires:
        bad.append(f"{name}: {hunk_a_fires} window(s) make R1h's guard -- "
                   f"cb3cca21b345 hunk (a), `from > string->len` -> "
                   f"RETURN_FALSE -- fire. That is the ADVERSARIAL case; "
                   f"check.py stage 7h requires R1h == R1 on every "
                   f"non-adversarial input, and a window R1h refuses is a "
                   f"window R1 over-reads on. inputs/adversarial-*.bin is "
                   f"where those live")
    if not over_sum:
        bad.append(f"{name}: NO window has `from + length > string->len`. "
                   f"⭐ TASK_PHP_018 REVERSED THIS ASSERTION: R1h is now hunk "
                   f"(a) alone -- the configuration upstream converged on after "
                   f"c2471b495009 removed hunk (b) as bug #49354 -- so that "
                   f"region is ordinary benign input and a corpus that avoids "
                   f"it measures 86.5 % of the domain while claiming all of it")
    if not hunk_b_moves:
        bad.append(f"{name}: {over_sum} window(s) have `from + length > "
                   f"string->len` but NONE of them is a window on which the "
                   f"withdrawn hunk (b) would have returned a different cut. "
                   f"Most of that region takes the `k >= string->len` shortcut "
                   f"under both configurations and answers identically, so the "
                   f"weaker assertion above can pass on a corpus that still "
                   f"never reaches the arm bug49354.phpt exercises")
    if maxk >= 2 ** 31:
        bad.append(f"{name}: max start+length = {maxk} overflows the `int` at "
                   f"mbfilter.c:1212 -- that is bug #71906 and is out of scope")
    print(f"  span ok: {name:24s} windows={len(blob)//stride:<6d} "
          f"steps={sorted(seen)} k>=len={kge:<5d} k<len={klt:<5d} "
          f"start==from={exact:<5d} start<from={over:<5d} from==len={atlen} "
          f"hunk(a)-fires={hunk_a_fires} from+len>len={over_sum} "
          f"hunk(b)-would-move={hunk_b_moves}")
    return bad


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def adversarial(rng, slen, frm, length, tail="whole"):
    """One window, no slack. `stride == n_blob`, so `nwin == 1`, the driver's
    window index is always 0, and the window is the last thing in the
    `malloc(n_blob)` the driver made -- so R1's first read past `val[slen]` is
    also its first read past the heap block.

    `tail` decides whether the LAST character is complete, and it is the only
    thing separating the two off-by-one cells:

      "whole"     `slen` is a character boundary. R1 over-reads and R1h does
                  not, and **they return the same answer**;
      "truncated" the string ends three bytes into a four-byte character, so
                  `slen` is NOT a boundary. R1 over-reads AND returns a
                  different answer.
      "ascii"     one-byte characters throughout -- the "whole" case with the
                  cursor never able to overshoot at all."""
    if tail == "ascii":
        body = bytes(0x41 + (i % 26) for i in range(slen))
    elif tail == "truncated":
        body = make_body(rng, slen - 3) + bytes([LEADS[4], CONT, CONT])
    else:
        body = make_body(rng, slen)
    assert len(body) == slen
    return (frm.to_bytes(4, "little", signed=True)
            + length.to_bytes(4, "little", signed=True) + body + b"\0")


def main():
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    print("ph07 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    # small: 32 windows x 553 B = 17.3 KiB, inside this box's 32 KiB L1.
    small = tiled(rng_for("small"), SMALL_WINS, SMALL_STRIDE)
    # large: 2050 windows x 4074 B = 8.0 MiB, 8x this box's 1 MiB L2, so the
    # window the driver picks is a cold walk every call.
    large = tiled(rng_for("large"), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    for p in problems:
        print("gen.py: " + p, file=sys.stderr)
    if problems:
        return 1
    write("small.bin", 25_000, SMALL_STRIDE, small)
    write("large.bin", 12_000, LARGE_STRIDE, large)

    # ---- adversarial: `from` past the end is the attack --------------------
    # n_iters is small: R1 executes undefined behaviour on three of these and
    # there is nothing to learn from doing it 25 000 times.

    # (1) THE ROW'S OWN TRIGGER, `mb_strcut($s, strlen($s) + 1, 1)`. `from` is
    #     ONE past the string. The walk reads `val[slen]` (the terminator, in
    #     bounds), finds `mbtab[0] == 1`, sets `n = slen + 1`, tests
    #     `n > from` -- slen+1 > slen+1 is FALSE -- and goes round once more,
    #     reading `val[slen + 1]`, which is one byte past the heap block.
    #     ⚠ The last character is TRUNCATED, so `slen` is not a boundary and
    #     R1 and R1h disagree in VALUE as well: R1's `start` ends past `slen`
    #     and clamps to `slen` (an empty cut) where R1h stops on the last
    #     boundary before it and returns three bytes.
    win = adversarial(rng_for("adv1"), 96, 96 + 1, 4, tail="truncated")
    write("adversarial-offbyone.bin", 8, len(win), win)

    # (2) ⭐ THE SAME DEFECT, SILENT. All-ASCII, so every step is 1 and `slen`
    #     is a boundary; R1 reads `val[slen + 1]` exactly as in (1) and then
    #     **returns byte-for-byte what R1h returns.** This cell exists because
    #     it is the row's explanation: an over-read whose result is invisible
    #     to the caller is one no test suite can see, and this one shipped
    #     byte-identical in six releases. NOTES.md §6.
    win = adversarial(rng_for("adv2"), 96, 96 + 1, 4, tail="ascii")
    write("adversarial-silent.bin", 8, len(win), win)

    # (3) THE SAME DEFECT, RUN OUT. `from = slen + 24`, so the walk keeps going
    #     for another ~24 bytes of whatever follows the block. It is here to
    #     show the over-read is bounded only by `from`; 24 keeps it inside the
    #     malloc arena so the non-sanitizer cells stay reproducible.
    #     ⚠ Its RETURN VALUE is still deterministic, and that is a proved
    #     property rather than an accident -- model.py::_r1_reads_oob's
    #     docstring has the argument, NOTES.md §6 has the consequence.
    win = adversarial(rng_for("adv3"), 96, 96 + 24, 8)
    write("adversarial-wild.bin", 8, len(win), win)

    # (4) THE SMALLEST INSTANCE THERE IS: the EMPTY string. `slen = 0`, so
    #     `string->val` is a one-byte allocation holding only the terminator,
    #     `stride` is 9, and `from = 1` is enough. `.temp/php16/02-reach.log`
    #     finds this as the first over-reading call in the whole interpreted
    #     space, and it is the case that shows the clamp has to be
    #     `from = string->len` and not `string->len - 1`.
    win = (1).to_bytes(4, "little", signed=True) \
        + (1).to_bytes(4, "little", signed=True) + b"\0"
    assert len(win) == 9, len(win)
    write("adversarial-empty.bin", 8, len(win), win)

    # (5) The degenerate shape: `stride > n_blob`, so the driver's guard skips
    #     the loop entirely rather than entering and breaking out of it (which
    #     would put a branch in the measured loop). Every rung prints 0 after
    #     zero kernel calls. This is the control for (1)-(3): the same driver,
    #     the same blob shape, no kernel call at all, declared clean.
    win = adversarial(rng_for("adv4"), 64, 0, 8)
    write("adversarial-nowin.bin", 8, len(win) + 1, win)
    return 0


if __name__ == "__main__":
    sys.exit(main())
