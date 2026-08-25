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

`--mutsub` settles whether a MUTABLE sub-slice is usable at the pinned vstd.

⚠⚠ **IT USED TO ENFORCE THE WRONG VERDICT.** Until TASK_092 it ran four probes
and exited non-zero **unless the fourth FAILED**, on the strength of a claim
that a mutable sub-slice at this pin is *"sound but valueless"*. That claim is
false (TASK_089_REVIEW B1): `vstd/slice.rs`'s `ExSliceIndex` is a **trait
declaration**, not the specification, and `~/tools/verus/vstd/std_specs/slice.rs`
ships a full **value-level** `assume_specification` for
`<Range<usize> as SliceIndex<[T]>>::index_mut`. The fourth probe verifies with
**one** added lemma call, and `r4_mutreslice`'s **full R5 verifies too**.

What this control now asserts, and every line of it is a verdict:

  1. the pinned vstd has **zero** `get_unchecked` specifications -- so the
     mutreslice R5 needs two NEW trusted items, which is disqualifier (a);
  2. `std_specs/slice.rs` DOES carry the value-level `index_mut` spec;
  3. five probes: the frame survives, the length follows, the write does not
     vanish (**must fail** -- that one is soundness), the value is unreachable
     **without** the lemma (**must fail**) and reachable **with** it;
  4. the full `v46_mutreslice` R5 from `controls/mkvariants.py`:
     **`21 verified, 0 errors`**;
  5. two mutations of it, both of which **must fail** -- so the proof is not
     vacuous.

It runs Verus eight times and takes a few minutes.
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
#: The lemma that closes the value probe. ONE line, and its absence is the whole
#: of what the retracted version of this control measured.
BRIDGE = ("    proof { vstd::seq::lemma_seq_subrange_index("
          "out@, i as int, (i + m + 1) as int, 0); }\n")

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
    "mutsub_value_nolemma": ("""    requires i + m + 1 <= 96,
    ensures final(out)@[i as int] == 7,
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    row[0] = 7;
}""", "MUST FAIL", "the value probe WITHOUT the subrange-index lemma. This is "
     "the exact probe that stood as *the* finding until TASK_092 -- it fails, "
     "and failing means only that Z3 was not handed the bridging lemma"),
    "mutsub_value": ("""    requires i + m + 1 <= 96,
    ensures final(out)@[i as int] == 7,
{
    let row: &mut [u64] = &mut out[i..i + m + 1];
    row[0] = 7;
""" + BRIDGE + "}", "VERIFIES",
     "**THE CORRECTION**: with ONE lemma call the written VALUE IS related back "
     "to the array. `~/tools/verus/vstd/std_specs/slice.rs` has the value-level "
     "`index_mut` spec; `vstd/slice.rs`'s `ExSliceIndex` is a trait declaration "
     "and not the specification"),
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

#: The two mutations of the full R5. Each must make it FAIL, or the proof is
#: decoration (`.memory/04-verus.md`: nothing but mutation testing defends a
#: postcondition).
R5_MUTATIONS = [
    ("nosafety", """    if n + m > OUTCAP {
        return REJ;
    }
""", "    // SAFETY LINE DELETED -- this is c/kernel.c.\n",
     "delete the safety line"),
    ("wrongval", "slice_set_unchecked(row, j, lo);",
     "slice_set_unchecked(row, j, lo ^ 1);", "write `lo ^ 1` instead of `lo`"),
]


def _verus(path, nerr_expected_zero):
    """Run Verus on `path`; return (matched text, verified_ok)."""
    r = subprocess.run([os.path.join(REPO, "verus_run.py"), path,
                        "--multiple-errors", "12"],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    txt = m.group(0) if m else "?? no verification line"
    ok = bool(m) and ((m.group(2) == "0") == nerr_expected_zero)
    return txt, ok, out


def mutsub():
    os.makedirs(SCRATCH, exist_ok=True)
    bad = 0

    # -- 1. the TCB census. This is disqualifier (a), and it is a grep. -----
    vstd = os.path.expanduser("~/tools/verus/vstd")
    hits = subprocess.run(["grep", "-rl", "get_unchecked", vstd],
                          capture_output=True, text=True).stdout.split()
    ok = len(hits) == 0
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} vstd get_unchecked census   "
          f"{len(hits)} file(s)          want 0 -- so an unchecked slice access "
          f"costs a NEW TRUSTED ITEM. p46 would go 5 external_body / 3 "
          f"contracted -> 7 / 5.")

    # -- 2. the specification the retracted claim said did not exist. -------
    spec = open(os.path.join(vstd, "std_specs", "slice.rs")).read()
    want = ("pub assume_specification<T>[ <Range<usize> as SliceIndex<[T]>>"
            "::index_mut ]")
    ok = want in spec and "final(r)@ == final(slice)@.subrange(" in spec
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} std_specs/slice.rs index_mut "
          f"{'PRESENT, value-level' if ok else 'ABSENT':20s} "
          f"want PRESENT -- `vstd/slice.rs`'s ExSliceIndex is the TRAIT "
          f"DECLARATION, not this.")
    print()

    # -- 3. the five probes. ------------------------------------------------
    for name, (body, want_v, why) in PROBES.items():
        p = os.path.join(SCRATCH, name + ".rs")
        open(p, "w").write(HEAD + body + TAIL)
        txt, ok, _ = _verus(p, want_v == "VERIFIES")
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name:22s} {txt:24s} "
              f"want {want_v:9s} -- {why}")
        try:
            os.unlink(p)
        except OSError:
            pass
    print()

    # -- 4. the FULL R5, and 5. its two mutations. --------------------------
    # `verus.rs` carries `#[path = "../../common/driver.rs"]`, which resolves
    # relative to the FILE's directory -- two levels up from the pattern dir is
    # the repo root. So the generated copy has to sit two levels below a
    # directory that has a `common/`, or Verus cannot even parse it.
    gen = os.path.join(SCRATCH, "gen", "pat")
    link = os.path.join(SCRATCH, "common")
    if not os.path.exists(link):
        os.symlink(os.path.join(REPO, "common"), link)
    subprocess.run([sys.executable,
                    os.path.join(HERE, "mkvariants.py"), "--write", gen],
                   capture_output=True, text=True, check=True)
    full = os.path.join(gen, "v46_mutreslice.rs")
    txt, ok, _ = _verus(full, True)
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} v46_mutreslice FULL R5 {txt:24s} "
          f"want 0 errors -- r4_mutreslice's R5, same postcondition as the "
          f"shipped verus.rs, no assume/admit")
    base = open(full).read()
    for tag, old, new, why in R5_MUTATIONS:
        if base.count(old) != 1:
            print(f"  FAIL mutation {tag}: span occurs {base.count(old)} times")
            bad += 1
            continue
        p = os.path.join(gen, f"v46_mutreslice_{tag}.rs")
        open(p, "w").write(base.replace(old, new))
        txt, ok, _ = _verus(p, False)
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} mutation {tag:13s} {txt:24s} "
              f"want ERRORS   -- {why}")

    if bad:
        sys.exit(f"{bad} check(s) disagreed with ../NOTES.md 0c -- either the "
                 f"pin moved or that section is now wrong")
    print("\n../NOTES.md 0c reproduces. A mutable sub-slice at this pin is "
          "USABLE and the full R5\nVERIFIES; `r4_mutreslice` is excluded by the "
          "TRUSTED BASE and by the `identity`\npin, not by the prover. The "
          "identity half is a measurement, not a Verus run --\nsee 0c's "
          "`R5 - R4 = 15n + 1` table.")


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
