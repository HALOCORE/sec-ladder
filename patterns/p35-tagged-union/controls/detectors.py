#!/usr/bin/env python3
"""p35 CONTROLS: **the detector-coverage table, WITH ONE POSITIVE CONTROL PER
DETECTOR.**

    python3 patterns/p35-tagged-union/controls/detectors.py

WHAT THIS MEASURES
------------------
p35's one statement ordering produces TWO harms and they are detected
differently:

    tag PTR over an int payload   the dereference of an attacker-derived
                                  integer -- SIGSEGV, and ASan reports it
    tag DBL over an int payload   a garbage double compared against 1.0 -- a
                                  SILENT WRONG VALUE, reported by nothing

This script builds the SHIPPED `c/kernel.c` and `c/kernel_hardened.c` -- not a
copy -- under five build lines and runs every non-`sweep-` input on each.

⚠⚠ **AND THE SECOND ROW IS A CLAIM ABOUT SILENCE, WHICH IS THE HARDEST KIND TO
SUPPORT.** `.memory/03-measurement.md` entry 14 and RECAP trap 5: a detector
that says nothing looks exactly like a detector that is not running. So this
script does not merely record the silence, it LICENSES it, and it licenses it
**per detector**:

    controls/ctl_asan.c    a wild pointer dereference -- p35's own loud harm in
                           isolation. FIRES under ASan. ⚠ Does NOT fire under
                           UBSan (`-fsanitize=undefined` has no wild-pointer
                           check): it SIGSEGVs at rc=139 with 0 diagnostics.
    controls/ctl_ubsan.c   signed integer overflow. FIRES under UBSan. Silent on
                           the plain build.

**A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** That is the whole
reason there are two files rather than one, and the ASan control's *failure* to
fire under UBSan is recorded here as a measured row rather than hidden -- it is
the evidence for the rule. `.temp/mgr147/NOTES.md` is where `TASK_143`'s
demonstration was found in the unlicensed state.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `ctl_asan` FIRES on the `asan` and `asan_clang` build lines;
  * `ctl_ubsan` FIRES on the `ubsan` build line and is SILENT on `plain`;
  * ⚠ `ctl_asan` does NOT fire on the `ubsan` build line -- recorded as the
    reason the second control exists, and asserted so that a future
    `-fsanitize=undefined` that DID gain a wild-pointer check would show up
    here rather than silently make this file's argument redundant;
  * R1 fires on the PTR-confusion inputs under ASan and is SILENT on the
    DBL-confusion ones under EVERY build line;
  * R1h is silent on EVERY input under EVERY build line, and its stdout equals
    the model's on every input -- which is stage 7h's expectation, re-measured
    here across five build lines instead of the gate's one.

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
OUT = os.path.join(REPO, ".temp", "p35ctl")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

#: name -> (compiler, extra flags). `-O1` throughout so that the sanitizer
#: builds and the plain build differ ONLY in the sanitizer, and
#: `-fstrict-aliasing` is passed explicitly for the reason `check.py`'s stage 7
#: documents (gcc turns it on at -O2 and this is -O1).
BUILDS = {
    "plain": (GCC, []),
    "asan": (GCC, ["-fsanitize=address", "-static-libasan"]),
    "ubsan": (GCC, ["-fsanitize=undefined", "-static-libubsan"]),
    "clang": (CLANG, []),
    "asan_clang": (CLANG, ["-fsanitize=address"]),
}

DIAG = re.compile(r"runtime error|AddressSanitizer|UndefinedBehaviorSanitizer"
                  r"|ERROR:")



def mask(txt):
    """Strip everything from a diagnostic that is not evidence.

    ⚠ A committed file that cites an absolute `.temp/` path costs the manager a
    `harness/tools/temp_citations.py` baseline entry for a file a fresh clone
    will not have, and that tool reads `git ls-files`, so the cost only shows
    up after the commit. ASan pids and pointer values are pure churn for the
    same reason `p23`'s `controls.log` is declared un-hashable
    (`.memory/05-layout.md`). The DIAGNOSTIC TEXT is what this control is
    evidence for; the path, the pid and the address are not."""
    txt = re.sub(re.escape(REPO) + r"/\.temp/\S*", "<scratch>", txt)
    txt = txt.replace(REPO + "/", "")
    txt = re.sub(r"==\d+==", "==<pid>==", txt)
    txt = re.sub(r"0x[0-9a-f]{6,}", "0x<addr>", txt)
    return txt

def sh(cmd, **kw):
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          timeout=600, **kw)


def build_kernel(tag, kernel, cc, flags):
    out = os.path.join(OUT, f"{tag}-{kernel[:-2]}")
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
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


def build_control(tag, src, cc, flags):
    out = os.path.join(OUT, f"{tag}-{src[:-2]}")
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", "-O1", "-g",
            "-fstrict-aliasing"] + flags +
           [os.path.join(HERE, src), "-o", out])
    r = sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: control build failed ({tag}, {src}):\n"
                         f"{(r.stdout + r.stderr)[-2000:]}")
    return out


def run(path, arg=None):
    r = sh([path] + ([arg] if arg else []))
    se = r.stderr
    return {"rc": r.returncode,
            "stdout": r.stdout.strip(),
            "hits": len(DIAG.findall(se)),
            # ⚠ never truncated with `head`: the whole stderr is squashed to one
            # line and the first 240 characters are kept, which is enough to
            # name the diagnostic without carrying ASLR addresses into a
            # committed file.
            "diagnostic": mask(re.sub(r"\s+", " ", se.strip()))[:240]}


def derived_from():
    out = {}
    for rel in ("patterns/p35-tagged-union/c/kernel.c",
                "patterns/p35-tagged-union/c/kernel_hardened.c",
                "patterns/p35-tagged-union/c/kernel.h",
                "patterns/p35-tagged-union/c/main.c",
                "patterns/p35-tagged-union/controls/ctl_asan.c",
                "patterns/p35-tagged-union/controls/ctl_ubsan.c",
                "patterns/p35-tagged-union/controls/detectors.py",
                "patterns/p35-tagged-union/inputs/gen.py",
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
    print("POSITIVE CONTROLS -- one per detector")
    for tag, (cc, flags) in BUILDS.items():
        for src in ("ctl_asan.c", "ctl_ubsan.c"):
            row = run(build_control(tag, src, cc, flags))
            controls[f"{src}/{tag}"] = row
            print(f"  {src:14s} {tag:11s} rc={row['rc']:<5d} "
                  f"hits={row['hits']}  {row['diagnostic'][:70]}")

    def fired(key):
        return controls[key]["hits"] > 0

    if not fired("ctl_asan.c/asan"):
        problems.append("ctl_asan.c did NOT fire under gcc ASan, so nothing "
                        "licenses this pattern's ASan column")
    if not fired("ctl_asan.c/asan_clang"):
        problems.append("ctl_asan.c did NOT fire under clang ASan")
    if not fired("ctl_ubsan.c/ubsan"):
        problems.append("ctl_ubsan.c did NOT fire under UBSan, so nothing "
                        "licenses this pattern's UBSan silence -- which is the "
                        "exact gap .temp/mgr147/NOTES.md found in TASK_143's "
                        "demonstration")
    if fired("ctl_ubsan.c/plain"):
        problems.append("ctl_ubsan.c fired on the PLAIN build, so it is not "
                        "measuring the sanitizer")
    if fired("ctl_asan.c/ubsan"):
        problems.append(
            "ctl_asan.c FIRED under UBSan. That is not a failure of this "
            "pattern -- it would mean `-fsanitize=undefined` has gained a "
            "wild-pointer check since this control was written, which would "
            "make ctl_ubsan.c redundant and would change what the p35 table's "
            "`ubsan` column means. Re-read the table before quoting it.")

    # ---- the two shipped kernels, five build lines, every input -----------
    print("\nSHIPPED KERNELS")
    for tag, (cc, flags) in BUILDS.items():
        for kernel, arm in (("kernel.c", "R1"), ("kernel_hardened.c", "R1h")):
            binp = build_kernel(tag, kernel, cc, flags)
            for n in names:
                row = run(binp, os.path.join(INPUTS, n))
                m = expect[n]
                row["model_stdout"] = str(m.checksum)
                row["model_sanitizer_expect"] = m.sanitizer_expect
                row["agrees_with_model"] = row["stdout"] == str(m.checksum)
                kernels[f"{arm}/{tag}/{n}"] = row
                print(f"  {arm:4s} {tag:11s} {n:32s} rc={row['rc']:<5d} "
                      f"hits={row['hits']} "
                      f"{'==model' if row['agrees_with_model'] else 'DIFFERS'}"
                      f"  {row['diagnostic'][:44]}")

    for n in names:
        for tag in BUILDS:
            r1h = kernels[f"R1h/{tag}/{n}"]
            if r1h["hits"]:
                problems.append(f"R1h/{tag}/{n}: the HARDENED rung produced a "
                                f"diagnostic: {r1h['diagnostic']}")
            if not r1h["agrees_with_model"]:
                problems.append(f"R1h/{tag}/{n}: hardened stdout "
                                f"{r1h['stdout']!r} != model "
                                f"{r1h['model_stdout']!r}")
        m = expect[n]
        if m.sanitizer_expect == "fires":
            for tag in ("asan", "asan_clang"):
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

    doc = {
        "pin": {"regenerate": "python3 patterns/p35-tagged-union/controls/"
                              "detectors.py"},
        "derived_from_sha256": derived_from(),
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "build_lines": {k: [v[0], v[1]] for k, v in BUILDS.items()},
        "controls": controls,
        "kernels": kernels,
        "problems": problems,
        "invariant": "Each positive control fires in the detector whose column "
                     "it licenses and only there: ctl_asan.c fires under ASan "
                     "(gcc and clang) and NOT under UBSan, ctl_ubsan.c fires "
                     "under UBSan and not on the plain build. With both alive, "
                     "R1's silence on the DBL-confusion inputs is REAL silence "
                     "and R1h's silence on every input is a measurement rather "
                     "than an absent detector.",
    }
    out = os.path.join(HERE, "detectors.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
