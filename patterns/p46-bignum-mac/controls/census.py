#!/usr/bin/env python3
"""p46 — the two tree-wide counts `../NOTES.md` 0c and 6d rest on, re-runnable.

Both were originally scratch files under `.temp/t89/`, and `.gitignore` contains
`.temp/`. `.memory/05-layout.md` step 11's corollary: **the more valuable the
residue, the more likely it is sitting in `.temp/`.** These two are the most
reusable things p46 produced and neither is about p46's own numbers, so they are
committed here rather than left in a task's scratch.

    controls/census.py --ensures    # 6d: is p46's `mac` postcondition novel?
    controls/census.py --mutsub     # 0c: can Verus specify a MUTABLE sub-slice?
    controls/census.py --all

`--ensures` RE-COUNTS rather than re-states. `TASK_086_REPORT` claimed p46's
`mac` clause was *"stronger than any `ensures` currently in the tree, all of
which are bounds facts"*; `TASK_089` §2 asked for it to be counted before it was
shipped, because *"the first termination proof in the project"* was a manager
sentence that was false and reached eight places, two of them inside
`contract_sha256`. **Counted, the claim is false**, and this is the command that
says so from the committed tree.

`--mutsub` writes four Verus probes and runs them. Three must verify and one
must FAIL; the failing one is the finding.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SCRATCH = os.path.join(REPO, ".temp", "check", "p46-controls")
sys.path.insert(0, os.path.join(REPO, "harness"))


# ---------------------------------------------------------------- 6d ----
def ensures_census(self_too):
    import vparse
    rows, files = [], sorted(glob.glob(os.path.join(REPO, "patterns",
                                                    "*", "verus.rs")))
    if not self_too:
        files = [f for f in files if "p46-" not in f]
    for f in files:
        src = open(f).read()
        for it in vparse.parse(src):
            cs = vparse.clause_spans(it)
            for a, b in cs.get("ensures", {}).get("spans", []):
                rows.append((os.path.basename(os.path.dirname(f)), it.name,
                             " ".join(src[a:b].split())))
    eq = [r for r in rows if "==" in r[2] or "=~=" in r[2]]
    ineq = [r for r in rows if r[2] not in (x[2] for x in eq)]
    kern = [r for r in rows if r[1] == "kernel"]
    print(f"{len(files)} verus.rs, {len(rows)} `ensures` conjuncts")
    print(f"  equalities (`==` or `=~=`) : {len(eq)}")
    print(f"  NOT equalities             : {len(ineq)}")
    for r in ineq:
        print(f"      {r[0]:22s} {r[1]:26s} {r[2]}")
    fold_re = re.compile(r"r == \w+_fold\(buf@,")
    n_fold = sum(1 for r in kern if fold_re.match(r[2]))
    print(f"  kernel postconditions      : {len(kern)}, of which "
          f"{n_fold} are of the form `r == <name>_fold(buf@, off, len)` -- "
          f"a FULL FUNCTIONAL postcondition, not a bound")
    print()
    print("VERDICT on TASK_086_REPORT's *\"all of which are bounds facts\"*: "
          f"FALSE by {len(eq)}/{len(rows)}.")
    print()
    # the claim that DID survive counting
    for label, pat in (("by (bit_vector)", r"by \(bit_vector\)"),
                       ("by (compute", r"by \(compute")):
        hits = []
        for f in sorted(glob.glob(os.path.join(REPO, "patterns", "*", "*.rs"))):
            if not self_too and "p46-" in f:
                continue
            code = "\n".join(re.sub(r"//.*", "", l)
                             for l in open(f).read().splitlines())
            n = len(re.findall(pat, code))
            if n:
                hits.append(f"{os.path.basename(os.path.dirname(f))}"
                            f"/{os.path.basename(f)} x{n}")
        print(f"{label:16s} in executable position: {len(hits)} file(s)"
              + (f" -- {hits}" if hits else ""))
    print()
    print("So what is new about p46's proof is the MODE, not the strength of "
          "the postcondition (../NOTES.md 6c, 6d).")


# ---------------------------------------------------------------- 0c ----
PROBES = {
    "mutsub_len": ("""    requires i + m + 1 <= 96,
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    assert(row@.len() == m + 1);
}""", "VERIFIES", "the sub-slice's LENGTH follows from the range"),
    "mutsub_frame": ("""    requires 1 <= i, i + m + 1 <= 96,
    ensures final(out)@[0] == old(out)@[0],
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    row[0] = 7;
}""", "VERIFIES", "the FRAME outside the sub-slice survives"),
    "mutsub_vanish": ("""    requires i + m + 1 <= 96,
    ensures final(out)@ =~= old(out)@,
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    row[0] = 7;
}""", "MUST FAIL", "the write does NOT vanish -- the model is sound"),
    "mutsub_value": ("""    requires i + m + 1 <= 96,
    ensures final(out)@[i as int] == 7,
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    row[0] = 7;
}""", "MUST FAIL", "**THE FINDING**: the written VALUE cannot be related back "
     "to the array, so no functional postcondition can be discharged through a "
     "mutable sub-slice at this pin"),
}

HEAD = """// p46 control -- generated by controls/census.py. See ../NOTES.md 0c.
use vstd::prelude::*;
verus!{
global size_of usize == 8;
broadcast use { vstd::slice::group_slice_axioms, vstd::array::group_array_axioms };

fn probe(out: &mut [u64; 96], i: usize, m: usize)
"""
TAIL = """
fn main() {}
}
"""


def mutsub():
    os.makedirs(SCRATCH, exist_ok=True)
    print("`slice_subrange` in the pinned vstd covers `&[T]` only, and "
          "`ExSliceIndex::index_mut` carries a `requires` and NO `ensures`.")
    print("Four probes; three must verify and one must fail.\n")
    bad = 0
    for name, (body, want, why) in PROBES.items():
        p = os.path.join(SCRATCH, name + ".rs")
        open(p, "w").write(HEAD + body + TAIL)
        r = subprocess.run([os.path.join(REPO, "verus_run.py"), p,
                            "--multiple-errors", "6"],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        m = re.search(r"(\d+) verified, (\d+) errors", out)
        got = "VERIFIES" if m and m.group(2) == "0" else "MUST FAIL"
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name:14s} {m.group(0) if m else '??':24s} "
              f"want {want:9s} -- {why}")
        try:
            os.unlink(p)
        except OSError:
            pass
    if bad:
        sys.exit(f"{bad} probe(s) disagreed with ../NOTES.md 0c -- either the "
                 f"pin moved or that section is now wrong")
    print("\n../NOTES.md 0c reproduces: a mutable sub-slice at this pin is "
          "SOUND but VALUELESS,\nso the cheapest unsafe spelling found "
          "(`r4_mutreslice`) is not an admissible rung.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ensures", action="store_true")
    ap.add_argument("--mutsub", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--include-p46", action="store_true",
                    help="count p46 too; the published figures EXCLUDE it, "
                         "because the question was what the tree looked like "
                         "BEFORE this pattern")
    a = ap.parse_args()
    if not (a.ensures or a.mutsub or a.all):
        ap.print_help()
        return
    if a.ensures or a.all:
        ensures_census(a.include_p46)
    if a.mutsub or a.all:
        print()
        mutsub()


if __name__ == "__main__":
    main()
