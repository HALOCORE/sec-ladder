#!/usr/bin/env python3
"""Generate p49's input files. Deterministic from a fixed seed; `.bin` is
gitignored and this script is what is committed (`.memory/02-bench-rules.md`),
and `harness/check.py` hashes it into `source_sha256`, so every law measured on
these blobs is re-derivable from a file the gate record sees.

    python3 patterns/p49-interned-pool/inputs/gen.py            # the matrix inputs
    python3 patterns/p49-interned-pool/inputs/gen.py --sweep     # + the sweep bands

Payload layout (../spec.md), p27's, p29's, p32's and p34's verbatim:

    word 0     u64  stride     bytes per window; the kernel walks one window
    byte 8..   u8[] blob       the windows; n_blob = payload_len - 8

A window is

    byte 0..4    nops  u32 LE     declared op count   ATTACKER DATA
    byte 4..     ops, each 2 bytes: c = opcode byte, a = operand byte

and `c % 4` selects DEFINE (0 or 1), BREAK (2) or READ (3) -- so every byte value
is a legal opcode. On a DEFINE the operand names the CONTENT and nothing else:
the width is `w = 1 + a % MAXW` and the key is `key = a % NKEY`, so `(key, w)`
is the string. On a BREAK or a READ the same byte names a RECORD, `a % nrec`.
**The file never names a buffer and never names an offset**: which records share
storage is something the POOL decides, from the strings the file asks for. That
is `p27`'s stated precedent -- *a file cannot name a pointer, but it CAN name an
operation that saves one* -- applied to an intern table, and `TASK_160` §4
established by reduction that it survives the `kernel(buf, off, len) -> u64`
signature.

--------------------------------------------------------------------------
THE THRESHOLD IS A REAL TEST, AND THIS IS WHERE THAT IS DECIDED
--------------------------------------------------------------------------
`MAXW = 6` and `THRESH = 4`, so `w` ranges over `1 .. 6` and `w < THRESH` is
true for three of the six. **Both branches of the INLINE_THRESHOLD are live on
every random stream**, and `rshd[]` -- which the safety line reads -- genuinely
varies.

⚠⚠ **THE REDUCTION THIS ROW IS BUILT FROM HAD THE OPPOSITE PROPERTY AND IT WAS
A DEFECT.** `.temp/t160/red/k40304.c` fixes the content width at `K_CLEN 3`
against `K_THRESH 5`, so `if (K_CLEN < K_THRESH)` is `if (3 < 5)` -- a
compile-time constant -- the non-interned branch is DEAD and **no record is ever
born owned**, so the `INLINE_THRESHOLD`, which is the CVE's own precondition, is
not a test at all. That is `.memory/03-measurement.md` entry 19's shape.

⚠⚠⚠ **AND THE STRONGER FORM OF THAT CLAIM -- *the copy-on-write guard
`if (r_shared[i])` CAN NEVER BE FALSE*, which `TASK_161.md` and
`.temp/mgr161/NOTES.md` both assert verbatim -- IS FALSE.** The reduction's own
copy-on-write arm writes `r_shared[i] = 0;` when it un-shares, so a SECOND BREAK
on a record the first one copied takes the false branch: measured in the
reduction's own C, 30 263 false evaluations out of 97 458 (31.1%) over 20 000
random op streams (`.temp/t161/red_probe/probe.py`). ⚠ What IS true of the
reduction AS SHIPPED is that its two blobs evaluate the guard ONCE between them
and it is TRUE that once. **The precise defect is *no record is ever born
owned*.** `../controls/threshold.py` measures both configurations side by side
on the SHIPPED kernel semantics rather than restating this paragraph, and splits
`guard FALSE` into *on a record born owned* and *after an earlier
copy-on-write* -- only the first is what the threshold buys.

--------------------------------------------------------------------------
WHY NO BENIGN WINDOW MAY BREAK A SHARED RECORD
--------------------------------------------------------------------------
Two independent reasons, and either alone would be enough:

  1. `harness/check.py` stage 2 requires every non-adversarial cell to agree
     with `../model.py` **and with every other cell**. A BREAK on a shared
     record is precisely where R1 and R1h part company, so such a window cannot
     be a performance row.
  2. TASK_055_REVIEW blocker B1, inherited from p27: the two rungs' answers must
     not depend on the optimisation level, and `build.py` builds both levels into
     one agreement set.

⚠ **The divergence is not only the corrupted byte.** R1h's copy-on-write also
consumes private storage and clears the record's `rshd` flag, and the epilogue
folds that flag, so a BREAK on a shared record moves the checksum even when no
OTHER record was naming the buffer. Both halves are excluded by the same
property, which is why the property is stated about the FLAG and not about the
corruption.

⚠ **What is NOT a reason here**: on p49 what the buggy rung returns IS
reproducible. The pool is a local array with no heap addresses in it, so R1's
checksum is one distinct value in twenty runs on every adversarial input
(../NOTES.md 2d). p49's adversarial rows are excluded from the agreement set
because they DISAGREE, not because they are unstable -- p32's position, not
p27's.

This generator carries a copy of the checked kernel and simply does not emit a
BREAK that would name a shared record: it picks an operand that names an OWNED
one instead, and emits a READ when the window holds no owned record at all.
Everything else -- exhausting the intern table, exhausting the arena, exhausting
the private region, filling the record table, deduplicating heavily -- is left
to the dice. `../model.py::no_share_break_problems` re-derives the property from
the SHIPPED blob at every gate invocation, and `../controls/no_share_break.py`
censuses the whole directory.

--------------------------------------------------------------------------
THE ADVERSARIAL ROWS ARE A HARM LADDER, NOT A MAGNITUDE LADDER
--------------------------------------------------------------------------
  `adversarial-share`    DEFINE two records with the SAME string, so they
                         deduplicate onto ONE buffer; BREAK the second; READ the
                         first. **R1 rewrites a value the first record owns.**
                         The row's headline in four operations.
  `adversarial-rehash`   the DOWNSTREAM half, and the port's actual harm: BREAK
                         an interned record, then DEFINE the same string AGAIN.
                         The dedup table still hands back the arena buffer, which
                         is now corrupt, so the NEW record is wrong from birth
                         and no record it shares with was ever written through.
  `adversarial-cascade`  four records on one buffer, one BREAK, four READs -- so
                         the blast radius is in the checksum rather than
                         inferred.
  `adversarial-cowfull`  the private region driven to exhaustion FIRST, then a
                         BREAK on a shared record. R1 writes through; R1h cannot
                         un-share and REFUSES. The cell that prices copy-on-write
                         as a repair that consumes a resource.
  `adversarial-many`     all four in one window, with the record table filled in
                         between so the `nrec == NREC` arm fires too.
  `adversarial-stride3`  a 3-byte window, too small for the `nops` header. The
                         driver guard `stride_w >= 4` skips the loop entirely and
                         every rung prints 0 after ZERO kernel calls.

--------------------------------------------------------------------------
p49 AND `.memory/02-bench-rules.md`'s WRITE RULE
--------------------------------------------------------------------------
p49's BREAK is a write, and it is not a write out of bounds: `roff[t]` is the
base of a buffer that was created under an explicit capacity test, so
`mem[roff[t]]` is inside `mem[0 .. MEM)` in every run of both rungs. The write
rule's threshold test (p12, TASK_041) is about a store that leaves the object,
and no store here can. **"The guard fired" and "the unguarded rung committed UB"
are not merely independent events on p49 -- the second one never happens on any
input**, which is this row's whole point: ../model.py declares
`sanitizer_expect` `clean` everywhere and says so.
"""

import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "common"))
import slb  # noqa: E402

SEED = 49
MASK = (1 << 64) - 1
HDR = 4
OPSZ = 2
MEM = 64
ARENA = 20
NENT = 8
NREC = 12
NKEY = 7
MAXW = 6
THRESH = 4
SENT = 251

DEFINE_A, DEFINE_B, BREAK, READ = 0, 1, 2, 3


def cbyte(key, j):
    return (key * 7 + j * 13 + 1) & 0xFF


# ---- the checked kernel, in Python, for the generator's own checks ----------
# Re-implemented here rather than imported from ../model.py, which imports `slb`
# against a file that does not exist yet. p27's, p29's and p32's gen.py duplicate
# their walk for the same reason. This is the OFFSET formulation -- the same one
# ../verus.rs's `run` uses -- and ../model.py's simulation is the OTHER one,
# buffer objects with identity.
class Sim:
    """The checked (R1h) semantics, stepped one op at a time so the generator
    can ask what an op WOULD do before committing to it."""

    def __init__(self):
        self.mem = bytearray(MEM)
        self.ekey, self.elen, self.eoff = [], [], []
        self.roff, self.rlen, self.rshd = [], [], []
        self.abump, self.pbump = 0, ARENA
        self.acc = 0
        self.share_break = False    # did a BREAK ever name a SHARED record?

    def break_is_owned(self, a):
        """Would a BREAK with operand `a` name a record this window OWNS?
        A window with no records at all folds SENT in every rung, which is
        agreeing, so it counts as owned."""
        if not self.roff:
            return True
        return self.rshd[a % len(self.roff)] == 0

    def step(self, op, a):
        w = 1 + a % MAXW
        key = a % NKEY
        if op in (DEFINE_A, DEFINE_B):
            if len(self.roff) >= NREC:
                v = SENT
            elif w < THRESH:
                f = len(self.ekey)
                for k in range(len(self.ekey)):
                    if self.ekey[k] == key and self.elen[k] == w:
                        f = k
                        break
                if f == len(self.ekey):
                    if len(self.ekey) >= NENT or self.abump + w > ARENA:
                        v = SENT
                    else:
                        for j in range(w):
                            self.mem[self.abump + j] = cbyte(key, j)
                        self.ekey.append(key)
                        self.elen.append(w)
                        self.eoff.append(self.abump)
                        self.roff.append(self.abump)
                        self.rlen.append(w)
                        self.rshd.append(1)
                        self.abump += w
                        v = a
                else:
                    self.roff.append(self.eoff[f])
                    self.rlen.append(w)
                    self.rshd.append(1)
                    v = a
            else:
                if self.pbump + w > MEM:
                    v = SENT
                else:
                    for j in range(w):
                        self.mem[self.pbump + j] = cbyte(key, j)
                    self.roff.append(self.pbump)
                    self.rlen.append(w)
                    self.rshd.append(0)
                    self.pbump += w
                    v = a
        elif op == BREAK:
            if not self.roff:
                v = SENT
            else:
                t = a % len(self.roff)
                if self.rshd[t]:
                    self.share_break = True
                    if self.pbump + self.rlen[t] > MEM:
                        self.acc = (self.acc * 31 + SENT) & MASK
                        return
                    for j in range(self.rlen[t]):
                        self.mem[self.pbump + j] = self.mem[self.roff[t] + j]
                    self.roff[t] = self.pbump
                    self.rshd[t] = 0
                    self.pbump += self.rlen[t]
                self.mem[self.roff[t]] = 0
                v = 2
        else:
            if not self.roff:
                v = SENT
            else:
                t = a % len(self.roff)
                v = 0
                for j in range(self.rlen[t]):
                    v = (v * 31 + self.mem[self.roff[t] + j]) & MASK
        self.acc = (self.acc * 31 + v) & MASK

    def result(self):
        acc = self.acc
        for t in range(len(self.roff)):
            for j in range(self.rlen[t]):
                acc = (acc * 31 + self.mem[self.roff[t] + j]) & MASK
            acc = (acc * 31 + self.rshd[t]) & MASK
        return (acc * 31 + len(self.roff)) & MASK


def _walk(win):
    """(result, a_BREAK_named_a_SHARED_record)."""
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
    return s.result(), s.share_break


def kernel_result(win):
    return _walk(win)[0]


def window_breaks_shared(win):
    return _walk(win)[1]


# ---- op-stream construction -------------------------------------------------
def opbyte(rng, op):
    """A byte whose `% 4` is `op`, so the opcode byte is not a constant."""
    return 4 * rng.randrange(0, 64) + op


def define_operand(rng, key, w):
    """A byte with `a % NKEY == key` and `1 + a % MAXW == w`. The two moduli are
    coprime, so CRT gives exactly one residue mod 42 and there are six of them
    below 256; the choice among those six varies the byte without varying the
    string."""
    want = [a for a in range(256) if a % NKEY == key and 1 + a % MAXW == w]
    return rng.choice(want)


def rec_operand(rng, t, nrec):
    """A byte with `a % nrec == t`, so the operand names record `t`."""
    want = [a for a in range(256) if nrec and a % nrec == t]
    return rng.choice(want) if want else rng.randrange(0, 256)


def encode(rng, ops):
    out = bytearray(struct.pack("<I", len(ops)))
    for op, a in ops:
        out.append(opbyte(rng, op))
        out.append(a & 0xFF)
    return bytes(out)


def benign_ops(rng, nops, pdefine, pbreak):
    """A stream of `nops` operations in which **no BREAK ever names a SHARED
    record**. The generator carries the checked semantics and simply does not
    emit one: when the dice say BREAK it looks for an operand naming an OWNED
    record, and emits a READ when the window holds none."""
    s = Sim()
    ops = []
    while len(ops) < nops:
        x = rng.random()
        if x < pdefine:
            key = rng.randrange(0, NKEY)
            w = 1 + rng.randrange(0, MAXW)
            op, a = DEFINE_A if rng.random() < 0.5 else DEFINE_B, \
                define_operand(rng, key, w)
        elif x < pdefine + pbreak:
            op = BREAK
            owned = [t for t in range(len(s.roff)) if s.rshd[t] == 0]
            if owned:
                a = rec_operand(rng, rng.choice(owned), len(s.roff))
            else:
                op, a = READ, rng.randrange(0, 256)
        else:
            op, a = READ, rng.randrange(0, 256)
        if op == BREAK and not s.break_is_owned(a):
            op = READ                     # belt and braces: never emit one
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


def _no_share_break(body, stride):
    """**The benign invariant**: no window may BREAK a record whose buffer is
    shared. See the module docstring for the two independent reasons."""
    out = []
    for w in range(len(body) // stride):
        if window_breaks_shared(body[w * stride:(w + 1) * stride]):
            out.append(f"window {w} BREAKs a SHARED record; R1 would write "
                       f"through a buffer it does not own and diverge, and this "
                       f"is not an adversarial file")
    return out


def write(name, n_iters, stride, body, declared_len=None, check_zero=True,
          check_share=True):
    if check_zero and stride and len(body) >= stride:
        for p in _no_zero_window(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    if check_share and stride and len(body) >= stride:
        for p in _no_share_break(body, stride):
            print(f"gen.py: {name}: {p}", file=sys.stderr)
            raise SystemExit(1)
    payload = slb.pack_head1_bytes(stride, body)
    path = os.path.join(HERE, name)
    slb.write(path, n_iters, payload, declared_len)
    print(f"  {name:32s} n_iters={n_iters:<8d} stride={stride:<7d} "
          f"n_blob={len(body):<9d} nwin={len(body)//stride if stride else 0:<6d} "
          f"payload={len(payload)}")


def tiled(rng, nwin, nops, pdefine, pbreak):
    """`nwin` windows of the same op count, so every window is `stride` bytes."""
    body = bytearray()
    for _ in range(nwin):
        body += encode(rng, benign_ops(rng, nops, pdefine, pbreak))
    return bytes(body), HDR + OPSZ * nops


# ---- the adversarial and degenerate windows ---------------------------------
# Built through a LIVE simulation rather than from hand-written record indices.
# ⚠ The first draft of this file hard-coded `nrec` at every BREAK site and the
# degenerate window's BREAK landed on a SHARED record -- `_no_share_break`
# caught it, which is what that check is for. A record index is a fact about the
# stream so far, so the stream so far is what has to compute it.
class Builder:
    """An op list and the checked semantics that op list produces, in step."""

    def __init__(self, rng):
        self.rng = rng
        self.sim = Sim()
        self.ops = []

    def emit(self, op, a):
        self.sim.step(op, a)
        self.ops.append((op, a))
        return self

    def short(self, k, w=2):
        """A SHORT string: `w < THRESH`, so it INTERNS and can be shared."""
        assert w < THRESH
        return self.emit(DEFINE_A, define_operand(self.rng, k, w))

    def long(self, k, w=5):
        """A LONG string: `w >= THRESH`, so it is copied and is OWNED."""
        assert w >= THRESH
        return self.emit(DEFINE_B, define_operand(self.rng, k, w))

    def rec(self, t):
        return rec_operand(self.rng, t, len(self.sim.roff))

    def brk(self, t):
        return self.emit(BREAK, self.rec(t))

    def read(self, t):
        return self.emit(READ, self.rec(t))

    def brk_owned(self):
        """BREAK a record this window OWNS -- the guard's FALSE branch."""
        owned = [t for t in range(len(self.sim.roff)) if self.sim.rshd[t] == 0]
        if not owned:
            return self.emit(READ, self.rng.randrange(0, 256))
        return self.brk(self.rng.choice(owned))

    def brk_shared(self):
        """BREAK a record whose buffer is SHARED -- the guard's TRUE branch, and
        the bug. Adversarial rows only; raises rather than emitting a READ,
        because an adversarial window that quietly stopped being adversarial is
        the failure this generator must not have."""
        shared = [t for t in range(len(self.sim.roff)) if self.sim.rshd[t] == 1]
        if not shared:
            raise SystemExit("gen.py: brk_shared() with no shared record -- the "
                             "adversarial window does not do what it says")
        return self.brk(self.rng.choice(shared))


def adv_share_window(rng):
    """The row's headline in six operations. Records 0 and 1 ask for the SAME
    string, so the pool deduplicates them onto ONE buffer; the BREAK on record 1
    then rewrites record 0's value in `c/kernel.c` and does not in
    `c/kernel_hardened.c`."""
    b = Builder(rng)
    b.short(3, 2).short(3, 2).read(0)
    b.brk(1)                       # record 1 shares record 0's buffer
    b.read(0).read(1)
    return b.ops


def adv_rehash_window(rng):
    """The DOWNSTREAM harm, and the port's actual one: the corrupted buffer is
    still what the DEDUP TABLE hands out. Record 0 interns the string, the BREAK
    writes through the arena copy, and a LATER record -- which no BREAK ever
    touched and which shared with nobody at the moment the BREAK happened -- is
    handed the corrupted bytes at birth. **This is the cell in which the harm
    crosses an ownership boundary FORWARDS IN TIME**, and it is the one the
    `p32` comparison cannot produce: no handle is stale, nothing was recycled,
    and the table's answer is exactly the one it should give."""
    b = Builder(rng)
    b.short(5, 3)
    b.brk(0)                       # writes through the ARENA copy
    b.short(5, 3)                  # dedup HIT on the now-corrupt entry
    b.read(1)
    b.long(2, 4)
    b.read(1).read(0)
    return b.ops


def adv_cascade_window(rng):
    """Four records on one buffer, ONE break, four reads: the blast radius is in
    the checksum rather than inferred."""
    b = Builder(rng)
    b.short(1, 1).short(1, 1).short(1, 1).short(1, 1)
    b.brk(2)
    b.read(0).read(1).read(2).read(3)
    return b.ops


def adv_cowfull_window(rng):
    """Drive the PRIVATE region to exhaustion with owned records, then BREAK a
    shared one. `c/kernel.c` writes through; `c/kernel_hardened.c` has nowhere to
    put the private copy and REFUSES. **The cell that prices copy-on-write as a
    repair that consumes a resource**, and the reason `c/kernel_hardened.c` has a
    SENT branch the bug does not."""
    b = Builder(rng)
    b.short(4, 3).short(4, 3)      # two records, ONE 3-byte arena buffer
    # The private region is `MEM - ARENA` = 44 bytes. Seven 6-byte strings fit
    # (`pbump` reaches 62) and the eighth folds SENT, so un-sharing a 3-byte
    # buffer needs 62 + 3 = 65 > 64 and CANNOT happen.
    for k in range(8):
        b.long(k % NKEY, 6)
    b.brk_shared()
    b.read(0).read(1)
    return b.ops


def adv_many_window(rng):
    b = Builder(rng)
    b.short(3, 2).short(3, 2).read(0).brk(1).read(0).read(1)
    b.short(5, 3).brk(0).short(5, 3).read(1)
    b.short(1, 1).short(1, 1).brk_shared()
    for k in range(4):             # fill the record table: the nrec == NREC arm
        b.long(k % NKEY, 4)
    b.long(0, 4).long(1, 4)        # both fold SENT
    b.read(0).brk_owned().read(0)
    return b.ops


# ---- degenerate: the shapes the contract has to decide, ALL AGREEING --------
#
#   * a BREAK and a READ before any record exists: `nrec == 0`, and every rung
#     folds SENT;
#   * every DEFINE shape: a dedup MISS, a dedup HIT, and an OWNED string;
#   * the intern TABLE exhausted (`nent == NENT`) and the ARENA exhausted
#     (`abump + w > ARENA`), which are two different SENT paths;
#   * the PRIVATE region exhausted (`pbump + w > MEM`), a third;
#   * the RECORD table filled (`nrec == NREC`), a fourth;
#   * BREAKs and READs on OWNED records throughout, i.e. the safety line's guard
#     evaluated and FALSE;
#   * a window whose declared `nops` exceeds what the window can hold, so the
#     cursor guard is what stops the walk rather than the counter.
#
#   Note what is NOT here: a BREAK on a SHARED record. That is the bug, it
#   belongs on the adversarial rows, and `_no_share_break` refuses to write this
#   file if one creeps in -- as it did, on this window, on the first draft.
def degenerate_ops(rng):
    b = Builder(rng)
    b.emit(BREAK, 7).emit(READ, 9)             # nrec == 0, both fold SENT
    for k in range(NKEY):                      # 7 distinct interned strings
        b.short(k, 1 + k % 3)
    b.short(0, 1).short(1, 2)                  # two dedup HITs
    b.short(6, 3)                              # the 8th entry: the table fills
    b.short(2, 3)                              # a 9th distinct string: SENT
    b.long(3, 6).long(4, 6)                    # owned strings
    b.brk_owned().brk_owned()                  # the guard, evaluated and FALSE
    b.long(5, 6)                               # nrec == NREC after this
    b.long(5, 6).short(1, 1)                   # both fold SENT: record table full
    b.read(3).read(11)
    return b.ops


# `--sweep`: bands skipped by `harness/check.py` and `harness/measure.py` on the
# `sweep-` prefix (`.memory/05-layout.md`: that prefix IS the mechanism).
# Appended LAST so the matrix blobs stay byte-identical when a band is added.
#
# Band O -- the OPERATION axis: mix fixed, op count swept.
SWEEP_O_NOPS = tuple(range(8, 129, 4))
# Band D -- the DEDUP axis: op count fixed, the DEFINE fraction swept, so the
#           number of interning lookups rises while the number of operations
#           does not. It is the band that can falsify "the dedup scan is free".
SWEEP_D_FRACS = tuple(i / 20.0 for i in range(0, 13))
SWEEP_WINS = 8
SWEEP_ITERS = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true",
                    help="also write the sweep-* bands")
    a = ap.parse_args()
    rng = random.Random(SEED)

    print("p49 inputs ->", HERE)

    # small: one tile of windows, few ops. large: many windows, many ops.
    body, stride = tiled(rng, 8, 24, 0.55, 0.20)
    write("small.bin", 200000, stride, body)

    body, stride = tiled(rng, 64, 120, 0.55, 0.20)
    write("large.bin", 20000, stride, body)

    # `nops` is deliberately OVERSTATED by 9 here, so the cursor guard
    # `len - p < 2` is what stops the walk rather than the counter. Every rung
    # stops in the same place and the file is a full-agreement row.
    ops = degenerate_ops(rng)
    body = bytearray(encode(rng, ops))
    body[0:4] = struct.pack("<I", len(ops) + 9)
    body = bytes(body)
    write("degenerate.bin", 200000, len(body), body)

    # --- adversarial: the harm lives here and nowhere else -----------------
    for name, win in (("share", adv_share_window(rng)),
                      ("rehash", adv_rehash_window(rng)),
                      ("cascade", adv_cascade_window(rng)),
                      ("cowfull", adv_cowfull_window(rng)),
                      ("many", adv_many_window(rng))):
        body = encode(rng, win)
        write(f"adversarial-{name}.bin", 200000, len(body), body,
              check_share=False)

    # A window too small for the header: the driver guard `stride_w >= 4` skips
    # the loop, so every rung prints 0 after zero kernel calls.
    write("adversarial-stride3.bin", 200000, 3, bytes(range(30)),
          check_zero=False, check_share=False)

    if not a.sweep:
        return 0

    print("  --- sweep bands (skipped by check.py and measure.py) ---")
    for nops in SWEEP_O_NOPS:
        body, stride = tiled(rng, SWEEP_WINS, nops, 0.55, 0.20)
        write(f"sweep-o{nops:03d}.bin", SWEEP_ITERS, stride, body)
    for frac in SWEEP_D_FRACS:
        body, stride = tiled(rng, SWEEP_WINS, 96, 0.30 + frac, 0.20)
        write(f"sweep-d{int(round(frac * 100)):03d}.bin", SWEEP_ITERS, stride,
              body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
