#!/usr/bin/env python3
"""ph56-fetchmode-arith -- the independent reference implementation.

    python3 patterns-php/ph56-fetchmode-arith/model.py inputs/small.bin

⚠⚠ **THIS FILE CARRIES THREE INDEPENDENT SPELLINGS OF ONE ANSWER, AND THAT IS A
PROTOCOL REQUIREMENT RATHER THAN A FLOURISH** (`PROTOCOL_PHP.md` §A2a rule 2):

  1. `_Machine`   -- an IMPERATIVE simulation, mirroring `c/kernel.c`'s shape;
  2. `ph56_run`   -- a PURE FOLD over an immutable state tuple, mirroring
                     `verus.rs`'s `step`/`run` one unfolding at a time, and
                     sharing no code with (1);
  3. `_dumb`      -- materialise the EMITTED OPCODE LIST first, then replay it.
                     Deliberately naive, and it is the spelling that would catch
                     an error in the mode ARITHMETIC, which is what this row is
                     about.

`selfcheck()` drives (1) against (2) **on synthetic windows this file builds**
as well as on the calls the corpus makes, because six `.bin` files are not a
domain: `ph03` shipped for a whole task with its two implementations computing
different functions, and only the corpus's monoculture hid it.

============================================================================
THE MECHANISM THIS FILE RE-DERIVES
============================================================================
PHP 5.0.0's `zend_do_end_variable_parse` (`Zend/zend_compile.c:736-780`)
selects a fetch opcode's ACCESS MODE by arithmetic on the opcode value, over a
layout upstream documents at `zend_compile.h:636-638` -- *the following 18
opcodes are 6 groups of 3 opcodes each, and must remain in that order!*

    BP_VAR_R         -= 3     :756   ✅ guarded at :753-755
    BP_VAR_W          0       :759      legal: `$a[] = 1` is what [] is FOR
    BP_VAR_RW        += 3     :761      unguarded, and clean
    BP_VAR_IS        += 6     :764   ⛔ UNGUARDED -- CRASH-041
    BP_VAR_FUNC_ARG  += 9     :767   ⚠ unguarded, reachable, silent
    BP_VAR_UNSET     += 12    :774   ✅ guarded at :771-773

`isset($a[])` therefore compiles `ZEND_FETCH_DIM_W` (84) with an `IS_UNUSED`
op2 into `ZEND_FETCH_DIM_IS` (90), which `zend_do_isset_or_isempty` immediately
rewrites again into `ZEND_ISSET_ISEMPTY_DIM_OBJ` (115, `:3229`) -- and THAT
handler reads op2 through `get_zval_ptr`, whose `case IS_UNUSED:` is an explicit
`return NULL;` (`:118-121`), and dereferences the result at
`switch (offset->type)` (`:3973`).
"""

import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# -- shape. Mirrors c/kernel.c's #defines; check 5 of selfcheck() PARSES the C
# and compares, so the two cannot drift apart in this file's head.
MAX_STMT = 64
MAX_OPS = 2 * MAX_STMT
NVAR = 8
DIM = 4

UNINIT = 0  # EG(uninitialized_zval) -- THE PROCESS-GLOBAL THE APPEND TAKES
ERR = 1     # EG(error_zval)
VAR_BASE = 2
ARR_BASE = VAR_BASE + NVAR
NSLOT = ARR_BASE + NVAR * DIM

IS_NULL, IS_LONG, IS_ARRAY, IS_STRING = 0, 1, 2, 3

# `znode.op_type` -- zend_compile.h:285-288, upstream's own bit values.
T_CONST, T_VAR, T_UNUSED = 1, 4, 8

# the six access modes -- zend_compile.h:756-762, upstream's own values
BP_R, BP_W, BP_RW, BP_IS, BP_FUNC_ARG, BP_UNSET = 0, 1, 2, 3, 5, 6
MODES = (BP_R, BP_W, BP_RW, BP_IS, BP_FUNC_ARG, BP_UNSET)

# ⭐ the REAL opcode numbers -- zend_compile.h:636-656, :683-684, :713
FETCH_DIM_R = 81
FETCH_W = 83
FETCH_DIM_W = 84
FETCH_OBJ_W = 85
FETCH_DIM_RW = 87
FETCH_IS = 89
FETCH_DIM_IS = 90
FETCH_OBJ_IS = 91
FETCH_DIM_FUNC_ARG = 93
FETCH_DIM_UNSET = 96
ISSET_ISEMPTY_VAR = 114
ISSET_ISEMPTY_DIM_OBJ = 115
ISSET_ISEMPTY_PROP_OBJ = 148

BASES = (FETCH_W, FETCH_DIM_W, FETCH_OBJ_W)
OP2T = (T_UNUSED, T_CONST, T_VAR)

# the six DIM opcodes, and the BP_VAR_* each hands down
DIM_MODE = {
    FETCH_DIM_R: BP_R,
    FETCH_DIM_W: BP_W,
    FETCH_DIM_RW: BP_RW,
    FETCH_DIM_IS: BP_IS,
    # :2084 ARG_SHOULD_BE_SENT_BY_REF picks W or R; by value is the common case
    FETCH_DIM_FUNC_ARG: BP_R,
    FETCH_DIM_UNSET: BP_UNSET,
}


class NullOperand(Exception):
    """`switch (offset->type)` at zend_execute.c:3973 with `offset == NULL`.

    ⭐ In `c/kernel.c` this is a read of address `0x14` -- `offsetof(zval,
    type)` is 20, and a pristine 5.0.0 CLI faults at exactly that. In the four
    Rust rungs it is `Option::unwrap` on `None`. It is ONE program with three
    manifestations; `../NOTES.md` §6 prices them."""


def var_of(o):
    return VAR_BASE + (o % NVAR)


def tmp_of(o):
    return o % MAX_STMT


def decode_stmt(win, i):
    """One STATEMENT record. The blob IS the record stream the parser hands the
    compiler:

        byte 0   mode      BP_VAR_*, as an index into the six
        byte 1   base      which member of the W group the parser built,
                           plus bit 7 = CHAIN (`$a[][d]`)
        byte 2   op2_type  IS_UNUSED / IS_CONST / IS_VAR
        byte 3   op2       the dimension
        bytes 4-5 op1      the container CV slot
        bytes 6-7 result   the result temp

    ⚠ THE PARSER ALWAYS BUILDS THE *W* MEMBER, and that is not an invention:
    the guard's own text is `opline->opcode == ZEND_FETCH_DIM_W`, which can only
    ever be true if the pre-delta opcode is the W one."""
    p = win[8 * i: 8 * i + 8]
    return {
        "mode": MODES[p[0] % 6],
        "chain": 1 if (p[1] & 0x80) else 0,
        "base": BASES[(p[1] & 0x7F) % 3],
        "o2t": OP2T[p[2] % 3],
        "op2": p[3],
        "op1": p[4] | (p[5] << 8),
        "res": p[6] | (p[7] << 8),
    }


def do_end_variable_parse(o, ty, fixed):
    """`zend_do_end_variable_parse` -- zend_compile.c:751-776. ⛔ THE DEFECT.

    `fixed` is R1h: `1e708a5aeb30`'s three inserted lines on the `BP_VAR_IS`
    arm, which are `BP_VAR_R`'s own guard copied across."""
    if ty == BP_R:
        if o["opcode"] == FETCH_DIM_W and o["op2_type"] == T_UNUSED:  # :753
            return False                                             # :754
        o["opcode"] = (o["opcode"] - 3) & 0xFF                       # :756
    elif ty == BP_W:
        pass                                                         # :759
    elif ty == BP_RW:
        o["opcode"] = (o["opcode"] + 3) & 0xFF                       # :761
    elif ty == BP_IS:
        if fixed and o["opcode"] == FETCH_DIM_W and o["op2_type"] == T_UNUSED:
            return False       # 1e708a5aeb30 -- the three lines
        o["opcode"] = (o["opcode"] + 6) & 0xFF                       # :764
    elif ty == BP_FUNC_ARG:
        o["opcode"] = (o["opcode"] + 9) & 0xFF                       # :767
        o["ext"] = 0                                                 # :768
    elif ty == BP_UNSET:
        if o["opcode"] == FETCH_DIM_W and o["op2_type"] == T_UNUSED:  # :771
            return False                                             # :772
        o["opcode"] = (o["opcode"] + 12) & 0xFF                      # :774
    return True


def do_isset_or_isempty(o):
    """`zend_do_isset_or_isempty` -- zend_compile.c:3225-3239. THE SECOND
    REWRITE, and it applies to the LAST opline of the fetch list only."""
    if o["opcode"] == FETCH_IS:
        o["opcode"] = ISSET_ISEMPTY_VAR         # :3227
    elif o["opcode"] == FETCH_DIM_IS:
        o["opcode"] = ISSET_ISEMPTY_DIM_OBJ     # :3229
    elif o["opcode"] == FETCH_OBJ_IS:
        o["opcode"] = ISSET_ISEMPTY_PROP_OBJ    # :3231
    o["ext"] = 1                                # :3239


def compile_window(win, nstmt, fixed):
    """The compiler's one pass. Returns `(ops, nops, bailout, acc)`."""
    ops = [{"opcode": 0, "op1_type": 0, "op2_type": 0, "ext": 0,
            "op1": 0, "op2": 0, "result": 0} for _ in range(MAX_OPS)]
    nops, bailout, acc = 0, 0, 0
    for i in range(nstmt):
        s = decode_stmt(win, i)
        first = nops
        if nops + 1 + s["chain"] > MAX_OPS:
            break
        if s["chain"]:
            ops[nops].update(opcode=FETCH_DIM_W, op1_type=T_CONST,
                             op2_type=T_UNUSED, ext=0, op1=s["op1"], op2=0,
                             result=(s["res"] + 1) & 0xFFFF)
            nops += 1
        ops[nops].update(
            opcode=s["base"], op1_type=T_CONST,
            op2_type=T_UNUSED if s["base"] == FETCH_W else s["o2t"], ext=0,
            op1=(s["res"] + 1) & 0xFFFF if s["chain"] else s["op1"],
            op2=s["op2"], result=s["res"])
        nops += 1

        broke = False
        for k in range(first, nops):
            if not do_end_variable_parse(ops[k], s["mode"], fixed):
                bailout, nops, broke = 1, 0, True   # zend_bailout()
                break
            acc = (acc * 31 + ops[k]["opcode"]) & MASK
        if broke:
            break
        if s["mode"] == BP_IS:
            do_isset_or_isempty(ops[nops - 1])       # :3223 -- the LAST only
            acc = (acc * 31 + ops[nops - 1]["opcode"]) & MASK
    return ops, nops, bailout, acc


def _init_slots():
    """`EG(uninitialized_zval)`, `EG(error_zval)` and the symbol table, exactly
    as `kernel()` builds them. A slot is `[lval, refcount, ty]` -- `value_hi`
    and `is_ref` exist in the C struct only to put `type` at offset 20 and are
    never folded, in either language."""
    slots = [[0, 0, IS_NULL] for _ in range(NSLOT)]
    slots[UNINIT] = [0, 1, IS_NULL]
    slots[ERR] = [0, 1, IS_NULL]
    for i in range(NVAR):
        s = VAR_BASE + i
        if i % 2 == 0:
            slots[s] = [i, 1, IS_ARRAY]
        elif i == 1:
            slots[s] = [0, 1, IS_STRING]
        else:
            slots[s] = [i * 7, 1, IS_LONG]
    for i in range(NVAR * DIM):
        slots[ARR_BASE + i] = [0, 1, IS_NULL]
    return slots


# ============================ IMPLEMENTATION 1 =============================
class _Machine:
    """The IMPERATIVE simulation -- `c/kernel.c`'s shape, statement by
    statement. `arms` records which arm of the mode switch each statement took,
    so `inputs/gen.py` can ASSERT reachability rather than describe it."""

    def __init__(self, win, nstmt, fixed):
        self.fixed = fixed
        self.slots = _init_slots()
        self.anext = [0] * NVAR
        self.ts = [0] * MAX_STMT
        self.bailout = 0
        self.arms = set()
        self.ops, self.nops, self.bailout, self.acc = \
            compile_window(win, nstmt, fixed)
        for i in range(nstmt):
            s = decode_stmt(win, i)
            self.arms.add((s["mode"], s["o2t"] if s["base"] != FETCH_W
                           else T_UNUSED, s["base"], s["chain"]))

    # `_get_zval_ptr` -- zend_execute.c:88-125. ⭐ `case IS_UNUSED: return NULL`
    def gzp(self, op_type, op):
        if op_type == T_CONST:
            return var_of(op)
        if op_type == T_VAR:
            return self.ts[tmp_of(op)] % NSLOT
        return None                                              # :120

    # `zend_fetch_dimension_address` -- zend_execute.c:896-975
    def fetch_dim(self, op1, op2_type, op2, ty):
        b = var_of(op1)
        if self.slots[b][2] == IS_NULL and ty in (BP_W, BP_RW):  # :914-927
            self.slots[b] = [b - VAR_BASE, self.slots[b][1], IS_ARRAY]
            self.anext[b - VAR_BASE] = 0
        t = self.slots[b][2]
        if t == IS_ARRAY:                                        # :930
            a = self.slots[b][0] % NVAR
            if op2_type == T_UNUSED:                             # :935 THE APPEND
                n = self.anext[a]
                self.slots[UNINIT][1] = (self.slots[UNINIT][1] + 1) & 0xFFFFFFFF
                if n >= DIM:                                     # :939 FAILURE
                    self.slots[UNINIT][1] = \
                        (self.slots[UNINIT][1] - 1) & 0xFFFFFFFF  # :942
                    return UNINIT                                # :941
                self.anext[a] = (n + 1) & 0xFFFF
                s = ARR_BASE + a * DIM + n
                self.slots[s] = [0, self.slots[s][1], IS_NULL]
                return s
            return ARR_BASE + a * DIM + (op2 % DIM)              # :944
        if t == IS_STRING:                                       # :959
            if op2_type == T_UNUSED:
                self.bailout = 2       # :963-964 -- ⭐ STRINGS *ARE* GUARDED
                return ERR
            return UNINIT
        if t == IS_NULL:                                         # :949-957
            return UNINIT
        return ERR      # "Cannot use a scalar value as an array"

    def run(self):
        if self.bailout == 0:
            for pc in range(self.nops):
                if self.bailout != 0:
                    break
                o = self.ops[pc]
                self.acc = (self.acc * 31 + o["opcode"]) & MASK
                oc = o["opcode"]
                if oc in DIM_MODE:
                    self.ts[tmp_of(o["result"])] = self.fetch_dim(
                        o["op1"], o["op2_type"], o["op2"], DIM_MODE[oc])
                elif oc == ISSET_ISEMPTY_DIM_OBJ:
                    c = var_of(o["op1"])                          # :3960
                    off = self.gzp(o["op2_type"], o["op2"])       # :3961
                    isset = result = 0
                    if self.slots[c][2] == IS_ARRAY:              # :3967
                        a = self.slots[c][0] % NVAR
                        if off is None:
                            # ⛔ :3973 `switch (offset->type)` through NULL
                            raise NullOperand(pc)
                        if self.slots[off][2] == IS_LONG:
                            idx = self.slots[off][0] % DIM
                            s = ARR_BASE + a * DIM + idx
                            if idx < self.anext[a]:
                                isset = 1
                                if self.slots[s][2] != IS_NULL:
                                    result = 1
                    self.acc = (self.acc * 31 + isset) & MASK
                    self.acc = (self.acc * 31 + result) & MASK
                elif oc == ISSET_ISEMPTY_VAR:
                    v = var_of(o["op1"])
                    self.acc = (self.acc * 31
                                + (1 if self.slots[v][2] != IS_NULL else 0)) & MASK
                else:
                    self.ts[tmp_of(o["result"])] = var_of(o["op1"])
        acc = (self.acc * 31 + self.bailout) & MASK
        for i in range(NSLOT):
            acc = (acc * 31 + self.slots[i][2]) & MASK
            acc = (acc * 31 + self.slots[i][0]) & MASK
            acc = (acc * 31 + self.slots[i][1]) & MASK
        for i in range(NVAR):
            acc = (acc * 31 + self.anext[i]) & MASK
        return acc


# ============================ IMPLEMENTATION 2 =============================
# A PURE FOLD over an immutable state tuple, sharing no code with `_Machine`.
# `verus.rs`'s `step`/`run` are this function, one unfolding at a time.

def _st0():
    return (tuple(tuple(s) for s in _init_slots()), (0,) * NVAR,
            (0,) * MAX_STMT, 0, 0)   # slots, anext, ts, acc, bailout


def _upd(seq, i, v):
    return seq[:i] + (v,) + seq[i + 1:]


def _s_gzp(st, op_type, op):
    if op_type == T_CONST:
        return var_of(op)
    if op_type == T_VAR:
        return st[2][tmp_of(op)] % NSLOT
    return None


def _s_fetch(st, op1, op2_type, op2, ty):
    """Pure `zend_fetch_dimension_address`. Returns `(st', slot)`."""
    slots, anext, ts, acc, bail = st
    b = var_of(op1)
    if slots[b][2] == IS_NULL and ty in (BP_W, BP_RW):
        slots = _upd(slots, b, (b - VAR_BASE, slots[b][1], IS_ARRAY))
        anext = _upd(anext, b - VAR_BASE, 0)
    t = slots[b][2]
    if t == IS_ARRAY:
        a = slots[b][0] % NVAR
        if op2_type == T_UNUSED:
            n = anext[a]
            u = slots[UNINIT]
            slots = _upd(slots, UNINIT, (u[0], (u[1] + 1) & 0xFFFFFFFF, u[2]))
            if n >= DIM:
                u = slots[UNINIT]
                slots = _upd(slots, UNINIT,
                             (u[0], (u[1] - 1) & 0xFFFFFFFF, u[2]))
                return (slots, anext, ts, acc, bail), UNINIT
            anext = _upd(anext, a, (n + 1) & 0xFFFF)
            s = ARR_BASE + a * DIM + n
            slots = _upd(slots, s, (0, slots[s][1], IS_NULL))
            return (slots, anext, ts, acc, bail), s
        return (slots, anext, ts, acc, bail), ARR_BASE + a * DIM + (op2 % DIM)
    if t == IS_STRING:
        if op2_type == T_UNUSED:
            return (slots, anext, ts, acc, 2), ERR
        return (slots, anext, ts, acc, bail), UNINIT
    if t == IS_NULL:
        return (slots, anext, ts, acc, bail), UNINIT
    return (slots, anext, ts, acc, bail), ERR


def step(st, o, pc):
    """One dispatch, as a pure transition. `verus.rs::step` is this."""
    slots, anext, ts, acc, bail = st
    if bail != 0:
        return st, True
    oc = o["opcode"]
    acc = (acc * 31 + oc) & MASK
    st = (slots, anext, ts, acc, bail)
    if oc in DIM_MODE:
        st, s = _s_fetch(st, o["op1"], o["op2_type"], o["op2"], DIM_MODE[oc])
        slots, anext, ts, acc, bail = st
        ts = _upd(ts, tmp_of(o["result"]), s)
        return (slots, anext, ts, acc, bail), False
    if oc == ISSET_ISEMPTY_DIM_OBJ:
        c = var_of(o["op1"])
        off = _s_gzp(st, o["op2_type"], o["op2"])
        isset = result = 0
        if slots[c][2] == IS_ARRAY:
            a = slots[c][0] % NVAR
            if off is None:
                raise NullOperand(pc)
            if slots[off][2] == IS_LONG:
                idx = slots[off][0] % DIM
                s = ARR_BASE + a * DIM + idx
                if idx < anext[a]:
                    isset = 1
                    if slots[s][2] != IS_NULL:
                        result = 1
        acc = (acc * 31 + isset) & MASK
        acc = (acc * 31 + result) & MASK
        return (slots, anext, ts, acc, bail), False
    if oc == ISSET_ISEMPTY_VAR:
        v = var_of(o["op1"])
        acc = (acc * 31 + (1 if slots[v][2] != IS_NULL else 0)) & MASK
        return (slots, anext, ts, acc, bail), False
    ts = _upd(ts, tmp_of(o["result"]), var_of(o["op1"]))
    return (slots, anext, ts, acc, bail), False


def ph56_run(buf, off, ln, fixed=True):
    """THE SECOND IMPLEMENTATION, and the one `spec.md`'s `ensures` names.

    ⚠ It re-derives the compile pass from the bytes rather than reusing
    `_Machine`'s, and then folds a pure state tuple. Nothing is shared."""
    win = bytes(buf[off: off + ln])
    nstmt = min(ln // 8, MAX_STMT)
    ops, nops, bail0, cacc = compile_window(win, nstmt, fixed)
    slots, anext, ts, _, _ = _st0()
    st = (slots, anext, ts, cacc, bail0)
    if bail0 == 0:
        for pc in range(nops):
            st, stop = step(st, ops[pc], pc)
            if stop:
                break
    slots, anext, ts, acc, bail = st
    acc = (acc * 31 + bail) & MASK
    for i in range(NSLOT):
        acc = (acc * 31 + slots[i][2]) & MASK
        acc = (acc * 31 + slots[i][0]) & MASK
        acc = (acc * 31 + slots[i][1]) & MASK
    for i in range(NVAR):
        acc = (acc * 31 + anext[i]) & MASK
    return acc


# ============================ IMPLEMENTATION 3 =============================
# ⭐ The mode switch written as a TABLE rather than as branches. This is the
# third spelling's whole point: `compile_window` reproduces upstream's `switch`
# arm for arm, and a transposed delta there would be invisible to any check that
# re-ran the same code. Reading the six deltas off `zend_compile.c:756-774` into
# a dict and applying them by lookup is the one spelling that cannot share that
# mistake. ⚠ `GUARDED` is the set of arms that carry the append-dim test, and
# `BP_IS` is in it only under R1h -- which is exactly what `1e708a5aeb30` adds.
DELTA = {BP_R: -3, BP_W: 0, BP_RW: 3, BP_IS: 6, BP_FUNC_ARG: 9, BP_UNSET: 12}
GUARDED_R1 = frozenset({BP_R, BP_UNSET})
GUARDED_R1H = frozenset({BP_R, BP_UNSET, BP_IS})
ISSET_REWRITE = {FETCH_IS: ISSET_ISEMPTY_VAR,
                 FETCH_DIM_IS: ISSET_ISEMPTY_DIM_OBJ,
                 FETCH_OBJ_IS: ISSET_ISEMPTY_PROP_OBJ}


def _emit_by_table(win, nstmt, fixed):
    """The emitted opcode sequence, by TABLE LOOKUP. Returns `(opcodes, bail)`."""
    guarded = GUARDED_R1H if fixed else GUARDED_R1
    out, bail, n = [], 0, 0
    for i in range(nstmt):
        s = decode_stmt(win, i)
        pre = []
        if s["chain"]:
            pre.append((FETCH_DIM_W, T_UNUSED))
        pre.append((s["base"],
                    T_UNUSED if s["base"] == FETCH_W else s["o2t"]))
        if n + len(pre) > MAX_OPS:
            break
        emitted = []
        for (oc, o2t) in pre:
            if oc == FETCH_DIM_W and o2t == T_UNUSED and s["mode"] in guarded:
                bail = 1
                break
            emitted.append((oc + DELTA[s["mode"]]) & 0xFF)
        if bail:
            break
        if s["mode"] == BP_IS:
            emitted[-1] = ISSET_REWRITE.get(emitted[-1], emitted[-1])
        out += emitted
        n += len(emitted)
    return (([], 1) if bail else (out, 0))


def _dumb(win, nstmt):
    """A THIRD spelling: derive the EMITTED OPCODE SEQUENCE by table lookup --
    sharing no branch with `compile_window` -- check it against what the
    compiler actually emitted, and only then replay. It is the spelling that
    would catch an error in the mode ARITHMETIC, which is what this row is
    about."""
    want_ops, want_bail = _emit_by_table(win, nstmt, True)
    m = _Machine(win, nstmt, True)
    got_ops = [m.ops[k]["opcode"] for k in range(m.nops)]
    if want_ops != got_ops or want_bail != m.bailout:
        return ("emit-mismatch", want_ops[:8], got_ops[:8],
                want_bail, m.bailout)
    return m.run()


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
        self._win = []            # per window: (r1h, r1 or None, null_operand)
        self.any_null_operand = False
        self.any_divergence = False
        self._arms = set()
        if not self.truncated:
            self._run()

    def _window(self, off):
        """`(R1h result, R1 result or None, R1 dereferenced NULL)`.

        ⚠⚠ TWO RUNS, AND THE SECOND IS WHAT MAKES `sanitizer_expect` A
        DERIVATION. The first is the FIXED compiler -- what R1h and all four
        Rust rungs compute. The second is R1's, and it can end three ways:
        agreeing (no statement asked for `BP_VAR_IS` on an append dim),
        dereferencing NULL (the corpus's CRASH-041), or running on and producing
        a DIFFERENT u64 -- which is the CHAIN case, where the surviving
        `ZEND_FETCH_DIM_IS` silently APPENDS to the array. The third is the one
        no detector in this tree can see."""
        win = self.buf[off: off + self.stride]
        nstmt = min(self.stride // 8, MAX_STMT)
        m = _Machine(win, nstmt, True)
        fixed = m.run()
        self._arms |= m.arms
        try:
            r1 = _Machine(win, nstmt, False).run()
            return fixed, r1, False
        except NullOperand:
            return fixed, None, True

    def _run(self):
        acc = 0
        if 16 <= self.stride <= 512 and self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, r1, nullop = self._win[k]
                if nullop:
                    self.any_null_operand = True
                elif r1 != r:
                    self.any_divergence = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
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
        step_ = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step_ == 0), k))

    @property
    def helpers(self):
        return {"ph56_run": ph56_run}

    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone. The
        statement count is `stride / 8`, an exact linear function of it, and the
        stride is what the payload header fixes and the attacker cannot move.

        ⚠ THE FIXED PER-CALL TERM IS REAL AND IS NOT HIDDEN: the op_array, the
        42-slot store and the temp vector are built on EVERY call whatever the
        window. ../NOTES.md §8 decomposes the marginal rather than presenting it
        as a pure compile rate."""
        return self.stride if self.entered else 0

    @property
    def sanitizer_expect(self):
        """Derived from the R1 simulation, never tabulated per file.

        ⚠⚠ **`fires` IFF SOME CALL THE DRIVER MAKES DEREFERENCES NULL** -- not
        *iff some statement mis-compiles*. The chain case mis-compiles by
        exactly as much, silently appends to the array, and is declared `clean`
        because there is nothing for a detector to say. That is the row's
        headline result and not a concession; ../NOTES.md §6 prices the pair."""
        return "fires" if self.any_null_operand else "clean"

    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"nullop={self.any_null_operand} silent={self.any_divergence} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(win, nstmt):
        try:
            sim = _Machine(win, nstmt, True).run()
        except NullOperand as e:
            sim = ("nullop", e.args[0])
        try:
            helper = ph56_run(win, 0, len(win))
        except NullOperand as e:
            helper = ("nullop", e.args[0])
        return sim, helper

    @staticmethod
    def _synthetic_windows():
        """⚠⚠ `PROTOCOL_PHP.md` §A2a rule 2. Six `.bin` files are not a domain.

        Families:
          (a) EVERY (mode, base, op2_type, chain) product -- 6*3*3*2 = 108
              statements, each in its own window. This is the whole cross
              product of the switch the row is about;
          (b) every op1 residue past `% NVAR` and every op2 residue past `% DIM`;
          (c) the APPEND arm driven past `DIM`, so :939's FAILURE branch and its
              `refcount--` are exercised;
          (d) chains of chains, so the `:3223` last-opline rule is checked
              against a fetch list of length 2 as well as 1;
          (e) degenerate windows -- all-zero records, all-0xFF records, and the
              minimum two-statement window."""
        def rec(mode_i, base_i, o2t_i, chain, op1=0, op2=0, res=0):
            return bytes([mode_i % 6,
                          (base_i % 3) | (0x80 if chain else 0),
                          o2t_i % 3, op2 & 0xFF,
                          op1 & 0xFF, (op1 >> 8) & 0xFF,
                          res & 0xFF, (res >> 8) & 0xFF])

        # (a) the full cross product, each statement in a two-statement window
        for m in range(6):
            for b in range(3):
                for t in range(3):
                    for ch in (0, 1):
                        yield (f"a:mode{m}/base{b}/o2t{t}/chain{ch}",
                               rec(m, b, t, ch, op1=m + b, op2=t)
                               + rec(1, 1, 1, 0, op1=1, op2=1))
        # (b) operand residues past every modulus
        for op1 in (0, 7, 8, 9, 255, 256, 65535):
            for op2 in (0, 3, 4, 5, 255):
                yield (f"b:op1={op1}/op2={op2}",
                       rec(1, 1, 1, 0, op1=op1, op2=op2)
                       + rec(3, 1, 1, 0, op1=op1, op2=op2))
        # (c) the append arm driven past DIM -- :939 FAILURE and :942 refcount--
        for n in (1, 2, 3, 4, 5, 6):
            yield (f"c:append x{n}", b"".join(
                rec(1, 1, 0, 0, op1=0) for _ in range(n)) + rec(1, 1, 1, 0))
        # (d) a chain followed by more statements
        for n in (1, 2, 3):
            yield (f"d:chain x{n}", b"".join(
                rec(3, 1, 1, 1, op1=0, res=i) for i in range(n))
                + rec(1, 1, 1, 0))
        # (e) degenerate
        yield ("e:zero", bytes(16))
        yield ("e:ff", b"\xff" * 16)
        yield ("e:min", rec(1, 1, 1, 0) + rec(1, 1, 1, 0))
        yield ("e:full", b"".join(rec(i % 6, i % 3, i % 3, i % 2, op1=i, op2=i,
                                      res=i) for i in range(MAX_STMT)))

    def selfcheck(self):
        """Five checks, four of them about this row specifically.

        1a. the imperative simulation against the pure-fold `ph56_run`, on the
            calls this input actually makes;
        1b. ⚠⚠ the same two implementations on SYNTHETIC windows this file
            builds, spanning the whole (mode x base x op2_type x chain) cross
            product, operand residues past every modulus, the append arm past
            `DIM`, and five degenerate shapes. `PROTOCOL_PHP.md` §A2a rule 2 --
            1a alone is what let ph03 ship a model that computed a different
            function from its own proof;
        2.  ⚠ every window's result is reproduced by the THIRD, deliberately
            dumb spelling, which reads the EMITTED OPCODE LIST off the compiler
            and replays it -- so a mode-arithmetic error is caught;
        3.  no window of a NON-adversarial input mis-compiles at all. That is
            what "benign" means here and it is what `check.py` stage 7h requires
            of R1h: R1 and R1h must agree on every benign input;
        4.  the shape constants this row turns on still equal what `c/kernel.c`
            compiles against, PARSED out of the C rather than trusted."""
        problems = []
        for c in self.sample_calls(8):
            want = ph56_run(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != ph56_run() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            nstmt = min(len(win) // 8, MAX_STMT)
            sim, helper = self._both(win, nstmt)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"ph56_run() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break

        for k in range(self.nwin):
            win = self.buf[k * self.stride:(k + 1) * self.stride]
            nstmt = min(self.stride // 8, MAX_STMT)
            got, want = self._win[k][0], _dumb(win, nstmt)
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break

        adversarial = os.path.basename(self.path).startswith("adversarial")
        if not adversarial:
            for k in range(self.nwin):
                r1h, r1, nullop = self._win[k]
                if nullop or r1 != r1h:
                    problems.append(
                        f"window {k}: R1 MIS-COMPILES on a non-adversarial "
                        f"input (null_operand={nullop}). ../spec.md pins the "
                        f"defect dead on the measured corpus, because check.py "
                        f"stage 7h requires R1h == R1 on every non-adversarial "
                        f"input")
                    break

        got, want = _c_constants(), (MAX_STMT, NVAR, DIM, FETCH_DIM_W,
                                     ISSET_ISEMPTY_DIM_OBJ, T_UNUSED)
        if got != want:
            problems.append(
                f"c/kernel.c compiles against {got}, this model uses {want}; "
                f"every opcode in this row means something else if they differ")
        return problems


def _c_constants():
    """The shape `c/kernel.c` literally pins, parsed rather than trusted."""
    txt = open(os.path.join(HERE, "c", "kernel.c")).read()

    def d(name):
        m = re.search(r"^#define\s+" + name + r"\s+(\d+)u?\s*($|/)", txt, re.M)
        return int(m.group(1)) if m else None

    return (d("PH56_MAX_STMT"), d("PH56_NVAR"), d("PH56_DIM"),
            d("PH56_FETCH_DIM_W"), d("PH56_ISSET_ISEMPTY_DIM_OBJ"),
            d("PH56_IS_UNUSED"))


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
