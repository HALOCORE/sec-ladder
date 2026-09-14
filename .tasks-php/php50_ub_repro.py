#!/usr/bin/env python3
"""TASK_PHP_050 §2 -- ⭐ **REPRODUCE F109's MOST QUOTABLE SENTENCE:
*"unsafe Rust with the bug is STRICTLY WORSE THAN C"* on
`adversarial-nullcall.bin`.**

    python3 .tasks-php/php50_ub_repro.py --selftest
    python3 .tasks-php/php50_ub_repro.py

**THE CLAIM** (`TASK_PHP_048_REPORT.md` §2, `patterns-php/ph55-opdata-stride/
NOTES.md`): C carrying the `4f68f3774c34` bug dies of **SIGNAL 11**, every safe
Rust port carrying the same bug **PANICS**, and `unsafe.rs` carrying it
**does not crash at all** -- `unwrap_unchecked` on a `None` is UB, LLVM takes
it, and the program exits 0 printing `11370550710093900800`, a **third** value
agreeing with neither C nor R1h.

⚠⚠⚠ **WHY IT NEEDS REPRODUCING RATHER THAN RE-READING.** The claim rests on a
value produced by *taking undefined behaviour*. `controls/stride_bug.json`
records it, but that file IS the single observed run -- re-reading it is not a
second observation. **A UB value has no guarantee of stability across a
recompile**, and *"a third wrong value"* is a stronger sentence than *"it did
not crash"*, so the two halves are scored SEPARATELY here:

    HALF 1  does `unsafe-bug` FAIL TO CRASH on the NULL case?   (the load-bearing half)
    HALF 2  is the value it prints the SAME `11370550710093900800`?

⛔ **SCOPE.** This rebuilds the row's MUTANTS, which are controls and not rungs;
it is not a re-measure and not a re-gate, it touches no rung binary, and it
writes **only** under `.temp/php50/`. ⭐ It reuses
`controls/stride_bug.py`'s OWN `FIX_SUBS`, `materialise`, `build_c`, `build_rs`
and `run` by importing the module and never calling its `main()` -- so the
mutation and the compiler flags are the row's, not mine, and a drift in either
shows up as an import-time failure rather than as a quiet difference.
⚠ `materialise()` writes under `.temp/php55-stride/` (its own SCRATCH, already
gitignored); nothing under `patterns-php/` is written, and in particular
`controls/stride_bug.json` is NOT touched.

§H: `verdict()` is a pure function of a results dict; `--selftest` drives it
over six synthetic cases, four must-FIRE and two must-NOT.
"""

import argparse
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTRL = os.path.join(ROOT, "patterns-php", "ph55-opdata-stride", "controls",
                    "stride_bug.py")
OUT = os.path.join(ROOT, ".temp", "php50", "ub_repro")

#: What `TASK_PHP_048_REPORT.md` §2 and `controls/stride_bug.json` record.
PUBLISHED = {
    "c-R1": {"class": "SIGNAL-11", "stdout": ""},
    "safe_naive-bug": {"class": "PANIC", "stdout": ""},
    "safe_tuned-bug": {"class": "PANIC", "stdout": ""},
    "unsafe-bug": {"class": "ANSWERED", "stdout": "11370550710093900800"},
}
INPUT = "adversarial-nullcall.bin"


def load_control():
    spec = importlib.util.spec_from_file_location("ph55_stride_bug", CTRL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for name in ("FIX_SUBS", "materialise", "build_c", "build_rs", "run",
                 "classify"):
        if not hasattr(m, name):
            raise AssertionError(
                f"controls/stride_bug.py no longer exports `{name}` -- this "
                f"reproduction drives the row's own recipe and cannot silently "
                f"fall back to a recipe of its own")
    return m


# ---------------------------------------------------------------------------
# the verdict arm -- a pure function, so it can be attacked
# ---------------------------------------------------------------------------

def verdict(got, published=PUBLISHED):
    """`(problems, half1, half2)`.

    HALF 1 -- *unsafe Rust does not crash where C does* -- is UPHELD when
    `c-R1` still takes a signal, every safe mutant still PANICs, and
    `unsafe-bug` exits 0. **That is the comparative sentence and it does not
    depend on the value.**

    HALF 2 -- *and prints that particular third value* -- is UPHELD only when
    the stdout matches to the digit. ⭐ **They are reported separately because
    HALF 2 can fail on a recompile without touching HALF 1**, and collapsing
    them would either over-claim (quote a UB value as stable) or under-claim
    (withdraw a sound comparative result because a UB digit moved).
    """
    p = []
    for cell, want in sorted(published.items()):
        if cell not in got:
            p.append(f"1. {cell}: not measured")
            continue
        if got[cell]["class"] != want["class"]:
            p.append(f"1. {cell}: published {want['class']}, measured "
                     f"{got[cell]['class']}")
    half1 = (got.get("c-R1", {}).get("class", "").startswith("SIGNAL")
             and all(got.get(c, {}).get("class") == "PANIC"
                     for c in ("safe_naive-bug", "safe_tuned-bug"))
             and got.get("unsafe-bug", {}).get("class") == "ANSWERED")
    uv = got.get("unsafe-bug", {}).get("stdout")
    half2 = uv == published["unsafe-bug"]["stdout"]
    if not half2 and got.get("unsafe-bug", {}).get("class") == "ANSWERED":
        p.append(f"2. unsafe-bug answered {uv!r}, published "
                 f"{published['unsafe-bug']['stdout']!r} -- the UB VALUE moved "
                 f"across a recompile. HALF 1 may still stand; HALF 2 does not, "
                 f"and the published digits must not be quoted as reproducible.")
    # a UB value that equals C's would make the sentence FALSE, not merely
    # unreproducible -- worth its own arm.
    if uv and uv == "17484701542569762048":
        p.append("3. unsafe-bug now agrees with C's wrong answer, so `a THIRD "
                 "wrong value` is refuted outright")
    return p, half1, half2


def selftest():
    bad = []
    ok = {c: dict(v) for c, v in PUBLISHED.items()}
    cases = [
        ("P1 the published shape", ok, False, True, True),
        ("N1 unsafe-bug crashes after all",
         {**ok, "unsafe-bug": {"class": "SIGNAL-11", "stdout": ""}},
         True, False, False),
        # ⭐⭐ N2 IS THE ARM THIS FILE EXISTS FOR: the comparative sentence
        # survives and the DIGITS do not.
        ("N2 the UB value moved but nothing else did",
         {**ok, "unsafe-bug": {"class": "ANSWERED", "stdout": "42"}},
         True, True, False),
        ("N3 unsafe-bug now agrees with C",
         {**ok, "unsafe-bug": {"class": "ANSWERED",
                               "stdout": "17484701542569762048"}},
         True, True, False),
        ("N4 a safe mutant stopped panicking",
         {**ok, "safe_naive-bug": {"class": "ANSWERED", "stdout": "7"}},
         True, False, True),
        ("P2 C takes a different signal but still a signal",
         {**ok, "c-R1": {"class": "SIGNAL-6", "stdout": ""}},
         True, True, True),
    ]
    for label, got, must_fire, w1, w2 in cases:
        p, h1, h2 = verdict(got)
        if bool(p) != must_fire:
            bad.append(f"{label}: fired={bool(p)} want={must_fire} ({p})")
        if h1 != w1:
            bad.append(f"{label}: half1={h1} want={w1}")
        if h2 != w2:
            bad.append(f"{label}: half2={h2} want={w2}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    bad = selftest()
    print(f"0. §H selftest {'PASS' if not bad else 'FAIL'}  "
          f"(6 arms: 4 must-FIRE, 2 must-NOT-fire)")
    for b in bad:
        print(f"   *** {b}")
    if args.selftest:
        return 1 if bad else 0
    if bad:
        print("refusing to measure with a broken verdict arm", file=sys.stderr)
        return 1

    m = load_control()
    os.makedirs(OUT, exist_ok=True)
    inp = os.path.join(ROOT, "patterns-php", "ph55-opdata-stride", "inputs",
                       INPUT)
    got, notes = {}, []
    exe, err = m.build_c("kernel.c", os.path.join(OUT, "c-R1"))
    if not exe:
        notes.append(f"c-R1 did not build: {err}")
    else:
        got["c-R1"] = m.run(exe, inp)
    for rel, name in (("safe_naive.rs", "safe_naive-bug"),
                      ("safe_tuned.rs", "safe_tuned-bug"),
                      ("unsafe.rs", "unsafe-bug")):
        src = m.materialise(rel, name)
        exe, err = m.build_rs(src, os.path.join(OUT, name))
        if not exe:
            notes.append(f"{name} did not build: {err}")
            continue
        got[name] = m.run(exe, inp)
    for c in sorted(got):
        got[c]["class"] = m.classify(got[c])
    print(f"\n1. INDEPENDENT REBUILD + RUN on {INPUT}")
    for c in sorted(got):
        print(f"   {c:18s} class={got[c]['class']:12s} exit={got[c]['exit']:>4} "
              f"stdout={got[c]['stdout']!r}")
    p, h1, h2 = verdict(got)
    print(f"\n2. VERDICT")
    print(f"   HALF 1  'unsafe Rust does not crash where C does' : "
          f"{'UPHELD' if h1 else 'NOT UPHELD'}")
    print(f"   HALF 2  'and prints 11370550710093900800'         : "
          f"{'UPHELD' if h2 else 'NOT UPHELD'}")
    for x in p + notes:
        print(f"   *** {x}")
    json.dump({"input": INPUT, "got": got, "problems": p, "notes": notes,
               "half1_no_crash": h1, "half2_same_value": h2},
              open(os.path.join(ROOT, ".temp", "php50", "ub_repro.json"), "w"),
              indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
