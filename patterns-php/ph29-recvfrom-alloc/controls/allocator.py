#!/usr/bin/env python3
"""ph29 -- IS THE ALLOCATOR SHIM LOAD-BEARING? Both directions, both run.

    python3 patterns-php/ph29-recvfrom-alloc/controls/allocator.py

⚠⚠⚠ **THIS IS THE CONTROL THE ROW EXISTS FOR.** `PLAN_PHP.md` §4.3:
*"an earlier effort substituted plain `malloc` during extraction and, as a
direct result, reported a real defect as unreachable and then invented an
explanation for the upstream fix."* `RECAP_PHP.md` **F6**: the shim itself
INVENTED a defect once, in the file written to prevent exactly that. Both
claims are about a shim nobody could falsify, because every row so far either
did not allocate or would have faulted under any allocator.

**ph29 faults ONLY under the shim.** So this file asks two questions and runs
both -- `PROTOCOL_PHP.md` §H: *a change to a validator lands with its must-fire
negatives, or it does not land*, and a control with only one arm is the shape
that rule exists to refuse.

    MUST FIRE       the shipped adversarial `to_read` values, WITH the shim,
                    under ASan -> `heap-buffer-overflow WRITE`
    MUST NOT FIRE   the same values, under plain `malloc` -> clean, and for
                    two different reasons the run prints rather than assumes
    MUST NOT FIRE   the benign values, WITH the shim -> clean
    MUST NOT FIRE   the same adversarial values WITH `445daac3ab1a` applied
                    -> refused before the allocation

⚠⚠ **THE SHIM BEHAVIOUR THIS ROW DEPENDS ON IS ONE STORE**, and it is
reproduced verbatim rather than modelled: `Zend/zend_alloc.c:129` declares
`unsigned int real_size` and `:135` assigns `REAL_SIZE(size)` -- a `size_t`
expression -- into it. `emalloc_shim.h:349-352` is those two lines. **If this
row could only be made to fault by a shim behaviour the real `zend_alloc.c`
does not have, the row would have to stop and report it** (`TASK_PHP_027` §6.1).
It does not: the store is cited, the excerpt is pinned in `../spec.md`'s
`provenance.extra_spans[1]` with its sha256, and `--audit` below re-derives the
truncation from the tarball text rather than from the shim.

⚠ **`navail` is 4 by default, and whether the process SURVIVES a 5-byte
overflow depends on the heap, not on the number.** In this probe it does,
because the block has a live chunk after it; in the row's own driver it does
NOT -- all four R1 cells abort with `malloc(): invalid size (unsorted)`,
measured. `--sweep` walks `navail` upward and records where glibc starts
noticing in THIS program; that boundary is a property of this box's allocator
and of the surrounding heap, not of PHP, and it is reported as such rather than
used as a premise. ⚠ This file is where the row's `u64` evidence comes from
precisely because it survives: it prints `bytes_mallocked` beside
`bytes_requested`, which the aborting driver cell cannot.
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php27", "alloc")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
SRC = os.path.join(HERE, "allocator.c")

#: index -> (name, shipped?) -- KEEP IN STEP WITH allocator.c's `cases` table.
CASES = [
    ("benign to_read=63 (cached class)", "benign"),
    ("benign to_read=4095 (malloc/free)", "benign"),
    ("to_read=-4294967297  [adversarial-trunc.bin]", "adv"),
    ("to_read=-1           [adversarial-neg.bin]", "adv"),
    ("to_read=4294967295   [the row's trigger, NOT shipped]", "adv"),
    ("to_read=0            [not a defect; the guard refuses it]", "benign"),
]


def build(tag, shim, guard, asan):
    out = os.path.join(SCRATCH, tag)
    cmd = [GCC, "-std=c99", "-O0", "-g", "-I", os.path.join(REPO, "common-php"),
           f"-DUSE_SHIM={1 if shim else 0}", f"-DGUARD={1 if guard else 0}"]
    if asan:
        cmd += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    cmd += ["-o", out, SRC]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print(f"  BUILD FAILED {tag}\n{(r.stdout + r.stderr)[:600]}")
        return None
    return out


def run(binpath, case, navail=4, timeout=120):
    """(rc, combined output). ⚠ `env -u LD_PRELOAD`: this shell inherits
    `LD_PRELOAD=libstdbuf.so` and gcc's shared ASan runtime then refuses to
    initialise, printing `ASan runtime does not come first` and exiting 1 with
    NO report -- which reads exactly like a clean run
    (`.memory/00-environment.md`)."""
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    r = subprocess.run([binpath, str(case), str(navail)], capture_output=True,
                       text=True, env=env, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)


def outcome(out):
    """OVERFLOW / ALLOC-REFUSED / CLEAN -- three outcomes, not two.

    ⚠⚠ **THE MIDDLE ONE IS WHY THIS FUNCTION IS NOT A BOOLEAN, AND THE
    FIRST DRAFT OF THIS FILE GOT IT WRONG.** Under plain `malloc` with
    `to_read = -4294967297` the request is 18.4 EB, and ASan REFUSES it with
    `requested allocation size ... exceeds maximum supported size` -- an ASan
    diagnostic that is NOT an out-of-bounds access. A control that only asked
    *"did the sanitizer print?"* scored that as the defect firing, which is
    F52's shape exactly: the probe's own setup deciding the answer. Real
    `malloc` returns NULL there (measured below, no-sanitizer arm) and PHP
    `exit(1)`s at `zend_alloc.c:189`, so the row is ABSENT either way -- but for
    a reason worth naming rather than collapsing."""
    if re.search(r"exceeds maximum supported size|"
                 r"failed to allocate", out):
        return "ALLOC-REFUSED"
    if re.search(r"ERROR: (AddressSanitizer|LeakSanitizer)|runtime error:",
                 out):
        return "OVERFLOW"
    return "CLEAN"


def summarise(out):
    m = re.search(r"ERROR: AddressSanitizer: ([a-z\-]+)", out)
    kind = m.group(1) if m else ""
    m2 = re.search(r"(WRITE|READ) of size (\d+)", out)
    m3 = re.search(r"is located (\d+) bytes after (\d+)-byte region", out)
    bits = [b for b in (kind,
                        f"{m2.group(1)} of size {m2.group(2)}" if m2 else "",
                        f"{m3.group(1)}B after a {m3.group(2)}B region"
                        if m3 else "") if b]
    return "  ".join(bits) if bits else "clean"


def audit():
    """Re-derive T1 FROM THE TARBALL TEXT, not from the shim.

    ⚠ The point of this arm is that the whole row rests on ten lines of
    `Zend/zend_alloc.c`, and *"the shim says so"* is not evidence about PHP."""
    tb = os.environ.get("PHP500_TARBALL", os.path.join(
        os.path.dirname(REPO),
        "php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz"))
    if not os.path.exists(tb):
        print(f"  CANNOT EVALUATE: no tarball at {tb} (set PHP500_TARBALL)")
        return 1
    txt = subprocess.run(["tar", "-xzOf", tb, "php-5.0.0/Zend/zend_alloc.c"],
                         capture_output=True, text=True).stdout.splitlines()
    want = {129: "unsigned int real_size;",
            132: "#define REAL_SIZE(size) ((size+7) & ~0x7)",
            135: "real_size = REAL_SIZE(size);"}
    bad = 0
    for ln, frag in sorted(want.items()):
        got = txt[ln - 1].strip() if ln - 1 < len(txt) else "<past EOF>"
        ok = frag.split()[0] in got and got.replace("\t", " ").split("\\")[0]\
            .strip().startswith(frag.split()[0])
        exact = frag in got.replace("\t", " ").replace("  ", " ")
        print(f"  zend_alloc.c:{ln:<4d} {'OK   ' if exact else 'CHECK'} "
              f"{got[:70]!r}")
        if not exact:
            bad += 1
    print("  -> the STORE at :135 into the `unsigned int` at :129 is the "
          "truncation. The macro at :132 only rounds up to 8.")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="walk navail upward and record where glibc aborts")
    ap.add_argument("--audit", action="store_true",
                    help="re-derive T1 from the tarball text and stop")
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)

    print(__doc__.split("\n\n")[0])
    print()
    if a.audit:
        return 1 if audit() else 0

    print("== T1, re-derived from the pristine tarball rather than from the shim")
    if audit():
        print("  RESULT: FAIL -- the cited lines are not what spec.md says")
        return 1
    print()

    bins = {}
    for tag, shim, guard, asan in (
            ("shim-asan", 1, 0, 1), ("malloc-asan", 0, 0, 1),
            ("shim-plain", 1, 0, 0), ("malloc-plain", 0, 0, 0),
            ("shim-guard-asan", 1, 1, 1)):
        b = build(tag, shim, guard, asan)
        if b is None:
            return 2
        bins[tag] = b

    if a.sweep:
        print("== navail sweep, shim, NO sanitizer: where does glibc notice?")
        print("   (a property of THIS box's malloc, not of PHP)")
        for navail in (0, 1, 4, 8, 16, 24, 32, 48, 64):
            rc, out = run(bins["shim-plain"], 2, navail)
            note = "survived" if rc == 0 else f"exit {rc}"
            m = re.search(r"(malloc|free|munmap_chunk|corrupted)[^\n]*", out)
            print(f"   navail={navail:<4d} {note:12s} "
                  f"{(m.group(0)[:60] if m else '')}")
        print()

    bad = 0
    print("== the four arms, ASan, navail=4")
    for i, (name, kind) in enumerate(CASES):
        rc_s, out_s = run(bins["shim-asan"], i)
        rc_m, out_m = run(bins["malloc-asan"], i)
        rc_g, out_g = run(bins["shim-guard-asan"], i)

        # every adversarial value overflows under the shim
        want_s = "OVERFLOW" if kind == "adv" else "CLEAN"
        # ⚠ under plain malloc the three adversarial values do three
        # DIFFERENT things, and that is the whole content of this control:
        #   -4294967297  the request is 18.4 EB -> the allocator refuses it
        #   -1           the request is 0       -> malloc(0) succeeds and is
        #                                          overflowed anyway
        #   4294967295   the request is 4 GiB   -> honoured; the write is in
        #                                          bounds and there is NO defect
        want_m = {2: "ALLOC-REFUSED", 3: "OVERFLOW"}.get(i, "CLEAN")
        # 445daac3ab1a refuses to_read <= 0, so only the positive trigger lives
        want_g = "OVERFLOW" if i == 4 else "CLEAN"

        for label, out, want in (("shim", out_s, want_s),
                                 ("plain malloc", out_m, want_m),
                                 ("shim+445daac", out_g, want_g)):
            got = outcome(out)
            ok = got == want
            bad += not ok
            print(f"  {name:52s} {label:13s} {got:14s} want {want:14s} "
                  f"{'PASS' if ok else 'FAIL'}   {summarise(out)}")
    print()
    print("== what the two allocators actually did, no sanitizer")
    for tag in ("shim-plain", "malloc-plain"):
        for i in (2, 4):
            rc, out = run(bins[tag], i)
            for line in out.splitlines():
                if line.strip() and not line.startswith(("allocator", "guard",
                                                         "navail", "#")):
                    print(f"  [{tag:12s}] {line}")
    print()
    print("RESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
