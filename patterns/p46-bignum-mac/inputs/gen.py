#!/usr/bin/env python3
"""p46-bignum-mac input generator. Deterministic; the gate hashes THIS FILE and
never the blobs, so the determinism is the whole basis of the claim that the
committed `.bin` files are reproducible. Regenerate twice and diff.

File format (`.memory/02-bench-rules.md`): `u64 n_iters`, `u64 payload_len`,
payload. p46's payload is p19's, p36's, p22's, p38's, p47's and eleven others':

    word 0     u64  stride      # bytes per window
    byte 8..   u8[] blob        # the windows

Window layout (../spec.md):

    byte 0        u8   n      a-limb count                       ATTACKER DATA
    byte 1        u8   m      b-limb count                       ATTACKER DATA
    byte 2 .. 8        unused (keeps the limbs 8-aligned)
    byte 8 ..     u64 LE limbs: a[0..n] then b[0..m]             ATTACKER DATA

**THE LIMB COUNTS ARE ATTACKER DATA AND THAT IS THE WHOLE PATTERN.** With
compile-time operand sizes the bug is unreachable; p46 exists because real
bignum code -- OpenSSL's `BN_mul()` among it -- takes the operand word counts
from the objects it was handed and must size the product buffer from them.
`audit()` refuses to write any blob whose declared `oob` disagrees with the
simulation.

⚠ **AND IT AUDITS THE HARM, NOT JUST THE BYTES.** `sim_unvalidated()`
re-implements the reach of `c/kernel.c` -- the rung with no output-side bound --
and reports the highest product-scratch index it touches. `>= OUTCAP` is the
overflow. Two adversarial rows are shipped:

    adversarial-nearmiss   n=48 m=49   reaches index 96 -- EXACTLY ONE LIMB past
    adversarial-oob        n=90 m=90   reaches index 179 -- 84 limbs past

⚠ **THE REJ PATH IS ADVERSARIAL BY CONSTRUCTION and cannot be anywhere else.**
`REJ` is returned exactly when `n + m > OUTCAP` while `8 + 8*(n+m) <= stride`,
which is precisely the condition under which `c/kernel.c` writes out of bounds.
So any window that exercises the REJ branch is a window on which the buggy rung
disagrees with the other five, and the gate requires every cell to agree on a
non-adversarial input. p19's generator carries the same note for the same
structural reason.

`--sweep` appends the `sweep-*` band. The prefix is the whole mechanism
(`check.py`'s inline `sweep-` test and `measure.py::SKIP_INPUT_PREFIX` --
cited by NAME, because line citations decay): `sweep-*` blobs are
diagnostic, are not part of the measured matrix, and a band named otherwise
would enter it and cost a full re-measure.

**THREE bands, because p46's cost law has TWO parameters** and
`.memory/03-measurement.md`'s residue rule then applies to each of them
separately:

    band N   n varies, m = 24 held         -- the row-count axis
    band M   m varies, n = 24 held         -- the MAC-per-row axis
    band D   neither held                  -- OUT OF SAMPLE for a fit on N + M

⚠ **RESIDUE CLASSES.** Both axes' value lists are
`{1,2,3,4,5,6,7,8,9,11,13,16,17,19,23,24,32,33,40,48}`, which cover **all four
residues mod 4** and **all eight mod 8**; `main()` prints the coverage on every
run, so a class-dependent fit is visible before it is published rather than
after. Band D exists because a two-parameter law fitted on two axis-aligned
bands has never been tested off the axes, and p38's additivity failure was
exactly that shape.

⚠ **AND THE LAWS IN ../NOTES.md 8 ARE FITTED FROM THE SHIPPED BINARIES, NOT
FROM A PROBE.** `.memory/03-measurement.md`: a probe measures a SLOPE; its
INTERCEPT is a property of the probe. p46's pre-build probe
(`.temp/t89/cost.rs`) gave `R2 - R4 = 5 + 7n + 7nm`; the shipped figures are in
../NOTES.md 8 and the probe's intercept is not quoted anywhere.

The limb bytes come from a plain LCG rather than `random`, so no draw is
rejection-sampled and the stream cannot re-converge after an edit
(`.memory/05-layout.md`).
"""

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTCAP = 96                   # must equal SLB_P46_OUTCAP and every rung's const
BCAP = 256                    # must equal SLB_P46_BCAP and every rung's const
REJ = 0x9E3779B97F4A7C15
MASK = (1 << 64) - 1


# ------------------------------------------------------------------ build ----
def lcg(seed):
    """A bare Lehmer generator. Every draw consumes exactly one step, so adding
    or removing a blob shifts later blobs by a predictable amount and nothing is
    rejection-sampled."""
    x = (seed * 2 + 1) & 0xFFFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x


def window(n, m, seed):
    """One window: the two declared limb counts, six pad bytes, then `n + m`
    little-endian u64 limbs. The limbs are drawn full-width so that every MAC
    step carries a real carry -- a window of small limbs would make `carry` zero
    on most steps and the `adc` chain would stop being the thing measured."""
    if not (0 <= n <= 255 and 0 <= m <= 255):
        raise SystemExit(f"gen.py: n={n} m={m} do not fit in a byte")
    g = lcg(seed)
    body = bytearray()
    for _ in range(n + m):
        v = 0
        for s in range(4):
            v |= (next(g) & 0xFFFF) << (16 * s)
        v |= 1 << 63                       # keep every limb top-heavy
        body += struct.pack("<Q", v)
    return bytes([n, m, 0, 0, 0, 0, 0, 0]) + bytes(body)


def stride_for(n, m):
    return 8 + 8 * (n + m)


def emit(path, n_iters, blob, stride):
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload)))
        f.write(payload)


def emit_truncated(path, n_iters, blob, stride, extra):
    """Declare `extra` more payload bytes than the file carries. A conforming
    driver notices and exits 5."""
    payload = struct.pack("<Q", stride) + blob
    with open(path, "wb") as f:
        f.write(struct.pack("<QQ", n_iters, len(payload) + extra))
        f.write(payload)


# ------------------------------------------------------------------ audit ----
def ld64(w, p):
    return (w[p] + 256 * w[p + 1] + 65536 * w[p + 2] + 16777216 * w[p + 3]
            + 4294967296 * w[p + 4] + 1099511627776 * w[p + 5]
            + 281474976710656 * w[p + 6] + 72057594037927936 * w[p + 7])


def sim(blob, off, stride):
    """The kernel's DEFINED semantics (i.e. c/kernel_hardened.c's),
    re-implemented here so the generator can assert what it is shipping.
    Deliberately NOT imported from model.py: a generator that imported the model
    could not catch a model bug. This copy also uses ONE Python big-integer
    multiply where model.py's `bn_fold` walks the limbs, so the two disagree if
    either is wrong."""
    if stride < 8:
        return 0, "short"
    w = blob[off:off + stride]
    n, m = w[0], w[1]
    if n == 0 or m == 0:
        return 0, "zero"
    if 8 + 8 * (n + m) > stride:
        return 0, "nofit"
    if n + m > OUTCAP:
        return REJ, "rej"
    a = sum(ld64(w, 8 + 8 * i) << (64 * i) for i in range(n))
    b = sum(ld64(w, 8 + 8 * (n + j)) << (64 * j) for j in range(m))
    p = a * b
    acc = 0
    for k in range(n + m):
        acc = (acc * 31 + ((p >> (64 * k)) & MASK)) & MASK
    return ((acc * 31 + n) * 31 + m) & MASK, "product"


def sim_unvalidated(blob, off, stride):
    """`c/kernel.c`: the nest with no output-side bound. Returns the highest
    product-scratch index the window would touch, or `-1` for a window that
    never reaches the nest."""
    if stride < 8:
        return -1
    w = blob[off:off + stride]
    n, m = w[0], w[1]
    if n == 0 or m == 0:
        return -1
    if 8 + 8 * (n + m) > stride:
        return -1
    return n + m - 1


def audit(name, blob, stride, oob=False, zero_ok=False, reach=None):
    """What must hold of every shipped blob."""
    if stride <= 0:
        return f"{name}: stride {stride}"
    if len(blob) % stride:
        return f"{name}: blob {len(blob)} is not a multiple of stride {stride}"
    nwin = len(blob) // stride
    if nwin == 0:
        return f"{name}: no whole window"
    hi = max(sim_unvalidated(blob, w * stride, stride) for w in range(nwin))
    got_oob = hi >= OUTCAP
    if got_oob != oob:
        return (f"{name}: declared oob={oob} but c/kernel.c's nest reaches "
                f"scratch index {hi} against OUTCAP {OUTCAP}")
    if reach is not None and hi != reach:
        return (f"{name}: declared reach {reach} but the nest reaches {hi}")
    r0 = sim(blob, 0, stride)[0]
    # `.memory/01-ladder.md`: window 0 returning 0 is an ABSORBING STATE --
    # `acc` stays 0, the Lemire index stays 0, and every later call re-runs
    # window 0. A blob whose first window folds to 0 measures one window.
    if r0 == 0 and not zero_ok:
        return f"{name}: window 0 folds to 0 (absorbing state)"
    return None


# ----------------------------------------------------------------- matrix ----
def uniform(n, m, nwin, seed0):
    """`nwin` windows all declaring the same `(n, m)`, so `work_per_call` --
    which model.py MINIMISES over windows -- is exactly `n * m`."""
    return b"".join(window(n, m, seed0 + 37 * w) for w in range(nwin))


def matrix(out):
    rows = []

    # ---- small: 16 windows of n = m = 24, i.e. 576 MAC steps per call.
    S_N = S_M = 24
    rows.append(("small.bin", uniform(S_N, S_M, 16, 5), stride_for(S_N, S_M),
                 4000, dict(oob=False, zero_ok=False)))

    # ---- large: 16 windows of n = m = 48, i.e. 2304 MAC steps -- 4x small's
    #      MAC work on 2x the bytes, so the two probe inputs differ in
    #      `work_per_call` and the marginal-rate assertion can run.
    L_N = L_M = 48
    rows.append(("large.bin", uniform(L_N, L_M, 16, 11), stride_for(L_N, L_M),
                 1000, dict(oob=False, zero_ok=False)))

    # ---- degenerate: every guard branch except REJ, with a real-work window
    #      FIRST so the blob is not absorbing. REJ cannot be here -- see the
    #      module docstring.
    D_STRIDE = stride_for(24, 24)
    d = [window(20, 20, 23)]                       # real work
    d.append(window(0, 13, 29)[:8] + bytes(D_STRIDE - 8))     # n == 0
    d.append(window(13, 0, 31)[:8] + bytes(D_STRIDE - 8))     # m == 0
    d.append(window(40, 40, 41)[:D_STRIDE])        # 8 + 8*80 = 648 > 392: nofit
    d[0] = d[0] + bytes(D_STRIDE - len(d[0]))
    degen = b"".join(x[:D_STRIDE] + bytes(max(0, D_STRIDE - len(x))) for x in d)
    rows.append(("degenerate.bin", degen, D_STRIDE, 2000,
                 dict(oob=False, zero_ok=False)))

    # ---- adversarial-nearmiss: n + m = OUTCAP + 1. The MAC loop itself stays
    #      inside the array (`i + j <= n + m - 2 = 95`); it is the row's final
    #      carry store `out[i + m]` at `i = n - 1` that lands on index 96 --
    #      EXACTLY ONE LIMB PAST a 96-limb automatic array. ASan calls it
    #      `stack-buffer-overflow / WRITE of size 8`; on this box gcc's default
    #      `-fstack-protector-strong` turns it into `*** stack smashing
    #      detected ***` and clang -O2/-O3 into SIGSEGV (../NOTES.md 0a).
    A1_N, A1_M = 48, 49
    rows.append(("adversarial-nearmiss.bin", uniform(A1_N, A1_M, 2, 101),
                 stride_for(A1_N, A1_M), 100,
                 dict(oob=True, zero_ok=True, reach=OUTCAP)))

    # ---- adversarial-oob: n + m = 180, so the nest reaches scratch index 179
    #      -- 84 limbs (672 bytes) past the array, through the saved registers
    #      and the canary.
    A2_N, A2_M = 90, 90
    rows.append(("adversarial-oob.bin", uniform(A2_N, A2_M, 2, 103),
                 stride_for(A2_N, A2_M), 100,
                 dict(oob=True, zero_ok=True, reach=A2_N + A2_M - 1)))

    # ---- adversarial-tiny: stride below the 8-byte header. The driver enters
    #      the loop (its only guard is `stride_w > 0`) and the KERNEL's
    #      `len < 8` test returns 0 on every call, so the degenerate branch
    #      every rung carries is reachable from the measured domain instead of
    #      being dead code the proof still has to discharge.
    rows.append(("adversarial-tiny.bin", bytes(range(64)) * 4, 4, 100,
                 dict(oob=False, zero_ok=True)))

    made = []
    for name, blob, stride, iters, kw in rows:
        emit(os.path.join(out, name), iters, blob, stride)
        made.append((name, blob, stride, iters, kw))

    # ---- adversarial-shortlen: `payload_len` declares 64 bytes more than the
    #      file carries. Handled in `slb_load` / `driver::load`, exit 5.
    short = uniform(S_N, S_M, 2, 5)
    emit_truncated(os.path.join(out, "adversarial-shortlen.bin"), 100,
                   short, stride_for(S_N, S_M), 64)
    made.append(("adversarial-shortlen.bin", short, stride_for(S_N, S_M), 100,
                 dict(oob=False, zero_ok=False)))
    return made


# ------------------------------------------------------------------ sweep ----
#: The value list both axis bands use. Chosen to cover every residue mod 4 and
#: every residue mod 8 on each axis independently.
SWEEP_VALS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 16, 17, 19, 23, 24, 32, 33,
              40, 48]
#: The value the OTHER parameter is held at in each axis band.
SWEEP_HOLD = 24
#: Band D: off both axes, and never measured before a fit on N + M is published.
SWEEP_DIAG = [(10, 10), (12, 20), (20, 12), (30, 30), (36, 42), (42, 36),
              (7, 41), (41, 7), (44, 44), (3, 60)]


def sweep(out):
    """Bands N, M and D. Every blob is 4 windows of one `(n, m)`."""
    made = []
    pairs = ([(v, SWEEP_HOLD) for v in SWEEP_VALS]
             + [(SWEEP_HOLD, v) for v in SWEEP_VALS if v != SWEEP_HOLD]
             + SWEEP_DIAG)
    for (n, m) in pairs:
        if n + m > OUTCAP:
            raise SystemExit(f"gen.py: sweep pair ({n},{m}) is over OUTCAP")
        stride = stride_for(n, m)
        blob = uniform(n, m, 4, 7 * n + 13 * m + 3)
        name = f"sweep-n{n:03d}m{m:03d}.bin"
        emit(os.path.join(out, name), 400, blob, stride)
        made.append((name, blob, stride, 400, dict(oob=False, zero_ok=False)))
    return made


# ------------------------------------------------------------------- main ----
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    made = matrix(a.out)
    if a.sweep:
        made += sweep(a.out)

    bad = 0
    for name, blob, stride, iters, kw in made:
        problem = audit(name, blob, stride, **kw)
        if problem:
            print(f"AUDIT FAIL  {problem}", file=sys.stderr)
            bad += 1
            continue
        nwin = len(blob) // stride
        w = blob[0:stride]
        n, m = (w[0], w[1]) if stride >= 8 else (0, 0)
        r0, why = sim(blob, 0, stride)
        hi = max(sim_unvalidated(blob, k * stride, stride) for k in range(nwin))
        print(f"{name:28s} stride={stride:6d} n={n:3d} m={m:3d} "
              f"macs={n * m:6d} nwin={nwin:3d} blob={len(blob):8d} "
              f"iters={iters:6d} reach={hi:4d}/{OUTCAP} win0={why} {r0}")

    if a.sweep:
        ns = sorted({n for n, _ in
                     [(v, SWEEP_HOLD) for v in SWEEP_VALS] + SWEEP_DIAG})
        ms = sorted({m for _, m in
                     [(SWEEP_HOLD, v) for v in SWEEP_VALS] + SWEEP_DIAG})
        print(f"\nsweep band N: {len(SWEEP_VALS)} values of n at m={SWEEP_HOLD}"
              f"; n mod 4 covers {sorted({v % 4 for v in SWEEP_VALS})}"
              f", n mod 8 covers {sorted({v % 8 for v in SWEEP_VALS})}")
        print(f"sweep band M: {len(SWEEP_VALS) - 1} values of m at "
              f"n={SWEEP_HOLD}"
              f"; m mod 4 covers {sorted({v % 4 for v in SWEEP_VALS})}"
              f", m mod 8 covers {sorted({v % 8 for v in SWEEP_VALS})}")
        print(f"sweep band D: {len(SWEEP_DIAG)} OFF-AXIS pairs {SWEEP_DIAG}"
              f" -- out of sample for any fit on N + M")
        print(f"distinct n over N+D: {ns}\ndistinct m over M+D: {ms}")

    if bad:
        raise SystemExit(f"{bad} blob(s) failed the audit")


if __name__ == "__main__":
    main()
