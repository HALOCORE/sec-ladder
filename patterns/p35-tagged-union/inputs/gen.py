#!/usr/bin/env python3
"""p35 input generator. Deterministic; `python3 inputs/gen.py` rebuilds every
`.bin` in this directory byte for byte.

The `.bin` files are gitignored, so THIS FILE is the committed artefact and the
only reproduction path for anything measured on them
(`.memory/00-environment.md` constraint 6; `harness/check.py` hashes it into
`source_sha256` for exactly that reason).

FORMAT (`.memory/02-bench-rules.md`, common/slb.py)
--------------------------------------------------
    u64 n_iters | u64 payload_len | payload
    payload = u64 stride | byte blob

The driver walks the blob in `stride`-byte windows and calls
`kernel(buf, n_blob, k * stride, stride)`. A window is

    u32 LE nops | nops * (opcode byte, operand byte)

    opcode c: c % 4 == 0  SET_INT   cannot fail
              c % 4 == 1  SET_PTR   takes a byte out of the budget
              c % 4 == 2  SET_DBL   takes a byte out of the budget
              c % 4 == 3  GET       dispatch on the tag
    operand a: cell index is `a % 8`; the payload is a function of `a`.

WHAT THE ADVERSARIAL INPUTS ARE FOR, AND HOW THEY ARE BUILT
-----------------------------------------------------------
`c/kernel.c` publishes the TAG BEFORE the payload lands, so a store that fails
for want of budget leaves a cell claiming a type its payload is not. Reaching
that state needs three things in one window, in order:

  1. a SET_INT into cell `k`, so the union holds an integer;
  2. enough successful SET_PTR/SET_DBL to exhaust `BUDGET`;
  3. a SET_PTR (or SET_DBL) into cell `k`, which FAILS -- and in R1 publishes
     the tag regardless;
  4. a GET on cell `k`.

⚠ **The BENIGN inputs must not reach it**, or the two C rungs would disagree on
an input the gate requires them to agree on. `_BuggyState` below is a live
simulation of R1's semantics inside the generator: the benign streams consult it
and never emit a GET on a cell whose tag and payload have come apart. That is a
CONSTRUCTION, not a filter -- there is no rejection sampling anywhere here, so
the generator is O(nops) and its output does not depend on a retry count.

⚠⚠ **`adversarial-stride3.bin` attacks the DRIVER, not the kernel**: its stride
is 3, below the 4-byte window header, so every conforming driver skips the loop
entirely and prints 0.
"""

import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

CELLS = 8
BUDGET = 4
T_UNSET, T_INT, T_PTR, T_DBL = 0, 1, 2, 3

# ---------------------------------------------------------------------------


class _BuggyState:
    """R1's semantics, tracked so the benign generator can stay out of the
    confused region. `tag[k]` is what the cell CLAIMS; `kind[k]` is what its
    payload actually is. R1 lets them differ; R1h cannot."""

    def __init__(self):
        self.tag = [T_UNSET] * CELLS
        self.kind = [T_UNSET] * CELLS
        self.navail = BUDGET

    def clean(self, k):
        return self.tag[k] == self.kind[k]

    def step(self, c, a):
        k = a % CELLS
        m = c % 4
        if m == 0:
            self.tag[k] = T_INT
            self.kind[k] = T_INT
        elif m in (1, 2):
            t = T_PTR if m == 1 else T_DBL
            self.tag[k] = t                 # R1 publishes here, always
            if self.navail > 0:
                self.kind[k] = t
                self.navail -= 1


def opbyte(rng, m):
    """An opcode byte congruent to `m` mod 4. Every byte value is a legal
    opcode, so the whole range is used rather than the four smallest."""
    return m + 4 * rng.randrange(0, 64)


def operand(rng, k):
    """An operand byte whose cell index is `k`. The high bits vary the payload
    without moving the cell."""
    return (k + CELLS * rng.randrange(0, 256 // CELLS)) & 0xFF


def encode(ops):
    """`nops | (c, a) * nops`, which is exactly one window."""
    body = struct.pack("<I", len(ops))
    for c, a in ops:
        body += bytes([c & 0xFF, a & 0xFF])
    return body


def benign_ops(rng, nops):
    """A stream that R1 and R1h agree on, by construction.

    Every op is legal and the budget is allowed to run out -- the `SENT` arm of
    a failed store IS exercised -- but a GET is only ever emitted on a cell
    whose tag and payload still agree under R1's semantics. Cells whose tag has
    come apart are simply never read."""
    st = _BuggyState()
    ops = []
    for _ in range(nops):
        r = rng.random()
        clean = [k for k in range(CELLS) if st.clean(k)]
        if r < 0.30:
            m, k = 0, rng.randrange(CELLS)
        elif r < 0.45:
            m, k = 1, rng.randrange(CELLS)
        elif r < 0.60:
            m, k = 2, rng.randrange(CELLS)
        elif clean:
            m, k = 3, rng.choice(clean)
        else:
            # Every cell's tag has come apart from its payload, so there is no
            # GET this stream may emit. A SET_INT cannot fail, so it puts one
            # cell back in agreement and the next op has somewhere to read.
            m, k = 0, rng.randrange(CELLS)
        c, a = opbyte(rng, m), operand(rng, k)
        st.step(c, a)
        ops.append((c, a))
    return ops


def confusion_ops(rng, claim, extra=0):
    """The four-step recipe from the module docstring. `claim` is the tag the
    failing store publishes: 1 = SET_PTR, 2 = SET_DBL."""
    ops = [(opbyte(rng, 0), operand(rng, 0))]                 # 1. SET_INT c0
    for j in range(BUDGET):                                   # 2. exhaust
        ops.append((opbyte(rng, 1 + (j % 2)), operand(rng, 1 + j)))
    ops.append((opbyte(rng, claim), operand(rng, 0)))         # 3. failing store
    ops.append((opbyte(rng, 3), operand(rng, 0)))             # 4. GET c0
    for _ in range(extra):                                    # padding ops
        ops.append((opbyte(rng, 0), operand(rng, 7)))
    return ops


def tiled(rng, nwin, nops):
    """`nwin` benign windows of the same stride, concatenated."""
    return b"".join(encode(benign_ops(rng, nops)) for _ in range(nwin))


def degenerate_windows(rng):
    """Windows that make the kernel return early or do nothing interesting:
    `nops == 0`, a stream that runs out of bytes before its declared count, and
    a stream of GETs on cells nothing ever wrote (the `tag == 0` arm)."""
    w = []
    # GETs on cells nothing wrote: the `tag == 0` arm folds SENT in both rungs.
    # FIRST, so that window 0 -- the one the driver always visits on its first
    # call, because `k` is derived from an accumulator that starts at 0 --
    # returns something other than 0 and the other two windows stay reachable.
    w.append(encode([(opbyte(rng, 3), operand(rng, k % CELLS))
                     for k in range(4)]))
    # nops == 0 -- the kernel returns 0 before touching a cell.
    w.append(struct.pack("<I", 0) + b"\x00" * 8)
    # nops declared far above what the window carries: the cursor guard stops
    # the walk, which is the `len - p < 2` break.
    w.append(struct.pack("<I", 4096) +
             b"".join(bytes([opbyte(rng, 0), operand(rng, k)])
                      for k in range(4)))
    n = max(len(x) for x in w)
    return b"".join(x + b"\x00" * (n - len(x)) for x in w), n


def write(name, n_iters, stride, body, declared_len=None):
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len=declared_len)
    return path


# ---------------------------------------------------------------------------
# The sweep. Diagnostic only: `harness/check.py` drops `sweep-*` from the
# matrix (`inputs_of`), and a per-call cost measured at ONE window length is a
# coincidence rather than a law.
# ⚠ CITATION CORRECTED AT TASK_153. This comment read ~~NOTES.md 8 fits the
# `Ir` per operation over this family~~ and NO SUCH FIT EXISTS: NOTES.md 8 is
# the *"what this pattern does NOT publish"* list and NOTES.md 12.6 says in
# terms that **no sweep law is published and nothing in the pattern rests on
# these blobs.** Same rot class as the `NOTES.md 6b/6c` letters TASK_148 caught
# one file over -- a pointer that decayed away from the thing it points at.
SWEEP_NOPS = tuple(range(4, 65, 4))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    rng = random.Random(35_0148)

    # --- small: one modest window family --------------------------------
    nops = 24
    stride = 4 + 2 * nops
    write("small.bin", 200, stride, tiled(rng, 8, nops))

    # --- large: the measurement blob ------------------------------------
    nops = 120
    stride = 4 + 2 * nops
    write("large.bin", 200, stride, tiled(rng, 64, nops))

    # --- degenerate: early returns and the unset-tag arm ----------------
    body, stride = degenerate_windows(rng)
    write("degenerate.bin", 200, stride, body)

    # --- adversarial: one window each, so the driver always visits it ---
    for name, claim in (("adversarial-ptr-confusion.bin", 1),
                        ("adversarial-dbl-confusion.bin", 2)):
        ops = confusion_ops(rng, claim)
        body = encode(ops)
        write(name, 40, len(body), body)

    # the PTR confusion reached DEEP in a window rather than at its seventh op,
    # so that the harm is not an artefact of a four-instruction prologue. The
    # prefix is benign by construction (`_BuggyState`) and is followed by the
    # recipe; `_BuggyState` is re-seeded because the recipe assumes a full
    # budget, so the prefix uses SET_INT and GET only.
    st = _BuggyState()
    ops = []
    for _ in range(24):
        k = rng.randrange(CELLS)
        m = 0 if rng.random() < 0.5 else 3
        c, a = opbyte(rng, m), operand(rng, k)
        st.step(c, a)
        ops.append((c, a))
    ops += confusion_ops(rng, 1)
    body = encode(ops)
    write("adversarial-ptr-deep.bin", 40, len(body), body)

    # the budget exhausted many times over, with a GET after every failed store
    ops = [(opbyte(rng, 0), operand(rng, k)) for k in range(CELLS)]
    for j in range(BUDGET):
        ops.append((opbyte(rng, 1), operand(rng, j)))
    for k in range(CELLS):
        ops.append((opbyte(rng, 2), operand(rng, k)))
        ops.append((opbyte(rng, 3), operand(rng, k)))
    body = encode(ops)
    write("adversarial-exhaust.bin", 40, len(body), body)

    # the driver's own guard: a stride below the 4-byte window header
    write("adversarial-stride3.bin", 200, 3, encode(benign_ops(rng, 24)))

    # --- the sweep ------------------------------------------------------
    for n in SWEEP_NOPS:
        stride = 4 + 2 * n
        write(f"sweep-nops{n:03d}.bin", SWEEP_ITERS, stride,
              tiled(rng, SWEEP_WINS, n))

    for f in sorted(os.listdir(HERE)):
        if f.endswith(".bin"):
            print(f"  {f:34s} {os.path.getsize(os.path.join(HERE, f)):>9d} B")


if __name__ == "__main__":
    main()
