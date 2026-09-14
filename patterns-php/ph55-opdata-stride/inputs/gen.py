#!/usr/bin/env python3
"""ph55-opdata-stride: build the input corpus.

    python3 patterns-php/ph55-opdata-stride/inputs/gen.py

`.bin` files are gitignored and re-derivable; this script is the generator and
it is the committed artefact (`CLAUDE.md` constraint 6).

THE PAYLOAD is `slb.head1_u64_bytes`: one head word (`stride`, the window in
BYTES) followed by the blob. ⭐ **The blob IS the instruction stream** -- one
`zend_op` per little-endian u64:

    byte 0    opcode          byte 1    extended_value
    bytes 2-3 op1             bytes 4-5 op2           bytes 6-7 result

and an operand is a CV slot unless its top bit is set, in which case it is a
temp (`IS_VAR`). This is the one candidate in the catalogue whose ORIGINAL C
SHAPE is the pinned kernel shape, so nothing is translated.

⚠⚠ **WHAT `_check_span` ASSERTS, AND WHY EACH HALF IS THERE**
(`PROTOCOL_PHP.md` §A2a rule 1):

  1. every BENIGN window reaches BOTH ARMS of the branch the defect lives on --
     `if (*var_ptr == EG(error_zval_ptr))` at zend_execute.c:1765. ⭐ It CAN,
     and that is the whole reason PHP 5.0.0 shipped with this defect: the error
     exit's stride of 1 is **CORRECT** for the one-word `default` form. The arm
     that hides the bug is the arm the corpus lives in.
  2. NO benign window reaches the CONJUNCTION -- the error exit with
     `increment_opline == 1`. That one cannot be benign: it IS the defect, and
     a window that reached it would make `c/kernel.c` dispatch a data word on a
     measured input. `check.py` stage 7h requires R1h == R1 on every
     non-adversarial input and would refuse it.
  3. every handler in the table is dispatched, so no opcode ships unexercised.

Assertions, not comments. `ph03` shipped a corpus whose own generator comment
described an arm it never emitted, and the model was wrong for a whole task.
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(ROOT, "common"))
sys.path.insert(0, os.path.join(HERE, ".."))
import slb    # noqa: E402
import model  # noqa: E402

M = model

# -- the assembler -----------------------------------------------------------


def W(oc, ext=0, op1=0, op2=0, res=0):
    """One instruction word."""
    return struct.pack("<BBHHH", oc, ext, op1, op2, res)


def cv(i):
    """A CV operand -- `$x`, an IS_CV slot."""
    return i & 0x7FFF


def tmp(i):
    """A temp operand -- an IS_VAR slot, i.e. `EX(Ts)[i].var.ptr_ptr`."""
    return 0x8000 | (i & 0x7FFF)


# ⚠ Every phrase is SELF-CONTAINED with respect to its own preconditions. A
# two-word `ASSIGN_ADD` must not hit the error arm on a benign input, so the
# phrase that emits one re-establishes its base as an array IMMEDIATELY before
# it -- `$a = array(); $a[d] += k;` is one PHP statement pair and it is the
# only shape that can promise this without the generator carrying its own
# interpreter.

def p_dim_add(a, d, k):
    """`$a = array(); $a[d] += $k;` -- ASSIGN_ADD, TWO WORDS, no error.
    The arm the flag exists for, and the exit that consults it (:1792)."""
    return [W(M.INIT_ARRAY, 0, cv(0), a),
            W(M.ASSIGN_ADD, M.X_DIM, cv(0), d, tmp(0)),
            W(M.OP_DATA, 0, cv(k), tmp(1))]


def p_default_err(v, d, k):
    """`$x = k; $t = &$x[d]; $t += $y;` -- ASSIGN_ADD, ONE word, ON THE ERROR
    EXIT. ⭐ The fetch on a scalar base yields `EG(error_zval_ptr)`, so :1765
    is TRUE and :1769 strides 1 -- which is CORRECT here, because
    `increment_opline` is 0. This is the arm that makes the defect invisible in
    ordinary code."""
    return [W(M.ASSIGN, 0, cv(v), k),
            W(M.FETCH_DIM_RW, 0, cv(v), d, tmp(2)),
            W(M.ASSIGN_ADD, M.X_DEFAULT, tmp(2), cv((v + 1) % M.NVAR), tmp(0))]


def p_default_ok(v, w):
    """`$y += $z;` -- ASSIGN_ADD, ONE word, no error. The normal exit with the
    flag clear."""
    return [W(M.ASSIGN_ADD, M.X_DEFAULT, cv(v), cv(w), tmp(0))]


def p_assign_dim_ok(a, d, k):
    """`$b = array(); $b[d] = $k;` -- zend_assign_dim_handler (:2198-2226), the
    CLEAN statically-two-word sibling. One exit, unconditional INC_OPCODE."""
    return [W(M.INIT_ARRAY, 0, cv(1), a),
            W(M.ASSIGN_DIM, 0, cv(1), d, tmp(0)),
            W(M.OP_DATA, 0, cv(k), tmp(3))]


def p_assign_dim_err(v, d, k):
    """`$x = k; $x[d] = $y;` -- the same sibling on a scalar base. It strides 2
    regardless, which is the point of putting it beside the broken one."""
    return [W(M.ASSIGN, 0, cv(v), k),
            W(M.ASSIGN_DIM, 0, cv(v), d, tmp(0)),
            W(M.OP_DATA, 0, cv(k % M.NVAR), tmp(3))]


def p_fetch_ok(a, d):
    """`$a = array(); $t = &$a[d];` -- FETCH_DIM_RW, non-error."""
    return [W(M.INIT_ARRAY, 0, cv(0), a),
            W(M.FETCH_DIM_RW, 0, cv(0), d, tmp(1))]


def p_add(r, x, y):
    return [W(M.ADD, 0, cv(x), cv(y), cv(r))]


def p_echo(v):
    return [W(M.ECHO, 0, cv(v))]


def p_echo_tmp(t):
    return [W(M.ECHO, 0, tmp(t))]


def p_nop():
    return [W(M.NOP)]


def p_assign(v, k):
    return [W(M.ASSIGN, 0, cv(v), k)]


class Rng:
    """xorshift64*, so the corpus is reproducible on any box and in any Python."""

    def __init__(self, seed):
        self.s = seed & ((1 << 64) - 1) or 0x9E3779B97F4A7C15

    def next(self):
        x = self.s
        x ^= (x << 13) & ((1 << 64) - 1)
        x ^= x >> 7
        x ^= (x << 17) & ((1 << 64) - 1)
        self.s = x
        return (x * 0x2545F4914F6CDD1D) & ((1 << 64) - 1)

    def below(self, n):
        return self.next() % n


def make_window(nwords, rng):
    """One well-formed op_array of exactly `nwords` words.

    ⭐ THE MANDATORY CORE comes first and is the same in every window: it is
    what makes assertion 1 a per-window fact rather than a union over the file.
    Ten words; the rest is filler."""
    words = []
    words += p_dim_add(rng.below(M.NVAR), rng.below(256), 2 + rng.below(6))
    words += p_default_err(2 + rng.below(6), rng.below(256), rng.below(4096))
    words += p_default_ok(2 + rng.below(6), 2 + rng.below(6))
    words += p_assign_dim_ok(rng.below(M.NVAR), rng.below(256), 2 + rng.below(6))

    fillers = [
        lambda: p_assign_dim_err(2 + rng.below(6), rng.below(256), rng.below(4096)),
        lambda: p_fetch_ok(rng.below(M.NVAR), rng.below(256)),
        lambda: p_add(2 + rng.below(6), 2 + rng.below(6), 2 + rng.below(6)),
        lambda: p_echo(rng.below(M.NVAR)),
        lambda: p_echo_tmp(rng.below(M.NT)),
        lambda: p_nop(),
        lambda: p_assign(2 + rng.below(6), rng.below(4096)),
        lambda: p_default_ok(2 + rng.below(6), 2 + rng.below(6)),
        lambda: p_dim_add(rng.below(M.NVAR), rng.below(256), 2 + rng.below(6)),
    ]
    while True:
        room = nwords - 2 - len(words)
        if room <= 0:
            break
        cand = fillers[rng.below(len(fillers))]()
        if len(cand) <= room:
            words += cand
        else:
            words += p_nop()
    # `zend_do_return` then `zend_do_handle_exception` -- zend_compile.c:1091-1092.
    words += [W(M.RETURN), W(M.RETURN)]
    assert len(words) == nwords, (len(words), nwords)
    return b"".join(words)


def benign(path, stride, nwin, n_iters, seed):
    rng = Rng(seed)
    blob = b"".join(make_window(stride // 8, rng) for _ in range(nwin))
    slb.write(path, n_iters, slb.pack_head1_bytes(stride, blob))
    return blob


# -- the two adversarial cases §2.5 asks to be priced SEPARATELY --------------
# They differ in ONE BYTE: the opcode field of the trailing data word.

def _trigger_window(nwords, data_opcode):
    """`$x = 1; $x[0] += 1;` -- the corpus's own trigger for CRASH-023.

    The base is a LONG, so `zend_fetch_dimension_address` yields
    `EG(error_zval_ptr)` (:1744), :1765 is TRUE, and :1769 strides 1 with
    `increment_opline == 1`. The PC lands on the word below.

    `data_opcode` is that word's opcode field:
      PH55_OP_DATA -- what `zend_compile` emits, and what `pass_two` gives a
                      NULL handler (:4427, zend_opcode.c:363). THE NULL CALL.
      PH55_ADD     -- a word with a REAL handler. The PC is just as wrong, the
                      executor dispatches it, and NOTHING notices."""
    words = [W(M.ASSIGN, 0, cv(2), 1),                       # $x = 1;
             W(M.ASSIGN_ADD, M.X_DIM, cv(2), 0, tmp(0)),     # $x[0] += $y;
             W(data_opcode, 0, cv(3), tmp(1)),               # the data word
             W(M.ECHO, 0, cv(2)),
             W(M.ECHO, 0, tmp(0))]
    words += [W(M.NOP)] * (nwords - 2 - len(words))
    words += [W(M.RETURN), W(M.RETURN)]
    assert len(words) == nwords
    return b"".join(words)


def _benign_err_window(nwords):
    """The DEFAULT form on the error exit, alone in its own window: the exit
    fires, the stride of 1 is correct, and nothing happens. The control that
    shows the error exit is not wrong -- only wrong on one arm."""
    words = [W(M.ASSIGN, 0, cv(2), 7),
             W(M.FETCH_DIM_RW, 0, cv(2), 0, tmp(2)),
             W(M.ASSIGN_ADD, M.X_DEFAULT, tmp(2), cv(3), tmp(0)),
             W(M.ECHO, 0, tmp(0))]
    words += [W(M.NOP)] * (nwords - 2 - len(words))
    words += [W(M.RETURN), W(M.RETURN)]
    return b"".join(words)


# -- the assertions ----------------------------------------------------------

def _check_span(path, expect_defect, full_arms=True):
    """Re-decode what was just written and assert the arm table over EVERY
    window. ⚠ `PROTOCOL_PHP.md` §A2a rule 1's load-bearing half is the
    assertion, not the intention: ph03's generator COMMENT described an arm it
    never emitted."""
    m = model.Model(path)
    if not m.entered:
        return f"{os.path.basename(path):30s} no window entered (by design)"
    problems = []
    for k in range(m.nwin):
        win = m.buf[k * m.stride:(k + 1) * m.stride]
        ops = model.decode(win, m.stride // 8)
        mm = model._Machine(ops, model.pass_two(ops), True)
        mm.run()
        need = {("ASSIGN_ADD", "default", False), ("ASSIGN_ADD", "default", True),
                ("ASSIGN_ADD", "dim", False), ("ASSIGN_DIM", False)}
        if full_arms and not need <= mm.arms:
            problems.append(f"window {k} misses {sorted(need - mm.arms, key=str)}")
        got_defect = ("ASSIGN_ADD", "dim", True) in mm.arms
        if got_defect != expect_defect:
            problems.append(f"window {k}: defect arm reached={got_defect}, "
                            f"want {expect_defect}")
    # every handler dispatched at least once across the file
    seen = set()
    for k in range(m.nwin):
        win = m.buf[k * m.stride:(k + 1) * m.stride]
        ops = model.decode(win, m.stride // 8)
        hs = model.pass_two(ops)
        mm = model._Machine(ops, hs, True)
        pc = 0
        for _ in range(m.stride // 8):
            seen.add(ops[pc]["opcode"])
            if ops[pc]["opcode"] == model.RETURN:
                break
            mm.pc = pc
            mm._h(ops[pc])
            pc = mm.pc
    if full_arms:
        want = set(range(model.N_OPCODES)) - model.NO_HANDLER
        if not want <= seen:
            problems.append(f"opcodes never dispatched: {sorted(want - seen)}")
    if problems:
        raise AssertionError(f"{path}: " + "; ".join(problems[:6]))
    sc = m.selfcheck()
    if sc:
        raise AssertionError(f"{path}: model selfcheck: {sc}")
    return (f"{os.path.basename(path):30s} {m.describe()}  "
            f"exit={m.expected_exit}")


def main():
    out = HERE
    lines = []

    # ---- benign. Two shapes so the marginal-Ir slope has a denominator that
    # moves: 16 instruction words and 64 (== PH55_MAX_OPS).
    benign(os.path.join(out, "small.bin"), 128, 24, 20000, 0xA55A55AA55AA55A5)
    benign(os.path.join(out, "large.bin"), 512, 24, 20000, 0x0123456789ABCDEF)

    # ---- adversarial. ⭐ Exactly one window each, so a hostile window the
    # driver never selects cannot be declared (see model.sanitizer_expect).
    for name, oc in (("adversarial-nullcall.bin", model.OP_DATA),
                     ("adversarial-opdatalive.bin", model.ADD)):
        slb.write(os.path.join(out, name), 2000,
                  slb.pack_head1_bytes(128, _trigger_window(16, oc)))

    slb.write(os.path.join(out, "adversarial-benignerr.bin"), 2000,
              slb.pack_head1_bytes(128, _benign_err_window(16)))

    # No window at all: `stride > n_blob`, so the driver's guard skips the loop
    # entirely rather than entering it and breaking out.
    slb.write(os.path.join(out, "adversarial-nowin.bin"), 2000,
              slb.pack_head1_bytes(512, _benign_err_window(16)))

    # `payload_len` declares more bytes than are present -- exit 5.
    full = slb.pack_head1_bytes(128, _benign_err_window(16))
    slb.write(os.path.join(out, "adversarial-shortlen.bin"), 2000,
              full[:-64], declared_len=len(full))

    # ⚠ The full arm table is asserted of the MEASURED corpus only. The two
    # single-purpose adversarial windows are single-purpose on purpose: each
    # isolates one arm, and demanding the whole table of them would force
    # scenery into a window whose point is that it has none.
    for n in ("small.bin", "large.bin"):
        lines.append(_check_span(os.path.join(out, n), expect_defect=False))
    for n in ("adversarial-benignerr.bin", "adversarial-nowin.bin"):
        lines.append(_check_span(os.path.join(out, n), expect_defect=False,
                                 full_arms=False))
    for n in ("adversarial-nullcall.bin", "adversarial-opdatalive.bin"):
        p = os.path.join(out, n)
        m = model.Model(p)
        assert m.nwin == 1, f"{n}: {m.nwin} windows, want exactly 1"
        ops = model.decode(m.buf, m.stride // 8)
        mm = model._Machine(ops, model.pass_two(ops), False)   # R1
        nullc = False
        try:
            mm.run()
        except model.NullCall:
            nullc = True
        assert ("ASSIGN_ADD", "dim", True) in mm.arms, \
            f"{n}: the defect arm is not reached"
        want_null = (n == "adversarial-nullcall.bin")
        assert nullc == want_null, f"{n}: null_call={nullc}, want {want_null}"
        assert m.sanitizer_expect == ("fires" if want_null else "clean"), n
        lines.append(f"{n:30s} {m.describe()}  exit={m.expected_exit}")
    m = model.Model(os.path.join(out, "adversarial-shortlen.bin"))
    assert m.truncated and m.expected_exit == 5
    lines.append(f"{'adversarial-shortlen.bin':30s} {m.describe()}  "
                 f"exit={m.expected_exit}")

    # ⭐ THE PAIR THE ROW EXISTS TO PRICE, asserted rather than described: the
    # two adversarial windows differ in EXACTLY ONE BYTE.
    a = model.Model(os.path.join(out, "adversarial-nullcall.bin")).buf
    b = model.Model(os.path.join(out, "adversarial-opdatalive.bin")).buf
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    assert diff == [16], f"the two adversarial blobs differ at {diff}, want [16]"

    for ln in lines:
        print(ln)
    print(f"\nthe two adversarial windows differ in one byte, at offset "
          f"{diff[0]}: the opcode field of the trailing data word "
          f"({a[16]} = OP_DATA vs {b[16]} = ADD)")


if __name__ == "__main__":
    main()
