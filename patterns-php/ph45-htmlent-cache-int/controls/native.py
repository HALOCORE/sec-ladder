#!/usr/bin/env python3
"""ph45 controls that need a compiler: `strchr_equiv.c` and `fatal.c`.

    python3 patterns-php/ph45-htmlent-cache-int/controls/native.py

⚠ Neither `.c` here is on any build path -- `harness/build.py` compiles exactly
three translation units and these are none of them.

  strchr_equiv.c   `strchr(html_entity_chars, c) != NULL` against the RANGE
                   PREDICATE the four Rust rungs spell, over all 256 byte
                   values, with a MUST-FIRE negative. ⭐ The must-fire case is
                   the interesting one: `strchr(s, 0)` returns the TERMINATOR,
                   which is non-NULL, so PHP treats a NUL byte inside an entity
                   body as a LEGAL entity character. A predicate that omits that
                   arm disagrees exactly once -- and no shipped window contains
                   a zero byte, which is exactly how it would have survived.
                   PROTOCOL_PHP.md §A1 clause (c).

  fatal.c          PHP 5.0.0's own allocator with no placed arena, forked.
                   PROTOCOL_PHP.md §A4 fidelity, and the reason the row has an
                   arena at all: the wild free at `:169` is unconditional, so
                   EVERY case faults including the one with no `&` in it.
                   Run under ASan too -- `ASAN_OPTIONS=abort_on_error=1`,
                   because ASan `_exit(1)`s rather than re-raising and the
                   verdict line would otherwise be wrong. ⚠ THE ASan REPORT IS
                   THE EVIDENCE, NOT THE VERDICT LINE.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
TMP = os.path.join(REPO, ".temp", "php45ctl")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
FLAGS = ["-std=c99", "-Wall", "-Wextra", "-O3"]


def build(src, out, extra=(), opt=None):
    os.makedirs(TMP, exist_ok=True)
    flags = [f for f in FLAGS if f != "-O3"] + [opt or "-O3"]
    cmd = ([GCC] + flags + list(extra)
           + ["-I", os.path.join(ROW, "c"), os.path.join(HERE, src),
              "-o", os.path.join(TMP, out)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
    return r.returncode == 0


def run(out, args=(), env=None, reps=1):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run([os.path.join(TMP, out)] + list(args),
                       capture_output=True, text=True, env=e)
    return r.returncode, r.stdout, r.stderr


def main():
    bad = 0

    print("=" * 72)
    print("1. strchr_equiv -- the entity-char predicate over all 256 byte values")
    print("=" * 72)
    if not build("strchr_equiv.c", "strchr_equiv"):
        return 1
    rc, out, err = run("strchr_equiv")
    print(out + err, end="")
    if rc != 0 or "PASS (0 disagreements" not in out:
        bad += 1
    if "expected 1 -> PASS" not in out:
        print("  ⚠ the MUST-FIRE negative did not fire")
        bad += 1

    print()
    print("=" * 72)
    print("2. fatal -- PHP 5.0.0's own allocator, no placed arena")
    print("=" * 72)
    if not build("fatal.c", "fatal"):
        return 1
    rc, out, err = run("fatal", ["15"])
    print(out, end="")
    print("  (first repetition's stage markers)")
    for ln in err.splitlines()[:8]:
        print("   " + ln)
    if "-> 60 of 60 runs faulted" not in out:
        print("  ⚠ EXPECTED 60 of 60")
        bad += 1

    print()
    print("2b. the same under ASan -- the §A4 category, and the corpus's own")
    # ⚠ `-static-libasan` IS NOT COSMETIC on this box: without it every run
    # prints `ASan runtime does not come first in initial library list` and
    # produces no report at all -- which reads exactly like "no fault".
    if not build("fatal.c", "fatal_asan",
                 ["-fsanitize=address", "-static-libasan",
                  "-fno-omit-frame-pointer", "-g"], opt="-O1"):
        return 1
    rc, out, err = run("fatal_asan", ["1"],
                       env={"ASAN_OPTIONS": "abort_on_error=1"})
    print(out.replace("SIGNAL 6", "SIGNAL 6 (ASan abort)"), end="")
    keep, want = [], 0
    lines = err.splitlines()
    for i, ln in enumerate(lines):
        if "ERROR: AddressSanitizer" in ln:
            keep += [ln] + [x for x in lines[i + 1:i + 5]
                            if "memory access" in x or "#0 " in x]
            want += 1
    for ln in keep:
        print("   " + ln.strip())
    if want < 4 or not any("SEGV" in ln for ln in keep):
        print("  ⚠ EXPECTED four ASan SEGV reports")
        bad += 1
    if not any("READ memory access" in ln for ln in keep):
        print("  ⚠ EXPECTED the benign case to be a READ in php_shim_efree")
        bad += 1
    if not any("WRITE memory access" in ln for ln in keep):
        print("  ⚠ EXPECTED the `&`-carrying cases to be a WRITE at :183")
        bad += 1
    print()
    print("   EXPECTED, and it is PROTOCOL_PHP.md A4 matching exactly:")
    print("     `hello, world` -> SEGV, READ, #0 php_shim_efree "
          "(emalloc_shim.h:414),")
    print("                       reached from the dtor -- i.e. :169's free,")
    print("                       on an input with NO `&` in it at all;")
    print("     the other three -> SEGV, WRITE, #0 dec (fatal.c:84), which is")
    print("                       `buffer[0] = '&'` -- mbfilter_htmlent.c:183,")
    print("                       the corpus's own recorded frame for CRASH-123.")

    print()
    print(f"-> {'PASS' if bad == 0 else 'FAIL'} ({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
