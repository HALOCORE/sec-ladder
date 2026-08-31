#!/usr/bin/env python3
"""p25-realloc-growth: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p25 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p27, p29, p32, p34 and p35
                  use, and NOT p02's before/after shape. p25's two vectors are
                  LOCALS of the kernel and both are freed before the call
                  returns, so no buffer crosses the signature and there is
                  nothing for an `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's, p29's, p32's and
                  p34's denomination. See the property's docstring for which way
                  it errs.
    sanitizer     **DERIVED, by SIMULATING THE BUGGY RUNG, and the derivation is
                  one that CAN FIRE.** ⚠⚠ `TASK_157` deliverable 2 asked for the
                  question to be decided FIRST and written down: *Python has no
                  dangling pointers and no `realloc`, so is the harm
                  representable at all?* **THE ANSWER IS YES, and
                  `sanitizer_expect` is derived rather than declared.** What
                  makes it representable is that the harm here is not about a
                  POINTER, it is about a BLOCK: `realloc` retires the old block
                  as a side effect of growth, and `Vec.grow` below models exactly
                  that -- the old `Block` is marked `retired` and the bytes are
                  COPIED into a new one, which is what `realloc` does. Every
                  read the buggy rung performs goes through `Heap.touch`, which
                  raises `_Escape` the moment it reaches a retired block.
                  ⚠ **Being representable is not the same as being live**, which
                  is `.memory/03-measurement.md` entry 19's point, so
                  `detector_selftest()` is the must-fire arm and `selfcheck()`
                  runs it on every gate invocation.

    ⚠⚠ **THE DERIVED COLUMN IS ASan's SEMANTICS AND NOT glibc's, DELIBERATELY.**
    `Heap.grow` retires the old block on EVERY growth of an existing block, which
    is what ASan's allocator does; glibc extends a small block in place until it
    runs out of the chunk it already has, so under glibc only some of these
    reads touch storage the allocator has taken back. The gate's `sanitizer_expect`
    column is compared against an **ASan** build, so modelling ASan is what makes
    the column checkable; and it is the CONSERVATIVE direction -- every read this
    file calls stale is a read the C standard already calls undefined
    (C11 7.22.3.5p4, DR 400: the old pointer is indeterminate after `realloc`
    returns **whether or not the block moved**). ../c/kernel.h has the argument
    and ../NOTES.md 2 reports the plain-build divergence separately, because
    **that** is the unbiased evidence.

    ⚠⚠ `selfcheck()` ALSO enforces `p25`'s structural constraint mechanically:
    **no NON-adversarial window may read through an interior pointer whose token
    vector has been reallocated since the SAVE.** `inputs/gen.py` cannot emit one
    and `controls/no_stale.py` censuses the whole directory.

TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE.
`TASK_136`'s model was a line-by-line transliteration of its own kernel -- same
variable names, same guard -- which satisfies check.py's model-sandbox rule
mechanically and defeats it in substance. p25's two implementations disagree
about what a dynamic array IS:

  * the **simulation** (`_sim_window`) is BLOCK-BASED. A `Vec` owns a `Block`
    with identity; growing it allocates a NEW `Block`, copies the bytes across
    and marks the old one `retired`; a saved reference is `(block, index)` and
    keeps naming the block it was taken from. It is the only one of the two that
    can represent the bug, and the only one the detector watches.
  * the **helper** `parse_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs and **HAS NO
    BLOCKS, NO CAPACITY AND NO ALLOCATOR**. It carries two `Seq<u8>`s and a saved
    INTEGER index, exactly as `run` does, because in the CHECKED semantics the
    answer does not depend on where the bytes live: `realloc` copies, so the
    element the saved index names is the same element before and after a growth.
    ⚠ **That is a real independence and not a cosmetic one** -- R1's bug is
    precisely that a third representation, the ADDRESS the interior pointer
    holds, can fall out of step with the two the others agree about.

    `parse_fold` is **iterative where the Verus function is recursive**, for
    p11's, p14's, p27's, p29's, p32's and p34's reason: `run` recurses once per
    operation and a window may declare more operations than CPython's recursion
    limit allows.

`selfcheck()` runs them against each other, runs the must-fire arm, and runs the
no-stale census on the input it was handed.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to touch retired storage on every input whose
window grows the token vector while a saved pointer is live; the gate records
that behaviour in its adversarial table rather than requiring it to vanish
(`.memory/02-bench-rules.md`).
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nops:u32
OPSZ = 2                  # opcode byte + operand byte
SEEDCAP = 4               # must equal every rung's SEED
MAXCAP = 64               # must equal every rung's MAXCAP
SENT = 251                # must equal every rung's SENT

PUSHT, PUSHS, SAVE, READ = 0, 1, 2, 3


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- blocks with identity. See the module docstring.
# --------------------------------------------------------------------------
class Block:
    """ONE HEAP BLOCK. Identity is what this pattern is about: an interior
    pointer is a reference to one of these plus an offset, and `retired` records
    whether `realloc` has handed the storage back to the allocator.

    **The storage (`mem`) is deliberately NOT cleared when the block is
    retired** -- a retired block still holds its bytes until something reuses
    it, which is exactly why R1's stale READ returns a plausible value rather
    than an obvious one."""

    __slots__ = ("mem", "cap", "retired", "bid")

    def __init__(self, bid, cap):
        self.bid = bid
        self.cap = cap
        self.mem = bytearray(cap)
        self.retired = False


class _Escape(Exception):
    """Raised the instant the simulated BUGGY rung reads through a reference into
    a retired block.

    ⚠ **It exists so the detector can REPORT rather than CRASH**, which is
    `TASK_157` deliverable 2's requirement and `TASK_145_REPORT` §4b's finding on
    p32: a must-fire arm whose failure mode is an exception loses the diagnostic.
    The buggy run's RESULT is discarded (`Model._window` keeps only its `uaf`
    flag), so abandoning the window at the first stale read costs nothing and is
    what a detector, rather than an interpreter, does."""


class Heap:
    """The heap, as this pattern uses it: a set of blocks, each of which the
    allocator either owns or has taken back.

    ⚠ `grow` is `realloc`, and the two halves of it are both load-bearing:
    the bytes are **COPIED** into the new block -- which is why the CHECKED
    answer is the same whether or not the block moved, and therefore why
    `parse_fold` needs no allocator at all -- and the old block is **RETIRED**,
    which is the whole of R1's harm. ⚠⚠ It retires on EVERY growth of an
    existing block, which is ASan's allocator and not glibc's; the module
    docstring says why that is the checkable choice and the conservative one."""

    def __init__(self):
        self.blocks = []
        self.uaf = False
        self.uaf_sites = []

    def alloc(self, cap):
        b = Block(len(self.blocks), cap)
        self.blocks.append(b)
        return b

    def grow(self, old, newcap):
        """`realloc(old, newcap)`: a new block, the old bytes copied forward, and
        the old block handed back."""
        b = self.alloc(newcap)
        b.mem[:len(old.mem)] = old.mem
        old.retired = True
        return b

    # -- the use-after-free detector ---------------------------------------
    def touch(self, site, blk, idx):
        """Record whether ONE read the BUGGY rung performs reaches a block whose
        storage has been handed back.

        ⚠ **This is a check about the BLOCK the rung reaches, not about the
        simulation's own bookkeeping** -- `.memory/03-measurement.md` entry 19's
        rule. The caller hands over the block the saved reference names; nothing
        here consults a capacity, a length or an index-versus-length test, and
        the guard is false for every block the CHECKED semantics can reach.
        Raises `_Escape` so the caller stops rather than continuing to interpret
        a program the allocator no longer owns."""
        if not blk.retired:
            return blk.mem[idx]
        self.uaf = True
        self.uaf_sites.append(f"{site} at offset {idx} of block {blk.bid}, "
                              f"retired by a realloc")
        raise _Escape(self.uaf_sites[-1])


class Vec:
    """One growable byte vector, with the capacity discipline every rung
    implements: accept while `n < MAXCAP`, and `realloc` to double the capacity
    when `n == cap`.

    ⚠ `MAXCAP` is `SEEDCAP * 2**k`, so the capacity sequence is 4, 8, 16, 32, 64
    and the acceptance guard fires exactly at `n == MAXCAP`. **That equivalence
    is why the four Rust rungs can spell the whole discipline as
    `if v.len() < MAXCAP { v.push(a) }`** -- with no capacity variable at all --
    and still be the same program. `../NOTES.md` 5 states it as an obligation the
    rungs are matched against rather than as a coincidence."""

    def __init__(self, heap):
        self.heap = heap
        self.blk = None
        self.n = 0
        self.cap = 0

    def push(self, a):
        """`True` if the push was accepted. Sets `self.grew` when an EXISTING
        block was retired -- the first allocation retires nothing."""
        self.grew = False
        if self.n >= MAXCAP:
            return False
        if self.n == self.cap:
            newcap = self.cap * 2 if self.cap else SEEDCAP
            if self.blk is None:
                self.blk = self.heap.alloc(newcap)
            else:
                self.blk = self.heap.grow(self.blk, newcap)
                self.grew = True
            self.cap = newcap
        self.blk.mem[self.n] = a
        self.n += 1
        return True


def _sim_window(buf, off, ln, harden):
    """`(result, read_through_retired_storage)` for one window, simulated with
    blocks that have identity.

    `harden` selects the CHECKED semantics (R1h and R2-R5) or the BUGGY one
    (R1): it is exactly whether the READ asks which block the current base is
    before dereferencing the saved reference. That single boolean IS the safety
    line, and it is the knob `detector_selftest()` turns."""
    if ln < HDR:
        return 0, False
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return 0, False
    heap = Heap()
    toks, strs = Vec(heap), Vec(heap)
    curblk, curi = None, 0
    acc, p = 0, HDR
    try:
        for _ in range(nops):
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            op = c % 4
            if op == PUSHT:
                v = a if toks.push(a) else SENT
            elif op == PUSHS:
                v = a if strs.push(a) else SENT
            elif op == SAVE:
                if toks.n > 0:
                    curi = a % toks.n
                    curblk = toks.blk
                    v = 2
                else:
                    v = SENT
            else:
                if curblk is None:
                    v = SENT
                elif harden and curblk is not toks.blk:
                    # THE SAFETY LINE: the container relocated, so re-derive from
                    # the CURRENT base. `realloc` copied, so this is the byte the
                    # saved reference named.
                    v = toks.blk.mem[curi]
                else:
                    v = heap.touch("*cur", curblk, curi)
            acc = (acc * 31 + v) & MASK
    except _Escape:
        # The buggy rung has read storage the allocator has taken back; its
        # answer past this point is not a thing this simulation can compute, and
        # nobody reads it (`Model._window` keeps only the flag).
        return (acc * 31 + (toks.n + strs.n)) & MASK, True
    return (acc * 31 + (toks.n + strs.n)) & MASK, heap.uaf


def window_stale(buf, off, ln):
    """`True` if the window at `off` reads through an interior pointer whose
    token vector has been reallocated since the SAVE.

    Used by `stale_free_problems` below and by `controls/no_stale.py`. It is the
    BUGGY simulation's flag, so the two can never drift apart."""
    return _sim_window(buf, off, ln, False)[1]


# --------------------------------------------------------------------------
# THE MUST-FIRE ARM. `selfcheck()` runs it, so the gate re-derives it once per
# input on every run -- not once, by whoever wrote it.
# --------------------------------------------------------------------------
# Three windows, written out as bytes so they depend on nothing in `inputs/`.
# None is ever fed to a rung. Op encoding: c % 4 = 0 PUSHT, 1 PUSHS, 2 SAVE,
# 3 READ. The operand byte is the pushed byte on a push and `curi` selector on a
# SAVE.
def _probe(ops):
    out = bytearray(len(ops).to_bytes(4, "little"))
    for op, a in ops:
        out.append(op)
        out.append(a)
    return bytes(out)


# PUSHT x4 (cap 4, exactly full), SAVE, READ -- no growth after the SAVE.
_PROBE_NOGROW = _probe([(PUSHT, 9), (PUSHT, 8), (PUSHT, 7), (PUSHT, 6),
                        (SAVE, 1), (READ, 0)])
# The same, plus one PUSHT that forces 4 -> 8 between the SAVE and the READ.
_PROBE_GROW = _probe([(PUSHT, 9), (PUSHT, 8), (PUSHT, 7), (PUSHT, 6),
                      (SAVE, 1), (PUSHT, 5), (READ, 0)])
# Growth after the SAVE but NO read through the saved reference: nothing is
# dereferenced, so nothing fires. The other half of the pair.
_PROBE_GROW_NOREAD = _probe([(PUSHT, 9), (PUSHT, 8), (PUSHT, 7), (PUSHT, 6),
                             (SAVE, 1), (PUSHT, 5)])


def detector_selftest():
    """Show that `Heap.touch` CAN FIRE, and that THE SAFETY LINE is what stops it.

    Six cells, and the pairing is the point -- the same window under both
    semantics:

      * `_PROBE_NOGROW`      hardened -> silent   buggy -> silent
      * `_PROBE_GROW`        hardened -> silent   buggy -> **fires**
      * `_PROBE_GROW_NOREAD` hardened -> silent   buggy -> silent

    ⚠ The two silent-under-buggy arms are the controls that stop a detector which
    fires on everything from passing this test, and they separate the two halves
    of the harm condition: `_PROBE_NOGROW` has the READ and no growth,
    `_PROBE_GROW_NOREAD` has the growth and no READ, and only the window with
    both fires."""
    problems = []
    arms = (("SAVE READ, no growth", _PROBE_NOGROW, False),
            ("SAVE PUSHT READ", _PROBE_GROW, True),
            ("SAVE PUSHT, no read", _PROBE_GROW_NOREAD, False))
    for shape, blob, want_fire in arms:
        _, quiet = _sim_window(blob, 0, len(blob), True)
        if quiet:
            problems.append(
                f"the stale-read detector FIRED on the `{shape}` probe under the "
                f"HARDENED semantics, which no shipped rung can do -- the probe "
                f"or `Heap.touch` is wrong")
        _, loud = _sim_window(blob, 0, len(blob), False)
        if loud != want_fire:
            if want_fire:
                problems.append(
                    f"MUST-FIRE ARM DEAD: the `{shape}` probe did NOT make the "
                    f"stale-read detector fire under the BUGGY semantics. "
                    f"`sanitizer_expect` is then a declaration wearing a "
                    f"derivation's clothes -- do not quote this pattern's "
                    f"`fires` as DERIVED until it fires again")
            else:
                problems.append(
                    f"the detector fired on the `{shape}` probe under the BUGGY "
                    f"semantics, and that probe has no read through a "
                    f"reallocated vector -- the detector is firing on something "
                    f"other than the missing conjunct")
    return problems


def stale_free_problems(path, buf, stride, n_blob):
    """**No NON-adversarial window may read through an interior pointer whose
    token vector has been reallocated since the SAVE.**

    ⚠⚠ This is `p25`'s harm condition stated as a mechanical check on the
    SHIPPED blob rather than as an argument about the generator. ASan's allocator
    moves on every `realloc`, so such a window would make R1 report
    `heap-use-after-free` on a row whose `sanitizer_expect` is `clean`; and
    `harness/check.py` stage 2 requires every non-adversarial cell to agree with
    this file and with every other cell, which a rung reading retired storage
    cannot do reproducibly."""
    if os.path.basename(path).startswith("adversarial-"):
        return []
    if not (HDR <= stride <= n_blob):
        return []
    out = []
    for w in range(n_blob // stride):
        if window_stale(buf, w * stride, stride):
            out.append(f"window {w} reads through an interior pointer whose "
                       f"token vector was reallocated after the SAVE, so R1 "
                       f"would read retired storage -- that belongs on an "
                       f"`adversarial-*` row and nowhere else")
            break
    return out


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
        self.any_uaf = False
        self.nwin = 0
        self._work = 0
        self._win = []
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_reads_retired_storage) for the window at `off`.

        Implementation 1 of 2 -- blocks with identity; see the module docstring.
        The second element is computed under the BUGGY semantics, because the
        question it answers is what the rung with no safety line would do."""
        r_ok, _ = _sim_window(self.buf, off, self.stride, True)
        _, uaf = _sim_window(self.buf, off, self.stride, False)
        return r_ok, uaf

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
                r, uaf = self._win[k]
                if uaf:
                    self.any_uaf = True
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
            r, _uaf = self._win[k]
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
    # (../verus.rs `run`) and carries **no heap, no block and no capacity** --
    # two byte sequences and one saved integer index.
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
        toks, strs = [], []
        curi = None
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            m = c % 4
            if m == PUSHT:
                if len(toks) < MAXCAP:
                    toks.append(a)
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == PUSHS:
                if len(strs) < MAXCAP:
                    strs.append(a)
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == SAVE:
                if toks:
                    curi = a % len(toks)
                    acc = (acc * 31 + 2) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                if curi is None:
                    acc = (acc * 31 + SENT) & MASK
                else:
                    acc = (acc * 31 + toks[curi]) & MASK
        return (acc * 31 + (len(toks) + len(strs))) & MASK

    def parse_fold(self, buf, off, ln):
        """`parse_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"parse_fold": self.parse_fold}

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
        p27's, p29's, p32's and p34's denomination and p16's, p05's, p11's,
        p12's, p06's and p14's.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every matrix
        input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count: **each 2 window bytes is one OPERATION**, and every
            operation does a modulo, a compare chain and a multiply-add, while a
            push that crosses a capacity boundary also calls `realloc` and copies
            the whole vector.

        The under-count is bounded here in a way p34's is not: the number of
        `realloc` calls per window is at most `2 * log2(MAXCAP / SEEDCAP) + 2`,
        i.e. **at most 10 allocator calls per window whatever the input**, so the
        estimate cannot be made arbitrarily loose by an adversarial op stream. No
        `min_ir_per_work` is declared, so the harness default of 0.25 Ir per byte
        applies unchanged, and what it catches is the failure it exists to catch
        -- a kernel the optimiser collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**DERIVED by simulating the buggy rung, and the derivation FIRES.**

        `fires` on exactly the inputs whose visited windows read through an
        interior pointer after the token vector has been reallocated, `clean`
        everywhere else -- and `inputs/gen.py` puts such a window on three of the
        `adversarial-*` rows and nowhere else, which `stale_free_problems`
        re-checks on the shipped blob at every gate invocation.

        ⚠⚠ **`adversarial-nogrow` IS AN `adversarial-*` INPUT THAT DERIVES
        `clean`, AND IT IS THERE ON PURPOSE.** It has the SAVE and the READ and
        no growth between them, so nothing is retired and R1 is correct. Without
        it, "the adversarial rows fire" would be true of the filename rather than
        of the measurement.

        ⚠⚠ **WHAT MAKES THAT A MEASUREMENT AND NOT A RESTATEMENT.** The
        simulation runs each window under the semantics with the safety line
        DELETED, and the read goes through `Heap.touch`, which fires the instant
        it reaches a block the simulated allocator has taken back. Turning the
        safety line back on silences it, on the same window:
        `detector_selftest()` runs both halves of that pair plus two controls,
        and `selfcheck()` runs it once per input on every gate invocation.

        ⚠ **What it does NOT derive, said so nobody reads it as more.** It
        derives that the buggy rung READS RETIRED STORAGE, which is what ASan
        reports. It says nothing about UBSan, and it should not: p25's undefined
        behaviour is purely temporal -- every index either rung forms is inside
        the block it names at the moment it is formed -- so **UBSan is silent on
        every input at both optimisation levels on both compilers**, and that
        silence needs its own positive control rather than this one
        (../controls/detectors.py, RECAP trap 5). Miri's answer is derived one
        level up and needs no simulation: ../spec.md's `miri.reason` states what
        it finds on the SHIPPED unsafe rung."""
        return "fires" if self.any_uaf else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p25's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27, p29, p32 and p34. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # recorded in the adversarial table rather than required.
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
        """The block simulation vs the allocator-free spec that mirrors Verus,
        plus the must-fire arm that proves the detector is alive, plus the
        no-stale census on this input."""
        problems = list(detector_selftest())
        problems += stale_free_problems(self.path, self.buf, self.stride,
                                        self.n_blob)
        for c in self.sample_calls(8):
            want = self.parse_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != parse_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
