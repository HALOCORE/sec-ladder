#!/usr/bin/env python3
"""Generate p27's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p27-handle-table/inputs/gen.py            # the 7 matrix inputs
    python3 patterns/p27-handle-table/inputs/gen.py --sweep     # + the three sweep bands

Payload layout (../spec.md), p06's/p11's/p16's/p17's/p05's/p07's/p03's/p12's/
p14's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects OPEN (0), CLOSE (1) or READ (2, 3) -- so every byte value is
a legal opcode and two of the four codes are reads. `a` is the record's value on
an OPEN and the slot number on a CLOSE or a READ. The conjunct R1 omits, and the
only thing it omits, is the LIVENESS test on the READ path:

    R1   if (h < ntab)                       acc = acc*31 + *tab[h];
    R1h  if (h < ntab && live[h] == 1)       acc = acc*31 + *tab[h];

--------------------------------------------------------------------------
WHY EVERY BENIGN WINDOW MUST READ ONLY LIVE SLOTS
--------------------------------------------------------------------------
Two independent reasons, and either alone would be enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree
     with `../model.py` **and with every other cell**. R1 reading a freed record
     disagrees with all of them, so such an input cannot be a perf row.
  2. TASK_055_REVIEW blocker B1: what a stale read *returns* is a function of
     the optimisation level. At `-O0` the store into the recycled record has
     happened and the stale read sees it; at `-O3` LLVM may dead-store-eliminate
     that store, because the recycled record's provenance differs from the stale
     pointer's, and the stale read then sees the ORIGINAL bytes. `build.py`
     builds both levels into one agreement set. Measured on the probe:
     `gcc -O0..-O2 2582767925679282152` against `gcc -O3 6789584477807083544`.

So the use-after-free lives on the `adversarial-*` rows alone, whose behaviour
`check.py` **records per cell** instead of requiring agreement (precedent:
`results/gate/p06-rotate.json`'s `adversarial-past48.bin/c-clang`, four
behaviours in four cells). This generator therefore runs a copy of the checked
kernel over every window it emits and refuses to write a benign blob in which
any READ names a slot that is in range and not alive.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE AN ALLOCATOR EXPERIMENT, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
A use-after-free has no magnitude axis -- there is no "one byte past" and "forty
bytes past". What it has instead is a RECYCLING axis, and that is what decides
whether the harm is disclosure or noise:

  `adversarial-uaf`      OPEN v0, CLOSE 0, OPEN v1, READ 0. glibc's tcache is
                         LIFO, so the second OPEN gets slot 0's chunk back and
                         writes `v1` into it. R1's stale read then returns
                         **another record's byte under this record's handle** --
                         a disclosure, deterministic at `-O0`, and the row the
                         pattern exists for.
  `adversarial-noreuse`  OPEN v0, CLOSE 0, READ 0, with no OPEN in between. The
                         chunk is still in the tcache, so bytes 0..8 of it are
                         glibc's safe-linked `next` word, which is a function of
                         the heap address and therefore of ASLR. R1 prints a
                         DIFFERENT number on every run. This row is here to show
                         that the harm is not always a disclosure and that a
                         naked use-after-free is not reproducible -- the
                         constraint `.memory/03-measurement.md` records.
  `adversarial-many`     24 stale reads in one window, so a rung that survives
                         one has to survive 24, and ASan's first report is not
                         the only one.
  `adversarial-stride3`  a 3-byte window, too small for the `nops` header. The
                         driver guard `stride_w >= 4` skips the loop entirely
                         and every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p27 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p27 is a READ pattern: R1's undefined behaviour is a LOAD through a dangling
pointer, and no rung ever stores out of bounds. So the write rule's threshold
test (p12, TASK_041) does not reach it at all, and "the guard fired" and "the
unguarded rung committed UB" are independent events -- which is exactly why the
adversarial rows can be confined to their own files.
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

SEED = 27
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
TABCAP = 32
SENT = 251

OPEN, CLOSE, READ = 0, 1, 2


# ---- op-stream construction -------------------------------------------------
def opbyte(rng, op):
    """A byte whose `% 4` is `op`. Two of the four residues are READ, so a READ
    is emitted with either 2 or 3 and the opcode byte is not a constant."""
    if op == READ:
        return 4 * rng.randrange(0, 64) + rng.choice((2, 3))
    return 4 * rng.randrange(0, 64) + op


def encode(rng, ops):
    """[(op, operand)] -> the window body, with an honest `nops` header."""
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, popen, pclose, cap=TABCAP):
    """A stream of `nops` operations in which **every READ and every CLOSE names
    a live slot**. Rejected operations (a CLOSE or READ with no live slot to
    name, or an OPEN past `cap`) are emitted as OPENs instead, so the stream
    never contains an operation whose outcome depends on the liveness bug."""
    ops, live, ntab = [], [], 0
    while len(ops) < nops:
        r = rng.random()
        if r < popen or not live:
            if ntab < cap and ntab < TABCAP:
                ops.append((OPEN, rng.randrange(1, 256)))
                live.append(ntab)
                ntab += 1
                continue
            # The generator's working set is full. A full-table OPEN is a
            # defined, agreeing operation in every rung, so it is fine to emit
            # one deliberately -- but the KERNEL's capacity is TABCAP, not
            # `cap`, so when `cap < TABCAP` the kernel ACCEPTS this open and
            # opens a slot this function is not tracking. Tracking it here is
            # what keeps the two slot numberings in step; the slot is
            # deliberately not added to `live`, so nothing ever names it and it
            # is freed by the epilogue.
            #
            # Without the `ntab += 1` the numberings drift and the generator
            # emits a READ of a slot it thinks is live and the kernel has
            # closed -- i.e. R1's bug, on a perf row. `_no_uaf` caught it on
            # `sweep-s15.bin`; this is the fix.
            ops.append((OPEN, rng.randrange(1, 256)))
            if ntab < TABCAP:
                ntab += 1
            continue
        if r < popen + pclose:
            h = rng.choice(live)
            live.remove(h)
            ops.append((CLOSE, h))
        else:
            ops.append((READ, rng.choice(live)))
    return ops


def mixed_ops(rng, nops, popen, pclose, cap=TABCAP):
    """`benign_ops` plus deliberate REJECTED operations: reads and closes of
    slots that were never opened (`h >= ntab`). Those are rejected by R1 too --
    R1 keeps the `h < ntab` bound -- so every rung folds SENT and the input is
    still a full-agreement row. It exists so the perf inputs exercise the
    rejected path, which is one of the four the law has to separate."""
    ops = benign_ops(rng, nops, popen, pclose, cap)
    for i in range(len(ops)):
        if rng.random() < 0.10:
            # `TABCAP` and NOT `cap`: a rejected op must be out of range in the
            # KERNEL, whose table holds TABCAP slots however small the
            # generator's working set is. With `rng.randrange(cap, 256)` a
            # band-S blob names slots in [cap, TABCAP) that the kernel really
            # has opened, and a rewritten CLOSE followed by a rewritten READ of
            # the same slot is R1's bug on a perf row -- `_no_uaf` caught it on
            # `sweep-s15.bin`. At `cap == TABCAP` the two spellings are the same
            # draw, so the matrix blobs are byte-identical either way.
            ops[i] = (rng.choice((CLOSE, READ)), rng.randrange(TABCAP, 256))
    return ops


# ---- the checked kernel, in Python, for the generator's own checks ----------
def kernel_result(win):
    """../model.py's checked semantics, re-implemented here so the generator can
    validate what it writes without importing the model (which imports `slb`
    against a file that does not exist yet)."""
    acc, uaf = _walk(win)
    return acc


def window_has_uaf(win):
    """True if R1 would dereference a freed record on this window."""
    return _walk(win)[1]


def _walk(win):
    if len(win) < HDR:
        return 0, False
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0, False
    tab, acc, p, uaf = [], 0, HDR, False
    for _ in range(nops):
        if len(win) - p < OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += OPSZ
        h = a
        op = c % 4
        if op == 0:
            if len(tab) < TABCAP:
                tab.append(a)
                acc = (acc * 31 + a) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        elif op == 1:
            if h < len(tab) and tab[h] is not None:
                tab[h] = None
                acc = (acc * 31 + 1) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        else:
            if h < len(tab) and tab[h] is not None:
                acc = (acc * 31 + tab[h]) & MASK
            else:
                if h < len(tab):
                    uaf = True
                acc = (acc * 31 + SENT) & MASK
    return (acc * 31 + len(tab)) & MASK, uaf


# ---- blob assembly ----------------------------------------------------------
def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`.

    p11 argued this from the shape of the return value; p12, p06, p14 and p27
    check it, which is strictly stronger and costs one pass at generation."""
    out = []
    for w in range(len(body) // stride):
        if kernel_result(body[w * stride:(w + 1) * stride]) == 0:
            out.append(f"window {w} returns 0; the driver's Lemire index has "
                       f"an absorbing state there")
    return out


def _no_uaf(body, stride):
    """**The benign invariant**: no window may make R1 read a freed record. See
    the module docstring for the two independent reasons."""
    out = []
    for w in range(len(body) // stride):
        if window_has_uaf(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} reads a CLOSED handle; R1 would execute a "
                       f"use-after-free and this is not an adversarial file")
    return out


def write(name, n_iters, stride, body, declared_len=None, check_zero=True,
          check_uaf=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    if check_uaf and stride and len(body) >= stride:
        for p in _no_uaf(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def tiled(rng, nwin, nops, popen, pclose, cap=TABCAP, mixed=True):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        gen = mixed_ops if mixed else benign_ops
        body += encode(rng, gen(rng, nops, popen, pclose, cap))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
def adv_uaf_window(rng, nstale):
    """OPEN, CLOSE, OPEN (the tcache hands the same chunk back), then READ the
    CLOSED handle -- repeated `nstale` times, each on a fresh pair of slots so
    the recycling is one-for-one. Padded with benign reads so the window has
    something for every rung to agree about up to the stale read."""
    ops, slot = [], 0
    for i in range(nstale):
        ops.append((OPEN, 0x10 + i))       # slot `slot`      -- the victim
        ops.append((CLOSE, slot))          # freed; chunk to the tcache
        ops.append((OPEN, 0xE0 + i))       # slot `slot+1`    -- SAME CHUNK
        ops.append((READ, slot))           # <-- R1 reads 0xE0+i, R1h SENT
        ops.append((READ, slot + 1))       # the newer record, read legally
        slot += 2
    return ops


def adv_noreuse_window(rng, nstale):
    """OPEN, CLOSE, READ with no OPEN in between: the chunk is still in the
    tcache and R1 reads glibc's own safe-linked `next` word."""
    ops, slot = [], 0
    for i in range(nstale):
        ops.append((OPEN, 0x20 + i))
        ops.append((CLOSE, slot))
        ops.append((READ, slot))           # <-- R1 reads tcache metadata
        slot += 1
    return ops


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a READ and a CLOSE of a slot that was never opened (`h >= ntab`): R1 keeps
#     the `h < ntab` bound, so every rung folds SENT and this is NOT the bug;
#   * a CLOSE of an already-closed slot: idempotent in every rung, and the
#     reason neither C rung can double-free. Note what is NOT here: a READ of a
#     closed slot. That is the bug, it belongs on an `adversarial-*` row, and
#     `_no_uaf` refuses to write this file if one creeps in -- it did, on the
#     first draft, and the check caught it;
#   * an OPEN past TABCAP: the capacity guard is in every rung including R1;
#   * `h == ntab` exactly and `h == ntab - 1` exactly: the boundary from both
#     sides;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
def degenerate_ops():
    ops = [(OPEN, 0x41), (OPEN, 0x42), (READ, 1), (READ, 2), (CLOSE, 5),
           (CLOSE, 0), (CLOSE, 0), (READ, 1), (READ, 200), (OPEN, 0x43)]
    ops += [(OPEN, 0x50 + i) for i in range(TABCAP)]   # past the capacity guard
    ops += [(READ, TABCAP - 1), (READ, TABCAP), (CLOSE, TABCAP + 7)]
    return ops


# `--sweep`: three bands, all skipped by `harness/check.py` and
# `harness/measure.py` on the `sweep-` prefix (`.memory/05-layout.md`: that
# prefix IS the mechanism -- a band named anything else enters the measurement
# matrix and costs a full re-measure). Appended LAST so the matrix blobs stay
# byte-identical when a band is added.
#
# Band O -- the OPERATION axis. The mix is held fixed and the op count swept, so
#           every regressor scales together: this is the band that says whether
#           the law is linear in the stream length at all.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band R -- the READ axis, and the one that matters: the op count is held FIXED
#           at 96 and the read fraction swept, so the number of allocator calls
#           falls exactly as the number of reads rises. That separates the price
#           of a READ from the price of an OPEN/CLOSE pair, which band O cannot.
SWEEP_R_FRACS = tuple(i / 20.0 for i in range(0, 17))
# Band S -- the LIVE-SLOT axis: op count and mix fixed, the table capacity the
#           generator uses swept 1..32, so the number of live records -- and
#           therefore the allocator's working set -- moves with everything else
#           held. It is the band that can falsify "a READ costs the same however
#           many records are alive".
SWEEP_S_CAPS = tuple(range(1, 33, 1))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p27 inputs ->", HERE)

    # small: one window, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.40, 0.25)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.40, 0.25)
    write("large.bin", 20000, stride, body)

    ops = degenerate_ops()
    body = encode(rng, ops)
    write("degenerate.bin", 200000, len(body), body)

    # --- adversarial: the UAF lives here and nowhere else ------------------
    ops = adv_uaf_window(rng, 6)
    body = encode(rng, ops)
    write("adversarial-uaf.bin", 200000, len(body), body, check_uaf=False)

    ops = adv_noreuse_window(rng, 4)
    body = encode(rng, ops)
    write("adversarial-noreuse.bin", 200000, len(body), body, check_uaf=False)

    ops = adv_uaf_window(rng, 12) + adv_noreuse_window(rng, 12)
    body = encode(rng, ops)
    write("adversarial-many.bin", 200000, len(body), body, check_uaf=False)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_uaf=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.40, 0.25)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_R_FRACS:
        po = (1.0 - frac) * 0.62
        pc = (1.0 - frac) * 0.38
        body, stride = tiled(rng, SWEEP_WINS, 96, po, pc)
        write(f"sweep-r{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride, body)
    for cap in SWEEP_S_CAPS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.40, 0.25, cap=cap)
        write(f"sweep-s{cap:02d}.bin", SWEEP_ITERS, stride, body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
