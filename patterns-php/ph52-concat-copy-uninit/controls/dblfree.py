#!/usr/bin/env python3
"""ph52 control: THE DOUBLE FREE, AND ITS ESCALATION TO `SIGABRT` AT `n_iters > 1`.

    python3 patterns-php/ph52-concat-copy-uninit/controls/dblfree.py
    python3 .../dblfree.py --selftest

⚠⚠ **WHY THIS FILE EXISTS.** `inputs/gen.py`'s comment on
`adversarial-dblfree.bin` says *"The escalation to SIGABRT is measured in
`controls/dblfree.py` instead, with both n_iters"*, and **`inputs/gen.py` is in the
MEASUREMENT digest** (`.memory-php/04-process.md` law 14). ▶ Writing the named file
costs one re-gate; correcting the pointer would cost a 32-cell re-measure.
`TASK_PHP_045_REPORT.md` §17 records it with the other three.

⭐⭐ **AND IT HAS REAL CONTENT, because the claim it backs is load-bearing for the
row's choice of `n_iters = 1`:** the second `efree` pushes the SAME header into
`cache[1]` twice (`zend_alloc.c:270-279`), so **nothing reaches `free()` during the
call**. The NEXT call's `php_shim_reset()` (`emalloc_shim.h:267-269`) then frees that
header twice and glibc aborts. ▶ **At `n_iters = 1` there is no next call, R1 runs to
completion, and the defect lands in the published u64 instead of in a signal** — which
is the stronger artefact, because a number is what the gate compares across six rungs.

**What it drives:** the shipped `c/kernel.c` and `c/kernel_hardened.c`, on
`inputs/adversarial-dblfree.bin` re-headed at several `n_iters`, over
`{gcc, clang} x {-O0, -O3}`. **The must-fire is the abort at `n_iters >= 2`; the
must-NOT-fire is R1h clean at every `n_iters`, and R1 clean at `n_iters = 1`.**
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
TMP = os.path.join(REPO, ".temp", "php45", "dblfree")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
sys.path.insert(0, os.path.join(REPO, "common-php"))
import slb  # noqa: E402

ITERS = (1, 2, 8, 64)


def blobs():
    os.makedirs(TMP, exist_ok=True)
    f = slb.read(os.path.join(ROW, "inputs", "adversarial-dblfree.bin"))
    out = {}
    for n in ITERS:
        p = os.path.join(TMP, f"dblfree-{n}.bin")
        slb.write(p, n, f.payload[: f.declared_len])
        out[n] = p
    return out


def build(cc, opt, kern):
    os.makedirs(TMP, exist_ok=True)
    ccb = GCC if cc == "gcc" else CLANG
    out = os.path.join(TMP, f"{cc}-{opt}-{kern.replace('.c','')}")
    cmd = [ccb, "-std=c99", "-Wall", "-Wextra", "-" + opt, "-DSLB_ISOLATED",
           "-I", os.path.join(REPO, "common"), "-I", os.path.join(ROW, "c"),
           os.path.join(REPO, "common", "driver.c"),
           os.path.join(ROW, "c", kern),
           os.path.join(ROW, "c", "main.c"), "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return out if r.returncode == 0 else None


def run(bin_, blob):
    r = subprocess.run([bin_, blob], capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout.strip() or
                          re.sub(r"\s+", " ", r.stderr.strip())[:70])


def table():
    bs = blobs()
    rows = {}
    for cc in ("gcc", "clang"):
        for opt in ("O0", "O3"):
            for kern, tag in (("kernel.c", "R1"), ("kernel_hardened.c", "R1h")):
                b = build(cc, opt, kern)
                if b is None:
                    rows[(tag, cc, opt)] = {"BUILD": "FAILED"}
                    continue
                rows[(tag, cc, opt)] = {n: run(b, bs[n]) for n in ITERS}
    return rows


def selftest():
    fails = []
    rows = table()

    def want(name, cond, why):
        if not cond:
            fails.append(f"{name}: {why}")

    r1 = {k: v for k, v in rows.items() if k[0] == "R1"}
    r1h = {k: v for k, v in rows.items() if k[0] == "R1h"}

    # N1 MUST-NOT-FIRE: R1 completes at n_iters = 1, and the defect is in the u64
    bad = [k for k, v in r1.items() if v.get(1, (None,))[0] != 0]
    want("N1 R1 completes at n_iters=1", not bad,
         f"R1 must exit 0 at n_iters=1 -- the defect lands in the number, not a "
         f"signal. Offenders: {bad}")

    # N2 MUST-FIRE: R1 ABORTS at n_iters >= 2, because php_shim_reset() then frees
    #    the doubled cache entry
    for n in (2, 8, 64):
        aborted = [k for k, v in r1.items() if v.get(n, (0,))[0] not in (0, 5)]
        want(f"N2 R1 aborts at n_iters={n}", len(aborted) == len(r1),
             f"R1 must abort at n_iters={n} in all {len(r1)} cells, got "
             f"{len(aborted)}")

    # N3 MUST-NOT-FIRE: R1h is clean at EVERY n_iters -- the fix removes the call
    bad = [(k, n) for k, v in r1h.items() for n in ITERS
           if v.get(n, (None,))[0] != 0]
    want("N3 R1h clean at every n_iters", not bad,
         f"R1h has no `:243` at all and must complete at every n_iters: {bad}")

    # N4 MUST-FIRE: R1 and R1h DISAGREE on the u64 at n_iters = 1
    pairs = 0
    for cc in ("gcc", "clang"):
        for opt in ("O0", "O3"):
            a = rows[("R1", cc, opt)].get(1, (None, None))[1]
            b = rows[("R1h", cc, opt)].get(1, (None, None))[1]
            if a != b:
                pairs += 1
    want("N4 the u64 separates R1 from R1h", pairs == 4,
         f"all 4 (compiler x opt) pairs must disagree at n_iters=1, got {pairs}")

    # N5 MUST-NOT-FIRE: the abort message names the DEFERRED free, not the call's own
    msgs = {v[n][1] for v in r1.values() for n in (2,) if isinstance(v.get(n), tuple)}
    want("N5 glibc names a double free", any("double free" in m for m in msgs),
         f"the abort must be glibc's double-free detector: {msgs}")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    rows = table()
    print("  adversarial-dblfree.bin re-headed at n_iters = " + ", ".join(map(str, ITERS)))
    for k in sorted(rows, key=lambda t: (t[0] != "R1", t[1], t[2])):
        v = rows[k]
        cells = "  ".join(f"n={n}:exit={v[n][0]} {v[n][1][:26]}" for n in ITERS
                          if isinstance(v.get(n), tuple))
        print(f"    {k[0]:4s} {k[1]}-{k[2]:3s}  {cells}")
    if a.selftest:
        fails = selftest()
        print("  --selftest: 8 assertions (4 must-fire, 4 must-NOT-fire)")
        for f in fails:
            print(f"    FAIL {f}")
        print("  --selftest PASS" if not fails else "  --selftest FAILED")
        return 1 if fails else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
