#!/usr/bin/env python3
"""ph45-htmlent-cache-int: regenerate every `.bin` in this directory.

    python3 patterns-php/ph45-htmlent-cache-int/inputs/gen.py

The `.bin` files are gitignored; this script and the fixed `SEED` are what make
them reproducible byte-for-byte. Nothing here reads `../model.py`: every
assertion below re-derives what it needs from the bytes it just emitted, so a
model bug and a fixture bug cannot cancel.

WHAT A WINDOW IS
================

    [u32 place][u32 order][ stride - 8 text bytes ]

    place = place_w & 3    bit 0 = filter A's heap region, bit 1 = filter B's
                           0 = LO (below 2^32), 1 = HI (LO + 2^32)
    order = order_w & 1    which filter is destroyed first
    text                   fed ALTERNATELY: even indices to A, odd to B

⚠⚠ `place` IS A PLATFORM PARAMETER AND NOT ATTACKER DATA, AND SAYING SO IS PART
OF THE ROW
==========================================================================
No PHP input chooses where `emalloc` puts a block. `place` lives in the window
because the harness gives a row exactly one channel -- the `.bin` -- and the row
has to be able to say *"this is 2004, where `(int)p` was lossless"* and *"this
is 2026, where it is not"* about the SAME kernel. It is the same role
`FD_SETSIZE` plays in `ph16` and the `REAL_SIZE` boundary in `ph29`, except that
those two really are attacker-reachable and this one is not.
⭐ `_check_place` below asserts that EVERY window of `small.bin` and
`large.bin` carries `place == 0`, because at any other placement R1 and R1h
compute different functions and `check.py` stage 7h would -- correctly -- refuse
the row. The other placements are where they belong: `adversarial-*.bin`, where
stage 4 RECORDS per-rung behaviour instead of requiring agreement.

⚠⚠ THE MEASURED CORPUS MUST REACH EVERY ARM OF `mbfl_filt_conv_html_dec`
========================================================================
`PROTOCOL_PHP.md` §A2a rule 1, and `ph03` is why it is a rule. The filter is a
state machine with nine distinguishable arms and `CRASH-123.php` -- which is one
`&#20013;` -- takes two of them:

    pass       :185  any ordinary byte, `!status && c != '&'`
    start      :183  `&`                             <- the corpus's cited WRITE
    numeric    :190  `&#233;`, selected by `buffer[1]=='#'`
    named_hit  :200  `&amp;`, found in the 251-entity table
    named_miss :213  `&zzq;`, not found -> `;` appended and the buffer flushed
    illegal    :225  `&ab cd`, a body byte outside `html_entity_chars`
    buffull    :225  `&abcdefghijklmn`, `filter->status+1 == 16`
    hash2      :225  `&a#`, a second `#` after two body characters
    amprestart :228  `&&`, which rewinds `status` and restarts the entity

⭐ `buffull` is the arm a casual corpus misses, and it is the one that BOUNDS the
17-byte buffer -- i.e. the arm that decides whether the wild write stays inside
one block. `_check_arms` re-decodes what this script just emitted, with its own
decoder, and refuses a corpus that misses any of the nine.

⚠ AND IT MUST NOT REACH `:193`'s SIGNED OVERFLOW.
`ent = ent*10 + (buffer[pos] - '0')` is `int` arithmetic over bytes that
`html_entity_chars` lets be LETTERS, so `&#abcdefghijkl;` reaches ~7.4e12 and
overflows -- a SECOND, uncatalogued defect in the same function (`../NOTES.md`
§12). `_check_arms` computes the largest `ent` any shipped window produces, on
BOTH rungs, and refuses a corpus that goes near `INT_MAX`: the row's numbers
must not be taken over undefined behaviour the row is not about.
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

HEAD = 8
ENTITY_CHARS = ("#0123456789abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
HTML_ENC_BUFFER_SIZE = 16

# ⚠ STRIDES CHOSEN SO THE TWO MEASURED INPUTS HAVE DIFFERENT WORK PER CALL and
# differ modulo several small numbers, so `check.py`'s marginal-Ir slope has two
# genuinely different points and no alignment coincidence can hide a defect.
SMALL_STRIDE, SMALL_WINS = 560, 32          # 17.9 KiB, inside this box's L1
LARGE_STRIDE, LARGE_WINS = 4086, 2050       # 8.4 MiB, 8x L2: a cold window
RESIDUE_MODULI = (4, 8, 16, 3)

# The token grammar. Every token is a byte string fed to ONE filter; the arm it
# is here to reach is in the comment. `_check_arms` re-derives the arms from the
# emitted bytes rather than trusting this table.
TOKENS = [
    (b"the quick brown fox ", "pass"),
    (b"jumps over 1234 ", "pass"),
    (b"&amp;", "named_hit"),
    (b"&lt;", "named_hit"),
    (b"&gt;", "named_hit"),
    (b"&nbsp;", "named_hit"),
    (b"&eacute;", "named_hit"),
    (b"&#233;", "numeric"),
    (b"&#65;", "numeric"),
    (b"&#20013;", "numeric"),
    (b"&#0;", "numeric"),
    (b"&zzq;", "named_miss"),
    (b"&notathing;", "named_miss"),
    (b"&ab cd", "illegal"),
    (b"&x/y", "illegal"),
    (b"&abcdefghijklmn", "buffull"),
    (b"&&x", "amprestart"),
    (b"&a#", "hash2"),
]


def rng_for(name):
    r = random.Random()
    r.seed(f"{SEED:x}-{name}")
    return r


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "little")


def stream(rng, n):
    """`n` bytes of token text for ONE filter, every token reachable."""
    out = bytearray()
    order = [t for t, _ in TOKENS]
    while len(out) < n:
        rng.shuffle(order)
        for t in order:
            out += t
            if len(out) >= n:
                break
    return bytes(out[:n])


def window(rng, stride, place=0, order=0):
    ntext = stride - HEAD
    assert ntext % 2 == 0, "stride must be even so the two filters get equal text"
    a = stream(rng, ntext // 2)
    b = stream(rng, ntext // 2)
    text = bytearray(ntext)
    text[0::2] = a
    text[1::2] = b
    w = _u32(place) + _u32(order) + bytes(text)
    assert len(w) == stride
    return w


def tiled(rng, nwin, stride):
    body = bytearray()
    for i in range(nwin):
        body += window(rng, stride, place=0, order=i & 1)
    return bytes(body)


# ===========================================================================
# the re-derivation.  ⚠ An INDEPENDENT decoder: it is not ../model.py's and it
# is not imported from anywhere.  A model bug and a fixture bug cannot cancel.
# ===========================================================================
def _rd32(b, i):
    return int.from_bytes(bytes(b[i:i + 4]), "little")


def _sc(v):
    return v - 256 if v >= 128 else v


def _is_ec(c):
    """`strchr(html_entity_chars, c) != NULL`, `mbfilter_htmlent.c:225`.
    ⚠ INCLUDING `c == 0`: `strchr(s, 0)` returns the TERMINATOR.
    `controls/strchr_equiv.c` measures it against the real `strchr`."""
    return c == 0 or chr(c) in ENTITY_CHARS


def _arms_of(s, entities):
    """Step ONE filter's byte stream and report (arms reached, max |ent|).

    A private 17-byte buffer, which is what R1h has at every placement and what
    R1 has at `place == 0`."""
    arms = set()
    buf = bytearray(17)
    status = 0
    max_ent = 0
    for c in s:
        if not status:
            if c == 0x26:
                status = 1
                buf[0] = 0x26
                arms.add("start")
            else:
                arms.add("pass")
            continue
        if c == 0x3B:
            buf[status] = 0
            if buf[1] == 0x23:
                ent = 0
                for pos in range(2, status):
                    ent = ent * 10 + (_sc(buf[pos]) - 0x30)
                max_ent = max(max_ent, abs(ent))
                arms.add("numeric")
                status = 0
            else:
                name = bytes(buf[1:status])
                if entities.get(name):
                    arms.add("named_hit")
                    status = 0
                else:
                    arms.add("named_miss")
                    buf[status] = 0x3B
                    status += 1
                    buf[status] = 0
                    status = 0
            continue
        buf[status] = c
        status += 1
        if (not _is_ec(c) or status + 1 == HTML_ENC_BUFFER_SIZE
                or (c == 0x23 and status > 2)):
            if not _is_ec(c):
                arms.add("illegal")
            if status + 1 == HTML_ENC_BUFFER_SIZE:
                arms.add("buffull")
            if c == 0x23 and status > 2:
                arms.add("hash2")
            if c == 0x26:
                status -= 1
                arms.add("amprestart")
            buf[status] = 0
            status = 0
            if c == 0x26:
                status = 1
                buf[0] = 0x26
    return arms, max_ent


WANT_ARMS = {"pass", "start", "numeric", "named_hit", "named_miss", "illegal",
             "buffull", "hash2", "amprestart"}
INT_MAX = (1 << 31) - 1
ENT_CEILING = INT_MAX // 100        # two more decimal digits of headroom


def _entities():
    """The 251-entity table, read from the SHIPPED C header rather than from
    the tarball -- so this check tests what the kernel will actually compile."""
    import re
    rx = re.compile(r'^\t\{"([^"]*)",\s*(-?\d+)\},$')
    out = {}
    p = os.path.join(HERE, "..", "c", "mbfl__html_entities.h")
    with open(p, encoding="utf-8") as fh:
        for ln in fh:
            m = rx.match(ln.rstrip("\n"))
            if m:
                out[m.group(1).encode("ascii")] = int(m.group(2))
    return out


def _check_residues():
    bad = []
    for m in RESIDUE_MODULI:
        if SMALL_STRIDE % m == LARGE_STRIDE % m:
            bad.append(f"strides {SMALL_STRIDE} and {LARGE_STRIDE} agree mod {m}")
    for s in (SMALL_STRIDE, LARGE_STRIDE):
        if s % 2:
            bad.append(f"stride {s} is odd: the two filters would get unequal text")
        if s < 16:
            bad.append(f"stride {s} is below the driver's guard")
    return bad


def _check_span(name, blob, stride):
    """Re-decode what was just emitted and refuse a corpus that misses an arm,
    carries a non-zero `place`, or goes near `:193`'s signed overflow."""
    ents = _entities()
    bad = []
    arms = set()
    max_ent = 0
    nwin = len(blob) // stride
    if nwin * stride != len(blob):
        bad.append(f"{name}: {len(blob)} bytes is not a whole number of windows")
    for k in range(nwin):
        win = blob[k * stride:(k + 1) * stride]
        place = _rd32(win, 0) & 3
        if place != 0:
            bad.append(f"{name}: window {k} has place={place}; a MEASURED window "
                       f"must be place 0 or R1 and R1h compute different "
                       f"functions and stage 7h refuses the row")
        text = win[HEAD:]
        for half in (text[0::2], text[1::2]):
            a, e = _arms_of(half, ents)
            arms |= a
            max_ent = max(max_ent, e)
    missing = WANT_ARMS - arms
    if missing:
        bad.append(f"{name}: arms never reached: {sorted(missing)}")
    if max_ent > ENT_CEILING:
        bad.append(f"{name}: max |ent| {max_ent} is within 100x of INT_MAX; "
                   f":193's signed overflow is reachable and the row's numbers "
                   f"would be taken over undefined behaviour")
    if not bad:
        print(f"  {name}: {nwin} windows, all place=0, "
              f"{len(arms)}/{len(WANT_ARMS)} arms, max |ent| {max_ent}")
    return bad


def adv(stride, place, order, seed):
    """ONE window, no slack. `stride == n_blob`, so `nwin == 1` and the
    driver's window index is always 0 -- a hostile window that is never
    selected would declare a behaviour nothing exercises."""
    return window(rng_for(seed), stride, place=place, order=order)


def alias_witness(stride, place):
    """⭐ THE MINIMAL, LEGIBLE ALIASING WITNESS.

    Filter A decodes `&amp;` while filter B writes `&#65;` through -- under
    truncation -- THE SAME 17 BYTES. B's `#` lands on A's buffer index 1, so
    when A's `;` arrives `buffer[1]=='#'` selects the NUMERIC arm of a named
    entity. `controls/alias.py` prints exactly what comes out."""
    a = b"x&amp;y"
    b = b" &#65; "
    n = max(len(a), len(b))
    a = (a + b"." * n)[:n]
    b = (b + b"." * n)[:n]
    text = bytearray(2 * n)
    text[0::2] = a
    text[1::2] = b
    w = bytearray(_u32(place) + _u32(0) + bytes(text))
    if stride is not None:
        assert len(w) <= stride
        w += b"." * (stride - len(w))
    if (len(w) - HEAD) & 1:
        w += b"."
    return bytes(w)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:34s} n_iters={n_iters:<7d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def main():
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    print("ph45 inputs ->", os.path.relpath(HERE, os.getcwd()))
    problems = _check_residues()
    for p in problems:
        print("gen.py: " + p, file=sys.stderr)
    if problems:
        return 1
    print(f"  residues ok: strides {SMALL_STRIDE}/{LARGE_STRIDE} differ mod "
          + ", ".join(str(m) for m in RESIDUE_MODULI))

    # ---- the two measured inputs -----------------------------------------
    small = tiled(rng_for("small"), SMALL_WINS, SMALL_STRIDE)
    large = tiled(rng_for("large"), LARGE_WINS, LARGE_STRIDE)
    problems = (_check_span("small.bin", small, SMALL_STRIDE)
                + _check_span("large.bin", large, LARGE_STRIDE))
    for p in problems:
        print("gen.py: " + p, file=sys.stderr)
    if problems:
        return 1
    write("small.bin", 1_500, SMALL_STRIDE, small)
    write("large.bin", 200, LARGE_STRIDE, large)

    # ---- adversarial ------------------------------------------------------
    # (0) ⭐ THE MUST-NOT-FIRE CONTROL, AND IT IS AN INPUT RATHER THAN A SCRIPT.
    #     Byte-for-byte the same text and the same interleaving as
    #     `adversarial-alias.bin`, with `place = 0` so the two work buffers do
    #     NOT alias. Every rung must agree here. Without it the divergence the
    #     alias window shows could be the interleaving rather than the aliasing,
    #     and nothing in the number would say which.
    w = alias_witness(560, place=0)
    write("adversarial-noalias.bin", 16, len(w), w)

    # (1) ⭐⭐ THE ORACLE. `place = 2`: filter A in LO, filter B in HI, exactly
    #     2^32 apart, so `(char*)(int)p` makes them ONE BUFFER. R1 decodes
    #     `&amp;` to something that is not 38, double-frees one block and leaks
    #     the other; R1h and all four Rust rungs are correct. NOTHING FAULTS and
    #     no sanitizer says a word -- which is the point: the harm of a wild
    #     write into another live allocation is a silent wrong answer.
    w = alias_witness(560, place=2)
    write("adversarial-alias.bin", 16, len(w), w)

    # (2) the mirror: filter A in HI, filter B in LO. The same aliasing with the
    #     roles swapped, which is what says the effect is not a property of
    #     which filter is fed first.
    w = alias_witness(560, place=1)
    write("adversarial-alias-mirror.bin", 16, len(w), w)

    # (3) BOTH filters in HI. ⭐ The decode is CORRECT -- the truncation shadows
    #     both buffers onto the LO region injectively, so every read sees what
    #     the matching write put there -- and ONLY the allocator is wrong: two
    #     frees of addresses the arena never issued, two blocks leaked. This is
    #     obligation O3 in isolation, with O2 satisfied by accident, and it is
    #     the cell that says the truncation is not one defect but three.
    w = adv(560, place=3, order=0, seed="hi-both")
    write("adversarial-hi-both.bin", 16, len(w), w)

    # (4) the rich text at `place = 2`: every token of the grammar, both
    #     filters, aliasing. Where (1) is legible, this one is broad.
    w = adv(560, place=2, order=1, seed="alias-rich")
    write("adversarial-alias-rich.bin", 16, len(w), w)

    # (5) the driver guard: a stride below 16 makes the loop body unreachable,
    #     so the kernel is never called and the checksum is 0.
    write("adversarial-nowin.bin", 16, 12, b"\x00" * 12)
    return 0


if __name__ == "__main__":
    sys.exit(main())
