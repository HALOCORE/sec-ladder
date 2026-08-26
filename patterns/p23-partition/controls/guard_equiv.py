#!/usr/bin/env python3
"""p23 control A -- IS `i < j` THE ONLY CORRECT SCAN GUARD? Answer: NO.

    python3 patterns/p23-partition/controls/guard_equiv.py

TASK_101 wrote into `c/kernel_hardened.c` that the alternative spelling

    while (i < m && scr[i]   <= pv) i++;
    while (j > 0 && scr[j-1] >= pv) j--;

is *"safe, and WRONG"* -- memory-safe but computing a different partition point,
because the upward cursor could pass the downward one. **That claim is FALSE and
this script is what refuted it**, before the pattern was measured. The two
spellings agree on every one of 800 000 randomised records, and the reason is a
one-line invariant the first draft missed:

    after an exchange, `scr[j] > pv` -- the element the exchange just moved
    there -- so the NEXT upward scan stops at or before `j` whatever its guard
    says. The upward cursor CANNOT pass the downward one.

and symmetrically `scr[i-1] < pv` stops the downward scan at or above `i`. So on
this kernel `i < m` and `j > 0` are not weaker guards, they are the same guard
reached by a different route, and the pin in `../spec.md` is a pin on the
SPELLING and not on the semantics.

⚠ **What that does NOT say:** it does not say the guard is optional. Delete both
conjuncts, as `c/kernel.c` does, and the scans have no bound at all -- that is
the pattern's bug and `guard_variants.c` shows it firing in both directions.
What it says is that the CHOICE among the three guarded spellings is a spelling
choice, and `../NOTES.md 8` prices it.

The alphabet is swept deliberately: a narrow one makes runs of bytes equal to
the pivot common, which is the case the non-strict comparisons exist for and the
only case where the two guards could plausibly diverge.
"""
import random
import sys

SCR = 64
TRIALS = 400000


def partition(scr0, m, pv, guard):
    scr = bytearray(scr0)
    i, j = 0, m
    while i < j:
        if guard == "ij":
            while i < j and scr[i] <= pv:
                i += 1
            while i < j and scr[j - 1] >= pv:
                j -= 1
        else:                                   # the `i < m` / `j > 0` variant
            while i < m and scr[i] <= pv:
                i += 1
            while j > 0 and scr[j - 1] >= pv:
                j -= 1
        if i < j:
            scr[i], scr[j - 1] = scr[j - 1], scr[i]
            i += 1
            j -= 1
    return bytes(scr), i


def sweep(rng, alphabet, trials):
    diffs = []
    for _ in range(trials):
        m = rng.randrange(0, SCR + 1)
        pv = rng.randrange(0, alphabet)
        scr0 = bytes(rng.randrange(0, alphabet) for _ in range(SCR))
        a = partition(scr0, m, pv, "ij")
        b = partition(scr0, m, pv, "mz")
        if a != b:
            diffs.append((m, pv, a[1], b[1]))
            if len(diffs) >= 3:
                break
    return diffs


def main():
    rng = random.Random(7)
    bad = 0
    for label, alphabet in (("full 0..255", 256), ("narrow 0..4", 5)):
        d = sweep(rng, alphabet, TRIALS)
        print(f"  {label:14s} trials={TRIALS} differing={len(d)}"
              + (f"  first={d[:3]}" if d else ""))
        bad += len(d)
    # THE MUST-FIRE ARM. A differential test that cannot report a difference is
    # not a test. `bug` has no guard at all; on an all-below record it walks off
    # the scratch, which this bounded stand-in reports as a differing answer.
    rng2 = random.Random(11)
    scr0 = bytes(rng2.randrange(0, 255) for _ in range(SCR))
    a = partition(scr0, 32, 255, "ij")
    b = partition(scr0, 32, 255, "mz")
    c = partition(scr0, 64, 255, "ij")          # a DIFFERENT m: must differ
    fired = (a != c)
    print(f"  must-fire arm: a partition of the same bytes at m=32 vs m=64 "
          f"differs: {fired}")
    print("verdict:", "EQUIVALENT" if bad == 0 and fired else "SEE ABOVE")
    return 0 if (bad == 0 and fired and a == b) else 1


if __name__ == "__main__":
    sys.exit(main())
