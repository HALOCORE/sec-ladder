#!/usr/bin/env python3
"""Generate p28's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p28-intrusive-lists/inputs/gen.py            # the matrix
    python3 patterns/p28-intrusive-lists/inputs/gen.py --sweep     # + the bands

Payload layout (../spec.md), p27's, p29's and p32's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects PUT (0), GET (1), DEL (2) or TRIM (3) -- so every byte value
is a legal opcode. `a` is the KEY on a PUT, a GET or a DEL, and `a % P28_NB` is
the bucket; TRIM ignores `a` and takes the oldest object. The safety line R1
omits, and the only thing it omits, is on the TRIM path: the nine-line splice
that leaves the victim's HASH CHAIN as well as the eviction list.

--------------------------------------------------------------------------
⚠⚠ THE BENIGN INVARIANT IS SHARPER HERE THAN ON p27 OR p29: A TRIM POISONS ITS
   VICTIM'S BUCKET **PERMANENTLY**
--------------------------------------------------------------------------
p27's rule was *"a benign window never READs a closed handle"* and p29's was
*"never USEs a stale record"* -- both are conditions on ONE later operation. Here
the freed object stays in its chain **for the rest of the window**, so *every*
later PUT, GET or DEL whose operand lands in bucket `victim->key % P28_NB`
touches it: the walk reads `n->key` out of freed storage before it can decide
anything. So the rule is a condition on a SET OF BUCKETS, not on a single op:

    once a TRIM has run, bucket `victim->key % NB` is closed for the rest of
    the window.

`benign_ops` below tracks the poisoned set and simply never emits an operand
that lands in one -- it re-rolls the key. Two independent reasons it must:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree
     with `../model.py` **and with every other cell**. R1 reading a released
     object disagrees with all of them, so such an input cannot be a perf row.
  2. TASK_055_REVIEW blocker B1, inherited from p27 and p29: what a stale read
     *returns* is a function of the optimisation level, and `build.py` builds
     both levels into one agreement set. ⚠ On p28 it happens ALSO to be stable
     run-to-run (../NOTES.md 2c), which is a different property and does not
     rescue it.

Every blob is then CHECKED rather than trusted: `write()` runs `model.py`'s own
`_sim_buggy` over every window of every benign blob and refuses to write one in
which the buggy rung touches a released object.

⚠ **`_sim_checked` and `_sim_buggy` are IMPORTED from `../model.py` rather than
re-implemented here**, which is where p27's and p29's generators differ from
this one. Their reason was that `model.py` could not be imported before the
blobs existed; that is not true of this file -- only `Model.__init__` reads a
blob, and the two window functions are free functions over bytes. Importing is
strictly better: a generator carrying its own copy of the semantics is a copy
that can drift, and the property being checked here (*"the buggy rung touches
nothing released"*) is only worth checking if it is the SAME predicate the gate
will evaluate.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A SITE-AND-SHAPE LADDER, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
p28's harm has no magnitude axis. What it has is WHERE THE DANGLING POINTER
LIVES and WHAT THE LATER OPERATION DOES WITH IT, and those two are the rows:

  `adversarial-uaf-read`   two keys in one bucket, TRIM the older, GET it. The
                           victim is the chain TAIL, so **the dangling pointer
                           is inside another heap object** -- the survivor's
                           `hn`. R1's walk reads `n->key` and then `n->val` out
                           of freed storage. ASan reports a
                           `heap-use-after-free READ`; the value R1 prints is
                           STABLE (../NOTES.md 2c).
  `adversarial-uaf-head`   ONE key in the bucket, TRIM it, GET it. The victim
                           was the chain HEAD, so **the dangling pointer is in
                           `bucket[]`** -- the other of the two sites the row
                           claims. Same walk, same ASan class, different site;
                           `controls/harm_sites.py` reads the two sites back out
                           of ASan's own report.
  `adversarial-uaf-write`  the same setup, then DEL the victim. The walk reaches
                           it, and the SPLICE then writes through `n->lp` --
                           which glibc's tcache has overwritten with its
                           safe-linked `next` word -- so in a plain build this
                           **SIGSEGVs**. The harm shape the read rows cannot
                           show: a use-after-free WRITE, landing at an address
                           the allocator chose.
  `adversarial-many`       both sites and both shapes, several times, in one
                           window, including a DEL of the SURVIVOR whose splice
                           writes the released object's `hp`.
  `adversarial-stride3`    a 3-byte window, too small for the `nops` header. The
                           driver guard `stride_w >= 4` skips the loop entirely
                           and every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p28 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p28 is **not** a pure read pattern -- `adversarial-uaf-write` is a store through
a link read out of a freed chunk. But the write rule's threshold test (p12,
TASK_041) is about a rung writing PAST THE END OF A BUFFER it was given, and no
rung here ever computes an out-of-range index: every index in this kernel is a
bucket number `a % NB` or a slot below `nmade`. What is out of range is the
object's LIFETIME. So "the guard fired" and "the unguarded rung committed UB"
remain independent events, which is what lets the adversarial rows be confined to
their own files.
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import model as m28  # noqa: E402
import slb  # noqa: E402

SEED = 28
HDR = 4
OPSZ = 2
NB = m28.NB
SLOTS = m28.SLOTS

PUT, GET, DEL, TRIM = 0, 1, 2, 3


# ---- the checked semantics, stepped, so the generator can look ahead --------
class Sim:
    """Enough of the checked kernel to answer *what would this op do?* before
    the op is committed. It is `model.py`'s dict cache, stepped: the same
    representation, so the generator and the model cannot drift about what a
    cache IS. What it adds is the POISON SET, which is a property of the BUGGY
    rung and therefore lives nowhere else."""

    def __init__(self):
        self.cache = {}
        self.order = []
        self.nmade = 0
        self.poison = set()

    def would_alloc(self, a):
        return a not in self.cache and self.nmade < SLOTS

    def step(self, op, a):
        if op == PUT:
            if a in self.cache:
                pass
            elif self.nmade < SLOTS:
                self.cache[a] = a
                self.order.append(a)
                self.nmade += 1
        elif op == DEL:
            if a in self.cache:
                del self.cache[a]
                self.order.remove(a)
        elif op == TRIM:
            if self.order:
                v = self.order.pop(0)
                del self.cache[v]
                # THE BUGGY RUNG'S CONSEQUENCE, and the only thing in this
                # class that is not the checked semantics: R1 leaves `v` in
                # bucket `v % NB` for the rest of the window.
                self.poison.add(v % NB)


def opbyte(rng, op):
    """A byte whose `% 4` is `op`, so the opcode byte is not a constant."""
    return 4 * rng.randrange(0, 64) + op


def encode(rng, ops):
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, pput, pdel, ptrim, keyhi=64):
    """A stream of `nops` operations in which **no operand ever lands in a
    poisoned bucket**, so R1 and R1h agree.

    Everything else is left to the dice: PUTs of live keys (which update in
    place), PUTs into a full cache, GETs and DELs of absent keys, and TRIMs of
    an empty cache. The allocation budget is kept clear of `SLOTS` here so the
    perf rows do not spend their tails in the SENT branch; `degenerate.bin`
    exhausts it on purpose."""
    s = Sim()
    ops = []
    while len(ops) < nops:
        r = rng.random()
        if r < ptrim and s.order and len(s.poison) < NB - 2:
            ops.append((TRIM, rng.randrange(0, 256)))
            s.step(TRIM, 0)
            continue
        # pick a key outside every poisoned bucket
        a = None
        for _ in range(64):
            cand = rng.randrange(1, keyhi)
            if cand % NB not in s.poison:
                a = cand
                break
        if a is None:
            ops.append((GET, 0) if 0 % NB not in s.poison else (TRIM, 0))
            continue
        if r < ptrim + pput:
            op = PUT
            if s.would_alloc(a) and s.nmade >= SLOTS - 4:
                op = GET          # keep the budget guard for degenerate.bin
        elif r < ptrim + pput + pdel:
            op = DEL
        else:
            op = GET
        s.step(op, a)
        ops.append((op, a))
    return ops


# ---- blob assembly ----------------------------------------------------------
def _win(body, stride, w):
    return body[w * stride:(w + 1) * stride]


def _no_zero_window(body, stride):
    """`.memory/01-ladder.md`: **window 0 must serve something.** A window
    returning 0 pins `acc` at 0 and `k = (acc * nwin) >> 64` is then 0 for ever
    -- the driver's Lemire index has an absorbing state at `acc == 0`."""
    out = []
    for w in range(len(body) // stride):
        win = _win(body, stride, w)
        if m28._sim_checked(win, 0, len(win)) == 0:
            out.append(f"window {w} returns 0; the driver's Lemire index has "
                       f"an absorbing state there")
    return out


def _no_uaf(body, stride):
    """**The benign invariant**, checked with the gate's own predicate: no
    window may make R1 touch an object it has released."""
    out = []
    for w in range(len(body) // stride):
        win = _win(body, stride, w)
        hit, sites = m28._sim_buggy(win, 0, len(win), False)
        if hit:
            out.append(f"window {w}: R1 touches a released object -- "
                       f"{sites[-1] if sites else '?'}; this is not an "
                       f"adversarial file")
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


def tiled(rng, nwin, nops, pput, pdel, ptrim, keyhi=64):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        body += encode(rng, benign_ops(rng, nops, pput, pdel, ptrim, keyhi))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
#
# Keys 5, 13 and 21 are all congruent to 5 modulo P28_NB = 8, so they share
# bucket 5 and the chain is `21 -> 13 -> 5` after three PUTs in that order
# (a PUT pushes at the chain head). The eviction list is insertion-ordered, so
# TRIM takes 5, then 13, then 21.
B5 = (5, 13, 21)


def adv_read_window():
    """The victim is the chain TAIL: the dangling pointer ends up in the
    SURVIVOR's `hn`, which is the row's headline site."""
    return [(PUT, 5), (PUT, 13), (TRIM, 0), (GET, 5)]


def adv_head_window():
    """The victim is the chain HEAD and the only member: the dangling pointer
    ends up in `bucket[5]`, which is the row's other site."""
    return [(PUT, 5), (GET, 5), (TRIM, 0), (GET, 5)]


def adv_write_window():
    """DEL the victim itself. The walk reaches it (a read), and the eviction
    splice then writes through `n->lp` -- the word glibc's tcache overwrites --
    so a plain build stores to an allocator-chosen address."""
    return [(PUT, 5), (PUT, 13), (TRIM, 0), (DEL, 5)]


def adv_many_window():
    """Both sites, both shapes, and the third write shape: a DEL of the
    SURVIVOR, whose splice writes the released object's `hp`."""
    return ([(PUT, 5), (PUT, 13), (PUT, 21), (GET, 13), (TRIM, 0), (GET, 13)]
            + [(GET, 5), (PUT, 5), (DEL, 13)]
            + [(PUT, 2), (PUT, 10), (TRIM, 0), (TRIM, 0), (GET, 2), (DEL, 10)]
            + [(PUT, 7), (TRIM, 0), (GET, 7), (PUT, 7), (GET, 7)])


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a TRIM of an EMPTY cache, and a GET and a DEL of an absent key;
#   * a duplicate PUT, which updates a live object's val in place;
#   * PUTs past P28_SLOTS, so the ALLOCATION BUDGET guard fires in every rung
#     -- 48 objects made, then 13 further PUTs rejected. It is the cache's ONLY
#     size limit and it is also the walk's fuel (../c/kernel.h);
#   * a DEL of the chain head, of a chain interior node and of a chain tail,
#     so all three arms of the two-list splice run;
#   * a DEL that empties the cache, then a TRIM against the empty cache;
#   * TRIMs LAST, and nothing after them touches a poisoned bucket, so R1 and
#     R1h still agree on this file;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
def degenerate_ops():
    ops = [(TRIM, 0), (GET, 9), (DEL, 9), (TRIM, 3)]     # the EMPTY cache
    ops += [(PUT, 5), (PUT, 13), (PUT, 21)]              # one chain, three deep
    ops += [(PUT, 13), (GET, 13)]                        # duplicate PUT
    ops += [(DEL, 21), (DEL, 5), (DEL, 13)]              # head, tail, only
    ops += [(GET, 5)]                                    # absent again
    # spend the whole allocation budget without ever calling TRIM, draining as
    # we go so that DELs of chain heads, interiors and tails all run
    k = 30
    while k < 30 + SLOTS + 8:
        keys = [k + i for i in range(8)]
        ops += [(PUT, x & 0xFF) for x in keys]
        ops += [(DEL, x & 0xFF) for x in keys[::2]]
        ops += [(DEL, x & 0xFF) for x in keys[1::2]]
        k += 8
    ops += [(PUT, 200), (PUT, 201), (GET, 200)]          # budget now exhausted
    ops += [(TRIM, 0), (TRIM, 0)]                        # empty cache again
    return ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: mix fixed, op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band K -- the KEY-SPACE axis: op count fixed at 96, the key range swept, so
#           the CHAIN LENGTH moves (fewer keys over NB buckets means longer
#           chains) with everything else held. It is the band that can falsify
#           "a walk costs the same however long the chain is".
SWEEP_K_HI = tuple(range(9, 138, 8))
# Band T -- the TRIM axis: op count fixed, the TRIM fraction swept, so the
#           number of `free` calls rises while the number of `malloc` calls
#           rises with it.
SWEEP_T_FRACS = tuple(i / 40.0 for i in range(0, 9))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p28 inputs ->", HERE)

    # small: one tile of windows, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.42, 0.20, 0.06)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.42, 0.20, 0.04)
    write("large.bin", 20000, stride, body)

    # `nops` is deliberately OVERSTATED by 9 here, so the cursor guard
    # `len - p < 2` is what stops the walk rather than the counter. Every rung
    # stops in the same place and the file is a full-agreement row.
    ops = degenerate_ops()
    body = bytearray(encode(rng, ops))
    body[0:4] = struct.pack("<I", len(ops) + 9)
    body = bytes(body)
    write("degenerate.bin", 20000, len(body), body)

    # --- adversarial: both harm shapes live here and nowhere else ----------
    for name, ops in (("adversarial-uaf-read.bin", adv_read_window()),
                      ("adversarial-uaf-head.bin", adv_head_window()),
                      ("adversarial-uaf-write.bin", adv_write_window()),
                      ("adversarial-many.bin", adv_many_window())):
        body = encode(rng, ops)
        write(name, 200000, len(body), body, check_uaf=False)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_uaf=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.42, 0.20, 0.04)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for hi in SWEEP_K_HI:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.42, 0.20, 0.04, keyhi=hi)
        write(f"sweep-k{hi:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_T_FRACS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.42, 0.20, frac)
        write(f"sweep-t{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride,
              body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
