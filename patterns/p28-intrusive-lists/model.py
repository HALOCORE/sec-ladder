#!/usr/bin/env python3
"""p28-intrusive-lists: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p28 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p27, p29 and p32 use, and
                  NOT p02's before/after shape. p28's objects are allocated
                  **and freed** inside the kernel, so no buffer crosses the
                  signature and there is nothing for an `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's, p29's and p32's
                  denomination. See the property's docstring for which way that
                  errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     **DERIVED, and the derivation FIRES ON SHIPPED INPUTS.** An
                  input is `fires` exactly when the simulated BUGGY rung reads
                  or writes an object it has already released. See
                  `sanitizer_expect` and `detector_selftest`.

--------------------------------------------------------------------------
TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE
--------------------------------------------------------------------------
`TASK_136`'s model was a line-by-line transliteration of its own kernel -- same
variable names, same guard -- which satisfies `check.py`'s model-sandbox rule
mechanically and defeats it in substance, and is how its delete bug went
undetected. `p29`'s model is the good example: a purely functional BST whose USE
test is a REACHABILITY WALK rather than a liveness bit. p28 does the same thing
one axis over, and the axis is the one the row is about:

  * the **simulation** (`_sim_checked`) **HAS NO LINKS OF ANY KIND, IN EITHER
    DIRECTION, IN EITHER LIST.** Every rung represents this cache as objects
    carrying four link fields -- `lp`, `ln`, `hn`, `hp` -- plus a `bucket[]`
    array of chain heads. The simulation is a **`dict` from key to object** plus
    an **insertion-ordered `list`**. A lookup is `a in cache`, an eviction is
    `order.pop(0)`, a delete is `order.remove(o)`. There is no bucket, no chain,
    no `hn`, no `hp` and no walk. **The two implementations therefore disagree
    about where the cache's membership is recorded** -- in fields inside the
    objects, or in two Python containers outside them -- and agree about the
    answer, which is the whole of what the sandbox rule is for. That is not a
    decorative difference here: R1's bug is precisely that ONE of the two
    intrusive representations can fall out of step with the other;
  * the **helper** `cache_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs, carrying
    the seven parallel slot sequences `ky`, `vl`, `lp`, `ln`, `hn`, `hp`, `lv`
    plus the bucket array, the two list ends and the two counters exactly as the
    proof does, **including the walk and its fuel**.

    `selfcheck()` runs them against each other, which makes the pair carry one
    fact neither carries alone: **the walk fuel never truncates a chain.** The
    dict simulation cannot truncate -- it has no chain -- so if the fuel were
    ever reached, the two implementations would disagree and `selfcheck` would
    say so. The arithmetic reason it cannot happen is that a
    chain holds only live objects and at most `SLOTS` objects are ever made, so
    no chain is longer than the fuel; the cross-check is what turns that from an
    argument into a test.

    `cache_fold` is **iterative where the Verus function is recursive**, for
    p11's, p14's, p27's, p29's and p32's reason: `run` recurses once per
    operation and a window may declare more operations than CPython's recursion
    limit allows.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where a TRIM is
followed by any operation on the victim's bucket; the gate RECORDS that
disagreement in its behaviour table rather than requiring it to vanish
(`.memory/02-bench-rules.md`).

--------------------------------------------------------------------------
⚠⚠ CAN THIS MODEL REPRESENT THE STALE LINK AT ALL? YES -- AND HERE IS EXACTLY
   HOW MUCH OF IT, WRITTEN DOWN BEFORE THE GATE WAS RUN RATHER THAN DISCOVERED
   AT IT (TASK_146 deliverable 2)
--------------------------------------------------------------------------
p28's whole harm is a pointer left in ANOTHER heap object's `hn` field, and a
`dict` has no such field. So the detector does **not** live in the dict
simulation. It lives in a THIRD function, `_sim_buggy`, which is neither of the
two implementations above and is never consulted for an answer:

    the C rungs   membership is a POINTER inside each object (`hn`/`hp`) and in
                  `bucket[b]`
    `_sim_buggy`  membership is a **Python list per bucket**, `chains[b]`, whose
                  elements are object references, and a released object is one
                  whose `released` flag is set. TRIM under the BUGGY semantics
                  frees the victim and **leaves it in `chains[b]`**; TRIM under
                  the checked semantics removes it first. That is the stale
                  link, represented.

**WHAT IT REPRESENTS FAITHFULLY:** that after a TRIM the victim is still
*reachable by a walk of its bucket*, that the walk reaches it in the same
position and after the same number of steps, that reading it is a
use-after-free, and that a DEL of a neighbour WRITES into it.

**WHAT IT COLLAPSES, said so nobody reads the derivation as more than it is:**
the membership list cannot distinguish *the dangling pointer is in `bucket[b]`*
(the victim was the chain head) from *the dangling pointer is in a live
predecessor's `hn`*. Both are "the victim is still an element of `chains[b]`"
here. **That distinction is the row's own claim about where the dangling pointer
lives, so it is measured OUTSIDE this file**, at C level, by
`controls/harm_sites.py`, which ships one adversarial window of each shape and
reads the site back out of ASan's report. ../NOTES.md 2.

--------------------------------------------------------------------------
**Why the benign inputs never touch a released object.** They cannot: the moment
one does, R1 returns a different number (or crashes) and the cell no longer
agrees with any other, and `harness/check.py` stage 2 requires every
non-adversarial cell to agree with this file *and with each other*.
⚠ **The constraint is sharper here than on p27 or p29, and `inputs/gen.py` has to
know it:** in R1 a TRIM **POISONS ITS VICTIM'S BUCKET PERMANENTLY** -- the freed
object stays in that chain for the rest of the window, so *any* later PUT, GET or
DEL whose operand lands in that bucket touches it. `inputs/gen.py` therefore
tracks the poisoned bucket set and refuses to emit an operand that lands in one,
and checks the property afterwards by running this file's `_sim_buggy` over every
window of every blob it writes. Both harm shapes live on the `adversarial-*` rows
alone.
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
NB = 8                    # must equal every rung's P28_NB
SLOTS = 48                # must equal every rung's P28_SLOTS: the objects one
                          # window may make, AND the chain walk's fuel
NIL = 255                 # must equal every rung's NIL
SENT = 251                # must equal every rung's SENT


def _val_of(a):
    """An object's payload is a function of the key that created it, in every
    rung: `a * 7 + 1` truncated to a byte. So a GET that returns a released
    object's payload returns a value no honest read of the key it asked for
    could produce -- which is what makes the harm visible in the checksum."""
    return (a * 7 + 1) & 0xFF


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- a dict cache with an insertion order, and NO LINKS.
# See the module docstring.
# --------------------------------------------------------------------------
class Obj:
    """ONE ALLOCATION. Identity is what this pattern is about: the harm is that
    a container still holds a reference to an object the program has released,
    so the object needs an identity a container can hold."""

    __slots__ = ("key", "val", "released")

    def __init__(self, key):
        self.key = key
        self.val = _val_of(key)
        self.released = False


def _sim_checked(buf, off, ln):
    """The CHECKED semantics (R1h and R2-R5), with no links anywhere.

    `cache` maps a key to the live object holding it -- at most one, because PUT
    updates in place on a hit. `order` is insertion order, oldest FIRST, so
    `order[0]` is what the rungs reach through `tail` and `order[-1]` is what
    they reach through `head`. Neither container is anything a rung has."""
    if ln < HDR:
        return 0
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return 0
    cache = {}
    order = []
    nmade = 0
    acc, p = 0, HDR
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        c = buf[off + p]
        a = buf[off + p + 1]
        p += OPSZ
        op = c % 4
        if op == 0:                                   # PUT
            if a in cache:
                cache[a].val = _val_of(a)
                acc = (acc * 31 + a) & MASK
            elif nmade < SLOTS:
                o = Obj(a)
                cache[a] = o
                order.append(o)
                nmade += 1
                acc = (acc * 31 + a) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        elif op == 1:                                 # GET
            acc = (acc * 31 + (cache[a].val if a in cache else SENT)) & MASK
        elif op == 2:                                 # DEL
            if a in cache:
                o = cache.pop(a)
                order.remove(o)
                o.released = True
                acc = (acc * 31 + 2) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        else:                                         # TRIM
            if order:
                o = order.pop(0)
                del cache[o.key]
                o.released = True
                acc = (acc * 31 + 3) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
    return (acc * 31 + nmade) & MASK


# --------------------------------------------------------------------------
# THE DETECTOR. Not an implementation of the kernel -- nothing reads its answer.
# See the module docstring's "CAN THIS MODEL REPRESENT THE STALE LINK AT ALL?".
# --------------------------------------------------------------------------
class _Escape(Exception):
    """Raised the instant the simulated BUGGY rung touches an object it has
    released.

    ⚠ **It exists so the detector REPORTS an escape instead of interpreting
    past one.** Once R1 has read `n->key` out of a freed chunk, what it does
    next is a function of what the allocator left there, and no simulation can
    say. `_sim_buggy` discards its accumulator anyway -- only the flag is read
    -- so abandoning the window at the first touch costs nothing and is what a
    detector, rather than an interpreter, should do. `TASK_145_REPORT` 4b's
    third finding was a model that CRASHED where it should have reported, so a
    firing detector and a broken one were indistinguishable."""


def _sim_buggy(buf, off, ln, harden):
    """`(touched, sites)` for one window under the rung selected by `harden`.

    `harden=False` is `c/kernel.c` -- **TRIM leaves the victim in its bucket's
    chain.** `harden=True` is `c/kernel_hardened.c` and every Rust rung, which
    remove it first. Everything else is identical between the two, which is what
    makes the pair a controlled comparison rather than two programs.

    Membership lives in `chains[b]` (newest first, mirroring a chain whose head
    is `bucket[b]`) and in `order` (oldest first). An object carries `released`.
    A TOUCH is any read or write the rung performs on an object it reached by
    walking, and the detector fires on the first touch of a released one."""
    sites = []

    def touch(o, what):
        if o.released:
            sites.append(f"{what} on an object released earlier in this window "
                         f"(key {o.key})")
            raise _Escape(sites[-1])

    def walk(chains, b, a):
        """The rungs' chain walk, fuel included. Reading `n->key` is a touch."""
        for i, o in enumerate(chains[b]):
            if i >= SLOTS:
                return None
            touch(o, "the walk reads `n->key`")
            if o.key == a:
                return o
        return None

    if ln < HDR:
        return False, sites
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return False, sites
    chains = [[] for _ in range(NB)]
    order = []
    nmade = 0
    p = HDR
    try:
        for _ in range(nops):
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            b = a % NB
            op = c % 4
            if op == 0:                               # PUT
                n = walk(chains, b, a)
                if n is not None:
                    touch(n, "PUT writes `n->val`")
                    n.val = _val_of(a)
                elif nmade < SLOTS:
                    o = Obj(a)
                    if chains[b]:
                        touch(chains[b][0], "PUT writes the old chain head's "
                                            "`hp`")
                    chains[b].insert(0, o)
                    order.append(o)
                    nmade += 1
            elif op == 1:                             # GET
                n = walk(chains, b, a)
                if n is not None:
                    touch(n, "GET reads `n->val`")
            elif op == 2:                             # DEL
                n = walk(chains, b, a)
                if n is not None:
                    touch(n, "DEL reads `n->hp`/`n->hn`/`n->lp`/`n->ln`")
                    i = chains[b].index(n)
                    if i > 0:
                        touch(chains[b][i - 1], "DEL writes the chain "
                                                "predecessor's `hn`")
                    if i + 1 < len(chains[b]):
                        touch(chains[b][i + 1], "DEL writes the chain "
                                                "successor's `hp`")
                    chains[b].pop(i)
                    order.remove(n)
                    n.released = True
            else:                                     # TRIM
                if order:
                    v = order.pop(0)
                    if harden:
                        # THE SAFETY LINE, and it is the whole of the
                        # difference between the two arms of this function.
                        j = chains[v.key % NB].index(v)
                        cb = chains[v.key % NB]
                        if j > 0:
                            touch(cb[j - 1], "the safety line writes the chain "
                                             "predecessor's `hn`")
                        if j + 1 < len(cb):
                            touch(cb[j + 1], "the safety line writes the chain "
                                             "successor's `hp`")
                        cb.pop(j)
                    v.released = True
    except _Escape:
        return True, sites
    return False, sites


# --------------------------------------------------------------------------
# THE MUST-FIRE ARM. `selfcheck()` runs it, so the gate re-derives it once per
# input on every run -- not once, by whoever wrote it.
# --------------------------------------------------------------------------
def _probe(ops):
    """A window, written out as bytes, depending on nothing in `inputs/`."""
    out = bytearray(len(ops).to_bytes(4, "little"))
    for op, a in ops:
        out.append(op)
        out.append(a)
    return bytes(out)


# Two objects in bucket 5 (5 % 8 == 5, 13 % 8 == 5), TRIM the older, then touch
# the bucket.  READ shape: a GET walks into the released object.
_PROBE_READ = _probe([(0, 5), (0, 13), (3, 0), (1, 5)])
# WRITE shape: a DEL of the SURVIVOR writes the released object's `hp`. The
# survivor is 13, which sits in front of 5 in the chain, so DEL 13 splices and
# writes into 5. Neither probe is ever fed to a rung.
_PROBE_WRITE = _probe([(0, 5), (0, 13), (3, 0), (2, 13)])


def detector_selftest():
    """Show that `_sim_buggy` CAN FIRE, and that the safety line is what stops
    it. Four cells, two per probe:

      * `_PROBE_READ`  with the safety line KEPT    -> silent
      * `_PROBE_READ`  with the safety line DELETED -> **fires**
      * `_PROBE_WRITE` with the safety line KEPT    -> silent
      * `_PROBE_WRITE` with the safety line DELETED -> **fires**

    ⚠⚠ `.memory/03-measurement.md` 19: *whatever a model DERIVES rather than
    declares owes an arm that shows it firing.* p28's derivation also fires on
    two SHIPPED inputs (`adversarial-uaf-read.bin` and
    `adversarial-uaf-write.bin`), which p32's could not, so this arm is the
    second line of evidence rather than the only one -- but it is the one that
    runs on every invocation and the one that keeps working if the adversarial
    blobs are ever regenerated differently.

    ⚠ **It REPORTS rather than CRASHES when the detector is broken**
    (`TASK_145_REPORT` 4b, `.memory/03-measurement.md` 19's closing paragraph:
    three of four planted mutations there failed by crashing, which is loud and
    loses the diagnostic). Every cell runs inside `try`, and an exception
    becomes the designed problem string with the exception text attached."""
    problems = []
    arms = (("READ", _PROBE_READ, "a GET walks into the released object"),
            ("WRITE", _PROBE_WRITE, "a DEL of the survivor writes into it"))
    for name, blob, what in arms:
        try:
            quiet, _ = _sim_buggy(blob, 0, len(blob), True)
        except Exception as e:                        # noqa: BLE001
            problems.append(
                f"MUST-FIRE ARM BROKEN ({name}, safety line KEPT): the "
                f"detector raised {type(e).__name__}: {e}. A crash is not a "
                f"firing; `sanitizer_expect` cannot be read as derived until "
                f"this arm runs to completion")
            continue
        if quiet:
            problems.append(
                f"the released-object detector FIRED on the {name} probe with "
                f"the SAFETY LINE PRESENT, which no shipped rung can do -- the "
                f"probe or `_sim_buggy` is wrong")
        try:
            loud, sites = _sim_buggy(blob, 0, len(blob), False)
        except Exception as e:                        # noqa: BLE001
            problems.append(
                f"MUST-FIRE ARM BROKEN ({name}, safety line DELETED): the "
                f"detector raised {type(e).__name__}: {e} instead of "
                f"reporting. See `.memory/03-measurement.md` 19")
            continue
        if not loud:
            problems.append(
                f"MUST-FIRE ARM DEAD ({name}): deleting the safety line from "
                f"the simulated buggy rung did NOT make the released-object "
                f"detector fire (expected: {what}). `sanitizer_expect` is then "
                f"a declaration wearing a derivation's clothes, which is what "
                f"`TASK_145` measured on p32 and `.memory/03-measurement.md` "
                f"19 forbids -- do not quote this pattern's `fires` as DERIVED "
                f"until it fires again")
        elif not sites:
            problems.append(
                f"MUST-FIRE ARM ({name}) reports a firing with NO SITE, so it "
                f"cannot say what fired")
    return problems


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
        self.uaf_sites = []
        # ⚠⚠ **THE DETECTOR MUST REPORT, NOT PROPAGATE**, and this field is how.
        # `.memory/03-measurement.md` 19's closing paragraph: three of the four
        # mutations planted into p32's repaired arm failed by CRASHING inside
        # the simulation rather than returning the designed message, so the
        # failure was loud and the DIAGNOSTIC was lost. `_window` below catches
        # ANY exception out of `_sim_buggy` -- not just `_Escape` -- records it
        # here, and `selfcheck()` turns it into a named problem. Found by
        # `.temp/t146/mustfire_probe.py`'s M4 arm, which plants a detector that
        # raises the WRONG exception type: before this field it escaped
        # `Model.__init__` and the gate saw a crash instead of a sentence.
        self.detector_error = None
        self.nwin = 0
        self._work = 0
        self._win = []      # per window: (result, R1_touches_a_released_object)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_touches_a_released_object) for the window at `off`.

        The first element is Implementation 1 -- the dict cache, no links. The
        second is the detector, run under the BUGGY semantics, because the
        question it answers is what the rung with no safety line would do."""
        r_ok = _sim_checked(self.buf, off, self.stride)
        try:
            uaf, sites = _sim_buggy(self.buf, off, self.stride, False)
        except Exception as e:                                # noqa: BLE001
            # See `detector_error`'s comment in __init__. The window's answer is
            # `_sim_checked`'s and does not depend on the detector, so the model
            # keeps working and `selfcheck()` says what broke.
            if self.detector_error is None:
                self.detector_error = f"{type(e).__name__}: {e}"
            return r_ok, False, []
        return r_ok, uaf, sites

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
                r, uaf, sites = self._win[k]
                if uaf:
                    self.any_uaf = True
                    if sites and sites[-1] not in self.uaf_sites:
                        self.uaf_sites.append(sites[-1])
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
            r, _uaf, _sites = self._win[k]
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
    # the dict simulation in disguise. It mirrors the *Verus* spec function
    # (../verus.rs `run`) and keeps the cache in seven parallel slot sequences
    # with a bucket array beside them, which is the RUNGS' representation and
    # not the simulation's -- links and all, walk and all, fuel and all.
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
        ky = [0] * SLOTS
        vl = [0] * SLOTS
        lp = [NIL] * SLOTS
        lnx = [NIL] * SLOTS
        hn = [NIL] * SLOTS
        hp = [NIL] * SLOTS
        lv = [0] * SLOTS
        bk = [NIL] * NB
        head, tail = NIL, NIL
        nmade = 0
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            b = a % NB
            m = c % 4
            if m == 3:
                if tail != NIL:
                    v = tail
                    if lp[v] != NIL:
                        lnx[lp[v]] = NIL
                    else:
                        head = NIL
                    tail = lp[v]
                    vb = ky[v] % NB
                    if hp[v] != NIL:
                        hn[hp[v]] = hn[v]
                    else:
                        bk[vb] = hn[v]
                    if hn[v] != NIL:
                        hp[hn[v]] = hp[v]
                    lv[v] = 0
                    acc = (acc * 31 + 3) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
                continue
            cur, steps, found = bk[b], 0, False
            while cur != NIL and lv[cur] == 1 and steps < SLOTS:
                steps += 1
                if ky[cur] == a:
                    found = True
                    break
                cur = hn[cur]
            if m == 0:
                if found:
                    vl[cur] = _val_of(a)
                    acc = (acc * 31 + a) & MASK
                elif nmade < SLOTS:
                    s = nmade
                    ky[s], vl[s], lv[s] = a, _val_of(a), 1
                    lp[s], lnx[s] = NIL, head
                    if head != NIL:
                        lp[head] = s
                    else:
                        tail = s
                    head = s
                    hp[s], hn[s] = NIL, bk[b]
                    if bk[b] != NIL:
                        hp[bk[b]] = s
                    bk[b] = s
                    nmade += 1
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == 1:
                acc = (acc * 31 + (vl[cur] if found else SENT)) & MASK
            else:
                if found:
                    if hp[cur] != NIL:
                        hn[hp[cur]] = hn[cur]
                    else:
                        bk[b] = hn[cur]
                    if hn[cur] != NIL:
                        hp[hn[cur]] = hp[cur]
                    if lp[cur] != NIL:
                        lnx[lp[cur]] = lnx[cur]
                    else:
                        head = lnx[cur]
                    if lnx[cur] != NIL:
                        lp[lnx[cur]] = lp[cur]
                    else:
                        tail = lp[cur]
                    lv[cur] = 0
                    acc = (acc * 31 + 2) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + nmade) & MASK

    def cache_fold(self, buf, off, ln):
        """`cache_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"cache_fold": self.cache_fold}

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
        p27's, p29's and p32's denomination and p16's, p05's, p11's, p12's,
        p06's and p14's.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count, and it dominates: **each 2 window bytes is one
            OPERATION**, and three of the four opcodes begin with a CHAIN WALK
            -- up to `SLOTS` steps, each a load and a compare -- while PUT, DEL
            and TRIM also splice up to four links and two of them call the
            allocator, which is tens of instructions each in glibc.

        So `stride` is far below the number of instructions the kernel must
        execute, the derived floor is one it clears by orders of magnitude, and
        it can never let a collapsed kernel through -- the only direction that
        matters. No `min_ir_per_work` is declared, so the harness default of
        0.25 Ir per byte applies unchanged."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**DERIVED from the simulated buggy run, never tabulated per file --
        and the derivation FIRES, on shipped inputs and on a planted probe.**

        R1's TRIM frees its victim and leaves it in the victim's hash chain, so
        R1 commits a memory error exactly when some visited window performs an
        operation that WALKS or SPLICES that chain afterwards. `_sim_buggy`
        carries the chain as a MEMBERSHIP LIST and the object's release as a
        FLAG, and reports the first touch of a released object; `_sim_checked`,
        the model's own answer, carries neither and cannot express the question.
        The module docstring says exactly how much of the real thing that
        represents and what it collapses.

        ⚠⚠ **WHAT MAKES IT A MEASUREMENT AND NOT A RESTATEMENT.** The predicate
        takes BOTH values on shipped inputs: `clean` on `small`, `large` and
        `degenerate` -- all of which TRIM, repeatedly -- and `fires` on
        `adversarial-uaf-read` and `adversarial-uaf-write`. It is not false by
        construction, it is false on the benign rows because `inputs/gen.py`
        keeps the poisoned buckets untouched, and TRUE the moment one is
        touched. `detector_selftest()` closes the other half by DELETING the
        safety line from the simulated rung and showing the same two probes go
        from silent to firing; `selfcheck()` runs it on every gate invocation.
        `.memory/03-measurement.md` 19.

        ⚠ **What it does NOT derive.** It derives the TEMPORAL half -- a
        released object is touched -- which is what ASan is looking for. It says
        nothing about UBSan, which sees nothing here for the same reason it sees
        nothing on p27 and p29: no signed overflow, no misaligned access, no
        out-of-range index. R1's every index is in range; what is out of range
        is the object's LIFETIME. ../NOTES.md 2."""
        return "fires" if self.any_uaf else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p28's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27, p29 and p32. `slb_load` rejecting a
        # short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # RECORDED in the adversarial table rather than required -- and on
        # `adversarial-uaf-write.bin` it is a SIGNAL rather than an exit code,
        # which is one of the behaviours that table exists to hold.
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
        """The dict cache vs the seven slot sequences that mirror Verus, plus
        the must-fire arm that proves the released-object detector is alive.

        The first arm carries more than agreement: the dict cache has no chain
        and therefore no fuel, so a disagreement is also how a fuel truncation
        would announce itself."""
        problems = list(detector_selftest())
        if self.detector_error is not None:
            problems.append(
                f"THE RELEASED-OBJECT DETECTOR RAISED instead of reporting: "
                f"{self.detector_error}. `sanitizer_expect` is then whatever "
                f"the surviving windows happened to say, which is not a "
                f"derivation -- see `detector_error` in __init__ and "
                f"`.memory/03-measurement.md` 19")
        for c in self.sample_calls(8):
            want = self.cache_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != cache_fold() {want} "
                    f"at off={c['off']} -- the dict cache and the slot-sequence "
                    f"machine disagree; a fuel truncation in the second is "
                    f"one of the ways that happens")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
        for s in m.uaf_sites:
            print(f"    site: {s}")
