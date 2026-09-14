#!/usr/bin/env python3
"""ph55 control -- **WHAT THE VERUS LIMITATION COSTS**: `Option<fn>` against
`Option<u8>` + `match`, priced in both statistic families.

    python3 patterns-php/ph55-opdata-stride/controls/fnptr_cost.py
    python3 patterns-php/ph55-opdata-stride/controls/fnptr_cost.py --selftest

`controls/fnptr.rs` shows that **Verus refuses the TYPE** `[Option<fn(..)>; N]`,
which is this row's own dispatch mechanism (`../NOTES.md` §7). `spec.md`'s
`identity` pins R4 == R5, so a representation R5 cannot express is one R4 may not
use either, and all four Rust rungs therefore carry a handler ID and a `match`.

`controls/fnptr_dispatch.rs` is that substitution UNDONE -- a real
`Option<fn(&mut Ex) -> bool>` table, one handler function each, a real indirect
call -- and this file prices it.

⚠⚠ **IT IS A PAIR DIFFERENCE OF TWO THINGS AND NOT ONE, AND THIS FILE SAYS SO
IN ITS OWN OUTPUT.** A function pointer has ONE signature, so every handler must
take the same argument; in C that is `(zend_execute_data *, zend_op *)` and here
it forces the machine state into a `struct Ex` where the rungs keep plain
locals. **Representation + frame**, never a clean one-variable cost.

⭐ **AND IT CHANGES NO ANSWER, WHICH IS ASSERTED BEFORE ANY NUMBER IS QUOTED.**
`Option<fn>` and `Option<u8>` are `None` for exactly the same opcode, so both
spellings turn C's NULL call into the same `unwrap()` panic --
`controls/stride_bug.py` measures that on the adversarial pair. Here the check
is checksum equality on every shipped input: **a variant that has drifted is not
measuring the substitution.**

§H (`PROTOCOL_PHP.md`): `--selftest` drives the verdict function over synthetic
rows -- four must-FIRE and three must-NOT-fire.
"""

import argparse
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(ROOT, ".temp", "php55fn")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
_TOTAL = re.compile(r"^([\d,]+)\s.*PROGRAM TOTALS")

#: `(label, source, why)`. The BASE is the shipped rung whose algorithm the
#: variant restores C's representation into.
PAIR = [("tag_match", os.path.join(PDIR, "safe_naive.rs"),
         "the SHIPPED representation: Option<u8> handler ID + a `match`"),
        ("fn_pointer", os.path.join(HERE, "fnptr_dispatch.rs"),
         "C's representation: Option<fn(&mut Ex) -> bool> + a real indirect call")]
INPUTS = ["small.bin", "large.bin"]

_M = None


def load_measure():
    global _M
    if _M is None:
        spec = importlib.util.spec_from_file_location(
            "slb_measure", os.path.join(ROOT, "harness", "measure.py"))
        _M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_M)
    return _M


def n_iters(inp):
    sys.path.insert(0, os.path.join(ROOT, "common"))
    import slb
    return slb.read(os.path.join(PDIR, "inputs", inp)).n_iters


def build(src, out):
    r = subprocess.run([RUSTC, "--edition", "2021", "-C", "opt-level=3",
                        "--cfg", "slb_isolated", "-A", "warnings", "-o", out, src],
                       capture_output=True, text=True)
    return (out if r.returncode == 0 else None,
            (r.stdout + r.stderr)[-400:] if r.returncode else "")


def checksums(exe):
    out = {}
    for p in sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin"))):
        r = subprocess.run([exe, p], capture_output=True, text=True)
        out[os.path.basename(p)] = (r.returncode, r.stdout.strip())
    return out


def families(exe, inp, tag):
    """`(A1, W1, err)` from one callgrind run. A1 via `measure.py::_sum_rows`,
    IMPORTED; W1 from `callgrind_annotate`'s own PROGRAM TOTALS."""
    M = load_measure()
    o = os.path.join(SCRATCH, f"cg.{tag}")
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + o,
                        exe, os.path.join(PDIR, "inputs", inp)],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0 or not os.path.exists(o):
        return None, None, f"callgrind failed on {tag} (rc {r.returncode})"
    a = subprocess.run([M.CG_ANNOTATE, "--threshold=100", o],
                       capture_output=True, text=True)
    txt = a.stdout + a.stderr
    os.unlink(o)
    k, _ = M._sum_rows(txt, "kernel")
    wp = None
    for ln in txt.splitlines():
        m = _TOTAL.match(ln.strip())
        if m:
            wp = int(m.group(1).replace(",", ""))
            break
    if k is None or wp is None:
        return None, None, f"{tag}: annotate gave kernel={k} totals={wp}"
    n = n_iters(inp)
    return k / n, wp / n, None


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def cost_problems(sums, errs):
    """`sums` is `{label: {input: (rc, stdout)}}`.

    1. both variants must BUILD;
    2. ⛔ the two must agree on EVERY input -- exit code and stdout. A variant
       that has drifted is not measuring the substitution and its Ir difference
       is a difference between two programs;
    3. ⭐ the agreement must include the ADVERSARIAL inputs, because the claim
       this file rests on is that `Option<fn>` and `Option<u8>` are `None` for
       exactly the same opcode. Agreeing on benign inputs only would leave that
       untested, which is the whole point.
    """
    p = list(errs)
    if len(sums) != 2:
        p.append(f"1. only {sorted(sums)} built; both are needed")
        return p
    (la, sa), (lb, sb) = sorted(sums.items())
    for nm in sorted(set(sa) | set(sb)):
        if sa.get(nm) != sb.get(nm):
            arm = "3." if nm.startswith("adversarial") else "2."
            p.append(f"{arm} {la} and {lb} DISAGREE on {nm}: {sa.get(nm)} vs "
                     f"{sb.get(nm)}. The substitution is supposed to change "
                     f"instructions and not behaviour")
    return p


def selftest():
    ok = {"small.bin": (0, "7"), "adversarial-nullcall.bin": (0, "9")}
    bad = []
    cases = [
        ("P1 the shipped shape", {"a": dict(ok), "b": dict(ok)}, [], False, None),
        ("N1 only one built", {"a": dict(ok)}, [], True, "1."),
        ("N2 a benign answer differs",
         {"a": dict(ok), "b": {**ok, "small.bin": (0, "8")}}, [], True, "2."),
        ("N3 an ADVERSARIAL answer differs",
         {"a": dict(ok), "b": {**ok, "adversarial-nullcall.bin": (101, "")}},
         [], True, "3."),
        ("N4 a build error is carried through",
         {"a": dict(ok), "b": dict(ok)}, ["1. b: build failed"], True, "1."),
        ("P2 both differ from the shipped values but agree with each other",
         {"a": {"small.bin": (0, "99")}, "b": {"small.bin": (0, "99")}},
         [], False, None),
        ("P3 an extra input both carry",
         {"a": {**ok, "large.bin": (0, "5")}, "b": {**ok, "large.bin": (0, "5")}},
         [], False, None),
    ]
    for label, sums, errs, must_fire, arm in cases:
        got = cost_problems(sums, errs)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC ROWS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"7 arms (4 must-FIRE, 3 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    print("\n1. BUILD, THEN AGREE ON EVERY INPUT BEFORE ANY NUMBER IS QUOTED")
    bins, sums, errs = {}, {}, []
    for label, src, why in PAIR:
        exe, e = build(src, os.path.join(SCRATCH, label))
        if e:
            errs.append(f"1. {label}: build failed -- {e}")
            print(f"   {label:12s} BUILD FAILED")
            continue
        bins[label] = exe
        sums[label] = checksums(exe)
        print(f"   {label:12s} ok   {why}")
    cp = cost_problems(sums, errs)
    print(f"   -> checksums over {len(next(iter(sums.values()), {}))} input(s): "
          + ("IDENTICAL -- the substitution changes no behaviour"
             if not cp else "*** DISAGREE, see problems"))
    problems.extend(cp)
    if cp:
        for p in problems:
            print(f"  *** {p}", file=sys.stderr)
        return 1

    print("\n2. THE PRICE -- A1 and W1, O3/isolated, `fn_pointer` against "
          "`tag_match`")
    rows = {}
    for inp in INPUTS:
        for label in bins:
            a, w, e = families(bins[label], inp, f"{label}.{inp}")
            if e:
                problems.append(e)
            rows[f"{label}/{inp}"] = {"A1": a, "W1": w}
    for inp in INPUTS:
        t = rows.get(f"tag_match/{inp}")
        f = rows.get(f"fn_pointer/{inp}")
        if not (t and f and t["A1"] and f["A1"]):
            continue
        da = (f["A1"] - t["A1"]) / t["A1"] * 100
        dw = (f["W1"] - t["W1"]) / t["W1"] * 100
        print(f"   {inp:11s} A1 {t['A1']:9.3f} -> {f['A1']:9.3f} = {da:+7.2f} %"
              f"   W1 {t['W1']:9.3f} -> {f['W1']:9.3f} = {dw:+7.2f} %")
    print("\n   ⚠ REPRESENTATION + FRAME, never a clean one-variable cost: a "
          "function\n   pointer has ONE signature, so every handler must take "
          "the same argument,\n   which forces the machine state into a `struct "
          "Ex` where the rungs keep\n   plain locals. ../NOTES.md §12.")
    print("\n   ⚠⚠ THESE ARE THIS FILE'S OWN BUILD (`rustc -C opt-level=3 "
          "--cfg slb_isolated`),\n   NOT `harness/build.py`'s, so the LEVELS "
          "are not comparable with ../NOTES.md\n   §8's table -- only the two "
          "columns here are comparable with each other,\n   and they are built "
          "with identical flags.")
    print("\n   ⭐⭐ AND THE TWO FAMILIES DISAGREE IN SIGN, FOR THE ROW'S OWN "
          "REASON.\n   A1 makes the function-pointer table look CHEAPER and W1 "
          "makes it DEARER,\n   because a function pointer is exactly what "
          "stops a handler being inlined:\n   the work leaves the `kernel` "
          "symbol without leaving the program. That is\n   ../NOTES.md §8b's "
          "blindness, arising a second time and from the mechanism\n   this row "
          "is about.")

    out = {"rows": rows, "checksums": sums, "problems": problems}
    dst = os.path.join(HERE, "fnptr_cost.json")
    out.update(_pin.pin(
        ['safe_naive.rs', 'inputs/gen.py', 'controls/fnptr_dispatch.rs', 'controls/fnptr_cost.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/fnptr_cost.py',
        'the two sides of the pair and the corpus. NOT the other rungs: this file compares safe_naive.rs against controls/fnptr_dispatch.rs and nothing else.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
