#!/usr/bin/env python3
"""Generate p29's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p29-bst-delete/inputs/gen.py            # the matrix inputs
    python3 patterns/p29-bst-delete/inputs/gen.py --sweep     # + the sweep bands

Payload layout (../spec.md), p27's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects INSERT (0), FIND (1), REMOVE (2) or USE (3) -- so every byte
value is a legal opcode. `a` is the KEY on an INSERT, a FIND or a REMOVE, and is
ignored by a USE. The safety line R1 omits, and the only thing it omits, is on
the USE path:

    R1   if (g_saved != NULL)
    R1h  if (g_saved != NULL && live[g_slot] == 1 && tab[g_slot][0] == g_key)

--------------------------------------------------------------------------
WHY EVERY BENIGN WINDOW MUST USE ONLY A RECORD THAT IS STILL ITSELF
--------------------------------------------------------------------------
Two independent reasons, and either alone would be enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree
     with `../model.py` **and with every other cell**. R1 reading a freed or
     re-occupied record disagrees with all of them, so such an input cannot be
     a perf row.
  2. TASK_055_REVIEW blocker B1, inherited from p27: what a stale read
     *returns* is a function of the optimisation level and, for the freed half,
     of the run. `build.py` builds both levels into one agreement set.

So both bug classes live on the `adversarial-*` rows alone, whose behaviour
`check.py` **records per cell** instead of requiring agreement. This generator
runs a copy of the checked kernel over every window it emits and refuses to
write a benign blob in which any USE names a record that has been freed or
overwritten.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A BUG-CLASS LADDER, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
Neither of p29's bug classes has a magnitude axis. What they have instead is
the DEGREE OF THE VICTIM, and that is what selects the class:

  `adversarial-uaf`      FIND a leaf, REMOVE it, USE. Degree 0: the splice
                         FREES the cached record, so R1's read is a genuine
                         `heap-use-after-free`, ASan aborts, and what the read
                         returns is NOT REPRODUCIBLE -- see ../NOTES.md 7.
  `adversarial-succ`     FIND the in-order SUCCESSOR of a two-child key, then
                         REMOVE that key. The cached record is the one the
                         splice frees, so this is the use-after-free class
                         reached from the OTHER end of the algorithm.
  `adversarial-recycle`  FIND a key whose node has TWO children, REMOVE it,
                         USE. Nothing is freed: the successor's key and val are
                         copied INTO the cached record. **ASan is silent, Miri
                         is silent, and R1's wrong answer is STABLE** -- the
                         row the pattern exists for, and the one no allocation-
                         shaped mechanism can see.
  `adversarial-many`     both classes, several times each, in one window.
  `adversarial-stride3`  a 3-byte window, too small for the `nops` header. The
                         driver guard `stride_w >= 4` skips the loop entirely
                         and every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p29 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p29 is a READ pattern: R1's undefined behaviour is a LOAD through a dangling
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

SEED = 29
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
TABCAP = 32
SENT = 251

INSERT, FIND, REMOVE, USE = 0, 1, 2, 3


def val_of(k):
    return (k * 7 + 1) & 0xFF


# ---- the checked kernel, in Python, for the generator's own checks ----------
# Re-implemented here rather than imported from ../model.py, which imports `slb`
# against a file that does not exist yet. p27's gen.py duplicates its walk for
# the same reason. This is the FUNCTIONAL formulation, the same one
# ../model.py's simulation uses.
class Rec:
    __slots__ = ("key", "val")

    def __init__(self, k, v):
        self.key, self.val = k, v


def _ins(t, k, st):
    if t is None:
        if st[0] < TABCAP:
            st[0] += 1
            st[1] = "new"
            return (Rec(k, val_of(k)), None, None)
        st[1] = "full"
        return None
    rec, l, r = t
    if k < rec.key:
        return (rec, _ins(l, k, st), r)
    if k > rec.key:
        return (rec, l, _ins(r, k, st))
    rec.val = val_of(k)
    st[1] = "dup"
    return t


def _find(t, k):
    if t is None:
        return None
    rec, l, r = t
    if k < rec.key:
        return _find(l, k)
    if k > rec.key:
        return _find(r, k)
    return rec


def _min_rec(t):
    rec, l, _r = t
    return rec if l is None else _min_rec(l)


def _del_min(t):
    rec, l, r = t
    if l is None:
        return r
    return (rec, _del_min(l), r)


def _rem(t, k, st):
    if t is None:
        return None
    rec, l, r = t
    if k < rec.key:
        return (rec, _rem(l, k, st), r)
    if k > rec.key:
        return (rec, l, _rem(r, k, st))
    st[2] = True
    if l is None:
        return r
    if r is None:
        return l
    s = _min_rec(r)
    rec.key, rec.val = s.key, s.val
    return (rec, l, _del_min(r))


def _reach(t, rec):
    if t is None:
        return False
    n, l, r = t
    return n is rec or _reach(l, rec) or _reach(r, rec)


class Sim:
    """The checked semantics, stepped one op at a time so the generator can ask
    what an op WOULD do before committing to it."""

    def __init__(self):
        self.root = None
        self.st = [0, "", False]
        self.saved = None
        self.skey = 0
        self.acc = 0
        self.stale = False        # a USE whose record is no longer itself
        self.freed = False        # a USE whose record has been FREED

    def step(self, op, a):
        if op == INSERT:
            self.st[1] = ""
            self.root = _ins(self.root, a, self.st)
            self.acc = (self.acc * 31
                        + (SENT if self.st[1] == "full" else a)) & MASK
        elif op == FIND:
            got = _find(self.root, a)
            if got is not None:
                self.saved, self.skey = got, a
                self.acc = (self.acc * 31 + 1) & MASK
            else:
                self.acc = (self.acc * 31 + SENT) & MASK
        elif op == REMOVE:
            self.st[2] = False
            self.root = _rem(self.root, a, self.st)
            self.acc = (self.acc * 31 + (2 if self.st[2] else SENT)) & MASK
        else:
            here = self.saved is not None and _reach(self.root, self.saved)
            if self.saved is not None and not here:
                self.freed = True
            if self.saved is not None and not (here
                                               and self.saved.key == self.skey):
                self.stale = True
            if here and self.saved.key == self.skey:
                self.acc = (self.acc * 31 + self.saved.val) & MASK
            else:
                self.acc = (self.acc * 31 + SENT) & MASK

    def use_is_clean(self):
        """Would a USE right now name a record that is still itself?"""
        if self.saved is None:
            return True          # folds SENT in every rung -- defined and equal
        return _reach(self.root, self.saved) and self.saved.key == self.skey

    def result(self):
        return (self.acc * 31 + self.st[0]) & MASK


def _walk(win):
    """(result, R1_reads_a_freed_record, R1_disagrees_at_all)."""
    if len(win) < HDR:
        return 0, False, False
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0, False, False
    s = Sim()
    p = HDR
    for _ in range(nops):
        if len(win) - p < OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += OPSZ
        s.step(c % 4, a)
    return s.result(), s.freed, s.stale


def kernel_result(win):
    return _walk(win)[0]


def window_is_stale(win):
    return _walk(win)[2]


# ---- op-stream construction -------------------------------------------------
def opbyte(rng, op):
    """A byte whose `% 4` is `op`, so the opcode byte is not a constant."""
    return 4 * rng.randrange(0, 64) + op


def encode(rng, ops):
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, pins, prem, keyhi=200):
    """A stream of `nops` operations in which **every USE names a record that is
    still in the tree under the key it was found by**. The generator carries the
    checked semantics and simply does not emit a USE that would be stale: it
    emits a fresh FIND instead, which is a defined, agreeing operation in every
    rung. Everything else -- inserts past TABCAP, duplicate inserts, finds and
    removes of absent keys, removes of every degree -- is left to the dice."""
    s = Sim()
    ops = []
    while len(ops) < nops:
        r = rng.random()
        if r < pins or s.st[0] == 0:
            op, a = INSERT, rng.randrange(1, keyhi)
        elif r < pins + prem:
            op, a = REMOVE, rng.randrange(1, keyhi)
        elif r < pins + prem + 0.20:
            op, a = FIND, rng.randrange(1, keyhi)
        else:
            op, a = USE, rng.randrange(0, 256)
            if not s.use_is_clean():
                op, a = FIND, rng.randrange(1, keyhi)
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
    """**The benign invariant**: no window may make R1 read a record that is no
    longer the one FIND returned -- freed OR re-occupied. See the module
    docstring for the two independent reasons."""
    out = []
    for w in range(len(body) // stride):
        if window_is_stale(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} USEs a stale record; R1 would diverge and "
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
    print(f"  {name:30s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def tiled(rng, nwin, nops, pins, prem, keyhi=200):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        body += encode(rng, benign_ops(rng, nops, pins, prem, keyhi))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
#
# The shared prefix builds
#
#         50
#       /    \
#     25      75
#    /  \    /  \
#  10    30 60    90
#
# so 25 and 75 have two children, 10/30/60/90 are leaves, and 90 is 75's
# in-order successor while 30 is 25's.
PREFIX = [(INSERT, 50), (INSERT, 25), (INSERT, 75),
          (INSERT, 10), (INSERT, 30), (INSERT, 60), (INSERT, 90)]


def adv_uaf_window(n):
    """FIND a leaf, REMOVE it, USE. Degree 0: the record is FREED."""
    ops = list(PREFIX)
    for leaf in (10, 30, 60, 90)[:n]:
        ops += [(FIND, leaf), (REMOVE, leaf), (USE, 0)]
    return ops


def adv_succ_window(n):
    """FIND the in-order SUCCESSOR, then REMOVE the two-child key. The cached
    record is the one the splice frees -- the use-after-free class reached from
    the other end of the algorithm."""
    ops = list(PREFIX)
    for key, succ in ((75, 90), (25, 30))[:n]:
        ops += [(FIND, succ), (REMOVE, key), (USE, 0)]
    return ops


def adv_recycle_window(n):
    """FIND a key whose node has TWO children, REMOVE it, USE. Nothing is
    freed. ASan is silent and R1's wrong answer is stable."""
    ops = list(PREFIX)
    for key in (75, 25)[:n]:
        ops += [(FIND, key), (REMOVE, key), (USE, 0), (USE, 0)]
    return ops


def adv_many_window():
    return (adv_recycle_window(2) + [(INSERT, 40), (INSERT, 45), (INSERT, 42)]
            + [(FIND, 42), (REMOVE, 42), (USE, 0)]
            + [(FIND, 45), (REMOVE, 40), (USE, 0)]
            + [(FIND, 60), (REMOVE, 60), (USE, 0), (USE, 0)]
            + [(FIND, 50), (REMOVE, 50), (USE, 0), (USE, 0)])


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a USE before any FIND has succeeded: `g_saved` is NULL, every rung SENT;
#   * a FIND and a REMOVE of a key that is not in the tree;
#   * a duplicate INSERT, which updates a live record's val in place;
#   * INSERTs past TABCAP, so the capacity guard fires in every rung;
#   * a REMOVE of the ROOT, of a two-child node, of a one-child node and of a
#     leaf -- all four degrees, none of them cached;
#   * a REMOVE that empties the tree, then a USE and a FIND against an empty
#     tree;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
#
#   Note what is NOT here: a USE of a stale record. That is the bug, it belongs
#   on the adversarial rows, and `_no_stale` refuses to write this file if one
#   creeps in.
def degenerate_ops():
    ops = [(USE, 0), (FIND, 77), (USE, 0), (REMOVE, 77)]   # the EMPTY tree
    ops += PREFIX
    ops += [(INSERT, 50), (FIND, 10), (USE, 0)]            # duplicate INSERT
    ops += [(FIND, 60), (USE, 0), (REMOVE, 90), (USE, 0)]  # a LEAF, not cached
    ops += [(REMOVE, 25), (USE, 0)]                        # TWO children, not
    #                                                        cached: the splice
    #                                                        runs and the cached
    #                                                        record is somebody
    #                                                        else's
    ops += [(FIND, 50), (USE, 0), (REMOVE, 50), (FIND, 75), (USE, 0)]
    #                                          ^ the ROOT, two children, and the
    #                                            cache is refreshed AFTER it
    ops += [(INSERT, 5 * i + 100) for i in range(TABCAP)]  # past the capacity
    ops += [(FIND, 100), (USE, 0), (REMOVE, 100), (FIND, 105), (USE, 0)]
    ops += [(REMOVE, 105), (REMOVE, 110), (FIND, 115), (USE, 0)]
    ops += [(FIND, 201), (REMOVE, 202), (USE, 0)]          # absent key, twice
    return ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: mix fixed, op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band K -- the KEY-SPACE axis: op count fixed at 96, the key range swept, so
#           the tree's DEPTH and the number of two-child nodes move together
#           with everything else held. It is the band that can falsify "a walk
#           costs the same however deep the tree is".
SWEEP_K_HI = tuple(range(4, 133, 8))
# Band R -- the REMOVE axis: op count fixed, the remove fraction swept, so the
#           number of allocator calls falls as the number of removes rises.
SWEEP_R_FRACS = tuple(i / 20.0 for i in range(0, 13))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p29 inputs ->", HERE)

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
    body = encode(rng, adv_uaf_window(4))
    write("adversarial-uaf.bin", 200000, len(body), body, check_stale=False)

    body = encode(rng, adv_succ_window(2))
    write("adversarial-succ.bin", 200000, len(body), body, check_stale=False)

    body = encode(rng, adv_recycle_window(2))
    write("adversarial-recycle.bin", 200000, len(body), body, check_stale=False)

    body = encode(rng, adv_many_window())
    write("adversarial-many.bin", 200000, len(body), body, check_stale=False)

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
    for hi in SWEEP_K_HI:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.40, 0.22, keyhi=hi + 2)
        write(f"sweep-k{hi:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_R_FRACS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.62 - frac, frac)
        write(f"sweep-r{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride,
              body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
