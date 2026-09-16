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

=============================================================================
⭐⭐⭐ AND THE PREDICATE CENSUS -- ITEM 139 (`F133`(i)) DISCHARGED FOR THIS ROW
=============================================================================
Item 139 asks, of every row, whether the R1h's strategy was ALREADY PRESENT
elsewhere in the same construct -- **as a GREP, not as a census** (the `_061`
reviewer's binding instruction). For `ph66` the construct is one file, so the
grep is exact and `census()` below runs it: every `if` in `Zend/zend_hash.c`
whose condition tests `p->h == h`, classified by HOW it tests the key kind.

⛔⛔ THE ANSWER REFUTES `ROW13_001.md` §6's OWN PREDICTION. That section guessed
`ph66` would be a natural COUNTEREXAMPLE to `F133`(i) -- *"its repair has no
sibling to copy, it is a genuine restructure of a boolean."* Measured, it is
`F133`(i)'s STRONGEST POSITIVE: **9 of the 10 predicates already spell the
repair's own conjunct form**, a higher ratio than `ph96`'s 7-of-23.

⭐⭐ BUT THE SHARP STATEMENT IS NOT "9 of 10 were already right", because the 9
are not doing `:464`'s job. `zend_hash_del_key_or_index` is **the only one of
the ten that serves BOTH key kinds through one call site** (its `flag`
parameter); the other nine are single-kind and never face the choice.
▶ So for this row `F133`(i) splits in two, and the split is the finding:
**the repair's SPELLING was present nine times; the repair's PROBLEM was
present nowhere.** `F133`(i) as worded cannot say that, and `ph96` -- where the
7 siblings WERE doing the same job -- is the case that hides the distinction.

⚠⚠ THIS IS A C-SIDE SCOPING MEASUREMENT AND NOTHING ELSE. It is not an
admission argument and must never be used to refuse a candidate
(`CLAUDE.md` rule 6).
"""
import os
import re
import subprocess
import sys

M64 = 1 << 64

TARBALL = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
           "build-5.0.0/php-5.0.0.tar.gz")
MEMBER = "php-5.0.0/Zend/zend_hash.c"


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


def _zend_hash_c():
    """The pinned tarball's zend_hash.c, or None if the tarball is not here.

    ⚠ The tarball lives in ANOTHER project's gitignored scratch, the same
    reason `probes/ph96_arrayaccess_matrix.sh` stays out of the sweep. When it
    is absent the census is VACUOUS -- and a vacuous arm SAYS SO rather than
    passing quietly (`quota.py`'s N1/N6b precedent; F135: a benign cause does
    not make a silent arm benign).
    """
    if not os.path.exists(TARBALL):
        return None
    out = subprocess.run(["tar", "-xzOf", TARBALL, MEMBER],
                         capture_output=True)
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else None


def census(src):
    """-> [(line, func, kind, text)] for every `if` testing `p->h == h`.

    `kind` is how the predicate settles the KEY KIND:
      'string'  -- `p->nKeyLength == nKeyLength` as a required conjunct
      'numeric' -- `p->nKeyLength == 0`          as a required conjunct
      'dual'    -- `p->nKeyLength == 0`          as a DISJUNCT that can
                   short-circuit the key comparison away entirely
      'guarded' -- a disjunct on the kind, but `== nKeyLength` hoisted OUT of
                   it into a required conjunct: THE R1h's OWN SHAPE
    ⛔ 'dual' is the defect shape and `:464` is expected to be its only member.

    ⚠⚠ THE 'guarded' CASE IS NOT DECORATION AND IT CAUGHT A REAL DEFECT IN THIS
    FUNCTION. The first version of this classifier tested only *"is there a
    `== 0` and a `||`"*, which is TRUE OF THE REPAIRED TEXT TOO -- `b73349dbe4e9`
    keeps both and merely hoists the length test in front of the `||`. So the
    census would have called the FIX defective and N6 would have passed on a
    repaired file. ▶ The discriminator is POSITIONAL: in the defect
    `== nKeyLength` sits AFTER the `||`, in the repair BEFORE it. N8 pins that
    by running the census over the actual post-image text.
    """
    lines = src.splitlines()
    fn, out = "?", []
    fndef = re.compile(r"^(ZEND_API|static)\b.*\(")
    for i, ln in enumerate(lines):
        if fndef.match(ln) and ";" not in ln:
            fn = ln.split("(")[0].split()[-1].lstrip("*")
        if "if (" not in ln:
            continue
        # join the condition across continuation lines until parens balance
        cond, depth = "", 0
        for j in range(i, min(i + 6, len(lines))):
            cond += " " + lines[j].strip()
            depth = cond.count("(") - cond.count(")")
            if depth <= 0:
                break
        if "p->h == h" not in cond:
            continue
        nk0 = "p->nKeyLength == 0" in cond
        nkn = "p->nKeyLength == nKeyLength" in cond
        if nk0 and "||" in cond:
            # positional: hoisted in front of the `||` == repaired (see docstring)
            kind = ("guarded" if nkn and cond.index("p->nKeyLength == nKeyLength")
                    < cond.index("||") else "dual")
        elif nk0:
            kind = "numeric"
        elif nkn:
            kind = "string"
        else:
            kind = "?"
        out.append((i + 1, fn, kind, " ".join(cond.split())))
    return out


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

    # ---- the predicate census (item 139). VACUOUS without the tarball. ----
    src = _zend_hash_c()
    if src is None:
        print(f"  ⓘ N6/N7 VACUOUS TODAY -- no tarball at {TARBALL}, so the "
              "census did not run. THE ARMS ARE NOT PASSING; they could not "
              "fire. Restore the tarball (patterns-php/SOURCES.md) to check "
              "item 139's reading for this row.")
    else:
        rows = census(src)
        dual = [r for r in rows if r[2] == "dual"]
        conj = [r for r in rows if r[2] in ("string", "numeric")]

        # N6 -- MUST-FIRE: exactly one dual-kind predicate, and it is the defect.
        ck("N6", len(dual) == 1 and dual[0][0] == 464 and
           dual[0][1] == "zend_hash_del_key_or_index",
           f"exactly ONE of the {len(rows)} `p->h == h` predicates settles the "
           "key kind by DISJUNCTION, and it is :464 in "
           f"zend_hash_del_key_or_index -- got {[(r[0], r[1]) for r in dual]}. "
           "⛔ If a second appears, the row's 'only site in the file' claim is "
           "wrong and the brief must say so.")

        # N7 -- MUST-FIRE: the repair's conjunct spelling was already the norm.
        ck("N7", len(conj) == len(rows) - 1 and len(conj) >= 9,
           f"the other {len(conj)} predicates ALL use the required-conjunct "
           "form the R1h adopts, so `F133`(i)'s 'strategy already present' "
           "holds here -- which is what REFUTES ROW13_001 §6's prediction. "
           "⚠ It does NOT mean a sibling faced :464's problem; see the "
           "docstring's two-way split.")

        # N8 -- MUST-FIRE, NON-VACUITY: the census must be able to SEE the
        # repair. This is b73349dbe4e9's own post-image text, and if the
        # classifier still called it `dual` then N6 would pass on a FIXED file
        # and the whole census would be measuring nothing.
        post = ('ZEND_API int zend_hash_del_key_or_index(HashTable *ht)\n{\n'
                '\t\tif ((p->h == h) \n'
                '\t\t\t && (p->nKeyLength == nKeyLength)\n'
                '\t\t\t && ((p->nKeyLength == 0) /* Numeric index */\n'
                '\t\t\t\t || !memcmp(p->arKey, arKey, nKeyLength))) {\n}\n')
        pk = [r[2] for r in census(post)]
        ck("N8", pk == ["guarded"],
           "fed the R1h's POST-IMAGE predicate, the census classifies it "
           f"'guarded', not 'dual' -- got {pk}. ⛔ The first draft of this "
           "classifier FAILED this arm: it keyed on `== 0` plus `||`, which "
           "the repair also has. An arm that cannot see the fix cannot "
           "certify the defect.")

    print("\nSELFTEST " + ("FAIL: " + " ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(f"{'string key':<10} {'h (zend_ulong)':>22} {'as a PHP int':>22}")
    for k in (b"abc", b"key", b"zz", b"x"):
        h, signed = collide(k)
        print(f"{k.decode():<10} {h:>22} {signed:>22}")

    print("\n--- item 139: every `p->h == h` predicate in Zend/zend_hash.c ---")
    src = _zend_hash_c()
    if src is None:
        print(f"ⓘ NOT RUN -- no tarball at {TARBALL}. This is a SKIP, not a "
              "clean result.")
    else:
        print(f"{'line':>5}  {'kind':<8} {'function':<40}")
        for line, fn, kind, _ in census(src):
            mark = "  ⛔ THE DEFECT" if kind == "dual" else ""
            print(f"{line:>5}  {kind:<8} {fn:<40}{mark}")
        print("▶ 'dual' = the key kind is settled by a DISJUNCT, so the key "
              "comparison can be short-circuited away. The R1h makes it a "
              "required conjunct -- the form every other row already uses.")

    print("\n⚠ Scoping only. Not an admission argument (CLAUDE.md rule 6).")
    sys.exit(0)
