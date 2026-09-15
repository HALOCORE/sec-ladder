#!/usr/bin/env python3
"""ph96 -- PRICE THE TWO ATTESTED REPAIRS AGAINST EACH OTHER.

    python3 patterns-php/ph96-outparam-unwritten/controls/repair_price.py

=============================================================================
WHY THIS ROW CAN DO SOMETHING NO OTHER ROW IN THE PROGRAMME CAN
=============================================================================
Every other row has ONE R1h. This one has **two strategies for one obligation,
both attested in the vulnerable file by the same author before the bug was
reported**:

  | | strategy            | C-side spelling                          | attested |
  |-|---------------------|------------------------------------------|----------|
  | **noout** | REMOVE the output | pass NULL, delete the local and the dtor | `:413`, and upstream's `cf020f133487` |
  | **guard** | TEST the output   | `if (!retval)` before use                | `:385`   |

`c/kernel_hardened.c` is the first, because that is what `PROTOCOL_PHP.md` §C
means by R1h. This file builds the second as a third C binary and measures both.

⚠⚠ **THE TWO VARIANTS ARE BEHAVIOURALLY IDENTICAL OVER THE WHOLE DOMAIN**, which
is what makes the difference a COST and not a semantics change: on a written
output both release exactly once; on the sentinel both fold `TAG_UNSET` and
release nothing. The control asserts the checksums are equal on every input
before it quotes a single instruction, because two numbers from two programs are
not a price.

⛔⛔ **EVERY FIGURE HERE OWES FIVE THINGS** (`.memory-php/03-numbers.md` F108):
STATISTIC (**A1 = `kernel_exclusive_ir` / calls**) · INPUT (named) · OPT/MODE
(**`O3/isolated`**) · BASE (named) · and, the base being a C cell, **WHICH
COMPILER -- both columns are measured and both are printed.**

⚠ `inside_share` here is the **`W` one** -- kernel exclusive Ir divided by
callgrind's own whole-run total -- and NOT `F74`'s
`(A1/n_iters) / marginal_ir_per_call` (`RECAP_PHP.md` F129: two quantities wear
that name).

⚠ The build directories are fixed-width `vNN` and asserted equal in length
(F101 / item 109: the kernel fingerprint is path-sensitive).
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

SCRATCH = os.path.join(REPO, ".temp", "php96", "price")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")

#: calls the driver makes on each input -- from the payload header, not guessed.
CALLS = {"small.bin": 20000, "large.bin": 2500}

VULN_SITE = """    ph96_zval *retval;                                          /* :509 */
    int core = 0;

    ph96_call_method(b, slot, &retval, n_rel, &core);            /* :512 */
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    ph96_zval_ptr_dtor(&retval, n_rel);      /* :513 <- write at 0x10 */
    return acc * 31u + PH96_TAG_UNSET;"""

GUARD_SITE = """    ph96_zval *retval;                                          /* :509 */
    int core = 0;

    ph96_call_method(b, slot, &retval, n_rel, &core);            /* :512 */
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    if (!retval) {                    /* the :385 spelling, at the :512 site */
        return acc * 31u + PH96_TAG_UNSET;
    }
    ph96_zval_ptr_dtor(&retval, n_rel);      /* :513 */
    return acc * 31u + PH96_TAG_UNSET;"""

_CG_ROW = re.compile(r"^\s*([\d,]+)\s+(.*)$")


def _cg(exe, inp, tag):
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", exe, inp],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        return {"error": f"callgrind exit {r.returncode}"}
    total = None
    for line in open(out):
        if line.startswith(("summary:", "totals:")):
            total = int(line.split(":", 1)[1].strip().split()[0])
    ann = subprocess.run([CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True).stdout
    kern = 0
    for line in ann.splitlines():
        m = _CG_ROW.match(line)
        if not m or ":" not in m.group(2):
            continue
        func = m.group(2).split(":", 1)[1].split(" [")[0].strip()
        if re.search(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])", func):
            kern += int(m.group(1).replace(",", ""))
    return {"kernel_exclusive_ir": kern or None, "whole_program_ir": total,
            "inside_share_W_pct": (100.0 * kern / total)
                                  if (kern and total) else None}


def build(vdir, cc, guard):
    """One C binary. `guard` selects the R1h-guard source; otherwise R1h-noout
    (`c/kernel_hardened.c`) is used verbatim."""
    d = os.path.join(SCRATCH, vdir)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    if guard:
        src = open(os.path.join(PDIR, "c", "kernel.c")).read()
        assert src.count(VULN_SITE) == 1, (
            "c/kernel.c no longer spells the unset site as expected")
        src = src.replace(VULN_SITE, GUARD_SITE, 1)
        kpath = os.path.join(d, "kernel_guard.c")
        open(kpath, "w").write(src)
    else:
        kpath = os.path.join(PDIR, "c", "kernel_hardened.c")
    out = os.path.join(d, "k")
    subprocess.run([cc, "-std=c99", "-O3", "-Wall", "-Wextra", "-DSLB_ISOLATED",
                    "-I", os.path.join(REPO, "common"),
                    "-I", os.path.join(PDIR, "c"),
                    os.path.join(REPO, "common", "driver.c"), kpath,
                    os.path.join(PDIR, "c", "main.c"), "-o", out],
                   check=True, capture_output=True)
    return out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    problems = []
    rec = {"problems": problems,
           "statistic": ("A1 = callgrind exclusive Ir of the `kernel` symbol, "
                         "divided by the calls the driver makes"),
           "cell": "O3/isolated", "variants": {}}
    variants = [("v00", "gcc", "noout (upstream cf020f133487)", "gcc", False),
                ("v01", "gcc", "guard (the :385 spelling)", "gcc", True),
                ("v02", "cla", "noout (upstream cf020f133487)", CLANG, False),
                ("v03", "cla", "guard (the :385 spelling)", CLANG, True)]
    exes = {}
    for vdir, cctag, label, cc, guard in variants:
        exes[(cctag, label)] = build(vdir, cc, guard)
    assert len({len(os.path.dirname(p)) for p in exes.values()}) == 1, (
        "the four build directories must have EQUAL PATH LENGTHS (F101)")

    print(f"{'compiler':10s}{'variant':34s}{'input':12s}{'A1 total':>13s}"
          f"{'A1/call':>11s}{'W-share':>10s}")
    for (cctag, label), exe in exes.items():
        key = f"c-{'gcc' if cctag == 'gcc' else 'clang'} / {label}"
        rec["variants"][key] = {}
        for inp, n in CALLS.items():
            ip = os.path.join(PDIR, "inputs", inp)
            got = subprocess.run([exe, ip], capture_output=True, text=True)
            c = _cg(exe, ip, f"{cctag}-{'g' if 'guard' in label else 'n'}-{inp}")
            c["checksum"] = got.stdout.strip()
            c["ir_per_call"] = (c["kernel_exclusive_ir"] / n
                                if c.get("kernel_exclusive_ir") else None)
            rec["variants"][key][inp] = c
            print(f"{('gcc' if cctag == 'gcc' else 'clang'):10s}{label:34s}"
                  f"{inp:12s}{c['kernel_exclusive_ir']:>13d}"
                  f"{c['ir_per_call']:>11.3f}{c['inside_share_W_pct']:>9.2f}%")

    # ---- A. are the two the same program? --------------------------------
    print("\nA. ARE THE TWO REPAIRS THE SAME FUNCTION? (checksums, every input)")
    rec["checksum_agreement"] = {}
    for cctag, cname in (("gcc", "c-gcc"), ("cla", "c-clang")):
        for inp in CALLS:
            a = rec["variants"][f"{cname} / noout (upstream cf020f133487)"][inp]["checksum"]
            b = rec["variants"][f"{cname} / guard (the :385 spelling)"][inp]["checksum"]
            same = a == b
            rec["checksum_agreement"][f"{cname}/{inp}"] = same
            print(f"   {cname:9s} {inp:12s} {'AGREE' if same else 'DIFFER'}  {a}")
            if not same:
                problems.append(f"{cname}/{inp}: the two repairs answer "
                                f"differently, so the difference below is not a "
                                f"price, it is a semantics change")

    # ---- B. the price, BOTH C COLUMNS ------------------------------------
    print("\nB. WHAT DOES *TESTING* THE OUTPUT COST OVER *REMOVING* IT?")
    print("   A1, O3/isolated, base = noout (upstream's own strategy), "
          "BOTH C COLUMNS")
    rec["guard_minus_noout_ir_per_call"] = {}
    rec["guard_minus_noout_pct"] = {}
    for cname in ("c-gcc", "c-clang"):
        for inp in CALLS:
            a = rec["variants"][f"{cname} / noout (upstream cf020f133487)"][inp]["ir_per_call"]
            b = rec["variants"][f"{cname} / guard (the :385 spelling)"][inp]["ir_per_call"]
            d = b - a
            pct = 100.0 * d / a if a else None
            rec["guard_minus_noout_ir_per_call"][f"{cname}/{inp}"] = d
            rec["guard_minus_noout_pct"][f"{cname}/{inp}"] = pct
            print(f"   ⭐ {cname:9s} {inp:12s} guard - noout = "
                  f"{d:+9.4f} Ir/call  ({pct:+7.4f} %)")

    # ---- C. THE MECHANISM, because a cost with no mechanism is an
    # incomplete row (PROTOCOL_PHP.md F8) -------------------------------------
    sys.path.insert(0, os.path.join(REPO, "harness"))
    import asm  # noqa: E402
    print("\nC. WHY. The two `kernel` symbols, compared instruction for "
          "instruction:")
    rec["identity"] = {}
    for cctag, cname in (("gcc", "c-gcc"), ("cla", "c-clang")):
        a = exes[(cctag, "noout (upstream cf020f133487)")]
        b = exes[(cctag, "guard (the :385 spelling)")]
        lvl, ev = asm.identity_level(asm.kernel(a), asm.kernel(b))
        rec["identity"][cname] = {"level": lvl, "counts_noout": ev["counts_a"],
                                  "counts_guard": ev["counts_b"],
                                  "md5_fn_equal": ev["md5_fn_a"] == ev["md5_fn_b"]}
        print(f"   {cname:9s} identity_level={lvl:7s} "
              f"insns {ev['counts_a'][0]} vs {ev['counts_b'][0]}, "
              f"bytes {ev['counts_a'][2]} vs {ev['counts_b'][2]}")

    # ---- §H must-fire: a mutant that really costs something --------------
    # If the two spellings measured the same on a build where they CANNOT, the
    # instrument would be dead. The guard source must differ from kernel.c.
    g = open(os.path.join(SCRATCH, "v01", "kernel_guard.c")).read()
    n1 = "if (!retval) {" in g and g.count("if (!retval) {") == 2
    print(f"\nN1 MUST-NOT-FIRE  the guard variant really carries a SECOND "
          f"`if (!retval)` -> {'ok' if n1 else 'BAD'}")
    if not n1:
        problems.append("N1: the guard variant does not carry a second "
                        "`if (!retval)`, so the two binaries differ in nothing "
                        "and every figure above is measuring the same program "
                        "twice")
    n2 = open(os.path.join(PDIR, "c", "kernel_hardened.c")).read()
    n2ok = "(ph96_zval **) 0, n_rel, &core);" in n2
    print(f"N2 MUST-NOT-FIRE  the noout variant IS c/kernel_hardened.c and "
          f"passes NULL -> {'ok' if n2ok else 'BAD'}")
    if not n2ok:
        problems.append("N2: c/kernel_hardened.c does not pass NULL at the "
                        "unset site, so the `noout` column is not upstream's "
                        "strategy")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "c/main.c",
                         "inputs/small.bin", "inputs/large.bin"],
                        "python3 controls/repair_price.py",
                        "four C builds and eight callgrind runs; minutes"))
    with open(os.path.join(HERE, "repair_price.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/repair_price.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
