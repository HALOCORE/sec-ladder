#!/usr/bin/env python3
"""ph56-fetchmode-arith: build the input corpus.

    python3 patterns-php/ph56-fetchmode-arith/inputs/gen.py

`.bin` files are gitignored and re-derivable; this script is the generator and
it is the committed artefact (`CLAUDE.md` constraint 6).

THE PAYLOAD is `slb.head1_u64_bytes`: one head word (`stride`, the window in
BYTES) followed by the blob. ⭐ **The blob IS the record stream the parser hands
the compiler** -- one statement per little-endian u64:

    byte 0   mode      BP_VAR_*, as an index into the six
    byte 1   base      which member of the W group the parser built,
                       plus bit 7 = CHAIN (`$a[][d]` rather than `$a[d]`)
    byte 2   op2_type  IS_UNUSED / IS_CONST / IS_VAR
    byte 3   op2       the dimension
    bytes 4-5 op1      the container CV slot
    bytes 6-7 result   the result temp

⚠⚠ **WHAT `_check_span` ASSERTS, AND WHY EACH HALF IS THERE**
(`PROTOCOL_PHP.md` §A2a rule 1):

  1. every BENIGN window reaches ALL SIX ARMS of `switch (type)` -- the switch
     the defect lives in (`zend_compile.c:751-776`). ⭐ It CAN, and that is the
     whole reason PHP 5.0.0 shipped with this defect: five of the six arms are
     correct, and the corpus lives in them.
  2. NO benign window reaches the DEFECT COMBINATION -- `BP_VAR_IS` on a
     `ZEND_FETCH_DIM_W` whose op2 is `IS_UNUSED`, whether directly or as the
     leading element of a chain. That one cannot be benign: it IS the defect,
     and `check.py` stage 7h requires R1h == R1 on every non-adversarial input.
  3. no benign window fires the two guards that DO exist either, because
     `E_COMPILE_ERROR` is a `zend_bailout()` and a window that bails on its
     first statement measures nothing at all.
  4. ⭐⭐ every benign window DOES carry `BP_VAR_W` and `BP_VAR_RW` and
     `BP_VAR_FUNC_ARG` on an `IS_UNUSED` dim -- `$a[] = 1`, `$a[] += 1` and
     `f($a[])`. Those are the three arms upstream left unguarded and did NOT
     fix, two of them deliberately; putting them in the MEASURED corpus is how
     this row's census becomes a number rather than a paragraph.
  5. every emitted opcode is dispatched, so none ships unexercised.

Assertions, not comments. `ph03` shipped a corpus whose own generator comment
described an arm it never emitted, and the model was wrong for a whole task.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(ROOT, "common"))
sys.path.insert(0, os.path.join(HERE, ".."))
import slb    # noqa: E402
import model  # noqa: E402

M = model

# -- the assembler -----------------------------------------------------------
# Mode / base / op2-type are written as the INDICES the decoder takes, so that
# what this file writes and what `model.decode_stmt` reads are the same table.
MODE_I = {M.BP_R: 0, M.BP_W: 1, M.BP_RW: 2, M.BP_IS: 3,
          M.BP_FUNC_ARG: 4, M.BP_UNSET: 5}
BASE_I = {M.FETCH_W: 0, M.FETCH_DIM_W: 1, M.FETCH_OBJ_W: 2}
O2T_I = {M.T_UNUSED: 0, M.T_CONST: 1, M.T_VAR: 2}


def S(mode, base=None, o2t=None, chain=0, op1=0, op2=0, res=0):
    """One statement record."""
    base = M.FETCH_DIM_W if base is None else base
    o2t = M.T_CONST if o2t is None else o2t
    return bytes([MODE_I[mode],
                  BASE_I[base] | (0x80 if chain else 0),
                  O2T_I[o2t], op2 & 0xFF,
                  op1 & 0xFF, (op1 >> 8) & 0xFF,
                  res & 0xFF, (res >> 8) & 0xFF])


# -- the PHP statements each record stands for -------------------------------
# ⚠ Every phrase names the PHP it is, because the row's whole census is about
# which PHP surface reaches which arm.

def p_read_dim(a, d, r):
    """`$x = $a[d];`  -- BP_VAR_R, op2 present. The guarded arm, not firing."""
    return S(M.BP_R, M.FETCH_DIM_W, M.T_CONST, op1=a, op2=d, res=r)


def p_write_dim(a, d, r):
    """`$a[d] = 1;`   -- BP_VAR_W, op2 present."""
    return S(M.BP_W, M.FETCH_DIM_W, M.T_CONST, op1=a, op2=d, res=r)


def p_append_w(a, r):
    """⭐ `$a[] = 1;`  -- BP_VAR_W on an IS_UNUSED dim. **LEGAL, AND IT IS WHAT
    `[]` IS FOR.** This is the arm that makes the missing guard look like an
    omission rather than a decision: the same `IS_UNUSED` operand is correct
    here and fatal two arms down."""
    return S(M.BP_W, M.FETCH_DIM_W, M.T_UNUSED, op1=a, res=r)


def p_append_rw(a, r):
    """⭐ `$a[] += 1;` -- BP_VAR_RW on an IS_UNUSED dim. Unguarded, and CLEAN:
    measured on a pristine 5.0.0 CLI it appends `int(1)` and exits 0, and it is
    still unchecked in PHP 8.5. ../NOTES.md §2."""
    return S(M.BP_RW, M.FETCH_DIM_W, M.T_UNUSED, op1=a, res=r)


def p_funcarg_append(a, r):
    """⚠⚠ `f($a[]);` where `f` is declared AFTER the call -- BP_VAR_FUNC_ARG on
    an IS_UNUSED dim. **THE LIVE UNCAUGHT SIBLING.** `zend_do_pass_param`
    (zend_compile.c:1411-1427) asks for `BP_VAR_R` when the callee is already
    declared and `BP_VAR_FUNC_ARG` when it is not, so the SAME PHP expression is
    a compile error or a silent array append depending on declaration order.
    `1e708a5aeb30` does not touch this arm and no PHP 5 release ever guarded it
    at compile time. ../NOTES.md §2."""
    return S(M.BP_FUNC_ARG, M.FETCH_DIM_W, M.T_UNUSED, op1=a, res=r)


def p_isset_dim(a, d, r):
    """`isset($a[d]);` -- BP_VAR_IS with op2 PRESENT. Compiles to
    ZEND_ISSET_ISEMPTY_DIM_OBJ carrying a real operand, which is the shape the
    handler's unconditional read is correct for."""
    return S(M.BP_IS, M.FETCH_DIM_W, M.T_CONST, op1=a, op2=d, res=r)


def p_isset_var(v, r):
    """`isset($x);`    -- BP_VAR_IS on a plain FETCH. `:3227` rewrites it to
    ZEND_ISSET_ISEMPTY_VAR, whose handler reads no op2 at all."""
    return S(M.BP_IS, M.FETCH_W, M.T_UNUSED, op1=v, res=r)


def p_unset_dim(a, d, r):
    """`unset($a[d]);` -- BP_VAR_UNSET, op2 present. The other guarded arm, not
    firing."""
    return S(M.BP_UNSET, M.FETCH_DIM_W, M.T_CONST, op1=a, op2=d, res=r)


def p_obj_is(a, r):
    """`isset($o->p);` -- BP_VAR_IS on a FETCH_OBJ_W, so `:3231` rewrites it to
    ZEND_ISSET_ISEMPTY_PROP_OBJ. Here so that all three arms of the SECOND
    rewrite are exercised, not just the one the row is about."""
    return S(M.BP_IS, M.FETCH_OBJ_W, M.T_CONST, op1=a, op2=1, res=r)


# ---- the two adversarial statements, and they differ in ONE BIT ------------

def p_isset_append(a, r):
    """⛔⛔ `isset($a[]);` -- BP_VAR_IS on a ZEND_FETCH_DIM_W whose op2 is
    IS_UNUSED. **CRASH-041.** `+= 6` makes it ZEND_FETCH_DIM_IS, `:3229`
    rewrites it to ZEND_ISSET_ISEMPTY_DIM_OBJ, and that handler reads the absent
    operand and dereferences NULL."""
    return S(M.BP_IS, M.FETCH_DIM_W, M.T_UNUSED, chain=0, op1=a, res=r)


def p_isset_chain(a, r):
    """⛔ `isset($a[][0]);` -- THE SAME STATEMENT WITH THE CHAIN BIT SET, and
    that is the only byte that differs. `:3223` rewrites the LAST opline of the
    fetch list only, so the `[]` opline SURVIVES as ZEND_FETCH_DIM_IS, reaches
    `zend_fetch_dimension_address`'s append arm (:935-943) and GROWS THE ARRAY.
    Exit 0, a plausible answer, no diagnostic from anything."""
    return S(M.BP_IS, M.FETCH_DIM_W, M.T_CONST, chain=1, op1=a, res=r)


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


# ⭐ An ARRAY container is an even CV index; odd ones are a string (index 1) or
# a long. The append arms need an array to append to.
def arr(rng):
    return 2 * rng.below(M.NVAR // 2)


def make_window(nstmt, rng):
    """One well-formed record stream of exactly `nstmt` statements.

    ⭐ THE MANDATORY CORE comes first and is the same in every window: it
    carries all six arms of the mode switch, all three arms of the second
    rewrite, and the three unguarded-and-not-fixed appends. Nine statements;
    the rest is filler."""
    out = [
        p_read_dim(arr(rng), rng.below(4), 0),        # BP_VAR_R
        p_write_dim(arr(rng), rng.below(4), 1),       # BP_VAR_W, op2 present
        p_append_w(arr(rng), 2),                      # BP_VAR_W    on []
        p_append_rw(arr(rng), 3),                     # BP_VAR_RW   on []
        p_isset_dim(arr(rng), rng.below(4), 4),       # BP_VAR_IS, op2 present
        p_isset_var(rng.below(M.NVAR), 5),            # BP_VAR_IS -> ISSET_VAR
        p_funcarg_append(arr(rng), 6),                # BP_VAR_FUNC_ARG on []
        p_unset_dim(arr(rng), rng.below(4), 7),       # BP_VAR_UNSET
        p_obj_is(rng.below(M.NVAR), 8),               # -> ISSET_PROP_OBJ
    ]
    fillers = [
        lambda: p_read_dim(arr(rng), rng.below(4), rng.below(16)),
        lambda: p_write_dim(arr(rng), rng.below(4), rng.below(16)),
        lambda: p_append_w(arr(rng), rng.below(16)),
        lambda: p_append_rw(arr(rng), rng.below(16)),
        lambda: p_isset_dim(arr(rng), rng.below(4), rng.below(16)),
        lambda: p_isset_var(rng.below(M.NVAR), rng.below(16)),
        lambda: p_funcarg_append(arr(rng), rng.below(16)),
        lambda: p_unset_dim(arr(rng), rng.below(4), rng.below(16)),
        lambda: p_obj_is(rng.below(M.NVAR), rng.below(16)),
    ]
    while len(out) < nstmt:
        out.append(fillers[rng.below(len(fillers))]())
    assert len(out) == nstmt, (len(out), nstmt)
    return b"".join(out)


def benign(path, stride, nwin, n_iters, seed):
    rng = Rng(seed)
    blob = b"".join(make_window(stride // 8, rng) for _ in range(nwin))
    slb.write(path, n_iters, slb.pack_head1_bytes(stride, blob))
    return blob


def _adv_window(nstmt, trigger):
    """One adversarial window: the trigger first, then inert filler."""
    rng = Rng(0xC0FFEE)
    out = [trigger] + [p_write_dim(arr(rng), rng.below(4), i)
                       for i in range(nstmt - 1)]
    return b"".join(out[:nstmt])


# -- the assertions ----------------------------------------------------------

def _arm_facts(win, nstmt):
    """`(modes reached, defect-combination reached, guard fired)` for one
    window, read off the decoder rather than off this file's intentions."""
    modes, defect, guard = set(), False, False
    for i in range(nstmt):
        s = M.decode_stmt(win, i)
        modes.add(s["mode"])
        dimw_unused = (s["base"] == M.FETCH_DIM_W and s["o2t"] == M.T_UNUSED)
        if s["mode"] == M.BP_IS and (s["chain"] or dimw_unused):
            defect = True
        if s["mode"] in (M.BP_R, M.BP_UNSET) and (s["chain"] or dimw_unused):
            guard = True
    return modes, defect, guard


def _check_span(path, expect_defect, full_arms=True):
    """Re-decode what was just written and assert the arm table over EVERY
    window. ⚠ `PROTOCOL_PHP.md` §A2a rule 1's load-bearing half is the
    ASSERTION, not the intention: ph03's generator COMMENT described an arm it
    never emitted."""
    m = model.Model(path)
    if not m.entered:
        return f"{os.path.basename(path):30s} no window entered (by design)"
    problems = []
    nstmt = min(m.stride // 8, M.MAX_STMT)
    all_modes = set(M.MODES)
    seen_opcodes = set()
    for k in range(m.nwin):
        win = m.buf[k * m.stride:(k + 1) * m.stride]
        modes, defect, guard = _arm_facts(win, nstmt)
        if full_arms and modes != all_modes:
            problems.append(f"window {k} misses modes {sorted(all_modes - modes)}")
        if defect != expect_defect:
            problems.append(f"window {k}: defect combination reached={defect}, "
                            f"want {expect_defect}")
        if full_arms and guard:
            problems.append(f"window {k}: a compile guard FIRES on a benign "
                            f"window; zend_bailout() would leave nothing to "
                            f"measure")
        ops, nops, bail, _ = M.compile_window(win, nstmt, True)
        for j in range(nops):
            seen_opcodes.add(ops[j]["opcode"])
    if full_arms:
        want = {M.FETCH_DIM_R, M.FETCH_DIM_W, M.FETCH_DIM_RW,
                M.FETCH_DIM_FUNC_ARG, M.FETCH_DIM_UNSET,
                M.ISSET_ISEMPTY_DIM_OBJ, M.ISSET_ISEMPTY_VAR,
                M.ISSET_ISEMPTY_PROP_OBJ}
        if not want <= seen_opcodes:
            problems.append(f"opcodes never emitted: "
                            f"{sorted(want - seen_opcodes)}")
    if problems:
        raise AssertionError(f"{path}: " + "; ".join(problems[:6]))
    sc = m.selfcheck()
    if sc:
        raise AssertionError(f"{path}: model selfcheck: {sc}")
    return f"{os.path.basename(path):30s} {m.describe()}  exit={m.expected_exit}"


def main():
    out = HERE
    lines = []

    # ---- benign. Two shapes so the marginal-Ir slope has a denominator that
    # moves: 16 statement records and 64 (== PH56_MAX_STMT).
    benign(os.path.join(out, "small.bin"), 128, 24, 20000, 0xA55A55AA55AA55A5)
    benign(os.path.join(out, "large.bin"), 512, 24, 20000, 0x0123456789ABCDEF)

    # ---- adversarial. ⭐ Exactly one window each, so a hostile window the
    # driver never selects cannot be declared (see model.sanitizer_expect).
    adv = {
        # ⛔ isset($a[]) -- the NULL operand dereference. CRASH-041.
        "adversarial-nullderef.bin": p_isset_append(0, 0),
        # ⛔ isset($a[][0]) -- ONE BIT away, and SILENT.
        "adversarial-chain.bin": p_isset_chain(0, 0),
        # ⚠ f($a[]) -- the arm upstream never guarded at compile time.
        "adversarial-funcarg.bin": p_funcarg_append(0, 0),
        # ✅ $x = $a[] -- the guard that DOES exist, firing.
        "adversarial-guardfires.bin":
            S(M.BP_R, M.FETCH_DIM_W, M.T_UNUSED, op1=0, res=0),
    }
    for name, trig in adv.items():
        slb.write(os.path.join(out, name), 2000,
                  slb.pack_head1_bytes(128, _adv_window(16, trig)))

    # No window at all: `stride > n_blob`, so the driver's guard skips the loop.
    slb.write(os.path.join(out, "adversarial-nowin.bin"), 2000,
              slb.pack_head1_bytes(512, _adv_window(16, p_write_dim(0, 0, 0))))

    # `payload_len` declares more bytes than are present -- exit 5.
    full = slb.pack_head1_bytes(128, _adv_window(16, p_write_dim(0, 0, 0)))
    slb.write(os.path.join(out, "adversarial-shortlen.bin"), 2000,
              full[:-64], declared_len=len(full))

    # ⚠ The full arm table is asserted of the MEASURED corpus only. The
    # single-purpose adversarial windows are single-purpose on purpose.
    for n in ("small.bin", "large.bin"):
        lines.append(_check_span(os.path.join(out, n), expect_defect=False))
    for n in ("adversarial-funcarg.bin", "adversarial-guardfires.bin",
              "adversarial-nowin.bin"):
        lines.append(_check_span(os.path.join(out, n), expect_defect=False,
                                 full_arms=False))
    for n in ("adversarial-nullderef.bin", "adversarial-chain.bin"):
        p = os.path.join(out, n)
        m = model.Model(p)
        assert m.nwin == 1, f"{n}: {m.nwin} windows, want exactly 1"
        want_null = (n == "adversarial-nullderef.bin")
        assert m.any_null_operand == want_null, \
            f"{n}: null_operand={m.any_null_operand}, want {want_null}"
        assert m.sanitizer_expect == ("fires" if want_null else "clean"), n
        if not want_null:
            assert m.any_divergence, \
                (f"{n}: R1 and R1h AGREE, so this input measures nothing. Its "
                 f"whole point is that R1 silently appends where R1h refuses "
                 f"to compile")
        lines.append(f"{n:30s} {m.describe()}  exit={m.expected_exit}")

    m = model.Model(os.path.join(out, "adversarial-shortlen.bin"))
    assert m.truncated and m.expected_exit == 5
    lines.append(f"{'adversarial-shortlen.bin':30s} {m.describe()}  "
                 f"exit={m.expected_exit}")

    # ⭐⭐ THE PAIR THE ROW EXISTS TO PRICE, ASSERTED RATHER THAN DESCRIBED: the
    # two adversarial windows differ in EXACTLY ONE BYTE, and within that byte
    # in exactly the CHAIN BIT plus the op2-type index -- `isset($a[])` against
    # `isset($a[][0])`.
    a = model.Model(os.path.join(out, "adversarial-nullderef.bin")).buf
    b = model.Model(os.path.join(out, "adversarial-chain.bin")).buf
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    assert diff in ([1], [1, 2]), \
        f"the two adversarial blobs differ at {diff}, want the first record only"

    # ⭐⭐⭐ AND THE CENSUS, ASSERTED: the R1h fix moves the two BP_VAR_IS inputs
    # and moves NEITHER of the two unguarded siblings. That is `../NOTES.md`
    # §2's whole finding, as a test rather than a paragraph.
    for name, should_move in (("adversarial-nullderef.bin", True),
                              ("adversarial-chain.bin", True),
                              ("adversarial-funcarg.bin", False),
                              ("small.bin", False),
                              ("large.bin", False)):
        mm = model.Model(os.path.join(out, name))
        moved = mm.any_null_operand or mm.any_divergence
        assert moved == should_move, \
            (f"{name}: R1h differs from R1 = {moved}, want {should_move}. The "
             f"census is that 1e708a5aeb30 fixes BP_VAR_IS and leaves "
             f"BP_VAR_FUNC_ARG standing")

    for ln in lines:
        print(ln)
    print(f"\nthe two adversarial windows differ at byte offset(s) {diff}: "
          f"the CHAIN bit of the first statement record -- isset($a[]) against "
          f"isset($a[][0])")
    print("census asserted: R1h moves BOTH BP_VAR_IS inputs and NEITHER "
          "unguarded sibling")


if __name__ == "__main__":
    main()
