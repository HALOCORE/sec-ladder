#!/usr/bin/env python3
"""p49-interned-pool: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p49 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p27, p29, p32, p34, p35 and
                  p25 use, and NOT p02's before/after shape. p49's pool is a
                  LOCAL of the kernel and nothing crosses the signature, so there
                  is nothing for an `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's, p29's, p32's,
                  p34's and p25's denomination. See the property's docstring for
                  which way it errs.
    sanitizer     ⚠⚠ **DECLARED `clean` ON EVERY INPUT, ADVERSARIAL INCLUDED,
                  AND THAT IS THIS ROW'S HEADLINE RATHER THAN A GAP.**
                  `c/kernel.c` allocates nothing, frees nothing, holds no
                  pointer, and forms no index outside `mem[0 .. MEM)`
                  (`../c/kernel.h` has the four-line proof), so there is no
                  undefined behaviour for ASan, UBSan, Miri or the glibc
                  allocator to report -- on the buggy rung, on the adversarial
                  inputs, at either optimisation level, on either compiler.
                  **The checksum is the only instrument this row has.**
                  ⚠ `.memory/03-measurement.md` entry 19: *DECLARING IS HONEST;
                  a derivation that cannot fire is not.* So `sanitizer_expect`
                  is a declaration with an argument beside it, `p01`'s, `p08`'s,
                  `p22`'s and `p47`'s shape -- and the derivation this file DOES
                  carry is a different one, below, which fires.

--------------------------------------------------------------------------
THE INSTRUMENT, AND WHY IT IS NOT THE SAFETY LINE WEARING A DISGUISE
--------------------------------------------------------------------------
Every other pattern in this tree has a detector as a second witness. p49 has
none, so this file carries the whole result and owes a derivation that can fire.
`Detector` asks TWO questions at each write the BUGGY rung performs, and both
are questions about **integers the caller hands over** -- a list of buffer ids
-- rather than about how this file stores a record:

  * `aliased`   -- does ANOTHER RECORD name the buffer being written?
                   The harm in `adversarial-share`, `-cascade` and `-many`.
  * `published` -- is the buffer still reachable from the DEDUP TABLE, so that a
                   LATER record can be handed it? The harm in
                   `adversarial-rehash`, where at the moment of the write no
                   other record names the buffer at all and the corruption
                   crosses the ownership boundary FORWARDS IN TIME.

`published` implies `aliased` is possible later; `aliased` does not imply
`published` in general and does here, because in this kernel a record can only
come to share a buffer through the table. ⚠ **Said plainly rather than dressed
up: `published` coincides extensionally with `rshd[t] == 1`, which is what the
safety line reads.** What makes it evidence rather than a restatement is that it
is computed from the TABLE'S CONTENTS and the RECORD LIST, neither of which
carries an ownership flag, and that `detector_selftest()` exhibits an input on
which the two questions ANSWER DIFFERENTLY -- an interned record nobody else
names. A predicate with three distinguishable outcomes on three probes is not a
predicate that cannot fire.

TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE.
`TASK_136`'s model was a line-by-line transliteration of its own kernel, which
satisfies check.py's model-sandbox rule mechanically and defeats it in
substance. p49's two implementations disagree about what a BUFFER IS:

  * the **simulation** (`_sim_window`) is OBJECT-BASED and **contains no offset
    arithmetic at all**. A buffer is a Python object with a stable id and its own
    `bytearray`; the intern table is a `dict` from the string `(key, w)` to one
    of those objects; a record is a `(buffer, shared)` pair. Storage pressure is
    two integers, `arena_used` and `priv_used`, because a bump allocator's only
    observable is how much room is left. It is the only one of the two that can
    represent the harm, and it is the one the detector watches.
  * the **helper** `intern_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs and is
    entirely OFFSET-BASED: one flat byte sequence, `roff`/`rlen`/`rshd` as
    parallel integer sequences, and a dedup table of `(ekey, elen, eoff)`. It has
    no notion of a buffer as a thing at all.

  ⚠ **That is a real independence and not a cosmetic one.** R1's bug is exactly
  that a write reaches storage the writer does not own, and the two formulations
  disagree about what "storage" even is -- an object with identity in one, a
  range of a flat array in the other. `intern_fold` is **iterative where the
  Verus function is recursive**, for p11's, p14's, p27's, p29's, p32's and p34's
  reason: a window may declare more operations than CPython's recursion limit
  allows.

⚠⚠ `selfcheck()` ALSO enforces p49's structural constraint mechanically:
**no NON-adversarial input may execute a BREAK on a record whose buffer is
SHARED.** That is the corollary of the row's headline -- the safety line's TRUE
branch cannot execute on an input R1 and R1h agree about -- and it is checked on
the SHIPPED blob rather than assumed. `inputs/gen.py` refuses to write one and
`controls/no_share_break.py` censuses every blob in the directory.
⚠ Note what the constraint is stated ABOUT: the FLAG, not the corruption. R1h's
copy-on-write also consumes private storage and clears the flag, and the
epilogue folds the flag, so a BREAK on a shared record moves the checksum even
when no other record was naming the buffer.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input whose window BREAKs
a shared record; the gate records that behaviour in its adversarial table rather
than requiring it to vanish (`.memory/02-bench-rules.md`).
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
MEM = 64                  # must equal every rung's MEM
ARENA = 20                # must equal every rung's ARENA
NENT = 8                  # must equal every rung's NENT
NREC = 12                 # must equal every rung's NREC
NKEY = 7                  # must equal every rung's NKEY
MAXW = 6                  # must equal every rung's MAXW
THRESH = 4                # must equal every rung's THRESH
SENT = 251                # must equal every rung's SENT

DEFINE_A, DEFINE_B, BREAK, READ = 0, 1, 2, 3


def cbyte(key, j):
    """A content byte, in every rung. The string a record holds is
    `cbyte(key,0) .. cbyte(key,w-1)`, so the pair `(key, w)` names the string
    and nothing else does -- which is why the kernel's `(ekey, elen)` comparison
    is an EXACT content comparison and not a hash with a collision story."""
    return (key * 7 + j * 13 + 1) & 0xFF


def content(key, w):
    return bytes(cbyte(key, j) for j in range(w))


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- buffers as OBJECTS. See the module docstring.
# --------------------------------------------------------------------------
class Buf:
    """ONE BUFFER. Identity is what this pattern is about: a record holds a
    direct reference to one of these, and two records holding the SAME one is
    what deduplication MEANS -- correct, intended, and the contract rather than
    the bug. `bid` is a stable integer so the detector can be asked its question
    without being handed a Python object."""

    __slots__ = ("bid", "data")

    def __init__(self, bid, data):
        self.bid = bid
        self.data = bytearray(data)


class Rec:
    """ONE RECORD: the buffer it names, and whether that buffer is its own."""

    __slots__ = ("buf", "shared")

    def __init__(self, buf, shared):
        self.buf = buf
        self.shared = shared


class Detector:
    """The row's only instrument, and it is asked about VALUES.

    ⚠ `.memory/03-measurement.md` entry 19: *whatever a model DERIVES rather
    than DECLARES owes an arm that SHOWS IT FIRING.* `detector_selftest()` is
    that arm and `selfcheck()` runs it once per input on every gate invocation.
    Nothing in this class knows how the simulation stores a record, a buffer or
    an ownership flag: it is handed the id of the buffer about to be written,
    the ids the OTHER records name, and the ids the dedup table still holds."""

    def __init__(self):
        self.aliased = False
        self.published = False
        self.sites = []

    def write(self, site, target, other_bids, table_bids):
        """Record what ONE write the BUGGY rung performs actually reaches."""
        a = target in other_bids
        p = target in table_bids
        if a:
            self.aliased = True
        if p:
            self.published = True
        if a or p:
            self.sites.append(
                f"{site}: buffer {target} is "
                + (" and ".join(x for x in
                                ("named by another record" if a else "",
                                 "still in the dedup table" if p else "") if x)))
        return a, p


def _sim_window(buf, off, ln, harden, det=None):
    """`(result, detector)` for one window, simulated with buffer OBJECTS.

    `harden` selects the CHECKED semantics (R1h and R2-R5) or the BUGGY one
    (R1): it is exactly whether the cycle-breaker un-shares before it writes.
    That single boolean IS the safety line, and it is the knob
    `detector_selftest()` turns.

    ⚠ There is no offset arithmetic anywhere in this function. Storage pressure
    is two integers -- how many bytes of the arena and of the private region are
    spent -- because that is a bump allocator's only observable."""
    if det is None:
        det = Detector()
    if ln < HDR:
        return 0, det
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return 0, det
    table = {}                 # (key, w) -> Buf     THE DEDUP TABLE
    recs = []                  # [Rec]
    nbuf = 0                   # next buffer id
    arena_used, priv_used = 0, 0
    acc, p = 0, HDR
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        c = buf[off + p]
        a = buf[off + p + 1]
        p += OPSZ
        w = 1 + a % MAXW
        key = a % NKEY
        op = c % 4
        if op in (DEFINE_A, DEFINE_B):
            if len(recs) >= NREC:
                v = SENT
            elif w < THRESH:
                # INTERN. A hit hands back the buffer an earlier record holds.
                hit = table.get((key, w))
                if hit is not None:
                    recs.append(Rec(hit, True))
                    v = a
                elif len(table) >= NENT or arena_used + w > ARENA:
                    v = SENT
                else:
                    b = Buf(nbuf, content(key, w))
                    nbuf += 1
                    table[(key, w)] = b
                    arena_used += w
                    recs.append(Rec(b, True))
                    v = a
            else:
                if priv_used + w > MEM - ARENA:
                    v = SENT
                else:
                    b = Buf(nbuf, content(key, w))
                    nbuf += 1
                    priv_used += w
                    recs.append(Rec(b, False))
                    v = a
        elif op == BREAK:
            if not recs:
                v = SENT
            else:
                t = a % len(recs)
                r = recs[t]
                if not harden:
                    det.write(f"BREAK on record {t}", r.buf.bid,
                              [q.buf.bid for i, q in enumerate(recs) if i != t],
                              [b.bid for b in table.values()])
                if harden and r.shared:
                    # THE SAFETY LINE: un-share before writing.
                    if priv_used + len(r.buf.data) > MEM - ARENA:
                        acc = (acc * 31 + SENT) & MASK
                        continue
                    nb = Buf(nbuf, r.buf.data)
                    nbuf += 1
                    priv_used += len(nb.data)
                    r.buf = nb
                    r.shared = False
                r.buf.data[0] = 0
                v = 2
        else:
            if not recs:
                v = SENT
            else:
                r = recs[a % len(recs)]
                v = 0
                for x in r.buf.data:
                    v = (v * 31 + x) & MASK
        acc = (acc * 31 + v) & MASK
    for r in recs:
        for x in r.buf.data:
            acc = (acc * 31 + x) & MASK
        acc = (acc * 31 + (1 if r.shared else 0)) & MASK
    return (acc * 31 + len(recs)) & MASK, det


def window_share_break(buf, off, ln):
    """Does the window at `off` execute a BREAK on a record whose buffer is
    SHARED -- i.e. does the safety line's guard ever take its TRUE branch?

    Used by `no_share_break_problems` below, by `inputs/gen.py` and by
    `controls/no_share_break.py`. It walks the CHECKED semantics, which is the
    one the flag belongs to."""
    if ln < HDR:
        return False, 0, 0
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return False, 0, 0
    table, recs, nbuf = {}, [], 0
    arena_used, priv_used = 0, 0
    p = HDR
    gt, gf = 0, 0
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        c, a = buf[off + p], buf[off + p + 1]
        p += OPSZ
        w, key, op = 1 + a % MAXW, a % NKEY, c % 4
        if op in (DEFINE_A, DEFINE_B):
            if len(recs) >= NREC:
                continue
            if w < THRESH:
                hit = table.get((key, w))
                if hit is not None:
                    recs.append(Rec(hit, True))
                elif len(table) < NENT and arena_used + w <= ARENA:
                    b = Buf(nbuf, content(key, w))
                    nbuf += 1
                    table[(key, w)] = b
                    arena_used += w
                    recs.append(Rec(b, True))
            elif priv_used + w <= MEM - ARENA:
                b = Buf(nbuf, content(key, w))
                nbuf += 1
                priv_used += w
                recs.append(Rec(b, False))
        elif op == BREAK and recs:
            r = recs[a % len(recs)]
            if r.shared:
                gt += 1
                if priv_used + len(r.buf.data) > MEM - ARENA:
                    continue
                nb = Buf(nbuf, r.buf.data)
                nbuf += 1
                priv_used += len(nb.data)
                r.buf = nb
                r.shared = False
            else:
                gf += 1
            r.buf.data[0] = 0
    return gt > 0, gt, gf


# --------------------------------------------------------------------------
# THE MUST-FIRE ARM. `selfcheck()` runs it, so the gate re-derives it once per
# input on every run -- not once, by whoever wrote it.
# --------------------------------------------------------------------------
# Three windows, written out as bytes so they depend on nothing in `inputs/`.
# None is ever fed to a rung. Op encoding: c % 4 = 0/1 DEFINE, 2 BREAK, 3 READ.
#   operand 3  -> w = 1 + 3 % 6 = 4 >= THRESH, key = 3    an OWNED string
#   operand 8  -> w = 1 + 8 % 6 = 3 <  THRESH, key = 1    an INTERNED string
_PROBE_OWNED = bytes([2, 0, 0, 0, 0, 3, 2, 0])                 # DEFINE(own) BREAK
_PROBE_LONE = bytes([2, 0, 0, 0, 0, 8, 2, 0])                  # DEFINE(intern) BREAK
_PROBE_SHARED = bytes([3, 0, 0, 0, 0, 8, 0, 8, 2, 1])          # x2 then BREAK rec 1


def detector_selftest():
    """Show that the detector CAN FIRE, that it DISTINGUISHES, and that THE
    SAFETY LINE is what silences it.

    Six cells, and the pairing is the point -- the same window under both
    semantics:

      * `_PROBE_OWNED`  buggy -> silent               hardened -> silent
      * `_PROBE_LONE`   buggy -> `published` ONLY     hardened -> silent
      * `_PROBE_SHARED` buggy -> `published` AND `aliased`
                                                      hardened -> silent

    ⚠ The middle arm is the one that makes this a derivation rather than a
    restatement: an interned record that NO OTHER RECORD NAMES. `aliased` is
    false there and `published` is true, so the two questions are not the same
    question, and neither of them is constant. The `_PROBE_OWNED` arm is the
    control that stops a detector which fires on everything from passing."""
    problems = []
    arms = (("OWNED, BREAK", _PROBE_OWNED, False, False),
            ("INTERNED but unshared, BREAK", _PROBE_LONE, False, True),
            ("SHARED by two records, BREAK", _PROBE_SHARED, True, True))
    for shape, blob, want_alias, want_pub in arms:
        _, quiet = _sim_window(blob, 0, len(blob), True)
        if quiet.aliased or quiet.published:
            problems.append(
                f"the detector FIRED on the `{shape}` probe under the HARDENED "
                f"semantics ({quiet.sites}), which no shipped rung can do -- the "
                f"probe or `Detector.write` is wrong")
        _, loud = _sim_window(blob, 0, len(blob), False)
        if loud.aliased != want_alias or loud.published != want_pub:
            problems.append(
                f"MUST-FIRE ARM WRONG on the `{shape}` probe under the BUGGY "
                f"semantics: got aliased={loud.aliased} published={loud.published}, "
                f"expected aliased={want_alias} published={want_pub}. This row "
                f"has NO detector but the checksum, so do not quote its harm as "
                f"DERIVED until this arm answers again")
    return problems


def no_share_break_problems(path, buf, stride, n_blob):
    """**No NON-adversarial input may execute a BREAK on a SHARED record.**

    ⚠⚠ This is p49's headline stated as a mechanical check on the shipped blob
    rather than as an argument about the generator. `harness/check.py` stage 2
    requires every non-adversarial cell to agree with this file and with every
    other cell, and a BREAK on a shared record is precisely where R1 and R1h
    part company -- both through the corrupted byte and through the private
    storage the copy-on-write spends and the ownership flag it clears, which the
    epilogue folds. ../inputs/gen.py refuses to emit one and
    ../controls/no_share_break.py censuses the directory."""
    if os.path.basename(path).startswith("adversarial-"):
        return []
    if not (HDR <= stride <= n_blob):
        return []
    out = []
    for w in range(n_blob // stride):
        hit, _, _ = window_share_break(buf, w * stride, stride)
        if hit:
            out.append(f"window {w} BREAKs a SHARED record, so R1 would write "
                       f"through a buffer it does not own -- that belongs on an "
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
        self.any_aliased = False
        self.any_published = False
        self.nwin = 0
        self._work = 0
        self._win = []
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(checked result, R1's detector) for the window at `off`.

        Implementation 1 of 2 -- buffers as objects; see the module docstring.
        The second element is computed under the BUGGY semantics, because the
        question it answers is what the rung with no safety line would reach."""
        r_ok, _ = _sim_window(self.buf, off, self.stride, True)
        _, det = _sim_window(self.buf, off, self.stride, False)
        return r_ok, det

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
                r, det = self._win[k]
                if det.aliased:
                    self.any_aliased = True
                if det.published:
                    self.any_published = True
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
            r, _det = self._win[k]
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
    # (../verus.rs `run`) and is entirely OFFSET-BASED: one flat byte sequence
    # and parallel integer sequences, with no buffer object anywhere.
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
        mem = [0] * MEM
        ekey, elen, eoff = [], [], []
        roff, rlen, rshd = [], [], []
        abump, pbump = 0, ARENA
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            w = 1 + a % MAXW
            key = a % NKEY
            m = c % 4
            if m in (DEFINE_A, DEFINE_B):
                if len(roff) >= NREC:
                    v = SENT
                elif w < THRESH:
                    f = len(ekey)
                    for k in range(len(ekey)):
                        if ekey[k] == key and elen[k] == w:
                            f = k
                            break
                    if f == len(ekey):
                        if len(ekey) >= NENT or abump + w > ARENA:
                            v = SENT
                        else:
                            for j in range(w):
                                mem[abump + j] = cbyte(key, j)
                            ekey.append(key)
                            elen.append(w)
                            eoff.append(abump)
                            roff.append(abump)
                            rlen.append(w)
                            rshd.append(1)
                            abump += w
                            v = a
                    else:
                        roff.append(eoff[f])
                        rlen.append(w)
                        rshd.append(1)
                        v = a
                else:
                    if pbump + w > MEM:
                        v = SENT
                    else:
                        for j in range(w):
                            mem[pbump + j] = cbyte(key, j)
                        roff.append(pbump)
                        rlen.append(w)
                        rshd.append(0)
                        pbump += w
                        v = a
            elif m == BREAK:
                if not roff:
                    v = SENT
                else:
                    t = a % len(roff)
                    if rshd[t]:
                        if pbump + rlen[t] > MEM:
                            acc = (acc * 31 + SENT) & MASK
                            continue
                        for j in range(rlen[t]):
                            mem[pbump + j] = mem[roff[t] + j]
                        roff[t] = pbump
                        rshd[t] = 0
                        pbump += rlen[t]
                    mem[roff[t]] = 0
                    v = 2
            else:
                if not roff:
                    v = SENT
                else:
                    t = a % len(roff)
                    v = 0
                    for j in range(rlen[t]):
                        v = (v * 31 + mem[roff[t] + j]) & MASK
            acc = (acc * 31 + v) & MASK
        for t in range(len(roff)):
            for j in range(rlen[t]):
                acc = (acc * 31 + mem[roff[t] + j]) & MASK
            acc = (acc * 31 + rshd[t]) & MASK
        return (acc * 31 + len(roff)) & MASK

    def intern_fold(self, buf, off, ln):
        """`intern_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"intern_fold": self.intern_fold}

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
        p27's, p29's, p32's, p34's and p25's denomination.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every matrix
        input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count: **each 2 window bytes is one OPERATION**, and every
            operation does two moduli, a compare chain and a multiply-add, while
            an interning DEFINE also SCANS the dedup table (up to `NENT`
            two-field comparisons) and materialises up to `MAXW` bytes, a READ
            folds up to `MAXW` bytes, and the epilogue folds every one of up to
            `NREC` records.

        ⚠ p49's under-count is BOUNDED, unlike p34's: no operation can do more
        than `NENT` comparisons plus `MAXW` byte moves, and the epilogue is at
        most `NREC * MAXW` bytes whatever the input, so no op stream can make the
        estimate arbitrarily loose. No `min_ir_per_work` is declared, so the
        harness default of 0.25 Ir per byte applies unchanged, and what it
        catches is the failure it exists to catch -- a kernel the optimiser
        collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """⚠⚠ **`clean`, ON EVERY INPUT, ADVERSARIAL INCLUDED -- DECLARED, AND
        IT IS THE ROW'S HEADLINE.**

        `c/kernel.c` allocates nothing, frees nothing, holds no pointer to
        anything it does not own for the whole call, and forms no index outside
        `mem[0 .. MEM)`; ../c/kernel.h proves the last clause in four lines.
        There is therefore **no undefined behaviour anywhere in the buggy rung**,
        and ASan, UBSan, Miri and the glibc allocator have nothing to report --
        on any input, at either optimisation level, on either compiler.
        ../NOTES.md 2 is the run; ../controls/detectors.py ships the positive
        controls, **which are load-bearing here in a way they are not elsewhere:
        every column on this row is silent, so a control that fires is the only
        thing separating "silent" from "not linked in".**

        ⚠ `.memory/03-measurement.md` entry 19 says *DECLARING IS HONEST; a
        derivation that cannot fire is not* -- so this is a declaration with an
        argument beside it (p01's, p08's, p22's and p47's shape) and NOT a
        simulation that would always answer `clean` while looking like a
        measurement. The derivation this file does carry is `Detector`, which
        answers a different question -- what did the write REACH -- and which
        fires, distinguishes and is exercised by `detector_selftest()` on every
        gate invocation.

        ✅ **That is the exact INVERSE of `p34`'s detector-only cell**, where the
        two rungs' checksums are bit-identical and ASan is the only
        discriminator. The two rows bracket *which instrument sees the harm*
        from opposite ends, and neither could have been written without the
        other."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p49's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27, p29, p32 and p34. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # recorded in the adversarial table rather than required -- and on this
        # row it is 0 everywhere, because R1 never crashes: it returns a
        # DIFFERENT NUMBER.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"R1-reaches(aliased={self.any_aliased},"
                f"published={self.any_published}) "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The object simulation vs the offset formulation that mirrors Verus,
        plus the must-fire arm that proves the detector is alive and
        discriminating, plus the no-shared-BREAK census on this input."""
        problems = list(detector_selftest())
        problems += no_share_break_problems(self.path, self.buf, self.stride,
                                            self.n_blob)
        for c in self.sample_calls(8):
            want = self.intern_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != intern_fold() {want} "
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
