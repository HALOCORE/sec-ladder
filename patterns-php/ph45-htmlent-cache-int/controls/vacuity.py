#!/usr/bin/env python3
"""ph45 control -- IS THE PROOF VACUOUS? Five mutants, and one of them DOES NOT
FIRE.

    python3 patterns-php/ph45-htmlent-cache-int/controls/vacuity.py

`ph07` measured its own vacuity by replacing the kernel body with `0u64`
(`.memory-php/02-ladder.md`); `TASK_PHP_034_REPORT` §6.8 predicted a vacuity
problem for this row's R5 in particular, because Verus's raw-pointer API carries
provenance and *"the value read back designates the same allocation"* might be
true by typing. ⚠ IT IS NOT TRUE BY TYPING HERE, because the representation is
an INDEX and an index carries no provenance at all: `wf_ptr` has to be
established and carried, and V5 measures what happens when it is not.

Each mutant is written into `.temp/php45ctl/` and put through Verus. FOUR MUST
FAIL. The fifth is reported as REDUNDANT rather than quietly removed, because
*a declaration that cannot fail is worth writing only if you have measured that
it cannot*.

  V1  `kernel`'s body -> `0u64`                       MUST FAIL
  V2  `alloc`'s O1 range `ensures` deleted            ⚠ DOES NOT FAIL -- see below
  V3  `bset`'s `ensures` names only the written slot  MUST FAIL
  V4  `wf_c`'s `bump[r] <= REGION` deleted            MUST FAIL
  V5  `wf_ptr` weakened to `0 <= f.cache`             MUST FAIL

⚠⚠ V2 IS THE ONE THAT MATTERS. `alloc`'s third `ensures` --
`r == 0 || (0 < r && r + BLOCK <= ASZ)` -- is the human-readable statement of
`pointer-value-integrity` obligation O1, and deleting it STILL VERIFIES 41/0,
because `r == s_alloc_r(old(self).g(), n)` plus `wf_c`'s bump bound already pin
the range. It is REDUNDANT. It is kept because it is the only place in the file
where O1 is legible as O1, and V4 is what shows where the fact really lives.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
TMP = os.path.join(REPO, ".temp", "php45ctl")
SRC = os.path.join(ROW, "verus.rs")

MUTANTS = [
    ("V1", "kernel's body -> 0u64", True,
     ("    let win: &[u8] = slice_subrange(buf, off, off + len);\n    run(win, len)\n}",
      "    let win: &[u8] = slice_subrange(buf, off, off + len);\n    let _ = win;\n    0u64\n}")),
    ("V2", "alloc's O1 range ensures deleted", False,
     ("            r == 0 || (0 < r && r + BLOCK <= ASZ),\n", "")),
    ("V3", "bset's ensures names only the written slot", True,
     ("    ensures\n        final(v)@ == old(v)@.update(i as int, x),\n{\n    unsafe {\n        *v.get_unchecked_mut(i) = x;\n    }\n}",
      "    ensures\n        final(v)@[i as int] == x,\n        final(v)@.len() == old(v)@.len(),\n{\n    unsafe {\n        *v.get_unchecked_mut(i) = x;\n    }\n}")),
    ("V4", "wf_c's bump[r] <= REGION deleted", True,
     ("    &&& c.bump@[0] <= REGION\n    &&& c.bump@[1] <= REGION\n", "")),
    ("V5", "wf_ptr weakened to `0 <= f.cache` (O2 deleted)", True,
     ("pub open spec fn wf_ptr(f: Filt) -> bool {\n    &&& 0 < f.cache\n    &&& f.cache + BLOCK <= ASZ\n}",
      "pub open spec fn wf_ptr(f: Filt) -> bool {\n    &&& 0 <= f.cache\n}")),
]

RESULT = re.compile(r"verification results:: (\d+) verified, (\d+) errors")


def verus(path):
    r = subprocess.run([sys.executable, os.path.join(REPO, "verus_run.py"), path],
                       capture_output=True, text=True, cwd=REPO)
    log = r.stdout + r.stderr
    m = RESULT.search(log)
    errs = [ln for ln in log.splitlines() if ln.startswith("error: ")]
    return (m.group(1), m.group(2)) if m else ("?", "?"), errs


def main():
    os.makedirs(TMP, exist_ok=True)
    base = open(SRC, encoding="utf-8").read()
    print("baseline:", end=" ", flush=True)
    (v, e), _ = verus(SRC)
    print(f"{v} verified, {e} errors  (expected 41 / 0)")
    bad = 0 if (v, e) == ("41", "0") else 1

    for tag, what, must_fail, (a, b) in MUTANTS:
        if base.count(a) != 1:
            print(f"{tag}: ⚠ the mutation anchor no longer matches verus.rs "
                  f"({base.count(a)} occurrences) -- this control has DRIFTED")
            bad += 1
            continue
        p = os.path.join(TMP, f"vac_{tag}.rs")
        open(p, "w", encoding="utf-8").write(base.replace(a, b))
        (v, e), errs = verus(p)
        fired = e != "0"
        ok = fired == must_fail
        print(f"{tag}  {'MUST FAIL ' if must_fail else 'redundant  '} "
              f"{what:48s} -> {v} verified, {e} errors  "
              f"{'ok' if ok else '⚠ UNEXPECTED'}")
        for ln in errs[:2]:
            print(f"       | {ln}")
        if not ok:
            bad += 1

    print()
    print("EXPECTED: V1, V3, V4 and V5 fail; V2 verifies, because the clause it")
    print("deletes is REDUNDANT and `wf_c`'s bump bound is what carries O1.")
    print(f"-> {'PASS' if bad == 0 else 'FAIL'} ({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
