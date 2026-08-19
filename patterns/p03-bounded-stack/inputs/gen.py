#!/usr/bin/env python3
"""Generate p03's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and since TASK_021 `harness/check.py` hashes it into `source_sha256`, so every
law measured on these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p03-bounded-stack/inputs/gen.py            # the 6 matrix inputs
    python3 patterns/p03-bounded-stack/inputs/gen.py --sweep    # + the four sweep bands

Payload layout (../spec.md), p16's/p17's/p05's/p07's/p11's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE      declared operation count   ATTACKER DATA
    byte 4..      operations, 5 bytes each: op u8 (0 = PUSH, else POP)
                                            val u32 LE
    data_start = 4 ; avail = len - 4 bytes actually present

and the kernel runs the operations against a fixed `uint64_t stack[64]`. The
guard that R1 omits, and the only thing it omits, is the guard on the POP:

    R1   sp = sp - 1; acc = acc*31 + stack[sp];              /* no test */
    R1h  if (sp > 0) { sp = sp - 1; acc = acc*31 + stack[sp]; }

--------------------------------------------------------------------------
THE OP STREAM IS THE CONTROL FLOW, AND THAT IS WHY THE ORDER IS GENERATED
--------------------------------------------------------------------------
Every earlier pattern here varies only the *data*: p16's lengths, p17's suffix
table, p05's dimensions, p07's keys, p11's string bytes. p03's file decides, per
step, which of two code paths runs. So this generator does not draw op bytes
independently -- it walks a constrained random walk, because three different
things have to be controllable independently:

  * **how many operations** there are            -> `sweep-n*`
  * **what fraction of them are POPs**           -> `sweep-d*`
  * **whether the POP's guard is TAKEN**         -> `sweep-e*`
  * **whether the op byte is PREDICTABLE**       -> `sweep-b*`

`walk()` below is the generator for the first, second and fourth: it emits
exactly `npop` POPs among `nops` operations and **every one of them pops**,
because it never emits a POP at `sp == 0`. It deliberately does NOT promise the
same of the PUSHes, and that is arithmetic rather than a concession: a stream
with `npush - npop > STACK_CAP` cannot keep every push in *any* order, because
the final depth would exceed the array. So **any density below 50% saturates the
stack** and the push guard starts dropping -- which is a real regime for a stack
machine, and it is the second thing `large` differs from `small` in. Both sides
of that are measured: `executed_pops()` here and `work_per_call` in ../model.py
agree with the model's own count on every shipped blob.

`free_walk()` is the generator for the third: it draws op bytes with no
constraint at all, so an unbalanced stream leaves POPs whose guard is *not*
taken. That is the band that separates "per POP operation" from "per POP that
actually pops", which is the axis ../NOTES.md 4 publishes the law in.

--------------------------------------------------------------------------
small AND large DIFFER IN POP DENSITY, NOT ONLY IN SIZE
--------------------------------------------------------------------------
`.memory/01-ladder.md` says to give `small` and `large` different residues and
records p01's modulus 4, p02's 16, p16's 4, p17's 4, p05's 8-and-16, p07's
octave and p11's string length. p03's second axis is the **pop density**, which
is the variable its law is linear in, so `small` is 50% POPs and `large` is 25%
-- ../spec.md requires them to differ, and `_check_residues()` additionally
asserts that `nops`, the executed pop count and the stride differ mod 4, 8, 16
and 32 between the two.

There is no unroll factor to alias against: the kernel's loop body is a
data-dependent two-way branch and neither gcc, clang nor rustc unrolls it
(checked on the disassembly, ../NOTES.md 1), which is why the moduli here are
about residues of a count rather than about a vector width.

--------------------------------------------------------------------------
SIZES
--------------------------------------------------------------------------
  * `small`: 12 windows x 1189 B = 13.9 KiB, inside this box's 32 KiB L1.
    237 operations per window, 118 of them POPs (49.8%).
  * `large`: 2000 windows x 4154 B = 7.9 MiB, ~8x this box's 1 MiB/core L2, so
    the window the driver jumps to is cold. 830 operations per window, 207 of
    them POPs (24.9%) -- so `large`'s stack RUNS FULL and its push guard drops
    values, where `small`'s hovers around half. The two differ in the pop
    density and, because of it, in the stack occupancy; ../NOTES.md 3 quotes
    both beside every per-call number.
  * every adversarial input is exactly one window (`n_blob == stride`), for
    p16's, p17's, p07's and p11's reason: `k = (acc * nwin) >> 64` is
    pseudo-random over `[0, nwin)`, so with several windows the malformed one is
    hit only probabilistically. p03 has a second, sharper reason: the address
    that goes out of range is **on the stack**, so a stray POP in a middle
    window is *just as much* a memory error as one in window 0 -- but the
    checksum it produces depends on stack garbage, and with one window the gate
    records one value rather than a mixture.
  * **window 0 must serve something** (p17, `.memory/01-ladder.md`): a window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`. Every
    window here returns `(acc*31 + sp)*31 + nops` with `nops != 0`, so no
    window can return 0 except by failing the length check on purpose, which is
    exactly and only what `adversarial-count` does -- and that file has ONE
    window, so `k` is 0 regardless and the absorbing state cannot bite.

And one about Miri, which is an `inputs/gen.py` decision and not a `check.py`
one (`.memory/05-layout.md` demand 8). `check.py` rewrites `n_iters` to 4 for
every Miri run, so the cost of a row is the payload `to_vec` (a bulk copy --
`head1_u64_bytes`) plus `4 x stride` bytes read. That is 4756 byte-visits on
`small` and 16 616 on `large`, against `.memory`'s measured budget of ~3.05 M in
180 s, so both rows are ~180x inside it. The only cost is the 8.3 MB `to_vec`;
p07's 12 MB one passes.
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
STACK_CAP = 64                            # the constant every rung carries

PUSH, POP = 0, 1

# The two measured shapes. `(nops, npop)`; the pop DENSITY is the second axis
# and `_check_residues()` is what holds it apart from the first.
SMALL_NOPS, SMALL_NPOP = 237, 118         # 49.79% POPs
SMALL_WINS = 12
LARGE_NOPS, LARGE_NPOP = 830, 207         # 24.94% POPs
LARGE_WINS = 2000

SMALL_ITERS, LARGE_ITERS = 6000, 1500
ADV_ITERS = 8                             # R1 executes UB on two of them; there
                                          # is nothing to learn from doing it
                                          # 6000 times.

RESIDUE_MODULI = (4, 8, 16, 32)


# ----------------------------------------------------------------- streams ---

def walk(rng, nops, npop):
    """`nops` op bytes of which exactly `npop` are POPs, and **every POP pops**.

    The one property that must hold on a *measured* input is that R1 never pops
    an empty stack: `small` and `large` are the inputs on which all eight cells
    must print the same checksum, and R1's underflow would break that. So this
    walk never emits a POP at `sp == 0`.

    It does **not** promise that every PUSH pushes, and that is not a
    concession, it is arithmetic: a stream with `npush - npop > STACK_CAP`
    cannot keep every push, whatever the order, because the final depth would
    exceed the array. So any density below 50% saturates the stack and the push
    guard starts dropping -- which is a real regime for a stack machine and is
    the second thing `large` differs from `small` in. `executed_pops(ops)` is
    what the laws are stated in, and this walk makes it exactly `npop`.

    Priorities, in order: place a POP if the stack would otherwise fill; place a
    PUSH if the stack is empty; otherwise draw with probability proportional to
    what is left of each."""
    npush = nops - npop
    assert npop <= npush, f"walk() needs npop <= npush, got {npop}/{npush}"
    ops = []
    sp = 0
    rp, rq = npush, npop
    for _ in range(nops):
        if rq == 0:
            op = PUSH
        elif rp == 0:
            op = POP
        elif sp == 0:
            op = PUSH
        elif sp == STACK_CAP:
            op = POP
        else:
            op = POP if rng.random() * (rp + rq) < rq else PUSH
        if op == PUSH:
            rp -= 1
            if sp < STACK_CAP:
                sp += 1
        else:
            rq -= 1
            sp -= 1
        ops.append(op)
    assert rp == 0 and rq == 0, (rp, rq)
    assert ops.count(POP) == npop, (ops.count(POP), npop)
    assert executed_pops(ops) == npop, "a POP found an empty stack"
    return ops


def free_walk(rng, nops, npop):
    """`nops` op bytes of which exactly `npop` are POPs, in a uniformly random
    ORDER and with no constraint at all -- so a POP at `sp == 0` is a POP whose
    guard is not taken (and, in R1, a read below the array)."""
    ops = [POP] * npop + [PUSH] * (nops - npop)
    rng.shuffle(ops)
    return ops


def alternating(nops, npop):
    """The PREDICTABLE stream: PUSH, POP, PUSH, POP, ... `sp` oscillates 0<->1,
    every op executes, and the branch is period-2. Only defined for a balanced
    stream, which is the only place ../NOTES.md 4e compares it."""
    assert 2 * npop == nops, "the predictable stream is the balanced one"
    return [PUSH if (i % 2 == 0) else POP for i in range(nops)]


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


def executed_pops(ops):
    """How many POPs actually pop, i.e. how many find `sp > 0`. This is the
    regressor ../NOTES.md 4's laws are linear in, and it is a property of the
    stream rather than of the count."""
    sp, x = 0, 0
    for op in ops:
        if op == PUSH:
            if sp < STACK_CAP:
                sp += 1
        else:
            if sp > 0:
                sp -= 1
                x += 1
    return x


def _check_residues():
    """`small` and `large` must differ on every axis that could carry a codegen
    or residue artefact. Returns a list of problems (empty when healthy)."""
    bad = []
    ds = SMALL_NPOP / SMALL_NOPS
    dl = LARGE_NPOP / LARGE_NOPS
    if abs(ds - dl) < 0.10:
        bad.append(f"small and large pop density ({ds:.3f}, {dl:.3f}) are "
                   f"within 0.10 of each other; the pop density IS p03's second "
                   f"axis (../spec.md) and the two measured inputs must sit on "
                   f"different points of it or the per-pop law is measured "
                   f"twice at one place")
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
    return bad


def tiled(rng, nwin, nops, npop):
    """`nwin` windows, identical in *shape* and different in *content*.

    Every window has the same `nops`, the same `npop` and therefore the same
    `work_per_call`; the op ORDER and the values differ per window, so the
    driver's anti-collapse barrier stays honest and no two windows produce the
    same checksum."""
    out = bytearray()
    for _ in range(nwin):
        ops = walk(rng, nops, npop)
        out += window(nops, ops, values(rng, nops))
    return bytes(out)


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<7d} stride={stride:<9d} "
          f"n_blob={len(body):<10d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


# ---- adversarial-underflow: the FIRST operation is a POP --------------------
#
# One window, `nops` operations, and operation 0 is a POP against an empty
# stack. Every checked rung treats it as a no-op; R1 computes `sp = 0 - 1 =
# SIZE_MAX` and reads `stack[SIZE_MAX]`, which wraps to `stack - 1` -- 8 bytes
# below a 512-byte local array, inside the kernel's own frame. It does not
# fault; ASan reports `stack-buffer-underflow`. And the damage does not stop
# there: with `sp == SIZE_MAX` the PUSH guard `sp < STACK_CAP` is false for the
# rest of the call, so **one stray POP disables the stack for the whole
# window**. THIS is the input for this pattern.
UNDERFLOW_NOPS, UNDERFLOW_NPOP = 40, 12

# ---- adversarial-allpop: every operation is a POP ---------------------------
#
# The sustained case. R1 walks one 8-byte slot further down the stack on every
# operation; at 200 operations that is 1600 bytes below the frame, which is
# mapped stack and does not fault. (../NOTES.md 7 records where it DOES fault:
# 1 048 576 pops, i.e. exactly this box's 8 MiB `ulimit -s`. That is a measured
# threshold, not a designed one, and it is why this file does not use it.)
# Every checked rung returns `(0*31 + 0)*31 + nops == nops`.
ALLPOP_NOPS = 200

# ---- adversarial-overflow: more than STACK_CAP consecutive pushes -----------
#
# THE CONTROL. The push guard is in EVERY rung including R1, so this input must
# produce the identical checksum in all eight cells. 96 pushes (32 more than the
# cap) then exactly 64 pops: the push guard drops 32 values in every rung, and
# the drain stops exactly at `sp == 0` so that R1's *missing* guard is never
# reached and this row stays a clean control rather than becoming a second copy
# of `adversarial-underflow`. Without it, "only the POP guard is the variable"
# would be a claim about the source rather than a measurement.
OVERFLOW_PUSH, OVERFLOW_POP = 96, 64

# ---- adversarial-count: the declared count the window cannot hold -----------
#
# THE OTHER CONTROL. `nops = 4096` against a window holding 40 operations, so
# `5*nops = 20480 > avail = 200`. The length check is in every rung, so every
# rung returns 0 -- and a 0 checksum is a weak oracle, which is why this row is
# here for the *behaviour* table and the sanitiser row rather than for its
# value: it is the input that would fire ASan in R1 if the length check were
# the missing one, and it does not.
COUNT_DECL = 4096
COUNT_NOPS = 40

# `--sweep`: four bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure).
#
# **Band A -- the operation-count axis, 64 consecutive counts.** Density held at
# 50%, every op executing, so `xpops == nops//2` is a constant of the file and
# the per-operation rate can be read off a lag pair rather than fitted. 64
# consecutive values is two full cycles of any modulus up to 32; there is no
# unroll factor here to alias against (../NOTES.md 1) but the rule is the rule.
SWEEP_A_NOPS = tuple(range(8, 72))

# **Band B -- the POP-DENSITY axis at fixed count.** Band A moves the count and
# holds the density, so every per-operation constant it yields is confounded
# with the pop count. Band B moves the pop count over 13 values at a fixed 240
# operations, every op still executing, which is what separates the per-OP term
# from the per-POP term (`.memory/01-ladder.md`: separating those is where
# p16's `nrec + 3` and p05's "+11.00 flat" both died). It stops at 120 because
# 50% is where `walk()`'s "every op executes" becomes impossible -- and band C
# is what happens past it.
SWEEP_B_NOPS = 240
SWEEP_B_NPOPS = tuple(range(0, 121, 10))

# **Band C -- past 50%, where the POP GUARD IS TAKEN.** Unconstrained order, so
# the excess POPs find an empty stack and do nothing. This is the band that
# decides whether the law is per POP *operation* or per POP that actually
# *pops*, which no earlier pattern in this project had a way to ask.
SWEEP_C_NOPS = 240
SWEEP_C_NPOPS = tuple(range(130, 241, 10))

# **Band P -- the BRANCH lever, and it is cleaner than p07's compiler flag.**
# Two files with the identical operation count, the identical POP count, the
# identical number of executed pops and the same value distribution, differing
# only in the ORDER of the op bytes: `sweep-bpred` alternates PUSH/POP with
# period 2 and `sweep-brand` is a uniformly random constrained walk. The op
# stream is attacker-chosen, so predictability is a property of the DATA here,
# where p07 had to change the program to move it. `callgrind --branch-sim=yes`
# reports `Bcm` for both (`.memory/00-environment.md`).
SWEEP_P_NOPS = 240
SWEEP_P_WINS = 8
SWEEP_ITERS = 2000


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sweep", action="store_true",
                    help="also emit sweep-*.bin (diagnostic; the gate and "
                         "measure.py skip the sweep- prefix)")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p03 inputs ->", os.path.relpath(HERE, os.getcwd()))
    for p in _check_residues():
        print("gen.py: " + p, file=sys.stderr)
        return 1
    print(f"  residues ok: nops {SMALL_NOPS}/{LARGE_NOPS}, npop "
          f"{SMALL_NPOP}/{LARGE_NPOP}, strides "
          f"{stride_of(SMALL_NOPS)}/{stride_of(LARGE_NOPS)}, pop density "
          f"{SMALL_NPOP/SMALL_NOPS:.3f}/{LARGE_NPOP/LARGE_NOPS:.3f}")

    # ---- the two measured inputs -----------------------------------------
    write("small.bin", SMALL_ITERS, stride_of(SMALL_NOPS),
          tiled(rng, SMALL_WINS, SMALL_NOPS, SMALL_NPOP))
    write("large.bin", LARGE_ITERS, stride_of(LARGE_NOPS),
          tiled(rng, LARGE_WINS, LARGE_NOPS, LARGE_NPOP))

    # ---- adversarial ------------------------------------------------------
    # (1) THE pattern: operation 0 is a POP against an empty stack.
    ops = walk(rng, UNDERFLOW_NOPS - 1, UNDERFLOW_NPOP - 1)
    ops = [POP] + ops
    assert ops.count(POP) == UNDERFLOW_NPOP
    write("adversarial-underflow.bin", ADV_ITERS, stride_of(UNDERFLOW_NOPS),
          window(UNDERFLOW_NOPS, ops, values(rng, UNDERFLOW_NOPS)))

    # (2) the sustained case: every operation is a POP.
    write("adversarial-allpop.bin", ADV_ITERS, stride_of(ALLPOP_NOPS),
          window(ALLPOP_NOPS, [POP] * ALLPOP_NOPS, values(rng, ALLPOP_NOPS)))

    # (3) CONTROL: the guard that IS in every rung. 96 pushes, then 96 pops.
    n = OVERFLOW_PUSH + OVERFLOW_POP
    write("adversarial-overflow.bin", ADV_ITERS, stride_of(n),
          window(n, [PUSH] * OVERFLOW_PUSH + [POP] * OVERFLOW_POP,
                 values(rng, n)))

    # (4) CONTROL: the length check, which is also in every rung.
    write("adversarial-count.bin", ADV_ITERS, stride_of(COUNT_NOPS),
          window(COUNT_DECL, walk(rng, COUNT_NOPS, COUNT_NOPS // 2),
                 values(rng, COUNT_NOPS)))

    if a.sweep:
        print("  -- sweep (diagnostic, not part of the matrix)")
        for n in SWEEP_A_NOPS:
            write(f"sweep-n{n:03d}.bin", SWEEP_ITERS, stride_of(n),
                  tiled(rng, 8, n, n // 2))
        for q in SWEEP_B_NPOPS:
            write(f"sweep-d{q:03d}.bin", SWEEP_ITERS, stride_of(SWEEP_B_NOPS),
                  tiled(rng, 8, SWEEP_B_NOPS, q))
        for q in SWEEP_C_NPOPS:
            body = bytearray()
            for _ in range(8):
                ops = free_walk(rng, SWEEP_C_NOPS, q)
                body += window(SWEEP_C_NOPS, ops, values(rng, SWEEP_C_NOPS))
            write(f"sweep-e{q:03d}.bin", SWEEP_ITERS, stride_of(SWEEP_C_NOPS),
                  bytes(body))
        # Band P: the branch pair. Same counts, same executed counts, same
        # values -- only the ORDER of the op bytes differs.
        half = SWEEP_P_NOPS // 2
        for tag, mk in (("bpred", lambda r: alternating(SWEEP_P_NOPS, half)),
                        ("brand", lambda r: walk(r, SWEEP_P_NOPS, half))):
            body = bytearray()
            prng = random.Random(SEED ^ 0x03)     # the SAME value stream for
            orng = random.Random(SEED ^ 0x30)     # both files, by construction
            for _ in range(SWEEP_P_WINS):
                body += window(SWEEP_P_NOPS, mk(orng), values(prng, SWEEP_P_NOPS))
            write(f"sweep-{tag}.bin", SWEEP_ITERS, stride_of(SWEEP_P_NOPS),
                  bytes(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
