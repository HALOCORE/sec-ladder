#!/usr/bin/env python3
"""p34 CONTROLS: **the detector-coverage table, WITH ONE POSITIVE CONTROL PER
DETECTOR, at BOTH optimisation levels on BOTH compilers.**

    python3 patterns/p34-refcount-stack/controls/detectors.py

WHAT THIS MEASURES
------------------
p34's one omitted statement produces TWO harms and they are separated by which
instrument sees them:

    DUP POP POP / DUP POP READ   the stale entry touches a FREED block whose
                                 bytes are still the right ones, so **the two
                                 rungs' checksums are BIT-IDENTICAL and ASan is
                                 the ONLY discriminator**
    DUP POP NEW READ             the next NEW RECYCLES the block, so the stale
                                 entry reads the new occupant and **the checksum
                                 DIVERGES**

and a third fact that is a published result in its own right: **UBSan is silent
on every input**, because p34's undefined behaviour is entirely TEMPORAL -- every
index the kernel forms is inside `stk[]` in both rungs.

This script builds the SHIPPED `c/kernel.c` and `c/kernel_hardened.c` -- not a
copy -- under **twelve** build lines (plain / ASan / UBSan x gcc / clang x
`-O0` / `-O3`) and runs every non-`sweep-` input on each. ⚠ Twelve rather than
p35's five because `.temp/mgr149/NOTES.md`'s table -- the one this row's headline
came from -- was gcc `-O1` ONLY, and `TASK_154` required the
checksum-agreement result and the recycle divergence to be re-derived at both
levels on both compilers before either is published.

⚠⚠ **THE SILENCE CLAIMS ARE THE HARD ONES.** `.memory/03-measurement.md` entry
14 and RECAP trap 5: a detector that says nothing looks exactly like a detector
that is not running. So this script does not merely record the silence, it
LICENSES it, **per detector**:

    controls/ctl_asan.c    a refcount driven to zero with a live alias -- p34's
                           own harm in isolation. FIRES under ASan. ⚠ Does NOT
                           fire under UBSan (`-fsanitize=undefined` has no
                           use-after-free check): it runs to completion with 0
                           diagnostics.
    controls/ctl_ubsan.c   signed integer overflow. FIRES under UBSan. Silent on
                           the plain build.

**A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** That is the whole
reason there are two files rather than one, and the ASan control's *failure* to
fire under UBSan is recorded here as a measured row rather than hidden -- it is
the evidence for the rule.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `ctl_asan` FIRES on every ASan build line and NOT on any UBSan one;
  * `ctl_ubsan` FIRES on every UBSan build line and is SILENT on every plain one;
  * R1 fires under ASan on exactly the inputs `model.py` derives as `fires`;
  * **R1 is SILENT under UBSan on every input, on both compilers and at both
    optimisation levels** -- the published silence;
  * R1h is silent under EVERY build line on EVERY input, and its stdout equals
    the model's -- stage 7h's expectation, re-measured across twelve build lines
    instead of the gate's one;
  * **on `adversarial-blind` and `adversarial-blindread` R1's PLAIN checksum
    EQUALS R1h's, and on `adversarial-recycle` and `adversarial-many` it DIFFERS
    -- on every plain build line.** That is the row's headline, asserted rather
    than eyeballed.

⚠ Sanitiser runs need `env -u LD_PRELOAD` (`.memory/00-environment.md`): the
container's `LD_PRELOAD` breaks the shared ASan runtime's init ordering. The
gate's own stage 7 sidesteps it with `-static-libasan`; this script does both.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
INPUTS = os.path.join(PDIR, "inputs")
OUT = os.path.join(REPO, ".temp", "p34ctl")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

#: name -> (compiler, opt, extra flags). Both levels and both compilers, because
#: the figures this row publishes were derived at gcc -O1 only and TASK_154
#: required them re-derived. `-fstrict-aliasing` is passed explicitly for the
#: reason check.py's stage 7 documents (gcc turns it on at -O2 and -O0 is below
#: that).
BUILDS = {}
for _cc_tag, _cc in (("gcc", GCC), ("clang", CLANG)):
    for _o in ("O0", "O3"):
        BUILDS[f"plain_{_cc_tag}_{_o}"] = (_cc, _o, [])
        BUILDS[f"asan_{_cc_tag}_{_o}"] = (
            _cc, _o, ["-fsanitize=address"]
            + (["-static-libasan"] if _cc is GCC else []))
        BUILDS[f"ubsan_{_cc_tag}_{_o}"] = (
            _cc, _o, ["-fsanitize=undefined"]
            + (["-static-libubsan"] if _cc is GCC else []))

PLAIN = [k for k in BUILDS if k.startswith("plain_")]
ASAN = [k for k in BUILDS if k.startswith("asan_")]
UBSAN = [k for k in BUILDS if k.startswith("ubsan_")]

DIAG = re.compile(r"runtime error|AddressSanitizer|UndefinedBehaviorSanitizer"
                  r"|ERROR:")

#: The two shapes whose CHECKSUMS AGREE between the rungs, and the two whose
#: checksums DIVERGE. Asserted below on every plain build line.
BLIND = ("adversarial-blind.bin", "adversarial-blindread.bin")
DIVERGE = ("adversarial-recycle.bin", "adversarial-many.bin")


def mask(txt):
    """Strip everything from a diagnostic that is not evidence: scratch paths,
    pids and addresses are churn, and a committed file that cites an absolute
    `.temp/` path costs the manager a `temp_citations.py` baseline entry for a
    file a fresh clone will not have."""
    txt = re.sub(re.escape(REPO) + r"/\.temp/\S*", "<scratch>", txt)
    txt = txt.replace(REPO + "/", "")
    txt = re.sub(r"==\d+==", "==<pid>==", txt)
    txt = re.sub(r"0x[0-9a-f]{6,}", "0x<addr>", txt)
    return txt


def sh(cmd, **kw):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=900, **kw)


def build_kernel(tag, kernel, cc, opt, flags):
    out = os.path.join(OUT, f"{tag}-{kernel[:-2]}")
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", f"-{opt}", "-g",
            "-fstrict-aliasing", "-DSLB_ISOLATED"] + flags +
           ["-I", COMMON, "-I", os.path.join(PDIR, "c"),
            os.path.join(COMMON, "driver.c"),
            os.path.join(PDIR, "c", kernel),
            os.path.join(PDIR, "c", "main.c"), "-o", out])
    r = sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: build failed ({tag}, {kernel}):\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def build_control(tag, src, cc, opt, flags):
    out = os.path.join(OUT, f"{tag}-{src[:-2]}")
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", f"-{opt}", "-g",
            "-fstrict-aliasing"] + flags + [os.path.join(HERE, src), "-o", out])
    r = sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: control build failed ({tag}, {src}):\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def run(path, arg=None):
    r = sh([path] + ([arg] if arg else []))
    return {"rc": r.returncode,
            "stdout": r.stdout.strip(),
            "hits": len(DIAG.findall(r.stderr)),
            # ⚠ never truncated with `head`: the whole stderr is squashed to one
            # line and the first 240 characters are kept, which names the
            # diagnostic without carrying ASLR addresses into a committed file.
            "diagnostic": mask(re.sub(r"\s+", " ", r.stderr.strip()))[:240]}


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/c/kernel.c",
                "patterns/p34-refcount-stack/c/kernel_hardened.c",
                "patterns/p34-refcount-stack/c/kernel.h",
                "patterns/p34-refcount-stack/c/main.c",
                "patterns/p34-refcount-stack/controls/ctl_asan.c",
                "patterns/p34-refcount-stack/controls/ctl_ubsan.c",
                "patterns/p34-refcount-stack/controls/detectors.py",
                "patterns/p34-refcount-stack/inputs/gen.py",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, PDIR)
    import model as M  # noqa: E402

    names = sorted(f for f in os.listdir(INPUTS)
                   if f.endswith(".bin") and not f.startswith("sweep-"))
    expect = {n: M.build(os.path.join(INPUTS, n)) for n in names}

    problems = []
    controls, kernels = {}, {}

    # ---- the two positive controls, one per detector ----------------------
    print("POSITIVE CONTROLS -- one per detector, twelve build lines")
    for tag, (cc, opt, flags) in sorted(BUILDS.items()):
        for src in ("ctl_asan.c", "ctl_ubsan.c"):
            row = run(build_control(tag, src, cc, opt, flags))
            controls[f"{src}/{tag}"] = row
            print(f"  {src:14s} {tag:16s} rc={row['rc']:<5d} "
                  f"hits={row['hits']}  {row['diagnostic'][:56]}")

    def fired(key):
        return controls[key]["hits"] > 0

    for tag in ASAN:
        if not fired(f"ctl_asan.c/{tag}"):
            problems.append(f"ctl_asan.c did NOT fire on {tag}, so nothing "
                            f"licenses this pattern's ASan column there")
        if fired(f"ctl_ubsan.c/{tag}"):
            pass  # ASan does not check signed overflow; silence is expected.
    for tag in UBSAN:
        if not fired(f"ctl_ubsan.c/{tag}"):
            problems.append(
                f"ctl_ubsan.c did NOT fire on {tag}, so nothing licenses this "
                f"pattern's UBSan SILENCE -- which is a published result here, "
                f"not an aside, and it is the exact gap .temp/mgr147/NOTES.md "
                f"found in TASK_143's demonstration")
        if fired(f"ctl_asan.c/{tag}"):
            problems.append(
                f"ctl_asan.c FIRED on {tag}. That is not a failure of this "
                f"pattern -- it would mean `-fsanitize=undefined` has gained a "
                f"use-after-free check since this control was written, which "
                f"would make ctl_ubsan.c redundant and would change what this "
                f"table's `ubsan` column means. Re-read the table before "
                f"quoting it.")
    for tag in PLAIN:
        for src in ("ctl_asan.c", "ctl_ubsan.c"):
            if fired(f"{src}/{tag}"):
                problems.append(f"{src} fired on the PLAIN build {tag}, so it "
                                f"is not measuring the sanitizer")

    # ---- the two shipped kernels, twelve build lines, every input ---------
    print("\nSHIPPED KERNELS")
    for tag, (cc, opt, flags) in sorted(BUILDS.items()):
        for kernel, arm in (("kernel.c", "R1"), ("kernel_hardened.c", "R1h")):
            binp = build_kernel(tag, kernel, cc, opt, flags)
            for n in names:
                row = run(binp, os.path.join(INPUTS, n))
                m = expect[n]
                row["model_stdout"] = str(m.checksum)
                row["model_sanitizer_expect"] = m.sanitizer_expect
                row["agrees_with_model"] = row["stdout"] == str(m.checksum)
                kernels[f"{arm}/{tag}/{n}"] = row
                print(f"  {arm:4s} {tag:16s} {n:28s} rc={row['rc']:<5d} "
                      f"hits={row['hits']} "
                      f"{'==model' if row['agrees_with_model'] else 'DIFFERS'}"
                      f"  {row['diagnostic'][:40]}")

    for n in names:
        m = expect[n]
        for tag in BUILDS:
            r1h = kernels[f"R1h/{tag}/{n}"]
            if r1h["hits"]:
                problems.append(f"R1h/{tag}/{n}: the HARDENED rung produced a "
                                f"diagnostic: {r1h['diagnostic']}")
            if not r1h["agrees_with_model"]:
                problems.append(f"R1h/{tag}/{n}: hardened stdout "
                                f"{r1h['stdout']!r} != model "
                                f"{r1h['model_stdout']!r}")
        if m.sanitizer_expect == "fires":
            for tag in ASAN:
                if not kernels[f"R1/{tag}/{n}"]["hits"]:
                    problems.append(
                        f"R1/{tag}/{n}: model.py derives sanitizer_expect="
                        f"'fires' and ASan reported nothing")
        else:
            for tag in BUILDS:
                if kernels[f"R1/{tag}/{n}"]["hits"]:
                    problems.append(
                        f"R1/{tag}/{n}: a diagnostic on an input model.py "
                        f"derives as clean: "
                        f"{kernels[f'R1/{tag}/{n}']['diagnostic']}")
        # THE PUBLISHED SILENCE: UBSan says nothing about p34, ever.
        for tag in UBSAN:
            if kernels[f"R1/{tag}/{n}"]["hits"]:
                problems.append(
                    f"R1/{tag}/{n}: UBSan produced a diagnostic. p34 publishes "
                    f"UBSan's silence as a RESULT -- its undefined behaviour is "
                    f"purely temporal -- so a hit here retracts that sentence "
                    f"rather than merely surprising the reader: "
                    f"{kernels[f'R1/{tag}/{n}']['diagnostic']}")

    # ---- THE HEADLINE: which shapes the checksum can and cannot see -------
    print("\nCHECKSUM DISCRIMINATION -- plain builds only")
    agree_rows = {}
    for tag in sorted(PLAIN):
        for n in names:
            a = kernels[f"R1/{tag}/{n}"]["stdout"]
            b = kernels[f"R1h/{tag}/{n}"]["stdout"]
            agree_rows[f"{tag}/{n}"] = {"R1": a, "R1h": b, "equal": a == b}
            if n in BLIND or n in DIVERGE:
                print(f"  {tag:16s} {n:28s} R1={a:<22s} R1h={b:<22s} "
                      f"{'IDENTICAL' if a == b else 'DIVERGES'}")
        for n in BLIND:
            if not agree_rows[f"{tag}/{n}"]["equal"]:
                problems.append(
                    f"{tag}/{n}: the two rungs' checksums DIFFER. This row's "
                    f"headline is that on this shape they are BIT-IDENTICAL and "
                    f"ASan is the only discriminator -- if that has stopped "
                    f"being true, the layout note in c/kernel.c is wrong or the "
                    f"allocator changed.")
        for n in DIVERGE:
            if agree_rows[f"{tag}/{n}"]["equal"]:
                problems.append(
                    f"{tag}/{n}: the two rungs' checksums AGREE. This shape is "
                    f"the gateable one precisely because the next NEW recycles "
                    f"the freed block and the answer changes; if it no longer "
                    f"does, the recycle is not happening.")

    doc = {
        "pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                              "detectors.py"},
        "derived_from_sha256": derived_from(),
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "build_lines": {k: [v[0], v[1], v[2]] for k, v in BUILDS.items()},
        "controls": controls,
        "kernels": kernels,
        "checksum_discrimination": agree_rows,
        "problems": problems,
        "invariant": "Each positive control fires in the detector whose column "
                     "it licenses and only there. With both alive: R1 fires "
                     "under ASan on exactly the inputs model.py derives as "
                     "`fires`; R1 is SILENT under UBSan on every input at both "
                     "optimisation levels on both compilers, which is a "
                     "published result and not an aside; R1h is silent "
                     "everywhere; and the two rungs' plain checksums are "
                     "BIT-IDENTICAL on adversarial-blind and "
                     "adversarial-blindread while DIVERGING on "
                     "adversarial-recycle and adversarial-many.",
    }
    out = os.path.join(HERE, "detectors.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
