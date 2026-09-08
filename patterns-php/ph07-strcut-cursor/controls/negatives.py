#!/usr/bin/env python3
"""ph07 -- the Verus mutants, and what each one is evidence FOR.

    python3 patterns-php/ph07-strcut-cursor/controls/negatives.py          # run all
    python3 patterns-php/ph07-strcut-cursor/controls/negatives.py --emit X # print one

A `verification results:: N verified, 0 errors` line is only evidence if
something could have made it say otherwise. `.memory/04-verus.md`: a
postcondition nothing consumes, a `requires` nothing can satisfy and a lemma
nobody needs all verify perfectly. These four mutants are what stops that
being true here.

    noguard   MUST FAIL   delete BOTH `cb3cca21b345` hunks -- i.e. turn R5
                          back into `c/kernel.c`.
                          ⭐ This is the whole row: with `from > string->len`
                          admitted, `get_unchecked(s, n)`'s `i < v@.len()` is
                          unprovable, which is exactly the over-read ASan
                          reports at c/kernel.c:171. **The proof refuses the
                          program PHP shipped for six releases.**
                          ⚠ It deletes both hunks and not just (a) because
                          hunk (b)'s `slen - frm` needs `frm <= slen` too, so a
                          hunk-(a)-only mutant fails on an ARITHMETIC
                          underflow one line later and never reaches the walk.
                          Measured: `.temp/php16/13-noguard.log`.
    nopos     MUST FAIL   make `mbtab_of` return 0 for one lead-byte class.
                          The start walk's `decreases` stops decreasing --
                          `mbfl_strcut` is not provably terminating without
                          "every table entry is >= 1".
    notable   MUST FAIL   change ONE entry of the literal `MBTAB`.
                          `lemma_mbtab_matches` is what ties the closed-form
                          spec to the 256 bytes lifted from
                          mbfilter_utf8.c:39-56; without this the closed form
                          would be a free-floating axiom about a table nobody
                          checked.
    noconsume MUST PASS   delete `main`'s `assert(r == strcut_fold(...))`.
                          ⚠ A must-PASS control is a WEAKER instrument than a
                          must-FAIL one -- it shows the postcondition is
                          unconsumed decoration unless something reads it, and
                          it cannot show that the file is still being mutated.
                          `noguard` shares the emit path and IS must-FAIL, so a
                          `negatives.py` that had stopped editing anything
                          would be caught there.

⚠ Every anchor is validated BEFORE any edit is applied, because one edit can
destroy the next one's anchor and a mutant that silently became a no-op is a
control that reports success for the wrong reason.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(ROW, "..", ".."))
SRC = os.path.join(ROW, "verus.rs")
TMP = os.path.join(REPO, ".temp", "php16")

MUTANTS = {
    "noguard": ("FAIL", [(
        """    // cb3cca21b345 hunk (a) -- the line every `get_unchecked` below rests on.
    if frm > slen {
        assert(strcut_fold(buf@, off as int, len as int) == 0xFFFF_FFFFu64);
        return 0xFFFF_FFFFu64;
    }
    // cb3cca21b345 hunk (b).
    let length: usize = if frm.saturating_add(length) > slen {
        slen - frm
    } else {
        length
    };
    assert(length as int == (if f0 + l0 > slq { slq - f0 } else { l0 }));""",
        """    // MUTANT noguard: BOTH cb3cca21b345 hunks DELETED -- this is
    // c/kernel.c, and it is the whole of what R1h adds.""")]),
    "nopos": ("FAIL", [(
        """    } else if b < 0xFE {
        6
    } else {
        1
    }
}""",
        """    } else if b < 0xFE {
        6
    } else {
        0
    }
}""")]),
    "notable": ("FAIL", [(
        """    4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 1, 1,
];""",
        """    4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 1, 2,
];""")]),
    "noconsume": ("PASS", [(
        """            assert(r == strcut_fold(buf@, (k * stride) as int, stride as int));""",
        """            // MUTANT noconsume: the postcondition is not consumed.""")]),
}


def emit(name):
    txt = open(SRC).read()
    _, edits = MUTANTS[name]
    for old, _new in edits:                       # validate ALL first
        if txt.count(old) != 1:
            sys.exit(f"negatives.py: anchor for {name!r} occurs "
                     f"{txt.count(old)} times in verus.rs, want exactly 1. "
                     f"The mutant would be a no-op or ambiguous; refusing.")
    for old, new in edits:
        txt = txt.replace(old, new)
    return txt


def run_one(name):
    expect, _ = MUTANTS[name]
    path = os.path.join(TMP, f"verus_{name}_tmp.rs")
    os.makedirs(TMP, exist_ok=True)
    before = open(SRC, "rb").read()
    open(path, "w").write(emit(name))
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path],
                       capture_output=True, text=True, cwd=REPO, timeout=1800)
    out = (r.stdout + r.stderr).strip()
    line = [l for l in out.splitlines() if "verification results" in l]
    got = "PASS" if line and line[0].endswith("0 errors") else "FAIL"
    os.remove(path)
    assert open(SRC, "rb").read() == before, "verus.rs was modified in place!"
    print(f"  {name:10s} expect {expect:4s} got {got:4s}  "
          f"{line[0].strip() if line else out[-160:]}  "
          f"{'ok' if got == expect else 'MISMATCH'}")
    return got == expect


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit", choices=sorted(MUTANTS))
    a = ap.parse_args()
    if a.emit:
        sys.stdout.write(emit(a.emit))
        return 0
    ok = True
    for name in MUTANTS:
        ok = run_one(name) and ok
    import hashlib
    print(f"  verus.rs sha256 unchanged: "
          f"{hashlib.sha256(open(SRC,'rb').read()).hexdigest()[:16]}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
