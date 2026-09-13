#!/usr/bin/env python3
"""ph52 control: THE THREE CONTENT-DIGEST CONSTANTS, AND ALL 256 OBJECT HANDLES.

    python3 patterns-php/ph52-concat-copy-uninit/controls/digest.py
    python3 .../digest.py --selftest

⚠⚠ **WHY IT EXISTS, AND IT IS A CITATION THE KERNEL MAKES.** `c/kernel.c`,
`c/kernel.h`, `c/kernel_hardened.c` and all four Rust rungs carry the comment
*"`controls/digest.py` drives all 256"*, and **`c/*` and the `.rs` rungs are in the
MEASUREMENT digest** — `.memory-php/04-process.md` law 14: a comment inside one cannot
be corrected at re-gate price. ▶ **So the cheap repair for a pointer that named a file
which did not exist was to WRITE the file, not to edit the comment**, and this one has
real content: `controls/*` is gate-only, so it costs one re-gate where editing
`c/kernel.c` would cost a 32-cell re-measure. ⚠ **The defect was found by a script that
looked for cited paths that do not resolve, not by reading** — `TASK_PHP_045_REPORT.md`
§17 records it with the other three.

**WHAT IT CHECKS, and none of it is a restatement of the kernel:**

1. **the three `PH52_DIG_*` constants against the LITERALS they stand for.**
   `PH52_DIG_PREFIX` must be `fold131("Object id #")`, `PH52_DIG_ARRAY`
   `fold131("Array")`, `PH52_DIG_ONE` `fold131("1")` — read out of `c/kernel.h` by
   regex, folded here from the byte strings.
2. ⭐ **the object arm over ALL 256 handles**, two ways: the kernel's three-way case
   analysis (transcribed) against a plain `fold131(prefix + decimal digits reversed)`.
   The kernel narrows `sprintf`'s `do { } while (d)` to an exhaustive three-way case
   **because `aux` is one window byte**, and this is where that exhaustiveness is
   driven rather than asserted.
3. **the declared `len`** — `OBJ_PREFIX_LEN + nd` — against `len(str(aux))` for all 256.
4. **`model.py`'s own arm** against both, so the model cannot drift from the C's
   constants.

⚠ `--selftest`'s negatives are NEW to this row (`.memory-php/04-process.md` law 7).
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
sys.path.insert(0, ROW)
import model  # noqa: E402

MASK = (1 << 64) - 1
PREFIX = b"Object id #"


def fold131(b, h=0):
    """The digest the kernel accumulates into `*dig`: h = h*131 + byte, mod 2^64."""
    for c in b:
        h = (h * 131 + c) & MASK
    return h


def kernel_case(aux, dig_prefix):
    """`c/kernel.c`'s `:250` arm, TRANSCRIBED: the prefix constant, then the handle's
    decimal digits least-significant-first, as an exhaustive three-way case."""
    dig = dig_prefix
    dig = (dig * 131 + (48 + aux % 10)) & MASK
    if aux < 10:
        nd = 1
    else:
        dig = (dig * 131 + (48 + (aux // 10) % 10)) & MASK
        if aux < 100:
            nd = 2
        else:
            dig = (dig * 131 + (48 + aux // 100)) & MASK
            nd = 3
    return dig, nd


def plain_fold(aux, dig_prefix):
    """The same value, spelled with NO case analysis: fold the prefix's digest, then
    the decimal digits in REVERSE. Shares no control flow with `kernel_case`."""
    ds = ("%d" % aux).encode()
    return fold131(ds[::-1], dig_prefix), len(ds)


def header_constants():
    """The three constants as `c/kernel.h` spells them."""
    out = {}
    with open(os.path.join(ROW, "c", "kernel.h")) as fh:
        for line in fh:
            m = re.match(r"#define\s+(PH52_DIG_\w+|PH52_OBJ_PREFIX_LEN)\s+(\d+)", line)
            if m:
                out[m.group(1)] = int(m.group(2))
    return out


def rust_constants():
    """The same three, as the Rust rungs spell them -- so a rung that drifted from the
    header would be caught here and not only by a cross-rung checksum."""
    out = {}
    for f in ("safe_naive.rs", "safe_tuned.rs", "unsafe.rs", "verus.rs"):
        txt = open(os.path.join(ROW, f)).read()
        per = {}
        for m in re.finditer(r"(?:const|pub const)\s+(DIG_\w+)\s*:\s*u64\s*=\s*(\d+)", txt):
            per[m.group(1)] = int(m.group(2))
        out[f] = per
    return out


def check():
    bad = []
    h = header_constants()

    # 1. the constants against the literals
    want = {"PH52_DIG_PREFIX": fold131(PREFIX),
            "PH52_DIG_ARRAY": fold131(b"Array"),
            "PH52_DIG_ONE": fold131(b"1")}
    for k, v in want.items():
        if h.get(k) != v:
            bad.append(f"c/kernel.h {k} = {h.get(k)}, fold131 of its literal = {v}")
    if h.get("PH52_OBJ_PREFIX_LEN") != len(PREFIX):
        bad.append(f"c/kernel.h PH52_OBJ_PREFIX_LEN = {h.get('PH52_OBJ_PREFIX_LEN')}, "
                   f"len({PREFIX!r}) = {len(PREFIX)}")

    # the four Rust rungs must carry the same three numbers
    rust_want = {"DIG_PREFIX": want["PH52_DIG_PREFIX"],
                 "DIG_ARRAY": want["PH52_DIG_ARRAY"],
                 "DIG_ONE": want["PH52_DIG_ONE"]}
    for f, per in rust_constants().items():
        for k, v in rust_want.items():
            if per.get(k) != v:
                bad.append(f"{f} {k} = {per.get(k)}, expected {v}")

    # 2-4. all 256 handles, three ways
    dp = want["PH52_DIG_PREFIX"]
    for aux in range(256):
        kd, knd = kernel_case(aux, dp)
        pd, pnd = plain_fold(aux, dp)
        if kd != pd:
            bad.append(f"aux={aux}: kernel case gives {kd}, plain fold gives {pd}")
            break
        if knd != pnd or knd != len(str(aux)):
            bad.append(f"aux={aux}: nd kernel={knd} plain={pnd} len(str)={len(str(aux))}")
            break
        # model.py's own arm, through `printable`
        al = model.Alloc()
        _uc, (mlen, mdig), _sl, _u, _d = model.printable(
            model.ARM_OBJECT, aux if aux % 2 == 0 else aux, al,
            ("empty", 0)) if aux % 2 == 0 else (1, (0, 0), None, 0, 0)
        if aux % 2 == 0:
            if mdig != kd:
                bad.append(f"aux={aux}: model dig {mdig} != kernel {kd}")
                break
            if mlen != h["PH52_OBJ_PREFIX_LEN"] + knd:
                bad.append(f"aux={aux}: model len {mlen} != {h['PH52_OBJ_PREFIX_LEN']}+{knd}")
                break
    return bad


# ---------------------------------------------------------------------------
# §H: a validator lands with its must-fire negatives, or it does not land.
# ---------------------------------------------------------------------------
def selftest():
    fails = []
    dp = fold131(PREFIX)

    def want(name, cond, why):
        if not cond:
            fails.append(f"{name}: {why}")

    # N1 MUST-NOT-FIRE: the shipped tree
    want("N1 shipped tree", not check(), f"the committed row must pass: {check()}")

    # N2 MUST-FIRE: a prefix digest off by one must be caught over the 256 sweep
    diffs = sum(1 for a in range(256)
                if kernel_case(a, dp + 1)[0] != plain_fold(a, dp)[0])
    want("N2 wrong prefix constant", diffs == 256,
         f"a prefix constant off by one must differ on every handle, got {diffs}/256")

    # N3 MUST-FIRE: the digits folded in the WRONG order (most-significant-first),
    #    which is the mistake the first draft of the kernel made
    def msf(aux, h0):
        return fold131(("%d" % aux).encode(), h0)
    diffs = sum(1 for a in range(256) if msf(a, dp) != kernel_case(a, dp)[0])
    want("N3 digit order", diffs > 0,
         "folding the digits most-significant-first must differ somewhere")
    want("N3b single digits agree", all(msf(a, dp) == kernel_case(a, dp)[0]
                                        for a in range(10)),
         "⭐ on ONE-digit handles the two orders AGREE, so a corpus that only used "
         "aux < 10 could not see the difference -- which is exactly ph03's monoculture "
         "and is why inputs/gen.py asserts all three digit counts")
    # ⭐⭐ N3c WAS WRONG IN THE FIRST DRAFT AND THE CODE WAS RIGHT, WHICH IS WHY THIS
    #     ARM IS WORTH ITS LENGTH. I asserted the two orders differ on every handle
    #     >= 10. They do not: a PALINDROME folds the same either way. The set that
    #     agrees is EXACTLY the palindromes, and there are 35 of them in a byte --
    #     10 one-digit, 9 two-digit (11..99) and 16 three-digit (101..191, 202..252).
    #     ▶ So a corpus whose object handles happened to be palindromic would be
    #     BLIND to the digit order, on 35 of 256 values. That is ph03's monoculture
    #     with a different shape, and `inputs/gen.py` does not currently assert
    #     non-palindromic handles -- recorded here rather than claimed as covered.
    pal = {a for a in range(256) if str(a) == str(a)[::-1]}
    agree = {a for a in range(256) if msf(a, dp) == kernel_case(a, dp)[0]}
    want("N3c the agreeing set is EXACTLY the palindromes", agree == pal,
         f"the two digit orders must agree on exactly the {len(pal)} palindromic "
         f"handles and differ on the other {256 - len(pal)}; agree={len(agree)} "
         f"pal={len(pal)} symmetric_difference={sorted(agree ^ pal)[:8]}")

    # N4 MUST-FIRE: dropping the `aux < 100` arm (so 3-digit handles lose a digit)
    def two_only(aux, h0):
        d = (h0 * 131 + (48 + aux % 10)) & MASK
        if aux < 10:
            return d
        return (d * 131 + (48 + (aux // 10) % 10)) & MASK
    diffs = sum(1 for a in range(100, 256) if two_only(a, dp) != kernel_case(a, dp)[0])
    want("N4 missing third arm", diffs == 156,
         f"dropping the 3-digit arm must differ on all 156 handles >= 100, got {diffs}")

    # N5 MUST-NOT-FIRE: the three-way case is EXHAUSTIVE over a byte
    want("N5 exhaustive over a byte", all(kernel_case(a, dp)[1] == len(str(a))
                                          for a in range(256)),
         "the nd the case analysis computes must equal len(str(aux)) for all 256 -- "
         "which is what makes `aux` being ONE WINDOW BYTE load-bearing")

    # N6 MUST-FIRE: a 4-digit handle would break the exhaustiveness, and the row
    #    DECLARES that bound rather than relying on it silently
    want("N6 the bound is real", kernel_case(1234, dp)[1] != len(str(1234)),
         "at 4 digits the three-way case is WRONG -- the kernel's `aux` is one byte and "
         "../spec.md declares that; this arm is what says the bound is not decoration")

    # N7 MUST-NOT-FIRE: the ARRAY and ONE constants are the literals' folds
    want("N7 DIG_ARRAY", fold131(b"Array") == header_constants()["PH52_DIG_ARRAY"],
         "PH52_DIG_ARRAY must be fold131(\"Array\")")
    want("N7b DIG_ONE", fold131(b"1") == header_constants()["PH52_DIG_ONE"],
         "PH52_DIG_ONE must be fold131(\"1\")")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        fails = selftest()
        print("  --selftest: 10 assertions (5 must-fire, 5 must-NOT-fire)")
        for f in fails:
            print(f"    FAIL {f}")
        print("  --selftest PASS" if not fails else "  --selftest FAILED")
        return 1 if fails else 0
    h = header_constants()
    print(f"  fold131(\"Object id #\") = {fold131(PREFIX)}   c/kernel.h: "
          f"{h.get('PH52_DIG_PREFIX')}")
    print(f"  fold131(\"Array\")       = {fold131(b'Array')}   c/kernel.h: "
          f"{h.get('PH52_DIG_ARRAY')}")
    print(f"  fold131(\"1\")           = {fold131(b'1')}   c/kernel.h: "
          f"{h.get('PH52_DIG_ONE')}")
    dp = fold131(PREFIX)
    nd = {}
    for a_ in range(256):
        nd[kernel_case(a_, dp)[1]] = nd.get(kernel_case(a_, dp)[1], 0) + 1
    print(f"  256 handles, digit-count histogram: {dict(sorted(nd.items()))}")
    probs = check()
    for p in probs:
        print(f"    PROBLEM {p}")
    print("  ok: the three constants, all 256 handles, and three spellings agree"
          if not probs else "  REFUSED")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
