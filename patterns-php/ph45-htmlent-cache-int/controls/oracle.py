#!/usr/bin/env python3
"""ph45 control -- THE ORACLE, AND THE ROW AT BOTH PLACEMENTS.

    python3 patterns-php/ph45-htmlent-cache-int/controls/oracle.py

Two things the gate cannot say, because the gate only ever sees `place == 0`:

  A. WHAT THE CATALOGUE'S PROPOSED ORACLE MEASURES, WHICH IS NOTHING.
     `CATALOGUE.md` proposes `u64 = decoded bytes + (allocs, frees)`. On the
     measured placement R1 and R1h are BIT-IDENTICAL -- the truncation is the
     identity below 2^32 -- so that number carries no evidence at all that the
     defect exists. ⭐ This is `ph64`'s lesson repeating on a second row, which
     is now TWICE, and it is why the row's real oracle is an aliasing pair.

  B. THE ROW AT BOTH PLACEMENTS, per the build task's §2.2, with the
     MUST-NOT-FIRE control beside the must-fire one:

       place 0  LO / LO   no alias   -- every rung agrees. THE CONTROL.
       place 2  LO / HI   ALIAS      -- R1 decodes `&amp;` to 65, not 38
       place 1  HI / LO   ALIAS      -- the mirror, same u64
       place 3  HI / HI   SHADOW     -- the decode is CORRECT and only the
                                        allocator is wrong: two wild frees,
                                        two leaks, O3 in isolation

⚠ THE CONTROL IS THE LOAD-BEARING HALF. `place 0` and `place 2` carry
BYTE-FOR-BYTE THE SAME TEXT and the same interleaving, so the divergence cannot
be the interleaving; the only thing that moves is where the second filter's work
buffer lives. Without it the number says nothing about which.

It drives `../model.py`'s memory model, and -- if the six binaries happen to be
in the build root -- the SHIPPED rungs as well, so the third edge of the
triangle is closed too.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, ROW)

import model  # noqa: E402

sys.path.insert(0, os.path.join(ROW, "inputs"))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "ph45gen", os.path.join(ROW, "inputs", "gen.py"))
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

BUILD = os.path.join(REPO, ".temp", "php-root", ".temp", "build", "ph45")
CELLS = [("R1", "c-gcc"), ("R1h", "c-gcc-h"), ("R2", "safe_naive"),
         ("R3", "safe_tuned"), ("R4", "unsafe"), ("R5", "verus")]
PLACES = [(0, "LO / LO   no alias  (the MUST-NOT-FIRE control)"),
          (2, "LO / HI   ALIAS"),
          (1, "HI / LO   ALIAS mirror"),
          (3, "HI / HI   SHADOW")]


def emitted(win, hardened):
    tr = []
    model._simulate(win, len(win), hardened, tr)
    return tr


def main():
    bad = 0
    print("A. the catalogue's oracle on the MEASURED corpus")
    print("   -- expectation: R1 == R1h on every window of small.bin, i.e. the")
    print("      proposed `decoded bytes + (allocs, frees)` measures NOTHING")
    m = model.build(os.path.join(ROW, "inputs", "small.bin"))
    same = 0
    for k in range(m.nwin):
        off = k * m.stride
        if m.r1_result(off) == m._win[k][0]:
            same += 1
    print(f"   small.bin: R1 == R1h on {same} of {m.nwin} windows")
    if same != m.nwin:
        print("   ⚠ EXPECTED all of them")
        bad += 1

    print()
    print("B. the row at BOTH placements, on ONE text")
    print("   text: filter A = `x&amp;y`, filter B = ` &#65; `, interleaved")
    print("   -- expectation: place 0 identical; place 1 and 2 wrong ANSWER and")
    print("      wrong frees; place 3 right answer and wrong frees ONLY")
    rows = []
    for place, label in PLACES:
        win = gen.alias_witness(560, place)
        r1, i1 = model._simulate(win, len(win), False)
        rh, ih = model._simulate(win, len(win), True)
        e1, eh = emitted(win, False), emitted(win, True)
        diff = [i for i, (a, b) in enumerate(zip(e1, eh)) if a != b]
        rows.append((place, label, r1, rh, i1, ih, e1, eh, diff))
        print(f"   place {place}  {label}")
        print(f"      R1  u64 {r1:<22d} alloc/free/dfree/wfree/leak = "
              f"{i1['n_alloc']}/{i1['n_free']}/{i1['n_dfree']}/"
              f"{i1['n_wfree']}/{i1['live']}")
        print(f"      R1h u64 {rh:<22d} alloc/free/dfree/wfree/leak = "
              f"{ih['n_alloc']}/{ih['n_free']}/{ih['n_dfree']}/"
              f"{ih['n_wfree']}/{ih['live']}")
        if diff:
            i = diff[0]
            print(f"      first emitted value that differs: index {i}, "
                  f"R1 = {e1[i]} ({chr(e1[i])!r}), R1h = {eh[i]} "
                  f"({chr(eh[i])!r})  <- `&amp;`")
        else:
            print("      emitted values: IDENTICAL")

    # the expectations, checked
    by = {p: r for p, _, r, *_ in [(a[0], a[1], a[2], a[3]) for a in rows]}
    exp = {0: "same", 2: "alias", 1: "alias", 3: "shadow"}
    for place, label, r1, rh, i1, ih, e1, eh, diff in rows:
        want = exp[place]
        if want == "same":
            ok = (r1 == rh and not diff and i1["n_dfree"] == 0
                  and i1["n_wfree"] == 0 and i1["live"] == 0)
        elif want == "alias":
            ok = (r1 != rh and len(diff) == 1 and e1[diff[0]] == 65
                  and eh[diff[0]] == 38 and i1["n_dfree"] == 1
                  and i1["live"] == 1)
        else:
            ok = (r1 != rh and not diff and i1["n_wfree"] == 2
                  and i1["live"] == 2 and i1["n_free"] == 0)
        if not ok:
            print(f"   ⚠ place {place}: expected `{want}` and the numbers do "
                  f"not match")
            bad += 1
    del by

    print()
    print("C. the SHIPPED binaries, if the build root has them")
    got = 0
    for tag, cell in CELLS:
        for opt in ("O3",):
            b = os.path.join(BUILD, f"{cell}-{opt}-isolated")
            if not os.path.exists(b):
                continue
            got += 1
            outs = []
            for name in ("adversarial-noalias.bin", "adversarial-alias.bin",
                         "adversarial-hi-both.bin"):
                r = subprocess.run([b, os.path.join(ROW, "inputs", name)],
                                   capture_output=True, text=True)
                outs.append(r.stdout.strip())
            print(f"   {tag:4s} noalias={outs[0]:<22s} alias={outs[1]:<22s} "
                  f"hi-both={outs[2]}")
    if got == 0:
        print("   (no binaries in the build root -- run "
              "`harness-php/gate.py --tool build ph45-htmlent-cache-int --all`)")
    else:
        print("   EXPECTED: R1 differs from the other five on `alias` and")
        print("   `hi-both` and agrees with them on `noalias`.")

    print()
    print(f"-> {'PASS' if bad == 0 else 'FAIL'} ({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
