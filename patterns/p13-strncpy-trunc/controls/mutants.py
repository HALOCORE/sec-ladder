#!/usr/bin/env python3
"""p13 control: mutate the proof and check that Verus refuses it.

`.memory/05-layout.md` step 5: *"a pattern whose `spec.md` pins are copied from
p01 without being re-derived is a pattern whose gate certifies p01"*, and item
11: a deliberately broken proof **cannot live in the pattern directory** --
`check.py` requires every `verus!`-bearing `.rs` there to be pinned and to
verify with 0 errors. So the mutants are derived from the shipped `verus.rs` by
**exact-string substitution**, each substitution asserting its own hit count, and
written to `.temp/p13/mutants/`. p17 §1c is the model.

    python3 patterns/p13-strncpy-trunc/controls/mutants.py

Three mutants, and the first is the one p13 exists for:

  M1  DELETE THE TERMINATION STORE from the exec code -- exactly the line
      `c/kernel.c` omits. The consumer loop then has no sentinel and Verus
      cannot discharge `dst_get_unchecked`'s `i < v@.len()`. This is the
      relation an omitted line should have to a proof: not "the postcondition
      is weaker" but "the memory-safety obligation is unprovable".

  M2  WEAKEN THE TRUSTED `requires` on `dst_get_unchecked` by one, from
      `i < v@.len()` to `i <= v@.len()`. p02's M7 is the precedent: a mutant
      that verifies cleanly and is caught only by the `spec.md` pin. Here the
      **verified twin** catches it too, which is what the twin regime is for --
      report both.

  M3  DELETE THE CONTENTS INVARIANT `dst@[DST_CAP - 1] == 0` from the consumer
      loop, leaving the store in place. This separates "the store happened" from
      "the proof carries the fact across the loop boundary" -- the two-site
      obligation's two sites, mutated independently.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
SCRATCH = os.path.join(REPO, ".temp", "p13", "mutants")
VERUS_RUN = os.path.join(REPO, "verus_run.py")
SRC = os.path.join(PDIR, "verus.rs")

MUTANTS = [
    ("m1_no_term_store",
     "the TERMINATION STORE deleted from the exec code -- c/kernel.c's bug, "
     "in the rung that has a proof",
     [("        dst_set_unchecked(&mut dst, DST_CAP - 1, 0);\n", "", 1)],
     None),
    ("m2_weak_dst_requires",
     "the trusted `dst_get_unchecked` precondition weakened by one, "
     "`i < v@.len()` -> `i <= v@.len()`",
     [("""fn dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i < v@.len(),""",
       """fn dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i <= v@.len(),""", 1)],
     None),
    ("m2b_weak_dst_requires_and_twin",
     "the same weakening applied to the trusted item AND to its verified twin, "
     "so the two configurations still agree and only the TWIN can object",
     [("""fn dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i < v@.len(),""",
       """fn dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i <= v@.len(),""", 1),
      ("""fn slb_twin_dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i < v@.len(),""",
       """fn slb_twin_dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i <= v@.len(),""", 1)],
     None),
    ("m3_no_contents_invariant",
     "the CONTENTS invariant `dst@[DST_CAP - 1] == 0` deleted from the "
     "consumer loop, with the store left in place",
     [("                dst@[DST_CAP - 1] == 0u8,\n", "", 1)],
     None),
]


def apply(txt, subs):
    for old, new, want in subs:
        n = txt.count(old)
        if n != want:
            raise SystemExit(f"mutants.py: substitution matched {n} time(s), "
                             f"expected {want}: {old[:70]!r}")
        txt = txt.replace(old, new)
    return txt


def pin_problems(path):
    """Exactly what `check.py` stage 5a does: lift the file's Verus items and
    diff their `external`/`requires`/`ensures` against `spec.md`'s pin.

    Reproduced here rather than described, because a mutant that Verus accepts
    is caught by this and by nothing else -- p02's M7 is the precedent, and
    saying so without running it is the failure mode this project keeps
    finding."""
    import json as _json
    sys.path.insert(0, os.path.join(REPO, "harness"))
    import vparse
    spec = open(os.path.join(PDIR, "spec.md")).read()
    pins = _json.loads(re.search(r"```slb-contract\s*\n(.*?)```", spec,
                                 re.S).group(1))["verus"]["items"]["verus.rs"]
    items = {i.name: i for i in vparse.parse(open(path).read())}
    out = []
    for name, want in pins.items():
        got = items.get(name)
        if got is None:
            out.append(f"item {name} missing from the file")
            continue
        for kw in ("requires", "ensures"):
            g = got.clauses.get(kw, [])
            if list(g) != list(want[kw]):
                out.append(f"{name}.{kw}: file says {list(g)}, spec.md pins "
                           f"{list(want[kw])}")
    return out


def verus(path, extra=()):
    r = subprocess.run([sys.executable, VERUS_RUN, path] + list(extra),
                       capture_output=True, text=True, cwd=REPO, timeout=1800)
    out = (r.stdout + r.stderr)
    m = re.search(r"(\d+) verified, (\d+) errors", out)
    counts = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    errs = [l.strip() for l in out.splitlines()
            if l.startswith("error") or "not satisfied" in l
            or "is not supported" in l or "possible arithmetic" in l]
    return counts, errs[:6], out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    base = open(SRC).read()

    print("=== baseline ===")
    c, e, _ = verus(SRC)
    print(f"  verus.rs (shipped)                 {c[0]} verified, {c[1]} errors")
    c2, _, _ = verus(SRC, ["--cfg", "slb_twin"])
    print(f"  verus.rs --cfg slb_twin            {c2[0]} verified, {c2[1]} errors")
    if c != (17, 0) or c2 != (20, 0):
        print("  !! baseline does not match the pins in spec.md")

    ok = True
    for name, why, subs, _ in MUTANTS:
        path = os.path.join(SCRATCH, f"{name}.rs")
        with open(path, "w") as f:
            f.write(apply(base, subs))
        print(f"\n=== {name} ===\n  {why}")
        c, errs, _ = verus(path)
        print(f"  shipped cfg:  {c[0]} verified, {c[1]} errors")
        for l in errs:
            print(f"    | {l[:150]}")
        ct, errt, _ = verus(path, ["--cfg", "slb_twin"])
        print(f"  --cfg slb_twin: {ct[0]} verified, {ct[1]} errors")
        for l in errt:
            print(f"    | {l[:150]}")
        pin = pin_problems(path)
        for pp in pin:
            print(f"  spec.md pin: {pp}")
        rejected = (c[1] or 0) > 0 or (ct[1] or 0) > 0
        caught = rejected or bool(pin)
        how = ("Verus" if rejected else "") + \
              (" + " if rejected and pin else "") + \
              ("spec.md `verus.items` pin (check.py stage 5a)" if pin else "")
        print(f"  ==> {'CAUGHT by ' + how if caught else 'NOT CAUGHT -- the obligation is not load-bearing and no pin sees it'}")
        ok = ok and caught
    print(f"\nall mutants rejected: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
