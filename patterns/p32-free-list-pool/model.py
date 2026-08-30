#!/usr/bin/env python3
"""p32-free-list-pool: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p32 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p27 and p29 use, and NOT
                  p02's before/after shape. p32's pool is a LOCAL of the kernel,
                  so no buffer crosses the signature and there is nothing for an
                  `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's and p29's
                  denomination. See the property's docstring for which way it
                  errs.
    sanitizer     **DERIVED, and it is derived by CHECKING rather than by
                  tabulating.** The simulation computes every index the buggy
                  rung would compute and records whether any of them escapes its
                  array. It never does -- see `sanitizer_expect` -- so every
                  input this pattern ships is `clean`, adversarial ones
                  included, and that is the row's detector-coverage result
                  rather than a concession. `controls/storage_arms.py` rebuilds
                  the same algorithm on `malloc` storage and measures which
                  harms become visible when the storage changes.

TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE.
`TASK_136`'s model was a line-by-line transliteration of its own kernel -- same
variable names, same guard -- which satisfies check.py's model-sandbox rule
mechanically and defeats it in substance, and is how its delete bug went
undetected. `p29`'s model is the good example: its simulation is a purely
functional BST whose USE test is a REACHABILITY WALK, not a liveness bit. p32
does the same thing one axis over:

  * the **simulation** (`_window`) has **NO GENERATION COUNTER AT ALL**. A block
    is a Python object with identity (`Block`); a HANDLE is a direct reference
    to that object; a slot's current tenant is `pool.live[slot]`, which ALLOC
    sets to a *newly constructed* `Block` and FREE sets to `None`. **A handle is
    current exactly when `handle is pool.live[handle.slot]`** -- Python object
    identity, which is the contract's own words (*"the handle must still name
    THIS incarnation of the block"*) with the counter deleted. The free list is
    a **successor MAP** `pool.succ`, walked with a visited set when the model
    needs to know whether it is still a simple list -- something no rung ever
    computes. The stored bytes live in `pool.mem`, which is never cleared,
    because the storage belongs to the program throughout and that is the
    pattern;
  * the **helper** `pool_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs, carrying
    the five parallel sequences `pool`, `nx`, `gen`, `rs`, `rg` plus the head
    and the alloc count exactly as the proof does, with integer generation
    compares.

    So the two implementations disagree about **what makes a handle stale** --
    an object is no longer the slot's tenant, or a counter no longer matches --
    and agree about the answer. That is not a decorative difference here: R1's
    bug is precisely that a third representation, a `(slot, generation)` pair
    the kernel issued and never re-checks, can fall out of step with both.

    `pool_fold` is **iterative where the Verus function is recursive**, for
    p11's, p14's, p27's and p29's reason: `run` recurses once per operation and
    a window may declare more operations than CPython's recursion limit allows.
    The functional simulation has no recursion at all.

`selfcheck()` runs them against each other, and also runs the simulation's own
out-of-range detector over the sampled windows.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input whose FREE, READ or
WRITE names a handle whose block has been recycled; the gate records that
disagreement in its behaviour table rather than requiring it to vanish
(`.memory/02-bench-rules.md`).

**Why the benign inputs never use a stale handle.** They cannot: the moment one
does, R1 returns a different number and the cell no longer agrees with any
other, and `harness/check.py` stage 2 requires every non-adversarial cell to
agree with this file *and with each other*. `inputs/gen.py` therefore emits op
streams in which every FREE/READ/WRITE names a register whose handle is still
current, and checks that property by running a copy of the model over every
window of every blob it writes. Both bug classes live on the `adversarial-*`
rows alone.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
M32 = (1 << 32) - 1
HDR = 4                   # nops:u32
OPSZ = 2                  # opcode byte + operand byte
SLOTS = 8                 # must equal every rung's SLOTS
BLK = 4                   # must equal every rung's BLK
NREG = 8                  # must equal every rung's NREG
NIL = 255                 # must equal every rung's NIL
SENT = 251                # must equal every rung's SENT


def _val_of(a):
    """A block's payload is a function of the operand that allocated it, in
    every rung: `a * 7 + 1` truncated to a byte. So a READ that returns a
    recycled block's payload returns a value no honest read of the handle's own
    incarnation could produce."""
    return (a * 7 + 1) & 0xFF


def _written(a):
    """What a WRITE stores, in every rung: `a * 13 + 3` truncated to a byte."""
    return (a * 13 + 3) & 0xFF


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- objects with identity. See the module docstring.
# --------------------------------------------------------------------------
class Block:
    """ONE INCARNATION of a pool slot. Identity is what this pattern is about:
    recycling a slot constructs a NEW `Block`, so a handle taken before the
    recycle names an object the slot no longer holds -- and the bytes it named
    are still there, occupied by somebody else."""

    __slots__ = ("slot",)

    def __init__(self, slot):
        self.slot = slot


class Pool:
    """The pool, with no generation counter anywhere.

    `mem` is the storage and it is never cleared -- that is the pattern. `live`
    maps a slot to the `Block` currently checked out of it, or `None` while the
    slot sits on the free list. `succ` is the free list's successor MAP and
    `head` its head; pushing a slot that is already the head makes `succ[h] == h`
    and the list SELF-LOOPS, exactly as the intrusive `nx[]` array does in every
    rung."""

    def __init__(self):
        self.mem = [[0] * BLK for _ in range(SLOTS)]
        self.live = [None] * SLOTS
        self.succ = {j: (j + 1 if j + 1 < SLOTS else None) for j in range(SLOTS)}
        self.head = 0
        self.nalloc = 0
        self.rel = [0] * SLOTS    # releases so far: the incarnation, counted
        self.oob = False          # did any index the BUGGY rung computes escape?

    # -- the free list, as a map ------------------------------------------
    def pop(self):
        s = self.head
        self.head = self.succ[s]
        return s

    def push(self, s):
        self.succ[s] = self.head
        self.head = s

    def list_is_simple(self):
        """Walk `succ` from `head` with a VISITED SET. No rung computes this and
        no rung can: the property it decides -- *the free list is a set of
        distinct slots* -- is what the safety line buys, and neither C nor Rust
        nor the proof ever states it. `selfcheck` and `inputs/gen.py` use it."""
        seen, t = set(), self.head
        while t is not None:
            if t in seen:
                return False
            seen.add(t)
            t = self.succ[t]
        return True

    # -- the operations ----------------------------------------------------
    def alloc(self, a):
        """Take a block. Returns `(handle, fold)`; `handle` is None when the
        pool is empty."""
        if self.head is None:
            return None, SENT
        s = self.pop()
        # the OWNER TAG and the PAYLOAD; the rest of the block is whatever the
        # previous tenant left, which is what makes the storage an arena
        self.mem[s][0] = a
        self.mem[s][1] = _val_of(a)
        blk = Block(s)
        self.live[s] = blk
        self.nalloc += 1
        # what every rung folds: the SLOT and the incarnation it was issued at.
        # The simulation has no counter, so it counts the incarnation the only
        # way it can -- how many times this slot has been RELEASED so far. The
        # `& M32` is the rungs' `wrapping_add(1)` on a `u32` generation; it is
        # unreachable on any window this project can hold (../spec.md) and is
        # written so the two implementations agree by construction and not by
        # the size of the inputs.
        return blk, (s + 8 * (self.rel[s] & M32)) & MASK

    def free(self, blk):
        self.live[blk.slot] = None
        self.rel[blk.slot] = self.rel[blk.slot] + 1
        self.push(blk.slot)
        return 1

    def read(self, blk):
        self._touch(blk.slot)
        return self.mem[blk.slot][1]

    def write(self, blk, a):
        self._touch(blk.slot)
        self.mem[blk.slot][1] = _written(a)
        return 3

    # -- the out-of-range detector ----------------------------------------
    def _touch(self, s):
        """Record whether the index the BUGGY rung would compute escapes the
        pool. It never does -- `regs[r]` is NIL or a real slot in both rungs --
        and this is what makes `sanitizer_expect` a derivation rather than a
        tabulation."""
        if not (0 <= s < SLOTS and 0 <= s * BLK + 1 < SLOTS * BLK):
            self.oob = True


def _sim_window(buf, off, ln, harden):
    """`(result, out_of_range)` for one window, simulated with objects.

    `harden` selects the CHECKED semantics (R1h and R2-R5) or the BUGGY one
    (R1). The model's own answer is the checked one; the buggy one exists so
    `inputs/gen.py` can ask whether a stream would make the two disagree."""
    if ln < HDR:
        return 0, False
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return 0, False
    pool = Pool()
    reg = [None] * NREG          # a handle register holds a Block, or nothing
    acc, p = 0, HDR
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        c = buf[off + p]
        a = buf[off + p + 1]
        p += OPSZ
        r = a % NREG
        op = c % 4
        if op == 0:
            blk, fold = pool.alloc(a)
            if blk is not None:
                reg[r] = blk
            acc = (acc * 31 + fold) & MASK
        else:
            blk = reg[r]
            # THE SAFETY LINE, expressed WITHOUT A COUNTER: is the object this
            # register holds still the slot's tenant?
            current = blk is not None and pool.live[blk.slot] is blk
            if blk is None:
                acc = (acc * 31 + SENT) & MASK
            elif harden and not current:
                acc = (acc * 31 + SENT) & MASK
            elif op == 1:
                acc = (acc * 31 + pool.free(blk)) & MASK
            elif op == 2:
                acc = (acc * 31 + pool.read(blk)) & MASK
            else:
                acc = (acc * 31 + pool.write(blk, a)) & MASK
    return (acc * 31 + pool.nalloc) & MASK, pool.oob


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.any_oob = False
        self.nwin = 0
        self._work = 0
        self._win = []
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_computes_an_out_of_range_index) for the window at `off`.

        Implementation 1 of 2 -- objects with identity; see the module
        docstring. The second element is computed under the BUGGY semantics,
        because the question it answers is what the rung with no safety line
        would do."""
        r_ok, _ = _sim_window(self.buf, off, self.stride, True)
        _, oob = _sim_window(self.buf, off, self.stride, False)
        return r_ok, oob

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            self._work = self.stride
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, oob = self._win[k]
                if oob:
                    self.any_oob = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            if self._win[k] is None:
                self._win[k] = self._window(k * self.stride)
            r, _oob = self._win[k]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- the second, independent implementation ----------------------------
    # This is what the derived `ensures` is evaluated against, so it must not be
    # the simulation in disguise. It mirrors the *Verus* spec function
    # (../verus.rs `run`) and keeps the pool in five parallel sequences with an
    # integer generation counter beside them, which is the RUNGS' representation
    # and not the simulation's.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, ln):
        """`run` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring."""
        nops = self._u32_at(buf, off)
        if nops == 0:
            return 0
        pool = [0] * (SLOTS * BLK)
        nx = [(j + 1 if j + 1 < SLOTS else NIL) for j in range(SLOTS)]
        gen = [0] * SLOTS
        rs = [NIL] * NREG
        rg = [0] * NREG
        head = 0
        nalloc = 0
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            r = a % NREG
            m = c % 4
            if m == 0:
                if head == NIL:
                    acc = (acc * 31 + SENT) & MASK
                else:
                    s = head
                    head = nx[s]
                    pool[s * BLK] = a
                    pool[s * BLK + 1] = _val_of(a)
                    rs[r] = s
                    rg[r] = gen[s]
                    nalloc += 1
                    acc = (acc * 31 + s + 8 * gen[s]) & MASK
            else:
                h = rs[r]
                g = rg[r]
                if h == NIL:
                    acc = (acc * 31 + SENT) & MASK
                elif gen[h] != g:
                    acc = (acc * 31 + SENT) & MASK
                elif m == 1:
                    gen[h] = (gen[h] + 1) & M32
                    nx[h] = head
                    head = h
                    acc = (acc * 31 + 1) & MASK
                elif m == 2:
                    acc = (acc * 31 + pool[h * BLK + 1]) & MASK
                else:
                    pool[h * BLK + 1] = _written(a)
                    acc = (acc * 31 + 3) & MASK
        return (acc * 31 + nalloc) & MASK

    def pool_fold(self, buf, off, ln):
        """`pool_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"pool_fold": self.pool_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "byte"

    @property
    def work_unit_bits(self):
        """One unit is one window byte. 8 bits."""
        return 8

    @property
    def work_per_call(self):
        """`stride` -- the bytes of the window, from the file alone, which is
        p27's and p29's denomination and p16's, p05's, p11's, p12's, p06's and
        p14's.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count: **each 2 window bytes is one OPERATION**, and every
            operation does at least a modulo, two array reads, a compare and a
            multiply-add on the accumulator, while ALLOC and FREE also
            read-modify-write the free list.

        p32's under-count is far smaller than p27's or p29's, because an
        operation here is O(1) rather than a tree walk -- there is no allocator
        call and no loop inside an op. It is still an under-count on every
        shipped input.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. What it catches is the failure it exists to
        catch -- a kernel the optimiser collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**`clean` on every input, adversarial ones included, and it is
        DERIVED.**

        The simulation runs each window under the BUGGY semantics and records
        whether any index the buggy rung computes escapes its array
        (`Pool._touch`). None ever does, and the reason is structural: `regs[r]`
        is `NIL` or a real slot in both rungs, `freehead` is `NIL` or a real
        slot, and `nx[]` only ever holds values drawn from those two -- so
        `pool[h * BLK + 1]`, `gen[h]` and `nx[h]` are in bounds in every run of
        every rung. **R1 executes no undefined behaviour at all.**

        ⚠⚠ **THAT IS THE ROW'S DETECTOR-COVERAGE RESULT AND NOT A CONCESSION.**
        The storage is a pool the program owns from the first instruction to the
        last, so there is no `free` for ASan to record, no drop for Rust to
        insert, no deallocation for Miri to see, and no `PointsTo` for a proof to
        consume -- while the answer on three of this pattern's four adversarial
        inputs is WRONG, and on one of them two handles alias one block.
        `controls/storage_arms.py` rebuilds the SAME algorithm with per-block
        `malloc`/`free` storage and measures exactly which of those harms become
        visible when the storage changes: two do, and the use-after-RECYCLE one
        stays bit-identical and silent in both. ../NOTES.md 2."""
        return "fires" if self.any_oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p32's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27 and p29. `slb_load` rejecting a
        # short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # recorded in the adversarial table rather than required -- and on this
        # pattern it is 0 there too, because R1 cannot crash.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The object-identity simulation vs the five sequences that mirror
        Verus, plus the simulation's own out-of-range detector."""
        problems = []
        for c in self.sample_calls(8):
            want = self.pool_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != pool_fold() {want} "
                    f"at off={c['off']}")
                break
        if self.any_oob:
            problems.append("the simulation says the BUGGY rung computes an "
                            "out-of-range index on this input, which p32's "
                            "whole argument says is impossible -- check "
                            "Pool._touch and c/kernel.c together")
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
