#!/usr/bin/env python3
"""ph96 -- is the C rung's fault address the SAME STRUCT OFFSET the PHP 5.0.0
CLI faults at, and is it a property of the BUILD rather than of a run?

    python3 patterns-php/ph96-outparam-unwritten/controls/fault_addr.py

=============================================================================
WHY THIS IS A HARDER TARGET THAN ph97's `(nil)`
=============================================================================
`ph97`'s C rung and the 5.0.0 CLI both fault at address **0**, which any null
dereference of a first field gives. This row's addresses are **struct offsets**:

    0x10  offsetof(zval, refcount)   `_zval_ptr_dtor`  (`zend_execute_API.c:389`)
    0x14  offsetof(zval, type)       `i_zend_is_true`  (`zend_execute.h:72`)

and both follow from `Zend/zend.h:270-293` on LP64, because `zend_object_value`
is `{zend_object_handle handle; zend_object_handlers *handlers;}` and so the
`zvalue_value` union is 16 bytes. ▶ **Matching them means the extraction
reproduced the LAYOUT, not just the mechanism.**

⭐ `c/kernel.c` holds itself to those offsets with three negative-array-size
assertions, so a change in the extraction fails the BUILD rather than moving a
measured address. This file (a) proves those assertions really are load-bearing
by compiling a mutant that violates one, and (b) re-runs both faults.

⚠⚠ TWO CAUTIONS TRAVEL WITH EVERY `si_addr` (§A3a) AND THIS ROW REPEATS THEM IN
`../NOTES.md` section 2: the CLI half was taken on php-in-safe-rust's ORACLE
build and not a museum-default one, and a clean run would not have been evidence
of absence (F3). This file's half is `gcc -O1 -g`, a THIRD build again -- so the
match below is a match of MECHANISM, not of toolchain.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php96", "faddr")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")


def build(d, cc, opt, src, extra_src=None):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    out = os.path.join(d, "k")
    r = subprocess.run([cc, "-std=c99", opt, "-g", "-Wall", "-Wextra",
                        "-DSLB_ISOLATED", "-I", os.path.join(REPO, "common"),
                        "-I", os.path.join(PDIR, "c"),
                        os.path.join(REPO, "common", "driver.c"),
                        extra_src or os.path.join(PDIR, "c", src),
                        os.path.join(PDIR, "c", "main.c"), "-o", out],
                       capture_output=True, text=True)
    return out, r


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    problems = []
    rec = {"problems": problems,
           "offsets_from_zend_h": {"refcount": "0x10", "type": "0x14"},
           "caution": ["the CLI half was taken on php-in-safe-rust's ORACLE "
                       "build, NOT a museum-default 5.0.0",
                       "a clean run would NOT have been evidence of absence "
                       "(RECAP_PHP.md F3); a faulting run IS evidence of "
                       "presence"]}
    shim = os.path.join(SCRATCH, "segaddr.so")
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", shim,
                    os.path.join(REPO, ".tasks-php", "probes", "segaddr.c")],
                   check=True, capture_output=True)

    # ---- A. the shipped assertions are LOAD-BEARING ---------------------
    # A mutant that pads the zval so `refcount` moves off 0x10 must FAIL TO
    # COMPILE. If it builds, the three assertions in c/kernel.c assert nothing.
    src = open(os.path.join(PDIR, "c", "kernel.c")).read()
    mut = src.replace("""typedef struct {
    ph96_zvalue_value value;                             /* zend.h:289 */""",
                      """typedef struct {
    uint64_t slb_pad_mutant;
    ph96_zvalue_value value;                             /* zend.h:289 */""", 1)
    assert mut != src, "the mutant substitution no longer matches c/kernel.c"
    mpath = os.path.join(SCRATCH, "mutant.c")
    open(mpath, "w").write(mut)
    _, r = build(os.path.join(SCRATCH, "m0"), "gcc", "-O1", None,
                 extra_src=mpath)
    rec["mutant_build_rc"] = r.returncode
    rec["mutant_diagnostic"] = re.sub(r"\s+", " ", (r.stderr or ""))[:400]
    fired = r.returncode != 0
    print(f"A. N1 MUST-FIRE  a zval with refcount off 0x10 -> "
          f"{'BUILD REFUSED (ok)' if fired else 'BUILT (BAD)'}")
    if not fired:
        problems.append("the layout mutant COMPILES, so c/kernel.c's three "
                        "offset assertions assert nothing and the fault "
                        "address below is a coincidence rather than a pin")
    else:
        print(f"   {rec['mutant_diagnostic'][:150]}")

    # ---- B. both limbs, both C rungs, two compilers ---------------------
    print("\nB. THE TWO FAULT ADDRESSES, from the row's own inputs")
    limbs = {"unset (:512-513)": "adversarial-unset.bin"}
    # the exists limb has no gate input, by design -- build it here.
    sys.path.insert(0, HERE)
    import second_limb as sl  # noqa: E402
    ex = os.path.join(SCRATCH, "sent-exists.bin")
    sl.make_input(ex, "exists")
    rec["cells"] = {}
    print(f"{'cell':14s}{'limb':20s}{'rc':>5s}  si_addr   want")
    i = 0
    for cc, cname in (("gcc", "c-gcc"), (CLANG, "c-clang")):
        for ksrc, tag in (("kernel.c", "R1"), ("kernel_hardened.c", "R1h")):
            exe, r = build(os.path.join(SCRATCH, f"v{i:02d}"), cc, "-O1", ksrc)
            i += 1
            if r.returncode != 0:
                problems.append(f"{cname}/{tag} failed to build: "
                                f"{r.stderr[:200]}")
                continue
            for limb, want in (("unset (:512-513)", "0x10"),
                               ("exists (:427-429)", "0x14")):
                inp = (os.path.join(PDIR, "inputs", "adversarial-unset.bin")
                       if limb.startswith("unset") else ex)
                p = subprocess.run([exe, inp], capture_output=True, text=True,
                                   env=dict(os.environ, LD_PRELOAD=shim),
                                   timeout=300)
                a = re.search(r"si_addr=(\S+)", p.stderr or "")
                got = a.group(1) if a else None
                rec["cells"][f"{cname}-{tag}/{limb}"] = {
                    "exit": p.returncode, "si_addr": got,
                    "stdout": p.stdout.strip()}
                # R1h repairs the unset limb ONLY, so that is the one cell that
                # is expected NOT to fault.
                expect = None if (tag == "R1h" and limb.startswith("unset")) \
                    else want
                ok = got == expect
                print(f"{cname + '-' + tag:14s}{limb:20s}{p.returncode:>5d}  "
                      f"{str(got):9s} {str(expect):9s} {'ok' if ok else 'BAD'}")
                if not ok:
                    problems.append(
                        f"{cname}-{tag} on the {limb} limb gave si_addr={got}, "
                        f"expected {expect}. An address that is NEITHER 0x10 "
                        f"NOR 0x14 is a DIFFERENT bug and must not be filed "
                        f"under this row.")

    # ---- C. the benign control -------------------------------------------
    exe, _ = build(os.path.join(SCRATCH, "v90"), "gcc", "-O1", "kernel.c")
    p = subprocess.run([exe, os.path.join(PDIR, "inputs", "small.bin")],
                       capture_output=True, text=True,
                       env=dict(os.environ, LD_PRELOAD=shim), timeout=600)
    rec["benign_control"] = {"exit": p.returncode, "stdout": p.stdout.strip()}
    print(f"\nC. N2 MUST-NOT-FIRE  R1 on small.bin -> exit {p.returncode}, "
          f"{p.stdout.strip()!r}")
    if p.returncode != 0:
        problems.append("R1 faults on the MEASURED corpus; a crash with no "
                        "benign control is half a result and this row has no "
                        "benign control left")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel.h", "c/kernel_hardened.c",
                         "inputs/adversarial-unset.bin"],
                        "python3 controls/fault_addr.py",
                        "five C builds and nine runs; under a minute"))
    with open(os.path.join(HERE, "fault_addr.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/fault_addr.json -- {len(problems)} problem(s)")
    for p2 in problems:
        print("  ⛔ " + p2)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
