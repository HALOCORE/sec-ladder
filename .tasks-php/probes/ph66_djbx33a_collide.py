#!/usr/bin/env python3
"""ph66 (row-13 candidate) -- the key/index collision the fixture needs.

    python3 .tasks-php/probes/ph66_djbx33a_collide.py
    python3 .tasks-php/probes/ph66_djbx33a_collide.py --selftest

⭐ WHY THIS EXISTS. `patterns-php/CATALOGUE.md`'s `ph66` block says *"The DJBX33A
preimage the fixture needs was never computed; compute it before building."*
⛔⛔ THAT NAMES THE WRONG DIRECTION, AND THE DIRECTION IT NAMES IS INFEASIBLE.
This file is the measurement behind that claim, so the claim has a generator
(`CLAUDE.md` rule 1) instead of living in gitignored scratch (F51/F99).

=============================================================================
MEASURED AGAINST THE PINNED 5.0.0 TARBALL (sha256 5783e0c0...d6919)
=============================================================================
(1) `Zend/zend_hash.h` -- `static inline ulong zend_inline_hash_func(char*, uint)`,
    `hash = 5381`, `hash = ((hash << 5) + hash) + *arKey++`. DJBX33A in a ulong.
(2) `Zend/zend_types.h` -- `typedef unsigned long zend_ulong;` => 64-bit on LP64.
    ▶ So a PREIMAGE is a 64-bit target. ⛔ It is NOT constructible by digit
      lifting: every 33^k is ODD, hence a UNIT mod 2^64, so no byte position
      owns a bit range and there is nothing to lift. And 2^64 is not
      searchable. It needs CVP/lattice or a ~2^32 meet-in-the-middle.
      ⓘ The manager tried the lifting route first and it failed; the failure
      is the evidence for this paragraph, which is why it is recorded.
(3) ⭐⭐ BUT NO PREIMAGE IS NEEDED. `_zend_hash_index_update_or_next_insert`
    stores `p->h = h` with `h` the RAW USER-CHOSEN INDEX, and its lookup is
    `(p->nKeyLength == 0) && (p->h == h)`.
    ▶ RUN THE HASH FORWARDS on any string key and USE THE RESULT AS THE
      INTEGER INDEX. One line, no search.
(4) `nKeyLength` INCLUDES THE NUL -- `Zend/zend_execute.c:3612` passes
    `varname->value.str.len + 1`.

The defect then fires at `Zend/zend_hash.c:461-462`
(`zend_hash_del_key_or_index`):

    if ((p->h == h) && ((p->nKeyLength == 0) || /* Numeric index */
        ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, nKeyLength)))))

-- the left disjunct fires on the numeric bucket and THE KEY IS NEVER COMPARED.

⚠⚠ THIS IS A C-SIDE SCOPING MEASUREMENT AND NOTHING ELSE. It is not an
admission argument and must never be used to refuse a candidate
(`CLAUDE.md` rule 6).
"""
import sys

M64 = 1 << 64


def djbx33a(bs):
    """zend_inline_hash_func, verified against Zend/zend_hash.h in the tarball."""
    h = 5381
    for b in bs:
        h = (h * 33 + b) % M64
    return h


def collide(key: bytes):
    """-> (h, signed) : the integer index whose numeric bucket `key` deletes."""
    h = djbx33a(key + b"\x00")          # nKeyLength = strlen + 1
    return h, (h - M64 if h >= (1 << 63) else h)


def selftest():
    bad = []

    def ck(name, cond, why):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}: {why}")
        if not cond:
            bad.append(name)

    # N1 -- the hash reproduces a value computed by hand from the 5.0.0 source.
    ck("N1", djbx33a(b"abc\x00") == 6385036779,
       "DJBX33A('abc'+NUL) == 6385036779. A pin on the ALGORITHM, not on any "
       "row: if this moves, the tarball reading in the docstring is wrong.")

    # N2 -- MUST-FIRE: the NUL is load-bearing, so dropping it must change h.
    ck("N2", djbx33a(b"abc") != djbx33a(b"abc\x00"),
       "hashing WITHOUT the NUL gives a different value -- so premise (4) is "
       "a real constraint and not decoration. If these ever agree, the "
       "strlen+1 convention has stopped mattering and (4) needs re-reading.")

    # N3 -- the forward route actually produces a usable index, round-tripped.
    h, signed = collide(b"key")
    ck("N3", h == djbx33a(b"key\x00") and (signed % M64) == h,
       "the forward route round-trips: the published index and the hash are "
       "the same 64 bits, which is the whole claim in (3).")

    # N4 -- MUST-FIRE: 33 is invertible mod 2^64, which is WHY lifting fails.
    ck("N4", pow(33, -1, M64) * 33 % M64 == 1,
       "33 is a UNIT mod 2^64. This is the reason the preimage direction has "
       "no digit structure -- stated as an arm so the argument in (2) is "
       "checked rather than asserted.")

    # N5 -- distinct keys give distinct indices (the fixture needs >1 pair).
    ks = [b"abc", b"key", b"zz", b"x"]
    ck("N5", len({collide(k)[0] for k in ks}) == len(ks),
       f"the {len(ks)} sample keys give {len(ks)} distinct indices, so a "
       "fixture can carry several collision pairs at once.")

    print("\nSELFTEST " + ("FAIL: " + " ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(f"{'string key':<10} {'h (zend_ulong)':>22} {'as a PHP int':>22}")
    for k in (b"abc", b"key", b"zz", b"x"):
        h, signed = collide(k)
        print(f"{k.decode():<10} {h:>22} {signed:>22}")
    print("\n⚠ Scoping only. Not an admission argument (CLAUDE.md rule 6).")
    sys.exit(0)
