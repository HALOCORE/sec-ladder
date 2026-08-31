#!/usr/bin/env python3
"""Generate p34's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p34-refcount-stack/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p34-refcount-stack/inputs/gen.py --sweep    # + the sweep bands

Payload layout (../spec.md), p06's/p11's/p16's/p17's/p05's/p07's/p03's/p12's/
p14's/p27's/p29's/p32's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects NEW (0), DUP (1), POP (2) or READ (3) -- so every byte value
is a legal opcode. `a` is the payload seed on a NEW and the reference index on a
READ; DUP and POP take the top of the stack and ignore `a`.

--------------------------------------------------------------------------
⚠⚠ THE HARD CONSTRAINT: NO MATRIX INPUT MAY CONTAIN A `DUP` OP
--------------------------------------------------------------------------
`../c/kernel.h` proves in two lines that a `DUP` executed by R1 ALWAYS ends in a
use-after-free: the safety line is the only increment in the kernel, so in R1
every object's `rc` is permanently 1, and the two releases that must follow a DUP
go `1 -> 0` (*free*) and then `0 -> underflow`, reading `o->rc` out of a freed
block. Two consequences, and either alone would be enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree with
     `../model.py` **and with every other cell**. A window with a DUP makes R1
     disagree, so such a window cannot be a perf row.
  2. The safety line's benign cost gradient is therefore `0.00` BY
     CONSTRUCTION -- a statement about the pattern rather than a measurement
     outcome -- and that claim is only worth making if the property is CHECKED.

So this generator emits NEW/POP/READ only on every matrix blob and refuses to
write one that contains a DUP, and `../model.py::no_dup_problems` re-derives the
same property from the SHIPPED blob on every gate invocation.
`../controls/no_dup.py` censuses every file in this directory.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A DETECTOR EXPERIMENT, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
A use-after-free has no magnitude axis. What p34 has instead is a pair of bug
classes SEPARATED BY WHICH INSTRUMENT SEES THEM, and the rows are one per class:

  `adversarial-blind`     NEW DUP POP POP. The second release reads `o->rc` out
                          of the freed block. **The two rungs' checksums are
                          BIT-IDENTICAL** -- the release path folds a constant --
                          so ASan is the ONLY discriminator. This is the row a
                          checksum-only gate misses entirely, and it is p34's
                          most interesting evidence.
  `adversarial-blindread` NEW DUP POP READ. The stale entry reads `o->data[0]`
                          out of the freed block. **Also bit-identical**,
                          because `data` starts at offset 16 and glibc's tcache
                          words land on `rc` and `len` (../c/kernel.c's disclosed
                          layout note). ASan is again the only discriminator.
  `adversarial-recycle`   NEW DUP POP NEW READ. The second NEW RECYCLES the
                          freed block, so the stale entry reads the NEW
                          OCCUPANT's payload and **the checksum DIVERGES**. This
                          is the gateable one.
  `adversarial-many`      36 stale uses of all three shapes in one window, so a
                          rung that survives one has to survive 36 and ASan's
                          first report is not the only one.
  `adversarial-stride3`   a 3-byte window, too small for the `nops` header. The
                          driver guard `stride_w >= 4` skips the loop entirely
                          and every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p34 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p34's release path WRITES `o->rc - 1` back into the object, and through a stale
reference that write lands in a freed block -- so unlike p27, p34 is not a pure
READ pattern. The write is to a location the kernel's own allocation once owned
and never outside any object, so no rung ever stores out of BOUNDS; the write
rule's spatial threshold test (p12, TASK_041) still does not reach it. What the
write does reach is glibc's tcache `next` word, and ../NOTES.md 2 measures the
consequence at every iteration count this pattern ships: none.
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

SEED = 34
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
CAP = 16
DLEN = 8
SENT = 251

NEW, DUP, POP, READ = 0, 1, 2, 3


# ---- op-stream construction -------------------------------------------------
def opbyte(rng, op):
    """A byte whose `% 4` is `op`. The high six bits are random, so an opcode
    byte is never a constant and a rung that switched on the whole byte would be
    caught by the checksum."""
    return 4 * rng.randrange(0, 64) + op


def encode(rng, ops):
    """[(op, operand)] -> the window body, with an honest `nops` header."""
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, pnew, ppop, cap=CAP):
    """A stream of `nops` operations drawn from NEW / POP / READ only.

    ⚠ **`DUP` is not in the alphabet this function can emit**, which is the
    module docstring's hard constraint expressed as a fact about the generator
    rather than as a filter over its output. `write()` re-checks the emitted
    bytes anyway, because a filter that cannot fire proves nothing.

    `cap` is the generator's working set, which the sweep bands move; the
    KERNEL's capacity is always `CAP`, and the two are kept in step so a stream
    never names a reference the kernel does not have."""
    ops, depth = [], 0
    while len(ops) < nops:
        r = rng.random()
        if r < pnew or depth == 0:
            if depth < cap and depth < CAP:
                ops.append((NEW, rng.randrange(1, 256)))
                depth += 1
                continue
            # The working set is full. A full-stack NEW folds SENT in every
            # rung, so it is a defined, agreeing operation -- but when
            # `cap < CAP` the KERNEL accepts it and pushes a reference this
            # function is not tracking, so the two depths must be kept in step.
            ops.append((NEW, rng.randrange(1, 256)))
            if depth < CAP:
                depth += 1
            continue
        if r < pnew + ppop:
            ops.append((POP, rng.randrange(0, 256)))
            depth -= 1
        else:
            ops.append((READ, rng.randrange(0, 256)))
    return ops


def mixed_ops(rng, nops, pnew, ppop, cap=CAP):
    """`benign_ops` plus deliberate REJECTED operations: a POP or a READ issued
    when the stack is empty folds SENT in every rung, so the input is still a
    full-agreement row. It exists so the perf inputs exercise the rejected path,
    which is one of the four the law has to separate.

    The rejection is produced by draining the stack rather than by naming an
    out-of-range reference, because p34 has no out-of-range reference to name:
    READ's index is `a % ntop`, so EVERY operand byte names a live entry."""
    ops = benign_ops(rng, nops, pnew, ppop, cap)
    # Prefix a drained pair: the stack starts empty, so op 0 as a POP and op 1
    # as a READ both fold SENT in every rung.
    return [(POP, 0), (READ, 7)] + ops[:max(0, nops - 2)]


# ---- the checked kernel, in Python, for the generator's own checks ----------
def _walk(win):
    """`(result, executes_a_DUP)` for one window, under the CHECKED semantics.

    ../model.py's semantics re-implemented here so the generator can validate
    what it writes without importing the model (which imports `slb` against a
    file that does not exist yet). ⚠ It carries **no reference count**: under the
    checked semantics an object is alive exactly while some stack entry names it,
    which is the same shape ../model.py's `rc_fold` uses and ../verus.rs's `run`
    proves."""
    if len(win) < HDR:
        return 0, False
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0, False
    stk, vals, acc, p, sawdup = [], [], 0, HDR, False
    for _ in range(nops):
        if len(win) - p < OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += OPSZ
        op = c % 4
        if op == NEW:
            if len(stk) < CAP:
                stk.append(len(vals))
                vals.append((a * 7 + 1) & 0xFF)
                acc = (acc * 31 + a) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        elif op == DUP:
            sawdup = True
            if 0 < len(stk) < CAP:
                stk.append(stk[-1])
                acc = (acc * 31 + 1) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        elif op == POP:
            if stk:
                stk.pop()
                acc = (acc * 31 + 2) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        else:
            if stk:
                acc = (acc * 31 + vals[stk[a % len(stk)]]) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
    return (acc * 31 + len(vals)) & MASK, sawdup


def kernel_result(win):
    return _walk(win)[0]


def window_has_dup(win):
    return _walk(win)[1]


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


def _no_dup(body, stride):
    """**THE BENIGN INVARIANT, and it is p34's headline.** No window of a matrix
    blob may execute a `DUP`. See the module docstring for the two independent
    reasons, and ../c/kernel.h for the two-line proof that a DUP in R1 always
    ends in a use-after-free."""
    out = []
    for w in range(len(body) // stride):
        if window_has_dup(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} executes a DUP; R1 would free an object a "
                       f"live stack entry still names, and this is not an "
                       f"adversarial file")
    return out


def write(name, n_iters, stride, body, declared_len=None, check_zero=True,
          check_dup=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    if check_dup and stride and len(body) >= stride:
        for p in _no_dup(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:30s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def tiled(rng, nwin, nops, pnew, ppop, cap=CAP, mixed=True):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        gen = mixed_ops if mixed else benign_ops
        body += encode(rng, gen(rng, nops, pnew, ppop, cap))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
def adv_blind_window(n):
    """`NEW DUP POP POP`, repeated. The second release reads `o->rc` out of the
    freed block; the release path folds the constant 2 either way, so **the two
    rungs' checksums agree bit for bit and ASan is the only discriminator**."""
    ops = []
    for i in range(n):
        ops += [(NEW, 0x11 + i), (DUP, 0), (POP, 0), (POP, 0)]
    return ops


def adv_blindread_window(n):
    """`NEW DUP POP READ`, then a POP to drain. The stale entry reads
    `o->data[0]` out of the freed block, and `data` starts at offset 16 -- clear
    of glibc's tcache `next`/`key` words -- so the byte is still the RIGHT one
    and **the checksums agree bit for bit** here too."""
    ops = []
    for i in range(n):
        ops += [(NEW, 0x21 + i), (DUP, 0), (POP, 0), (READ, 0), (POP, 0)]
    return ops


def adv_recycle_window(n):
    """`NEW DUP POP NEW READ`, then two POPs to drain. glibc's tcache is LIFO, so
    the second NEW gets the freed block back and writes its own payload into it;
    R1's stale READ then returns **another object's byte under this reference**
    and **the checksum DIVERGES**. This is the gateable row."""
    ops = []
    for i in range(n):
        ops += [(NEW, 0x31 + i), (DUP, 0), (POP, 0), (NEW, 0xC1 + i),
                (READ, 0), (POP, 0), (POP, 0)]
    return ops


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a POP and a READ with an EMPTY stack: both fold SENT in every rung, and
#     this is NOT the bug;
#   * a NEW past CAP: the capacity guard is in every rung including R1;
#   * a READ whose operand exceeds the stack depth: the index is `a % ntop`, so
#     every operand names a live entry and nothing is rejected for being
#     malformed -- the boundary from both sides, `a == ntop` and `a == ntop - 1`;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
#
# ⚠ What is NOT here: a DUP. That is the bug, it belongs on an `adversarial-*`
# row, and `_no_dup` refuses to write this file if one creeps in.
def degenerate_ops():
    ops = [(POP, 0), (READ, 3), (NEW, 0x41), (NEW, 0x42), (READ, 0), (READ, 1),
           (READ, 2), (READ, 200), (POP, 0), (POP, 0), (POP, 0), (NEW, 0x43)]
    ops += [(NEW, 0x50 + i) for i in range(CAP + 2)]   # past the capacity guard
    ops += [(READ, CAP - 1), (READ, CAP), (POP, 0), (READ, 255)]
    return ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism -- a band
# named anything else enters the measurement matrix and costs a full re-measure).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: the mix held fixed and the op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band R -- the READ axis: op count fixed at 96, read fraction swept, so the
#           number of allocator calls falls exactly as the number of reads rises.
#           That separates the price of a READ from the price of a NEW/POP pair.
SWEEP_R_FRACS = tuple(i / 20.0 for i in range(0, 17))
# Band S -- the LIVE-OBJECT axis: op count and mix fixed, the generator's stack
#           capacity swept 1..16, so the allocator's working set moves with
#           everything else held.
SWEEP_S_CAPS = tuple(range(1, CAP + 1))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p34 inputs ->", HERE)

    # small: one band of windows, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.45, 0.30)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.45, 0.30)
    write("large.bin", 20000, stride, body)

    ops = degenerate_ops()
    body = encode(rng, ops)
    write("degenerate.bin", 200000, len(body), body)

    # --- adversarial: every DUP in this pattern lives here -----------------
    body = encode(rng, adv_blind_window(4))
    write("adversarial-blind.bin", 200000, len(body), body, check_dup=False)

    body = encode(rng, adv_blindread_window(4))
    write("adversarial-blindread.bin", 200000, len(body), body, check_dup=False)

    body = encode(rng, adv_recycle_window(4))
    write("adversarial-recycle.bin", 200000, len(body), body, check_dup=False)

    body = encode(rng, adv_blind_window(12) + adv_blindread_window(12)
                  + adv_recycle_window(12))
    write("adversarial-many.bin", 20000, len(body), body, check_dup=False)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_dup=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.45, 0.30)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_R_FRACS:
        pn = (1.0 - frac) * 0.60
        pp = (1.0 - frac) * 0.40
        body, stride = tiled(rng, SWEEP_WINS, 96, pn, pp)
        write(f"sweep-r{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride, body)
    for cap in SWEEP_S_CAPS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.45, 0.30, cap=cap)
        write(f"sweep-s{cap:02d}.bin", SWEEP_ITERS, stride, body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
