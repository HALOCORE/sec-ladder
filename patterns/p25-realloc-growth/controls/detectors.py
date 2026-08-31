#!/usr/bin/env python3
"""p25 CONTROLS: **the per-detector table, with one positive control per
detector, and both C arms under both detectors.**

    python3 patterns/p25-realloc-growth/controls/detectors.py

⚠⚠ **A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN** (RECAP trap 5;
`.memory/03-measurement.md` entry 14). `../NOTES.md` 2 publishes a per-detector
column, so this control ships `ctl_asan.c` **and** `ctl_ubsan.c` and requires
each to fire in its own build -- because a UBSan build that says nothing looks
exactly like one that was never linked in, and `.temp/mgr155/NOTES.md` §3 caught
p25's own pre-build demonstration in precisely that state.

⚠⚠ **AND IT RUNS BOTH C ARMS, NOT JUST THE BUGGY ONE.** `TASK_151` added gate
stage `7h` because until then no gate stage had ever run a detector on
`c/kernel_hardened.c`, for any pattern -- `p28d`'s hardened arm SEGVed on a
BENIGN input and nothing saw it. This control keeps that standard locally: R1h
must be **clean on every input, adversarial included**, and it cannot be
declared away.

WHAT IT ASSERTS
---------------
  * `ctl_asan` fires under ASan and is **silent under UBSan** (recorded, and it
    is the whole reason the second control exists);
  * `ctl_ubsan` fires under UBSan and is silent under ASan;
  * R1 (`../c/kernel.c`) under ASan matches `../model.py`'s per-input
    `sanitizer_expect` exactly -- `fires` on the three stale rows, `clean` on the
    other five, **including `adversarial-nogrow`, which is the negative control
    among the adversarial rows**;
  * R1 under UBSan is **silent on every input**, which is a published result and
    is what the UBSan control licenses;
  * R1h (`../c/kernel_hardened.c`) is clean under both detectors on **every**
    input.

⚠ **ASan IS A BIASED INSTRUMENT FOR THIS ROW AND THIS FILE DOES NOT HIDE IT.**
ASan's allocator moves on EVERY `realloc`, so the ASan column would fire even
under a topology in which glibc never relocated. `reloc_probe.py` is the
unbiased half -- it counts which growth actually moves under the shipped driver
-- and `../NOTES.md` 2 reports the plain-build R1-vs-R1h divergence separately.
"""

import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
CDIR = os.path.join(PDIR, "c")
INDIR = os.path.join(PDIR, "inputs")
TMP = os.path.join(REPO, ".temp", "p25ctl")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

sys.path.insert(0, PDIR)
import model as m25  # noqa: E402

SAN = {
    "asan": ["-fsanitize=address", "-fno-omit-frame-pointer"],
    # `-fstrict-aliasing` is passed EXPLICITLY: gcc enables it at -O2 and above
    # and this builds at -O1, so without the token a flag-gated UB class is
    # structurally invisible (harness/check.py's own note, TASK_077).
    "ubsan": ["-fsanitize=undefined", "-fno-sanitize-recover=all",
              "-fstrict-aliasing"],
}


def env_clean():
    e = dict(os.environ)
    e.pop("LD_PRELOAD", None)          # hand-run sanitisers need this
    e["ASAN_OPTIONS"] = "detect_leaks=0"
    return e


def build_kernel(kern, san, tag):
    out = os.path.join(TMP, f"det_{tag}")
    cmd = [GCC, "-std=c99", "-O1", "-I", COMMON, "-I", CDIR] + SAN[san] + [
        "-o", out, os.path.join(CDIR, kern), os.path.join(CDIR, "main.c"),
        os.path.join(COMMON, "driver.c")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: build failed ({tag}):\n{r.stderr}")
    return out


def build_ctl(src, san, tag):
    out = os.path.join(TMP, f"det_{tag}")
    cmd = [GCC, "-std=c99", "-O1"] + SAN[san] + ["-o", out,
                                                 os.path.join(HERE, src)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: build failed ({tag}):\n{r.stderr}")
    return out


def fired(stderr):
    """The two diagnostics, read out of the TEXT and never out of the exit code.
    A control that 'fails' by exiting non-zero is indistinguishable from one that
    failed to build."""
    s = stderr
    return {"asan": "AddressSanitizer" in s,
            "ubsan": "runtime error:" in s}


def run(binary, arg=None):
    cmd = [binary] + ([arg] if arg else [])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                       env=env_clean())
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def derived_from():
    out = {}
    for rel in ("patterns/p25-realloc-growth/c/kernel.c",
                "patterns/p25-realloc-growth/c/kernel_hardened.c",
                "patterns/p25-realloc-growth/c/main.c",
                "patterns/p25-realloc-growth/model.py",
                "patterns/p25-realloc-growth/inputs/gen.py",
                "patterns/p25-realloc-growth/controls/ctl_asan.c",
                "patterns/p25-realloc-growth/controls/ctl_ubsan.c",
                "patterns/p25-realloc-growth/controls/detectors.py",
                "common/driver.c"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    problems, ctl_rows, kern_rows = [], [], []

    print("A. the positive controls -- one per detector")
    for src, owns in (("ctl_asan.c", "asan"), ("ctl_ubsan.c", "ubsan")):
        for san in ("asan", "ubsan"):
            b = build_ctl(src, san, f"{src[:-2]}_{san}")
            rc, so, se = run(b)
            f = fired(se)
            ctl_rows.append({"control": src, "build": san, "exit": rc,
                             "stdout": so, "fired": f,
                             "diagnostic": " ".join(se.split())[:200]})
            print(f"     {src:14s} under {san:6s} exit={rc!s:4s} "
                  f"asan={f['asan']} ubsan={f['ubsan']} out={so!r}")
            if san == owns and not f[owns]:
                problems.append(
                    f"{src} did NOT fire under {san}. It is the POSITIVE "
                    f"CONTROL for that column, so a {san} column in "
                    f"../NOTES.md would be unlicensed -- silence from the "
                    f"kernel would be indistinguishable from a detector that "
                    f"was never linked in")
            if san != owns and f[san]:
                problems.append(
                    f"{src} fired under {san}, which it is not the control "
                    f"for. That makes the two controls interchangeable and "
                    f"defeats the point of shipping two")

    print("B. the two C arms, every input, both detectors")
    inputs = sorted(f for f in os.listdir(INDIR)
                    if f.endswith(".bin") and not f.startswith("sweep-"))
    bins = {(arm, san): build_kernel(kern, san, f"{arm}_{san}")
            for arm, kern in (("R1", "kernel.c"), ("R1h", "kernel_hardened.c"))
            for san in ("asan", "ubsan")}
    for name in inputs:
        mod = m25.build(os.path.join(INDIR, name))
        want = mod.sanitizer_expect
        for arm in ("R1", "R1h"):
            for san in ("asan", "ubsan"):
                rc, so, se = run(bins[(arm, san)], os.path.join(INDIR, name))
                f = fired(se)
                kern_rows.append({"input": name, "arm": arm, "build": san,
                                  "exit": rc, "stdout": so, "fired": f[san],
                                  "model_expect": want,
                                  "model_stdout": str(mod.checksum),
                                  "diagnostic": " ".join(se.split())[:200]})
                print(f"     {name:26s} {arm:4s} {san:6s} exit={rc!s:4s} "
                      f"fired={f[san]!s:6s} model={want:6s} out={so!r}")
                if arm == "R1" and san == "asan":
                    if (want == "fires") != f["asan"]:
                        problems.append(
                            f"{name}: model.py derives sanitizer_expect="
                            f"{want!r} and the ASan build "
                            f"{'fired' if f['asan'] else 'said nothing'}. The "
                            f"derivation and the detector have to agree, or the "
                            f"derived column is not a measurement")
                if arm == "R1" and san == "ubsan" and f["ubsan"]:
                    problems.append(
                        f"{name}: UBSan fired on R1, and ../NOTES.md publishes "
                        f"UBSan SILENCE as a result of this row -- p25's "
                        f"undefined behaviour is supposed to be entirely "
                        f"temporal. Diagnostic: {se[:160]}")
                if arm == "R1h" and f[san]:
                    problems.append(
                        f"{name}: {san} fired on the HARDENED arm. R1h must be "
                        f"clean on EVERY input, adversarial included -- that is "
                        f"gate stage 7h's standard and p28d is why it exists. "
                        f"Diagnostic: {se[:160]}")
                if arm == "R1h" and so != str(mod.checksum):
                    problems.append(
                        f"{name}: R1h under {san} printed {so!r}, model says "
                        f"{mod.checksum}")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "detectors.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "positive_controls": ctl_rows,
           "kernels": kern_rows,
           "problems": problems,
           "invariant": "Each positive control fires in its OWN detector and "
                        "only there; R1's ASan column equals model.py's derived "
                        "sanitizer_expect on every input; R1 is UBSan-silent on "
                        "every input; and R1h is clean under BOTH detectors on "
                        "every input including the adversarial ones (stage 7h's "
                        "standard). ⚠ ASan is a BIASED instrument here -- its "
                        "allocator moves on every realloc -- so this table is "
                        "the conservative half and reloc_probe.py is the "
                        "unbiased one."}
    out = os.path.join(HERE, "detectors.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    for k in list(bins.values()):
        if os.path.exists(k):
            os.unlink(k)
    for src in ("ctl_asan", "ctl_ubsan"):
        for san in ("asan", "ubsan"):
            b = os.path.join(TMP, f"det_{src}_{san}")
            if os.path.exists(b):
                os.unlink(b)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
