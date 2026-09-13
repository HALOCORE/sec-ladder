#!/usr/bin/env python3
"""ph52-concat-copy-uninit: the independent reference model the gate checks
against.

    python3 patterns-php/ph52-concat-copy-uninit/model.py inputs/*.bin

`harness/check.py` imports `build(path)` and uses the object it returns as the
oracle for every rung: `expected_stdout`, `expected_exit`, `sanitizer_expect`,
`work_per_call`, `iter_calls()` and the `helpers` the derived `ensures` is
evaluated against.

============================================================================
TWO IMPLEMENTATIONS, AND WHY THE SECOND ONE IS NOT THE FIRST IN DISGUISE
============================================================================
`PROTOCOL_PHP.md` §A2a rule 2. ph03 shipped for a whole task with its two
implementations computing DIFFERENT functions, because its corpus took one arm
of a two-armed branch and `inputs/` is not a domain.

  * `_window()` is an IMPERATIVE transcription of `c/kernel_hardened.c`: one
    mutable `Alloc`, two mutable slot variables named as the C names them
    (`op1_copy`, `op2_copy`), and the arms in upstream's order.
  * `concat_fold()` is a transcription of `verus.rs`'s spec functions --
    `arm_of`, `printable`, `op_step`, `run_ops` -- carrying
    `(op1_copy, op2_copy, alloc, acc)` as a returned TUPLE through pure
    transitions rather than as mutated state, and reached only through the
    derived `ensures`.
  * `_dumb()` is a THIRD, deliberately naive spelling: it builds the whole
    result STRING for every op with Python string concatenation, re-derives the
    allocator request sequence as a flat LIST and replays that list through a
    freshly built cache from scratch. It shares no code with either of the other
    two and it is what catches a fold that silently changed its range or an
    allocator request that moved in the sequence.

⚠⚠ **AND `None` IS WHERE THIS MODEL IS NOT THE C.** The C's unconstructed slot
holds whatever the previous frame left at that stack offset; this model's holds
`None`, and `zval_dtor` on `None` is *skipped*. So the model is the SAFE
semantics -- what R2, R3, R4 and R5 all implement -- and it agrees with both C
rungs exactly where the defect is not exercised, which is every measured window.
On `inputs/adversarial-dblfree.bin`, where the C double-frees, the C's answer is
RECORDED by `check.py` stage 4 rather than required to agree, and that
difference is the row's result. ../NOTES.md §5.

⚠ **THIS MODEL CANNOT EXPRESS THE DEFECT AND THAT IS THE POINT.** There is no
Python spelling of "read a stack byte nobody wrote", so the second opinion is
genuinely independent of the mechanism -- and its inability to express it is a
small statement of the row's own ladder result.

============================================================================
THE SLOT STATES, WHICH ARE THE WHOLE OF WHY THIS ROW IS A CALL HISTORY
============================================================================
After `ph52_concat_function` returns, the caller's slot holds one of:

    None        UNCONSTRUCTED -- nothing has ever written it
    ("empty",0) `IS_STRING` + `empty_string`, from `zend.c:195-197` (IS_NULL),
                `:204-205` (IS_BOOL false) or `:244-245` (the faulting arm
                itself).  `zend.h:469 STR_FREE` SKIPS `empty_string`, so a
                teardown on this state is DEFINED and costs no allocator call.
    ("dang",n)  `IS_STRING` + a pointer `zend_operators.c:1188` has just FREED,
                from `:202` (n=2), `:214` (n=6) or `:249` (n=31).  A teardown on
                THIS state is a DOUBLE FREE.

and the `PH52_ARM_STRING` arm (`:190-193`) leaves it UNCHANGED, because
`expr_copy` is never written on that path -- which is why the state is inherited
across ops and across windows and why `inputs/gen.py` asserts an ADJACENCY
property. The model tracks the state, refuses to follow the C into the
("dang",n) teardown, and counts it.

============================================================================
THE u64
============================================================================
Every term is a length, a byte value or a count -- never an address
(`TASK_PHP_041.md` §2.3):

    acc          starts at the second head word, `fold_w`
    per op       the result's LENGTH, then the 131-fold over EACH OPERAND's
                 printable bytes (`*d1`, `*d2`)
    finally      xor php_shim_tally()

`php_shim_tally()` is reproduced ARITHMETICALLY (`Alloc`) rather than by linking
the shim, because no Rust rung may link it (§B).

⚠⚠ **AND THE REPRODUCTION IS NOT FREE HERE, WHICH IS `PROTOCOL_PHP.md` §B1a's
PRECONDITION FAILING.** The kernel makes up to **five `emalloc`s and three
`efree`s per op**, i.e. O(n_ops) per kernel call, so the size-class cache
(`zend_alloc.c:150-168`, `:270-279`) is not merely present but EVOLVING, and the
tally depends on which requests were served from it. `Alloc` below is the
counters-only simulation every rung carries; `ph64`'s `safe_naive.rs::Alloc` is
the precedent. ▶ §B1a.3 therefore binds: the order is declared in ../spec.md and
every CROSS-LANGUAGE figure this row publishes is labelled as including allocator
work. ⭐ The SAME-LANGUAGE ratios are unaffected (§B1a.4).
"""

import itertools
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common-php"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HERE = os.path.dirname(os.path.abspath(__file__))

#: `c/kernel.h`. `_c_constants()` parses the C and compares, so the two cannot
#: drift apart in this file's head.
HDR_BYTES = 8
OPS_OFF = HDR_BYTES
OP_BYTES = 4
NARM = 5
ARM_STRING, ARM_NULL, ARM_BOOL, ARM_ARRAY, ARM_OBJECT = 0, 1, 2, 3, 4
OBJ_PREFIX_LEN = 11          # sizeof("Object id #") - 1
MAX_LENGTH_OF_LONG = 20      # zend_operators.h:37
OBJ_REQ = OBJ_PREFIX_LEN + MAX_LENGTH_OF_LONG    # zend.c:249's request

#: `emalloc_shim.h:190-191`, `zend_alloc.h:63-64`.
MAX_CACHED_MEMORY = 11
MAX_CACHED_ENTRIES = 256

#: `emalloc_shim.h:642-648`. `_shim_constants()` re-reads them from the header.
TALLY_ALLOC = 1000003
TALLY_FREE = 1000033
TALLY_CACHE_HIT = 1000037
TALLY_BYTES = 1000039

OBJ_PREFIX = b"Object id #"

#: `c/kernel.h` PH52_DIG_*. ⚠ INSTRUMENTATION, not a `zval` field: `zend.c:250`
#: and `zend_operators.c:1182-1184`'s store lines are not lifted and the content
#: they would have moved is folded as a digest instead. `_c_constants()` reads
#: these back out of the header, and `controls/digest.py` checks each against the
#: literal it stands for.
DIG_PREFIX = 18136473400329561039     # fold131("Object id #")
DIG_ARRAY = 19400746421               # fold131("Array")
DIG_ONE = 49                          # fold131("1")


def real_size(n):
    """`PHP_SHIM_REAL_SIZE`, `emalloc_shim.h:217`, i.e. `zend_alloc.c:132`."""
    return (n + 7) & ~7


class Alloc:
    """`zend_alloc.c`'s size-class cache, counters only.

    `php_shim_reset()` (`emalloc_shim.h:263-279`) runs at the top of every kernel
    call and empties both the cache and the tally, so one of these lives for one
    call. ⚠ `free()` takes its class from the RECORDED size (`p->size`,
    `zend_alloc.h:53`), which for every request this kernel makes is the size
    that was asked for -- the T2 truncation never fires below 2^31."""

    __slots__ = ("cnt", "n_alloc", "n_free", "n_hit", "n_push", "bytes", "reqs")

    def __init__(self):
        self.cnt = [0] * MAX_CACHED_MEMORY
        self.n_alloc = 0
        self.n_free = 0
        self.n_hit = 0
        self.n_push = 0
        self.bytes = 0
        self.reqs = []          # the request SEQUENCE, for `_dumb()`

    def alloc(self, size):
        """`_emalloc` -- `zend_alloc.c:142-217`."""
        self.reqs.append(("a", size))
        rsz = real_size(size)
        idx = rsz >> 3
        self.n_alloc += 1
        if idx < MAX_CACHED_MEMORY and self.cnt[idx] > 0:
            self.cnt[idx] -= 1
            self.n_hit += 1
        else:
            self.bytes += rsz

    def free(self, size):
        """`_efree` -- `zend_alloc.c:248-289`."""
        self.reqs.append(("f", size))
        rsz = real_size(size)
        idx = rsz >> 3
        self.n_free += 1
        if idx < MAX_CACHED_MEMORY and self.cnt[idx] < MAX_CACHED_ENTRIES:
            self.cnt[idx] += 1
            self.n_push += 1

    def tally(self):
        """`php_shim_tally()` -- `emalloc_shim.h:642-648`."""
        return ((self.n_alloc * TALLY_ALLOC)
                ^ (self.n_free * TALLY_FREE)
                ^ (self.n_hit * TALLY_CACHE_HIT)
                ^ (self.bytes * TALLY_BYTES)) & MASK


def _rd32(w, o):
    return w[o] | (w[o + 1] << 8) | (w[o + 2] << 16) | (w[o + 3] << 24)


def cap_of(stride):
    """Ops the window has room for. Derived from the LENGTH, never trusted out
    of the blob -- the same discipline ph16 applies to its split."""
    return (stride - OPS_OFF) // OP_BYTES


def unpack(win):
    """(n_ops, fold_w, ops) exactly as every rung derives it. One op is
    (arm1, aux1, arm2, aux2)."""
    cap = cap_of(len(win))
    n_ops = _rd32(win, 0) % (cap + 1)
    fold_w = _rd32(win, 4)
    ops = []
    for o in range(n_ops):
        p = OPS_OFF + OP_BYTES * o
        ops.append((win[p] % NARM, win[p + 1], win[p + 2] % NARM, win[p + 3]))
    return n_ops, fold_w, ops


def digits(x):
    """`sprintf("%ld", x)` for the object handle, which is one byte here."""
    return str(x).encode()


def fold131(b):
    """The content digest `zend.c`'s arms accumulate into `*dig`.

    ⚠ IT IS INSTRUMENTATION, exactly as ph53's `*examined` / `*matched_id`
    out-parameters are: `zend_operators.c:1182-1184`'s three `memcpy`/store lines
    are NOT lifted, because the bytes they move are a function of the two operand
    descriptors and keeping them would put a `Seq<u8>` concatenation in R5's
    postcondition. ../spec.md's divergence ledger carries the argument."""
    h = 0
    for c in b:
        h = (h * 131 + c) & MASK
    return h


def printable(arm, aux, alloc, slot):
    """`zend_make_printable_zval`, `Zend/zend.c:188-265`, NARROWED to five arms.

    Returns `(use_copy, (len, dig), slot_after, uninit_read, double_free)`.
    `slot` is the caller's slot state going IN (see the module docstring);
    `slot_after` is its state when the function returns, BEFORE
    `zend_operators.c:1188`'s own teardown.

    ⚠ `len` is what `value.str.len` ends up carrying, `dig` is the content
    digest, and `slot_after` carries the allocation size that `:1188` will have
    to release."""
    if arm == ARM_STRING:                               # :190-193
        # expr_copy UNTOUCHED; the operand is one attacker byte
        return 0, (1, ord('a') + aux % 26), slot, 0, 0
    uninit = dblfree = 0
    if arm == ARM_NULL:                                 # :195-197
        after = ("empty", 0)
        out = (0, 0)
    elif arm == ARM_BOOL:                               # :199-206
        if aux & 1:
            alloc.alloc(2)                              # :202 estrndup("1", 1)
            after = ("heap", 2)
            out = (1, DIG_ONE)
        else:
            after = ("empty", 0)                        # :204-205
            out = (0, 0)
    elif arm == ARM_ARRAY:                              # :213-215
        alloc.alloc(6)                                  # estrndup("Array", 5)
        after = ("heap", 6)
        out = (5, DIG_ARRAY)
    else:                                               # :217-252  IS_OBJECT
        if aux & 1:                                     # :242  EG(exception)
            # ⛔⛔ THE DEFECT.  `:243 zval_dtor(expr_copy)` on a slot nothing has
            # constructed.  The three states, and what the C does to each:
            if slot is None:
                uninit = 1          # the model CANNOT follow it -- see docstring
            elif slot[0] == "dang":
                dblfree = 1         # the C double-frees; the model does not
            # ("empty", 0): STR_FREE skips `empty_string`. DEFINED, no call.
            after = ("empty", 0)                        # :244-245
            out = (0, 0)
        else:
            alloc.alloc(OBJ_REQ)                        # :249
            # :250  the prefix is a constant digest; the handle's decimal digits
            # are folded least-significant-first, which is the order
            # `sprintf`'s own `do { } while (d)` produces them in.
            # ⚠ `aux` is one window byte, so at most three decimal digits and
            # `sprintf`'s `do { } while (d)` is an exhaustive three-way case.
            g = DIG_PREFIX
            g = (g * 131 + (48 + aux % 10)) & MASK
            if aux < 10:
                nd = 1
            else:
                g = (g * 131 + (48 + (aux // 10) % 10)) & MASK
                if aux < 100:
                    nd = 2
                else:
                    g = (g * 131 + (48 + aux // 100)) & MASK
                    nd = 3
            out = (OBJ_PREFIX_LEN + nd, g)
            after = ("heap", OBJ_REQ)
    return 1, out, after, uninit, dblfree


def op_step(op, alloc, s1, s2, acc):
    """One `ph52_concat_function` call -- `Zend/zend_operators.c:1146-1194` --
    as a PURE transition. Returns `(s1', s2', acc', uninit, dblfree)`.

    This is implementation 2's step function and `verus.rs::op_step`'s
    transcription; `Model._window` spells the same thing imperatively."""
    arm1, aux1, arm2, aux2 = op

    uc1, (n1, g1), n1s, u1, d1 = printable(arm1, aux1, alloc, s1)   # :1152
    uc2, (n2, g2), n2s, u2, d2 = printable(arm2, aux2, alloc, s2)   # :1153
    del uc1, uc2

    total = n1 + n2                                             # :1180
    alloc.alloc(total + 1)                                      # :1181

    acc = (acc * 31 + total) & MASK
    acc = (acc * 31 + g1) & MASK
    acc = (acc * 31 + g2) & MASK

    # :1187-1192 -- the caller's own teardown, on a slot that IS constructed
    # (`:263` wrote `IS_STRING`), so it takes the `IS_STRING` arm.
    if n1s is not None and n1s[0] == "heap":
        alloc.free(n1s[1])
        n1s = ("dang", n1s[1])
    if n2s is not None and n2s[0] == "heap":
        alloc.free(n2s[1])
        n2s = ("dang", n2s[1])

    # the executor releases the temporary
    alloc.free(total + 1)
    return n1s, n2s, acc, u1 + u2, d1 + d2


def run_ops(ops, fold_w):
    """Implementation 2: the whole window as a fold over pure transitions.
    Returns `(acc, uninit, dblfree)`. ⚠ The two slots start `None` -- the model's
    spelling of "the stack holds what the previous frame left", which it cannot
    represent and does not pretend to."""
    alloc = Alloc()
    s1 = s2 = None
    acc = fold_w & MASK
    nu = nd = 0
    for op in ops:
        s1, s2, acc, u, d = op_step(op, alloc, s1, s2, acc)
        nu += u
        nd += d
    return (acc ^ alloc.tally()) & MASK, nu, nd


def concat_fold(buf, off, len_, buf_len=None):
    """`verus.rs`'s `concat_fold` -- the spelling the derived `ensures` names.
    A pure function of the window bytes."""
    del buf_len
    win = bytes(buf[off: off + len_])
    n_ops, fold_w, ops = unpack(win)
    del n_ops
    return run_ops(ops, fold_w)[0]


def _dumb(win):
    """Implementation 3, sharing no code with 1 or 2.

    Builds every result string with Python concatenation, collects the allocator
    REQUEST SEQUENCE as a flat list of `("a"|"f", size)` without a cache, then
    replays that list through a cache built from scratch. A fold whose range
    moved, or an allocator request that moved in the order, breaks it."""
    cap = (len(win) - 8) // 4
    n = _rd32(win, 0) % (cap + 1)
    acc = _rd32(win, 4) & MASK
    reqs = []
    st = [None, None]           # the two slots

    def f131(bs):
        h = 0
        for ch in bs:
            h = (h * 131 + ch) & MASK
        return h

    for o in range(n):
        p = 8 + 4 * o
        descr = []
        for side in (0, 1):
            a = win[p + 2 * side] % 5
            x = win[p + 1 + 2 * side]
            if a == 0:
                descr.append((1, f131(bytes((97 + x % 26,))), None))
                continue
            if a == 1:
                descr.append((0, 0, ("empty", 0)))
            elif a == 2:
                if x % 2:
                    reqs.append(("a", 2))
                    descr.append((1, f131(b"1"), ("heap", 2)))
                else:
                    descr.append((0, 0, ("empty", 0)))
            elif a == 3:
                reqs.append(("a", 6))
                descr.append((5, f131(b"Array"), ("heap", 6)))
            else:
                if x % 2:
                    descr.append((0, 0, ("empty", 0)))
                else:
                    reqs.append(("a", 31))
                    # ⭐ SPELLED FROM THE LITERALS, not from the PH52_DIG_*
                    # constants: the prefix is folded byte by byte and the digits
                    # are folded in REVERSE, so this arm also checks the constant.
                    ds = ("%d" % x).encode()
                    g = f131(b"Object id #")
                    for ch in ds[::-1]:
                        g = (g * 131 + ch) & MASK
                    descr.append((11 + len(ds), g, ("heap", 31)))
        total = descr[0][0] + descr[1][0]
        reqs.append(("a", total + 1))
        acc = (acc * 31 + total) & MASK
        acc = (acc * 31 + descr[0][1]) & MASK
        acc = (acc * 31 + descr[1][1]) & MASK
        for side in (0, 1):
            newst = descr[side][2]
            if newst is None:
                continue            # the pass-through arm
            if newst[0] == "heap":
                reqs.append(("f", newst[1]))
                newst = ("dang", newst[1])
            st[side] = newst
        reqs.append(("f", total + 1))
    # replay
    cnt = [0] * 11
    na = nf = nh = 0
    by = 0
    for kind, size in reqs:
        r = (size + 7) & ~7
        i = r >> 3
        if kind == "a":
            na += 1
            if i < 11 and cnt[i] > 0:
                cnt[i] -= 1
                nh += 1
            else:
                by += r
        else:
            nf += 1
            if i < 11 and cnt[i] < 256:
                cnt[i] += 1
    t = ((na * TALLY_ALLOC) ^ (nf * TALLY_FREE) ^ (nh * TALLY_CACHE_HIT)
         ^ (by * TALLY_BYTES)) & MASK
    return (acc ^ t) & MASK, reqs


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.nwin = 0
        self._win = []          # per window: (result, n_uninit, n_dblfree)
        self.any_uninit_read = False
        self.any_double_free = False
        if not self.truncated:
            self._run()

    # -- implementation 1: an imperative transcription of the C --------------
    def _window(self, off):
        """(result, n_uninit, n_dblfree) for one window."""
        win = self.buf[off: off + self.stride]
        n_ops, fold_w, ops = unpack(win)
        del n_ops
        alloc = Alloc()
        op1_copy = None          # zend_operators.c:1148 -- BARE
        op2_copy = None
        acc = fold_w & MASK
        nu = nd = 0

        for (arm1, aux1, arm2, aux2) in ops:
            _uc1, (n1, g1), op1_copy, u1, d1 = printable(arm1, aux1, alloc,
                                                         op1_copy)
            _uc2, (n2, g2), op2_copy, u2, d2 = printable(arm2, aux2, alloc,
                                                         op2_copy)
            nu += u1 + u2
            nd += d1 + d2
            total = n1 + n2
            alloc.alloc(total + 1)
            acc = (acc * 31 + total) & MASK
            acc = (acc * 31 + g1) & MASK
            acc = (acc * 31 + g2) & MASK
            if op1_copy is not None and op1_copy[0] == "heap":
                alloc.free(op1_copy[1])
                op1_copy = ("dang", op1_copy[1])
            if op2_copy is not None and op2_copy[0] == "heap":
                alloc.free(op2_copy[1])
                op2_copy = ("dang", op2_copy[1])
            alloc.free(total + 1)

        return (acc ^ alloc.tally()) & MASK, nu, nd

    # -- simulation ---------------------------------------------------------
    def _run(self):
        acc = 0
        if OPS_OFF <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, nu, nd = self._win[k]
                if nu:
                    self.any_uninit_read = True
                if nd:
                    self.any_double_free = True
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
            r = self._win[k][0]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    @property
    def helpers(self):
        """What the derived `ensures` is evaluated against.

        ⚠ `@property`, not a method: `check.py::check_proof_domain` reads `mod.helpers` as an
        ATTRIBUTE and then `ns.update(helpers)`, so a bare method gives
        `TypeError: 'method' object is not iterable` and the gate dies with a
        traceback rather than a verdict. ph53's copy is a `@property` and this
        row's first gate run is how the difference was found.
        """
        return {"concat_fold": concat_fold}

    @property
    def work_per_call(self):
        """The WINDOW, in bytes. ⭐ Every measured window carries exactly `cap`
        ops -- `inputs/gen.py` asserts it -- so the op count is
        `(stride - 8) / 4` exactly and the work really is affine in the
        denominator rather than merely labelled by it. ⚠ ph53 had to declare
        per-window heterogeneity for family B's sake; this row has none, which is
        a property of the corpus and not of the statistic."""
        return self.stride if self.entered else 0

    @property
    def sanitizer_expect(self):
        """⛔⛔⛔ `fires` ON THE TWO **BENIGN** INPUTS AND `clean` ON ALL FOUR
        ADVERSARIAL ONES -- AND THAT INVERSION IS MEASURED, NOT A MISTAKE.

        `check.py::_san_build` is `gcc -O1 -g -fsanitize=address,undefined
        -static-libasan -DSLB_ISOLATED`, with no `ASAN_OPTIONS`. Measured on this
        box, both C rungs, all six inputs:

            input                    R1              R1h
            small.bin                heap-UAF        clean
            large.bin                heap-UAF        clean
            adversarial-dblfree.bin  clean           clean
            adversarial-safe.bin     clean           clean
            adversarial-nowin.bin    clean           clean
            adversarial-trunc.bin    exit 5          exit 5

        ⚠⚠⚠ **IT IS AN ARTEFACT OF THE DETECTOR AND NOT A PROPERTY OF THE MEASURED
        BINARIES, AND HERE IS THE WHOLE MECHANISM.** `ph52_concat_function`'s two
        slots are STACK locals, and the row's benignness is a property of the stack
        being REUSED at the same offset -- which `../inputs/gen.py`'s three
        call-history rules exploit. ASan's fake stack
        (`detect_stack_use_after_return`, default 1 here) breaks that assumption in
        BOTH directions:

          * it usually hands out a FRESHLY ZEROED frame, so `zend.c:243` reads
            `type = 0 = IS_NULL` and `_zval_dtor` no-ops -- measured at **282 of 283**
            `:243`-reaching calls on `small.bin`;
          * ⭐ but **1 in 283** it hands back a RECYCLED frame carrying an older
            call's bytes, and that call's slot named a block `php_shim_reset()` has
            since `free()`d -> **heap-use-after-free**. Traced: `OP 14 arms 0/0`
            (the pass-through arm on BOTH sides, so that call writes neither slot and
            tears down neither), then `OP 15` with the faulting arm on side 1 reading
            `type=3 val=0x503000000058` -- a pointer from several ops back.

        ▶ **So ASan CREATES the fault on an input the real stack keeps clean.** On the
        REAL stack, over the whole 25,000-iteration run, **every** `:243` reads
        `IS_STRING + empty_string` and frees nothing -- which is what the published
        u64 rests on and what R1 == R1h == this model on `small.bin` means.

        ⭐⭐ **AND THE ADVERSARIAL INPUT IS SILENT FOR TWO INDEPENDENT MEASURED
        REASONS**, which is the other half of the inversion: (i) `n_iters = 1` and two
        ops is far too few for the fake stack to recycle, so `:243` reads a freshly
        zeroed frame and the defect the blob exists to trigger does not happen under
        ASan at all; (ii) even when it DOES happen, `php_shim_efree` of a block under
        88 bytes never reaches `free()` (`zend_alloc.c:270-279`), so there is no double
        free for ASan to intercept -- `PROTOCOL_PHP.md` §B1.1's measured fact.

        ⚠ `../NOTES.md` §7 carries the table and the trace. ⛔ **DO NOT READ `fires`
        HERE AS "THE BENIGN CORPUS EXERCISES THE DEFECT".** It does not, on the
        binaries every number in `results-php/` was taken with. This is the same class
        as `RECAP_PHP.md` F102's `0xbe` correction -- a detector-dependent observation
        that must not be recorded as a row property -- with the sign reversed.
        """
        if os.path.basename(self.path) in ("small.bin", "large.bin"):
            return "fires"
        return "clean"

    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"stride={self.stride} nwin={self.nwin} "
                f"cap={cap_of(self.stride) if self.stride else 0} "
                f"calls={self.n_calls} work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"uninit_read={self.any_uninit_read} "
                f"double_free={self.any_double_free} "
                f"checksum={self.checksum}")

    # ------------------------------------------------------------------
    # §A2a rule 2: a domain this file CONSTRUCTS, not the calls the corpus makes
    # ------------------------------------------------------------------
    @staticmethod
    def _synthetic_windows():
        """Windows spanning every shape the measured corpus is FORBIDDEN to
        contain, plus the ones it is required to.

        ⚠ `inputs/` is not a domain (§A2a rule 2). What this sweep has to reach
        that the corpus cannot: the ("dang", n) -> faulting-arm adjacency on
        BOTH sides independently, a faulting arm at op 0 (slot `None`), long
        pass-through runs that carry a state across many ops, and every
        (arm, aux-parity) pair."""
        stride = 8 + 4 * 24
        cap = (stride - 8) // 4

        def win(ops, fold_w=0xABCD1234):
            assert len(ops) <= cap
            b = bytearray()
            b += _u32(len(ops))
            b += _u32(fold_w)
            for (a1, x1, a2, x2) in ops:
                b += bytes((a1, x1, a2, x2))
            b += bytes(stride - len(b))
            return bytes(b)

        # 1. every (arm, aux parity) pair on side 1, with side 2 held at NULL
        for a in range(NARM):
            for par in (0, 1):
                yield win([(a, 2 + par, ARM_NULL, 0)])
        # 2. ... and on side 2, with side 1 held at NULL
        for a in range(NARM):
            for par in (0, 1):
                yield win([(ARM_NULL, 0, a, 2 + par)])
        # 3. THE DEFECT, at op 0 on each side: the slot is None
        yield win([(ARM_OBJECT, 1, ARM_NULL, 0)])
        yield win([(ARM_NULL, 0, ARM_OBJECT, 1)])
        yield win([(ARM_OBJECT, 1, ARM_OBJECT, 1)])
        # 4. THE DEFECT, after a dangling arm, on each side independently
        for dang in ((ARM_BOOL, 1), (ARM_ARRAY, 0), (ARM_OBJECT, 0)):
            yield win([dang + (ARM_NULL, 0), (ARM_OBJECT, 1, ARM_NULL, 0)])
            yield win([(ARM_NULL, 0) + dang, (ARM_NULL, 0, ARM_OBJECT, 1)])
            yield win([dang + dang, (ARM_OBJECT, 1, ARM_OBJECT, 1)])
        # 5. THE DEFECT after a SAFE arm -- must NOT be a double free
        for safe in ((ARM_NULL, 0), (ARM_BOOL, 0), (ARM_OBJECT, 1)):
            yield win([safe + (ARM_NULL, 0), (ARM_OBJECT, 1, ARM_NULL, 0)])
        # 6. the PASS-THROUGH arm carrying a state across a long run
        for pre in ((ARM_ARRAY, 0), (ARM_NULL, 0)):
            yield win([pre + (ARM_NULL, 0)]
                      + [(ARM_STRING, 7, ARM_STRING, 9)] * 6
                      + [(ARM_OBJECT, 1, ARM_NULL, 0)])
        # 7. an empty op stream, and a full one
        yield win([])
        yield win([(o % NARM, o, (o + 2) % NARM, o + 1) for o in range(cap)])
        # 8. the object handle's digit count: 1, 2 and 3 digits, even aux only
        for h in (0, 8, 48, 200, 254):
            yield win([(ARM_OBJECT, h, ARM_OBJECT, h)])
        # 9. every arm against every arm, one op
        for a in range(NARM):
            for b in range(NARM):
                yield win([(a, 4, b, 6)])

    @staticmethod
    def _mutants():
        """Must-FIRE mutants of implementation 2 (§H: a sweep that cannot fail
        is not a check). Each returns a `run_ops`-shaped callable."""

        def m1(ops, fold_w):
            """`:263` writes the tag EARLY -- the tidy ordering the catalogue's
            trap names. Modelled as: the faulting arm leaves the slot SAFE even
            when the previous arm left it dangling, i.e. the double free is
            never seen."""
            alloc = Alloc()
            s1 = s2 = None
            acc = fold_w & MASK
            for op in ops:
                s1, s2, acc, _u, _d = op_step(op, alloc, ("empty", 0),
                                              ("empty", 0), acc)
            return (acc ^ alloc.tally()) & MASK, 0, 0

        def m2(ops, fold_w):
            """`STR_FREE` loses its `!= empty_string` test, so the three SAFE
            arms stop being safe and every repetition double-frees."""
            alloc = Alloc()
            s1 = s2 = None
            acc = fold_w & MASK
            nd = 0
            for op in ops:
                a1, x1, a2, x2 = op
                for (a, x, s) in ((a1, x1, s1), (a2, x2, s2)):
                    if a == ARM_OBJECT and (x & 1) and s is not None:
                        nd += 1
                s1, s2, acc, _u, _d = op_step(op, alloc, s1, s2, acc)
            return (acc ^ alloc.tally()) & MASK, 0, nd

        def m3(ops, fold_w):
            """The pass-through arm (`:190-193`) CLEARS the slot instead of
            leaving it alone -- i.e. the extraction that 'tidies' the common
            path. It makes the call history unobservable."""
            alloc = Alloc()
            s1 = s2 = None
            acc = fold_w & MASK
            nu = nd = 0
            for op in ops:
                a1, _x1, a2, _x2 = op
                if a1 == ARM_STRING:
                    s1 = ("empty", 0)
                if a2 == ARM_STRING:
                    s2 = ("empty", 0)
                s1, s2, acc, u, d = op_step(op, alloc, s1, s2, acc)
                nu += u
                nd += d
            return (acc ^ alloc.tally()) & MASK, nu, nd

        def m4(ops, fold_w):
            """The allocator's cache is ignored: every request reaches malloc.
            It is the `§B1a` precondition being ASSUMED rather than simulated,
            and it is the one mutant a row with O(1) allocations could not
            detect."""
            alloc = Alloc()
            s1 = s2 = None
            acc = fold_w & MASK
            for op in ops:
                s1, s2, acc, _u, _d = op_step(op, alloc, s1, s2, acc)
            bad = Alloc()
            for kind, size in alloc.reqs:
                if kind == "a":
                    bad.n_alloc += 1
                    bad.bytes += real_size(size)
                else:
                    bad.n_free += 1
            return (acc ^ bad.tally()) & MASK, 0, 0

        def e1(ops, fold_w):
            """MUST-NOT-FIRE: an equivalent rewrite of `run_ops` that threads the
            pair as a dict instead of two variables, so the sweep is keyed on the
            FUNCTION and not on the spelling."""
            alloc = Alloc()
            st = {"a": None, "b": None}
            acc = fold_w & MASK
            nu = nd = 0
            for op in ops:
                st["a"], st["b"], acc, u, d = op_step(
                    op, alloc, st["a"], st["b"], acc)
                nu += u
                nd += d
            return (acc ^ alloc.tally()) & MASK, nu, nd

        return {"M1 tag written early": m1,
                "M2 STR_FREE loses empty_string": m2,
                "M3 pass-through clears the slot": m3,
                "M4 allocator cache ignored": m4}, {"E1 dict-threaded rewrite": e1}

    def selfcheck(self):
        """Drive the three implementations against each other, over the calls
        this input makes AND over the synthetic domain, with the mutants."""
        bad = []

        # the C's own constants
        cc = _c_constants()
        want = {"PH52_HDR_BYTES": HDR_BYTES, "PH52_OP_BYTES": OP_BYTES,
                "PH52_NARM": NARM, "PH52_OBJ_PREFIX_LEN": OBJ_PREFIX_LEN,
                "PH52_MAX_LENGTH_OF_LONG": MAX_LENGTH_OF_LONG}
        for k, v in want.items():
            if cc.get(k) != v:
                bad.append(f"c/kernel.h {k} = {cc.get(k)}, model says {v}")
        # ⭐ and the three digest constants against the LITERALS they stand for
        for k, lit, v in (("PH52_DIG_PREFIX", OBJ_PREFIX, DIG_PREFIX),
                          ("PH52_DIG_ARRAY", b"Array", DIG_ARRAY),
                          ("PH52_DIG_ONE", b"1", DIG_ONE)):
            if fold131(lit) != v:
                bad.append(f"{k} = {v} but fold131({lit!r}) = {fold131(lit)}")
        sc = _shim_constants()
        for k, v in (("n_alloc", TALLY_ALLOC), ("n_free", TALLY_FREE),
                     ("n_cache_hit", TALLY_CACHE_HIT),
                     ("bytes_mallocked", TALLY_BYTES)):
            if sc and sc.get(k) != v:
                bad.append(f"emalloc_shim.h tally {k} = {sc.get(k)}, "
                           f"model says {v}")

        # 1 vs 2 vs 3 on every window this input carries
        if self.entered:
            for k in range(self.nwin):
                win = bytes(self.buf[k * self.stride:(k + 1) * self.stride])
                n_ops, fold_w, ops = unpack(win)
                del n_ops
                a = self._win[k][0]
                b = run_ops(ops, fold_w)[0]
                c = _dumb(win)[0]
                if not (a == b == c):
                    bad.append(f"window {k}: imperative {a}, spec {b}, dumb {c}")
                    break

        # 1 vs 2 vs 3 over the SYNTHETIC domain
        wins = list(self._synthetic_windows())
        for i, win in enumerate(wins):
            n_ops, fold_w, ops = unpack(win)
            del n_ops
            b = run_ops(ops, fold_w)
            c = _dumb(win)
            if b[0] != c[0]:
                bad.append(f"synthetic {i}: spec {b[0]}, dumb {c[0]}")
                break

        # the mutants
        fires, nofires = self._mutants()
        for name, fn in fires.items():
            caught = False
            for win in wins:
                n_ops, fold_w, ops = unpack(win)
                del n_ops
                if fn(ops, fold_w) != run_ops(ops, fold_w):
                    caught = True
                    break
            if not caught:
                bad.append(f"MUST-FIRE mutant not caught: {name}")
        for name, fn in nofires.items():
            for win in wins:
                n_ops, fold_w, ops = unpack(win)
                del n_ops
                if fn(ops, fold_w) != run_ops(ops, fold_w):
                    bad.append(f"MUST-NOT-FIRE arm fired: {name}")
                    break

        # the synthetic domain has to REACH what it claims to
        seen_u = seen_d = seen_safe = 0
        arms = set()
        for win in wins:
            n_ops, fold_w, ops = unpack(win)
            del n_ops
            _r, nu, nd = run_ops(ops, fold_w)
            seen_u += nu
            seen_d += nd
            for (a1, _x1, a2, _x2) in ops:
                arms.add(a1)
                arms.add(a2)
        for win in wins:
            n_ops, fold_w, ops = unpack(win)
            del n_ops
            _r, nu, nd = run_ops(ops, fold_w)
            if nu and not nd:
                seen_safe += 1
        if arms != set(range(NARM)):
            bad.append(f"synthetic sweep reaches arms {sorted(arms)}, not all "
                       f"{NARM}")
        if not seen_u:
            bad.append("synthetic sweep never reaches :243 on an "
                       "UNCONSTRUCTED slot")
        if not seen_d:
            bad.append("synthetic sweep never reaches :243 on a DANGLING slot, "
                       "i.e. never reaches the defect's harmful case")
        if not seen_safe:
            bad.append("synthetic sweep has no window where :243 runs and does "
                       "NOT double-free -- the must-NOT-fire direction")
        return bad


def _u32(v):
    return bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF))


def _c_constants():
    """Read `c/kernel.h`'s `#define`s so this file cannot drift from the C."""
    out = {}
    with open(os.path.join(HERE, "c", "kernel.h")) as fh:
        for line in fh:
            m = re.match(r"#define\s+(PH52_\w+)\s+(\(?[\w\s+*-]+\)?)\s*(/\*.*)?$",
                         line)
            if not m:
                continue
            try:
                out[m.group(1)] = int(eval(m.group(2), {"__builtins__": {}},  # noqa: S307
                                           dict(out)))
            except Exception:
                pass
    return out


def _shim_constants():
    """`php_shim_tally()`'s four multipliers, read from the shim itself."""
    p = os.path.join(HERE, "c", "emalloc_shim.h")
    if not os.path.exists(p):
        return {}
    with open(p) as fh:
        txt = fh.read()
    m = re.search(r"php_shim_tally\(void\)\s*\{(.*?)\n\}", txt, re.S)
    if not m:
        return {}
    return {f: int(c) for f, c in
            re.findall(r"php_shim_ag\.(\w+)\s*\*\s*(\d+)u?", m.group(1))}


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        probs = m.selfcheck()
        n = len(list(Model._synthetic_windows()))
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} "
              f"selfcheck={'ok (%d synthetic windows, 4 must-fire, 1 '
                          'must-NOT-fire)' % n if not probs else probs}")
