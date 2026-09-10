#!/usr/bin/env python3
"""ph29 -- WHAT THE `u64` SEES, AND WHERE THE DETECTOR SEES IT.

    python3 patterns-php/ph29-recvfrom-alloc/controls/oracle.py

Two questions, and both are about whether this row has an oracle a reader can
check without a sanitizer.

**Q1 -- the differential.** `../spec.md`'s `divergences` declares one
substitution with real content: `php_stream_xport_recvfrom` becomes
`ph29_stream_read` in `../c/kernel.c`. `PROTOCOL_PHP.md` §A1 clause (c) says a
substitution claimed to be behaviour-preserving needs a DIFFERENTIAL WITH A
MUST-FIRE CONTROL, not a comment. So this drives the **shipped kernel**
(`controls/oracle.c` `#include`s `../c/kernel.c`, so the thing measured is the
thing that ships) against an independent Python re-derivation of
`streamsfuncs.c:300-345` + `transports.c:391`, over a `to_read x ctl x want x
stride` grid the corpus does not span -- and then perturbs the Python side to
show the comparison can fail.

⚠⚠ **WHAT THIS DOES NOT CLAIM.** It cannot compare against real
`php_stream_read`, because there is no PHP here to run. It compares the shipped
C against a reading of the source, which catches a transcription error and not
a misreading. The misreading risk is bounded instead by
`provenance.extra_spans[0]`, which pins `transports.c:381-392` by sha256 so a
reviewer can read the twelve lines themselves -- and the arm that matters is
three lines long: `if (flags == 0 && addr == NULL) return
php_stream_read(stream, buf, buflen);`.

**Q2 -- the detector, and the `navail` sweep.** `model.py::sanitizer_expect`
claims there is NO SILENT BAND on this row: `php_shim_emalloc` calls
`malloc(header + real_size)` and returns `p + header`, so the payload ends
exactly where the malloc region ends and every byte past `real_size` is past
the region. ⭐ That is the OPPOSITE of `ph16`, whose over-write is invisible to
ASan past 32 bytes because it lands in a live neighbouring `fd_set`. This sweep
runs `navail` from 0 upward with and without ASan and prints:

  * ASan's verdict at each `navail`  -- expected: reported at every one
  * glibc's verdict without ASan     -- MEASURED: silent at `navail <= 1`,
    where the write fits in the 8 bytes of unused `mchunk_prev_size` that
    follow a 24-byte region, and `malloc(): corrupted top size` from 4 upward
    IN THIS PROGRAM, where the block is adjacent to the top chunk

⚠⚠ **The second column is a property of THIS BOX's allocator AND of the
surrounding heap, not of PHP, and it is not the same in the row's own driver.**
The shipped `adversarial-trunc.bin` makes all four R1 cells abort with
`malloc(): invalid size (unsorted)` at `navail = 4`. `inputs/gen.py` says so;
this sweep is what measures the boundary rather than assuming one.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php27", "oracle")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
ENV = {k: v for k, v in os.environ.items() if k != "LD_PRELOAD"}

MASK = (1 << 64) - 1
U32 = (1 << 32) - 1
HEAD = 12
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039


def payload(stride):
    """The same deterministic bytes controls/oracle.c writes."""
    return bytes(((0xA5 + 7 * i) & 0xFF) for i in range(stride - HEAD))


def r1(to_read, ctl, want, stride, perturb=0):
    """`streamsfuncs.c:300-345` + `transports.c:391`, re-derived from the
    source rather than lifted from `../model.py` -- which implements the SAFE
    algorithm and would agree with the C only on benign inputs.

    `perturb` is the must-fire control: a non-zero value moves the block size
    by that many bytes, which must make the comparison go red."""
    pay = payload(stride)
    n_pay = stride - HEAD
    navail = want % (n_pay + 1)
    size = (to_read + 1) & MASK
    real_size = (((size + 7) & ~7) & U32) + perturb      # zend_alloc.c:129/:135
    recorded = (size & U32) & 0x7FFFFFFF                 # zend_alloc.h:53
    remote_len = 0
    if ctl & 2:
        recvd = -1
        n = 0
    else:
        n = min(navail, to_read & MASK)                  # transports.c:406-407
        if ctl & 1:
            remote_len = n % 32
        recvd = n
    h = 0
    n_free = 0
    ris = 0
    if recvd >= 0:
        if (ctl & 1) and remote_len:
            ris = 1
        for i in range(recvd):
            h = (h * 31 + pay[i]) & MASK
        n_free = 1
    tally = ((1 * T_ALLOC) ^ (n_free * T_FREE) ^ (0 * T_HIT)
             ^ ((real_size * T_BYTES) & MASK)) & MASK
    acc = 0
    for v in (h, recvd & U32, remote_len, ris, recorded, tally):
        acc = (acc * 31 + v) & MASK
    return acc, real_size, (0 if recvd < 0 else recvd + 1)


def build(tag, asan):
    out = os.path.join(SCRATCH, tag)
    cmd = [GCC, "-std=c99", "-O0", "-g",
           "-I", os.path.join(REPO, "common"),
           "-I", os.path.join(ROW, "c"),
           "-I", os.path.join(REPO, "common-php"),
           "-DSLB_ISOLATED"]
    if asan:
        cmd += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    cmd += ["-o", out, os.path.join(HERE, "oracle.c")]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print(f"  BUILD FAILED {tag}\n{(r.stdout + r.stderr)[:800]}")
        return None
    return out


def run(exe, to_read, ctl, want, stride, timeout=120):
    r = subprocess.run([exe, str(to_read), str(ctl), str(want), str(stride)],
                       capture_output=True, text=True, env=ENV, timeout=timeout)
    out = (r.stdout + r.stderr)
    m = re.search(r"^(\d+)$", r.stdout.strip(), re.M)
    return r.returncode, (int(m.group(1)) if m else None), out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    print(__doc__.split("\n\n")[0])
    print()
    plain = build("oracle-plain", asan=False)
    asan = build("oracle-asan", asan=True)
    if plain is None or asan is None:
        return 2
    bad = 0

    # ---- Q1 --------------------------------------------------------------
    print("== Q1  the shipped kernel vs an independent re-derivation, over a")
    print("       grid inputs/ does not span. BENIGN cells only, because R1")
    print("       aborts or corrupts the heap on the others and the point here")
    print("       is the SUBSTITUTION, not the defect.")
    n_ok = n_run = 0
    for stride in (16, 20, 45, 550, 4076):
        n_pay = stride - HEAD
        for to_read in (1, 2, 7, 8, 63, 64, 87, 88, n_pay - 1, n_pay, n_pay + 1,
                        4095):
            if to_read < 1:
                continue
            for ctl in (0, 1, 2, 3):
                for want in (0, 1, 31, 32, 33, n_pay, n_pay + 1, 65535):
                    # keep it benign: the block must hold navail + 1
                    navail = want % (n_pay + 1)
                    if min(navail, to_read) + 1 > (((to_read + 1) + 7) & ~7):
                        continue
                    rc, got, out = run(plain, to_read, ctl, want, stride)
                    want_u64 = r1(to_read, ctl, want, stride)[0]
                    n_run += 1
                    if rc == 0 and got == want_u64:
                        n_ok += 1
                    else:
                        bad += 1
                        if bad < 4:
                            print(f"   DISAGREE stride={stride} to_read="
                                  f"{to_read} ctl={ctl} want={want}: C={got} "
                                  f"python={want_u64} rc={rc}")
    print(f"   {n_ok} of {n_run} cells agree")
    # the must-fire control: the comparison must be able to fail
    ctl_to_read, ctl_stride = 63, 550
    rc, got, _ = run(plain, ctl_to_read, 0, 40, ctl_stride)
    perturbed = r1(ctl_to_read, 0, 40, ctl_stride, perturb=8)[0]
    fired = (got != perturbed)
    print(f"   must-fire control: an 8-byte perturbation of the python block "
          f"size is detected -> {'PASS' if fired else 'FAIL'}")
    bad += not fired
    print()

    # ---- Q2 --------------------------------------------------------------
    print("== Q2  the navail sweep on the row's own trigger (to_read = "
          "-4294967297, real_size = 0)")
    print("   ASan is expected to report at EVERY navail -- there is no silent")
    print("   band on this row, unlike ph16. glibc is expected to be silent")
    print("   for a small overflow and then to notice.")
    print(f"   {'navail':>8s}  {'wrote':>6s}  {'ASan':<24s}  glibc, no sanitizer")
    stride = 550
    n_pay = stride - HEAD
    seen_silent = seen_loud = False
    for navail in (0, 1, 4, 8, 16, 24, 32, 48, 64, 128, n_pay):
        want = navail
        rc_a, _, out_a = run(asan, -4294967297, 0, want, stride)
        m = re.search(r"ERROR: AddressSanitizer: ([a-z\-]+)", out_a)
        av = m.group(1) if m else ("clean" if rc_a == 0 else f"exit {rc_a}")
        rc_p, got_p, out_p = run(plain, -4294967297, 0, want, stride)
        m2 = re.search(r"(malloc|free|munmap_chunk|corrupted|Aborted)[^\n]*",
                       out_p)
        pv = ("silent, u64 = %d" % got_p) if rc_p == 0 else \
             (m2.group(0)[:44] if m2 else f"exit {rc_p}")
        if rc_p == 0:
            seen_silent = True
        else:
            seen_loud = True
        wrote = min(navail, (-4294967297) & MASK) + 1
        print(f"   {navail:8d}  {wrote:6d}  {av:<24s}  {pv}")
        if av in ("clean",):
            print("      FAIL: ASan did not report an out-of-bounds access")
            bad += 1
    if not (seen_silent and seen_loud):
        print(f"   ⚠ the glibc column did not show BOTH outcomes "
              f"(silent: {seen_silent}, loud: {seen_loud}) -- the claim that "
              f"navail = 4 is chosen to keep the process alive is then "
              f"unsupported on this box")
        bad += 1
    print()
    print("RESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
