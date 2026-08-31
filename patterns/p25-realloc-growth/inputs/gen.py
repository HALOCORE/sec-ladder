#!/usr/bin/env python3
"""Generate p25's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p25-realloc-growth/inputs/gen.py            # the 8 matrix inputs
    python3 patterns/p25-realloc-growth/inputs/gen.py --sweep    # + the sweep bands

Payload layout (../spec.md), p06's/p11's/p16's/p17's/p05's/p07's/p03's/p12's/
p14's/p27's/p29's/p32's/p34's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects PUSHT (0), PUSHS (1), SAVE (2) or READ (3) -- so every byte
value is a legal opcode. `a` is the byte pushed on a PUSHT/PUSHS and the element
selector on a SAVE (`curi = a % ntok`); READ ignores `a`.

--------------------------------------------------------------------------
⚠⚠ THE HARD CONSTRAINT: NO NON-ADVERSARIAL WINDOW MAY GROW THE TOKEN
    VECTOR WHILE A SAVED INTERIOR POINTER IS LIVE
--------------------------------------------------------------------------
**ASan's allocator MOVES ON EVERY `realloc`.** So a benign window that grew
`toks` after a SAVE and then read through `cur` would make R1 report
`heap-use-after-free` on a row whose `sanitizer_expect` is `clean`, and stage 7
would fail -- while under plain glibc the same window might be silent, because
glibc extends a small block in place until it runs out of the chunk it has.

That is not a hypothetical about the detector, it is the row's own harm
condition: the interval between a SAVE and the next token-vector `realloc` is
exactly where R1's undefined behaviour lives. Two consequences, either alone
enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree with
     `../model.py` **and with every other cell**. A window that goes stale makes
     R1's answer a draw from freed storage, so such a window cannot be a perf row.
  2. Stage 7 requires the ASan+UBSan C build to be silent on every input declared
     `clean`, and ASan is deliberately the STRICTER instrument here.

So this generator constructs matrix streams in which a `PUSHT` after a `SAVE` is
emitted only while it cannot trigger a `realloc` (`ntok < tcap`), it re-simulates
every blob it writes and refuses to emit one that goes stale, `../model.py`
re-derives the same property from the SHIPPED blob on every gate invocation, and
`../controls/no_stale.py` censuses every file in this directory.

⚠ Note what is NOT forbidden: a `PUSHS` after a `SAVE`. The string vector is a
different allocation and growing it cannot invalidate an interior pointer into
the token vector -- and it is exactly what puts a second live block behind the
token vector so that the token vector's next growth has to MOVE.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS, AND THE HARM WINDOW IS ONE GROWTH WIDE
--------------------------------------------------------------------------
glibc's minimum chunk gives a 4-byte `malloc` 24 usable bytes, so `4 -> 8` and
`8 -> 16` are satisfied in place and it is `16 -> 32` that has to move -- and it
moves only because the string vector was allocated after the token vector and is
still live. **The adversarial windows are TUNED to that growth.** Saying
*"`realloc` moves"* without that qualification would mislead a reader into
expecting the harm at every growth; `../controls/reloc_probe.py` measures which
growth actually relocates under the shipped driver.

  `adversarial-move`      16 PUSHT (so `tcap == 16`), one PUSHS early to pin the
                          token block, a SAVE, then the PUSHT that forces
                          `16 -> 32`, then READs. R1 dereferences an interior
                          pointer into the retired block.
  `adversarial-many`      the same shape four times over in one window, so a
                          rung that survives one stale read has to survive
                          several and ASan's first report is not the only one.
  `adversarial-lateread`  one relocation and then EIGHT stale READs, so the
                          divergence is not a single byte -- see the collision
                          note in ../NOTES.md 2c.
  `adversarial-nogrow`    THE NEGATIVE CONTROL AMONG THE ADVERSARIAL ROWS. A
                          SAVE followed by PUSHTs that do NOT reach the capacity
                          boundary, then READs. Nothing relocates, R1 is correct,
                          ASan is silent, and `model.py` derives `clean` for it.
                          ⚠ It is what stops "the adversarial rows all fire" from
                          being true by construction rather than by measurement.
  `adversarial-stride3`   a 3-byte window, too small for the `nops` header. The
                          driver guard `stride_w >= 4` skips the loop entirely
                          and every rung prints 0 after ZERO kernel calls.
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

SEED = 25
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
SEEDCAP = 4     # must equal every rung's SEED
MAXCAP = 64     # must equal every rung's MAXCAP
SENT = 251      # must equal every rung's SENT

PUSHT, PUSHS, SAVE, READ = 0, 1, 2, 3


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


class _Grow:
    """The capacity discipline both C rungs and all four Rust rungs implement,
    used by the generator to know when a push would `realloc`.

    `n < MAXCAP` is the acceptance guard and `n == cap` is the growth trigger;
    `MAXCAP` is `SEEDCAP * 2**k`, so the sequence is 4, 8, 16, 32, 64 and the
    guard fires exactly at `n == MAXCAP`. **That equivalence is why the safe Rust
    rungs can spell the whole discipline as `if v.len() < MAXCAP { v.push(a) }`**
    and still be the same program."""

    def __init__(self):
        self.n = 0
        self.cap = 0

    def would_grow(self):
        return self.n < MAXCAP and self.n == self.cap

    def push(self):
        """`True` if the push was accepted; sets `self.grew`."""
        self.grew = False
        if self.n >= MAXCAP:
            return False
        if self.n == self.cap:
            # `realloc(NULL, SEEDCAP)` is an allocation, not a relocation; only a
            # growth of an EXISTING block can retire one.
            self.grew = self.cap > 0
            self.cap = self.cap * 2 if self.cap else SEEDCAP
        self.n += 1
        return True


def benign_ops(rng, nops, ppusht, ppushs, psave):
    """A stream of `nops` operations in which **no `PUSHT` that would `realloc`
    is ever emitted after a `SAVE`**.

    ⚠ The constraint is expressed as a fact about what this function can EMIT
    rather than as a filter over its output; `write()` re-simulates the emitted
    bytes anyway, because a filter that cannot fire proves nothing."""
    ops = []
    t, s, saved = _Grow(), _Grow(), False
    while len(ops) < nops:
        r = rng.random()
        if r < ppusht:
            # The one restricted op. After a SAVE it is emitted only while it
            # cannot trigger a growth; when it could, spend the slot on a PUSHS,
            # which is unrestricted and is what pins the token block in place.
            if saved and t.would_grow():
                ops.append((PUSHS, rng.randrange(1, 256)))
                s.push()
                continue
            ops.append((PUSHT, rng.randrange(1, 256)))
            t.push()
        elif r < ppusht + ppushs:
            ops.append((PUSHS, rng.randrange(1, 256)))
            s.push()
        elif r < ppusht + ppushs + psave:
            ops.append((SAVE, rng.randrange(0, 256)))
            if t.n > 0:
                saved = True
        else:
            ops.append((READ, rng.randrange(0, 256)))
    return ops


def mixed_ops(rng, nops, ppusht, ppushs, psave):
    """`benign_ops` prefixed with the two REJECTED shapes, which fold SENT in
    every rung and are therefore full-agreement operations: a `SAVE` with an
    empty token vector and a `READ` before any `SAVE`. They exist so the perf
    inputs exercise the rejected path, which is one of the paths the law has to
    separate."""
    ops = benign_ops(rng, nops, ppusht, ppushs, psave)
    return [(SAVE, 0), (READ, 7)] + ops[:max(0, nops - 2)]


# ---- the checked kernel, in Python, for the generator's own checks ----------
def _walk(win):
    """`(result, went_stale)` for one window under the CHECKED semantics.

    ../model.py's semantics re-implemented here so the generator can validate
    what it writes without importing the model (which imports `slb` against a
    file that does not exist yet).

    ⚠ `went_stale` is **ASan's** condition, not glibc's: the token vector was
    REALLOCATED while a saved interior pointer was live and the program then read
    through it. ASan moves on every `realloc`, so that is exactly when ASan's
    pointer is dead; glibc sometimes extends in place, so it is a conservative
    over-approximation of when glibc's is. ../c/kernel.h says why the gate's
    column is deliberately ASan's."""
    if len(win) < HDR:
        return 0, False
    nops = int.from_bytes(win[0:4], "little")
    if nops == 0:
        return 0, False
    t, s = _Grow(), _Grow()
    toks, strs = [], []
    curi, stale, went = None, False, False
    acc, p = 0, HDR
    for _ in range(nops):
        if len(win) - p < OPSZ:
            break
        c, a = win[p], win[p + 1]
        p += OPSZ
        op = c % 4
        if op == PUSHT:
            if t.push():
                toks.append(a)
                if t.grew and curi is not None:
                    stale = True
                v = a
            else:
                v = SENT
        elif op == PUSHS:
            if s.push():
                strs.append(a)
                v = a
            else:
                v = SENT
        elif op == SAVE:
            if t.n > 0:
                curi = a % t.n
                stale = False
                v = 2
            else:
                v = SENT
        else:
            if curi is None:
                v = SENT
            else:
                if stale:
                    went = True
                v = toks[curi]
        acc = (acc * 31 + v) & MASK
    return (acc * 31 + (t.n + s.n)) & MASK, went


def kernel_result(win):
    return _walk(win)[0]


def window_goes_stale(win):
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


def _no_stale(body, stride):
    """**THE BENIGN INVARIANT, and it is p25's shipped harm condition.** No
    window of a matrix blob may read through an interior pointer whose token
    vector has been reallocated since the SAVE."""
    out = []
    for w in range(len(body) // stride):
        if window_goes_stale(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} reads through an interior pointer whose "
                       f"token vector was reallocated after the SAVE, so R1 "
                       f"would touch retired storage and this is not an "
                       f"adversarial file")
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


def tiled(rng, nwin, nops, ppusht, ppushs, psave, mixed=True):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        gen = mixed_ops if mixed else benign_ops
        body += encode(rng, gen(rng, nops, ppusht, ppushs, psave))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial windows ------------------------------------------------
def adv_move_ops(nread=3):
    """ONE RELOCATION, TUNED TO THE `16 -> 32` GROWTH.

    The single early `PUSHS` is load-bearing and not decoration: it puts a live
    4-byte string block immediately behind the 4-byte token block, so that when
    the token block finally needs more than the 24 usable bytes glibc gave it,
    it cannot extend and must move. Without it the token vector is the newest
    allocation and glibc extends it in place -- which is exactly the topology
    `TASK_134` measured and mistook for a fact about C."""
    ops = [(PUSHT, 0x41), (PUSHS, 0x61)]
    ops += [(PUSHT, 0x41 + i) for i in range(1, 16)]   # ntok == 16 == tcap
    ops += [(SAVE, 3)]                                  # cur = &toks[3]
    ops += [(PUSHT, 0xF0)]                              # 16 -> 32: RELOCATES
    ops += [(READ, 0)] * nread
    return ops


def adv_nogrow_ops(nread=3):
    """THE NEGATIVE CONTROL AMONG THE ADVERSARIAL ROWS: a SAVE, then pushes that
    stay strictly inside the current capacity, then READs. Nothing is retired,
    R1 is correct, and `model.py` derives `sanitizer_expect: clean` -- so the
    `fires` rows are a measurement rather than a property of the filename."""
    ops = [(PUSHT, 0x41), (PUSHS, 0x61)]
    ops += [(PUSHT, 0x41 + i) for i in range(1, 6)]     # ntok == 6, tcap == 8
    ops += [(SAVE, 2)]
    ops += [(PUSHT, 0xF0)]                              # ntok 6 -> 7 < tcap: no realloc
    ops += [(READ, 0)] * nread
    return ops


def adv_lateread_ops(nread=8):
    return adv_move_ops(nread)


def adv_many_ops(rounds=4):
    """The relocation shape repeated: four SAVE / grow / READ rounds on the SAME
    two vectors.

    ⚠⚠ **AND THE MEASUREMENT SAYS ONLY ONE OF THE FOUR ROUNDS ACTUALLY
    RELOCATES.** `../controls/reloc_probe.py` on this window records seven
    `realloc` calls at sizes `[4, 4, 8, 16, 32, 64, 8]` and **MOVED only at
    32**, on both compilers -- so the `32 -> 64` growth extends in place, because
    by then the token block has already moved to the top of the heap and has room.
    An earlier version of this docstring asserted that the later rounds relocate
    at `32 -> 64`; that was a prediction and it is FALSE.

    ⚠ That is not a defect of the input, it is the row's ASan-vs-glibc bias
    stated as data: `../model.py` derives `fires` for all four rounds because
    ASan's allocator moves on every `realloc`, while under plain glibc exactly
    one of the four reads retired storage. Both facts are reported, in
    `../NOTES.md` 2."""
    ops = [(PUSHT, 0x41), (PUSHS, 0x61)]
    for r in range(rounds):
        ops += [(PUSHT, 0x50 + r), (PUSHT, 0x51 + r), (PUSHT, 0x52 + r),
                (PUSHT, 0x53 + r)]
        ops += [(SAVE, 1 + r)]
        ops += [(PUSHT, 0x60 + r)] * 12
        ops += [(READ, 0), (READ, 1)]
        ops += [(PUSHS, 0x70 + r)]
    return ops


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a SAVE with an EMPTY token vector and a READ before any SAVE: both fold
#     SENT in every rung, and neither is the bug;
#   * a push past MAXCAP: the capacity guard is in every rung including R1;
#   * a SAVE whose operand exceeds the token count: the index is `a % ntok`, so
#     every operand names a live element and nothing is rejected for being
#     malformed -- the boundary from both sides;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
#
# ⚠ What is NOT here: a growth after a SAVE. That is the bug, it belongs on an
# `adversarial-*` row, and `_no_stale` refuses to write this file if one creeps
# in.
def degenerate_ops():
    ops = [(SAVE, 0), (READ, 3), (PUSHT, 0x41), (PUSHS, 0x42)]
    ops += [(PUSHT, 0x50 + (i % 200)) for i in range(MAXCAP + 2)]  # past MAXCAP
    ops += [(PUSHS, 0x30 + (i % 200)) for i in range(MAXCAP + 2)]  # past MAXCAP
    ops += [(SAVE, MAXCAP - 1), (READ, 0), (SAVE, MAXCAP), (READ, 0),
            (SAVE, 255), (READ, 0), (READ, 9)]
    return ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism -- a band
# named anything else enters the measurement matrix and costs a full re-measure).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: the mix held fixed and the op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band R -- the READ axis: op count fixed at 96, read fraction swept, so the
#           number of pushes (and therefore of `realloc` calls) falls exactly as
#           the number of guarded reads rises. That separates the price of the
#           safety line from the price of a push.
SWEEP_R_FRACS = tuple(i / 20.0 for i in range(0, 17))
# Band T -- the TOKEN-SHARE axis: op count and read fraction fixed, the split
#           between PUSHT and PUSHS swept, so the number of token-vector
#           growths moves with everything else held.
SWEEP_T_SHARES = tuple(i / 10.0 for i in range(1, 10))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p25 inputs ->", HERE)

    # small: one band of windows, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.34, 0.22, 0.14)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.34, 0.22, 0.14)
    write("large.bin", 20000, stride, body)

    ops = degenerate_ops()
    body = encode(rng, ops)
    write("degenerate.bin", 200000, len(body), body)

    # --- adversarial: every stale read in this pattern lives here ----------
    body = encode(rng, adv_move_ops())
    write("adversarial-move.bin", 200000, len(body), body, check_stale=False)

    body = encode(rng, adv_lateread_ops())
    write("adversarial-lateread.bin", 200000, len(body), body, check_stale=False)

    body = encode(rng, adv_many_ops())
    write("adversarial-many.bin", 20000, len(body), body, check_stale=False)

    # The negative control among the adversarial rows: a SAVE, pushes that do
    # NOT reach the capacity boundary, then READs. Nothing relocates.
    body = encode(rng, adv_nogrow_ops())
    write("adversarial-nogrow.bin", 200000, len(body), body)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_stale=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.34, 0.22, 0.14)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_R_FRACS:
        rest = 1.0 - frac
        body, stride = tiled(rng, SWEEP_WINS, 96, rest * 0.48, rest * 0.32,
                             rest * 0.20)
        write(f"sweep-r{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride, body)
    for share in SWEEP_T_SHARES:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.56 * share,
                             0.56 * (1.0 - share), 0.14)
        write(f"sweep-t{int(round(share * 100)):03d}.bin", SWEEP_ITERS, stride, body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
