#!/usr/bin/env python3
"""ph16 -- the two spellings of `99e290f882c9` guard (b), differenced
EXHAUSTIVELY over the whole reachable domain.

    python3 patterns-php/ph16-fdset-index/controls/guard_equiv.py

`../spec.md`'s `provenance.divergences` records a SUBSTITUTION:

    c/kernel_hardened.c, safe_naive.rs        `this_fd < FD_SETSIZE`
    safe_tuned.rs, unsafe.rs, verus.rs        `w < NW`, where `w = this_fd / 64`

`PROTOCOL_PHP.md` §A1(c) says a substitution in a non-`modelled` tier must be
**DEMONSTRATED** behaviour-preserving over the reachable domain by a
differential with a must-fire control -- not asserted. `§B`'s worked failure is
`ZEND_SIGNED_MULTIPLY_LONG`, where *"modelled by an equivalent builtin"* was
**84 523 disagreements** away from faithful.

The domain is not a sample: `this_fd` is `PH16_IDX(e)`, a 14-bit field, so it is
**exactly `0 ..= 16383`** and this file drives every one of them. Three
implementations are compared per value:

    C          `controls/guard_equiv.c`, which asks the PLATFORM's own `FD_SET`
               which word and bit it touched, read back out of a real `fd_set`
    upstream   `f < FD_SETSIZE`, in Python
    wordindex  `f / 64 < NW`, in Python

and what is compared is the pair `(writes?, word, bit)` -- not just the verdict,
because two spellings could agree on *whether* to write and disagree on
*where*.

CONTROLS (`PROTOCOL_PHP.md` §H -- a validator lands with its negatives):

  must-fire      `--mutate off-by-one` scores `f <= FD_SETSIZE` against the C.
                 It MUST disagree, on exactly one value (1024), and if it does
                 not this file is not comparing anything. ⚠ It is the sharpest
                 available mutant BECAUSE it is one value wide: a mutant that
                 disagreed everywhere would pass a differential that only
                 counted disagreements and never located them.
  must-fire #2   `--mutate mask` scores `f & 1023` -- the "repair" `../spec.md`
                 `forbidden[0]` bans -- and it MUST disagree. ⚠ MEASURED: it
                 disagrees **15 360 times in the VERDICT column**, not in the
                 word column, because masking makes the spelling write for every
                 `this_fd` instead of skipping the out-of-range ones. The first
                 draft of this docstring predicted the opposite and was wrong;
                 the number is what it says now. The word column stays at 0 for
                 every mutant here, so on THIS row it is an unexercised half of
                 the comparison and is kept because a spelling that wrote in the
                 right cases and the wrong place is the failure it exists for.
  must-fire #3   `--mutate shift` scores `f / 32 < NW`, a plausible typo. MUST
                 disagree.
  must-NOT-fire  the shipped pair, over all 16 384 values: ZERO disagreements.

A run that cannot evaluate says so and exits non-zero.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php25", "guard_equiv")
GCC = "/usr/bin/gcc"
FD_SETSIZE = 1024
NW = 16
DOMAIN = 16384                      # PH16_IDX is 14 bits: 0 ..= 16383
ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}


def c_table():
    """(writes, word, bit) per `this_fd`, from a build of the C."""
    os.makedirs(SCRATCH, exist_ok=True)
    exe = os.path.join(SCRATCH, "guard_equiv")
    r = subprocess.run([GCC, "-std=c99", "-Wall", "-Wextra", "-O2",
                        os.path.join(HERE, "guard_equiv.c"), "-o", exe],
                       capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        return None, (r.stdout + r.stderr).strip()
    r = subprocess.run([exe], capture_output=True, text=True, env=ENV,
                       timeout=600)
    if r.returncode != 0 or "CANNOT EVALUATE" in r.stdout:
        return None, r.stdout.strip() + r.stderr.strip()
    out = {}
    for line in r.stdout.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fd, up, wi, word, bit = (int(x) for x in line.split())
        out[fd] = (up, wi, word, bit)
    if len(out) != DOMAIN:
        return None, f"the C probe printed {len(out)} rows, want {DOMAIN}"
    return out, None


SPELLINGS = {
    "upstream": lambda f: (f < FD_SETSIZE, f // 64, f % 64),
    "wordindex": lambda f: (f // 64 < NW, f // 64, f % 64),
    # --- mutants, all of which MUST disagree -------------------------------
    "off-by-one": lambda f: (f <= FD_SETSIZE, f // 64, f % 64),
    "mask": lambda f: (True, (f & 1023) // 64, (f & 1023) % 64),
    "shift": lambda f: (f // 32 < NW, f // 64, f % 64),
}


def score(name, ctab):
    """Disagreements between `name` and the C's own (writes, word, bit)."""
    fn = SPELLINGS[name]
    verdict_bad, place_bad, first = 0, 0, None
    for fd in range(DOMAIN):
        up, wi, cword, cbit = ctab[fd]
        writes, word, bit = fn(fd)
        # The C probe writes when EITHER shipped spelling says so, and reports
        # the word/bit it touched; where neither writes it reports -1/-1.
        c_writes = bool(up)
        if writes != c_writes:
            verdict_bad += 1
            first = first or (fd, "verdict", writes, c_writes)
        elif writes and (word, bit) != (cword, cbit):
            place_bad += 1
            first = first or (fd, "place", (word, bit), (cword, cbit))
    return verdict_bad, place_bad, first


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mutate", choices=("off-by-one", "mask", "shift"))
    args = ap.parse_args()

    if not os.path.exists(GCC):
        print(f"CANNOT EVALUATE: no gcc at {GCC}")
        return 2
    ctab, err = c_table()
    if ctab is None:
        print(f"CANNOT EVALUATE: the C probe did not run: {err}")
        return 2
    print(f"domain: this_fd in 0..{DOMAIN - 1} (PH16_IDX is 14 bits), "
          f"{DOMAIN} values, all driven")

    bad = 0
    names = [args.mutate] if args.mutate else list(SPELLINGS)
    for name in names:
        v, p, first = score(name, ctab)
        shipped = name in ("upstream", "wordindex")
        tag = "must-NOT-fire" if shipped else "must-fire"
        okd = (v == 0 and p == 0) if shipped else (v + p > 0)
        print(f"  {tag:14s} {name:11s} verdict-disagreements={v:<6d} "
              f"place-disagreements={p:<6d} "
              f"{'PASS' if okd else 'FAIL'}"
              + (f"   first: {first}" if first else ""))
        if not okd:
            bad += 1

    # The sharper half of must-fire #1: the off-by-one mutant must disagree on
    # EXACTLY ONE value, and that value must be FD_SETSIZE. A differential that
    # counted only totals would call a mutant disagreeing everywhere a pass.
    if args.mutate in (None, "off-by-one"):
        diffs = [f for f in range(DOMAIN)
                 if SPELLINGS["off-by-one"](f)[0] != bool(ctab[f][0])]
        okd = diffs == [FD_SETSIZE]
        print(f"  must-fire      off-by-one LOCATED at {diffs} "
              f"{'PASS' if okd else 'FAIL'} -- the guard's test is `<` and not "
              f"`<=`, so 1024 is the ONE value that separates them, and this "
              f"row's `adversarial-redzone.bin` is built on exactly it")
        if not okd:
            bad += 1

    print("\nRESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
