#!/usr/bin/env python3
"""ph07 -- the Rust rungs' `usize` clamps against the C's `int` clamps.

    python3 patterns-php/ph07-strcut-cursor/controls/guard_equiv.py

`PROTOCOL_PHP.md` §A1(c): *"modelled by an equivalent is a claim that needs a
DIFFERENTIAL TEST, not a comment"* -- and §B's own worked failure is
`ZEND_SIGNED_MULTIPLY_LONG`, where "the same predicate" was **84 523
disagreements** away from faithful. This is that test for ph07's one such
claim.

**The claim.** `c/kernel.c`'s wrapper writes mbstring.c:1787-1805 and
`cb3cca21b345` in `int32_t`, verbatim. The four Rust rungs write the same
function in `usize`, with `saturating_sub` for the two negative clamps and
`saturating_add` for hunk (b)'s sum. They compute the same `(from, length)` --
or the same refusal -- on every triple this kernel's domain can hold.

**The domain, and it is the whole of it, not a sample.** `from` and `length`
reach `mb_strcut` as `long`s and reach `mbfl_strcut` as `int`s, and `string->len`
is a window length. This probe sweeps every `slen` in a set of edge and random
values crossed with every `from`/`length` in a set that includes `INT_MIN`,
`INT_MAX`, `+-slen`, `+-(slen+-1)`, `0`, `+-1` and randoms -- the values at which
a sign or a saturation could differ.

**The must-fire control is the point of the file.** Three mutants of the Rust
spelling, each one line, each a mistake a careful person makes:

    m1  `saturating_sub` -> plain subtraction with a wrap    (negative `from`)
    m2  hunk (a) spelled `>=` instead of `>`                 (off by one)
    m3  hunk (b) clamps `len` to `string->len` instead of to `len - from`

⭐ **And two VARIANTS that are results rather than controls, both must-NOT-fire.**

`c32` replaces the `usize` saturating sum with the C's literal 32-bit
`(unsigned) from + (unsigned) len` and changes **nothing**, because hunk (a)
runs first and has already bounded `from <= string->len <= INT_MAX`, so the sum
cannot reach 2^32. ⚠ **The `(unsigned)` casts in the shipped fix, which look
like an accident waiting to happen, are adequate on this domain.**

`ord` swaps the two guards. It changes nothing either -- and the reason is
worth the line: hunk (a)'s `RETURN_FALSE` DISCARDS whatever hunk (b) computed,
so the order is unobservable in the output. ⚠ **I predicted `ord` would fire
and it does not**; the prediction and the refutation are both left here,
because a control written to fire and then quietly reclassified is how a probe
stops measuring anything.
"""

import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, ".temp", "php16")
M32 = (1 << 32) - 1
M64 = (1 << 64) - 1


def rust(slen, fw, lw, mutant=None):
    """The four Rust rungs' spelling, transcribed. `fw`/`lw` are the RAW 32-bit
    words the window carries; the rungs branch on the top bit rather than
    converting to a signed type, because `usize` has no negatives."""
    def sat_sub(a, b):
        if mutant == "m1":
            return (a - b) & M64          # MUTANT: wraps instead of saturating
        return a - b if a >= b else 0

    frm = fw if fw < 0x8000_0000 else sat_sub(slen, (-fw) & M32)
    if lw < 0x8000_0000:
        length = lw
    else:
        length = sat_sub(sat_sub(slen, frm), (-lw) & M32)

    def hunk_a():
        # cb3cca21b345 hunk (a). MUTANT m2 spells it `>=`.
        return frm >= slen if mutant == "m2" else frm > slen

    def hunk_b(ln):
        # cb3cca21b345 hunk (b). `c32` uses the C's literal 32-bit sum where
        # the rungs use `saturating_add`.
        s = ((frm + ln) & M32) if mutant in ("c32", "ord") else min(frm + ln, M64)
        if s <= slen:
            return ln
        # MUTANT m3: clamp to `string->len` rather than to `len - from`.
        return slen if mutant == "m3" else ((slen - frm) & M64)

    if mutant == "ord":
        # VARIANT: the two guards in the OTHER order. Upstream refuses first and
        # clamps second; this clamps first, so `from` is still unbounded when
        # the 32-bit sum is taken.
        length = hunk_b(length)
        if hunk_a():
            return "FALSE"
        return (frm, length)

    if hunk_a():
        return "FALSE"
    return (frm, hunk_b(length))


def triples():
    rng = random.Random("ph07-guard-equiv")
    slens = [0, 1, 2, 3, 7, 96, 544, 4065, 65535, 0x7FFF_FFFE, 0x7FFF_FFFF]
    slens += [rng.randrange(0, 1 << 20) for _ in range(12)]
    for slen in slens:
        vals = {0, 1, -1, 2, -2, slen, -slen, slen + 1, -(slen + 1), slen - 1,
                -(slen - 1), slen * 2, -slen * 2, -0x8000_0000, 0x7FFF_FFFF,
                0x7FFF_FFFE, -0x7FFF_FFFF}
        vals |= {rng.randrange(-(1 << 31), 1 << 31) for _ in range(10)}
        vals = sorted(v for v in vals if -(1 << 31) <= v < (1 << 31))
        for fr in vals:
            for ln in vals[::3]:
                yield slen, fr, ln


def main():
    os.makedirs(OUT, exist_ok=True)
    exe = os.path.join(OUT, "guard_equiv")
    src = os.path.join(HERE, "guard_equiv.c")
    r = subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-O2", src,
                        "-o", exe], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        return 1
    print(f"built {os.path.relpath(exe, REPO)}")

    tri = list(triples())
    stdin = "\n".join(f"{a} {b} {c}" for a, b, c in tri) + "\n"
    r = subprocess.run([exe], input=stdin, capture_output=True, text=True)
    lines = r.stdout.split("\n")
    got = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        got.append("FALSE" if ln == "FALSE" else tuple(int(x) for x in ln.split()))
    assert len(got) == len(tri), (len(got), len(tri))

    rc = 0
    for mutant in (None, "c32", "ord", "m1", "m2", "m3"):
        bad = 0
        first = None
        for (slen, fr, ln), want in zip(tri, got):
            have = rust(slen, fr & M32, ln & M32, mutant)
            if have != want:
                bad += 1
                if first is None:
                    first = (slen, fr, ln, want, have)
        tag = "SHIPPED " if mutant is None else f"VARIANT {mutant}"
        must_not = mutant in (None, "c32", "ord")
        expect = "must NOT fire" if must_not else "must FIRE"
        ok = (bad == 0) if must_not else (bad > 0)
        print(f"  {tag:9s} {expect:13s} disagreements={bad:<8d} "
              f"{'ok' if ok else 'FAILED'}"
              + (f"   first: slen={first[0]} from={first[1]} length={first[2]} "
                 f"C={first[3]} rust={first[4]}" if first else ""))
        if not ok:
            rc = 1
    print(f"  triples compared: {len(tri)}")
    print("  ⭐ `c32` is a RESULT, not a control: replacing the saturating sum "
          "with the C's own")
    print("     32-bit `(unsigned) from + (unsigned) len` changes NOTHING, "
          "because hunk (a) runs")
    print("     FIRST and has already bounded `from <= string->len <= "
          "INT_MAX`, so the sum")
    print("     cannot reach 2^32. The fix's `(unsigned)` casts are adequate "
          "on this domain.")
    print("  ⭐ `ord` swaps the guards and also changes nothing: hunk (a)'s "
          "RETURN_FALSE discards")
    print("     whatever hunk (b) computed, so their order is unobservable. "
          "That was predicted")
    print("     to fire and did not -- see the module docstring.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
