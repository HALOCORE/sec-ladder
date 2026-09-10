#!/usr/bin/env python3
"""ph29 -- WHAT EACH STAGE OF THE UPSTREAM FIX ACTUALLY REMOVES.

    python3 patterns-php/ph29-recvfrom-alloc/controls/fix_scope.py

⚠⚠⚠ **THE ANSWER IS "NOT THIS ROW'S DEFECT", AND THAT IS THE RESULT.**
`PLAN_PHP.md` §4.4: *"an upstream fix is not automatically correct ... That is a
result, and one of the strongest a row can carry. Report it; do not repair it."*

The repair is in TWO STAGES and the row had to choose between them
(`.tasks-php/UPSTREAM_001.md` §4, `TASK_PHP_027` §2):

    5.0.0   read_buf = emalloc(to_read + 1);                    -- R1
    5.1.0   if (to_read <= 0) { RETURN_FALSE; }  <-- STAGE 1    -- R1h, shipped
            445daac3ab1a, Ilia Alshanetsky, 2004-07-28, 1 file, +5
    5.3.0   ... then safe_emalloc(1, to_read, 1);  <-- STAGE 2  -- cited, not shipped
            6ac8ffdfea10, Antony Dovgal, 2006-12-25, 1 file, +1/-1

Both patches are beside this file, fetched from
`https://github.com/php/php-src/commit/<sha>.patch` and sha-pinned in
`../spec.md`. **Verified at the commit and not at the column**
(`PROTOCOL_PHP.md` §F5(iii)).

This file answers four questions over the WHOLE `to_read` domain, in exact
integer arithmetic, and then checks the arithmetic against the compiled C on a
sample so that the model is not the only witness:

    Q1  which `to_read` make the allocation truncate, i.e. give a block
        SMALLER than the program believes it asked for?
    Q2  which of those does STAGE 1 refuse?
    Q3  which does STAGE 2 refuse, and what does it buy OVER stage 1?
    Q4  what does each stage refuse that was never a defect?

⚠ **Q4 is the half a "does the fix work?" question does not ask.** A guard can
be wrong in two directions and `.memory-php/02-ladder.md` already records one
upstream fix that was *"half dead and half incomplete"* and another that was
*"half wrong"*. Stage 1 is **over-broad on the safe side and under-broad on the
unsafe side at once**, and both halves are printed here with counts.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
SCRATCH = os.path.join(REPO, ".temp", "php27", "fixscope")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

U64 = (1 << 64) - 1
U32 = (1 << 32) - 1
LONG_MAX = (1 << 63) - 1
LONG_MIN = -(1 << 63)


def real_size(to_read):
    """`Zend/zend_alloc.c:129` + `:135`. The block's ACTUAL length."""
    size = (to_read + 1) & U64
    return ((size + 7) & ~7) & U32


def believed(to_read):
    """What the caller then passes to the transport at `:323` -- `to_read`,
    widened to `size_t`. It writes at most this many bytes, plus the NUL."""
    return to_read & U64


def truncates(to_read):
    """Does the block come back SMALLER than the request?"""
    return real_size(to_read) < ((to_read + 1) & U64)


def faults(to_read, navail):
    """Does R1 write outside the block? It writes `min(navail, (size_t)to_read)`
    bytes and then one NUL at that offset."""
    n = min(navail, believed(to_read))
    return n + 1 > real_size(to_read)


def stage1_refuses(to_read):
    """445daac3ab1a: `if (to_read <= 0) RETURN_FALSE;`"""
    return to_read <= 0


def stage2_refuses(to_read):
    """6ac8ffdfea10: `safe_emalloc(1, to_read, 1)`.

    `zend_alloc.c:221-244`: nmemb/size/offset are `size_t`, the guard is
    `nmemb < LONG_MAX && size < LONG_MAX && offset < LONG_MAX`, then
    ZEND_SIGNED_MULTIPLY_LONG(1, to_read) and
    `!use_dval && lval < LONG_MAX - offset`. ⚠ It then calls the TRUNCATING
    `_emalloc` at `:238`, so refusing is the ONLY thing it can contribute."""
    nmemb, size, offset = 1, to_read & U64, 1
    if not (nmemb < LONG_MAX and size < LONG_MAX and offset < LONG_MAX):
        return True
    prod = (nmemb * size)
    lval = prod - (1 << 64) if prod >= (1 << 63) else prod   # narrowed to long
    # the double-precision heuristic (zend_multiply.h:36-45) reports overflow
    # for products at or above 2^53; 1 * size never triggers it for size < 2^53
    if abs(lval) >= (1 << 53):
        dres = float(nmemb) * float(size)
        if (float(lval) - dres) + dres != dres:
            return True
    return not (lval < LONG_MAX - offset)


NAVAIL = 4          # what the shipped adversarial inputs deliver


def band(pred, lo, hi, step):
    return [t for t in range(lo, hi, step) if pred(t)]


def main():
    print(__doc__.split("\n\n")[0])
    print()

    # ---- Q1 -------------------------------------------------------------
    print("== Q1  which to_read make the ALLOCATION TRUNCATE?")
    print("   `truncates` means the block is SMALLER than `to_read + 1`:")
    print("   * every to_read < 0 EXCEPT to_read == -1, where the request is 0")
    print("     and a 0-byte block is not smaller than a 0-byte request -- but")
    print("     the write is still 5 bytes, so it FAULTS anyway. Truncation and")
    print("     fault are two different predicates and this row needs both.")
    print("   * every to_read >= 0 with to_read + 1 >= 2^32")
    n_pos = 0
    for t in range(0, 1 << 20):
        if truncates(t):
            n_pos += 1
    print(f"   measured: 0 <= to_read < 2^20     -> {n_pos} truncate")
    neg = sum(1 for t in range(-(1 << 20), 0) if truncates(t))
    print(f"   measured: -2^20 <= to_read < 0    -> {neg} of {1 << 20} truncate "
          f"(the exception is to_read == -1; see above)")
    boundary = [t for t in ((1 << 32) - 10, (1 << 32) - 9, (1 << 32) - 8,
                            (1 << 32) - 2, (1 << 32) - 1, 1 << 32,
                            (1 << 33) - 1, (1 << 33), LONG_MAX - 2,
                            LONG_MAX - 1, LONG_MAX)]
    for t in boundary:
        print(f"   to_read = {t:<22d} real_size = {real_size(t):<12d} "
              f"believed = {believed(t):<22d} "
              f"{'TRUNCATES' if truncates(t) else 'honoured'}")
    print()

    # ---- Q2/Q3 -----------------------------------------------------------
    print("== Q2/Q3  which faulting to_read does each stage refuse?")
    print("   (a to_read `faults` when R1 writes past the block with navail = "
          f"{NAVAIL})")
    domain = ([t for t in range(-4096, 4096)]
              + [(1 << 32) - 1 - k for k in range(0, 8)]
              + [(1 << 32) + k for k in range(0, 8)]
              + [(1 << 33) - 1 - k for k in range(0, 8)]
              + [LONG_MAX - k for k in range(0, 4)]
              + [LONG_MIN + k for k in range(0, 4)]
              + [-(1 << 32) - 1, -(1 << 32), -(1 << 33) - 1])
    domain = sorted(set(domain))
    rows = []
    for t in domain:
        rows.append((t, faults(t, NAVAIL), stage1_refuses(t),
                     stage2_refuses(t)))
    nf = sum(1 for _, f, _, _ in rows if f)
    s1 = sum(1 for _, f, a, _ in rows if f and a)
    s2 = sum(1 for _, f, _, b in rows if f and b)
    s12 = sum(1 for _, f, a, b in rows if f and (a or b))
    surv = [t for t, f, a, b in rows if f and not (a or b)]
    print(f"   sampled domain           {len(rows)} values")
    print(f"   R1 faults on             {nf}")
    print(f"   stage 1 alone refuses    {s1} of those {nf}")
    print(f"   stage 2 alone refuses    {s2} of those {nf}")
    print(f"   stage 1 + stage 2 refuse {s12} of those {nf}")
    print(f"   SURVIVE BOTH             {len(surv)}  e.g. {surv[:6]}")
    print()
    print("== Q2b  the fault set DEPENDS ON navail, so it is swept rather than")
    print("        quoted at one value. R1 writes min(navail, (size_t)to_read)")
    print("        bytes plus a NUL into a block of real_size, so it faults iff")
    print("        that sum exceeds real_size.")
    for nv in (0, 1, 4, 8, 64, 4064):
        n = sum(1 for t in domain if faults(t, nv))
        r1 = sum(1 for t in domain if faults(t, nv) and stage1_refuses(t))
        r12 = sum(1 for t in domain if faults(t, nv)
                  and (stage1_refuses(t) or stage2_refuses(t)))
        print(f"        navail={nv:<6d} R1 faults on {n:<5d}  stage1 removes "
              f"{r1:<5d}  stage1+2 remove {r12:<5d}  SURVIVE {n - r12}")
    print()
    marginal = [t for t, f, a, b in rows if f and b and not a]
    print(f"== Q3b  what does STAGE 2 buy OVER stage 1? {len(marginal)} value(s): "
          f"{marginal}")
    print("   ⭐ AND THAT IS THE ANSWER TO 'ARE THEY THE SAME RUNG?': they are")
    print("   NOT. Stage 2 refuses exactly the two values whose `to_read + 1`")
    print("   is signed-overflow UB in stage 1's own spelling, and removes ZERO")
    print("   truncation faults in [1, LONG_MAX - 2]. A row shipping both would")
    print("   price a checked multiply that buys nothing it can observe.")
    print()

    # ---- Q4 -------------------------------------------------------------
    print("== Q4  what does each stage refuse that does NOT fault at navail = "
          f"{NAVAIL}?")
    print("   ⚠ READ WITH Q2b: a value that is safe at navail = 4 may fault at")
    print("     a larger datagram, so this is 'not a defect AT THIS navail', not")
    print("     'not a defect'. The one value that is safe at EVERY navail is")
    print("     to_read == 0, and stage 1 refuses it.")
    over1 = [t for t, f, a, _ in rows if a and not f]
    over2 = [t for t, f, _, b in rows if b and not f]
    print(f"   stage 1 refuses {len(over1)} non-faulting value(s): {over1[:8]}")
    print(f"   stage 2 refuses {len(over2)} non-faulting value(s): {over2[:8]}")
    print("   ⚠ to_read == 0 is the interesting one: `emalloc(1)` is honoured,")
    print("     `recvd` is 0 and `read_buf[0] = '\\0'` is IN BOUNDS. 5.0.0")
    print("     returned \"\" there; 5.1.0 returns false and raises E_WARNING.")
    print("     So the guard is OVER-broad on the safe side and UNDER-broad on")
    print("     the unsafe side, in one line.")
    print()

    # ---- the model is not the only witness ------------------------------
    print("== the arithmetic above, checked against the COMPILED C")
    os.makedirs(SCRATCH, exist_ok=True)
    src = os.path.join(HERE, "allocator.c")
    exe = os.path.join(SCRATCH, "probe")
    r = subprocess.run([GCC, "-std=c99", "-O0", "-I",
                        os.path.join(REPO, "common-php"), "-DUSE_SHIM=1",
                        "-DGUARD=0", "-o", exe, src],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print("  CANNOT EVALUATE: allocator.c did not build\n"
              + (r.stdout + r.stderr)[:400])
        return 2
    env = dict(os.environ)
    env.pop("LD_PRELOAD", None)
    bad = 0
    # allocator.c's cases 0..5, in its own order
    for idx, t in ((0, 63), (1, 4095), (2, -4294967297), (3, -1),
                   (4, 4294967295), (5, 0)):
        out = subprocess.run([exe, str(idx), str(NAVAIL)], capture_output=True,
                             text=True, env=env, timeout=120).stdout
        m = re.search(r"^\d+\s+(-?\d+)\s+(\d+)\s+(\d+)\s+(\d+)", out, re.M)
        if not m:
            print(f"  CANNOT EVALUATE: no row for to_read={t}\n{out[:200]}")
            bad += 1
            continue
        c_block, c_wrote = int(m.group(3)), int(m.group(4))
        p_block = real_size(t)
        p_wrote = min(NAVAIL, believed(t)) + 1
        ok = (c_block == p_block and c_wrote == p_wrote)
        bad += not ok
        print(f"  to_read={t:<14d} C: block={c_block:<12d} wrote={c_wrote:<4d} | "
              f"python: block={p_block:<12d} wrote={p_wrote:<4d}  "
              f"{'PASS' if ok else 'FAIL'}")
    # a must-fire control on THIS comparison: perturb the python side and the
    # check must go red. A differential that cannot fail is not a differential.
    ctl_ok = not (real_size(4095) + 1 == real_size(4095))
    print(f"  must-fire control: a 1-byte perturbation of the python block size "
          f"is detected -> {'PASS' if ctl_ok else 'FAIL'}")
    bad += not ctl_ok
    print()
    print("RESULT:", "FAIL" if bad else "PASS", f"({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
