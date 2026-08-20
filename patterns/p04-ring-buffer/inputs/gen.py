#!/usr/bin/env python3
"""Generate p04's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p04-ring-buffer/inputs/gen.py            # the 5 matrix inputs
    python3 patterns/p04-ring-buffer/inputs/gen.py --sweep    # + the four sweep bands

Payload layout (../spec.md), p16's/p17's/p05's/p07's/p11's/p03's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE      declared operation count   ATTACKER DATA
    byte 4..      operations, 5 bytes each: op u8 (0 = PUSH, else POP)
                                            val u32 LE
    data_start = 4 ; avail = len - 4 bytes actually present

and the kernel runs the operations against a fixed `uint64_t ring[64]` with two
cursors. The guard R1 omits, and the only thing it omits, is the FULLNESS check:

    R1   ring[tail] = val; tail = (tail + 1) % RING_CAP;
    R1h  if ((tail + 1) % RING_CAP != head) { ring[tail] = val; tail = ...; }

--------------------------------------------------------------------------
WHY EVERY SHIPPED MATRIX INPUT KEEPS THE RING BELOW CAPACITY
--------------------------------------------------------------------------
p04's bug is a WRITE, and `.memory/02-bench-rules.md`'s inheritance table puts
p04 in the **does not inherit** row: the guard's threshold is `RING_CAP`, a
*live length below the allocation's extent*, not the extent itself, so "the
guard fired" and "the unguarded rung committed UB" are INDEPENDENT events. Every
index p04 forms is `< RING_CAP` in every rung, R1 included. So the choice here
is free, and it is made the same way a read pattern's would be: `small` and
`large` are inputs on which **all eight cells must print the same checksum**, so
neither may contain a push onto a full ring. `sweep-f*` is where they live, and
sweep blobs are dropped from the checksum stage and from the measurement matrix
by the `sweep-` prefix (`.memory/05-layout.md`).

--------------------------------------------------------------------------
small AND large DIFFER IN FILL RATIO, NOT ONLY IN SIZE
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues and
records p01's modulus 4, p02's 16, p16's 4, p17's 4, p05's 8-and-16, p07's
octave, p11's string length and p03's pop density. p04's second axis is the
**fill ratio** -- the mean ring occupancy as a fraction of the 63 usable slots
-- because the fullness check's cost is per *rejected* push and the occupancy is
what decides how close an input is to rejecting. `small` hovers at ~6/63 and
`large` at ~55/63, and `_check_residues()` additionally asserts that `nops`, the
executed pop count and the stride differ mod 4, 8, 16 and 32 between the two.

There is no unroll factor to alias against: the kernel's loop body is a
data-dependent two-way branch and neither gcc, clang nor rustc unrolls it
(checked on the disassembly, ../NOTES.md 1), which is why the moduli here are
about residues of a count rather than about a vector width.

--------------------------------------------------------------------------
SIZES
--------------------------------------------------------------------------
  * `small`: 12 windows x 1189 B = 13.9 KiB, inside this box's 32 KiB L1.
    237 operations per window, 118 of them POPs, occupancy hovering near 6.
  * `large`: 2000 windows x 4154 B = 7.9 MiB, ~8x this box's 1 MiB/core L2, so
    the window the driver jumps to is cold. 830 operations per window, 413 of
    them POPs, occupancy hovering near 55 -- **13x `small`'s fill ratio and
    still four slots short of rejecting a push.**
  * every adversarial input is exactly one window (`n_blob == stride`), for
    p16's, p17's, p07's, p11's and p03's reason: `k = (acc * nwin) >> 64` is
    pseudo-random over `[0, nwin)`, so with several windows the malformed one is
    hit only probabilistically and the gate would record a mixture.
  * **window 0 must serve something** (p17, `.memory/01-ladder.md`): a window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`. Every
    window here returns `((acc*31 + head)*31 + tail)*31 + nops` with
    `nops != 0`, so no window can return 0 except by failing the length check on
    purpose, which is exactly and only what `adversarial-count` does -- and that
    file has ONE window, so `k` is 0 regardless.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run, so the cost of a row is the payload `to_vec` (a bulk copy --
`head1_u64_bytes`) plus `4 x stride` bytes read. That is 4756 byte-visits on
`small` and 16 616 on `large`, against `.memory`'s measured budget of ~3.05 M in
180 s, so both rows are ~180x inside it.
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "common"))
import slb  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 0x5EC1ADDE  # "sec-ladder", fixed forever: the .bin files are gitignored
                   # and must be regenerable byte-for-byte from this file alone.

HDR = 4                                   # nops:u32
OPLEN = 5                                 # op:u8 + val:u32
RING_CAP = 64                             # the constant every rung carries
USABLE = RING_CAP - 1                     # one slot is reserved: the ring is
                                          # FULL at 63 elements, because
                                          # (tail + 1) % CAP == head is the test

PUSH, POP = 0, 1

# The two measured shapes. `(nops, npop, target occupancy)`.
SMALL_NOPS, SMALL_NPOP, SMALL_OCC = 237, 118, 6
SMALL_WINS = 12
LARGE_NOPS, LARGE_NPOP, LARGE_OCC = 830, 413, 55
LARGE_WINS = 2000

SMALL_ITERS, LARGE_ITERS = 6000, 1500
ADV_ITERS = 8

RESIDUE_MODULI = (4, 8, 16, 32)


# ----------------------------------------------------------------- streams ---

def walk(rng, nops, npop, occ):
    """`nops` op bytes of which exactly `npop` are POPs, **every one of which
    executes**, and no PUSH is ever rejected -- with the occupancy biased toward
    `occ`.

    The property that must hold on a *measured* input is that R1 never pushes
    onto a full ring: `small` and `large` are the inputs on which all eight
    cells must print the same checksum, and R1's silent overwrite would break
    it. So this walk never emits a PUSH at depth `USABLE` and never a POP at
    depth 0.

    Feasibility is a property of the counts alone. Write `d` for the depth and
    `rp`/`rq` for the pushes/pops still to place; `d + rp - rq` is invariant and
    equals the final depth, so `d == 0 && rp == 0` implies a negative final
    depth and `d == USABLE && rq == 0` implies one above the cap. Neither can
    happen while `0 <= npush - npop <= USABLE`, which is asserted below, so a
    greedy scheduler never paints itself into a corner."""
    npush = nops - npop
    assert 0 <= npush - npop <= USABLE, (
        f"walk() needs 0 <= npush - npop <= {USABLE}, got {npush} - {npop}")
    ops = []
    d = 0
    rp, rq = npush, npop
    for _ in range(nops):
        if d == 0 or rq == 0:
            op = PUSH
        elif d == USABLE or rp == 0:
            op = POP
        else:
            # Bias toward the target occupancy, then fall back on what is left
            # of each count so the exact totals are still met.
            bias = 0.5 + 0.5 * max(-1.0, min(1.0, (d - occ) / 8.0))
            share = rq / (rp + rq)
            op = POP if rng.random() < 0.5 * bias + 0.5 * share else PUSH
        if op == PUSH:
            rp -= 1
            d += 1
        else:
            rq -= 1
            d -= 1
        ops.append(op)
    assert rp == 0 and rq == 0, (rp, rq)
    assert ops.count(POP) == npop, (ops.count(POP), npop)
    x = counts(ops)
    assert x["dpush"] == 0 and x["epop"] == 0, x
    return ops


def counts(ops):
    """The four things an operation can be, which are the regressors
    ../NOTES.md 4's laws are linear in. `xpush` a push that pushes, `dpush` a
    push the FULLNESS guard drops, `xpop` a pop that pops, `epop` a pop that
    finds the ring empty. Computed exactly as the checked kernel runs, with the
    two cursors rather than with a depth counter, so this function and the rungs
    cannot disagree about what "full" means."""
    head = tail = 0
    c = dict(xpush=0, dpush=0, xpop=0, epop=0)
    for op in ops:
        if op == PUSH:
            if (tail + 1) % RING_CAP != head:
                tail = (tail + 1) % RING_CAP
                c["xpush"] += 1
            else:
                c["dpush"] += 1
        else:
            if head != tail:
                head = (head + 1) % RING_CAP
                c["xpop"] += 1
            else:
                c["epop"] += 1
    return c


def window(nops_decl, ops, vals):
    """A window: the declared count, then one 5-byte record per operation.

    `nops_decl` is written verbatim rather than derived from `ops`, so that
    `adversarial-count` can declare a count the window cannot hold -- which is
    the row that shows the length check is in every rung."""
    out = bytearray(nops_decl.to_bytes(4, "little"))
    for op, v in zip(ops, vals):
        out.append(op)
        out += (v & 0xFFFFFFFF).to_bytes(4, "little")
    return bytes(out)


def values(rng, n):
    """One value per operation. Non-zero and all distinct-ish, so that a rung
    which popped the wrong slot cannot land on the right checksum by luck."""
    return [rng.randrange(1, 1 << 32) for _ in range(n)]


def stride_of(nops):
    return HDR + OPLEN * nops


def mean_occupancy(ops):
    """The FILL RATIO's numerator: mean live elements over the window's run."""
    head = tail = 0
    tot = 0
    for op in ops:
        if op == PUSH:
            if (tail + 1) % RING_CAP != head:
                tail = (tail + 1) % RING_CAP
        else:
            if head != tail:
                head = (head + 1) % RING_CAP
        tot += (tail - head) % RING_CAP
    return tot / len(ops) if ops else 0.0


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    or residue artefact. Returns a list of problems (empty when healthy)."""
    bad = []
    pairs = [("nops", SMALL_NOPS, LARGE_NOPS),
             ("npop", SMALL_NPOP, LARGE_NPOP),
             ("stride", stride_of(SMALL_NOPS), stride_of(LARGE_NOPS))]
    for label, a, b in pairs:
        for m in RESIDUE_MODULI:
            if a % m == b % m:
                bad.append(f"small and large {label} ({a}, {b}) are both "
                           f"== {a % m} (mod {m}); pick values in different "
                           f"residue classes or the delta you publish is one "
                           f"residue wearing the label of a constant")
    if abs(SMALL_OCC - LARGE_OCC) < 16:
        bad.append(f"small and large target occupancy ({SMALL_OCC}, "
                   f"{LARGE_OCC}) are within 16 of each other; the FILL RATIO "
                   f"is p04's second axis (../spec.md) and the two measured "
                   f"inputs must sit on different points of it")
    for label, occ in (("small", SMALL_OCC), ("large", LARGE_OCC)):
        if not 0 < occ < USABLE:
            bad.append(f"{label} target occupancy {occ} is outside "
                       f"(0, {USABLE}); a shipped matrix input may never reject "
                       f"a push (see the module docstring)")
    return bad


def tiled(rng, nwin, nops, npop, occ):
    """`nwin` windows, identical in *shape* and different in *content*.

    Every window has the same `nops`, the same `npop` and therefore the same
    `work_per_call`; the op ORDER and the values differ per window, so the
    driver's anti-collapse barrier stays honest and no two windows produce the
    same checksum."""
    out = bytearray()
    occs = []
    for _ in range(nwin):
        ops = walk(rng, nops, npop, occ)
        occs.append(mean_occupancy(ops))
        out += window(nops, ops, values(rng, nops))
    return bytes(out), sum(occs) / len(occs)


def write(name, n_iters, stride, body, declared_len=None, note=""):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<9d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}{note}")


# ---- adversarial-overwrite: sustained pushes onto a FULL ring ---------------
#
# THE BUG. One window: 63 pushes fill the ring, then 137 more arrive. Every
# checked rung drops all 137 -- `(tail + 1) % RING_CAP == head` -- and returns
# the 63 it kept. R1 has no fullness test, so its 64th push stores into the one
# RESERVED slot and advances `tail` onto `head`: the ring now reads EMPTY and
# all 63 live elements are unreachable. **No index leaves [0, 64) in any rung.**
OVERWRITE_FILL, OVERWRITE_EXTRA = 63, 137

# ---- adversarial-wrap: head and tail crossing the wrap point repeatedly -----
#
# THE CONTROL for the modular arithmetic itself. A balanced walk at low
# occupancy, long enough that each cursor advances past 0 several times, so the
# `% RING_CAP` on both cursors is exercised in both directions. Every rung
# including R1 agrees, because the ring never fills.
WRAP_NOPS, WRAP_NPOP, WRAP_OCC = 520, 259, 3

# ---- adversarial-count: the declared count the window cannot hold -----------
#
# THE OTHER CONTROL. `nops = 4096` against a window holding 40 operations, so
# `5*nops = 20480 > avail = 200`. The length check is in every rung, so every
# rung returns 0 -- and a 0 checksum is a weak oracle, which is why this row is
# here for the *behaviour* table rather than for its value.
COUNT_DECL = 4096
COUNT_NOPS = 40

# `--sweep`: four bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# **Band N -- the operation-count axis, 64 consecutive counts.** Balanced, every
# op executing, occupancy low. 64 consecutive values is two full cycles of any
# modulus up to 32.
SWEEP_N_NOPS = tuple(range(8, 72))

# **Band D -- the PUSH:POP RATIO at fixed count.** Band N moves the count and
# holds the ratio, so every per-operation constant it yields is confounded
# between `xpush` and `xpop`. Band D moves the pop count at a fixed 240
# operations, every op still executing, which is what separates the two
# (`.memory/01-ladder.md`: separating those is where p16's `nrec + 3` and p05's
# "+11.00 flat" both died). It stops at 96 because `npush - npop <= 63` is what
# "every push executes" costs.
SWEEP_D_NOPS = 240
SWEEP_D_NPOPS = tuple(range(96, 121, 3))

# **Band F -- the FILL RATIO, and the band the pattern is named for.** 63 pushes
# fill the ring, `q` more are REJECTED, then the remainder alternates POP/PUSH
# at the cap so the ring stays full and every later push is accepted only
# because a pop just made room. This is the only band on which the fullness
# check ever fires, and therefore the only band on which R1 stops running the
# same program as the model.
SWEEP_F_NOPS = 240
SWEEP_F_DROPS = tuple(range(0, 121, 10))

# **Band E -- the EMPTY POP.** `q` POPs against an empty ring first, then a
# balanced walk. This is the band that decides whether the emptiness check's
# cost is per POP *operation* or per pop that actually *pops*, and it is what
# makes `epop` identifiable at all: `small`, `large` and the other three bands
# all have `epop == 0`.
SWEEP_E_NOPS = 200
SWEEP_E_EMPTIES = tuple(range(0, 121, 10))

SWEEP_WINS = 8
SWEEP_ITERS = 2000


def band_f_ops(q):
    """63 pushes, `q` rejected pushes, then POP/PUSH alternation at the cap."""
    ops = [PUSH] * OVERWRITE_FILL + [PUSH] * q
    rest = SWEEP_F_NOPS - len(ops)
    ops += [POP if (i % 2 == 0) else PUSH for i in range(rest)]
    return ops


def band_e_ops(rng, q):
    """`q` POPs against an empty ring, then a balanced walk."""
    n = SWEEP_E_NOPS - q
    return [POP] * q + walk(rng, n, n // 2, 4)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p04 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: nops {SMALL_NOPS}/{LARGE_NOPS}, npop "
          f"{SMALL_NPOP}/{LARGE_NPOP}, strides "
          f"{stride_of(SMALL_NOPS)}/{stride_of(LARGE_NOPS)}, target occupancy "
          f"{SMALL_OCC}/{LARGE_OCC} of {USABLE}")

    # ---- the two measured inputs -----------------------------------------
    body, occ = tiled(rng, SMALL_WINS, SMALL_NOPS, SMALL_NPOP, SMALL_OCC)
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NOPS), body,
          note=f"  fill={occ / USABLE:.3f}")
    body, occ = tiled(rng, LARGE_WINS, LARGE_NOPS, LARGE_NPOP, LARGE_OCC)
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NOPS), body,
          note=f"  fill={occ / USABLE:.3f}")

    # ---- adversarial ------------------------------------------------------
    # (1) THE pattern: sustained pushes onto a full ring, all in bounds.
    n = OVERWRITE_FILL + OVERWRITE_EXTRA
    write("adversarial-overwrite.bin", ADV_ITERS, stride_of(n),
          window(n, [PUSH] * n, values(rng, n)))

    # (2) CONTROL: the modular arithmetic itself, both cursors past 0 repeatedly.
    ops = walk(rng, WRAP_NOPS, WRAP_NPOP, WRAP_OCC)
    write("adversarial-wrap.bin", ADV_ITERS, stride_of(WRAP_NOPS),
          window(WRAP_NOPS, ops, values(rng, WRAP_NOPS)),
          note=f"  wraps={counts(ops)['xpop'] // RING_CAP}")

    # (3) CONTROL: the length check, which is in every rung.
    write("adversarial-count.bin", ADV_ITERS, stride_of(COUNT_NOPS),
          window(COUNT_DECL, walk(rng, COUNT_NOPS, COUNT_NOPS // 2, 4),
                 values(rng, COUNT_NOPS)))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for n in SWEEP_N_NOPS:
            body, _ = tiled(rng, SWEEP_WINS, n, n // 2, 4)
            write(f"sweep-n{n:03d}.bin", SWEEP_ITERS, stride_of(n), body)
        for q in SWEEP_D_NPOPS:
            body, _ = tiled(rng, SWEEP_WINS, SWEEP_D_NOPS, q, 30)
            write(f"sweep-d{q:03d}.bin", SWEEP_ITERS, stride_of(SWEEP_D_NOPS),
                  body)
        for q in SWEEP_F_DROPS:
            body = bytearray()
            for _ in range(SWEEP_WINS):
                body += window(SWEEP_F_NOPS, band_f_ops(q),
                               values(rng, SWEEP_F_NOPS))
            write(f"sweep-f{q:03d}.bin", SWEEP_ITERS, stride_of(SWEEP_F_NOPS),
                  bytes(body))
        for q in SWEEP_E_EMPTIES:
            body = bytearray()
            for _ in range(SWEEP_WINS):
                body += window(SWEEP_E_NOPS, band_e_ops(rng, q),
                               values(rng, SWEEP_E_NOPS))
            write(f"sweep-e{q:03d}.bin", SWEEP_ITERS, stride_of(SWEEP_E_NOPS),
                  bytes(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
