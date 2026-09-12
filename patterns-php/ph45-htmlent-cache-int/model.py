#!/usr/bin/env python3
"""ph45-htmlent-cache-int -- the independent reference implementation.

`harness/check.py` drives this: it re-derives the checksum, the per-call
bindings the `ensures` clauses are evaluated against, `work_per_call`, the
sanitizer expectation and the expected exit code, all from the `.bin` alone.

⚠⚠ TWO IMPLEMENTATIONS, AND THEY ARE GENUINELY DIFFERENT ALGORITHMS
===================================================================
`PROTOCOL_PHP.md` §A2a rule 2, and `ph03` is why it is a rule: a second
implementation that is the first one in disguise checks nothing.

  1. `_simulate(win, ln, hardened)` -- a MEMORY MODEL.  It owns two 4096-byte
     regions, runs `c/arena.h`'s bump allocator over them, and steps
     `mbfl_filt_conv_html_dec` one byte at a time through a 17-byte buffer
     reached by an ADDRESS.  On R1 that address is the truncation of the one
     `mbfl_malloc` returned, so two filters placed 2^32 apart write through the
     SAME bytes.  It has status, a buffer, and `strcmp` reading a C string out
     of it.

  2. `html_fold(buf, off, ln)` -- a STREAM DECODER.  No buffer, no address, no
     allocator, no `status`: it tokenises each filter's byte stream with a
     one-pass scanner and maps each token to what it emits.  It is what R1h and
     all four Rust rungs compute, and it is what `verus.rs`'s `ensures` names.
     ⭐ It CANNOT express the defect -- a stream decoder has no shared buffer to
     alias -- which is exactly why it is a useful second opinion, and it is also
     a small statement of this row's ladder result.

`selfcheck()` drives them against each other over a domain it CONSTRUCTS: every
placement x every destruction order x a token grammar that reaches all six arms
of `mbfl_filt_conv_html_dec`, plus the six arms in isolation, plus the aliasing
witnesses.  `inputs/` is not a domain.

⚠ The 251-entity table below is GENERATED from the pinned tarball by
`controls/entity_table.py`, which also checks it -- with a must-fire negative --
against the five other copies the row ships.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common-php"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# ---- c/arena.h ------------------------------------------------------------
BLOCK = 32          # PH45_BLOCK
SLOTS = 8           # PH45_SLOTS
REGION = 4096       # PH45_REGION_BYTES
LO, HI = 0, 1

# ---- mbfilter_htmlent.c:155 ----------------------------------------------
HTML_ENC_BUFFER_SIZE = 16
REQ = HTML_ENC_BUFFER_SIZE + 1                      # the mbfl_malloc request
ENTITY_CHARS = ("#0123456789abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ")       # :156

HEAD = 8            # [u32 place][u32 order]

# `sizeof(mbfl_convert_filter)` on this ABI: six function pointers (48) + data
# (8) + status + cache (8) + from/to (16) + illegal_mode/substchar (8) = 88,
# and 96 for R1h, which adds `void *opaque`.  ⚠ The kernel folds the shim's
# three COUNT fields and NOT `bytes_mallocked`, precisely because this number
# moves; NOTES.md §8.
SZ_FILTER = 88
SZ_FILTER_H = 96
MAX_CACHED_MEMORY = 11

# ---- html_entities.c:37-290, GENERATED -- do not edit ---------------------
ENTITIES = [
    ("quot", 34),
    ("amp", 38),
    ("lt", 60),
    ("gt", 62),
    ("nbsp", 160),
    ("iexcl", 161),
    ("cent", 162),
    ("pound", 163),
    ("curren", 164),
    ("yen", 165),
    ("brvbar", 166),
    ("sect", 167),
    ("uml", 168),
    ("copy", 169),
    ("ordf", 170),
    ("laquo", 171),
    ("not", 172),
    ("shy", 173),
    ("reg", 174),
    ("macr", 175),
    ("deg", 176),
    ("plusmn", 177),
    ("sup2", 178),
    ("sup3", 179),
    ("acute", 180),
    ("micro", 181),
    ("para", 182),
    ("middot", 183),
    ("cedil", 184),
    ("sup1", 185),
    ("ordm", 186),
    ("raquo", 187),
    ("frac14", 188),
    ("frac12", 189),
    ("frac34", 190),
    ("iquest", 191),
    ("Agrave", 192),
    ("Aacute", 193),
    ("Acirc", 194),
    ("Atilde", 195),
    ("Auml", 196),
    ("Aring", 197),
    ("AElig", 198),
    ("Ccedil", 199),
    ("Egrave", 200),
    ("Eacute", 201),
    ("Ecirc", 202),
    ("Euml", 203),
    ("Igrave", 204),
    ("Iacute", 205),
    ("Icirc", 206),
    ("Iuml", 207),
    ("ETH", 208),
    ("Ntilde", 209),
    ("Ograve", 210),
    ("Oacute", 211),
    ("Ocirc", 212),
    ("Otilde", 213),
    ("Ouml", 214),
    ("times", 215),
    ("Oslash", 216),
    ("Ugrave", 217),
    ("Uacute", 218),
    ("Ucirc", 219),
    ("Uuml", 220),
    ("Yacute", 221),
    ("THORN", 222),
    ("szlig", 223),
    ("agrave", 224),
    ("aacute", 225),
    ("acirc", 226),
    ("atilde", 227),
    ("auml", 228),
    ("aring", 229),
    ("aelig", 230),
    ("ccedil", 231),
    ("egrave", 232),
    ("eacute", 233),
    ("ecirc", 234),
    ("euml", 235),
    ("igrave", 236),
    ("iacute", 237),
    ("icirc", 238),
    ("iuml", 239),
    ("eth", 240),
    ("ntilde", 241),
    ("ograve", 242),
    ("oacute", 243),
    ("ocirc", 244),
    ("otilde", 245),
    ("ouml", 246),
    ("divide", 247),
    ("oslash", 248),
    ("ugrave", 249),
    ("uacute", 250),
    ("ucirc", 251),
    ("uuml", 252),
    ("yacute", 253),
    ("thorn", 254),
    ("yuml", 255),
    ("OElig", 338),
    ("oelig", 339),
    ("Scaron", 352),
    ("scaron", 353),
    ("Yuml", 376),
    ("fnof", 402),
    ("circ", 710),
    ("tilde", 732),
    ("Alpha", 913),
    ("Beta", 914),
    ("Gamma", 915),
    ("Delta", 916),
    ("Epsilon", 917),
    ("Zeta", 918),
    ("Eta", 919),
    ("Theta", 920),
    ("Iota", 921),
    ("Kappa", 922),
    ("Lambda", 923),
    ("Mu", 924),
    ("Nu", 925),
    ("Xi", 926),
    ("Omicron", 927),
    ("Pi", 928),
    ("Rho", 929),
    ("Sigma", 931),
    ("Tau", 932),
    ("Upsilon", 933),
    ("Phi", 934),
    ("Chi", 935),
    ("Psi", 936),
    ("Omega", 937),
    ("beta", 946),
    ("gamma", 947),
    ("delta", 948),
    ("epsilon", 949),
    ("zeta", 950),
    ("eta", 951),
    ("theta", 952),
    ("iota", 953),
    ("kappa", 954),
    ("lambda", 955),
    ("mu", 956),
    ("nu", 957),
    ("xi", 958),
    ("omicron", 959),
    ("pi", 960),
    ("rho", 961),
    ("sigmaf", 962),
    ("sigma", 963),
    ("tau", 964),
    ("upsilon", 965),
    ("phi", 966),
    ("chi", 967),
    ("psi", 968),
    ("omega", 969),
    ("thetasym", 977),
    ("upsih", 978),
    ("piv", 982),
    ("ensp", 8194),
    ("emsp", 8195),
    ("thinsp", 8201),
    ("zwnj", 8204),
    ("zwj", 8205),
    ("lrm", 8206),
    ("rlm", 8207),
    ("ndash", 8211),
    ("mdash", 8212),
    ("lsquo", 8216),
    ("rsquo", 8217),
    ("sbquo", 8218),
    ("ldquo", 8220),
    ("rdquo", 8221),
    ("bdquo", 8222),
    ("dagger", 8224),
    ("Dagger", 8225),
    ("bull", 8226),
    ("hellip", 8230),
    ("permil", 8240),
    ("prime", 8242),
    ("Prime", 8243),
    ("lsaquo", 8249),
    ("rsaquo", 8250),
    ("oline", 8254),
    ("frasl", 8260),
    ("euro", 8364),
    ("weierp", 8472),
    ("image", 8465),
    ("real", 8476),
    ("trade", 8482),
    ("alefsym", 8501),
    ("larr", 8592),
    ("uarr", 8593),
    ("rarr", 8594),
    ("darr", 8595),
    ("harr", 8596),
    ("crarr", 8629),
    ("lArr", 8656),
    ("uArr", 8657),
    ("rArr", 8658),
    ("dArr", 8659),
    ("hArr", 8660),
    ("forall", 8704),
    ("part", 8706),
    ("exist", 8707),
    ("empty", 8709),
    ("nabla", 8711),
    ("isin", 8712),
    ("notin", 8713),
    ("ni", 8715),
    ("prod", 8719),
    ("sum", 8721),
    ("minus", 8722),
    ("lowast", 8727),
    ("radic", 8730),
    ("prop", 8733),
    ("infin", 8734),
    ("ang", 8736),
    ("and", 8743),
    ("or", 8744),
    ("cap", 8745),
    ("cup", 8746),
    ("int", 8747),
    ("there4", 8756),
    ("sim", 8764),
    ("cong", 8773),
    ("asymp", 8776),
    ("ne", 8800),
    ("equiv", 8801),
    ("le", 8804),
    ("ge", 8805),
    ("sub", 8834),
    ("sup", 8835),
    ("nsub", 8836),
    ("sube", 8838),
    ("supe", 8839),
    ("oplus", 8853),
    ("otimes", 8855),
    ("perp", 8869),
    ("sdot", 8901),
    ("lceil", 8968),
    ("rceil", 8969),
    ("lfloor", 8970),
    ("rfloor", 8971),
    ("lang", 9001),
    ("rang", 9002),
    ("loz", 9674),
    ("spades", 9824),
    ("clubs", 9827),
    ("hearts", 9829),
    ("diams", 9830),
]

ENTITY_CODE = {n.encode("ascii"): c for n, c in ENTITIES}


def _rd32(b, i):
    return int.from_bytes(bytes(b[i:i + 4]), "little")


def _sc(v):
    """C `char` on x86-64 is SIGNED.  `buffer[pos] - '0'` depends on it."""
    return v - 256 if v >= 128 else v


def _is_ec(c):
    """`strchr(html_entity_chars, c) != NULL` -- `mbfilter_htmlent.c:225`.

    ⚠⚠ INCLUDING `c == 0`.  `strchr(s, 0)` returns a pointer to the TERMINATOR,
    which is non-NULL, so PHP treats a NUL byte inside an entity body as a legal
    entity character.  Missing that makes every rung compute a different
    function from the C on any window containing a zero byte, and no shipped
    window does -- which is exactly how it would have survived.
    `controls/strchr_equiv.c` drives all 256 byte values against the real
    `strchr`, with a must-fire negative for the predicate that omits this arm.
    """
    return c == 0 or chr(c) in ENTITY_CHARS


class Wild(Exception):
    """R1 evaluated something this model refuses to predict."""


# ===========================================================================
# implementation 1 of 2 -- THE MEMORY MODEL
# ===========================================================================
class _Arena:
    """`c/arena.h`.  Two regions, `base[HI] == base[LO] + 2^32` exactly.

    ⭐ NO REAL ADDRESS IS NEEDED.  `MAP_32BIT` puts `base[LO]` below 2^31 and
    the regions are one page, so for every block `(r, off)` the 32-bit
    truncation of its address is `base[LO] + off` -- i.e. the LO region at the
    SAME offset, whichever region the block is really in.  That is the whole of
    `(char*)(int)p`, it is independent of where the kernel happens to land, and
    it is why this model is deterministic where the real program is not."""

    def __init__(self):
        self.mem = [bytearray(REGION), bytearray(REGION)]
        self.bump = [0, 0]
        self.blk = []                 # [region, off, live]
        self.region = LO
        self.n_alloc = self.n_free = self.n_dfree = self.n_wfree = 0
        self.bytes = 0

    def malloc(self, n):
        self.n_alloc += 1
        r = self.region
        if n > BLOCK or self.bump[r] + BLOCK > REGION:
            return None
        off = self.bump[r]
        self.bump[r] += BLOCK
        self.bytes += BLOCK
        if len(self.blk) < 2 * SLOTS:
            self.blk.append([r, off, 1])
        return (r, off)

    def free(self, p):
        for b in self.blk:
            if b[0] == p[0] and b[1] == p[1]:
                if b[2]:
                    b[2] = 0
                    self.n_free += 1
                else:
                    self.n_dfree += 1
                return
        self.n_wfree += 1

    def live(self):
        return sum(1 for b in self.blk if b[2])

    # the two accessors every dereference goes through
    def get(self, p, i):
        return self.mem[p[0]][p[1] + i]

    def set(self, p, i, v):
        self.mem[p[0]][p[1] + i] = v & 0xFF


def _trunc(p):
    """`(char*)(int)p` -- `mbfilter_htmlent.c:178`, `:249`, and `:169`'s
    `(void*)`.  See `_Arena`'s docstring for why this is exact."""
    return None if p is None else (LO, p[1])


class _Filter:
    """`struct _mbfl_convert_filter` (mbfl_convert.h:40-54), the two fields
    that matter.  `cache` holds the ADDRESS as an `int` on R1 and `opaque`
    holds it as a pointer on R1h -- which is the whole of `e8901dc17087`."""

    __slots__ = ("status", "cache", "opaque", "hardened")

    def __init__(self, hardened):
        self.status = 0
        self.cache = None            # R1: the block, to be truncated on read
        self.opaque = None           # R1h: the block, verbatim
        self.hardened = hardened

    def buffer(self):
        """`:178` / `:249`.  R1 truncates; R1h does not."""
        return self.opaque if self.hardened else _trunc(self.cache)

    def stored(self):
        """what `:169` hands the deallocator."""
        return self.opaque if self.hardened else _trunc(self.cache)

    def nonzero(self):
        """`:167` `if (filter->cache)` / `if (filter->opaque)`."""
        return (self.opaque if self.hardened else self.cache) is not None


def _simulate(win, ln, hardened, trace=None):
    """One window, one C rung.  A transcription of `c/kernel*.c`.

    Returns `(u64, info)`.  `hardened=False` is R1 (5.0.0), `True` is R1h
    (`e8901dc17087`).  `trace`, if given, is a list every emitted value is
    appended to -- `controls/alias.py` is what needs it, and nothing the gate
    drives passes it."""
    place = _rd32(win, 0) & 3
    order = _rd32(win, 4) & 1
    text = win[HEAD:ln]

    al = _Arena()
    out = {"fold": 0, "emitted": 0, "arms": set(), "max_ent": 0}

    def emit(c):
        """`(*filter->output_function)(c, filter->data)` -- ph45_output."""
        out["fold"] = (out["fold"] * 31 + (c & 0xFFFFFFFF)) & MASK
        out["emitted"] += 1
        if trace is not None:
            trace.append(c)
        return 0

    def ctor(f, region):                       # :158-162
        f.status = 0
        al.region = region
        p = al.malloc(REQ)
        if hardened:
            f.opaque = p
        else:
            f.cache = p

    def dtor(f):                               # :164-172
        f.status = 0
        if f.nonzero():
            al.free(f.stored())                # :169  <== O3
        if hardened:
            f.opaque = None
        else:
            f.cache = None

    def flush(f):                              # :244-257
        buf = f.buffer()                       # :249  <== cast back #2
        status = f.status
        pos = 0
        while status:
            status -= 1
            emit(_sc(al.get(buf, pos)))
            pos += 1
        f.status = 0
        return 0

    def dec(c, f):                             # :174-242
        ent = 0
        buf = f.buffer()                       # :178  <== cast back #1
        if not f.status:
            if c == 0x26:                      # '&'
                f.status = 1
                al.set(buf, 0, 0x26)           # :183  <== the cited WRITE
                out["arms"].add("start")
            else:
                emit(c)                        # :185
                out["arms"].add("pass")
        else:
            if c == 0x3B:                      # ';'
                al.set(buf, f.status, 0)       # :189
                if al.get(buf, 1) == 0x23:     # '#'  :190
                    for pos in range(2, f.status):
                        ent = ent * 10 + (_sc(al.get(buf, pos)) - 0x30)
                    out["max_ent"] = max(out["max_ent"], abs(ent))
                    if not -(1 << 31) <= ent < (1 << 31):
                        raise Wild("`ent` overflows `int` at :193")
                    emit(ent)                  # :195
                    f.status = 0
                    out["arms"].add("numeric")
                else:
                    for name, code in ENTITIES:          # :200-207
                        if _strcmp_eq(al, buf, name):
                            ent = code
                            break
                    if ent:
                        emit(ent)              # :210
                        f.status = 0
                        out["arms"].add("named_hit")
                    else:
                        al.set(buf, f.status, 0x3B)      # :215
                        f.status += 1
                        al.set(buf, f.status, 0)         # :216
                        flush(f)                         # :218
                        out["arms"].add("named_miss")
            else:
                al.set(buf, f.status, c)       # :223
                f.status += 1
                if (not _is_ec(c)
                        or f.status + 1 == HTML_ENC_BUFFER_SIZE
                        or (c == 0x23 and f.status > 2)):     # :225
                    if not _is_ec(c):
                        out["arms"].add("illegal")
                    if f.status + 1 == HTML_ENC_BUFFER_SIZE:
                        out["arms"].add("buffull")
                    if c == 0x23 and f.status > 2:
                        out["arms"].add("hash2")
                    if c == 0x26:                        # :228
                        f.status -= 1
                        out["arms"].add("amprestart")
                    al.set(buf, f.status, 0)             # :230
                    flush(f)                             # :232
                    if c == 0x26:                        # :233-237
                        f.status = 1
                        al.set(buf, 0, 0x26)
        return c

    fa = _Filter(hardened)
    fb = _Filter(hardened)
    al.region = LO
    ctor(fa, place & 1)
    ctor(fb, (place >> 1) & 1)

    for i, c in enumerate(text):               # mbfilter.c:262-267, two filters
        dec(c, fb if (i & 1) else fa)
    flush(fa)
    flush(fb)

    acc = out["fold"]
    acc = (acc * 31 + out["emitted"]) & MASK

    for f in ((fb, fa) if order else (fa, fb)):
        dtor(f)

    for v in (al.n_alloc, al.n_free, al.n_dfree, al.n_wfree, al.live(),
              al.bytes):
        acc = (acc * 31 + v) & MASK
    # the shim's three COUNT fields: two filter structs in, two out, and
    # REAL_SIZE(88)>>3 == 11 == MAX_CACHED_MEMORY so nothing is ever cached.
    for v in _shim_counts(hardened):
        acc = (acc * 31 + v) & MASK

    info = dict(place=place, order=order, ntext=len(text),
                emitted=out["emitted"], arms=frozenset(out["arms"]),
                max_ent=out["max_ent"], n_alloc=al.n_alloc, n_free=al.n_free,
                n_dfree=al.n_dfree, n_wfree=al.n_wfree, live=al.live(),
                bytes=al.bytes)
    return acc, info


def _strcmp_eq(al, buf, name):
    """`strcmp(buffer+1, entity->name) == 0`, byte for byte.

    ⚠ It reads AT MOST `len(name)+1` bytes of the buffer, because `strcmp`
    stops at the first difference and every entity name is 8 characters or
    fewer (measured: `controls/entity_table.py`).  So the read stays inside the
    17-byte block even when the terminator the caller wrote at `:189` has been
    overwritten by the OTHER filter."""
    for i, ch in enumerate(name.encode("ascii")):
        if al.get(buf, 1 + i) != ch:
            return False
    return al.get(buf, 1 + len(name)) == 0


def _shim_counts(hardened):
    """`php_shim_ag.{n_alloc, n_free, n_cache_hit}` for one kernel call.

    Two `php_shim_emalloc(sizeof(mbfl_convert_filter))` and two
    `php_shim_efree`.  `REAL_SIZE(88) >> 3` is 11 and `REAL_SIZE(96) >> 3` is
    12, and `MAX_CACHED_MEMORY` is 11 -- so NEITHER size is cacheable and
    `n_cache_hit` is 0 on both rungs, which is why the three counts are
    identical where `bytes_mallocked` (88 vs 96) is not."""
    sz = SZ_FILTER_H if hardened else SZ_FILTER
    idx = ((sz + 7) & ~7) >> 3
    hit = 0 if idx >= MAX_CACHED_MEMORY else 0
    return (2, 2, hit)


# ===========================================================================
# implementation 2 of 2 -- THE STREAM DECODER
# ===========================================================================
def _stream(s):
    """What ONE filter emits for the byte string `s`, plus the final flush.

    A one-pass scanner over the stream.  It carries a PENDING TOKEN -- the
    bytes since the last unconsumed `&` -- as a Python object, never as bytes
    in a buffer, so there is no address, no `int`, no allocator and nothing to
    alias.  It is the function `e8901dc17087` makes the C compute, and the one
    all four Rust rungs compute."""
    out = []
    tok = None              # None = outside an entity; else list of body chars
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        i += 1
        if tok is None:
            if c == 0x26:
                tok = []
            else:
                out.append(c)
            continue
        # inside an entity: `tok` is the body after the '&'
        if c == 0x3B:
            body = bytes(tok)
            if body[:1] == b"#":
                ent = 0
                for ch in body[1:]:
                    ent = ent * 10 + (_sc(ch) - 0x30)
                if not -(1 << 31) <= ent < (1 << 31):
                    raise Wild("`ent` overflows `int` at :193")
                out.append(ent)
            else:
                code = ENTITY_CODE.get(body)
                if code:
                    out.append(code)
                else:
                    out.extend([0x26] + list(body) + [0x3B])
            tok = None
            continue
        tok.append(c)
        status = 1 + len(tok)
        if (not _is_ec(c) or status + 1 == HTML_ENC_BUFFER_SIZE
                or (c == 0x23 and status > 2)):
            if c == 0x26:
                tok.pop()
            out.extend([0x26] + list(tok))
            tok = [] if c == 0x26 else None
    if tok is not None:
        out.extend([0x26] + list(tok))
    return out


def html_fold(buf, off, ln):
    """`html_fold` in ../verus.rs: what the kernel must return.

    R1h and R2-R5 all compute exactly this, at EVERY placement, because a
    pointer that was never narrowed designates its own block wherever it is."""
    win = bytes(buf[off:off + ln])
    place = _rd32(win, 0) & 3
    order = _rd32(win, 4) & 1
    text = win[HEAD:ln]

    sa = _stream(text[0::2])
    sb = _stream(text[1::2])
    # ⚠ the interleaving is the C's, re-derived rather than replayed: filter A
    # sees even indices and filter B odd ones, each emits in its own order, and
    # the two streams merge by ORIGINAL BYTE INDEX.  The tail of each stream
    # (what its final `mbfl_filt_conv_html_dec_flush` emits) comes after all of
    # the interleaved output: the C flushes A then B after the whole feed.
    merged, fa_tail, fb_tail = _merge(text, sa, sb)
    seq = merged + fa_tail + fb_tail

    acc = 0
    for c in seq:
        acc = (acc * 31 + (c & 0xFFFFFFFF)) & MASK
    acc = (acc * 31 + len(seq)) & MASK

    # the arena, counted rather than replayed.  On a pointer-typed field the
    # answer does not depend on `place` at all: two blocks out, two blocks
    # back, nothing double-freed, nothing wild, nothing leaked.
    for v in (2, 2, 0, 0, 0, 2 * BLOCK):
        acc = (acc * 31 + v) & MASK
    for v in _shim_counts(True):
        acc = (acc * 31 + v) & MASK
    del place, order
    return acc


def _merge(text, sa, sb):
    """Split each filter's emission into (during-feed, at-final-flush).

    `_stream` returns everything a filter emits INCLUDING its trailing flush;
    the C emits the trailing flush only after BOTH filters have been fed.  The
    tail is what the pending token contributes, which `_stream_tail` recomputes
    from the stream alone."""
    ta = _stream_tail(text[0::2])
    tb = _stream_tail(text[1::2])
    da = sa[:len(sa) - ta]
    db = sb[:len(sb) - tb]
    # interleave by original byte index: a byte at even index i emits its part
    # of `da` before the byte at index i+1 emits its part of `db`.
    return (_interleave(text, da, db), sa[len(sa) - ta:], sb[len(sb) - tb:])


def _stream_tail(s):
    """How many of `_stream(s)`'s outputs come from the FINAL flush."""
    tok = None
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        i += 1
        if tok is None:
            if c == 0x26:
                tok = []
            continue
        if c == 0x3B:
            tok = None
            continue
        tok.append(c)
        status = 1 + len(tok)
        if (not _is_ec(c) or status + 1 == HTML_ENC_BUFFER_SIZE
                or (c == 0x23 and status > 2)):
            if c == 0x26:
                tok.pop()
            tok = [] if c == 0x26 else None
    return 0 if tok is None else 1 + len(tok)


def _interleave(text, da, db):
    """Merge two emission lists by the index of the byte that produced them.

    Re-derived from the stream: `_counts` says how many outputs each byte of a
    filter's stream produced, so the merge needs no simulation."""
    ca = _counts(text[0::2])
    cb = _counts(text[1::2])
    out, ia, ib = [], 0, 0
    ka = kb = 0
    for i in range(len(text)):
        if i & 1:
            k = cb[kb] if kb < len(cb) else 0
            kb += 1
            out.extend(db[ib:ib + k])
            ib += k
        else:
            k = ca[ka] if ka < len(ca) else 0
            ka += 1
            out.extend(da[ia:ia + k])
            ia += k
    return out


def _counts(s):
    """How many values each byte of `s` makes its filter emit, flush excluded.

    This is the stream decoder again, instrumented -- not the memory model."""
    res = []
    tok = None
    for c in s:
        before = 0
        if tok is None:
            if c == 0x26:
                tok = []
            else:
                before = 1
        elif c == 0x3B:
            body = bytes(tok)
            if body[:1] == b"#":
                before = 1
            else:
                before = 1 if ENTITY_CODE.get(body) else 2 + len(body)
            tok = None
        else:
            tok.append(c)
            status = 1 + len(tok)
            if (not _is_ec(c)
                    or status + 1 == HTML_ENC_BUFFER_SIZE
                    or (c == 0x23 and status > 2)):
                if c == 0x26:
                    tok.pop()
                before = 1 + len(tok)
                tok = [] if c == 0x26 else None
        res.append(before)
    return res


# ===========================================================================
class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.nwin = 0
        self._win = []
        self.selfcheck_note = ""
        if not self.truncated:
            self._run()

    # -- one window --------------------------------------------------------
    def _window(self, off):
        """`(result, r1_state, info)`.

        `result` is R1h's -- the function R1h and R2-R5 all compute.
        `r1_state` says what R1 does with the same window:

          "same"   R1's u64 is identical: the placement made `(char*)(int)p` the
                   IDENTITY, so nothing was narrowed.  This is every window of
                   `small.bin` and `large.bin` and it is `check.py` stage 7h's
                   requirement being SATISFIED;
          "shadow" R1 decodes the same text but its FREES go to addresses the
                   arena never issued: the work buffers are in HI, the
                   truncation shadows them onto LO, and every access is
                   self-consistent.  Only the allocator counters move;
          "alias"  two filters' buffers are exactly 2^32 apart, so under
                   truncation they are ONE BUFFER.  The decode itself is wrong
                   and the frees are wrong.  This is the row's oracle."""
        win = self.buf[off: off + self.stride]
        r1h, info = _simulate(win, self.stride, True)
        try:
            r1, i1 = _simulate(win, self.stride, False)
        except Wild:
            return r1h, "wild", info
        if r1 == r1h:
            state = "same"
        elif i1["emitted"] == info["emitted"] and i1["n_wfree"]:
            state = "shadow"
        else:
            state = "alias"
        return r1h, state, info

    def r1_result(self, off):
        """R1's own u64, or None where R1 evaluates something unpredictable.
        Not used by the gate; it is what `controls/` compares against."""
        try:
            return _simulate(self.buf[off:off + self.stride],
                             self.stride, False)[0]
        except Wild:
            return None

    def _run(self):
        acc = 0
        if 16 <= self.stride <= 268435456 and self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                acc = (acc * 31 + self._win[k][0]) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            r = self._win[k][0]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    @property
    def helpers(self):
        return {"html_fold": html_fold}

    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        The kernel feeds EVERY byte past the two head words to a filter, one at
        a time, so the work really is linear in the window and the unit is not
        under the attacker's control: `ntext = stride - 8` on every call of
        every input.  It over-estimates, because one window byte buys one
        filter call and one filter call is far more than one instruction, and
        an over-estimate raises the derived floor -- the direction a floor
        should err."""
        return self.stride if self.entered else 0

    @property
    def sanitizer_expect(self):
        """⚠⚠ `clean` ON EVERY INPUT, AND THAT IS THE FINDING RATHER THAN A GAP.

        `PROTOCOL_PHP.md` §A4 wants the corpus's recorded category reproduced.
        The corpus records `SEGV ... WRITE` at `mbfilter_htmlent.c:183` for
        CRASH-123, and `TASK_PHP_034_REPORT` §5.5 reproduced exactly that with
        the faithful allocator -- `controls/fatal.c` is that build and it is
        where the row's §A4 evidence lives.

        The MEASURED rungs cannot fire a sanitizer and it is not an accident of
        the corpus: the defect is a TYPE error, and the address it produces is a
        legitimately mapped page of the row's own arena.  ASan does not track
        `mmap`, and UBSan has nothing to say -- `(int)ptr` and `(char*)i` are
        IMPLEMENTATION-DEFINED (C99 6.3.2.3p5/p6), not undefined; what is
        undefined is the DEREFERENCE, and no sanitizer has a check for it.
        ⭐ So on this row the detectors are silent and the CHECKSUM is the only
        observer -- which is why the arena's five counters are folded into it.
        NOTES.md §9."""
        return "clean"

    @property
    def expected_exit(self):
        # ph45's payload allocates nothing from an attacker-controlled size:
        # both work buffers and both filter structs are a fixed count per call.
        # `slb_load` rejecting a short file is the only non-zero exit the
        # driver produces -- except exit 9, which `c/arena.h` uses when the
        # mapping does not land where the row needs it, and which is an
        # environment failure rather than an input-dependent one.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        states = {}
        for _, s, _ in self._win:
            states[s] = states.get(s, 0) + 1
        arms = set()
        for _, _, i in self._win:
            arms |= i["arms"]
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"r1={states} arms={len(arms)} truncated={self.truncated} "
                f"expected={self.checksum}")

    # -- driving BOTH implementations --------------------------------------
    @staticmethod
    def _both(win):
        """`(_simulate hardened, html_fold)` for an arbitrary window."""
        return _simulate(win, len(win), True)[0], html_fold(win, 0, len(win))

    @staticmethod
    def mkwin(place, order, text, stride=None):
        w = bytearray(place.to_bytes(4, "little") + order.to_bytes(4, "little"))
        w += bytes(text)
        if stride is not None:
            assert len(w) <= stride
            w += b"z" * (stride - len(w))
        if (len(w) - HEAD) & 1:
            w += b"z"
        return bytes(w)

    # the token grammar: each entry reaches a named arm of :174-242.
    TOKENS = [
        ("pass", b"hi, "),
        ("named_hit", b"&amp;"),
        ("named_hit2", b"&lt;"),
        ("numeric", b"&#233;"),
        ("numeric2", b"&#65;"),
        ("named_miss", b"&zzq;"),
        ("illegal", b"&ab cd"),
        ("buffull", b"&abcdefghijklmn"),
        ("amprestart", b"&&x"),
        ("hash2", b"&a#"),
    ]

    @staticmethod
    def _synthetic_windows():
        """A domain this file CONSTRUCTS.  ⚠ `inputs/` is not a domain."""
        toks = [t for _, t in Model.TOKENS]
        # (a) every token, alone, on each filter, at every placement and order
        for place in range(4):
            for order in range(2):
                for name, t in Model.TOKENS:
                    a, b = t, b"." * len(t)
                    yield (f"solo-{name}-p{place}-o{order}",
                           Model.mkwin(place, order,
                                       bytes(itertools.chain.from_iterable(
                                           zip(a, b)))))
        # (b) every ordered PAIR of tokens on one filter, place 0
        for i, (na, ta) in enumerate(Model.TOKENS):
            for nb, tb in Model.TOKENS:
                a = ta + tb
                b = b"." * len(a)
                yield (f"pair-{na}-{nb}",
                       Model.mkwin(0, i & 1,
                                   bytes(itertools.chain.from_iterable(
                                       zip(a, b)))))
        # (c) the two filters carrying DIFFERENT tokens, every placement --
        #     the family the aliasing lives in
        for place in range(4):
            for ta in toks:
                for tb in toks:
                    n = max(len(ta), len(tb))
                    a = (ta + b"." * n)[:n]
                    b = (tb + b"." * n)[:n]
                    yield (f"cross-p{place}-{ta.decode('latin1')}"
                           f"-{tb.decode('latin1')}",
                           Model.mkwin(place, 0,
                                       bytes(itertools.chain.from_iterable(
                                           zip(a, b)))))
        # (d) empty-ish and boundary windows
        for place in range(4):
            for order in range(2):
                yield (f"min-p{place}-o{order}",
                       Model.mkwin(place, order, b"ab", stride=16))
                yield (f"amps-p{place}-o{order}",
                       Model.mkwin(place, order, b"&&&&&&&&"))
                yield (f"openent-p{place}-o{order}",
                       Model.mkwin(place, order, b"&a&b&c&d"))

    def selfcheck(self):
        """The two implementations, driven against each other.

        ⚠⚠ `html_fold` is R1h's function, so it is compared against
        `_simulate(hardened=True)` at EVERY placement, and against
        `_simulate(hardened=False)` only where the truncation is the identity
        (`place == 0`).  Where it is not, the two MUST differ on at least one
        window -- that is the must-fire half, and without it a `_simulate` that
        had quietly stopped modelling the aliasing would pass."""
        bad = []
        arms = set()
        n = 0
        r1_differs_at_place = {1: 0, 2: 0, 3: 0}
        for label, win in self._synthetic_windows():
            n += 1
            try:
                sim, fold = self._both(win)
            except Wild as e:
                bad.append(f"{label}: R1h raised {e}")
                continue
            if sim != fold:
                bad.append(f"{label}: _simulate(hardened) {sim} != "
                           f"html_fold {fold}")
            _, info = _simulate(win, len(win), True)
            arms |= info["arms"]
            place = _rd32(win, 0) & 3
            try:
                r1, _ = _simulate(win, len(win), False)
            except Wild:
                continue
            if place == 0:
                if r1 != fold:
                    bad.append(f"{label}: place 0 must be lossless, "
                               f"R1 {r1} != html_fold {fold}")
            elif r1 != fold:
                r1_differs_at_place[place] += 1
        # must-fire: each non-zero placement separates R1 from R1h somewhere
        for p in (1, 2, 3):
            if not r1_differs_at_place[p]:
                bad.append(f"MUST-FIRE: no synthetic window separates R1 from "
                           f"R1h at place {p}")
        want = {"pass", "start", "numeric", "named_hit", "named_miss",
                "illegal", "buffull", "amprestart", "hash2"}
        missing = want - arms
        if missing:
            bad.append(f"arms never reached by the synthetic domain: "
                       f"{sorted(missing)}")
        # ⚠ A LIST OF PROBLEM STRINGS, EMPTY WHEN CLEAN. `check.py::build_models` does
        # `for p in sb(m.selfcheck): rep.fail(...)`, so returning a STRING makes
        # it iterate CHARACTER BY CHARACTER and report `)` as a problem -- which
        # is exactly what this row's first gate run printed.
        self.selfcheck_note = (
            f"{n} synthetic windows, 9 arms, must-fire "
            f"{r1_differs_at_place[1]}/{r1_differs_at_place[2]}/"
            f"{r1_differs_at_place[3]} windows separate R1 from R1h at "
            f"place 1/2/3")
        return bad


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        probs = m.selfcheck()
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck="
              f"{'ok (' + m.selfcheck_note + ')' if not probs else probs}")
