#!/usr/bin/env python3
"""Generate p32's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p32-free-list-pool/inputs/gen.py            # the matrix inputs
    python3 patterns/p32-free-list-pool/inputs/gen.py --sweep     # + the sweep bands

Payload layout (../spec.md), p27's and p29's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects ALLOC (0), FREE (1), READ (2) or WRITE (3) -- so every byte
value is a legal opcode. `a % NREG` selects the HANDLE REGISTER, and `a` itself
is the payload an ALLOC stores and a WRITE writes. **The file never names a slot
and never names a generation**: ALLOC issues the handle, a register holds it, and
the file says which register to use. That is what makes the generation
unforgeable and it is `p29`'s corrected sentence -- *a file cannot name a
pointer, but it can name an operation that saves one* -- applied to a pool.
`../c/kernel.h` and `../NOTES.md` 1b argue it and measure the alternative.

The safety line R1 omits, and the only thing it omits, is `gen[h] != g` at the
three handle-consuming sites:

    R1   if (h == NIL) { ... } else { ... }
    R1h  if (h == NIL) { ... } else if (gen[h] != g) { ... } else { ... }

--------------------------------------------------------------------------
WHY EVERY BENIGN WINDOW MUST USE ONLY A HANDLE THAT IS STILL CURRENT
--------------------------------------------------------------------------
Two independent reasons, and either alone would be enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree
     with `../model.py` **and with every other cell**. R1 consuming a stale
     handle disagrees with all of them, so such an input cannot be a perf row.
  2. TASK_055_REVIEW blocker B1, inherited from p27: the two rungs' answers must
     not depend on the optimisation level, and `build.py` builds both levels into
     one agreement set.

⚠ **What is NOT a reason here, and it is worth saying because it is p27's and
p29's first reason**: on p32 what a stale use returns IS reproducible. The pool
is a local array with no heap addresses in it, so R1's checksum is one distinct
value in twenty runs on every adversarial input (../NOTES.md 2d). p32's
adversarial rows are excluded from the agreement set because they DISAGREE, not
because they are unstable -- which is a property neither built temporal row has.

So both bug classes live on the `adversarial-*` rows alone, whose behaviour
`check.py` **records per cell** instead of requiring agreement. This generator
runs a copy of the checked kernel over every window it emits and refuses to
write a benign blob in which any FREE, READ or WRITE names a stale handle.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A BUG-CLASS LADDER, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
  `adversarial-stale-read`  ALLOC r0, ALLOC r1, FREE r0, READ r0. The block is
                            on the free list and nobody owns it, so R1 reads
                            bytes that are STILL CORRECT -- the arena never
                            scrubs them. **The harm here is only that R1h
                            refuses and R1 does not**; in the `malloc` arm of
                            `../controls/storage_arms.py` this same input is an
                            ASan `heap-use-after-free` and its value is not
                            reproducible. The clearest single row for "the
                            storage decides what the detector sees".
  `adversarial-recycle`     FREE r0, then ALLOC r2, which RECYCLES slot 0, then
                            READ r0. R1 returns the NEW OCCUPANT's payload.
                            ⚠⚠ **Bit-identical and silent in BOTH storage arms**
                            -- the use-after-recycle harm is storage-independent
                            and invisible to every allocation-shaped instrument.
                            `p33`'s arm of this row.
  `adversarial-doublefree`  FREE r0 twice. `nx[h] = freehead` with
                            `freehead == h` SELF-LOOPS the free list, so the two
                            following ALLOCs return the SAME slot. `p32`'s arm.
  `adversarial-alias`       the same self-loop, then a WRITE through one of the
                            two aliased handles and a READ through the other, so
                            the ALIASING is in the checksum rather than inferred.
                            ⚠ **This harm has no analogue in `p27` or `p29`.**
  `adversarial-many`        all four, in one window, with the pool driven to
                            exhaustion in between.
  `adversarial-stride3`     a 3-byte window, too small for the `nops` header. The
                            driver guard `stride_w >= 4` skips the loop entirely
                            and every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p32 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p32 has a WRITE opcode, and it is not a write out of bounds: `h` is `NIL` or a
real slot in both rungs, so `pool[h * BLK + 1]` is in range in every run. The
write rule's threshold test (p12, TASK_041) is about a store that leaves the
object, and no store here can. "The guard fired" and "the unguarded rung
committed UB" are not merely independent events on p32 -- **the second one never
happens**, which is the row's detector-coverage result (../model.py's
`sanitizer_expect` derives it rather than declaring it).
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

SEED = 32
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
SLOTS = 8
BLK = 4
NREG = 8
SENT = 251

ALLOC, FREE, READ, WRITE = 0, 1, 2, 3


def val_of(a):
    return (a * 7 + 1) & 0xFF


def written(a):
    return (a * 13 + 3) & 0xFF


# ---- the checked kernel, in Python, for the generator's own checks ----------
# Re-implemented here rather than imported from ../model.py, which imports `slb`
# against a file that does not exist yet. p27's and p29's gen.py duplicate their
# walk for the same reason. This is the OBJECT-IDENTITY formulation, the same
# one ../model.py's simulation uses, and it carries NO generation counter.
class Block:
    __slots__ = ("slot",)

    def __init__(self, slot):
        self.slot = slot


class Sim:
    """The checked semantics, stepped one op at a time so the generator can ask
    what an op WOULD do before committing to it."""

    def __init__(self):
        self.mem = [[0] * BLK for _ in range(SLOTS)]
        self.live = [None] * SLOTS
        self.succ = {j: (j + 1 if j + 1 < SLOTS else None) for j in range(SLOTS)}
        self.head = 0
        self.rel = [0] * SLOTS
        self.reg = [None] * NREG
        self.nalloc = 0
        self.acc = 0
        self.stale = False        # would R1 consume a handle that is not current?

    def use_is_clean(self, r):
        """Would a FREE/READ/WRITE on register `r` name a handle that is still
        current? An EMPTY register is clean: it folds SENT in both rungs."""
        b = self.reg[r]
        return b is None or self.live[b.slot] is b

    def list_is_simple(self):
        """Walk the successor map with a VISITED SET. No rung computes this."""
        seen, t = set(), self.head
        while t is not None:
            if t in seen:
                return False
            seen.add(t)
            t = self.succ[t]
        return True

    def step(self, op, a):
        r = a % NREG
        if op == ALLOC:
            if self.head is None:
                self.acc = (self.acc * 31 + SENT) & MASK
                return
            s = self.head
            self.head = self.succ[s]
            self.mem[s][0] = a
            self.mem[s][1] = val_of(a)
            b = Block(s)
            self.live[s] = b
            self.reg[r] = b
            self.nalloc += 1
            self.acc = (self.acc * 31 + s + 8 * self.rel[s]) & MASK
            return
        b = self.reg[r]
        if b is None:
            self.acc = (self.acc * 31 + SENT) & MASK
            return
        if self.live[b.slot] is not b:
            self.stale = True                 # what R1 would do, recorded
            self.acc = (self.acc * 31 + SENT) & MASK
            return
        s = b.slot
        if op == FREE:
            self.live[s] = None
            self.rel[s] += 1
            self.succ[s] = self.head
            self.head = s
            self.acc = (self.acc * 31 + 1) & MASK
        elif op == READ:
            self.acc = (self.acc * 31 + self.mem[s][1]) & MASK
        else:
            self.mem[s][1] = written(a)
            self.acc = (self.acc * 31 + 3) & MASK

    def result(self):
        return (self.acc * 31 + self.nalloc) & MASK


def _walk(win):
    """(result, R1_would_use_a_stale_handle)."""
    if len(win) < HDR:
        return 0, False
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0, False
    s = Sim()
    p = HDR
    for _ in range(nops):
        if len(win) - p < OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += OPSZ
        s.step(c % 4, a)
    return s.result(), s.stale


def kernel_result(win):
    return _walk(win)[0]


def window_is_stale(win):
    return _walk(win)[1]


# ---- op-stream construction -------------------------------------------------
def opbyte(rng, op):
    """A byte whose `% 4` is `op`, so the opcode byte is not a constant."""
    return 4 * rng.randrange(0, 64) + op


def operand(rng, r):
    """A byte whose `% NREG` is `r`, so the payload varies while the register
    does not."""
    return (8 * rng.randrange(0, 32) + r) & 0xFF


def oper(reg, pay):
    """A DETERMINISTIC operand: register `reg`, payload varied by `pay`."""
    return (8 * pay + reg) & 0xFF


def encode(rng, ops):
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, palloc, pfree):
    """A stream of `nops` operations in which **every FREE, READ and WRITE names
    a handle register that is still current** (or is empty, which folds SENT in
    every rung). The generator carries the checked semantics and simply does not
    emit an op that would be stale: it emits an ALLOC into that register
    instead, which is defined and agreeing in every rung and restores the
    register. Everything else -- allocating from an EXHAUSTED pool, using an
    empty register, recycling a slot repeatedly -- is left to the dice."""
    s = Sim()
    ops = []
    while len(ops) < nops:
        x = rng.random()
        r = rng.randrange(0, NREG)
        if x < palloc:
            op = ALLOC
        elif x < palloc + pfree:
            op = FREE
        elif x < palloc + pfree + 0.20:
            op = READ
        else:
            op = WRITE
        if op != ALLOC and not s.use_is_clean(r):
            op = ALLOC
        a = operand(rng, r)
        s.step(op, a)
        ops.append((op, a))
    return ops


# ---- blob assembly ----------------------------------------------------------
def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`."""
    out = []
    for w in range(len(body) // stride):
        if kernel_result(body[w * stride:(w + 1) * stride]) == 0:
            out.append(f"window {w} returns 0; the driver's Lemire index has "
                       f"an absorbing state there")
    return out


def _no_stale(body, stride):
    """**The benign invariant**: no window may make R1 consume a handle whose
    block is no longer the one ALLOC issued it for. See the module docstring for
    the two independent reasons."""
    out = []
    for w in range(len(body) // stride):
        if window_is_stale(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} uses a stale handle; R1 would diverge and "
                       f"this is not an adversarial file")
    return out


def write(name, n_iters, stride, body, declared_len=None, check_zero=True,
          check_stale=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    if check_stale and stride and len(body) >= stride:
        for p in _no_stale(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:32s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def tiled(rng, nwin, nops, palloc, pfree):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        body += encode(rng, benign_ops(rng, nops, palloc, pfree))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
def adv_stale_read_window():
    """FREE r0 and then READ r0. In the shipped pool storage the bytes are
    still the ones ALLOC wrote, so R1's answer is *correct data read without
    permission*; only R1h's refusal separates the rungs. Under `malloc` storage
    the same input is a `heap-use-after-free`."""
    return [(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)),
            (FREE, oper(0, 3)), (READ, oper(0, 4))]


def adv_recycle_window():
    """FREE r0, ALLOC r2 -- which pops slot 0 straight back off the LIFO list --
    then READ r0: the NEW OCCUPANT's payload. Storage-independent and silent
    everywhere."""
    return [(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)), (FREE, oper(0, 3)),
            (ALLOC, oper(2, 9)), (READ, oper(0, 4)), (READ, oper(2, 5))]


def adv_doublefree_window():
    """FREE r0 twice: the second push writes `nx[h] = freehead` with
    `freehead == h`, so the list SELF-LOOPS and every later ALLOC returns the
    same slot."""
    return [(ALLOC, oper(0, 1)), (ALLOC, oper(1, 2)), (FREE, oper(0, 3)),
            (FREE, oper(0, 4)), (ALLOC, oper(2, 5)), (ALLOC, oper(3, 6)),
            (READ, oper(2, 7)), (READ, oper(3, 8))]


def adv_alias_window():
    """The self-loop, and then the ALIASING made visible: r2 and r3 name ONE
    block, so a WRITE through r2 is READ back through r3 and vice versa. **No
    built row can produce this harm.**"""
    return [(ALLOC, oper(0, 1)), (FREE, oper(0, 2)), (FREE, oper(0, 3)),
            (ALLOC, oper(2, 5)), (ALLOC, oper(3, 6)), (WRITE, oper(2, 7)),
            (READ, oper(3, 8)), (WRITE, oper(3, 9)), (READ, oper(2, 10))]


def adv_many_window():
    return (adv_stale_read_window() + adv_recycle_window()
            + adv_doublefree_window() + adv_alias_window()
            # drain the pool, so an ALLOC also folds SENT in this window
            + [(ALLOC, oper(k % NREG, 20 + k)) for k in range(12)]
            + [(READ, oper(4, 30)), (WRITE, oper(5, 31)), (READ, oper(5, 32))])


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a FREE, a READ and a WRITE through a register that never held a handle:
#     `h == NIL`, and every rung folds SENT;
#   * an ALLOC from an EXHAUSTED pool, so the `freehead == NIL` arm fires;
#   * a full cycle -- allocate every slot, free every slot, allocate them all
#     again -- so every slot's generation is bumped and every one is recycled;
#   * two registers ALLOCated to the same slot ACROSS a free, used in the right
#     order, so the recycle happens and nothing is stale when it is used;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
#
#   Note what is NOT here: a use of a stale handle. That is the bug, it belongs
#   on the adversarial rows, and `_no_stale` refuses to write this file if one
#   creeps in.
def degenerate_ops():
    ops = [(FREE, oper(0, 1)), (READ, oper(1, 2)), (WRITE, oper(2, 3))]
    ops += [(ALLOC, oper(k, 10 + k)) for k in range(NREG)]      # fill the pool
    ops += [(ALLOC, oper(0, 40))]                               # EXHAUSTED
    ops += [(READ, oper(3, 4)), (WRITE, oper(3, 5)), (READ, oper(3, 6))]
    ops += [(FREE, oper(k, 20 + k)) for k in range(NREG)]       # drain it
    ops += [(ALLOC, oper(k, 30 + k)) for k in range(NREG)]      # recycle it all
    ops += [(READ, oper(k, 50 + k)) for k in range(NREG)]
    ops += [(FREE, oper(2, 60)), (ALLOC, oper(2, 61)), (READ, oper(2, 62))]
    ops += [(FREE, oper(2, 63)), (ALLOC, oper(4, 64)), (READ, oper(4, 65))]
    #                                    ^ slot recycled INTO A DIFFERENT
    #                                      register, and r2 is never used again
    return ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: mix fixed, op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band F -- the FREE axis: op count fixed, the free fraction swept, so the
#           number of RECYCLES rises while the number of operations does not.
#           It is the band that can falsify "recycling costs the same as not".
SWEEP_F_FRACS = tuple(i / 20.0 for i in range(0, 13))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p32 inputs ->", HERE)

    # small: one tile of windows, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.40, 0.22)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.40, 0.22)
    write("large.bin", 20000, stride, body)

    # `nops` is deliberately OVERSTATED by 9 here, so the cursor guard
    # `len - p < 2` is what stops the walk rather than the counter. Every rung
    # stops in the same place and the file is a full-agreement row.
    ops = degenerate_ops()
    body = bytearray(encode(rng, ops))
    body[0:4] = struct.pack("<I", len(ops) + 9)
    body = bytes(body)
    write("degenerate.bin", 200000, len(body), body)

    # --- adversarial: the two bug classes live here and nowhere else -------
    for name, win in (("stale-read", adv_stale_read_window()),
                      ("recycle", adv_recycle_window()),
                      ("doublefree", adv_doublefree_window()),
                      ("alias", adv_alias_window()),
                      ("many", adv_many_window())):
        body = encode(rng, win)
        write(f"adversarial-{name}.bin", 200000, len(body), body,
              check_stale=False)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_stale=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.40, 0.22)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_F_FRACS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.62 - frac, frac)
        write(f"sweep-f{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride,
              body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
