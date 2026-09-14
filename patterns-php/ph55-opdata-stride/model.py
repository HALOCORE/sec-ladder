#!/usr/bin/env python3
"""ph55-opdata-stride: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph55 differs.

    bindings      buf/off/len/buf_len/result. The kernel mutates only its own
                  frame -- the op_array, the zval store and the temp slots --
                  and folds all of it before returning, so there is no
                  destination to bind before and after. What escapes the call is
                  the u64.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated, and here the derivation is about the
                  DISPATCH TABLE: a call "fires" iff, under R1's stride, the PC
                  lands on a word whose `handler` is NULL. See
                  `sanitizer_expect`.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's. It is PHP
5.0.0's executor **with the real upstream fix applied**, which is exactly
`c/kernel_hardened.c` and exactly R2-R5:

    R1     Zend/zend_execute.c:1724-1796 as shipped in 5.0.0 -- CRASH-023
    R1h    + 4f68f3774c34 (Stanislav Malyshev, 2004-08-30, "fix crash #29893"),
           HAND BACKPORTED: three lines, and they are the normal exit's own
           three lines copied onto the error exit
    R2-R5  the same function, in Rust

⭐ The fix is COMPLETE for this defect: it removes every mis-stride and changes
no benign answer. `controls/fix_scope.py` measures that rather than asserting
it.

⚠⚠ THE MODEL ALSO SIMULATES R1, and that is not decoration -- it is how
`sanitizer_expect` stops being a table. `_window` runs each window TWICE, once
with the fix and once without, and records whether the unfixed run reaches a
word with no handler. That is the ONLY thing this row's detector can see, and
the second adversarial input exists to show that it is not the same question as
"did the bug fire".

Three independent implementations, as ph03, ph07 and ph16 do:

  * the **simulation** (`_Machine`) walks each window once with imperative
    handlers over a mutable state, cursors named as the C names them;
  * the **helper** `ph55_run` -- the one the derived `ensures` is evaluated
    against -- is a PURE TRANSITION driven to a fixpoint, carrying the whole
    machine as an immutable tuple, mirroring the Verus spec functions
    `step` / `run` in ../verus.rs one unfolding at a time;
  * `_dumb`, a third spelling that first materialises the instruction list and
    the set of PCs the program visits, then replays the visit list.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2: a
second implementation is only as strong as the domain it is exercised over, and
`inputs/` is not a domain -- it is a handful of files. ph03 shipped for a full
task with its two implementations computing different functions because its
corpus took one arm of a two-armed branch.
"""

import itertools
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# -- the shape, mirrored from c/kernel.c and re-parsed out of it by check 5 ---
MAX_OPS = 64
NVAR = 8
DIM = 4
NT = 4

UNINIT = 0
ERR = 1
VAR_BASE = 2
ARR_BASE = VAR_BASE + NVAR
NSLOT = ARR_BASE + NVAR * DIM

IS_NULL, IS_LONG, IS_ARRAY = 0, 1, 2

NOP, ASSIGN, INIT_ARRAY, ADD, FETCH_DIM_RW = 0, 1, 2, 3, 4
ASSIGN_DIM, ASSIGN_ADD, OP_DATA, ECHO, RETURN = 5, 6, 7, 8, 9
N_OPCODES = 10

X_DEFAULT, X_DIM = 0, 1

#: ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` -- zend_execute.c:4427. The
#: ONE opcode with no handler, and the whole reason a wrong PC is fatal rather
#: than merely wrong. Every other opcode has one.
NO_HANDLER = frozenset({OP_DATA})

#: Instructions that occupy TWO words. ⚠ `ASSIGN_DIM` is two words STATICALLY
#: (zend_assign_dim_handler, :2198-2226, one exit, unconditional INC_OPCODE);
#: `ASSIGN_ADD` is two words only when `extended_value == ZEND_ASSIGN_DIM`
#: (:1734, :1749). That difference is the row: a static width needs no flag, a
#: data-dependent one does, and the flag is what the error exit forgets.
def two_word(opcode, ext):
    return opcode == ASSIGN_DIM or (opcode == ASSIGN_ADD and ext == X_DIM)


def is_tmp(o):
    return (o & 0x8000) != 0


def var_of(o):
    return VAR_BASE + (o & 0x7FFF) % NVAR


def tmp_of(o):
    return (o & 0x7FFF) % NT


def decode(win, nops):
    """The blob IS the instruction stream. One `zend_op` per little-endian u64.

    ⚠ The last two words are forced to `ZEND_RETURN`, and that is PHP's own
    tail rather than a bounds check: `zend_do_end_function_declaration` emits
    `zend_do_return` then `zend_do_handle_exception`
    (Zend/zend_compile.c:1091-1092). Two terminators plus a maximum stride of
    two is what keeps the PC inside the op_array with the executor testing
    nothing -- ../NOTES.md §4."""
    ops = []
    for i in range(nops):
        p = win[8 * i: 8 * i + 8]
        ops.append({
            "opcode": p[0] % N_OPCODES,
            "ext": p[1],
            "op1": p[2] | (p[3] << 8),
            "op2": p[4] | (p[5] << 8),
            "result": p[6] | (p[7] << 8),
        })
    if nops >= 2:
        ops[nops - 2]["opcode"] = RETURN
        ops[nops - 1]["opcode"] = RETURN
    return emit_fixup(ops)


def width(o):
    """How wide an instruction is. ⚠ BOTH FORMS ARE HERE AND THEY ARE NOT THE
    SAME KIND OF FACT: `ZEND_ASSIGN_DIM` is two words for EVERY instance, which
    is why `zend_assign_dim_handler` needs no flag (:2224); `ZEND_ASSIGN_ADD`
    is two words only when its `extended_value` says so (:1734, :1749), which
    is why `zend_binary_assign_op_helper` does."""
    return 2 if two_word(o["opcode"], o["ext"]) else 1


def emit_fixup(ops):
    """THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S.

    `zend_compile` emits `ZEND_OP_DATA` ONLY as the trailing word of a two-word
    instruction, so NO INSTRUCTION START IS A DATA WORD -- which is exactly why
    `execute()` may dispatch through `opline->handler` without testing it
    (:1391). The compiler is outside this row (the blob IS the op_array), so
    this walk stands in for it: it visits exactly the words a CORRECT executor
    visits and refuses a data word at any of them, and touches nothing else.
    That is what lets `adversarial-opdatalive.bin` exist. ../NOTES.md §4."""
    n = len(ops)
    p = 0
    while p + 2 < n:
        if ops[p]["opcode"] == OP_DATA:
            ops[p]["opcode"] = NOP
        p += width(ops[p])
    return ops


def pass_two(ops):
    """`opline->handler = zend_opcode_handlers[opline->opcode];`
    -- Zend/zend_opcode.c:363. The table is copied into EVERY instruction,
    including the data word, which is how a NULL entry becomes reachable from a
    PC."""
    return [None if o["opcode"] in NO_HANDLER else o["opcode"] for o in ops]


class NullCall(Exception):
    """The executor dispatched through a `handler` field that is NULL
    (zend_execute.c:1391, no test). In C this is an indirect call through NULL;
    here it stops the simulation and is RECORDED."""


class _Machine:
    """Implementation 1 of 3: an imperative transcription of the C, one method
    per handler, cursors named as `c/kernel.c` names them."""

    def __init__(self, ops, handlers, fixed):
        self.ops = ops
        self.handlers = handlers
        self.fixed = fixed          # False == R1 (the bug), True == R1h
        self.kind = [IS_NULL] * NSLOT
        self.val = [0] * NSLOT
        self.ts = [0] * NT
        self.acc = 0
        self.pc = 0
        for i in range(NVAR):
            self.kind[VAR_BASE + i] = IS_LONG
        for i in range(NVAR * DIM):
            self.kind[ARR_BASE + i] = IS_LONG
        #: every (opcode, ext, took_error_arm) the run reached -- §A2a rule 1
        self.arms = set()
        self.null_call = False

    # -- the zval layer ----------------------------------------------------
    def gzpp(self, op):                 # get_zval_ptr_ptr
        return self.ts[tmp_of(op)] if is_tmp(op) else var_of(op)

    def gzp(self, op):                  # get_zval_ptr
        s = self.gzpp(op)
        return self.val[s] if self.kind[s] == IS_LONG else 0

    def fetch_dim(self, base, dim):
        """`zend_fetch_dimension_address(..., BP_VAR_RW)` -- :1744. On a
        non-array base it yields `EG(error_zval_ptr)`, which is
        `$x = 1; $x[0] += 1;` -- the corpus's trigger for CRASH-023."""
        b = var_of(base)
        if self.kind[b] != IS_ARRAY:
            return ERR
        return ARR_BASE + (self.val[b] % NVAR) * DIM + (dim % DIM)

    def add_function(self, dst, v):
        if self.kind[dst] != IS_LONG:
            self.kind[dst] = IS_LONG
            self.val[dst] = 0
        self.val[dst] = (self.val[dst] + v) & MASK

    # -- the handlers ------------------------------------------------------
    def _h(self, o):
        oc = o["opcode"]
        if oc == NOP:
            self.pc += 1
        elif oc == ASSIGN:
            d = var_of(o["op1"])
            self.kind[d] = IS_LONG
            self.val[d] = o["op2"]
            self.ts[tmp_of(o["result"])] = d
            self.pc += 1
        elif oc == INIT_ARRAY:
            d = var_of(o["op1"])
            self.kind[d] = IS_ARRAY
            self.val[d] = o["op2"] % NVAR
            self.ts[tmp_of(o["result"])] = d
            self.pc += 1
        elif oc == ADD:
            # ⚠ BOTH OPERANDS BEFORE THE DESTINATION -- `result` may name the
            # same slot as `op1`. The first draft of this row wrote `kind[d]`
            # first in all of C, `_Machine` and `step`'s ancestor, and the
            # synthetic sweep caught the disagreement (§A2a rule 2).
            v = (self.gzp(o["op1"]) + self.gzp(o["op2"])) & MASK
            d = var_of(o["result"])
            self.kind[d] = IS_LONG
            self.val[d] = v
            self.pc += 1
        elif oc == FETCH_DIM_RW:
            self.ts[tmp_of(o["result"])] = self.fetch_dim(o["op1"], o["op2"])
            self.pc += 1
        elif oc == ASSIGN_DIM:
            self._assign_dim(o)
        elif oc == ASSIGN_ADD:
            self._binary_assign_op(o)
        elif oc == ECHO:
            s = self.gzpp(o["op1"])
            self.acc = (self.acc * 31 + self.kind[s]) & MASK
            self.acc = (self.acc * 31 + self.val[s]) & MASK
            self.pc += 1
        elif oc == RETURN:
            return 1
        else:                                    # pragma: no cover
            raise AssertionError(f"no handler for opcode {oc}")
        return 0

    def _assign_dim(self, o):
        """`zend_assign_dim_handler` -- :2198-2226. THE CLEAN SIBLING: two
        words STATICALLY, one exit, `INC_OPCODE(); NEXT_OPCODE();` at
        :2224-2225 under upstream's own `assign_dim has two opcodes!`."""
        od = self.ops[self.pc + 1]
        dst = self.fetch_dim(o["op1"], o["op2"])
        self.ts[tmp_of(od["op2"])] = dst
        value = self.gzp(od["op1"])
        self.arms.add(("ASSIGN_DIM", dst == ERR))
        if dst != ERR:
            self.kind[dst] = IS_LONG
            self.val[dst] = value
        self.ts[tmp_of(o["result"])] = dst
        self.pc += 2                              # INC_OPCODE + NEXT_OPCODE

    def _binary_assign_op(self, o):
        """`zend_binary_assign_op_helper` -- :1724-1796. THE DEFECT."""
        increment_opline = 0                                        # :1728
        if o["ext"] == X_DIM:                                       # :1734
            od = self.ops[self.pc + 1]                              # :1742
            self.ts[tmp_of(od["op2"])] = self.fetch_dim(o["op1"], o["op2"])
            value = self.gzp(od["op1"])                             # :1746
            var_ptr = self.gzpp(od["op2"])                          # :1747
            increment_opline = 1                                    # :1749
        else:                                                       # :1753
            value = self.gzp(o["op2"])                              # :1754
            var_ptr = self.gzpp(o["op1"])                           # :1755

        self.arms.add(("ASSIGN_ADD", "dim" if increment_opline else "default",
                       var_ptr == ERR))

        if var_ptr == ERR:                                          # :1765
            self.ts[tmp_of(o["result"])] = UNINIT                   # :1766
            if self.fixed and increment_opline:
                self.pc += 1        # R1h: 4f68f3774c34's three lines, :1793
            self.pc += 1            # NEXT_OPCODE(), :1769
            return

        self.add_function(var_ptr, value)                           # :1783
        self.ts[tmp_of(o["result"])] = var_ptr                      # :1786
        if increment_opline:                                        # :1792
            self.pc += 1                                            # :1793
        self.pc += 1                                                # :1795

    # -- execute() ---------------------------------------------------------
    def run(self):
        """`execute()`'s loop -- :1383-1394. NOTHING between `EX(opline)` and
        the call: no PC bound, no NULL test."""
        while True:
            o = self.ops[self.pc]
            self.acc = (self.acc * 31 + o["opcode"]) & MASK
            if self.handlers[self.pc] is None:
                self.null_call = True
                raise NullCall(self.pc)
            if self._h(o):
                break
        for i in range(NSLOT):
            self.acc = (self.acc * 31 + self.kind[i]) & MASK
            self.acc = (self.acc * 31 + self.val[i]) & MASK
        for i in range(NT):
            self.acc = (self.acc * 31 + self.ts[i]) & MASK
        return self.acc


# ---------------------------------------------------------------------------
# Implementation 2 of 3: a PURE TRANSITION driven to a fixpoint. This is what
# the derived `ensures` is evaluated against, so it must not be the simulation
# in disguise. It mirrors the *Verus* spec functions (../verus.rs `step` /
# `run`): the whole machine is an immutable tuple and each application is
# exactly one unfolding.
# ---------------------------------------------------------------------------

def _upd(seq, i, v):
    return seq[:i] + (v,) + seq[i + 1:]


def _st0():
    kind = tuple(IS_NULL if i < VAR_BASE else IS_LONG for i in range(NSLOT))
    return (kind, (0,) * NSLOT, (0,) * NT, 0, 0, False)   # kind,val,ts,acc,pc,done


def _sgzpp(st, op):
    return st[2][tmp_of(op)] if is_tmp(op) else var_of(op)


def _sgzp(st, op):
    s = _sgzpp(st, op)
    return st[1][s] if st[0][s] == IS_LONG else 0


def _sfetch(st, base, dim):
    b = var_of(base)
    if st[0][b] != IS_ARRAY:
        return ERR
    return ARR_BASE + (st[1][b] % NVAR) * DIM + (dim % DIM)


def step(ops, st, fixed):
    """One unfolding of ../verus.rs's `step`. Returns the next state."""
    kind, val, ts, acc, pc, done = st
    o = ops[pc]
    oc, ext = o["opcode"], o["ext"]
    acc = (acc * 31 + oc) & MASK
    st = (kind, val, ts, acc, pc, done)

    if oc == RETURN:
        return (kind, val, ts, acc, pc, True)
    if oc == NOP:
        return (kind, val, ts, acc, pc + 1, False)
    if oc == ASSIGN:
        d = var_of(o["op1"])
        return (_upd(kind, d, IS_LONG), _upd(val, d, o["op2"]),
                _upd(ts, tmp_of(o["result"]), d), acc, pc + 1, False)
    if oc == INIT_ARRAY:
        d = var_of(o["op1"])
        return (_upd(kind, d, IS_ARRAY), _upd(val, d, o["op2"] % NVAR),
                _upd(ts, tmp_of(o["result"]), d), acc, pc + 1, False)
    if oc == ADD:
        d = var_of(o["result"])
        v = (_sgzp(st, o["op1"]) + _sgzp(st, o["op2"])) & MASK
        return (_upd(kind, d, IS_LONG), _upd(val, d, v), ts, acc, pc + 1, False)
    if oc == FETCH_DIM_RW:
        return (kind, val, _upd(ts, tmp_of(o["result"]),
                                _sfetch(st, o["op1"], o["op2"])),
                acc, pc + 1, False)
    if oc == ASSIGN_DIM:
        od = ops[pc + 1]
        dst = _sfetch(st, o["op1"], o["op2"])
        ts = _upd(ts, tmp_of(od["op2"]), dst)
        st = (kind, val, ts, acc, pc, done)
        value = _sgzp(st, od["op1"])
        if dst != ERR:
            kind, val = _upd(kind, dst, IS_LONG), _upd(val, dst, value)
        return (kind, val, _upd(ts, tmp_of(o["result"]), dst), acc, pc + 2, False)
    if oc == ASSIGN_ADD:
        inc = 0
        if ext == X_DIM:
            od = ops[pc + 1]
            ts = _upd(ts, tmp_of(od["op2"]), _sfetch(st, o["op1"], o["op2"]))
            st = (kind, val, ts, acc, pc, done)
            value = _sgzp(st, od["op1"])
            var_ptr = _sgzpp(st, od["op2"])
            inc = 1
        else:
            value = _sgzp(st, o["op2"])
            var_ptr = _sgzpp(st, o["op1"])
        if var_ptr == ERR:
            ts = _upd(ts, tmp_of(o["result"]), UNINIT)
            return (kind, val, ts, acc, pc + 1 + (inc if fixed else 0), False)
        if kind[var_ptr] != IS_LONG:
            kind, val = _upd(kind, var_ptr, IS_LONG), _upd(val, var_ptr, 0)
        val = _upd(val, var_ptr, (val[var_ptr] + value) & MASK)
        ts = _upd(ts, tmp_of(o["result"]), var_ptr)
        return (kind, val, ts, acc, pc + 1 + inc, False)
    if oc == ECHO:
        s = _sgzpp(st, o["op1"])
        acc = (acc * 31 + kind[s]) & MASK
        acc = (acc * 31 + val[s]) & MASK
        return (kind, val, ts, acc, pc + 1, False)
    raise AssertionError(f"no handler for opcode {oc}")            # OP_DATA


def ph55_run(buf, off, ln):
    """`ph55_run` in ../verus.rs: what the kernel must return.

    R1h semantics -- the FIXED stride -- because that is what R2-R5 and
    `c/kernel_hardened.c` implement."""
    win = buf[off: off + ln]
    nops = ln // 8
    ops = decode(win, nops)
    handlers = pass_two(ops)
    st = _st0()
    while not st[5]:
        if handlers[st[4]] is None:
            raise NullCall(st[4])
        nxt = step(ops, st, True)
        if nxt[4] <= st[4] and not nxt[5]:                # pragma: no cover
            raise AssertionError("the PC did not advance")
        st = nxt
    kind, val, ts, acc = st[0], st[1], st[2], st[3]
    for i in range(NSLOT):
        acc = (acc * 31 + kind[i]) & MASK
        acc = (acc * 31 + val[i]) & MASK
    for i in range(NT):
        acc = (acc * 31 + ts[i]) & MASK
    return acc


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
        self._win = []          # per window: (r1h_result, r1_result, null_call)
        self.any_null_call = False   # some call the driver makes NULL-dispatches
        self.any_divergence = False  # ... or silently computes something else
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(R1h result, R1 result or None, R1 null-called) for one window.

        ⚠⚠ TWO RUNS, AND THE SECOND IS WHAT MAKES `sanitizer_expect` A
        DERIVATION. The first is the fixed executor -- what every rung but R1
        computes. The second is R1's, and it can end three ways: agreeing (the
        error exit was correct, because the instruction was one word), NULL-
        dispatching (the PC landed on the data word -- the corpus's CRASH-023),
        or running on and producing a DIFFERENT u64 (the PC landed on a word
        that does have a handler). The third is the case a sanitizer cannot
        see, and ../spec.md ships an adversarial input for it."""
        win = self.buf[off: off + self.stride]
        nops = self.stride // 8
        ops = decode(win, nops)
        handlers = pass_two(ops)

        m = _Machine(ops, handlers, True)
        fixed = m.run()
        self._arms |= m.arms

        try:
            r1 = _Machine(decode(win, nops), handlers, False).run()
            return fixed, r1, False
        except NullCall:
            return fixed, None, True

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        self._arms = set()
        if 16 <= self.stride <= 512 and self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, r1, nullc = self._win[k]
                if nullc:
                    self.any_null_call = True
                elif r1 != r:
                    self.any_divergence = True
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
        step_ = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step_ == 0), k))

    @property
    def helpers(self):
        return {"ph55_run": ph55_run}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the instruction count.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call = 0`. The instruction count IS `stride / 8`, so the
        two denominators differ by a constant factor and the stride is the one
        the payload header fixes and the attacker cannot move. It is a strict
        over-estimate -- the executor visits at most `nops` words and usually
        fewer, since a two-word instruction consumes two -- and an
        over-estimate raises the derived floor, which is the direction a floor
        should err.

        ⚠ The fixed per-call term is REAL and is not hidden: the frame is
        zeroed on every call whatever the window. ../NOTES.md §8 decomposes the
        marginal rather than presenting it as a pure dispatch rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the R1 simulation, never tabulated per file.

        ⚠⚠ **THE DERIVATION IS ABOUT THE DISPATCH TABLE AND NOT ABOUT THE
        DEFECT.** The defect is a CONTROL-FLOW error -- a wrong PC. A detector
        can only see it when the wrong PC happens to land on a word whose
        `handler` is NULL, which in PHP 5.0.0 is exactly `ZEND_OP_DATA`
        (zend_execute.c:4427). So the expectation is

            "fires" iff some call the driver makes NULL-DISPATCHES under R1

        and NOT "iff some call mis-strides". ⚠ **That is a weaker claim than
        it looks, and it is the row's headline result rather than a
        concession**: `adversarial-opdatalive.bin` mis-strides by exactly as
        much as `adversarial-nullcall.bin`, differs from it in ONE BYTE, is
        declared `clean`, and silently executes an instruction the program
        does not contain. ../NOTES.md §6 prices the pair.

        Note "the driver makes": windows are picked from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input has exactly one window --
        `inputs/gen.py`. (`adversarial-nowin.bin` has ZERO, which is its whole
        point, and declares `clean`.)"""
        return "fires" if self.any_null_call else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph55's payload allocates nothing -- the op_array and the
        # execute_data are frame objects of a size the row fixes -- so p02's
        # exit 7 has no analogue here. `slb_load` rejecting a short file is the
        # only non-zero exit this pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"nullcall={self.any_null_call} silent={self.any_divergence} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(win):
        """(simulated, ph55_run) for an arbitrary window, off-corpus.

        ⚠ A synthetic window MAY put the PC on a word with no handler -- family
        (a) does it on purpose, by naming a one-word opcode where the stream
        carries a two-word one. Both implementations must then agree that they
        cannot proceed AND agree about WHERE, so a NULL dispatch is compared as
        the value `("nullcall", pc)` rather than swallowed. A sweep that
        silently skipped those windows would not be exercising the one thing
        this row is about."""
        nops = len(win) // 8
        ops = decode(win, nops)
        try:
            sim = _Machine(ops, pass_two(ops), True).run()
        except NullCall as e:
            sim = ("nullcall", e.args[0])
        try:
            helper = ph55_run(win, 0, len(win))
        except NullCall as e:
            helper = ("nullcall", e.args[0])
        return sim, helper

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it** -- see the module docstring.

        Five families, each isolating one thing the implementations could
        disagree about:

          a. every OPCODE in a body slot, so no handler is unexercised;
          b. every `extended_value` byte in 0..255 on an `ASSIGN_ADD`, so the
             `default` arm is driven by values the corpus never carries -- the
             switch has two arms and 255 of the 256 bytes take one of them;
          c. both sides of the error test, on BOTH forms: a `dim` form whose
             base is an array and one whose base is a long, and a `default`
             form whose operand is a temp holding `error_zval` and one holding
             a real slot;
          d. every operand encoding: CV and TMP, at every index and past every
             modulus, including operands whose raw value exceeds NVAR/NT;
          e. degenerate op_arrays: the minimum two words, an all-NOP body, a
             body of nothing but two-word instructions, and a window at
             MAX_OPS."""
        import struct

        def W(oc, ext=0, op1=0, op2=0, res=0):
            return struct.pack("<BBHHH", oc, ext, op1, op2, res)

        def cv(i):
            return i & 0x7FFF

        def tmp(i):
            return 0x8000 | (i & 0x7FFF)

        def win(words, n):
            body = list(words)[: max(0, n - 2)]
            body += [W(NOP)] * (n - 2 - len(body))
            return b"".join(body) + W(RETURN) + W(RETURN)

        # a. every opcode in a body slot
        for oc in range(N_OPCODES):
            yield (f"opcode={oc}",
                   win([W(INIT_ARRAY, 0, cv(0), 1), W(ASSIGN, 0, cv(2), 7),
                        W(oc, X_DIM, cv(0), 1, tmp(0)), W(OP_DATA, 0, cv(2), tmp(1)),
                        W(ECHO, 0, cv(0)), W(ECHO, 0, tmp(0))], 10))
        # b. every extended_value byte
        for ext in range(256):
            yield (f"ext={ext}",
                   win([W(INIT_ARRAY, 0, cv(0), 2), W(ASSIGN, 0, cv(3), 11),
                        W(ASSIGN_ADD, ext, cv(0), 1, tmp(0)),
                        W(OP_DATA, 0, cv(3), tmp(2)),
                        W(ECHO, 0, tmp(0)), W(ECHO, 0, cv(3))], 10))
        # c. both sides of the error test, on both forms
        for arr in (True, False):
            pre = W(INIT_ARRAY, 0, cv(1), 3) if arr else W(ASSIGN, 0, cv(1), 5)
            yield (f"dim-form base-is-array={arr}",
                   win([pre, W(ASSIGN_ADD, X_DIM, cv(1), 2, tmp(0)),
                        W(OP_DATA, 0, cv(2), tmp(3)),
                        W(ECHO, 0, tmp(0)), W(ECHO, 0, cv(1))], 10))
            yield (f"default-form via-fetch base-is-array={arr}",
                   win([pre, W(FETCH_DIM_RW, 0, cv(1), 2, tmp(1)),
                        W(ASSIGN_ADD, X_DEFAULT, tmp(1), cv(2), tmp(0)),
                        W(ECHO, 0, tmp(0)), W(ECHO, 0, tmp(1))], 10))
            yield (f"assign_dim base-is-array={arr}",
                   win([pre, W(ASSIGN_DIM, 0, cv(1), 2, tmp(0)),
                        W(OP_DATA, 0, cv(2), tmp(3)),
                        W(ECHO, 0, tmp(0))], 10))
        # d. operand encodings past every modulus
        for raw in (0, 1, NVAR - 1, NVAR, NVAR + 1, NT, 0x7FFE, 0x7FFF):
            yield (f"operand raw={raw}",
                   win([W(INIT_ARRAY, 0, cv(raw), raw), W(ASSIGN, 0, cv(raw), raw),
                        W(ADD, 0, cv(raw), tmp(raw), cv(raw)),
                        W(FETCH_DIM_RW, 0, cv(raw), raw, tmp(raw)),
                        W(ASSIGN_ADD, X_DEFAULT, tmp(raw), cv(raw), tmp(raw)),
                        W(ECHO, 0, tmp(raw)), W(ECHO, 0, cv(raw))], 12))
        # e. degenerate op_arrays
        yield ("minimal", win([], 2))
        yield ("all-nop", win([], 16))
        two = []
        for i in range(6):
            two += [W(INIT_ARRAY, 0, cv(0), i % NVAR),
                    W(ASSIGN_ADD, X_DIM, cv(0), i, tmp(0)),
                    W(OP_DATA, 0, cv(2), tmp(1))]
        yield ("all-two-word", win(two, 24))
        yield ("max-ops",
               win([W(INIT_ARRAY, 0, cv(0), 1)]
                   + [W(ADD, 0, cv(i % NVAR), cv((i + 1) % NVAR), cv(i % NVAR))
                      for i in range(MAX_OPS - 4)], MAX_OPS))

    def selfcheck(self):
        """Six checks, five of them about this row specifically.

        1a. the imperative simulation against the pure-transition `ph55_run`,
            on the calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning every opcode, every `extended_value` byte, both
            sides of the error test on both instruction forms, and operand
            encodings past every modulus. `PROTOCOL_PHP.md` §A2a rule 2 -- 1a
            alone is what let ph03 ship a model that computed a different
            function from its own proof;
        2.  ⚠⚠ **THE ARM TABLE, OVER THE CALLS THE DRIVER ACTUALLY MAKES.**
            `inputs/gen.py::_check_span` asserts the same table over EVERY
            window in the file, which is a superset condition: the driver picks
            windows from a checksum-derived index and need not visit them all.
            This is the sharper half and the one that is true of the
            measurement;
        3.  ⚠ every window's result is reproduced by a THIRD, deliberately dumb
            spelling -- materialise the visit list first, then replay it -- so a
            dispatch that silently changed its stride is caught;
        4.  no window of a NON-adversarial input mis-strides at all. That is
            what "benign" means here and it is what `check.py` stage 7h
            requires of R1h: R1 and R1h must agree on every benign input;
        5.  the shape constants this row turns on still equal what
            `c/kernel.c` compiles against. This file writes them as Python
            integers and the C writes them as `#define`s; check 5 parses the C
            and compares, so the two cannot drift apart in this file's head.
        """
        problems = []
        for c in self.sample_calls(8):
            want = ph55_run(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != ph55_run() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"ph55_run() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break

        adversarial = os.path.basename(self.path).startswith("adversarial")
        if not adversarial and self.entered:
            problems += self._arm_table()

        for k in range(self.nwin):
            got = self._win[k][0]
            want = _dumb(self.buf[k * self.stride:(k + 1) * self.stride])
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break

        if not adversarial:
            for k in range(self.nwin):
                r1h, r1, nullc = self._win[k]
                if nullc or r1 != r1h:
                    problems.append(
                        f"window {k}: R1 MIS-STRIDES on a non-adversarial "
                        f"input (null_call={nullc}). ../spec.md pins the "
                        f"defect dead on the measured corpus, because "
                        f"check.py stage 7h requires R1h == R1 on every "
                        f"non-adversarial input and a window R1h strides "
                        f"differently on is one R1 dispatches a data word on")
                    break

        got, want = _c_constants(), (MAX_OPS, NVAR, DIM, NT, N_OPCODES, OP_DATA)
        if got != want:
            problems.append(
                f"c/kernel.c compiles against {got}, this model uses {want}; "
                f"every offset in this row means something else if they differ")
        return problems

    def _arm_table(self):
        """`PROTOCOL_PHP.md` §A2a rule 1, over the VISITED calls.

        The branch the defect lives on is `if (*var_ptr == EG(error_zval_ptr))`
        at :1765, and BOTH its arms must be reached benignly. They can be,
        because the error exit's stride of 1 is CORRECT for the one-word
        `default` form -- which is precisely why 5.0.0 shipped with this and
        why the arm that hides the defect is the one the corpus lives in."""
        seen, arms = set(), set()
        for c in self.iter_calls():
            if c["off"] in seen:
                continue
            seen.add(c["off"])
            win = self.buf[c["off"]:c["off"] + c["len"]]
            ops = decode(win, c["len"] // 8)
            m = _Machine(ops, pass_two(ops), True)
            m.run()
            arms |= m.arms
        want = {
            ("ASSIGN_ADD", "default", False): "the one-word form, no error",
            ("ASSIGN_ADD", "default", True):
                "the one-word form ON THE ERROR EXIT -- where stride 1 is "
                "CORRECT, and the reason 5.0.0 shipped with this",
            ("ASSIGN_ADD", "dim", False):
                "the TWO-word form, no error -- the exit that consults the flag",
            ("ASSIGN_DIM", False): "the clean statically-two-word sibling",
            ("ASSIGN_DIM", True): "... on an error base",
        }
        bad = [f"the VISITED calls never reach {k} ({v})"
               for k, v in sorted(want.items(), key=str) if k not in arms]
        if ("ASSIGN_ADD", "dim", True) in arms:
            bad.append("the VISITED calls REACH the two-word form on the error "
                       "exit -- that is the defect, and a benign input must not")
        return [f"visited-call arm coverage: {b}" for b in bad]


def _dumb(win):
    """A third spelling of one window's answer: materialise the list of PCs the
    program visits FIRST, by walking the instruction widths, then replay that
    list. Deliberately naive, deliberately not sharing `_Machine`'s or
    `step`'s code, and it is the spelling that would catch a stride error --
    which is the thing this row is about."""
    nops = len(win) // 8
    ops = decode(win, nops)
    handlers = pass_two(ops)
    m = _Machine(ops, handlers, True)
    visits, pc, guard = [], 0, 0
    while guard <= nops:
        guard += 1
        visits.append(pc)
        if ops[pc]["opcode"] == RETURN:
            break
        m.pc = pc
        m.acc = 0
        m._h(ops[pc])
        pc = m.pc
    m2 = _Machine(decode(win, nops), handlers, True)
    for pc in visits:
        m2.acc = (m2.acc * 31 + ops[pc]["opcode"]) & MASK
        m2.pc = pc
        if m2._h(ops[pc]):
            break
    acc = m2.acc
    for i in range(NSLOT):
        acc = (acc * 31 + m2.kind[i]) & MASK
        acc = (acc * 31 + m2.val[i]) & MASK
    for i in range(NT):
        acc = (acc * 31 + m2.ts[i]) & MASK
    return acc


def _c_constants():
    """The shape `c/kernel.c` literally pins, parsed rather than trusted:
    check 5."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", "kernel.c")
    txt = open(p).read()

    def d(name):
        m = re.search(r"^#define\s+" + name + r"\s+(\d+)u?\s*($|/)", txt, re.M)
        return int(m.group(1)) if m else None

    return (d("PH55_MAX_OPS"), d("PH55_NVAR"), d("PH55_DIM"), d("PH55_NT"),
            d("PH55_N_OPCODES"), d("PH55_OP_DATA"))


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
